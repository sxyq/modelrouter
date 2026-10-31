"""Read AA catalog records and retain provider IDs and exact AA source slugs."""

from __future__ import annotations

import json
import math
import re
from html import unescape
from html.parser import HTMLParser
from typing import Any


MODEL_IDS = ("gpt-6.1-sol", "gpt-6-luna", "qwen3.8-flash")
AA_SLUGS = {"gpt-6.1-sol": "gpt-6-1-sol", "gpt-6-luna": "gpt-6-luna"}
INDEX_METRICS = (
    "artificial_analysis_intelligence_index",
    "artificial_analysis_coding_index",
    "artificial_analysis_agentic_index",
)


class _Scripts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[tuple[dict, str]] = []
        self.attrs: dict | None = None
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "script":
            self.attrs, self.parts = dict(attrs), []

    def handle_data(self, data: str) -> None:
        if self.attrs is not None:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
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


def _records(value: Any) -> list[dict]:
    result, pending = [], [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if ("evaluations" in item or "intelligenceIndexEvaluations" in item) and any(
                key in item for key in ("slug", "model_id", "id")
            ):
                result.append(item)
            else:
                pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(reversed(item))
    return result


def _public_record(row: dict, benchmark_names: dict, index_version: str) -> dict:
    if "intelligenceIndexEvaluations" not in row:
        return row
    effort = (row.get("effort") or {}).get("slug")
    evaluations = {}
    if row.get("intelligenceIndex") is not None and not row.get("intelligenceIndexIsEstimated"):
        evaluations[INDEX_METRICS[0]] = {
            "score_raw": row["intelligenceIndex"], "score_unit": "INDEX",
            "benchmark_version": index_version,
        }
    for entry in row["intelligenceIndexEvaluations"]:
        name = benchmark_names.get(entry["slug"], entry["slug"])
        version = re.search(r"\bv?(\d+(?:\.\d+)+)\b", name)
        evaluations[entry["slug"]] = {
            "score_raw": entry["score"],
            "score_unit": "ELO" if entry["slug"] == "aa-briefcase" else "NOT_REPORTED",
            "benchmark_version": version.group(1) if version else "NOT_REPORTED",
            "benchmark_name": name,
        }
    return {
        "slug": row["slug"], "evaluated_native_effort": effort,
        "model_creator": row.get("creator"), "release_date": row.get("releaseDate"),
        "context_limits": {"context_window_tokens": row.get("contextWindowTokens")},
        "provider": (row.get("performanceDataSource") or {}).get("providerName"),
        "pricing": {"currency": "USD", "unit": "PER_MILLION_TOKENS",
                    "input": row.get("price1mInputTokens"), "output": row.get("price1mOutputTokens"),
                    "cached_input": row.get("cacheHitPrice"), "cache_write": row.get("cacheWritePrice")},
        "evaluations": evaluations,
    }


def public_catalog(html: str) -> dict:
    """Decode Next.js JSON/Flight data; never evaluate page JavaScript."""
    parser, documents, chunks = _Scripts(), [], []
    parser.feed(html)
    decoder = json.JSONDecoder()
    for attrs, body in parser.scripts:
        if attrs.get("id") == "__NEXT_DATA__" or attrs.get("type") == "application/json":
            documents.append(json.loads(body))
        for match in re.finditer(r"self\.__next_f\.push\(", body):
            payload, _ = decoder.raw_decode(body[match.end():])
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
    version = re.search(r"Artificial Analysis Intelligence Index v(\d+(?:\.\d+)+)", html)
    rows = [_public_record(row, names, version.group(1) if version else "NOT_REPORTED")
            for document in documents for row in _records(document)]
    if not rows:
        raise ValueError("No embedded AA evaluation records")
    return {"data": rows}


def _table_rows(html: str) -> list[list[str]]:
    return [[unescape(re.sub(r"<[^>]+>", "", cell)).strip()
             for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)]


def provider_metadata(body: str, model_id: str, source_url: str, fetched_at_utc: str) -> dict:
    """Read exact vendor documents; published prices are not episode billing."""
    result = {"model_id": model_id, "source_url": source_url, "fetched_at_utc": fetched_at_utc,
              "model_revision": "NOT_REPORTED", "evidence_status": "OFFICIAL_DOCUMENTATION"}
    if model_id in MODEL_IDS[:2]:
        identity = re.search(r"Model ID: `([^`]+)`", body)
        if identity is None or identity.group(1) != model_id:
            raise ValueError("Official document model identity differs")
        result["provider"] = "OpenAI"
        result["context_limits"] = {name: int(match.group(1).replace(",", ""))
            for name, pattern in (("context_window_tokens", r"([\d,]+) context window"),
                                  ("max_input_tokens", r"Maximum input tokens: ([\d,]+)"),
                                  ("max_output_tokens", r"([\d,]+) max output tokens"))
            if (match := re.search(pattern, body))}
        pricing_section = body.split("### Text tokens", 1)[1].split("## Endpoints", 1)[0]
        rates = {name: float(value) for name, value in re.findall(
            r"\| (Input|Cached input|Cache writes|Output) \| \$([\d.]+) \| 1M tokens \|", pricing_section)}
        result["pricing"] = {"currency": "USD", "unit": "PER_MILLION_TOKENS",
                             "rates": rates, "conditions": [line[2:] for line in pricing_section.splitlines()
                                                            if line.startswith("- ")]}
        effort_section = body.split("`reasoning.effort` supports", 1)[1].split(".", 1)[0]
        result["native_efforts"] = re.findall(r"`([^`]+)`", effort_section)
    else:
        marker = "window.__ICE_PAGE_PROPS__="
        document, _ = json.JSONDecoder().raw_decode(body.split(marker, 1)[1])
        data = document["docDetailData"]["storeData"]["data"]
        content = data["content"]
        if data["docTitle"] != model_id or f"<code>{model_id}</code>" not in content:
            raise ValueError("Official document model identity differs")
        result.update(provider="Alibaba Cloud", document_modified_at=data["lastModifiedTime"])
        limits = content.split('<h2 id="context-limits">', 1)[1].split('<h2 id="model-pricing">', 1)[0]
        result["context_limits"] = {row[index]: int(row[index + 1])
            for row in _table_rows(limits)[1:] for index in (0, 2)}
        price_content = content.split('<h2 id="model-pricing">', 1)[1].split("<h2 ", 1)[0]
        regions = []
        for section in re.findall(r"<h4[^>]*>(.*?)</h4>(.*?)(?=<h4|\Z)", price_content, re.S):
            region = unescape(re.sub(r"<[^>]+>", "", section[0])).strip()
            for table in re.finditer(r"<table[^>]*>(.*?)</table>", section[1], re.S):
                scopes = re.findall(r"Deployment scope: ([^<]+)", section[1][:table.start()])
                rows = _table_rows(table.group(1))
                currency = re.search(r"Price \((\w+)\)", rows[0][1]).group(1)
                regions.append({"region": region, "deployment_scope": scopes[-1] if scopes else None,
                                "currency": currency, "rates": [
                                    {"billing_item": row[0], "price": float(row[1]), "unit": row[2]}
                                    for row in rows[1:]]})
        result["pricing"] = {"regions": regions, "promotions_included": False}
    return result


def missing_metric(name: str, source_url: str, reason: str = "NOT_MEASURED") -> dict:
    return {
        "metric_name": name,
        "score_raw": None,
        "score_unit": "INDEX" if name in INDEX_METRICS else "NOT_REPORTED",
        "benchmark_version": "NOT_REPORTED",
        "harness_id": "NOT_REPORTED",
        "evaluated_native_effort": None,
        "score_scope": "model",
        "source_url": source_url,
        "evidence_status": "NOT_MEASURED",
        "missing_reason": reason,
    }


def normalize_catalog(payload: dict, source_url: str, fetched_at_utc: str) -> dict:
    """Keep exact identities, original score values, and reported measurement scope."""
    if not isinstance(payload, dict):
        raise ValueError("AA catalog must be a JSON object")
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise ValueError("AA catalog data must be a list")
    models = {
        model_id: {
            "model_id": model_id,
            "evidence_status": "MODEL_NOT_FOUND",
            "model_revision": "NOT_REPORTED",
            "model_creator": None,
            "pricing": {},
            "source_url": source_url,
            "fetched_at_utc": fetched_at_utc,
            "metrics": [],
        }
        for model_id in MODEL_IDS
    }
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("AA model records must be JSON objects")
        identity = row.get("slug") or row.get("model_id") or row.get("id")
        if row.get("slug") and row.get("model_id") and row["slug"] != row["model_id"]:
            if row["slug"] in MODEL_IDS or row["model_id"] in MODEL_IDS:
                raise ValueError("AA model identities differ")
        for model_id in MODEL_IDS:
            if identity not in (model_id, AA_SLUGS.get(model_id, model_id)):
                continue
            model = models[model_id]
            model.update(
                evidence_status="NOT_MEASURED",
                aa_model_slug=identity,
                model_revision=row.get("model_revision") or row.get("revision") or "NOT_REPORTED",
                model_creator=row.get("model_creator"),
                pricing=row.get("pricing") or {},
                provider=row.get("provider"), context_limits=row.get("context_limits") or {},
                release_date=row.get("release_date"),
            )
            evaluations = row.get("evaluations") or {}
            if not isinstance(evaluations, dict):
                raise ValueError("AA evaluations must be a JSON object")
            effort = row.get("evaluated_native_effort", row.get("native_effort", row.get("reasoning_effort")))
            for name, value in evaluations.items():
                if name.endswith("_version") or not isinstance(value, (int, float, dict)) or isinstance(value, bool):
                    continue
                detail = value if isinstance(value, dict) else {"score_raw": value}
                raw = detail.get("score_raw", detail.get("score", detail.get("value")))
                if raw is None:
                    continue
                if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
                    raise ValueError("AA scores must be finite numeric values")
                metric = missing_metric(name, source_url)
                unit = detail.get("score_unit") or detail.get("unit") or metric["score_unit"]
                if name in INDEX_METRICS and str(unit).upper() != "INDEX":
                    raise ValueError("AA composite indices use INDEX units")
                if name in INDEX_METRICS:
                    unit = "INDEX"
                measured_effort = detail.get("evaluated_native_effort", detail.get("native_effort", effort))
                metric.update(
                    score_raw=raw,
                    score_unit=unit,
                    benchmark_version=(detail.get("benchmark_version") or detail.get("version")
                                       or evaluations.get(f"{name}_version")
                                       or row.get("benchmark_version") or payload.get("benchmark_version")
                                       or "NOT_REPORTED"),
                    harness_id=detail.get("harness_id") or row.get("harness_id") or "NOT_REPORTED",
                    evaluated_native_effort=measured_effort,
                    score_scope="effort" if measured_effort is not None else "model",
                    evidence_status="MEASURED",
                    missing_reason=None,
                )
                if detail.get("benchmark_name"):
                    metric["benchmark_name"] = detail["benchmark_name"]
                model["metrics"].append(metric)
    for model in models.values():
        known = {metric["metric_name"] for metric in model["metrics"]}
        reason = model["evidence_status"]
        model["metrics"].extend(
            missing_metric(name, source_url, reason) for name in INDEX_METRICS if name not in known
        )
        if any(metric["evidence_status"] == "MEASURED" for metric in model["metrics"]):
            model["evidence_status"] = "MEASURED"
    return models
