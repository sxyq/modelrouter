#!/usr/bin/env python3
"""Read training records and publish the existing dashboard's live and per-run data."""
from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import shlex
import shutil
import subprocess
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUR_PROJECT_DASHBOARD_DIR = PROJECT_ROOT / "our-project/dashboard"
OLD_CORE_IDS = {
    "P0_B03_C01_QB_PB-e02", "P0_B01_C01_QB_PB-e02", "P0_B03_C05_QB_PB-e02",
    "P0_B03_C08_QB_PB-e02", "P0_B02_C01_QB_PB-e02",
}
_JSON_CACHE = {}
_LOG_CACHE = {}
_PROGRESS = {}
_HISTORY = {}
logger = logging.getLogger("fetch_live_status")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path, default=None):
    path = Path(path)
    if not path.is_file():
        return default
    st = path.stat()
    identity = (st.st_mtime_ns, st.st_size)
    saved = _JSON_CACHE.get(str(path))
    if saved and saved[0] == identity:
        return saved[1]
    value = json.loads(path.read_text(encoding="utf-8"))
    _JSON_CACHE[str(path)] = (identity, value)
    return value


def age_seconds(value):
    if not value:
        return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return max(0, time.time() - dt.timestamp())


def relative(path, root):
    return str(Path(path).relative_to(root))


def run_key(family, path, root):
    return family + "--" + re.sub(r"[^a-zA-Z0-9_.-]", "--", relative(path, root))


def read_local_processes():
    result = subprocess.run(["ps", "-eo", "pid,etimes,args"], capture_output=True, text=True, timeout=4)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Process listing failed")
    process = {"laya": {}, "kev": {}}
    for line in result.stdout.splitlines()[1:]:
        fields = line.strip().split(None, 2)
        if len(fields) != 3 or not fields[0].isdigit():
            continue
        pid, elapsed, command = fields
        # Shell launchers and the collector's own SSH command are not training workers.
        argv = shlex.split(command)
        executable = Path(argv[0]).name
        if not executable.startswith("python"):
            continue
        family = "laya" if any(Path(a).name == "laya_batch_train.py" for a in argv) else (
            "kev" if "kev.train" in argv else None)
        if family:
            options = {a: argv[i + 1] for i, a in enumerate(argv[:-1]) if a.startswith("--")}
            process[family] = {"train_pid": int(pid), "elapsed_s": int(elapsed), "is_training": True,
                               "run_id": options.get("--full-coverage-run"),
                               "out_root": options.get("--out-root"), "out": options.get("--out"),
                               "batch": options.get("--batch"), "accum": options.get("--accum")}
    return process


def read_local_gpu_status():
    result = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,name",
                             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=4)
    if result.returncode:
        return {"error": result.stderr.strip() or "GPU metrics unavailable"}
    parts = result.stdout.strip().splitlines()[0].split(",")
    values = [float(v.strip()) for v in parts[:5]]
    return {**dict(zip(("used_mb", "total_mb", "util_pct", "temp_c", "power_w"), values)), "name": parts[5].strip()}


def _checkpoint(path, checkpoint_id, epoch, metadata, root):
    candidates = [path] if path.is_file() else path.glob("*")
    weights = [p for p in candidates if p.is_file() and not p.is_symlink()
               and (p.name in ("model.safetensors", "model.pt", "head.pt", "pytorch_model.bin")
                    or p.name.startswith(("adapter_model", "model-", "epoch_")) and p.suffix in (".pt", ".safetensors", ".bin"))]
    physical = bool(weights) and all(p.stat().st_size > 0 for p in weights)
    prior = metadata.get("was_previously_saved")
    freed = metadata.get("freed_bytes")
    pruned = not physical and prior is True and isinstance(freed, (int, float)) and freed > 0
    evidence = "PHYSICAL_FILES" if physical else ("RECORDED_SAVED_AND_PRUNED" if pruned else (
        "RECORDED_NEVER_SAVED" if prior is False and metadata.get("weights_saved") is False else "MISSING_HISTORY_UNCERTAIN"))
    return {"checkpoint_id": checkpoint_id, "epoch": epoch, "path": relative(path, root),
            "physical": physical, "weight_bytes": sum(p.stat().st_size for p in weights),
            "ever_saved": True if physical or prior is True else (False if prior is False else None),
            "pruned": pruned, "evidence": evidence, "retention_status": metadata.get("retention_status"),
            "retention_reason": metadata.get("retention_reason"), "source": metadata.get("source"),
            "manifest_retention_status": metadata.get("manifest_retention_status"),
            "metadata_weights_saved": metadata.get("weights_saved"),
            "recorded_freed_bytes": freed,
            "metadata_disagrees": metadata.get("weights_saved") is not None and metadata["weights_saved"] != physical}


def _validation(history, source, validation_set=None):
    result = []
    for epoch in history:
        for stream, metrics in (epoch.get("validation") or {}).items():
            if stream not in ("S1", "S2", "S3", "clean") or not isinstance(metrics, dict):
                continue
            result.append({"epoch": epoch.get("epoch"), "step": epoch.get("global_step", epoch.get("optimizer_updates")),
                           "stream": stream, "source": source, "validation_set": validation_set,
                           **{k: metrics.get(k) for k in ("loss", "accuracy", "brier", "ece", "items")}})
    return result


def _validation_identity(meta, directory, root):
    explicit = meta.get("validation_set") or meta.get("fixed_validation")
    if explicit:
        return explicit
    val = directory.parent / "val"
    if val.is_dir():
        return relative(val, root)
    # Missing dataset identity keeps comparisons confined to this run.
    return relative(directory / "run.json", root)


def _new_log_state():
    return {"offset": 0, "points": defaultdict(list), "pending": [], "context": None,
            "last_epoch": None, "segments": defaultdict(int), "last_step": {}}


def read_log_points(path, root, known_run=None, family="laya"):
    """Read only appended complete lines; delayed epoch records identify anonymous logs."""
    if not path.is_file():
        return {}
    state = _LOG_CACHE.setdefault(str(path), _new_log_state())
    if path.stat().st_size < state["offset"]:
        state = _new_log_state()
        _LOG_CACHE[str(path)] = state

    def add(rid, point):
        if not rid:
            return
        step = point.get("step")
        previous = state["last_step"].get(rid)
        if step is not None and previous is not None and step < previous:
            state["segments"][rid] += 1
        state["last_step"][rid] = step
        point.update(segment=state["segments"][rid], source=relative(path, root),
                     timestamp=point.get("timestamp"), learning_rate=point.get("learning_rate"))
        state["points"][rid].append(point)

    with path.open("r", encoding="utf-8", errors="replace") as stream:
        stream.seek(state["offset"])
        while True:
            position = stream.tell()
            line = stream.readline()
            if not line or not line.endswith("\n"):
                state["offset"] = position
                break
            match = re.search(r"\[([^\]]+)\] Epoch (\d+)/(\d+) Chunk (\d+)/(\d+): loss=([\d.eE+-]+), step=(\d+)/(\d+), consumed=(\d+)/(\d+)", line)
            if match:
                rid, ep, _, chunk, _, loss, step, _, count, _ = match.groups()
                add(rid, {"epoch": int(ep), "chunk": int(chunk), "train_loss": float(loss), "step": int(step),
                          "optimizer_updates": int(step), "consumed_records": int(count), "samples_per_s": None})
                continue
            start = re.match(r"START (\S+) ", line)
            if start:
                state["context"] = start.group(1)
            explicit = re.search(r"\[([^\]]+)\].*RESUME_CONSISTENCY", line)
            if explicit:
                state["segments"][explicit.group(1)] += 1
            if family == "kev":
                match = re.search(r"ep(\d+) step (\d+)/(\d+) loss ([\d.eE+-]+).*?([\d.]+)s/rec", line)
                if match:
                    ep, step, _, loss, seconds = match.groups()
                    add(known_run, {"epoch": int(ep) + 1, "step": int(step), "optimizer_updates": int(step),
                                    "train_loss": float(loss), "consumed_records": None,
                                    "samples_per_s": 1 / float(seconds) if float(seconds) > 0 else None,
                                    "speed_scope": "upstream cumulative seconds per record"})
                continue
            match = re.search(r"epoch (\d+)/(\d+) step (\d+) loss ([\d.eE+-]+)", line)
            if match:
                ep, _, step, loss = match.groups()
                point = {"epoch": int(ep), "step": int(step), "train_loss": float(loss),
                         "axis_scope": "epoch_local_step", "consumed_records": None, "samples_per_s": None}
                if known_run or state["context"]:
                    add(known_run or state["context"], point)
                else:
                    state["pending"].append(point)
            if line.startswith("{") and '"event": "epoch_complete"' in line:
                row = json.loads(line)
                rid = row.get("run_id")
                for point in state["pending"]:
                    add(rid, point)
                state["pending"].clear()
    return state["points"]


def build_training_history(project_root=PROJECT_ROOT, dashboard_dir=None, processes=None):
    """Publish original observations without changing runs, manifests, or weight files."""
    root = Path(project_root)
    output = Path(dashboard_dir or root / "our-project/dashboard")
    runs_root = root / "runs"
    p0 = runs_root / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
    full = read_json(p0 / "full_coverage_manifest.json", {})
    kev_queue = read_json(root / "our-project/results/training/kev/candidate_queue.json", [])
    manifest_rows = {}
    for directory in runs_root.glob("*"):
        if directory.is_dir():
            data = read_json(directory / "checkpoint_manifest.json", {})
            for row in data.get("checkpoints", []):
                manifest_rows[(directory.name, row.get("checkpoint_id"))] = row
    runs = []
    details = {}
    # Only run directories; do not traverse datasets or read weights.
    paths = set(runs_root.glob("*/run.json")) | set(runs_root.glob("*/*/run.json"))
    for path in sorted(paths):
        meta = read_json(path)
        rid = meta.get("run_id", path.parent.name)
        family = "kev" if "KEV" in rid.upper() else "laya"
        history = read_json(path.parent / "epoch_metrics.json", meta.get("history", []))
        if not isinstance(history, list):
            history = history.get("history", [])
        history = [{**entry, "consumed_items": entry.get("consumed_items", entry.get("items_consumed"))} for entry in history]
        if len(history) == 1 and meta.get("global_steps") is not None:
            history[0].setdefault("global_step", meta["global_steps"])
        protocol = meta.get("protocol_version", meta.get("protocol")) or (
            "LEGACY_INPUT_PROTOCOL" if path.parent.parent.name == "MR-FULL-GRADED-TRAINING" else
            "LAYA_OVERNIGHT_" + path.parent.parent.name if "OVERNIGHT" in str(path) else "UNRECORDED_PROTOCOL")
        if family == "kev" and meta.get("device") == "cpu" and "physical_verification" in meta:
            protocol = "KEV_POINTER_HEAD_PILOT"
        key = run_key(family, path.parent, root)
        validation_set = _validation_identity(meta, path.parent, root)
        validation = _validation(history, relative(path, root), validation_set)
        for entry in history:
            if entry.get("val_choice_acc") is not None:
                validation.append({"epoch": entry.get("epoch"), "step": entry.get("global_step"),
                                   "stream": "choice", "accuracy": entry["val_choice_acc"],
                                   "loss": None, "brier": None, "ece": None, "items": None,
                                   "validation_set": validation_set, "source": relative(path, root)})
        if family == "kev" and meta.get("metrics"):
            pilot_metrics = meta["metrics"]
            validation.append({"epoch": None, "step": meta.get("steps_completed"), "stream": "choice",
                               "accuracy": pilot_metrics.get("val_choice_accuracy"), "loss": None,
                               "brier": None, "ece": None, "items": None,
                               "validation_set": validation_set, "source": relative(path, root)})
        checkpoints = []
        for epoch in history:
            cid = epoch.get("checkpoint_id", f"{rid}-e{epoch.get('epoch')}")
            manifest_row = manifest_rows.get((path.parent.parent.name, cid), {})
            saved = {**manifest_row, **epoch, "source": relative(path, root),
                     "manifest_retention_status": manifest_row.get("retention_status")}
            cp = path.parent / "checkpoints" / f"epoch_{epoch['epoch']:02d}"
            if not cp.exists() and cp.with_suffix(".pt").is_file():
                cp = cp.with_suffix(".pt")
            checkpoints.append(_checkpoint(cp, cid, epoch.get("epoch"), saved, root))
        covered = {c["path"] for c in checkpoints}
        for cp in (path.parent / "checkpoints").glob("*"):
            if not cp.is_symlink() and relative(cp, root) not in covered:
                c = _checkpoint(cp, rid + ":" + cp.name, None, {}, root)
                if c["physical"]:
                    checkpoints.append(c)
        if family == "kev" and not history:
            cp = path.parent / "checkpoint"
            c = _checkpoint(cp, rid + ":pilot", None, {}, root)
            if c["physical"]:
                checkpoints.append(c)
        cursor = read_json(path.parent / "cursor.json", {})
        coverage = read_json(path.parent / "run_coverage_ledger.json", {})
        exposure = {"candidate_records": meta.get("total_eligible_items", sum(meta.get("train_groups", {}).values()) or None),
                    "materialized_records": (coverage.get("census_metrics") or {}).get("materialized_items"),
                    "encoded_records": (coverage.get("census_metrics") or {}).get("encoded_items"),
                    "trained_records": cursor.get("consumed_items", coverage.get("consumed_items", meta.get("total_items_consumed"))),
                    "distinct_units": cursor.get("consumed_units", coverage.get("distinct_units_covered")),
                    "by_stream_actual": meta.get("trained_by_supervision"),
                    "train_groups": meta.get("train_groups"), "ledger_updated_at": coverage.get("updated_at"),
                    "train_val_overlap_count": coverage.get("train_val_overlap_count")}
        row = {"key": key, "family": family, "run_id": rid, "protocol": protocol,
               "status": meta.get("status", "COMPLETED" if meta.get("finished_at") else "UNKNOWN").upper(), "epochs": len(history),
               "planned_epochs": meta.get("epochs_max"), "started_at": meta.get("started_at"),
               "finished_at": meta.get("finished_at"), "root": relative(path.parent, root),
               "validation": validation, "exposure": exposure, "checkpoints": checkpoints,
               "layers": meta.get("layers"), "layer_fractions": meta.get("layer_fractions"),
               "supervision_classes": meta.get("supervision_classes", list(meta.get("train_groups", {}))),
               "best_epoch_recorded": meta.get("best_epoch"),
               "config": {k: v for k, v in (meta.get("config") or {}).items() if k in (
                   "epochs", "micro_batch", "grad_accum", "encoder_lr", "head_lr", "min_lr",
                   "weight_decay", "loss", "seed", "freeze_encoder", "max_len", "head_max_len")},
               "origin": "LOCAL_RUN", "validation_set": validation_set,
               "execution_evidence": bool(history or cursor.get("step_count") or meta.get("global_steps") or meta.get("steps_completed")),
               "training_kind": "POINTER_HEAD_PILOT" if protocol in ("KEV_POINTER_HEAD_PILOT", "MR-V8-MULTITASK-v1") else "TRAINING_RUN",
               "loss_definition": (meta.get("config") or {}).get("loss"),
               "parent_checkpoint": meta.get("parent_checkpoint_id"),
               "terminal_metrics": meta.get("metrics"),
               "curve_path": f"shards/training_runs/{key}.json", "source": relative(path, root),
               "limitations": ["Actual per-stream gradient exposure was not recorded"] if not exposure["by_stream_actual"] else []}
        if family == "kev" and not history:
            row["limitations"].append("Pointer head pilot has no epoch history; it is not a formal LoRA run")
        runs.append(row)
        durations = [{"epoch": e.get("epoch"), "epoch_seconds": e.get("epoch_seconds"),
                      "train_seconds": e.get("train_seconds"), "segment": 0,
                      "source": relative(path, root)} for e in history]
        details[key] = {"run": row, "points": [], "speed_points": durations,
                        "validation": validation, "exposure": exposure, "epochs": history}

    # Kev adapters and official training folders have training_config/metrics, not Laya run.json.
    kev_dirs = [root / "models/kev-4b-adapter"]
    for folder in runs_root.glob("KEV*"):
        kev_dirs += [p.parent for p in folder.glob("*/training_config.json")]
    for directory in sorted(set(kev_dirs)):
        if not (directory / "training_config.json").is_file() and not (directory / "training_metrics.json").is_file():
            continue
        config = read_json(directory / "training_config.json", {})
        metrics = read_json(directory / "training_metrics.json", {})
        args = config.get("args", {})
        cursor = read_json(directory.parent / "cursor.json", {}) if directory.name in ("formal_run", "checkpoint") else {}
        plan = next((q for q in kev_queue if q.get("checkpoint_path") == relative(directory, root)), {})
        key = run_key("kev", directory, root)
        rid = plan.get("candidate_id", directory.parent.name + "/" + directory.name)
        if directory.parent.name == "models":
            rid = directory.name
        imported = directory.parent.name == "models"
        partial = bool(args.get("max_steps") or args.get("stop_after"))
        protocol = "KEV_IMPORTED_LORA" if imported else ("KEV_FORMAL_LORA" if args.get("device") == "cuda" and not partial else "KEV_LORA_SMOKE")
        checkpoint = _checkpoint(directory, rid + ":adapter", None, {}, root)
        result = read_json(directory / "result.json", plan.get("metrics", {}))
        clean = result.get("clean", {})
        validation = [{"epoch": None, "step": metrics.get("optimizer_steps"), "stream": "clean",
                       "loss": clean.get("nll"), "accuracy": clean.get("acc"), "brier": clean.get("brier"),
                       "ece": clean.get("ece"), "items": clean.get("n"),
                       "validation_set": result.get("validation_set") or config.get("holdout") or relative(directory / "result.json", root),
                       "source": relative(directory / "val_metrics.json" if result.get("validation_protocol") else directory / "result.json", root)}] if clean else []
        completed_epochs = len(metrics.get("grad_norm", [])) if metrics and not partial else 0
        row = {"key": key, "family": "kev", "run_id": rid, "protocol": protocol,
               "status": "COMPLETED" if metrics else cursor.get("status", "UNKNOWN"),
               "execution_evidence": bool(metrics or cursor.get("step")),
               "training_status": "COMPLETED" if metrics else cursor.get("status", "UNKNOWN"),
               "evaluation_status": plan.get("evaluation_status") or ("FAILED" if plan.get("failure_reason") == "Validation evaluation failed" else "EVALUATED" if clean else "NOT_EVALUATED"),
               "queue_status": plan.get("status"), "failure_reason": plan.get("failure_reason"),
               "epochs": completed_epochs, "planned_epochs": args.get("epochs"),
               "root": relative(directory, root), "started_at": None, "finished_at": None,
               "parent_checkpoint": Path(args["init_from"]).name if args.get("init_from") else None,
               "validation": validation, "checkpoints": [checkpoint] if checkpoint["physical"] else [],
               "curve_path": f"shards/training_runs/{key}.json", "source": relative(directory / "training_config.json", root),
               "config": {k: args.get(k) for k in ("lr", "epochs", "batch", "accum", "lora", "perm_kl", "synthetic_repeat", "max_steps")},
               "terminal_metrics": {k: metrics.get(k) for k in ("wall_seconds", "optimizer_steps", "records_seen", "requested_records")},
               "exposure": {"trained_records": metrics.get("records_seen"), "requested_records": metrics.get("requested_records"),
                            "by_stream_actual": None, "optimizer_updates": metrics.get("optimizer_steps")},
               "limitations": ["Imported adapter history is upstream training, not a new local GPU run"] if directory.parent.name == "models" else []}
        row["origin"] = "IMPORTED_ADAPTER" if directory.parent.name == "models" else "LOCAL_RUN"
        row["training_kind"] = "IMPORTED_LORA" if imported else ("LORA_SMOKE" if partial or args.get("device") != "cuda" else "FORMAL_LORA")
        runs.append(row)
        log = directory / "train.log"
        if directory.name == "formal_run" and not log.is_file():
            log = directory.parent / "train.log"
        # A shared unlabelled CPU log cannot identify smoke_run vs test_run.
        points = list(read_log_points(log, root, key, "kev").get(key, []))
        durations = [{"step": i + 1, "optimizer_step_seconds": seconds, "segment": 0,
                      "source": relative(directory / "training_metrics.json", root)}
                     for i, seconds in enumerate(metrics.get("step_seconds", []))]
        details[key] = {"run": row, "points": points, "speed_points": durations,
                        "validation": validation, "exposure": row["exposure"]}

    laya_maps = {}
    for folder in runs_root.glob("*"):
        for log in folder.glob("*.log"):
            if log.name in ("continuous_queue.log", "queue_batch1.log", "queue_daemon.log", "matrix_training.log"):
                laya_maps[str(log)] = read_log_points(log, root)
    for row in runs:
        detail = details[row["key"]]
        if row["family"] == "laya":
            points = []
            for log, mapping in laya_maps.items():
                if str(root / row["root"]).startswith(str(Path(log).parent)):
                    ambiguous_alias = any(r["root"].endswith("/" + row["run_id"] + "_LEGACY_MINFACTOR") for r in runs)
                    if not ambiguous_alias:
                        points.extend(mapping.get(row["run_id"], []))
            unique = {}
            for point in points:
                identity = (point.get("epoch"), point.get("step"), point.get("chunk"), point.get("train_loss"))
                unique.setdefault(identity, dict(point))
            points = list(unique.values())
            if len({p.get("source") for p in points}) > 1:
                for point in points:
                    point["segment"] = f"{point['source']}:{point['segment']}"
            if not points:
                points = [{"epoch": e.get("epoch"), "step": e.get("global_step", e.get("optimizer_updates")),
                           "train_loss": e.get("train_loss"), "learning_rate": None,
                           "configured_learning_rate": e.get("learning_rate"), "segment": 0,
                           "consumed_records": e.get("consumed_items"),
                           "timestamp": e.get("timestamp"), "source": row["source"]} for e in detail.pop("epochs", [])]
            else:
                detail.pop("epochs", None)
            detail["points"] = points
        elif "epochs" in detail:
            detail["points"] = [{"epoch": e.get("epoch"), "step": e.get("global_step"),
                                 "train_loss": e.get("train_loss"), "segment": 0,
                                 "timestamp": e.get("timestamp"), "source": row["source"]}
                                for e in detail.pop("epochs")]
            if not detail["points"] and row.get("terminal_metrics"):
                pilot = read_json(root / row["source"], {})
                detail["points"] = [{"epoch": None, "step": pilot.get("steps_completed"),
                                     "train_loss": (pilot.get("metrics") or {}).get("train_loss_final"),
                                     "segment": 0, "timestamp": pilot.get("finished_at"), "source": row["source"]}]
        row["curve_points"] = len(detail["points"])
        row["status"] = "TRAINING" if any(
            p.get("train_pid") and str((root / (p.get("out") or str(Path(p.get("out_root", "")) / p.get("run_id", "")))).resolve()) == str((root / row["root"]).resolve())
            for p in (processes or {}).values()) else row["status"]
        row["curve_granularity"] = "CHUNK_STEP" if any(p.get("chunk") is not None for p in detail["points"]) else (
            "STEP" if any(p.get("axis_scope") or p.get("optimizer_updates") is not None for p in detail["points"]) else "EPOCH")
        if not detail["points"]:
            row["curve_granularity"] = "UNRECORDED"
        destination = output / row["curve_path"]
        if read_json(destination) != detail:
            atomic_json(destination, detail)

    checkpoints = [dict(c, run_id=r["run_id"], key=r["key"], family=r["family"]) for r in runs for c in r["checkpoints"]]
    old = [next((c for c in checkpoints if c["checkpoint_id"] == cid),
                {"checkpoint_id": cid, "physical": None, "evidence": "NO_MATCHING_RECORD"}) for cid in sorted(OLD_CORE_IDS)]
    cleanup = read_json(p0 / "cleanup_audit_log.json", {})
    new_ids = {c.get("checkpoint_id") for c in cleanup.get("protected_items", []) if c.get("reason") == "protected_new_core_pool_15pct"}
    parent_ids = {r.get("parent_checkpoint_id") for r in full.get("plans", {}).values() if r.get("parent_checkpoint_id")}
    parent_ids.update(r["parent_checkpoint"] for r in runs if r.get("parent_checkpoint"))
    for plan in full.get("plans", {}).values():
        parent_run = next((r for r in runs if r["run_id"] == plan.get("parent_run_id") and r["root"].startswith(relative(p0, root) + "/")), {})
        parent_ids.update(c["checkpoint_id"] for c in parent_run.get("checkpoints", []) if c["epoch"] == parent_run.get("best_epoch_recorded") and c["epoch"] is not None)
    recovery = [c for c in checkpoints if "recovery" in c["path"] or c.get("retention_status") == "TEMP_RECOVERY"]
    parents = [c for c in checkpoints if c["checkpoint_id"] in parent_ids or c.get("retention_status") == "PINNED_PARENT"]
    new = [c for c in checkpoints if c["checkpoint_id"] in new_ids]
    global_ids = {c.get("checkpoint_id") for c in cleanup.get("protected_items", []) if c.get("reason") == "protected_global_best"}
    global_best = [c for c in checkpoints if c["checkpoint_id"] in global_ids]
    classified = {c["path"] for c in old + new + parents + recovery + global_best if c.get("path")}
    counts = {}
    for family in ("laya", "kev"):
        rr = [r for r in runs if r["family"] == family]
        cc = [c for c in checkpoints if c["family"] == family]
        counts[family] = {"planned_runs": len(full.get("plans", {})) if family == "laya" else len(kev_queue),
                          "observed_runs": len(rr), "completed_runs": sum(r["origin"] == "LOCAL_RUN" and r["execution_evidence"] and r["status"] in ("COMPLETED", "EARLY_STOPPED") for r in rr),
                          "running_runs": sum(r["status"] in ("RUNNING", "TRAINING") for r in rr),
                          "local_runs": sum(r["origin"] == "LOCAL_RUN" for r in rr),
                          "local_completed_runs": sum(r["origin"] == "LOCAL_RUN" and r["execution_evidence"] and r["status"] in ("COMPLETED", "EARLY_STOPPED") for r in rr),
                          "executed_runs": sum(r["origin"] == "LOCAL_RUN" and r["execution_evidence"] for r in rr),
                          "metadata_only_runs": sum(not r["execution_evidence"] for r in rr),
                          "imported_assets": sum(r["origin"] == "IMPORTED_ADAPTER" for r in rr),
                          "recorded_epochs": sum(r.get("epochs") or 0 for r in rr),
                          "checkpoint_versions": len(cc), "physical_checkpoints": sum(c["physical"] for c in cc),
                          "confirmed_saved_versions": sum(c["ever_saved"] is True for c in cc),
                          "metadata_versions": sum(not c["physical"] for c in cc), "pruned_versions": sum(c["pruned"] for c in cc),
                          "unknown_missing_versions": sum(c["evidence"] == "MISSING_HISTORY_UNCERTAIN" for c in cc),
                          "train_curve_runs": sum(any(isinstance(p.get("train_loss"), (float, int)) for p in details[r["key"]]["points"]) for r in rr),
                          "step_curve_runs": sum(r["curve_granularity"] in ("CHUNK_STEP", "STEP") for r in rr),
                          "unrecorded_curve_runs": sum(r["curve_points"] == 0 for r in rr),
                          "epoch_only_runs": sum(r["curve_granularity"] == "EPOCH" for r in rr)}
    comparisons = []
    grouped = defaultdict(dict)
    for row in runs:
        if row["origin"] != "IMPORTED_ADAPTER" and row["status"] not in ("COMPLETED", "EARLY_STOPPED"):
            continue
        for v in row["validation"]:
            for metric in ("loss", "accuracy", "brier", "ece"):
                if v.get(metric) is not None:
                    set_id = json.dumps(v.get("validation_set"), ensure_ascii=False, sort_keys=True)
                    supervision = "+".join(sorted(row.get("supervision_classes") or []))
                    group = grouped[(row["family"], row["protocol"], set_id, v["stream"], v.get("items"), row.get("loss_definition"), supervision, metric)]
                    previous = group.get(row["key"])
                    value = {"run_id": row["run_id"], "key": row["key"], "epoch": v["epoch"], "value": v[metric]}
                    if previous is None or (value["value"] > previous["value"] if metric == "accuracy" else value["value"] < previous["value"]):
                        group[row["key"]] = value
    for (family, protocol, set_id, stream, items, loss_definition, supervision, metric), values in sorted(grouped.items(), key=lambda pair: str(pair[0])):
        ranked = sorted(values.values(), key=lambda v: v["value"], reverse=metric == "accuracy")
        comparisons.append({"family": family, "protocol": protocol, "validation_set": f"{set_id} / {stream}:{items}",
                            "metric": metric, "loss_definition": loss_definition,
                            "supervision": supervision,
                            "selection": "Each completed run contributes its best observed epoch for this metric",
                            "best": ranked[0], "worst": ranked[-1], "observations": len(values)})
    current_manifest = read_json(p0 / "checkpoint_manifest.json", {})
    recorded_slots = {g.get("new_pool_total_quota") for g in current_manifest.get("comparable_groups", {}).values() if g.get("new_pool_total_quota") is not None}
    payload = {"counts": counts, "runs": runs,
               "retention": {"old_core": old, "new_core": new, "parents": parents, "recovery": recovery,
                             "global_best": global_best,
                             "unclassified": [c for c in checkpoints if c["physical"] and c["path"] not in classified],
                             "new_pool_slots": next(iter(recorded_slots)) if len(recorded_slots) == 1 else None,
                             "manifest_generated_at": current_manifest.get("generated_at"),
                             "cleanup_generated_at": cleanup.get("generated_at", cleanup.get("updated_at")),
                             "source": "physical files + last recorded cleanup; no policy execution"},
               "protocol_counts": {family: dict(Counter(r["protocol"] for r in runs if r["family"] == family)) for family in ("laya", "kev")},
               "comparisons": comparisons, "data_census": full.get("census"),
               "limitations": ["Epoch records count observations, not proof that all versions were physically saved.",
                                "Missing files without deletion evidence remain uncertain.",
                                "Historical learning-rate fields are configured rates; actual scheduler curves were not logged.",
                                "Laya and Kev validation sets and metric definitions are separate.",
                                "Actual per-stream gradient exposure is unavailable for historical streaming runs."]}
    previous = read_json(output / "shards/training_history.json", {})
    content = {k: v for k, v in previous.items() if k not in ("generated_at", "revision")}
    if content == payload:
        payload = previous
    else:
        payload.update(generated_at=now_iso(), revision=time.time_ns())
        atomic_json(output / "shards/training_history.json", payload)
    _HISTORY[str(root)] = {"built_at": time.monotonic(), "payload": payload}
    return payload


def _live_family(family, processes, history):
    proc = processes.get(family, {})
    metric = {"family": family, "status": "IDLE", "is_training": bool(proc.get("train_pid")),
              "process_pid": proc.get("train_pid"), "elapsed_s": proc.get("elapsed_s"),
              **{k: None for k in ("run_id", "epoch", "chunk", "step", "loss", "total_steps", "total_chunks",
                                   "consumed_records", "optimizer_updates", "last_progress_at", "last_progress_age_s")}}
    if not proc:
        recent = [r for r in history["runs"] if r["family"] == family and r.get("training_kind") == "FORMAL_LORA"
                  and r.get("training_status") == "COMPLETED"]
        if recent:
            row = max(recent, key=lambda r: (PROJECT_ROOT / r["root"] / "training_metrics.json").stat().st_mtime)
            terminal = read_json(PROJECT_ROOT / row["root"] / "training_metrics.json", {})
            cursor = read_json((PROJECT_ROOT / row["root"]).parent / "cursor.json", {})
            metric.update(run_id=row["run_id"], status=row.get("training_status", row["status"]),
                          epoch=row["epochs"], planned_epochs=row.get("planned_epochs"),
                          step=terminal.get("optimizer_steps"), optimizer_updates=terminal.get("optimizer_steps"),
                          consumed_records=terminal.get("records_seen"), training_seconds=terminal.get("wall_seconds"),
                          evaluation_status=row.get("evaluation_status"), failure_reason=row.get("failure_reason"),
                          queue_status=row.get("queue_status"), protocol=row["protocol"],
                          last_progress_at=cursor.get("updated_at"), loss=cursor.get("loss"),
                          loss_step=cursor.get("step"))
        return metric
    if family == "laya":
        directory = PROJECT_ROOT / proc["out_root"] / proc["run_id"]
    else:
        directory = PROJECT_ROOT / proc["out"]
    row = next((r for r in history["runs"] if r["root"] == relative(directory, PROJECT_ROOT)), {})
    cursor_path = directory / "cursor.json" if family == "laya" else directory.parent / "cursor.json"
    cursor = read_json(cursor_path, {})
    epoch = cursor.get("epoch")
    step = cursor.get("step_count", cursor.get("step"))
    timestamp = cursor.get("updated_at")
    metric.update(run_id=row.get("run_id", proc.get("run_id", cursor.get("run_id"))),
                  status="TRAINING" if cursor else "PROGRESS_UNAVAILABLE",
                  epoch=(min(epoch + 1, row["planned_epochs"]) if epoch is not None and row.get("planned_epochs") else epoch + 1 if epoch is not None else None),
                  epoch_index=epoch, planned_epochs=row.get("planned_epochs"), chunk=cursor.get("chunk_idx"),
                  step=step, optimizer_updates=step, loss=cursor.get("latest_chunk_loss", cursor.get("loss")),
                  total_steps=cursor.get("total_updates", cursor.get("total_steps")), total_chunks=cursor.get("total_chunks"),
                  consumed_records=cursor.get("consumed_items"), reported_consumed_records=cursor.get("consumed_records"),
                  distinct_units=cursor.get("consumed_units"), last_progress_at=timestamp,
                  last_progress_age_s=age_seconds(timestamp), protocol=row.get("protocol"))
    terminal = read_json(directory / "training_metrics.json", {}) if family == "kev" else {}
    metric["training_seconds"] = terminal.get("wall_seconds")
    if not timestamp:
        metric["status"] = "PROGRESS_UNAVAILABLE"
    if family == "kev":
        metric["consumed_records"] = None
        metric["consumed_scope"] = "Cursor count is step × batch × accum, not an upstream observed records_seen count"
    identity = (metric["run_id"], step)
    last = _PROGRESS.get(family)
    if last is None or last["identity"] != identity:
        rate = None
        if last and last["identity"][0] == metric["run_id"] and timestamp and last.get("timestamp"):
            interval = age_seconds(last["timestamp"]) - age_seconds(timestamp)
            before, after = last.get("consumed_records"), metric["consumed_records"]
            if interval > 0 and before is not None and after is not None and after > before:
                rate = (after - before) / interval
        _PROGRESS[family] = {"identity": identity, "advanced_at": time.monotonic(),
                             "timestamp": timestamp, "consumed_records": metric["consumed_records"],
                             "samples_per_s": rate}
    elif time.monotonic() - last["advanced_at"] > 300:
        metric["status"] = "STALLED"
    if metric["last_progress_age_s"] is not None and metric["last_progress_age_s"] > 300:
        metric["status"] = "STALE" if metric["status"] != "STALLED" else "STALLED"
    metric["samples_per_s"] = _PROGRESS[family].get("samples_per_s")
    metric["training_seconds"] = metric["training_seconds"] if metric["training_seconds"] is not None else proc.get("elapsed_s")
    return metric


def fetch_local_server_data():
    proc = read_local_processes()
    previous = _HISTORY.get(str(PROJECT_ROOT))
    if previous is None or time.monotonic() - previous["built_at"] >= 30:
        history = build_training_history(processes=proc)
    else:
        history = previous["payload"]
    disk = shutil.disk_usage(PROJECT_ROOT)
    return {"connection_status": "CONNECTED", "gpu": read_local_gpu_status(), "process": proc,
            "disk": {"total_bytes": disk.total, "used_bytes": disk.used, "free_bytes": disk.free},
            "laya": _live_family("laya", proc, history), "kev": _live_family("kev", proc, history),
            "history": {"index": "shards/training_history.json", "revision": history["revision"]}}


def fetch_server_data_ssh():
    # Connection details are local configuration, never embedded in the public page.
    runtime = read_json(PROJECT_ROOT / "our-project/experiments/configs/benchmark_runtime.json", {})
    target = os.environ.get("MODELROUTER_SSH_TARGET", runtime.get("dashboard_ssh"))
    key = os.environ.get("MODELROUTER_SSH_KEY", runtime.get("dashboard_ssh_key"))
    remote_root = os.environ.get("MODELROUTER_REMOTE_ROOT")
    if not target or not key or not remote_root:
        return {"connection_status": "DISCONNECTED", "error": "Configure SSH target, key path and remote project root locally"}
    cmd = ["ssh", "-i", key, "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=4", target,
           f"python3 {shlex.quote(remote_root + '/scripts/fetch_live_status.py')} --probe-only"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode:
        return {"connection_status": "DISCONNECTED", "error": "SSH collection failed", "exit_code": result.returncode}
    return json.loads(result.stdout)


def sync_once(source="auto"):
    try:
        local = source == "local" or (source == "auto" and platform.system() == "Linux" and (PROJECT_ROOT / "runs").is_dir())
        data = fetch_local_server_data() if local else fetch_server_data_ssh()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        data = {"connection_status": "DISCONNECTED", "error": type(exc).__name__,
                "laya": {"status": "DISCONNECTED"}, "kev": {"status": "DISCONNECTED"}}
    timestamp = now_iso()
    payload = {"collected_at_iso": timestamp, "collected_at_unix": time.time(), "updated_at": timestamp,
               "collector_source": source, "server_connected": data.get("connection_status") == "CONNECTED", **data}
    atomic_json(OUR_PROJECT_DASHBOARD_DIR / "live_status.json", payload)
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("auto", "local", "ssh"), default="auto")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--history-only", action="store_true")
    args = parser.parse_args()
    if args.history_only:
        history = build_training_history()
        print(json.dumps({"counts": history["counts"], "history": "shards/training_history.json"}))
        return
    if args.probe_only:
        print(json.dumps(fetch_local_server_data()))
        return
    if args.loop:
        while True:
            sync_once(args.source)
            time.sleep(args.interval)
    else:
        print(json.dumps(sync_once(args.source)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
