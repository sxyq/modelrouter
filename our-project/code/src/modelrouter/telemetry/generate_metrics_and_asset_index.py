#!/usr/bin/env python3
"""Use the existing training-history publisher from the previous generation entry."""
import json
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[5])
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from scripts import fetch_live_status as _implementation


def audit_all():
    return _implementation.build_training_history()


if __name__ == "__main__":
    history = audit_all()
    print(json.dumps({"counts": history["counts"],
                      "history": "shards/training_history.json"}, ensure_ascii=False))
