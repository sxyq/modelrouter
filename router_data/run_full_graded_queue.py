"""Lightweight, resumable automated queue controller for ModelRouter FULL-GRADED experiments.

Strictly orchestrates existing modules (`prepare_router_data.py`, `router_data/batch_prep.py`,
`router_data/laya_batch_train.py`, `router_data/checkpoint_retention.py`) without re-implementing
training loops, optimizers, loss functions, or data cleaning logic.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from router_data.checkpoint_retention import (
        DEFAULT_ACTIVE_BUDGET_BYTES,
        GIB,
        LEGACY_PROTOCOL_VERSION,
        NEW_PROTOCOL_VERSION,
        CheckpointRetentionManager,
        DiskBudgetExceededError,
        compute_run_dedup_signature,
        load_or_default_baseline_0,
        run_storage_policy_verification,
        sync_server_metadata_and_build_dashboard,
    )
except ImportError:
    from checkpoint_retention import (
        DEFAULT_ACTIVE_BUDGET_BYTES,
        GIB,
        LEGACY_PROTOCOL_VERSION,
        NEW_PROTOCOL_VERSION,
        CheckpointRetentionManager,
        DiskBudgetExceededError,
        compute_run_dedup_signature,
        load_or_default_baseline_0,
        run_storage_policy_verification,
        sync_server_metadata_and_build_dashboard,
    )


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    tmp.replace(path)


def check_gpu_available(max_busy_mib: int = 4096) -> Tuple[bool, Dict[str, Any]]:
    """Verify the single RTX A6000 GPU is available and not occupied by another heavy job."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        ).strip()
        line = out.splitlines()[0]
        parts = [p.strip() for p in line.split(",")]
        used_mib = float(parts[3])
        util_pct = float(parts[4])
        info = {
            "gpu_index": int(parts[0]),
            "gpu_name": parts[1],
            "memory_total_mib": float(parts[2]),
            "memory_used_mib": used_mib,
            "utilization_pct": util_pct,
        }
        return used_mib <= max_busy_mib, info
    except Exception as exc:
        return False, {"error": repr(exc)}


def verify_laya_encoding_for_run(
    project_root: Path,
    data_dir: Path,
    groups: List[str],
    model_dir: Path,
    max_len: int = 1024,
    head_max_len: int = 512,
) -> Tuple[bool, Dict[str, Any]]:
    """Verify official Laya `items_from_rows` encoding has `skipped == {}` and `items == rows`."""
    laya_dir = str(project_root / "external" / "laya")
    if laya_dir not in sys.path:
        sys.path.insert(0, laya_dir)
    from transformers import AutoTokenizer
    from laya.train import items_from_rows, read_data

    tok_path = model_dir / "tokenizer" if (model_dir / "tokenizer").is_dir() else model_dir
    tok = AutoTokenizer.from_pretrained(str(tok_path), trust_remote_code=True)
    report: Dict[str, Any] = {}
    all_ok = True
    for g in groups:
        for split in ("train", "val"):
            fp = data_dir / split / f"{g}.jsonl"
            if not fp.is_file():
                all_ok = False
                report[f"{split}_{g}"] = {"error": "missing_file"}
                continue
            rows = read_data(str(fp))
            items, skipped = items_from_rows(tok, rows, max_len=max_len, head_max_len=head_max_len)
            ok = len(rows) > 0 and len(items) == len(rows) and skipped == {}
            if not ok:
                all_ok = False
            report[f"{split}_{g}"] = {
                "rows": len(rows),
                "items": len(items),
                "skipped": skipped,
                "ok": ok,
            }
    return all_ok, report


def materialize_plan_on_demand(
    project_root: Path,
    out_root: Path,
    manifest: Dict[str, Any],
    manifest_path: Path,
    run_id: str,
) -> bool:
    """Materialize an eligible unmaterialized plan using `router_data/batch_prep.py`."""
    plans = manifest.get("plans") or {}
    spec = plans.get(run_id)
    if not spec:
        return False
    base_id = spec.get("base_run_id") or (run_id[3:] if run_id.startswith("P0_") else run_id)
    p0_id = run_id if run_id.startswith("P0_") else f"P0_{base_id}"

    train_dir = out_root / "train" / p0_id
    val_dir = out_root / "val"
    groups = list(spec.get("groups") or spec.get("supervision_classes") or [])
    if train_dir.is_dir() and all((train_dir / "train" / f"{g}.jsonl").is_file() for g in groups):
        return True

    # Call batch_prep.materialize_single_p0_plan if available, or materialize from graded pool
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from router_data.batch_prep import prepare_p0_repaired_plans

    graded_root = project_root / "runs" / "MR-ALLDATA-PREP-20261011" / "quality_grading_v2_1"
    if not graded_root.is_dir():
        return False
    prepare_p0_repaired_plans(
        graded_root=graded_root,
        out_root=out_root,
        target_base_run_ids=[base_id],
    )
    # Reload updated manifest if modified
    if manifest_path.is_file():
        updated = json.loads(manifest_path.read_text(encoding="utf8"))
        manifest.update(updated)
    return (out_root / "train" / p0_id).is_dir()


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
    failed_runs = dict(queue_state.get("failed_runs") or {})

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

        if exec_id in completed_runs or b_id in completed_runs:
            counts["NEW_PROTOCOL_COMPLETED"] += 1
            continue

        if int((failed_runs.get(exec_id) or {}).get("attempts", 0)) >= 2:
            counts["FAILED"] += 1
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
    max_runs: int = 10,
    epochs: int = 2,
    active_budget_gib: float = 120.0,
    stages: Tuple[int, ...] = (0, 1, 2, 3),
    sync_github_every: int = 0,
    allow_unmaterialized: bool = False,
) -> Dict[str, Any]:
    """Execute the FULL-GRADED automated training queue with pre-run checks and retention."""
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

    # Step 2: Run 14-point pre-execution verification (`P11-01..P11-14`)
    ver = run_storage_policy_verification(project_root=project_root, run_official_load=True)
    _write_json(out_root / "storage_policy_verification.json", ver)
    if not ver.get("all_passed"):
        queue_state["queue_status"] = "STOPPED_PREFLIGHT_VERIFICATION_FAILED"
        queue_state["stop_reason"] = f"Verification passed {ver.get('passed_count')}/{ver.get('total_checks')}"
        _write_json(state_path, queue_state)
        return {"queue_state": queue_state, "verification": ver}

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

    cached_audit_runs: Dict[str, Any] = {}
    audit_file = out_root / "cpu_encoding_audit.json"
    if audit_file.is_file():
        try:
            cached_audit_runs = (json.loads(audit_file.read_text(encoding="utf8")).get("runs") or {})
        except (OSError, json.JSONDecodeError):
            cached_audit_runs = {}

    executed_this_session: List[str] = []
    for spec in ordered:
        if len(executed_this_session) >= max_runs:
            queue_state["queue_status"] = "PAUSED_MAX_RUNS_REACHED"
            queue_state["stop_reason"] = f"Completed requested batch of {max_runs} runs"
            break

        run_id = spec["run_id"]
        data_rel = spec.get("data") or f"data/{run_id}"
        is_mat = bool(spec.get("materialized")) or (out_root / data_rel).is_dir() or (out_root / "data" / run_id).is_dir() or (out_root / "train" / run_id).is_dir()
        if not is_mat:
            if not allow_unmaterialized:
                continue
            ok_mat = materialize_plan_on_demand(project_root, out_root, manifest, manifest_path, run_id)
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

        # Verify official Laya encoding (`skipped == {}`)
        data_dir = out_root / data_rel if (out_root / data_rel).is_dir() else (out_root / "data" / run_id)
        groups = list(spec.get("groups") or spec.get("supervision_classes") or [])
        if (cached_audit_runs.get(run_id) or {}).get("all_zero_skipped") is True:
            enc_ok, enc_report = True, cached_audit_runs[run_id]
        else:
            enc_ok, enc_report = verify_laya_encoding_for_run(project_root, data_dir, groups, model_dir)
        if not enc_ok:
            queue_state["failed_runs"][run_id] = {
                "attempts": 2,
                "reason": "laya_encoding_verification_failed",
                "detail": enc_report,
            }
            _write_json(state_path, queue_state)
            continue

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
        sync_server_metadata_and_build_dashboard(project_root=project_root, run_official_load=False)
        _, reconciliation = build_ordered_queue(out_root, manifest, queue_state, stages=stages)
        queue_state["reconciliation"] = reconciliation
        queue_state["updated_at"] = _now_iso()
        _write_json(state_path, queue_state)
        if sync_github_every > 0 and len(executed_this_session) % sync_github_every == 0:
            _git_sync_dashboard(project_root, f"auto-sweep: sync after {run_id}")

    if queue_state.get("queue_status") == "RUNNING":
        queue_state["queue_status"] = "IDLE_STAGE_COMPLETE"
        queue_state["current_run"] = None
    sync_Summary = sync_server_metadata_and_build_dashboard(project_root=project_root, run_official_load=True)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="ModelRouter FULL-GRADED Automated Queue Controller")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-root", default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012")
    parser.add_argument("--manifest", default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/experiment_matrix.json")
    parser.add_argument("--model-dir", default="models/laya-421m")
    parser.add_argument("--max-runs", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--active-budget-gib", type=float, default=120.0)
    parser.add_argument("--stages", default="0,1,2,3")
    parser.add_argument("--sync-github-every", type=int, default=0)
    parser.add_argument("--allow-unmaterialized", action="store_true")
    parser.add_argument("--dry-reconcile", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    out_root = (project_root / args.out_root).resolve()
    manifest_path = (project_root / args.manifest).resolve()
    model_dir = (project_root / args.model_dir).resolve()
    stages = tuple(int(x.strip()) for x in args.stages.split(",") if x.strip())

    if args.dry_reconcile:
        manifest = json.loads(manifest_path.read_text(encoding="utf8")) if manifest_path.is_file() else {}
        state_path = out_root / "queue_state.json"
        q_state = json.loads(state_path.read_text(encoding="utf8")) if state_path.is_file() else {}
        ordered, rec = build_ordered_queue(out_root, manifest, q_state, stages=stages)
        print(json.dumps({
            "reconciliation": rec,
            "next_20_in_queue": [
                {"run_id": x["run_id"], "stage": x["_stage"], "batch_id": x.get("batch_id"), "combo_id": x.get("combo_id"), "groups": x.get("groups")}
                for x in ordered[:20]
            ],
            "skipped_identical_count": len(q_state.get("skipped_runs") or {}),
        }, ensure_ascii=False, indent=2))
        return

    res = run_queue(
        project_root=project_root,
        out_root=out_root,
        manifest_path=manifest_path,
        model_dir=model_dir,
        max_runs=args.max_runs,
        epochs=args.epochs,
        active_budget_gib=args.active_budget_gib,
        stages=stages,
        sync_github_every=args.sync_github_every,
        allow_unmaterialized=args.allow_unmaterialized,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

