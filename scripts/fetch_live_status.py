#!/usr/bin/env python3
"""Synchronize true remote server training state to local live_status.json with full multi-run history."""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REMOTE_SCRIPT = """
import json, re, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

# 1. GPU metrics
gpu_used, gpu_total, gpu_util = '0', '0', '0'
try:
    res = subprocess.run(
        ['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=3
    )
    if res.returncode == 0 and res.stdout.strip():
        parts = [p.strip() for p in res.stdout.strip().split(',')]
        if len(parts) >= 3:
            gpu_used, gpu_total, gpu_util = parts[0], parts[1], parts[2]
except Exception:
    pass

# 2. Check process live status
train_pid, daemon_pid = None, None
try:
    ps_res = subprocess.run(['ps', '-eo', 'pid,cmd'], capture_output=True, text=True, timeout=3)
    if ps_res.returncode == 0:
        for line in ps_res.stdout.splitlines():
            if 'laya_batch_train.py' in line and 'grep' not in line:
                train_pid = line.strip().split()[0]
            if 'run_full_graded_queue.py' in line and 'grep' not in line:
                daemon_pid = line.strip().split()[0]
except Exception:
    pass

is_alive = train_pid is not None
is_daemon_alive = daemon_pid is not None

# 3. Read queue_state.json
p0_root = Path('/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012')
q_path = p0_root / 'queue_state.json'
q_data = {}
if q_path.is_file():
    try:
        q_data = json.loads(q_path.read_text(encoding='utf8'))
    except Exception:
        pass

current_run = q_data.get('current_run') or ('F04' if is_alive else None)

# 4. Read Cursor for current_run
c_data = {}
if current_run:
    c_path = p0_root / current_run / 'cursor.json'
    if c_path.is_file():
        try:
            c_data = json.loads(c_path.read_text(encoding='utf8'))
        except Exception:
            pass

# 5. Metadata & Validation scores from run directories
runs_info = {}
for p in p0_root.iterdir():
    if not p.is_dir():
        continue
    rj = p / 'run.json'
    if rj.is_file():
        try:
            d = json.loads(rj.read_text(encoding='utf8'))
            runs_info[p.name] = {
                'run_id': p.name,
                'started_at': d.get('started_at'),
                'completed_at': d.get('completed_at'),
                'status': d.get('status'),
                'layers': d.get('layers', []),
                'supervision_classes': d.get('supervision_classes', []),
                'total_eligible_items': d.get('total_eligible_items', 0),
                'best_s1_acc': None,
                'best_val_loss': None
            }
        except Exception:
            pass
        em = p / 'epoch_metrics.json'
        if em.is_file():
            try:
                emd = json.loads(em.read_text(encoding='utf8'))
                if isinstance(emd, list) and emd:
                    best = emd[-1]
                    s1 = (best.get('validation', {}).get('S1') or {})
                    runs_info[p.name]['best_s1_acc'] = s1.get('accuracy')
                    runs_info[p.name]['best_val_loss'] = s1.get('loss')
            except Exception:
                pass

# 6. Read continuous_queue.log
log_path = p0_root / 'continuous_queue.log'
log_mtime = 0
run_pts = {}
chronological_runs = []
timeline_points = []
if log_path.is_file():
    try:
        log_mtime = log_path.stat().st_mtime
        lines = log_path.read_text(encoding='utf8', errors='ignore').splitlines()
        for l in lines:
            if 'Chunk' in l and 'loss=' in l:
                m = re.search(r'^\[([A-Za-z0-9_]+)\]\s+Epoch\s+([0-9]+)/([0-9]+)\s+Chunk\s+([0-9]+)/([0-9]+):\s+loss=([0-9.]+),\s+step=([0-9]+)/([0-9]+),\s+consumed=([0-9]+)/([0-9]+)', l)
                if m:
                    r, ep, ep_tot, c, c_tot, loss_val, s, s_tot, cons, cons_tot = m.groups()
                    if r == 'F03' and int(s_tot) == 45836:
                        r = 'F03_LEGACY_MINFACTOR'
                    pt = {
                        'run_id': r,
                        'epoch': int(ep),
                        'total_epochs': int(ep_tot),
                        'chunk': int(c),
                        'total_chunks': int(c_tot),
                        'loss': round(float(loss_val), 4),
                        'step': int(s),
                        'total_steps': int(s_tot),
                        'consumed': int(cons),
                        'total_consumed': int(cons_tot)
                    }
                    if r not in run_pts:
                        run_pts[r] = []
                        chronological_runs.append(r)
                    run_pts[r].append(pt)
                    timeline_points.append(pt)
    except Exception:
        pass

# 7. Package Processed Runs
processed_runs = {}
now_sec = time.time()
windows = {
    'all': [],
    'last_48h': [],
    'last_24h': [],
    'last_12h': [],
    'last_6h': [],
    'full_coverage': [],
    'ablation': [],
    'baseline': [],
    'archived': []
}

for r in chronological_runs:
    pts = run_pts[r]
    meta = runs_info.get(r, {})
    losses = [p['loss'] for p in pts]
    l_start = losses[0]
    l_min = min(losses)
    l_end = losses[-1]
    reduct = round(((l_start - l_end) / l_start) * 100, 2) if l_start > 0 else 0

    cat = 'baseline'
    if r.startswith('ALGN'):
        cat = 'ablation'
    elif r in ['F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07']:
        cat = 'full_coverage'
    elif r == 'F03_LEGACY_MINFACTOR':
        cat = 'archived'

    # Sample points for multi-run overlay if dense (keep full for current_run)
    sampled_pts = pts
    if len(pts) > 120 and r != current_run:
        step_stride = len(pts) / 120.0
        sampled_pts = [pts[int(i * step_stride)] for i in range(120)]
        if pts[-1] not in sampled_pts:
            sampled_pts.append(pts[-1])

    # Time window detection
    started_at = meta.get('started_at')
    dt_hours = None
    if started_at:
        try:
            t_run = datetime.fromisoformat(started_at.replace('Z', '+00:00')).timestamp()
            dt_hours = round(max(0.0, (now_sec - t_run) / 3600), 2)
        except Exception:
            pass
    elif r == current_run:
        dt_hours = 0.1

    is_6h = (dt_hours is not None and dt_hours <= 6.0) or (r == current_run)
    is_12h = (dt_hours is not None and dt_hours <= 12.0) or (r == current_run)
    is_24h = (dt_hours is not None and dt_hours <= 24.0) or (r == current_run)
    is_48h = (dt_hours is not None and dt_hours <= 48.0) or (r == current_run)

    windows['all'].append(r)
    if is_48h: windows['last_48h'].append(r)
    if is_24h: windows['last_24h'].append(r)
    if is_12h: windows['last_12h'].append(r)
    if is_6h: windows['last_6h'].append(r)
    if cat == 'full_coverage': windows['full_coverage'].append(r)
    if cat == 'ablation': windows['ablation'].append(r)
    if cat == 'baseline': windows['baseline'].append(r)

    processed_runs[r] = {
        'run_id': r,
        'category': cat,
        'started_at': started_at,
        'completed_at': meta.get('completed_at'),
        'hours_ago': dt_hours,
        'status': 'running' if r == current_run and is_alive else (meta.get('status') or 'completed'),
        'layers': meta.get('layers', []),
        'supervision_classes': meta.get('supervision_classes', []),
        'total_chunks': pts[-1]['total_chunks'],
        'total_steps': pts[-1]['total_steps'],
        'total_consumed': pts[-1]['total_consumed'],
        'best_s1_acc': meta.get('best_s1_acc'),
        'best_val_loss': meta.get('best_val_loss'),
        'raw_points_count': len(pts),
        'stats': {
            'start_loss': l_start,
            'min_loss': l_min,
            'end_loss': l_end,
            'reduction_pct': reduct,
            'current_step': pts[-1]['step'],
            'current_chunk': pts[-1]['chunk'],
            'total_steps': pts[-1]['total_steps'],
            'total_chunks': pts[-1]['total_chunks'],
            'consumed': pts[-1]['consumed'],
            'total_consumed': pts[-1]['total_consumed']
        },
        'points': sampled_pts
    }

# 8. Sample timeline_points for sequential view if very large
timeline_sampled = timeline_points
if len(timeline_points) > 350:
    stride = len(timeline_points) / 350.0
    timeline_sampled = [timeline_points[int(i * stride)] for i in range(350)]
    if timeline_points[-1] not in timeline_sampled:
        timeline_sampled.append(timeline_points[-1])

# 9. Synthesize payload
epoch_str = f'Epoch {c_data.get(\"epoch\", 0) + 1}/2' if c_data else 'N/A'
chunk_str = f'{c_data.get(\"chunk_idx\", \"N/A\")}/{c_data.get(\"total_chunks\", \"N/A\")}' if c_data else 'N/A'
step_str = f'{c_data.get(\"step_count\", \"N/A\")}/{c_data.get(\"total_updates\", \"N/A\")}' if c_data else 'N/A'
loss_val = c_data.get('latest_chunk_loss')
if loss_val is not None:
    loss_val = round(float(loss_val), 4)

payload = {
    'collected_at_unix': now_sec,
    'collected_at_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now_sec)),
    'process_alive': is_alive,
    'daemon_alive': is_daemon_alive,
    'train_pid': train_pid,
    'daemon_pid': daemon_pid,
    'current_run': current_run,
    'status': 'RUNNING' if is_alive else (q_data.get('queue_status') or 'STOPPED'),
    'epoch': epoch_str,
    'chunk': chunk_str,
    'chunk_idx': c_data.get('chunk_idx'),
    'total_chunks': c_data.get('total_chunks'),
    'step': step_str,
    'step_idx': c_data.get('step_count'),
    'total_steps': c_data.get('total_updates'),
    'loss': loss_val,
    'consumed': c_data.get('consumed_items'),
    'consumed_units': c_data.get('consumed_units'),
    'cursor_updated_at': c_data.get('updated_at'),
    'gpu_memory': f'{gpu_used}MiB / {gpu_total}MiB',
    'gpu_util': f'{gpu_util}%',
    'recent_points': timeline_points[-30:] if timeline_points else [],
    'chronological_runs': chronological_runs,
    'history_runs': processed_runs,
    'windows': windows,
    'timeline_points': timeline_sampled,
    'total_all_chunks': len(timeline_points),
    'reconciliation': q_data.get('reconciliation', {}),
    'log_mtime': log_mtime
}
print(json.dumps(payload))
"""

def fetch_live_status():
    cmd = ["ssh", "-o", "ConnectTimeout=4", "a6000", "python3"]
    res = subprocess.run(cmd, input=REMOTE_SCRIPT, capture_output=True, text=True, timeout=12)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout.strip())
        except Exception as e:
            sys.stderr.write(f"JSON parse error: {e}\n")
            return None
    else:
        sys.stderr.write(f"SSH fetch error: {res.stderr}\n")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run continuous loop")
    parser.add_argument("--interval", type=int, default=10, help="Poll interval in seconds")
    args = parser.parse_args()

    out_file = Path(__file__).resolve().parent.parent / "docs" / "training-dashboard" / "live_status.json"

    while True:
        data = fetch_live_status()
        if data:
            out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf8")
            now_str = datetime.now().strftime("%X")
            cur_run = data.get("current_run")
            chunk = data.get("chunk")
            loss = data.get("loss")
            pid = data.get("train_pid")
            alive = data.get("process_alive")
            all_chunks = data.get("total_all_chunks")
            print(f"[{now_str}] True Live State: run={cur_run} chunk={chunk} loss={loss} pid={pid} alive={alive} total_chunks={all_chunks}", flush=True)
        if not args.loop:
            break
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
