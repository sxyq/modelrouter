"""Use the existing native Adapter for an experimental server checkpoint."""
from __future__ import annotations

import json
import fcntl
import select
import subprocess
import sys
import time
from pathlib import Path
from contextlib import nullcontext
from uuid import uuid4

from modelrouter.agent.router_clients import RouterDecision
from modelrouter.serving.schemas import PreDecisionState
from modelrouter.v9.training.real_supervision import MODEL_TARGETS


class CheckpointRouterClient:
    def __init__(self, config):
        self.checkpoint = config["router_checkpoint"]
        self.timeout = config.get("router_timeout_sec", 20.0)
        self.process = None

    def route(self, *, pre_decision_state, legal_actions, **_):
        actions = {action["model"]: action for action in legal_actions}
        if len(actions) != len(legal_actions):
            raise ValueError(
                "Checkpoint MODEL_ONLY routing requires one action per model; "
                "multiple Native Effort actions for the same model are unsupported"
            )
        target, instruction = MODEL_TARGETS["STEP_LEVEL_PREFERENCE"]
        payload = {
            "checkpoint_path": self.checkpoint["path"],
            "device": self.checkpoint.get("device", "cpu"),
            "state": PreDecisionState.model_validate(pre_decision_state).router_text(),
            "questions": {target: {
                "type": "choice", "instructions": instruction,
                "criteria": {model: model for model in actions},
            }},
        }
        if payload["device"] == "cuda":
            payload["gpu_lock_path"] = self.checkpoint["gpu_lock_path"]
        started = time.perf_counter()
        if self.process is None:
            self.process = subprocess.Popen(self.checkpoint["command"], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, text=True)
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()
        if not select.select([self.process.stdout], [], [], self.timeout)[0]:
            raise subprocess.TimeoutExpired(self.checkpoint["command"], self.timeout)
        body = json.loads(self.process.stdout.readline())
        answer = body["answers"][target]
        probabilities = answer["probabilities"]
        return RouterDecision(
            request_id=str(uuid4()), router_family="laya", checkpoint_id=body["checkpoint_id"],
            selected_action=actions[answer["choice"]],
            ranked_actions=[{"action": actions[model], "score": probability, "probability": probability}
                            for model, probability in sorted(probabilities.items(),
                                                              key=lambda item: item[1], reverse=True)],
            decision_latency_ms=(time.perf_counter() - started) * 1000,
            inference_latency_ms=body["decision_latency_ms"], confidence=answer.get("confidence"),
            router_identity={"router_run_id": body["run_id"],
                             "router_weights_path": body["weights_path"],
                             "router_initialization_ms": body["initialization_latency_ms"],
                             "router_process_reused": body["process_reused"],
                             "router_device": body["device"],
                             "router_gpu_wait_ms": body["gpu_wait_ms"],
                             "router_device_transfer_ms": body["device_transfer_ms"],
                             "router_question_id": target,
                             "router_candidate_order": list(actions),
                             "router_identity_source": "SERVER_NATIVE_ADAPTER_OVER_SSH_STDIO",
                             "router_identity_status": "SERVER_NATIVE_CHECKPOINT_METADATA"},
        )

    def close(self):
        if self.process is not None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None


def main():
    initialized = time.perf_counter()
    import torch
    from modelrouter.serving.laya_adapter import LayaAdapter

    adapter = None
    for line in sys.stdin:
        payload = json.loads(line)
        reused = adapter is not None
        initialization_ms = 0.0
        if not reused:
            checkpoint = Path(payload["checkpoint_path"]).resolve()
            run = json.loads((checkpoint / "rl_agent_config.json").read_text())["training_run"]
            adapter = LayaAdapter(model_dir=str(checkpoint), device="cpu")
            initialization_ms = (time.perf_counter() - initialized) * 1000
        device = payload.get("device", "cpu")
        gpu_wait_ms, transfer_ms = 0.0, 0.0
        lock = open(payload["gpu_lock_path"], "a") if device == "cuda" else nullcontext()
        with lock as lock_file:
            try:
                if device == "cuda":
                    from laya.agent import _cuda_amp_dtype
                    before = time.perf_counter()
                    fcntl.flock(lock_file, fcntl.LOCK_EX)
                    gpu_wait_ms = (time.perf_counter() - before) * 1000
                    before = time.perf_counter()
                    adapter.agent.model.to("cuda")
                    adapter.agent.device = torch.device("cuda")
                    adapter.agent.dtype = _cuda_amp_dtype(adapter.agent.cfg.get("amp_dtype", "fp16"))
                    adapter.agent.amp_enabled = True
                    transfer_ms += (time.perf_counter() - before) * 1000
                with torch.inference_mode():
                    answers, latency, usage = adapter.system_one(payload["state"], payload["questions"])
            finally:
                if device == "cuda":
                    before = time.perf_counter()
                    adapter.agent.model.to("cpu")
                    adapter.agent.device = torch.device("cpu")
                    adapter.agent.dtype = torch.float32
                    adapter.agent.amp_enabled = False
                    torch.cuda.empty_cache()
                    transfer_ms += (time.perf_counter() - before) * 1000
        print(json.dumps({"answers": answers, "decision_latency_ms": latency, "usage": usage,
                          "initialization_latency_ms": initialization_ms, "process_reused": reused,
                          "device": device, "gpu_wait_ms": gpu_wait_ms, "device_transfer_ms": transfer_ms,
                          "run_id": run["run_id"], "checkpoint_id": f"{run['run_id']}-e{run['epoch']:02d}",
                          "weights_path": str(checkpoint)}), flush=True)


if __name__ == "__main__":
    main()
