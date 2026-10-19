#!/usr/bin/env python3
"""
modelrouter.datasets - ModelRouter Dataset & Supervision Layer.
"""

from modelrouter.datasets.causal_schema import (
    CausalRecord,
    PreDecisionState,
    ObservedDecision,
    GroundTruthOutcome,
    Provenance,
    PolicyTag,
    SupervisionType,
    LabelNature,
    validate_causal_isolation,
)
from modelrouter.datasets.public_sources import (
    PUBLIC_SOURCES_REGISTRY,
    SourceMetadata,
    PublicDatasetLoader,
)
from modelrouter.datasets.audit import DatasetAuditor

__all__ = [
    "CausalRecord",
    "PreDecisionState",
    "ObservedDecision",
    "GroundTruthOutcome",
    "Provenance",
    "PolicyTag",
    "SupervisionType",
    "LabelNature",
    "validate_causal_isolation",
    "PUBLIC_SOURCES_REGISTRY",
    "SourceMetadata",
    "PublicDatasetLoader",
    "DatasetAuditor",
]
