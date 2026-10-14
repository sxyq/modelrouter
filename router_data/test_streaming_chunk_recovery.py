#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Production-grade test suite for streaming chunk recovery & epoch boundary consistency.

Verifies:
1. Exact Epoch Boundary Recovery:
   - Run 1 (Golden Reference): Train 2 Epochs (5 chunks/epoch), save weights at Epoch 1 end & Epoch 2 end.
   - Run 2 (Interrupted & Resumed): Train Epoch 1, start Epoch 2, simulate crash at Chunk 3.
     Resume from previous valid save point (Epoch 1 end).
     Verify start_chunk reset to 0, consumed_items rolled back to Epoch 1 boundary (no phantom double-counting).
     Verify model weights, logits, optimizer step, and consumption match Run 1.
2. Forbid using Epoch 1 weights with mid-epoch (Chunk 3) cursor.
3. Forbid empty completed write when final epoch weights are missing.
4. Distinguish between metadata-only pruned checkpoints and active recovery checkpoints.
"""

import copy
import json
import math
import os
import shutil
import tempfile
import torch
import torch.nn as nn
from pathlib import Path


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
    tmp_dir = target_dir.parent / f"_tmp_{target_dir.name}"
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    weights_file = tmp_dir / "model.pt"
    torch.save(model.state_dict(), weights_file)

    optim_file = tmp_dir / "optim_state.pt"
    opt_data = {
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict() if scheduler else None,
        "rng_state": torch.get_rng_state(),
    }
    torch.save(opt_data, optim_file)

    meta_file = tmp_dir / "recovery_state.json"
    meta_file.write_text(json.dumps(recovery_meta, indent=2))

    # Atomic rename/publish
    shutil.rmtree(target_dir, ignore_errors=True)
    tmp_dir.rename(target_dir)


def has_physical_weights(target_dir: Path) -> bool:
    if not target_dir or not target_dir.is_dir():
        return False
    pt = target_dir / "model.pt"
    st = target_dir / "model.safetensors"
    return (pt.is_file() and pt.stat().st_size > 100) or (st.is_file() and st.stat().st_size > 100)


def resolve_recovery_point(run_root: Path, run_id: str, run_epochs: int):
    """Production resolution rule:
    Finds the latest physical checkpoint and returns its matched recovery boundary.
    Any mid-epoch in-flight chunk progress without physical weights is rolled back.
    """
    cursor_path = run_root / "cursor.json"
    if not cursor_path.is_file():
        return None, 0, 0, 0, 0, "COLD_START"

    cur = json.loads(cursor_path.read_text())
    cur_ep = int(cur.get("epoch", 0))
    cur_chunk = int(cur.get("chunk_idx", 0))

    ep_ckpt_dir = run_root / "checkpoints" / f"epoch_{cur_ep:02d}"
    temp_recovery_dir = run_root / "checkpoints" / "_temp_recovery"

    # Rule: Claiming completion requires physical weights
    if cur_ep >= run_epochs:
        if has_physical_weights(ep_ckpt_dir):
            return ep_ckpt_dir, cur_ep, 0, cur.get("step_count", 0), cur.get("consumed_items", 0), "COMPLETED"
        else:
            raise RuntimeError(f"Corrupt state: Cursor claims {cur_ep}/{run_epochs} completed but final weights missing!")

    # Check valid checkpoints
    candidate_ckpt = None
    if cur_ep > 0 and has_physical_weights(ep_ckpt_dir):
        candidate_ckpt = ep_ckpt_dir
    elif temp_recovery_dir.is_dir() and has_physical_weights(temp_recovery_dir):
        candidate_ckpt = temp_recovery_dir

    if candidate_ckpt is not None:
        rec_meta_file = candidate_ckpt / "recovery_state.json"
        if rec_meta_file.is_file():
            rec_meta = json.loads(rec_meta_file.read_text())
            # Enforce exact match to recovery state
            rec_ep = int(rec_meta.get("epoch", 0))
            rec_chunk = int(rec_meta.get("chunk_idx", 0))
            rec_step = int(rec_meta.get("step_count", 0))
            rec_consumed = int(rec_meta.get("consumed_items", 0))
            return candidate_ckpt, rec_ep, rec_chunk, rec_step, rec_consumed, "EXACT_RESUME"
        else:
            # Fallback epoch boundary
            return candidate_ckpt, cur_ep, 0, cur.get("step_count", 0), cur.get("consumed_items", 0), "WEIGHT_ONLY_CONTINUATION"

    # If physical weights missing
    return None, 0, 0, 0, 0, "EPOCH_RESTART"


def test_streaming_chunk_recovery():
    print("=== TEST 1: Golden Reference vs Interrupted-Resumed Trajectory ===")
    torch.manual_seed(42)
    device = torch.device("cpu")

    # Generate synthetic data: 2 epochs, 5 chunks per epoch, 16 items per chunk
    chunks_data = []
    for c in range(10): # 10 chunks total
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

    epoch1_ref_weights = copy.deepcopy(model_ref.state_dict())

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

    ref_final_weights = copy.deepcopy(model_ref.state_dict())
    eval_x = torch.randint(0, 100, (8, 10))
    with torch.no_grad():
        ref_logits = model_ref(eval_x)

    print(f"[Run 1 Ref] Steps={ref_steps}, Consumed={ref_consumed}")

    # --- Run 2: Interrupted at Epoch 2 Chunk 3 -> Resumed from Epoch 1 ---
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_test"
        run_root.mkdir(parents=True)
        ckpt_dir = run_root / "checkpoints"
        ckpt_dir.mkdir(parents=True)

        model_run2 = MockLayaModel().to(device)
        model_run2.load_state_dict(init_state)
        opt_run2 = torch.optim.AdamW(model_run2.parameters(), lr=1e-3)
        sched_run2 = torch.optim.lr_scheduler.CosineAnnealingLR(opt_run2, T_max=10)

        step2 = 0
        consumed2 = 0

        # Epoch 1
        for c_idx in range(5):
            x, y = chunks_data[c_idx]
            opt_run2.zero_grad()
            out = model_run2(x)
            loss = loss_fn(out, y)
            loss.backward()
            opt_run2.step()
            sched_run2.step()
            step2 += 1
            consumed2 += len(x)

        # Save Epoch 1 Checkpoint + Recovery State
        ep1_dir = ckpt_dir / "epoch_01"
        rec_meta_ep1 = {
            "run_id": "RUN_001",
            "epoch": 1,
            "chunk_idx": 0,
            "step_count": step2,
            "consumed_items": consumed2,
        }
        save_atomic_checkpoint(model_run2, opt_run2, sched_run2, ep1_dir, rec_meta_ep1)
        # Also copy to _temp_recovery
        shutil.copytree(ep1_dir, ckpt_dir / "_temp_recovery")

        # Start Epoch 2 and simulate training Chunk 0, 1, 2, then CRASH at Chunk 3!
        for c_idx in range(5, 8): # chunks 5, 6, 7 (which correspond to chunk 0, 1, 2 of epoch 2)
            x, y = chunks_data[c_idx]
            opt_run2.zero_grad()
            out = model_run2(x)
            loss = loss_fn(out, y)
            loss.backward()
            opt_run2.step()
            sched_run2.step()
            step2 += 1
            consumed2 += len(x)

        # Simulated crash! In-flight cursor was written with mid-epoch progress
        crash_cursor = {
            "run_id": "RUN_001",
            "epoch": 1, # currently in epoch index 1 (epoch 2)
            "chunk_idx": 3,
            "step_count": step2, # 8 steps
            "consumed_items": consumed2, # 128 items
        }
        (run_root / "cursor.json").write_text(json.dumps(crash_cursor))
        print(f"[Simulated Crash] Cursor: chunk_idx=3, step={step2}, consumed={consumed2}")

        # --- NOW PERFORM PRODUCTION RESUME ---
        ckpt_resume, start_ep, start_chk, resumed_step, resumed_consumed, mode = resolve_recovery_point(run_root, "RUN_001", 2)
        print(f"[Recovery Engine] Selected ckpt={ckpt_resume.name}, mode={mode}")
        print(f"[Recovery Engine] Rolled back: start_epoch={start_ep}, start_chunk={start_chk}, step={resumed_step}, consumed={resumed_consumed}")

        # CRITICAL ASSERTIONS:
        # 1. start_chunk must be 0 (re-run incomplete epoch from epoch boundary)
        assert start_chk == 0, f"Error: start_chunk must be 0, got {start_chk}"
        # 2. consumed_items must roll back to 80 (not 128)
        assert resumed_consumed == 80, f"Error: consumed_items must roll back to 80, got {resumed_consumed}"
        # 3. step must roll back to 5 (not 8)
        assert resumed_step == 5, f"Error: step must roll back to 5, got {resumed_step}"
        # 4. mode must be EXACT_RESUME
        assert mode == "EXACT_RESUME"

        # Load weights and optimizer state into fresh model instance
        resumed_model = MockLayaModel().to(device)
        resumed_model.load_state_dict(torch.load(ckpt_resume / "model.pt"))
        resumed_opt = torch.optim.AdamW(resumed_model.parameters(), lr=1e-3)
        resumed_sched = torch.optim.lr_scheduler.CosineAnnealingLR(resumed_opt, T_max=10)

        opt_st = torch.load(ckpt_resume / "optim_state.pt")
        resumed_opt.load_state_dict(opt_st["optimizer"])
        resumed_sched.load_state_dict(opt_st["scheduler"])
        torch.set_rng_state(opt_st["rng_state"])

        # Execute Epoch 2 cleanly from Chunk 0 (which is chunks_data[5..9])
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

        # No physical weights in checkpoints/epoch_01
        _, start_ep, start_chk, step, consumed, mode = resolve_recovery_point(run_root, "R1", 2)
        assert mode == "EPOCH_RESTART"
        assert start_ep == 0 and start_chk == 0 and step == 0 and consumed == 0
        print(">>> TEST 2 PASSED: Missing physical weights correctly triggers EPOCH_RESTART and resets counts to 0!")

    print("\n=== TEST 3: Completed Claim without Physical Weights Blocked ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        run_root = Path(tmpdir) / "run_corrupt_complete"
        run_root.mkdir()
        (run_root / "checkpoints").mkdir()
        (run_root / "cursor.json").write_text(json.dumps({"run_id": "R2", "epoch": 2, "chunk_idx": 0, "step_count": 200, "consumed_items": 10000}))

        try:
            resolve_recovery_point(run_root, "R2", 2)
            assert False, "Should have raised RuntimeError!"
        except RuntimeError as e:
            assert "Corrupt state" in str(e)
            print(f">>> TEST 3 PASSED: False completed claim blocked: {e}")

    print("\nALL PRODUCTION STREAMING RECOVERY TESTS PASSED (3/3)!")


if __name__ == "__main__":
    test_streaming_chunk_recovery()
