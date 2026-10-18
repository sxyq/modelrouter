"""
Pydantic schemas for ModelRouter FastAPI Serving Endpoint.
Conforms strictly to V8 §7.1 specifications.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LegalAction(BaseModel):
    provider: str = Field(..., description="Model provider, e.g. openai, anthropic, deepseek")
    model: str = Field(..., description="Model identifier, e.g. gpt-4o, claude-3-5-sonnet")
    revision: Optional[str] = Field("latest", description="Model revision or version hash")
    native_effort: str = Field("none", description="Native reasoning effort: none, low, medium, high")


class PreDecisionState(BaseModel):
    task_domain: Optional[str] = "software_engineering"
    step_index: Optional[int] = 0
    context_chars: Optional[int] = 0
    prior_tool_calls_count: Optional[int] = 0
    prior_error_signals_count: Optional[int] = 0
    prompt: Optional[str] = Field("", description="Pre-decision prompt snippet or observation")
    history_snippet: Optional[str] = Field("", description="Recent tool execution history snippet")


class RouteRequest(BaseModel):
    request_id: str = Field(..., description="Unique request UUID")
    episode_id: Optional[str] = Field("ep-default", description="Episode tracking ID")
    decision_id: Optional[str] = Field("dec-default", description="Step-level decision ID")
    policy_version: Optional[str] = Field("v8.0", description="Policy version string")
    router_family: str = Field("laya", description="Target router: 'laya' or 'kev'")
    pre_decision_state: PreDecisionState = Field(default_factory=PreDecisionState)
    legal_actions: List[LegalAction] = Field(..., min_items=1, description="List of legal candidate actions")
    budget_remaining: Optional[float] = Field(None, description="Remaining USD budget")
    features_presence_mask: Optional[List[int]] = Field(None, description="Binary feature availability mask")


class ActionScore(BaseModel):
    action: LegalAction
    score: float
    probability: float


class RouteResponse(BaseModel):
    request_id: str
    router_family: str
    checkpoint_id: str
    selected_action: LegalAction
    ranked_actions_or_scores_if_available: List[ActionScore] = Field(default_factory=list)
    decision_latency_ms: float
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    confidence_if_defined: Optional[float] = None


class ModelInfo(BaseModel):
    family: str
    run_id: str
    checkpoint_id: str
    epoch: Optional[int] = None
    loaded: bool
    weights_path: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class ModelsResponse(BaseModel):
    models: List[ModelInfo]


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_used_mb: Optional[float] = None
    gpu_memory_total_mb: Optional[float] = None
    gpu_utilization_pct: Optional[float] = None
    models_loaded: Dict[str, bool] = Field(default_factory=dict)
    weights_loaded: Dict[str, bool] = Field(default_factory=dict)
    inference_verified: Dict[str, bool] = Field(default_factory=dict)


class SystemOneRequest(BaseModel):
    router_family: Optional[str] = Field("laya", description="Target router: 'laya' or 'kev'")
    model: Optional[str] = Field(None, description="Optional model identifier, alias for router_family")
    state: Any = Field(..., description="Observed agent state (str, dict, or list)")
    questions: Dict[str, Any] = Field(..., description="Questions mapping: {qid: {type, instructions, criteria}}")


class SystemOneResponse(BaseModel):
    router_family: str
    model: str
    checkpoint_id: str
    answers: Dict[str, Any]
    decision_latency_ms: float
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

