"""Manually refresh AA evidence: python -m modelrouter.v9.capabilities.refresh."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from .features import DEFAULT_DATA_DIR, _evidence_summary, load_current
from .normalize import AA_SLUGS, MODEL_IDS, normalize_catalog, provider_metadata, public_catalog


API_URL = "https://artificialanalysis.ai/api/v2/data/llms/models"
PUBLIC_URL = "https://artificialanalysis.ai/models/{}"
PROVIDER_URLS = {
    "gpt-6.1-sol": "https://developers.openai.com/api/docs/models/gpt-6.1-sol.md",
    "gpt-6-luna": "https://developers.openai.com/api/docs/models/gpt-6-luna.md",
    "qwen3.8-flash": "https://help.aliyun.com/en/model-studio/qwen3-8-flash",
}
DEFAULT_CONFIG = Path(__file__).resolve().parents[6] / "experiments" / "agent_pilot" / "configs" / "generator_credentials.json"


def _safe_headers(headers) -> dict:
    return {name: headers[name] for name in ("Content-Type", "Date", "Last-Modified") if name in headers}


def _api_key(config_path: str | Path | None) -> str | None:
    key = os.environ.get("ARTIFICIAL_ANALYSIS_API_KEY")
    if key:
        return key.strip()
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG
    if not path.exists():
        return None
    config = json.loads(path.read_text(encoding="utf-8"))
    key = config.get("artificial_analysis", {}).get("api_key") or config.get("artificial_analysis_api_key")
    return key.strip() if key else None


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".aa-", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def refresh(data_dir: str | Path = DEFAULT_DATA_DIR, *, config_path: str | Path | None = None,
            timeout: float = 30.0) -> dict:
    """Fetch once per invocation; retain current evidence on source/parse failure."""
    data_dir = Path(data_dir)
    previous = load_current(data_dir)
    timestamp = datetime.now(timezone.utc)
    utc = timestamp.isoformat().replace("+00:00", "Z")
    attempts, models = [], {}
    prior_evidence = _evidence_summary(previous.get("models", {}))
    event = {"fetched_at_utc": utc, "status": "FAILED", "snapshot_id": previous.get("snapshot_id"),
             **prior_evidence}
    source_url, response_info, key = API_URL, {}, None
    try:
        key = _api_key(config_path)
        sources = [("AA_API", None, API_URL)] if key else [
            ("AA_PUBLIC", model_id, PUBLIC_URL.format(slug)) for model_id, slug in AA_SLUGS.items()]
        sources.extend(("PROVIDER_DOCUMENTATION", model_id, url) for model_id, url in PROVIDER_URLS.items())
        if not key:
            attempts.append({"source_url": API_URL, "fetched_at_utc": utc, "status": "API_KEY_MISSING"})
        for source_kind, model_id, source_url in sources:
            response_info = {}
            is_api = source_kind == "AA_API"
            is_provider = source_kind == "PROVIDER_DOCUMENTATION"
            headers = {"User-Agent": "ModelRouter/9", "Cache-Control": "no-cache",
                       "Accept": "application/json" if is_api else "text/plain" if is_provider else "text/html"}
            if is_api:
                headers["x-api-key"] = key
            request = urllib.request.Request(source_url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    raw_body = response.read()
                    response_info = {"http_status": response.status,
                                     "response_headers": _safe_headers(response.headers),
                                     "response_bytes": len(raw_body)}
                    body = raw_body.decode("utf-8")
                if is_provider:
                    metadata = provider_metadata(body, model_id, source_url, utc)
                else:
                    payload = json.loads(body) if is_api else public_catalog(body)
                if not is_api and not is_provider:
                    payload = {**payload, "data": [row for row in payload["data"] if
                        row.get("slug") == AA_SLUGS[model_id] or row.get("model_id") == model_id or
                        (not row.get("slug") and not row.get("model_id") and row.get("id") == model_id)]}
                if not is_provider:
                    parsed = normalize_catalog(payload, source_url, utc)
            except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
                if is_api:
                    raise
                failure = {"model_id": model_id, "source_url": source_url, "fetched_at_utc": utc,
                           "source_kind": source_kind,
                           "status": "FAILED", "error_type": type(exc).__name__,
                           "capability_evidence_status": "NOT_MEASURED", "measured_metric_count": 0,
                           **response_info}
                if isinstance(exc, urllib.error.HTTPError):
                    failure.update(http_status=exc.code, response_headers=_safe_headers(exc.headers))
                    exc.close()
                    if exc.code == 404 and not is_provider:
                        failure["status"] = "MODEL_NOT_FOUND"
                        models[model_id] = normalize_catalog({"data": []}, source_url, utc)[model_id]
                attempts.append(failure)
                if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 429):
                    break
                continue
            if is_provider:
                model = models.setdefault(model_id, normalize_catalog(
                    {"data": []}, PUBLIC_URL.format(model_id), utc)[model_id])
                model["provider_metadata"] = metadata
                if model["evidence_status"] == "MODEL_NOT_FOUND":
                    model["evidence_status"] = "NOT_MEASURED"
                attempts.append({"source_url": source_url, "model_id": model_id,
                                 "source_kind": source_kind, "fetched_at_utc": utc,
                                 "status": "FETCHED_METADATA", **response_info})
                continue
            if is_api:
                models.update(parsed)
            else:
                models[model_id] = parsed[model_id]
            source_evidence = _evidence_summary(parsed if is_api else {model_id: parsed[model_id]})
            attempts.append({"source_url": source_url, "fetched_at_utc": utc,
                             "source_kind": source_kind,
                             **({"model_id": model_id} if not is_api else {}),
                             "status": "FETCHED" if source_evidence["measured_metric_count"] else "FETCHED_MISSING",
                             **response_info, **source_evidence})
        evidence = _evidence_summary(models)
        if any(attempt["status"] == "FAILED" for attempt in attempts):
            event["status"] = "PARTIAL" if (evidence["measured_metric_count"] or
                evidence["provider_metadata_model_count"]) else "FAILED"
        elif (not evidence["measured_metric_count"] and prior_evidence["measured_metric_count"]
              and not evidence["provider_metadata_model_count"]):
            event["status"] = "UNCHANGED_MISSING"
        else:
            event["status"] = "UPDATED_MISSING" if not evidence["measured_metric_count"] else (
                "UPDATED" if evidence["capability_evidence_status"] == "MEASURED" else "PARTIAL")
    except (OSError, ValueError, TypeError) as exc:
        failure = {"source_url": source_url, "fetched_at_utc": utc, "status": "FAILED",
                   "error_type": type(exc).__name__}
        if isinstance(exc, urllib.error.HTTPError):
            failure["http_status"] = exc.code
            failure["response_headers"] = _safe_headers(exc.headers)
            exc.close()
        failure.update(response_info)
        attempts.append(failure)
    attempt_evidence = _evidence_summary(models)
    if event["status"] not in ("FAILED", "UNCHANGED_MISSING") or not previous:
        for model_id in MODEL_IDS:
            if model_id in models:
                continue
            model_url = API_URL if key else PUBLIC_URL.format(model_id)
            model = normalize_catalog({"data": []}, model_url, utc)[model_id]
            model["evidence_status"] = "NOT_MEASURED"
            for metric in model["metrics"]:
                metric["missing_reason"] = "SOURCE_UNAVAILABLE"
            models[model_id] = model
        for model_id, saved in previous.get("models", {}).items():
            fresh = models[model_id]
            if saved.get("provider_metadata"):
                fresh.setdefault("provider_metadata", deepcopy(saved["provider_metadata"]))
            measured = [metric for metric in saved["metrics"]
                        if metric["evidence_status"] == "MEASURED" and metric["score_raw"] is not None]
            if not measured:
                continue
            if not any(metric["evidence_status"] == "MEASURED" for metric in fresh["metrics"]):
                models[model_id] = deepcopy(saved)
                if fresh.get("provider_metadata"):
                    models[model_id]["provider_metadata"] = fresh["provider_metadata"]
                continue
            def metric_key(metric):
                return metric["metric_name"], metric["score_scope"], metric["evaluated_native_effort"]
            retained = {metric_key(metric): deepcopy(metric) for metric in measured}
            for metric in retained.values():
                metric.setdefault("fetched_at_utc", saved["fetched_at_utc"])
                metric.setdefault("model_revision", saved["model_revision"])
            merged = [retained.get(metric_key(metric), metric)
                      if metric["evidence_status"] != "MEASURED" else metric for metric in fresh["metrics"]]
            known = {metric_key(metric) for metric in merged}
            merged.extend(metric for identity, metric in retained.items() if identity not in known)
            fresh["metrics"] = merged
            fresh["evidence_status"] = "MEASURED"
        evidence = _evidence_summary(models)
        version = previous.get("snapshot_version", 0) + 1
        snapshot_id = f"{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}-v{version}"
        snapshot = {"schema_version": 1, "snapshot_id": snapshot_id, "snapshot_version": version,
                    "fetched_at_utc": utc, "status": event["status"], "models": models,
                    "sources": attempts, **evidence}
        snapshot_file = f"snapshots/{snapshot_id}.json"
        _atomic_json(data_dir / snapshot_file, snapshot)
        _atomic_json(data_dir / "current.json", {"snapshot_id": snapshot_id,
                     "snapshot_version": version, "snapshot_file": snapshot_file,
                     "fetched_at_utc": utc, "status": event["status"], **evidence})
        event.update(snapshot_id=snapshot_id, **evidence)
    event["attempt_capability_evidence_status"] = attempt_evidence["capability_evidence_status"]
    event["attempt_measured_metric_count"] = attempt_evidence["measured_metric_count"]
    event["attempts"] = attempts
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / "refresh_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--config", type=Path, default=None,
                        help="Existing JSON: artificial_analysis.api_key or artificial_analysis_api_key")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    result = refresh(args.data_dir, config_path=args.config, timeout=args.timeout)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["status"] == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
