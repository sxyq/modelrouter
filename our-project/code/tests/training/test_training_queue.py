"""Existing training resource and continuation cases."""
import json
from pathlib import Path

from test_retention_ordering import _PROJECT_ROOT, _dummy_saver


def test_queue_gpu_uses_available_memory(monkeypatch):
    from router_data import run_full_graded_queue as queue
    def gpu_query(cmd, **kwargs):
        assert "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu" in cmd
        return "0, NVIDIA RTX A6000, 49140, 20081, 28460, 98"
    monkeypatch.setattr(queue.subprocess, "check_output", gpu_query)
    available, info = queue.check_gpu_available()
    assert available
    assert info["required_free_mib"] == 16384
    assert info["memory_free_mib"] == 28460
    monkeypatch.setattr(queue.subprocess, "check_output", lambda *a, **k:
                        "0, NVIDIA RTX A6000, 49140, 32200, 16341, 98")
    assert queue.check_gpu_available()[0] is False


def test_queue_completed_parent_is_not_retrained(tmp_path, monkeypatch):
    from router_data import run_full_graded_queue as queue
    monkeypatch.setattr(queue, "FULL_COVERAGE_STAGE_MAP", {"F01": (2, 1), "F17": (5, 1),
                        "F18": (5, 2), "F01_S3": (6, 1)})
    queue._write_json(tmp_path / "F01/run.json", {"run_id": "F01", "status": "completed",
                      "best_epoch": 2, "history": []})
    state = {"completed_runs": ["F01"]}
    ordered, rec = queue.build_ordered_full_coverage_queue(tmp_path, {}, state)
    assert [p["run_id"] for p in ordered] == ["F01_S3"]
    assert set(rec["pending_parents"]) == {"F17", "F18"}
    assert not any(p.get("regenerate_parent") for p in ordered)
    _dummy_saver(tmp_path / "F01/checkpoints/epoch_01")
    assert [p["run_id"] for p in queue.build_ordered_full_coverage_queue(tmp_path, {}, state)[0]] == ["F01_S3"]
    _dummy_saver(tmp_path / "F01/checkpoints/epoch_02")
    assert [p["run_id"] for p in queue.build_ordered_full_coverage_queue(tmp_path, {}, state)[0]] == ["F17", "F01_S3"]


def test_queue_completed_state_prevents_f03_repeat(tmp_path, monkeypatch):
    from router_data import run_full_graded_queue as queue
    monkeypatch.setattr(queue, "FULL_COVERAGE_STAGE_MAP", {"F03": (2, 1)})
    ordered, rec = queue.build_ordered_full_coverage_queue(tmp_path, {}, {"completed_runs": ["F03"]})
    assert not ordered
    assert rec["completed_runs_count"] == 1


def test_queue_materialization_reuses_matrix_and_keeps_history(tmp_path, monkeypatch):
    from router_data import run_full_graded_queue as queue
    from router_data import batch_prep
    out = tmp_path / "out"
    out.mkdir()
    (tmp_path / "runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1").mkdir(parents=True)
    done = {"run_id": "P0_DONE", "status": "completed"}
    queue._write_json(out / "P0_DONE/run.json", done)
    manifest = {"plans": {"P0_DONE": done, "P0_B05_C01_QB_PB": {
        "base_run_id": "B05_C01_QB_PB", "groups": ["S1"]}}, "materialized": {"P0_DONE": {"S1": 1}}}
    def prepare(args):
        assert args.matrix_run_ids == "B05_C01_QB_PB"
        assert args.matrix_max_items == 4096
        data = Path(args.matrix_out_dir) / "data/P0_B05_C01_QB_PB/train"
        data.mkdir(parents=True)
        (data / "S1.jsonl").write_text("{}\n")
        return {"plans": {"P0_B05_C01_QB_PB": {"materialized": True,
                "data": "data/P0_B05_C01_QB_PB"}},
                "materialized": {"P0_B05_C01_QB_PB": {"S1": 1}},
                "materialization_audit": {"P0_B05_C01_QB_PB": {}}}
    monkeypatch.setattr(batch_prep, "prepare_full_matrix", prepare)
    assert queue.materialize_plan_on_demand(tmp_path, out, manifest, out / "experiment_matrix.json",
                                           "P0_B05_C01_QB_PB")
    assert json.loads((out / "P0_DONE/run.json").read_text()) == done
    assert manifest["plans"]["P0_DONE"] == done
    assert (out / "data/P0_B05_C01_QB_PB/train/S1.jsonl").exists()
    assert not list(out.glob("_matrix_prep_*"))


def test_queue_failed_independent_run_continues_and_hands_off(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from router_data import run_full_graded_queue as queue
    original_mode_a = queue.run_queue
    queue._write_json(tmp_path / "baseline_0.json", {"S1": {"loss": .7}})
    queue._write_json(tmp_path / "full_coverage_manifest.json", {"plans": {}})
    monkeypatch.setattr(queue, "FULL_COVERAGE_STAGE_MAP", {"F08": (4, 1), "F09": (4, 2)})
    disk_runs = []
    monkeypatch.setattr(queue, "CheckpointRetentionManager", lambda **k: SimpleNamespace(
                        pre_run_disk_check=lambda **k: disk_runs.append(k["run_id"])))
    monkeypatch.setattr(queue, "check_gpu_available", lambda: (True, {}))
    def sync(project_root):
        assert project_root == tmp_path.resolve()
        return {}
    monkeypatch.setattr(queue, "build_training_history", sync)
    assert not hasattr(queue, "run_storage_policy_verification")
    launched = []
    def launch(cmd, **kwargs):
        rid = cmd[cmd.index("--full-coverage-run") + 1]
        launched.append(rid)
        assert "--regenerate-parent" not in cmd
        return SimpleNamespace(returncode=1 if rid == "F08" else 0)
    monkeypatch.setattr(queue.subprocess, "run", launch)
    handoff = []
    def matrix(**kwargs):
        handoff.append(kwargs)
        return {"queue_state": {"queue_status": "IDLE_STAGE_COMPLETE"}}
    monkeypatch.setattr(queue, "run_queue", matrix)
    result = queue.run_continuous_full_coverage_queue(
        tmp_path, tmp_path, tmp_path / "full_coverage_manifest.json", tmp_path / "model",
        tmp_path, tmp_path, sync_github_every=0)
    assert launched == ["F08", "F09"]
    assert disk_runs == ["F08", "F09"]
    assert result["executed_runs"] == ["F09"]
    assert len(handoff) == 1
    assert handoff[0]["max_runs"] is None
    assert handoff[0]["allow_unmaterialized"] is True
    state = json.loads((tmp_path / "queue_state.json").read_text())
    assert state["failed_runs"]["F08"]["attempts"] == 1
    assert state["failed_runs"]["F08"]["reason"] == "RUN_FAILED"
    queue._write_json(tmp_path / "experiment_matrix.json", {"plans": {}})
    mode_a_result = original_mode_a(tmp_path, tmp_path, tmp_path / "experiment_matrix.json",
                                    tmp_path / "model", max_runs=None)
    assert mode_a_result["executed_runs"] == []
    assert not (tmp_path / "storage_policy_verification.json").exists()


def test_queue_materialization_uses_real_batch_prep(tmp_path, monkeypatch):
    import gzip
    from router_data import run_full_graded_queue as queue
    from router_data import batch_prep
    graded = tmp_path / "runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1"
    index = graded / "by_source"
    index.mkdir(parents=True)
    raw = {"pre_decision_state": {"candidate_model_a": "a", "candidate_model_b": "b"},
           "observed_decision": {"winner_model": "a"}}
    source = tmp_path / "data/公开数据/清洗数据" / batch_prep.PUBLIC_FILES["ROUTE-004"]
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps(raw) + "\n")
    ref = {"source_id": "ROUTE-004", "source_line": 1, "split": "train",
           "train_eligible": True, "source_policy_train_allowed": True, "quality_grade": "Q1",
           "assigned_layer": "L1", "primary_supervision_class": "S1", "stable_record_id": "r1",
           "independent_unit_id": "u1", "candidate_targets": ["human_pairwise_preference"]}
    for src in batch_prep.MATRIX_ALLOWED_SOURCES:
        with gzip.open(index / f"{src}.jsonl.gz", "wt") as stream:
            if src == "ROUTE-004":
                stream.write(json.dumps(ref) + "\n")
    queue._write_json(graded / "quality_summary.json", {"quality_by_source": {
        src: {"rows": 1 if src == "ROUTE-004" else 0} for src in batch_prep.MATRIX_ALLOWED_SOURCES}})
    val = graded / "batch_preparation/batch1/val"
    val.mkdir(parents=True)
    (val / "S1.jsonl").write_text(json.dumps({"state": {}, "questions": {}, "expected": {}}) + "\n")
    out = tmp_path / "out"
    out.mkdir()
    manifest = {"plans": {"P0_B01_C01_QB_PB": {"base_run_id": "B01_C01_QB_PB", "groups": ["S1"]}}}
    monkeypatch.chdir(_PROJECT_ROOT)
    assert queue.materialize_plan_on_demand(tmp_path, out, manifest, out / "experiment_matrix.json",
                                           "P0_B01_C01_QB_PB")
    row = json.loads((out / "data/P0_B01_C01_QB_PB/train/S1.jsonl").read_text())
    assert row["expected"]["model_choice"] == "a"
    assert manifest["plans"]["P0_B01_C01_QB_PB"]["materialized_counts"] == {"S1": 1}
    saved = json.loads((out / "experiment_matrix.json").read_text())
    assert saved["plans"]["P0_B01_C01_QB_PB"]["materialized"] is True
    assert saved["materialized"]["P0_B01_C01_QB_PB"] == {"S1": 1}
    assert (out / "data/P0_B01_C01_QB_PB/val/S1.jsonl").is_file()
    assert not list(out.glob("_matrix_prep_*"))


