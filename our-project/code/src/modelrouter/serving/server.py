"""FastAPI endpoints sharing one native forward path per Router architecture."""
import logging
import os
import subprocess
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .kev_adapter import KevAdapter
from .laya_adapter import LayaAdapter
from .schemas import (HealthResponse, ModelInfo, ModelsResponse, RouteRequest, RouteResponse,
                      SystemOneRequest, SystemOneResponse, route_questions, route_scores)

logger = logging.getLogger("router_serving")
app = FastAPI(title="ModelRouter Dual-Model Serving API", version="9.0.0")
app.add_middleware(CORSMiddleware,
    allow_origins=["http://127.0.0.1:8765", "http://localhost:8765",
                   "http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
START_TIME = time.monotonic()
REQUEST_LATENCIES = []
TOTAL_REQUESTS = ERROR_REQUESTS = 0
laya_adapter = kev_adapter = None


@app.on_event("startup")
def startup_event():
    global laya_adapter, kev_adapter
    try:
        laya_adapter = LayaAdapter(model_dir=os.environ.get("LAYA_CKPT",
            "/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/checkpoints/best"),
            device=os.environ.get("LAYA_DEVICE", "cpu"))
    except Exception:
        logger.exception("Laya weights could not be loaded")
    try:
        kev_adapter = KevAdapter(adapter_dir=os.environ.get("KEV_DIR", "/home/syy/路由/models/kev-4b-adapter"))
    except Exception:
        logger.exception("Kev weights could not be loaded")


def get_gpu_status():
    try:
        result = subprocess.run(["nvidia-smi",
            "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            return {"available": True, "name": parts[0].strip(), "memory_used_mb": float(parts[1]),
                    "memory_total_mb": float(parts[2]), "utilization_pct": float(parts[3])}
    except (OSError, subprocess.TimeoutExpired):
        logger.warning("GPU metadata unavailable")
    return {"available": False, "name": None, "memory_used_mb": None,
            "memory_total_mb": None, "utilization_pct": None}


@app.get("/health", response_model=HealthResponse)
def health():
    gpu = get_gpu_status()
    adapters = {"laya": laya_adapter, "kev": kev_adapter}
    loaded = {name: adapter is not None and adapter.is_loaded for name, adapter in adapters.items()}
    return HealthResponse(status="healthy" if all(loaded.values()) else "models_unavailable",
        uptime_seconds=round(time.monotonic() - START_TIME, 2), gpu_available=gpu["available"],
        gpu_name=gpu["name"], gpu_memory_used_mb=gpu["memory_used_mb"],
        gpu_memory_total_mb=gpu["memory_total_mb"], gpu_utilization_pct=gpu["utilization_pct"],
        models_loaded=loaded, weights_loaded=loaded,
        inference_verified={name: adapter is not None and adapter.inference_verified
                            for name, adapter in adapters.items()})


@app.get("/models", response_model=ModelsResponse)
def get_models():
    return ModelsResponse(models=[ModelInfo(family=name, run_id=adapter.run_id,
        checkpoint_id=adapter.checkpoint_id, loaded=adapter.is_loaded,
        weights_path=adapter.model_dir if name == "laya" else adapter.adapter_dir,
        metrics=adapter.metrics) for name, adapter in (("laya", laya_adapter), ("kev", kev_adapter))
        if adapter is not None])


@app.post("/system-one", response_model=SystemOneResponse)
@app.post("/v1/systemone", response_model=SystemOneResponse)
def system_one(req: SystemOneRequest):
    global TOTAL_REQUESTS, ERROR_REQUESTS
    target = req.model or req.router_family or "laya"
    family = {"laya": "laya", "laya-421m": "laya", "kev": "kev", "kev-4b": "kev"}.get(target)
    if family is None:
        raise HTTPException(400, detail=f"Unknown router model: {target}")
    adapter = laya_adapter if family == "laya" else kev_adapter
    if adapter is None or not adapter.is_loaded:
        raise HTTPException(503, detail=f"{family} weights are not loaded")
    if not req.questions:
        raise HTTPException(400, detail="questions must contain at least one question")
    TOTAL_REQUESTS += 1
    try:
        answers, latency, usage = adapter.system_one(req.state, req.questions)
    except Exception as exc:
        ERROR_REQUESTS += 1
        logger.exception("%s native forward failed", family)
        raise HTTPException(500, detail=f"{family} forward failed: {exc}") from exc
    REQUEST_LATENCIES.append(latency)
    if len(REQUEST_LATENCIES) > 1000:
        REQUEST_LATENCIES.pop(0)
    identity = {"router_run_id": adapter.run_id,
        "router_weights_path": adapter.model_dir if family == "laya" else adapter.adapter_dir,
        "router_input_usage": usage, "router_identity_status": "ATOMIC_ROUTE_RESPONSE"}
    return SystemOneResponse(router_family=family, model="laya-421m" if family == "laya" else "kev-4b",
        checkpoint_id=adapter.checkpoint_id, answers=answers, decision_latency_ms=latency,
        usage=usage, router_identity=identity)


@app.post("/route", response_model=RouteResponse)
def route(req: RouteRequest):
    native = system_one(SystemOneRequest(router_family=req.router_family,
        state=req.pre_decision_state.router_text(), questions=route_questions(req.legal_actions)))
    selected, ranked, confidence = route_scores(native.answers, req.legal_actions)
    return RouteResponse(request_id=req.request_id, router_family=native.router_family,
        checkpoint_id=native.checkpoint_id, selected_action=selected,
        ranked_actions_or_scores_if_available=ranked, decision_latency_ms=native.decision_latency_ms,
        confidence_if_defined=confidence, router_identity=native.router_identity)


@app.get("/metrics")
def metrics():
    import numpy as np
    return {"total_requests": TOTAL_REQUESTS, "error_requests": ERROR_REQUESTS,
        "error_rate": ERROR_REQUESTS / TOTAL_REQUESTS if TOTAL_REQUESTS else 0,
        "latency_p50_ms": float(np.percentile(REQUEST_LATENCIES, 50)) if REQUEST_LATENCIES else None,
        "latency_p95_ms": float(np.percentile(REQUEST_LATENCIES, 95)) if REQUEST_LATENCIES else None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("modelrouter.serving.server:app", host="0.0.0.0", port=int(os.environ.get("ROUTER_PORT", 8012)))
