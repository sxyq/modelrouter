"""TwinRouterBench Evaluation Interface.

Provides:
- Dataset loader for TwinRouterBench 970-item step-level holdout set.
- Mapping between TwinRouterBench capability tiers (low, mid, mid_high, high) and agent model pools.
- Offline evaluation metrics: Accuracy, Normalized Score, Confusion Matrix, and Cost Efficiency.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


TIER_MAPPING = {
    "low": 0,
    "mid": 1,
    "mid_high": 2,
    "high": 3,
}

TIER_NAMES = ["low", "mid", "mid_high", "high"]


@dataclass
class TwinRouterRecord:
    instance_id: str
    step_index: int
    state_text: str
    expected_choice: str
    expected_score: int
    raw_data: Dict[str, Any]

    @property
    def key(self) -> str:
        return f"{self.instance_id}_step_{self.step_index}"


class TwinRouterBenchEvaluator:
    def __init__(self, data_path: Optional[str | Path] = None):
        if data_path is None:
            data_path = Path(__file__).resolve().parent.parent.parent / "external" / "benchmarks" / "twinrouterbench" / "test_twinrouterbench_holdout.jsonl"
        self.data_path = Path(data_path)
        if not self.data_path.is_file():
            raise FileNotFoundError(f"TwinRouterBench dataset not found at: {self.data_path}")
        self.records: List[TwinRouterRecord] = self._load_records()

    def _load_records(self) -> List[TwinRouterRecord]:
        records = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                prov = d.get("provenance", {})
                expected = d.get("expected", {})
                records.append(
                    TwinRouterRecord(
                        instance_id=prov.get("instance_id", ""),
                        step_index=prov.get("step_index", 0),
                        state_text=d.get("state", ""),
                        expected_choice=expected.get("routing_tier_choice", "low"),
                        expected_score=expected.get("routing_tier_score", 0),
                        raw_data=d,
                    )
                )
        return records

    def __len__(self) -> int:
        return len(self.records)

    def evaluate_policy(
        self,
        predict_fn: Callable[[TwinRouterRecord], str],
        max_samples: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Evaluates a prediction function on the benchmark.
        
        predict_fn takes TwinRouterRecord and returns one of: 'low', 'mid', 'mid_high', 'high'.
        """
        targets = self.records[:max_samples] if max_samples else self.records
        total = len(targets)
        correct = 0
        confusion: Dict[str, Dict[str, int]] = {
            t: {p: 0 for p in TIER_NAMES} for t in TIER_NAMES
        }
        predictions_dist: Dict[str, int] = {t: 0 for t in TIER_NAMES}

        for rec in targets:
            pred = predict_fn(rec)
            if pred not in TIER_NAMES:
                pred = "low"  # default fallback
            predictions_dist[pred] += 1
            exp = rec.expected_choice
            if exp not in TIER_NAMES:
                exp = "low"
            confusion[exp][pred] += 1
            if pred == exp:
                correct += 1

        acc = correct / total if total > 0 else 0.0
        return {
            "total_samples": total,
            "correct": correct,
            "accuracy": round(acc, 4),
            "predictions_distribution": predictions_dist,
            "confusion_matrix": confusion,
        }
