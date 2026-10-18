#!/usr/bin/env python3
"""
run_kev_continuous_train.py - Formal Continuous GPU Training Runner for Kev-4B LoRA/Pointer Head.
Monitors and updates cursor.json for Kev, outputting real metrics to dashboard and ledgers.
"""

import os
import sys
import time
import json
import re
import signal
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/home/syy/路由")
OUT_DIR = PROJECT_ROOT / "runs" / "KEV-V8-HOMOLOGOUS-20261018"
RUN_DIR = OUT_DIR / "formal_run"
LOG_FILE = OUT_DIR / "train.log"
CURSOR_FILE = OUT_DIR / "cursor.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)

CMD = [
    str(PROJECT_ROOT / ".venv" / "bin" / "python"),
    "-u",
    "-m",
    "kev.train",
    "--base", str(PROJECT_ROOT / "models" / "qwen3.5-4b-base"),
    "--init_from", str(PROJECT_ROOT / "models" / "kev-4b-adapter"),
    "--data", str(PROJECT_ROOT / "data" / "kev" / "公开数据" / "train.jsonl"),
    "--out", str(RUN_DIR),
    "--device", "cuda",
    "--dtype", "bf16",
    "--weights_dtype", "bf16",
    "--checkpointing", "1",
    "--batch", "1",
    "--accum", "4",
    "--lr", "2e-5",
    "--epochs", "1",
    "--seed", "42"
]

ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(PROJECT_ROOT / "external" / "kev")

print(f"Launching Kev formal training with command: {' '.join(CMD)}")
print(f"Logging to: {LOG_FILE}")
print(f"Cursor at: {CURSOR_FILE}")

with open(LOG_FILE, "a", encoding="utf-8") as log_f:
    proc = subprocess.Popen(
        CMD,
        cwd=str(PROJECT_ROOT),
        env=ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Write initial cursor
    cursor = {
        "run_id": "KEV-V8-HOMOLOGOUS-20261018",
        "pid": proc.pid,
        "status": "TRAINING",
        "epoch": 0,
        "step": 0,
        "total_steps": 16857,
        "loss": None,
        "kl": None,
        "consumed_records": 0,
        "checkpoints": ["models/kev-4b-adapter/ (init_checkpoint)"],
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(CURSOR_FILE, "w", encoding="utf-8") as cf:
        json.dump(cursor, cf, indent=2)

    # Regex for train step: ep0 step 1/16857 loss 1.234 ...
    step_re = re.compile(r"ep(\d+)\s+step\s+(\d+)/(\d+)\s+loss\s+([0-9.]+)")

    for line in proc.stdout:
        log_f.write(line)
        log_f.flush()

        m = step_re.search(line)
        if m:
            ep = int(m.group(1))
            step = int(m.group(2))
            total_steps = int(m.group(3))
            loss = float(m.group(4))

            cursor.update({
                "epoch": ep,
                "step": step,
                "total_steps": total_steps,
                "loss": loss,
                "consumed_records": step * 4,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
            with open(CURSOR_FILE, "w", encoding="utf-8") as cf:
                json.dump(cursor, cf, indent=2)

    proc.wait()
    cursor["status"] = "COMPLETED" if proc.returncode == 0 else "FAILED"
    cursor["exit_code"] = proc.returncode
    cursor["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(CURSOR_FILE, "w", encoding="utf-8") as cf:
        json.dump(cursor, cf, indent=2)

print(f"Kev training process finished with code {proc.returncode}")
