"""Normalize AA catalog data without conflating model and effort scores."""

from __future__ import annotations

import json
import math
import re
from html.parser import HTMLParser

from modelrouter.providers.registry import ModelRegistry, V9_MODEL_IDS

INDEX_METRICS = ("artificial_analysis_intelligence_index", "artificial_analysis_coding_index",
                 "artificial_analysis_agentic_index")
REGISTRY = ModelRegistry()


def matches_model(row, model_id):
    slug = model_id.replace(".", "-")
    suffixes = {"non-reasoning", *REGISTRY.get_spec(model_id).native_efforts}
    return row.get("model_id") == model_id or row.get("slug") in {slug, *(f"{slug}-{effort}" for effort in suffixes)}


class _Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts, self.attrs, self.parts = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.attrs, self.parts = dict(attrs), []

    def handle_data(self, data):
        if self.attrs is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.attrs is not None:
            self.scripts.append((self.attrs, "".join(self.parts)))
            self.attrs = None


def _json_values(text: str) -> list:
    decoder, values, offset = json.JSONDecoder(), [], 0
    while match := re.search(r"[\[{]", text[offset:]):
        start = offset + match.start()
        try:
            value, consumed = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            offset = start + 1
        else:
            values.append(value)
            offset = start + consumed
    return values


def _records(value) -> list[dict]:
    records, pending = [], [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if "intelligenceIndexEvaluations" in item and any(k in item for k in ("slug", "id")):
                records.append(item)
            else:
                pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(reversed(item))
    return records


def _effort_label(row: dict) -> str | None:
    reported = (row.get("effort") or {}).get("slug")
    if reported:
        return reported
    match = re.search(r"\(([^()]*)\)$", row.get("name", ""))
    if not match:
        return None
    label = match.group(1).split(",", 1)[0].strip().lower()
    return "none" if label == "non-reasoning" else label


def public_catalog(html: str) -> dict:
    """Decode public AA page records, retaining AA IDs and each reported effort."""
    parser, documents, chunks = _Scripts(), [], []
    parser.feed(html)
    for attrs, body in parser.scripts:
        if attrs.get("id") == "__NEXT_DATA__" or attrs.get("type") == "application/json":
            documents.append(json.loads(body))
        for match in re.finditer(r"self\.__next_f\.push\(", body):
            payload, _ = json.JSONDecoder().raw_decode(body[match.end():])
            if len(payload) > 1 and payload[0] == 1 and isinstance(payload[1], str):
                chunks.append(payload[1])
    documents.extend(_json_values("".join(chunks)))
    names, pending = {}, list(documents)
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if "slug" in item and "name" in item and "keywords" in item:
                names[item["slug"]] = item["name"]
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    page_version = re.search(r"Artificial Analysis Intelligence Index v(\d+(?:\.\d+)+)", html)
    rows = []
    for row in (record for doc in documents for record in _records(doc)):
        effort = _effort_label(row)
        evaluations = {}
        if row.get("intelligenceIndex") is not None and not row.get("intelligenceIndexIsEstimated"):
            evaluations[INDEX_METRICS[0]] = {"score_raw": row["intelligenceIndex"], "score_unit": "INDEX",
                "benchmark_version": page_version.group(1) if page_version else "NOT_REPORTED"}
        for entry in row["intelligenceIndexEvaluations"]:
            name = names.get(entry["slug"], entry["slug"])
            version = re.search(r"\bv?(\d+(?:\.\d+)+)\b", name)
            evaluations[entry["slug"]] = {"score_raw": entry["score"],
                "score_unit": "ELO" if entry["slug"] == "aa-briefcase" else "NOT_REPORTED",
                "benchmark_version": version.group(1) if version else "NOT_REPORTED",
                "benchmark_name": name}
        rows.append({"id": row.get("id"), "slug": row["slug"], "name": row.get("name"),
            "model_revision": row.get("revision") or row.get("modelRevision") or "NOT_REPORTED",
            "publication_at": row.get("publishedAt") or row.get("publicationDate") or "NOT_REPORTED",
            "release_date": row.get("releaseDate"), "model_creator": row.get("creator"),
            "context_limits": {"context_window_tokens": row.get("contextWindowTokens")},
            "provider": (row.get("performanceDataSource") or {}).get("providerName"),
            "pricing": {"currency": "USD", "unit": "PER_MILLION_TOKENS",
                "input": row.get("price1mInputTokens"), "output": row.get("price1mOutputTokens"),
                "cached_input": row.get("cacheHitPrice"), "cache_write": row.get("cacheWritePrice")},
            "effort_records": [{"aa_model_id": row.get("id"), "aa_model_slug": row["slug"],
                "aa_model_name": row.get("name"),
                "evaluated_native_effort": effort, "model_revision": row.get("revision") or
                row.get("modelRevision") or "NOT_REPORTED", "publication_at": row.get("publishedAt") or
                row.get("publicationDate") or "NOT_REPORTED", "evaluations": evaluations}],
            "model_metrics": []})
    if not rows:
        raise ValueError("No embedded AA evaluation records")
    return {"data": rows, "aa_index_version": page_version.group(1) if page_version else "NOT_REPORTED"}


def _metric(name, value, *, model_id, slug, effort, source_url, fetched_at, index_version,
            revision, publication_at, freshness):
    detail = value if isinstance(value, dict) else {"score_raw": value}
    score = detail.get("score_raw", detail.get("score", detail.get("value")))
    if score is not None and (isinstance(score, bool) or not isinstance(score, (int, float))
                              or not math.isfinite(score)):
        raise ValueError("AA scores must be finite numbers")
    benchmark_version = detail.get("benchmark_version", detail.get("version", "NOT_REPORTED"))
    return {"metric_name": name, "score_raw": score,
        "score_unit": detail.get("score_unit", detail.get("unit",
            "INDEX" if name in INDEX_METRICS else "NOT_REPORTED")),
        "benchmark_version": benchmark_version,
        "harness_id": detail.get("harness_id", "NOT_REPORTED"),
        "score_scope": "effort" if effort else "model", "evaluated_native_effort": effort,
        "aa_index_version": index_version, "aa_model_id": model_id, "aa_model_slug": slug,
        "aa_model_name": detail.get("aa_model_name"),
        "evaluation_identity": f"aa:{model_id or slug}:{slug}:{effort or 'model'}",
        "comparability_status": ("COMPARABLE_WITH_MATCHING_EFFORT_AND_VERSION"
            if effort and benchmark_version != "NOT_REPORTED" else
            "EXACT_EFFORT_VERSION_NOT_REPORTED" if effort else "MODEL_LEVEL_ONLY"),
        "model_revision": revision, "publication_at": publication_at,
        "source_url": source_url, "fetched_at_utc": fetched_at, "freshness_status": freshness,
        "evidence_status": "MEASURED" if score is not None else "NOT_MEASURED",
        "missing_reason": None if score is not None else "NOT_MEASURED",
        **({"benchmark_name": detail["benchmark_name"]} if detail.get("benchmark_name") else {})}


def _dedupe_metrics(rows):
    unique, seen = [], set()
    for row in rows:
        identity = tuple(row.get(name) for name in (
            "aa_model_id", "aa_model_slug", "evaluated_native_effort", "metric_name",
            "benchmark_version", "aa_index_version", "score_scope"))
        if identity not in seen:
            seen.add(identity)
            unique.append(row)
    return unique


def normalize_catalog(payload: dict, source_url: str, fetched_at_utc: str,
                      freshness_status="FRESH") -> dict:
    """Build model-level metadata and independent registry effort observations."""
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("AA catalog data must be a list")
    index_version = str(payload.get("aa_index_version", payload.get("intelligence_index_version", "NOT_REPORTED")))
    if index_version != "NOT_REPORTED" and "." not in index_version:
        index_version += ".0"
    models = {}
    for model_id in V9_MODEL_IDS:
        spec, slug = REGISTRY.get_spec(model_id), model_id.replace(".", "-")
        matched = [row for row in rows if matches_model(row, model_id)]
        model_metrics, effort_rows = [], {}
        source = source_url
        for row in matched:
            source = row.get("source_url", source)
            row_fetched = row.get("fetched_at_utc", fetched_at_utc)
            row_index = row.get("aa_index_version", index_version)
            shared = {"aa_model_id": row.get("id"), "aa_model_slug": row.get("slug", slug),
                "aa_model_name": row.get("name"),
                "model_revision": row.get("model_revision", row.get("revision", "NOT_REPORTED")),
                "publication_at": row.get("publication_at", "NOT_REPORTED")}
            evaluations = row.get("evaluations", {})
            for name, value in evaluations.items():
                if value is None or isinstance(value, (dict, int, float)) and not isinstance(value, bool):
                    model_metrics.append(_metric(name, value, model_id=shared["aa_model_id"],
                        slug=shared["aa_model_slug"], effort=None, source_url=source,
                        fetched_at=row_fetched, index_version=row_index,
                        revision=shared["model_revision"], publication_at=shared["publication_at"],
                        freshness=freshness_status))
            if not row.get("effort_records"):
                effort = row.get("evaluated_native_effort", row.get("native_effort"))
                if effort:
                    effort_rows.setdefault(effort, []).append(({**row, "aa_model_id": row.get("id"),
                        "aa_model_slug": row.get("slug", slug), "aa_model_name": row.get("name"),
                        "model_revision": shared["model_revision"], "publication_at": shared["publication_at"],
                        "source_url": source, "fetched_at_utc": row_fetched,
                        "aa_index_version": row_index}, evaluations))
            for record in row.get("effort_records", []):
                effort = record.get("evaluated_native_effort") or _effort_label(row)
                if effort:
                    effort_rows.setdefault(effort, []).append(({**record,
                        "aa_model_name": record.get("aa_model_name", row.get("name")),
                        "source_url": source, "fetched_at_utc": row_fetched,
                        "aa_index_version": row_index}, record.get("evaluations", {})))
                else:
                    for name, value in record.get("evaluations", {}).items():
                        model_metrics.append(_metric(name, value, model_id=record.get("aa_model_id"),
                            slug=record.get("aa_model_slug", slug), effort=None, source_url=source,
                            fetched_at=row_fetched, index_version=row_index,
                            revision=record.get("model_revision", "NOT_REPORTED"),
                            publication_at=record.get("publication_at", "NOT_REPORTED"),
                            freshness=freshness_status))
        available_metrics = set(INDEX_METRICS)
        available_metrics.update(metric["metric_name"] for metric in model_metrics)
        available_metrics.update(name for values in effort_rows.values() for _, items in values for name in items)
        first = matched[0] if matched else {}
        actions = {}
        for effort in spec.native_efforts or ("none",):
            records = effort_rows.get(effort, [])
            observations, missing = [], []
            for record, evaluations in records:
                rid, rslug = record.get("aa_model_id", shared.get("aa_model_id") if matched else None), record.get("aa_model_slug", slug)
                revision = record.get("model_revision", shared.get("model_revision", "NOT_REPORTED") if matched else "NOT_REPORTED")
                publication = record.get("publication_at", shared.get("publication_at", "NOT_REPORTED") if matched else "NOT_REPORTED")
                for name, value in evaluations.items():
                    if value is None or isinstance(value, (dict, int, float)) and not isinstance(value, bool):
                        observations.append(_metric(name, {**value, "aa_model_name": record.get("aa_model_name")}
                            if isinstance(value, dict) else {"score_raw": value, "aa_model_name": record.get("aa_model_name")}, model_id=rid, slug=rslug,
                            effort=effort, source_url=record.get("source_url", source), fetched_at=record.get("fetched_at_utc", fetched_at_utc),
                            index_version=record.get("aa_index_version", index_version),
                            revision=revision, publication_at=publication,
                            freshness=freshness_status))
            observations = _dedupe_metrics(observations)
            present = {metric["metric_name"] for metric in observations if metric["score_raw"] is not None}
            for name in sorted(available_metrics - present):
                source_record = records[0][0] if records else matched[0] if matched else {}
                exact_record = bool(records)
                metric = _metric(name, {"score_raw": None, "aa_model_name": source_record.get("aa_model_name", source_record.get("name"))},
                    model_id=source_record.get("aa_model_id", source_record.get("id")) if exact_record else None,
                    slug=source_record.get("aa_model_slug", source_record.get("slug")) if exact_record else None,
                    effort=effort, source_url=source_record.get("source_url", source) if exact_record else None,
                    fetched_at=source_record.get("fetched_at_utc", fetched_at_utc) if exact_record else None,
                    index_version=source_record.get("aa_index_version", index_version) if exact_record else "NOT_REPORTED",
                    revision=source_record.get("model_revision", "NOT_REPORTED") if exact_record else "NOT_REPORTED",
                    publication_at=source_record.get("publication_at", "NOT_REPORTED") if exact_record else "NOT_REPORTED",
                    freshness=freshness_status if exact_record else "NOT_MEASURED")
                metric["missing_reason"] = ("EXACT_EFFORT_SCORE_NOT_REPORTED" if exact_record else
                    "MODEL_LEVEL_ONLY" if any(item["metric_name"] == name for item in model_metrics) else
                    "EFFORT_NOT_MEASURED" if matched else "MODEL_NOT_FOUND")
                if not exact_record:
                    metric["evaluation_identity"] = f"NOT_MEASURED:{model_id}:{effort}:{name}"
                missing.append(metric)
            aa_identity = (records[0][0].get("aa_model_id") or slug) if records else slug
            aa_slug = records[0][0].get("aa_model_slug", slug) if records else first.get("slug", slug)
            model_level_only = not records and bool(model_metrics)
            other_effort_reference = ("SEE_INDEPENDENT_EFFORT_ROWS" if not records and not model_level_only
                and any(name != effort and entries for name, entries in effort_rows.items()) else None)
            actions[effort] = {"evaluation_identity": (f"aa:{aa_identity}:{aa_slug}:{effort}" if records
                    else f"MODEL_LEVEL_ONLY:{model_id}:{effort}" if model_level_only else
                    f"NOT_MEASURED:{model_id}:{effort}"),
                "other_effort_reference": other_effort_reference,
                "aa_model_id": records[0][0].get("aa_model_id") if records else first.get("id") if model_level_only else None,
                "aa_model_slug": records[0][0].get("aa_model_slug") if records else first.get("slug") if model_level_only else None,
                "aa_model_name": records[0][0].get("aa_model_name") if records else first.get("name") if model_level_only else None,
                "native_effort": effort, "evaluation_status": "EXACT_EFFORT" if records else
                    "MODEL_LEVEL_ONLY" if model_level_only else "NOT_MEASURED",
                        "freshness_status": freshness_status,
                "aa_fetched_at": records[0][0].get("fetched_at_utc", fetched_at_utc) if records else
                    matched[0].get("fetched_at_utc", fetched_at_utc) if matched else None,
                "aa_index_version": records[0][0].get("aa_index_version", index_version) if records else
                    matched[0].get("aa_index_version", index_version) if matched else "NOT_REPORTED",
                "source_url": records[0][0].get("source_url", source) if records else source if matched else None,
                "model_revision": records[0][0].get("model_revision", "NOT_REPORTED") if records else
                    matched[0].get("model_revision", "NOT_REPORTED") if matched else "NOT_REPORTED",
                "publication_at": records[0][0].get("publication_at", "NOT_REPORTED") if records else
                    matched[0].get("publication_at", "NOT_REPORTED") if matched else "NOT_REPORTED",
                "metrics": [metric for metric in observations if metric["score_raw"] is not None],
                "missing_metrics": missing}
        models[model_id] = {"model_id": model_id, "aa_model_id": first.get("id"),
            "aa_model_slug": first.get("slug", slug), "model_revision": first.get("model_revision", "NOT_REPORTED"),
            "aa_model_name": first.get("name"),
            "publication_at": first.get("publication_at", "NOT_REPORTED"),
            "model_creator": first.get("model_creator"), "release_date": first.get("release_date"),
            "provider": spec.provider, "aa_provider": first.get("provider"),
            "context_limits": first.get("context_limits", {"context_window_tokens": spec.context_window,
                                                               "max_output_tokens": spec.max_output_tokens}),
            "pricing": first.get("pricing", {"input": spec.input_price_per_1m,
                "output": spec.output_price_per_1m, "source": spec.pricing_source,
                "status": spec.pricing_status}), "source_url": source if matched else None,
            "aa_fetched_at": max((row.get("fetched_at_utc", fetched_at_utc) for row in matched), default=None),
            "aa_index_version": first.get("aa_index_version", index_version) if matched else "NOT_REPORTED",
            "freshness_status": freshness_status if matched else "NOT_MEASURED",
            "evidence_status": "MEASURED" if model_metrics else "NOT_MEASURED",
            "model_metrics": model_metrics, "evaluations": actions}
    return models
