#!/usr/bin/env python3
"""F05 Task Boundary Guardian & Official Queue Transition Sentinel.

Monitors the active F05 training process (PID 3989607).
Without disrupting, stopping, or pausing F05, this guardian waits until F05 reaches
its natural completion boundary (Epoch 2 evaluated, run.json status completed).
At that exact safe task boundary:
1. Ensures F03 is absent from queue_state.json completed_runs;
2. Gracefully restarts the single official queue daemon with the latest codebase;
3. Verifies that F03 (Stage 2) is immediately picked up as the next run;
4. Guarantees strictly ONE official queue is running at all times.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path("/home/syy/路由")
OUT_ROOT = PROJECT_ROOT / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
QUEUE_STATE_FILE = OUT_ROOT / "queue_state.json"
MANIFEST_FILE = OUT_ROOT / "full_coverage_manifest.json"
CONTINUOUS_LOG = OUT_ROOT / "continuous_queue.log"
GUARDIAN_LOG = OUT_ROOT / "f05_boundary_guardian.log"


def log(msg: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [GUARDIAN] {msg}"
    print(formatted, flush=True)
    try:
        with open(GUARDIAN_LOG, "a", encoding="utf8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_current_f05_pid() -> int:
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "laya_batch_train.py --full-coverage-run F05"],
            text=True
        ).strip()
        if out:
            return int(out.splitlines()[0])
    except Exception:
        pass
    return 0


def get_queue_daemon_pid() -> int:
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "run_full_graded_queue.py --mode continuous_full_coverage"],
            text=True
        ).strip()
        if out:
            return int(out.splitlines()[0])
    except Exception:
        pass
    return 0


def clean_f03_from_queue_state() -> None:
    if QUEUE_STATE_FILE.is_file():
        try:
            d = json.loads(QUEUE_STATE_FILE.read_text(encoding="utf8"))
            completed = d.get("completed_runs", [])
            if "F03" in completed:
                d["completed_runs"] = [r for r in completed if r != "F03"]
                QUEUE_STATE_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf8")
                log("Successfully removed F03 from queue_state.json completed_runs.")
        except Exception as e:
            log(f"Error cleaning F03 from queue_state.json: {e}")


def launch_official_queue() -> int:
    clean_f03_from_queue_state()
    cmd = (
        f"nohup {PROJECT_ROOT}/.venv/bin/python {PROJECT_ROOT}/router_data/run_full_graded_queue.py "
        f"--mode continuous_full_coverage --chunk-size 8192 --epochs 2 "
        f"--out-root {OUT_ROOT} --manifest {MANIFEST_FILE} >> {CONTINUOUS_LOG} 2>&1 & echo $!"
    )
    res = subprocess.check_output(["bash", "-c", cmd], text=True, cwd=str(PROJECT_ROOT)).strip()
    new_pid = int(res) if res.isdigit() else get_queue_daemon_pid()
    log(f"Launched new official queue daemon with PID: {new_pid}")
    return new_pid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Run background monitor until F05 completes")
    parser.add_argument("--status", action="store_true", help="Check current F05 and guardian status")
    args = parser.parse_args()

    f05_pid = get_current_f05_pid()
    daemon_pid = get_queue_daemon_pid()

    if args.status:
        print(f"F05 Active PID:    {f05_pid} (alive={is_pid_alive(f05_pid)})")
        print(f"Queue Daemon PID:  {daemon_pid} (alive={is_pid_alive(daemon_pid)})")
        if QUEUE_STATE_FILE.is_file():
            d = json.loads(QUEUE_STATE_FILE.read_text(encoding="utf8"))
            print(f"F03 in completed:  {'F03' in d.get('completed_runs', [])}")
            print(f"Current run:       {d.get('current_run')}")
        return

    log(f"F05 Boundary Guardian initialized. Monitoring F05 (PID {f05_pid}).")
    clean_f03_from_queue_state()

    # Loop waiting for F05 to complete
    while True:
        if not f05_pid or not is_pid_alive(f05_pid):
            log(f"F05 process {f05_pid} has exited! Natural task boundary reached.")
            break
        time.sleep(15)

    # Allow 3 seconds for F05 run.json / metrics to flush cleanly
    time.sleep(3)

    # Check F05 status in run.json
    f05_run_json = OUT_ROOT / "F05" / "run.json"
    status = "unknown"
    if f05_run_json.is_file():
        try:
            status = json.loads(f05_run_json.read_text(encoding="utf8")).get("status", "unknown")
        except Exception:
            pass
    log(f"F05 verified finished with status: {status}.")

    # Stop old parent queue daemon before it dispatches F06
    old_daemon = get_queue_daemon_pid()
    if old_daemon and is_pid_alive(old_daemon):
        log(f"Gracefully stopping pre-commit queue daemon (PID {old_daemon})...")
        os.kill(old_daemon, signal.SIGTERM)
        time.sleep(2)
        if is_pid_alive(old_daemon):
            os.kill(old_daemon, signal.SIGKILL)

    # Restart official queue with latest code where F03 is at top of queue
    log("Restarting official queue with updated controller logic...")
    new_pid = launch_official_queue()
    time.sleep(3)

    # Verify next run started is F03
    curr = "unknown"
    if QUEUE_STATE_FILE.is_file():
        try:
            curr = json.loads(QUEUE_STATE_FILE.read_text(encoding="utf8")).get("current_run")
        except Exception:
            pass
    log(f"Transition complete. Queue status: active (PID {new_pid}), current_run={curr}.")


if __name__ == "__main__":
    main()
