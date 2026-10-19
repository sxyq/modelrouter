#!/usr/bin/env python3
"""
causal_schema.py - Strict Causal State-Outcome Separation Schema for ModelRouter.

Enforces fundamental scientific principles:
1. Pre-decision state (T/M/H) contains ONLY information observable BEFORE model routing.
2. Ground truth outcomes (S1/S2/S3) are strictly quarantined to post-execution records.
3. Zero causal leakage between future execution results and router inputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Set


class PolicyTag(str, Enum):
    TRAIN_ROUTER_CANDIDATE = "TRAIN_ROUTER_CANDIDATE"
    EVAL_BENCHMARK_ONLY = "EVAL_BENCHMARK_ONLY"
    RESEARCH_ANALYSIS_ONLY = "RESEARCH_ANALYSIS_ONLY"
    GATED_PENDING = "GATED_PENDING"


class LabelNature(str, Enum):
    HUMAN_PREFERENCE = "HUMAN_PREFERENCE"  # S1
    POST_HOC_BENCHMARK_ORACLE = "POST_HOC_BENCHMARK_ORACLE"  # S1
    OBSERVED_ACTION = "OBSERVED_ACTION"  # S2
    AGENT_RESOLVED = "AGENT_RESOLVED"  # S2
    OBSERVED_REUSE_OPPORTUNITY = "OBSERVED_REUSE_OPPORTUNITY"  # S3
    OBSERVED_WORKLOAD = "OBSERVED_WORKLOAD"  # S3
    TASK_ENVIRONMENT = "TASK_ENVIRONMENT"
    MEMORY_BENCHMARK = "MEMORY_BENCHMARK"
    GATED_INACCESSIBLE = "GATED_INACCESSIBLE"


class SupervisionType(str, Enum):
    S1_HUMAN_PREFERENCE = "S1"  # Preference / Choice
    S2_AGENT_OUTCOME = "S2"  # Trajectory resolved / Task pass
    S3_AUXILIARY_SYSTEM = "S3"  # Prefix cache / Token usage / Workload timing
    UNSUPERVISED_OR_TIED = "UNSUPERVISED"


# Attributes forbidden inside pre-decision state (future outcome leakage)
FORBIDDEN_PRE_DECISION_KEYS: Set[str] = {
    "task_resolved",
    "resolved",
    "winner_model",
    "winner_choice",
    "total_steps",
    "total_steps_executed",
    "exit_code",
    "output_length",
    "generated_tokens",
    "completion_tokens",
    "pass_at_1",
    "eval_score",
    "execution_success",
    "ground_truth_outcome",
    "oracle_model",
    "actual_cost_usd",
}


@dataclass
class PreDecisionState:
    """T (Task) + M (Model) + H (History) state representation observable before routing."""
    # T (Task State)
    task_domain: str = "general"
    initial_prompt_snippet: str = ""
    prompt_length: int = 0
    task_difficulty: Optional[str] = None
    repo_name: Optional[str] = None
    problem_statement: Optional[str] = None

    # M (Model State)
    current_model: Optional[str] = None
    available_candidates: List[str] = field(default_factory=list)
    model_family: Optional[str] = None
    context_window_limit: Optional[int] = None

    # H (History State)
    step_index: int = 0
    context_chars: int = 0
    prior_tool_calls_count: int = 0
    prior_error_signals_count: int = 0
    cumulative_latency_sec: float = 0.0

    # Additional sanitized auxiliary features
    extra_features: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        extra = d.pop("extra_features", {})
        d.update(extra)
        return d


@dataclass
class ObservedDecision:
    """Routing choice, action, or effort tier dispatched by the agent."""
    model_choice: Optional[str] = None
    effort_tier: Optional[str] = None  # low, medium, high
    action_type: Optional[str] = None  # str_replace_editor, bash, submit, text_response
    action_payload: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GroundTruthOutcome:
    """Post-execution outcome quarantined from pre-decision routing input."""
    label_nature: LabelNature = LabelNature.OBSERVED_ACTION
    supervision_type: SupervisionType = SupervisionType.S2_AGENT_OUTCOME

    # S1: Preference & Benchmark Oracle
    winner_model: Optional[str] = None
    winner_choice: Optional[str] = None  # model_a, model_b, tie
    candidate_scores: Dict[str, float] = field(default_factory=dict)
    candidate_costs_usd: Dict[str, float] = field(default_factory=dict)

    # S2: Agent Trajectory Outcome
    task_resolved: Optional[bool] = None
    exit_code: Optional[int] = None
    total_steps_executed: Optional[int] = None

    # S3: Auxiliary Cache & Token Usage
    observed_prefix_hit_blocks: Optional[int] = None
    prefix_block_count: Optional[int] = None
    estimated_reusable_tokens: Optional[int] = None
    actual_prompt_tokens: Optional[int] = None
    actual_completion_tokens: Optional[int] = None
    request_interval_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Provenance:
    """Data provenance, licensing, and lineage traceability."""
    source_id: str
    source_name: str
    official_origin: str
    license: str
    instance_id: str
    timestamp: Optional[str] = None
    dataset_version: str = "v1.1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CausalRecord:
    """Canonical single-sample unit for ModelRouter training, evaluation, and analysis."""
    provenance: Provenance
    pre_decision_state: PreDecisionState
    observed_decision: ObservedDecision
    ground_truth_outcome: GroundTruthOutcome
    policy_tag: PolicyTag = PolicyTag.TRAIN_ROUTER_CANDIDATE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provenance": self.provenance.to_dict(),
            "pre_decision_state": self.pre_decision_state.to_dict(),
            "observed_decision": self.observed_decision.to_dict(),
            "ground_truth_outcome": self.ground_truth_outcome.to_dict(),
            "policy_tag": self.policy_tag.value,
        }


def validate_causal_isolation(record_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates strict causal isolation of a record.
    Returns (is_valid, violation_reasons).
    """
    violations: List[str] = []
    pre_state = record_dict.get("pre_decision_state", {})

    if not isinstance(pre_state, dict):
        violations.append("pre_decision_state is missing or not a dictionary")
        return False, violations

    # Check for forbidden future outcome keys in pre-decision state
    for k in pre_state.keys():
        if k in FORBIDDEN_PRE_DECISION_KEYS:
            violations.append(f"Causal leakage: forbidden key '{k}' found inside pre_decision_state")

    # Check non-negative constraints
    step_idx = pre_state.get("step_index", 0)
    if isinstance(step_idx, (int, float)) and step_idx < 0:
        violations.append(f"Invalid step_index: {step_idx} must be >= 0")

    prior_tools = pre_state.get("prior_tool_calls_count", 0)
    if isinstance(prior_tools, (int, float)) and prior_tools < 0:
        violations.append(f"Invalid prior_tool_calls_count: {prior_tools} must be >= 0")

    # Check provenance
    prov = record_dict.get("provenance", {})
    if not isinstance(prov, dict) or not prov.get("source_id"):
        violations.append("Missing or incomplete provenance block")

    # Check policy tag
    policy_tag = record_dict.get("policy_tag")
    if policy_tag and policy_tag not in [t.value for t in PolicyTag]:
        violations.append(f"Invalid policy_tag: {policy_tag}")

    return len(violations) == 0, violations
