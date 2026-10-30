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


def _get_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def cmd_status(args):
    """Checks health of A6000 router serving and local token budget."""
    print("=== ModelRouter Status ===")
    
    # 1. Router serving health
    try:
        opener = _get_opener()
        req = urllib.request.Request("http://127.0.0.1:8000/health")
        with opener.open(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Router Serving (Port 8000): HEALTHY (uptime: {data.get('uptime_seconds', 0):.1f}s)")
            print(f"  GPU: {data.get('gpu_name')} (used: {data.get('gpu_memory_used_mb')} MiB, util: {data.get('gpu_utilization_pct')}%)")
            print(f"  Models: {data.get('models_loaded')}")
    except Exception as e:
        print(f"Router Serving (Port 8000): UNREACHABLE ({e})")

    # 2. Recorded API usage
    budget_paths = [
        Path("experiments/agent_pilot/token_budget.json"),
        Path("our-project/data/token_budget.json"),
    ]
    for bp in budget_paths:
        if bp.is_file():
            try:
                with open(bp, "r") as f:
                    bdata = json.load(f)
                print(f"API Usage: {bdata.get('consumed_total_tokens', 0)} tokens consumed; no cumulative token limit")
                break
            except Exception:
                pass


def cmd_route(args):
    """Executes a sample routing decision via local FastAPI server."""
    import time
    payload = {
        "request_id": f"cli-test-{int(time.time())}",
        "episode_id": "ep-cli",
        "decision_id": "dec-cli",
        "policy_version": "v9.0",
        "router_family": args.model or "laya",
        "pre_decision_state": {
            "task_domain": "software_engineering",
            "prompt": args.prompt or "Fix git merge conflicts",
            "context_chars": len(args.prompt or "")
        },
        "legal_actions": [
            {"provider": "openai", "model": "gpt-6-luna", "revision": "latest", "native_effort": "medium"},
            {"provider": "openai", "model": "gpt-5.6-luna", "revision": "latest", "native_effort": "low"}
        ]
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8000/route",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        opener = _get_opener()
        with opener.open(req, timeout=15) as resp:
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
