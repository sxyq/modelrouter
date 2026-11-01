#!/usr/bin/env python3
"""Generate a 150,000-token distribution with both uniform KLs equal to 10.

All logarithms are natural, so the divergences are measured in nats.
Seven tokens carry almost all the mass; a strictly positive uniform tail
keeps KL(U || P) finite. Two bracketed scalar solves tune the tail mass
and the relative weight of the first head token.
"""

from pathlib import Path

import numpy as np
from scipy.optimize import brentq

VOCAB_SIZE = 150_000
TARGET_KL = 10.0
TOLERANCE = 0.001
HEAD_SIZE = 7
OUTPUT_PATH = Path("/app/dist.npy")


def kl_divergences(probabilities):
    """Return KL(P || U), KL(U || P) for a positive, normalized vector."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("Probabilities must be a nonempty one-dimensional array.")
    if not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("All probabilities must be finite and strictly positive.")
    if not np.isclose(p.sum(), 1.0, rtol=0.0, atol=1e-12):
        raise ValueError("Probabilities must sum to one.")
    log_ratio = np.log(p) + np.log(p.size)
    return float(np.dot(p, log_ratio)), float(-np.mean(log_ratio))


def build_distribution():
    """Solve for and validate the requested float64 probability vector."""
    tail_size = VOCAB_SIZE - HEAD_SIZE
    counts = np.array([1, HEAD_SIZE - 1, tail_size], dtype=np.float64)

    def grouped_kl(head_fraction, log_tail_mass):
        # Each group has a shared per-token probability. Log-space arithmetic
        # avoids taking logarithms of rounded or underflowed probabilities.
        tail_mass = np.exp(log_tail_mass)
        log_head_mass = np.log1p(-tail_mass)
        log_p = np.array([
            log_head_mass + np.log(head_fraction),
            log_head_mass + np.log1p(-head_fraction) - np.log(HEAD_SIZE - 1),
            log_tail_mass - np.log(tail_size),
        ])
        log_ratio = log_p + np.log(VOCAB_SIZE)
        forward = np.dot(counts * np.exp(log_p), log_ratio)
        backward = -np.dot(counts / VOCAB_SIZE, log_ratio)
        return forward, backward

    def solve_log_tail(head_fraction):
        return brentq(
            lambda log_tail: grouped_kl(head_fraction, log_tail)[1] - TARGET_KL,
            -100.0, -1.0, xtol=1e-13,
        )

    # At equal head weights the forward KL is below 10; assigning half of
    # the head mass to the first token puts it above 10. Both endpoints
    # already have backward KL = 10 thanks to the inner solve.
    head_fraction = brentq(
        lambda fraction: grouped_kl(fraction, solve_log_tail(fraction))[0] - TARGET_KL,
        1.0 / HEAD_SIZE, 0.5, xtol=1e-14,
    )
    tail_mass = np.exp(solve_log_tail(head_fraction))
    p = np.full(VOCAB_SIZE, tail_mass / tail_size, dtype=np.float64)
    p[0] = (1.0 - tail_mass) * head_fraction
    p[1:HEAD_SIZE] = (1.0 - tail_mass) * (1.0 - head_fraction) / (HEAD_SIZE - 1)
    p /= p.sum()

    forward, backward = kl_divergences(p)
    if abs(forward - TARGET_KL) > TOLERANCE or abs(backward - TARGET_KL) > TOLERANCE:
        raise RuntimeError(f"KL targets not satisfied: {forward=}, {backward=}")
    return p


def main():
    probabilities = build_distribution()
    np.save(OUTPUT_PATH, probabilities, allow_pickle=False)
    forward, backward = kl_divergences(probabilities)
    print(f"Saved {OUTPUT_PATH}")
    print(f"Shape: {probabilities.shape}; dtype: {probabilities.dtype}")
    print(f"Sum: {probabilities.sum():.17g}; minimum: {probabilities.min():.17g}")
    print(f"KL(P || U): {forward:.15f}")
    print(f"KL(U || P): {backward:.15f}")


if __name__ == "__main__":
    main()
