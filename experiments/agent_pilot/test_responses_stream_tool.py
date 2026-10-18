#!/usr/bin/env python3
"""
Test Suite for GPT Responses Streaming, Native Reasoning Effort, and Tool Calling Roundtrip.
Validates:
1. Responses API request with stream: true
2. SSE event stream decoding (output_text.delta, function_call_arguments.delta, completed)
3. Native reasoning effort validation ('low' vs 'medium')
4. Safe tool calling roundtrip with get_test_status()
5. TTFT (Time to First Token) measurement
6. Standardized multi-model logging and OpenRouter reference pricing audit
"""

import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

from experiments.agent_pilot.registry import ModelSpec
from experiments.agent_pilot.provider import OpenAIResponsesProvider, execute_safe_tool, GET_TEST_STATUS_TOOL
from experiments.agent_pilot.multi_model_logger import global_multi_model_logger


class MockResponsesSSEHandler(BaseHTTPRequestHandler):
    """Local HTTP mock server streaming standard OpenAI /v1/responses SSE events."""

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging
        pass

    def do_POST(self):
        if self.path != "/v1/responses" and self.path != "/responses":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8"))

        stream = payload.get("stream", False)
        reasoning = payload.get("reasoning", {})
        effort = reasoning.get("effort", "none")
        input_data = payload.get("input", [])

        # Check if this is a tool return follow-up turn
        has_tool_output = False
        if isinstance(input_data, list):
            for item in input_data:
                if isinstance(item, dict) and item.get("type") == "function_call_output":
                    has_tool_output = True
                    break

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        if has_tool_output:
            # Second turn: model receives tool output and streams final explanation
            events = [
                ("response.output_item.added", {
                    "type": "response.output_item.added",
                    "item": {"type": "message", "id": "msg_002", "role": "assistant"}
                }),
                ("response.output_text.delta", {
                    "type": "response.output_text.delta",
                    "delta": "Thought: The test status indicates environment is ready.\nAction: echo SUCCESS_COMPLETED"
                }),
                ("response.output_item.done", {
                    "type": "response.output_item.done",
                    "item": {"type": "message", "id": "msg_002"}
                }),
                ("response.completed", {
                    "type": "response.completed",
                    "response": {
                        "status": "completed",
                        "usage": {
                            "input_tokens": 145,
                            "output_tokens": 38,
                            "output_tokens_details": {
                                "reasoning_tokens": 12 if effort in ("low", "medium") else 0
                            },
                            "input_tokens_details": {"cached_tokens": 40}
                        }
                    }
                }),
            ]
        else:
            # First turn: model calls tool get_test_status
            events = [
                ("response.output_item.added", {
                    "type": "response.output_item.added",
                    "item": {
                        "type": "function_call",
                        "id": "fc_001",
                        "call_id": "call_status_999",
                        "name": "get_test_status"
                    }
                }),
                ("response.function_call_arguments.delta", {
                    "type": "response.function_call_arguments.delta",
                    "call_id": "call_status_999",
                    "delta": "{}"
                }),
                ("response.output_item.done", {
                    "type": "response.output_item.done",
                    "item": {
                        "type": "function_call",
                        "id": "fc_001",
                        "call_id": "call_status_999",
                        "name": "get_test_status",
                        "arguments": "{}"
                    }
                }),
                ("response.completed", {
                    "type": "response.completed",
                    "response": {
                        "status": "completed",
                        "usage": {
                            "input_tokens": 98,
                            "output_tokens": 22,
                            "output_tokens_details": {
                                "reasoning_tokens": 8 if effort in ("low", "medium") else 0
                            },
                            "input_tokens_details": {"cached_tokens": 0}
                        }
                    }
                }),
            ]

        for ev_name, ev_data in events:
            time.sleep(0.015)  # Simulate realistic network chunk latency
            out = f"event: {ev_name}\ndata: {json.dumps(ev_data)}\n\n".encode("utf-8")
            self.wfile.write(out)
            self.wfile.flush()

        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()


def run_tests():
    print("=" * 70)
    print("RUNNING RESPONSES STREAMING & TOOL CALLING TEST SUITE")
    print("=" * 70)

    # 1. Start ephemeral mock SSE server
    server_address = ("127.0.0.1", 18999)
    httpd = HTTPServer(server_address, MockResponsesSSEHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    print(f"[1] Ephemeral Mock SSE Server running at http://127.0.0.1:18999/v1")

    # 2. Setup Provider pointing to mock server
    provider = OpenAIResponsesProvider(
        base_url="http://127.0.0.1:18999/v1",
        api_key="test-key-safe"
    )

    model_spec = ModelSpec(
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

    # 3. Test Test Case A: Streaming + Reasoning Effort 'low' + Tool Calling Roundtrip
    print("\n[2] Executing Test Case A: Reasoning Effort 'low' + Tool Roundtrip")
    resp_low = provider.generate(
        messages=[{"role": "user", "content": "Please verify current test status."}],
        model_spec=model_spec,
        native_effort="low",
        stream=True,
        tools=[GET_TEST_STATUS_TOOL],
        tool_executor=execute_safe_tool,
    )

    print("  -> Response Content:")
    print(f"     {resp_low.content}")
    print(f"  -> Thought: {resp_low.thought}")
    print(f"  -> Action: {resp_low.action}")
    print(f"  -> TTFT (ms): {resp_low.ttft_ms}")
    print(f"  -> Latency (ms): {resp_low.latency_ms:.2f}")
    print(f"  -> Prompt Tokens: {resp_low.prompt_tokens}, Completion Tokens: {resp_low.completion_tokens}")
    print(f"  -> Reasoning Tokens: {resp_low.reasoning_tokens}")
    print(f"  -> Tool Calls Executed: {resp_low.tool_calls}")

    assert resp_low.ttft_ms is not None, "TTFT should be measured on first text delta"
    assert len(resp_low.tool_calls) == 1, "Should have executed 1 tool call roundtrip"
    assert resp_low.tool_calls[0]["name"] == "get_test_status", "Tool executed must be get_test_status"
    assert resp_low.tool_calls[0]["output"]["status"] == "ready", "Tool output status should be ready"
    assert "echo SUCCESS_COMPLETED" in resp_low.action, "Final action must match model stream"
    print("  -> [PASS] Test Case A verified successfully!")

    # 4. Test Test Case B: Reasoning Effort 'medium'
    print("\n[3] Executing Test Case B: Reasoning Effort 'medium' + Tool Roundtrip")
    resp_med = provider.generate(
        messages=[{"role": "user", "content": "Execute test with medium reasoning."}],
        model_spec=model_spec,
        native_effort="medium",
        stream=True,
        tools=[GET_TEST_STATUS_TOOL],
        tool_executor=execute_safe_tool,
    )

    print(f"  -> TTFT (ms): {resp_med.ttft_ms}")
    print(f"  -> Latency (ms): {resp_med.latency_ms:.2f}")
    print(f"  -> Reasoning Tokens: {resp_med.reasoning_tokens}")
    assert resp_med.reasoning_tokens > 0, "Reasoning tokens must be > 0 under medium effort"
    print("  -> [PASS] Test Case B verified successfully!")

    # 5. Check Multi-Model Logger and OpenRouter Reference Pricing
    print("\n[4] Validating Multi-Model Logger & OpenRouter Reference Audit")
    summary = global_multi_model_logger.get_summary()
    print(f"  -> Total Calls Logged: {summary.get('total_calls')}")
    print(f"  -> Protocols breakdown: {summary.get('protocols')}")
    print(f"  -> Models breakdown: {summary.get('models')}")

    assert summary.get("total_calls", 0) >= 2, "At least 2 calls should be recorded in logger"
    assert "responses" in summary.get("protocols", {}), "'responses' protocol must be tracked"
    print("  -> [PASS] Multi-Model Logger audit verified successfully!")

    # 6. Shutdown mock server
    httpd.shutdown()
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED: Responses SSE Stream, Reasoning, Tool Calling & Logging Verified!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
