"""External Benchmark evaluation interface, isolation guards, and composite scoring for ModelRouter.

Integrates ENV-004 (Terminal-Bench 2.0) with strict three-tier evaluation:
1. INTERNAL_VALIDATION: Fixed validation set metrics after each epoch.
2. EXTERNAL_DEV: Independent agent benchmark for Top candidate models.
3. FINAL_TEST: Permanently sealed evaluation set.
"""
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("router_data.external_benchmark")

# Tier Constants
TIER_INTERNAL_VALIDATION = "INTERNAL_VALIDATION"
TIER_EXTERNAL_DEV = "EXTERNAL_DEV"
TIER_FINAL_TEST = "FINAL_TEST"

# Status Constants
STATUS_NOT_EVALUATED = "NOT_EVALUATED"
STATUS_ROUTER_SERVING_NOT_READY = "ROUTER_SERVING_NOT_READY"
STATUS_EVALUATED = "EVALUATED"
STATUS_SEALED = "SEALED"
STATUS_EXECUTION_ERROR = "EXECUTION_ERROR"

DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parent / "terminal_bench_manifest.json"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_terminal_bench_manifest(manifest_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load the Terminal-Bench 2.0 manifest containing Canary, External DEV, and Sealed Final Test."""
    path = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Terminal-Bench manifest not found at: {path}")
    return json.loads(path.read_text(encoding="utf8"))


def evaluate_canary_smoke_test(manifest_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Verify Canary tasks (12 tasks) can be parsed and validated without error."""
    manifest = load_terminal_bench_manifest(manifest_path)
    canary = manifest.get("subsets", {}).get("canary", {})
    tasks = canary.get("tasks", [])
    if len(tasks) != 12:
        return {
            "tier": "CANARY",
            "passed": False,
            "error": f"Expected 12 canary tasks, found {len(tasks)}",
            "checked_at": _now_iso(),
        }
    return {
        "tier": "CANARY",
        "passed": True,
        "task_count": len(tasks),
        "task_ids": [t["task_id"] for t in tasks],
        "checked_at": _now_iso(),
    }


def evaluate_external_dev(
    checkpoint_dir: Union[str, Path],
    serving_endpoint: Optional[str] = None,
    harness_config: Optional[Dict[str, Any]] = None,
    manifest_path: Optional[Union[str, Path]] = None,
    max_tasks: Optional[int] = None,
) -> Dict[str, Any]:
    """Evaluate candidate model on EXTERNAL_DEV subset (48 tasks).

    CRITICAL SAFETY & ACADEMIC INTEGRITY RULES:
    1. Laya is a routing decision model, NOT a generative agent. Executing Terminal-Bench
       requires a live routing inference server + agent execution harness (e.g. Harbor).
    2. When no live serving endpoint or authorized API agent harness is provided, this function
       MUST report `ROUTER_SERVING_NOT_READY` or `NOT_EVALUATED`.
    3. NEVER fabricate pass rates, synthetic scores, or random numbers.
    """
    manifest = load_terminal_bench_manifest(manifest_path)
    dev_info = manifest.get("subsets", {}).get("external_dev", {})
    tasks = dev_info.get("tasks", [])
    task_count = len(tasks)

    # Check if serving endpoint is live and reachable
    serving_url = serving_endpoint or os.environ.get("ROUTER_SERVING_ENDPOINT")
    harness_available = bool(harness_config or os.environ.get("ROUTER_AGENT_HARNESS_CMD"))

    if not serving_url or not harness_available:
        return {
            "tier": TIER_EXTERNAL_DEV,
            "status": STATUS_ROUTER_SERVING_NOT_READY,
            "reason": "Router serving endpoint or authorized agent harness is not online/configured",
            "task_count": task_count,
            "executed_tasks": 0,
            "resolved_tasks": 0,
            "pass_rate": None,
            "normalized_score": None,
            "checkpoint_dir": str(checkpoint_dir),
            "evaluated_at": _now_iso(),
        }

    # If serving and harness are configured, perform actual execution
    # (Future harness integration hook)
    try:
        import urllib.request
        req = urllib.request.Request(f"{serving_url}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status != 200:
                return {
                    "tier": TIER_EXTERNAL_DEV,
                    "status": STATUS_ROUTER_SERVING_NOT_READY,
                    "reason": f"Serving endpoint returned status code {resp.status}",
                    "task_count": task_count,
                    "executed_tasks": 0,
                    "resolved_tasks": 0,
                    "pass_rate": None,
                    "normalized_score": None,
                    "evaluated_at": _now_iso(),
                }
    except Exception as exc:
        return {
            "tier": TIER_EXTERNAL_DEV,
            "status": STATUS_ROUTER_SERVING_NOT_READY,
            "reason": f"Serving health check failed: {exc}",
            "task_count": task_count,
            "executed_tasks": 0,
            "resolved_tasks": 0,
            "pass_rate": None,
            "normalized_score": None,
            "evaluated_at": _now_iso(),
        }

    # Live execution placeholder (requires explicit user authorization for external API calls)
    return {
        "tier": TIER_EXTERNAL_DEV,
        "status": STATUS_ROUTER_SERVING_NOT_READY,
        "reason": "Authorized agent execution harness awaiting rollout dispatch",
        "task_count": task_count,
        "executed_tasks": 0,
        "resolved_tasks": 0,
        "pass_rate": None,
        "normalized_score": None,
        "evaluated_at": _now_iso(),
    }


def evaluate_final_test(
    checkpoint_dir: Union[str, Path],
    authorization_key: Optional[str] = None,
) -> Dict[str, Any]:
    """FINAL_TEST is strictly and permanently sealed.

    Raises PermissionError if accessed during training or model selection.
    """
    expected_seal_key = os.environ.get("MODELROUTER_FINAL_TEST_UNSEAL_KEY")
    if not authorization_key or not expected_seal_key or authorization_key != expected_seal_key:
        raise PermissionError(
            "Access Denied: FINAL_TEST (100 tasks) is permanently sealed. "
            "Zero exposure is permitted during training, tuning, or model selection."
        )

    return {
        "tier": TIER_FINAL_TEST,
        "status": STATUS_SEALED,
        "sealed": True,
        "task_count": 100,
        "message": "Final Test is sealed for ultimate post-training evaluation.",
        "evaluated_at": _now_iso(),
    }


def compute_composite_selection_score(
    normalized_internal_score: Optional[float],
    external_dev_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute the model promotion and retention score according to the two-stage formula:

    If EXTERNAL_DEV has been evaluated:
        selection_score = 0.80 * normalized_internal_score + 0.20 * normalized_external_dev_score
    If EXTERNAL_DEV is NOT_EVALUATED or ROUTER_SERVING_NOT_READY:
        selection_score = normalized_internal_score (100% internal weight)
    """
    if normalized_internal_score is None:
        return {
            "selection_score": None,
            "internal_score": None,
            "external_dev_score": None,
            "external_dev_status": STATUS_NOT_EVALUATED,
            "formula_used": "UNDEFINED",
        }

    dev_res = external_dev_result or {}
    dev_status = dev_res.get("status", STATUS_NOT_EVALUATED)
    dev_score = dev_res.get("normalized_score")

    if dev_status == STATUS_EVALUATED and isinstance(dev_score, (int, float)):
        composite = 0.80 * float(normalized_internal_score) + 0.20 * float(dev_score)
        formula = "0.80 * internal + 0.20 * external_dev"
    else:
        composite = float(normalized_internal_score)
        formula = "1.00 * internal (external_dev not evaluated or serving not ready)"

    return {
        "selection_score": round(composite, 4),
        "internal_score": round(float(normalized_internal_score), 4),
        "external_dev_score": round(float(dev_score), 4) if isinstance(dev_score, (int, float)) else None,
        "external_dev_status": dev_status,
        "formula_used": formula,
        "evaluated_at": _now_iso(),
    }
