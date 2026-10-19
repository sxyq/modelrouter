"""Fixture-only input mapping; no weights or network inference."""
import io
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modelrouter.agent.router_clients import RouterClient, MockRouter
from modelrouter.providers.registry import ModelRegistry
from modelrouter.serving.schemas import LegalAction, PreDecisionState, RouteRequest
from modelrouter.serving.laya_adapter import LayaAdapter
from modelrouter.serving.kev_adapter import KevAdapter


@pytest.fixture
def actions():
    return [LegalAction(**a) for a in ModelRegistry().list_legal_actions() if a["model"] in ("gpt-6-luna", "gpt-5.6-luna")]


@pytest.fixture
def state():
    return PreDecisionState(task_id="fixture-task", prompt="Fix one parser", step_index=2, history_snippet="prior echo output", budget_remaining_usd=1.0)


def test_schema_preserves_action_ids_and_state(actions, state):
    req = RouteRequest(request_id="fixture", pre_decision_state=state, legal_actions=actions)
    assert RouteRequest.model_validate_json(req.model_dump_json()) == req
    assert req.legal_actions[0].action_id == actions[0].action_id
    assert "fixture-task" in req.pre_decision_state.router_text()
    with pytest.raises(ValueError):
        LegalAction(provider="jiji", model="gpt-6-luna", native_effort="invalid")
    with pytest.raises(ValueError):
        LegalAction(provider="jiji", model="gpt-6-luna", action_id="wrong:none")


@pytest.mark.parametrize("count", [1, 2, 4, 8])
def test_laya_fixture_stable_ids_after_permutation(actions, state, count):
    adapter = LayaAdapter.__new__(LayaAdapter)
    inputs = []
    def system_one(text, questions):
        inputs.append((text, questions))
        keys = list(questions["route_decision"]["criteria"])
        return {"answers": {"route_decision": {"choice": keys[-1], "probabilities": {key: float(key == keys[-1]) for key in keys}, "confidence": 1.0}}}
    adapter.agent = SimpleNamespace(system_one=system_one)
    subset = actions[:count]
    first = adapter.route(state, subset)
    repeat = adapter.route(state, subset)
    reverse = adapter.route(state, list(reversed(subset)))
    assert first[0].action_id == repeat[0].action_id == reverse[0].action_id
    assert first[1] == repeat[1] == reverse[1]
    assert inputs[0] == inputs[1] == inputs[2]


@pytest.mark.parametrize("count", [1, 2, 4, 8])
def test_kev_fixture_stable_ids_after_permutation(monkeypatch, actions, state, count):
    records = []
    def admit(model, tokenizer, record):
        records.append(record)
        return record
    monkeypatch.setitem(sys.modules, "kev.model", SimpleNamespace(admit=admit))
    adapter = KevAdapter.__new__(KevAdapter)
    adapter.tokenizer = object()
    adapter.model = SimpleNamespace(probs=lambda record: [[0.0] * (len(record["questions"][0]["options"]) - 1) + [1.0]])
    first = adapter.route(state, actions[:count])
    repeat = adapter.route(state, actions[:count])
    reverse = adapter.route(state, list(reversed(actions[:count])))
    assert first[0].action_id == repeat[0].action_id == reverse[0].action_id
    assert first[1] == reverse[1]
    assert not first[4]
    assert records[0] == records[1] == records[2]
    assert records[0]["state"] == state.router_text()


def test_kev_dimension_error_is_marked_fallback(monkeypatch, actions, state):
    monkeypatch.setitem(sys.modules, "kev.model", SimpleNamespace(admit=lambda *args: {}))
    adapter = KevAdapter.__new__(KevAdapter)
    adapter.tokenizer = object()
    adapter.model = SimpleNamespace(probs=lambda enc: [[1.0]])
    result = adapter.route(state, actions[:2])
    assert result[4] is True


def test_laya_wrong_probability_ids_rejected(actions, state):
    adapter = LayaAdapter.__new__(LayaAdapter)
    adapter.agent = SimpleNamespace(system_one=lambda *args: {"answers": {"route_decision": {"choice": "other", "probabilities": {"other": 1.0}}}})
    with pytest.raises(ValueError, match="probability IDs"):
        adapter.route(state, actions[:2])


def test_router_client_uses_service_schema(actions, state):
    client = RouterClient(max_retries=0)
    captured = []
    def open_response(request, **kwargs):
        req = json.loads(request.data)
        captured.append(req)
        body = {"request_id": req["request_id"], "router_family": "laya", "checkpoint_id": "fixture", "selected_action": req["legal_actions"][1], "ranked_actions_or_scores_if_available": [{"action": req["legal_actions"][1], "score": 0.8, "probability": 0.8}], "decision_latency_ms": 2.5, "confidence_if_defined": 0.8, "fallback_used": False}
        response = io.BytesIO(json.dumps(body).encode())
        response.status = 200
        return response
    client._opener = SimpleNamespace(open=open_response)
    result = client.route("ep", "dec", state.model_dump(), [a.model_dump() for a in actions])
    assert result.selected_action["action_id"] == sorted(actions, key=lambda a: a.action_id)[1].action_id
    assert result.confidence == 0.8
    assert result.inference_latency_ms == 2.5
    assert result.ranked_actions[0]["probability"] == 0.8
    assert not result.fallback_used
    assert captured[0]["pre_decision_state"]["task_id"] == "fixture-task"
    client.route("ep", "dec", state.model_dump(), [a.model_dump() for a in reversed(actions)])
    assert captured[0]["legal_actions"] == captured[1]["legal_actions"]
    for request in captured:
        request.pop("request_id")
    assert captured[0] == captured[1]
    assert MockRouter.route("laya", {}, [a.model_dump() for a in actions]).fallback_used
