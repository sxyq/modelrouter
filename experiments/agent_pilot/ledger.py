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
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from experiments.agent_pilot.agent import EpisodeResult

logger = logging.getLogger("experiments.agent_pilot.ledger")

_LEDGER_LOCK = threading.Lock()


class ExperimentLedger:
    """Manages writing of run artifacts and aggregate ledgers."""

    def __init__(
        self,
        runs_root: Optional[str | Path] = None,
        ledgers_root: Optional[str | Path] = None,
        pricing_sha256: str = "v8-pricing-sha",
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
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
                            "latency_sec": step["step_duration_sec"],
                        }
                        f_model.write(json.dumps(model_rec) + "\n")

                        # Tool execution record
                        tool_rec = {
                            "step_index": step["step_index"],
                            "command": step["tool_action"],
                            "exit_code": step["tool_exit_code"],
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
            json.dump(result.to_dict(), f, indent=2)

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

        # 2. Append to Global Aggregate Ledgers (Thread-safe)
        with _LEDGER_LOCK:
            # 2.1 experiments_ledger.jsonl
            jsonl_path = self.ledgers_root / "experiments_ledger.jsonl"
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
            }
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(summary_entry) + "\n")

            # 2.2 experiments_ledger.csv
            csv_path = self.ledgers_root / "experiments_ledger.csv"
            write_header = not csv_path.exists() or csv_path.stat().st_size == 0
            fieldnames = list(summary_entry.keys())
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                writer.writerow(summary_entry)

            # 2.3 Recompute and write summary.json
            self._update_summary_json(jsonl_path)

        return ep_dir

    def _update_summary_json(self, jsonl_path: Path) -> None:
        """Reads all completed episodes from JSONL and generates aggregate statistics."""
        if not jsonl_path.is_file():
            return

        total_episodes = 0
        resolved_count = 0
        total_cost_usd = 0.0
        total_steps = 0
        total_time_sec = 0.0
        policy_stats: Dict[str, Dict[str, Any]] = {}
        router_fallback_count = 0

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                total_episodes += 1
                if d.get("resolved"):
                    resolved_count += 1
                cost = d.get("total_cost_usd", 0.0)
                total_cost_usd += cost
                total_steps += d.get("total_steps", 0)
                total_time_sec += d.get("elapsed_time_sec", 0.0)

                pol = d.get("policy_id", "unknown")
                if pol not in policy_stats:
                    policy_stats[pol] = {"total": 0, "resolved": 0, "cost_usd": 0.0, "steps": 0}
                policy_stats[pol]["total"] += 1
                if d.get("resolved"):
                    policy_stats[pol]["resolved"] += 1
                policy_stats[pol]["cost_usd"] = round(policy_stats[pol]["cost_usd"] + cost, 4)
                policy_stats[pol]["steps"] += d.get("total_steps", 0)

        pass_rate = resolved_count / total_episodes if total_episodes > 0 else 0.0
        mean_cost = total_cost_usd / total_episodes if total_episodes > 0 else 0.0
        mean_steps = total_steps / total_episodes if total_episodes > 0 else 0.0
        mean_time = total_time_sec / total_episodes if total_episodes > 0 else 0.0

        for pol, st in policy_stats.items():
            tot = st["total"]
            st["pass_at_1"] = round(st["resolved"] / tot, 4) if tot > 0 else 0.0
            st["mean_cost_usd"] = round(st["cost_usd"] / tot, 4) if tot > 0 else 0.0

        summary = {
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "total_episodes": total_episodes,
            "resolved_count": resolved_count,
            "pass_at_1": round(pass_rate, 4),
            "total_cost_usd": round(total_cost_usd, 4),
            "mean_cost_usd": round(mean_cost, 4),
            "mean_steps_per_episode": round(mean_steps, 2),
            "mean_duration_sec": round(mean_time, 2),
            "policy_breakdown": policy_stats,
        }

        with open(self.ledgers_root / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
