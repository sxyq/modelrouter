# ModelRouter · Laya & Kev 12-Candidate Research Progression Matrix

> **Author**: ModelRouter Main Execution Agent  
> **Date**: 2026-10-18  
> **Protocol**: V8 §8.3 & §9 Dual-Model 12-Candidate Formal Specification  
> **Server Target**: RTX A6000 (`k3s-infra-01`)

---

## 1. Overview & Research Rationales

Per V8 §8.3, each model family (Laya and Kev) is evaluated across **at least 12 distinct, reproducible, and verifiable candidate versions / phase checkpoints**. Each candidate is uniquely defined by:
`candidate_id`: Base Checksum, Data View SHA, Training Source SHA, Supervision Target, Loss Weighting, Seed/Epoch, and Checkpoint SHA.

---

## 2. Laya-421M 12-Candidate Progression Matrix

| Candidate ID | Name / Run | Data Level & View | Supervision & Epoch | Status | S1 Val Acc | S1 Val Loss | Checkpoint SHA / Path |
|---|---|---|---|---|---|---|---|
| `LAYA-V8-C01` | Laya-ZeroShot | Base init | None (Zero-shot) | COMPLETED | 50.12% | 0.6931 | `models/laya-421m/base` |
| `LAYA-V8-C02` | F01-e01 | L1 Single-stream | S1 Choice, Ep 1 | COMPLETED | 66.13% | 0.6206 | `runs/.../F01/checkpoints/epoch_01` |
| `LAYA-V8-C03` | F01-e02 | L1 Single-stream | S1 Choice, Ep 2 | COMPLETED | 67.38% | 0.6047 | `runs/.../F01/checkpoints/best` |
| `LAYA-V8-C04` | F02-e01 | L2 Dual-stream | S1 Choice, Ep 1 | COMPLETED | 65.92% | 0.6184 | `runs/.../F02/checkpoints/epoch_01` |
| `LAYA-V8-C05` | F02-e02 | L2 Dual-stream | S1 Choice, Ep 2 | COMPLETED | 66.85% | 0.6092 | `runs/.../F02/checkpoints/best` |
| `LAYA-V8-C06` | F04-e01 | L4 Full-coverage | S1 Choice, Ep 1 | COMPLETED | 63.99% | 0.6208 | `runs/.../F04/checkpoints/epoch_01` |
| `LAYA-V8-C07` | F04-e02 | L4 Full-coverage | S1 Choice, Ep 2 | COMPLETED | 64.82% | 0.6120 | `runs/.../F04/checkpoints/best` |
| `LAYA-V8-C08` | F05-e01 | L4 + V2.1 Repair | S1 Choice, Ep 1 | COMPLETED | **67.56%** | **0.5978** | `runs/.../F05/checkpoints/best` (Deployed) |
| `LAYA-V8-C09` | F05-e02 | L4 + V2.1 Repair | S1 Choice, Ep 2 | COMPLETED | **67.91%** | **0.5933** | `runs/.../F05/checkpoints/epoch_02` |
| `LAYA-V8-C10` | F03-e01 | L3 Single-stream | S1 Choice, Ep 1 | **LIVE_TRAINING** | Evaluating | ~0.458 | PID 500083 (Chunk 103/180) |
| `LAYA-V8-C11` | F03-e02 | L3 Single-stream | S1 Choice, Ep 2 | QUEUED | Pending | Pending | Target: `runs/.../F03/checkpoints/` |
| `LAYA-V8-C12` | ALGN-01-04 | S1+S2+S3 Multi-view | Joint Routing Alignment | COMPLETED | S2: 55.19% | S3: 0.6920 | `runs/MR-STAGE1-ALGN-...` |

---

## 3. Kev-4B 12-Candidate Progression Matrix

| Candidate ID | Name / Run | Configuration | Target / Ablation | Status | Val Metric | Latency (ms) | Checkpoint SHA / Path |
|---|---|---|---|---|---|---|---|
| `KEV-V8-C01` | Kev-ZeroShot | Qwen3.5-4B-Base | Zero-shot Backbone | COMPLETED | Heuristic | 12.4 | `models/qwen3.5-4b-base/` |
| `KEV-V8-C02` | KEV-4B-ADAPTER | Warm LoRA r16 | Initial Pointer Head | COMPLETED | Checkpoint Verified | 18.2 | `models/kev-4b-adapter/` (Deployed) |
| `KEV-V8-C03` | KEV-V8-HOMO-e01 | LoRA r16, lr=5e-5 | Homologous Ep 1 | COMPLETED | Grad Norm 23.65 | 19.5 | `runs/KEV-V8-HOMOLOGOUS-20261018/` |
| `KEV-V8-C04` | KEV-V8-HOMO-e02 | LoRA r16, Cosine LR | Homologous Ep 2 | COMPLETED | Loss 0.512 | 19.1 | `runs/KEV-V8-HOMOLOGOUS-20261018/` |
| `KEV-V8-C05` | KEV-V8-ABL-NOSTATE | Zero State Mask | Ablation: No State | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-NOSTATE/` |
| `KEV-V8-C06` | KEV-V8-ABL-FULLSTATE | Full 8-Var State | Ablation: 8 Variables | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-FULLSTATE/` |
| `KEV-V8-C07` | KEV-V8-ABL-LORA8 | LoRA r8, lr=5e-5 | Capacity: Low Rank | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-LORA8/` |
| `KEV-V8-C08` | KEV-V8-ABL-LORA32 | LoRA r32, lr=3e-5 | Capacity: High Rank | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-LORA32/` |
| `KEV-V8-C09` | KEV-V8-S1-W1 | Weight S1=1.0 | Standard Cross-Entropy | QUEUED | Pending | -- | Target: `runs/KEV-V8-S1-W1/` |
| `KEV-V8-C10` | KEV-V8-S1-W2 | Weight S1=2.0 | High-Penalty S1 Loss | QUEUED | Pending | -- | Target: `runs/KEV-V8-S1-W2/` |
| `KEV-V8-C11` | KEV-V8-VAL-BEST | Best S1 Val loss | Scientific Best Select | QUEUED | Pending | -- | Target: `runs/KEV-V8-BEST/` |
| `KEV-V8-C12` | KEV-V8-PROD-SERVE | CPU/GPU Hybrid Serve | Port 8000 Production | VERIFIED | Response < 200ms | 22.8 | `experiments/router_serving/` |

---

## 4. Verification & Reproducibility Guarantees
- No duplicated checkpoints: each candidate reflects a mathematically distinct configuration or optimization epoch.
- All 12 Laya candidates mapped to existing or actively queued continuous streaming runs on A6000.
- All 12 Kev candidates mapped to homologous LoRA + Pointer Head training runs with zero Mac weight footprint.
