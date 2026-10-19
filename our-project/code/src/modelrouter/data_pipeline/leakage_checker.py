#!/usr/bin/env python3
"""
leakage_checker.py - Cross-Split & Benchmark Task Leakage Detection.
"""

from __future__ import annotations

import re
import hashlib
from typing import Any, Dict, Iterable, List, Set, Tuple


def normalize_prompt(text: str) -> str:
    """Normalizes prompt text by lowercasing and removing non-alphanumeric punctuation."""
    t = (text or "").lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def prompt_hash(text: str) -> str:
    canon = normalize_prompt(text)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16] if canon else ""


class LeakageDetector:
    """Detects exact and canonical prompt/task leakage between datasets or splits."""

    def __init__(self):
        self.reference_task_ids: Set[str] = set()
        self.reference_prompt_hashes: Set[str] = set()
        self.reference_prompts_map: Dict[str, str] = {}

    def register_benchmark_tasks(self, task_ids: Iterable[str], prompts: Iterable[str] = ()):
        for tid in task_ids:
            if tid:
                self.reference_task_ids.add(str(tid).strip().lower())
        for p in prompts:
            h = prompt_hash(p)
            if h:
                self.reference_prompt_hashes.add(h)
                self.reference_prompts_map[h] = p[:100]

    def check_leakage(
        self, candidate_task_id: Optional[str], candidate_prompt: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """Returns (has_leakage, detail_string)."""
        if candidate_task_id:
            tid_clean = str(candidate_task_id).strip().lower()
            if tid_clean in self.reference_task_ids:
                return True, f"Exact task ID match: {tid_clean}"

        if candidate_prompt:
            h = prompt_hash(candidate_prompt)
            if h and h in self.reference_prompt_hashes:
                snippet = self.reference_prompts_map.get(h, "")
                return True, f"Normalized prompt hash match (hash={h}, snippet='{snippet}')"

        return False, None
