"""Legacy import path for the canonical batch preparation API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.batch_prep import *
from modelrouter.data_pipeline.batch_prep import (
    _batch1_pick_one_per_unit, _batch1_priority, _batch1_ref_targets,
    _build_matrix_coverage, _copy_rewritten_jsonl, _dump, _example,
    _matrix_materialize, _matrix_ref, _matrix_select, _matrix_unit,
    _neutral_instruction, _rewrite_materialized_row, _source_rows, _sweep_audit,
    _sweep_rows, _sweep_sample, _sweep_write_rows, _unit, _use,
)

