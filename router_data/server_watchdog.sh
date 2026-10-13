#!/usr/bin/env bash
# ==============================================================================
# ModelRouter Server-Side Watchdog & Daemon Controller
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_ROOT="$PROJECT_ROOT/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"

MONITOR_PID_FILE="$OUT_ROOT/server_monitor.pid"
MONITOR_LOG="$OUT_ROOT/server_monitor.log"
STATUS_MD="$OUT_ROOT/SERVER_MONITOR_STATUS.md"

action="${1:-status}"

case "$action" in
  start)
    if [ -f "$MONITOR_PID_FILE" ]; then
      old_pid="$(cat "$MONITOR_PID_FILE" 2>/dev/null || true)"
      if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
        echo "Server monitor already running with PID $old_pid."
        exit 0
      fi
    fi
    echo "Starting Server Monitor Daemon in background on host $(hostname)..."
    nohup "$PYTHON_BIN" "$SCRIPT_DIR/server_monitor.py" \
      --project-root "$PROJECT_ROOT" \
      --out-root "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012" \
      --interval 30 > "$MONITOR_LOG" 2>&1 &
    new_pid=$!
    echo "$new_pid" > "$MONITOR_PID_FILE"
    echo "Server monitor daemon started with PID $new_pid."
    echo "Log: $MONITOR_LOG"
    ;;

  stop)
    if [ -f "$MONITOR_PID_FILE" ]; then
      pid="$(cat "$MONITOR_PID_FILE" 2>/dev/null || true)"
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo "Stopping server monitor PID $pid..."
        kill "$pid" || true
        rm -f "$MONITOR_PID_FILE"
        echo "Stopped."
        exit 0
      fi
    fi
    echo "Server monitor is not running."
    ;;

  status)
    if [ -f "$STATUS_MD" ]; then
      cat "$STATUS_MD"
    else
      echo "Status file not found. Running one-time snapshot:"
      "$PYTHON_BIN" "$SCRIPT_DIR/server_monitor.py" --once --project-root "$PROJECT_ROOT"
    fi
    ;;

  log)
    echo "Tailing continuous queue training log:"
    tail -f "$OUT_ROOT/continuous_queue.log"
    ;;

  *)
    echo "Usage: $0 {start|stop|status|log}"
    exit 1
    ;;
esac
