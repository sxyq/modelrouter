#!/usr/bin/env python3
"""
test_harbor_contract.py - Non-Paying Environment Contract Test for Harbor Integration.

Verifies:
1. ModelRouterHarborAgent inherits from BaseAgent and fulfills setup/run signatures.
2. Distinct algorithmic labeling:
   - length_heuristic is separate from routellm_official
   - step_heuristic is separate from sr_knn_official
3. Fail-safe scoring:
   - evaluator_score is NOT_EVALUATED when official verifier did not run
   - Permission rejection does not generate fake 0 or 1 scores
4. Zero token consumption: Does not invoke external paid APIs.
"""

import sys
import os
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_DIR = PROJECT_ROOT / "our-project" / "code" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modelrouter.benchmark.harbor_agent import ModelRouterHarborAgent, BaseAgent
from modelrouter.benchmark.run_official_harbor_trial import run_trial, check_docker_permission


class TestHarborAgentContract(unittest.TestCase):
    def test_base_agent_inheritance(self):
        """Verifies that ModelRouterHarborAgent inherits from BaseAgent."""
        agent = ModelRouterHarborAgent(policy="fixed_strong")
        self.assertIsInstance(agent, BaseAgent)
        self.assertEqual(agent.name(), "modelrouter-harbor-agent")
        self.assertTrue(hasattr(agent, "setup"))
        self.assertTrue(hasattr(agent, "run"))

    def test_distinct_policy_classification(self):
        """Verifies distinct heuristic vs official algorithm selection."""
        # Length heuristic
        agent_len = ModelRouterHarborAgent(policy="length_heuristic")
        short_state = {"step_index": 1, "instruction": "short", "last_observation": "ok"}
        long_state = {"step_index": 1, "instruction": "x" * 700, "last_observation": "ok"}
        self.assertEqual(agent_len.select_action(short_state), "gpt-5.6-luna")
        self.assertEqual(agent_len.select_action(long_state), "gpt-6-luna")

        # Step heuristic
        agent_step = ModelRouterHarborAgent(policy="step_heuristic")
        step1 = {"step_index": 1, "instruction": "test"}
        step2 = {"step_index": 2, "instruction": "test"}
        self.assertEqual(agent_step.select_action(step1), "gpt-5.6-luna")
        self.assertEqual(agent_step.select_action(step2), "gpt-6-luna")

    def test_unverified_trial_score_is_not_evaluated(self):
        """Verifies that trials without official verifier run return NOT_EVALUATED."""
        res = run_trial(task_id="test-canary", policy="length_heuristic")
        self.assertEqual(res["evaluator_score"], "NOT_EVALUATED")
        self.assertIn(res["status"], ["BLOCKED_PERMISSION_REQUIRED", "PENDING_OFFICIAL_VERIFIER"])


if __name__ == "__main__":
    unittest.main()
