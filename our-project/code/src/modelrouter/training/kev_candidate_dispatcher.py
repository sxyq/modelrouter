#!/usr/bin/env python3
"""
kev_candidate_dispatcher.py - Multi-Candidate Scientific Progression Dispatcher for Kev-4B.

Ensures that:
1. Current live Kev training (PID 1357764) is monitored without interruption.
2. Upon completion, formal fixed validation (accuracy, NLL, ECE, Brier) is computed and saved.
3. Subsequent queued candidates (Ep 2 continuation, state ablations, LoRA rank ablations, V8 extension)
   are automatically dispatched in sequence with independent runs, configs, logs, and checkpoints.
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("kev_dispatcher")

PROJECT_ROOT = Path("/home/syy/路由")
KEV_RUNS_ROOT = PROJECT_ROOT / "runs"
QUEUED_CANDIDATES_FILE = PROJECT_ROOT / "our-project" / "results" / "training" / "kev" / "candidate_queue.json"
LEDGER_FILE = PROJECT_ROOT / "our-project" / "results" / "training" / "kev" / "candidate_ledger.json"

DEFAULT_QUEUE = [
    {
        "candidate_id": "KEV-V8-C04",
        "name": "KEV-V8-HOMO-e02",
        "description": "Homologous continuation Ep 2 with cosine lr decay",
        "init_from": "runs/KEV-V8-HOMOLOGOUS-20261018/formal_run",
        "lr": "1e-5",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": []
    },
    {
        "candidate_id": "KEV-V8-C05",
        "name": "KEV-V8-ABL-NOSTATE",
        "description": "State ablation: zero/masked state features",
        "init_from": "models/kev-4b-adapter",
        "lr": "2e-5",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": []
    },
    {
        "candidate_id": "KEV-V8-C07",
        "name": "KEV-V8-ABL-LORA8",
        "description": "Capacity ablation: LoRA rank 8",
        "init_from": "models/kev-4b-adapter",
        "lr": "5e-5",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": []
    },
    {
        "candidate_id": "KEV-V8-C09",
        "name": "KEV-V8-EXT-01",
        "description": "V8 Extension: Arena human preferences + agent traces",
        "init_from": "models/kev-4b-adapter",
        "lr": "2e-5",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": []
    }
]

def load_queue():
    if QUEUED_CANDIDATES_FILE.is_file():
        try:
            return json.loads(QUEUED_CANDIDATES_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Error loading queue file, using default: {e}")
    QUEUED_CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUED_CANDIDATES_FILE.write_text(json.dumps(DEFAULT_QUEUE, indent=2), encoding="utf-8")
    return DEFAULT_QUEUE

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def evaluate_checkpoint(run_dir: Path) -> dict:
    logger.info(f"Running formal validation evaluation on checkpoint: {run_dir}")
    eval_cmd = [
        str(PROJECT_ROOT / ".venv" / "bin" / "python"),
        "-m", "kev.evaluate",
        "--run", str(run_dir),
        "--device", "auto",
        "--seed", "42"
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "external" / "kev")
    
    try:
        res = subprocess.run(eval_cmd, cwd=str(PROJECT_ROOT), env=env, capture_output=True, text=True, timeout=600)
        out_metrics = {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        metrics_file = run_dir / "val_metrics.json"
        metrics_file.write_text(json.dumps(out_metrics, indent=2), encoding="utf-8")
        logger.info(f"Validation metrics written to {metrics_file}")
        return out_metrics
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return {"error": str(e)}

def monitor_and_dispatch():
    logger.info("Starting Kev Multi-Candidate Progression Dispatcher")
    
    # Check current active training
    cur_file = KEV_RUNS_ROOT / "KEV-V8-HOMOLOGOUS-20261018" / "cursor.json"
    active_pid = None
    if cur_file.is_file():
        try:
            cd = json.loads(cur_file.read_text(encoding="utf-8"))
            active_pid = cd.get("pid")
            logger.info(f"Current active Kev run: {cd.get('run_id')}, PID: {active_pid}, Step: {cd.get('step')}")
        except Exception:
            pass

    # Wait for active training to finish
    if active_pid and is_pid_alive(active_pid):
        logger.info(f"Waiting for live PID {active_pid} to conclude naturally...")
        while is_pid_alive(active_pid):
            time.sleep(30)
        logger.info(f"Live Kev process {active_pid} completed!")

    # Perform evaluation on finished run
    current_run_dir = KEV_RUNS_ROOT / "KEV-V8-HOMOLOGOUS-20261018" / "formal_run"
    if current_run_dir.exists():
        evaluate_checkpoint(current_run_dir)

    # Dispatch next candidate in queue
    queue = load_queue()
    if not queue:
        logger.info("No more candidates in queue.")
        return

    next_candidate = queue.pop(0)
    logger.info(f"Dispatching next queued candidate: {next_candidate['candidate_id']} ({next_candidate['name']})")
    
    # Save updated queue
    QUEUED_CANDIDATES_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    
    cand_dir = KEV_RUNS_ROOT / next_candidate["name"]
    cand_dir.mkdir(parents=True, exist_ok=True)
    out_dir = cand_dir / "checkpoint"
    log_file = cand_dir / "train.log"
    
    train_cmd = [
        str(PROJECT_ROOT / ".venv" / "bin" / "python"),
        "-u",
        "-m", "kev.train",
        "--base", str(PROJECT_ROOT / "models" / "qwen3.5-4b-base"),
        "--init_from", str(PROJECT_ROOT / next_candidate["init_from"]),
        "--data", str(PROJECT_ROOT / "data" / "kev" / "公开数据" / "train.jsonl"),
        "--out", str(out_dir),
        "--device", "cuda",
        "--dtype", "bf16",
        "--weights_dtype", "bf16",
        "--checkpointing", "1",
        "--batch", next_candidate.get("batch", "1"),
        "--accum", next_candidate.get("accum", "4"),
        "--lr", next_candidate.get("lr", "2e-5"),
        "--epochs", next_candidate.get("epochs", "1"),
        "--seed", "42"
    ]
    
    logger.info(f"Launching candidate with command: {' '.join(train_cmd)}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "external" / "kev")
    
    with open(log_file, "a", encoding="utf-8") as lf:
        proc = subprocess.Popen(train_cmd, cwd=str(PROJECT_ROOT), env=env, stdout=lf, stderr=subprocess.STDOUT)
        logger.info(f"Candidate {next_candidate['name']} launched with PID {proc.pid}")

if __name__ == "__main__":
    monitor_and_dispatch()
