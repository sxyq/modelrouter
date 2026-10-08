# ModelRouter · Planning Memory（研究协作记忆）

> **版本：v0.3｜更新：2026-10-09｜角色：Planning Agent + Execution Agent**
>
> **定位**：供后续 ChatGPT Planning Agent、本地 Execution Agent 快速恢复项目上下文的唯一**公开安全**交接入口。它是 GitHub 版本化的项目记忆，**不是 ChatGPT 产品内置 Memory，也不会自动在后台更新**。执行 Agent 每完成任务须按本文件的协议同步三份文档并提交 GitHub。
>
> **公开性**：仓库为 public。不得提交私有服务器 IP、SSH 用户名/命令凭据、密钥、原始私人会话、私有任务内容、个人本地绝对路径及未脱敏日志。必要的机器路径放在本地不跟踪的配置或安全通道内。

## 0. 30 秒恢复上下文

- 项目：**ModelRouter**，研究**长程单/多 Agent 执行过程中的状态感知、任务级 Model × Reasoning Effort 联合路由**。
- 主方法：**确定性 State Builder + 动态候选与硬约束 + 单一 Kev-4B（Qwen3.5-4B-Base/LoRA/pointer head）决策模型 + Agent Harness + 完整记账与任务终局评价**。
- 目标：在可靠性/成功率约束下减少**任务完成总成本**，考虑动作对后续步骤、失败恢复、缓存连续性和成本剩余量的影响。
- 当前阶段：**E0 只读环境审计已由 Execution Agent 报告完成；E1 工程骨架、Schema、Harness、可重放任务均未实现**。不存在已验证的训练收益。
- 硬件：授权的单卡 **RTX A6000 48GB**；截至 E0 报告，GPU 基本空闲。实际运行前重新检查资源和共享服务。
- 现有 CCH 数据为 **110 行聚合记录，代表 750,212 次调用**；Blog GPT 数据为 **221,128 条调用明细**。二者都缺少可靠的任务级决策状态/终局成功标签，**不能直接作为反事实路由监督数据**。
- GitHub 正式文档：[项目状态](PROJECT_STATUS.md)、[研究与方法](RESEARCH_OVERVIEW.md)、本文件。历史 `IMPLEMENTATION_RESEARCH.md` 保留作历史设计参考，**不再代表当前唯一方法**。
- 首要下一步：下发并执行 **MR-E1-001（本地最小可测试工程骨架 + Schema + 单元测试 + 文档同步）**，再做受控任务 pilot；不得跳过验收直接训练。
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

**历史方案迁移说明**：2026-09 的 `IMPLEMENTATION_RESEARCH.md` 重点是“任务开始前一次选择 + GBDT/MLP 事前成本预测”。这是仍有价值的**对照基线和文献证据**，但当前主方法已更新为“运行时状态感知 + 单一 Kev-4B + 任务级回报”。不得在新代码中未经讨论把旧设计当作强制架构。

## 3. E0 环境事实快照（[AUDIT]，非实时监控）

| 维度 | 观测 | 对后续的意义 |
|---|---|---|
| 仓库 | `sxyq/modelrouter`，`main`；研究材料为主，**尚无 Router/Harness Python 实现** | 从最小代码骨架开始 |
| 本地 | macOS Apple Silicon；Python 3.9.6；PyTorch 2.4.1/MPS | 适合轻量开发、静态测试和数据检查 |
| 服务器 | Ubuntu 24.04，80 CPU 核，约 376 GiB RAM，单卡 A6000 48GB | 可进行 Kev smoke test，需隔离共享资源 |
| GPU | E0 时 682 MiB/49140 MiB，利用率 0% | **仅是当时快照**；执行前重新查询 |
| 服务器 Python | 3.12.3；已有环境报告 torch 2.14.0+cu126 | 兼容性待专用环境验证；不污染共享环境 |
| 模型服务 | Ollama 端口服务及其他共享服务已存在 | 不重启、不覆盖、不占用他人端口 |
| 模型权重 | 服务器共享模型目录存在大量已下载权重 | Kev-4B 及 Qwen3.5-4B-Base **尚未确认已存在** |
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
- 可在任务卡授权范围内修改代码、运行测试、更新三份文档并提交 GitHub；每个任务都记录 commit SHA、测试结果、已知风险。
- 不擅自访问新主机、安装大型依赖、下载模型、占用共享 GPU、调用付费 API、修改生产服务或上传私人数据。
- 任务完成**必须同步三份文档**：Memory 记决策/交接，Status 记实测进度，Research 记新增证据/方法改变；无变化也应检查并注明“本次无需修改”。
- 每轮交付 Git commit 或 PR URL、变更文件列表、执行命令、输出摘要、失败/未完成项和下一步建议；不得只说“完成”。
- 若任务超出授权或有冲突，停止并回报 Planning Agent。

### GitHub 工作流

1. 检查 `git status --short`、`git branch --show-current`、`git rev-parse HEAD`、远端状态；尊重本地现存未提交修改。
2. 优先为实验代码/跨文件改动建立 `agent/<task-id>-<topic>` 分支和 PR；文档小修可在经授权且无冲突时提交主分支。
3. 提交前运行适用的 lint/tests/schema validation；文档检查链接、相对路径、敏感信息和三文档一致性。
4. Commit message 带任务编号；记录实际 commit SHA/PR 链接；不 force push、不覆盖他人工作。
5. 公开仓库提交前检查：无 IP/密钥/个人绝对路径/私人 prompt/数据明细；保留来源与许可证信息。
6. **实时更新的含义**：每次有新的执行结果或研究决策即在该轮工作内同步提交；不是无人值守的持续后台监控。

## 6. 当前任务台账

| Task ID | 任务 | 状态 | 证据/验收 |
|---|---|---|---|
| MR-E0-001 | 本地/服务器只读审计 | **Execution 报告完成** | 用户提供 2026-10-09 报告；Planning 尚未远程复验 |
| MR-DOC-001 | 将研究总纲拆为三份 GitHub 规范文档 | 已完成（首次提交 cb460e8；后续校验已通过） | GitHub commit SHA + 三文件链接 |
| MR-E1-001 | 最小工程骨架、schema、cost ledger、单元测试 | **待下发** | 可导入、可测试、无未来泄漏 |
| MR-E1-002 | 数据字段映射与数据可用性检查 | **待下发** | 字段覆盖、单位校验、脱敏汇总 |
| MR-E1-003 | A6000 Kev-4B 兼容性与资源 smoke test | **待批准资源操作** | 真实峰值显存/延迟/版本日志 |
| MR-E2-001 | Harness + 固定基线任务 pilot | **未开始** | 可重放任务与终局成功标签 |
| MR-E3-001 | 同状态受控分支实验 | **未开始** | 成对轨迹、预算和配对统计 |
| MR-E4-001 | Kev 训练与消融 | **未开始** | 训练日志、固定测试集、对照结果 |

## 7. 下一张任务卡建议：MR-E1-001

**目标**：本地实现最小可测试的包结构和严格 Schema，不连服务器、不调用模型、不下载大权重。

**建议交付**：`pyproject.toml`、`src/modelrouter/`（`schemas.py`、`constraints.py`、`pricing.py`、`state_builder.py`、`router/base.py`）、`tests/`、最小 README、可脱敏的 JSONL 示例。代码细节由 Planning Agent 审查任务卡后确认。

**强制验收**：状态只包含决策前字段；缓存 read/write 与估计 overlap 分开；CCH USD 与 Blog quotaUnits 不相加；候选能力注册与硬约束可单测；无付费调用；三文档同步；提交可复查 commit/PR。

## 8. 交接时的固定回复格式

每次 Execution Agent 结束任务时报告：

- `Task ID` / `Status` / `Branch` / `Commit or PR`
- `Observed facts`（证据路径 + 命令）
- `Files changed`（包括三份文档的同步状态）
- `Tests run`（通过/失败/未运行）
- `Resource / cost usage`（仅真实数据）
- `Risks / blockers`
- `Next recommended task`（不自动执行）

Planning Agent 下一轮先阅读本文件、[状态](PROJECT_STATUS.md)、[研究方法](RESEARCH_OVERVIEW.md)和最近一次任务报告，再决策。
