"""Provider interface for the single-agent generation path."""
from __future__ import annotations

import json
import io
import os
import sys
import time
import urllib.error
import urllib.request
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseGeneratorProvider, GeneratorResponse, ProviderResponseError, parse_react_response
from .protocols import ChatCompletions, Responses, response_error as protocol_response_error
from .simulation import MockGeneratorProvider, OracleGeneratorProvider
from .usage import _record_budget, _token_budget, update_token_budget
from .registry import ModelSpec


def load_generator_credentials() -> Dict[str, Any]:
    """Read the shared external text-model settings; never copy credentials."""
    path = Path(os.environ.get("EXTERNAL_TEXT_MODEL_CONFIG",
                               str(Path.home() / ".agent-global/外部文本模型.local.json")))
    return json.loads(path.read_text(encoding="utf-8"))



class OpenAICompatibleProvider(BaseGeneratorProvider):
    """Single-request Chat Completions transport; tools belong to the agent."""

    protocol = "chat_completions"

    def __init__(
        self, base_url: Optional[str] = None, api_key: Optional[str] = None,
        request_timeout_sec: float = 60.0,
        model_endpoints: Optional[Dict[str, Dict[str, str]]] = None,
    ):
        creds = load_generator_credentials()
        self.base_url = (base_url or creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        credential_endpoint = (creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key if api_key is not None else (
            creds.get("api_key", "") if self.base_url == credential_endpoint else ""
        )
        self.request_timeout_sec = request_timeout_sec
        self.model_endpoints = {item["model"]: item for item in creds.get("providers", [])}
        self.model_endpoints.update(creds.get("model_endpoints", {}))
        self.model_endpoints.update(model_endpoints or {})
        self.account_endpoints = creds.get("account_endpoints", {})
        self.luna_registry = None
        if creds.get("luna_provider_project"):
            source = Path(creds["luna_provider_project"]) / "code/cweaver_v2/src"
            sys.path.insert(0, str(source))
            from cweaver.models.provider import ProviderRegistry
            self.luna_registry = ProviderRegistry()

    @staticmethod
    def _record_response_bytes(raw, capture, secret):
        if capture is not None:
            capture.write(raw.replace(secret, b"[REDACTED_API_KEY]") if secret else raw)
            capture.flush()

    def candidate_conditions(self, model_spec, input_tokens, max_output_tokens):
        """Expose current non-secret endpoint facts before selection; no HTTP call."""
        target = model_spec.model_id
        endpoint = (self.luna_registry.get_endpoint(self.account_endpoints[target])
                    if self.luna_registry is not None and target in self.account_endpoints else None)
        result = {"model_id": target, "provider": model_spec.provider,
                  "endpoint_id": None, "base_url": self.base_url,
                  "protocol": model_spec.protocol or self.protocol,
                  "availability": "UNKNOWN", "exclusion_reason": None,
                  "tool_supported": model_spec.tool_supported,
                  "input_tokens_estimate": input_tokens,
                  "input_tokens_status": "ESTIMATED_UTF8_BYTES_UPPER_BOUND",
                  "requested_output_tokens": max_output_tokens,
                  "cache_session_reuse": "NOT_MEASURED", "physical_kv_shared": "UNKNOWN"}
        capacity, output_capacity = model_spec.context_window, model_spec.max_output_tokens
        credentials = self.model_endpoints.get(target)
        if credentials is not None:
            result.update(endpoint_id=credentials.get("endpoint_id"), base_url=credentials.get("base_url"),
                          availability="CONFIGURED_NOT_PROBED")
            capacity = credentials.get("context_window") or capacity
            output_capacity = credentials.get("max_output_tokens") or output_capacity
        elif target == "glm-5.3-flash" and endpoint is None:
            result.update(base_url=None, availability="UNAVAILABLE", exclusion_reason="MODEL_ENDPOINT_UNBOUND")
        if endpoint is not None:
            result.update(endpoint_id=endpoint.endpoint_id, base_url=endpoint.base_url,
                          availability=("RECORDED_UNHEALTHY" if not endpoint.is_healthy else
                              "RECORDED_HEALTHY" if endpoint.last_checked_iso or endpoint.success_count else "CONFIGURED_NOT_PROBED"),
                          last_status_time=endpoint.last_checked_iso)
            capacity = endpoint.context_window or capacity
            output_capacity = endpoint.max_output_tokens or output_capacity
            if not endpoint.is_healthy:
                result["exclusion_reason"] = "RECORDED_ENDPOINT_UNHEALTHY"
        if model_spec.tool_supported is False:
            result["exclusion_reason"] = "TOOLS_NOT_SUPPORTED"
        if input_tokens + max_output_tokens > capacity:
            result["exclusion_reason"] = "CONTEXT_CAPACITY_EXCEEDED"
        if max_output_tokens > output_capacity:
            result["exclusion_reason"] = "OUTPUT_CAPACITY_EXCEEDED"
        result.update(context_capacity=capacity, output_capacity=output_capacity)
        return result


    def query_raw(self, messages, model_spec, native_effort="none", max_tokens=1024,
                  tools=None, stream=True, *, response_format=None, raw_response_path=None):
        """Switch only registered Luna accounts after a failed transport response."""
        excluded, attempts = [], []
        while True:
            attempt_started = time.perf_counter()
            try:
                body, metrics = self._query_raw(
                    messages, model_spec, native_effort, max_tokens, tools, stream,
                    response_format=response_format, raw_response_path=raw_response_path,
                    excluded_endpoints=excluded)
            except (urllib.error.HTTPError, ProviderResponseError) as exc:
                endpoint = (exc.metrics["provider_endpoint_id"] if isinstance(exc, ProviderResponseError)
                            else exc.provider_endpoint_id)
                retry = (model_spec.model_id == "gpt-6-luna" and endpoint is not None and
                         (isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 429, 502, 503, 509, 520)
                          or isinstance(exc, ProviderResponseError) and str(exc) in
                          ("EMPTY_RESPONSE", "INCOMPLETE_RESPONSE", "INCOMPLETE_TOOL_CALL", "rate_limit_error")))
                attempt = dict(exc.metrics) if isinstance(exc, ProviderResponseError) else {
                    "http_status": exc.code, "usage_status": "MISSING", "cost_usd": None,
                    "prompt_tokens": None, "completion_tokens": None,
                    "latency_ms": (time.perf_counter() - attempt_started) * 1000}
                attempt.update(provider_endpoint_id=endpoint, error=str(exc))
                attempts.append(attempt)
                exc.account_attempts = attempts
                if isinstance(exc, ProviderResponseError):
                    exc.metrics["account_attempts"] = attempts
                if not retry:
                    raise
                excluded.append(endpoint)
                if not self.luna_registry.list_active_endpoints("luna", "gpt-6-luna", excluded):
                    raise
                raw_response_path = None
                continue
            attempts.append(dict(metrics))
            if len(attempts) > 1:
                metrics["account_attempts"] = attempts
                metrics["account_attempts_elapsed_ms"] = sum(item["latency_ms"] for item in attempts)
                known_costs = [item["cost_usd"] for item in attempts if item.get("cost_usd") is not None]
                metrics["known_model_rate_cost_usd"] = sum(known_costs) if known_costs else None
                for field in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens", "cache_write_tokens", "cost_usd", "actual_billed_cost_usd"):
                    values = [item.get(field) for item in attempts]
                    metrics[field] = sum(values) if all(value is not None for value in values) else None
                metrics["usage_status"] = "REPORTED" if metrics["prompt_tokens"] is not None and metrics["completion_tokens"] is not None else "PARTIAL_ACCOUNT_SWITCH"
            return body, metrics

    def _query_raw(
        self,
        messages: List[Dict[str, Any]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = True,
        *,
        response_format: Optional[Dict[str, Any]] = None,
        raw_response_path: Optional[str | Path] = None,
        excluded_endpoints=(),
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return (native_response, metrics); one request, no execution or retry.

        Usage accounting is completed here. Callers must not charge it again.
        Missing usage, returned identity or billing remains explicitly unknown.
        raw_response_path enables local-only diagnostic capture for this request.
        Capture contains response bytes only, with any echoed request key removed.
        """
        target = model_spec.model_id
        target_spec = model_spec
        effective_effort = native_effort
        request_api_key = self.api_key
        request_protocol = model_spec.protocol or self.protocol
        request_base_url = self.base_url
        provider_name = model_spec.provider
        pool_endpoint = None
        endpoint_credentials = self.model_endpoints.get(target)
        if endpoint_credentials is not None:
            request_base_url = endpoint_credentials.get("base_url", request_base_url).rstrip("/")
            request_api_key = endpoint_credentials.get("api_key", request_api_key)
        if self.luna_registry is not None and (target == "gpt-6-luna" or target in self.account_endpoints):
            pool_endpoint = (self.luna_registry.get_endpoint(self.account_endpoints[target])
                             if target in self.account_endpoints and self.account_endpoints[target] not in excluded_endpoints else
                             self.luna_registry.select_active_endpoint("luna", target, excluded_endpoints))
            if pool_endpoint is None:
                raise RuntimeError("No active Luna account endpoint")
            request_base_url = pool_endpoint.base_url
            request_api_key = pool_endpoint.api_key
            if pool_endpoint.max_output_tokens is not None:
                max_tokens = min(max_tokens, pool_endpoint.max_output_tokens)
        if target == "glm-5.3-flash" and endpoint_credentials is None and pool_endpoint is None:
            raise RuntimeError("No configured provider endpoint for glm-5.3-flash")
        model_spec.validate_effort(effective_effort)
        transport = Responses if request_protocol == "responses" else ChatCompletions
        payload = transport.payload(messages, target, effective_effort, max_tokens, tools, stream)
        if response_format is not None:
            if request_protocol == "responses":
                payload["text"] = {"format": response_format}
            else:
                payload["response_format"] = response_format
        endpoint = "/chat/completions" if request_protocol == "chat_completions" else "/responses"
        request = urllib.request.Request(
            request_base_url + endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {request_api_key}",
                     "User-Agent": "curl/8.7.1" if pool_endpoint or target == "gpt-6-luna" else "ModelRouter/10"},
            method="POST",
        )
        started = time.perf_counter()
        input_bound = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        request_bound = input_bound + max_tokens
        with ExitStack() as files:
            capture = None
            if raw_response_path is not None:
                capture_path = Path(raw_response_path)
                capture_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                capture = files.enter_context(os.fdopen(os.open(
                    capture_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"))
            try:
                try:
                    with urllib.request.urlopen(request, timeout=self.request_timeout_sec) as response:
                        http_status = response.status
                        response_content_type = response.headers.get("Content-Type")
                        body, ttft_ms = transport.read(
                            response, stream or "text/event-stream" in (response_content_type or ""),
                            started, capture, request_api_key.encode("utf-8"), self._record_response_bytes)
                except urllib.error.HTTPError as exc:
                    exc.provider_endpoint_id = pool_endpoint.endpoint_id if pool_endpoint else None
                    if capture is not None:
                        raw = exc.read()
                        self._record_response_bytes(raw, capture, request_api_key.encode("utf-8"))
                        # Existing HTTPError consumers must still be able to read the body.
                        exc.read = io.BytesIO(raw).read
                    raise
            except (Exception, KeyboardInterrupt) as exc:
                with _token_budget() as budget:
                    _record_budget(budget, None, None, request_bound)
                if pool_endpoint is not None:
                    self.luna_registry.record_request_complete(
                        pool_endpoint.endpoint_id, (time.perf_counter() - started) * 1000,
                        status="failed", error=f"HTTP {exc.code}" if isinstance(exc, urllib.error.HTTPError)
                        else type(exc).__name__)
                raise
        raw_usage = body.get("usage")
        p_tokens, c_tokens, r_tokens, cached, cache_written = transport.usage(raw_usage or {})
        usage_consistent = r_tokens is None or c_tokens is None or r_tokens <= c_tokens
        reported_completion = (raw_usage or {}).get("completion_tokens") if request_protocol == "chat_completions" else (raw_usage or {}).get("output_tokens")
        with _token_budget() as budget:
            _record_budget(budget, p_tokens if usage_consistent else None,
                           c_tokens if usage_consistent else None, request_bound)
        latency_ms = (time.perf_counter() - started) * 1000
        returned = body.get("model")
        matched = returned == target
        identity_status = "MATCHED_REQUEST" if matched else ("MISSING" if not returned else "MISMATCH")
        returned_effort = (body.get("reasoning") or {}).get("effort") or body.get("reasoning_effort")
        effort_status = ("NOT_REPORTED" if returned_effort is None else
                         "PROVIDER_REPORTED_MATCH" if returned_effort == effective_effort else
                         "PROVIDER_REPORTED_MISMATCH")
        usage_complete = p_tokens is not None and c_tokens is not None
        cost = target_spec.calculate_cost(p_tokens, c_tokens, r_tokens or 0, cached or 0, cache_written or 0) if usage_complete and usage_consistent and matched else None
        # Vendor cost is distinct from the configured price estimate.
        reported_cost = (raw_usage or {}).get("cost")
        reported_cost_unit = (raw_usage or {}).get("cost_currency") or (raw_usage or {}).get("currency")
        billed_cost = reported_cost if reported_cost_unit == "USD" else None
        stream_elapsed_ms = latency_ms - ttft_ms if stream and ttft_ms is not None else None
        stream_output_tokens_per_s = (
            c_tokens * 1000 / stream_elapsed_ms
            if usage_complete and stream_elapsed_ms is not None and stream_elapsed_ms > 0 else None
        )
        response_error = protocol_response_error(body, request_protocol)
        if not response_error and not matched:
            response_error = "MODEL_IDENTITY_MISMATCH"
        elif not response_error and effort_status == "PROVIDER_REPORTED_MISMATCH":
            response_error = "NATIVE_EFFORT_MISMATCH"
        if pool_endpoint is not None:
            self.luna_registry.record_request_complete(
                pool_endpoint.endpoint_id, latency_ms, tokens=(p_tokens or 0) + (c_tokens or 0),
                status="success" if matched and not response_error else "failed",
                error=response_error if response_error or matched else "model identity mismatch",
                request_id=body.get("id", ""))
        metrics = {
            "requested_model_id": model_spec.model_id,
            "selected_model_id": model_spec.model_id,
            "response_id": body.get("id"),
            "request_model_id": target,
            "returned_model_id": returned,
            "provider": provider_name,
            "provider_base_url": "PRIVATE_ACCOUNT_POOL" if pool_endpoint else request_base_url,
            "provider_endpoint_id": pool_endpoint.endpoint_id if pool_endpoint else (endpoint_credentials or {}).get("endpoint_id"),
            "actual_backend_model_id": None,
            "physical_backend_identity_status": "NOT_REPORTED",
            "protocol": request_protocol,
            "http_status": http_status,
            "response_content_type": response_content_type,
            "diagnostic_capture_enabled": raw_response_path is not None,
            "finish_reason": (body.get("status") if request_protocol == "responses"
                              else next((choice.get("finish_reason") for choice in body.get("choices", [])), None)),
            "response_status": response_error or "COMPLETE",
            "stream_end": body.get("_stream_end"),
            "incomplete_details": body.get("incomplete_details"),
            "native_effort": effective_effort,
            "requested_native_effort": native_effort,
            "request_native_effort": effective_effort,
            "sent_effort_parameter": {name: payload[name] for name in ("thinking", "reasoning", "reasoning_effort")
                                      if name in payload},
            "returned_native_effort": returned_effort,
            "native_effort_status": effort_status,
            "stream": stream,
            "requested_max_output_tokens": max_tokens,
            "reported_max_output_tokens": body.get("max_output_tokens"),
            "raw_usage": raw_usage,
            "usage_status": "INCONSISTENT_REASONING_SUBSET" if not usage_consistent else "REPORTED" if usage_complete else "MISSING",
            "identity_status": identity_status,
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
            "cost_basis": "REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE",
            "backend_model_rate_cost_usd": cost,
            "backend_model_rate_source": target_spec.pricing_source,
            "backend_model_rate_status": target_spec.pricing_status,
            "cache_cost_policy": "Missing cache counts stay null; corresponding input uses the ordinary input rate",
            "reasoning_cost_policy": "Reasoning is included in completion tokens and charged once",
            "cost_status": target_spec.pricing_status if cost is not None else "UNKNOWN",
            "actual_billed_cost_usd": billed_cost,
            "raw_reported_cost": reported_cost,
            "reported_cost_unit": reported_cost_unit or "NOT_REPORTED",
            "budget_accounted": True,
            "status": "RECORDED" if usage_complete and matched else "NOT_EVALUATED",
        }
        if response_format is not None:
            metrics["requested_response_format"] = response_format
        if response_error:
            raise ProviderResponseError(response_error, body, metrics)
        return body, metrics

    def generate(self, messages, model_spec, native_effort="none", max_tokens=1024, tools=None,
                 stream=False, *, response_format=None) -> GeneratorResponse:
        body, metrics = self.query_raw(messages, model_spec, native_effort, max_tokens, tools, stream,
                                       response_format=response_format)
        if metrics["protocol"] == "responses":
            content = "".join(part.get("text", "") for item in body["output"]
                              if item["type"] == "message" for part in item["content"])
            calls = [item for item in body["output"] if item["type"] == "function_call"]
            return self._generation(content, calls, body, metrics)
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




class OpenAIResponsesProvider(OpenAICompatibleProvider):
    """Native Responses protocol selected by ModelSpec.protocol."""

    protocol = "responses"


OpenAIChatCompletionsProvider = OpenAICompatibleProvider


