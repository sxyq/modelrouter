"""Extract observed public tool feedback and successful reference evidence."""

from __future__ import annotations

import copy
import json
import re

from modelrouter.data_pipeline.sources.tra import extract_swesmith_action
from modelrouter.data_pipeline.batch_prep import _example
from modelrouter.datasets.public_sources import PublicDatasetLoader


def text_content(message):
    value = message.get("content")
    if isinstance(value, list):
        return "\n".join(item.get("text", "") for item in value if isinstance(item, dict))
    return value if isinstance(value, str) else "" if value is None else json.dumps(value, ensure_ascii=False)


def tool_result(message):
    """A code listing containing error words is not a failed command."""
    content = text_content(message)
    value = message.get("content")
    if isinstance(value, str) and value.lstrip().startswith("{"):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
    if isinstance(value, dict):
        code = value.get("returncode", value.get("exit_code"))
        if isinstance(code, str) and re.fullmatch(r"-?\d+", code):
            code = int(code)
        output = (value["output"] if "output" in value else
                  "\n".join(value[name] for name in ("output_head", "output_tail") if name in value))
        return code if type(code) is int else None, str(output)
    match = re.search(r"(?im)^(?:returncode|exit_code|exit code)\s*[:=]\s*(-?\d+)\s*$", content)
    return (int(match.group(1)) if match else None), content


def action_excerpt(message):
    """Quote observed tool arguments, avoiding an invented teacher explanation."""
    calls = message.get("tool_calls") or []
    if calls:
        arguments = []
        for call in calls:
            function = call.get("function", call)
            value = function.get("arguments")
            arguments.append(str(function.get("name", "")) + " " +
                             (value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)))
        return " | ".join(arguments)[:500]
    _, _, has_action = extract_swesmith_action(message, "tool")
    if not has_action:
        return None
    content = text_content(message)
    command = re.search(r"```(?:bash|sh)?\s*\n(.*?)```", content, re.S)
    return (command.group(1).strip() if command else content)[:500]


def link_task_trajectory(task, trajectory_row):
    """Match exact identities and retain unavailable trajectory-version evidence."""
    task_id_matches = task["instance_id"] == trajectory_row["instance_id"]
    trace_repo = trajectory_row.get("repo")
    trace_commit = trajectory_row.get("base_commit")
    identities_match = task_id_matches and (trace_repo is None or trace_repo == task["repo"])
    reference = trajectory_row.get("metadata", {}).get("reference_patch", {}).get("patch")
    return {
        "instance_id_matches": task_id_matches,
        "repo_matches": task["repo"] == trace_repo if trace_repo else None,
        "base_commit_matches": task["base_commit"] == trace_commit if trace_commit else None,
        "task_base_commit": task["base_commit"],
        "trajectory_base_commit": trace_commit,
        "reference_patch_matches": task["patch"] == reference if reference is not None else None,
        "identity_status": ("EXACT_ID_VERSION_UNREPORTED" if identities_match and trace_commit is None else
                            "EXACT_ID_VERSION_MATCHED" if identities_match and trace_commit == task["base_commit"] else
                            "IDENTITY_OR_VERSION_MISMATCH"),
    }




def reference_candidate(episode):
    if episode["resolved"] is not True:
        return None
    steps, observations, actions = 0, [], []
    prompt = None
    for message in episode["messages"]:
        if message.get("role") == "assistant":
            steps += 1
            excerpt = action_excerpt(message)
            if excerpt:
                actions.append((steps, excerpt))
        elif message.get("role") == "user" and prompt is None:
            prompt = text_content(message)
        elif message.get("role") == "tool" or (message.get("role") == "user" and steps):
            code, text = tool_result(message)
            observations.append((steps, code, text[:800]))
    if not observations or steps < 2:
        return None
    failures = [entry for entry in observations if entry[1] is not None and entry[1] != 0]
    unknowns = [entry for entry in observations if entry[1] is None]
    if not failures and unknowns:
        return None
    kind = "failure_recovery" if failures else "efficient_success"
    validation_steps = {step for step, action in actions
                        if re.search(r"\b(?:pytest|unittest)\b|\bpython\S*\b.*test", action)}
    verification = next((entry for entry in reversed(observations)
                         if entry[0] in validation_steps and entry[1] == 0 and entry[2]), None)
    recovery = (verification if failures and verification and verification[0] > failures[-1][0] else
                next((entry for entry in observations
                      if failures and entry[0] > failures[-1][0] and entry[1] == 0), None))
    if failures and recovery is None:
        return None
    meta = PublicDatasetLoader().get_source_metadata(episode["source_id"])
    evidence = {"field": "resolved", "value": True, "source_path": episode["source_path"],
                "source_row": episode["source_row"], "label_nature": "PUBLIC_DATASET_RESOLVED_FIELD",
                "train_anchor": episode["anchor"].get("stable_record_id")}
    goal = re.search(r"<pr_description>(.*?)</pr_description>", prompt or "", re.S)
    summary = "任务原文摘录：" + (goal.group(1).strip() if goal else prompt or "")[:300]
    summary += f"；已观测 {steps} 次生成、{len(observations)} 条工具反馈。"
    verification_action = next((text for step, text in actions if verification and step == verification[0]), None)
    excerpts = actions[:1] + (actions[len(actions) // 2:len(actions) // 2 + 1] if len(actions) > 2 else [])
    excerpts += [(verification[0], verification_action)] if verification_action else actions[-1:]
    summary += "过程原文摘录：" + " → ".join(text for _, text in excerpts)
    if verification and not failures:
        summary += "；验证工具返回原文（退出码0）：" + verification[2]
    if failures:
        summary += "；末次失败工具返回原文：" + failures[-1][2]
        summary += "；末次失败后的工具返回原文（退出码0）：" + recovery[2]
    summary += "；公开数据 resolved=1，成功依据独立于工具退出码。"
    return {"reference_kind": kind, "source_id": episode["source_id"],
            "dataset_revision": episode["dataset_revision"], "task_id": episode["task_id"],
            "episode_id": episode["episode_id"], "split": "train", "success_evidence": evidence,
            "summary": summary, "observed_through_step": steps, "source_url": meta.official_origin,
            "license": meta.license, "summary_method": "EXTRACTIVE_OBSERVED_MESSAGES",
            "selection_scope": "TYPED_TRAIN_MATCHES_WITHIN_INPUT_SCAN",
            "tool_failure_evidence": failures, "recovery_evidence": recovery,
            "verification_evidence": verification, "verification_action": verification_action,
            "selection_metric": {"assistant_steps": steps, "tool_results": len(observations),
            "failed_tool_results": len(failures), "unknown_tool_results": len(unknowns)}}


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


def trajectory_prefixes(episode, cutoffs=(1, 4, 8)):
    """Emit pre-action histories; final episode outcomes remain targets only."""
    history, prompt, step, calls, errors = [], None, 0, 0, 0
    last_code = last_result = None
    for index, message in enumerate(episode["messages"]):
        role = message.get("role")
        if role == "user" and prompt is None:
            prompt = text_content(message)
        if role == "assistant":
            step += 1
            action, nature, has_action = extract_swesmith_action(message, "tool")
            if step in cutoffs and has_action:
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
                       "primary_supervision_class": "S2", "split": episode["split"],
                       "label_evidence": {"observed_action": [f"messages[{index}]"]}}
                sample = _example(episode["source_id"], {"pre_decision_state": pre,
                                  "observed_decision": {"action_type": action}}, ref, "observed_action")
                sample["provenance"].update(task_id=episode["task_id"], episode_id=episode["episode_id"],
                    dataset_revision=episode["dataset_revision"], observed_through_step=step - 1,
                    message_cutoff_exclusive=index)
                sample["provenance"].update({name: episode["anchor"][name] for name in (
                    "assigned_layer", "quality_grade", "train_eligible", "source_policy_train_allowed",
                    "train_anchor_file", "qualification_source_path") if name in episode["anchor"]})
                sample["provenance"]["train_anchor_stable_id"] = episode["anchor"].get("stable_record_id")
                sample["_meta"].update(action_nature=nature, observed_outcome=episode["resolved"],
                                      input_kind="TRAJECTORY_PREFIX")
                sample["observed_messages"] = copy.deepcopy(episode["messages"][:index])
                yield sample
        elif role == "tool" or (role == "user" and step > 0):
            calls += 1
            last_code, last_result = tool_result(message)
            errors += int(last_code is not None and last_code != 0)
            last_result = last_result[:2000]
        history.append({name: message[name] for name in ("role", "content", "tool_calls", "tool_call_id")
                        if name in message})
