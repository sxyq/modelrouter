"""
Pydantic schemas for ModelRouter FastAPI Serving Endpoint.
Conforms strictly to V8 §7.1 specifications.
"""

from typing import Dict, List, Optional, Any
import json
from pydantic import BaseModel, Field, model_validator


class LegalAction(BaseModel):
    provider: str = Field(..., description="Model provider, e.g. openai, anthropic, deepseek")
    model: str = Field(..., description="Model identifier, e.g. gpt-4o, claude-3-5-sonnet")
    revision: Optional[str] = Field("latest", description="Model revision or version hash")
    native_effort: str = Field("none", description="Native reasoning effort: none, low, medium, high")
    action_id: Optional[str] = None
    pool: Optional[str] = None

    @model_validator(mode="after")
    def resolve_registered_action(self):
        from modelrouter.providers.registry import ModelRegistry
        try:
            spec = ModelRegistry().get_spec(self.model)
        except KeyError as exc:
            raise ValueError(f"Unknown registered model: {self.model}") from exc
        spec.validate_effort(self.native_effort)
        if self.provider != spec.provider:
            raise ValueError(f"Provider does not match {self.model}")
        expected_id = f"{self.model}:{self.native_effort}"
        if self.action_id is not None and self.action_id != expected_id:
            raise ValueError("action_id does not match model and effort")
        self.action_id = expected_id
        self.pool = spec.pool
        return self


class PreDecisionState(BaseModel):
    task_id: Optional[str] = None
    phase: Optional[str] = None
    last_tool_exit_code: Optional[int] = None
    last_observation_summary: Optional[str] = None
    history_length: Optional[int] = None
    budget_remaining_usd: Optional[float] = None
    steps_remaining: Optional[int] = None
    context_tokens_approx: Optional[int] = None
    task_domain: Optional[str] = "software_engineering"
    step_index: Optional[int] = 0
    context_chars: Optional[int] = 0
    prior_tool_calls_count: Optional[int] = 0
    prior_error_signals_count: Optional[int] = 0
    prompt: Optional[str] = Field("", description="Pre-decision prompt snippet or observation")
    history_snippet: Optional[str] = Field("", description="Recent tool execution history snippet")
    teacher_assessment: Optional[Dict[str, Any]] = None
    capability_cards: List[Dict[str, Any]] = Field(default_factory=list)
    capability_snapshot_id: Optional[str] = None
    feature_training_status: Optional[str] = None
    agent_context: Optional[Dict[str, Any]] = None
    continuity: Optional[Dict[str, Any]] = None

    def router_text(self) -> str:
        """Both adapters consume the same named pre-decision fields."""
        payload = self.model_dump()
        extensions = ("teacher_assessment", "capability_cards", "capability_snapshot_id",
                      "feature_training_status", "agent_context", "continuity")
        for name in extensions:
            if payload[name] is None or payload[name] == []:
                payload.pop(name)
        if not any(name in payload for name in extensions):
            return json.dumps(payload, sort_keys=True, ensure_ascii=False)
        from modelrouter.v9.runtime.context import format_router_payload
        return format_router_payload(payload)


class RouteRequest(BaseModel):
    request_id: str = Field(..., description="Unique request UUID")
    episode_id: Optional[str] = Field("ep-default", description="Episode tracking ID")
    decision_id: Optional[str] = Field("dec-default", description="Step-level decision ID")
    policy_version: Optional[str] = Field("v8.0", description="Policy version string")
    router_family: str = Field("laya", description="Target router: 'laya' or 'kev'")
    pre_decision_state: PreDecisionState = Field(default_factory=PreDecisionState)
    legal_actions: List[LegalAction] = Field(..., min_length=1, description="List of legal candidate actions")
    budget_remaining: Optional[float] = Field(None, description="Remaining USD budget")
    features_presence_mask: Optional[List[int]] = Field(None, description="Binary feature availability mask")

    @model_validator(mode="after")
    def unique_actions(self):
        ids = [action.action_id for action in self.legal_actions]
        if len(ids) != len(set(ids)):
            raise ValueError("legal_actions contains repeated action_id")
        return self


class ActionScore(BaseModel):
    action: LegalAction
    score: float
    probability: float = Field(ge=0, le=1, allow_inf_nan=False)


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

