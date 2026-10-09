# ModelRouter · Planning Memory（研究协作记忆）

> **版本：v0.7｜更新：2026-10-09｜角色：Planning Agent + Execution Agent**
>
> **定位**：供后续 ChatGPT Planning Agent、本地 Execution Agent 快速恢复项目上下文的唯一**公开安全**交接入口。它是 GitHub 版本化的项目记忆，**不是 ChatGPT 产品内置 Memory，也不会自动在后台更新**。Execution Agent 按职责检查三份文档：Memory/Status 随事件更新，Research 仅在研究证据、方法或实验协议变化时修改；本地频繁 commit，按约定定期 push 后 GitHub 才能看到更新。
>
> **公开性**：仓库为 public。不得提交私有服务器 IP、SSH 用户名/命令凭据、密钥、原始私人会话、私有任务内容、个人本地绝对路径及未脱敏日志。必要的机器路径放在本地不跟踪的配置或安全通道内。

## 0. 30 秒恢复上下文

- 项目：**ModelRouter**，研究**长程单/多 Agent 执行过程中的状态感知、任务级 Model × Reasoning Effort 联合路由**。
- 主方法：**确定性 State Builder + 动态候选与硬约束 + 单一 Kev-4B（Qwen3.5-4B-Base/LoRA/pointer head）决策模型 + Agent Harness + 完整记账与任务终局评价**。
- 目标：在可靠性/成功率约束下减少**任务完成总成本**，考虑动作对后续步骤、失败恢复、缓存连续性和成本剩余量的影响。
- 当前阶段：**E-DESIGN 详细实验设计问答（已启动，尚未冻结协议）**。E0.5-ENV 已由项目负责人确认：未来使用独立 ModelRouter 工作目录和 Python 环境，共享资源只读；当前不执行任何服务器操作。MR-DIR-001 与 MR-SYNC-001 已验收。
- 执行路线：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- 硬件：授权的单卡 **RTX A6000 48GB**；2026-10-09 审计快照显示显存占用仅 682 MiB。实际运行前重新检查资源和共享服务。
- 现有 CCH 数据为 **110 行聚合记录，代表 750,212 次调用**；Blog GPT 数据为 **221,128 条调用明细**。二者都缺少可靠的任务级决策状态/终局成功标签，**不能直接作为反事实路由监督数据**。
- GitHub 正式文档：[项目状态](PROJECT_STATUS.md)、[研究与方法](RESEARCH_OVERVIEW.md)、本文件及 [实验设计问答](EXPERIMENT_QA.md)（E-DESIGN 已建立，记录 Q-ID、选项、推荐、负责人回答与最终决策）。历史 `IMPLEMENTATION_RESEARCH.md` 保留作历史设计参考，**不再代表当前唯一方法**。
- 首要下一步：**E-DESIGN Q-001 评测任务集选择（等待负责人答复）→ 依次冻结动作空间、预算、基线、受控实验和统计协议 → 之后才下发 MR-E1-001 工程骨架**。服务器隔离原则已确认但未实际创建目录；不得提前启动代码开发、模型下载或训练。
- 当前论文表述纪律：不要把状态字段数量本身作为创新点；**论文不讨论“多变量”或“混沌”**。新意必须靠任务级状态决策、Model × Effort、延迟成本/成功影响和严谨评测证明。

## 1. 事实来源、证据等级和时间

| 标记 | 含义 | 本轮证据 |
|---|---|---|
| [AUDIT] | 本地 Agent 的只读观测；Planning 未直接登录服务器复核 | 用户提供的 MR-E0-001 报告，2026-10-09 |
| [GITHUB] | GitHub 连接器读取的远端仓库事实 | 2026-10-09 读取 main、README、规划及文献文件 |
| [OFFICIAL] | 模型/项目官方说明 | Kev 官方 model card / README，2026-10-09 查阅 |
| [PAPER] | 原论文/公开预印本 | 论文原文链接；同行评审状态另行核查 |
| [DESIGN] | 当前计划或待验证的研究假设 | 不能写成实验结果 |
| [UNKNOWN] | 尚无证据或需要再次确认 | 必须在任务卡中安排检查 |

**GitHub 基线**：[GITHUB] 在本次三文档整理前，`main` = `13c14a387d1c18ecfe32b84a86b4efc1d751b72d`（2026-10-07 提交）。后续提交会改变 HEAD；**不得把旧 SHA 当作永远最新**。

## 2. 已确认的研究决策（Decision Log）

| ID | 决策 | 理由 | 状态 |
|---|---|---|---|
| D-001 | 长程 Agent 任务级而非单条 Prompt 级路由 | 单步最便宜不代表整任务最便宜 | 已确认 |
| D-002 | 动作空间为 `(model, effort)`，候选池动态变化 | 不同 provider、上下文限制、effort 能力不同 | 已确认 |
| D-003 | 主路由器优先采用**单一 Kev-4B** | 降低模型堆叠复杂度，支持 typed choice 和概率输出 | 已确认，效果待测 |
| D-004 | Agent 运行中可多次决策；admission-only 保留作对照 | 真实长程任务状态持续变化 | 已确认 |
| D-005 | 缓存是可观测状态与切换代价，不假设跨模型 KV 可直接迁移 | 实际 cache hit 与估计 prefix overlap 必须分离 | 已确认 |
| D-006 | 使用任务级终局成功、实际费用和成本剩余量评估 | 延迟回报无法由 API HTTP 成功替代 | 已确认 |
| D-007 | 历史日志只用于分布先验/成本校准，不构造虚假未选动作标签 | 缺 task_id、状态与 counterfactual | 已确认 |
| D-008 | 先搭建 Harness/Schema，再采集可重放受控轨迹 | 当前仓库没有可执行路由代码 | 已确认 |
| D-009 | 论文聚焦真实 Agent 状态与决策机制；不以字段数量为新意 | 避免空泛主张 | 已确认 |
| D-010 | 三份 Markdown 为持续维护的公开事实源 | 支持 ChatGPT 与本地 Agent 交接、审阅和版本控制 | 已确认 |
| D-011 | 采用轻量 Git：默认 main、本地频繁 commit、按会话/里程碑或最长 24 小时工作周期 push；不要求 PR | 研究实验优先可追溯和及时备份，避免不必要的工程流程 | 已确认（2026-10-09） |
| D-012 | 暂不迁移或归档历史研究目录，保持当前物理结构 | 现有目录可控，移动 PDF/截图可能破坏引用且不减少 Git 历史体积 | 已确认（2026-10-09） |
| D-013 | 服务器未来采用独立 ModelRouter 工作目录与 Python 环境；既有共享资源只读；本轮禁止实际服务器操作 | 降低对共享服务和既有资产的干扰，隔离实验依赖 | 已确认（2026-10-09，E0.5-ENV） |

**历史方案迁移说明**：2026-09 的 `IMPLEMENTATION_RESEARCH.md` 重点是“任务开始前一次选择 + GBDT/MLP 事前成本预测”。这是仍有价值的**对照基线和文献证据**，但当前主方法已更新为“运行时状态感知 + 单一 Kev-4B + 任务级回报”。不得在新代码中未经讨论把旧设计当作强制架构。

## 3. E0/E0.5 环境事实快照（[AUDIT]，2026-10-09 审计快照，非实时监控）

| 维度 | 观测 | 对后续的意义 |
|---|---|---|
| 仓库 | `sxyq/modelrouter`，`main`；在已授权扫描范围内为纯研究资产，**尚无 Router/Harness Python 实现** | 从最小代码骨架开始 |
| 本地 | macOS Apple Silicon；Python 3.9.6；PyTorch 2.4.1/MPS | 适合轻量开发、静态测试和数据检查 |
| 服务器 | 授权 GPU 服务器：Ubuntu 24.04，80 CPU 核，约 376 GiB RAM，单卡 A6000 48GB | 可进行 Kev smoke test，需隔离共享资源 |
| GPU | 2026-10-09 审计快照时 682 MiB/49140 MiB，利用率 0% | **仅是当时快照**；执行前重新查询 |
| 服务器 Python | 3.12.3；已有环境报告 torch 2.14.0+cu126 | 兼容性待专用环境验证；不污染共享环境 |
| 模型端点 | 已有共享文本、图像与对话端点已存在 | 不重启、不覆盖、不占用他人端口 |
| 模型权重 | 服务器共享模型目录存在大量已下载权重 | 在已授权扫描范围内**尚未确认 Kev-4B 及 Qwen3.5-4B-Base 权重已存在** |
| 项目目录 | 在已授权扫描范围内未发现 ModelRouter 项目目录 | 新建/克隆需任务授权 |
| CCH | 110 组统计、43 个模型、8 种 effort 标签、代表 750,212 调用 | 成本/缓存/Token 分布先验 |
| Blog GPT | 221,128 条调用、10 模型、7 effort 标签、37 个实际组合 | 调用级经验分布；成本是 quotaUnits 非 USD |
| Codex 监控 | 约 3,403 sessions、61,870 token 记录 | **隐私高风险**，不可直接提交或开放训练 |

**禁止推断**：上述快照不能证明当前 GPU 仍空闲、服务仍在线、模型版本不变，或所有日志字段均已达到训练要求。

## 4. 研究方法的固定接口原则

### 决策时刻 t

- `state_t`：只包含决策前可观察的任务、Agent、上下文、工具、验证、缓存、时间和服务商状态。
- `candidates_t`：当前可用的 Model × Effort 配置；显式记录 provider、模型版本、能力与限制。
- `constraints_t`：预算、上下文、权限、隐私、tool-loop continuity、速率限制、模型可用性等硬约束。
- `action_t`：一个合法 `(model, effort)`；不支持 effort 的本地模型不得伪造 low/medium/high 轴。
- `outcome`：动作后真实 usage、缓存命中、错误、后续执行轨迹与任务终局。
- `cost_to_go`：从决策点到任务终局的**观察到的**剩余成本；行为策略下的轨迹标签≠其他候选动作的反事实效果。

### 八组状态

1. Task/Subtask；2. Agent/Coordination；3. Context/Memory；4. Tool/Environment；
5. Verification/Recovery；6. KV Cache/Continuity；7. Temporal/Execution；8. Provider/Availability。

必须有**原始观测 / 派生特征 / 决策时硬约束 / 训练目标**的字段边界。任何来自当前动作之后的字段不得回流到决策前状态。

## 5. Planning / Execution 协作协议

### Planning Agent（本 ChatGPT）

- 审核 Execution 报告，区分事实、推断、未知；确定研究目标、实验假设、优先级和验收条件。
- 下发单一编号任务卡：`Task ID / Goal / Inputs / Allowed operations / Forbidden operations / Deliverables / Tests / Documentation / Git workflow / Stop conditions`。
- 对代码变更进行架构与实验有效性审查；对统计结论要求可复现证据。
- 根据回报修订三份文档的研究决策与后续计划。
- **不能**声称自动监听本地或服务器、自动运行后台任务、或已完成未实际执行的实验。

### Execution Agent（本地 Agent）

- 严格按任务卡执行，先检查工作区状态和最新 GitHub HEAD；发现未提交修改不得覆盖、reset、clean 或强推。
- 可在任务卡授权范围内修改代码、运行测试，按职责检查三份文档；频繁本地 commit、定期 push；记录本地 HEAD、远端 HEAD、测试结果和已知风险。
- 不擅自访问新主机、安装大型依赖、下载模型、占用共享 GPU、调用付费 API、修改生产服务或上传私人数据。
- 任务完成必须**检查**三份文档：Memory 记决策/交接，Status 记实测进度；Research 仅在证据、方法或实验协议变化时修改。无需修改的文档在交付报告注明即可，不做无意义提交。
- 每轮交付本地 HEAD SHA、`origin/main` SHA、ahead/behind、未提交状态、最近 push 状态、变更文件列表、测试摘要、风险和下一步建议；不得只说“完成”。
- 若任务超出授权或有冲突，停止并回报 Planning Agent。

### 轻量 Git 工作流（2026-10-09 起生效）
 
1. **默认在 `main` 开发**，不要求 PR；只有需要隔离高风险试验或用户明确要求时才使用独立分支。既有 PR #1 已关闭且未合并，保留为历史记录。
2. 每个可验证的小步骤或实验里程碑在本地 `git commit`；提交信息写清主题，重要工作可附任务编号。不要把每一行小改动都拆成独立提交。
3. **推送频率**：每次工作会话结束、重要实验里程碑完成时推送；连续工作期间原则上不超过 24 小时不推送。离线或推送失败时明确标记“仅本地”，不能写成 GitHub 已同步。
4. 提交前检查 `git status -sb`、`git diff --stat`、`git branch --show-current`；仅暂存需要的文件，不使用盲目的 `git add -A`，保护未跟踪的私人 `AGENTS.md`、配置、日志与数据。
5. 推送前 `git fetch origin`，比较 `git rev-parse HEAD`、`git rev-parse origin/main` 和 `git rev-list --left-right --count origin/main...HEAD`。本地干净且可快进时才 `git pull --ff-only`；出现分叉/未提交冲突则停止并报告，禁止自动 reset、clean、rebase、force push。
6. 在 `main` 且无冲突时使用 `git push origin main`；推送后再次核实远端 SHA。**本地 commit 不等于远端已更新**，GitHub 不会自动读取未推送内容。
7. 实验记录需关联 **代码 commit SHA、配置版本、数据快照标识、模型版本、运行环境与结果路径**。服务器尚未部署时明确写“未部署”，不得把 GitHub main SHA 当作服务器运行版本。
8. 提交前运行适用测试并检查公开仓库敏感信息、相对链接与许可证。历史 PR/分支曾包含内部环境标识；不得未经批准重写公开 Git 历史。

## 6. 当前任务台账

| Task ID | 任务 | 状态 | 证据/验收 |
|---|---|---|---|
| MR-E0-001 | 本地/服务器只读审计 | **Execution 报告完成** | 用户提供 2026-10-09 报告；Planning 尚未远程复验 |
| MR-DOC-001 | 将研究总纲拆为三份 GitHub 规范文档 | 已完成（首次提交 cb460e8；后续校验已通过） | GitHub commit SHA + 三文件链接 |
| MR-DIR-001 | 当前本地/服务器目录核查与精简方案 | **审计报告与文档已验收** | Planning 核实 GitHub 分支和修订；服务器事实依据 Execution 审计快照，非独立实测；未移动/删除文件 |
| MR-SYNC-001 | 本地 Git 版本对齐核对 | **Execution 报告完成；Planning 验收** | Execution 报告本地 main 与 origin/main 同为 db355c7、ahead/behind 0/0；跟踪文件无修改，但 AGENTS.md 未跟踪；服务器未重查 |
| E0.5-ENV | 服务器独立工作目录及共享资源边界确认 | **已由项目负责人确认，E0.5 结束** | 未来独立工作目录和 Python 环境，共享资源只读；未授权任何服务器实际操作 |
| E-DESIGN | 详细实验设计与用户决策（`EXPERIMENT_QA.md`） | **进行中：Q-001 待用户答复** | 首先选择评测任务集；随后讨论动作空间、预算、对照、受控实验与统计方案；协议未冻结 |
| MR-E1-001 | 最小工程骨架、schema、cost ledger、单元测试 | **排在 E-DESIGN 决策后** | 可导入、可测试、无未来泄漏 |
| MR-E1-002 | 数据字段映射与数据可用性检查 | **待下发** | 字段覆盖、单位校验、脱敏汇总 |
| MR-E1-003 | A6000 Kev-4B 兼容性与资源 smoke test | **待批准资源操作** | 真实峰值显存/延迟/版本日志 |
| MR-E2-001 | Harness + 固定基线任务 pilot | **未开始** | 可重放任务与终局成功标签 |
| MR-E3-001 | 同状态受控分支实验 | **未开始** | 成对轨迹、预算和配对统计 |
| MR-E4-001 | Kev 训练与消融 | **未开始** | 训练日志、固定测试集、对照结果 |

## 7. 当前版本同步与下一阶段规划：E-DESIGN

**MR-SYNC-001 已完成（Execution 报告）**：本地 `main` 与当时 GitHub `origin/main` 均为 `db355c7`，ahead/behind 0/0；已跟踪文件无修改，`AGENTS.md` 仍未跟踪。Planning 已独立核实该 GitHub SHA，但不能直接检查本地工作树；本次文档更新会使 GitHub main 再前进一个提交，本地需下次工作时安全快进。旧审计分支不得直接合并或 cherry-pick 到 `main`，避免引入历史中的内部环境标识。

**环境决策已完成**：项目负责人确认未来使用独立 ModelRouter 工作目录及 Python 环境，共享资源只读。保留现有文献与数据目录，不迁移、不删除；服务器当前不创建项目目录、不安装依赖、不下载 Kev-4B、不运行实验。E0.5 已结束，E-DESIGN 正式启动。

**定位与目标**：在进入代码实现之前，由 Planning Agent 梳理并向项目负责人提出实验设计关键问题，明确评测任务集、动作空间与 effort 档位、预算上限、对照基线等核心边界。

**问答登记文件**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md) 已在 E-DESIGN 启动时建立，专职记录 Q-ID、问题、选项、Planning 推荐及理由、用户回答、最终决策、日期和实验/预算/论文影响；Q-001 已提出但尚无用户回答。

**后续工程衔接（MR-E1-001）**：待 E-DESIGN 问答决策完成并冻结实验边界后，再由 Planning Agent 下发 MR-E1-001 任务卡，启动本地最小工程骨架与 Schema 开发。建议交付包含 `pyproject.toml`、`src/modelrouter/`、`tests/` 等本地轻量代码，不连服务器、不调用付费 API。

## 8. 交接时的固定回复格式

每次 Execution Agent 结束任务时报告：

- `Task / Status / Local HEAD / origin/main HEAD / Ahead-Behind / Dirty / Last push`
- `Observed facts`（审计时间与证据范围；服务器部署 SHA 或“未部署”）
- `Files changed`（三份文档逐份注明“已修改/已检查无需修改”）
- `Tests run`（通过/失败/未运行）
- `Resource / cost usage`（仅真实数据）
- `Risks / blockers / Next recommended task`（不自动执行）

Planning Agent 下一轮先阅读本文件、[状态](PROJECT_STATUS.md)、[研究方法](RESEARCH_OVERVIEW.md)和最近一次任务报告，再决策。

## 9. 文档分层与按时间顺序的交接记录（MR-DIR-001 新规则）

### 9.1 文档体系与职责分工

| 类别 | 文件 | 读者 | 更新触发与职责 |
|---|---|---|---|
| A · 交接/记忆 | 本文件 `PLANNING_MEMORY.md` | Planning + Execution | **每次任务与决策**；按时间追加审计事件、Planning 审查意见、纠正事项、提交记录与后续决策 |
| B · 研究总纲 | `RESEARCH_OVERVIEW.md` | 项目负责人/论文研究 | **研究证据、方法或实验协议改变时**；方法未变时无需修改，避免流水账 |
| B · 进度看板 | `PROJECT_STATUS.md` | 项目负责人 | **每次任务状态变化**；统一首页看板、阶段表、工作包队列，确保当前状态一致 |
| C · 实验问答决策 | `EXPERIMENT_QA.md` | Planning + 项目负责人 | **规划于 E-DESIGN 阶段建立（本轮仅登记计划，不提前创建）**；专职记录 Planning 提出的实验设计问题、选项、负责人回答、最终决策及日期 |

“实时进度”定义为**Execution 在本地随任务事件更新并 commit，按工作会话/里程碑或最长 24 小时工作周期 push 后 GitHub 可见**；未推送内容只有本地可见。不能声称 ChatGPT 自动后台监视本地、服务器或持续推送；不得为了更新泄漏私人日志。

### 9.2 时间线（只追加新事件；纠错注明原因）

| 日期 | 事件 | 证据/操作 | 状态 |
|---|---|---|---|
| 2026-10-07 | 历史研究材料、文献与实验资产已存在于 `main` | GitHub 旧提交 `13c14a3` | 历史基线 |
| 2026-10-09 | Execution 提供 MR-E0-001 本地/服务器只读环境审计 | 用户提供的审计报告；Planning 未直接连接服务器 | 报告已接收 |
| 2026-10-09 | 将原研究总纲整理为 Memory、Status、Research 三份 GitHub 文件 | GitHub `cb460e8`；补充完成状态 `51d0eb2` | 已完成 |
| 2026-10-09 | Planning 重新读取 GitHub 根目录与 `our-project/planning` | `main=51d0eb2`；远端结构已核验 | **仅 GitHub 已核验** |
| 2026-10-09 | 用户要求先核查**当前**本地和服务器目录、保持目录简洁，再启动工程开发 | 新任务 MR-DIR-001；本地/服务器最新目录尚未获取 | 已安排 |
| 2026-10-09 | Execution Agent 提交 MR-DIR-001 审计报告与精简方案到独立分支 | 独立分支 `agent/mr-dir-001-directory-audit`，完成初步审计 | 审计完成 |
| 2026-10-09 | Planning Agent 审阅反馈：未见正式 PR，要求修正阶段顺序（插入 E-DESIGN）、限定统计口径、公开脱敏、披露 Git 历史暴露风险 | 收到 MR-DIR-001-R1 修订任务要求 | 待修订 |
| 2026-10-09 | Execution Agent 完成 MR-DIR-001-R1 修订并创建指向 main 的正式 PR | 插入 E-DESIGN、登记 EXPERIMENT_QA.md 计划、修正 209 文件口径、脱敏内部细节、披露历史暴露风险、创建正式 GitHub PR | 已提交，随后经 Planning 核验 |
| 2026-10-09 | Planning 核实 MR-DIR-001-R1 修订与 GitHub 版本差异 | GitHub main 仍为旧版本、PR #1 的 head 为 a76fe4b；Planning 认可审计报告但未独立连接服务器 | 文档验收 |
| 2026-10-09 | 项目负责人改用轻量 Git 工作流 | 默认 main、本地频繁 commit、定期 push，不再要求 PR；PR #1 已关闭且未合并，直接更新 main；历史分支仍需注意隐私风险 | 已决策 |
| 2026-10-09 | Execution 回报 MR-SYNC-001 本地版本核对 | main 与 origin/main 均为 db355c7；ahead/behind 0/0；跟踪文件无改动，未跟踪 AGENTS.md 保留；服务器未重新核查 | Planning 验收；E0.5-ENV 待确认 |

### 9.3 当前 GitHub 已核验的核心目录（非本地/服务器最新快照）

~~~text
modelrouter/
├── README.md
├── our-project/
│   ├── README.md
│   ├── planning/        # 当前三份规范文档 + 历史 IMPLEMENTATION_RESEARCH.md
│   ├── literature/
│   ├── data/
│   └── 汇报/
├── research/            # 历史研究与专题
├── papers/              # 论文资产
├── external-projects/   # 第三方项目说明
└── .workbuddy/          # 历史工具记忆；需确认是否仍在使用
~~~

上图仅来自 GitHub 远端目录列表，**不能推断本地工作树、服务器磁盘与 GitHub 一致**。此前 E0 报告提及本地有未提交修改和 `AGENTS.md`，需要重新核实。

### 9.4 MR-DIR-001：本地/服务器目录治理审计任务卡（历史记录；PR 要求已废止）

**目标**：在开始编写 Router 代码前，找出实际目录、重复副本、共享资源边界和可精简的研究资产；先形成方案，不移动/删除。

**允许**：读取授权本地仓库及已配置服务器的项目相关目录；使用 `pwd`、`git status`、`git worktree list`、限制深度的 `find`/`du`/`ls`、`nvidia-smi` 等只读命令；脱敏汇总；在安全独立工作区内更新 Memory 和 Status，提交文档 PR。

**禁止**：猜测服务器连接信息；递归扫描整个私人 home；输出密钥、IP、私人绝对路径和原始会话；安装、下载、训练、重启共享服务；移动、清理、删除、覆盖目录或未提交工作；自动合并 PR。

**核查对象**：
1. 本地真实仓库根目录、一级/二级目录、重要三级目录；各目录用途、数量、大小、是否受 Git 跟踪、重复与风险。
2. 授权服务器 ModelRouter 克隆、数据、模型缓存、Python 环境、实验输出、共享服务目录；连接失败就报告未知。
3. GitHub 远端树与本地/服务器的差异；不得把 GitHub 列表当成机器目录清单。
4. 输出“实际树 / 建议精简树 / 保留 / 待归档 / 禁止碰触 / 待批准操作”。
5. 将**公开安全的汇总**追加到本文件时间线及 `PROJECT_STATUS.md` 进度看板；研究方法无变化时无需改 `RESEARCH_OVERVIEW.md`。

**验收**：有真实命令和时间戳支持的本地/服务器目录概览；每项归档建议说明是否共享、是否被引用、Git 跟踪与风险；无任何移动/删除；无敏感信息提交；Git commit/PR 可核查；停止等待 Planning 批准后续目录整理。

**历史记录（已被后续决策取代）**：MR-DIR-001 曾通过独立分支和 PR 提交审计材料；后续 Planning 已验收，PR #1 已关闭且未合并。现行流程为直接提交 main，详细实验设计尚未开始。

### 9.5 MR-DIR-001 / MR-DIR-001-R1：本地与服务器目录审计执行记录与交接

- **执行日期**：2026-10-09
- **执行角色**：Execution Agent
- **历史分支与提交**：`agent/mr-dir-001-directory-audit`，修订 head `a76fe4b`；曾创建 PR #1，现已关闭且未合并。当前安全修订内容由 Planning 直接提交到 `main`，不引入该分支中间提交。
- **只读操作说明**：未移动、删除或重命名任何现有代码、模型权重或研究数据。

#### 9.5.1 核心审计事实（只读实测证据快照）

1. **本地仓库（项目根目录）**：
   - **统计口径说明**：Git 跟踪管理的文件为 208 个，当前工作区未跟踪文件为 1 个（`AGENTS.md`），合计 209 个项目资产文件（总体积约 251.3 MB；若包含本地系统临时文件 `.DS_Store` 与未纳入版本控制的历史笔记 `.workbuddy/`，本地物理文件总数为 214 个）。
   - **代码状态**：在已授权扫描范围内未发现任何自研可执行 Python/Shell 代码，无 `pyproject.toml` 或 `requirements.txt`。
   - **数据状态**：`our-project/data/` 仅含 CCH 聚合统计（110 行，85 KB）与博客 GPT 历史明细（221,128 行，33 MB），为调用级数据，缺失 `task_id`、前置状态与终局 `resolved` 标签。
   - **文献与资产**：`research/task-level-cost-routing/literature/pdfs`（58 个 PDF，158.6 MB）与 `visual_report_assets`（73 个图像，25.4 MB）均已进入 Git 跟踪。
   - **重叠与冗余**：
     - `external-projects/`（9 个微型卡片，共 1.8 KB）与 `IMPLEMENTATION_RESEARCH.md` 内容重叠；
     - `research/jev-deep/`（7 文件，177 KB）与 `our-project/literature/jev-model-research.md` 存在大量重叠调研内容；
     - `papers/unified-ai-gateway.pdf`（4.0 MB）单立目录，与 `research/.../pdfs` 割裂；
     - `our-project/汇报/`（30 文件，29.2 MB）包含历史 PPT 页面与静态图。
   - **历史工具目录**：`.workbuddy/` 历史工具记忆此前在本地已被加入 `.gitignore`。

2. **远程授权 GPU 服务器（RTX A6000，2026-10-09 审计快照，非实时监控）**：
   - **硬件资源**：Ubuntu 24.04 LTS，80 核 CPU，376 GiB RAM（346 GiB 可用），1.2 TiB 可用磁盘，1× RTX A6000 48GB 显存（审计快照时显存占用 682 MiB，利用率 0%）。
   - **已有服务现状**：
     - AI 推理服务运行于服务器共享目录；
     - 已有共享文本、图像及 Web 对话服务处于运行中状态；
     - vLLM 推理服务当前为未运行状态。
   - **项目目录现状**：在已授权扫描范围内未发现 ModelRouter 项目目录或独立克隆。

#### 9.5.2 目录精简方案（暂不迁移；保留历史建议）

Planning 决定当前物理目录保持不变；PDF/截图迁移可能破坏引用且不能缩小已有 Git 历史。以下仅是历史建议，未经新授权不得执行。

- **建议保留的核心目录**：
  - `src/modelrouter/`（待后续任务新建）
  - `tests/`、`configs/`、`pyproject.toml`
  - `our-project/planning/`（规范文档体系）
  - `our-project/data/`（真实数据源：source / cleaned / summaries）
  - `our-project/literature/`（核心报告与 F1-F7 证据）
- **建议归档项目（待批准）**：
  - 将 `external-projects/` 收敛为单文件 `our-project/literature/external-references.md`；
  - 将 `papers/unified-ai-gateway.pdf` 归入统一文献目录；
  - 将 `research/` 下早期素材和 `our-project/汇报/` 标记为只读历史资产。

#### 9.5.3 公开仓库隐私脱敏与 Git 历史暴露风险披露

- **脱敏范围**：当前工作区各文档已全面删除或泛化内部主机名、用户家目录、私人绝对路径、连接细节与服务端口。
- **Git 历史暴露风险**：由于分支 `agent/mr-dir-001-directory-audit` 早期提交（`b9c2321`、`fbbb53e` 等）已推送到公开仓库，其历史提交记录中曾包含内部主机名、用户家目录路径前缀及端口号。
- **处理准则与状态**：本任务严格遵循安全纪律，**禁止擅自 force push 或重写远端公开历史**。上述历史暴露范围已如实向 Planning Agent 与项目负责人报告，等待决策后续是否需要启动专门的 Git 历史清理程序（如 `git-filter-repo`）。

### 9.6 最新项目阶段说明与执行路线

- **执行路线**：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- **当前状态**：**MR-DIR-001 与 MR-SYNC-001 均已依据 Execution 报告验收；E0.5 仅待服务器工作目录与共享资源边界决策；E-DESIGN 尚未开始。**
- **严禁事项**：不得在目录审计验收前跳过 E-DESIGN 直接启动 MR-E1-001 工程代码开发，不得下载大模型或修改服务器共享服务。

### 9.7 MR-SYNC-001：版本信息完整性核对

Planning 可直接读取 GitHub `main` HEAD 和已推送的三份文档，**不能据此知道本地未提交改动、未推送 commit、服务器当前代码或 GPU 实况**。Execution 每轮提供一份简短版本快照：

- `git status -sb`、`git branch --show-current`、`git rev-parse HEAD`；
- `git fetch origin` 后的 `git rev-parse origin/main`、`git rev-list --left-right --count origin/main...HEAD`；
- `git log -3 --oneline`、最近一次成功 push 的时间/commit；
- 本地未提交/未跟踪文件的**脱敏摘要**，禁止上传私人文件内容；
- 服务器项目目录/部署 commit（若不存在，写“未部署”）及环境观测时间；
- 本次三文档的更新/无需更新判断、测试与实验结果版本。

旧分支 `agent/mr-dir-001-directory-audit` 的历史仍在公开仓库中，**关闭 PR 不等于清除历史**；不擅自 force push、删远端分支或重写历史。

### 9.8 MR-SYNC-001 交付验收（2026-10-09）

- **Execution 报告**：本地分支 `main`、本地 HEAD 与 `origin/main` 均为 `db355c74d14fa062c55f128ad4ece1ac83111d30`；ahead/behind = 0/0，`git diff main origin/main` 为空。
- **工作区措辞**：已跟踪文件无修改，但 `AGENTS.md` 仍是本地未跟踪的私人文件；不得写作“整个工作区严格 clean”。
- **证据边界**：Planning 通过 GitHub 连接器核实远端 `main` 为上述 SHA；本地 Git 命令输出与服务器未重新核查的状态来自 Execution 报告。远端版本在后续文档提交后会改变，旧 SHA 仅代表本次对齐快照。
- **处理结论**：MR-SYNC-001 验收通过，不需要重做同步任务；服务器 ModelRouter 部署状态沿用审计快照，不当作实时核验。
- **后续结果（2026-10-09）**：项目负责人已确认独立 ModelRouter 工作目录与独立 Python 环境、共享资源只读，E0.5 已结束；E-DESIGN 已启动并创建 `EXPERIMENT_QA.md`，当前不创建、不安装、不下载、不训练。

### 9.9 E0.5-ENV 验收与 E-DESIGN 启动（2026-10-09）

- **负责人明确确认**：未来服务器使用独立 ModelRouter 工作目录与独立 Python 环境；已有共享资源只读。**这是隔离原则的决策，不是服务器写操作的授权**；实际路径、资源配额、依赖安装、模型下载和 GPU 使用仍需后续单独确认。
- **阶段判定**：E0.5 完成；E-DESIGN 正式启动，实验协议尚未冻结。建立 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 记录设计问题与用户决策。
- **首轮问题**：Q-001 评测任务集和 pilot 构成，Planning 推荐分阶段混合任务方案；目前仅是推荐，待用户答复。后续 Q-002～Q-010 依次处理动作空间、预算、指标、基线、分支设计、数据分割、统计、复杂场景及 Kev 可行性。
- **Git 同步边界**：本次文档由 Planning 直接提交 GitHub main；Execution 的上一轮本地 HEAD 快照在提交后不再等于最新远端 HEAD，下次本地工作前先安全 fetch/ff-only；保护私人未跟踪文件。
