"""Legacy import path for canonical V2.1 quality classification."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.quality.quality_v2 import *

