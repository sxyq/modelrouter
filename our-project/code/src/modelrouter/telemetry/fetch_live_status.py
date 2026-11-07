"""Canonical ModelRouter live-status publisher and command-line entry."""
from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    _SRC_ROOT = Path(__file__).resolve().parents[2]
    if str(_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(_SRC_ROOT))

from modelrouter.telemetry import common as _common
from modelrouter.telemetry import history as _history
from modelrouter.telemetry import resources as _resources
from modelrouter.telemetry.history import (
    _checkpoint, _new_log_state, _validation, _validation_identity, build_training_history as _build_training_history,
    read_log_points, training_context,
)
from modelrouter.telemetry.reports import training_eta, write_training_research_report

PROJECT_ROOT = _common.PROJECT_ROOT
OUR_PROJECT_DASHBOARD_DIR = PROJECT_ROOT / "our-project/dashboard"
OLD_CORE_IDS = _common.OLD_CORE_IDS
_JSON_CACHE = _common._JSON_CACHE
_LOG_CACHE = _common._LOG_CACHE
_PROGRESS = {}
_HISTORY = _common._HISTORY
_VAL_CACHE = {}
_REPORT_SIGNATURE = None
atomic_json = _common.atomic_json
age_seconds = _common.age_seconds
finite_values = _common.finite_values
kev_cursor = _common.kev_cursor
now_iso = _common.now_iso
public_training_record = _common.public_training_record
read_json = _common.read_json
relative = _common.relative
run_key = _common.run_key
logger = logging.getLogger("fetch_live_status")


def build_training_history(project_root=PROJECT_ROOT, dashboard_dir=None, processes=None):
    _common._JSON_CACHE = _JSON_CACHE
    _common._HISTORY = _HISTORY
    _history._HISTORY = _HISTORY
    _history._LOG_CACHE = _LOG_CACHE
    return _build_training_history(project_root, dashboard_dir, processes)


def read_local_processes():
    return _resources.read_local_processes()


def read_local_gpu_status():
    return _resources.read_local_gpu_status()


def live_kev_validation(directory, candidate):
    return _resources.live_kev_validation(directory, candidate, _VAL_CACHE, age_seconds)


def _live_family(family, processes, history):
    _history._LOG_CACHE = _LOG_CACHE
    return _resources.live_family(family, processes, history, PROJECT_ROOT, _PROGRESS, age_seconds)


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
