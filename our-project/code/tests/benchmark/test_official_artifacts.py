"""CPU-only tests; every test uses temporary synthetic fixtures, never claims official scores."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from modelrouter.benchmark.official_artifacts import audit_trial, audit_job, main


def create_trial(root, *, reward=0.0, result_reward=0.0, with_lock=True):
    root.mkdir(parents=True, exist_ok=True)
    (root / "config.json").write_text('{"agent":{"name":"oracle"}}')
    (root / "result.json").write_text(json.dumps({
        "verifier_result": {"rewards": {"reward": result_reward}},
        "exception_info": None,
    }))
    if with_lock:
        (root / "lock.json").write_text('{"locked":true}')
    (root / "verifier").mkdir(exist_ok=True)
    (root / "verifier" / "reward.txt").write_text(str(reward))
    return root


class TestOfficialArtifacts(unittest.TestCase):
    def test_zero_reward_is_real_evaluated_failure(self):
        with tempfile.TemporaryDirectory() as d:
            row = audit_trial(create_trial(Path(d) / "trial"))
            self.assertEqual(row["status"], "OFFICIAL_ARTIFACT_VERIFIED")
            self.assertEqual(row["reward"], 0.0)

    def test_positive_reward_verified_without_reinterpreting(self):
        with tempfile.TemporaryDirectory() as d:
            row = audit_trial(create_trial(Path(d) / "trial", reward=1.0, result_reward=1.0))
            self.assertEqual(row["status"], "OFFICIAL_ARTIFACT_VERIFIED")
            self.assertEqual(row["reward"], 1.0)

    def test_missing_verifier_cannot_claim_success(self):
        with tempfile.TemporaryDirectory() as d:
            t = create_trial(Path(d) / "trial", reward=1.0, result_reward=1.0)
            (t / "verifier" / "reward.txt").unlink()
            self.assertEqual(audit_trial(t)["status"], "NOT_EVALUATED")

    def test_missing_lock_cannot_claim_official(self):
        with tempfile.TemporaryDirectory() as d:
            t = create_trial(Path(d) / "trial", reward=1.0, result_reward=1.0, with_lock=False)
            self.assertEqual(audit_trial(t)["status"], "NOT_EVALUATED")

    def test_score_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            t = create_trial(Path(d) / "trial", reward=0.0, result_reward=1.0)
            self.assertEqual(audit_trial(t)["status"], "VERIFIER_MISMATCH")

    def test_job_requires_job_evidence_and_checks_all_trials(self):
        with tempfile.TemporaryDirectory() as d:
            job = Path(d)
            create_trial(job / "trials" / "a", reward=1, result_reward=1)
            self.assertEqual(audit_job(job)["status"], "NOT_EVALUATED")
            for p in ("config.json", "result.json", "lock.json"):
                (job / p).write_text("{}")
            self.assertEqual(audit_job(job)["status"], "OFFICIAL_ARTIFACT_VERIFIED")
            create_trial(job / "trials" / "b", reward=0, result_reward=1)
            self.assertEqual(audit_job(job)["status"], "PARTIAL_OR_UNVERIFIED")

    def test_cli_exit_status_reflects_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            job = Path(d) / "job"
            job.mkdir()
            self.assertEqual(main([str(job)]), 2)
            for p in ("config.json", "result.json", "lock.json"):
                (job / p).write_text("{}")
            create_trial(job / "trials" / "one", reward=1, result_reward=1)
            self.assertEqual(main([str(job), "--output", str(Path(d) / "audit.json")]), 0)
            self.assertTrue((Path(d) / "audit.json").is_file())


if __name__ == "__main__":
    unittest.main()
