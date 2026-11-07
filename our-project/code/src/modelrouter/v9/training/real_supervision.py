"""Turn paired real candidate outcomes into separately scoped routing targets."""
from __future__ import annotations

import copy
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from modelrouter.v9.capabilities.features import candidate_action
from modelrouter.serving.schemas import route_questions
from modelrouter.providers.registry import legal_actions


ACTION_POOL_ID = "LUNA_GLM53FLASH_TERRA_MODEL_EFFORT_15_V1"
ACTION_POOL = tuple(
    {**action, "model_id": action["model"]} for action in legal_actions()
)
ACTION_POOL_IDS = {action["action_id"] for action in ACTION_POOL}


def action_pool_question(actions=ACTION_POOL):
    return route_questions([SimpleNamespace(**{
        "action_id": action["action_id"], "provider": action["provider"],
        "model": action["model"], "native_effort": action["native_effort"],
    }) for action in actions])


def prepare_action_pool_comparison(row, split):
    """Prepare only a complete, confirmed 15-action next-step verifier comparison."""
    if (row.get("supervision_type") != "STEP_LEVEL_PREFERENCE"
            or row.get("selection_scope") == "MODEL_ONLY"
            or row.get("native_efforts_confirmed") is not True):
        return None, "ACTION_POOL_SCOPE_NOT_CONFIRMED"
    actions = [candidate_action(action) for action in row["candidate_actions"]]
    if (len(actions) != len(ACTION_POOL) or {action["action_id"] for action in actions} != ACTION_POOL_IDS
            or any((action["model_id"], action["native_effort"]) !=
                   (pool_action["model_id"], pool_action["native_effort"])
                   for action in actions
                   for pool_action in ACTION_POOL if action["action_id"] == pool_action["action_id"])):
        return None, "ACTION_POOL_CANDIDATES_INCOMPLETE"
    results = row["candidate_results"]
    pool_by_id = {action["action_id"]: action for action in ACTION_POOL}
    if (len(results) != len(ACTION_POOL)
            or {item["action_id"] for item in results} != ACTION_POOL_IDS
            or any((item["model_id"], item["native_effort"]) !=
                   (pool_by_id[item["action_id"]]["model_id"],
                    pool_by_id[item["action_id"]]["native_effort"]) for item in results)):
        return None, "ACTION_POOL_RESULTS_INCOMPLETE"
    prepared, reason = prepare_comparison(row, split)
    if reason:
        return None, reason
    previous_target = next(iter(prepared["expected"]))
    winner = prepared["expected"][previous_target]
    question = action_pool_question()["route_decision"]
    prepared.update(questions={"route_decision": question},
                    expected={"route_decision": winner}, candidate_actions=list(ACTION_POOL))
    prepared["_meta"].update(target="route_decision", input_kind="REAL_ACTION_POOL_COMPARISON",
                             action_pool_id=ACTION_POOL_ID, selection_scope="MODEL_NATIVE_EFFORT",
                             comparison_axis="MODEL_NATIVE_EFFORT", full_action_pool_optimum=True)
    return prepared, None


SUPERVISION_TYPES = (
    "TASK_LEVEL_PREFERENCE", "STEP_LEVEL_PREFERENCE", "OBSERVED_OUTCOME_ONLY",
    "AUXILIARY_FEATURE_ONLY", "UNLABELED",
)
PREFERENCE_TARGETS = {
    "TASK_LEVEL_PREFERENCE": (
        "task_model_effort_preference",
        "For this initial task state, select a model and its native effort to complete the "
        "episode under the original verifier. Prefer verified completion; among candidates "
        "with equal verified completion, prefer lower measured model-rate cost.",
    ),
    "STEP_LEVEL_PREFERENCE": (
        "step_model_effort_preference",
        "For this observed decision prefix, select a model and its native effort for one "
        "native Agent step. Prefer passing the original task verifier immediately after "
        "that step; among passing candidates, prefer lower measured model-rate cost. "
        "This target does not describe the eventual episode outcome.",
    ),
}
MODEL_TARGETS = {
    kind: (target.replace("model_effort", "model"), instruction.replace(
        "a model and its native effort", "a model under the recorded Provider configuration"
    ) + " The applied native effort is not a supervised target.")
    for kind, (target, instruction) in PREFERENCE_TARGETS.items()
}


def prepare_comparison(row, split):
    """Use only the paired verifier horizon; retain observations without choice labels."""
    kind = row["supervision_type"]
    if kind not in SUPERVISION_TYPES:
        return None, "UNKNOWN_SUPERVISION_TYPE"
    if kind not in PREFERENCE_TARGETS:
        return None, "NO_ROUTING_TARGET"
    if split == "train" and row["provenance"].get("train_eligible") is not True:
        return None, "SOURCE_NOT_TRAIN_ELIGIBLE"
    conditions = row["comparison_conditions"]
    if not all(conditions[name] for name in (
        "same_observed_messages", "same_initial_environment", "same_agent_protocol",
        "original_verifier_unchanged", "candidate_identity_matched", "trusted_outcomes",
    )):
        return None, "COMPARISON_NOT_VALID"
    actions = [candidate_action(action) for action in row["candidate_actions"]]
    results = row["candidate_results"]
    if any(item.get("trusted_outcome") is False or item.get("identities_matched") is False
           or item["resolved"] is None for item in results):
        return None, "COMPARISON_NOT_VALID"
    if {action["action_id"] for action in actions} != {item["action_id"] for item in results}:
        return None, "CANDIDATE_IDENTITY_CONFLICT"
    model_only = row.get("selection_scope") == "MODEL_ONLY"
    if model_only:
        actions = [{**action, "action_id": action["model_id"], "native_effort": None,
                    "requested_native_effort": action.get("requested_native_effort", action["native_effort"])}
                   for action in actions]
        results = [{**item, "action_id": item["model_id"]} for item in results]
    elif any(item.get("native_effort_status") == "PROVIDER_REPORTED_MISMATCH" for item in results):
        return None, "NATIVE_EFFORT_MISMATCH"
    elif row.get("native_efforts_confirmed") is False:
        return None, "NATIVE_EFFORT_NOT_CONFIRMED"
    passing = [item for item in results if item["resolved"] is True]
    if not passing:
        return None, "NO_VERIFIED_ACTION"
    basis = "VERIFIED_QUALITY_AT_RECORDED_HORIZON"
    if len(passing) > 1:
        if any(item["model_rate_cost_usd"] is None for item in passing):
            return None, "COST_NOT_MEASURED"
        passing.sort(key=lambda item: item["model_rate_cost_usd"])
        if passing[0]["model_rate_cost_usd"] == passing[1]["model_rate_cost_usd"]:
            return None, "NO_STRICT_PREFERENCE"
        basis = "LOWER_MODEL_RATE_COST_AT_EQUAL_VERIFIER_RESULT"
    winner = passing[0]["action_id"]
    target, instruction = (MODEL_TARGETS if model_only else PREFERENCE_TARGETS)[kind]
    prepared = deepcopy(row)
    prepared.update(
        candidate_actions=actions,
        candidate_results=results,
        questions={target: {"type": "choice", "instructions": instruction,
                           "criteria": {action["action_id"]:
                                        (action['model_id'] if model_only else
                                         f"{action['model_id']} / {action['native_effort']}")
                                        for action in actions}}},
        expected={target: winner},
        _meta={"supervision_class": "S1", "supervision_type": kind, "target": target,
               "input_kind": "REAL_CANDIDATE_COMPARISON", "preference_basis": basis,
               "supervision_qualification": "PAIRED_REAL_VERIFIER_RESULT",
               "comparison_size_k": len({action["model_id"] for action in actions}),
               "candidate_action_count": len(actions),
               "comparison_axis": ("NATIVE_EFFORT" if len({action["model_id"] for action in actions}) == 1
                                   else "MODEL_NATIVE_EFFORT" if len(actions) > len({action["model_id"] for action in actions})
                                   else "MODEL"),
               "selection_scope": "MODEL_ONLY" if model_only else "MODEL_NATIVE_EFFORT",
               "full_three_model_optimum": False},
    )
    return prepared, None


def prepare_candidate_outcomes(row, split):
    """Separate observed candidate completion from the existing preference target."""
    conditions = row["comparison_conditions"]
    eligible = split != "train" or row["provenance"].get("train_eligible") is True
    actions = {(action["action_id"], action["model_id"])
               for action in map(candidate_action, row["candidate_actions"])}
    observations = []
    for item in row["candidate_results"]:
        known = (conditions["original_verifier_unchanged"] and eligible
                 and (item["action_id"], item["model_id"]) in actions
                 and item.get("trusted_outcome") is True
                 and item.get("identities_matched") is True
                 and item["resolved"] is not None)
        observations.append({
            **item,
            "observed_verifier_completion": item["resolved"] if known else None,
            "outcome_status": ("PASSED" if item["resolved"] else "FAILED") if known else "UNKNOWN",
            "auxiliary_target": "CANDIDATE_VERIFIER_COMPLETION_AT_RECORDED_HORIZON",
        })
    return observations


def prepare_candidate_view(records, output_path):
    """Export source/state identities without creating Trainer choice targets."""
    seen, rows, counts = set(), [], Counter()
    for original in records:
        row = copy.deepcopy(original)
        provenance = row["provenance"]
        task_key = (provenance["source_id"], provenance["task_id"], provenance["repo"],
                    provenance.get("base_commit", provenance.get("base_commit_prefix")),
                    provenance.get("fault_identity"))
        state_key = (*task_key, provenance.get("episode_id"),
                     provenance.get("message_cutoff_exclusive"))
        if state_key in seen:
            counts["DUPLICATE_STATE"] += 1
            continue
        seen.add(state_key)
        reasons = []
        if "candidate_results" in row:
            prepared, reason = prepare_comparison(row, "train")
            observations = prepare_candidate_outcomes(row, "train")
            row["candidate_outcome_observations"] = observations
            actions = list(map(candidate_action, row["candidate_actions"]))
            identities = {(item["action_id"], item["model_id"]) for item in actions}
            comparable = (
                all(row["comparison_conditions"][name] for name in (
                    "same_observed_messages", "same_initial_environment", "same_agent_protocol",
                    "original_verifier_unchanged", "candidate_identity_matched", "trusted_outcomes",
                ))
                and len(actions) == len(observations) == len(identities) >= 2
                and identities == {(item["action_id"], item["model_id"]) for item in observations}
                and all(item["outcome_status"] != "UNKNOWN" for item in observations)
            )
            row["pair_comparable"] = comparable
            category = ("VALID_PREFERENCE" if prepared and comparable else
                        "COMPARABLE_UNLABELED" if comparable else "INVALID_OR_UNKNOWN")
            if reason:
                reasons.append(reason)
        else:
            state_available = row["decision_state_status"] == "FULL_HISTORY_RECOVERED"
            evidence = row["environment_evidence"]
            reproducible = state_available and all(evidence.get(name) for name in (
                "image_name", "verify_command_available", "original_test_ids_complete", "historical_verifier_trusted",
            ))
            local_image_present = evidence.get("local_image_status") == "PRESENT"
            local_verifier_runnable = evidence.get("local_original_verifier_status") == "RUNNABLE"
            row.update(historical_state_complete=state_available,
                       historical_reproduction_evidence_complete=reproducible,
                       local_exact_image_present=local_image_present,
                       local_original_verifier_runnable=local_verifier_runnable,
                       currently_executable=reproducible and local_image_present and local_verifier_runnable)
            category = "REPRODUCIBLE_CANDIDATE" if row["currently_executable"] else "OBSERVATION_ONLY"
            if reproducible and not local_image_present:
                reasons.append("LOCAL_EXACT_IMAGE_MISSING")
            if reproducible and not local_verifier_runnable:
                reasons.append("LOCAL_ORIGINAL_VERIFIER_NOT_CONFIRMED")
            if not state_available:
                reasons.append("FULL_DECISION_HISTORY_UNAVAILABLE")
            if not evidence.get("original_test_ids_complete"):
                reasons.append("ORIGINAL_TEST_IDS_UNAVAILABLE")
            if not evidence.get("image_name"):
                reasons.append("ENVIRONMENT_IMAGE_UNAVAILABLE")
            if not evidence.get("historical_verifier_trusted"):
                reasons.append("ORIGINAL_VERIFIER_EVIDENCE_UNAVAILABLE")
            if not all(task_key[1:4]):
                category = "INVALID_OR_UNKNOWN"
                reasons.append("TASK_VERSION_IDENTITY_INCOMPLETE")
        row.update(cleaning_status=category, label_loss_reasons=reasons,
                   trainer_target_created=False, supervision_type=row.get("supervision_type", "UNLABELED"),
                   task_identity=list(task_key), decision_identity=list(state_key))
        counts[category] += 1
        rows.append(row)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"input_records": len(records), "output_records": len(rows), "classification": dict(counts),
            "independent_tasks": len({tuple(row["task_identity"]) for row in rows}),
            "repositories": len({row["provenance"]["repo"] for row in rows}),
            "historical_state_complete": sum(row.get("historical_state_complete", False) for row in rows),
            "historical_reproduction_evidence_complete": sum(row.get("historical_reproduction_evidence_complete", False) for row in rows),
            "local_exact_images_present": sum(row.get("local_exact_image_present", False) for row in rows),
            "local_original_verifiers_runnable": sum(row.get("local_original_verifier_runnable", False) for row in rows),
            "currently_executable": sum(row.get("currently_executable", False) for row in rows),
            "trainer_targets_added": 0}


def prepare_local_quality_relation(initial, candidates, f2p_ids, p2p_ids, *, pair_comparable):
    """Compare recorded repair sets on two axes without creating a formal preference."""
    f2p, p2p = set(f2p_ids), set(p2p_ids)
    fixed = f2p | p2p
    before = initial["original_test_status"]
    initial_f2p_failed = {name for name in f2p if before[name] == "FAILED"}
    initial_p2p_failed = {name for name in p2p if before[name] == "FAILED"}
    results = []
    for candidate in candidates:
        after = candidate["original_test_status"]
        passed = {name for name in fixed if after.get(name) == "PASSED"}
        failed = {name for name in fixed if after.get(name) == "FAILED"}
        unknown = {name for name in fixed if before[name] not in ("PASSED", "FAILED")
                   or after.get(name) not in ("PASSED", "FAILED")}
        unknown.update(initial.get("unknown_test_ids", []))
        unknown.update(candidate.get("unknown_test_ids", []))
        results.append({
            "model_id": candidate["model_id"], "fixed_test_ids": sorted(fixed),
            "initial_f2p_failed_ids": sorted(initial_f2p_failed),
            "repaired_initial_f2p_ids": sorted(initial_f2p_failed & passed),
            "initial_p2p_failed_ids": sorted(initial_p2p_failed),
            "restored_initial_p2p_ids": sorted(initial_p2p_failed & passed),
            "new_p2p_regressions": sorted({name for name in p2p if before[name] == "PASSED"} & failed),
            "new_f2p_regressions": sorted({name for name in f2p if before[name] == "PASSED"} & failed),
            "unknown_test_ids": sorted(unknown),
            "trusted_outcome": candidate["trusted_outcome"],
        })
    trusted = (pair_comparable and initial["trusted_outcome"]
               and all(item["trusted_outcome"] and not item["unknown_test_ids"] for item in results))
    repairs = [(set(item["repaired_initial_f2p_ids"]), set(item["restored_initial_p2p_ids"]))
               for item in results]
    regressions = [(set(item["new_f2p_regressions"]), set(item["new_p2p_regressions"]))
                   for item in results]
    dominant = None
    if trusted:
        for index, other in ((0, 1), (1, 0)):
            if (not any(regressions[index])
                    and all(a >= b for a, b in zip(repairs[index], repairs[other]))
                    and (repairs[index] != repairs[other] or any(regressions[other]))):
                dominant = results[index]["model_id"]
    relationship = ("UNKNOWN" if not trusted else "STRICT_MULTIDIMENSIONAL_DOMINANCE" if dominant else
                    "NO_LOCAL_IMPROVEMENT" if not any(any(pair) for pair in repairs + regressions) else
                    "EQUAL_LOCAL_PROGRESS" if repairs[0] == repairs[1] and regressions[0] == regressions[1] else
                    "INCOMPARABLE_LOCAL_RESULTS")
    axis_relations, axis_opportunities = {}, {}
    for name, initial_ids, regression in (
        ("f2p_repair", initial_f2p_failed, False),
        ("p2p_restoration", initial_p2p_failed, False),
        ("f2p_regression", {name for name in f2p if before[name] == "PASSED"}, True),
        ("p2p_regression", {name for name in p2p if before[name] == "PASSED"}, True),
    ):
        field = {"f2p_repair": "repaired_initial_f2p_ids",
                 "p2p_restoration": "restored_initial_p2p_ids",
                 "f2p_regression": "new_f2p_regressions",
                 "p2p_regression": "new_p2p_regressions"}[name]
        first, second = (set(item[field]) for item in results)
        better_first = first < second if regression else first > second
        better_second = second < first if regression else second > first
        axis_opportunities[name] = bool(initial_ids)
        axis_relations[name] = ("UNKNOWN" if not trusted else "EQUAL" if first == second else
                                results[0]["model_id"] if better_first else
                                results[1]["model_id"] if better_second else "INCOMPARABLE")
    return {"relationship": relationship, "dominant_model_id": dominant,
            "candidates": results, "pair_comparable": trusted,
            "axis_relations": axis_relations, "axis_opportunities": axis_opportunities,
            "auxiliary_target": "RECORDED_F2P_REPAIR_AND_P2P_RESTORATION_RELATION",
            "formal_preference_created": False}
