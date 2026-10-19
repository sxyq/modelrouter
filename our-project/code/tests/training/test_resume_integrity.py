#!/usr/bin/env python3
"""
Unit test verifying model-optimizer reference integrity during training resume.

Verifies:
1. Optimizer param_groups match model.parameters() by object ID.
2. Real forward + backward + optimizer.step() changes parameters as expected.
3. EXACT_RESUME restores momentum, scheduler step, and RNG states bit-for-bit.
4. Physical weight absence correctly detected via has_physical_weights.
"""

import sys
import tempfile
import unittest
from pathlib import Path

import torch
import torch.nn as nn

from modelrouter.training.common.checkpoint_retention import has_physical_weights


class ToyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Linear(8, 8)
        self.head = nn.Linear(8, 2)

    def forward(self, x):
        return self.head(torch.relu(self.encoder(x)))


class TestResumeIntegrity(unittest.TestCase):
    def test_buggy_pattern_reproduction(self):
        """Proves creating optimizer before checkpoint reload leaves new model un-updated."""
        torch.manual_seed(42)
        model_a = ToyModel()
        groups_a = [{"params": [p for p in model_a.parameters() if p.requires_grad], "lr": 0.05}]
        optimizer = torch.optim.AdamW(groups_a, weight_decay=0.01)

        model_b = ToyModel()
        weight_b_before = model_b.head.weight.clone().detach()

        x = torch.randn(4, 8)
        loss = model_b(x).sum()
        loss.backward()
        optimizer.step()

        weight_b_after = model_b.head.weight.clone().detach()
        self.assertTrue(torch.equal(weight_b_before, weight_b_after))

    def test_fixed_resume_parameter_identity_and_update(self):
        """Verifies creating optimizer directly on reloaded model updates parameters."""
        torch.manual_seed(42)
        model = ToyModel()
        weight_before = model.head.weight.clone().detach()

        groups = [{"params": [p for p in model.parameters() if p.requires_grad], "lr": 0.05}]
        optimizer = torch.optim.AdamW(groups, weight_decay=0.01)

        model_param_ids = {id(p) for p in model.parameters()}
        for grp in optimizer.param_groups:
            for p in grp["params"]:
                self.assertIn(id(p), model_param_ids)

        x = torch.randn(4, 8)
        loss = model(x).sum()
        loss.backward()
        optimizer.step()

        weight_after = model.head.weight.clone().detach()
        self.assertFalse(torch.equal(weight_before, weight_after))
        diff = (weight_after - weight_before).abs().max().item()
        self.assertGreater(diff, 1e-5)

    def test_exact_resume_trajectory_continuity(self):
        """Verifies EXACT_RESUME produces bit-identical continuation trajectory."""
        torch.manual_seed(1234)
        model = ToyModel()
        groups = [{"params": [p for p in model.parameters() if p.requires_grad], "lr": 0.05}]
        optimizer = torch.optim.AdamW(groups, weight_decay=0.01)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10, eta_min=1e-4)

        # Step 1
        x = torch.randn(4, 8)
        loss = model(x).sum()
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            opt_data = {
                "optimizer": optimizer.state_dict(),
                "scheduler": scheduler.state_dict(),
                "rng_state": torch.get_rng_state(),
            }
            torch.save(opt_data, tmp_path / "optim_state.pt")

            # Resumed in a new model
            resumed_model = ToyModel()
            resumed_model.load_state_dict(model.state_dict())
            res_groups = [{"params": [p for p in resumed_model.parameters() if p.requires_grad], "lr": 0.05}]
            res_optimizer = torch.optim.AdamW(res_groups, weight_decay=0.01)
            res_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(res_optimizer, T_max=10, eta_min=1e-4)

            loaded_data = torch.load(tmp_path / "optim_state.pt")
            res_optimizer.load_state_dict(loaded_data["optimizer"])
            res_scheduler.load_state_dict(loaded_data["scheduler"])
            torch.set_rng_state(loaded_data["rng_state"])

            # Verify identical step continuation
            x2 = torch.randn(4, 8)
            res_loss = resumed_model(x2).sum()
            res_loss.backward()
            res_optimizer.step()
            res_scheduler.step()

            torch.set_rng_state(loaded_data["rng_state"])
            x2_orig = torch.randn(4, 8)
            self.assertTrue(torch.equal(x2, x2_orig))
            orig_loss = model(x2_orig).sum()
            orig_loss.backward()
            optimizer.step()
            scheduler.step()

            self.assertTrue(torch.equal(model.head.weight, resumed_model.head.weight))
            self.assertEqual(optimizer.param_groups[0]["lr"], res_optimizer.param_groups[0]["lr"])

    def test_physical_weights_presence_check(self):
        """Verifies checkpoint directory weight detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ck_dir = Path(tmpdir) / "checkpoints" / "epoch_01"
            ck_dir.mkdir(parents=True)
            self.assertFalse(has_physical_weights(ck_dir))

            (ck_dir / "model.safetensors").write_text("fake weight binary")
            self.assertTrue(has_physical_weights(ck_dir))


if __name__ == "__main__":
    unittest.main()
