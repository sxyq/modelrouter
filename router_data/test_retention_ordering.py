#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression test for P0-1 Checkpoint Retention Ordering.

Verifies:
1. Current epoch is present in run_meta["history"] before load_and_evaluate_all is called.
2. The current epoch is evaluated by evaluate_cohort_retention and receives a real decision
   (not a fallback 'not_qualified' caused by absence in run.json).
3. Idempotency: multiple calls do not duplicate epoch entries in run_meta["history"].
4. Physical weights are saved if qualified.
"""

import json
import copy
import shutil
import sys
import tempfile
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from router_data.checkpoint_retention import (
    CheckpointRetentionManager,
    STATUS_RETAINED_BEST,
    STATUS_RETAINED_TOP_K,
    STATUS_METADATA_ONLY,
    OLD_CORE_CHECKPOINT_IDS,
    HISTORICAL_PRE_Q012_COMPLETED_RUNS,
    NEW_PROTOCOL_VERSION,
    build_comparable_group_id,
    collect_pinned_parent_ids,
    evaluate_cohort_retention,
    select_run_best_epoch,
    update_safe_symlink,
)


def _dummy_saver(target_dir):
    p = Path(target_dir)
    p.mkdir(parents=True, exist_ok=True)
    (p / "model.safetensors").write_bytes(b"dummy_weights_12345")
    (p / "rl_agent_config.json").write_text(json.dumps({"test": True}))


def test_retention_ordering():
    print("=== TEST RETENTION ORDERING REGRESSION ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_root = Path(tmpdir)
        mgr = CheckpointRetentionManager(
            out_root=out_root,
            s2_audit_passed=True,
            stop_free_bytes=1024**2,
            stop_free_pct=0.01,
        )

        run_id = "TEST_RUN_01"
        run_root = out_root / run_id
        run_root.mkdir()

        run_meta = {
            "run_id": run_id,
            "base_run_id": run_id,
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "supervision_classes": ["S1"],
            "train_groups": {"S1": 1000},
            "val_groups": {"S1": 561},
            "history": [],
        }

        # Epoch 1 Entry (super good metrics beating baseline)
        entry_e1 = {
            "checkpoint_id": f"{run_id}-e01",
            "epoch": 1,
            "train_loss": 0.55,
            "validation": {
                "S1": {
                    "items": 561,
                    "loss": 0.58,
                    "accuracy": 0.68,
                    "brier": 0.40,
                    "ece": 0.03,
                    "by_source": {
                        "ROUTE-004": {"items": 561, "loss": 0.58, "accuracy": 0.68, "brier": 0.40, "ece": 0.03}
                    },
                }
            },
            "improved_0_5pct": True,
            "best_epoch": 1,
            "global_step": 100,
        }

        # Call handle_epoch_checkpoint (with entry already appended or appended during call)
        ret_result = mgr.handle_epoch_checkpoint(
            run_id=run_id,
            epoch=1,
            is_final_epoch=False,
            save_fn=_dummy_saver,
            run_meta=run_meta,
            entry=entry_e1,
        )

        print(f"Epoch 1 Decision: status={ret_result['retention_status']}, reason={ret_result['retention_reason']}")

        # Verify entry was evaluated and qualified
        assert ret_result["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K), \
            f"Expected retained status, got {ret_result['retention_status']}"
        assert ret_result["weights_saved"] is True

        # Verify run.json and epoch_metrics.json on disk contain epoch 1
        run_json = json.loads((run_root / "run.json").read_text())
        assert len(run_json["history"]) == 1
        assert run_json["history"][0]["checkpoint_id"] == f"{run_id}-e01"
        assert run_json["history"][0]["retention_status"] == ret_result["retention_status"]

        # Verify physical weights exist on disk
        ckpt_dir = run_root / "checkpoints" / "epoch_01"
        assert (ckpt_dir / "model.safetensors").is_file()

        # Now test Epoch 2 (even better metrics)
        entry_e2 = {
            "checkpoint_id": f"{run_id}-e02",
            "epoch": 2,
            "train_loss": 0.50,
            "validation": {
                "S1": {
                    "items": 561,
                    "loss": 0.52,
                    "accuracy": 0.72,
                    "brier": 0.38,
                    "ece": 0.02,
                    "by_source": {
                        "ROUTE-004": {"items": 561, "loss": 0.52, "accuracy": 0.72, "brier": 0.38, "ece": 0.02}
                    },
                }
            },
            "improved_0_5pct": True,
            "best_epoch": 2,
            "global_step": 200,
        }

        ret_result_2 = mgr.handle_epoch_checkpoint(
            run_id=run_id,
            epoch=2,
            is_final_epoch=True,
            save_fn=_dummy_saver,
            run_meta=run_meta,
            entry=entry_e2,
        )

        print(f"Epoch 2 Decision: status={ret_result_2['retention_status']}, reason={ret_result_2['retention_reason']}")
        assert ret_result_2["retention_status"] in (STATUS_RETAINED_BEST, STATUS_RETAINED_TOP_K)
        assert ret_result_2["weights_saved"] is True

        # Check final manifest
        manifest = mgr.write_checkpoint_manifest()
        top5_manifest = json.loads((out_root / "top5_core_checkpoint_manifest.json").read_text())
        new_core_cids = [c["checkpoint_id"] for c in top5_manifest["new_core_checkpoints"]]
        print(f"New Core CIDs: {new_core_cids}")
        assert f"{run_id}-e02" in new_core_cids, f"Expected {run_id}-e02 in new_core_checkpoints, found {new_core_cids}"

        print(">>> TEST RETENTION ORDERING PASSED!")


def test_two_phase_cleanup_protects_running_run():
    print("=== TEST TWO PHASE CLEANUP PROTECTS RUNNING RUN ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_root = Path(tmpdir)
        # active_budget_bytes set to 10 bytes so budget is strictly exceeded
        mgr = CheckpointRetentionManager(
            out_root=out_root,
            active_budget_bytes=10,
            stop_free_bytes=1024**2,
            stop_free_pct=0.01,
        )

        run_id = "RUNNING_RUN_01"
        run_root = out_root / run_id
        ckpt_dir = run_root / "checkpoints" / "epoch_01"
        ckpt_dir.mkdir(parents=True)
        (ckpt_dir / "model.safetensors").write_bytes(b"x" * 1024)

        run_meta = {
            "run_id": run_id,
            "status": "running",
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "history": [
                {
                    "checkpoint_id": f"{run_id}-e01",
                    "epoch": 1,
                    "train_loss": 0.8,
                    "validation": {"S1": {"loss": 0.9, "accuracy": 0.4}},
                }
            ],
        }
        (run_root / "run.json").write_text(json.dumps(run_meta))
        (run_root / "epoch_metrics.json").write_text(json.dumps(run_meta["history"]))

        # Cleanup should NEVER evict this running run in Step 3 or Step 4
        res = mgr.two_phase_cleanup()
        assert res["phase2_executed_count"] == 0, f"Expected 0 deletions, got {res['phase2_executed_count']}"
        assert (ckpt_dir / "model.safetensors").is_file(), "Active running weights must remain intact!"

        # Now mark as completed
        run_meta["status"] = "completed"
        (run_root / "run.json").write_text(json.dumps(run_meta))

        res2 = mgr.two_phase_cleanup()
        assert res2["phase2_executed_count"] == 1, "Completed low-score run should be pruned/evicted"
        assert not (ckpt_dir / "model.safetensors").is_file(), "Completed run weights cleaned up"

        print(">>> TEST TWO PHASE CLEANUP PROTECTS RUNNING RUN PASSED!")


def test_two_phase_cleanup_protects_dual_pool_and_pinned():
    print("=== TEST TWO PHASE CLEANUP PROTECTS DUAL POOL AND PINNED ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_root = Path(tmpdir)
        # active_budget_bytes set to 10 bytes so budget is strictly exceeded
        mgr = CheckpointRetentionManager(
            out_root=out_root,
            active_budget_bytes=10,
            stop_free_bytes=1024**2,
            stop_free_pct=0.01,
            explicit_pinned={"PINNED_RUN-e01"},
        )

        # 1. Old Core Pool checkpoint (P0_B03_C01_QB_PB-e02)
        old_core_run = "P0_B03_C01_QB_PB"
        old_core_dir = out_root / old_core_run
        old_core_ckpt = old_core_dir / "checkpoints" / "epoch_02"
        old_core_ckpt.mkdir(parents=True)
        (old_core_ckpt / "model.safetensors").write_bytes(b"old_core_weights")
        old_core_meta = {
            "run_id": old_core_run,
            "status": "completed",
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "history": [{"checkpoint_id": f"{old_core_run}-e02", "epoch": 2, "train_loss": 0.4}],
        }
        (old_core_dir / "run.json").write_text(json.dumps(old_core_meta))
        (old_core_dir / "epoch_metrics.json").write_text(json.dumps(old_core_meta["history"]))

        # 2. Pinned parent checkpoint
        pinned_run = "PINNED_RUN"
        pinned_dir = out_root / pinned_run
        pinned_ckpt = pinned_dir / "checkpoints" / "epoch_01"
        pinned_ckpt.mkdir(parents=True)
        (pinned_ckpt / "model.safetensors").write_bytes(b"pinned_weights")
        pinned_meta = {
            "run_id": pinned_run,
            "status": "completed",
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "history": [{"checkpoint_id": f"{pinned_run}-e01", "epoch": 1, "train_loss": 0.5}],
        }
        (pinned_dir / "run.json").write_text(json.dumps(pinned_meta))
        (pinned_dir / "epoch_metrics.json").write_text(json.dumps(pinned_meta["history"]))

        # 3. Disposable un-retained low-score run
        disp_run = "DISPOSABLE_RUN"
        disp_dir = out_root / disp_run
        disp_ckpt = disp_dir / "checkpoints" / "epoch_01"
        disp_ckpt.mkdir(parents=True)
        (disp_ckpt / "model.safetensors").write_bytes(b"disp_weights")
        disp_meta = {
            "run_id": disp_run,
            "status": "completed",
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "history": [{"checkpoint_id": f"{disp_run}-e01", "epoch": 1, "train_loss": 0.9, "validation": {"S1": {"loss": 1.2, "accuracy": 0.3}}}],
        }
        (disp_dir / "run.json").write_text(json.dumps(disp_meta))
        (disp_dir / "epoch_metrics.json").write_text(json.dumps(disp_meta["history"]))

        res = mgr.two_phase_cleanup()
        # Old core and pinned parent MUST remain intact
        assert (old_core_ckpt / "model.safetensors").is_file(), "Old Core weights must be protected!"
        assert (pinned_ckpt / "model.safetensors").is_file(), "Pinned parent weights must be protected!"
        # Disposable run should be cleaned up
        assert not (disp_ckpt / "model.safetensors").is_file(), "Disposable weights should be cleaned up"
        print(">>> TEST TWO PHASE CLEANUP PROTECTS DUAL POOL AND PINNED PASSED!")


def test_sync_run_best_symlink_scientific_integrity(monkeypatch):
    print("=== TEST SYNC RUN BEST SYMLINK SCIENTIFIC INTEGRITY ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_root = Path(tmpdir)
        mgr = CheckpointRetentionManager(out_root=out_root)
        run_id = "SCIENTIFIC_RUN_01"
        run_dir = out_root / run_id
        ckroot = run_dir / "checkpoints"
        ckroot.mkdir(parents=True)

        ep1_dir = ckroot / "epoch_01"
        ep2_dir = ckroot / "epoch_02"
        ep1_dir.mkdir()
        ep2_dir.mkdir()
        import router_data.checkpoint_retention as retention
        available = {ep1_dir.resolve()}
        monkeypatch.setattr(retention, "has_physical_weights", lambda path: Path(path).resolve() in available)
        monkeypatch.setattr(retention, "is_loadable_checkpoint_path", lambda path: Path(path).resolve() in available)

        # History: Epoch 1 (loss 0.60), Epoch 2 (loss 0.50 -> scientific best)
        history = [
            {"epoch": 1, "validation": {"S1": {"loss": 0.60, "accuracy": 0.65}}},
            {"epoch": 2, "validation": {"S1": {"loss": 0.50, "accuracy": 0.75}}},
        ]
        rdata = {
            "run_id": run_id,
            "status": "completed",
            "history": history,
            "best_epoch": 2,
        }

        # Scenario A: Epoch 2 weights pruned, only suboptimal Epoch 1 weights exist
        mgr._sync_run_best_symlink(run_id, rdata)

        # 1. best_epoch MUST strictly remain 2, NEVER overwritten to 1
        assert rdata["best_epoch"] == 2, f"Expected best_epoch=2, got {rdata['best_epoch']}"
        # 2. best_checkpoint MUST be None, not pointing to suboptimal epoch_01
        assert rdata["best_checkpoint"] is None, f"Expected best_checkpoint=None, got {rdata['best_checkpoint']}"
        assert not (ckroot / "best").exists(), "best symlink must be absent or unlinked when scientific best is missing"

        # Scenario B: Scientific best Epoch 2 weights physically restored/generated
        available.add(ep2_dir.resolve())
        mgr._sync_run_best_symlink(run_id, rdata)

        assert rdata["best_epoch"] == 2
        assert rdata["best_checkpoint"] == f"{run_id}/checkpoints/best"
        assert (ckroot / "best").resolve().name == "epoch_02"
        print(">>> TEST SYNC RUN BEST SYMLINK SCIENTIFIC INTEGRITY PASSED!")


def _retention_node(run_id, group="A", epoch=1, loss=.55, family="S1"):
    metrics = {"items": 561, "loss": loss, "accuracy": .7, "brier": .4, "ece": .03,
               "balanced_accuracy": .5, "macro_f1": .4}
    return {"run_id": run_id, "checkpoint_id": f"{run_id}-e{epoch:02d}", "epoch": epoch,
            "run_status": "completed", "protocol_version": NEW_PROTOCOL_VERSION,
            "supervision_classes": [family], "task_family": family, "val_groups": {family: 561},
            "config": {"loss": group}, "dedup_signature": run_id, "validation": {family: metrics}}


def _selected(nodes, pinned=None, **kwargs):
    decisions, groups = evaluate_cohort_retention(nodes, pinned or {}, **kwargs)
    return {cid for cid, d in decisions.items() if d.get("retention_pool") == "NEW_CORE_POOL"}, decisions, groups


def test_retention_algorithm_remainder_is_order_independent():
    nodes = [_retention_node(f"TEST_A_{i}", "A", loss=.55 - i * .001) for i in range(3)]
    nodes += [_retention_node(f"TEST_B_{i}", "B", loss=.55 - i * .001) for i in range(7)]
    selected, _, groups = _selected(copy.deepcopy(nodes))
    reversed_selected, _, _ = _selected(copy.deepcopy(list(reversed(nodes))))
    assert selected == reversed_selected == {"TEST_A_2-e01", "TEST_B_6-e01"}
    assert sorted(g["new_pool_quota"] for g in groups.values()) == [1, 1]
    assert sum(g["new_pool_quota"] for g in groups.values()) == 2


def test_retention_algorithm_equal_remainder_uses_group_id():
    nodes = [_retention_node("TEST_B", "B"), _retention_node("TEST_A", "A")]
    selected, _, groups = _selected(nodes)
    assert selected == {"TEST_A-e01"}
    assert sum(g["new_pool_quota"] for g in groups.values()) == 1


def test_retention_algorithm_full_history_same_best_standard():
    first = _retention_node("TEST_RUN", epoch=1, loss=.50)
    second = _retention_node("TEST_RUN", epoch=2, loss=.51)
    second["validation"]["S1"].update(accuracy=.9, brier=.3, ece=.02)
    run = {**first, "history": [first, second], "best_epoch": 1}
    assert select_run_best_epoch(run) == 1
    parent_map = collect_pinned_parent_ids({"TEST_RUN": run},
        {"CHILD": {"parent_run_id": "TEST_RUN", "continuation_mode": "warm_start"}})
    assert "TEST_RUN-e01" in parent_map
    assert "TEST_RUN-e02" not in parent_map
    selected, decisions, _ = _selected([first, second])
    assert selected == {"TEST_RUN-e01"}
    assert decisions["TEST_RUN-e02"]["is_run_best_epoch"] is False
    invalid = _retention_node("TEST_RUN", epoch=3, loss=.01)
    invalid["validation"]["S1"]["loss"] = float("nan")
    run["history"].append(invalid)
    assert select_run_best_epoch(run) == 1


def test_s1_best_definition_ignores_retention_metadata():
    first = {"epoch": 1, "validation": {"S1": {"loss": .50}}}
    second = {"epoch": 2, "validation": {"S1": {"loss": .51, "accuracy": .9}}}
    run = {"supervision_classes": ["S1"], "val_groups": {"S1": 561}, "history": [second, first]}
    assert select_run_best_epoch(run) == 1
    first["validation"]["S1"].update(items=12, accuracy=None, brier=None, ece=None)
    assert select_run_best_epoch(run) == 1
    second["validation"]["S1"]["loss"] = .50
    assert select_run_best_epoch(run) == 2


def test_retention_algorithm_complete_candidate_count_and_protection():
    nodes = [_retention_node(f"TEST_GOOD_{i}") for i in range(7)]
    running = _retention_node("TEST_ACTIVE")
    running["run_status"] = "running"
    missing = _retention_node("TEST_MISSING")
    missing["validation"]["S1"]["accuracy"] = None
    invalid = _retention_node("TEST_INVALID")
    invalid["validation"]["S1"]["loss"] = float("nan")
    partial = _retention_node("TEST_PARTIAL")
    partial["validation"]["S1"]["items"] = 12
    duplicate = _retention_node("TEST_Z_DUPLICATE")
    duplicate["dedup_signature"] = "TEST_GOOD_0"
    old_id = sorted(OLD_CORE_CHECKPOINT_IDS)[0]
    old = _retention_node(old_id.rsplit("-e", 1)[0], epoch=int(old_id.rsplit("-e", 1)[1]))
    historical = _retention_node(sorted(HISTORICAL_PRE_Q012_COMPLETED_RUNS)[0])
    parent = _retention_node("TEST_PARENT")
    nodes.extend([running, missing, invalid, partial, duplicate, old, historical, parent])
    selected, decisions, groups = _selected(nodes, {parent["checkpoint_id"]: ["child"]})
    assert len(selected) == 2
    assert sum(g.get("new_pool_eligible_runs", 0) for g in groups.values()) == 7
    assert decisions[old_id]["retention_pool"] == "OLD_CORE_POOL"
    assert decisions[parent["checkpoint_id"]]["retention_pool"] == "PINNED_PARENT"
    assert decisions[historical["checkpoint_id"]]["retention_pool"] == "HISTORICAL_METADATA_ONLY"
    assert not selected.intersection(n["checkpoint_id"] for n in [running, missing, invalid, partial, duplicate])
    mgr = object.__new__(CheckpointRetentionManager)
    assert mgr.is_mandatory_checkpoint(cid="unknown", dec={}, run_status="completed")[0]
    assert mgr.is_mandatory_checkpoint(cid="active", dec={}, run_status="failed")[0]
    assert mgr.is_mandatory_checkpoint(cid=missing["checkpoint_id"],
        dec=decisions[missing["checkpoint_id"]], node=missing, run_status="completed")[0]


def test_retention_algorithm_no_task_score_mix_and_group_identity():
    s1 = _retention_node("TEST_S1", family="S1")
    s2 = _retention_node("TEST_S2", family="S2", loss=1.0)
    selected, _, groups = _selected([s2, s1], s2_audit_passed=False)
    assert selected == {"TEST_S1-e01"}
    assert sum(g.get("new_pool_eligible_runs", 0) for g in groups.values()) == 1
    a = build_comparable_group_id(s1)
    mixed = copy.deepcopy(s1)
    mixed["supervision_classes"] = ["S1", "S2"]
    mixed["val_groups"]["S2"] = 337
    assert build_comparable_group_id(mixed) != a
    mixed["val_groups"]["S2"] = 336
    assert "S2:336" in build_comparable_group_id(mixed)


def test_retention_algorithm_metadata_does_not_delete_unknown_entity(tmp_path, monkeypatch):
    target = tmp_path / "best"
    target.mkdir()
    (target / "metadata.json").write_text("{}")
    monkeypatch.setattr(shutil, "rmtree", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("No entity removal")))
    update_safe_symlink(target, None)
    assert target.is_dir()
    unknown_file = tmp_path / "latest"
    unknown_file.write_text("unknown original entity")
    update_safe_symlink(unknown_file, None)
    assert unknown_file.read_text() == "unknown original entity"
    run = _retention_node("TEST_RUN")
    run["history"] = [run.copy()]
    run["best_epoch"] = 1
    mgr = CheckpointRetentionManager(out_root=tmp_path)
    mgr._sync_run_best_symlink("TEST_RUN", run)
    assert run["best_epoch"] == 1
    assert run["best_checkpoint"] is None


def test_retention_algorithm_final_save_sees_best_before_complete(tmp_path, monkeypatch):
    mgr = CheckpointRetentionManager(out_root=tmp_path)
    node = _retention_node("TEST_FINAL")
    run = {**node, "history": [], "status": "running"}
    monkeypatch.setattr(mgr, "disk_status", lambda: {"stop_triggered": True, "root_avail_bytes": 0})
    def observe(*args):
        persisted = json.loads((tmp_path / "TEST_FINAL" / "run.json").read_text())
        assert persisted["history"][0]["epoch"] == 1
        assert persisted["best_epoch"] == 1
        assert persisted["status"] == "running"
        assert _selected([dict(node, run_status=persisted["status"])])[0] == set()
        return {}, [], {}, {}, {}
    monkeypatch.setattr(mgr, "load_and_evaluate_all", observe)
    from router_data.checkpoint_retention import DiskBudgetExceededError
    import pytest
    with pytest.raises(DiskBudgetExceededError):
        mgr.handle_epoch_checkpoint("TEST_FINAL", 1, True,
            lambda *args: (_ for _ in ()).throw(AssertionError("No saver invocation")), run, node)


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


def test_collector_original_history_inputs_and_unchanged_revision():
    from scripts import fetch_live_status as collector

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        runs_root = root / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
        def write_json(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")

        for rid, loss, validation_set in (("F01", .5, "same-fixed-val"),
                                          ("F02", .6, "same-fixed-val"),
                                          ("F03", .7, "other-fixed-val"),
                                          ("F03_LEGACY_MINFACTOR", .8, "legacy-fixed-val")):
            directory = runs_root / rid
            history = [{"checkpoint_id": rid + "-e01", "epoch": 1, "global_step": 10,
                        "train_loss": None if rid == "F03" else .4,
                        "validation": {"S1": {"loss": loss, "accuracy": .6, "items": 561}}}]
            if rid == "F01":
                history.append({"checkpoint_id": "F01-e02", "epoch": 2, "global_step": 20,
                                "train_loss": None, "validation": {"S1": {"loss": None, "items": 561}}})
            write_json(directory / "run.json", {"run_id": rid, "status": "completed",
                "protocol_version": "LEGACY_MINFACTOR" if "LEGACY" in rid else NEW_PROTOCOL_VERSION,
                "validation_set": validation_set, "history": history})
            write_json(directory / "epoch_metrics.json", history)
            write_json(directory / "cursor.json", {"consumed_items": 100, "consumed_units": 7})
        physical = runs_root / "F01/checkpoints/epoch_01.pt"
        physical.parent.mkdir(parents=True)
        physical.write_bytes(b"temporary fixture only")
        queue_log = runs_root / "continuous_queue.log"
        queue_log.write_text("[F03] Epoch 1/2 Chunk 1/2: loss=0.123, step=99/100, consumed=90/100\n")

        imported = root / "models/kev-4b-adapter"
        local_parent = root / "runs/KEV-FIXTURE"
        for directory, maximum in ((imported, None), (local_parent / "smoke_run", 2),
                                   (local_parent / "test_run", 3)):
            args = {"device": "cpu", "epochs": 2}
            if maximum is not None:
                args["max_steps"] = maximum
            write_json(directory / "training_config.json", {"args": args})
            write_json(directory / "training_metrics.json", {"optimizer_steps": maximum or 8,
                       "records_seen": 4, "grad_norm": [1.0, .9]})
            (directory / "adapter_model.pt").write_bytes(b"temporary adapter fixture only")
        (local_parent / "train_cpu.log").write_text("ep0 step 2/3 loss 0.111 1.0s/rec\n")

        originals = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
        output = root / "dashboard"
        payload = collector.build_training_history(root, output, processes={})
        assert payload["counts"]["laya"]["local_runs"] == 4
        assert payload["counts"]["kev"]["local_runs"] == 2
        assert payload["counts"]["kev"]["imported_assets"] == 1
        local_kev = [row for row in payload["runs"] if row["family"] == "kev" and row["origin"] == "LOCAL_RUN"]
        assert len(local_kev) == 2
        assert all(row["epochs"] == 0 and row["curve_points"] == 0 for row in local_kev)
        assert all(row["checkpoints"][0]["physical"] for row in local_kev)
        f01 = next(row for row in payload["runs"] if row["run_id"] == "F01")
        assert f01["checkpoints"][0]["physical"] is True
        assert f01["checkpoints"][0]["weight_bytes"] == physical.stat().st_size
        assert f01["checkpoints"][1]["evidence"] == "MISSING_HISTORY_UNCERTAIN"
        assert f01["checkpoints"][1]["ever_saved"] is None
        assert f01["exposure"]["trained_records"] == 100
        assert f01["validation"][1]["loss"] is None
        for row in payload["runs"]:
            detail = json.loads((output / row["curve_path"]).read_text())
            if row["run_id"] in ("F03", "F03_LEGACY_MINFACTOR"):
                assert all(point["step"] != 99 for point in detail["points"])
            if row["run_id"] == "F03":
                assert detail["points"][0]["train_loss"] is None
        comparison = next(row for row in payload["comparisons"]
                          if row["metric"] == "loss" and "same-fixed-val" in row["validation_set"])
        assert comparison["observations"] == 2
        assert comparison["best"]["run_id"] == "F01"
        assert comparison["worst"]["run_id"] == "F02"
        index = output / "shards/training_history.json"
        first_mtime = index.stat().st_mtime_ns
        again = collector.build_training_history(root, output, processes={})
        assert again["revision"] == payload["revision"]
        assert index.stat().st_mtime_ns == first_mtime
        assert all(path.read_bytes() == content for path, content in originals.items())


if __name__ == "__main__":
    test_retention_ordering()
    test_two_phase_cleanup_protects_running_run()
    test_two_phase_cleanup_protects_dual_pool_and_pinned()
    import pytest
    with pytest.MonkeyPatch.context() as monkeypatch:
        test_sync_run_best_symlink_scientific_integrity(monkeypatch)


