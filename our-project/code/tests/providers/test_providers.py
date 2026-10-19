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
from modelrouter.providers.registry import ModelSpec
from modelrouter.providers.registry import MODEL_REGISTRY
from modelrouter.providers import provider as provider_module


@pytest.fixture(autouse=True)
def isolated_accounting(tmp_path, monkeypatch):
    budget = tmp_path / "token_budget.json"
    budget.write_text(json.dumps({"max_tokens": 1000000, "consumed_total_tokens": 0}))
    monkeypatch.setattr(provider_module, "_pilot_file", lambda name: budget)
    monkeypatch.setattr(provider_module, "load_generator_credentials", lambda: {})
    monkeypatch.setattr(provider_module.global_multi_model_logger, "log_call", lambda **kwargs: kwargs)
    return budget


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
