"""Legacy trajectory imports use the existing package implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project/code/src"))

from modelrouter.data_pipeline.sources.tra import *
