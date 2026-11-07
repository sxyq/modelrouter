"""Compatibility import for the canonical training retention API."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "our-project" / "code" / "src"
if str(_ROOT) not in sys.path: sys.path.insert(0, str(_ROOT))
if str(_SRC) not in sys.path: sys.path.insert(0, str(_SRC))
from modelrouter.training.common import checkpoint_retention as _implementation

sys.modules[__name__] = _implementation
