# ModelRouter · 汇报四

> 最新真实训练/调用/Harbor 执行、JevAgentHarness 与 Whose turn 两篇核心研究、BAAR/SAAR 补充研究，以及六套独立论文改向选择。**已制作数据素材与研究笔记，16页 HTML 演示稿尚未生成。** 基准日 2026-11-08。

## 正式入口

- **[16 页详细制作大纲](汇报规划.md)**：逐页页眉标题、副标题、主要区域、具体文字、作者原图、数据图表、颜色/页码/字号规则。无封面、无结尾插画、页脚只放标准页码。
- **[真实实测快照](数据/真实实测快照.json)**：训练、Provider、89任务覆盖、49次尝试、三题八策略、成本与缓存；保留无Reward、费用下界及未知字段。
- **[五张真实数据图](图片/数据图/)**：训练对照、覆盖/终局分段条、三题官方Reward热力图、已知费用、教师/缓存/前向，全部为矢量SVG。
- **[作者论文图及真实性说明](图片/论文原图/README.md)**：Jev 原作者 Fig.1、Fig.2、Fig.3、官方结果图；Whose/BAAR/SAAR 图片状态亦列明。
- **[素材状态清单](数据/论文素材状态.json)**：按论文记录已存与尚缺的真实PDF/截图，不用伪图补位。
- **[全仓基础数据依据](资料与数据依据.md)**：保留早期规划阶段的来源背景，演示稿主讲不重复全部旧数据。

## 详细文献笔记（统一格式）

| 文献 | 详细笔记 | 正式PDF/原文 |
|---|---|---|
| JevAgentHarness | [笔记](笔记/JevAgentHarness/笔记.md) | [作者PDF已归档](../../our-project/external/research/papers/60_JevAgentHarness_Benchmarking_Deploying_and_Training_Decision_Models.pdf)，作者图已归档 |
| Whose turn is it? | [笔记](笔记/Whose-turn/笔记.md) | [论文库当前仅来源链接](../../our-project/external/research/papers/59_Whose_Turn_Is_It_PDF_LINK.md)：**原版PDF/三张真实截图未取得** |
| BAAR | [笔记](笔记/BAAR/笔记.md) | [既有原版PDF](../../our-project/external/research/papers/09_Budget-Aware_Agentic_Routing_via_Boundary-Guided_Training.pdf) |
| SAAR | [笔记](笔记/SAAR/笔记.md) | [vLLM 官方技术文章](https://vllm.ai/blog/2026-06-02-session-aware-agentic-routing)，不是作者PDF论文 |

## 内容页序

`P01–P05` 我们最新的训练/外部模型/真实任务/成本与缓存；
`P06–P08` JevAgentHarness 三页（问题、方法、结果）；
`P09–P11` Whose turn 三页（问题、方法、结果）；
`P12` BAAR、`P13` SAAR 各一页摘要，`P14` 二者与V9的重叠对照；
`P15–P16` 六套独立的论文修改方向，每页三张卡。

## 后续网页制作方式

只复用 [汇报三第二版](../汇报三%20第二个版本/README.md) 的 **1920×1080、暖纸白、两到三大内容区、SVG/PNG+HTML叠加、单文件离线deck.html、翻页与目录**。页脚只保留 `01 / 16`；不加入解释性文字、装饰品牌栏或结论条。准确实验数字由保存快照而来；未取得的作者截图不能用 AI 虚构。

## 科研口径

- 正式 Single-Agent：`Harbor → ModelRouterMiniSweAgent → DefaultAgent`；历史多Agent旧图不代表现行系统。
- 训练完成 ≠ 任务增益；49尝试不是49独立任务；6,600,628历史异构行不是当前17行新池监督。
- 模型/教师参考费不包含完整基础设施现金成本；Provider Prompt Cache不等于跨模型物理KV；缺Reward不视作Reward0。
- Jev与Whose应分别研究重叠，不拼成所谓新方法；最后六套方向彼此独立且尚未定稿。
