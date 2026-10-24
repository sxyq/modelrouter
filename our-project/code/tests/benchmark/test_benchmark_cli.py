"""Offline contract tests for CLI; no Docker, model API or Harbor trial is invoked."""
import json
import io
import os
import socket
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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

    def test_explicit_dry_run_never_calls_harbor(self):
        with patch.object(cli.iterations, "latest", return_value=None), \
             patch.object(cli.subprocess, "call", side_effect=AssertionError("no live run")):
            code = cli.main(["run", "--task", "fix-git", "--agent", "oracle", "--dry-run"])
            self.assertEqual(code, 0)

    def test_pipeline_preserves_requested_official_order(self):
        manifest = {"subsets": {"canary": {"tasks": [{"task_id": "fix-git"}]}}}
        units = cli.execution_units([{"task_id": "dev-task"}], ["fixed_strong", "random"], "modelrouter", 42, manifest, "dev")
        self.assertEqual([u["pipeline_stage"] for u in units], ["ORACLE_SINGLE", "NATIVE_SINGLE", "ROUTED_SINGLE", "CANARY", "DEV", "DEV"])
        self.assertEqual(len({u["job_name"] for u in units}), len(units))

    def test_explicit_upstream_task_path_is_used_when_supplied(self):
        command = cli.build_harbor_command("fix-git", task_source="/installed/upstream/tasks")
        self.assertEqual(command[:4], ["harbor", "run", "-p", "/installed/upstream/tasks/fix-git"])
        self.assertNotIn("-d", command)

    def test_sealed_run_fails_without_explicit_permission(self):
        self.assertEqual(
            cli.main(["run", "--task", "chess-best-move", "--subset", "sealed"]),
            2,
        )

    def test_run_is_real_by_default(self):
        with tempfile.TemporaryDirectory() as d, \
             patch.object(cli.iterations, "latest", return_value=None), \
             patch.object(cli, "run_iteration", return_value=2) as run:
            self.assertEqual(cli.main(["run", "--task", "fix-git", "--agent", "oracle", "--iteration-dir", d]), 2)
            run.assert_called_once()
            self.assertTrue((Path(d) / "run_config.json").exists())

    def test_resume_skips_original_scored_trials(self):
        from modelrouter.benchmark import iterations
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "iteration"
            iterations.start(p, {"units": [{"status": "EVALUATED", "job_name": "original"}]})
            with patch.object(iterations, "execute", side_effect=AssertionError("must not rerun")), patch.object(iterations, "publish", return_value={}):
                self.assertEqual(cli.run_iteration(p, resume=True), 0)

    def test_same_docker_error_does_not_launch_another_job(self):
        from modelrouter.benchmark import iterations
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            iterations.start(p, {"environment": "docker", "units": [{"status": "NOT_EVALUATED", "job_name": "original"}]})
            with patch.object(iterations, "publish", return_value={}):
                iterations.finish(p, "BLOCKED", "Docker is not installed or not on PATH")
            with patch.object(cli, "_probe", return_value={"status": "MISSING"}), patch.object(iterations, "execute", side_effect=AssertionError("no duplicate attempt")):
                self.assertEqual(cli.run_iteration(p, resume=True), 2)
            self.assertEqual(json.loads((p / "resume_state.json").read_text())["status"], "BLOCKED")

    def test_available_docker_resolves_recorded_docker_problem(self):
        with patch.object(cli, "_probe", return_value={"status": "READY"}):
            outcome = cli.resolve_previous_failure({"status": "BLOCKED", "reason": "Docker socket permission denied"}, "docker")
            self.assertEqual(outcome["status"], "RESOLVED")

    def test_native_miniswe_relay_and_options_use_real_harbor_parser(self):
        from modelrouter.benchmark import iterations
        from contextlib import contextmanager
        @contextmanager
        def relay(path):
            yield {"port": 23456, "api_key": "ephemeral-fixture-only"}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            iterations.start(p, {"units": [{"task_id": "fix-git", "policy": "mini-swe-agent", "agent": "mini-swe-agent", "job_name": "native", "status": "PENDING"}],
                                 "model": "openai/gpt-6-luna", "environment": "docker", "seed": 42,
                                 "max_steps": 30, "max_output_tokens": 2048})
            def parse(path, cmd, env, **kwargs):
                assert "ephemeral-fixture-only" not in " ".join(cmd)
                assert env["MODELROUTER_NATIVE_RELAY_KEY"] == "ephemeral-fixture-only"
                result = cli.subprocess.run([str(Path(sys.executable).parent / "harbor"), *cmd[1:], "--print-config"],
                                            env=env, text=True, capture_output=True)
                assert result.returncode == 0, result.stderr
                config = json.loads(result.stdout)
                native = config["agents"][0]
                assert native["model_api_key_name"] == "MODELROUTER_NATIVE_RELAY_KEY"
                assert native["kwargs"]["config"]["agent"]["step_limit"] == 30
                assert native["kwargs"]["reasoning_effort"] == "low"
                assert native["kwargs"]["litellm_model_registry"]["openai/gpt-6-luna"]["output_cost_per_token"] == 8 / 1e6
                return 0
            with patch("modelrouter.providers.provider.native_generator_relay", relay), patch.object(iterations, "execute", side_effect=parse), patch.object(iterations, "publish", return_value={}):
                assert cli.run_iteration(p) == 2  # Parser evidence is not an evaluated task.

    def test_summarize_and_export_without_trials_leave_no_science_scores(self):
        from modelrouter.benchmark import iterations
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "iteration"
            iterations.start(p, {"units": []})
            self.assertEqual(cli.main(["summarize", str(p)]), 0)
            self.assertEqual(cli.main(["export", str(p)]), 0)
            output = json.loads((p / "analysis/official_results.json").read_text())
            self.assertEqual(output["status"], "NOT_EVALUATED")
            self.assertEqual(output["table3"], [])


class TestDockerRuntime(unittest.TestCase):
    def test_probe_passes_selected_host_without_mutating_shell(self):
        with tempfile.TemporaryDirectory() as d, socket.socket(socket.AF_UNIX) as sock:
            endpoint = "unix://" + str(Path(d) / "docker.sock")
            sock.bind(endpoint.removeprefix("unix://"))
            with patch.dict(os.environ, {"DOCKER_HOST": "unix:///original.sock"}), \
                 patch.object(cli.shutil, "which", return_value="/fixture/docker"), \
                 patch.object(cli.subprocess, "run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = "fixture rootless daemon"
                result = cli._probe(["docker", "info"], env=cli._runtime_env(endpoint))
                self.assertEqual(result["status"], "READY")
                self.assertEqual(run.call_args.kwargs["env"]["DOCKER_HOST"], endpoint)
                self.assertEqual(os.environ["DOCKER_HOST"], "unix:///original.sock")

    def test_missing_socket_remains_blocked_without_docker_request(self):
        with tempfile.TemporaryDirectory() as d, \
             patch.object(cli.subprocess, "run", side_effect=AssertionError("no Docker request")):
            result = cli._probe(["docker", "info"], env=cli._runtime_env("unix://" + d + "/absent.sock"))
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIn("socket missing", result["reason"])

    def test_preflight_uses_runtime_host_and_explicit_override(self):
        for override, expected in ((None, "ssh://fixture-user@fixture"), ("ssh://override", "ssh://override")):
            with self.subTest(override=override), \
                 patch.object(cli, "_runtime_config", return_value={"docker_host": "ssh://fixture-user@fixture"}), \
                 patch.object(cli, "_probe", return_value={"status": "BLOCKED", "reason": "fixture; no daemon"}) as probe:
                result = cli.preflight("docker", override)
                self.assertEqual(result["docker_host"], expected)
                self.assertEqual(result["status"], "BLOCKED_OR_UNVERIFIED")
                self.assertEqual(result["official_trials"], 0)
                self.assertEqual([c.kwargs["env"]["DOCKER_HOST"] for c in probe.call_args_list], [expected, expected])

    def test_preflight_cli_host_argument(self):
        with patch.object(cli, "preflight", return_value={"status": "BLOCKED_OR_UNVERIFIED"}) as preflight, redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["preflight", "--docker-host", "ssh://fixture"]), 2)
            preflight.assert_called_once_with("docker", "ssh://fixture")

    def test_run_cli_host_override_is_recorded_and_assessed(self):
        with tempfile.TemporaryDirectory() as d:
            previous = Path(d) / "previous"
            previous.mkdir()
            (previous / "next_iteration.json").write_text(json.dumps({"status": "BLOCKED", "reason": "Docker absent"}))
            with patch.object(cli, "_runtime_config", return_value={"docker_host": "ssh://configured"}), \
                 patch.object(cli.iterations, "latest", return_value=previous), \
                 patch.object(cli, "resolve_previous_failure", return_value={"status": "UNRESOLVED"}) as assess, \
                 patch.object(cli, "run_iteration", side_effect=AssertionError("dry plan only")), redirect_stdout(io.StringIO()) as output:
                code = cli.main(["run", "--task", "fix-git", "--agent", "oracle", "--dry-run", "--docker-host", "ssh://override"])
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(output.getvalue())["docker_host"], "ssh://override")
                self.assertEqual(assess.call_args.args[2], "ssh://override")

    def _saved_run(self, path, **config):
        unit = {"task_id": "fix-git", "policy": "oracle", "agent": "oracle", "job_name": "original", "status": "NOT_EVALUATED"}
        (path / "run_config.json").write_text(json.dumps({"environment": "docker", **config}))
        (path / "resume_state.json").write_text(json.dumps({"status": "BLOCKED", "units": [unit]}))
        (path / "next_iteration.json").write_text(json.dumps({"status": "BLOCKED", "reason": "Parser dependency was missing", "pending_units": [unit]}))

    def test_resolved_resume_uses_saved_host_or_override_on_original_job(self):
        for override, expected in ((None, "ssh://saved"), ("ssh://override", "ssh://override")):
            with self.subTest(override=override), tempfile.TemporaryDirectory() as d:
                path = Path(d)
                report = {"status": "RESOLVED", "problem": "Parser dependency was missing", "evidence": "Installed dependency; import succeeded"}
                self._saved_run(path, docker_host="ssh://saved", reported_resolution=report)
                job = path / "jobs/original"
                job.mkdir(parents=True)
                (job / "config.json").write_text("{}")
                with patch.object(cli, "_runtime_config", return_value={"docker_host": "ssh://configured"}), \
                     patch.object(cli.iterations, "event"), patch.object(cli.iterations, "finish"), \
                     patch.object(cli, "audit_job", return_value={"status": "NOT_EVALUATED"}), \
                     patch.object(cli.iterations, "execute", return_value=0) as execute, \
                     patch.dict(os.environ, {"DOCKER_HOST": "ssh://shell"}):
                    self.assertEqual(cli.run_iteration(path, resume=True, docker_host=override), 2)
                    self.assertEqual(execute.call_args.args[1], ["harbor", "jobs", "resume", "--job-path", str(job)])
                    self.assertEqual(execute.call_args.kwargs["env"]["DOCKER_HOST"], expected)
                    self.assertEqual(os.environ["DOCKER_HOST"], "ssh://shell")
                    self.assertEqual(json.loads((path / "run_config.json").read_text())["docker_host"], "ssh://saved")

    def test_run_missing_socket_does_not_start_job(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            self._saved_run(path, docker_host="unix://" + d + "/missing.sock")
            with patch.object(cli, "_runtime_config", return_value={}), \
                 patch.object(cli.iterations, "event"), patch.object(cli.iterations, "finish") as finish, \
                 patch.object(cli, "audit_job", return_value={"status": "NOT_EVALUATED"}), \
                 patch.object(cli.iterations, "execute", side_effect=AssertionError("no Docker request")):
                self.assertEqual(cli.run_iteration(path), 2)
                self.assertEqual(finish.call_args.args[1], "BLOCKED")
                self.assertIn("socket missing", finish.call_args.args[2])

    def test_new_run_uses_runtime_host_when_saved_config_has_no_endpoint(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            self._saved_run(path)
            with patch.object(cli, "_runtime_config", return_value={"docker_host": "ssh://configured"}), \
                 patch.object(cli.iterations, "event"), patch.object(cli.iterations, "finish"), \
                 patch.object(cli, "audit_job", return_value={"status": "NOT_EVALUATED"}), \
                 patch.object(cli.iterations, "execute", return_value=0) as execute:
                self.assertEqual(cli.run_iteration(path), 2)
                self.assertEqual(execute.call_args.kwargs["env"]["DOCKER_HOST"], "ssh://configured")
                self.assertEqual(execute.call_args.args[1][:2], ["harbor", "run"])
                command = execute.call_args.args[1]
                self.assertEqual(command[command.index("-p") + 1],
                                 str(cli.iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks/fix-git"))
                self.assertNotIn("-d", command)

    def test_unknown_error_resume_uses_runtime_report_without_repeating_failure(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            self._saved_run(path)
            with patch.object(cli, "_runtime_config", return_value={}), \
                 patch.object(cli.iterations, "event"), redirect_stdout(io.StringIO()), \
                 patch.object(cli.iterations, "execute", side_effect=AssertionError("unresolved error must not repeat")):
                self.assertEqual(cli.run_iteration(path, resume=True), 2)
            report = {"status": "RESOLVED", "problem": "Parser dependency was missing", "evidence": "Existing environment import now succeeds"}
            with patch.object(cli, "_runtime_config", return_value={"docker_host": "ssh://configured", "reported_resolution": report}), \
                 patch.object(cli.iterations, "event"), patch.object(cli.iterations, "finish"), \
                 patch.object(cli, "audit_job", return_value={"status": "NOT_EVALUATED"}), \
                 patch.object(cli.iterations, "execute", return_value=0) as execute:
                self.assertEqual(cli.run_iteration(path, resume=True), 2)
                execute.assert_called_once()

    def test_unknown_error_requires_matching_resolution_evidence(self):
        plan = {"status": "BLOCKED", "reason": "Provider quota 402", "pending_units": []}
        for report in (None, {"status": "RESOLVED", "problem": "Other error", "evidence": "fixed"},
                       {"status": "RESOLVED", "problem": plan["reason"]}):
            with self.subTest(report=report):
                self.assertEqual(cli.resolve_previous_failure(plan, "docker", reported_resolution=report)["status"], "UNRESOLVED")
        report = {"status": "RESOLVED", "problem": plan["reason"], "evidence": "Existing account quota restored; original budget unchanged"}
        self.assertEqual(cli.resolve_previous_failure(plan, "docker", reported_resolution=report)["status"], "RESOLVED")
        self.assertEqual(cli.resolve_previous_failure({**plan, "reported_resolution": report}, "docker")["status"], "RESOLVED")

    def test_rootless_error_cannot_be_cleared_by_report_when_socket_missing(self):
        with tempfile.TemporaryDirectory() as d, patch.object(cli.subprocess, "run", side_effect=AssertionError("no Docker request")):
            plan = {"status": "BLOCKED", "reason": "newuidmap absent; uid_map EPERM"}
            report = {"status": "RESOLVED", "problem": plan["reason"], "evidence": "fixture report"}
            outcome = cli.resolve_previous_failure(plan, "docker", "unix://" + d + "/missing.sock", report)
            self.assertEqual(outcome["status"], "UNRESOLVED")
            self.assertEqual(outcome["sandbox"]["status"], "BLOCKED")

    def test_resume_cli_override_keeps_saved_endpoint(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            self._saved_run(path, docker_host="ssh://saved")
            with patch.object(cli.iterations, "event"), patch.object(cli, "run_iteration", return_value=2) as run:
                self.assertEqual(cli.main(["resume", d, "--docker-host", "ssh://override"]), 2)
                run.assert_called_once_with(path, resume=True, docker_host="ssh://override")
                self.assertEqual(json.loads((path / "run_config.json").read_text())["docker_host"], "ssh://saved")


if __name__ == "__main__":
    unittest.main()
