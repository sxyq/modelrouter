"""Offline contract tests for CLI; no Docker, model API or Harbor trial is invoked."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from modelrouter.benchmark import __main__ as cli


class TestBenchmarkCLI(unittest.TestCase):
    def test_preflight_is_blocked_without_harbor_or_docker(self):
        with patch.object(cli.shutil, "which", return_value=None):
            result = cli.preflight("docker")
            self.assertEqual(result["status"], "BLOCKED_OR_UNVERIFIED")
            self.assertEqual(result["official_trials"], 0)

    def test_progress_missing_job_returns_no_fake_score(self):
        with tempfile.TemporaryDirectory() as d:
            result = cli.progress(Path(d))
            self.assertEqual(result["verified_trials"], 0)
            self.assertIsNone(result["verified_reward_mean"])
            self.assertEqual(result["status"], "NOT_EVALUATED")

    def test_watch_once_produces_machine_readable_status(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "progress.json"
            exit_code = cli.main(["watch", str(Path(d) / "missing"), "--once", "--output", str(out)])
            self.assertEqual(exit_code, 2)
            report = json.loads(out.read_text())
            self.assertEqual(report["verified_trials"], 0)

    def test_cli_does_not_interpret_unverified_results_as_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(cli.main(["audit", d]), 2)


    def test_harbor_command_uses_single_task_and_original_dataset(self):
        cmd = cli.build_harbor_command("fix-git", "mini-swe-agent", "openai/verified")
        self.assertEqual(cmd[:4], ["harbor", "run", "-d", "terminal-bench/terminal-bench-2-1"])
        self.assertEqual(cmd[cmd.index("--include-task-name") + 1], "fix-git")
        self.assertIn("mini-swe-agent", cmd)
        self.assertIn("openai/verified", cmd)

    def test_subset_manifest_validates_frozen_task_ids(self):
        self.assertTrue(cli._task_in_subset("fix-git", "canary"))
        self.assertFalse(cli._task_in_subset("invented-task-123", "canary"))
        self.assertTrue(cli._task_in_subset("bn-fit-modify", "dev"))
        self.assertTrue(cli._task_in_subset("chess-best-move", "sealed"))

    def test_run_defaults_to_dry_run_and_never_calls_harbor(self):
        with patch.object(cli.subprocess, "call", side_effect=AssertionError("no live run")):
            code = cli.main(["run", "--task", "fix-git", "--agent", "oracle"])
            self.assertEqual(code, 0)

    def test_sealed_run_fails_without_explicit_permission(self):
        self.assertEqual(
            cli.main(["run", "--task", "chess-best-move", "--subset", "sealed"]),
            2,
        )


if __name__ == "__main__":
    unittest.main()
