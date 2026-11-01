"""Use the existing native Adapter for an experimental server checkpoint."""
from __future__ import annotations

import json
import select
import subprocess
import sys
import time
from pathlib import Path
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
        target, instruction = MODEL_TARGETS["STEP_LEVEL_PREFERENCE"]
        payload = {
            "checkpoint_path": self.checkpoint["path"],
            "state": PreDecisionState.model_validate(pre_decision_state).router_text(),
            "questions": {target: {
                "type": "choice", "instructions": instruction,
                "criteria": {model: model for model in actions},
            }},
        }
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
        answers, latency, usage = adapter.system_one(payload["state"], payload["questions"])
        print(json.dumps({"answers": answers, "decision_latency_ms": latency, "usage": usage,
                          "initialization_latency_ms": initialization_ms, "process_reused": reused,
                          "run_id": run["run_id"], "checkpoint_id": f"{run['run_id']}-e{run['epoch']:02d}",
                          "weights_path": str(checkpoint)}), flush=True)


if __name__ == "__main__":
    main()
