"""Unified Router Client for ModelRouter (Laya and Kev Serving APIs).

Implements the strict V8 §7.1 contract:
- Calls remote router API via POST /route.
- Provides automatic retries, latency timing, and structured error handling.
- Gracefully falls back to MockRouter when the server endpoint is offline or busy,
  explicitly tagging `fallback_used=True` and recording `fallback_reason`.
"""
from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4
from modelrouter.serving.schemas import RouteRequest, RouteResponse

logger = logging.getLogger("experiments.agent_pilot.router_clients")

# Limit concurrent remote calls to avoid overloading single-worker uvicorn
_ROUTER_SEMAPHORE = threading.Semaphore(2)


@dataclass
class RouterDecision:
    request_id: str
    router_family: str
    checkpoint_id: str
    selected_action: Dict[str, Any]
    ranked_actions: List[Dict[str, Any]] = field(default_factory=list)
    decision_latency_ms: float = 0.0
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    confidence: Optional[float] = None
    inference_latency_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "router_family": self.router_family,
            "checkpoint_id": self.checkpoint_id,
            "selected_action": self.selected_action,
            "ranked_actions": self.ranked_actions,
            "decision_latency_ms": round(self.decision_latency_ms, 2),
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "confidence": round(self.confidence, 4) if self.confidence is not None else None,
            "inference_latency_ms": self.inference_latency_ms,
            "evidence_type": "MOCK_OR_FALLBACK" if self.fallback_used else "REMOTE_ROUTE",
        }


class MockRouter:
    """Deterministic offline router simulating Laya and Kev decision logic."""

    @staticmethod
    def route(
        router_family: str,
        pre_decision_state: Dict[str, Any],
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        req_id = str(uuid4())
        phase = pre_decision_state.get("phase", "inspect")
        last_exit = pre_decision_state.get("last_tool_exit_code", 0)
        budget_remaining = pre_decision_state.get("budget_remaining_usd", 1.0)

        # Separate actions by pool
        fast_actions = [a for a in legal_actions if a.get("pool") == "Fast"]
        standard_actions = [a for a in legal_actions if a.get("pool") == "Standard"]
        reasoning_actions = [a for a in legal_actions if a.get("pool") == "Reasoning"]
        strong_actions = [a for a in legal_actions if a.get("pool") == "Strong"]

        # Policy logic based on router_family
        if router_family.lower() == "kev":
            checkpoint_id = "kev-4b-lora-e02"
            # Kev is tuned for high-difficulty tool error recovery and reasoning
            if last_exit != 0 and reasoning_actions:
                # On tool error, Kev prioritizes reasoning
                selected = reasoning_actions[0]
                conf = 0.88
            elif phase == "modify" and standard_actions:
                selected = standard_actions[0]
                conf = 0.79
            elif fast_actions:
                selected = fast_actions[0]
                conf = 0.84
            else:
                selected = legal_actions[0]
                conf = 0.50
        else:
            # Laya-V2 (421M token router)
            checkpoint_id = "laya-v2-421m-f03-best"
            # Laya optimizes cost vs quality trade-off
            if budget_remaining < 0.20 and fast_actions:
                selected = fast_actions[0]
                conf = 0.92
            elif phase == "inspect" and fast_actions:
                selected = fast_actions[0]
                conf = 0.85
            elif phase == "verify" and fast_actions:
                selected = fast_actions[0]
                conf = 0.81
            elif standard_actions:
                selected = standard_actions[0]
                conf = 0.76
            elif fast_actions:
                selected = fast_actions[0]
                conf = 0.70
            else:
                selected = legal_actions[0]
                conf = 0.50

        latency_ms = (time.time() - t0) * 1000 + random.uniform(8.0, 25.0)

        return RouterDecision(
            request_id=req_id,
            router_family=router_family,
            checkpoint_id=checkpoint_id,
            selected_action=selected,
            ranked_actions=legal_actions[:3],
            decision_latency_ms=latency_ms,
            fallback_used=True,
            fallback_reason="MOCK_ROUTER",
            confidence=conf,
        )


class RouterClient:
    """HTTP Client connecting to remote A6000 Router Serving API with automatic fallback."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        timeout: float = 20.0,
        max_retries: int = 1,
        router_family: str = "laya",
        protocol: str = "route",
    ):
        self.endpoint = (
            endpoint
            or os.environ.get("ROUTER_SERVING_ENDPOINT")
            or "http://127.0.0.1:8000"
        ).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.router_family = router_family
        self.protocol = protocol
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def is_healthy(self) -> bool:
        """Checks if the remote serving endpoint /health returns 200 OK."""
        try:
            url = f"{self.endpoint}/health"
            req = urllib.request.Request(url, method="GET")
            with self._opener.open(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def route(
        self,
        episode_id: str,
        decision_id: str,
        pre_decision_state: Dict[str, Any],
        legal_actions: List[Dict[str, Any]],
        policy_version: str = "v8.0",
    ) -> RouterDecision:
        """Requests route decision from server. Falls back to MockRouter if offline."""
        req_id = str(uuid4())
        payload = {
            "request_id": req_id,
            "episode_id": episode_id,
            "decision_id": decision_id,
            "policy_version": policy_version,
            "router_family": self.router_family,
            "pre_decision_state": pre_decision_state,
            "legal_actions": legal_actions,
            "budget_remaining": pre_decision_state.get("budget_remaining_usd", 1.0),
            "features_presence_mask": [int(key in pre_decision_state) for key in (
                "task_domain", "step_index", "context_chars", "prior_tool_calls_count",
                "prior_error_signals_count", "prompt", "history_snippet", "budget_remaining_usd",
            )],
        }
        route_request = RouteRequest.model_validate(payload)
        route_request.legal_actions.sort(key=lambda action: action.action_id)
        card_order = {action.action_id: index for index, action in enumerate(route_request.legal_actions)}
        route_request.pre_decision_state.capability_cards = sorted(
            route_request.pre_decision_state.capability_cards,
            key=lambda card: card_order.get(card.get("action_id"), len(card_order)),
        )
        payload = route_request.model_dump()
        candidates = {a.action_id: a for a in route_request.legal_actions}
        native_options = {f"opt_{index}": action for index, action in
                          enumerate(route_request.legal_actions)}
        if self.protocol == "system_one":
            payload = {
                "router_family": self.router_family,
                "state": route_request.pre_decision_state.router_text(),
                "questions": {"route_decision": {
                    "type": "choice",
                    "instructions": "Select the model and native effort for the next agent generation.",
                    "criteria": {key: f"{action.provider}/{action.model} (effort={action.native_effort})"
                                 for key, action in native_options.items()},
                }},
            }

        # Try remote endpoint with concurrency throttle
        attempts = 0
        last_err = ""
        with _ROUTER_SEMAPHORE:
            while attempts <= self.max_retries:
                attempts += 1
                t0 = time.time()
                try:
                    url = f"{self.endpoint}/v1/systemone" if self.protocol == "system_one" else f"{self.endpoint}/route"
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=data,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self._opener.open(req, timeout=self.timeout) as resp:
                        lat_ms = (time.time() - t0) * 1000
                        if resp.status == 200:
                            body = json.loads(resp.read().decode("utf-8"))
                            if self.protocol == "system_one":
                                answer = body["answers"]["route_decision"]
                                probabilities = answer["probabilities"]
                                if set(probabilities) != set(native_options):
                                    raise ValueError("Router probability IDs differ from the request candidates")
                                body = {
                                    "request_id": req_id,
                                    "router_family": body["router_family"],
                                    "checkpoint_id": body["checkpoint_id"],
                                    "selected_action": native_options[answer["choice"]].model_dump(),
                                    "ranked_actions_or_scores_if_available": [
                                        {"action": native_options[key].model_dump(),
                                         "score": value, "probability": value}
                                        for key, value in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
                                    ],
                                    "decision_latency_ms": body["decision_latency_ms"],
                                    "fallback_used": body["fallback_used"],
                                    "fallback_reason": body.get("fallback_reason"),
                                    "confidence_if_defined": answer.get("confidence"),
                                }
                            response = RouteResponse.model_validate(body)
                            returned_actions = [response.selected_action] + [score.action for score in response.ranked_actions_or_scores_if_available]
                            if any(candidates.get(action.action_id) != action for action in returned_actions):
                                raise ValueError("Router returned an action outside the request candidates")
                            if response.request_id != req_id or response.router_family != self.router_family:
                                raise ValueError("Router response identifies a different request")
                            return RouterDecision(
                                request_id=response.request_id,
                                router_family=response.router_family,
                                checkpoint_id=response.checkpoint_id,
                                selected_action=response.selected_action.model_dump(),
                                ranked_actions=[score.model_dump() for score in response.ranked_actions_or_scores_if_available],
                                decision_latency_ms=lat_ms,
                                fallback_used=response.fallback_used,
                                fallback_reason=response.fallback_reason,
                                confidence=response.confidence_if_defined,
                                inference_latency_ms=response.decision_latency_ms,
                            )
                except urllib.error.HTTPError as e:
                    last_err = f"HTTPError {e.code}: {e.reason}"
                    if e.code not in (429, 502, 503, 504):
                        break
                except urllib.error.URLError as e:
                    last_err = f"URLError: {e.reason}"
                except Exception as e:
                    last_err = f"Exception: {str(e)}"
                    break

        # Remote server unreachable -> Fallback to MockRouter
        logger.warning(
            "Remote router API at %s unreachable (%s). Invoking MockRouter fallback.",
            self.endpoint,
            last_err,
        )
        decision = MockRouter.route(
            router_family=self.router_family,
            pre_decision_state=pre_decision_state,
            legal_actions=legal_actions,
        )
        decision.fallback_used = True
        decision.request_id = req_id
        decision.fallback_reason = f"REMOTE_UNREACHABLE: {last_err}"
        return decision
