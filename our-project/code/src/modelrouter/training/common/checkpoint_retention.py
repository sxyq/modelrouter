"""Compatibility import for the maintained router_data retention module."""
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from router_data import checkpoint_retention as _implementation

if __name__ != "__main__":
    sys.modules[__name__] = _implementation
