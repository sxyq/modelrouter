"""Historical offline providers retained for local pipeline reproduction."""
from __future__ import annotations

import random
import time
from typing import Dict, List

from .base import BaseGeneratorProvider, GeneratorResponse
from .registry import ModelSpec


class MockGeneratorProvider(BaseGeneratorProvider):
    def __init__(self, failure_rate: float = 0.0):
        self.failure_rate = failure_rate

    def generate(self, messages: List[Dict[str, str]], model_spec: ModelSpec,
                 native_effort: str = "none", max_tokens: int = 1024) -> GeneratorResponse:
        t0 = time.time()
        user_msg = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
        step_count = sum(m.get("role") == "assistant" for m in messages)
        if "fix-git" in user_msg.lower():
            plan = [("Checking git branch and log status.", "git status"),
                    ("Switching back to master branch.", "git checkout master"),
                    ("Merging detached commit into master branch.", "git merge e5f6g7h"),
                    ("Master branch is up to date and verified.", "FINISH")]
        elif "count-dataset-tokens" in user_msg.lower():
            plan = [("Checking workspace files.", "ls -la"),
                    ("Running tokenizer token count on dataset.", "python -m count_tokens dataset.jsonl"),
                    ("Token count verified successfully.", "FINISH")]
        else:
            plan = [("Inspecting current workspace and directory layout.", "pwd && ls -la"),
                    ("Running automated tests and environment checks.", "cat Makefile || ls -la"),
                    ("Verifying changes and build outputs.", "echo 'build verified'"),
                    ("All execution requirements satisfied.", "FINISH")]
        thought, action = plan[min(step_count, len(plan) - 1)]
        prompt = random.randint(350, 1200) + step_count * 250
        completion = random.randint(45, 120)
        reasoning = 0
        if native_effort in ("medium", "high") or model_spec.pool == "Reasoning":
            reasoning = random.randint(200, 600) * (2 if native_effort == "high" else 1)
            completion += reasoning
        cached = int(prompt * 0.4) if step_count else 0
        return GeneratorResponse(
            content=f"Thought: {thought}\nAction: {action}", thought=thought, action=action,
            prompt_tokens=prompt, completion_tokens=completion, reasoning_tokens=reasoning,
            cached_tokens=cached, latency_ms=(time.time() - t0) * 1000 + random.uniform(12, 35),
            cost_usd=model_spec.calculate_cost(prompt, completion, reasoning, cached),
            is_finish=action == "FINISH",
        )


class OracleGeneratorProvider(BaseGeneratorProvider):
    def generate(self, messages: List[Dict[str, str]], model_spec: ModelSpec,
                 native_effort: str = "none", max_tokens: int = 1024) -> GeneratorResponse:
        t0 = time.time()
        thought, action = (("Oracle inspecting task.", "pwd") if not any(
            m.get("role") == "assistant" for m in messages) else ("Oracle completing task.", "FINISH"))
        return GeneratorResponse(
            content=f"Thought: {thought}\nAction: {action}", thought=thought, action=action,
            prompt_tokens=250, completion_tokens=40, reasoning_tokens=0, cached_tokens=0,
            latency_ms=(time.time() - t0) * 1000 + 5, cost_usd=0.0, is_finish=action == "FINISH",
        )
