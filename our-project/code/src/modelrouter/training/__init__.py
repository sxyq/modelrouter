#!/usr/bin/env python3
"""
modelrouter.training - ModelRouter Training Recipes, Lifecycle, and Metric Parsers.
"""

from modelrouter.training.lifecycle import (
    CandidateStage,
    CandidateLifecycleTracker,
    VALID_TRANSITIONS,
)
from modelrouter.training.metric_parsers import (
    S1MetricParser,
    S2MetricParser,
    S3MetricParser,
    KevFixedValParser,
)
from modelrouter.training.supervision_loaders import (
    MultiViewSupervisionLoader,
    SupervisionBatch,
)

__all__ = [
    "CandidateStage",
    "CandidateLifecycleTracker",
    "VALID_TRANSITIONS",
    "S1MetricParser",
    "S2MetricParser",
    "S3MetricParser",
    "KevFixedValParser",
    "MultiViewSupervisionLoader",
    "SupervisionBatch",
]
