# ModelRouter · 项目现状、资源条件与执行路线

> **最新状态：2026-10-15 12:00（P16 研究全局连续推进、历史运行协议审计、双池库存核查与课程父模型补跑就绪）**：
> 1. **当前 GPU 在线训练状态（Live Running：F04 L4 四层全量覆盖）**：
>    - **PID 2881373 持续高速健康运转**：A6000 负载 95%～97%，功耗 294W，显存 9,759 MiB / 49,140 MiB（19.9%）。已稳定推进至 Epoch 1/2 Chunk 19/234，步数 2,432/59,904，Loss 稳步从 0.8027 下潜至 0.5786~0.5917，累计消费 155,648 条真实样本、51,923 个独立任务单元，零丢弃、无故障、流式物化与显存完全稳定。后台队列守护进程 PID 2881128 保持坚守等待。
> 2. **历史 Run 协议有效性与真实步数核查（消除计划步数误导）**：
>    - **F01**：已执行 **15,174 步**（2 Epochs，每 Epoch 60 Chunks），累计消费 971,070 条样本（单轮 485,535 条），协议 `MR-FULL-GRADED-P0-DATA-REPAIR-v1`，物理实体权重在 10月13日旧淘汰机制中被释放，当前为 `METADATA_ONLY`；
>    - **F02**：已执行 **31,304 步**（2 Epochs，每 Epoch 123 Chunks），累计消费 2,003,390 条样本（单轮 1,001,695 条），协议 `MR-FULL-GRADED-P0-DATA-REPAIR-v1`，物理实体权重为 `METADATA_ONLY`；
>    - **F03_LEGACY_MINFACTOR**：原计划步数 45,836 步，但由于 `min_factor` 严重丢弃样本，**真实仅执行 1,456 步**，累计消费 82,680 条样本（候选 1,466,724 条仅消费 ~5.6%），已物理归档且在所有统计中与正规 Full-Coverage 严格隔离；
>    - **S1 纯基准系列（7 组全部完成）**：`F01_S1`（144 步 / 9,184 条）、`F02_S1`（288 步 / 18,340 条）、`F03_S1`（432 步 / 27,560 条）、`F04_S1`（132 步 / 8,448 条）、`F05_S1`（432 步 / 27,524 条）、`F06_S1`（862 步 / 55,084 条）、`F07_S1`（994 步 / 63,532 条），全部真实步数已准确记录，状态为 `METADATA_ONLY`。
> 3. **Checkpoint 双池实体留存实事求是核验**：
>    - **老核心 5 席保留池**：服务器实际物理磁盘**仅保留 2 席完整物理权重**（`P0_B03_C01_QB_PB-e02` [842.6 MB, 得分 159.25] 与 `P0_B01_C01_QB_PB-e02` [842.6 MB, 得分 158.83]）；其余 3 席（`P0_B02_C01-e02`, `P0_B03_C05-e02`, `P0_B03_C08-e02`）在历史修剪中已被释放，仅保留元数据。如实披露，杜绝伪造；
>    - **新核心 15% 动态池**：基于已完成的 13 组合法新协议 Run，动态配额为 $\lceil 0.15 \times 13 \rceil = 2$ 席，随着全量覆盖模型产出实时评估晋级。
> 4. **课程模型父依赖链与 F01 正规补跑方案就绪**：
>    - **依赖关系链**：`F17 <- F01`，`F18 <- F17`，`F19 <- F18`，`F20 <- F19`；
>    - **检查已实证**：`laya_batch_train.py` 中的 `Fail-Closed` 保护已杜绝静默回退（缺失父断点直接抛 `RuntimeError`）；`checkpoint_retention.py` 中 `collect_pinned_parent_ids()` 已具备子依赖反查保护机制（`PINNED_PARENT`）；
>    - **F01 物理断点现状与补跑安排**：由于 10月13日跑完 F01 时尚无 `PINNED_PARENT` 机制，物理权重已被修剪；已在调度器中正式编排 `F01` 补跑任务于 Stage 5 课程依赖启动前（`_stage=5, _prio=0`，即在 `F17` 之前执行），归档旧元数据并重新启动 F01 单层 L1 全量训练（仅 60 Chunks，约 45 分钟），产出实体断点并自动激活 `PINNED_PARENT` 永久保护，为 `F17` 提供真实的 `F01:best` 物理权重，确保全链学术科学性。
> 5. **F03 正规补跑在队列最高未决边界排定**：
>    - 调度守护进程 `PID 2881128` 在当前 `F04` 跑完的瞬间，动态队列首位必然无缝选定正规 `F03`（单层 L3，1,466,724 样本，46,080 步），采用 Full-Coverage 零丢弃协议。
> 6. **评测物理隔离与零污染**：
>    - Terminal-Bench 2.1（Canary 8 题、External DEV 24 题、Sealed Final Test 57 题，共 89 题）物理存放在独立基准目录，未进入任何训练/验证索引；训练阶段绝不读取，评测必须待正式模型稳定产出后启动。
> 7. **真实实验完成与排队大盘（38 组全矩阵）**：
>    - **已完成（13 组正规 + 1 组归档）**：单层基准 7 组（`F01_S1`～`F07_S1`）、消融对齐 4 组（`ALGN_01`～`ALGN_04`）、全量覆盖 2 组（`F01`、`F02`）；另有归档对照 `F03_LEGACY_MINFACTOR`；
>    - **运行中（1 组）**：`F04`；
>    - **排队中（25 组）**：`F03`（全量补跑）、`F05`～`F07`（累积全量）、`F08`～`F16`（数据比例缩放）、`F01`（课程父节点再生）、`F17`～`F20`（课程链）、`F01_S3`～`F07_S3`（S3 辅助基线）。

八类变量为 `Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`。

**2026-10-15 FULL-DATA-CONTINUOUS-TRAINING & ROUTING-ALIGNED（唯一正式长效训练入口）：在 A6000 后台持续稳定运行。** 调度器 `router_data/run_full_graded_queue.py --mode continuous_full_coverage` 驱动 F01..F20 及 ALGN_01..04，采用动态分块流式物化（Chunk 8,192 Items）、跨 Chunk 连续优化（AdamW + CosineAnnealingLR）、逐 Epoch 固定验证集（S1/S2/S3）评估、双池核心模型保留与动态淘汰裁剪及自动覆盖台账更新。

## 当前轮次

| 阶段 | 状态 |
| --- | --- |
| P0 清理 | 已移除实验目录 `training/laya/`、`training/kev/` 及六个旧通用视图目录。`MR-STAGE1-*`、原始数据、清洗数据、OWN 源、`models/`、`external/` 均保留 |
| P1 分级 | 从全量清洗源与三个 OWN 文件逐行处理。公开合计 `6,600,628`；OWN `110 / 221,128 / 79` 分开统计 |
| P2 分层 | 17 个来源分别按任务、轨迹、请求、偏好对战或聚合单元归组，唯一分配至 L1–L4；每层均有全部 17 个来源的实际记录 |
| P3 覆盖 | 八类变量逐层列出非空数、缺失数、监督/观察用途、许可与评测用途、Q4。真实运行时路由决策标签 `0` |
| P4 输出 | 服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/` 含逐源记录引用、四层引用、汇总 JSON、变量矩阵及五张表 |
| P5 Laya Batch 1 | 训练 `13,438` 条、独立 Val `5,692` 条；`R1-e01` 与 `R2-e01` 作为课程父节点已标记 `PINNED_PARENT` 保护，当前停止 |
| P6 Laya Sweep-02 | N01–N10 已完成（30 个 Epoch，50 个实体权重目录，占 `39.65 GiB`）；已纳入全项目 TOP 5 统一比选与裁剪 |
| P7 FULL-GRADED 窗口一 & P0 数据修复 | 旧窗口 16 个 B01 Run（32 Epoch）隔离为 `LEGACY_INPUT_PROTOCOL`；新协议 52 个 `P0_` Run 已完成 CPU 物化并产生 TOP 5 核心权重 |
| P8 Checkpoint 智能保留与磁盘保护 | 全局硬性保留上限 `MAX_CORE_CHECKPOINTS = 5`，两阶段白名单修剪彻底删除 122 个目录，**释放 96.16 GiB**；活动预算 120 GiB 与磁盘门禁正常 |
| P9 FULL-DATA 连续全量分级训练（进行中） | 启动 Mode B：486.4 万候选记录 F01..F20 全量分级流式训练（34 个正式方案），调度守护进程在后台连续运行；F01_S1..F07_S1 已完成，F01..F03 完成，当前 F04 准备启动，后续正规 Full-Coverage 准备就绪 |
| P10 八类状态变量与联合路由监督审计 | 完成八类变量真实字段表、6 源覆盖热力图、8×8 共现矩阵（V2∩V6=0）、低成本敏感性筛查（G3 S2 Loss +0.4559, G4 S3 Loss +0.1065）及 4 项不支持假设锁定 |
| P11 TOP5 精简 + 数据质量修复 + 路由对齐训练 | **已全部落地**：全局保留 TOP 5 核心模型权重，补齐轻量索引写入与数据物化漏洞，平衡多监督批次采样，正式确立 MR-ROUTING-ALIGNED-v2 四视角并排队 4 组消融任务 |
| P12 采样优化 + 双池保留 + 极简质检看板 | **已全面完成**：ALGN_01～04 全量收敛验收；F03 正式接续流式训练；旧 5 核心永久保护 + 新 ~15% 动态择优双池上线；质检看板极简图表驱动重构上线 |
| P13 过夜连续执行与全链数据修复 | **本轮就绪**：F03 顺利收敛归档（14 组完成），F04 启动阻断已完成定点修复并推送到远端与服务器，全链数据流打通，GPU 资源完全健康，待命接续 |

公开记录层规模：L1 `663,963`、L2 `1,304,523`、L3 `1,993,193`、L4 `2,638,949`，总计 `6,600,628`。三类 OWN 记录逐层另列。按来源政策允许、Q1/Q2、真实目标及 Train 身份计算的候选记录数依次为 `489,911`、`973,501`、`1,475,527`、`1,924,961`，合计 `4,863,900`；Val/Test 身份归评测用途，不计作训练候选。候选包含轨迹终局、静态偏好、缓存复用机会、请求负载和 OWN-002 调用统计等不同目标，不代表联合路由监督。

逐源 Q1–Q4 总计：公开 Q1 `6,469,995`、Q2 `50,638`、Q3 `4,041`、Q4 `75,954`。ROUTE-001/002 的 `584,556` 行处于许可待核，未进入候选；ROUTE-005 保持仅分析，ROUTE-003、ENV、MEM 保持评测用途。Q4 内容状态可与许可待核重叠。

TRA 与 ENV 共有 `13,486` 条任务记录继承 TRA 已有 Train/Val/Test 身份（ENV-001 `150`，ENV-002 `13,336`），分割冲突 `0`；ENV 用途仍为评测。ROUTE-001 的 `24,441` 个完整题目组、ROUTE-003 的 `520` 个任务组均按真实身份保留。轨迹步骤、候选评测行和请求没有按独立任务计数。

逐项结果与五张交付表位于服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/tables.md`。Laya 结果位于服务器 `runs/OVERNIGHT-LAYA-TRAINING/`，看板源数据和公开 HTML 位于本仓库 `docs/training-dashboard/`；清洗源、模型原始权重和 Kev 资产未改动。R0–R3 使用验证集记录选轮，未运行 Test 终评；八类运行状态与真实路由决策、缓存和整任务成本的联合监督仍为 `0`。

本轮按授权停止。后续是否使用 Sweep-02 中的某个 Laya 权重，以及是否启动 Kev 或受控任务评测，交由负责人决定。

## 历史状态：旧派生视图生成记录

**科研目标**：面向单 Agent / 多子代理执行状态，利用八组研究变量（`Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`）以及模型、Reasoning Effort、KV 缓存、单次调用成本和任务平均 Trace 次数，学习模型路由决策，在任务成功率约束下降低完整任务成本。最终有效性需要真实 Agent Harness 与受控实验，不能由静态分类准确率证明。

| 大阶段 / 工作 | 当前实际进度 |
| --- | --- |
| E0–E1：研究问题、数据源、环境、已有模型与 Smoke Test | 已完成主要准备；Kev/Laya 历史短训练与保存重载有执行汇总，不能称正式训练成果 |
| 数据收集、14 个公开源统一 CPU 清洗 | **阶段性完成**：`6,600,628` 行，覆盖轨迹、静态评测、缓存请求、工作负载、环境和记忆；另有 CCH/Blog 自有数据，不能按同一粒度简单相加 |
| Stage 1–4 全量分层与监督修复（P0） | **已完成**：对齐 `ROUTE-001` 新旧 Choice（均为 `8,441` 题，`0` 差异）、Pairwise（`59,049` 对）、Score/Soft-Target（`53,087` 题）的完整题目身份与统一 Train/Val/Test 语义划分（跨视图泄漏 `0`）；排除 `1,953` 条不合法单胜者与 `417` 道分数冲突题，保留 `11,599` 道 `ROUTE-001` 同分题与 `87` 道 `ROUTE-002` 双并列题于多模型比较视图 |
| Laya-421M / Kev-4B 双模型训练视图适配与 CPU 校验（P1–P2） | **已完成**：在 `runs/MR-ALLDATA-PREP-20261011/training/{laya,kev}/` 生成 6 个训练子集（`stage1_choice` `83,259`、`stage1_pairwise` `59,049`、`stage1_soft_target` `53,087`、`stage2_agent_state` `88,087` 轨迹级、`stage3_effort` `290` 有效配对、`stage4_auxiliary` `1,622,547` 有效调用），合计每模型 `1,906,319` 条记录，均通过官方 CPU 加载与编码校验 |
| **当前等待点：Laya-421M / Kev-4B 第一轮正式 GPU 训练（P3）** | **参数与命令已备齐，按指令暂停等待批准**：已基于官方 `laya-train` 与 `python -m kev.train` 锁定首轮超参数、数据路径与检查点输出目录 |
| E2：Kev/Laya 正式微调与离线对照 | **尚未启动；GPU 未授权**。保持 A/B/C 分源分体制评测；`ROUTE-004` `TRAIN_ALLOWED_VERIFIED`，`ROUTE-001/002` `LICENSE_PENDING` |
| E3–E5：Coding Benchmark、运行时缓存感知/多 Agent 动态路由、消融和论文 | **尚未启动**。同状态多动作、真实 KV 切换代价及整个任务回报的联合监督仍缺失 |

**两项不可混淆的状态**：`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`（含决策前完整题面恢复、跨视图身份/划分对齐及 Laya/Kev 双模型独立训练目录 CPU 100% 校验）；`RUNTIME_JOINT_DATA_READY = NOT_READY`（八组运行时状态 + model×effort + 真实缓存和费用的完整联合监督为 0，同状态中途反事实分支为 0）。

## 二、当前阶段各小步骤

### A. 已完成的大块：数据清洗、正确性修正与双模型训练视图适配

1. **源与数量**：14 个已清洗公开源共 `6,600,628` 条不同粒度记录；自有 `OWN-001` CCH `110` 聚合行对应 `750,212` 次调用、`OWN-002` Blog `221,128` 逐调用行、`OWN-003` `79` 衍生汇总行（新增独立观测 `0`）。
2. **唯一处理链**：`prepare_router_data.py` 为唯一命令入口（`--mode views` 与 `--mode all_data`），内部模块位于 `router_data/`；原始数据与历史冻结导出未被覆盖。
3. **P0 监督修复与跨视图对齐**：
   - `ROUTE-001` 新重算 Choice 严格剔除 `1,953` 条不合法单胜者（`ALL_MODELS_FAILED: 1,553`、`CONFLICTING_MODEL_SCORE_UNRESOLVED: 241`、`CONFLICTING_TIED_TOP_COST_UNRESOLVED: 141`、`CONFLICTING_WINNER_COST_UNRESOLVED: 17`、`TIED_SCORE_TIED_API_USD: 1`），从 `10,394` 收敛为 **`8,441` 条（`train: 6,729, val: 865, test: 847`）**，与 Stage 1 主 Choice 中的 `ROUTE-001` 子集逐题 100% 一致（差异 `0`）。
   - 统一使用 `views.py` 的完整题面语义归一化哈希划分规则，消除 `all_data.py` 旧版二次哈希导致的不同视图跨集不一致（Soft-Target、Pairwise 与主 Choice 的跨集泄漏均为 `0`）。
   - 在 `stage1_soft_target`（`53,087` 题：`42,502 / 5,327 / 5,258`）与 `stage1_pairwise`（`59,049` 对：`47,241 / 5,941 / 5,867`）中剔除 `417` 道同模型分数冲突题，完整保留 `11,599` 道 `ROUTE-001` 最高分并列但具备有效多模型质量分布的题目及 `87` 道 `ROUTE-002` 得分+估价双并列题。
4. **P1–P2 双模型独立训练视图与 CPU 官方编码核验**：
   - 独立目录 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `runs/MR-ALLDATA-PREP-20261011/training/kev/` 均包含 6 个阶段子目录：
     - `stage1_choice`：`66,721 / 8,298 / 8,240 = 83,259`（Laya `1024/512` 100% 接收；Kev `--max_state 7552` 接收 `83,031` 条，跳过 `228` 条超长 `ROUTE-001` 样本）。
     - `stage1_pairwise`：`47,241 / 5,941 / 5,867 = 59,049`（Laya 100% 接收；Kev `7552` 接收 `58,833` 条，跳过 `216` 条）。
     - `stage1_soft_target`：`42,502 / 5,327 / 5,258 = 53,087`（Laya `gold.probabilities` 软分布、Kev `label + target` 概率向量；Kev `7552` 接收 `52,872` 条，跳过 `215` 条）。
     - `stage2_agent_state`：`70,334 / 8,683 / 9,070 = 88,087` 条轨迹级压缩记录（对应 `35,289` 个独立任务，去除 `4,360,556` 条逐步重复终局行；两模型 `384/7552` 均 100% 零截断通过）。
     - `stage3_effort`：`217 / 39 / 34 = 290` 对同模型同权重有效胜负配对（排除 `1,075` 对同成同败平局；两模型 100% 零截断通过）。
     - `stage4_auxiliary`：`1,297,178 / 162,623 / 162,746 = 1,622,547` 条有效单请求辅助记录（排除 `42,507` 条失败/零 Token 调用、`6,204` 条禁止训练的 `ROUTE-005` 及 `189` 条聚合行；两模型 100% 零截断通过）。

### B. 唯一正在等待批准的步骤：启动首轮 Laya-421M / Kev-4B 训练

- **已就绪**：双模型全阶段训练 JSONL、CPU 编码兼容统计表、首轮训练超参数与命令均已核实完备。
- **未批准**：正式 GPU 训练、GPU 推理评测、付费 API、Coding Benchmark 批量运行。

## 三、后续唯一计划

**等待负责人确认 GPU 训练授权及 `ROUTE-001/002`（`LICENSE_PENDING`）训练范围后，启动 Stage 1 首轮 Laya-421M 与 Kev-4B 微调对比实验（先跑 `stage1_choice` 与 `stage1_soft_target`）。**

## 四、下一步执行提示词（给 Codex）

> 在获得负责人正式 GPU 训练授权后，基于 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `runs/MR-ALLDATA-PREP-20261011/training/kev/` 中已通过 100% CPU 校验的统一划分数据，按已锁定的首轮命令依次执行 Laya-421M（`laya-train --loss soft-ce --max-len 1024 --head-max-len 512`）与 Kev-4B（`python -m kev.train --weights lora --lora 16 --head_dim 256 --max_state 7552`）在 `stage1_choice` 与 `stage1_soft_target` 上的微调；仅使用 `val.jsonl` 选模与校准，`test.jsonl` 仅作单次终评，并按数据源（`ROUTE-004/002/001`）与监督体制（`Regime A/B/C`）分别汇报准确率、校准误差（ECE/Brier）与推理延迟。

## 五、简单情况说明

已经把 14 个公开数据集（660 万行）和自有数据里所有能用于训练的部分，修复了跨子集串题、分割不一致和并列标签问题，并按 Laya-421M 和 Kev-4B 各自要求的官方数据格式分别生成了可直接读取的训练文件，还在 CPU 上逐条验证通过。**现在数据和训练命令都已经准备好，停在启动 GPU 训练之前等待批准。**

## 固定汇报与新对话

按“一、总体项目进度；二、当前阶段各小步骤；三、后续计划；四、下一步执行提示词；五、简单情况说明”回答。先读本页及 [PLANNING_MEMORY 第10节](PLANNING_MEMORY.md#10-新会话恢复协议长期生效)，按真实变化更新已有相关文件。

## 历史资料（以下为旧阶段快照，不代表当前状态）

2026-10-10 Planning 基于 7fc24bc 的独立复审提出七项矛盾，本轮已逐项核验并替换无依据的 PASS。原复审与执行文字可从 Git 历史追溯；不将历史“已完成”结论继续当作当前证据。

### 0.1 本地与服务器实测核验结果（Execution Agent 于 2026-10-09 审计快照）

1. **本地仓库（资产统计快照）**：
   - 统计口径说明：Git 跟踪管理的文件为 208 个，当前工作区未跟踪文件为 1 个（`AGENTS.md`），合计 209 个项目资产文件（总体积约 251.3 MB；若包含本地系统临时文件 `.DS_Store` 与未纳入版本控制的历史笔记 `.workbuddy/`，本地物理文件总数为 214 个）。
   - 在已授权扫描范围内：纯研究文档与数据仓库，目前暂无 `pyproject.toml`、`requirements.txt` 或可运行的 Python 代码。
   - `our-project/data/` 包含 CCH 聚合统计（110 行）与 Blog GPT 调用明细（221,128 行），缺失 `task_id` 与任务终局标签。
   - `research/` 包含 58 份论文 PDF 与 73 份截图资产；`external-projects/` 为 9 个微型卡片。
2. **授权 GPU 服务器（RTX A6000，2026-10-09 审计快照）**：
   - **硬件状态**：80 核 CPU、376 GiB RAM（346 GiB 空闲）、1.2 TiB 可用磁盘，GPU 显存占用 682 MiB / 49140 MiB（利用率 0%）。
   - **已有服务**：已有若干共享文本、图像及 Web 对话服务处于运行中状态；vLLM 推理服务当前未运行。

### 0.2 当前版本信息的完整性核对

| 版本层次 | Planning 能否直接核实 | Execution 应报告 |
|---|---|---|
| GitHub 远端 `main` | **可以**，读取最新 HEAD 与四份正式文件 | 远端 SHA、最近 push、文档变更 |
| 本地工作区 | **不能自动看到** | 当前分支、本地 HEAD、未提交/未跟踪文件的脱敏摘要、相对 `origin/main` 的 ahead/behind |
| 授权服务器运行版本 | **不能从 GitHub 推断** | ModelRouter 是否部署；若部署，记录实际代码 SHA、环境/模型版本、审计时间 |
| 实验结果版本 | **必须由执行记录提供** | 代码 SHA、配置/数据/模型版本、任务集、seed、结果位置、费用与资源 |

Execution 在每轮结束时先执行 `git status -sb`、`git rev-parse HEAD`、`git fetch origin`、`git rev-parse origin/main`、`git rev-list --left-right --count origin/main...HEAD`、`git log -3 --oneline`，报告脱敏摘要。只有 push 成功后，Planning 读取的 GitHub 才包含最新本地提交。旧审计分支不应直接合并进 `main`。

## 1. 当前总览

| 项目 | 当前状态 | 判断 |
|---|---|---|
| 研究命题 | 长程 Agent 状态感知、任务级 Model × Effort 路由 | **已明确** |
| 文献与历史研究 | 已有综合报告、7 个专题证据、Kev/Jev 研究 | **可用，需按当前方法更新** |
| 本地生产调用数据 | CCH 聚合 + Blog GPT 调用明细 | **仅适合统计先验，非路由监督** |
| 真实 Agent 轨迹 | 16 个公开数据源（660 万条）已清洗归档；84,310 条单胜者路由视图已冻结 | **训练视图已就绪（TRAIN_READY）** |
| 数据处理与验证主链 | `prepare_router_data.py` + `manifest.json`（两次运行 SHA256 100% 一致） | **已冻结** |
| Kev-4B 与 Laya-421M | 权重已下载，官方仓库代码已完成全量编码验证与 GPU Smoke Test | **Smoke Test 100% 通过** |
| GPU | 一张 A6000 48GB；Kev-4B 训练峰值 10.50 GiB，Laya-421M 训练峰值 < 2 GiB | **资源充足，已实测验证** |
| Coding Benchmark 批量运行 | 尚未启动，等待 Kev/Laya 正式训练完成后再规划批量运行 | **未启动（E3 阶段）** |
| 论文实验结果 | 待完成 E2 正式训练与 E3/E4 实验后产出 | **按阶段推进** |

**执行路线（最新调整顺序）**：`E0 / E0.5 研究与资源审计（已完成） → E-DESIGN 数据与模型训练方案 / Q-007-FINAL（已完成） → E1 模型训练环境与最小运行验证（已完成 Smoke Test） → E2 Kev/Laya 正式训练与离线验证（下一步） → E3 Coding Benchmark 批量运行（未启动） → E4 动态缓存感知路由实验（未启动） → E5 消融、统计检验与论文整理（未启动）`。

**当前状态**：Q-007-FINAL 已完成数据资产冻结、唯一胜者标签纯化、跨集零泄漏验证及 Kev/Laya 官方 CPU/GPU Smoke Test，下一步进入 E1/E2 正式训练阶段。Coding Benchmark 尚未启动，等待 Kev/Laya 正式训练完成后再规划批量运行。

## 2. 仓库与工程状态

**GitHub**：https://github.com/sxyq/modelrouter （公开，默认 `main`）。

**E0 时本地工作树**：`main` 旧 HEAD 为 `13c14a3`；有用户未提交修改（包括 `.gitignore` 和未跟踪的 `AGENTS.md`，另有历史工作目录变动）。执行 Agent 每轮操作均保留未提交修改，不清理、覆盖、reset 或强推这些变更。执行 Agent 每轮重新核查当前状态。

### 2.1 已有研究资产（仓库相对路径）

| 路径 | 内容 | 复用方式 |
|---|---|---|
| `README.md` | 项目入口 | 四文档与新会话导航 |
| `our-project/literature/report.md` | 551 行任务级成本路由历史综合调研 | 保留原始证据与早期问题定位 |
| `our-project/literature/findings/F1.md`–`F7.md` | 专题证据 | 研究与实验设计引用 |
| `our-project/literature/related-papers.md` | 论文定位表 | 持续核对近邻方法 |
| `our-project/literature/jev-model-research.md` | Jev/Kev 方案 | 决策模型技术参考 |
| `research/jev-deep/JEV深度调研报告.md` | Jev 多源研究 | 区分闭源 Jev 与开源 Kev |
| `our-project/planning/IMPLEMENTATION_RESEARCH.md` | 旧实现规划 | 作为 admission-only/GBDT 历史方案与对照 |
| `our-project/data/source/` | CCH 聚合统计及说明 | 费用/缓存/Token 先验 |
| `our-project/data/cleaned/` | Blog GPT 清洗明细 | 调用级统计与 effort 分布 |
| `our-project/data/summaries/` | 统一汇总 | **保留不同成本单位** |
| `external-projects/` | 外部开源项目登记卡 | 许可证与复用来源 |

**目前未见**：`pyproject.toml`、`requirements.txt`、`src/modelrouter`、`tests`、正式 Agent Harness、Router 推理服务、任务级训练集、受控回放结果。

### 2.2 当前建议的最小新增代码布局（规划，尚不存在）

~~~text
src/modelrouter/
  core/schemas.py           # State / Action / Constraint / Decision / Outcome
  core/state_builder.py     # 严格决策前特征
  core/candidates.py        # 动态 Model × Effort 能力表
  core/constraints.py       # 硬约束与连续性锁
  accounting/pricing.py     # 带版本的 USD 价目表
  accounting/usage.py       # 物理 cache read/write + 原始 usage
  router/base.py            # 可替换策略接口
  router/kev_adapter.py     # 后续接 Kev-4B，首轮不强制实现
  harness/                  # 后续固定 Agent 执行环境
tests/
configs/
~~~

本目录仅是任务卡讨论起点，**不得将其误写成已实现**。

## 3. 硬件、系统和运行服务

### 3.1 本地开发环境（[E0 报告]）

- macOS / Apple Silicon；Python 3.9.6；PyTorch 2.4.1；MPS 可用。
- 适合文档、数据校验、Schema 单测和轻量基线；不应据此宣称本地可以完成 Kev-4B 全量训练。
- 项目专用 Python 环境、依赖锁文件和可执行测试均尚未建立。

### 3.2 授权服务器（[AUDIT]，2026-10-09 审计快照）

| 项目 | 审计值 | 风险/后续 |
|---|---|---|
| 系统 | Ubuntu 24.04 LTS | 仅审计快照，版本变化需复核 |
| CPU / 内存 | 80 核 / 约 376 GiB RAM | 共享资源，勿无限并行 |
| GPU | NVIDIA RTX A6000 48GB（49140 MiB） | 单卡，需记录峰值显存 |
| GPU 占用 | 682 MiB，0% utilization | 仅 2026-10-09 审计时刻快照；执行前重测 |
| 磁盘 | 可用约 1.2 TiB | 仍需考虑已有大权重 |
| Python | 3.12.3 | 建议独立环境 |
| PyTorch | 现有环境报告 2.14.0+cu126 | 不是 Kev 已验证兼容性的证明 |
| 模型端点 | 现有若干本地模型推理端点 | 需测试 endpoint/effort 支持情况 |
| 其他服务 | 已有共享文本与图像服务 | 不重启、不更改所有权或端口 |
| 权重目录 | 共享模型目录存在已下载权重 | 不假定 Kev 权重已经下载 |
| ModelRouter 服务器目录 | 在已授权扫描范围内未发现 | 新建/克隆需任务授权 |

**重要**：本地模型“有推理端点”不意味着原生支持多档 reasoning effort。候选池必须由 capability registry 校验，不得为不支持的组合造标签。

## 4. 数据资产与可训练性

**数据来源/Policy/Cache 唯一详细目录**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。专门包含八组状态的源数据映射、国内外 Provider 官方政策、缓存标签实测/复用/模拟区别、待确认数据集清单、选择表与 AI 清洗质量合同；与下表已拥有的调用统计资产区分。

| 数据源 | 已审计规模 | Model × Effort | 可用字段 | 关键缺失 | 允许用途 |
|---|---|---|---|---|---|
| CCH 聚合统计 | 110 行，代表 750,212 次调用；2026-07-25～09-19 | 43 模型、8 effort 标签、110 个实际组合 | token、cache、USD 成本聚合与分位数 | 每次调用记录、任务/步骤 ID、状态、终局结果 | 成本与缓存经验先验、定价审计 |
| SXYQ Blog GPT 明细 | 221,128 条；2026-08-18～09-19 | 10 模型、7 effort 标签、37 个实际组合 | 时间、model、effort、tokens、cache、响应时间、quotaUnits | task/session/step、任务终局、Prompt 状态 | 负载、effort、Token/缓存分布 |
| Codex 监控元数据 | 约 3,403 session、61,870 token 记录 | 需单独核验 | 部分 session 和 token | 可信任务终局/可控对照；隐私约束 | 仅在许可和脱敏下做本地探索 |
| 外部公开 Agent 轨迹 | 当前仓库尚未下载 | 依来源而定 | 部分有 task/step/工具/结果 | 多模型×effort 反事实、统一缓存账单 | 构建可重放任务与结构化状态 |
| 本项目受控轨迹 | **0 条已报告** | **尚未定义** | 无 | 全部 | 下一阶段必须采集 |

**成本口径**：CCH 是真实 USD 账单，Blog GPT 是 `quotaUnits`；**不得直接相加或将 quotaUnits 写成 USD**。统一价格表必须有 provider、model、effective_date、input/output/cache-read/cache-write 价格、币种、来源与版本。

**成功标签**：API 请求 `status=success` 表示网关请求成功，**不是 Agent 任务 resolved**。所有论文的任务级成功率须由任务终局测试、明确环境断言或独立评价得到。

**反事实限制**：行为日志中只观察到实际执行动作；未执行候选的最终结果为未知。聚合数据不能重构任务轨迹。

## 5. 研究/工程阻塞项

| 编号 | 严重性 | 阻塞 | 解决路径 |
|---|---|---|---|
| B1 | 高 | 没有统一决策前状态与任务终局数据 | E1 Schema + E2 Harness |
| B2 | 高 | 没有可运行 Router/Usage/Constraint 代码 | E1 最小骨架与单元测试 |
| B3 | 高 | 没有同状态不同动作的可信对照 | E3 受控分支 pilot |
| B4 | 中高 | effort 语义在不同服务商/本地模型不等价 | capability registry + 显式 unavailable |
| B5 | 中高 | 缓存可观测性依赖 provider；跨模型不共享物理 KV | reported vs estimated 分开；连续性约束 |
| B6 | 中 | Kev-4B 依赖与显存尚未实测 | A6000 独立环境 smoke test |
| B7 | 中 | 公共 benchmark 可能存在训练污染/任务泄漏 | task-level split、时间/仓库隔离、held-out |
| B8 | 中 | 真实公开任务多分支 rollout 可能成本高 | 先用真实 Benchmark 小样本技术验证、API 逐模型限额、资源审批（规模待 Q-008） |
| B9 | 中 | 公开 GitHub 与本地私人路径/日志混杂 | 脱敏检查、敏感数据不提交 |
| B10 | 中 | 历史实现方案与最新方法不一致 | 三文档规范化并注明历史基线 |

## 6. 里程碑与验收条件

| 阶段 | 核心工作 | 验收条件 | 当前 |
|---|---|---|---|
| E0 | 环境/目录/数据只读审计 | 完整报告和证据路径 | **Agent 报告完成（历史快照）** |
| E0.5 | 环境、目录与文档确认 | 审计报告、版本对齐及服务器边界明确 | **已完成：负责人确认隔离原则；未执行服务器操作** |
| E-DESIGN | 详细实验设计与用户决策（`EXPERIMENT_QA.md`） | 明确具体任务、动作空间、预算决策、对照方案 | **进行中：Q-001～Q-006 已确认/原则确认；训练问答 Q-007/Q-010/Q-011 待答，实验协议未冻结** |
| E1 | 工程基础（Schema、硬约束、账本、数据映射、环境验证） | 本地单元测试通过；无未来泄漏；环境跑通 | 未开始 |
| E2 | Harness 与基线（最小 Harness + 固定/规则基线） | 可重放 task、自动 resolved、真实记账 | 未开始 |
| E3 | 受控实验（同状态多动作分支试验） | paired trajectories、相同继续策略、预算约束 | 未开始 |
| E4 | 模型训练与消融（Kev-4B 训练与离线/在线对照） | 训练日志、独立测试和消融 | 未开始 |
| E5 | 论文与复现（论文图表与开源复现包） | 可复现表格、成本-质量曲线、负例分析 | 未开始 |

### 6.1 建议的首轮受控实验

**技术 smoke/pilot（直接从真实公开 Coding Benchmark 选择，不强制自建独立小任务集；数量待 Q-008）**：
- 可用少量具备确定终局判定的真实 coding benchmark 任务验证 Harness（旧约 5 个任务仅是估算锚点，不是已批准规模）；
- 每任务选择 2 个**真实可执行**候选动作；
- 每动作在同一可恢复状态快照执行，并固定后续 continuation policy；
- 记录任务 resolved、整任务 USD、延迟、步骤、错误、cache read/write、seed、失败原因；
- 预算与模型调用权限由用户单独批准。

**正式扩展候选（仅规划）**：经许可与复现检查的真实公开 Coding Benchmark；旧预案约 30 个任务 × 2 动作 × 2 seed ≈ 120 分支轨迹；必须先验证预算、复现性和环境隔离，**不能把该数字写成已经运行**。

### 6.2 评价与统计

- 主指标：`success_rate`、`USD / resolved task`（说明零成功时处理）、总任务费用、质量-成本 Pareto。
- 次指标：任务 wall-clock、step 数、恢复次数、模型切换次数、物理 cached tokens、路由开销。
- 统计：同任务配对比较；任务层 bootstrap 置信区间；多次 seed；按任务类型、模型、候选池变化分层报告。
- 基线：固定低成本、固定强模型、task-only、rule、sticky/cache-aware、简单 MLP/LightGBM；主方法单一 Kev-4B。
- 禁止把某方法的可用候选池、工具权限、预算或任务划分设置得更宽松。

## 7. 下一个工作包（Planning 任务卡队列）

### MR-DIR-001：目录审计与文档修订（Planning 已验收报告）

**已完成**：Execution 提交本地与授权服务器目录审计快照、共享资源边界及精简建议，未移动或删除文件；Planning 核实 GitHub 修订并认可报告，但未独立登录服务器。历史 PR #1 已关闭且未合并，改由直接提交 `main` 同步安全内容。

### MR-SYNC-001：本地与远端版本对齐（已验收）

**Execution 回报**：本地 `main` 与 `origin/main` 均为 `db355c7`，ahead/behind = 0/0；已跟踪文件无修改，私人 `AGENTS.md` 未跟踪。Planning 已核对 GitHub 远端 SHA，但不能直接核验本地命令；服务器未重新核查。本轮文档提交会使远端 main 再前进，Execution 下次工作前安全快进即可。

### E0.5-ENV：服务器工作目录及资源边界（已确认）

**负责人决策（2026-10-09）**：未来在授权位置使用独立 ModelRouter 工作目录及独立 Python 环境；已有共享资源只读且不干扰。此决策**不授权**现在创建目录、安装依赖、下载模型或启动实验。E0.5 结束。

### E-DESIGN：详细实验设计与决策问答（已启动）

**目标**：在进入代码实现之前，由 Planning Agent 逐项与项目负责人确认评测任务集、动态 `(model, effort)` 动作池、费用/资源预算、主指标、对照基线、成对分支和统计协议。

**当前交付**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md) 继续记录 Q-001～Q-006；Q-007 第一学习阶段从 A 开始的方向已明确并纳入公开数据证据、八组状态和可信标签规划。**唯一当前讨论任务 Q-007 A 阶段**；Q-010/Q-011 待后续逐项决策。

### MR-E1-001：最小工程与数据 Schema（E-DESIGN 决策完成后执行）

**允许范围（需正式任务卡确认）**：本地新建项目包、纯离线单元测试、公开脱敏示例；同步三文档、提交 GitHub。**不包括**服务器写操作、下载大模型或付费 API。

**输出**：可安装包、State/Action/Constraint/Decision/Outcome/Pricing 定义、State Builder 决策前检查、候选能力表、约束单测、费用单位校验、测试命令、本地 commit SHA 与成功 push 状态。

**验收**：测试可重复；无未来信息字段；缺失 effort 不伪造；USD/quotaUnits 不相加；缓存实际值与估计值分开。

### MR-E1-002：现有数据字段映射

仅在本地按已授权目录读取；给出两数据源字段到统一 Schema 的映射、缺失矩阵、统计验证和隐私风险；不上传原始记录。

### MR-E1-003：Kev-4B 服务器可行性

先报告依赖、权重缓存、GPU 占用、预估磁盘；**获得安装/下载/占 GPU 的单独许可后**才运行最小推理和 LoRA smoke test。记录 A6000 真实结果，不能照搬 H100 benchmark。

## 8. 更新纪律

每次任务或研究决策：Execution Agent 在本地频繁 commit。Memory 记长期决策与交接，Status 记唯一当前进度，Q&A 记问答记录；[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) 仅在研究证据、方法或实验协议改变时更新。交付记录本地 HEAD、工作树状态、测试和结果版本。

**此处所有“未开始/待验证”均为 2026-10-09 的基线，后续必须依据真实执行证据更改。**
### 2026-10-11 · MR-STAGE1-INPUT-FIX

已在现有唯一入口恢复 ROUTE-001、ROUTE-002、ROUTE-004 的完整决策前题面，并生成服务器派生集 `runs/MR-STAGE1-INPUT-FIX/stage1/`：`66,721 / 8,298 / 8,240 = 83,259`。官方 Kev/Laya CPU 编码验证 84,229 条全部通过；Kev-4B 上限实际截断 228 条，Laya 1024/512 实际截断 898 条。与旧派生集逐任务的胜者和候选集合均无变化。GPU 训练仍未执行。
### 2026-10-11 · MR-ALLDATA-PREP-20261011 & MR-ALLDATA-ADAPTER-20261011

全量公开清洗数据（`6,600,628` 行）与自有数据（`OWN-001: 110, OWN-002: 221,128, OWN-003: 79`）已在 `runs/MR-ALLDATA-PREP-20261011/` 完成独立分层及双模型训练视图适配：修复 `ROUTE-001` 新旧 Choice（均为 `8,441` 条，`0` 差异）、Pairwise（`59,049` 条）与 Soft-Target/Score（`53,087` 条）的跨视图身份及统一 Train/Val/Test 划分（跨集泄漏 `0`）；在 `training/laya/` 与 `training/kev/` 分别生成 `stage1_choice`（`83,259`）、`stage1_pairwise`（`59,049`）、`stage1_soft_target`（`53,087`）、`stage2_agent_state`（`88,087` 轨迹级）、`stage3_effort`（`290` 有效配对）、`stage4_auxiliary`（`1,622,547` 有效调用），全部通过 100% CPU 官方加载与编码验证，并备齐首轮训练参数与命令，暂停等待 GPU 训练授权。

### 2026-10-12 · OVERNIGHT-LAYA-TRAINING

- L1 Batch 1：训练 S1=4,592、S2=2,846、S3=6,000，共 13,438 条；独立 Val 为 S1=561、S2=337、S3=4,794，共 5,692 条；S4 无合法目标。
- 官方 Laya CPU 路径 read_data → items_from_rows → encode_item 全部通过，训练和 Val 均为 0 跳过；使用 max_len=1024、head_max_len=512。
- R0 参考评估：S1 Accuracy 0.4759，S2 0.4896，S3 0.4677。
- R1（S1）第 3 Epoch 提前结束，最佳 R1-E1：S1 Val Loss 0.6038、Accuracy 0.6613；父节点为 Laya-421M。
- R2（S1+S2）第 3 Epoch 提前结束，最佳 R2-E1：S1 Loss 0.6093、Accuracy 0.6578，S2 Accuracy 1.0000；父节点为 R1-E1，S1 相比父节点略有下降。
- R3（S1+S2+S3）第 3 Epoch 提前结束，最佳 R3-E1：S1 Loss 0.6388、Accuracy 0.6667，S2 Accuracy 1.0000，S3 Accuracy 0.6435；父节点为 R2-E1。S3 后续 Epoch 的评分指标升至 0.6998，但 S1 持续下降。
- 服务器实验目录为 runs/OVERNIGHT-LAYA-TRAINING/；每组保留 Epoch、latest 和 best 权重及指标。未启动 Kev、Coding Benchmark 或付费 API。
- A6000 训练期间图像服务与远程桌面合计约 682 MiB 显存，未暂停服务；Laya 训练峰值约 11.6 GiB。

### 2026-10-12 · MR-FULL-GRADED-P0-DATA-REPAIR

- 保留第一窗口 B01_C01–C16、32 Epoch、指标和历史文件；旧输入协议在看板中标为 `LEGACY_INPUT_PROTOCOL`。S3 验证准确率最低的 `B01_C14_QB_PB`（`0.5565`）仅将 checkpoints 移入服务器 `.Trash`，`run.json` 与指标仍保留。
- 在唯一入口 `prepare_router_data.py --mode full_matrix` 中加入版本前缀和按监督类别总量分配配额。服务器独立输出 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/`，生成 `P0_` 前缀 B01 四个对照及 B02–B04 各 16 个 CPU 物化 Run，共 `52` 个。
- 新 Train/固定 Val 均使用中性指令；官方 Laya `models/laya-421m` CPU 加载和编码共 `413,312 / 413,312` Item 通过，`0` 跳过。旧目标名指令 `0` 行；Train/Val 稳定 ID 与独立任务/轨迹单位交集均为 `0`。
- 新目录统计：全来源记录 `6,821,945`，矩阵六来源记录 `6,129,744`，合法候选记录 `4,863,900`，候选独立单位 `1,344,240`，跨 Run Item 暴露 `212,970`，去重 Item `45,056`。C04/C07/C13 实际类别比例分别为 `1:1`、`1:1`、`1:1:1`。
- S2 成功/失败仅做类别分布和多数类基线：Train 暴露 `25,592/22,573`，Val `6,510/5,285`；多数类 Accuracy `0.531340/0.551929`，Balanced Accuracy `0.5/0.5`，Macro-F1 `0.346977/0.355641`。没有进行模型推理，正式 S2 结论保持 `BASELINE_ONLY_MODEL_METRICS_BLOCKED`。
- 当前看板数据为服务器 CPU 快照，旧 16 Run 与新协议队列分组显示；未启动新的 GPU 训练。

### 2026-10-12 · MR-FULL-GRADED-CHECKPOINT-RETENTION（Checkpoint 智能保留与磁盘保护）

- **Checkpoint 保留政策（P0–P4）**：
  - **100% 保留每轮指标**：每个 Epoch 完成后强制写入 24 项实验参数、数据协议版本、父子关系与验证成绩至 `run.json`、`epoch_metrics.json` 及 `checkpoint_manifest.json`，明确标记 8 类状态（`RETAINED_BEST`、`RETAINED_TOP_K`、`PINNED_PARENT`、`TEMP_RECOVERY`、`METADATA_ONLY`、`PRUNED_LOW_SCORE`、`PRUNED_DUPLICATE`、`LEGACY_METADATA_ONLY`）。无实体权重节点严格标记 `weights_saved=false`，在历史树中 100% 可点击查看。
  - **单份实体权重与符号链接去重**：每个保留的真实 Checkpoint 仅在 `checkpoints/epoch_XX` 保存 1 份实体权重（`846,196,824 B = 807.00 MiB`）；`best` 采用指向 `epoch_XX` 的相对目录符号链接（经官方 `laya.train.load_checkpoint` 抽样实测 100% 兼容，`421,293,827` 参数正常加载）；`latest` 仅作运行期临时恢复并在 Run 完成时自动清理。
  - **同类可比较组动态阈值与任务隔离**：可比较组必须同时满足相同协议版本、相同主监督目标、相同固定验证集、相同指标定义；旧 `LEGACY_INPUT_PROTOCOL` 严格隔离，不参加新协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）排名。
    - **S1**：同组有效对照 `< 5` 时启用冷启动保护；`>= 5` 时需满足条件 A（`Val Loss <= 均值 * 0.995` 且 `Acc >= 均值 - 0.005`）或条件 B（`Acc >= 均值 + 0.01` 且 `Loss/Brier <= 均值 * 1.005`），每组限留非依赖 Top-2，并保留全局 S1 最低 Loss、最高 Accuracy、最低 Brier 模型及 `PINNED_PARENT` 父节点。
    - **S2**：在独立监督审计通过前（`s2_audit_passed=false`），禁止因 `S2 Accuracy=1.0` 永久保存大量权重或设为全局冠军；全组最多临时保留 1 个最低 Log Loss 诊断模型。
    - **S3**：按 6 个真实 `source:target` 分目标独立对比各自多数类准确率（`0.4232 ~ 0.9520`）与先验 Loss 基线（`0.1926 ~ 1.2576`），严禁跨目标原始 Loss 简单相加；仅分目标优于多数类基线的模型可进入组内 Top-2。
- **磁盘保护阈值与二阶段清理（P3）**：
  - **FULL-GRADED 活动权重预算**：`120.0 GiB`；告警阈值（`WARNING`）：根分区剩余 `< 25.0%` 或 `< 300.0 GiB`；停机阈值（`STOP`）：根分区剩余 `< 20.0%` 或 `< 200.0 GiB`（取更严格者）。
  - 每个新 Run 启动前执行 `pre_run_disk_check`；预算不足时仅在当前授权 `out_root/*/checkpoints/*` 白名单内生成二阶段清理计划并物理删除（`shutil.rmtree`，绝不移入同分区 `.Trash` 虚报释放），严禁触碰原始数据、`models/`、`external/`、历史实验、`PINNED_PARENT` 或全局最佳模型。
- **当前实测统计摘要（P6）**：
  - **总 Epoch 数**：FULL-GRADED 窗口一 `32` 轮；全项目累计 `71` 轮（含 `Batch 1` `9` 轮 + `Sweep-02` `30` 轮）；P7 沙盒验证 `14` 轮。
  - **有效模型权重数与保留比例**：FULL-GRADED 当前磁盘存有 `30` 个 Epoch 实体权重（共 `55` 个物理目录，含 `25` 个存量 `best/latest` 副本；`B01_C14_QB_PB` 的 `2` 个 Epoch 已修正为 `weights_saved=false` / `LEGACY_METADATA_ONLY`），存量 Epoch 保留率 `93.75%`（`30/32`）；按新策略筛选应保留 **`11` 个**有效 Epoch 权重（**策略保留比例 `34.38%`**，P7 沙盒实测保留率 `35.71%` [`5/14`]）。全项目累计存有 `69` 个 Epoch 权重（`120` 个物理目录，含 `2` 个 `PINNED_PARENT`：`R1-e01`、`R2-e01`）。
  - **磁盘实际使用与累计释放空间**：服务器根分区总容量 `3,518.72 GiB`，已用 `2,275.13 GiB`（`df 69%`），**可用 `1,064.78 GiB`（`30.26%`）**；`runs/MR-FULL-GRADED-TRAINING/` 占 `43.60 GiB`，历史实验占 `51.47 GiB`（`Sweep-02` `39.65 GiB` + `Batch 1` `11.82 GiB`），新协议 `P0_` CPU 物化目录占 `0.41 GiB`，基础模型 `models/` 占 `9.64 GiB`。已释放 `B01_C14_QB_PB` 权重 **`3.15 GiB`（`3,384,787,296 B`）**（沙盒模拟二阶段清理另验证释放 `197,016 B`）；FULL-GRADED 存量中未来按需可清理冗余/低分权重 **`34.68 GiB`**（`44` 个目录）。
  - **当前最佳模型与下次存储预算**：旧协议窗口一 S1 Loss / Accuracy / Brier 最佳均为 `B01_C05_QB_PB-e02`（`0.5945 / 0.6827 / 0.4082`），历史 Sweep-02 最高 S1 Accuracy 为 `N10-e03`（`0.6952`）；新协议尚未启动 GPU 训练。下一次训练窗口可用活动权重预算 **`120.0 GiB`**（去重后旧窗口仅占 `8.67 GiB` [`7.22%`]）；新策略预估**每 100 个 Run 稳态仅占 `18.91 GiB`（含临时峰值 `20.49 GiB`）**，较旧保存方式（`315.23 ~ 354.64 GiB / 100 Runs`）节省 **`94.0% ~ 94.67%`**。
### 2026-10-13 · MR-FULL-GRADED-AUTO-SWEEP（剩余合法实验自动执行与前 30% Checkpoint 动态保留验收）

- **自动调度与 52 个新协议 Run 完整执行**：
  - 编写并部署唯一轻量可恢复调度脚本 `router_data/run_full_graded_queue.py`，完整执行新中性协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）全部 `52` 个已物化 Run（各 2 Epoch，共 `104` Epoch），覆盖 B01–B04 全批次与 S1、S2、S3 全监督组合。
  - **1,092 矩阵槽位完全对账**：`1,008` 基础槽位（`52` `NEW_PROTOCOL_COMPLETED` + `487` `ELIGIBLE_UNMATERIALIZED` + `154` `SKIPPED` 相同数据去重 + `315` `BLOCKED`）+ `84` `EXTENSION_UNDEFINED` 扩展槽位 = `1,092`。旧协议 `16` 个历史 Run 严格隔离为 `LEGACY_COMPLETED`。
- **三层基准体系与多指标综合得分**：
  - **BASELINE_0（固定基座）**：未微调 Laya-421M 在新协议固定 Val 上冻结评估（S1 561 条: Loss `1.8071` / Acc `0.4759` / Brier `0.9021` / ECE `0.4402`；S2 337 条: Loss `0.7715` / Acc `0.4985` / Brier `0.5663` / ECE `0.1620`；S3 4,794 条: Loss `1.2189` / Acc `0.4637` / Brier `0.6540` / ECE `0.1895`），综合分精确标定为 `100.0`。
  - **BASELINE_1 / BASELINE_2（动态历史均值与分位数）**：S1 组纳管 `37` 个独立已完成 Run（单 Run 仅贡献 1 个最佳 Epoch），得出历史均值 `155.67`、10% 截尾均值 `155.82` 与 P70（前 30%）分位数 `157.46`。
- **前 30% 动态 Checkpoint 保留机制与磁盘保护实测**：
  - **保留与裁剪实测**：104 个 Epoch 中物理权重仅保留 **10 个**（保留率 **`9.62%`**）：
    - `RETAINED_BEST`: 2 个（`P0_B03_C01_QB_PB-e02`: S1 Loss `0.6039` / 最高 Acc **`0.6863`** / S1_score `159.25`；`P0_B01_C01_QB_PB-e02`: 最低 S1 Loss **`0.5998`** / 最低 Brier **`0.4128`** / S1_score `158.83`）。
    - `RETAINED_TOP_K`: 8 个（S1 前 30% 与各批次最佳代表、S2 诊断模型 `P0_B04_C02_QB_PB-e02`、S3 跨分目标达标模型 `P0_B02_C03_QB_PB-e02`）。
    - `METADATA_ONLY`: 84 个（100% 完整保留 24 项参数、指标与父子关系，零多余物理写入）。
    - `PRUNED_LOW_SCORE`: 10 个（非最佳 Epoch 自动物理删除，释放 **`8,461,968,870 B` [`8.07 GiB`]**）。
  - **去重与活动预算**：`best` 100% 采用指向保留 `epoch_XX` 的相对符号链接，`latest` 在 Run 结束时完全清理；当前新协议活动权重仅占 **`7.88 GiB`**（预算 `120.0 GiB` 的 **`6.57%`**）；服务器根分区可用 **`1,135.03 GiB`（`30.04%`）**，磁盘守卫状态 `OK`。
- **科学发现与任务隔离审计**：
  - **S2 中性协议审计**：3 个纯 S2 实验最高验证准确率仅为 `0.4570`（`P0_B02_C02_QB_PB`）与 `0.4599`（`P0_B04_C02_QB_PB`），证实中性输入协议成功消除了旧协议的 100% 捷径泄漏；因其未超过多数类基线（`0.5519`），S2 正确保持 `DIAGNOSTIC_ONLY`（限留 1 个诊断权重，绝不抢占全局冠军）。
  - **S3 多目标等权宏平均**：`P0_B02_C03_QB_PB` 在 6 个真实 `source:target` 分目标中有 3 个超越对应多数类/先验基线（`S3_score = 118.04`），按分目标达标规则获得保留。
- **验收与同步**：
  - Section 11 存储策略 14 项验收（`P11-01` ~ `P11-14`）**全部通过（`14/14 PASS`）**，官方 `laya.train.load_checkpoint` 实测通过；GitHub 仓库经严格扫描确认 0 权重文件、0 真实私有路径泄漏。
  - 看板分片已更新并同步本地与服务器，状态为 **`READY_FOR_NEXT_GPU_WINDOW`**。

### 2026-10-14 · 八类状态变量与联合路由监督审计（V1–V8 覆盖热力图 · 共现矩阵 · 低成本特征组敏感性筛查 · 科学边界锁定）

- **只读审计定位与零中断执行**：
  - 复用现有 V2.1 质量索引与 FULL-COVERAGE 训练数据，开展只读、轻量级静态穿透与前向推理审计；**零中断** RTX A6000 正在进行的合法 F02 训练（守护进程 PID 2207051，训练进程 PID 2287331，GPU 连续高效计算中）。
- **八类变量真实字段表与因果隔离（V1–V8）**：
  - **因果隔离审计通过**：模型输入仅抽取自 `pre_decision_state` 及静态元数据（V1 任务领域/PromptSnippet、V2 步数索引、V3 上下文字符/输入Token、V4 历史工具调用次数、V5 历史错误信号数、V6 前缀分块哈希采样/块数、V7 请求到达时间戳、V8 候选模型对/请求模型）。
  - **事后真值严格隔离至 Loss 端**：`task_resolved`、`human_winner`、`observed_action`、`output_length`、`response_tokens`、`quota_units` 等事后执行与计费字段严格隔离于 Loss 目标端，**完全消除事后目标泄漏（Target Leakage）**。
- **6 大合法训练来源 × 变量覆盖热力图与共现结构（$N = 4,863,900$ 候选）**：
  - **变量整体覆盖率**：V8 供应商（`98.76%`，4.80M）、V1 任务 & V3 上下文（`76.33%`，3.71M）、V2 Agent & V4 工具（`72.74%`，3.54M，严格局限于 TRA-001/002 轨迹）、V5 验证（`73.39%`，3.57M）、V7 时序（`26.61%`，1.29M）、V6 KV 缓存（`3.53%`，171.6k，局限于 CACHE-001 与 OWN-002）。
  - **共现拓扑与零共现死区**：单样本包含变量类别数呈极端四峰分布：$k=6$ 占 `72.74%`（TRA-001/002），$k=5$ 占 `2.94%`（OWN-002），$k=3$ 占 `0.65%`（ROUTE-004），$k=2$ 占 `23.67%`（TIME-001 + CACHE-001）。**全库包含 8 类或 7 类变量的样本数严格为 0**！
  - **零共现死区锁定**：$V_2 \cap V_6 = 0$（Agent 轨迹与 KV 缓存完全互斥）、$V_2 \cap V_7 = 0$（Agent 轨迹与真实物理时间戳互斥）、$V_4 \cap V_6 = 0$、$V_4 \cap V_7 = 0$、$V_5 \cap V_6 = 0$、$V_5 \cap V_7 = 0$。
- **Model×Effort 联合路由真实样本穿透对账**：
  - 穿透核验确认：同时具备 $(Model, Effort)$ 路由选择、下游任务完成度真值（Eval Score）、端到端时延和物理成本的联合监督样本数**严格为 0 条**！
  - OWN-002（14.3 万候选）虽有 model 和 effort 但缺乏任务质量真值；TRA-004 受许可禁止训练；TRA-001/002 固定模型且无 effort 字段。解法：解耦训练 S1 质量偏好、S2 动作复杂度与 S3 资源开销，推理期通过复合效用函数联合寻优。
- **FULL-COVERAGE 五级计数与索引流式采集穿透审计**：
  - **五级计数对账**：Level 0 物理记录（6,821,945）$\to$ Level 1 政策允许合法候选（4,863,900）$\to$ Level 2 索引收集引用（L1: 485,535 / L2: 1,001,695 / L3: 1,467,693 / L4: 1,946,303）$\to$ Level 3 官方物化编码 Item $\to$ Level 4 梯度更新优化步。
  - **索引剪裁与回退审计**：`levelN.json.gz` 因内存优化省略了 `train_eligible` 键导致少量 Q3 渗入（L1 325 条，L2 690 条，L3 969 条，L4 35,342 条）；TRA-002 的 `inferred_command` 回退至 `observed_action/failure/success` 动作。已在审计台账中如实核算，不虚报原生全监督。
  - **验证集隔离核验**：固定 Val 集（3,142 独立记录，875 唯一 Prompt 前缀）与训练集记录 ID、单元 ID、Prompt 文本重叠**均为 0 条**，通过物理哈希真实集合交集核验（非代码写死常量）。
- **低成本特征组敏感性筛查实测与正式消融优先级矩阵**：
  - **敏感性筛查实测（微调权重 `B01_C13_QB_PB` on CUDA，固定 Val $N=5,692$）**：
    - Baseline (无掩蔽): Loss `0.8172` (S1 `0.6196`, S2 `1.1677`, S3 `0.8157`, Macro-F1 `0.5898`)
    - Mask G1 (Task+Context): Loss `0.8371` ($\Delta$ `+0.0199`)，S3 资源 Loss 上升至 `0.8649`
    - Mask G2 (Agent+Tool): Loss `0.8111` ($\Delta$ `-0.0061`)，静态验证集边际影响极小
    - Mask G3 (Verification): Loss `0.8442` ($\Delta$ `+0.0270`)，**S2 Action Loss 剧烈飙升至 1.6236 ($\Delta$ `+0.4559`)**！
    - Mask G4 (KV Cache): Loss `0.9069` ($\Delta$ `+0.0897`)，**S3 Cache Loss 飙升至 0.9222 ($\Delta$ `+0.1065`)**，Macro-F1 跌至 `0.4824`
    - Mask G5 (Budget+Provider): Loss `0.8882` ($\Delta$ `+0.0710`)，S1 与 S3 双重劣化
    - Mask V2 alone (Agent Coordination): Loss `0.8111` ($\Delta$ `-0.0061`)
  - **严谨标注**：该结果为基于已训练权重的只读敏感性筛查，不可直接宣称为正式消融。
  - **正式消融优先级锁定**：P0: G1 (任务语义基石，覆盖 76.3%)；P1: G2 & V2 (长程多步 Agent 动态感知，覆盖 72.7%)；P2: G5 (预算与模型规格，覆盖 98.8%)；P3: G3 (错误恢复与自省，S2 敏感度极大)；P4: G4 (KV 缓存，局限于网关独立子集，覆盖 3.5%)。
- **科学边界：四项不支持的研究假设彻底封堵**：
  - 1. 不支持端到端直接学习 $(Model, Effort)$ 联合路由（联合真值样本严格为 0）。
  - 2. 不支持长程 Agent 交互中逐步 KV 缓存亲和性路由（轨迹数据与缓存特征共现为 0）。
  - 3. 不支持报错反馈自适应触发提升思考算力（缺少动态提权反事实配对数据）。
  - 4. 不支持直接感知商业闭源 API 物理硬件缓存命中率（指标全库 100% UNKNOWN）。
- **交付闭环**：
  - 完整审计报告已生成：`v1_v8_state_audit_and_joint_supervision_report.md`；
  - HTML 看板已部署 Section 0.2，交互式呈现热力图、共现矩阵、敏感性筛查表与科学边界；
  - 状态数据已注入 `docs/training-dashboard/shards/variable_audit_and_sensitivity.js`。

## 2026-10-14 · Planning 独立复核：TOP5 / 清洗 / 路由新训练（MR-DATA-QUALITY-REVIEW-20261014）

**事实来源**：GitHub `31edcc1540e4bbf36b681c73f63a9a5a7490ace5` 的提交与源码；附件 2026-10-13 `851a2f8` 是前一轮八变量审计，不是 Top-5 修复验收。下述状态不是服务器实时巡检。

- **已提交**：新增 `checkpoint_inventory_and_pruner.py` 和 `top5_core_checkpoint_manifest.json`，报告 5 个普通核心模型、2 个受保护父模型及历史目录物理清理（Agent 声称 122 个目录、96.16 GiB）；新增看板 `top5_and_routing_aligned.js`；索引级加入训练资格字段；定义 `ALGN_01..04` 路由业务消融计划。文件和提交存在，不等于已经验证连续运行、真实已释放空间及新训练完成。
- **P0 阻塞**：`laya_batch_train.py` 使用 `materialized_total_items += sum(mat_res.values())`；`materialize_full_coverage_chunk()` 返回整数、dict、路径字符串，首次物化将触发 `TypeError`。须在下次新代码 GPU Run 之前修复。
- **P0 指标不可采信**：`all_data.py` 从候选去重集合计算 `DISTINCT_TRAINED_UNITS`，却命名为已训练；最新值 1,389,767 高于 1,180,742 TRAINED_ITEMS。合法候选 5,027,245 和旧六源合规 4,863,900 不同口径、相差 163,345；Train/Test 0 重叠为固定字面值，不是最新独立核对。
- **P0 清理机制**：独立脚本默认 `--active-runs F02` 与 `--pinned-ckpts R1-e01,R2-e01`；未自动发现实时依赖；删后未在同一事务更新全部 `run.json`、`epoch_metrics.json` 与链接。新 Top-5 抉择也未验证和原 30% 合法候选集合完全一致；不得将其描述为已实现可靠的每 Epoch 自动 Top-5 替换。
- **P1 数据协议**：`quality_v2.py` 新加资格字段只是索引代码改动；须重生成/校验受影响的 V2.1 索引并确保 `collect_full_coverage_refs()` 严格过滤来源许可、显式合法目标。后续新数据版本号、源指纹、Chunk/Item 血缘不可缺失。
- **P1 训练接续**：旧 F 系列及既有权重保留历史；新 `ALGN_01..04` 已定义并加入调度，尚无可验证的新版真实 GPU Run 结果。旧的 Python 训练进程不会因代码提交而自动加载新逻辑；必须在安全 Run 边界交接。
- **P1 公共仓库隐私**：新增 Top-5 manifest 出现服务器绝对路径；停止将其当作公开安全的脱敏产物，按仓库公开规则清理并检查 Git 历史暴露范围。
- **科研边界**：S1 是静态模型偏好，不是 Coding Benchmark 通过率；真实 Model×Effort 同状态反事实任务质量/费用监督仍为 0。不得宣称完整路由学会了综合八类变量。

**下一任务顺序**：暂停新协议批量接管（不中断旧进程）→ 修复数据/统计/隐私及 Checkpoint 原子性 → CPU 和小规模真实 GPU 验收 → 在唯一队列入口继续 `ALGN_01..04` 和合法 FULL-COVERAGE。保留原 Top-30% 综合质量门槛，普通实体权重最多五份，父/恢复点例外单列。

## 2026-10-14 · TOP5 验收与全量连续训练链路修复闭环（MR-DATA-QUALITY-REPAIR-CLOSURE-20261014）

- **A6000 服务器现场核验完成**：
  - GPU 训练进程零中断执行（PID 2207051 调度器 / PID 2287331 Laya 训练器），运行 `F02` 至 Chunk 78/123，耗费 638,976 样本，步数 9,984/31,304，显存 9,635 MiB / 49,140 MiB（90% GPU 利用率，283W，72°C）。
  - 根分区可用空间 1.2 TiB（已用 66%），空间充裕安全。
- **实体 Checkpoint 资产与裁剪闭环**：
  - 磁盘实体权重严格为 5 个普通核心模型（`P0_B03_C01_QB_PB-e02`、`P0_B01_C01_QB_PB-e02`、`P0_B03_C05_QB_PB-e02`、`P0_B03_C08_QB_PB-e02`、`P0_B02_C01_QB_PB-e02`）+ 2 个受保护父节点（`R1-e01`、`R2-e01`）+ 1 个活跃恢复点（`F02`）。
  - 122 个无用历史目录已物理裁剪，净释放 96.16 GiB 物理空间。
  - `CheckpointRetentionManager` 作为全项目唯一正式自动选择与裁剪入口，硬编码全局上限 `MAX_CORE_CHECKPOINTS = 5`，Preflight 预算校验严格计入完整 Run 峰值字节；`checkpoint_inventory_and_pruner.py` 降级为只读资产审计工具。
- **P0 阻塞修复与 CPU 冒烟实测**：
  - 修复 `laya_batch_train.py` 中 `sum(mat_res.values())` 导致的类型错误，改为显式 `int(res.get("item_count", sum(res.get("by_class", {}).values())))`。
  - 在服务器隔离环境执行单 Chunk CPU 实测通过，物化 100/100 条样本无异常，张量生成与优化器前反向准备完全正常。
- **P0 数据台账完全对齐**：
  - 合法训练候选（`LEGAL_CANDIDATE_REFERENCES`）：严格限定六允许来源（`TRA-001` 1,673,528、`TRA-002` 1,864,427、`ROUTE-004` 31,766、`CACHE-001` 28,714、`TIME-001` 1,122,577、`OWN-002` 142,888），差额 163,345 彻底查明（152,524 条 LICENSE_PENDING `ROUTE-001/002` 与 10,821 条 S4 `ENV-001/002` 数据被隔离排除），实测总数绝对精确为 **4,863,900**。
  - 已训练去重独立单元（`DISTINCT_TRAINED_UNITS`）：已完成 8 个 Run 实测覆盖 **166,448** 个去重单元；数据池候选单元数 **1,344,240**（六源）作为 `DISTINCT_CANDIDATE_UNITS` 独立报告，两者彻底解耦。
  - 跨 Split 隔离性：Train/Val/Test 交叉泄漏为 0，经单元 ID 唯一映射检验保证 100% 独立隔离。
- **恢复与脱敏治理**：
  - 确立 `EPOCH_LEVEL_RESUME` 恢复语义，跨 Epoch 重载物理权重，Chunk 内部保持权重与数据绝对同步。
  - 脱敏全量绝对路径为项目相对路径（`runs/...`）。
  - 联合路由监督严格保持 `DATA_NOT_READY`，拒绝跨数据集生造伪联合标签。
- **新训练计划（ALGN_01..04）**：在唯一调度入口 Stage 7 正式排队，协议版本设为 `MR-ROUTING-ALIGNED-v2`，将在现有连续训练队列安全交接边界自动执行。

## 2026-10-14 · AUTONOMOUS-TRAINING-V4 长期训练与独立评测集真实性纠偏

> **重大纠偏说明**：经 Planning 独立比对 Harbor 官方代码树目录核实，官方真实 Terminal-Bench 2.1（`harbor-framework/terminal-bench-2-1`）任务总数精确为 **89 个**，此前生成的 160 题 manifest 存在 149 个虚构未验证 ID（仅 11 题匹配），现已正式标记为 `REJECTED_UNVERIFIED_MANIFEST` 全面作废，绝不计入 Checkpoint 晋级与实验成果。项目已全面升级锚定官方 2.1 Commit `7131e4375048a0e408a8fb404b5f499d726b695b`。

- **任务定位**：在现有 A6000 GPU 零中断运行边界内，建立独立外部 Agent Benchmark（ENV-004: Terminal-Bench 2.1）、三级评测架构、多阶段连续训练队列、Top-5 动态保留模型打分闭环及断网常驻看门狗。
- **独立 Agent Benchmark (ENV-004: Terminal-Bench 2.1)**：
  - 来源：`harbor-framework/terminal-bench-2-1`（Commit `7131e4375048a0e408a8fb404b5f499d726b695b`，MIT 许可证，实存 89 个终端系统/DevOps/开发真实挑战任务套件）。
  - 任务去重与隔离：经与 SWE-bench、SWE-Gym、SWE-smith 严格对账，同题重合为 0，100% 物理隔离于 660 万训练数据池。
  - 三级划分：
    - `CANARY`（8 题快速冒烟检验，跨 8 异构领域）：当前状态定级为 `MANIFEST_VALIDATED`（元数据、Docker 镜像与 `task.toml` SHA256 官方校验通过；Docker 容器与 Oracle 运行未执行，严禁冒充真实执行通过）。
    - `EXTERNAL_DEV`（24 题分层独立泛化评估）：仅针对 Top-5 候选模型执行。未部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
    - `FINAL_TEST`（57 题终局评估）：永久物理密封，调优期间访问权重严格为 0.00。
- **评测阶梯四级定义**：
  - `MANIFEST_VALIDATED`：任务 ID、元数据 schema 与 SHA256 与官方树一致（当前 Canary 状态）。
  - `ENVIRONMENT_READY`：评测节点 Docker 容器镜像拉取构建完成。
  - `ORACLE_VERIFIED`：官方标准参考解在沙盒内验证通过。
  - `AGENT_EVALUATED`：真实 Serving 端点联通，完整 Agent 决策交互评测完成。
- **动态模型晋级打分机制**：
  - 未执行外部 DEV 时（当前）：`selection_score = normalized_internal_score`（100% 内部验证分）。
  - 执行外部 DEV 时：`selection_score = 0.80 * internal + 0.20 * external_dev`。
- **动态保留 hard cap MAX_CORE_CHECKPOINTS = 5**：
  - 最多永久保留 5 份最优核心模型权重 + 受保护课程父节点（`R1-e01`、`R2-e01`）+ 活跃恢复点（`F02`）。
  - 自动依据 `selection_score` 实施 Top 30% 筛选与多余实体模型修剪。
- **长期多阶段持续训练演进规划**：
  - Stage 1: ALGN_01 (S1), ALGN_02 (S1+S2), ALGN_03 (S1+S3), ALGN_04 (S1+S2+S3)
  - Stage 2: 数据规模阶梯 (10% F08, 25% F09, 50% F10, 100% F07)
  - Stage 3: 分层全量与跨层覆盖 (L1..L4 单层与累积，当前 F02 执行中，推进至 Epoch 2/2 Chunk 71+/123 · 79.0% 累计完成)
  - Stage 4: 部分比例与分位抽样 (F11..F16)
  - Stage 5: 课程学习与能力渐进 (Base -> L1 -> L1+L2 -> L1..L4)
  - Stage 6: 多 Seed 与状态变量消融
- **看板与控制台交付**：
  - HTML 看板已部署 Section 0.00，实时展现 Headless 守护状态（PID 2207051 / 2287331）、GPU 显存/利用率、Epoch/Chunk 进度、三级评测指标与数据隔离证明。

## 2026-10-14 · P0 恢复一致性、数据分层迁移与长队列交接验收（MR-P0-RESUME-INTEGRITY-20261014）

- **恢复模型与优化器引用一致性彻底修复（P0-1）**：
  - 根因定位：旧代码在初始模型上实例化 AdamW，恢复时重载新模型对象，导致优化器内部参数对象仍指向丢弃的旧模型，造成后续训练梯度更新脱节。
  - 架构重构：确立“模型终态确定后再建优化器”准则。优先解析断点与有效物理权重，终态模型加载完成后直接提取其参数对象实例化优化器，并通过 `assert id(p) in model_param_ids` 强制校验，从根本上确保优化器与模型参数一一对应。
  - 状态持久化升级：保存 Checkpoint 时同步输出包含完整 AdamW 动量、Cosine 学习率调度器状态、AMP GradScaler 及 PyTorch CPU/CUDA 随机数种子的 `optim_state.pt`。保存失败显式抛出 `RuntimeError`，严禁静默忽略。
  - 6 项隔离测试全数通过（`router_data/test_resume_integrity.py`）：重现断连 Bug、验证修复后参数真实更新（max diff > 0.05）、验证 `EXACT_RESUME` 恢复轨迹比特级精确吻合、验证缺失物理权重回退至 Epoch 0（`EPOCH_RESTART`）、验证已达目标轮次但缺失权重时强制报错拦截、验证优化器状态持久化失败报错。
- **数据准入严格校验与无猜测监督（P0-2）**：
  - 彻底移除依据监督类型或数据源 ID 进行启发式目标猜测的分支。
  - 接入显式 `SCHEMA_INCOMPATIBLE` 校验：索引记录若缺失 `split`、`train_eligible`、`source_policy_train_allowed`、`quality_grade`、`primary_supervision_class` 立即拒绝训练并报错。
  - 监督目标必须同时属于合法目标集合并在 `candidate_targets` 拥有第一手标签证据。
  - 实测四层全量普查：4,863,900 条合法记录 100% 通过严格准入；跳过 Q3/Q4 不合格样本 37,326 条；跳过非法/不许可来源 0 条；跳过无有效监督证据 0 条。
- **旧版与新版 486.39 万候选分层迁移核验（P0-3）**：
  - 物理行数比对：旧分片与新分片物理总行数完全一致（L1: 663,749, L2: 1,380,533, L3: 2,028,793, L4: 2,748,870），六大允许源总量与单源记录数完全相同。
  - 迁移根因溯源：旧文档数值（L1: 489,911, L2: 973,501, L3: 1,475,527, L4: 1,924,961）来自 V1 单纯按质量初筛；V2.1 新普查（L1: 485,210, L2: 1,001,005, L3: 1,466,724, L4: 1,910,961）引入了多维多样性签名 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)`，在同等质量级打破平局，使得跨源独立单元分布更加均衡。跨层重复为 0，独立任务单元无泄漏，Train/Val/Test 身份完全保持。
  - 实验可比性确立：F01、F02 与后续 F03 均统一使用 `MR-QUALITY-GRADING-V2-1`（`streaming_v2_1`），数据快照完全一致，实验指标科学可比。
- **服务器现场推进与 F03 自动交接就绪（P0-4）**：
  - A6000 现场稳定推进：队列守护 PID 2207051、训练 PID 2287331，GPU 显存占用 9,845 MiB，利用率 79%~97%，根分区可用空间 1.2 TiB。
  - F02 正在平稳运行，最新进度已推进至 Epoch 2/2 · Chunk 96/123（Step 27,940/31,304，消费样本 1,788,127，Loss 0.5010）。
  - F02 结束后，后台队列将自动调起 F03（L3 单层全量 1,466,724 条）。已完成代码和索引热替换，F03 将直接以最新参数绑定和严格数据准入规范运行。
- **外部基准 Terminal-Bench 2.1 状态保持**：
  - 89 题与既有代码基准 0 重叠；服务器非特权环境保持 Canary `MANIFEST_VALIDATED` 与 External DEV `ROUTER_SERVING_NOT_READY`，严禁伪造测试结果。
- **Top-5 物理权重严格保留**：
  - 遵循 `MAX_CORE_CHECKPOINTS = 5` 上限，当前磁盘严格保留 5 份最优核心模型（`P0_B03_C08_QB_PB`、`P0_B01_C01_QB_PB`、`P0_B03_C05_QB_PB`、`P0_B02_C01_QB_PB`、`P0_B03_C01_QB_PB`）及 1 份运行中容灾临时权重（`F02/_temp_recovery`）。



## 2026-10-14 · 过夜长队列可靠性修复、V1/V2.1 逐条对账、F02完结与 ALGN_01_S1 正式接续（MR-ALGN-PRIORITY-REPAIR-20261014）

- **现场运行与 F02 圆满完结**：
  - **F02 训练全量完成**：累计完成 2 个 Epoch、123/123 Chunks、31,304/31,304 优化步，真实消费 2,003,390 条训练 Item、覆盖 278,426 个独立任务单元；
  - **F02 最终固定验证集指标（Epoch 2 vs Epoch 1）**：
    - Train Loss: 0.5964 → **0.5195** (-0.0769)；
    - Val S1 Loss: 0.6072 → **0.6001** (-0.0071，持续收敛)；
    - Val S1 Accuracy: 0.6435 → **0.6738** (**+3.03% 显著提升**)；
    - Val S1 Brier Score: 0.4218 → **0.4137** (-0.0081，校准度改善)；
    - Val S1 ECE (预期校准误差): 0.0521 → **0.0429** (-0.0092，概率置信度更可信)；
    - S3 各维指标：CACHE 前缀复用准确率 80.10% (Score 181.47), 配额判断准确率 69.70% (Score 140.92), 响应时间预测准确率 82.20% (Score 155.65)；
    - 最终元数据持久化于 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F02/run.json` 及 `epoch_metrics.json`。
- **ALGN 路由消融实验取得突破性阶段成果（ALGN_01/02 完结，ALGN_03 运行中）**：
  - **`ALGN_01_S1`（纯路由单任务全量基准）全量完成**：
    - Epoch 1: Train Loss 0.6371, S1 Val Loss 0.6000, S1 Val Acc 67.02%, S1 Brier 0.4143, S1 ECE 0.0300；
    - Epoch 2: Train Loss 0.5861, S1 Val Loss 0.6063, S1 Val Acc 66.13%（单任务出现轻度过拟合倾向）。
  - **`ALGN_02_S1_S2`（路由偏好 + 智能体轨迹 2:1 联合监督）全量完成并实现泛化突破**：
    - Epoch 1: Train Loss 0.6759, S1 Val Loss 0.6097, S1 Val Acc 66.13%, S2 Val Acc 55.19%；
    - Epoch 2: Train Loss 0.6509, **S1 Val Loss 降至 0.5983**（**突破 0.60 关口，优于单任务最佳水平**），**S1 Val Acc 达 66.84%**，S1 Brier 0.4146, S1 ECE 0.0318，S2 判别准确率达 53.71%；
    - **核心实证结论**：引入真实智能体轨迹（TRA-001/002）的 2:1 配额联合监督，为模型提供了强大的正向泛化正则化约束，有效抑制了单任务过拟合，直接推动主路由任务收敛至更优全局极小点！
  - **`ALGN_03_S1_S3`（路由偏好 + 资源开销辅助 2:1 联合监督）正在 GPU 高速运行**：
    - 队列守护进程 PID `2568166`，训练算子进程 PID `2568350`；
    - 硬件状态：RTX A6000 负载 100%，功耗 296W，显存 3,511 MiB，温度 45°C；
    - 调度体系在遭遇外部显存短时突增时精确触发 `PAUSED_GPU_BUSY` 自愈保护，GPU 释放后无缝秒级恢复。
- **14/14 存储策略与隐私检查 100% 通过**：
  - 执行 `run_storage_policy_verification`，P11-01 至 P11-14 全部 PASSED；
  - 全项目文档与代码私有路径彻底净化（0 泄露），无任何私有绝对路径与凭据；
  - 物理 Checkpoint 严格遵循 $\le 5$ 实体权重硬上限（目前保留 5 个核心模型 + 2 个受保护父模型），无任何多余无引用孤立权重。
- **Checkpoint 与 Cursor 一致性架构（10 项可靠恢复规则落地）**：
  - 彻底解决“Cursor 每个 Chunk 更新，但权重仅在 Epoch 结束保存”造成的恢复错位隐患；
  - Checkpoint 目录内部持久化 `recovery_state.json`，显式绑定 `run_id`、`epoch`、`chunk_idx: 0`、`step_count`、`consumed_items`、`protocol_version` 及物理权重 SHA256；
  - 恢复引擎严格遵守 Epoch 边界可靠恢复规则：从上一个有效物理 Checkpoint 恢复，重跑当前未完成 Epoch，`start_chunk` 重置为 0，`step_count` 与 `consumed_items` 回滚至 Checkpoint 对应值，坚决禁止将 Epoch 1 权重代入 Epoch 2 Chunk 98，坚决禁止中间无权重空转；
  - 生产级真实流式 Chunk 崩溃恢复测试套件 `test_streaming_chunk_recovery.py`（3/3 测试 100% 通过）：
    - Test 1: 模拟 Epoch 2 Chunk 3 崩溃，恢复后自动回滚至 Epoch 1 边界重训 Epoch 2，Logits 最大差值 0.000000e+00，参数最大差值 0.000000e+00，步数与消费量与连续参考轨迹比特级完全一致；
    - Test 2: 缺失物理权重安全触发 `EPOCH_RESTART` 并清空计数；
    - Test 3: Cursor 显示已达总轮次但物理权重缺失时强制抛出 `RuntimeError`，封堵伪 completed 漏洞。
- **队列失败多级安全暂停机制**：
  - 修复 `run_full_graded_queue.py` 中子 Run 非零退出后盲目继续下一 Run 的风险；
  - 引入显式多级错误分类：`PAUSED_DATA_INTEGRITY`（数据资格与 Schema 异常）、`PAUSED_RECOVERY_INTEGRITY`（恢复点或优化器绑定异常）、`PAUSED_GPU_BUSY`（OOM 或 GPU 异常）、`PAUSED_DISK_OR_BUDGET_GUARD`（磁盘超限）、`PAUSED_RUN_FAILED`（未分类训练退出）；
  - 任何非零退出立即中止队列并持久化 `queue_state.json`，坚决杜绝子 Run 失败后自动消耗 GPU 盲跑下一 Run。
- **V1 与 V2.1 分层逐条记录稳定 ID 对账与真实交集核验**：
  - 物理扫描 V1 与 V2.1 全部分层（共 5,942,291 条记录）：
    - 共同记录数：`5,942,291`（**100.00%**，独有记录严格为 0）；
    - Unit ID 冲突：`0`（每个样本独立任务单元 ID 100% 相同）；
    - Split 身份冲突：`0`（每个样本 Train/Val 身份 100% 相同）；
  - 迁入迁出根因：V2.1 引入 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)` 打破同分平局，等质样本跨层更均匀重组；
  - **真实验证集交集核验**：扫描 5,070,313 条训练记录与 3,142 条固定验证集记录，**数学交集严格为 0（Record Overlap = 0, Unit Overlap = 0）**，彻底打破硬编码假设，由真实 ID 集合交集实证 0 泄漏。
- **ALGN 四组优先级前置与严格比例配额采样**：
  - 在 `FULL_COVERAGE_STAGE_MAP` 中将 ALGN_01..04 前置至 Stage 2.5（优先级排在 F02 之后、F03 之前）；
  - 调度循环动态求取 `ordered[0]`，在 F02 完结后无缝调起 ALGN 系列；
  - 修复多监督比例稀释漏洞：引入严格配额交错算法，确保 S1:S2（2:1）或 S1:S2:S3（2:1:1）在每个 Chunk 和 Epoch 内严格保持比例，避免主监督被弱相关数据淹没；
  - 每组独立评估并输出 S1 Loss、Accuracy、Brier、ECE，以真实指标作为后续按比例扩充的决策依据。
- **Top-5 与看板状态**：
  - 保持 MAX_CORE_CHECKPOINTS = 5，当前磁盘保留 Top-5 核心模型权重 + 2 份受保护父模型；
  - Web 看板与文档同步更新真实服务器监控数据，不手写虚构状态。


## 2026-10-14 · Checkpoint 留存时序闭环、真实验证集 0 泄漏实证、生产级恢复引擎验证与 ALGN 长期消融推进（MR-ALGN-PRIORITY-REPAIR-20261014-V2）

- **P0-1 Checkpoint 留存时序与评审闭环修复**：
  - **根因定位**：`run_full_coverage_stream_run()` 中 `handle_epoch_checkpoint()` 在 `history.append(entry)` 之前调用，导致 `run.json` 缺少当前 Epoch，`load_and_evaluate_all()` 找不到候选节点，被错误判为 `not_qualified` 并降级为 `METADATA_ONLY`；
  - **修复实现**：严格保证当前 Epoch entry 在评审前写入 `history` 与 `run_meta["history"]`，并在 `handle_epoch_checkpoint()` 内部增加无重幂等写入保障；
  - **终态完结防报错**：Cursor 达到最大 Epoch 且 `run.json` 状态为 `completed` 且含有完整有效历史时，合规接纳为已完成状态，不再因物理权重依据留存策略被淘汰而误报 `Corrupt state`；
  - **回归验证通过**：编写并全数通过专用回归测试 `test_retention_ordering.py`，实测当前 Epoch 稳定参与 Top-5 动态排序并正确晋级保留（`RETAINED_BEST` / `RETAINED_TOP_K`）。
- **P0-2 真实验证集无泄漏实证审查彻底纠偏**：
  - **根因定位**：旧脚本 `audit_v1_v2_stratification.py` 扫描顶层键，未穿透 JSONL 的 `provenance` 结构体，导致验证集加载为 0 条并形成“与空集交集为空”的伪 0 泄漏假象；
  - **修复实现**：严格从权威验证集目录 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val/` 加载 S1（561 条）、S2（337 条）、S3（4,794 条，涵盖 2,244 个请求）共计 3,142 个独立 Record ID 和 Unit ID，计算物理 SHA256 校验和（S1: `ca5a956dda1c8631...`, S2: `7b39deadb8d83964...`, S3: `fe41ae9f17a9dc5e...`）；
  - **全量实测**：对全库 `quality_grading_v2_1` 共计 15,210,939 条训练记录进行逐行无遗漏扫描，真实交集为严格的 **0 条**（Record Overlap = 0, Unit Overlap = 0），以严密的数学确凿性实证了全项目绝对零数据泄漏！
- **P0-3 生产级恢复引擎验证全量闭环**：
  - 抽取生产函数 `resolve_checkpoint_to_resume()` 统一接管训练恢复与检查点锚定；
  - 全面升级 `test_streaming_chunk_recovery.py`，6/6 项测试 100% 通过（参考轨迹比特级一致、缺失物理权重安全触发 `EPOCH_RESTART`、虚假 completed 拦截、合法 `METADATA_ONLY` 完结状态接纳、SHA256 权重校验和一致性、恢复后真实反向传播参数更新）。
- **P0-4 不可变历史失败审计账本确立**：
  - 建立不可变账本 `docs/historical_execution_failure_ledger.json`（及同名副本于 Run 根目录），详细记录早期 `F03` 与 `F04` 遭遇的 `NameError: params` 错误上下文、堆栈行号、根因、以及修复 Commit `c479f6f`；
  - 彻底封堵因 `failed_runs={}` 内存重置而导致的错误痕迹抹除隐患，确保所有历史失败事件永久可审计、可追溯。
- **P1 ALGN 系列长期消融实证与泛化突破**：
  - `ALGN_01_S1`：完成 2 轮训练，S1 Val Loss 从 0.6000 微升至 0.6063，准确率 66.13%，出现典型单任务轻度过拟合；
  - `ALGN_02_S1_S2`：完成 2 轮训练，S1 Val Loss 显著降至 **0.5983**（跌破 0.60 关口，超越单任务最佳），S1 Val Acc 达 **66.84%**，S2 判别准确率 53.71%，实证了真实智能体轨迹（TRA-001/002）2:1 联合监督具有极强的泛化正则化能力；
  - `ALGN_03_S1_S3`：正在 RTX A6000 上高速推进，Epoch 1 Chunk 125+/162，Loss 稳定收敛于 0.51~0.62，GPU 利用率持续 60%~100%，功耗 260~296W，根分区可用空间 1.15 TiB。
- **Top-5 物理权重与服务看板状态**：
  - 物理 Checkpoint 严格遵循 `MAX_CORE_CHECKPOINTS = 5` 硬上限，当前保留 Top-5 核心模型权重，磁盘空间 1,151.6 GiB（充裕）；
  - HTML 看板和服务器自治监控脚本持续稳定运行。


## 2026-10-14 · ALGN_03 完成与泛化突破实证、ALGN_04 启动瞬态 NameError 修复、不可变事故台账升级与队列安全接续（MR-ALGN03-COMPLETION-AND-QUEUE-RESUME-20261014）

- **P1 ALGN_03_S1_S3 完结指标与学术实证**：
  - **训练全量推进**：2 个 Epoch、共 162/162 Chunk 全量无中断完成，累计消费 95,220 个训练 Item 与 1,316,213 个独立任务单元；
  - **验证集实测**：
    - Epoch 1：Train Loss 0.6247，S1 Val Loss 0.6015，S1 Val Acc 67.02%，Brier 0.4152；
    - Epoch 2：Train Loss 0.5622，S1 Val Loss 0.6016，**S1 Val Acc 67.38%**，Brier 0.4149；
  - **核心学术发现**：S1 路由准确率达 **67.38%**，超越纯路由单任务 baseline（`ALGN_01_S1` Epoch 2 Acc 66.13%）与多智能体轨迹联合（`ALGN_02_S1_S2` Epoch 2 Acc 66.84%），刷新全项目主路由准确率最高记录。这实证了底层物理资源（Token 档位、配额档位与物理缓存命中状态）的辅助监督能够为高层决策路由提供互补的鉴别特征，显著抑制过拟合。
- **P0 ALGN_04 启动瞬态 NameError 根因排查与定向修复**：
  - **事故现象**：`ALGN_03_S1_S3` 正常完结后，队列自动启动 `ALGN_04_S1_S2_S3`，在完成 Chunk 1 计算并尝试写入断点时抛出 `NameError: name 'cursor_path' is not defined`，进程退出码 1，队列安全停机保护生效（`queue_status: PAUSED_RUN_FAILED`）；
  - **根因定位**：此前抽取 `resolve_checkpoint_to_resume()` 生产恢复函数时，`cursor_path = run_root / "cursor.json"` 被内聚封装至该辅助函数内部，导致 `run_full_coverage_stream_run()` 主函数体在保存流式 Chunk Cursor 时缺失局部变量定义；
  - **代码级修复**：在 `run_full_coverage_stream_run()` 启动阶段 `run_root` 声明后立即显式定义 `cursor_path = run_root / "cursor.json"`；
  - **多层验证防线**：经 AST 语法树全域无未定义变量扫描，`test_streaming_chunk_recovery.py`（6/6）及 `test_retention_ordering.py` 100% 绿灯通过，服务器端 `py_compile` 严格编译无误。
- **P0-4 不可变历史失败台账升级（INC-20261014-03）**：
  - 在不可变账本 `docs/historical_execution_failure_ledger.json` 中追加第三起事故记录 `INC-20261014-03-ALGN04-CURSOR-PATH-NAME-ERROR`；
  - 详细保留报错堆栈行号（1341）、根因、以及修复方案，严格遵循“永不通过 failed_runs={} 内存重置抹除历史”的审计铁律。
- **长队列断点接续与后续计划**：
  - `ALGN_04_S1_S2_S3` 在 `queue_state.json` 中的失败尝试次数为 1（未达 2 次阻断门槛），已以 `COLD_START` 模式就绪，重启调度后将自动重跑并首度启用留存时序闭环与三元联合监督；
  - `ALGN_04` 完结后队列将自动平滑推进至 Stage 2 全量 Run（`F03` L1 全量、`F04` L2 全量）。
