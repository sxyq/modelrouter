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

| Candidate ID | Name / Run | Data Level & View | Supervision & Epoch | Status | S1 Val Acc | S1 Val Loss | S1 Brier | Checkpoint SHA / Path |
|---|---|---|---|---|---|---|---|---|
| `LAYA-V8-C01` | Laya-ZeroShot | Base init | None (Zero-shot) | COMPLETED | 50.12% | 0.6931 | 0.5000 | `models/laya-421m/base` |
| `LAYA-V8-C02` | F01-e01 | L1 Single-stream | S1 Choice, Ep 1 | COMPLETED | 66.13% | 0.6206 | 0.4190 | `runs/.../F01/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C03` | F01-e02 | L1 Single-stream | S1 Choice, Ep 2 | COMPLETED | 67.38% | 0.6047 | 0.4074 | `runs/.../F01/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C04` | F02-e01 | L2 Dual-stream | S1 Choice, Ep 1 | COMPLETED | 65.92% | 0.6184 | 0.4172 | `runs/.../F02/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C05` | F02-e02 | L2 Dual-stream | S1 Choice, Ep 2 | COMPLETED | 66.85% | 0.6092 | 0.4110 | `runs/.../F02/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C06` | F04-e01 | L4 Full-coverage | S1 Choice, Ep 1 | COMPLETED | 63.99% | 0.6208 | 0.4285 | `runs/.../F04/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C07` | F04-e02 | L4 Full-coverage | S1 Choice, Ep 2 | COMPLETED | 64.82% | 0.6120 | 0.4215 | `runs/.../F04/epoch_metrics.json` (Pruned) |
| `LAYA-V8-C08` | F05-e01 | L4 + V2.1 Repair | Multi-task S1/S2/S3, Ep 1 | COMPLETED | **67.56%** | **0.5978** | **0.4130** | `runs/.../F05/checkpoints/best` (**Active in Serving**) |
| `LAYA-V8-C09` | F05-e02 | L4 + V2.1 Repair | Multi-task S1/S2/S3, Ep 2 | COMPLETED | **63.64%** | **0.5980** | **0.4142** | `runs/.../F05/run.json` (Pruned; 台账67.91%实为F05_S1) |
| `LAYA-V8-C10` | F03-e01 | L3 Single-stream | S1 Choice, Ep 1 | COMPLETED | 64.71% | 0.6135 | 0.4257 | `runs/.../F03/epoch_metrics.json` (Finished) |
| `LAYA-V8-C11` | F03-e02 | L3 Single-stream | S1 Choice, Ep 2 | COMPLETED | 67.20% | 0.6059 | 0.4190 | `runs/.../F03/epoch_metrics.json` (Finished) |
| `LAYA-V8-C12` | F06-e02 | L4 Full-Coverage 3-Layer | Ep 2 (92,280 steps, 5.9M items) | COMPLETED | **68.09%** | 0.5936 | **0.4079** | `runs/.../F06` (**RETAINED_BEST**, global best S1 Acc) |
| `LAYA-V8-C13` | F07-e02 | L1+L2+L3+L4 Full-Coverage | Ep 2 (151,998 steps, 9.7M items) | COMPLETED | **68.27%** | 0.6076 | 0.4203 | `runs/.../F07` (Target score: 158.44, Pruned) |
| `LAYA-V8-C14` | F08-e02 | L1+L2 Cumulative | Ep 2 (23,002 steps, 1.47M items) | COMPLETED | 67.02% | 0.6123 | 0.4246 | `runs/.../F08` (Target score: 157.55, Pruned) |
| `LAYA-V8-C15` | F09-e02 | L1+L2+L3 Cumulative | Ep 2 (30,826 steps, 1.97M items) | COMPLETED | 66.49% | 0.6100 | 0.4226 | `runs/.../F09` (Target score: 157.99, Pruned) |
| `LAYA-V8-C16` | F10 | L1+L4 Stratified | Ep 1 Chunk 135/152 (17,280/38,732) | **LIVE_TRAINING** | Evaluating | ~0.4934 | PID 4158797 (1.1M items consumed, GPU 93-100%) |

> **关键物理权重区分**：
> - **当前在线 Serving 权重**：`F05/checkpoints/best`（Epoch 1，S1 Acc 67.56%，Loss 0.5978，Brier 0.4130，4.2 GB 实体在盘，Port 8000 活跃加载）；
> - **物理在盘历史最高准确率留存**：`F06-e02`（`RETAINED_BEST`，S1 Acc **68.09%**，Loss 0.5936，Brier 0.4079，在盘保留）；
> - **当前实时持续训练**：`F10`（PID 4158797，Epoch 0 Chunk 135/152，Step 17,280/38,732，已消费 1,105,920 样本，最新 Chunk Loss 0.4934）。

---

## 3. Kev-4B 12-Candidate Progression Matrix

| Candidate ID | Name / Run | Configuration | Target / Ablation | Status | Val Metric (Fixed Val 8,436 items) | Latency (ms) | Checkpoint SHA / Path |
|---|---|---|---|---|---|---|---|
| `KEV-V8-C01` | Kev-ZeroShot | Qwen3.5-4B-Base | Zero-shot Backbone | BASELINE | Heuristic Baseline | 12.4 | `models/qwen3.5-4b-base/` |
| `KEV-V8-C02` | KEV-4B-ADAPTER | Warm LoRA r16 | Initial Pointer Head | COMPLETED | Base Val: 87.26% (NLL 0.516, 1,264 items) | 18.2 | `models/kev-4b-adapter/` (**Active in Serving**) |
| `KEV-V8-C03` | KEV-V8-HOMO-e01 | LoRA r16, lr=2e-5 | Homologous Ep 1 (16,857 steps) | COMPLETED | Clean Acc: **57.16%**, NLL: 1.0796, Brier: 0.5375 | 333.8 (P50) | `runs/KEV-V8-HOMOLOGOUS-20261018/formal_run` (Evaluated) |
| `KEV-V8-C04` | KEV-V8-HOMO-e02 | LoRA r16, lr=1e-5 | Homologous Ep 2 (16,857 steps) | COMPLETED | Clean Acc: **57.12%**, NLL: 1.0873, Brier: 0.5403 | 321.2 (P50) | `runs/KEV-V8-HOMO-e02/checkpoint` (Evaluated, Report on disk) |
| `KEV-V8-C05` | KEV-V8-ABL-NOSTATE | Zero State Mask | Ablation: No State | PENDING | Missing `train_nostate.jsonl` | -- | Target: `runs/KEV-V8-ABL-NOSTATE/` |
| `KEV-V8-C06` | KEV-V8-ABL-FULLSTATE | Full 8-Var State | Ablation: 8 Variables | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-FULLSTATE/` |
| `KEV-V8-C07` | KEV-V8-ABL-LORA8 | LoRA r8, lr=5e-5 | Capacity: Low Rank | PENDING | Warm-start Rank 16 vs Rank 8 Incompatible | -- | Target: `runs/KEV-V8-ABL-LORA8/` |
| `KEV-V8-C08` | KEV-V8-ABL-LORA32 | LoRA r32, lr=1e-5 | Capacity: High Rank | QUEUED | Pending | -- | Target: `runs/KEV-V8-ABL-LORA32/` |
| `KEV-V8-C09` | KEV-V8-EXT-01 | LoRA r16 + V8 Views | V8 Extension Data | PENDING | PARTIAL_MATERIAL (Records overlap C03) | -- | Target: `runs/KEV-V8-EXT-01/` |
| `KEV-V8-C10` | KEV-V8-S1-W2 | Weight S1=2.0 | High-Penalty S1 Loss | QUEUED | Pending | -- | Target: `runs/KEV-V8-S1-W2/` |
| `KEV-V8-C11` | KEV-V8-VAL-BEST | Best S1 Val loss | Scientific Best Select | QUEUED | Pending | -- | Target: `runs/KEV-V8-BEST/` |
| `KEV-V8-C12` | KEV-V8-PROD-SERVE | CPU/GPU Hybrid Serve | Port 8000 Production | VERIFIED | Real Probability (Serving healthy) | 2650.9 | `experiments/router_serving/` |

> **真实完成候选核定**：
> - 真正具备物理 Checkpoint、完整训练日志及固定 Val 验证的已完成训练候选数：**Laya 15 个**，**Kev 3 个**（初始适配器 C02、正式同源 C03、同源续训 C04）；
> - 正在现场 GPU 计算的活动候选数：**1 个**（Laya F10，PID 4158797，GPU 93-100%）；
> - 待决/排队候选数：严格标注为 `PENDING`（附带无法启动的科学依据，如数据缺失或 Rank 不匹配）或 `QUEUED`，绝不虚报为全数完成。

---

## 4. Verification & Scientific Rigor Guarantees

1. **真实训练与候选版本边界**：严禁将在线 Serving 或处于计划/排队中的候选标注为已完训版本。Kev 当前仅进行单次 1 Epoch 真实训练（`KEV-V8-HOMOLOGOUS-20261018`），每个后续候选必须在安全边界以独立 Run、独立超参、物理 Checkpoint 和固定 Val 逐一产出。
2. **算力竞争与显存余量科学界定**：显存占用 20 GB / 48 GB（余量 ~29 GB）仅保证**不发生 OOM 与显存换页**，但不等于两模型“零算力竞争”；两者在 GPU 流多处理器（SM）、L2 缓存、显存带宽及 PCIe 总线上存在物理竞争，需以单任务独占 vs 双任务并行的 `step/s` 和 `walltime` 进行客观基准测量。
3. **官方 Benchmark 评测真实性准则**：在宿主环境（`LocalHarborSandboxEnvironment`）完成的 Canary 执行仅为通道调试（`LOCAL_HOST_EXPERIMENTAL`）。在未具备官方 Docker 容器沙箱隔离、官方 Harbor Trial ID 及容器内原生未修改 CTRF 评测报告前，严格标记官方 Benchmark 为 `BLOCKED / UNFINISHED`，不得计入学术主表。
4. **V8 三类扩展视图独立性**：新清洗产出的 V8 三类数据视图（`MR-V8-DATA-EXTENSION-20261018`）严禁中途混入正在运行的 F06 或当前 Kev 训练；任何基于该扩展视图的训练均必须建立独立新 Run。
