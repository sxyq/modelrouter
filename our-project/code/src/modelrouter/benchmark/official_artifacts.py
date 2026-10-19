"""Fail-closed, CPU-only auditor for actual Harbor job/trial verifier artifacts.

This checks structural provenance, not authenticity of arbitrary third-party files.
An official publication still requires checking the locked benchmark/source and
the original Harbor run against the host's job directory.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _verifier_reward(trial_dir: Path) -> float | None:
    """Read the original on-disk Harbor verifier reward; do not infer success."""
    reward_dir = trial_dir / "verifier"
    reward_json = reward_dir / "reward.json"
    reward_txt = reward_dir / "reward.txt"
    if reward_json.is_file():
        data = _read_json(reward_json)
        if data is None or not isinstance(data.get("reward"), (int, float)):
            return None
        val = float(data["reward"])
    elif reward_txt.is_file():
        try:
            val = float(reward_txt.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return None
    else:
        return None
    return val if math.isfinite(val) else None


def audit_trial(trial_dir: str | Path) -> dict[str, Any]:
    """Classify a trial WITHOUT generating or rewriting any benchmark score."""
    p = Path(trial_dir)
    result: dict[str, Any] = {
        "trial_dir": str(p),
        "status": "NOT_EVALUATED",
        "reward": None,
        "error": None,
        "reason": "",
    }
    if not (p / "config.json").is_file() or not (p / "result.json").is_file():
        result["reason"] = "Missing original Harbor trial config.json or result.json"
        return result
    if not (p / "lock.json").is_file():
        result["reason"] = "Missing Harbor trial lock.json (source digest not verified)"
        return result
    data = _read_json(p / "result.json")
    if data is None:
        result["reason"] = "Invalid original Harbor trial result.json"
        return result
    verifier = data.get("verifier_result")
    rewards = verifier.get("rewards") if isinstance(verifier, dict) else None
    scored = rewards.get("reward") if isinstance(rewards, dict) else None
    original = _verifier_reward(p)
    if isinstance(scored, bool) or not isinstance(scored, (int, float)):
        result["reason"] = "No numeric official verifier_result.rewards.reward"
        return result
    if original is None:
        result["reason"] = "Original verifier/reward.txt or verifier/reward.json absent"
        return result
    score = float(scored)
    if not math.isfinite(score) or not math.isclose(original, score, abs_tol=1e-8):
        result["status"] = "VERIFIER_MISMATCH"
        result["reason"] = "Trial result reward differs from original verifier artifact"
        return result
    result["status"] = "OFFICIAL_ARTIFACT_VERIFIED"
    result["reward"] = score
    result["error"] = data.get("exception_info")
    result["reason"] = "Structured Harbor trial, lock, verifier and reward agree"
    return result


def audit_job(job_dir: str | Path) -> dict[str, Any]:
    """Only count trials under a Harbor job with its own config/lock/results."""
    p = Path(job_dir)
    job_files = ("config.json", "result.json", "lock.json")
    missing = [name for name in job_files if not (p / name).is_file()]
    report: dict[str, Any] = {
        "job_dir": str(p), "status": "NOT_EVALUATED",
        "missing_job_files": missing, "trials": [], "counts": {},
    }
    if missing:
        return report
    found = sorted(
        x.parent for x in p.rglob("result.json")
        if x.parent != p and (x.parent / "config.json").is_file()
    )
    if not found:
        report["missing_job_files"].append("trial directories")
        return report
    rows = [audit_trial(path) for path in found]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    report["trials"] = rows
    report["counts"] = counts
    report["status"] = (
        "OFFICIAL_ARTIFACT_VERIFIED"
        if counts.get("OFFICIAL_ARTIFACT_VERIFIED") == len(rows)
        else "PARTIAL_OR_UNVERIFIED"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit existing Harbor verifier provenance without API calls")
    parser.add_argument("job_dir", help="Actual Harbor job output directory")
    parser.add_argument("--output", type=Path, help="Optional machine-readable local report")
    args = parser.parse_args(argv)
    report = audit_job(args.job_dir)
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(output + "\n", encoding="utf-8")
        temporary.replace(args.output)
    print(output)
    return 0 if report["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
