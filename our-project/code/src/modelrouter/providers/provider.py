"""Generator Provider Abstraction for Single Agent Loop.

Supports:
- BaseGeneratorProvider: Abstract contract
- MockGeneratorProvider: Zero-cost realistic ReAct generator for offline stress testing
- OracleGeneratorProvider: Perfect execution for pipeline verification
- OpenAICompatibleProvider: Ready for production API key activation tomorrow morning
"""
from __future__ import annotations

import json
import fcntl
import logging
import os
import random
import re
import secrets
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from modelrouter.v9.runtime.alias import AliasMapping

try:
    from modelrouter.providers.registry import ModelSpec
    from modelrouter.telemetry.multi_model_logger import global_multi_model_logger
except ImportError:
    from experiments.agent_pilot.registry import ModelSpec
    from experiments.agent_pilot.multi_model_logger import global_multi_model_logger

logger = logging.getLogger("modelrouter.providers.provider")


@dataclass
class GeneratorResponse:
    content: str
    thought: str
    action: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    reasoning_tokens: Optional[int]
    cached_tokens: Optional[int]
    latency_ms: float
    cost_usd: Optional[float]
    is_finish: bool
    ttft_ms: Optional[float] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content[:300] if len(self.content) > 300 else self.content,
            "thought": self.thought[:300] if len(self.thought) > 300 else self.thought,
            "action": self.action,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "cached_tokens": self.cached_tokens,
            "latency_ms": round(self.latency_ms, 2),
            "ttft_ms": round(self.ttft_ms, 2) if self.ttft_ms is not None else None,
            "tool_calls": self.tool_calls or [],
            "cost_usd": self.cost_usd,
            "is_finish": self.is_finish,
            **self.metadata,
        }


def parse_react_response(text: str) -> tuple[str, str, bool]:
    """Extracts thought and single bash command from ReAct format."""
    thought = ""
    action = ""
    is_finish = False

    thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", text, re.DOTALL | re.IGNORECASE)
    if thought_match:
        thought = thought_match.group(1).strip()

    action_match = re.search(r"Action:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
    if action_match:
        action = action_match.group(1).strip()
        # Clean multi-line if any
        if "\n" in action:
            action = action.split("\n")[0].strip()

    if not action:
        # Fallback to whole text or simple echo
        action = "pwd"
        thought = text.strip()

    if action.upper() in ("FINISH", "AGENT_DONE", "EXIT", "COMPLETED"):
        is_finish = True

    return thought, action, is_finish


class BaseGeneratorProvider:
    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        raise NotImplementedError


class MockGeneratorProvider(BaseGeneratorProvider):
    """Zero-cost ReAct generator simulating valid agent steps and token statistics."""

    def __init__(self, failure_rate: float = 0.0):
        self.failure_rate = failure_rate

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        t0 = time.time()
        
        # Analyze messages to detect task and step
        user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "")
                break

        # Count history turns to determine step count
        step_count = sum(1 for m in messages if m.get("role") == "assistant")

        # Scenario-specific scripts
        if "fix-git" in user_msg.lower():
            plan = [
                ("Checking git branch and log status.", "git status"),
                ("Switching back to master branch.", "git checkout master"),
                ("Merging detached commit into master branch.", "git merge e5f6g7h"),
                ("Master branch is up to date and verified.", "FINISH"),
            ]
        elif "count-dataset-tokens" in user_msg.lower():
            plan = [
                ("Checking workspace files.", "ls -la"),
                ("Running tokenizer token count on dataset.", "python -m count_tokens dataset.jsonl"),
                ("Token count verified successfully.", "FINISH"),
            ]
        else:
            plan = [
                ("Inspecting current workspace and directory layout.", "pwd && ls -la"),
                ("Running automated tests and environment checks.", "cat Makefile || ls -la"),
                ("Verifying changes and build outputs.", "echo 'build verified'"),
                ("All execution requirements satisfied.", "FINISH"),
            ]

        idx = min(step_count, len(plan) - 1)
        thought, action = plan[idx]
        is_finish = (action == "FINISH")

        content = f"Thought: {thought}\nAction: {action}"

        # Simulate token counts
        prompt_tokens = random.randint(350, 1200) + step_count * 250
        completion_tokens = random.randint(45, 120)
        reasoning_tokens = 0
        if native_effort in ("medium", "high") or model_spec.pool == "Reasoning":
            effort_mult = 2 if native_effort == "high" else 1
            reasoning_tokens = random.randint(200, 600) * effort_mult
            completion_tokens += reasoning_tokens

        cached_tokens = int(prompt_tokens * 0.4) if step_count > 0 else 0

        # Latency simulation: 15-45ms
        latency_ms = (time.time() - t0) * 1000 + random.uniform(12.0, 35.0)

        # In mock mode, actual USD is recorded as 0.0 (or simulated theoretical cost for benchmarking)
        # We record theoretical cost so benchmark can compare policies!
        theoretical_cost = model_spec.calculate_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            cache_read_tokens=cached_tokens,
        )

        return GeneratorResponse(
            content=content,
            thought=thought,
            action=action,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            cached_tokens=cached_tokens,
            latency_ms=latency_ms,
            cost_usd=theoretical_cost,
            is_finish=is_finish,
        )


class OracleGeneratorProvider(BaseGeneratorProvider):
    """Oracle provider that always executes correct actions and succeeds."""

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        t0 = time.time()
        step_count = sum(1 for m in messages if m.get("role") == "assistant")

        if step_count == 0:
            thought = "Oracle inspecting task."
            action = "pwd"
            is_finish = False
        else:
            thought = "Oracle completing task."
            action = "FINISH"
            is_finish = True

        content = f"Thought: {thought}\nAction: {action}"
        return GeneratorResponse(
            content=content,
            thought=thought,
            action=action,
            prompt_tokens=250,
            completion_tokens=40,
            reasoning_tokens=0,
            cached_tokens=0,
            latency_ms=(time.time() - t0) * 1000 + 5.0,
            cost_usd=0.0,
            is_finish=is_finish,
        )


def _pilot_file(name: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "experiments" / "agent_pilot" / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Existing experiments/agent_pilot/{name} not found")


def load_generator_credentials() -> Dict[str, Any]:
    """Read the existing local settings without changing them."""
    cfg: Dict[str, Any] = {
        "primary_model": "gpt-6-luna",
        "fallback_model": "gpt-5.6-luna",
        "allowed_models": ["gpt-6-luna", "gpt-5.6-luna"],
    }
    try:
        cfg.update(json.loads(_pilot_file("configs/generator_credentials.json").read_text()))
    except FileNotFoundError:
        pass
    env_key = os.environ.get("MODELROUTER_GENERATOR_API_KEY") or os.environ.get("OPENAI_API_KEY")
    env_base = os.environ.get("MODELROUTER_GENERATOR_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    if env_key:
        cfg["api_key"] = env_key
    if env_base:
        cfg["base_url"] = env_base
    return cfg


@contextmanager
def _token_budget():
    """Serialize requests and accounting against the existing shared file."""
    with _pilot_file("token_budget.json").open("r+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        data = json.load(handle)
        try:
            yield data
        finally:
            handle.seek(0)
            json.dump(data, handle, indent=2)
            handle.truncate()
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle, fcntl.LOCK_UN)


def _record_budget(data: Dict[str, Any], prompt_tokens: Optional[int], completion_tokens: Optional[int],
                   unknown_token_bound: int = 0) -> None:
    data["total_calls"] = data.get("total_calls", 0) + 1
    if prompt_tokens is None or completion_tokens is None:
        data["unknown_usage_calls"] = data.get("unknown_usage_calls", 0) + 1
        data["reserved_unknown_tokens"] = data.get("reserved_unknown_tokens", 0) + unknown_token_bound
    else:
        data["consumed_prompt_tokens"] = data.get("consumed_prompt_tokens", 0) + prompt_tokens
        data["consumed_completion_tokens"] = data.get("consumed_completion_tokens", 0) + completion_tokens
        data["consumed_total_tokens"] = data.get("consumed_total_tokens", 0) + prompt_tokens + completion_tokens
    data["max_tokens"] = None
    data["remaining_tokens"] = None
    data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def update_token_budget(prompt_tokens: int, completion_tokens: int) -> None:
    with _token_budget() as data:
        _record_budget(data, prompt_tokens, completion_tokens)


class OpenAICompatibleProvider(BaseGeneratorProvider):
    """Single-request Chat Completions transport; tools belong to the agent."""

    protocol = "chat_completions"

    def __init__(
        self, base_url: Optional[str] = None, api_key: Optional[str] = None,
        alias_mapping: Optional[AliasMapping] = None,
    ):
        creds = {} if alias_mapping is not None else load_generator_credentials()
        self.base_url = (base_url or creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        credential_endpoint = (creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key if api_key is not None else (
            creds.get("api_key", "") if self.base_url == credential_endpoint else ""
        )
        self.primary_model = creds.get("primary_model", "gpt-6-luna")
        self.fallback_model = creds.get("fallback_model", "gpt-5.6-luna")
        self.allowed_models = set(creds.get("allowed_models", ["gpt-6-luna", "gpt-5.6-luna"]))
        self.alias_mapping = alias_mapping

    def _normalize_model(self, model_id: str) -> str:
        aliases = {"gpt-6": "gpt-6-luna", "luna": "gpt-6-luna", "gpt-5.6": "gpt-5.6-luna"}
        model = model_id.lower().replace(" ", "-")
        target = aliases.get(model, model)
        if target not in self.allowed_models:
            target = self.primary_model
        if target not in {"gpt-6-luna", "gpt-5.6-luna"}:
            raise ValueError("Only the two authorized Luna endpoints may be requested")
        return target

    def _read_response(self, response, stream: bool, started: float) -> Tuple[Dict[str, Any], Optional[float]]:
        if not stream:
            return json.loads(response.read().decode("utf-8")), None
        body: Dict[str, Any] = {"object": "chat.completion", "choices": []}
        choices: Dict[int, Dict[str, Any]] = {}
        tool_calls: Dict[Tuple[int, int], Dict[str, Any]] = {}
        ttft = None
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            if "error" in chunk:
                raise RuntimeError(f"Provider stream error: {chunk['error'].get('type', 'unknown')}")
            for key in ("id", "model", "created", "system_fingerprint"):
                if key in chunk:
                    body[key] = chunk[key]
            if chunk.get("usage") is not None:
                body["usage"] = chunk["usage"]
            for item in chunk.get("choices") or []:
                index = item["index"]
                choice = choices.setdefault(index, {"index": index, "message": {"role": "assistant", "content": ""}, "finish_reason": None})
                delta = item.get("delta", {})
                if (delta.get("content") or delta.get("tool_calls")) and ttft is None:
                    ttft = (time.perf_counter() - started) * 1000
                for key in ("content", "reasoning_content"):
                    if delta.get(key):
                        choice["message"][key] = choice["message"].get(key, "") + delta[key]
                for tc in delta.get("tool_calls") or []:
                    tool = tool_calls.setdefault((index, tc["index"]), {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                    if tc.get("id"):
                        tool["id"] = tc["id"]
                    for key in ("name", "arguments"):
                        tool["function"][key] += (tc.get("function") or {}).get(key) or ""
                if item.get("finish_reason") is not None:
                    choice["finish_reason"] = item["finish_reason"]
        for index, choice in sorted(choices.items()):
            calls = [tool for (choice_index, _), tool in sorted(tool_calls.items()) if choice_index == index]
            if calls:
                choice["message"]["tool_calls"] = calls
            body["choices"].append(choice)
        return body, ttft

    def _make_payload(self, messages, target_model, native_effort, max_tokens, tools, stream):
        payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "stream": stream}
        if stream:
            payload["stream_options"] = {"include_usage": True}
        if native_effort != "none":
            payload["reasoning_effort"] = native_effort
        if tools:
            payload["tools"] = tools
        return payload

    @staticmethod
    def _usage_counts(usage):
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
        reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
        if prompt is not None and completion is not None and reasoning:
            if usage.get("total_tokens") == prompt + completion + reasoning:
                completion += reasoning
        return (
            prompt, completion, reasoning,
            (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
            (usage.get("prompt_tokens_details") or {}).get("cache_write_tokens"),
        )

    def query_raw(
        self,
        messages: List[Dict[str, Any]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = True,
        *,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return (native_response, metrics); one request, no execution or retry.

        Usage accounting is completed here. Callers must not charge it again.
        Missing usage, returned identity or billing remains explicitly unknown.
        """
        from modelrouter.providers.registry import MODEL_REGISTRY

        alias_facts = self.alias_mapping.resolve(model_spec.model_id, native_effort) if self.alias_mapping is not None else None
        if alias_facts is not None:
            target = alias_facts["actual_backend_model_id"]
            effective_effort = alias_facts["effective_native_effort"]
            target_spec = model_spec
            request_base_url = (self.alias_mapping.base_url or self.base_url).rstrip("/")
            provider_name = "openai-compatible"
        else:
            model_spec.validate_effort(native_effort)
            target = self._normalize_model(model_spec.model_id)
            target_spec = MODEL_REGISTRY[target]
            target_spec.validate_effort(native_effort)
            effective_effort = native_effort
            request_base_url = self.base_url
            provider_name = target_spec.provider
        payload = self._make_payload(messages, target, effective_effort, max_tokens, tools, stream)
        if response_format is not None:
            payload["response_format"] = response_format
        endpoint = "/chat/completions" if self.protocol == "chat_completions" else "/responses"
        request = urllib.request.Request(
            request_base_url + endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}", "User-Agent": "ModelRouter/10"},
            method="POST",
        )
        started = time.perf_counter()
        with _token_budget() as budget:
            input_bound = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            request_bound = input_bound + max_tokens
            try:
                with urllib.request.urlopen(request, timeout=60.0) as response:
                    body, ttft_ms = self._read_response(response, stream, started)
            except Exception:
                _record_budget(budget, None, None, request_bound)
                raise
            raw_usage = body.get("usage")
            p_tokens, c_tokens, r_tokens, cached, cache_written = self._usage_counts(raw_usage or {})
            reported_completion = (raw_usage or {}).get("completion_tokens") if self.protocol == "chat_completions" else (raw_usage or {}).get("output_tokens")
            _record_budget(budget, p_tokens, c_tokens, request_bound)
        latency_ms = (time.perf_counter() - started) * 1000
        returned = body.get("model")
        identity_status = "MATCHED_REQUEST_ALIAS" if returned == target else ("MISSING" if not returned else "MISMATCH")
        usage_complete = p_tokens is not None and c_tokens is not None
        cost = target_spec.calculate_cost(p_tokens, c_tokens, r_tokens or 0, cached or 0, cache_written or 0) if usage_complete and (alias_facts is not None or returned == target) else None
        # Vendor cost is distinct from the configured price estimate.
        reported_cost = (raw_usage or {}).get("cost")
        reported_cost_unit = (raw_usage or {}).get("cost_currency") or (raw_usage or {}).get("currency")
        billed_cost = reported_cost if reported_cost_unit == "USD" else None
        stream_elapsed_ms = latency_ms - ttft_ms if stream and ttft_ms is not None else None
        stream_output_tokens_per_s = (
            c_tokens * 1000 / stream_elapsed_ms
            if usage_complete and stream_elapsed_ms is not None and stream_elapsed_ms > 0 else None
        )
        metrics = {
            "requested_model_id": model_spec.model_id,
            "response_id": body.get("id"),
            "request_model_id": target,
            "returned_model_id": returned,
            "provider": provider_name,
            "protocol": self.protocol,
            "native_effort": effective_effort,
            "stream": stream,
            "requested_max_output_tokens": max_tokens,
            "reported_max_output_tokens": body.get("max_output_tokens"),
            "raw_usage": raw_usage,
            "usage_status": "REPORTED" if usage_complete else "MISSING",
            "identity_status": identity_status,
            "alias_mapping_applied": alias_facts is not None or model_spec.model_id != target,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "reported_completion_tokens": reported_completion,
            "reasoning_tokens": r_tokens,
            "cached_tokens": cached,
            "cache_write_tokens": cache_written,
            "ttft_ms": ttft_ms,
            "latency_ms": latency_ms,
            "output_tokens_per_s": (c_tokens * 1000 / latency_ms) if usage_complete and stream and ttft_ms is not None else None,
            "throughput_definition": "reported_output_including_reasoning / complete_request_seconds",
            "stream_output_tokens_per_s": stream_output_tokens_per_s,
            "stream_output_tokens_per_s_status": "ESTIMATE" if stream_output_tokens_per_s is not None else "UNAVAILABLE",
            "stream_throughput_definition": "reported completion including reasoning / (request latency - TTFT); not token counts from output chunks",
            "cost_usd": cost,
            "cost_model_id": target_spec.model_id,
            "cost_source": target_spec.pricing_source,
            "cost_basis": "SELECTED_MODEL_RATES_WITH_BACKEND_USAGE" if alias_facts is not None else "REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE",
            "cache_cost_policy": "Missing cache counts stay null; corresponding input uses the ordinary input rate",
            "reasoning_cost_policy": "Reasoning is included in completion tokens and charged once",
            "cost_status": "MAPPED_EXPERIMENT_PRICE" if alias_facts is not None and cost is not None else (target_spec.pricing_status if cost is not None else "UNKNOWN"),
            "actual_billed_cost_usd": billed_cost,
            "raw_reported_cost": reported_cost,
            "reported_cost_unit": reported_cost_unit or "NOT_REPORTED",
            "budget_accounted": True,
            "status": "RECORDED" if usage_complete and (alias_facts is not None or returned == target) else "NOT_EVALUATED",
        }
        if alias_facts is not None:
            metrics.update(alias_facts)
            metrics["cost_status"] = "MAPPED_EXPERIMENT_PRICE" if cost is not None else "MAPPED_PRICE_NOT_MEASURED"
        if response_format is not None:
            metrics["requested_response_format"] = response_format
        if usage_complete:
            global_multi_model_logger.log_call(
                protocol=self.protocol, model_id=model_spec.model_id if alias_facts is not None else returned or target, provider=provider_name,
                reasoning_effort=native_effort, stream=stream, ttft_ms=ttft_ms, total_latency_ms=latency_ms,
                prompt_tokens=p_tokens, completion_tokens=c_tokens, reasoning_tokens=r_tokens or 0,
                cache_read_tokens=cached or 0, actual_billed_cost_usd=billed_cost,
                status=metrics["status"], metadata=metrics,
            )
        return body, metrics

    def generate(self, messages, model_spec, native_effort="none", max_tokens=1024, tools=None, stream=False) -> GeneratorResponse:
        body, metrics = self.query_raw(messages, model_spec, native_effort, max_tokens, tools, stream)
        message = body["choices"][0]["message"]
        return self._generation(message.get("content") or "", message.get("tool_calls", []), body, metrics)

    @staticmethod
    def _generation(content, tool_calls, body, metrics):
        thought, action, finished = parse_react_response(content)
        return GeneratorResponse(
            content=content, thought=thought, action=action, is_finish=finished,
            prompt_tokens=metrics["prompt_tokens"], completion_tokens=metrics["completion_tokens"],
            reasoning_tokens=metrics["reasoning_tokens"], cached_tokens=metrics["cached_tokens"],
            latency_ms=metrics["latency_ms"], cost_usd=metrics["cost_usd"],
            ttft_ms=metrics["ttft_ms"], tool_calls=tool_calls, metadata=metrics, raw_response=body,
        )


@contextmanager
def native_generator_relay(record_dir: str | Path, bind: str = "0.0.0.0"):
    """Expose query_raw to native mini for this context's lifetime only.

    Yields port, api_key and a Docker-facing base_url. api_key is a temporary
    in-memory credential: pass it as the native client's API key, never log it.
    Provider credentials and shared usage accounting remain on the host.
    Upstream requests stream for timing; downstream may request JSON or SSE.
    SSE is replayed after the single upstream response, not live forwarded.
    X-Session-ID identifies the episode. Existing events restore steps and cost.
    An explicitly positive cost_limit applies after a completed call;
    this does not predict or cap the bill of an in-flight provider request.
    """
    from modelrouter.benchmark.iterations import event, rows
    from modelrouter.providers.registry import MODEL_REGISTRY

    record_dir = Path(record_dir)
    provider = OpenAICompatibleProvider()
    relay_key = secrets.token_urlsafe(32)
    episode_steps: Dict[str, int] = {}
    episode_costs: Dict[Optional[str], Optional[float]] = {}
    config_path = record_dir / "run_config.json"
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    cost_limit = float(config.get("cost_limit", 0.0))
    for record in rows(record_dir / "events.jsonl"):
        if record.get("source") != "native_generator_relay":
            continue
        episode = record.get("episode_id")
        if episode is not None and record.get("step") is not None:
            episode_steps[episode] = max(episode_steps.get(episode, 0), record["step"] + 1)
        if record["event"] == "GENERATOR_END":
            previous = episode_costs.get(episode, 0.0)
            cost = record.get("cost_usd")
            episode_costs[episode] = previous + cost if previous is not None and cost is not None else None
    step_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def send_json(self, code, body):
            data = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if not secrets.compare_digest(self.headers.get("Authorization", "").encode(),
                                          f"Bearer {relay_key}".encode()):
                self.send_json(401, {"error": {"type": "authentication_error", "message": "Invalid relay credential"}})
                return
            if self.path != "/v1/chat/completions":
                self.send_json(404, {"error": {"type": "not_found", "message": "Use /v1/chat/completions"}})
                return
            request_id = "native-" + secrets.token_hex(12)
            episode_id = self.headers.get("X-Session-ID") or None
            step = None
            if episode_id is not None:
                with step_lock:
                    step = episode_steps.get(episode_id, 0)
                    episode_steps[episode_id] = step + 1
            attribution = {"episode_id": episode_id, "step": step,
                           "policy": "mini-swe-agent", "sample_kind": "benchmark"}
            started = time.perf_counter()
            try:
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                model = payload["model"].removeprefix("openai/")
                if model not in ("gpt-6-luna", "gpt-5.6-luna"):
                    raise ValueError("Only the two Luna models are authorized")
                with step_lock:
                    previous_cost = episode_costs.get(episode_id, 0.0)
                    if cost_limit > 0 and previous_cost is not None and previous_cost >= cost_limit:
                        reason = "EPISODE_COST_LIMIT"
                        event(record_dir, "ERROR", source="native_generator_relay", category="BUDGET",
                              **attribution, request_id=request_id, error=reason,
                              episode_estimated_cost_usd=previous_cost, episode_cost_limit_usd=cost_limit)
                        self.send_json(402, {"error": {"type": reason, "message": "Episode budget cannot fund another request"}})
                        return
                    raw, metrics = provider.query_raw(
                        messages=payload["messages"], model_spec=MODEL_REGISTRY[model],
                        native_effort=payload.get("reasoning_effort", "low"),
                        max_tokens=payload.get("max_completion_tokens", payload.get("max_tokens", 1024)),
                        tools=payload.get("tools"), stream=True,
                    )
                    cost = metrics["cost_usd"]
                    episode_cost = previous_cost + cost if previous_cost is not None and cost is not None else None
                    episode_costs[episode_id] = episode_cost
            except Exception as exc:
                event(record_dir, "ERROR", source="native_generator_relay", category="PROVIDER",
                      **attribution,
                      request_id=request_id, error=type(exc).__name__,
                      duration_ms=(time.perf_counter() - started) * 1000)
                code = 400 if isinstance(exc, (ValueError, KeyError, TypeError)) else 502
                self.send_json(code, {"error": {"type": type(exc).__name__, "message": "Native relay request failed; see host iteration metrics"}})
                return
            event(record_dir, "GENERATOR_END", **metrics, source="native_generator_relay",
                  **attribution,
                  request_id=request_id, native_stream=bool(payload.get("stream", False)),
                  episode_estimated_cost_usd=episode_cost, episode_cost_limit_usd=cost_limit,
                  model=metrics["request_model_id"], returned_model=metrics["returned_model_id"],
                  effort=metrics["native_effort"])
            if not payload.get("stream", False):
                self.send_json(200, raw)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            chunk = {key: raw[key] for key in ("id", "model", "created") if key in raw}
            chunk.update(object="chat.completion.chunk", choices=[])
            for choice in raw["choices"]:
                delta = dict(choice["message"])
                if delta.get("tool_calls"):
                    delta["tool_calls"] = [{"index": index, **call} for index, call in enumerate(delta["tool_calls"])]
                chunk["choices"].append({"index": choice["index"], "delta": delta, "finish_reason": None})
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            chunk["choices"] = [{"index": choice["index"], "delta": {}, "finish_reason": choice.get("finish_reason")} for choice in raw["choices"]]
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            if "usage" in raw:
                chunk.update(choices=[], usage=raw["usage"])
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")

    server = ThreadingHTTPServer((bind, 0), Handler)
    server.daemon_threads = False
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
    thread.start()
    try:
        event(record_dir, "NATIVE_RELAY_START", bind=bind, port=port, cost_limit=cost_limit)
        yield {"port": port, "api_key": relay_key, "base_url": f"http://host.docker.internal:{port}/v1"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
        event(record_dir, "NATIVE_RELAY_STOP", port=port)


GET_TEST_STATUS_TOOL = {
    "type": "function", "name": "get_test_status",
    "description": "Returns local fixture status",
    "parameters": {"type": "object", "properties": {}, "required": []},
}


def execute_safe_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Explicit legacy fixture executor; never invoked by query_raw."""
    if name == "get_test_status":
        return {"status": "ready", "evidence_type": "FIXTURE", "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return {"error": f"Tool '{name}' not found"}


class OpenAIResponsesProvider(OpenAICompatibleProvider):
    """Native Responses transport, sharing identity and usage accounting."""

    protocol = "responses"

    def _make_payload(self, messages, target_model, native_effort, max_tokens, tools, stream):
        payload = {"model": target_model, "input": messages, "max_output_tokens": max_tokens, "stream": stream}
        if native_effort != "none":
            payload["reasoning"] = {"effort": native_effort}
        if tools:
            payload["tools"] = tools
        return payload

    def _usage_counts(self, usage):
        return (
            usage.get("input_tokens"), usage.get("output_tokens"),
            (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
            (usage.get("input_tokens_details") or {}).get("cached_tokens"),
            (usage.get("input_tokens_details") or {}).get("cache_write_tokens"),
        )

    def _read_response(self, response, stream, started):
        if not stream:
            return json.loads(response.read().decode("utf-8")), None
        body: Dict[str, Any] = {}
        output = {}
        text = ""
        ttft = None
        event = ""
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if line.startswith("event:"):
                event = line[6:].strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
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
                body = item.get("response", {})
            if kind in ("error", "response.failed"):
                raise RuntimeError(f"Provider stream ended with {kind}")
        if "output" not in body:
            body["output"] = list(output.values())
            if text:
                body["output"].append({"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": text}]})
        return body, ttft

    def generate(self, messages, model_spec, native_effort="none", max_tokens=1024, stream=True, tools=None, tool_executor=None):
        body, metrics = self.query_raw(messages, model_spec, native_effort, max_tokens, tools, stream)
        outputs = body.get("output", [])
        text = "".join(part.get("text", "") for item in outputs if item["type"] == "message" for part in item.get("content", []))
        calls = [item for item in outputs if item["type"] == "function_call"]
        if calls and tool_executor is not None:
            executed = []
            followup = list(messages) + outputs
            for call in calls:
                args = json.loads(call.get("arguments") or "{}")
                value = tool_executor(call["name"], args)
                executed.append({"call_id": call["call_id"], "name": call["name"], "args": args, "output": value})
                followup.append({"type": "function_call_output", "call_id": call["call_id"], "output": json.dumps(value)})
            body2, metrics2 = self.query_raw(followup, model_spec, native_effort, max_tokens, tools, stream)
            text += "".join(part.get("text", "") for item in body2.get("output", []) if item["type"] == "message" for part in item.get("content", []))
            combined = dict(metrics)
            for key in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens", "cost_usd", "actual_billed_cost_usd", "latency_ms"):
                combined[key] = metrics[key] + metrics2[key] if metrics[key] is not None and metrics2[key] is not None else None
            combined["requests"] = [metrics, metrics2]
            combined["raw_usage"] = [metrics["raw_usage"], metrics2["raw_usage"]]
            combined["status"] = "RECORDED" if all(m["status"] == "RECORDED" for m in (metrics, metrics2)) else "NOT_EVALUATED"
            combined["output_tokens_per_s"] = None
            combined["stream_output_tokens_per_s"] = None
            combined["stream_output_tokens_per_s_status"] = "PER_REQUEST_ONLY"
            return self._generation(text, executed, {"responses": [body, body2]}, combined)
        return self._generation(text, calls, body, metrics)


OpenAIChatCompletionsProvider = OpenAICompatibleProvider


class AnthropicMessagesProvider(BaseGeneratorProvider):
    """Provider for Anthropic /v1/messages protocol.
    
    Reports BLOCKED_PROTOCOL when upstream endpoint forbids dispatch.
    """

    PROTOCOL_STATUS = "BLOCKED_PROTOCOL"
    BLOCKED_REASON = "This group does not allow /v1/messages dispatch (HTTP 403 permission_error)"

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        creds = load_generator_credentials()
        self.base_url = (base_url or os.environ.get("ANTHROPIC_BASE_URL") or creds.get("base_url") or "https://api.anthropic.com/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or creds.get("api_key", "")
        self.primary_model = creds.get("primary_model", "gpt-6-luna")
        self.status = "BLOCKED_PROTOCOL"
        self.status_details: Dict[str, Any] = {}

    def probe(self) -> Dict[str, Any]:
        """Probes the /v1/messages endpoint and records protocol status."""
        url = f"{self.base_url}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ModelRouter/1.0",
        }
        payload = {
            "model": self.primary_model,
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "ping"}],
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                self.status = "SUPPORTED"
                self.status_details = {"status": "SUPPORTED", "code": resp.status}
                return self.status_details
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                parsed_err = json.loads(err_body)
                err_msg = parsed_err.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = err_body

            self.status = "BLOCKED_PROTOCOL"
            self.status_details = {
                "status": "BLOCKED_PROTOCOL",
                "http_code": e.code,
                "reason": err_msg,
                "error_type": "permission_error" if "permission_error" in err_body else "http_error",
                "endpoint": url,
            }
            logger.warning("AnthropicMessagesProvider protocol probe blocked: %s", self.status_details)
            return self.status_details
        except Exception as e:
            self.status = "BLOCKED_PROTOCOL"
            self.status_details = {
                "status": "BLOCKED_PROTOCOL",
                "http_code": 0,
                "reason": str(e),
                "endpoint": url,
            }
            return self.status_details

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        probe_res = self.probe()
        if self.status == "BLOCKED_PROTOCOL":
            raise PermissionError(
                f"Protocol BLOCKED_PROTOCOL: /v1/messages is not supported or permitted on endpoint {self.base_url}. "
                f"Details: {probe_res.get('reason', self.BLOCKED_REASON)}"
            )
        raise NotImplementedError("Anthropic message generation not implemented for blocked protocol.")
