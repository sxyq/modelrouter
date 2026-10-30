"""Real 8-Policy Benchmark Matrix Execution on Terminal-Bench 2.1 Canary Tasks.

Strictly follows V8 §9.2 and user instructions:
1. Executes real agent episodes across all 8 policies:
   - fixed_strong
   - fixed_cheap
   - random
   - rule_sticky
   - routellm (official winrate threshold architecture)
   - sr_knn (official 8D state vector representation)
   - laya_v2 (remote A6000 serving API)
   - kev_4b (remote A6000 serving API)
2. Across both canary tasks:
   - fix-git
   - count-dataset-tokens
3. In isolated LocalHarborSandboxEnvironment with official pytest CTRF verifiers.
4. Calling real generator API (gpt-6-luna) under global token budget (< 1,000,000 tokens).
5. Outputting runs/agent_pilot/comparison.csv and real_matrix_summary.json.
"""
from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.agent_pilot.agent import SingleAgent
from experiments.agent_pilot.ledger import ExperimentLedger
from experiments.agent_pilot.policy import create_policy
from experiments.agent_pilot.provider import OpenAIChatCompletionsProvider
from experiments.harbor.environment import LocalHarborSandboxEnvironment
from experiments.harbor.task_loader import TerminalBenchLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("benchmark_matrix")

POLICIES = [
    "fixed_strong",
    "fixed_cheap",
    "random",
    "rule_sticky",
    "routellm",
    "sr_knn",
    "laya_v2",
    "kev_4b",
]

TASKS = [
    "fix-git",
    "count-dataset-tokens",
]


def run_matrix():
    print("=" * 80)
    print("STARTING REAL 8-POLICY BENCHMARK MATRIX EXECUTION (Terminal-Bench 2.1)")
    print("=" * 80)

    loader = TerminalBenchLoader()
    ledger = ExperimentLedger()
    provider = OpenAIChatCompletionsProvider()

    print(f"Benchmark: {loader.benchmark_id}")
    print(f"Generator Base URL: {provider.base_url}")
    print(f"Primary Generator Model: {provider.primary_model}")
    print(f"Total Policies: {len(POLICIES)}")
    print(f"Total Tasks: {len(TASKS)}")
    print("-" * 80)

    all_records: List[Dict[str, Any]] = []
    matrix_dir = Path(__file__).resolve().parent.parent.parent / "runs" / "agent_pilot"
    matrix_dir.mkdir(parents=True, exist_ok=True)
    csv_file = matrix_dir / "comparison.csv"
    summary_file = matrix_dir / "real_matrix_summary.json"

    for task_idx, task_id in enumerate(TASKS, 1):
        print(f"\n================================================================================")
        print(f"TASK {task_idx}/{len(TASKS)}: {task_id}")
        print(f"================================================================================")

        task_obj = loader.get_task(task_id)
        if not task_obj:
            logger.error("Task %s not found in manifest!", task_id)
            continue
        task_dict = task_obj.to_dict()

        for pol_idx, pol_name in enumerate(POLICIES, 1):
            print(f"\n--- [{task_id}] Policy {pol_idx}/{len(POLICIES)}: {pol_name} ---")
            t_start = time.time()

            try:
                policy = create_policy(pol_name, seed=42)
            except Exception as e:
                logger.error("Failed to create policy %s: %s", pol_name, e)
                continue

            env = LocalHarborSandboxEnvironment()
            # Bounded steps (max 4 steps) to stay safely within token and time limits
            agent = SingleAgent(max_steps=4, time_budget_sec=60.0, usd_budget=0.5)

            try:
                ep_result = agent.run_episode(
                    task=task_dict,
                    environment=env,
                    policy=policy,
                    provider=provider,
                    seed=42,
                )
                ep_dir = ledger.record_episode(ep_result, benchmark_name="terminal-bench-2-1")
                elapsed = time.time() - t_start

                # Extract mean router latency from episode decisions
                router_latencies = [
                    d.get("decision_latency_ms", 0.0)
                    for d in ep_result.router_decisions
                    if isinstance(d, dict)
                ]
                mean_router_lat = (
                    sum(router_latencies) / len(router_latencies)
                    if router_latencies
                    else 0.0
                )

                rec = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "task_id": task_id,
                    "policy_id": pol_name,
                    "status": ep_result.status,
                    "resolved": ep_result.resolved,
                    "score": ep_result.score,
                    "steps": ep_result.total_steps,
                    "cost_usd": round(ep_result.total_cost_usd, 6),
                    "prompt_tokens": ep_result.total_prompt_tokens,
                    "completion_tokens": ep_result.total_completion_tokens,
                    "elapsed_sec": round(elapsed, 2),
                    "mean_router_latency_ms": round(mean_router_lat, 2),
                    "ctrf_summary": ep_result.evaluator_details.get("ctrf_summary", {}),
                    "run_dir": str(ep_dir),
                }
                all_records.append(rec)

                print(f"  Result: {ep_result.status} | Resolved: {ep_result.resolved} | Steps: {ep_result.total_steps} | Cost: ${ep_result.total_cost_usd:.5f} | Time: {elapsed:.1f}s")
                if "ctrf_summary" in ep_result.evaluator_details:
                    ctrf = ep_result.evaluator_details["ctrf_summary"]
                    print(f"  CTRF: tests={ctrf.get('tests', 0)}, passed={ctrf.get('passed', 0)}, failed={ctrf.get('failed', 0)}")

            except Exception as e:
                logger.error("Episode execution failed for %s on %s: %s", pol_name, task_id, e)
                rec = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "task_id": task_id,
                    "policy_id": pol_name,
                    "status": "ERROR",
                    "resolved": False,
                    "score": 0.0,
                    "steps": 0,
                    "cost_usd": 0.0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "elapsed_sec": round(time.time() - t_start, 2),
                    "mean_router_latency_ms": 0.0,
                    "ctrf_summary": {},
                    "run_dir": "",
                    "error": str(e),
                }
                all_records.append(rec)

            finally:
                env.close()

            # Save incremental progress to CSV and JSON
            _save_artifacts(csv_file, summary_file, all_records)

    print("\n" + "=" * 80)
    print("REAL BENCHMARK MATRIX EXECUTION FINISHED")
    print("=" * 80)
    _print_summary_table(all_records)


def _save_artifacts(csv_file: Path, summary_file: Path, records: List[Dict[str, Any]]):
    fieldnames = [
        "timestamp",
        "task_id",
        "policy_id",
        "status",
        "resolved",
        "score",
        "steps",
        "cost_usd",
        "prompt_tokens",
        "completion_tokens",
        "elapsed_sec",
        "mean_router_latency_ms",
        "run_dir",
    ]
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    # Policy aggregation
    policy_stats: Dict[str, Dict[str, Any]] = {}
    for r in records:
        pid = r["policy_id"]
        if pid not in policy_stats:
            policy_stats[pid] = {
                "policy_id": pid,
                "total_tasks": 0,
                "resolved_tasks": 0,
                "total_steps": 0,
                "total_cost_usd": 0.0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_elapsed_sec": 0.0,
                "latencies": [],
            }
        s = policy_stats[pid]
        s["total_tasks"] += 1
        if r["resolved"]:
            s["resolved_tasks"] += 1
        s["total_steps"] += r["steps"]
        s["total_cost_usd"] += r["cost_usd"]
        s["total_prompt_tokens"] += r["prompt_tokens"]
        s["total_completion_tokens"] += r["completion_tokens"]
        s["total_elapsed_sec"] += r["elapsed_sec"]
        if r["mean_router_latency_ms"] > 0:
            s["latencies"].append(r["mean_router_latency_ms"])

    summary_rows = []
    for pid, s in policy_stats.items():
        n = s["total_tasks"]
        pass_rate = round(s["resolved_tasks"] / n, 4) if n > 0 else 0.0
        mean_steps = round(s["total_steps"] / n, 2) if n > 0 else 0.0
        mean_cost = round(s["total_cost_usd"] / n, 5) if n > 0 else 0.0
        mean_lat = round(sum(s["latencies"]) / len(s["latencies"]), 2) if s["latencies"] else 0.0
        summary_rows.append({
            "policy_id": pid,
            "total_tasks": n,
            "resolved_tasks": s["resolved_tasks"],
            "pass_rate": pass_rate,
            "total_cost_usd": round(s["total_cost_usd"], 5),
            "mean_cost_usd": mean_cost,
            "mean_steps": mean_steps,
            "mean_router_latency_ms": mean_lat,
        })

    summary_payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(records),
        "policy_summaries": summary_rows,
        "records": records,
    }
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)


def _print_summary_table(records: List[Dict[str, Any]]):
    print(f"{'Task':<22} {'Policy':<14} {'Status':<10} {'Res':<5} {'Steps':<6} {'Cost($)':<10} {'Latency(ms)':<12}")
    print("-" * 85)
    for r in records:
        res_str = "YES" if r["resolved"] else "NO"
        print(f"{r['task_id']:<22} {r['policy_id']:<14} {r['status']:<10} {res_str:<5} {r['steps']:<6} {r['cost_usd']:<10.5f} {r['mean_router_latency_ms']:<12.1f}")


if __name__ == "__main__":
    run_matrix()
