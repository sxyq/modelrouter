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
    events_by_episode = defaultdict(list)
    for event in events:
        if event.get("episode_id") is not None:
            events_by_episode[str(event["episode_id"])].append(event)

    def provider_requests(trial):
        episode = str(trial["trial_id"])
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

    by_policy = defaultdict(list)
    for trial in usable:
        by_policy[trial["policy"]].append(trial)
    trial_requests = {str(trial["trial_id"]): provider_requests(trial) for trial in raw
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
    output.update(observed_research_groups(usable, events))
    from .rq3_analysis import compute_decomposition_benchmarks
    output["rq3_single_agent_observations"] = compute_decomposition_benchmarks(raw, events)
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


def observed_research_groups(trials, events):
    """Group only declared experimental factors and observed official outcomes."""
    from .iterations import percentile

    def label(trial, field):
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
        generator = [t.get("cost_usd") for t in group]
        complete = [full_cost(t) for t in group]
        return {**labels, "episodes": len(group), "successes": success,
                "success_rate": success / len(group), "ci95": wilson_score_interval(success, len(group)),
                "generator_mean_usd": sum(generator) / len(group) if all(c is not None for c in generator) else None,
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
               "table8": ("supervision_ablation",), "table11": ("checkpoint_id",)}
    group_status = {}
    for table, fields in factors.items():
        grouped = defaultdict(list)
        for trial in trials:
            values = tuple(label(trial, f) for f in fields)
            if any(value is None for value in values):
                continue
            grouped[(trial["policy"], *values)].append(trial)
        records = []
        for key, group in sorted(grouped.items(), key=lambda kv: str(kv[0])):
            same_policy = [v for k, v in grouped.items() if k[0] == key[0]]
            sets = [{task_seed(t) for t in v} for v in same_policy]
            paired = len(sets) > 1 and all(s == sets[0] for s in sets)
            records.append(summarize(group, {"policy": key[0], **dict(zip(fields, key[1:])),
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
                  fig7={"information": result["table4"], "actions": result["table5"],
                        "supervision": result["table8"], "checkpoints": result["table11"]},
                  fig8=comparisons, observed_factor_status=group_status)
    return result


