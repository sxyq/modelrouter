"""Full-coverage plan definitions, reference collection, and chunk materialization."""

import csv
import gzip
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Optional

from modelrouter.data_pipeline.quality.quality_v2 import OWN_FILES, PUBLIC_FILES
from .batch_constants import MATRIX_ALLOWED_SOURCES, MATRIX_TARGETS
from .batch_examples import _dump, _example, _rewrite_materialized_row


FULL_COVERAGE_SERIES_DEFS = {
    # 1. Pure S1 Routing Full Coverage (31,766 total S1 candidate items across L1..L4)
    "F01_S1": {
        "run_id": "F01_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% Pure S1 Routing Full Coverage (4,592 records)",
    },
    "F02_S1": {
        "run_id": "F02_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% Pure S1 Routing Full Coverage (9,170 records)",
    },
    "F03_S1": {
        "run_id": "F03_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% Pure S1 Routing Full Coverage (13,780 records)",
    },
    "F04_S1": {
        "run_id": "F04_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% Pure S1 Routing Full Coverage (4,224 records)",
    },
    "F05_S1": {
        "run_id": "F05_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% Pure S1 Routing Cumulative Coverage (13,762 records)",
    },
    "F06_S1": {
        "run_id": "F06_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% Pure S1 Routing Cumulative Coverage (27,542 records)",
    },
    "F07_S1": {
        "run_id": "F07_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% Pure S1 Routing Grand Total Coverage (31,766 records)",
    },

    # 2. Single-Layer Full Coverage (F01..F04, All Supervisable Classes S1+S2+S3)
    "F01": {
        "run_id": "F01",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% All Supervision Full Coverage (485,210 records)",
    },
    "F02": {
        "run_id": "F02",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% All Supervision Full Coverage (1,001,005 records)",
    },
    "F03": {
        "run_id": "F03",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% All Supervision Full Coverage (1,466,724 records)",
    },
    "F04": {
        "run_id": "F04",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% All Supervision Full Coverage (1,910,961 records)",
    },

    # 3. Cumulative Full Coverage (F05..F07)
    "F05": {
        "run_id": "F05",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% All Supervision Cumulative Coverage (1,486,215 records)",
    },
    "F06": {
        "run_id": "F06",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% All Supervision Cumulative Coverage (2,952,939 records)",
    },
    "F07": {
        "run_id": "F07",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% All Supervision Grand Total Full Coverage (4,863,900 records)",
    },

    # 4. Fractional Scale with Nested Subsets (F08..F16)
    "F08": {
        "run_id": "F08",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 25% Nested Subset",
    },
    "F09": {
        "run_id": "F09",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 50% Nested Subset",
    },
    "F10": {
        "run_id": "F10",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 75% Nested Subset",
    },
    "F11": {
        "run_id": "F11",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 25% Nested Subset",
    },
    "F12": {
        "run_id": "F12",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 50% Nested Subset",
    },
    "F13": {
        "run_id": "F13",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 75% Nested Subset",
    },
    "F14": {
        "run_id": "F14",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 25% Nested Subset",
    },
    "F15": {
        "run_id": "F15",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 50% Nested Subset",
    },
    "F16": {
        "run_id": "F16",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 75% Nested Subset",
    },

    # 5. Curriculum Chaining (F17..F20)
    "F17": {
        "run_id": "F17",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F01",
        "epochs": 2,
        "description": "Curriculum Step 1: Warm start from F01 best, train on L2 100%",
    },
    "F18": {
        "run_id": "F18",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F17",
        "epochs": 2,
        "description": "Curriculum Step 2: Warm start from F17 best, train on L3 100%",
    },
    "F19": {
        "run_id": "F19",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F18",
        "epochs": 2,
        "description": "Curriculum Step 3: Warm start from F18 best, train on L4 100%",
    },
    "F20": {
        "run_id": "F20",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F19",
        "epochs": 2,
        "description": "Curriculum High-Quality Final Adaptation: Warm start from F19 best, re-adapt on L1 100%",
    },

    # 6. Pure S3 Auxiliary Full Coverage (F01_S3..F07_S3)
    "F01_S3": {
        "run_id": "F01_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% Pure S3 Auxiliary Full Coverage (132,805 records)",
    },
    "F02_S3": {
        "run_id": "F02_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% Pure S3 Auxiliary Full Coverage (265,642 records)",
    },
    "F03_S3": {
        "run_id": "F03_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% Pure S3 Auxiliary Full Coverage (398,215 records)",
    },
    "F04_S3": {
        "run_id": "F04_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% Pure S3 Auxiliary Full Coverage (497,517 records)",
    },
    "F05_S3": {
        "run_id": "F05_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% Pure S3 Auxiliary Cumulative Coverage (398,447 records)",
    },
    "F06_S3": {
        "run_id": "F06_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% Pure S3 Auxiliary Cumulative Coverage (796,662 records)",
    },
    "F07_S3": {
        "run_id": "F07_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% Pure S3 Auxiliary Grand Total Coverage (1,294,179 records)",
    },

    # 7. ROUTING-ALIGNED Series (ALGN_01..ALGN_04) under MR-ROUTING-ALIGNED-DATA-v2
    "ALGN_01_S1": {
        "run_id": "ALGN_01_S1",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "ratios": {"S1": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1: Static Model Preference (ROUTE-004 LMSYS Arena pairwise) single-task full coverage",
    },
    "ALGN_02_S1_S2": {
        "run_id": "ALGN_02_S1_S2",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1_s2",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2"],
        "groups": ["S1", "S2"],
        "ratios": {"S1": 2.0, "S2": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+2: Static Model Preference (S1) + Observed Agent Outcome (S2 TRA-001/002) balanced 2:1",
    },
    "ALGN_03_S1_S3": {
        "run_id": "ALGN_03_S1_S3",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1_s3",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S3"],
        "groups": ["S1", "S3"],
        "ratios": {"S1": 2.0, "S3": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+3: Static Model Preference (S1) + Resource Cache Auxiliary (S3 TIME/CACHE/OWN) balanced 2:1",
    },
    "ALGN_04_S1_S2_S3": {
        "run_id": "ALGN_04_S1_S2_S3",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_tri",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "ratios": {"S1": 2.0, "S2": 1.0, "S3": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+2+3: Routing Preference + Agent Outcome + Resource Auxiliary balanced 2:1:1",
    },
}

ROUTING_ALIGNED_VIEWS = {
    "STATIC_MODEL_PREFERENCE": {
        "view_id": "STATIC_MODEL_PREFERENCE",
        "supervision_class": "S1",
        "sources": ["ROUTE-004"],
        "primary_targets": ["human_pairwise_preference"],
        "eligible_record_count": 31766,
        "status": "READY",
        "description": "Human pairwise preference on LMSYS Chatbot Arena battles",
    },
    "OBSERVED_AGENT_OUTCOME": {
        "view_id": "OBSERVED_AGENT_OUTCOME",
        "supervision_class": "S2",
        "sources": ["TRA-001", "TRA-002"],
        "primary_targets": ["observed_action"],
        "eligible_record_count": 3537955,
        "status": "READY",
        "description": "Agent trajectory step actions and outcomes in coding environments",
    },
    "RESOURCE_CACHE_AUXILIARY": {
        "view_id": "RESOURCE_CACHE_AUXILIARY",
        "supervision_class": "S3",
        "sources": ["TIME-001", "CACHE-001", "OWN-002"],
        "primary_targets": ["request_response_tokens", "output_token_length", "call_quota_units"],
        "eligible_record_count": 1294179,
        "status": "READY",
        "description": "Inference resource consumption, response length, and cache tier auxiliary supervision",
    },
    "JOINT_ROUTING_COMPARISON": {
        "view_id": "JOINT_ROUTING_COMPARISON",
        "supervision_class": "JOINT",
        "sources": [],
        "primary_targets": [],
        "eligible_record_count": 0,
        "status": "DATA_NOT_READY",
        "description": "Concurrent multi-objective routing (Arena preference + SWE outcome + Mooncake cache). No authentic joint records exist across disparate sources; synthetic cross-benchmark pairing strictly prohibited.",
    },
}

def get_full_coverage_plan_spec(run_id: str) -> Optional[dict]:
    """Return plan configuration for a Full Coverage run."""
    spec = FULL_COVERAGE_SERIES_DEFS.get(run_id)
    if not spec:
        return None
    res = dict(spec)
    if run_id.startswith("ALGN_"):
        res["protocol_version"] = "MR-ROUTING-ALIGNED-v2"
    else:
        res["protocol_version"] = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
    res["legacy_input_protocol"] = False
    res["status"] = "ELIGIBLE"
    return res

def collect_full_coverage_refs(
    graded_root: str,
    layers: list,
    layer_fractions: dict,
    supervision_classes: list,
    seed: int = 42,
) -> tuple:
    """Scan V2.1 gzip index files and collect eligible candidate references.
    
    Applies deterministic hashing on independent units for fractional subsets,
    guaranteeing strict mathematical nesting: 25% subset of 50% subset of 75% subset of 100%.
    """
    graded_root = os.path.abspath(graded_root)
    sup_set = set(supervision_classes)
    collected = []
    census = {
        "by_layer": Counter(),
        "by_class": Counter(),
        "by_source": Counter(),
        "distinct_units": set(),
        "total_records": 0,
        "skipped_q3_q4": 0,
        "skipped_ineligible": 0,
        "skipped_disallowed_source": 0,
        "skipped_no_valid_target": 0,
    }

    for layer in layers:
        layer_num = layer[1:] if layer.startswith("L") else layer
        layer_dir = os.path.join(graded_root, f"level{layer_num}")
        if not os.path.isdir(layer_dir):
            continue
        fraction = float(layer_fractions.get(layer, 1.0))

        for src in sorted(MATRIX_ALLOWED_SOURCES):
            idx_file = os.path.join(layer_dir, f"{src}.jsonl.gz")
            if not os.path.isfile(idx_file):
                continue
            with gzip.open(idx_file, "rt", encoding="utf8") as f:
                for line in f:
                    rec = json.loads(line)
                    if rec.get("split") != "train":
                        continue
                    
                    # P0-2: Strict schema validation - require all mandatory fields.
                    for k in ("split", "train_eligible", "source_policy_train_allowed", "quality_grade", "primary_supervision_class"):
                        if k not in rec:
                            raise ValueError(f"SCHEMA_INCOMPATIBLE: Record in {idx_file} missing mandatory key '{k}'. Rebuild index before training.")

                    if rec["split"] != "train":
                        continue

                    if rec["train_eligible"] is not True:
                        census["skipped_ineligible"] = census.get("skipped_ineligible", 0) + 1
                        continue

                    if rec["source_policy_train_allowed"] is not True or src not in MATRIX_ALLOWED_SOURCES:
                        census["skipped_disallowed_source"] = census.get("skipped_disallowed_source", 0) + 1
                        continue

                    q_grade = rec["quality_grade"]
                    if q_grade not in {"Q1", "Q2"}:
                        census["skipped_q3_q4"] = census.get("skipped_q3_q4", 0) + 1
                        continue

                    sup = rec["primary_supervision_class"]
                    if sup not in sup_set:
                        continue

                    unit_id = rec.get("independent_unit_id") or rec.get("stable_record_id")
                    if fraction < 1.0:
                        unit_hash = int(hashlib.sha256(f"{src}:{unit_id}:{seed}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
                        if unit_hash >= fraction:
                            continue

                    # Strict target verification: MUST have real supervision evidence in candidate_targets.
                    # NO heuristic guessing from supervision class or source ID.
                    allowed_targets = MATRIX_TARGETS.get(sup, set())
                    target = rec.get("target")
                    cand_list = rec.get("candidate_targets") or []

                    valid_target = None
                    if target and target in allowed_targets and target in cand_list:
                        valid_target = target
                    elif cand_list:
                        valid_cands = [t for t in cand_list if t in allowed_targets]
                        if valid_cands:
                            valid_target = valid_cands[0]

                    if not valid_target:
                        census["skipped_no_valid_target"] = census.get("skipped_no_valid_target", 0) + 1
                        continue
                    target = valid_target

                    ref = {
                        "source_id": src,
                        "source_line": rec["source_line"],
                        "source_file": rec.get("source_file") or (PUBLIC_FILES.get(src) if src in PUBLIC_FILES else OWN_FILES.get(src, "")),
                        "stable_record_id": rec.get("stable_record_id"),
                        "independent_unit_id": unit_id,
                        "trajectory_id": rec.get("trajectory_id"),
                        "primary_supervision_class": sup,
                        "assigned_layer": layer,
                        "target": target,
                        "quality_grade": q_grade,
                        "split": "train",
                        "train_eligible": True,
                    }
                    collected.append(ref)
                    census["by_layer"][layer] += 1
                    census["by_class"][sup] += 1
                    census["by_source"][src] += 1
                    census["distinct_units"].add(unit_id)
                    census["total_records"] += 1

    return collected, census

def materialize_full_coverage_chunk(
    chunk_refs: list,
    chunk_dir: str,
    cleaned_root: str,
    project_root: str = ".",
) -> dict:
    """Materialize a single dynamic chunk of records into train/S1,S2,S3.jsonl without monolithic file creation."""
    os.makedirs(os.path.join(chunk_dir, "train"), exist_ok=True)
    # Group refs by source_id -> source_line
    by_src_line = defaultdict(lambda: defaultdict(list))
    for r in chunk_refs:
        by_src_line[r["source_id"]][r["source_line"]].append(r)

    stats = Counter()
    distinct_units = set()
    handles = {}

    try:
        for src in sorted(by_src_line):
            lines_map = by_src_line[src]
            max_line = max(lines_map.keys())
            if src in PUBLIC_FILES:
                path = os.path.join(cleaned_root, PUBLIC_FILES[src])
            else:
                own_rel = OWN_FILES.get(src, "")
                path = os.path.join(project_root, own_rel) if not os.path.isabs(own_rel) else own_rel

            if not os.path.isfile(path):
                continue

            min_line = min(lines_map.keys())
            max_line = max(lines_map.keys())
            target_line_set = set(lines_map.keys())

            with open(path, encoding='utf-8-sig', newline='') as f:
                if path.endswith('.csv'):
                    reader = csv.DictReader(f)
                    for line_no, raw in enumerate(reader, 2):
                        if line_no < min_line:
                            continue
                        if line_no > max_line:
                            break
                        if line_no in target_line_set:
                            for ref in lines_map[line_no]:
                                row = _example(src, raw, ref, ref["target"])
                                if row is None:
                                    continue
                                row = _rewrite_materialized_row(row)
                                sup_class = ref["primary_supervision_class"]
                                if sup_class not in handles:
                                    handles[sup_class] = open(
                                        os.path.join(chunk_dir, "train", f"{sup_class}.jsonl"),
                                        "w",
                                        encoding="utf8",
                                    )
                                handles[sup_class].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + "\n")
                                stats[sup_class] += 1
                                distinct_units.add(ref["independent_unit_id"])
                else:
                    for line_no, line in enumerate(f, 1):
                        if line_no < min_line:
                            continue
                        if line_no > max_line:
                            break
                        if line_no in target_line_set:
                            s = line.strip()
                            if not s:
                                continue
                            raw = json.loads(s)
                            for ref in lines_map[line_no]:
                                row = _example(src, raw, ref, ref["target"])
                                if row is None:
                                    continue
                                row = _rewrite_materialized_row(row)
                                sup_class = ref["primary_supervision_class"]
                                if sup_class not in handles:
                                    handles[sup_class] = open(
                                        os.path.join(chunk_dir, "train", f"{sup_class}.jsonl"),
                                        "w",
                                        encoding="utf8",
                                    )
                                handles[sup_class].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + "\n")
                                stats[sup_class] += 1
                                distinct_units.add(ref["independent_unit_id"])
    finally:
        for h in handles.values():
            h.close()

    return {
        "item_count": sum(stats.values()),
        "by_class": dict(stats),
        "distinct_units_count": len(distinct_units),
        "chunk_dir": chunk_dir,
    }

def prepare_full_coverage_manifest(
    graded_root: str,
    out_root: str,
) -> dict:
    """Generate the full coverage experiment manifest (full_coverage_manifest.json)."""
    graded_root = os.path.abspath(graded_root)
    out_root = os.path.abspath(out_root)
    os.makedirs(out_root, exist_ok=True)

    plans = {}
    for run_id, spec in FULL_COVERAGE_SERIES_DEFS.items():
        plan = dict(spec)
        if run_id.startswith("ALGN_"):
            plan["protocol_version"] = "MR-ROUTING-ALIGNED-v2"
        else:
            plan["protocol_version"] = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
        plan["legacy_input_protocol"] = False
        plan["status"] = "ELIGIBLE"
        plan["materialized"] = False
        plan["data"] = f"stream:{run_id}"
        plans[run_id] = plan

    manifest = {
        "experiment_id": "MR-FULL-DATA-CONTINUOUS-TRAINING",
        "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if "time" in globals() else "",
        "census": {
            "total_raw_records": 6821945,
            "eligible_candidate_records": 4863900,
            "layers": {
                "L1": {"total_records": 485210, "distinct_units": 139274, "S1": 4592, "S2": 347813, "S3": 132805},
                "L2": {"total_records": 1001005, "distinct_units": 278426, "S1": 9170, "S2": 726193, "S3": 265642},
                "L3": {"total_records": 1466724, "distinct_units": 417529, "S1": 13780, "S2": 1054729, "S3": 398215},
                "L4": {"total_records": 1910961, "distinct_units": 509011, "S1": 4224, "S2": 1409220, "S3": 497517},
            },
            "supervision": {
                "S1": 31766,
                "S2": 3537955,
                "S3": 1294179,
            },
        },
        "fixed_validation": {
            "root": "val",
            "S1": "val/S1.jsonl",
            "S2": "val/S2.jsonl",
            "S3": "val/S3.jsonl",
        },
        "plans": plans,
        "routing_aligned_views": ROUTING_ALIGNED_VIEWS,
    }
    manifest_path = os.path.join(out_root, "full_coverage_manifest.json")
    _dump(manifest_path, manifest)
    return manifest
