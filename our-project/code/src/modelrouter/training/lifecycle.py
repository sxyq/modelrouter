#!/usr/bin/env python3
"""
lifecycle.py - Candidate Training Lifecycle Management for ModelRouter.

Strictly manages transitions between candidate stages:
ZERO_SHOT -> AUX_SMOKE -> POINTER_HEAD_PILOT -> LORA_FINETUNE -> FULL_RUN -> VALIDATED.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("modelrouter.training.lifecycle")

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
STAGES_CONFIG_PATH = WORKSPACE_ROOT / "our-project" / "experiments" / "configs" / "training_stages.json"


class CandidateStage(str, Enum):
    ZERO_SHOT = "ZERO_SHOT"
    AUX_SMOKE = "AUX_SMOKE"
    POINTER_HEAD_PILOT = "POINTER_HEAD_PILOT"
    LORA_FINETUNE = "LORA_FINETUNE"
    FULL_RUN = "FULL_RUN"
    VALIDATED = "VALIDATED"


VALID_TRANSITIONS: Dict[CandidateStage, Set[CandidateStage]] = {
    CandidateStage.ZERO_SHOT: {CandidateStage.AUX_SMOKE, CandidateStage.POINTER_HEAD_PILOT},
    CandidateStage.AUX_SMOKE: {CandidateStage.POINTER_HEAD_PILOT, CandidateStage.LORA_FINETUNE},
    CandidateStage.POINTER_HEAD_PILOT: {CandidateStage.LORA_FINETUNE, CandidateStage.FULL_RUN},
    CandidateStage.LORA_FINETUNE: {CandidateStage.FULL_RUN},
    CandidateStage.FULL_RUN: {CandidateStage.VALIDATED},
    CandidateStage.VALIDATED: set(),
}


class CandidateLifecycleTracker:
    """Tracks and validates stages for router model candidates."""

    def __init__(self, candidate_id: str, initial_stage: CandidateStage = CandidateStage.ZERO_SHOT):
        self.candidate_id = candidate_id
        self.current_stage = initial_stage
        self.history: List[Dict[str, Any]] = [
            {
                "stage": initial_stage.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": {},
                "note": "Initialized candidate lifecycle",
            }
        ]

    def can_transition_to(self, target_stage: CandidateStage) -> bool:
        return target_stage in VALID_TRANSITIONS.get(self.current_stage, set())

    def transition_to(
        self,
        target_stage: CandidateStage,
        metrics: Optional[Dict[str, Any]] = None,
        note: str = "",
    ) -> bool:
        if not self.can_transition_to(target_stage):
            raise ValueError(
                f"Invalid transition from {self.current_stage.value} to {target_stage.value}. "
                f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(self.current_stage, set())]}"
            )

        self.current_stage = target_stage
        record = {
            "stage": target_stage.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics or {},
            "note": note,
        }
        self.history.append(record)
        logger.info(f"Candidate {self.candidate_id} transitioned to {target_stage.value}")
        return True

    def get_summary(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "current_stage": self.current_stage.value,
            "history_length": len(self.history),
            "history": self.history,
        }
