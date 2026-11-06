"""Run the original mini-SWE-agent on an isolated local development workspace."""
from __future__ import annotations

import json
import os
import shlex
import time
from copy import deepcopy
from contextlib import ExitStack
from importlib.metadata import version
from pathlib import Path

from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted

from modelrouter.agent.state import AgentState, EpisodeStatus
from modelrouter.benchmark.iterations import event, now, rows, write_atomic
from modelrouter.providers.provider import OpenAICompatibleProvider, OpenAIResponsesProvider
from modelrouter.telemetry.ledger import ExperimentLedger
from .context import record_tool_result


def api_key_names(config):
    names = {name for name in os.environ if name == "API_KEY" or name.endswith("_API_KEY")}
    names.update(("OPENAI_API_KEY", "QWEN_API_KEY", "MODELROUTER_GENERATOR_API_KEY",
                  "MODELROUTER_ALIAS_API_KEY"))
    names.update(config[name] for name in ("api_key_env", "teacher_api_key_env") if config.get(name))
    return names


class RecordedEnvironment:
    """Record the original native environment's observations and submissions."""

    def __init__(self, environment, *, state, record_dir, api_key_env_names=()):
        self._api_key_env_names = api_key_names({}) | set(api_key_env_names)
        self.environment = environment
        self.state, self.record_dir = state, record_dir

    def get_template_vars(self, **kwargs):
        return {name: value for name, value in self.environment.get_template_vars(**kwargs).items()
                if name not in self._api_key_env_names}

    def serialize(self):
        return self.environment.serialize()

    def execute(self, action, cwd="", *, timeout=None):
        started = time.perf_counter()
        try:
            output = self.environment.execute(action, cwd, timeout=timeout)
        except Submitted as exc:
            output = {"output": "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\n" + exc.messages[-1]["content"],
                      "returncode": 0}
            record_tool_result(self.state, self.record_dir, action, output,
                               (time.perf_counter() - started) * 1000, submission=True)
            raise
        record_tool_result(self.state, self.record_dir, action, output,
                           (time.perf_counter() - started) * 1000)
        return output


def run_development(*, workspace: Path, instruction: str, verify_command: str,
                    config: dict, record_dir: Path, task_id: str, policy="laya_v2",
                    max_steps=15, max_output_tokens=4096, api_key=None,
                    provider=None, observed_messages=None, task_environment=None) -> dict:
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
        initial_cwd = config.get("initial_cwd", task_environment.config.cwd if task_environment is not None
                                 else str(workspace))
        instruction = f"{instruction}\n\nWorkspace and initial working directory (absolute CWD): {initial_cwd}"
        record_dir.mkdir(parents=True, exist_ok=True)
        provider_type = OpenAIResponsesProvider if config.get("generator_protocol") == "responses" else OpenAICompatibleProvider
        provider = provider if provider is not None else provider_type(
            api_key=api_key, request_timeout_sec=config.get("provider_timeout_sec", 60.0))
        mode = "REAL_API"
        evidence_scope = config.get("evidence_scope", "LOCAL_HOST_EXPERIMENTAL")
        state = AgentState(task_id=task_id, episode_id=record_dir.name, policy_id=policy,
                           max_steps=max_steps, usd_budget=0)
        if observed_messages is not None:
            from modelrouter.v9.training.prepare import build_offline_prefix_input
            prefix = {"observed_messages": observed_messages,
                      "pre_decision_state": config["pre_decision_state"],
                      "provenance": {"task_id": task_id, "episode_id": state.episode_id,
                                     "tool_result_alignment": config.get("tool_result_alignment"),
                                     "observed_through_step": sum(message.get("role") == "assistant"
                                                                  for message in observed_messages)}}
            state, observed_messages = build_offline_prefix_input(prefix, lambda _: state)
        state.task_prompt = instruction
        started = time.perf_counter()
        run_config = {
            **{key: value for key, value in config.items() if key not in ("api_key", "teacher_api_key")},
            "task_id": task_id, "policy": policy, "workspace": str(workspace),
            "execution_mode": mode, "evidence_scope": evidence_scope,
            "selection_scope": "MODEL_NATIVE_EFFORT",
            "backend_deployment_status": config.get("backend_deployment_status", "PROVIDER_RETURNED_IDENTITY_NOT_WEIGHT_INSPECTION"),
            "mini_swe_version": version("mini-swe-agent"), "started_at": now(),
            "max_steps": max_steps, "max_output_tokens": max_output_tokens,
            "instruction": instruction, "verify_command": verify_command,
            "upstream_cost_counter_status": "MODEL_RATE_ESTIMATE_NOT_AN_INVOICE",
            "upstream_runtime_options": dict(runtime_options),
            "comparison_scope": "ONE_NATIVE_AGENT_STEP" if observed_messages is not None else "EPISODE",
        }
        mini = mini_configuration(max_steps=max_steps, cost_limit=0)
        model = PolicyModel(policy=policy, state=state, record_dir=record_dir, provider=provider,
                            v9_config=config, max_output_tokens=max_output_tokens,
                            candidate_actions=config.get("candidate_actions"),
                            model_name="openai/gpt-6-luna",
                            **mini["model"])
        if observed_messages is not None and model.v9_hook is not None:
            hook = model.v9_hook
            hook.episode_id = state.episode_id
            hook.trigger.reset(state.episode_id)
            for _ in range(state.step_index):
                hook.trigger.after_generation()
            hook.continuity = deepcopy(config["pre_decision_state"].get("continuity") or {})
            hook.previous_selected = hook.continuity.get("selected_model_id")
            hook.previous_backend = hook.continuity.get("actual_backend_model_id")
        run_config.update(capability_snapshot_id=(model.v9_hook.capability_snapshot.get("snapshot_id")
                                                  if model.v9_hook else None),
                          feature_training_status=config.get("feature_training_status", "FEATURE_NOT_TRAINED"))
        write_atomic(record_dir / "run_config.json", run_config)
        event(record_dir, "ITERATION_START", execution_mode=mode,
              backend_deployment_status=run_config["backend_deployment_status"],
              evidence_scope=evidence_scope, episode_id=state.episode_id)
        private_names = api_key_names(config)
        if task_environment is None:
            task_environment = LocalEnvironment(cwd=initial_cwd, timeout=30,
                                                env={name: "" for name in private_names})
        environment = RecordedEnvironment(
            task_environment,
            state=state, record_dir=record_dir,
            api_key_env_names=private_names,
        )
        agent_config = {key: value for key, value in mini["agent"].items() if key != "mode"}
        agent_config["output_path"] = record_dir / "mini-swe-agent.trajectory.json"
        agent = DefaultAgent(model, environment, **agent_config)
        observed_tool_calls = len(state.history)
        error, agent_result = None, {}
        try:
            state.start()
            if observed_messages is None:
                agent_result = agent.run(instruction)
            else:
                agent.messages = deepcopy(observed_messages)
                agent.step()
                agent_result = {"exit_status": "STEP_EXECUTED"}
        except Submitted as exc:
            agent.add_messages(*exc.messages)
            agent_result = exc.messages[-1]["extra"]
        except Exception as exc:
            error = type(exc).__name__
            event(record_dir, "ERROR", category="AGENT", error=error, detail=str(exc))
        finally:
            agent.save(agent.config.output_path)
        patch = task_environment.execute({"command": "git diff --binary HEAD -- ."})
        if patch["output"]:
            (record_dir / "changes.patch").write_text(patch["output"], encoding="utf-8")
        verifier_restore = None
        if config.get("original_verifier_paths"):
            verifier_restore = task_environment.execute({
                "command": shlex.join(["git", "restore", "--source=HEAD", "--",
                                       *config["original_verifier_paths"]])})
            event(record_dir, "ORIGINAL_VERIFIER_RESTORED", **verifier_restore)
            if verifier_restore["returncode"] != 0:
                raise RuntimeError("Original verifier files could not be restored")
        step_error = error if observed_messages is not None else None
        verified = ({"returncode": None, "output": ""} if step_error else
                    task_environment.execute({"command": verify_command}, timeout=task_environment.config.timeout))
        verification_error = step_error or verified.get("extra", {}).get("exception_type")
        verification_exit_code = None if verification_error else verified["returncode"]
        verification_output = verified["output"]
        (record_dir / "verification.txt").write_text(verification_output, encoding="utf-8")
        usage = model.episode_usage
        failed_requests = sum(row["event"] == "ERROR" and row.get("category") == "PROVIDER"
                              for row in rows(record_dir / "events.jsonl"))
        complete = lambda field: sum(item[field] for item in usage) if not failed_requests and usage and all(item.get(field) is not None for item in usage) else None
        total_cost = None if failed_requests else model.complete_episode_cost_usd
        agent_exit_status = agent_result.get("exit_status", error)
        success = not error and verification_exit_code == 0 and (
            observed_messages is not None or agent_exit_status == "Submitted")
        state.finish(EpisodeStatus.SUCCESS if success else EpisodeStatus.TIMEOUT
                     if agent_exit_status in ("LimitsExceeded", "TimeExceeded") else EpisodeStatus.FAILED)
        result = {
            "episode_id": state.episode_id, "task_id": task_id, "policy_id": policy,
            "recorded_at": now(), "finished_at": now(), "run_dir": str(record_dir),
            "benchmark": config.get("dataset", "local-development"), "execution_mode": mode,
            "backend_deployment_status": run_config["backend_deployment_status"],
            "evidence_scope": evidence_scope, "official_result_eligible": False,
            "scientific_result_eligible": False, "evaluation_status": "LOCAL_VERIFICATION_ONLY",
            "resolved": None if verification_error else verification_exit_code == 0,
            "verification_exit_code": verification_exit_code,
            "comparison_scope": run_config["comparison_scope"],
            "verification_error": verification_error, "agent_exit_status": agent_exit_status,
            "original_verifier_restore_exit_code": verifier_restore["returncode"] if verifier_restore else None,
            "agent_error": error, "status": "RUNTIME_VERIFIED" if success else "FAILED",
            "total_steps": len(model.usage), "tool_calls": len(state.history) - observed_tool_calls,
            "observed_tool_calls": observed_tool_calls, "history_tool_calls": len(state.history),
            "teacher_calls": sum(row.get("provider_request_attempted", False) for row in model.teacher_metrics),
            "teacher_attempts": len(model.teacher_metrics),
            "teacher_assessments": sum(row["status"] == "SUCCESS" for row in model.teacher_metrics),
            "elapsed_time_sec": time.perf_counter() - started,
            "total_prompt_tokens": complete("prompt_tokens"),
            "total_completion_tokens": complete("completion_tokens"),
            "total_reasoning_tokens": complete("reasoning_tokens"),
            "total_cached_tokens": complete("cached_tokens"),
            "total_cache_write_tokens": complete("cache_write_tokens"),
            "total_cost_usd": total_cost,
            "known_model_rate_cost_usd": round(sum(item["cost_usd"] for item in usage
                                                  if item.get("cost_usd") is not None), 10),
            "failed_provider_requests": failed_requests,
            "actual_billed_cost_usd": complete("actual_billed_cost_usd"),
            "cost_status": "REQUEST_MODEL_RATE_ESTIMATE" if total_cost is not None else "USAGE_INCOMPLETE",
            "cost_basis": "REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE",
            "router_fallback_used": model.fallback_used,
            "logical_models_selected": sorted({item["selected_model_id"] for item in model.usage}),
            "router_checkpoint_ids": sorted({item["router_checkpoint_id"] for item in model.usage}),
            "actual_backend_model_ids": sorted({item["returned_model_id"] for item in usage
                                                if item.get("returned_model_id")}),
            "capability_snapshot_id": run_config["capability_snapshot_id"],
            "feature_training_status": run_config["feature_training_status"],
        }
        write_atomic(record_dir / "metrics.json", result)
        ExperimentLedger().record_development_episode(result)
        event(record_dir, "ITERATION_END", **result)
        return result
