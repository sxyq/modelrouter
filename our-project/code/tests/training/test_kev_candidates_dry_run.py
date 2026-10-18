#!/usr/bin/env python3
"""
test_kev_candidates_dry_run.py - Validates that Kev candidate configs construct valid CLI commands.
"""

import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
