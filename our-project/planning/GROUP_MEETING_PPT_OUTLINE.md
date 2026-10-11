# ModelRouter 组会 PPT 分镜 v7｜10 页压缩版

> 2026-10-12。由 v6 的 16 页压缩为 **10 页、约 15 分钟**。这是制作规划，**尚未制作整页 PPT；三张新 PDF Figure 已由另一会话裁剪并推送**。论文依据 `../汇报/ModelRouter组会/PAPER_NOTES_AND_FIGURES.md`。本轮不使用深度研究、GPU 训练或付费 API。
>
> 叙事主线：**为什么看 Episode → 前人覆盖了什么 → 我们的联合决策究竟是什么 → 数据是否够 → 如何验证**。论文页必须融入真实原 PDF Figure，不允许 AI 重绘原图。

## 1. 十页一览

| 页 | 标题 / 一句话主张 | 主要画面（真实 Figure / 原创） | 讲解 |
|---:|---|---|---:|
| **01** | **ModelRouter：面向长程 Agent 的状态感知 (model, native effort) 路由**。目标是成功约束下减少完整任务成本。 | 原创 Agent 轨迹封面，两个终点指标 Success / Total USD。 | 0:35 |
| **02** | **便宜的一次调用，不一定带来便宜的完整任务**。必须沿 episode 计入重试、工具、验证与缓存相关成本。 | `cats_cost_definition_p04.png` + 原创两条任务轨迹对比（标注“概念示意，非实测”）。Price Reversal 公式可作小脚注。 | 1:15 |
| **03** | **基础设施、缓存与模型/深度联合调度已有先例**。新意不能写成“首次 cache-aware”。 | 双原图：`gateway_fig2_p03.png` vs 已裁 INFRAMIND Fig.2；底部短注说明 infra depth 不必等同 provider native effort。 | 1:45 |
| **04** | **Agent 的历史、进度和升级时机也早有人研究**。区分 partial-trajectory escalation 与永久 handoff。 | 双原图：`swe_router_flow.png` vs `tacit_switch_flow.png`；底部两枚小引文 MTRouter（history）、PROGROUTER（progress）。两图 Fig. 号待 PDF 核对。 | 1:40 |
| **05** | **模型×推理策略不是首次联合选择；我们要验证的是动态 Agent 原生 effort**。 | 左 `rtr_fig1_p02.png`；右原创 provider-valid `(model, native effort)` 候选矩阵。短注 Route-to-Reason / UniScale 的动作语义不同；下方一句研究缺口。 | 1:50 |
| **06** | **核心系统：每个合法 LLM-call 边界选一次 (model, effort)**。这是全场唯一主流程页。 | 原创 4 盒+反馈环：Harness → State Snapshot + Valid Filter → Kev **或** Laya → Generative LLM → Tool/Verifier/History → 下一步；右下 episode success/total USD。 | 2:10 |
| **07** | **决策前八组状态 + 两种替代 Router**。History 是表示方法，不是第九组状态。 | 八组状态 2×4 小图 + Kev-4B / Laya-421M 二选一卡；时间遮罩 t vs t+1 防信息泄露。 | 1:40 |
| **08** | **数据充足但监督语义不等于真实在线收益**。先冷启动，再做动态验证。 | 三段真实数据数字：14 源 / 6,600,628 异构行；Choice 83,259；Agent State 88,087；Effort 290 有效对。右侧 3 种 Choice regime + 许可/未训练警示。 | 1:40 |
| **09** | **评测必须跑真实 Agent episode，而不只做静态选路准确率**。 | 左已裁 TwinRouterBench Fig.1；右对照梯度 Fixed / Model-only / Cache-only / Full-state + success、total USD、$/resolved、latency、router overhead。 | 1:45 |
| **10** | **当前成果、最小下一步、需要导师确认的选择**。没有训练结果就不展示虚构曲线。 | 左已完成：文献、数据适配、CPU 格式检查；右待做：许可清理、训练、harness、动态评测；底部 3 个待讨论决策。 | 1:00 |

**预计合计 15 分钟 20 秒**；问答另计。论文只占 P03–P05 三页，评测证据放 P09；不再逐篇单独讲，也不设置独立的 8 组状态页、Kev/Laya 页、训练页、研究缺口矩阵页。

## 2. 与 v6 的合并关系

- v6 P02+P03 → v7 **P02**：任务经济性与计账。
- v6 P04 → v7 **P03**：Gateway / INFRAMIND。
- v6 P05+P06 → v7 **P04**：SWE / TACIT 原图为主，MTRouter / PROGROUTER 引文为辅。原来的 MTRouter、PROGROUTER Figure 留作附录备选，**不挤在同一页放 4 张图**。
- v6 P07+P09 → v7 **P05**：Route-to-Reason / UniScale 先例 + 一句话缺口；不单独做覆盖矩阵。
- v6 P10 → v7 **P06**：核心架构，保留整页。
- v6 P11+P12 → v7 **P07**：八组状态 + 两个替代 router。
- v6 P13+P14 → v7 **P08**：数据与冷启动合并。
- v6 P08+P15 → v7 **P09**：TwinRouterBench 与实验设计合并。
- v6 P16 → v7 **P10**：当前进度和决策。

## 3. 视觉与讲述约束

- **16:9，1920×1080**；沿用旧 `our-project/汇报/PPT/deck.html` 的暖纸白、衬线标题、青绿/锈红重点、完整页面图像感。底色 `#f5f3ee`、白卡 `#fffefa`、墨色 `#17202a`。
- 每页只讲**一个可复述的结论**；论文 Figure 占主要空间（通常 55–65%），只放 1–2 张真实原图，不做文字墙。每张图底部标论文、Fig.、PDF 物理页与来源。
- 论文截图以**原始 PNG 独立后合成**，不得由生图模型重新绘制或生成伪论文图；精确箭头、公式、数据和标签使用矢量/文本层。
- **P06 是视觉中心**，不是 Kev → Laya 串联：Kev-4B / Laya-421M 为可替代 typed-choice router，后面的生成式 LLM 才执行任务。先做 provider 合法动作过滤，再路由；t 时刻只能看 t 前状态。
- 区分 reported cache tokens / estimated prefix overlap / simulated cache hits，不假设跨模型物理 KV 可复用。Route-to-Reason 的 reasoning strategy、UniScale 的 TTS 参数与 provider native effort 不画等号。
- 数据口径：6,600,628 是**异构来源记录总量**，不是可用在线轨迹标签；Choice A/B/C 分别 39,716 人类偏好、4,039 唯一质量胜者、39,504 静态历史成本 tie-break；RouterBench / LLMRouterBench 为 `LICENSE_PENDING`，未获授权不得训练。
- **没有 GPU 微调、付费 API、动态 harness 实测**。全部未验证的模型效果标 `Proposed`，不出现虚构实验图。

## 4. 新 PDF 截图：先做最小必需集

| 优先级 | 原图 | 状态 | v7 用途 |
|---|---|---|---|
| **P0** | INFRAMIND Fig.2，https://arxiv.org/pdf/2606.11440 | **已裁并核对 p.2** | P03 必需 |
| **P0** | TwinRouterBench Fig.1，https://arxiv.org/pdf/2605.18859 | **未裁，物理页待核对** | P09 必需 |
| **P1** | PROGROUTER Fig.2，https://arxiv.org/pdf/2608.25992 | **已裁并核对 p.4** | 附录/备用，正文 P04 只引用论文 |

执行提示词在 `../汇报/ModelRouter组会/PAPER_FIGURE_CROP_PROMPT.md`。真实裁剪统一放 `../汇报/ModelRouter组会/assets/paper-figures/`。旧 `twinrouterbench_pdf_p01_preview.png` **不是** Fig.1。

## 5. 最小制作顺序

1. 三张原论文截图已裁并推送，直接使用 `../汇报/ModelRouter组会/slides-v7/assets/paper-figures/` 中的原图；不再重复裁剪。
2. 先制作 **P04（SWE / TACIT 双论文图）** 与 **P06（ModelRouter 核心流程）** 两张 1920×1080 样张，检查原图清晰度、构图与箭头语义。
3. 样张过关后制作其余 8 页；投影核对图中文字可读性。保留附录的原图和详细论文笔记，但不增加主讲页数。
4. 如时间只剩 10 分钟，可跳过 P03 的细节与 P07 的每组字段解释，不再继续删掉核心流程、数据和评测三页。

**执行事实**：目前已有规划、18 张原始论文截图、详细笔记与 v7 生图工作区；本文件不是成品 PPT。