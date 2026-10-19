#!/usr/bin/env python3
"""
test_rq4_ablation.py - Unit tests for RQ4 Systematic Ablation Analysis.
"""

import unittest
from modelrouter.experiments.rq4_analysis import RQ4AblationAnalyzer


class TestRQ4Ablation(unittest.TestCase):
    def setUp(self):
        self.analyzer = RQ4AblationAnalyzer()

    def test_table_5_action_ablation(self):
        t5 = self.analyzer.generate_table_5_actions()
        self.assertEqual(len(t5), 5)
        action_ids = [x["action_id"] for x in t5]
        self.assertIn("FIXED_M_E", action_ids)
        self.assertIn("MODEL_ONLY", action_ids)
        self.assertIn("EFFORT_ONLY", action_ids)
        self.assertIn("HIERARCHICAL_M_THEN_E", action_ids)
        self.assertIn("JOINT_M_X_E", action_ids)

        # Joint MxE must have higher pass@1 and cost savings than Model-Only
        joint = next(x for x in t5 if x["action_id"] == "JOINT_M_X_E")
        model_only = next(x for x in t5 if x["action_id"] == "MODEL_ONLY")
        self.assertGreater(joint["pass_at_1"], model_only["pass_at_1"])
        self.assertGreater(joint["cost_savings_pct"], model_only["cost_savings_pct"])

    def test_table_4_information_ablation(self):
        t4 = self.analyzer.generate_table_4_information()
        self.assertGreaterEqual(len(t4), 7)
        full = next(x for x in t4 if x["config_id"] == "T_M_H_FULL")
        self.assertEqual(full["delta_vs_full"], 0.0)

        # T alone must have lower pass@1 than full T+M+H
        t_only = next(x for x in t4 if x["config_id"] == "T_ONLY")
        self.assertLess(t_only["pass_at_1"], full["pass_at_1"])

    def test_table_8_supervision_ablation(self):
        t8 = self.analyzer.generate_table_8_supervision()
        self.assertEqual(len(t8), 6)
        full = next(x for x in t8 if x["config_id"] == "S1_S2_S3_FULL")
        s1_only = next(x for x in t8 if x["config_id"] == "S1_ONLY")
        self.assertGreater(full["s1_accuracy"], s1_only["s1_accuracy"])
        self.assertLess(full["brier_score"], s1_only["brier_score"])

    def test_table_11_checkpoints(self):
        t11 = self.analyzer.generate_table_11_checkpoints()
        self.assertEqual(len(t11), 2)
        laya = next(x for x in t11 if x["model_id"] == "LAYA_421M_CHECKPOINT")
        kev = next(x for x in t11 if x["model_id"] == "KEV_4B_CHECKPOINT")
        # Kev has higher accuracy, Laya has much lower latency
        self.assertGreater(kev["pass_at_1"], laya["pass_at_1"])
        self.assertLess(laya["routing_latency_ms"], kev["routing_latency_ms"])

    def test_fig_7_panels(self):
        fig_7 = self.analyzer.generate_fig_7_data()
        self.assertIn("panel_a_action", fig_7)
        self.assertIn("panel_b_information", fig_7)
        self.assertIn("panel_c_supervision", fig_7)

    def test_execute_and_save(self):
        payload = self.analyzer.execute_and_save()
        self.assertEqual(payload["experiment_id"], "RQ4_SYSTEMATIC_ABLATION")


if __name__ == "__main__":
    unittest.main()
