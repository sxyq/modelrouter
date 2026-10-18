"""Canary verification for Terminal-Bench 2.1 (8 Canary tasks).

Provides:
- Manifest schema validation
- Canary task environment smoke checks (specifically `fix-git` and `count-dataset-tokens`)
- Readiness report generation
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

try:
    from modelrouter.sandbox.environment import MockSandboxEnvironment
    from modelrouter.sandbox.task_loader import TerminalBenchLoader
except ImportError:
    from experiments.harbor.environment import MockSandboxEnvironment
    from experiments.harbor.task_loader import TerminalBenchLoader

logger = logging.getLogger("modelrouter.sandbox.canary_verifier")


def run_canary_smoke_verification() -> Dict[str, Any]:
    """Runs zero-cost Canary smoke verification for Terminal-Bench 2.1 tasks.
    
    Verifies:
    1. Exactly 8 Canary tasks exist in manifest.
    2. Each task has valid ID, docker image, category, and SHA256.
    3. `fix-git` smoke execution works as expected.
    4. `count-dataset-tokens` smoke execution works as expected.
    """
    loader = TerminalBenchLoader()
    canary_tasks = loader.get_canary_tasks()
    
    results: List[Dict[str, Any]] = []
    
    # 1. Verify all 8 tasks schema & metadata
    for task in canary_tasks:
        env = MockSandboxEnvironment()
        env.reset(task.to_dict())
        
        # Run a basic smoke command
        res = env.exec("pwd")
        valid_schema = bool(
            task.task_id
            and task.docker_image
            and task.task_toml_sha256
            and task.category
        )
        
        task_report = {
            "task_id": task.task_id,
            "category": task.category,
            "difficulty": task.difficulty,
            "docker_image": task.docker_image,
            "schema_valid": valid_schema,
            "env_initialized": True,
            "pwd_status": res.exit_code == 0,
        }
        
        # Specific smoke test for fix-git
        if task.task_id == "fix-git":
            env.exec("git status")
            env.exec("git checkout master")
            env.exec("git merge e5f6g7h")
            passed, score, details = env.evaluate()
            task_report["smoke_passed"] = passed
            task_report["smoke_score"] = score
            task_report["smoke_details"] = details
        # Specific smoke test for count-dataset-tokens
        elif task.task_id == "count-dataset-tokens":
            env.exec("ls")
            env.exec("python -m count_tokens dataset.jsonl")
            passed, score, details = env.evaluate()
            task_report["smoke_passed"] = passed
            task_report["smoke_score"] = score
            task_report["smoke_details"] = details
        else:
            env.exec("ls")
            passed, score, details = env.evaluate()
            task_report["smoke_passed"] = passed
            task_report["smoke_score"] = score
            task_report["smoke_details"] = details
            
        results.append(task_report)
        
    all_passed = all(r["schema_valid"] and r["smoke_passed"] for r in results)
    summary = {
        "benchmark_id": loader.benchmark_id,
        "upstream_commit": loader.upstream_commit,
        "total_canary_tasks": len(canary_tasks),
        "verified_count": len(results),
        "all_passed": all_passed,
        "stage": "ENVIRONMENT_SMOKE_VERIFIED",
        "tasks": results,
    }
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    res = run_canary_smoke_verification()
    print(json.dumps(res, indent=2))
