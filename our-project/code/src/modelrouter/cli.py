#!/usr/bin/env python3
"""
modelrouter.cli - Formal Command Line Interface for ModelRouter
Provides canonical entrypoints for:
- status: Check system health, GPU, token budget, and server status.
- route: Test routing inference via local API endpoint.
- benchmark: Run agent benchmarks (canary, matrix, stress).
- dashboard: Sync and serve training dashboard.
"""

import sys
import json
import argparse
import urllib.request
from pathlib import Path


def cmd_status(args):
    """Checks health of A6000 router serving and local token budget."""
    print("=== ModelRouter Status ===")
    
    # 1. Router serving health
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Router Serving (Port 8000): HEALTHY (uptime: {data.get('uptime_seconds', 0):.1f}s)")
            print(f"  GPU: {data.get('gpu_name')} (used: {data.get('gpu_memory_used_mb')} MiB, util: {data.get('gpu_utilization_pct')}%)")
            print(f"  Models: {data.get('models_loaded')}")
    except Exception as e:
        print(f"Router Serving (Port 8000): UNREACHABLE ({e})")

    # 2. Token budget
    budget_paths = [
        Path("experiments/agent_pilot/token_budget.json"),
        Path("our-project/data/token_budget.json"),
    ]
    for bp in budget_paths:
        if bp.is_file():
            try:
                with open(bp, "r") as f:
                    bdata = json.load(f)
                print(f"Token Budget: {bdata.get('consumed_total_tokens', 0)} / {bdata.get('max_tokens', 1000000)} consumed ({bdata.get('remaining_tokens', 0)} remaining)")
                break
            except Exception:
                pass


def cmd_route(args):
    """Executes a sample routing decision via local FastAPI server."""
    payload = {
        "request_id": "cli-test",
        "prompt": args.prompt or "Fix git merge conflicts",
        "model_requested": args.model or "laya",
        "legal_actions": [
            {"provider": "openai", "model": "gpt-6-luna", "native_effort": "medium"},
            {"provider": "openai", "model": "gpt-5.6-luna", "native_effort": "low"}
        ]
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8000/route",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Route error: {e}")


def main():
    parser = argparse.ArgumentParser(prog="modelrouter", description="ModelRouter Unified CLI")
    subparsers = parser.add_subparsers(dest="command")

    # status
    p_status = subparsers.add_parser("status", help="Check system health, serving, and token budget")
    p_status.set_defaults(func=cmd_status)

    # route
    p_route = subparsers.add_parser("route", help="Execute test routing query")
    p_route.add_argument("--prompt", type=str, default="Fix git merge conflicts", help="Input prompt")
    p_route.add_argument("--model", type=str, default="laya", choices=["laya", "kev"], help="Router model")
    p_route.set_defaults(func=cmd_route)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
