"""Configuration-matrix queue reconciliation and execution."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .checkpoint_retention import (
    GIB, LEGACY_PROTOCOL_VERSION, NEW_PROTOCOL_VERSION,
    CheckpointRetentionManager, DiskBudgetExceededError, compute_run_dedup_signature,
)
from .queue_support import _now_iso, _write_json, check_gpu_available, materialize_plan_on_demand

def build_ordered_queue(
    out_root: Path,
    manifest: Dict[str, Any],
    queue_state: Dict[str, Any],
    stages: Tuple[int, ...] = (0, 1, 2, 3, 4),
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Reconcile the 1,092-slot matrix and build the ordered execution queue across Stages 0..4."""
    plans = manifest.get("plans") or {}
    p0_by_base: Dict[str, Dict[str, Any]] = {}
    base_slots: Dict[str, Dict[str, Any]] = {}
    for pid, p in plans.items():
        b_id = p.get("base_run_id") or (pid[3:] if pid.startswith("P0_") else pid)
        if pid.startswith("P0_"):
            p0_by_base[b_id] = p
            base_slots.setdefault(b_id, p)
        else:
            base_slots[b_id] = p

    # Discover already completed new-protocol runs on disk
    completed_runs: Dict[str, Dict[str, Any]] = {}
    seen_signatures: Dict[str, str] = {}
    for rpath in sorted(out_root.glob("*/run.json")):
        try:
            rdata = json.loads(rpath.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            continue
        rid = rdata.get("run_id") or rpath.parent.name
        if rid == "R0" or rdata.get("legacy_input_protocol") or rdata.get("protocol_version") == LEGACY_PROTOCOL_VERSION:
            continue
        if rdata.get("status") in ("completed", "early_stopped"):
            completed_runs[rid] = rdata
            sig = compute_run_dedup_signature(rdata, out_root=out_root)
            seen_signatures.setdefault(sig, rid)

    skipped_runs = dict(queue_state.get("skipped_runs") or {})

    stage_buckets: Dict[int, List[Dict[str, Any]]] = {0: [], 1: [], 2: [], 3: [], 4: []}
    counts = Counter()

    def _slot_canon_order(item: Tuple[str, Dict[str, Any]]) -> Tuple[int, int, str]:
        b_id, bp = item
        p0_spec = p0_by_base.get(b_id)
        exec_id = p0_spec["run_id"] if p0_spec else f"P0_{b_id}"
        is_mat = bool((p0_spec or bp).get("materialized")) or (out_root / "train" / exec_id).is_dir()
        q_c = (p0_spec or bp).get("quality_code") or ""
        p_c = (p0_spec or bp).get("sampling_code") or ""
        is_qb_pb = (q_c == "QB" and p_c == "PB")
        return (0 if is_mat else 1, 0 if is_qb_pb else 1, b_id)

    for b_id, bp in sorted(base_slots.items(), key=_slot_canon_order):
        orig_status = str(bp.get("status") or "")
        elig_reason = str(bp.get("eligibility_reason") or "")
        is_ext = (
            not b_id.startswith("B0")
            or bp.get("batch_id") is None
            or "extension slot" in elig_reason
            or orig_status == "PENDING_PARENT_SELECTION"
        )
        if is_ext:
            p0_spec = p0_by_base.get(b_id)
            exec_id = p0_spec["run_id"] if p0_spec else f"P0_{b_id}"
            if exec_id in completed_runs or b_id in completed_runs:
                counts["NEW_PROTOCOL_COMPLETED"] += 1
            elif bool((p0_spec or bp).get("materialized")) or (out_root / "train" / exec_id).is_dir():
                counts["CPU_MATERIALIZED"] += 1
            else:
                counts["EXTENSION_UNDEFINED"] += 1
            continue
        if orig_status.startswith("BLOCKED"):
            counts["BLOCKED"] += 1
            continue

        p0_spec = p0_by_base.get(b_id)
        exec_id = p0_spec["run_id"] if p0_spec else f"P0_{b_id}"
        spec = dict(bp)
        if p0_spec:
            spec.update(p0_spec)
        spec["run_id"] = exec_id
        spec["base_run_id"] = b_id
        spec["protocol_version"] = NEW_PROTOCOL_VERSION
        spec["legacy_input_protocol"] = False

        if (exec_id in completed_runs or b_id in completed_runs
                or exec_id in (queue_state.get("completed_runs") or [])):
            counts["NEW_PROTOCOL_COMPLETED"] += 1
            continue

        sig = compute_run_dedup_signature(spec, out_root=out_root)
        if sig in seen_signatures:
            first_rid = seen_signatures[sig]
            skipped_runs[exec_id] = f"SKIPPED_IDENTICAL_DATA:{first_rid}"
            counts["SKIPPED"] += 1
            continue
        seen_signatures[sig] = exec_id

        is_mat = bool(spec.get("materialized")) or (out_root / "train" / exec_id).is_dir()
        counts["CPU_MATERIALIZED" if is_mat else "ELIGIBLE_UNMATERIALIZED"] += 1

        batch_id = spec.get("batch_id") or ""
        combo_id = spec.get("combo_id") or ""
        q_code = spec.get("quality_code") or ""
        p_code = spec.get("sampling_code") or ""
        sup = tuple(spec.get("supervision_classes") or spec.get("groups") or [])

        # Assign stage & priority key
        if exec_id == "P0_B02_C02_QB_PB":
            st = 0
            prio = (0, batch_id, combo_id)
        elif q_code == "QB" and p_code == "PB" and batch_id in ("B01", "B02", "B03", "B04"):
            st = 1
            # Prioritize S1-only (C01), S3-only (C03), S1+S3 (C07/C08/C09), then S1+S2+S3
            sup_rank = 0 if sup == ("S1",) else (1 if "S2" not in sup else 2)
            prio = (sup_rank, batch_id, combo_id)
        elif q_code == "QB" and p_code == "PB" and batch_id in ("B05", "B06", "B07"):
            st = 2
            sup_rank = 0 if sup == ("S1",) else (1 if "S2" not in sup else 2)
            prio = (sup_rank, batch_id, combo_id)
        else:
            st = 3
            sup_rank = 0 if sup == ("S1",) else (1 if "S2" not in sup else 2)
            prio = (0 if is_mat else 1, sup_rank, batch_id, combo_id, q_code, p_code)

        spec["_stage"] = st
        spec["_prio"] = prio
        stage_buckets[st].append(spec)

    queue_state["skipped_runs"] = skipped_runs
    ordered: List[Dict[str, Any]] = []
    for st in sorted(stages):
        bucket = stage_buckets.get(st) or []
        bucket.sort(key=lambda x: x["_prio"])
        ordered.extend(bucket)

    reconciliation = {
        "total_matrix_slots": len(base_slots),
        "legacy_completed": 16,
        "status_counts": dict(counts),
        "queued_count": len(ordered),
    }
    return ordered, reconciliation


def run_queue(
    project_root: Path,
    out_root: Path,
    manifest_path: Path,
    model_dir: Path,
    max_runs: Optional[int] = 10,
    epochs: int = 2,
    active_budget_gib: float = 120.0,
    stages: Tuple[int, ...] = (0, 1, 2, 3),
    sync_github_every: int = 0,
    allow_unmaterialized: bool = False,
) -> Dict[str, Any]:
    """Execute the FULL-GRADED automated training queue with pre-run checks and retention."""
    from scripts.fetch_live_status import build_training_history

    project_root = Path(project_root).resolve()
    out_root = Path(out_root).resolve()
    manifest_path = Path(manifest_path).resolve()
    model_dir = Path(model_dir).resolve()
    budget_bytes = int(active_budget_gib * GIB)

    state_path = out_root / "queue_state.json"
    queue_state: Dict[str, Any] = {}
    if state_path.is_file():
        try:
            queue_state = json.loads(state_path.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            queue_state = {}

    queue_state.setdefault("protocol_version", NEW_PROTOCOL_VERSION)
    queue_state.setdefault("started_at", _now_iso())
    queue_state.setdefault("completed_runs", [])
    queue_state.setdefault("skipped_runs", {})
    queue_state.setdefault("failed_runs", {})
    queue_state.setdefault("s2_audit_passed", False)
    queue_state["queue_status"] = "RUNNING_PREFLIGHT"
    _write_json(state_path, queue_state)

    # Step 1: Ensure BASELINE_0 (`baseline_0.json`) exists, has valid S1/S2/S3 metrics, and is frozen
    b0_path = out_root / "baseline_0.json"
    b0_valid = False
    if b0_path.is_file():
        try:
            b0_data = json.loads(b0_path.read_text(encoding="utf8"))
            b0_valid = isinstance((b0_data.get("S1") or {}).get("loss"), (int, float))
        except (OSError, json.JSONDecodeError):
            b0_valid = False
    if not b0_valid:
        cmd = [
            sys.executable,
            str(project_root / "router_data" / "laya_batch_train.py"),
            "--compute-baseline0",
            "--model-dir", str(model_dir),
            "--out-root", str(out_root),
            "--sweep-data-root", str(out_root),
            "--project-root", str(project_root),
        ]
        subprocess.run(cmd, check=True, cwd=str(project_root))

    manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    ordered, reconciliation = build_ordered_queue(out_root, manifest, queue_state, stages=stages)
    queue_state["reconciliation"] = reconciliation
    queue_state["queue_status"] = "RUNNING"
    _write_json(state_path, queue_state)

    mgr = CheckpointRetentionManager(
        out_root=out_root,
        active_budget_bytes=budget_bytes,
        s2_audit_passed=bool(queue_state.get("s2_audit_passed", False)),
    )

    executed_this_session: List[str] = []
    for spec in ordered:
        if max_runs is not None and len(executed_this_session) >= max_runs:
            queue_state["queue_status"] = "PAUSED_MAX_RUNS_REACHED"
            queue_state["stop_reason"] = f"Completed requested batch of {max_runs} runs"
            break

        run_id = spec["run_id"]
        data_rel = spec.get("data") or f"data/{run_id}"
        is_mat = bool(spec.get("materialized")) or (out_root / data_rel).is_dir() or (out_root / "data" / run_id).is_dir() or (out_root / "train" / run_id).is_dir()
        if not is_mat:
            if not allow_unmaterialized:
                continue
            try:
                ok_mat = materialize_plan_on_demand(project_root, out_root, manifest, manifest_path, run_id)
            except (OSError, ValueError) as exc:
                queue_state["failed_runs"][run_id] = {
                    "attempts": 2, "reason": "materialization_failed", "detail": str(exc),
                }
                _write_json(state_path, queue_state)
                continue
            if not ok_mat:
                continue

        # Check GPU availability
        gpu_ok, gpu_info = check_gpu_available()
        if not gpu_ok:
            queue_state["queue_status"] = "PAUSED_GPU_BUSY"
            queue_state["stop_reason"] = f"GPU busy or unavailable: {gpu_info}"
            _write_json(state_path, queue_state)
            break

        # Check disk & active weight budget before starting Run
        try:
            mgr.pre_run_disk_check(run_id=run_id, manifest=manifest)
        except DiskBudgetExceededError as exc:
            queue_state["queue_status"] = "PAUSED_DISK_OR_BUDGET_GUARD"
            queue_state["stop_reason"] = str(exc)
            _write_json(state_path, queue_state)
            break

        queue_state["current_run"] = run_id
        queue_state["interrupted_run"] = run_id
        queue_state["updated_at"] = _now_iso()
        _write_json(state_path, queue_state)

        # Execute Run via `router_data/laya_batch_train.py`
        run_epochs = int(spec.get("epochs") or epochs)
        cmd = [
            sys.executable,
            str(project_root / "router_data" / "laya_batch_train.py"),
            "--sweep-run", run_id,
            "--sweep-manifest", str(manifest_path),
            "--model-dir", str(model_dir),
            "--out-root", str(out_root),
            "--sweep-data-root", str(out_root),
            "--epochs", str(run_epochs),
            "--active-budget-gib", str(active_budget_gib),
            "--project-root", str(project_root),
        ]
        if queue_state.get("s2_audit_passed"):
            cmd.append("--s2-audit-passed")

        proc = subprocess.run(cmd, cwd=str(project_root))
        if proc.returncode == 0:
            if run_id not in queue_state["completed_runs"]:
                queue_state["completed_runs"].append(run_id)
            queue_state["current_run"] = None
            queue_state["interrupted_run"] = None
            executed_this_session.append(run_id)

            # Check if this was the Stage 0 S2 neutral-protocol verification run (`P0_B02_C02_QB_PB`)
            if run_id == "P0_B02_C02_QB_PB":
                r_file = out_root / run_id / "run.json"
                if r_file.is_file():
                    rdata = json.loads(r_file.read_text(encoding="utf8"))
                    s2_accs = [
                        ((h.get("validation") or {}).get("S2") or {}).get("accuracy")
                        for h in (rdata.get("history") or [])
                    ]
                    s2_losses = [
                        ((h.get("validation") or {}).get("S2") or {}).get("loss")
                        for h in (rdata.get("history") or [])
                    ]
                    s2_accs = [float(a) for a in s2_accs if isinstance(a, (int, float))]
                    s2_losses = [float(l) for l in s2_losses if isinstance(l, (int, float))]
                    still_100 = any(a >= 0.999 for a in s2_accs)
                    beats_maj = any(
                        a > 0.551929 and l < 0.687729
                        for a, l in zip(s2_accs, s2_losses)
                    )
                    queue_state["s2_audit_passed"] = bool((not still_100) and beats_maj)
                    queue_state["s2_neutral_verification"] = {
                        "run_id": run_id,
                        "verified_at": _now_iso(),
                        "epoch_accuracies": s2_accs,
                        "epoch_losses": s2_losses,
                        "majority_baseline_accuracy": 0.551929,
                        "prior_baseline_loss": 0.687729,
                        "still_100pct_separable": still_100,
                        "beats_majority_baseline": beats_maj,
                        "s2_audit_passed": bool((not still_100) and beats_maj),
                        "policy": (
                            "NORMAL_RANKING"
                            if ((not still_100) and beats_maj)
                            else "DIAGNOSTIC_ONLY (cap=1, excluded from global champion)"
                        ),
                    }
        else:
            prev_att = int((queue_state["failed_runs"].get(run_id) or {}).get("attempts", 0))
            queue_state["failed_runs"][run_id] = {
                "attempts": prev_att + 1,
                "returncode": proc.returncode,
                "failed_at": _now_iso(),
            }

        # Rebuild dashboard & manifest after each Run
        build_training_history(project_root)
        _, reconciliation = build_ordered_queue(out_root, manifest, queue_state, stages=stages)
        queue_state["reconciliation"] = reconciliation
        queue_state["updated_at"] = _now_iso()
        _write_json(state_path, queue_state)
        if sync_github_every > 0 and len(executed_this_session) % sync_github_every == 0:
            _git_sync_dashboard(project_root, f"auto-sweep: sync after {run_id}")

    if queue_state.get("queue_status") == "RUNNING":
        queue_state["queue_status"] = "IDLE_STAGE_COMPLETE"
        queue_state["current_run"] = None
    sync_Summary = build_training_history(project_root)
    queue_state["updated_at"] = _now_iso()
    _write_json(state_path, queue_state)
    if sync_github_every > 0 and executed_this_session:
        _git_sync_dashboard(project_root, f"auto-sweep: sync batch ({len(executed_this_session)} runs)")
    return {
        "executed_runs": executed_this_session,
        "queue_state": queue_state,
        "dashboard_sync": sync_Summary,
    }


def _git_sync_dashboard(project_root: Path, message: str) -> Dict[str, Any]:
    """Safely stage and push lightweight dashboard metadata (`docs/training-dashboard/`) without weights."""
    try:
        if not (Path(project_root) / ".git").is_dir():
            return {"committed": False, "reason": "not_a_git_repo"}
        subprocess.run(
            ["git", "add", "docs/training-dashboard/data.js", "docs/training-dashboard/shards/"],
            cwd=str(project_root),
            check=False,
            capture_output=True,
        )
        diff_res = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=str(project_root),
            check=False,
            capture_output=True,
        )
        if diff_res.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(project_root),
                check=False,
                capture_output=True,
            )
            push_res = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=str(project_root),
                check=False,
                capture_output=True,
                text=True,
            )
            return {"committed": True, "pushed": push_res.returncode == 0}
        return {"committed": False, "reason": "no_changes"}
    except Exception as exc:
        return {"committed": False, "error": repr(exc)}

