"""One tool-free teacher request through the existing, injected Provider."""
from __future__ import annotations

import json
import time
import urllib.error
from pathlib import Path

from modelrouter.providers.provider import ProviderResponseError
from modelrouter.providers.registry import ModelRegistry
from modelrouter.v9.runtime.context import build_teacher_context


FIELDS = ("progress_summary", "main_blocker", "next_milestone")
REFERENCE_FIELDS = ("source_id", "dataset_revision", "task_id", "episode_id", "split",
                    "success_evidence", "observed_through_step")
DEFAULT_REFERENCES = Path(__file__).resolve().parents[4] / "data/v9/references/two_references.json"
_INSTRUCTION = (
    "Write a brief status record using only explicitly observed Agent facts. "
    "The two fixed reference excerpts are examples of reporting, not current-task facts. "
    "Do not analyze code or data, derive a solution, or compare possible plans. "
    "Never invent completed work, future results, hidden tests or answers. "
    "Do not select a model, execute tools or take over the Agent. "
    "Return only one JSON object, without Markdown, with exactly these three string fields: "
    "progress_summary, main_blocker, next_milestone. "
    "Each value must be one concise sentence of at most 25 words. "
    "Summarize the observed evidence; do not solve the task or plan detailed commands."
)


class TrajectoryAssessor:
    def __init__(self, provider, references_path=DEFAULT_REFERENCES, *, model_id="gpt-6-luna",
                 native_effort="low", max_output_tokens=4096, context_chars=8000):
        self.provider = provider
        self.references_path = Path(references_path)
        self.model_id, self.native_effort = model_id, native_effort
        if model_id != "gpt-6-luna":
            raise ValueError("The V9 trajectory teacher is gpt-6-luna")
        self.max_output_tokens, self.context_chars = max_output_tokens, context_chars
        self.references = None

    def load_references(self):
        if self.references is None:
            references = json.loads(self.references_path.read_text(encoding="utf-8"))
            if len(references) != 2:
                raise ValueError("Two recorded success references are required")
            for reference in references:
                for name in (*REFERENCE_FIELDS, "summary"):
                    reference[name]
                if not reference["success_evidence"]:
                    raise ValueError("Reference has no recorded success evidence")
            if len({(ref["source_id"], ref["episode_id"]) for ref in references}) != 2:
                raise ValueError("Two distinct success references are required")
            self.references = references
        return self.references

    def assess(self, state, messages, trigger_reason):
        started = time.perf_counter()
        metrics = {
            "role": "teacher", "episode_id": state.episode_id,
            "decision_id": f"{state.episode_id}-{state.step_index}",
            "assessed_through_decision_id": getattr(
                state, "last_decision_id", f"{state.episode_id}-{state.step_index - 1}"),
            "assessed_through_step": state.step_index, "phase": state.current_phase,
            "for_decision_id": f"{state.episode_id}-{state.step_index}",
            "trigger_reason": trigger_reason, "selected_model_id": self.model_id,
            "teacher_model_id": self.model_id, "cost_model_id": self.model_id,
            "actual_backend_model_id": None,
            "request_model_id": self.model_id, "returned_model_id": None,
            "protocol": self.provider.protocol, "provider_base_url": self.provider.base_url,
            "requested_max_output_tokens": self.max_output_tokens,
            "requested_native_effort": self.native_effort,
            "effective_native_effort": self.native_effort,
            "router_checkpoint_id": getattr(state, "last_router_checkpoint_id", None),
            "reference_ids": [],
            "prompt_tokens": None, "completion_tokens": None, "reasoning_tokens": None,
            "cached_tokens": None, "cost_usd": None, "actual_billed_cost_usd": None,
            "cost_source": ModelRegistry().get_spec(self.model_id).pricing_source,
            "cost_basis": "REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE",
            "cost_status": "UNKNOWN",
            "usage_status": "MISSING", "assessment_consumed_by_router": False,
            "provider_request_attempted": False,
            "execution_mode": "TEACHER",
        }
        try:
            references = self.load_references()
            if any(ref["task_id"] == state.task_id or ref["episode_id"] == state.episode_id
                   or ref["split"].lower() in ("sealed_final", "final") for ref in references):
                raise ValueError("Reference overlaps the current task or final evaluation")
            metrics["reference_ids"] = [{name: ref[name] for name in REFERENCE_FIELDS}
                                        for ref in references]
            context = build_teacher_context(state, messages, references, self.context_chars)
            metrics.update(context_chars=len(context), context_char_limit=self.context_chars,
                           token_measurement_status="CHARACTERS_ONLY_BEFORE_REQUEST")
            metrics["provider_request_attempted"] = True
            response = self.provider.generate(
                [{"role": "system", "content": _INSTRUCTION}, {"role": "user", "content": context}],
                ModelRegistry().get_spec(self.model_id), self.native_effort,
                self.max_output_tokens, tools=None, stream=True,
                response_format={"type": "json_object"})
            body, usage = response.raw_response, response.metadata
            metrics.update(usage)
            metrics["execution_mode"] = "TEACHER"
            metrics["teacher_model_id"] = self.model_id
            metrics["raw_response"] = body
            content = response.content.strip()
            parsed = json.loads(content)
            if set(parsed) != set(FIELDS):
                raise ValueError("Teacher must return exactly the three assessment fields")
            assessment = {name: parsed[name] for name in FIELDS}
            if any(not isinstance(value, str) for value in assessment.values()):
                raise ValueError("Teacher fields must be strings")
            metrics["status"] = "SUCCESS"
            assessment.update(episode_id=state.episode_id, phase=state.current_phase,
                              for_decision_id=metrics["for_decision_id"],
                              assessed_through_decision_id=metrics["assessed_through_decision_id"],
                              assessed_through_step=state.step_index,
                              teacher_model_id=metrics["teacher_model_id"],
                              reference_ids=metrics["reference_ids"])
            return assessment, metrics
        except Exception as exc:
            if isinstance(exc, ProviderResponseError):
                metrics.update(exc.metrics)
                metrics["raw_response"] = exc.response
                metrics["execution_mode"] = "TEACHER"
            metrics["account_attempts"] = getattr(exc, "account_attempts", [])
            metrics.update(status="FAILED", error_type=type(exc).__name__)
            if isinstance(exc, urllib.error.HTTPError):
                metrics.update(http_status=exc.code,
                               error_response=exc.read().decode("utf-8", errors="replace"))
            return None, metrics
        finally:
            metrics["teacher_wall_ms"] = (time.perf_counter() - started) * 1000
            metrics.setdefault("latency_ms", metrics["teacher_wall_ms"])
