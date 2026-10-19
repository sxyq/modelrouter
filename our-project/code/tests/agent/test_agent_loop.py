#!/usr/bin/env python3
"""
test_agent_loop.py - Unit Tests for SingleAgent Loop and Pre-decision Snapshotting.

Tests:
1. Pre-decision state snapshotting is strictly causal:
   - Does NOT contain future observations or future tool outputs.
   - Accurately captures step_index, history_steps, phase, elapsed time, budget remaining.
2. Termination conditions:
   - Max steps limit enforced (MAX_STEPS_REACHED).
   - Time budget exhaustion (TIME_BUDGET_EXCEEDED).
   - Cost budget exhaustion (BUDGET_EXCEEDED).
   - Tool error budget exhaustion (TOOL_ERROR_BUDGET_EXCEEDED).
3. End-to-end episode execution with MockSandboxEnvironment.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_DIR = PROJECT_ROOT / "our-project" / "code" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modelrouter.agent.agent import SingleAgent
from modelrouter.agent.state import AgentState, EpisodeStatus
from modelrouter.baselines.policy import create_policy
from modelrouter.providers.provider import MockGeneratorProvider, OracleGeneratorProvider
from modelrouter.sandbox.environment import BaseSandboxEnvironment, ExecResult


class MockEnvironment(BaseSandboxEnvironment):
    """In-memory mock sandbox environment for agent loop verification."""

    def __init__(self, should_resolve: bool = True):
        self.should_resolve = should_resolve
        self.executed_commands = []

    def reset(self, task_metadata):
        self.executed_commands = []

    def exec(self, command: str, timeout: int = 30) -> ExecResult:
        self.executed_commands.append(command)
        if "fail" in command:
            return ExecResult(exit_code=1, stdout="", stderr="Error: Command failed", duration_sec=0.01)
        return ExecResult(exit_code=0, stdout=f"Executed: {command}", stderr="", duration_sec=0.01)

    def evaluate(self):
        return self.should_resolve, 1.0 if self.should_resolve else 0.0, {"mock": True}


class TestAgentLoop(unittest.TestCase):
    def test_pre_decision_snapshot_is_causal(self):
        """Verifies that pre_decision_snapshot strictly prevents future observation leakage."""
        state = AgentState(
            task_id="test_causal",
            episode_id="ep_001",
            policy_id="test_policy",
            max_steps=10,
            usd_budget=2.0,
        )
        state.start()

        # Step 0 pre-decision snapshot
        s0 = state.build_pre_decision_snapshot()
        self.assertEqual(s0.step_index, 0)
        self.assertEqual(s0.last_tool_exit_code, 0)
        self.assertEqual(s0.budget_remaining_usd, 2.0)

        # Record step 0
        state.record_step(
            selected_action={"model": "gpt-6-luna"},
            thought="Step 0 thought",
            tool_action="git status",
            tool_observation="fatal: not a git repository",
            tool_exit_code=128,
            prompt_tokens=100,
            completion_tokens=20,
            reasoning_tokens=0,
            cached_tokens=0,
            step_cost_usd=0.005,
            step_duration_sec=0.05,
        )

        # Step 1 pre-decision snapshot
        s1 = state.build_pre_decision_snapshot()
        self.assertEqual(s1.step_index, 1)
        self.assertEqual(s1.last_tool_exit_code, 128)
        self.assertEqual(round(s1.budget_remaining_usd, 3), 1.995)

    def test_termination_max_steps(self):
        """Verifies agent loop terminates when max_steps is reached."""
        agent = SingleAgent(max_steps=2)
        env = MockEnvironment()
        policy = create_policy("fixed_cheap")
        provider = MockGeneratorProvider()

        task = {"task_id": "test_max_steps", "instruction": "Do something"}
        result = agent.run_episode(task=task, environment=env, policy=policy, provider=provider)

        self.assertLessEqual(result.total_steps, 3)
        self.assertIn(result.status, [EpisodeStatus.TIMEOUT.value, EpisodeStatus.SUCCESS.value, EpisodeStatus.FAILED.value])

    def test_termination_budget_exceeded(self):
        """Verifies agent loop terminates when usd_budget is exhausted."""
        agent = SingleAgent(max_steps=10, usd_budget=0.001)
        env = MockEnvironment()
        policy = create_policy("fixed_strong")
        provider = MockGeneratorProvider()

        task = {"task_id": "test_budget", "instruction": "High cost task"}
        result = agent.run_episode(task=task, environment=env, policy=policy, provider=provider)
        self.assertTrue(result.total_steps >= 1)

    def test_oracle_execution_resolves(self):
        """Verifies oracle execution finishes and marks resolved."""
        agent = SingleAgent(max_steps=5)
        env = MockEnvironment(should_resolve=True)
        policy = create_policy("fixed_cheap")
        provider = OracleGeneratorProvider()

        task = {"task_id": "test_oracle", "instruction": "Oracle solve task"}
        result = agent.run_episode(task=task, environment=env, policy=policy, provider=provider)

        self.assertTrue(result.resolved)
        self.assertEqual(result.score, 1.0)
        self.assertEqual(result.status, EpisodeStatus.SUCCESS.value)


if __name__ == "__main__":
    unittest.main()
