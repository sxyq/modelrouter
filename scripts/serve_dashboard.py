#!/usr/bin/env python3
"""
serve_dashboard.py - Dedicated Read-Only Web Server for ModelRouter Dashboard on A6000.

Specifications:
- Listens on 0.0.0.0:8765 (accessible via campus/LAN/VPN at http://10.16.15.202:8765/).
- Serves STRICTLY the sanitized site directory: /home/syy/路由/our-project/dashboard/.
- Never exposes project root, weights, training logs, private keys, or Router control APIs.
- Applies Cache-Control: no-store, no-cache, must-revalidate for JSON assets.
- Read-only: accepts ONLY GET, HEAD, and OPTIONS requests; rejects state-modifying requests.
- Runs purely in user space without requiring root/sudo privileges.
"""

import http.server
import logging
import os
import socketserver
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("serve_dashboard")

PORT = 8765
HOST = "0.0.0.0"

# Target directory on A6000
A6000_DASHBOARD_DIR = Path("/home/syy/路由/our-project/dashboard")
LOCAL_DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "our-project" / "dashboard"
SERVE_DIR = A6000_DASHBOARD_DIR if A6000_DASHBOARD_DIR.is_dir() else LOCAL_DASHBOARD_DIR


class DashboardServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Keep one slow browser connection from blocking all dashboard requests."""

    allow_reuse_address = True
    daemon_threads = True


class ReadOnlyNoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def do_POST(self):
        self.send_error(405, "Method Not Allowed: Dashboard is strictly read-only")

    def do_PUT(self):
        self.send_error(405, "Method Not Allowed: Dashboard is strictly read-only")

    def do_DELETE(self):
        self.send_error(405, "Method Not Allowed: Dashboard is strictly read-only")

    def end_headers(self):
        # Force fresh reads for dynamic status JSON files
        if self.path.endswith(".json") or "live_status" in self.path:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        else:
            self.send_header("Cache-Control", "public, max-age=60")
        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def log_message(self, format, *args):
        # Suppress noisy periodic poll logs, only log on errors or first requests
        if args and str(args[1]) in ("200", "304") and "live_status.json" in str(args[0]):
            return
        logger.info("%s - %s", self.client_address[0], format % args)


def main():
    if not SERVE_DIR.is_dir():
        logger.error("Dashboard directory does not exist: %s", SERVE_DIR)
        sys.exit(1)

    logger.info("Initializing ModelRouter Dashboard Server on %s:%d...", HOST, PORT)
    logger.info("Serving strictly from read-only directory: %s", SERVE_DIR)

    try:
        with DashboardServer((HOST, PORT), ReadOnlyNoCacheHandler) as httpd:
            logger.info("Dashboard active and listening at http://%s:%d/ (Target: http://10.16.15.202:%d/)", HOST, PORT, PORT)
            httpd.serve_forever()
    except Exception as e:
        logger.error("Failed to start server on %s:%d: %s", HOST, PORT, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
