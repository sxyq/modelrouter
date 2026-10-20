"""Compatibility import and CLI for the maintained router_data training queue."""
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from router_data import run_full_graded_queue as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation


