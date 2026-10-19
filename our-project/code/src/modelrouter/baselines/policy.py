"""Dynamic Model × Native Effort Routing Policies.

Strictly follows V8 §7.3, §8.4, and §9.2 specifications:
- All 8 policies implement both `select(state, legal_actions)` and `route(state, legal_actions)`:
  1. `FixedStrongPolicy` (policy_id: "fixed_strong")
  2. `FixedCheapPolicy` (policy_id: "fixed_cheap")
  3. `RandomPolicy` (policy_id: "random")
  4. `RuleStickyPolicy` (policy_id: "rule_sticky")
  5. `RouteLLMPolicy` (policy_id: "routellm") - example threshold parameters
  6. `SRKNNPolicy` (policy_id: "sr_knn") - example 8D reference vectors
  7. `LayaServerPolicy` (policy_id: "laya_v2") - remote A6000 Laya Serving API
  8. `KevServerPolicy` (policy_id: "kev_4b") - remote A6000 Kev Serving API
"""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4
from modelrouter.providers.registry import ModelRegistry

try:
    from modelrouter.baselines.routellm_adapter import RouteLLMAdapter
    from modelrouter.baselines.sr_knn_adapter import SRKNNAdapter
    from modelrouter.agent.router_clients import MockRouter, RouterClient, RouterDecision
    from modelrouter.agent.state import AgentState
except ImportError:
    from experiments.agent_pilot.baselines.routellm_adapter import RouteLLMAdapter
    from experiments.agent_pilot.baselines.sr_knn_adapter import SRKNNAdapter
    from experiments.agent_pilot.router_clients import MockRouter, RouterClient, RouterDecision
    from experiments.agent_pilot.state import AgentState

logger = logging.getLogger("experiments.agent_pilot.policy")


class BasePolicy:
    """Abstract base class for all routing policies."""

    implementation_status = "CONFIGURED_POLICY"

    def __init__(self, policy_id: str):
        self.policy_id = policy_id

    @staticmethod
    def _snapshot(state):
        if hasattr(state, "pre_decision_snapshot"):
            return state.pre_decision_snapshot
        return state.build_pre_decision_snapshot().to_dict()

    @staticmethod
    def _price_order(actions):
        """Order declared input/output unit prices without changing model pools."""
        registry = ModelRegistry()
        def key(action):
            spec = registry.get_spec(action["model"])
            return (spec.input_price_per_1m + spec.output_price_per_1m,
                    action["model"], action.get("native_effort", "none"))
        return sorted(actions, key=key)

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        """Mandatory selection interface required by V8 §7.3 / §9.2."""
        raise NotImplementedError

    def route(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        """Alias to select() ensuring backward compatibility with existing agent runners."""
        return self.select(state, legal_actions)


class RandomPolicy(BasePolicy):
    """Uniform random selection across all legal (model, native_effort) pairs."""

    def __init__(self, seed: int = 42):
        super().__init__("random")
        self.rng = random.Random(seed)

    def select(
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
            confidence=1.0 / len(legal_actions) if legal_actions else 0.5,
        )


class FixedStrongPolicy(BasePolicy):
    """Use the configured strong model, or the higher declared price endpoint."""

    def __init__(self, target_model: str = "gpt-4o-2024-08-06"):
        super().__init__("fixed_strong")
        self.target_model = target_model

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        matches = [a for a in legal_actions if a.get("model") == self.target_model]
        if not matches:
            matches = list(reversed(self._price_order(legal_actions)))
        selected = matches[0]
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
    """Use the configured cheap model, or the lower declared price endpoint."""

    def __init__(self, target_model: str = "deepseek-chat"):
        super().__init__("fixed_cheap")
        self.target_model = target_model

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        matches = [a for a in legal_actions if a.get("model") == self.target_model]
        if not matches:
            matches = self._price_order(legal_actions)
        selected = matches[0]
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

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = self._snapshot(state)
        phase = snapshot["phase"]
        budget_remaining = snapshot["budget_remaining_usd"]

        priced = self._price_order(legal_actions)
        fast_actions = [a for a in priced if a.get("pool") == "Fast"] or [priced[0]]
        standard_actions = [a for a in priced if a.get("pool") == "Standard"] or [priced[-1]]
        reasoning_actions = [a for a in reversed(priced) if a.get("pool") == "Reasoning"]

        # Budget constraint overrides phase
        if budget_remaining < 0.30 and fast_actions:
            selected = fast_actions[0]
            conf = 0.95
        elif snapshot["last_tool_exit_code"] != 0 and reasoning_actions:
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
    """Reuse the existing threshold calculation with unverified example weights."""

    implementation_status = "UNVERIFIED_EXAMPLE"

    def __init__(self, threshold: float = 0.55):
        super().__init__("routellm")
        self.threshold = threshold
        self.adapter = RouteLLMAdapter(threshold=threshold)
        self.adapter.status = self.implementation_status

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = self._snapshot(state)

        score = self.adapter.compute_difficulty(
            instruction=getattr(state, "task_prompt", snapshot["task_id"]),
            history_steps=snapshot["step_index"],
            max_steps=state.max_steps,
            context_tokens=snapshot["context_tokens_approx"],
            last_exit_code=snapshot["last_tool_exit_code"],
            tool_error_count=state.tool_error_count,
            budget_remaining_ratio=snapshot["budget_remaining_usd"] / state.usd_budget,
        )
        score.algorithm_status = self.implementation_status

        priced = self._price_order(legal_actions)
        fast_actions = [a for a in priced if a.get("pool") == "Fast"] or [priced[0]]
        strong_actions = [a for a in reversed(priced) if a.get("pool") in ("Strong", "Reasoning")]

        if score.win_rate >= self.threshold and strong_actions:
            selected = strong_actions[0]
        elif fast_actions:
            selected = fast_actions[0]
        else:
            selected = legal_actions[0]

        lat_ms = (time.time() - t0) * 1000

        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_routellm",
            checkpoint_id=self.implementation_status,
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=lat_ms,
            fallback_used=False,
            confidence=score.win_rate,
        )


class SRKNNPolicy(BasePolicy):
    """Reuse existing 8D voting with unverified example reference vectors."""

    implementation_status = "UNVERIFIED_EXAMPLE"

    def __init__(self, k: int = 3):
        super().__init__("sr_knn")
        self.k = k
        self.adapter = SRKNNAdapter(k=k)
        self.adapter.status = self.implementation_status

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = self._snapshot(state)

        vec = self.adapter.extract_vector(
            step_index=snapshot["step_index"],
            max_steps=state.max_steps,
            phase=snapshot["phase"],
            last_exit_code=snapshot["last_tool_exit_code"],
            context_tokens=snapshot["context_tokens_approx"],
            budget_remaining_ratio=snapshot["budget_remaining_usd"] / state.usd_budget,
            tool_error_count=state.tool_error_count,
        )

        pred = self.adapter.predict(vec)
        tier = pred["predicted_tier"]

        # Preference matching based on predicted tier
        tier_pref_order = {
            "Fast": ["Fast", "Standard"],
            "Standard": ["Standard", "Fast", "Strong"],
            "Strong": ["Strong", "Reasoning", "Standard"],
            "Reasoning": ["Reasoning", "Strong", "Standard"],
        }.get(tier, ["Fast"])

        selected = None
        priced = self._price_order(legal_actions)
        preferred = list(reversed(priced)) if tier in ("Strong", "Reasoning") else priced
        for pool in tier_pref_order:
            matches = [a for a in preferred if a.get("pool") == pool]
            if matches:
                selected = matches[0]
                break
        if not selected:
            selected = preferred[0]

        lat_ms = (time.time() - t0) * 1000

        return RouterDecision(
            request_id=str(uuid4()),
            router_family="baseline_sr_knn",
            checkpoint_id=self.implementation_status,
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=lat_ms,
            fallback_used=False,
            confidence=pred["confidence"],
        )


class LayaServerPolicy(BasePolicy):
    """Routes using the remote Laya Serving API (with automatic fallback)."""

    implementation_status = "REMOTE_NEURAL_ROUTER"

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__("laya_v2")
        self.client = RouterClient(endpoint=endpoint, router_family="laya")

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        snapshot = self._snapshot(state)
        decision_id = f"dec_{state.episode_id}_{state.step_index}"
        return self.client.route(
            episode_id=state.episode_id,
            decision_id=decision_id,
            pre_decision_state=snapshot,
            legal_actions=legal_actions,
            policy_version="laya_v2.1",
        )


class KevServerPolicy(BasePolicy):
    """Routes using the remote Kev Serving API (with automatic fallback)."""

    implementation_status = "REMOTE_NEURAL_ROUTER"

    def __init__(self, endpoint: Optional[str] = None):
        super().__init__("kev_4b")
        self.client = RouterClient(endpoint=endpoint, router_family="kev")

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        snapshot = self._snapshot(state)
        decision_id = f"dec_{state.episode_id}_{state.step_index}"
        return self.client.route(
            episode_id=state.episode_id,
            decision_id=decision_id,
            pre_decision_state=snapshot,
            legal_actions=legal_actions,
            policy_version="kev_v8.0",
        )


class LengthHeuristicPolicy(BasePolicy):
    """Simple baseline heuristic routing based strictly on prompt/instruction character length."""

    def __init__(self, threshold_chars: int = 600):
        super().__init__("length_heuristic")
        self.threshold_chars = threshold_chars

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = state.build_pre_decision_snapshot()
        prompt_len = getattr(snapshot, "context_chars", len(getattr(snapshot, "task_id", "")))
        strong_actions = [a for a in legal_actions if a.get("pool") in ("Strong", "Reasoning") or "gpt-6" in a.get("model", "")]
        cheap_actions = [a for a in legal_actions if a.get("pool") in ("Fast", "Standard") or "gpt-5.6" in a.get("model", "")]
        if prompt_len > self.threshold_chars and strong_actions:
            selected = strong_actions[0]
        elif cheap_actions:
            selected = cheap_actions[0]
        else:
            selected = legal_actions[0]
        return RouterDecision(
            request_id=str(uuid4()),
            router_family="heuristic_length",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=0.6,
        )


class StepHeuristicPolicy(BasePolicy):
    """Simple baseline heuristic routing based strictly on step index."""

    def __init__(self):
        super().__init__("step_heuristic")

    def select(
        self,
        state: AgentState,
        legal_actions: List[Dict[str, Any]],
    ) -> RouterDecision:
        t0 = time.time()
        snapshot = state.build_pre_decision_snapshot()
        step = snapshot.step_index
        strong_actions = [a for a in legal_actions if a.get("pool") in ("Strong", "Reasoning") or "gpt-6" in a.get("model", "")]
        cheap_actions = [a for a in legal_actions if a.get("pool") in ("Fast", "Standard") or "gpt-5.6" in a.get("model", "")]
        if step % 2 == 0 and strong_actions:
            selected = strong_actions[0]
        elif cheap_actions:
            selected = cheap_actions[0]
        else:
            selected = legal_actions[0]
        return RouterDecision(
            request_id=str(uuid4()),
            router_family="heuristic_step",
            checkpoint_id="none",
            selected_action=selected,
            ranked_actions=[selected],
            decision_latency_ms=(time.time() - t0) * 1000,
            fallback_used=False,
            confidence=0.6,
        )


def create_policy(policy_name: str, **kwargs) -> BasePolicy:
    """Factory to instantiate policies by name."""
    p = policy_name.lower().replace("-", "_")
    if p in ("random", "baseline_random"):
        return RandomPolicy(seed=kwargs.get("seed", 42))
    elif p in ("fixed_strong", "strong"):
        return FixedStrongPolicy(target_model=kwargs.get("target_model", "gpt-4o-2024-08-06"))
    elif p in ("luna", "fixed_luna", "gpt_6_luna", "gpt-6-luna"):
        return FixedStrongPolicy(target_model="gpt-6-luna")
    elif p in ("fixed_cheap", "cheap", "fast"):
        return FixedCheapPolicy(target_model=kwargs.get("target_model", "deepseek-chat"))
    elif p in ("rule_sticky", "rule"):
        return RuleStickyPolicy()
    elif p in ("length_heuristic", "length"):
        return LengthHeuristicPolicy(threshold_chars=kwargs.get("threshold_chars", 600))
    elif p in ("step_heuristic", "step"):
        return StepHeuristicPolicy()
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
