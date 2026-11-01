#!/usr/bin/env python3
"""Generate /app/dist.npy with forward and backward KL both equal to 10.

All logarithms are natural. Seven tokens carry almost all probability mass;
the remaining tokens share a small, strictly positive tail. Two free group
masses suffice to solve the two KL constraints.
"""

from pathlib import Path

import numpy as np
from scipy.optimize import root
from scipy.special import log_softmax

VOCAB_SIZE = 150_000
TARGET_KL = 10.0
KL_TOLERANCE = 0.001
OUTPUT_PATH = Path("/app/dist.npy")


def kl_divergences(probabilities: np.ndarray) -> tuple[float, float]:
    """Return KL(P||U) and KL(U||P), rejecting invalid distributions."""
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.ndim != 1 or probabilities.size == 0:
        raise ValueError("Probabilities must be a nonempty one-dimensional array.")
    if not np.all(np.isfinite(probabilities)) or np.any(probabilities <= 0.0):
        raise ValueError("Finite backward KL requires strictly positive probabilities.")
    if not np.isclose(probabilities.sum(), 1.0, rtol=0.0, atol=1e-12):
        raise ValueError("Probabilities must sum to one.")

    log_ratios = np.log(probabilities) + np.log(probabilities.size)
    forward = np.dot(probabilities, log_ratios)
    backward = -np.mean(log_ratios)
    return float(forward), float(backward)


def validate_distribution(probabilities: np.ndarray) -> tuple[float, float]:
    """Check the required vocabulary size, validity, and both target KLs."""
    if probabilities.shape != (VOCAB_SIZE,):
        raise ValueError(f"Expected exactly {VOCAB_SIZE} probabilities.")
    divergences = kl_divergences(probabilities)
    if not np.all(np.isfinite(divergences)) or np.any(
        np.abs(np.asarray(divergences) - TARGET_KL) > KL_TOLERANCE
    ):
        raise ValueError(f"KL constraints not satisfied: {divergences}")
    return divergences


def generate_distribution() -> np.ndarray:
    """Solve two group-mass parameters and expand to 150,000 probabilities."""
    # The required entropy is log(150000) - 10, just below log(7).
    # Split the seven high-probability tokens into groups of one and six.
    counts = np.array([1, 6, VOCAB_SIZE - 7], dtype=np.int64)
    uniform_group_masses = counts / VOCAB_SIZE
    log_counts = np.log(counts)
    log_vocab_size = np.log(VOCAB_SIZE)

    def grouped_divergences(parameters: np.ndarray) -> np.ndarray:
        # The tail group's logit is fixed at zero. Softmax ensures positive,
        # normalized group masses while allowing two unconstrained variables.
        log_masses = log_softmax(np.r_[parameters, 0.0])
        log_ratios = log_masses - log_counts + log_vocab_size
        return np.array(
            [
                np.dot(np.exp(log_masses), log_ratios),
                -np.dot(uniform_group_masses, log_ratios),
            ]
        )

    # Begin with about exp(-10) total tail mass and a 1:3 split of head mass.
    initial = np.log(np.array([0.25, 0.75])) + TARGET_KL
    solution = root(
        lambda parameters: grouped_divergences(parameters) - TARGET_KL,
        initial,
        method="hybr",
        options={"xtol": 1e-11},
    )
    if not solution.success or not np.all(np.isfinite(solution.x)):
        raise RuntimeError(f"KL solver failed: {solution.message}")

    group_masses = np.exp(log_softmax(np.r_[solution.x, 0.0]))
    probabilities = np.repeat(group_masses / counts, counts)
    probabilities /= probabilities.sum()
    validate_distribution(probabilities)
    return probabilities


def main() -> None:
    probabilities = generate_distribution()
    np.save(OUTPUT_PATH, probabilities, allow_pickle=False)

    # Verify the actual saved artifact, not just the in-memory construction.
    saved = np.load(OUTPUT_PATH, allow_pickle=False)
    if not np.array_equal(saved, probabilities):
        raise RuntimeError("Saved distribution differs from the generated one.")
    forward, backward = validate_distribution(saved)
    print(f"Saved {OUTPUT_PATH} ({saved.size:,} probabilities, {saved.dtype})")
    print(f"Sum: {saved.sum():.16f}")
    print(f"Minimum probability: {saved.min():.12e}")
    print(f"KL(P||U): {forward:.12f}")
    print(f"KL(U||P): {backward:.12f}")


if __name__ == "__main__":
    main()
