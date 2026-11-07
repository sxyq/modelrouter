"""Legacy import path for the canonical unified-view builder."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.views import build_unified_training_and_evaluation_views, validate_kev_exports

