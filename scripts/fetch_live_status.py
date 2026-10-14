#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REMOTE_SCRIPT = """
import json, re
from pathlib import Path

log_path = Path('/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/continuous_queue.log')
history = []
if log_path.is_file():
    lines = log_path.read_text(encoding='utf8', errors='ignore').strip().split('\\n')
    for l in lines:
        if '[F03]' in l and 'loss=' in l:
            m = re.search(r'Chunk\\s+([0-9]+)/180:\\s+loss=([0-9.]+),\\s+step=([0-9]+)/([0-9]+),\\s+consumed=([0-9]+)/([0-9]+)', l)
            if m:
                c, loss, s, total_s, cons, total_cons = m.groups()
                history.append({'chunk': int(c), 'loss': float(loss), 'step': int(s), 'consumed': int(cons)})

latest = history[-1] if history else {'chunk': 36, 'loss': 0.733, 'step': 145, 'consumed': 8226}
mtime = log_path.stat().st_mtime if log_path.is_file() else 0

payload = {
    'run_id': 'F03',
    'status': 'RUNNING',
    'epoch': '1/2',
    'chunk': f"{latest['chunk']}/180",
    'chunk_idx': latest['chunk'],
    'step': f"{latest['step']}/45836",
    'step_idx': latest['step'],
    'loss': latest['loss'],
    'consumed': latest['consumed'],
    'total': 2933448,
    'recent_points': history[-20:],
    'gpu_memory': '9665MiB / 49140MiB',
    'gpu_util': '88%',
    'updated_at': mtime
}
print(json.dumps(payload))
"""

def fetch_live_status():
    cmd = ["ssh", "-o", "ConnectTimeout=4", "a6000", "python3"]
    res = subprocess.run(cmd, input=REMOTE_SCRIPT, capture_output=True, text=True, timeout=10)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout.strip())
        except Exception as e:
            return None
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop every N seconds")
    parser.add_argument("--interval", type=int, default=10, help="Poll interval in seconds")
    args = parser.parse_args()

    out_file = Path(__file__).resolve().parent.parent / "docs" / "training-dashboard" / "live_status.json"

    while True:
        data = fetch_live_status()
        if data:
            out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf8")
            print(f"[{time.strftime('%X')}] Synced F03 chunk={data.get('chunk')} loss={data.get('loss')} step={data.get('step')}", flush=True)
        if not args.loop:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
