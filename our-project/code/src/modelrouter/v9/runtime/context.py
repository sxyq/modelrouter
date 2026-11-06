"""Character-bounded views of observed Agent state; never alter its messages."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping

from modelrouter.agent.state import StepTrace


TEST_COMMAND = re.compile(r"\b(?:pytest|unittest|ctest)\b|\b(?:npm|pnpm|yarn|cargo|go|mvn)\s+test\b")
TOOL_FAILURE = re.compile(r"^(?:E\s|FAILED |ERROR |FAIL:)|^\w*(?:Error|Exception):|command not found", re.MULTILINE)
WRITE_COMMAND = re.compile(
    r"\b(?:cat\s*>|sed\s+-i\b|git\s+apply\b|apply_patch\b|"
    r"open\([^\n]*,\s*['\"]w['\"]\)|\w+\.write_text\()"
)
_METRIC_FIELDS = ("metric_name", "score_raw", "score_unit", "benchmark_version",
                  "score_scope", "evaluated_native_effort")


def _metric_rows(metrics):
    measured, missing = [], []
    for metric in metrics:
        if metric.get("evidence_status") == "MEASURED" and metric.get("score_raw") is not None:
            measured.append([metric.get(name) for name in _METRIC_FIELDS])
        else:
            missing.append(metric["metric_name"])
    return measured, list(dict.fromkeys(missing))


def format_router_payload(payload: Mapping) -> str:
    """One T/M/H representation for online decisions and prepared training."""
    data = dict(payload)
    task = {name: data.get(name) for name in (
        "task_id", "task_domain", "step_index", "phase", "budget_status", "budget_remaining_usd",
        "steps_remaining", "elapsed_time_sec", "time_remaining_sec", "time_budget_sec",
        "agent_state")}
    prompt = data.get("prompt") or ""
    task["prompt"] = task_text(None, [{"role": "user", "content": prompt}], router_view=True)
    teacher = data.get("teacher_assessment")
    assessment = ({name: teacher.get(name) for name in (
        "progress_summary", "main_blocker", "next_milestone",
        "assessed_through_step", "assessed_through_decision_id", "for_decision_id", "phase")}
        if teacher else {"status": "NOT_AVAILABLE"})
    conditions = {row["model_id"]: row for row in data.get("candidate_conditions", [])}
    models = {}
    for card in data.get("capability_cards", []):
        model_id = card["model_id"]
        if model_id not in models:
            metadata = card.get("model_provider_metadata", {})
            models[model_id] = {
                "provider": card.get("model_provider"),
                "revision": card.get("model_revision", "NOT_REPORTED"),
                "supported_native_efforts": metadata.get("native_efforts", "NOT_REPORTED"),
                "context_limits": card.get("model_context_limits", {}),
                "pricing": card.get("model_pricing", {}),
                "capabilities": {name: metadata.get(name, "NOT_MEASURED") for name in
                    ("tool_supported", "input_modalities", "output_modalities", "capability_status")},
                "model_metrics": _metric_rows(card.get("model_metrics", []))[0],
                "reference_metrics": _metric_rows(card.get("reference_metrics", []))[0],
                "metric_fields": list(_METRIC_FIELDS),
                "evidence_status": card.get("model_evidence_status", "NOT_MEASURED"),
                "source_url": card.get("source_url"),
                "condition": conditions.get(model_id, {"availability": "UNKNOWN"}),
                "efforts": [],
            }
        models[model_id]["efforts"].append({
            "native_effort": card.get("native_effort"), "action_id": card["action_id"],
            "evidence_status": card.get("evidence_status", "NOT_MEASURED"),
            "metrics": _metric_rows(card.get("action_metrics", []))[0],
        })
    history = {name: data.get(name) for name in (
        "history_length", "prior_tool_calls_count", "prior_error_signals_count",
        "last_tool_exit_code", "last_observation_summary", "context_chars",
        "context_tokens_approx", "agent_context", "model_time_sec", "tool_time_sec")}
    continuity = dict(data.get("continuity") or {})
    # Runtime identity and old Router input copies are evidence, not Agent state.
    for name in list(continuity):
        if name.startswith("router_") or name in (
            "episode_id", "decision_id", "capability_snapshot_id", "previous_router_run_id",
            "previous_router_checkpoint_id"):
            continuity.pop(name)
    history["continuity"] = continuity
    history["history_snippet"] = data.get("history_snippet")
    groups = {
        "T": task, "teacher_assessment": assessment, "M": models, "H": history,
        "capability_snapshot_id": data.get("capability_snapshot_id"),
        "feature_training_status": data.get("feature_training_status", "FEATURE_NOT_TRAINED"),
    }
    for name in data.get("disabled_information_groups", []):
        groups[name] = {"status": "ABLATION_DISABLED"}
    return json.dumps(groups, ensure_ascii=False, separators=(",", ":"))


def tool_result_phase(command, returncode, output):
    """Derive the phase from an observed command and its actual feedback."""
    if TEST_COMMAND.search(command):
        return "verify"
    if returncode or TOOL_FAILURE.search(output):
        return "recover"
    if WRITE_COMMAND.search(command):
        return "modify"
    return "inspect"


def encoded_group_coverage(state, tokenizer, dropped=0):
    """Locate actual serialized T/M/H spans in the native tokenizer's kept prefix."""
    if not isinstance(state, str) or not state.startswith('{"T":'):
        return {}
    offsets = tokenizer(state, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    kept = len(offsets) - dropped
    result = {}
    for name in ("T", "teacher_assessment", "M", "H"):
        marker = json.dumps(name) + ":"
        start = state.index(marker) + len(marker)
        _, length = json.JSONDecoder().raw_decode(state[start:])
        positions = [i for i, (a, b) in enumerate(offsets) if b > start and a < start + length]
        result[name] = {"status": "FULL" if positions[-1] < kept else "PARTIAL" if positions[0] < kept else "DROPPED",
                        "token_start": positions[0], "token_end": positions[-1] + 1}
    return result


def record_tool_result(state, record_dir, action, output, duration_ms, *, submission=False):
    """Keep the upstream result and attach it to its generating decision."""
    from modelrouter.benchmark.iterations import append, event, now

    command = action["command"]
    extra = output.get("extra", {})
    exit_code = extra.get("actual_exit_code", output["returncode"])
    state.current_phase = tool_result_phase(command, output["returncode"], output["output"])
    state.last_output = output
    state.tool_error_count += int(output["returncode"] != 0)
    state.history.append(StepTrace(
        step_index=state.step_index, phase=state.current_phase,
        selected_action=dict(getattr(state, "last_selected_action", {})), thought="",
        tool_action=command, tool_observation=output["output"] or output.get("exception_info", ""),
        tool_exit_code=exit_code, prompt_tokens=0, completion_tokens=0,
        reasoning_tokens=0, cached_tokens=0, step_cost_usd=0,
        step_duration_sec=duration_ms / 1000,
    ))
    record = {
        "kind": "agent_tool", "timestamp": now(), "episode_id": state.episode_id,
        "step": state.step_index, "decision_id": getattr(state, "last_decision_id", None),
        "router_checkpoint_id": getattr(state, "last_router_checkpoint_id", None),
        "command": command, "tool_call_id": action.get("tool_call_id"),
        "exit_code": exit_code, "duration_ms": duration_ms,
        "output": extra.get("actual_output", output["output"]), "exception_info": output.get("exception_info", ""),
        "adapter_returncode": output["returncode"],
        "submission": submission, "phase": state.current_phase,
        "phase_source": "COMMAND_HEURISTIC",
    }
    append(record_dir / "tool_calls.jsonl", record)
    event(record_dir, "TOOL_END", **record)


def visible_history(state):
    return [step for step in state.history if step.step_index <= state.step_index]


def observed_messages(state, messages):
    visible, generations = [], 0
    for message in messages:
        if message.get("role") == "assistant":
            if generations >= state.step_index:
                break
            generations += 1
        visible.append(message)
    return visible


def task_text(state, messages, *, router_view=False):
    prompt = getattr(state, "task_prompt", "") or next((str(message.get("content") or "")
        for message in messages if message.get("role") == "user"), "")
    if router_view:
        description = re.search(r"<pr_description>(.*?)</pr_description>", prompt, re.DOTALL)
        if description is not None:
            return description.group(1)
    return prompt


def message_chars(messages):
    return sum(len(json.dumps(message, ensure_ascii=False)) for message in messages)


def command_summary(command):
    if len(command) <= 256:
        return command
    return command[:126] + "\n...\n" + command[-125:]


def recent_tools(state, char_limit):
    parts, remaining = [], char_limit
    history = list(reversed(visible_history(state)))
    failure = next((step for step in history if step.tool_exit_code != 0
                    or TOOL_FAILURE.search(step.tool_observation)), None)
    reserve_failure = bool(history and failure is not None and failure is not history[0])
    if reserve_failure:
        history = [history[0], failure] + [step for step in history[1:] if step is not failure]
    for index, step in enumerate(history):
        allowance = remaining // 2 if index == 0 and reserve_failure else remaining
        heading = (f"step={step.step_index} phase={step.phase} exit={step.tool_exit_code}\n"
                   f"command={command_summary(step.tool_action)}\noutput=")
        room = max(0, allowance - len(heading) - 1)
        highlights = "\n".join(line for line in step.tool_observation.splitlines() if TOOL_FAILURE.search(line))
        highlights = highlights[:room // 2]
        tail_room = max(0, room - len(highlights) - bool(highlights))
        output = highlights + ("\n" if highlights else "") + (step.tool_observation[-tail_room:] if tail_room else "")
        part = (heading + output)[:allowance]
        parts.append(part)
        remaining -= len(part) + 1
        if remaining <= 0:
            break
    return "\n".join(parts)


def recent_messages(messages, char_limit):
    parts, remaining = [], char_limit
    for message in reversed(messages):
        if message.get("role") == "system":
            continue
        data = {name: message[name] for name in ("content", "tool_calls", "tool_call_id")
                if name in message}
        heading = f"{message.get('role', 'unknown')}: "
        text = json.dumps(data, ensure_ascii=False)
        room = max(0, remaining - len(heading) - 1)
        part = (heading + (text[-room:] if room else ""))[:remaining]
        parts.append(part)
        remaining -= len(part) + 1
        if remaining <= 0:
            break
    return "\n".join(reversed(parts))


def compact_router_state(state, messages, snapshot, char_limit=6000):
    """The budget covers task/tool text; model cards retain their own evidence."""
    history = visible_history(state)
    task = task_text(state, messages, router_view=True)[:min(char_limit, 2000)]
    tools = recent_tools(state, char_limit - len(task))
    generations = recent_messages([m for m in messages if m.get("role") == "assistant"], 1200)
    result = dict(snapshot, prompt=task, history_snippet=tools, phase=state.current_phase,
                  context_chars=message_chars(messages), context_tokens_approx=(message_chars(messages) + 3) // 4,
                  history_length=len(history), prior_tool_calls_count=len(history),
                  prior_error_signals_count=state.tool_error_count,
                  last_tool_exit_code=0, last_observation_summary="Initial task prompt")
    if history:
        result.update(last_tool_exit_code=history[-1].tool_exit_code,
                      last_observation_summary=(f"command={command_summary(history[-1].tool_action)}\n"
                                                f"output={history[-1].tool_observation[-512:]}"))
    result["agent_context"] = {
        "observed_generation_summary": generations,
        "message_count": len(messages), "context_chars": result["context_chars"],
        "router_task_tool_char_limit": char_limit,
        "router_task_chars": len(task), "router_tool_chars": len(tools),
        "observed_through_step": state.step_index,
        "token_measurement_status": "ESTIMATED_CHARS_DIV_4_NOT_PROVIDER_USAGE",
    }
    modified = next((step for step in reversed(history) if step.tool_exit_code == 0
                     and WRITE_COMMAND.search(step.tool_action)), None)
    result["agent_context"]["last_successful_modification"] = ({"step": modified.step_index,
        "command": command_summary(modified.tool_action), "feedback": modified.tool_observation[-256:]}
        if modified else {"status": "NO_OBSERVED_SUCCESSFUL_WRITE"})
    durations = [step.step_duration_sec for step in history]
    result["tool_time_sec"] = None if any(value is None for value in durations) else sum(durations)
    result["model_time_sec"] = getattr(state, "model_time_sec", 0.0)
    result["task_domain"] = getattr(state, "task_domain", snapshot.get("task_domain"))
    result["agent_state"] = getattr(state, "agent_state", snapshot.get("agent_state") or {"framework": "RECORDED_TRAJECTORY", "role": "NOT_REPORTED", "coordination": "NOT_REPORTED"})
    return result


def build_teacher_context(state, messages, references, char_limit=48000):
    facts = {
        "task_id": state.task_id, "episode_id": state.episode_id,
        "observed_through_step": state.step_index, "phase": state.current_phase,
        "steps_remaining": state.steps_remaining,
        "budget_remaining_usd": state.budget_remaining_usd,
    }
    reference_text = json.dumps([{
        "task_id": ref["task_id"], "reference_kind": ref["reference_kind"],
        "observed_through_step": ref["observed_through_step"],
        "summary_excerpt": ref["summary"][:300] + "\n...\n" + ref["summary"][-300:],
    } for ref in references], ensure_ascii=False)
    headings = ("OBSERVED STATE\n", "CURRENT TASK\n", "FIXED REFERENCE EXCERPTS\n", "OBSERVED TOOLS\n")
    available = max(0, char_limit - sum(map(len, headings)) - len(headings))
    limits = [available // 10, available // 5, len(reference_text)]
    limits.append(min(1600, available - sum(limits)))
    sections = (
        json.dumps(facts, ensure_ascii=False), task_text(state, messages), reference_text,
        recent_tools(state, limits[3]),
    )
    return "\n".join(heading + text[:limit]
                     for heading, text, limit in zip(headings, sections, limits))
