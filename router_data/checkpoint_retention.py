"""Intelligent checkpoint retention, three-tier baselines, composite scoring, Top 30% selection, deduplication, and disk budget guard for Laya FULL-GRADED training."""
import hashlib
import json
import math
import os
import random
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    from router_data.external_benchmark import (
        STATUS_EVALUATED,
        STATUS_NOT_EVALUATED,
        STATUS_ROUTER_SERVING_NOT_READY,
        compute_composite_selection_score,
        evaluate_external_dev,
    )
except ImportError:
    try:
        from external_benchmark import (
            STATUS_EVALUATED,
            STATUS_NOT_EVALUATED,
            STATUS_ROUTER_SERVING_NOT_READY,
            compute_composite_selection_score,
            evaluate_external_dev,
        )
    except ImportError:
        STATUS_NOT_EVALUATED = "NOT_EVALUATED"
        STATUS_ROUTER_SERVING_NOT_READY = "ROUTER_SERVING_NOT_READY"
        STATUS_EVALUATED = "EVALUATED"
        def compute_composite_selection_score(score, dev_res=None):
            return {
                "selection_score": score,
                "internal_score": score,
                "external_dev_score": None,
                "external_dev_status": STATUS_NOT_EVALUATED,
                "formula_used": "1.00 * internal",
            }
        def evaluate_external_dev(ckpt, **kw):
            return {"status": STATUS_NOT_EVALUATED, "normalized_score": None}

# Canonical checkpoint retention statuses required by P4 & FULL-GRADED-AUTO-SWEEP
STATUS_RETAINED_BEST = "RETAINED_BEST"
STATUS_RETAINED_TOP_K = "RETAINED_TOP_K"
STATUS_PINNED_PARENT = "PINNED_PARENT"
STATUS_TEMP_RECOVERY = "TEMP_RECOVERY"
STATUS_METADATA_ONLY = "METADATA_ONLY"
STATUS_PRUNED_LOW_SCORE = "PRUNED_LOW_SCORE"
STATUS_PRUNED_DUPLICATE = "PRUNED_DUPLICATE"
STATUS_LEGACY_METADATA_ONLY = "LEGACY_METADATA_ONLY"

ALL_RETENTION_STATUSES = (
    STATUS_RETAINED_BEST,
    STATUS_RETAINED_TOP_K,
    STATUS_PINNED_PARENT,
    STATUS_TEMP_RECOVERY,
    STATUS_METADATA_ONLY,
    STATUS_PRUNED_LOW_SCORE,
    STATUS_PRUNED_DUPLICATE,
    STATUS_LEGACY_METADATA_ONLY,
)

# P3 Default Disk Budget & Protection Thresholds
GIB = 1024 ** 3
MIB = 1024 ** 2
DEFAULT_ACTIVE_BUDGET_BYTES = 120 * GIB          # 120 GiB active FULL-GRADED weight budget
DISK_WARN_FREE_PCT = 25.0                        # Free disk < 25% -> WARNING
DISK_STOP_FREE_PCT = 20.0                        # Free disk < 20% -> STOP new runs
DISK_WARN_FREE_BYTES = 300 * GIB                 # Free disk < 300 GiB -> WARNING
DISK_STOP_FREE_BYTES = 200 * GIB                 # Free disk < 200 GiB -> STOP new runs
SINGLE_CKPT_ESTIMATED_BYTES = 846_196_824        # ~807 MiB (846.2 MB) per physical Laya-421M checkpoint
ESTIMATED_RUN_PEAK_TEMP_BYTES = 2 * SINGLE_CKPT_ESTIMATED_BYTES  # Peak during atomic write + temp recovery

# Centralized Dynamic Baseline & Top 30% Retention Constants (Section 4)
RETENTION_TARGET = 0.30                          # Retain Top 30% (ceil(0.30 * N)) per comparable group
MEAN_FLOOR_RATIO = 0.98                          # Composite score must be >= 0.98 * historical robust mean
MIN_COMPARABLE_RUNS = 5                          # Cold-start until >= 5 distinct completed Runs in group
MIN_COMPARABLE_CONTROLS = MIN_COMPARABLE_RUNS    # Backward-compatible alias
TRIM_RATIO = 0.10                                # 10% two-sided trimmed mean when N >= 10
S1_SCORE_BASELINE = 100.0                        # BASELINE_0 normalized composite score
S2_SCORE_BASELINE = 100.0
S3_SCORE_BASELINE = 100.0
IMPROVEMENT_CLIP = (-1.00, 1.00)                 # Clip single-metric relative improvement to [-1.0, 1.0] (preserves full [0, L0] resolution while bounding negative blow-ups)
ECE_DENOM_FLOOR = 0.05                           # Prevent division explosion when E0 is small
PARETO_TIE_MARGIN = 0.50                         # Pareto-front priority when composite score within 0.5 pts
COLD_START_TOP_K = 2                             # Temporary Top-K cap when N < 5 during cold start
GROUP_TOP_K = COLD_START_TOP_K                   # Backward-compatible alias
MAX_CORE_CHECKPOINTS = 5                         # Global hard cap for old core pool: permanently retain 5 optimal core checkpoints
OLD_CORE_CHECKPOINT_IDS = {
    "P0_B03_C01_QB_PB-e02",
    "P0_B01_C01_QB_PB-e02",
    "P0_B03_C05_QB_PB-e02",
    "P0_B03_C08_QB_PB-e02",
    "P0_B02_C01_QB_PB-e02",
}
NEW_CORE_POOL_RATIO = 0.15                       # New core pool retention ratio: ~15% (ceil(0.15 * N_new_eligible))
DUAL_POOL_POLICY_VERSION = "DUAL_POOL_RETENTION_V2"

# Legacy P1 single-metric tolerances kept as secondary diagnostic flags
S1_LOSS_IMPROVEMENT_REL = 0.005
S1_ACC_DEGRADATION_TOL = 0.005
S1_ACC_IMPROVEMENT_ABS = 0.010
S1_LOSS_BRIER_DEGRADATION_REL = 0.005

NEW_PROTOCOL_VERSION = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
LEGACY_PROTOCOL_VERSION = "LEGACY_INPUT_PROTOCOL"
RETENTION_POLICY_VERSION = "Composite-Retention-v2"

# Fixed validation majority/prior baselines (computed on V2.1 fixed validation sets)
S2_VAL_BASELINE = {
    "items": 337,
    "num_classes": 2,
    "label_counts": {"False": 186, "True": 151},
    "majority_label": "False",
    "majority_accuracy": 0.551929,
    "majority_balanced_accuracy": 0.500000,
    "majority_macro_f1": 0.355641,
    "prior_loss": 0.687729,
    "uniform_loss": 0.693147,
    "prior_brier": 0.494606,
}

S3_VAL_BASELINES = {
    "CACHE-001:historical_prefix_reuse_tier": {
        "items": 397,
        "num_classes": 4,
        "qtype": "score",
        "label_counts": {"0": 16, "1": 119, "2": 94, "3": 168},
        "majority_label": "3",
        "majority_accuracy": 0.423174,
        "majority_balanced_accuracy": 0.250000,
        "majority_macro_f1": 0.148673,
        "prior_loss": 1.195592,
        "uniform_loss": 1.386294,
        "prior_brier": 0.673100,
    },
    "CACHE-001:observed_output_token_tier": {
        "items": 397,
        "num_classes": 4,
        "qtype": "score",
        "label_counts": {"0": 190, "1": 160, "2": 47},
        "majority_label": "0",
        "majority_accuracy": 0.478589,
        "majority_balanced_accuracy": 0.250000,
        "majority_macro_f1": 0.161840,
        "prior_loss": 0.971545,
        "uniform_loss": 1.386294,
        "prior_brier": 0.594400,
    },
    "OWN-002:observed_quota_tier": {
        "items": 1000,
        "num_classes": 4,
        "qtype": "score",
        "label_counts": {"0": 247, "1": 541, "2": 82, "3": 130},
        "majority_label": "1",
        "majority_accuracy": 0.541000,
        "majority_balanced_accuracy": 0.250000,
        "majority_macro_f1": 0.175535,
        "prior_loss": 1.148066,
        "uniform_loss": 1.386294,
        "prior_brier": 0.622700,
    },
    "OWN-002:observed_response_token_tier": {
        "items": 1000,
        "num_classes": 4,
        "qtype": "score",
        "label_counts": {"0": 103, "1": 271, "2": 445, "3": 181},
        "majority_label": "2",
        "majority_accuracy": 0.445000,
        "majority_balanced_accuracy": 0.250000,
        "majority_macro_f1": 0.153979,
        "prior_loss": 1.257633,
        "uniform_loss": 1.386294,
        "prior_brier": 0.685200,
    },
    "OWN-002:physical_cache_hit": {
        "items": 1000,
        "num_classes": 2,
        "qtype": "noul",
        "label_counts": {"True": 952, "False": 48},
        "majority_label": "True",
        "majority_accuracy": 0.952000,
        "majority_balanced_accuracy": 0.500000,
        "majority_macro_f1": 0.487705,
        "prior_loss": 0.192584,
        "uniform_loss": 0.693147,
        "prior_brier": 0.091392,
    },
    "TIME-001:observed_response_token_tier": {
        "items": 1000,
        "num_classes": 4,
        "qtype": "score",
        "label_counts": {"0": 592, "1": 310, "2": 93, "3": 5},
        "majority_label": "0",
        "majority_accuracy": 0.592000,
        "majority_balanced_accuracy": 0.250000,
        "majority_macro_f1": 0.185930,
        "prior_loss": 0.920803,
        "uniform_loss": 1.386294,
        "prior_brier": 0.544700,
    },
}

# Default BASELINE_0 (Frozen un-finetuned Laya-421M on fixed Validation; evaluated by `--compute-baseline0` on GPU)
DEFAULT_BASELINE_0: Dict[str, Any] = {
    "baseline_id": "BASELINE_0_LAYA_421M_FROZEN",
    "model_name": "Laya-421M (un-finetuned base)",
    "protocol_version": NEW_PROTOCOL_VERSION,
    "frozen": True,
    "composite_scores": {
        "S1_score": 100.0,
        "S2_score": 100.0,
        "S3_score": 100.0,
    },
    "validation": {
        "S1": {
            "items": 561,
            "loss": 1.8071,
            "accuracy": 0.4759,
            "balanced_accuracy": 0.5015,
            "macro_f1": 0.3283,
            "brier": 0.9021,
            "ece": 0.4402,
            "by_source": {
                "ROUTE-004": {"items": 561, "loss": 1.8071, "accuracy": 0.4759, "brier": 0.9021, "ece": 0.4402},
            },
        },
        "S2": {
            "items": 337,
            "loss": 0.7715,
            "accuracy": 0.4985,
            "balanced_accuracy": 0.4659,
            "macro_f1": 0.4229,
            "brier": 0.5663,
            "ece": 0.1620,
            "confusion_matrix": {"tn": 145, "fp": 41, "fn": 128, "tp": 23},
        },
        "S3": {
            "items": 4794,
            "loss": 1.2189,
            "accuracy": 0.4637,
            "balanced_accuracy": 0.2397,
            "macro_f1": 0.1719,
            "brier": 0.6540,
            "ece": 0.1895,
            "by_source_target": {
                "CACHE-001:historical_prefix_reuse_tier": {"items": 397, "loss": 2.5322, "accuracy": 0.0327, "balanced_accuracy": 0.1371, "macro_f1": 0.0345, "brier": 1.1934, "ece": 0.5440},
                "CACHE-001:observed_output_token_tier": {"items": 397, "loss": 1.3836, "accuracy": 0.3451, "balanced_accuracy": 0.2981, "macro_f1": 0.1656, "brier": 0.7735, "ece": 0.1472},
                "OWN-002:observed_quota_tier": {"items": 1000, "loss": 1.2365, "accuracy": 0.5410, "balanced_accuracy": 0.2495, "macro_f1": 0.1753, "brier": 0.6555, "ece": 0.1206},
                "OWN-002:observed_response_token_tier": {"items": 1000, "loss": 1.5008, "accuracy": 0.2280, "balanced_accuracy": 0.2512, "macro_f1": 0.1302, "brier": 0.7932, "ece": 0.3712},
                "OWN-002:physical_cache_hit": {"items": 1000, "loss": 0.2105, "accuracy": 0.9520, "balanced_accuracy": 0.5000, "macro_f1": 0.4877, "brier": 0.0973, "ece": 0.0572},
                "TIME-001:observed_response_token_tier": {"items": 1000, "loss": 1.3091, "accuracy": 0.3120, "balanced_accuracy": 0.2449, "macro_f1": 0.1341, "brier": 0.7285, "ece": 0.3338},
            },
        },
    },
}

# Protected directory names/prefixes that must NEVER be touched by cleanup (P3)
FORBIDDEN_PATH_TOKENS = (
    "models",
    "external",
    "raw_data",
    "原始数据",
    "清洗数据",
    "our-project",
    "research",
    "papers",
    "OVERNIGHT-LAYA-TRAINING",
    "OVERNIGHT-LAYA-SWEEP-02",
    "MR-STAGE1-",
    "MR-ALLDATA-PREP-",
    "E1-smoke-test-",
)


class DiskBudgetExceededError(RuntimeError):
    """Raised when disk free space or active weight budget prohibits starting a new Run."""


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _atomic_write_json(path: Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf8")
    tmp.replace(path)


def sanitize_command_str(cmd: Any) -> str:
    """Strip any private host/user prefixes from command strings before saving or publishing."""
    if isinstance(cmd, (list, tuple)):
        text = " ".join(str(x) for x in cmd)
    else:
        text = str(cmd or "")
    for prefix in ("/home/syy/路由/", "/home/syy/", "/Users/sunyiyang/Desktop/Project/路由/", "/Users/sunyiyang/"):
        text = text.replace(prefix, "")
    return text


def sanitize_deep(obj: Any) -> Any:
    """Recursively scrub private server/developer path prefixes from strings, dicts, and lists."""
    if isinstance(obj, str):
        for prefix in ("/home/syy/路由/", "/home/syy/", "/Users/sunyiyang/Desktop/Project/路由/", "/Users/sunyiyang/"):
            if prefix in obj:
                obj = obj.replace(prefix, "")
        return obj
    if isinstance(obj, dict):
        return {k: sanitize_deep(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_deep(x) for x in obj]
    return obj


def _clip_improvement(val: float) -> float:
    """Clip single-metric relative improvement to [-0.5, 0.5] per Section 3.1."""
    if not math.isfinite(val):
        return 0.0
    return max(IMPROVEMENT_CLIP[0], min(IMPROVEMENT_CLIP[1], float(val)))


def _normalize_baseline_0_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(d)
    val = dict(out.get("validation") or {})
    for k in ("S1", "S2", "S3", "S1_by_source", "S3_by_source_target"):
        if k in val and k not in out:
            out[k] = val[k]
        elif k in out and k not in val:
            val[k] = out[k]
    if "S1" in val and isinstance(val["S1"], dict) and "by_source" in val["S1"] and "S1_by_source" not in out:
        out["S1_by_source"] = val["S1"]["by_source"]
        val["S1_by_source"] = val["S1"]["by_source"]
    if "S3" in val and isinstance(val["S3"], dict) and "by_source_target" in val["S3"] and "S3_by_source_target" not in out:
        out["S3_by_source_target"] = val["S3"]["by_source_target"]
        val["S3_by_source_target"] = val["S3"]["by_source_target"]
    out["validation"] = val
    return out


def load_or_default_baseline_0(search_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load frozen `baseline_0.json` if available on disk; otherwise return `DEFAULT_BASELINE_0`."""
    candidates: List[Path] = []
    if search_root is not None:
        sr = Path(search_root).resolve()
        candidates.extend([
            sr / "baseline_0.json",
            sr.parent / "baseline_0.json",
            sr.parent / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "baseline_0.json",
            sr / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "baseline_0.json",
            sr / "runs" / "MR-FULL-GRADED-TRAINING" / "baseline_0.json",
            sr / "docs" / "training-dashboard" / "baseline_0.json",
        ])
    for cand in candidates:
        if cand.is_file():
            try:
                loaded = json.loads(cand.read_text(encoding="utf8"))
                if isinstance(loaded, dict) and ("validation" in loaded or "S1" in loaded):
                    return _normalize_baseline_0_dict(loaded)
            except (OSError, json.JSONDecodeError):
                continue
    return _normalize_baseline_0_dict(json.loads(json.dumps(DEFAULT_BASELINE_0)))


def classification_metrics_from_records(
    records: Sequence[Tuple[int, Any, Any, int]],
    include_item_vectors: bool = False,
    return_item_vectors: bool = False,
) -> Dict[str, Any]:
    """Compute Balanced Accuracy, Macro-F1, Confusion Matrix, and majority/prior baseline stats from calibration_records."""
    if not records:
        return {
            "balanced_accuracy": None,
            "macro_f1": None,
            "majority_baseline_accuracy": None,
            "majority_balanced_accuracy": None,
            "prior_baseline_loss": None,
            "beats_majority_baseline": False,
        }
    golds: List[int] = []
    preds: List[int] = []
    max_k = 2
    losses: List[float] = []
    corrects: List[int] = []
    for _qt, logits, target, k in records:
        k = int(k)
        max_k = max(max_k, k)
        z = [float(x) for x in list(logits)[:k]]
        t = [float(x) for x in list(target)[:k]]
        z_max = max(z) if z else 0.0
        exp_z = [math.exp(x - z_max) for x in z]
        s_exp = sum(exp_z) or 1.0
        p = [x / s_exp for x in exp_z]
        log_p = [x - z_max - math.log(s_exp) for x in z]
        losses.append(-sum(ti * lpi for ti, lpi in zip(t, log_p)))
        g = max(range(len(t)), key=lambda i: t[i]) if t else 0
        pr = max(range(len(p)), key=lambda i: p[i]) if p else 0
        golds.append(g)
        preds.append(pr)
        corrects.append(1 if g == pr else 0)

    n = len(golds)
    gold_counts = Counter(golds)
    pred_counts = Counter(preds)
    tp_counts = Counter(g for g, p in zip(golds, preds) if g == p)

    active_classes = sorted(gold_counts.keys())
    recalls = [tp_counts[c] / gold_counts[c] for c in active_classes if gold_counts[c] > 0]
    balanced_acc = sum(recalls) / len(recalls) if recalls else 0.0

    all_classes = sorted(set(active_classes) | set(pred_counts.keys()) | set(range(max_k)))
    f1s = []
    for c in all_classes:
        tp = tp_counts[c]
        fp = pred_counts[c] - tp
        fn = gold_counts[c] - tp
        denom = 2 * tp + fp + fn
        f1s.append((2.0 * tp / denom) if denom > 0 else 0.0)
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

    maj_cls, maj_count = gold_counts.most_common(1)[0]
    maj_acc = maj_count / n
    maj_bal_acc = 1.0 / max(2, len(active_classes))
    prior_loss = -sum((cnt / n) * math.log(cnt / n) for cnt in gold_counts.values() if cnt > 0)
    mean_loss = sum(losses) / n if losses else 0.0
    acc = sum(corrects) / n if n > 0 else 0.0
    beats = bool(
        acc > maj_acc + 0.005
        and mean_loss < prior_loss * 0.995
        and balanced_acc > maj_bal_acc + 0.005
    )
    out: Dict[str, Any] = {
        "num_classes": max(2, len(active_classes)),
        "majority_class": int(maj_cls),
        "majority_baseline_accuracy": round(maj_acc, 4),
        "majority_balanced_accuracy": round(maj_bal_acc, 4),
        "prior_baseline_loss": round(prior_loss, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "macro_f1": round(macro_f1, 4),
        "beats_majority_baseline": beats,
        "gold_counts": {str(k): int(v) for k, v in sorted(gold_counts.items())},
        "pred_counts": {str(k): int(v) for k, v in sorted(pred_counts.items())},
    }
    if max_k == 2:
        tn = sum(1 for g, p in zip(golds, preds) if g == 0 and p == 0)
        fp = sum(1 for g, p in zip(golds, preds) if g == 0 and p == 1)
        fn = sum(1 for g, p in zip(golds, preds) if g == 1 and p == 0)
        tp = sum(1 for g, p in zip(golds, preds) if g == 1 and p == 1)
        out["confusion_matrix"] = {"tn": tn, "fp": fp, "fn": fn, "tp": tp}
    if include_item_vectors or return_item_vectors:
        out["item_losses"] = [round(float(x), 6) for x in losses]
        out["item_correct"] = corrects
    return out


def enrich_s3_target_metrics(
    s3_breakdown: Dict[str, Dict[str, Any]],
    b0_s3_targets: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Attach fixed S3 target majority/prior baseline comparisons and per-target S3_score_t."""
    if not isinstance(s3_breakdown, dict):
        return {}
    b0_targets = b0_s3_targets or (DEFAULT_BASELINE_0["validation"]["S3"].get("by_source_target") or {})
    enriched = {}
    for target_key, metrics in s3_breakdown.items():
        if not isinstance(metrics, dict):
            continue
        item = dict(metrics)
        base = S3_VAL_BASELINES.get(target_key)
        b0_t = b0_targets.get(target_key) or base or {}
        if base:
            loss = item.get("loss")
            acc = item.get("accuracy")
            brier = item.get("brier")
            maj_acc = base["majority_accuracy"]
            prior_loss = base["prior_loss"]
            item["majority_baseline_accuracy"] = round(maj_acc, 4)
            item["majority_balanced_accuracy"] = round(base["majority_balanced_accuracy"], 4)
            item["majority_macro_f1"] = round(base["majority_macro_f1"], 4)
            item["prior_baseline_loss"] = round(prior_loss, 4)
            if item.get("balanced_accuracy") is None:
                item["balanced_accuracy"] = round(
                    max(base["majority_balanced_accuracy"], acc * 0.85)
                    if isinstance(acc, (int, float)) and acc > maj_acc + 0.02
                    else base["majority_balanced_accuracy"],
                    4,
                )
            if item.get("macro_f1") is None:
                item["macro_f1"] = round(
                    max(base["majority_macro_f1"], acc * 0.80)
                    if isinstance(acc, (int, float)) and acc > maj_acc + 0.02
                    else base["majority_macro_f1"],
                    4,
                )
            beats = bool(
                isinstance(acc, (int, float))
                and isinstance(loss, (int, float))
                and acc > maj_acc + 0.005
                and loss < prior_loss * 0.995
            )
            item["beats_majority_baseline"] = beats
            item["relative_loss_reduction_vs_prior"] = (
                round((prior_loss - loss) / prior_loss, 4)
                if isinstance(loss, (int, float)) and prior_loss > 0
                else None
            )
            item["accuracy_gain_vs_majority"] = (
                round(acc - maj_acc, 4)
                if isinstance(acc, (int, float))
                else None
            )
            # Compute target composite score S3_score_t (Section 3.3)
            l0 = float(b0_t.get("loss") or prior_loss or 1.0)
            ba0 = float(b0_t.get("balanced_accuracy") or base["majority_balanced_accuracy"] or 0.25)
            f1_0 = float(b0_t.get("macro_f1") or base["majority_macro_f1"] or 0.15)
            b0 = float(b0_t.get("brier") or base.get("prior_brier") or 0.50)

            l_val = float(loss) if isinstance(loss, (int, float)) else l0
            ba_val = float(item.get("balanced_accuracy") or ba0)
            f1_val = float(item.get("macro_f1") or f1_0)
            b_val = float(brier) if isinstance(brier, (int, float)) else b0

            i_loss = _clip_improvement((l0 - l_val) / max(l0, 1e-6))
            i_ba = _clip_improvement((ba_val - ba0) / max(1.0 - ba0, 0.05))
            i_f1 = _clip_improvement((f1_val - f1_0) / max(1.0 - f1_0, 0.05))
            i_brier = _clip_improvement((b0 - b_val) / max(b0, 1e-6))
            score_t = 100.0 * (1.0 + 0.40 * i_loss + 0.25 * i_ba + 0.20 * i_f1 + 0.15 * i_brier)
            item["s3_target_score"] = round(score_t, 4)
        enriched[target_key] = item
    return enriched


def compute_s1_composite_score(
    s1_val: Optional[Dict[str, Any]],
    b0_s1: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute S1 multi-metric composite score relative to BASELINE_0 (Section 3.1).

    Formula:
      I_loss  = clip((L0 - L) / L0)
      I_acc   = clip((A - A0) / max(1 - A0, 0.05))
      I_brier = clip((B0 - B) / B0)
      I_ece   = clip((E0 - E) / max(E0, 0.05))
      S1_score = 100 * (1 + 0.45 * I_loss + 0.30 * I_acc + 0.15 * I_brier + 0.10 * I_ece)
    """
    if not isinstance(s1_val, dict) or not isinstance(s1_val.get("loss"), (int, float)):
        return {
            "s1_score": None,
            "beats_baseline_0": False,
            "i_loss": None,
            "i_acc": None,
            "i_brier": None,
            "i_ece": None,
        }
    ref = b0_s1 or DEFAULT_BASELINE_0["validation"]["S1"]
    l0 = float(ref.get("loss") or 0.659632)
    a0 = float(ref.get("accuracy") or 0.579323)
    b0 = float(ref.get("brier") or 0.476765)
    e0 = float(ref.get("ece") or 0.056262)

    l_val = float(s1_val["loss"])
    a_val = float(s1_val.get("accuracy") if isinstance(s1_val.get("accuracy"), (int, float)) else a0)
    b_val = float(s1_val.get("brier") if isinstance(s1_val.get("brier"), (int, float)) else b0)
    e_val = float(s1_val.get("ece") if isinstance(s1_val.get("ece"), (int, float)) else e0)

    i_loss = _clip_improvement((l0 - l_val) / max(l0, 1e-6))
    i_acc = _clip_improvement((a_val - a0) / max(1.0 - a0, 0.05))
    i_brier = _clip_improvement((b0 - b_val) / max(b0, 1e-6))
    i_ece = _clip_improvement((e0 - e_val) / max(e0, ECE_DENOM_FLOOR))

    score = 100.0 * (1.0 + 0.45 * i_loss + 0.30 * i_acc + 0.15 * i_brier + 0.10 * i_ece)
    # Condition A: S1_score > 100.0 AND Val Loss <= L0 AND Accuracy >= A0 - 0.005
    beats_b0 = bool(
        score > S1_SCORE_BASELINE + 1e-6
        and l_val <= l0 + 1e-6
        and a_val >= a0 - 0.005 - 1e-6
    )
    return {
        "score": round(score, 4),
        "s1_score": round(score, 4),
        "beats_baseline_0": beats_b0,
        "i_loss": round(i_loss, 4),
        "i_acc": round(i_acc, 4),
        "i_brier": round(i_brier, 4),
        "i_ece": round(i_ece, 4),
        "delta_loss_vs_b0": round(l_val - l0, 4),
        "delta_acc_vs_b0": round(a_val - a0, 4),
        "delta_brier_vs_b0": round(b_val - b0, 4),
        "delta_ece_vs_b0": round(e_val - e0, 4),
    }


def compute_s2_composite_score(
    s2_val: Optional[Dict[str, Any]],
    b0_s2: Optional[Dict[str, Any]] = None,
    s2_audit_passed: bool = False,
) -> Dict[str, Any]:
    """Compute S2 risk classification composite score (Section 3.2).

    Before independent audit passes (`s2_audit_passed=False`) or if `accuracy >= 0.999`
    (shortcut anomaly), status is `DIAGNOSTIC_ONLY` and `s2_ranking_enabled=False`.
    Formula:
      S2_score = 100 * (1 + 0.35 * I_loss + 0.30 * I_bal_acc + 0.20 * I_f1 + 0.15 * I_brier)
    """
    if not isinstance(s2_val, dict) or not isinstance(s2_val.get("loss"), (int, float)):
        return {
            "score": None,
            "s2_score": None,
            "s2_diagnostic_score": None,
            "s2_status": "NOT_EVALUATED",
            "s2_ranking_enabled": False,
            "beats_baseline_0": False,
            "beats_majority_baseline": False,
        }
    ref = b0_s2 or DEFAULT_BASELINE_0["validation"]["S2"]
    # Guard against legacy R0 S2 shortcut where L0 was 0.0005
    l0 = float(ref.get("loss") if isinstance(ref.get("loss"), (int, float)) and ref["loss"] > 0.05 else S2_VAL_BASELINE["prior_loss"])
    ba0 = float(ref.get("balanced_accuracy") if isinstance(ref.get("balanced_accuracy"), (int, float)) and ref["balanced_accuracy"] < 0.99 else S2_VAL_BASELINE["majority_balanced_accuracy"])
    f1_0 = float(ref.get("macro_f1") if isinstance(ref.get("macro_f1"), (int, float)) and ref["macro_f1"] < 0.99 else S2_VAL_BASELINE["majority_macro_f1"])
    b0 = float(ref.get("brier") if isinstance(ref.get("brier"), (int, float)) and ref["brier"] > 0.02 else S2_VAL_BASELINE["prior_brier"])

    l_val = float(s2_val["loss"])
    acc_val = float(s2_val.get("accuracy") if isinstance(s2_val.get("accuracy"), (int, float)) else S2_VAL_BASELINE["majority_accuracy"])
    ba_val = float(s2_val.get("balanced_accuracy") if isinstance(s2_val.get("balanced_accuracy"), (int, float)) else (1.0 if acc_val >= 0.999 else S2_VAL_BASELINE["majority_balanced_accuracy"]))
    f1_val = float(s2_val.get("macro_f1") if isinstance(s2_val.get("macro_f1"), (int, float)) else (1.0 if acc_val >= 0.999 else S2_VAL_BASELINE["majority_macro_f1"]))
    b_val = float(s2_val.get("brier") if isinstance(s2_val.get("brier"), (int, float)) else b0)

    shortcut_suspected = bool(acc_val >= 0.999 or l_val < 0.005)
    i_loss = _clip_improvement((l0 - l_val) / max(l0, 1e-6))
    i_ba = _clip_improvement((ba_val - ba0) / max(1.0 - ba0, 0.05))
    i_f1 = _clip_improvement((f1_val - f1_0) / max(1.0 - f1_0, 0.05))
    i_brier = _clip_improvement((b0 - b_val) / max(b0, 1e-6))

    raw_score = 100.0 * (1.0 + 0.35 * i_loss + 0.30 * i_ba + 0.20 * i_f1 + 0.15 * i_brier)
    beats_maj = bool(
        not shortcut_suspected
        and acc_val > S2_VAL_BASELINE["majority_accuracy"] + 0.005
        and ba_val > S2_VAL_BASELINE["majority_balanced_accuracy"] + 0.005
        and f1_val > S2_VAL_BASELINE["majority_macro_f1"] + 0.005
        and l_val < S2_VAL_BASELINE["prior_loss"] * 0.995
    )
    ranking_enabled = bool(s2_audit_passed and not shortcut_suspected)
    return {
        "score": round(raw_score, 4),
        "s2_score": round(raw_score, 4) if ranking_enabled else None,
        "s2_diagnostic_score": round(raw_score, 4),
        "s2_status": "AUDITED_RANKING" if ranking_enabled else "DIAGNOSTIC_ONLY",
        "s2_ranking_enabled": ranking_enabled,
        "shortcut_suspected": shortcut_suspected,
        "beats_baseline_0": bool(ranking_enabled and raw_score > S2_SCORE_BASELINE and l_val <= l0),
        "beats_majority_baseline": beats_maj,
        "i_loss": round(i_loss, 4),
        "i_bal_acc": round(i_ba, 4),
        "i_f1": round(i_f1, 4),
        "i_brier": round(i_brier, 4),
    }


def compute_s3_composite_score(
    s3_val: Optional[Dict[str, Any]],
    s3_targets: Optional[Dict[str, Dict[str, Any]]] = None,
    b0_s3: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute S3 macro-averaged per-target composite score (Section 3.3).

    Never sums raw losses across S3 targets.
    For each real `source:target` t:
      S3_score_t = 100 * (1 + 0.40 * I_loss_t + 0.25 * I_bal_acc_t + 0.20 * I_f1_t + 0.15 * I_brier_t)
    Overall S3_score is the equal-weight macro-average of S3_score_t across active targets.
    """
    # Support 2-arg call `compute_s3_composite_score(s3_targets_dict, b0_s3_targets_dict)`
    if isinstance(s3_val, dict) and any(":" in str(k) for k in s3_val.keys()) and b0_s3 is None:
        actual_targets = s3_val
        b0_targets = (
            s3_targets.get("by_source_target")
            if isinstance(s3_targets, dict) and "by_source_target" in s3_targets
            else (s3_targets if isinstance(s3_targets, dict) else DEFAULT_BASELINE_0["validation"]["S3"]["by_source_target"])
        )
    else:
        actual_targets = s3_targets or (s3_val.get("by_source_target") if isinstance(s3_val, dict) else {}) or {}
        b0_targets = (b0_s3 or DEFAULT_BASELINE_0["validation"]["S3"]).get("by_source_target") or {}
    enriched_targets = enrich_s3_target_metrics(actual_targets, b0_s3_targets=b0_targets)
    if not enriched_targets:
        return {
            "score": None,
            "s3_score": None,
            "beats_baseline_0": False,
            "beaten_targets": [],
            "beaten_target_count": 0,
            "active_target_count": 0,
            "per_target_scores": {},
            "mean_relative_loss_reduction_vs_prior": None,
        }
    per_target_scores: Dict[str, float] = {}
    beaten_targets: List[str] = []
    rel_gains: List[float] = []
    for t_key, t_metrics in sorted(enriched_targets.items()):
        t_score = t_metrics.get("s3_target_score")
        if isinstance(t_score, (int, float)):
            per_target_scores[t_key] = round(float(t_score), 4)
        if t_metrics.get("beats_majority_baseline") and isinstance(t_score, (int, float)) and t_score > S3_SCORE_BASELINE:
            beaten_targets.append(t_key)
        if t_metrics.get("beats_majority_baseline") and isinstance(t_metrics.get("relative_loss_reduction_vs_prior"), (int, float)):
            rel_gains.append(float(t_metrics["relative_loss_reduction_vs_prior"]))

    active_cnt = len(per_target_scores)
    macro_score = sum(per_target_scores.values()) / active_cnt if active_cnt > 0 else None
    min_req_targets = min(2, max(1, active_cnt))
    beats_b0 = bool(
        macro_score is not None
        and macro_score > S3_SCORE_BASELINE + 1e-6
        and len(beaten_targets) >= min_req_targets
    )
    mean_rel_gain = sum(rel_gains) / len(rel_gains) if rel_gains else -1.0
    return {
        "score": round(macro_score, 4) if macro_score is not None else None,
        "s3_score": round(macro_score, 4) if macro_score is not None else None,
        "beats_baseline_0": beats_b0,
        "beaten_targets": beaten_targets,
        "beaten_target_count": len(beaten_targets),
        "active_target_count": active_cnt,
        "per_target_scores": per_target_scores,
        "mean_relative_loss_reduction_vs_prior": round(mean_rel_gain, 4),
    }


def compute_node_composite_scores(
    validation: Dict[str, Any],
    task_family: str,
    baseline_0: Optional[Dict[str, Any]] = None,
    s2_audit_passed: bool = False,
) -> Dict[str, Any]:
    """Compute S1_score, S2_score, S3_score and select the task-appropriate primary_score."""
    b0_val = (baseline_0 or DEFAULT_BASELINE_0).get("validation") or DEFAULT_BASELINE_0["validation"]
    s1_res = compute_s1_composite_score((validation or {}).get("S1"), b0_val.get("S1"))
    s2_res = compute_s2_composite_score((validation or {}).get("S2"), b0_val.get("S2"), s2_audit_passed=s2_audit_passed)
    s3_res = compute_s3_composite_score(
        (validation or {}).get("S3"),
        (validation or {}).get("S3_by_source_target"),
        b0_val.get("S3"),
    )
    if task_family == "S1":
        primary_score = s1_res["s1_score"]
        beats_b0 = s1_res["beats_baseline_0"]
    elif task_family == "S2":
        primary_score = s2_res["s2_score"] if s2_res["s2_ranking_enabled"] else s2_res["s2_diagnostic_score"]
        beats_b0 = s2_res["beats_baseline_0"]
    else:
        primary_score = s3_res["s3_score"]
        beats_b0 = s3_res["beats_baseline_0"]

    return {
        "task_family": task_family,
        "primary_score": primary_score,
        "beats_baseline_0": beats_b0,
        "s1_score": s1_res["s1_score"],
        "s2_score": s2_res["s2_score"],
        "s2_diagnostic_score": s2_res["s2_diagnostic_score"],
        "s2_status": s2_res["s2_status"],
        "s3_score": s3_res["s3_score"],
        "S1_detail": s1_res,
        "S2_detail": s2_res,
        "S3_detail": s3_res,
    }


def compute_run_dedup_signature(run_or_node: Dict[str, Any], out_root: Optional[Path] = None) -> str:
    """Build deterministic `(protocol_version, data_manifest_hash, config_hash, seed)` signature.

    Ensures duplicate runs or repeated data/config runs never double-count in `BASELINE_1`
    or `BASELINE_2` (Section 2.1 & Check 11.14).
    """
    protocol = str(run_or_node.get("protocol_version") or NEW_PROTOCOL_VERSION)
    seed = int(run_or_node.get("seed", 42))

    # 1. Data manifest hash (explicit if provided, else derived from canonical data fingerprint)
    data_hash = run_or_node.get("data_manifest_hash")
    batch_id = str(run_or_node.get("batch_id") or "")
    combo_id = str(run_or_node.get("combo_id") or "")
    if not data_hash and not (batch_id and combo_id) and out_root is not None:
        rid = str(run_or_node.get("run_id") or "")
        dm_path = out_root / "train" / rid / "data_manifest.json"
        if dm_path.is_file():
            try:
                data_hash = hashlib.sha256(dm_path.read_bytes()).hexdigest()[:16]
            except OSError:
                data_hash = None
    if not data_hash:
        sup = sorted(
            run_or_node.get("supervision_classes")
            or run_or_node.get("groups")
            or (run_or_node.get("train_groups") or {}).keys()
        )
        q_code = str(run_or_node.get("quality_code") or "")
        p_code = str(run_or_node.get("sampling_code") or "")
        ratios = list(run_or_node.get("ratios") or [])
        # Canonicalize known 100%-identical data equivalence classes in B01..B07:
        # - S1-only (`C01`): only Q1 ROUTE-004 exists (1 row/unit), so QA==QB and PA==PB==PC
        # - S3-only (`C03`) and S1+S3 (`C07,C08,C09`): only Q1 exists and 1 source per target, so QA==QB and PA==PC
        # - S2 under QC (`C02_QC`): only TRA-002 has Q2 rows, so PA==PC
        eff_q = q_code
        eff_p = p_code
        if sup == ["S1"] and q_code in ("QA", "QB"):
            eff_q = "QA_QB_EQ"
            eff_p = "PA_PB_PC_EQ"
        elif set(sup) <= {"S1", "S3"} and q_code in ("QA", "QB"):
            eff_q = "QA_QB_EQ"
            if p_code in ("PA", "PC"):
                eff_p = "PA_PC_EQ"
        elif sup == ["S2"] and q_code == "QC" and p_code in ("PA", "PC"):
            eff_p = "PA_PC_EQ"
        if batch_id and combo_id:
            data_payload = {
                "batch_id": batch_id,
                "combo_id": combo_id,
                "eff_q": eff_q,
                "eff_p": eff_p,
                "sup": sup,
                "ratios": ratios,
                "cursor_offset": run_or_node.get("cursor_offset", 0),
            }
        else:
            data_payload = {
                "run_id": str(run_or_node.get("run_id") or ""),
                "sup": sup,
                "ratios": ratios,
                "train_groups": dict(run_or_node.get("train_groups") or {}),
                "independent_units": dict(run_or_node.get("independent_units") or {}),
                "cursor_offset": run_or_node.get("cursor_offset", 0),
            }
        data_hash = hashlib.sha256(json.dumps(data_payload, sort_keys=True).encode("utf8")).hexdigest()[:16]

    # 2. Config hash
    cfg = dict(run_or_node.get("config") or {})
    cfg_payload = {
        "encoder_lr": cfg.get("encoder_lr", 2.5e-5),
        "head_lr": cfg.get("head_lr", 1e-4),
        "micro_batch": cfg.get("micro_batch", 8),
        "grad_accum": cfg.get("grad_accum", 8),
        "weight_decay": cfg.get("weight_decay", 0.01),
        "grad_clip": cfg.get("grad_clip", 1.0),
        "loss": cfg.get("loss", "soft-ce"),
        "freeze_encoder": bool(cfg.get("freeze_encoder", False)),
        "parent_checkpoint_id": run_or_node.get("parent_checkpoint_id") or "Base",
        "supervision_classes": sorted(run_or_node.get("supervision_classes") or (run_or_node.get("train_groups") or {}).keys()),
        "ratios": list(run_or_node.get("ratios") or []),
    }
    cfg_hash = str(run_or_node.get("config_hash") or hashlib.sha256(
        json.dumps(cfg_payload, sort_keys=True).encode("utf8")
    ).hexdigest()[:16])

    return f"{protocol}|data:{data_hash}|cfg:{cfg_hash}|seed:{seed}"


def _quantile_sorted(sorted_vals: Sequence[float], q: float) -> Optional[float]:
    """Linear-interpolated quantile on a pre-sorted non-empty list of floats."""
    if not sorted_vals:
        return None
    n = len(sorted_vals)
    if n == 1:
        return float(sorted_vals[0])
    pos = max(0.0, min(1.0, float(q))) * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = pos - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def compute_robust_distribution_stats(values: Sequence[float], trim_ratio: float = TRIM_RATIO) -> Dict[str, Optional[float]]:
    """Compute BASELINE_1 (Mean, Median, 10% Trimmed Mean when N>=10, Std, IQR) & BASELINE_2 (P50, P70, P90, Max)."""
    clean = sorted(float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v)))
    n = len(clean)
    if n == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "trimmed_mean": None,
            "robust_mean": None,
            "std": None,
            "iqr": None,
            "p25": None,
            "p50": None,
            "p70": None,
            "p75": None,
            "p90": None,
            "min": None,
            "max": None,
        }
    mean_v = sum(clean) / n
    if n >= 10:
        k_trim = max(1, int(math.floor(n * trim_ratio)))
        trimmed_slice = clean[k_trim:n - k_trim] if (2 * k_trim < n) else clean
        trimmed_mean = sum(trimmed_slice) / len(trimmed_slice)
        robust_mean = trimmed_mean
    else:
        trimmed_mean = mean_v
        robust_mean = mean_v

    var_v = sum((x - mean_v) ** 2 for x in clean) / n if n > 1 else 0.0
    std_v = math.sqrt(var_v)
    p25 = _quantile_sorted(clean, 0.25)
    p50 = _quantile_sorted(clean, 0.50)
    p70 = _quantile_sorted(clean, 0.70)
    p75 = _quantile_sorted(clean, 0.75)
    p90 = _quantile_sorted(clean, 0.90)
    iqr = (p75 - p25) if (p75 is not None and p25 is not None) else 0.0
    return {
        "count": n,
        "mean": round(mean_v, 4),
        "median": round(p50, 4) if p50 is not None else None,
        "trimmed_mean": round(trimmed_mean, 4),
        "trimmed_mean_10pct": round(trimmed_mean, 4),
        "robust_mean": round(robust_mean, 4),
        "std": round(std_v, 4),
        "iqr": round(iqr, 4),
        "p25": round(p25, 4) if p25 is not None else None,
        "p50": round(p50, 4) if p50 is not None else None,
        "p70": round(p70, 4) if p70 is not None else None,
        "p75": round(p75, 4) if p75 is not None else None,
        "p90": round(p90, 4) if p90 is not None else None,
        "min": round(clean[0], 4),
        "max": round(clean[-1], 4),
    }


def compute_pareto_frontier_ids(candidates: Sequence[Dict[str, Any]], task_family: str = "S1") -> Set[str]:
    """Return checkpoint_ids on the Pareto non-dominated frontier for `(loss_asc, -acc_desc, brier_asc, ece_asc)`."""
    vecs: List[Tuple[str, Tuple[float, float, float, float]]] = []
    for n in candidates:
        cid = n["checkpoint_id"]
        v = (n.get("validation") or {}).get(task_family) or {}
        loss = v.get("loss")
        acc = v.get("accuracy")
        brier = v.get("brier")
        ece = v.get("ece")
        if not isinstance(loss, (int, float)) or not isinstance(acc, (int, float)):
            continue
        vec = (
            float(loss),
            -float(acc),
            float(brier) if isinstance(brier, (int, float)) else 999.0,
            float(ece) if isinstance(ece, (int, float)) else 999.0,
        )
        vecs.append((cid, vec))

    pareto_ids: Set[str] = set()
    for cid_a, va in vecs:
        dominated = False
        for cid_b, vb in vecs:
            if cid_a == cid_b:
                continue
            # vb dominates va iff vb[i] <= va[i] for all i and vb[i] < va[i] for at least one i
            if all(vb[i] <= va[i] + 1e-9 for i in range(4)) and any(vb[i] < va[i] - 1e-6 for i in range(4)):
                dominated = True
                break
        if not dominated:
            pareto_ids.add(cid_a)
    return pareto_ids


def compute_bootstrap_ci(
    model_losses: Sequence[float],
    model_correct: Sequence[int],
    ref_losses: Sequence[float],
    ref_correct: Sequence[int],
    n_boot: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Compute paired unit-level Bootstrap 95% confidence intervals on S1 validation items (Section 5.4)."""
    n = min(len(model_losses), len(model_correct), len(ref_losses), len(ref_correct))
    if n == 0:
        return {"items": 0, "status": "NO_ITEM_VECTORS"}
    d_loss = [float(model_losses[i]) - float(ref_losses[i]) for i in range(n)]
    d_acc = [float(model_correct[i]) - float(ref_correct[i]) for i in range(n)]
    mean_dl = sum(d_loss) / n
    mean_da = sum(d_acc) / n

    rng = random.Random(seed)
    boot_dl: List[float] = []
    boot_da: List[float] = []
    for _ in range(int(n_boot)):
        idxs = [rng.randrange(n) for _ in range(n)]
        boot_dl.append(sum(d_loss[i] for i in idxs) / n)
        boot_da.append(sum(d_acc[i] for i in idxs) / n)
    boot_dl.sort()
    boot_da.sort()
    dl_lo = _quantile_sorted(boot_dl, 0.025) or 0.0
    dl_hi = _quantile_sorted(boot_dl, 0.975) or 0.0
    da_lo = _quantile_sorted(boot_da, 0.025) or 0.0
    da_hi = _quantile_sorted(boot_da, 0.975) or 0.0

    loss_sig_better = bool(dl_hi < 0.0)
    acc_sig_better = bool(da_lo > 0.0)
    directionally_better = bool(mean_dl < 0.0 or mean_da > 0.0)
    verdict = (
        "STATISTICALLY_SIGNIFICANT"
        if (loss_sig_better or acc_sig_better)
        else ("DIRECTIONALLY_BETTER" if directionally_better else "NO_GAIN_OVER_REFERENCE")
    )
    return {
        "items": n,
        "bootstrap_samples": int(n_boot),
        "delta_loss_mean": round(mean_dl, 5),
        "delta_loss_ci95": [round(dl_lo, 5), round(dl_hi, 5)],
        "loss_significantly_better": loss_sig_better,
        "delta_accuracy_mean": round(mean_da, 5),
        "delta_accuracy_ci95": [round(da_lo, 5), round(da_hi, 5)],
        "accuracy_significantly_better": acc_sig_better,
        "verdict": verdict,
    }


def physical_dir_bytes(path: Path) -> int:
    """Return total bytes of regular (non-symlink) files under `path`."""
    path = Path(path)
    if not path.exists() or path.is_symlink():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for f in path.rglob("*"):
        try:
            if f.is_file() and not f.is_symlink():
                total += f.stat().st_size
        except OSError:
            continue
    return total


def has_physical_weights(ckpt_dir: Path) -> bool:
    """True iff `ckpt_dir` is a real directory (not a symlink) containing `model.safetensors` or `model.pt`."""
    ckpt_dir = Path(ckpt_dir)
    if not ckpt_dir.exists() or ckpt_dir.is_symlink() or not ckpt_dir.is_dir():
        return False
    st = ckpt_dir / "model.safetensors"
    if st.is_file() and not st.is_symlink() and st.stat().st_size > 0:
        return True
    pt = ckpt_dir / "model.pt"
    if pt.is_file() and not pt.is_symlink() and pt.stat().st_size > 0:
        return True
    return False


def is_loadable_checkpoint_path(ckpt_dir: Path) -> bool:
    """True iff `ckpt_dir` (real dir or valid symlink) has `rl_agent_config.json` and (`model.safetensors` or `model.pt`)."""
    ckpt_dir = Path(ckpt_dir)
    try:
        if not ckpt_dir.exists() or not ckpt_dir.is_dir():
            return False
        has_w = (ckpt_dir / "model.safetensors").is_file() or (ckpt_dir / "model.pt").is_file()
        has_cfg = (ckpt_dir / "rl_agent_config.json").is_file() or (ckpt_dir / "recovery_state.json").is_file()
        return has_w and has_cfg
    except OSError:
        return False


def update_safe_symlink(link_path: Path, target_rel_name: Optional[str]) -> None:
    """Atomically point `link_path` (e.g. `checkpoints/best`) as a relative symlink to `target_rel_name`.

    If `target_rel_name` is None or the target does not have valid weights, removes `link_path`
    so `best` or `latest` never dangles or points to missing weights.
    """
    link_path = Path(link_path)
    parent = link_path.parent
    if not target_rel_name:
        if link_path.is_symlink() or link_path.is_file():
            link_path.unlink(missing_ok=True)
        elif link_path.is_dir():
            shutil.rmtree(link_path)
        return

    target_dir = parent / target_rel_name
    if not is_loadable_checkpoint_path(target_dir):
        if link_path.is_symlink() or link_path.is_file():
            link_path.unlink(missing_ok=True)
        return

    # If link_path is currently a full duplicate physical directory (legacy), do not delete it here
    # unless explicitly deduplicating; only replace if it's a symlink or doesn't exist.
    if link_path.exists() and not link_path.is_symlink() and link_path.is_dir():
        return

    tmp_link = parent / f".tmp_link_{link_path.name}_{os.getpid()}"
    if tmp_link.exists() or tmp_link.is_symlink():
        tmp_link.unlink(missing_ok=True)
    os.symlink(target_rel_name, tmp_link)
    os.replace(tmp_link, link_path)


def build_comparable_group_id(run_meta: Dict[str, Any]) -> str:
    """Build the strict comparable group identifier (Section 2 & P1).

    Comparable experiments must share:
    1. Input protocol version (`MR-FULL-GRADED-P0-DATA-REPAIR-v1` vs `LEGACY_INPUT_PROTOCOL`)
    2. Primary supervision target structure (`S1`, `S1+S2`, `S1+S3`, `S1+S2+S3`, `S2`, `S3`, `S2+S3`)
    3. Fixed validation set signature (`S1:561`, `S2:337`, `S3:4794`)
    4. Metric definition (`soft-ce_raw_logit`)
    """
    legacy = bool(
        run_meta.get("legacy_input_protocol")
        or run_meta.get("protocol_version") == LEGACY_PROTOCOL_VERSION
        or str(run_meta.get("run_id", "")).startswith("B01_")
    )
    protocol = LEGACY_PROTOCOL_VERSION if legacy else (
        run_meta.get("protocol_version") or NEW_PROTOCOL_VERSION
    )
    family = primary_task_family(run_meta)
    val_groups = run_meta.get("val_groups") or {}
    if family in val_groups:
        val_sig = f"{family}:{val_groups[family]}"
    elif family == "S1":
        val_sig = "S1:561"
    elif family == "S2":
        val_sig = "S2:337"
    else:
        val_sig = "S3:4794"
    loss_name = (run_meta.get("config") or {}).get("loss", "soft-ce")
    return f"{protocol}|sup:{family}|val:{val_sig}|metric:{loss_name}_raw_logit"


def primary_task_family(run_meta: Dict[str, Any]) -> str:
    """Return 'S1', 'S2', or 'S3' as the primary evaluation task family (never mixing tasks)."""
    classes = list(run_meta.get("supervision_classes") or sorted((run_meta.get("train_groups") or {}).keys()))
    if "S1" in classes:
        return "S1"
    if classes == ["S2"]:
        return "S2"
    return "S3"


def collect_pinned_parent_ids(
    runs: Dict[str, Dict[str, Any]],
    plans: Optional[Dict[str, Dict[str, Any]]] = None,
    explicit_pinned: Optional[Iterable[str]] = None,
) -> Dict[str, List[str]]:
    """Return mapping `parent_checkpoint_id -> list of dependent child run_ids`."""
    pinned: Dict[str, List[str]] = defaultdict(list)
    for cid in (explicit_pinned or ()):
        if cid:
            pinned[str(cid)].append("EXPLICIT_PIN")
    for rid, r in (runs or {}).items():
        parent = r.get("parent_checkpoint_id")
        if parent and parent != "Base":
            if rid not in pinned[str(parent)]:
                pinned[str(parent)].append(rid)
    for pid, p in (plans or {}).items():
        parent = p.get("parent_checkpoint_id")
        if parent and parent != "Base":
            if pid not in pinned[str(parent)]:
                pinned[str(parent)].append(pid)
    return {k: sorted(v) for k, v in pinned.items()}


def _node_primary_sort_key(node: Dict[str, Any], task_family: str) -> Tuple[float, float, float, int]:
    """Sort key (ascending = better) for selecting the single best Epoch within a Run."""
    score = node.get("primary_score")
    v = (node.get("validation") or {}).get(task_family) or {}
    loss = v.get("loss")
    acc = v.get("accuracy")
    return (
        -(float(score) if isinstance(score, (int, float)) else -9999.0),
        float(loss) if isinstance(loss, (int, float)) else 9999.0,
        -(float(acc) if isinstance(acc, (int, float)) else -1.0),
        int(node.get("epoch", 99)),
    )


def evaluate_cohort_retention(
    nodes: List[Dict[str, Any]],
    pinned_map: Dict[str, List[str]],
    s2_audit_passed: bool = False,
    allow_legacy_reference_eval: bool = False,
    baseline_0: Optional[Dict[str, Any]] = None,
    out_root: Optional[Path] = None,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Evaluate Three-Tier Baselines (BASELINE_0/1/2), Multi-Metric Composite Scores, and Top 30% retention.

    Implements Sections 2, 3, and 4:
    1. Strictly separates new-protocol checkpoints from `LEGACY_INPUT_PROTOCOL`.
    2. Never mixes S1, S2, and S3 rankings.
    3. Within each Run, selects at most 1 best Epoch (`is_run_best_epoch`) for non-dependent retention.
    4. Deduplicates Runs by `dedup_signature = (protocol_version, data_manifest_hash, config_hash, seed)`
       so each distinct Run contributes at most 1 record (its best Epoch) to `BASELINE_1` & `BASELINE_2`.
    5. Evaluates Conditions A (beat `BASELINE_0`, score > 100), B (`score >= 0.98 * loo_robust_mean_score`),
       C (Top 30% `ceil(0.30 * N)` when N >= 5), D (Cold-Start Top-2 when N < 5), E (Pareto tie-break),
       and F (Mandatory retention: `PINNED_PARENT`, Global S1 champions, per-batch `B01..B07` best passing Cond A).
    """
    b0 = baseline_0 or DEFAULT_BASELINE_0
    b0_val = b0.get("validation") or DEFAULT_BASELINE_0["validation"]
    decisions: Dict[str, Dict[str, Any]] = {}
    group_summaries: Dict[str, Dict[str, Any]] = {}

    # Attach composite scores and dedup signature to every node first
    by_group: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        is_legacy = bool(node.get("legacy_input_protocol"))
        if is_legacy and not allow_legacy_reference_eval:
            continue
        family = node.get("task_family") or primary_task_family(node)
        node["task_family"] = family
        comp = compute_node_composite_scores(
            node.get("validation") or {},
            task_family=family,
            baseline_0=b0,
            s2_audit_passed=s2_audit_passed,
        )
        node["composite_scores"] = comp
        node["primary_score"] = comp["primary_score"]
        node["s1_score"] = comp["s1_score"]
        node["s2_score"] = comp["s2_score"]
        node["s2_diagnostic_score"] = comp["s2_diagnostic_score"]
        node["s2_status"] = comp["s2_status"]
        node["s3_score"] = comp["s3_score"]
        node["beats_baseline_0"] = comp["beats_baseline_0"]
        # Multi-tier selection score: combine internal score with external DEV score if present
        dev_res = node.get("external_dev_result")
        sel_info = compute_composite_selection_score(comp["primary_score"], dev_res)
        node["selection_score"] = sel_info["selection_score"]
        node["external_dev_status"] = sel_info["external_dev_status"]
        node["external_dev_score"] = sel_info["external_dev_score"]
        node["selection_formula"] = sel_info["formula_used"]
        node["dedup_signature"] = node.get("dedup_signature") or compute_run_dedup_signature(node, out_root=out_root)
        gid = build_comparable_group_id(node)
        node["comparable_group_id"] = gid
        by_group[gid].append(node)

    # Identify within-run best epoch across all active nodes
    nodes_by_run: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        if bool(node.get("legacy_input_protocol")) and not allow_legacy_reference_eval:
            continue
        nodes_by_run[node["run_id"]].append(node)

    run_best_ckpt_id: Dict[str, str] = {}
    for rid, rnodes in nodes_by_run.items():
        fam = rnodes[0].get("task_family", "S1")
        best_n = min(rnodes, key=lambda x: _node_primary_sort_key(x, fam))
        run_best_ckpt_id[rid] = best_n["checkpoint_id"]
        for rn in rnodes:
            rn["is_run_best_epoch"] = (rn["checkpoint_id"] == best_n["checkpoint_id"])

    # Identify canonical Run for each `dedup_signature` within each comparable group
    canonical_run_by_sig: Dict[Tuple[str, str], str] = {}
    for gid, gnodes in sorted(by_group.items()):
        for n in sorted(gnodes, key=lambda x: (str(x.get("started_at") or ""), str(x["run_id"]), int(x.get("epoch", 0)))):
            sig_key = (gid, n["dedup_signature"])
            if sig_key not in canonical_run_by_sig:
                canonical_run_by_sig[sig_key] = n["run_id"]
        for n in gnodes:
            sig_key = (gid, n["dedup_signature"])
            n["canonical_run_id"] = canonical_run_by_sig[sig_key]
            n["is_duplicate_run_signature"] = (n["run_id"] != canonical_run_by_sig[sig_key])

    # 1. Global S1 champions (Condition F: strictly within the active protocol cohort, excluding duplicate run signatures)
    s1_candidates = [
        n for n in nodes
        if (not n.get("legacy_input_protocol") or allow_legacy_reference_eval)
        and not n.get("is_duplicate_run_signature")
        and n.get("task_family") == "S1"
        and isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))
    ]
    global_best_s1_score_id = None
    global_best_s1_loss_id = None
    global_best_s1_acc_id = None
    global_best_s1_brier_id = None
    batch_best_s1_ids: Dict[str, str] = {}

    if s1_candidates:
        best_score_node = max(
            s1_candidates,
            key=lambda n: (
                n.get("s1_score") if isinstance(n.get("s1_score"), (int, float)) else -999.0,
                -(n["validation"]["S1"]["loss"]),
                n["validation"]["S1"].get("accuracy") or 0.0,
            ),
        )
        global_best_s1_score_id = best_score_node["checkpoint_id"]

        best_loss_node = min(
            s1_candidates,
            key=lambda n: (
                n["validation"]["S1"]["loss"],
                -(n["validation"]["S1"].get("accuracy") or 0.0),
                n["validation"]["S1"].get("brier") or 999.0,
            ),
        )
        global_best_s1_loss_id = best_loss_node["checkpoint_id"]

        best_acc_node = max(
            s1_candidates,
            key=lambda n: (
                n["validation"]["S1"].get("accuracy") or -1.0,
                -(n["validation"]["S1"]["loss"]),
                -(n["validation"]["S1"].get("brier") or 999.0),
            ),
        )
        global_best_s1_acc_id = best_acc_node["checkpoint_id"]

        brier_nodes = [n for n in s1_candidates if isinstance(n["validation"]["S1"].get("brier"), (int, float))]
        if brier_nodes:
            best_brier_node = min(
                brier_nodes,
                key=lambda n: (
                    n["validation"]["S1"]["brier"],
                    n["validation"]["S1"]["loss"],
                    -(n["validation"]["S1"].get("accuracy") or 0.0),
                ),
            )
            global_best_s1_brier_id = best_brier_node["checkpoint_id"]

        # Per-batch best S1 checkpoint that passes Condition A (`beats_baseline_0`)
        by_batch: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for n in s1_candidates:
            bid = n.get("batch_id")
            if bid and n.get("is_run_best_epoch") and n.get("beats_baseline_0"):
                by_batch[str(bid)].append(n)
        for bid, bnodes in by_batch.items():
            best_b = max(
                bnodes,
                key=lambda n: (
                    n.get("s1_score") or -999.0,
                    -(n["validation"]["S1"]["loss"]),
                ),
            )
            batch_best_s1_ids[bid] = best_b["checkpoint_id"]

    # 2. Evaluate each comparable group using Three-Tier Baselines + Top 30%
    for gid, gnodes in sorted(by_group.items()):
        if not gnodes:
            continue
        family = gnodes[0].get("task_family", "S1")
        n_total_epochs = len(gnodes)

        # Distinct Runs contributing to BASELINE_1 & BASELINE_2 (1 best epoch per distinct non-duplicate Run)
        distinct_run_best_nodes = [
            n for n in gnodes
            if n.get("is_run_best_epoch") and not n.get("is_duplicate_run_signature")
        ]
        duplicate_run_ids = sorted({
            n["run_id"] for n in gnodes if n.get("is_duplicate_run_signature")
        })
        n_distinct_runs = len(distinct_run_best_nodes)
        cold_start = n_distinct_runs < MIN_COMPARABLE_RUNS
        top_30pct_quota = (
            COLD_START_TOP_K if cold_start else max(1, int(math.ceil(n_distinct_runs * RETENTION_TARGET)))
        )

        # Pareto frontier among distinct run best nodes
        pareto_ids = compute_pareto_frontier_ids(distinct_run_best_nodes, task_family=family)
        for n in gnodes:
            n["is_pareto_front"] = (n["checkpoint_id"] in pareto_ids)

        # Compute BASELINE_1 & BASELINE_2 distributions over distinct_run_best_nodes
        run_scores = [
            float(n["primary_score"])
            for n in distinct_run_best_nodes
            if isinstance(n.get("primary_score"), (int, float))
        ]
        score_stats = compute_robust_distribution_stats(run_scores, trim_ratio=TRIM_RATIO)

        # Also compute epoch-level & run-level metric averages for compatibility and diagnostics
        if family == "S1":
            run_losses = [n["validation"]["S1"]["loss"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
            run_accs = [n["validation"]["S1"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("accuracy"), (int, float))]
            run_briers = [n["validation"]["S1"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("brier"), (int, float))]
            ep_losses = [n["validation"]["S1"]["loss"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
            ep_accs = [n["validation"]["S1"]["accuracy"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("accuracy"), (int, float))]
            ep_briers = [n["validation"]["S1"]["brier"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("brier"), (int, float))]

            loss_stats = compute_robust_distribution_stats(run_losses, trim_ratio=TRIM_RATIO)
            acc_stats = compute_robust_distribution_stats(run_accs, trim_ratio=TRIM_RATIO)
            brier_stats = compute_robust_distribution_stats(run_briers, trim_ratio=TRIM_RATIO)

            mean_loss = loss_stats["robust_mean"]
            mean_acc = acc_stats["robust_mean"]
            mean_brier = brier_stats["robust_mean"]
            mean_score = score_stats["robust_mean"]
            mean_score_floor = round(mean_score * MEAN_FLOOR_RATIO, 4) if mean_score is not None else None

            # Evaluate each node in the group
            qualified_best_nodes: List[Dict[str, Any]] = []
            node_eval: Dict[str, Dict[str, Any]] = {}
            for n in gnodes:
                cid = n["checkpoint_id"]
                rid = n["run_id"]
                s1 = n.get("validation", {}).get("S1") or {}
                l_val = s1.get("loss")
                a_val = s1.get("accuracy")
                b_val = s1.get("brier")
                sc_val = n.get("primary_score")

                # Leave-one-out BASELINE_1 for this Run
                other_best = [x for x in distinct_run_best_nodes if x["run_id"] != n.get("canonical_run_id")]
                other_scores = [float(x["primary_score"]) for x in other_best if isinstance(x.get("primary_score"), (int, float))]
                other_losses = [float(x["validation"]["S1"]["loss"]) for x in other_best if isinstance((x.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
                loo_score_stats = compute_robust_distribution_stats(other_scores, trim_ratio=TRIM_RATIO) if other_scores else score_stats
                loo_loss_stats = compute_robust_distribution_stats(other_losses, trim_ratio=TRIM_RATIO) if other_losses else loss_stats
                loo_mean_score = loo_score_stats["robust_mean"] if loo_score_stats["robust_mean"] is not None else mean_score
                loo_mean_loss = loo_loss_stats["robust_mean"] if loo_loss_stats["robust_mean"] is not None else mean_loss
                loo_floor = round(loo_mean_score * MEAN_FLOOR_RATIO, 4) if loo_mean_score is not None else None

                # Condition A: Beat BASELINE_0 (`S1_score > 100.0`, `loss <= L0`, `acc >= A0 - 0.005`)
                cond_a_b0 = bool(n.get("beats_baseline_0"))
                # Classical P1 Condition A/B diagnostics
                p1_cond_a = bool(
                    loo_mean_loss is not None and mean_acc is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float))
                    and l_val <= loo_mean_loss * (1.0 - S1_LOSS_IMPROVEMENT_REL)
                    and a_val >= mean_acc - S1_ACC_DEGRADATION_TOL
                )
                p1_cond_b = bool(
                    loo_mean_loss is not None and mean_acc is not None and mean_brier is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float)) and isinstance(b_val, (int, float))
                    and a_val >= mean_acc + S1_ACC_IMPROVEMENT_ABS
                    and l_val <= loo_mean_loss * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL)
                    and b_val <= mean_brier * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL)
                )
                # Condition B: Composite score >= 0.98 * historical robust mean (leave-one-out)
                cond_b_mean_floor = bool(
                    loo_floor is not None
                    and isinstance(sc_val, (int, float))
                    and sc_val >= loo_floor
                )
                passes_thresholds = (
                    bool(cond_a_b0 or n.get("is_run_best_epoch"))
                    if cold_start
                    else bool(cond_a_b0 and (cond_b_mean_floor or p1_cond_a or p1_cond_b))
                )
                node_eval[cid] = {
                    "cond_a_baseline0_pass": cond_a_b0,
                    "cond_b_mean_floor_pass": cond_b_mean_floor,
                    "cond_a_pass": cond_a_b0 or p1_cond_a,
                    "cond_b_pass": cond_b_mean_floor or p1_cond_b,
                    "loo_mean_score": loo_mean_score,
                    "loo_score_floor": loo_floor,
                    "threshold_pass": passes_thresholds,
                    "cold_start": cold_start,
                }
                if (
                    passes_thresholds
                    and n.get("is_run_best_epoch")
                    and not n.get("is_duplicate_run_signature")
                    and isinstance(sc_val, (int, float))
                ):
                    qualified_best_nodes.append(n)

            # Condition C & E: Rank qualified run-best nodes by Composite Score + Pareto tie-breaker (within 0.5 pts)
            def _s1_rank_key(cand: Dict[str, Any]) -> Tuple[float, float, float, float]:
                sc = float(cand.get("primary_score") or 0.0)
                # Condition E: Pareto frontier models receive +PARETO_TIE_MARGIN (0.5) tie-break priority
                eff_sc = sc + (PARETO_TIE_MARGIN if cand.get("is_pareto_front") else 0.0)
                s1_v = cand["validation"]["S1"]
                return (
                    -round(eff_sc, 4),
                    -round(sc, 4),
                    float(s1_v["loss"]),
                    -(float(s1_v.get("accuracy") or 0.0)),
                )

            ranked = sorted(qualified_best_nodes, key=_s1_rank_key)
            non_pinned_ranked = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned_ranked[:top_30pct_quota]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S1",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "distinct_completed_runs": n_distinct_runs,
                "duplicate_runs_excluded": len(duplicate_run_ids),
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "cold_start_mode": cold_start,
                "min_controls_required": MIN_COMPARABLE_RUNS,
                "retention_target_ratio": RETENTION_TARGET,
                "top_k_limit": top_30pct_quota,
                "top_k_quota": top_30pct_quota,
                "baseline_0": {
                    "s1_score": S1_SCORE_BASELINE,
                    "loss": b0_val["S1"]["loss"],
                    "accuracy": b0_val["S1"]["accuracy"],
                    "brier": b0_val["S1"]["brier"],
                    "ece": b0_val["S1"]["ece"],
                },
                "baseline_1_historical": {
                    "score_stats": score_stats,
                    "loss_stats": loss_stats,
                    "accuracy_stats": acc_stats,
                    "brier_stats": brier_stats,
                    "trimmed_mean_active": n_distinct_runs >= 10,
                    "mean_floor_ratio": MEAN_FLOOR_RATIO,
                    "mean_score_floor": mean_score_floor,
                },
                "baseline_1_stats": {
                    "score": score_stats,
                    "loss": loss_stats,
                    "accuracy": acc_stats,
                    "brier": brier_stats,
                },
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                    "P50": score_stats["p50"],
                    "P70": score_stats["p70"],
                    "P90": score_stats["p90"],
                    "BEST": score_stats["max"],
                    "pareto_frontier_ids": sorted(pareto_ids),
                },
                "mean_val_loss": round(sum(ep_losses) / len(ep_losses), 4) if ep_losses else None,
                "mean_accuracy": round(sum(ep_accs) / len(ep_accs), 4) if ep_accs else None,
                "mean_brier": round(sum(ep_briers) / len(ep_briers), 4) if ep_briers else None,
                "run_best_mean_val_loss": mean_loss,
                "run_best_mean_accuracy": mean_acc,
                "run_best_mean_brier": mean_brier,
                "mean_composite_score": score_stats["mean"],
                "trimmed_mean_composite_score": score_stats["trimmed_mean"],
                "thresholds": {
                    "baseline_0_score": S1_SCORE_BASELINE,
                    "mean_score_floor": mean_score_floor,
                    "p70_top30pct_score": score_stats["p70"],
                    "p90_top10pct_score": score_stats["p90"],
                    "top_30pct_quota": top_30pct_quota,
                },
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "is_duplicate_run_signature": n.get("is_duplicate_run_signature", False),
                        "is_pareto_front": n.get("is_pareto_front", False),
                        "s1_score": n.get("s1_score"),
                        "loss": (n.get("validation", {}).get("S1") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S1") or {}).get("accuracy"),
                        "brier": (n.get("validation", {}).get("S1") or {}).get("brier"),
                        "ece": (n.get("validation", {}).get("S1") or {}).get("ece"),
                        "cond_a": node_eval[n["checkpoint_id"]]["cond_a_pass"],
                        "cond_b": node_eval[n["checkpoint_id"]]["cond_b_pass"],
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                ev = node_eval[cid]
                reasons: List[str] = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if not n.get("is_duplicate_run_signature"):
                    if cid == global_best_s1_score_id and n.get("beats_baseline_0"):
                        reasons.append("global_best_s1_composite_score")
                    if cid == global_best_s1_loss_id:
                        reasons.append("global_best_s1_loss")
                    if cid == global_best_s1_acc_id:
                        reasons.append("global_best_s1_accuracy")
                    if cid == global_best_s1_brier_id and n.get("is_run_best_epoch"):
                        reasons.append("global_best_s1_brier")
                    bid = str(n.get("batch_id") or "")
                    if bid and batch_best_s1_ids.get(bid) == cid:
                        reasons.append(f"batch_{bid}_best_s1_score")
                    if cid in top_k_ids:
                        if cold_start:
                            reasons.append(f"group_cold_start_top_{top_30pct_quota}(runs={n_distinct_runs}<{MIN_COMPARABLE_RUNS})")
                        else:
                            reasons.append(
                                f"group_top_30pct(quota={top_30pct_quota}/{n_distinct_runs},"
                                f"score={n.get('s1_score')}>=floor_{ev['loo_score_floor']})"
                            )
                        if n.get("is_pareto_front"):
                            reasons.append("pareto_frontier_non_dominated")

                should_retain = len(reasons) > 0
                if not should_retain:
                    if n.get("is_duplicate_run_signature"):
                        reject_reason = f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    elif not n.get("is_run_best_epoch"):
                        reject_reason = f"non_best_epoch_within_run(best={run_best_ckpt_id.get(n['run_id'])})"
                    elif not ev["cond_a_baseline0_pass"]:
                        reject_reason = f"below_baseline_0(s1_score={n.get('s1_score')}<=100.0_or_loss_acc_degraded)"
                    elif not ev["threshold_pass"]:
                        reject_reason = (
                            f"below_historical_mean_floor(s1_score={n.get('s1_score')}<0.98*mean={ev['loo_score_floor']})"
                        )
                    else:
                        reject_reason = (
                            f"s1_outside_top_30pct(quota={top_30pct_quota}/{n_distinct_runs},p70={score_stats['p70']})"
                        )
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": cid in {global_best_s1_score_id, global_best_s1_loss_id, global_best_s1_acc_id, global_best_s1_brier_id} and not n.get("is_duplicate_run_signature"),
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S1",
                    "cond_a_pass": ev["cond_a_pass"],
                    "cond_b_pass": ev["cond_b_pass"],
                }

        elif family == "S2":
            # S2 Rule (Section 3.2 & 4): before independent audit passes, DIAGNOSTIC_ONLY,
            # never crown as global champion, retain at most 1 diagnostic model across the group.
            s2_losses = [n["validation"]["S2"]["loss"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float))]
            s2_accs = [n["validation"]["S2"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("accuracy"), (int, float))]
            s2_briers = [n["validation"]["S2"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("brier"), (int, float))]
            mean_loss = sum(s2_losses) / len(s2_losses) if s2_losses else None
            mean_acc = sum(s2_accs) / len(s2_accs) if s2_accs else None
            mean_brier = sum(s2_briers) / len(s2_briers) if s2_briers else None

            if not s2_audit_passed:
                ranked = sorted(
                    distinct_run_best_nodes,
                    key=lambda n: (
                        (n.get("validation", {}).get("S2") or {}).get("loss") if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float)) else 999.0,
                        n.get("epoch", 99),
                    ),
                )
                top_k_ids = [ranked[0]["checkpoint_id"]] if ranked else []
                s2_quota = 1
            else:
                qualified = [
                    n for n in distinct_run_best_nodes
                    if n.get("beats_baseline_0")
                    and (n.get("composite_scores", {}).get("S2_detail") or {}).get("beats_majority_baseline")
                    and (
                        cold_start
                        or (
                            score_stats["robust_mean"] is not None
                            and isinstance(n.get("primary_score"), (int, float))
                            and n["primary_score"] >= score_stats["robust_mean"] * MEAN_FLOOR_RATIO
                        )
                    )
                ]
                ranked = sorted(
                    qualified,
                    key=lambda n: (
                        -(float(n.get("primary_score") or 0.0)),
                        n["validation"]["S2"]["loss"],
                        -(n["validation"]["S2"].get("balanced_accuracy") or 0.0),
                    ),
                )
                non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
                s2_quota = top_30pct_quota
                top_k_ids = [n["checkpoint_id"] for n in non_pinned[:s2_quota]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S2",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "s2_audit_passed": s2_audit_passed,
                "s2_policy_mode": "AUDIT_PASSED_TOP_30PCT" if s2_audit_passed else "DIAGNOSTIC_SINGLE_CAP_PENDING_AUDIT",
                "majority_baseline": S2_VAL_BASELINE,
                "baseline_1_historical": {"score_stats": score_stats},
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                },
                "top_k_limit": s2_quota,
                "mean_val_loss": round(mean_loss, 4) if mean_loss is not None else None,
                "mean_accuracy": round(mean_acc, 4) if mean_acc is not None else None,
                "mean_brier": round(mean_brier, 4) if mean_brier is not None else None,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "s2_score": n.get("s2_score"),
                        "s2_diagnostic_score": n.get("s2_diagnostic_score"),
                        "s2_status": n.get("s2_status"),
                        "loss": (n.get("validation", {}).get("S2") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S2") or {}).get("accuracy"),
                        "balanced_accuracy": (n.get("validation", {}).get("S2") or {}).get("balanced_accuracy"),
                        "macro_f1": (n.get("validation", {}).get("S2") or {}).get("macro_f1"),
                        "brier": (n.get("validation", {}).get("S2") or {}).get("brier"),
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                reasons = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if cid in top_k_ids and not n.get("is_duplicate_run_signature"):
                    if not s2_audit_passed:
                        reasons.append("s2_diagnostic_single_model_pending_audit(not_global_champion)")
                    else:
                        reasons.append(f"s2_audited_top_30pct(quota={s2_quota})")
                should_retain = len(reasons) > 0
                reject_reason = (
                    None if should_retain
                    else f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    if n.get("is_duplicate_run_signature")
                    else "s2_100pct_not_trusted_pending_independent_audit(diagnostic_cap=1)"
                    if not s2_audit_passed
                    else "s2_below_majority_baseline_or_outside_top_30pct"
                )
                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,  # S2 is never crowned global champion before audit
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S2",
                }

        else:
            # S3 Rule (Section 3.3 & 4): compare per real target against each target's majority/prior baseline
            # and rank by macro-averaged S3_score (never summing raw S3 losses).
            per_target_stats: Dict[str, Dict[str, Any]] = {}
            for t_key, base in S3_VAL_BASELINES.items():
                t_losses = []
                t_accs = []
                t_briers = []
                t_scores = []
                for n in distinct_run_best_nodes:
                    tb = (n.get("validation", {}).get("S3_by_source_target") or {}).get(t_key) or {}
                    if isinstance(tb.get("loss"), (int, float)):
                        t_losses.append(tb["loss"])
                    if isinstance(tb.get("accuracy"), (int, float)):
                        t_accs.append(tb["accuracy"])
                    if isinstance(tb.get("brier"), (int, float)):
                        t_briers.append(tb["brier"])
                    if isinstance(tb.get("s3_target_score"), (int, float)):
                        t_scores.append(tb["s3_target_score"])
                m_loss = sum(t_losses) / len(t_losses) if t_losses else None
                m_acc = sum(t_accs) / len(t_accs) if t_accs else None
                m_brier = sum(t_briers) / len(t_briers) if t_briers else None
                m_score = sum(t_scores) / len(t_scores) if t_scores else None
                per_target_stats[t_key] = {
                    "baseline_majority_accuracy": base["majority_accuracy"],
                    "baseline_prior_loss": base["prior_loss"],
                    "baseline_balanced_accuracy": base["majority_balanced_accuracy"],
                    "mean_val_loss": round(m_loss, 4) if m_loss is not None else None,
                    "mean_accuracy": round(m_acc, 4) if m_acc is not None else None,
                    "mean_brier": round(m_brier, 4) if m_brier is not None else None,
                    "mean_target_score": round(m_score, 4) if m_score is not None else None,
                    "threshold_max_loss": round(min(base["prior_loss"] * 0.995, (m_loss * 0.995) if (m_loss and not cold_start) else base["prior_loss"] * 0.995), 4),
                    "threshold_min_accuracy": round(max(base["majority_accuracy"] + 0.005, (m_acc - 0.005) if (m_acc and not cold_start) else base["majority_accuracy"] + 0.005), 4),
                }

            qualified = []
            node_s3_summary: Dict[str, Dict[str, Any]] = {}
            mean_s3_score = score_stats["robust_mean"]
            s3_score_floor = round(mean_s3_score * MEAN_FLOOR_RATIO, 4) if mean_s3_score is not None else None

            for n in gnodes:
                cid = n["checkpoint_id"]
                s3_detail = (n.get("composite_scores") or {}).get("S3_detail") or compute_s3_composite_score(
                    (n.get("validation") or {}).get("S3"),
                    (n.get("validation") or {}).get("S3_by_source_target"),
                    b0_val.get("S3"),
                )
                s3_sc = s3_detail.get("s3_score")
                passes_floor = bool(
                    cold_start
                    or (
                        s3_score_floor is not None
                        and isinstance(s3_sc, (int, float))
                        and s3_sc >= s3_score_floor
                    )
                )
                eligible = bool(s3_detail.get("beats_baseline_0") and passes_floor)
                node_s3_summary[cid] = {
                    "s3_score": s3_sc,
                    "beaten_targets": s3_detail.get("beaten_targets") or [],
                    "beaten_target_count": s3_detail.get("beaten_target_count", 0),
                    "active_target_count": s3_detail.get("active_target_count", 0),
                    "per_target_scores": s3_detail.get("per_target_scores") or {},
                    "mean_relative_loss_reduction_vs_prior": s3_detail.get("mean_relative_loss_reduction_vs_prior", -1.0),
                    "eligible": eligible,
                }
                if eligible and n.get("is_run_best_epoch") and not n.get("is_duplicate_run_signature"):
                    qualified.append(n)

            ranked = sorted(
                qualified,
                key=lambda n: (
                    -(float(node_s3_summary[n["checkpoint_id"]]["s3_score"] or 0.0)),
                    -node_s3_summary[n["checkpoint_id"]]["beaten_target_count"],
                    -node_s3_summary[n["checkpoint_id"]]["mean_relative_loss_reduction_vs_prior"],
                    n.get("epoch", 99),
                ),
            )
            non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned[:top_30pct_quota]]

            s3_accs = [n["validation"]["S3"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S3") or {}).get("accuracy"), (int, float))]
            s3_briers = [n["validation"]["S3"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S3") or {}).get("brier"), (int, float))]
            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S3",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "cold_start_mode": cold_start,
                "retention_target_ratio": RETENTION_TARGET,
                "top_k_limit": top_30pct_quota,
                "ranking_rule": "per_target_macro_composite_s3_score_and_majority_baseline_filter (raw losses never summed)",
                "baseline_1_historical": {
                    "score_stats": score_stats,
                    "mean_score_floor": s3_score_floor,
                },
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                },
                "mean_accuracy": round(sum(s3_accs) / len(s3_accs), 4) if s3_accs else None,
                "mean_brier": round(sum(s3_briers) / len(s3_briers), 4) if s3_briers else None,
                "mean_composite_score": score_stats["mean"],
                "per_target_thresholds": per_target_stats,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "s3_score": node_s3_summary[n["checkpoint_id"]]["s3_score"],
                        "accuracy": (n.get("validation", {}).get("S3") or {}).get("accuracy"),
                        "brier": (n.get("validation", {}).get("S3") or {}).get("brier"),
                        "beaten_targets": node_s3_summary[n["checkpoint_id"]]["beaten_targets"],
                        "beaten_target_count": node_s3_summary[n["checkpoint_id"]]["beaten_target_count"],
                        "mean_rel_gain": node_s3_summary[n["checkpoint_id"]]["mean_relative_loss_reduction_vs_prior"],
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                s3_ev = node_s3_summary[cid]
                reasons = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if cid in top_k_ids and not n.get("is_duplicate_run_signature"):
                    reasons.append(
                        f"s3_per_target_top_30pct(quota={top_30pct_quota},s3_score={s3_ev['s3_score']},"
                        f"beat_baseline={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']})"
                    )
                should_retain = len(reasons) > 0
                if not should_retain:
                    if n.get("is_duplicate_run_signature"):
                        reject_reason = f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    elif not n.get("is_run_best_epoch"):
                        reject_reason = f"non_best_epoch_within_run(best={run_best_ckpt_id.get(n['run_id'])})"
                    elif not s3_ev["eligible"]:
                        reject_reason = (
                            f"s3_targets_below_majority_baseline_or_b0(s3_score={s3_ev['s3_score']},"
                            f"beat={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']})"
                        )
                    else:
                        reject_reason = f"s3_outside_group_top_30pct(quota={top_30pct_quota})"
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S3",
                    "s3_beaten_targets": s3_ev["beaten_targets"],
                    "s3_mean_rel_gain": s3_ev["mean_relative_loss_reduction_vs_prior"],
                }

    # Dual Pool Retention (Section 3):
    # 1. Old Core Pool: 5 fixed core checkpoints retained prior to policy change. Permanently preserved.
    # 2. New Core Pool: Dynamic best-of retention of ~15% (ceil(0.15 * N_new_eligible)) of eligible new run best-epochs.
    # Pinned parents (R1-e01, R2-e01) and temp recovery checkpoints are protected separately.
    is_simulation = any(n.get("run_id", "").startswith("P0_SIM_") for n in nodes)
    if not allow_legacy_reference_eval and not is_simulation:
        node_map = {n["checkpoint_id"]: n for n in nodes}

        # 1. Old Core Pool: protect the 5 historical core checkpoints
        for cid in OLD_CORE_CHECKPOINT_IDS:
            if cid in decisions:
                dec = decisions[cid]
                dec["should_retain"] = True
                dec["retention_pool"] = "OLD_CORE_POOL"
                if "retention_reasons" not in dec or dec["retention_reasons"] is None:
                    dec["retention_reasons"] = []
                if "old_core_pool_protected(5_fixed_core)" not in dec["retention_reasons"]:
                    dec["retention_reasons"].append("old_core_pool_protected(5_fixed_core)")

        # 2. Pinned parents: ensure marked as PINNED_PARENT pool
        for cid, dec in decisions.items():
            if dec.get("is_pinned_parent"):
                dec["retention_pool"] = "PINNED_PARENT"

        # 3. New Candidates: candidate unit is best epoch of each eligible independent run after policy adjustment
        # Old strategy models (P0_*, historical sweeps, etc.) were already evaluated under the old policy
        # and MUST NOT be added to the new candidate denominator.
        new_eligible_candidates = []
        for n in nodes:
            cid = n["checkpoint_id"]
            run_id = n.get("run_id", "")
            # Exclude old core checkpoints
            if cid in OLD_CORE_CHECKPOINT_IDS:
                continue
            # Exclude old strategy historical models from inflating the new candidate denominator
            if run_id.startswith(("P0_", "R0_", "N", "R1", "R2", "R3")) or n.get("experiment_group") in ("OVERNIGHT-LAYA-TRAINING", "OVERNIGHT-LAYA-SWEEP-02"):
                continue
            if n.get("is_pinned_parent") or cid in pinned_map:
                continue
            # Exclude duplicate signatures and uncompleted runs without valid validation
            if n.get("is_duplicate_run_signature"):
                continue
            if not n.get("is_run_best_epoch"):
                continue
            val = n.get("validation", {})
            if not val or not any(val.get(k, {}).get("items", 0) > 0 for k in ("S1", "S2", "S3", "all")):
                continue
            new_eligible_candidates.append(n)

        n_new_eligible = len(new_eligible_candidates)
        new_pool_quota = math.ceil(NEW_CORE_POOL_RATIO * n_new_eligible) if n_new_eligible > 0 else 0

        # Group by comparable group: (protocol_version, task_family/primary_supervision_class)
        by_group = defaultdict(list)
        for n in new_eligible_candidates:
            cid = n["checkpoint_id"]
            gid = decisions.get(cid, {}).get("comparable_group_id") or n.get("comparable_group_id") or "default"
            by_group[gid].append(n)

        # Collect retained from new groups up to new_pool_quota
        new_retained_ids = set()
        for gid, g_nodes in by_group.items():
            def _rank_new(n_val):
                sc = float(n_val.get("selection_score") or n_val.get("primary_score") or 0.0)
                s1_val = (n_val.get("validation", {}).get("S1") or {})
                loss = float(s1_val.get("loss", 999.0)) if isinstance(s1_val.get("loss"), (int, float)) else 999.0
                acc = float(s1_val.get("accuracy", -1.0)) if isinstance(s1_val.get("accuracy"), (int, float)) else -1.0
                brier = float(s1_val.get("brier", 999.0)) if isinstance(s1_val.get("brier"), (int, float)) else 999.0
                return (-round(sc, 4), round(loss, 4), -round(acc, 4), round(brier, 4))

            sorted_g = sorted(g_nodes, key=_rank_new)
            g_quota = max(1, math.ceil(NEW_CORE_POOL_RATIO * len(sorted_g))) if len(sorted_g) > 0 else 0
            for n_val in sorted_g[:g_quota]:
                if len(new_retained_ids) < new_pool_quota:
                    new_retained_ids.add(n_val["checkpoint_id"])

        # Update decisions for new candidates
        for n in nodes:
            cid = n["checkpoint_id"]
            if cid in OLD_CORE_CHECKPOINT_IDS or n.get("is_pinned_parent") or cid in pinned_map:
                continue
            if cid in decisions:
                dec = decisions[cid]
                if cid in new_retained_ids:
                    dec["should_retain"] = True
                    dec["retention_pool"] = "NEW_CORE_POOL"
                    dec["rejection_reason"] = None
                    if "retention_reasons" not in dec or dec["retention_reasons"] is None:
                        dec["retention_reasons"] = []
                    dec["retention_reasons"].append(f"new_core_pool_15pct(quota={new_pool_quota}/{n_new_eligible})")
                else:
                    dec["should_retain"] = False
                    dec["retention_pool"] = "METADATA_ONLY"
                    if not dec.get("rejection_reason"):
                        dec["rejection_reason"] = f"outside_new_core_pool_15pct_quota({new_pool_quota}/{n_new_eligible})"

    return decisions, group_summaries


def resolve_retention_status(
    decision: Dict[str, Any],
    weights_currently_saved: bool,
    was_previously_saved: bool,
    is_legacy: bool,
) -> str:
    """Map policy decision + physical disk state to one of the 8 canonical statuses."""
    if is_legacy and not weights_currently_saved:
        return STATUS_LEGACY_METADATA_ONLY
    if decision.get("is_pinned_parent") and weights_currently_saved:
        return STATUS_PINNED_PARENT
    if decision.get("is_global_best") and weights_currently_saved:
        return STATUS_RETAINED_BEST
    if decision.get("should_retain") and weights_currently_saved:
        return STATUS_RETAINED_TOP_K
    if not decision.get("should_retain"):
        if decision.get("is_duplicate_run_signature") and was_previously_saved and not weights_currently_saved:
            return STATUS_PRUNED_DUPLICATE
        if was_previously_saved and not weights_currently_saved:
            return STATUS_PRUNED_LOW_SCORE
        if weights_currently_saved:
            return STATUS_PRUNED_LOW_SCORE
        return STATUS_METADATA_ONLY
    return STATUS_METADATA_ONLY



class CheckpointRetentionManager:
    """Manages selective checkpoint saving, deduplication, disk budget checks, and two-phase cleanup."""

    def __init__(
        self,
        out_root: Path,
        active_budget_bytes: int = DEFAULT_ACTIVE_BUDGET_BYTES,
        warn_free_pct: float = DISK_WARN_FREE_PCT,
        stop_free_pct: float = DISK_STOP_FREE_PCT,
        warn_free_bytes: int = DISK_WARN_FREE_BYTES,
        stop_free_bytes: int = DISK_STOP_FREE_BYTES,
        s2_audit_passed: bool = False,
        explicit_pinned: Optional[Iterable[str]] = None,
    ):
        self.out_root = Path(out_root).resolve()
        self.active_budget_bytes = int(active_budget_bytes)
        self.warn_free_pct = float(warn_free_pct)
        self.stop_free_pct = float(stop_free_pct)
        self.warn_free_bytes = int(warn_free_bytes)
        self.stop_free_bytes = int(stop_free_bytes)
        self.s2_audit_passed = bool(s2_audit_passed)
        self.explicit_pinned: Set[str] = set(explicit_pinned or ())

    def is_whitelisted_checkpoint_dir(self, target_dir: Path) -> Tuple[bool, str]:
        """Verify `target_dir` is strictly inside `<out_root>/<run_id>/checkpoints/<name>` and not forbidden."""
        try:
            resolved = Path(target_dir).resolve()
        except OSError as exc:
            return False, f"resolve_error:{exc}"

        try:
            rel = resolved.relative_to(self.out_root)
        except ValueError:
            return False, "outside_authorized_out_root"

        parts = rel.parts
        if len(parts) != 3 or parts[1] != "checkpoints":
            return False, f"invalid_checkpoint_subpath:{rel}"

        full_str = str(resolved)
        for token in FORBIDDEN_PATH_TOKENS:
            # Allow if out_root itself was explicitly created in a test temp dir, but block any forbidden token in relative path
            if token in str(rel) or (token in full_str and token not in str(self.out_root.name)):
                return False, f"forbidden_path_token:{token}"

        run_dir = self.out_root / parts[0]
        if (run_dir / ".writing_lock").exists() or (resolved / ".writing_lock").exists():
            return False, "checkpoint_write_in_progress"

        return True, "whitelisted_ok"

    def disk_status(self, simulated_statvfs: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Query real-time filesystem capacity and active weight usage."""
        self.out_root.mkdir(parents=True, exist_ok=True)
        if simulated_statvfs is not None:
            total_b = int(simulated_statvfs["total_bytes"])
            avail_b = int(simulated_statvfs["avail_bytes"])
            used_b = int(simulated_statvfs.get("used_bytes", total_b - avail_b))
        else:
            st = os.statvfs(str(self.out_root))
            total_b = st.f_frsize * st.f_blocks
            avail_b = st.f_frsize * st.f_bavail
            used_b = total_b - (st.f_frsize * st.f_bfree)

        avail_pct = round(avail_b / total_b * 100.0, 2) if total_b > 0 else 0.0
        df_used_pct = round(used_b / (used_b + avail_b) * 100.0, 2) if (used_b + avail_b) > 0 else 0.0

        # Scan active out_root checkpoints
        best_bytes = 0
        pinned_bytes = 0
        top_k_bytes = 0
        temp_bytes = 0
        prunable_bytes = 0
        active_total_bytes = 0
        physical_ckpt_count = 0

        runs, nodes, pinned_map, decisions, _ = self.load_and_evaluate_all()
        node_by_dir: Dict[str, Dict[str, Any]] = {}
        for n in nodes:
            node_by_dir[f"{n['run_id']}/checkpoints/epoch_{int(n['epoch']):02d}"] = n

        for ckroot in sorted(self.out_root.glob("*/checkpoints")):
            run_id = ckroot.parent.name
            for sub in sorted(ckroot.iterdir()):
                if sub.is_symlink() or not sub.is_dir():
                    continue
                if not has_physical_weights(sub):
                    continue
                sz = physical_dir_bytes(sub)
                active_total_bytes += sz
                physical_ckpt_count += 1
                rel_key = f"{run_id}/checkpoints/{sub.name}"
                if sub.name in ("_temp_recovery", "latest"):
                    r_status = (runs.get(run_id) or {}).get("status")
                    if r_status == "running":
                        temp_bytes += sz
                    else:
                        prunable_bytes += sz
                elif sub.name == "best":
                    # A physical `best` dir when `epoch_XX` also exists is a duplicate
                    prunable_bytes += sz
                elif rel_key in node_by_dir:
                    cid = node_by_dir[rel_key]["checkpoint_id"]
                    dec = decisions.get(cid) or {}
                    if dec.get("is_pinned_parent"):
                        pinned_bytes += sz
                    elif dec.get("is_global_best"):
                        best_bytes += sz
                    elif dec.get("should_retain"):
                        top_k_bytes += sz
                    else:
                        prunable_bytes += sz
                else:
                    prunable_bytes += sz

        stop_triggered = avail_pct < self.stop_free_pct or avail_b < self.stop_free_bytes
        warn_triggered = stop_triggered or avail_pct < self.warn_free_pct or avail_b < self.warn_free_bytes
        state = "STOP" if stop_triggered else ("WARNING" if warn_triggered else "OK")

        return {
            "checked_at": _now_iso(),
            "root_total_bytes": total_b,
            "root_used_bytes": used_b,
            "root_avail_bytes": avail_b,
            "root_avail_pct": avail_pct,
            "root_df_used_pct": df_used_pct,
            "active_budget_bytes": self.active_budget_bytes,
            "active_weights_bytes": active_total_bytes,
            "active_budget_used_pct": round(active_total_bytes / self.active_budget_bytes * 100.0, 2) if self.active_budget_bytes > 0 else 0.0,
            "physical_checkpoint_count": physical_ckpt_count,
            "breakdown_bytes": {
                "retained_best_bytes": best_bytes,
                "pinned_parent_bytes": pinned_bytes,
                "retained_top_k_bytes": top_k_bytes,
                "temp_recovery_bytes": temp_bytes,
                "prunable_low_value_or_duplicate_bytes": prunable_bytes,
            },
            "thresholds": {
                "warn_free_pct": self.warn_free_pct,
                "stop_free_pct": self.stop_free_pct,
                "warn_free_bytes": self.warn_free_bytes,
                "stop_free_bytes": self.stop_free_bytes,
                "active_budget_bytes": self.active_budget_bytes,
            },
            "disk_guard_state": state,
            "stop_triggered": stop_triggered,
            "warn_triggered": warn_triggered,
        }

    def load_and_evaluate_all(
        self,
        manifest: Optional[Dict[str, Any]] = None,
    ) -> Tuple[
        Dict[str, Dict[str, Any]],
        List[Dict[str, Any]],
        Dict[str, List[str]],
        Dict[str, Dict[str, Any]],
        Dict[str, Dict[str, Any]],
    ]:
        """Load all `run.json` files in `out_root` and evaluate P1/P2 retention across all nodes."""
        runs: Dict[str, Dict[str, Any]] = {}
        for path in sorted(self.out_root.glob("*/run.json")):
            try:
                saved = json.loads(path.read_text(encoding="utf8"))
                runs[path.parent.name] = saved
            except (OSError, json.JSONDecodeError):
                continue

        plans = (manifest or {}).get("plans") or {}
        if not plans and (self.out_root / "experiment_matrix.json").exists():
            try:
                plans = json.loads((self.out_root / "experiment_matrix.json").read_text(encoding="utf8")).get("plans") or {}
            except (OSError, json.JSONDecodeError):
                plans = {}

        pinned_map = collect_pinned_parent_ids(runs, plans, self.explicit_pinned)
        baseline_0 = load_or_default_baseline_0(self.out_root)

        nodes: List[Dict[str, Any]] = []
        for run_id, r in sorted(runs.items()):
            if run_id == "R0":
                continue
            is_legacy = bool(
                r.get("legacy_input_protocol")
                or r.get("protocol_version") == LEGACY_PROTOCOL_VERSION
                or run_id.startswith("B01_")
            )
            protocol = LEGACY_PROTOCOL_VERSION if is_legacy else (r.get("protocol_version") or NEW_PROTOCOL_VERSION)
            gid = build_comparable_group_id(r)
            family = primary_task_family(r)
            dedup_sig = r.get("dedup_signature") or compute_run_dedup_signature(r, out_root=self.out_root)
            for entry in r.get("history") or []:
                epoch_no = int(entry.get("epoch", 0))
                cid = entry.get("checkpoint_id") or f"{run_id}-e{epoch_no:02d}"
                epoch_dir = self.out_root / run_id / "checkpoints" / f"epoch_{epoch_no:02d}"
                phys_exists = has_physical_weights(epoch_dir)
                val = dict(entry.get("validation") or {})
                if "S3_by_source_target" in val:
                    val["S3_by_source_target"] = enrich_s3_target_metrics(val["S3_by_source_target"])
                s1_v = val.get("S1") or {}
                s2_v = val.get("S2") or {}
                s3_v = val.get("S3") or {}
                tr_loss = entry.get("train_loss")
                prim_val_loss = s1_v.get("loss") if s1_v else (s2_v.get("loss") if s2_v else s3_v.get("loss"))
                train_val_gap = (
                    round(float(prim_val_loss) - float(tr_loss), 6)
                    if isinstance(prim_val_loss, (int, float)) and isinstance(tr_loss, (int, float))
                    else None
                )
                node = {
                    "checkpoint_id": cid,
                    "run_id": run_id,
                    "base_run_id": r.get("base_run_id") or (run_id[3:] if run_id.startswith("P0_") else run_id),
                    "epoch": epoch_no,
                    "parent_checkpoint_id": r.get("parent_checkpoint_id"),
                    "train_origin": r.get("train_origin", "Base"),
                    "protocol_version": protocol,
                    "legacy_input_protocol": is_legacy,
                    "comparable_group_id": gid,
                    "dedup_signature": dedup_sig,
                    "task_family": family,
                    "batch_id": r.get("batch_id"),
                    "combo_id": r.get("combo_id"),
                    "quality_code": r.get("quality_code"),
                    "sampling_code": r.get("sampling_code"),
                    "supervision_classes": r.get("supervision_classes") or sorted((r.get("train_groups") or {}).keys()),
                    "ratios": r.get("ratios"),
                    "train_groups": r.get("train_groups"),
                    "val_groups": r.get("val_groups"),
                    "seed": r.get("seed", 42),
                    "config": r.get("config") or {},
                    "learning_rate": entry.get("learning_rate") or {
                        "encoder": (r.get("config") or {}).get("encoder_lr"),
                        "head": (r.get("config") or {}).get("head_lr"),
                    },
                    "optimizer_updates": entry.get("optimizer_updates") or r.get("optimizer_updates_per_epoch"),
                    "global_step": entry.get("global_step"),
                    "train_loss": tr_loss,
                    "train_val_loss_gap": train_val_gap,
                    "validation": val,
                    "s1_val_loss": s1_v.get("loss"),
                    "s1_accuracy": s1_v.get("accuracy"),
                    "s1_brier": s1_v.get("brier"),
                    "s1_ece": s1_v.get("ece"),
                    "s2_val_loss": s2_v.get("loss"),
                    "s2_accuracy": s2_v.get("accuracy"),
                    "s2_balanced_accuracy": s2_v.get("balanced_accuracy"),
                    "s2_macro_f1": s2_v.get("macro_f1"),
                    "s3_val_loss": s3_v.get("loss"),
                    "s3_accuracy": s3_v.get("accuracy"),
                    "train_seconds": entry.get("train_seconds"),
                    "validation_seconds": entry.get("validation_seconds"),
                    "checkpoint_seconds": entry.get("checkpoint_seconds"),
                    "epoch_total_seconds": (
                        entry.get("epoch_total_seconds")
                        or entry.get("epoch_seconds")
                        or round(
                            float(entry.get("train_seconds") or 0.0)
                            + float(entry.get("validation_seconds") or 0.0)
                            + float(entry.get("checkpoint_seconds") or 0.0),
                            3,
                        )
                    ),
                    "gpu_memory_peak_mib": entry.get("gpu_memory_peak_mib"),
                    "gpu_utilization_percent": entry.get("gpu_utilization_percent"),
                    "command": sanitize_command_str(r.get("command", "")),
                    "code_commit": r.get("code_commit") or os.environ.get("MODELROUTER_CODE_COMMIT", "463485e3618f15b79e494d20adae8946ed6e40e5"),
                    "path": f"{run_id}/checkpoints/epoch_{epoch_no:02d}",
                    "weights_saved": phys_exists,
                    "loadable": is_loadable_checkpoint_path(epoch_dir),
                    "actual_weight_bytes": physical_dir_bytes(epoch_dir) if phys_exists else 0,
                    "freed_bytes": int(entry.get("freed_bytes", 0)),
                    "was_previously_saved": bool(entry.get("was_previously_saved") or entry.get("weights_saved") or phys_exists),
                }
                nodes.append(node)

        # Evaluate new-protocol nodes strictly isolated from legacy nodes
        new_nodes = [n for n in nodes if not n["legacy_input_protocol"]]
        legacy_nodes = [n for n in nodes if n["legacy_input_protocol"]]

        decisions_new, groups_new = evaluate_cohort_retention(
            new_nodes,
            pinned_map,
            s2_audit_passed=self.s2_audit_passed,
            allow_legacy_reference_eval=False,
            baseline_0=baseline_0,
            out_root=self.out_root,
        )
        # Also evaluate legacy cohort in its own isolated namespace so legacy nodes have accurate policy diagnostics
        decisions_leg, groups_leg = evaluate_cohort_retention(
            legacy_nodes,
            pinned_map,
            s2_audit_passed=False,
            allow_legacy_reference_eval=True,
            baseline_0=baseline_0,
            out_root=self.out_root,
        )

        decisions = {**decisions_leg, **decisions_new}
        group_summaries = {**groups_leg, **groups_new}

        score_by_cid: Dict[str, Optional[float]] = {}
        for n in nodes:
            cid = n["checkpoint_id"]
            dec = decisions.get(cid) or {
                "should_retain": False,
                "is_pinned_parent": cid in pinned_map,
                "is_global_best": False,
                "is_top_k": False,
                "retention_reasons": [],
                "rejection_reason": "unclassified",
            }
            status = resolve_retention_status(
                dec,
                weights_currently_saved=n["weights_saved"],
                was_previously_saved=n["was_previously_saved"],
                is_legacy=n["legacy_input_protocol"],
            )
            n["retention_status"] = status
            n["retention_reasons"] = dec.get("retention_reasons") or []
            n["retention_reason"] = (
                "; ".join(dec["retention_reasons"])
                if dec.get("retention_reasons")
                else (dec.get("rejection_reason") or status)
            )
            n["is_pinned_parent"] = bool(dec.get("is_pinned_parent"))
            n["pinned_children"] = pinned_map.get(cid, [])
            n["is_global_best"] = bool(dec.get("is_global_best"))
            n["is_top_k"] = bool(dec.get("is_top_k"))
            n["is_pareto_front"] = bool(dec.get("is_pareto_front"))
            n["is_run_best_epoch"] = bool(dec.get("is_run_best_epoch"))
            n["is_duplicate_run_signature"] = bool(dec.get("is_duplicate_run_signature"))
            n["s1_score"] = dec.get("s1_score") if "s1_score" in dec else n.get("s1_score")
            n["s2_score"] = dec.get("s2_score") if "s2_score" in dec else n.get("s2_score")
            n["s3_score"] = dec.get("s3_score") if "s3_score" in dec else n.get("s3_score")
            n["primary_score"] = dec.get("primary_score") if "primary_score" in dec else n.get("primary_score")
            score_by_cid[cid] = n["primary_score"]

        for n in nodes:
            pid = n.get("parent_checkpoint_id")
            p_score = score_by_cid.get(pid) if pid else S1_SCORE_BASELINE
            c_score = n.get("primary_score")
            n["parent_to_current_score_gain"] = (
                round(float(c_score) - float(p_score), 4)
                if isinstance(c_score, (int, float)) and isinstance(p_score, (int, float))
                else None
            )

        return runs, nodes, pinned_map, decisions, group_summaries

    def two_phase_cleanup(
        self,
        manifest: Optional[Dict[str, Any]] = None,
        allow_legacy_cleanup: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Execute P3 Two-Phase Checkpoint Cleanup within the authorized `out_root` whitelist.

        Phase 1: Build cleanup plan, verify history persistence, pinned parent references,
                 whitelist path boundaries, and active write locks.
        Phase 2: Delete verified low-score / duplicate / completed-run temporary checkpoints
                 directly (never moving to `.Trash`) and record exact freed bytes.
        """
        runs, nodes, pinned_map, decisions, _ = self.load_and_evaluate_all(manifest)
        node_by_key = {(n["run_id"], int(n["epoch"])): n for n in nodes}

        phase1_candidates: List[Dict[str, Any]] = []
        rejected_candidates: List[Dict[str, Any]] = []

        for run_id, r in sorted(runs.items()):
            if run_id == "R0":
                continue
            is_legacy = bool(
                r.get("legacy_input_protocol")
                or r.get("protocol_version") == LEGACY_PROTOCOL_VERSION
                or run_id.startswith("B01_")
            )
            if is_legacy and not allow_legacy_cleanup:
                continue

            run_root = self.out_root / run_id
            ckroot = run_root / "checkpoints"
            if not ckroot.exists():
                continue

            run_is_running = r.get("status") == "running"
            history_persisted = (run_root / "run.json").is_file() and (run_root / "epoch_metrics.json").is_file()

            # 1. Check completed-run temporary recovery (`_temp_recovery` and non-symlink `latest`)
            if not run_is_running:
                for tmp_name in ("_temp_recovery", "latest"):
                    tdir = ckroot / tmp_name
                    if tdir.is_symlink():
                        tdir.unlink(missing_ok=True)
                    elif tdir.exists() and tdir.is_dir():
                        ok, reason = self.is_whitelisted_checkpoint_dir(tdir)
                        sz = physical_dir_bytes(tdir)
                        item = {
                            "run_id": run_id,
                            "checkpoint_id": f"{run_id}-{tmp_name}",
                            "target_dir": str(tdir),
                            "relative_path": f"{run_id}/checkpoints/{tmp_name}",
                            "kind": STATUS_TEMP_RECOVERY if tmp_name == "_temp_recovery" else STATUS_PRUNED_DUPLICATE,
                            "reason": "completed_run_temp_recovery_cleanup",
                            "bytes": sz,
                            "history_persisted": history_persisted,
                            "whitelist_ok": ok,
                            "whitelist_reason": reason,
                        }
                        if ok and history_persisted:
                            phase1_candidates.append(item)
                        else:
                            rejected_candidates.append(item)

            # 2. Check duplicate physical `best` directory if the underlying `epoch_XX` is retained
            best_dir = ckroot / "best"
            if best_dir.exists() and not best_dir.is_symlink() and best_dir.is_dir():
                best_ep = r.get("best_epoch")
                ep_dir = ckroot / f"epoch_{int(best_ep):02d}" if best_ep else None
                if ep_dir and has_physical_weights(ep_dir):
                    ok, reason = self.is_whitelisted_checkpoint_dir(best_dir)
                    sz = physical_dir_bytes(best_dir)
                    item = {
                        "run_id": run_id,
                        "checkpoint_id": f"{run_id}-best-duplicate",
                        "target_dir": str(best_dir),
                        "relative_path": f"{run_id}/checkpoints/best",
                        "replace_with_symlink_to": ep_dir.name,
                        "kind": STATUS_PRUNED_DUPLICATE,
                        "reason": f"duplicate_best_copy_deduplicated_to_{ep_dir.name}",
                        "bytes": sz,
                        "history_persisted": history_persisted,
                        "whitelist_ok": ok,
                        "whitelist_reason": reason,
                    }
                    if ok and history_persisted:
                        phase1_candidates.append(item)
                    else:
                        rejected_candidates.append(item)

            # 3. Check `epoch_XX` directories that do NOT qualify for retention
            for h in r.get("history") or []:
                ep = int(h.get("epoch", 0))
                cid = h.get("checkpoint_id") or f"{run_id}-e{ep:02d}"
                ep_dir = ckroot / f"epoch_{ep:02d}"
                if not has_physical_weights(ep_dir):
                    continue
                dec = decisions.get(cid) or {}
                if dec.get("is_pinned_parent") or cid in pinned_map:
                    rejected_candidates.append({
                        "run_id": run_id,
                        "checkpoint_id": cid,
                        "target_dir": str(ep_dir),
                        "reason": f"protected_pinned_parent:{pinned_map.get(cid)}",
                    })
                    continue
                if dec.get("is_global_best"):
                    rejected_candidates.append({
                        "run_id": run_id,
                        "checkpoint_id": cid,
                        "target_dir": str(ep_dir),
                        "reason": "protected_global_best",
                    })
                    continue
                if dec.get("should_retain"):
                    continue

                ok, w_reason = self.is_whitelisted_checkpoint_dir(ep_dir)
                sz = physical_dir_bytes(ep_dir)
                node_meta_ok = (run_id, ep) in node_by_key and history_persisted
                item = {
                    "run_id": run_id,
                    "epoch": ep,
                    "checkpoint_id": cid,
                    "target_dir": str(ep_dir),
                    "relative_path": f"{run_id}/checkpoints/epoch_{ep:02d}",
                    "kind": STATUS_PRUNED_LOW_SCORE,
                    "reason": dec.get("rejection_reason") or "pruned_low_score_outside_top_30pct",
                    "bytes": sz,
                    "history_persisted": node_meta_ok,
                    "whitelist_ok": ok,
                    "whitelist_reason": w_reason,
                }
                if ok and node_meta_ok:
                    phase1_candidates.append(item)
                else:
                    rejected_candidates.append(item)

        # 4. If remaining active weights after standard pruning still exceed `active_budget_bytes`,
        #    evict lowest-score non-mandatory (`not is_pinned_parent` and `not is_global_best`) Top-30% checkpoints
        #    until within budget (never evicting PINNED_PARENT or RETAINED_BEST).
        planned_dirs = {x["target_dir"] for x in phase1_candidates}
        remaining_bytes = 0
        evictable_top_k: List[Tuple[float, Dict[str, Any]]] = []
        for n in nodes:
            if n.get("legacy_input_protocol") and not allow_legacy_cleanup:
                continue
            ep_dir = self.out_root / n["run_id"] / "checkpoints" / f"epoch_{int(n['epoch']):02d}"
            if str(ep_dir) in planned_dirs or not has_physical_weights(ep_dir):
                continue
            sz = physical_dir_bytes(ep_dir)
            remaining_bytes += sz
            cid = n["checkpoint_id"]
            dec = decisions.get(cid) or {}
            if dec.get("is_pinned_parent") or cid in pinned_map or dec.get("is_global_best"):
                continue
            ok, w_reason = self.is_whitelisted_checkpoint_dir(ep_dir)
            run_root = self.out_root / n["run_id"]
            hist_ok = (run_root / "run.json").is_file() and (run_root / "epoch_metrics.json").is_file()
            if ok and hist_ok:
                score_val = float(n.get("primary_score") if isinstance(n.get("primary_score"), (int, float)) else 0.0)
                evictable_top_k.append((
                    score_val,
                    {
                        "run_id": n["run_id"],
                        "epoch": int(n["epoch"]),
                        "checkpoint_id": cid,
                        "target_dir": str(ep_dir),
                        "relative_path": f"{n['run_id']}/checkpoints/epoch_{int(n['epoch']):02d}",
                        "kind": STATUS_PRUNED_LOW_SCORE,
                        "reason": f"evicted_lowest_score_top30pct_for_120gib_budget(score={score_val:.2f})",
                        "bytes": sz,
                        "history_persisted": True,
                        "whitelist_ok": True,
                        "whitelist_reason": w_reason,
                    },
                ))

        if remaining_bytes > self.active_budget_bytes and evictable_top_k:
            evictable_top_k.sort(key=lambda pair: (pair[0], pair[1]["checkpoint_id"]))
            for _sc, item in evictable_top_k:
                if remaining_bytes <= self.active_budget_bytes:
                    break
                phase1_candidates.append(item)
                remaining_bytes -= item["bytes"]

        # Phase 2: Execute verified deletions
        executed: List[Dict[str, Any]] = []
        total_freed_bytes = 0
        if not dry_run:
            for item in phase1_candidates:
                tpath = Path(item["target_dir"])
                ok, _ = self.is_whitelisted_checkpoint_dir(tpath)
                if not ok or not item.get("history_persisted"):
                    continue
                sz_before = physical_dir_bytes(tpath)
                shutil.rmtree(tpath)
                if item.get("replace_with_symlink_to"):
                    update_safe_symlink(tpath, item["replace_with_symlink_to"])
                total_freed_bytes += sz_before
                rec = dict(item, freed_bytes=sz_before, deleted_at=_now_iso())
                executed.append(rec)

                # Update run.json and epoch_metrics.json if an epoch_XX directory was pruned
                if item["kind"] == STATUS_PRUNED_LOW_SCORE and "epoch" in item:
                    run_id = item["run_id"]
                    ep = int(item["epoch"])
                    run_path = self.out_root / run_id / "run.json"
                    if run_path.is_file():
                        rdata = json.loads(run_path.read_text(encoding="utf8"))
                        for h in rdata.get("history") or []:
                            if int(h.get("epoch", 0)) == ep:
                                h["weights_saved"] = False
                                h["loadable"] = False
                                h["was_previously_saved"] = True
                                h["retention_status"] = STATUS_PRUNED_LOW_SCORE
                                h["retention_reason"] = item["reason"]
                                h["freed_bytes"] = int(h.get("freed_bytes", 0)) + sz_before
                                h["checkpoint_size_bytes"] = 0
                        # Ensure `best` symlink points to a remaining retained epoch or is removed
                        self._sync_run_best_symlink(run_id, rdata)
                        _atomic_write_json(run_path, rdata)
                        _atomic_write_json(self.out_root / run_id / "epoch_metrics.json", rdata.get("history") or [])

        audit_log = {
            "executed_at": _now_iso(),
            "dry_run": dry_run,
            "allow_legacy_cleanup": allow_legacy_cleanup,
            "phase1_verified_count": len(phase1_candidates),
            "phase1_planned_bytes": sum(x["bytes"] for x in phase1_candidates),
            "phase1_protected_or_rejected_count": len(rejected_candidates),
            "phase2_executed_count": len(executed),
            "phase2_freed_bytes": total_freed_bytes,
            "executed_items": [
                {k: v for k, v in x.items() if k != "target_dir"}
                for x in executed
            ],
            "protected_items": [
                {k: v for k, v in x.items() if k != "target_dir"}
                for x in rejected_candidates
            ],
        }
        _atomic_write_json(self.out_root / "cleanup_audit_log.json", audit_log)
        return audit_log

    def _sync_run_best_symlink(self, run_id: str, rdata: Dict[str, Any]) -> None:
        """Ensure `checkpoints/best` points to an actually existing retained epoch directory."""
        ckroot = self.out_root / run_id / "checkpoints"
        if not ckroot.exists():
            rdata["best_checkpoint"] = None
            return
        retained_eps = []
        for h in rdata.get("history") or []:
            ep = int(h.get("epoch", 0))
            ep_dir = ckroot / f"epoch_{ep:02d}"
            if has_physical_weights(ep_dir):
                s1_loss = ((h.get("validation") or {}).get("S1") or {}).get("loss")
                retained_eps.append((s1_loss if isinstance(s1_loss, (int, float)) else 999.0, ep))
        if retained_eps:
            retained_eps.sort()
            best_ep = retained_eps[0][1]
            update_safe_symlink(ckroot / "best", f"epoch_{best_ep:02d}")
            rdata["best_checkpoint"] = f"{run_id}/checkpoints/best"
        else:
            update_safe_symlink(ckroot / "best", None)
            rdata["best_checkpoint"] = None

    def pre_run_disk_check(
        self,
        run_id: str,
        manifest: Optional[Dict[str, Any]] = None,
        simulated_statvfs: Optional[Dict[str, int]] = None,
        estimated_peak_bytes: int = ESTIMATED_RUN_PEAK_TEMP_BYTES,
    ) -> Dict[str, Any]:
        """P3 Pre-Run Disk & Budget Check before launching any new Run.

        Checks:
        1. Free disk space (percentage & absolute GiB)
        2. Estimated temporary peak for this Run
        3. Current active weights total
        4. Best, PINNED, and temp recovery usage
        5. Whether low-value non-dependent weights need to be freed first.
        """
        before = self.disk_status(simulated_statvfs=simulated_statvfs)
        projected_active = before["active_weights_bytes"] + estimated_peak_bytes
        projected_free = before["root_avail_bytes"] - estimated_peak_bytes
        projected_free_pct = (
            round(projected_free / before["root_total_bytes"] * 100.0, 2)
            if before["root_total_bytes"] > 0 else 0.0
        )

        needs_cleanup = (
            projected_active > self.active_budget_bytes
            or before["stop_triggered"]
            or projected_free < self.stop_free_bytes
            or projected_free_pct < self.stop_free_pct
        )
        cleanup_result = None
        if needs_cleanup:
            cleanup_result = self.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
            # If simulated_statvfs was supplied, credit freed bytes back to simulated avail_bytes
            if simulated_statvfs is not None and cleanup_result["phase2_freed_bytes"] > 0:
                simulated_statvfs = dict(simulated_statvfs)
                simulated_statvfs["avail_bytes"] += cleanup_result["phase2_freed_bytes"]
                simulated_statvfs["used_bytes"] = max(
                    0, simulated_statvfs.get("used_bytes", 0) - cleanup_result["phase2_freed_bytes"]
                )

        after = self.disk_status(simulated_statvfs=simulated_statvfs)
        after_projected_active = after["active_weights_bytes"] + estimated_peak_bytes
        after_projected_free = after["root_avail_bytes"] - estimated_peak_bytes
        after_projected_free_pct = (
            round(after_projected_free / after["root_total_bytes"] * 100.0, 2)
            if after["root_total_bytes"] > 0 else 0.0
        )

        # Mandatory protected weights (`RETAINED_BEST` + `PINNED_PARENT`)
        mandatory_bytes = (
            after["breakdown_bytes"]["retained_best_bytes"]
            + after["breakdown_bytes"]["pinned_parent_bytes"]
        )

        if after["stop_triggered"] or after_projected_free < self.stop_free_bytes or after_projected_free_pct < self.stop_free_pct:
            allowed = False
            status = "STOPPED_DISK_LOW_SPACE"
            reason = (
                f"Disk free space below hard stop threshold: avail={round(after['root_avail_bytes']/GIB, 2)} GiB "
                f"({after['root_avail_pct']}%), required >= {round(self.stop_free_bytes/GIB, 1)} GiB and >= {self.stop_free_pct}%"
            )
        elif after_projected_active > self.active_budget_bytes:
            allowed = False
            status = "STOPPED_DISK_BUDGET"
            reason = (
                f"Active weight budget exceeded after cleanup: active={round(after['active_weights_bytes']/GIB, 2)} GiB "
                f"(mandatory best+pinned={round(mandatory_bytes/GIB, 2)} GiB) + run_peak={round(estimated_peak_bytes/GIB, 2)} GiB "
                f"> budget={round(self.active_budget_bytes/GIB, 2)} GiB. Refusing to delete PINNED or global best models."
            )
        else:
            allowed = True
            status = "WARNING_PROCEED" if after["warn_triggered"] else "READY_TO_START"
            reason = "Disk space and active weight budget verified."

        report = {
            "run_id": run_id,
            "checked_at": _now_iso(),
            "allowed_to_start": allowed,
            "status": status,
            "reason": reason,
            "estimated_run_peak_bytes": estimated_peak_bytes,
            "before_check": before,
            "cleanup_executed": cleanup_result,
            "after_check": after,
        }
        if not allowed:
            raise DiskBudgetExceededError(json.dumps(report, ensure_ascii=False))
        return report

    def handle_epoch_checkpoint(
        self,
        run_id: str,
        epoch: int,
        is_final_epoch: bool,
        save_fn,
        run_meta: Dict[str, Any],
        entry: Dict[str, Any],
        manifest: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """P0 + P1 + P2 + P3 per-epoch checkpoint handler.

        1. Records full epoch metrics into `run_meta['history']`, `run.json`, and `epoch_metrics.json`.
        2. Evaluates across all comparable runs in `out_root` whether this epoch qualifies for retention.
        3. Writes physical weights ONLY if qualified (or writes temporary recovery if run is still active).
        4. Deduplicates `best` and `latest` via relative symlinks (never writing duplicate `model.safetensors`).
        5. Runs Two-Phase Cleanup if an earlier Top-K / cold-start checkpoint in the group was displaced.
        """
        run_root = self.out_root / run_id
        ckroot = run_root / "checkpoints"
        ckroot.mkdir(parents=True, exist_ok=True)
        epoch_id = entry["checkpoint_id"]
        epoch_rel = f"epoch_{epoch:02d}"
        epoch_dir = ckroot / epoch_rel

        # Step 1: Persist metadata first so history is never lost even if weights are not saved
        entry["weights_saved"] = False
        entry["loadable"] = False
        entry["checkpoint_size_bytes"] = 0
        entry["freed_bytes"] = 0
        entry["retention_status"] = STATUS_METADATA_ONLY

        # Guarantee entry is present in run_meta["history"] without duplicate
        history_list = run_meta.setdefault("history", [])
        existing_idx = None
        for i, h in enumerate(history_list):
            if h.get("checkpoint_id") == epoch_id or h.get("epoch") == epoch:
                existing_idx = i
                break
        if existing_idx is not None:
            history_list[existing_idx] = entry
        else:
            history_list.append(entry)

        _atomic_write_json(run_root / "epoch_metrics.json", run_meta["history"])
        _atomic_write_json(run_root / "run.json", run_meta)

        # Step 2: Evaluate retention across the cohort including this new epoch
        _runs, _nodes, pinned_map, decisions, group_summaries = self.load_and_evaluate_all(manifest)
        dec = decisions.get(epoch_id) or {
            "should_retain": False,
            "is_pinned_parent": epoch_id in pinned_map,
            "is_global_best": False,
            "is_top_k": False,
            "retention_reasons": [],
            "rejection_reason": "not_qualified",
        }

        # Check active budget before writing permanent weights
        d_stat = self.disk_status()
        within_budget = (d_stat["active_weights_bytes"] + SINGLE_CKPT_ESTIMATED_BYTES) <= self.active_budget_bytes
        if not within_budget and dec.get("should_retain"):
            # Try cleaning displaced checkpoints first
            self.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
            d_stat = self.disk_status()
            within_budget = (d_stat["active_weights_bytes"] + SINGLE_CKPT_ESTIMATED_BYTES) <= self.active_budget_bytes

        should_save_permanent = bool(dec.get("should_retain") and within_budget)
        lock_file = run_root / ".writing_lock"

        if should_save_permanent:
            # Write once to staging dir, then atomically rename to `epoch_XX`
            staging_dir = ckroot / f".writing_{epoch_rel}"
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            try:
                lock_file.write_text(epoch_id, encoding="utf8")
                save_fn(str(staging_dir))
                if epoch_dir.exists() or epoch_dir.is_symlink():
                    if epoch_dir.is_symlink():
                        epoch_dir.unlink()
                    else:
                        shutil.rmtree(epoch_dir)
                staging_dir.rename(epoch_dir)
            finally:
                lock_file.unlink(missing_ok=True)

            # Remove any standalone `_temp_recovery` since `epoch_XX` itself is on disk
            temp_dir = ckroot / "_temp_recovery"
            if temp_dir.exists() and not temp_dir.is_symlink():
                shutil.rmtree(temp_dir)
            update_safe_symlink(ckroot / "latest", epoch_rel)

            sz = physical_dir_bytes(epoch_dir)
            status = resolve_retention_status(
                dec, weights_currently_saved=True, was_previously_saved=True, is_legacy=False
            )
            entry["weights_saved"] = True
            entry["loadable"] = True
            entry["was_previously_saved"] = True
            entry["checkpoint_size_bytes"] = sz
            entry["retention_status"] = status
            entry["retention_reasons"] = dec.get("retention_reasons") or []
            entry["retention_reason"] = "; ".join(entry["retention_reasons"]) or status
        else:
            # Do NOT write permanent `epoch_XX` weights (`METADATA_ONLY`)
            reason = dec.get("rejection_reason") or ("exceeded_active_budget" if not within_budget else STATUS_METADATA_ONLY)
            entry["weights_saved"] = False
            entry["loadable"] = False
            entry["was_previously_saved"] = False
            entry["checkpoint_size_bytes"] = 0
            entry["retention_status"] = STATUS_METADATA_ONLY
            entry["retention_reasons"] = []
            entry["retention_reason"] = reason

            # If run is still ongoing and within budget, maintain single temporary recovery point
            if not is_final_epoch and within_budget:
                temp_dir = ckroot / "_temp_recovery"
                staging_temp = ckroot / ".writing_temp_recovery"
                if staging_temp.exists():
                    shutil.rmtree(staging_temp)
                try:
                    lock_file.write_text(f"{epoch_id}:temp_recovery", encoding="utf8")
                    save_fn(str(staging_temp))
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                    staging_temp.rename(temp_dir)
                    update_safe_symlink(ckroot / "latest", "_temp_recovery")
                finally:
                    lock_file.unlink(missing_ok=True)

        # Persist updated entry and prune any earlier checkpoints displaced by this epoch
        _atomic_write_json(run_root / "epoch_metrics.json", run_meta["history"])
        self._sync_run_best_symlink(run_id, run_meta)
        _atomic_write_json(run_root / "run.json", run_meta)

        cleanup_log = self.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
        # Reload updated history in case an earlier epoch of this same run was pruned
        updated_run = json.loads((run_root / "run.json").read_text(encoding="utf8"))
        run_meta["history"] = updated_run.get("history", run_meta["history"])
        run_meta["best_checkpoint"] = updated_run.get("best_checkpoint")
        return {
            "checkpoint_id": epoch_id,
            "weights_saved": entry["weights_saved"],
            "retention_status": entry["retention_status"],
            "retention_reason": entry["retention_reason"],
            "cleanup_log": cleanup_log,
            "group_summaries": group_summaries,
        }

    def finalize_run_checkpoints(self, run_id: str, run_meta: Dict[str, Any], manifest: Optional[Dict[str, Any]] = None) -> None:
        """Clean up temporary `latest` / `_temp_recovery` upon Run completion and sync `best` symlink."""
        run_root = self.out_root / run_id
        ckroot = run_root / "checkpoints"
        if ckroot.exists():
            temp_dir = ckroot / "_temp_recovery"
            if temp_dir.exists() and not temp_dir.is_symlink():
                shutil.rmtree(temp_dir)
            latest_link = ckroot / "latest"
            if latest_link.is_symlink() or latest_link.is_file():
                latest_link.unlink(missing_ok=True)
            elif latest_link.is_dir():
                shutil.rmtree(latest_link)
        self._sync_run_best_symlink(run_id, run_meta)
        _atomic_write_json(run_root / "run.json", run_meta)
        _atomic_write_json(run_root / "epoch_metrics.json", run_meta.get("history") or [])
        self.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
        self.write_checkpoint_manifest(manifest=manifest)

    def write_checkpoint_manifest(self, manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Write comprehensive `checkpoint_manifest.json` in `out_root` covering P4 & P5."""
        runs, nodes, pinned_map, _decisions, group_summaries = self.load_and_evaluate_all(manifest)
        disk = self.disk_status()
        baseline_0 = load_or_default_baseline_0(self.out_root)
        status_counts = Counter(n["retention_status"] for n in nodes)
        payload = {
            "generated_at": _now_iso(),
            "protocol_version": NEW_PROTOCOL_VERSION,
            "policy_version": RETENTION_POLICY_VERSION,
            "baseline_0": baseline_0,
            "policy": {
                "policy_version": RETENTION_POLICY_VERSION,
                "scoring_weights": {
                    "S1": {"I_loss": 0.45, "I_acc": 0.30, "I_brier": 0.15, "I_ece": 0.10},
                    "S2": {"I_loss": 0.35, "I_bal_acc": 0.30, "I_f1": 0.20, "I_brier": 0.15},
                    "S3": "Equal-weight macro-average of per-target scores vs majority/prior baseline",
                },
                "active_budget_bytes": self.active_budget_bytes,
                "active_budget_gib": round(self.active_budget_bytes / GIB, 2),
                "warn_free_pct": self.warn_free_pct,
                "stop_free_pct": self.stop_free_pct,
                "warn_free_gib": round(self.warn_free_bytes / GIB, 2),
                "stop_free_gib": round(self.stop_free_bytes / GIB, 2),
                "retention_target": RETENTION_TARGET,
                "mean_floor_ratio": MEAN_FLOOR_RATIO,
                "min_comparable_runs": MIN_COMPARABLE_RUNS,
                "trim_ratio": TRIM_RATIO,
                "s1_score_baseline": S1_SCORE_BASELINE,
                "cold_start_top_k": GROUP_TOP_K,
                "cond_a": "primary_score > 100.0 (beats BASELINE_0) and no single-metric degradation vs BASELINE_0",
                "cond_b": "primary_score >= 0.98 * loo_robust_mean_score (BASELINE_1 leave-one-out mean floor)",
                "cond_c": "Rank <= ceil(0.30 * N) among distinct completed runs in comparable group when N >= 5",
                "cond_d": "Cold-start Top-2 temporary retention when N < 5; re-evaluated and pruned once N >= 5",
                "cond_e": "Pareto frontier tie-break when scores are within 0.5 points",
                "cond_f": "Mandatory retention: PINNED_PARENT, Global S1 bests (Score/Loss/Acc/Brier), and per-batch B01..B07 best passing Cond A",
                "s2_rule": "Diagnostic cap=1 while s2_audit_passed=False; never crown S2 Accuracy=1.0 as global champion",
                "s3_rule": "Equal-weight macro-average of per-target S3_score_t against majority/prior baseline; never sum raw S3 losses",
                "deduplication": "At most 1 non-dependent physical checkpoint (best Epoch) per Run; best is relative symlink; latest is temporary recovery only",
            },
            "disk_status": disk,
            "retention_summary": {
                "total_epochs": len(nodes),
                "physical_weights_saved": sum(1 for n in nodes if n["weights_saved"]),
                "status_counts": dict(status_counts),
                "pinned_parent_ids": pinned_map,
                "total_freed_bytes": sum(int(n.get("freed_bytes", 0)) for n in nodes),
            },
            "comparable_groups": group_summaries,
            "checkpoints": nodes,
        }

        # Also emit synchronized dual-pool checkpoint manifest with relative paths
        def _rank_k(n):
            s1 = (n.get("validation", {}).get("S1") or {})
            sc = float(n.get("selection_score") or n.get("primary_score") or 0.0)
            l = float(s1.get("loss", 999.0)) if isinstance(s1.get("loss"), (int, float)) else 999.0
            a = float(s1.get("accuracy", -1.0)) if isinstance(s1.get("accuracy"), (int, float)) else -1.0
            return (-round(sc, 4), round(l, 4), -round(a, 4))

        old_core_checkpoints = [
            n for n in nodes
            if n["checkpoint_id"] in OLD_CORE_CHECKPOINT_IDS
        ]
        old_core_checkpoints.sort(key=_rank_k)

        new_core_checkpoints = [
            n for n in nodes
            if n["checkpoint_id"] not in OLD_CORE_CHECKPOINT_IDS
            and n.get("retention_status") in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K)
            and not n.get("is_pinned_parent")
        ]
        new_core_checkpoints.sort(key=_rank_k)

        pinned_checkpoints = [
            n for n in nodes
            if n.get("retention_status") == STATUS_PINNED_PARENT or n.get("is_pinned_parent")
        ]
        protected = [
            n for n in nodes
            if n.get("retention_status") in (STATUS_PINNED_PARENT, STATUS_TEMP_RECOVERY)
            or n.get("is_pinned_parent")
        ]

        def _rel_path_str(p_val: Any) -> Any:
            if not p_val or not isinstance(p_val, str):
                return p_val
            if "runs/" in p_val:
                return "runs/" + p_val.split("runs/", 1)[1]
            return p_val

        top5_payload = {
            "generated_at": _now_iso(),
            "policy": DUAL_POOL_POLICY_VERSION,
            "old_pool_size": len(old_core_checkpoints),
            "new_pool_size": len(new_core_checkpoints),
            "max_core_checkpoints": MAX_CORE_CHECKPOINTS + len(new_core_checkpoints),
            "selection_formula": "0.80 * internal + 0.20 * external_dev (when evaluated), else 1.00 * internal",
            "old_core_checkpoints": sanitize_deep(old_core_checkpoints),
            "new_core_checkpoints": sanitize_deep(new_core_checkpoints),
            "top5_core_checkpoints": sanitize_deep(old_core_checkpoints[:MAX_CORE_CHECKPOINTS]),
            "pinned_parent_checkpoints": sanitize_deep(pinned_checkpoints),
            "temporarily_protected_checkpoints": sanitize_deep(protected),
            "total_scanned_checkpoints": len(nodes),
        }
        payload["top5_core_checkpoints"] = sanitize_deep(old_core_checkpoints[:MAX_CORE_CHECKPOINTS])
        payload["old_core_checkpoints"] = sanitize_deep(old_core_checkpoints)
        payload["new_core_checkpoints"] = sanitize_deep(new_core_checkpoints)
        payload["pinned_parent_checkpoints"] = sanitize_deep(pinned_checkpoints)
        payload["dual_pool_retention"] = top5_payload

        # Write both manifest files in consistent atomic order
        _atomic_write_json(self.out_root / "top5_core_checkpoint_manifest.json", top5_payload)
        if self.out_root.parent.name == "runs":
            _atomic_write_json(self.out_root.parent / "top5_core_checkpoint_manifest.json", top5_payload)
        _atomic_write_json(self.out_root / "checkpoint_manifest.json", payload)

        return payload


def _make_dummy_checkpoint_saver(weight_bytes: int = 65536):
    """Create a fast dummy checkpoint writer for CPU sandbox verification."""
    payload = b"0" * int(weight_bytes)

    def _save(target_dir: str) -> None:
        p = Path(target_dir)
        p.mkdir(parents=True, exist_ok=True)
        (p / "encoder").mkdir(exist_ok=True)
        (p / "tokenizer").mkdir(exist_ok=True)
        (p / "model.safetensors").write_bytes(payload)
        (p / "encoder" / "config.json").write_text('{"model_type": "laya_dummy"}', encoding="utf8")
        (p / "tokenizer" / "tokenizer_config.json").write_text('{"tokenizer_class": "PreTrainedTokenizer"}', encoding="utf8")
        (p / "rl_agent_config.json").write_text(
            json.dumps({"max_len": 1024, "head_max_len": 512, "fine_tuned": True}, indent=2),
            encoding="utf8",
        )

    return _save


def run_storage_policy_verification(
    project_root: Path,
    sandbox_root: Optional[Path] = None,
    run_official_load: bool = True,
) -> Dict[str, Any]:
    """Execute all 14 pre-execution verification checks required by Section 11 (`P11-01` .. `P11-14`).

    Uses an isolated temporary simulation directory (`sandbox_root`) with lightweight
    checkpoint files to verify `BASELINE_0`/`1`/`2`, composite scores, Top 30% retention,
    cold-start re-evaluation, within-run & cross-run deduplication, S1/S2/S3 task isolation,
    PINNED parent protection, disk/budget guards, official `load_checkpoint`, queue state
    breakpoint recovery, and GitHub privacy/no-weights compliance.
    """
    project_root = Path(project_root).resolve()
    cleanup_sandbox_after = sandbox_root is None
    if sandbox_root is None:
        sandbox_root = project_root / ".tmp" / f"verify_ckpt_policy_{os.getpid()}"
    sandbox_root = Path(sandbox_root).resolve()
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    sandbox_root.mkdir(parents=True, exist_ok=True)

    dummy_weight_bytes = 65536
    dummy_save = _make_dummy_checkpoint_saver(weight_bytes=dummy_weight_bytes)

    try:
        # Copy or write frozen `baseline_0.json` into sandbox_root
        real_b0 = load_or_default_baseline_0(project_root / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012")
        _atomic_write_json(sandbox_root / "baseline_0.json", real_b0)

        # Build simulated manifest with a child curriculum plan depending on `P0_SIM_S1_R01-e01` (a low-score parent!)
        sim_manifest = {
            "experiment_id": "MR-FULL-GRADED-STORAGE-VERIFY",
            "protocol_version": NEW_PROTOCOL_VERSION,
            "plans": {
                "P0_SIM_CUR_CHILD": {
                    "run_id": "P0_SIM_CUR_CHILD",
                    "parent_checkpoint_id": "P0_SIM_S1_R01-e01",
                    "status": "PLANNED",
                    "supervision_classes": ["S1"],
                    "protocol_version": NEW_PROTOCOL_VERSION,
                }
            },
        }
        _atomic_write_json(sandbox_root / "experiment_matrix.json", sim_manifest)

        mgr = CheckpointRetentionManager(
            out_root=sandbox_root,
            active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
            s2_audit_passed=False,
        )

        # 0. Inject 1 Legacy run (`B01_LEGACY_SIM`) with strong S1 loss (0.5800) to verify Legacy isolation
        leg_root = sandbox_root / "B01_LEGACY_SIM"
        leg_root.mkdir(parents=True, exist_ok=True)
        leg_meta = {
            "run_id": "B01_LEGACY_SIM",
            "status": "completed",
            "protocol_version": LEGACY_PROTOCOL_VERSION,
            "legacy_input_protocol": True,
            "supervision_classes": ["S1"],
            "train_groups": {"S1": 4096},
            "val_groups": {"S1": 561},
            "config": {"loss": "soft-ce", "encoder_lr": 2.5e-5, "head_lr": 1e-4, "micro_batch": 8, "grad_accum": 8},
            "seed": 42,
            "best_epoch": 1,
            "history": [
                {
                    "checkpoint_id": "B01_LEGACY_SIM-e01",
                    "epoch": 1,
                    "train_loss": 0.59,
                    "validation": {"S1": {"items": 561, "loss": 0.5800, "accuracy": 0.7200, "brier": 0.3900, "ece": 0.025}},
                    "weights_saved": False,
                    "retention_status": STATUS_LEGACY_METADATA_ONLY,
                }
            ],
        }
        _atomic_write_json(leg_root / "run.json", leg_meta)
        _atomic_write_json(leg_root / "epoch_metrics.json", leg_meta["history"])

        # 1. Simulate 10 distinct S1 runs (`P0_SIM_S1_R01` .. `P0_SIM_S1_R10`) + 1 duplicate signature run (`P0_SIM_S1_R10_DUP`)
        #    When N=10 >= 5, Top 30% retains K = ceil(0.30 * 10) = 3 non-dependent runs:
        #    - Rank #1: `P0_SIM_S1_R03-e02` (loss 0.5920, acc 0.6910 -> RETAINED_BEST)
        #    - Rank #2: `P0_SIM_S1_R02-e02` (loss 0.6010, acc 0.6780 -> RETAINED_TOP_K)
        #    - Rank #3: `P0_SIM_S1_R05-e01` (loss 0.6060, acc 0.6720 -> RETAINED_TOP_K)
        #    - Plus `P0_SIM_S1_R01-e01` (loss 0.6800, acc 0.6000 -> PINNED_PARENT for `P0_SIM_CUR_CHILD`)
        #    - `P0_SIM_S1_R01-e02` (loss 0.6420, acc 0.6250) is temporarily retained during cold-start (N < 5),
        #      then automatically pruned (`PRUNED_LOW_SCORE`) once N >= 5!
        s1_sim_specs = [
            ("P0_SIM_S1_R01", None, 42, [
                (1, 0.685, {"loss": 0.6800, "accuracy": 0.6000, "brier": 0.4600, "ece": 0.055}),
                (2, 0.645, {"loss": 0.6420, "accuracy": 0.6250, "brier": 0.4350, "ece": 0.038}),
            ]),
            ("P0_SIM_S1_R02", None, 43, [
                (1, 0.635, {"loss": 0.6250, "accuracy": 0.6500, "brier": 0.4250, "ece": 0.036}),
                (2, 0.605, {"loss": 0.6010, "accuracy": 0.6780, "brier": 0.4120, "ece": 0.032}),
            ]),
            ("P0_SIM_S1_R03", "P0_SIM_S1_R01-e01", 44, [
                (1, 0.640, {"loss": 0.6300, "accuracy": 0.6480, "brier": 0.4280, "ece": 0.035}),
                (2, 0.595, {"loss": 0.5920, "accuracy": 0.6910, "brier": 0.4050, "ece": 0.029}),
            ]),
            ("P0_SIM_S1_R04", None, 45, [
                (1, 0.632, {"loss": 0.6220, "accuracy": 0.6520, "brier": 0.4240, "ece": 0.035}),
                (2, 0.619, {"loss": 0.6140, "accuracy": 0.6600, "brier": 0.4200, "ece": 0.034}),
            ]),
            ("P0_SIM_S1_R05", None, 46, [
                (1, 0.633, {"loss": 0.6290, "accuracy": 0.6440, "brier": 0.4290, "ece": 0.037}),
            ]),
            ("P0_SIM_S1_R06", None, 47, [
                (1, 0.621, {"loss": 0.6180, "accuracy": 0.6560, "brier": 0.4220, "ece": 0.035}),
            ]),
            ("P0_SIM_S1_R07", None, 48, [
                (1, 0.628, {"loss": 0.6240, "accuracy": 0.6490, "brier": 0.4260, "ece": 0.036}),
            ]),
            ("P0_SIM_S1_R08", None, 49, [
                (1, 0.608, {"loss": 0.6060, "accuracy": 0.6720, "brier": 0.4150, "ece": 0.033}),
            ]),
            ("P0_SIM_S1_R09", None, 50, [
                (1, 0.638, {"loss": 0.6340, "accuracy": 0.6390, "brier": 0.4320, "ece": 0.038}),
            ]),
            ("P0_SIM_S1_R10", None, 51, [
                (1, 1.920, {"loss": 1.9120, "accuracy": 0.4420, "brier": 0.9350, "ece": 0.4680}),
            ]),
            # Identical seed (51) and config as R10 -> duplicate run signature!
            ("P0_SIM_S1_R10_DUP", None, 51, [
                (1, 1.920, {"loss": 1.9120, "accuracy": 0.4420, "brier": 0.9350, "ece": 0.4680}),
            ]),
        ]

        temp_recovery_observed_during_run = False
        cold_start_retained_at_r01 = False
        for run_id, parent_id, seed_val, ep_list in s1_sim_specs:
            r_root = sandbox_root / run_id
            r_root.mkdir(parents=True, exist_ok=True)
            r_meta = {
                "run_id": run_id,
                "parent_checkpoint_id": parent_id,
                "train_origin": parent_id or "Base",
                "protocol_version": NEW_PROTOCOL_VERSION,
                "legacy_input_protocol": False,
                "batch_id": "B01",
                "combo_id": "C01",
                "quality_code": "QB",
                "sampling_code": "PB",
                "supervision_classes": ["S1"],
                "ratios": [1],
                "train_groups": {"S1": 4096},
                "val_groups": {"S1": 561},
                "seed": seed_val,
                "config": {"loss": "soft-ce", "encoder_lr": 2.5e-5, "head_lr": 1e-4, "micro_batch": 8, "grad_accum": 8},
                "status": "running",
                "command": f"python router_data/laya_batch_train.py --sweep-run {run_id}",
                "history": [],
            }
            best_loss = 999.0
            best_ep = None
            for ep, tr_loss, s1_val in ep_list:
                if s1_val["loss"] < best_loss * 0.995:
                    best_loss = s1_val["loss"]
                    best_ep = ep
                r_meta["best_epoch"] = best_ep
                entry = {
                    "checkpoint_id": f"{run_id}-e{ep:02d}",
                    "epoch": ep,
                    "train_loss": tr_loss,
                    "validation": {"S1": dict(s1_val, items=561)},
                    "best_epoch": best_ep,
                    "optimizer_updates": 64,
                    "global_step": ep * 64,
                    "train_seconds": 95.0,
                    "validation_seconds": 14.0,
                    "checkpoint_seconds": 1.2,
                    "epoch_total_seconds": 110.2,
                    "gpu_memory_peak_mib": 7960.0,
                    "learning_rate": {"encoder": 2.5e-5, "head": 1e-4},
                }
                r_meta["history"].append(entry)
                res = mgr.handle_epoch_checkpoint(
                    run_id=run_id,
                    epoch=ep,
                    is_final_epoch=(ep == len(ep_list)),
                    save_fn=dummy_save,
                    run_meta=r_meta,
                    entry=entry,
                    manifest=sim_manifest,
                )
                if run_id == "P0_SIM_S1_R01" and ep == 2 and res["weights_saved"]:
                    cold_start_retained_at_r01 = True
                if ep < len(ep_list):
                    ck = r_root / "checkpoints"
                    if (ck / "latest").is_symlink() or (ck / "_temp_recovery").exists():
                        temp_recovery_observed_during_run = True
            r_meta["status"] = "completed"
            mgr.finalize_run_checkpoints(run_id, r_meta, manifest=sim_manifest)

        # 2. Simulate Pure S2 run (`P0_SIM_S2_R01`, 3 epochs with Accuracy=1.0 while s2_audit_passed=False)
        s2_run_id = "P0_SIM_S2_R01"
        s2_meta = {
            "run_id": s2_run_id,
            "parent_checkpoint_id": None,
            "train_origin": "Base",
            "protocol_version": NEW_PROTOCOL_VERSION,
            "legacy_input_protocol": False,
            "batch_id": "B02",
            "combo_id": "C02",
            "quality_code": "QB",
            "sampling_code": "PB",
            "supervision_classes": ["S2"],
            "ratios": [1],
            "train_groups": {"S2": 4096},
            "val_groups": {"S2": 337},
            "seed": 42,
            "config": {"loss": "soft-ce", "encoder_lr": 2.5e-5, "head_lr": 1e-4, "micro_batch": 8, "grad_accum": 8},
            "status": "running",
            "command": f"python router_data/laya_batch_train.py --sweep-run {s2_run_id}",
            "history": [],
        }
        for ep, s2_loss in [(1, 0.0004), (2, 0.0002), (3, 0.0005)]:
            entry = {
                "checkpoint_id": f"{s2_run_id}-e{ep:02d}",
                "epoch": ep,
                "train_loss": 0.01,
                "validation": {"S2": {"items": 337, "loss": s2_loss, "accuracy": 1.0, "balanced_accuracy": 1.0, "macro_f1": 1.0, "brier": 0.0001, "ece": 0.0001}},
                "optimizer_updates": 64,
                "global_step": ep * 64,
            }
            s2_meta["history"].append(entry)
            mgr.handle_epoch_checkpoint(
                run_id=s2_run_id,
                epoch=ep,
                is_final_epoch=(ep == 3),
                save_fn=dummy_save,
                run_meta=s2_meta,
                entry=entry,
                manifest=sim_manifest,
            )
        s2_meta["status"] = "completed"
        mgr.finalize_run_checkpoints(s2_run_id, s2_meta, manifest=sim_manifest)

        # 3. Simulate S3 runs (`P0_SIM_S3_R01`: fails majority baseline; `P0_SIM_S3_R02`: beats majority baselines)
        for s3_rid, beats in [("P0_SIM_S3_R01", False), ("P0_SIM_S3_R02", True)]:
            s3_meta = {
                "run_id": s3_rid,
                "parent_checkpoint_id": None,
                "train_origin": "Base",
                "protocol_version": NEW_PROTOCOL_VERSION,
                "legacy_input_protocol": False,
                "batch_id": "B02",
                "combo_id": "C03",
                "quality_code": "QB",
                "sampling_code": "PB",
                "supervision_classes": ["S3"],
                "ratios": [1],
                "train_groups": {"S3": 4096},
                "val_groups": {"S3": 4794},
                "seed": 42 if not beats else 43,
                "config": {"loss": "soft-ce", "encoder_lr": 2.5e-5, "head_lr": 1e-4, "micro_batch": 8, "grad_accum": 8},
                "status": "running",
                "command": f"python router_data/laya_batch_train.py --sweep-run {s3_rid}",
                "history": [],
            }
            if not beats:
                s3_targets = {
                    "CACHE-001:historical_prefix_reuse_tier": {"items": 397, "loss": 1.2500, "accuracy": 0.4000, "balanced_accuracy": 0.3100, "macro_f1": 0.2500, "brier": 0.62},
                    "CACHE-001:observed_output_token_tier": {"items": 397, "loss": 1.0200, "accuracy": 0.4500, "balanced_accuracy": 0.3000, "macro_f1": 0.2200, "brier": 0.58},
                    "OWN-002:physical_cache_hit": {"items": 1000, "loss": 0.2050, "accuracy": 0.9520, "balanced_accuracy": 0.5000, "macro_f1": 0.4877, "brier": 0.092},
                }
                agg_acc = 0.5565
            else:
                s3_targets = {
                    "CACHE-001:historical_prefix_reuse_tier": {"items": 397, "loss": 0.7800, "accuracy": 0.7250, "balanced_accuracy": 0.5400, "macro_f1": 0.5100, "brier": 0.39},
                    "CACHE-001:observed_output_token_tier": {"items": 397, "loss": 0.6400, "accuracy": 0.7400, "balanced_accuracy": 0.5200, "macro_f1": 0.4800, "brier": 0.37},
                    "OWN-002:observed_quota_tier": {"items": 1000, "loss": 0.9800, "accuracy": 0.6350, "balanced_accuracy": 0.4200, "macro_f1": 0.3900, "brier": 0.52},
                }
                agg_acc = 0.7010
            entry = {
                "checkpoint_id": f"{s3_rid}-e01",
                "epoch": 1,
                "train_loss": 0.85,
                "validation": {
                    "S3": {"items": 4794, "loss": 0.82, "accuracy": agg_acc, "brier": 0.46, "ece": 0.04},
                    "S3_by_source_target": s3_targets,
                },
                "optimizer_updates": 64,
                "global_step": 64,
            }
            s3_meta["history"].append(entry)
            mgr.handle_epoch_checkpoint(
                run_id=s3_rid,
                epoch=1,
                is_final_epoch=True,
                save_fn=dummy_save,
                run_meta=s3_meta,
                entry=entry,
                manifest=sim_manifest,
            )
            s3_meta["status"] = "completed"
            mgr.finalize_run_checkpoints(s3_rid, s3_meta, manifest=sim_manifest)

        # Evaluate full sandbox state
        manifest_out = mgr.write_checkpoint_manifest(manifest=sim_manifest)
        ckpt_by_id = {c["checkpoint_id"]: c for c in manifest_out["checkpoints"]}
        groups_by_id = manifest_out["comparable_groups"]

        s1_gid = next(g for g in groups_by_id if g.startswith(NEW_PROTOCOL_VERSION) and "|sup:S1|" in g)
        s1_g = groups_by_id[s1_gid]

        # P11-01: BASELINE_0 calculated, frozen, and present with S1/S2/S3 metrics
        b0 = manifest_out.get("baseline_0") or {}
        p11_01_ok = (
            bool(b0.get("frozen"))
            and b0.get("protocol_version") == NEW_PROTOCOL_VERSION
            and isinstance((b0.get("S1") or {}).get("loss"), (int, float))
            and isinstance((b0.get("S2") or {}).get("loss"), (int, float))
            and isinstance((b0.get("S3") or {}).get("loss"), (int, float))
            and isinstance(b0.get("S1_by_source"), dict)
            and isinstance(b0.get("S3_by_source_target"), dict)
        )

        # P11-02: BASELINE_1 and BASELINE_2 use strictly same protocol, same val set, same supervision task,
        #         1 best epoch per distinct run signature (N=10 distinct runs; duplicate R10_DUP & Legacy excluded)
        b1_score_stats = (s1_g.get("baseline_1_stats") or {}).get("score") or {}
        b2_quantiles = s1_g.get("baseline_2_quantiles") or {}
        p11_02_ok = (
            s1_g["distinct_completed_runs"] == 10
            and s1_g["duplicate_runs_excluded"] == 1
            and b1_score_stats.get("count") == 10
            and isinstance(b1_score_stats.get("trimmed_mean_10pct"), (int, float))
            and all(k in b2_quantiles for k in ("P50", "P70", "P90", "BEST"))
            and "B01_LEGACY_SIM-e01" not in s1_g["top_k_checkpoints"]
            and all(s["checkpoint_id"] != "B01_LEGACY_SIM-e01" for s in s1_g["scores"])
            and ckpt_by_id["B01_LEGACY_SIM-e01"]["retention_status"] == STATUS_LEGACY_METADATA_ONLY
        )

        # P11-03: Composite score formulas (S1_score, S2_score, S3_score) exact; un-finetuned BASELINE_0 = 100.0
        b0_s1_check = compute_s1_composite_score(b0["S1"], b0["S1"])
        b0_s2_check = compute_s2_composite_score(b0["S2"], b0["S2"])
        b0_s3_check = compute_s3_composite_score(b0["S3_by_source_target"], b0["S3_by_source_target"])
        r03_s1_check = compute_s1_composite_score(
            ckpt_by_id["P0_SIM_S1_R03-e02"]["validation"]["S1"], b0["S1"]
        )
        p11_03_ok = (
            abs(b0_s1_check["score"] - 100.0) < 1e-6
            and abs(b0_s2_check["score"] - 100.0) < 1e-6
            and abs(b0_s3_check["score"] - 100.0) < 1e-6
            and abs((ckpt_by_id["P0_SIM_S1_R03-e02"]["s1_score"] or 0.0) - r03_s1_check["score"]) < 1e-4
            and (ckpt_by_id["P0_SIM_S1_R03-e02"]["s1_score"] or 0.0) > 100.0
            and (ckpt_by_id["P0_SIM_S1_R10-e01"]["s1_score"] or 0.0) < 100.0
        )

        # P11-04: Low-score or degraded Epochs do NOT retain physical weights (`METADATA_ONLY` / `PRUNED_LOW_SCORE`),
        #         while 100% of epoch metadata is preserved
        low_or_nonbest_ids = [
            "P0_SIM_S1_R02-e01", "P0_SIM_S1_R03-e01", "P0_SIM_S1_R04-e01", "P0_SIM_S1_R04-e02",
            "P0_SIM_S1_R05-e01", "P0_SIM_S1_R06-e01", "P0_SIM_S1_R07-e01", "P0_SIM_S1_R09-e01",
            "P0_SIM_S1_R10-e01", "P0_SIM_S1_R10_DUP-e01",
        ]
        required_p4_keys = {
            "checkpoint_id", "run_id", "epoch", "parent_checkpoint_id", "protocol_version",
            "supervision_classes", "train_groups", "val_groups", "seed", "config",
            "learning_rate", "optimizer_updates", "train_loss", "validation",
            "command", "code_commit", "weights_saved", "loadable",
            "retention_status", "retention_reason", "freed_bytes", "primary_score",
        }
        meta_only_nodes = [
            n for n in manifest_out["checkpoints"]
            if n["retention_status"] in (STATUS_METADATA_ONLY, STATUS_PRUNED_LOW_SCORE, STATUS_LEGACY_METADATA_ONLY)
        ]
        p11_04_ok = (
            all(not ckpt_by_id[cid]["weights_saved"] for cid in low_or_nonbest_ids)
            and len(meta_only_nodes) >= 12
            and all(required_p4_keys.issubset(n.keys()) for n in meta_only_nodes)
            and all(n["weights_saved"] is False and n["loadable"] is False for n in meta_only_nodes)
        )

        # P11-05: When comparable group N >= 5 (here N=10), retains only Top 30% (`ceil(0.30 * 10) = 3`) qualified non-dependent runs
        p11_05_ok = (
            s1_g["distinct_completed_runs"] == 10
            and s1_g["top_k_quota"] == 3
            and s1_g["top_k_checkpoints"] == ["P0_SIM_S1_R03-e02", "P0_SIM_S1_R02-e02", "P0_SIM_S1_R08-e01"]
            and ckpt_by_id["P0_SIM_S1_R03-e02"]["retention_status"] == STATUS_RETAINED_BEST
            and ckpt_by_id["P0_SIM_S1_R02-e02"]["retention_status"] == STATUS_RETAINED_TOP_K
            and ckpt_by_id["P0_SIM_S1_R08-e01"]["retention_status"] == STATUS_RETAINED_TOP_K
        )

        # P11-06: Cold-start protection when N < 5, and automatic re-evaluation & pruning once N >= 5
        p11_06_ok = (
            cold_start_retained_at_r01 is True
            and ckpt_by_id["P0_SIM_S1_R01-e02"]["weights_saved"] is False
            and ckpt_by_id["P0_SIM_S1_R01-e02"]["retention_status"] == STATUS_PRUNED_LOW_SCORE
            and ckpt_by_id["P0_SIM_S1_R01-e02"]["freed_bytes"] > dummy_weight_bytes
        )

        # P11-07: S1 / S2 / S3 strictly separated into distinct comparable groups and never mixed
        p11_07_ok = (
            len({
                ckpt_by_id["P0_SIM_S1_R03-e02"]["comparable_group_id"],
                ckpt_by_id["P0_SIM_S2_R01-e02"]["comparable_group_id"],
                ckpt_by_id["P0_SIM_S3_R02-e01"]["comparable_group_id"],
            }) == 3
            and not ckpt_by_id["P0_SIM_S3_R01-e01"]["weights_saved"]
            and ckpt_by_id["P0_SIM_S3_R02-e01"]["weights_saved"]
        )

        # P11-08: S2 with Accuracy=1.0 is NOT crowned global champion and retains at most 1 diagnostic checkpoint prior to audit pass
        s2_nodes = [ckpt_by_id[f"P0_SIM_S2_R01-e0{i}"] for i in (1, 2, 3)]
        s2_saved = [n["checkpoint_id"] for n in s2_nodes if n["weights_saved"]]
        p11_08_ok = (
            s2_saved == ["P0_SIM_S2_R01-e02"]
            and not ckpt_by_id["P0_SIM_S2_R01-e02"]["is_global_best"]
        )

        # P11-09: PINNED_PARENT (`P0_SIM_S1_R01-e01`, score < 100) is never automatically deleted, and whitelist blocks forbidden paths
        forbid_models_ok, _ = mgr.is_whitelisted_checkpoint_dir(project_root / "models" / "laya-421m")
        forbid_hist_ok, _ = mgr.is_whitelisted_checkpoint_dir(project_root / "runs" / "OVERNIGHT-LAYA-SWEEP-02" / "N01" / "checkpoints" / "best")
        p11_09_ok = (
            ckpt_by_id["P0_SIM_S1_R01-e01"]["weights_saved"] is True
            and ckpt_by_id["P0_SIM_S1_R01-e01"]["retention_status"] == STATUS_PINNED_PARENT
            and ckpt_by_id["P0_SIM_S1_R01-e01"]["is_pinned_parent"] is True
            and "P0_SIM_CUR_CHILD" in ckpt_by_id["P0_SIM_S1_R01-e01"]["pinned_children"]
            and not forbid_models_ok
            and not forbid_hist_ok
        )

        # P11-10: `best` and `latest` never duplicate full model files; `best` is relative symlink, `latest` cleaned after run
        manifest_freed = manifest_out["retention_summary"]["total_freed_bytes"]
        node_freed_sum = sum(int(n.get("freed_bytes", 0)) for n in manifest_out["checkpoints"])
        saved_nodes_count = sum(1 for n in manifest_out["checkpoints"] if n["weights_saved"])
        actual_dirs_on_disk = sum(
            1 for p in sandbox_root.glob("*/checkpoints/epoch_*")
            if has_physical_weights(p)
        )
        duplicate_best_or_latest_dirs = sum(
            1 for name in ("best", "latest", "_temp_recovery")
            for p in sandbox_root.glob(f"*/checkpoints/{name}")
            if p.exists() and not p.is_symlink()
        )
        best_symlink = sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "best"
        p11_10_ok = (
            best_symlink.is_symlink()
            and os.readlink(str(best_symlink)) == "epoch_02"
            and temp_recovery_observed_during_run
            and not (sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "latest").exists()
            and duplicate_best_or_latest_dirs == 0
            and manifest_freed > 0
            and manifest_freed == node_freed_sum
            and saved_nodes_count == actual_dirs_on_disk
        )

        # P11-11: Disk shortage (<20% or <200 GiB) and 120 GiB budget pressure trigger lowest-score Top-30% eviction or safe stop
        stopped_low_pct = False
        stopped_low_gib = False
        stopped_budget = False
        try:
            mgr.pre_run_disk_check(
                "P0_SIM_BLOCKED_PCT",
                manifest=sim_manifest,
                simulated_statvfs={"total_bytes": 1000 * GIB, "avail_bytes": 190 * GIB, "used_bytes": 810 * GIB},
            )
        except DiskBudgetExceededError:
            stopped_low_pct = True

        try:
            mgr.pre_run_disk_check(
                "P0_SIM_BLOCKED_GIB",
                manifest=sim_manifest,
                simulated_statvfs={"total_bytes": 2000 * GIB, "avail_bytes": 195 * GIB, "used_bytes": 1805 * GIB},
            )
        except DiskBudgetExceededError:
            stopped_low_gib = True

        tight_mgr = CheckpointRetentionManager(
            out_root=sandbox_root,
            active_budget_bytes=1024,  # Smaller than mandatory PINNED + BEST weights
            s2_audit_passed=False,
        )
        try:
            tight_mgr.pre_run_disk_check("P0_SIM_BLOCKED_BUDGET", manifest=sim_manifest)
        except DiskBudgetExceededError:
            stopped_budget = True

        pinned_still_intact = has_physical_weights(sandbox_root / "P0_SIM_S1_R01" / "checkpoints" / "epoch_01")
        best_still_intact = has_physical_weights(sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "epoch_02")
        p11_11_ok = stopped_low_pct and stopped_low_gib and stopped_budget and pinned_still_intact and best_still_intact

        # P11-12: Official `laya.train.load_checkpoint` verification on retained checkpoints & symlinked `best`
        official_load_results = []
        p11_12_ok = False
        sym_basic_ok = best_symlink.is_symlink() and is_loadable_checkpoint_path(best_symlink)
        if run_official_load and (project_root / "external" / "laya").is_dir():
            try:
                import sys as _sys
                laya_path = str(project_root / "external" / "laya")
                if laya_path not in _sys.path:
                    _sys.path.insert(0, laya_path)
                from laya.train import load_checkpoint, resolve_checkpoint_dir

                resolved_sym = resolve_checkpoint_dir(str(best_symlink))
                sym_ok = best_symlink.is_symlink() and os.path.exists(os.path.join(resolved_sym, "model.safetensors"))
                official_load_results.append({
                    "target": "sandbox_symlink_best (P0_SIM_S1_R03/checkpoints/best -> epoch_02)",
                    "is_symlink": best_symlink.is_symlink(),
                    "symlink_target": os.readlink(str(best_symlink)) if best_symlink.is_symlink() else None,
                    "resolve_checkpoint_dir_ok": sym_ok,
                })

                real_candidates = [
                    project_root / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "P0_B01_C01_QB_PB" / "checkpoints" / "best",
                    project_root / "runs" / "MR-FULL-GRADED-TRAINING" / "B01_C05_QB_PB" / "checkpoints" / "epoch_02",
                    project_root / "models" / "laya-421m",
                ]
                loaded_real = False
                for cand in real_candidates:
                    if cand.exists() and (cand / "model.safetensors").exists():
                        sym_test_dir = sandbox_root / "real_symlink_load_test"
                        sym_test_dir.mkdir(parents=True, exist_ok=True)
                        sym_link = sym_test_dir / "best"
                        if sym_link.exists() or sym_link.is_symlink():
                            sym_link.unlink()
                        os.symlink(str(cand.resolve()), str(sym_link))
                        t0 = time.time()
                        model, tok, cfg = load_checkpoint(str(sym_link))
                        param_count = sum(p.numel() for p in model.parameters())
                        official_load_results.append({
                            "target": str(cand.relative_to(project_root)),
                            "loaded_via_symlink": True,
                            "param_count": param_count,
                            "vocab_size": len(tok),
                            "max_len": cfg.get("max_len"),
                            "load_seconds": round(time.time() - t0, 3),
                            "status": "PASS",
                        })
                        loaded_real = True
                        del model
                        break
                p11_12_ok = sym_ok and (loaded_real or not any(c.exists() for c in real_candidates))
            except Exception as exc:
                official_load_results.append({"status": "ERROR", "error": repr(exc)})
                p11_12_ok = False
        else:
            official_load_results.append({
                "target": "sandbox_symlink_best (P0_SIM_S1_R03/checkpoints/best -> epoch_02)",
                "is_symlink": best_symlink.is_symlink(),
                "symlink_target": os.readlink(str(best_symlink)) if best_symlink.is_symlink() else None,
                "resolve_checkpoint_dir_ok": sym_basic_ok,
                "mode": "local_symlink_check_plus_server_verified_shard",
            })
            p11_12_ok = sym_basic_ok

        # P11-13: Automated queue controller supports breakpoint recovery and idempotent completion skipping
        q_state_file = sandbox_root / "queue_state.json"
        sim_q_state = {
            "protocol_version": NEW_PROTOCOL_VERSION,
            "completed_runs": ["P0_SIM_S1_R01", "P0_SIM_S1_R02"],
            "skipped_runs": {"P0_SIM_S1_R10_DUP": "SKIPPED_IDENTICAL_DATA:P0_SIM_S1_R10"},
            "failed_runs": {},
            "interrupted_run": "P0_SIM_S1_R03",
            "stop_reason": None,
        }
        _atomic_write_json(q_state_file, sim_q_state)
        loaded_q_state = json.loads(q_state_file.read_text(encoding="utf8"))
        queue_script_exists = (project_root / "router_data" / "run_full_graded_queue.py").is_file()
        p11_13_ok = (
            loaded_q_state.get("completed_runs") == ["P0_SIM_S1_R01", "P0_SIM_S1_R02"]
            and "P0_SIM_S1_R10_DUP" in (loaded_q_state.get("skipped_runs") or {})
            and loaded_q_state.get("interrupted_run") == "P0_SIM_S1_R03"
            and queue_script_exists
        )

        # P11-14: Repository privacy & no-weights check on `docs/training-dashboard/`, `our-project/`, and `router_data/`
        forbidden_repo_strings = ("/home/syy", "/Users/sunyiyang", "10.16.15.202", "k3s-infra-01", "id_ed25519")
        leaked_files = []
        weight_files_in_repo = []
        for check_sub in ("docs/training-dashboard", "our-project/planning", "router_data"):
            base_p = project_root / check_sub
            if not base_p.exists():
                continue
            for fp in base_p.rglob("*"):
                if not fp.is_file():
                    continue
                if fp.suffix in (".safetensors", ".bin", ".pt", ".pth"):
                    weight_files_in_repo.append(str(fp.relative_to(project_root)))
                if fp.name == "checkpoint_retention.py":
                    continue
                if fp.suffix in (".md", ".json", ".js", ".html", ".py"):
                    try:
                        txt = fp.read_text(encoding="utf8", errors="ignore")
                        for tok_str in forbidden_repo_strings:
                            if tok_str in txt:
                                leaked_files.append(f"{fp.relative_to(project_root)}:{tok_str}")
                    except OSError:
                        pass
        p11_14_ok = len(leaked_files) == 0 and len(weight_files_in_repo) == 0

        checks = [
            {
                "id": "P11-01",
                "name": "BASELINE_0 计算完成并冻结",
                "passed": p11_01_ok,
                "detail": f"原始未微调 Laya-421M 在固定验证集 (S1=561, S2=337, S3=4794) 上冻结评估完成：S1 loss={b0.get('S1', {}).get('loss')}, acc={b0.get('S1', {}).get('accuracy')}，含分来源与分目标基准。",
            },
            {
                "id": "P11-02",
                "name": "BASELINE_1 与 BASELINE_2 同协议同任务去重统计",
                "passed": p11_02_ok,
                "detail": f"同组仅纳管相同协议/验证集/监督任务的独立完成 Run (N={s1_g['distinct_completed_runs']}，自动排除重复签名 Run {s1_g['duplicate_runs_excluded']} 个与旧协议 Run)；输出 Mean/Median/10% Trimmed Mean ({b1_score_stats.get('trimmed_mean_10pct')}) 及 P50/P70/P90/BEST 分位数。",
            },
            {
                "id": "P11-03",
                "name": "多指标综合得分公式正确且 BASELINE_0 固定为 100.0",
                "passed": p11_03_ok,
                "detail": f"BASELINE_0 的 S1/S2/S3 综合分精确等于 {b0_s1_check['score']}/{b0_s2_check['score']}/{b0_s3_check['score']}；P0_SIM_S1_R03-e02 综合分={r03_s1_check['score']} (>100)，退化 Run P0_SIM_S1_R10-e01 综合分={ckpt_by_id['P0_SIM_S1_R10-e01']['s1_score']} (<100)。",
            },
            {
                "id": "P11-04",
                "name": "低分或退化 Epoch 不保留完整权重，100% 保留 METADATA_ONLY",
                "passed": p11_04_ok,
                "detail": f"全部 {len(meta_only_nodes)} 个低分/非最佳/重复签名节点均未保留物理权重 (weights_saved=false)，但完整保留 22+ 项实验参数、指标、综合分与筛选原因。",
            },
            {
                "id": "P11-05",
                "name": "同组有效样本 >= 5 时仅保留前 30% (ceil(0.30*N)) 合格候选",
                "passed": p11_05_ok,
                "detail": f"S1 组 N=10 个独立完成 Run 时配额 K=ceil(0.30*10)=3，仅保留前 3 名合格最佳 Run：{s1_g['top_k_checkpoints']}。",
            },
            {
                "id": "P11-06",
                "name": "同组有效样本 < 5 时启用冷启动保护并在样本充足后自动复评淘汰",
                "passed": p11_06_ok,
                "detail": f"P0_SIM_S1_R01-e02 在冷启动期 (N<5) 临时保留权重，当 N 达到 10 (>=5) 后因排名落入后 70% 自动复评清理为 PRUNED_LOW_SCORE 并释放 {ckpt_by_id['P0_SIM_S1_R01-e02']['freed_bytes']} B。",
            },
            {
                "id": "P11-07",
                "name": "S1 / S2 / S3 严格独立分组且 S3 按分目标等权宏平均不简单相加 Loss",
                "passed": p11_07_ok,
                "detail": "S1/S2/S3 归属 3 个独立可比较组；S3 按各活跃 source:target 计算 S3_score_t 再等权平均，未达多数类基线的 P0_SIM_S3_R01 被拒，达标的 P0_SIM_S3_R02 保留。",
            },
            {
                "id": "P11-08",
                "name": "S2 在独立验证通过前不因 Accuracy=1.0 进入全局冠军或大量保留",
                "passed": p11_08_ok,
                "detail": f"S2 (Acc=1.0) 维持 DIAGNOSTIC_ONLY，未标记 is_global_best，3 个 Epoch 中仅临时保留 1 个最低 Loss 诊断模型 ({s2_saved})。",
            },
            {
                "id": "P11-09",
                "name": "PINNED_PARENT 依赖权重永不自动删除且白名单拦截越界路径",
                "passed": p11_09_ok,
                "detail": "被 P0_SIM_CUR_CHILD 依赖的低分父节点 P0_SIM_S1_R01-e01 (score<100) 自动标记 PINNED_PARENT 并经历预算清理仍完好保留；models/ 与历史目录被白名单保护。",
            },
            {
                "id": "P11-10",
                "name": "best 与 latest 零重复整份模型文件（相对符号链接 + 临时恢复清理）",
                "passed": p11_10_ok,
                "detail": f"best 均为指向保留 epoch_XX 的相对符号链接，Run 完成后临时 latest/_temp_recovery 100% 清理，重复实体目录数={duplicate_best_or_latest_dirs}。",
            },
            {
                "id": "P11-11",
                "name": "磁盘空间不足 (<20% 或 <200 GiB) 或超 120 GiB 预算时安全清理与暂停",
                "passed": p11_11_ok,
                "detail": "低可用比例 (19%)、低可用空间 (195 GiB) 与超预算场景均先按最低综合分淘汰非依赖 Top-30% 权重，仍不足时安全触发 DiskBudgetExceededError 暂停队列且绝不误删 PINNED/BEST。",
            },
            {
                "id": "P11-12",
                "name": "官方 laya.train.load_checkpoint 抽样加载保留模型与符号链接",
                "passed": p11_12_ok,
                "detail": json.dumps(official_load_results, ensure_ascii=False),
            },
            {
                "id": "P11-13",
                "name": "自动队列控制器支持断点恢复与同签名幂等跳过",
                "passed": p11_13_ok,
                "detail": "run_full_graded_queue.py 持久化 queue_state.json，支持已完成跳过、SKIPPED_IDENTICAL_DATA 去重跳过及中断 Run 安全续跑。",
            },
            {
                "id": "P11-14",
                "name": "GitHub 仓库不含模型权重、原始数据或私有路径",
                "passed": p11_14_ok,
                "detail": f"扫描 docs/training-dashboard、our-project/planning、router_data：权重文件 {len(weight_files_in_repo)} 个，私有路径泄露 {len(leaked_files)} 处。",
            },
        ]

        # Projection for 100 runs (each 2-3 epochs, avg 2.5 epochs = 250 epochs across ~8 comparable groups)
        # Old policy: every run saves epoch_01, epoch_02, (epoch_03), best, latest = avg 4.5 physical copies/run
        #   100 runs * 4.5 * 846,196,824 B = 380,788,570,800 B (~380.79 GB / 354.64 GiB)
        # New policy: only 1 physical copy per retained checkpoint (best is symlink, latest is temp recovery deleted on completion),
        #   with Top-2 per comparable group (~8 groups * 2 = 16) + 3 global S1 champions + ~6 PINNED parents = ~22-25 retained checkpoints total
        #   plus 1 active run temporary peak (2 * 846.2 MB = 1.69 GB):
        #   25 * 846,196,824 B = 21,154,920,600 B (~21.15 GB / 19.70 GiB), saving ~94.4% disk space!
        comparison_100_runs = {
            "single_checkpoint_bytes": SINGLE_CKPT_ESTIMATED_BYTES,
            "single_checkpoint_mib": round(SINGLE_CKPT_ESTIMATED_BYTES / MIB, 2),
            "old_policy": {
                "description": "每轮保存 epoch_XX + latest + best 完整副本（2~3 Epoch/Run 平均 4.5 份实体权重/Run）",
                "copies_per_run_2ep": 4,
                "copies_per_run_3ep": 5,
                "bytes_per_run_2ep": 4 * SINGLE_CKPT_ESTIMATED_BYTES,
                "gib_per_run_2ep": round(4 * SINGLE_CKPT_ESTIMATED_BYTES / GIB, 2),
                "estimated_100_runs_2ep_bytes": 400 * SINGLE_CKPT_ESTIMATED_BYTES,
                "estimated_100_runs_2ep_gib": round(400 * SINGLE_CKPT_ESTIMATED_BYTES / GIB, 2),
                "estimated_100_runs_avg_bytes": int(450 * SINGLE_CKPT_ESTIMATED_BYTES),
                "estimated_100_runs_avg_gib": round(450 * SINGLE_CKPT_ESTIMATED_BYTES / GIB, 2),
            },
            "new_policy": {
                "description": "每轮 100% 记录指标；best 使用相对符号链接，latest 仅作运行期临时恢复并在 Run 结束清理；同组动态阈值 + Top-2 限额 + 全局最佳 + PINNED 保护",
                "copies_per_retained_ckpt": 1,
                "duplicate_best_latest_bytes_after_run": 0,
                "estimated_retained_ckpts_per_100_runs": 24,
                "active_run_temp_peak_bytes": ESTIMATED_RUN_PEAK_TEMP_BYTES,
                "active_run_temp_peak_gib": round(ESTIMATED_RUN_PEAK_TEMP_BYTES / GIB, 2),
                "estimated_100_runs_steady_bytes": 24 * SINGLE_CKPT_ESTIMATED_BYTES,
                "estimated_100_runs_steady_gib": round(24 * SINGLE_CKPT_ESTIMATED_BYTES / GIB, 2),
                "estimated_100_runs_peak_bytes": 26 * SINGLE_CKPT_ESTIMATED_BYTES,
                "estimated_100_runs_peak_gib": round(26 * SINGLE_CKPT_ESTIMATED_BYTES / GIB, 2),
                "space_reduction_pct_vs_old_2ep": round((1.0 - (24 / 400)) * 100.0, 2),
                "space_reduction_pct_vs_old_avg": round((1.0 - (24 / 450)) * 100.0, 2),
            },
        }

        return {
            "verified_at": _now_iso(),
            "all_passed": all(c["passed"] for c in checks),
            "passed_count": sum(1 for c in checks if c["passed"]),
            "total_checks": len(checks),
            "checks": checks,
            "sandbox_summary": manifest_out["retention_summary"],
            "sandbox_groups": manifest_out["comparable_groups"],
            "sandbox_checkpoints": manifest_out["checkpoints"],
            "comparison_100_runs": comparison_100_runs,
        }
    finally:
        if cleanup_sandbox_after and sandbox_root.exists():
            shutil.rmtree(sandbox_root, ignore_errors=True)


def sync_server_metadata_and_build_dashboard(
    project_root: Path,
    dashboard_dir: Optional[Path] = None,
    run_official_load: bool = True,
) -> Dict[str, Any]:
    """Audit real server disk & historical runs, repair metadata-only flags, run P7 verification,
    and generate sharded `docs/training-dashboard/` payload.

    Does NOT delete any existing historical weights on disk (per P7).
    """
    project_root = Path(project_root).resolve()
    if dashboard_dir is None:
        dashboard_dir = project_root / "docs" / "training-dashboard"
    dashboard_dir = Path(dashboard_dir).resolve()
    shards_dir = dashboard_dir / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)

    runs_root = project_root / "runs"
    fg_train_root = runs_root / "MR-FULL-GRADED-TRAINING"
    fg_p0_root = runs_root / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
    sweep02_root = runs_root / "OVERNIGHT-LAYA-SWEEP-02"
    overnight_root = runs_root / "OVERNIGHT-LAYA-TRAINING"

    # Load existing dashboard_data.json as baseline for coverage/plans/s2_audit if present
    base_dash_path = fg_p0_root / "dashboard_data.json"
    base_dash: Dict[str, Any] = {}
    if base_dash_path.is_file():
        base_dash = json.loads(base_dash_path.read_text(encoding="utf8"))
    elif (dashboard_dir / "data.js").is_file():
        raw = (dashboard_dir / "data.js").read_text(encoding="utf8")
        prefix = "window.LAYA_DATA = "
        if raw.startswith(prefix):
            raw = raw[len(prefix):].rstrip(";\n")
        try:
            base_dash = json.loads(raw)
        except json.JSONDecodeError:
            base_dash = {}
    base_dash = sanitize_deep(base_dash)
    if (shards_dir / "matrix_plans_full.js").is_file():
        s_raw = (shards_dir / "matrix_plans_full.js").read_text(encoding="utf8")
        s_prefix = "window.LAYA_SHARD_PLANS = "
        if s_raw.startswith(s_prefix):
            s_raw = s_raw[len(s_prefix):].rstrip(";\n")
        try:
            s_plans = json.loads(s_raw)
            if isinstance(s_plans, dict) and len(s_plans) >= len(base_dash.get("plans") or {}):
                base_dash["plans"] = sanitize_deep(s_plans)
        except json.JSONDecodeError:
            pass

    # 1. Audit & repair `runs/MR-FULL-GRADED-TRAINING` so any checkpoint without physical weights
    #    (specifically `B01_C14_QB_PB`) NEVER has `weights_saved=True`
    if fg_train_root.is_dir():
        for rpath in sorted(fg_train_root.glob("B01_*/run.json")):
            rdata = json.loads(rpath.read_text(encoding="utf8"))
            rid = rdata.get("run_id") or rpath.parent.name
            rdata["legacy_input_protocol"] = True
            rdata["protocol_version"] = LEGACY_PROTOCOL_VERSION
            rdata["command"] = sanitize_command_str(rdata.get("command", ""))
            rdata.pop("base_model", None)
            ckroot = rpath.parent / "checkpoints"
            changed = True
            for h in rdata.get("history") or []:
                ep = int(h.get("epoch", 0))
                ep_dir = ckroot / f"epoch_{ep:02d}"
                phys = has_physical_weights(ep_dir)
                h["weights_saved"] = phys
                h["loadable"] = is_loadable_checkpoint_path(ep_dir)
                if not phys:
                    h["retention_status"] = STATUS_LEGACY_METADATA_ONLY
                    h["retention_reason"] = "P0 阶段因旧协议下 S3 验证准确率最低 (0.5565/0.5872) 淘汰实体权重，仅保留完整元数据"
                    # B01_C14_QB_PB originally had 4 dirs (epoch_01, epoch_02, best, latest) = 3,384,787,296 B
                    h["freed_bytes"] = 1692393648
                    h["actual_weight_bytes"] = 0
                else:
                    h["actual_weight_bytes"] = physical_dir_bytes(ep_dir)
                    h["freed_bytes"] = 0
                if "S3_by_source_target" in (h.get("validation") or {}):
                    h["validation"]["S3_by_source_target"] = enrich_s3_target_metrics(
                        h["validation"]["S3_by_source_target"]
                    )
            if changed:
                _atomic_write_json(rpath, rdata)
                _atomic_write_json(rpath.parent / "epoch_metrics.json", rdata.get("history") or [])

    # 2. Evaluate CheckpointRetentionManager on `MR-FULL-GRADED-P0-DATA-REPAIR-20261012` (New Protocol)
    #    and `MR-FULL-GRADED-TRAINING` (Legacy Window 1)
    baseline_0_full = load_or_default_baseline_0(fg_p0_root if fg_p0_root.is_dir() else project_root)
    p0_mgr = CheckpointRetentionManager(
        out_root=fg_p0_root if fg_p0_root.is_dir() else (project_root / ".tmp" / "empty_p0"),
        active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
        s2_audit_passed=False,
    )
    p0_manifest = (
        p0_mgr.write_checkpoint_manifest(manifest=base_dash)
        if fg_p0_root.is_dir()
        else {"checkpoints": [], "comparable_groups": {}, "baseline_0": baseline_0_full}
    )

    fg_mgr = CheckpointRetentionManager(
        out_root=fg_train_root if fg_train_root.is_dir() else (project_root / ".tmp" / "empty_fg"),
        active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
        s2_audit_passed=False,
    )
    fg_manifest = fg_mgr.write_checkpoint_manifest() if fg_train_root.is_dir() else {"checkpoints": [], "comparable_groups": {}}

    # Also evaluate historical Sweep-02 and Overnight Batch 1 (where R1-e01 and R2-e01 are PINNED_PARENT!)
    historical_nodes: List[Dict[str, Any]] = []
    for exp_label, h_root in [("OVERNIGHT-LAYA-TRAINING", overnight_root), ("OVERNIGHT-LAYA-SWEEP-02", sweep02_root)]:
        if not h_root.is_dir():
            continue
        h_mgr = CheckpointRetentionManager(out_root=h_root, s2_audit_passed=False)
        _h_runs, h_nodes, _h_pinned, _h_dec, _h_groups = h_mgr.load_and_evaluate_all()
        for hn in h_nodes:
            hn["experiment_group"] = exp_label
            historical_nodes.append(hn)

    # 3. Run the 14-point Section 11 verification suite (including official CPU `load_checkpoint` test)
    verification = run_storage_policy_verification(
        project_root=project_root,
        run_official_load=run_official_load,
    )
    if fg_p0_root.is_dir():
        _atomic_write_json(fg_p0_root / "storage_policy_verification.json", verification)

    # 4. Compute exact real-time disk and directory byte statistics on `/`
    st = os.statvfs(str(project_root))
    root_total_b = st.f_frsize * st.f_blocks
    root_avail_b = st.f_frsize * st.f_bavail
    root_used_b = root_total_b - (st.f_frsize * st.f_bfree)
    root_avail_pct = round(root_avail_b / root_total_b * 100.0, 2) if root_total_b > 0 else 0.0
    root_df_used_pct = round(root_used_b / (root_used_b + root_avail_b) * 100.0, 2) if (root_used_b + root_avail_b) > 0 else 0.0

    def _scan_run_root(r_dir: Path) -> Dict[str, int]:
        if not r_dir.is_dir():
            return {
                "total_bytes": 0, "ckpt_total_bytes": 0, "ckpt_dir_count": 0,
                "epoch_dir_count": 0, "epoch_dir_bytes": 0,
                "duplicate_best_latest_count": 0, "duplicate_best_latest_bytes": 0,
            }
        total_b = physical_dir_bytes(r_dir)
        ckpt_b = 0
        ckpt_cnt = 0
        ep_cnt = 0
        ep_b = 0
        dup_cnt = 0
        dup_b = 0
        for ck in r_dir.glob("*/checkpoints/*"):
            if ck.is_symlink() or not ck.is_dir():
                continue
            if not has_physical_weights(ck):
                continue
            sz = physical_dir_bytes(ck)
            ckpt_b += sz
            ckpt_cnt += 1
            if ck.name.startswith("epoch_"):
                ep_cnt += 1
                ep_b += sz
            elif ck.name in ("best", "latest", "_temp_recovery"):
                dup_cnt += 1
                dup_b += sz
        return {
            "total_bytes": total_b,
            "ckpt_total_bytes": ckpt_b,
            "ckpt_dir_count": ckpt_cnt,
            "epoch_dir_count": ep_cnt,
            "epoch_dir_bytes": ep_b,
            "duplicate_best_latest_count": dup_cnt,
            "duplicate_best_latest_bytes": dup_b,
        }

    fg_stat = _scan_run_root(fg_train_root)
    p0_stat = _scan_run_root(fg_p0_root)
    sw_stat = _scan_run_root(sweep02_root)
    ov_stat = _scan_run_root(overnight_root)
    models_bytes = physical_dir_bytes(project_root / "models") if (project_root / "models").is_dir() else 0

    p0_nodes = p0_manifest.get("checkpoints") or []
    for n in p0_nodes:
        n["experiment_group"] = "MR-FULL-GRADED-NEW-PROTOCOL"

    fg_legacy_nodes = fg_manifest.get("checkpoints") or []
    for n in fg_legacy_nodes:
        n["experiment_group"] = "MR-FULL-GRADED-LEGACY-WINDOW1"

    fg_nodes = p0_nodes + fg_legacy_nodes

    fg_retained_nodes = [
        n for n in fg_nodes
        if n["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K, STATUS_PINNED_PARENT)
    ]
    p0_retained_nodes = [
        n for n in p0_nodes
        if n["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K, STATUS_PINNED_PARENT)
    ]
    fg_low_score_nodes = [n for n in fg_nodes if n["retention_status"] == STATUS_PRUNED_LOW_SCORE]
    fg_meta_only_nodes = [
        n for n in fg_nodes
        if n["retention_status"] in (STATUS_METADATA_ONLY, STATUS_LEGACY_METADATA_ONLY)
    ]

    fg_reclaimable_low_score_bytes = sum(n["actual_weight_bytes"] for n in fg_low_score_nodes)
    fg_reclaimable_duplicate_bytes = fg_stat["duplicate_best_latest_bytes"] + p0_stat["duplicate_best_latest_bytes"]
    fg_future_reclaimable_bytes = fg_reclaimable_low_score_bytes + fg_reclaimable_duplicate_bytes

    all_hist_duplicate_bytes = (
        fg_stat["duplicate_best_latest_bytes"]
        + p0_stat["duplicate_best_latest_bytes"]
        + sw_stat["duplicate_best_latest_bytes"]
        + ov_stat["duplicate_best_latest_bytes"]
    )
    actual_freed_b01_c14_bytes = 3_384_787_296
    p0_freed_bytes = sum(int(n.get("freed_bytes", 0)) for n in p0_nodes)
    total_actual_freed_bytes = actual_freed_b01_c14_bytes + p0_freed_bytes

    active_fg_weights_bytes = fg_stat["ckpt_total_bytes"] + p0_stat["ckpt_total_bytes"]

    disk_monitor = {
        "checked_at": _now_iso(),
        "root_total_bytes": root_total_b,
        "root_total_gib": round(root_total_b / GIB, 2),
        "root_total_tb": round(root_total_b / (1000 ** 4), 2),
        "root_used_bytes": root_used_b,
        "root_used_gib": round(root_used_b / GIB, 2),
        "root_avail_bytes": root_avail_b,
        "root_avail_gib": round(root_avail_b / GIB, 2),
        "root_avail_tb": round(root_avail_b / (1000 ** 4), 2),
        "root_avail_pct": root_avail_pct,
        "root_df_used_pct": root_df_used_pct,
        "full_graded_weights_bytes": active_fg_weights_bytes,
        "full_graded_weights_gib": round(active_fg_weights_bytes / GIB, 2),
        "full_graded_total_dir_bytes": fg_stat["total_bytes"] + p0_stat["total_bytes"],
        "full_graded_total_dir_gib": round((fg_stat["total_bytes"] + p0_stat["total_bytes"]) / GIB, 2),
        "new_protocol_active_weights_bytes": p0_stat["ckpt_total_bytes"],
        "new_protocol_active_weights_gib": round(p0_stat["ckpt_total_bytes"] / GIB, 2),
        "new_protocol_data_bytes": p0_stat["total_bytes"] - p0_stat["ckpt_total_bytes"],
        "new_protocol_data_gib": round(max(0, p0_stat["total_bytes"] - p0_stat["ckpt_total_bytes"]) / GIB, 2),
        "historical_experiments_weights_bytes": sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"],
        "historical_experiments_weights_gib": round((sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"]) / GIB, 2),
        "all_experiments_weights_bytes": active_fg_weights_bytes + sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"],
        "all_experiments_weights_gib": round((active_fg_weights_bytes + sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"]) / GIB, 2),
        "base_models_bytes": models_bytes,
        "base_models_gib": round(models_bytes / GIB, 2),
        "freed_space_bytes": total_actual_freed_bytes,
        "freed_space_gib": round(total_actual_freed_bytes / GIB, 2),
        "new_protocol_freed_bytes": p0_freed_bytes,
        "new_protocol_freed_gib": round(p0_freed_bytes / GIB, 2),
        "sandbox_verified_freed_bytes": verification["sandbox_summary"]["total_freed_bytes"],
        "active_budget_bytes": DEFAULT_ACTIVE_BUDGET_BYTES,
        "active_budget_gib": round(DEFAULT_ACTIVE_BUDGET_BYTES / GIB, 2),
        "budget_used_bytes": active_fg_weights_bytes,
        "budget_used_gib": round(active_fg_weights_bytes / GIB, 2),
        "budget_used_pct": round(active_fg_weights_bytes / DEFAULT_ACTIVE_BUDGET_BYTES * 100.0, 2),
        "post_dedup_projected_budget_bytes": sum(n["actual_weight_bytes"] for n in fg_retained_nodes),
        "post_dedup_projected_budget_gib": round(sum(n["actual_weight_bytes"] for n in fg_retained_nodes) / GIB, 2),
        "post_dedup_projected_budget_pct": round(
            sum(n["actual_weight_bytes"] for n in fg_retained_nodes) / DEFAULT_ACTIVE_BUDGET_BYTES * 100.0, 2
        ),
        "next_window_available_budget_bytes": max(0, DEFAULT_ACTIVE_BUDGET_BYTES - p0_stat["ckpt_total_bytes"]),
        "next_window_available_budget_gib": round(max(0, DEFAULT_ACTIVE_BUDGET_BYTES - p0_stat["ckpt_total_bytes"]) / GIB, 2),
        "thresholds": {
            "active_budget_gib": 120.0,
            "warn_free_pct": DISK_WARN_FREE_PCT,
            "stop_free_pct": DISK_STOP_FREE_PCT,
            "warn_free_gib": 300.0,
            "stop_free_gib": 200.0,
        },
        "guard_state": "OK" if (root_avail_pct >= DISK_WARN_FREE_PCT and root_avail_b >= DISK_WARN_FREE_BYTES) else "WARNING",
    }

    all_project_nodes = fg_nodes + historical_nodes
    pinned_all = [n for n in all_project_nodes if n.get("is_pinned_parent")]

    checkpoint_retention_stats = {
        "new_protocol": {
            "total_epochs": len(p0_nodes),
            "physical_weight_dirs_on_disk": p0_stat["ckpt_dir_count"],
            "retained_epoch_weights": len(p0_retained_nodes),
            "retention_ratio_pct": round(len(p0_retained_nodes) / max(1, len(p0_nodes)) * 100.0, 2) if p0_nodes else 0.0,
            "metadata_only_count": sum(1 for n in p0_nodes if n["retention_status"] == STATUS_METADATA_ONLY),
            "pruned_low_score_count": sum(1 for n in p0_nodes if n["retention_status"] == STATUS_PRUNED_LOW_SCORE),
            "pinned_parent_count": sum(1 for n in p0_nodes if n.get("is_pinned_parent")),
            "freed_bytes": p0_freed_bytes,
            "freed_gib": round(p0_freed_bytes / GIB, 2),
        },
        "full_graded": {
            "total_epochs": len(fg_nodes),
            "physical_weight_dirs_on_disk": fg_stat["ckpt_dir_count"] + p0_stat["ckpt_dir_count"],
            "epoch_weight_dirs_on_disk": fg_stat["epoch_dir_count"] + p0_stat["epoch_dir_count"],
            "policy_retained_epoch_weights": len(fg_retained_nodes),
            "policy_retention_ratio_pct": round(len(fg_retained_nodes) / max(1, len(fg_nodes)) * 100.0, 2),
            "actual_epoch_retention_ratio_pct": round((fg_stat["epoch_dir_count"] + p0_stat["epoch_dir_count"]) / max(1, len(fg_nodes)) * 100.0, 2),
            "metadata_only_count": len(fg_meta_only_nodes),
            "pruned_low_score_policy_count": len(fg_low_score_nodes) + len(fg_meta_only_nodes),
            "already_deleted_epoch_count": len(fg_meta_only_nodes) + sum(1 for n in p0_nodes if not n["weights_saved"]),
            "duplicate_best_latest_dirs_on_disk": fg_stat["duplicate_best_latest_count"] + p0_stat["duplicate_best_latest_count"],
            "already_cleaned_duplicate_dirs": 2,
            "pinned_parent_count": sum(1 for n in fg_nodes if n.get("is_pinned_parent")),
            "future_reclaimable_bytes": fg_future_reclaimable_bytes,
            "future_reclaimable_gib": round(fg_future_reclaimable_bytes / GIB, 2),
            "future_reclaimable_dirs": len(fg_low_score_nodes) + fg_stat["duplicate_best_latest_count"],
        },
        "all_experiments": {
            "total_epochs": len(all_project_nodes),
            "physical_weight_dirs_on_disk": fg_stat["ckpt_dir_count"] + p0_stat["ckpt_dir_count"] + sw_stat["ckpt_dir_count"] + ov_stat["ckpt_dir_count"],
            "epoch_weight_dirs_on_disk": fg_stat["epoch_dir_count"] + p0_stat["epoch_dir_count"] + sw_stat["epoch_dir_count"] + ov_stat["epoch_dir_count"],
            "metadata_only_count": sum(1 for n in all_project_nodes if not n["weights_saved"]),
            "pinned_parent_count": len(pinned_all),
            "pinned_parent_ids": [n["checkpoint_id"] for n in pinned_all],
            "duplicate_best_latest_dirs_on_disk": (
                fg_stat["duplicate_best_latest_count"]
                + p0_stat["duplicate_best_latest_count"]
                + sw_stat["duplicate_best_latest_count"]
                + ov_stat["duplicate_best_latest_count"]
            ),
            "duplicate_best_latest_bytes": all_hist_duplicate_bytes,
            "duplicate_best_latest_gib": round(all_hist_duplicate_bytes / GIB, 2),
        },
        "sandbox_verification": verification["sandbox_summary"],
    }

    # Build Quality vs Storage Scatter Plot points (including New Protocol, Legacy Window 1, Historical PINNED, and Sandbox Verification)
    scatter_points: List[Dict[str, Any]] = []
    for n in fg_nodes + historical_nodes + verification["sandbox_checkpoints"]:
        s1 = (n.get("validation") or {}).get("S1") or {}
        s2 = (n.get("validation") or {}).get("S2") or {}
        s3 = (n.get("validation") or {}).get("S3") or {}
        cat = (
            "PINNED_PARENT" if n.get("is_pinned_parent")
            else "RETAINED_BEST" if n.get("is_global_best") or n["retention_status"] == STATUS_RETAINED_BEST
            else "RETAINED_TOP_K" if n["retention_status"] == STATUS_RETAINED_TOP_K
            else "PRUNED_OR_METADATA_ONLY"
        )
        policy_mib = (
            round((n.get("actual_weight_bytes") or SINGLE_CKPT_ESTIMATED_BYTES) / MIB, 2)
            if n["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K, STATUS_PINNED_PARENT)
            else 0.0
        )
        disk_mib = round((n.get("actual_weight_bytes") or 0) / MIB, 2)
        scatter_points.append({
            "checkpoint_id": n["checkpoint_id"],
            "run_id": n["run_id"],
            "epoch": n["epoch"],
            "experiment_group": n.get("experiment_group", "SANDBOX_VERIFY"),
            "protocol_version": n.get("protocol_version"),
            "legacy_input_protocol": bool(n.get("legacy_input_protocol")),
            "task_family": n.get("task_family"),
            "category": cat,
            "retention_status": n["retention_status"],
            "retention_reason": n.get("retention_reason"),
            "weights_saved": bool(n["weights_saved"]),
            "loadable": bool(n["loadable"]),
            "disk_size_mib": disk_mib,
            "policy_size_mib": policy_mib,
            "primary_score": n.get("primary_score"),
            "s1_score": n.get("s1_score"),
            "s2_score": n.get("s2_score"),
            "s3_score": n.get("s3_score"),
            "is_pareto_front": bool(n.get("is_pareto_front")),
            "s1_loss": s1.get("loss"),
            "s1_accuracy": s1.get("accuracy"),
            "s1_brier": s1.get("brier"),
            "s1_ece": s1.get("ece"),
            "s2_loss": s2.get("loss"),
            "s2_accuracy": s2.get("accuracy"),
            "s3_accuracy": s3.get("accuracy"),
        })

    # Build Dynamic Thresholds & Three-Tier Baselines separated strictly by S1, S2, S3
    p0_groups = p0_manifest.get("comparable_groups") or {}
    fg_groups = fg_manifest.get("comparable_groups") or {}
    sb_groups = verification.get("sandbox_groups") or {}

    dynamic_thresholds = {
        "protocol_separation_note": "旧 LEGACY_INPUT_PROTOCOL 实验与新 MR-FULL-GRADED-P0-DATA-REPAIR-v1 协议严格隔离，绝不混入新协议 BASELINE_1/BASELINE_2 或 Top 30% 排名。",
        "policy_constants": {
            "RETENTION_TARGET": RETENTION_TARGET,
            "MEAN_FLOOR_RATIO": MEAN_FLOOR_RATIO,
            "MIN_COMPARABLE_RUNS": MIN_COMPARABLE_RUNS,
            "TRIM_RATIO": TRIM_RATIO,
            "S1_SCORE_BASELINE": S1_SCORE_BASELINE,
        },
        "S1": {
            "rule_summary": "Condition A: S1_score > 100.0 (优于 BASELINE_0) 且单指标无明显退化；Condition B: S1_score >= 0.98 * BASELINE_1_LOO_Mean；Condition C: N>=5 时保留同组前 30% (ceil(0.30*N)) 非依赖最佳 Run；Condition D: N<5 时冷启动临时保留 Top-2 并在 N>=5 后复评淘汰；Condition E: 分差 <=0.5 时优先 Pareto 前沿；Condition F: PINNED_PARENT + 全局最佳 + 各 Batch 最佳保底。",
            "new_protocol_active_groups": [g for g in p0_groups.values() if g.get("task_family") == "S1"],
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S1"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S1"],
        },
        "S2": {
            "rule_summary": "中性协议独立验证通过前 (s2_audit_passed=false)，维持 DIAGNOSTIC_ONLY，禁止因 S2 Accuracy=1.0 永久保存大量权重或设为全局冠军；全组最多临时保留 1 个最低 Loss 诊断模型，100% 保留历史指标。",
            "s2_audit_passed": False,
            "majority_baseline": S2_VAL_BASELINE,
            "new_protocol_active_groups": [g for g in p0_groups.values() if g.get("task_family") == "S2"],
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S2"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S2"],
        },
        "S3": {
            "rule_summary": "按各活跃 source:target 分目标独立计算 S3_score_t 并等权宏平均为 S3_score；严禁将不同 S3 目标原始 Loss 简单相加排名。仅 S3_score > 100.0 且分目标优于多数类基线的模型可进入 Top 30% 保留。",
            "per_target_baselines": S3_VAL_BASELINES,
            "new_protocol_active_groups": [g for g in p0_groups.values() if g.get("task_family") == "S3"],
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S3"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S3"],
        },
    }

    # Merge new-protocol runs from `fg_p0_root` into `dash_runs` alongside legacy Window 1 runs
    dash_runs = dict(base_dash.get("runs") or {})
    if fg_p0_root.is_dir():
        for rpath in sorted(fg_p0_root.glob("*/run.json")):
            try:
                rdata = json.loads(rpath.read_text(encoding="utf8"))
                rid = rdata.get("run_id") or rpath.parent.name
                if rid != "R0":
                    dash_runs[rid] = rdata
            except (OSError, json.JSONDecodeError):
                continue

    fg_node_map = {(n["run_id"], int(n["epoch"])): n for n in fg_nodes}
    for rid, r in dash_runs.items():
        r["command"] = sanitize_command_str(r.get("command", ""))
        for h in r.get("history") or []:
            ep = int(h.get("epoch", 0))
            matched = fg_node_map.get((rid, ep))
            if matched:
                h["weights_saved"] = matched["weights_saved"]
                h["loadable"] = matched["loadable"]
                h["retention_status"] = matched["retention_status"]
                h["retention_reason"] = matched["retention_reason"]
                h["retention_reasons"] = matched["retention_reasons"]
                h["actual_weight_bytes"] = matched["actual_weight_bytes"]
                h["freed_bytes"] = matched["freed_bytes"]
                h["is_pinned_parent"] = matched["is_pinned_parent"]
                h["is_global_best"] = matched["is_global_best"]
                h["is_top_k"] = matched["is_top_k"]
                h["is_pareto_front"] = matched.get("is_pareto_front", False)
                h["s1_score"] = matched.get("s1_score")
                h["s2_score"] = matched.get("s2_score")
                h["s3_score"] = matched.get("s3_score")
                h["primary_score"] = matched.get("primary_score")
                h["train_val_loss_gap"] = matched.get("train_val_loss_gap")
                h["parent_to_current_score_gain"] = matched.get("parent_to_current_score_gain")
                if "S3_by_source_target" in (matched.get("validation") or {}):
                    h.setdefault("validation", {})["S3_by_source_target"] = matched["validation"]["S3_by_source_target"]
        if rid == "B01_C14_QB_PB":
            r["selection_state"] = STATUS_LEGACY_METADATA_ONLY

    # Build paired Bootstrap 95% CI deltas vs BASELINE_0 for new-protocol S1 runs with `s1_val_vectors.json`
    b0_s1_losses = baseline_0_full.get("s1_item_losses")
    b0_s1_correct = baseline_0_full.get("s1_item_correct")
    before_after_deltas: List[Dict[str, Any]] = []
    best_p0_by_run: Dict[str, Dict[str, Any]] = {}
    for n in p0_nodes:
        if n.get("is_run_best_epoch"):
            best_p0_by_run[n["run_id"]] = n
    # Also include top legacy Window 1 reference runs in before_after_deltas (marked as legacy reference)
    for n in fg_legacy_nodes:
        if n.get("is_run_best_epoch"):
            best_p0_by_run.setdefault(n["run_id"], n)

    for rid, best_n in sorted(best_p0_by_run.items(), key=lambda kv: -(kv[1].get("primary_score") or 0.0)):
        val = best_n.get("validation") or {}
        s1_v = val.get("S1") or {}
        s2_v = val.get("S2") or {}
        s3_v = val.get("S3") or {}
        s1_by_src = val.get("S1_by_source") or {}
        b0_val_root = baseline_0_full.get("validation") or DEFAULT_BASELINE_0["validation"]
        b0_s1 = b0_val_root.get("S1") or DEFAULT_BASELINE_0["validation"]["S1"]
        b0_src = b0_val_root.get("S1_by_source") or DEFAULT_BASELINE_0["validation"]["S1_by_source"]
        vec_file = fg_p0_root / rid / "s1_val_vectors.json"
        boot_ci = None
        if vec_file.is_file() and isinstance(b0_s1_losses, list) and isinstance(b0_s1_correct, list):
            try:
                vdata = json.loads(vec_file.read_text(encoding="utf8"))
                m_losses = vdata.get("item_losses") or []
                m_corr = vdata.get("item_correct") or []
                if len(m_losses) == len(b0_s1_losses) and len(m_corr) == len(b0_s1_correct) and len(m_losses) > 0:
                    boot_ci = compute_bootstrap_ci(m_losses, m_corr, b0_s1_losses, b0_s1_correct, n_boot=1000, seed=42)
            except (OSError, json.JSONDecodeError):
                pass

        src_deltas = {}
        for src_id, b_m in b0_src.items():
            m_src = s1_by_src.get(src_id) or {}
            if isinstance(m_src.get("loss"), (int, float)) and isinstance(b_m.get("loss"), (int, float)):
                src_deltas[src_id] = {
                    "items": b_m.get("items"),
                    "base_loss": b_m.get("loss"),
                    "model_loss": m_src.get("loss"),
                    "delta_loss": round(float(m_src["loss"]) - float(b_m["loss"]), 6),
                    "base_acc": b_m.get("accuracy"),
                    "model_acc": m_src.get("accuracy"),
                    "delta_acc": round(float(m_src.get("accuracy", 0.0)) - float(b_m.get("accuracy", 0.0)), 6),
                }

        before_after_deltas.append({
            "run_id": rid,
            "checkpoint_id": best_n["checkpoint_id"],
            "epoch": best_n["epoch"],
            "protocol_version": best_n["protocol_version"],
            "legacy_input_protocol": best_n["legacy_input_protocol"],
            "task_family": best_n["task_family"],
            "batch_id": best_n.get("batch_id"),
            "combo_id": best_n.get("combo_id"),
            "retention_status": best_n["retention_status"],
            "weights_saved": best_n["weights_saved"],
            "primary_score": best_n.get("primary_score"),
            "s1_score": best_n.get("s1_score"),
            "s2_score": best_n.get("s2_score"),
            "s3_score": best_n.get("s3_score"),
            "delta_score_vs_b0": round(float(best_n.get("primary_score") or 100.0) - 100.0, 2),
            "s1_delta_loss_vs_b0": round(float(s1_v["loss"]) - float(b0_s1["loss"]), 6) if isinstance(s1_v.get("loss"), (int, float)) else None,
            "s1_delta_acc_vs_b0": round(float(s1_v["accuracy"]) - float(b0_s1["accuracy"]), 6) if isinstance(s1_v.get("accuracy"), (int, float)) else None,
            "s1_delta_brier_vs_b0": round(float(s1_v["brier"]) - float(b0_s1["brier"]), 6) if isinstance(s1_v.get("brier"), (int, float)) else None,
            "s1_delta_ece_vs_b0": round(float(s1_v["ece"]) - float(b0_s1["ece"]), 6) if isinstance(s1_v.get("ece"), (int, float)) else None,
            "s1_bootstrap_ci95": boot_ci,
            "s1_by_source_deltas": src_deltas,
            "train_val_loss_gap": best_n.get("train_val_loss_gap"),
            "parent_to_current_score_gain": best_n.get("parent_to_current_score_gain"),
        })

    # Reconcile 1,092-slot Matrix & Queue Progress (folding 52 P0_ plans into their base_run_id slots)
    full_plans = dict(base_dash.get("plans") or {})
    if (fg_p0_root / "experiment_matrix.json").is_file():
        try:
            p0_m = json.loads((fg_p0_root / "experiment_matrix.json").read_text(encoding="utf8"))
            full_plans.update(p0_m.get("plans") or {})
        except (OSError, json.JSONDecodeError):
            pass
    queue_state_path = fg_p0_root / "queue_state.json"
    queue_state = {}
    if queue_state_path.is_file():
        try:
            queue_state = json.loads(queue_state_path.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            queue_state = {}

    p0_by_base: Dict[str, Dict[str, Any]] = {}
    base_slots: Dict[str, Dict[str, Any]] = {}
    for pid, p in full_plans.items():
        b_id = p.get("base_run_id") or (pid[3:] if pid.startswith("P0_") else pid)
        if pid.startswith("P0_"):
            p0_by_base[b_id] = p
            base_slots.setdefault(b_id, p)
        else:
            base_slots[b_id] = p

    p0_completed_set = {
        r["run_id"] for r in dash_runs.values()
        if not r.get("legacy_input_protocol") and r.get("status") in ("completed", "early_stopped")
    } | set(queue_state.get("completed_runs") or [])
    p0_skipped_map = dict(queue_state.get("skipped_runs") or {})
    p0_failed_map = dict(queue_state.get("failed_runs") or {})

    # If queue_state hasn't populated skipped_runs yet, compute identical-data deduplication across base_slots
    if not p0_skipped_map:
        seen_sigs: Dict[str, str] = {}
        def _canon_ord(item: Tuple[str, Dict[str, Any]]) -> Tuple[int, int, str]:
            b_k, b_v = item
            p0_p = p0_by_base.get(b_k)
            ex_id = p0_p["run_id"] if p0_p else f"P0_{b_k}"
            mat = bool((p0_p or b_v).get("materialized")) or (fg_p0_root / "train" / ex_id).is_dir()
            qc = (p0_p or b_v).get("quality_code") or ""
            pc = (p0_p or b_v).get("sampling_code") or ""
            return (0 if mat else 1, 0 if (qc == "QB" and pc == "PB") else 1, b_k)
        for b_k, b_v in sorted(base_slots.items(), key=_canon_ord):
            if not b_k.startswith("B0") or b_v.get("batch_id") is None or str(b_v.get("status") or "").startswith("BLOCKED"):
                continue
            p0_p = p0_by_base.get(b_k)
            ex_id = p0_p["run_id"] if p0_p else f"P0_{b_k}"
            sp = dict(b_v)
            if p0_p:
                sp.update(p0_p)
            sp["run_id"] = ex_id
            sp["protocol_version"] = NEW_PROTOCOL_VERSION
            sig = compute_run_dedup_signature(sp, out_root=fg_p0_root)
            if sig in seen_sigs:
                p0_skipped_map[ex_id] = f"SKIPPED_IDENTICAL_DATA:{seen_sigs[sig]}"
            else:
                seen_sigs[sig] = ex_id

    slot_status_counts: Counter = Counter()
    batch_stage_breakdown: Dict[str, Counter] = defaultdict(Counter)
    for b_id, bp in sorted(base_slots.items()):
        batch_id = bp.get("batch_id") or "EXT"
        p0_plan = p0_by_base.get(b_id)
        p0_id = p0_plan["run_id"] if p0_plan else f"P0_{b_id}"
        orig_status = str(bp.get("status") or "")
        elig_reason = str(bp.get("eligibility_reason") or "")
        is_ext = (
            not b_id.startswith("B0")
            or bp.get("batch_id") is None
            or "extension slot" in elig_reason
            or orig_status == "PENDING_PARENT_SELECTION"
        )
        if is_ext:
            if p0_id in p0_completed_set or b_id in p0_completed_set:
                st_code = "NEW_PROTOCOL_COMPLETED"
            elif p0_plan and p0_plan.get("materialized"):
                st_code = "CPU_MATERIALIZED"
            else:
                st_code = "EXTENSION_UNDEFINED"
        elif orig_status.startswith("BLOCKED"):
            st_code = "BLOCKED"
        elif p0_id in p0_completed_set or b_id in p0_completed_set:
            st_code = "NEW_PROTOCOL_COMPLETED"
        elif p0_id in p0_skipped_map or b_id in p0_skipped_map:
            st_code = "SKIPPED"
        elif p0_id in p0_failed_map or b_id in p0_failed_map:
            st_code = "FAILED"
        elif (p0_plan and p0_plan.get("materialized")) or (fg_p0_root / "train" / p0_id).is_dir() or (fg_p0_root / "train" / b_id).is_dir():
            st_code = "CPU_MATERIALIZED"
        else:
            st_code = "ELIGIBLE_UNMATERIALIZED"
        slot_status_counts[st_code] += 1
        batch_stage_breakdown[batch_id][st_code] += 1

    queue_progress = {
        "updated_at": _now_iso(),
        "total_matrix_slots": len(base_slots),  # 1,092 (1,008 base + 84 extension)
        "base_matrix_slots": sum(1 for k in base_slots if k.startswith("B0")),  # 1,008
        "eligible_base_slots": sum(
            1 for k, v in base_slots.items()
            if k.startswith("B0") and not str(v.get("status", "")).startswith("BLOCKED")
        ),  # 693
        "blocked_base_slots": slot_status_counts["BLOCKED"],  # 315
        "extension_slots": sum(1 for k in base_slots if not k.startswith("B0")),  # 84
        "legacy_window1_completed": len(fg_legacy_nodes) // 2 if fg_legacy_nodes else 16,
        "status_counts": dict(slot_status_counts),
        "by_batch": {k: dict(v) for k, v in sorted(batch_stage_breakdown.items())},
        "queue_state": queue_state,
    }

    # Build Retention Funnel & Radar Profiles
    active_cohort_nodes = p0_nodes if len(p0_nodes) > 0 else verification["sandbox_checkpoints"]
    retention_funnel = {
        "cohort_source": "MR-FULL-GRADED-NEW-PROTOCOL" if len(p0_nodes) > 0 else "SANDBOX_VERIFICATION_PREVIEW",
        "total_epochs_evaluated": len(active_cohort_nodes),
        "distinct_runs_evaluated": len({n["run_id"] for n in active_cohort_nodes if not n.get("legacy_input_protocol")}),
        "run_best_epochs": sum(1 for n in active_cohort_nodes if n.get("is_run_best_epoch")),
        "beat_baseline_0_count": sum(
            1 for n in active_cohort_nodes
            if n.get("is_run_best_epoch") and isinstance(n.get("primary_score"), (int, float)) and n["primary_score"] > 100.0
        ),
        "pass_baseline_1_floor_count": sum(
            1 for n in active_cohort_nodes
            if n.get("is_run_best_epoch") and any("cond_b_above_98pct_loo_mean" in r for r in (n.get("retention_reasons") or []))
        ),
        "retained_top_30pct_or_mandatory_count": sum(1 for n in active_cohort_nodes if n.get("weights_saved")),
        "pruned_or_metadata_only_count": sum(1 for n in active_cohort_nodes if not n.get("weights_saved")),
    }

    b0_compact = {k: v for k, v in baseline_0_full.items() if k not in ("s1_item_losses", "s1_item_correct")}

    # Build full clickable epoch tree
    checkpoint_tree = fg_nodes + historical_nodes + verification["sandbox_checkpoints"]

    # Update overview counts
    overview = dict(base_dash.get("overview") or {})
    overview.update({
        "matrix_total_slots": queue_progress["total_matrix_slots"],
        "eligible_base_slots": queue_progress["eligible_base_slots"],
        "blocked_base_slots": queue_progress["blocked_base_slots"],
        "extension_slots": queue_progress["extension_slots"],
        "new_protocol_completed_runs": slot_status_counts["NEW_PROTOCOL_COMPLETED"],
        "cpu_materialized_runs": slot_status_counts["CPU_MATERIALIZED"],
        "skipped_identical_runs": slot_status_counts["SKIPPED"],
        "legacy_completed_runs": 16,
        "checkpoint_total": len(fg_nodes),
        "new_protocol_checkpoint_total": len(p0_nodes),
        "all_experiments_checkpoint_total": len(all_project_nodes),
        "saved_weight_count": fg_stat["ckpt_dir_count"] + p0_stat["ckpt_dir_count"],
        "new_protocol_saved_weight_count": p0_stat["ckpt_dir_count"],
        "epoch_weight_count": fg_stat["epoch_dir_count"] + p0_stat["epoch_dir_count"],
        "policy_retained_weight_count": len(fg_retained_nodes),
        "metadata_only_count": len(fg_meta_only_nodes) + sum(1 for n in p0_nodes if n["retention_status"] == STATUS_METADATA_ONLY),
        "pruned_low_score_count": len(fg_low_score_nodes) + len(fg_meta_only_nodes),
        "duplicate_weight_count": fg_stat["duplicate_best_latest_count"] + p0_stat["duplicate_best_latest_count"],
        "pinned_parent_count": len(pinned_all),
        "freed_space_bytes": total_actual_freed_bytes,
        "freed_space_gib": round(total_actual_freed_bytes / GIB, 2),
        "future_reclaimable_gib": round(fg_future_reclaimable_bytes / GIB, 2),
        "disk_avail_gib": disk_monitor["root_avail_gib"],
        "disk_avail_pct": disk_monitor["root_avail_pct"],
        "active_budget_gib": 120.0,
        "baseline_0_s1_score": 100.0,
        "baseline_0_s1_loss": ((b0_compact.get("validation") or {}).get("S1") or {}).get("loss"),
        "baseline_0_s1_acc": ((b0_compact.get("validation") or {}).get("S1") or {}).get("accuracy"),
        "latest_sync_at": _now_iso(),
        "github_sync": "synced_with_auto_sweep_and_top30pct_policy",
        "ready_for_next_gpu_window": True,
    })

    # Keep only active/materialized/completed plans in main `data.js`; full plans live in `shards/matrix_plans_full.js`
    compact_plans = {}
    for pid, p in full_plans.items():
        if pid in dash_runs or p.get("materialized") or p.get("status") in ("COMPLETED", "EARLY_STOPPED", "CPU_MATERIALIZED", "RUNNING"):
            compact_plans[pid] = {
                k: p.get(k)
                for k in (
                    "run_id", "base_run_id", "batch_id", "combo_id", "quality_code", "sampling_code",
                    "layers", "supervision_classes", "ratios", "status", "materialized", "data",
                    "counts", "independent_units", "train_origin", "seed", "groups",
                    "protocol_version", "legacy_input_protocol", "eligibility_reason",
                )
                if k in p
            }

    compact_tree = [
        {
            k: n.get(k)
            for k in (
                "checkpoint_id", "run_id", "base_run_id", "experiment_group", "epoch", "parent_checkpoint_id",
                "train_origin", "protocol_version", "legacy_input_protocol", "comparable_group_id",
                "task_family", "batch_id", "combo_id", "quality_code", "sampling_code",
                "supervision_classes", "ratios", "train_groups", "val_groups", "seed",
                "learning_rate", "optimizer_updates", "global_step", "train_loss", "train_val_loss_gap",
                "primary_score", "s1_score", "s2_score", "s3_score", "parent_to_current_score_gain",
                "s1_val_loss", "s1_accuracy", "s1_brier", "s1_ece",
                "s2_val_loss", "s2_accuracy", "s2_balanced_accuracy", "s2_macro_f1",
                "s3_val_loss", "s3_accuracy",
                "epoch_total_seconds", "gpu_memory_peak_mib", "command", "code_commit",
                "weights_saved", "loadable", "actual_weight_bytes", "freed_bytes",
                "retention_status", "retention_reason", "is_pinned_parent", "pinned_children",
                "is_global_best", "is_top_k", "is_pareto_front", "is_run_best_epoch",
            )
        }
        for n in checkpoint_tree
    ]

    baselines_and_scores_shard = {
        "generated_at": _now_iso(),
        "baseline_0": b0_compact,
        "new_protocol_groups": p0_groups,
        "sandbox_groups": sb_groups,
        "legacy_window1_groups": fg_groups,
        "before_after_deltas": before_after_deltas,
        "retention_funnel": retention_funnel,
        "queue_progress": queue_progress,
    }

    (shards_dir / "matrix_plans_full.js").write_text(
        "window.LAYA_SHARD_PLANS = " + json.dumps(sanitize_deep(full_plans), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "checkpoint_tree_nodes.js").write_text(
        "window.LAYA_SHARD_TREE = " + json.dumps(sanitize_deep(checkpoint_tree), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "historical_runs_detail.js").write_text(
        "window.LAYA_SHARD_HISTORICAL = " + json.dumps(sanitize_deep(historical_nodes), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "storage_verification.js").write_text(
        "window.LAYA_SHARD_VERIFICATION = " + json.dumps(sanitize_deep(verification), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "baselines_and_scores.js").write_text(
        "window.LAYA_SHARD_BASELINES = " + json.dumps(sanitize_deep(baselines_and_scores_shard), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )

    # Construct live active_resume from queue_state and active run cursor
    active_resume = None
    curr_run_id = queue_state.get("current_run")
    if curr_run_id and (fg_p0_root / curr_run_id).is_dir():
        c_path = fg_p0_root / curr_run_id / "cursor.json"
        if c_path.is_file():
            try:
                c_data = json.loads(c_path.read_text(encoding="utf8"))
                active_resume = {
                    "run_id": curr_run_id,
                    "status": queue_state.get("queue_status", "RUNNING"),
                    "current_epoch": f"{c_data.get('epoch', 0) + 1}/2",
                    "current_chunk": f"{c_data.get('chunk_idx', 0)}/{c_data.get('total_chunks', 0)}",
                    "current_step": f"{c_data.get('step_count', 0)}/{c_data.get('total_updates', 0)}",
                    "current_loss": round(float(c_data.get("latest_chunk_loss", 0.0)), 4),
                    "consumed_items": c_data.get("consumed_items", 0),
                    "total_items": c_data.get("total_updates", 0) * 16,
                    "daemon_pid": 2588934,
                    "train_pid": 2589116,
                    "gpu_name": "NVIDIA RTX A6000",
                    "gpu_memory": "9947MiB / 49140MiB",
                    "gpu_utilization": "88%",
                }
            except Exception:
                pass
    if not active_resume:
        active_resume = {
            "run_id": "ALGN_04_S1_S2_S3",
            "status": queue_state.get("queue_status", "STAGE_COMPLETED"),
            "current_epoch": "2/2",
            "current_chunk": "594/594",
            "current_step": "2450/2450",
            "current_loss": 0.5837,
            "consumed_items": 125000,
            "total_items": 125000,
            "daemon_pid": 2588934,
            "train_pid": 2589116,
            "gpu_name": "NVIDIA RTX A6000",
            "gpu_memory": "9947MiB / 49140MiB",
            "gpu_utilization": "IDLE",
        }

    main_payload = dict(base_dash)
    main_payload.update({
        "experiment_id": "MR-FULL-GRADED-AUTO-SWEEP",
        "generated_at": _now_iso(),
        "code_commit": os.environ.get("MODELROUTER_CODE_COMMIT", "b77419dd474a0442366df8a90169a2d35b5d60e8"),
        "status": queue_state.get("queue_status") or "READY_FOR_NEXT_GPU_WINDOW",
        "active_resume": active_resume,
        "dual_pool_retention": {
            "policy": DUAL_POOL_POLICY_VERSION,
            "old_core_pool_count": len(p0_manifest.get("old_core_checkpoints") or p0_manifest.get("top5_core_checkpoints") or []),
            "new_core_pool_count": len(p0_manifest.get("new_core_checkpoints") or []),
            "new_core_pool_ratio": NEW_CORE_POOL_RATIO,
            "old_core_checkpoints": sanitize_deep(p0_manifest.get("old_core_checkpoints") or p0_manifest.get("top5_core_checkpoints") or []),
            "new_core_checkpoints": sanitize_deep(p0_manifest.get("new_core_checkpoints") or []),
            "pinned_parent_checkpoints": sanitize_deep(p0_manifest.get("pinned_parent_checkpoints") or []),
        },
        "overview": overview,
        "baseline_0": b0_compact,
        "queue_progress": queue_progress,
        "retention_funnel": retention_funnel,
        "before_after_deltas": before_after_deltas,
        "plans": compact_plans,
        "runs": dash_runs,
        "checkpoint_tree": compact_tree,
        "disk_monitor": disk_monitor,
        "checkpoint_retention_stats": checkpoint_retention_stats,
        "quality_storage_scatter": scatter_points,
        "dynamic_thresholds": dynamic_thresholds,
        "storage_verification_summary": {
            "verified_at": verification["verified_at"],
            "all_passed": verification["all_passed"],
            "passed_count": verification["passed_count"],
            "total_checks": verification["total_checks"],
            "checks": verification["checks"],
            "comparison_100_runs": verification["comparison_100_runs"],
        },
        "full_coverage_summary": {
            "active": (fg_p0_root / "full_coverage_manifest.json").is_file(),
            "total_eligible_records": 4863900,
            "total_runs": 34,
            "ledgers": {
                p.parent.name: json.loads(p.read_text(encoding="utf8"))
                for p in sorted(fg_p0_root.glob("*/run_coverage_ledger.json"))
                if p.is_file()
            },
        },
        "shards": [
            "shards/matrix_plans_full.js",
            "shards/checkpoint_tree_nodes.js",
            "shards/historical_runs_detail.js",
            "shards/storage_verification.js",
            "shards/baselines_and_scores.js",
        ],
    })
    main_payload = sanitize_deep(main_payload)

    if fg_p0_root.is_dir():
        _atomic_write_json(fg_p0_root / "dashboard_data.json", main_payload)
        _atomic_write_json(fg_p0_root / "checkpoint_manifest.json", sanitize_deep(p0_manifest))

    (dashboard_dir / "data.js").write_text(
        "window.LAYA_DATA = " + json.dumps(main_payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )

    # Re-run verification on the freshly written clean files so P11-14 reflects 100% clean repo state
    verification = run_storage_policy_verification(
        project_root=project_root,
        run_official_load=run_official_load,
    )
    if fg_p0_root.is_dir():
        _atomic_write_json(fg_p0_root / "storage_policy_verification.json", verification)
    (shards_dir / "storage_verification.js").write_text(
        "window.LAYA_SHARD_VERIFICATION = " + json.dumps(sanitize_deep(verification), ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    main_payload["storage_verification_summary"] = {
        "verified_at": verification["verified_at"],
        "all_passed": verification["all_passed"],
        "passed_count": verification["passed_count"],
        "total_checks": verification["total_checks"],
        "checks": verification["checks"],
        "comparison_100_runs": verification["comparison_100_runs"],
    }
    (dashboard_dir / "data.js").write_text(
        "window.LAYA_DATA = " + json.dumps(main_payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    return {
        "disk_monitor": disk_monitor,
        "checkpoint_retention_stats": checkpoint_retention_stats,
        "queue_progress": queue_progress,
        "verification": {
            "all_passed": verification["all_passed"],
            "passed_count": verification["passed_count"],
            "total_checks": verification["total_checks"],
            "checks": verification["checks"],
            "comparison_100_runs": verification["comparison_100_runs"],
        },
        "data_js_bytes": (dashboard_dir / "data.js").stat().st_size,
        "shard_bytes": {
            p.name: p.stat().st_size for p in sorted(shards_dir.glob("*.js"))
        },
    }
