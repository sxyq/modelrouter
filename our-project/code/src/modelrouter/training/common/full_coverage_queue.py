"""Full-coverage run ordering and continuous queue execution."""
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .checkpoint_retention import (
    GIB, NEW_PROTOCOL_VERSION, CheckpointRetentionManager, DiskBudgetExceededError,
    has_physical_weights,
)
from .queue_support import _now_iso, _write_json, check_gpu_available
from .matrix_queue import run_queue

FULL_COVERAGE_STAGE_MAP = {
    # Stage 1: Pure S1 Routing Full Coverage (31,766 items total) - High priority router benchmark
    "F01_S1": (1, 1),
    "F02_S1": (1, 2),
    "F03_S1": (1, 3),
    "F04_S1": (1, 4),
    "F05_S1": (1, 5),
    "F06_S1": (1, 6),
    "F07_S1": (1, 7),
    # Stage 2: Single-Layer Full Coverage (F01..F04, All Supervisable Classes S1+S2+S3)
    "F01": (2, 1),
    "F02": (2, 2),
    # Stage 2.5: Routing-Aligned Ablation Priority Series (ALGN_01..ALGN_04 under small budget)
    "ALGN_01_S1": (2, 3),
    "ALGN_02_S1_S2": (2, 4),
    "ALGN_03_S1_S3": (2, 5),
    "ALGN_04_S1_S2_S3": (2, 6),
    # Stage 2 Continued: Remaining Single Layers
    "F03": (2, 7),
    "F04": (2, 8),
    # Stage 3: Cumulative Full Coverage (F05..F07)
    "F05": (3, 1),
    "F06": (3, 2),
    "F07": (3, 3),
    # Stage 4: Fractional Scale with Nested Subsets (F08..F16)
    "F08": (4, 1),
    "F09": (4, 2),
    "F10": (4, 3),
    "F11": (4, 4),
    "F12": (4, 5),
    "F13": (4, 6),
    "F14": (4, 7),
    "F15": (4, 8),
    "F16": (4, 9),
    # Stage 5: Curriculum Chaining (F17..F20)
    "F17": (5, 1),
    "F18": (5, 2),
    "F19": (5, 3),
    "F20": (5, 4),
    # Stage 6: Pure S3 Auxiliary Full Coverage (F01_S3..F07_S3)
    "F01_S3": (6, 1),
    "F02_S3": (6, 2),
    "F03_S3": (6, 3),
    "F04_S3": (6, 4),
    "F05_S3": (6, 5),
    "F06_S3": (6, 6),
    "F07_S3": (6, 7),
}


def build_ordered_full_coverage_queue(
    out_root: Path,
    manifest: Dict[str, Any],
    queue_state: Dict[str, Any],
    stages: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7),
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Build the ordered execution queue for Mode B FULL-COVERAGE series (F01..F20 + S1/S3 branches)."""
    from router_data.batch_prep import get_full_coverage_plan_spec

    plans = manifest.get("plans") or {}
    completed_runs: Dict[str, Dict[str, Any]] = {}

    for rpath in sorted(out_root.glob("*/run.json")):
        try:
            rdata = json.loads(rpath.read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            continue
        rid = rdata.get("run_id") or rpath.parent.name
        if rid.endswith("_LEGACY_MINFACTOR") or rdata.get("protocol_version") == "LEGACY_MINFACTOR":
            continue
        if rdata.get("status") in ("completed", "early_stopped"):
            completed_runs[rid] = rdata

    counts = Counter()
    ordered = []
    pending_parents = {}

    for run_id, stage_prio in sorted(FULL_COVERAGE_STAGE_MAP.items(), key=lambda kv: kv[1]):
        st, prio = stage_prio
        if st not in stages:
            continue
        spec = plans.get(run_id) or get_full_coverage_plan_spec(run_id)
        if not spec:
            continue
        spec = dict(spec)
        spec["_stage"] = st
        spec["_prio"] = prio

        is_completed = (
            (run_id in completed_runs and completed_runs[run_id].get("protocol_version") != "LEGACY_MINFACTOR")
            or run_id in (queue_state.get("completed_runs") or [])
        )
        if is_completed:
            counts["NEW_PROTOCOL_COMPLETED"] += 1
            continue

        if spec.get("continuation_mode") == "warm_start":
            parent_id = spec.get("parent_run_id")
            parent = completed_runs.get(parent_id) or {}
            best_epoch = parent.get("best_epoch")
            if best_epoch is None:
                history = parent.get("history") or []
                if history:
                    best_epoch = min(history, key=lambda h: float(
                        ((h.get("validation") or {}).get("S1") or {}).get("loss", 999.0)
                    ))["epoch"]
            ck_root = out_root / (parent_id or "") / "checkpoints"
            parent_path = (ck_root / f"epoch_{int(best_epoch):02d}" if best_epoch is not None
                           else (ck_root / "best").resolve())
            if not parent or not has_physical_weights(parent_path):
                counts["PENDING_PARENT"] += 1
                pending_parents[run_id] = {"parent_run_id": parent_id, "best_epoch": best_epoch,
                                          "reason": "missing_completed_parent_weights"}
                if parent and parent_id not in {r["run_id"] for r in ordered}:
                    regeneration = dict(plans.get(parent_id) or get_full_coverage_plan_spec(parent_id))
                    regeneration.update(run_id=parent_id, regenerate_parent=True, _stage=st, _prio=prio)
                    ordered.append(regeneration)
                    counts["PARENT_REGENERATION_REQUIRED"] += 1
                continue

        spec.pop("regenerate_parent", None)
        counts["ELIGIBLE_QUEUED"] += 1
        ordered.append(spec)

    ordered.sort(key=lambda x: (x.get("_stage", 99), x.get("_prio", 99)))

    reconciliation = {
        "total_full_coverage_runs": len(FULL_COVERAGE_STAGE_MAP),
        "completed_runs_count": counts["NEW_PROTOCOL_COMPLETED"],
        "queued_runs_count": len(ordered),
        "status_counts": dict(counts),
        "pending_parents": pending_parents,
    }
    return ordered, reconciliation


def run_continuous_full_coverage_queue(
    project_root: Path,
    out_root: Path,
    manifest_path: Path,
    model_dir: Path,
    graded_root: Path,
    cleaned_root: Path,
    epochs: int = 2,
    chunk_size: int = 8192,
    active_budget_gib: float = 120.0,
    stages: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7),
    sync_github_every: int = 0,
    max_runs: Optional[int] = None,
    continue_matrix: bool = True,
) -> Dict[str, Any]:
    """Execute the long-running continuous full-coverage training loop until all eligible tasks complete."""
    from router_data.batch_prep import prepare_full_coverage_manifest
    from scripts.fetch_live_status import build_training_history

    project_root = Path(project_root).resolve()
    out_root = Path(out_root).resolve()
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
    queue_state.setdefault("campaign", "FULL-DATA-CONTINUOUS-TRAINING")
    queue_state.setdefault("started_at", _now_iso())
    queue_state.setdefault("completed_runs", [])
    queue_state.setdefault("skipped_runs", {})
    queue_state.setdefault("failed_runs", {})
    queue_state.setdefault("s2_audit_passed", False)
    queue_state["queue_status"] = "RUNNING_PREFLIGHT"
    _write_json(state_path, queue_state)

    # Step 1: Ensure BASELINE_0 exists & is frozen
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

    # Step 3: Ensure full_coverage_manifest.json exists
    if not manifest_path.is_file():
        prepare_full_coverage_manifest(str(graded_root), str(manifest_path.parent))
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))

    ordered, reconciliation = build_ordered_full_coverage_queue(out_root, manifest, queue_state, stages=stages)
    queue_state["reconciliation"] = reconciliation
    queue_state["queue_status"] = "RUNNING"
    _write_json(state_path, queue_state)

    mgr = CheckpointRetentionManager(
        out_root=out_root,
        active_budget_bytes=budget_bytes,
        s2_audit_passed=bool(queue_state.get("s2_audit_passed", False)),
    )

    executed_this_session: List[str] = []
    failed_this_session = set()

    while True:
        # Dynamically evaluate ordered queue on each loop to pick up newly added/re-prioritized runs
        manifest = json.loads(manifest_path.read_text(encoding="utf8"))
        ordered, reconciliation = build_ordered_full_coverage_queue(out_root, manifest, queue_state, stages=stages)
        ordered = [spec for spec in ordered if spec["run_id"] not in failed_this_session]
        queue_state["reconciliation"] = reconciliation
        _write_json(state_path, queue_state)

        if not ordered:
            break

        if max_runs is not None and len(executed_this_session) >= max_runs:
            queue_state["queue_status"] = "PAUSED_MAX_RUNS_REACHED"
            queue_state["stop_reason"] = f"Completed requested batch of {max_runs} runs"
            _write_json(state_path, queue_state)
            break

        spec = ordered[0]
        run_id = spec["run_id"]

        # Check GPU availability
        gpu_ok, gpu_info = check_gpu_available()
        if not gpu_ok:
            queue_state["queue_status"] = "PAUSED_GPU_BUSY"
            queue_state["stop_reason"] = f"GPU busy or unavailable: {gpu_info}"
            _write_json(state_path, queue_state)
            time.sleep(30)
            continue

        # Check disk space & active weight budget
        try:
            mgr.pre_run_disk_check(run_id=run_id, manifest=manifest)
        except DiskBudgetExceededError as exc:
            queue_state["queue_status"] = "PAUSED_DISK_OR_BUDGET_GUARD"
            queue_state["stop_reason"] = str(exc)
            _write_json(state_path, queue_state)
            break

        queue_state["queue_status"] = "RUNNING"
        queue_state.pop("stop_reason", None)
        queue_state["current_run"] = run_id
        queue_state["interrupted_run"] = run_id
        queue_state["updated_at"] = _now_iso()
        _write_json(state_path, queue_state)

        run_epochs = int(spec.get("epochs") or epochs)
        cmd = [
            sys.executable,
            str(project_root / "router_data" / "laya_batch_train.py"),
            "--full-coverage-run", run_id,
            "--sweep-manifest", str(manifest_path),
            "--model-dir", str(model_dir),
            "--out-root", str(out_root),
            "--graded-root", str(graded_root),
            "--cleaned-root", str(cleaned_root),
            "--epochs", str(run_epochs),
            "--chunk-size", str(chunk_size),
            "--active-budget-gib", str(active_budget_gib),
            "--project-root", str(project_root),
        ]
        if queue_state.get("s2_audit_passed"):
            cmd.append("--s2-audit-passed")

        if spec.get("regenerate_parent"):
            cmd.append("--regenerate-parent")
        proc = subprocess.run(
            ["flock", str(Path.home() / "ai-serving/state/gpu.lock"), *cmd], cwd=str(project_root))
        if proc.returncode == 0:
            if run_id not in queue_state["completed_runs"]:
                queue_state["completed_runs"].append(run_id)
            queue_state["current_run"] = None
            queue_state["interrupted_run"] = None
            executed_this_session.append(run_id)
        else:
            failed_this_session.add(run_id)
            prev_att = int((queue_state["failed_runs"].get(run_id) or {}).get("attempts", 0))
            queue_state["failed_runs"][run_id] = {
                "attempts": prev_att + 1,
                "returncode": proc.returncode,
                "failed_at": _now_iso(),
            }
            # Specific error classification and safe queue halt
            log_tail = ""
            log_file = out_root / "continuous_queue.log"
            if log_file.is_file():
                try:
                    with open(log_file, "r", encoding="utf-8", errors="replace") as lf:
                        log_tail = "".join(lf.readlines()[-30:])
                except Exception:
                    pass

            if "SCHEMA_INCOMPATIBLE" in log_tail or "DataAdmissionError" in log_tail:
                err_class = "PAUSED_DATA_INTEGRITY"
            elif "RECOVERY_INTEGRITY" in log_tail or "Corrupt state" in log_tail or "Optimizer parameter identity mismatch" in log_tail:
                err_class = "PAUSED_RECOVERY_INTEGRITY"
            elif "CUDA out of memory" in log_tail:
                err_class = "PAUSED_GPU_BUSY"
            else:
                err_class = "PAUSED_RUN_FAILED"

            if err_class != "PAUSED_GPU_BUSY":
                queue_state["failed_runs"][run_id]["reason"] = "RUN_FAILED"
                queue_state["current_run"] = None
                queue_state["interrupted_run"] = None
                queue_state["updated_at"] = _now_iso()
                _write_json(state_path, queue_state)
                print(f"[RUN FAILED] {run_id}: exit {proc.returncode}; continuing independent runs.", flush=True)
                continue
            queue_state["queue_status"] = err_class
            queue_state["stop_reason"] = f"Run {run_id} failed with exit code {proc.returncode} ({err_class})."
            queue_state["updated_at"] = _now_iso()
            _write_json(state_path, queue_state)
            print(f"[QUEUE PAUSED] Halting queue execution because {run_id} failed with returncode {proc.returncode} ({err_class}). Subsequent runs will NOT be executed.", flush=True)
            break

        # Rebuild dashboard & manifest after each run
        build_training_history(project_root)
        _, reconciliation = build_ordered_full_coverage_queue(out_root, manifest, queue_state, stages=stages)
        queue_state["reconciliation"] = reconciliation
        queue_state["updated_at"] = _now_iso()
        _write_json(state_path, queue_state)

        if sync_github_every > 0 and len(executed_this_session) % sync_github_every == 0:
            _git_sync_dashboard(project_root, f"continuous-training: completed {run_id}")

        # Safe Run-boundary code reload: if .reload_queue_daemon signal is set, re-exec daemon in-place with latest code
        reload_flag = out_root / ".reload_queue_daemon"
        if reload_flag.is_file():
            reload_flag.unlink(missing_ok=True)
            print(f"[QUEUE DAEMON RELOAD] Safe boundary reached after {run_id}. Re-executing queue controller in-place with latest code...", flush=True)
            os.execv(sys.executable, [sys.executable] + sys.argv)

    if queue_state.get("queue_status") == "RUNNING":
        remaining_queued = [r for r in FULL_COVERAGE_STAGE_MAP if r not in queue_state["completed_runs"]]
        if not remaining_queued:
            queue_state["queue_status"] = "FULL_DATA_CAMPAIGN_COMPLETED"
        else:
            queue_state["queue_status"] = "IDLE_STAGE_COMPLETE"
        queue_state["current_run"] = None

    sync_summary = build_training_history(project_root)
    queue_state["updated_at"] = _now_iso()
    _write_json(state_path, queue_state)
    if sync_github_every > 0 and executed_this_session:
        _git_sync_dashboard(project_root, f"continuous-training: sync batch ({len(executed_this_session)} runs)")

    matrix_result = None
    if continue_matrix and queue_state["queue_status"] in ("FULL_DATA_CAMPAIGN_COMPLETED", "IDLE_STAGE_COMPLETE"):
        matrix_result = run_queue(
            project_root=project_root, out_root=out_root,
            manifest_path=out_root / "experiment_matrix.json", model_dir=model_dir,
            max_runs=None, epochs=epochs, active_budget_gib=active_budget_gib,
            stages=(0, 1, 2, 3, 4), sync_github_every=sync_github_every,
            allow_unmaterialized=True,
        )

    return {
        "executed_runs": executed_this_session,
        "queue_state": matrix_result["queue_state"] if matrix_result else queue_state,
        "dashboard_sync": sync_summary,
        "matrix_continuation": matrix_result,
    }

