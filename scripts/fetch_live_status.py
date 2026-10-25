#!/usr/bin/env python3
"""Read training records and publish the existing dashboard's live and per-run data."""
from __future__ import annotations

import argparse
import json
import logging
import math
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
from statistics import median

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
_VAL_CACHE = {}
_REPORT_SIGNATURE = None
logger = logging.getLogger("fetch_live_status")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(finite_values(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def finite_values(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite_values(v) for k, v in value.items()}
    if isinstance(value, list):
        return [finite_values(v) for v in value]
    return value


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


def kev_cursor(directory):
    directory = Path(directory)
    return directory / "cursor.json" if (directory / "cursor.json").is_file() else directory.parent / "cursor.json"


def live_kev_validation(directory, candidate):
    result = read_json(directory / "val_metrics.json", candidate.get("metrics", {}))
    status = result.get("evaluation_status", candidate.get("evaluation_status"))
    fields = {"evaluation_status": status, "validation_metrics": result.get("clean", {}),
              "validation_coverage": result.get("coverage"), "evaluation_seconds": result.get("duration_sec"),
              "validation_device": result.get("device"), "validation_attempt": result.get("attempt_id")}
    if status != "EVALUATING" or not result.get("report_path"):
        return fields
    data_path = Path(result["validation_set"])
    data_stat = data_path.stat()
    identity = (data_stat.st_mtime_ns, data_stat.st_size)
    data = _VAL_CACHE.get(str(data_path))
    if not data or data["identity"] != identity:
        records = questions = 0
        with data_path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    record = json.loads(line)
                    records += 1
                    questions += len(record["questions"])
        data = {"identity": identity, "records": records, "questions": questions}
        _VAL_CACHE[str(data_path)] = data
    predictions = Path(result["report_path"]).parent / "predictions.jsonl"
    progress = _VAL_CACHE.setdefault(str(predictions), {"offset": 0, "records": 0, "questions": 0})
    if predictions.is_file():
        with predictions.open(encoding="utf-8") as stream:
            stream.seek(progress["offset"])
            while True:
                position = stream.tell()
                line = stream.readline()
                if not line or not line.endswith("\n"):
                    progress["offset"] = position
                    break
                prediction = json.loads(line)
                progress["records"] += 1
                progress["questions"] += len(prediction["rows"])
        fields["validation_last_progress_at"] = datetime.fromtimestamp(predictions.stat().st_mtime, timezone.utc).isoformat()
    fields["validation_coverage"] = {"requested_records": data["records"], "requested_questions": data["questions"],
                                     "evaluated_records": progress["records"], "evaluated_questions": progress["questions"]}
    attempts = candidate.get("evaluation_attempts", [])
    started_at = result.get("started_at") or (attempts[-1].get("started_at") if attempts else None)
    fields["evaluation_seconds"] = age_seconds(started_at)
    return fields


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
            "kev" if "kev.train" in argv or "--train-candidate" in argv else None)
        if family:
            options = {a: argv[i + 1] for i, a in enumerate(argv[:-1]) if a.startswith("--")}
            process[family] = {"train_pid": int(pid), "elapsed_s": int(elapsed), "is_training": True,
                               "run_id": options.get("--full-coverage-run", options.get("--sweep-run")),
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
                           **{k: metrics.get(k) for k in ("loss", "nll", "accuracy", "brier", "ece", "items")},
                           "by_type": metrics.get("by_type"),
                           "balanced_accuracy": metrics.get("balanced_accuracy"),
                           "by_source": (epoch.get("validation") or {}).get(stream + "_by_source"),
                           "by_source_target": (epoch.get("validation") or {}).get(stream + "_by_source_target")})
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


def training_context(meta, spec, history, coverage, cursor):
    groups = meta.get("train_groups") or {}
    streams = meta.get("supervision_classes") or spec.get("supervision_classes") or list(groups)
    ratios = meta.get("ratios", spec.get("ratios"))
    requested = dict(zip(streams, ratios)) if isinstance(ratios, list) else ratios
    origin = meta.get("train_origin") or spec.get("category") or ""
    mode = "CONTROLLED_RATIO" if "routing_aligned" in origin else (
        "MATRIX_RATIO" if requested else "FULL_COVERAGE" if meta.get("total_eligible_items") else "HISTORICAL_UNKNOWN")
    trained = coverage.get("trained_by_supervision", meta.get("trained_by_supervision"))
    loaded = meta.get("loaded") or {}
    materialized = {s: loaded["train_" + s].get("rows") for s in streams if "train_" + s in loaded} or None
    encoded = {s: loaded["train_" + s].get("items") for s in streams if "train_" + s in loaded} or None
    times = [e.get("epoch_seconds", e.get("epoch_total_seconds")) for e in history]
    wall = sum(times) if times and all(isinstance(t, (int, float)) and t > 0 for t in times) else None
    if wall is None and meta.get("started_at") and meta.get("finished_at"):
        wall = (datetime.fromisoformat(meta["finished_at"].replace("Z", "+00:00"))
                - datetime.fromisoformat(meta["started_at"].replace("Z", "+00:00"))).total_seconds()
    parent = meta.get("parent_checkpoint_id")
    stage = "ALGN" if mode == "CONTROLLED_RATIO" else "COURSE" if parent else (
        "N_SERIES" if str(meta.get("run_id", "")).startswith("N") else "MATRIX" if requested else origin or None)
    return {"sampling": {"mode": mode, "requested_ratios": requested,
                         "materialized_per_epoch_by_stream": materialized,
                         "encoded_per_epoch_by_stream": encoded,
                         "trained_total_by_stream": trained,
                         "ratio_label": ":".join(str(requested.get(s)) for s in streams) if requested else None},
            "stage": stage, "training_seconds": wall,
            "training_seconds_scope": "sum recorded epoch wall seconds" if times and all(isinstance(t, (int, float)) and t > 0 for t in times) else "recorded run start to finish",
            "initialization": {"base_model": meta.get("base_model"), "parent_checkpoint": parent,
                               "mode": meta.get("continuation_mode", meta.get("resume_mode"))},
            "candidate_by_stream": meta.get("counts", spec.get("counts")), "independent_units_by_stream": meta.get("independent_units", spec.get("independent_units")),
            "audit_flags": meta.get("audit_flags"), "failure_reason": meta.get("error", meta.get("stop_reason")),
            "code_commit": meta.get("code_commit"), "command": meta.get("command")}


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
    matrix = read_json(p0 / "experiment_matrix.json", {})
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
        history = finite_values([{**entry, "consumed_items": entry.get("consumed_items", entry.get("items_consumed"))} for entry in history])
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
        groups = meta.get("train_groups") or {}
        if exposure["trained_records"] is None and groups and meta.get("status") in ("completed", "early_stopped"):
            exposure.update(trained_records=sum(groups.values()) * len(history),
                            trained_records_scope="derived from loaded full-pass items × recorded epochs; not a measured counter")
        if coverage.get("census_metrics", {}).get("distinct_trained_units", 0) > (exposure.get("trained_records") or float("inf")):
            exposure["distinct_units_recorded"] = exposure["distinct_units"]
            exposure["distinct_units"] = None
            exposure["distinct_units_issue"] = "recorded independent units exceed trained records; not used as actual training coverage"
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
               "epoch_records": history,
               "curve_path": f"shards/training_runs/{key}.json", "source": relative(path, root),
               "limitations": ["Actual per-stream gradient exposure was not recorded"] if not exposure["by_stream_actual"] else []}
        spec = (full.get("plans") or {}).get(rid, (matrix.get("plans") or {}).get(rid, {}))
        row["design_description"] = spec.get("description", meta.get("description"))
        row["config"].update(seed=meta.get("seed", row["config"].get("seed")), epochs=meta.get("epochs_max", row["config"].get("epochs")))
        row.update(training_context(meta, spec, history, coverage, cursor))
        row["materialization_audit"] = spec.get("materialization_audit")
        if meta.get("counts") or spec.get("counts"):
            exposure["candidate_records"] = sum((meta.get("counts") or spec["counts"]).values())
            exposure["candidate_records_scope"] = "original legal candidate references before materialization"
        if groups:
            exposure["materialized_records"] = sum(v.get("rows", 0) for k, v in (meta.get("loaded") or {}).items() if k.startswith("train_")) or None
            exposure["encoded_records"] = sum(groups.values())
            exposure["encoded_records_scope"] = "loaded items per epoch; not cumulative encoding operations"
            if exposure.get("trained_records_scope"):
                row["sampling"]["trained_total_by_stream_derived"] = {s: n * len(history) for s, n in groups.items()}
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
        cursor = read_json(kev_cursor(directory), {}) if directory.name in ("formal_run", "checkpoint") else {}
        plan = next((q for q in kev_queue if q.get("checkpoint_path") == relative(directory, root)), {})
        key = run_key("kev", directory, root)
        rid = plan.get("candidate_id", directory.parent.name + "/" + directory.name)
        if directory.parent.name == "models":
            rid = directory.name
        imported = directory.parent.name == "models"
        partial = bool(args.get("max_steps") or args.get("stop_after"))
        protocol = "KEV_IMPORTED_LORA" if imported else ("KEV_FORMAL_LORA" if args.get("device") == "cuda" and not partial else "KEV_LORA_SMOKE")
        retention = plan.get("retention") or {}
        checkpoint = _checkpoint(directory, rid + ":adapter", None, {
            "retention_status": retention.get("status"), "retention_reason": retention.get("reason"),
            "freed_bytes": retention.get("freed_bytes"),
            "was_previously_saved": True if retention.get("status") == "PRUNED_LOW_SCORE" else None}, root)
        result = read_json(directory / "val_metrics.json", read_json(directory / "result.json", plan.get("metrics", {})))
        clean = result.get("clean", {})
        validation = [{"epoch": None, "step": metrics.get("optimizer_steps"), "stream": "clean",
                       "loss": clean.get("nll"), "nll": clean.get("nll"), "accuracy": clean.get("acc"), "brier": clean.get("brier"),
                       "ece": clean.get("ece"), "items": clean.get("n"),
                       "validation_set": result.get("validation_set") or config.get("holdout") or relative(directory / "result.json", root),
                       "source": relative(directory / "val_metrics.json" if result.get("validation_protocol") else directory / "result.json", root)}] if clean else []
        completed_epochs = len(metrics.get("grad_norm", [])) if metrics and not partial else 0
        row = {"key": key, "family": "kev", "run_id": rid, "protocol": protocol,
               "status": "COMPLETED" if metrics else plan.get("training_status", cursor.get("status", "UNKNOWN")),
               "execution_evidence": bool(metrics or cursor.get("step")),
               "training_status": "COMPLETED" if metrics else plan.get("training_status", cursor.get("status", "UNKNOWN")),
               "evaluation_status": plan.get("evaluation_status") or ("FAILED" if plan.get("failure_reason") == "Validation evaluation failed" else "EVALUATED" if clean else "NOT_EVALUATED"),
               "queue_status": plan.get("status"), "failure_reason": plan.get("failure_reason"),
               "validation_metrics": clean, "validation_coverage": result.get("coverage"),
               "comparison_to_c03": result.get("comparison_to_c03", plan.get("comparison_to_c03")),
               "selection": plan.get("selection"), "retention": retention,
               "recipe": plan.get("recipe"), "question_loss_weights": config.get("question_loss_weights"),
               "evaluation_seconds": result.get("duration_sec"),
               "epochs": completed_epochs, "planned_epochs": args.get("epochs"),
               "root": relative(directory, root), "started_at": plan.get("started_at"), "finished_at": plan.get("finished_at"),
               "parent_checkpoint": Path(args["init_from"]).name if args.get("init_from") else None,
               "validation": validation, "checkpoints": [checkpoint],
               "curve_path": f"shards/training_runs/{key}.json", "source": relative(directory / "training_config.json", root),
               "config": {k: args.get(k) for k in ("lr", "head_lr", "epochs", "batch", "accum", "lora", "perm_kl", "synthetic_repeat", "max_steps", "seed", "max_state", "dtype", "weights_dtype", "checkpointing", "lora_targets", "head_dim")},
               "data_path": args.get("data"),
               "terminal_metrics": {k: metrics.get(k) for k in ("wall_seconds", "optimizer_steps", "records_seen", "requested_records")},
               "exposure": {"trained_records": metrics.get("records_seen"), "requested_records": metrics.get("requested_records"),
                            "by_stream_actual": None, "question_exposure": metrics.get("question_exposure"),
                            "optimizer_updates": metrics.get("optimizer_steps")},
               "limitations": ["Imported adapter history is upstream training, not a new local GPU run"] if directory.parent.name == "models" else []}
        row.update(stage="IMPORTED" if imported else "SHORT_TRAINING" if partial else "FORMAL_LORA",
                   supervision_classes=[], sampling={"mode": "FIXED_JSONL", "requested_ratios": None,
                       "materialized_per_epoch_by_stream": None, "trained_total_by_stream": None, "ratio_label": None},
                   training_seconds=metrics.get("wall_seconds"),
                   initialization={"base_model": args.get("base"), "init_from": args.get("init_from")},
                   code_commit=plan.get("code_commit"), command=(plan.get("training_attempts") or [{}])[-1].get("command"))
        row["origin"] = "IMPORTED_ADAPTER" if directory.parent.name == "models" else "LOCAL_RUN"
        row["training_kind"] = "IMPORTED_LORA" if imported else ("LORA_SMOKE" if partial or args.get("device") != "cuda" else "FORMAL_LORA")
        runs.append(row)
        log = directory / "train.log"
        if directory.name in ("formal_run", "checkpoint") and not log.is_file():
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
            for metric in ("loss", "nll", "accuracy", "brier", "ece"):
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
    # The original plan index is static between materialization updates.
    plans = {"full_coverage": full.get("plans"), "matrix": matrix.get("plans"),
             "matrix_generation": matrix.get("generation"),
             "matrix_aggregate": matrix.get("aggregate"), "matrix_audit": matrix.get("audit")}
    plan_path = output / "shards/training_plans.json"
    if read_json(plan_path) != plans:
        atomic_json(plan_path, plans)
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
               "experiment_plans": {"index": "shards/training_plans.json",
                   "matrix_aggregate": matrix.get("aggregate"),
                   "laya_queue": read_json(p0 / "queue_state.json", {}), "kev_queue": [
                       {k: c.get(k) for k in ("candidate_id", "name", "status", "training_status", "evaluation_status",
                          "pending_reason", "failure_reason", "data_path", "init_from", "configuration_source", "comparison_to_c03",
                          "candidate_kind", "metrics", "recipe", "coverage_analysis", "selection", "retention")}
                       for c in kev_queue]},
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


def training_eta(history, plans, live, plan_rows):
    """Estimate the original queue from recorded wall time and configured exposure."""
    root_runs = [r for r in history["runs"] if r["root"].startswith("runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/")]
    samples = []
    for run in root_runs:
        records, seconds = run["exposure"].get("trained_records"), run.get("training_seconds")
        if run["protocol"] == "MR-FULL-GRADED-P0-DATA-REPAIR-v1" and run["status"] in ("COMPLETED", "EARLY_STOPPED") and records and seconds and seconds > 0:
            samples.append({"run_id": run["run_id"], "mode": run["sampling"]["mode"],
                            "supervision": run.get("supervision_classes"), "records_per_second": records / seconds,
                            "records": records, "wall_seconds": seconds, "source": run["source"]})
    full_rates = [s["records_per_second"] for s in samples if s["mode"] == "FULL_COVERAGE" and s["supervision"] == ["S1", "S2", "S3"]]
    matrix_rates = [s["records_per_second"] for s in samples if s["mode"] == "MATRIX_RATIO"]
    val_samples = [e["validation_seconds"] for r in root_runs if r.get("supervision_classes") == ["S1", "S2", "S3"]
                   for e in r.get("epoch_records", []) if e.get("validation_seconds") is not None]
    current = {}
    for family in ("laya", "kev"):
        observed = live.get(family) or {}
        step, total = observed.get("step"), observed.get("total_steps")
        rate = observed.get("samples_per_s")
        method = "recent observed records/s under current GPU sharing"
        if family == "laya":
            remaining = None
            spec = (plans.get("full_coverage") or {}).get(observed.get("run_id"), {})
            census = (history.get("data_census") or {}).get("layers", {})
            total_records = sum(sum(census.get(layer, {}).get(s, 0) for s in spec.get("supervision_classes", []))
                                * fraction for layer, fraction in spec.get("layer_fractions", {}).items()) * spec.get("epochs", 2)
            if rate and observed.get("consumed_records") is not None and total_records:
                remaining = max(0, total_records - observed["consumed_records"]) / rate
            elif step and total and observed.get("elapsed_s"):
                remaining = max(0, total - step) * observed["elapsed_s"] / step
                method = "current process elapsed/optimizer-step; includes initialization"
            remaining_epochs = max(0, spec.get("epochs", 2) - observed.get("epoch_index", 0)) if observed.get("epoch_index") is not None else None
            validation = median(val_samples) * remaining_epochs if val_samples and remaining_epochs is not None else None
        else:
            proc = (live.get("process") or {}).get("kev") or {}
            batch, accum = proc.get("batch"), proc.get("accum")
            remaining = max(0, total - step) * int(batch) * int(accum) / rate if (
                rate and step is not None and total is not None and batch and accum) else None
            method = "upstream cumulative seconds/record × configured batch × accumulation"
            run = next((r for r in history["runs"] if r["family"] == "kev" and r["run_id"] == observed.get("run_id")), {})
            fixed_val = next((v for v in run.get("validation", []) if v["stream"] == "clean"), {})
            timed = [{"run_id": r["run_id"], "seconds": r["evaluation_seconds"], "source": v["source"]}
                     for r in history["runs"] if r["family"] == "kev" and r["protocol"] == run.get("protocol")
                     and r.get("evaluation_status") == "EVALUATED" and r.get("evaluation_seconds")
                     for v in r.get("validation", []) if v["stream"] == "clean"
                     and fixed_val.get("validation_set") is not None and fixed_val.get("items") is not None
                     and v.get("validation_set") == fixed_val["validation_set"] and v.get("items") == fixed_val["items"]]
            validation = median(t["seconds"] for t in timed) if timed else None
            completed = observed.get("status") == "COMPLETED" and not observed.get("is_training") and not proc.get("train_pid")
            if completed:
                remaining, validation = 0, 0
                method = "completed run; no active training worker"
        current[family] = {"run_id": observed.get("run_id"), "status": observed.get("status"),
            "evaluation_status": observed.get("evaluation_status"),
            "remaining_training_seconds": remaining, "validation_seconds": validation,
            "estimated_finish_at": datetime.fromtimestamp(time.time() + remaining + (validation or 0), timezone.utc).isoformat() if remaining is not None and not (family == "kev" and completed) else None,
            "method": method, "validation_in_finish_estimate": validation is not None and not (family == "kev" and completed),
            "validation_method": "same fixed Laya Val timed matrix epochs as a proxy; all remaining epochs" if family == "laya" else
                f"median of {len(timed)} same fixed Kev Val observed durations" + ("; completed run has no pending Val time" if completed else "")}
        if family == "kev":
            current[family]["validation_samples"] = timed
    groups = []
    pending = []
    cpu_times = [p["materialization_audit"]["materialization_seconds"] for p in (plans.get("matrix") or {}).values()
                 if (p.get("materialization_audit") or {}).get("materialization_seconds") is not None]
    census = (history.get("data_census") or {}).get("layers", {})
    for name, category in (("F08–F16", "full_coverage"), ("纯 S3", "full_coverage"), ("原矩阵", "matrix")):
        selected = [p for p in plan_rows if p["category"] == category and p["status"] in ("ELIGIBLE", "CPU_MATERIALIZED")
                    and (category == "matrix" or (p["run_id"].endswith("_S3") if name == "纯 S3" else not p["run_id"].endswith("_S3")))]
        records = 0
        task_times = []
        for p in selected:
            spec = plans[category][p["run_id"]]
            if category == "matrix":
                counts = spec.get("materialized_counts")
                if counts is None:
                    budget = (plans.get("matrix_generation") or {}).get("max_items_per_class")
                    weights = spec.get("ratios") or []
                    if budget is None or not weights:
                        pending.append({"group": p["run_id"], "count": 1, "reason": "recorded materialization budget unavailable"})
                        continue
                    counts = {s: min((spec.get("counts") or {}).get(s, 0), max(1, int(budget * w / sum(weights))))
                              for s, w in zip(spec.get("supervision_classes", []), weights)}
                task_records = sum(counts.values()) * spec.get("epochs", 2)
                records += task_records
                comparable_rates = [s["records_per_second"] for s in samples if s["mode"] == "MATRIX_RATIO"
                                    and s["supervision"] == spec.get("supervision_classes")]
                if comparable_rates:
                    task_times.append((task_records / median(comparable_rates), task_records / max(comparable_rates), task_records / min(comparable_rates)))
            else:
                records += sum(math.floor(sum(census.get(layer, {}).get(s, 0) for s in spec.get("supervision_classes", [])) * fraction)
                               for layer, fraction in spec.get("layer_fractions", {}).items()) * spec.get("epochs", 2)
        rates = matrix_rates if category == "matrix" else full_rates
        rate = median(rates) if rates else None
        wall = records / rate if rate else None
        if category == "matrix" and len(task_times) == len(selected):
            wall = sum(t[0] for t in task_times)
            rate = records / wall if wall else None
        needs_cpu = sum(not p["materialized"] for p in selected) if category == "matrix" else 0
        cpu_seconds = needs_cpu * median(cpu_times) if cpu_times else None
        groups.append({"group": name, "count": len(selected), "run_ids": [p["run_id"] for p in selected],
            "remaining_records": records, "training_seconds": wall, "validation_seconds": None,
            "materialization_seconds": cpu_seconds, "records_per_second": rate,
            "method": "configured full-pass exposure / same-protocol wall throughput; matrix weighted by supervision; validation included" + ("; tri-supervision full runs are a speed surrogate for S3-only" if name == "纯 S3" else "") + ("; fractional records are approximate expectations, unit-based selection may differ" if name == "F08–F16" else ""),
            "fast_seconds": sum(t[1] for t in task_times) if task_times and len(task_times) == len(selected) else records / max(rates) if rates else None,
            "slow_seconds": sum(t[2] for t in task_times) if task_times and len(task_times) == len(selected) else records / min(rates) if rates else None,
            "needs_materialization": needs_cpu})
    pending += [{"group": p["run_id"], "count": 1, "reason": p["reason"]} for p in plan_rows if p["status"] == "PENDING_PARENT"]
    for candidate in history["experiment_plans"]["kev_queue"]:
        if candidate["status"] not in ("COMPLETED", "RUNNING", "TRAINING"):
            pending.append({"group": candidate["candidate_id"], "count": 1,
                            "reason": candidate.get("pending_reason") or candidate.get("failure_reason") or "candidate method/material/initialization unresolved; no launch assumed"})
    live_seconds = [c["remaining_training_seconds"] + (c["validation_seconds"] or 0)
                    for c in current.values() if c["remaining_training_seconds"] is not None]
    cpu_total = sum(g["materialization_seconds"] or 0 for g in groups)
    wall = sum(g["training_seconds"] or 0 for g in groups) + max(live_seconds, default=0) + cpu_total
    low = sum(g["fast_seconds"] or 0 for g in groups) + max(live_seconds, default=0)
    high = sum(g["slow_seconds"] or 0 for g in groups) + sum(live_seconds) + cpu_total
    return {"observed_at": live.get("collected_at_iso", now_iso()), "current": current, "groups": groups,
        "totals": {"serial_wall_seconds": wall, "lower_bound_wall_seconds": low, "range_seconds": [low, high],
                   "estimated_finish_at": datetime.fromtimestamp(time.time() + wall, timezone.utc).isoformat(),
                   "planned_executable_runs": sum(g["count"] for g in groups), "measured_gpu_active_hours": None,
                   "unestimated_cpu_materialization": sum(g["needs_materialization"] for g in groups if g["materialization_seconds"] is None),
                   "estimated_cpu_materialization_seconds": cpu_total if cpu_times else None},
        "blocked": pending, "throughput_samples": samples,
        "assumptions": ["Wall-time GPU-hours are a scheduling estimate, not measured GPU-active time or USD cost.",
            "Current two runs overlap on one GPU; their remaining time is max(), future Laya runs remain sequential.",
            "Completed-run wall throughput includes validation and recorded pauses; no extra validation time is added twice.",
            "CPU materialization uses recorded original-entry durations when available; one sample cannot identify task-to-task variation. Unrecorded switching time remains excluded.",
            "Fast/slow range uses observed same-mode extrema; it is a scenario range, not a statistical confidence interval.",
            "Unresolved parent weights and Kev candidates have no completion date; paper completion is not estimated."]}


def write_training_research_report(history, project_root=PROJECT_ROOT, live=None):
    """Summarize the existing observations; never launch training or read Test."""
    root = Path(project_root)
    plans = read_json(root / "our-project/dashboard" / history["experiment_plans"]["index"], {})
    runs = history["runs"]
    queue = history["experiment_plans"]["laya_queue"]
    by_id = {r["run_id"]: r for r in runs if r["root"].startswith("runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/")}
    plan_rows = []
    for category in ("full_coverage", "matrix"):
        for rid, plan in (plans.get(category) or {}).items():
            observed = by_id.get(rid)
            reason = (queue.get("skipped_runs") or {}).get(rid)
            state = observed["status"] if observed and observed["execution_evidence"] else (
                "SKIPPED" if reason else plan.get("status", "PLANNED"))
            failed = (queue.get("failed_runs") or {}).get(rid) or {}
            if not observed and failed.get("attempts", 0) >= 2:
                state, reason = "FAILED", failed
            parent_id = plan.get("parent_run_id")
            if not observed and parent_id:
                parent = by_id.get(parent_id)
                valid = [v for v in (parent or {}).get("validation", []) if v["stream"] == "S1" and v.get("loss") is not None]
                best = min(valid, key=lambda v: v["loss"]) if valid else None
                physical = any(c["physical"] and best and c["epoch"] == best["epoch"] for c in (parent or {}).get("checkpoints", []))
                if not parent or parent["status"] not in ("COMPLETED", "EARLY_STOPPED") or not physical:
                    state, reason = "PENDING_PARENT", "required completed parent best-epoch weights unavailable: " + parent_id
            plan_rows.append({"category": category, "run_id": rid, "status": state,
                "reason": reason or plan.get("eligibility_reason"), "supervision_classes": plan.get("supervision_classes"),
                "ratios": plan.get("ratios"), "layers": plan.get("layers"),
                "counts": plan.get("counts"), "materialized": plan.get("materialized"),
                "parent_run_id": plan.get("parent_run_id"), "parent_checkpoint_id": plan.get("parent_checkpoint_id")})
    observations = []
    for run in runs:
        if not run["execution_evidence"] and run["origin"] != "IMPORTED_ADAPTER":
            continue
        primary = ("S1" if "S1" in {v["stream"] for v in run["validation"]} else
                   next(iter(run.get("supervision_classes") or []), "S1")) if run["family"] == "laya" else (
                       "clean" if any(v["stream"] == "clean" for v in run["validation"]) else "choice")
        candidates = [v for v in run["validation"] if v["stream"] == primary and v.get("loss") is not None]
        chosen = min(candidates, key=lambda v: v["loss"]) if candidates else None
        accuracy_candidates = [v for v in run["validation"] if v["stream"] == primary and v.get("accuracy") is not None]
        best_accuracy = max(accuracy_candidates, key=lambda v: v["accuracy"]) if accuracy_candidates else None
        values = [v for v in run["validation"] if chosen and v["epoch"] == chosen["epoch"]]
        cp = next((c for c in run["checkpoints"] if chosen and c["epoch"] == chosen["epoch"]), None)
        if run["family"] == "kev" and chosen:
            cp = next(iter(run["checkpoints"]), None)
        accuracy_cp = next((c for c in run["checkpoints"] if best_accuracy and c["epoch"] == best_accuracy["epoch"]), None)
        detail = read_json(root / "our-project/dashboard" / run["curve_path"], {})
        loss_points = [p for p in detail.get("points", []) if isinstance(p.get("train_loss"), (int, float)) and math.isfinite(p["train_loss"])]
        epochs = run.get("epoch_records", [])
        train_epochs = [e for e in epochs if isinstance(e.get("train_loss"), (int, float)) and math.isfinite(e["train_loss"])]
        stage = run.get("stage") or run.get("training_kind")
        meaning = {"ALGN": "按受控比例抽样，比较监督组合与训练预算；与全材料覆盖分别解释。",
                   "MATRIX": "原矩阵的层级、质量、抽样、监督配比对照；仅同材料和预算支持配比比较。",
                   "N_SERIES": "早期训练规模与参数探索；与现行输入协议分别解释。",
                   "COURSE": "从已完成父模型接续，比较课程次序；初始化与额外训练共同改变。",
                   "FORMAL_LORA": "官方 Kev typed state/questions 正式 LoRA；固定项目 Val 单独比较。",
                   "SHORT_TRAINING": "短训练用于通路验证，不能视为正式模型能力。",
                   "IMPORTED": "上游导入资产，不计为本地新增训练。"}.get(stage,
                       "全材料层级/规模对照。" if run["sampling"]["mode"] == "FULL_COVERAGE" else "历史探索或扩展 Pilot；协议与正式训练分别解释。")
        observations.append({"run_id": run["run_id"], "family": run["family"], "protocol": run["protocol"],
            "key": run["key"], "origin": run["origin"], "training_kind": run["training_kind"],
            "design": {"description": run.get("design_description"), "interpretation": meaning,
                       "variables": {"layers": run.get("layers"), "layer_fractions": run.get("layer_fractions"),
                                     "sampling": run.get("sampling"), "config": run.get("config"), "initialization": run.get("initialization")}},
            "status": run["status"], "stage": run.get("stage"), "supervision": run.get("supervision_classes"),
            "sampling": run.get("sampling"), "initialization": run.get("initialization"),
            "config": run.get("config"), "exposure": run["exposure"], "epochs": run["epochs"],
            "training_seconds": run.get("training_seconds"), "best_loss_epoch": chosen,
            "best_accuracy_epoch": best_accuracy, "best_accuracy_physical": accuracy_cp.get("physical") if accuracy_cp else None,
            "best_train_loss_epoch": min(train_epochs, key=lambda e: e["train_loss"]).get("epoch") if train_epochs else None,
            "epoch_records": epochs,
            "evaluation_seconds": run.get("evaluation_seconds"), "evaluation_status": run.get("evaluation_status"),
            "failure_reason": run.get("failure_reason"),
            "loss_trajectory": {"points": len(loss_points), "granularity": run["curve_granularity"],
                                "first": loss_points[0]["train_loss"] if loss_points else None,
                                "last": loss_points[-1]["train_loss"] if loss_points else None,
                                "minimum": min(p["train_loss"] for p in loss_points) if loss_points else None,
                                "maximum_step": max((p.get("step") or 0 for p in detail.get("points", [])), default=0) or None,
                                "segments": len({str(p.get("segment")) for p in detail.get("points", [])})},
            "primary_stream": primary, "validation_all_epochs": run["validation"],
            "loss_definition": run.get("loss_definition"), "validation_coverage": run.get("validation_coverage"),
            "comparison_to_c03": run.get("comparison_to_c03"),
            "candidate_by_stream": run.get("candidate_by_stream"),
            "independent_units_by_stream": run.get("independent_units_by_stream"),
            "materialization_audit": run.get("materialization_audit"),
            "code_commit": run.get("code_commit"), "command": run.get("command"),
            "data_path": run.get("data_path"), "started_at": run.get("started_at"), "finished_at": run.get("finished_at"),
            "training_seconds_scope": run.get("training_seconds_scope", "recorded upstream training wall time"),
            "validation_at_selected_epoch": values, "selected_epoch_physical": cp.get("physical") if cp else None,
            "source": run["source"], "curve_path": run["curve_path"], "checkpoints": run["checkpoints"],
            "actual_cost_usd": None})
    for row in observations:
        trajectory = {}
        for stream in sorted({v["stream"] for v in row["validation_all_epochs"]}):
            values = [v for v in row["validation_all_epochs"] if v["stream"] == stream]
            first, last = values[0], values[-1]
            trajectory[stream] = {"first_epoch": first.get("epoch"), "last_epoch": last.get("epoch"),
                "changes": {k: last[k] - first[k] if len(values) > 1 and isinstance(last.get(k), (int, float)) and isinstance(first.get(k), (int, float)) else None
                            for k in ("accuracy", "loss", "nll", "brier", "ece")},
                "interpretation": "within-run observed change, not isolated causal effect"}
        row["validation_changes"] = trajectory
        peers = [r for r in observations if r["key"] != row["key"] and r["family"] == row["family"] and r["protocol"] == row["protocol"]
                 and r["best_loss_epoch"] and row["best_loss_epoch"]
                 and r["primary_stream"] == row["primary_stream"] and r["loss_definition"] == row["loss_definition"]
                 and r["best_loss_epoch"].get("validation_set") == row["best_loss_epoch"].get("validation_set")
                 and r["best_loss_epoch"].get("items") == row["best_loss_epoch"].get("items")
                 and r["design"]["variables"]["layers"] == row["design"]["variables"]["layers"]
                 and r["initialization"] == row["initialization"]]
        control = next((r for r in peers if r["supervision"] == ["S1"] and r["stage"] == row["stage"]), None)
        row["comparison"] = {"control_key": control["key"] if control else None,
            "accuracy_delta": row["best_loss_epoch"]["accuracy"] - control["best_loss_epoch"]["accuracy"] if control and row["best_loss_epoch"].get("accuracy") is not None and control["best_loss_epoch"].get("accuracy") is not None else None,
            "loss_delta": row["best_loss_epoch"]["loss"] - control["best_loss_epoch"]["loss"] if control else None,
            "stream": row["primary_stream"],
            "scope": "same model/protocol/Val/target/loss definition/layers/initialization; exposure, budget and selected epoch may differ"}
        has_physical = any(c["physical"] for c in row["checkpoints"])
        row["candidate_role"] = ("短训练或Pilot实体，正式能力待评测" if has_physical and row["training_kind"] in ("LORA_SMOKE", "POINTER_HEAD_PILOT") else
                                 "辅助目标实体，S1选模能力无实测" if has_physical and row["family"] == "laya" and row["primary_stream"] != "S1" else
                                 "可加载的离线候选，任务级能力待评测" if row["selected_epoch_physical"] else
                                 "可加载的其他Epoch候选，最低Loss实体不可用，指标按实际Epoch呈现" if has_physical else
                                 "历史消融或负结果；主Val最佳实体不可用" if row["best_loss_epoch"] else "证据不足，保留历史对象")
        row["missing_evidence"] = [label for label, missing in (
            ("逐监督梯度贡献", True), ("实付费用", True), ("独立任务成功率/完整Episode费用", True),
            ("完整训练耗时", row["training_seconds"] is None), ("主Val", row["best_loss_epoch"] is None),
            ("最佳Loss实体", not row["selected_epoch_physical"])) if missing]
    loadable = []
    trends = {}
    metric_fields = ("epoch", "step", "stream", "accuracy", "loss", "nll", "brier", "ece", "items", "validation_set", "source")
    for row in observations:
        for checkpoint in row["checkpoints"]:
            if not checkpoint["physical"]:
                continue
            validation = [{k: v.get(k) for k in metric_fields} for v in row["validation_all_epochs"] if v["epoch"] == checkpoint["epoch"]]
            loadable.append({"key": row["key"], "run_id": row["run_id"], "family": row["family"],
                "protocol": row["protocol"], "training_kind": row["training_kind"], "primary_stream": row["primary_stream"],
                "checkpoint_id": checkpoint["checkpoint_id"], "epoch": checkpoint["epoch"],
                "path": checkpoint["path"], "evidence": checkpoint["evidence"], "validation": validation,
                "primary_validation": next((v for v in validation if v["stream"] == row["primary_stream"]), None),
                "is_best_loss_epoch": bool(row["best_loss_epoch"] and checkpoint["epoch"] == row["best_loss_epoch"]["epoch"]),
                "is_best_accuracy_epoch": bool(row["best_accuracy_epoch"] and checkpoint["epoch"] == row["best_accuracy_epoch"]["epoch"]),
                "candidate_role": row["candidate_role"], "source": row["source"]})
        selected = row["best_loss_epoch"]
        if not selected or selected.get("validation_set") is None or selected.get("items") is None:
            continue
        identity = (row["family"], row["protocol"], json.dumps(selected["validation_set"], ensure_ascii=False, sort_keys=True),
                    row["primary_stream"], selected["items"], row["loss_definition"])
        group = trends.setdefault(identity, {"family": row["family"], "protocol": row["protocol"],
            "validation_set": selected["validation_set"], "stream": row["primary_stream"], "items": selected["items"],
            "loss_definition": row["loss_definition"], "observations": [],
            "scope": "same model/protocol/fixed Val/target/loss definition; descriptive history, budgets and initialization may differ"})
        group["observations"].append({"key": row["key"], "run_id": row["run_id"], "status": row["status"],
            "started_at": row["started_at"], "supervision": row["supervision"], "sampling": row["sampling"],
            "initialization": row["initialization"], "trained_records": row["exposure"].get("trained_records"),
            "training_seconds": row["training_seconds"], "best_loss_epoch": {k: selected.get(k) for k in metric_fields},
            "selected_epoch_physical": row["selected_epoch_physical"],
            "best_accuracy_epoch": {k: row["best_accuracy_epoch"].get(k) for k in metric_fields} if row["best_accuracy_epoch"] else None,
            "best_accuracy_physical": row["best_accuracy_physical"], "source": row["source"]})
    for group in trends.values():
        group["observations"].sort(key=lambda r: (r["started_at"] is None, r["started_at"] or "", r["run_id"]))
        group["order"] = "recorded start time; undated runs follow in Run ID order"
    def public(value):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if isinstance(value, str):
            return value.replace(str(root) + "/", "").replace(str(root), ".")
        if isinstance(value, dict):
            return {k: public(v) for k, v in value.items() if k not in ("raw_output", "error")}
        if isinstance(value, list):
            return [public(v) for v in value]
        return value
    result = public({"generated_at": now_iso(), "code_commit": os.environ.get("MODELROUTER_CODE_COMMIT"),
        "counts": history["counts"], "plans": plan_rows, "observations": observations,
        "loadable_candidates": loadable, "objective_trends": list(trends.values()),
        "retention": history["retention"], "comparisons": history["comparisons"],
        "kev_candidates": history["experiment_plans"]["kev_queue"], "data_census": history.get("data_census"),
        "laya_queue": {k: queue.get(k) for k in ("queue_status", "current_run", "next_run", "failed_runs", "blocked_runs")},
        "kev_materialization": read_json(root / "data/kev/v8_extension/materialization.json", {}),
        "selection": "One minimum primary validation Loss epoch per run; highest Accuracy epoch is independent; loadable candidates use their actual epoch metrics",
        "limitations": history["limitations"]})
    live = live if live is not None else read_json(root / "our-project/dashboard/live_status.json", {})
    result["live_observation"] = public({k: live.get(k) for k in ("collected_at_iso", "server_connected", "gpu", "process", "laya", "kev")})
    result["training_eta"] = public(training_eta(history, plans, live, plan_rows))
    result["continuation"] = {
        "laya_boundary_reload_requested": (root / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/.reload_queue_daemon").is_file(),
        "laya_order": [p["run_id"] for p in plan_rows if p["category"] == "full_coverage" and p["status"] in ("TRAINING", "ELIGIBLE")],
        "kev_boundary": "The original dispatcher owns training and Val; terminal results and pending reasons remain in the original records",
        "kev_retention_applied": any((c.get("retention") or {}).get("applied") for c in result["kev_candidates"]),
        "kev_pruned_weight_bytes": sum((c.get("retention") or {}).get("total_released_bytes", 0) for c in result["kev_candidates"]),
    }
    destination = root / "our-project/results/training"
    atomic_json(destination / "training_research.json", result)
    def cell(v):
        return "N/A" if v is None else json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    def table(headers, records):
        return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
            "| " + " | ".join(cell(v).replace("|", "/").replace("\n", " ") for v in record) + " |" for record in records]
    lines = ["# Laya / Kev 全历史训练研究报告", "", "生成时间：" + result["generated_at"], "",
        "本报告来自原 Run、Epoch、Cursor、训练日志、队列和权重目录；当前训练仍在执行，全部计划尚未完成。",
        "仅使用训练记录和项目 Val，不读取最终 Test。Loss 最佳 Epoch 与 Accuracy 最佳 Epoch分别识别；本表按主任务最低 Val Loss选择同一 Epoch，辅助成绩沿用该 Epoch。", "",
        "## 1. 历史对象与物理实体", ""]
    lines += table(["模型", "实际本地 Run", "结束 Run", "运行 Run", "导入资产", "Epoch", "版本", "实体", "Step/Chunk曲线", "Epoch曲线"], [
        [family, c["executed_runs"], c["completed_runs"], c["running_runs"], c["imported_assets"], c["recorded_epochs"], c["checkpoint_versions"], c["physical_checkpoints"], c["step_curve_runs"], c["epoch_only_runs"]]
        for family, c in result["counts"].items()])
    lines += ["", "旧五份实体：" + str(sum(bool(c["physical"]) for c in result["retention"]["old_core"])) + "/5。新池、课程父权重与恢复点分别见 JSON；缺失实体没有被恢复。", "",
        "## 2. 现有计划执行情况", ""]
    lines += table(["计划", "状态", "数量"], [[category, status, count] for category in ("full_coverage", "matrix")
        for status, count in sorted(Counter(p["status"] for p in plan_rows if p["category"] == category).items())])
    lines += ["", "全部计划 ID、组合、配比、层级、材料数量和原原因保存在 training_research.json 的 plans，未执行不代表完成。", "",
        "## 3. 同协议描述比较", "", "模型、协议、Val身份、问题数量与监督组合分别分组。组内仍可能包含数据量、初始化、预算和层级差异，排名不能解释为配比的因果效应。", ""]
    lines += table(["模型/协议", "Val/监督", "指标", "Run数", "最好", "最差"], [[c["family"] + "/" + c["protocol"], c["validation_set"] + "/" + c["supervision"], c["metric"], c["observations"], c["best"], c["worst"]] for c in result["comparisons"] if c["observations"] > 1])
    lines += ["", "## 4. 全部已执行版本", ""]
    lines += table(["模型/Run", "协议/阶段", "组合/配比", "训练量/独立量", "Epoch/时间s", "主Val最低Loss Epoch", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "该Epoch实体"], [
        [r["family"] + "/" + r["run_id"], r["protocol"] + "/" + str(r["stage"]), str(r["supervision"]) + "/" + str((r["sampling"] or {}).get("ratio_label")),
         str(r["exposure"].get("trained_records")) + "/" + str(r["exposure"].get("distinct_units")), str(r["epochs"]) + "/" + str(r["training_seconds"]),
         (r["best_loss_epoch"] or {}).get("epoch"), [{k: v.get(k) for k in ("stream", "accuracy", "loss", "nll", "brier", "ece")} for v in r["validation_at_selected_epoch"]], r["selected_epoch_physical"]] for r in result["observations"]])
    lines += ["", "## 5. 同材料范围配比对照", "",
        "B02/QB/PB 保持原材料范围、初始化、种子与两Epoch预算。主Val按每Run最低主Loss选择；选中Epoch不同会影响比较，全部Epoch均保存在JSON。", ""]
    ratio_rows = [r for r in result["observations"] if r["run_id"].startswith("P0_B02_C") and r["run_id"].endswith("QB_PB") and r["protocol"] == "MR-FULL-GRADED-P0-DATA-REPAIR-v1"]
    lines += table(["Run/监督", "主目标", "配比", "载入/stream", "所选Epoch", "主Val Accuracy", "Loss", "Brier", "ECE", "辅助Val"], [
        [r["run_id"] + "/" + str(r["supervision"]), r["primary_stream"], (r["sampling"] or {}).get("ratio_label"), r["exposure"].get("train_groups"),
         (r["best_loss_epoch"] or {}).get("epoch"), (r["best_loss_epoch"] or {}).get("accuracy"), (r["best_loss_epoch"] or {}).get("loss"),
         (r["best_loss_epoch"] or {}).get("brier"), (r["best_loss_epoch"] or {}).get("ece"),
         [{k: v.get(k) for k in ("stream", "accuracy", "loss", "brier", "ece")} for v in r["validation_at_selected_epoch"] if v["stream"] != r["primary_stream"]]] for r in ratio_rows])
    lines += ["", "上表分别呈现Accuracy与概率质量，不宣布唯一最优比例。", "",
        "F06完整轨迹：" + cell([{k: v.get(k) for k in ("epoch", "stream", "accuracy", "loss", "brier", "ece")} for r in result["observations"] if r["run_id"] == "F06" for v in r["validation_all_epochs"]]), "",
        "曝光数量异常：" + cell([{ "run_id": r["run_id"], "exposure": r["exposure"]} for r in result["observations"] if r["exposure"].get("distinct_units_issue")]), "",
        "## 6. Kev 候选与材料", "",
        "正式Kev的实际训练状态与全部固定Val：" + cell([{ "run_id": r["run_id"], "status": r["status"], "validation": r["validation_all_epochs"]} for r in result["observations"] if r["family"] == "kev" and r["stage"] == "FORMAL_LORA"]),
        "C05原文本state含任务与Prompt，没有可单独移除的动态字段，未创建无效状态消融。C07既定Rank8与现有Rank16初权重不兼容，从基座重建会同时改变初始化，未擅自启动。",
        "C09原视图与项目固定划分不一致。原转换入口仅导出位于同一项目Train/Val的Arena记录，保持任务文本与typed标签；导出训练记录全部已在C03使用，新训练记录为0。缓存标量及已观察终局没有当前正式配置的typed目标，完整C09保持PARTIAL_MATERIAL/PENDING，不重训C03材料冒充新增数据。", "",
        "材料统计：" + cell(result["kev_materialization"]), "",
        "Kev训练与Val沿用原入口，当前状态见实时观测；候选方法与材料待决原因保留在原队列。", "",
        "## 7. 科学解释与当前限制", "",
        "1. 候选规模、物化、编码、实际训练量和独立量分别保留。由载入条目×Epoch派生的数带 scope说明，不能当实测计数。逐监督梯度贡献没有历史记录，无法直接识别。",
        "2. S1与加入S2/S3的比较使用同Val的Accuracy、Loss、Brier和ECE。Laya没有单独保存的NLL使用N/A；不得擅自把不同标签的Loss合并为主路由收益。",
        "3. S1/S3的1:1、2:1、1:2及三监督配比均保留原参数。只有初始化、材料范围、预算和Val都一致时才支持受控比较。",
        "4. F全量自然材料覆盖与ALGN按最小供给的受控抽样存在曝光与优化器预算差异；两者不能用于单独证明监督组合效应。",
        "5. 层级、规模、种子和课程变化保留逐Run轨迹；缺失课程父权重的子项不能通过改用基座或重训已完成父Run来补齐。",
        "6. Accuracy与概率质量可能发生权衡。饱和、过拟合和负迁移应结合完整Val轨迹及同协议对照判断，不能由最小Train Loss直接推断。",
        "7. Kev正式LoRA、导入模型、部分训练及Pointer Head Pilot分开。C04使用C03权重与新优化器；收益同时包含更多训练及不同学习率。C05状态不可分离、C07 Rank与初始化不兼容时保留待决原因。",
        "8. 固定Val连续参与选模，结果为开发期描述；不能代替独立最终Test，也不直接比较Laya与Kev不同Val的Accuracy。",
        "9. 各Run主Val最佳Epoch的实体状态逐行展示，元数据不能代替可加载权重。留存策略源码与服务器实际部署状态分别报告。",
        "10. 本轮可支持RQ4训练监督与概率质量的离线消融准备。正式任务成功率、完整Episode费用、Model×Effort效果与RQ1–RQ5结论仍需原版Verifier的真实AgentEpisode。", "",
        "训练实付费用N/A；本地权重没有Token按量费用。原日志路径、配置、曝光和每个版本实体状态见同目录JSON，曲线仍由原shards/training_runs提供。", ""]
    def compact_metric(r):
        v = r["best_loss_epoch"] or {}
        return [r["run_id"], r["primary_stream"], (r["sampling"] or {}).get("ratio_label"), r["exposure"].get("trained_records"),
                r["training_seconds"], v.get("epoch"), *[v.get(k) for k in ("accuracy", "loss", "nll", "brier", "ece")],
                r["selected_epoch_physical"]]
    eta = result["training_eta"]
    overview = ["## Executive Summary", "",
        "Laya 实际执行 " + str(result["counts"]["laya"]["executed_runs"]) + " 个 Run；Kev本地执行与导入资产分别统计，完整对象见附录。历史完成项目沿用原结果。",
        "当前双模型进度：" + cell([{ "model": family, "run_id": eta["current"][family]["run_id"], "status": eta["current"][family]["status"], "evaluation_status": eta["current"][family]["evaluation_status"]} for family in ("laya", "kev")]) + "。观测时间：" + cell(eta["observed_at"]) + "。",
        "B02 同层级配比对照显示，增加辅助监督没有稳定提高 S1 Accuracy。S1+S3 的 2:1 存在主Loss改善与Accuracy下降的权衡；S2+S3缺少直接S1监督，主任务结果较弱。具体值与预算见下表。",
        "ALGN四项在主Val上的差异较小，但训练曝光和时间不同。F系列增加全材料覆盖后的主任务Accuracy可能上升，辅助概率质量可能恶化。无法由单次开发期Val确定最优比例或模型架构。",
        "旧五份实体只剩 " + str(sum(c["physical"] is True for c in result["retention"]["old_core"])) + " 份。主Val最低Loss模型与当前可加载模型分开。Kev实体处理见下方同协议记录，Laya原策略保持。",
        "建议先完成原定当前Run和代表性对照，再由Planning决定是否减少新增矩阵。离线证据已支持监督与概率质量分析，任务成功率和真实费用仍需官方AgentEpisode。",
        "现有可计算队列预计墙钟 " + str(round(eta["totals"]["serial_wall_seconds"] / 3600, 1)) + " 小时；CPU物化、共享GPU波动和待决候选的限制见时间预算。整体论文完成日期N/A。", "",
        "## 技术演进与研究变量", "",
        "早期N系列和旧输入协议探索训练规模、参数和输入表达；旧协议16项与现行P0协议分别统计。P0矩阵把监督组合、比例、层级、质量和采样拆为已有参数，实际完成的槽位支持开发期对照。",
        "ALGN采用受控配比与有限抽样；F系列逐层、累计层、比例子集采用全材料覆盖。课程Run改变初始化及训练次序。V8扩展中的Pointer Head Pilot与正式LoRA分别记录，不能用Pilot代表完整Kev训练。",
        "Kev C03通过官方typed state/questions接口完成正式训练和项目固定Val；C04从C03接续，学习率与训练预算共同改变。不同模型Val和输出标签并不一致，当前没有跨架构因果对照。", "",
        "## 可观察的配比、预算与任务权衡", "",
        "下表按最低主Val Loss的同一Epoch取Accuracy、Brier、ECE；完整Epoch在附录。S1-only可作为同层主监督参考，辅助任务仍分别呈现。S2/S3主目标衡量各自标签，不能用于S1模型选择能力排序；缺少S1实测保留N/A。小样本单种子差异未作显著性或因果宣称。", ""]
    overview += table(["B02 Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"], [compact_metric(r) for r in ratio_rows])
    overview += ["", "ALGN受控配比：", ""]
    overview += table(["Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"],
                      [compact_metric(r) for r in result["observations"] if r["stage"] == "ALGN"])
    overview += ["", "全材料及纯监督按层级/规模保留各自预算；下表不能单独隔离监督比例的影响。", ""]
    overview += table(["Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"],
                      [compact_metric(r) for r in result["observations"] if r["family"] == "laya" and r["sampling"]["mode"] == "FULL_COVERAGE"])
    overview += ["", "F06最低S1 Loss与最高S1 Accuracy独立列出，同列的其他指标均来自对应Epoch：", ""]
    overview += table(["Run", "选择依据", "Epoch", "Accuracy", "Loss", "Brier", "ECE", "实体"],
                      [[r["run_id"], label, *[(r[field] or {}).get(k) for k in ("epoch", "accuracy", "loss", "brier", "ece")], r[physical]]
                       for r in result["observations"] if r["run_id"] == "F06"
                       for label, field, physical in (("最低S1 Loss", "best_loss_epoch", "selected_epoch_physical"),
                                                      ("最高S1 Accuracy", "best_accuracy_epoch", "best_accuracy_physical"))])
    overview += ["", "F06的主任务/辅助任务逐Epoch值：", ""]
    overview += table(["Epoch", "监督", "Accuracy", "Loss", "Brier", "ECE"],
                      [[v.get(k) for k in ("epoch", "stream", "accuracy", "loss", "brier", "ece")]
                       for r in result["observations"] if r["run_id"] == "F06" for v in r["validation_all_epochs"] if v["stream"] in ("S1", "S2", "S3")])
    overview += ["", "F06第二Epoch主Accuracy上升但主Loss没有改善，S2 Loss/ECE恶化；主Accuracy、校准、辅助任务收益应分别解释。现有记录不足以区分更多数据、训练时间和共享表征造成的影响。",
        "全量候选统计：" + cell(result["data_census"]) + "。这是候选材料规模；ALGN抽样、矩阵quota、编码跳过和重复曝光均会改变优化器实际输入。逐监督梯度贡献没有记录，不能从原材料比例推断。", "",
        "## 同固定Val、同目标的历史趋势", "",
        "各组按原记录的开始时间排列，未记录时间的Run按ID列在后面。最低Loss与最高Accuracy各自选择Epoch，实体状态分别列出；层级、配比、初始化和训练预算可能不同，趋势仅作描述。S1、S2、S3与Kev clean分别呈现，未将辅助目标当作S1收益。", ""]
    for group in result["objective_trends"]:
        if len(group["observations"]) < 2:
            continue
        overview += ["", cell({k: group[k] for k in ("family", "protocol", "validation_set", "stream", "items", "loss_definition")}), ""]
        overview += table(["Run/状态", "监督/比例", "训练曝光/时间s", "最低Loss Epoch", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "Loss实体", "最高Accuracy Epoch", "Accuracy", "Accuracy实体"],
                          [[r["run_id"] + "/" + r["status"], {"streams": r["supervision"], "ratio": r["sampling"]["ratio_label"]},
                            "/".join(cell(r[k]) for k in ("trained_records", "training_seconds")), r["best_loss_epoch"]["epoch"],
                            "/".join(cell(r["best_loss_epoch"].get(k)) for k in ("accuracy", "loss", "nll", "brier", "ece")), r["selected_epoch_physical"],
                            (r["best_accuracy_epoch"] or {}).get("epoch"), (r["best_accuracy_epoch"] or {}).get("accuracy"), r["best_accuracy_physical"]]
                           for r in group["observations"]])
    overview += ["", "## 可加载实体与最终候选", "",
        "以下候选仅来自采集时有实体的记录，指标使用实体对应Epoch；最低Loss实体缺失时不挪用其成绩。短训练、Pilot、导入资产与正式训练分别标明，任务级能力仍待评测。", ""]
    overview += table(["模型/Run", "协议/类别", "主目标", "Epoch", "最低Loss/最高Accuracy Epoch", "Val/数量", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "用途", "实体位置"],
                      [[c["family"] + "/" + c["run_id"], c["protocol"] + "/" + c["training_kind"], c["primary_stream"], c["epoch"],
                        [c["is_best_loss_epoch"], c["is_best_accuracy_epoch"]],
                        "/".join(cell((c["primary_validation"] or {}).get(k)) for k in ("validation_set", "items")),
                        "/".join(cell((c["primary_validation"] or {}).get(k)) for k in ("accuracy", "loss", "nll", "brier", "ece")), c["candidate_role"], c["path"]]
                       for c in result["loadable_candidates"]])
    missing_best = [r for r in result["observations"] if r["family"] == "laya" and r["best_loss_epoch"] and not r["selected_epoch_physical"]]
    overview += ["", "Laya有主Val Loss的实际Run中，" + str(len(missing_best)) + " 个最佳Loss Epoch没有物理实体。可使用现存候选做任务级实验，历史最优成绩只能用于离线分析；替代实体不能标成相同Epoch。",
        "Kev正式固定Val和coverage：" + cell([{ "run_id": r["run_id"], "metrics": r["validation_all_epochs"], "coverage": r["validation_coverage"], "comparison_to_c03": r["comparison_to_c03"], "training_seconds": r["training_seconds"], "evaluation_seconds": r["evaluation_seconds"]}
                                              for r in result["observations"] if r["family"] == "kev" and r["stage"] == "FORMAL_LORA"]), "",
        "### Kev候选、模型内评分与实体留存", "",
        "评分只用于同一固定Val下的内部实体选择，论文主指标保持原始Accuracy、NLL、Brier、ECE。C11是现有候选选择记录，不新增训练或复制权重。", ""]
    overview += table(["候选", "执行/Val", "Accuracy/NLL/Brier/ECE", "内部评分", "实体状态/释放字节", "尚缺条件"],
                      [[c["candidate_id"], [c.get("status"), c.get("evaluation_status")],
                        (c.get("metrics") or {}).get("clean"), c.get("selection"), c.get("retention"),
                        c.get("pending_reason") or c.get("failure_reason")]
                       for c in result["kev_candidates"]])
    overview += ["", "配方、原训练命令、父实体与验证记录保留在candidate_queue.json、candidate_ledger.json和本报告JSON；未记录的数据内容标识与历史源码提交使用N/A，不承诺遗失材料可精确重建。", "",
        "## 终点与Planning建议", "",
        "Run级：全材料入口按原定Epoch完成，当前运行状态见实时观测，Kev已完成Val不计入待运行耗时。矩阵/历史小训练入口已有连续两Epoch未达0.5%主Loss改善的结束条件；该条件不适用于全材料入口，不新增结束规则。",
        "实验组级：结合所有Epoch观察Accuracy、Loss、Brier、ECE。F06的权衡及B02辅助监督的负结果支持减少机械扩张的建议，不能据此提前结束健康Run。当前缺多种子误差与独立Test，尚不能宣布性能平台期或唯一最优比例。",
        "整体研究级：代表性主监督、受控双/三监督、层级与规模已有离线结果。建议Planning优先保留能隔离预算和初始化的关键对照，并尽早转向官方Episode；原矩阵缩减只作为建议，执行计划本轮不变。",
        "缩减情景以本次ETA下表的剩余Run和组预算为依据；已完成Run的耗时不可再节省。保留哪些对照尚未确定，部分缩减的可节省时间N/A；原计划本轮不变。",
        "若Planning取消全部尚未运行原矩阵，可节省下表该组的估算墙钟，但会失去质量/采样/层级扩展及未运行配比重复对照；若取消纯S3，将失去辅助目标单独训练的完整规模对照。建议不把课程缺父实体转成新的重训计划。", "",
        "## 全剩余队列时间预算", "", "最后观测时间：" + cell(eta["observed_at"]) + "。", ""]
    overview += table(["当前Run", "剩余训练h", "Val h", "预计结束UTC", "依据"],
                      [[c["run_id"], round(c["remaining_training_seconds"] / 3600, 2) if c["remaining_training_seconds"] is not None else None,
                        round(c["validation_seconds"] / 3600, 2) if c["validation_seconds"] is not None else None,
                        c["estimated_finish_at"], c["method"]] for c in eta["current"].values()])
    overview += ["", "下面训练预算包含历史同类墙钟中的固定验证，未重复计入Val；GPU实际活跃时间N/A。", ""]
    overview += table(["组", "剩余Run", "预计曝光", "历史吞吐records/s", "预计墙钟h", "最快/最慢h", "待物化"],
                      [[g["group"], g["count"], g["remaining_records"], g["records_per_second"],
                        round(g["training_seconds"] / 3600, 2) if g["training_seconds"] is not None else None,
                        [round(g[k] / 3600, 2) if g[k] is not None else None for k in ("fast_seconds", "slow_seconds")],
                        g["needs_materialization"]] for g in eta["groups"]])
    overview += ["", "总体估计：" + cell(eta["totals"]), "",
        "CPU物化和任务切换没有完整独立历史耗时，保留N/A；原矩阵待物化数量不视为已就绪。当前两Run取较长剩余时间估算重叠阶段，后续Laya串行。最快/最慢来自历史有效吞吐极值，属于情景范围，无法保证未来GPU资源稳定。",
        "课程父权重、Kev状态标签/Rank初始化/V8材料待决：" + cell(eta["blocked"]), "",
        "完整吞吐样本及原文件位置在training_research.json的training_eta.throughput_samples，每Run自然边界和原采集器轻量状态更新ETA。训练矩阵结束、待决实验结束与论文科研闭环是三个不同时间范围。", "",
        "## 附录：对象、原始Epoch与日志索引", ""]
    # Readable conclusions precede the existing complete historical tables.
    lines = lines[:7] + [""] + overview + lines[7:]
    lines += ["", "### 逐对象设计、关系、用途与缺证", ""]
    lines += table(["对象/类别", "设计与变量", "初始化/配置", "合理对照/变化", "Train轨迹", "最佳Train/Loss/Accuracy Epoch", "用途", "缺证/来源"],
        [[r["family"] + "/" + r["run_id"] + "/" + r["origin"] + "/" + r["training_kind"], r["design"],
          {"initialization": r["initialization"], "config": r["config"]}, {"control": r["comparison"], "within_run": r["validation_changes"]}, r["loss_trajectory"],
          {"train": r["best_train_loss_epoch"], "loss": (r["best_loss_epoch"] or {}).get("epoch"), "accuracy": (r["best_accuracy_epoch"] or {}).get("epoch"), "accuracy_physical": r["best_accuracy_physical"]},
          r["candidate_role"], {"missing": r["missing_evidence"], "source": r["source"], "curve": r["curve_path"]}] for r in result["observations"]])
    lines += ["", "### 全部Epoch指标", ""]
    lines += table(["对象", "Epoch", "Step", "Train Loss", "训练/验证/保存秒", "监督", "Accuracy", "Loss", "NLL", "Brier", "ECE", "来源"],
        [[r["family"] + "/" + r["run_id"], v.get("epoch"), v.get("step"),
          next((e.get("train_loss") for e in r["epoch_records"] if e.get("epoch") == v.get("epoch")), None),
          next(({k: e.get(k) for k in ("train_seconds", "validation_seconds", "checkpoint_seconds", "epoch_seconds")} for e in r["epoch_records"] if e.get("epoch") == v.get("epoch")), None),
          *[v.get(k) for k in ("stream", "accuracy", "loss", "nll", "brier", "ece", "source")]] for r in result["observations"] for v in r["validation_all_epochs"]])
    report = destination / "training_research.md"
    temporary = report.with_suffix(".md.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(report)
    return {"report": relative(report, root), "data": "our-project/results/training/training_research.json", "counts": result["counts"]}


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
            cursor = read_json(kev_cursor(PROJECT_ROOT / row["root"]), {})
            metric.update(run_id=row["run_id"], status=row.get("training_status", row["status"]),
                          epoch=row["epochs"], planned_epochs=row.get("planned_epochs"),
                          step=terminal.get("optimizer_steps"), optimizer_updates=terminal.get("optimizer_steps"),
                          consumed_records=terminal.get("records_seen"), training_seconds=terminal.get("wall_seconds"),
                          evaluation_status=row.get("evaluation_status"), failure_reason=row.get("failure_reason"),
                          queue_status=row.get("queue_status"), protocol=row["protocol"],
                          last_progress_at=cursor.get("updated_at"), loss=cursor.get("loss"),
                          loss_step=cursor.get("loss_step", cursor.get("step")))
            metric.update(validation_metrics=row.get("validation_metrics"),
                          validation_coverage=row.get("validation_coverage"), evaluation_seconds=row.get("evaluation_seconds"))
            if terminal.get("records_seen") and terminal.get("wall_seconds"):
                metric.update(samples_per_s=terminal["records_seen"] / terminal["wall_seconds"],
                              speed_scope="completed training records / upstream wall seconds",
                              speed_source=relative(PROJECT_ROOT / row["root"] / "training_metrics.json", PROJECT_ROOT),
                              speed_step=terminal.get("optimizer_steps"))
        return metric
    if family == "laya":
        directory = PROJECT_ROOT / proc["out_root"] / proc["run_id"]
    else:
        directory = PROJECT_ROOT / proc["out"]
    row = next((r for r in history["runs"] if r["root"] == relative(directory, PROJECT_ROOT)), {})
    cursor_path = directory / "cursor.json" if family == "laya" else kev_cursor(directory)
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
        metric["loss_step"] = cursor.get("loss_step", step)
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
    if family == "kev":
        log = directory / "train.log"
        if not log.is_file():
            log = directory.parent / "train.log"
        key = run_key("kev", directory, PROJECT_ROOT)
        points = read_log_points(log, PROJECT_ROOT, key, "kev").get(key, [])
        if points:
            point = points[-1]
            metric.update(samples_per_s=point["samples_per_s"], speed_scope=point["speed_scope"],
                          speed_source=point["source"], speed_step=point["step"])
    metric["training_seconds"] = metric["training_seconds"] if metric["training_seconds"] is not None else proc.get("elapsed_s")
    return metric


def fetch_local_server_data():
    global _REPORT_SIGNATURE
    proc = read_local_processes()
    previous = _HISTORY.get(str(PROJECT_ROOT))
    if previous is None or time.monotonic() - previous["built_at"] >= 30:
        history = build_training_history(processes=proc)
    else:
        history = previous["payload"]
    signature = ([(r["key"], r["status"], r["epochs"], r["validation"]) for r in history["runs"]],
                 history["experiment_plans"]["matrix_aggregate"], history["experiment_plans"]["kev_queue"])
    disk = shutil.disk_usage(PROJECT_ROOT)
    queue = read_json(PROJECT_ROOT / "our-project/results/training/kev/candidate_queue.json", [])
    kev = _live_family("kev", proc, history)
    kev["candidates"] = [{k: c.get(k) for k in ("candidate_id", "candidate_kind", "status", "training_status", "evaluation_status", "failure_reason", "pending_reason", "configuration_status", "checkpoint_path", "selection", "retention")} for c in queue]
    kev["completed_candidates"] = sum(c.get("status") == "COMPLETED" and c.get("evaluation_status") == "EVALUATED" for c in queue)
    current = next((c for c in queue if c.get("candidate_id") == kev.get("run_id")), {})
    if current:
        kev.update(live_kev_validation(PROJECT_ROOT / current["checkpoint_path"], current),
                   queue_status=current.get("status"), failure_reason=current.get("failure_reason"))
    live = {"collected_at_iso": now_iso(), "server_connected": True,
            "connection_status": "CONNECTED", "gpu": read_local_gpu_status(), "process": proc,
            "disk": {"total_bytes": disk.total, "used_bytes": disk.used, "free_bytes": disk.free},
            "laya": _live_family("laya", proc, history), "kev": kev,
            "history": {"index": "shards/training_history.json", "revision": history["revision"]}}
    if signature != _REPORT_SIGNATURE:
        write_training_research_report(history, live=live)
        _REPORT_SIGNATURE = signature
    report = read_json(PROJECT_ROOT / "our-project/results/training/training_research.json", {})
    plans = read_json(OUR_PROJECT_DASHBOARD_DIR / history["experiment_plans"]["index"], {})
    live["training_eta"] = training_eta(history, plans, live, report.get("plans", []))
    return live


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
    parser.add_argument("--research-report", action="store_true")
    args = parser.parse_args()
    if args.research_report:
        print(json.dumps(write_training_research_report(build_training_history(processes=read_local_processes()))))
        return
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
