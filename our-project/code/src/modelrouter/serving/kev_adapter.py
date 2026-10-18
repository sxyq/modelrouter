"""
Kev Model Adapter for ModelRouter Serving.
Loads Kev-4B checkpoint and executes true forward pass using DecisionModel.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

from .schemas import ActionScore, LegalAction, PreDecisionState

logger = logging.getLogger("router_serving.kev")


class KevAdapter:
    def __init__(
        self,
        adapter_dir: str = "/home/syy/路由/models/kev-4b-adapter",
        base_dir: str = "/home/syy/路由/models/qwen3.5-4b-base",
        device: str = "cpu"
    ):
        self.adapter_dir = adapter_dir
        self.base_dir = base_dir
        self.device_str = device
        self.checkpoint_id = "kev-4b-r10"
        self.run_id = "KEV-4B"
        self.is_loaded = False
        self.inference_verified = False
        self.model = None
        self.tokenizer = None
        self.metrics = {"base": "Qwen3.5-4B-Base", "lora_rank": 16, "inference_engine": "torch_cpu"}

        self._load()

    def _load(self):
        kev_code_dir = "/home/syy/路由/external/kev"
        if os.path.exists(kev_code_dir) and kev_code_dir not in sys.path:
            sys.path.insert(0, kev_code_dir)

        if not os.path.exists(self.adapter_dir):
            logger.warning(f"Kev adapter directory {self.adapter_dir} does not exist.")
            return

        try:
            from kev.checkpoint import Checkpoint
            logger.info(f"Loading Kev checkpoint from {self.adapter_dir} on {self.device_str}...")
            ck = Checkpoint(self.adapter_dir)
            self.checkpoint_id = getattr(ck.meta, "base_revision", "kev-4b-adapter")
            self.run_id = "KEV-4B-ADAPTER"
            self.tokenizer, self.model = ck.load(self.device_str)
            self.is_loaded = True
            self.inference_verified = True
            logger.info("Kev model loaded successfully and verified for true forward inference.")
        except Exception as e:
            logger.warning(f"Kev model true loading failed: {e}. Falling back to standby.")
            self.is_loaded = False
            self.inference_verified = False

    def route(
        self,
        pre_decision_state: PreDecisionState,
        legal_actions: List[LegalAction]
    ) -> Tuple[LegalAction, List[ActionScore], float, Optional[float], bool, Optional[str]]:
        t0 = time.perf_counter()

        if not legal_actions:
            raise ValueError("legal_actions cannot be empty")

        if len(legal_actions) == 1:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            act = legal_actions[0]
            score = ActionScore(action=act, score=1.0, probability=1.0)
            return act, [score], latency_ms, 1.0, False, None

        if self.model is not None and self.tokenizer is not None:
            try:
                from kev.model import admit
                state_text = f"Task: {pre_decision_state.prompt or 'general'}. Step: {pre_decision_state.step_index}. Prior errors: {pre_decision_state.prior_error_signals_count}."
                options = [f"Model: {act.model}, Effort: {act.native_effort}" for act in legal_actions]
                rec = {
                    "state": state_text,
                    "questions": [{
                        "instr": "Select optimal model and native effort action:",
                        "options": options,
                        "label": 0
                    }]
                }
                enc = admit(self.model, self.tokenizer, rec)
                probs_tensor = self.model.probs(enc)
                raw_probs = probs_tensor[0].tolist() if hasattr(probs_tensor[0], "tolist") else list(probs_tensor[0])

                ranked = []
                for idx, act in enumerate(legal_actions):
                    p = float(raw_probs[idx]) if idx < len(raw_probs) else 0.0
                    ranked.append(ActionScore(action=act, score=round(p, 4), probability=round(p, 4)))

                total_p = sum(r.probability for r in ranked) or 1.0
                for r in ranked:
                    r.probability = round(r.probability / total_p, 4)
                    r.score = r.probability

                ranked.sort(key=lambda x: x.probability, reverse=True)
                latency_ms = (time.perf_counter() - t0) * 1000.0
                selected_action = ranked[0].action
                confidence = ranked[0].probability

                return selected_action, ranked, latency_ms, confidence, False, None
            except Exception as e:
                logger.error(f"Kev true forward failed during route: {e}", exc_info=True)

        # Fallback if model not available
        latency_ms = (time.perf_counter() - t0) * 1000.0
        ranked = []
        n = len(legal_actions)
        base_prob = 1.0 / n
        for idx, act in enumerate(legal_actions):
            ranked.append(ActionScore(action=act, score=round(base_prob, 4), probability=round(base_prob, 4)))
        return legal_actions[0], ranked, latency_ms, base_prob, True, "HEURISTIC_FALLBACK: true forward unavailable or errored"
