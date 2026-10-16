#!/usr/bin/env python3
"""
One-shot unattended safe handover script:
Waits for F05 (PID 3989607) to naturally complete its 2 epochs and validation,
verifies run.json integrity, terminates the frozen old controller (PID 2881128),
and launches the single official queue controller to backfill F03 and continue the 38-run campaign.
Self-terminates immediately after verifying F03 launch.
"""
import sys
import os
import time
import json
import signal
import subprocess
from pathlib import Path
from datetime import datetime

F05_PID = 3989607
OLD_CONTROLLER_PIDS = [2881128, 2881127]
PROJECT_ROOT = Path("/home/syy/路由")
RUN_ROOT = PROJECT_ROOT / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
F05_DIR = RUN_ROOT / "F05"
F05_RUN_JSON = F05_DIR / "run.json"
F05_CURSOR = F05_DIR / "cursor.json"
QUEUE_STATE = RUN_ROOT / "queue_state.json"
LOG_PATH = RUN_ROOT / "handover_execution.log"
QUEUE_LOG = RUN_ROOT / "continuous_queue.log"
PYTHON_BIN = PROJECT_ROOT / ".venv/bin/python"
MANIFEST_PATH = RUN_ROOT / "full_coverage_manifest.json"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def is_pid_alive(pid):
    """Check if process exists and is not a zombie."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    
    # Check if it's in zombie state
    try:
        status_file = Path(f"/proc/{pid}/status")
        if status_file.exists():
            content = status_file.read_text()
            for line in content.splitlines():
                if line.startswith("State:"):
                    if "Z (zombie)" in line:
                        return False
                    return True
    except Exception:
        pass
    return True

def get_process_list(name_filter):
    try:
        res = subprocess.run(["ps", "-eo", "pid,stat,cmd"], capture_output=True, text=True, check=True)
        lines = []
        for l in res.stdout.splitlines():
            if name_filter in l and "grep" not in l:
                lines.append(l.strip())
        return lines
    except Exception:
        return []

def main():
    log("=== ONESHOT HANDOVER AGENT INITIALIZED ===")
    log(f"Target F05 PID: {F05_PID}")
    log(f"Target Frozen Controller PIDs: {OLD_CONTROLLER_PIDS}")
    log(f"Project Root: {PROJECT_ROOT}")
    log(f"Run Root: {RUN_ROOT}")

    # Step 1: Wait for F05 to complete
    log("Phase 1: Monitoring F05 active training process...")
    f05_running = True
    check_interval = 30
    last_chunk_reported = -1

    while f05_running:
        alive = is_pid_alive(F05_PID)
        
        # Log cursor progress periodically
        if F05_CURSOR.exists():
            try:
                c_data = json.loads(F05_CURSOR.read_text())
                c_idx = c_data.get("chunk_idx", -1)
                c_epoch = c_data.get("epoch", 0)
                if c_idx != last_chunk_reported:
                    last_chunk_reported = c_idx
                    loss = c_data.get("latest_chunk_loss", 0.0)
                    step = c_data.get("step_count", 0)
                    log(f"F05 Progress: Epoch {c_epoch + 1}/2 Chunk {c_idx + 1}/182 | Step {step} | Loss {loss:.4f} | Process alive={alive}")
            except Exception:
                pass

        if not alive:
            log(f"F05 PID {F05_PID} has exited. Waiting 15s for file flush and disk I/O...")
            time.sleep(15)
            # Recheck to be completely sure process has settled
            if not is_pid_alive(F05_PID):
                f05_running = False
                log("F05 process termination confirmed.")
            else:
                log(f"Warning: PID {F05_PID} appeared again or is settling.")
        else:
            time.sleep(check_interval)

    # Step 2: Verify F05 completion and artifact integrity
    log("Phase 2: Verifying F05 disk artifacts and completion status...")
    if not F05_RUN_JSON.exists():
        log(f"CRITICAL ERROR: {F05_RUN_JSON} does not exist! Aborting handover.")
        sys.exit(1)

    try:
        run_data = json.loads(F05_RUN_JSON.read_text())
    except Exception as e:
        log(f"CRITICAL ERROR: Failed to parse {F05_RUN_JSON}: {e}. Aborting handover.")
        sys.exit(1)

    status = run_data.get("status")
    log(f"F05 run.json status: '{status}'")
    if status != "completed":
        log(f"CRITICAL ERROR: F05 status is '{status}' (expected 'completed'). Aborting handover.")
        sys.exit(1)

    epoch_metrics_path = F05_DIR / "epoch_metrics.json"
    if not epoch_metrics_path.exists():
        log(f"WARNING: {epoch_metrics_path} does not exist, but run.json is completed.")
    else:
        log(f"F05 epoch_metrics.json verified present.")

    # Step 3: Clean up frozen old controller
    log("Phase 3: Safely terminating frozen old controller processes...")
    for pid in OLD_CONTROLLER_PIDS:
        if is_pid_alive(pid):
            log(f"Sending SIGKILL to old process PID {pid}...")
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception as e:
                log(f"Notice when killing PID {pid}: {e}")
        else:
            log(f"Old process PID {pid} is already terminated.")

    time.sleep(5)
    for pid in OLD_CONTROLLER_PIDS:
        if is_pid_alive(pid):
            log(f"CRITICAL ERROR: Old process PID {pid} could not be killed! Aborting.")
            sys.exit(1)
    log("Old controller processes cleanly removed.")

    # Verify no rogue queue controller is running
    controllers = get_process_list("run_full_graded_queue.py")
    if controllers:
        log(f"CRITICAL ERROR: Unexpected running controller detected: {controllers}. Aborting.")
        sys.exit(1)

    # Step 4: Ensure F03 is top candidate in queue
    log("Phase 4: Verifying queue reconciliation for F03...")
    reconcile_cmd = [
        str(PYTHON_BIN),
        str(PROJECT_ROOT / "router_data/run_full_graded_queue.py"),
        "--mode", "continuous_full_coverage",
        "--chunk-size", "8192",
        "--epochs", "2",
        "--out-root", str(RUN_ROOT),
        "--manifest", str(MANIFEST_PATH),
        "--dry-reconcile"
    ]
    res = subprocess.run(reconcile_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    if res.returncode != 0:
        log(f"CRITICAL ERROR: Dry-reconcile failed: {res.stderr}. Aborting.")
        sys.exit(1)

    try:
        rec_data = json.loads(res.stdout)
        next_queue = rec_data.get("next_queue", [])
        if not next_queue:
            log("CRITICAL ERROR: next_queue is empty! Aborting.")
            sys.exit(1)
        next_run_id = next_queue[0].get("run_id")
        log(f"Verified next_queue[0] run_id: '{next_run_id}'")
        if next_run_id != "F03":
            log(f"CRITICAL ERROR: Expected next run to be 'F03', but found '{next_run_id}'. Aborting.")
            sys.exit(1)
    except Exception as e:
        log(f"CRITICAL ERROR: Failed to parse reconcile output: {e}. Aborting.")
        sys.exit(1)

    # Step 5: Launch single official continuous queue controller
    log("Phase 5: Launching single official continuous queue controller...")
    launch_cmd = (
        f"cd {PROJECT_ROOT} && nohup {PYTHON_BIN} router_data/run_full_graded_queue.py "
        f"--mode continuous_full_coverage "
        f"--chunk-size 8192 "
        f"--epochs 2 "
        f"--out-root {RUN_ROOT} "
        f"--manifest {MANIFEST_PATH} "
        f">> {QUEUE_LOG} 2>&1 & echo LAUNCHED_PID=$!"
    )
    res = subprocess.run(launch_cmd, shell=True, capture_output=True, text=True, executable="/bin/bash")
    log(f"Launch output: {res.stdout.strip()}")

    # Step 6: Verify F03 has started
    log("Phase 6: Verifying F03 GPU execution and initial cursor...")
    f03_started = False
    for attempt in range(24):  # wait up to 120s
        time.sleep(5)
        f03_procs = get_process_list("laya_batch_train.py --full-coverage-run F03")
        f03_cursor = RUN_ROOT / "F03/cursor.json"
        
        if f03_procs or f03_cursor.exists():
            log(f"SUCCESS: F03 training process confirmed active!")
            if f03_procs:
                log(f"F03 Process: {f03_procs[0]}")
            if f03_cursor.exists():
                try:
                    c = json.loads(f03_cursor.read_text())
                    log(f"F03 Cursor confirmed initialized: chunk={c.get('chunk_idx')}, step={c.get('step_count')}")
                except Exception:
                    pass
            f03_started = True
            break
        log(f"Waiting for F03 process initialization... (attempt {attempt + 1}/24)")

    if not f03_started:
        log("WARNING: F03 process not detected within 120s. Check continuous_queue.log.")
    else:
        log("=== HANDOVER COMPLETED SUCCESSFULLY ===")
        log("Official continuous queue is now actively training F03 and will proceed to F06, F07... autonomously.")

if __name__ == "__main__":
    main()
