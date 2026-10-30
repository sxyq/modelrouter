"""Run the original mini-SWE-agent on an isolated local development workspace."""
from __future__ import annotations

import json
import os
import subprocess
import time
from contextlib import ExitStack
from importlib.metadata import version
from pathlib import Path

from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted

from modelrouter.agent.state import AgentState, EpisodeStatus
from modelrouter.benchmark.iterations import event, now, write_atomic
from modelrouter.telemetry.ledger import ExperimentLedger
from .alias import alias_provider, DEFAULT_BACKEND_DEPLOYMENT_STATUS
from .context import record_tool_result


def api_key_names(config):
    names = {name for name in os.environ if name == "API_KEY" or name.endswith("_API_KEY")}
    names.update(("OPENAI_API_KEY", "QWEN_API_KEY", "MODELROUTER_GENERATOR_API_KEY",
                  "MODELROUTER_ALIAS_API_KEY"))
    names.update(config[name] for name in ("api_key_env", "teacher_api_key_env") if config.get(name))
    return names


class RecordedLocalEnvironment(LocalEnvironment):
    """Add observations to the existing state; upstream executes and submits."""

    def __init__(self, *, state, record_dir, api_key_env_names=(), **kwargs):
        self._api_key_env_names = api_key_names({}) | set(api_key_env_names)
        overrides = dict(kwargs.pop("env", {}))
        overrides.update({name: "" for name in self._api_key_env_names})
        super().__init__(env=overrides, **kwargs)
        self.state, self.record_dir = state, record_dir

    def get_template_vars(self, **kwargs):
        return {name: value for name, value in super().get_template_vars(**kwargs).items()
                if name not in self._api_key_env_names}

    def execute(self, action, cwd="", *, timeout=None):
        self._active_action, self._tool_started = action, time.perf_counter()
        return super().execute(action, cwd, timeout=timeout)

    def _check_finished(self, output):
        duration = (time.perf_counter() - self._tool_started) * 1000
        try:
            super()._check_finished(output)
        except Submitted:
            record_tool_result(self.state, self.record_dir, self._active_action, output,
                               duration, submission=True)
            raise
        record_tool_result(self.state, self.record_dir, self._active_action, output, duration)


def run_development(*, workspace: Path, instruction: str, verify_command: str,
                    config: dict, record_dir: Path, task_id: str, policy="laya_v2",
                    max_steps=15, max_output_tokens=4096, api_key=None) -> dict:
    """One upstream episode; local verification is never an official score."""
    with ExitStack() as runtime_environment:
        runtime_options = {"MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT": "1",
                           "LITELLM_LOCAL_MODEL_COST_MAP": "true"}
        for name, value in runtime_options.items():
            previous = os.environ.get(name)
            if previous is None:
                runtime_environment.callback(os.environ.pop, name, None)
            else:
                runtime_environment.callback(os.environ.__setitem__, name, previous)
            os.environ[name] = value
        from minisweagent.agents.default import DefaultAgent
        from modelrouter.benchmark.harbor_agent import PolicyModel, mini_configuration

        workspace, record_dir = workspace.resolve(), record_dir.resolve()
        instruction = f"{instruction}\n\nWorkspace and initial working directory (absolute CWD): {workspace}"
        record_dir.mkdir(parents=True, exist_ok=True)
        provider = alias_provider(config, api_key)
        state = AgentState(task_id=task_id, episode_id=record_dir.name, policy_id=policy,
                           max_steps=max_steps, usd_budget=0)
        state.task_prompt = instruction
        started = time.perf_counter()
        run_config = {
            **{key: value for key, value in config.items() if key not in ("api_key", "teacher_api_key")},
            "task_id": task_id, "policy": policy, "workspace": str(workspace),
            "execution_mode": "ALIAS_SMOKE", "evidence_scope": "LOCAL_HOST_EXPERIMENTAL",
            "backend_deployment_status": config.get("backend_deployment_status", DEFAULT_BACKEND_DEPLOYMENT_STATUS),
            "mini_swe_version": version("mini-swe-agent"), "started_at": now(),
            "max_steps": max_steps, "max_output_tokens": max_output_tokens,
            "instruction": instruction, "verify_command": verify_command,
            "upstream_cost_counter_status": "UNPRICED_PLACEHOLDER_NOT_AN_INVOICE",
            "upstream_runtime_options": dict(runtime_options),
        }
        mini = mini_configuration(max_steps=max_steps, cost_limit=0)
        model = PolicyModel(policy=policy, state=state, record_dir=record_dir, provider=provider,
                            v9_config=config, max_output_tokens=max_output_tokens,
                            model_name="openai/" + config["actual_backend_model_id"], **mini["model"])
        run_config.update(capability_snapshot_id=(model.v9_hook.capability_snapshot.get("snapshot_id")
                                                  if model.v9_hook else None),
                          feature_training_status=config.get("feature_training_status", "FEATURE_NOT_TRAINED"))
        write_atomic(record_dir / "run_config.json", run_config)
        event(record_dir, "ITERATION_START", execution_mode="ALIAS_SMOKE",
              backend_deployment_status=run_config["backend_deployment_status"],
              evidence_scope="LOCAL_HOST_EXPERIMENTAL", episode_id=state.episode_id)
        private_names = api_key_names(config)
        shell_env = {name: value for name, value in os.environ.items() if name not in private_names}
        environment = RecordedLocalEnvironment(
            state=state, record_dir=record_dir, cwd=str(workspace), timeout=30,
            api_key_env_names=private_names,
        )
        agent_config = {key: value for key, value in mini["agent"].items() if key != "mode"}
        agent_config["output_path"] = record_dir / "mini-swe-agent.trajectory.json"
        agent = DefaultAgent(model, environment, **agent_config)
        error, agent_result = None, {}
        try:
            state.start()
            agent_result = agent.run(instruction)
        except Exception as exc:
            error = type(exc).__name__
            event(record_dir, "ERROR", category="AGENT", error=error)
        finally:
            agent.save(agent.config.output_path)
        verification_error = None
        try:
            verified = subprocess.run(verify_command, shell=True, cwd=workspace, text=True,
                                      capture_output=True, timeout=60, env=shell_env)
            verification_exit_code = verified.returncode
            verification_output = verified.stdout + verified.stderr
        except subprocess.TimeoutExpired as exc:
            verification_error, verification_exit_code = type(exc).__name__, None
            verification_output = "".join(part.decode(errors="replace") if isinstance(part, bytes) else part or ""
                                          for part in (exc.stdout, exc.stderr))
        (record_dir / "verification.txt").write_text(verification_output, encoding="utf-8")
        patch = subprocess.run(["git", "diff", "--binary", "HEAD", "--", "."], cwd=workspace,
                               capture_output=True, text=True, env=shell_env)
        if patch.stdout:
            (record_dir / "changes.patch").write_text(patch.stdout, encoding="utf-8")
        usage = model.episode_usage
        complete = lambda field: sum(item[field] for item in usage) if usage and all(item.get(field) is not None for item in usage) else None
        agent_exit_status = agent_result.get("exit_status", error)
        success = not error and agent_exit_status == "Submitted" and verification_exit_code == 0
        state.finish(EpisodeStatus.SUCCESS if success else EpisodeStatus.TIMEOUT
                     if agent_exit_status in ("LimitsExceeded", "TimeExceeded") else EpisodeStatus.FAILED)
        result = {
            "episode_id": state.episode_id, "task_id": task_id, "policy_id": policy,
            "recorded_at": now(), "finished_at": now(), "run_dir": str(record_dir),
            "benchmark": "local-development", "execution_mode": "ALIAS_SMOKE",
            "backend_deployment_status": run_config["backend_deployment_status"],
            "evidence_scope": "LOCAL_HOST_EXPERIMENTAL", "official_result_eligible": False,
            "scientific_result_eligible": False, "evaluation_status": "LOCAL_VERIFICATION_ONLY",
            "resolved": verification_exit_code == 0, "verification_exit_code": verification_exit_code,
            "verification_error": verification_error, "agent_exit_status": agent_exit_status,
            "agent_error": error, "status": "RUNTIME_VERIFIED" if success else "FAILED",
            "total_steps": len(model.usage), "tool_calls": len(state.history),
            "teacher_calls": sum(row.get("provider_request_attempted", False) for row in model.teacher_metrics),
            "teacher_attempts": len(model.teacher_metrics),
            "teacher_assessments": sum(row["status"] == "SUCCESS" for row in model.teacher_metrics),
            "elapsed_time_sec": time.perf_counter() - started,
            "total_prompt_tokens": complete("prompt_tokens"),
            "total_completion_tokens": complete("completion_tokens"),
            "total_reasoning_tokens": complete("reasoning_tokens"),
            "total_cached_tokens": complete("cached_tokens"), "total_cost_usd": model.complete_episode_cost_usd,
            "actual_billed_cost_usd": complete("actual_billed_cost_usd"),
            "cost_status": config.get("cost_status", "BACKEND_PRICE_NOT_MEASURED"),
            "router_fallback_used": model.fallback_used,
            "logical_models_selected": sorted({item["selected_model_id"] for item in model.usage}),
            "router_checkpoint_ids": sorted({item["router_checkpoint_id"] for item in model.usage}),
            "actual_backend_model_id": config["actual_backend_model_id"],
            "capability_snapshot_id": run_config["capability_snapshot_id"],
            "feature_training_status": run_config["feature_training_status"],
        }
        write_atomic(record_dir / "metrics.json", result)
        ExperimentLedger().record_development_episode(result)
        event(record_dir, "ITERATION_END", **result)
        return result
