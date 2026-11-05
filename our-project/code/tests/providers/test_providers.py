#!/usr/bin/env python3
"""
test_providers.py - Unit & Integration Tests for ModelRouter Providers.

Tests:
1. Base & MockGeneratorProvider generation, token counting, and cost calculation.
2. OracleGeneratorProvider deterministic finish sequence.
3. OpenAICompatibleProvider model normalization and fallback logic.
4. OpenAIResponsesProvider SSE event streaming, reasoning effort, and safe tool roundtrip.
5. Token budget tracker updates and ceiling safety.
"""

import json
import os
import sys
import threading
import time
import unittest
import io
import socket
import urllib.request
import urllib.error
import pytest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SRC_DIR = PROJECT_ROOT / "our-project" / "code" / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from modelrouter.providers.provider import (
    BaseGeneratorProvider,
    MockGeneratorProvider,
    OracleGeneratorProvider,
    OpenAICompatibleProvider,
    OpenAIResponsesProvider,
    execute_safe_tool,
    GET_TEST_STATUS_TOOL,
    parse_react_response,
    update_token_budget,
    native_generator_relay,
)
from modelrouter.providers.registry import ModelRegistry, ModelSpec, V9_MODEL_IDS
from modelrouter.providers.registry import MODEL_REGISTRY
from modelrouter.providers import provider as provider_module
from modelrouter.v9.runtime.alias import AliasMapping


@pytest.fixture(autouse=True)
def isolated_accounting(tmp_path, monkeypatch):
    budget = tmp_path / "token_budget.json"
    budget.write_text(json.dumps({"max_tokens": 1000000, "consumed_total_tokens": 0}))
    monkeypatch.setattr(provider_module, "_pilot_file", lambda name: budget)
    monkeypatch.setattr(provider_module, "load_generator_credentials", lambda: {})
    monkeypatch.setattr(provider_module.global_multi_model_logger, "log_call", lambda **kwargs: kwargs)
    return budget


def test_alias_credentials_stay_with_the_configured_endpoint(monkeypatch):
    monkeypatch.setattr(provider_module, "load_generator_credentials", lambda: {
        "base_url": "https://original.invalid/v1", "api_key": "original-provider-key",
    })
    alias = AliasMapping("Qwen3.8-27B", "http://127.0.0.1:19002/v1")
    isolated = OpenAICompatibleProvider(base_url=alias.base_url, alias_mapping=alias)
    assert isolated.api_key == ""
    assert OpenAICompatibleProvider(base_url=alias.base_url).api_key == ""
    assert OpenAICompatibleProvider().api_key == "original-provider-key"
    explicit = OpenAICompatibleProvider(base_url=alias.base_url, alias_mapping=alias,
                                        api_key="alias-provider-key")
    assert explicit.api_key == "alias-provider-key"


def test_nullable_stream_fields_are_absent_actions():
    chunks = [
        {"choices": None},
        {"model": "Qwen3.8-27B", "choices": [{"index": 0,
            "delta": {"content": "observed", "tool_calls": None}}]},
        {"choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0, "id": "tool-1",
            "function": {"name": "bash", "arguments": None}}]}}]},
        {"choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0,
            "function": {"name": None, "arguments": "{\"command\":\"pwd\"}"}}]}}]},
        {"choices": [], "usage": {"prompt_tokens": 10, "completion_tokens": 1}},
    ]
    stream = io.BytesIO(("".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks)
                         + "data: [DONE]\n\n").encode())
    body, ttft = OpenAICompatibleProvider()._read_response(stream, True, time.perf_counter())
    assert body["choices"][0]["message"]["content"] == "observed"
    assert body["usage"]["completion_tokens"] == 1
    assert body["choices"][0]["message"]["tool_calls"][0]["function"] == {
        "name": "bash", "arguments": '{"command":"pwd"}',
    }
    assert ttft is not None


def test_unknown_usage_reserves_the_existing_request_allowance():
    data = {"max_tokens": 1000000, "consumed_total_tokens": 100}
    provider_module._record_budget(data, None, None, 2048)
    assert data["consumed_total_tokens"] == 100
    assert data["reserved_unknown_tokens"] == 2048
    assert data["remaining_tokens"] == 1000000 - 100 - 2048


class MockResponsesSSEHandler(BaseHTTPRequestHandler):
    """Local HTTP mock server streaming standard OpenAI /v1/responses SSE events."""

    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8"))

        input_data = payload.get("input", [])
        has_tool_output = any(
            isinstance(item, dict) and item.get("type") == "function_call_output"
            for item in input_data
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        if has_tool_output:
            events = [
                ("response.output_text.delta", {"delta": "Thought: Tool executed.\nAction: echo DONE"}),
                ("response.completed", {
                    "response": {
                        "model": "gpt-6-luna",
                        "status": "completed",
                        "usage": {"input_tokens": 100, "output_tokens": 20, "output_tokens_details": {"reasoning_tokens": 5}}
                    }
                }),
            ]
        else:
            events = [
                ("response.output_item.added", {
                    "item": {"type": "function_call", "call_id": "call_123", "name": "get_test_status"}
                }),
                ("response.function_call_arguments.delta", {"call_id": "call_123", "delta": "{}"}),
                ("response.output_item.done", {
                    "item": {"type": "function_call", "call_id": "call_123", "name": "get_test_status", "arguments": "{}"}
                }),
                ("response.completed", {
                    "response": {
                        "model": "gpt-6-luna",
                        "status": "completed",
                        "usage": {"input_tokens": 80, "output_tokens": 15, "output_tokens_details": {"reasoning_tokens": 0}}
                    }
                }),
            ]

        for ev_name, ev_data in events:
            time.sleep(0.005)
            chunk = f"event: {ev_name}\ndata: {json.dumps(ev_data)}\n\n".encode("utf-8")
            self.wfile.write(chunk)
            self.wfile.flush()

        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


class TestProviders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_address = ("127.0.0.1", 19888)
        cls.httpd = HTTPServer(cls.server_address, MockResponsesSSEHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        self.spec = ModelSpec(
            model_id="gpt-6-luna",
            pool="Strong",
            provider="jiji",
            display_name="GPT 6 Luna",
            context_window=128000,
            max_output_tokens=4096,
            native_efforts=("none", "low", "medium", "high"),
            input_price_per_1m=2.5,
            output_price_per_1m=10.0,
            reasoning_price_per_1m=10.0,
            cache_read_price_per_1m=0.3,
        )

    def test_mock_provider(self):
        """Verifies MockGeneratorProvider execution and token statistics."""
        provider = MockGeneratorProvider()
        messages = [{"role": "user", "content": "Fix git branch problem"}]
        resp = provider.generate(messages, self.spec, native_effort="none")
        self.assertTrue(len(resp.content) > 0)
        self.assertTrue(resp.prompt_tokens > 0)
        self.assertTrue(resp.completion_tokens > 0)
        self.assertFalse(resp.is_finish)

    def test_oracle_provider(self):
        """Verifies OracleGeneratorProvider completes on second turn."""
        provider = OracleGeneratorProvider()
        messages_t1 = [{"role": "user", "content": "Task 1"}]
        resp1 = provider.generate(messages_t1, self.spec)
        self.assertFalse(resp1.is_finish)

        messages_t2 = [
            {"role": "user", "content": "Task 1"},
            {"role": "assistant", "content": resp1.content},
            {"role": "user", "content": "Observation: ok"},
        ]
        resp2 = provider.generate(messages_t2, self.spec)
        self.assertTrue(resp2.is_finish)
        self.assertEqual(resp2.action, "FINISH")

    def test_react_parser(self):
        """Verifies extraction of thought and bash action."""
        text = "Thought: Inspecting files.\nAction: ls -la"
        thought, action, is_finish = parse_react_response(text)
        self.assertEqual(thought, "Inspecting files.")
        self.assertEqual(action, "ls -la")
        self.assertFalse(is_finish)

        finish_text = "Thought: Task completed.\nAction: FINISH"
        _, _, finish_flag = parse_react_response(finish_text)
        self.assertTrue(finish_flag)

    def test_safe_tool_executor(self):
        """Verifies execute_safe_tool returns ready status."""
        out = execute_safe_tool("get_test_status", {})
        self.assertEqual(out.get("status"), "ready")
        self.assertIn("timestamp_utc", out)

    def test_responses_streaming_and_tool_roundtrip(self):
        """Verifies SSE streaming and tool calling roundtrip against mock server."""
        provider = OpenAIResponsesProvider(
            base_url="http://127.0.0.1:19888",
            api_key="test-key"
        )
        resp = provider.generate(
            messages=[{"role": "user", "content": "check status"}],
            model_spec=self.spec,
            native_effort="low",
            stream=True,
            tools=[GET_TEST_STATUS_TOOL],
            tool_executor=execute_safe_tool,
        )
        self.assertIsNotNone(resp.ttft_ms)
        self.assertEqual(len(resp.tool_calls), 1)
        self.assertEqual(resp.tool_calls[0]["name"], "get_test_status")
        self.assertEqual(resp.action, "echo DONE")
        self.assertEqual(resp.prompt_tokens, 180)
        self.assertEqual(resp.completion_tokens, 35)
        self.assertEqual(resp.reasoning_tokens, 5)


def test_reasoning_is_included_in_completion():
    spec = MODEL_REGISTRY["gpt-6-luna"]
    assert spec.calculate_cost(1000, 500, 300, 200) == pytest.approx(0.0057)
    with pytest.raises(ValueError):
        spec.calculate_cost(1, 10, 11)


def test_chat_raw_stream_keeps_tool_calls_and_usage(monkeypatch, isolated_accounting):
    chunks = [
        {"id": "fixture", "model": "gpt-6-luna", "choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0, "id": "call-a", "function": {"name": "bash", "arguments": '{"command":'}}]}}]},
        {"choices": [{"index": 0, "delta": {"tool_calls": [{"index": 0, "function": {"arguments": '"echo hello"}'}}]}, "finish_reason": "tool_calls"}]},
        {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 20, "completion_tokens_details": {"reasoning_tokens": 5}}},
    ]
    sent = []
    def open_response(request, **kwargs):
        sent.append(json.loads(request.data))
        return io.BytesIO("".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks).encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    raw, metrics = OpenAICompatibleProvider(api_key="fixture").query_raw(
        [{"role": "user", "content": "echo hello"}], MODEL_REGISTRY["gpt-6-luna"], "low",
        tools=[{"type": "function", "function": {"name": "bash"}}],
    )
    assert len(sent) == 1
    assert raw["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] == '{"command":"echo hello"}'
    assert metrics["ttft_ms"] is not None
    assert metrics["output_tokens_per_s"] > 0
    assert metrics["output_tokens_per_s"] == pytest.approx(20 * 1000 / metrics["latency_ms"])
    assert metrics["stream_output_tokens_per_s"] == pytest.approx(20 * 1000 / (metrics["latency_ms"] - metrics["ttft_ms"]))
    assert metrics["stream_output_tokens_per_s_status"] == "ESTIMATE"
    assert metrics["actual_billed_cost_usd"] is None
    assert metrics["cost_usd"] == pytest.approx(0.00036)
    assert json.loads(isolated_accounting.read_text())["consumed_total_tokens"] == 120


@pytest.mark.parametrize("returned,usage", [("gpt-6-luna", None), ("different-model", {"prompt_tokens": 10, "completion_tokens": 2})])
def test_unknown_evidence_not_invented(monkeypatch, returned, usage):
    body = {"model": returned, "choices": [{"message": {"content": "hi"}}], "usage": usage}
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", lambda *args, **kwargs: io.BytesIO(json.dumps(body).encode()))
    raw, metrics = OpenAICompatibleProvider(api_key="fixture").query_raw([], MODEL_REGISTRY["gpt-6-luna"], stream=False)
    assert metrics["status"] == "NOT_EVALUATED"
    assert metrics["cost_usd"] is None
    assert metrics["ttft_ms"] is None
    assert metrics["stream_output_tokens_per_s"] is None
    assert metrics["raw_usage"] == usage
    if usage is None:
        assert metrics["prompt_tokens"] is None


@pytest.mark.parametrize("provider_cls", [OpenAICompatibleProvider, OpenAIResponsesProvider])
def test_invalid_effort_is_not_sent(provider_cls, monkeypatch):
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", lambda *a, **kw: pytest.fail("unexpected paid request"))
    with pytest.raises(ValueError, match="Unsupported native_effort"):
        provider_cls(api_key="fixture").query_raw([], MODEL_REGISTRY["gpt-6-luna"], "invalid")


def test_v9_registry_keeps_unknown_capabilities():
    registry = ModelRegistry()
    actions = registry.list_legal_actions()
    assert set(V9_MODEL_IDS) <= {action["model"] for action in actions}
    for model_id in ("gpt-6.1-sol", "qwen3.8-flash"):
        spec = registry.get_spec(model_id)
        assert spec.context_window is spec.max_output_tokens is None
        assert spec.native_efforts == ()
        assert spec.context_status == spec.native_efforts_status == "NOT_MEASURED"
        assert spec.pricing_status == spec.identity_status == "NOT_MEASURED"
        assert spec.calculate_cost(100, 20) is None
        assert all(price is None for price in (
            spec.input_price_per_1m, spec.output_price_per_1m,
            spec.reasoning_price_per_1m, spec.cache_read_price_per_1m,
            spec.cache_write_price_per_1m,
        ))
        action = next(action for action in actions if action["model"] == model_id)
        assert action["native_effort"] == "none"
        assert action["native_efforts_status"] == "NOT_MEASURED"
        spec.validate_effort("none")


@pytest.mark.parametrize("model_id,target", [
    ("gpt-6-luna", "gpt-6-luna"),
    ("gpt-5.6-luna", "gpt-5.6-luna"),
    ("gpt-6.1-sol", "gpt-6-luna"),
    ("qwen3.8-flash", "gpt-6-luna"),
])
def test_authorized_luna_default_without_alias(monkeypatch, model_id, target):
    sent = []
    def open_response(request, **kwargs):
        payload = json.loads(request.data)
        sent.append(payload)
        return io.BytesIO(json.dumps({
            "model": payload["model"], "choices": [{"message": {"content": "hi"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2},
        }).encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    _, metrics = OpenAICompatibleProvider(api_key="fixture").query_raw(
        [], MODEL_REGISTRY[model_id], stream=False,
    )
    assert len(sent) == 1 and sent[0]["model"] == target
    assert metrics["request_model_id"] == target
    assert metrics.get("execution_mode") != "ALIAS_SMOKE"
    assert metrics["cost_usd"] is not None


@pytest.mark.parametrize("model_id", V9_MODEL_IDS)
@pytest.mark.parametrize("stream", [False, True])
def test_v9_alias_query_reuses_transport_and_accounting(monkeypatch, isolated_accounting, model_id, stream):
    backend = "fixture-qwen3.8-27b"
    mapping = AliasMapping(backend, "http://alias.invalid/v1/")
    usage = {"prompt_tokens": 100, "completion_tokens": 20, "cost": 99.0, "cost_currency": "USD",
             "completion_tokens_details": {"reasoning_tokens": 5},
             "prompt_tokens_details": {"cached_tokens": 40}}
    tool_call = {"id": "fixture-tool", "type": "function",
                 "function": {"name": "bash", "arguments": '{"command":"echo fixture"}'}}
    message = {"role": "assistant", "content": "Thought: Next step.\nAction: echo fixture", "tool_calls": [tool_call]}
    body = {"id": "fixture-response", "model": backend,
            "choices": [{"index": 0, "message": message, "finish_reason": "tool_calls"}], "usage": usage}
    sent, logged = [], []
    def open_response(request, **kwargs):
        payload = json.loads(request.data)
        sent.append((request.full_url, payload))
        if not stream:
            return io.BytesIO(json.dumps(body).encode())
        delta = {**message, "tool_calls": [{"index": 0, **tool_call}]}
        chunks = [
            {"id": body["id"], "model": backend, "choices": [{"index": 0, "delta": delta, "finish_reason": "tool_calls"}]},
            {"choices": [], "usage": usage},
        ]
        return io.BytesIO(("".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n").encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    monkeypatch.setattr(provider_module.global_multi_model_logger, "log_call", lambda **kwargs: logged.append(kwargs))
    messages = [{"role": "user", "content": "Task"}, {"role": "assistant", "content": "Prior step"},
                {"role": "user", "content": "Actual prior tool output"}]
    tools = [{"type": "function", "function": {"name": "bash"}}]
    result = OpenAICompatibleProvider(
        base_url="http://original.invalid/v1", api_key="fixture", alias_mapping=mapping,
    ).generate(messages, MODEL_REGISTRY[model_id], "high", tools=tools, stream=stream)
    assert len(sent) == 1
    url, payload = sent[0]
    assert url == "http://alias.invalid/v1/chat/completions"
    assert payload["model"] == backend
    assert payload["messages"] == messages and payload["tools"] == tools
    assert "reasoning_effort" not in payload
    assert payload["stream"] is stream
    if stream:
        assert payload["stream_options"] == {"include_usage": True}
        assert result.ttft_ms is not None
    metrics = result.metadata
    assert metrics["selected_model_id"] == model_id
    assert metrics["actual_backend_model_id"] == metrics["returned_model_id"] == backend
    assert metrics["requested_native_effort"] == "high"
    assert metrics["native_effort"] == metrics["effective_native_effort"] == "none"
    assert metrics["execution_mode"] == "ALIAS_SMOKE"
    assert metrics["alias_mapping_applied"] is True
    assert metrics["context_resend_required"] is None and metrics["context_resend_status"] == "UNKNOWN"
    assert metrics["raw_usage"] == usage
    assert result.cost_usd is None
    assert metrics["actual_billed_cost_usd"] == usage["cost"]
    assert metrics["cost_status"] == "LOCAL_COMPUTE_UNPRICED"
    assert result.tool_calls == [tool_call]
    assert result.prompt_tokens == 100 and result.completion_tokens == 20
    assert result.reasoning_tokens == 5 and result.cached_tokens == 40
    assert logged[0]["model_id"] == backend and logged[0]["provider"] == "local"
    assert logged[0]["reasoning_effort"] == "none"
    assert logged[0]["actual_billed_cost_usd"] == usage["cost"]
    budget = json.loads(isolated_accounting.read_text())
    assert budget["total_calls"] == 1 and budget["consumed_total_tokens"] == 120
    assert budget["max_tokens"] == 1000000


@pytest.mark.parametrize("reported_cost", [None, 0.125])
def test_v9_alias_keeps_backend_reported_cost(monkeypatch, isolated_accounting, reported_cost):
    mapping = AliasMapping("Qwen3.8-27B", "https://public-gateway.invalid/v1",
                           cost_status="BACKEND_PRICE_NOT_MEASURED")
    usage = {"prompt_tokens": 10, "completion_tokens": 2}
    if reported_cost is not None:
        usage["cost"] = reported_cost
    body = {"model": mapping.backend_model_id,
            "choices": [{"message": {"content": "hi"}}], "usage": usage}
    sent, logged = [], []
    def open_response(request, **kwargs):
        sent.append((request.full_url, json.loads(request.data)))
        return io.BytesIO(json.dumps(body).encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    monkeypatch.setattr(provider_module.global_multi_model_logger, "log_call", lambda **kwargs: logged.append(kwargs))
    result = OpenAICompatibleProvider(api_key="fixture", alias_mapping=mapping).generate(
        [], MODEL_REGISTRY["gpt-6.1-sol"], "high",
    )
    assert len(sent) == 1 and sent[0][0] == "https://public-gateway.invalid/v1/chat/completions"
    assert sent[0][1]["model"] == "Qwen3.8-27B"
    assert "reasoning_effort" not in sent[0][1]
    assert result.cost_usd is None
    assert result.metadata["cost_status"] == "BACKEND_PRICE_NOT_MEASURED"
    assert result.metadata["actual_billed_cost_usd"] is None
    assert result.metadata["raw_reported_cost"] == reported_cost
    assert result.metadata["reported_cost_unit"] == "NOT_REPORTED"
    assert result.metadata["raw_usage"] == usage
    assert result.metadata["provider"] == logged[0]["provider"] == "openai-compatible"
    assert logged[0]["actual_billed_cost_usd"] is None
    assert json.loads(isolated_accounting.read_text())["total_calls"] == 1


def test_v9_alias_can_be_disabled(monkeypatch, isolated_accounting):
    sent = []
    def open_response(request, **kwargs):
        payload = json.loads(request.data)
        sent.append((request.full_url, payload["model"]))
        return io.BytesIO(json.dumps({"model": payload["model"],
            "choices": [{"message": {"content": "hi"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2}}).encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    provider = OpenAICompatibleProvider(base_url="http://original.invalid/v1", api_key="fixture",
        alias_mapping=AliasMapping("fixture-qwen3.8-27b", "http://alias.invalid/v1"))
    _, aliased = provider.query_raw([], MODEL_REGISTRY["gpt-6-luna"], stream=False)
    provider.alias_mapping = None
    _, normal = provider.query_raw([], MODEL_REGISTRY["gpt-6-luna"], stream=False)
    assert sent == [("http://alias.invalid/v1/chat/completions", "fixture-qwen3.8-27b"),
                    ("http://original.invalid/v1/chat/completions", "gpt-6-luna")]
    assert aliased["cost_usd"] is None and normal["cost_usd"] is not None
    assert normal.get("execution_mode") != "ALIAS_SMOKE"
    assert AliasMapping("fixture-qwen3.8-27b").resolve("gpt-5.6-luna", "low") is None
    assert json.loads(isolated_accounting.read_text())["total_calls"] == 2


def test_v9_alias_uses_shared_token_limit(monkeypatch, isolated_accounting):
    isolated_accounting.write_text(json.dumps({"max_tokens": 1000000, "consumed_total_tokens": 999999}))
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", lambda *a, **kw: pytest.fail("unexpected request"))
    with pytest.raises(RuntimeError, match="Existing total-token budget"):
        OpenAICompatibleProvider(api_key="fixture", alias_mapping=AliasMapping("fixture-qwen3.8-27b")).query_raw(
            [], MODEL_REGISTRY["gpt-6.1-sol"], "high", stream=False,
        )
    assert json.loads(isolated_accounting.read_text()).get("total_calls", 0) == 0


def test_responses_single_request_has_no_implicit_tools(monkeypatch, isolated_accounting):
    body = {"model": "gpt-6-luna", "output": [{"type": "function_call", "call_id": "a", "name": "bash", "arguments": "{}"}], "usage": {"input_tokens": 10, "output_tokens": 2}}
    sent = []
    def open_response(req, **kwargs):
        sent.append(json.loads(req.data))
        return io.BytesIO(json.dumps(body).encode())
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", open_response)
    result = OpenAIResponsesProvider(api_key="fixture").generate([], MODEL_REGISTRY["gpt-6-luna"], max_tokens=32, stream=False)
    assert len(sent) == 1
    assert "tools" not in sent[0]
    assert sent[0]["max_output_tokens"] == 32
    assert result.tool_calls == body["output"]
    assert json.loads(isolated_accounting.read_text())["total_calls"] == 1


def test_budget_updates_do_not_lose_concurrent_usage(isolated_accounting):
    workers = [threading.Thread(target=update_token_budget, args=(10, 2)) for _ in range(6)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    budget = json.loads(isolated_accounting.read_text())
    assert budget["consumed_total_tokens"] == 72
    assert budget["total_calls"] == 6


@pytest.fixture
def native_upstream(monkeypatch, isolated_accounting):
    calls = []
    upstream_key = "upstream-fixture-credential-stays-on-host"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_POST(self):
            assert self.path == "/v1/chat/completions"
            assert self.headers["Authorization"] == f"Bearer {upstream_key}"
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append(payload)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            chunks = [
                {"id": "fixture-native-call", "model": payload["model"], "created": 1, "choices": [{"index": 0, "delta": {"role": "assistant", "tool_calls": [{"index": 0, "id": "fixture-tool", "type": "function", "function": {"name": "bash", "arguments": '{"command":"echo not-executed-by-relay"}'}}]}, "finish_reason": None}]},
                {"choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]},
                {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 20, "completion_tokens_details": {"reasoning_tokens": 5}}},
            ]
            for chunk in chunks:
                self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .05}, daemon=True)
    thread.start()
    monkeypatch.setattr(provider_module, "load_generator_credentials", lambda: {
        "base_url": f"http://127.0.0.1:{server.server_address[1]}/v1", "api_key": upstream_key,
    })
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    monkeypatch.setattr(provider_module.urllib.request, "urlopen", opener.open)
    monkeypatch.setattr(provider_module, "execute_safe_tool", lambda *a: pytest.fail("relay executed a tool"))
    try:
        yield calls, upstream_key
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize("native_stream", [False, True])
def test_native_relay_one_request_one_budget_update(tmp_path, native_upstream, isolated_accounting, native_stream):
    calls, upstream_key = native_upstream
    payload = {"model": "openai/gpt-5.6-luna", "messages": [{"role": "user", "content": "Fixture command"}],
               "max_completion_tokens": 64, "stream": native_stream,
               "tools": [{"type": "function", "function": {"name": "bash", "parameters": {"type": "object"}}}]}
    with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        assert relay["base_url"] == f"http://host.docker.internal:{relay['port']}/v1"
        assert relay["api_key"] != upstream_key
        request = urllib.request.Request(f"http://127.0.0.1:{relay['port']}/v1/chat/completions",
            data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {relay['api_key']}", "Content-Type": "application/json", "X-Session-ID": "fixture-trial__agent"})
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode()
        if native_stream:
            chunks = [json.loads(line[5:]) for line in raw.splitlines() if line.startswith("data:") and line != "data: [DONE]"]
            assert chunks[0]["choices"][0]["delta"]["tool_calls"][0]["function"]["name"] == "bash"
            assert chunks[-1]["usage"]["completion_tokens"] == 20
            assert "data: [DONE]" in raw
        else:
            body = json.loads(raw)
            assert body["model"] == "gpt-5.6-luna"
            assert body["choices"][0]["message"]["tool_calls"][0]["function"]["name"] == "bash"
            assert body["usage"]["completion_tokens"] == 20
        assert len(calls) == 1
        assert calls[0]["messages"] == payload["messages"]
        assert calls[0]["tools"] == payload["tools"]
        assert calls[0]["reasoning_effort"] == "low"
        assert calls[0]["max_tokens"] == 64
        assert calls[0]["stream"] is True
        budget = json.loads(isolated_accounting.read_text())
        assert budget["consumed_total_tokens"] == 120
        assert budget["total_calls"] == 1
        assert budget["max_tokens"] == 1000000
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", relay["port"]), timeout=.1)
    log = (tmp_path / "events.jsonl").read_text()
    assert relay["api_key"] not in log and upstream_key not in log
    records = [json.loads(line) for line in log.splitlines()]
    generation = [record for record in records if record["event"] == "GENERATOR_END"]
    assert len(generation) == 1
    assert generation[0]["budget_accounted"] is True
    assert generation[0]["source"] == "native_generator_relay"
    assert generation[0]["native_stream"] is native_stream
    assert generation[0]["ttft_ms"] is not None
    assert generation[0]["output_tokens_per_s"] > 0
    assert generation[0]["actual_billed_cost_usd"] is None
    assert generation[0]["episode_id"] == "fixture-trial__agent"
    assert generation[0]["step"] == 0
    assert generation[0]["policy"] == "mini-swe-agent"
    assert generation[0]["sample_kind"] == "benchmark"
    assert generation[0]["episode_estimated_cost_usd"] == generation[0]["cost_usd"]
    assert generation[0]["episode_cost_limit_usd"] == 3.0
    assert records[-1]["event"] == "NATIVE_RELAY_STOP"


def test_native_relay_tracks_episode_steps_independently(tmp_path, native_upstream, isolated_accounting):
    calls, _ = native_upstream
    with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        for episode_id in ("first-trial", "second-trial", "first-trial"):
            request = urllib.request.Request(f"http://127.0.0.1:{relay['port']}/v1/chat/completions",
                data=json.dumps({"model":"gpt-6-luna", "messages":[], "max_tokens":64}).encode(),
                headers={"Authorization":f"Bearer {relay['api_key']}", "X-Session-ID":episode_id})
            with urllib.request.urlopen(request) as response:
                assert response.status == 200
                response.read()
    generations = [row for row in map(json.loads, (tmp_path / "events.jsonl").read_text().splitlines())
                   if row["event"] == "GENERATOR_END"]
    assert [(row["episode_id"], row["step"]) for row in generations] == [
        ("first-trial", 0), ("second-trial", 0), ("first-trial", 1)]
    assert all(row["sample_kind"] == "benchmark" and row["policy"] == "mini-swe-agent" for row in generations)
    budget = json.loads(isolated_accounting.read_text())
    assert len(calls) == budget["total_calls"] == 3
    assert budget["consumed_total_tokens"] == 360


@pytest.mark.parametrize("case,expected_code", [("credential", 401), ("model", 400), ("effort", 400), ("budget", 502)])
def test_native_relay_does_not_dispatch_rejected_request(tmp_path, native_upstream, isolated_accounting, case, expected_code):
    calls, upstream_key = native_upstream
    if case == "budget":
        isolated_accounting.write_text(json.dumps({"max_tokens":1000000,"consumed_total_tokens":999999}))
    with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        payload = {"model":"not-authorized" if case == "model" else "gpt-6-luna", "messages":[],
                   "reasoning_effort":"invalid" if case == "effort" else "low", "max_tokens":32}
        request = urllib.request.Request(f"http://127.0.0.1:{relay['port']}/v1/chat/completions", data=json.dumps(payload).encode(),
            headers={"Authorization":"Bearer incorrect-fixture" if case == "credential" else f"Bearer {relay['api_key']}"})
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code == expected_code
        assert upstream_key not in error.value.read().decode()
    assert calls == []
    assert json.loads(isolated_accounting.read_text()).get("total_calls", 0) == 0


def test_native_relay_closes_after_context_error(tmp_path, native_upstream):
    with pytest.raises(RuntimeError, match="fixture context exit"):
        with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
            port = relay["port"]
            raise RuntimeError("fixture context exit")
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", port), timeout=.1)


def test_native_relay_restores_episode_cost_without_recharging(tmp_path, native_upstream, isolated_accounting):
    calls, _ = native_upstream
    (tmp_path / "run_config.json").write_text(json.dumps({"cost_limit":0.0005}))

    def request(relay, episode):
        req = urllib.request.Request(f"http://127.0.0.1:{relay['port']}/v1/chat/completions",
            data=json.dumps({"model":"gpt-6-luna", "messages":[], "max_tokens":64}).encode(),
            headers={"Authorization":f"Bearer {relay['api_key']}", "X-Session-ID":episode})
        with urllib.request.urlopen(req) as response:
            response.read()

    with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        request(relay, "original-episode")
    assert json.loads(isolated_accounting.read_text())["total_calls"] == 1
    with native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        assert json.loads(isolated_accounting.read_text())["total_calls"] == 1
        request(relay, "original-episode")
        with pytest.raises(urllib.error.HTTPError) as error:
            request(relay, "original-episode")
        assert error.value.code == 402
        request(relay, "separate-episode")
    assert len(calls) == 3
    budget = json.loads(isolated_accounting.read_text())
    assert budget["total_calls"] == 3
    assert budget["consumed_total_tokens"] == 360
    records = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    generations = [r for r in records if r["event"] == "GENERATOR_END"]
    assert [(r["episode_id"], r["step"]) for r in generations] == [
        ("original-episode", 0), ("original-episode", 1), ("separate-episode", 0)]
    assert [r["episode_estimated_cost_usd"] for r in generations] == pytest.approx([.00036, .00072, .00036])
    assert all(r["episode_cost_limit_usd"] == .0005 for r in generations)
    assert next(r for r in records if r["event"] == "ERROR")["error"] == "EPISODE_COST_LIMIT"
    assert not (tmp_path / "episode_budget.json").exists()


if __name__ == "__main__":
    unittest.main()
