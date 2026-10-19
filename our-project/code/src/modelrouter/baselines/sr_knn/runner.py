#!/usr/bin/env python3
"""Standalone CLI runner for the SR-KNN baseline method."""
from __future__ import annotations

import argparse
import json
from modelrouter.baselines.sr_knn_adapter import SRKNNAdapter


def main() -> None:
    parser = argparse.ArgumentParser(description="SR-KNN Standalone Baseline Runner")
    parser.add_argument("-k", "--neighbors", type=int, default=3, help="Number of nearest neighbors")
    parser.add_argument("--step-index", type=int, default=2, help="Current step index")
    parser.add_argument("--max-steps", type=int, default=10, help="Max step limit")
    parser.add_argument("--phase", type=str, default="modify", choices=["inspect", "modify", "verify"], help="Agent phase")
    parser.add_argument("--last-exit-code", type=int, default=0, help="Exit code of previous tool")
    parser.add_argument("--context-tokens", type=int, default=4000, help="Context token length")
    parser.add_argument("--budget-ratio", type=float, default=0.75, help="Budget remaining ratio")
    parser.add_argument("--tool-errors", type=int, default=0, help="Cumulative tool errors")
    parser.add_argument("--difficulty", type=float, default=0.5, help="Initial task difficulty score")
    args = parser.parse_args()

    adapter = SRKNNAdapter(k=args.neighbors)
    vec = adapter.extract_vector(
        step_index=args.step_index,
        max_steps=args.max_steps,
        phase=args.phase,
        last_exit_code=args.last_exit_code,
        context_tokens=args.context_tokens,
        budget_remaining_ratio=args.budget_ratio,
        tool_error_count=args.tool_errors,
        task_difficulty_score=args.difficulty,
    )

    pred = adapter.predict(vec)
    out = {
        "method": "SR-KNN",
        "upstream_commit": adapter.upstream_commit,
        "k_neighbors": args.neighbors,
        "state_vector_8d": [round(x, 4) for x in vec],
        "prediction": pred,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
