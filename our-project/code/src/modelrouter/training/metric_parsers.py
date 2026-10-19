#!/usr/bin/env python3
"""
metric_parsers.py - Automated Metric Parsers for ModelRouter Fixed Validation Gates.

Strictly supports:
- S1 (Human Preference / Routing Choice, 561 samples): Accuracy, Brier score, Cross-Entropy loss.
- S2 (Agent Trajectory Resolved, 337 samples): BCE loss, Accuracy, Precision, Recall, F1.
- S3 (Auxiliary Cache Reuse, 4,794 samples): MSE, MAE, R^2.
- Kev Fixed Val (2,437 samples): Top-1 accuracy, Top-3 accuracy, Multi-class Brier score.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence


class S1MetricParser:
    """Parses S1 Human Preference / Routing Choice validation metrics (561 samples benchmark)."""

    EXPECTED_SAMPLE_COUNT = 561

    @staticmethod
    def parse(predictions: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        count = len(predictions)
        if count == 0:
            return {"sample_count": 0, "accuracy": 0.0, "brier_score": 1.0, "cross_entropy": 0.0}

        correct = 0
        brier_sum = 0.0
        ce_sum = 0.0

        for p in predictions:
            pred_choice = p.get("pred_model") or p.get("pred_choice")
            target_choice = p.get("target_model") or p.get("target_choice")
            prob = float(p.get("prob", 0.5))

            is_correct = (pred_choice == target_choice)
            if is_correct:
                correct += 1

            # Brier score calculation: (prob - y)^2
            y = 1.0 if is_correct else 0.0
            brier_sum += (prob - y) ** 2

            # Cross entropy: -log(prob)
            eps = 1e-7
            p_clamped = min(max(prob if is_correct else (1.0 - prob), eps), 1.0 - eps)
            ce_sum += -math.log(p_clamped)

        acc = round(correct / count, 4)
        brier = round(brier_sum / count, 4)
        ce = round(ce_sum / count, 4)

        return {
            "sample_count": count,
            "expected_sample_count": S1MetricParser.EXPECTED_SAMPLE_COUNT,
            "count_matches_expected": (count == S1MetricParser.EXPECTED_SAMPLE_COUNT),
            "accuracy": acc,
            "brier_score": brier,
            "cross_entropy": ce,
        }


class S2MetricParser:
    """Parses S2 Agent Trajectory Resolved validation metrics (337 samples benchmark)."""

    EXPECTED_SAMPLE_COUNT = 337

    @staticmethod
    def parse(predictions: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        count = len(predictions)
        if count == 0:
            return {"sample_count": 0, "accuracy": 0.0, "bce_loss": 0.0, "f1": 0.0}

        tp = fp = tn = fn = 0
        bce_sum = 0.0
        eps = 1e-7

        for p in predictions:
            prob = float(p.get("pred_prob", 0.5))
            target = bool(p.get("task_resolved", False))
            y = 1.0 if target else 0.0

            # Binary cross entropy
            prob_clamped = min(max(prob, eps), 1.0 - eps)
            bce_sum += -(y * math.log(prob_clamped) + (1.0 - y) * math.log(1.0 - prob_clamped))

            pred_bool = (prob >= 0.5)
            if pred_bool and target:
                tp += 1
            elif pred_bool and not target:
                fp += 1
            elif not pred_bool and not target:
                tn += 1
            else:
                fn += 1

        accuracy = round((tp + tn) / count, 4)
        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0
        bce = round(bce_sum / count, 4)

        return {
            "sample_count": count,
            "expected_sample_count": S2MetricParser.EXPECTED_SAMPLE_COUNT,
            "count_matches_expected": (count == S2MetricParser.EXPECTED_SAMPLE_COUNT),
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "bce_loss": bce,
        }


class S3MetricParser:
    """Parses S3 Auxiliary Cache Reuse validation metrics (4,794 samples benchmark)."""

    EXPECTED_SAMPLE_COUNT = 4794

    @staticmethod
    def parse(predictions: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        count = len(predictions)
        if count == 0:
            return {"sample_count": 0, "mse": 0.0, "mae": 0.0, "r2": 0.0}

        mse_sum = 0.0
        mae_sum = 0.0
        actuals = []

        for p in predictions:
            pred = float(p.get("pred_ratio", 0.0))
            actual = float(p.get("actual_ratio", 0.0))
            actuals.append(actual)

            diff = pred - actual
            mse_sum += diff ** 2
            mae_sum += abs(diff)

        mse = round(mse_sum / count, 5)
        mae = round(mae_sum / count, 5)

        # R^2 calculation
        mean_actual = sum(actuals) / count
        ss_tot = sum((y - mean_actual) ** 2 for y in actuals)
        r2 = round(1.0 - (mse_sum / max(1e-7, ss_tot)), 4) if ss_tot > 0 else 0.0

        return {
            "sample_count": count,
            "expected_sample_count": S3MetricParser.EXPECTED_SAMPLE_COUNT,
            "count_matches_expected": (count == S3MetricParser.EXPECTED_SAMPLE_COUNT),
            "mse": mse,
            "mae": mae,
            "r2_score": max(-1.0, min(1.0, r2)),
        }


class KevFixedValParser:
    """Parses Kev Fixed Validation Metrics (2,437 samples benchmark)."""

    EXPECTED_SAMPLE_COUNT = 2437

    @staticmethod
    def parse(predictions: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        count = len(predictions)
        if count == 0:
            return {"sample_count": 0, "top1_accuracy": 0.0, "top3_accuracy": 0.0, "brier_score": 1.0}

        top1_correct = 0
        top3_correct = 0
        brier_sum = 0.0

        for p in predictions:
            target = p.get("target_model")
            pred_top1 = p.get("pred_model")
            pred_top3 = p.get("top3_candidates", [pred_top1])
            confidence = float(p.get("confidence", 0.5))

            if pred_top1 == target:
                top1_correct += 1
            if target in pred_top3:
                top3_correct += 1

            y = 1.0 if (pred_top1 == target) else 0.0
            brier_sum += (confidence - y) ** 2

        return {
            "sample_count": count,
            "expected_sample_count": KevFixedValParser.EXPECTED_SAMPLE_COUNT,
            "count_matches_expected": (count == KevFixedValParser.EXPECTED_SAMPLE_COUNT),
            "top1_accuracy": round(top1_correct / count, 4),
            "top3_accuracy": round(top3_correct / count, 4),
            "brier_score": round(brier_sum / count, 4),
        }
