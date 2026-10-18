#!/usr/bin/env python3
"""
OpenRouter Official Pricing Fetcher and Normalizer.
Fetches https://openrouter.ai/api/v1/models, archives raw snapshot with SHA256,
and produces a normalized USD / 1M Tokens reference pricing index.
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import logging
from typing import Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pricing_fetcher")

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
PRICING_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS_DIR = os.path.join(PRICING_DIR, "snapshots")
INDEX_FILE = os.path.join(PRICING_DIR, "normalized_pricing_index.json")


def fetch_openrouter_models() -> Tuple[bytes, str]:
    """Fetch raw JSON payload from OpenRouter and compute SHA-256."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ModelRouter/1.0",
        "Accept": "application/json",
    }
    req = urllib.request.Request(OPENROUTER_MODELS_URL, headers=headers, method="GET")
    logger.info("Fetching OpenRouter models catalog from %s ...", OPENROUTER_MODELS_URL)
    with urllib.request.urlopen(req, timeout=30.0) as resp:
        raw_bytes = resp.read()
    
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    logger.info("Fetched %d bytes, SHA256: %s", len(raw_bytes), sha256)
    return raw_bytes, sha256


def save_snapshot(raw_bytes: bytes, sha256: str) -> str:
    """Saves raw snapshot to snapshots directory with timestamp and sha256."""
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    snapshot_filename = f"openrouter_models_{timestamp}_{sha256[:8]}.json"
    snapshot_path = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
    
    with open(snapshot_path, "wb") as f:
        f.write(raw_bytes)
    
    latest_path = os.path.join(SNAPSHOTS_DIR, "latest.json")
    try:
        if os.path.islink(latest_path) or os.path.exists(latest_path):
            os.remove(latest_path)
        os.symlink(snapshot_filename, latest_path)
    except Exception as e:
        # Fallback if symlinks not permitted
        with open(latest_path, "wb") as f:
            f.write(raw_bytes)
            
    logger.info("Saved snapshot to %s (and updated latest.json)", snapshot_path)
    return snapshot_path


def parse_float_price(val: Any) -> Optional[float]:
    """Converts a token price string/number to float, or returns None if invalid/missing."""
    if val is None:
        return None
    try:
        f = float(val)
        if f < 0:
            return None
        return f
    except (ValueError, TypeError):
        return None


def normalize_pricing_data(raw_json: Dict[str, Any], sha256: str, snapshot_file: str) -> Dict[str, Any]:
    """
    Normalizes OpenRouter model pricing from per-token float to USD / 1M Tokens.
    Distinguishes:
      - prompt_usd_per_1m
      - completion_usd_per_1m
      - cache_read_usd_per_1m
    Marks missing or unpriced fields as 'UNKNOWN' / 'UNPRICED' rather than 0.
    """
    models_data = raw_json.get("data", [])
    normalized_models: Dict[str, Any] = {}
    
    for item in models_data:
        m_id = item.get("id")
        if not m_id:
            continue
        
        m_name = item.get("name", m_id)
        raw_pricing = item.get("pricing", {})
        context_length = item.get("context_length")
        
        # OpenRouter pricing is per single token (e.g. "0.000002" -> $2.00 / 1M tokens)
        prompt_per_tok = parse_float_price(raw_pricing.get("prompt"))
        completion_per_tok = parse_float_price(raw_pricing.get("completion"))
        cache_read_per_tok = parse_float_price(raw_pricing.get("input_cache_read"))
        
        prompt_1m = round(prompt_per_tok * 1_000_000.0, 6) if prompt_per_tok is not None else "UNKNOWN"
        completion_1m = round(completion_per_tok * 1_000_000.0, 6) if completion_per_tok is not None else "UNKNOWN"
        cache_read_1m = round(cache_read_per_tok * 1_000_000.0, 6) if cache_read_per_tok is not None else "UNKNOWN"
        
        is_priced = (prompt_per_tok is not None) and (completion_per_tok is not None)
        status = "PRICED" if is_priced else "UNPRICED"
        
        normalized_models[m_id] = {
            "id": m_id,
            "name": m_name,
            "context_length": context_length,
            "status": status,
            "prompt_usd_per_1m": prompt_1m,
            "completion_usd_per_1m": completion_1m,
            "cache_read_usd_per_1m": cache_read_1m,
            "raw_pricing": raw_pricing,
        }
        
    index_payload = {
        "metadata": {
            "source": "OpenRouter Public API (/api/v1/models)",
            "fetched_at_utc": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
            "sha256": sha256,
            "snapshot_file": os.path.basename(snapshot_file),
            "total_models": len(normalized_models),
            "unit": "USD / 1M Tokens",
        },
        "models": normalized_models,
    }
    return index_payload


def run_pipeline() -> Dict[str, Any]:
    """Runs the full fetch, archive, and normalize pipeline."""
    raw_bytes, sha256 = fetch_openrouter_models()
    snapshot_path = save_snapshot(raw_bytes, sha256)
    
    raw_json = json.loads(raw_bytes.decode("utf-8"))
    index_payload = normalize_pricing_data(raw_json, sha256, snapshot_path)
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2, ensure_ascii=False)
    
    logger.info("Successfully generated pricing index with %d models at %s", 
                index_payload["metadata"]["total_models"], INDEX_FILE)
    return index_payload


def lookup_model_price(model_id: str) -> Optional[Dict[str, Any]]:
    """Lookup normalized price for a model ID in local index."""
    if not os.path.exists(INDEX_FILE):
        run_pipeline()
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        models = data.get("models", {})
        
        # Direct match
        if model_id in models:
            return models[model_id]
        
        # Lowercase / suffix match (e.g. 'gpt-4o' -> 'openai/gpt-4o')
        clean_id = model_id.lower().strip()
        for k, v in models.items():
            if k.lower() == clean_id or k.lower().endswith(f"/{clean_id}"):
                return v
        return None
    except Exception as e:
        logger.warning("Error reading pricing index: %s", e)
        return None


def calculate_reference_cost(
    model_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    cache_read_tokens: int = 0
) -> Tuple[Optional[float], str]:
    """
    Computes reference cost in USD using OpenRouter official snapshot.
    Returns (cost_usd, status_or_note).
    If model is unknown or unpriced, returns (None, 'UNKNOWN_PRICING').
    """
    pricing = lookup_model_price(model_id)
    if not pricing:
        return None, "MODEL_NOT_IN_OPENROUTER_CATALOG"
    
    p_rate = pricing.get("prompt_usd_per_1m")
    c_rate = pricing.get("completion_usd_per_1m")
    cr_rate = pricing.get("cache_read_usd_per_1m")
    
    if p_rate == "UNKNOWN" or c_rate == "UNKNOWN" or not isinstance(p_rate, (int, float)) or not isinstance(c_rate, (int, float)):
        return None, "UNPRICED_MODEL"
    
    cost = (prompt_tokens * p_rate + completion_tokens * c_rate) / 1_000_000.0
    if isinstance(cr_rate, (int, float)) and cache_read_tokens > 0:
        cost += (cache_read_tokens * cr_rate) / 1_000_000.0
        
    return round(cost, 8), "OK"


if __name__ == "__main__":
    result = run_pipeline()
    print(f"Done. Catalog size: {result['metadata']['total_models']} models.")
    # Quick sanity check on known models
    for test_m in ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-chat"]:
        p = lookup_model_price(test_m)
        if p:
            print(f"Sample: {p['id']} -> Prompt: ${p['prompt_usd_per_1m']}/1M, Output: ${p['completion_usd_per_1m']}/1M")
