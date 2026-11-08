# ModelRouter · 汇报四

> 主题：V9 全仓成果、真实实验进展、JevAgentHarness / Whose turn 直接竞争研究，以及论文调整方向的组会讨论。
> 创建日期：2026-11-08。**目前只建立资料目录和规划，未制作正式图片、HTML 页面或 PPT；研究方向尚未最终批准。**
> 本次资料核查基准：GitHub main `f52d1232ba5d8347f04cedc6ba3515296e148272`。新数据出现时以实际原始结果更新，不以此日期冻结实验事实。

## 目录入口

- [汇报规划.md](汇报规划.md)：逐页内容、视觉/交互设计、制作顺序及讲述重点。
- [资料与数据依据.md](资料与数据依据.md)：全仓相关资料、最新真实数字、历史/模拟/未知口径、论文笔记现状与来源。
- **后续素材统一落在本目录下**；只有产生实际文件时再创建子目录，不用空目录占位：
  - `笔记/`：JevAgentHarness、Whose turn 论文笔记及其他重点论文简表；按“汇报二/笔记”的完整方法写，保留原图出处。
  - `图片/`：AI 生成的封面/场景视觉、论文原图裁剪、实验图表导出、静态整页 PNG；原图与生成图分开命名。
  - `HTML/`：逐页精确排版、局部互动、CSS/JS、主播放器及最终可离线使用的 `deck.html`。
  - `数据/`：为汇报整理的极小、脱敏的统计快照/图表输入；原始大量数据仍在 `our-project/data` 和 `our-project/results`，不重复复制。
  - `讲稿/`：正式演讲文稿、每页讲述与引用，待内容定稿后再建。

## 主要制作方式

沿用 [汇报三第二版](../汇报三%20第二个版本/README.md) 的 **16:9 图片主体 + 少数 HTML 精确/交互覆盖 + 统一 HTML 播放器**。封面、装饰和概念插画可使用 GPT 图片生成；模型选择树、论文原图、真实数据表、图表数值、公式和脚注必须使用可核实的源内容及 HTML/SVG 绘制，不能让生图模型编造。链接与截图必须有论文名、图号、PDF 页码和来源。

## 研究与数据边界

1. 只汇报真实已有成果；旧 Demo / Synthetic RQ 图不能作为最新正式效果。
2. 当前正式链路是 Harbor → ModelRouterMiniSweAgent → DefaultAgent 的 **Single-Agent**。历史多 Agent 汇报不代表现行实现。
3. 89 题整体覆盖、49 次最新尝试、三题 K=3 比较互为不同统计层级，不可混合计算成功率。
4. 缺官方 Reward 不当失败；缓存读取 Token 不当跨模型物理 KV 共享；模型/教师参考费不当包含 GPU、VM 等完整现金成本。
5. JevAgentHarness 与 Whose turn 分开介绍重叠，保留六条独立的研究调整备选供导师讨论，不提前定稿。
6. 此轮不重新训练、下载数据或修改 Router/Harness；原实验与前三次汇报文件保持原位。

## 上游参考

- [全项目进度](../../our-project/planning/PROJECT_STATUS.md)
- [公开与自有数据总览](../../our-project/data/README.md)
- [训练研究汇总](../../our-project/results/training/training_research.md)
- [Harbor 89 题官方结果](../../our-project/results/benchmark/README.md)
- [汇报二论文笔记范式](../汇报二/笔记/TwinRouterBench/笔记.md)
- [汇报三第二版播放器](../汇报三%20第二个版本/README.md)
