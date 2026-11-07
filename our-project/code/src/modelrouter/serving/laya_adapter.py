"""
Laya Model Adapter for ModelRouter Serving.
Loads physical weights from A6000 and exposes predict() conforming to V8 §7.1.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger("router_serving.laya")


class LayaAdapter:
    def __init__(
        self,
        model_dir: str = "/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/checkpoints/best",
        device: Optional[str] = None
    ):
        self.model_dir = model_dir
        self.device_str = device
        self.agent = None
        self.checkpoint_id = "unknown"
        self.run_id = "unknown"
        self.is_loaded = False
        self.inference_verified = False
        self.metrics = {}

        self._load()

    def _load(self):
        # Resolve best target dir
        target_dir = self.model_dir
        if not os.path.exists(os.path.join(target_dir, "model.safetensors")):
            raise FileNotFoundError(f"No Laya weights found in the requested checkpoint: {target_dir}")

        sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "external/laya"))
        from laya import load
        import torch

        # SDPA avoids the slower fused CPU attention path on these long states.
        torch.backends.mha.set_fastpath_enabled(False)

        # Check recovery/metrics
        rec_path = os.path.join(target_dir, "recovery_state.json")
        if os.path.exists(rec_path):
            try:
                with open(rec_path, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                    self.checkpoint_id = rec.get("checkpoint_id", os.path.basename(os.path.realpath(target_dir)))
                    self.run_id = rec.get("run_id", os.path.basename(os.path.realpath(target_dir)))
                    self.metrics = rec.get("metrics", {})
            except Exception as e:
                logger.warning(f"Could not read recovery_state.json: {e}")
        else:
            self.checkpoint_id = os.path.basename(os.path.realpath(target_dir))
            self.run_id = self.checkpoint_id

        logger.info(f"Loading Laya RLAgent from {target_dir} on device={self.device_str or 'auto'}...")
        t0 = time.time()
        self.agent = load(target_dir, device=self.device_str, backend="eager")
        load_time = time.time() - t0
        self.is_loaded = True
        logger.info(f"Laya RLAgent loaded successfully in {load_time:.2f}s (run={self.run_id}, ckpt={self.checkpoint_id}).")

    def system_one(
        self,
        state: Any,
        questions: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], float, Optional[Dict[str, Any]]]:
        t0 = time.perf_counter()
        if not self.is_loaded or self.agent is None:
            raise RuntimeError("NO_MODEL_LOADED: Laya RLAgent is not loaded")

        res = self.agent.system_one(state, questions)
        self.inference_verified = True
        latency_ms = (time.perf_counter() - t0) * 1000.0
        if res.get("usage") is not None:
            from modelrouter.v9.runtime.context import encoded_group_coverage
            res["usage"]["state_group_coverage"] = encoded_group_coverage(
                state, self.agent.tok, res["usage"].get("state_tokens_dropped", 0))
        return res["answers"], latency_ms, res.get("usage")

