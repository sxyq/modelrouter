# ModelRouter 组会 PPT：沿用旧版「生图页面 + 真实论文原图嵌入」的制作规划（v5）

> 2026-10-12｜本轮**只规划与更新 Markdown，不生图、不制作 PPT、不启动深度研究、不训练模型**。
> 事实依据：仓库旧版 \`our-project/汇报/PPT/deck.html\`、\`演讲文稿.md\`、\`PPT_19页论文与数据汇报规划.md\`、已有论文截图清单，以及 \`GROUP_MEETING_RESEARCH_BRIEF.md\`、\`RESEARCH_OVERVIEW.md\`、\`PROJECT_STATUS.md\`。
> **重要修正**：已经通过旧版 deck 与演讲稿明确“最初已用的四篇”是 **Unified AI Gateway、Google CATS、OpenSquilla / Agentic Routing、Route-to-Reason**。先前 v4 不知道旧四篇是谁，误把 Gateway、Route-to-Reason 当作“新图”；现在纠正。此处的“看过”指已检查 HTML/讲稿/素材文件与引用关系；**尚未对每张二进制 PNG 做像素级视觉预览**。

## 0. 先学旧汇报：不是把论文 PDF 直接塞进幻灯片

### 0.1 仓库中真实存在的旧成品

- **播放器**：\`our-project/汇报/PPT/deck.html\`，20 页，目录、翻页、全屏。
- **完整图片页面**：\`our-project/汇报/PPT/assets/deck-images/page-01.png\` 至 \`page-20.png\` 中的 18 张；P3、P4 是 \`P3-model-matrix-dashboard.html\` 与 \`P4-kv-cache.html\` 两页独立 HTML。**不要误说“旧版是普通 PPT”**。
- **论文页在旧版中的位置**：P7–9 Gateway；P10–12 Google CATS；P13–15 OpenSquilla；P16–18 Route-to-Reason。四篇各按“问题 → 方法 → 结果”讲，原论文 Figure 是整页视觉叙事的组成部分。
- **已有裁剪源**：\`research/task-level-cost-routing/visual_report_assets/paper_screenshots/\` 下有 \`raw/\`、\`crops/\`、\`annotated/\`。例如 \`crops/unified_gateway_p03_fig02.png\`、\`crops/rtr_p02_fig01.png\`、\`crops/mtrouter_p04_fig02.png\`、\`crops/cats_p02_fig01.png\`、\`crops/opensquilla_p06_fig02.png\`。
- **额外旧图**：\`our-project/汇报/PPT/assets/unified-gateway-images/page-06-hidden-cache-cost.png\`、\`page-07-joint-control-plane.png\`、\`page-08-results-boundary.png\`。不要重复制作这些已存在的论点图。

### 0.2 继承旧版视觉语言，但新内容要重排

旧版 HTML 明确的配色：背景 \`#f5f3ee\`（暖纸白）、卡片 \`#fffefa\`、正文 \`#17202a\`、注释 \`#66727d\`、锈红 \`#b45739\`（研究问题/强调）、青绿 \`#2e766b\`（执行/反馈）、蓝 \`#4b7795\`（状态/数据）、金 \`#bd8a36\`（成本/预算）；标题采用 Georgia/宋体式衬线，正文采用无衬线。16:9；浅色背景；细线卡片；留白充足。

**要复制的是“有论文原图、图像化讲故事、少字、风格统一”的呈现方式，不是复制旧版 20 页内容。** 旧版的最终问题是“执行前预测是否值得”（admission-only），**现版主线已变成 runtime Agent state-aware 的逐次 Model×Effort 联合选择**。不能沿用旧版最后一页的研究结论，也不能把旧版 859,549 次调用和新整理的 6,600,628 异构行混为一谈。

## 1. 新版统一生产方式：生图负责视觉，原论文图必须真实无损

### 1.1 每页分三层，而不是一口气让模型画完全部文字和论文图

1. **内容锁定层（文字/数据/流程逻辑）**：先写该页唯一结论、准确的数值、合法箭头与引用，来自本项目 Markdown/论文 PDF。不能让生图模型自由编造。
2. **视觉生成层（生图）**：为每页生成**完整 16:9 背景构图、空间、卡片、装饰和原创概念插画**，预留清楚的论文图/数据图插入区域。可以把旧版 \`page-07.png\`、\`page-14.png\`、\`page-16.png\` 作为**风格参考**，但不能复用其中旧的研究结论。
3. **真实素材合成层（最后嵌入）**：将原 PDF 裁剪出的 Figure、真实数据图、精确标题、来源和关键标注，**以原始像素/矢量独立叠加到生成的页面上**。不能让生图模型“临摹”论文流程图或重新生成图中文字；否则不再是真实论文图。最终输出仍是一张视觉统一的完整页面 PNG，视觉上和旧版一致。

**生成与合成的区别**：可以把原图作为生图时的版式参考，但最终必须用源文件的真实裁剪图覆盖到指定区域。对主流程图的关键箭头、状态名称、公式、数值同样采用受控矢量/文字叠加，生图仅负责美术表达。

### 1.2 三种页面模版

| 类型 | 用途 | 生图生成什么 | 后合成什么 |
|---|---|---|---|
| **A 论文证据页** | 03/04/05/12 | 有层次的论文介绍页、边框、解释区、指引线与留白 | **真实论文 Figure**（优先占宽 55–65%）、论文名、Fig.号、来源、1 句结论/限制 |
| **B 我们的方法页** | 02/06/07/08/10/11/13/14 | Agent 场景插画、流程容器、概念分层、卡片、适量抽象纹理 | 真实流程箭头、状态字段、模型名称、合法动作、公式、待验证标记 |
| **C 真实数据页** | 09（以及必要时 13） | 背景版式、数据可视化容器、图例位置 | **从真实表计算生成**的柱图/比例/数字；不让图像模型自由写数据 |

页面文字总量：标题 1 行、结论 1 句、图中标签若干、脚注 1 行。讲解内容放演讲稿，不塞满图片。

## 2. 新版 14 页逐页生图分镜（18–20 分钟）

| 页 | 核心画面（最终生成页面） | 类型 | 必须叠加的真实内容/来源 | 这一页观众记住什么 |
|---:|---|---|---|---|
| **01** | 浅纸白封面；长程 Agent 多步路径沿画面延伸，终点显示任务成功/费用的两个图形符号 | B | 标题 ModelRouter；副标题“Runtime State-Aware Model × Reasoning-Effort Routing” | 目标是任务级成功与成本 |
| **02** | **左右两条对照 Agent 轨迹**：单次便宜但多次测试失败/重试 vs 单次贵但较快完成；路径用不同线型 | B | 标“概念示例，非实验结果”；不要编造具体美元/成功率 | 便宜的一次不等于便宜的任务 |
| **03** | **双论文证据拼贴**：左 55% 旧 Gateway 原图，右 35% 新 INFRAMIND 原图；下方一条研究边界总结 | A | 旧 \`unified_gateway_p03_fig02.png\`；新 INFRAMIND Fig.2（PDF 第 2 页，实际本地核实）；论文出处 | KV+模型联合、系统状态路由已有先例 |
| **04** | **两篇 Agent 状态研究对照**：MTRouter 的 History Encoder vs ProgRouter 的 progress ledger，背景是 Agent 运行时间轴 | A | **已存** \`mtrouter_p04_fig02.png\`；**待截** ProgRouter Fig.2（页码待本地 PDF 核实） | History/Progress 已有人做，需验证增量价值 |
| **05** | 左侧旧 Route-to-Reason Fig.1，右侧简洁的 \`Model × Effort\` 合法组合矩阵，选中一个格子 | A+B | **已存** \`rtr_p02_fig01.png\`；我们自己的 provider capability 示例；图下注“reasoning strategy ≠ 原生 effort” | 联合动作已有先例，但 Agent 在线约束不同 |
| **06** | **全场主图：ModelRouter 在线闭环**。中间 4 主盒，底部工具/验证/History 反馈，右下任务终局 | B | 见第 3 节：每条箭头、标签、模型身份、合法动作都要精确 | 每次合法调用边界重新选 Model×Effort |
| **07** | 把 06 的 State Snapshot **局部放大**：8 组状态分成三层，旁边一条“决策前可见”时间界线 | B | 八组状态名称，History 非第九组；cache reported/estimated/simulated 区分 | 状态要可观测、不能偷看未来 |
| **08** | Kev-4B 与 Laya-421M 的**并列比较卡**；中间是同一组候选动作，绝不画 Kev→Laya 串联 | B | Kev：Qwen3.5-4B hybrid + pointer；Laya：ModernBERT-large 421M + choice head；“CPU 适配、尚未正式微调” | 两个可比较的 typed decision router |
| **09** | **真实数据海报**：14 公开源的五类数据块 + 6 个训练视图条带；大数强调异构而非动态标签 | C | 6,600,628 异构公开行；Choice 83,259、Agent State 88,087、Effort 290；所有数字由报告核对 | 数据多，不等于可用动态真值多 |
| **10** | **离线训练冷启动流水线**：合法数据 → 同分割 Kev/Laya → 校准/测试；使用细线和三段式卡片 | B | A/B/C 标签含义、训练许可 pending 的来源、无正式 GPU 训练 | 静态训练只证明冷启动，不证明整任务降本 |
| **11** | **History 三选一视觉比较**：最近 K 步 / 结构化事件摘要 / 混合输入，右边用时间轴展示压缩 | B | 三种候选及“结构化摘要优先试验，未定” | History 是表示方案，需要消融 |
| **12** | 左侧 **TwinRouterBench 原 Fig.1**（静态 vs 动态）；右侧我们真实 Harness 任务级计费的简短实验路径 | A+B | 待截 TwinRouterBench Fig.1，PDF 第 2 页；右侧是拟议实验，非已运行 | 静态分数不能代替真实 Agent 结果 |
| **13** | **RQ × Baseline/消融矩阵**：5 行 RQ 与固定/任务级/cache-only/model-only/full-state 列；图例按成功与费用两轴 | B+C | 5 RQ、真实待测指标 Success / Episode Cost / Spend per Resolved / Pareto / overhead | 如何证伪我们的方法 |
| **14** | **两栏收束页**：左“已完成数据/CPU 适配”，右“未完成 GPU/动态实验”；底部四个导师决策卡 | B | 已完成/未完成状态；History、状态消融、Kev/Laya、Harness/预算四项待讨论 | 下一步需要决定什么 |

**论文截图出现的位置**：03、04、05、12。其它页面都主要是我们自己的原创生图与受控数据/流程叠加。旧四篇可以**少量复用**，不再按每篇三页占用大量篇幅。

## 3. 第 06 页主流程图：具体构图和生图边界（只规划，不画）

**16:9 布局**：标题 12% 高度；主链 58%；底部反馈环 22%；脚注 8%。浅纸白，主链四盒从左至右，箭头粗细一致，最突出 **State + Feasible Actions → Router**。

\`\`\`text
                  [调用前可观察的 8 组 Agent Runtime 状态]
                                    ↓
 [Agent Harness at step t] → [State Snapshot + 合法动作过滤] → [Kev 或 Laya Router] → [选中的生成模型 + Effort]
          ↑                                                                             │
          └──── [History 更新] ← [Test / Verifier] ← [Tool / Environment] ← [执行输出] ────┘
                                                                                         └→ [Episode End]
                                                                                             success? / total cost
\`\`\`

**画面设计**：
- **① Agent Harness**：一张简化的 coding 任务卡和历史轨迹图标。
- **② State + Filter**：8 组状态用小标签围绕状态汇聚点；下面用 \`A_t = valid {(model, effort)}\` 表示合法动作集合；可展示 \`(A,low)\`、\`(B,medium)\` 等**纯示例**，不暗示所有 provider 支持这些档位。
- **③ Router**：单个路由决策器，标题 \`Kev-4B / Laya-421M (alternatives)\`；只输出 \`(m_t,e_t)\`，不是生成答案。
- **④ Generative LLM**：模型调用、回复与 usage；KV reported/estimated 两类用不同线型的小标签。
- **底部闭环**：工具 → 验证 → 错误/恢复 → History → 下一次调用。只有在**下一个合法边界**才重新路由；任务结束另进终局评价。
- **图中不能出现**：未来 verifier 结果提前进入当前状态、默认跨模型物理 KV 迁移、Kev→Laya 串联、已实测的降本数字、假定已训练成功的概率。

**生图实施**：先生成不含复杂文字的主链空间、4 个容器和底部反馈的美术草图；随后把**精确箭头、盒名、动作集合、8 组状态、出处/拟议标记**以矢量/文字层覆盖。不能让生图模型自由决定箭头逻辑。最终依然是一张完整、风格统一的 PNG。

## 4. 真实论文 Figure：哪些直接复用，哪些还需要新增

| 论文 | 旧汇报是否已用 | 实际素材或新增目标 | 新版放哪里 |
|---|---|---|---|
| **Unified AI Gateway** | **已用，P7–9** | **复用** \`visual_report_assets/paper_screenshots/crops/unified_gateway_p03_fig02.png\`；另有 Fig.4、Fig.5 现成截图 | 03 |
| **Google CATS** | **已用，P10–12** | 已有 \`crops/cats_p02_fig01.png\` 等；新版只在 02/13 需要成本视角时可复用，**不强求出图** | 备用 |
| **OpenSquilla / Agentic Routing** | **已用，P13–15** | 已有 \`crops/opensquilla_p06_fig02.png\` 等；可在 07 或 12 做小图补充，**不强求出图** | 备用 |
| **Route-to-Reason** | **已用，P16–18** | **复用** \`crops/rtr_p02_fig01.png\`；另有 Fig.4、Fig.7 现成截图 | 05 |
| **MTRouter** | 不在“最初四篇”主讲中 | **已有** \`crops/mtrouter_p04_fig02.png\`，不必重新截 | 04 |
| **INFRAMIND** | 旧 deck 未列为主讲 | **新裁剪** Fig.2（PDF 物理第 2 页，打开本地 PDF 核实）；Fig.3（第 5 页）备用 | 03 |
| **ProgRouter** | 旧 deck 未列为主讲 | **新裁剪** Fig.2（具体 PDF 物理页待本地核实） | 04 |
| **TwinRouterBench** | 旧 deck 未列为主讲 | **新裁剪** Fig.1（PDF 物理第 2 页，打开本地 PDF 核实） | 12 |
| **SWE-Router** | 旧 deck 非四篇主讲 | 已有 \`visual_report_assets/crops/swe-flow.png\` 和 \`sweRouter_p2-02.png\`，先看是否可复用；如不需要不新增 | 备选 |

**优先新增的真实原图实际只有 3 张**：INFRAMIND Fig.2、ProgRouter Fig.2、TwinRouterBench Fig.1。其它优先从已有裁剪资产拿，不要重复下载/裁剪。若 Fig.2 太密不适合 16:9，选原论文中更易讲的替代 Figure，但必须说明理由、图号和页码。

**重要**：真实论文图作为**最终合成的锁定图层**；可以缩放、整体裁边、加外部标注，不可重绘、替换文字、改数据。每张图在最终页保留准确论文名/年份/Figure 编号/来源。原论文结果与我们的研究假设必须用不同标签区分。

## 5. 三类生图提示词模版（本地 Agent 可直接改成逐页提示词）

### A. 论文原图嵌入型（03/04/05/12）

> 设计一张 16:9 学术组会汇报视觉页面，参考本仓库 \`our-project/汇报/PPT/assets/deck-images/page-07.png\` 与 \`page-16.png\` 的统一风格：暖纸白 \`#f5f3ee\`、墨色标题、锈红/青绿/蓝色小面积强调、衬线大标题、细线卡片、充足留白。整页是一幅完整的讲解型视觉构图，不是普通白底 PPT。画面左侧约 60% 为**清晰的论文 Figure 占位区域**（不要生成/重画其中的流程图、文字或数字），右侧约 35% 为一句主结论、两条简短解释、一个局限；底部留论文来源栏。此页的准确标题与文字由后处理叠加。画面不出现虚构实验图表、不添加水印、不堆小字。**最终将指定的真实 PDF 裁剪 Figure 原样嵌入占位区域**。

### B. 我们的方法/流程型（02/06/07/08/10/11/14）

> 生成 16:9 学术技术汇报插画页面，延续旧版暖纸白、锈红、青绿、蓝的克制配色与 editorial infographic 质感。核心是一张清楚的技术概念示意，空间布局和分区按提供的版式规范执行；避免 3D 机器人、赛博城市、发光大脑、复杂背景和装饰性大箭头。**不要自行编写公式、模型名、节点名、实验数字或决定逻辑**；为这些信息预留干净空间，之后用准确矢量文字和连线叠加。页脚标明 Proposed / Not yet evaluated（后合成）。

### C. 数据与对照型（09/13）

> 生成一张 16:9 学术数据可视化页面的完整美术底版，风格同旧版 deck：暖纸白、细线卡片、清晰信息层级。预留一块大面积主图、两块小解释区、图例和来源区；仅生成背景、装饰与卡片，不生成数据条高度、坐标刻度、数值或统计结论。所有数据图从本项目真实数据或已确认统计表生成后合成；数字、单位、分母、类别必须保留准确。

**生图负面约束统一追加**：不生成假论文图、不伪造 Fig. 编号、不编造成功率或降本比例、不重画真实 Figure、不把策略名称当 provider 原生 effort、不画跨模型 KV 物理共享、不混用旧版和新版数据口径。

## 6. 本地 Agent 的最短执行计划（以后授权生图时用）

1. **读旧成品**：打开 \`our-project/汇报/PPT/deck.html\`，重点实际预览旧 P7、P14、P16 与 P19，确定字号、留白、原图嵌入比例；检查 P3/P4 两页 HTML 的可复用样式。**本轮 Planning 已检查结构但未直接像素预览 PNG，本地这一步必要。**
2. **素材复用与补齐**：复用 Gateway、RTR、MTRouter 现成 crop；仅新裁 INFRAMIND Fig.2、ProgRouter Fig.2、TwinRouterBench Fig.1；记录 PDF 物理页、图号、图片路径。
3. **先做两张风格样张**：**P04 论文原图嵌入型**和**P06 我们自己的主流程型**，每张一幅完整 16:9 页面。样张必须体现“真实 Figure 是画面的一部分”的效果；P06 不得靠模型乱画箭头。
4. **确认样张后再做其余 12 页**：逐页按第 2 节分镜生图，叠加真实论文图、精确文字和数据；输出单页 PNG。需要交互的旧 HTML 仅作参考，不要求照搬。
5. **最小检查与交付**：一次性查看 14 页缩略图，重点检查论文原图未失真、主图箭头正确、数字真实、来源可读；复用旧播放器或简单串联页图即可。**不先制作 PPTX，不进行不必要的工程流程。**

### 本地 Agent 总提示词（待用户批准生图时复制）

> 请先阅读 \`our-project/planning/GROUP_MEETING_PPT_OUTLINE.md\` v5，并打开旧版 \`our-project/汇报/PPT/deck.html\`，实际观看 \`assets/deck-images/page-07.png\`、\`page-14.png\`、\`page-16.png\`、\`page-19.png\`。我们的新汇报要沿用旧版**“完整页面生图 + 原论文真实 Figure 嵌入 + 少量文字解释”**的视觉方式，而不是把截图作为一张普通幻灯片上的附件。四篇已用论文为 Unified AI Gateway、Google CATS、OpenSquilla、Route-to-Reason，旧素材尽量复用；新增优先 INFRAMIND Fig.2、ProgRouter Fig.2、TwinRouterBench Fig.1。真实 Figure 作为锁定图层最终叠加，绝不让图像模型重画或改动其内容。先只制作 P04（论文页）与 P06（原创主流程页）的**样张**供确认，其它 12 页先不要做；生图版式、精确箭头、数据口径、逐页内容和配色全部以 v5 为准。不要深度研究、训练、付费 API、PR/CI 或无关工程工作。

## 7. 这轮不做什么

不实际生图、不截 PDF、不做 PPTX、不改旧 \`our-project/汇报/\` 成品、不启动深度研究。新图、样张与完整组会页面均待下一步明确授权。

拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。
