"""Backward-compatibility shim for modelrouter.serving.kev_adapter."""
import os
import sys

_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "our-project", "code", "src"))
if os.path.isdir(_src_dir) and _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from modelrouter.serving.kev_adapter import *
from modelrouter.serving.kev_adapter import KevAdapter
