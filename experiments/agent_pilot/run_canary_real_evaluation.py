"""Real Harbor Sandbox Execution and Canary Evaluation for ModelRouter V8.

Executes real agent episodes on Terminal-Bench 2.1 Canary tasks:
1. Docker availability check on Mac
2. fix-git real execution using gpt-6-luna and official verifier
3. count-dataset-tokens real execution using gpt-6-luna and official verifier
4. Records all traces, tool calls, model decisions, and CTRF verifier artifacts into:
   runs/agent_pilot/<date>/terminal-bench-2-1/...
5. Updates and validates token_budget.json.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from experiments.agent_pilot.agent import SingleAgent
from experiments.agent_pilot.ledger import ExperimentLedger
from experiments.agent_pilot.policy import create_policy
from experiments.agent_pilot.provider import OpenAIChatCompletionsProvider
from experiments.harbor.environment import DockerSandboxEnvironment, LocalHarborSandboxEnvironment
from experiments.harbor.task_loader import TerminalBenchLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("canary_eval")


def run_real_canary_evaluation():
    print("=" * 70)
    print("STARTING REAL HARBOR CANARY EVALUATION (gpt-6-luna)")
    print("=" * 70)

    # 1. Check Docker availability on Mac
    docker_env = DockerSandboxEnvironment()
    docker_check = docker_env.check_availability()
    print(f"\n[1] Docker Availability Check on Host (macOS):")
    print(f"    Available: {docker_check['available']}")
    print(f"    Status: {docker_check.get('error', 'Docker is available')}")
    if not docker_check["available"]:
        print("    -> Proceeding with LocalHarborSandboxEnvironment (strict process isolation + official pytest verifiers).")

    # 2. Initialize benchmark loader and ledger
    loader = TerminalBenchLoader()
    ledger = ExperimentLedger()
    provider = OpenAIChatCompletionsProvider()
    policy = create_policy("luna")

    print(f"\n[2] Benchmark Info:")
    print(f"    Benchmark: {loader.benchmark_id}")
    print(f"    Upstream Commit: {loader.upstream_commit}")
    print(f"    Provider Base URL: {provider.base_url}")
    print(f"    Primary Model: {provider.primary_model}")

    canary_task_ids = ["fix-git", "count-dataset-tokens"]
    results = []

    for task_id in canary_task_ids:
        print("\n" + "-" * 70)
        print(f"EXECUTING CANARY TASK: {task_id}")
        print("-" * 70)

        task_obj = loader.get_task(task_id)
        if not task_obj:
            logger.error("Task %s not found in manifest!", task_id)
            continue

        task_dict = task_obj.to_dict()
        print(f"Instruction snippet: {task_obj.instruction[:120]}...")

        # Initialize real sandbox environment
        env = LocalHarborSandboxEnvironment()
        agent = SingleAgent(max_steps=8, time_budget_sec=120.0, usd_budget=1.0)

        # Run episode
        t0 = datetime.now(timezone.utc)
        ep_result = agent.run_episode(
            task=task_dict,
            environment=env,
            policy=policy,
            provider=provider,
            seed=42,
        )

        # Record to append-only ledger and copy verifier artifacts
        ep_dir = ledger.record_episode(ep_result, benchmark_name="terminal-bench-2-1")

        print(f"\n[Result for {task_id}]:")
        print(f"  Status: {ep_result.status}")
        print(f"  Resolved: {ep_result.resolved}")
        print(f"  Score: {ep_result.score}")
        print(f"  Total Steps: {ep_result.total_steps}")
        print(f"  Cost (USD): ${ep_result.total_cost_usd:.5f}")
        print(f"  Prompt Tokens: {ep_result.total_prompt_tokens}")
        print(f"  Completion Tokens: {ep_result.total_completion_tokens}")
        print(f"  Run Directory: {ep_dir}")

        if "ctrf_summary" in ep_result.evaluator_details:
            print(f"  Official CTRF Summary: {ep_result.evaluator_details['ctrf_summary']}")

        results.append({
            "task_id": task_id,
            "status": ep_result.status,
            "resolved": ep_result.resolved,
            "score": ep_result.score,
            "steps": ep_result.total_steps,
            "cost_usd": ep_result.total_cost_usd,
            "prompt_tokens": ep_result.total_prompt_tokens,
            "completion_tokens": ep_result.total_completion_tokens,
            "run_dir": str(ep_dir),
            "ctrf_summary": ep_result.evaluator_details.get("ctrf_summary", {}),
        })

    # Read updated token budget
    budget_file = Path(__file__).resolve().parent / "token_budget.json"
    budget_data = {}
    if budget_file.exists():
        budget_data = json.loads(budget_file.read_text(encoding="utf-8"))

    print("\n" + "=" * 70)
    print("CANARY EVALUATION COMPLETE - SUMMARY REPORT")
    print("=" * 70)
    print(f"Total Tasks Evaluated: {len(results)}")
    for r in results:
        res_str = "PASSED" if r["resolved"] else "FAILED"
        print(f"  - {r['task_id']:<22} {res_str:<8} (score={r['score']}, steps={r['steps']}, cost=${r['cost_usd']:.5f})")
    print(f"\nToken Budget Status:")
    print(f"  Consumed Total Tokens: {budget_data.get('consumed_total_tokens', 0)}")
    print(f"  Remaining Tokens:      {budget_data.get('remaining_tokens', 0)}")
    print(f"  Total API Calls:       {budget_data.get('total_calls', 0)}")
    print("=" * 70)

    # Save summary report to runs/agent_pilot/canary_report.json
    report_file = Path(__file__).resolve().parent.parent.parent / "runs" / "agent_pilot" / "canary_report.json"
    report_payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docker_availability": docker_check,
        "results": results,
        "token_budget": budget_data,
    }
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)
    print(f"Canary report saved to: {report_file}")


if __name__ == "__main__":
    run_real_canary_evaluation()
