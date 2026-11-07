"""Current process, GPU, validation, and training status."""
from __future__ import annotations

import json
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from modelrouter.telemetry.common import kev_cursor, read_json, relative, run_key
from modelrouter.telemetry.history import read_log_points

def live_kev_validation(directory, candidate, cache, age):
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
    data = cache.get(str(data_path))
    if not data or data["identity"] != identity:
        records = questions = 0
        with data_path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    record = json.loads(line)
                    records += 1
                    questions += len(record["questions"])
        data = {"identity": identity, "records": records, "questions": questions}
        cache[str(data_path)] = data
    predictions = Path(result["report_path"]).parent / "predictions.jsonl"
    progress = cache.setdefault(str(predictions), {"offset": 0, "records": 0, "questions": 0})
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
    fields["evaluation_seconds"] = age(started_at)
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


def live_family(family, processes, history, project_root, progress, age):
    proc = processes.get(family, {})
    metric = {"family": family, "status": "IDLE", "is_training": bool(proc.get("train_pid")),
              "process_pid": proc.get("train_pid"), "elapsed_s": proc.get("elapsed_s"),
              **{k: None for k in ("run_id", "epoch", "chunk", "step", "loss", "total_steps", "total_chunks",
                                   "consumed_records", "optimizer_updates", "last_progress_at", "last_progress_age_s")}}
    if not proc:
        recent = [r for r in history["runs"] if r["family"] == family and r.get("training_kind") == "FORMAL_LORA"
                  and r.get("training_status") == "COMPLETED"]
        if recent:
            row = max(recent, key=lambda r: (project_root / r["root"] / "training_metrics.json").stat().st_mtime)
            terminal = read_json(project_root / row["root"] / "training_metrics.json", {})
            cursor = read_json(kev_cursor(project_root / row["root"]), {})
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
                              speed_source=relative(project_root / row["root"] / "training_metrics.json", project_root),
                              speed_step=terminal.get("optimizer_steps"))
        return metric
    if family == "laya":
        directory = project_root / proc["out_root"] / proc["run_id"]
    else:
        directory = project_root / proc["out"]
    row = next((r for r in history["runs"] if r["root"] == relative(directory, project_root)), {})
    if family == "kev" and not row:
        candidate = next((c for c in read_json(project_root / "our-project/results/training/kev/candidate_queue.json", [])
                          if c.get("checkpoint_path") == relative(directory, project_root)), {})
        row = {"run_id": candidate.get("candidate_id"), "planned_epochs": int(candidate["epochs"]) if candidate.get("epochs") else None,
               "protocol": "KEV_FORMAL_LORA"}
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
                  last_progress_age_s=age(timestamp), protocol=row.get("protocol"))
    terminal = read_json(directory / "training_metrics.json", {}) if family == "kev" else {}
    metric["training_seconds"] = terminal.get("wall_seconds")
    if not timestamp:
        metric["status"] = "PROGRESS_UNAVAILABLE"
    if family == "kev":
        metric["loss_step"] = cursor.get("loss_step", step)
        metric["consumed_records"] = None
        metric["consumed_scope"] = "Cursor count is step × batch × accum, not an upstream observed records_seen count"
    identity = (metric["run_id"], step)
    last = progress.get(family)
    if last is None or last["identity"] != identity:
        rate = None
        if last and last["identity"][0] == metric["run_id"] and timestamp and last.get("timestamp"):
            interval = age(last["timestamp"]) - age(timestamp)
            before, after = last.get("consumed_records"), metric["consumed_records"]
            if interval > 0 and before is not None and after is not None and after > before:
                rate = (after - before) / interval
        progress[family] = {"identity": identity, "advanced_at": time.monotonic(),
                             "timestamp": timestamp, "consumed_records": metric["consumed_records"],
                             "samples_per_s": rate}
    elif time.monotonic() - last["advanced_at"] > 300:
        metric["status"] = "STALLED"
    if metric["last_progress_age_s"] is not None and metric["last_progress_age_s"] > 300:
        metric["status"] = "STALE" if metric["status"] != "STALLED" else "STALLED"
    metric["samples_per_s"] = progress[family].get("samples_per_s")
    if family == "kev":
        log = directory / "train.log"
        if not log.is_file():
            log = directory.parent / "train.log"
        key = run_key("kev", directory, project_root)
        points = read_log_points(log, project_root, key, "kev").get(key, [])
        if points:
            point = points[-1]
            metric.update(samples_per_s=point["samples_per_s"], speed_scope=point["speed_scope"],
                          speed_source=point["source"], speed_step=point["step"])
    metric["training_seconds"] = metric["training_seconds"] if metric["training_seconds"] is not None else proc.get("elapsed_s")
    return metric
