#!/usr/bin/env python3
"""
test_kev_candidates_dry_run.py - Validates that Kev candidate configs construct valid CLI commands.
"""

import json
import copy
from contextlib import ExitStack
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from modelrouter.training import kev_candidate_dispatcher as dispatcher

PROJECT_ROOT = Path("/home/syy/路由")


class TestKevCandidateConfigs(unittest.TestCase):
    def test_independent_pending_candidates_do_not_hide_following_failure(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            queue = [copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[2]), copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[4])]
            queue[1].update(status="FAILED", failure_reason="recorded failure")
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=queue))
            refreshed = []
            def refresh(candidate):
                refreshed.append(candidate["candidate_id"])
                candidate.setdefault("training_status", "QUEUED")
                return False
            stack.enter_context(patch.object(dispatcher, "refresh_training", side_effect=refresh))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            self.assertEqual(dispatcher.main_loop(), 1)
            self.assertEqual(refreshed, ["KEV-V8-C05", "KEV-V8-C09"])
            self.assertEqual(queue[0]["status"], "PENDING")
            self.assertEqual(queue[1]["failure_reason"], "recorded failure")
            train.assert_not_called()

    def test_v8_export_preserves_existing_project_split_and_typed_records(self):
        import gzip
        from router_data.build_v8_data_extension import export_kev_training
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data/kev/公开数据"
            data.mkdir(parents=True)
            record = {"state": "original task", "provenance": {"source_id": "ROUTE-004", "battle_id": "1"},
                "questions": {"model_choice": {"type": "choice", "criteria": {"a": "", "b": ""}, "label": "a"}},
                "expected": {"model_choice": "a"}}
            (data / "train.jsonl").write_text(json.dumps(record) + "\n")
            (data / "val.jsonl").write_text("")
            (root / "test.jsonl").write_text("must not read")
            view = {"battle_id": "1", "candidate_models": ["a", "b"], "winner_choice": "model_a", "winner_model": "a"}
            for split in ("train", "val"):
                with gzip.open(root / (split + ".gz"), "wt") as stream:
                    stream.write(json.dumps(view) + "\n")
            (root / "config.json").write_text(json.dumps({"data_views": {"router_choice": "train.gz"}, "validation_views": {"router_choice": "val.gz"}}))
            result = export_kev_training("config.json", root)
            self.assertEqual(result["splits"]["train"]["written_records"], 1)
            self.assertEqual(result["splits"]["val"]["excluded_project_split_mismatch"], 1)
            self.assertEqual(json.loads((root / "data/kev/v8_extension/train.jsonl").read_text()), record)
            self.assertEqual(result["new_train_records_vs_c03"], 0)
            self.assertEqual(result["configuration_status"], "PARTIAL_MATERIAL_NOT_FULL_C09")
            self.assertEqual((root / "test.jsonl").read_text(), "must not read")

    def test_load_queue_applies_existing_c09_config_only_before_start(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)), \
             patch.object(dispatcher, "QUEUE_FILE", Path(tmp) / "queue.json"):
            root = Path(tmp)
            config_path = root / "our-project/data/configs/training/KEV-V8-EXT-01.json"
            config_path.parent.mkdir(parents=True)
            source_config = Path(__file__).resolve().parents[3] / "data/configs/training/KEV-V8-EXT-01.json"
            config = json.loads(source_config.read_text(encoding="utf-8"))
            config_path.write_text(json.dumps(config))
            original = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES)
            original[-1]["checkpoint_path"] = original[-1]["pilot_checkpoint_path"]
            dispatcher.QUEUE_FILE.write_text(json.dumps(original))
            loaded = dispatcher.load_queue()
            self.assertEqual(loaded[:-1], original[:-1])
            candidate = loaded[-1]
            self.assertEqual(candidate["init_from"], config["init_from"])
            for name, value in config["training_knobs"].items():
                self.assertEqual(candidate["lora" if name == "lora_rank" else name], str(value))
            self.assertTrue(candidate["checkpoint_path"].endswith("formal_run"))
            self.assertTrue(candidate["pilot_checkpoint_path"].endswith("checkpoint"))
            self.assertEqual(candidate["configuration_source"], str(config_path))
            self.assertEqual(json.loads(dispatcher.QUEUE_FILE.read_text()), original)
            original[-1].update(status="RUNNING", started_at="fixture started", init_from="already-used-init")
            dispatcher.QUEUE_FILE.write_text(json.dumps(original))
            self.assertEqual(dispatcher.load_queue(), original)
            config_path.unlink()
            original[-1] = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[-1])
            dispatcher.QUEUE_FILE.write_text(json.dumps(original))
            self.assertEqual(dispatcher.load_queue()[-1]["init_from"], original[-1]["init_from"])

    def test_c04_lr_schedule(self):
        cand = {
            "candidate_id": "KEV-V8-C04",
            "lr": "1e-5",
            "lora": "16",
            "init_from": "runs/KEV-V8-HOMOLOGOUS-20261018/formal_run"
        }
        cmd = [
            "python", "-m", "kev.train",
            "--lr", cand["lr"],
            "--lora", cand["lora"],
            "--init_from", str(PROJECT_ROOT / cand["init_from"])
        ]
        self.assertIn("--lr", cmd)
        self.assertEqual(cmd[cmd.index("--lr") + 1], "1e-5")
        self.assertEqual(cmd[cmd.index("--lora") + 1], "16")

    def test_c05_state_ablation(self):
        cand = {
            "candidate_id": "KEV-V8-C05",
            "data_path": "data/kev/公开数据/train_nostate.jsonl"
        }
        cmd = ["python", "-m", "kev.train", "--data", str(PROJECT_ROOT / cand["data_path"])]
        self.assertIn("train_nostate.jsonl", cmd[cmd.index("--data") + 1])

    def test_c07_lora_rank_8(self):
        cand = {
            "candidate_id": "KEV-V8-C07",
            "lora": "8",
            "lr": "5e-5"
        }
        cmd = ["python", "-m", "kev.train", "--lora", cand["lora"], "--lr", cand["lr"]]
        self.assertEqual(cmd[cmd.index("--lora") + 1], "8")
        self.assertEqual(cmd[cmd.index("--lr") + 1], "5e-5")

    def test_c09_v8_extension(self):
        cand = dispatcher.DEFAULT_CANDIDATES[-1]
        self.assertTrue(cand["checkpoint_path"].endswith("formal_run"))
        self.assertTrue(cand["pilot_checkpoint_path"].endswith("checkpoint"))

    def test_all_formal_candidates_use_local_val_and_upstream_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            val = root / dispatcher.FIXED_VAL_PATH
            val.parent.mkdir(parents=True)
            val.write_text(json.dumps({
                "state": "fixture task", "provenance": {"split": "val"},
                "questions": {"choice": {"type": "choice", "instructions": "Choose",
                    "criteria": {"a": "", "b": ""}, "label": "a"}},
            }) + "\n", encoding="utf-8")
            report = {
                "clean": {"n": 1, "acc": 1.0, "nll": .2, "brier": .1, "ece": .15},
                "coverage": {"requested_records": 1, "evaluated_records": 1,
                             "rejected_records": 0, "truncated_records": 0},
                "data": str(val), "split": "custom",
            }

            def score(cmd, **kwargs):
                self.assertEqual(cmd[cmd.index("-m") + 1], "kev.benchmark")
                self.assertEqual(cmd[cmd.index("--data") + 1], str(val))
                self.assertNotIn("--allow-test", cmd)
                self.assertNotIn("--seed", cmd)
                self.assertEqual(kwargs["cwd"], str(root))
                self.assertEqual(kwargs["env"]["PYTHONPATH"], str(root / "external/kev"))
                kwargs["stdout"].write("evaluated 1/1\n")
                directory = Path(cmd[cmd.index("--out") + 1])
                directory.mkdir(parents=True)
                (directory / "report.json").write_text(json.dumps(report), encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, "evaluated 1/1", "")

            with patch.object(dispatcher, "PROJECT_ROOT", root), patch.object(dispatcher.subprocess, "run", side_effect=score) as process:
                for candidate in dispatcher.DEFAULT_CANDIDATES:
                    with self.subTest(candidate=candidate["candidate_id"]):
                        ckpt = root / candidate["checkpoint_path"]
                        output = ckpt / "val_metrics.json"
                        ok, metrics = dispatcher.run_fixed_validation(ckpt, output)
                        self.assertTrue(ok)
                        self.assertEqual(metrics["clean"], report["clean"])
                        self.assertEqual(metrics["report"], report)
                        self.assertEqual(metrics["evaluation_status"], "EVALUATED")
                        self.assertEqual(metrics["dataset_split"], "val")
                        self.assertFalse(metrics["test_used"])
                        self.assertEqual(metrics["exit_code"], 0)
                        self.assertGreaterEqual(metrics["duration_sec"], 0)
                        self.assertEqual(json.loads(output.read_text()), metrics)
                self.assertEqual(process.call_count, 5)

    def test_evaluation_failure_is_persisted_without_scores(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)):
            output = Path(tmp) / "formal_run/val_metrics.json"
            result = subprocess.CompletedProcess([], 1, "progress", "fixture evaluation error")
            def fail(cmd, **kwargs):
                kwargs["stdout"].write(result.stderr)
                return result
            with patch.object(dispatcher.subprocess, "run", side_effect=fail):
                ok, metrics = dispatcher.run_fixed_validation(output.parent, output)
            self.assertFalse(ok)
            self.assertEqual(metrics["evaluation_status"], "FAILED")
            self.assertEqual(metrics["exit_code"], 1)
            self.assertEqual(metrics["error"], result.stderr)
            self.assertNotIn("clean", metrics)
            self.assertEqual(json.loads(output.read_text()), metrics)

    def test_partial_coverage_remains_partial(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)):
            output = Path(tmp) / "formal_run/val_metrics.json"
            def score(cmd, **kwargs):
                report_dir = Path(cmd[cmd.index("--out") + 1])
                report_dir.mkdir(parents=True)
                (report_dir / "report.json").write_text(json.dumps({
                    "clean": {"n": 1, "acc": 1.0},
                    "coverage": {"requested_records": 2, "evaluated_records": 1, "rejected_records": 1},
                }))
                return subprocess.CompletedProcess(cmd, 0)
            with patch.object(dispatcher.subprocess, "run", side_effect=score):
                ok, metrics = dispatcher.run_fixed_validation(output.parent, output)
            self.assertFalse(ok)
            self.assertEqual(metrics["evaluation_status"], "PARTIAL")
            self.assertEqual(metrics["coverage"]["requested_records"], 2)

    def test_timeout_has_unknown_exit_code_and_no_scores(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)):
            output = Path(tmp) / "formal_run/val_metrics.json"
            with patch.object(dispatcher.subprocess, "run", side_effect=subprocess.TimeoutExpired("fixture", 900)):
                ok, metrics = dispatcher.run_fixed_validation(output.parent, output)
            self.assertFalse(ok)
            self.assertIsNone(metrics["exit_code"])
            self.assertNotIn("clean", metrics)
            self.assertEqual(json.loads(output.read_text()), metrics)

    def test_queue_keeps_completed_training_when_evaluation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = {**dispatcher.DEFAULT_CANDIDATES[0]}
            run = root / "runs" / candidate["name"]
            ckpt = root / candidate["checkpoint_path"]
            ckpt.mkdir(parents=True)
            (run / "cursor.json").write_text(json.dumps({"pid": 123, "status": "COMPLETED", "exit_code": 0}))
            training = {"optimizer_steps": 16857, "records_seen": 67428,
                        "requested_records": 67428, "wall_seconds": 138508.88}
            (ckpt / "training_metrics.json").write_text(json.dumps(training))
            queue_file = root / "candidate_queue.json"
            with patch.object(dispatcher, "PROJECT_ROOT", root), \
                 patch.object(dispatcher, "KEV_RUNS_ROOT", root / "runs"), \
                 patch.object(dispatcher, "QUEUE_FILE", queue_file), \
                 patch.object(dispatcher, "load_queue", return_value=[candidate]), \
                 patch.object(dispatcher, "is_pid_alive", return_value=False), \
                 patch.object(dispatcher, "check_checkpoint_integrity", return_value=(True, "fixture")), \
                 patch.object(dispatcher, "run_fixed_validation", return_value=(False, {
                     "evaluation_status": "FAILED", "exit_code": 1, "error": "fixture error"})), \
                 patch.object(dispatcher.subprocess, "Popen") as train:
                self.assertEqual(dispatcher.main_loop(), 1)
                train.assert_not_called()
            recorded = json.loads(queue_file.read_text())[0]
            self.assertEqual(recorded["training_status"], "COMPLETED")
            self.assertEqual(recorded["training_exit_code"], 0)
            self.assertEqual(recorded["training_metrics"], training)
            self.assertEqual(recorded["evaluation_status"], "FAILED")
            self.assertEqual(recorded["status"], "FAILED")
            self.assertEqual(recorded["metrics"]["exit_code"], 1)
            self.assertEqual(recorded["validation_set"], str(root / dispatcher.FIXED_VAL_PATH))

    def test_cpu_val_attempts_keep_old_report_and_stream_log(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)):
            output = Path(tmp) / "formal_run/val_metrics.json"
            output.parent.mkdir()
            old = {"evaluation_status": "FAILED", "error": "previous failure"}
            output.write_text(json.dumps(old))

            def score(cmd, **kwargs):
                self.assertEqual(cmd[cmd.index("--device") + 1], "cpu")
                self.assertEqual(kwargs["env"]["OMP_NUM_THREADS"], "8")
                self.assertEqual(kwargs["env"]["CUDA_VISIBLE_DEVICES"], "")
                self.assertIsNone(kwargs["timeout"])
                self.assertEqual(json.loads(output.read_text())["evaluation_status"], "EVALUATING")
                kwargs["stdout"].write("evaluated 50/8436\n")
                directory = Path(cmd[cmd.index("--out") + 1])
                self.assertFalse(directory.exists())
                directory.mkdir()
                (directory / "report.json").write_text(json.dumps({
                    "clean": {"n": 9330, "acc": .6}, "coverage": {
                        "requested_records": 8436, "evaluated_records": 8436,
                        "requested_questions": 9330, "evaluated_questions": 9330}}))
                return subprocess.CompletedProcess(cmd, 0)

            with patch.object(dispatcher.subprocess, "run", side_effect=score):
                for expected in (1, 2):
                    ok, metrics = dispatcher.run_fixed_validation(output.parent, output, device="cpu")
                    self.assertTrue(ok)
                    self.assertEqual(metrics["attempt_id"], expected)
                    self.assertEqual(Path(metrics["log_path"]).read_text(), "evaluated 50/8436\n")
            self.assertEqual(json.loads((output.with_suffix("") / "attempt_0000.json").read_text()), old)
            self.assertTrue((output.with_suffix("") / "attempt_0001/report.json").exists())

    def test_cli_validation_only_device_and_timeout(self):
        with patch.object(dispatcher, "main_loop", return_value=0) as loop:
            self.assertEqual(dispatcher.main(["--validation-only", "--validation-device", "cpu", "--validation-timeout", "18000"]), 0)
            loop.assert_called_once_with(True, "cpu", 18000.)

    def test_failed_c03_is_not_skipped_on_restart(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            queue = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[:2])
            queue[0].update(status="FAILED", failure_reason="Validation evaluation failed")
            stack.enter_context(patch.object(dispatcher, "PROJECT_ROOT", root))
            stack.enter_context(patch.object(dispatcher, "KEV_RUNS_ROOT", root / "runs"))
            stack.enter_context(patch.object(dispatcher, "QUEUE_FILE", root / "queue.json"))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=queue))
            val = stack.enter_context(patch.object(dispatcher, "run_fixed_validation"))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            self.assertEqual(dispatcher.main_loop(), 1)
            self.assertEqual(queue[1]["status"], "QUEUED")
            val.assert_not_called()
            train.assert_not_called()

    def test_validation_only_reuses_training_and_keeps_failure_history(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            queue = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[:2])
            queue[0].update(status="FAILED", failure_reason="original network error")
            ckpt = root / queue[0]["checkpoint_path"]
            ckpt.mkdir(parents=True)
            (ckpt / "training_metrics.json").write_text(json.dumps({"optimizer_steps": 16857, "records_seen": 67428}))
            (ckpt.parent / "cursor.json").write_text(json.dumps({"status": "COMPLETED", "exit_code": 0}))
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"),
                                ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=queue))
            metrics = {"evaluation_status": "EVALUATED", "validation_set": str(root / dispatcher.FIXED_VAL_PATH)}
            val = stack.enter_context(patch.object(dispatcher, "run_fixed_validation", return_value=(True, metrics)))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            self.assertEqual(dispatcher.main_loop(True, "cpu"), 0)
            val.assert_called_once_with(ckpt, ckpt / "val_metrics.json", device="cpu", timeout=None)
            train.assert_not_called()
            self.assertEqual(queue[1]["status"], "QUEUED")
            self.assertEqual(queue[0]["training_status"], "COMPLETED")
            self.assertEqual(queue[0]["evaluation_attempts"][0]["failure_reason"], "original network error")
            self.assertEqual(queue[0]["evaluation_attempts"][-1]["status"], "EVALUATED")
            self.assertNotIn("failure_reason", queue[0])

    def test_existing_successful_val_not_repeated(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            queue = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[:1])
            ckpt = root / queue[0]["checkpoint_path"]
            ckpt.mkdir(parents=True)
            (ckpt / "training_metrics.json").write_text('{"optimizer_steps":16857}')
            queue[0]["metrics"] = {"evaluation_status": "EVALUATED", "validation_set": str(root / dispatcher.FIXED_VAL_PATH)}
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=queue))
            val = stack.enter_context(patch.object(dispatcher, "run_fixed_validation"))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            self.assertEqual(dispatcher.main_loop(), 0)
            val.assert_not_called()
            train.assert_not_called()

    def test_missing_c05_and_c09_data_stay_pending(self):
        for index in (2, 4):
            with self.subTest(candidate=index), tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                root = Path(tmp)
                queue = [copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[index])]
                for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                    stack.enter_context(patch.object(dispatcher, name, value))
                stack.enter_context(patch.object(dispatcher, "load_queue", return_value=queue))
                train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
                self.assertEqual(dispatcher.main_loop(), 1)
                self.assertEqual(queue[0]["status"], "PENDING")
                self.assertIn("Missing training data", queue[0]["pending_reason"])
                self.assertFalse((root / queue[0]["data_path"]).exists())
                train.assert_not_called()

    def test_c07_rank_mismatch_does_not_launch(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[3])
            data = root / candidate["data_path"]
            data.parent.mkdir(parents=True)
            data.write_text('{}\n')
            init = root / candidate["init_from"]
            init.mkdir(parents=True)
            (init / "training_config.json").write_text('{"args":{"lora":16}}')
            (init / "adapter_config.json").write_text('{"r":8}')
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=[candidate]))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            self.assertEqual(dispatcher.main_loop(), 1)
            self.assertEqual(candidate["configuration_status"], "INCOMPATIBLE")
            self.assertIn("source rank 16, requested rank 8", candidate["pending_reason"])
            self.assertEqual(candidate["init_lora_source"], str(init / "training_config.json"))
            train.assert_not_called()
            (init / "training_config.json").unlink()
            (init / "adapter_config.json").write_text('{"r":16}')
            self.assertEqual(dispatcher.main_loop(), 1)
            self.assertEqual(candidate["init_lora_source"], str(init / "adapter_config.json"))
            train.assert_not_called()

    def test_c09_pilot_preserved_real_progress_and_training_exit_recorded(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[-1])
            data = root / candidate["data_path"]
            data.parent.mkdir(parents=True)
            data.write_text('{}\n')
            (root / candidate["init_from"]).mkdir(parents=True)
            peak_file = root / dispatcher.DEFAULT_CANDIDATES[0]["checkpoint_path"] / "training_metrics.json"
            peak_file.parent.mkdir(parents=True)
            peak_file.write_text('{"peak_device_bytes":10542966784}')
            pilot = root / candidate["pilot_checkpoint_path"] / "head.pt"
            pilot.parent.mkdir(parents=True)
            pilot.write_bytes(b'original pilot fixture')
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=[candidate]))
            stack.enter_context(patch.object(dispatcher, "is_pid_alive", return_value=False))
            def training_lines():
                output = root / candidate["checkpoint_path"]
                self.assertFalse(output.exists())
                output.mkdir(parents=True)
                yield "ep0 step 10/20 loss 9.45e-1\n"
                yield "training error\n"
            proc = Mock(pid=789, stdout=training_lines())
            proc.wait.return_value = 7
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen", return_value=proc))
            stack.enter_context(patch.object(dispatcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "16000\n")))
            self.assertEqual(dispatcher.main_loop(), 1)
            cmd = train.call_args.args[0]
            self.assertEqual(cmd[cmd.index("--out") + 1], str(root / candidate["checkpoint_path"]))
            self.assertEqual(pilot.read_bytes(), b'original pilot fixture')
            self.assertEqual(candidate["training_kind"], "FORMAL_LORA")
            self.assertEqual(candidate["step"], 10)
            self.assertEqual(candidate["loss"], .945)
            self.assertEqual(candidate["loss_step"], 10)
            self.assertEqual(candidate["training_exit_code"], 7)
            self.assertEqual(candidate["training_attempts"][0]["exit_code"], 7)
            self.assertGreaterEqual(candidate["training_attempts"][0]["duration_sec"], 0)

    def test_final_steps_do_not_relabel_last_logged_loss(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)), \
             patch.object(dispatcher, "KEV_RUNS_ROOT", Path(tmp) / "runs"):
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[0])
            ckpt = Path(tmp) / candidate["checkpoint_path"]
            ckpt.mkdir(parents=True)
            (ckpt / "training_metrics.json").write_text('{"optimizer_steps":16857,"records_seen":67428}')
            (ckpt.parent / "cursor.json").write_text('{"status":"COMPLETED","exit_code":0}')
            (ckpt.parent / "train.log").write_text('ep0 step 16850/16857 loss 0.945\n')
            dispatcher.refresh_training(candidate)
            self.assertEqual(candidate["step"], 16857)
            self.assertEqual(candidate["loss_step"], 16850)
            self.assertEqual(candidate["loss"], .945)

    def test_saved_successful_val_reused_when_plan_not_updated(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)), \
             patch.object(dispatcher, "QUEUE_FILE", Path(tmp) / "queue.json"):
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[0])
            candidate.update(status="FAILED", failure_reason="old failure", evaluation_attempts=[{"failure_reason": "old failure"}])
            ckpt = Path(tmp) / candidate["checkpoint_path"]
            ckpt.mkdir(parents=True)
            metrics = {"evaluation_status": "EVALUATED", "validation_set": str(Path(tmp) / dispatcher.FIXED_VAL_PATH)}
            (ckpt / "val_metrics.json").write_text(json.dumps(metrics))
            with patch.object(dispatcher, "run_fixed_validation") as val:
                self.assertTrue(dispatcher.validate_candidate(candidate, [candidate], "cpu"))
                val.assert_not_called()
            self.assertEqual(candidate["metrics"], metrics)
            self.assertEqual(candidate["evaluation_attempts"][0]["failure_reason"], "old failure")
            self.assertEqual(candidate["evaluation_attempts"][-1]["failure_reason"], "old failure")
            self.assertNotIn("failure_reason", candidate)

    def test_c09_old_pilot_cursor_is_not_formal_training(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)), \
             patch.object(dispatcher, "KEV_RUNS_ROOT", Path(tmp) / "runs"):
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[-1])
            run_dir = Path(tmp) / "runs" / candidate["name"]
            run_dir.mkdir(parents=True)
            (run_dir / "cursor.json").write_text('{"status":"COMPLETED","exit_code":0,"step":50}')
            dispatcher.refresh_training(candidate)
            self.assertEqual(candidate["training_status"], "UNKNOWN")
            self.assertIsNone(candidate["training_exit_code"])
            self.assertEqual(json.loads((run_dir / "cursor.json").read_text())["step"], 50)

    def test_low_gpu_free_returns_waiting_without_training(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[1])
            init = root / candidate["init_from"]
            init.mkdir(parents=True)
            (init / "training_metrics.json").write_text('{"peak_device_bytes":10542966784}')
            (init / "adapter_config.json").write_text('{"r":16}')
            data = root / candidate["data_path"]
            data.parent.mkdir(parents=True)
            data.write_text('{}\n')
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=[candidate]))
            gpu = stack.enter_context(patch.object(dispatcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "666\n")))
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen"))
            sleep = stack.enter_context(patch.object(dispatcher.time, "sleep"))
            self.assertEqual(dispatcher.main_loop(), 1)
            self.assertEqual(candidate["status"], "WAITING_FOR_GPU")
            self.assertEqual(candidate["gpu_resource"]["required_mib"], 12103)
            self.assertEqual(candidate["gpu_resource"]["free_mib"], 666)
            self.assertEqual(candidate["gpu_resource"]["peak_device_bytes"], 10542966784)
            gpu.assert_called_once_with(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits", "--id=0"],
                                       capture_output=True, text=True, check=True)
            train.assert_not_called()
            sleep.assert_not_called()

    def test_c03_comparison_new_and_reused_val(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(dispatcher, "PROJECT_ROOT", Path(tmp)), \
             patch.object(dispatcher, "QUEUE_FILE", Path(tmp) / "queue.json"):
            root = Path(tmp)
            metrics = {"evaluation_status": "EVALUATED", "validation_protocol": "KEV_FIXED_VAL_JSONL",
                       "validation_set": str(root / dispatcher.FIXED_VAL_PATH),
                       "coverage": {"requested_records": 8436, "evaluated_records": 8436,
                                    "requested_questions": 9330, "evaluated_questions": 9330,
                                    "rejected_records": 0, "truncated_records": 0},
                       "clean": {"n": 9330, "acc": .6, "nll": .8, "brier": .3, "ece": .1}}
            reference = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[0])
            reference["metrics"] = copy.deepcopy(metrics)
            dispatcher.record_c03_comparison(reference, [reference])
            self.assertEqual(reference["comparison_to_c03"]["status"], "REFERENCE")
            self.assertTrue(all(v is None for v in reference["comparison_to_c03"]["deltas"].values()))
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[1])
            result = copy.deepcopy(metrics)
            result["clean"].update(acc=.65, nll=.7, brier=.25, ece=.08)
            queue = [reference, candidate]
            with patch.object(dispatcher, "run_fixed_validation", return_value=(True, result)):
                self.assertTrue(dispatcher.validate_candidate(candidate, queue))
            for key, expected in {"acc": .05, "nll": -.1, "brier": -.05, "ece": -.02}.items():
                self.assertAlmostEqual(candidate["comparison_to_c03"]["deltas"][key], expected)
            ckpt = root / candidate["checkpoint_path"]
            ckpt.mkdir(parents=True)
            (ckpt / "val_metrics.json").write_text(json.dumps(result))
            candidate.pop("comparison_to_c03")
            with patch.object(dispatcher, "run_fixed_validation") as val:
                self.assertTrue(dispatcher.validate_candidate(candidate, queue))
                val.assert_not_called()
            saved = json.loads((root / "queue.json").read_text())[1]
            self.assertEqual(saved["comparison_to_c03"]["status"], "COMPARABLE")
            self.assertEqual(saved["comparison_to_c03"], candidate["comparison_to_c03"])

    def test_c03_comparison_incompatible_results_have_null_deltas(self):
        metrics = {"evaluation_status": "EVALUATED", "validation_protocol": "KEV_FIXED_VAL_JSONL",
                   "validation_set": "project/val.jsonl", "clean": {"n": 9330, "acc": .6, "nll": .8, "brier": .3, "ece": .1},
                   "coverage": {"requested_records": 8436, "evaluated_records": 8436,
                                "requested_questions": 9330, "evaluated_questions": 9330}}
        changes = [{"validation_protocol": "IMPORTED_PUBLIC_TEST"}, {"validation_set": "other/val.jsonl"},
                   {"coverage": {"requested_records": 1264, "evaluated_records": 1264,
                                 "requested_questions": 1264, "evaluated_questions": 1264}},
                   {"coverage": {}}, {"evaluation_status": "PARTIAL"},
                   {"clean": {"n": 1264, "acc": .8726}}, {"validation_protocol": None}]
        for change in changes:
            with self.subTest(change=change):
                reference = {"candidate_id": "KEV-V8-C03", "metrics": {**copy.deepcopy(metrics), **change}}
                candidate = {"candidate_id": "KEV-V8-C04", "metrics": copy.deepcopy(metrics)}
                dispatcher.record_c03_comparison(candidate, [reference, candidate])
                self.assertEqual(candidate["comparison_to_c03"]["status"], "NOT_EVALUATED")
                self.assertTrue(all(v is None for v in candidate["comparison_to_c03"]["deltas"].values()))
        candidate = {"candidate_id": "KEV-V8-C04", "metrics": metrics}
        dispatcher.record_c03_comparison(candidate, [{"candidate_id": "KEV-V8-C02", "metrics": metrics}, candidate])
        self.assertEqual(candidate["comparison_to_c03"]["status"], "NOT_EVALUATED")

    def test_c04_inherits_c03_training_parameters(self):
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
            root = Path(tmp)
            candidate = copy.deepcopy(dispatcher.DEFAULT_CANDIDATES[1])
            init = root / candidate["init_from"]
            init.mkdir(parents=True)
            (init / "training_metrics.json").write_text('{"peak_device_bytes":10542966784}')
            data = root / candidate["data_path"]
            data.parent.mkdir(parents=True)
            data.write_text('{}\n')
            parameters = {"base": str(root / "models/qwen3.5-4b-base"), "data": str(data),
                          "lora": 16, "lr": 2e-5, "dtype": "bf16", "weights_dtype": "bf16",
                          "max_state": 384, "batch": 1, "accum": 4, "checkpointing": 1,
                          "epochs": 1, "seed": 42, "option_isolation": 0, "special_embeddings": 0,
                          "head_dim": 256, "device": "cuda", "shared_prefix": 0,
                          "init_from": "original-adapter", "out": str(init), "suite": None}
            (init / "training_config.json").write_text(json.dumps({"args": parameters}))
            for name, value in (("PROJECT_ROOT", root), ("KEV_RUNS_ROOT", root / "runs"), ("QUEUE_FILE", root / "queue.json")):
                stack.enter_context(patch.object(dispatcher, name, value))
            stack.enter_context(patch.object(dispatcher, "load_queue", return_value=[candidate]))
            stack.enter_context(patch.object(dispatcher, "is_pid_alive", return_value=False))
            stack.enter_context(patch.object(dispatcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "38851\n")))
            proc = Mock(pid=987, stdout=iter([]))
            proc.wait.return_value = 7
            train = stack.enter_context(patch.object(dispatcher.subprocess, "Popen", return_value=proc))
            self.assertEqual(dispatcher.main_loop(), 1)
            cmd = train.call_args.args[0]
            for name, value in parameters.items():
                if name not in ("lr", "init_from", "out", "suite"):
                    self.assertEqual(cmd[cmd.index(f"--{name}") + 1], str(value))
            self.assertEqual(float(cmd[cmd.index("--lr") + 1]), 1e-5)
            self.assertEqual(cmd[cmd.index("--init_from") + 1], str(init))
            self.assertEqual(cmd[cmd.index("--out") + 1], str(root / candidate["checkpoint_path"]))
            self.assertNotIn("--suite", cmd)
            self.assertEqual(candidate["training_parameters_source"], str(init / "training_config.json"))
            self.assertEqual(candidate["training_parameters"]["max_state"], 384)
            self.assertEqual(json.loads((init / "training_config.json").read_text())["args"], parameters)


if __name__ == "__main__":
    unittest.main()
