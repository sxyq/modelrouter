"""Fixed, random, sticky and heuristic controls; real Laya/Kev native routing."""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4
from modelrouter.providers.registry import ModelRegistry

from modelrouter.agent.router_clients import RouterClient, RouterDecision
from modelrouter.agent.state import AgentState

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
            raise ValueError(f"Fixed model is unavailable: {self.target_model}")
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
            raise ValueError(f"Fixed model is unavailable: {self.target_model}")
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
        if budget_remaining is not None and budget_remaining < 0.30 and fast_actions:
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




class LayaServerPolicy(BasePolicy):
    """Routes using the real Laya Serving API."""

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
    """Routes using the real Kev Serving API."""

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
    elif p in ("laya", "laya_v2", "laya_server"):
        return LayaServerPolicy(endpoint=kwargs.get("endpoint"))
    elif p in ("kev", "kev_4b", "kev_server"):
        return KevServerPolicy(endpoint=kwargs.get("endpoint"))
    else:
        raise ValueError(f"Unknown policy name: {policy_name}")
