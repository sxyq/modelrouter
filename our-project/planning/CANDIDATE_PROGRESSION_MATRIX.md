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
| `KEV-V8-C01` | Kev-ZeroShot | Qwen3.5-4B-Base | Zero-shot Backbone | COMPLETED | Heuristic Baseline | 12.4 | `models/qwen3.5-4b-base/` |
| `KEV-V8-C02` | KEV-4B-ADAPTER | Warm LoRA r16 | Initial Pointer Head | COMPLETED | Base Val: 87.26% (NLL 0.516) | 18.2 | `models/kev-4b-adapter/` (Active in Serving) |
| `KEV-V8-C03` | KEV-V8-HOMO-e01 | LoRA r16, lr=2e-5 | Homologous Ep 1 (16,857 steps) | **LIVE_TRAINING** | Step 710 Loss 1.330 | 19.5 | PID 1357764 (`runs/KEV-V8-HOMOLOGOUS-20261018/`) |
| `KEV-V8-C04` | KEV-V8-HOMO-e02 | LoRA r16, Cosine LR | Homologous Ep 2 | QUEUED | Pending (post Ep 1) | -- | Target: `runs/KEV-V8-HOMO-E02/` |
| `KEV-V8-C05` | KEV-V8-ABL-NOSTATE | Zero State Mask | Ablation: No State | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-NOSTATE/` |
| `KEV-V8-C06` | KEV-V8-ABL-FULLSTATE | Full 8-Var State | Ablation: 8 Variables | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-FULLSTATE/` |
| `KEV-V8-C07` | KEV-V8-ABL-LORA8 | LoRA r8, lr=5e-5 | Capacity: Low Rank | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-LORA8/` |
| `KEV-V8-C08` | KEV-V8-ABL-LORA32 | LoRA r32, lr=1e-5 | Capacity: High Rank | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-LORA32/` |
| `KEV-V8-C09` | KEV-V8-S1-W1 | Weight S1=1.0 | Standard Cross-Entropy | QUEUED | Pending | -- | Target: `runs/KEV-V8-S1-W1/` |
| `KEV-V8-C10` | KEV-V8-S1-W2 | Weight S1=2.0 | High-Penalty S1 Loss | QUEUED | Pending | -- | Target: `runs/KEV-V8-S1-W2/` |
| `KEV-V8-C11` | KEV-V8-VAL-BEST | Best S1 Val loss | Scientific Best Select | QUEUED | Pending | -- | Target: `runs/KEV-V8-BEST/` |
| `KEV-V8-C12` | KEV-V8-PROD-SERVE | CPU/GPU Hybrid Serve | Port 8000 Production | VERIFIED | Response Verified | 22.8 | `experiments/router_serving/` |

---

## 4. Verification & Scientific Rigor Guarantees

1. **真实训练与候选版本边界**：严禁将在线 Serving 或处于计划/排队中的候选标注为已完训版本。Kev 当前仅进行单次 1 Epoch 真实训练（`KEV-V8-HOMOLOGOUS-20261018`），每个后续候选必须在安全边界以独立 Run、独立超参、物理 Checkpoint 和固定 Val 逐一产出。
2. **算力竞争与显存余量科学界定**：显存占用 20 GB / 48 GB（余量 ~29 GB）仅保证**不发生 OOM 与显存换页**，但不等于两模型“零算力竞争”；两者在 GPU 流多处理器（SM）、L2 缓存、显存带宽及 PCIe 总线上存在物理竞争，需以单任务独占 vs 双任务并行的 `step/s` 和 `walltime` 进行客观基准测量。
3. **官方 Benchmark 评测真实性准则**：在宿主环境（`LocalHarborSandboxEnvironment`）完成的 Canary 执行仅为通道调试（`LOCAL_HOST_EXPERIMENTAL`）。在未具备官方 Docker 容器沙箱隔离、官方 Harbor Trial ID 及容器内原生未修改 CTRF 评测报告前，严格标记官方 Benchmark 为 `BLOCKED / UNFINISHED`，不得计入学术主表。
4. **V8 三类扩展视图独立性**：新清洗产出的 V8 三类数据视图（`MR-V8-DATA-EXTENSION-20261018`）严禁中途混入正在运行的 F06 或当前 Kev 训练；任何基于该扩展视图的训练均必须建立独立新 Run。
