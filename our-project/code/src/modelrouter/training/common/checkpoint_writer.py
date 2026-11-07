"""Persist, finalize, and publish checkpoint state."""
import json, shutil
from collections import Counter
from typing import Any, Dict, Optional
from .checkpoint_metrics import *
from .checkpoint_metrics import _atomic_write_json, _now_iso
from .checkpoint_identity import *
from .checkpoint_policy import *

def _sync_run_best_symlink(manager, run_id: str, rdata: Dict[str, Any]) -> None:
    """Ensure `checkpoints/best` points to the true scientific best epoch directory ONLY if it exists physically.
    Never overwrite `best_epoch` with a suboptimal surviving epoch after pruning.
    """
    ckroot = manager.out_root / run_id / "checkpoints"
    history = rdata.get("history") or []

    scientific_best_ep = select_run_best_epoch(rdata, load_or_default_baseline_0(manager.out_root), manager.s2_audit_passed)

    # Preserve scientific best epoch in rdata (fallback to existing best_epoch if history is empty)
    if scientific_best_ep is not None:
        rdata["best_epoch"] = scientific_best_ep
    elif not history and rdata.get("best_epoch") is not None:
        scientific_best_ep = int(rdata["best_epoch"])

    if not ckroot.exists() or scientific_best_ep is None:
        if history and scientific_best_ep is None:
            rdata["best_epoch"] = None
        rdata["best_checkpoint"] = None
        if ckroot.exists():
            update_safe_symlink(ckroot / "best", None)
        return

    # 2. Check if the true scientific best epoch physically exists
    best_ep_dir = ckroot / f"epoch_{scientific_best_ep:02d}"
    if has_physical_weights(best_ep_dir):
        update_safe_symlink(ckroot / "best", f"epoch_{scientific_best_ep:02d}")
        rdata["best_checkpoint"] = f"{run_id}/checkpoints/best"
    else:
        # The scientific best epoch lacks physical weights (was pruned or not saved).
        # Strictly remove/clear `checkpoints/best` link. Never redirect to a suboptimal surviving epoch!
        update_safe_symlink(ckroot / "best", None)
        rdata["best_checkpoint"] = None

def handle_epoch_checkpoint(
    manager,
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
    run_root = manager.out_root / run_id
    ckroot = run_root / "checkpoints"
    ckroot.mkdir(parents=True, exist_ok=True)
    epoch_id = entry["checkpoint_id"]
    epoch_rel = f"epoch_{epoch:02d}"
    epoch_dir = ckroot / epoch_rel

    # Step 1: Persist metadata first so history is never lost even if weights are not saved
    entry["weights_saved"] = has_physical_weights(epoch_dir)
    entry["loadable"] = is_loadable_checkpoint_path(epoch_dir)
    entry["checkpoint_size_bytes"] = physical_dir_bytes(epoch_dir) if entry["weights_saved"] else 0
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

    best_epoch = select_run_best_epoch(run_meta, load_or_default_baseline_0(manager.out_root), manager.s2_audit_passed)
    if best_epoch is not None:
        run_meta["best_epoch"] = best_epoch
        for h in run_meta["history"]:
            h["is_run_best_epoch"] = h.get("epoch") == best_epoch
    _atomic_write_json(run_root / "epoch_metrics.json", run_meta["history"])
    _atomic_write_json(run_root / "run.json", run_meta)

    # Step 2: Evaluate retention across the cohort including this new epoch
    _runs, _nodes, pinned_map, decisions, group_summaries = manager.load_and_evaluate_all(manifest)
    dec = decisions.get(epoch_id) or {
        "should_retain": False,
        "is_pinned_parent": epoch_id in pinned_map,
        "is_global_best": False,
        "is_top_k": False,
        "retention_reasons": [],
        "rejection_reason": "not_qualified",
    }

    # Check physical disk safety limits before writing permanent weights
    d_stat = manager.disk_status()
    if d_stat["stop_triggered"] or d_stat["root_avail_bytes"] < manager.stop_free_bytes:
        raise DiskBudgetExceededError(
            f"[{run_id}] Refusing to save checkpoint {epoch_id}: "
            f"Disk free space ({round(d_stat['root_avail_bytes']/GIB, 2)} GiB) below hard limit {round(manager.stop_free_bytes/GIB, 2)} GiB."
        )
    within_budget = (d_stat["active_weights_bytes"] + SINGLE_CKPT_ESTIMATED_BYTES) <= manager.active_budget_bytes
    if not within_budget and dec.get("should_retain"):
        # Try cleaning displaced checkpoints first
        manager.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
        d_stat = manager.disk_status()
        if d_stat["stop_triggered"] or d_stat["root_avail_bytes"] < manager.stop_free_bytes:
            raise DiskBudgetExceededError(
                f"[{run_id}] Refusing to save checkpoint {epoch_id}: "
                f"Disk free space ({round(d_stat['root_avail_bytes']/GIB, 2)} GiB) below hard limit {round(manager.stop_free_bytes/GIB, 2)} GiB."
            )
        within_budget = (d_stat["active_weights_bytes"] + SINGLE_CKPT_ESTIMATED_BYTES) <= manager.active_budget_bytes

    is_pinned = bool(
        dec.get("is_pinned_parent")
        or epoch_id in pinned_map
        or f"{run_id}:best" in pinned_map
        or any(run_id in str(x) for x in (manager.explicit_pinned or ()))
        or any(epoch_id in str(x) for x in (manager.explicit_pinned or ()))
    )
    is_run_best_candidate = bool(
        epoch == best_epoch
        or is_final_epoch
        or dec.get("should_retain")
    )
    should_save_permanent = bool(is_pinned or (is_run_best_candidate and within_budget))
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
            if not has_physical_weights(epoch_dir):
                raise RuntimeError(
                    f"[{run_id}] FATAL: Verification failed after saving weights to {epoch_dir}! "
                    f"Physical weights missing or corrupt."
                )
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
        entry["weights_saved"] = has_physical_weights(epoch_dir)
        entry["loadable"] = is_loadable_checkpoint_path(epoch_dir)
        entry["was_previously_saved"] = bool(entry.get("was_previously_saved") or entry["weights_saved"])
        entry["checkpoint_size_bytes"] = physical_dir_bytes(epoch_dir) if entry["weights_saved"] else 0
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
    manager._sync_run_best_symlink(run_id, run_meta)
    _atomic_write_json(run_root / "run.json", run_meta)

    cleanup_log = manager.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
    # Reload updated history in case an earlier epoch of this same run was pruned
    updated_run = json.loads((run_root / "run.json").read_text(encoding="utf8"))
    run_meta["history"] = updated_run.get("history", run_meta["history"])
    run_meta["best_checkpoint"] = updated_run.get("best_checkpoint")
    run_meta["best_epoch"] = updated_run.get("best_epoch")
    return {
        "checkpoint_id": epoch_id,
        "weights_saved": entry["weights_saved"],
        "retention_status": entry["retention_status"],
        "retention_reason": entry["retention_reason"],
        "cleanup_log": cleanup_log,
        "group_summaries": group_summaries,
    }

def finalize_run_checkpoints(manager, run_id: str, run_meta: Dict[str, Any], manifest: Optional[Dict[str, Any]] = None) -> None:
    """Clean up temporary `latest` / `_temp_recovery` upon Run completion and sync `best` symlink."""
    run_root = manager.out_root / run_id
    ckroot = run_root / "checkpoints"
    manager._sync_run_best_symlink(run_id, run_meta)
    if (ckroot.exists() and run_meta.get("status") in ("completed", "early_stopped")
            and run_meta.get("best_checkpoint") is not None):
        temp_dir = ckroot / "_temp_recovery"
        if temp_dir.exists() and not temp_dir.is_symlink():
            shutil.rmtree(temp_dir)
        latest_link = ckroot / "latest"
        if latest_link.is_symlink():
            latest_link.unlink(missing_ok=True)
    _atomic_write_json(run_root / "run.json", run_meta)
    _atomic_write_json(run_root / "epoch_metrics.json", run_meta.get("history") or [])
    cleanup = manager.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
    if not cleanup["phase2_executed_count"]:
        manager.write_checkpoint_manifest(manifest=manifest)

def write_checkpoint_manifest(manager, manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write comprehensive `checkpoint_manifest.json` in `out_root` covering P4 & P5."""
    runs, nodes, pinned_map, _decisions, group_summaries = manager.load_and_evaluate_all(manifest)
    disk = manager.disk_status()
    baseline_0 = load_or_default_baseline_0(manager.out_root)
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
            "active_budget_bytes": manager.active_budget_bytes,
            "active_budget_gib": round(manager.active_budget_bytes / GIB, 2),
            "warn_free_pct": manager.warn_free_pct,
            "stop_free_pct": manager.stop_free_pct,
            "warn_free_gib": round(manager.warn_free_bytes / GIB, 2),
            "stop_free_gib": round(manager.stop_free_bytes / GIB, 2),
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
    _atomic_write_json(manager.out_root / "top5_core_checkpoint_manifest.json", top5_payload)
    if manager.out_root.parent.name == "runs":
        _atomic_write_json(manager.out_root.parent / "top5_core_checkpoint_manifest.json", top5_payload)
    _atomic_write_json(manager.out_root / "checkpoint_manifest.json", payload)

    return payload
