"""RQ3 observations from official single-agent Harbor runs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional


def compute_decomposition_benchmarks(
    base_records: Optional[List[Dict[str, Any]]] = None,
    events: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Report observed task starts, phase changes and generation boundaries only."""
    by_episode = defaultdict(list)
    for event in events or []:
        if event.get("event") in ("ROUTER_END", "ROUTER_REUSE") and event.get("episode_id") is not None:
            by_episode[str(event["episode_id"])].append(event)

    observations = []
    for trial in base_records or []:
        if trial.get("agent") == "oracle" or not trial.get("trial_id"):
            continue
        decisions = sorted(by_episode[str(trial["trial_id"])],
                           key=lambda row: row.get("decision_sequence", row.get("step", 0)))
        generations = []
        subtask_ids = []
        subtask_boundaries = []
        previous_subtask = None
        for index, decision in enumerate(decisions):
            state = decision.get("pre_decision_state") or {}
            phase = state.get("phase")
            agent_state = state.get("agent_state") or {}
            subtask_id = agent_state.get("subtask_id") or agent_state.get("subtask")
            if subtask_id is not None and (not subtask_ids or subtask_ids[-1] != subtask_id):
                subtask_ids.append(subtask_id)
            if subtask_id is not None and previous_subtask is not None and subtask_id != previous_subtask:
                subtask_boundaries.append({"from": previous_subtask, "to": subtask_id,
                                           "generation": state.get("step_index", decision.get("step"))})
            if subtask_id is not None:
                previous_subtask = subtask_id
            generations.append({
                "decision_id": decision.get("decision_id"),
                "step": state.get("step_index", decision.get("step")),
                "phase": phase,
                "phase_source": (agent_state.get("progress") or {}).get("phase_source"),
                "selected_action": decision.get("selected_action"),
                "subtask_id": subtask_id,
                "task_start": index == 0 and state.get("step_index", 0) == 0,
            })
        phase_changes = []
        previous_phase = None
        for row in generations:
            if row["phase"] is not None and previous_phase is not None and row["phase"] != previous_phase:
                phase_changes.append({"from": previous_phase, "to": row["phase"],
                                      "generation": row["step"]})
            if row["phase"] is not None:
                previous_phase = row["phase"]
        observations.append({
            "trial_id": str(trial["trial_id"]),
            "task_id": trial.get("task_name") or trial.get("task_id"),
            "policy": trial.get("policy"),
            "status": trial.get("status"),
            "reward": trial.get("reward"),
            "execution_model": "singleAgent",
            "task_scope": "WHOLE_TASK_SINGLE_AGENT",
            "task_start_observed": any(row["task_start"] for row in generations),
            "phase_changes": phase_changes,
            "implemented_subtask_ids": subtask_ids or None,
            "subtask_boundaries": subtask_boundaries or None,
            "subtask_boundary_status": "OBSERVED" if subtask_boundaries else "NOT_IMPLEMENTED_OR_RECORDED",
            "generation_count": len(generations),
            "router_call_count": sum(not row.get("decision_reused", False) for row in decisions),
            "generation_granularity": decisions[0].get("routing_granularity", "generation") if decisions else None,
            "generations": generations,
        })

    groups = defaultdict(list)
    for row in observations:
        decisions = by_episode[row["trial_id"]]
        if not decisions or row["reward"] is None:
            continue
        first = decisions[0]
        if first.get("checkpoint_id") in (None, "none"):
            continue
        pre = first["pre_decision_state"]
        key = (row["task_id"], first["checkpoint_id"], pre.get("capability_snapshot_id"),
               tuple(pre.get("disabled_information_groups", [])), pre.get("teacher_status") == "DISABLED")
        groups[key].append(row)
    comparisons = [rows for rows in groups.values()
                   if len({row["generation_granularity"] for row in rows}) > 1]
    return {
        "data_origin": "OFFICIAL_HARBOR_TRIALS_AND_ROUTER_EVENTS",
        "execution_model": "singleAgent",
        "decomposition_comparison_status": "NOT_EVALUATED",
        "decomposition_comparison_reason": "No repeated official trials at declared single-agent decomposition settings",
        "subtask_boundaries_implemented": any(row["subtask_boundaries"] for row in observations),
        "granularity_comparisons": comparisons,
        "granularity_comparison_status": "RECORDED_OFFICIAL_RESULTS" if comparisons else "NOT_EVALUATED",
        "observations": observations,
    }
