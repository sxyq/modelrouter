"""Validation and edge-case tests for the distribution generator."""

import unittest

import numpy as np
from scipy.stats import entropy

from generate_dist import (
    OUTPUT_PATH, TARGET_KL, TOLERANCE, VOCAB_SIZE,
    build_distribution, kl_divergences,
)


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = build_distribution()

    def test_valid_probability_distribution(self):
        self.assertEqual(self.p.shape, (VOCAB_SIZE,))
        self.assertEqual(self.p.dtype, np.dtype("float64"))
        self.assertTrue(np.all(np.isfinite(self.p)))
        self.assertTrue(np.all(self.p > 0))
        self.assertTrue(np.all(self.p <= 1))
        self.assertAlmostEqual(float(self.p.sum()), 1.0, places=14)

    def test_targets_independently_with_scipy(self):
        uniform = np.full(VOCAB_SIZE, 1.0 / VOCAB_SIZE)
        for value in (entropy(self.p, uniform), entropy(uniform, self.p)):
            self.assertLessEqual(abs(value - TARGET_KL), TOLERANCE)

    def test_saved_file_matches_solution(self):
        saved = np.load(OUTPUT_PATH, allow_pickle=False)
        np.testing.assert_array_equal(saved, self.p)
        for value in kl_divergences(saved):
            self.assertLessEqual(abs(value - TARGET_KL), TOLERANCE)

    def test_uniform_and_single_token_distributions(self):
        for size in (1, 7, VOCAB_SIZE):
            with self.subTest(size=size):
                p = np.full(size, 1.0 / size)
                np.testing.assert_allclose(kl_divergences(p), (0.0, 0.0), atol=1e-12)

    def test_positive_skewed_distribution(self):
        forward, backward = kl_divergences([0.9, 0.1])
        self.assertGreater(forward, 0.0)
        self.assertGreater(backward, 0.0)

    def test_invalid_inputs(self):
        invalid = (
            [], [[0.5, 0.5]], [1.0, 0.0], [1.1, -0.1],
            [np.nan, 0.5], [np.inf, 0.5], [0.2, 0.2],
        )
        for p in invalid:
            with self.subTest(probabilities=p):
                with self.assertRaises(ValueError):
                    kl_divergences(p)


if __name__ == "__main__":
    unittest.main()
