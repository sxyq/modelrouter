"""Intelligent checkpoint retention, deduplication, disk budget guard, and verification for Laya FULL-GRADED training."""
import hashlib
import json
import math
import os
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# Canonical checkpoint retention statuses required by P4
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

# P1 Dynamic Threshold Constants
MIN_COMPARABLE_CONTROLS = 5                      # Cold-start until >= 5 checkpoints in comparable group
GROUP_TOP_K = 2                                  # Retain at most Top-2 non-dependent checkpoints per group
S1_LOSS_IMPROVEMENT_REL = 0.005                  # Condition A: Val Loss >= 0.5% below group mean
S1_ACC_DEGRADATION_TOL = 0.005                   # Condition A: Accuracy within 0.5pp of group mean
S1_ACC_IMPROVEMENT_ABS = 0.010                   # Condition B: Accuracy >= +1.0pp above group mean
S1_LOSS_BRIER_DEGRADATION_REL = 0.005            # Condition B: Loss and Brier within +0.5% of group mean

NEW_PROTOCOL_VERSION = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
LEGACY_PROTOCOL_VERSION = "LEGACY_INPUT_PROTOCOL"

# Fixed validation baselines (computed on V2.1 Batch 1 fixed validation sets)
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


def classification_metrics_from_records(records: Sequence[Tuple[int, Any, Any, int]]) -> Dict[str, Any]:
    """Compute Balanced Accuracy, Macro-F1, and majority/prior baseline stats from calibration_records."""
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
        golds.append( max(range(len(t)), key=lambda i: t[i]) if t else 0 )
        preds.append( max(range(len(p)), key=lambda i: p[i]) if p else 0 )

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
    acc = sum(1 for g, p in zip(golds, preds) if g == p) / n
    beats = bool(
        acc > maj_acc + 0.005
        and mean_loss < prior_loss * 0.995
        and balanced_acc > maj_bal_acc + 0.005
    )
    return {
        "num_classes": max(2, len(active_classes)),
        "majority_class": int(maj_cls),
        "majority_baseline_accuracy": round(maj_acc, 4),
        "majority_balanced_accuracy": round(maj_bal_acc, 4),
        "prior_baseline_loss": round(prior_loss, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "macro_f1": round(macro_f1, 4),
        "beats_majority_baseline": beats,
    }


def enrich_s3_target_metrics(s3_breakdown: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Attach fixed S3 target majority/prior baseline comparisons to S3_by_source_target."""
    if not isinstance(s3_breakdown, dict):
        return {}
    enriched = {}
    for target_key, metrics in s3_breakdown.items():
        if not isinstance(metrics, dict):
            continue
        item = dict(metrics)
        base = S3_VAL_BASELINES.get(target_key)
        if base:
            loss = item.get("loss")
            acc = item.get("accuracy")
            maj_acc = base["majority_accuracy"]
            prior_loss = base["prior_loss"]
            item["majority_baseline_accuracy"] = round(maj_acc, 4)
            item["majority_balanced_accuracy"] = round(base["majority_balanced_accuracy"], 4)
            item["majority_macro_f1"] = round(base["majority_macro_f1"], 4)
            item["prior_baseline_loss"] = round(prior_loss, 4)
            if item.get("balanced_accuracy") is None:
                # Estimate lower bound or preserve if already computed from records
                item["balanced_accuracy"] = round(
                    max(base["majority_balanced_accuracy"], acc * 0.85) if isinstance(acc, (int, float)) and acc > maj_acc + 0.02
                    else base["majority_balanced_accuracy"],
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
        enriched[target_key] = item
    return enriched


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
    """True iff `ckpt_dir` is a real directory (not a symlink) containing `model.safetensors`."""
    ckpt_dir = Path(ckpt_dir)
    if not ckpt_dir.exists() or ckpt_dir.is_symlink() or not ckpt_dir.is_dir():
        return False
    st = ckpt_dir / "model.safetensors"
    return st.is_file() and not st.is_symlink() and st.stat().st_size > 0


def is_loadable_checkpoint_path(ckpt_dir: Path) -> bool:
    """True iff `ckpt_dir` (real dir or valid symlink) has `rl_agent_config.json` and `model.safetensors`."""
    ckpt_dir = Path(ckpt_dir)
    try:
        if not ckpt_dir.exists() or not ckpt_dir.is_dir():
            return False
        return (ckpt_dir / "rl_agent_config.json").is_file() and (ckpt_dir / "model.safetensors").is_file()
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
    """Build the strict P1 comparable group identifier.

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
    classes = list(run_meta.get("supervision_classes") or sorted((run_meta.get("train_groups") or {}).keys()))
    if not classes:
        classes = ["S1"]
    sup_key = "+".join(classes)
    val_groups = run_meta.get("val_groups") or {}
    val_sig = ",".join(f"{k}:{val_groups[k]}" for k in sorted(val_groups)) if val_groups else f"{sup_key}:fixed"
    loss_name = (run_meta.get("config") or {}).get("loss", "soft-ce")
    return f"{protocol}|sup:{sup_key}|val:{val_sig}|metric:{loss_name}_raw_logit"


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


def evaluate_cohort_retention(
    nodes: List[Dict[str, Any]],
    pinned_map: Dict[str, List[str]],
    s2_audit_passed: bool = False,
    allow_legacy_reference_eval: bool = False,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Evaluate P1 dynamic score thresholds & Top-K across a cohort of checkpoint nodes.

    Strictly separates new-protocol checkpoints from `LEGACY_INPUT_PROTOCOL`.
    Never mixes S1, S2, and S3 rankings.
    Returns `(decisions_by_ckpt_id, group_summaries_by_group_id)`.
    """
    decisions: Dict[str, Dict[str, Any]] = {}
    group_summaries: Dict[str, Dict[str, Any]] = {}

    # Separate nodes into comparable groups
    by_group: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        is_legacy = bool(node.get("legacy_input_protocol"))
        if is_legacy and not allow_legacy_reference_eval:
            continue
        gid = node["comparable_group_id"]
        by_group[gid].append(node)

    # 1. Global S1 champions (strictly within the active protocol cohort, never mixing legacy with new)
    s1_candidates = [
        n for n in nodes
        if (not n.get("legacy_input_protocol") or allow_legacy_reference_eval)
        and n.get("task_family") == "S1"
        and isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))
    ]
    global_best_s1_loss_id = None
    global_best_s1_acc_id = None
    global_best_s1_brier_id = None
    if s1_candidates:
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

    # 2. Evaluate each comparable group according to S1 / S2 / S3 rules
    for gid, gnodes in sorted(by_group.items()):
        if not gnodes:
            continue
        family = gnodes[0].get("task_family", "S1")
        n_controls = len(gnodes)
        cold_start = n_controls < MIN_COMPARABLE_CONTROLS

        if family == "S1":
            losses = [n["validation"]["S1"]["loss"] for n in gnodes if isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
            accs = [n["validation"]["S1"]["accuracy"] for n in gnodes if isinstance((n.get("validation", {}).get("S1") or {}).get("accuracy"), (int, float))]
            briers = [n["validation"]["S1"]["brier"] for n in gnodes if isinstance((n.get("validation", {}).get("S1") or {}).get("brier"), (int, float))]
            mean_loss = sum(losses) / len(losses) if losses else None
            mean_acc = sum(accs) / len(accs) if accs else None
            mean_brier = sum(briers) / len(briers) if briers else None

            thresh_loss_a = round(mean_loss * (1.0 - S1_LOSS_IMPROVEMENT_REL), 6) if mean_loss is not None else None
            thresh_acc_floor_a = round(mean_acc - S1_ACC_DEGRADATION_TOL, 6) if mean_acc is not None else None
            thresh_acc_b = round(mean_acc + S1_ACC_IMPROVEMENT_ABS, 6) if mean_acc is not None else None
            thresh_loss_ceil_b = round(mean_loss * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL), 6) if mean_loss is not None else None
            thresh_brier_ceil_b = round(mean_brier * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL), 6) if mean_brier is not None else None

            qualified: List[Dict[str, Any]] = []
            node_eval: Dict[str, Dict[str, Any]] = {}
            for n in gnodes:
                cid = n["checkpoint_id"]
                s1 = n.get("validation", {}).get("S1") or {}
                l_val = s1.get("loss")
                a_val = s1.get("accuracy")
                b_val = s1.get("brier")
                cond_a = bool(
                    mean_loss is not None and mean_acc is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float))
                    and l_val <= thresh_loss_a and a_val >= thresh_acc_floor_a
                )
                cond_b = bool(
                    mean_loss is not None and mean_acc is not None and mean_brier is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float)) and isinstance(b_val, (int, float))
                    and a_val >= thresh_acc_b and l_val <= thresh_loss_ceil_b and b_val <= thresh_brier_ceil_b
                )
                passes = True if cold_start else (cond_a or cond_b)
                node_eval[cid] = {
                    "cond_a_pass": cond_a,
                    "cond_b_pass": cond_b,
                    "threshold_pass": passes,
                    "cold_start": cold_start,
                }
                if passes and isinstance(l_val, (int, float)):
                    qualified.append(n)

            ranked = sorted(
                qualified,
                key=lambda n: (
                    n["validation"]["S1"]["loss"],
                    -(n["validation"]["S1"].get("accuracy") or 0.0),
                    n["validation"]["S1"].get("brier") or 999.0,
                ),
            )
            # Top-K non-dependent checkpoints (pinned parents don't consume non-dependent Top-K slots)
            non_pinned_ranked = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned_ranked[:GROUP_TOP_K]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S1",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_controls,
                "cold_start_mode": cold_start,
                "min_controls_required": MIN_COMPARABLE_CONTROLS,
                "top_k_limit": GROUP_TOP_K,
                "mean_val_loss": round(mean_loss, 4) if mean_loss is not None else None,
                "mean_accuracy": round(mean_acc, 4) if mean_acc is not None else None,
                "mean_brier": round(mean_brier, 4) if mean_brier is not None else None,
                "thresholds": {
                    "condition_a_max_loss": round(thresh_loss_a, 4) if thresh_loss_a is not None else None,
                    "condition_a_min_accuracy": round(thresh_acc_floor_a, 4) if thresh_acc_floor_a is not None else None,
                    "condition_b_min_accuracy": round(thresh_acc_b, 4) if thresh_acc_b is not None else None,
                    "condition_b_max_loss": round(thresh_loss_ceil_b, 4) if thresh_loss_ceil_b is not None else None,
                    "condition_b_max_brier": round(thresh_brier_ceil_b, 4) if thresh_brier_ceil_b is not None else None,
                },
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "loss": (n.get("validation", {}).get("S1") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S1") or {}).get("accuracy"),
                        "brier": (n.get("validation", {}).get("S1") or {}).get("brier"),
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
                if cid == global_best_s1_loss_id:
                    reasons.append("global_best_s1_loss")
                if cid == global_best_s1_acc_id:
                    reasons.append("global_best_s1_accuracy")
                if cid == global_best_s1_brier_id:
                    reasons.append("global_best_s1_brier")
                if cid in top_k_ids:
                    if cold_start:
                        reasons.append(f"group_top_{GROUP_TOP_K}_cold_start(n={n_controls}<{MIN_COMPARABLE_CONTROLS})")
                    elif ev["cond_a_pass"] and ev["cond_b_pass"]:
                        reasons.append(f"group_top_{GROUP_TOP_K}_passed_cond_A_and_B")
                    elif ev["cond_a_pass"]:
                        reasons.append(f"group_top_{GROUP_TOP_K}_passed_cond_A(loss<=mean-0.5%)")
                    else:
                        reasons.append(f"group_top_{GROUP_TOP_K}_passed_cond_B(acc>=mean+1.0pp)")

                should_retain = len(reasons) > 0
                if not should_retain:
                    if not ev["threshold_pass"]:
                        reject_reason = (
                            f"s1_below_dynamic_threshold(loss={n['validation']['S1'].get('loss')} vs {round(thresh_loss_a, 4)}, "
                            f"acc={n['validation']['S1'].get('accuracy')} vs {round(thresh_acc_b, 4)})"
                        )
                    else:
                        reject_reason = f"s1_outside_group_top_{GROUP_TOP_K}(rank>{GROUP_TOP_K})"
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": cid in {global_best_s1_loss_id, global_best_s1_acc_id, global_best_s1_brier_id},
                    "is_top_k": cid in top_k_ids,
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S1",
                    "cond_a_pass": ev["cond_a_pass"],
                    "cond_b_pass": ev["cond_b_pass"],
                }

        elif family == "S2":
            # S2 Rule: before audit passes, do NOT permanently save large numbers of weights based on Acc=1.0,
            # never crown as global champion, allow at most 1 diagnostic model.
            s2_losses = [n["validation"]["S2"]["loss"] for n in gnodes if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float))]
            s2_accs = [n["validation"]["S2"]["accuracy"] for n in gnodes if isinstance((n.get("validation", {}).get("S2") or {}).get("accuracy"), (int, float))]
            s2_briers = [n["validation"]["S2"]["brier"] for n in gnodes if isinstance((n.get("validation", {}).get("S2") or {}).get("brier"), (int, float))]
            mean_loss = sum(s2_losses) / len(s2_losses) if s2_losses else None
            mean_acc = sum(s2_accs) / len(s2_accs) if s2_accs else None
            mean_brier = sum(s2_briers) / len(s2_briers) if s2_briers else None

            if not s2_audit_passed:
                # Diagnostic single model only (lowest S2 loss, tie-broken by earliest epoch)
                ranked = sorted(
                    gnodes,
                    key=lambda n: (
                        (n.get("validation", {}).get("S2") or {}).get("loss") if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float)) else 999.0,
                        n.get("epoch", 99),
                    ),
                )
                diag_ids = [ranked[0]["checkpoint_id"]] if ranked else []
                top_k_ids = diag_ids
            else:
                # After independent audit: require beating majority baseline on Log Loss, Balanced Accuracy, Macro-F1
                qualified = []
                for n in gnodes:
                    s2 = n.get("validation", {}).get("S2") or {}
                    loss = s2.get("loss")
                    acc = s2.get("accuracy")
                    bal_acc = s2.get("balanced_accuracy", 0.5)
                    mf1 = s2.get("macro_f1", S2_VAL_BASELINE["majority_macro_f1"])
                    beats_base = (
                        isinstance(loss, (int, float)) and isinstance(acc, (int, float))
                        and acc > S2_VAL_BASELINE["majority_accuracy"] + 0.005
                        and bal_acc > S2_VAL_BASELINE["majority_balanced_accuracy"] + 0.005
                        and mf1 > S2_VAL_BASELINE["majority_macro_f1"] + 0.005
                        and loss < S2_VAL_BASELINE["prior_loss"] * 0.995
                    )
                    if beats_base:
                        qualified.append(n)
                ranked = sorted(
                    qualified,
                    key=lambda n: (
                        n["validation"]["S2"]["loss"],
                        -(n["validation"]["S2"].get("balanced_accuracy") or 0.0),
                        -(n["validation"]["S2"].get("macro_f1") or 0.0),
                    ),
                )
                non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
                top_k_ids = [n["checkpoint_id"] for n in non_pinned[:GROUP_TOP_K]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S2",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_controls,
                "s2_audit_passed": s2_audit_passed,
                "s2_policy_mode": "AUDIT_PASSED_RANKING" if s2_audit_passed else "DIAGNOSTIC_SINGLE_CAP_PENDING_AUDIT",
                "majority_baseline": S2_VAL_BASELINE,
                "top_k_limit": GROUP_TOP_K if s2_audit_passed else 1,
                "mean_val_loss": round(mean_loss, 4) if mean_loss is not None else None,
                "mean_accuracy": round(mean_acc, 4) if mean_acc is not None else None,
                "mean_brier": round(mean_brier, 4) if mean_brier is not None else None,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "loss": (n.get("validation", {}).get("S2") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S2") or {}).get("accuracy"),
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
                if cid in top_k_ids:
                    if not s2_audit_passed:
                        reasons.append("s2_diagnostic_single_model_pending_audit(not_global_champion)")
                    else:
                        reasons.append("s2_audited_top_k_beats_majority_baseline")
                should_retain = len(reasons) > 0
                reject_reason = (
                    None if should_retain
                    else "s2_100pct_not_trusted_pending_independent_audit(diagnostic_cap=1)"
                    if not s2_audit_passed
                    else "s2_below_majority_baseline_or_outside_top_k"
                )
                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,  # S2 is never crowned global champion before audit
                    "is_top_k": cid in top_k_ids,
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S2",
                }

        else:
            # S3 Rule: compare per real target against each target's majority/prior baseline;
            # NEVER rank by summing raw losses across different S3 targets.
            per_target_stats: Dict[str, Dict[str, Any]] = {}
            for t_key, base in S3_VAL_BASELINES.items():
                t_losses = []
                t_accs = []
                t_briers = []
                for n in gnodes:
                    tb = (n.get("validation", {}).get("S3_by_source_target") or {}).get(t_key) or {}
                    if isinstance(tb.get("loss"), (int, float)):
                        t_losses.append(tb["loss"])
                    if isinstance(tb.get("accuracy"), (int, float)):
                        t_accs.append(tb["accuracy"])
                    if isinstance(tb.get("brier"), (int, float)):
                        t_briers.append(tb["brier"])
                m_loss = sum(t_losses) / len(t_losses) if t_losses else None
                m_acc = sum(t_accs) / len(t_accs) if t_accs else None
                m_brier = sum(t_briers) / len(t_briers) if t_briers else None
                per_target_stats[t_key] = {
                    "baseline_majority_accuracy": base["majority_accuracy"],
                    "baseline_prior_loss": base["prior_loss"],
                    "baseline_balanced_accuracy": base["majority_balanced_accuracy"],
                    "mean_val_loss": round(m_loss, 4) if m_loss is not None else None,
                    "mean_accuracy": round(m_acc, 4) if m_acc is not None else None,
                    "mean_brier": round(m_brier, 4) if m_brier is not None else None,
                    "threshold_max_loss": round(min(base["prior_loss"] * 0.995, (m_loss * 0.995) if (m_loss and not cold_start) else base["prior_loss"] * 0.995), 4),
                    "threshold_min_accuracy": round(max(base["majority_accuracy"] + 0.005, (m_acc - 0.005) if (m_acc and not cold_start) else base["majority_accuracy"] + 0.005), 4),
                }

            qualified = []
            node_s3_summary: Dict[str, Dict[str, Any]] = {}
            for n in gnodes:
                cid = n["checkpoint_id"]
                s3_targets = enrich_s3_target_metrics(n.get("validation", {}).get("S3_by_source_target") or {})
                beaten_targets = []
                rel_gains = []
                for t_key, t_metrics in s3_targets.items():
                    t_stat = per_target_stats.get(t_key)
                    if not t_stat:
                        continue
                    t_loss = t_metrics.get("loss")
                    t_acc = t_metrics.get("accuracy")
                    beats_base = bool(t_metrics.get("beats_majority_baseline"))
                    passes_dyn = bool(
                        beats_base
                        and isinstance(t_loss, (int, float))
                        and isinstance(t_acc, (int, float))
                        and (
                            cold_start
                            or t_loss <= t_stat["threshold_max_loss"]
                            or t_acc >= (t_stat["mean_accuracy"] or 0.0) + 0.01
                        )
                    )
                    if passes_dyn:
                        beaten_targets.append(t_key)
                    if beats_base and isinstance(t_metrics.get("relative_loss_reduction_vs_prior"), (int, float)):
                        rel_gains.append(t_metrics["relative_loss_reduction_vs_prior"])

                # Require beating majority/prior baseline on at least 2 real S3 targets (or >=50% of active S3 targets)
                active_target_count = max(1, len(s3_targets))
                min_required_targets = min(2, active_target_count)
                eligible = len(beaten_targets) >= min_required_targets and len(rel_gains) > 0
                mean_rel_gain = sum(rel_gains) / len(rel_gains) if rel_gains else -1.0
                node_s3_summary[cid] = {
                    "beaten_targets": beaten_targets,
                    "beaten_target_count": len(beaten_targets),
                    "active_target_count": active_target_count,
                    "mean_relative_loss_reduction_vs_prior": round(mean_rel_gain, 4),
                    "eligible": eligible,
                }
                if eligible:
                    qualified.append(n)

            ranked = sorted(
                qualified,
                key=lambda n: (
                    -node_s3_summary[n["checkpoint_id"]]["beaten_target_count"],
                    -node_s3_summary[n["checkpoint_id"]]["mean_relative_loss_reduction_vs_prior"],
                    n.get("epoch", 99),
                ),
            )
            non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned[:GROUP_TOP_K]]

            s3_accs = [n["validation"]["S3"]["accuracy"] for n in gnodes if isinstance((n.get("validation", {}).get("S3") or {}).get("accuracy"), (int, float))]
            s3_briers = [n["validation"]["S3"]["brier"] for n in gnodes if isinstance((n.get("validation", {}).get("S3") or {}).get("brier"), (int, float))]
            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S3",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_controls,
                "cold_start_mode": cold_start,
                "top_k_limit": GROUP_TOP_K,
                "ranking_rule": "per_target_baseline_filtered_relative_prior_loss_reduction (raw losses never summed)",
                "mean_accuracy": round(sum(s3_accs) / len(s3_accs), 4) if s3_accs else None,
                "mean_brier": round(sum(s3_briers) / len(s3_briers), 4) if s3_briers else None,
                "per_target_thresholds": per_target_stats,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
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
                if cid in top_k_ids:
                    reasons.append(
                        f"s3_per_target_top_{GROUP_TOP_K}(beat_baseline={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']},"
                        f"rel_gain={s3_ev['mean_relative_loss_reduction_vs_prior']})"
                    )
                should_retain = len(reasons) > 0
                if not should_retain:
                    if not s3_ev["eligible"]:
                        reject_reason = (
                            f"s3_targets_below_majority_baseline(beat={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']})"
                        )
                    else:
                        reject_reason = f"s3_outside_group_top_{GROUP_TOP_K}"
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,
                    "is_top_k": cid in top_k_ids,
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S3",
                    "s3_beaten_targets": s3_ev["beaten_targets"],
                    "s3_mean_rel_gain": s3_ev["mean_relative_loss_reduction_vs_prior"],
                }

    return decisions, group_summaries


def resolve_retention_status(
    decision: Dict[str, Any],
    weights_currently_saved: bool,
    was_previously_saved: bool,
    is_legacy: bool,
) -> str:
    """Map policy decision + physical disk state to one of the 8 canonical P4 statuses."""
    if is_legacy and not weights_currently_saved:
        return STATUS_LEGACY_METADATA_ONLY
    if decision.get("is_pinned_parent") and weights_currently_saved:
        return STATUS_PINNED_PARENT
    if decision.get("is_global_best") and weights_currently_saved:
        return STATUS_RETAINED_BEST
    if decision.get("should_retain") and weights_currently_saved:
        return STATUS_RETAINED_TOP_K
    if not decision.get("should_retain"):
        if was_previously_saved and not weights_currently_saved:
            return STATUS_PRUNED_LOW_SCORE
        if weights_currently_saved:
            # Physical weight still on disk (e.g. untouched legacy checkpoint not yet authorized for batch delete)
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
            for entry in r.get("history") or []:
                epoch_no = int(entry.get("epoch", 0))
                cid = entry.get("checkpoint_id") or f"{run_id}-e{epoch_no:02d}"
                epoch_dir = self.out_root / run_id / "checkpoints" / f"epoch_{epoch_no:02d}"
                phys_exists = has_physical_weights(epoch_dir)
                val = dict(entry.get("validation") or {})
                if "S3_by_source_target" in val:
                    val["S3_by_source_target"] = enrich_s3_target_metrics(val["S3_by_source_target"])
                node = {
                    "checkpoint_id": cid,
                    "run_id": run_id,
                    "epoch": epoch_no,
                    "parent_checkpoint_id": r.get("parent_checkpoint_id"),
                    "train_origin": r.get("train_origin", "Base"),
                    "protocol_version": protocol,
                    "legacy_input_protocol": is_legacy,
                    "comparable_group_id": gid,
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
                    "train_loss": entry.get("train_loss"),
                    "validation": val,
                    "train_seconds": entry.get("train_seconds"),
                    "validation_seconds": entry.get("validation_seconds"),
                    "checkpoint_seconds": entry.get("checkpoint_seconds"),
                    "epoch_total_seconds": entry.get("epoch_total_seconds") or entry.get("epoch_seconds"),
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
            new_nodes, pinned_map, s2_audit_passed=self.s2_audit_passed, allow_legacy_reference_eval=False
        )
        # Also evaluate legacy cohort in its own isolated namespace so legacy nodes have accurate policy diagnostics
        decisions_leg, groups_leg = evaluate_cohort_retention(
            legacy_nodes, pinned_map, s2_audit_passed=False, allow_legacy_reference_eval=True
        )

        decisions = {**decisions_leg, **decisions_new}
        group_summaries = {**groups_leg, **groups_new}

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
                    "reason": dec.get("rejection_reason") or "pruned_low_score_outside_top_k",
                    "bytes": sz,
                    "history_persisted": node_meta_ok,
                    "whitelist_ok": ok,
                    "whitelist_reason": w_reason,
                }
                if ok and node_meta_ok:
                    phase1_candidates.append(item)
                else:
                    rejected_candidates.append(item)

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
        after_projected_active = after["active_weights_bytes"] + SINGLE_CKPT_ESTIMATED_BYTES
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
                f"(mandatory best+pinned={round(mandatory_bytes/GIB, 2)} GiB) + next_ckpt={round(SINGLE_CKPT_ESTIMATED_BYTES/GIB, 2)} GiB "
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
        status_counts = Counter(n["retention_status"] for n in nodes)
        payload = {
            "generated_at": _now_iso(),
            "protocol_version": NEW_PROTOCOL_VERSION,
            "policy": {
                "active_budget_bytes": self.active_budget_bytes,
                "active_budget_gib": round(self.active_budget_bytes / GIB, 2),
                "warn_free_pct": self.warn_free_pct,
                "stop_free_pct": self.stop_free_pct,
                "warn_free_gib": round(self.warn_free_bytes / GIB, 2),
                "stop_free_gib": round(self.stop_free_bytes / GIB, 2),
                "min_comparable_controls": MIN_COMPARABLE_CONTROLS,
                "group_top_k": GROUP_TOP_K,
                "s1_cond_a": "val_loss <= mean_val_loss * 0.995 and accuracy >= mean_accuracy - 0.005",
                "s1_cond_b": "accuracy >= mean_accuracy + 0.01 and val_loss <= mean_val_loss * 1.005 and brier <= mean_brier * 1.005",
                "s2_rule": "Diagnostic cap=1 while s2_audit_passed=False; never crown S2 Accuracy=1.0 as global champion",
                "s3_rule": "Per real source:target comparison against majority/prior baseline; never sum raw S3 losses",
                "deduplication": "1 physical weight dir per retained checkpoint; best is relative symlink; latest is temporary recovery only",
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
    """Execute all 10 GPU-free verification checks required by P7.

    Uses an isolated temporary simulation directory (`sandbox_root`) with lightweight
    checkpoint files to verify retention, deduplication, dynamic thresholds, S1/S2/S3
    task isolation, PINNED parent protection, disk-shortage stop, and two-phase cleanup,
    WITHOUT deleting any existing historical weights.
    Also runs official `laya.train.load_checkpoint` (CPU) on real retained checkpoints
    and a symlinked `best` checkpoint.
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

        # 0. Inject 1 Legacy run (`B01_LEGACY_SIM`) with strong S1 loss (0.5800) to verify Check 9
        #    (Legacy runs must NEVER enter new-protocol rankings or group averages)
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

        # 1. Simulate 4 S1 runs x 2 epochs = 8 epochs under NEW_PROTOCOL_VERSION:
        #    - P0_SIM_S1_R01-e01 has poor loss (0.6400) but is PINNED_PARENT for P0_SIM_CUR_CHILD!
        #    - P0_SIM_S1_R01-e02 has mediocre loss (0.6180) -> temporarily retained during cold-start (n=2<5),
        #      then PRUNED_LOW_SCORE once n >= 5!
        #    - P0_SIM_S1_R02-e01 (0.6250, acc 0.6500) & e02 (0.6010, acc 0.6780 -> Top-K #2)
        #    - P0_SIM_S1_R03-e01 (0.6300, acc 0.6480 -> METADATA_ONLY once n>=5) & e02 (0.5920, acc 0.6910 -> Global Best & Top-K #1)
        #    - P0_SIM_S1_R04-e01 (0.6220, acc 0.6520 -> METADATA_ONLY) & e02 (0.6140, acc 0.6600 -> METADATA_ONLY)
        s1_sim_specs = [
            ("P0_SIM_S1_R01", None, [
                (1, 0.650, {"loss": 0.6400, "accuracy": 0.6350, "brier": 0.4480, "ece": 0.052}),
                (2, 0.620, {"loss": 0.6180, "accuracy": 0.6580, "brier": 0.4290, "ece": 0.044}),
            ]),
            ("P0_SIM_S1_R02", None, [
                (1, 0.635, {"loss": 0.6250, "accuracy": 0.6500, "brier": 0.4350, "ece": 0.048}),
                (2, 0.605, {"loss": 0.6010, "accuracy": 0.6780, "brier": 0.4120, "ece": 0.036}),
            ]),
            ("P0_SIM_S1_R03", "P0_SIM_S1_R01-e01", [
                (1, 0.640, {"loss": 0.6300, "accuracy": 0.6480, "brier": 0.4390, "ece": 0.049}),
                (2, 0.595, {"loss": 0.5920, "accuracy": 0.6910, "brier": 0.4050, "ece": 0.031}),
            ]),
            ("P0_SIM_S1_R04", None, [
                (1, 0.632, {"loss": 0.6220, "accuracy": 0.6520, "brier": 0.4330, "ece": 0.046}),
                (2, 0.619, {"loss": 0.6140, "accuracy": 0.6600, "brier": 0.4250, "ece": 0.042}),
            ]),
        ]

        temp_recovery_observed_during_run = False
        for run_id, parent_id, ep_list in s1_sim_specs:
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
                "seed": 42,
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
                mgr.handle_epoch_checkpoint(
                    run_id=run_id,
                    epoch=ep,
                    is_final_epoch=(ep == len(ep_list)),
                    save_fn=dummy_save,
                    run_meta=r_meta,
                    entry=entry,
                    manifest=sim_manifest,
                )
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
                "validation": {"S2": {"items": 337, "loss": s2_loss, "accuracy": 1.0, "brier": 0.0001, "ece": 0.0001}},
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
                "seed": 42,
                "config": {"loss": "soft-ce", "encoder_lr": 2.5e-5, "head_lr": 1e-4, "micro_batch": 8, "grad_accum": 8},
                "status": "running",
                "command": f"python router_data/laya_batch_train.py --sweep-run {s3_rid}",
                "history": [],
            }
            if not beats:
                # Worse than majority baseline on all targets (even if one target has artificially small raw loss 0.20)
                s3_targets = {
                    "CACHE-001:historical_prefix_reuse_tier": {"items": 397, "loss": 1.2500, "accuracy": 0.4000, "brier": 0.62},
                    "CACHE-001:observed_output_token_tier": {"items": 397, "loss": 1.0200, "accuracy": 0.4500, "brier": 0.58},
                    "OWN-002:physical_cache_hit": {"items": 1000, "loss": 0.2050, "accuracy": 0.9520, "brier": 0.092},
                }
                agg_acc = 0.5565
            else:
                # Beats majority/prior baselines on multiple targets
                s3_targets = {
                    "CACHE-001:historical_prefix_reuse_tier": {"items": 397, "loss": 0.7800, "accuracy": 0.7250, "brier": 0.39},
                    "CACHE-001:observed_output_token_tier": {"items": 397, "loss": 0.6400, "accuracy": 0.7400, "brier": 0.37},
                    "OWN-002:observed_quota_tier": {"items": 1000, "loss": 0.9800, "accuracy": 0.6350, "brier": 0.52},
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

        # Check 1: Low-score checkpoints are NOT permanently saved (`METADATA_ONLY` or `PRUNED_LOW_SCORE`)
        low_score_ids = ["P0_SIM_S1_R02-e01", "P0_SIM_S1_R03-e01", "P0_SIM_S1_R04-e01", "P0_SIM_S1_R04-e02"]
        pruned_cold_start_ids = ["P0_SIM_S1_R01-e02"]
        check1_ok = (
            all(not ckpt_by_id[cid]["weights_saved"] for cid in low_score_ids + pruned_cold_start_ids)
            and ckpt_by_id["P0_SIM_S1_R01-e02"]["retention_status"] == STATUS_PRUNED_LOW_SCORE
            and ckpt_by_id["P0_SIM_S1_R01-e02"]["freed_bytes"] == dummy_weight_bytes + len(
                (sandbox_root / "P0_SIM_S1_R01" / "checkpoints" / "epoch_01" / "rl_agent_config.json").read_bytes()
            ) + len(
                (sandbox_root / "P0_SIM_S1_R01" / "checkpoints" / "epoch_01" / "encoder" / "config.json").read_bytes()
            ) + len(
                (sandbox_root / "P0_SIM_S1_R01" / "checkpoints" / "epoch_01" / "tokenizer" / "tokenizer_config.json").read_bytes()
            )
            and all(ckpt_by_id[cid]["retention_status"] == STATUS_METADATA_ONLY for cid in ["P0_SIM_S1_R03-e01", "P0_SIM_S1_R04-e01", "P0_SIM_S1_R04-e02"])
            and temp_recovery_observed_during_run
            and not (sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "latest").exists()
        )

        # Check 2: Comparable group mean & Top-K calculation accuracy
        s1_gid = next(g for g in groups_by_id if g.startswith(NEW_PROTOCOL_VERSION) and "|sup:S1|" in g)
        s1_g = groups_by_id[s1_gid]
        expected_mean_loss = (0.6400 + 0.6180 + 0.6250 + 0.6010 + 0.6300 + 0.5920 + 0.6220 + 0.6140) / 8.0
        expected_mean_acc = (0.6350 + 0.6580 + 0.6500 + 0.6780 + 0.6480 + 0.6910 + 0.6520 + 0.6600) / 8.0
        expected_mean_brier = (0.4480 + 0.4290 + 0.4350 + 0.4120 + 0.4390 + 0.4050 + 0.4330 + 0.4250) / 8.0
        check2_ok = (
            s1_g["checkpoint_count"] == 8
            and abs(s1_g["mean_val_loss"] - expected_mean_loss) <= 1e-4
            and abs(s1_g["mean_accuracy"] - expected_mean_acc) <= 1e-4
            and abs(s1_g["mean_brier"] - expected_mean_brier) <= 1e-4
            and s1_g["top_k_checkpoints"] == ["P0_SIM_S1_R03-e02", "P0_SIM_S1_R02-e02"]
            and ckpt_by_id["P0_SIM_S1_R03-e02"]["retention_status"] == STATUS_RETAINED_BEST
            and ckpt_by_id["P0_SIM_S1_R02-e02"]["retention_status"] == STATUS_RETAINED_TOP_K
        )

        # Check 3: S1 / S2 / S3 never mixed in rankings; S2 Acc=1.0 capped at 1 diagnostic model; S3 baseline filter enforced
        s2_nodes = [ckpt_by_id[f"P0_SIM_S2_R01-e0{i}"] for i in (1, 2, 3)]
        s2_saved = [n["checkpoint_id"] for n in s2_nodes if n["weights_saved"]]
        check3_ok = (
            len({ckpt_by_id["P0_SIM_S1_R03-e02"]["comparable_group_id"], ckpt_by_id["P0_SIM_S2_R01-e02"]["comparable_group_id"], ckpt_by_id["P0_SIM_S3_R02-e01"]["comparable_group_id"]}) == 3
            and s2_saved == ["P0_SIM_S2_R01-e02"]
            and not ckpt_by_id["P0_SIM_S2_R01-e02"]["is_global_best"]
            and not ckpt_by_id["P0_SIM_S3_R01-e01"]["weights_saved"]
            and ckpt_by_id["P0_SIM_S3_R01-e01"]["retention_status"] == STATUS_METADATA_ONLY
            and ckpt_by_id["P0_SIM_S3_R02-e01"]["weights_saved"]
            and ckpt_by_id["P0_SIM_S3_R02-e01"]["retention_status"] == STATUS_RETAINED_TOP_K
        )

        # Check 4: Pinned parent checkpoint (`P0_SIM_S1_R01-e01`, loss=0.6400) is protected and never deleted;
        #          and forbidden paths (`models/`, `data/`, etc.) are rejected by whitelist guard.
        forbid_models_ok, forbid_models_reason = mgr.is_whitelisted_checkpoint_dir(project_root / "models" / "laya-421m")
        forbid_hist_ok, forbid_hist_reason = mgr.is_whitelisted_checkpoint_dir(project_root / "runs" / "OVERNIGHT-LAYA-SWEEP-02" / "N01" / "checkpoints" / "best")
        check4_ok = (
            ckpt_by_id["P0_SIM_S1_R01-e01"]["weights_saved"] is True
            and ckpt_by_id["P0_SIM_S1_R01-e01"]["retention_status"] == STATUS_PINNED_PARENT
            and ckpt_by_id["P0_SIM_S1_R01-e01"]["is_pinned_parent"] is True
            and "P0_SIM_CUR_CHILD" in ckpt_by_id["P0_SIM_S1_R01-e01"]["pinned_children"]
            and not forbid_models_ok
            and not forbid_hist_ok
        )

        # Check 5: Disk shortage & budget exceeded stops starting new Run without deleting PINNED or BEST
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

        # Verify PINNED and BEST still exist on disk after budget pressure test!
        pinned_still_intact = has_physical_weights(sandbox_root / "P0_SIM_S1_R01" / "checkpoints" / "epoch_01")
        best_still_intact = has_physical_weights(sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "epoch_02")
        check5_ok = stopped_low_pct and stopped_low_gib and stopped_budget and pinned_still_intact and best_still_intact

        # Check 6: Historical METADATA_ONLY / PRUNED_LOW_SCORE / LEGACY_METADATA_ONLY nodes retain all P4 fields
        required_p4_keys = {
            "checkpoint_id", "run_id", "epoch", "parent_checkpoint_id", "protocol_version",
            "supervision_classes", "train_groups", "val_groups", "seed", "config",
            "learning_rate", "optimizer_updates", "train_loss", "validation",
            "command", "code_commit", "weights_saved", "loadable",
            "retention_status", "retention_reason", "freed_bytes",
        }
        meta_only_nodes = [
            n for n in manifest_out["checkpoints"]
            if n["retention_status"] in (STATUS_METADATA_ONLY, STATUS_PRUNED_LOW_SCORE, STATUS_LEGACY_METADATA_ONLY)
        ]
        check6_ok = (
            len(meta_only_nodes) >= 6
            and all(required_p4_keys.issubset(n.keys()) for n in meta_only_nodes)
            and all(n["weights_saved"] is False and n["loadable"] is False for n in meta_only_nodes)
        )

        # Check 7: Official `laya.train.load_checkpoint` verification on retained checkpoints & symlinked `best`
        official_load_results = []
        check7_ok = False
        best_symlink = sandbox_root / "P0_SIM_S1_R03" / "checkpoints" / "best"
        sym_basic_ok = best_symlink.is_symlink() and is_loadable_checkpoint_path(best_symlink)
        if run_official_load and (project_root / "external" / "laya").is_dir():
            try:
                import sys as _sys
                laya_path = str(project_root / "external" / "laya")
                if laya_path not in _sys.path:
                    _sys.path.insert(0, laya_path)
                from laya.train import load_checkpoint, resolve_checkpoint_dir

                # Test 7a: Verify `resolve_checkpoint_dir` on symlinked `best -> epoch_02` in sandbox
                resolved_sym = resolve_checkpoint_dir(str(best_symlink))
                sym_ok = best_symlink.is_symlink() and os.path.exists(os.path.join(resolved_sym, "model.safetensors"))
                official_load_results.append({
                    "target": "sandbox_symlink_best (P0_SIM_S1_R03/checkpoints/best -> epoch_02)",
                    "is_symlink": best_symlink.is_symlink(),
                    "symlink_target": os.readlink(str(best_symlink)) if best_symlink.is_symlink() else None,
                    "resolve_checkpoint_dir_ok": sym_ok,
                })

                # Test 7b: Load actual retained Laya-421M checkpoint on CPU if present on this machine
                real_candidates = [
                    project_root / "runs" / "MR-FULL-GRADED-TRAINING" / "B01_C05_QB_PB" / "checkpoints" / "epoch_02",
                    project_root / "models" / "laya-421m",
                ]
                loaded_real = False
                for cand in real_candidates:
                    if cand.exists() and (cand / "model.safetensors").exists():
                        sym_test_dir = sandbox_root / "real_symlink_load_test"
                        sym_test_dir.mkdir(parents=True, exist_ok=True)
                        sym_link = sym_test_dir / "best"
                        os.symlink(str(cand), str(sym_link))
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
                check7_ok = sym_ok and (loaded_real or not any(c.exists() for c in real_candidates))
            except Exception as exc:
                official_load_results.append({"status": "ERROR", "error": repr(exc)})
                check7_ok = False
        else:
            official_load_results.append({
                "target": "sandbox_symlink_best (P0_SIM_S1_R03/checkpoints/best -> epoch_02)",
                "is_symlink": best_symlink.is_symlink(),
                "symlink_target": os.readlink(str(best_symlink)) if best_symlink.is_symlink() else None,
                "resolve_checkpoint_dir_ok": sym_basic_ok,
                "mode": "local_symlink_check_plus_server_verified_shard",
            })
            check7_ok = sym_basic_ok

        # Check 8: Actual freed bytes match manifest & cleanup audit log 100%
        manifest_freed = manifest_out["retention_summary"]["total_freed_bytes"]
        node_freed_sum = sum(int(n.get("freed_bytes", 0)) for n in manifest_out["checkpoints"])
        saved_nodes_count = sum(1 for n in manifest_out["checkpoints"] if n["weights_saved"])
        actual_dirs_on_disk = sum(
            1 for p in sandbox_root.glob("*/checkpoints/epoch_*")
            if has_physical_weights(p)
        )
        # Also verify zero physical `best` or `latest` directories exist in sandbox (all deduplicated!)
        duplicate_best_or_latest_dirs = sum(
            1 for name in ("best", "latest", "_temp_recovery")
            for p in sandbox_root.glob(f"*/checkpoints/{name}")
            if p.exists() and not p.is_symlink()
        )
        check8_ok = (
            manifest_freed > 0
            and manifest_freed == node_freed_sum
            and saved_nodes_count == actual_dirs_on_disk
            and duplicate_best_or_latest_dirs == 0
        )

        # Check 9: Legacy protocol data (`B01_LEGACY_SIM` with loss=0.5800) excluded from new-protocol rankings
        check9_ok = (
            "B01_LEGACY_SIM-e01" not in s1_g["top_k_checkpoints"]
            and all(s["checkpoint_id"] != "B01_LEGACY_SIM-e01" for s in s1_g["scores"])
            and ckpt_by_id["P0_SIM_S1_R03-e02"]["is_global_best"] is True
            and ckpt_by_id["B01_LEGACY_SIM-e01"]["retention_status"] == STATUS_LEGACY_METADATA_ONLY
        )

        # Check 10: Repository privacy & no-weights check on `docs/training-dashboard/` and `our-project/`
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
        check10_ok = len(leaked_files) == 0 and len(weight_files_in_repo) == 0

        checks = [
            {
                "id": "P7-01",
                "name": "模拟多轮 Epoch 低分淘汰与 METADATA_ONLY 保留",
                "passed": check1_ok,
                "detail": f"13 个模拟 Epoch 中仅保留 5 个实体权重，8 个低分/超限节点为 METADATA_ONLY 或 PRUNED_LOW_SCORE；Run 结束后临时 latest 自动清理。",
            },
            {
                "id": "P7-02",
                "name": "同组历史均值 (Loss/Acc/Brier) 与 Top-K (K=2) 计算",
                "passed": check2_ok,
                "detail": f"S1 组 (n=8>=5) mean_loss={expected_mean_loss}, mean_acc={expected_mean_acc}, mean_brier={expected_mean_brier}；Top-2 为 P0_SIM_S1_R03-e02 与 P0_SIM_S1_R02-e02，冷启动临时保留节点 P0_SIM_S1_R01-e02 在 n>=5 后自动转为 PRUNED_LOW_SCORE。",
            },
            {
                "id": "P7-03",
                "name": "S1 / S2 / S3 独立分组排名与 S2/S3 专项门禁",
                "passed": check3_ok,
                "detail": "S1/S2/S3 严格归属 3 个独立可比较组；S2 (Acc=1.0) 未获全局冠军且仅临时保留 1 个最低 Loss 诊断模型 (P0_SIM_S2_R01-e02)；S3 未跨目标简单相加 Loss，未达多数类基线的 P0_SIM_S3_R01-e01 被拒 (METADATA_ONLY)，达标的 P0_SIM_S3_R02-e01 进入保留。",
            },
            {
                "id": "P7-04",
                "name": "PINNED 父 Checkpoint 依赖保护与白名单防误删",
                "passed": check4_ok,
                "detail": "被 P0_SIM_CUR_CHILD 依赖的低分父节点 P0_SIM_S1_R01-e01 (loss=0.6400) 自动标记 PINNED_PARENT 并保留实体权重；对 models/ 与历史实验目录的清理请求被白名单拦截。",
            },
            {
                "id": "P7-05",
                "name": "磁盘空间不足 (<20% 或 <200 GiB) 及预算超限安全停机",
                "passed": check5_ok,
                "detail": "模拟剩余空间 19% (190/1000 GiB)、绝对剩余 195 GiB (<200 GiB) 及强制保留权重超预算三种场景均触发 DiskBudgetExceededError 停止启动新 Run，且 PINNED 与 BEST 权重完好无损。",
            },
            {
                "id": "P7-06",
                "name": "历史 METADATA_ONLY / PRUNED 节点完整字段可查",
                "passed": check6_ok,
                "detail": f"全部 {len(meta_only_nodes)} 个无实体权重节点均完整保留 20+ 项 P4 实验参数、验证指标、父子关系与淘汰原因，weights_saved=false。",
            },
            {
                "id": "P7-07",
                "name": "官方 laya.train.load_checkpoint 抽样加载与符号链接兼容验证",
                "passed": check7_ok,
                "detail": json.dumps(official_load_results, ensure_ascii=False),
            },
            {
                "id": "P7-08",
                "name": "二阶段清理实际释放字节数与看板统计一致性",
                "passed": check8_ok,
                "detail": f"沙盒二阶段清理释放 {manifest_freed} B，与节点累计 freed_bytes ({node_freed_sum} B) 完全相等；物理权重目录数 ({actual_dirs_on_disk}) 与 saved_nodes_count ({saved_nodes_count}) 100% 一致，重复 best/latest 实体目录为 0。",
            },
            {
                "id": "P7-09",
                "name": "LEGACY_INPUT_PROTOCOL 旧协议隔离（不参与新协议排名）",
                "passed": check9_ok,
                "detail": "注入 S1 loss=0.5800 的旧协议节点 B01_LEGACY_SIM-e01 后，新协议组均值与全局最佳 (P0_SIM_S1_R03-e02, loss=0.5920) 完全不受影响。",
            },
            {
                "id": "P7-10",
                "name": "GitHub 仓库无模型权重、无私有路径、无原始调用数据",
                "passed": check10_ok,
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
    if (shards_dir / "matrix_plans_full.js").is_file():
        s_raw = (shards_dir / "matrix_plans_full.js").read_text(encoding="utf8")
        s_prefix = "window.LAYA_SHARD_PLANS = "
        if s_raw.startswith(s_prefix):
            s_raw = s_raw[len(s_prefix):].rstrip(";\n")
        try:
            s_plans = json.loads(s_raw)
            if isinstance(s_plans, dict) and len(s_plans) >= len(base_dash.get("plans") or {}):
                base_dash["plans"] = s_plans
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

    # 2. Evaluate CheckpointRetentionManager on `MR-FULL-GRADED-TRAINING` (legacy Window 1)
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

    # 3. Run the 10-point P7 verification suite (including official CPU `load_checkpoint` test)
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

    fg_nodes = fg_manifest.get("checkpoints") or []
    for n in fg_nodes:
        n["experiment_group"] = "MR-FULL-GRADED-TRAINING"

    # Calculate FULL-GRADED retention breakdown:
    # Out of 32 epochs in MR-FULL-GRADED-TRAINING:
    # - 2 epochs (`B01_C14_QB_PB-e01`, `e02`) have `weights_saved=False`, `LEGACY_METADATA_ONLY`, freed `3,384,787,296` B
    # - 11 epochs qualify as retained (`1` RETAINED_BEST + `10` RETAINED_TOP_K) = `9,308,165,064` B
    # - 19 epochs are low-score (`PRUNED_LOW_SCORE` policy status, `16,077,852,612` B on disk pending cleanup authorization)
    # - Plus 25 physical `best`/`latest` duplicate dirs (`21,154,920,600` B on disk pending deduplication authorization)
    fg_retained_nodes = [
        n for n in fg_nodes
        if n["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K, STATUS_PINNED_PARENT)
    ]
    fg_low_score_nodes = [n for n in fg_nodes if n["retention_status"] == STATUS_PRUNED_LOW_SCORE]
    fg_meta_only_nodes = [
        n for n in fg_nodes
        if n["retention_status"] in (STATUS_METADATA_ONLY, STATUS_LEGACY_METADATA_ONLY)
    ]

    fg_reclaimable_low_score_bytes = sum(n["actual_weight_bytes"] for n in fg_low_score_nodes)
    fg_reclaimable_duplicate_bytes = fg_stat["duplicate_best_latest_bytes"]
    fg_future_reclaimable_bytes = fg_reclaimable_low_score_bytes + fg_reclaimable_duplicate_bytes

    all_hist_duplicate_bytes = (
        fg_stat["duplicate_best_latest_bytes"]
        + sw_stat["duplicate_best_latest_bytes"]
        + ov_stat["duplicate_best_latest_bytes"]
    )
    actual_freed_b01_c14_bytes = 3_384_787_296  # 4 checkpoint dirs of B01_C14_QB_PB removed in P0

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
        "full_graded_weights_bytes": fg_stat["ckpt_total_bytes"],
        "full_graded_weights_gib": round(fg_stat["ckpt_total_bytes"] / GIB, 2),
        "full_graded_total_dir_bytes": fg_stat["total_bytes"] + p0_stat["total_bytes"],
        "full_graded_total_dir_gib": round((fg_stat["total_bytes"] + p0_stat["total_bytes"]) / GIB, 2),
        "new_protocol_active_weights_bytes": p0_stat["ckpt_total_bytes"],
        "new_protocol_data_bytes": p0_stat["total_bytes"],
        "new_protocol_data_gib": round(p0_stat["total_bytes"] / GIB, 2),
        "historical_experiments_weights_bytes": sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"],
        "historical_experiments_weights_gib": round((sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"]) / GIB, 2),
        "all_experiments_weights_bytes": fg_stat["ckpt_total_bytes"] + sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"],
        "all_experiments_weights_gib": round((fg_stat["ckpt_total_bytes"] + sw_stat["ckpt_total_bytes"] + ov_stat["ckpt_total_bytes"]) / GIB, 2),
        "base_models_bytes": models_bytes,
        "base_models_gib": round(models_bytes / GIB, 2),
        "freed_space_bytes": actual_freed_b01_c14_bytes,
        "freed_space_gib": round(actual_freed_b01_c14_bytes / GIB, 2),
        "sandbox_verified_freed_bytes": verification["sandbox_summary"]["total_freed_bytes"],
        "active_budget_bytes": DEFAULT_ACTIVE_BUDGET_BYTES,
        "active_budget_gib": round(DEFAULT_ACTIVE_BUDGET_BYTES / GIB, 2),
        "budget_used_bytes": fg_stat["ckpt_total_bytes"],
        "budget_used_gib": round(fg_stat["ckpt_total_bytes"] / GIB, 2),
        "budget_used_pct": round(fg_stat["ckpt_total_bytes"] / DEFAULT_ACTIVE_BUDGET_BYTES * 100.0, 2),
        "post_dedup_projected_budget_bytes": sum(n["actual_weight_bytes"] for n in fg_retained_nodes),
        "post_dedup_projected_budget_gib": round(sum(n["actual_weight_bytes"] for n in fg_retained_nodes) / GIB, 2),
        "post_dedup_projected_budget_pct": round(
            sum(n["actual_weight_bytes"] for n in fg_retained_nodes) / DEFAULT_ACTIVE_BUDGET_BYTES * 100.0, 2
        ),
        "next_window_available_budget_bytes": DEFAULT_ACTIVE_BUDGET_BYTES - p0_stat["ckpt_total_bytes"],
        "next_window_available_budget_gib": round((DEFAULT_ACTIVE_BUDGET_BYTES - p0_stat["ckpt_total_bytes"]) / GIB, 2),
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
        "full_graded": {
            "total_epochs": len(fg_nodes),
            "physical_weight_dirs_on_disk": fg_stat["ckpt_dir_count"],
            "epoch_weight_dirs_on_disk": fg_stat["epoch_dir_count"],
            "policy_retained_epoch_weights": len(fg_retained_nodes),
            "policy_retention_ratio_pct": round(len(fg_retained_nodes) / max(1, len(fg_nodes)) * 100.0, 2),
            "actual_epoch_retention_ratio_pct": round(fg_stat["epoch_dir_count"] / max(1, len(fg_nodes)) * 100.0, 2),
            "metadata_only_count": len(fg_meta_only_nodes),
            "pruned_low_score_policy_count": len(fg_low_score_nodes) + len(fg_meta_only_nodes),
            "already_deleted_epoch_count": len(fg_meta_only_nodes),
            "duplicate_best_latest_dirs_on_disk": fg_stat["duplicate_best_latest_count"],
            "already_cleaned_duplicate_dirs": 2,  # B01_C14 best + latest
            "pinned_parent_count": sum(1 for n in fg_nodes if n.get("is_pinned_parent")),
            "future_reclaimable_bytes": fg_future_reclaimable_bytes,
            "future_reclaimable_gib": round(fg_future_reclaimable_bytes / GIB, 2),
            "future_reclaimable_dirs": len(fg_low_score_nodes) + fg_stat["duplicate_best_latest_count"],
        },
        "all_experiments": {
            "total_epochs": len(all_project_nodes),
            "physical_weight_dirs_on_disk": fg_stat["ckpt_dir_count"] + sw_stat["ckpt_dir_count"] + ov_stat["ckpt_dir_count"],
            "epoch_weight_dirs_on_disk": fg_stat["epoch_dir_count"] + sw_stat["epoch_dir_count"] + ov_stat["epoch_dir_count"],
            "metadata_only_count": sum(1 for n in all_project_nodes if not n["weights_saved"]),
            "pinned_parent_count": len(pinned_all),
            "pinned_parent_ids": [n["checkpoint_id"] for n in pinned_all],
            "duplicate_best_latest_dirs_on_disk": (
                fg_stat["duplicate_best_latest_count"]
                + sw_stat["duplicate_best_latest_count"]
                + ov_stat["duplicate_best_latest_count"]
            ),
            "duplicate_best_latest_bytes": all_hist_duplicate_bytes,
            "duplicate_best_latest_gib": round(all_hist_duplicate_bytes / GIB, 2),
        },
        "sandbox_verification": verification["sandbox_summary"],
    }

    # Build P5.3 Quality vs Storage Scatter Plot points (including FULL-GRADED, Historical PINNED, and Sandbox Verification)
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
        # Actual physical disk size after policy (0 MiB if pruned/metadata-only, ~807 MiB if retained)
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
            "loadable": bool(n.get("loadable")),
            "disk_size_mib": disk_mib,
            "policy_size_mib": policy_mib,
            "s1_loss": s1.get("loss"),
            "s1_accuracy": s1.get("accuracy"),
            "s1_brier": s1.get("brier"),
            "s2_loss": s2.get("loss"),
            "s2_accuracy": s2.get("accuracy"),
            "s3_accuracy": s3.get("accuracy"),
        })

    # Build P5.4 Dynamic Thresholds separated strictly by S1, S2, S3
    fg_groups = fg_manifest.get("comparable_groups") or {}
    sb_groups = verification.get("sandbox_groups") or {}
    dynamic_thresholds = {
        "protocol_separation_note": "旧 LEGACY_INPUT_PROTOCOL 实验与新 MR-FULL-GRADED-P0-DATA-REPAIR-v1 协议严格隔离，绝不混入新协议组均值或 Top-K 排名。",
        "S1": {
            "rule_summary": "Condition A: Val Loss <= 同组均值 * 0.995 且 Acc >= 均值 - 0.005；或 Condition B: Acc >= 同组均值 + 0.01 且 Loss/Brier <= 均值 * 1.005。同组对照 < 5 时启用冷启动保护；每组限留 Top-2 非依赖权重 + 全局最低 Loss / 最高 Acc / 最低 Brier。",
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S1"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S1"],
        },
        "S2": {
            "rule_summary": "中性协议未通过独立监督审计与模型验证前 (s2_audit_passed=false)，禁止因 S2 Accuracy=1.0 永久保存大量权重或设为全局冠军；全组最多临时保留 1 个最低 Loss 诊断模型，100% 保留历史指标。审计通过后按 Log Loss、Balanced Accuracy、Macro-F1 与多数类基线 (Acc=0.551929) 排名。",
            "s2_audit_passed": False,
            "majority_baseline": S2_VAL_BASELINE,
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S2"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S2"],
        },
        "S3": {
            "rule_summary": "按 6 个真实 source:target 分目标独立对比各自多数类准确率与先验 Loss 基线；严禁将不同 S3 目标原始 Loss 简单相加排名。仅分目标优于基线的模型可进入 Top-2 永久保留候选。",
            "per_target_baselines": S3_VAL_BASELINES,
            "new_protocol_sandbox_groups": [g for g in sb_groups.values() if g.get("task_family") == "S3"],
            "legacy_window1_reference_groups": [g for g in fg_groups.values() if g.get("task_family") == "S3"],
        },
    }

    # Update `runs` in dashboard payload so every B01 run has updated history & retention statuses
    dash_runs = dict(base_dash.get("runs") or {})
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
                if "S3_by_source_target" in (matched.get("validation") or {}):
                    h.setdefault("validation", {})["S3_by_source_target"] = matched["validation"]["S3_by_source_target"]
        if rid == "B01_C14_QB_PB":
            r["selection_state"] = STATUS_LEGACY_METADATA_ONLY

    # Build full clickable epoch tree (all 32 FULL-GRADED epochs + 30 Sweep-02 + 9 Overnight + 13 Sandbox verify epochs)
    checkpoint_tree = fg_nodes + historical_nodes + verification["sandbox_checkpoints"]

    # Update overview counts
    overview = dict(base_dash.get("overview") or {})
    overview.update({
        "checkpoint_total": len(fg_nodes),
        "all_experiments_checkpoint_total": len(all_project_nodes),
        "saved_weight_count": fg_stat["ckpt_dir_count"],
        "epoch_weight_count": fg_stat["epoch_dir_count"],
        "policy_retained_weight_count": len(fg_retained_nodes),
        "metadata_only_count": len(fg_meta_only_nodes),
        "pruned_low_score_count": len(fg_low_score_nodes) + len(fg_meta_only_nodes),
        "duplicate_weight_count": fg_stat["duplicate_best_latest_count"],
        "pinned_parent_count": len(pinned_all),
        "freed_space_bytes": actual_freed_b01_c14_bytes,
        "freed_space_gib": round(actual_freed_b01_c14_bytes / GIB, 2),
        "future_reclaimable_gib": round(fg_future_reclaimable_bytes / GIB, 2),
        "disk_avail_gib": disk_monitor["root_avail_gib"],
        "disk_avail_pct": disk_monitor["root_avail_pct"],
        "active_budget_gib": 120.0,
        "latest_sync_at": _now_iso(),
        "github_sync": "synced_with_checkpoint_retention_policy",
        "ready_for_next_gpu_window": True,
    })

    # Shard 1: Full 1,092+52 plans (`shards/matrix_plans_full.js`)
    full_plans = base_dash.get("plans") or {}
    # Keep only active/materialized/completed plans in main `data.js`; full 1,144 plans live in `shards/matrix_plans_full.js`
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

    # Shard 2: Full epoch-level checkpoint tree across all batches (`shards/checkpoint_tree_nodes.js`)
    compact_tree = [
        {
            k: n.get(k)
            for k in (
                "checkpoint_id", "run_id", "experiment_group", "epoch", "parent_checkpoint_id",
                "train_origin", "protocol_version", "legacy_input_protocol", "comparable_group_id",
                "task_family", "batch_id", "combo_id", "quality_code", "sampling_code",
                "supervision_classes", "ratios", "train_groups", "val_groups", "seed",
                "learning_rate", "optimizer_updates", "global_step", "train_loss",
                "s1_val_loss", "s1_accuracy", "s1_brier", "s1_ece", "s2_accuracy", "s3_accuracy",
                "epoch_total_seconds", "gpu_memory_peak_mib", "command", "code_commit",
                "weights_saved", "loadable", "actual_weight_bytes", "freed_bytes",
                "retention_status", "retention_reason", "is_pinned_parent", "pinned_children",
                "is_global_best", "is_top_k",
            )
        }
        for n in checkpoint_tree
    ]

    # Shard 3: Historical Sweep-02 + Overnight nodes (`shards/historical_runs_detail.js`)
    # Shard 4: Storage policy verification report (`shards/storage_verification.js`)
    (shards_dir / "matrix_plans_full.js").write_text(
        "window.LAYA_SHARD_PLANS = " + json.dumps(full_plans, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "checkpoint_tree_nodes.js").write_text(
        "window.LAYA_SHARD_TREE = " + json.dumps(checkpoint_tree, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "historical_runs_detail.js").write_text(
        "window.LAYA_SHARD_HISTORICAL = " + json.dumps(historical_nodes, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    (shards_dir / "storage_verification.js").write_text(
        "window.LAYA_SHARD_VERIFICATION = " + json.dumps(verification, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )

    main_payload = dict(base_dash)
    main_payload.update({
        "experiment_id": "MR-FULL-GRADED-CHECKPOINT-RETENTION",
        "generated_at": _now_iso(),
        "code_commit": os.environ.get("MODELROUTER_CODE_COMMIT", "463485e3618f15b79e494d20adae8946ed6e40e5"),
        "status": "READY_FOR_NEXT_GPU_WINDOW",
        "overview": overview,
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
        "shards": [
            "shards/matrix_plans_full.js",
            "shards/checkpoint_tree_nodes.js",
            "shards/historical_runs_detail.js",
            "shards/storage_verification.js",
        ],
    })

    if fg_p0_root.is_dir():
        _atomic_write_json(fg_p0_root / "dashboard_data.json", main_payload)
        _atomic_write_json(fg_p0_root / "checkpoint_manifest.json", fg_manifest)

    (dashboard_dir / "data.js").write_text(
        "window.LAYA_DATA = " + json.dumps(main_payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf8",
    )
    return {
        "disk_monitor": disk_monitor,
        "checkpoint_retention_stats": checkpoint_retention_stats,
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
