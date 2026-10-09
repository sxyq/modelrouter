# ModelRouter · Planning Memory（研究协作记忆）

> **版本：v2.0｜更新：2026-10-09｜角色：Planning Agent + Execution Agent**
>
> **定位**：供后续 ChatGPT Planning Agent、本地 Execution Agent 快速恢复项目上下文的唯一**公开安全**交接入口。它是 GitHub 版本化的项目记忆，**不是 ChatGPT 产品内置 Memory，也不会自动在后台更新**。Execution Agent 按职责检查四份文档：Memory/Status 随事件更新，Research 仅在研究证据、方法或实验协议变化时修改；本地频繁 commit，按约定定期 push 后 GitHub 才能看到更新。
>
> **公开性**：仓库为 public。不得提交私有服务器 IP、SSH 用户名/命令凭据、密钥、原始私人会话、私有任务内容、个人本地绝对路径及未脱敏日志。必要的机器路径放在本地不跟踪的配置或安全通道内。

## 0. 30 秒恢复上下文

- 项目：**ModelRouter**，研究**长程单/多 Agent 执行过程中的状态感知、任务级 Model × Reasoning Effort 联合路由**。
- 主方法：**确定性 State Builder + 动态候选与硬约束 + 单一 Kev-4B（Qwen3.5-4B-Base/LoRA/pointer head）决策模型 + Agent Harness + 完整记账与任务终局评价**。
- 目标：在可靠性/成功率约束下减少**任务完成总成本**，考虑动作对后续步骤、失败恢复、缓存连续性和成本剩余量的影响。
- **最新阶段/唯一下一行动以 [PROJECT_STATUS.md](PROJECT_STATUS.md) 首页为准**；E-DESIGN 问答批准以 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 为准。截至 2026-10-09 第二批答复后：E-DESIGN 进行中；Q-001=A/Q-002=B/Q-003=B 原则/Q-004=B/Q-005=B/Q-006=A 已记录。当前聚焦 Q-007 的公开轨迹 A 起步阶段，Q-010/Q-011 待依序讨论，不讨论具体实验步骤；“rq 3 需要 ab 同选”暂记指代未核清。此为当前快照而非永久现状。
- 执行路线：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- 硬件：授权的单卡 **RTX A6000 48GB**；2026-10-09 审计快照显示显存占用仅 682 MiB。实际运行前重新检查资源和共享服务。
- 现有 CCH 数据为 **110 行聚合记录，代表 750,212 次调用**；Blog GPT 数据为 **221,128 条调用明细**。二者都缺少可靠的任务级决策状态/终局成功标签，**不能直接作为反事实路由监督数据**。
- GitHub 正式文档：[项目状态](PROJECT_STATUS.md)、[研究与方法](RESEARCH_OVERVIEW.md)、本文件及 [实验设计问答](EXPERIMENT_QA.md)（E-DESIGN 已建立，记录 Q-ID、选项、推荐、负责人回答与最终决策）。历史 `IMPLEMENTATION_RESEARCH.md` 保留作历史设计参考，**不再代表当前唯一方法**。
- **下一步是动态字段**：每次先查最新 [PROJECT_STATUS.md](PROJECT_STATUS.md) 的「当前任务/正在等待/下一步」，如果处于 E-DESIGN 再查 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 待答 Q-ID；数据来源与 Provider/Cache 政策详见 [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)，不得重复已经确认的问题、提前执行未授权工程或训练。
- 当前论文表述纪律：不要把状态字段数量本身作为创新点；**论文不讨论“多变量”或“混沌”**。新意必须靠任务级状态决策、Model × Effort、延迟成本/成功影响和严谨评测证明。

## 0.1 新对话恢复规则（持续生效）

**新对话角色**：ChatGPT 必须同时以长期 Planning Agent、需求探索/方法讨论伙伴、论文文献研究者的身份工作。和用户讨论研究方向、相关工作、训练监督、Kev/Jev、论文图及框架；实际本机文件由 Codex、服务器公开数据由 Execution Agent 处理，不宣称自己可实时访问本地/服务器。启动时读取全部五核心文档及最新证据，历史计划与真实执行分离。


- **版本**：首先核查 GitHub `main` 最新 HEAD，从同一提交读取四份正式文档；文中旧 SHA、日期、章节「当时」均不作为实时证据。
- **唯一状态来源**：[PROJECT_STATUS.md](PROJECT_STATUS.md) 首页；**实验决定**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md)；**长期历史与协作**：本文件；**研究假设与方法**：[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)。
- **证据分层**：GitHub main、实际本地工作树、授权服务器部署、实验数据/结果分别核对。没有最新 Execution 回报就不能声称知道本地未推送更改或服务器实时状况。
- **冲突处理**：先确认是否只是历史快照，查看明确日期与最新提交；仍有冲突则说明并请负责人裁决，不擅自猜测、reset、覆盖或重写。
- **恢复输出**：HEAD、当前阶段、最近已批准事项、唯一进行中事项、阻塞与权限、下一行动和证据缺口；直接接续而非重跑已完成阶段。
- **更新闭环**：有用户明确决定、任务验收、阶段切换或真实实验结果时更新各自负责的文档、记录日期和影响并校验远端提交；没有新事实就无需更改。禁止未经请求的深度研究、服务器操作或付费使用。

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
| D-010 | 初期三份 Markdown 为公开事实源，E-DESIGN 后增为四份 | 支持 ChatGPT 与本地 Agent 交接、审阅和版本控制 | 已确认 |
| D-011 | 采用轻量 Git：默认 main、本地频繁 commit、按会话/里程碑或最长 24 小时工作周期 push；不要求 PR | 研究实验优先可追溯和及时备份，避免不必要的工程流程 | 已确认（2026-10-09） |
| D-012 | 暂不迁移或归档历史研究目录，保持当前物理结构 | 现有目录可控，移动 PDF/截图可能破坏引用且不减少 Git 历史体积 | 已确认（2026-10-09） |
| D-013 | 服务器未来采用独立 ModelRouter 工作目录与 Python 环境；既有共享资源只读；本轮禁止实际服务器操作 | 降低对共享服务和既有资产的干扰，隔离实验依赖 | 已确认（2026-10-09，E0.5-ENV） |
| D-014 | 未来所有新会话从 GitHub 最新 main 及四份职责分离文档恢复，单一现状入口，事件后更新 | 防止旧聊天记忆、历史快照、推荐和未推送状态冒充当前事实 | 已确认（2026-10-09） |
| D-015 | Q-001=A：直接以真实公开 Coding Benchmark 为首轮任务来源，不要求自建合成任务先行 | 负责人明确选择 A 取代 Planning 原推荐 C；实际 Benchmark/样本量另议 | 已确认（2026-10-09） |
| D-016 | Q-002=B：商业 API 与本地开源模型进入同一候选池，effort 按真实能力标注 | 联合模型与推理档位、处理异构可用性，不伪造不支持的 effort | 已确认原则（2026-10-09）；型号待核验 |
| D-017 | Q-003=B：分阶段预算，本地模型费用无预先固定上限，API 按模型限额；额度及执行权限未批 | 区分预算原则、物理资源用量与实际操作授权 | 已确认原则（2026-10-09）；额度/权限未决 |
| D-018 | Q-004=B：成功率约束下最小化整任务成本，具体阈值待定 | 与任务级研究主目标一致，避免只追逐调用价 | 已确认原则（2026-10-09） |
| D-019 | Q-005=B：分层基线与消融，历史 admission-only 仅作对照 | 需要区分运行时状态、effort、缓存的增量价值 | 已确认范围（2026-10-09），实施细节暂缓 |
| D-020 | Q-006=A：同一决策前状态受控分支为主验证原则，实施细节暂缓 | 仅历史观察数据无法提供未选动作真实结果 | 已确认原则（2026-10-09）；另有“rq 3 需要 ab 同选”待澄清 |
| D-021 | 当前 Planning 问答优先逐阶段讨论**如何训练模型**，暂不展开具体实验实施 | 负责人改变讨论优先级，不改变已确认的长期模型路由研究主线或 E1～E5 授权门槛 | 已确认协作要求（2026-10-09） |
| D-022 | Q-007 首阶段从 A 公开 Agent 轨迹着手；规划覆盖八组状态，但不制造缺失标签 | 负责人“从 A 开始”只明确起点，完整训练数据闭环（含自采）仍待商定 | 首阶段方向明确（2026-10-09），全阶段未冻结 |
| D-023 | 数据源、厂商模型/缓存/计费政策需要**一个专门长期台账**，先登记再逐源选择，最后才讨论 AI 数据清洗；Q&A 保留用户正式批准的唯一裁决 | 唯一详细台账位于 our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md；不得在 Q&A/Research/Status 另维护平行最新版，不新建第二条执行链 | 结构需求确认（2026-10-09）；数据选择/清洗/训练未授权 |

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
- 根据真实报告或明确决定按职责更新四份文档；无新增事实的讨论不制造进度提交。
- **不能**声称自动监听本地或服务器、自动运行后台任务、或已完成未实际执行的实验。

### Execution Agent（本地 Agent）

- 严格按任务卡执行，先检查工作区状态和最新 GitHub HEAD；发现未提交修改不得覆盖、reset、clean 或强推。
- 可在任务卡授权范围内修改代码、运行测试，按职责检查四份文档；频繁本地 commit、定期 push；记录本地 HEAD、远端 HEAD、测试结果和已知风险。
- 不擅自访问新主机、安装大型依赖、下载模型、占用共享 GPU、调用付费 API、修改生产服务或上传私人数据。
- 任务完成必须**检查**四份文档：Memory 记决策/交接，Status 记实测进度；Research 仅在证据、方法或实验协议变化时修改。无需修改的文档在交付报告注明即可，不做无意义提交。
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
| E-DESIGN | 详细实验设计与用户决策（`EXPERIMENT_QA.md`） | **进行中：Q-007 首阶段 A 起步明确；Q-010/Q-011 后续依次讨论** | 唯一 Q-007 第一阶段公开数据/八组变量/可信标签讨论工作包；Q-008/Q-009 实验细节暂缓，资源许可未批 |
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

**问答登记文件**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md) 已在 E-DESIGN 启动时建立，专职记录 Q-ID、问题、选项、Planning 推荐及理由、用户回答、最终决策、日期和实验/预算/论文影响。2026-10-09 第二批 Q-004=B/Q-005=B/Q-006=A 已补记，和第一批共同保留；目前优先 Q-007 的公开轨迹 A 阶段，Q-010/Q-011 待依次讨论，Q-008/Q-009 实验细节暂缓。具体以 Status 首页和 Q&A 为准。

**后续工程衔接（MR-E1-001）**：待 E-DESIGN 问答决策完成并冻结实验边界后，再由 Planning Agent 下发 MR-E1-001 任务卡，启动本地最小工程骨架与 Schema 开发。建议交付包含 `pyproject.toml`、`src/modelrouter/`、`tests/` 等本地轻量代码，不连服务器、不调用付费 API。

## 8. 交接时的固定回复格式

每次 Execution Agent 结束任务时报告：

- `Task / Status / Local HEAD / origin/main HEAD / Ahead-Behind / Dirty / Last push`
- `Observed facts`（审计时间与证据范围；服务器部署 SHA 或“未部署”）
- `Files changed`（四份正式文档逐份注明“已修改/已检查无需修改”）
- `Tests run`（通过/失败/未运行）
- `Resource / cost usage`（仅真实数据）
- `Risks / blockers / Next recommended task`（不自动执行）

Planning Agent 必须使用第 10 节新会话恢复协议；先核对 GitHub HEAD，按 [Status](PROJECT_STATUS.md) → [Q&A](EXPERIMENT_QA.md) → Memory → [Research](RESEARCH_OVERVIEW.md) 的顺序确认唯一下一行动。

## 9. 文档分层与按时间顺序的交接记录（MR-DIR-001 新规则）

### 9.1 文档体系与职责分工

| 类别 | 文件 | 读者 | 更新触发与职责 |
|---|---|---|---|
| A · 交接/记忆 | 本文件 `PLANNING_MEMORY.md` | Planning + Execution | **每次任务与决策**；按时间追加审计事件、Planning 审查意见、纠正事项、提交记录与后续决策 |
| B · 研究总纲 | `RESEARCH_OVERVIEW.md` | 项目负责人/论文研究 | **研究证据、方法或实验协议改变时**；方法未变时无需修改，避免流水账 |
| B · 进度看板 | `PROJECT_STATUS.md` | 项目负责人 | **每次任务状态变化**；统一首页看板、阶段表、工作包队列，确保当前状态一致 |
| C · 实验问答决策 | `EXPERIMENT_QA.md` | Planning + 项目负责人 | **已于 2026-10-09 E-DESIGN 启动时建立**；专职记录 Planning 提出的实验设计问题、选项、负责人回答、最终决策及日期 |
| D · 数据源与 Provider 政策 | [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md) | Planning + Execution + 数据审核 | **唯一详细数据/政策台账**；维护 Source IDs、官方链接、证据、许可证、八组状态映射、缓存实测/模拟等级、候选选择栏与下一阶段 AI 清洗质控；逐源选择仍回 Q&A |

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

### 9.6 历史阶段说明（以下是旧快照，不代表现状）

> **这一节保留 E0.5 确认前的原始阶段记录；最新阶段唯一由 [PROJECT_STATUS.md](PROJECT_STATUS.md) 首页确定。**

- **执行路线**：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- **当时状态（已过时）**：MR-DIR-001 与 MR-SYNC-001 当时已验收；E0.5 当时待服务器边界确认；E-DESIGN 当时尚未开始。**随后 E0.5 已完成并启动 E-DESIGN，详情见 9.9 与最新 Status。**
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
- **首轮问题（当时的历史记录）**：Q-001 提出时 Planning 推荐分阶段混合任务方案 C，当时尚待用户答复。**后续 2026-10-09 负责人已明确选择 A**，并确认 Q-002=B、Q-003=B 预算原则。当前待答是第二批 Q-004～Q-006，之后依次完成余下问答；具体情况仅以最新版 Q&A/Status 为准。
- **Git 同步边界**：本次文档由 Planning 直接提交 GitHub main；Execution 的上一轮本地 HEAD 快照在提交后不再等于最新远端 HEAD，下次本地工作前先安全 fetch/ff-only；保护私人未跟踪文件。

### 9.10 E-DESIGN 第一批决策与第二批交接（2026-10-09）

- **负责人明确答复**：Q-001=A（直接使用真实公开 Coding Benchmark）、Q-002=B（商业 API + 本地开源混合池）、Q-003=B（分阶段预算；本地模型推理费用不设固定上限，API 额度按具体模型限制）。
- **历史建议处理**：Q-001 原 Planning 推荐 C 已被 A 取代；不重启旧 admission-only 研究线。真 Benchmark 内的小样本 smoke 可讨论，具体任务集/数量仍待批准。
- **授权**：只批准实验路线与预算**原则**；API 每模型具体额度未填，未授权付费调用、服务器访问/写入、GPU、安装、模型下载或训练。
- **唯一当前工作包**：E-DESIGN 第二批 Q-004～Q-006 已提出，等待负责人选项；其后继续 Q-007～Q-010 和尚未补齐的额度/任务/evaluator 细节。没有开始 E1。
- **写入职责**：Q&A 保存原话与选择，Status 首页保存唯一当前任务，Memory 保存 D-015～D-017 及交接；Research 仅同步 Q-001/Q-002/Q-003 的实质实验协议影响。此记录不宣称本地 Codex 或服务器状态已被直接核验。

### 9.11 E-DESIGN 第二批确认与训练优先交接（2026-10-09）

- **明确决定**：Q-004=B（成功率约束下优化整任务成本）、Q-005=B（分层基线/消融）、Q-006=A（严格同状态分支原则）；这三项已经由负责人明确答复，具体实施暂缓。
- **原话及未决指代**：“rq 3 需要 ab 同选”；在已给定 Q-006=A 的同条消息中出现，指代 RQ3 还是第三题尚不清楚，不擅自补成 Q-006=A+B。留在 Q&A 核对。
- **协作指令**：先只讨论模型如何训练，分阶段推进，暂缓实验实施/规模/统计/场景细节。这是**当前讨论顺序**的改变，不是直接跳到 E4 或重开一条训练工程链。
- **唯一下一工作包**：在既有 Q&A 文档中提问 Q-007（训练数据）、Q-010（Kev 训练初始化）、Q-011（监督目标/阶段），其他 Q-ID 未关闭的细节保留、不得视作批准。
- **权限**：没有新增任何服务器、共享资源、GPU、付费 API、安装/下载或训练执行许可；GitHub 远端与本地/服务器状态须分层报告。

### 9.12 Q-007 第一学习阶段公开轨迹研究（2026-10-09）

- **负责人方向**：“第七个问题需要仔细查询……最后决策用的变量有多个，需要都覆盖到；从 A 开始”。记为第一阶段优先公开 Agent 轨迹，不误认完整训练只能用 A。
- **八组状态**：Task/Subtask、Agent/Coordination、Context/Memory、Tool/Environment、Verification/Recovery、KV Cache/Continuity、Temporal/Execution、Provider/Availability。还需 Action/Constraints 与 Outcome/Provenance；可缺失但不能虚构成功、物理缓存或 effort 标签。
- **外部证据**：Open-SWE-Traces（首选，许可记录在 Q&A）、CMU agent_trajectories、SWE-Gym、AgentSuite（用途/许可需区分）；Finding the Right Fit 明示不可用于微调或训练。
- **学习阶段建议尚未批准**：公开前缀 + 已执行动作结果预测，若有真实账本才学观察到的 cost-to-go，随后再讨论有真值的预算/能力规则辅助与可比动作的 choice 训练。Kev 官方 continuation 推荐仍需 Q-010 确认。
- **状态/权限**：只进行了只读源研究与文件更新，没有下载数据、运行训练、使用 GPU/付费 API、访问或修改服务器。

### 9.13 Q-007-R1：开源数据与训练预处理方案（2026-10-09）

- Planning 按负责人要求研究两类训练主数据：Agent 运行轨迹与静态任务-模型结果；并审查八组状态、缓存和厂商规则、所需数据量。
- 数据源、具体许可证阻塞、预处理顺序、真实标签与规则标签边界、阶段划分，详见 Q&A 的 Q-007-R1；未知许可证数据不得加入训练，Finding the Right Fit 明确禁止训练。
- 本轮为**只读研究及文档提案**，无真实语料下载/处理/训练、无服务器/GPU/付费 API 使用；唯一当前任务仍是第一大阶段 Q-007 训练数据来源及加工方案的审议。

### 9.14 Q-007-R2：多变量数据目录和 OpenSquilla 架构研究（2026-10-09）

- 用户要求先把**缓存真实调用与复用、Context/Memory、Agent 协作、执行时间预算、主要中国及国际 Provider 政策**数据源列完整；不讨论数据量，不清洗、不启动工程。
- Q&A Q-007-R2 新增 Mooncake FAST25 真实请求前缀 hash（reuse potential 非实报 cache hit）、BurstGPT/阿里 xMaaS 的时间资源负载、LongMemEval-V2/LoCoMo 等记忆、MARBLE/MASBench/AgentWorld 等多 Agent，供应商政策登记和局限。
- OpenSquilla 论文与实际代码明确 Harness/Router/Memory/Context 分工，可供单一 ModelRouter Harness 的结构参考；不在此阶段复制完整 Agent 产品、也不启动并行实现链。
- 本轮只增加数据候选目录和长期研究记忆，**无下载/清洗/训练/模型推理/GPU/服务器/付费 API**；具体原始数据许可证和每字段覆盖率未实际审计。

### 9.15 Q-007 数据与政策专用台账正式建立（2026-10-09）

- 负责人要求在文档中**专设一处**长期登记公开训练数据源、主流模型与供应商政策、KV 缓存政策，然后按批准结果挑选哪些数据、如何让 AI 合规清洗。
- GitHub main 建立 [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)，在既有 data/ 目录下唯一维护原始来源、八组变量、Cache 数据真实性、Provider 官方证据、选择状态和后续数据加工质量合同；原 Q-007-R1/R2 仅保留作为历史研究与问答，不再平行更新政策详细清单。
- 仍无数据源逐项批准、真实下载/清洗/训练、服务器/GPU/API 使用授权。下一步负责人审阅 Source Registry/Provider Policy/Selection Board，项目阶段 E-DESIGN 不变。

### 9.16 Q-007 文件数量审计与真实数据源清洗/训练规划（2026-10-09）

- GitHub main 文件树检查：210 个文件，44 Markdown，五份当前核心管理文档（Status、Q&A、Memory、Research、Registry）；历史 IMPLEMENTATION_RESEARCH 与导航 README 不计入核心五份。
- 明确不是过度物理拆分，而是 Q&A 历史 R1/R2 / Research/Memory 重复数据事实。**以后 Registry 唯一更新最新 Source/Provider/Cache/AI 清洗详情；Q&A 记录负责人选择，Status 保留唯一当前任务。**
- 官方数据卡与 Kev 训练格式复核：Open-SWE 参考补丁不能进决策输入、SWE-smith 多 split 需核、Mooncake hash 只代表缓存可复用潜力、LLMRouterBench 许可仍待审、Kev 通用微调记录有严格 2048 token 限制。
- Registry §6.2～6.5 已列推荐最低源、source-specific normalize、task/repo split、真实标签/静态比较/缓存模拟的分离及 Kev M1～M4 训练路线。全部是 Planning 推荐，**没有逐源批准、下载/清理、训练或模型/API/GPU 操作**。

### 9.17 E-DESIGN 路由训练相关工作、论文方法图与外部 Harness 方案（2026-10-09）

- 负责人提出：当前数据→清洗→训练顺序是否学术充分，传统/神经模型路由及 LoRA 类论文怎么训练与发表，论文方法图怎么画，外部 Agent 框架怎样搭。
- 本轮只读核对 RouteLLM (ICLR 2025)、FrugalGPT (TMLR 2024)、BEST-Route (ICML 2025)、Route-to-Reason (2025 / WWW 2026)、TwinRouterBench、Budget-Aware Agentic Routing、ProgRouter、HM-Router、OpenSquilla、Kev 官方格式及 mini-SWE-agent/LangGraph 官方能力，完整比较见 RESEARCH_OVERVIEW §6.2。
- 研究结论：数据清洗前必须定义路由状态/动作/合法池/真实标签，训练前需要最小 Harness state/log/checkpoint 契约和可验证任务终局；训练中的 observational outcome、static preference、cache reuse 与同状态 counterfactual 严格分离；建议单 Kev 的领域适配与后续真实配对决策分阶段，**不规定必须 RL**。
- 论文方法图应分「在线 Agent/Harness/Router/Provider 账本」和「离线多来源 supervision → Kev 训练 → 同状态比较/校准」；OpenSquilla 现行公开 SquillaRouter 自学习已移除，不能当现成在线训练引擎。Harness 未来只批准**单一主实现/调用入口**，优先比较 mini-SWE-agent（coding 基准）和 LangGraph（多 Agent checkpoint）。
- 这轮仅作学术规划文档更新，不批准 Q-010/Q-011、下载/清洗真实数据、服务器/GPU/API、编写代码或启动训练。唯一当前讨论包仍是 Q-007 数据源审核，Status 不变。

### 9.18 最简论文实验流程与 Kev 微调执行风格（2026-10-09）

- 负责人最新明确：删去工程审批门禁、复杂工程单测/CI、防御性框架、版本冻结和哈希管理；仅一个终端入口，优先真实数据清理、微调与进度输出。
- Research §6.3 已说明公开来源→可信监督→Kev LoRA 初始适配→Harness 同状态比较→动态路由微调→任务级评估。保留训练/测试分割、未来泄漏、cache 真实标签区分这三项科研事实约束。
- 本轮只更新研究设计和协作规则；已上传清洗脚本仍非可比较的最优路由标签数据集。没有执行 GPU/训练/下载新数据，拟议 run_experiment.py 尚未创建。

### 9.19 五文档持续对话、Paper Research Router/Obsidian 与服务器任务交接（2026-10-09）

- 当前唯一科学主线：长程单/多 Agent 执行中，联合 model×reasoning effort、KV 缓存、8 组状态与实际任务级总成本；目标是成功率约束下节省整任务费用。现有 Blog/CCH 221,128 行→178,621 样本来自本地执行报告，是实际调用记录而非真实最优选择标签。GitHub main 可核 prepare_router_data.py；公开 Agent 数据服务器清洗还未收到实测报告，Kev 尚未训练。
- 分工：ChatGPT 为 Planning/科研讨论；本机 Codex 完成最新 GitHub 文档同步、真实 Skill 调用、PDF 阅读、Obsidian 一文一笔记；服务器 Execution Agent 在自有中文研究目录做公开源下载/CPU 清洗和统计，所有大数据留服务器。
- 已查实 Skill 位于私有 sxyq/skill- 的 latest/skills/codex/paper-research-router/SKILL.md，本机通常检查 ~/.codex/skills/paper-research-router/SKILL.md；它对已有 PDF 提供 intake、paper-reader、页码证据与结构化笔记。新论文检索由 sxyq/research-router 的 research-router 负责，证据审阅可用 literature-evidence-audit。其 paper-intake/reader 的完整研究 workspace 模式可能需要未随 Skill 附带的 .research/schema，缺失时采用轻量 Obsidian 笔记。
- 本仓库 research/task-level-cost-routing/literature/pdfs/ 实有 **58 个 PDF**；manifest.json 仅有 **54 条**，README/index 也截至 54；55–58 对应 CATS、Harness-Native Agentic Routing、EET 和 Price Reversal。先补现有 manifest/index/README 的差额，勿重复下载。以原 literature 文件夹作为一个 Obsidian Vault，在其中新增中文 论文笔记/ 和 主题索引/；每篇用唯一编号、规范 frontmatter、[[wikilinks]] 与原 PDF 相连。
- 第一轮重点论文：SWE-Router、TRACE-Router、PROGROUTER、TwinRouterBench、Boundary-Guided Agentic Routing、Harness-Native Agentic Routing、TACIT-Switch、EarlyEval；Route-to-Reason、Switchcraft、BEST-Route、UNISCALE；RouteLLM、RouterBench、LLMRouterBench；Unified AI Gateway、InfraMind、KVFlow、LMCache、TokenDance；Kev、TypeSafe Jev/System One、Visual Jev、Laya、Simple Jev、AnyJev。分别标明真实训练数据、训练方式、结果和本项目对照差异，所有断言追溯原文。
- 新目录和新 Markdown 报告尽量中文；技术代码、标准目录、原数据集英文名不批量改。用户不希望 CI/工程门禁/版本冻结/复杂 hash 管理；最小论文真实性检查依旧必要。GitHub 只提交代码/报告/少量公开笔记，不提交私密现场、大数据、凭据。
- 本轮是 Planning 在远端五文档同步后的交接约定，**并非本机 Codex/Obsidian/服务器数据已经执行完成的证明**。

### 9.20 服务器首批公开数据运行报告的科研审阅（2026-10-09）

- Execution 报告/远端 main 966f582 可核对：本地/服务器运行新增 prepare_router_data.py public 模式，原始下载约 405MB，导出 20k Agent step、30k Arena 偏好、30k Mooncake 请求、970 TwinRouterBench，合计 80,970 样本，并写 train 57,165 / val 12,123 / test 11,682。实际读取的 Open-SWE 和 SWE-smith 都只是一份 Parquet shard，并非全部官方公开轨迹；LLMRouterBench 仅索引了任务目录。Planning 已核对 GitHub 代码和 50 条预览，**没有登陆服务器重新核验完整原始/清洗 JSONL**。
- **重大标签审查**：Agent 的 step_complexity=step/error 阈值、is_high_effort=complexity==high、cache_hit=step>1；Arena 的 is_high_effort 取 winner 模型关键词或 prompt 长度，cost_tier 由 prompt 长度估出，state 只有 prompt_chars 无实际 Prompt；Mooncake 的 cache_affinity=hash prefix hit ratio 阈值、is_cache_hit=历史请求 hash 复用机会，不是实际 Provider cached_read。标签明显有多项规则映射/不对应真实动作，不能称 80,970 个最优 model×effort 标签。
- **泄漏/评测**：Agent 清洗在处理 assistant 当前消息后才记录 context_chars/prior_tool_calls，包含当前动作信息（pre-decision 泄漏）；原脚本按 trajectory ID 分 Train/Val/Test，无法保证同一真实 instance/repo 不串集；Mooncake 每 100 条人造 task_session_id，不是真任务；TwinRouterBench 被合入 training，失去独立评测效力。未实际评估跨同题重复，不能称严格无泄漏。
- **Kev 官方接口不兼容**：需将 choice.options 换成 choice.criteria map，score.levels 换成 score.criteria list，score.label 从 budget/standard/premium 字符串改为 0/1/2；只使用证据充分的监督问题。官方来源 jaredpalmer/kev 的 skills/kev-finetune/references/data-format.md 和 README.md；可用官方现有工具做单次轻量输入验证，然后才做小样本 LoRA smoke test。
- **唯一接续任务**：原始公开数据保留服务器，在唯一 prepare_router_data.py 上修正科研标签和数据格式；重提取 Agent 真实 outcome，只做 observed continuation 监督；Arena 原 Prompt+winner 做偏好；Mooncake 单独作为 cache workload；TwinRouterBench 留独立测试；模型最佳动作训练必须等同状态真实动作后续对照。优先向 Codex/Execution 派发修复，不额外创建 v2 脚本或 CI。
- **公开文档隐私提醒**：执行者提交的《服务器资源与目录说明》公开版曾含内部网络/登录及端口信息；Planning 已对最新 main 的公开版进行最小脱敏，但旧提交仍有历史痕迹。未来只写用户 Home 相对路径和公开可披露聚合硬件数；需要完全删除历史必须另行明确讨论。

### 9.21 Q-007 全量公开数据重建、真实清洗与四批次样本 GitHub 审查交付（2026-10-09）

- **彻底废弃旧产物**：Execution Agent 在 GPU 服务器与本机彻底删除此前由固定切片截取（80,970 条）和规则推断伪标签产生的旧清洗数据，保证无历史污染。
- **全量真实清洗完成（4 大批次，16 个核心数据集，2,282,484 条真实有效记录）**：
  1. **Batch 1 (Agent 执行轨迹)**:
     - `TRA-001` (NVIDIA Open-SWE-Traces, 6 代表分片, 942 MB): 43,154 决策步, `OBSERVED_ACTION`
     - `TRA-002` (SWE-smith Trajectories, 全部 8 分片, 972 MB): 107,983 决策步, `OBSERVED_ACTION` (Claude 3.7 Sonnet)
     - `TRA-003` (CMU Agent Trajectories): 上游 HTTP 403 Gated，严格执行零造假记录为 0 条
     - `TRA-004` (AgentSuite multi_challenge, 全部 8 模型全量 JSONL, 44 MB): 2,736 决策步, Thinking-On/Off 对照
  2. **Batch 2 (模型路由比较)**:
     - `ROUTE-001` (LLMRouterBench, 700 评测文件, 6.6 GB 解压): 548,059 条实测记录, 27 benchmark × 40 模型
     - `ROUTE-002` (RouterBench, 95 MB): 36,497 条 0-shot 样本, 11 模型评估 + Oracle 路由
     - `ROUTE-003` (TwinRouterBench, 1.2 MB): 970 步降级搜索标签, **强制标为 `EVAL_BENCHMARK_ONLY` 绝不进训练**
     - `ROUTE-004` (Arena 55k, 176 MB): 57,477 场真实用户 Prompt 与盲测胜负, `HUMAN_PREFERENCE`
     - `ROUTE-005` (Finding The Right Fit, 0.2 MB): 6,204 条多 Harness 实测开销, **标为 `RESEARCH_ANALYSIS_ONLY` 禁训**
  3. **Batch 3 (KV 缓存与时间负载)**:
     - `CACHE-001` (Mooncake FAST'25, 3.2 MB): 39,632 条请求, 前缀块复用机会标为 `OBSERVED_REUSE_OPPORTUNITY`，绝不冒充商业 Provider 实际缓存
     - `TIME-001` (BurstGPT, 49 MB): 1,404,294 条生产环境请求真实时序到达与负载, `OBSERVED_WORKLOAD`
  4. **Batch 4 (记忆、协作与任务环境)**:
     - `ENV-001` (SWE-Gym, 42 MB): 2,438 个任务环境基准与回归测试套件, `TASK_ENVIRONMENT`
     - `ENV-002` (SWE-rebench-V2, 409 MB): 32,079 个跨 20 种编程语言任务基准, `TASK_ENVIRONMENT`
     - `MEM-003` (LongMemEval-V2, 0.8 MB): 451 个长程任务与 100 轮干草堆记忆, `MEMORY_BENCHMARK`
     - `MEM-005` (MemoryCraft, 16.5 MB): 510 条跨会话记忆与问答对, `MEMORY_BENCHMARK`
     - `MAS-001` (MARBLE-MultiAgentBench): 上游 HTTP 401 Gated，合规审计记录为 0 条
- **审查资产全部上线**：为每个数据集独立抽取 35 条代表性真实样本（`清洗样本.jsonl`）、完整统计（`字段统计.json`）与规范说明（`样本说明.md`），全部提交并推送到 GitHub main。
- **唯一脚本演进**：保留唯一主程序 `prepare_router_data.py`，未建立任何并行清洗入口或冗余工程门禁。
- **当前状态**：四批次全部交付完成，等待 Planning Agent (ChatGPT) 审查 GitHub 独立样本并给出下一步指示。

### 9.22 Q-007 公开数据全量重建科研纠偏执行完成（2026-10-10）

- **差额澄清与数量统一**：Execution Agent 查明此前 1,681,177 行差额源于旧报告误将轨迹数填入步数列。本轮重新清洗后，**16 源 `字段统计.json` 汇总数（6,600,628 步/条）与服务器物理文件实际 `wc -l` 绝对吻合，差额为 0**。
- **全量分片下载与清洗扩充**：
  - `TRA-001` (Open-SWE-Traces): 12 分片，30,000 轨迹，2,075,629 决策步，保留 Qwen3.6/3.5/3.8/DeepSeek/MiniMax 真实开源模型。
  - `TRA-002` (SWE-smith): 全部 24 分片（8 ticks + 8 tool + 8 xml），76,002 轨迹，2,331,584 决策步，抽取 125.6 万次 `str_replace_editor`、90.1 万次 `bash` 与 12.2 万次 `submit`，彻底根除“全为 text_response”缺陷。
  - `TRA-003` (CMU Agent): 上游 HTTP 403 Gated，如实记录为 0 条，不造假。
  - `TRA-004` (AgentSuite): 全部 30 模型/思考模式，8,190 episode，41,430 步，提取 `meta.id` 对齐 273 个独特任务实例，生成同题跨模型审查组。
  - `ROUTE-001` ~ `ROUTE-005`: 涵盖 548,059 条 LLMRouterBench、36,497 条 RouterBench、970 步 TwinRouterBench（移除未来 total_steps 并强制 `EVAL_BENCHMARK_ONLY`）、57,477 场 Arena 人类盲测偏好、6,204 条 FindingTheRightFit（强制 `RESEARCH_ANALYSIS_ONLY`）。
  - `CACHE-001` (Mooncake): 39,632 条请求，按时间戳排序，计算严格 LCP 连续前缀匹配，`output_length` 隔离至事后结果，抽取连续 35 条请求展示动态演进。
  - `TIME-001` (BurstGPT): 1,404,294 条生产环境请求真实时序到达与 Token 负载。
  - `ENV-001` & `ENV-002`: 2,438 个 SWE-Gym 与 32,079 个 SWE-rebench-V2 跨语言任务环境。
  - `MEM-003` (LongMemEval-V2): 451 个长程记忆任务，成功载入 `questions.jsonl` 真实题面、企业领域、环境名称、标准答案与评估函数。
  - `MEM-005` (MemoryCraft): 扩充包含 `ama_bench` 与 `membench`，有效记录达 23,884 条。
  - `MAS-001` (MARBLE): 上游 HTTP 401 Gated，如实记录为 0 条。
- **十项代码级缺陷彻底闭环**：时序严格递增、模型标识客观真实、多格式动作识别、跨模型同题对齐、LCP 前缀匹配、排除未来泄漏、记忆题面注入、多来源扩充、动态缺失率计算、单脚本独立 `--mode public` 运行。
- **当前状态**：16 组样本与统计已全部推送到 GitHub main，等待 Planning Agent（ChatGPT）通过 GitHub MCP 进行最终审查。

## 10. 新会话恢复协议（长期生效）

### 10.1 每轮研究如何接续与更新

1. **启动**：核验 main HEAD → Status → Q&A → Memory → Research → Registry → 必要最新 Execution 报告与论文资料，不能只用此前聊天记忆。
2. **继续**：以 Status 首页任务/实测、Q&A 已确认选择为准；同时继续和用户讨论相关论文、方法、实验设计、训练与研究创新，不将当前委派执行任务误报为完成。
3. **完成决策**：负责人明确回答 Q-ID 时，Q&A 记录答复、最终决策、日期、实验和预算影响及下一题；Status 改进度/当前任务；重要长期决策追加 Memory 的 D-ID/交接事件。
4. **完成工程/实验**：Execution 提供 Git SHA、任务编号、已完成/未完成、真实测试证据、资源/费用、未推送状态、阻塞和下一工作项；更新 Status 和 Memory。只有方法/证据/协议真正变化时才更新 Research。
5. **验证**：公开脱敏，按既定 main 工作流提交，重新读取 GitHub 最新 HEAD 和改变的文件验证；不能凭此推断服务器实时状况。无新事件不产生空更新，不为新窗口另造文档/代码分支或第二套流程。
6. **执行范围**：用户已有公开数据服务器 CPU 清洗、本机 Codex 文献整理的明确任务要求；不扩展为 GPU 训练、付费 API、修改共享服务。研究文献检索按用户当前问题进行。

### 10.2 通用 ChatGPT 新窗口启动提示词

以下可直接复制到以后任意新 ChatGPT 对话；不写死日期、阶段或 SHA。

~~~text
你是 ModelRouter 项目的长期 Planning Agent，同时是我的需求讨论、模型训练、相关工作/论文和研究方法论讨论伙伴。不要重新开题、重复询问已确认的问题或虚构实验进展。

仓库：https://github.com/sxyq/modelrouter。先核对当前最新 main HEAD，依次读取五核心文档：
1. our-project/planning/PROJECT_STATUS.md
2. our-project/planning/EXPERIMENT_QA.md
3. our-project/planning/PLANNING_MEMORY.md
4. our-project/planning/RESEARCH_OVERVIEW.md
5. our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md
按当前问题再核查 prepare_router_data.py、执行 Agent 报告、research/task-level-cost-routing/literature/manifest.json、index.md、pdfs/ 和原论文正文。报告哪些是 GitHub 实际证据、哪些是用户/Execution 自报、哪些只是计划。不要把历史 Status 里的旧快照当最新。

科学主线：长程单/多 Agent 在调用前观察真实八组状态，考虑模型、推理 effort、KV 缓存连续性、任务成功率与完整任务成本，用已发布 Kev 类决策骨干进行可验证的监督适配和后续真实任务路由。静态模型偏好、已执行轨迹结果、前缀复用机会与同状态真实动作比较不是同一种标签；不能造最优 Model×Effort 标签。论文原创可写我们的路由/监督/任务级研究方法，但必须如实披露已有 Kev/LoRA，TypeSafe Jev 原厂训练不可假称复现。

角色分工：你负责 Planning + 深入需求和学术讨论；本机 Codex 负责 GitHub 文档同步、论文 Skill、Obsidian 笔记和必要代码；服务器 Execution Agent 在用户自有服务器下载/CPU 清洗公开数据。用户指定新研究目录和 Markdown 尽量中文，代码/开源数据集正式名保持英文。单一清洗主链，不搞工程化门禁/CI/复杂 hash 系统；保留必要科研数据隔离和标签真实性。未收到执行报告就写待执行，不得自己声称完成。

文献资源已在本仓库 literature/pdfs/ 有 58 PDF，但旧 manifest/README 仍列 54；本机 Codex 应先补清单，利用 ~/.codex/skills/paper-research-router/SKILL.md（源仓库 sxyq/skill-）对已有 PDF 一篇一中文 Obsidian 笔记；新文献搜索由 sxyq/research-router 负责。不要建立第二套 PDF 仓库。最新 Execution 已输出公开数据约 80,970 混合样本，但 Planning 发现大量规则伪标签、并非真实最优动作，TwinRouterBench 与训练混合、Kev JSONL 还缺官方 schema 转换，因此下一阶段是**修正数据标签与独立划分，不是盲目马上训练**。重点核对 Agent 动态路由、模型×推理档位、KV/成本反转、Jev/Kev 训练相关文献的真实数据、方法、评价与缺陷。

启动时简洁汇报当前阶段、真实已完成/委派中、证据差异、直接相关论文和下一步问题；然后立即继续回答我这次的问题。获得新执行成果后更新五核心文档相应职责，并核实 GitHub。无需对用户重复问答，必要时才提出真正改变研究路径的单个问题。
~~~

### 10.3 信息缺口和回退

GitHub 公开文件只能表示已推送事实，不能自动提供本地未推送代码、私人配置、服务器状态与未公开实验轨迹。新会话必须说明哪些内容经过独立核实，哪些仍需用户或 Execution Agent 补充；**不能承诺任意新窗口自动获得当前私有上下文**。

