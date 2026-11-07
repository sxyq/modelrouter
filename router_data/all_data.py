"""Legacy import path for the canonical data-view materializer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.sources.all_data import *
from modelrouter.data_pipeline.sources.all_data import _map_action_category, _variable_refs
from modelrouter.data_pipeline.sources.all_data_shared import (
    _dump, _load_stage1_reference, _prompt, _route001_groups, _routerbench_prompts,
    _semantic_split, _shuffled_criteria, _soft_distribution, _split, _stage_dir,
)
from modelrouter.data_pipeline.sources.all_data_stage1 import _build_stage1_all_views
from modelrouter.data_pipeline.sources.all_data_adapters import (
    _build_stage2_adapters, _build_stage3_adapters, _build_stage4_adapters,
)

