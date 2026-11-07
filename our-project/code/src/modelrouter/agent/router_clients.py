"""One real HTTP route request; transport failures remain failures."""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from modelrouter.serving.schemas import RouteRequest, RouteResponse, route_questions

# The existing single-worker Serving shares this concurrency limit.
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
    router_identity: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {**self.__dict__, "evidence_type": "REMOTE_ROUTE"}


class RouterClient:
    def __init__(self, endpoint=None, timeout=20.0, router_family="laya", protocol="route"):
        self.endpoint = (endpoint or os.environ.get("ROUTER_SERVING_ENDPOINT")
                         or "http://127.0.0.1:8000").rstrip("/")
        self.timeout, self.router_family, self.protocol = timeout, router_family, protocol
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def route(self, episode_id, decision_id, pre_decision_state, legal_actions, policy_version="v9"):
        req_id = str(uuid4())
        request = RouteRequest.model_validate({
            "request_id": req_id, "episode_id": episode_id, "decision_id": decision_id,
            "policy_version": policy_version, "router_family": self.router_family,
            "pre_decision_state": pre_decision_state, "legal_actions": legal_actions,
            "budget_remaining": pre_decision_state.get("budget_remaining_usd"),
        })
        request.legal_actions.sort(key=lambda action: action.action_id)
        candidates = {a.action_id: a for a in request.legal_actions}
        options = {a.action_id: a for a in request.legal_actions}
        payload = request.model_dump()
        path = "/route"
        if self.protocol == "system_one":
            path = "/v1/systemone"
            payload = {
                "router_family": self.router_family, "state": request.pre_decision_state.router_text(),
                "questions": route_questions(request.legal_actions),
            }
        started = time.monotonic()
        with _ROUTER_SEMAPHORE:
            req = urllib.request.Request(self.endpoint + path, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"}, method="POST")
            with self._opener.open(req, timeout=self.timeout) as response:
                body = json.load(response)
        identity = None
        if self.protocol == "system_one":
            identity = {**(body.get("router_identity") or {}), "router_input_usage": body.get("usage"),
                        "router_identity_source": self.endpoint + path,
                        "router_identity_status": "ATOMIC_ROUTE_RESPONSE" if body.get("router_identity")
                        else "NOT_REPORTED_BY_RUNNING_SERVING"}
            answer = body["answers"]["route_decision"]
            probabilities = answer["probabilities"]
            if set(probabilities) != set(options):
                raise ValueError("Router probability IDs differ from request candidates")
            body = {
                "request_id": req_id, "router_family": body["router_family"],
                "checkpoint_id": body["checkpoint_id"],
                "selected_action": options[answer["choice"]].model_dump(),
                "ranked_actions_or_scores_if_available": [
                    {"action": options[key].model_dump(), "score": value, "probability": value}
                    for key, value in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)],
                "decision_latency_ms": body["decision_latency_ms"], "fallback_used": body["fallback_used"],
                "fallback_reason": body.get("fallback_reason"), "confidence_if_defined": answer.get("confidence"),
            }
        response = RouteResponse.model_validate(body)
        if self.protocol == "route":
            identity = response.router_identity
        actions = [response.selected_action] + [score.action for score in response.ranked_actions_or_scores_if_available]
        if any(candidates.get(a.action_id) != a for a in actions):
            raise ValueError("Router returned an action outside request candidates")
        if response.request_id != req_id or response.router_family != self.router_family:
            raise ValueError("Router response identifies a different request")
        if response.fallback_used:
            raise RuntimeError(response.fallback_reason)
        return RouterDecision(
            request_id=req_id, router_family=response.router_family, checkpoint_id=response.checkpoint_id,
            selected_action=response.selected_action.model_dump(),
            ranked_actions=[score.model_dump() for score in response.ranked_actions_or_scores_if_available],
            decision_latency_ms=(time.monotonic() - started) * 1000,
            confidence=response.confidence_if_defined, inference_latency_ms=response.decision_latency_ms,
            router_identity=identity,
        )
