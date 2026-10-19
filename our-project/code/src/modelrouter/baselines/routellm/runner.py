#!/usr/bin/env python3
"""Standalone CLI runner for the RouteLLM baseline method."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from modelrouter.baselines.routellm_adapter import RouteLLMAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description="RouteLLM Standalone Baseline Runner")
    parser.add_argument("--threshold", type=float, default=0.55, help="Decision boundary theta")
    parser.add_argument("--instruction", type=str, default="Fix git merge conflict in repo", help="Task prompt")
    parser.add_argument("--steps", type=int, default=2, help="Completed steps")
    parser.add_argument("--tokens", type=int, default=2500, help="Context tokens approx")
    parser.add_argument("--last-exit-code", type=int, default=0, help="Last tool exit code")
    parser.add_argument("--tool-errors", type=int, default=0, help="Total tool errors")
    args = parser.parse_args()

    adapter = RouteLLMAdapter(threshold=args.threshold)
    score = adapter.compute_difficulty(
        instruction=args.instruction,
        history_steps=args.steps,
        max_steps=10,
        context_tokens=args.tokens,
        last_exit_code=args.last_exit_code,
        tool_error_count=args.tool_errors,
        budget_remaining_ratio=0.8,
    )

    out = {
        "method": "RouteLLM",
        "upstream_commit": adapter.upstream_commit,
        "threshold": args.threshold,
        "win_rate": round(score.win_rate, 4),
        "selected_tier": score.selected_tier,
        "feature_projection": {k: round(v, 4) for k, v in score.feature_projection.items()},
        "algorithm_status": score.algorithm_status,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
