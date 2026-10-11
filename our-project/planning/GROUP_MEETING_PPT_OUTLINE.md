# ModelRouter 组会 PPT：叙事重排、原创路由流程图与论文原图规划（v4：主图设计与本地截图库任务版）

> 2026-10-12｜**只规划，不画图、不裁剪/导出 PDF 图片、不制作 PPT、不训练模型**。本版重新明确论文选取优先级、主流程图版式、原图取舍和本地 Agent 的最小交付。
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
| 03 | **KV Cache 为什么是起点，又为什么不够？** | 原来关注缓存连续性与切换损失；Gateway 已联合模型/缓存，INFRAMIND 已用基础设施状态进行 Agent 编排 | **Gateway Fig.2 + INFRAMIND Fig.2**：前者解释 KV 联合控制，后者直观展示基础设施感知选择；INFRAMIND Fig.3 留作备用 | 直接先例，P0 |
| 04 | **Agent 路由为什么还需要历史和进度？** | MTRouter 已考虑历史，ProgRouter 已考虑工作流进度；我们需回答状态增量与任务总费用 | **ProgRouter Fig.2** 为新图主选；若最初四篇中已有 MTRouter，直接复用旧素材，不重复裁剪 | 最近邻，P0 |
| 05 | **模型和推理强度能一起选择吗？** | Route-to-Reason 已做 model×reasoning strategy；SWE-Router 说明部分轨迹可触发升级。说明 provider 原生 effort 与论文中的 strategy 不是同义词 | **Route-to-Reason Fig.1** 为主；SWE-Router 如在最初四篇中已用，仅复用，不重复裁剪 | 已有先例，P0/P1 |
| 06 | **我们的 ModelRouter 每一步怎样工作？** | **整场核心：原创在线闭环路由流程图**，展示调用前状态→合法候选→路由器→模型执行→工具/验证/费用→下一步；终局评价 | **一张占大部分版面的原创流程图**；不使用论文截图 | **拟议方法，尚未实测** |
| 07 | **八组状态到底改变了哪个决策？** | 把八组状态贴回第 06 页流程的“State Snapshot”；分任务/协作、交互/验证、缓存/系统三层，强调决策前可见 | 原创状态分层图或主图局部放大，**不再重新画第二张大流程** | 假设，需要消融 |
| 08 | **谁来做路由决策：Kev 还是 Laya？** | Kev-4B 混合 Qwen3.5 骨干+pointer；Laya-421M ModernBERT+决策头；二者都是 typed decision，非生成 Agent | 官方模型卡/源码事实绘制的对照卡，不伪装成论文 Figure | 已适配，未正式训练 |
| 09 | **数据已经准备到什么程度？** | 14 公开源 6,600,628 异构行；6 个视图，Choice 83,259 / Agent State 88,087 / Effort 290 等，不是 660 万真值 | **真实数据图**：来源分布+视图用途，清楚分开单位 | 已完成清洗/适配 |
| 10 | **第一轮微调能证明什么、不能证明什么？** | Kev/Laya 同许可数据静态冷启动；标签 A/B/C 语义不同；训练许可与 holdout 约束；静态准确率不代表动态收益 | 简洁“合法数据→训练→验证/校准→留出测试”图 | **拟议**；GPU 未启动 |
| 11 | **Agent History 该给路由器什么？** | 最近 K 步、结构化事件摘要、混合方案；首轮建议结构化，但未定 | 3 种输入示意卡；可旁注 MTRouter 原图对应位置 | **待导师讨论** |
| 12 | **怎样用真实 Agent 验证？** | 一个现有 Coding Harness、任务级完整执行、每次决策日志、真实费用/缓存与终局；TwinRouterBench 是动态评测依据 | **TwinRouterBench Fig.1**（静态/动态两条轨道）+ 我们自己的极简实验流程 | **拟议**，非已运行 |
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


### 2.4 在 PPT 上具体怎样摆放（比复杂架构图更容易讲）

推荐使用 16:9 横版：**上方标题和一句结论（约 15% 高度）；中间四个主盒子（约 55%）；下方反馈闭环（约 25%）；右下角终局结果小框**。四个主盒子各占相近宽度，状态快照+合法动作过滤可在同一个盒子里上下分区。

| 位置 | 框内只保留的文字 | 演讲时一句话 |
|---|---|---|
| 左 ① Agent Harness | 当前任务 / 角色 / 调用边界 t | “Agent 每次需要调用 LLM 时才触发路由” |
| 中左 ② State + Feasible Actions | 8 组决策前状态；Provider 支持的 Model×Effort | “先知道现在发生了什么，再排除不合法选项” |
| 中右 ③ Decision Router | Kev-4B **或** Laya-421M；typed choice | “路由器只负责选择，不负责生成代码” |
| 右 ④ Generative LLM | 选中的模型+effort；LLM 回复 | “真正写代码/规划工具动作的是生成模型” |
| 下方回环 | Tool → Test → Recovery/History → t+1 | “测试与工具结果更新下一轮状态” |
| 右下终局 | resolved?；episode total USD；latency | “完整任务结束才评价成功和总费用” |

**画图示例（只作示意，非训练结果）**：第 t 步最近测试失败、剩余预算充足，候选集合里有 (A, high) 与 (B, medium)；第 t+1 步工具成功后状态改变，路由器可重新选择。不要画成固定“失败必升强模型、成功必降便宜模型”的硬规则。

**两个绝不能画错的地方**：① Kev 与 Laya 是并列实验候选，不是 Kev → Laya 两级串联；② Cache continuity 是观测/估计状态，不是默认可跨模型直接迁移的物理 KV。八组状态可以在第 07 页放大解释，**第 06 页不堆八张小卡**。

**图的视觉优先级**：在线调用的 ①→④ 实线最粗；底部工具/验证反馈次之；离线训练只放第 10 页。状态与动作盒子是方法的核心；系统监控不是单独研究一套 GPU 调度系统。主图标题下标注“Proposed / Not yet evaluated”。

## 3. 论文原图：5 篇新图主选 + 1 篇条件补位 + 2 篇备选

> 用户明确说明最初四篇论文的图片已用过。仓库研究证据表按序的前四篇是 MTRouter、BiCSRouter、SWE-Router、EvoRoute，**但排序不能证明这就是 PPT 已用的四篇**。本地 Agent 必须先查旧 PPT/截图资产；已用的只复用，不重复裁剪。新素材不超过 5–6 张，不为凑数量而加图。

### 3.1 新增优先级：论文、具体 Figure、为什么选

| 优先级 / PPT | 论文及官方 PDF | 具体原图与 PDF 物理页（从 1 开始） | 讲述作用 / 核实情况 |
|---|---|---|---|
| **P0 / 03** | [Unified AI Gateway](https://arxiv.org/pdf/2609.06940) | **Fig. 2**，Conventional AI Gateway vs Unified AI Gateway；**物理页待本地 PDF 核实** | 缓存管理与模型选择联合控制已有先例；图号及内容从论文文本镜像核实，**本轮未成功打开原 PDF** |
| **P0 / 03** | [INFRAMIND](https://arxiv.org/pdf/2606.11440) | **Figure 2，物理第 2 页**：Traditional MAS vs InfraMind 的负载/模型/策略选择对照。**Figure 3，物理第 5 页**：完整 Planner–Executor–Monitor–Scheduler（备选） | Fig.2 比 Fig.3 更适合与 Gateway 并排投影；两图编号与页码已从原 PDF 核实，Fig.3 已直接查看原图 |
| **P0 / 04** | [ProgRouter](https://arxiv.org/pdf/2608.25992) | **Figure 2**：Progress-guided routing overall procedure；**物理页待本地 PDF 核实** | 用工作流 ledger、进度、预算说明为什么只看 KV 不够；图号从论文文本转载核实，**本轮未成功打开原 PDF** |
| **P0 / 05** | [Route-to-Reason](https://arxiv.org/pdf/2505.19435) | **Figure 1，物理第 2 页**：Dynamic Reasoning vs Model Routing vs RTR | 已直接查看原 PDF 图；证明联合 model×reasoning strategy 已有研究，**不等于原生 provider reasoning_effort** |
| **P0 / 12** | [TwinRouterBench](https://arxiv.org/pdf/2605.18859) | **Figure 1，物理第 2 页**：Fast Static Track vs Live Dynamic Track | 已直接查看原 PDF 图；解释为何静态路由精度不能代替真实任务成功与 provider 花费 |
| **条件补位 / 04、11** | [MTRouter（ACL 2026）](https://aclanthology.org/2026.acl-long.2045.pdf) | **Figure 2，物理第 4 页，印刷第 44209 页**：History Encoder + Model Encoder + Outcome Estimator | 已直接查看 ACL 原 PDF 图；**只有旧四篇没用过或需要复用旧资产时才放，不再重复截** |

### 3.2 备选论文和只引文、不裁图的论文

| 层级 | 论文 | 安排 |
|---|---|---|
| **P1 备选** | [SWE-Router](https://arxiv.org/pdf/2607.00053) | Figure 1，物理第 2 页（据仓库前次核对；本轮未重新打开 PDF）；第 04/11 页需要说明“部分轨迹→继续/升级”时使用。若在旧四篇中，复用已有图 |
| **P1 备选** | [EarlyEval](https://arxiv.org/pdf/2609.02783) | 适合“中途历史预测终局”的第 11/12 页；**不锁定 Figure 编号与页码**，本地读原 PDF 后决定 |
| **P2 正文引用** | [FrugalGPT](https://arxiv.org/abs/2305.05176)、[RouteLLM](https://arxiv.org/abs/2406.18665)、[RouterBench](https://arxiv.org/abs/2403.12031) | 第 02/09/10 页：请求级路由和静态监督背景，不再占用大图 |
| **P2 正文引用** | [TRACE-Router](https://arxiv.org/abs/2607.22465)、[TACIT-Switch](https://arxiv.org/abs/2608.27911)、[Budget-Aware Agentic Routing](https://arxiv.org/abs/2602.21227)、[EvoRoute](https://aclanthology.org/2026.acl-long.1771/) | 第 04/12/13 页：任务级路由、切换、预算和反馈的近邻；已用旧图优先复用 |
| **P2 正文引用** | [Mooncake](https://www.usenix.org/conference/fast25/presentation/qin)、[LMCache](https://arxiv.org/abs/2510.09665) | 第 03/07 页：缓存系统背景；不是 ModelRouter 的直接算法对照 |
| **P2 讨论备用** | [RouteGuard](https://arxiv.org/abs/2608.07583)、[Task- and Session-Level Model Routing](https://arxiv.org/abs/2608.14641) | 第 13 页：提醒“路由器分数高”不一定意味着任务级收益；通常只需引用 |

**图像配额与版面**：第 03 页 2 张（Gateway Fig.2 + INFRAMIND Fig.2）；第 04 页 1 张（ProgRouter Fig.2，必要时配旧 MTRouter 小图）；第 05 页 1 张（Route-to-Reason Fig.1）；第 12 页 1 张（TwinRouterBench Fig.1）。因此正常情况下**新增 5 张原图即可**，不是八篇全部截图。第 06 页只放我们的原创主流程图，不掺论文原图。

**图像验证分级**：
- **已直接查看原 PDF 图**：INFRAMIND Fig.3、MTRouter Fig.2、Route-to-Reason Fig.1、TwinRouterBench Fig.1。
- **原 PDF 文本已核对 Figure 编号和物理页，截图未成功或未再次取得**：INFRAMIND Fig.2。
- **仅图注/正文镜像核对，必须由本地打开原 PDF 才能裁剪**：Unified AI Gateway Fig.2、ProgRouter Fig.2。
- **备选待核对**：EarlyEval。任何 PDF 版本变化都以本地实际打开的 PDF 为准；记录 PDF 物理页（1-based）和实际 Figure 标号，**不得猜页码**。

## 4. 给本地 Codex / Agent 的提示词（可直接复制）

> **任务：ModelRouter 组会真实论文图片核对与裁剪；只交素材，不做 PPT，也不画我们的主流程图。**
>
> 仓库 sxyq/modelrouter。先读：
> - our-project/planning/GROUP_MEETING_PPT_OUTLINE.md（当前最新版）
> - our-project/planning/GROUP_MEETING_RESEARCH_BRIEF.md
> - our-project/planning/RESEARCH_OVERVIEW.md 与 PROJECT_STATUS.md
> - research/task-level-cost-routing/literature/evidence/direct-evidence.md
> - research/task-level-cost-routing/literature/index.md
>
> **步骤 1 — 去重旧四篇。** 查 our-project/汇报/、research/task-level-cost-routing/literature/ 下历史 PPT、PDF、visual_report_assets、图片和引用记录，列出“旧四篇的准确标题—已使用 Figure—旧素材路径”。仓库证据表前四条（MTRouter、BiCSRouter、SWE-Router、EvoRoute）只是线索，不能直接当结论；如果无法确认，标注待用户确认，继续做可确定的素材。
>
> **步骤 2 — 先核查 P0 的 5 张新图。** 依次从官方原 PDF 打开并核实：Unified AI Gateway Fig.2（页码待核）；INFRAMIND Fig.2（PDF 第 2 页，备选 Fig.3 第 5 页）；ProgRouter Fig.2（页码待核）；Route-to-Reason Fig.1（第 2 页）；TwinRouterBench Fig.1（第 2 页）。如果某篇已在旧四篇中且图已裁过，**优先复用旧文件**。如 P0 图不可读、不支持本页论点或重复，才按第 3.2 节考虑 MTRouter Fig.2、SWE-Router Fig.1、EarlyEval 的替代。所有 PDF 物理页从 1 开始，渲染工具若用 0-based 索引要注明转换。
>
> **步骤 3 — 读图而不是只找图号。** 对每张先看正文方法段、Figure 图注、前后 1–2 段，写清楚这张图**证明了什么、不证明什么**。特别注意：Gateway 的跨模型 KV 映射是条件性的系统能力，不代表我们的 provider 已实现；INFRAMIND Flash/Concise/DeepThink 是 prompting strategy，不是原生 reasoning_effort；Route-to-Reason 也是 model×strategy，不等同原生 effort；TwinRouterBench 的动态轨道按实际任务执行与费用计账。
>
> **步骤 4 — 裁剪真实原图。** 用本地已存的原 PDF 优先，缺失再取官方 PDF；只裁 Figure 主体，必要时保留图注或另存图注文字。优先矢量裁剪或清晰 PNG（约 2–3 倍展示分辨率）。不得 AI 重绘冒充原图，不改数值、图例、箭头和标签。旧图不重复下载/裁剪。原论文 PDF 版本、官方链接必须留档。
>
> **步骤 5 — 最小交付。** 复用已有 PPT 素材目录，最多新增约 5 张 P0 图。生成一份 Markdown 素材清单：准确论文标题、官方 URL、PDF 版本、Figure 编号、PDF 物理页、图注/一句图意、截图路径、目标 PPT 页、是否与旧四篇重复、核查状态。给每张一个可快速查看的预览。按“已完成/重复复用/未找到/待用户确认”汇报即可。
>
> **严格禁止：** 不生成 PPT、不画 ModelRouter 原创流程图、不更改科研方法或训练数据、不训练、不调用付费模型、不编造 Figure 页码或实验收益。不做 PR/CI、工程门禁、可信基线建立或反复复核等无关流程。

## 5. 下一步怎么用这些素材

1. **先由本地 Agent 返回去重结果和约 5 张真实原图**；如旧四篇确实包含 MTRouter/SWE-Router，直接引用旧素材。
2. **我们另行确认第 06 页原创主流程图**：四主盒 + 底部反馈回环 + 终局计费；本轮仍只规划，不画。
3. 最后再排 PPT 页面；不能用原论文图的模拟收益冒充我们的实验结果。

**本轮范围**：只更新组会 PPT 规划 Markdown；不下载/裁剪论文图、不制作幻灯片、不运行模型或实验。

拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。
