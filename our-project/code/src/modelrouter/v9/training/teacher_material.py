"""Import and prepare observed, single-Agent teacher assessments."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from .constants import DATA_ROOT
from .material_io import iter_rows
from .supervision import offline_teacher_state, prepare_record
from .prefix_replay import build_offline_prefix_input


def generate_offline_teacher_material(*, assessor, state_factory,
        prefixes_path=DATA_ROOT / "prepared/trajectory_prefixes/train.jsonl", max_prefixes=6,
        summary_path=None):
    """Use the existing assessor and its injected Provider for selected recorded prefixes."""
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
            reason = trigger.reason(state)
            saved = offline_teacher_state(row, row.get("pre_decision_state", {}), row["provenance"])
            cached = saved["assessment"]
            if cached:
                current_refs = [{name: ref[name] for name in REFERENCE_FIELDS}
                                for ref in assessor.load_references()]
                if cached["reference_ids"] != current_refs:
                    cached = None
            if cached and cached["assessed_through_step"] == state.step_index:
                trigger.record_attempt(state)
            if cached and not trigger.assessment_is_current(state):
                cached = None
            if cached:
                assessment = copy.deepcopy(cached)
                source_metrics = saved["metrics"].get("source_request_metrics", saved["metrics"])
                metrics = {"status": "REUSED", "provider_request_attempted": False,
                           "teacher_model_id": assessment["teacher_model_id"], "cost_usd": 0,
                           "native_effort": assessment.get("native_effort", source_metrics.get("native_effort")),
                           "assessed_through_step": assessment["assessed_through_step"],
                           "source_request_metrics": copy.deepcopy(source_metrics)}
                assessments[episode], request_metrics[episode] = assessment, copy.deepcopy(source_metrics)
            elif reason:
                assessment, metrics = assessor.assess(state, messages, reason)
                trigger.record_attempt(state)
                assessments[episode], request_metrics[episode] = assessment, copy.deepcopy(metrics)
            else:
                assessment = copy.deepcopy(assessments.get(episode))
                if assessment and not trigger.assessment_is_current(state):
                    assessment = None
                    assessments[episode] = None
                metrics = {"status": "REUSED" if assessment else "NOT_TRIGGERED",
                           "provider_request_attempted": False,
                           "observed_generations": state.step_index,
                           "observed_through_step": state.step_index,
                           "assessed_through_step": assessment.get("assessed_through_step") if assessment else None}
                if assessment:
                    metrics.update(source_request_metrics=request_metrics[episode], cost_usd=0,
                                   teacher_model_id=assessment.get("teacher_model_id"))
            alias = ("ALIAS_SMOKE" in str(metrics.get("execution_mode", ""))
                     or "ALIAS_SMOKE" in str((assessment or {}).get("execution_mode", ""))
                     or (metrics.get("teacher_model_id") is not None
                         and metrics["teacher_model_id"] != assessor.model_id))
            mode = "OFFLINE_TEACHER_ALIAS_SMOKE" if alias else "OFFLINE_TEACHER"
            metrics.update(role="offline_teacher", cost_scope="DATA_PREPARATION", execution_mode=mode,
                           source_episode_id=episode, observed_generations=state.step_index,
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
              "request_usage_totals": totals, "known_usage_totals": known_totals,
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
