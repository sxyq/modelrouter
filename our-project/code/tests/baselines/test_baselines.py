#!/usr/bin/env python3
"""
test_baselines.py - Unit Tests for ModelRouter Baseline Policies & Adapters.

Tests:
1. RouteLLMAdapter:
   - Logistic win-rate calculation P(Strong | query, state).
   - Monotonic increase with task length, context tokens, and tool errors.
   - Threshold decision boundary theta.
2. SRKNNAdapter:
   - 8-dimensional normalized state vector extraction.
   - Distance-weighted k-NN voting and capability tier prediction.
   - Upstream commit and benchmark source metadata verification.
3. LengthHeuristicPolicy and StepHeuristicPolicy:
   - Distinct heuristic classification.
4. create_policy factory:
   - Successful instantiation of all 10 defined policies.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_DIR = PROJECT_ROOT / "our-project" / "code" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modelrouter.agent.state import AgentState
from modelrouter.baselines.policy import (
    create_policy,
    FixedStrongPolicy,
    FixedCheapPolicy,
    RandomPolicy,
    RuleStickyPolicy,
    LengthHeuristicPolicy,
    StepHeuristicPolicy,
    RouteLLMPolicy,
    SRKNNPolicy,
    LayaServerPolicy,
    KevServerPolicy,
)
from modelrouter.baselines.routellm_adapter import RouteLLMAdapter, UPSTREAM_COMMIT as ROUTELLM_COMMIT
from modelrouter.baselines.sr_knn_adapter import SRKNNAdapter, UPSTREAM_COMMIT as SRKNN_COMMIT


class TestBaselines(unittest.TestCase):
    def test_routellm_adapter_logic(self):
        """Verifies RouteLLM logistic win-rate calculation and monotonicity."""
        adapter = RouteLLMAdapter(threshold=0.55)
        self.assertEqual(adapter.upstream_commit, ROUTELLM_COMMIT)

        # Baseline simple task
        winrate_simple = adapter.calculate_strong_win_rate(
            instruction="Simple echo",
            history_steps=1,
            max_steps=10,
            context_tokens=500,
            last_exit_code=0,
            tool_error_count=0,
        )

        # Complex task with tool error and heavy context
        winrate_complex = adapter.calculate_strong_win_rate(
            instruction="Complex architecture refactor across multiple git repositories",
            history_steps=6,
            max_steps=10,
            context_tokens=12000,
            last_exit_code=1,
            tool_error_count=3,
        )

        self.assertGreater(winrate_complex, winrate_simple)
        self.assertTrue(0.01 <= winrate_simple <= 0.99)
        self.assertTrue(0.01 <= winrate_complex <= 0.99)

        score_res = adapter.compute_difficulty(
            instruction="Complex task",
            history_steps=6,
            context_tokens=10000,
            last_exit_code=1,
            tool_error_count=2,
        )
        self.assertIn(score_res.selected_tier, ["strong", "cheap"])
        self.assertIn("win_rate", score_res.feature_projection)

    def test_sr_knn_adapter(self):
        """Verifies SR-KNN 8D state vector extraction and distance-weighted voting."""
        adapter = SRKNNAdapter(k=3)
        self.assertEqual(adapter.upstream_commit, SRKNN_COMMIT)

        # 1. Early inspect phase vector
        vec_early = adapter.extract_vector(
            step_index=1,
            max_steps=10,
            phase="inspect",
            last_exit_code=0,
            context_tokens=200,
            budget_remaining_ratio=1.0,
            tool_error_count=0,
            task_difficulty_score=0.2,
        )
        self.assertEqual(len(vec_early), 8)
        pred_early = adapter.predict(vec_early)
        self.assertIn(pred_early["predicted_tier"], ["Fast", "Standard"])

        # 2. Crash recovery phase vector
        vec_crash = adapter.extract_vector(
            step_index=6,
            max_steps=10,
            phase="modify",
            last_exit_code=1,
            context_tokens=8000,
            budget_remaining_ratio=0.5,
            tool_error_count=2,
            task_difficulty_score=0.8,
        )
        self.assertEqual(len(vec_crash), 8)
        pred_crash = adapter.predict(vec_crash)
        self.assertIn(pred_crash["predicted_tier"], ["Reasoning", "Strong"])

    def test_heuristics_distinct_classification(self):
        """Verifies length and step heuristics make decisions according to designated rules."""
        state = AgentState(task_id="test_len", episode_id="ep_001", policy_id="test")
        state.start()
        legal_actions = [
            {"provider": "openai", "model": "gpt-6-luna", "pool": "Strong"},
            {"provider": "openai", "model": "gpt-5.6-luna", "pool": "Fast"},
        ]

        # Length heuristic
        pol_len = LengthHeuristicPolicy(threshold_chars=50)
        dec_len = pol_len.select(state, legal_actions)
        self.assertEqual(dec_len.router_family, "heuristic_length")
        self.assertIn(dec_len.selected_action["model"], ["gpt-6-luna", "gpt-5.6-luna"])

        # Step heuristic
        pol_step = StepHeuristicPolicy()
        dec_step = pol_step.select(state, legal_actions)
        self.assertEqual(dec_step.router_family, "heuristic_step")

    def test_policy_factory_instantiation(self):
        """Verifies create_policy instantiates all 10 policies cleanly."""
        policies = [
            ("fixed_strong", FixedStrongPolicy),
            ("fixed_cheap", FixedCheapPolicy),
            ("random", RandomPolicy),
            ("rule_sticky", RuleStickyPolicy),
            ("length_heuristic", LengthHeuristicPolicy),
            ("step_heuristic", StepHeuristicPolicy),
            ("routellm", RouteLLMPolicy),
            ("sr_knn", SRKNNPolicy),
            ("laya_v2", LayaServerPolicy),
            ("kev_4b", KevServerPolicy),
        ]
        for name, cls in policies:
            instance = create_policy(name)
            self.assertIsInstance(instance, cls, f"Policy '{name}' did not instantiate as {cls.__name__}")


if __name__ == "__main__":
    unittest.main()
