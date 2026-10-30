"""Protected Experiment Ledger and Run Artifact Management.

Implements the strict V8 §7.5 schema:
Per-episode directory:
  runs/agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/
    ├── run_manifest.json
    ├── decisions.jsonl
    ├── model_calls.jsonl
    ├── tools.jsonl
    ├── events.jsonl
    └── episode.json

Global aggregate ledgers:
  experiments/agent_pilot/ledgers/
    ├── experiments_ledger.jsonl
    ├── experiments_ledger.csv
    └── summary.json
"""
from __future__ import annotations

import csv
import fcntl
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    try:
        from modelrouter.agent.agent import EpisodeResult
    except ImportError:
        from experiments.agent_pilot.agent import EpisodeResult

logger = logging.getLogger("modelrouter.telemetry.ledger")

_LEDGER_LOCK = threading.Lock()


def _find_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "experiments" / "agent_pilot" / "token_budget.json").is_file():
            return parent
    return Path.cwd()


class ExperimentLedger:
    """Manages writing of run artifacts and aggregate ledgers."""

    def __init__(
        self,
        runs_root: Optional[str | Path] = None,
        ledgers_root: Optional[str | Path] = None,
        pricing_sha256: str = "v8-pricing-sha",
    ):
        base_dir = _find_project_root()
        self.runs_root = Path(runs_root or base_dir / "runs" / "agent_pilot")
        self.ledgers_root = Path(ledgers_root or base_dir / "experiments" / "agent_pilot" / "ledgers")
        self.pricing_sha256 = pricing_sha256

        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.ledgers_root.mkdir(parents=True, exist_ok=True)

    def record_episode(
        self,
        result: EpisodeResult,
        benchmark_name: str = "terminal-bench-2-1",
    ) -> Path:
        """Records an EpisodeResult into both the structured episode run directory
        and the global aggregate ledgers.
        """
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y%m%d")
        details = result.evaluator_details or {}
        router_fallback = any(d.get("fallback_used", False) for d in result.router_decisions)
        official = {}
        if details.get("trial_dir"):
            from modelrouter.benchmark.official_artifacts import audit_trial
            official = audit_trial(details["trial_dir"])
        official_evaluated = official.get("status") == "OFFICIAL_ARTIFACT_VERIFIED"
        provenance = {
            "evaluation_status": "EVALUATED" if official_evaluated else "NOT_EVALUATED",
            "router_evidence_status": "ROUTER_FALLBACK" if router_fallback else "NO_REPORTED_FALLBACK",
            "official_result_eligible": official_evaluated and not router_fallback,
            "job_id": official.get("job_id"),
            "trial_id": official.get("trial_id"),
            "verifier_path": official.get("verifier_path"),
            "official_success": official.get("success") if official_evaluated else None,
        }

        # 1. Build episode folder
        # runs/agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/
        ep_dir = (
            self.runs_root
            / date_str
            / benchmark_name
            / result.policy_id
            / result.task_id
            / str(result.seed)
        )
        ep_dir.mkdir(parents=True, exist_ok=True)

        # 1.1 run_manifest.json
        manifest = {
            "benchmark": benchmark_name,
            "task_id": result.task_id,
            "policy_id": result.policy_id,
            "seed": result.seed,
            "pricing_sha256": self.pricing_sha256,
            "recorded_at": now.isoformat(),
            "status": result.status,
            "resolved": result.resolved,
            "score": result.score,
            **provenance,
        }
        with open(ep_dir / "run_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # 1.2 decisions.jsonl
        with open(ep_dir / "decisions.jsonl", "w", encoding="utf-8") as f:
            for dec in result.router_decisions:
                f.write(json.dumps(dec) + "\n")

        # 1.3 model_calls.jsonl and tools.jsonl and events.jsonl
        with open(ep_dir / "model_calls.jsonl", "w", encoding="utf-8") as f_model:
            with open(ep_dir / "tools.jsonl", "w", encoding="utf-8") as f_tool:
                with open(ep_dir / "events.jsonl", "w", encoding="utf-8") as f_event:
                    for step in result.step_traces:
                        # Model call record
                        model_rec = {
                            "step_index": step["step_index"],
                            "action": step["selected_action"],
                            "prompt_tokens": step["prompt_tokens"],
                            "completion_tokens": step["completion_tokens"],
                            "reasoning_tokens": step["reasoning_tokens"],
                            "cached_tokens": step["cached_tokens"],
                            "cost_usd": step["step_cost_usd"],
                            "episode_step_duration_sec": step["step_duration_sec"],
                            "generator_latency_ms": step.get("generator_latency_ms"),
                            "requested_model_id": step["selected_action"].get("model"),
                            "returned_model_id": step.get("returned_model_id"),
                            "raw_usage": step.get("raw_usage"),
                            "ttft_ms": step.get("ttft_ms"),
                            "output_tokens_per_s": step.get("output_tokens_per_s"),
                            "cost_status": step.get("cost_status", "UNVERIFIED_LEGACY"),
                        }
                        f_model.write(json.dumps(model_rec) + "\n")

                        # Tool execution record
                        tool_rec = {
                            "step_index": step["step_index"],
                            "command": step["tool_action"],
                            "exit_code": step["tool_exit_code"],
                            "duration_ms": step.get("tool_duration_ms"),
                            "observation_snippet": step["tool_observation"][:200],
                        }
                        f_tool.write(json.dumps(tool_rec) + "\n")

                        # Timeline event
                        event_rec = {
                            "step_index": step["step_index"],
                            "phase": step["phase"],
                            "model": step["selected_action"].get("model"),
                            "native_effort": step["selected_action"].get("native_effort"),
                            "action": step["tool_action"],
                            "exit_code": step["tool_exit_code"],
                            "timestamp": step["timestamp"],
                        }
                        f_event.write(json.dumps(event_rec) + "\n")

        # 1.4 episode.json
        with open(ep_dir / "episode.json", "w", encoding="utf-8") as f:
            json.dump({**result.to_dict(), **provenance}, f, indent=2)

        # 1.5 Official Verifier Artifacts (CTRF, reward, verifier output)
        if isinstance(result.evaluator_details, dict):
            import shutil
            ctrf_p = result.evaluator_details.get("ctrf_path")
            if ctrf_p and os.path.exists(ctrf_p):
                shutil.copy(ctrf_p, ep_dir / "ctrf.json")
            reward_p = result.evaluator_details.get("reward_path")
            if reward_p and os.path.exists(reward_p):
                shutil.copy(reward_p, ep_dir / "reward.txt")
            if "ctrf_summary" in result.evaluator_details:
                with open(ep_dir / "verifier_summary.json", "w", encoding="utf-8") as f_vs:
                    json.dump(result.evaluator_details["ctrf_summary"], f_vs, indent=2)

        summary_entry = {
                "recorded_at": now.isoformat(),
                "date": date_str,
                "benchmark": benchmark_name,
                "task_id": result.task_id,
                "episode_id": result.episode_id,
                "policy_id": result.policy_id,
                "seed": result.seed,
                "status": result.status,
                "resolved": result.resolved,
                "score": result.score,
                "total_steps": result.total_steps,
                "elapsed_time_sec": result.elapsed_time_sec,
                "total_cost_usd": result.total_cost_usd,
                "total_prompt_tokens": result.total_prompt_tokens,
                "total_completion_tokens": result.total_completion_tokens,
                "total_reasoning_tokens": result.total_reasoning_tokens,
                "total_cached_tokens": result.total_cached_tokens,
                "run_dir": str(ep_dir),
                **provenance,
        }
        self._append_summary(summary_entry)
        return ep_dir

    def record_official_trial(self, trial: dict, *, events_path: Path) -> None:
        """Index a completed collect_trials row, retaining the original Harbor source."""
        if not trial.get("trial_id") or not trial.get("finished_at"):
            return
        metadata = trial.get("agent_metadata") or {}
        evaluated = trial["status"] == "OFFICIAL_ARTIFACT_VERIFIED"
        fallback = trial.get("router_fallback_used") is True
        scientific = (evaluated and trial.get("agent") != "oracle" and not fallback
                      and not trial.get("untested_native_efforts_used")
                      and trial.get("policy_implementation_status") != "UNVERIFIED_EXAMPLE"
                      and trial.get("policy") not in ("routellm", "sr_knn")
                      and (trial.get("policy") not in ("laya_v2", "kev_4b", "joint_laya", "joint_kev")
                           and trial.get("policy_implementation_status") != "REMOTE_NEURAL_ROUTER"
                           or trial.get("neural_router_evidence_eligible") is True))
        billed = trial.get("actual_billed_cost_usd")
        components = [billed, metadata.get("sandbox_cost_usd"), metadata.get("router_compute_cost_usd")]
        full_cost = sum(components) if all(v is not None for v in components) else None
        self._append_summary({
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "benchmark": trial.get("benchmark", "terminal-bench-2-1"),
            "task_id": trial.get("task_id"), "episode_id": str(trial["trial_id"]),
            "policy_id": trial.get("policy"), "seed": trial.get("seed"),
            "agent": trial.get("agent"), "status": trial["status"],
            "resolved": trial.get("success") if evaluated else None,
            "score": trial.get("reward") if evaluated else None,
            "reward": trial.get("reward"), "rewards": trial.get("rewards"),
            "evaluation_status": "EVALUATED" if evaluated else "NOT_EVALUATED",
            "official_result_eligible": evaluated,
            "scientific_result_eligible": scientific,
            "official_success": trial.get("success") if evaluated else None,
            "router_evidence_status": "ROUTER_FALLBACK" if fallback else "NO_REPORTED_FALLBACK",
            "job_id": trial.get("job_id"), "trial_id": str(trial["trial_id"]),
            "task_version": trial.get("task_version"), "task_git_sha": trial.get("task_git_sha"),
            "task_source": trial.get("task_source"), "task_digest": trial.get("task_digest"),
            "task_checksum": trial.get("task_checksum"), "verifier_path": trial.get("verifier_path"),
            "verifier_artifacts": trial.get("verifier_artifacts"),
            "trial_dir": trial["trial_dir"], "run_dir": trial["trial_dir"],
            "official_source": str(Path(trial["trial_dir"]) / "result.json"),
            "events_path": str(events_path), "trace_files": (trial.get("trace") or {}).get("files", []),
            "tool_calls_path": str(events_path.parent / "tool_calls.jsonl"),
            "native_trace_path": trial.get("native_trace_path"), "model_usage": trial.get("model_usage"),
            "source_kind": "HARBOR_ORIGINAL_TRIAL", "evidence_scope": trial.get("evidence_scope"),
            "reason": trial.get("reason"), "error": trial.get("error"),
            "started_at": trial.get("started_at"), "finished_at": trial["finished_at"],
            "total_steps": len((trial.get("trace") or {}).get("steps", [])) or None,
            "elapsed_time_sec": trial.get("duration_sec"),
            "total_cost_usd": full_cost, "generator_cost_usd": trial.get("cost_usd"),
            "cost_statuses": trial.get("cost_statuses"),
            "generator_cost_source": "harbor_agent_context; not an invoice",
            "actual_billed_cost_usd": billed, "sandbox_cost_usd": components[1],
            "router_compute_cost_usd": components[2],
            "total_prompt_tokens": trial.get("n_input_tokens"),
            "total_completion_tokens": trial.get("n_output_tokens"),
            "total_cached_tokens": trial.get("n_cache_tokens"),
            "agent_metadata": metadata,
        })

    def record_development_episode(self, result: dict) -> None:
        """Index local evidence in the original ledger without copying its files."""
        self._append_summary({**result, "official_result_eligible": False,
                              "scientific_result_eligible": False,
                              "official_success": None,
                              "router_evidence_status": "ROUTER_FALLBACK" if result.get("router_fallback_used")
                                                       else "NO_REPORTED_FALLBACK"})

    def _append_summary(self, summary_entry: dict) -> None:
        """Share the existing JSONL/CSV ledger; a Harbor Trial ID is recorded once."""
        jsonl_path = self.ledgers_root / "experiments_ledger.jsonl"
        with _LEDGER_LOCK, jsonl_path.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            if summary_entry.get("trial_id"):
                stream.seek(0)
                if any(json.loads(line).get("trial_id") == summary_entry["trial_id"]
                       for line in stream if line.strip()):
                    return
            stream.write(json.dumps(summary_entry) + "\n")
            stream.flush()
            csv_path = self.ledgers_root / "experiments_ledger.csv"
            write_header = not csv_path.exists() or csv_path.stat().st_size == 0
            fieldnames = list(summary_entry.keys())
            if not write_header:
                with csv_path.open(newline="", encoding="utf-8") as existing:
                    reader = csv.DictReader(existing)
                    prior_fields = reader.fieldnames
                    fieldnames = list(dict.fromkeys(prior_fields + fieldnames))
                    rows = list(reader) if prior_fields != fieldnames else None
                if rows is not None:
                    with csv_path.open("w", newline="", encoding="utf-8") as existing:
                        writer = csv.DictWriter(existing, fieldnames=fieldnames, lineterminator="\n")
                        writer.writeheader()
                        writer.writerows(rows)
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
                if write_header:
                    writer.writeheader()
                writer.writerow(summary_entry)

            self._update_summary_json(jsonl_path)

    def _update_summary_json(self, jsonl_path: Path) -> None:
        """Reads all completed episodes from JSONL and generates aggregate statistics."""
        if not jsonl_path.is_file():
            return

        total_episodes = 0
        resolved_count = 0
        total_cost_usd = 0.0
        known_cost_count = 0
        total_steps = 0
        total_time_sec = 0.0
        known_steps_count = 0
        known_time_count = 0
        policy_stats: Dict[str, Dict[str, Any]] = {}
        router_fallback_count = 0
        official_count = 0
        official_resolved = 0
        official_binary_count = 0

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                total_episodes += 1
                if d.get("resolved"):
                    resolved_count += 1
                router_fallback_count += int(d.get("router_evidence_status") == "ROUTER_FALLBACK")
                if d.get("official_result_eligible"):
                    official_count += 1
                    official_binary_count += int(d.get("official_success") is not None)
                    official_resolved += int(d.get("official_success") is True)
                cost = d.get("total_cost_usd")
                if cost is not None:
                    total_cost_usd += cost
                    known_cost_count += 1
                steps = d.get("total_steps")
                duration = d.get("elapsed_time_sec")
                if steps is not None:
                    total_steps += steps
                    known_steps_count += 1
                if duration is not None:
                    total_time_sec += duration
                    known_time_count += 1

                pol = d.get("policy_id", "unknown")
                if pol not in policy_stats:
                    policy_stats[pol] = {"total": 0, "resolved": 0, "cost_usd": 0.0, "steps": 0, "known_cost_count": 0, "official_count": 0, "official_resolved": 0, "official_binary_count": 0}
                if d.get("official_result_eligible"):
                    policy_stats[pol]["official_count"] += 1
                    policy_stats[pol]["official_binary_count"] += int(d.get("official_success") is not None)
                    policy_stats[pol]["official_resolved"] += int(d.get("official_success") is True)
                policy_stats[pol]["total"] += 1
                if d.get("resolved"):
                    policy_stats[pol]["resolved"] += 1
                if cost is not None:
                    policy_stats[pol]["cost_usd"] += cost
                    policy_stats[pol]["known_cost_count"] += 1
                if steps is not None:
                    policy_stats[pol]["steps"] += steps

        pass_rate = resolved_count / total_episodes if total_episodes > 0 else 0.0
        cost_complete = total_episodes > 0 and known_cost_count == total_episodes
        mean_steps = total_steps / total_episodes if total_episodes > 0 else 0.0
        mean_time = total_time_sec / total_episodes if total_episodes > 0 else 0.0

        for pol, st in policy_stats.items():
            tot = st["total"]
            st["legacy_pass_at_1"] = round(st["resolved"] / tot, 4) if tot > 0 else 0.0
            st["pass_at_1"] = st["official_resolved"] / st["official_binary_count"] if st["official_binary_count"] else None
            complete = st["known_cost_count"] == tot
            st["mean_cost_usd"] = round(st["cost_usd"] / tot, 4) if complete else None
            st["cost_usd"] = round(st["cost_usd"], 4) if complete else None

        summary = {
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "total_episodes": total_episodes,
            "resolved_count": resolved_count,
            "legacy_pass_at_1": round(pass_rate, 4),
            "pass_at_1": official_resolved / official_binary_count if official_binary_count else None,
            "official_count": official_count,
            "official_resolved": official_resolved,
            "router_fallback_count": router_fallback_count,
            "total_cost_usd": round(total_cost_usd, 4) if cost_complete else None,
            "mean_cost_usd": round(total_cost_usd / total_episodes, 4) if cost_complete else None,
            "known_cost_episodes": known_cost_count,
            "mean_steps_per_episode": round(mean_steps, 2) if known_steps_count == total_episodes else None,
            "mean_duration_sec": round(mean_time, 2) if known_time_count == total_episodes else None,
            "policy_breakdown": policy_stats,
        }

        with open(self.ledgers_root / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
