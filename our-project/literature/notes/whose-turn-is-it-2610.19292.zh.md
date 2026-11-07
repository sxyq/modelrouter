# 《Whose turn is it?》中文技术笔记：缓存切换与 ModelRouter V9 的研究边界

> 整理日期：2026-11-08。**文献笔记与待讨论研究方案，不是已批准的 V9 RQ 改动，不是我方实验结果。** 区分原文作者结论、第三方解读、我们的推断和现有仓库证据。

## 1. 论文、PDF 与中文资料

- 原文：Anikesh Parashar, Avik Dutta, Vashu Chauhan, Sumit Gulwani, Priyanshu Gupta, Hosein Hasanbeig, Vu Le, Ashish Tiwari, Jack Williams, *Whose turn is it? Context-guided model routing for stateful agents*, arXiv:2610.19292v1，2026-10-13。
- **官方原版 PDF（直接打开）：** https://arxiv.org/pdf/2610.19292
- 论文页：https://arxiv.org/abs/2610.19292
- 中文论文摘要/译介：https://www.alphaxiv.org/zh/abs/2610.19292
- 中文技术评述（第三方而非作者原文）：https://www.themoonlight.io/zh/review/whose-turn-is-it-context-guided-model-routing-for-stateful-agents
- 英文正文转录辅助：https://bytez.com/docs/arxiv/2610.19292/paper

**PDF 归档状态：** 此次已登记原版 PDF 的永久来源链接，但未将论文二进制复制入仓库；不得把链接文件冒充已上传的 PDF。原 PDF 如需仓库离线留存，需把 arXiv v1 原件保存为 `our-project/external/research/papers/59_Whose_Turn_Is_It_Context_Guided_Model_Routing_for_Stateful_Agents.pdf`，并保留原始来源及版权信息。本笔记不重制原文或复制大段正文。

## 2. 论文做了什么（原文确认）

**研究单位与算法**：作者定义 *turn* 为一次用户请求及其内部完整的 Agent LLM/工具循环。模型选择发生在**用户轮次开始之前**，该轮内由同一个候选模型负责；并非在每个 LLM 生成节点重新路由。研究的是无需路由标签和微调的 **zero-shot、二候选模型配对** 策略，比较路由器、无历史路由器、cheap→expensive escalation、expensive→cheap de-escalation、随机与固定模型。

**候选差异与评测**：SheetCopilot 和 SpreadsheetBench 2 的多轮表格 Agent。比较同提供方不同型号、不同提供方以及同模型不同 reasoning effort 的模型对；示例包括 GPT-5.6 Sol/Luna、Sol/Claude Haiku 4.5 和 Claude Opus 4.8 high/low。不是异构 K=3/5/7 的单一学习型 Router，不是软件工程 Harbor/Mini-SWE-agent 的真实修复任务。

**历史信息**：使用当前用户输入和会话历史，包括工具观察、错误、工作簿状态与以往决策。作者比较匹配廉价模型卸载比例时，有无历史的路由效果。

**缓存**：切换模型时，前一模型的会话轨迹专属 Prompt Cache 不能自动传给新模型；但新模型自身常驻的 system/tool 公共前缀仍可能命中，因此既不能视为零损失，也不能机械按“全部 Token 必然重算”处理。文中讨论的是 Provider 的 *prompt-cache billing/prefix*，不证明异构模型之间物理 KV 张量共享或转码已实现。

## 3. 论文报告的发现与适用边界

1. 作者报告在 SheetCopilot 相近的 cheap-turn 比例下，history-aware 路由比 current-request-only 路由约 **+3.3 个百分点**任务通过率（28.3% 对 25.0%）；不要推广为所有工作负载都如此。
2. 廉价模型的单次 Token 价差并不等于完整任务费用差。作者在两种不同长度/任务域的表格工作流中观察到 Haiku 相对 Sol 的整任务费用优势从 **6.8× 缩小至 3.2×**；该对比还受工作流差异影响，不能解释为纯粹增加长度的因果效应。
3. 闭式 **cache break-even** 分析：在论文价格、公共前缀常驻、输入缓存定价及执行调用次数的设定下，从贵模型向便宜模型切换的额外缓存输入成本可能在约两次后续调用内收回；反方向在其评估条件下不能仅靠输入缓存价差收回。**这不是一般化的“任何贵→便宜永远两步回本”，也没有考虑真实 Coding Agent 工具失败的全部路径反事实。**
4. 作者也发现候选 pair 极其重要：当便宜模型的真实质量达到或超过昂贵模型时，**始终使用便宜模型**可以优于复杂路由；不能把“动态切换越多越好”当成研究目标。
5. **费用口径注意**：正文讨论了路由开销，附录 Table 3/4 的模型执行 cost 列注明“excluding router call”，且跨提供方 LLM router 价格并非每一行均可精确分摊。与 ModelRouter 的完整 Episode USD 比较须明示口径。
6. 本论文主要是 **zero-shot + user-turn + spreadsheet agent + 二元候选**。作者讨论 learned/per-call 路由的相关性，但这些不是本论文主结果所验证的部署机制。

## 4. 与近邻工作共同界定边界

| 研究 | 已经覆盖 | ModelRouter 不应主张首次提出 |
|---|---|---|
| Whose turn is it? (2610.19292) | 有状态历史、零样本用户轮次级路由、切换方向和 Prompt Cache 回本 | “缓存影响模型切换” |
| Unified AI Gateway (2609.06940) | 请求时联合选择模型/执行位置/KV 处理动作，以解析仿真分析 TTFT 和输入费 | “模型与 KV Cache 联合优化” |
| InfraMind (2606.11440) | Agent step 使用队列、缓存压力和基础设施状态选择模型与推理深度 | “Agent 路由首次结合 Infra 状态” |
| MTRouter (2604.23530) | 逐 turn 历史—候选模型表示与学习型效用估计 | “小型/学习型候选质量路由” |
| JevAgentHarness (2610.21412) | 决策模型参与 Agent Harness、包括模型委派 | “Agent 模型动态委派” |
| HyDRA (2605.17106；EMNLP 2026 industry) | 异构五模型池、能力需求匹配、变更候选目录无需重训编码器，含 SWE-bench 实验 | “池规模 K=5／添加模型／能力卡”本身 | 
| vLLM SAAR (2026-06-02 工程报告) | session memory、工具循环保护、切换边界与 prefix-cache-aware 估价 | “第一次使用缓存感知 Sticky/切换边界”本身 |

进一步最相近证据：[HyDRA 论文](https://aclanthology.org/2026.emnlp-industry.82/)（五模型和目录解耦，但主要是请求路由）与 [vLLM SAAR 技术报告](https://vllm.ai/blog/2026-06-02-session-aware-agentic-routing)（缓存感知切换与 session continuity；工程/系统报告，不直接等于与我们的 Harbor 成功—成本评测）。因此 **“K=5 可扩”“Cache-aware Sticky”也都不是天然新颖性**。特别需要研究 K 扩张与 Agent 实际结果、缓存经济性及训练稀疏性的交互，不能简单把 K 作为创新数字。

已有仓库文献根源：[2026-09-15 任务级事前成本 Brief](../brief.md)（当时明确暂不以 KV Infra 为主线）、[2026-10-11 组会研究简纲](../../planning/GROUP_MEETING_RESEARCH_BRIEF.md)（明确“最初以 KV Cache 与切换成本为动机”）、[模型路由及缓存相关论文表](../related-papers.md)。**不同日期的研究范围发生过演变，不能混为同一已经正式验证的方案。**

## 5. ModelRouter V9 的真实现状与保留资产

以仓库 2026-11-08 状态为准：正式链是 `Harbor → ModelRouterMiniSweAgent → DefaultAgent`；单 Agent 每次合法**生成机会**可调用单活跃 Laya 或 Kev；T/M/H 状态、真实工具/验证历史、Provider 缓存 usage、成本记录、AA 卡、可选轨迹教师和 Model×Native Effort 基础框架已实现/有部分真实执行。训练完成与历史偏好数据是研究资产。

尚未证明：异构 K=3 的稳定模型分工与完整正收益，更不用说 K=5/7；模型切换所造成的**真实缓存因果增量**、训练后的独立任务成功收益、完整资源 USD 和高并发吞吐亦不可臆称。GLM 访问/响应证据不能代替其全部 Effort 的有效 Agent 执行能力。

历史方案一度要求不同 K 与同 K 不同成员，但**2026-11-07 正式 RQ2 已被收窄为固定目标池 K=3**。用户 2026-11-08 重新提出 K=3/5/7，是研究范围**拟修订建议**；在正式决定和实际候选可用性确定前，不把现行文档偷偷改写为已获证实的 K=7 实验。

## 6. 真正值得推进的差异化假设（不是论文已证结论）

**核心：把“切换是否划算”从单次 API 账单延伸到真实软件 Agent 的后续成功率/错误恢复、跨模型持续上下文、原生 Effort 与总 Episode USD。**

- **H1 候选条件质量 × 缓存经济性**：同一时间截止之前的真实前缀下，可靠质量优势与 cache-switch 代价是否会改变最佳 Model×Effort 动作？若没有增量，结论应承认固定/Sticky 足够好。不要捏造未执行候选的成功标签。
- **H2 路由决策粒度**：固定任务开始、真实阶段转折、真实子任务边界、逐次生成，比对任务完整收益、实际 decision 数、路由耗时、缓存读写与切换方向。每次生成是可选边界，不等于每次都必须昂贵重算 Router。
- **H3 模型池规模与组成**：拟恢复 K=3/5/7 的嵌套池和少量同 K 不同成员；K 是不同真实模型身份数，而非 Effort 数；必须有实际 Provider/model/revision、合法 Effort 和费用，不能用 Alias 充当独立模型。
- **H4 不完整与删失监督**：局部工具/测试进展、等质量费用、Provider/Verifier UNKNOWN 分开记录；探索是否有可迁移的动作相对优势，不能将离线偏好视为在线最终成功的充分证明。
- **H5 完整净收益**：固定/Sticky、History-only、Cache-only、Task+Cache、Full T/M/H 与 Jev/MTRouter/Whose 可适配方法，在**同 Harness、同池、同任务集**下比较 Task Success、完整 Episode USD、成本/成功数、端到端时延；包括教师、Router 和重试开销，缺失 VM/USD 保持 UNKNOWN。

这些假设不要求新建 KV 传输/转换服务，不需要重新训练全部历史模型，也不要求把教师触发升级成独立创新。优先复用已有 Provider usage、Agent 前缀、Harbor 原 Verifier、Laya/Kev Checkpoint。

## 7. 拟议五 RQ 如何保留完整研究范围（尚非正式替换）

- RQ1：**整个 Agent 的成功率—成本 Pareto**，与固定、Sticky、公开同类路由比较。
- RQ2：**池规模/成员及 Model×Native Effort**，拟恢复 K=3/5/7；先有实际候选和真实比较，再作图。
- RQ3：**单 Agent 的阶段/真实子任务边界及生成路由频率**，分辨阶段标签和物理拆分，衡量 cache-switch 开销与长期路径变化。
- RQ4：**消融**，优先 Task-only、Task+Cache、Task+History、Full T/M/H、Model-only/Effort-only/Joint、教师开/关与 S1/S2/S3；只做能解释关键因果的少量组合。
- RQ5：**切换有用和无用的工作负载边界**，按先验可观测的上下文长短、任务阶段、恢复难度、候选质量差距和缓存环境分组。

**研究定位备选**：*Cache- and Outcome-Aware Model×Effort Routing for Long-Horizon Software Agents*。不能用“首次 cache-aware”宣传；潜在贡献在受真实任务质量约束的**多模型、多 Effort、Agent 内路由粒度与缓存机会成本**交互，以及有证据的净收益/负收益条件。

## 8. 最有价值的下一批真实结果，而不是新框架

1. 先用已验证的模型身份做同任务的 Fixed / Sticky / 当前 Router 对照，记录每步模型、Effort、是否切换、上次与当前缓存 usage、上下文和最终 Verifier。没有可靠独立结果，不能因 K=7 规划而延迟基本比较。
2. 从已保存的相同决策前缀抽取少量具有明显工具/验证差异的真实候选对照；每个候选必须独立实际执行，不能由单轨迹推断未选动作结果。
3. 按已存在的缓存字段比较留在 A、切到 B、仅切 Effort 的账单和后续执行路径；Provider cached_tokens 是**报告的缓存读取**，不是不同模型共享物理 KV 的证据。
4. 对实际已测策略计算完整成功率/成本（缺失项标 UNKNOWN），据结果决定要不要扩展池、保留教师以及晋升 Laya 或 Kev。原已投入的微调和历史数据全部保留，且与最新 K 池监督定义严格分开。

## 9. 避免两种错误

- **重复已有工作却改名**：仅靠缓存感知、二元强弱分流、每步路由、小决策模型或固定的两步回本公式不能证明新颖性。
- **因为有先例就丢弃真实资产**：V9 有合法模型动作、真实 Coding Agent 工具/验证执行、可训练小 Router、分开记录的缓存与模型费用。这些可以作为独立研究的实验基础；价值需要最终实验确认，而不是通过文字判断“完全撞题”。

> 本笔记仅新增文献事实与可验证的研究假设，不覆盖此前的原数据、权重、五 RQ 正式定义或历史结果。最后要依据真实结果收窄论文贡献，不预设正向结论。
