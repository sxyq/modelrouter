"""Model and Capability Registry for Agent Pilot.

Defines the 5 major model pools, pricing matrices, and native effort capabilities:
- Fast: Lightweight, fast, low cost (e.g., gpt-4o-mini, claude-3-haiku, deepseek-chat, llama-3.1-8b)
- Standard: Balanced cost and performance (e.g., gpt-4o, claude-3-5-sonnet, deepseek-v2.5, qwen-2.5-72b)
- Strong: Flagship general reasoning (e.g., gpt-4o-2024-08-06, claude-3-opus, deepseek-v3)
- Reasoning: Test-time compute models with native effort control (e.g., o1-mini, o1, o3-mini, deepseek-r1)
- Vision: Multimodal visual inspection & execution

Follows V8 §7.3 & §7.5 standards:
- Pricing in USD per 1M tokens.
- Native efforts separated from model names.
- Reasoning tokens explicitly tracked.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    pool: str  # Fast, Standard, Strong, Reasoning, Vision
    provider: str
    display_name: str
    context_window: Optional[int]
    max_output_tokens: Optional[int]
    native_efforts: Tuple[str, ...]  # e.g., ("none",) or ("low", "medium", "high")
    input_price_per_1m: Optional[float]
    output_price_per_1m: Optional[float]
    reasoning_price_per_1m: Optional[float]
    cache_read_price_per_1m: Optional[float] = 0.0
    cache_write_price_per_1m: Optional[float] = 0.0
    rpm_limit: Optional[int] = 500
    tpm_limit: Optional[int] = 200_000
    tool_supported: Optional[bool] = True
    pricing_status: str = "UNVERIFIED_CONFIG"
    pricing_source: Optional[str] = None
    identity_status: str = "UNVERIFIED_CONFIG"
    context_status: str = "UNVERIFIED_CONFIG"
    native_efforts_status: str = "UNVERIFIED_CONFIG"

    def calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        reasoning_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> Optional[float]:
        """Calculate configured USD; completion includes its reasoning subset."""
        net_prompt_tokens = max(0, prompt_tokens - cache_read_tokens - cache_write_tokens)
        visible_completion_tokens = completion_tokens - reasoning_tokens
        if visible_completion_tokens < 0:
            raise ValueError("reasoning_tokens must be a subset of completion_tokens")
        charges = (
            (net_prompt_tokens, self.input_price_per_1m),
            (visible_completion_tokens, self.output_price_per_1m),
            (reasoning_tokens, self.reasoning_price_per_1m),
            (cache_read_tokens, self.cache_read_price_per_1m),
            (cache_write_tokens, self.cache_write_price_per_1m),
        )
        if any(tokens and price is None for tokens, price in charges):
            return None
        cost = sum(tokens * price for tokens, price in charges if tokens) / 1_000_000
        return round(cost, 10)

    def validate_effort(self, native_effort: str) -> None:
        # Unknown support permits omission, without asserting a measured level.
        if not self.native_efforts and self.native_efforts_status == "NOT_MEASURED" and native_effort == "none":
            return
        if native_effort not in self.native_efforts:
            raise ValueError(f"Unsupported native_effort {native_effort!r} for {self.model_id}")


V9_MODEL_IDS = ("gpt-6.1-sol", "gpt-6-luna", "qwen3.8-flash")


# 5 Major Model Pools
MODEL_REGISTRY: Dict[str, ModelSpec] = {
    # 1. Fast Pool
    "gpt-4o-mini": ModelSpec(
        model_id="gpt-4o-mini",
        pool="Fast",
        provider="openai",
        display_name="GPT-4o Mini",
        context_window=128_000,
        max_output_tokens=16_384,
        native_efforts=("none",),
        input_price_per_1m=0.15,
        output_price_per_1m=0.60,
        reasoning_price_per_1m=0.0,
        cache_read_price_per_1m=0.075,
    ),
    "deepseek-chat": ModelSpec(
        model_id="deepseek-chat",
        pool="Fast",
        provider="deepseek",
        display_name="DeepSeek V3 Chat",
        context_window=64_000,
        max_output_tokens=8_192,
        native_efforts=("none",),
        input_price_per_1m=0.14,
        output_price_per_1m=0.28,
        reasoning_price_per_1m=0.0,
        cache_read_price_per_1m=0.014,
    ),
    "claude-3-haiku": ModelSpec(
        model_id="claude-3-haiku",
        pool="Fast",
        provider="anthropic",
        display_name="Claude 3 Haiku",
        context_window=200_000,
        max_output_tokens=4_096,
        native_efforts=("none",),
        input_price_per_1m=0.25,
        output_price_per_1m=1.25,
        reasoning_price_per_1m=0.0,
    ),
    # 2. Standard Pool
    "gpt-4o": ModelSpec(
        model_id="gpt-4o",
        pool="Standard",
        provider="openai",
        display_name="GPT-4o Standard",
        context_window=128_000,
        max_output_tokens=16_384,
        native_efforts=("none",),
        input_price_per_1m=2.50,
        output_price_per_1m=10.00,
        reasoning_price_per_1m=0.0,
        cache_read_price_per_1m=1.25,
    ),
    "claude-3-5-sonnet": ModelSpec(
        model_id="claude-3-5-sonnet",
        pool="Standard",
        provider="anthropic",
        display_name="Claude 3.5 Sonnet",
        context_window=200_000,
        max_output_tokens=8_192,
        native_efforts=("none",),
        input_price_per_1m=3.00,
        output_price_per_1m=15.00,
        reasoning_price_per_1m=0.0,
    ),
    "qwen-2.5-72b": ModelSpec(
        model_id="qwen-2.5-72b",
        pool="Standard",
        provider="aliyun",
        display_name="Qwen 2.5 72B Instruct",
        context_window=128_000,
        max_output_tokens=8_192,
        native_efforts=("none",),
        input_price_per_1m=0.50,
        output_price_per_1m=2.00,
        reasoning_price_per_1m=0.0,
    ),
    # 3. Strong Pool
    "gpt-4o-2024-08-06": ModelSpec(
        model_id="gpt-4o-2024-08-06",
        pool="Strong",
        provider="openai",
        display_name="GPT-4o Flagship (08-06)",
        context_window=128_000,
        max_output_tokens=16_384,
        native_efforts=("none",),
        input_price_per_1m=2.50,
        output_price_per_1m=10.00,
        reasoning_price_per_1m=0.0,
    ),
    "claude-3-opus": ModelSpec(
        model_id="claude-3-opus",
        pool="Strong",
        provider="anthropic",
        display_name="Claude 3 Opus",
        context_window=200_000,
        max_output_tokens=4_096,
        native_efforts=("none",),
        input_price_per_1m=15.00,
        output_price_per_1m=75.00,
        reasoning_price_per_1m=0.0,
    ),
    # 4. Reasoning Pool
    "o1-mini": ModelSpec(
        model_id="o1-mini",
        pool="Reasoning",
        provider="openai",
        display_name="OpenAI o1 Mini",
        context_window=128_000,
        max_output_tokens=65_536,
        native_efforts=("low", "medium", "high"),
        input_price_per_1m=1.10,
        output_price_per_1m=4.40,
        reasoning_price_per_1m=4.40,
    ),
    "o1": ModelSpec(
        model_id="o1",
        pool="Reasoning",
        provider="openai",
        display_name="OpenAI o1 Flagship",
        context_window=200_000,
        max_output_tokens=100_000,
        native_efforts=("low", "medium", "high"),
        input_price_per_1m=15.00,
        output_price_per_1m=60.00,
        reasoning_price_per_1m=60.00,
    ),
    "deepseek-r1": ModelSpec(
        model_id="deepseek-r1",
        pool="Reasoning",
        provider="deepseek",
        display_name="DeepSeek R1",
        context_window=64_000,
        max_output_tokens=8_192,
        native_efforts=("medium", "high"),
        input_price_per_1m=0.55,
        output_price_per_1m=2.19,
        reasoning_price_per_1m=2.19,
    ),
    # 5. Vision Pool
    "gpt-4o-vision": ModelSpec(
        model_id="gpt-4o-vision",
        pool="Vision",
        provider="openai",
        display_name="GPT-4o Vision",
        context_window=128_000,
        max_output_tokens=16_384,
        native_efforts=("none",),
        input_price_per_1m=2.50,
        output_price_per_1m=10.00,
        reasoning_price_per_1m=0.0,
    ),
    # 6. Luna Generators (V8 Live Execution)
    "gpt-6-luna": ModelSpec(
        model_id="gpt-6-luna",
        pool="Reasoning",
        provider="jiji",
        display_name="GPT 6 Luna",
        context_window=200_000,
        max_output_tokens=65_536,
        native_efforts=("none", "low", "medium", "high"),
        # Official Standard rates, <=272K input, 30m cache writes:
        # https://developers.openai.com/api/docs/models/gpt-6-luna
        input_price_per_1m=0.10,
        output_price_per_1m=0.50,
        reasoning_price_per_1m=0.50,
        cache_read_price_per_1m=0.01,
        cache_write_price_per_1m=0.125,
        pricing_status="VERIFIED_OFFICIAL_STANDARD_SHORT_CONTEXT",
        pricing_source="https://developers.openai.com/api/docs/models/gpt-6-luna",
    ),
    "gpt-5.6-luna": ModelSpec(
        model_id="gpt-5.6-luna",
        pool="Reasoning",
        provider="jiji",
        display_name="GPT 5.6 Luna",
        context_window=128_000,
        max_output_tokens=32_768,
        native_efforts=("none", "low", "medium", "high"),
        input_price_per_1m=1.00,
        output_price_per_1m=4.00,
        reasoning_price_per_1m=4.00,
        cache_read_price_per_1m=0.25,
    ),
    "gpt-6.1-sol": ModelSpec(
        model_id="gpt-6.1-sol", pool="Reasoning", provider="openai",
        display_name="GPT 6.1 Sol", context_window=None, max_output_tokens=None,
        native_efforts=(), input_price_per_1m=2.0, output_price_per_1m=10.0,
        reasoning_price_per_1m=10.0, cache_read_price_per_1m=0.1,
        cache_write_price_per_1m=2.5, rpm_limit=None, tpm_limit=None,
        tool_supported=None, pricing_status="VERIFIED_OFFICIAL_STANDARD_SHORT_CONTEXT",
        pricing_source="https://developers.openai.com/api/docs/models/gpt-6.1-sol.md",
        identity_status="NOT_MEASURED", context_status="NOT_MEASURED",
        native_efforts_status="NOT_MEASURED",
    ),
    "qwen3.8-flash": ModelSpec(
        model_id="qwen3.8-flash", pool="Fast", provider="aliyun",
        display_name="Qwen 3.8 Flash", context_window=None, max_output_tokens=None,
        native_efforts=(), input_price_per_1m=0.15, output_price_per_1m=0.47,
        reasoning_price_per_1m=0.47, cache_read_price_per_1m=0.016,
        cache_write_price_per_1m=None, rpm_limit=None, tpm_limit=None,
        tool_supported=None, pricing_status="OPENROUTER_PUBLISHED_USD_REFERENCE",
        pricing_source="https://openrouter.ai/api/v1/models",
        identity_status="NOT_MEASURED", context_status="NOT_MEASURED",
        native_efforts_status="NOT_MEASURED",
    ),
}


class ModelRegistry:
    """Manages legal model actions and cost evaluation."""

    def __init__(self, models: Optional[Dict[str, ModelSpec]] = None):
        self._models = models or MODEL_REGISTRY

    def get_spec(self, model_id: str) -> ModelSpec:
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found in registry.")
        return self._models[model_id]

    def list_models_by_pool(self, pool_name: str) -> List[ModelSpec]:
        return [m for m in self._models.values() if m.pool.lower() == pool_name.lower()]

    def list_legal_actions(self, allowed_pools: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Returns all legal (model, native_effort) pairs for the given pools.
        
        Unknown effort support exposes parameter omission with its evidence status.
        """
        actions = []
        for model in self._models.values():
            if allowed_pools and model.pool.lower() not in [p.lower() for p in allowed_pools]:
                continue
            efforts = model.native_efforts or ("none",)
            for effort in efforts:
                action = {
                    "provider": model.provider,
                    "model": model.model_id,
                    "pool": model.pool,
                    "native_effort": effort,
                    "action_id": f"{model.model_id}:{effort}",
                }
                if not model.native_efforts:
                    action["native_efforts_status"] = model.native_efforts_status
                actions.append(action)
        return actions

    def compute_cost(
        self,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        reasoning_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> Optional[float]:
        spec = self.get_spec(model_id)
        return spec.calculate_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            cache_read_tokens=cache_read_tokens,
            cache_write_tokens=cache_write_tokens,
        )

    def get_pricing_sha256(self) -> str:
        """Returns a deterministic SHA256 of the active pricing table."""
        records = [
            f"{m.model_id}:{m.input_price_per_1m}:{m.output_price_per_1m}:{m.reasoning_price_per_1m}"
            for m in sorted(self._models.values(), key=lambda x: x.model_id)
        ]
        return hashlib.sha256(";".join(records).encode("utf-8")).hexdigest()[:16]
