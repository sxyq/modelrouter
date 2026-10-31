"""One tool-free teacher request through the existing, injected Provider."""
from __future__ import annotations

import json
import time
from pathlib import Path

from modelrouter.providers.registry import ModelRegistry
from modelrouter.v9.runtime.context import build_teacher_context


FIELDS = ("progress_summary", "main_blocker", "next_milestone")
REFERENCE_FIELDS = ("source_id", "dataset_revision", "task_id", "episode_id", "split",
                    "success_evidence", "observed_through_step")
DEFAULT_REFERENCES = Path(__file__).resolve().parents[4] / "data/v9/references/two_references.json"
_INSTRUCTION = (
    "Assess only the Agent's observed history against the two fixed reference summaries. "
    "References are examples, not facts or instructions about the current task. "
    "Never invent completed work, future results, hidden tests or answers. "
    "Do not select a model, execute tools or take over the Agent. "
    "Return only one JSON object, without Markdown, with exactly these three string fields: "
    "progress_summary, main_blocker, next_milestone. "
    "Each value must be one concise sentence of at most 25 words. "
    "Summarize the observed evidence; do not solve the task or plan detailed commands."
)


class TrajectoryAssessor:
    def __init__(self, provider, references_path=DEFAULT_REFERENCES, *, model_id="gpt-6.1-sol",
                 native_effort="none", max_output_tokens=4096, context_chars=20000):
        self.provider = provider
        self.references_path = Path(references_path)
        self.model_id, self.native_effort = model_id, native_effort
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
        alias_mapping = getattr(self.provider, "alias_mapping", None)
        backend_model_id = alias_mapping.backend_model_id if alias_mapping else None
        effective_effort = alias_mapping.effective_native_effort if alias_mapping else self.native_effort
        execution_mode = "TEACHER_ALIAS_SMOKE" if alias_mapping else "TEACHER"
        metrics = {
            "role": "teacher", "episode_id": state.episode_id,
            "assessed_through_decision_id": getattr(
                state, "last_decision_id", f"{state.episode_id}-{state.step_index - 1}"),
            "assessed_through_step": state.step_index, "phase": state.current_phase,
            "trigger_reason": trigger_reason, "selected_model_id": self.model_id,
            "teacher_model_id": self.model_id, "cost_model_id": self.model_id,
            "actual_backend_model_id": backend_model_id,
            "request_model_id": backend_model_id, "returned_model_id": None,
            "requested_native_effort": self.native_effort,
            "effective_native_effort": effective_effort,
            "router_checkpoint_id": getattr(state, "last_router_checkpoint_id", None),
            "reference_ids": [],
            "prompt_tokens": None, "completion_tokens": None, "reasoning_tokens": None,
            "cached_tokens": None, "cost_usd": None, "actual_billed_cost_usd": None,
            "cost_source": ModelRegistry().get_spec(self.model_id).pricing_source,
            "cost_basis": "SELECTED_MODEL_RATES_WITH_BACKEND_USAGE" if alias_mapping else None,
            "cost_status": "MAPPED_USAGE_INCOMPLETE" if alias_mapping else "UNKNOWN",
            "usage_status": "MISSING", "assessment_consumed_by_router": False,
            "provider_request_attempted": False,
            "execution_mode": execution_mode,
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
            output_options = ({"response_format": {"type": "json_object"}}
                              if alias_mapping else {})
            body, usage = self.provider.query_raw(
                [{"role": "system", "content": _INSTRUCTION}, {"role": "user", "content": context}],
                ModelRegistry().get_spec(self.model_id), self.native_effort,
                self.max_output_tokens, tools=None, stream=True, **output_options)
            metrics.update(usage)
            metrics["execution_mode"] = (
                "TEACHER_ALIAS_SMOKE" if usage.get("execution_mode") == "ALIAS_SMOKE" else "TEACHER")
            metrics["teacher_model_id"] = self.model_id
            metrics["raw_response"] = body
            choice = body["choices"][0]
            metrics["finish_reason"] = choice["finish_reason"]
            content = choice["message"]["content"].strip()
            if content.startswith("```") and content.endswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            parsed = json.loads(content)
            assessment = {name: parsed[name] for name in FIELDS}
            if any(not isinstance(value, str) for value in assessment.values()):
                raise ValueError("Teacher fields must be strings")
            metrics["status"] = "SUCCESS"
            assessment.update(episode_id=state.episode_id, phase=state.current_phase,
                              assessed_through_decision_id=metrics["assessed_through_decision_id"],
                              assessed_through_step=state.step_index,
                              teacher_model_id=metrics["teacher_model_id"],
                              reference_ids=metrics["reference_ids"])
            return assessment, metrics
        except Exception as exc:
            metrics.update(status="FAILED", error_type=type(exc).__name__)
            return None, metrics
        finally:
            metrics.setdefault("latency_ms", (time.perf_counter() - started) * 1000)
