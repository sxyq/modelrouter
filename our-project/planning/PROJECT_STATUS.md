# ModelRouter · 项目现状、资源条件与执行路线

> **最新状态：2026-10-12。** ModelRouter 研究目标是面向单 Agent / 多子代理任务，利用八类变量、Reasoning Effort、KV Cache、调用成本与 Trace 次数，在成功率约束下降低整任务成本。数据起点为 14 个公开清洗源 `6,600,628` 行；OWN-001/002/003 分别 `110 / 221,128 / 79` 行，单独统计。Laya-421M 已按授权完成 Batch 1 的 R0 参考评估与 R1→R2→R3 三组逐层训练，当前停止；Kev、Coding Benchmark 和付费 API 均未运行。

八类变量为 `Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`。

## 当前轮次

| 阶段 | 状态 |
| --- | --- |
| P0 清理 | 已移除实验目录 `training/laya/`、`training/kev/` 及六个旧通用视图目录。`MR-STAGE1-*`、原始数据、清洗数据、OWN 源、`models/`、`external/` 均保留 |
| P1 分级 | 从全量清洗源与三个 OWN 文件逐行处理。公开合计 `6,600,628`；OWN `110 / 221,128 / 79` 分开统计 |
| P2 分层 | 17 个来源分别按任务、轨迹、请求、偏好对战或聚合单元归组，唯一分配至 L1–L4；每层均有全部 17 个来源的实际记录 |
| P3 覆盖 | 八类变量逐层列出非空数、缺失数、监督/观察用途、许可与评测用途、Q4。真实运行时路由决策标签 `0` |
| P4 输出 | 服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/` 含逐源记录引用、四层引用、汇总 JSON、变量矩阵及五张表 |
| P5 Laya Batch 1 | 训练 `13,438` 条、独立 Val `5,692` 条；R1/R2/R3 均保留逐轮权重和指标，当前停止 |

公开记录层规模：L1 `663,963`、L2 `1,304,523`、L3 `1,993,193`、L4 `2,638,949`，总计 `6,600,628`。三类 OWN 记录逐层另列。按来源政策允许、Q1/Q2、真实目标及 Train 身份计算的候选记录数依次为 `489,911`、`973,501`、`1,475,527`、`1,924,961`，合计 `4,863,900`；Val/Test 身份归评测用途，不计作训练候选。候选包含轨迹终局、静态偏好、缓存复用机会、请求负载和 OWN-002 调用统计等不同目标，不代表联合路由监督。

逐源 Q1–Q4 总计：公开 Q1 `6,469,995`、Q2 `50,638`、Q3 `4,041`、Q4 `75,954`。ROUTE-001/002 的 `584,556` 行处于许可待核，未进入候选；ROUTE-005 保持仅分析，ROUTE-003、ENV、MEM 保持评测用途。Q4 内容状态可与许可待核重叠。

TRA 与 ENV 共有 `13,486` 条任务记录继承 TRA 已有 Train/Val/Test 身份（ENV-001 `150`，ENV-002 `13,336`），分割冲突 `0`；ENV 用途仍为评测。ROUTE-001 的 `24,441` 个完整题目组、ROUTE-003 的 `520` 个任务组均按真实身份保留。轨迹步骤、候选评测行和请求没有按独立任务计数。

逐项结果与五张交付表位于服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/tables.md`。Laya 结果位于服务器 `runs/OVERNIGHT-LAYA-TRAINING/`，看板源数据和公开 HTML 位于本仓库 `docs/training-dashboard/`；清洗源、模型原始权重和 Kev 资产未改动。R0–R3 使用验证集记录选轮，未运行 Test 终评；八类运行状态与真实路由决策、缓存和整任务成本的联合监督仍为 `0`。

本轮按授权停止。后续是否使用 R1、R2 或 R3 的最佳权重，以及是否启动 Kev 或受控任务评测，交由负责人决定。

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
