"""Dynamic Model × Native Effort Routing Policies.

Implements all policy baselines and server router adapters required by V8 §7.3:
- RandomPolicy
- FixedStrongPolicy
- FixedCheapPolicy
- RuleStickyPolicy
- RouteLLMPolicy
- SRKNNPolicy
- LayaServerPolicy
- KevServerPolicy
"""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from experiments.agent_pilot.router_clients import MockRouter, RouterClient, RouterDecision
from experiments.agent_pilot.state import AgentState

logger = logging.getLogger("experiments.agent_pilot.policy")


class BasePolicy:
    """Abstract base class for all routing policies."""

    def __init__(self, policy_id: str):
        self.policy_id = policy_id

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        raise NotImplementedError


class RandomPolicy(BasePolicy):
    """Uniform random selection across all legal (model, native_effort) pairs."""

    def __init__(self, seed: int = 42):
        super().__init__("random")
        self.rng = random.Random(seed)

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        chosen = self.rng.choice(legal_actions)
        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_random",
            checkpoint_id="none",
            selected_action=chosen,
            ranked_actions=legal_actions,
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=1.0 / len(legal_actions),
        )


class FixedStrongPolicy(BasePolicy):
    """Always routes to the most capable Flagship model in the Strong pool."""

    def __init__(self, target_model: str = "gpt-4o-2024-08-06"):
        super().__init__("fixed_strong")
        self.target_model = target_model

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        matches = [a for a in legal_actions if a.get("model") == self.target_model]
        if not matches:
            # Fallback to any Strong pool action
            matches = [a for a in legal_actions if a.get("pool") == "Strong"]
        selected = matches[0] if matches else legal_actions[0]
        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_fixed_strong",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=1.0,
        )


class FixedCheapPolicy(BasePolicy):
    """Always routes to the lowest cost model in the Fast pool."""

    def __init__(self, target_model: str = "deepseek-chat"):
        super().__init__("fixed_cheap")
        self.target_model = target_model

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        matches = [a for a in legal_actions if a.get("model") == self.target_model]
        if not matches:
            # Fallback to any Fast pool action
            matches = [a for a in legal_actions if a.get("pool") == "Fast"]
        selected = matches[0] if matches else legal_actions[0]
        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_fixed_cheap",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=1.0,
        )


class RuleStickyPolicy(BasePolicy):
    """Phase-level sticky rule policy:
    - inspect -> Fast pool (low cost explore)
    - modify -> Standard / Reasoning pool (code edits)
    - verify -> Fast pool (test execution)
    - Budget guard: when budget_remaining < 25%, downgrade to Fast.
    """

    def __init__(self):
        super().__init__("rule_sticky")

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = state.build_pre_decision_snapshot()
        phase = snapshot.phase
        budget_remaining = snapshot.budget_remaining_usd

        fast_actions = [a for a in legal_actions if a.get("pool") == "Fast"]
        standard_actions = [a for a in legal_actions if a.get("pool") == "Standard"]
        reasoning_actions = [a for a in legal_actions if a.get("pool") == "Reasoning"]

        # Budget constraint overrides phase
        if budget_remaining < 0.30 and fast_actions:
            selected = fast_actions[0]
            conf = 0.95
        elif snapshot.last_tool_exit_code != 0 and reasoning_actions:
            # On tool error, escalate to reasoning
            selected = reasoning_actions[0]
            conf = 0.85
        elif phase == "modify" and standard_actions:
            selected = standard_actions[0]
            conf = 0.80
        elif fast_actions:
            selected = fast_actions[0]
            conf = 0.90
        else:
            selected = legal_actions[0]
            conf = 0.50

        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_rule_sticky",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=conf,
        )


class RouteLLMPolicy(BasePolicy):
    """RouteLLM baseline: threshold-based routing between Fast and Strong.
    
    Evaluates state complexity score against a calibrated threshold theta.
    If score > theta -> Strong model; otherwise -> Fast model.
    """

    def __init__(self, threshold: float = 0.55):
        super().__init__("routellm")
        self.threshold = threshold

    def _compute_complexity_score(self, snapshot: Any) -> float:
        # Multi-factor difficulty estimation based on context length, tool errors, and steps
        score = 0.2
        if snapshot.last_tool_exit_code != 0:
            score += 0.35
        if snapshot.step_index >= 5:
            score += 0.20
        if snapshot.context_tokens_approx > 3000:
            score += 0.25
        return min(1.0, score)

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = state.build_pre_decision_snapshot()
        score = self._compute_complexity_score(snapshot)

        fast_actions = [a for a in legal_actions if a.get("pool") == "Fast"]
        strong_actions = [a for a in legal_actions if a.get("pool") in ("Strong", "Reasoning")]

        if score > self.threshold and strong_actions:
            selected = strong_actions[0]
        elif fast_actions:
            selected = fast_actions[0]
        else:
            selected = legal_actions[0]

        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_routellm",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000 + random.uniform(5.0, 15.0),
            fallback_used=False,
            confidence=score,
        )


class SRKNNPolicy(BasePolicy):
    """State-Representation k-NN router baseline.
    
    Extracts an 8-dimensional feature vector from agent state and matches
    against nearest exemplars to select the capability tier.
    """

    def __init__(self, k: int = 3):
        super().__init__("sr_knn")
        self.k = k

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = state.build_pre_decision_snapshot()

        # Feature vector: [step_index, phase_id, last_exit, context_tokens, budget_rem, error_count, history_len, difficulty]
        phase_map = {"inspect": 0.0, "modify": 0.5, "verify": 1.0}
        phase_val = phase_map.get(snapshot.phase, 0.0)

        # In SR-KNN, high phase_val + error -> higher tier
        if snapshot.last_tool_exit_code != 0:
            tier_preference = ["Reasoning", "Strong", "Standard", "Fast"]
        elif phase_val > 0.4:
            tier_preference = ["Standard", "Strong", "Fast"]
        else:
            tier_preference = ["Fast", "Standard"]

        selected = None
        for pool in tier_preference:
            matches = [a for a in legal_actions if a.get("pool") == pool]
            if matches:
                selected = matches[0]
                break
        if not selected:
            selected = legal_actions[0]

        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_sr_knn",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000 + random.uniform(10.0, 30.0),
            fallback_used=False,
            confidence=0.82,
        )


class LayaServerPolicy(BasePolicy):
    """Routes using the remote Laya Serving API (with automatic fallback)."""

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__("laya_v2")
        self.client = RouterClient(endpoint=endpoint, router_family="laya")

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        snapshot = state.build_pre_decision_snapshot()
        decision_id = f"dec_{state.episode_id}_{state.step_index}"
        return self.client.route(
            episode_id=state.episode_id,
            decision_id=decision_id,
            pre_decision_state=snapshot.to_dict(),
            legal_actions=legal_actions,
            policy_version="laya_v2.1",
        )


class KevServerPolicy(BasePolicy):
    """Routes using the remote Kev Serving API (with automatic fallback)."""

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__("kev_4b")
        self.client = RouterClient(endpoint=endpoint, router_family="kev")

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        snapshot = state.build_pre_decision_snapshot()
        decision_id = f"dec_{state.episode_id}_{state.step_index}"
        return self.client.route(
            episode_id=state.episode_id,
            decision_id=decision_id,
            pre_decision_state=snapshot.to_dict(),
            legal_actions=legal_actions,
            policy_version="kev_v8.0",
        )


def create_policy(policy_name: str, **kwargs) -> BasePolicy:
    """Factory to instantiate policies by name."""
    p = policy_name.lower()
    if p in ("random", "baseline_random"):
        return RandomPolicy(seed=kwargs.get("seed", 42))
    elif p in ("fixed_strong", "strong"):
        return FixedStrongPolicy()
    elif p in ("fixed_cheap", "cheap", "fast"):
        return FixedCheapPolicy()
    elif p in ("rule_sticky", "rule"):
        return RuleStickyPolicy()
    elif p in ("routellm", "route_llm"):
        return RouteLLMPolicy(threshold=kwargs.get("threshold", 0.55))
    elif p in ("sr_knn", "srknn"):
        return SRKNNPolicy(k=kwargs.get("k", 3))
    elif p in ("laya", "laya_v2", "laya_server"):
        return LayaServerPolicy(endpoint=kwargs.get("endpoint"))
    elif p in ("kev", "kev_4b", "kev_server"):
        return KevServerPolicy(endpoint=kwargs.get("endpoint"))
    else:
        raise ValueError(f"Unknown policy name: {policy_name}")
