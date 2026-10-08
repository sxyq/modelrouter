# ModelRouter · 项目现状、资源条件与执行路线

> **版本 v0.4｜状态截止 2026-10-09｜依据：MR-E0-001 只读审计报告 + GitHub main 实际核查**
>
> **读者**：项目负责人、实验执行人员。**本文件记录“已经有什么、还缺什么、何时算完成”**。详细研究论证见 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)；Agent 交接规则见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据注意**：服务器、GPU、进程和数据规模来自本地 Execution Agent 提交的 E0 报告，不代表 Planning Agent 直接登录复验，也不构成实时监控。公开文档刻意不包含服务器内网 IP、SSH 登录信息和私人绝对路径。

## 0. 项目负责人进度看板（任务事件更新）

| 项目 | 当前 |
|---|---|
| **当前阶段** | **E0.5：本地/服务器目录复核与文档交接治理（已完成审计与 PR）** |
| **当前任务** | **MR-DIR-001 审计报告与精简方案已提交 PR**，等待 Planning Agent 验收 |
| **已完成** | E0 只读审计报告；三文档拆分与规范化（`cb460e8`、`51d0eb2`、`789a65e`）；MR-DIR-001 本地与服务器最新目录只读复核、真实目录树提取与文档同步 |
| **正在等待** | Planning Agent 验收目录方案，并下发 MR-E1-001 任务卡 |
| **主要阻塞** | 尚未建立工程骨架（无代码无测试）；Kev-4B 权重与环境未在 A6000 部署；目录精简方案待批准 |
| **下一步** | Planning 验收 MR-DIR-001 → 下发 MR-E1-001（Schema / Pricing / 单元测试） |
| **更新方式** | 每个任务/里程碑由 Execution 更新并提交 GitHub；**不是后台自动监控** |
| **最近更新时间** | 2026-10-09；当前任务 MR-DIR-001 |

**文档分层**：Agent 交接历史 → [PLANNING_MEMORY.md](PLANNING_MEMORY.md)；给负责人看的稳定研究方案 → [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)；给负责人看的**最新进度** → 本文件。

### 0.1 本地与服务器最新实测核验结果（MR-DIR-001 快照）

1. **本地仓库（209 文件，251.3 MB）**：
   - 纯研究文档与数据仓库，目前暂无 `pyproject.toml`、`requirements.txt` 或可运行的 Python 代码。
   - `our-project/data/` 包含 CCH 聚合统计（110 行）与 Blog GPT 调用明细（221,128 行），缺失 `task_id` 与任务终局标签。
   - `research/` 包含 58 份论文 PDF 与 73 份截图资产；`external-projects/` 为 9 个微型卡片。
2. **服务器（RTX A6000 / `k3s-infra-01`）**：
   - **ModelRouter 代码目录**：服务器上暂未创建，无重复克隆。
   - **Kev-4B 权重**：在服务器模型与工作区目录中未检索到本地文件。
   - **硬件状态**：80 核 CPU、376 GiB RAM（346 GiB 空闲）、1.2 TiB 可用磁盘，GPU 显存占用仅 682 MiB / 49140 MiB（利用率 0%）。
   - **独立项目与共享边界**：共享模型权重池（>400GB）、已有在线推理服务与微调工作区，建议保持隔离，不作改动。

## 1. 当前总览

| 项目 | 当前状态 | 判断 |
|---|---|---|
| 研究命题 | 长程 Agent 状态感知、任务级 Model × Effort 路由 | **已明确** |
| 文献与历史研究 | 已有综合报告、7 个专题证据、Kev/Jev 研究 | **可用，需按当前方法更新** |
| 本地生产调用数据 | CCH 聚合 + Blog GPT 调用明细 | **仅适合统计先验，非路由监督** |
| 真实 Agent 轨迹 | 私有 Codex 监控部分有 session，但隐私限制；公开可用轨迹未落地 | **缺关键训练/评测数据** |
| Router 代码 | 仓库中无自研可执行 Python Router/Harness | **未开始** |
| 统一 Schema/账本 | 有规划，没有可运行实现 | **待实现** |
| Kev-4B | 官方技术路线已核查；本项目尚未加载、微调或测延迟 | **待 smoke test** |
| GPU | 一张 A6000 48GB；E0 时空闲 | **资源可行性较好，需再核查** |
| 任务级评估 | 尚无本项目的成对任务轨迹、成功标签、预算与统计结果 | **未开始** |
| 论文实验结果 | 无本项目可信对照/消融数据 | **不能声称已验证方法** |

**总体阶段：E0 历史审计报告已接收 → E0.5 目录与文档治理待执行 → E1 数据协议与工程最小闭环。**

## 2. 仓库与工程状态

**GitHub**：https://github.com/sxyq/modelrouter （公开，默认 `main`）。

**E0 时本地工作树**：`main` 旧 HEAD 为 `13c14a3`；有用户未提交修改（包括 `.gitignore` 和未跟踪的 `AGENTS.md`，另有历史工作目录变动）。执行 Agent 每轮操作均保留未提交修改，不清理、覆盖、reset 或强推这些变更。执行 Agent 每轮重新核查当前状态。

### 2.1 已有研究资产（仓库相对路径）

| 路径 | 内容 | 复用方式 |
|---|---|---|
| `README.md` | 项目入口 | 增加三文档导航 |
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

### 3.2 授权服务器（[E0 报告]）

| 项目 | 审计值 | 风险/后续 |
|---|---|---|
| 系统 | Ubuntu 24.04 LTS | 版本变化需复核 |
| CPU / 内存 | 80 核 / 约 376 GiB RAM | 共享资源，勿无限并行 |
| GPU | NVIDIA RTX A6000 48GB（49140 MiB） | 单卡，需记录峰值显存 |
| GPU E0 占用 | 682 MiB，0% utilization | 仅审计时刻，执行前重测 |
| 磁盘 | E0 报告可用约 1.2 TiB | 仍需考虑已有大权重 |
| Python | 3.12.3 | 建议独立环境 |
| PyTorch | 现有共享环境报告 2.14.0+cu126 | 不是 Kev 已验证兼容性的证明 |
| Ollama | 现有网关与约 14 个本地模型 | 需测试 endpoint/effort 支持情况 |
| 其他服务 | 已有共享文本与图像服务 | 不重启、不更改所有权或端口 |
| 权重目录 | 存在 >400GB 模型权重 | 不假定 Kev 权重已经下载 |
| ModelRouter 服务器目录 | E0 未发现 | 新建/克隆需任务授权 |

**重要**：本地模型“有 Ollama 端点”不意味着原生支持多档 reasoning effort。候选池必须由 capability registry 校验，不得为不支持的组合造标签。

## 4. 数据资产与可训练性

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
| B8 | 中 | 任务级多分支 rollout 可能成本高 | 5 任务 pilot、预算上限、审批 |
| B9 | 中 | 公开 GitHub 与本地私人路径/日志混杂 | 脱敏检查、敏感数据不提交 |
| B10 | 中 | 历史实现方案与最新方法不一致 | 三文档规范化并注明历史基线 |

## 6. 里程碑与验收条件

| 阶段 | 核心工作 | 验收条件 | 当前 |
|---|---|---|---|
| E0 | 环境/目录/数据只读审计 | 完整报告和证据路径 | **Agent 报告完成（历史快照）** |
| E0.5 | 当前本地/服务器目录复核与精简建议 | 实际目录树、共享边界、风险与 Git PR | **MR-DIR-001 PR 已提交，待 Planning 验收** |
| E1-A | 项目骨架、Schema、硬约束、账本 | 本地单元测试通过；无未来泄漏 | 待下发任务卡 |
| E1-B | 生产数据映射与字段覆盖 | 真实统计、字段定义、缺失矩阵 | 未开始 |
| E1-C | Kev-4B A6000 smoke test | 真实模型加载/显存/延迟记录 | 未开始 |
| E2 | 最小 Harness + 固定/规则基线 | 可重放 task、自动 resolved、真实记账 | 未开始 |
| E3 | 同状态多动作分支试验 | paired trajectories、相同继续策略、预算 | 未开始 |
| E4 | Kev-4B 训练与离线/在线对照 | 训练日志、独立测试、消融/CI | 未开始 |
| E5 | 论文图表与开源复现 | 可复现表格、成本-质量曲线、负例 | 未开始 |

### 6.1 建议的首轮受控实验

**Pilot（先验证 Harness，不是正式论文规模）**：
- 约 5 个有确定终局判定的 coding/Agent 任务；
- 每任务选择 2 个**真实可执行**候选动作；
- 每动作在同一可恢复状态快照执行，并固定后续 continuation policy；
- 记录任务 resolved、整任务 USD、延迟、步骤、错误、cache read/write、seed、失败原因；
- 预算与模型调用权限由用户单独批准。

**扩展候选（仅规划）**：约 30 个任务 × 2 动作 × 2 seed ≈ 120 分支轨迹；必须先验证预算、复现性和环境隔离，**不能把该数字写成已经运行**。

### 6.2 评价与统计

- 主指标：`success_rate`、`USD / resolved task`（说明零成功时处理）、总任务费用、质量-成本 Pareto。
- 次指标：任务 wall-clock、step 数、恢复次数、模型切换次数、物理 cached tokens、路由开销。
- 统计：同任务配对比较；任务层 bootstrap 置信区间；多次 seed；按任务类型、模型、候选池变化分层报告。
- 基线：固定低成本、固定强模型、task-only、rule、sticky/cache-aware、简单 MLP/LightGBM；主方法单一 Kev-4B。
- 禁止把某方法的可用候选池、工具权限、预算或任务划分设置得更宽松。

## 7. 下一个工作包（Planning 任务卡队列）

### MR-DIR-001：当前目录复核与精简方案（已完成审计并提交 PR）

**执行完成**：本地与授权服务器的项目相关目录、重复克隆、数据/模型/共享服务边界完成全面只读审计；提取了真实目录树与精简方案，未移动或删除任何文件。文档同步更新，已在分支 `agent/mr-dir-001-directory-audit` 提交 PR，等待 Planning 验收。

### MR-E1-001：最小工程与数据 Schema（目录复核验收后执行）

**允许范围（需正式任务卡确认）**：本地新建项目包、纯离线单元测试、公开脱敏示例；同步三文档、提交 GitHub。**不包括**服务器写操作、下载大模型或付费 API。

**输出**：可安装包、State/Action/Constraint/Decision/Outcome/Pricing 定义、State Builder 决策前检查、候选能力表、约束单测、费用单位校验、测试命令与 commit/PR。

**验收**：测试可重复；无未来信息字段；缺失 effort 不伪造；USD/quotaUnits 不相加；缓存实际值与估计值分开。

### MR-E1-002：现有数据字段映射

仅在本地按已授权目录读取；给出两数据源字段到统一 Schema 的映射、缺失矩阵、统计验证和隐私风险；不上传原始记录。

### MR-E1-003：Kev-4B 服务器可行性

先报告依赖、权重缓存、GPU 占用、预估磁盘；**获得安装/下载/占 GPU 的单独许可后**才运行最小推理和 LoRA smoke test。记录 A6000 真实结果，不能照搬 H100 benchmark。

## 8. 更新纪律

每次完成任务或研究决策：Execution Agent 更新本文件的**状态表、阻塞项、实测结果、提交链接**；Planning Agent 审阅并更新研究决策；同步 [PLANNING_MEMORY.md](PLANNING_MEMORY.md) 与 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) 中相应部分。提交必须记录 Task ID 和 Git commit/PR。

**此处所有“未开始/待验证”均为 2026-10-09 的基线，后续必须依据真实执行证据更改。**
