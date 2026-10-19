#!/usr/bin/env python3
"""
test_rq5_boundary.py - Unit tests for RQ5 Workload Applicability Boundary Analysis.
"""

import unittest
from modelrouter.experiments.rq5_analysis import RQ5BoundaryAnalyzer


class TestRQ5Boundary(unittest.TestCase):
    def setUp(self):
        self.analyzer = RQ5BoundaryAnalyzer()

    def test_table_9_workload_boundary(self):
        t9 = self.analyzer.generate_table_9_data()
        self.assertEqual(len(t9), 4)

        categories = [x["category_id"] for x in t9]
        self.assertIn("CODING", categories)
        self.assertIn("TOOL_HEAVY", categories)
        self.assertIn("CONTEXT_HEAVY", categories)
        self.assertIn("MULTI_AGENT_COORDINATION", categories)

        coding = next(x for x in t9 if x["category_id"] == "CODING")
        self.assertGreater(coding["delta_success"], 0.0)
        self.assertGreater(coding["net_cost_savings_pct"], 50.0)
        self.assertFalse(coding["negative_gain_risk"])

        # Check negative-gain region is properly detected for multi-agent coordination
        multi_agent = next(x for x in t9 if x["category_id"] == "MULTI_AGENT_COORDINATION")
        self.assertLess(multi_agent["delta_success"], 0.0)
        self.assertTrue(multi_agent["negative_gain_risk"])
        self.assertEqual(multi_agent["boundary_regime"], "NEGATIVE_GAIN_BOUNDARY")

    def test_ci95_calculation(self):
        low, high = RQ5BoundaryAnalyzer.calculate_delta_ci95(0.68, 0.704, 250)
        self.assertLess(low, 0.024)
        self.assertGreater(high, 0.024)

    def test_fig_8_phase_diagram(self):
        fig_8 = self.analyzer.generate_fig_8_data()
        self.assertIn("points", fig_8)
        self.assertEqual(len(fig_8["points"]), 4)
        self.assertIn("decision_boundary_rule", fig_8)

    def test_execute_and_save(self):
        payload = self.analyzer.execute_and_save()
        self.assertEqual(payload["experiment_id"], "RQ5_WORKLOAD_APPLICABILITY_BOUNDARY")


if __name__ == "__main__":
    unittest.main()
