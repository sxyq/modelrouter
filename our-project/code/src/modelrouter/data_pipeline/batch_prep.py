"""Public data-preparation API assembled from its single-purpose modules."""

from .batch_examples import (
    _dump, _example, _neutral_instruction, _rewrite_materialized_row,
    _source_rows, _unit, _use,
)
from .batch_constants import (
    FULL_COMBOS, FULL_LAYERS, FULL_POLICIES, FULL_QUALITY,
    MATRIX_ALLOWED_SOURCES, MATRIX_TARGETS,
)
from .matrix import (
    _build_matrix_coverage, _copy_rewritten_jsonl, _matrix_materialize,
    _matrix_ref, _matrix_select, _matrix_unit, prepare_full_matrix,
)
from .batch_materialization import (
    _batch1_pick_one_per_unit, _batch1_priority, _batch1_ref_targets,
    prepare_batch1, run_batch_prep, validate_representatives,
)
from .sweep import _sweep_audit, _sweep_rows, _sweep_sample, _sweep_write_rows, prepare_sweep02
from .full_coverage import (
    FULL_COVERAGE_SERIES_DEFS, ROUTING_ALIGNED_VIEWS, collect_full_coverage_refs,
    get_full_coverage_plan_spec, materialize_full_coverage_chunk,
    prepare_full_coverage_manifest,
)
