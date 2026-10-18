#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelRouter P16/P17 真实双模型 Demo 桥接服务

职责：
1. 同源托管 P16.html / P17.html / deck.html，避免浏览器 CORS 限制；
2. 把 /api/* 转发到 A6000 上真实运行的 ModelRouter Dual-Model Serving API；
3. 保存每一轮真实 Request/Response 原文，并配对"同一轮"的 Laya/Kev 结果，
   供 P17 读取，保证两页展示的是同一次双模型请求。

上游地址来源（优先级）：
  --upstream 参数 > 环境变量 MR_UPSTREAM > assets/local_config.json > http://127.0.0.1:8000

只使用 Python 标准库，不引入额外依赖。
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # 汇报三/
ASSETS = ROOT / "assets"
RUNS = ROOT / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

CST = timezone(timedelta(hours=8))
LOCK = threading.Lock()

DEFAULT_UPSTREAM = "http://127.0.0.1:8000"
LATEST_PAIR = RUNS / "latest_pair.json"


def load_upstream() -> str:
    cfg = ASSETS / "local_config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            value = data.get("upstream")
            if value:
                return str(value).rstrip("/")
        except Exception:
            pass
    return DEFAULT_UPSTREAM


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="milliseconds")


def stamp() -> str:
    return datetime.now(CST).strftime("%Y%m%d_%H%M%S")


class UpstreamError(Exception):
    def __init__(self, status: int, payload):
        self.status = status
        self.payload = payload
        super().__init__(str(payload))


def http_json(method: str, url: str, body: dict | None = None, timeout: float = 180.0):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw) if raw.strip() else {"detail": raw}
        except json.JSONDecodeError:
            payload = {"detail": raw}
        raise UpstreamError(exc.code, payload) from exc
    except urllib.error.URLError as exc:
        raise UpstreamError(0, {"detail": f"UPSTREAM_UNREACHABLE: {exc.reason}"}) from exc
    except TimeoutError:
        raise UpstreamError(0, {"detail": "UPSTREAM_TIMEOUT"}) from exc


def read_latest() -> dict | None:
    if not LATEST_PAIR.exists():
        return None
    try:
        return json.loads(LATEST_PAIR.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_latest(pair: dict) -> None:
    tmp = LATEST_PAIR.with_suffix(".tmp")
    tmp.write_text(json.dumps(pair, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(LATEST_PAIR)


def extract_state_questions(body: dict) -> tuple:
    return body.get("state"), body.get("questions")


class Handler(BaseHTTPRequestHandler):
    server_version = "MR-P16P17-Bridge/1.0"

    def log_message(self, fmt, *args):  # 静音默认日志，改为简洁输出
        sys.stderr.write("[%s] %s\n" % (datetime.now(CST).strftime("%H:%M:%S"), fmt % args))

    # ---------- 基础工具 ----------
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def _json(self, status: int, payload):
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    # ---------- 路由 ----------
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            return self._proxy_get("/health")
        if path == "/api/models":
            return self._proxy_get("/models")
        if path == "/api/metrics":
            return self._proxy_get("/metrics")
        if path == "/api/config":
            return self._json(200, {
                "upstream": UPSTREAM,
                "upstream_display": urllib.parse.urlparse(UPSTREAM).netloc,
                "server_time": now_iso(),
                "runs_dir": str(RUNS.name),
            })
        if path == "/api/latest":
            pair = read_latest()
            if pair is None:
                return self._json(404, {"detail": "NO_PAIR_YET"})
            return self._json(200, pair)
        if path == "/api/history":
            items = []
            for file in sorted(RUNS.glob("*.json"), reverse=True):
                if file.name == "latest_pair.json":
                    continue
                items.append({"file": file.name, "size": file.stat().st_size})
            return self._json(200, {"items": items[:50]})

        return self._serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/systemone":
            return self._handle_systemone()
        if parsed.path == "/api/pair":
            return self._handle_pair()
        return self._json(404, {"detail": "NOT_FOUND"})

    # ---------- 代理 ----------
    def _proxy_get(self, upstream_path: str):
        try:
            status, payload = http_json("GET", UPSTREAM + upstream_path, timeout=10)
            payload = dict(payload) if isinstance(payload, dict) else {"data": payload}
            payload["_bridge"] = {"upstream": urllib.parse.urlparse(UPSTREAM).netloc, "fetched_at": now_iso()}
            return self._json(status, payload)
        except UpstreamError as exc:
            return self._json(502 if exc.status == 0 else exc.status, {
                "detail": exc.payload.get("detail", str(exc.payload)) if isinstance(exc.payload, dict) else str(exc.payload),
                "error_class": "UPSTREAM_UNREACHABLE" if exc.status == 0 else "UPSTREAM_ERROR",
                "upstream": urllib.parse.urlparse(UPSTREAM).netloc,
                "at": now_iso(),
            })

    def _handle_systemone(self):
        body = self._read_json()
        if not isinstance(body, dict):
            return self._json(400, {"detail": "INVALID_JSON"})

        family = (body.get("router_family") or body.get("model") or "laya").lower()
        test_id = body.pop("test_id", None) or uuid.uuid4().hex[:12]
        started = time.perf_counter()

        try:
            status, payload = http_json("POST", UPSTREAM + "/system-one", body, timeout=180)
        except UpstreamError as exc:
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            record = {
                "test_id": test_id,
                "family": family,
                "request": body,
                "response": None,
                "error": exc.payload,
                "http_status": exc.status,
                "bridge_elapsed_ms": elapsed,
                "completed_at": now_iso(),
            }
            self._save_run(record, family)
            error_payload = exc.payload if isinstance(exc.payload, dict) else {"detail": str(exc.payload)}
            return self._json(502 if exc.status == 0 else exc.status, {
                **error_payload,
                "error_class": "UPSTREAM_UNREACHABLE" if exc.status == 0 else "UPSTREAM_ERROR",
                "test_id": test_id,
                "completed_at": record["completed_at"],
            })

        elapsed = round((time.perf_counter() - started) * 1000, 2)
        record = {
            "test_id": test_id,
            "family": family,
            "request": body,
            "response": payload,
            "error": None,
            "http_status": status,
            "bridge_elapsed_ms": elapsed,
            "completed_at": now_iso(),
        }
        self._save_run(record, family)

        out = dict(payload) if isinstance(payload, dict) else {"data": payload}
        out["test_id"] = test_id
        out["bridge_elapsed_ms"] = elapsed
        out["completed_at"] = record["completed_at"]
        return self._json(status, out)

    def _handle_pair(self):
        """同一份 State / Questions，依次调用 Laya 与 Kev，并原子保存为同一轮。"""
        body = self._read_json()
        if not isinstance(body, dict):
            return self._json(400, {"detail": "INVALID_JSON"})

        state = body.get("state")
        questions = body.get("questions")
        if state is None or not isinstance(questions, dict) or not questions:
            return self._json(400, {"detail": "MISSING_STATE_OR_QUESTIONS"})

        test_id = body.get("test_id") or "MR-" + datetime.now(CST).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4]
        selected = body.get("families") or ["laya", "kev"]

        results = {}
        started_all = now_iso()
        for family in selected:
            family = str(family).lower()
            payload = {"router_family": family, "state": state, "questions": questions}
            started = time.perf_counter()
            try:
                _, response = http_json("POST", UPSTREAM + "/system-one", payload, timeout=240)
                results[family] = {
                    "ok": True,
                    "request": payload,
                    "response": response,
                    "http_status": 200,
                    "error": None,
                    "bridge_elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                }
            except UpstreamError as exc:
                results[family] = {
                    "ok": False,
                    "request": payload,
                    "response": None,
                    "http_status": exc.status,
                    "error": exc.payload,
                    "error_class": "UPSTREAM_UNREACHABLE" if exc.status == 0 else "UPSTREAM_ERROR",
                    "bridge_elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                }

        pair = {
            "test_id": test_id,
            "state": state,
            "questions": questions,
            "families": selected,
            "results": results,
            "started_at": started_all,
            "completed_at": now_iso(),
            "upstream": urllib.parse.urlparse(UPSTREAM).netloc,
        }

        with LOCK:
            write_latest(pair)
            (RUNS / f"pair_{stamp()}_{test_id}.json").write_text(
                json.dumps(pair, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        all_ok = all(r["ok"] for r in results.values())
        return self._json(200 if all_ok else 207, pair)

    # ---------- 存档 ----------
    def _save_run(self, record: dict, family: str) -> None:
        with LOCK:
            name = f"{stamp()}_{family}_{record['test_id']}.json"
            (RUNS / name).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- 静态 ----------
    def _serve_static(self, path: str):
        if path in ("", "/"):
            path = "/interactive/P16.html"
        rel = urllib.parse.unquote(path).lstrip("/")
        target = (ROOT / rel).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            return self._json(403, {"detail": "FORBIDDEN"})
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            return self._json(404, {"detail": f"FILE_NOT_FOUND: {rel}"})

        ctype, _ = mimetypes.guess_type(str(target))
        ctype = ctype or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        raw = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)


UPSTREAM = DEFAULT_UPSTREAM


def main():
    global UPSTREAM
    parser = argparse.ArgumentParser(description="P16/P17 真实双模型 Demo 桥接服务")
    parser.add_argument("--port", type=int, default=8775)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--upstream", default=None, help="A6000 服务基址，例如 http://127.0.0.1:8000")
    args = parser.parse_args()

    UPSTREAM = (args.upstream or os.environ.get("MR_UPSTREAM") or load_upstream()).rstrip("/")

    host_display = urllib.parse.urlparse(UPSTREAM).netloc
    print("=" * 62)
    print("ModelRouter P16/P17 真实双模型 Demo")
    print(f"  上游服务 : {host_display}")
    print(f"  本地入口 : http://{args.host}:{args.port}/interactive/P16.html")
    print(f"  结果存档 : {RUNS}")
    print("=" * 62)

    try:
        status, _ = http_json("GET", UPSTREAM + "/health", timeout=5)
        if status == 200:
            print("[OK] 上游 /health 可达")
    except UpstreamError as exc:
        print(f"[WARN] 上游当前不可达：{exc.payload}；页面会显示真实的断连状态。")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
