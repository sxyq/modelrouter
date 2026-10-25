# ModelRouter · Laya & Kev 12-Candidate Research Progression Matrix

> **Author**: ModelRouter Main Execution Agent  
> **Date**: 2026-10-18  
> **Protocol**: V8 §8.3 & §9 Dual-Model 12-Candidate Formal Specification  
> **Server Target**: RTX A6000 (`k3s-infra-01`)

---

<!-- KEV_LIVE_CANDIDATES_BEGIN -->
## 当前 Kev 候选（原队列自动更新）

来源：原候选队列、固定 Val 和实体留存记录。生成时间 UTC：2026-10-25T03:32:17.781763+00:00。
配比固定 Val 已完成 0/16；材料 READY 不计训练完成。以下为当前状态，下方带日期的条目保留历史。

| 候选 | 监督比例 | 执行 | 固定 Val | Accuracy | NLL | Brier | ECE | 计分问题 | 内部评分 | 实体状态 | 累计释放字节 | 尚缺条件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KEV-V8-C03 | N/A | COMPLETED | EVALUATED | 0.5715969989281886 | 1.0795525776246775 | 0.537533605673637 | 0.05104668378873653 | 9330 | 100.0 | PROTECTED | 0 | N/A |
| KEV-V8-C04 | N/A | COMPLETED | EVALUATED | 0.5711682743837084 | 1.0872975000322915 | 0.5402653787706695 | 0.05987151793598101 | 9330 | 97.84213070623746 | PROTECTED | 0 | N/A |
| KEV-V8-C05 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | Missing training data: data/kev/公开数据/train_nostate.jsonl |
| KEV-V8-C06 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | Eight real state fields are not available in the current typed training records |
| KEV-V8-C07 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | warm_start lora: source rank 16, requested rank 8 |
| KEV-V8-C08 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | warm_start lora: source rank 16, requested rank 32 |
| KEV-V8-C09 | N/A | RUNNING | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | N/A |
| KEV-V8-C10 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | PENDING | 0 | Original train contains 35,645 ROUTE-001/002 rows excluded by current policy and 17 TRA-004 rows outside the legal source set; difficulty_tier is historical auxiliary supervision |
| KEV-V8-C11 | N/A | PENDING | N/A | N/A | N/A | N/A | N/A | N/A | N/A | NOT_SAVED | 0 | Selection uses comparable completed Val results; no new training |
| KEV-V8-R01 | {"S1": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R02 | {"S2": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R03 | {"S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R04 | {"S1": 1, "S2": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R05 | {"S1": 2, "S2": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R06 | {"S1": 1, "S2": 2} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R07 | {"S1": 1, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R08 | {"S1": 2, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R09 | {"S1": 1, "S3": 2} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R10 | {"S2": 1, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R11 | {"S2": 2, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R12 | {"S2": 1, "S3": 2} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R13 | {"S1": 1, "S2": 1, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R14 | {"S1": 2, "S2": 1, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R15 | {"S1": 1, "S2": 2, "S3": 1} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |
| KEV-V8-R16 | {"S1": 1, "S2": 1, "S3": 2} | MATERIAL_READY | NOT_EVALUATED | N/A | N/A | N/A | N/A | N/A | N/A | N/A | 0 | 等待原 dispatcher 自然接续 |

内部评分只用于实体选择；固定 Val 不计官方 Agent 成功率。完整配方、材料、命令与原始指标见 training_research.json 和 candidate_ledger.json。
<!-- KEV_LIVE_CANDIDATES_END -->

## 1. Overview & Research Rationales

Per V8 §8.3, each model family (Laya and Kev) is evaluated across **at least 12 distinct, reproducible, and verifiable candidate versions / phase checkpoints**. Each candidate is uniquely defined by:
`candidate_id`: Base Checksum, Data View SHA, Training Source SHA, Supervision Target, Loss Weighting, Seed/Epoch, and Checkpoint SHA.

## 2026-10-25 · 当前候选与材料状态

依据为 A6000 台北 10:46–10:53 的实际记录。下方第 2–4 节保留 10/24 及此前历史原文，其中 F10 在训、C06/C08/C10 排队和 C09 待决均为旧状态；当前候选以本节为准，不把计划或材料就绪计为完成。

| 对象 | 当前状态 | 依据与范围 |
|---|---|---|
| Laya F11 | RUNNING，健康在训 | worker `303160` / 原 controller `499841`；未补写 F10 最终指标 |
| Kev C03/C04 | COMPLETED，正式训练及固定 Val 均完成 | 同一固定 Val：8,436 记录 / 9,330 问题；两实体保护，0 删除、0 释放 |
| Kev C05/C06 | PENDING | 状态拆分不成立，不能据旧排队状态启动 |
| Kev C07/C08 | PENDING | Rank16 初始化与 Rank8/32 请求不兼容；保持原初始化 |
| Kev C09 | RUNNING，健康在训 | worker `413095` / 原 dispatcher `413082`；固定 Val 尚待本 Run 完训后完成 |
| Kev C10 | PENDING，材料待决 | 实际 loss 权重有效；原材料含 35,645 条禁用 ROUTE-001/002 来源 + 17 条 TRA-004，不擅改或追加训练 |
| Kev C11 | 选择记录，当前 C03 | 不计新 Run，不冒充新训练版本 |
| Kev R01–R16 | READY，训练未完成 | 108,656 条训练材料已官方 strict CPU 编码，0 异常；等待 C09 完训及固定 Val 后同 dispatcher 接续 |

唯一接续命令标识 `420899` 已存在，勿再次派发。R01–R16 的 READY 只证明材料就绪；CPU 编码、训练进度和固定 Val 均不计官方 Agent 成绩。

### C03/C04 同固定 Val 的精确记录

| 指标 | C03 | C04 |
|---|---:|---:|
| acc | 0.5715969989281886 | 0.5711682743837084 |
| nll | 1.0795525776246775 | 1.0872975000322915 |
| brier | 0.537533605673637 | 0.5402653787706695 |
| ece | 0.05104668378873653 | 0.05987151793598101 |
| 内部 score | 100 | 97.842 |

C03 的 acc 更高，nll/brier/ece 更低。内部 score 只用于当前内部比较，不代表论文主要评价或官方 Agent 成绩；C11 当前选择 C03 的记录不增加正式训练次数。

Laya 历史为 105 个真实 Run（104 结束 + F11 在训）、220 个版本、7 份实体；旧核心 2/5，新池 F05-e01 一份，F06-e02 另列历史留存。Kev 为 6 个执行对象 + 1 个导入对象，正式完成仅 C03/C04，C09 在训，导入对象不计本地正式训练。

未来任务 515 项 = 499 Laya + 16 Kev，不含当前两个在训 Run。10:50 条件 ETA 约 478 小时，情景 398–524 小时，中心约台北 11/14；不保证日期，不宣布论文完成。原报告已更新监督材料与实际状态，候选科学定义、QA/Research与数据政策保持，不新增科研 Q-ID。

---

## 2. Laya-421M 12-Candidate Progression Matrix

| Candidate ID | Name / Run | Data Level & View | Supervision & Epoch | Status | S1 Val Acc | S1 Val Loss | S1 Brier | Checkpoint SHA / Path |
|---|---|---|---|---|---|---|---|---|
| `LAYA-V8-C01` | Laya-ZeroShot | Base init | None (Zero-shot) | NOT_EVALUATED | N/A | N/A | N/A | `models/laya-421m/`；无独立零样本评测记录 |
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
| `LAYA-V8-C12` | F06-e02 | L4 Full-Coverage 3-Layer | Ep 2 (92,280 steps, 5.9M items) | COMPLETED | **68.63%** | 0.6017 | **0.4150** | `runs/.../F06/checkpoints/epoch_02`；实体在盘，最低 S1 Loss 属无实体的 e01 |
| `LAYA-V8-C13` | F07-e01 | L1+L2+L3+L4 Full-Coverage | Run 完成 Ep 2 (151,998 steps, 9.7M items)；此行取 e01 | COMPLETED | **68.27%** | 0.6076 | 0.4203 | `runs/.../F07/epoch_metrics.json`；无实体，原记录未保存 |
| `LAYA-V8-C14` | F08-e02 | L1+L2 Cumulative | Ep 2 (23,002 steps, 1.47M items) | COMPLETED | 67.02% | 0.6123 | 0.4246 | `runs/.../F08/epoch_metrics.json`；无实体，原记录未保存 |
| `LAYA-V8-C15` | F09-e02 | L1+L2+L3 Cumulative | Ep 2 (30,826 steps, 1.97M items) | COMPLETED | 66.49% | 0.6100 | 0.4226 | `runs/.../F09/epoch_metrics.json`；无实体，原记录未保存 |
| `LAYA-V8-C16` | F10 | L1+L4 Stratified | 23:38 观测 Ep 2 Chunk 32/152 (23,462/38,732) | **LIVE_TRAINING** | e01: 64.88% | e01: 0.6105 | e01: 0.4238 | PID 4158797；e01 实体在盘，最终 Val 尚未完成 |

> **关键物理权重区分**：
> - **当前在线 Serving 权重**：`F05/checkpoints/best`（Epoch 1，S1 Acc 67.56%，Loss 0.5978，Brier 0.4130，4.2 GB 实体在盘，Port 8000 活跃加载）；
> - **物理在盘准确率代表候选**：`F06-e02`（S1 Acc **68.63%**，Loss 0.6017，Brier 0.4150）；其最低 S1 Loss e01 无实体。`F06_S1-e02` 的 68.09% / 0.5936 / 0.4079 不属于 F06。
> - **23:38 训练观测**：`F10`（PID 4158797，第 2 Epoch Chunk 32/152，Step 23,462/38,732，消费 1,501,536 条，Chunk Loss 0.4708748825868163）。后续实时值见原看板。

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
> - 上表 Laya 历史 Epoch 条目不等于物理实体。23:52 全历史 Laya 实际执行 104 Run、完成 103、在训 1，219 条 Epoch 记录、8 份实体；其中含 Pilot、课程父权重与 F10 未完成 Run 的恢复权重。临时恢复文件随当前训练变化，单次实体盘点不用于推算历史生成总数。Kev 正式训练及相同固定 Val 完成 **2 Run**（C03/C04）；C02 是导入资产，验证集不同，不计为本地正式训练。
> - 正在现场 GPU 计算的活动候选数：**1 个**（Laya F10，PID 4158797，GPU 93-100%）；
> - 待决/排队候选数：严格标注为 `PENDING`（附带无法启动的科学依据，如数据缺失或 Rank 不匹配）或 `QUEUED`，绝不虚报为全数完成。

---

## 4. Verification & Scientific Rigor Guarantees

1. **真实训练与候选版本边界**：在线 Serving、导入资产与计划候选分开。Kev C03/C04 各完成一次正式 Run 和相同固定 Val，C04 从 C03 接续；C05/C07/C09 已由原入口记为 PENDING。物理实体、历史 Epoch 和完成 Run 分别计数。
2. **算力竞争与显存余量科学界定**：显存占用 20 GB / 48 GB（余量 ~29 GB）仅保证**不发生 OOM 与显存换页**，但不等于两模型“零算力竞争”；两者在 GPU 流多处理器（SM）、L2 缓存、显存带宽及 PCIe 总线上存在物理竞争，需以单任务独占 vs 双任务并行的 `step/s` 和 `walltime` 进行客观基准测量。
3. **官方 Benchmark 评测真实性准则**：在宿主环境（`LocalHarborSandboxEnvironment`）完成的 Canary 执行仅为通道调试（`LOCAL_HOST_EXPERIMENTAL`）。在未具备官方 Docker 容器沙箱隔离、官方 Harbor Trial ID 及容器内原生未修改 CTRF 评测报告前，严格标记官方 Benchmark 为 `BLOCKED / UNFINISHED`，不得计入学术主表。
4. **V8 三类扩展视图独立性**：新清洗产出的 V8 三类数据视图（`MR-V8-DATA-EXTENSION-20261018`）严禁中途混入正在运行的 F06 或当前 Kev 训练；任何基于该扩展视图的训练均必须建立独立新 Run。
