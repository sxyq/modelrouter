#!/usr/bin/env python3
"""
validation.py - Stream Validator for Causal Schema & Dataset Integrity.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List, Tuple

from modelrouter.datasets.causal_schema import validate_causal_isolation, FORBIDDEN_PRE_DECISION_KEYS

logger = logging.getLogger("modelrouter.data_pipeline.validation")


class CausalStreamValidator:
    """Validates records in streaming workflows without loading all into memory."""

    def __init__(self, raise_on_error: bool = False):
        self.raise_on_error = raise_on_error
        self.total_checked = 0
        self.total_errors = 0
        self.error_counts_by_reason: Dict[str, int] = {}

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        self.total_checked += 1
        is_valid, reasons = validate_causal_isolation(record)

        if not is_valid:
            self.total_errors += 1
            for r in reasons:
                self.error_counts_by_reason[r] = self.error_counts_by_reason.get(r, 0) + 1
            if self.raise_on_error:
                raise ValueError(f"Causal validation error: {reasons}")

        return is_valid, reasons

    def filter_valid_records(self, stream: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """Yields only causally valid records from an iterator."""
        for rec in stream:
            is_valid, _ = self.validate_record(rec)
            if is_valid:
                yield rec

    def summary(self) -> Dict[str, Any]:
        return {
            "total_checked": self.total_checked,
            "total_errors": self.total_errors,
            "pass_rate": (
                (self.total_checked - self.total_errors) / self.total_checked
                if self.total_checked > 0
                else 1.0
            ),
            "errors_by_reason": self.error_counts_by_reason,
        }
