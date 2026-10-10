# ModelRouter · 项目现状、资源条件与执行路线

> **版本 v2.0｜状态截止 2026-10-09｜依据：MR-E0-001 只读审计快照 + MR-DIR-001 目录审计快照 + GitHub main 实际核查**
>
> **读者**：项目负责人、实验执行人员、新会话 Planning Agent。**本文件首页是最新阶段、任务、阻塞和唯一下一行动的权威入口**。详细研究论证见 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)；Agent 交接规则见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据注意**：服务器、GPU、进程和数据规模来自本地 Execution Agent 于 2026-10-09 提交的审计快照，不代表 Planning Agent 直接登录复验，也不构成实时监控。公开文档刻意不包含服务器内网 IP、SSH 登录信息、内部主机名、用户家目录与私人绝对路径。

## 2026-10-10 新增当前工作包：全量数据分层、八组状态覆盖检查与目录规划（Planning 方案，未执行）

**最新用户要求**：不能仅核对 84,310 条静态模型选择数据，需检查全部 6,600,628 条清洗记录如何用于不同学习阶段、八组研究变量是否真实覆盖；同时盘点并规范本机/服务器目录，避免重复下载、重复脚本，任务结束清理独立临时文件。此任务优先于 E2 正式多轮模型训练；既有 Q-007 单胜者训练视图完成不等于整个动态路由研究已经 TRAIN_READY。禁止据此自动启动 GPU 训练。

**GitHub manifest 已确认的 14 个公开清洗来源**：Agent 轨迹 4,448,643 条（TRA-001/002/004），模型比较/研究参考 649,207 条（ROUTE-001..005），缓存与时间 1,443,926 条（CACHE-001、TIME-001），任务/记忆 58,852 条（ENV-001/002、MEM-003/005），合计 6,600,628。**这些是异构行/步/请求/评测记录，不是 660 万道可训练模型胜者题**。路由候选任务池 100,380，单胜者监督候选 84,310（其中 Train/Val/Test 份额仍因报告与 manifest 冲突而待服务器对账），并列/全败分析池 16,070，TwinRouterBench 独立评测 970 步。CCH/Blog 现有生产统计属另外的数据资产，不把聚合调用量重复计入公开数据。

**本阶段 5 个小步骤**：
1. **只读盘点**本机仓库和服务器目录，标记每个现存文件的用途、归属、体积、可否重建、是否重复、是否正在使用；不要先移动、删除、下载。
2. **按研究问题分层使用全部数据**：静态选择真标签、并列/全败候选结果、Agent 决策前状态与已执行结果、Thinking 成对 Episode、缓存/费用/时间测量、Coding 环境与长记忆评测。逐层统计可用**独立任务/轨迹/配对**，而非只报总行数。
3. **八组状态真实覆盖率**：逐来源逐字段报告「真实观测/统计估计/模拟/未知、决策前可见、缺失率、是否有可验证目标」；分别核查 Model、Reasoning Effort、KV 缓存、单次调用费用及整任务成功/费用。绝不能把不同任务的数据拼成同一条真实训练样本。
4. **先按任务/仓库/会话整体隔离，再分阶段生成按需轻量视图**；已有 84,310 单胜者数据只是静态选择阶段，不代表全数据被浪费。不得随机按 660 万原始行混合划分；不修改现有正式 train/val/test，除非找到确凿错误并报告影响。
5. **统一目录与临时文件生命周期**：保留现有项目根目录、原始只读数据、唯一 `prepare_router_data.py`、既有 Kev/Laya 训练格式、模型权重及外部官方代码；未来正式结果只在根下一个 `runs/<实验编号>/` 保存，临时文件只在同根 `.tmp/<任务专属随机目录>/` 并在任务结束自动清理；保留必要的实验日志和可复现结果，绝不删除仍在运行或来源不明的文件。完整方案见数据台账「6.13」。

**下一行动**：向 Execution Agent 下发「只读目录审计 + 分源/分阶段/八组状态覆盖统计 + 目录整改预案」，交付真实缺口与训练阶段建议；随后再就 Kev/Laya 的正式训练起点与任务选择作用户决定（Q-010/Q-011）。未授权不进行正式多轮训练、付费 API 或共享服务操作。

## 固定汇报格式（2026-10-10 用户确认，长期生效）

**适用场景**：用户每次提供 Codex / Execution Agent 的新执行结果，或要求汇报 ModelRouter 当前进度时，Planning Agent 必须**先汇报整体进度**，再按下面顺序回答。不要先堆满代码审查和术语。

1. **总体进度**：用容易理解的话说明项目目前走到哪里、已经完成什么、目前还差什么。可用简短的阶段表；不要编造整项目百分比。说明已核实、仅执行方报告和尚未验证的区别。
2. **当前阶段的小步骤**：列出本阶段 3–6 个具体步骤，标记「已完成 / 进行中 / 待确认 / 未开始」，每步说明结果、问题和剩余事项。优先说清用户现在最关心的事。
3. **后续计划**：只说下一步确实该做的任务，以及完成后会进入哪个阶段；不无限添加流程，不将建议当成用户已授权执行。
4. **详细的可复制执行提示词**：给当前 Codex 一份直接可用、范围明确的任务指令，包括检查哪些现有文件、按什么顺序做、怎样验证、交付什么、什么时候停止；先复用原有脚本和文件，禁止每次新建第二套流程。未授权不得启动正式 GPU 训练、付费 API、影响共享服务。
5. **通俗说明**：用 2–4 句话解释为什么现在做这件事、有什么风险、用户需要知道什么；专业术语不得替代解释。

**长度与风格**：首先给结论，语言简短直白；不重复以前完整的长篇背景。确有必要的文件名、提交号、样本数量和命令可以保留，但要解释它们意味着什么。

**文档职责与新对话**：最新阶段和下一行动仍以本文件实际证据为准；完整模板、执行报告接手规则及「新窗口最简启动提示词」以 [PLANNING_MEMORY.md 第 10 节](PLANNING_MEMORY.md#10-新会话恢复协议长期生效) 为准。用户发来新结果时应按职责同步必要文档，不是机械地每次重写全部五份。

**2026-10-10 待对账提醒（Planning 的 GitHub 文件复查，不是服务器直接实测）**：现有 `PROJECT_STATUS.md` 报告正式三组数量为 67,853 / 8,136 / 8,321，但同一远端提交的 `manifest.json` 与 `数据划分统计.json` 报告为 67,428 / 8,436 / 8,446，虽均合计 84,310，暂不得把二者同时当成唯一已冻结版本；此外 Source ID 与 Thinking 对照数在个别文件中存在冲突。下一步仅需**只读核实服务器正式文件行数及校验值，再定向统一记录**；不因此重做全部清洗或启动模型训练。

### 0.2 最新科研验收结论（Execution 2026-10-10 Q-007-FINAL 数据资产冻结、清洗最终验收与 Kev/Laya 训练前兼容性验证完成）

- **2026-10-10 Execution Q-007-FINAL 数据资产冻结、清洗最终验收与 Kev/Laya 官方 GPU Smoke Test 闭环**：
  1. **全量数据资产冻结与两次确定性复现 (P0–P1)**：
     - 完整核查注册表全部 **35 个 Source ID**（16 个已下载清洗、4 个自有生产日志、15 个明确标注缓装/归档原因），在 `our-project/data/公开数据/manifest.json` 冻结全部原始文件、清洗输出、训练视图的 SHA256、行数与字节数；
     - 连续运行两次 `prepare_router_data.py`（Run A vs Run B），8 个输出文件（4 个 Kev 视图 + 4 个 Laya 视图）SHA256 **100% 字节级完全一致**。
  2. **训练标签唯一性纯化与零跨集泄漏 (P2)**：
     - **LLMRouterBench 并列剔除**：将 12,188 题最高分并列且成本不可比（`cost_uncompared`）及 884 题最高分与实测美元成本均并列（`tied_score_and_cost`）的样本全部移出正式监督集，转入 `analysis_unsupervised_or_tied.jsonl`；仅保留 **9,386 题**严格唯一胜者（8,348 题最高分唯一 + 1,038 题最高分并列但实测 API 美元成本严格更低）；
     - **AgentSuite 唯一胜者**：仅保留 **19 题**严格唯一成功模型样本，246 题并列成功与 8 题全败保留在分析集；
     - **正式监督集锁定 84,310 条严格唯一单胜者样本**：`ROUTE-004` (Arena 39,716) + `ROUTE-001` (RouterBench 35,189) + `ROUTE-002` (LLMRouterBench 9,386) + `TRA-004` (AgentSuite 19)，分布为 `train.jsonl` (67,853) / `val.jsonl` (8,136) / `test.jsonl` (8,321)；另有 `analysis_unsupervised_or_tied.jsonl` (16,070 条) 与 `holdout_eval_twinrouter.jsonl` (970 条)；
     - **跨 Split 零泄漏**：修复短题面与纯标点题面分桶逻辑，Task ID、Exact Prompt、Canonical Prompt 在 `train/val/test/holdout` 四集合间两两交集均为 **0**。
  3. **官方开源代码全量格式验证与 GPU Smoke Test 100% 通过 (P3–P5)**：
     - **Kev 官方代码 (`kev` repo)**：85,280 条样本 100% 通过 `load_records -> materialize -> encode`（0 失败，最大 `state_tokens=1,636 <= 7,552`）；在 RTX A6000 上完成 `Qwen3.5-4B-Base + kev-4b-adapter` 真实 `kev.train` 前向/反向/参数更新（`--batch 2 --accum 4 --checkpointing 1`，峰值显存 **10.50 GiB**）与临时 Checkpoint 保存重载测试（`max_reload_prob_diff = 0.0`）；
     - **Laya 官方代码 (`laya` repo)**：85,280 条样本 100% 通过 `read_data -> items_from_rows -> build_sequence`（`skipped={}`，全量 102,424 个问题完美对齐）；在 RTX A6000 上完成 `laya-421m` 真实 `laya.train.finetune`（`rlcd` loss 由 `8.9714` 降至 `2.9823`，`soft-ce` loss 由 `8.9714` 降至 `3.5132`）与临时 Checkpoint 保存重载测试（`max_reload_prob_diff = 0.0`）；正式模型目录保持零改动。

**最新阶段判定：Q-007-FINAL 全部完成并冻结（DATA_FROZEN & SMOKE_TEST_PASSED）。项目执行优先顺序明确为：`数据最终验收 → Kev/Laya 模型训练 → 离线能力验证 → 大规模 Coding Benchmark → 动态缓存感知路由 → 论文实验`。下一步进入 E1/E2 正式训练阶段。**

## 0. 项目负责人进度看板（任务事件更新）

| 项目 | 当前 |
|---|---|
| **当前阶段** | **E-DESIGN / Q-007-FINAL 已完成：数据资产冻结（35 个 Source ID 清单 + `manifest.json`）、84,310 条严格唯一单胜者监督集纯化、两次复现 SHA256 100% 一致、Kev-4B 与 Laya-421M 官方 CPU/GPU Smoke Test 100% 通过** |
| **当前任务** | **Q-007-FINAL 全部收尾闭环。准备进入 E1（模型训练环境与最小运行验证）与 E2（Kev-4B / Laya-421M 正式训练与离线验证）** |
| **已完成** | **彻底完成 Q-007-FINAL 数据资产冻结、清洗最终验收与 Kev/Laya 训练前兼容性验证**：<br>1. **P0–P1 资产清点与确定性复现**：核对 35 个 Source ID，生成 `manifest.json`，两次独立运行 `prepare_router_data.py` 的 8 个 Kev/Laya 输出文件 SHA256 100% 一致。<br>2. **P2 标签唯一性纯化与零泄漏**：将 LLMRouterBench 12,188 题 `cost_uncompared` 并列与 884 题 `tied_score_and_cost` 并列移入分析集；正式监督集锁定 84,310 条严格唯一单胜者样本（Train 67,853 / Val 8,136 / Test 8,321），分析集 16,070 条，Holdout 970 条；跨 Split 的 Task/Exact/Canonical Prompt 重叠均为 0。<br>3. **P3–P4 官方加载器 100% 验证**：85,280 条样本 100% 通过官方 `kev` 与 `laya` 数据管线（0 跳过、0 失败）。<br>4. **P5 官方 GPU Smoke Test 100% 通过**：Kev-4B（峰值显存 10.50 GiB）与 Laya-421M（`rlcd` 与 `soft-ce`）在 A6000 上完成前向、Loss、反向、参数更新与临时 Checkpoint 重载一致性验证（`max_reload_prob_diff = 0.0`）。<br>5. **P6 逐项回答全部 13 个必答问题**，同步更新核心文档与 GitHub `main`。 |
| **正在等待** | Planning Agent 确认 Q-007-FINAL 验收报告并下达 E1/E2 正式训练指令 |
| **主要阻塞** | 无执行阻塞。Coding Benchmark 尚未启动，等待 Kev/Laya 正式训练完成后再规划批量运行 |
| **下一步** | **进入 E1/E2 正式训练阶段（Kev-4B 与 Laya-421M 多轮正式微调、校准与离线评测）** |
| **更新方式** | 本地频繁 commit；按阶段/里程碑定期 push 到 GitHub main；不设审批门禁，不开发第二套流水线 |
| **最近更新时间** | 2026-10-10：Execution Agent 完成 Q-007-FINAL 数据资产冻结、清洗最终验收与 Kev/Laya 官方 GPU Smoke Test |

**持续角色**：本 ChatGPT 为长期 Planning Agent、需求讨论与论文研究伙伴；本机 Codex/Execution Agent 负责本地文档同步/代码维护与服务器执行。研究讨论无需因执行任务尚在进行而中止；用户已选择的简单实验风格优先，不增加工程化门禁。新对话须阅读全部五核心文档并确认最新证据。

**通用新会话恢复顺序（不随阶段变化）**：

1. 核查 GitHub 最新 main HEAD 并读取**五核心文档（Status/Q&A/Memory/Research/Registry）**；**本文件首页唯一决定当前阶段、当前任务、阻塞和下一行动**，历史审计不是实时信息。
2. [EXPERIMENT_QA.md](EXPERIMENT_QA.md)：最新问题与已确认答案；[PLANNING_MEMORY.md](PLANNING_MEMORY.md)：D-ID、历史交接、完整通用新窗口启动提示词（第 10 节）；[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)：方法与证据。
3. **本次有效状态**：Q-001～Q-007-FINAL 全部完成并冻结；84,310 条严格唯一单胜者训练视图与官方 Kev/Laya 模型环境已通过 GPU Smoke Test 验证。
4. **执行范围**：服务器公开数据下载/CPU 清洗和本机 CodeX 同步/文献整理已由负责人明确要求；正式多轮 GPU 训练与付费 Coding Benchmark 批量运行按阶段指令推进。保留科研必要的数据隔离/标签真实性，不新增复杂工程门禁。
5. 后续阶段/决策/实验状态变化时更新本页和相关 Q&A/Memory，只有方法或证据变化才更新 Research；不制造空提交，不能在仓库正文写死永久最新 SHA。

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
| E4 | 模型训练与消融（Kev-4B 训练与离线/在线对照） | 训练日志、独立测试、消融/CI | 未开始 |
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

每次任务或研究决策：Execution Agent 在本地频繁 commit，并在工作会话结束、重要里程碑或最长 24 小时工作周期内 push。Memory 记长期决策与交接，Status 记唯一当前进度，Q&A 记问答批准；[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) 仅在研究证据、方法或实验协议改变时更新。交付记录本地 HEAD、远端 HEAD、ahead/behind、dirty、最近 push、测试和结果版本；不要求 PR。

**此处所有“未开始/待验证”均为 2026-10-09 的基线，后续必须依据真实执行证据更改。**
