#!/usr/bin/env python3
"""
test_rq1_rq3_analysis.py - Unit Tests for RQ1 and RQ3 Benchmark Analysis Suites.

Tests:
1. RQ1 Analysis:
   - Analysis execution against sample episodes.
   - Table 3 and Table 10 column structure.
   - Pareto frontier identification.
   - Cost decomposition calculation.
2. RQ3 Analysis:
   - Analysis execution across G0-G3 task decompositions.
   - Table 7 comparison structure.
   - Dual-panel data points for Fig 6.
   - Monotonic property of route calls F and context replication overhead.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_DIR = PROJECT_ROOT / "our-project" / "code" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modelrouter.benchmark.rq1_analysis import analyze_rq1, wilson_score_interval
from modelrouter.benchmark.rq3_analysis import compute_decomposition_benchmarks
from modelrouter.benchmark.rq1_analysis import observed_research_groups


class TestRQ1RQ3Analysis(unittest.TestCase):
    def test_missing_official_factors_produce_no_research_samples(self):
        output = observed_research_groups([], [])
        for number in (4, 5, 6, 7, 8, 9, 11):
            self.assertEqual(output[f"table{number}"], [])
        self.assertEqual(output["fig8"], [])

    def test_observed_factors_use_task_seed_pairs_and_actual_cost_only(self):
        def trial(identifier, policy, success, generator, billed, pool, k):
            return {"trial_id": identifier, "task_name": "same-task", "seed": 42,
                    "task_git_sha": "fixture-source", "task_digest": "fixture-task",
                    "policy": policy, "reward": success, "cost_usd": generator,
                    "actual_billed_cost_usd": billed, "verifier_path": "fixture/test.sh",
                    "agent_metadata": {"pool_id": pool, "pool_k": k, "granularity": "G0",
                       "information_ablation": "T", "action_ablation": "model-only",
                       "supervision_ablation": "S1", "checkpoint_id": "fixture-checkpoint",
                       "workload": "parser", "workload_label_source": "PRE_TASK_MANIFEST",
                       "sandbox_cost_usd": .1, "router_compute_cost_usd": 0.01}}
        records = [trial("fixed", "fixed_strong", 0, 1, 1, "small", 2),
                   trial("routed", "random", 1, .5, .5, "small", 2)]
        output = observed_research_groups(records, [])
        self.assertEqual(output["table9"][0]["delta_success_rate"], 1)
        self.assertIsNone(output["table9"][0]["gain_boundary"])
        self.assertFalse(output["table6"][0]["publication_eligible"])
        records.append(trial("large", "random", 1, .4, None, "large", 4))
        output = observed_research_groups(records, [])
        random_pools = [r for r in output["table6"] if r["policy"] == "random"]
        self.assertTrue(all(r["paired_task_seed_sets"] for r in random_pools))
        self.assertIsNone(next(r for r in random_pools if r["pool_k"] == 4)["actual_complete_mean_usd"])
        self.assertEqual(output["table9"], [])  # Ambiguous repeated workload cells are not overwritten.

    def test_wilson_score_interval(self):
        """Verifies Wilson score confidence interval computation."""
        low, high = wilson_score_interval(successes=5, total=10)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)
        self.assertTrue(0.0 <= low <= high <= 1.0)

    def test_rq1_analysis_pipeline(self):
        """Verifies RQ1 analysis correctly aggregates episodes and identifies Pareto frontier."""
        sample_episodes = [
            {"policy_id": "fixed_strong", "resolved": True, "total_cost_usd": 0.025, "total_steps": 4, "elapsed_time_sec": 10.0, "total_prompt_tokens": 1000, "total_completion_tokens": 100, "total_reasoning_tokens": 20, "total_cached_tokens": 100},
            {"policy_id": "fixed_strong", "resolved": False, "total_cost_usd": 0.020, "total_steps": 4, "elapsed_time_sec": 12.0, "total_prompt_tokens": 1000, "total_completion_tokens": 80, "total_reasoning_tokens": 10, "total_cached_tokens": 100},
            {"policy_id": "fixed_cheap", "resolved": True, "total_cost_usd": 0.001, "total_steps": 3, "elapsed_time_sec": 3.0, "total_prompt_tokens": 800, "total_completion_tokens": 60, "total_reasoning_tokens": 0, "total_cached_tokens": 50},
            {"policy_id": "fixed_cheap", "resolved": False, "total_cost_usd": 0.001, "total_steps": 3, "elapsed_time_sec": 3.5, "total_prompt_tokens": 800, "total_completion_tokens": 60, "total_reasoning_tokens": 0, "total_cached_tokens": 50},
            {"policy_id": "kev_4b", "resolved": True, "total_cost_usd": 0.003, "total_steps": 4, "elapsed_time_sec": 6.0, "total_prompt_tokens": 900, "total_completion_tokens": 70, "total_reasoning_tokens": 15, "total_cached_tokens": 80},
        ]

        res = analyze_rq1(sample_episodes)
        self.assertEqual(res["total_episodes_analyzed"], 5)
        self.assertTrue(len(res["table3_main_results"]) >= 3)
        self.assertTrue(len(res["table10_cost_ledger"]) >= 3)

        pareto = res["fig3_pareto_frontier"]["pareto_optimal_points"]
        self.assertTrue(len(pareto) >= 1)

    def test_rq3_analysis_pipeline(self):
        """Verifies RQ3 decomposition matrix across G0..G3."""
        res = compute_decomposition_benchmarks()
        self.assertEqual(res["analysis_target"], "RQ3 Task Decomposition Granularity (G0..G3)")

        table7 = res["table7_decomposition_matrix"]
        self.assertEqual(len(table7), 8)  # 4 levels x 2 policies

        levels = [r["decomposition_level"] for r in table7]
        self.assertIn("G0", levels)
        self.assertIn("G1", levels)
        self.assertIn("G2", levels)
        self.assertIn("G3", levels)

        dual_panel = res["fig6_dual_panel"]
        self.assertEqual(len(dual_panel["panel_a_success"]), 4)
        self.assertEqual(len(dual_panel["panel_b_cost"]), 4)

        # Verify monotonic increase of available decision points F
        f_calls = [p["route_calls_f"] for p in dual_panel["panel_b_cost"]]
        self.assertEqual(f_calls, sorted(f_calls))


if __name__ == "__main__":
    unittest.main()
