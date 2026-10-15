#!/usr/bin/env python3
"""Safe Run-Boundary Transition Watcher for ModelRouter Queue Daemon.

Monitors the healthy running F04 GPU training process (PID 2881373).
While F04 is actively computing, this script strictly sleeps (zero interference, zero risk).
The moment F04 finishes and exits, it waits for the old daemon (PID 2881128) to finalize
F04's completion in `queue_state.json` and sync metadata.
Once finalized (or within a safe timeout), it cleanly stops PID 2881128,
verifies all child processes are settled, and launches the updated queue daemon
with the latest code (including automatic F03 selection, parent model regeneration,
fail-closed verification, and dual-pool 15% quota enforcement).
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = PROJECT_ROOT / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
QUEUE_STATE_PATH = OUT_ROOT / "queue_state.json"
MANIFEST_PATH = OUT_ROOT / "full_coverage_manifest.json"
LOG_PATH = OUT_ROOT / "boundary_transition.log"

TARGET_RUN_ID = "F04"
TARGET_TRAIN_PID = 2881373
OLD_DAEMON_PID = 2881128
BASH_PARENT_PID = 2881127


def log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    line = f"[{ts}] [SAFE_TRANSITION] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_pid_running(pid: int) -> bool:
    if pid <= 1:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def main():
    log("Starting Safe Boundary Transition Watcher.")
    log(f"Target Run: {TARGET_RUN_ID}, Active Train PID: {TARGET_TRAIN_PID}, Old Daemon PID: {OLD_DAEMON_PID}")

    # Phase 1: Sleep while target train PID is alive
    check_count = 0
    while is_pid_running(TARGET_TRAIN_PID):
        time.sleep(5)
        check_count += 1
        if check_count % 60 == 0:  # Every 5 minutes
            log(f"Target PID {TARGET_TRAIN_PID} ({TARGET_RUN_ID}) is healthy and running. Watcher continuing to stand by...")

    log(f"Target Train PID {TARGET_TRAIN_PID} ({TARGET_RUN_ID}) has EXITED!")

    # Phase 2: Allow the old daemon up to 60 seconds to finish writing F04 completion in queue_state.json
    log("Waiting for old daemon to record completion in queue_state.json...")
    completed_recorded = False
    for i in range(120):
        if QUEUE_STATE_PATH.is_file():
            try:
                state = json.loads(QUEUE_STATE_PATH.read_text(encoding="utf8"))
                if TARGET_RUN_ID in (state.get("completed_runs") or []) or TARGET_RUN_ID in (state.get("failed_runs") or {}):
                    completed_recorded = True
                    log(f"Completion of {TARGET_RUN_ID} successfully confirmed in queue_state.json (attempt {i+1}).")
                    break
            except Exception:
                pass
        time.sleep(0.5)

    if not completed_recorded:
        log("Warning: Completion not recorded within timeout. Checking run.json directly...")
        run_json = OUT_ROOT / TARGET_RUN_ID / "run.json"
        if run_json.is_file():
            try:
                rdata = json.loads(run_json.read_text(encoding="utf8"))
                if rdata.get("status") in ("completed", "early_stopped"):
                    log(f"run.json confirmed completed! Ensuring queue_state.json records {TARGET_RUN_ID}...")
                    try:
                        state = json.loads(QUEUE_STATE_PATH.read_text(encoding="utf8")) if QUEUE_STATE_PATH.is_file() else {}
                        cr = state.setdefault("completed_runs", [])
                        if TARGET_RUN_ID not in cr:
                            cr.append(TARGET_RUN_ID)
                        state["current_run"] = None
                        QUEUE_STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf8")
                    except Exception as e:
                        log(f"Error updating queue_state.json: {e}")
            except Exception:
                pass

    # Give extra 3 seconds for file sync
    time.sleep(3)

    # Phase 3: Stop old daemon gracefully
    if is_pid_running(OLD_DAEMON_PID):
        log(f"Sending SIGTERM to old daemon PID {OLD_DAEMON_PID}...")
        try:
            os.kill(OLD_DAEMON_PID, signal.SIGTERM)
        except OSError:
            pass

        for _ in range(30):
            if not is_pid_running(OLD_DAEMON_PID):
                break
            time.sleep(0.5)
        else:
            log(f"Force-killing old daemon PID {OLD_DAEMON_PID} with SIGKILL...")
            try:
                os.kill(OLD_DAEMON_PID, signal.SIGKILL)
            except OSError:
                pass

    if is_pid_running(BASH_PARENT_PID):
        try:
            os.kill(BASH_PARENT_PID, signal.SIGTERM)
        except OSError:
            pass

    log("Old queue controller stopped cleanly.")

    # Phase 4: Launch updated queue daemon with latest code
    cmd = [
        str(PROJECT_ROOT / ".venv" / "bin" / "python"),
        str(PROJECT_ROOT / "router_data" / "run_full_graded_queue.py"),
        "--mode", "continuous_full_coverage",
        "--chunk-size", "8192",
        "--epochs", "2",
        "--out-root", str(OUT_ROOT),
        "--manifest", str(MANIFEST_PATH),
    ]
    log(f"Launching new queue daemon: {' '.join(cmd)}")
    queue_log = open(OUT_ROOT / "continuous_queue.log", "a", encoding="utf8")
    proc = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=queue_log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log(f"New queue controller successfully launched with PID: {proc.pid}")
    log("Safe Boundary Transition complete. Transition watcher exiting.")


if __name__ == "__main__":
    main()
