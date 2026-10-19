#!/usr/bin/env python3
"""
supervision_loaders.py - Multi-View Supervision Loaders for ModelRouter Training & Validation.

Supports flexible combinations:
- S1 (Human Preference / Oracle Routing Choice)
- S1+S2 (Preference + Agent Trajectory Resolved)
- S1+S3 (Preference + Cache Reuse Opportunity)
- S1+S2+S3 (Full Multi-Task Multi-View Formulation)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from modelrouter.datasets.causal_schema import SupervisionType
from modelrouter.datasets.public_sources import PublicDatasetLoader

logger = logging.getLogger("modelrouter.training.supervision_loaders")


@dataclass
class SupervisionBatch:
    batch_type: str
    records: List[Dict[str, Any]]
    supervision_types: List[SupervisionType]

    @property
    def size(self) -> int:
        return len(self.records)


class MultiViewSupervisionLoader:
    """CPU-friendly data loader constructing batched views for training and evaluation."""

    def __init__(self, dataset_loader: Optional[PublicDatasetLoader] = None):
        self.dataset_loader = dataset_loader or PublicDatasetLoader()

    def get_s1_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads S1 Routing Choice / Preference records (ROUTE-004, ROUTE-002, ROUTE-001)."""
        recs = []
        for sid in ["ROUTE-004", "ROUTE-002"]:
            for r in self.dataset_loader.iter_preview_samples(sid):
                recs.append(r)
                if limit and len(recs) >= limit:
                    return recs
        return recs

    def get_s2_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads S2 Agent Outcome records (TRA-001, TRA-002, TRA-004)."""
        recs = []
        for sid in ["TRA-001", "TRA-002"]:
            for r in self.dataset_loader.iter_preview_samples(sid):
                recs.append(r)
                if limit and len(recs) >= limit:
                    return recs
        return recs

    def get_s3_records(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads S3 Cache / System Auxiliary records (CACHE-001, TIME-001)."""
        recs = []
        for sid in ["CACHE-001", "TIME-001"]:
            for r in self.dataset_loader.iter_preview_samples(sid):
                recs.append(r)
                if limit and len(recs) >= limit:
                    return recs
        return recs

    def build_combination(
        self,
        combination_name: str,
        batch_size: int = 32,
        max_samples_per_view: Optional[int] = None,
    ) -> Iterator[SupervisionBatch]:
        """
        Builds multi-task batches for:
        - 'S1'
        - 'S1+S2'
        - 'S1+S3'
        - 'S1+S2+S3'
        """
        pools: List[Tuple[SupervisionType, List[Dict[str, Any]]]] = []

        if "S1" in combination_name:
            pools.append((SupervisionType.S1_HUMAN_PREFERENCE, self.get_s1_records(max_samples_per_view)))
        if "S2" in combination_name:
            pools.append((SupervisionType.S2_AGENT_OUTCOME, self.get_s2_records(max_samples_per_view)))
        if "S3" in combination_name:
            pools.append((SupervisionType.S3_AUXILIARY_SYSTEM, self.get_s3_records(max_samples_per_view)))

        if not pools:
            raise ValueError(f"Unknown combination: {combination_name}")

        # Interleave records evenly
        all_records = []
        max_len = max(len(recs) for _, recs in pools) if pools else 0
        for i in range(max_len):
            for stype, recs in pools:
                if i < len(recs):
                    all_records.append((stype, recs[i]))

        # Yield in batches
        for start_idx in range(0, len(all_records), batch_size):
            chunk = all_records[start_idx : start_idx + batch_size]
            batch_recs = [r for _, r in chunk]
            batch_stypes = list(set(st for st, _ in chunk))
            yield SupervisionBatch(
                batch_type=combination_name,
                records=batch_recs,
                supervision_types=batch_stypes,
            )
