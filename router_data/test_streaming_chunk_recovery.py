#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Production-grade test suite for streaming chunk recovery & epoch boundary consistency.

Verifies:
1. Exact Epoch Boundary Recovery using production resolve_checkpoint_to_resume:
   - Run 1 (Golden Reference): Train 2 Epochs (5 chunks/epoch), save weights at Epoch 1 end & Epoch 2 end.
   - Run 2 (Interrupted & Resumed): Train Epoch 1, start Epoch 2, simulate crash at Chunk 3.
     Resume from previous valid save point (Epoch 1 end).
     Verify start_chunk reset to 0, consumed_items rolled back to Epoch 1 boundary (no phantom double-counting).
     Verify model weights, logits, optimizer step, and consumption match Run 1.
2. Forbid using Epoch 1 weights with mid-epoch (Chunk 3) cursor.
3. Forbid empty completed write when final epoch weights are missing and run.json is not completed.
4. Correctly recognize completed runs when run.json has status: completed and full history.
5. Strict SHA256 checkpoint weight hash verification in recovery_state.json.
6. Verify optimizer parameter binding and actual weight updates after recovery.
"""

import copy
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
from pathlib import Path
import torch
import torch.nn as nn

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from router_data.laya_batch_train import (
    resolve_checkpoint_to_resume,
    has_physical_weights,
)


class MockLayaModel(nn.Module):
    def __init__(self, vocab_size=100, hidden_dim=32, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.encoder = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.head = nn.Linear(hidden_dim, num_classes)

    def forward(self, input_ids):
        emb = self.embedding(input_ids)
        enc = self.encoder(emb)
        pooled = enc.mean(dim=1)
        return self.head(pooled)


def save_atomic_checkpoint(model, optimizer, scheduler, target_dir: Path, recovery_meta: dict):
    """Mirror production _save_ckpt_with_optim behavior:
    saves weights, optim_state.pt, and recovery_state.json with SHA256 checksum.
    """
    tmp_dir = target_dir.parent / f"_tmp_{target_dir.name}"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    weights_file = tmp_dir / "model.pt"
    torch.save(model.state_dict(), weights_file)

    # Compute SHA256
    h = hashlib.sha256()
    with open(weights_file, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    weight_hash = h.hexdigest()

    optim_file = tmp_dir / "optim_state.pt"
    opt_data = {
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict() if scheduler else None,
        "rng_state": torch.get_rng_state(),
    }
    torch.save(opt_data, optim_file)

    meta = dict(recovery_meta)
    meta["checkpoint_hash"] = weight_hash
    meta["saved_at"] = "2026-10-14T12:00:00Z"
    meta_file = tmp_dir / "recovery_state.json"
    meta_file.write_text(json.dumps(meta, indent=2))

    # Atomic rename/publish
    shutil.rmtree(target_dir, ignore_errors=True)
    tmp_dir.rename(target_dir)


def test_streaming_chunk_recovery():
    print("=== TEST 1: Golden Reference vs Interrupted-Resumed Trajectory ===")
    torch.manual_seed(42)
    device = torch.device("cpu")

    # Generate synthetic data: 2 epochs, 5 chunks per epoch, 16 items per chunk
    chunks_data = []
    for c in range(10):
        x = torch.randint(0, 100, (16, 10))
        y = torch.randint(0, 2, (16,))
        chunks_data.append((x, y))

    # --- Run 1: Golden Reference (Uninterrupted) ---
    model_ref = MockLayaModel().to(device)
    init_state = copy.deepcopy(model_ref.state_dict())

    opt_ref = torch.optim.AdamW(model_ref.parameters(), lr=1e-3)
    sched_ref = torch.optim.lr_scheduler.CosineAnnealingLR(opt_ref, T_max=10)
    loss_fn = nn.CrossEntropyLoss()

    ref_steps = 0
    ref_consumed = 0
    # Epoch 1 (chunks 0..4)
    for c_idx in range(5):
        x, y = chunks_data[c_idx]
        opt_ref.zero_grad()
        out = model_ref(x)
        loss = loss_fn(out, y)
        loss.backward()
        opt_ref.step()
        sched_ref.step()
        ref_steps += 1
        ref_consumed += len(x)

    # Save Golden Epoch 1
    golden_ep1_state = copy.deepcopy(model_ref.state_dict())
    golden_ep1_opt = copy.deepcopy(opt_ref.state_dict())
    golden_ep1_sched = copy.deepcopy(sched_ref.state_dict())

    # Epoch 2 (chunks 5..9)
    for c_idx in range(5, 10):
        x, y = chunks_data[c_idx]
        opt_ref.zero_grad()
        out = model_ref(x)
        loss = loss_fn(out, y)
        loss.backward()
        opt_ref.step()
        sched_ref.step()
        ref_steps += 1
        ref_consumed += len(x)

    # Evaluation probe
    eval_x = torch.randint(0, 100, (32, 10))
    with torch.no_grad():
        ref_logits = model_ref(eval_x)

    # --- Run 2: Interrupted at Epoch 2 Chunk 3 and Resumed via production resolver ---
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "RUN_RESUME"
        run_root.mkdir()
        ckroot = run_root / "checkpoints"
        ckroot.mkdir()

        # Step 2.1: Model trains Epoch 1
        model_resumed = MockLayaModel().to(device)
        model_resumed.load_state_dict(init_state)
        opt_resumed = torch.optim.AdamW(model_resumed.parameters(), lr=1e-3)
        sched_resumed = torch.optim.lr_scheduler.CosineAnnealingLR(opt_resumed, T_max=10)

        step_r = 0
        consumed_r = 0
        for c_idx in range(5):
            x, y = chunks_data[c_idx]
            opt_resumed.zero_grad()
            out = model_resumed(x)
            loss = loss_fn(out, y)
            loss.backward()
            opt_resumed.step()
            sched_resumed.step()
            step_r += 1
            consumed_r += len(x)

        # Save Epoch 1 checkpoint atomically with metadata
        ep1_dir = ckroot / "epoch_01"
        rec_meta_ep1 = {
            "run_id": "RUN_RESUME",
            "epoch": 1,
            "chunk_idx": 0,
            "step_count": step_r,
            "consumed_items": consumed_r,
            "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
            "history": [{"epoch": 1, "train_loss": 0.5}],
        }
        save_atomic_checkpoint(model_resumed, opt_resumed, sched_resumed, ep1_dir, rec_meta_ep1)

        # Save cursor at Epoch 1 completion
        cursor_data = {
            "run_id": "RUN_RESUME",
            "epoch": 1,
            "chunk_idx": 0,
            "step_count": step_r,
            "consumed_items": consumed_r,
        }
        (run_root / "cursor.json").write_text(json.dumps(cursor_data))

        # Step 2.2: Simulate Epoch 2 crash at Chunk 3
        for c_idx in range(5, 8):
            x, y = chunks_data[c_idx]
            opt_resumed.zero_grad()
            out = model_resumed(x)
            loss = loss_fn(out, y)
            loss.backward()
            opt_resumed.step()
            sched_resumed.step()
            step_r += 1
            consumed_r += len(x)

            # Cursor advanced to mid-epoch Chunk 3
            cursor_data = {
                "run_id": "RUN_RESUME",
                "epoch": 1,
                "chunk_idx": (c_idx - 5) + 1,
                "step_count": step_r,
                "consumed_items": consumed_r,
            }
            (run_root / "cursor.json").write_text(json.dumps(cursor_data))

        print(f"[Simulated Crash] Cursor: epoch=1, chunk=3, step={step_r}, consumed={consumed_r}")
        assert step_r == 8
        assert consumed_r == 128

        # Step 2.3: Production recovery resolution
        ckpt_resume, start_ep, start_chk, resumed_step, resumed_consumed, mode, history = resolve_checkpoint_to_resume(
            run_root=run_root,
            run_id="RUN_RESUME",
            run_epochs=2,
        )

        print(f"[Production Resume] mode={mode}, ckpt={ckpt_resume.name if ckpt_resume else None}, start_ep={start_ep}, start_chk={start_chk}, step={resumed_step}, consumed={resumed_consumed}")

        assert ckpt_resume == ep1_dir
        assert start_ep == 1
        assert start_chk == 0, f"Error: start_chunk must be 0, got {start_chk}"
        assert resumed_consumed == 80, f"Error: consumed_items must roll back to 80, got {resumed_consumed}"
        assert resumed_step == 5, f"Error: step must roll back to 5, got {resumed_step}"
        assert mode == "STREAMING_EXACT_RESUME"
        assert len(history) == 1

        # Load weights and optimizer state into fresh model instance
        resumed_model = MockLayaModel().to(device)
        resumed_model.load_state_dict(torch.load(ckpt_resume / "model.pt"))
        resumed_opt = torch.optim.AdamW(resumed_model.parameters(), lr=1e-3)
        resumed_sched = torch.optim.lr_scheduler.CosineAnnealingLR(resumed_opt, T_max=10)

        opt_st = torch.load(ckpt_resume / "optim_state.pt")
        resumed_opt.load_state_dict(opt_st["optimizer"])
        resumed_sched.load_state_dict(opt_st["scheduler"])
        torch.set_rng_state(opt_st["rng_state"])

        # Execute Epoch 2 cleanly from Chunk 0
        for c_idx in range(5, 10):
            x, y = chunks_data[c_idx]
            resumed_opt.zero_grad()
            out = resumed_model(x)
            loss = loss_fn(out, y)
            loss.backward()
            resumed_opt.step()
            resumed_sched.step()
            resumed_step += 1
            resumed_consumed += len(x)

        # Verification against Golden Reference:
        with torch.no_grad():
            resumed_logits = resumed_model(eval_x)

        logit_diff = (resumed_logits - ref_logits).abs().max().item()
        param_diff = max((p1 - p2).abs().max().item() for p1, p2 in zip(resumed_model.parameters(), model_ref.parameters()))

        print(f"[Verification] Max Logit Diff vs Ref: {logit_diff:.6e}")
        print(f"[Verification] Max Param Diff vs Ref: {param_diff:.6e}")
        print(f"[Verification] Final Steps: {resumed_step} (Ref: {ref_steps})")
        print(f"[Verification] Final Consumed: {resumed_consumed} (Ref: {ref_consumed})")

        assert logit_diff == 0.0, f"Logit diff must be 0, got {logit_diff}"
        assert param_diff == 0.0, f"Param diff must be 0, got {param_diff}"
        assert resumed_step == ref_steps
        assert resumed_consumed == ref_consumed
        print(">>> TEST 1 PASSED: Bit-exact recovery from crash across streaming chunks!")

    print("\n=== TEST 2: Missing Physical Weights Detection ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_missing"
        run_root.mkdir()
        (run_root / "checkpoints").mkdir()
        (run_root / "cursor.json").write_text(json.dumps({"run_id": "R1", "epoch": 1, "chunk_idx": 5, "step_count": 100, "consumed_items": 5000}))

        _, start_ep, start_chk, step, consumed, mode, _ = resolve_checkpoint_to_resume(run_root, "R1", 2)
        assert mode == "EPOCH_RESTART"
        assert start_ep == 0 and start_chk == 0 and step == 0 and consumed == 0
        print(">>> TEST 2 PASSED: Missing physical weights correctly triggers EPOCH_RESTART and resets counts to 0!")

    print("\n=== TEST 3: Completed Claim without Physical Weights or Completed run.json Blocked ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_corrupt_complete"
        run_root.mkdir()
        (run_root / "checkpoints").mkdir()
        (run_root / "cursor.json").write_text(json.dumps({"run_id": "R2", "epoch": 2, "chunk_idx": 0, "step_count": 200, "consumed_items": 10000}))

        try:
            resolve_checkpoint_to_resume(run_root, "R2", 2)
            assert False, "Should have raised RuntimeError!"
        except RuntimeError as e:
            assert "Corrupt state" in str(e)
            print(f">>> TEST 3 PASSED: False completed claim blocked: {e}")

    print("\n=== TEST 4: Legitimate Completed Run with METADATA_ONLY Final Epoch Accepted ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_completed_metadata_only"
        run_root.mkdir()
        (run_root / "checkpoints").mkdir()
        (run_root / "cursor.json").write_text(json.dumps({"run_id": "R_META", "epoch": 2, "chunk_idx": 0, "step_count": 200, "consumed_items": 10000}))
        run_meta_data = {
            "run_id": "R_META",
            "status": "completed",
            "history": [
                {"epoch": 1, "train_loss": 0.6, "retention_status": "METADATA_ONLY"},
                {"epoch": 2, "train_loss": 0.5, "retention_status": "METADATA_ONLY"},
            ],
        }
        (run_root / "run.json").write_text(json.dumps(run_meta_data))

        resolved, ep, chk, step, consumed, mode, hist = resolve_checkpoint_to_resume(run_root, "R_META", 2)
        assert mode == "COMPLETED"
        assert ep == 2
        print(">>> TEST 4 PASSED: Legitimate completed run with pruned METADATA_ONLY weights recognized as COMPLETED!")

    print("\n=== TEST 5: SHA256 Hash Matching and Integrity Verification ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_hash_test"
        run_root.mkdir()
        ckpt_dir = run_root / "checkpoints" / "epoch_01"
        m = MockLayaModel()
        opt = torch.optim.AdamW(m.parameters(), lr=1e-3)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=10)
        save_atomic_checkpoint(m, opt, sched, ckpt_dir, {"run_id": "R_HASH", "epoch": 1, "chunk_idx": 0, "step_count": 10, "consumed_items": 100})

        # Verify hash matches actual file
        rec_meta = json.loads((ckpt_dir / "recovery_state.json").read_text())
        h = hashlib.sha256()
        with open(ckpt_dir / "model.pt", "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        real_hash = h.hexdigest()
        assert rec_meta["checkpoint_hash"] == real_hash
        print(f">>> TEST 5 PASSED: Checkpoint SHA256 verified ({real_hash[:16]}...)!")

    print("\n=== TEST 6: Real Parameter Value Updates Verified After Resume ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_param_update"
        run_root.mkdir()
        ckpt_dir = run_root / "checkpoints" / "epoch_01"
        m = MockLayaModel()
        opt = torch.optim.AdamW(m.parameters(), lr=1e-3)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=10)
        save_atomic_checkpoint(m, opt, sched, ckpt_dir, {"run_id": "R_UPDATE", "epoch": 1, "chunk_idx": 0, "step_count": 10, "consumed_items": 100})

        # Resume model
        resumed_m = MockLayaModel()
        resumed_m.load_state_dict(torch.load(ckpt_dir / "model.pt"))
        before_weight = resumed_m.head.weight.clone()

        resumed_opt = torch.optim.AdamW(resumed_m.parameters(), lr=1e-3)
        resumed_opt.load_state_dict(torch.load(ckpt_dir / "optim_state.pt")["optimizer"])

        # Train 1 step
        x = torch.randint(0, 100, (16, 10))
        y = torch.randint(0, 2, (16,))
        out = resumed_m(x)
        loss = nn.CrossEntropyLoss()(out, y)
        loss.backward()
        resumed_opt.step()

        after_weight = resumed_m.head.weight.clone()
        weight_change = (after_weight - before_weight).abs().max().item()
        assert weight_change > 0.0, "Weight change must be non-zero after optimizer.step()!"
        print(f">>> TEST 6 PASSED: Parameters actively updated after resume (max change={weight_change:.6e})!")

    print("\nALL PRODUCTION STREAMING RECOVERY TESTS PASSED (6/6)!")


if __name__ == "__main__":
    test_streaming_chunk_recovery()
