"""Narrow tests for preserved targets, causal prefixes and evidence-based references."""

import gzip
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from modelrouter.agent.state import AgentState
from modelrouter.serving.schemas import PreDecisionState
from modelrouter.v9.capabilities.normalize import normalize_catalog
from modelrouter.v9.teacher.assessor import TrajectoryAssessor
from modelrouter.v9.training.prepare import (
    build_offline_prefix_input, generate_offline_teacher_material,
    main, prepare, prepare_record, reencode_prepared, reference_candidate, tool_result, trajectory, trajectory_prefixes,
)


def typed(source, group, target, label, stable, episode=None):
    criteria = {"model-z": "", "model-a": ""} if group == "S1" else {"false": "Unresolved", "true": "Resolved"}
    qid = "model_choice" if group == "S1" else "trajectory_resolved"
    kind = "choice" if group == "S1" else "noul"
    if group == "S3":
        qid = {"output_token_length": "observed_output_token_tier",
               "request_response_tokens": "observed_response_token_tier",
               "call_output_tokens": "observed_response_token_tier",
               "call_quota_units": "observed_quota_tier"}.get(target, target)
        kind, criteria = "score", ["short", "medium", "long", "extended"]
    return {"provenance": {"source_id": source, "stable_record_id": stable,
            "independent_unit_id": stable, "trajectory_id": episode, "split": "train"},
            "state": {"pre_decision_state": {"prompt_snippet": "Original task"}},
            "questions": {qid: {"type": kind, "criteria": criteria}},
            "expected": {qid: label}, "_meta": {"supervision_class": group, "target": target}}


def episode_row(eid, failed=False, resolved=True, generations=4):
    messages = [{"role": "user", "content": "<pr_description>Repair parser</pr_description>"}]
    for index in range(generations):
        messages.extend([
            {"role": "assistant", "content": f"Run tool {index}", "tool_calls": [
                {"function": {"name": "bash", "arguments": json.dumps({"command": f"python test_{index}.py"})}}]},
            {"role": "tool", "content": json.dumps({"returncode": 1 if failed and index == 0 else 0,
                "output": "ACTUAL_FIRST_FAILURE" if failed and index == 0 else f"OBSERVED_RESULT_{index}"})},
        ])
    return {"instance_id": f"task-{eid}", "trajectory_id": eid, "messages": messages, "resolved": resolved}


def saved_teacher(step=3):
    references = [{"source_id": source, "task_id": f"ref-task-{i}", "episode_id": f"ref-episode-{i}",
                   "split": "train", "success_evidence": {"field": "resolved", "value": True}}
                  for i, source in enumerate(("TRA-001", "TRA-002"))]
    return {"dataset_revision": "offline-teacher-v1", "assessment": {
                "progress_summary": "Observed three completed tool calls", "main_blocker": "Parser failure",
                "next_milestone": "Run the parser test"},
            "metrics": {"status": "SUCCESS", "teacher_model_id": "gpt-6.1-sol", "native_effort": "max",
                        "assessed_through_step": step, "reference_ids": references,
                        "prompt_tokens": 1200, "completion_tokens": 100, "cost_usd": .002}}


class PrepareTests(unittest.TestCase):
    def test_original_choices_targets_missing_values_and_serializer(self):
        row = typed("ROUTE-004", "S1", "human_pairwise_preference", "model-a", "battle-1")
        with patch.object(PreDecisionState, "router_text", autospec=True, return_value="SERIALIZED_STATE") as serialize:
            prepared, reason = prepare_record(row, "train")
        self.assertIsNone(reason)
        self.assertEqual(serialize.call_count, 1)
        self.assertEqual(prepared["state"], "SERIALIZED_STATE")
        self.assertEqual(list(prepared["questions"]["model_choice"]["criteria"]), ["model-z", "model-a"])
        self.assertEqual(prepared["expected"], row["expected"])
        self.assertEqual(prepared["questions"]["model_choice"]["label"], "model-a")
        self.assertIsNone(prepared["pre_decision_state"]["budget_remaining_usd"])
        self.assertIsNone(prepared["teacher_assessment"])
        self.assertIsNone(prepared["capability_snapshot_id"])
        self.assertEqual(prepared["capability_cards"], [])
        self.assertIsNone(prepared["pre_decision_state"]["task_id"])
        self.assertEqual(prepared["_meta"]["teacher_data_status"], "NOT_GENERATED")
        self.assertNotIn("label", row["questions"]["model_choice"])

    def test_source_measurements_survive_the_shared_serializer(self):
        row = typed("CACHE-001", "S3", "output_token_length", 1, "cache-1")
        row["state"]["pre_decision_state"] = {
            "arrival_timestamp": 3000, "input_length": 2012, "prefix_block_count": 4,
            "trace_type": "conversation", "prompt_snippet": None, "task_domain": "coding",
        }
        prepared, reason = prepare_record(row, "train")
        self.assertIsNone(reason)
        state = json.loads(prepared["state"])
        self.assertIsNone(state["prompt"])
        self.assertEqual(state["context_tokens_approx"], 2012)
        self.assertEqual(state["task_domain"], "coding")
        features = json.loads(state["history_snippet"])["source_pre_decision_features"]
        self.assertEqual(features, {"arrival_timestamp": 3000, "input_length": 2012,
                                    "prefix_block_count": 4, "trace_type": "conversation"})
        self.assertEqual(features["arrival_timestamp"], 3000)
        self.assertEqual(features["prefix_block_count"], 4)
        self.assertTrue(prepared["_meta"]["auxiliary_not_model_choice"])
        own = typed("OWN-002", "S3", "call_output_tokens", 2, "own-1")
        own["state"]["pre_decision_state"] = {
            "model_normalized": "existing-model-id", "reasoning_effort": "max",
            "prompt_tokens": "199", "is_stream": None,
        }
        prepared, reason = prepare_record(own, "train")
        self.assertIsNone(reason)
        state = json.loads(prepared["state"])
        self.assertEqual(state["context_tokens_approx"], 199)
        features = json.loads(state["history_snippet"])["source_pre_decision_features"]
        self.assertEqual(features["model_normalized"], "existing-model-id")
        self.assertIsNone(features["is_stream"])

    def test_unknown_outcome_is_not_failure_and_auxiliary_stays_separate(self):
        row = typed("TRA-001", "S2", "observed_failure", None, "sample")
        self.assertEqual(prepare_record(row, "train")[1], "MISSING_TARGET")
        row["expected"]["trajectory_resolved"] = False
        prepared, reason = prepare_record(row, "train")
        self.assertIsNone(reason)
        self.assertIs(prepared["expected"]["trajectory_resolved"], False)
        self.assertTrue(prepared["_meta"]["auxiliary_not_model_choice"])
        row = typed("ROUTE-004", "S1", "human_pairwise_preference", "model-a", "conflict")
        row["questions"]["model_choice"]["label"] = "model-z"
        self.assertEqual(prepare_record(row, "train")[1], "TARGET_CONFLICT")

    def test_offline_teacher_and_capabilities_enter_the_same_serialized_input(self):
        row = typed("ROUTE-004", "S1", "human_pairwise_preference", "gpt-6.1-sol:max", "battle-v9")
        row["questions"]["model_choice"]["criteria"] = {"gpt-6.1-sol:max": "", "gpt-6-luna:high": ""}
        row["state"]["pre_decision_state"]["step_index"] = 4
        row["provenance"]["observed_through_step"] = 3
        row["offline_teacher_state"] = saved_teacher()
        row["legal_actions"] = [{"model": "gpt-6-luna", "native_effort": "high"},
                                {"model_id": "gpt-6.1-sol", "native_effort": "max"}]
        snapshot = {"snapshot_id": "capability-v1", "models": normalize_catalog({"data": [{
            "slug": "gpt-6-luna", "native_effort": "high", "evaluations": {
                "artificial_analysis_intelligence_index": {"score": 47.2, "version": 4}}}]}, "https://artificialanalysis.ai", "now")}
        prepared, reason = prepare_record(row, "train", capability_snapshot=snapshot)
        self.assertIsNone(reason)
        state = json.loads(prepared["state"])
        self.assertEqual(state["teacher_assessment"]["progress_summary"], row["offline_teacher_state"]["assessment"]["progress_summary"])
        self.assertEqual(set(state["teacher_assessment"]), {"progress_summary", "main_blocker", "next_milestone"})
        assessment = prepared["pre_decision_state"]["teacher_assessment"]
        self.assertEqual(assessment["teacher_model_id"], "gpt-6.1-sol")
        self.assertEqual(assessment["assessed_through_step"], 3)
        self.assertEqual(prepared["offline_teacher_state"]["metrics"]["prompt_tokens"], 1200)
        self.assertEqual(prepared["_meta"]["teacher_data_status"], "GENERATED")
        self.assertEqual([card["action_id"] for card in state["capability_cards"]],
                         ["gpt-6.1-sol:max", "gpt-6-luna:high"])
        self.assertEqual(state["capability_snapshot_id"], "capability-v1")
        metric = dict(zip(state["metric_fields"], state["capability_cards"][1]["action_metrics"][0]))
        self.assertEqual(metric["score_raw"], 47.2)
        self.assertEqual(metric["benchmark_version"], 4)
        self.assertEqual(prepared["expected"], row["expected"])
        self.assertNotIn("label", row["questions"]["model_choice"])

    def test_future_or_failed_teacher_does_not_replace_an_observed_target(self):
        row = typed("TRA-001", "S2", "observed_success", True, "anchor", "ep")
        row["state"]["pre_decision_state"]["step_index"] = 4
        row["provenance"]["observed_through_step"] = 3
        row["offline_teacher_state"] = saved_teacher(4)
        prepared, reason = prepare_record(row, "train")
        self.assertIsNone(reason)
        self.assertEqual(prepared["offline_teacher_state"]["status"], "FUTURE_ASSESSMENT")
        self.assertIsNone(prepared["teacher_assessment"])
        self.assertNotIn("Observed three completed tool calls", prepared["state"])
        self.assertEqual(prepared["expected"], row["expected"])
        row["offline_teacher_state"] = saved_teacher()
        row["offline_teacher_state"]["metrics"]["status"] = "FAILED"
        prepared, reason = prepare_record(row, "train")
        self.assertEqual(prepared["offline_teacher_state"]["status"], "FAILED")
        self.assertIsNone(prepared["teacher_assessment"])
        self.assertIs(prepared["expected"]["trajectory_resolved"], True)
        row["offline_teacher_state"] = saved_teacher()
        row["offline_teacher_state"]["metrics"]["reference_ids"][0]["split"] = "sealed_final"
        prepared, reason = prepare_record(row, "train")
        self.assertEqual(prepared["offline_teacher_state"]["status"], "REFERENCE_SCOPE_MISMATCH")

    def test_supplied_new_candidates_only_augment_auxiliary_targets(self):
        candidates = ["gpt-6.1-sol:none", "gpt-6-luna:none", "qwen3.8-flash:none"]
        snapshot = {"snapshot_id": "unmeasured", "models": normalize_catalog({"data": []}, "official", "now")}
        preference = typed("ROUTE-004", "S1", "human_pairwise_preference", "model-a", "historical")
        prepared, reason = prepare_record(preference, "train", capability_snapshot=snapshot, candidates=candidates)
        self.assertEqual([card["model_id"] for card in prepared["capability_cards"]], ["model-z", "model-a"])
        self.assertEqual(prepared["expected"], preference["expected"])
        auxiliary = typed("TIME-001", "S3", "request_response_tokens", 2, "time")
        auxiliary["pre_decision_state"] = {"prompt": None, "step_index": None}
        prepared, reason = prepare_record(auxiliary, "train", capability_snapshot=snapshot, candidates=candidates)
        self.assertIsNone(reason)
        self.assertIsNone(prepared["pre_decision_state"]["prompt"])
        self.assertEqual([card["action_id"] for card in prepared["capability_cards"]], candidates)
        self.assertTrue(prepared["_meta"]["auxiliary_not_model_choice"])
        self.assertEqual(prepared["expected"], auxiliary["expected"])

    def test_saved_candidate_reference_reuses_existing_target_constructor(self):
        reference = {"source_id": "ROUTE-004", "primary_supervision_class": "S1", "split": "train",
                     "train_eligible": True, "candidate_targets": ["human_pairwise_preference"],
                     "target": "human_pairwise_preference", "source_line": 25, "source_file": "existing.jsonl",
                     "stable_record_id": "battle", "independent_unit_id": "unit", "assigned_layer": "L1",
                     "quality_grade": "Q1", "label_evidence": {"human_pairwise_preference": ["observed_decision.winner_model"]}}
        row = {"candidate_reference": reference, "source_record": {
            "pre_decision_state": {"candidate_model_a": "model-z", "candidate_model_b": "model-a", "prompt_snippet": "Existing prompt"},
            "observed_decision": {"winner_model": "model-a"}}}
        prepared, reason = prepare_record(row, "train")
        self.assertIsNone(reason)
        self.assertEqual(prepared["expected"], {"model_choice": "model-a"})
        self.assertEqual(prepared["provenance"]["assigned_layer"], "L1")
        self.assertEqual(prepared["provenance"]["source_line"], 25)
        reference["train_eligible"] = False
        self.assertEqual(prepare_record(row, "train")[1], "SOURCE_NOT_TRAIN_ELIGIBLE")

    def test_prefix_never_contains_current_action_or_future_observation(self):
        original = episode_row("ep-recovery", failed=True)
        anchor = {"stable_record_id": "anchor", "independent_unit_id": "unit", "dataset_revision": None}
        episode = trajectory(original, "TRA-001", "public.parquet", 3, anchor)
        samples = list(trajectory_prefixes(episode))
        self.assertEqual(len(samples), 2)
        first, later = samples
        self.assertNotIn("ACTUAL_FIRST_FAILURE", json.dumps(first["state"]))
        self.assertIn("ACTUAL_FIRST_FAILURE", json.dumps(later["state"]))
        self.assertNotIn("OBSERVED_RESULT_3", json.dumps(later["state"]))
        self.assertNotIn("test_3.py", json.dumps(later["state"]))
        self.assertEqual(later["provenance"]["observed_through_step"], 3)
        prepared, reason = prepare_record(later, "train")
        self.assertIsNone(reason)
        self.assertIn("ACTUAL_FIRST_FAILURE", prepared["state"])
        self.assertNotIn("test_3.py", prepared["state"])
        self.assertEqual(prepared["expected"], later["expected"])

    def test_offline_input_replays_complete_recorded_prefix_without_source_usage(self):
        original = episode_row("full-prefix", failed=True, generations=8)
        episode = trajectory(original, "TRA-001", "public.parquet", 3,
                             {"stable_record_id": "anchor", "independent_unit_id": "unit"})
        samples = list(trajectory_prefixes(episode))
        self.assertEqual([row["provenance"]["observed_through_step"] for row in samples], [0, 3, 7])
        self.assertEqual(samples[2]["observed_messages"], original["messages"][:15])
        self.assertEqual(len(json.loads(samples[2]["state"]["pre_decision_state"]["history_snippet"])), 8)
        factory = lambda info: AgentState(info["task_id"], info["episode_id"], "OFFLINE_TEST", max_steps=20)
        state, messages = build_offline_prefix_input(samples[2], factory)
        self.assertEqual(state.step_index, 7)
        self.assertEqual(len(state.history), 7)
        self.assertEqual(state.tool_error_count, 1)
        self.assertIsNone(state.current_phase)
        self.assertTrue(all(step.step_cost_usd is None and step.prompt_tokens is None
                            and step.step_duration_sec is None for step in state.history))
        self.assertNotIn("test_7.py", json.dumps(messages))
        missing = dict(samples[2], observed_messages=messages[:-2])
        with self.assertRaises(ValueError):
            build_offline_prefix_input(missing, factory)
        original["messages"][0]["content"] = "Original task " + "x" * 6000
        episode = trajectory(original, "TRA-001", "public.parquet", 3, episode["anchor"])
        later = list(trajectory_prefixes(episode))[-1]
        prepared, reason = prepare_record(later, "train")
        self.assertIsNone(reason)
        encoded = json.loads(prepared["state"])
        self.assertEqual(len(encoded["prompt"]), 2000)
        self.assertEqual(prepared["pre_decision_state"]["prompt"], original["messages"][0]["content"])
        self.assertEqual(prepared["observed_messages"], original["messages"][:15])
        self.assertEqual(encoded["agent_context"]["observed_through_step"], 7)

    def test_offline_generation_uses_existing_teacher_trigger_and_reuses_success(self):
        class AliasProvider:
            alias_mapping = {"gpt-6.1-sol": "Qwen3.8-27B"}

            def __init__(self):
                self.calls = []
                self.fail_on_call = None

            def query_raw(self, messages, spec, effort, tokens, **kwargs):
                self.calls.append((messages, kwargs))
                if len(self.calls) == self.fail_on_call:
                    raise TimeoutError("Test request timeout")
                content = {"progress_summary": "Three observed tools", "main_blocker": "Parser error",
                           "next_milestone": "Run the parser test"}
                return {"choices": [{"message": {"content": json.dumps(content)}}]}, {
                    "returned_model_id": "Qwen3.8-27B", "execution_mode": "ALIAS_SMOKE",
                    "prompt_tokens": 1200, "completion_tokens": 100,
                    "reasoning_tokens": None, "cached_tokens": None, "cost_usd": .002,
                    "usage_status": "PROMPT_COMPLETION_REPORTED"}

        with tempfile.TemporaryDirectory(prefix="mr-v9-offline-") as temporary:
            root = Path(temporary)
            references = saved_teacher()["metrics"]["reference_ids"]
            for ref in references:
                ref.update(dataset_revision="test-reference", summary="Recorded successful example",
                           observed_through_step=4)
            refs_path = root / "references.json"
            refs_path.write_text(json.dumps(references))
            original = episode_row("offline", generations=8)
            episode = trajectory(original, "TRA-001", "public.parquet", 3,
                                 {"stable_record_id": "anchor", "independent_unit_id": "unit"})
            candidates = ["gpt-6.1-sol:none", "gpt-6-luna:none", "qwen3.8-flash:none"]
            rows = [prepare_record(row, "train", candidates=candidates)[0] for row in trajectory_prefixes(episode)]
            physical = root / "agent_auxiliary/train.jsonl"
            physical.parent.mkdir()
            physical.write_text("\n".join(map(json.dumps, rows)))
            path = root / "trajectory_prefixes/train.jsonl"
            path.parent.mkdir()
            path.symlink_to(Path("..") / "agent_auxiliary/train.jsonl")
            summary_path = root / "summary.json"
            summary_path.write_text(json.dumps({"counts": {"agent_auxiliary/train.jsonl": 3},
                                                "teacher_generation_requests": 0}))
            states = []

            def factory(info):
                self.assertNotIn("expected", info)
                state = AgentState(info["task_id"], info["episode_id"], "OFFLINE_TEST", max_steps=20)
                states.append(state)
                return state

            provider = AliasProvider()
            assessor = TrajectoryAssessor(provider, refs_path)
            report = generate_offline_teacher_material(assessor=assessor, state_factory=factory, prefixes_path=path)
            self.assertTrue(path.is_symlink())
            self.assertEqual(path.resolve(), physical.resolve())
            self.assertEqual(len(provider.calls), 1)
            self.assertEqual(report["teacher_generation_requests"], 1)
            self.assertEqual(report["usable_assessments"], 2)
            self.assertEqual(report["status_counts"], {"NOT_TRIGGERED": 1, "SUCCESS": 1, "REUSED": 1})
            self.assertEqual(report["request_usage_totals"]["cost_usd"], .002)
            self.assertIsNone(report["request_usage_totals"]["reasoning_tokens"])
            self.assertEqual(provider.calls[0][1], {"tools": None, "stream": False})
            self.assertNotIn("test_3.py", provider.calls[0][0][1]["content"])
            output = [json.loads(line) for line in path.read_text().splitlines()]
            for before, after in zip(rows, output):
                self.assertEqual(after["expected"], before["expected"])
                self.assertEqual(after["candidate_actions"], before["candidate_actions"])
                self.assertEqual(after["observed_messages"], before["observed_messages"])
            teacher = output[1]["offline_teacher_state"]
            self.assertEqual(teacher["assessment"]["teacher_model_id"], "Qwen3.8-27B")
            self.assertEqual(teacher["assessment"]["execution_mode"], "OFFLINE_TEACHER_ALIAS_SMOKE")
            self.assertEqual(output[2]["teacher_assessment"]["assessed_through_step"], 3)
            self.assertTrue(all(state.accumulated_cost_usd == 0 for state in states))
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary["teacher_data_status"], "PARTIAL")
            self.assertEqual(summary["teacher_status_counts"], {"NOT_GENERATED": 1, "GENERATED": 2})
            repeat = generate_offline_teacher_material(assessor=assessor, state_factory=factory, prefixes_path=path)
            self.assertEqual(len(provider.calls), 1)
            self.assertEqual(repeat["teacher_generation_requests"], 0)
            self.assertEqual(repeat["usable_assessments"], 2)
            self.assertEqual(json.loads(summary_path.read_text())["teacher_generation_requests"], 1)
            original["messages"][11]["tool_calls"][0]["function"]["arguments"] = json.dumps({"command": "pytest parser_test.py"})
            episode = trajectory(original, "TRA-001", "public.parquet", 3, episode["anchor"])
            path.write_text("\n".join(json.dumps(prepare_record(row, "train")[0])
                                      for row in trajectory_prefixes(episode)))
            triggered = generate_offline_teacher_material(assessor=assessor, state_factory=factory, prefixes_path=path)
            self.assertEqual(triggered["teacher_generation_requests"], 2)
            self.assertEqual(triggered["metrics"][-1]["trigger_reason"], "NEW_VERIFICATION_RESULT")
            path.write_text("\n".join(json.dumps(prepare_record(row, "train")[0])
                                      for row in trajectory_prefixes(episode)))
            provider.fail_on_call = len(provider.calls) + 2
            partial = generate_offline_teacher_material(assessor=assessor, state_factory=factory, prefixes_path=path)
            self.assertEqual(partial["teacher_generation_requests"], 2)
            self.assertIsNone(partial["request_usage_totals"]["prompt_tokens"])
            self.assertIsNone(partial["request_usage_totals"]["completion_tokens"])
            self.assertIsNone(partial["request_usage_totals"]["cost_usd"])
            self.assertEqual(partial["known_usage_totals"]["prompt_tokens"], 1200)
            self.assertEqual(partial["known_usage_totals"]["completion_tokens"], 100)
            self.assertEqual(partial["known_usage_totals"]["cost_usd"], .002)
            self.assertEqual(partial["missing_usage_request_count"], 1)

    def test_reencoding_merges_legacy_prefixes_into_one_physical_s2_view(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-merge-") as temporary:
            root = Path(temporary)
            anchor = typed("TRA-001", "S2", "observed_success", True, "anchor", "merge")
            base = prepare_record(anchor, "train")[0]
            physical = root / "agent_auxiliary/train.jsonl"
            physical.parent.mkdir()
            physical.write_text(json.dumps(base))
            episode = trajectory(episode_row("merge"), "TRA-001", "public.parquet", 3,
                                 {"stable_record_id": "anchor", "independent_unit_id": "unit"})
            rows = [prepare_record(row, "train")[0] for row in trajectory_prefixes(episode)]
            prefix_path = root / "trajectory_prefixes/train.jsonl"
            prefix_path.parent.mkdir()
            prefix_path.write_text("\n".join(map(json.dumps, rows)))
            (root / "train").mkdir()
            (root / "train/S2.jsonl").symlink_to(Path("..") / "agent_auxiliary/train.jsonl")
            summary = {"counts": {"agent_auxiliary/train.jsonl": 1, "trajectory_prefixes/train.jsonl": 2},
                       "eligible_counts": {"agent_auxiliary/train.jsonl": 1, "trajectory_prefixes/train.jsonl": 2},
                       "trainer_views": {"train": {"S2": str(root / "train/S2.jsonl")}}}
            (root / "summary.json").write_text(json.dumps(summary))
            updated = reencode_prepared(root)
            self.assertEqual(updated["counts"], {"agent_auxiliary/train.jsonl": 3})
            self.assertEqual(updated["trajectory_prefix_count"], 2)
            self.assertEqual(updated["eligible_counts"], {"agent_auxiliary/train.jsonl": 3})
            self.assertEqual(updated["trainer_root"], ".")
            self.assertEqual(updated["trainer_views"]["train"]["S2"], "train/S2.jsonl")
            self.assertTrue(prefix_path.is_symlink())
            self.assertEqual(prefix_path.resolve(), physical.resolve())
            actual = [row for row in map(json.loads, physical.read_text().splitlines())]
            for before, after in zip([base, *rows], actual):
                self.assertEqual(after["pre_decision_state"], before["pre_decision_state"])
                self.assertEqual(after["provenance"], before["provenance"])
                self.assertEqual(after["expected"], before["expected"])
            self.assertEqual(reencode_prepared(root)["counts"], updated["counts"])

    def test_unknown_tool_status_is_not_an_efficient_success(self):
        row = episode_row("unknown")
        for message in row["messages"]:
            if message["role"] == "tool":
                message["content"] = '{code listing: returncode = 1; contains "error"}'
        episode = trajectory(row, "TRA-001", "public.parquet", 1, {"stable_record_id": "anchor"})
        self.assertIsNone(reference_candidate(episode))
        self.assertIsNone(tool_result(row["messages"][2])[0])

    def test_cli_materialization_deduplicates_and_writes_exactly_two_references(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            (root / "input/train").mkdir(parents=True)
            preference = typed("ROUTE-004", "S1", "human_pairwise_preference", "model-a", "battle-1")
            anchors = [typed("TRA-001", "S2", "observed_success", True, f"anchor-{eid}", eid)
                       for eid in ["ep-efficient", "ep-recovery"]]
            (root / "input/train/S1.jsonl").write_text("\n".join(json.dumps(preference) for _ in range(2)))
            (root / "input/train/S2.jsonl").write_text("\n".join(map(json.dumps, anchors)))
            raw_path = root / "raw.jsonl"
            raw_path.write_text("\n".join(map(json.dumps, [episode_row("ep-efficient"), episode_row("ep-recovery", True),
                                                        episode_row("no-train-anchor", True)])))
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                result = main(["--typed-root", str(root / "input"), "--trajectory", f"TRA-001={raw_path}",
                               "--out-dir", str(root / "out"), "--references-path", str(root / "references.json"),
                               "--split", "train"])
            self.assertEqual(result, 0)
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["counts"]["model_comparison/train.jsonl"], 1)
            self.assertEqual(summary["skipped"]["DUPLICATE"], 1)
            self.assertFalse((root / "out/system_auxiliary").exists())
            references = json.loads((root / "references.json").read_text())
            self.assertEqual(len(references), 2)
            self.assertEqual([ref["reference_kind"] for ref in references], ["efficient_success", "failure_recovery"])
            self.assertEqual({ref["episode_id"] for ref in references}, {"ep-efficient", "ep-recovery"})
            self.assertTrue(all(ref["success_evidence"]["value"] is True for ref in references))
            self.assertTrue(all(ref["dataset_revision"] is None for ref in references))
            self.assertGreater(len(references[1]["tool_failure_evidence"]), 0)
            self.assertEqual([ref["success_evidence"]["train_anchor"] for ref in references],
                             ["anchor-ep-efficient", "anchor-ep-recovery"])
            self.assertEqual(references[0]["selection_metric"]["unknown_tool_results"], 0)
            self.assertIn("test_0.py", references[0]["summary"])
            self.assertEqual(summary["teacher_data_status"], "NOT_GENERATED")
            trainer_path = root / "out" / summary["trainer_views"]["train"]["S1"]
            self.assertTrue(trainer_path.is_symlink())
            self.assertEqual(trainer_path.resolve(), (root / "out/model_comparison/train.jsonl").resolve())

    def test_source_target_sampling_preserves_more_than_the_first_source(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            records = [typed("CACHE-001", "S3", "output_token_length", 1, f"cache-{i}") for i in range(5)]
            records.append(typed("TIME-001", "S3", "request_response_tokens", 2, "time-1"))
            source = root / "typed.jsonl"
            source.write_text("\n".join(map(json.dumps, records)))
            summary = prepare(inputs=[source], out_dir=root / "out", references_path=root / "references.json",
                              splits=("train",), limit_per_view=2)
            rows = [json.loads(line) for line in (root / "out/system_auxiliary/train.jsonl").read_text().splitlines()]
            self.assertEqual([row["provenance"]["source_id"] for row in rows], ["CACHE-001", "TIME-001"])
            self.assertEqual(summary["limited_counts"]["system_auxiliary/train.jsonl"], 4)

    def test_v8_unknown_outcomes_are_counted_without_labels(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            with gzip.open(root / "observed_agent_outcome_train.jsonl.gz", "wt") as stream:
                stream.write(json.dumps({"provenance": {"source_id": "TRA-001"},
                                         "known_terminal_outcome": "UNKNOWN"}) + "\n")
            summary = prepare(v8_views=root, out_dir=root / "out", references_path=root / "references.json",
                              splits=("train",))
            self.assertEqual(summary["skipped"]["UNKNOWN_OUTCOME"], 1)
            self.assertFalse(summary["counts"])
            self.assertFalse((root / "out/agent_auxiliary").exists())

    def test_bounded_public_export_keeps_original_origin(self):
        row = episode_row("origin")
        row.update(source_path="/public/original.parquet", source_row=233)
        episode = trajectory(row, "TRA-001", "subset.jsonl", 1, {"stable_record_id": "typed-anchor"})
        reference = reference_candidate(episode)
        self.assertEqual(reference["success_evidence"]["source_path"], "/public/original.parquet")
        self.assertEqual(reference["success_evidence"]["source_row"], 233)

    def test_missing_recovery_does_not_fabricate_a_second_reference(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            source = root / "typed.jsonl"
            source.write_text(json.dumps(typed("TRA-001", "S2", "observed_success", True, "anchor", "ep")))
            raw = root / "raw.jsonl"
            raw.write_text(json.dumps(episode_row("ep")))
            summary = prepare(inputs=[source], trajectories=[("TRA-001", raw)], out_dir=root / "out",
                              references_path=root / "references.json", splits=("train",))
            self.assertEqual(summary["missing_reference_kinds"], ["failure_recovery"])
            self.assertFalse((root / "references.json").exists())

    def test_inline_cached_trajectory_uses_the_same_prefix_and_reference_path(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            anchor = typed("TRA-001", "S2", "observed_success", True, "cached-anchor", "cached-ep")
            raw = episode_row("cached-ep")
            raw.update(source_path="/public/original.parquet", source_row=233)
            source = root / "cached.jsonl"
            source.write_text("\n".join(map(json.dumps, [anchor, {"source_id": "TRA-001", "trajectory_record": raw}])))
            summary = prepare(inputs=[source], out_dir=root / "out", references_path=root / "references.json",
                              splits=("train",), capabilities_dir=root / "no-capabilities")
            self.assertEqual(summary["trajectory_prefix_count"], 2)
            self.assertEqual(summary["counts"]["agent_auxiliary/train.jsonl"], 3)
            self.assertNotIn("trajectory_prefixes/train.jsonl", summary["counts"])
            self.assertTrue((root / "out/trajectory_prefixes/train.jsonl").is_symlink())
            self.assertEqual(summary["teacher_generation_requests"], 0)
            self.assertEqual(summary["v9_model_effort_target_count"], 0)
            rows = [json.loads(line) for line in (root / "out/trajectory_prefixes/train.jsonl").read_text().splitlines()
                    if json.loads(line)["_meta"].get("input_kind") == "TRAJECTORY_PREFIX"]
            self.assertTrue(all(row["provenance"]["source_file"] == "/public/original.parquet" for row in rows))
            self.assertTrue(all(row["provenance"]["source_line"] == 233 for row in rows))

    def test_rerun_reuses_fixed_references_and_removes_obsolete_views(self):
        with tempfile.TemporaryDirectory(prefix="mr-v9-prepare-") as temporary:
            root = Path(temporary)
            source = root / "typed.jsonl"
            source.write_text("\n".join(json.dumps(typed("TRA-001", "S2", "observed_success", True,
                                                        f"anchor-{eid}", eid)) for eid in ("ep", "recovery")))
            raw = root / "raw.jsonl"
            raw.write_text("\n".join(map(json.dumps, [episode_row("ep"), episode_row("recovery", True)])))
            prepare(inputs=[source], trajectories=[("TRA-001", raw)], out_dir=root / "out",
                    references_path=root / "references.json", splits=("train",))
            self.assertTrue((root / "references.json").is_file())
            reference_text = (root / "references.json").read_text()
            unrelated = root / "out/user_data.txt"
            unrelated.write_text("keep")
            summary = prepare(out_dir=root / "out", references_path=root / "references.json", splits=("train",))
            self.assertFalse(summary["counts"])
            self.assertFalse((root / "out/agent_auxiliary").exists())
            self.assertFalse((root / "out/train/S2.jsonl").exists())
            self.assertFalse((root / "out/trajectory_prefixes").exists())
            self.assertEqual((root / "references.json").read_text(), reference_text)
            self.assertEqual(summary["fixed_references_reused"], 2)
            self.assertEqual(summary["references_status"], "READY")
            self.assertEqual(unrelated.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
