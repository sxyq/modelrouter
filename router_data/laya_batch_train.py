"""Compatibility import and CLI for modelrouter.training.laya.laya_batch_train."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "our-project" / "code" / "src"
if str(_ROOT) not in sys.path: sys.path.insert(0, str(_ROOT))
if str(_SRC) not in sys.path: sys.path.insert(0, str(_SRC))
from modelrouter.training.laya import laya_batch_train as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
