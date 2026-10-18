"""Agent Execution State and Pre-Decision Snapshot Tracker.

Tracks complete Agent lifecycle, step traces, token expenditures, and budget limits
strictly following V8 §7.3 & §7.5.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EpisodeStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    TOOL_ERROR_BUDGET_EXCEEDED = "TOOL_ERROR_BUDGET_EXCEEDED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


class PhaseType(str, Enum):
    INSPECT = "inspect"
    MODIFY = "modify"
    VERIFY = "verify"


@dataclass
class StepTrace:
    step_index: int
    phase: str
    selected_action: Dict[str, Any]
    thought: str
    tool_action: str
    tool_observation: str
    tool_exit_code: int
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    cached_tokens: int
    step_cost_usd: float
    step_duration_sec: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "phase": self.phase,
            "selected_action": self.selected_action,
            "thought": self.thought[:500] if len(self.thought) > 500 else self.thought,
            "tool_action": self.tool_action,
            "tool_observation": self.tool_observation[:500] if len(self.tool_observation) > 500 else self.tool_observation,
            "tool_exit_code": self.tool_exit_code,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cached_tokens": self.cached_tokens,
            "step_cost_usd": self.step_cost_usd,
            "step_duration_sec": round(self.step_duration_sec, 3),
            "timestamp": self.timestamp,
        }


@dataclass
class PreDecisionSnapshot:
    step_index: int
    phase: str
    last_tool_exit_code: int
    last_observation_summary: str
    history_length: int
    budget_remaining_usd: float
    steps_remaining: int
    context_tokens_approx: int
    task_id: str
    episode_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_index": self.step_index,
            "phase": self.phase,
            "last_tool_exit_code": self.last_tool_exit_code,
            "last_observation_summary": self.last_observation_summary,
            "history_length": self.history_length,
            "budget_remaining_usd": round(self.budget_remaining_usd, 4),
            "steps_remaining": self.steps_remaining,
            "context_tokens_approx": self.context_tokens_approx,
            "task_id": self.task_id,
            "episode_id": self.episode_id,
            "timestamp": self.timestamp,
        }


class AgentState:
    """Manages full state and budget tracking for a single Agent episode."""

    def __init__(
        self,
        task_id: str,
        episode_id: str,
        policy_id: str,
        seed: int = 42,
        max_steps: int = 20,
        time_budget_sec: float = 300.0,
        usd_budget: float = 2.0,
        max_tool_error_budget: int = 5,
    ):
        self.task_id = task_id
        self.episode_id = episode_id
        self.policy_id = policy_id
        self.seed = seed
        self.max_steps = max_steps
        self.time_budget_sec = time_budget_sec
        self.usd_budget = usd_budget
        self.max_tool_error_budget = max_tool_error_budget

        self.step_index = 0
        self.current_phase = PhaseType.INSPECT.value
        self.history: List[StepTrace] = []
        self.status = EpisodeStatus.INITIALIZED

        # Budget & Usage
        self.accumulated_cost_usd: float = 0.0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_reasoning_tokens: int = 0
        self.total_cached_tokens: int = 0
        self.tool_error_count: int = 0

        self.start_time: float = time.time()
        self.end_time: Optional[float] = None

    @property
    def elapsed_time_sec(self) -> float:
        if self.end_time is not None:
            return round(self.end_time - self.start_time, 3)
        return round(time.time() - self.start_time, 3)

    @property
    def budget_remaining_usd(self) -> float:
        return max(0.0, self.usd_budget - self.accumulated_cost_usd)

    @property
    def steps_remaining(self) -> int:
        return max(0, self.max_steps - self.step_index)

    def start(self) -> None:
        self.start_time = time.time()
        self.status = EpisodeStatus.RUNNING

    def check_termination(self) -> Optional[EpisodeStatus]:
        """Checks if budget or step limits have been exceeded."""
        if self.step_index >= self.max_steps:
            return EpisodeStatus.TIMEOUT
        if self.elapsed_time_sec >= self.time_budget_sec:
            return EpisodeStatus.TIMEOUT
        if self.accumulated_cost_usd >= self.usd_budget:
            return EpisodeStatus.BUDGET_EXCEEDED
        if self.tool_error_count >= self.max_tool_error_budget:
            return EpisodeStatus.TOOL_ERROR_BUDGET_EXCEEDED
        return None

    def build_pre_decision_snapshot(self) -> PreDecisionSnapshot:
        last_exit = 0
        last_obs = "Initial task prompt"
        if self.history:
            last = self.history[-1]
            last_exit = last.tool_exit_code
            last_obs = last.tool_observation[:150]

        # Context tokens approximation: roughly 4 chars per token for all history
        approx_chars = sum(len(h.thought) + len(h.tool_action) + len(h.tool_observation) for h in self.history)
        approx_tokens = approx_chars // 4

        return PreDecisionSnapshot(
            step_index=self.step_index,
            phase=self.current_phase,
            last_tool_exit_code=last_exit,
            last_observation_summary=last_obs,
            history_length=len(self.history),
            budget_remaining_usd=self.budget_remaining_usd,
            steps_remaining=self.steps_remaining,
            context_tokens_approx=approx_tokens,
            task_id=self.task_id,
            episode_id=self.episode_id,
        )

    def record_step(
        self,
        selected_action: Dict[str, Any],
        thought: str,
        tool_action: str,
        tool_observation: str,
        tool_exit_code: int,
        prompt_tokens: int,
        completion_tokens: int,
        reasoning_tokens: int,
        cached_tokens: int,
        step_cost_usd: float,
        step_duration_sec: float,
    ) -> None:
        trace = StepTrace(
            step_index=self.step_index,
            phase=self.current_phase,
            selected_action=selected_action,
            thought=thought,
            tool_action=tool_action,
            tool_observation=tool_observation,
            tool_exit_code=tool_exit_code,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            cached_tokens=cached_tokens,
            step_cost_usd=step_cost_usd,
            step_duration_sec=step_duration_sec,
        )
        self.history.append(trace)

        # Update totals
        self.accumulated_cost_usd = round(self.accumulated_cost_usd + step_cost_usd, 6)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_reasoning_tokens += reasoning_tokens
        self.total_cached_tokens += cached_tokens

        if tool_exit_code != 0:
            self.tool_error_count += 1

        self.step_index += 1

        # Advance G1 phase heuristics
        if self.step_index == 1:
            self.current_phase = PhaseType.MODIFY.value
        elif self.step_index >= max(2, self.max_steps - 3):
            self.current_phase = PhaseType.VERIFY.value

    def finish(self, status: EpisodeStatus) -> None:
        self.status = status
        self.end_time = time.time()

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "episode_id": self.episode_id,
            "policy_id": self.policy_id,
            "seed": self.seed,
            "status": self.status.value,
            "total_steps": self.step_index,
            "elapsed_time_sec": self.elapsed_time_sec,
            "accumulated_cost_usd": self.accumulated_cost_usd,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_reasoning_tokens": self.total_reasoning_tokens,
            "total_cached_tokens": self.total_cached_tokens,
            "tool_error_count": self.tool_error_count,
        }
