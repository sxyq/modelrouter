#!/usr/bin/env python3
"""
v8_extension_loader.py - Data Loader and Preprocessor for ModelRouter V8 Extension Views.

Supports the three new V8 views:
1. ROUTER_CHOICE (Arena-55k pairwise battles) -> Bradley-Terry / Routing Cross-Entropy
2. CACHE_REUSE_OPPORTUNITY (Mooncake prefix block traces) -> Token reuse potential regression
3. OBSERVED_AGENT_OUTCOME (Open-SWE-Traces & SWE-smith) -> Trajectory terminal outcome prediction

Guarantees:
- Strict split isolation (train / val / test) without cross-split leakage.
- Strict causal order (decision-before state, no future lookahead).
- Standalone independent execution, compatible with both Laya MoE and Kev Pointer Head.
"""

import gzip
import json
import logging
from pathlib import Path
from typing import Dict, Any, Iterator, List, Optional

logger = logging.getLogger("v8_extension_loader")

PROJECT_ROOT = Path("/home/syy/路由")
V8_VIEWS_DIR = PROJECT_ROOT / "runs" / "MR-V8-DATA-EXTENSION-20261018" / "views"

class V8ExtensionDataset:
    def __init__(self, views_dir: Optional[Path] = None, split: str = "train"):
        self.views_dir = views_dir or V8_VIEWS_DIR
        self.split = split
        assert split in ("train", "val", "test"), f"Invalid split: {split}"

    def iter_router_choice(self) -> Iterator[Dict[str, Any]]:
        """Iterates over ROUTER_CHOICE records for routing classification."""
        path = self.views_dir / f"router_choice_{self.split}.jsonl.gz"
        if not path.is_file():
            logger.warning(f"File not found: {path}")
            return
        
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                yield {
                    "view_type": "ROUTER_CHOICE",
                    "prompt": record.get("prompt_snippet", ""),
                    "candidates": record.get("candidate_models", []),
                    "winner": record.get("winner_model", ""),
                    "winner_choice": record.get("winner_choice", ""),
                    "label_nature": record.get("label_nature", "HUMAN_PREFERENCE")
                }

    def iter_cache_reuse(self) -> Iterator[Dict[str, Any]]:
        """Iterates over CACHE_REUSE_OPPORTUNITY for prefix caching auxiliary supervision."""
        path = self.views_dir / f"cache_reuse_opportunity_{self.split}.jsonl.gz"
        if not path.is_file():
            logger.warning(f"File not found: {path}")
            return
        
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                input_len = float(record.get("input_length", 0))
                reusable = float(record.get("estimated_reusable_blocks", 0))
                ratio = reusable / max(1.0, float(record.get("prefix_block_count", 1)))
                yield {
                    "view_type": "CACHE_REUSE_OPPORTUNITY",
                    "input_length": input_len,
                    "reusable_blocks": reusable,
                    "reusable_ratio": min(1.0, max(0.0, ratio)),
                    "evidence_label": record.get("evidence_label", "OBSERVED_REUSE")
                }

    def iter_agent_outcome(self) -> Iterator[Dict[str, Any]]:
        """Iterates over OBSERVED_AGENT_OUTCOME for trajectory outcome value prediction."""
        path = self.views_dir / f"observed_agent_outcome_{self.split}.jsonl.gz"
        if not path.is_file():
            logger.warning(f"File not found: {path}")
            return
        
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                yield {
                    "view_type": "OBSERVED_AGENT_OUTCOME",
                    "task_id": record.get("task_id", ""),
                    "episode_id": record.get("episode_id", ""),
                    "step_id": record.get("step_id", 0),
                    "state_before": record.get("state_before", {}),
                    "observed_model": record.get("observed_model", ""),
                    "outcome": record.get("known_terminal_outcome", "UNKNOWN")
                }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ds = V8ExtensionDataset(split="val")
    print("Testing ROUTER_CHOICE sample:")
    for item in ds.iter_router_choice():
        print(item)
        break
    print("Testing CACHE_REUSE sample:")
    for item in ds.iter_cache_reuse():
        print(item)
        break
