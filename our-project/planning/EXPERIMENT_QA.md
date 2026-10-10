# ModelRouter · E-DESIGN 实验设计问答与决策记录

> **版本 v1.3｜建立：2026-10-09｜第一、二批决策：2026-10-09｜阶段：E-DESIGN（进行中，尚未冻结）**
>
> **职责**：记录每项实验设计的 Q-ID、问题、选项、Planning 推荐及理由、项目负责人回答、最终决策、日期，以及对实验设计、资源/预算和论文结论的影响。研究方法总览见 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)，实时阶段见 [PROJECT_STATUS.md](PROJECT_STATUS.md)，交接历史见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据边界**：本文件中“Planning 推荐”不是用户批准；“待回答”不是最终决策；预案任务数量和费用均不代表已执行或已授权。当前负责人已明确要求在自有服务器进行公开数据下载与 CPU 清洗、在本机用 Codex 整理论文库；其他 GPU 训练/付费 API/共享服务修改并未因此获批。

## 0. 阶段入口与决策规则

- **E0.5 已完成（2026-10-09）**：负责人确认未来在授权服务器使用独立 ModelRouter 工作目录与独立 Python 环境，现有共享资源只读；仅确认原则，尚未部署。
- **E-DESIGN 最新进度**：Q-001=A、Q-002=B、Q-003=B 预算原则、Q-004=B、Q-005=B、Q-006=A 已确认。Q-007 公开数据优先路线现已委派服务器清洗；本机 Codex 被要求同步 GitHub 五核心文档及构建 Obsidian 论文笔记。Q-010/Q-011 微调细节仍待研究；文献整理和数据 CPU 清洗无需重新请示。
- **研究问题**：长程单/多 Agent 执行中，依据决策前可观测状态，在动态合法候选池中选择 `(model, reasoning_effort)`，能否在成功率约束下降低整任务成本。
- **E-DESIGN 退出条件**：任务/划分与终局 evaluator、候选池与 effort 支持、预算及审批边界、主次指标、基线公平性、成对实验可恢复性、数据训练/验证/测试隔离、统计协议和停止条件均由负责人明确确认。未完成不得启动 MR-E1-001。
- **纪律**：任务成功 ≠ API 成功；实际缓存读取 ≠ 可迁移 KV；调用聚合数据 ≠ 任务级标签；CCH USD ≠ Blog GPT quotaUnits；已观察的行为轨迹 ≠ 未执行动作的反事实结果。决策时刻不得使用未来信息。
- **维护**：每次用户答复后补齐原话或忠实摘要、最终决策、日期和影响；若改变旧决策，保留修订记录。默认直接提交 `main`，不需要 PR；公开内容先脱敏。

### 0.1 问答状态机与跨对话恢复

- `待提问`：尚未提出；`已提出待答`：Planning 推荐但用户未批准；`已确认`：用户明确确认并记录日期与影响；`暂缓/待证据`：保留阻塞；`已取代/撤销`：保留历史并说明新决策来源。
- 在新会话先读 [PROJECT_STATUS.md](PROJECT_STATUS.md) 当前任务，再核对本文件对应 Q-ID 的「用户回答/最终决策/日期」，只继续未关闭的问题。用户要求审查报告、比较方案或延续研究不自动构成对推荐的批准。
- 以后提出 Q-011 等新问题，继续维护这一个问答文档；明确决定后记录原答复、批准日期、最终状态、实验影响、预算与权限边界、下一依赖，并同步最新 Status/Memory。回答实验问题不等于自动批准模型下载、服务器操作、GPU、训练或付费 API。
- 必须区分真实任务 benchmark（如 SWE-bench 系列）、Agent 训练环境/公开轨迹（SWE-Gym、Open-SWE-Traces）、路由评测框架（TwinRouterBench）和本项目新采集的受控分支轨迹；已有轨迹不自动具备未选动作的反事实结果，许可与 evaluator 等尚需核验。

## 1. 决策队列（未回答的问题不视为批准）

| Q-ID | 主题 | 状态 | 对应关键假设 |
|---|---|---|---|
| Q-001 | 评测任务集、任务类型与 pilot 组成 | **已确认 A，2026-10-09** | H1/H3/H6 |
| Q-002 | 真实可用的 Model × Effort 候选动作与 provider 能力 | **已确认 B，2026-10-09；具体清单待核验** | H2/H5 |
| Q-003 | 总预算、单任务硬上限、API/GPU 授权门槛 | **B 预算原则已确认；金额/运行权限未决** | H3/H7 |
| Q-004 | 主要 estimand：成功率约束、总 USD、每成功任务成本与延迟 | **已确认 B，2026-10-09；成功率阈值待定** | H1/H3/H7 |
| Q-005 | 固定、task-only、规则/sticky、MLP/GBDT、admission-only 基线 | **已确认 B，2026-10-09；实现细节暂缓** | H1/H2/H4 |
| Q-006 | 相同决策状态的受控分支、后续 continuation policy 与复现边界 | **已确认 A，2026-10-09；“rq 3 需要 ab 同选”指代待澄清** | H3/H4 |
| Q-007 | 数据采集、训练/验证/测试隔离、任务泄漏与隐私 | **第一学习阶段 A 方向明确；全阶段数据路线待确认** | H1/H5 |
| Q-008 | Pilot/正式规模、seed、任务层配对统计与停止准则 | **暂缓，负责人要求先讨论模型训练** | H1–H7 |
| Q-009 | 多 Agent、失败恢复、缓存与动态 provider 场景的分层 | **暂缓实验分层细节** | H4/H5/H6 |
| Q-010 | Kev-4B 在 A6000 上的可行性门槛与降级预案 | **已提出待答：先确认训练起点，资源实测暂缓** | H5/H7 |
| Q-011 | 路由器监督目标与分阶段训练顺序 | **已提出待答：新训练设计问题** | H3/H5 |

## 2. Q-001｜首批评测任务集与 pilot 构成

**提出日期**：2026-10-09  
**状态**：负责人 2026-10-09 已确认 A；具体 benchmark/evaluator/split 未冻结  
**核心问题**：首轮是否优先使用可复现、自动验证终局的真实 Agent 任务，如何平衡 Harness 可靠性、外部有效性与可控实验成本？

### 选项

- **A｜直接使用公开真实 coding benchmark**：例如经许可证/环境检查后选取可复现的真实仓库修复任务；优势是外部有效性较强；风险是环境恢复、依赖、测试和模型费用高，初期很难把 Harness 故障与路由效应分离。
- **B｜只用小型自建可验证 Agent 任务**：本地沙箱中的 coding、工具调用、失败恢复任务；优势是可控、可重复、低成本；风险是任务分布狭窄，容易高估方法效果，单独用于论文主结论不足。
- **C｜分阶段混合（原 Planning 推荐，现已由负责人批准的 A 取代）**：先用约 **5 个**低成本、终局可自动判定的沙箱 coding/tool-use Agent 任务验证 Harness、ledger、恢复与状态快照；通过 pilot 门槛后，再引入经过复现性与许可检查的**公开真实 coding Agent 任务**作为正式主评测，并预留少量多 Agent/失败恢复分层任务。扩展到约 30 个任务 × 2 个动作 × 2 seeds 只是初始预算估算锚点，**不代表批准规模**。

### Planning 推荐及理由

**原 Planning 推荐 C（历史提案，现已由负责人批准的 A 取代）**。它把工程可靠性 pilot 与论文效度分开：先验证任务级成功判定、全链路 USD、相同状态恢复和失败记录；随后用真实任务验证是否能泛化，避免只在合成任务上得出过强结论。首轮不强制上复杂多 Agent 框架，但正式评测必须覆盖可观察的工具、验证、恢复状态；多 Agent 扩展须保证权限和可重放性。

**拟议准入条件（尚未批准）**：任务有可记录的起始快照、明确成功/失败/超时判据、隔离工具权限、可重跑的环境/依赖版本、完整任务级费用账本；同任务多策略使用一致的 evaluator、预算、候选池和工具条件。不能从旧 CCH/Blog GPT 调用日志伪造这些任务标签。

### 用户回答

**2026-10-09 负责人明确答复：Q-001=A。** 直接使用公开真实 Coding Benchmark，不采用独立自建小任务集先行的 C 路线。

### 最终决策与日期

**已确认 A；2026-10-09。** 首轮以经过许可证、版本、自动终局 evaluator 和环境可复现性核验的真实公开 Coding Benchmark 为主。可以先对真实 Benchmark 的少量任务进行 Harness smoke/pilot，但不强制先开发独立的合成任务集；具体 benchmark、规模、分割、evaluator 和执行费用尚待确认。本选择不批准安装/下载/API/GPU/服务器操作。

### 对实验设计、预算和论文的影响

- **实验设计**：A 更重真实仓库复现；B 更重 Harness 内部有效性；C 先小 pilot，再真实 benchmark 与复杂场景分层。
- **预算**：本问只决定任务类型与分阶段原则；调用费用、GPU 额度、正式样本量需在 Q-003/Q-008 单独审批。
- **论文**：若只选 B，必须限制外部有效性主张；若选 A/C，需公开任务筛选、失败/排除和污染检查规则。
- **后续依赖**：Q-002 动作池必须与选定任务的工具、上下文和 provider 能力兼容。

## 3. Q-002｜真实 Model × Effort 候选池

**负责人答复与日期**：2026-10-09，**Q-002=B**。  
**原选项**：A 仅商业 API；B 商业 API + 本地开源模型（已选）；C 仅本地开源模型。

**最终决策及影响**：混合候选池，按 provider/model/version 的实际工具、上下文、effort 和可用性建立 registry；不支持 effort 的本地模型不能虚构档位。需区分 API 费用与本地计算资源消耗；保持任务、权限和评价器一致。**具体模型清单、effort 支持、版本、候选数量和价格均待核验。** 不授权付费 API、下载或 GPU。

## 4. Q-003｜分阶段预算与实际运行权限

**负责人原话（2026-10-09）**：**“Q-003=B；初步预算：本地模型的预算不限制，API 额度根据模型进行限制。”**  
**原选项**：A 零付费 API；B 分阶段硬预算管理（已选，按负责人条件调整）；C 等待价格证据。

**最终决策及影响**：**已确认 B 预算管理原则；2026-10-09，具体金额及资源权限仍未确认。**
- **本地模型**：模型推理费用不设预先固定的预算上限，但仍需记录 GPU 时长、显存、延迟及合理的计算资源成本；不等于 GPU、显存、服务并发无限可用或已获使用许可，也不能把本地资源成本简单记作零。
- **API**：额度按具体模型分别设置硬上限并在到达限额时停止；**逐模型金额、单任务上限、总体费用边界、价格版本均未明确**，留作 Q-003 的未完成细节，不得擅自填写数字。
- **实际权限**：未授权实际服务器访问/写入、安装依赖、下载权重、GPU、训练、付费 API 或工程启动。批准预算原则不等于批准具体执行。待具体模型名单与 Q-004 指标确定后再细化额度和停止条件。

## 5. Q-004｜评价主目标（第二批，已提出待答）

**选项**：
- **A**：成功率与任务费用并列主指标，不预设成功率约束；容易展示，可能出现取舍和排序歧义。
- **B（Planning 推荐）**：先设成功率下限或相对强基线的非劣容忍度，再优化**整任务成本**；同时报告 success rate、总费用、cost/resolved、延迟、Pareto 与任务级置信区间。
- **C**：以质量–费用–延迟 Pareto 曲线为唯一主结果，不设单一优先目标；范围完整但论文主命题较分散。

**负责人回答（2026-10-09）：`Q-004=B`。最终确认**在成功率约束下优化整任务成本**；具体成功率下限/非劣容忍度、API 与本地资源费用可比口径尚待证据和后续批准。API USD 与本地 GPU 使用仍分开记账。此为目标原则的确认，不授权实验。**具体阈值暂缓。**

## 6. Q-005｜需要哪些公平基线（第二批，已提出待答）

**选项**：
- **A**：固定低成本、固定强模型、随机合法动作；低工程成本但贡献归因不足。
- **B（Planning 推荐）**：固定低成本/强模型 + task-only + rule/sticky/cache-aware + admission-only + 轻量 MLP/GBDT；另外做 Model-only、移除 state/cache 等消融，并按可复现性选少数直接相关工作对照。
- **C**：优先复现全部最近邻方法；覆盖多但工程开销与环境一致性风险高。

**负责人回答（2026-10-09）：`Q-005=B`。最终确认分层基线及消融范围：固定模型、task-only、rule/sticky/cache-aware、admission-only、MLP/GBDT 和必要的少数最近邻方法；具体复现与实验实施步骤依负责人新指示**暂缓讨论**。不得将历史 admission-only 恢复为主方法。

## 7. Q-006｜同状态分支与轨迹可恢复性（第二批，已提出待答）

**选项**：
- **A（Planning 推荐）**：从相同可恢复决策前状态快照出发，对两个真实合法动作分别 rollout，并固定后续 continuation policy、工具权限、预算、环境版本与 evaluator。
- **B**：只做历史轨迹的离线观察性回放；缺少未执行动作的真实反事实，不能声称因果对照。
- **C**：从任务开头多次重跑但不固定相同中间状态；可用于整体策略评估，不能替代局部严格同状态配对。

**负责人回答（2026-10-09）：`Q-006=A`。** 正式确认严格同一决策前状态分支作为后续主要受控比较原则，真实 Benchmark 恢复性及 continuation policy 等具体实现暂缓；本决定不授权实际 rollout。

**同一条消息的额外原话**：“rq 3 需要 ab 同选”。当前文档并无名为 RQ3 的已确认独立决策。它可能指第三个问题 Q-006 的 A+B，也可能指研究问题 RQ3 或后续批次的第三题。由于明确同时给出 `Q-006=A`，在指代核清之前**保留 Q-006=A 不自动改写为 A+B**。若确指 Q-006，则可将 A 的同状态受控分支与 B 的历史轨迹观察性分析作为互补证据，但二者的证据级别不可混同；这是待澄清的解释而非新批准。

## 8. 第三批训练规划问答（仅规划，不涉及实验实施）

**自 2026-10-09 起的唯一数据源与政策台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。Q-007-R1/R2 以下为**历史研究取证记录**，来源/模型/缓存政策后续更新仅在台账维护，避免同一信息出现多个“最新”版本；但负责人对具体源的批准、变更、日期和影响仍只能在本 Q&A 决策记录中生效。台账现仅候选，未批准下载/清洗/训练。

**负责人 2026-10-09 新要求**：“现在先不讨论具体如何实验 只讨论如何训模型一个阶段一个阶段的来”。保留现有 E0.5 → E-DESIGN → E1～E5 总路线，不提前启动 E4；当前只在 E-DESIGN 内依次讨论训练数据、训练起点、监督信号。Q-008/Q-009 的实验规模/场景协议待重新开启，Q-003 额度和资源授权仍未解决。

### Q-007｜训练数据从哪里来？（第一学习阶段 A 已明确；整体方案未冻结）

- **A**：优先使用经许可证和隐私核查的公开 Agent 轨迹，作为可用的**已执行动作**监督；承认缺少同状态未选动作标签。
- **B**：优先规划未来从真实 Coding Benchmark 自采高质量 Agent 状态与终局标签；暂不依赖公开轨迹作初始训练集，但采集本身需另行授权。
- **C（Planning 推荐）**：公开轨迹用于理解状态、初始化可学特征或已执行动作的有限监督；未来再用同状态受控轨迹补足比较标签并精调路由器；训练/验证/测试按任务、仓库隔离。旧 CCH/Blog 仅做调用统计先验，不伪造反事实标签。

**2026-10-09 阶段性答复**：负责人提出“从 A 开始”，表示先用公开轨迹研究模型如何学习；完整 B/C 后续是否使用尚未作出排他性选择。

**负责人 2026-10-09 本轮原话**：“第七个问题需要你仔细查询并给出对应的规划……最后决策用的变量有多个，需要都覆盖到；从 A 开始，模型学习阶段你推荐怎么做。”

**已明确范围**：第一学习阶段按 A，**以公开 Agent 轨迹起步**。这只决定起步顺序，**没有**批准“后续只用公开轨迹、不自采轨迹”，因此 Q-007 全阶段数据路线仍待最终确定。也没有批准数据下载、模型训练或服务器/GPU/API 操作。

#### 只读公开数据证据（正式训练前需再次固定版本及许可）

| 数据资源 | 已核实内容 | 第一阶段用途/限制 |
|---|---|---|
| [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | 官方卡片记录 207,489 条轨迹（某版本）；任务/仓库/Agent scaffold、消息/工具与 resolved，CC BY 4.0 且说明可用于训练 | **首选**，学习真实前缀与已执行动作结果；缺完整 Model×Effort 反事实、物理 KV/缓存计费 |
| [CMU Agent Trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 8,653 条、5 个源模型、6 类任务，含完整轨迹、reward、部分 token/timing | 可补充多领域；需逐项核验使用许可；同任务从头重跑 ≠ 相同中间状态分支 |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | 2,438 个真实仓库任务和可执行环境 | 更适合作未来数据采集环境，任务集合本身不构成路由监督 |
| [AgentSuite trajectories](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 多模型/同任务数据，含一些 thinking on/off 配置 | 可分析 effort 类差异；训练许可待核，thinking 配置并不等于任意 provider 的 effort |
| [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | 6,204 条模型×Harness 评分轨迹，含 token/cache/cost | **仅分析，不能训练**；发布者明确禁止训练、微调、蒸馏 |

#### 覆盖最终路由决策所需的八组状态

| 状态组（RESEARCH_OVERVIEW §2） | 公开轨迹是否可支持 | 阶段 A 的诚实用法 |
|---|---|---|
| 1. Task/Subtask | 任务、repo、语言与已发生步骤通常有；子任务图不一定有 | 任务类型/阶段、已观测进度；缺失子任务信息保留 unknown |
| 2. Agent/Coordination | scaffold/执行 agent 通常有；多子 Agent 关系未必有 | 角色/协作轮次/handoff 字段保留；无证据不虚构多 Agent |
| 3. Context/Memory | 有历史消息和近似上下文长度；token/压缩未必可靠 | 实际上报值与估算值分离，缺失掩码 |
| 4. Tool/Environment | 工具调用、返回与已发生错误较充分 | 只使用当前时间以前的工具调用和环境反馈 |
| 5. Verification/Recovery | 有已发生的测试/失败/重试迹象 | 历史测试结果入 state；最终 evaluator/标准补丁仅作为监督或审计，不进输入 |
| 6. KV Cache/Continuity | 物理 cache read/write、TTL、sticky 通常缺失 | 保留字段及 missing 标志；不能用文本重合冒充物理缓存命中 |
| 7. Temporal/Execution | step/turn 与部分时长可见；预算通常不全 | 使用已发生耗时/调用数，不使用未来总耗时/总 token |
| 8. Provider/Availability | 已用模型可见，真实候选能力/effort/价格表不全 | 单独保留动态动作注册表，未知标 unknown，不伪造候选 |

**还需贯穿所有训练样本的两层**：① Action/Constraints（model、provider、revision、真实 effort、候选合法性、上下文、价格、缓存/切换约束）；② Outcome/Provenance（已执行动作、最终 resolved、可用时真实 cost-to-go、数据/模型版本、task/repo、observed_at、许可与缺失标记）。八组状态全部进入设计不代表八组都有可学习的真实监督。

#### 建议的阶段 A 学习目标与后续顺序（后续尚未获批准）

1. **A0 数据/Schema 审查**：优先公开数据许可、轨迹完整度、决策前前缀提取、八组状态覆盖率和 missingness；不得下载或训练。
2. **A1 真实 Agent 前缀 → 已执行动作的结果预测**：把未来终局 resolved 作为 label，仅将其对应时刻之前的状态及当时实际采取的动作作为输入；Kev 可以用 noul 学是否最终 resolved。对 resolved=-1 或不可信结局不生成硬标签。同一任务的全部轨迹与前缀须在相同 train/val/test 侧，避免重叠和未来信息泄漏。
3. **A1 成本目标有条件开启**：只有轨迹存在同一账本范围内真实 usage、时间与价格，才可学习观察到的剩余 token/费用区间（可用有序 score）；缺失时不制造 USD 标签。这里仅学习行为策略下结果，不推出其他动作的效果。
4. **A2 能力/预算/缓存规则辅助**：后续可用具有确定真值的能力表、费用计算和明确缓存/连续性规则产生 typed choice/noul/score 的辅助训练样本，以覆盖公开轨迹薄弱状态；这是规则监督，不是伪造真实模型成功率或缓存效果。
5. **B 真实动作比较（未来）**：只有相同恢复状态下多个真实合法 (model, effort) 的可比终局与成本，才能训练有依据的候选胜者 choice/pointer；单条行为轨迹的其他候选结果保持 unknown。
6. **C 路由校准（未来）**：在成功率约束下取舍，独立校准集选阈值和温度，保留硬约束优先；校准后的概率不可宣称自动是另一模型反事实成功率。

**Kev 官方依据**：项目 https://github.com/jaredpalmer/kev 的训练说明提供已训练 Kev-4B 权重的 init_from + LoRA/pointer continuation，并支持 choice/noul/score 的有监督样本；是否采用官方 checkpoint 为唯一训练起点属于尚待回答的 Q-010。这里只提供学习阶段推荐，不批准 GPU、权重下载、实验规模、种子、训练超参或新实现链。



#### Q-007-R1｜开源训练数据来源与处理方案（2026-10-09）

**本轮只处于第一大阶段：训练数据来源与加工契约研究。** 用户要求覆盖两类监督数据（运行轨迹、不同任务的模型选择）、全部八组状态、缓存、供应商规则、数据量；尚未批准下载/清洗/训练，以下均为 Planning 方案，不是已产出的训练集。

| 来源 | 可提供的证据 | 许可/限制 |
|---|---|---|
| [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | v1.0 约 207k 软件 Agent 轨迹，v1.1/v1.2 已扩容；任务/工具/消息/resolved；轨迹主源 | CC BY 4.0，固定实际 revision，-1 结局不作成功标签；没有同状态未选动作反事实 |
| [SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories) | 5017 条公开训练轨迹子集；其它 SWE-smith 任务与轨迹不能混作该子集 | MIT 数据卡，核对生成模型输出的训练用途 |
| [LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | 33 models/21+ datasets/400k+ benchmark 记录；同题模型输出、性能、Token、费用 | **数据许可证未核实，暂不纳入训练**；大多请求级，并非长程 Agent |
| [RouterBench](https://huggingface.co/datasets/withmartian/routerbench) | 30k+ Prompts、11 模型的回答/质量/估算成本 | **数据集许可标签不明，暂不纳入训练**；请求级比较 |
| [TwinRouterBench Static](https://huggingface.co/datasets/Amorph/TwinRouterBench) | 970 个 Agent 前缀 → 四级 tier，Apache-2.0 | tier 不是具体 model×effort；防正式对照集泄漏 |
| [Arena Human Preference 55k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | 同题两模型偏好，Apache-2.0，参考 RouteLLM | 人类偏好不是终局软件任务成功 |
| [CMU agent_trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 8653 个多领域/多模型轨迹 | gated 且训练许可待核 |
| [AgentSuite](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 30 模型 × 273 任务、thinking 配置和评估结果 | 许可待核；thinking 开关不等于通用 effort |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) / [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | 真实代码修复任务及可执行环境 | 任务不是天然的已标注模型选择轨迹 |
| [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | model×harness 数据及成本 | **发布条款明确禁止训练、微调和蒸馏** |

**相关训练思路**：RouteLLM 从同题双模型 human preference 训练模型胜负；RouterBench 和 LLMRouterBench 提供按任务的多模型真实得分/成本来拟合静态模型路由；Kev 官方基础决策训练集约 12,576 个 typed 选择/规则样本，后续分阶段添加真实文档及开发工具标签并校准。以上来源均不能从单条 Agent 历史轨迹凭空推断未选 model×effort 的结局。

**加工合同 / 顺序**：

1. Source manifest：repo/dataset revision、license、训练用途权、任务和原始数据 hash；未知许可进入 quarantine，商业 API 输出的模型训练权限需单独核对。
2. Task/Episode：task/repo、harness、模型版本、实际 effort、工具、时序、可信 resolved；-1 不作为成败监督。**先按 task/repo/近重复任务去重并冻结 train/validation/test，再抽轨迹前缀**。
3. DecisionPrefix：在每个真实模型调用前截断，保留 Research 八组状态及 observed_at、provenance、measured/estimated/missing；标准修复补丁、最终测试、未来 token/调用/失败不得进入输入；同任务前缀采样加权防伪独立。
4. Actions：provider/model/revision/effort requested/effective、候选合法性、上下文、工具、价格和缓存/会话条件；缺失为 unknown，不伪造多 Agent handoff、effort、缓存。
5. Outcome：严格区分 observed task resolved、真实计费时的 observed cost-to-go、同静态 Prompt 的 model score/preference、由能力表确定的合法性标签。未执行候选 outcome 始终 missing；API status != task resolved。
6. Kev train JSONL：noul（实际观察的成败或规则真值）、score（有可信计量的有序成本类别）、choice（真实可比较的动作或确定性规则）；保留 task/source/split/label provenance 和 option permutation；无真实反事实时不能标注最优中途 model×effort。
7. 训练数据 ready 门禁：许可证完整、去重分割无泄漏、字段/八组状态覆盖率与缺失率、真实成功标签可用率、effort 与模型组合覆盖、缓存观测覆盖、USD/quotaUnits 保真、JSONL 可验证和 checksum。

**Cache 与厂商政策**：公开轨迹通常只有 estimated prefix overlap，而非实际 physical cache read/write。CCH/Blog 是成本先验不能作同状态缓存效果监督；未来实际 Provider usage/vLLM metrics 才能给缓存真标签。官方缓存差异见 [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching)、[Claude](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)、[Gemini](https://ai.google.dev/gemini-api/docs/caching)、[DeepSeek](https://api-docs.deepseek.com/api/create-chat-completion/)、[vLLM](https://docs.vllm.ai/en/latest/usage/metrics/)。effort 支持、缓存 TTL、计价、限流、工具、隐私/ToS 等**不能只训练进 Kev 权重**，应由版本化 Registry+硬约束执行，样本只用于学习稳定的状态与动作效果。Google [Gemini API Terms](https://ai.google.dev/gemini-api/terms/) 对竞争模型训练有条款限制，不能默认商业 API 输出可用于训练。

**样本量**：Kev 官方基础约 12,576 个决策样本，RouteLLM 采用万级偏好，说明不必无差别全量喂 20 万轨迹。但对任务级路由并无证明足够的固定 N。可先**规划**审计约 1k–3k 独立任务、数千～数万条有真实结局的代表性前缀及合法静态模型比较，按 task/repo/model/effort 独立覆盖、学习曲线和标签质量决定扩张；缺乏同状态多动作真值时增加 prefix 数不能补救。

**大阶段（仅讨论结构）**：D-PREP 当前来源/许可证/Schema → D-BUILD 经批准实际加工数据 → M-INIT Kev 对观察到的动作结果学习 → M-CHOICE 只有真可比结果时学选择 → M-CAL 可靠性校准 → EVAL 最后讨论实验。仍遵守既有 E-DESIGN/E1–E5 和所有权限，不创建第二条执行链。


#### Q-007-R2：数据候选全集 V1（缓存、记忆、多 Agent、时间与 Provider；2026-10-09）

**负责人本轮明确范围**：先把可取得的数据集、相关科研工作及主要国内外厂商官方政策尽量搜齐；**先不决定数据量、不做数据清洗，也不新建 Agent 执行框架**。本节只扩充已有 Q-007 的数据候选目录，**尚未完成训练许可证/原始字段的最终审计，也没有下载样本**。

##### A. KV 缓存、真实调用和时间成本

| 候选编号 | 源及关键数据 | 研究用途/不能宣称的内容 |
|---|---|---|
| CACHE-01 | [Mooncake FAST25 traces](https://github.com/kvcache-ai/Mooncake/blob/main/FAST25-release/README.md)：真实 conversation 12,031 条、toolagent 23,608 条；另有 synthetic 3,993 条。匿名 timestamp、input_length、output_length、512-token 前缀 hash_ids | **P0 首选**：真实调用里的前缀块可复用机会 + 真实到达时间；**没有实际生产 cache_read_tokens、cache_hit 标签** |
| CACHE-02 | [Mooncake 旧版 arxiv trace](https://github.com/kvcache-ai/Mooncake/tree/main/arxiv-trace) | 旧版本比较；可能与 FAST25 重叠，不能当独立新样本数 |
| CACHE-03 | [Mooncake KV cache simulator](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html) | 用真实块 hash 重放，可模拟不同容量/淘汰条件下的缓存读取与 hit rate；**模拟数据不是生产实际命中** |
| CACHE-04 | [KV Cache Workload Bench](https://github.com/hokiyoung/kv-cache-workload-bench) | ShareGPT 派生多轮/并发/增长/驱逐的合成 workload；无 Provider 真实账单 |
| TIME-01 | [BurstGPT](https://github.com/HPMLL/BurstGPT) | 数百万条真实请求、session ID、耗时与 Token，研究服务压力、会话增长、延迟预算；无原始 Agent task-resolved |
| TIME-02 | [Alibaba xMaaS 2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas) | 真实 LLM MaaS 服务集群的资源/模型实例/显存/时间负载，**多数为实例级，不是每次 prompt 或 KV hit** |
| TIME-03 | [Alibaba GenTD26](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) | 包括图像生成等的队列/QPS/延迟/资源工作负载；仅系统时间行为补充，不当成 LLM 任务路由标签 |
| TIME-04 | 既有 Open-SWE-Traces、SWE-smith 与 Mooncake toolagent | Agent 已发生阶段、时间和 Token 等作为时间状态；同一原始数据只登记一次，剩余预算必须有原任务预算减真实已耗才可靠 |

**缓存标签定义（非可互换）**：provider/vLLM 报告的 read/write/hit token 才是 measured；Mooncake 共享 hash 仅为真实请求可复用 prefix potential；配置缓存 TTL/容量/路由后推演的是 simulated hit；文本最长公共前缀只是 estimated overlap。**不可将 hash 匹配、模拟命中训练成商业 API 真实物理命中标签。** 跨模型、跨实例、跨账户/租户共享 KV 的技术和权限不能假设存在。

##### B. 上下文、记忆、协作与执行状态

| 来源 | 已核实特点 | 训练相关性及限制 |
|---|---|---|
| [LoCoMo](https://github.com/snap-research/locomo) | 10 个超长、多会话对话、时间、会话摘要、QA 证据 | 记忆压缩、跨会话更新、信息保持；不是路由胜者 |
| [LongMemEval](https://github.com/xiaowu0162/longmemeval) | 500 问答，历史会话、时间与证据，多会话更新/冲突 | 记忆特征/检索候选，需防止把官方 test 用作训练 |
| [LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) | 451 问题，数百条 web Agent 轨迹组成长历史，记忆、工作流、环境失误 | **P0 长程 Agent 历史**；是否开放训练用途及实际记录结构另核 |
| [MemoryAgentBench](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) | 增量多轮、检索与记忆更新 | P1，非任务模型选择真值 |
| [MemoryCraft collection](https://huggingface.co/datasets/daven3/MemoryCraft) | 汇编 LoCoMo/LongMemEval/MemoryAgentBench/AMA-bench/Membench | P2 转换参考，沿用各上游许可证、不可重复样本计数 |
| [LongBench](https://github.com/THUDM/LongBench) | 长上下文检索/理解基准 | 上下文压力和能力的可选辅助数据 |
| [MARBLE / MultiAgentBench](https://github.com/ulab-uiuc/MARBLE) | multi-agent 角色、star/chain/tree/graph、共享记忆、milestones | **P0 多 Agent 协作环境/Schema**，开源任务不表示全量动作轨迹已发布 |
| [MASBench](https://github.com/BUPT-GAMMA/MASBench) | 部分可观测的协议、记忆、路由与通信成本 | P1，训练轨迹和许可证待核 |
| [AgentWorld](https://arxiv.org/abs/2609.31590) | 长程多智能体、非对称角色和真实协作依赖 | P1，刚发表的新基准；具体记录与许可证待核 |
| [OpenSquilla](https://github.com/TokenRhythm/opensquilla) | 完整 Harness、ContextBudget、Memory、Router、可选 Ensemble | **软件/论文参考，不是公开训练轨迹数据集**；参考 [路由文档](https://github.com/TokenRhythm/opensquilla/blob/main/docs/features/squilla-router.md) 和 [Memory 文档](https://github.com/TokenRhythm/opensquilla/blob/main/docs/features/memory.md) |

**OpenSquilla 的具体研究含义**：[Harness-Native Agentic Routing](https://arxiv.org/abs/2607.11399) 将 query、Harness state、model decision、execution trace、outcome 与 cost 串成数据飞轮。[ContextBudget 源码](https://github.com/TokenRhythm/opensquilla/blob/main/src/opensquilla/engine/context_budget.py) 管理压缩与上下文预算，[Decision Record 源码](https://github.com/TokenRhythm/opensquilla/blob/main/src/opensquilla/engine/steps/router_decision_record.py) 记录实际选用动作。用户的设想应写成**单一 Agent Harness 在模型请求前组织 Context/Memory、Agent 协作、Tool、时间和预算的 StateSnapshot；外部 Kev Router 只接收状态和动态合法候选，选实际 (model, effort)；Provider Adapter 执行并回传 usage，形成训练账本**。现阶段不要复刻 OpenSquilla，也不允许新建第二条 Agent 主调用链。OpenSquilla 的多模型 proposer→aggregator ensemble 是**复合动作**，不自动等于现有 Q-002 已批准单个 (model, effort) 候选。

##### C. 官方 Provider 规则数据源（国内主要模型、国际闭源与开源托管）

| Provider 或模型/部署族 | 官方证据 | 本轮认定与后续字段 |
|---|---|---|
| OpenAI / GPT、Codex | https://developers.openai.com/api/docs/guides/prompt-caching | 缓存 input read/write、TTL、写入收费随新旧模型不同；按 API/型号/地区/组织保存 |
| Anthropic / Claude | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | cache_read_input_tokens、cache_creation_input_tokens、5m/1h、breakpoint；effort/tool 前缀约束要验证 |
| Google / Gemini | https://ai.google.dev/gemini-api/docs/caching | 隐式和显式缓存、TTL/存储价格；thinking 按实际型号 |
| xAI / Grok | https://docs.x.ai/developers/advanced-api-usage/prompt-caching | 自动前缀缓存、cached_tokens 和会话 ID 粘性 |
| OpenRouter（聚合） | https://openrouter.ai/docs/guides/best-practices/prompt-caching | provider sticky/session_id、真实承载 endpoint；同模型跨实际供应商不必有共同缓存 |
| DeepSeek 原厂 API / 自托管开源 | https://api-docs.deepseek.com/zh-cn/guides/kv_cache/ | hit_tokens/miss_tokens、尽力命中；**开源权重不继承 API 的缓存定价** |
| 阿里百炼：Qwen、托管 GLM/DeepSeek/MiniMax | https://help.aliyun.com/zh/model-studio/context-cache | 隐式/显式、模型/地域/版本相关 TTL、折扣和 cached_tokens |
| 火山方舟 / 豆包 | https://docs.volcengine.com/docs/ark/context-cache?lang=zh | 隐式/显式/Session cache，thinking/tools 的连续性和字段 |
| Kimi / Moonshot | https://www.kimi.com/academy/best-practices-for-context-caching | 5m/1h、cache read/write，随 Chat/Responses/Messages API 字段变化 |
| 腾讯 Hunyuan / TokenHub | https://cloud.tencent.com/document/product/1729/101838 | 旧 API 的 CachedTokens；业务迁移到 TokenHub，现行端点/型号单独核 |
| 百度 Qianfan / ERNIE | https://ai.baidu.com/ai-doc/WENXINWORKSHOP/Rm6uq7jy9 | 官方证实部分型号 cached_tokens，**不是全系列自动同能力** |
| 智谱原厂 GLM / Z.ai | https://docs.bigmodel.cn/ | 厂商入口确认，cache/effort/价目具体型号与字段本轮**未核**；不能套用百炼托管 GLM |
| MiniMax 原厂 | https://platform.minimaxi.com/ | 厂商入口确认；原厂 cache/read/effort 逐型号**待核** |
| 阶跃星辰 StepFun | https://platform.stepfun.com/ | 厂商入口确认；具体模型参数与缓存**待核** |
| 硅基流动 SiliconFlow | https://docs.siliconflow.cn/ | 托管服务规则按实际 endpoint，不按模型权重名推断；cache **待核** |
| 国际其它及转售 | https://docs.mistral.ai/ 、https://docs.cohere.com/ 、https://docs.together.ai/ 、https://console.groq.com/docs 、https://docs.fireworks.ai/ | 纳入 provider 候选全集，但 per-model cache/effort/价格本轮**待核** |
| 自托管开源 Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan 等 | https://docs.vllm.ai/en/latest/design/prefix_caching/ 、https://docs.sglang.ai/ | 缓存由真实 inference engine/实例/tokenizer/tenant 隔离决定，不由权重名称决定 |

**Registry 建议字段**：source_url/verified_at/evidence_level、provider/model/deployment/revision/region、open/closed/hosted、supported_context/tools/effort_requested/effort_effective、cache_mode/read/write/TTL/min_prefix、price_version/currency、health/rate_limit、tenant/session_affinity、data_retention/training_output_terms/effective_dates。政策未知记 unknown 而非 false。厂商政策、effort 支持和价格作为动态合法性及计价**外部硬约束**，不通过训练 Kev 权重当作永久真值。缓存和时间类数据只是补充有证据的输入或条件监督。

**阶段关闭边界**：本轮已汇集 candidate source catalog V1，但**没有宣称全部通过许可证审计**，没有指定样本量，没有下载、清洗、生成 Kev JSONL、使用 GPU/服务器/API，亦没有构建 Agent 框架。下一步才按用户另行指示开展逐个数据源许可与字段检查；随后再讨论真实数据加工。

### Q-010｜Kev-4B 训练从哪个基础开始？（已提出待答）

- **A（Planning 推荐）**：以官方版本明确的 Kev-4B 权重为起点，优先研究官方 continuation/LoRA + pointer 选择头适配；先定训练方法，不操作 GPU。
- **B**：从其底层 Qwen3.5-4B-Base 出发初始化 Kev 风格决策头并重新训练；与已确认的“Kev-4B 为起点”有迁移影响，若选择须再论证权重、标签需求与可行性。
- **C**：两种初始化方式均保留为候选研究方向，先做只读证据核查再决定唯一训练起点；不启动双套实现。

**待答**：A/B/C，仅决定训练起点原则；A6000 可用性门槛、权重下载、安装与 LoRA smoke 均留待专门授权。

### Q-011｜首先学习什么监督目标，如何分阶段？（新问题，已提出待答）

- **A**：先只预测已执行动作对应的任务最终成功与观察到的剩余成本（outcome / cost-to-go），待有可比数据再决定是否做动作排序。
- **B（Planning 推荐）**：训练路线分为“已执行动作的 outcome/cost-to-go 监督 → 同状态成对标签训练动作选择/pointer head → 受约束路由校准”三步；各步是否能启动由数据真实性与权限决定，不假定配对数据现成。
- **C**：一开始直接学习模型×effort 最优选择；仅在已具有同状态合法动作可比较标签时才合理，否则不能从单条行为轨迹推导最佳动作。

**待答**：A/B/C。无训练数据不能将未选动作标为失败，也不得把 API 成功视作任务成功。本批不选择训练超参、样本数、seed 或实验统计。

## 9. 决策变更记录

| 日期 | Q-ID | 变更 | 证据 |
|---|---|---|---|
| 2026-10-09 | Q-001 | 首次提出 A/B/C 方案；Planning 推荐 C；用户回答及最终决策待定 | E-DESIGN 启动的历史记录 |
| 2026-10-09 | Q-001 | 负责人批准 A，直接从真实公开 Coding Benchmark 开始，取代原推荐 C | 本轮明确答复 |
| 2026-10-09 | Q-002 | 负责人批准 B，API+本地模型混合候选，具体能力待核验 | 本轮明确答复 |
| 2026-10-09 | Q-003 | 负责人批准 B 原则：本地模型预算不限制、API 按模型限额；金额与使用权限未批 | 本轮明确答复 |
| 2026-10-09 | Q-004～Q-006 | 第二批三个 A/B/C 问题正式提出，均无用户答复 | 当时提案，后有正式答复 |
| 2026-10-09 | Q-004 | 负责人批准 B：成功率约束下优化整任务成本 | 本轮明确答复 |
| 2026-10-09 | Q-005 | 负责人批准 B：分层基线/消融；具体实施暂缓 | 本轮明确答复 |
| 2026-10-09 | Q-006 | 负责人批准 A：同状态受控分支；另记“rq 3 需要 ab 同选”指代待澄清 | 本轮明确答复与补充原话 |
| 2026-10-09 | 研究协作顺序 | 负责人要求先只讨论怎样训练模型、逐阶段推进，不讨论具体实验实施 | 本轮明确要求 |
| 2026-10-09 | Q-007、Q-010、Q-011 | 第三批训练导向三个问题已提出待答；Q-008/Q-009 暂缓 | Planning 提案，不是批准 |
| 2026-10-09 | Q-007 | 负责人指明第一学习阶段从 A 公开轨迹开始；补充公开数据检索、八组状态与学习阶段边界；全阶段数据选择仍开放 | 本轮答复与只读资料核验，未授权执行 |
| 2026-10-09 | Q-007 台账治理 | 负责人要求专门登记数据集来源、Provider/Cache 政策并为后续 AI 筛选清洗留结构；建立 DATA_SOURCE_AND_POLICY_REGISTRY.md 作为唯一详细台账 | 本轮明确文档结构需求；未批准具体源或执行 |
| 2026-10-09 | 论文实验简化执行 | 负责人要求最少可执行代码、单终端实时进度，不要审批门禁、CI/工程测试/复杂防御性编程/哈希与版本冻结 | 最新执行风格，科学数据隔离与真实标签仍需保持；不代表已有训练成果或第三方计算/付费 API 授权 |
| 2026-10-09 | 公开数据清洗位置 | 本机存储不足，选定自有服务器作为 Open-SWE/SWE-smith/Arena/Mooncake 等公开数据下载、CPU 清洗及存储环境；中文目录优先；完整数据不推 GitHub | 用户已委派执行，实测报告未回传，GPU/付费 API 未因此获批 |
| 2026-10-09 | 本机 Codex 论文知识库 | 要求同步 GitHub 五核心文档，用 Paper Research Router 整理 58 篇现有 PDF，Obsidian 中一篇一笔记、双向链接并补充直接相关路由/Jev/Kev 资料 | 明确交付任务；本 ChatGPT 负责 Planning 和需求学术讨论，本机 Codex 执行 |
| 2026-10-09 | 论文引用与模型公开 | 允许将论文创新叙事放在任务级状态、缓存与 model×effort 决策，使用 Kev 已发布权重仍须在 Implementation/Experiments 披露 | 不能将闭源 Jev 训练方案或 Kev LoRA 架构写为原创 |
| 2026-10-09 | Q-007 首批数据科研审查 | Execution 在服务器产出 80,970 混合样本并提供 GitHub 966f582 源码与 50 条预览；Planning 核对到 Arena 真实 winner 30k，但 Agent effort/complexity、Mooncake dispatch/缓存、成本 tier 大量为规则标签；且 TwinRouterBench 已混进 train/val/test | 已执行数据解析≠真实最优路由监督；禁止以 80,970 直接证明 TRAIN_READY；同一 prepare_router_data.py 修正、TwinRouterBench 留外部评测 |
| 2026-10-09 | Kev 官方格式核对 | 官方数据样本要求 questions.choice.criteria 对象与 choice 字符串标签、score.criteria 等级数组与整数索引标签；现有输出为 options、levels 及字符串 score 标签，且补充 provenance 需确认不影响官方解析 | 在进入微调前最简改造与 validate 即可，不增加工程门禁；训练/评测按 task/repo/group 而非单个 trajectory 隔离 |
| 2026-10-09 | Q-007 重建成果二次科研复审 | Planning 核对 16 个 GitHub 字段统计与唯一清洗程序，核出 **3,963,661 vs 报告 2,282,484** 总量冲突；Open-SWE 6 分片仅部分、SWE-smith 仅 ticks、AgentSuite 8/30 模型；前决策状态混入当前工具动作、模型名错映射、Mooncake 复用计算非有序 prefix 与其它字段问题 | 这是 Planning 源码与公开数据审查，**不是负责人新增批准/否决**；当前不应以 TRAIN_READY 开始正式微调；只修改既有脚本，不再全盘删原始文件 |
| 2026-10-10 | Q-007 第三次科研复审（0b39a7e） | GitHub 16 源字段统计和=6,600,628，与 Execution 报告一致；多项代码修正确认，但 AgentSuite pass_criteria/target_question 可能含评测 rubric、SWE-smith 代码块误判工具动作、Mooncake 只有前缀复用潜力、missing_rate 仅按预览样本、缺真正同状态路由标签与 Train/Val/Test 物理切分、TRA-001 官方仍部分下载 | **Planning 审查意见，非负责人新批准**；保留已下载原始数据，继续原脚本定向科研纠偏；不得宣布 TRAIN_READY 或启动微调 |
| 2026-10-10 | Q-007-FINAL 数据资产冻结与 Kev/Laya 兼容验证 | 完成全部已登记 Source ID 资产盘点与机器可读 `manifest.json`、双遍确定性可复现验证；将 LLMRouterBench 13,072 道同分成本未比/并列题移入分析集，锁定 **84,310 道严格唯一单胜者监督题**（Train 67,428 / Val 8,436 / Test 8,446）与 970 步 Holdout；修复短/标点 Prompt 跨集泄漏（0 重叠）；通过官方 `kev` 与 `laya` 仓库 100% 全量兼容性及 A6000 最小训练/保存恢复 Smoke Test | **Q-007-FINAL 全部 PASS，数据资产正式冻结**；下一阶段为 E1/E2 Kev/Laya 正式训练与离线验证，E3 Coding Benchmark 批量运行尚未启动 |

