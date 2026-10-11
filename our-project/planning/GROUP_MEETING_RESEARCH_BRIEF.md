# ModelRouter 组会研究内容简纲：文献、方法与实验

> 2026-10-11｜讨论稿，非论文结论、非实验报告。
> 研究主线以 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) 和 [PROJECT_STATUS.md](PROJECT_STATUS.md) 为准。
> 整理依据：本轮提供的《面向长程任务的动态大语言模型路由与推理强度联合优化研究报告》、仓库既有 [2026-09-15 深度调研](../literature/report.md)、[相关论文表](../literature/related-papers.md)、[19 篇直接证据](../../research/task-level-cost-routing/literature/evidence/direct-evidence.md)、[Kev/Jev 调研](../literature/jev-model-research.md)。当前可直接读取的新增附件为上述一份；如“第二份新报告”是另一个未随本轮提供的独立文件，仍须补读后更新本稿。
> 标注原则：**已完成**仅指仓库有记录的事实；**拟议**为下一步研究设计；**待证**为假设。2026-09 的 admission-only 报告是历史思路和对照来源，**不是当前运行时动态路由的最终方法**。

## 1. 一句话研究问题与演变

**研究问题**：长程单 Agent / 多 Agent 任务执行期间，在每个合法模型调用边界，怎样根据决策前运行时状态，选择实际支持的 (model, reasoning_effort)，在任务成功率约束下降低**完整任务总成本**？

**演变链条**：早期以 KV Cache 命中和模型切换代价为主要状态 → 发现系统级与基础设施感知路由已有先例 → 单纯最大化缓存复用可能因模型能力不足、工具失败、重试和任务未完成而得不偿失 → 扩展为八组状态，联合考虑认知/执行反馈和系统成本 → 用真实 Agent 动态实测判断扩展是否真正有效。

这里的“创新”不能写成首次使用 KV、首次 Agent step routing 或首次 model×reasoning 联合选择。需要证明的是：**八组状态中的增量信息、合法 Model×Effort 决策、缓存连续性与任务级目标**组合后是否优于近邻基线。变量数量本身不构成贡献。

## 2. 必须单列的两篇先例：它们究竟做到了什么？

| 论文 | 已做到的事 | 不能替它宣称的事 | 对我们的影响 |
| --- | --- | --- | --- |
| [Unified AI Gateway (2026)](https://arxiv.org/abs/2609.06940) | 在请求级联合选择**模型、执行位置、KV Cache 处理动作**；考虑命中、映射、迁移、重前充的代价；八类负载的解析仿真 | 不是实际 Agent 沙箱中逐步验证任务成功与失败恢复的实验；跨模型 KV 映射不等于所有后端已可直接互通 | 仅以“缓存命中影响模型选择”为卖点已经不够 |
| [INFRAMIND (2026)](https://arxiv.org/abs/2606.11440) | 在多 Agent 编排中使用**队列深度、KV-cache pressure/utilization、延迟和预算**等实时系统信号；逐步选模型与推理深度，关注质量、时延与 SLO | 不能等同于显式前缀命中最大化或跨模型 KV 转换；也不以单个 Coding 任务的完整费用/验证恢复为主目标 | “基础设施状态 + Agent 逐步路由 + 推理深度”本身已有近邻，必须正面比较 |

补充背景：[LMCache](https://arxiv.org/abs/2510.09665)、[Mooncake](https://www.usenix.org/conference/fast25/presentation/qin)、[TokenDance](https://arxiv.org/abs/2604.03143) 主要是缓存基础设施/生命周期；它们不应被错误当作与 ModelRouter 完全同粒度的模型选择算法。

**组会核心论证**：KV 状态告诉我们“这一步切换贵不贵”，但不能独立回答“继续用这个模型能否修好当前错误、还会调用多少次、最终是否完成”。因此必须把工具、验证、任务进度、历史、预算与候选可用性纳入**可检验的状态消融**，而非仅增加字段。

## 3. 八组状态：为什么扩展、怎样避免堆特征？

| 状态组 | 预期影响路由的原因 | 决策前候选观测（尚不代表全部已采集） |
| --- | --- | --- |
| Task / Subtask | 不同任务与阶段需要不同能力 | 任务类型、当前子任务、阶段 |
| Agent / Coordination | 角色和交接改变错误传播代价 | 当前角色、handoff、活跃子 Agent |
| Context / Memory | 上下文增长影响能力与成本 | 当前 token 长度、压缩/摘要状态 |
| Tool / Environment | 工具执行反馈揭示当前障碍 | 最近工具类型、返回码、异常 |
| Verification / Recovery | 验证失败与连续重试改变升级收益 | 已发生的测试结果、连续失败数 |
| KV Cache / Continuity | 复用、切换和重前充影响调用成本 | reported cached tokens、估计前缀重合、会话锁 |
| Temporal / Execution | 预算与剩余时间改变最优动作 | 已用步数、累计时延、预算余额 |
| Provider / Availability | 只可选择真正可执行的动作 | model/effort 支持、价格、限流、上下文上限 |

可以用三层组织 PPT：**任务与协作**、**交互/验证/记忆**、**缓存/预算/服务系统**。所有特征必须在模型调用前可观测；物理 KV 命中、provider 回报的缓存 token、最长公共前缀估计、仿真命中率必须区分。不能把终局 resolved、未来调用次数、未来测试结果写进当前输入。八组状态的有效性由 Task-only → Task+Cache → Task+交互反馈 → Full-8 和逐组移除消融证明。

## 4. 两个开源决策模型：Kev 与 Laya

**概念纠正**：Jev-style/System One 指“输入状态和类型化问题，单次前向输出候选概率”的决策接口/范式，**不是与 Transformer 对立的独立骨干架构**，也不同于 Meta JEPA。Kev 和 Laya 都不是生成 Agent 回复的主模型，而是拟用作旁路路由决策器。

| 维度 | [Kev-4B](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md) | [Laya-421M](https://github.com/NandhaKishorM/laya) |
| --- | --- | --- |
| 基座 | Qwen3.5-4B-Base，24 层 Gated DeltaNet + 8 层 full attention 的混合架构 | ModernBERT-large 双向 Transformer 编码器 |
| 决策机制 | LoRA + pointer head，prefill-only 的 typed choice/score | 编码器 + 决策头，typed choice/score，支持 soft-CE / RLCD |
| 量级 | 约 4B | 约 421M |
| 预期角色 | 主研究路由器候选，适合比较复杂状态输入 | 轻量对照，比较延迟、显存与校准 |
| 当前事实 | 已完成数据格式适配、官方 CPU 加载/编码检查 | 同左 |
| 尚未证明 | 任务级动态路由收益、泛化、真实延迟与成本优势 | 同左 |

二者同时存在**参数量、编码方式、训练机制**差异；直接比较不能推导“架构优劣”。第一轮用相同、合法、同语义的训练样本与验证协议比较 accuracy、ECE/Brier、覆盖率、延迟、显存；必要时再补容量匹配的小模型对照。Kev 官方较长 serving 窗口不等于该长度下质量已验证。

## 5. 数据来源、清洗结果与初步微调

### 5.1 已有数据资产（仓库事实）

**14 个公开来源共 6,600,628 条异构记录**，不能理解为同粒度独立任务或 660 万条动态路由标签。

| 用途 | 数据集 | 清洗记录 |
| --- | --- | ---: |
| Agent 轨迹 | Open-SWE-Traces、SWE-smith、AgentSuite | 4,448,643 |
| 静态路由与偏好 | LLMRouterBench、RouterBench、TwinRouterBench、Arena、Finding the Right Fit | 649,207 |
| 缓存与负载 | Mooncake、BurstGPT | 1,443,926 |
| Coding 环境 | SWE-Gym、SWE-rebench-V2 | 34,517 |
| 长期记忆 | LongMemEval-V2、MemoryCraft | 24,335 |

另有自有 CCH 110 行聚合（对应 750,212 次调用）、Blog 221,128 次调用及 79 行衍生统计，**不能混入上述 660 万行，也不能将 quotaUnits 视为 USD**。

**已准备的六个训练视图**：Stage 1 Choice 83,259（train 66,721 / val 8,298 / test 8,240）；Pairwise 59,049；Soft Target 53,087；Stage 2 Agent State 88,087（35,289 个独立任务）；Stage 3 Effort 290 对有效比较；Stage 4 Auxiliary 1,622,547。Kev 和 Laya 各自适配视图合计 1,906,319 行，**不是各有 190 万条有效动态选择真值**。

Stage 1 Choice 的 Regime A/B/C 分别是 **39,716 人类偏好 / 4,039 质量唯一胜者 / 39,504 质量同分后的历史静态费用规则**；Regime C 不是 Agent 最终任务账单。

### 5.2 下一步最小微调（拟议，未授权执行）

1. 先解决训练范围：Arena（ROUTE-004）训练许可已核实；RouterBench、LLMRouterBench（ROUTE-002/001）仍为 LICENSE_PENDING，**未获许可不得纳入正式训练**。
2. 获 GPU 授权后，用同一许可范围的 Stage 1 Choice 做 **Kev 一次、Laya 一次**初步微调；Soft Target 作为后续小规模补充/对照，不把 Stage 2–4 强行合成 Choice 标签。
3. 同任务与同题保持统一 train/val/test；仅用 val 调参与校准，test 留作终评；分数据源与 A/B/C 体制报告指标。
4. 比较分类/排序质量、概率校准、输入截断/跳过率、路由器自身推断成本；Stage 1 仅证明**静态冷启动能力**，不能证明 Agent 动态策略成功。
5. 后续真实受控 Agent 轨迹补齐决策前状态、所选动作、后续结果、provider 原始 usage、真实费用与终局；不能把单条已执行轨迹复制为所有未选择动作的反事实标签。

当前事实：训练参数和 CPU 适配已完成，**正式 GPU 微调、付费 API、Coding Benchmark、动态 Harness 实测均未开始**。最新进度以 [PROJECT_STATUS.md](PROJECT_STATUS.md) 为准。

## 6. Agent History：明确尚未决定

| 候选方案 | 优点 | 主要风险 |
| --- | --- | --- |
| 最近 K 步原始工具/对话窗口 | 保留局部语义和错误细节 | 长文本、截断与推理开销 |
| **结构化事件摘要（首轮建议）** | 记录工具错误、测试状态、重试、进度、预算、切换等，适配双模型；可做消融 | 可能丢失关键代码/语义信息 |
| 结构化摘要 + 最近 1–3 步文本 | 兼顾全局统计与局部细节 | 特征提取与 token 预算更复杂 |

建议先讨论第二种作为 MVP，第三种作为对照，**不是已定方案**。可参考 [MTRouter](https://arxiv.org/abs/2604.23530)、[SWE-Router](https://arxiv.org/abs/2607.00053)、[PROGROUTER](https://arxiv.org/abs/2608.25992)、[EarlyEval](https://arxiv.org/abs/2609.02783)。History 由 Agent Harness 维护并在决策前截断，不应让 Kev/Laya 负责生成整段历史摘要。

## 7. 真实实验：从离线到 Agent 闭环（拟议）

- **E2 离线冷启动**：Kev/Laya 与 rule、logistic/GBDT 基线比较静态 Choice/Soft Target；检查标签语义、校准、截断和候选位置偏差。
- **E3 小规模真实任务试点**：选择**一个**现有 Coding Agent Harness（如 mini-SWE-agent）和一个可执行任务环境（优先 SWE-Gym，后续考虑 SWE-bench Verified / SWE-rebench）；记录调用前状态、model/effort、工具/测试、真实 usage、费用、缓存和终局。先少量任务验证指标可测，不将其称为完整研究结果。
- **E4 动态对照**：在相同任务集合与预算规则下比较 Always-strong、Always-cheap、admission-only、Task-only、Cache-only、Model-only dynamic、Full-state Model×Effort；在关键决策点进行**少量受控同状态分支**，要求恢复环境、历史与执行约束，不能靠静态回放推断未选动作。
- **E5 消融与泛化**：去掉 Verification/Recovery、KV/Continuity、History、Effort、剩余成本目标；报告跨仓库/任务类别、价格敏感性、失败任务费用和路由器开销。并非所有 Provider 都支持同名 effort，动作池必须先过滤合法组合。

**主指标**：Task Success / Resolve Rate、Episode Total Cost、Total Spend / #Resolved、成功率—成本 Pareto；辅以端到端时延、步骤/重试、缓存读取、切换次数、router overhead、ECE/Brier。Total Spend / #Resolved **包括失败任务花费**，不能写成“只统计成功任务的平均费用”。

## 8. 建议的五个 RQ

| RQ | 要回答的问题 | 核心对照 |
| --- | --- | --- |
| **RQ1 状态增量** | 八组状态比 Task-only / Cache-only 是否真的改善成功率—成本？ | Task-only、Task+Cache、Full-8、去 Verification |
| **RQ2 联合动作** | Model×Effort 比仅选 Model 是否扩展 Pareto 前沿？ | 固定 effort、model-only、联合选择 |
| **RQ3 任务级目标** | 考虑失败/重试/剩余费用是否优于单次便宜贪心？ | 单次费用贪心、admission-only、task-aware |
| **RQ4 缓存与 History** | 真实缓存连续性和不同 History 表示各有多少边际价值？ | cache-blind/sticky；结构化/短窗口/混合 |
| **RQ5 决策器与开销** | Kev 与 Laya 的准确率、校准、泛化和路由开销如何权衡？ | 同训练数据、同合法动作、简单分类器 |

每个 RQ 均允许“没有增益”的结论；先完成可观测性和受控对照，再讨论复杂学习目标。旧报告的 ex-ante 预测方案保留为 **admission-only 基线**，不取代当前运行时主方法。

## 9. 相关工作：组会按四条线讲，不按 58 篇逐一讲

1. **请求级成本路由**：[FrugalGPT](https://arxiv.org/abs/2305.05176)、[RouteLLM](https://arxiv.org/abs/2406.18665)、[RouterBench](https://arxiv.org/abs/2403.12031)：为 Stage 1 静态监督与基础基线提供背景。
2. **Agent 多轮、历史与任务级路由**：[MTRouter](https://arxiv.org/abs/2604.23530)、[SWE-Router](https://arxiv.org/abs/2607.00053)、[TRACE-Router](https://arxiv.org/abs/2607.22465)、[PROGROUTER](https://arxiv.org/abs/2608.25992)、[EvoRoute](https://arxiv.org/abs/2604.14840)、[Harness-Native Agentic Routing](https://arxiv.org/abs/2607.11399)、[TwinRouterBench](https://arxiv.org/abs/2605.18859)：是必须正面比较的近邻，尤其不能宣称首次逐步状态路由。
3. **模型×推理策略/计算预算**：[Route-to-Reason](https://arxiv.org/abs/2505.19435)、[BEST-Route](https://proceedings.mlr.press/v267/ding25d.html)、[R2-Router](https://arxiv.org/abs/2602.02823)：已有联合计算分配，但“reasoning strategy / token budget”不必然等同各 Provider 原生 reasoning_effort。
4. **缓存与基础设施**：[Unified AI Gateway](https://arxiv.org/abs/2609.06940)、[INFRAMIND](https://arxiv.org/abs/2606.11440)、[LMCache](https://arxiv.org/abs/2510.09665)、[Mooncake](https://www.usenix.org/conference/fast25/presentation/qin)：用于界定缓存状态与系统侧成本的先例。

正式写论文前回到 PDF 正文核实图号、公式、发表状态与数字。新增报告中的“首次”“25% 降本”“毫秒级必达”和未验证的 BibTeX/图号不应直接写成我们的方法事实。

## 10. 组会希望导师帮助决定的四件事

1. 八组状态是否以 **Task+Cache → Verification/Tool → Full-8** 的分层消融作为主论证？
2. Agent History 首轮是否采用结构化事件摘要，并以最近 K 步窗口作为对照？
3. Kev 主模型、Laya 轻量对照是否先完成**同许可静态冷启动**，再进入真实 Agent 数据采集？
4. 动态实验先选哪一个 Coding Harness、哪组可用 Model×Effort、多少任务与预算？这些仍是**计划，不是执行授权**。

**范围约束**：本轮只新增两份组会 Markdown 讨论稿；不启动训练、下载模型、调用付费 API、构建 Harness 或修改数据主链。拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。
