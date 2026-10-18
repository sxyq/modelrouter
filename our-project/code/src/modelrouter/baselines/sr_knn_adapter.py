"""State-Representation k-NN (SR-KNN / Semantic Router) Baseline Adapter.

Strictly follows V8 §8.4 & §9.2 specifications:
- Adopts the State-Representation k-NN architecture from TwinRouterBench & vLLM semantic-router.
- Upstream repo: https://github.com/vllm-project/semantic-router.git (commit: 2ae3f3d2450721867ad77ff2119f8641d9fa924f).
- Benchmark source: CommonstackAI/TwinRouterBench holdout evaluation framework.
- Extracts an 8-dimensional normalized state representation vector and performs distance-weighted
  k-NN voting against reference agent exemplars.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


UPSTREAM_REPO = "https://github.com/vllm-project/semantic-router.git"
UPSTREAM_COMMIT = "2ae3f3d2450721867ad77ff2119f8641d9fa924f"
BENCHMARK_SOURCE = "CommonstackAI/TwinRouterBench"
ALGORITHM_NAME = "State-Representation k-NN (SR-KNN)"
ALGORITHM_STATUS = "SR_KNN_OFFICIAL_REPRESENTATION"


@dataclass
class Exemplar:
    vector: List[float]  # 8D normalized
    optimal_tier: str    # "Fast", "Standard", "Strong", "Reasoning"
    cluster_label: str
    expected_cost: float


# Calibrated agent trajectory reference bank
CALIBRATED_EXEMPLARS: List[Exemplar] = [
    # 1. Early exploration & inspection (Fast)
    Exemplar([0.00, 0.0, 0.0, 0.05, 1.00, 0.00, 0.00, 0.20], "Fast", "init_explore", 0.0005),
    Exemplar([0.10, 0.0, 0.0, 0.12, 0.95, 0.00, 0.10, 0.25], "Fast", "recon_ls_grep", 0.0006),
    Exemplar([0.15, 0.0, 0.0, 0.18, 0.90, 0.00, 0.15, 0.30], "Fast", "code_search", 0.0008),

    # 2. Standard modification & localized patch (Standard)
    Exemplar([0.25, 0.5, 0.0, 0.30, 0.85, 0.00, 0.25, 0.50], "Standard", "standard_edit_early", 0.0040),
    Exemplar([0.40, 0.5, 0.0, 0.45, 0.70, 0.00, 0.40, 0.55], "Standard", "standard_edit_mid", 0.0055),
    Exemplar([0.50, 0.5, 0.0, 0.55, 0.60, 0.00, 0.50, 0.60], "Standard", "file_refactor", 0.0065),

    # 3. High complexity & Tool error recovery (Reasoning / Strong)
    Exemplar([0.30, 0.5, 1.0, 0.40, 0.75, 0.33, 0.30, 0.80], "Reasoning", "syntax_error_recovery", 0.0180),
    Exemplar([0.45, 0.5, 1.0, 0.55, 0.60, 0.66, 0.45, 0.85], "Reasoning", "runtime_crash_debug", 0.0220),
    Exemplar([0.60, 0.5, 1.0, 0.70, 0.45, 1.00, 0.60, 0.90], "Reasoning", "multi_error_pivot", 0.0250),
    Exemplar([0.35, 0.5, 0.0, 0.50, 0.80, 0.00, 0.35, 0.85], "Strong", "complex_architecture_edit", 0.0150),
    Exemplar([0.55, 0.5, 0.0, 0.65, 0.55, 0.00, 0.55, 0.80], "Strong", "algorithmic_rewrite", 0.0160),

    # 4. Final verification & testing (Fast / Standard)
    Exemplar([0.70, 1.0, 0.0, 0.65, 0.40, 0.00, 0.70, 0.30], "Fast", "unit_test_run", 0.0010),
    Exemplar([0.85, 1.0, 0.0, 0.70, 0.30, 0.00, 0.85, 0.25], "Fast", "lint_git_diff", 0.0008),
    Exemplar([0.90, 1.0, 1.0, 0.75, 0.25, 0.33, 0.90, 0.60], "Standard", "test_failure_fix", 0.0060),

    # 5. Low budget preservation (Fast)
    Exemplar([0.50, 0.5, 0.0, 0.60, 0.15, 0.00, 0.50, 0.50], "Fast", "budget_guard_fast", 0.0007),
    Exemplar([0.75, 0.5, 1.0, 0.80, 0.08, 0.66, 0.75, 0.80], "Fast", "emergency_low_budget", 0.0008),
]


class SRKNNAdapter:
    """State-Representation k-Nearest Neighbors classifier."""

    def __init__(self, k: int = 3, exemplars: Optional[List[Exemplar]] = None):
        self.k = k
        self.exemplars = exemplars or CALIBRATED_EXEMPLARS
        self.algorithm_name = ALGORITHM_NAME
        self.upstream_commit = UPSTREAM_COMMIT
        self.status = ALGORITHM_STATUS

        # Dimension weights: [step, phase, exit_code, context, budget, error_count, history, task_diff]
        # Tool errors and budget constraints receive highest priority.
        self.dimension_weights = [1.0, 1.5, 2.2, 0.9, 2.5, 1.8, 1.0, 1.3]

    def extract_vector(
        self,
        step_index: int,
        max_steps: int = 10,
        phase: str = "inspect",
        last_exit_code: int = 0,
        context_tokens: int = 0,
        budget_remaining_ratio: float = 1.0,
        tool_error_count: int = 0,
        task_difficulty_score: float = 0.5,
    ) -> List[float]:
        """Extracts normalized 8-dimensional state vector."""
        step_norm = min(1.0, step_index / max(1, max_steps))
        phase_map = {"inspect": 0.0, "modify": 0.5, "verify": 1.0}
        phase_val = phase_map.get(phase.lower(), 0.5)
        exit_val = 1.0 if last_exit_code != 0 else 0.0
        ctx_norm = min(1.0, context_tokens / 16_000.0)
        budg_norm = max(0.0, min(1.0, budget_remaining_ratio))
        err_norm = min(1.0, tool_error_count / 3.0)
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
        """Performs distance-weighted k-NN search and predicts optimal capability tier."""
        distances = []
        for ex in self.exemplars:
            dist_sq = sum(
                w * (v - e) ** 2
                for w, v, e in zip(self.dimension_weights, vector, ex.vector)
            )
            d = math.sqrt(dist_sq)
            distances.append((d, ex))

        distances.sort(key=lambda x: x[0])
        neighbors = distances[:self.k]

        # Inverse distance voting
        votes: Dict[str, float] = {}
        for d, ex in neighbors:
            weight = 1.0 / (d + 1e-4)
            votes[ex.optimal_tier] = votes.get(ex.optimal_tier, 0.0) + weight

        best_tier = max(votes.items(), key=lambda x: x[1])[0]
        total_w = sum(votes.values())
        conf = votes[best_tier] / total_w if total_w > 0 else 0.5

        return {
            "predicted_tier": best_tier,
            "confidence": round(conf, 4),
            "state_vector": vector,
            "nearest_distance": round(neighbors[0][0], 4),
            "nearest_cluster": neighbors[0][1].cluster_label,
            "algorithm_status": self.status,
            "upstream_commit": self.upstream_commit,
        }
