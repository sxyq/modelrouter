"""Official mini-swe-agent v2 with a per-request ModelRouter model hook.

Upstream owns the loop, parsing, observations and exit semantics.
The historical SingleAgent remains in modelrouter.agent.agent.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.error
from importlib.metadata import version
from pathlib import Path

import litellm
import yaml
from harbor.agents.base import BaseAgent
from harbor.agents.capabilities import AgentCapabilities
from harbor.agents.installed.mini_swe_agent import convert_mini_swe_agent_to_atif
from harbor.models.agent.context import AgentContext
from harbor.models.trial.config import TaskConfig
from minisweagent import package_dir
from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted
from minisweagent.models.litellm_model import LitellmModel
from minisweagent.models.utils.actions_toolcall import BASH_TOOL

from modelrouter.agent.state import AgentState
from modelrouter.baselines.policy import create_policy
from modelrouter.providers.provider import OpenAICompatibleProvider, OpenAIResponsesProvider
from modelrouter.providers.registry import ModelRegistry, V9_MODEL_IDS
from modelrouter.serving.schemas import LegalAction, PreDecisionState
from modelrouter.v9.runtime.alias import DEFAULT_BACKEND_DEPLOYMENT_STATUS
from modelrouter.v9.runtime.context import record_tool_result
from .iterations import append, event, now, rows


def mini_configuration(max_steps=30, cost_limit=0.0):
    config = yaml.safe_load((package_dir / "config/mini.yaml").read_text())
    config["agent"].update(step_limit=max_steps, cost_limit=cost_limit, mode="yolo")
    # The official bash function tool does not use LiteLLM's MCP gateway.
    config["model"]["model_kwargs"]["_skip_mcp_handler"] = True
    # Both harness variants use the recorded chat-completions protocol.
    config["model"]["model_kwargs"]["_skip_responses_api_bridge"] = True
    config["model"]["model_kwargs"]["num_retries"] = 0
    return config


def legal_actions(joint=False):
    registry = ModelRegistry()
    actions = []
    for model in ("gpt-6-luna", "gpt-5.6-luna"):
        spec = registry.get_spec(model)
        efforts = spec.native_efforts if joint else ("low",)
        for effort in efforts:
            spec.validate_effort(effort)
            actions.append(LegalAction(provider=spec.provider, model=model, revision="latest",
                                       native_effort=effort).model_dump())
    return sorted(actions, key=lambda action: action["action_id"])


class PolicyModel(LitellmModel):
    """Reuse official tool handling; call the existing Provider once per query."""

    abort_exceptions = LitellmModel.abort_exceptions + [ValueError, RuntimeError, TypeError, urllib.error.HTTPError]

    def __init__(self, *, policy, state, record_dir, provider=None, seed=42, max_output_tokens=2048,
                 v9_config=None, candidate_actions=None, **kwargs):
        super().__init__(**kwargs)
        self.policy_name = policy
        self.v9_enabled = v9_config is not None and v9_config.get("enabled", True)
        if candidate_actions is not None:
            self.actions = [LegalAction.model_validate(action).model_dump() for action in candidate_actions]
        elif self.v9_enabled:
            registry = ModelRegistry()
            self.actions = [LegalAction(provider=registry.get_spec(model).provider, model=model,
                                        native_effort="none").model_dump() for model in V9_MODEL_IDS]
        else:
            self.actions = legal_actions(joint=policy.startswith("joint_"))
        policy_key = {"joint_laya": "laya_v2", "joint_kev": "kev_4b"}.get(policy, policy)
        target = "gpt-6-luna" if policy == "fixed_strong" else "gpt-5.6-luna"
        if self.v9_enabled:
            target = "gpt-6.1-sol" if policy == "fixed_strong" else "qwen3.8-flash"
        self.policy = create_policy(policy_key, seed=seed, target_model=target)
        self.state, self.record_dir = state, record_dir
        self.provider = provider
        if self.provider is None:
            if self.v9_enabled and v9_config.get("actual_backend_model_id"):
                from modelrouter.v9.runtime.alias import alias_provider
                self.provider = alias_provider(v9_config)
            else:
                provider_type = (OpenAIResponsesProvider if self.v9_enabled
                                 and v9_config.get("generator_protocol") == "responses"
                                 else OpenAICompatibleProvider)
                self.provider = provider_type(request_timeout_sec=(
                    v9_config.get("provider_timeout_sec", 60.0) if self.v9_enabled else 60.0))
        self.max_output_tokens = max_output_tokens
        self.last_metrics, self.usage = {}, []
        self.fallback_used = False
        self.untested_efforts_used = set()
        self.v9_hook = None
        if self.v9_enabled:
            from modelrouter.v9.runtime.decision_hook import V9DecisionHook
            self.v9_hook = V9DecisionHook(v9_config, self.provider, Path(record_dir))
            if hasattr(self.policy, "client"):
                self.policy.client.protocol = "system_one"
                self.policy.client.endpoint = v9_config["router_endpoint"].rstrip("/")
                self.policy.client.timeout = v9_config.get(
                    "router_timeout_sec", 60.0 if self.policy.client.router_family == "kev" else 20.0)
        self.teacher_metrics = self.v9_hook.teacher_metrics if self.v9_hook else []
        self.action_validation = {
            action["action_id"]: ("ALIAS_SMOKE_ONLY" if self.v9_enabled and
                                  getattr(self.provider, "alias_mapping", None) is not None else
                                  "REAL_API_NOT_OBSERVED" if self.v9_enabled else
                                  "REAL_TESTED_LOW" if action["native_effort"] == "low" else "NOT_TESTED")
            for action in self.actions
        }

    def _query(self, messages, **kwargs):
        decision_id = f"{self.state.episode_id}-{self.state.step_index}"
        snapshot = self.state.build_pre_decision_snapshot().to_dict()
        if self.v9_hook:
            snapshot = self.v9_hook.before_route(self.state, messages, snapshot, self.actions)
        else:
            snapshot.update(prompt=json.dumps(messages, ensure_ascii=False))
            snapshot.update(context_chars=len(snapshot["prompt"]), prior_tool_calls_count=len(self.state.history),
                            prior_error_signals_count=self.state.tool_error_count,
                            context_tokens_approx=len(snapshot["prompt"]) // 4,
                            history_snippet=json.dumps([
                                {"command": step.tool_action, "output": step.tool_observation,
                                 "exit_code": step.tool_exit_code} for step in self.state.history
                            ], ensure_ascii=False))
            if hasattr(self.state, "last_output"):
                snapshot.update(last_tool_exit_code=self.state.last_output["returncode"],
                                last_observation_summary=self.state.last_output["output"])
        snapshot = PreDecisionState.model_validate(snapshot).model_dump()
        self.state.pre_decision_snapshot = snapshot
        route_start = time.perf_counter()
        if hasattr(self.policy, "client"):
            decision = self.policy.client.route(
                episode_id=self.state.episode_id, decision_id=decision_id,
                pre_decision_state=snapshot, legal_actions=self.actions,
                policy_version="mini-v9" if self.v9_enabled else "mini-v10")
        else:
            decision = self.policy.select(self.state, self.actions)
        selected = LegalAction.model_validate(decision.selected_action).model_dump()
        if selected not in self.actions:
            raise ValueError("Selected action is not part of this trial's candidate set")
        self.state.last_decision_id = decision_id
        self.state.last_router_checkpoint_id = decision.checkpoint_id
        self.state.last_selected_action = selected
        if self.v9_hook:
            self.v9_hook.after_route(decision, neural_route=hasattr(self.policy, "client"))
        router_identity = {key: value for key, value in self.v9_hook.current_context.items()
                           if key.startswith("router_") and key not in
                           ("router_checkpoint_id", "router_family", "router_fallback_used")} if self.v9_hook else {}
        self.fallback_used = self.fallback_used or decision.fallback_used
        if selected["native_effort"] != "low" and not (self.v9_enabled and selected["native_effort"] == "none"):
            self.untested_efforts_used.add(selected["native_effort"])
        event(self.record_dir, "ROUTER_END", episode_id=self.state.episode_id, step=self.state.step_index,
              decision_id=decision_id,
              policy=self.policy_name, router_family=decision.router_family,
              router_latency_ms=(time.perf_counter() - route_start) * 1000,
              inference_latency_ms=decision.inference_latency_ms,
              checkpoint_id=decision.checkpoint_id, fallback_used=decision.fallback_used,
              ranked_actions=decision.ranked_actions, confidence=decision.confidence,
              **router_identity,
              policy_implementation_status=self.policy.implementation_status,
              effort_validation_status=self.action_validation[selected["action_id"]],
              selected_action=selected, pre_decision_state=snapshot, legal_actions=self.actions)
        spec = ModelRegistry().get_spec(selected["model"])
        started = time.perf_counter()
        try:
            body, metrics = self.provider.query_raw(
                messages, spec, selected["native_effort"], self.max_output_tokens, [BASH_TOOL], True)
        except Exception as exc:
            alias_mapping = getattr(self.provider, "alias_mapping", None)
            alias_facts = (alias_mapping.resolve(spec.model_id, selected["native_effort"]) or {}
                           if alias_mapping else {})
            event(self.record_dir, "ERROR", category="PROVIDER", error=type(exc).__name__,
                  episode_id=self.state.episode_id, model=selected["model"], role="generator",
                  selected_model_id=spec.model_id, cost_model_id=spec.model_id,
                  actual_backend_model_id=alias_facts.get("actual_backend_model_id"),
                  request_model_id=alias_facts.get("actual_backend_model_id", spec.model_id),
                  returned_model_id=None, requested_native_effort=selected["native_effort"],
                  effective_native_effort=alias_facts.get("effective_native_effort", selected["native_effort"]),
                  router_checkpoint_id=decision.checkpoint_id,
                  execution_mode=alias_facts.get("execution_mode", "REAL_API"),
                  cost_usd=None, actual_billed_cost_usd=None, usage_status="MISSING",
                  cost_status="MAPPED_USAGE_INCOMPLETE" if alias_facts else "UNKNOWN",
                  duration_ms=(time.perf_counter() - started) * 1000)
            raise
        metrics = dict(metrics, episode_id=self.state.episode_id, decision_id=decision_id,
                       router_checkpoint_id=decision.checkpoint_id,
                       router_family=decision.router_family, **router_identity,
                       capability_snapshot_id=snapshot.get("capability_snapshot_id"))
        if self.v9_enabled:
            is_alias = metrics.get("execution_mode") == "ALIAS_SMOKE" or metrics["alias_mapping_applied"]
            metrics["execution_mode"] = "ALIAS_SMOKE" if is_alias else "REAL_API"
            identity_status = ("ALIAS_SMOKE_ONLY" if is_alias else
                               "REAL_API_IDENTITY_MATCHED" if metrics["identity_status"] == "MATCHED_REQUEST_ALIAS"
                               else "REAL_API_IDENTITY_UNVERIFIED")
            self.action_validation[selected["action_id"]] = identity_status
            metrics["effort_validation_status"] = identity_status
        self.last_metrics = metrics
        self.usage.append(metrics)
        self.state.accumulated_cost_usd += metrics.get("cost_usd") or 0
        if self.v9_hook:
            self.v9_hook.after_generation(metrics, selected, body)
        event(self.record_dir, "GENERATOR_END", **metrics,
              step=self.state.step_index, policy=self.policy_name, model=selected["model"],
              returned_model=metrics["returned_model_id"], effort=selected["native_effort"])
        self.state.step_index += 1
        if self.provider.protocol == "responses":
            calls = [{"id": item["call_id"], "type": "function",
                      "function": {"name": item["name"], "arguments": item["arguments"]}}
                     for item in body["output"] if item["type"] == "function_call"]
            content = "".join(part.get("text", "") for item in body["output"]
                              if item["type"] == "message" for part in item["content"])
            message = {"role": "assistant", "content": content}
            if calls:
                message["tool_calls"] = calls
            finish_reason = (body["incomplete_details"]["reason"]
                             if body["status"] == "incomplete" else "tool_calls" if calls else "stop")
            if finish_reason == "max_output_tokens":
                finish_reason = "length"
            body = {"id": body["id"], "model": body["model"],
                    "choices": [{"index": 0, "message": message,
                                 "finish_reason": finish_reason}],
                    "usage": {"prompt_tokens": metrics["prompt_tokens"],
                              "completion_tokens": metrics["completion_tokens"]}}
        return litellm.ModelResponse(**body)

    def _calculate_cost(self, response):
        # Upstream needs a number; unpriced API usage remains null in records.
        cost = self.last_metrics.get("cost_usd") or 0.0
        teacher_cost = sum(row.get("cost_usd") or 0 for row in
                           (self.v9_hook.last_teacher_metrics if self.v9_hook else []))
        return {"cost": cost + teacher_cost}

    @property
    def episode_usage(self):
        return self.usage + [row for row in self.teacher_metrics
                            if row.get("provider_request_attempted", True)]

    @property
    def complete_episode_cost_usd(self):
        usage = self.episode_usage
        return sum(row["cost_usd"] for row in usage) if usage and all(
            row.get("cost_usd") is not None for row in usage) else None

    def serialize(self):
        model_config = self.config.model_dump(mode="json")
        model_kwargs = model_config.get("model_kwargs", {})
        model_kwargs.pop("api_key", None)
        if model_kwargs.get("extra_headers"):
            model_kwargs["extra_headers"] = {name: value for name, value in model_kwargs["extra_headers"].items()
                                              if name.lower() != "authorization"}
        result = {"info": {"config": {"model": model_config,
                                    "model_type": type(self).__name__, "policy": self.policy_name,
                                    "legal_actions": self.actions,
                                    "action_validation": self.action_validation,
                                    "policy_implementation_status": self.policy.implementation_status},
                         "fallback_used": self.fallback_used, "provider_metrics": self.usage}}
        if self.v9_hook:
            result["info"]["v9"] = {
                "teacher_metrics": self.teacher_metrics, "continuity": self.v9_hook.continuity,
                "capability_snapshot_id": self.v9_hook.capability_snapshot.get("snapshot_id"),
                "router_checkpoint_ids": sorted({row["router_checkpoint_id"] for row in self.usage}),
                "router_checkpoints": [dict(router_family=family, run_id=run_id, checkpoint_id=checkpoint_id)
                                       for family, run_id, checkpoint_id in sorted(
                                           {(row["router_family"], row.get("router_run_id"), row["router_checkpoint_id"])
                                            for row in self.usage}, key=lambda item: (item[0], item[1] or "", item[2]))],
                "feature_training_status": self.v9_hook.config.get("feature_training_status", "FEATURE_NOT_TRAINED"),
                "backend_deployment_status": self.v9_hook.config.get("backend_deployment_status", DEFAULT_BACKEND_DEPLOYMENT_STATUS),
                "complete_episode_cost_usd": self.complete_episode_cost_usd,
                "upstream_cost_accounting": "KNOWN_COSTS_PLUS_UNKNOWN_PLACEHOLDERS_NOT_BILLING",
            }
        return result


class HarborEnvironment(LocalEnvironment):
    """Keep upstream submission handling, executing only in Harbor's sandbox."""

    def __init__(self, environment, loop, record_dir, state, system_info):
        super().__init__()
        self.environment, self.loop = environment, loop
        self.record_dir, self.state, self.system_info = record_dir, state, system_info

    def execute(self, action, cwd="", *, timeout=None):
        started = time.perf_counter()
        result = asyncio.run_coroutine_threadsafe(
            self.environment.exec(command=action["command"], timeout_sec=timeout or self.config.timeout),
            self.loop,
        ).result()
        output = {"output": (result.stdout or "") + (result.stderr or ""),
                  "returncode": result.return_code, "exception_info": ""}
        duration = (time.perf_counter() - started) * 1000
        try:
            self._check_finished(output)
        except Submitted:
            record_tool_result(self.state, self.record_dir, action, output, duration, submission=True)
            raise
        record_tool_result(self.state, self.record_dir, action, output, duration)
        return output

    def get_template_vars(self, **kwargs):
        return self.system_info | kwargs

    def serialize(self):
        return {"info": {"config": {"environment_type": "harbor", "system_info": self.system_info}}}


class ModelRouterMiniSweAgent(BaseAgent):
    capabilities = AgentCapabilities(atif=True)
    def __init__(self, logs_dir=None, model_name=None, *, policy="fixed_strong", seed=42,
                 max_steps=30, max_output_tokens=2048, cost_limit=0.0,
                 v9_config=None, candidate_actions=None, provider=None, **kwargs):
        super().__init__(logs_dir=Path(logs_dir or "/tmp/modelrouter-mini"), model_name=model_name, **kwargs)
        self.policy, self.seed = policy, int(seed)
        self.max_steps, self.max_output_tokens = int(max_steps), int(max_output_tokens)
        self.cost_limit = float(cost_limit)
        self.v9_config, self.candidate_actions, self.provider = v9_config, candidate_actions, provider

    @staticmethod
    def name():
        return "modelrouter-mini-swe-agent"

    @staticmethod
    def version():
        return "10.0-mini-" + version("mini-swe-agent")

    async def setup(self, environment):
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    async def run(self, instruction, environment, context: AgentContext):
        config = mini_configuration(self.max_steps, self.cost_limit)
        trial_config = self.logs_dir.parent / "config.json"
        task_id = "unknown"
        if trial_config.is_file():
            task = TaskConfig.model_validate(json.loads(trial_config.read_text())["task"])
            task_id = task.get_task_id().get_name()
        state = AgentState(task_id=task_id, episode_id=str(self.context_id or self.logs_dir.parent.name),
                           policy_id=self.policy, seed=self.seed, max_steps=self.max_steps,
                           usd_budget=self.cost_limit)
        state.task_prompt = instruction
        record_dir = Path(os.environ.get("MODELROUTER_ITERATION", str(self.logs_dir)))
        model = PolicyModel(policy=self.policy, state=state, record_dir=record_dir, seed=self.seed,
                            provider=self.provider, v9_config=self.v9_config,
                            candidate_actions=self.candidate_actions,
                            max_output_tokens=self.max_output_tokens,
                            model_name=self.model_name or "openai/gpt-6-luna", **config["model"])
        setup_started = time.perf_counter()
        info_command = "uname -s && uname -r && uname -v && uname -m"
        result = await environment.exec(command=info_command, timeout_sec=10)
        system, release, kernel_version, machine = result.stdout.strip().splitlines()
        system_info = dict(system=system, release=release, machine=machine, version=kernel_version)
        append(record_dir / "tool_calls.jsonl", {"kind": "agent_setup", "timestamp": now(),
               "episode_id": state.episode_id, "command": info_command, "exit_code": result.return_code,
               "duration_ms": (time.perf_counter() - setup_started) * 1000, "output": result.stdout})
        env = HarborEnvironment(environment, asyncio.get_running_loop(), record_dir, state, system_info)
        agent_config = {k: v for k, v in config["agent"].items() if k != "mode"}
        agent_config.update(step_limit=self.max_steps, output_path=self.logs_dir / "mini-swe-agent.trajectory.json")
        agent = DefaultAgent(model, env, **agent_config)
        try:
            state.start()
            await asyncio.to_thread(agent.run, instruction)
        finally:
            context.metadata = {**(context.metadata or {}), "harness": "minisweagent.agents.default.DefaultAgent",
                                "mini_version": version("mini-swe-agent"), "policy": self.policy,
                                "task_id": task_id,
                                "task_identity_source": "harbor_task_config" if task_id != "unknown" else "UNAVAILABLE",
                                "fallback_used": model.fallback_used,
                                "policy_implementation_status": model.policy.implementation_status,
                                "action_validation": model.action_validation,
                                "untested_native_efforts_used": sorted(model.untested_efforts_used),
                                "neural_router_evidence_eligible": bool(model.usage) and (
                                    model.policy.implementation_status == "REMOTE_NEURAL_ROUTER"
                                    and not model.fallback_used and not model.untested_efforts_used
                                    and not any(u.get("execution_mode") in ("ALIAS_SMOKE", "TEACHER_ALIAS_SMOKE")
                                                or (model.v9_enabled and u.get("alias_mapping_applied"))
                                                for u in model.episode_usage)),
                                "raw_trajectory": str(self.logs_dir / "mini-swe-agent.trajectory.json")}
            if model.v9_hook:
                context.metadata["v9"] = model.serialize()["info"]["v9"]
            if model.usage:
                usage = model.episode_usage
                if all(u["usage_status"] == "REPORTED" for u in usage):
                    context.n_input_tokens = sum(u["prompt_tokens"] for u in usage)
                    context.n_output_tokens = sum(u["completion_tokens"] for u in usage)
                    if all(u["cached_tokens"] is not None for u in usage):
                        context.n_cache_tokens = sum(u["cached_tokens"] for u in usage)
                if model.complete_episode_cost_usd is not None:
                    context.cost_usd = model.complete_episode_cost_usd
                context.metadata["provider_metrics"] = model.usage
                context.metadata["cost_statuses"] = sorted({u.get("cost_status", "UNKNOWN") for u in usage})
                context.metadata["actual_billed_cost_usd"] = (
                    sum(u["actual_billed_cost_usd"] for u in usage)
                    if all(u.get("actual_billed_cost_usd") is not None for u in usage) else None)
            agent.save(agent.config.output_path)
            raw = json.loads(agent.config.output_path.read_text())
            trajectory = convert_mini_swe_agent_to_atif(raw, state.episode_id).to_json_dict()
            generated = [step for step in trajectory["steps"] if step["source"] == "agent"]
            for step, usage in zip(generated, model.usage):
                step["model_name"] = usage["selected_model_id"]
                step["reasoning_effort"] = usage.get("effective_native_effort", usage["native_effort"])
                step["metrics"] = {"prompt_tokens": usage.get("prompt_tokens"),
                                   "completion_tokens": usage.get("completion_tokens"),
                                   "cached_tokens": usage.get("cached_tokens"),
                                   "cost_usd": usage.get("cost_usd"),
                                   "extra": usage}
            tool_records = [row for row in rows(record_dir / "tool_calls.jsonl")
                            if row.get("kind") == "agent_tool" and row.get("episode_id") == state.episode_id]
            tool_by_id = {row["tool_call_id"]: row for row in tool_records if row.get("tool_call_id")}
            for step in generated:
                for observation in (step.get("observation") or {}).get("results", []):
                    record = tool_by_id.get(observation.get("source_call_id"))
                    if record:
                        observation["extra"] = (observation.get("extra") or {}) | {
                            "exit_code": record["exit_code"], "duration_ms": record["duration_ms"]}
            (self.logs_dir / "trajectory.json").write_text(json.dumps(trajectory, ensure_ascii=False, indent=2))
            context.metadata["atif_trajectory"] = str(self.logs_dir / "trajectory.json")


# Existing callers share the official loop. SingleAgent stays historical.
ModelRouterHarborAgent = ModelRouterMiniSweAgent
