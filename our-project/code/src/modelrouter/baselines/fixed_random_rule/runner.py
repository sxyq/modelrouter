#!/usr/bin/env python3
"""Standalone CLI runner for Static, Random, and Rule-based baselines."""
from __future__ import annotations

import argparse
import json
from modelrouter.agent.state import AgentState
from modelrouter.baselines.policy import create_policy


def main() -> None:
    parser = argparse.ArgumentParser(description="Static Baselines Runner")
    parser.add_argument(
        "--policy",
        type=str,
        default="rule_sticky",
        choices=["fixed_strong", "fixed_cheap", "random", "rule_sticky"],
        help="Policy ID to evaluate",
    )
    parser.add_argument("--phase", type=str, default="modify", choices=["inspect", "modify", "verify"])
    parser.add_argument("--budget", type=float, default=1.5, help="Remaining budget in USD")
    args = parser.parse_args()

    state = AgentState(
        task_id="runner_sample_task",
        episode_id="runner_ep_01",
        policy_id=args.policy,
        usd_budget=args.budget,
    )
    state.start()
    state.current_phase = args.phase

    legal_actions = [
        {"provider": "openai", "model": "gpt-6-luna", "pool": "Strong", "native_effort": "high"},
        {"provider": "openai", "model": "gpt-5.6-luna", "pool": "Fast", "native_effort": "low"},
        {"provider": "anthropic", "model": "claude-3-5-sonnet", "pool": "Standard", "native_effort": "medium"},
    ]

    pol = create_policy(args.policy)
    dec = pol.select(state, legal_actions)

    out = {
        "policy": args.policy,
        "selected_model": dec.selected_action["model"],
        "selected_pool": dec.selected_action.get("pool"),
        "confidence": dec.confidence,
        "decision_latency_ms": round(dec.decision_latency_ms, 3),
        "router_family": dec.router_family,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
