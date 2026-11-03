"""Turn paired real candidate outcomes into separately scoped routing targets."""
from __future__ import annotations

from copy import deepcopy

from modelrouter.v9.capabilities.features import candidate_action


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
    if any(item.get("trusted_outcome") is False or item["resolved"] is None for item in results):
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
                                   else "MODEL"),
               "selection_scope": "MODEL_ONLY" if model_only else "MODEL_NATIVE_EFFORT",
               "full_three_model_optimum": False},
    )
    return prepared, None


def prepare_candidate_outcomes(row, split):
    """Separate observed candidate completion from the existing preference target."""
    conditions = row["comparison_conditions"]
    shared = all(conditions[name] for name in (
        "same_observed_messages", "same_initial_environment", "same_agent_protocol",
        "original_verifier_unchanged",
    ))
    eligible = split != "train" or row["provenance"].get("train_eligible") is True
    actions = {candidate_action(action)["action_id"] for action in row["candidate_actions"]}
    observations = []
    for item in row["candidate_results"]:
        known = (shared and eligible and item["action_id"] in actions
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
