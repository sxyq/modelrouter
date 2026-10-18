"""Generator Provider Abstraction for Single Agent Loop.

Supports:
- BaseGeneratorProvider: Abstract contract
- MockGeneratorProvider: Zero-cost realistic ReAct generator for offline stress testing
- OracleGeneratorProvider: Perfect execution for pipeline verification
- OpenAICompatibleProvider: Ready for production API key activation tomorrow morning
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from experiments.agent_pilot.registry import ModelSpec

logger = logging.getLogger("experiments.agent_pilot.provider")


@dataclass
class GeneratorResponse:
    content: str
    thought: str
    action: str
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int
    cached_tokens: int
    latency_ms: float
    cost_usd: float
    is_finish: bool

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
            "cost_usd": self.cost_usd,
            "is_finish": self.is_finish,
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


def load_generator_credentials() -> Dict[str, Any]:
    """Load secrets only from an external, owner-readable config (or environment).

    Never load secrets from a path inside the Git working tree. Rotate any
    credential previously committed to Git; deleting the tracked file does
    not invalidate a credential already exposed in repository history.
    """
    from pathlib import Path

    external_path = os.environ.get("MODELROUTER_CREDENTIALS_FILE", "").strip()
    cfg_path = (
        Path(external_path).expanduser()
        if external_path
        else Path.home() / ".config" / "modelrouter" / "generator_credentials.json"
    )
    try:
        if not cfg_path.is_file():
            return {}
        if os.name == "posix" and (cfg_path.stat().st_mode & 0o077):
            logger.error("Credentials file permissions are too open; require chmod 600.")
            return {}
        with cfg_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("Unable to load external generator credentials: %s", type(e).__name__)
        return {}


def update_token_budget(prompt_tokens: int, completion_tokens: int) -> None:
    """Safely updates global token budget tracker."""
    budget_file = os.path.join(os.path.dirname(__file__), "token_budget.json")
    total_new = prompt_tokens + completion_tokens
    budget_data = {
        "max_tokens": 1000000,
        "consumed_prompt_tokens": 0,
        "consumed_completion_tokens": 0,
        "consumed_total_tokens": 0,
        "remaining_tokens": 1000000,
        "total_calls": 0,
    }
    if os.path.exists(budget_file):
        try:
            with open(budget_file, "r", encoding="utf-8") as f:
                budget_data.update(json.load(f))
        except Exception:
            pass

    consumed = budget_data.get("consumed_total_tokens", 0) + total_new
    if consumed >= budget_data.get("max_tokens", 1000000):
        logger.error("Token budget exceeded: %d >= %d", consumed, budget_data.get("max_tokens", 1000000))

    budget_data["consumed_prompt_tokens"] = budget_data.get("consumed_prompt_tokens", 0) + prompt_tokens
    budget_data["consumed_completion_tokens"] = budget_data.get("consumed_completion_tokens", 0) + completion_tokens
    budget_data["consumed_total_tokens"] = consumed
    budget_data["remaining_tokens"] = max(0, budget_data.get("max_tokens", 1000000) - consumed)
    budget_data["total_calls"] = budget_data.get("total_calls", 0) + 1
    budget_data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    try:
        with open(budget_file, "w", encoding="utf-8") as f:
            json.dump(budget_data, f, indent=2)
    except Exception as e:
        logger.warning("Failed to persist token_budget.json: %s", e)


class OpenAICompatibleProvider(BaseGeneratorProvider):
    """Production provider calling OpenAI-compatible Chat Completions API endpoint."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        creds = load_generator_credentials()
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or creds.get("api_key", "")
        self.primary_model = creds.get("primary_model", "gpt-6-luna")
        self.fallback_model = creds.get("fallback_model", "gpt-5.6-luna")
        self.allowed_models = set(creds.get("allowed_models", ["gpt-6-luna", "gpt-5.6-luna"]))

    def _normalize_model(self, model_id: str) -> str:
        m = model_id.lower().replace(" ", "-")
        if m in ("gpt-6-luna", "gpt-6", "luna"):
            return "gpt-6-luna"
        if m in ("gpt-5.6-luna", "gpt-5.6"):
            return "gpt-5.6-luna"
        if m in self.allowed_models:
            return m
        return self.primary_model

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        t0 = time.time()
        url = f"{self.base_url}/chat/completions"
        target_model = self._normalize_model(model_spec.model_id)

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if native_effort != "none" and native_effort in model_spec.native_efforts:
            payload["reasoning_effort"] = native_effort

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ModelRouter/1.0",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60.0) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # Fallback to fallback_model if primary fails
            if target_model != self.fallback_model and self.fallback_model:
                logger.warning("Primary model %s failed (%s), attempting fallback %s", target_model, e, self.fallback_model)
                payload["model"] = self.fallback_model
                data = json.dumps(payload).encode("utf-8")
                req2 = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req2, timeout=60.0) as resp2:
                    body = json.loads(resp2.read().decode("utf-8"))
            else:
                raise

        choice = body["choices"][0]
        content = choice["message"]["content"]
        thought, action, is_finish = parse_react_response(content)

        usage = body.get("usage", {})
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)
        r_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
        cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)

        update_token_budget(p_tokens, c_tokens)

        cost = model_spec.calculate_cost(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            reasoning_tokens=r_tokens,
            cache_read_tokens=cached,
        )

        return GeneratorResponse(
            content=content,
            thought=thought,
            action=action,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            reasoning_tokens=r_tokens,
            cached_tokens=cached,
            latency_ms=(time.time() - t0) * 1000,
            cost_usd=cost,
            is_finish=is_finish,
        )


class OpenAIResponsesProvider(BaseGeneratorProvider):
    """Production provider calling OpenAI /v1/responses endpoint."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        creds = load_generator_credentials()
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL") or creds.get("base_url") or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or creds.get("api_key", "")
        self.primary_model = creds.get("primary_model", "gpt-6-luna")
        self.fallback_model = creds.get("fallback_model", "gpt-5.6-luna")
        self.allowed_models = set(creds.get("allowed_models", ["gpt-6-luna", "gpt-5.6-luna"]))

    def _normalize_model(self, model_id: str) -> str:
        m = model_id.lower().replace(" ", "-")
        if m in ("gpt-6-luna", "gpt-6", "luna"):
            return "gpt-6-luna"
        if m in ("gpt-5.6-luna", "gpt-5.6"):
            return "gpt-5.6-luna"
        if m in self.allowed_models:
            return m
        return self.primary_model

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        t0 = time.time()
        url = f"{self.base_url}/responses"
        target_model = self._normalize_model(model_spec.model_id)

        # Convert chat messages to responses input
        input_text = ""
        for m in messages:
            input_text += f"{m.get('role', 'user').upper()}: {m.get('content', '')}\n\n"

        payload: Dict[str, Any] = {
            "model": target_model,
            "input": input_text.strip(),
        }
        if native_effort != "none" and native_effort in model_spec.native_efforts:
            payload["reasoning"] = {"effort": native_effort}

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ModelRouter/1.0",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        content = ""
        for item in body.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        content += c.get("text", "")

        thought, action, is_finish = parse_react_response(content)

        usage = body.get("usage", {})
        p_tokens = usage.get("input_tokens", 0)
        c_tokens = usage.get("output_tokens", 0)
        r_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)
        cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)

        update_token_budget(p_tokens, c_tokens)

        cost = model_spec.calculate_cost(
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            reasoning_tokens=r_tokens,
            cache_read_tokens=cached,
        )

        return GeneratorResponse(
            content=content,
            thought=thought,
            action=action,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            reasoning_tokens=r_tokens,
            cached_tokens=cached,
            latency_ms=(time.time() - t0) * 1000,
            cost_usd=cost,
            is_finish=is_finish,
        )


# Alias OpenAIChatCompletionsProvider to OpenAICompatibleProvider
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
