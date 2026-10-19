#!/usr/bin/env python3
"""
test_rq2_pools.py - Unit tests for RQ2 model pool architecture and K-selection analysis.
"""

import unittest
from modelrouter.experiments.rq2_analysis import RQ2PoolAnalyzer


class TestRQ2Pools(unittest.TestCase):
    def setUp(self):
        self.analyzer = RQ2PoolAnalyzer()

    def test_registry_loaded(self):
        self.assertGreater(len(self.analyzer.models_data), 5)
        self.assertIn("gpt-4o", self.analyzer.models_data)
        self.assertIn("claude-3-7-sonnet", self.analyzer.models_data)

    def test_table_6_generation(self):
        table_6 = self.analyzer.generate_table_6_data()
        self.assertEqual(len(table_6), 5)
        pool_ids = [p["pool_id"] for p in table_6]
        self.assertIn("AA_PARETO", pool_ids)
        self.assertIn("AGENT_DEV", pool_ids)
        self.assertIn("PRICE_TIERED", pool_ids)
        self.assertIn("COMPLEMENTARY", pool_ids)
        self.assertIn("RANDOM", pool_ids)

        for p in table_6:
            self.assertEqual(p["k"], 5)
            self.assertGreater(p["simulated_pass_at_1"], 0.60)
            self.assertGreater(p["cost_reduction_vs_flagship_pct"], 50.0)

    def test_fig_5_k_scaling(self):
        fig_5 = self.analyzer.generate_fig_5_data()
        self.assertIn("series", fig_5)
        series = fig_5["series"]
        self.assertEqual(len(series), 4)  # K in {3, 5, 8, 12}
        k_values = [p["k"] for p in series]
        self.assertEqual(k_values, [3, 5, 8, 12])

        # Verify monotonic pass@1 increase with diminishing returns
        for i in range(1, len(series)):
            self.assertGreaterEqual(series[i]["pass_at_1"], series[i - 1]["pass_at_1"])

    def test_execute_and_save(self):
        res = self.analyzer.execute_and_save()
        self.assertEqual(res["experiment_id"], "RQ2_MODEL_POOLS")
        self.assertEqual(len(res["table_6_equal_k_pools"]), 5)


if __name__ == "__main__":
    unittest.main()
