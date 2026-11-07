"""Stable run identity, statistics, checkpoint paths, and Kev selection."""
import hashlib, json, math, os, random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from .checkpoint_metrics import *
from .checkpoint_metrics import _clip_improvement

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
        if link_path.is_symlink():
            link_path.unlink(missing_ok=True)
        return

    target_dir = parent / target_rel_name
    if not is_loadable_checkpoint_path(target_dir):
        if link_path.is_symlink():
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
    classes = sorted(run_meta.get("supervision_classes") or (run_meta.get("train_groups") or {}).keys() or [family])
    if val_groups:
        val_sig = "+".join(f"{key}:{val_groups[key]}" for key in sorted(val_groups))
    loss_name = (run_meta.get("config") or {}).get("loss", "soft-ce")
    return f"{protocol}|sup:{'+'.join(classes)}|val:{val_sig}|metric:{loss_name}_raw_logit"


def primary_task_family(run_meta: Dict[str, Any]) -> str:
    """Return 'S1', 'S2', or 'S3' as the primary evaluation task family (never mixing tasks)."""
    classes = list(run_meta.get("supervision_classes") or sorted((run_meta.get("train_groups") or {}).keys()))
    if not classes:
        classes = sorted({stream for entry in run_meta.get("history") or [run_meta]
                          for stream in (entry.get("validation") or {}) if stream in ("S1", "S2", "S3")})
    if "S1" in classes:
        return "S1"
    if classes == ["S2"]:
        return "S2"
    return "S3"


def collect_pinned_parent_ids(
    runs: Dict[str, Dict[str, Any]],
    plans: Optional[Dict[str, Dict[str, Any]]] = None,
    explicit_pinned: Optional[Iterable[str]] = None,
    baseline_0: Optional[Dict[str, Any]] = None,
    s2_audit_passed: bool = False,
) -> Dict[str, List[str]]:
    """Return mapping `parent_checkpoint_id -> list of dependent child run_ids`."""
    pinned: Dict[str, List[str]] = defaultdict(list)
    for cid in (explicit_pinned or ()):
        if cid:
            pinned[str(cid)].append("EXPLICIT_PIN")
    for rid, r in (runs or {}).items():
        # Explicit retention declarations survive the process that supplied them.
        # Ordinary dependency statuses are still derived from current runs/plans.
        for entry in r.get("history") or []:
            cid = entry.get("checkpoint_id")
            if cid and "EXPLICIT_PIN" in (entry.get("retention_reason") or ""):
                if "EXPLICIT_PIN" not in pinned[str(cid)]:
                    pinned[str(cid)].append("EXPLICIT_PIN")
        parent = r.get("parent_checkpoint_id")
        if parent and parent != "Base":
            if rid not in pinned[str(parent)]:
                pinned[str(parent)].append(rid)
    for pid, p in (plans or {}).items():
        parent = p.get("parent_checkpoint_id")
        if parent and parent != "Base":
            if pid not in pinned[str(parent)]:
                pinned[str(parent)].append(pid)
        parent_run = p.get("parent_run_id")
        if parent_run and p.get("continuation_mode") == "warm_start":
            child_run = (runs or {}).get(pid)
            if not child_run or child_run.get("status") not in ("completed", "early_stopped"):
                prun_data = (runs or {}).get(parent_run) or {}
                hist = prun_data.get("history") or []
                if hist:
                    best_ep_no = select_run_best_epoch(prun_data, baseline_0, s2_audit_passed)
                    if best_ep_no is None:
                        best_ep_no = prun_data.get("best_epoch")
                    best_cids = []
                    if best_ep_no is not None:
                        for h in hist:
                            if int(h.get("epoch", 0)) == int(best_ep_no):
                                best_cids.append(h.get("checkpoint_id"))
                    if not best_cids:
                        best_cids = [
                            h.get("checkpoint_id") for h in hist
                            if h.get("is_run_best_epoch") or h.get("is_best_epoch")
                        ]
                    for bcid in best_cids:
                        if bcid and pid not in pinned[str(bcid)]:
                            pinned[str(bcid)].append(f"{pid}(curriculum_child)")
                    pinned[f"{parent_run}:best"].append(f"{pid}(curriculum_child)")
                else:
                    pinned[f"{parent_run}-e02"].append(f"{pid}(curriculum_child)")
                    pinned[f"{parent_run}:best"].append(f"{pid}(curriculum_child)")
    return {k: sorted(v) for k, v in pinned.items()}


def _node_primary_sort_key(node: Dict[str, Any], task_family: str) -> Tuple[float, float, float, int]:
    """Sort key (ascending = better) for selecting the single best Epoch within a Run."""
    score = node.get("primary_score")
    v = (node.get("validation") or {}).get(task_family) or {}
    loss = v.get("loss")
    acc = v.get("accuracy")
    score_key = -(float(score) if _finite_metric(score) else -float("inf"))
    loss_key = float(loss) if _finite_metric(loss) else float("inf")
    return (
        loss_key if task_family == "S1" else score_key,
        score_key if task_family == "S1" else loss_key,
        -(float(acc) if _finite_metric(acc) else -1.0),
        int(node.get("epoch", 99)),
    )


def _finite_metric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _rankable_node(node: Dict[str, Any]) -> bool:
    family = node.get("task_family") or primary_task_family(node)
    metrics = (node.get("validation") or {}).get(family) or {}
    items = metrics.get("items")
    expected = (node.get("val_groups") or {}).get(family)
    fields = (("loss", "accuracy", "brier", "ece") if family == "S1"
              else ("loss", "accuracy", "balanced_accuracy", "macro_f1", "brier") if family == "S2"
              else ("loss", "accuracy"))
    return (all(_finite_metric(metrics.get(field)) for field in fields)
            and _finite_metric(items) and items > 0 and _finite_metric(expected) and expected == items
            and _finite_metric(node.get("primary_score")))


def select_run_best_epoch(run_meta: Dict[str, Any], baseline_0=None, s2_audit_passed=False) -> Optional[int]:
    """Use minimum observed S1 loss; keep the existing S2/S3 score order."""
    family = primary_task_family(run_meta)
    candidates = []
    for entry in run_meta.get("history") or []:
        validation = entry.get("validation") or {}
        metrics = validation.get(family) or {}
        if not _finite_metric(metrics.get("loss")):
            continue
        if family == "S1":
            tie_metrics = {key: value for key, value in metrics.items()
                           if key not in ("accuracy", "brier", "ece") or _finite_metric(value)}
            scores = compute_node_composite_scores({**validation, "S1": tie_metrics}, family, baseline_0, s2_audit_passed)
            candidates.append({**entry, "primary_score": scores["primary_score"]})
            continue
        if any(not _finite_metric(value) for key, value in metrics.items()
               if key in ("accuracy", "brier", "ece", "balanced_accuracy", "macro_f1") and value is not None):
            continue
        scores = compute_node_composite_scores(validation, family, baseline_0, s2_audit_passed)
        if _finite_metric(scores["primary_score"]):
            candidates.append({**entry, "primary_score": scores["primary_score"]})
    return int(min(candidates, key=lambda n: _node_primary_sort_key(n, family))["epoch"]) if candidates else None


KEV_SELECTION_VERSION = "KEV_FIXED_VAL_FOUR_METRIC_V1"
KEV_FIXED_VAL_PATH = "data/kev/公开数据/val.jsonl"
KEV_SCORE_WEIGHTS = {"nll": 0.45, "acc": 0.30, "brier": 0.15, "ece": 0.10}
KEV_RESEARCH_GROUPS = {
    "KEV-V8-C03": "HOMOLOGOUS_CONTINUATION", "KEV-V8-C04": "HOMOLOGOUS_CONTINUATION",
    "KEV-V8-C05": "STATE_ABLATION", "KEV-V8-C06": "STATE_ABLATION",
    "KEV-V8-C07": "LORA_RANK_ABLATION", "KEV-V8-C08": "LORA_RANK_ABLATION",
    "KEV-V8-C09": "V8_EXTENSION", "KEV-V8-C10": "S1_WEIGHT_ABLATION",
}
KEV_NECESSARY_CONTROL_IDS = set(KEV_RESEARCH_GROUPS) | {"KEV-V8-R01"}
KEV_WEIGHT_NAMES = ("head.pt", "adapter_model.bin", "adapter_model.safetensors")


def _kev_val_issue(metrics: Dict[str, Any]) -> Optional[str]:
    if metrics.get("evaluation_status") != "EVALUATED" or metrics.get("exit_code") != 0:
        return "completed_val_required"
    dataset = metrics.get("validation_set", "")
    if (metrics.get("validation_protocol") != "KEV_FIXED_VAL_JSONL"
            or metrics.get("dataset_split") != "val" or metrics.get("test_used") is not False
            or not dataset or not (dataset == KEV_FIXED_VAL_PATH or
                                    Path(dataset).is_absolute() and dataset.endswith("/" + KEV_FIXED_VAL_PATH))):
        return "project_fixed_val_required"
    coverage = metrics.get("coverage") or {}
    expected = {"requested_records": 8436, "evaluated_records": 8436,
                "requested_questions": 9330, "evaluated_questions": 9330,
                "rejected_records": 0, "truncated_records": 0}
    if any(coverage.get(k) != v for k, v in expected.items()):
        return "incomplete_or_different_coverage"
    clean = metrics.get("clean") or {}
    if clean.get("n") != 9330:
        return "incomplete_scored_questions"
    for key in KEV_SCORE_WEIGHTS:
        value = clean.get(key)
        upper = {"acc": 1, "ece": 1, "brier": 2}.get(key, math.inf)
        if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= upper:
            return "missing_or_invalid_" + key
    report = metrics.get("report") or {}
    for key in ("clean", "coverage"):
        if key in report and report[key] != metrics[key]:
            return "inconsistent_report_" + key
    return None


def compute_kev_selection_score(metrics: Dict[str, Any], reference_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Internal Kev retention score; C03 supplies the scale, never a paper metric.

    I_nll=(N0-N)/max(N0,1e-6), I_acc=(A-A0)/max(1-A0,.05),
    I_brier=(B0-B)/max(B0,1e-6), I_ece=(E0-E)/max(E0,.05).
    Each improvement is clipped to [-1,1]; score=100*(1+sum(weight*I)).
    NLL/Brier/ECE decrease and Accuracy increases. Missing values have no score.
    Ties: score descending, NLL ascending, Accuracy descending, Brier/ECE
    ascending, then stable candidate ID. No rounding is used for ranking.
    """
    result = {"version": KEV_SELECTION_VERSION, "purpose": "internal_checkpoint_retention",
              "reference_candidate_id": "KEV-V8-C03", "weights": dict(KEV_SCORE_WEIGHTS),
              "directions": {"nll": "lower", "acc": "higher", "brier": "lower", "ece": "lower"},
              "formula": "I_nll=(N0-N)/max(N0,1e-6); I_acc=(A-A0)/max(1-A0,.05); "
                         "I_brier=(B0-B)/max(B0,1e-6); I_ece=(E0-E)/max(E0,.05); "
                         "clip I to [-1,1]; score=100*(1+.45*I_nll+.30*I_acc+.15*I_brier+.10*I_ece)",
              "tie_rule": "score_desc,nll_asc,acc_desc,brier_asc,ece_asc,candidate_id_asc",
              "score": None, "rank": None, "status": "PENDING"}
    issue = _kev_val_issue(reference_metrics)
    if issue:
        result["reason"] = "c03_" + issue
        return result
    issue = _kev_val_issue(metrics)
    if issue:
        result["reason"] = issue
        return result
    for field in ("validation_set", "validation_protocol", "coverage"):
        if metrics[field] != reference_metrics[field]:
            result["reason"] = "different_" + field
            return result
    # Recorded per-task counts also identify the scored targets, when supplied.
    reports = [m.get("report") or {} for m in (metrics, reference_metrics)]
    task_counts = [{k: v.get("n") for k, v in r.get("tasks", {}).items()} for r in reports]
    policy_fields = ("version", "nll", "nll_floor", "renormalize_returned_probabilities")
    policies = [{k: r.get("metric_policy", {}).get(k) for k in policy_fields} for r in reports]
    if task_counts[0] != task_counts[1] or policies[0] != policies[1]:
        result["reason"] = "different_prediction_targets_or_metric_policy"
        return result
    ref, clean = reference_metrics["clean"], metrics["clean"]
    scales = {"nll": max(ref["nll"], 1e-6), "acc": max(1 - ref["acc"], .05),
              "brier": max(ref["brier"], 1e-6), "ece": max(ref["ece"], .05)}
    improvements = {k: _clip_improvement((clean[k] - ref[k] if k == "acc" else ref[k] - clean[k]) / scales[k])
                    for k in KEV_SCORE_WEIGHTS}
    result.update(status="COMPARABLE", reason=None, reference_metrics={k: ref[k] for k in KEV_SCORE_WEIGHTS},
                  scales=scales, improvements=improvements,
                  score=100 * (1 + sum(KEV_SCORE_WEIGHTS[k] * improvements[k] for k in KEV_SCORE_WEIGHTS)))
    return result


def _kev_recipe_issue(candidate: Dict[str, Any]) -> Optional[str]:
    """Use existing recipe identities and actual training records, without new digests."""
    recipe = candidate.get("recipe") or {}
    required = ("run_id", "candidate_id", "source_git_sha", "upstream_git_sha", "base_model",
                "init_from", "parent_init_source", "data_path", "data_identity",
                "validation_set", "command", "checkpoint_path", "retraining")
    missing = [k for k in required if not recipe.get(k) or
               isinstance(recipe[k], str) and recipe[k].strip().upper() in ("N/A", "UNKNOWN", "NONE", "NULL")]
    if missing:
        return "incomplete_recipe:" + ",".join(missing)
    for key in ("candidate_id", "init_from", "data_path", "checkpoint_path"):
        if recipe[key] != candidate.get(key):
            return "inconsistent_recipe_" + key
    if recipe["run_id"] != candidate.get("name") or recipe.get("test_used") is not False:
        return "inconsistent_recipe_run_or_split"
    if recipe["validation_set"] != KEV_FIXED_VAL_PATH:
        return "inconsistent_recipe_val"
    parameters = candidate.get("training_parameters") or {}
    if any(parameters.get(k) is None for k in ("lr", "lora", "epochs", "batch", "accum", "seed",
                                               "dtype", "head_lr", "weight_decay", "lora_targets", "max_state")):
        return "incomplete_recorded_training_parameters"
    training = candidate.get("training_metrics") or {}
    if any(not _finite_metric(training.get(k)) or training[k] <= 0
           for k in ("optimizer_steps", "records_seen", "requested_records", "wall_seconds")):
        return "incomplete_recorded_training_metrics"
    if training["records_seen"] != training["requested_records"]:
        return "incomplete_training_exposure"
    if (not _finite_metric(candidate.get("loss")) or not candidate.get("finished_at")
            or not candidate["metrics"].get("evaluated_at") or not candidate["metrics"].get("report_path")):
        return "incomplete_recorded_loss_or_val_location"
    return None


def evaluate_kev_retention(candidates: List[Dict[str, Any]], *, project_root: Path,
                           apply: bool = False, persist=None,
                           protected_paths: Iterable[str] = (), protected_ids: Iterable[str] = ()) -> Dict[str, Any]:
    """Write selection/retention into the original candidates, using save_queue as persist.

    Groups follow the existing research goals or explicit retention_group. Each
    group retains ceil(.15*N) independent completed runs plus required scientific
    representatives; these protections can exceed the core quota. C03/C04 remain.
    Variant names describe a ratio or setting, not scientific necessity; the
    original C-series, R01 S1-only continuation and explicit scientific flags
    supply that evidence.
    Unknown base revision remains N/A with a recorded reproduction limitation;
    the actual base/parent paths, data identity and training recipe are required.
    Report mode never deletes. Apply persists all original records before unlink
    and records each result through the same callback. Only known Kev weight files
    directly inside an explicit runs checkpoint are removed; directories remain.
    released_bytes counts allocated bytes of successfully unlinked last-link files;
    removed_weight_bytes counts their logical size. Both are zero on a repeated call.
    Runtime/Serving users outside this queue supply protected paths or IDs.
    """
    root = Path(project_root).resolve()
    paths = {c["candidate_id"]: root / c["checkpoint_path"] for c in candidates if c.get("checkpoint_path")}
    protected = {root / p for p in protected_paths}
    # Parents remain available for pending work and the recorded child recipes.
    protected.update(root / c["init_from"] for c in candidates if c.get("init_from"))
    ids = set(protected_ids) | OLD_CORE_CHECKPOINT_IDS | {"KEV-V8-C03", "KEV-V8-C04", "KEV-V8-R01"}
    reference = next((c.get("metrics", {}) for c in candidates if c["candidate_id"] == "KEV-V8-C03"), {})
    groups = defaultdict(list)
    prior = {c["candidate_id"]: dict(c.get("retention") or {}) for c in candidates}
    for c in candidates:
        cid = c["candidate_id"]
        selection = compute_kev_selection_score(c.get("metrics") or {}, reference)
        group = c.get("retention_group") or KEV_RESEARCH_GROUPS.get(cid)
        selection["group"] = group
        if c.get("candidate_kind") == "SELECTION":
            selection = {**(c.get("selection") or {}), **selection}
            # Keep C11's existing best-Accuracy/NLL observations alongside its non-run status.
            selection.update(status="PENDING", score=None, reason="selection_record_not_a_training_run")
        elif (c.get("status") != "COMPLETED" or c.get("training_status") != "COMPLETED"
              or c.get("evaluation_status", "EVALUATED") != "EVALUATED"
              or c.get("training_exit_code", 0) != 0):
            selection.update(status="PENDING", score=None, reason="completed_consistent_training_required")
        elif not group:
            selection.update(status="PENDING", score=None, reason="research_group_not_recorded")
        elif sum(other.get("name") == c.get("name") or other["candidate_id"] == cid
                 for other in candidates) != 1:
            selection.update(status="PENDING", score=None, reason="ambiguous_run_identity")
        c["selection"] = selection
        if selection["score"] is not None:
            groups[group].append(c)
    kept, representatives, summaries = set(), set(), {}
    def sort_key(c):
        m = c["metrics"]["clean"]
        return (-c["selection"]["score"], m["nll"], -m["acc"], m["brier"], m["ece"], c["candidate_id"])
    for group, members in sorted(groups.items()):
        ranked = sorted(members, key=sort_key)
        quota = math.ceil(NEW_CORE_POOL_RATIO * len(ranked))
        kept.update(c["candidate_id"] for c in ranked[:quota])
        representatives.add(ranked[0]["candidate_id"])
        # Original C-series and R01 identify necessary contrasts; ratio names alone do not.
        for rank, c in enumerate(ranked, 1):
            c["selection"]["rank"] = rank
            if c["candidate_id"] in KEV_NECESSARY_CONTROL_IDS:
                representatives.add(c["candidate_id"])
        summaries[group] = {"eligible_runs": len(ranked), "core_quota": quota, "ratio": NEW_CORE_POOL_RATIO,
                            "ranked_ids": [c["candidate_id"] for c in ranked]}
    deletions = []
    for c in candidates:
        cid, selection = c["candidate_id"], c["selection"]
        path = paths.get(cid)
        files = [path / name for name in KEV_WEIGHT_NAMES if (path / name).is_file()] if path else []
        reasons = []
        if cid in ids or c.get("checkpoint_id") in ids:
            reasons.append("explicit_or_continuation_protection")
        if path and (path.resolve().is_relative_to(root / "models") or any(
                path.resolve().is_relative_to(p.resolve()) or p.resolve().is_relative_to(path.resolve()) for p in protected)):
            reasons.append("base_import_serving_or_parent_path")
        for flag in ("protected", "scientific_representative", "is_scientific_best", "is_serving",
                     "is_base_model", "is_imported", "is_old_core", "is_curriculum_parent", "recovery_in_use",
                     "validation_in_use", "training_in_use"):
            if c.get(flag):
                reasons.append(flag)
        if any(c.get(k) in ("RUNNING", "EVALUATING", "VALIDATING", "RECOVERING")
               for k in ("status", "training_status", "evaluation_status")):
            reasons.append("active_training_validation_or_recovery")
        if cid in representatives:
            reasons.append("necessary_scientific_representative")
        revision = (c.get("recipe") or {}).get("base_revision")
        revision_unknown = revision is None or (isinstance(revision, str) and
            revision.strip().upper() in ("", "N/A", "UNKNOWN", "NONE", "NULL"))
        result = {"status": "PENDING", "reason": selection.get("reason"), "protection_reasons": reasons,
                  "weight_files": [str(f) for f in files], "weights_present": bool(files),
                  "applied": apply, "released_bytes": 0, "freed_bytes": 0, "removed_weight_bytes": 0,
                  "total_released_bytes": prior[cid].get("total_released_bytes", 0),
                  "removed_files": list(prior[cid].get("removed_files", [])), "planned_action": None,
                  "pruned_at": prior[cid].get("pruned_at"), "updated_at": prior[cid].get("updated_at"),
                  "base_revision": "N/A" if revision_unknown else revision,
                  "retraining_limitations": ["Base revision is not recorded; reproduction requires the recorded local "
                      "base and parent weights. Exact revision or byte equality is not promised."] if revision_unknown else []}
        c["retention"] = result
        if reasons:
            result.update(status="PROTECTED", reason=";".join(reasons))
        elif not files:
            if prior[cid].get("status") == STATUS_PRUNED_LOW_SCORE and prior[cid].get("removed_files"):
                result.update(status=STATUS_PRUNED_LOW_SCORE, reason="previously_recorded_pruning")
            elif (c.get("weights_saved") is False or prior[cid].get("status") == "NOT_SAVED"
                  or c.get("candidate_kind") == "SELECTION"):
                result.update(status="NOT_SAVED", reason="recorded_not_saved")
            else:
                result["reason"] = "no_weight_entity_or_saved_record"
        elif selection["score"] is None:
            pass
        elif cid in kept:
            result.update(status="RETAINED", reason="group_core_15pct")
        else:
            issue = _kev_recipe_issue(c)
            if not issue and c.get("weights_saved") is False:
                issue = "inconsistent_saved_record_and_weight_entity"
            names = {f.name for f in files} | {Path(p).name for p in result["removed_files"]}
            if not issue and ("head.pt" not in names or not names.intersection(KEV_WEIGHT_NAMES[1:])):
                issue = "incomplete_weight_entity_without_removal_record"
            if not issue and (not path.is_relative_to(root / "runs") or path == root / "runs"
                              or path.resolve() != path or any(f.is_symlink() or f.stat().st_nlink != 1 for f in files)):
                issue = "ambiguous_or_shared_weight_entity"
            if not issue and any(other is not c and other.get("checkpoint_path")
                                 and (root / other["checkpoint_path"]).resolve() == path.resolve() for other in candidates):
                issue = "shared_candidate_checkpoint"
            if issue:
                result["reason"] = issue
            else:
                result.update(reason="report_only" if not apply else "awaiting_original_record_persistence",
                              planned_action=STATUS_PRUNED_LOW_SCORE)
                if apply and persist is not None:
                    deletions.append((c, [(f, f.stat()) for f in files]))
                elif apply:
                    result["reason"] = "original_queue_persistence_required"
    if persist is not None:
        persist(candidates)
    for c, files in deletions:
        result = c["retention"]
        for f, recorded_stat in files:
            try:
                stat = f.lstat()
                if (f.is_symlink() or stat.st_nlink != 1
                        or (stat.st_dev, stat.st_ino, stat.st_size) !=
                           (recorded_stat.st_dev, recorded_stat.st_ino, recorded_stat.st_size)):
                    raise OSError("weight entity changed during original record persistence")
                f.unlink()
            except OSError as exc:
                result.update(status="PENDING", reason=f"weight_removal_failed:{exc}")
                break
            result["removed_files"].append(str(f))
            result["released_bytes"] += stat.st_blocks * 512
            result["removed_weight_bytes"] += stat.st_size
        else:
            result.update(status=STATUS_PRUNED_LOW_SCORE, reason="low_group_rank_unprotected", planned_action=None,
                          pruned_at=_now_iso())
        result["total_released_bytes"] += result["released_bytes"]
        result["freed_bytes"] = result["released_bytes"]
        result["updated_at"] = _now_iso()
        persist(candidates)
    return {"version": KEV_SELECTION_VERSION, "apply": apply, "applied": apply, "groups": summaries,
            "decisions": {c["candidate_id"]: c["retention"] for c in candidates},
            "released_bytes": sum(c["retention"]["released_bytes"] for c in candidates),
            "freed_bytes": sum(c["retention"]["released_bytes"] for c in candidates),
            "removed_weight_bytes": sum(c["retention"]["removed_weight_bytes"] for c in candidates)}
