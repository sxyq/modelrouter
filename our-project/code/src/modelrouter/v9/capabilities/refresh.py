"""Refresh AA capability evidence: python -m modelrouter.v9.capabilities.refresh."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from modelrouter.providers.registry import ModelRegistry, V9_MODEL_IDS
from .features import DEFAULT_DATA_DIR, load_current, distinct_stale_metrics
from .normalize import INDEX_METRICS, normalize_catalog, public_catalog, matches_model

API_URL = "https://artificialanalysis.ai/api/v2/language/models/free"
PUBLIC_URL = "https://artificialanalysis.ai/models/"
PUBLIC_RELEASE_URL = "https://artificialanalysis.ai/models/releases/{}"
DEFAULT_CONFIG = Path(os.environ.get("EXTERNAL_TEXT_MODEL_CONFIG",
                                    str(Path.home() / ".agent-global/外部文本模型.local.json")))
DEFAULT_MAX_AGE_SECONDS = 86_400


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _api_key(config_path: str | Path | None) -> str | None:
    key = os.environ.get("ARTIFICIAL_ANALYSIS_API_KEY")
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG
    if key:
        return key.strip()
    if not path.exists():
        return None
    config = json.loads(path.read_text(encoding="utf-8"))
    key = config.get("artificial_analysis", {}).get("api_key") or config.get("artificial_analysis_api_key")
    return key.strip() if key else None


def _safe_headers(headers) -> dict:
    return {name: headers[name] for name in ("Content-Type", "Date", "Last-Modified") if name in headers}


def _fetch(url: str, *, key: str | None = None, accept="application/json", timeout=30.0):
    headers = {"User-Agent": "ModelRouter/9", "Cache-Control": "no-cache", "Accept": accept}
    if key:
        headers["x-api-key"] = key
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        info = {"http_status": response.status, "response_headers": _safe_headers(response.headers),
                "response_bytes": len(body)}
    return body, info, _utc_now()


def _fetch_api(key: str, timeout: float):
    pages, raw, fetched, page, total = [], [], None, 1, 1
    while page <= total:
        url = f"{API_URL}?{urllib.parse.urlencode({'page': page})}"
        body, info, fetched_at = _fetch(url, key=key, timeout=timeout)
        payload = json.loads(body)
        pagination = payload["pagination"]
        pages.append(payload)
        raw.append({"url": url, "body": body.decode("utf-8"), **info})
        fetched = fetched_at
        page, total = pagination["page"] + 1, pagination["total_pages"]
    result = {"data": [row for response in pages for row in response["data"]],
              "intelligence_index_version": pages[0].get("intelligence_index_version", "NOT_REPORTED"),
              "tier": pages[0]["tier"]}
    return result, raw, fetched, pages[0]["tier"]


def _atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".aa-", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _old_metrics(previous: dict, model_id: str, effort: str) -> list[dict]:
    model = previous.get("models", {}).get(model_id, {})
    old = model.get("evaluations", {}).get(effort)
    if old:
        rows = [*old.get("metrics", []), *old.get("stale_metrics", [])]
        fetched = old.get("aa_fetched_at") or model.get("aa_fetched_at") or model.get("fetched_at_utc")
    else:
        rows = [metric for metric in model.get("metrics", [])
                if metric.get("evaluated_native_effort") == effort]
        fetched = model.get("fetched_at_utc") or model.get("aa_fetched_at")
    retained = []
    for row in rows:
        if row.get("score_raw") is None:
            continue
        metric = deepcopy(row)
        if not metric.get("fetched_at_utc"):
            metric["fetched_at_utc"] = fetched
        metric.setdefault("source_url", model.get("source_url"))
        metric.setdefault("model_revision", model.get("model_revision", "NOT_REPORTED"))
        metric.setdefault("publication_at", "NOT_REPORTED")
        metric.setdefault("aa_index_version", "NOT_REPORTED")
        metric.setdefault("aa_model_slug", model.get("aa_model_slug"))
        metric["freshness_status"] = "STALE"
        retained.append(metric)
    unique = {}
    for metric in sorted(retained, key=lambda row: row.get("fetched_at_utc") or ""):
        key = tuple(metric.get(name) for name in (
            "aa_model_slug", "evaluated_native_effort", "metric_name", "score_raw",
            "benchmark_version", "aa_index_version"))
        unique.setdefault(key, metric)
    return list(unique.values())


def _merge_models(api_models: dict, public_models: dict, previous: dict, *, api_ok: bool,
                  public_ok: set[str]) -> dict:
    registry = ModelRegistry()
    merged = {}
    empty = normalize_catalog({"data": []}, PUBLIC_URL, None, "NOT_MEASURED")
    for model_id in V9_MODEL_IDS:
        api_model, page_model = api_models.get(model_id, empty[model_id]), public_models.get(model_id, empty[model_id])
        api_present, page_present = bool(api_model.get("aa_model_id")), bool(page_model.get("aa_model_id"))
        source_model = page_model if page_present else api_model if api_present else empty[model_id]
        model = deepcopy(source_model)
        model["model_id"] = model_id
        model["model_provider"] = registry.get_spec(model_id).provider
        model["model_metrics"] = _merge_metric_rows(api_model.get("model_metrics", []), page_model.get("model_metrics", []))
        model["aa_index_version"] = next((row.get("aa_index_version") for row in
            (*model["model_metrics"], *(metric for action in page_model.get("evaluations", {}).values()
                for metric in action.get("metrics", []))) if row.get("aa_index_version") != "NOT_REPORTED"),
            source_model.get("aa_index_version", "NOT_REPORTED"))
        model_times = [row.get("fetched_at_utc") for row in model["model_metrics"] if row.get("fetched_at_utc")]
        model_times.extend(action.get("aa_fetched_at") for action in page_model.get("evaluations", {}).values()
                           if action.get("aa_fetched_at"))
        model["aa_fetched_at"] = max(model_times, default=source_model.get("aa_fetched_at"))
        page_current = model_id in public_ok
        api_current = api_present and api_ok
        model["freshness_status"] = "FRESH" if page_current or api_current else "STALE" if previous else "NOT_MEASURED"
        actions = {}
        for effort in registry.get_spec(model_id).native_efforts or ("none",):
            api_action = api_model.get("evaluations", {}).get(effort, {})
            page_action = page_model.get("evaluations", {}).get(effort, {})
            metrics = _merge_metric_rows(api_action.get("metrics", []), page_action.get("metrics", []))
            previous_metrics = _old_metrics(previous, model_id, effort)
            stale_metrics = distinct_stale_metrics(metrics, previous_metrics)
            known = set(INDEX_METRICS) | {row["metric_name"] for row in model["model_metrics"]}
            for source in (api_model, page_model):
                for item in source.get("evaluations", {}).values():
                    known.update(row["metric_name"] for row in item.get("metrics", []))
                    known.update(row["metric_name"] for row in item.get("missing_metrics", []))
            present = {row["metric_name"] for row in metrics if row.get("score_raw") is not None}
            missing = []
            source_action = page_action if page_action.get("metrics") or page_action.get("evaluation_status", "").startswith("EXACT_EFFORT") else api_action
            for name in sorted(known - present):
                prior = next((row for row in (*page_action.get("missing_metrics", []),
                    *api_action.get("missing_metrics", [])) if row.get("metric_name") == name), None)
                row = deepcopy(prior) if prior else {"metric_name": name, "score_raw": None,
                    "score_unit": "INDEX" if name in INDEX_METRICS else "NOT_REPORTED",
                    "benchmark_version": "NOT_REPORTED", "score_scope": "effort",
                    "evaluated_native_effort": effort, "aa_index_version": model["aa_index_version"],
                    "source_url": model.get("source_url"), "fetched_at_utc": model.get("aa_fetched_at")}
                row.update(score_raw=None, score_scope="effort", evaluated_native_effort=effort,
                           freshness_status="FRESH" if page_current or api_current else "NOT_MEASURED",
                           missing_reason="MODEL_LEVEL_ONLY" if any(m.get("metric_name") == name
                               for m in model["model_metrics"]) else
                               "STALE_VALUE_AVAILABLE" if any(m.get("metric_name") == name
                                   for m in stale_metrics) else row.get("missing_reason", "EFFORT_NOT_MEASURED"))
                missing.append(row)
            latest_stale = max(stale_metrics, key=lambda row: row.get("fetched_at_utc") or "") if stale_metrics else {}
            old_time = latest_stale.get("fetched_at_utc")
            fetched = next((row.get("fetched_at_utc") for row in metrics if row.get("fetched_at_utc")),
                           source_action.get("aa_fetched_at") or model.get("aa_fetched_at") or old_time)
            source_url = next((row.get("source_url") for row in metrics if row.get("source_url")),
                              source_action.get("source_url") or model.get("source_url") or latest_stale.get("source_url"))
            revision = next((row.get("model_revision") for row in metrics if row.get("model_revision")),
                            source_action.get("model_revision") or model.get("model_revision", "NOT_REPORTED") or
                            latest_stale.get("model_revision", "NOT_REPORTED"))
            publication = next((row.get("publication_at") for row in metrics if row.get("publication_at")),
                                source_action.get("publication_at") or model.get("publication_at", "NOT_REPORTED") or
                                latest_stale.get("publication_at", "NOT_REPORTED"))
            if metrics:
                status, identity = "EXACT_EFFORT", metrics[0].get("evaluation_identity")
                action_freshness = "FRESH"
            elif stale_metrics:
                status, identity, action_freshness = "EXACT_EFFORT_STALE", f"STALE:{model_id}:{effort}", "STALE"
            elif model["model_metrics"]:
                status, identity = "MODEL_LEVEL_ONLY", f"MODEL_LEVEL_ONLY:{model_id}:{effort}"
                action_freshness = "FRESH" if api_current or page_current else "STALE" if stale_metrics else "NOT_MEASURED"
            else:
                status, identity = "NOT_MEASURED", f"NOT_MEASURED:{model_id}:{effort}"
                action_freshness = "FRESH" if page_current else "STALE" if stale_metrics else "NOT_MEASURED"
            other_effort_reference = page_action.get("other_effort_reference") or (
                "SEE_INDEPENDENT_EFFORT_ROWS" if not metrics and not model["model_metrics"] and any(
                    action.get("metrics") for other, action in page_model.get("evaluations", {}).items()
                    if other != effort) else None)
            actions[effort] = {"evaluation_identity": identity, "native_effort": effort,
                "evaluation_status": status, "freshness_status": action_freshness,
                "other_effort_reference": other_effort_reference,
                "aa_fetched_at": fetched, "aa_index_version": next((row.get("aa_index_version")
                    for row in (*metrics, *reversed(stale_metrics)) if row.get("aa_index_version")), model["aa_index_version"]),
                "source_url": source_url, "model_revision": revision, "publication_at": publication,
                "aa_model_id": metrics[0].get("aa_model_id") if metrics else latest_stale.get("aa_model_id", page_action.get("aa_model_id", model.get("aa_model_id"))),
                "aa_model_slug": metrics[0].get("aa_model_slug") if metrics else latest_stale.get("aa_model_slug", page_action.get("aa_model_slug", model.get("aa_model_slug"))),
                "aa_model_name": metrics[0].get("aa_model_name") if metrics else latest_stale.get("aa_model_name", page_action.get("aa_model_name", model.get("aa_model_name"))),
                "metrics": metrics, "missing_metrics": missing, "stale_metrics": stale_metrics}
        model["evaluations"] = actions
        merged[model_id] = model
    return merged


def _merge_metric_rows(*groups):
    merged = {}
    for row in (row for group in groups for row in group):
        key = tuple(row.get(name) for name in (
            "aa_model_id", "aa_model_slug", "evaluated_native_effort", "metric_name",
            "benchmark_version", "aa_index_version", "score_scope"))
        if key not in merged:
            merged[key] = deepcopy(row)
    return list(merged.values())


def refresh(data_dir: str | Path = DEFAULT_DATA_DIR, *, config_path: str | Path | None = None,
            timeout: float = 30.0) -> dict:
    """Fetch paginated free API data and each registry model's public release rows."""
    data_dir = Path(data_dir)
    previous = load_current(data_dir)
    attempted_at, attempts, api_models, public_models = _utc_now(), [], {}, {}
    raw_pages, raw_public, api_ok, api_tier, api_fetched = [], [], False, None, None
    public_ok, public_rows, public_versions, public_times = set(), [], [], []
    key = _api_key(config_path)
    if key:
        try:
            payload, raw_pages, api_fetched, api_tier = _fetch_api(key, timeout)
            api_models = normalize_catalog(payload, API_URL, api_fetched)
            api_ok = True
            attempts.append({"source_kind": "AA_API_FREE", "source_url": API_URL,
                "fetched_at_utc": api_fetched, "status": "FETCHED", "tier": api_tier,
                "pages": len(raw_pages)})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            info = {"status": "FAILED", "source_kind": "AA_API_FREE", "source_url": API_URL,
                    "attempted_at_utc": _utc_now(), "error_type": type(exc).__name__}
            if isinstance(exc, urllib.error.HTTPError):
                info.update(http_status=exc.code, response_headers=_safe_headers(exc.headers))
                exc.close()
            attempts.append(info)
    else:
        attempts.append({"source_kind": "AA_API_FREE", "source_url": API_URL,
                         "attempted_at_utc": attempted_at, "status": "KEY_UNAVAILABLE"})
    for model_id in V9_MODEL_IDS:
        slug = model_id.replace(".", "-")
        url = PUBLIC_RELEASE_URL.format(slug)
        try:
            body, info, fetched_at = _fetch(url, accept="text/html", timeout=timeout)
            payload = public_catalog(body.decode("utf-8"))
            matching = [row for row in payload["data"] if matches_model(row, model_id)]
            rows = [{**row, "source_url": url, "fetched_at_utc": fetched_at,
                     "aa_index_version": payload["aa_index_version"]} for row in payload["data"]]
            public_rows.extend(row for row in rows if matches_model(row, model_id))
            public_versions.append(payload["aa_index_version"])
            public_times.append(fetched_at)
            raw_public.append({"model_id": model_id, "url": url, "body": body})
            if matching:
                public_ok.add(model_id)
            attempts.append({"source_kind": "AA_PUBLIC_RELEASE", "model_id": model_id,
                "source_url": url, "fetched_at_utc": fetched_at,
                "status": "FETCHED" if matching else "MODEL_NOT_FOUND", **info,
                "matched_variants": len(matching)})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            failure = {"source_kind": "AA_PUBLIC_RELEASE", "model_id": model_id,
                       "source_url": url, "attempted_at_utc": _utc_now(),
                       "status": "FAILED", "error_type": type(exc).__name__}
            if isinstance(exc, urllib.error.HTTPError):
                failure.update(http_status=exc.code, response_headers=_safe_headers(exc.headers))
                exc.close()
            attempts.append(failure)
    if public_rows:
        public_payload = {"data": public_rows, "aa_index_version": public_versions[-1]}
        public_models = normalize_catalog(public_payload, PUBLIC_URL, max(public_times))
    models = _merge_models(api_models, public_models, previous, api_ok=api_ok, public_ok=public_ok)
    snapshot_version = previous.get("snapshot_version", 0) + 1
    stamp = datetime.now(timezone.utc)
    snapshot_id = f"{stamp.strftime('%Y%m%dT%H%M%S%fZ')}-v{snapshot_version}"
    aa_fetched_at = max((value for value in (api_fetched, *public_times) if value), default=None)
    freshness = ("FRESH" if api_ok and len(public_ok) == len(V9_MODEL_IDS) else
                 "PARTIAL" if api_ok or public_ok else "STALE")
    measured = sum(len(action["metrics"]) for model in models.values()
                   for action in model["evaluations"].values())
    snapshot = {"schema_version": 2, "snapshot_id": snapshot_id, "snapshot_version": snapshot_version,
        "created_at_utc": _utc_now(), "aa_fetched_at": aa_fetched_at or previous.get("aa_fetched_at") or previous.get("fetched_at_utc"),
        "fetched_at_utc": aa_fetched_at or previous.get("fetched_at_utc"),
        "aa_index_version": next((model["aa_index_version"] for model in models.values()
            if model.get("aa_index_version") != "NOT_REPORTED"), "NOT_REPORTED"),
        "freshness_status": freshness, "status": freshness, "models": models, "sources": attempts,
        "action_count": sum(len(model["evaluations"]) for model in models.values()),
        "measured_metric_count": measured,
        "capability_evidence_status": "MEASURED" if measured else "NOT_MEASURED"}
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(raw_pages, 1):
        path = raw_dir / f"{snapshot_id}-api-page-{index}.json"
        path.write_text(page["body"], encoding="utf-8")
        attempts[0].setdefault("raw_files", []).append(str(path.relative_to(data_dir)))
    for item in raw_public:
        path = raw_dir / f"{snapshot_id}-public-{item['model_id'].replace('.', '-')}.html"
        path.write_bytes(item["body"])
        attempt = next(source for source in attempts if source.get("source_url") == item["url"])
        attempt["raw_file"] = str(path.relative_to(data_dir))
    snapshot["sources"] = attempts
    snapshot_file = f"snapshots/{snapshot_id}.json"
    _atomic_json(data_dir / snapshot_file, snapshot)
    _atomic_json(data_dir / "current.json", {key: snapshot[key] for key in
        ("snapshot_id", "snapshot_version", "aa_fetched_at", "fetched_at_utc", "aa_index_version",
         "freshness_status", "status", "action_count", "measured_metric_count", "capability_evidence_status")}
        | {"snapshot_file": snapshot_file})
    event = {"attempted_at_utc": attempted_at, "snapshot_id": snapshot_id, "status": freshness,
             "aa_fetched_at": snapshot["aa_fetched_at"], "aa_index_version": snapshot["aa_index_version"],
             "action_count": snapshot["action_count"], "measured_metric_count": measured,
             "sources": attempts}
    data_dir.mkdir(parents=True, exist_ok=True)
    with (data_dir / "refresh_log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return snapshot


def ensure_current(output_dir: str | Path = DEFAULT_DATA_DIR, max_age_seconds: float = DEFAULT_MAX_AGE_SECONDS,
                   force: bool = False, pinned_snapshot: dict | None = None, *,
                   config_path: str | Path | None = None, timeout: float = 30.0) -> dict:
    """Use a pinned snapshot unchanged; otherwise refresh only when expired or stale."""
    if pinned_snapshot is not None:
        return pinned_snapshot
    current = load_current(output_dir)
    fetched = current.get("aa_fetched_at") or current.get("fetched_at_utc")
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched.replace("Z", "+00:00"))).total_seconds() if fetched else None
    if force or not current or current.get("freshness_status") == "STALE" or age is None or age > max_age_seconds:
        refresh(output_dir, config_path=config_path, timeout=timeout)
        current = load_current(output_dir)
    if current:
        current["freshness_status"] = current.get("freshness_status", current.get("status", "NOT_MEASURED"))
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-age-seconds", type=float, default=DEFAULT_MAX_AGE_SECONDS)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    snapshot = ensure_current(args.data_dir, max_age_seconds=args.max_age_seconds,
                              force=args.force, config_path=args.config, timeout=args.timeout)
    print(json.dumps({key: value for key, value in snapshot.items() if key != "models"}, ensure_ascii=False))
    return 1 if snapshot["freshness_status"] == "STALE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
