"""Integration fixtures for the real mini loop; these are not official trials."""
import asyncio
import json
import io
from types import SimpleNamespace

import pytest
from harbor.agents.base import BaseAgent
from harbor.models.agent.context import AgentContext
from modelrouter.agent.router_clients import RouterClient, RouterDecision
from modelrouter.benchmark import harbor_agent
from modelrouter.agent.state import AgentState, StepTrace
from modelrouter.baselines.policy import create_policy
from modelrouter.serving.schemas import LegalAction


class FixtureProvider:
    def __init__(self):
        self.count = 0

    def query_raw(self, messages, spec, effort, max_tokens, tools, stream):
        assert tools == [harbor_agent.BASH_TOOL]
        assert stream is True
        spec.validate_effort(effort)
        self.count += 1
        command = "echo fixture-output" if self.count == 1 else "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
        body = {"model": spec.model_id, "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
            "role": "assistant", "content": "fixture", "tool_calls": [{"id": f"call{self.count}",
            "type": "function", "function": {"name": "bash", "arguments": json.dumps({"command": command})}}]}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
        metrics = {"cost_usd": .001, "returned_model_id": spec.model_id, "usage_status": "REPORTED",
                   "requested_model_id": spec.model_id, "request_model_id": spec.model_id,
                   "native_effort": effort, "protocol": "chat_completions", "raw_usage": body["usage"],
                   "budget_accounted": True, "cost_status": "FIXTURE", "actual_billed_cost_usd": None,
                   "prompt_tokens": 10, "completion_tokens": 5, "cached_tokens": 0,
                   "ttft_ms": 2, "latency_ms": 10, "output_tokens_per_s": 500}
        return body, metrics


class FixtureEnvironment:
    async def exec(self, command, timeout_sec):
        if command == "uname -s && uname -r && uname -v && uname -m":
            output = "Linux\nunit-test\nfixture-kernel-version\nx86_64"
        elif command == "echo fixture-output":
            output = "fixture-output"
        else:
            assert command == "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
            output = "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
        return SimpleNamespace(stdout=output, stderr="", return_code=0)


@pytest.mark.parametrize("policy", ["fixed_strong", "fixed_cheap", "random", "rule_sticky",
                                    "routellm", "sr_knn", "laya_v2", "kev_4b", "joint_laya", "joint_kev"])
def test_same_official_loop_for_all_policies(tmp_path, monkeypatch, policy):
    monkeypatch.setattr(harbor_agent, "OpenAICompatibleProvider", FixtureProvider)
    monkeypatch.setenv("MODELROUTER_ITERATION", str(tmp_path))
    (tmp_path / "config.json").write_text(json.dumps({"task": {"name": "terminal-bench/fix-git", "ref": "test-version"}, "trial_name": "fix-git__random-suffix"}))
    (tmp_path / "result.json").write_text(json.dumps({"future_verifier_result": "FUTURE_SENTINEL"}))

    def route(self, **kwargs):
        return RouterDecision(request_id="unit", router_family="unit_fixture", checkpoint_id="unit_fixture",
                              selected_action=kwargs["legal_actions"][0], ranked_actions=kwargs["legal_actions"],
                              decision_latency_ms=1, fallback_used=False, confidence=1)

    monkeypatch.setattr(RouterClient, "route", route)
    agent = harbor_agent.ModelRouterMiniSweAgent(logs_dir=tmp_path / "agent", policy=policy)
    assert isinstance(agent, BaseAgent)
    context = AgentContext()

    async def run():
        environment = FixtureEnvironment()
        await agent.setup(environment)
        await agent.run("fixture task", environment, context)

    asyncio.run(run())
    trajectory = json.loads((tmp_path / "agent/mini-swe-agent.trajectory.json").read_text())
    assert trajectory["info"]["exit_status"] == "Submitted"
    assert trajectory["info"]["config"]["agent_type"] == "minisweagent.agents.default.DefaultAgent"
    assert context.n_input_tokens == 20
    assert context.cost_usd == .002
    assert "fixture-output" in trajectory["messages"][3]["content"]
    tools = [json.loads(line) for line in (tmp_path / "tool_calls.jsonl").read_text().splitlines()]
    assert len([t for t in tools if t["kind"] == "agent_tool"]) == 2
    assert len([t for t in tools if t["kind"] == "agent_setup"]) == 1
    assert context.metadata["task_id"] == "terminal-bench/fix-git"
    assert context.metadata["fallback_used"] is False
    assert context.metadata["actual_billed_cost_usd"] is None
    atif = json.loads((tmp_path / "agent/trajectory.json").read_text())
    assert atif["schema_version"] == "ATIF-v1.7"
    from harbor.models.trajectories.trajectory import Trajectory
    Trajectory.model_validate(atif)
    generated = [step for step in atif["steps"] if step["source"] == "agent"]
    assert len(generated) == 2
    assert all(step["model_name"] in ("gpt-6-luna", "gpt-5.6-luna") for step in generated)
    assert sum(step["metrics"]["cost_usd"] for step in generated) == .002
    assert context.metadata["policy_implementation_status"] == (
        "UNVERIFIED_EXAMPLE" if policy in ("routellm", "sr_knn")
        else "REMOTE_NEURAL_ROUTER" if policy in ("laya_v2", "kev_4b", "joint_laya", "joint_kev")
        else "CONFIGURED_POLICY")
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    routes = [entry for entry in events if "pre_decision_state" in entry]
    assert len(routes) == 2
    for route in routes:
        assert route["pre_decision_state"]["task_id"] == "terminal-bench/fix-git"
        assert "fixture task" in route["pre_decision_state"]["prompt"]
        assert "FUTURE_SENTINEL" not in json.dumps(route)
        assert all(action["pool"] == "Reasoning" for action in route["legal_actions"])
        assert all(LegalAction.model_validate(action).model_dump() == action for action in route["legal_actions"])
        assert route["selected_action"]["native_effort"] == ("high" if policy.startswith("joint_") else "low")
    assert "fixture-output" in routes[1]["pre_decision_state"]["history_snippet"]
    assert context.metadata["untested_native_efforts_used"] == (["high"] if policy.startswith("joint_") else [])
    if policy.startswith("joint_") or policy in ("routellm", "sr_knn"):
        assert context.metadata["neural_router_evidence_eligible"] is False


def test_legacy_runner_delegates_to_single_cli(monkeypatch):
    from modelrouter.benchmark.run_official_harbor_trial import run_trial
    from modelrouter.benchmark import __main__
    seen = []
    monkeypatch.setattr(__main__, "main", lambda argv: seen.append(argv) or 0)
    assert run_trial(execute=False) == 0
    assert seen[0][:3] == ["run", "--task", "fix-git"]
    assert "--dry-run" in seen[0]


@pytest.mark.parametrize("policy,expected", [("fixed_strong", "gpt-6-luna"), ("fixed_cheap", "gpt-5.6-luna")])
def test_fixed_price_roles_with_shared_pool(policy, expected):
    state = AgentState(task_id="task", episode_id="ep", policy_id=policy)
    actions = harbor_agent.legal_actions()
    assert {a["native_effort"] for a in actions} == {"low"}
    for ordered in (actions, list(reversed(actions))):
        assert create_policy(policy).select(state, ordered).selected_action["model"] == expected


@pytest.mark.parametrize("phase,error,spent,expected", [
    ("inspect", 0, 0, "gpt-5.6-luna"), ("modify", 0, 0, "gpt-6-luna"),
    ("verify", 0, 0, "gpt-5.6-luna"), ("inspect", 1, 0, "gpt-6-luna"),
    ("modify", 1, 1.8, "gpt-5.6-luna"),
])
def test_rule_price_roles_with_shared_pool(phase, error, spent, expected):
    state = AgentState(task_id="task", episode_id="ep", policy_id="rule_sticky")
    state.current_phase = phase
    state.accumulated_cost_usd = spent
    state.pre_decision_snapshot = state.build_pre_decision_snapshot().to_dict() | {"last_tool_exit_code": error}
    assert create_policy("rule_sticky").select(state, harbor_agent.legal_actions()).selected_action["model"] == expected


@pytest.mark.parametrize("policy", ["routellm", "sr_knn"])
@pytest.mark.parametrize("expensive", [False, True])
def test_example_policies_use_prices_without_relabeling(monkeypatch, policy, expensive):
    state = AgentState(task_id="original-task-id", episode_id="ep", policy_id=policy, max_steps=37, usd_budget=3.0)
    state.task_prompt = "Original task instruction, independent of the task ID"
    selected_policy = create_policy(policy)
    if policy == "routellm":
        def score(**kwargs):
            assert kwargs["instruction"] == state.task_prompt
            assert kwargs["max_steps"] == 37
            assert kwargs["budget_remaining_ratio"] == 1.0
            return SimpleNamespace(win_rate=.9 if expensive else .1)
        monkeypatch.setattr(selected_policy.adapter, "compute_difficulty", score)
    else:
        monkeypatch.setattr(selected_policy.adapter, "predict", lambda vec: {"predicted_tier": "Reasoning" if expensive else "Fast", "confidence": .8})
    actions = harbor_agent.legal_actions()
    for ordered in (actions, list(reversed(actions))):
        decision = selected_policy.select(state, ordered)
        assert decision.selected_action["model"] == ("gpt-6-luna" if expensive else "gpt-5.6-luna")
        assert decision.selected_action["pool"] == "Reasoning"
        assert decision.checkpoint_id == "UNVERIFIED_EXAMPLE"
    assert selected_policy.implementation_status == selected_policy.adapter.status == "UNVERIFIED_EXAMPLE"


def test_hook_complete_prestate_and_canonical_wire_payload(tmp_path):
    payloads = []
    def open_response(request, **kwargs):
        payload = json.loads(request.data)
        payloads.append(payload)
        response = io.BytesIO(json.dumps({"request_id": payload["request_id"], "router_family": "laya", "checkpoint_id": "fixture", "selected_action": payload["legal_actions"][0], "decision_latency_ms": 2.0, "fallback_used": False}).encode())
        response.status = 200
        return response

    for reversed_order in (False, True):
        state = AgentState(task_id="original-task", episode_id="same-episode", policy_id="laya_v2")
        state.task_prompt = "Original task instruction"
        prior_output = "prior-observation-" * 100
        state.history.append(StepTrace(step_index=0, phase="inspect", selected_action={}, thought="", tool_action="echo prior", tool_observation=prior_output, tool_exit_code=7, prompt_tokens=0, completion_tokens=0, reasoning_tokens=0, cached_tokens=0, step_cost_usd=0, step_duration_sec=.1))
        state.last_output = {"returncode": 7, "output": prior_output}
        state.tool_error_count = 1
        model = harbor_agent.PolicyModel(policy="laya_v2", state=state, record_dir=tmp_path,
                                        provider=FixtureProvider(), model_name="openai/gpt-6-luna")
        model.policy.client._opener = SimpleNamespace(open=open_response)
        if reversed_order:
            model.actions.reverse()
        raw = model._query([{"role": "user", "content": state.task_prompt}, {"role": "tool", "content": prior_output}])
        assert raw.choices[0].message.tool_calls[0].function.name == "bash"
        assert model.last_metrics["budget_accounted"] is True
    for payload in payloads:
        payload.pop("request_id")
    assert payloads[0] == payloads[1]
    state = payloads[0]["pre_decision_state"]
    assert state["task_id"] == "original-task"
    assert state["last_observation_summary"] == prior_output
    assert prior_output in state["history_snippet"]
    assert state["last_tool_exit_code"] == 7
    assert state["prior_tool_calls_count"] == state["prior_error_signals_count"] == 1


def test_mock_fallback_is_recorded_without_stopping_loop(tmp_path, monkeypatch):
    from modelrouter.agent.router_clients import MockRouter
    monkeypatch.setattr(harbor_agent, "OpenAICompatibleProvider", FixtureProvider)
    monkeypatch.setenv("MODELROUTER_ITERATION", str(tmp_path))
    monkeypatch.setattr(RouterClient, "route", lambda self, **kwargs: MockRouter.route("laya", kwargs["pre_decision_state"], kwargs["legal_actions"]))
    context = AgentContext()
    agent = harbor_agent.ModelRouterMiniSweAgent(logs_dir=tmp_path / "agent", policy="laya_v2")
    asyncio.run(agent.run("fixture task", FixtureEnvironment(), context))
    assert context.metadata["task_id"] == "unknown"
    assert context.metadata["fallback_used"] is True
    assert context.metadata["neural_router_evidence_eligible"] is False
    trajectory = json.loads((tmp_path / "agent/mini-swe-agent.trajectory.json").read_text())
    assert trajectory["info"]["exit_status"] == "Submitted"
