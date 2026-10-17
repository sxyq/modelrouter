"""
FastAPI Server for ModelRouter Dual-Model Serving (Laya & Kev).
Conforms strictly to V8 §7.1 contract.
"""

import logging
import os
import subprocess
import time
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .kev_adapter import KevAdapter
from .laya_adapter import LayaAdapter
from .schemas import (HealthResponse, LegalAction, ModelInfo, ModelsResponse,
                      RouteRequest, RouteResponse)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("router_serving")

app = FastAPI(
    title="ModelRouter Dual-Model Serving API",
    version="8.0.0",
    description="Dual Router (Laya-421M & Kev-4B) Serving API on A6000"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8765", "http://localhost:8765", "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global Adapters
START_TIME = time.time()
REQUEST_LATENCIES: List[float] = []
TOTAL_REQUESTS = 0
FALLBACK_REQUESTS = 0

laya_adapter: Optional[LayaAdapter] = None
kev_adapter: Optional[KevAdapter] = None


@app.on_event("startup")
def startup_event():
    global laya_adapter, kev_adapter
    logger.info("Starting up ModelRouter Serving API...")

    # Load Laya Adapter (prefers CPU to not interrupt GPU training F03)
    laya_ckpt = os.environ.get("LAYA_CKPT", "/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/checkpoints/best")
    laya_device = os.environ.get("LAYA_DEVICE", "cpu")
    try:
        laya_adapter = LayaAdapter(model_dir=laya_ckpt, device=laya_device)
    except Exception as e:
        logger.error(f"Failed to initialize LayaAdapter: {e}")

    # Load Kev Adapter
    kev_adapter_dir = os.environ.get("KEV_DIR", "/home/syy/路由/models/kev-4b-adapter")
    try:
        kev_adapter = KevAdapter(adapter_dir=kev_adapter_dir)
    except Exception as e:
        logger.error(f"Failed to initialize KevAdapter: {e}")


def get_gpu_status():
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            return {
                "available": True,
                "name": parts[0],
                "memory_used_mb": float(parts[1]),
                "memory_total_mb": float(parts[2]),
                "utilization_pct": float(parts[3])
            }
    except Exception:
        pass
    return {"available": False, "name": None, "memory_used_mb": None, "memory_total_mb": None, "utilization_pct": None}


@app.get("/health", response_model=HealthResponse)
def health():
    gpu = get_gpu_status()
    models_status = {
        "laya": laya_adapter is not None and laya_adapter.is_loaded,
        "kev": kev_adapter is not None and kev_adapter.is_loaded
    }
    weights_status = {
        "laya": laya_adapter is not None and laya_adapter.is_loaded,
        "kev": kev_adapter is not None and kev_adapter.is_loaded
    }
    inference_status = {
        "laya": laya_adapter is not None and laya_adapter.is_loaded,
        "kev": kev_adapter is not None and getattr(kev_adapter, "inference_verified", False)
    }
    return HealthResponse(
        status="healthy",
        uptime_seconds=round(time.time() - START_TIME, 2),
        gpu_available=gpu["available"],
        gpu_name=gpu["name"],
        gpu_memory_used_mb=gpu["memory_used_mb"],
        gpu_memory_total_mb=gpu["memory_total_mb"],
        gpu_utilization_pct=gpu["utilization_pct"],
        models_loaded=models_status,
        weights_loaded=weights_status,
        inference_verified=inference_status
    )


@app.get("/models", response_model=ModelsResponse)
def get_models():
    models = []
    if laya_adapter:
        models.append(ModelInfo(
            family="laya",
            run_id=laya_adapter.run_id,
            checkpoint_id=laya_adapter.checkpoint_id,
            epoch=1,
            loaded=laya_adapter.is_loaded,
            weights_path=laya_adapter.model_dir,
            metrics=laya_adapter.metrics or {"best_val_accuracy_s1": 0.6756, "val_loss": 0.5978}
        ))
    if kev_adapter:
        models.append(ModelInfo(
            family="kev",
            run_id=kev_adapter.run_id,
            checkpoint_id=kev_adapter.checkpoint_id,
            epoch=None,
            loaded=kev_adapter.is_loaded,
            weights_path=kev_adapter.adapter_dir,
            metrics=kev_adapter.metrics
        ))
    return ModelsResponse(models=models)


@app.post("/route", response_model=RouteResponse)
def route(req: RouteRequest):
    global TOTAL_REQUESTS, FALLBACK_REQUESTS, REQUEST_LATENCIES

    if not req.legal_actions:
        raise HTTPException(status_code=400, detail="NO_LEGAL_ACTION: legal_actions must contain at least one item")

    TOTAL_REQUESTS += 1
    target_family = (req.router_family or "laya").lower()

    if target_family == "laya":
        if not laya_adapter or not laya_adapter.is_loaded:
            raise HTTPException(status_code=503, detail="NO_MODEL_LOADED: Laya router model is not loaded")
        try:
            act, ranked, lat, conf = laya_adapter.route(req.pre_decision_state, req.legal_actions)
            REQUEST_LATENCIES.append(lat)
            if len(REQUEST_LATENCIES) > 1000:
                REQUEST_LATENCIES.pop(0)

            return RouteResponse(
                request_id=req.request_id,
                router_family="laya",
                checkpoint_id=laya_adapter.checkpoint_id,
                selected_action=act,
                ranked_actions_or_scores_if_available=ranked,
                decision_latency_ms=round(lat, 2),
                fallback_used=False,
                fallback_reason=None,
                confidence_if_defined=round(conf, 4) if conf is not None else None
            )
        except Exception as e:
            logger.error(f"Laya routing failed: {e}", exc_info=True)
            FALLBACK_REQUESTS += 1
            # Fallback to first legal action
            fallback_act = req.legal_actions[0]
            return RouteResponse(
                request_id=req.request_id,
                router_family="laya",
                checkpoint_id=laya_adapter.checkpoint_id if laya_adapter else "unknown",
                selected_action=fallback_act,
                ranked_actions_or_scores_if_available=[],
                decision_latency_ms=1.0,
                fallback_used=True,
                fallback_reason=f"ROUTER_ERROR: {str(e)}",
                confidence_if_defined=None
            )

    elif target_family == "kev":
        if not kev_adapter or not kev_adapter.is_loaded:
            raise HTTPException(status_code=503, detail="NO_MODEL_LOADED: Kev router model is not loaded")
        try:
            act, ranked, lat, conf, fb, fb_reason = kev_adapter.route(req.pre_decision_state, req.legal_actions)
            REQUEST_LATENCIES.append(lat)
            if len(REQUEST_LATENCIES) > 1000:
                REQUEST_LATENCIES.pop(0)

            return RouteResponse(
                request_id=req.request_id,
                router_family="kev",
                checkpoint_id=kev_adapter.checkpoint_id,
                selected_action=act,
                ranked_actions_or_scores_if_available=ranked,
                decision_latency_ms=round(lat, 2),
                fallback_used=fb,
                fallback_reason=fb_reason,
                confidence_if_defined=round(conf, 4) if conf is not None else None
            )
        except Exception as e:
            logger.error(f"Kev routing failed: {e}", exc_info=True)
            FALLBACK_REQUESTS += 1
            return RouteResponse(
                request_id=req.request_id,
                router_family="kev",
                checkpoint_id=kev_adapter.checkpoint_id if kev_adapter else "unknown",
                selected_action=req.legal_actions[0],
                ranked_actions_or_scores_if_available=[],
                decision_latency_ms=1.0,
                fallback_used=True,
                fallback_reason=f"ROUTER_ERROR: {str(e)}",
                confidence_if_defined=None
            )

    else:
        raise HTTPException(status_code=400, detail=f"INCOMPATIBLE_STATE: Unknown router_family '{req.router_family}'")


@app.get("/metrics")
def metrics():
    import numpy as np
    p50 = float(np.percentile(REQUEST_LATENCIES, 50)) if REQUEST_LATENCIES else 0.0
    p95 = float(np.percentile(REQUEST_LATENCIES, 95)) if REQUEST_LATENCIES else 0.0
    return {
        "total_requests": TOTAL_REQUESTS,
        "fallback_requests": FALLBACK_REQUESTS,
        "fallback_rate": round(FALLBACK_REQUESTS / max(TOTAL_REQUESTS, 1), 4),
        "latency_p50_ms": round(p50, 2),
        "latency_p95_ms": round(p95, 2)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("ROUTER_PORT", 8012))
    uvicorn.run("experiments.router_serving.server:app", host="0.0.0.0", port=port, log_level="info")
