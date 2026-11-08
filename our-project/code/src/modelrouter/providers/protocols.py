"""Wire serialization, stream parsing and Usage decoding per API protocol."""
from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Tuple


class ChatCompletions:
    @staticmethod
    def payload(messages, model, effort, max_tokens, tools, stream):
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": stream}
        if stream:
            payload["stream_options"] = {"include_usage": True}
        if effort != "none" or model == "gpt-6-luna":
            payload["reasoning_effort"] = effort
        if model == "glm-5.3-flash":
            payload["thinking"] = {"type": "enabled"}
        if tools:
            payload["tools"] = tools
        return payload

    @staticmethod
    def read(response, stream, started, capture, secret, record_bytes):
        if not stream:
            raw = response.read()
            record_bytes(raw, capture, secret)
            return json.loads(raw.decode("utf-8")), None
        body: Dict[str, Any] = {"object": "chat.completion", "choices": []}
        choices, tool_calls = {}, {}
        ttft = None
        done_received = False
        for raw_line in response:
            record_bytes(raw_line, capture, secret)
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                done_received = True
                break
            chunk = json.loads(data)
            if "error" in chunk:
                body["error"] = chunk["error"]
                break
            for key in ("id", "model", "created", "system_fingerprint", "reasoning", "reasoning_effort"):
                if key in chunk:
                    body[key] = chunk[key]
            if chunk.get("usage") is not None:
                body["usage"] = chunk["usage"]
            for item in chunk.get("choices") or []:
                index = item["index"]
                choice = choices.setdefault(index, {"index": index, "message": {"role": "assistant", "content": ""},
                                                     "finish_reason": None})
                delta = item.get("delta", {})
                if (delta.get("content") or delta.get("tool_calls")) and ttft is None:
                    ttft = (time.perf_counter() - started) * 1000
                for key in ("content", "reasoning_content"):
                    if delta.get(key):
                        choice["message"][key] = choice["message"].get(key, "") + delta[key]
                for call in delta.get("tool_calls") or []:
                    tool = tool_calls.setdefault((index, call["index"]),
                        {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                    if call.get("id"):
                        tool["id"] = call["id"]
                    for key in ("name", "arguments"):
                        tool["function"][key] += (call.get("function") or {}).get(key) or ""
                if item.get("finish_reason") is not None:
                    choice["finish_reason"] = item["finish_reason"]
        for index, choice in sorted(choices.items()):
            calls = [call for (choice_index, _), call in sorted(tool_calls.items()) if choice_index == index]
            if calls:
                choice["message"]["tool_calls"] = calls
            body["choices"].append(choice)
        body["_stream_end"] = {"done_received": done_received}
        return body, ttft

    @staticmethod
    def usage(usage):
        prompt, completion = usage.get("prompt_tokens"), usage.get("completion_tokens")
        reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
        if prompt is not None and completion is not None and reasoning:
            if usage.get("total_tokens") == prompt + completion + reasoning:
                completion += reasoning
        return (prompt, completion, reasoning,
                (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
                (usage.get("prompt_tokens_details") or {}).get("cache_write_tokens"))


class Responses:
    @staticmethod
    def payload(messages, model, effort, max_tokens, tools, stream):
        inputs = []
        for message in messages:
            if message.get("role") == "tool":
                inputs.append({"type": "function_call_output", "call_id": message["tool_call_id"],
                               "output": message["content"]})
            elif message.get("tool_calls"):
                if message.get("content"):
                    inputs.append({"role": message["role"], "content": message["content"]})
                inputs.extend({"type": "function_call", "call_id": call["id"], **call["function"]}
                              for call in message["tool_calls"])
            else:
                inputs.append({"role": message["role"], "content": message["content"]})
        payload = {"model": model, "input": inputs, "max_output_tokens": max_tokens, "stream": stream}
        if effort != "none" or model in ("gpt-6-luna", "gpt-6.1-terra"):
            payload["reasoning"] = {"effort": effort}
        if tools:
            payload["tools"] = [{"type": tool["type"], **tool["function"]} if "function" in tool else tool
                                for tool in tools]
        return payload

    @staticmethod
    def read(response, stream, started, capture, secret, record_bytes):
        if not stream:
            raw = response.read()
            record_bytes(raw, capture, secret)
            return json.loads(raw.decode("utf-8")), None
        body, output, text = {}, {}, ""
        ttft, event, terminal_event = None, "", None
        done_received = False
        for raw_line in response:
            record_bytes(raw_line, capture, secret)
            line = raw_line.decode("utf-8").strip()
            if line.startswith("event:"):
                event = line[6:].strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                done_received = True
                break
            item = json.loads(data)
            kind = item.get("type", event)
            if kind in ("response.output_text.delta", "response.function_call_arguments.delta"):
                if item.get("delta") and ttft is None:
                    ttft = (time.perf_counter() - started) * 1000
                if kind == "response.output_text.delta":
                    text += item.get("delta", "")
            if kind in ("response.output_item.added", "response.output_item.done"):
                value = item["item"]
                output[value.get("id") or value.get("call_id") or str(item.get("output_index", 0))] = value
            if kind in ("response.completed", "response.done", "response.incomplete"):
                body, terminal_event = item.get("response", {}), kind
            if kind in ("error", "response.failed"):
                body, terminal_event = item.get("response", body), kind
                error = body.get("error") or item
                body["error"] = {**error, "type": error.get("code") or error.get("type", kind)}
                break
        if "output" not in body:
            body["output"] = list(output.values())
            if text:
                body["output"].append({"type": "message", "role": "assistant",
                                      "content": [{"type": "output_text", "text": text}]})
        body["_stream_end"] = {"done_received": done_received, "terminal_event": terminal_event}
        return body, ttft

    @staticmethod
    def usage(usage):
        return (usage.get("input_tokens"), usage.get("output_tokens"),
                (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
                (usage.get("input_tokens_details") or {}).get("cached_tokens"),
                (usage.get("input_tokens_details") or {}).get("cache_write_tokens"))


def response_error(body, protocol):
    if body.get("error") is not None:
        return body["error"].get("type", "unknown")
    if protocol == "responses":
        outputs = body.get("output", [])
        calls = [item for item in outputs if item["type"] == "function_call"]
        if any(call.get("status") == "incomplete" for call in calls):
            return "INCOMPLETE_TOOL_CALL"
        if body.get("status") != "completed":
            return "INCOMPLETE_RESPONSE"
        content = any(part.get("text") for item in outputs if item["type"] == "message"
                      for part in item.get("content", []))
    else:
        choices = body.get("choices", [])
        if not choices:
            return "EMPTY_RESPONSE"
        message = choices[0].get("message") or {}
        content = message.get("content")
        calls = [call.get("function", {}) for call in message.get("tool_calls") or []]
        if choices[0].get("finish_reason") == "length":
            return "INCOMPLETE_RESPONSE"
        if choices[0].get("finish_reason") is None:
            return "INCOMPLETE_RESPONSE" if content or calls else "EMPTY_RESPONSE"
    if not content and not calls:
        return "EMPTY_RESPONSE"
    for call in calls:
        if not call.get("name") or not call.get("arguments"):
            return "INCOMPLETE_TOOL_CALL"

        def unique_arguments(pairs):
            arguments = dict(pairs)
            if len(arguments) != len(pairs):
                raise ValueError("DUPLICATE_TOOL_ARGUMENT")
            return arguments

        try:
            json.loads(call["arguments"], object_pairs_hook=unique_arguments)
        except json.JSONDecodeError:
            return "INVALID_TOOL_ARGUMENTS"
        except ValueError as exc:
            return str(exc)
    return None
