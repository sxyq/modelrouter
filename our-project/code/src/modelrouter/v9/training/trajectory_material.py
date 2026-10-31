"""Extract observed public tool feedback and successful reference evidence."""

from __future__ import annotations

import copy
import json
import re

from modelrouter.data_pipeline.sources.tra import extract_swesmith_action
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
