"""Existing package identity and CLI cases."""
import sys

from router_data.test_retention_ordering import _PROJECT_ROOT
from router_data.checkpoint_retention import CheckpointRetentionManager


def test_migrated_package_retention_is_same_module_and_private_symbols():
    from router_data import checkpoint_retention as canonical
    from modelrouter.training.common import checkpoint_retention as packaged
    from modelrouter.training.common.checkpoint_retention import _node_primary_sort_key

    assert packaged is canonical
    assert packaged.evaluate_cohort_retention is canonical.evaluate_cohort_retention
    assert packaged.CheckpointRetentionManager is canonical.CheckpointRetentionManager
    assert packaged.select_run_best_epoch is canonical.select_run_best_epoch
    assert _node_primary_sort_key is canonical._node_primary_sort_key


def test_migrated_package_training_is_same_module_and_cli(monkeypatch):
    from router_data import laya_batch_train as canonical
    from modelrouter.training.laya import laya_batch_train as packaged
    from modelrouter.training.laya.laya_batch_train import _save_ckpt_with_optim

    assert packaged is canonical
    assert packaged.run_full_coverage_stream_run is canonical.run_full_coverage_stream_run
    assert packaged.resolve_checkpoint_to_resume is canonical.resolve_checkpoint_to_resume
    assert packaged.CheckpointRetentionManager is CheckpointRetentionManager
    assert _save_ckpt_with_optim is canonical._save_ckpt_with_optim
    assert packaged.main is canonical.main
    sentinel = lambda: "shared-cli"
    monkeypatch.setattr(packaged, "main", sentinel)
    assert canonical.main is sentinel


def test_migrated_package_training_cli_help_from_other_directory(tmp_path):
    import subprocess

    module_name = "modelrouter.training.laya.laya_batch_train"
    file_path = _PROJECT_ROOT / "our-project/code/src/modelrouter/training/laya/laya_batch_train.py"
    for entry in (["-m", module_name], [str(file_path)]):
        result = subprocess.run([sys.executable, *entry, "--help"], cwd=tmp_path,
                                text=True, capture_output=True, timeout=15)
        assert result.returncode == 0, result.stderr
        assert "--full-coverage-run" in result.stdout
        assert "--regenerate-parent" in result.stdout


def test_migrated_package_collector_is_same_module_and_cli(tmp_path):
    import subprocess
    from scripts import fetch_live_status as canonical
    from modelrouter.telemetry import fetch_live_status as packaged
    from modelrouter.telemetry.fetch_live_status import _JSON_CACHE

    assert packaged is canonical
    assert packaged.build_training_history is canonical.build_training_history
    assert packaged.sync_once is canonical.sync_once
    assert packaged.main is canonical.main
    assert _JSON_CACHE is canonical._JSON_CACHE
    file_path = _PROJECT_ROOT / "our-project/code/src/modelrouter/telemetry/fetch_live_status.py"
    for entry in (["-m", "modelrouter.telemetry.fetch_live_status"], [str(file_path)]):
        result = subprocess.run([sys.executable, *entry, "--help"], cwd=tmp_path,
                                text=True, capture_output=True, timeout=15)
        assert result.returncode == 0, result.stderr
        assert "--history-only" in result.stdout
        assert "--probe-only" in result.stdout


def test_migrated_package_queue_is_same_module_and_cli(tmp_path):
    import subprocess
    from router_data import run_full_graded_queue as canonical
    from modelrouter.training.common import run_full_graded_queue as packaged
    from modelrouter.training.common.run_full_graded_queue import _write_json

    assert packaged is canonical
    assert packaged.main is canonical.main
    assert _write_json is canonical._write_json
    assert packaged.CheckpointRetentionManager is CheckpointRetentionManager
    file_path = _PROJECT_ROOT / "our-project/code/src/modelrouter/training/common/run_full_graded_queue.py"
    for entry in (["-m", "modelrouter.training.common.run_full_graded_queue"], [str(file_path)]):
        result = subprocess.run([sys.executable, *entry, "--help"], cwd=tmp_path,
                                text=True, capture_output=True, timeout=15)
        assert result.returncode == 0, result.stderr
        assert "--max-runs" in result.stdout
        assert "--epochs" in result.stdout


