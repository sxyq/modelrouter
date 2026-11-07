#!/usr/bin/env python3
"""Compatibility CLI and import path for the canonical telemetry collector."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _WORKSPACE_ROOT / "our-project/code/src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from modelrouter.telemetry import fetch_live_status as _implementation

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
