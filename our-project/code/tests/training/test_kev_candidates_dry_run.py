#!/usr/bin/env python3
"""
test_kev_candidates_dry_run.py - Validates that Kev candidate configs construct valid CLI commands.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from modelrouter.training import kev_candidate_dispatcher as dispatcher

PROJECT_ROOT = Path("/home/syy/路由")


class TestKevCandidateConfigs(unittest.TestCase):
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
        cand = {
            "candidate_id": "KEV-V8-C09",
            "out": "runs/KEV-V8-EXT-01/checkpoint"
        }
        self.assertTrue(cand["out"].endswith("checkpoint"))

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
            with patch.object(dispatcher.subprocess, "run", return_value=result):
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
            report_dir = output.with_suffix("")
            report_dir.mkdir(parents=True)
            (report_dir / "report.json").write_text(json.dumps({
                "clean": {"n": 1, "acc": 1.0},
                "coverage": {"requested_records": 2, "evaluated_records": 1, "rejected_records": 1},
            }))
            with patch.object(dispatcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
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
                with self.assertRaises(SystemExit):
                    dispatcher.main_loop()
                train.assert_not_called()
            recorded = json.loads(queue_file.read_text())[0]
            self.assertEqual(recorded["training_status"], "COMPLETED")
            self.assertEqual(recorded["training_exit_code"], 0)
            self.assertEqual(recorded["training_metrics"], training)
            self.assertEqual(recorded["evaluation_status"], "FAILED")
            self.assertEqual(recorded["status"], "FAILED")
            self.assertEqual(recorded["metrics"]["exit_code"], 1)
            self.assertEqual(recorded["validation_set"], str(root / dispatcher.FIXED_VAL_PATH))


if __name__ == "__main__":
    unittest.main()
