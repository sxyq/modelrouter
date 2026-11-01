"""Regression and edge-case tests for the KL-constrained distribution."""

import unittest

import numpy as np
from scipy.stats import entropy

from generate_distribution import (
    KL_TOLERANCE,
    OUTPUT_PATH,
    TARGET_KL,
    VOCAB_SIZE,
    generate_distribution,
    kl_divergences,
    validate_distribution,
)


class DistributionTests(unittest.TestCase):
    def test_saved_distribution_with_independent_scipy_calculation(self):
        probabilities = np.load(OUTPUT_PATH, allow_pickle=False)
        self.assertEqual(probabilities.shape, (VOCAB_SIZE,))
        self.assertEqual(probabilities.dtype, np.dtype(np.float64))
        self.assertTrue(np.all(np.isfinite(probabilities)))
        self.assertTrue(np.all(probabilities > 0.0))
        self.assertTrue(np.all(probabilities <= 1.0))
        self.assertAlmostEqual(float(probabilities.sum()), 1.0, places=12)
        uniform = np.full(VOCAB_SIZE, 1.0 / VOCAB_SIZE)
        forward = float(entropy(probabilities, uniform))
        backward = float(entropy(uniform, probabilities))
        print(f"\nIndependent SciPy KLs: forward={forward:.12f}, backward={backward:.12f}")
        self.assertLessEqual(abs(forward - TARGET_KL), KL_TOLERANCE)
        self.assertLessEqual(abs(backward - TARGET_KL), KL_TOLERANCE)
        np.testing.assert_allclose(
            validate_distribution(probabilities), [forward, backward],
            rtol=0.0, atol=1e-11,
        )

    def test_generator_is_reproducible(self):
        saved = np.load(OUTPUT_PATH, allow_pickle=False)
        np.testing.assert_array_equal(generate_distribution(), saved)

    def test_uniform_distributions_have_zero_kl(self):
        for size in (1, 2, VOCAB_SIZE):
            with self.subTest(size=size):
                np.testing.assert_allclose(
                    kl_divergences(np.full(size, 1.0 / size)),
                    [0.0, 0.0], rtol=0.0, atol=1e-12,
                )

    def test_small_nonuniform_distribution(self):
        probabilities = np.array([0.1, 0.2, 0.7])
        uniform = np.full(3, 1.0 / 3)
        np.testing.assert_allclose(
            kl_divergences(probabilities),
            [entropy(probabilities, uniform), entropy(uniform, probabilities)],
            rtol=0.0, atol=1e-12,
        )

    def test_smallest_positive_float_does_not_overflow(self):
        probabilities = np.array([np.nextafter(0.0, 1.0), 1.0])
        self.assertTrue(np.all(np.isfinite(kl_divergences(probabilities))))

    def test_invalid_distributions_are_rejected(self):
        invalid = [
            np.array([]),
            np.array([[0.5, 0.5]]),
            np.array([0.0, 1.0]),
            np.array([-0.1, 1.1]),
            np.array([np.nan, 1.0]),
            np.array([np.inf, 1.0]),
            np.array([0.2, 0.2]),
        ]
        for probabilities in invalid:
            with self.subTest(probabilities=probabilities):
                with self.assertRaises(ValueError):
                    kl_divergences(probabilities)

    def test_wrong_vocabulary_size_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_distribution(np.array([0.5, 0.5]))

    def test_wrong_kl_targets_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_distribution(np.full(VOCAB_SIZE, 1.0 / VOCAB_SIZE))


if __name__ == "__main__":
    unittest.main()
