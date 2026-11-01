#!/usr/bin/env python3
"""Construct P with KL(P || U) = KL(U || P) = 10 using natural logs."""
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

VOCAB_SIZE = 150_000
CORE_SIZE = 7
TAIL_SIZE = VOCAB_SIZE - CORE_SIZE
TARGET = 10.0
TOLERANCE = 0.001
OUTPUT = Path('/app/dist.npy')
LOG_N = np.log(VOCAB_SIZE)


def kl_to_uniform(probabilities):
    """Return forward and backward KL for a strictly positive distribution."""
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1 or p.size == 0:
        raise ValueError('Expected a nonempty one-dimensional array.')
    if not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError('Probabilities must be finite and strictly positive.')
    if not np.isclose(p.sum(), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError('Probabilities must sum to one.')
    log_ratio = np.log(p) + np.log(p.size)
    return float(np.sum(p * log_ratio)), float(-np.mean(log_ratio))


def grouped_kl(q, log_tail_mass):
    """KL values for six equal core tokens, one special token, and a tail.

    q is the special token's fraction of the core mass. All tail tokens
    share the remaining mass equally. Logarithmic arithmetic keeps the
    backward-KL calculation stable even for very small tail probabilities.
    """
    tail_mass = np.exp(log_tail_mass)
    core_mass = 1.0 - tail_mass
    log_core_mass = np.log1p(-tail_mass)
    log_common = log_core_mass + np.log1p(-q) - np.log(CORE_SIZE - 1)
    log_special = log_core_mass + np.log(q)
    log_tail = log_tail_mass - np.log(TAIL_SIZE)
    forward = (
        core_mass * (1.0 - q) * (LOG_N + log_common)
        + core_mass * q * (LOG_N + log_special)
        + tail_mass * (LOG_N + log_tail)
    )
    backward = -(
        (CORE_SIZE - 1) * (LOG_N + log_common)
        + (LOG_N + log_special)
        + TAIL_SIZE * (LOG_N + log_tail)
    ) / VOCAB_SIZE
    return forward, backward


def solve_log_tail(q):
    return brentq(
        lambda log_mass: grouped_kl(q, log_mass)[1] - TARGET,
        -100.0,
        np.log(TAIL_SIZE / VOCAB_SIZE),
        xtol=1e-13,
        rtol=1e-14,
    )


def find_distribution():
    # First satisfy backward KL by solving for the tail mass; then tune q
    # to satisfy forward KL without changing backward KL.
    q = brentq(
        lambda q: grouped_kl(q, solve_log_tail(q))[0] - TARGET,
        1e-12,
        1.0 / CORE_SIZE,
        xtol=1e-14,
        rtol=1e-14,
    )
    tail_mass = np.exp(solve_log_tail(q))
    p = np.full(VOCAB_SIZE, tail_mass / TAIL_SIZE, dtype=np.float64)
    p[:CORE_SIZE - 1] = (1.0 - tail_mass) * (1.0 - q) / (CORE_SIZE - 1)
    p[CORE_SIZE - 1] = (1.0 - tail_mass) * q
    p /= p.sum()
    forward, backward = kl_to_uniform(p)
    if max(abs(forward - TARGET), abs(backward - TARGET)) > TOLERANCE:
        raise RuntimeError(f'KL targets not satisfied: {forward}, {backward}')
    return p


def main():
    p = find_distribution()
    np.save(OUTPUT, p, allow_pickle=False)
    # Verify the artifact, not just the in-memory candidate.
    saved = np.load(OUTPUT, allow_pickle=False)
    if saved.shape != (VOCAB_SIZE,) or not np.array_equal(p, saved):
        raise RuntimeError('Saved distribution failed the round-trip check.')
    forward, backward = kl_to_uniform(saved)
    print(f'Saved {OUTPUT}: shape={saved.shape}, dtype={saved.dtype}')
    print(f'Sum={saved.sum():.17g}; minimum={saved.min():.17g}')
    print(f'KL(P||U)={forward:.15f}')
    print(f'KL(U||P)={backward:.15f}')


if __name__ == '__main__':
    main()
