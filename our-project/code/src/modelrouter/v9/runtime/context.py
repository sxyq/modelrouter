"""Character-bounded views of observed Agent state; never alter its messages."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping

from modelrouter.agent.state import StepTrace


TEST_COMMAND = re.compile(r"\b(?:pytest|unittest|ctest)\b|\b(?:npm|pnpm|yarn|cargo|go|mvn)\s+test\b")
_EXTENSIONS = ("teacher_assessment", "capability_cards", "capability_snapshot_id",
               "feature_training_status", "agent_context", "continuity")
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


def _pricing_values(value):
    if isinstance(value, Mapping):
        metadata = {"source", "source_url", "source_urls", "url", "urls", "fetched_at_utc",
                    "error", "error_details", "conditions"}
        result = {name: _pricing_values(item) for name, item in value.items() if name not in metadata}
        if result.get("regions"):
            rate_sets, regions = [], []
            for region in result.pop("regions"):
                rates = [[row.get(name) for name in ("billing_item", "price", "unit")]
                         for row in region["rates"]]
                if rates not in rate_sets:
                    rate_sets.append(rates)
                regions.append([region["region"], region.get("deployment_scope"),
                                region["currency"], rate_sets.index(rates)])
            result.update(rate_fields=["billing_item", "price", "unit"], rate_sets=rate_sets,
                          region_fields=["region", "deployment_scope", "currency", "rate_set_ref"],
                          regions=regions)
        return result
    if isinstance(value, list):
        return [_pricing_values(item) for item in value]
    return value


def _router_card(card, snapshot_id):
    result = {name: card.get(name) for name in ("model_id", "native_effort", "action_id", "revision")}
    for name in ("model_revision", "model_evidence_status", "evidence_status", "metric", "unit", "missing"):
        if name in card:
            result[name] = card[name]
    if card.get("snapshot_id") != snapshot_id:
        result["snapshot_id"] = card.get("snapshot_id")
    model_rows, model_missing = _metric_rows(card.get("model_metrics", []))
    effort_rows, effort_missing = _metric_rows(card.get("action_metrics", []))
    if model_rows:
        result["model_metrics"] = model_rows
    if effort_rows:
        result["action_metrics"] = effort_rows
    reference_rows, _ = _metric_rows(card.get("reference_metrics", []))
    if reference_rows:
        result["reference_metrics"] = reference_rows
    shared = [name for name in model_missing if name in effort_missing]
    missing = {"model_and_effort": shared,
               "model": [name for name in model_missing if name not in shared],
               "effort": [name for name in effort_missing if name not in shared]}
    if any(missing.values()):
        result["NOT_MEASURED"] = {scope: names for scope, names in missing.items() if names}
    if "model_pricing" in card:
        result["model_pricing"] = _pricing_values(card["model_pricing"])
    for name in ("model_provider", "model_context_limits"):
        if card.get(name):
            result[name] = card[name]
    return result


def format_router_payload(payload: Mapping) -> str:
    """One view; shared card values apply to all cards, table refs are zero-based."""
    data = dict(payload)
    for name in _EXTENSIONS:
        if data.get(name) is None or data.get(name) == []:
            data.pop(name, None)
    if not any(name in data for name in _EXTENSIONS):
        return json.dumps(data, sort_keys=True, ensure_ascii=False)
    prompt = data.pop("prompt", None)
    if isinstance(prompt, str):
        prompt = task_text(None, [{"role": "user", "content": prompt}], router_view=True)
    result = {"prompt": prompt}
    teacher = data.pop("teacher_assessment", None)
    result["teacher_assessment"] = ({name: teacher.get(name) for name in
        ("progress_summary", "main_blocker", "next_milestone")} if teacher is not None else None)
    continuity = data.pop("continuity", None)
    if continuity is not None:
        values = {name: continuity[name] for name in (
            "observed_cached_tokens", "cache_usage_status", "physical_kv_cache_shared",
            "actual_backend_model_id", "selected_model_id", "router_checkpoint_id",
            "backend_deployment_status", "identity_status", "logical_model_changed",
            "actual_backend_changed", "router_fallback_used", "context_delivery",
            "history_messages_resent", "previous_selected_model_id", "previous_actual_backend_model_id",
            "previous_router_checkpoint_id", "switch_extra_tokens", "switch_extra_cost_usd",
            "switch_cost_status") if name in continuity}
        same = []
        for previous, current in (("previous_selected_model_id", "selected_model_id"),
                                  ("previous_actual_backend_model_id", "actual_backend_model_id"),
                                  ("previous_router_checkpoint_id", "router_checkpoint_id")):
            if previous in values and values.get(current) is not None and values[previous] == values[current]:
                values.pop(previous)
                same.append(current)
        if same:
            values["previous_equals_current"] = same
        result["continuity"] = values
    for name in ("phase", "budget_remaining_usd", "steps_remaining", "step_index",
                 "last_tool_exit_code", "context_chars", "context_tokens_approx",
                 "backend_deployment_status"):
        if name in data:
            result[name] = data.pop(name)
    snapshot_id = data.pop("capability_snapshot_id", None)
    result["capability_snapshot_id"] = snapshot_id
    history = {name: data.pop(name) for name in ("last_observation_summary", "history_snippet") if name in data}
    result.update({name: value and value[-128:] for name, value in history.items()
                   if name == "last_observation_summary"})
    cards = [_router_card(card, snapshot_id) for card in data.pop("capability_cards", [])]
    # Keep all candidate identities ahead of verbose metric/pricing metadata.
    # The full evidence stays in this same view and the frozen snapshot.
    priority_fields = ("model_id", "native_effort", "action_id", "model_provider",
                       "model_evidence_status", "evidence_status")
    result["capability_summary"] = [{name: card[name] for name in priority_fields if name in card}
                                    for card in cards]
    for summary, card in zip(result["capability_summary"], cards):
        intelligence = [row for row in card.get("reference_metrics", [])
                        if row[0] == "artificial_analysis_intelligence_index"]
        if intelligence:
            row = intelligence[0]
            summary["aa_intelligence_reference"] = {
                "score_raw": row[1], "score_unit": row[2],
                "benchmark_version": row[3], "evaluated_native_effort": row[5]}
    missing_names, missing_sets = [], []
    for card in cards:
        missing = card.pop("NOT_MEASURED", None)
        if missing:
            scopes = {}
            for scope, names in missing.items():
                indexes = []
                for name in names:
                    if name not in missing_names:
                        missing_names.append(name)
                    indexes.append(missing_names.index(name))
                scopes[scope] = indexes
            if scopes not in missing_sets:
                missing_sets.append(scopes)
            card["not_measured_ref"] = missing_sets.index(scopes)
    if missing_sets:
        result["NOT_MEASURED"] = {"metric_names": missing_names, "scope_index_sets": missing_sets}
    shared = {}
    if len(cards) > 1:
        for name in ("model_revision", "model_evidence_status", "evidence_status", "model_pricing",
                     "model_context_limits"):
            if name in cards[0] and all(name in card and card[name] == cards[0][name] for card in cards):
                shared[name] = cards[0][name]
                for card in cards:
                    card.pop(name)
    if shared:
        result["capability_shared"] = shared
    if any(card.get("model_metrics") or card.get("action_metrics") or card.get("reference_metrics") for card in cards):
        result["metric_fields"] = list(_METRIC_FIELDS)
    result["capability_cards"] = cards
    for name in ("history_length", "prior_tool_calls_count", "prior_error_signals_count",
                 "feature_training_status", "task_id"):
        if name in data:
            result[name] = data.pop(name)
    agent_context = data.pop("agent_context", None)
    if agent_context is not None:
        result["agent_context"] = {name: agent_context[name] for name in
            ("message_count", "context_chars", "completed_generations", "observed_through_step",
             "token_measurement_status") if name in agent_context}
    result.update(data)
    result.update({name: value for name, value in history.items() if name == "history_snippet"})
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))


def record_tool_result(state, record_dir, action, output, duration_ms, *, submission=False):
    """Keep the upstream result and attach it to its generating decision."""
    from modelrouter.benchmark.iterations import append, event, now

    command = action["command"]
    if TEST_COMMAND.search(command):
        state.current_phase = "verify"
    elif output["returncode"]:
        state.current_phase = "recover"
    elif state.step_index > 1:
        state.current_phase = "modify"
    state.last_output = output
    state.tool_error_count += int(output["returncode"] != 0)
    state.history.append(StepTrace(
        step_index=state.step_index, phase=state.current_phase,
        selected_action=dict(getattr(state, "last_selected_action", {})), thought="",
        tool_action=command, tool_observation=output["output"],
        tool_exit_code=output["returncode"], prompt_tokens=0, completion_tokens=0,
        reasoning_tokens=0, cached_tokens=0, step_cost_usd=0,
        step_duration_sec=duration_ms / 1000,
    ))
    record = {
        "kind": "agent_tool", "timestamp": now(), "episode_id": state.episode_id,
        "step": state.step_index, "decision_id": getattr(state, "last_decision_id", None),
        "router_checkpoint_id": getattr(state, "last_router_checkpoint_id", None),
        "command": command, "tool_call_id": action.get("tool_call_id"),
        "exit_code": output["returncode"], "duration_ms": duration_ms,
        "output": output["output"], "exception_info": output.get("exception_info", ""),
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


def recent_tools(state, char_limit):
    parts, remaining = [], char_limit
    for step in reversed(visible_history(state)):
        heading = (f"step={step.step_index} phase={step.phase} exit={step.tool_exit_code}\n"
                   f"command={step.tool_action[:256]}\noutput=")
        room = max(0, remaining - len(heading) - 1)
        output = step.tool_observation[-room:] if room else ""
        part = (heading + output)[:remaining]
        parts.append(part)
        remaining -= len(part) + 1
        if remaining <= 0:
            break
    return "\n".join(reversed(parts))


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
    result = dict(snapshot, prompt=task, history_snippet=tools,
                  context_chars=message_chars(messages), context_tokens_approx=None,
                  history_length=len(history), prior_tool_calls_count=len(history),
                  prior_error_signals_count=state.tool_error_count,
                  last_tool_exit_code=0, last_observation_summary="Initial task prompt")
    if history:
        result.update(last_tool_exit_code=history[-1].tool_exit_code,
                      last_observation_summary=history[-1].tool_observation[-512:])
    result["agent_context"] = {
        "message_count": len(messages), "context_chars": result["context_chars"],
        "router_task_tool_char_limit": char_limit,
        "router_task_chars": len(task), "router_tool_chars": len(tools),
        "observed_through_step": state.step_index,
        "token_measurement_status": "NOT_MEASURED",
    }
    return result


def build_teacher_context(state, messages, references, char_limit=48000):
    facts = {
        "task_id": state.task_id, "episode_id": state.episode_id,
        "observed_through_step": state.step_index, "phase": state.current_phase,
        "steps_remaining": state.steps_remaining,
        "budget_remaining_usd": state.budget_remaining_usd,
    }
    reference_fields = ("source_id", "dataset_revision", "task_id", "episode_id", "split",
                        "success_evidence", "summary", "observed_through_step")
    reference_text = json.dumps([{name: ref[name] for name in reference_fields}
                                 for ref in references], ensure_ascii=False)
    headings = ("OBSERVED STATE\n", "CURRENT TASK\n", "FIXED REFERENCES\n",
                "OBSERVED TOOLS\n", "RECENT MESSAGES\n")
    available = max(0, char_limit - sum(map(len, headings)) - len(headings))
    limits = [available // 10, available // 5, available // 4, available // 5]
    limits.append(available - sum(limits))
    sections = (
        json.dumps(facts, ensure_ascii=False), task_text(state, messages), reference_text,
        recent_tools(state, limits[3]), recent_messages(observed_messages(state, messages), limits[4]),
    )
    return "\n".join(heading + text[:limit]
                     for heading, text, limit in zip(headings, sections, limits))
