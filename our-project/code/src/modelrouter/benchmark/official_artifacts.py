"""Read original Harbor 0.24 job, trial, ATIF and verifier artifacts.

Agreement between recorded artifacts does not authenticate arbitrary files.
Missing observations stay null; no score, usage or timing is synthesized.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _seconds(timing: dict | None) -> float | None:
    timing = timing or {}
    if not timing.get("started_at") or not timing.get("finished_at"):
        return None
    return (datetime.fromisoformat(timing["finished_at"].replace("Z", "+00:00"))
            - datetime.fromisoformat(timing["started_at"].replace("Z", "+00:00"))).total_seconds()


def _reward_artifact(directory: Path) -> tuple[dict | None, str | None]:
    # Harbor prefers reward.json when both artifacts exist.
    txt, js = directory / "reward.txt", directory / "reward.json"
    if js.is_file():
        return _read_json(js), str(js)
    if txt.is_file():
        try:
            return {"reward": float(txt.read_text().strip())}, str(txt)
        except ValueError:
            return None, str(txt)
    return None, None


def _same_rewards(left: dict | None, right: dict | None) -> bool:
    if not left or not right or left.keys() != right.keys():
        return False
    for key, value in left.items():
        other = right[key]
        if (isinstance(value, bool) or isinstance(other, bool)
                or not isinstance(value, (int, float))
                or not isinstance(other, (int, float))
                or not math.isfinite(value) or not math.isfinite(other)
                or not math.isclose(value, other, rel_tol=0, abs_tol=1e-8)):
            return False
    return True


def read_trace(trial_dir: str | Path) -> dict[str, Any]:
    """Extract recorded ATIF calls and observations, without timing estimates."""
    root = Path(trial_dir)
    paths = ([root / "agent" / "trajectory.json"]
             + sorted(root.glob("steps/*/agent/trajectory.json")))
    events, files = [], []
    for path in paths:
        trajectory = _read_json(path)
        if trajectory is None:
            continue
        files.append(str(path))
        for step in trajectory.get("steps", []):
            if step.get("source") != "agent" or step.get("is_copied_context"):
                continue
            observations = {
                item.get("source_call_id"): item
                for item in (step.get("observation") or {}).get("results", [])
            }
            calls = []
            for call in step.get("tool_calls") or []:
                observation = observations.get(call.get("tool_call_id"), {})
                extra = observation.get("extra") or {}
                calls.append({
                    **call, "observation": observation,
                    "exit_code": extra.get("exit_code"),
                    "duration_ms": extra.get("duration_ms"),
                })
            events.append({
                "trace_file": str(path), "step_id": step["step_id"],
                "timestamp": step.get("timestamp"),
                "model": step.get("model_name") or (trajectory.get("agent") or {}).get("model_name"),
                "effort": step.get("reasoning_effort"),
                "metrics": step.get("metrics") or {}, "tool_calls": calls,
            })
    return {"files": files, "steps": events,
            "tool_call_count": sum(len(step["tool_calls"]) for step in events)}


def audit_trial(trial_dir: str | Path) -> dict[str, Any]:
    """Parse the installed Harbor format and retain its reward-valid policy."""
    root = Path(trial_dir)
    config = _read_json(root / "config.json") or {}
    data = _read_json(root / "result.json") or {}
    lock = _read_json(root / "lock.json") or {}
    task = lock.get("task") or {}
    agent_result = data.get("agent_result") or {}
    contexts = ([agent_result] if agent_result else [
        step["agent_result"] for step in data.get("step_results") or []
        if step.get("agent_result")
    ])
    usage = {}
    for field in ("n_input_tokens", "n_cache_tokens", "n_output_tokens", "cost_usd"):
        values = [context.get(field) for context in contexts]
        usage[field] = sum(values) if values and all(v is not None for v in values) else None
    native = _read_json(root / "agent" / "mini-swe-agent.trajectory.json") or {}
    if not contexts and native:
        messages = [m for m in native.get("messages", [])
                    if m.get("role") == "assistant" or m.get("object") == "response"]
        raw_usage = [((m.get("extra") or {}).get("response") or {}).get("usage")
                     or m.get("usage") for m in messages]
        for field, candidates in (("n_input_tokens", ("prompt_tokens", "input_tokens")),
                                  ("n_output_tokens", ("completion_tokens", "output_tokens"))):
            values = [next((u[k] for k in candidates if k in u), None) if u else None
                      for u in raw_usage]
            usage[field] = sum(values) if values and all(v is not None for v in values) else None
        usage["cost_usd"] = ((native.get("info") or {}).get("model_stats") or {}).get("instance_cost")
    metadata = agent_result.get("metadata") or native.get("info") or {}
    row: dict[str, Any] = {
        "trial_dir": str(root), "trial_id": data.get("id"),
        "trial_name": data.get("trial_name") or config.get("trial_name"), "job_id": config.get("job_id"),
        "task_id": data.get("task_id") or config.get("task"), "task_name": data.get("task_name"),
        "task_version": task.get("version"), "task_digest": task.get("digest"),
        "task_git_sha": task.get("git_commit_id"), "task_source": task.get("source"),
        "task_checksum": data.get("task_checksum"),
        "agent_info": data.get("agent_info"), "environment": config.get("environment"),
        "status": "NOT_EVALUATED", "reward": None, "rewards": None,
        "success": None, "error": data.get("exception_info"), "reason": "",
        "usage": usage, "model_usage": agent_result.get("model_usage"),
        **usage, "duration_sec": _seconds(data), "verifier_path": None,
        "native_trace_path": str(root / "agent" / "mini-swe-agent.trajectory.json") if native else None,
        "router_fallback_used": metadata.get("fallback_used"),
        "agent_metadata": metadata,
        "policy_implementation_status": metadata.get("policy_implementation_status"),
        "untested_native_efforts_used": metadata.get("untested_native_efforts_used"),
        "neural_router_evidence_eligible": metadata.get("neural_router_evidence_eligible"),
        "cost_statuses": metadata.get("cost_statuses"),
        "actual_billed_cost_usd": metadata.get("actual_billed_cost_usd"),
        "started_at": data.get("started_at"), "finished_at": data.get("finished_at"),
        "episode_wall_s": _seconds(data),
        "phase_wall_s": {key: _seconds(data.get(key)) for key in (
            "environment_setup", "agent_setup", "agent_execution", "verifier")},
        "verifier_artifacts": [], "trace": read_trace(root),
        "runtime_log": str(root / "trial.log") if (root / "trial.log").is_file() else None,
        "evidence_scope": "recorded_artifact_agreement",
    }
    if not config or not data or not lock:
        row["reason"] = "Missing original Harbor config, result or lock"
        return row
    if not row["trial_id"] or not task.get("digest"):
        row["reason"] = "Original trial ID or task identity absent"
        return row
    # Harbor 0.24's lock digest and legacy task_checksum use different encodings.

    phases = data.get("step_results") or [data]
    for phase in phases:
        directory = root / "steps" / phase["step_name"] if phase.get("step_name") else root
        rewards = (phase.get("verifier_result") or {}).get("rewards")
        original, path = _reward_artifact(directory / "verifier")
        row["verifier_path"] = path
        row["verifier_artifacts"].append({
            "step_name": phase.get("step_name"), "reward_path": path,
            "rewards": original, "result_rewards": rewards,
            "stdout_path": str(directory / "verifier" / "test-stdout.txt")
            if (directory / "verifier" / "test-stdout.txt").is_file() else None,
            "ctrf_path": str(directory / "verifier" / "ctrf.json")
            if (directory / "verifier" / "ctrf.json").is_file() else None,
        })
        if original is None or not rewards or not (phase.get("verifier") or {}).get("finished_at"):
            row["reason"] = "Original verifier output or completed verifier timing absent"
            return row
        if not _same_rewards(original, rewards):
            row["status"] = "VERIFIER_MISMATCH"
            row["reason"] = "Trial result rewards differ from original verifier artifact"
            return row
        if row["task_name"] == "terminal-bench/fix-git" and not (directory / "verifier" / "ctrf.json").is_file():
            row["reason"] = "fix-git pytest CTRF report absent; verifier reward is not a measured task outcome"
            return row

    from harbor.models.trial.error_policy import policy_for

    exceptions = [p["exception_info"] for p in [data, *phases] if p.get("exception_info")]
    if any(not policy_for(e["exception_type"]).reward_valid for e in exceptions):
        row["reason"] = "Harbor classifies this exception as an invalid reward measurement"
        return row
    rewards = (data.get("verifier_result") or {}).get("rewards")
    if not rewards or not data.get("finished_at"):
        row["reason"] = "Final trial reward or completion absent"
        return row
    row.update(status="OFFICIAL_ARTIFACT_VERIFIED", rewards=rewards,
               reward=rewards.get("reward"), reason="Original Harbor task lock and verifier artifacts recorded")
    if row["reward"] in (0, 1):
        row["success"] = row["reward"] == 1
    return row


def audit_job(job_dir: str | Path) -> dict[str, Any]:
    """Read partial jobs as well as completed jobs; never invent Harbor IDs."""
    root = Path(job_dir)
    data = _read_json(root / "result.json") or {}
    config = _read_json(root / "config.json") or {}
    lock = _read_json(root / "lock.json") or {}
    # A running trial may not have a lock or result yet; keep it visible.
    trial_dirs = {p.parent for pattern in ("*/config.json", "*/result.json",
                  "trials/*/config.json", "trials/*/result.json") for p in root.glob(pattern)}
    rows = [audit_trial(path) for path in sorted(trial_dirs)]
    for row in rows:
        row["job_id"] = data.get("id") or row["job_id"]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    missing = [name for name in ("config.json", "result.json", "lock.json")
               if not (root / name).is_file()]
    status = "NOT_EVALUATED"
    if not missing and data.get("id") and rows:
        status = "RUNNING" if not data.get("finished_at") else "PARTIAL_OR_UNVERIFIED"
        if (data.get("finished_at") and len(rows) == data.get("n_total_trials")
                and counts.get("OFFICIAL_ARTIFACT_VERIFIED") == len(rows)):
            status = "OFFICIAL_ARTIFACT_VERIFIED"
    return {
        "job_dir": str(root), "job_id": data.get("id"),
        "job_name": config.get("job_name"), "harbor": lock.get("harbor"),
        "status": status, "missing_job_files": missing, "trials": rows, "counts": counts,
        "n_total_trials": data.get("n_total_trials"), "stats": data.get("stats"),
        "started_at": data.get("started_at"), "finished_at": data.get("finished_at"),
        "job_wall_s": _seconds(data),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read original Harbor verifier artifacts")
    parser.add_argument("job_dir")
    parser.add_argument("--output", type=Path)
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
