"""
Laya Model Adapter for ModelRouter Serving.
Loads physical weights from A6000 and exposes predict() conforming to V8 §7.1.
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from .schemas import ActionScore, LegalAction, PreDecisionState

logger = logging.getLogger("router_serving.laya")


class LayaAdapter:
    def __init__(
        self,
        model_dir: str = "/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/checkpoints/best",
        fallback_dir: str = "/home/syy/路由/models/laya-421m",
        device: Optional[str] = None
    ):
        self.model_dir = model_dir
        self.fallback_dir = fallback_dir
        self.device_str = device
        self.agent = None
        self.checkpoint_id = "unknown"
        self.run_id = "unknown"
        self.is_loaded = False
        self.metrics = {}

        self._load()

    def _load(self):
        # Resolve best target dir
        target_dir = self.model_dir
        if not os.path.exists(os.path.join(target_dir, "model.safetensors")):
            logger.warning(f"Target model_dir {target_dir} not found or missing safetensors. Falling back to {self.fallback_dir}")
            target_dir = self.fallback_dir

        if not os.path.exists(os.path.join(target_dir, "model.safetensors")):
            raise FileNotFoundError(f"No valid Laya weights found in {self.model_dir} or {self.fallback_dir}")

        # Ensure models/laya-421m is in sys.path for rl_common
        laya_code_dir = self.fallback_dir
        if laya_code_dir not in sys.path:
            sys.path.insert(0, laya_code_dir)

        # Import RLAgent
        try:
            from rl_agent_api import RLAgent
        except ImportError:
            # Try finding rl_agent_api in parent
            sys.path.insert(0, os.path.abspath(os.path.join(laya_code_dir, "..")))
            from rl_agent_api import RLAgent

        # Check recovery/metrics
        rec_path = os.path.join(target_dir, "recovery_state.json")
        if os.path.exists(rec_path):
            try:
                with open(rec_path, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                    self.checkpoint_id = rec.get("checkpoint_id", os.path.basename(os.path.realpath(target_dir)))
                    self.run_id = rec.get("run_id", "F05")
                    self.metrics = rec.get("metrics", {})
            except Exception as e:
                logger.warning(f"Could not read recovery_state.json: {e}")
        else:
            self.checkpoint_id = os.path.basename(os.path.realpath(target_dir))
            self.run_id = "F05" if "F05" in target_dir else "laya-base"

        logger.info(f"Loading Laya RLAgent from {target_dir} on device={self.device_str or 'auto'}...")
        t0 = time.time()
        self.agent = RLAgent(target_dir, device=self.device_str)
        load_time = time.time() - t0
        self.is_loaded = True
        logger.info(f"Laya RLAgent loaded successfully in {load_time:.2f}s (run={self.run_id}, ckpt={self.checkpoint_id}).")

    def route(
        self,
        pre_decision_state: PreDecisionState,
        legal_actions: List[LegalAction]
    ) -> Tuple[LegalAction, List[ActionScore], float, Optional[float]]:
        """
        Routes the pre-decision state across legal_actions.
        Returns: (selected_action, ranked_action_scores, latency_ms, confidence)
        """
        t0 = time.perf_counter()

        if not legal_actions:
            raise ValueError("legal_actions cannot be empty")

        if len(legal_actions) == 1:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            act = legal_actions[0]
            score = ActionScore(action=act, score=1.0, probability=1.0)
            return act, [score], latency_ms, 1.0

        # Construct candidate option mapping
        # Keys must be string identifiers
        criteria = {}
        key_to_action = {}
        for idx, act in enumerate(legal_actions):
            key = f"opt_{idx}_{act.provider}_{act.model}_{act.native_effort}".replace("/", "_").replace(".", "_")
            desc = f"{act.provider}/{act.model} (effort={act.native_effort})"
            criteria[key] = desc
            key_to_action[key] = act

        # Format state
        prompt_snippet = pre_decision_state.prompt or ""
        history_snippet = pre_decision_state.history_snippet or ""
        state_text = (
            f"Domain: {pre_decision_state.task_domain or 'code'}\n"
            f"Step: {pre_decision_state.step_index or 0}\n"
            f"Prior Tool Calls: {pre_decision_state.prior_tool_calls_count or 0}\n"
            f"Prior Errors: {pre_decision_state.prior_error_signals_count or 0}\n"
            f"Context snippet: {prompt_snippet[:1500]}\n"
            f"History: {history_snippet[:500]}"
        )

        questions = {
            "route_decision": {
                "type": "choice",
                "instructions": "Select the optimal model and reasoning effort for the next agent execution step.",
                "criteria": criteria
            }
        }

        # Run inference
        res = self.agent.system_one(state_text, questions)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        q_ans = res["answers"]["route_decision"]
        selected_key = q_ans["choice"]
        probs = q_ans.get("probabilities", {})
        confidence = q_ans.get("confidence", 0.0)

        # Selected action
        selected_action = key_to_action.get(selected_key, legal_actions[0])

        # Rank all actions
        ranked = []
        for k, act in key_to_action.items():
            prob = float(probs.get(k, 0.0))
            ranked.append(ActionScore(action=act, score=prob, probability=prob))

        ranked.sort(key=lambda x: x.probability, reverse=True)

        return selected_action, ranked, latency_ms, confidence

    def system_one(
        self,
        state: Any,
        questions: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], float, Optional[Dict[str, Any]]]:
        t0 = time.perf_counter()
        if not self.is_loaded or self.agent is None:
            raise RuntimeError("NO_MODEL_LOADED: Laya RLAgent is not loaded")

        formatted_questions = {}
        for qid, q in questions.items():
            if hasattr(q, "model_dump"):
                q_dict = q.model_dump()
            elif hasattr(q, "dict"):
                q_dict = q.dict()
            elif isinstance(q, dict):
                q_dict = dict(q)
            else:
                q_dict = {
                    "type": getattr(q, "type", "choice"),
                    "instructions": getattr(q, "instructions", ""),
                    "criteria": getattr(q, "criteria", {})
                }
            formatted_questions[qid] = q_dict

        res = self.agent.system_one(state, formatted_questions)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return res["answers"], latency_ms, res.get("usage")

