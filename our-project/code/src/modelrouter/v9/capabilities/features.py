"""Load local capability evidence and make cards for the supplied legal actions."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from .normalize import INDEX_METRICS, MODEL_IDS, missing_metric


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "v9" / "capabilities"


def _evidence_summary(models: dict) -> dict:
    measured = [(model_id, metric) for model_id, model in models.items()
                for metric in model.get("metrics", [])
                if metric.get("evidence_status") == "MEASURED" and metric.get("score_raw") is not None]
    covered = {(model_id, metric["metric_name"]) for model_id, metric in measured}
    complete = all((model_id, name) in covered for model_id in MODEL_IDS for name in INDEX_METRICS)
    return {
        "capability_evidence_status": "NOT_MEASURED" if not measured else "MEASURED" if complete else "PARTIAL",
        "measured_metric_count": len(measured),
        "provider_metadata_model_count": sum(bool(model.get("provider_metadata")) for model in models.values()),
    }


def load_current(path: str | Path = DEFAULT_DATA_DIR) -> dict:
    """Read a capability directory or its current.json index; no network access."""
    path = Path(path)
    index_path = path if path.name == "current.json" else path / "current.json"
    if not index_path.exists():
        return {}
    index = json.loads(index_path.read_text(encoding="utf-8"))
    snapshot = json.loads((index_path.parent / index["snapshot_file"]).read_text(encoding="utf-8"))
    snapshot.update(_evidence_summary(snapshot.get("models", {})))
    return snapshot


def candidate_action(action) -> dict:
    """Accept saved model IDs, model/effort IDs and serving action objects unchanged."""
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
    if not isinstance(model, str) or not model:
        raise ValueError("Candidate model identity is missing")
    effort = action.get("native_effort")
    if effort is not None and (not isinstance(effort, str) or not effort):
        raise ValueError("Candidate effort must be a string or unreported")
    action_id = f"{model}:{effort}" if effort is not None else model
    if action.get("action_id") not in (None, action_id):
        raise ValueError("Candidate action identity differs from model and effort")
    return {**action, "model_id": model, "native_effort": effort, "action_id": action_id}


def capability_cards(snapshot: dict, legal_actions: list) -> list[dict]:
    """Keep model-level evidence separate from measured model/effort evidence."""
    cards = []
    for action in legal_actions:
        action = candidate_action(action)
        model_id = action["model_id"]
        effort = action["native_effort"]
        model = snapshot.get("models", {}).get(model_id, {})
        model_status = model.get("evidence_status", "NOT_MEASURED")
        metadata = model.get("provider_metadata", {})
        evidence = model.get("metrics", [])
        names = list(dict.fromkeys([*INDEX_METRICS, *(item["metric_name"] for item in evidence)]))
        action_metrics = []
        for name in names:
            measured = [item for item in evidence if item["metric_name"] == name
                        and effort is not None and item["score_scope"] == "effort"
                        and item["evaluated_native_effort"] == effort
                        and item["evidence_status"] == "MEASURED"]
            if measured:
                action_metrics.extend(deepcopy(measured))
            else:
                missing = missing_metric(name, model.get("source_url", ""),
                    "MODEL_NOT_FOUND" if model_status == "MODEL_NOT_FOUND" else
                    "EFFORT_NOT_REPORTED" if effort is None else
                    "EFFORT_NOT_MEASURED" if model else
                    "MODEL_NOT_IN_CAPABILITY_SET" if snapshot else "SNAPSHOT_NOT_AVAILABLE")
                missing["score_scope"] = "effort"
                action_metrics.append(missing)
        cards.append({
            "model_id": model_id,
            "native_effort": effort,
            "action_id": action["action_id"],
            "snapshot_id": snapshot.get("snapshot_id"),
            "source_url": model.get("source_url"),
            "fetched_at_utc": model.get("fetched_at_utc"),
            "model_revision": model.get("model_revision", "NOT_REPORTED"),
            "model_evidence_status": model_status,
            "evidence_status": "MEASURED" if any(
                item["evidence_status"] == "MEASURED" for item in action_metrics
            ) else "NOT_MEASURED",
            "model_metrics": deepcopy([item for item in evidence if item["score_scope"] == "model"]),
            "reference_metrics": deepcopy([item for item in evidence if item["score_scope"] == "effort"
                and item.get("evidence_status") == "MEASURED"
                and item.get("evaluated_native_effort") != effort]),
            "action_metrics": action_metrics,
            "model_pricing": deepcopy(metadata.get("pricing", model.get("pricing", {}))),
            "model_provider": metadata.get("provider", model.get("provider")),
            "model_context_limits": deepcopy(metadata.get("context_limits", model.get("context_limits", {}))),
            "model_provider_metadata": deepcopy(metadata),
        })
    return cards
