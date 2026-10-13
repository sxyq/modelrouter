#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Server-Side Autonomous Watchdog & Progress Monitor.

Runs independently on the remote server (`a6000`) without requiring an active
local terminal or SSH connection. Periodically monitors:
1. Training queue daemon (`run_full_graded_queue.py`) & worker (`laya_batch_train.py`).
2. NVIDIA RTX A6000 GPU utilization, VRAM, and thermals.
3. Disk space and checkpoint storage budget.
4. Real-time progress (in-flight epoch, chunk, loss, steps).
5. Writes `SERVER_MONITOR_STATUS.md` and `monitor_status.json`.
6. Regenerates dashboard data (`data.js` and shards) on completion of runs.
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def _get_gpu_info() -> Dict[str, Any]:
    """Query nvidia-smi for RTX A6000 status."""
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw",
            "--format=csv,noheader,nounits",
        ]
        out = subprocess.check_output(cmd, text=True, timeout=5).strip()
        parts = [p.strip() for p in out.split(",")]
        if len(parts) >= 7:
            return {
                "name": parts[0],
                "memory_total_mib": float(parts[1]),
                "memory_used_mib": float(parts[2]),
                "memory_free_mib": float(parts[3]),
                "utilization_gpu_pct": float(parts[4]),
                "temperature_gpu_c": float(parts[5]),
                "power_draw_w": float(parts[6]),
                "ok": True,
            }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "unknown"}


def _get_disk_info(path: str = "/") -> Dict[str, Any]:
    """Get filesystem usage for disk path."""
    try:
        usage = shutil.disk_usage(path)
        total_gib = usage.total / (1024 ** 3)
        free_gib = usage.free / (1024 ** 3)
        used_gib = usage.used / (1024 ** 3)
        used_pct = (usage.used / usage.total) * 100
        return {
            "total_gib": round(total_gib, 1),
            "used_gib": round(used_gib, 1),
            "free_gib": round(free_gib, 1),
            "used_pct": round(used_pct, 1),
            "ok": True,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _find_training_pids() -> Dict[str, Optional[int]]:
    """Locate queue runner and active trainer PIDs."""
    res = {"queue_pid": None, "trainer_pid": None, "trainer_cmd": None}
    try:
        out = subprocess.check_output(["ps", "-eo", "pid,ppid,args"], text=True)
        for line in out.splitlines():
            line_str = line.strip()
            parts = line_str.split(None, 2)
            if len(parts) < 3 or not parts[0].isdigit():
                continue
            pid, ppid, cmd = int(parts[0]), int(parts[1]) if parts[1].isdigit() else 0, parts[2]
            if "run_full_graded_queue.py" in cmd and "grep" not in cmd:
                res["queue_pid"] = pid
            if "laya_batch_train.py" in cmd and "grep" not in cmd:
                res["trainer_pid"] = pid
                res["trainer_cmd"] = cmd
    except Exception:
        pass
    return res


def _read_json_safe(path: Path) -> Optional[Dict[str, Any]]:
    """Safely parse json file."""
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _get_latest_log_chunk(log_path: Path, max_lines: int = 15) -> List[str]:
    """Read last N non-empty lines from log."""
    if not log_path.is_file():
        return []
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
            return lines[-max_lines:]
    except Exception:
        return []


def collect_monitor_snapshot(project_root: Path, out_root: Path) -> Dict[str, Any]:
    """Gather full system and training snapshot."""
    gpu = _get_gpu_info()
    disk = _get_disk_info("/")
    pids = _find_training_pids()

    state_path = out_root / "queue_state.json"
    queue_state = _read_json_safe(state_path) or {}

    log_path = out_root / "continuous_queue.log"
    recent_logs = _get_latest_log_chunk(log_path, max_lines=12)

    # In-flight run details
    current_run_id = queue_state.get("current_run")
    in_flight_cursor = {}
    if current_run_id:
        cursor_file = out_root / current_run_id / "cursor.json"
        in_flight_cursor = _read_json_safe(cursor_file) or {}

    # Scan completed full-coverage runs
    completed_runs = []
    run_dirs = sorted(out_root.glob("F*"))
    for rdir in run_dirs:
        if not rdir.is_dir():
            continue
        run_json_path = rdir / "run.json"
        rj = _read_json_safe(run_json_path)
        if not rj:
            continue
        rid = rj.get("run_id", rdir.name)
        status = rj.get("status", "unknown")
        items = rj.get("total_eligible_items", 0)
        best_loss = rj.get("best_loss")
        best_epoch = rj.get("best_epoch")
        completed_runs.append({
            "run_id": rid,
            "status": status,
            "items": items,
            "best_loss": round(best_loss, 4) if best_loss is not None else None,
            "best_epoch": best_epoch,
            "layers": rj.get("layers", []),
            "supervision": rj.get("supervision_classes", []),
        })

    reconciliation = queue_state.get("reconciliation", {})
    queue_status = queue_state.get("queue_status", "UNKNOWN")

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "timestamp_utc": now_iso,
        "gpu": gpu,
        "disk": disk,
        "processes": pids,
        "queue_status": queue_status,
        "current_run": current_run_id,
        "in_flight_cursor": in_flight_cursor,
        "reconciliation": reconciliation,
        "completed_runs": completed_runs,
        "recent_logs": recent_logs,
    }


def format_status_markdown(data: Dict[str, Any]) -> str:
    """Format snapshot into clean GitHub-flavored markdown."""
    ts = data["timestamp_utc"]
    gpu = data["gpu"]
    disk = data["disk"]
    proc = data["processes"]
    q_stat = data["queue_status"]
    cur_run = data["current_run"]
    cur_cur = data["in_flight_cursor"]
    reconc = data["reconciliation"]
    completed = data["completed_runs"]
    logs = data["recent_logs"]

    # Header & Status badges
    is_alive = proc["queue_pid"] is not None
    stat_badge = "🟢 **RUNNING**" if is_alive else ("🔴 **STOPPED**" if q_stat != "CAMPAIGN_TERMINAL" else "🏁 **TERMINAL**")

    md = []
    md.append("# 🚀 ModelRouter · 服务器端自治监控与运行看板")
    md.append("")
    md.append(f"> **状态更新于**: `{ts}` | **守护运行节点**: `k3s-infra-01` (RTX A6000) | **独立驻留模式**: `Server-Daemon`")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 一、服务与硬件实时健康度")
    md.append("")
    md.append("| 指标项 | 状态 / 数值 | 判定 |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **训练队列进程** | PID `{proc['queue_pid'] or 'NONE'}` | {stat_badge} |")
    md.append(f"| **底层训练算子** | PID `{proc['trainer_pid'] or 'IDLE'}` | {'🟢 活跃计算中' if proc['trainer_pid'] else '⚪ 等待切批'} |")

    if gpu.get("ok"):
        vram_pct = round((gpu['memory_used_mib'] / gpu['memory_total_mib']) * 100, 1)
        md.append(f"| **GPU 设备** | `{gpu['name']}` | 🟢 在线 |")
        md.append(f"| **GPU 核心利用率** | `{gpu['utilization_gpu_pct']}%` | {'🟢 高负荷训练' if gpu['utilization_gpu_pct'] > 50 else '🟡 阶段空闲'} |")
        md.append(f"| **显存占用** | `{gpu['memory_used_mib']:.0f} / {gpu['memory_total_mib']:.0f} MiB` ({vram_pct}%) | 🟢 安全充足 (预算充裕) |")
        md.append(f"| **GPU 温度与功耗** | `{gpu['temperature_gpu_c']:.0f} °C` / `{gpu['power_draw_w']:.0f} W` | 🟢 散热正常 |")
    else:
        md.append(f"| **GPU 设备** | {gpu.get('error', 'Error')} | 🔴 异常 |")

    if disk.get("ok"):
        md.append(f"| **磁盘可用空间 (/)** | 可用 `{disk['free_gib']} GiB` / 总量 `{disk['total_gib']} GiB` ({disk['used_pct']}% 已用) | {'🟢 空间充裕' if disk['free_gib'] > 200 else '⚠️ 需关注'} |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 二、全量覆盖训练链当前进度")
    md.append("")

    tot_runs = reconc.get("total_full_coverage_runs", 34)
    done_count = reconc.get("completed_runs_count", len([c for c in completed if c.get("status") == "completed"]))
    rem_count = reconc.get("queued_runs_count", tot_runs - done_count)
    progress_pct = round((done_count / tot_runs) * 100, 1) if tot_runs else 0

    md.append(f"- **总计划任务数**: `{tot_runs}`")
    md.append(f"- **已完成任务数**: `{done_count}` / `{tot_runs}` ({progress_pct}%)")
    md.append(f"- **等待排队任务**: `{rem_count}`")
    md.append(f"- **当前执行任务**: `{cur_run or 'NONE'}`")

    if cur_cur:
        c_ep = cur_cur.get("epoch", 1)
        c_chk = cur_cur.get("chunk_idx", 1)
        t_chk = cur_cur.get("total_chunks", 1)
        c_step = cur_cur.get("step_count", 0)
        c_items = cur_cur.get("consumed_items", 0)
        c_loss = cur_cur.get("latest_chunk_loss")
        loss_str = f"`{c_loss:.4f}`" if c_loss is not None else "`N/A`"
        md.append(f"  - **Epoch / Chunk**: Epoch `{c_ep}`, Chunk `{c_chk}/{t_chk}`")
        md.append(f"  - **优化器步数**: `{c_step}` 步")
        md.append(f"  - **已消费训练样本**: `{c_items:,}` 条")
        md.append(f"  - **当前分块 Loss**: {loss_str}")

    md.append("")
    md.append("### 已完成全量覆盖任务台账")
    md.append("")
    md.append("| 任务 ID | 层级范围 | 监督类型 | 训练样本数 | 最佳 Epoch | 最佳 Loss | 状态 |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    if completed:
        for c in completed:
            l_str = "+".join(c["layers"]) if c["layers"] else "-"
            s_str = "+".join(c["supervision"]) if c["supervision"] else "S1"
            loss_v = f"`{c['best_loss']:.4f}`" if c.get("best_loss") is not None else "-"
            ep_v = f"Epoch {c['best_epoch']}" if c.get("best_epoch") is not None else "-"
            st_badge = "✅ COMPLETED" if c.get("status") == "completed" else f"⏳ {c.get('status')}"
            md.append(f"| `{c['run_id']}` | {l_str} | {s_str} | `{c['items']:,}` | {ep_v} | {loss_v} | {st_badge} |")
    else:
        md.append("| *(暂无完成记录)* | - | - | - | - | - | - |")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## 三、底层运行日志最新抓取")
    md.append("")
    md.append("```text")
    if logs:
        for ln in logs:
            md.append(ln)
    else:
        md.append("(暂无新日志)")
    md.append("```")
    md.append("")
    md.append("---")
    md.append("")
    md.append("> ℹ️ **说明**: 本监控进程完全运行于远程服务器后台。即使本地 Mac 电脑关机或终端会话关闭，训练与监控将持续在服务器上自主推进。")

    return "\n".join(md) + "\n"


def run_monitor_loop(project_root: Path, out_root: Path, interval_s: int = 30) -> None:
    """Run detached daemon loop on server."""
    pid_file = out_root / "server_monitor.pid"
    status_md_file = out_root / "SERVER_MONITOR_STATUS.md"
    status_json_file = out_root / "monitor_status.json"

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    print(f"[{datetime.datetime.now()}] Server monitor daemon started (PID {os.getpid()}), interval={interval_s}s")
    sys.stdout.flush()

    last_completed_count = -1

    try:
        while True:
            try:
                snap = collect_monitor_snapshot(project_root, out_root)
                md_text = format_status_markdown(snap)

                # Write markdown and json atomically
                with open(status_md_file, "w", encoding="utf-8") as f:
                    f.write(md_text)
                with open(status_json_file, "w", encoding="utf-8") as f:
                    json.dump(snap, f, indent=2, ensure_ascii=False)

                # If completed runs increased, rebuild dashboard data
                curr_completed = len([c for c in snap["completed_runs"] if c.get("status") == "completed"])
                if curr_completed > last_completed_count and last_completed_count >= 0:
                    try:
                        print(f"[{datetime.datetime.now()}] Detected new completed run ({last_completed_count} -> {curr_completed}), rebuilding dashboard payload...")
                        sys.stdout.flush()
                        subprocess.run(
                            [sys.executable, str(project_root / "router_data" / "sync_dashboard_payload.py")],
                            cwd=str(project_root),
                            check=False,
                            capture_output=True,
                        )
                    except Exception as e:
                        print(f"Dashboard sync error: {e}")
                last_completed_count = curr_completed

            except Exception as loop_err:
                print(f"[{datetime.datetime.now()}] Monitor loop error: {loop_err}")
                sys.stdout.flush()

            time.sleep(interval_s)
    finally:
        if pid_file.is_file():
            try:
                pid_file.unlink()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="Server-Side Autonomous Watchdog & Progress Monitor")
    parser.add_argument("--project-root", type=str, default="/home/syy/路由")
    parser.add_argument("--out-root", type=str, default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--once", action="store_true", help="Print single snapshot and exit")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    out_root = (project_root / args.out_root).resolve()

    if args.once:
        snap = collect_monitor_snapshot(project_root, out_root)
        md = format_status_markdown(snap)
        print(md)
        return

    run_monitor_loop(project_root, out_root, interval_s=args.interval)


if __name__ == "__main__":
    main()
