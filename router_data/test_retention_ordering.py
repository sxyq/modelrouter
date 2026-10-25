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
    compute_kev_selection_score,
    evaluate_kev_retention,
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

        # Report production reads existing shards and leaves source observations intact.
        research_root = root / "our-project/dashboard"
        published = collector.build_training_history(root, research_root, processes={})
        summary = collector.write_training_research_report(published, root)
        report = json.loads((root / summary["data"]).read_text())
        selected = next(r for r in report["observations"] if r["run_id"] == "F01")
        assert selected["best_loss_epoch"]["epoch"] == 1
        assert selected["selected_epoch_physical"] is True
        assert selected["best_accuracy_epoch"]["epoch"] == 1
        assert selected["epoch_records"][0]["global_step"] == 10
        assert len(report["observations"]) == 7
        assert selected["actual_cost_usd"] is None
        assert all(path.read_bytes() == content for path, content in originals.items())


def test_collector_research_same_target_and_loadable_epochs(tmp_path):
    from scripts import fetch_live_status as collector

    def write_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    runs_root = tmp_path / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
    fixtures = {
        "F06": ("S1", [(1, .6738, .6002, .4141, .0247), (2, .6863, .6017, .415, .0549)]),
        "F06_S1": ("S1", [(2, .6809, .5936, .4079, None)]),
        "F07": ("S1", [(1, .6827, .6076, .4203, .0567), (2, .6791, .6145, .4213, .0388)]),
        "F08": ("S1", [(2, .6702, .6123, .4246, .0555)]),
        "F09": ("S1", [(2, .6649, .6100, .4226, .0271)]),
        "AUX_S2": ("S2", [(1, .9, .2, None, None)]),
        "AUX_S3": ("S3", [(1, .9, .2, None, None)]),
    }
    for index, (rid, (stream, values)) in enumerate(fixtures.items()):
        epochs = [{"epoch": epoch, "weights_saved": False,
                   "validation": {stream: {"accuracy": acc, "loss": loss, "brier": brier, "ece": ece, "items": 561}}}
                  for epoch, acc, loss, brier, ece in values]
        write_json(runs_root / rid / "run.json", {"run_id": rid, "status": "completed", "epochs_max": 2,
            "protocol_version": NEW_PROTOCOL_VERSION, "validation_set": "same-fixed-val",
            "supervision_classes": ["S1", "S2", "S3"] if rid in ("F06", "F07", "F08", "F09") else [stream],
            "train_origin": "cumulative", "base_model": "fixture-base",
            "layers": ["L1"], "config": {"loss": "soft-ce"},
            "started_at": f"2026-10-{index + 10:02d}T00:00:00Z", "history": epochs})
    physical = runs_root / "F06/checkpoints/epoch_02.pt"
    physical.parent.mkdir(parents=True)
    physical.write_bytes(b"temporary fixture only")

    c03 = {"acc": .5715969989281886, "nll": 1.0795525776246775,
           "brier": .537533605673637, "ece": .05104668378873653, "n": 9330}
    c04 = {"acc": .5711682743837084, "nll": 1.0872975000322915,
           "brier": .5402653787706695, "ece": .05987151793598101, "n": 9330}
    candidates = []
    for rid, metrics, seconds in (("KEV-V8-C03", c03, 3099.012350168079),
                                  ("KEV-V8-C04", c04, 2982.712651308626)):
        directory = tmp_path / "runs" / rid / "formal_run"
        write_json(directory / "training_config.json", {"args": {"device": "cuda", "epochs": 1,
                   "init_from": "fixture-parent-" + rid}})
        write_json(directory / "training_metrics.json", {"optimizer_steps": 16857, "grad_norm": [1.0]})
        val_metrics = {"clean": metrics, "duration_sec": seconds,
                   "validation_protocol": "fixed-val", "validation_set": "kev-fixed-val",
                   "coverage": {"requested_questions": 9330, "evaluated_questions": 9330}}
        write_json(directory / "val_metrics.json", val_metrics)
        (directory / "adapter_model.pt").write_bytes(b"temporary adapter fixture only")
        candidates.append({"candidate_id": rid, "status": "COMPLETED", "evaluation_status": "EVALUATED",
                           "checkpoint_path": str(directory.relative_to(tmp_path)), "metrics": val_metrics})
    candidates[1]["comparison_to_c03"] = {"status": "COMPARABLE", "direction": "candidate_minus_c03",
                                          "deltas": {k: c04[k] - c03[k] for k in ("acc", "nll", "brier", "ece")}}
    candidates[1]["coverage_analysis"] = {"ratio": {"S1": 2, "S3": 1}, "splits": {"train": {
        "records_by_class": {"S1": 4, "S3": 2}, "independent_units_by_class": {"S1": 4, "S3": 1}}},
        "encoding": {"encoded_records": 6}}
    write_json(tmp_path / "our-project/results/training/kev/candidate_queue.json", candidates)
    matrix_path = tmp_path / "our-project/planning/CANDIDATE_PROGRESSION_MATRIX.md"
    matrix_path.parent.mkdir(parents=True)
    matrix_header = "# 候选推进矩阵\n\n"
    matrix_history = "## 历史\n\n2026-10-24：C03/C04 已完成固定 Val，原有科学对照记录继续保留。\n"
    matrix_path.write_text(matrix_header + matrix_history, encoding="utf-8")
    originals = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file() and p != matrix_path}
    history = collector.build_training_history(tmp_path, processes={})
    original_validation = copy.deepcopy({r["key"]: r["validation"] for r in history["runs"]})
    # Other Val identities, counts, protocols and loss definitions stay separate.
    reference = next(r for r in history["runs"] if r["run_id"] == "F06_S1")
    for field, value in (("validation_set", "other-fixed-val"), ("items", 562),
                         ("protocol", "other-protocol"), ("loss_definition", "other-loss")):
        other = copy.deepcopy(reference)
        other["run_id"] = other["key"] = "OTHER_" + field
        if field in ("validation_set", "items"):
            other["validation"][0][field] = value
        else:
            other[field] = value
        history["runs"].append(other)
    live = {"kev": {"run_id": "KEV-V8-C04", "status": "COMPLETED", "evaluation_status": "EVALUATED",
                    "is_training": False}, "process": {"kev": {}}}
    summary = collector.write_training_research_report(history, tmp_path, live)
    report = json.loads((tmp_path / summary["data"]).read_text())
    rows = {r["run_id"]: r for r in report["observations"]}
    f06 = rows["F06"]
    assert (f06["best_loss_epoch"]["epoch"], f06["best_loss_epoch"]["loss"], f06["selected_epoch_physical"]) == (1, .6002, False)
    assert (f06["best_accuracy_epoch"]["epoch"], f06["best_accuracy_epoch"]["accuracy"], f06["best_accuracy_physical"]) == (2, .6863, True)
    assert rows["F06_S1"]["best_loss_epoch"]["loss"] == .5936
    assert (rows["F07"]["best_loss_epoch"]["epoch"], rows["F07"]["best_accuracy_epoch"]["epoch"]) == (1, 1)
    for rid in ("F07", "F08", "F09"):
        assert all(not c["physical"] and not c["pruned"] and c["ever_saved"] is None for c in rows[rid]["checkpoints"])
    for rid in ("AUX_S2", "AUX_S3"):
        assert rows[rid]["comparison"]["control_key"] is None
        assert rows[rid]["comparison"]["accuracy_delta"] is None
        assert rows[rid]["comparison"]["loss_delta"] is None
    trend = next(g for g in report["objective_trends"] if g["family"] == "laya" and g["stream"] == "S1"
                 and g["validation_set"] == "same-fixed-val" and g["items"] == 561
                 and g["protocol"] == NEW_PROTOCOL_VERSION and g["loss_definition"] == "soft-ce")
    assert [r["run_id"] for r in trend["observations"]] == ["F06", "F06_S1", "F07", "F08", "F09"]
    loaded = next(c for c in report["loadable_candidates"] if c["run_id"] == "F06")
    assert loaded["epoch"] == 2 and loaded["is_best_loss_epoch"] is False and loaded["is_best_accuracy_epoch"] is True
    assert [loaded["primary_validation"][k] for k in ("accuracy", "loss", "brier", "ece")] == [.6863, .6017, .415, .0549]
    assert "其他Epoch" in f06["candidate_role"]
    assert all(c["run_id"] not in ("F07", "F08", "F09", "F06_S1") for c in report["loadable_candidates"])
    kev_trend = next(g for g in report["objective_trends"] if g["protocol"] == "KEV_FORMAL_LORA")
    assert len(kev_trend["observations"]) == 2
    for rid, metrics in (("KEV-V8-C03", c03), ("KEV-V8-C04", c04)):
        assert [rows[rid]["best_loss_epoch"][k] for k in ("accuracy", "nll", "brier", "ece")] == [metrics[k] for k in ("acc", "nll", "brier", "ece")]
        assert rows[rid]["validation_coverage"]["evaluated_questions"] == 9330
    assert rows["KEV-V8-C04"]["evaluation_seconds"] == 2982.712651308626
    assert rows["KEV-V8-C04"]["comparison_to_c03"] == candidates[1]["comparison_to_c03"]
    assert rows["KEV-V8-C04"]["supervision"] == ["S1", "S3"]
    assert rows["KEV-V8-C04"]["sampling"]["ratio_label"] == "2:1"
    assert rows["KEV-V8-C04"]["sampling"]["materialized_per_epoch_by_stream"] == {"S1": 4, "S3": 2}
    assert rows["KEV-V8-C04"]["exposure"]["materialized_records"] == 6
    assert rows["KEV-V8-C04"]["exposure"]["encoded_records"] == 6
    assert rows["KEV-V8-C04"]["exposure"]["trained_records"] is None
    assert rows["KEV-V8-C03"]["exposure"]["materialized_records"] is None
    assert collector.public_training_record({str(tmp_path / "data"): {"raw_output": "private", "error": "private", "n": 6}}, tmp_path) == {"data": {"n": 6}}
    current = report["training_eta"]["current"]["kev"]
    assert (current["remaining_training_seconds"], current["validation_seconds"], current["estimated_finish_at"]) == (0, 0, None)
    assert current["validation_in_finish_estimate"] is False
    assert len(current["validation_samples"]) == 2
    assert "median of 2" in current["validation_method"]
    assert all(r["validation"] == original_validation[r["key"]] for r in history["runs"] if r["key"] in original_validation)
    assert all(p.read_bytes() == content for p, content in originals.items())
    markdown = (tmp_path / summary["report"]).read_text()
    assert "| F06 | 最低S1 Loss | 1 | 0.6738 | 0.6002 | 0.4141 | 0.0247 | False |" in markdown
    assert "| F06 | 最高S1 Accuracy | 2 | 0.6863 | 0.6017 | 0.415 | 0.0549 | True |" in markdown
    assert "0.6863/0.6017/N/A/0.415/0.0549" in markdown
    assert "9330" in markdown and "2982.712651308626" in markdown
    assert "COMPLETED" in markdown and "EVALUATED" in markdown
    assert "当前F07为两Epoch" not in markdown and "Kev运行中的旧dispatcher" not in markdown
    assert "节省229小时" not in markdown and "节省40小时" not in markdown and "节省26小时" not in markdown
    begin, end = "<!-- KEV_LIVE_CANDIDATES_BEGIN -->", "<!-- KEV_LIVE_CANDIDATES_END -->"
    for _ in range(2):
        matrix = matrix_path.read_text(encoding="utf-8")
        assert matrix.count(begin) == matrix.count(end) == 1
        assert matrix.startswith(matrix_header.rstrip("\n")) and matrix.endswith(matrix_history)
        for cid, metrics in (("KEV-V8-C03", c03), ("KEV-V8-C04", c04)):
            row = next(line for line in matrix.splitlines() if line.startswith("| " + cid + " |"))
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            assert [float(value) for value in cells[4:8]] == [metrics[k] for k in ("acc", "nll", "brier", "ece")]
            assert cells[8] == "9330"
        if _ == 0:
            collector.write_training_research_report(history, tmp_path, live)
    assert all(p.read_bytes() == content for p, content in originals.items())


def test_collector_training_eta_original_budget(tmp_path):
    from scripts import fetch_live_status as collector
    history = {"runs": [{"root": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F01", "run_id": "F01",
        "protocol": NEW_PROTOCOL_VERSION,
        "status": "COMPLETED", "family": "laya", "sampling": {"mode": "FULL_COVERAGE"},
        "exposure": {"trained_records": 1000}, "training_seconds": 100,
        "supervision_classes": ["S1", "S2", "S3"], "source": "run.json"}],
        "data_census": {"layers": {"L1": {"S1": 1000}}}, "experiment_plans": {"kev_queue": []}}
    plans = {"full_coverage": {"F08": {"supervision_classes": ["S1"], "layer_fractions": {"L1": .25}, "epochs": 2}}, "matrix": {}}
    rows = [{"category": "full_coverage", "status": "ELIGIBLE", "run_id": "F08", "materialized": False}]
    estimate = collector.training_eta(history, plans, {}, rows)
    assert estimate["groups"][0]["remaining_records"] == 500
    assert estimate["groups"][0]["training_seconds"] == 50
    assert estimate["totals"]["planned_executable_runs"] == 1
    assert estimate["current"]["laya"]["remaining_training_seconds"] is None
    kev_val = {"stream": "clean", "validation_set": "same-kev-val", "items": 9330, "source": "val_metrics.json"}
    history["runs"] += [{"family": "kev", "root": "runs/" + rid, "run_id": rid, "protocol": "KEV_FORMAL_LORA",
                         "validation": [kev_val], "evaluation_status": "EVALUATED", "evaluation_seconds": seconds}
                        for rid, seconds in (("C03", 3000), ("C04", 3200))]
    history["runs"].append({"family": "kev", "root": "models/imported", "run_id": "imported", "protocol": "KEV_IMPORTED_LORA",
                            "validation": [kev_val], "evaluation_status": "EVALUATED", "evaluation_seconds": 9000})
    live = {"kev": {"run_id": "C04", "status": "TRAINING", "step": 5, "total_steps": 10,
                    "samples_per_s": 2, "is_training": True}, "process": {"kev": {"train_pid": 123, "batch": 1, "accum": 4}}}
    current = collector.training_eta(history, plans, live, rows)["current"]["kev"]
    assert current["remaining_training_seconds"] == 10 and current["validation_seconds"] == 3100
    assert current["validation_in_finish_estimate"] is True
    assert [s["run_id"] for s in current["validation_samples"]] == ["C03", "C04"]
    assert current["validation_method"] == "median of 2 same fixed Kev Val observed durations"
    path = tmp_path / "status.json"
    collector.atomic_json(path, {"loss": float("nan")})
    assert json.loads(path.read_text()) == {"loss": None}


def test_collector_live_terminal_results_and_observed_rate(tmp_path, monkeypatch):
    from scripts import fetch_live_status as collector
    monkeypatch.setattr(collector, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(collector, "_PROGRESS", {})
    directory = tmp_path / "runs/KEV-EXAMPLE/formal_run"
    directory.mkdir(parents=True)
    (directory / "training_metrics.json").write_text(json.dumps({
        "optimizer_steps": 17, "records_seen": 68, "wall_seconds": 30}))
    (directory.parent / "cursor.json").write_text(json.dumps({
        "step": 10, "consumed_records": 40, "loss": .4, "updated_at": "2026-10-20T04:00:00Z"}))
    history = {"runs": [{"family": "kev", "training_kind": "FORMAL_LORA", "root": "runs/KEV-EXAMPLE/formal_run",
        "run_id": "C03", "status": "COMPLETED", "training_status": "COMPLETED", "epochs": 1, "planned_epochs": 1,
        "evaluation_status": "FAILED", "queue_status": "FAILED", "failure_reason": "Validation evaluation failed",
        "protocol": "KEV_FORMAL_LORA"}]}
    result = collector._live_family("kev", {}, history)
    assert (result["step"], result["consumed_records"], result["loss_step"]) == (17, 68, 10)
    assert result["evaluation_status"] == "FAILED" and result["training_seconds"] == 30
    assert result["samples_per_s"] == 68 / 30
    assert result["speed_step"] == 17

    laya = tmp_path / "runs/LAYA/F07"
    laya.mkdir(parents=True)
    cursor = {"step_count": 10, "consumed_items": 100, "updated_at": "2026-10-20T04:00:00Z"}
    (laya / "cursor.json").write_text(json.dumps(cursor))
    monkeypatch.setattr(collector, "age_seconds", lambda t: 20 if t.endswith("00Z") else 10)
    proc = {"laya": {"train_pid": 123, "run_id": "F07", "out_root": "runs/LAYA", "elapsed_s": 30}}
    history = {"runs": [{"family": "laya", "run_id": "F07", "root": "runs/LAYA/F07", "protocol": "example"}]}
    assert collector._live_family("laya", proc, history)["samples_per_s"] is None
    cursor.update(step_count=20, consumed_items=200, updated_at="2026-10-20T04:00:10Z")
    (laya / "cursor.json").write_text(json.dumps(cursor))
    assert collector._live_family("laya", proc, history)["samples_per_s"] == 10

    (directory.parent / "train.log").write_text("ep0 step 10/17 loss 0.400 2.0s/rec\n")
    proc = {"kev": {"train_pid": 456, "out": str(directory), "elapsed_s": 30}}
    history = {"runs": [{"family": "kev", "run_id": "C04", "root": "runs/KEV-EXAMPLE/formal_run",
                          "protocol": "KEV_FORMAL_LORA", "planned_epochs": 1}]}
    live = collector._live_family("kev", proc, history)
    assert live["samples_per_s"] == .5 and live["speed_step"] == 10
    assert live["consumed_records"] is None
    assert live["speed_source"] == "runs/KEV-EXAMPLE/train.log"
    assert collector._live_family("kev", proc, history)["samples_per_s"] == .5
    with (directory.parent / "train.log").open("a") as stream:
        stream.write("ep0 step 15/17 loss 0.300 2.5s/rec\n")
    live = collector._live_family("kev", proc, history)
    assert live["samples_per_s"] == .4 and live["speed_step"] == 15


def test_collector_kev_validation_appended_rows(tmp_path, monkeypatch):
    from scripts import fetch_live_status as collector
    monkeypatch.setattr(collector, "_VAL_CACHE", {})
    monkeypatch.setattr(collector, "age_seconds", lambda value: 15 if value else None)
    directory = tmp_path / "formal_run"
    attempt = directory / "val_metrics/attempt_0002"
    attempt.mkdir(parents=True)
    data = tmp_path / "val.jsonl"
    data.write_text(json.dumps({"questions": {"a": {}, "b": {}}}) + "\n"
                    + json.dumps({"questions": {"c": {}}}) + "\n")
    result = {"evaluation_status": "EVALUATING", "validation_set": str(data),
              "report_path": str(attempt / "report.json"), "attempt_id": 2, "device": "cuda"}
    (directory / "val_metrics.json").write_text(json.dumps(result))
    predictions = attempt / "predictions.jsonl"
    first = json.dumps({"rows": [{}, {}]}) + "\n"
    second = json.dumps({"rows": [{}]})
    predictions.write_text(first + second)
    candidate = {"evaluation_attempts": [{"started_at": "2026-10-20T08:00:00Z"}]}
    observed = collector.live_kev_validation(directory, candidate)
    assert observed["validation_coverage"] == {"requested_records": 2, "requested_questions": 3,
                                               "evaluated_records": 1, "evaluated_questions": 2}
    assert observed["evaluation_seconds"] == 15 and observed["validation_metrics"] == {}
    assert collector.live_kev_validation(directory, candidate)["validation_coverage"] == observed["validation_coverage"]
    with predictions.open("a") as stream:
        stream.write("\n")
    assert collector.live_kev_validation(directory, candidate)["validation_coverage"]["evaluated_records"] == 2
    result.update(evaluation_status="EVALUATED", clean={"acc": .75}, duration_sec=20,
                  coverage={"evaluated_records": 2, "requested_records": 2})
    (directory / "val_metrics.json").write_text(json.dumps(result))
    complete = collector.live_kev_validation(directory, candidate)
    assert complete["validation_metrics"]["acc"] == .75 and complete["evaluation_seconds"] == 20
    (directory.parent / "cursor.json").write_text("{}")
    assert collector.kev_cursor(directory) == directory.parent / "cursor.json"
    (directory / "cursor.json").write_text("{}")
    assert collector.kev_cursor(directory) == directory / "cursor.json"


def _kev_candidate(root, number, **updates):
    cid = f"KEV-V8-C{number:02d}"
    name = f"KEV-RUN-{number:02d}"
    checkpoint = f"runs/{name}/checkpoint"
    metrics = {"evaluation_status": "EVALUATED", "exit_code": 0,
               "validation_protocol": "KEV_FIXED_VAL_JSONL", "dataset_split": "val", "test_used": False,
               "validation_set": "data/kev/公开数据/val.jsonl", "report_path": checkpoint + "/report.json",
               "evaluated_at": "2026-10-25T00:00:00Z",
               "clean": {"n": 9330, "nll": 1.0, "acc": .6, "brier": .5, "ece": .05},
               "coverage": {"requested_records": 8436, "evaluated_records": 8436,
                            "requested_questions": 9330, "evaluated_questions": 9330,
                            "rejected_records": 0, "truncated_records": 0}}
    candidate = {"candidate_id": cid, "name": name, "checkpoint_path": checkpoint,
                 "status": "COMPLETED", "training_status": "COMPLETED", "evaluation_status": "EVALUATED",
                 "init_from": "models/kev-4b-adapter", "data_path": "data/kev/公开数据/train.jsonl",
                 "metrics": metrics, "loss": .8, "finished_at": "2026-10-25T00:00:00Z",
                 "training_parameters": {"lr": 2e-5, "lora": 16, "epochs": 1, "batch": 1, "accum": 4,
                                         "seed": 42, "dtype": "bf16", "head_lr": 0, "weight_decay": .01,
                                         "lora_targets": "all", "max_state": 384},
                 "training_metrics": {"optimizer_steps": 16857, "records_seen": 67428,
                                      "requested_records": 67428, "wall_seconds": 100}}
    candidate["recipe"] = {"run_id": name, "candidate_id": cid, "source_git_sha": "recorded-project-revision",
                           "upstream_git_sha": "recorded-kev-revision", "base_model": "models/base",
                           "base_revision": "recorded-model-revision", "init_from": candidate["init_from"],
                           "parent_init_source": {"revision": "recorded-parent-revision"},
                           "data_path": candidate["data_path"], "data_identity": {"version": "fixed-project-data"},
                           "validation_set": metrics["validation_set"], "test_used": False,
                           "command": ["python", "-m", "kev.train"], "checkpoint_path": checkpoint,
                           "retraining": "Use the recorded initialization, data and parameters"}
    directory = root / checkpoint
    directory.mkdir(parents=True)
    (directory / "head.pt").write_bytes(b"pointer-weights")
    (directory / "adapter_model.safetensors").write_bytes(b"adapter-weights")
    (directory / "training_config.json").write_text(json.dumps(candidate["training_parameters"]))
    (directory / "train.log").write_text("recorded loss .8")
    candidate.update(updates)
    return candidate


def _kev_queue(root):
    queue = [_kev_candidate(root, n) for n in (3, 4, 10, 20, 21, 22, 23, 24)]
    for c in queue[3:]:
        c["retention_group"] = "HOMOLOGOUS_CONTINUATION"
        c["metrics"]["clean"].update(nll=1.2 + int(c["candidate_id"][-2:]) / 100,
                                      acc=.55, brier=.6, ece=.08)
    return queue


def test_kev_selection_formula_directions_and_reference_scales(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    result = compute_kev_selection_score(reference, reference)
    assert result["score"] == 100 and result["version"] == "KEV_FIXED_VAL_FOUR_METRIC_V1"
    assert result["weights"] == {"nll": .45, "acc": .30, "brier": .15, "ece": .10}
    for metric, delta in (("nll", -.1), ("acc", .1), ("brier", -.1), ("ece", -.01)):
        improved = copy.deepcopy(reference)
        improved["clean"][metric] += delta
        score = compute_kev_selection_score(improved, reference)
        assert score["score"] > 100
        expected = 100 * (1 + result["weights"][metric] * abs(delta) / result["scales"][metric])
        assert abs(score["score"] - expected) < 1e-10
    reference["clean"].update(ece=0, nll=0, brier=0, acc=1)
    result = compute_kev_selection_score(reference, reference)
    assert result["score"] == 100
    assert result["scales"] == {"nll": 1e-6, "acc": .05, "brier": 1e-6, "ece": .05}


def test_kev_selection_incomplete_or_invalid_results_never_rank(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    invalid = []
    for key in ("acc", "nll", "brier", "ece"):
        for value in (None, float("nan"), float("inf"), True, -.1):
            item = copy.deepcopy(reference)
            item["clean"][key] = value
            invalid.append(item)
    for key, value in (("requested_records", 1264), ("evaluated_records", 8435),
                       ("evaluated_questions", 9329), ("rejected_records", 1), ("truncated_records", 1)):
        item = copy.deepcopy(reference)
        item["coverage"][key] = value
        invalid.append(item)
    for key, value in (("dataset_split", "test"), ("validation_set", "other/val.jsonl"),
                       ("test_used", True), ("evaluation_status", "PARTIAL"), ("exit_code", 1)):
        invalid.append({**copy.deepcopy(reference), key: value})
    for item in invalid:
        result = compute_kev_selection_score(item, reference)
        assert result["score"] is None and result["rank"] is None
        assert compute_kev_selection_score(reference, item)["score"] is None


def test_kev_selection_targets_policy_and_original_report_agree(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    reference["report"] = {"clean": copy.deepcopy(reference["clean"]),
                           "coverage": copy.deepcopy(reference["coverage"]),
                           "tasks": {"custom_choice": {"n": 8436}, "custom_score": {"n": 894}},
                           "metric_policy": {"version": 2, "nll_floor": 1e-9}}
    assert compute_kev_selection_score(reference, reference)["score"] == 100
    other = copy.deepcopy(reference)
    other["report"]["tasks"]["custom_choice"]["n"] -= 1
    assert compute_kev_selection_score(other, reference)["score"] is None
    other = copy.deepcopy(reference)
    other["report"]["metric_policy"]["version"] = 1
    assert compute_kev_selection_score(other, reference)["score"] is None
    other = copy.deepcopy(reference)
    other["report"]["clean"]["nll"] = .1
    assert compute_kev_selection_score(other, reference)["reason"] == "inconsistent_report_clean"


def test_kev_retention_continuation_and_single_s1_group_keep_all(tmp_path):
    queue = [_kev_candidate(tmp_path, n) for n in (3, 4, 10)]
    queue[1]["metrics"]["clean"].update(nll=1.1, ece=.06)
    queue[2]["init_from"] = queue[0]["checkpoint_path"]
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert report["released_bytes"] == 0
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue)
    assert queue[0]["selection"]["score"] == 100
    assert queue[1]["selection"]["score"] < 100
    assert queue[2]["selection"]["group"] == "S1_WEIGHT_ABLATION"
    assert report["groups"]["HOMOLOGOUS_CONTINUATION"]["eligible_runs"] == 2
    assert report["groups"]["S1_WEIGHT_ABLATION"]["eligible_runs"] == 1


def test_kev_retention_group_quota_ties_and_required_control_levels(tmp_path):
    queue = _kev_queue(tmp_path)
    for c in queue[3:]:
        c["metrics"]["clean"] = copy.deepcopy(queue[0]["metrics"]["clean"])
    first = evaluate_kev_retention(queue, project_root=tmp_path)
    second = evaluate_kev_retention(list(reversed(queue)), project_root=tmp_path)
    assert first["groups"] == second["groups"]
    group = first["groups"]["HOMOLOGOUS_CONTINUATION"]
    assert group["eligible_runs"] == 7 and group["core_quota"] == 2
    assert group["ranked_ids"] == ["KEV-V8-C03", "KEV-V8-C04", "KEV-V8-C20", "KEV-V8-C21",
                                    "KEV-V8-C22", "KEV-V8-C23", "KEV-V8-C24"]
    queue += [_kev_candidate(tmp_path, n) for n in (5, 6, 7, 8, 9)]
    # The original state contrasts remain necessary even with a shared display label.
    queue[-5]["control_variant"] = queue[-4]["control_variant"] = "STATE_PAIR"
    evaluate_kev_retention(queue, project_root=tmp_path)
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue[-5:])


def test_kev_retention_report_persists_fields_without_removing_weights(tmp_path):
    queue = _kev_queue(tmp_path)
    saved = []
    report = evaluate_kev_retention(queue, project_root=tmp_path, persist=lambda q: saved.append(copy.deepcopy(q)))
    assert len(saved) == 1 and saved[0][-1]["selection"]["rank"] is not None
    assert report["released_bytes"] == 0
    low = queue[-1]
    assert low["retention"]["status"] == "PENDING"
    assert low["retention"]["planned_action"] == "PRUNED_LOW_SCORE"
    assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_apply_only_weights_with_real_bytes_and_repeat(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    directory = tmp_path / low["checkpoint_path"]
    originals = {p: p.read_bytes() for p in directory.iterdir() if p.suffix in (".json", ".log")}
    allocated = sum((directory / n).stat().st_blocks * 512 for n in ("head.pt", "adapter_model.safetensors"))
    logical = sum((directory / n).stat().st_size for n in ("head.pt", "adapter_model.safetensors"))
    queue_path = tmp_path / "candidate_queue.json"
    ledger_path = tmp_path / "candidate_ledger.json"
    snapshots = []
    def persist(q):
        snapshots.append(copy.deepcopy(q))
        queue_path.write_text(json.dumps(q))
        ledger_path.write_text(json.dumps({"candidates": q}))
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    assert snapshots[0][-1]["recipe"] == low["recipe"]
    assert snapshots[0][-1]["retention"]["status"] == "PENDING"
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["released_bytes"] == allocated
    assert low["retention"]["removed_weight_bytes"] == logical
    assert report["released_bytes"] == allocated * 5
    assert directory.is_dir() and all(p.read_bytes() == data for p, data in originals.items())
    assert json.loads(ledger_path.read_text())["candidates"][-1]["retention"]["status"] == "PRUNED_LOW_SCORE"
    pruned_at = low["retention"]["pruned_at"]
    again = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    assert again["released_bytes"] == 0 and low["retention"]["released_bytes"] == 0
    assert low["retention"]["total_released_bytes"] == allocated
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["pruned_at"] == pruned_at


def test_kev_retention_missing_recipe_or_persistence_preserves_weights(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    for missing in ("source_git_sha", "parent_init_source", "data_identity", "base_model", "init_from", "command"):
        value = low["recipe"].pop(missing)
        evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
        assert low["retention"]["status"] == "PENDING"
        assert missing in low["retention"]["reason"]
        assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()
        low["recipe"][missing] = value
    source = low["recipe"]["source_git_sha"]
    low["recipe"]["source_git_sha"] = "N/A"
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and "source_git_sha" in low["retention"]["reason"]
    low["recipe"]["source_git_sha"] = source
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True)
    assert low["retention"]["reason"] == "original_queue_persistence_required"
    def cannot_persist(q):
        raise OSError("original record is not writable")
    import pytest
    with pytest.raises(OSError):
        evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=cannot_persist)
    assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_all_entity_protections_and_pending_metrics(tmp_path):
    queue = _kev_queue(tmp_path)
    queue[3]["status"] = "RUNNING"
    queue[4]["recovery_in_use"] = True
    queue[5]["scientific_representative"] = True
    queue[6]["is_curriculum_parent"] = True
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None,
                                   protected_paths=[queue[7]["checkpoint_path"]])
    assert report["released_bytes"] == 0
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue)
    queue[7]["metrics"]["clean"]["nll"] = None
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert queue[7]["selection"]["score"] is None
    assert queue[7]["retention"]["status"] == "PENDING"
    assert (tmp_path / queue[7]["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_missing_entity_does_not_invent_pruning(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    for name in ("head.pt", "adapter_model.safetensors"):
        (tmp_path / low["checkpoint_path"] / name).unlink()
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING"
    assert low["retention"]["released_bytes"] == 0
    low["weights_saved"] = False
    evaluate_kev_retention(queue, project_root=tmp_path)
    assert low["retention"]["status"] == "NOT_SAVED"


def test_kev_retention_symlink_shared_files_and_outside_runs_preserved(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    directory = tmp_path / low["checkpoint_path"]
    head = directory / "head.pt"
    target = tmp_path / "outside-weight.pt"
    target.write_bytes(head.read_bytes())
    head.unlink()
    head.symlink_to(target)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and target.is_file()
    head.unlink()
    import os
    os.link(target, head)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and head.is_file()
    low["checkpoint_path"] = "outside"
    low["recipe"]["checkpoint_path"] = "outside"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "head.pt").write_bytes(b"not-a-run")
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and (outside / "head.pt").is_file()


def test_kev_retention_partial_entity_requires_original_removal_record(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    (tmp_path / low["checkpoint_path"] / "head.pt").unlink()
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["reason"] == "incomplete_weight_entity_without_removal_record"
    assert low["retention"]["status"] == "PENDING" and low["retention"]["freed_bytes"] == 0
    assert (tmp_path / low["checkpoint_path"] / "adapter_model.safetensors").is_file()


def test_kev_retention_partial_removal_records_only_successful_bytes(tmp_path, monkeypatch):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    head = tmp_path / low["checkpoint_path"] / "head.pt"
    adapter = head.with_name("adapter_model.safetensors")
    head_bytes, adapter_bytes = head.stat().st_blocks * 512, adapter.stat().st_blocks * 512
    original_unlink = Path.unlink
    def unlink(path, *args, **kwargs):
        if path == adapter:
            raise PermissionError("recorded weight cannot be removed")
        return original_unlink(path, *args, **kwargs)
    monkeypatch.setattr(Path, "unlink", unlink)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and adapter.is_file()
    assert low["retention"]["freed_bytes"] == low["retention"]["released_bytes"] == head_bytes
    assert low["retention"]["applied"] is True
    monkeypatch.setattr(Path, "unlink", original_unlink)
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["released_bytes"] == adapter_bytes
    assert low["retention"]["total_released_bytes"] == head_bytes + adapter_bytes
    assert report["freed_bytes"] == report["released_bytes"] == adapter_bytes


def test_kev_retention_c11_original_observations_survive(tmp_path):
    queue = _kev_queue(tmp_path)
    original = {"best_accuracy": "KEV-V8-C03", "best_nll": "KEV-V8-C03", "outstanding": ["KEV-V8-C09"]}
    c11 = {"candidate_id": "KEV-V8-C11", "name": "KEV-V8-VAL-BEST", "candidate_kind": "SELECTION",
           "status": "PENDING", "selection": copy.deepcopy(original)}
    queue.append(c11)
    report = evaluate_kev_retention(queue, project_root=tmp_path)
    assert all(c11["selection"][k] == v for k, v in original.items())
    assert c11["selection"]["score"] is None and c11["retention"]["status"] == "NOT_SAVED"
    assert report["applied"] is False and report["freed_bytes"] == 0


def _kev_ratio_queue(root):
    queue = [_kev_candidate(root, n) for n in (3, 4)]
    for index in range(16):
        cid, variant = f"KEV-V8-R{index + 1:02d}", f"R{index + 1:02d}"
        c = _kev_candidate(root, index + 20, candidate_id=cid, control_variant=variant,
                           retention_group="KEV_TYPED_COVERAGE_V1", init_from=queue[0]["checkpoint_path"])
        c["recipe"].update(candidate_id=cid, init_from=c["init_from"], base_revision=None)
        c["metrics"]["clean"]["nll"] += (index + 1) * .01
        queue.append(c)
    return queue


def test_kev_retention_sixteen_ratio_names_keep_three_and_prune_fixtures(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    reversed_report = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == reversed_report["groups"]
    assert first["decisions"] == reversed_report["decisions"]
    group = first["groups"]["KEV_TYPED_COVERAGE_V1"]
    assert (group["eligible_runs"], group["core_quota"]) == (16, 3)
    removed = [tmp_path / c["checkpoint_path"] / name for c in queue[5:]
               for name in ("head.pt", "adapter_model.safetensors")]
    allocated = sum(p.stat().st_blocks * 512 for p in removed)
    originals = {p: p.read_bytes() for c in queue for p in (tmp_path / c["checkpoint_path"]).iterdir()
                 if p.suffix in (".json", ".log")}
    snapshots = []
    def persist(candidates):
        snapshots.append(copy.deepcopy(candidates))
        (tmp_path / "candidate_queue.json").write_text(json.dumps(candidates))
        (tmp_path / "candidate_ledger.json").write_text(json.dumps({"candidates": candidates}))
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    kept = [c["candidate_id"] for c in queue[2:] if c["retention"]["status"] in ("RETAINED", "PROTECTED")]
    assert kept == ["KEV-V8-R01", "KEV-V8-R02", "KEV-V8-R03"]
    assert all(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[5:])
    assert all(not p.exists() for p in removed)
    assert report["released_bytes"] == allocated and report["removed_weight_bytes"] > 0
    assert snapshots[0][-1]["recipe"]["base_revision"] is None
    assert snapshots[0][-1]["retention"]["planned_action"] == "PRUNED_LOW_SCORE"
    assert all(c["recipe"]["base_revision"] is None and c["retention"]["base_revision"] == "N/A"
               and c["retention"]["retraining_limitations"] for c in queue[2:])
    assert all((tmp_path / c["checkpoint_path"]).is_dir() for c in queue)
    assert all(p.read_bytes() == content for p, content in originals.items())
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue[:2])


def test_kev_retention_ratios_explicit_science_parent_and_active_protections(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    queue[-1]["scientific_representative"] = True
    queue[-3]["is_serving"] = True
    queue[-4].update(status="RUNNING", training_status="RUNNING", metrics={})
    queue[-5]["checkpoint_id"] = sorted(OLD_CORE_CHECKPOINT_IDS)[0]
    child = _kev_candidate(tmp_path, 90, status="PENDING", training_status="QUEUED", metrics={},
                           init_from=queue[-2]["checkpoint_path"])
    queue.append(child)
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    second = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == second["groups"] and first["decisions"] == second["decisions"]
    assert first["groups"]["KEV_TYPED_COVERAGE_V1"]["core_quota"] == 3
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    for c in queue[13:18]:
        assert c["retention"]["status"] == "PROTECTED"
        assert (tmp_path / c["checkpoint_path"] / "head.pt").is_file()
    assert "base_import_serving_or_parent_path" in queue[16]["retention"]["protection_reasons"]
    assert "scientific_representative" in queue[17]["retention"]["protection_reasons"]
    assert any(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[5:13])


def test_kev_retention_low_rank_s1_only_r01_remains_required(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    r01 = queue[2]
    r01["metrics"]["clean"]["nll"] = 2.0
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    reversed_report = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == reversed_report["groups"] and first["decisions"] == reversed_report["decisions"]
    assert first["groups"]["KEV_TYPED_COVERAGE_V1"]["ranked_ids"][-1] == "KEV-V8-R01"
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert r01["selection"]["rank"] == 16 and r01["retention"]["status"] == "PROTECTED"
    assert (tmp_path / r01["checkpoint_path"] / "head.pt").is_file()
    assert report["groups"]["KEV_TYPED_COVERAGE_V1"]["core_quota"] == 3
    kept = [c["candidate_id"] for c in queue[2:] if c["retention"]["status"] in ("RETAINED", "PROTECTED")]
    assert kept == ["KEV-V8-R01", "KEV-V8-R02", "KEV-V8-R03", "KEV-V8-R04"]
    assert all(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[6:])


def test_kev_retention_unknown_revision_alone_preserves_recipe_and_allows_pruning(tmp_path):
    for index, revision in enumerate((None, "N/A", "", "UNKNOWN", "missing")):
        root = tmp_path / str(index)
        queue = _kev_queue(root)
        low = queue[-1]
        if revision == "missing":
            low["recipe"].pop("base_revision")
        else:
            low["recipe"]["base_revision"] = revision
        recipe = copy.deepcopy(low["recipe"])
        evaluate_kev_retention(queue, project_root=root, apply=True, persist=lambda q: None)
        assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
        assert low["recipe"] == recipe
        assert low["retention"]["base_revision"] == "N/A"
        assert low["retention"]["retraining_limitations"]


if __name__ == "__main__":
    test_retention_ordering()
    test_two_phase_cleanup_protects_running_run()
    test_two_phase_cleanup_protects_dual_pool_and_pinned()
    import pytest
    with pytest.MonkeyPatch.context() as monkeypatch:
        test_sync_run_best_symlink_scientific_integrity(monkeypatch)


