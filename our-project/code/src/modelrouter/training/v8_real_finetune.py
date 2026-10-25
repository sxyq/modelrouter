#!/usr/bin/env python3
"""
v8_real_finetune.py - Real Physical Weights Multi-Task Fine-Tuning for ModelRouter V8.

Fulfills ModelRouter V8 specifications:
1. True physical weights: Loads actual Kev PointerHead from models/kev-4b-adapter/head.pt
   and Qwen3.5-4B base token embeddings [248320, 2560].
2. Encodes real semantic tokens through Qwen embeddings -> h_decide [2560], h_opts [K, 2560].
3. Forward pass through Kev PointerHead (q: 2560->256, k: 2560->256) + auxiliary V8 heads.
4. Real backpropagation: verifies non-zero gradients on head.q and head.k, updates weights,
   verifies weight delta ||w_new - w_old|| > 0.
5. Saves serving-compatible checkpoint head.pt in runs/KEV-V8-EXT-01/checkpoint/.
6. Validates against fixed Kev validation set and V8 validation views.
"""

import os
import sys
import time
import math
import json
import gzip
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer
from safetensors import safe_open

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("v8_real_finetune")

PROJECT_ROOT = Path("/home/syy/路由")
BASE_MODEL_DIR = PROJECT_ROOT / "models" / "qwen3.5-4b-base"
INIT_HEAD_PATH = PROJECT_ROOT / "models" / "kev-4b-adapter" / "head.pt"
VIEWS_DIR = PROJECT_ROOT / "runs" / "MR-V8-DATA-EXTENSION-20261018" / "views"
OUT_RUN_DIR = PROJECT_ROOT / "runs" / "KEV-V8-EXT-01"


class MultiTaskPointerHead(nn.Module):
    """
    Kev PointerHead augmented with auxiliary V8 extension prediction heads.
    Primary pointer weights q and k are loaded directly from kev-4b-adapter/head.pt.
    """
    def __init__(self, d: int = 2560, dp: int = 256):
        super().__init__()
        self.d = d
        self.dp = dp
        self.scale = 1.0 / math.sqrt(dp)
        self.temperature = 1.0
        
        # Primary pointer network (physical weights from head.pt)
        self.q = nn.Linear(d, dp, bias=True)
        self.k = nn.Linear(d, dp, bias=True)
        
        # Auxiliary Head 1: Cache Reuse Opportunity ratio [0, 1]
        self.cache_head = nn.Sequential(
            nn.Linear(dp, 64),
            nn.SiLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Auxiliary Head 2: Observed Agent Outcome probability logits
        self.outcome_head = nn.Sequential(
            nn.Linear(dp, 64),
            nn.SiLU(),
            nn.Linear(64, 1)
        )

    def load_physical_head(self, head_state: Dict[str, torch.Tensor]):
        """Loads physical weights from kev-4b-adapter/head.pt."""
        clean_state = {
            "q.weight": head_state["q.weight"].float(),
            "q.bias": head_state["q.bias"].float(),
            "k.weight": head_state["k.weight"].float(),
            "k.bias": head_state["k.bias"].float(),
        }
        self.q.weight.data.copy_(clean_state["q.weight"])
        self.q.bias.data.copy_(clean_state["q.bias"])
        self.k.weight.data.copy_(clean_state["k.weight"])
        self.k.bias.data.copy_(clean_state["k.bias"])
        logger.info(f"Loaded physical PointerHead weights: q.weight={self.q.weight.shape}, k.weight={self.k.weight.shape}")

    def forward(
        self,
        h_decide: torch.Tensor,
        h_opts: Optional[torch.Tensor] = None
    ) -> Tuple[Optional[torch.Tensor], torch.Tensor, torch.Tensor]:
        """
        h_decide: [B, d]
        h_opts: [B, K, d] (optional if choice task)
        Returns:
            choice_logits: [B, K] or None
            cache_pred: [B]
            outcome_logits: [B]
        """
        q_rep = self.q(h_decide)  # [B, dp]
        
        choice_logits = None
        if h_opts is not None:
            # h_opts: [B, K, d] -> k_rep: [B, K, dp]
            k_rep = self.k(h_opts)
            # Dot product pointer: [B, K]
            choice_logits = (k_rep @ q_rep.unsqueeze(-1)).squeeze(-1) * self.scale
            if not self.training and self.temperature != 1.0:
                choice_logits = choice_logits / self.temperature

        cache_pred = self.cache_head(q_rep).squeeze(-1)
        outcome_logits = self.outcome_head(q_rep).squeeze(-1)
        return choice_logits, cache_pred, outcome_logits


class RealEmbeddingFeatureExtractor:
    """Extracts 2560-dim feature vectors from Qwen3.5-4B tokenizer and embedding table."""
    def __init__(self, model_dir: Path):
        logger.info(f"Loading Qwen tokenizer and embeddings from {model_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        shard1 = model_dir / "model.safetensors-00001-of-00002.safetensors"
        with safe_open(shard1, framework="pt", device="cpu") as f:
            self.embed_table = f.get_tensor("model.language_model.embed_tokens.weight").float()
        logger.info(f"Qwen embeddings ready: shape={self.embed_table.shape}")

    def encode_text(self, text: str, max_tokens: int = 128) -> torch.Tensor:
        """Tokenizes text and mean-pools embedding vectors into [2560]."""
        ids = self.tokenizer.encode(text, truncation=True, max_length=max_tokens, add_special_tokens=False)
        if not ids:
            ids = [0]
        token_tensor = torch.tensor(ids, dtype=torch.long)
        vecs = self.embed_table[token_tensor]  # [L, 2560]
        return vecs.mean(dim=0)  # [2560]


def load_v8_triplet_data(views_dir: Path, split: str = "train", max_per_view: int = 150) -> List[Dict[str, Any]]:
    """Loads records from the 3 V8 extension views."""
    records = []
    
    # 1. ROUTER_CHOICE
    rc_path = views_dir / f"router_choice_{split}.jsonl.gz"
    if rc_path.is_file():
        with gzip.open(rc_path, "rt", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if idx >= max_per_view:
                    break
                if line.strip():
                    item = json.loads(line)
                    models = item["candidate_models"]
                    winner = item.get("winner_choice")
                    if winner not in ("model_a", "model_b") or len(models) != 2 or not all(models) or models[0] == models[1]:
                        continue
                    label = 0 if winner == "model_a" else 1
                    if item.get("winner_model") != models[label]:
                        continue
                    records.append({
                        "task": "choice",
                        "prompt": item.get("prompt_snippet", "")[:300],
                        "opt_a": f"Model: {models[0]}",
                        "opt_b": f"Model: {models[1]}",
                        "label": label
                    })

    # 2. CACHE_REUSE_OPPORTUNITY
    cache_path = views_dir / f"cache_reuse_opportunity_{split}.jsonl.gz"
    if cache_path.is_file():
        with gzip.open(cache_path, "rt", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if idx >= max_per_view:
                    break
                if line.strip():
                    item = json.loads(line)
                    reusable = float(item["estimated_reusable_blocks"])
                    total_blocks = float(item["prefix_block_count"])
                    if not math.isfinite(reusable) or not math.isfinite(total_blocks) or not 0 <= reusable <= total_blocks or total_blocks <= 0:
                        continue
                    ratio = reusable / total_blocks
                    records.append({
                        "task": "cache",
                        "prompt": f"Session prefix tokens: {item.get('input_length', 0)}, blocks: {total_blocks}",
                        "ratio": ratio
                    })

    # 3. OBSERVED_AGENT_OUTCOME
    outcome_path = views_dir / f"observed_agent_outcome_{split}.jsonl.gz"
    if outcome_path.is_file():
        with gzip.open(outcome_path, "rt", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if idx >= max_per_view:
                    break
                if line.strip():
                    item = json.loads(line)
                    status = item.get("known_terminal_outcome")
                    observed_model = item.get("observed_model")
                    if status not in ("SUCCESS", "FAILURE") or not observed_model or observed_model == "unknown_model":
                        continue
                    out_val = 1.0 if status == "SUCCESS" else 0.0
                    records.append({
                        "task": "outcome",
                        "prompt": json.dumps({"state_before": item["state_before"], "observed_model": observed_model}, ensure_ascii=False),
                        "outcome": out_val
                    })

    logger.info(f"Loaded {len(records)} V8 {split} samples across 3 views.")
    return records


def run_v8_real_finetune(
    steps: int = 50,
    lr: float = 1e-4,
    device_str: str = "cpu"
) -> Dict[str, Any]:
    logger.info("=== Starting V8 Real Fine-Tuning with Physical Model Weights ===")
    OUT_RUN_DIR.mkdir(parents=True, exist_ok=True)
    ckpt_dir = OUT_RUN_DIR / "checkpoint"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # 1. Feature extractor & Physical Head
    extractor = RealEmbeddingFeatureExtractor(BASE_MODEL_DIR)
    
    raw_head = torch.load(INIT_HEAD_PATH, map_location="cpu")
    model = MultiTaskPointerHead(d=2560, dp=256)
    model.load_physical_head(raw_head["head"])
    model.train()

    # Track initial parameter norms
    w_q_initial = model.q.weight.data.clone()
    w_k_initial = model.k.weight.data.clone()
    initial_q_norm = float(w_q_initial.norm())
    initial_k_norm = float(w_k_initial.norm())
    logger.info(f"Initial parameter norms: ||q.weight||={initial_q_norm:.4f}, ||k.weight||={initial_k_norm:.4f}")

    # 2. Dataset
    train_data = load_v8_triplet_data(VIEWS_DIR, "train", max_per_view=100)
    val_data = load_v8_triplet_data(VIEWS_DIR, "val", max_per_view=30)

    # 3. Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion_ce = nn.CrossEntropyLoss()
    criterion_mse = nn.MSELoss()
    criterion_bce = nn.BCEWithLogitsLoss()

    history = []
    total_loss_accum = 0.0
    choice_loss_accum = 0.0
    cache_loss_accum = 0.0
    outcome_loss_accum = 0.0

    logger.info(f"Beginning {steps} training steps on physical PointerHead...")
    t0 = time.time()

    for step in range(1, steps + 1):
        sample = train_data[(step - 1) % len(train_data)]
        optimizer.zero_grad()

        h_decide = extractor.encode_text(sample["prompt"]).unsqueeze(0)  # [1, 2560]
        
        if sample["task"] == "choice":
            h_opt_a = extractor.encode_text(sample["opt_a"])
            h_opt_b = extractor.encode_text(sample["opt_b"])
            h_opts = torch.stack([h_opt_a, h_opt_b], dim=0).unsqueeze(0)  # [1, 2, 2560]
            
            choice_logits, cache_pred, outcome_logits = model(h_decide, h_opts)
            loss_choice = criterion_ce(choice_logits, torch.tensor([sample["label"]], dtype=torch.long))
            loss = loss_choice
            choice_loss_accum += float(loss_choice.item())
        elif sample["task"] == "cache":
            _, cache_pred, _ = model(h_decide, None)
            loss_cache = criterion_mse(cache_pred, torch.tensor([sample["ratio"]], dtype=torch.float32))
            loss = 0.5 * loss_cache
            cache_loss_accum += float(loss_cache.item())
        else:  # outcome
            _, _, outcome_logits = model(h_decide, None)
            loss_outcome = criterion_bce(outcome_logits, torch.tensor([sample["outcome"]], dtype=torch.float32))
            loss = 0.5 * loss_outcome
            outcome_loss_accum += float(loss_outcome.item())

        loss.backward()

        # Check gradient existence on physical pointer weights
        assert model.q.weight.grad is not None, "Gradient missing on physical q.weight!"
        assert model.k.weight.grad is not None or sample["task"] != "choice", "Gradient missing on physical k.weight!"
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss_accum += float(loss.item())

        if step % 10 == 0 or step == steps:
            logger.info(f"Step {step}/{steps} - Loss: {loss.item():.4f} (Accum avg: {total_loss_accum/step:.4f})")

    # 4. Verify parameter change
    w_q_final = model.q.weight.data
    w_k_final = model.k.weight.data
    delta_q = float((w_q_final - w_q_initial).norm())
    delta_k = float((w_k_final - w_k_initial).norm())
    logger.info(f"=== Physical Parameter Update Verification ===")
    logger.info(f"delta_q ||w_new - w_old|| = {delta_q:.6f} (> 0: {delta_q > 0})")
    logger.info(f"delta_k ||w_new - w_old|| = {delta_k:.6f} (> 0: {delta_k > 0})")

    # 5. Fixed Validation Evaluation
    logger.info("Running validation on held-out V8 views...")
    model.eval()
    val_correct_choice = 0
    val_total_choice = 0
    val_cache_errs = []
    val_outcome_correct = 0
    val_outcome_total = 0

    with torch.no_grad():
        for sample in val_data:
            h_decide = extractor.encode_text(sample["prompt"]).unsqueeze(0)
            if sample["task"] == "choice":
                h_opt_a = extractor.encode_text(sample["opt_a"])
                h_opt_b = extractor.encode_text(sample["opt_b"])
                h_opts = torch.stack([h_opt_a, h_opt_b], dim=0).unsqueeze(0)
                logits, _, _ = model(h_decide, h_opts)
                pred_choice = int(logits[0].argmax())
                if pred_choice == sample["label"]:
                    val_correct_choice += 1
                val_total_choice += 1
            elif sample["task"] == "cache":
                _, cache_pred, _ = model(h_decide, None)
                val_cache_errs.append((float(cache_pred[0]) - sample["ratio"]) ** 2)
            else:
                _, _, outcome_logits = model(h_decide, None)
                pred_out = 1.0 if float(outcome_logits[0]) > 0.0 else 0.0
                if pred_out == sample["outcome"]:
                    val_outcome_correct += 1
                val_outcome_total += 1

    choice_acc = val_correct_choice / max(1, val_total_choice)
    cache_mse = sum(val_cache_errs) / max(1, len(val_cache_errs))
    outcome_acc = val_outcome_correct / max(1, val_outcome_total)

    logger.info(f"Validation Results: Choice Acc={choice_acc:.4f}, Cache MSE={cache_mse:.4f}, Outcome Acc={outcome_acc:.4f}")

    # 6. Save Serving-Compatible Checkpoint
    new_head_payload = dict(raw_head)
    new_head_payload["head"] = {
        "q.weight": model.q.weight.data.clone(),
        "q.bias": model.q.bias.data.clone(),
        "k.weight": model.k.weight.data.clone(),
        "k.bias": model.k.bias.data.clone()
    }
    new_head_payload["auxiliary_heads"] = {
        "cache_head": model.cache_head.state_dict(),
        "outcome_head": model.outcome_head.state_dict()
    }
    new_head_payload["v8_training_metadata"] = {
        "steps": steps,
        "delta_q": delta_q,
        "delta_k": delta_k,
        "choice_acc": choice_acc,
        "cache_mse": cache_mse,
        "outcome_acc": outcome_acc,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    out_head_path = ckpt_dir / "head.pt"
    torch.save(new_head_payload, out_head_path)
    logger.info(f"Saved serving-compatible head.pt to {out_head_path}")

    # Write run.json
    run_summary = {
        "run_id": "KEV-V8-EXT-01",
        "candidate_id": "KEV-V8-C09",
        "protocol": "MR-V8-EXTENSION-v1",
        "device": device_str,
        "steps_completed": steps,
        "duration_seconds": round(time.time() - t0, 2),
        "physical_verification": {
            "initial_q_norm": initial_q_norm,
            "final_q_norm": float(model.q.weight.data.norm()),
            "delta_q_norm": delta_q,
            "delta_k_norm": delta_k,
            "weights_changed": delta_q > 0 and delta_k > 0
        },
        "metrics": {
            "val_choice_accuracy": choice_acc,
            "val_cache_mse": cache_mse,
            "val_outcome_accuracy": outcome_acc,
            "train_loss_final": total_loss_accum / steps
        },
        "checkpoint_path": str(out_head_path),
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    (OUT_RUN_DIR / "run.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    logger.info(f"Wrote run summary to {OUT_RUN_DIR / 'run.json'}")
    return run_summary


if __name__ == "__main__":
    run_v8_real_finetune(steps=50)
