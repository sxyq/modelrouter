"""
Multi-Model Logging and Cost Auditing Module.
Provides standardized, future-proof logging for any LLM API call across
both ChatCompletions and Responses protocols, recording fine-grained tokens,
TTFT, native reasoning effort, tools invoked, reference cost (OpenRouter),
and actual billed cost.
"""

import os
import sys
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from modelrouter.telemetry.ledger import _find_project_root

try:
    from modelrouter.providers.pricing.fetch_openrouter import calculate_reference_cost
except ImportError:
    try:
        from experiments.agent_pilot.pricing.fetch_openrouter import calculate_reference_cost
    except ImportError:
        from .pricing.fetch_openrouter import calculate_reference_cost


DEFAULT_LOG_PATH = os.path.join(_find_project_root(), "runs", "agent_pilot", "multi_model_calls.jsonl")


class MultiModelLogger:
    """Thread-safe append-only logger for multi-model LLM invocations."""

    def __init__(self, log_path: str = DEFAULT_LOG_PATH):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_call(
        self,
        protocol: str,
        model_id: str,
        provider: str = "custom",
        reasoning_effort: str = "none",
        stream: bool = False,
        ttft_ms: Optional[float] = None,
        total_latency_ms: float = 0.0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        reasoning_tokens: int = 0,
        cache_read_tokens: int = 0,
        actual_billed_cost_usd: Optional[float] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Records a single LLM invocation event.
        Uses recorded Provider rates; other callers retain the existing reference price.
        """
        if metadata and metadata.get("cost_basis") in (
            "SELECTED_MODEL_RATES_WITH_BACKEND_USAGE", "REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE"
        ):
            ref_cost, ref_status = metadata["cost_usd"], metadata["cost_status"]
        else:
            ref_cost, ref_status = calculate_reference_cost(
                model_id=model_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cache_read_tokens=cache_read_tokens,
            )

        record = {
            "call_id": f"call_{uuid.uuid4().hex[:12]}",
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "protocol": protocol,  # "chat_completions" | "responses"
            "model_id": model_id,
            "provider": provider,
            "reasoning_effort": reasoning_effort,
            "stream": stream,
            "latency": {
                "ttft_ms": round(ttft_ms, 2) if ttft_ms is not None else None,
                "total_latency_ms": round(total_latency_ms, 2),
            },
            "tokens": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "reasoning_tokens": reasoning_tokens,
                "cache_read_tokens": metadata.get("cached_tokens", cache_read_tokens) if metadata else cache_read_tokens,
                "cache_write_tokens": metadata.get("cache_write_tokens") if metadata else None,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "cost": {
                "reference_cost_usd": ref_cost,
                "reference_pricing_status": ref_status,
                "actual_billed_cost_usd": (
                    round(actual_billed_cost_usd, 8) if actual_billed_cost_usd is not None else None
                ),
            },
            "tool_calls": tool_calls or [],
            "status": status,
            "error_message": error_message,
            "metadata": metadata or {},
        }

        # Thread-safe append
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return record

    def get_summary(self) -> Dict[str, Any]:
        """Aggregates log file statistics by model and protocol."""
        if not os.path.exists(self.log_path):
            return {"total_calls": 0, "models": {}, "protocols": {}}

        total_calls = 0
        total_tokens = 0
        total_ref_cost = 0.0
        total_billed_cost = 0.0
        by_model: Dict[str, Dict[str, Any]] = {}
        by_protocol: Dict[str, int] = {}

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue

                total_calls += 1
                proto = rec.get("protocol", "unknown")
                by_protocol[proto] = by_protocol.get(proto, 0) + 1

                m_id = rec.get("model_id", "unknown")
                if m_id not in by_model:
                    by_model[m_id] = {
                        "calls": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "reasoning_tokens": 0,
                        "ref_cost_usd": 0.0,
                        "billed_cost_usd": 0.0,
                    }

                toks = rec.get("tokens", {})
                p_tok = toks.get("prompt_tokens", 0)
                c_tok = toks.get("completion_tokens", 0)
                r_tok = toks.get("reasoning_tokens", 0)
                total_tokens += p_tok + c_tok

                by_model[m_id]["calls"] += 1
                by_model[m_id]["prompt_tokens"] += p_tok
                by_model[m_id]["completion_tokens"] += c_tok
                by_model[m_id]["reasoning_tokens"] += r_tok

                cost = rec.get("cost", {})
                rc = cost.get("reference_cost_usd")
                if isinstance(rc, (int, float)):
                    by_model[m_id]["ref_cost_usd"] += rc
                    total_ref_cost += rc

                bc = cost.get("actual_billed_cost_usd")
                if isinstance(bc, (int, float)):
                    by_model[m_id]["billed_cost_usd"] += bc
                    total_billed_cost += bc

        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_reference_cost_usd": round(total_ref_cost, 6),
            "total_billed_cost_usd": round(total_billed_cost, 6),
            "protocols": by_protocol,
            "models": by_model,
        }


# Global singleton instance
global_multi_model_logger = MultiModelLogger()
