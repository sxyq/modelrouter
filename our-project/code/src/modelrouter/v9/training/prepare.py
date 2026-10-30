"""Prepare existing typed supervision and two extractive public trajectory references."""

from __future__ import annotations

import argparse
import copy
import gzip
import importlib.util
import json
import os
import sys
from collections import Counter
from itertools import islice, zip_longest
from pathlib import Path

# Load the existing pure data module without importing unrelated training audits.
_quality_name = "modelrouter.data_pipeline.quality.quality_v2"
if _quality_name not in sys.modules:
    _quality_path = Path(__file__).resolve().parents[2] / "data_pipeline/quality/quality_v2.py"
    _quality_spec = importlib.util.spec_from_file_location(_quality_name, _quality_path)
    _quality_module = importlib.util.module_from_spec(_quality_spec)
    sys.modules[_quality_name] = _quality_module
    _quality_spec.loader.exec_module(_quality_module)

from modelrouter.data_pipeline.batch_prep import (
    MATRIX_ALLOWED_SOURCES, MATRIX_TARGETS, _example, _neutral_instruction, _source_rows,
)
from modelrouter.data_pipeline.v8_extension_loader import V8ExtensionDataset
from modelrouter.datasets.public_sources import PublicDatasetLoader
from modelrouter.serving.schemas import PreDecisionState
from modelrouter.training.supervision_loaders import MultiViewSupervisionLoader
from modelrouter.v9.capabilities.features import (
    DEFAULT_DATA_DIR, candidate_action, capability_cards, load_current,
)
from modelrouter.v9.capabilities.normalize import MODEL_IDS
from modelrouter.v9.training.trajectory_material import (
    action_excerpt, reference_candidate, text_content, tool_result,
)


DATA_ROOT = Path(__file__).resolve().parents[4] / "data" / "v9"
GROUPS = {"S1": "model_comparison", "S2": "agent_auxiliary", "S3": "system_auxiliary"}
PUBLIC_TRAJECTORIES = {"TRA-001", "TRA-002"}
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
    "execution_mode", "cost_scope",
)


def iter_rows(path):
    """Read existing files without loading model weights or whole source tables."""
    path = Path(path)
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        source = pq.ParquetFile(path)
        columns = [name for name in (
            "instance_id", "trajectory_id", "traj_id", "messages", "resolved",
            "dataset_revision", "hf_dataset_name",
        ) if name in source.schema_arrow.names]
        index = 0
        for batch in source.iter_batches(batch_size=16, columns=columns):
            for row in batch.to_pylist():
                index += 1
                yield index, row
        return
    if str(path) == "-" or path.suffix == ".gz":
        stream = sys.stdin if str(path) == "-" else gzip.open(path, "rt", encoding="utf8")
        try:
            for index, line in enumerate(stream, 1):
                if line.strip():
                    yield index, json.loads(line)
        finally:
            if stream is not sys.stdin:
                stream.close()
        return
    yield from _source_rows(str(path))


def decision_state(pre, task_id=None):
    """Use the same serializer consumed by the existing serving adapters."""
    values = {name: pre.get(name) for name in PreDecisionState.model_fields}
    features = {name: pre[name] for name in SOURCE_PRE_FIELDS if name in pre}
    history = pre.get("history_snippet")
    if features:
        history = json.dumps({"observed_history": history, "source_pre_decision_features": features},
                             ensure_ascii=False)
    if values.get("context_tokens_approx") is None:
        values["context_tokens_approx"] = (pre.get("input_length") if pre.get("input_length") is not None
                                           else pre.get("prompt_tokens"))
    if values.get("task_domain") is None:
        values["task_domain"] = pre.get("task_domain")
    prompt = next((pre[name] for name in ("prompt", "prompt_snippet", "initial_prompt_snippet")
                   if pre.get(name) is not None), None)
    values.update(
        task_id=pre.get("task_id") or task_id, prompt=prompt,
        history_snippet=history,
        feature_training_status="FEATURE_NOT_TRAINED",
    )
    values["capability_cards"] = pre.get("capability_cards") or []
    return PreDecisionState.model_validate(values)


def offline_teacher_state(row, pre, provenance):
    """Import the existing assessor's assessment/metrics pair; never call a teacher."""
    saved = row.get("offline_teacher_state") or pre.get("offline_teacher_state") or {}
    assessment = copy.deepcopy(saved.get("assessment", pre.get("teacher_assessment")))
    metrics = copy.deepcopy(saved.get("metrics", row.get("teacher_metrics") or {}))
    result = {"schema_version": 1, "status": "NOT_GENERATED", "origin": "IMPORTED_OFFLINE",
              "assessment": None, "metrics": metrics,
              "dataset_revision": saved.get("dataset_revision")}
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


def build_offline_prefix_input(row, state_factory):
    """Replay recorded messages into an injected AgentState; limits come from the caller."""
    from modelrouter.agent.state import EpisodeStatus, StepTrace

    provenance = row["provenance"]
    messages = copy.deepcopy(row.get("observed_messages"))
    if not isinstance(messages, list):
        raise ValueError("Full observed prefix messages are required")
    completed = sum(message.get("role") == "assistant" for message in messages)
    if completed != provenance.get("observed_through_step"):
        raise ValueError("Observed generation count differs from the saved cutoff")
    pre = row.get("pre_decision_state")
    if pre is None:
        pre = row.get("state", {})
        pre = json.loads(pre) if isinstance(pre, str) else pre
        pre = pre.get("pre_decision_state", pre)
    info = {"task_id": provenance["task_id"], "episode_id": provenance["episode_id"],
            "completed_generations": completed, "pre_decision_state": copy.deepcopy(pre),
            "source_usage_status": "NOT_REPORTED", "limits_scope": "CALLER_OFFLINE_POLICY"}
    state = state_factory(info)
    if state.task_id != info["task_id"] or state.episode_id != info["episode_id"]:
        raise ValueError("Offline state must retain the source task and episode identities")
    state.step_index, state.history = completed, []
    state.current_phase = pre.get("phase")
    state.status = EpisodeStatus.RUNNING
    state.tool_error_count = 0
    state.task_prompt = next((text_content(message) for message in messages if message.get("role") == "user"), "")
    generation, command, thought = 0, None, ""
    for message in messages:
        if message.get("role") == "assistant":
            generation += 1
            thought = text_content(message)
            calls = message.get("tool_calls") or []
            if len(calls) != 1:
                command = None
                continue
            function = calls[0].get("function", calls[0])
            arguments = function.get("arguments")
            arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
            command = arguments.get("command") if isinstance(arguments, dict) else None
        elif message.get("role") == "tool" or (message.get("role") == "user" and generation):
            code, output = tool_result(message)
            if command is None or code is None:
                raise ValueError("Recorded tool command and exit status are required")
            state.history.append(StepTrace(
                step_index=generation, phase=state.current_phase, selected_action={}, thought=thought,
                tool_action=command, tool_observation=output, tool_exit_code=code,
                prompt_tokens=None, completion_tokens=None, reasoning_tokens=None, cached_tokens=None,
                step_cost_usd=None, step_duration_sec=None, timestamp=None,
            ))
            state.tool_error_count += int(code != 0)
    return state, messages


def _router_input_text(row, decision):
    """Reuse online task/tool compaction; the complete record remains unchanged."""
    if row.get("_meta", {}).get("input_kind") != "TRAJECTORY_PREFIX":
        return decision.router_text()
    from modelrouter.agent.state import AgentState
    from modelrouter.v9.runtime.context import compact_router_state

    def factory(info):
        return AgentState(info["task_id"], info["episode_id"], "V9_OFFLINE_DATA_REPLAY")

    try:
        state, messages = build_offline_prefix_input(dict(row, pre_decision_state=decision.model_dump()), factory)
    except (KeyError, ValueError):
        return decision.router_text()
    compact = compact_router_state(state, messages, decision.model_dump())
    return PreDecisionState.model_validate(compact).router_text()


def generate_offline_teacher_material(*, assessor, state_factory,
        prefixes_path=DATA_ROOT / "prepared/trajectory_prefixes/train.jsonl", max_prefixes=6,
        summary_path=None):
    """Use the existing assessor and trigger with its budget-aware injected Provider."""
    from modelrouter.v9.teacher.assessor import REFERENCE_FIELDS
    from modelrouter.v9.teacher.trigger import TeacherTrigger

    path = Path(prefixes_path).resolve()
    rows = [row for _, row in iter_rows(path)]
    triggers, assessments, request_metrics = {}, {}, {}
    selected = sorted((row for row in rows if row.get("_meta", {}).get("input_kind") == "TRAJECTORY_PREFIX"),
                      key=lambda row: (row["provenance"]["episode_id"], row["provenance"]["observed_through_step"]))
    changed, metrics_rows = {}, []
    for row in selected[:max_prefixes]:
        identity = row["provenance"]["stable_record_id"]
        try:
            state, messages = build_offline_prefix_input(row, state_factory)
        except (ValueError, KeyError) as exc:
            metrics = {"status": "SOURCE_CONTEXT_MISSING", "error_type": type(exc).__name__,
                       "provider_request_attempted": False, "cost_scope": "DATA_PREPARATION"}
            updated = copy.deepcopy(row)
            updated["offline_teacher_state"] = {"schema_version": 1, "assessment": None, "metrics": metrics}
        else:
            episode = state.episode_id
            trigger = triggers.setdefault(episode, TeacherTrigger())
            if trigger.episode_id != episode:
                trigger.reset(episode)
            for _ in range(state.step_index - trigger.generation_count):
                trigger.after_generation()
            reason = trigger.reason(state)
            saved = offline_teacher_state(row, row.get("pre_decision_state", {}), row["provenance"])
            cached = saved["assessment"]
            if cached and (cached["assessed_through_step"] == state.step_index or
                           (reason is None and trigger.signals(state) == trigger.last_signals)):
                current_refs = [{name: ref[name] for name in REFERENCE_FIELDS}
                                for ref in assessor.load_references()]
                if cached["reference_ids"] != current_refs:
                    cached = None
            else:
                cached = None
            if cached:
                assessment = copy.deepcopy(cached)
                source_metrics = saved["metrics"].get("source_request_metrics", saved["metrics"])
                metrics = {"status": "REUSED", "provider_request_attempted": False,
                           "teacher_model_id": assessment["teacher_model_id"], "cost_usd": 0,
                           "native_effort": assessment.get("native_effort", source_metrics.get("native_effort")),
                           "assessed_through_step": assessment["assessed_through_step"],
                           "source_request_metrics": copy.deepcopy(source_metrics)}
                if assessment["assessed_through_step"] == state.step_index:
                    trigger.record_attempt(state)
                assessments[episode], request_metrics[episode] = assessment, copy.deepcopy(source_metrics)
            elif reason:
                assessment, metrics = assessor.assess(state, messages, reason)
                trigger.record_attempt(state)
                assessments[episode], request_metrics[episode] = assessment, copy.deepcopy(metrics)
            else:
                if assessments.get(episode) is not None and trigger.signals(state) != trigger.last_signals:
                    assessments[episode] = None
                assessment = copy.deepcopy(assessments.get(episode))
                metrics = {"status": "REUSED" if assessment else "NOT_TRIGGERED",
                           "provider_request_attempted": False,
                           "observed_generations": trigger.generation_count,
                           "observed_through_step": state.step_index,
                           "assessed_through_step": assessment.get("assessed_through_step") if assessment else None}
                if assessment:
                    metrics.update(source_request_metrics=request_metrics[episode], cost_usd=0,
                                   teacher_model_id=assessment.get("teacher_model_id"))
            alias = ("ALIAS_SMOKE" in str(metrics.get("execution_mode", ""))
                     or "ALIAS_SMOKE" in str((assessment or {}).get("execution_mode", ""))
                     or bool(getattr(assessor.provider, "alias_mapping", None))
                     or (metrics.get("teacher_model_id") is not None and
                         metrics["teacher_model_id"] != assessor.model_id))
            mode = "OFFLINE_TEACHER_ALIAS_SMOKE" if alias else "OFFLINE_TEACHER"
            metrics.update(role="offline_teacher", cost_scope="DATA_PREPARATION", execution_mode=mode,
                           source_episode_id=episode, observed_generations=trigger.generation_count,
                           limits_scope="CALLER_OFFLINE_POLICY", source_usage_status="NOT_REPORTED")
            metrics.setdefault("native_effort", assessor.native_effort)
            if assessment:
                assessment = dict(assessment, execution_mode=mode, cost_scope="DATA_PREPARATION")
            updated = copy.deepcopy(row)
            updated["offline_teacher_state"] = {"schema_version": 1, "assessment": assessment, "metrics": metrics}
        prepared, error = prepare_record(updated, updated["provenance"]["split"])
        if error:
            raise ValueError(error)
        changed[identity] = prepared
        metrics_rows.append(metrics)
    with path.open("w", encoding="utf8") as stream:
        for row in rows:
            stream.write(json.dumps(changed.get(row["provenance"]["stable_record_id"], row), ensure_ascii=False) + "\n")
    requests = [item for item in metrics_rows if item.get("provider_request_attempted") is True]
    totals, known_totals = {}, {}
    for name in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens",
                 "cost_usd", "actual_billed_cost_usd"):
        values = [item[name] for item in requests if isinstance(item.get(name), (int, float))]
        known_totals[name] = sum(values) if values else None
        totals[name] = sum(values) if requests and len(values) == len(requests) else None
    report = {"prefix_rows": len(changed), "teacher_generation_requests": len(requests),
              "generated_assessments": sum(item.get("status") == "SUCCESS" for item in requests),
              "usable_assessments": sum(row["offline_teacher_state"]["status"] == "GENERATED"
                                        for row in changed.values()),
              "request_usage_totals": totals,
              "known_usage_totals": known_totals,
              "missing_usage_request_count": sum(
                  item.get("prompt_tokens") is None or item.get("completion_tokens") is None
                  for item in requests),
              "status_counts": dict(Counter(item.get("status") for item in metrics_rows)),
              "cost_scope": "DATA_PREPARATION", "metrics": metrics_rows}
    summary_path = Path(summary_path) if summary_path else path.parent.parent / "summary.json"
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf8"))
        statuses, models = Counter(), Counter()
        for key in summary["counts"]:
            for _, row in iter_rows(summary_path.parent / key):
                teacher = row["offline_teacher_state"]
                statuses[teacher["status"]] += 1
                if teacher["assessment"]:
                    models[teacher["assessment"]["teacher_model_id"]] += 1
        summary.update(teacher_status_counts=dict(statuses), teacher_model_ids=dict(models),
                       teacher_data_status=("GENERATED" if statuses["GENERATED"] == sum(statuses.values())
                                            else "PARTIAL" if statuses["GENERATED"] else "NOT_GENERATED"),
                       teacher_generation_requests=summary.get("teacher_generation_requests", 0) + len(requests),
                       offline_teacher_preparation=report)
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    return report


def prepare_record(row, split, dataset_revision=None, *, capability_snapshot=None, candidates=()):
    """Keep actual choice identities and targets; auxiliary labels remain auxiliary."""
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
    if source_id not in MATRIX_ALLOWED_SOURCES or group not in GROUPS:
        return None, "SOURCE_OR_TARGET_NOT_SUPPORTED"
    if meta.get("target") not in MATRIX_TARGETS[group]:
        return None, "SOURCE_OR_TARGET_NOT_SUPPORTED"
    if provenance.get("split") not in (None, split):
        return None, "OTHER_SPLIT"
    questions = copy.deepcopy(row.get("questions", {}))
    expected = copy.deepcopy(row.get("expected", {}))
    if not questions or not expected:
        return None, "MISSING_TARGET"
    for qid, question in questions.items():
        label = expected.get(qid)
        if label is None:
            return None, "MISSING_TARGET"
        if question.get("type") == "choice" and label not in question.get("criteria", {}):
            return None, "LABEL_OUTSIDE_CHOICES"
        if question.get("type") == "noul" and not isinstance(label, bool):
            return None, "UNKNOWN_OUTCOME"
        if "label" in question and question["label"] != label:
            return None, "TARGET_CONFLICT"
        if question.get("type") == "score" and (
            type(label) is not int or not 0 <= label < len(question.get("criteria", []))
        ):
            return None, "LABEL_OUTSIDE_CHOICES"
        question["label"] = label
        if meta.get("target"):
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
    task_id = provenance.get("task_id") or provenance.get("instance_id")
    decision = decision_state(pre, task_id)
    provenance["split"] = split
    if provenance.get("dataset_revision") is None:
        provenance["dataset_revision"] = dataset_revision
    meta.update(
        auxiliary_not_model_choice=group != "S1",
        teacher_data_status="GENERATED" if teacher["assessment"] else "NOT_GENERATED",
        offline_teacher_status=teacher["status"],
        feature_training_status="FEATURE_NOT_TRAINED", original_target=meta.get("target"),
        supervision_qualification="PRESERVED_SOURCE_TARGET",
    )
    result = {**row, "provenance": provenance, "state": _router_input_text(row, decision),
              "pre_decision_state": decision.model_dump(), "questions": questions,
              "expected": expected, "teacher_assessment": decision.teacher_assessment,
              "offline_teacher_state": teacher, "candidate_actions": actions,
              "capability_cards": decision.capability_cards,
              "capability_snapshot_id": decision.capability_snapshot_id,
              "feature_training_status": "FEATURE_NOT_TRAINED",
              "_meta": meta}
    return result, None


def v8_records(views_dir, split, dataset_revision=None, skipped=None):
    """Reuse the V8 loader, retaining the original record's identity and evidence."""
    dataset = V8ExtensionDataset(Path(views_dir), split)
    methods = {"S1": ("router_choice", dataset.iter_router_choice),
               "S2": ("observed_agent_outcome", dataset.iter_agent_outcome),
               "S3": ("cache_reuse_opportunity", dataset.iter_cache_reuse)}
    for group, (name, method) in methods.items():
        path = Path(views_dir) / f"{name}_{split}.jsonl.gz"
        if not path.is_file():
            continue
        for (line_number, original), loaded in zip(iter_rows(path), method()):
            provenance = {**original.get("provenance", {}), "split": original.get("split", split),
                          "task_id": original.get("task_id"), "source_file": str(path),
                          "source_line": line_number,
                          "episode_id": original.get("episode_id"),
                          "trajectory_id": original.get("episode_id"),
                          "dataset_revision": original.get("provenance", {}).get("dataset_revision") or dataset_revision}
            provenance.setdefault("stable_record_id", original.get("battle_id") or
                                  f"{provenance.get('source_id')}:{path.name}:{line_number}")
            pre = original.get("state_before", {})
            if group == "S1":
                pre = {"prompt": loaded["prompt"]}
                criteria = dict.fromkeys(loaded["candidates"], "")
                questions = {"model_choice": {"type": "choice", "criteria": criteria}}
                expected = {"model_choice": loaded["winner"]}
                target = "human_pairwise_preference"
            elif group == "S2":
                outcome = loaded["outcome"]
                if outcome not in ("SUCCESS", "FAILURE"):
                    if skipped is not None:
                        skipped["UNKNOWN_OUTCOME"] += 1
                    continue
                pre = {**pre, "step_index": original.get("step_id")}
                questions = {"trajectory_resolved": {"type": "noul", "criteria": {"false": "Unresolved", "true": "Resolved"}}}
                expected = {"trajectory_resolved": outcome == "SUCCESS"}
                target = "observed_success" if outcome == "SUCCESS" else "observed_failure"
            else:
                provenance.setdefault("source_id", "CACHE-001")
                pre = {name: original.get(name) for name in
                       ("input_length", "prefix_block_count", "prefix_hash_sample")}
                pre.update(arrival_timestamp=original.get("timestamp"),
                           trace_type=provenance.get("trace_type"))
                if original.get("estimated_reusable_blocks") is None or original.get("prefix_block_count") is None:
                    if skipped is not None:
                        skipped["MISSING_TARGET"] += 1
                    continue
                ratio = loaded["reusable_ratio"]
                questions = {"historical_prefix_reuse_tier": {"type": "score", "criteria": ["none", "under 50%", "under 80%", "80% or more"]}}
                expected = {"historical_prefix_reuse_tier": 0 if ratio <= 0 else 1 if ratio < .5 else 2 if ratio < .8 else 3}
                target = "prefix_reuse_opportunity"
            yield {"provenance": provenance, "state": pre, "questions": questions,
                   "expected": expected, "_meta": {"supervision_class": group,
                   "target": target, "input_kind": "V8_VIEW", "source_view": original.get("view_type"),
                   "label_evidence": original.get("label_nature", original.get("evidence_label"))}}




def trajectory(row, source_id, path, row_number, anchor):
    messages = row.get("messages")
    if isinstance(messages, str):
        messages = json.loads(messages)
    if not isinstance(messages, list):
        return None
    messages = [message for message in messages if isinstance(message, dict)]
    outcome = row.get("resolved")
    outcome = True if outcome is True or outcome == 1 else False if outcome is False or outcome == 0 else None
    return {"source_id": source_id, "source_path": row.get("source_path") or str(path),
            "source_row": row.get("source_row", row_number),
            "task_id": row.get("instance_id"), "episode_id": row.get("trajectory_id", row.get("traj_id")),
            "dataset_revision": row.get("dataset_revision") or anchor.get("dataset_revision"),
            "split": "train", "messages": messages, "resolved": outcome, "anchor": anchor}


def trajectory_prefixes(episode):
    """Emit causal states before generations 1, 4 and 8, with observed auxiliary targets."""
    history, prompt, step, calls, errors = [], None, 0, 0, 0
    last_code = last_result = None
    for index, message in enumerate(episode["messages"]):
        role = message.get("role")
        if role == "user" and prompt is None:
            prompt = text_content(message)
        if role == "assistant":
            step += 1
            action, nature, has_action = extract_swesmith_action(message, "tool")
            if step in (1, 4, 8) and has_action:
                pre = {"prompt": prompt, "history_snippet": json.dumps(history[-8:], ensure_ascii=False),
                       "task_domain": "software_engineering",
                       "history_length": len(history), "step_index": step,
                       "context_chars": sum(len(text_content(item)) for item in history),
                       "prior_tool_calls_count": calls, "prior_error_signals_count": errors,
                       "last_tool_exit_code": last_code, "last_observation_summary": last_result}
                ref = {**episode["anchor"], "source_id": episode["source_id"],
                       "source_file": episode["source_path"], "source_line": episode["source_row"],
                       "task_id": episode["task_id"], "trajectory_id": episode["episode_id"],
                       "stable_record_id": f"{episode['source_id']}:{episode['episode_id']}:{step}",
                       "primary_supervision_class": "S2", "split": "train",
                       "label_evidence": {"observed_action": [f"messages[{index}]"]}}
                raw = {"pre_decision_state": pre, "observed_decision": {"action_type": action}}
                sample = _example(episode["source_id"], raw, ref, "observed_action")
                sample["provenance"].update(task_id=episode["task_id"], episode_id=episode["episode_id"],
                    dataset_revision=episode["dataset_revision"], observed_through_step=step - 1)
                sample["provenance"].update({name: episode["anchor"][name] for name in (
                    "assigned_layer", "quality_grade", "train_eligible", "source_policy_train_allowed",
                    "train_anchor_file", "qualification_source_path") if name in episode["anchor"]})
                sample["provenance"]["train_anchor_stable_id"] = episode["anchor"].get("stable_record_id")
                sample["_meta"].update(action_nature=nature, observed_outcome=episode["resolved"],
                                      input_kind="TRAJECTORY_PREFIX")
                sample["observed_messages"] = copy.deepcopy(history)
                yield sample
        elif role == "tool" or (role == "user" and step > 0):
            calls += 1
            last_code, last_result = tool_result(message)
            errors += int(last_code is not None and last_code != 0)
            last_result = last_result[:2000]
        history.append({name: message[name] for name in ("role", "content", "tool_calls", "tool_call_id")
                        if name in message})


def prepare(typed_root=None, *, inputs=(), v8_views=None, preview_root=None, trajectories=(),
            out_dir=DATA_ROOT / "prepared", references_path=DATA_ROOT / "references" / "two_references.json",
            splits=("train", "val"), limit_per_view=64, max_episodes=1000, dataset_revision=None,
            capabilities_dir=DEFAULT_DATA_DIR, candidates=()):
    out_dir, references_path = Path(out_dir), Path(references_path)
    counts, eligible, skipped, saved_sources = Counter(), Counter(), Counter(), Counter()
    missing, pools, anchors, seen, references = [], {}, {}, set(), {}
    snapshot = load_current(capabilities_dir)
    candidates = [candidate_action(action) for action in candidates]
    teacher_statuses, teacher_models, target_scopes, prefix_counts = Counter(), Counter(), Counter(), Counter()
    inline_trajectories, inline_counts = [], Counter()
    fixed_reference_kinds = set()
    if references_path.is_file():
        for ref in json.loads(references_path.read_text(encoding="utf8")):
            if (ref.get("reference_kind") in ("efficient_success", "failure_recovery")
                    and ref.get("source_id") in PUBLIC_TRAJECTORIES and ref.get("split") == "train"
                    and ref.get("success_evidence", {}).get("value") is True):
                references[ref["reference_kind"]] = ref
                fixed_reference_kinds.add(ref["reference_kind"])

    def save(row, split):
        prepared, reason = prepare_record(row, split, dataset_revision,
                                          capability_snapshot=snapshot, candidates=candidates)
        if prepared is None:
            skipped[reason] += 1
            return
        provenance, meta = prepared["provenance"], prepared["_meta"]
        if (split == "train" and meta["supervision_class"] == "S2"
                and meta.get("input_kind") not in ("TRAJECTORY_PREFIX", "V8_VIEW")
                and provenance["source_id"] in PUBLIC_TRAJECTORIES and provenance.get("trajectory_id")):
            anchors.setdefault((provenance["source_id"], provenance["trajectory_id"]), {
                **provenance, "typed_outcome": prepared["expected"].get("trajectory_resolved"),
            })
        group = GROUPS[meta["supervision_class"]]
        is_prefix = meta.get("input_kind") == "TRAJECTORY_PREFIX"
        identity = (split, provenance["source_id"], provenance.get("stable_record_id"),
                    provenance.get("task_id"), provenance.get("trajectory_id"),
                    provenance.get("dataset_revision"),
                    json.dumps(prepared["questions"], ensure_ascii=False), prepared["state"])
        if identity in seen:
            skipped["DUPLICATE"] += 1
            return
        seen.add(identity)
        key = f"{group}/{split}.jsonl"
        eligible[key] += 1
        bucket = pools.setdefault(key, {}).setdefault((provenance["source_id"], meta["target"], is_prefix), [])
        if not limit_per_view or len(bucket) < limit_per_view:
            bucket.append(prepared)

    for split in splits:
        if typed_root:
            for group in GROUPS:
                path = Path(typed_root) / split / f"{group}.jsonl"
                if path.is_file():
                    for _, row in iter_rows(path):
                        save(row, split)
                else:
                    missing.append(str(path))
        if v8_views:
            for row in v8_records(v8_views, split, dataset_revision, skipped):
                save(row, split)
    for path in inputs:
        if str(path) != "-" and not Path(path).is_file():
            missing.append(str(path))
            continue
        for row_number, row in iter_rows(path):
            if "trajectory_record" in row:
                inline_counts[str(path)] += 1
                if inline_counts[str(path)] <= max_episodes:
                    inline_trajectories.append((row.get("source_id"), path, row_number, row["trajectory_record"]))
                else:
                    skipped["TRAJECTORY_LIMIT_REACHED"] += 1
                continue
            split = row.get("candidate_reference", row.get("provenance", {})).get("split")
            if split in splits:
                save(row, split)
    if preview_root:
        loader = MultiViewSupervisionLoader(PublicDatasetLoader(Path(preview_root)))
        for method in (loader.get_s1_records, loader.get_s2_records, loader.get_s3_records):
            for row in method(limit=limit_per_view or None):
                split = row.get("provenance", {}).get("split")
                if not row.get("questions"):
                    skipped["UNTYPED_PREVIEW"] += 1
                elif split in splits:
                    save(row, split)
    def raw_episodes():
        yield from inline_trajectories
        for source_id, path in trajectories:
            if str(path) != "-" and not Path(path).is_file():
                missing.append(str(path))
                continue
            for row_number, row in iter_rows(path):
                if row_number > max_episodes:
                    break
                yield source_id, path, row_number, row

    for source_id, path, row_number, row in raw_episodes():
        if source_id not in PUBLIC_TRAJECTORIES:
            skipped["SOURCE_OR_TARGET_NOT_SUPPORTED"] += 1
            continue
        episode_id = row.get("trajectory_id", row.get("traj_id"))
        anchor = anchors.get((source_id, episode_id))
        if anchor is None:
            skipped["NO_TYPED_TRAIN_ANCHOR"] += 1
            continue
        episode = trajectory(row, source_id, path, row_number, anchor)
        if episode is None:
            skipped["MISSING_TRAJECTORY_MESSAGES"] += 1
            continue
        if (anchor.get("typed_outcome") is not None and episode["resolved"] is not None
                and anchor["typed_outcome"] != episode["resolved"]):
            skipped["PUBLIC_OUTCOME_CONFLICT"] += 1
            continue
        for sample in trajectory_prefixes(episode):
            save(sample, "train")
        candidate = reference_candidate(episode)
        if candidate:
            kind = candidate["reference_kind"]
            previous = references.get(kind)
            if kind not in fixed_reference_kinds and (
                    previous is None or candidate["observed_through_step"] < previous["observed_through_step"]):
                references[kind] = candidate

    for key, buckets in pools.items():
        streams = []
        for is_prefix in (False, True):
            bundles = [bucket for (_, _, prefix), bucket in buckets.items() if prefix == is_prefix]
            rows = (row for bundle in zip_longest(*bundles) for row in bundle if row is not None)
            streams.append(islice(rows, limit_per_view) if limit_per_view else rows)
        path = out_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf8") as stream:
            for row in (row for stream_rows in streams for row in stream_rows):
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                counts[key] += 1
                saved_sources[f"{key}:{row['provenance']['source_id']}:{row['_meta']['target']}"] += 1
                teacher = row["offline_teacher_state"]
                if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX":
                    prefix_counts[row["provenance"]["split"]] += 1
                teacher_statuses[teacher["status"]] += 1
                if teacher["assessment"]:
                    teacher_models[teacher["assessment"]["teacher_model_id"]] += 1
                if row["_meta"]["supervision_class"] == "S1":
                    for label in row["expected"].values():
                        action = candidate_action(label)
                        if action["model_id"] in MODEL_IDS:
                            target_scopes["v9_model_choice"] += 1
                            if action["native_effort"] is not None:
                                target_scopes["v9_model_effort_choice"] += 1
                else:
                    target_scopes["auxiliary_not_model_choice"] += 1

    trainer_views = {}
    for split in splits:
        for group in GROUPS.values():
            key = f"{group}/{split}.jsonl"
            path = out_dir / key
            if key not in counts and (path.is_file() or path.is_symlink()):
                path.unlink()
                if not any(path.parent.iterdir()):
                    path.parent.rmdir()
        for name, group in GROUPS.items():
            key = f"{group}/{split}.jsonl"
            alias = out_dir / split / f"{name}.jsonl"
            if alias.is_file() or alias.is_symlink():
                alias.unlink()
            if key in counts:
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.symlink_to(Path("..") / key)
                trainer_views.setdefault(split, {})[name] = str(Path(split) / f"{name}.jsonl")
            elif alias.parent.is_dir() and not any(alias.parent.iterdir()):
                alias.parent.rmdir()
        prefix_alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        if prefix_alias.is_file() or prefix_alias.is_symlink():
            prefix_alias.unlink()
        if prefix_counts[split]:
            prefix_alias.parent.mkdir(parents=True, exist_ok=True)
            prefix_alias.symlink_to(Path("..") / "agent_auxiliary" / f"{split}.jsonl")
        elif prefix_alias.parent.is_dir() and not any(prefix_alias.parent.iterdir()):
            prefix_alias.parent.rmdir()
    kinds = ("efficient_success", "failure_recovery")
    missing_kinds = [kind for kind in kinds if kind not in references]
    if not missing_kinds and len(fixed_reference_kinds) != 2:
        references_path.parent.mkdir(parents=True, exist_ok=True)
        references_path.write_text(json.dumps([references[kind] for kind in kinds], ensure_ascii=False, indent=2), encoding="utf8")
    summary = {"counts": dict(counts), "skipped": dict(skipped), "missing_inputs": missing,
               "eligible_counts": dict(eligible), "source_target_counts": dict(saved_sources),
               "limited_counts": {key: count - counts[key] for key, count in eligible.items() if count > counts[key]},
               "trainer_root": ".", "trainer_views": trainer_views,
               "trajectory_prefix_count": sum(prefix_counts.values()),
               "references_status": "READY" if not missing_kinds else "MISSING",
               "fixed_references_reused": len(fixed_reference_kinds),
               "missing_reference_kinds": missing_kinds,
               "references_path": os.path.relpath(references_path, out_dir) if not missing_kinds else None,
               "dataset_revision": dataset_revision,
               "teacher_data_status": ("GENERATED" if teacher_statuses["GENERATED"] == sum(counts.values()) and counts
                                       else "PARTIAL" if teacher_statuses["GENERATED"] else "NOT_GENERATED"),
               "offline_teacher_schema_version": 1, "teacher_status_counts": dict(teacher_statuses),
               "teacher_model_ids": dict(teacher_models), "teacher_generation_requests": 0,
               "capability_snapshot_id": snapshot.get("snapshot_id"),
               "capability_evidence_status": snapshot.get("capability_evidence_status", "NOT_MEASURED"),
               "capability_measured_metric_count": snapshot.get("measured_metric_count", 0),
               "supplied_auxiliary_candidates": candidates,
               "v9_model_choice_target_count": target_scopes["v9_model_choice"],
               "v9_model_effort_target_count": target_scopes["v9_model_effort_choice"],
               "auxiliary_not_model_choice_count": target_scopes["auxiliary_not_model_choice"],
               "supervision_qualification": "PRESERVED_SOURCE_TARGETS_AND_SPLITS",
               "feature_training_status": "FEATURE_NOT_TRAINED",
               "schema_fields_missing": [name for name in NEW_FEATURE_FIELDS if name not in PreDecisionState.model_fields],
               "supervision_note": "S2/S3 and trajectory prefixes are auxiliary, not optimal model labels."}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    return summary


def reencode_prepared(out_dir=DATA_ROOT / "prepared"):
    """Retain raw records, use the shared formatter and store prefixes in physical S2."""
    out_dir = Path(out_dir)
    summary_path = out_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf8"))
    legacy_prefixes = {}
    for split in summary["trainer_views"]:
        alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        if alias.is_file() and not alias.is_symlink():
            legacy_prefixes[split] = [row for _, row in iter_rows(alias)]
    counts, sources, statuses, models, prefixes = Counter(), Counter(), Counter(), Counter(), Counter()
    trainer_views = {}
    for split in summary["trainer_views"]:
        for name, group in GROUPS.items():
            key = f"{group}/{split}.jsonl"
            path = out_dir / key
            if not path.is_file():
                continue
            rows = [row for _, row in iter_rows(path)]
            if name == "S2" and split in legacy_prefixes:
                existing = {row["provenance"]["stable_record_id"] for row in rows
                            if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX"}
                rows.extend(row for row in legacy_prefixes[split]
                            if row["provenance"]["stable_record_id"] not in existing)
            with path.open("w", encoding="utf8") as stream:
                for row in rows:
                    decision = decision_state(row["pre_decision_state"], row["provenance"].get("task_id"))
                    row["state"] = _router_input_text(row, decision)
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    counts[key] += 1
                    sources[f"{key}:{row['provenance']['source_id']}:{row['_meta']['target']}"] += 1
                    teacher = row["offline_teacher_state"]
                    statuses[teacher["status"]] += 1
                    if teacher["assessment"]:
                        models[teacher["assessment"]["teacher_model_id"]] += 1
                    if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX":
                        prefixes[split] += 1
            trainer_views.setdefault(split, {})[name] = str(Path(split) / f"{name}.jsonl")
        alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        target = Path("..") / "agent_auxiliary" / f"{split}.jsonl"
        if prefixes[split] and (not alias.is_symlink() or Path(os.readlink(alias)) != target):
            if alias.is_file() or alias.is_symlink():
                alias.unlink()
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to(target)
    eligible = summary.get("eligible_counts", {})
    for split in trainer_views:
        old_key = f"trajectory_prefixes/{split}.jsonl"
        if old_key in eligible:
            key = f"agent_auxiliary/{split}.jsonl"
            eligible[key] = eligible.get(key, 0) + eligible.pop(old_key)
    references = summary.get("references_path")
    if references and Path(references).is_absolute():
        references = os.path.relpath(references, out_dir)
    summary.update(counts=dict(counts), source_target_counts=dict(sources),
                   eligible_counts=eligible, trainer_root=".", trainer_views=trainer_views,
                   limited_counts={key: value - counts[key] for key, value in eligible.items() if value > counts[key]},
                   references_path=references, trajectory_prefix_count=sum(prefixes.values()),
                   teacher_status_counts=dict(statuses), teacher_model_ids=dict(models),
                   teacher_data_status=("GENERATED" if counts and statuses["GENERATED"] == sum(counts.values())
                                        else "PARTIAL" if statuses["GENERATED"] else "NOT_GENERATED"),
                   router_serializer="modelrouter.v9.runtime.context.format_router_payload")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--typed-root", type=Path)
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--v8-views", type=Path)
    parser.add_argument("--preview-root", type=Path)
    parser.add_argument("--trajectory", action="append", default=[], metavar="SOURCE_ID=PATH")
    parser.add_argument("--out-dir", type=Path, default=DATA_ROOT / "prepared")
    parser.add_argument("--reencode-prepared", action="store_true",
                        help="Reencode current physical views and link prefixes to S2; no teacher or network requests.")
    parser.add_argument("--references-path", type=Path, default=DATA_ROOT / "references" / "two_references.json")
    parser.add_argument("--split", choices=("train", "val"), action="append")
    parser.add_argument("--limit-per-view", type=int, default=64,
                        help="Maximum rows per view; source/target buckets are interleaved. Use 0 for all typed rows.")
    parser.add_argument("--max-episodes", type=int, default=1000,
                        help="Maximum raw trajectory rows scanned per input file.")
    parser.add_argument("--dataset-revision")
    parser.add_argument("--capabilities-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="Existing capability directory or current.json; preparation never refreshes it.")
    parser.add_argument("--candidate-action", action="append", default=[], metavar="MODEL[:EFFORT]",
                        help="Candidate input for auxiliary views only; original S1 choices remain unchanged.")
    args = parser.parse_args(argv)
    if args.reencode_prepared:
        print(json.dumps(reencode_prepared(args.out_dir), ensure_ascii=False))
        return 0
    summary = prepare(args.typed_root, inputs=args.input, v8_views=args.v8_views,
        preview_root=args.preview_root, trajectories=[item.split("=", 1) for item in args.trajectory],
        out_dir=args.out_dir, references_path=args.references_path, splits=args.split or ("train", "val"),
        limit_per_view=args.limit_per_view, max_episodes=args.max_episodes, dataset_revision=args.dataset_revision,
        capabilities_dir=args.capabilities_dir, candidates=args.candidate_action)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
