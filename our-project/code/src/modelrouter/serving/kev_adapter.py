"""
Kev Model Adapter for ModelRouter Serving.
Loads Kev-4B checkpoint and executes true forward pass using DecisionModel.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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

        from kev.checkpoint import Checkpoint
        logger.info(f"Loading Kev checkpoint from {self.adapter_dir} on {self.device_str}...")
        ck = Checkpoint(self.adapter_dir)
        self.checkpoint_id = str(Path(self.adapter_dir).resolve())
        self.metrics["base_revision"] = ck.meta.base_revision
        self.run_id = Path(self.adapter_dir).name
        self.tokenizer, self.model = ck.load(self.device_str)
        self.is_loaded = True
        logger.info("Kev model loaded successfully; inference has not yet run.")

    def system_one(
        self,
        state: Any,
        questions: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], float, Optional[Dict[str, Any]]]:
        t0 = time.perf_counter()
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("NO_MODEL_LOADED: Kev model or tokenizer is not loaded")

        from kev.api import SystemOneRequest as KevSysOneReq, to_record, to_answers, output_tokens
        from kev.model import admit, SERVE_MAX_STATE

        kev_req = KevSysOneReq(state=state, model="kev-4b", questions=questions)
        rec, meta = to_record(kev_req)
        enc = admit(self.model, self.tokenizer, rec)
        probs_tensor = self.model.probs(enc)
        self.inference_verified = True
        raw_probs = [p.tolist() if hasattr(p, "tolist") else list(p) for p in probs_tensor]
        answers = to_answers(raw_probs, meta)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        n_tokens = len(enc.get("ids", []))
        usage = {
            "input_tokens": n_tokens,
            "output_tokens": output_tokens(self.tokenizer, answers),
            "state_tokens": enc["state_tokens"],
            "state_limit_tokens": SERVE_MAX_STATE,
            "truncated": enc["state_truncated"],
        }
        from modelrouter.v9.runtime.context import encoded_group_coverage
        usage["state_group_coverage"] = encoded_group_coverage(state, self.tokenizer)
        return answers, latency_ms, usage

