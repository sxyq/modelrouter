"""Attach teacher/card state to the existing model-generation boundary."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import urllib.request

from modelrouter.benchmark.iterations import event
from modelrouter.v9.capabilities.features import capability_cards, load_current, DEFAULT_DATA_DIR
from modelrouter.v9.teacher.assessor import TrajectoryAssessor, DEFAULT_REFERENCES
from modelrouter.v9.teacher.trigger import TeacherTrigger
from .context import compact_router_state, message_chars


class V9DecisionHook:
    def __init__(self, config: dict, provider, record_dir: Path):
        self.config, self.record_dir = dict(config), Path(record_dir)
        self.capability_snapshot = (
            deepcopy(config["capability_snapshot"]) if "capability_snapshot" in config
            else load_current(config.get("capabilities_path", DEFAULT_DATA_DIR)))
        self.teacher_enabled = config.get("teacher_enabled", True)
        self.assessor = TrajectoryAssessor(
            provider, config.get("references_path", DEFAULT_REFERENCES),
            model_id=config.get("teacher_model_id", "gpt-6.1-sol"),
            native_effort=config.get("teacher_native_effort", "none"),
            max_output_tokens=config.get("teacher_max_output_tokens", 4096),
            context_chars=config.get("teacher_context_chars", 20000))
        self.trigger = TeacherTrigger()
        self.episode_id = None
        self.assessment = None
        self.teacher_metrics = []
        self.last_teacher_metrics = []
        self.continuity = {}
        self.previous_selected = None
        self.previous_backend = None
        self.current_context = {}
        self._identity_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _router_identity(self, decision, neural_route):
        identity = {"router_run_id": None, "router_identity_source": None,
                    "router_identity_status": "NOT_A_NEURAL_ROUTE"}
        if not neural_route or decision.fallback_used:
            return identity
        from modelrouter.serving.schemas import ModelsResponse

        url = self.config["router_endpoint"].rstrip("/") + "/models"
        identity.update(router_identity_source=url, router_identity_status="UNAVAILABLE")
        try:
            with self._identity_opener.open(url, timeout=3.0) as response:
                models = ModelsResponse.model_validate(json.load(response)).models
            matches = [model for model in models if model.loaded
                       and model.family == decision.router_family
                       and model.checkpoint_id == decision.checkpoint_id]
            if len(matches) == 1 and matches[0].run_id and matches[0].run_id != "unknown":
                identity.update(router_run_id=matches[0].run_id,
                                router_weights_path=matches[0].weights_path,
                                router_identity_status="SERVING_MODELS_SNAPSHOT_NOT_ATOMIC_WITH_ROUTE")
            else:
                identity["router_identity_status"] = "MISSING_OR_AMBIGUOUS_MATCH"
        except (OSError, ValueError) as exc:
            identity["router_identity_error"] = type(exc).__name__
        return identity

    def before_route(self, state, messages, snapshot, legal_actions):
        if state.episode_id != self.episode_id:
            self.episode_id = state.episode_id
            self.trigger.reset(state.episode_id)
            self.assessment, self.continuity = None, {}
            self.previous_selected = self.previous_backend = None
            self.teacher_metrics.clear()
        self.last_teacher_metrics = []
        self.current_context = {
            "episode_id": state.episode_id, "decision_id": f"{state.episode_id}-{state.step_index}",
            "message_count": len(messages), "message_chars": message_chars(messages),
            "capability_snapshot_id": self.capability_snapshot.get("snapshot_id"),
        }
        result = compact_router_state(state, messages, snapshot,
                                      self.config.get("router_context_chars", 6000))
        if self.teacher_enabled:
            reason = self.trigger.reason(state)
            if reason:
                self.assessment, metrics = self.assessor.assess(state, messages, reason)
                self.trigger.record_attempt(state)
                self.teacher_metrics.append(metrics)
                self.last_teacher_metrics.append(metrics)
                if metrics.get("cost_usd") is not None:
                    state.accumulated_cost_usd += metrics["cost_usd"]
                    result["budget_remaining_usd"] = state.budget_remaining_usd
                event(self.record_dir, "TEACHER_END" if self.assessment is not None else "TEACHER_ERROR",
                      assessment=self.assessment, **metrics)
            elif self.assessment is not None and self.trigger.signals(state) != self.trigger.last_signals:
                self.assessment = None
        result.update(
            teacher_assessment=deepcopy(self.assessment) if self.teacher_enabled else None,
            capability_cards=capability_cards(self.capability_snapshot, legal_actions),
            capability_snapshot_id=self.capability_snapshot.get("snapshot_id"),
            feature_training_status=self.config.get("feature_training_status", "FEATURE_NOT_TRAINED"),
            continuity=deepcopy(self.continuity),
        )
        result["agent_context"]["completed_generations"] = self.trigger.generation_count
        return result

    def after_route(self, decision, neural_route=True):
        self.current_context.update(router_checkpoint_id=decision.checkpoint_id,
                                    router_family=decision.router_family,
                                    router_fallback_used=decision.fallback_used)
        self.current_context.update(self._router_identity(decision, neural_route))
        if self.assessment is None:
            return
        consumed = neural_route and not decision.fallback_used
        self.teacher_metrics[-1]["assessment_consumed_by_router"] |= consumed
        event(self.record_dir, "TEACHER_ROUTER_INPUT", **self.current_context,
              assessed_through_decision_id=self.assessment["assessed_through_decision_id"],
              checkpoint_id=decision.checkpoint_id, assessment_consumed_by_router=consumed)

    def after_generation(self, metrics, selected):
        backend = metrics.get("actual_backend_model_id") or metrics.get("returned_model_id")
        model_id = selected["model"]
        cached = metrics.get("cached_tokens")
        self.continuity = {
            **self.current_context,
            "previous_router_checkpoint_id": self.continuity.get("router_checkpoint_id"),
            "previous_router_run_id": self.continuity.get("router_run_id"),
            "previous_selected_model_id": self.previous_selected,
            "selected_model_id": model_id,
            "previous_actual_backend_model_id": self.previous_backend,
            "actual_backend_model_id": backend,
            "logical_model_changed": self.previous_selected is not None and self.previous_selected != model_id,
            "actual_backend_changed": None if self.previous_backend is None else self.previous_backend != backend,
            "context_delivery": "FULL_MESSAGE_HISTORY",
            "history_messages_resent": self.previous_selected is not None and self.current_context["message_count"] > 1,
            "observed_cached_tokens": cached,
            "cache_usage_status": "REPORTED" if cached is not None else "NOT_REPORTED",
            "physical_kv_cache_shared": None,
            "switch_extra_tokens": None, "switch_extra_cost_usd": None,
            "switch_cost_status": "NOT_MEASURED",
        }
        self.previous_selected, self.previous_backend = model_id, backend
        self.trigger.after_generation()
        event(self.record_dir, "V9_CONTEXT_END", **self.continuity)
