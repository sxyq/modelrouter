# ModelRouter 组会 PPT 论文原图截图库

> 用途：为 ModelRouter 组会 PPT 补齐真实论文 Figure 截图。本目录只存放从官方论文 PDF 原始渲染裁剪的 PNG；**不使用 AI 生图，不临摹、不重画、不翻译或修改论文 Figure**，图片保持原始比例（未拉伸）。
> 渲染参数：PyMuPDF（仓库内 PDF 直接渲染）；INFRAMIND / TwinRouterBench 300 DPI，PROGROUTER 400 DPI（源 PDF 内嵌原图约 520 DPI，无损范围内）。裁剪均保留完整图形、图内文字与图注，四周仅少量边距。

## 核对记录（2026-10-12）

| 论文 | 官方 PDF 来源 | Fig. 编号 | PDF 物理页 | 完整图注（原文） | 输出文件名 | 核对状态 |
|---|---|---|---|---|---|---|
| INFRAMIND: Infrastructure-Aware Multi-Agent Orchestration（arXiv 2606.11440） | https://arxiv.org/pdf/2606.11440 （本地：`research/task-level-cost-routing/literature/pdfs/39_InfraMind_Infrastructure-Aware_Multi-Agent_Orchestration.pdf`） | Figure 2 | **p.2**（右栏） | "Figure 2: INFRAMIND reads live system metrics and routes around congestion while adapting reasoning depth (Flash/Concise/DeepThink) to current capacity." | `inframind_fig2_p02.png`（884×709） | ✅ 已核对：论文标题、图号、物理页、图注逐项与 PDF 一致；已完成视觉检查（Traditional MAS 与 InfraMind 对比完整、箭头/图例/细字清晰） |
| PROGROUTER: Online Progress-Guided Orchestration for Multi-Agent LLM Workflows under Quality-Cost Tradeoffs（arXiv 2608.25992v2） | https://arxiv.org/pdf/2608.25992 （本地：`research/task-level-cost-routing/literature/pdfs/05_PROGROUTER_…Quality-Cost_Tradeoffs.pdf`） | Figure 2 | **p.4**（整页宽；任务说明"物理页码未知"，已实测为 p.4，非计划猜测） | "Figure 2: Overall procedure of PROGROUTER. A coordinator LLM agent manages a collaborative multi-agent LLM workflow by dispatching worker agents and observing real-time workflow states. The online task progress predictor estimates multi-view task progress from structured and semantic state representations, and the progress-guided router selects suitable LLMs from the model zoo by jointly considering predicted progress gain, remaining task difficulty, and cost-budget constraints." | `progrouter_fig2_p04.png`（2579×1390） | ✅ 已核对：图号、物理页、图注逐项与 PDF 一致；已完成视觉检查（Coordinator / Online Task Progress Predictor / Progress-Guided Router / Model Zoo 全链路完整） |
| TwinRouterBench: Fast Static and Live Dynamic Evaluation for Realistic Agentic LLM Routing（arXiv 2605.18859v2） | https://arxiv.org/pdf/2605.18859 （本地：`research/task-level-cost-routing/literature/pdfs/07_TwinRouterBench_…Agentic_LLM_Routing.pdf`） | Figure 1 | **p.2**（整页宽；已排除页眉"Commonstack / TwinRouterBench"） | "Figure 1. Overview of TwinRouterBench. The benchmark provides a fast static track for offline router development and a live dynamic track for end-to-end validation. The static track covers 970 step-level rows from 520 instances across five workloads, each with an execution-verified target tier; the dynamic track runs routers on SWE-bench Verified with realized API cost." | `twinrouterbench_fig1_p02.png`（1988×1000） | ✅ 已核对：图号、物理页、图注逐项与 PDF 一致；已完成视觉检查（FAST STATIC TRACK 与 LIVE DYNAMIC TRACK 对照完整） |

## 与预期的差异报告

1. **图号与预期一致**：三张图的真实图号均为任务预期的 Fig.2 / Fig.2 / Fig.1，无需替换或冒充。
2. **PROGROUTER 物理页实测为 p.4**（任务标注"未知"，已按图注实际定位）。
3. **指定路径适配**：任务指定的 `our-project/汇报/ModelRouter组会/…` 在仓库中不存在（`our-project/汇报/` 已按负责人 2026-10-12 要求整体 `git mv` 至仓库根目录 `汇报/汇报一/`），且 `PAPER_NOTES_AND_FIGURES.md` 与本 README 原文件在仓库及 Git 全部历史中均不存在——本次为**新建**本 README，目录落盘于当前汇报结构 `汇报/汇报二/ModelRouter组会/assets/paper-figures/`。
4. 未覆盖任何已有截图：本目录三张 PNG 为新建文件，与素材库 `research/task-level-cost-routing/visual_report_assets/paper_screenshots/crops/` 中已核验的裁剪字节一致。

## 使用边界（引用图中内容时必须遵守）

- INFRAMIND 的 Flash/Concise/DeepThink 是论文自定义推理策略，**不等同于 Provider 原生 reasoning_effort**；
- 图中数字（队列深度 130+、67% 容量闲置、970 rows / 520 instances 等）均为**论文实验结果**，不代表本地数据实测。
