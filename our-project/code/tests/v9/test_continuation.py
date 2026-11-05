"""Queue-boundary tests with local JSON fixtures and simulated Trainer calls."""

import copy
import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, call, patch

from modelrouter.serving.schemas import PreDecisionState
from modelrouter.v9.training import continuation as cont
from modelrouter.training import kev_candidate_dispatcher as dispatcher
from router_data import laya_batch_train
from router_data import checkpoint_retention as retention


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf8")


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf8")


def feature_row():
    return {"pre_decision_state": {
        "prompt": "Observed task", "step_index": 3,
        "teacher_assessment": {"progress_summary": "Observed progress", "main_blocker": "Tool result",
            "next_milestone": "Next action", "teacher_model_id": "recorded-teacher",
            "assessed_through_step": 2, "reference_ids": [{"episode_id": "train-reference"}]},
        "capability_cards": [{"action_id": "b:none", "model_id": "b"},
                             {"action_id": "a:none", "model_id": "a"}],
        "capability_snapshot_id": "recorded-snapshot", "feature_training_status": "FEATURE_NOT_TRAINED"},
        "state": "UNUSED", "questions": {"model_choice": {
            "type": "choice", "instructions": "Choose", "criteria": {"b": "B", "a": "A"}, "label": "a"}},
        "expected": {"model_choice": "a"}, "provenance": {"split": "train", "source_id": "ROUTE-004"}}


def prepared(root, *, ready=True):
    data = root / "data/v9/prepared"
    write_rows(data / "train/S1.jsonl", [feature_row()])
    metadata = {"trainer_root": str(data), "trainer_views": {"train": {"S1": str(data / "train/S1.jsonl")}},
                "dataset_revision": "existing-revision", "teacher_data_status": "GENERATED" if ready else "NOT_GENERATED",
                "counts": {"model_comparison/train.jsonl": 1}, "training": {"kev": {"max_state": 8192}}}
    write_json(data / "summary.json", metadata)
    return data / "summary.json", metadata


def laya_run(root, run_id, *, complete=True):
    value = {"run_id": run_id, "status": "completed" if complete else "running",
             "seed": 17, "max_len": 1024, "head_max_len": 512, "epochs_max": 1,
             "config": {"encoder_lr": 2.5e-5, "head_lr": 1e-4, "freeze_encoder": False},
             "val_groups": {"S1": 2}, "history": [{"epoch": 1, "validation": {
                 "S1": {"items": 2, "loss": .4, "accuracy": .8, "brier": .2, "ece": .05}}}]}
    write_json(root / run_id / "run.json", value)
    write_json(root / run_id / "checkpoints/epoch_01/rl_agent_config.json", {
        "encoder": "recorded-encoder", "head_layers": 2, "max_prefixes": 6,
        "training_run": {"run_id": run_id, "epoch": 1}})
    return value


def laya_node(run_id, score, group="group-A", loss=.4):
    return {"run_id": run_id, "checkpoint_id": run_id + "-e01", "epoch": 1,
            "path": run_id + "/checkpoints/epoch_01", "run_status": "completed",
            "loadable": True, "comparable_group_id": group, "selection_score": score, "primary_score": score,
            "validation": {"S1": {"items": 2, "loss": loss, "accuracy": .8, "brier": .2, "ece": .05}}}


def laya_boundary(root, run_id):
    run = laya_run(root, run_id)
    run['epochs_max'] = 2
    run['history'].append({**copy.deepcopy(run['history'][0]), 'epoch': 2})
    write_json(root / run_id / 'run.json', run)
    return run


def full_exposure(records=1, passes=2):
    return {'source_records': records, 'records_used': records, 'input_passes': passes,
            'teacher_source_records': records, 'teacher_records_retained': records,
            'teacher_input_passes_retained': passes, 'teacher_input_passes_incomplete': 0,
            'capability_source_records': records, 'capability_records_retained': records,
            'capability_input_passes_retained': passes, 'capability_input_passes_incomplete': 0}


def kev_metrics(*, nll=1.0, acc=.5, brier=.5, ece=.1):
    return {"evaluation_status": "EVALUATED", "exit_code": 0, "validation_protocol": "KEV_FIXED_VAL_JSONL",
            "validation_set": "data/kev/公开数据/val.jsonl", "dataset_split": "val", "test_used": False,
            "coverage": {"requested_records": 8436, "evaluated_records": 8436,
                         "requested_questions": 9330, "evaluated_questions": 9330,
                         "rejected_records": 0, "truncated_records": 0},
            "clean": {"n": 9330, "nll": nll, "acc": acc, "brier": brier, "ece": ece}}


def kev_candidate(root, cid, *, group="same-group", metrics=None):
    candidate = {"candidate_id": cid, "name": cid, "status": "COMPLETED", "training_status": "COMPLETED",
                 "checkpoint_path": f"runs/{cid}/checkpoint", "retention_group": group,
                 "metrics": metrics or kev_metrics()}
    args = {"base": str(root / "models/recorded-kev-base"), "lora": 16, "full_ft": 0,
            "head_dim": 256, "option_isolation": 0, "special_embeddings": 0, "lora_targets": "all",
            "lr": 2e-5, "epochs": 1, "batch": 1, "accum": 4, "seed": 42, "max_state": 384}
    candidate["training_parameters"] = args
    write_json(root / candidate["checkpoint_path"] / "training_config.json", {"args": args})
    write_json(root / candidate["checkpoint_path"] / "adapter_config.json", {
        "r": 16, "base_model_name_or_path": args["base"]})
    report_path = root / candidate["checkpoint_path"] / "val_metrics/attempt_0001/report.json"
    candidate["metrics"]["report_path"] = str(report_path)
    write_json(report_path, {"clean": candidate["metrics"]["clean"], "coverage": candidate["metrics"]["coverage"],
                             "run": str(root / candidate["checkpoint_path"]),
                             "data": str(root / candidate["metrics"]["validation_set"])})
    write_json(root / candidate["checkpoint_path"] / "val_metrics.json", candidate["metrics"])
    write_rows(root / candidate["metrics"]["validation_set"], [{"fixed_val_fixture": True}])
    return candidate


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def fake_kev_files(self, allowed):
        return patch.object(dispatcher, "check_checkpoint_integrity",
                            side_effect=lambda path: (path.parent.name in allowed, "simulated entity"))

    def kev_completed_matrix(self):
        reference = kev_candidate(self.root, "KEV-V8-C03", group="reference-group")
        first = kev_candidate(self.root, "KEV-V8-R01", group=cont.KEV_COMPLETION_GROUP,
                              metrics=kev_metrics(nll=.8, acc=.7, brier=.3, ece=.05))
        second = kev_candidate(self.root, "KEV-V8-R02", group=cont.KEV_COMPLETION_GROUP,
                               metrics=kev_metrics(nll=.6, acc=.8, brier=.2, ece=.03))
        unrelated = {"candidate_id": "KEV-V8-C05", "name": "existing-state-experiment",
                     "checkpoint_path": "runs/existing-state-experiment/checkpoint",
                     "status": "PENDING", "training_status": "UNKNOWN",
                     "pending_reason": "Original state material unavailable"}
        write_json(self.root / "data/kev/v8_extension/materialization_coverage.json", {
            "runs": {"R01": {"status": "READY"}, "R02": {"status": "READY"}}})
        return [reference, first, second, unrelated]

    def test_serializer_matches_serving_and_preserves_candidates(self):
        original = feature_row()
        result = cont.serialize_training_record(original)
        self.assertEqual(result["state"], PreDecisionState.model_validate(original["pre_decision_state"]).router_text())
        self.assertEqual(list(result["questions"]["model_choice"]["criteria"]), ["b", "a"])
        self.assertEqual([c["action_id"] for c in json.loads(result["state"])["capability_cards"]], ["b:none", "a:none"])
        self.assertEqual(original["state"], "UNUSED")
        self.assertEqual(result["expected"], original["expected"])

    def test_later_teacher_state_is_not_consumed(self):
        row = feature_row()
        row["pre_decision_state"]["teacher_assessment"]["assessed_through_step"] = 4
        with self.assertRaises(ValueError):
            cont.serialize_training_record(row)

    def test_canonical_decision_features_survive_empty_older_fields(self):
        row = feature_row()
        row.update(teacher_assessment=None, capability_cards=[], capability_snapshot_id=None)
        result = cont.serialize_training_record(row)
        state = json.loads(result["state"])
        self.assertEqual(result["pre_decision_state"]["teacher_assessment"]["teacher_model_id"], "recorded-teacher")
        self.assertEqual(state["teacher_assessment"]["progress_summary"], "Observed progress")
        self.assertEqual([c["action_id"] for c in state["capability_cards"]], ["b:none", "a:none"])

    def test_laya_optional_input_keeps_original_validation(self):
        old = self.root / "original"
        new = self.root / "prepared"
        write_rows(old / "train/S1.jsonl", [{"state": "OLD_TRAIN"}])
        write_rows(old / "val/S1.jsonl", [{"state": "ORIGINAL_FIXED_VAL"}])
        write_rows(new / "train/S1.jsonl", [feature_row()])
        module = types.SimpleNamespace(
            read_data=lambda path: [json.loads(line) for line in Path(path).read_text().splitlines()],
            items_from_rows=lambda tok, rows, **kwargs: ([copy.deepcopy(row) for row in rows], {}))
        train, val, _, val_rows = laya_batch_train._load_named_groups(old, ["S1"], None, module, 1024, 512)
        self.assertEqual(train["S1"][0]["state"], "OLD_TRAIN")
        self.assertEqual(val["S1"][0]["state"], "ORIGINAL_FIXED_VAL")
        transform = Mock(wraps=cont.serialize_training_record)
        train, val, _, val_rows = laya_batch_train._load_named_groups(
            new, ["S1"], None, module, 1024, 512, validation_root=old, record_transform=transform)
        self.assertEqual(transform.call_count, 1)
        self.assertEqual(train["S1"][0]["state"], cont.serialize_training_record(feature_row())["state"])
        self.assertEqual(val_rows["S1"], [{"state": "ORIGINAL_FIXED_VAL"}])
        self.assertEqual(val["S1"][0]["state"], "ORIGINAL_FIXED_VAL")

    def test_relative_training_paths_reach_original_laya_loader(self):
        data = self.root / "prepared"
        metadata_path = data / "summary.json"
        metadata = {"trainer_root": "views", "trainer_views": {"train": {"S1": "custom/supervision.jsonl"}}}
        view = data / "views/custom/supervision.jsonl"
        write_rows(view, [feature_row()])
        fixed = self.root / "original/fixed/s1.jsonl"
        write_rows(fixed, [{"state": "ORIGINAL_FIXED_VAL"}])
        paths = cont.training_paths(metadata, metadata_path)
        self.assertEqual(paths, {"S1": view.resolve()})
        module = types.SimpleNamespace(
            read_data=lambda path: [json.loads(line) for line in Path(path).read_text().splitlines()],
            items_from_rows=lambda tok, rows, **kwargs: (rows, {}))
        train, val, _, _ = laya_batch_train._load_named_groups(
            data, ["S1"], None, module, 1024, 512, training_paths=paths,
            validation_paths={"S1": fixed}, record_transform=cont.serialize_training_record)
        self.assertEqual(train["S1"][0]["state"], cont.serialize_training_record(feature_row())["state"])
        self.assertEqual(val["S1"][0]["state"], "ORIGINAL_FIXED_VAL")

    def test_laya_run_cannot_replace_original_fixed_val_counts(self):
        out = self.root / "runs/original"
        run = laya_run(out, "A0")
        run["val_groups"] = {"S1": 1}
        run["history"][0]["validation"]["S1"]["items"] = 1
        self.assertFalse(cont._laya_val_complete(run, {"S1": 2}))

    def test_laya_next_child_boundary_does_not_wait_for_theoretical_matrix(self):
        prepared(self.root, ready=False)
        out = self.root / "runs/original"
        write_json(out / "full_coverage_manifest.json", {"plans": {"A0": {}, "F14": {}}})
        write_json(out / "experiment_matrix.json", {
            "selected_queue": ["A0"], "plans": {"OLD_UNMATERIALIZED": {"status": "ELIGIBLE"}}})
        write_rows(out / "val/S1.jsonl", [{"fixed": 1}, {"fixed": 2}])
        run = laya_boundary(out, "A0")
        write_json(out / 'checkpoint_manifest.json', {'checkpoints': [laya_node('A0', 120)]})
        state = {'completed_runs': [], 'current_run': 'A0', 'queue_status': 'RUNNING'}
        original = copy.deepcopy(state)
        trainer = Mock(return_value=run)
        with patch.object(retention, 'has_physical_weights', return_value=True), \
             patch.object(retention, 'is_loadable_checkpoint_path', return_value=True):
            result = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='A0',
                                       queue_state=state, trainer=trainer, resource_reader=lambda: (True, {}))
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(trainer.call_count, 1)
        self.assertEqual(state, original)
        self.assertNotIn('v9_continuation', state)

    def test_laya_incomplete_child_does_not_launch(self):
        prepared(self.root)
        out = self.root / "runs/original"
        write_json(out / "full_coverage_manifest.json", {"plans": {"F13": {}, "F14": {}}})
        laya_run(out, "F13", complete=False)
        state = {"completed_runs": ["F13"], "queue_status": "IDLE_STAGE_COMPLETE", "original_value": 15}
        trainer = Mock()
        result = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='F13',
                                   queue_state=state, trainer=trainer)
        self.assertEqual(result["status"], "TRAINING_PENDING")
        self.assertEqual(result['pending_reason'], 'original_child_two_epochs_or_fixed_val_incomplete')
        self.assertEqual(state["original_value"], 15)
        self.assertEqual(trainer.call_count, 0)
        self.assertFalse((out / 'queue_state.json').exists())
        self.assertEqual(json.loads((out / 'F13/run.json').read_text())['status'], 'running')

    def test_laya_uses_original_score_group_and_existing_physical_parent(self):
        out = self.root / "runs/original"
        for rid in ("A0", "A1", "A2", "B0"):
            laya_run(out, rid)
        nodes = [laya_node("A0", 90, loss=.1), laya_node("A1", 120, loss=.4),
                 laya_node("A2", 500), laya_node("B0", 900, "another-protocol")]
        write_json(out / "checkpoint_manifest.json", {"checkpoints": nodes})
        state = {"completed_runs": ["A0", "A1", "A2", "B0"]}
        with patch.object(retention, "has_physical_weights", side_effect=lambda path: path.parent.parent.name != "A2"), \
             patch.object(retention, "is_loadable_checkpoint_path", return_value=True):
            parent = cont.select_laya_parent(out, state, {"S1": 2}, "group-A")
        self.assertEqual(parent[0]["run_id"], "A1")

    def test_laya_ignores_alias_dev_score_and_different_architecture(self):
        out = self.root / "runs/original"
        for rid in ("ALIAS_DEV", "OTHER_ARCH", "CURRENT"):
            laya_run(out, rid)
        alias = laya_node("ALIAS_DEV", 90)
        alias.update(selection_score=9000, external_dev_status="ALIAS")
        other = laya_node("OTHER_ARCH", 8000)
        cfg_path = out / "OTHER_ARCH/checkpoints/epoch_01/rl_agent_config.json"
        config = json.loads(cfg_path.read_text())
        config["encoder"] = "different-encoder"
        write_json(cfg_path, config)
        current = laya_node("CURRENT", 120)
        write_json(out / "checkpoint_manifest.json", {"checkpoints": [alias, other, current]})
        with patch.object(retention, "has_physical_weights", return_value=True), \
             patch.object(retention, "is_loadable_checkpoint_path", return_value=True):
            parent = cont.select_laya_parent(out, {"completed_runs": ["ALIAS_DEV", "OTHER_ARCH", "CURRENT"]}, {"S1": 2})
        self.assertEqual(parent[0]["run_id"], "CURRENT")

    def test_laya_requires_selected_epoch_complete_val_and_matching_origin(self):
        out = self.root / "runs/original"
        run = laya_run(out, "A0")
        run["epochs_max"] = 2
        complete = copy.deepcopy(run["history"][0])
        complete["epoch"] = 2
        run["history"][0]["validation"]["S1"].update(items=1, loss=.1)
        run["history"].append(complete)
        write_json(out / "A0/run.json", run)
        first = laya_node("A0", 900)
        first["validation"] = run["history"][0]["validation"]
        second = {**laya_node("A0", 120), "checkpoint_id": "A0-e02", "epoch": 2,
                  "path": "A0/checkpoints/epoch_02", "validation": complete["validation"]}
        cfg_path = out / "A0/checkpoints/epoch_02/rl_agent_config.json"
        config = {"encoder": "recorded-encoder", "head_layers": 2, "max_prefixes": 6,
                  "training_run": {"run_id": "A0", "epoch": 2}}
        write_json(cfg_path, config)
        write_json(out / "checkpoint_manifest.json", {"checkpoints": [first, second]})
        with patch.object(retention, "has_physical_weights", return_value=True), \
             patch.object(retention, "is_loadable_checkpoint_path", return_value=True):
            parent = cont.select_laya_parent(out, {"completed_runs": ["A0"]}, {"S1": 2})
            self.assertEqual(parent[0]["checkpoint_id"], "A0-e02")
            config["training_run"]["epoch"] = 1
            write_json(cfg_path, config)
            self.assertIsNone(cont.select_laya_parent(out, {"completed_runs": ["A0"]}, {"S1": 2}))

    def test_laya_auxiliary_only_score_does_not_replace_s1_parent(self):
        out = self.root / "runs/original"
        laya_run(out, "S1_PARENT")
        run = laya_run(out, "S3_ONLY")
        metrics = run["history"][0]["validation"].pop("S1")
        run["val_groups"] = {"S3": 2}
        run["history"][0]["validation"] = {"S3": metrics}
        write_json(out / "S3_ONLY/run.json", run)
        node = laya_node("S3_ONLY", 9000, "only-S3")
        node["validation"] = {"S3": metrics}
        write_json(out / "checkpoint_manifest.json", {"checkpoints": [laya_node("S1_PARENT", 120), node]})
        with patch.object(retention, "has_physical_weights", return_value=True), \
             patch.object(retention, "is_loadable_checkpoint_path", return_value=True):
            parent = cont.select_laya_parent(out, {"completed_runs": ["S1_PARENT", "S3_ONLY"]}, {"S1": 2, "S3": 2})
        self.assertEqual(parent[0]["run_id"], "S1_PARENT")

    def test_laya_reservation_is_single_and_passes_original_fixed_val(self):
        metadata_path, metadata = prepared(self.root)
        out = self.root / "runs/original"
        write_json(out / "full_coverage_manifest.json", {"plans": {"A0": {}}, "fixed_validation": {"S1": "val/S1.jsonl"}})
        write_rows(out / "val/S1.jsonl", [{"state": "V1"}, {"state": "V2"}])
        original_run = laya_boundary(out, "A0")
        write_json(out / "checkpoint_manifest.json", {"checkpoints": [laya_node("A0", 120)]})
        state = {"completed_runs": ["A0"], "queue_status": "IDLE_STAGE_COMPLETE",
                 "reconciliation": {"queued_count": 9}}
        result_meta = {**original_run, 'run_id': 'V9_LAYA_001',
                       "loaded": {"train_S1": {"rows": 1, "items": 1}},
                       'v9_continuation': {'input_exposure': full_exposure()}}
        trainer = Mock(return_value=result_meta)
        with patch.object(retention, "has_physical_weights", return_value=True), \
             patch.object(retention, "is_loadable_checkpoint_path", return_value=True):
            result = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='A0', queue_state=state, trainer=trainer,
                                        resource_reader=lambda: (True, {"source": "simulated"}))
            write_json(out / 'queue_state.json', state)
            laya_boundary(out, 'NEXT_CHILD')
            again = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='NEXT_CHILD',
                                      queue_state=state, trainer=trainer)
            metadata["dataset_revision"] = "later-revision"
            write_json(metadata_path, metadata)
            self.assertEqual(cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='NEXT_CHILD',
                                               queue_state=state, trainer=trainer), result)
        self.assertEqual(result, again)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["feature_training_status"], "FEATURE_TRAINED")
        self.assertEqual(trainer.call_count, 1)
        self.assertEqual(trainer.call_args.kwargs["validation_root"], str(out.resolve()))
        self.assertEqual({key: Path(value).resolve() for key, value in trainer.call_args.kwargs["training_paths"].items()},
                         {"S1": (metadata_path.parent / "train/S1.jsonl").resolve()})
        self.assertEqual(trainer.call_args.kwargs["validation_paths"], {"S1": str((out / "val/S1.jsonl").resolve())})
        self.assertEqual(result["parent_selection_basis"], "FIXED_VAL_INTERNAL_ONLY")
        self.assertIs(trainer.call_args.kwargs["record_transform"], cont.serialize_training_record)
        self.assertIn("A0", trainer.call_args.args[1]["plans"])
        self.assertNotIn('v9_continuation', state)
        self.assertEqual(json.loads((out / 'A0/run.json').read_text())['v9_continuation']['run_id'], 'V9_LAYA_001')
        self.assertNotIn('v9_continuation', json.loads((out / 'NEXT_CHILD/run.json').read_text()))
        self.assertEqual(json.loads((out / "full_coverage_manifest.json").read_text())["plans"], {"A0": {}})

    def test_no_prepared_output_leaves_original_queue_unchanged(self):
        out = self.root / "runs/original"
        state = {"completed_runs": ["A0"]}
        self.assertIsNone(cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='A0', queue_state=state))
        self.assertEqual(state, {"completed_runs": ["A0"]})
        self.assertFalse((out / "queue_state.json").exists())
        queue = []
        persist = Mock()
        self.assertIsNone(cont.plan_kev_continuation(queue, project_root=self.root, persist=persist))
        self.assertEqual(persist.call_count, 0)

    def test_material_validates_rows_after_first_feature_sample(self):
        metadata_path, _ = prepared(self.root)
        future = feature_row()
        future["pre_decision_state"]["teacher_assessment"]["assessed_through_step"] = 4
        write_rows(metadata_path.parent / "train/S1.jsonl", [feature_row(), future])
        trainer = Mock()
        with self.assertRaises(ValueError):
            cont._material(metadata_path, json.loads(metadata_path.read_text()))
        self.assertEqual(trainer.call_count, 0)

    def test_kev_scores_only_same_architecture_and_original_validation(self):
        c03 = kev_candidate(self.root, "KEV-V8-C03", metrics=kev_metrics())
        r01 = kev_candidate(self.root, "R01", metrics=kev_metrics(nll=.1, acc=.2, brier=1.4, ece=.6))
        r02 = kev_candidate(self.root, "R02", metrics=kev_metrics(nll=.6, acc=.8, brier=.2, ece=.03))
        other = kev_candidate(self.root, "OTHER", group="other-group", metrics=kev_metrics(nll=.01, acc=.99, brier=.01, ece=0))
        missing = kev_candidate(self.root, "REMOVED", metrics=kev_metrics(nll=.01, acc=.99, brier=.01, ece=0))
        changed = kev_candidate(self.root, "INCOMPLETE", metrics=kev_metrics())
        changed["metrics"]["coverage"]["evaluated_records"] = 4
        with self.fake_kev_files({"KEV-V8-C03", "R01", "R02", "OTHER", "INCOMPLETE"}):
            parent = cont.select_kev_parent([c03, r01, r02, other, missing, changed], self.root, "same-group")
        self.assertEqual(parent[0]["candidate_id"], "R02")
        self.assertEqual(parent[2]["full_ft"], 0)

    def test_kev_requires_actual_fixed_val_report_for_same_checkpoint(self):
        c03 = kev_candidate(self.root, "KEV-V8-C03")
        alias = kev_candidate(self.root, "ALIAS", metrics=kev_metrics(nll=.1, acc=.9, brier=.1, ece=0))
        report_path = Path(alias["metrics"]["report_path"])
        report = json.loads(report_path.read_text())
        report["run"] = str(self.root / c03["checkpoint_path"])
        write_json(report_path, report)
        changed = kev_candidate(self.root, "CHANGED", metrics=kev_metrics(nll=.2, acc=.9, brier=.1, ece=0))
        changed["metrics"]["clean"]["nll"] = .01
        with self.fake_kev_files({"KEV-V8-C03", "ALIAS", "CHANGED"}):
            parent = cont.select_kev_parent([c03, alias, changed], self.root, "same-group")
        self.assertEqual(parent[0]["candidate_id"], "KEV-V8-C03")

    def test_kev_excludes_changed_lora_targets_inside_same_research_group(self):
        c03 = kev_candidate(self.root, "KEV-V8-C03")
        different = kev_candidate(self.root, "DIFFERENT", metrics=kev_metrics(nll=.1, acc=.95, brier=.01, ece=0))
        args = copy.deepcopy(different["training_parameters"])
        args["lora_targets"] = "attention"
        write_json(self.root / different["checkpoint_path"] / "training_config.json", {"args": args})
        current = kev_candidate(self.root, "CURRENT", metrics=kev_metrics(nll=.6, acc=.8, brier=.2, ece=.03))
        with self.fake_kev_files({"KEV-V8-C03", "DIFFERENT", "CURRENT"}):
            parent = cont.select_kev_parent([c03, different, current], self.root, "same-group")
        self.assertEqual(parent[0]["candidate_id"], "CURRENT")

    def test_kev_plan_pending_then_once_queued_without_old_recipe_changes(self):
        path, metadata = prepared(self.root, ready=False)
        c03 = kev_candidate(self.root, "KEV-V8-C03")
        r01 = kev_candidate(self.root, "R01", metrics=kev_metrics(nll=.6, acc=.8, brier=.2, ece=.03))
        r01["status"] = "PENDING"
        queue = [c03, r01]
        persist = Mock()
        with self.fake_kev_files({"KEV-V8-C03", "R01"}):
            record = cont.plan_kev_continuation(queue, project_root=self.root, persist=persist)
            self.assertEqual(record["status"], "TRAINING_PENDING")
            self.assertIn("R01", record["original_pending_runs"])
            r01["status"] = "COMPLETED"
            original_recipes = copy.deepcopy(queue[:2])
            metadata["teacher_data_status"] = "PARTIAL"
            write_json(path, metadata)
            ready = cont.plan_kev_continuation(queue, project_root=self.root, persist=persist)
            self.assertIs(record, ready)
            self.assertEqual(ready["status"], "QUEUED")
            candidate = queue[-1]
            self.assertEqual(candidate["training_parameters"]["max_state"], 8192)
            self.assertEqual(candidate["training_parameters"]["epochs"], 2)
            self.assertEqual(candidate['v9_continuation']['parent_training_parameters']['epochs'], 1)
            self.assertEqual(candidate['v9_continuation']['parent_training_parameters']['max_state'], 384)
            self.assertEqual(candidate["training_parameters"]["full_ft"], 0)
            metadata["dataset_revision"] = "later-revision"
            write_json(path, metadata)
            candidate["status"] = "FAILED"
            candidate["training_attempts"] = [{"command": "simulated-existing-attempt"}]
            failed = cont.plan_kev_continuation(queue, project_root=self.root, persist=persist)
            self.assertEqual(failed["status"], "QUEUED")
            self.assertEqual(len(candidate['training_attempts']), 1)
        self.assertEqual(len(queue), 3)
        self.assertEqual(queue[:2], original_recipes)
        self.assertEqual(record["parent_candidate_id"], "R01")

    def test_kev_completed_matrix_is_independent_of_other_pending_experiments(self):
        prepared(self.root)
        queue = self.kev_completed_matrix()
        original = copy.deepcopy(queue)
        with self.fake_kev_files({"KEV-V8-C03", "KEV-V8-R01", "KEV-V8-R02"}):
            record = cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock(),
                                                completion_group=cont.KEV_COMPLETION_GROUP)
            again = cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock())
        self.assertIs(record, again)
        self.assertEqual(record["status"], "QUEUED")
        self.assertEqual(record["original_pending_runs"], [])
        self.assertEqual(record["original_boundary_ids"], ["KEV-V8-R01", "KEV-V8-R02"])
        self.assertEqual(record["parent_candidate_id"], "KEV-V8-R02")
        self.assertEqual(queue[:4], original)
        self.assertEqual(len(queue), 5)

    def test_kev_completion_uses_existing_matrix_plan_and_complete_val(self):
        prepared(self.root)
        queue = self.kev_completed_matrix()
        missing = queue.pop(2)
        with self.fake_kev_files({"KEV-V8-C03", "KEV-V8-R01", "KEV-V8-R02"}):
            record = cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock(),
                                                completion_group=cont.KEV_COMPLETION_GROUP)
            self.assertEqual(record["original_pending_runs"], ["KEV-V8-R02"])
            self.assertEqual(record["status"], "TRAINING_PENDING")
            missing["metrics"]["coverage"]["evaluated_records"] = 1
            queue.append(missing)
            incomplete = cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock())
        self.assertIs(incomplete, record)
        self.assertEqual(record["status"], "TRAINING_PENDING")
        self.assertEqual(record["original_pending_runs"], ["KEV-V8-R02"])

    def test_kev_existing_cli_can_plan_without_touching_other_experiments_or_gpu(self):
        metadata_path, _ = prepared(self.root)
        queue = self.kev_completed_matrix()
        original = copy.deepcopy(queue)
        with self.fake_kev_files({"KEV-V8-C03", "KEV-V8-R01", "KEV-V8-R02"}), \
             patch.object(dispatcher, "PROJECT_ROOT", self.root), \
             patch.object(dispatcher, "load_queue", return_value=queue), patch.object(dispatcher, "save_queue"), \
             patch.object(dispatcher, "complete_candidate_plan") as old_plan, \
             patch.object(dispatcher, "refresh_training") as refresh, \
             patch.object(dispatcher, "update_retention") as retention_call, \
             patch.object(dispatcher.subprocess, "run") as gpu, \
             patch.object(dispatcher.subprocess, "Popen") as launch, patch("builtins.print"):
            result = dispatcher.main(["--v9-continuation", "--plan-only", "--prepared-path", str(metadata_path)])
        self.assertEqual(result, 0)
        self.assertEqual(old_plan.call_count, 0)
        self.assertEqual(refresh.call_count, 0)
        self.assertEqual(retention_call.call_count, 0)
        self.assertEqual(gpu.call_count, 0)
        self.assertEqual(launch.call_count, 0)
        self.assertEqual(queue[:4], original)
        self.assertEqual(queue[-1]["status"], "QUEUED")

    def test_kev_continuation_mode_never_dispatches_unrelated_pending_candidate(self):
        old = {"candidate_id": "KEV-V8-C05", "status": "PENDING", "training_status": "UNKNOWN"}
        candidate = {"candidate_id": "KEV-V9-001", "status": "QUEUED", "training_status": "UNKNOWN",
                     "v9_continuation": {"status": "QUEUED"}}
        with patch.object(dispatcher, "load_queue", return_value=[old, candidate]), \
             patch.object(dispatcher, "refresh_training", return_value=False) as refresh, \
             patch.object(dispatcher, "save_queue"), patch.object(dispatcher, "scientific_selection") as selection, \
             patch.object(cont, "plan_kev_continuation", return_value={"status": "TRAINING_PENDING"}), \
             patch.object(dispatcher.subprocess, "run") as gpu, \
             patch.object(dispatcher.subprocess, "Popen") as launch:
            self.assertEqual(dispatcher.main_loop(v9_only=True, completion_group=cont.KEV_COMPLETION_GROUP), 1)
        refresh.assert_called_once_with(candidate)
        self.assertEqual(selection.call_count, 0)
        self.assertEqual(gpu.call_count, 0)
        self.assertEqual(launch.call_count, 0)
        self.assertEqual(old["status"], "PENDING")

    def test_kev_failed_attempt_without_worker_can_be_reserved_normally(self):
        candidate = {"status": "FAILED", 'training_status': 'FAILED', 'pid': 123,
                     'training_attempts': [{'exit_code': 1, 'status': 'FAILED'}],
                     "v9_continuation": {"status": "FAILED"}}
        command = ["recorded-python", "-m", "kev.train"]
        with patch.object(dispatcher, 'is_pid_alive', return_value=False):
            attempt = cont.reserve_kev_attempt(candidate, command)
        self.assertEqual(attempt["status"], "LAUNCH_REQUESTED")
        self.assertEqual(len(candidate["training_attempts"]), 2)
        self.assertEqual(candidate["v9_continuation"]["status"], "LAUNCH_REQUESTED")
        self.assertNotIn('pending_reason', candidate)

    def test_kev_active_worker_or_completed_training_never_relaunches(self):
        candidate = {'status': 'RUNNING', 'pid': 123, 'training_status': 'RUNNING',
                     'training_attempts': [{'pid': 123}], 'v9_continuation': {'status': 'RUNNING'}}
        with patch.object(dispatcher, 'is_pid_alive', return_value=True):
            self.assertIsNone(cont.reserve_kev_attempt(candidate, ['original-command']))
        self.assertEqual(candidate['status'], 'RUNNING')
        candidate['training_status'] = 'COMPLETED'
        self.assertIsNone(cont.reserve_kev_attempt(candidate, ['original-command']))
        self.assertEqual(len(candidate['training_attempts']), 1)
        self.assertNotIn('pending_reason', candidate)

    def test_kev_reuses_official_data_and_reports_actual_exposure(self):
        metadata_path, _ = prepared(self.root)
        view = metadata_path.parent / "train/S1.jsonl"
        s2 = metadata_path.parent / 'train/S2.jsonl'
        write_rows(s2, [feature_row()])
        original = feature_row()
        original['provenance']['stable_record_id'] = 'same-source-different-view-question'
        write_rows(view, [original])
        auxiliary = copy.deepcopy(original)
        auxiliary['questions'] = {'observed_action': auxiliary['questions']['model_choice']}
        auxiliary['expected'] = {'observed_action': auxiliary['expected']['model_choice']}
        write_rows(s2, [auxiliary])
        candidate = {"candidate_id": "KEV-V9-001", "epochs": 1, "recipe": {},
                     "v9_continuation": {"training_paths": {"S1": str(view), 'S2': str(s2)}}}
        emitted = []
        train = types.ModuleType("kev.train")
        def official_load(path, source):
            rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
            for index, row in enumerate(rows):
                row['_meta'] = {'id': f'{source}/{index}'}
            return rows
        train.load_records = Mock(side_effect=official_load)
        train.training_requests = lambda args, tok, manifest, holdout: train.load_records(str(metadata_path))[:1]
        train.batch_loss = Mock(return_value=('original-loss', {}))
        train.question_loss = Mock(return_value=2.0)
        train.write_json = lambda path, value: emitted.append((str(path), value))
        original_load = train.load_records
        original_requests, original_batch_loss = train.training_requests, train.batch_loss
        original_argv = sys.argv
        def main():
            tok = types.SimpleNamespace(decode=lambda ids, **kwargs: ''.join(map(chr, ids)))
            rows = train.training_requests(None, tok, None, None)
            self.assertEqual(rows[0]["state"], cont.serialize_training_record(feature_row())["state"])
            self.assertEqual(train.question_loss(None, {"qid": "model_choice"}), 2.0)
            ids = [0] + list(map(ord, rows[0]['state']))
            variant = types.SimpleNamespace(request_id=rows[0]['_meta']['id'], enc={'ids': ids, 'seg': [0] * len(ids)})
            self.assertEqual(train.batch_loss(None, None, [variant], None, None, None, None), ('original-loss', {}))
            train.write_json("training_config.json", {"args": {}, "init_source": "recorded-parent"})
            train.write_json("training_metrics.json", {"records_seen": 1})
        train.main = Mock(side_effect=main)
        kev = types.ModuleType("kev")
        kev.train = train
        with patch.dict(sys.modules, {"kev": kev, "kev.train": train}), \
             patch.object(dispatcher, "load_queue", return_value=[candidate]):
            dispatcher.train_with_question_weights(candidate["candidate_id"], ["--data", str(metadata_path)])
        self.assertEqual(train.main.call_count, 1)
        self.assertEqual(original_load.call_args_list, [call(str(view), 'custom_S1'), call(str(s2), 'custom_S2')])
        self.assertIs(train.load_records, original_load)
        self.assertIs(train.training_requests, original_requests)
        self.assertIs(train.batch_loss, original_batch_loss)
        self.assertIs(sys.argv, original_argv)
        result = emitted[-1][1]["v9_continuation"]
        self.assertEqual(result["material_records"], 2)
        self.assertEqual(result['admitted_records'], 1)
        self.assertEqual(result['input_exposure']['teacher_records_retained'], 1)
        self.assertEqual(result['input_exposure']['records_used'], 1)
        self.assertEqual(result['input_exposure']['source_records'], 2)
        self.assertEqual(result["feature_training_status"], "FEATURE_PARTIALLY_TRAINED")

    def test_kev_end_boundary_plans_without_another_dispatcher(self):
        from modelrouter.v9.training.continuation import plan_kev_continuation
        self.assertTrue(callable(plan_kev_continuation))
        with patch.object(dispatcher, "load_queue", return_value=[]), \
             patch.object(dispatcher, "scientific_selection"), \
             patch.object(cont, "plan_kev_continuation", return_value={"status": "TRAINING_PENDING"}) as planner, \
             patch.object(dispatcher.subprocess, "Popen") as launch:
            self.assertEqual(dispatcher.main_loop(), 0)
        self.assertEqual(planner.call_count, 1)
        self.assertEqual(launch.call_count, 0)

    def test_kev_pending_v9_material_returns_without_gpu_or_launch(self):
        candidate = {"candidate_id": "KEV-V9-001", "status": "QUEUED", "training_status": "UNKNOWN",
                     "v9_continuation": {"status": "QUEUED"}}
        with patch.object(dispatcher, "load_queue", return_value=[candidate]), \
             patch.object(dispatcher, "refresh_training", return_value=False), \
             patch.object(dispatcher, "save_queue"), patch.object(dispatcher, "scientific_selection"), \
             patch.object(cont, "plan_kev_continuation", return_value={"status": "TRAINING_PENDING"}), \
             patch.object(dispatcher.subprocess, "run") as resource, \
             patch.object(dispatcher.subprocess, "Popen") as launch:
            self.assertEqual(dispatcher.main_loop(), 1)
        self.assertEqual(resource.call_count, 0)
        self.assertEqual(launch.call_count, 0)

    def test_common_entry_is_only_an_alias_to_the_root_queue(self):
        from router_data import run_full_graded_queue as root_queue
        original = root_queue.run_queue
        queue_module = importlib.import_module("modelrouter.training.common.run_full_graded_queue")
        self.assertIs(queue_module, root_queue)
        self.assertIs(queue_module.run_queue, original)
        self.assertFalse(hasattr(queue_module, '_attach_v9'))
        self.assertFalse(hasattr(queue_module, '_run_queue_with_v9'))

    def test_material_accepts_formal_teacher_statuses_and_no_teacher_targets(self):
        metadata_path, metadata = prepared(self.root)
        row = feature_row()
        row['pre_decision_state'].pop('teacher_assessment')
        write_rows(metadata_path.parent / 'train/S1.jsonl', [row])
        for status in ('GENERATED', 'PARTIAL', 'NOT_GENERATED'):
            metadata['teacher_data_status'] = status
            paths, identity, reason = cont._material(metadata_path, metadata)
            self.assertIsNone(reason)
            self.assertEqual(identity['source_records'], {'S1': 1})
            self.assertEqual(identity['teacher_model_ids'], {})
            self.assertEqual(list(paths), ['S1'])
        self.assertEqual(cont.serialize_training_record(row)['expected'], row['expected'])

    def test_missing_or_empty_material_remains_a_normal_dependency(self):
        metadata_path, metadata = prepared(self.root)
        metadata['trainer_views']['train']['S2'] = 'train/missing.jsonl'
        self.assertEqual(cont._material(metadata_path, metadata)[2], 'missing_prepared_training_views')
        metadata['trainer_views']['train'].pop('S2')
        write_rows(metadata_path.parent / 'train/S1.jsonl', [])
        self.assertEqual(cont._material(metadata_path, metadata)[2], 'empty_prepared_training_views')

    def test_feature_status_uses_real_fields_not_only_record_counts(self):
        row = cont.serialize_training_record(feature_row())
        exposure = cont.InputExposure()
        exposure.add('train/0', row['state'])
        exposure.observe('train/0', row['state'].split('"teacher_assessment":')[0])
        self.assertEqual(exposure.summary()['records_used'], 1)
        self.assertEqual(exposure.summary()['partial_state_records_retained'], 1)
        self.assertEqual(exposure.summary()['full_state_records_retained'], 0)
        self.assertEqual(cont.feature_training_status(exposure.summary(), True), 'FEATURE_NOT_TRAINED')
        exposure.observe('train/0', row['state'])
        self.assertEqual(cont.feature_training_status(exposure.summary(), True), 'FEATURE_PARTIALLY_TRAINED')
        complete = cont.InputExposure()
        complete.add('train/0', row['state'])
        complete.observe('train/0', row['state'])
        self.assertEqual(cont.feature_training_status(complete.summary(), True), 'FEATURE_TRAINED')

    def test_laya_retry_and_saved_result_reuse_do_not_change_original_success(self):
        prepared(self.root)
        out = self.root / 'runs/original'
        original = laya_boundary(out, 'A0')
        write_rows(out / 'val/S1.jsonl', [{}, {}])
        write_json(out / 'checkpoint_manifest.json', {'checkpoints': [laya_node('A0', 120)]})
        saved = {**original, 'run_id': 'V9_LAYA_001', 'v9_continuation': {'input_exposure': full_exposure()}}
        def train(*args, **kwargs):
            if train.calls == 0:
                train.calls += 1
                raise ValueError('simulated failed training')
            train.calls += 1
            write_json(out / 'V9_LAYA_001/run.json', saved)
            return saved
        train.calls = 0
        with patch.object(retention, 'has_physical_weights', return_value=True), \
             patch.object(retention, 'is_loadable_checkpoint_path', return_value=True):
            failed = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='A0',
                                        trainer=train, resource_reader=lambda: (True, {}))
            self.assertEqual(failed['status'], 'FAILED')
            self.assertEqual(json.loads((out / 'A0/run.json').read_text())['status'], 'completed')
            laya_boundary(out, 'NEXT')
            done = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='NEXT',
                                      queue_state={'completed_runs': ['A0']}, trainer=train,
                                      resource_reader=lambda: (True, {}))
            self.assertEqual(done['status'], 'COMPLETED')
            owner = json.loads((out / 'A0/run.json').read_text())
            owner['v9_continuation'].update(status='RUNNING', worker_pid=123)
            write_json(out / 'A0/run.json', owner)
            with patch.object(dispatcher, 'is_pid_alive', return_value=False), \
                 patch.object(cont, 'select_laya_parent', side_effect=AssertionError('no reselection')):
                recovered = cont.continue_laya(project_root=self.root, out_root=out, completed_run_id='NEXT', trainer=train)
            self.assertEqual(recovered['status'], 'COMPLETED')
        self.assertEqual(train.calls, 2)
        self.assertEqual(done['run_id'], failed['run_id'])

    def test_original_full_child_calls_v9_only_after_saved_return(self):
        package, module = types.ModuleType('laya'), types.ModuleType('laya.train')
        package.train = module
        events = []
        def original(**kwargs):
            events.extend(['two_epochs', 'fixed_val', 'saved_original'])
            return {'run_id': 'NEXT', 'status': 'completed'}
        def after(**kwargs):
            events.append('v9_same_child')
            self.assertIs(kwargs['trainer'], laya_batch_train.run_sweep_experiment)
            self.assertEqual(kwargs['completed_run_id'], 'NEXT')
            return {'status': 'TRAINING_PENDING'}
        argv = ['laya_batch_train', '--full-coverage-run', 'NEXT', '--epochs', '2',
                '--project-root', str(self.root), '--out-root', str(self.root / 'runs')]
        with patch.dict(sys.modules, {'laya': package, 'laya.train': module}), \
             patch.object(sys, 'argv', argv), patch.object(laya_batch_train, 'run_full_coverage_stream_run', side_effect=original), \
             patch.object(cont, 'continue_laya', side_effect=after) as continuation, patch('builtins.print'):
            laya_batch_train.main()
        self.assertEqual(events, ['two_epochs', 'fixed_val', 'saved_original', 'v9_same_child'])
        self.assertEqual(continuation.call_count, 1)

    def test_v9_dependency_error_does_not_fail_a_successful_original_child(self):
        package, module = types.ModuleType('laya'), types.ModuleType('laya.train')
        package.train = module
        original = {'run_id': 'NEXT', 'status': 'completed'}
        argv = ['laya_batch_train', '--full-coverage-run', 'NEXT', '--project-root', str(self.root)]
        with patch.dict(sys.modules, {'laya': package, 'laya.train': module}), patch.object(sys, 'argv', argv), \
             patch.object(laya_batch_train, 'run_full_coverage_stream_run', return_value=original), \
             patch.object(cont, 'continue_laya', side_effect=ImportError('missing formatter')), patch('builtins.print') as emitted:
            self.assertIsNone(laya_batch_train.main())
        self.assertEqual(original['status'], 'completed')
        self.assertEqual(json.loads(emitted.call_args_list[0].args[0])['event'], 'v9_continuation_unavailable')

    def test_laya_original_encoder_counts_training_inputs_and_restores_function(self):
        data, out = self.root / 'prepared', self.root / 'runs'
        short, long = feature_row(), feature_row()
        long['pre_decision_state']['prompt'] = 'x' * 2000
        write_rows(data / 'train/S2.jsonl', [short, long])
        write_rows(out / 'val/S2.jsonl', [short, short])
        package, module = types.ModuleType('laya'), types.ModuleType('laya.train')
        package.train = module
        tok = types.SimpleNamespace(decode=lambda ids, **kwargs: ''.join(map(chr, ids)))
        class TrainConfig:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
            def validate(self):
                pass
        module.TrainConfig = TrainConfig
        module.read_data = lambda path: [json.loads(line) for line in Path(path).read_text().splitlines()]
        module.items_from_rows = lambda tok, rows, max_len, **kwargs: ([
            {'q': next(iter(row['questions'].values())), 'state_ids': list(map(ord, row['state']))[:max_len],
             'target': [.5, .5], 'k': 2, 'qtype': 0} for row in rows], {})
        def sequence(tok, state, question, max_len, head_max_len, option_order=None, state_ids=None,
                     return_truncation_stats=False):
            retained = state_ids[:max(0, max_len - 17)]
            value = ([0] * 16 + retained + [0], [1, 2])
            return value + ({'state_tokens_used': len(retained)},) if return_truncation_stats else value
        module.build_sequence = sequence
        module.encode_item = lambda tok, item, max_len, head_max_len, *args: {'ids': sequence(
            tok, None, item['q'], max_len, head_max_len, state_ids=item['state_ids'])[0]}
        official_encode = module.encode_item
        model = types.SimpleNamespace(to=Mock(), encoder=types.SimpleNamespace(config=types.SimpleNamespace(max_position_embeddings=8192)))
        module.load_checkpoint = lambda path: (model, tok, {'encoder': 'recorded-encoder'})
        module.optimizer_updates = lambda *args: 1
        module.save_checkpoint = Mock()
        def training(model, tok, items, config, dev, max_len, head_max_len, on_epoch_end):
            for epoch in range(config.epochs):
                for item in items:
                    module.encode_item(tok, item, max_len, head_max_len, None, False)
                on_epoch_end(epoch, .4)
        module.train_model = training
        fake_torch = types.ModuleType('torch')
        fake_torch.device = lambda value: value
        fake_torch.cuda = types.SimpleNamespace(is_available=lambda: False)
        manager = Mock()
        manager.pre_run_disk_check.return_value = {}
        manager.finalize_run_checkpoints.side_effect = lambda rid, meta, **kwargs: write_json(out / rid / 'run.json', meta)
        metrics = {'S2': {'items': 2, 'loss': .4, 'accuracy': .8, 'brier': .2, 'ece': .05}}
        spec = {'data': '.', 'groups': ['S2'], 'v9_continuation': {'data_identity': {'prepared_metadata': 'prepared/summary.json'}}}
        with patch.dict(sys.modules, {'laya': package, 'laya.train': module, 'torch': fake_torch}), \
             patch.object(laya_batch_train, 'CheckpointRetentionManager', return_value=manager), \
             patch.object(laya_batch_train, '_groups', return_value=metrics), patch.object(laya_batch_train, '_sweep_public_run'), \
             patch.object(laya_batch_train.subprocess, 'check_output', return_value='0'), patch('builtins.print'):
            result = laya_batch_train.run_sweep_experiment('V9_LAYA_001', {'plans': {'V9_LAYA_001': spec}},
                'remote-model-only', out, data_root=data, validation_root=out, epochs=2,
                record_transform=cont.serialize_training_record)
        self.assertIs(module.encode_item, official_encode)
        stats = result['v9_continuation']['input_exposure']
        self.assertEqual(stats['source_records'], 2)
        self.assertEqual(stats['records_used'], 2)
        self.assertEqual(stats['teacher_records_retained'], 1)
        self.assertEqual(stats['teacher_input_passes_retained'], 2)
        self.assertEqual(stats['teacher_input_passes_incomplete'], 2)
        self.assertEqual(stats['full_state_records_retained'], 1)
        self.assertEqual(stats['partial_state_records_retained'], 1)
        self.assertEqual(stats['full_state_input_passes'], 2)
        self.assertEqual(stats['partial_state_input_passes'], 2)
        self.assertEqual(result['v9_continuation']['feature_training_status'], 'FEATURE_PARTIALLY_TRAINED')
        self.assertEqual(result['max_len'], 1024)
        self.assertEqual(result['encoder_context_limit'], 8192)

    def test_kev_loop_retries_failed_candidate_once_without_other_dispatch(self):
        metadata_path, _ = prepared(self.root)
        queue = self.kev_completed_matrix()
        with self.fake_kev_files({'KEV-V8-C03', 'KEV-V8-R01', 'KEV-V8-R02'}):
            cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock(), completion_group=cont.KEV_COMPLETION_GROUP)
        candidate = queue[-1]
        candidate.update(status='FAILED', training_status='FAILED', pid=123, training_exit_code=1,
                         training_attempts=[{'status': 'FAILED', 'exit_code': 1}])
        write_json(self.root / 'runs' / candidate['name'] / 'cursor.json', {'pid': 123, 'exit_code': 1})
        write_json(self.root / dispatcher.DEFAULT_CANDIDATES[0]['checkpoint_path'] / 'training_metrics.json', {'peak_device_bytes': 1048576})
        process = Mock(pid=456, stdout=iter(['ep0 step 1/1 loss 0.8\n']))
        def finish_training():
            self.assertEqual(candidate['status'], 'RUNNING')
            self.assertEqual(candidate['training_status'], 'RUNNING')
            self.assertIsNone(candidate['training_exit_code'])
            self.assertEqual(candidate['training_attempts'][0]['exit_code'], 1)
            return 1
        process.wait.side_effect = finish_training
        def command(cmd, **kwargs):
            return types.SimpleNamespace(stdout='50000' if cmd[0] == 'nvidia-smi' else 'existing-source', returncode=0)
        with self.fake_kev_files({'KEV-V8-C03', 'KEV-V8-R01', 'KEV-V8-R02'}), \
             patch.object(dispatcher, 'PROJECT_ROOT', self.root), patch.object(dispatcher, 'KEV_RUNS_ROOT', self.root / 'runs'), \
             patch.object(dispatcher, 'load_queue', return_value=queue), patch.object(dispatcher, 'save_queue'), \
             patch.object(dispatcher, 'is_pid_alive', return_value=False), \
             patch.object(dispatcher.subprocess, 'run', side_effect=command), \
             patch.object(dispatcher.subprocess, 'Popen', return_value=process) as launch:
            result = dispatcher.main_loop(v9_only=True, prepared_path=metadata_path, completion_group=cont.KEV_COMPLETION_GROUP)
        self.assertEqual(result, 1)
        self.assertEqual(launch.call_count, 1)
        self.assertEqual(launch.call_args.args[0][:7], [str(self.root / '.venv/bin/python'), '-u', '-m',
            'modelrouter.training.kev_candidate_dispatcher', '--train-candidate', candidate['candidate_id'], '--'])
        self.assertEqual(launch.call_args.kwargs['cwd'], str(self.root))
        self.assertEqual(launch.call_args.kwargs['env']['PYTHONPATH'].split(dispatcher.os.pathsep),
            [str(self.root), str(self.root / 'external/kev'), str(self.root / 'our-project/code/src')])
        self.assertEqual(len(candidate['training_attempts']), 2)
        self.assertEqual(candidate['status'], 'FAILED')
        self.assertEqual(candidate['training_attempts'][-1]['exit_code'], 1)
        self.assertEqual(queue[3]['status'], 'PENDING')

    def test_kev_last_oom_lower_bound_reuses_original_resource_wait(self):
        metadata_path, _ = prepared(self.root)
        queue = self.kev_completed_matrix()
        with self.fake_kev_files({'KEV-V8-C03', 'KEV-V8-R01', 'KEV-V8-R02'}):
            cont.plan_kev_continuation(queue, project_root=self.root, persist=Mock(), completion_group=cont.KEV_COMPLETION_GROUP)
        candidate = queue[-1]
        run_dir = self.root / 'runs' / candidate['name']
        log_file = run_dir / 'train.log'
        log_text = (
            'torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 128.00 MiB. '
            'Including non-PyTorch memory, this process has 15.00 GiB memory in use.\n'
            'torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 60.00 MiB. '
            'GPU 0 has a total capacity of 47.54 GiB of which 52.38 MiB is free. '
            'Process 4085749 has 8.87 GiB memory in use. Process 12345 has 24.25 GiB memory in use. '
            'Including non-PyTorch memory, this process has 13.54 GiB memory in use.\n')
        run_dir.mkdir(parents=True, exist_ok=True)
        log_file.write_text(log_text, encoding='utf-8')
        attempts = [{'pid': 13266, 'status': 'FAILED', 'exit_code': 1},
                    {'pid': 16722, 'status': 'FAILED', 'exit_code': 1}]
        peak_file = self.root / dispatcher.DEFAULT_CANDIDATES[0]['checkpoint_path'] / 'training_metrics.json'
        for peak_bytes, expected_mib in ((10542966784, 15973), (21474836480, 22528)):
            with self.subTest(peak_bytes=peak_bytes):
                candidate.update(status='FAILED', training_status='FAILED', pid=16722,
                                 training_exit_code=1, training_attempts=copy.deepcopy(attempts))
                write_json(run_dir / 'cursor.json', {'pid': 16722, 'exit_code': 1})
                write_json(peak_file, {'peak_device_bytes': peak_bytes})
                with self.fake_kev_files({'KEV-V8-C03', 'KEV-V8-R01', 'KEV-V8-R02'}), \
                     patch.object(dispatcher, 'PROJECT_ROOT', self.root), \
                     patch.object(dispatcher, 'KEV_RUNS_ROOT', self.root / 'runs'), \
                     patch.object(dispatcher, 'load_queue', return_value=queue), patch.object(dispatcher, 'save_queue'), \
                     patch.object(dispatcher, 'is_pid_alive', return_value=False), \
                     patch.object(dispatcher.subprocess, 'run', return_value=types.SimpleNamespace(stdout='13932', returncode=0)), \
                     patch.object(dispatcher.subprocess, 'Popen') as launch:
                    self.assertEqual(dispatcher.main_loop(v9_only=True, prepared_path=metadata_path,
                        completion_group=cont.KEV_COMPLETION_GROUP), 1)
                launch.assert_not_called()
                self.assertEqual(candidate['status'], 'WAITING_FOR_GPU')
                self.assertEqual(candidate['training_status'], 'WAITING_FOR_GPU')
                self.assertEqual(candidate['training_attempts'], attempts)
                self.assertEqual(log_file.read_text(encoding='utf-8'), log_text)
                resource = candidate['gpu_resource']
                self.assertEqual(resource['peak_device_bytes'], peak_bytes)
                self.assertEqual(resource['required_mib'], expected_mib)
                self.assertEqual(resource['margin_mib'], 2048)
                self.assertEqual(resource['free_mib'], 13932)
                observation = resource['oom_observation']
                self.assertEqual(observation['source'], str(log_file))
                self.assertEqual(observation['line_number'], 2)
                self.assertEqual(observation['process_memory_gib'], 13.54)
                self.assertEqual(observation['failed_allocation_mib'], 60.0)
                self.assertEqual(observation['lower_bound_bytes'], 14601378857)
                self.assertEqual(resource['required_basis_bytes'], max(peak_bytes, observation['lower_bound_bytes']))
                self.assertEqual(observation['basis'], 'OBSERVED_CUDA_OOM_LOWER_BOUND_NOT_FULL_2_EPOCH_PEAK')

    def test_kev_weighted_worker_uses_module_and_legacy_entry_is_unchanged(self):
        write_rows(self.root / 'data/train.jsonl', [feature_row()])
        write_json(self.root / 'runs/parent/checkpoint/training_config.json', {'args': {'lora': 16}})
        write_json(self.root / dispatcher.DEFAULT_CANDIDATES[0]['checkpoint_path'] / 'training_metrics.json',
                   {'peak_device_bytes': 1048576})
        for weighted in (True, False):
            with self.subTest(weighted=weighted):
                cid = 'KEV-V8-WEIGHTED' if weighted else 'KEV-V8-LEGACY'
                candidate = {'candidate_id': cid, 'name': cid, 'status': 'QUEUED', 'training_status': 'UNKNOWN',
                    'init_from': 'runs/parent/checkpoint', 'data_path': 'data/train.jsonl',
                    'checkpoint_path': f'runs/{cid}/checkpoint', 'lr': '2e-5', 'lora': '16', 'epochs': '1'}
                if weighted:
                    candidate['question_loss_weights'] = {'model_choice': 2.0}
                process = Mock(pid=456, stdout=iter([]))
                process.wait.return_value = 1
                with patch.object(dispatcher, 'PROJECT_ROOT', self.root), \
                     patch.object(dispatcher, 'KEV_RUNS_ROOT', self.root / 'runs'), \
                     patch.object(dispatcher, 'load_queue', return_value=[candidate]), \
                     patch.object(dispatcher, 'save_queue'), patch.object(dispatcher, 'is_pid_alive', return_value=False), \
                     patch.object(dispatcher, 'scientific_selection'), \
                     patch.object(cont, 'plan_kev_continuation', return_value=None), \
                     patch.object(dispatcher.subprocess, 'run', return_value=types.SimpleNamespace(stdout='50000', returncode=0)), \
                     patch.object(dispatcher.subprocess, 'Popen', return_value=process) as launch:
                    self.assertEqual(dispatcher.main_loop(), 1)
                launch.assert_called_once()
                command = launch.call_args.args[0]
                self.assertEqual(command[:3], [str(self.root / '.venv/bin/python'), '-u', '-m'])
                if weighted:
                    self.assertEqual(command[3:7], ['modelrouter.training.kev_candidate_dispatcher',
                        '--train-candidate', cid, '--'])
                else:
                    self.assertEqual(command[3:5], ['kev.train', '--base'])
                self.assertEqual(launch.call_args.kwargs['cwd'], str(self.root))
                paths = [str(self.root), str(self.root / 'external/kev')]
                if weighted:
                    paths.append(str(self.root / 'our-project/code/src'))
                self.assertEqual(launch.call_args.kwargs['env']['PYTHONPATH'].split(dispatcher.os.pathsep), paths)

    def test_kev_completed_training_with_failed_val_retries_val_without_training(self):
        candidate = {'candidate_id': 'KEV-V9-001', 'status': 'FAILED', 'training_status': 'COMPLETED',
                     'checkpoint_path': 'runs/KEV-V9-001/checkpoint', 'v9_continuation': {'status': 'FAILED'}}
        with patch.object(dispatcher, 'PROJECT_ROOT', self.root), patch.object(dispatcher, 'load_queue', return_value=[candidate]), \
             patch.object(dispatcher, 'refresh_training', return_value=False), patch.object(dispatcher, 'save_queue'), \
             patch.object(dispatcher, 'validate_candidate', return_value=False) as validation, \
             patch.object(dispatcher.subprocess, 'Popen') as launch:
            self.assertEqual(dispatcher.main_loop(v9_only=True), 1)
        validation.assert_called_once_with(candidate, [candidate], 'auto', None)
        self.assertEqual(launch.call_count, 0)

    def test_v9_cli_reuses_original_resource_wait(self):
        with patch.object(dispatcher, 'main_loop', return_value=0) as loop:
            self.assertEqual(dispatcher.main(['--v9-continuation']), 0)
        self.assertTrue(loop.call_args.kwargs['wait_for_resources'])
        self.assertTrue(loop.call_args.kwargs['v9_only'])


if __name__ == "__main__":
    unittest.main()
