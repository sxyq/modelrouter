#!/usr/bin/env python3
"""Aggregate RQ1 and observed research factors from official Harbor evidence."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
from modelrouter.providers.usage import known_request_cost, request_decision_id


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculates Wilson score confidence interval for binomial proportion."""
    if total <= 0:
        return (0.0, 0.0)
    z = 1.95996  # 95% confidence
    p = successes / total
    denom = 1.0 + (z**2) / total
    center = (p + (z**2) / (2 * total)) / denom
    spread = z * math.sqrt((p * (1 - p) + (z**2) / (4 * total)) / total) / denom
    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return (round(lower, 4), round(upper, 4))


def analyze_rq1(episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize recorded episode values without estimating missing measurements."""
    from .iterations import percentile

    grouped = defaultdict(list)
    for ep in episodes:
        grouped[ep["policy_id"]].append(ep)

    table3_rows, table10_rows, pareto_candidates = [], [], []
    for policy, rows in grouped.items():
        n = len(rows)
        successes = sum(bool(row["resolved"]) for row in rows)
        costs = [row.get("total_cost_usd") for row in rows]
        total_cost = sum(costs) if all(cost is not None for cost in costs) else None
        rate = successes / n
        latency = [row.get("router_latency_ms") for row in rows]
        latency = [value for value in latency if isinstance(value, (int, float))]
        mean_cost = total_cost / n if total_cost is not None else None
        table3_rows.append({
            "policy_id": policy, "episodes": n, "resolved": successes,
            "task_success_rate": rate, "ci_95_success": wilson_score_interval(successes, n),
            "mean_episode_usd": mean_cost,
            "cost_per_resolved": total_cost / successes if total_cost is not None and successes else None,
            "p95_time_sec": percentile([row.get("elapsed_time_sec") for row in rows], .95),
            "router_latency_ms": percentile(latency, .5),
            "router_cost_usd": (sum(row["router_cost_usd"] for row in rows) / n
                                if all(row.get("router_cost_usd") is not None for row in rows) else None),
        })
        unresolved = [row.get("total_cost_usd") for row in rows if not row["resolved"]]
        table10_rows.append({
            "policy_id": policy,
            "unresolved_episode_cost_usd": sum(unresolved) if all(v is not None for v in unresolved) else None,
            "router_cost_usd": table3_rows[-1]["router_cost_usd"],
            "mean_trace_steps": (sum(row["total_steps"] for row in rows) / n
                                 if all(row.get("total_steps") is not None for row in rows) else None),
            "total_episode_usd": mean_cost,
        })
        if mean_cost is not None:
            pareto_candidates.append({"policy_id": policy, "x_cost_usd": mean_cost,
                                      "y_success_rate": rate})

    # Identify Pareto optimal points (maximize success, minimize cost)
    # A point (c, s) is dominated if there exists another (c', s') such that c' <= c and s' >= s (with at least one strict)
    for cand in pareto_candidates:
        c = cand["x_cost_usd"]
        s = cand["y_success_rate"]
        dominated = False
        for other in pareto_candidates:
            if other == cand:
                continue
            oc = other["x_cost_usd"]
            os_ = other["y_success_rate"]
            if oc <= c and os_ >= s and (oc < c or os_ > s):
                dominated = True
                break
        cand["is_pareto_optimal"] = not dominated

    pareto_frontier = [c for c in pareto_candidates if c["is_pareto_optimal"]]
    pareto_frontier.sort(key=lambda p: p["x_cost_usd"])

    return {
        "data_origin": "RECORDED_EPISODE_VALUES",
        "publication_eligible": False,
        "total_episodes_analyzed": len(episodes),
        "table3_main_results": table3_rows,
        "table10_cost_ledger": table10_rows,
        "fig3_pareto_frontier": {
            "all_points": pareto_candidates,
            "pareto_optimal_points": pareto_frontier,
            "x_axis": "Mean Complete Episode USD",
            "y_axis": "Task Success Rate (Pass@1)",
        },
        "fig4_cost_decomposition": table10_rows,
    }


def provider_requests(trial, events):
    events_by_episode = defaultdict(list)
    for event in events:
        if event.get('episode_id') is not None:
            events_by_episode[str(event['episode_id'])].append(event)
    episode = str(trial.get("trial_id") or next((e["episode_id"] for e in events if e.get("event") == "AGENT_START"), None))
    metadata = trial.get("agent_metadata") or {}
    recorded = {}
    for item in events_by_episode[episode]:
        kind = item.get("event")
        if kind not in ("GENERATOR_END", "TEACHER_END", "TEACHER_ERROR") and not (
                kind == "ERROR" and item.get("category") == "PROVIDER"):
            continue
        if kind == "TEACHER_ERROR" and not item.get("provider_request_attempted", True):
            continue
        role = "teacher" if kind.startswith("TEACHER") or item.get("role") == "teacher" else "generator"
        identity = request_decision_id(item) or (kind, len(recorded))
        key = (role, identity)
        recorded[key] = {**recorded.get(key, {}), **item, "role": role}
    for source, role, items in (("generator", "generator", metadata.get("provider_metrics", [])),
                                ("failure", "generator", metadata.get("provider_failures", []))):
        for index, item in enumerate(items):
            identity = request_decision_id(item) or (source, index)
            key = (role, identity)
            row = {**recorded.get(key, {}), **item, "role": role}
            row.setdefault("event", "ERROR" if source == "failure" else "GENERATOR_END")
            recorded[key] = row
    v9 = metadata.get("v9") or {}
    for index, item in enumerate(v9.get("teacher_metrics", [])):
        if item.get("provider_request_attempted", True):
            identity = request_decision_id(item) or ("teacher", index)
            key = ("teacher", identity)
            row = {**recorded.get(key, {}), **item, "role": "teacher"}
            row.setdefault("event", "TEACHER_END")
            recorded[key] = row
    ended = {
        "generator": {request_decision_id(item) for item in recorded.values()
                      if item.get("role") == "generator" and item.get("event") in ("GENERATOR_END", "ERROR")},
        "teacher": {request_decision_id(item) for item in recorded.values()
                    if item.get("role") == "teacher" and item.get("event") in ("TEACHER_END", "TEACHER_ERROR")},
    }
    for item in events_by_episode[episode]:
        kind = item.get("event")
        if kind not in ("GENERATOR_START", "TEACHER_START"):
            continue
        role = "generator" if kind == "GENERATOR_START" else "teacher"
        decision_id = item.get("decision_id")
        if decision_id not in ended[role]:
            key = (role, decision_id)
            recorded[key] = {**recorded.get(key, {}), "event": "ERROR", "cost_usd": None,
                             "role": role, "decision_id": decision_id}
    return list(recorded.values())


def export_official_results(iteration_dir: Path) -> Dict[str, Any]:
    """Aggregate Harbor outcomes and the costs recorded by each Provider response."""
    from .iterations import collect_trials, rows, write_atomic, percentile

    raw = collect_trials(iteration_dir)
    usable = [r for r in raw if r["status"] == "OFFICIAL_ARTIFACT_VERIFIED"
              and r.get("agent") != "oracle" and not r.get("router_fallback_used")
              and r.get("reward") in (0, 1)
              and r.get("policy_implementation_status") != "UNVERIFIED_EXAMPLE"
              and r.get("policy") not in ("routellm", "sr_knn", "laya_v2", "kev_4b")
              and (r.get("policy") not in ("joint_laya", "joint_kev")
                   or r.get("neural_router_evidence_eligible") is True)]
    events = rows(iteration_dir / "events.jsonl")
    by_policy = defaultdict(list)
    for trial in usable:
        by_policy[trial["policy"]].append(trial)
    trial_requests = {str(trial["trial_id"]): provider_requests(trial, events) for trial in raw
                      if trial.get("trial_id")}
    table3, table10 = [], []
    for policy, trials in by_policy.items():
        n = len(trials)
        successes = sum(t["reward"] == 1 for t in trials)
        requests = [request for trial in trials for request in trial_requests[str(trial["trial_id"])] ]
        costs = [request.get("cost_usd") for request in requests]
        costs_known = bool(costs) and all(c is not None for c in costs)
        ids = {str(t["trial_id"]) for t in trials}
        calls = [e for e in events if e["event"] == "GENERATOR_END" and str(e.get("episode_id")) in ids]
        routing = [e for e in events if e["event"] == "ROUTER_END" and e.get("episode_id") in ids]
        table3.append({
            "policy": policy, "episodes": n, "successes": successes,
            "success_rate": successes / n, "ci95": wilson_score_interval(successes, n),
            "provider_recorded_mean_usd": sum(costs) / n if costs_known and n else None,
            "provider_recorded_cost_per_success_usd": sum(costs) / successes if costs_known and successes else None,
            "complete_cost_usd": None,
            "episode_p95_s": percentile([t.get("duration_sec") for t in trials], .95),
            "router_p50_ms": percentile([r.get("router_latency_ms") for r in routing], .5),
            "router_p95_ms": percentile([r.get("router_latency_ms") for r in routing], .95),
            "trial_ids": sorted(ids), "verifier_paths": [t["verifier_path"] for t in trials],
        })
    attempted_by_policy = defaultdict(list)
    for trial in raw:
        if (trial.get("agent") != "oracle" and trial.get("policy")
                and trial.get("policy") not in ("routellm", "sr_knn", "laya_v2", "kev_4b")
                and trial.get("policy_implementation_status") != "UNVERIFIED_EXAMPLE"):
            attempted_by_policy[trial["policy"]].extend(trial_requests.get(str(trial.get("trial_id")), []))
    table10 = []
    for policy, requests in attempted_by_policy.items():
        costs = [request.get("cost_usd") for request in requests]
        known_costs = [known_request_cost(request) for request in requests]
        failed = [request for request in requests if request.get("event") in ("ERROR", "TEACHER_ERROR")
                  or request.get("status") not in (None, "RECORDED", "SUCCESS")]
        known_failed_costs = [known_request_cost(request) for request in failed]
        calls = [request for request in requests if request.get("event") == "GENERATOR_END"]
        sources = {(request.get("cost_model_id"), request.get("cost_source"), request.get("cost_status"))
                   for request in requests}
        sources.update((attempt.get("cost_model_id"), attempt.get("cost_source"), attempt.get("cost_status"))
                       for request in requests for attempt in request.get("account_attempts", []))
        table10.append({"policy": policy,
                        "provider_recorded_cost_usd": sum(costs) if costs and all(c is not None for c in costs) else None,
                        "known_provider_recorded_cost_usd": sum(c for c in known_costs if c is not None) if any(c is not None for c in known_costs) else None,
                        "failed_provider_cost_usd": (sum(request.get("cost_usd") for request in failed)
                                                      if all(request.get("cost_usd") is not None for request in failed) else None),
                        "known_failed_provider_cost_usd": (sum(c for c in known_failed_costs if c is not None)
                                                            if any(c is not None for c in known_failed_costs) else None),
                        "failed_provider_request_count": len(failed),
                        "unknown_provider_cost_request_count": sum(c is None for c in costs),
                        "provider_cost_sources": sorted(sources, key=str),
                        "input_tokens": sum(c["prompt_tokens"] for c in calls) if calls and all(c.get("prompt_tokens") is not None for c in calls) else None,
                        "output_tokens": sum(c["completion_tokens"] for c in calls) if calls and all(c.get("completion_tokens") is not None for c in calls) else None})
    task_sets = [{t.get("task_name") or str(t.get("task_id")) for t in v} for v in by_policy.values()]
    paired = len(task_sets) > 1 and all(s == task_sets[0] for s in task_sets)
    output = {
        "data_origin": "OFFICIAL_HARBOR_TRIALS", "status": "PARTIAL" if usable else "NOT_EVALUATED",
        "publication_eligible": False, "paired_task_sets": paired,
        "table3": table3, "table10": table10,
        "fig3": [{"policy": r["policy"], "success_rate": r["success_rate"],
                  "provider_recorded_mean_usd": r["provider_recorded_mean_usd"]} for r in table3],
        "fig4": table10,
        "pending": {
            "RQ1": "Need paired task/seed sets, attributable model identities and full infrastructure billing",
            "RQ2_Table6_Fig5": "Need repeated official trials grouped by registry-derived Model×Native Effort action sets",
            "RQ3_Table7_Fig6": "Need repeated official trials at declared single-agent decomposition settings",
            "RQ4_Table4_Table5_Table8_Table11_Fig7": "Need observed ablation and checkpoint assignments",
            "RQ5_Table9_Fig8": "Need workload labels independent of outcomes and paired observed costs",
        },
        "excluded": [{"trial_id": r.get("trial_id"), "status": r["status"],
                      "policy": r.get("policy")} for r in raw if r not in usable],
    }
    output.update(observed_research_groups(usable, events, trial_requests))
    from .rq3_analysis import compute_decomposition_benchmarks
    output["rq3_single_agent_observations"] = compute_decomposition_benchmarks(raw, events)
    grain = output["rq3_single_agent_observations"]
    grain["granularity_comparisons"] = [r for r in output["table7"] if r["paired_task_seed_sets"]]
    grain["granularity_comparison_status"] = "RECORDED_OFFICIAL_RESULTS" if grain["granularity_comparisons"] else "NOT_EVALUATED"
    destination = iteration_dir / "analysis"
    write_atomic(destination / "official_results.json", output)
    for number in range(3, 12):
        name = f"table{number}"
        records = output.get(name, [])
        write_atomic(destination / f"{name}.json", records)
        with (destination / f"{name}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]) if records else ["status"])
            writer.writeheader()
            writer.writerows(records)
    for number in range(3, 9):
        write_atomic(destination / f"fig{number}.json", output.get(f"fig{number}", []))
    return output


def observed_research_groups(trials, events, request_rows):
    """Group only declared experimental factors and observed official outcomes."""
    from .iterations import percentile

    def label(trial, field):
        decisions = [e for e in events if e.get("event") in ("ROUTER_END", "ROUTER_REUSE")
                     and str(e.get("episode_id")) == str(trial.get("trial_id"))]
        if field in ("granularity", "checkpoint_id", "information_ablation", "capability_snapshot_id", "teacher_enabled"):
            values = set()
            for row in decisions:
                pre = row.get("pre_decision_state") or {}
                values.add({"granularity": row.get("routing_granularity"),
                            "checkpoint_id": row.get("checkpoint_id"),
                            "information_ablation": tuple(pre.get("disabled_information_groups", [])),
                            "capability_snapshot_id": pre.get("capability_snapshot_id"),
                            "teacher_enabled": pre.get("teacher_status") != "DISABLED"}[field])
            return next(iter(values)) if len(values) == 1 else None
        if field == "model_effort_action_set":
            episode = str(trial.get("trial_id"))
            action_sets = {
                tuple(sorted((action.get("model") or action.get("model_id"),
                              action.get("native_effort")) for action in event.get("legal_actions", [])))
                for event in events if event.get("event") == "ROUTER_END"
                and str(event.get("episode_id")) == episode and event.get("legal_actions")
            }
            return next(iter(action_sets)) if len(action_sets) == 1 else None
        value = trial.get(field)
        if value is None:
            value = (trial.get("agent_metadata") or {}).get(field)
        return value

    def task_seed(trial):
        return (trial.get("task_name") or str(trial.get("task_id")), trial.get("seed"),
                trial.get("task_git_sha"), trial.get("task_digest"))

    def full_cost(trial):
        metadata = trial.get("agent_metadata") or {}
        parts = [trial.get("actual_billed_cost_usd"), metadata.get("sandbox_cost_usd"),
                 metadata.get("router_compute_cost_usd")]
        return sum(parts) if all(p is not None for p in parts) else None

    def summarize(group, labels):
        ids = {str(t["trial_id"]) for t in group}
        routed = [e for e in events if e["event"] == "ROUTER_END" and e.get("episode_id") in ids]
        calls = [e for e in events if e["event"] == "GENERATOR_END" and e.get("episode_id") in ids]
        success = sum(t["reward"] == 1 for t in group)
        requests = [r for t in group for r in request_rows[str(t["trial_id"])]]
        generator = [r.get("cost_usd") for r in requests if r["role"] == "generator"]
        teacher = [r.get("cost_usd") for r in requests if r["role"] == "teacher"]
        complete = [full_cost(t) for t in group]
        return {**labels, "episodes": len(group), "successes": success,
                "success_rate": success / len(group), "ci95": wilson_score_interval(success, len(group)),
                "generator_mean_usd": sum(generator) / len(group) if generator and all(c is not None for c in generator) else None,
                "teacher_mean_usd": sum(teacher) / len(group) if all(c is not None for c in teacher) else None,
                "actual_complete_mean_usd": sum(complete) / len(group) if all(c is not None for c in complete) else None,
                "actual_cost_per_success_usd": sum(complete) / success if success and all(c is not None for c in complete) else None,
                "episode_p95_s": percentile([t.get("duration_sec") for t in group], .95),
                "router_inference_p50_ms": percentile([r.get("inference_latency_ms") for r in routed], .5),
                "router_inference_p95_ms": percentile([r.get("inference_latency_ms") for r in routed], .95),
                "ttft_p50_ms": percentile([c.get("ttft_ms") for c in calls], .5),
                "output_tokens_per_s": percentile([c.get("output_tokens_per_s") for c in calls], .5),
                "execution_model": "singleAgent",
                "trial_ids": sorted(ids), "verifier_paths": [t["verifier_path"] for t in group],
                "data_origin": "OFFICIAL_HARBOR_TRIALS", "publication_eligible": False}

    result = {}
    factors = {"table6": ("model_effort_action_set",), "table7": ("granularity",),
               "table4": ("information_ablation",), "table5": ("action_ablation",),
               "table8": ("supervision_ablation",), "table11": ("checkpoint_id",),
               "teacher": ("teacher_enabled",)}
    controls = ("checkpoint_id", "capability_snapshot_id", "information_ablation", "teacher_enabled", "model_effort_action_set", "granularity")
    group_status = {}
    for table, fields in factors.items():
        grouped = defaultdict(list)
        for trial in trials:
            values = tuple(label(trial, f) for f in fields)
            if any(value is None for value in values):
                continue
            cohort = ((trial.get("agent_metadata") or {}).get("policy", trial["policy"]),
                      tuple((f, label(trial, f)) for f in controls if f not in fields))
            grouped[(cohort, *values)].append(trial)
        records = []
        for key, group in sorted(grouped.items(), key=lambda kv: str(kv[0])):
            same_policy = [v for k, v in grouped.items() if k[0] == key[0]]
            sets = [{task_seed(t) for t in v} for v in same_policy]
            paired = len(sets) > 1 and all(s == sets[0] for s in sets)
            records.append(summarize(group, {"policy": key[0][0], **dict(key[0][1]), **dict(zip(fields, key[1:])),
                                            "paired_task_seed_sets": paired}))
        result[table] = records
        group_status[table] = {"status": "PARTIAL" if records else "NOT_EVALUATED",
                               "required_observed_fields": list(fields)}

    workloads = defaultdict(list)
    for trial in trials:
        workload = label(trial, "workload")
        if workload is not None and label(trial, "workload_label_source") == "PRE_TASK_MANIFEST":
            workloads[workload].append(trial)
    comparisons = []
    for workload, group in workloads.items():
        fixed_groups = defaultdict(list)
        for trial in group:
            if trial["policy"] == "fixed_strong":
                fixed_groups[task_seed(trial)].append(trial)
        fixed = {key: records[0] for key, records in fixed_groups.items() if len(records) == 1}
        for policy in sorted({t["policy"] for t in group} - {"fixed_strong"}):
            routed_groups = defaultdict(list)
            for trial in group:
                if trial["policy"] == policy:
                    routed_groups[task_seed(trial)].append(trial)
            routed = {key: records[0] for key, records in routed_groups.items() if len(records) == 1}
            pairs = [(fixed[key], routed[key]) for key in sorted(fixed.keys() & routed.keys(), key=str)]
            if not pairs:
                continue
            delta = [b["reward"] - a["reward"] for a, b in pairs]
            costs = [full_cost(a) - full_cost(b) if full_cost(a) is not None and full_cost(b) is not None else None for a, b in pairs]
            comparisons.append({"workload": workload, "policy": policy, "paired_episodes": len(pairs),
                "delta_success_rate": sum(delta) / len(delta),
                "actual_mean_cost_saving_usd": sum(costs) / len(costs) if all(c is not None for c in costs) else None,
                "gain_boundary": None, "boundary_status": "NOT_ESTIMATED",
                "trial_pairs": [[a["trial_id"], b["trial_id"]] for a, b in pairs],
                "publication_eligible": False})
    result.update(table9=comparisons, fig5=result["table6"], fig6=result["table7"],
                  fig7={"information": result["table4"], "teacher": result["teacher"], "actions": result["table5"],
                        "supervision": result["table8"], "checkpoints": result["table11"]},
                  fig8=comparisons, observed_factor_status=group_status)
    return result


def export_batch_results(root, config, output_root=None):
    """Collect the same Provider and official facts, including unscored paid attempts."""
    from .iterations import rows, write_atomic, percentile
    output_root = root if output_root is None else output_root
    if output_root != root:
        from shutil import copyfile
        output_root.mkdir(parents=True, exist_ok=True)
        for name in ("config.json", "manifest.json", "jobs.jsonl", "metrics/resource_observations.json"):
            destination = output_root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            copyfile(root / name, destination)
    tasks = {t["task_id"]: t for t in config["tasks"]}
    strategies = {s["id"]: s for s in config["strategies"]}
    units = json.loads((root / "manifest.json").read_text())["units"]
    job_states = {r["unit_id"]: r for r in rows(root / "jobs.jsonl")}
    episodes = []
    for unit in units:
        relative = Path(unit["task_id"]) / unit["strategy_id"] / str(unit["seed"])
        public = output_root / "trials" / relative
        source_public = root / "trials" / relative
        private = root / ".private/episodes" / relative
        if (source_public / "summary.json").exists() and not private.exists():
            episodes.append(json.loads((source_public / "summary.json").read_text()))
            continue
        strategy, task = strategies[unit["strategy_id"]], tasks[unit["task_id"]]
        row = {**unit, "run_id": config["run_id"], "benchmark_name": "Terminal-Bench",
               "benchmark_version": "2.0", "benchmark_commit": config["dataset_commit"],
               "source_revision": config["source_revision"], "original_subset": task["original_subset"],
               "historically_exposed": task["historically_exposed"],
               "used_for_current_training": task["used_for_current_training"],
               "used_for_model_selection": task["used_for_model_selection"],
               "independent_of_training_and_selection": not task["used_for_current_training"] and not task["used_for_model_selection"],
               "checkpoint_path": strategy.get("checkpoint", {}).get("path"),
               "router_device": strategy.get("checkpoint", {}).get("device"),
               "teacher_enabled": strategy.get("teacher_enabled", False),
               "aa_snapshot_id": config["capability_snapshot"]["snapshot_id"],
               "harbor_version": config["harbor_version"], "mini_swe_version": config["mini_swe_version"],
               "task_resources": task["environment"], "reward": None, "error_type": None,
               "execution_status": job_states.get(unit["unit_id"], unit)["status"],
               "effort_comparison_eligible": not job_states.get(unit["unit_id"], {}).get("unsupported_effort", False),
               "episode_wall_s": None, "generator_known_reference_usd": None,
               "harbor_trial_count": 0, "attempts_wall_s": None,
               "teacher_known_reference_usd": None, "reference_cost_usd": None,
               "supplier_billed_usd": None, "router_compute_cost_usd": None,
               "environment_cost_usd": None, "complete_cost_usd": None,
               "physical_kv_sharing": "UNKNOWN", "evidence_path": str(private)}
        state_path = private / "resume_state.json"
        if not state_path.exists():
            episodes.append(row)
            continue
        state = json.loads(state_path.read_text())
        row["status"] = state["status"]
        if state["status"] not in ("EVALUATED", "PARTIAL", "BLOCKED"):
            episodes.append(row)
            continue
        trials = rows(private / "official_trials.jsonl")
        trial = max(trials, key=lambda r: r["finished_at"]) if trials else {}
        error = trial.get("error") or {}
        events = rows(private / "events.jsonl")
        requests = [request for attempt in trials for request in provider_requests(attempt, events)]
        generator = [r for r in requests if r["role"] == "generator"]
        teacher = [r for r in requests if r["role"] == "teacher"]
        routing = [e for e in events if e["event"] == "ROUTER_END"]
        contexts = [e for e in events if e["event"] == "V9_CONTEXT_END"]
        def known_cost(group):
            return sum(known_request_cost(r) or 0 for r in group)
        def reported(group, field):
            values = [r.get(field) for r in group]
            return sum(values) if all(v is not None for v in values) else None
        row.update(trial_id=trial.get("trial_id"), reward=trial.get("reward"),
                   effort_comparison_eligible=not strategy.get("model") or not any(r.get("native_effort_status") == "PROVIDER_REPORTED_MISMATCH" for r in generator),
                   harbor_trial_count=len(trials),
                   attempts_wall_s=sum(t["duration_sec"] for t in trials),
                   previous_attempts=[{**{k: t.get(k) for k in ("trial_id", "job_name", "trial_dir", "status", "reward", "started_at", "finished_at", "duration_sec", "phase_wall_s")}, "error_type": (t.get("error") or {}).get("exception_type")} for t in trials if t is not trial],
                   official_status=trial.get("status"), error_type=error.get("exception_type"),
                   failed_provider_http_status=next((r.get("http_status") for r in requests if r.get("event") in ("ERROR", "TEACHER_ERROR") and r.get("http_status")), None),
                   verifier_path=trial.get("verifier_path"), episode_wall_s=trial.get("duration_sec"),
                   phase_wall_s=trial.get("phase_wall_s"),
                   generator_requests=len(generator), teacher_requests=len(teacher),
                   started_tool_calls=sum(e["event"] == "TOOL_START" for e in events),
                   completed_tool_calls=sum(e["event"] == "TOOL_END" for e in events),
                   generator_known_reference_usd=known_cost(generator), teacher_known_reference_usd=known_cost(teacher),
                   reference_cost_usd=reported(requests, "cost_usd"),
                   supplier_billed_usd=reported(requests, "actual_billed_cost_usd"),
                   unknown_provider_cost_requests=sum(r.get("cost_usd") is None for r in requests),
                   prompt_tokens=reported(requests, "prompt_tokens"), completion_tokens=reported(requests, "completion_tokens"),
                   reasoning_tokens=reported(requests, "reasoning_tokens"),
                   reported_cache_read_tokens=reported(requests, "cached_tokens"),
                   known_cache_read_tokens=sum(r.get("cached_tokens") or 0 for r in requests),
                   cache_read_unknown_records=sum(r.get("cached_tokens") is None for r in requests),
                   reported_cache_write_tokens=reported(requests, "cache_write_tokens"),
                   cache_write_unknown_records=sum(r.get("cache_write_tokens") is None for r in requests),
                   router_wall_s=sum(e.get("router_latency_ms", 0) for e in routing) / 1000,
                   router_cpu_time_sec=sum(e.get("router_cpu_time_sec", 0) for e in routing),
                   router_gpu_wait_s=sum(e.get("router_gpu_wait_ms", 0) for e in routing) / 1000,
                   router_transfer_s=sum(e.get("router_device_transfer_ms", 0) for e in routing) / 1000,
                   teacher_wall_s=sum(r.get("teacher_wall_ms", 0) for r in teacher) / 1000,
                   generator_wall_s=sum(r.get("agent_request_wall_ms", r.get("duration_ms", 0)) for r in generator) / 1000,
                   selected_actions=[e["selected_action"] for e in routing],
                   request_return_identities=[{k: r.get(k) for k in ("role", "request_model_id", "returned_model_id", "requested_native_effort", "returned_native_effort", "native_effort_status", "sent_effort_parameter", "protocol", "stream", "requested_max_output_tokens", "reported_max_output_tokens", "finish_reason", "http_status", "physical_backend_identity_status", "provider_endpoint_id", "identity_status", "cost_source", "cost_status", "cache_cost_policy", "reasoning_cost_policy")} for r in requests],
                   logical_model_changes=sum(bool(e.get("logical_model_changed")) for e in contexts),
                   endpoint_changes=sum(e.get("previous_provider_endpoint_id") is not None and e.get("previous_provider_endpoint_id") != e.get("provider_endpoint_id") for e in contexts),
                   prefix_continuity_counts={label: sum(e.get("input_prefix_continuity") == label for e in contexts) for label in ("FIRST_REQUEST", "EXACT_PREVIOUS_MESSAGES", "PREFIX_CHANGED")},
                   router_truncated_decisions=sum(bool((e.get("router_input_usage") or {}).get("truncated")) for e in routing),
                   teacher_consumed_decisions=sum(e.get("assessment_consumed_by_router") is True for e in events if e["event"] == "TEACHER_ROUTER_INPUT"))
        public.mkdir(parents=True, exist_ok=True)
        write_atomic(public / "official_result.json", {**{k: trial.get(k) for k in ("trial_id", "task_name", "task_git_sha", "status", "reward", "duration_sec", "started_at", "finished_at", "verifier_path")}, "error_type": row["error_type"], "failed_provider_http_status": row["failed_provider_http_status"]})
        write_atomic(public / "summary.json", row)
        fields = {"timestamp", "monotonic_ns", "event", "episode_id", "decision_id", "selected_action", "request_model_id", "returned_model_id", "requested_native_effort", "returned_native_effort", "native_effort_status", "sent_effort_parameter", "protocol", "stream", "requested_max_output_tokens", "reported_max_output_tokens", "finish_reason", "physical_backend_identity_status", "provider_endpoint_id", "cost_usd", "cost_source", "cost_status", "cache_cost_policy", "reasoning_cost_policy", "actual_billed_cost_usd", "prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens", "cache_write_tokens", "router_latency_ms", "inference_latency_ms", "router_input_usage", "router_cpu_time_sec", "teacher_wall_ms", "capability_snapshot_id", "assessment_consumed_by_router", "http_status", "category"}
        with (public / "events.jsonl").open("w") as stream:
            for event in events:
                stream.write(json.dumps({k: v for k, v in event.items() if k in fields}, ensure_ascii=False) + "\n")
        episodes.append(row)
    metrics = output_root / "metrics"
    metrics.mkdir(exist_ok=True)
    def write_csv(name, records):
        fields = list(dict.fromkeys(k for row in records for k in row))
        with (metrics / name).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in records)
    grouped = []
    def measured_sum(group, field):
        values = [r[field] for r in group if r.get(field) is not None]
        return sum(values) if values else None
    for strategy in strategies:
        all_rows = [r for r in episodes if r["strategy_id"] == strategy]
        for subset, group in (("all", all_rows), ("independent_of_training_and_selection", [r for r in all_rows if r["independent_of_training_and_selection"]]), ("historically_exposed", [r for r in all_rows if r["historically_exposed"]]), ("not_historically_exposed", [r for r in all_rows if not r["historically_exposed"]])):
            n = len(group)
            eligible = [r for r in group if r["effort_comparison_eligible"]]
            one, zero = sum(r["reward"] == 1 for r in eligible), sum(r["reward"] == 0 for r in eligible)
            finished = [r for r in group if r["status"] in ("EVALUATED", "PARTIAL", "BLOCKED")]
            running = sum(r["execution_status"] == "RUNNING" and r["status"] not in ("EVALUATED", "PARTIAL", "BLOCKED") for r in group)
            unavailable = sum(r["execution_status"] == "UNAVAILABLE_PROVIDER_EFFORT" for r in group)
            grouped.append({"strategy_id": strategy, "subset": subset, "tasks": n,
                            "attempted": len(finished), "reward_1": one, "reward_0": zero,
                            "harbor_trial_count": sum(r["harbor_trial_count"] for r in group),
                            "no_official_reward": sum(r["reward"] is None for r in finished),
                            "running": running, "not_started": n - len(finished) - running - unavailable,
                            "unavailable": unavailable, "effort_mismatch_completed": sum(not r["effort_comparison_eligible"] for r in finished),
                            "not_finished": n - len(finished), "scored_pass_rate": one / (one + zero) if one + zero else None,
                            "benchmark_success_lower": one / n if n else None,
                            "benchmark_success_upper": (n - zero) / n if n else None,
                            "generator_known_reference_usd": measured_sum(group, "generator_known_reference_usd"),
                            "teacher_known_reference_usd": measured_sum(group, "teacher_known_reference_usd"),
                            **{field: measured_sum(group, field) for field in ("generator_requests", "teacher_requests", "prompt_tokens", "completion_tokens", "reasoning_tokens", "known_cache_read_tokens", "cache_read_unknown_records", "unknown_provider_cost_requests", "router_wall_s", "router_cpu_time_sec", "router_gpu_wait_s", "teacher_wall_s", "logical_model_changes", "endpoint_changes")},
                            "complete_cost_usd": None, "supplier_billed_usd": None,
                            "episode_total_wall_s": measured_sum(group, "attempts_wall_s"),
                            "episode_p50_s": percentile([r["episode_wall_s"] for r in group], .5),
                            "episode_p95_s": percentile([r["episode_wall_s"] for r in group], .95)})
    comparisons = []
    pairs = [(f"{family}_{version}_off", f"{family}_{version}_on", "teacher") for family in ("laya", "kev") for version in ("original", "trained")]
    pairs += [(f"{family}_original_{teacher}", f"{family}_trained_{teacher}", "training") for family in ("laya", "kev") for teacher in ("off", "on")]
    pairs += [(fixed["id"], router["id"], "fixed_vs_router") for fixed in strategies.values() if fixed.get("model") for router in strategies.values() if router["stage"] == "router"]
    fixed = [s for s in strategies.values() if s["stage"] == "fixed"]
    pairs += [(x["id"], y["id"], "native_effort" if x.get("model") == y.get("model") else "fixed_strategy")
              for i, x in enumerate(fixed) for y in fixed[i + 1:]]
    for left, right, factor in pairs:
        a = {(r["task_id"], r["seed"]): r for r in episodes if r["strategy_id"] == left}
        b = {(r["task_id"], r["seed"]): r for r in episodes if r["strategy_id"] == right}
        paired = [(a[k], b[k]) for k in a.keys() & b.keys() if a[k]["reward"] in (0, 1) and b[k]["reward"] in (0, 1) and a[k]["effort_comparison_eligible"] and b[k]["effort_comparison_eligible"]]
        cost_pairs = [(x, y) for x, y in paired if x["reference_cost_usd"] is not None and y["reference_cost_usd"] is not None]
        comparisons.append({"factor": factor, "left": left, "right": right, "scored_pairs": len(paired),
                            "left_reward_1": sum(x["reward"] == 1 for x, y in paired),
                            "right_reward_1": sum(y["reward"] == 1 for x, y in paired),
                            "reference_known_pairs": len(cost_pairs),
                            "left_reference_known_pairs_usd": sum(x["reference_cost_usd"] for x, y in cost_pairs) if cost_pairs else None,
                            "right_reference_known_pairs_usd": sum(y["reference_cost_usd"] for x, y in cost_pairs) if cost_pairs else None,
                            "reward_delta_sum": sum(y["reward"] - x["reward"] for x, y in paired),
                            **{field + "_delta_sum": sum(y[field] - x[field] for x, y in paired) if paired and all(x.get(field) is not None and y.get(field) is not None for x, y in paired) else None for field in ("generator_requests", "teacher_requests", "teacher_known_reference_usd", "known_cache_read_tokens", "logical_model_changes", "router_wall_s", "episode_wall_s")},
                            "known_reference_delta_usd": sum(y["reference_cost_usd"] - x["reference_cost_usd"] for x, y in paired) if paired and all(x["reference_cost_usd"] is not None and y["reference_cost_usd"] is not None for x, y in paired) else None,
                            "complete_cash_net_benefit_usd": None})
    write_csv("per_episode.csv", episodes)
    task_rows = [{"task_id": task, "attempted_strategies": sum(r["task_id"] == task and r["status"] in ("EVALUATED", "PARTIAL", "BLOCKED") for r in episodes),
                  "ended_fixed_strategies": sum(r["task_id"] == task and strategies[r["strategy_id"]]["stage"] == "fixed" and r["status"] in ("EVALUATED", "PARTIAL", "BLOCKED") for r in episodes),
                  "scored_strategies": sum(r["task_id"] == task and r["reward"] in (0, 1) for r in episodes)} for task in tasks]
    write_csv("per_task.csv", task_rows)
    write_csv("per_strategy.csv", grouped)
    write_csv("cost_breakdown.csv", [{k: r[k] for k in ("task_id", "strategy_id", "seed", "generator_known_reference_usd", "teacher_known_reference_usd", "reference_cost_usd", "supplier_billed_usd", "router_compute_cost_usd", "environment_cost_usd", "complete_cost_usd")} for r in episodes])
    write_atomic(metrics / "comparisons.json", comparisons)
    totals = {field: sum(r[field] for r in grouped if r["subset"] == "all")
              for field in ("tasks", "attempted", "harbor_trial_count", "reward_1", "reward_0", "no_official_reward", "running", "not_started", "unavailable")}
    fixed_count = sum(s["stage"] == "fixed" for s in strategies.values())
    report = ["# Terminal-Bench 2.0 RQ1\n", f"官方版本：{config['dataset_commit']}；源码：{config['source_revision']}。\n",
              "**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**\n",
              f"共{totals['tasks']}个任务/策略/seed位置；已结束{totals['attempted']}，运行中{totals['running']}，未开始{totals['not_started']}，渠道档位不可用{totals['unavailable']}。已结束位置中，无已报告档位冲突的官方Reward 1/0为{totals['reward_1']}/{totals['reward_0']}，无官方Reward {totals['no_official_reward']}。\n",
              f"已保存原Harbor Trial {totals['harbor_trial_count']}次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。\n",
              f"按逐题表：{sum(r['attempted_strategies'] > 0 for r in task_rows)}/{len(tasks)}题已有结束记录；{sum(r['ended_fixed_strategies'] == fixed_count for r in task_rows)}题已结束全部{fixed_count}个固定/简单策略；{sum(r['attempted_strategies'] == len(strategies) for r in task_rows)}题已结束全部{len(strategies)}个策略。批次先执行固定阶段，再执行Router阶段。\n",
              "GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。\n",
              "完整89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务，89题全量结果尚在执行。\n",
              "| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in grouped:
        if r["subset"] == "all":
            cost = "UNKNOWN" if r["generator_known_reference_usd"] is None else f"{r['generator_known_reference_usd'] + (r['teacher_known_reference_usd'] or 0):.8f}"
            rate = "未评分" if r["scored_pass_rate"] is None else f"{r['reward_1']}/{r['reward_1'] + r['reward_0']} = {r['scored_pass_rate']:.2%}"
            report.append(f"| {r['strategy_id']} | {r['attempted']} | {r['reward_1']} | {r['reward_0']} | {rate} | {r['no_official_reward']} | {r['running']} | {r['not_started']} | {r['unavailable']} | {cost} |")
    (output_root / "review.md").write_text("\n".join(report) + "\n")
    return {"episodes": episodes, "strategies": grouped, "comparisons": comparisons}


