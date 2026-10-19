"""CPU unit exercises of the installed upstream task loop; no benchmark scores."""
from importlib.metadata import version

from minisweagent.agents.default import DefaultAgent
from minisweagent.environments.local import LocalEnvironment
from minisweagent.models.test_models import DeterministicModel, make_output


def test_upstream_install_loop_observation_and_submission(tmp_path):
    assert version("mini-swe-agent").startswith("2.")
    model = DeterministicModel(outputs=[
        make_output("inspect", [{"command": "printf mini-unit"}], cost=0),
        make_output("submit", [{"command": "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"}], cost=0),
    ], cost_per_call=0)
    agent = DefaultAgent(model, LocalEnvironment(cwd=str(tmp_path)),
                         system_template="unit exercise", instance_template="{{task}}",
                         output_path=tmp_path / "trajectory.json")
    result = agent.run("exercise official loop")
    assert result["exit_status"] == "Submitted"
    assert agent.n_calls == 2
    assert "mini-unit" in agent.messages[3]["content"]
    assert (tmp_path / "trajectory.json").is_file()


def test_upstream_model_loop_uses_native_relay_without_extra_tool_execution(tmp_path, monkeypatch):
    import json
    import litellm
    from minisweagent.models.litellm_model import LitellmModel
    from modelrouter.providers import provider
    from modelrouter.benchmark.harbor_agent import mini_configuration

    class FixtureProvider:
        calls = 0
        def query_raw(self, messages, model_spec, native_effort, max_tokens, tools, stream):
            assert stream is True
            self.calls += 1
            command = "printf native-relay-tool" if self.calls == 1 else "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
            body = {"id": f"fixture-{self.calls}", "object": "chat.completion", "created": 1,
                    "model": model_spec.model_id,
                    "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {"role": "assistant", "content": "fixture", "tool_calls": [
                        {"id": f"call-{self.calls}", "type": "function", "function": {"name": "bash", "arguments": json.dumps({"command": command})}}]}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5}}
            return body, {"request_model_id": model_spec.model_id, "returned_model_id": model_spec.model_id,
                          "native_effort": native_effort, "prompt_tokens": 10, "completion_tokens": 5,
                          "protocol": "chat_completions", "cost_usd": .00006, "ttft_ms": 1,
                          "latency_ms": 2, "output_tokens_per_s": 2500, "budget_accounted": True}

    monkeypatch.setattr(provider, "OpenAICompatibleProvider", FixtureProvider)
    monkeypatch.setenv("MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT", "1")
    litellm.utils.register_model({"openai/gpt-6-luna": {"input_cost_per_token": 2 / 1e6,
                                  "output_cost_per_token": 8 / 1e6,
                                  "supports_function_calling": True, "supports_reasoning": True,
                                  "litellm_provider": "openai", "mode": "chat"}})
    config = mini_configuration(30)
    config["agent"].pop("mode")
    with provider.native_generator_relay(tmp_path, bind="127.0.0.1") as relay:
        model = LitellmModel(model_name="openai/gpt-6-luna", **config["model"])
        model.config.model_kwargs.update(api_base=f"http://127.0.0.1:{relay['port']}/v1", api_key=relay["api_key"],
                                        reasoning_effort="low", max_tokens=128,
                                        timeout=5, num_retries=0,
                                        extra_headers={"X-Session-ID": "fixture-native-episode"})
        agent = DefaultAgent(model, LocalEnvironment(cwd=str(tmp_path)), **config["agent"],
                             output_path=tmp_path / "native.trajectory.json")
        result = agent.run("fixture task")
    assert result["exit_status"] == "Submitted"
    assert agent.n_calls == 2
    assert "native-relay-tool" in agent.messages[3]["content"]
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    generated = [e for e in events if e["event"] == "GENERATOR_END"]
    assert [e["step"] for e in generated] == [0, 1]
    assert all(e["episode_id"] == "fixture-native-episode" for e in generated)
