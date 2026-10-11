# ModelRouter 组会 PPT：叙事重排、原创路由流程图与论文原图规划（v3：论文原图核查版）

> 2026-10-12｜**只规划，不画图、不裁剪/导出 PDF 图片、不制作 PPT、不训练模型**。v3 在 v2 叙事重排基础上补入本轮核实的原论文 Figure 编号与 PDF 页码。
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

### 2.1 推荐版式：16:9 的“4 个主盒子 + 底部反馈回环”，不是六个盒子挤一排

**图名**：Runtime State-Aware Model × Reasoning-Effort Routing for Long-Horizon Agents（拟议方法）。

**图的核心观点**：**每次模型调用前重新决策，而不是只在任务开始时选一次模型**。图中同时区分“谁执行任务”（生成模型/Agent Harness）与“谁选择模型”（Kev/Laya 路由器）。

**从左到右的四个主盒子**：

1. **Agent Harness / Task at step t**：当前 Coding 任务、Agent 角色、已执行历史和下一次合法 LLM 调用边界；Harness 负责实际任务、工具与测试。
2. **State Snapshot + Feasible Action Filter**：在调用前截取八组状态，形成合法候选集合 `A_t = {(model, effort) | provider/上下文/预算/可用性支持}`。该盒内部上下两层：上层“八组决策前状态”，下层“合法动作过滤”。**过滤并不意味着已实现系统调度**。
3. **Router: Kev-4B OR Laya-421M**：将状态和合法候选编码为 typed choice/score，输出本步选定的 `(model_t, effort_t)`；Kev 与 Laya 是**互为对照的实现**，不是串联的两个模型。图中不要伪造已训练的 Q-value/成功概率。
4. **Selected Generative LLM Call**：调用真实可用的生成模型与其支持的 effort，得到回复、真实 provider usage 和可获得的 cache usage。**Kev/Laya 不负责生成 Agent 的代码/答案**。

**底部回环（从右向左）**：`Tool / Environment → Test / Verifier → Recovery / History Update → State at t+1`；只有存在下一次合法调用时，才回到第 1–2 盒重新路由。**任务结束**则从右侧单独连到 `Episode End: resolved? / total USD / latency`，终局信息**不能逆流成为当前 t 的输入**。

**图顶端一条窄带**（视觉上可分 3 色，但不要堆 8 个大卡）：
- 任务层：Task/Subtask、Agent/Coordination、Context/Memory
- 执行反馈层：Tool/Environment、Verification/Recovery
- 系统层：KV/Continuity、Temporal/Execution、Provider/Availability

History 是这些状态的**表示方式**，不是“第九组”。KV 的 provider-reported cached tokens、估计 prefix overlap 和模拟命中必须在注释中分开；**不得画出默认跨模型物理 KV 迁移**。

**示例动作**只用于视觉解释：`(A, low)`、`(A, high)`、`(B, medium)`，必须标注“示意；最终以 provider 真实能力过滤”。若页面空间不足，把离线训练虚线分支完全移至第 10 页，不与在线闭环混画。

**建议讲图的顺序（约 45–60 秒）**：① Agent 到达调用边界；② 读当前八组状态；③ 过滤不合法 model×effort；④ Kev 或 Laya 选下一调用；⑤ 生成模型执行，工具/测试返回反馈；⑥ 任务终局统一核算成功和总费用。

### 2.2 视觉层级与讲解节奏

- **深色/主色实线**：真实 Agent 在线执行路径；**回环箭头**：下一次调用重新决策；**虚线**：拟议训练/实验，不是已经完成。
- **唯一突出的大盒子**：Router + Feasible Action Filter；旁边直接展示示例候选，如 (Model A, low), (Model A, high), (Model B, medium)，**仅作示意**，必须说明真实合法性取决于 provider。
- **KV 小标注放在 Provider/State 两端**：reported cached tokens ≠ estimated prefix overlap ≠ simulated hit；切换的损失依赖真实服务后端。
- **不出现**未来测试结果进入路由输入、模型间无条件 KV 迁移、无来源的百分比降本、已经完成的实时调度/训练。
- **讲图顺序 20–30 秒**：① 什么时候决策 → ② 看哪些状态 → ③ 过滤什么动作 → ④ 谁做选择 → ⑤ 执行后什么反馈 → ⑥ 终局如何算成功与成本。

### 2.3 为什么这张图应成为主图

它与相关工作的比较轴直接对应：Gateway 的“系统缓存/模型联合控制”、INFRAMIND 的“基础设施 Agent 编排”、MTRouter 的“History”、PROGROUTER 的“Progress”、Route-to-Reason 的“Model×Reasoning”，最终落到**我们的具体研究假设**：这些信息在**真实任务级反馈**下是否能产生可测增量。八组状态只是输入组织方式，不自动等于创新。

## 3. 论文原图：确定 6 篇主选 + 2 篇备选，并标明核实程度

> **先去重最初已用的四篇**：用户明确表示已有四篇论文的图片在先前 PPT 中使用。仓库的 19 篇证据表**不能证明**“前四条就是已用四篇”。本地 Agent 需检查已有 PPT/截图目录，列出确切四篇与已用 Figure；下列 6 篇主选**按去重后补位**，不是强制重复使用。优先让每张原图只承担一个论点。

### 3.1 六篇主选：4 篇已亲自从原 PDF 核实图号/物理页

| PPT 页 | 论文 | 指定真实图 | 核实级别与用途 |
|---|---|---|---|
| **03** | [Unified AI Gateway](https://arxiv.org/pdf/2609.06940) | **Fig. 2**：Conventional vs Unified AI Gateway（模型路由与共享 KV 协调对比） | **题名/图号经论文 HTML 文本镜像确认，原 PDF 本轮无法打开**；本地必须核对物理页/版本后截图；证明 KV+模型联合控制已有先例 |
| **03** | [INFRAMIND](https://arxiv.org/pdf/2606.11440) | **Figure 3，PDF 物理第 5 页（索引 p4，印刷第 5 页）**：Planner + Runtime Executor + System Monitor + EDF Scheduler；若放不下可换 **Figure 2，物理第 2 页** 的直观对比 | **原 PDF 图文已核实**；证明系统状态与逐步 model+reasoning strategy 选择已有先例；其 Flash/Concise/DeepThink 是 prompting strategy，非 provider 原生 effort |
| **04** | [MTRouter (ACL 2026)](https://aclanthology.org/2026.acl-long.2045.pdf) | **Figure 2，PDF 物理第 4 页（索引 p3，印刷 44209）**：History Encoder + Model Encoder + Outcome Estimator | **ACL 原 PDF 图文已核实**；证明 history–model joint embedding 已有工作；**如果在已用四篇中则不重复截** |
| **04** | [ProgRouter](https://arxiv.org/pdf/2608.25992) | **Figure 2**：progress-guided routing 的完整 procedure；不要选只说明多 Agent 基本结构的 Figure 1 | **图号/图注见论文文本转载，原 PDF 本轮无法打开**；本地核对物理页和真实图片后再截；证明 progress/ledger/预算已有先例 |
| **05** | [Route-to-Reason](https://arxiv.org/pdf/2505.19435) | **Figure 1，PDF 物理第 2 页（索引 p1，印刷第 2 页）**：Dynamic Reasoning vs Model Routing vs RTR | **原 PDF 图文已核实**；证明 model×reasoning strategy 联合选择不是空白；注意 strategy ≠ 原生 effort |
| **12** | [TwinRouterBench](https://arxiv.org/pdf/2605.18859) | **Figure 1，PDF 物理第 2 页（索引 p1，印刷第 2 页）**：Fast Static Track vs Live Dynamic Track | **原 PDF 图文已核实**；证明真实 Agent 动态运行/费用核算不能由静态标签取代 |

### 3.2 两篇备选与其他只引文工作

| 级别 | 论文 | 图像指令 | 使用条件 |
|---|---|---|---|
| **P1** | [SWE-Router](https://arxiv.org/pdf/2607.00053) | **Figure 1，PDF 物理第 2 页（索引 p1）**：K 步探索→partial trajectory→继续/升级；原 PDF 图文已核实 | 若 MTRouter 或 ProgRouter 与已用四篇重复，优先补到第 04/11 页；特别注意升级到强模型可能从原任务重新开始 |
| **P1** | [EarlyEval](https://arxiv.org/pdf/2609.02783) | 部分轨迹预测终局结果的**真实方法图（图号/页码待 PDF 核实）** | 第 11/12 页需要解释“早期信号”时补；本轮无法打开原 PDF，**不可锁定图号** |
| **P2（引用，不强求图）** | [EvoRoute](https://aclanthology.org/2026.acl-long.1771.pdf)、[TRACE-Router](https://arxiv.org/pdf/2607.22465)、[RouteLLM](https://arxiv.org/pdf/2406.18665)、[FrugalGPT](https://arxiv.org/pdf/2305.05176)、[Mooncake](https://www.usenix.org/conference/fast25/presentation/qin)、[LMCache](https://arxiv.org/abs/2510.09665) | 仅在相关页面用小字引用 | 支撑多轮动态、请求级基线、缓存基础设施，不为增加论文数而截图 |
| **P2（可列近邻，不强求图）** | [Budget-Aware Agentic Routing via Boundary-Guided Training](../../research/task-level-cost-routing/literature/evidence/direct-evidence.md)、[TACIT-Switch](../../research/task-level-cost-routing/literature/evidence/direct-evidence.md) | 查仓库 19 篇直接证据与本地 PDF | 说明历史/预算/升级等方向已有先例，防止夸大创新 |

**选图配额**：第 03 页 2 张、第 04 页 1–2 张、第 05 页 1 张、第 12 页 1 张，总计约 **5–6 张原论文图**。四篇已用论文若重复则**跳过，不再截**；不要为了凑数把八篇全放上去。保留 PDF 版本、图注、来源和出处；PDF 物理页按 **1-based** 标注，避免与 0-based 渲染索引混淆。

**注意两类证据不同**：本轮**原 PDF 已打开并核对**：INFRAMIND、MTRouter、Route-to-Reason、TwinRouterBench、SWE-Router。**只通过文本镜像核实 Figure 编号/内容，原 PDF 未打开**：Unified AI Gateway、ProgRouter。EarlyEval 暂不锁图号。**这些均未导出为素材文件**。

## 4. 交给本地 Codex / Agent 的可复制提示词（只做文献图像核查与裁剪）

> **任务名称：ModelRouter 组会论文原图选取与真实 PDF 裁剪（只做素材，不做 PPT）。**
>
> 仓库：sxyq/modelrouter。请先阅读 our-project/planning/GROUP_MEETING_PPT_OUTLINE.md（v2）、GROUP_MEETING_RESEARCH_BRIEF.md、RESEARCH_OVERVIEW.md、PROJECT_STATUS.md、research/task-level-cost-routing/literature/evidence/direct-evidence.md、research/task-level-cost-routing/literature/index.md。
>
> **第一步，去重**：用户明确说“最初四篇论文已经用过”。检查本地已有 PPT、研究汇报目录、research 下的截图资产、已有图像/引用记录，列出这四篇的**确切论文名、已有 Figure/页码和资产路径**。找不到时写“无法确认”，不得凭猜测把索引前四篇当成“已用四篇”；先完成其余可确定工作，并列出待用户确认项。
>
> **第二步，按本稿第 3 节的主选→备选顺序核查原论文**：先检查本稿已经列出的**原 PDF 已核实的图号与物理页**（INFRAMIND Fig.3 p5；MTRouter Fig.2 p4；Route-to-Reason Fig.1 p2；TwinRouterBench Fig.1 p2；备选 SWE-Router Fig.1 p2），再打开 **Unified AI Gateway Fig.2**、**ProgRouter Fig.2** 的官方 PDF **确认版本和实际物理页**；本轮这两篇只从文本镜像确认图号，绝不可当成已截图或已核实 PDF 页码。优先用仓库已有 PDF，缺失时从官方来源获取。逐篇读正文、图注及前后解释，先输出“论文—Figure 编号/原图题—PDF 物理页（1-based）—PPT 页—一句证据—与已用四篇是否重复”的清单。若图不支持目标论点，明确写“未找到”并替换候选。
>
> **第三步，裁剪**：只裁剪确认过的原始 PDF 图像，优先保留矢量或高清分辨率；不得用文生图重绘后冒充论文原图，不得改动坐标轴、图例、图中文字、数值或图注语义。允许在最终 PPT 中另加解释标注，但原始裁剪图本身保持真实。每张导出 PNG（建议 2×–3× 适合投影）或 SVG/PDF 矢量，并保留原始 PDF 链接。
>
> **第四步，最小交付**：建立一个简单素材目录（优先复用已有 PPT 资产目录，不另建复杂工程），在去重后输出最多 5–6 张高优先级原图；另存一份 Markdown 清单，逐项包含：论文准确标题、官方 URL、PDF 版本、Figure 编号、图注原文或准确简述、PDF 物理页码、印刷页码（如有）、导出文件路径、计划放置的 PPT 页、选择理由、去重结果。另提供每张图的快速预览或联系表供人工选择。
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
