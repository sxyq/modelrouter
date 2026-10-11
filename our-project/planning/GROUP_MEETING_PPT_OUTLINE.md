# ModelRouter 组会 PPT：叙事重排、原创路由流程图与论文原图规划（v2 讨论稿）

> 2026-10-12｜**只规划，不画图、不截 PDF、不制作 PPT、不训练模型**。本稿替换原来“15 页逐项罗列”的结构。
> 研究事实以 [RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md)、[PROJECT_STATUS](PROJECT_STATUS.md)、[研究内容简纲](GROUP_MEETING_RESEARCH_BRIEF.md) 为准。
> **用户补充**：最初四篇论文的图已经使用过。当前仓库文献表尚不能唯一确认是哪四篇、用了哪些 Figure；本稿不擅自认定，要求本地 Agent 先核对已有 PPT/截图资产，**优先补充不重复的新论文图**。

## 0. 这次组会真正要讲的三个问题

1. **为什么换方向**：KV Cache 影响切换成本，但它不能单独决定长程 Agent 的工具失败、恢复、成功概率和任务总费用；Gateway/INFRAMIND 等先例也要求我们不能把“缓存感知路由”说成首创。
2. **我们的方法究竟是什么**：在每个合法模型调用边界，基于八组**决策前**状态，过滤真实可执行的模型×推理档位组合，由 Kev/Laya 类路由决策器选择，Agent 执行后收集工具/验证/真实费用反馈，再进入下一轮；任务结束后按成功率与完整费用评价。
3. **凭什么相信有效**：目前只有数据、训练视图和 CPU 适配，**没有**正式微调或真实 Agent 路由降本结果。后续必须用真实 Harness 的动态对照、状态消融和任务级计费证明。

**表达规则**：少堆名词和论文列表；先用场景与别人的原图说明研究缺口，再用一张我们自己的主流程图解释机制，最后讲数据、可检验实验和导师需要决定的事。

## 1. 重排后的 14 页 PPT（约 18–20 分钟）

| 页 | 标题（尽量用问题句） | 这一页只讲一件事 | 图像安排 | 证据/状态 |
|---:|---|---|---|---|
| 01 | **ModelRouter：为什么一次便宜不等于任务便宜？** | 长程 Coding Agent，目标是在成功率约束下降低整任务成本 | 简洁封面，**不占用论文原图** | 项目目标；不是已证实结论 |
| 02 | **Agent 会反复调用模型：费用在哪里累积？** | 调用、工具、测试、失败重试形成长链；用“便宜但多次失败 vs 较贵但更快完成”的**假设场景**解释动机 | 我们自己的两条轨迹示意，标注“概念示例，非实验数据” | 动机 |
| 03 | **KV Cache 为什么是起点，又为什么不够？** | 原来关注缓存连续性与切换损失；Gateway 已联合模型/缓存，INFRAMIND 已用基础设施状态进行 Agent 编排 | **两篇论文的真实方法图**，保留出处，最多各取一张/一处局部 | 直接先例，P0 |
| 04 | **Agent 路由为什么还需要历史和进度？** | MTRouter 已考虑历史，PROGROUTER 已考虑工作流进度；我们需回答状态增量与任务总费用 | 两篇真实方法图，优先各 1 张；可做左右对照 | 最近邻，P0 |
| 05 | **模型和推理强度能一起选择吗？** | Route-to-Reason 已做 model×reasoning strategy；SWE-Router 说明部分轨迹可触发升级。说明 provider 原生 effort 与论文中的 strategy 不是同义词 | Route-to-Reason **真实框架图**为主；SWE-Router 原图为可选备份 | 已有先例，P0/P1 |
| 06 | **我们的 ModelRouter 每一步怎样工作？** | **整场核心：原创在线闭环路由流程图**，展示调用前状态→合法候选→路由器→模型执行→工具/验证/费用→下一步；终局评价 | **一张占大部分版面的原创流程图**；不使用论文截图 | **拟议方法，尚未实测** |
| 07 | **八组状态到底改变了哪个决策？** | 把八组状态贴回第 06 页流程的“State Snapshot”；分任务/协作、交互/验证、缓存/系统三层，强调决策前可见 | 原创状态分层图或主图局部放大，**不再重新画第二张大流程** | 假设，需要消融 |
| 08 | **谁来做路由决策：Kev 还是 Laya？** | Kev-4B 混合 Qwen3.5 骨干+pointer；Laya-421M ModernBERT+决策头；二者都是 typed decision，非生成 Agent | 官方模型卡/源码事实绘制的对照卡，不伪装成论文 Figure | 已适配，未正式训练 |
| 09 | **数据已经准备到什么程度？** | 14 公开源 6,600,628 异构行；6 个视图，Choice 83,259 / Agent State 88,087 / Effort 290 等，不是 660 万真值 | **真实数据图**：来源分布+视图用途，清楚分开单位 | 已完成清洗/适配 |
| 10 | **第一轮微调能证明什么、不能证明什么？** | Kev/Laya 同许可数据静态冷启动；标签 A/B/C 语义不同；训练许可与 holdout 约束；静态准确率不代表动态收益 | 简洁“合法数据→训练→验证/校准→留出测试”图 | **拟议**；GPU 未启动 |
| 11 | **Agent History 该给路由器什么？** | 最近 K 步、结构化事件摘要、混合方案；首轮建议结构化，但未定 | 3 种输入示意卡；可旁注 MTRouter 原图对应位置 | **待导师讨论** |
| 12 | **怎样用真实 Agent 验证？** | 一个现有 Coding Harness、任务级完整执行、每次决策日志、真实费用/缓存与终局；TwinRouterBench 是动态评测依据 | **TwinRouterBench 原论文静态/动态评测图** + 我们自己的极简实验流程 | **拟议**，非已运行 |
| 13 | **五个 RQ 与必要消融** | RQ1 状态增量；RQ2 Model×Effort；RQ3 任务级目标；RQ4 KV/History；RQ5 Kev/Laya 开销。比较 fixed/task-only/cache-only/model-only/full | 一张 RQ×对照矩阵；主指标 Success、Total Cost、Total Spend/#Resolved、Pareto | 待证伪 |
| 14 | **目前完成什么，还需要导师决定什么？** | 已完成数据/CPU 适配；未完成 GPU 微调、History、真实动态实验；讨论状态、History、模型、Harness/预算 | 进度两栏+四个具体问题 | 当前事实 |

**顺序重点**：03–05 是“别人已经做过什么”，06 是“我们怎么做”，07–11 是“输入、模型、数据”，12–14 是“怎么验证”。不要把全部相关论文挤在最后一页才出现。

## 2. 第 06 页原创主流程图：先确定画法，不实际绘制

### 2.1 建议版式：横向三段 + 一条执行反馈回环

**图名**：Runtime State-Aware Model × Reasoning-Effort Routing for Long-Horizon Agents（拟议）。

**主体从左到右 6 个盒子**：

1. **Task + Agent Harness**：Coding task / 当前 Agent 角色 / 已有执行历史；不是模型路由器本身。
2. **Pre-decision State Snapshot at step t**：八组状态的摘要，严格只含本次模型调用前可获得的信息。旁边小字区分 observed / estimated / unavailable。
3. **Feasible Action Filter**：列出真正合法的 (model, reasoning_effort)；过滤 provider 支持、上下文上限、预算/可用性；缓存兼容/会话连续性只作约束或成本信号，**不假定跨模型 KV 物理互通**。
4. **Router (Kev-4B or Laya-421M)**：输入 state 与合法候选，输出本步所选 (model, effort)；两者是**候选实现/比较对象**，不是同时串联运行。可在框下写目标“task success constraint + episode total cost”，但不能画成已训练出的精确价值函数。
5. **Provider Model Call**：执行被选中的生成模型及其真实支持的 effort；显示调用返回、provider usage、reported cached tokens（如提供）。
6. **Agent Continues: Tool / Test / Verifier**：工具输出、测试失败/通过、重试、下一步上下文；向左/上回到下一次合法决策边界，标记 **t → t+1**。

**图底部**：单独的 **Episode End → Task Success + Total Spend + Latency** 结果盒。来自真实终局与账单；不是当前 t 的输入。失败任务的费用仍计入 Total Spend/#Resolved。

**图上方一条细带**：把八组状态分成三类，避免在主图中塞 8 张大卡：
- Task/Coordination/Context
- Tool/Verification/History
- KV/Temporal/Provider

注意“History”是跨组的输入表达形式，**不是第九组状态**；第 07/11 页单独解释。

**图左下角一条虚线离线支路（可选）**：许可范围内历史数据 → Stage 1 静态训练 → Kev/Laya 路由器权重。**虚线标记 planned/offline**，不得把未来任务成功或未来 usage 反向接入当前在线 State Snapshot。若画面拥挤，整条离线支路删除，放到第 10 页。

### 2.2 视觉层级与讲解节奏

- **深色/主色实线**：真实 Agent 在线执行路径；**回环箭头**：下一次调用重新决策；**虚线**：拟议训练/实验，不是已经完成。
- **唯一突出的大盒子**：Router + Feasible Action Filter；旁边直接展示示例候选，如 (Model A, low), (Model A, high), (Model B, medium)，**仅作示意**，必须说明真实合法性取决于 provider。
- **KV 小标注放在 Provider/State 两端**：reported cached tokens ≠ estimated prefix overlap ≠ simulated hit；切换的损失依赖真实服务后端。
- **不出现**未来测试结果进入路由输入、模型间无条件 KV 迁移、无来源的百分比降本、已经完成的实时调度/训练。
- **讲图顺序 20–30 秒**：① 什么时候决策 → ② 看哪些状态 → ③ 过滤什么动作 → ④ 谁做选择 → ⑤ 执行后什么反馈 → ⑥ 终局如何算成功与成本。

### 2.3 为什么这张图应成为主图

它与相关工作的比较轴直接对应：Gateway 的“系统缓存/模型联合控制”、INFRAMIND 的“基础设施 Agent 编排”、MTRouter 的“History”、PROGROUTER 的“Progress”、Route-to-Reason 的“Model×Reasoning”，最终落到**我们的具体研究假设**：这些信息在**真实任务级反馈**下是否能产生可测增量。八组状态只是输入组织方式，不自动等于创新。

## 3. 论文原图：先选论文，再由本地 Agent 核对 Figure 号/页码

> **先做已用四篇去重**。下表是“新增原图候选池”，不是已截好的图片，也**没有**擅自填写 Figure 编号。PDF 真实图题、编号、页码由本地 Agent 在原始 PDF 中核对后再定。

| 优先级 | 论文与可靠 PDF | 指定找的**真实图类型**（每篇优先 1 张） | 放在哪页、想证明什么 |
|---|---|---|---|
| **P0** | [Unified AI Gateway](https://arxiv.org/pdf/2609.06940) | **Global Control Plane / Joint Model Routing + KV Management 的总架构/决策流程图**；若有多个，优先含 model / placement / KV action 的图 | 03：缓存与模型联合控制已存在 |
| **P0** | [INFRAMIND](https://arxiv.org/pdf/2606.11440) | **Infrastructure-aware multi-Agent orchestration 的系统/方法框架图**；应能看到基础设施状态输入和模型/推理选择 | 03：Agent 基础设施感知路由已有先例 |
| **P0** | [MTRouter](https://aclanthology.org/2026.acl-long.2045.pdf) | **History–Model Joint Embeddings / multi-turn router 的方法图**，要能识别历史如何进入决策 | 04/11：History 不是空白领域 |
| **P0** | [PROGROUTER](https://arxiv.org/pdf/2608.25992) | **Progress-guided online orchestration / workflow ledger 的框架图** | 04：Agent 进度状态已有人研究 |
| **P0** | [Route-to-Reason](https://arxiv.org/pdf/2505.19435) | **模型×推理策略联合路由的方法总图**，不要把 token budget / reasoning strategy 标成 provider 原生 effort | 05：联合选择已有先例 |
| **P0** | [TwinRouterBench](https://arxiv.org/pdf/2605.18859) | **Static vs Live Dynamic evaluation 的双轨框架/评测流程图** | 12：静态准确率不能代替动态执行 |
| P1 | [SWE-Router](https://arxiv.org/pdf/2607.00053) | **K 步 exploration → partial trajectory → continue/escalate 的方法图** | 05/11：中途反馈与升级 |
| P1 | [EarlyEval](https://arxiv.org/pdf/2609.02783) | **部分轨迹预测任务结果/提前评测的流程图**（先验证该 PDF 的正确题名） | 11/12：验证/历史的辅助证据 |
| P2（只引文） | [EvoRoute](https://aclanthology.org/2026.acl-long.1771.pdf)、[TRACE-Router](https://arxiv.org/pdf/2607.22465)、[RouteLLM](https://arxiv.org/pdf/2406.18665)、[FrugalGPT](https://arxiv.org/pdf/2305.05176)、[Mooncake](https://www.usenix.org/conference/fast25/presentation/qin) | 不优先截图；必要时核实论文里真正与该页论点相符的图 | 作为口头或页脚相关工作，不增加版面拥挤 |

**选图配额**：P0 共 6 篇，目标 5–6 张原图；若最初四篇已包含某篇，**不重复截图**，从 P1 补充或只保留引用。不是 6 篇每篇必须占一页；原图过密时第 03/04/05/12 页各保留最有解释力的 1–2 张。真实图优先于摘要页截图、标题截图和无关性能柱状图。

**已知原始论文索引**：[19 篇直接证据](../../research/task-level-cost-routing/literature/evidence/direct-evidence.md)、[58 篇 PDF 索引](../../research/task-level-cost-routing/literature/index.md)、[相关论文表](../literature/related-papers.md)。**MTRouter/EvoRoute 使用 ACL 官方 PDF，不使用之前未核实的 arXiv ID。**

## 4. 交给本地 Codex / Agent 的可复制提示词（只做文献图像核查与裁剪）

> **任务名称：ModelRouter 组会论文原图选取与真实 PDF 裁剪（只做素材，不做 PPT）。**
>
> 仓库：sxyq/modelrouter。请先阅读 our-project/planning/GROUP_MEETING_PPT_OUTLINE.md（v2）、GROUP_MEETING_RESEARCH_BRIEF.md、RESEARCH_OVERVIEW.md、PROJECT_STATUS.md、research/task-level-cost-routing/literature/evidence/direct-evidence.md、research/task-level-cost-routing/literature/index.md。
>
> **第一步，去重**：用户明确说“最初四篇论文已经用过”。检查本地已有 PPT、研究汇报目录、research 下的截图资产、已有图像/引用记录，列出这四篇的**确切论文名、已有 Figure/页码和资产路径**。找不到时写“无法确认”，不得凭猜测把索引前四篇当成“已用四篇”；先完成其余可确定工作，并列出待用户确认项。
>
> **第二步，按本稿第 3 节的 P0→P1 优先级核查原论文**：优先使用仓库已保存的完整 PDF；缺失时只从论文作者/会议/arXiv 官方地址下载。逐篇读 PDF 正文、图注及前后解释，选能直接支持该页论点的**原始真实 Figure**，不要仅凭论文标题或检索缩略图选图。先输出“论文—候选图题/编号—PDF 实际页码—目标 PPT 页—一句证据—是否与已用四篇重复”的清单。若原论文没有符合所述图类型，明确记“未找到”，换候选而不是编造 Figure。
>
> **第三步，裁剪**：只裁剪确认过的原始 PDF 图像，优先保留矢量或高清分辨率；不得用文生图重绘后冒充论文原图，不得改动坐标轴、图例、图中文字、数值或图注语义。允许在最终 PPT 中另加解释标注，但原始裁剪图本身保持真实。每张导出 PNG（建议 2×–3× 适合投影）或 SVG/PDF 矢量，并保留原始 PDF 链接。
>
> **第四步，最小交付**：建立一个简单素材目录（优先复用已有 PPT 资产目录，不另建复杂工程），输出 5–6 张高优先级原图；另存一份 Markdown 清单，逐项包含：论文准确标题、官方 URL、PDF 版本、Figure 编号、图注原文或准确简述、PDF 物理页码、印刷页码（如有）、导出文件路径、计划放置的 PPT 页、选择理由、去重结果。另提供每张图的快速预览或联系表供人工选择。
>
> **第五步，汇报**：列出可用/不适合/重复/无法核实的图。**不要创建 PPT，不要绘制 ModelRouter 主流程图，不要改科研方法/训练数据，不要训练、不调用付费模型。** 主流程图只参考本稿第 2 节的结构，等用户确认后另行绘制。
>
> **严格要求**：任何 Figure 编号、页码和论文图内容都必须来自实际打开的 PDF；图中有“缓存命中”时区分真实 provider 命中与模拟；不把 Route-to-Reason 的 reasoning strategy 偷换为原生 effort；不把 INFRAMIND 的 KV pressure 说成跨模型缓存物理命中。拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。

## 5. 现在先不做的事

- 不制作幻灯片成品；不画第 06 页流程图；不下载/截取论文原图（这些由本地 Agent 在下一步做）。
- 不锁死尚未亲眼核对的 Figure 号、PDF 页码；不认定“已用四篇”的身份。
- 不把计划的 Kev/Laya 训练、真实 Agent Harness、缓存收益、降本曲线写成已完成。
- 本稿仅作为**新的 PPT 内容与素材执行计划**，等本地真实图片清单返回后，再确定每页最终图片和图文比例。

拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。
