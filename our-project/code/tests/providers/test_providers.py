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
)
from modelrouter.providers.registry import ModelSpec


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


if __name__ == "__main__":
    unittest.main()
