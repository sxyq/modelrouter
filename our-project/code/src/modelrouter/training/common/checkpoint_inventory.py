"""Read run records and evaluate checkpoint retention."""
import json, os
from typing import Any, Dict, List, Optional, Tuple
from .checkpoint_metrics import *
from .checkpoint_identity import *
from .checkpoint_policy import *

def load_and_evaluate_all(
    manager,
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
    for path in sorted(manager.out_root.glob("*/run.json")):
        try:
            saved = json.loads(path.read_text(encoding="utf8"))
            runs[path.parent.name] = saved
        except (OSError, json.JSONDecodeError):
            continue

    plans = (manifest or {}).get("plans") or {}
    if not plans and (manager.out_root / "experiment_matrix.json").exists():
        try:
            plans = json.loads((manager.out_root / "experiment_matrix.json").read_text(encoding="utf8")).get("plans") or {}
        except (OSError, json.JSONDecodeError):
            plans = {}

    baseline_0 = load_or_default_baseline_0(manager.out_root)
    pinned_map = collect_pinned_parent_ids(runs, plans, manager.explicit_pinned,
                                         baseline_0, manager.s2_audit_passed)

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
        dedup_sig = r.get("dedup_signature") or compute_run_dedup_signature(r, out_root=manager.out_root)
        for entry in r.get("history") or []:
            epoch_no = int(entry.get("epoch", 0))
            cid = entry.get("checkpoint_id") or f"{run_id}-e{epoch_no:02d}"
            epoch_dir = manager.out_root / run_id / "checkpoints" / f"epoch_{epoch_no:02d}"
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
                "run_status": r.get("status"),
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
        s2_audit_passed=manager.s2_audit_passed,
        allow_legacy_reference_eval=False,
        baseline_0=baseline_0,
        out_root=manager.out_root,
    )
    # Also evaluate legacy cohort in its own isolated namespace so legacy nodes have accurate policy diagnostics
    decisions_leg, groups_leg = evaluate_cohort_retention(
        legacy_nodes,
        pinned_map,
        s2_audit_passed=False,
        allow_legacy_reference_eval=True,
        baseline_0=baseline_0,
        out_root=manager.out_root,
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
