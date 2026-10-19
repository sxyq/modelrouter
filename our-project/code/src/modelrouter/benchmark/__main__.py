"""CPU-only official benchmark preflight, artifact audit, and live trial progress.

Example: python -m modelrouter.benchmark preflight
         python -m modelrouter.benchmark audit ~/.cache/harbor/jobs/job-X
         python -m modelrouter.benchmark watch ~/.cache/harbor/jobs/job-X --once
Actual benchmark tasks are launched with the INSTALLED harbor CLI, not faked here.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from .official_artifacts import audit_job


def _probe(cmd: list[str], timeout: float = 6) -> dict:
    if not shutil.which(cmd[0]):
        return {"status": "MISSING", "reason": cmd[0] + " not found"}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLOCKED", "reason": type(exc).__name__}
    details = (result.stdout or result.stderr or "").strip().splitlines()
    return {
        "status": "READY" if result.returncode == 0 else "BLOCKED",
        "reason": details[0][:160] if details else "exit " + str(result.returncode),
    }


def preflight(environment: str = "docker") -> dict:
    """Local checks; never reads or prints the API key."""
    harbor = _probe(["harbor", "--version"])
    sandbox = _probe(["docker", "info"]) if environment == "docker" else {
        "status": "NOT_CHECKED",
        "reason": "Check authorized cloud provider environment independently",
    }
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": "terminal-bench/terminal-bench-2-1",
        "agent_recommended": "mini-swe-agent",
        "environment": environment,
        "harbor": harbor,
        "sandbox": sandbox,
        "status": "READY_FOR_ORACLE" if harbor["status"] == "READY" and sandbox["status"] == "READY"
                  else "BLOCKED_OR_UNVERIFIED",
        "official_trials": 0,
    }


def progress(job_dir: Path) -> dict:
    result = audit_job(job_dir)
    trials = result["trials"]
    verified = [r for r in trials if r["status"] == "OFFICIAL_ARTIFACT_VERIFIED"]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_dir": str(job_dir),
        "status": result["status"],
        "observed_trials": len(trials),
        "verified_trials": len(verified),
        "verified_reward_sum": sum(float(x["reward"]) for x in verified),
        "verified_reward_mean": (
            sum(float(x["reward"]) for x in verified) / len(verified) if verified else None
        ),
        "remaining_unverified": len(trials) - len(verified),
        "counts": result["counts"],
        "missing_job_files": result["missing_job_files"],
    }


def _write_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="ModelRouter official Harbor evidence CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("preflight", help="Check Harbor and Docker, with no API calls")
    p.add_argument("--environment", choices=["docker", "daytona", "modal", "e2b"], default="docker")
    p = sub.add_parser("audit", help="Verify original job/trial/lock/verifier artifacts")
    p.add_argument("job_dir", type=Path)
    p.add_argument("--output", type=Path)
    p = sub.add_parser("watch", help="Report verified trial progress in the terminal")
    p.add_argument("job_dir", type=Path)
    p.add_argument("--once", action="store_true")
    p.add_argument("--interval", type=float, default=10.0)
    p.add_argument("--output", type=Path, help="Optional progress JSON file for the dashboard")
    args = parser.parse_args(argv)

    if args.command == "preflight":
        result = preflight(args.environment)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "READY_FOR_ORACLE" else 2

    if args.command == "audit":
        result = audit_job(args.job_dir)
        if args.output:
            _write_atomic(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else 2

    if args.interval < 1:
        parser.error("--interval must be at least 1 second")
    try:
        while True:
            result = progress(args.job_dir)
            if args.output:
                _write_atomic(args.output, result)
            print(
                "{time} | {status} | official {done}/{total} | mean reward {reward}".format(
                    time=result["timestamp"],
                    status=result["status"],
                    done=result["verified_trials"],
                    total=result["observed_trials"],
                    reward=("N/A" if result["verified_reward_mean"] is None
                            else "{:.4f}".format(result["verified_reward_mean"])),
                ),
                flush=True,
            )
            if args.once:
                return 0 if result["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else 2
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
