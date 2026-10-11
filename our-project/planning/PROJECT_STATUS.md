# ModelRouter · 项目现状、资源条件与执行路线

> **最新状态：2026-10-11。** 已阶段性结束「公开数据收集、清洗、Stage 1 静态样本纠偏」；**唯一当前小任务**为 `MR-STAGE1-INPUT-FIX`（在唯一主链中最小修正模型训练题面截断，并用 CPU 确认 Kev/Laya 第一批参数）。**已授权必要源码最小修改与 CPU 验证；未授权任何正式 GPU 训练、GPU 测试、付费 API 或 Coding Benchmark。** 此页首页是当前状态，以下历史快照不得倒灌覆盖。

## 一、总体项目进度

**科研目标**：在真实单/多 Agent 的合法决策时刻，依据任务、代理协作、上下文记忆、工具环境、验证恢复、KV 缓存连续性、时间费用、模型/服务状态等八组可观测信息，选择 `(model, reasoning_effort)`；在成功率约束下优化整任务费用、Trace 次数和缓存切换成本。最终有效性需要真实 Agent Harness 与受控实验，不能由静态分类准确率证明。

| 大阶段 / 工作 | 当前实际进度 |
| --- | --- |
| E0–E1：研究问题、数据源、环境、已有模型与 Smoke Test | 已完成主要准备；Kev/Laya 历史短训练与保存重载有执行汇总，不能称正式训练成果 |
| 数据收集、14 个公开源统一 CPU 清洗 | **阶段性完成**：`6,600,628` 行，覆盖轨迹、静态评测、缓存请求、工作负载、环境和记忆；另有 CCH/Blog 自有数据，不能按同一粒度简单相加 |
| Stage 1 静态训练样本纠偏与唯一处理链 | **已完成 `MR-STAGE1-FAST-FIX`**：修复 `ROUTE-001` 跨子集同题混拼、完全重复评测、胜者冲突，排除元路由器；保留唯一 `prepare_router_data.py` CLI + `router_data/` 内部模块 |
| Stage 1 修复版纯静态视图 | **`83,259` 题已生成**：Train `66,566` / Val `8,343` / Test `8,350`；Kev/Laya 现有 CPU 编码检查报告均 100% 通过 |
| **当前小任务：Stage 1 训练输入修正与训练配置** | **待执行/未收到完成报告**：实际训练 `state` 仍使用约 400 字符 `prompt_snippet`；已批准仅对相关部分作最小 CPU 修正，并确定 Kev/Laya 首批参数 |
| E2：Kev/Laya 正式微调与离线对照 | **尚未启动；GPU 未授权**。保持 A/B/C 分源分体制评测；`ROUTE-001/002` 许可状态 `LICENSE_PENDING`，不得写成已获授权 |
| E3–E5：Coding Benchmark、运行时缓存感知/多 Agent 动态路由、消融和论文 | **尚未启动**。同状态多动作、真实 KV 切换代价及整个任务回报的联合监督仍缺失 |

**两项不可混淆的状态**：`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY` 仅指 2026-10-11 `FAST-FIX` 已完成的版本及其既有 CPU 编码检查，**不包含后续题面完整性修复**；`RUNTIME_JOINT_DATA_READY = NOT_READY`（八组运行时状态 + model×effort + 真实缓存和费用的完整联合监督为 0，同状态中途反事实分支为 0）。所有证据依据 GitHub `main` 与此前 Execution 报告；Planning 未实时读取服务器中的完整 JSONL 或 GPU 进程。

## 二、当前阶段各小步骤

### A. 已完成的大块：数据清洗、正确性修正

1. **源与数量**：14 个已清洗公开源共 `6,600,628` 条不同粒度记录；自有 `OWN-001` CCH `110` 聚合行对应 `750,212` 次调用、`OWN-002` Blog `221,128` 逐调用行、`OWN-003` `79` 衍生汇总行（新增独立观测 `0`）；纠正了 `6,620,400`、Source ID 错位与重复相加。
2. **唯一处理链**：`prepare_router_data.py` 仍为唯一命令入口，8 种 `--mode` 保留；14 个公开源的独立适配保留于 `router_data/`，已冻结原始数据与历史导出未被 `FAST-FIX` 覆盖。
3. **Agent/思考记录**：TRA-001/002/004 轨迹共 `4,448,643` 行，其中 AgentSuite `273` 任务 × `30` 配置 = `8,190` 次配置评估，清洗展开 `41,430` 行；同权重运行时 Thinking 开关配对 `1,365`，专用 Thinking 权重对照 `273`，跨版本对照 `1,365`。这些不是完整相同中途状态的反事实路由标签。
4. **ROUTE-001**：`548,059` 次评估，原始 700 JSON 按完整 Prompt 哈希合并为 `24,441` 道独立题；去掉 `21,144` 条完全重复模型评测，隔离 `1,219` 道潜在胜者分数/费用冲突题，排除 `openrouter`，最终入 Stage 1 `8,441` 道合法纯静态胜者题。
5. **ROUTE-002**：`35,189` 条历史单标签中剔除 `87` 条同分同估价真并列，保留 `35,102`；候选顺序按固定种子确定性打乱。ROUTE-004 Arena 保留 `39,716` 条人类胜负偏好。AgentSuite `19` 条末轮配置胜者不混入 Stage 1 主训练。
6. **Stage 1 最终已有派生视图**：`ROUTE-004: 39,716` + `ROUTE-002: 35,102` + `ROUTE-001: 8,441` = **`83,259`**；Regime A `39,716`（人类偏好）、B `4,039`（质量唯一高分）、C `39,504`（同质量历史费用规则）；`16,360` 条分析池题、TwinRouterBench `970` 步隔离留出。两次导出文件 SHA256 相同，已有 Train/Val/Test ID/题面隔离验证与 Kev/Laya CPU 加载记录。
7. **费用与数据边界**：ROUTE-002 费用主要为 Token × 价目估算；ROUTE-001 上游正费用缺逐条结算来源；CCH USD 与 Blog quotaUnits 不混加。Mooncake 前缀潜在复用不等于供应商物理缓存命中。660 万行不等于 660 万个最佳路由标签。

### B. 唯一正在等待执行的小任务：`MR-STAGE1-INPUT-FIX`

- **现有代码实际缺口**：`router_data/route.py` 对 ROUTE-001/002 使用 `[:400]` 构造 `prompt_snippet`；`router_data/views.py` 的 ROUTE-001 训练 `state`、ROUTE-002 训练 `state` 和 Arena 训练 `state` 仍消费该摘要。完整 Prompt 哈希只保证去重身份，并不使模型训练自动看到全文。
- **已批准**：在唯一 `--mode views` 路径及必要既有函数内最小修复决策前完整题面；保留标签与划分，输出新的派生目录，只做必要 CPU 样本/编码核对；从现有官方 Kev/Laya 源码确定首批真实参数和拟执行命令。
- **未批准**：GPU 正式训练/推理、付费 API、下载依赖或模型、改写原始数据/冻结 JSONL、第二条流水线。上一轮 `FAST-FIX` 的 100% 编码通过不能代替此轮的全文 Token 截断统计。

## 三、后续唯一计划

**先执行 `MR-STAGE1-INPUT-FIX`，完成后停止并回报。** 如全文保留导致官方上下文窗口或候选标记受损，记录实际受影响题数并做必要最小修正；不得悄悄将过长输入称为“已完整可见”。输出本轮新的 `train/val/test` 数量、Regime A/B/C、Kev/Laya 有效交集与候选训练参数。正式 `E2-STAGE1-BATCH1` 只能在负责人之后明确批准 GPU 及数据使用范围时启动。

## 四、下一步执行提示词（给 Codex）

> 继续 ModelRouter 唯一 `prepare_router_data.py --mode views`，不新建任何工程化流水线。当前正式旧派生集 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/` 为 `66,566 / 8,343 / 8,350 = 83,259`；只针对 ROUTE-001/002/Arena 的模型训练题面被约 400 字符截断问题，在 `router_data/route.py`、`router_data/views.py` 及必要旧函数内实施最小 CPU 修正，从已有原始文件获取决策前全文，不泄漏未来结果、标签和评分；保留现有任务身份、A/B/C、候选与 split、原始/冻结文件；所有新派生输出定向 `runs/MR-STAGE1-INPUT-FIX/`，小样本先验，再仅核对受影响数据的 CPU 编码及真实 Token 截断/候选折叠。只读现有官方 Kev/Laya 训练代码并提出两个模型各一份未执行的训练参数与命令；不得调用 GPU、API、下载或开展 Benchmark。只更新必要已有文件，按已有授权审查后提交推送，五段汇报后停止。

## 五、简单情况说明

已经处理的是“把大量不同来源记录清洗好、分类好，并筛出可靠的静态模型选择题”。接下来要处理的是“让模型实际看到足够完整的题目，再决定怎么训练”。**当前还没有 Kev/Laya 正式训练结果，也没有证明 KV 缓存感知动态路由能节省任务总成本的实验结果。**

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
