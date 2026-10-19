#!/usr/bin/env python3
"""
test_lifecycle_and_parsers.py - Unit tests for Candidate Lifecycle and Metric Parsers.
"""

import unittest
from modelrouter.training.lifecycle import (
    CandidateStage,
    CandidateLifecycleTracker,
    VALID_TRANSITIONS,
)
from modelrouter.training.metric_parsers import (
    S1MetricParser,
    S2MetricParser,
    S3MetricParser,
    KevFixedValParser,
)
from modelrouter.training.supervision_loaders import MultiViewSupervisionLoader


class TestLifecycleAndParsers(unittest.TestCase):
    def test_lifecycle_valid_transitions(self):
        tracker = CandidateLifecycleTracker("TEST-C01", CandidateStage.ZERO_SHOT)
        self.assertTrue(tracker.can_transition_to(CandidateStage.AUX_SMOKE))
        tracker.transition_to(CandidateStage.AUX_SMOKE, {"loss": 0.85})
        self.assertEqual(tracker.current_stage, CandidateStage.AUX_SMOKE)

        self.assertTrue(tracker.can_transition_to(CandidateStage.POINTER_HEAD_PILOT))
        tracker.transition_to(CandidateStage.POINTER_HEAD_PILOT, {"s1_acc": 0.58})

        self.assertTrue(tracker.can_transition_to(CandidateStage.LORA_FINETUNE))
        tracker.transition_to(CandidateStage.LORA_FINETUNE, {"s1_acc": 0.63})

        self.assertTrue(tracker.can_transition_to(CandidateStage.FULL_RUN))
        tracker.transition_to(CandidateStage.FULL_RUN, {"s1_acc": 0.67})

        self.assertTrue(tracker.can_transition_to(CandidateStage.VALIDATED))
        tracker.transition_to(CandidateStage.VALIDATED, {"s1_acc": 0.68, "brier": 0.182})
        self.assertEqual(tracker.current_stage, CandidateStage.VALIDATED)

    def test_lifecycle_invalid_transition_rejected(self):
        tracker = CandidateLifecycleTracker("TEST-C02", CandidateStage.ZERO_SHOT)
        # Cannot jump from ZERO_SHOT directly to VALIDATED
        self.assertFalse(tracker.can_transition_to(CandidateStage.VALIDATED))
        with self.assertRaises(ValueError):
            tracker.transition_to(CandidateStage.VALIDATED)

    def test_s1_metric_parser(self):
        # 561 samples
        preds = []
        for i in range(561):
            is_correct = (i % 3 != 0)  # ~66.7% accuracy
            preds.append({
                "pred_model": "gpt-4o" if is_correct else "gpt-3.5-turbo",
                "target_model": "gpt-4o",
                "prob": 0.75 if is_correct else 0.40,
            })
        res = S1MetricParser.parse(preds)
        self.assertEqual(res["sample_count"], 561)
        self.assertTrue(res["count_matches_expected"])
        self.assertAlmostEqual(res["accuracy"], 0.6667, delta=0.01)
        self.assertLess(res["brier_score"], 0.3)

    def test_s2_metric_parser(self):
        # 337 samples
        preds = []
        for i in range(337):
            resolved = (i % 2 == 0)
            preds.append({
                "pred_prob": 0.8 if resolved else 0.2,
                "task_resolved": resolved,
            })
        res = S2MetricParser.parse(preds)
        self.assertEqual(res["sample_count"], 337)
        self.assertTrue(res["count_matches_expected"])
        self.assertEqual(res["accuracy"], 1.0)
        self.assertEqual(res["f1_score"], 1.0)

    def test_s3_metric_parser(self):
        # 4794 samples
        preds = []
        for i in range(4794):
            actual = (i % 100) / 100.0
            preds.append({
                "pred_ratio": actual + 0.01,
                "actual_ratio": actual,
            })
        res = S3MetricParser.parse(preds)
        self.assertEqual(res["sample_count"], 4794)
        self.assertTrue(res["count_matches_expected"])
        self.assertLess(res["mse"], 0.001)
        self.assertGreater(res["r2_score"], 0.95)

    def test_kev_fixed_val_parser(self):
        # 2437 samples
        preds = []
        for i in range(2437):
            preds.append({
                "target_model": "model_A",
                "pred_model": "model_A" if i % 4 != 0 else "model_B",
                "top3_candidates": ["model_A", "model_B", "model_C"],
                "confidence": 0.80,
            })
        res = KevFixedValParser.parse(preds)
        self.assertEqual(res["sample_count"], 2437)
        self.assertTrue(res["count_matches_expected"])
        self.assertAlmostEqual(res["top1_accuracy"], 0.75, delta=0.01)
        self.assertEqual(res["top3_accuracy"], 1.0)

    def test_supervision_loader_combinations(self):
        loader = MultiViewSupervisionLoader()
        # Test S1 alone
        s1_batches = list(loader.build_combination("S1", batch_size=10, max_samples_per_view=20))
        self.assertGreater(len(s1_batches), 0)

        # Test S1+S2+S3
        multi_batches = list(loader.build_combination("S1+S2+S3", batch_size=12, max_samples_per_view=15))
        self.assertGreater(len(multi_batches), 0)


if __name__ == "__main__":
    unittest.main()
