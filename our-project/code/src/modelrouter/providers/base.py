"""Shared generator result and call interface."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .registry import ModelSpec


class ProviderResponseError(RuntimeError):
    def __init__(self, reason, response, metrics):
        super().__init__(reason)
        self.response = response
        self.metrics = metrics


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
    thought = ""
    action = ""
    thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", text, re.DOTALL | re.IGNORECASE)
    if thought_match:
        thought = thought_match.group(1).strip()
    action_match = re.search(r"Action:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
    if action_match:
        action = action_match.group(1).strip().split("\n", 1)[0].strip()
    if not action:
        action, thought = "pwd", text.strip()
    return thought, action, action.upper() in ("FINISH", "AGENT_DONE", "EXIT", "COMPLETED")


class BaseGeneratorProvider:
    def generate(self, messages: List[Dict[str, str]], model_spec: ModelSpec,
                 native_effort: str = "none", max_tokens: int = 1024) -> GeneratorResponse:
        raise NotImplementedError
