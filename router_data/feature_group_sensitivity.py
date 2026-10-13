"""Feature group sensitivity screening for pre-trained ModelRouter checkpoints.

Runs lightweight forward-pass evaluation on the fixed validation set under 6 mask conditions:
  - Baseline (unmasked)
  - Mask G1: Task & Context Baseline (V1 + V3)
  - Mask G2: Interactive Agent State (V2 + V4)
  - Mask G3: Verification & Recovery (V5)
  - Mask G4: KV Cache & System State (V6)
  - Mask G5: Execution Budget & Provider (V7 + V8)
  - Mask V2: Multi-Agent & Trajectory Coordination (Agent/Coordination)

NOTE: This is a low-cost screening of feature group sensitivity, NOT claimed as a full ablation study.
Full ablation requires multi-seed re-training from scratch on each feature subset.
"""
import argparse
import copy
import json
import os
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_LAYA = str(Path(_ROOT) / "external" / "laya")
if _LAYA not in sys.path:
    sys.path.insert(0, _LAYA)

import torch
from laya.train import (
    items_from_rows,
    load_checkpoint,
    read_data,
    calibration_records,
    evaluate_records,
)
from router_data.checkpoint_retention import classification_metrics_from_records


def mask_row_features(row: dict, group: str) -> dict:
    """Return a masked copy of a validation data row according to feature group."""
    r = copy.deepcopy(row)
    state = r.get("state", {})
    pre = state.get("pre_decision_state")
    if not isinstance(pre, dict):
        return r

    if group == "G1":
        # Task & Context Baseline: V1 + V3
        for k in ["initial_prompt_snippet", "prompt_snippet", "task_domain", "context_chars", "input_length", "prompt_tokens"]:
            if k in pre:
                pre[k] = "" if isinstance(pre[k], str) else 0

    elif group == "G2":
        # Interactive Agent State: V2 + V4
        for k in ["step_index", "prior_tool_calls_count", "agent_framework", "repo"]:
            if k in pre:
                pre[k] = "" if isinstance(pre[k], str) else 0

    elif group == "G3":
        # Verification & Recovery: V5
        for k in ["prior_error_signals_count"]:
            if k in pre:
                pre[k] = 0

    elif group == "G4":
        # KV Cache & Continuity: V6
        for k in ["prefix_hash_sample", "prefix_block_count"]:
            if k in pre:
                pre[k] = "" if isinstance(pre[k], str) else 0

    elif group == "G5":
        # Execution Budget & Provider: V7 + V8
        for k in ["arrival_timestamp", "candidate_model_a", "candidate_model_b", "requested_model", "model_normalized", "reasoning_effort"]:
            if k in pre:
                pre[k] = "" if isinstance(pre[k], str) else 0

    elif group == "V2":
        # Agent & Coordination specifically
        if "step_index" in pre:
            pre["step_index"] = 0
        if "agent_framework" in pre:
            pre["agent_framework"] = ""

    return r


def evaluate_masked_group(model, tok, val_rows: dict, group_name: str, dev: torch.device, max_len=1024, head_max_len=512) -> dict:
    """Evaluate model on validation groups with masked feature set."""
    all_records = []
    group_results = {}

    for g_name, rows in val_rows.items():
        masked_rows = [mask_row_features(r, group_name) for r in rows]
        items, _ = items_from_rows(tok, masked_rows, max_len=max_len, head_max_len=head_max_len)
        with torch.no_grad():
            recs = calibration_records(model, tok, items, dev, max_len, head_max_len)
        all_records.extend(recs)
        ev = evaluate_records(recs, [1.0, 1.0, 1.0], None)
        clf = classification_metrics_from_records(recs)
        group_results[g_name] = {
            "loss": ev.get("loss"),
            "score": ev.get("score"),
            "accuracy": clf.get("accuracy"),
            "macro_f1": clf.get("macro_f1"),
            "samples": len(recs),
        }

    overall_ev = evaluate_records(all_records, [1.0, 1.0, 1.0], None)
    overall_clf = classification_metrics_from_records(all_records)

    return {
        "overall": {
            "loss": overall_ev.get("loss"),
            "score": overall_ev.get("score"),
            "accuracy": overall_clf.get("accuracy"),
            "macro_f1": overall_clf.get("macro_f1"),
            "total_samples": len(all_records),
        },
        "by_supervision_class": group_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Feature group sensitivity screening on fixed validation set.")
    parser.add_argument("--checkpoint-dir", default="runs/MR-FULL-GRADED-TRAINING/B01_C13_QB_PB/checkpoints/best")
    parser.add_argument("--val-dir", default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val")
    parser.add_argument("--out", default="router_data/feature_sensitivity_results.json")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    dev = torch.device(args.device)
    print(f"Loading checkpoint from {args.checkpoint_dir} onto {dev}...", flush=True)
    model, tok, cfg = load_checkpoint(args.checkpoint_dir)
    model.to(dev)
    model.eval()

    val_dir = Path(args.val_dir)
    val_rows = {}
    for g in ("S1", "S2", "S3"):
        fp = val_dir / f"{g}.jsonl"
        if fp.is_file():
            val_rows[g] = read_data(str(fp))
            print(f"Loaded {len(val_rows[g])} rows for {g}", flush=True)

    conditions = [
        ("Baseline", "unmasked"),
        ("G1", "Task & Context Baseline (V1+V3)"),
        ("G2", "Interactive Agent State (V2+V4)"),
        ("G3", "Verification & Recovery (V5)"),
        ("G4", "KV Cache & Continuity (V6)"),
        ("G5", "Execution Budget & Provider (V7+V8)"),
        ("V2", "Multi-Agent Coordination (V2 alone)"),
    ]

    results = {}
    baseline_loss = None
    baseline_acc = None

    for cond_id, desc in conditions:
        print(f"Evaluating condition: {cond_id} ({desc})...", flush=True)
        res = evaluate_masked_group(model, tok, val_rows, cond_id, dev)
        ov = res["overall"]

        by_class = res["by_supervision_class"]
        s1_acc = by_class.get("S1", {}).get("accuracy")
        s2_acc = by_class.get("S2", {}).get("accuracy")
        s3_loss = by_class.get("S3", {}).get("loss")
        ov_loss = ov.get("loss", 0.0)

        if cond_id == "Baseline":
            baseline_loss = ov_loss
            baseline_s1 = s1_acc
            baseline_s2 = s2_acc
            baseline_s3 = s3_loss
            delta_loss = 0.0
            delta_s1 = 0.0
            delta_s2 = 0.0
            delta_s3 = 0.0
        else:
            delta_loss = ov_loss - baseline_loss if baseline_loss is not None else 0.0
            delta_s1 = (s1_acc - baseline_s1) if s1_acc is not None and baseline_s1 is not None else 0.0
            delta_s2 = (s2_acc - baseline_s2) if s2_acc is not None and baseline_s2 is not None else 0.0
            delta_s3 = (s3_loss - baseline_s3) if s3_loss is not None and baseline_s3 is not None else 0.0

        results[cond_id] = {
            "description": desc,
            "metrics": res,
            "overall_loss": ov_loss,
            "s1_accuracy": s1_acc,
            "s2_accuracy": s2_acc,
            "s3_loss": s3_loss,
            "delta_loss_vs_baseline": delta_loss,
            "delta_s1_acc": delta_s1,
            "delta_s2_acc": delta_s2,
            "delta_s3_loss": delta_s3,
        }
        s1_str = f"{s1_acc:.4f}" if s1_acc is not None else "N/A"
        s2_str = f"{s2_acc:.4f}" if s2_acc is not None else "N/A"
        print(f"  -> Loss: {ov_loss:.4f} (Δ: {delta_loss:+.4f}), S1 Acc: {s1_str} (Δ: {delta_s1:+.4f}), S2 Acc: {s2_str} (Δ: {delta_s2:+.4f})", flush=True)

    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf8") as f:
        json.dump(
            {
                "checkpoint": args.checkpoint_dir,
                "val_dir": args.val_dir,
                "device": str(dev),
                "screening_notice": "This is a low-cost screening of feature group sensitivity, NOT claimed as a full ablation study.",
                "conditions": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nFeature group sensitivity screening complete! Saved to {out_p}", flush=True)


if __name__ == "__main__":
    main()
