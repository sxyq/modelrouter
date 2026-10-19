#!/usr/bin/env python3
"""
test_leakage_and_isolation.py - Unit tests for leakage detector and split isolation.
"""

import unittest
from modelrouter.data_pipeline.leakage_checker import LeakageDetector, normalize_prompt, prompt_hash


class TestLeakageAndIsolation(unittest.TestCase):
    def setUp(self):
        self.detector = LeakageDetector()
        self.detector.register_benchmark_tasks(
            task_ids=["terminal_bench_task_01", "adaptive-rejection-sampler"],
            prompts=["Implement an adaptive rejection sampler in R", "Fix bug in memory allocator"],
        )

    def test_exact_task_id_leakage_detected(self):
        has_leak, detail = self.detector.check_leakage("adaptive-rejection-sampler", "unrelated text")
        self.assertTrue(has_leak)
        self.assertIn("Exact task ID match", detail)

    def test_normalized_prompt_leakage_detected(self):
        # Case variation and punctuation
        dirty_prompt = "  IMPLEMENT an ADAPTIVE rejection sampler in R!  "
        has_leak, detail = self.detector.check_leakage("safe_candidate_id", dirty_prompt)
        self.assertTrue(has_leak)
        self.assertIn("Normalized prompt hash match", detail)

    def test_unrelated_task_passes(self):
        has_leak, detail = self.detector.check_leakage("unique_training_task_999", "Optimize SQL index on users")
        self.assertFalse(has_leak)
        self.assertIsNone(detail)


if __name__ == "__main__":
    unittest.main()
