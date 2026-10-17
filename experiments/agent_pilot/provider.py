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


class OpenAICompatibleProvider(BaseGeneratorProvider):
    """Production provider calling OpenAI-compatible API endpoint (activated tomorrow morning)."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def generate(
        self,
        messages: List[Dict[str, str]],
        model_spec: ModelSpec,
        native_effort: str = "none",
        max_tokens: int = 1024,
    ) -> GeneratorResponse:
        t0 = time.time()
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": model_spec.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if native_effort != "none" and native_effort in model_spec.native_efforts:
            payload["reasoning_effort"] = native_effort

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            body = json.loads(resp.read().decode("utf-8"))

        choice = body["choices"][0]
        content = choice["message"]["content"]
        thought, action, is_finish = parse_react_response(content)

        usage = body.get("usage", {})
        p_tokens = usage.get("prompt_tokens", 0)
        c_tokens = usage.get("completion_tokens", 0)
        r_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
        cached = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)

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
