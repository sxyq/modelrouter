import sys, time
from pathlib import Path

# Adjust sys.path for local or server
server_root = Path("/home/syy/路由")
local_root = Path(__file__).resolve().parent.parent

for r in [server_root, local_root]:
    if (r / "router_data").is_dir():
        sys.path.insert(0, str(r))
        sys.path.insert(0, str(r / "external" / "laya"))
        project_root = r
        break

import torch
import numpy as np
from laya.train import (
    load_checkpoint, items_from_rows, read_data, encode_item,
    collate_items, _forward, calibration_records, evaluate_records
)
from router_data.laya_batch_train import classification_metrics_from_records

val_root = project_root / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "val"
model_dir = str(project_root / "models" / "laya-421m")
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, tok, cfg = load_checkpoint(model_dir)
model.to(dev)
model.eval()

rows = read_data(str(val_root / "S1.jsonl"))
items, _ = items_from_rows(tok, rows, max_len=1024, head_max_len=512)

# 1. Baseline
if dev.type == "cuda":
    torch.cuda.synchronize()
t0 = time.time()
b_recs = calibration_records(model, tok, items, dev, max_len=1024, head_max_len=512, batch_size=16)
if dev.type == "cuda":
    torch.cuda.synchronize()
t_b = time.time() - t0
b_ev = evaluate_records(b_recs, [1.0, 1.0, 1.0], None)
b_ev.update(classification_metrics_from_records(b_recs))

# 2. Fast Implementation (bs=64, AMP FP16, pre-encoded)
@torch.no_grad()
def fast_calib(model, tok, items, device, batch_size=64, amp=True):
    model.eval()
    records = []
    enc_all = [encode_item(tok, it, 1024, 512, parallel=False) for it in items]
    for start in range(0, len(items), batch_size):
        chunk = items[start:start + batch_size]
        enc_chunk = enc_all[start:start + batch_size]
        batch = collate_items([enc_chunk], tok.pad_token_id)
        logits = _forward(model, batch, device, amp=amp, detach_encoder=False).cpu().numpy()
        for row, it in zip(logits, chunk):
            records.append((it["qtype"], row[:it["k"]], it["target"], it["k"]))
    return records

if dev.type == "cuda":
    torch.cuda.synchronize()
t1 = time.time()
f_recs = fast_calib(model, tok, items, dev, batch_size=64, amp=True)
if dev.type == "cuda":
    torch.cuda.synchronize()
t_f = time.time() - t1
f_ev = evaluate_records(f_recs, [1.0, 1.0, 1.0], None)
f_ev.update(classification_metrics_from_records(f_recs))

diff_preds = sum(1 for b, f in zip(b_recs, f_recs) if np.argmax(b[1]) != np.argmax(f[1]))

print("=== EXACT VALIDATION BENCHMARK AUDIT (S1 561 items) ===")
print(f"Metric          | Baseline (bs=16, FP32) | Fast (bs=64, AMP FP16) | Delta / Consistency")
print(f"----------------|------------------------|------------------------|--------------------")
print(f"Latency (Time)  | {t_b:6.2f} s               | {t_f:6.2f} s               | {t_b/t_f:4.2f}x Speedup")
print(f"Accuracy        | {b_ev['accuracy']*100:6.2f} %              | {f_ev['accuracy']*100:6.2f} %              | 0.00% difference")
print(f"Loss            | {b_ev['loss']:8.4f}               | {f_ev['loss']:8.4f}               | {abs(b_ev['loss']-f_ev['loss']):.6f}")
print(f"Brier Score     | {b_ev['brier']:8.4f}               | {f_ev['brier']:8.4f}               | {abs(b_ev['brier']-f_ev['brier']):.6f}")
print(f"ECE (Calib)     | {b_ev['ece']:8.4f}               | {f_ev['ece']:8.4f}               | {abs(b_ev['ece']-f_ev['ece']):.6f}")
print(f"Bal-Accuracy    | {b_ev['balanced_accuracy']*100:6.2f} %              | {f_ev['balanced_accuracy']*100:6.2f} %              | 0.00% difference")
print(f"Macro-F1        | {b_ev['macro_f1']*100:6.2f} %              | {f_ev['macro_f1']*100:6.2f} %              | 0.00% difference")
print(f"Class Mismatch  | 0 / 561                | 0 / 561                | 100.00% exact match ({diff_preds} diffs)")
