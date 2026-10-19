"""Offline evidence labels and model/tool timing separation."""
import json
import csv
from pathlib import Path
from types import SimpleNamespace

import pytest

from modelrouter.benchmark import iterations
from modelrouter.telemetry.ledger import ExperimentLedger


def episode(fallback):
    return SimpleNamespace(
        task_id="fixture", episode_id="fixture-episode", policy_id="laya", seed=1,
        status="COMPLETED", resolved=True, score=1.0, total_steps=1, elapsed_time_sec=2.0,
        total_cost_usd=0.1, total_prompt_tokens=10, total_completion_tokens=2,
        total_reasoning_tokens=0, total_cached_tokens=0,
        router_decisions=[{"fallback_used": fallback}], evaluator_details={},
        step_traces=[{"step_index":1,"selected_action":{"provider":"jiji","model":"gpt-6-luna","native_effort":"low","action_id":"gpt-6-luna:low"},"prompt_tokens":10,"completion_tokens":2,"reasoning_tokens":0,"cached_tokens":0,"step_cost_usd":0.1,"step_duration_sec":2.0,"tool_action":"echo fixture","tool_exit_code":0,"tool_observation":"fixture","phase":"inspect","timestamp":0}],
        to_dict=lambda: {"resolved":True},
    )


def test_legacy_success_does_not_become_official(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs", tmp_path / "ledgers")
    path = ledger.record_episode(episode(False))
    record = json.loads((path / "episode.json").read_text())
    assert record["evaluation_status"] == "NOT_EVALUATED"
    assert record["official_result_eligible"] is False
    call = json.loads((path / "model_calls.jsonl").read_text())
    assert call["action"]["action_id"] == "gpt-6-luna:low"
    assert call["episode_step_duration_sec"] == 2.0
    assert call["generator_latency_ms"] is None
    assert call["returned_model_id"] is None
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["pass_at_1"] is None
    assert summary["legacy_pass_at_1"] == 1.0


def test_fallback_is_excluded_from_official_summary(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs", tmp_path / "ledgers")
    result = episode(True)
    result.evaluator_details = {"official_evaluator_executed":True,"job_id":"fixture-job","trial_id":"fixture-trial","verifier_path":"fixture-only"}
    path = ledger.record_episode(result)
    record = json.loads((path / "episode.json").read_text())
    assert record["router_evidence_status"] == "ROUTER_FALLBACK"
    assert record["official_result_eligible"] is False
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["router_fallback_count"] == 1
    assert summary["pass_at_1"] is None


def test_declared_verifier_flag_without_artifacts_is_not_evidence(tmp_path):
    ledger = ExperimentLedger(tmp_path / "runs", tmp_path / "ledgers")
    result = episode(False)
    result.evaluator_details = {"official_evaluator_executed":True,"job_id":"fixture-job","trial_id":"fixture-trial","verifier_path":"fixture-only"}
    path = ledger.record_episode(result)
    record = json.loads((path / "episode.json").read_text())
    assert record["evaluation_status"] == "NOT_EVALUATED"
    assert record["official_result_eligible"] is False


def official_iteration(tmp_path, *, agent="modelrouter", terminal=True, verifier=True):
    """Harbor-shaped files live only in pytest's temporary directory."""
    root = tmp_path / "iteration"
    trial = root / "jobs" / "fixture-job" / "fix-git__fixture"
    trial.mkdir(parents=True)
    config = {
        "started_at": "2026-10-19T00:00:00+00:00",
        "ledger_root": str(tmp_path / "ledgers"), "ledger_runs_root": str(tmp_path / "runs"),
        "units": [{"job_name": "fixture-job", "policy": "laya_v2", "agent": agent, "seed": 42,
                   "task_id": "fix-git", "status": "RUNNING"}],
    }
    iterations.write_atomic(root / "run_config.json", config)
    iterations.write_atomic(root / "resume_state.json", {"status": "RUNNING", "units": config["units"]})
    iterations.write_atomic(trial / "config.json", {"job_id": "original-job-id", "trial_name": trial.name,
                                                    "environment": {"type": "docker"}})
    iterations.write_atomic(trial / "lock.json", {"task": {"version": "2.1", "digest": "sha256:fixture",
                                "git_commit_id": "upstream-fixture-commit", "source": "fixture-upstream"}})
    result = {"id": "original-trial-id", "trial_name": trial.name, "task_name": "fix-git",
              "task_id": {"path": "tasks/fix-git", "git_url": "fixture-upstream"},
              "task_checksum": "fixture", "started_at": "2026-10-19T00:00:00+00:00",
              "finished_at": "2026-10-19T00:00:02+00:00" if terminal else None,
              "agent_result": {"metadata": {"fallback_used": True, "untested_native_efforts_used": [],
                                  "policy_implementation_status": "REMOTE_NEURAL_ROUTER",
                                  "neural_router_evidence_eligible": False, "cost_statuses": ["UNVERIFIED_CONFIG"]}},
              "verifier_result": {"rewards": {"reward": 1.0}} if verifier else None,
              "verifier": {"finished_at": "2026-10-19T00:00:02+00:00"} if verifier else None}
    iterations.write_atomic(trial / "result.json", result)
    if verifier:
        iterations.write_atomic(trial / "verifier" / "reward.json", {"reward": 1.0})
    return root, trial


def test_collect_terminal_trial_indexes_same_official_source_once(tmp_path):
    root, trial_dir = official_iteration(tmp_path)
    first = iterations.collect_trials(root)
    second = iterations.collect_trials(root)
    assert first == second
    records = iterations.rows(tmp_path / "ledgers" / "experiments_ledger.jsonl")
    assert len(records) == 1
    record = records[0]
    assert record["job_id"] == "original-job-id"
    assert record["trial_id"] == "original-trial-id"
    assert record["evaluation_status"] == "EVALUATED"
    assert record["official_result_eligible"] is True
    assert record["scientific_result_eligible"] is False
    assert record["reward"] == first[0]["reward"] == 1.0
    assert record["task_id"] == first[0]["task_id"]
    assert record["task_version"] == "2.1"
    assert record["task_git_sha"] == "upstream-fixture-commit"
    assert record["verifier_path"] == str(trial_dir / "verifier" / "reward.json")
    assert record["official_source"] == str(trial_dir / "result.json")
    assert record["run_dir"] == str(trial_dir)
    assert record["events_path"] == str(root / "events.jsonl")
    assert record["total_cost_usd"] is None
    assert record["generator_cost_usd"] is None
    assert record["actual_billed_cost_usd"] is None
    assert record["total_prompt_tokens"] is None
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["official_count"] == 1
    assert summary["pass_at_1"] == 1.0
    assert summary["total_cost_usd"] is None
    assert summary["mean_cost_usd"] is None
    assert summary["policy_breakdown"]["laya_v2"]["cost_usd"] is None
    assert not list((tmp_path / "runs").iterdir())  # No copied official episode/source.
    with (tmp_path / "ledgers" / "experiments_ledger.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == 1


def test_running_trial_visible_but_not_ledgered_until_terminal(tmp_path):
    root, trial_dir = official_iteration(tmp_path, terminal=False, verifier=False)
    live = iterations.collect_trials(root)
    assert live[0]["status"] == "NOT_EVALUATED"
    assert not (tmp_path / "ledgers").exists()
    result = json.loads((trial_dir / "result.json").read_text())
    result["finished_at"] = "2026-10-19T00:00:02+00:00"
    result["exception_info"] = {"exception_type": "RuntimeError", "exception_message": "fixture sandbox unavailable"}
    iterations.write_atomic(trial_dir / "result.json", result)
    iterations.collect_trials(root)
    iterations.collect_trials(root)
    record, = iterations.rows(tmp_path / "ledgers" / "experiments_ledger.jsonl")
    assert record["evaluation_status"] == "NOT_EVALUATED"
    assert record["official_result_eligible"] is False
    assert record["reward"] is None
    assert record["error"]["exception_message"] == "fixture sandbox unavailable"


def test_official_index_and_legacy_record_share_csv_and_summary(tmp_path):
    root, _ = official_iteration(tmp_path)
    ledger = ExperimentLedger(tmp_path / "runs", tmp_path / "ledgers")
    ledger.record_episode(episode(False))
    iterations.collect_trials(root)
    ledger.record_episode(episode(False))
    with (tmp_path / "ledgers" / "experiments_ledger.csv").open() as stream:
        records = list(csv.DictReader(stream))
    assert len(records) == 3
    assert records[1]["trial_id"] == "original-trial-id"
    assert records[1]["total_cost_usd"] == ""
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["total_episodes"] == 3
    assert summary["official_count"] == 1
    assert summary["total_cost_usd"] is None


@pytest.mark.parametrize("status", ["NOT_EVALUATED", "VERIFIER_MISMATCH", "TASK_IDENTITY_MISMATCH"])
def test_nonofficial_terminal_status_not_counted(tmp_path, status):
    ledger = ExperimentLedger(tmp_path / "runs", tmp_path / "ledgers")
    ledger.record_official_trial({"trial_id": "fixture-id", "finished_at": "fixture-finished",
                                  "status": status, "reward": 1.0, "success": True,
                                  "trial_dir": str(tmp_path / "original")}, events_path=tmp_path / "events.jsonl")
    record, = iterations.rows(tmp_path / "ledgers" / "experiments_ledger.jsonl")
    assert record["reward"] == 1.0
    assert record["official_success"] is None
    assert record["official_result_eligible"] is False
    assert record["evaluation_status"] == "NOT_EVALUATED"
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["official_count"] == 0
    assert summary["pass_at_1"] is None


def test_benchmark_display_excludes_probes_and_previous_trial_tools(tmp_path):
    root, _ = official_iteration(tmp_path, terminal=False, verifier=False)
    for event in (
        {"event": "GENERATOR_END", "sample_kind": "PROVIDER_PROBE", "prompt_tokens": 900,
         "completion_tokens": 90, "cost_usd": 9.0, "returned_model": "probe-model"},
        {"event": "ROUTER_END", "sample_kind": "ROUTER_PROBE", "router_family": "laya", "router_latency_ms": 999},
        {"event": "GENERATOR_END", "episode_id": "original-trial-id", "step": 2,
         "prompt_tokens": 10, "completion_tokens": 2, "cost_usd": .1, "model": "benchmark-model", "effort": "low"},
        {"event": "ROUTER_END", "episode_id": "original-trial-id", "router_family": "laya", "router_latency_ms": 8},
    ):
        iterations.append(root / "events.jsonl", event)
    iterations.append(root / "tool_calls.jsonl", {"kind": "agent_tool", "episode_id": "original-trial-id",
                                                 "step": 2, "command": "echo real-fixture", "exit_code": 0, "duration_ms": 3})
    iterations.append(root / "tool_calls.jsonl", {"kind": "agent_tool", "episode_id": "previous-trial-id",
                                                 "command": "stale command", "exit_code": 1, "duration_ms": 4})
    metrics = iterations.summarize(root)
    assert metrics["generator_tokens"] == 12
    assert metrics["generator_cost_usd"] == .1
    assert metrics["router_latency_ms"]["laya"]["p50"] == 8
    assert metrics["last_generator"]["model"] == "benchmark-model"
    assert metrics["last_tool"]["command"] == "echo real-fixture"
    assert metrics["measurement_counts"]["PROVIDER_PROBE"] == 1
    line = iterations.display(metrics)
    assert "Job=original-job-id" in line
    assert "Trial=original-trial-id" in line
    assert "LastTool=echo real-fixture" in line
    assert "Reward=N/A" in line
    assert "probe-model" not in line


@pytest.mark.parametrize("agent", ["oracle", "mini-swe-agent"])
def test_absent_benchmark_measurements_stay_null(tmp_path, agent):
    root, _ = official_iteration(tmp_path, agent=agent, terminal=False, verifier=False)
    metrics = iterations.summarize(root)
    assert metrics["generator_tokens"] is None
    assert metrics["generator_cost_usd"] is None
    assert metrics["known_generator_cost_usd"] is None
    assert metrics["last_generator"] is None
    assert metrics["last_tool"] is None
    assert metrics["models"] == {}
    assert "Tokens=N/A" in iterations.display(metrics)


@pytest.mark.parametrize("billed", [None, .25])
def test_reported_native_usage_keeps_estimate_separate_from_full_cost(tmp_path, billed):
    root, trial_dir = official_iteration(tmp_path, agent="mini-swe-agent")
    result = json.loads((trial_dir / "result.json").read_text())
    result["agent_result"].update(n_input_tokens=10, n_output_tokens=2, cost_usd=.2)
    result["agent_result"]["metadata"].update(actual_billed_cost_usd=billed,
                                              sandbox_cost_usd=.5, router_compute_cost_usd=.125)
    iterations.write_atomic(trial_dir / "result.json", result)
    metrics = iterations.summarize(root)
    record, = iterations.rows(tmp_path / "ledgers" / "experiments_ledger.jsonl")
    assert metrics["generator_tokens"] == 12
    assert metrics["generator_cost_usd"] == record["generator_cost_usd"] == .2
    assert record["cost_statuses"] == ["UNVERIFIED_CONFIG"]
    assert record["actual_billed_cost_usd"] == billed
    assert metrics["actual_generator_cost_usd"] == billed
    expected = None if billed is None else .875
    assert record["total_cost_usd"] == metrics["complete_cost_usd"] == expected
    summary = json.loads((tmp_path / "ledgers" / "summary.json").read_text())
    assert summary["total_cost_usd"] == expected
