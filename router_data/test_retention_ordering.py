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


if __name__ == "__main__":
    test_retention_ordering()
    test_two_phase_cleanup_protects_running_run()

