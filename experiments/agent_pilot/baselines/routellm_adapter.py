"""RouteLLM Baseline Adapter for Agent Pilot.

Implements RouteLLM threshold-based routing between cheap (Fast) and strong (Strong/Reasoning)
models based on multidimensional difficulty scoring and cost-quality calibration.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class RouteLLMScore:
    difficulty_score: float
    selected_tier: str  # "cheap" or "strong"
    calibrated_threshold: float
    confidence: float
    predicted_cost_usd: float
    feature_breakdown: Dict[str, float]


class RouteLLMAdapter:
    """Calculates multidimensional task/step difficulty and routes according to threshold theta."""

    def __init__(self, threshold: float = 0.55):
        self.threshold = threshold

    def compute_difficulty(
        self,
        instruction: str,
        history_steps: int,
        context_tokens: int,
        last_exit_code: int,
        tool_error_count: int,
    ) -> RouteLLMScore:
        features = {}

        # 1. Lexical / Prompt Complexity (0.0 - 0.3)
        code_keywords = len(re.findall(r"\b(def|class|import|return|function|git|docker|curl|eval|run)\b", instruction, re.IGNORECASE))
        lex_score = min(0.30, (len(instruction) / 1000.0) * 0.15 + (code_keywords / 10.0) * 0.15)
        features["lexical_complexity"] = round(lex_score, 4)

        # 2. Step Depth Complexity (0.0 - 0.25)
        depth_score = min(0.25, (history_steps / 15.0) * 0.25)
        features["depth_complexity"] = round(depth_score, 4)

        # 3. Execution Context & Error Pressure (0.0 - 0.35)
        err_score = 0.0
        if last_exit_code != 0:
            err_score += 0.20
        if tool_error_count > 0:
            err_score += min(0.15, tool_error_count * 0.05)
        features["error_pressure"] = round(err_score, 4)

        # 4. Context Window Pressure (0.0 - 0.10)
        ctx_score = min(0.10, (context_tokens / 8000.0) * 0.10)
        features["context_pressure"] = round(ctx_score, 4)

        total_score = min(1.0, lex_score + depth_score + err_score + ctx_score)
        tier = "strong" if total_score >= self.threshold else "cheap"

        # Confidence: distance from threshold
        dist = abs(total_score - self.threshold)
        conf = 0.5 + min(0.48, dist * 1.5)

        # Predicted step cost
        est_cost = 0.015 if tier == "strong" else 0.0008

        return RouteLLMScore(
            difficulty_score=round(total_score, 4),
            selected_tier=tier,
            calibrated_threshold=self.threshold,
            confidence=round(conf, 4),
            predicted_cost_usd=est_cost,
            feature_breakdown=features,
        )
