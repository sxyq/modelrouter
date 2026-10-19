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
from minisweagent.models.litellm_model import LitellmModel
from minisweagent.models.utils.actions_toolcall import BASH_TOOL

from modelrouter.agent.state import AgentState, StepTrace
from modelrouter.baselines.policy import create_policy
from modelrouter.providers.provider import OpenAICompatibleProvider
from modelrouter.providers.registry import ModelRegistry
from modelrouter.serving.schemas import LegalAction, PreDecisionState
from .iterations import append, event, now, rows


def mini_configuration(max_steps=30, cost_limit=3.0):
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

    abort_exceptions = LitellmModel.abort_exceptions + [ValueError, RuntimeError, urllib.error.HTTPError]

    def __init__(self, *, policy, state, record_dir, provider=None, seed=42, max_output_tokens=2048, **kwargs):
        super().__init__(**kwargs)
        self.policy_name = policy
        self.actions = legal_actions(joint=policy.startswith("joint_"))
        policy_key = {"joint_laya": "laya_v2", "joint_kev": "kev_4b"}.get(policy, policy)
        target = "gpt-6-luna" if policy == "fixed_strong" else "gpt-5.6-luna"
        self.policy = create_policy(policy_key, seed=seed, target_model=target)
        self.state, self.record_dir = state, record_dir
        self.provider = provider or OpenAICompatibleProvider()
        self.max_output_tokens = max_output_tokens
        self.last_metrics, self.usage = {}, []
        self.fallback_used = False
        self.untested_efforts_used = set()
        self.action_validation = {
            action["action_id"]: "REAL_TESTED_LOW" if action["native_effort"] == "low" else "NOT_TESTED"
            for action in self.actions
        }

    def _query(self, messages, **kwargs):
        snapshot = self.state.build_pre_decision_snapshot().to_dict()
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
                episode_id=self.state.episode_id, decision_id=f"{self.state.episode_id}-{self.state.step_index}",
                pre_decision_state=snapshot, legal_actions=self.actions, policy_version="mini-v10")
        else:
            decision = self.policy.select(self.state, self.actions)
        selected = LegalAction.model_validate(decision.selected_action).model_dump()
        if selected not in self.actions:
            raise ValueError("Selected action is not part of this trial's candidate set")
        self.fallback_used = self.fallback_used or decision.fallback_used
        if selected["native_effort"] != "low":
            self.untested_efforts_used.add(selected["native_effort"])
        event(self.record_dir, "ROUTER_END", episode_id=self.state.episode_id, step=self.state.step_index,
              policy=self.policy_name, router_family=decision.router_family,
              router_latency_ms=(time.perf_counter() - route_start) * 1000,
              inference_latency_ms=decision.inference_latency_ms,
              checkpoint_id=decision.checkpoint_id, fallback_used=decision.fallback_used,
              policy_implementation_status=self.policy.implementation_status,
              effort_validation_status=self.action_validation[selected["action_id"]],
              selected_action=selected, pre_decision_state=snapshot, legal_actions=self.actions)
        spec = ModelRegistry().get_spec(selected["model"])
        spec.validate_effort(selected["native_effort"])
        started = time.perf_counter()
        try:
            body, metrics = self.provider.query_raw(
                messages, spec, selected["native_effort"], self.max_output_tokens, [BASH_TOOL], True)
        except Exception as exc:
            event(self.record_dir, "ERROR", category="PROVIDER", error=type(exc).__name__,
                  episode_id=self.state.episode_id, model=selected["model"],
                  duration_ms=(time.perf_counter() - started) * 1000)
            raise
        self.last_metrics = metrics
        self.usage.append(metrics)
        self.state.accumulated_cost_usd += metrics.get("cost_usd") or 0
        event(self.record_dir, "GENERATOR_END", **metrics, episode_id=self.state.episode_id,
              step=self.state.step_index, policy=self.policy_name, model=selected["model"],
              returned_model=metrics["returned_model_id"], effort=selected["native_effort"])
        self.state.step_index += 1
        return litellm.ModelResponse(**body)

    def _calculate_cost(self, response):
        if self.last_metrics.get("cost_usd") is None:
            raise ValueError("Provider has no attributable model usage/cost; retained as NOT_EVALUATED")
        return {"cost": self.last_metrics["cost_usd"]}

    def serialize(self):
        return {"info": {"config": {"model": self.config.model_dump(mode="json"),
                                    "model_type": type(self).__name__, "policy": self.policy_name,
                                    "legal_actions": self.actions,
                                    "action_validation": self.action_validation,
                                    "policy_implementation_status": self.policy.implementation_status},
                         "fallback_used": self.fallback_used, "provider_metrics": self.usage}}


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
        append(self.record_dir / "tool_calls.jsonl", {
            "kind": "agent_tool", "timestamp": now(), "episode_id": self.state.episode_id,
            "step": self.state.step_index, "command": action["command"],
            "tool_call_id": action.get("tool_call_id"), "exit_code": result.return_code,
            "duration_ms": (time.perf_counter() - started) * 1000, "output": output["output"],
        })
        event(self.record_dir, "TOOL_END", episode_id=self.state.episode_id, step=self.state.step_index,
              exit_code=result.return_code, duration_ms=(time.perf_counter() - started) * 1000)
        if result.return_code:
            self.state.tool_error_count += 1
        self.state.last_output = output
        self.state.history.append(StepTrace(
            step_index=self.state.step_index, phase=self.state.current_phase, selected_action={},
            thought="", tool_action=action["command"], tool_observation=output["output"],
            tool_exit_code=result.return_code, prompt_tokens=0, completion_tokens=0,
            reasoning_tokens=0, cached_tokens=0, step_cost_usd=0,
            step_duration_sec=time.perf_counter() - started))
        self.state.current_phase = "verify" if self.state.steps_remaining <= 3 else "modify"
        self._check_finished(output)
        return output

    def get_template_vars(self, **kwargs):
        return self.system_info | kwargs

    def serialize(self):
        return {"info": {"config": {"environment_type": "harbor", "system_info": self.system_info}}}


class ModelRouterMiniSweAgent(BaseAgent):
    capabilities = AgentCapabilities(atif=True)
    def __init__(self, logs_dir=None, model_name=None, *, policy="fixed_strong", seed=42,
                 max_steps=30, max_output_tokens=2048, cost_limit=3.0, **kwargs):
        super().__init__(logs_dir=Path(logs_dir or "/tmp/modelrouter-mini"), model_name=model_name, **kwargs)
        self.policy, self.seed = policy, int(seed)
        self.max_steps, self.max_output_tokens = int(max_steps), int(max_output_tokens)
        self.cost_limit = float(cost_limit)

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
                                    and not model.fallback_used and not model.untested_efforts_used),
                                "raw_trajectory": str(self.logs_dir / "mini-swe-agent.trajectory.json")}
            if model.usage:
                if all(u["usage_status"] == "REPORTED" for u in model.usage):
                    context.n_input_tokens = sum(u["prompt_tokens"] for u in model.usage)
                    context.n_output_tokens = sum(u["completion_tokens"] for u in model.usage)
                    if all(u["cached_tokens"] is not None for u in model.usage):
                        context.n_cache_tokens = sum(u["cached_tokens"] for u in model.usage)
                if all(u["cost_usd"] is not None for u in model.usage):
                    context.cost_usd = sum(u["cost_usd"] for u in model.usage)
                context.metadata["provider_metrics"] = model.usage
                context.metadata["cost_statuses"] = sorted({u.get("cost_status", "UNKNOWN") for u in model.usage})
                context.metadata["actual_billed_cost_usd"] = (
                    sum(u["actual_billed_cost_usd"] for u in model.usage)
                    if all(u.get("actual_billed_cost_usd") is not None for u in model.usage) else None)
            agent.save(agent.config.output_path)
            raw = json.loads(agent.config.output_path.read_text())
            trajectory = convert_mini_swe_agent_to_atif(raw, state.episode_id).to_json_dict()
            generated = [step for step in trajectory["steps"] if step["source"] == "agent"]
            for step, usage in zip(generated, model.usage):
                step["model_name"] = usage["returned_model_id"]
                step["reasoning_effort"] = usage["native_effort"]
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
