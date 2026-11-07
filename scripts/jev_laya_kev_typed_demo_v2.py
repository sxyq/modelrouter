#!/usr/bin/env python3
"""Compatibility CLI for the canonical typed decision demo."""
from __future__ import annotations

import runpy
from pathlib import Path

_DEMO = Path(__file__).resolve().parents[1] / "jev_laya_kev_typed_demo_v2.py"

if __name__ == "__main__":
    runpy.run_path(str(_DEMO), run_name="__main__")
