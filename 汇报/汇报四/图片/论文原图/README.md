# 汇报四 · 实际图像素材与来源

## 已取得、已经存入 GitHub 的作者原件（非GPT重绘）

| 文件 | 来源和性质 | 用于 |
|---|---|---|
| `JevAgentHarness_原作者_fig1.png` | 作者 [JevAgentHarness/JevAgentHarness](https://github.com/JevAgentHarness/JevAgentHarness/blob/main/assets/paper_fig1.png)，论文 Fig.1 原导出 | P06 |
| `JevAgentHarness_原作者_fig2.webp` | 作者 [项目网站 Fig.2](https://github.com/JevAgentHarness/jevagentharness.github.io/blob/main/assets/fig2.webp) 原导出 | P07 候选 |
| `JevAgentHarness_原作者_fig3.webp` | 作者 [项目网站 Fig.3](https://github.com/JevAgentHarness/jevagentharness.github.io/blob/main/assets/fig3.webp) 原导出 | P07/08 候选 |
| `JevAgentHarness_原作者_Results.png` | 作者 [路由结果原图](https://github.com/JevAgentHarness/JevAgentHarness/blob/main/assets/results-light.png)，对应作者实际 Terminal-Bench 2.0 汇总 | P08 |

Jev 原版论文 PDF 保存于 `our-project/external/research/papers/60_JevAgentHarness_Benchmarking_Deploying_and_Training_Decision_Models.pdf`，源文件来自作者仓库 `paper/JevAgentHarness.pdf`。上述图是真正**作者导出的原图**，并非通过截图工具从 PDF 逐个坐标裁切；具体 PDF 物理页和图号须在最终排版时核对，不能擅自写页码。

## 仍缺少的原始截图或二进制

- **Whose turn**：论文库现有 `59_Whose_Turn_Is_It_PDF_LINK.md`、既有中文笔记，但本轮公开原版 arXiv PDF 请求未取得文件；P09 的 Figure 1、P10 缓存公式和 P11 主要 Table 尚未保存原始截图。来源：[arXiv PDF](https://arxiv.org/pdf/2610.19292)；禁用替代的AI拟造图。
- **BAAR**：本仓 `09_Budget-Aware_Agentic_Routing_via_Boundary-Guided_Training.pdf` 已存在；本轮没有重复导入，也尚未把指定 Figure 1 单独裁切保存。
- **SAAR**：原作者正式来源是 [vLLM 博客](https://vllm.ai/blog/2026-06-02-session-aware-agentic-routing) 而非论文 PDF。推荐 Figure2 [policy-flow.png](https://github.com/vllm-project/vllm-project.github.io/blob/main/assets/figures/2026-06-02-session-aware-agentic-routing/policy-flow.png) 和 Figure6 [synthetic-headline.png](https://github.com/vllm-project/vllm-project.github.io/blob/main/assets/figures/2026-06-02-session-aware-agentic-routing/synthetic-headline.png)；当前这两个原图单文件 >1MB，连接器无法返回二进制内容，只有URL定位，没有上传“空图”或假图。

## 我们自有的实测图（矢量 SVG）

在 `../数据图/` 下：`P01_微调.svg`、`P03_真实任务覆盖.svg`、`P04_三题八策略.svg`、`P05_费用.svg`、`P05_缓存教师前向.svg`。这些是由真实汇总值排版的**本项目原创数据可视化**，不是论文截图。绘制数值参照 [数据快照](../../数据/真实实测快照.json)，且缺失费用保留下界符号，不把无 Reward 当 Reward 0。

## Whose turn：本轮已核对的图号与素材缺口

| 指定图 | 对应组会页 | 作者内容/位置 | 当前存档状态 |
|---|---|---|---|
| **Figure 1** | P09 | 用户轮次路由与策略示意，作者正文 §1/§2 | 已核图号与图注，原PDF截图**未取得** |
| **Figure 4** | P10 | Sol→Luna/Haiku 的缓存输入净成本 vs 新模型后续调用次数，作者缓存分析段 | 已核图号与图注，原PDF截图**未取得** |
| **Figure 2** | P11 | 2 Benchmark×3 pairs 成本–通过率散点图，Table3/4的图形摘要 | 已核图号与图注，原PDF截图**未取得** |

作者原 PDF [arXiv:2610.19292v1](https://arxiv.org/pdf/2610.19292) 约 196 KB。此次确认数据及图片说明所用辅助页面： [Bytez 正文](https://bytez.com/docs/arxiv/2610.19292/paper)、[thelatestinai 带图表标签的论文转录](https://thelatestinai.com/papers/2610.19292)、[alphaXiv 作者摘要与图说明](https://www.alphaxiv.org/abs/2610.19292)。**链接不等于已经存入原图**。此外 Table4 在 SpreadsheetBench2 的 Opus high/low 下历史信息反而导致 35.8%→32.4% 的下降，P11应保留此反例，不仅强调 SheetCopilot 的 +3.3pp。
