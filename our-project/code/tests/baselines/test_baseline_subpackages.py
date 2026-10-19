#!/usr/bin/env python3
"""Unit tests for independent baseline subpackages (routellm, sr_knn, fixed_random_rule)."""
import unittest
from pathlib import Path

from modelrouter.baselines.routellm import RouteLLMAdapter, RouteLLMPolicy
from modelrouter.baselines.sr_knn import SRKNNAdapter, SRKNNPolicy
from modelrouter.baselines.fixed_random_rule import (
    FixedStrongPolicy,
    FixedCheapPolicy,
    RandomPolicy,
    RuleStickyPolicy,
)
from modelrouter.agent.state import AgentState


class TestBaselineSubpackages(unittest.TestCase):
    def test_routellm_subpackage(self):
        adapter = RouteLLMAdapter(threshold=0.6)
        self.assertEqual(adapter.threshold, 0.6)
        score = adapter.compute_difficulty("Implement sorting algorithm")
        self.assertIn(score.selected_tier, ["cheap", "strong"])

        pol = RouteLLMPolicy(threshold=0.55)
        self.assertEqual(pol.policy_id, "routellm")

    def test_sr_knn_subpackage(self):
        adapter = SRKNNAdapter(k=3)
        self.assertEqual(adapter.k, 3)
        vec = adapter.extract_vector(
            step_index=1,
            max_steps=10,
            phase="inspect",
            last_exit_code=0,
            context_tokens=500,
            budget_remaining_ratio=1.0,
            tool_error_count=0,
            task_difficulty_score=0.3,
        )
        self.assertEqual(len(vec), 8)
        pred = adapter.predict(vec)
        self.assertIn("predicted_tier", pred)

        pol = SRKNNPolicy(k=3)
        self.assertEqual(pol.policy_id, "sr_knn")

    def test_fixed_random_rule_subpackage(self):
        state = AgentState("test_task", "test_ep", "rule_sticky")
        state.start()
        actions = [
            {"provider": "openai", "model": "gpt-6-luna", "pool": "Strong"},
            {"provider": "openai", "model": "gpt-5.6-luna", "pool": "Fast"},
        ]

        p_strong = FixedStrongPolicy()
        dec_strong = p_strong.select(state, actions)
        self.assertEqual(dec_strong.selected_action["model"], "gpt-6-luna")

        p_cheap = FixedCheapPolicy()
        dec_cheap = p_cheap.select(state, actions)
        self.assertEqual(dec_cheap.selected_action["model"], "gpt-5.6-luna")

        p_rule = RuleStickyPolicy()
        dec_rule = p_rule.select(state, actions)
        self.assertIn(dec_rule.selected_action["model"], ["gpt-6-luna", "gpt-5.6-luna"])


if __name__ == "__main__":
    unittest.main()
