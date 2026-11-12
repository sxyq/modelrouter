"""Shared token-budget accounting for real Provider requests."""
from __future__ import annotations

import fcntl
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional


def _pilot_file(name: str) -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "experiments" / "agent_pilot" / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Existing experiments/agent_pilot/{name} not found")


@contextmanager
def _token_budget():
    with _pilot_file("token_budget.json").open("r+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        data = json.load(handle)
        try:
            yield data
        finally:
            handle.seek(0)
            json.dump(data, handle, indent=2)
            handle.truncate()
            handle.flush()
            os.fsync(handle.fileno())
            fcntl.flock(handle, fcntl.LOCK_UN)


def _record_budget(data: Dict[str, Any], prompt_tokens: Optional[int], completion_tokens: Optional[int],
                   unknown_token_bound: int = 0) -> None:
    data["total_calls"] = data.get("total_calls", 0) + 1
    if prompt_tokens is None or completion_tokens is None:
        data["unknown_usage_calls"] = data.get("unknown_usage_calls", 0) + 1
        data["reserved_unknown_tokens"] = data.get("reserved_unknown_tokens", 0) + unknown_token_bound
    else:
        data["consumed_prompt_tokens"] = data.get("consumed_prompt_tokens", 0) + prompt_tokens
        data["consumed_completion_tokens"] = data.get("consumed_completion_tokens", 0) + completion_tokens
        data["consumed_total_tokens"] = data.get("consumed_total_tokens", 0) + prompt_tokens + completion_tokens
    data["max_tokens"] = data["remaining_tokens"] = None
    data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def update_token_budget(prompt_tokens: int, completion_tokens: int) -> None:
    with _token_budget() as data:
        _record_budget(data, prompt_tokens, completion_tokens)


def request_decision_id(record):
    """Resolve the recorded request boundary, including saved teacher records."""
    return record.get("decision_id") or record.get("for_decision_id") or record.get("request_id")


def known_request_cost(record):
    """Read known charges, retaining a partially priced account-switch request."""
    if record.get("cost_usd") is not None:
        return record["cost_usd"]
    if record.get("known_model_rate_cost_usd") is not None:
        return record["known_model_rate_cost_usd"]
    known = [attempt["cost_usd"] for attempt in record.get("account_attempts", [])
             if attempt.get("cost_usd") is not None]
    return sum(known) if known else None


def known_request_tokens(record, field):
    value = record.get(field)
    if value is not None:
        return value
    return sum(a[field] for a in record.get("account_attempts", []) if a.get(field) is not None)
