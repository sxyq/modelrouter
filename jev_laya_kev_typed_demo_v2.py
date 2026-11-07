#!/usr/bin/env python3
"""ModelRouter live demo: Choice / Score / Noul typed decisions on A6000.

Features:
- Dual model native inference: Laya-421M (ModernBERT) and Kev-4B (Qwen3.5-4B).
- TypeSafe System One 3 decision primitives: Choice, Score, Noul.
- Side-by-side dual-model comparison and single-model drill-down.
- Real-time SVG dials, bar charts, and discrete distribution histograms.
- 16:9 widescreen layout for projector and advisor presentation.
- Zero mock, zero hallucinations: all predictions come from true forward passes.
- Local server: http://127.0.0.1:8766
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("modelrouter_demo")

HOST = "127.0.0.1"
PORT = int(os.environ.get("DEMO_PORT", "8766"))
ROUTER_URL = os.environ.get("ROUTER_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAX_PAYLOAD = 256 * 1024
HTML_PATH = Path(__file__).resolve().parent / "our-project/dashboard/assets/jev_laya_kev_typed_demo_v2.html"
HTML_CONTENT = HTML_PATH.read_text(encoding="utf-8")


def fetch_remote_json(url: str, body: Optional[Dict[str, Any]] = None, timeout: float = 45.0) -> Dict[str, Any]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if payload is not None else "GET"
    )
    # Bypassing macOS system proxies
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def execute_single_system_one(family: str, state: Any, questions: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    endpoint = f"{ROUTER_URL}/system-one"
    payload = {
        "router_family": family,
        "state": state,
        "questions": questions
    }
    raw = fetch_remote_json(endpoint, payload, timeout=45.0)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    raw["elapsed_ms"] = elapsed_ms
    return raw


class DemoServerHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.info(f"{self.address_string()} - {fmt % args}")

    def respond_json(self, status_code: int, data: Any):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_html(self, status_code: int, html_str: str):
        body = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.respond_html(200, HTML_CONTENT)

        if self.path == "/api/status":
            reachable = False
            laya_loaded = False
            kev_loaded = False
            laya_ckpt = "F05/best"
            kev_ckpt = "1001bb4d82..."
            gpu_info = {}

            try:
                h = fetch_remote_json(f"{ROUTER_URL}/health", timeout=3.0)
                reachable = (h.get("status") == "healthy")
                laya_loaded = bool(h.get("models_loaded", {}).get("laya"))
                kev_loaded = bool(h.get("models_loaded", {}).get("kev"))
                gpu_info = {
                    "name": h.get("gpu_name"),
                    "memory_used_mb": h.get("gpu_memory_used_mb"),
                    "utilization_pct": h.get("gpu_utilization_pct")
                }
            except Exception:
                reachable = False

            return self.respond_json(200, {
                "router_reachable": reachable,
                "router_url": ROUTER_URL,
                "laya_loaded": laya_loaded,
                "kev_loaded": kev_loaded,
                "laya_checkpoint": laya_ckpt,
                "kev_checkpoint": kev_ckpt,
                "gpu": gpu_info
            })

        return self.respond_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path != "/api/decision":
            return self.respond_json(404, {"error": "Not Found"})

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_PAYLOAD:
            return self.respond_json(400, {"error": "Invalid request payload size"})

        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            router = body.get("router", "laya").lower()
            state = body.get("state")
            questions = body.get("questions")

            if not state or not questions:
                return self.respond_json(400, {"error": "Missing 'state' or 'questions'"})

            if router in ("laya", "kev"):
                res = execute_single_system_one(router, state, questions)
                return self.respond_json(200, res)

            elif router in ("both", "compare"):
                # Execute Laya and Kev concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    fut_laya = executor.submit(execute_single_system_one, "laya", state, questions)
                    fut_kev = executor.submit(execute_single_system_one, "kev", state, questions)
                    res_laya = fut_laya.result()
                    res_kev = fut_kev.result()

                return self.respond_json(200, {
                    "mode": "both",
                    "laya": res_laya,
                    "kev": res_kev
                })

            else:
                return self.respond_json(400, {"error": f"Unsupported router family: {router}"})

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Upstream HTTP error: {e.code} - {err_body}")
            return self.respond_json(502, {"error": f"Upstream A6000 Serving Error (HTTP {e.code}): {err_body}"})
        except Exception as e:
            logger.error(f"Internal Demo Error: {e}", exc_info=True)
            return self.respond_json(500, {"error": f"Demo Server Error: {str(e)}"})


def main():
    logger.info(f"Starting ModelRouter Typed Decision Demo on http://{HOST}:{PORT}")
    logger.info(f"Target Router API: {ROUTER_URL}")
    server = ThreadingHTTPServer((HOST, PORT), DemoServerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Demo server stopping...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
