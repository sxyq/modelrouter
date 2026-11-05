"""Isolated teacher/Hook tests; fixture references are not research evidence."""
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from modelrouter.agent.router_clients import RouterDecision
from modelrouter.agent.state import AgentState, EpisodeStatus, StepTrace
from modelrouter.benchmark.harbor_agent import PolicyModel
from modelrouter.providers.registry import ModelRegistry, V9_MODEL_IDS
from modelrouter.serving.schemas import LegalAction
from modelrouter.v9.runtime.alias import AliasMapping
from modelrouter.v9.runtime.context import build_teacher_context, compact_router_state, format_router_payload, task_text
from modelrouter.v9.runtime.decision_hook import V9DecisionHook
from modelrouter.v9.teacher.trigger import TeacherTrigger


class FixtureProvider:
    def __init__(self, *, cost=None, teacher_cost=None, teacher_error=None,
                 cost_status="BACKEND_PRICE_NOT_MEASURED"):
        self.cost, self.teacher_cost, self.teacher_error = cost, teacher_cost, teacher_error
        self.cost_status, self.calls = cost_status, []
        self.alias_mapping = AliasMapping("Qwen3.8-27B", cost_status=cost_status) if cost is None else None

    def query_raw(self, messages, spec, native_effort, max_tokens, tools=None, stream=True):
        teacher = tools is None
        self.calls.append({"teacher": teacher, "messages": deepcopy(messages),
                           "model_id": spec.model_id, "tools": tools, "stream": stream})
        if teacher and isinstance(self.teacher_error, Exception):
            raise self.teacher_error
        content = json.dumps({"progress_summary": "unit-only progress",
                              "main_blocker": "unit-only issue",
                              "next_milestone": "unit-only target"}) if teacher else "unit-only response"
        if teacher and self.teacher_error == "invalid_json":
            content = "not JSON"
        metrics = {
            "selected_model_id": spec.model_id, "returned_model_id": "Qwen3.8-27B",
            "actual_backend_model_id": "Qwen3.8-27B", "native_effort": native_effort,
            "execution_mode": "ALIAS_SMOKE" if self.alias_mapping else "UNIT_TEST_ONLY",
            "cost_status": self.cost_status, "cost_usd": self.teacher_cost if teacher else self.cost,
            "actual_billed_cost_usd": None, "prompt_tokens": 10, "completion_tokens": 4,
            "reasoning_tokens": None, "cached_tokens": None, "usage_status": "REPORTED",
            "latency_ms": 1.0,
        }
        body = {"id": "unit-response", "object": "chat.completion", "created": 0,
                "model": "Qwen3.8-27B", "choices": [{"index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": content}}]}
        return body, metrics


class LoopProvider(FixtureProvider):
    """Unit responses only; Bash is executed by the installed mini agent."""

    def __init__(self, commands, **kwargs):
        super().__init__(**kwargs)
        self.commands = iter(commands)

    def query_raw(self, messages, spec, native_effort, max_tokens, tools=None, stream=True):
        body, metrics = super().query_raw(messages, spec, native_effort, max_tokens, tools, stream)
        if tools is not None:
            body["choices"][0].update(finish_reason="tool_calls", message={
                "role": "assistant", "content": "UNIT_TEST_ONLY",
                "tool_calls": [{"id": f"unit-call-{len(self.calls)}", "type": "function",
                                "function": {"name": "bash", "arguments": json.dumps({
                                    "command": next(self.commands)})}}],
            })
        return body, metrics


@pytest.fixture
def references(tmp_path):
    data = [{"source_id": "UNIT_TEST_ONLY", "dataset_revision": "fixture",
             "task_id": f"fixture-task-{index}", "episode_id": f"fixture-episode-{index}",
             "split": "UNIT_TEST_ONLY", "success_evidence": {"fixture_only": True},
             "summary": "Synthetic unit input; not a published success case.",
             "observed_through_step": 2} for index in range(2)]
    path = tmp_path / "unit-references.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def state_for(episode="unit-episode"):
    state = AgentState("unit-task", episode, "laya", max_steps=20)
    state.task_prompt = "Unit task"
    return state


def add_tool(state, command="read unit.py", output="unit observation", code=0, *, step=None):
    state.history.append(StepTrace(
        step_index=state.step_index if step is None else step, phase=state.current_phase,
        selected_action={}, thought="", tool_action=command, tool_observation=output,
        tool_exit_code=code, prompt_tokens=0, completion_tokens=0, reasoning_tokens=0,
        cached_tokens=0, step_cost_usd=0, step_duration_sec=0))
    if code:
        state.tool_error_count += 1


def actions():
    registry = ModelRegistry()
    return [LegalAction(provider=registry.get_spec(model).provider, model=model).model_dump()
            for model in V9_MODEL_IDS]


def hook_for(tmp_path, references, provider, **config):
    return V9DecisionHook({"references_path": references, "capability_snapshot": {}, **config},
                          provider, tmp_path / "run")


def before(hook, state, messages=None):
    return hook.before_route(state, messages or [{"role": "user", "content": "Unit task"}],
                             state.build_pre_decision_snapshot().to_dict(), actions())


def test_context_is_bounded_and_does_not_include_future(references):
    state = state_for()
    state.step_index = 1
    add_tool(state, output="observed " + "x" * 5000)
    add_tool(state, output="FUTURE_TOOL_SECRET", step=2)
    messages = [{"role": "user", "content": "Unit task"},
                {"role": "assistant", "content": "observed model output"},
                {"role": "tool", "content": "observed tool output"},
                {"role": "assistant", "content": "FUTURE_MESSAGE_SECRET"}]
    original = deepcopy(messages)
    context = build_teacher_context(state, messages, json.loads(references.read_text()), 1200)
    snapshot = compact_router_state(state, messages, state.build_pre_decision_snapshot().to_dict(), 500)
    assert len(context) <= 1200
    assert "FUTURE_" not in context + json.dumps(snapshot)
    assert len(snapshot["prompt"]) + len(snapshot["history_snippet"]) <= 500
    assert snapshot["prompt"] == "Unit task"
    assert snapshot["context_tokens_approx"] is None
    assert messages == original

    description = "\nUNIT_TEST_ONLY: Repair the parser described here and run its existing test.\n"
    wrapped = "unit SWE wrapper " * 350 + "<pr_description>" + description + "</pr_description>"
    state.task_prompt = wrapped
    messages[0]["content"] = wrapped
    original = deepcopy(messages)
    assert task_text(state, messages) == wrapped
    assert task_text(state, messages, router_view=True) == description
    snapshot = compact_router_state(state, messages, state.build_pre_decision_snapshot().to_dict(), 500)
    assert snapshot["prompt"] == description
    full_teacher = build_teacher_context(state, messages, json.loads(references.read_text()), 48000)
    assert "CURRENT TASK\n" + wrapped in full_teacher
    assert json.dumps(json.loads(references.read_text()), ensure_ascii=False) in full_teacher
    assert "FUTURE_" not in full_teacher
    assert messages == original and state.task_prompt == wrapped
    state.task_prompt = "UNIT_TEST_ONLY: Keep the invoice task text unchanged."
    assert task_text(state, messages, router_view=True) == state.task_prompt


def test_short_router_budget_preserves_complete_task():
    """Synthetic text sizing only; no Agent task execution."""
    prefix = "UNIT_TEST_ONLY: observed task text "
    task = prefix + "x" * (1019 - len(prefix))
    state = state_for()
    state.task_prompt, state.step_index = task, 1
    output = "u" * 3835
    add_tool(state, output=output)
    messages = [{"role": "user", "content": task}, {"role": "tool", "content": output}]
    snapshot = state.build_pre_decision_snapshot().to_dict()
    original_messages, original_snapshot, original_history = deepcopy(messages), deepcopy(snapshot), deepcopy(state.history)
    result = compact_router_state(state, messages, snapshot, char_limit=2300)
    assert result["prompt"] == task and len(result["prompt"]) == 1019
    assert 0 < len(result["history_snippet"]) <= 2300 - 1019
    assert result["agent_context"]["router_task_chars"] == 1019
    assert result["agent_context"]["router_tool_chars"] == len(result["history_snippet"])
    assert messages == original_messages and snapshot == original_snapshot
    assert state.task_prompt == task and state.history == original_history
    long_state = state_for()
    long_state.task_prompt = task * 3
    default = compact_router_state(long_state, [{"role": "user", "content": long_state.task_prompt}], {})
    assert default["prompt"] == long_state.task_prompt[:2000]
    assert default["agent_context"]["router_task_tool_char_limit"] == 6000


def test_router_formatter_preserves_priority_identity_and_measured_values():
    """Formatting input only; no task execution or benchmark evidence."""
    from modelrouter.v9.capabilities.features import capability_cards

    legacy = {"prompt": "Unit task", "phase": "inspect", "budget_remaining_usd": None,
              "teacher_assessment": None, "capability_cards": [], "capability_snapshot_id": None}
    expected = {name: value for name, value in legacy.items() if name not in
                ("teacher_assessment", "capability_cards", "capability_snapshot_id")}
    assert format_router_payload(legacy) == json.dumps(expected, sort_keys=True, ensure_ascii=False)
    cards = list(reversed(sorted(capability_cards({}, actions()), key=lambda card: card["action_id"])))
    for card in cards:
        card.update(snapshot_id="UNIT-snapshot", revision="latest", model_pricing={
            "input_price": None, "currency": None, "status": "NOT_MEASURED",
            "source_url": "https://unit-only.invalid/" + "metadata" * 100})
    cards[0]["model_metrics"] = [{
        "metric_name": "unit_coding_metric", "score_raw": 0, "score_unit": "INDEX",
        "benchmark_version": "unit-v1", "score_scope": "model", "evaluated_native_effort": None,
        "source_url": "https://unit-only.invalid/metric", "evidence_status": "MEASURED"}]
    payload = {
        "prompt": "UNIT_TEST_ONLY: preserve this English task before capability and history metadata.",
        "teacher_assessment": {"progress_summary": "Unit progress", "main_blocker": "Unit issue",
            "next_milestone": "Unit target", "reference_ids": [{"summary": "metadata" * 100}] * 2,
            "assessed_through_decision_id": "UNIT-only"},
        "capability_cards": cards, "capability_snapshot_id": "UNIT-snapshot",
        "phase": "verify", "budget_remaining_usd": None, "steps_remaining": 3,
        "context_chars": 4000, "agent_context": {"message_count": 4, "completed_generations": 3},
        "continuity": {"observed_cached_tokens": 3136, "cache_usage_status": "REPORTED",
            "physical_kv_cache_shared": None, "context_delivery": "FULL_MESSAGE_HISTORY",
            "actual_backend_changed": False, "logical_model_changed": False,
            "selected_model_id": cards[0]["model_id"], "previous_selected_model_id": cards[0]["model_id"],
            "actual_backend_model_id": "UNIT-backend", "previous_actual_backend_model_id": "UNIT-backend",
            "router_checkpoint_id": "UNIT-checkpoint", "previous_router_checkpoint_id": "UNIT-checkpoint",
            "backend_deployment_status": "API_IDENTITY_ONLY_UNVERIFIED_PHYSICAL_BACKEND"},
        "last_observation_summary": "Unit observation", "history_snippet": "unit history " * 500,
    }
    original = deepcopy(payload)
    encoded = format_router_payload(payload)
    result = json.loads(encoded)
    assert payload == original
    assert list(result)[0] == "prompt" and result["prompt"] == payload["prompt"]
    assert list(result)[-1] == "history_snippet"
    assert result["teacher_assessment"] == {name: payload["teacher_assessment"][name] for name in
        ("progress_summary", "main_blocker", "next_milestone")}
    assert list(result).index("continuity") == 2
    assert encoded.index('"observed_cached_tokens"') < encoded.index('"capability_cards"')
    assert encoded.index('"phase"') < encoded.index('"capability_cards"')
    missing_table = result["NOT_MEASURED"]
    assert len(missing_table["metric_names"]) == len(set(missing_table["metric_names"]))
    shared = result["capability_shared"]
    for before, after in zip(cards, result["capability_cards"]):
        assert all(before[name] == after[name] for name in ("model_id", "native_effort", "action_id", "revision"))
        assert shared["model_pricing"]["currency"] is None
        assert "source_url" not in shared["model_pricing"]
        scopes = missing_table["scope_index_sets"][after["not_measured_ref"]]
        decoded = {scope: [missing_table["metric_names"][index] for index in indexes]
                   for scope, indexes in scopes.items()}
        for scope, field in (("model", "model_metrics"), ("effort", "action_metrics")):
            expected_missing = {metric["metric_name"] for metric in before.get(field, [])
                                if metric.get("evidence_status") != "MEASURED" or metric.get("score_raw") is None}
            assert set(decoded.get(scope, []) + decoded.get("model_and_effort", [])) == expected_missing
    measured = dict(zip(result["metric_fields"], result["capability_cards"][0]["model_metrics"][0]))
    assert measured == {name: cards[0]["model_metrics"][0][name] for name in result["metric_fields"]}
    assert measured["score_raw"] == 0 and measured["score_scope"] == "model"
    assert measured["evaluated_native_effort"] is None
    assert result["continuity"]["observed_cached_tokens"] == 3136
    assert result["continuity"]["physical_kv_cache_shared"] is None
    assert result["continuity"]["previous_equals_current"] == [
        "selected_model_id", "actual_backend_model_id", "router_checkpoint_id"]
    assert not any(name.startswith("previous_") and name != "previous_equals_current"
                   for name in result["continuity"])
    assert result["continuity"]["backend_deployment_status"] == payload["continuity"]["backend_deployment_status"]
    assert result["history_snippet"] == payload["history_snippet"]
    assert result["last_observation_summary"] == payload["last_observation_summary"]
    assert "reference_ids" not in encoded and "missing_reason" not in encoded
    prefix = {name: value for name, value in result.items() if name not in ("history_snippet", "last_observation_summary")}
    critical = {}
    for name, value in result.items():
        critical[name] = value
        if name == "capability_cards":
            break
    print(json.dumps({"fixture_raw_chars": len(json.dumps(payload, ensure_ascii=False)),
                      "fixture_encoded_chars": len(encoded),
                      "fixture_priority_chars": len(json.dumps(prefix, ensure_ascii=False, separators=(",", ":"))),
                      "fixture_cached_offset_chars": encoded.index('"observed_cached_tokens"'),
                      "fixture_candidates_end_chars": len(json.dumps(critical, ensure_ascii=False, separators=(",", ":"))) }))
    different = deepcopy(payload)
    different["capability_cards"][0]["model_pricing"].update(input_price=2.5, currency="EUR", status="REPORTED")
    different["capability_cards"][2]["action_metrics"].append({"metric_name": "UNIT_EXTRA_MISSING",
        "score_raw": None, "evidence_status": "NOT_MEASURED"})
    different["continuity"].update(previous_actual_backend_model_id="UNIT-previous-backend",
                                    actual_backend_changed=True)
    altered = json.loads(format_router_payload(different))
    assert "model_pricing" not in altered["capability_shared"]
    assert altered["capability_cards"][0]["model_pricing"]["currency"] == "EUR"
    assert altered["capability_cards"][0]["model_pricing"]["input_price"] == 2.5
    assert altered["continuity"]["previous_actual_backend_model_id"] == "UNIT-previous-backend"
    assert "actual_backend_model_id" not in altered["continuity"]["previous_equals_current"]
    assert altered["NOT_MEASURED"]["metric_names"].count("UNIT_EXTRA_MISSING") == 1
    refs = [card["not_measured_ref"] for card in altered["capability_cards"]]
    assert refs[0] == refs[1] and refs[2] != refs[0]
    extra_scope = altered["NOT_MEASURED"]["scope_index_sets"][refs[2]]["effort"]
    assert "UNIT_EXTRA_MISSING" in [altered["NOT_MEASURED"]["metric_names"][index] for index in extra_scope]


@pytest.mark.parametrize("protocol", ["route", "system_one"])
def test_router_client_reorders_only_request_cards(protocol):
    """Unit HTTP response only; preserve the caller's card and option order."""
    import io
    from modelrouter.agent.router_clients import RouterClient

    options = actions()
    raw = {"prompt": "UNIT_TEST_ONLY: Keep the original task.", "capability_cards": [
        {"action_id": action["action_id"], "model_id": action["model"],
         "native_effort": action["native_effort"], "revision": action["revision"]}
        for action in sorted(options, key=lambda action: action["action_id"], reverse=True)]}
    original, original_options = deepcopy(raw), deepcopy(options)
    expected = sorted(options, key=lambda action: action["action_id"])
    captured = []

    def open_response(request, **kwargs):
        payload = json.loads(request.data)
        captured.append(payload)
        if protocol == "system_one":
            keys = list(payload["questions"]["route_decision"]["criteria"])
            body = {"router_family": "laya", "checkpoint_id": "UNIT-checkpoint", "fallback_used": False,
                "decision_latency_ms": 1.0, "answers": {"route_decision": {
                    "choice": keys[0], "probabilities": {key: float(key == keys[0]) for key in keys}}}}
        else:
            body = {"request_id": payload["request_id"], "router_family": "laya",
                "checkpoint_id": "UNIT-checkpoint", "selected_action": payload["legal_actions"][0],
                "decision_latency_ms": 1.0, "fallback_used": False}
        response = io.BytesIO(json.dumps(body).encode())
        response.status = 200
        return response

    client = RouterClient(protocol=protocol, max_retries=0)
    client._opener = SimpleNamespace(open=open_response)
    decision = client.route("UNIT-episode", "UNIT-decision", raw, options)
    assert raw == original and options == original_options
    assert decision.selected_action["action_id"] == expected[0]["action_id"]
    sent_state = (json.loads(captured[0]["state"]) if protocol == "system_one"
                  else captured[0]["pre_decision_state"])
    assert [card["action_id"] for card in sent_state["capability_cards"]] == [action["action_id"] for action in expected]
    assert [card["action_id"] for card in json.loads(format_router_payload(raw))["capability_cards"]] == [
        card["action_id"] for card in original["capability_cards"]]
    if protocol == "system_one":
        assert list(captured[0]["questions"]["route_decision"]["criteria"].values()) == [
            f"{action['provider']}/{action['model']} (effort={action['native_effort']})" for action in expected]


@pytest.mark.parametrize("change,reason", [("phase", "PHASE_CHANGED"),
    ("test", "NEW_VERIFICATION_RESULT"), ("error", "REPEATED_ERROR")])
def test_trigger_counts_generations_and_uses_observed_events(change, reason):
    state, trigger = state_for(), TeacherTrigger()
    assert trigger.reason(state) is None
    state.step_index = 9
    assert trigger.reason(state) is None
    for _ in range(3):
        trigger.after_generation()
    assert trigger.reason(state) == "INITIAL_THREE_GENERATIONS"
    trigger.record_attempt(state)
    assert trigger.reason(state) is None
    trigger.after_generation()
    state.step_index += 1
    if change == "phase":
        state.current_phase = "modify"
    elif change == "test":
        add_tool(state, "pytest unit_test.py", "unit test output")
    else:
        add_tool(state, "python unit.py", "unit error", 1, step=9)
        add_tool(state, "python unit.py", "unit error", 1)
    assert trigger.reason(state) == reason
    trigger.record_attempt(state)
    trigger.after_generation()
    assert trigger.reason(state) is None


def test_terminal_task_does_not_force_teacher():
    state, trigger = state_for(), TeacherTrigger()
    trigger.reason(state)
    for _ in range(3):
        trigger.after_generation()
    state.finish(EpisodeStatus.SUCCESS)
    assert trigger.reason(state) is None


def test_last_generation_slot_does_not_force_teacher():
    state, trigger = state_for(), TeacherTrigger()
    trigger.reset(state.episode_id)
    for _ in range(3):
        trigger.after_generation()
    state.step_index = state.max_steps - 1
    assert trigger.reason(state) is None


def test_hook_reuses_assessment_but_not_across_episodes(tmp_path, references):
    state, provider = state_for(), FixtureProvider()
    hook = hook_for(tmp_path, references, provider)
    for index in range(3):
        assert before(hook, state)["teacher_assessment"] is None
        hook.after_generation({"returned_model_id": "Qwen3.8-27B"}, actions()[index])
        state.step_index += 1
    assessed = before(hook, state)
    assert len(provider.calls) == 1 and provider.calls[0]["teacher"]
    assert provider.calls[0]["tools"] is None and provider.calls[0]["stream"] is False
    assert provider.calls[0]["model_id"] == "gpt-6.1-sol"
    assert assessed["teacher_assessment"]["assessed_through_step"] == 3
    assert hook.teacher_metrics[0]["execution_mode"] == "TEACHER_ALIAS_SMOKE"
    assert hook.teacher_metrics[0]["assessment_consumed_by_router"] is False
    hook.after_route(RouterDecision("unit-route", "laya", "UNIT_TEST_ONLY", actions()[0]))
    assert hook.teacher_metrics[0]["assessment_consumed_by_router"] is True
    hook.after_generation({"returned_model_id": "Qwen3.8-27B", "cached_tokens": None}, actions()[1])
    state.step_index += 1
    assert before(hook, state)["teacher_assessment"] == assessed["teacher_assessment"]
    assert len(provider.calls) == 1
    hook.after_route(RouterDecision("unit-fallback", "laya", "UNIT_TEST_ONLY", actions()[1],
                                    fallback_used=True))
    assert hook.teacher_metrics[0]["assessment_consumed_by_router"] is True
    assert hook.continuity["logical_model_changed"] is True
    assert hook.continuity["actual_backend_changed"] is False
    assert hook.continuity["observed_cached_tokens"] is None
    assert before(hook, state_for("new-unit-episode"))["teacher_assessment"] is None
    assert hook.teacher_metrics == []
    disabled = hook_for(tmp_path, references, provider, teacher_enabled=False)
    state.step_index = 3
    before(disabled, state)
    for _ in range(3):
        disabled.after_generation({}, actions()[0])
    assert before(disabled, state)["teacher_assessment"] is None
    assert len(provider.calls) == 1


@pytest.mark.parametrize("failure", [TimeoutError("unit failure body"), "invalid_json"])
def test_teacher_failure_is_recorded_once_and_returns_no_assessment(tmp_path, references, failure):
    provider, state = FixtureProvider(teacher_error=failure), state_for()
    hook = hook_for(tmp_path, references, provider)
    before(hook, state)
    for _ in range(3):
        hook.after_generation({}, actions()[0])
        state.step_index += 1
    assert before(hook, state)["teacher_assessment"] is None
    assert before(hook, state)["teacher_assessment"] is None
    assert len(provider.calls) == 1
    assert len(hook.teacher_metrics) == 1
    assert hook.teacher_metrics[0]["status"] == "FAILED"
    assert "unit failure body" not in json.dumps(hook.teacher_metrics)
    assert state.status == EpisodeStatus.INITIALIZED


def model_for(tmp_path, references, provider, monkeypatch, **config):
    model = PolicyModel(policy="laya", state=state_for(), record_dir=tmp_path / "model-run",
                        provider=provider, model_name="openai/gpt-6-luna",
                        v9_config={"router_endpoint": "http://unit-only.invalid",
                                   "references_path": references, "capability_snapshot": {}, **config})
    routed = []
    def route(**kwargs):
        routed.append(deepcopy(kwargs))
        selected = kwargs["legal_actions"][(len(routed) - 1) % 3]
        return RouterDecision("unit-route", "laya", "UNIT_TEST_ONLY", selected)
    monkeypatch.setattr(model.policy.client, "route", route)
    return model, routed


def test_v9_router_timeout_reaches_existing_client(tmp_path, references):
    """Unit HTTP responses only; timeout settings use the original client."""
    import io

    config = {"router_endpoint": "http://unit-only.invalid", "references_path": references,
              "capability_snapshot": {}, "teacher_enabled": False}
    cases = [("kev", config, 60.0), ("laya", config, 20.0),
             ("kev", dict(config, router_timeout_sec=75.0), 75.0),
             ("laya", dict(config, router_timeout_sec=45.0), 45.0),
             ("kev", None, 20.0),
             ("kev", dict(config, enabled=False, router_timeout_sec=75.0), 20.0)]
    for index, (policy, v9_config, expected) in enumerate(cases):
        provider = FixtureProvider()
        model = PolicyModel(policy=policy, state=state_for(), record_dir=tmp_path / f"timeout-{index}",
                            provider=provider, model_name="openai/gpt-6-luna", v9_config=v9_config)
        client, received = model.policy.client, []

        def open_response(request, **kwargs):
            received.append(kwargs["timeout"])
            payload = json.loads(request.data)
            body = {"router_family": client.router_family, "checkpoint_id": "UNIT-checkpoint",
                    "decision_latency_ms": 1.0, "fallback_used": False}
            if client.protocol == "system_one":
                keys = list(payload["questions"]["route_decision"]["criteria"])
                body["answers"] = {"route_decision": {"choice": keys[0],
                    "probabilities": {key: float(key == keys[0]) for key in keys}}}
            else:
                body.update(request_id=payload["request_id"], selected_action=payload["legal_actions"][0])
            response = io.BytesIO(json.dumps(body).encode())
            response.status = 200
            return response

        client._opener = SimpleNamespace(open=open_response)
        decision = client.route("UNIT-episode", "UNIT-decision", {"prompt": "Unit timeout input"}, model.actions)
        assert model.policy.client is client
        assert client.timeout == expected and received == [expected]
        assert not decision.fallback_used and provider.calls == []


@pytest.mark.parametrize("cost_status", ["LOCAL_COMPUTE_UNPRICED", "BACKEND_PRICE_NOT_MEASURED"])
def test_policy_model_uses_three_candidates_and_preserves_unknown_usd(tmp_path, references, monkeypatch, cost_status):
    provider = FixtureProvider(cost_status=cost_status)
    model, routed = model_for(tmp_path, references, provider, monkeypatch)
    messages = [{"role": "user", "content": "Unit task"}]
    for _ in range(4):
        model._query(messages)
        assert model._calculate_cost(None)["cost"] == 0
    assert [len(call["pre_decision_state"]["prompt"]) for call in routed] == [9] * 4
    assert routed[2]["pre_decision_state"]["teacher_assessment"] is None
    assert routed[3]["pre_decision_state"]["teacher_assessment"]["progress_summary"] == "unit-only progress"
    assert {action["model"] for action in model.actions} == set(V9_MODEL_IDS)
    assert {action["native_effort"] for action in model.actions} == {"none"}
    assert model.policy.client.protocol == "system_one"
    assert model.complete_episode_cost_usd is None
    assert all(row["cost_usd"] is None for row in model.usage + model.teacher_metrics)
    assert model.serialize()["info"]["v9"]["complete_episode_cost_usd"] is None
    assert all(call["messages"] == messages for call in provider.calls if not call["teacher"])


@pytest.mark.parametrize("teacher_error", [None, "invalid_json"])
def test_known_teacher_cost_is_included_once(tmp_path, references, monkeypatch, teacher_error):
    model, _ = model_for(tmp_path, references, FixtureProvider(
        cost=0.2, teacher_cost=0.1, teacher_error=teacher_error), monkeypatch)
    for _ in range(4):
        model._query([{"role": "user", "content": "Unit task"}])
    assert model._calculate_cost(None)["cost"] == pytest.approx(0.3)
    assert model.complete_episode_cost_usd == pytest.approx(0.9)
    assert model.state.accumulated_cost_usd == pytest.approx(0.9)


def test_missing_references_skip_request_and_keep_generator_cost(tmp_path, monkeypatch):
    provider = FixtureProvider(cost=0.2)
    model, routed = model_for(tmp_path, tmp_path / "absent-references.json", provider, monkeypatch)
    for _ in range(4):
        model._query([{"role": "user", "content": "Unit task"}])
    assert len(provider.calls) == 4 and not any(call["teacher"] for call in provider.calls)
    assert model.teacher_metrics[0]["provider_request_attempted"] is False
    assert model.teacher_metrics[0]["error_type"] == "FileNotFoundError"
    assert routed[-1]["pre_decision_state"]["teacher_assessment"] is None
    assert model.complete_episode_cost_usd == pytest.approx(0.8)


def test_v9_upstream_loop_preserves_submission_and_decision_feedback(tmp_path, references, monkeypatch):
    from minisweagent.agents.default import DefaultAgent
    from modelrouter.benchmark.iterations import rows
    from modelrouter.v9.runtime.development import RecordedLocalEnvironment

    provider = LoopProvider([
        "printf 'unit-first\\n'", "printf 'unit-second\\n'", "printf 'unit-third\\n'",
        "printf 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\\nunit submission\\n'",
    ])
    model, routed = model_for(tmp_path, references, provider, monkeypatch,
                              capability_snapshot={"snapshot_id": "UNIT_TEST_ONLY-snapshot"})
    environment = RecordedLocalEnvironment(state=model.state, record_dir=model.record_dir,
                                            cwd=str(tmp_path))
    agent = DefaultAgent(model, environment, system_template="Unit exercise", instance_template="{{task}}",
                         step_limit=6, cost_limit=0, output_path=tmp_path / "unit-trajectory.json")
    result = agent.run("Unit task")
    assert result["exit_status"] == "Submitted"
    assert result["submission"] == "unit submission\n"
    assert agent.n_calls == len(model.usage) == len(model.state.history) == 4
    assert len([call for call in provider.calls if call["teacher"]]) == 1
    generator_calls = [call for call in provider.calls if not call["teacher"]]
    assert "unit-first" in json.dumps(generator_calls[1]["messages"])
    assert "unit-second" in json.dumps(generator_calls[2]["messages"])
    assert "unit-third" in json.dumps(generator_calls[3]["messages"])
    assert [call["decision_id"] for call in routed] == [f"unit-episode-{index}" for index in range(4)]
    snapshot = routed[-1]["pre_decision_state"]
    assert snapshot["teacher_assessment"]["assessed_through_decision_id"] == "unit-episode-2"
    assert snapshot["agent_context"]["completed_generations"] == 3
    assert snapshot["continuity"]["router_checkpoint_id"] == "UNIT_TEST_ONLY"
    assert snapshot["capability_snapshot_id"] == "UNIT_TEST_ONLY-snapshot"
    tools = rows(model.record_dir / "tool_calls.jsonl")
    events = rows(model.record_dir / "events.jsonl")
    assert [row["decision_id"] for row in tools] == [row["decision_id"] for row in model.usage]
    assert tools[-1]["output"] == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\nunit submission\n"
    assert tools[-1]["submission"] is True and tools[-1]["exit_code"] == 0
    assert model.state.history[-1].selected_action == model.actions[0]
    assert all(row["router_checkpoint_id"] == "UNIT_TEST_ONLY" for row in tools)
    assert len([row for row in events if row["event"] == "TEACHER_END"]) == 1
    assert model.complete_episode_cost_usd is None


@pytest.mark.parametrize("submit", [True, False])
def test_development_result_keeps_upstream_exit_and_bound_snapshot(tmp_path, monkeypatch, submit):
    from modelrouter.v9.runtime import development

    workspace, record_dir = tmp_path / "workspace", tmp_path / "unit-run"
    workspace.mkdir()
    prefix = "UNIT_TEST_ONLY task "
    instruction = prefix + "x" * (1019 - len(prefix))
    command = "printf 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT\\nunit final\\n'" if submit else "printf 'unit tool\\n'"
    provider = LoopProvider([command])
    recorded, routed = [], []
    monkeypatch.setattr(development, "alias_provider", lambda config, api_key: provider)
    monkeypatch.setattr(development, "ExperimentLedger", lambda: SimpleNamespace(
        record_development_episode=recorded.append))
    from modelrouter.agent.router_clients import RouterClient
    def route(self, **kwargs):
        routed.append(deepcopy(kwargs["pre_decision_state"]))
        return RouterDecision("unit-route", "laya", "UNIT_TEST_ONLY-checkpoint", kwargs["legal_actions"][0])
    monkeypatch.setattr(RouterClient, "route", route)
    result = development.run_development(
        workspace=workspace, instruction=instruction, verify_command="printf 'unit verifier\\n'",
        config={"base_url": "http://unit-only.invalid", "actual_backend_model_id": "Qwen3.8-27B",
                "router_endpoint": "http://unit-only.invalid", "teacher_enabled": False,
                "router_context_chars": 2300,
                "capability_snapshot": {"snapshot_id": "UNIT_TEST_ONLY-bound"}},
        record_dir=record_dir, task_id="UNIT_TEST_ONLY", max_steps=1, api_key="UNIT_TEST_ONLY",
    )
    assert result["status"] == ("RUNTIME_VERIFIED" if submit else "FAILED")
    assert result["agent_exit_status"] == ("Submitted" if submit else "LimitsExceeded")
    assert result["verification_exit_code"] == 0
    assert result["official_result_eligible"] is result["scientific_result_eligible"] is False
    assert result["capability_snapshot_id"] == "UNIT_TEST_ONLY-bound"
    assert result["router_checkpoint_ids"] == ["UNIT_TEST_ONLY-checkpoint"]
    assert result["total_cost_usd"] is None
    assert recorded == [result]
    run_config = json.loads((record_dir / "run_config.json").read_text())
    assert run_config["capability_snapshot_id"] == "UNIT_TEST_ONLY-bound"
    assert run_config["instruction"].startswith(instruction + "\n\n")
    assert str(workspace.resolve()) in run_config["instruction"] and len(run_config["instruction"]) < 2000
    assert routed[0]["prompt"] == run_config["instruction"]
    initial_user = next(message["content"] for message in provider.calls[0]["messages"] if message["role"] == "user")
    assert run_config["instruction"] in initial_user


def test_default_policy_model_keeps_previous_pipeline(tmp_path):
    model = PolicyModel(policy="fixed_strong", state=state_for(), record_dir=tmp_path / "old-run",
                        provider=FixtureProvider(), model_name="openai/gpt-6-luna")
    assert model.v9_hook is None
    assert {action["model"] for action in model.actions} == {"gpt-6-luna", "gpt-5.6-luna"}
    model._query([{"role": "user", "content": "Unit task"}])
    with pytest.raises(ValueError):
        model._calculate_cost(None)


def test_alias_credential_source_stays_private(tmp_path, monkeypatch):
    """One unit source exercise; no real credentials or API requests."""
    import os
    import shlex
    import sys
    from modelrouter.agent.router_clients import RouterClient
    from modelrouter.providers import provider as provider_module
    from modelrouter.v9.runtime import alias, development

    explicit_key, env_key, source_key = (f"UNIT_TEST_ONLY-{name}" for name in ("explicit", "env", "source"))
    source = tmp_path / "unit-source.toml"
    source.write_text('[model_providers.ccswitch]\nexperimental_bearer_token = "' + source_key + '"\n')
    private_names = ("UNIT_ALIAS_TOKEN", "OPENAI_API_KEY", "QWEN_API_KEY", "UNIT_EXTRA_API_KEY")
    for name in private_names:
        monkeypatch.setenv(name, env_key)
    script = ("import os; assert not any(os.environ.get(name) for name in " + repr(private_names) + "); "
              "print('COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'); print('unit isolation')")
    command = shlex.quote(sys.executable) + " -c " + shlex.quote(script)
    instances = []
    def make_provider(**kwargs):
        instance = LoopProvider([command])
        instance.api_key, instance.alias_mapping = kwargs["api_key"], kwargs["alias_mapping"]
        instances.append(instance)
        return instance
    monkeypatch.setattr(provider_module, "OpenAICompatibleProvider", make_provider)
    config = {
        "base_url": "http://unit-only.invalid", "actual_backend_model_id": "Qwen3.8-27B",
        "router_endpoint": "http://unit-only.invalid", "teacher_enabled": False,
        "capability_snapshot": {}, "api_key_env": "UNIT_ALIAS_TOKEN",
        "credential_file": str(source),
        "credential_field": "model_providers.ccswitch.experimental_bearer_token",
        "backend_deployment_status": "API_IDENTITY_ONLY_UNVERIFIED_PHYSICAL_BACKEND",
        "api_key": "UNIT_TEST_ONLY-unused-config",
    }
    assert alias.alias_provider(config, explicit_key).api_key == explicit_key
    assert alias.alias_provider(config, "").api_key == ""
    assert alias.alias_provider(config).api_key == env_key
    monkeypatch.delenv("UNIT_ALIAS_TOKEN")
    assert alias.alias_provider(config).api_key == source_key
    assert "experimental_bearer_token" not in config
    import dotenv
    env_source = tmp_path / "unit-source.local.env"
    env_source.write_text("OTHER_PROVIDER_API_KEY=UNIT_TEST_ONLY-other\n"
                          "export QWEN_API_KEY = '" + source_key + "' # unit field\n"
                          "SECOND_PROVIDER_API_KEY=UNIT_TEST_ONLY-second\n")
    original_dotenv_values = dotenv.dotenv_values
    def selected_dotenv_values(**kwargs):
        assert "OTHER_PROVIDER" not in kwargs["stream"].getvalue()
        assert "SECOND_PROVIDER" not in kwargs["stream"].getvalue()
        assert kwargs["interpolate"] is False
        return original_dotenv_values(**kwargs)
    monkeypatch.setattr(dotenv, "dotenv_values", selected_dotenv_values)
    config.update(credential_file=str(env_source), credential_field="QWEN_API_KEY")
    assert alias.alias_provider(config).api_key == source_key
    monkeypatch.setenv("UNIT_ALIAS_TOKEN", env_key)
    from modelrouter.benchmark import harbor_agent
    original_configuration = harbor_agent.mini_configuration
    def mini_configuration(**kwargs):
        result = original_configuration(**kwargs)
        result["model"]["model_kwargs"].update(
            api_key="UNIT_TEST_ONLY-model-config",
            extra_headers={"Authorization": "Bearer UNIT_TEST_ONLY-header", "X-Unit": "public"})
        return result
    monkeypatch.setattr(harbor_agent, "mini_configuration", mini_configuration)
    monkeypatch.setattr(development, "ExperimentLedger", lambda: SimpleNamespace(record_development_episode=lambda result: None))
    monkeypatch.setattr(RouterClient, "route", lambda self, **kwargs: RouterDecision(
        "unit-route", "laya", "UNIT_TEST_ONLY-checkpoint", kwargs["legal_actions"][0]))
    workspace, record_dir = tmp_path / "workspace", tmp_path / "unit-record"
    workspace.mkdir()
    monkeypatch.setenv("MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT", "7")
    monkeypatch.delenv("LITELLM_LOCAL_MODEL_COST_MAP", raising=False)
    result = development.run_development(
        workspace=workspace, instruction="Unit credential isolation", verify_command=command,
        config=config, record_dir=record_dir, task_id="UNIT_TEST_ONLY", max_steps=1, api_key=source_key)
    assert result["status"] == "RUNTIME_VERIFIED"
    assert result["verification_exit_code"] == 0
    assert instances[-1].api_key == source_key
    assert os.environ["MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT"] == "7"
    assert "LITELLM_LOCAL_MODEL_COST_MAP" not in os.environ
    assert all(os.environ[name] == env_key for name in private_names)
    outputs = "\n".join(path.read_text() for path in record_dir.iterdir() if path.is_file())
    assert not any(value in outputs for value in (
        explicit_key, env_key, source_key, "UNIT_TEST_ONLY-unused-config",
        "UNIT_TEST_ONLY-model-config", "UNIT_TEST_ONLY-header"))
    run_config = json.loads((record_dir / "run_config.json").read_text())
    assert run_config["upstream_runtime_options"] == {
        "MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT": "1", "LITELLM_LOCAL_MODEL_COST_MAP": "true"}
    trajectory = json.loads((record_dir / "mini-swe-agent.trajectory.json").read_text())
    assert run_config["backend_deployment_status"] == result["backend_deployment_status"]
    assert trajectory["info"]["v9"]["backend_deployment_status"] == result["backend_deployment_status"]
    assert "api_key" not in trajectory["info"]["config"]["model"]["model_kwargs"]
    assert "Authorization" not in trajectory["info"]["config"]["model"]["model_kwargs"]["extra_headers"]
