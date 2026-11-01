"""Use the existing native Adapter for an experimental server checkpoint."""
from __future__ import annotations

import json
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

    def route(self, *, pre_decision_state, legal_actions, **_):
        actions = {action["model"]: action for action in legal_actions}
        payload = {
            "checkpoint_path": self.checkpoint["path"],
            "state": PreDecisionState.model_validate(pre_decision_state).router_text(),
            "questions": {"route_decision": {
                "type": "choice", "instructions": MODEL_TARGETS["STEP_LEVEL_PREFERENCE"][1],
                "criteria": {model: model for model in sorted(actions)},
            }},
        }
        started = time.perf_counter()
        result = subprocess.run(self.checkpoint["command"], input=json.dumps(payload),
                                capture_output=True, text=True, check=True, timeout=self.timeout)
        body = json.loads(result.stdout)
        answer = body["answers"]["route_decision"]
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
                             "router_identity_source": "SERVER_NATIVE_ADAPTER_OVER_SSH_STDIO",
                             "router_identity_status": "SERVER_NATIVE_CHECKPOINT_METADATA"},
        )


def main():
    from modelrouter.serving.laya_adapter import LayaAdapter

    payload = json.load(sys.stdin)
    checkpoint = Path(payload["checkpoint_path"]).resolve()
    run = json.loads((checkpoint / "rl_agent_config.json").read_text())["training_run"]
    adapter = LayaAdapter(model_dir=str(checkpoint), device="cpu")
    answers, latency, usage = adapter.system_one(payload["state"], payload["questions"])
    json.dump({"answers": answers, "decision_latency_ms": latency, "usage": usage,
               "run_id": run["run_id"], "checkpoint_id": f"{run['run_id']}-e{run['epoch']:02d}",
               "weights_path": str(checkpoint)}, sys.stdout)


if __name__ == "__main__":
    main()
