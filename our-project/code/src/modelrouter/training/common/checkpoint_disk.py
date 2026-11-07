"""Checkpoint disk accounting, cleanup, and run-start resource policy."""
import json, os, shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from .checkpoint_metrics import *
from .checkpoint_metrics import _atomic_write_json, _now_iso
from .checkpoint_identity import *
from .checkpoint_identity import _rankable_node
from .checkpoint_policy import *

def is_whitelisted_checkpoint_dir(manager, target_dir: Path) -> Tuple[bool, str]:
    """Verify `target_dir` is strictly inside `<out_root>/<run_id>/checkpoints/<name>` and not forbidden."""
    try:
        resolved = Path(target_dir).resolve()
    except OSError as exc:
        return False, f"resolve_error:{exc}"

    try:
        rel = resolved.relative_to(manager.out_root)
    except ValueError:
        return False, "outside_authorized_out_root"

    parts = rel.parts
    if len(parts) != 3 or parts[1] != "checkpoints":
        return False, f"invalid_checkpoint_subpath:{rel}"

    full_str = str(resolved)
    for token in FORBIDDEN_PATH_TOKENS:
        # Allow if out_root itself was explicitly created in a test temp dir, but block any forbidden token in relative path
        if token in str(rel) or (token in full_str and token not in str(manager.out_root.name)):
            return False, f"forbidden_path_token:{token}"

    run_dir = manager.out_root / parts[0]
    if (run_dir / ".writing_lock").exists() or (resolved / ".writing_lock").exists():
        return False, "checkpoint_write_in_progress"

    return True, "whitelisted_ok"

def is_mandatory_checkpoint(
    manager,
    cid: str,
    dec: Dict[str, Any],
    node: Optional[Dict[str, Any]] = None,
    pinned_map: Optional[Dict[str, Any]] = None,
    run_status: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Return (True, reason) if this checkpoint is mandatory to retain and must NEVER be pruned or evicted."""
    # 1. Active in-flight running run
    if run_status not in ("completed", "early_stopped") or (node and node.get("run_status") not in ("completed", "early_stopped")):
        return True, "protected_active_running_run"

    # 2. Pinned parent for curriculum learning
    if (
        dec.get("is_pinned_parent")
        or (pinned_map and cid in pinned_map)
        or (node and node.get("is_pinned_parent"))
        or dec.get("retention_pool") == "PINNED_PARENT"
    ):
        p_info = pinned_map.get(cid) if pinned_map else None
        return True, f"protected_pinned_parent:{p_info or 'curriculum_dependency'}"

    # 3. Old Core Pool (permanent 5 core checkpoints)
    if cid in OLD_CORE_CHECKPOINT_IDS or dec.get("retention_pool") == "OLD_CORE_POOL":
        return True, "protected_old_core_pool"

    if not dec or (node and not _rankable_node(node)):
        return True, "protected_unscored_checkpoint"

    # 4. New Core Pool (dynamically retained ~15% post-Q012 quota)
    if dec.get("retention_pool") == "NEW_CORE_POOL":
        return True, "protected_new_core_pool_15pct"

    # 5. Global Best
    if dec.get("is_global_best"):
        return True, "protected_global_best"

    return False, None

def disk_status(manager, simulated_statvfs: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Query real-time filesystem capacity and active weight usage."""
    manager.out_root.mkdir(parents=True, exist_ok=True)
    if simulated_statvfs is not None:
        total_b = int(simulated_statvfs["total_bytes"])
        avail_b = int(simulated_statvfs["avail_bytes"])
        used_b = int(simulated_statvfs.get("used_bytes", total_b - avail_b))
    else:
        st = os.statvfs(str(manager.out_root))
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

    runs, nodes, pinned_map, decisions, _ = manager.load_and_evaluate_all()
    node_by_dir: Dict[str, Dict[str, Any]] = {}
    for n in nodes:
        node_by_dir[f"{n['run_id']}/checkpoints/epoch_{int(n['epoch']):02d}"] = n

    for ckroot in sorted(manager.out_root.glob("*/checkpoints")):
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

    stop_triggered = avail_pct < manager.stop_free_pct or avail_b < manager.stop_free_bytes
    warn_triggered = stop_triggered or avail_pct < manager.warn_free_pct or avail_b < manager.warn_free_bytes
    state = "STOP" if stop_triggered else ("WARNING" if warn_triggered else "OK")

    return {
        "checked_at": _now_iso(),
        "root_total_bytes": total_b,
        "root_used_bytes": used_b,
        "root_avail_bytes": avail_b,
        "root_avail_pct": avail_pct,
        "root_df_used_pct": df_used_pct,
        "active_budget_bytes": manager.active_budget_bytes,
        "active_weights_bytes": active_total_bytes,
        "active_budget_used_pct": round(active_total_bytes / manager.active_budget_bytes * 100.0, 2) if manager.active_budget_bytes > 0 else 0.0,
        "physical_checkpoint_count": physical_ckpt_count,
        "breakdown_bytes": {
            "retained_best_bytes": best_bytes,
            "pinned_parent_bytes": pinned_bytes,
            "retained_top_k_bytes": top_k_bytes,
            "temp_recovery_bytes": temp_bytes,
            "prunable_low_value_or_duplicate_bytes": prunable_bytes,
        },
        "thresholds": {
            "warn_free_pct": manager.warn_free_pct,
            "stop_free_pct": manager.stop_free_pct,
            "warn_free_bytes": manager.warn_free_bytes,
            "stop_free_bytes": manager.stop_free_bytes,
            "active_budget_bytes": manager.active_budget_bytes,
        },
        "disk_guard_state": state,
        "stop_triggered": stop_triggered,
        "warn_triggered": warn_triggered,
    }

def two_phase_cleanup(
    manager,
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
    runs, nodes, pinned_map, decisions, _ = manager.load_and_evaluate_all(manifest)
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

        run_root = manager.out_root / run_id
        ckroot = run_root / "checkpoints"
        if not ckroot.exists():
            continue

        run_is_running = r.get("status") not in ("completed", "early_stopped")
        history_persisted = (run_root / "run.json").is_file() and (run_root / "epoch_metrics.json").is_file()

        # 1. Check completed-run temporary recovery (`_temp_recovery` and non-symlink `latest`)
        best_epoch = select_run_best_epoch(r, load_or_default_baseline_0(manager.out_root), manager.s2_audit_passed)
        completed_best_exists = (best_epoch is not None
                                and has_physical_weights(ckroot / f"epoch_{best_epoch:02d}"))
        if not run_is_running and completed_best_exists:
            for tmp_name in ("_temp_recovery", "latest"):
                tdir = ckroot / tmp_name
                if tdir.exists() and not tdir.is_symlink() and tdir.is_dir():
                    ok, reason = manager.is_whitelisted_checkpoint_dir(tdir)
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
                ok, reason = manager.is_whitelisted_checkpoint_dir(best_dir)
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
        if run_is_running:
            # Active in-flight run: protect its epoch checkpoints and recovery assets during training
            continue

        for h in r.get("history") or []:
            ep = int(h.get("epoch", 0))
            cid = h.get("checkpoint_id") or f"{run_id}-e{ep:02d}"
            ep_dir = ckroot / f"epoch_{ep:02d}"
            if not has_physical_weights(ep_dir):
                continue
            dec = decisions.get(cid) or {}
            node = node_by_key.get((run_id, ep))
            is_mand, mand_reason = manager.is_mandatory_checkpoint(
                cid=cid, dec=dec, node=node, pinned_map=pinned_map, run_status=r.get("status")
            )
            if is_mand:
                rejected_candidates.append({
                    "run_id": run_id,
                    "checkpoint_id": cid,
                    "target_dir": str(ep_dir),
                    "reason": mand_reason,
                })
                continue
            if dec.get("should_retain"):
                continue

            ok, w_reason = manager.is_whitelisted_checkpoint_dir(ep_dir)
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
    #    evict lowest-score non-mandatory checkpoints until within budget (never evicting OLD_CORE_POOL,
    #    NEW_CORE_POOL, PINNED_PARENT, GLOBAL_BEST, or active RUNNING runs).
    planned_dirs = {x["target_dir"] for x in phase1_candidates}
    remaining_bytes = 0
    evictable_top_k: List[Tuple[float, Dict[str, Any]]] = []
    for n in nodes:
        if n.get("legacy_input_protocol") and not allow_legacy_cleanup:
            continue
        ep_dir = manager.out_root / n["run_id"] / "checkpoints" / f"epoch_{int(n['epoch']):02d}"
        if str(ep_dir) in planned_dirs or not has_physical_weights(ep_dir):
            continue
        sz = physical_dir_bytes(ep_dir)
        remaining_bytes += sz
        cid = n["checkpoint_id"]
        dec = decisions.get(cid) or {}
        run_status = n.get("run_status") or (runs.get(n["run_id"]) or {}).get("status")
        is_mand, mand_reason = manager.is_mandatory_checkpoint(
            cid=cid, dec=dec, node=n, pinned_map=pinned_map, run_status=run_status
        )
        if is_mand:
            continue
        ok, w_reason = manager.is_whitelisted_checkpoint_dir(ep_dir)
        run_root = manager.out_root / n["run_id"]
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

    if remaining_bytes > manager.active_budget_bytes and evictable_top_k:
        evictable_top_k.sort(key=lambda pair: (pair[0], pair[1]["checkpoint_id"]))
        for _sc, item in evictable_top_k:
            if remaining_bytes <= manager.active_budget_bytes:
                break
            phase1_candidates.append(item)
            remaining_bytes -= item["bytes"]

    # Phase 2: Execute verified deletions
    executed: List[Dict[str, Any]] = []
    total_freed_bytes = 0
    if not dry_run:
        for item in phase1_candidates:
            tpath = Path(item["target_dir"])
            ok, _ = manager.is_whitelisted_checkpoint_dir(tpath)
            if not ok or not item.get("history_persisted"):
                continue
            cid = item.get("checkpoint_id")
            dec = decisions.get(cid) or {}
            node = node_by_key.get((item.get("run_id"), item.get("epoch")))
            run_status = (runs.get(item.get("run_id")) or {}).get("status")
            is_mand, _ = manager.is_mandatory_checkpoint(
                cid=cid, dec=dec, node=node, pinned_map=pinned_map, run_status=run_status
            )
            if is_mand:
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
                run_path = manager.out_root / run_id / "run.json"
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
                    manager._sync_run_best_symlink(run_id, rdata)
                    _atomic_write_json(run_path, rdata)
                    _atomic_write_json(manager.out_root / run_id / "epoch_metrics.json", rdata.get("history") or [])

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
    _atomic_write_json(manager.out_root / "cleanup_audit_log.json", audit_log)
    if executed:
        manager.write_checkpoint_manifest(manifest=manifest)
    return audit_log

def pre_run_disk_check(
    manager,
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
    before = manager.disk_status(simulated_statvfs=simulated_statvfs)
    projected_active = before["active_weights_bytes"] + estimated_peak_bytes
    projected_free = before["root_avail_bytes"] - estimated_peak_bytes
    projected_free_pct = (
        round(projected_free / before["root_total_bytes"] * 100.0, 2)
        if before["root_total_bytes"] > 0 else 0.0
    )

    needs_cleanup = (
        projected_active > manager.active_budget_bytes
        or before["stop_triggered"]
        or projected_free < manager.stop_free_bytes
        or projected_free_pct < manager.stop_free_pct
    )
    cleanup_result = None
    if needs_cleanup:
        cleanup_result = manager.two_phase_cleanup(manifest=manifest, allow_legacy_cleanup=False, dry_run=False)
        # If simulated_statvfs was supplied, credit freed bytes back to simulated avail_bytes
        if simulated_statvfs is not None and cleanup_result["phase2_freed_bytes"] > 0:
            simulated_statvfs = dict(simulated_statvfs)
            simulated_statvfs["avail_bytes"] += cleanup_result["phase2_freed_bytes"]
            simulated_statvfs["used_bytes"] = max(
                0, simulated_statvfs.get("used_bytes", 0) - cleanup_result["phase2_freed_bytes"]
            )

    after = manager.disk_status(simulated_statvfs=simulated_statvfs)
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

    if after["stop_triggered"] or after_projected_free < manager.stop_free_bytes or after_projected_free_pct < manager.stop_free_pct:
        allowed = False
        status = "STOPPED_DISK_LOW_SPACE"
        reason = (
            f"Disk free space below hard stop threshold: avail={round(after['root_avail_bytes']/GIB, 2)} GiB "
            f"({after['root_avail_pct']}%), required >= {round(manager.stop_free_bytes/GIB, 1)} GiB and >= {manager.stop_free_pct}%"
        )
    elif after_projected_active > manager.active_budget_bytes:
        allowed = False
        status = "STOPPED_DISK_BUDGET"
        reason = (
            f"Active weight budget exceeded after cleanup: active={round(after['active_weights_bytes']/GIB, 2)} GiB "
            f"(mandatory best+pinned={round(mandatory_bytes/GIB, 2)} GiB) + run_peak={round(estimated_peak_bytes/GIB, 2)} GiB "
            f"> budget={round(manager.active_budget_bytes/GIB, 2)} GiB. Refusing to delete PINNED or global best models."
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
