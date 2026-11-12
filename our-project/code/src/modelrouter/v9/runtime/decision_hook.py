"""Attach teacher/card state to the existing model-generation boundary."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from modelrouter.benchmark.iterations import event, write_atomic
from modelrouter.v9.capabilities.features import capability_cards, DEFAULT_DATA_DIR
from modelrouter.v9.capabilities.refresh import ensure_current, DEFAULT_MAX_AGE_SECONDS
from modelrouter.v9.teacher.assessor import TrajectoryAssessor, DEFAULT_REFERENCES
from modelrouter.v9.teacher.trigger import TeacherTrigger
from .context import compact_router_state, message_chars


class V9DecisionHook:
    def __init__(self, config: dict, provider, record_dir: Path):
        self.config, self.record_dir = dict(config), Path(record_dir)
        self.capability_snapshot = (
            json.loads(Path(config["comparison_config_path"]).read_text())["v9_config"]["capability_snapshot"]
            if "comparison_config_path" in config else
            deepcopy(config["capability_snapshot"]) if "capability_snapshot" in config
            else ensure_current(config.get("capabilities_path", DEFAULT_DATA_DIR),
                                max_age_seconds=config.get("capability_max_age_seconds", DEFAULT_MAX_AGE_SECONDS),
                                force=config.get("capability_force_refresh", False)))
        self.teacher_enabled = config.get("teacher_enabled", True)
        self.assessor = TrajectoryAssessor(
            provider, config.get("references_path", DEFAULT_REFERENCES),
            model_id=config.get("teacher_model_id", "gpt-6-luna"),
            native_effort=config.get("teacher_native_effort", "low"),
            max_output_tokens=config.get("teacher_max_output_tokens", 4096),
            context_chars=config.get("teacher_context_chars", 8000), record_dir=self.record_dir)
        self.trigger = TeacherTrigger()
        self.episode_id = None
        self.assessment = None
        self.teacher_metrics = []
        self.last_teacher_metrics = []
        self.continuity = {}
        self.previous_selected = None
        self.previous_backend = None
        self.previous_messages = []
        self.current_context = {}

    def _router_identity(self, decision, neural_route):
        identity = {"router_run_id": None, "router_identity_source": None,
                    "router_identity_status": "NOT_A_NEURAL_ROUTE"}
        if not neural_route or decision.fallback_used:
            return identity
        return decision.router_identity or {"router_run_id": None,
            "router_identity_status": "NOT_REPORTED_BY_RUNNING_SERVING"}

    def before_route(self, state, messages, snapshot, legal_actions, *, route_due=True):
        if state.episode_id != self.episode_id:
            self.episode_id = state.episode_id
            self.trigger.reset(state.episode_id)
            self.assessment, self.continuity = None, {}
            self.previous_selected = self.previous_backend = None
            self.previous_messages = []
            self.teacher_metrics.clear()
        self.last_teacher_metrics = []
        self.current_context = {
            "episode_id": state.episode_id, "decision_id": f"{state.episode_id}-{state.step_index}",
            "message_count": len(messages), "message_chars": message_chars(messages),
            "capability_snapshot_id": self.capability_snapshot.get("snapshot_id"),
            "input_prefix_continuity": ("FIRST_REQUEST" if not self.previous_messages else
                "EXACT_PREVIOUS_MESSAGES" if messages[:len(self.previous_messages)] == self.previous_messages
                else "PREFIX_CHANGED"),
            "previous_request_message_count": len(self.previous_messages),
        }
        self.previous_messages = deepcopy(messages)
        result = compact_router_state(state, messages, snapshot,
                                      self.config.get("router_context_chars", 6000))
        if self.teacher_enabled:
            reason = self.trigger.reason(state)
            teacher_status = "CARRIED_ASSESSMENT" if self.assessment else "NOT_TRIGGERED"
            if reason and route_due:
                event(self.record_dir, "TEACHER_START", episode_id=state.episode_id,
                      decision_id=self.current_context["decision_id"], trigger_reason=reason)
                self.assessment, metrics = self.assessor.assess(state, messages, reason)
                teacher_status = metrics["status"]
                self.trigger.record_attempt(state)
                self.teacher_metrics.append(metrics)
                self.last_teacher_metrics.append(metrics)
                if state.teacher_time_sec is not None:
                    state.teacher_time_sec += metrics["teacher_wall_ms"] / 1000
                if metrics.get("cost_usd") is not None:
                    state.accumulated_cost_usd += metrics["cost_usd"]
                    result["budget_remaining_usd"] = state.budget_remaining_usd
                event(self.record_dir, "TEACHER_END" if self.assessment is not None else "TEACHER_ERROR",
                      assessment=self.assessment, **metrics)
            elif self.assessment is not None and not self.trigger.assessment_is_current(state):
                self.assessment = None
                teacher_status = "PRIOR_ASSESSMENT_OUTDATED"
        result.update(
            disabled_information_groups=self.config.get("disabled_information_groups", []),
            teacher_assessment=deepcopy(self.assessment) if self.teacher_enabled else None,
            teacher_status=teacher_status if self.teacher_enabled else "DISABLED",
            capability_cards=capability_cards(self.capability_snapshot, legal_actions),
            capability_snapshot_id=self.capability_snapshot.get("snapshot_id"),
            aa_fetched_at=self.capability_snapshot.get("aa_fetched_at"),
            aa_index_version=self.capability_snapshot.get("aa_index_version"),
            capability_freshness=self.capability_snapshot.get("freshness_status"),
            feature_training_status=self.config.get("feature_training_status", "FEATURE_NOT_TRAINED"),
            continuity={**deepcopy(self.continuity),
                        "input_prefix_continuity": self.current_context["input_prefix_continuity"],
                        "previous_request_message_count": self.current_context["previous_request_message_count"],
                        "message_count": len(messages),
                        "prefix_reuse_estimate": "PREVIOUS_MESSAGES_RETAINED" if self.current_context["input_prefix_continuity"] == "EXACT_PREVIOUS_MESSAGES" else "NO_EXACT_PREFIX_EVIDENCE"},
        )
        result["agent_context"]["completed_generations"] = state.step_index
        elapsed = state.elapsed_time_sec
        result.update(elapsed_time_sec=elapsed, teacher_time_sec=state.teacher_time_sec,
                      time_remaining_sec=max(0, state.time_budget_sec - elapsed) if state.time_budget_sec and elapsed is not None else None)
        return result

    def after_route(self, decision, neural_route=True):
        self.current_context.update(router_checkpoint_id=decision.checkpoint_id,
                                    router_family=decision.router_family,
                                    router_fallback_used=decision.fallback_used)
        self.current_context.update(self._router_identity(decision, neural_route))
        if self.assessment is None:
            return
        consumed = neural_route and not decision.fallback_used
        usage = (decision.router_identity or {}).get("router_input_usage") or {}
        coverage = usage.get("state_group_coverage", {})
        encoded = coverage.get("teacher_assessment", {}).get("status") == "FULL"
        self.teacher_metrics[-1]["assessment_consumed_by_router"] |= consumed and encoded
        event(self.record_dir, "TEACHER_ROUTER_INPUT", **self.current_context,
              assessed_through_decision_id=self.assessment["assessed_through_decision_id"],
              checkpoint_id=decision.checkpoint_id, assessment_consumed_by_router=consumed and encoded,
              assessment_sent_to_router=consumed, teacher_encoding_status=coverage.get("teacher_assessment"))

    def after_generation(self, metrics, selected, response):
        write_atomic(self.record_dir / "provider_responses" / f"{metrics['decision_id']}.json",
                     {"response": response, "metrics": metrics})
        backend = metrics.get("actual_backend_model_id")
        model_id = selected["model"]
        cached = metrics.get("cached_tokens")
        self.continuity = {
            **self.current_context,
            "previous_router_checkpoint_id": self.continuity.get("router_checkpoint_id"),
            "previous_router_run_id": self.continuity.get("router_run_id"),
            "previous_selected_model_id": self.previous_selected,
            "selected_model_id": model_id,
            "previous_request_model_id": self.continuity.get("request_model_id"),
            "request_model_id": metrics["request_model_id"],
            "previous_returned_model_id": metrics.get("returned_model_id"),
            "previous_provider": self.continuity.get("provider"),
            "provider": metrics["provider"],
            "previous_provider_endpoint_id": self.continuity.get("provider_endpoint_id"),
            "provider_endpoint_id": metrics.get("provider_endpoint_id"),
            "previous_provider_base_url": self.continuity.get("provider_base_url"),
            "provider_base_url": metrics.get("provider_base_url"),
            "previous_request_input_tokens": self.continuity.get("request_input_tokens"),
            "request_input_tokens": metrics.get("prompt_tokens"),
            "previous_response_output_tokens": metrics.get("completion_tokens"),
            "previous_response_reasoning_tokens": metrics.get("reasoning_tokens"),
            "previous_response_cost_usd": metrics.get("cost_usd"),
            "previous_response_latency_ms": metrics.get("latency_ms"),
            "previous_response_status": metrics["response_status"],
            "context_tokens_resent": None,
            "previous_selected_native_effort": self.continuity.get("selected_native_effort"),
            "selected_native_effort": selected["native_effort"],
            "request_native_effort": metrics["request_native_effort"],
            "returned_native_effort": metrics["returned_native_effort"],
            "native_effort_status": metrics["native_effort_status"],
            "previous_actual_backend_model_id": self.previous_backend,
            "actual_backend_model_id": backend,
            "logical_model_changed": self.previous_selected is not None and self.previous_selected != model_id,
            "actual_backend_changed": None if self.previous_backend is None or backend is None else self.previous_backend != backend,
            "context_delivery": "FULL_MESSAGE_HISTORY",
            "history_messages_resent": self.previous_selected is not None and self.current_context["message_count"] > 1,
            "observed_cached_tokens": cached,
            "observed_cache_write_tokens": metrics.get("cache_write_tokens"),
            "cache_usage_status": "REPORTED" if cached is not None else "NOT_REPORTED",
            "physical_kv_cache_shared": None,
            "switch_extra_tokens": None, "switch_extra_cost_usd": None,
            "switch_cost_status": "NOT_MEASURED",
        }
        self.previous_selected, self.previous_backend = model_id, backend
        event(self.record_dir, "V9_CONTEXT_END", **self.continuity)
