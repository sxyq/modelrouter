"""State-Representation k-NN (SR-KNN) Router Baseline Adapter.

Extracts an 8-dimensional normalized state vector and performs k-Nearest Neighbors
lookup against reference exemplars to predict optimal model tier.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class Exemplar:
    vector: List[float]  # 8D normalized
    optimal_tier: str    # "Fast", "Standard", "Strong", "Reasoning"
    expected_cost: float


# Calibrated reference exemplar bank
REFERENCE_EXEMPLARS: List[Exemplar] = [
    # Fast initial exploration
    Exemplar([0.0, 0.0, 0.0, 0.05, 1.0, 0.0, 0.0, 0.2], "Fast", 0.0005),
    Exemplar([0.05, 0.0, 0.0, 0.10, 0.95, 0.0, 0.05, 0.2], "Fast", 0.0006),
    # Standard code modification
    Exemplar([0.15, 0.5, 0.0, 0.25, 0.85, 0.0, 0.15, 0.5], "Standard", 0.005),
    Exemplar([0.25, 0.5, 0.0, 0.35, 0.75, 0.0, 0.25, 0.6], "Standard", 0.007),
    # Tool error recovery -> Reasoning
    Exemplar([0.30, 0.5, 1.0, 0.40, 0.70, 0.2, 0.30, 0.8], "Reasoning", 0.018),
    Exemplar([0.40, 0.5, 1.0, 0.55, 0.60, 0.4, 0.40, 0.9], "Reasoning", 0.022),
    # Late verification -> Fast
    Exemplar([0.80, 1.0, 0.0, 0.65, 0.40, 0.0, 0.80, 0.3], "Fast", 0.001),
    Exemplar([0.90, 1.0, 0.0, 0.70, 0.35, 0.0, 0.90, 0.2], "Fast", 0.001),
    # Low budget guard -> Fast
    Exemplar([0.50, 0.5, 0.0, 0.50, 0.10, 0.0, 0.50, 0.5], "Fast", 0.0008),
]


class SRKNNAdapter:
    """State-Representation k-Nearest Neighbors classifier."""

    def __init__(self, k: int = 3, exemplars: Optional[List[Exemplar]] = None):
        self.k = k
        self.exemplars = exemplars or REFERENCE_EXEMPLARS

    def extract_vector(
        self,
        step_index: int,
        max_steps: int,
        phase: str,
        last_exit_code: int,
        context_tokens: int,
        budget_remaining_ratio: float,
        tool_error_count: int,
        task_difficulty_score: float = 0.5,
    ) -> List[float]:
        step_norm = min(1.0, step_index / max(1, max_steps))
        phase_map = {"inspect": 0.0, "modify": 0.5, "verify": 1.0}
        phase_val = phase_map.get(phase.lower(), 0.5)
        exit_val = 1.0 if last_exit_code != 0 else 0.0
        ctx_norm = min(1.0, context_tokens / 16_000.0)
        budg_norm = max(0.0, min(1.0, budget_remaining_ratio))
        err_norm = min(1.0, tool_error_count / 5.0)
        hist_norm = step_norm
        diff_norm = max(0.0, min(1.0, task_difficulty_score))

        return [
            round(step_norm, 3),
            round(phase_val, 3),
            round(exit_val, 3),
            round(ctx_norm, 3),
            round(budg_norm, 3),
            round(err_norm, 3),
            round(hist_norm, 3),
            round(diff_norm, 3),
        ]

    def predict(self, vector: List[float]) -> Dict[str, Any]:
        distances = []
        for ex in self.exemplars:
            # Weighted Euclidean distance (higher weights on error, budget, and phase)
            weights = [1.0, 1.5, 2.0, 0.8, 2.5, 1.5, 1.0, 1.2]
            dist_sq = sum(w * (v - e) ** 2 for w, v, e in zip(weights, vector, ex.vector))
            d = math.sqrt(dist_sq)
            distances.append((d, ex))

        distances.sort(key=lambda x: x[0])
        neighbors = distances[:self.k]

        # Vote
        votes: Dict[str, float] = {}
        for d, ex in neighbors:
            weight = 1.0 / (d + 1e-5)
            votes[ex.optimal_tier] = votes.get(ex.optimal_tier, 0.0) + weight

        best_tier = max(votes.items(), key=lambda x: x[1])[0]
        total_w = sum(votes.values())
        conf = votes[best_tier] / total_w if total_w > 0 else 0.5

        return {
            "predicted_tier": best_tier,
            "confidence": round(conf, 4),
            "state_vector": vector,
            "nearest_distance": round(neighbors[0][0], 4),
        }
