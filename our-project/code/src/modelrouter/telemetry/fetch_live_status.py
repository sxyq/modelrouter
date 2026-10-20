"""Compatibility import and CLI for the maintained scripts status collector."""
import logging
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[5])
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from scripts import fetch_live_status as _implementation

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
