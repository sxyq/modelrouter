"""Single Agent Decision Loop for ModelRouter Agent Pilot.

Strictly adheres to V8 §7.3:
- ReAct / Reflexion loop with single shell action parsing.
- Dynamic per-step Model × Native Effort routing.
- Immutable pre-decision state snapshotting.
- Strict termination conditions and budget gates.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

from experiments.agent_pilot.policy import BasePolicy
from experiments.agent_pilot.provider import BaseGeneratorProvider, GeneratorResponse
from experiments.agent_pilot.registry import MODEL_REGISTRY, ModelRegistry
from experiments.agent_pilot.router_clients import RouterDecision
from experiments.agent_pilot.state import AgentState, EpisodeStatus
from experiments.harbor.environment import BaseSandboxEnvironment

logger = logging.getLogger("experiments.agent_pilot.agent")


SYSTEM_PROMPT = """You are an autonomous software engineering and systems agent.
You solve tasks in a containerized environment by executing single bash commands.
Use the following ReAct format strictly:
Thought: <your reasoning for this step>
Action: <single bash command to run, or FINISH when verified>
"""


@dataclass
class EpisodeResult:
    task_id: str
    episode_id: str
    policy_id: str
    seed: int
    status: str
    resolved: bool
    score: float
    total_steps: int
    elapsed_time_sec: float
    total_cost_usd: float
    total_prompt_tokens: int
    total_completion_tokens: int
    total_reasoning_tokens: int
    total_cached_tokens: int
    router_decisions: List[Dict[str, Any]]
    step_traces: List[Dict[str, Any]]
    evaluator_details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "episode_id": self.episode_id,
            "policy_id": self.policy_id,
            "seed": self.seed,
            "status": self.status,
            "resolved": self.resolved,
            "score": self.score,
            "total_steps": self.total_steps,
            "elapsed_time_sec": self.elapsed_time_sec,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_reasoning_tokens": self.total_reasoning_tokens,
            "total_cached_tokens": self.total_cached_tokens,
            "router_decisions_count": len(self.router_decisions),
            "evaluator_details": self.evaluator_details,
        }


class SingleAgent:
    """Core Single Agent loop with dynamic routing."""

    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        max_steps: int = 15,
        time_budget_sec: float = 180.0,
        usd_budget: float = 2.0,
        max_tool_error_budget: int = 5,
    ):
        self.registry = registry or ModelRegistry()
        self.max_steps = max_steps
        self.time_budget_sec = time_budget_sec
        self.usd_budget = usd_budget
        self.max_tool_error_budget = max_tool_error_budget

    def run_episode(
        self,
        task: Dict[str, Any],
        environment: BaseSandboxEnvironment,
        policy: BasePolicy,
        provider: BaseGeneratorProvider,
        seed: int = 42,
    ) -> EpisodeResult:
        task_id = task.get("task_id", "unknown_task")
        episode_id = f"ep_{task_id}_{uuid4().hex[:8]}"

        state = AgentState(
            task_id=task_id,
            episode_id=episode_id,
            policy_id=policy.policy_id,
            seed=seed,
            max_steps=self.max_steps,
            time_budget_sec=self.time_budget_sec,
            usd_budget=self.usd_budget,
            max_tool_error_budget=self.max_tool_error_budget,
        )
        state.start()

        # Reset environment
        environment.reset(task)

        # Messages for LLM
        instruction = task.get("description") or task.get("instruction") or f"Task: {task_id}"
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Task instructions:\n{instruction}"},
        ]

        legal_actions = self.registry.list_legal_actions()
        router_decisions: List[Dict[str, Any]] = []

        is_done = False
        while not is_done:
            # 1. Termination check
            term = state.check_termination()
            if term is not None:
                state.finish(term)
                break

            step_t0 = time.time()

            # 2. Immutable Pre-decision snapshot & Route
            decision = policy.route(state, legal_actions)
            router_decisions.append(decision.to_dict())

            selected = decision.selected_action
            model_id = selected.get("model", "gpt-4o-mini")
            native_effort = selected.get("native_effort", "none")
            model_spec = self.registry.get_spec(model_id)

            # 3. Call Generator Provider
            try:
                gen_resp: GeneratorResponse = provider.generate(
                    messages=messages,
                    model_spec=model_spec,
                    native_effort=native_effort,
                )
            except Exception as e:
                logger.error("Generator error at step %d: %s", state.step_index, e)
                state.finish(EpisodeStatus.PROVIDER_UNAVAILABLE)
                break

            # 4. Check for Agent termination signal
            if gen_resp.is_finish:
                is_done = True
                # Record step
                state.record_step(
                    selected_action=selected,
                    thought=gen_resp.thought,
                    tool_action="FINISH",
                    tool_observation="Agent signaled task completion.",
                    tool_exit_code=0,
                    prompt_tokens=gen_resp.prompt_tokens,
                    completion_tokens=gen_resp.completion_tokens,
                    reasoning_tokens=gen_resp.reasoning_tokens,
                    cached_tokens=gen_resp.cached_tokens,
                    step_cost_usd=gen_resp.cost_usd,
                    step_duration_sec=time.time() - step_t0,
                )
                break

            # 5. Execute action in sandbox
            exec_res = environment.exec(gen_resp.action)

            # 6. Record step trace
            obs_text = exec_res.stdout
            if exec_res.stderr:
                obs_text += f"\nSTDERR: {exec_res.stderr}"
            if not obs_text.strip():
                obs_text = f"(Command exited with code {exec_res.exit_code})"

            state.record_step(
                selected_action=selected,
                thought=gen_resp.thought,
                tool_action=gen_resp.action,
                tool_observation=obs_text,
                tool_exit_code=exec_res.exit_code,
                prompt_tokens=gen_resp.prompt_tokens,
                completion_tokens=gen_resp.completion_tokens,
                reasoning_tokens=gen_resp.reasoning_tokens,
                cached_tokens=gen_resp.cached_tokens,
                step_cost_usd=gen_resp.cost_usd,
                step_duration_sec=time.time() - step_t0,
            )

            # 7. Append observation to dialogue history
            messages.append({"role": "assistant", "content": gen_resp.content})
            messages.append({"role": "user", "content": f"Observation (exit code {exec_res.exit_code}):\n{obs_text}"})

        # Evaluate final state
        resolved, score, details = environment.evaluate()
        if state.status == EpisodeStatus.RUNNING:
            state.finish(EpisodeStatus.SUCCESS if resolved else EpisodeStatus.FAILED)

        return EpisodeResult(
            task_id=task_id,
            episode_id=episode_id,
            policy_id=policy.policy_id,
            seed=seed,
            status=state.status.value,
            resolved=resolved,
            score=score,
            total_steps=state.step_index,
            elapsed_time_sec=state.elapsed_time_sec,
            total_cost_usd=state.accumulated_cost_usd,
            total_prompt_tokens=state.total_prompt_tokens,
            total_completion_tokens=state.total_completion_tokens,
            total_reasoning_tokens=state.total_reasoning_tokens,
            total_cached_tokens=state.total_cached_tokens,
            router_decisions=router_decisions,
            step_traces=[t.to_dict() for t in state.history],
            evaluator_details=details,
        )
