"""Load capability snapshots and serialize shared model and exact effort data."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from modelrouter.providers.registry import ModelRegistry, V9_MODEL_IDS

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "v9" / "capabilities"


def load_current(path: str | Path = DEFAULT_DATA_DIR) -> dict:
    """Read a local capability directory or current.json pointer without network access."""
    path = Path(path)
    index_path = path if path.name == "current.json" else path / "current.json"
    if not index_path.exists():
        return {}
    index = json.loads(index_path.read_text(encoding="utf-8"))
    snapshot = json.loads((index_path.parent / index["snapshot_file"]).read_text(encoding="utf-8"))
    return snapshot


def candidate_action(action) -> dict:
    if isinstance(action, str):
        model, separator, effort = action.rpartition(":")
        if not separator or effort not in ("none", "minimal", "low", "medium", "high", "xhigh", "max"):
            model, effort = action, None
        action = {"model_id": model, "native_effort": effort, "action_id": action}
    else:
        action = dict(action) if isinstance(action, Mapping) else action.model_dump()
    model = action.get("model_id") or action.get("model")
    if action.get("model_id") and action.get("model") and action["model_id"] != action["model"]:
        raise ValueError("Candidate model identities differ")
    effort = action.get("native_effort")
    if not isinstance(model, str) or not model or (effort is not None and not isinstance(effort, str)):
        raise ValueError("Candidate model/effort identity is invalid")
    action_id = f"{model}:{effort}" if effort is not None else model
    if action.get("action_id") not in (None, action_id):
        raise ValueError("Candidate action identity differs from model and effort")
    return {**action, "model_id": model, "native_effort": effort, "action_id": action_id}


def capability_cards(snapshot: dict, legal_actions: list) -> list[dict]:
    registry, cards = ModelRegistry(), []
    for supplied in legal_actions:
        action = candidate_action(supplied)
        model_id, effort = action["model_id"], action["native_effort"]
        model = snapshot.get("models", {}).get(model_id, {})
        evaluation = model.get("evaluations", {}).get(effort, {})
        spec = registry.get_spec(model_id) if model_id in V9_MODEL_IDS else None
        pricing = ({"input": spec.input_price_per_1m, "output": spec.output_price_per_1m,
                    "reasoning": spec.reasoning_price_per_1m, "cache_read": spec.cache_read_price_per_1m,
                    "cache_write": spec.cache_write_price_per_1m, "unit": "USD_PER_MILLION_TOKENS",
                    "status": spec.pricing_status, "as_of": spec.pricing_as_of, "source": spec.pricing_source}
                   if spec else deepcopy(model.get("pricing", {})))
        context = ({"context_window": spec.context_window, "max_output_tokens": spec.max_output_tokens,
                    "status": spec.context_status} if spec else deepcopy(model.get("context_limits", {})))
        metadata = {
            "provider": spec.provider if spec else model.get("provider"),
            "native_efforts": list(spec.native_efforts or ("none",)) if spec else [],
            "tool_supported": spec.tool_supported if spec else None,
            "input_modalities": getattr(spec, "input_modalities", "NOT_MEASURED") if spec else "NOT_MEASURED",
            "output_modalities": getattr(spec, "output_modalities", "NOT_MEASURED") if spec else "NOT_MEASURED",
            "pricing": pricing,
            "context_limits": context,
            "aa_provider": model.get("aa_provider"),
        }
        if spec and spec.tool_supported is None:
            metadata["tool_supported"] = "NOT_MEASURED"
        cards.append({
            "model_id": model_id, "native_effort": effort, "action_id": action["action_id"],
            "evaluation_identity": evaluation.get("evaluation_identity", f"NOT_MEASURED:{model_id}:{effort}"),
            "evaluation_status": evaluation.get("evaluation_status", "NOT_MEASURED"),
            "freshness_status": evaluation.get("freshness_status", model.get("freshness_status", "NOT_MEASURED")),
            "other_effort_reference": evaluation.get("other_effort_reference"),
            "snapshot_id": snapshot.get("snapshot_id"),
            "aa_model_id": evaluation.get("aa_model_id", model.get("aa_model_id")),
            "aa_model_slug": evaluation.get("aa_model_slug", model.get("aa_model_slug")),
            "aa_model_name": evaluation.get("aa_model_name", model.get("aa_model_name")),
            "aa_fetched_at": evaluation.get("aa_fetched_at", model.get("aa_fetched_at")),
            "aa_index_version": evaluation.get("aa_index_version", model.get("aa_index_version", "NOT_REPORTED")),
            "source_url": evaluation.get("source_url", model.get("source_url")),
            "publication_at": evaluation.get("publication_at", model.get("publication_at", "NOT_REPORTED")),
            "model_revision": evaluation.get("model_revision", model.get("model_revision", "NOT_REPORTED")),
            "model_evidence_status": model.get("evidence_status", "NOT_MEASURED"),
            "model_metrics": deepcopy(model.get("model_metrics", [])),
            "metrics": deepcopy(evaluation.get("metrics", [])),
            "missing_metrics": deepcopy(evaluation.get("missing_metrics", [])),
            "stale_metrics": deepcopy(evaluation.get("stale_metrics", [])),
            "model_pricing": deepcopy(pricing), "model_provider": metadata["provider"],
            "model_context_limits": deepcopy(context),
            "model_provider_metadata": metadata,
        })
        if "requested_native_effort" in action:
            cards[-1]["requested_native_effort"] = action["requested_native_effort"]
    return cards
