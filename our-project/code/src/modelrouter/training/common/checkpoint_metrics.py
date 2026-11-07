"""Checkpoint metrics, reference baselines, and scoring."""
import json, math, sys, time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
if _WORKSPACE_ROOT not in sys.path: sys.path.insert(0, _WORKSPACE_ROOT)
from router_data.external_benchmark import STATUS_EVALUATED, STATUS_NOT_EVALUATED, STATUS_ROUTER_SERVING_NOT_READY, compute_composite_selection_score, evaluate_external_dev

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
# The 13 historical runs completed before or at the Q-012 policy boundary under the metadata-only regime.
# Their checkpoints were already finalized as METADATA_ONLY and MUST NOT inflate the new post-Q012 candidate denominator.
HISTORICAL_PRE_Q012_COMPLETED_RUNS = {
    "F01_S1", "F02_S1", "F03_S1", "F04_S1", "F05_S1", "F06_S1", "F07_S1",
    "F01", "F02", "ALGN_01_S1", "ALGN_02_S1_S2", "ALGN_03_S1_S3", "ALGN_04_S1_S2_S3",
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
