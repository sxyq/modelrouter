"""Prepare typed supervision while preserving its source targets and evidence."""
from __future__ import annotations

import copy
import json

from modelrouter.data_pipeline.batch_prep import MATRIX_ALLOWED_SOURCES, MATRIX_TARGETS, _example, _neutral_instruction
from modelrouter.serving.schemas import PreDecisionState
from modelrouter.v9.capabilities.features import candidate_action, capability_cards
from .prefix_replay import router_input_text
from .real_supervision import ACTION_POOL_ID, prepare_action_pool_comparison, prepare_comparison


SOURCE_PRE_FIELDS = (
    "candidate_model_a", "candidate_model_b", "input_length", "prompt_tokens",
    "arrival_timestamp", "prefix_block_count", "prefix_hash_sample", "trace_type",
    "model_normalized", "requested_model", "reasoning_effort", "is_stream", "log_type",
)
NEW_FEATURE_FIELDS = (
    "teacher_assessment", "capability_cards", "capability_snapshot_id", "feature_training_status",
)
TEACHER_FIELDS = ("progress_summary", "main_blocker", "next_milestone")
TEACHER_METADATA = (
    "episode_id", "phase", "assessed_through_decision_id", "assessed_through_step",
    "teacher_model_id", "reference_ids", "teacher_dataset_revision", "native_effort",
    "execution_mode", "cost_scope", "for_decision_id",
)


def decision_state(pre, task_id=None):
    """Use the same serializer consumed by the existing serving adapters."""
    values = {name: pre[name] for name in PreDecisionState.model_fields if name in pre}
    features = {name: pre[name] for name in SOURCE_PRE_FIELDS if name in pre}
    history = pre.get("history_snippet")
    if features:
        history = json.dumps({"observed_history": history, "source_pre_decision_features": features},
                             ensure_ascii=False)
    prompt = next((pre[name] for name in ("prompt", "prompt_snippet", "initial_prompt_snippet")
                   if pre.get(name) is not None), None)
    values.update(task_id=pre.get("task_id") or task_id, prompt=prompt, history_snippet=history,
                  feature_training_status="FEATURE_NOT_TRAINED")
    values["budget_status"] = pre.get("budget_status") or "UNKNOWN"
    values["capability_cards"] = pre.get("capability_cards") or []
    return PreDecisionState.model_validate(values)


def offline_teacher_state(row, pre, provenance):
    """Import the existing assessor's assessment/metrics pair; never call a teacher."""
    saved = row.get("offline_teacher_state") or pre.get("offline_teacher_state") or {}
    assessment = copy.deepcopy(saved.get("assessment", pre.get("teacher_assessment")))
    metrics = copy.deepcopy(saved.get("metrics", row.get("teacher_metrics") or {}))
    result = {"schema_version": 1, "status": "NOT_GENERATED", "origin": "IMPORTED_OFFLINE",
              "assessment": None, "metrics": metrics, "dataset_revision": saved.get("dataset_revision")}
    if assessment is None:
        result["status"] = "FAILED" if metrics.get("status") == "FAILED" else "NOT_GENERATED"
        return result
    if metrics.get("status") == "FAILED":
        result["status"] = "FAILED"
        return result
    if not isinstance(assessment, dict) or any(not isinstance(assessment.get(name), str) for name in TEACHER_FIELDS):
        result["status"] = "INVALID_FORMAT"
        return result
    imported = {name: assessment[name] for name in TEACHER_FIELDS}
    imported.update({name: assessment.get(name, metrics.get(name)) for name in TEACHER_METADATA})
    actual_model = metrics.get("teacher_model_id") or metrics.get("returned_model_id")
    if actual_model and imported["teacher_model_id"] and actual_model != imported["teacher_model_id"]:
        result["status"] = "TEACHER_MODEL_ID_CONFLICT"
        return result
    imported["teacher_model_id"] = actual_model or imported["teacher_model_id"]
    if not imported["teacher_model_id"]:
        result["status"] = "MODEL_ID_NOT_REPORTED"
        return result
    if imported["teacher_model_id"] != "gpt-6-luna":
        result["status"] = "TEACHER_MODEL_NOT_FORMAL"
        return result
    cutoff = imported["assessed_through_step"]
    observed = provenance.get("observed_through_step", pre.get("step_index"))
    if type(cutoff) is not int or type(observed) is not int:
        result["status"] = "CAUSAL_SCOPE_NOT_REPORTED"
        return result
    if cutoff < 0 or cutoff > observed:
        result["status"] = "FUTURE_ASSESSMENT"
        return result
    episode = provenance.get("episode_id") or provenance.get("trajectory_id")
    if episode and imported["episode_id"] and episode != imported["episode_id"]:
        result["status"] = "OTHER_EPISODE"
        return result
    references = imported["reference_ids"]
    if not isinstance(references, list) or len(references) != 2 or any(not isinstance(ref, dict) for ref in references):
        result["status"] = "REFERENCES_NOT_REPORTED"
        return result
    for ref in references:
        if (ref.get("split") != "train" or not ref.get("success_evidence")
                or (provenance.get("task_id") and ref.get("task_id") == provenance["task_id"])
                or (episode and ref.get("episode_id") == episode)):
            result["status"] = "REFERENCE_SCOPE_MISMATCH"
            return result
    result.update(status="GENERATED", assessment=imported)
    return result


def candidate_inputs(row, pre, questions, group, supplied=()):
    """Historical choice order takes precedence; supplied actions augment auxiliary views."""
    actions = next((row.get(name) or pre.get(name) for name in
                    ("legal_actions", "candidate_actions", "candidates")
                    if row.get(name) or pre.get(name)), None)
    if group == "S1":
        choices = next(question["criteria"] for question in questions.values() if question.get("type") == "choice")
        if not actions:
            return [candidate_action(choice) for choice in choices]
        actions = [candidate_action(action) for action in actions]
        ordered = []
        for choice in choices:
            matches = [action for action in actions if choice in (action["action_id"], action["model_id"])]
            if len(matches) != 1:
                raise ValueError("Candidate identities do not match the original choices")
            ordered.append(matches[0])
        return ordered
    return [candidate_action(action) for action in (actions or pre.get("capability_cards") or supplied)]


def prepare_record(row, split, dataset_revision=None, *, capability_snapshot=None, candidates=()):
    """Keep actual choice identities and targets; auxiliary labels remain auxiliary."""
    action_pool_supervision = row.get("_meta", {}).get("action_pool_id") == ACTION_POOL_ID
    real_preference = "supervision_type" in row and not action_pool_supervision
    if real_preference:
        row, reason = prepare_comparison(row, split)
        if reason:
            return None, reason
    if "candidate_reference" in row:
        reference = copy.deepcopy(row["candidate_reference"])
        if reference.get("split") == "train" and reference.get("train_eligible") is not True:
            return None, "SOURCE_NOT_TRAIN_ELIGIBLE"
        target = reference.get("target")
        if target not in reference.get("candidate_targets", []):
            return None, "MISSING_TARGET"
        materialized = _example(reference["source_id"], row["source_record"], reference, target)
        if materialized is None:
            return None, "MISSING_TARGET"
        materialized["provenance"].update({name: reference[name] for name in
            ("dataset_revision", "task_id", "assigned_layer", "quality_grade", "train_eligible") if name in reference})
        materialized["_meta"]["input_kind"] = "SAVED_CANDIDATE_REFERENCE"
        row = {**materialized, **{name: row[name] for name in
               (*NEW_FEATURE_FIELDS, "offline_teacher_state", "teacher_metrics", "legal_actions", "candidate_actions") if name in row}}
    provenance = copy.deepcopy(row.get("provenance", {}))
    source_id = provenance.get("source_id")
    meta = copy.deepcopy(row.get("_meta", {}))
    group = meta.get("supervision_class")
    if (source_id not in MATRIX_ALLOWED_SOURCES and not action_pool_supervision) or group not in ("S1", "S2", "S3"):
        return None, "SOURCE_OR_TARGET_NOT_SUPPORTED"
    if meta.get("target") not in MATRIX_TARGETS[group] and not (real_preference or action_pool_supervision):
        return None, "SOURCE_OR_TARGET_NOT_SUPPORTED"
    if provenance.get("split") not in (None, split):
        return None, "OTHER_SPLIT"
    questions = copy.deepcopy(row.get("questions", {}))
    expected = copy.deepcopy(row.get("expected", {}))
    if not questions or not expected:
        return None, "MISSING_TARGET"
    for qid, question in questions.items():
        label = expected.get(qid)
        if question.get("type") == "noul" and not isinstance(label, bool):
            return None, "UNKNOWN_OUTCOME"
        if label is None:
            return None, "MISSING_TARGET"
        if question.get("type") == "choice" and label not in question.get("criteria", {}):
            return None, "LABEL_OUTSIDE_CHOICES"
        if "label" in question and question["label"] != label:
            return None, "TARGET_CONFLICT"
        if question.get("type") == "score" and (
            type(label) is not int or not 0 <= label < len(question.get("criteria", []))
        ):
            return None, "LABEL_OUTSIDE_CHOICES"
        question["label"] = label
        if meta.get("target") and not (real_preference or action_pool_supervision):
            question["instructions"] = _neutral_instruction(meta["target"])
    state = row.get("pre_decision_state", row.get("state", {}))
    if isinstance(state, str):
        state = json.loads(state)
    pre = copy.deepcopy(state.get("pre_decision_state", state))
    for name in (*NEW_FEATURE_FIELDS, "offline_teacher_state"):
        if name in row and (name not in pre or pre[name] is None or pre[name] == []):
            pre[name] = copy.deepcopy(row[name])
    teacher = offline_teacher_state(row, pre, provenance)
    pre["teacher_assessment"] = teacher["assessment"]
    try:
        actions = candidate_inputs(row, pre, questions, group, candidates)
    except ValueError:
        return None, "CANDIDATE_IDENTITY_CONFLICT"
    if capability_snapshot is not None:
        pre["capability_cards"] = capability_cards(capability_snapshot, actions)
        pre["capability_snapshot_id"] = capability_snapshot.get("snapshot_id")
        pre["aa_fetched_at"] = capability_snapshot.get("aa_fetched_at")
        pre["aa_index_version"] = capability_snapshot.get("aa_index_version")
        pre["capability_freshness"] = capability_snapshot.get("freshness_status")
    task_id = provenance.get("task_id") or provenance.get("instance_id")
    decision = decision_state(pre, task_id)
    provenance["split"] = split
    if provenance.get("dataset_revision") is None:
        provenance["dataset_revision"] = dataset_revision
    meta.update(auxiliary_not_model_choice=group != "S1",
        teacher_data_status="GENERATED" if teacher["assessment"] else "NOT_GENERATED",
        offline_teacher_status=teacher["status"], feature_training_status="FEATURE_NOT_TRAINED",
        original_target=meta.get("target"),
        supervision_qualification=meta.get("supervision_qualification", "PRESERVED_SOURCE_TARGET"))
    try:
        router_text = router_input_text(row, decision)
    except (KeyError, ValueError) as exc:
        return None, f"PREFIX_REPLAY:{type(exc).__name__}:{exc}"
    result = {**row, "provenance": provenance, "state": router_text,
              "pre_decision_state": decision.model_dump(), "questions": questions, "expected": expected,
              "teacher_assessment": decision.teacher_assessment, "offline_teacher_state": teacher,
              "candidate_actions": actions, "capability_cards": decision.capability_cards,
              "capability_snapshot_id": decision.capability_snapshot_id,
              "feature_training_status": "FEATURE_NOT_TRAINED", "_meta": meta}
    return result, None


def prepare_action_pool_record(row, split, dataset_revision=None, *, capability_snapshot=None):
    prepared, reason = prepare_action_pool_comparison(row, split)
    if reason:
        return None, reason
    return prepare_record(prepared, split, dataset_revision, capability_snapshot=capability_snapshot)
