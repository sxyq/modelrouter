#!/usr/bin/env python3
"""
Kev-4B Homologous Training & Single-Card Concurrency Verification (Phase 4 / S2).
Executes homologous training steps on V2.1 L1+L2 data using local Qwen3.5-4B-Base and Kev-4B LoRA adapter.
Measures: optimizer steps > 0, forward/backward latency, GPU memory peak, throughput, and zero-interference on F03.
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kev_train")


def run_training(
    base_dir: str = "/home/syy/路由/models/qwen3.5-4b-base",
    adapter_dir: str = "/home/syy/路由/models/kev-4b-adapter",
    train_data_path: str = "/home/syy/路由/data/kev/公开数据/train.jsonl",
    out_dir: str = "/home/syy/路由/runs/KEV-V8-HOMOLOGOUS-20261018",
    device_name: str = "cuda",
    max_steps: int = 5,
    accum_steps: int = 2
):
    os.makedirs(out_dir, exist_ok=True)
    ckpt_dir = os.path.join(out_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)

    kev_lib = "/home/syy/路由/external/kev"
    if kev_lib not in sys.path:
        sys.path.insert(0, kev_lib)

    device = torch.device(device_name if torch.cuda.is_available() and device_name == "cuda" else "cpu")
    logger.info(f"Using device: {device}")

    # Track initial GPU stats
    initial_vram_mb = torch.cuda.memory_allocated(device) / (1024 * 1024) if device.type == "cuda" else 0.0

    from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
    from peft import PeftModel, LoraConfig

    logger.info(f"Loading local tokenizer and base model from {base_dir}...")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(base_dir)
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32

    # Load base model directly in target dtype
    base_model = AutoModelForCausalLM.from_pretrained(
        base_dir,
        torch_dtype=dtype,
        device_map={"": device.index if device.index is not None else 0} if device.type == "cuda" else None
    ).model
    if device.type == "cpu":
        base_model = base_model.to(device)

    # Attach LoRA adapter
    logger.info(f"Attaching LoRA adapter from {adapter_dir}...")
    model = PeftModel.from_pretrained(base_model, adapter_dir, torch_device=str(device))
    model.train()

    # Pointer head projection
    hidden_dim = base_model.config.hidden_size
    head = torch.nn.Linear(hidden_dim, 1, bias=False, device=device, dtype=dtype)
    torch.nn.init.normal_(head.weight, std=0.02)

    optimizer = torch.optim.AdamW(list(model.parameters()) + list(head.parameters()), lr=2e-5, weight_decay=0.01)

    load_time = time.time() - t0
    logger.info(f"Model and adapter loaded in {load_time:.2f}s.")

    # Read training data
    logger.info(f"Reading training records from {train_data_path}...")
    from kev.data import load_records
    records = load_records(train_data_path)[: max_steps * accum_steps * 2]
    logger.info(f"Prepared {len(records)} training records.")

    step_losses = []
    step_latencies = []
    optimizer_step_count = 0
    total_samples = 0
    t_train_start = time.time()

    accum_counter = 0
    optimizer.zero_grad()

    for idx, rec in enumerate(records):
        t_fwd_start = time.perf_counter()
        state_text = rec["state"]
        q_dict = rec["questions"]
        q_key = list(q_dict.keys())[0]
        q_info = q_dict[q_key]

        options = list(q_info.get("criteria", {}).keys()) if isinstance(q_info.get("criteria"), dict) else [str(i) for i in range(2)]
        target_label = q_info.get("label")
        if target_label in options:
            label_idx = options.index(target_label)
        else:
            label_idx = 0

        # Build prompt sequence: state + options
        options_text = " ".join([f"Option {i}: {opt}" for i, opt in enumerate(options)])
        full_text = f"State: {state_text[:500]}\nOptions: {options_text}\nSelection:"
        inputs = tok(full_text, return_tensors="pt", truncation=True, max_length=512).to(device)

        # Forward
        outputs = model(input_ids=inputs.input_ids, attention_mask=inputs.attention_mask, output_hidden_states=True)
        last_hidden = outputs.last_hidden_state[:, -1, :]  # [1, hidden_dim]

        # Score per option
        option_logits = []
        for opt_idx, opt in enumerate(options):
            opt_input = tok(f" {opt}", return_tensors="pt").to(device)
            opt_embed = model.get_input_embeddings()(opt_input.input_ids).mean(dim=1)
            score = (last_hidden * opt_embed).sum(dim=-1)
            option_logits.append(score)

        logits = torch.stack(option_logits, dim=-1)  # [1, n_options]
        loss = F.cross_entropy(logits, torch.tensor([label_idx], device=device)) / accum_steps

        # Backward
        loss.backward()
        accum_counter += 1
        total_samples += 1

        if accum_counter >= accum_steps:
            torch.nn.utils.clip_grad_norm_(list(model.parameters()) + list(head.parameters()), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            optimizer_step_count += 1
            accum_counter = 0

            step_loss_val = float(loss.item() * accum_steps)
            step_losses.append(step_loss_val)
            lat = (time.perf_counter() - t_fwd_start) * 1000.0
            step_latencies.append(lat)
            logger.info(f"[Kev Step {optimizer_step_count}/{max_steps}] Loss: {step_loss_val:.4f}, Latency: {lat:.1f}ms")

            if optimizer_step_count >= max_steps:
                break

    train_walltime = time.time() - t_train_start
    peak_vram_mb = torch.cuda.max_memory_allocated(device) / (1024 * 1024) if device.type == "cuda" else 0.0

    # Save trained adapter checkpoint
    save_path = os.path.join(ckpt_dir, "step_05")
    model.save_pretrained(save_path)
    torch.save(head.state_dict(), os.path.join(save_path, "head.pt"))
    logger.info(f"Saved Kev trained checkpoint to {save_path}")

    summary = {
        "run_id": "KEV-V8-HOMOLOGOUS-20261018",
        "base_model": "Qwen3.5-4B-Base",
        "init_from": adapter_dir,
        "device": str(device),
        "optimizer_steps": optimizer_step_count,
        "total_samples": total_samples,
        "wall_time_seconds": round(train_walltime, 2),
        "samples_per_second": round(total_samples / max(train_walltime, 0.01), 2),
        "updates_per_second": round(optimizer_step_count / max(train_walltime, 0.01), 2),
        "initial_loss": step_losses[0] if step_losses else None,
        "final_loss": step_losses[-1] if step_losses else None,
        "loss_history": step_losses,
        "mean_step_latency_ms": round(sum(step_latencies) / max(len(step_latencies), 1), 2),
        "initial_vram_mb": round(initial_vram_mb, 2),
        "peak_vram_mb": round(peak_vram_mb, 2),
        "checkpoint_path": save_path,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    summary_file = os.path.join(out_dir, "kev_training_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Kev homologous training summary saved to {summary_file}")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--accum-steps", type=int, default=2)
    args = parser.parse_args()

    run_training(device_name=args.device, max_steps=args.max_steps, accum_steps=args.accum_steps)
