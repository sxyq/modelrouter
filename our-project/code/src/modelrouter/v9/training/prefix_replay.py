"""Rebuild a single AgentState from the saved, pre-decision message prefix."""
from __future__ import annotations

import copy
import json

from modelrouter.serving.schemas import PreDecisionState
from modelrouter.v9.runtime.context import compact_router_state
from .trajectory_material import text_content, tool_result


def build_offline_prefix_input(row, state_factory):
    from modelrouter.agent.state import EpisodeStatus, StepTrace
    from modelrouter.v9.runtime.context import tool_result_phase

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
    state.task_prompt = next((text_content(message) for message in messages
                              if message.get("role") == "user"), "")
    state.replayed_elapsed_sec = pre.get("elapsed_time_sec")
    state.start_monotonic = None
    state.model_time_sec = pre.get("model_time_sec")
    state.router_time_sec = pre.get("router_time_sec")
    state.teacher_time_sec = pre.get("teacher_time_sec")
    generation, commands, thought, tool_cursor = 0, {}, "", 0
    for message in messages:
        if message.get("role") == "assistant":
            generation += 1
            thought = text_content(message)
            commands = {}
            tool_cursor = 0
            for call in message.get("tool_calls") or []:
                function = call.get("function", call)
                arguments = function.get("arguments")
                arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
                commands[call.get("id")] = arguments.get("command") if isinstance(arguments, dict) else None
        elif message.get("role") == "user" and message.get("extra", {}).get("interrupt_type") == "FormatError":
            continue
        elif message.get("role") == "tool" or (message.get("role") == "user" and generation):
            command = (commands.get(message.get("tool_call_id")) if message.get("role") == "tool"
                       else next(iter(commands.values())) if len(commands) == 1 else None)
            if message.get("role") == "tool" and "tool_call_id" not in message:
                if len(commands) == 1:
                    command = next(iter(commands.values()))
                elif provenance.get("tool_result_alignment") == "OPEN_SWE_ORDERED_RESULTS":
                    message["tool_call_id"] = list(commands)[tool_cursor]
                    command = commands[message["tool_call_id"]]
                    tool_cursor += 1
            code, output = tool_result(message)
            if command is None or code is None:
                raise ValueError("Recorded tool command and exit status are required")
            state.current_phase = tool_result_phase(command, code, output)
            state.history.append(StepTrace(
                step_index=generation, phase=state.current_phase, selected_action={}, thought=thought,
                tool_action=command, tool_observation=output, tool_exit_code=code,
                prompt_tokens=None, completion_tokens=None, reasoning_tokens=None, cached_tokens=None,
                step_cost_usd=None, step_duration_sec=None, timestamp=None,
            ))
            state.tool_error_count += int(code != 0)
    return state, messages


def router_input_text(row, decision):
    """Keep captured online states; rebuild only public recorded prefixes."""
    if row.get("_meta", {}).get("input_kind") != "TRAJECTORY_PREFIX":
        return decision.router_text()

    from modelrouter.agent.state import AgentState

    def factory(info):
        return AgentState(info["task_id"], info["episode_id"], "V9_OFFLINE_DATA_REPLAY")

    state, messages = build_offline_prefix_input(
        dict(row, pre_decision_state=decision.model_dump()), factory)
    compact = compact_router_state(state, messages, decision.model_dump())
    compact["tool_time_sec"] = decision.tool_time_sec
    return PreDecisionState.model_validate(compact).router_text()
