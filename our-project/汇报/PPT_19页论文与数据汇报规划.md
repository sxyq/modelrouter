# 19 页研究汇报 PPT 规划

## 0. 文档用途

这份文档记录 19 页 PPT 的页序、每页要回答的问题、讲解重点、数据来源和论文截图位置。当前先做规划，不生成 PPT 文件，也不把尚未完成的任务级实验结果写成结论。

本方案是在原 16 页结构上增加第四篇论文的 3 页。原结构中的三篇核心论文保留为：

1. `Unified AI Gateway`：模型路由与 KV Cache 状态联合考虑；
2. Google `Cost-effective Agent Test-Time Scaling (CATS)`：工具型 Agent 的整条轨迹成本；
3. `OpenSquilla / Agentic Routing`：harness 状态驱动的 Agent 路由。

新增的第四篇采用 `Route to Reason`，它对应会话中提到的“模型路由与推理能力/推理策略联合选择”方向，正好增加 3 页。`MTRouter` 放在成本口径证据页和最后的相关工作边界中，作为长程多轮成本路由的近邻，不占用第四篇的三页。

## 1. 全场主线

> 长程 Agent 的费用由完整执行轨迹决定。真实调用数据先展示推理档位、缓存和单次调用成本三个变量，再用四篇论文说明这些变量分别如何进入模型路由与 Agent 成本问题，最后提出：在任务开始前，预测一个配置的整条轨迹是否值得，能否比在线学习或盲分配更有效。

研究问题的工作标题：

> **Is Ex-Ante Prediction Necessary for Agent Routing?**

中文标题可写为：

**长程 Agent 的任务级成本路由**

## 3. 19 页页序规划

| 页码 | 标题                                                   | 页面要回答的问题                | 页面内容与讲解重点                                                                                                                                                                                               | 计划使用的视觉材料                                                                                                                               |
| ---: | ------------------------------------------------------ | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
|    1 | 从一次 Agent Step 到 Long-Horizon Task                 | 长程任务为什么会产生累计成本    | 一个任务由多轮 model call、tool call、失败和重试组成；单次调用费用沿整条轨迹累计为任务费用；最后引出研究问题                                                                                                     | Task → Step 1…Step N → Result 的平直流程图；页脚引用 MTRouter multi-turn framing                                                              |
|    2 | 真实调用数据：我们观察到了什么                         | 数据资产有多大、能说明什么      | GPT 清理子集：859,549 次来源内调用、约 99.3B token、11 个规范化模型、51 个 model × effort 组合、约 56.7 天；明确这是调用级观测                                                                                  | 模型×档位矩阵、token 分桶和时间带；不拆成 CCH/Blog 两套主叙事                                                                                   |
|    3 | Model × Effort × Cache × Call Cost                  | 一次调用层面有哪些变量          | 展示模型、推理档位、cache read/write、普通输入、输出和单次调用费用；说明这些变量需要沿多轮轨迹聚合                                                                                                               | 三列 small multiples：effort、cache token、call cost；颜色固定为蓝、青绿、琥珀                                                                   |
|    4 | 推理档位会移动能力—成本位置                           | 为什么把 effort 作为路由动作    | 介绍 AI Radar 的 cost × IQ 视图；同一模型的不同 effort 对应不同能力与成本位置；不把高档位默认成最优                                                                                                             | AI Radar 原图或网页截图；右侧只放一句结论和两个标注数字                                                                                          |
|    5 | 成本口径：近期论文如何记账                             | 我们的用户侧 USD 口径是否有依据 | 说明单次调用按 input、output、cache read/write 与 provider price 计费，任务成本沿 episode 累计；补充 MTRouter、EET、Price Reversal、UniScale 的口径差异                                                          | MTRouter p.3 Eq.(1) 大图；EET p.6 Table 1 和 Price Reversal p.4 Eq.(2) 小框；UniScale eFLOPs 作为对照；底部写“计量依据，不是核心 Related Work” |
|    6 | Unified AI Gateway：模型切换为什么有隐藏成本           | 第一篇论文解决什么问题          | 模型切换可能使已有 KV Cache 无法直接复用；重新 prefill 会影响 TTFT、输入 token 和成本                                                                                                                            | **论文截图：Unified AI Gateway PDF 第 3 页 Fig. 2**，对比 conventional gateway 与 unified gateway                                          |
|    7 | Unified AI Gateway：模型、位置和 Cache Action 联合决策 | 它的核心系统方法是什么          | Global Control Plane 读取模型需求、资源状态和 cache 状态，联合决定目标模型、执行位置和 cache action                                                                                                              | **论文截图：第 5 页 Fig. 4**；右侧列出 reuse、mapping、transfer、re-prefill 等动作；不要堆长段落                                           |
|    8 | Unified AI Gateway：效果与边界                         | 这篇结果能支持到什么程度        | TTFT 约 1.25×–13.28×、输入成本收益约 1.20×–6.16×；明确这些来自 workload-level analytical simulation，不等同在线 Agent 路由实测                                                                             | **论文截图：第 12 页 Fig. 5** 或第 11 页 Table 4；图下写“analytical simulation”                                                          |
|    9 | Google CATS：Agent 成本为什么要沿轨迹计算              | 第二篇论文解决什么问题          | 工具型 Agent 同时产生 token cost 与 tool-call cost；顺序扩展可能探索不足，并行扩展可能重复调用工具                                                                                                               | 先取得 Google 官方论文 PDF；计划截取论文问题定义/成本定义图或表；若正式 PDF 无图，使用官方研究页预览图并明确标注网页来源                         |
|   10 | Google CATS：预算感知的顺序/并行资源分配               | CATS 如何工作                   | 给定预算，在 sequential exploration 与 parallel exploration 之间分配资源；新状态回到控制器继续决策                                                                                                               | 论文方法流程图截图；目标是保留 CATS controller、sequential、parallel、tool use、budget 的完整关系                                                |
|   11 | Google CATS：性能、工具调用和实际成本                  | 它与我们的任务级成本有什么连接  | 关注 accuracy、tool calls、realized cost 的联合比较；区分 budget 与 realized cost；注明 tool call 可能采用统一的事后标准费率，不等同每个 API 的逐项真实账单                                                      | 论文 scaling curve 或主结果表截图；最终以正式 PDF 的图号和页码为准                                                                               |
|   12 | OpenSquilla：Agent Router 不能只看 Prompt              | 第三篇论文解决什么问题          | Agent 场景还要看 harness state、tool state、verifier、recovery 和 context pressure                                                                                                                               | **论文截图：Agentic Routing PDF 第 6 页 Fig. 2**，保留 query-level 与 harness-native 对比                                                  |
|   13 | OpenSquilla：Harness-native routing 如何工作           | 它的核心方法是什么              | harness state 与 model pool 进入 router，再进入 singleton/ensemble 执行、验证、反馈和数据飞轮                                                                                                                    | **论文截图：第 2 页 Fig. 1**；右侧解释两个 operating regimes                                                                               |
|   14 | OpenSquilla：成本—质量结果与适用范围                  | 它证明了什么                    | 用 PinchBench/DRACO 的 aggregate billed cost per task 与质量结果说明 Agentic routing 的系统可行性；注明这是固定 harness 和模型池下的技术报告结果                                                                 | **论文截图：第 19 页 Fig. 3**，可加第 14–15 页 Table 1/2 局部；不外推到所有 Agent                                                         |
|   15 | Route to Reason：为什么只选模型还不够                  | 第四篇论文解决什么问题          | 模型能力与 reasoning strategy 共同影响效果和输出长度；固定高强度推理会造成 overthinking 与成本增加                                                                                                               | **论文截图：Route-to-Reason PDF 第 2 页 Fig. 1**，保留图号和页码；右侧写问题、变量、局限                                                   |
|   16 | Route to Reason：模型 × 推理策略联合路由              | 它怎样做联合选择                | 输入、候选模型、候选策略编码；预测 performance 与 output length；形成 routing table 后选 model-strategy pair                                                                                                     | **论文截图：第 4 页 Fig. 4**；图占左侧约 60%，右侧用短句解释输入、预测、选择                                                               |
|   17 | Route to Reason：它对我们的启发                        | 这篇论文支持什么，不能支持什么  | 它证明 effort/strategy 是有效路由变量；它主要是 query-level，成本多以输出长度/token 代理，未解决长程任务终局成本                                                                                                 | **论文截图：第 8 页 Fig. 7 或第 13 页 Fig. 9**；结果只写论文原文数字，并标明这是 token proxy                                               |
|   18 | 四篇论文覆盖了哪些变量，还缺什么                       | 现有工作与我们的研究空间是什么  | Unified Gateway 给出 cache 状态；CATS 给出整轨迹成本；OpenSquilla 给出 harness-native routing；Route-to-Reason 给出 model × strategy；MTRouter 作为逐轮路由近邻。逐项标出决策时点、粒度、成本单位和是否完整轨迹 | 四论文稀疏矩阵：Model、Effort、KV Cache、Task Cost × admission/online；不写“完全没人做过”                                                     |
|   19 | Our Idea：执行前预测是否值得                           | 我们最终要验证什么              | 统一任务级账本，比较 ex-ante predictor、TRACE-UCB、share-matched blind、fixed cheap/strong、oracle；列出 RQ1–RQ3 和结果分流：预测有效、预测接近盲分配、或固定策略已足够                                         | 右侧放 predictor / online / blind / fixed / oracle 对照流程；底部列出“当前调用级数据 → 未来受控 episode 数据”                                 |

## 4. 四篇核心论文的统一讲法

四篇核心论文的 3 页版式保持一致：

1. **问题页**：论文面对的系统或推理问题；
2. **方法页**：论文原始流程图，旁边只解释输入、决策、输出；
3. **效果页**：主结果图或表，下面写适用范围和限制。

每页论文截图遵循“左图右文”：

- 左侧约 60% 放原始 Figure/Table 或高分辨率局部；
- 右侧放一句结论、两条证据、一个限制；
- 底部保留作者、年份、`Fig./Table` 编号和 PDF 页码；
- 不用整页 PDF 缩成背景，不把截图当装饰；
- 论文结果与我们数据使用不同颜色和标签，避免听众误解。

## 5. 四篇论文截图清单

| 论文                                                                           | 本地材料                                                                                                                                   | 首选截图                                    | 备用截图                       | PPT 作用                                                                             | 当前限制                                                                                          |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Unified AI Gateway                                                             | `research/task-level-cost-routing/literature/pdfs/38_Unified_AI_Gateway_A_Framework_for_Joint_Model_Routing_and_KV_Cache_Management.pdf` | p.3 Fig.2、p.5 Fig.4                        | p.12 Fig.5、p.11 Table 4       | 证明模型切换与 KV Cache 状态有关                                                     | 主要是系统与解析仿真；不等于任务级路由实测                                                        |
| Google CATS（正式题名：Budget-Aware Tool Use Enables Effective Agent Scaling） | `research/task-level-cost-routing/literature/pdfs/55_CATS_Budget-Aware_Tool_Use_Enables_Effective_Agent_Scaling.pdf` | p.2 Fig.1、p.7 Fig.6、p.4 成本定义 | p.9 Fig.7 | 证明 Agent 成本要同时考虑 token、tool call 与完整执行过程 | 工具调用费用采用论文中的统一标准费率，不能直接当成每个外部 API 的逐项账单 |
| OpenSquilla / Agentic Routing                                                  | `research/task-level-cost-routing/literature/pdfs/56_Agentic_Routing_The_Harness-Native_Data_Flywheel.pdf` | p.6 Fig.2、p.2 Fig.1 | p.19 Fig.3 | 证明 harness state 可以进入 Agent routing，且论文报告 aggregate billed cost per task | 技术报告/预印本；结果依赖固定 harness、模型池和 benchmark |
| Route to Reason                                                                | `research/task-level-cost-routing/literature/pdfs/12_Route_to_Reason_Adaptive_Routing_for_LLM_and_Reasoning_Strategy_Selection.pdf`      | p.2 Fig.1、p.4 Fig.4                        | p.8 Fig.7、p.13 Fig.9          | 证明模型与 reasoning strategy 可以联合选择                                           | 主要是 query-level；成本主要由 token/output length 表示，不是整任务 USD                           |
| MTRouter（补充边界）                                                           | `research/task-level-cost-routing/literature/pdfs/01_Cost-Aware_Multi-Turn_LLM_Routing_with_History-Model_Joint_Embeddings.pdf`          | p.1 Fig.1、p.3 Eq.(1)                       | p.4 Fig.2、p.6 Table 3         | 成本口径证据与相关工作边界                                                           | 论文以逐轮 routing 为主，不等于本研究的事前多目标预测                                             |

## 6. 论文截图制作流程

### 阶段 A：材料核验

1. 读取每篇论文正文和图注；
2. 记录论文版本、发布日期、页码、图号和结果口径；
3. 已将 Google CATS 与 OpenSquilla 正式 PDF 保存到现有 `literature/pdfs/` 目录；
4. 只选能直接支撑当前页结论的 Figure/Table。

### 阶段 B：截图与裁切

1. 用 PDF 渲染得到原始页面图；
2. 只裁切相关 panel，保留 `Fig./Table` 编号和必要图注；
3. 在截图上加 1–2 个细线框或编号，不用大量箭头；
4. 把截图路径登记到 PPT 素材清单；
5. 截图只放在论文证据页，数据图保持可编辑。

### 阶段 C：PPT 编排

1. 先完成 P1–P6 的问题、数据和成本口径；
2. 依次完成四篇论文的 12 页；
3. 最后完成 P18–P19 的综合和研究问题；
4. 渲染全套 PPT，检查截图文字在投影尺寸下可读；
5. 复核每页来源、页码、图号、单位和“论文结果/我们数据”标签。

## 7. 数据页的固定口径

P3–P5 只使用 GPT 清理子集：

- CCH GPT：638,421 次调用；
- SXYQ Blog GPT：221,128 次调用；
- 合计：859,549 条来源记录；
- 11 个规范化模型；
- 51 个模型 × 推理档位组合；
- 约 99.33B token；
- 时间范围约为 2026-07-25 至 2026-09-19，约 56.7 天。

必须在页脚说明：

> 统计单位为来源内调用记录，不等于任务数量；CCH 与 Blog 的成本单位不同，当前不做跨来源金额相加。

## 8. 最终 PPT 不应提前写出的内容

- “成本反转已经被当前日志证明”；
- “执行前预测一定优于 TRACE 或在线学习”；
- “路由预计可以降低某个固定百分比”；
- “四篇论文已经覆盖所有相关工作”；
- “当前 859,549 条记录可以直接计算任务级 `$/resolved`”。

这些内容只能在受控 episode 实验完成后，根据实际结果填写。

## 9. 已完成与待完成的材料

- [x] 核对 Google CATS 与 OpenSquilla 的本地正式 PDF；
- [x] 从四篇核心论文中按清单生成局部高清截图；
- [x] Route-to-Reason 使用 p.8 Fig. 7 的 plot-only 局部，图号保留在来源条中；
- [x] 将截图路径登记到下一节的素材清单；
- [ ] 从现有数据生成 P3–P5 的 GPT 子集图表；
- [ ] 明确 PPT 面向组会、开题还是论文提案，以确定讲解节奏；
- [ ] 生成 PPT 后做逐页渲染和投影尺寸可读性检查。

## 10. 已生成的论文截图素材

`raw/` 保留渲染后的整页来源，仅供定位；PPT 应优先使用 `annotated/`，需要无标注版本时使用 `crops/`。所有标注图都保留图号或表号、必要图注和来源条，细框只用于指示证据区域。

目录：

```text
research/task-level-cost-routing/visual_report_assets/paper_screenshots/
├── raw/
├── crops/
└── annotated/
```

| PPT 页 | 论文证据 | PDF 页码与编号 | 裁切图 | 标注图 | 在 PPT 中讲什么 |
|---:|---|---|---|---|---|
| 5 | MTRouter 成本约束 | p.3, Eq.(1) | `crops/mtrouter_p03_cost.png` | `annotated/mtrouter_p03_cost.png` | episode 成本预算与逐轮费用 |
| 5 | EET 评估字段 | p.6, Table 1 | `crops/eet_p06_table01.png` | `annotated/eet_p06_table01.png` | resolved、API calls、输入/输出 token、总成本 |
| 5 | Pricing Reversal | p.4, Fig.2 | `crops/price_reversal_p04_fig02.png` | `annotated/price_reversal_p04_fig02.png` | listed price 与实际成本可能反转 |
| 5 | Pricing Reversal 成本公式 | p.4, Eq.(2) | `crops/price_reversal_p04_eq02.png` | `annotated/price_reversal_p04_eq02.png` | input、output、cache write/read token 共同计费 |
| 6 | Unified AI Gateway | p.3, Fig.2 | `crops/unified_gateway_p03_fig02.png` | `annotated/unified_gateway_p03_fig02.png` | 常规 Gateway 与 KV-cache-aware Gateway 的差别 |
| 7 | Unified AI Gateway | p.5, Fig.4 | `crops/unified_gateway_p05_fig04.png` | `annotated/unified_gateway_p05_fig04.png` | 控制平面联合选择 cache path 与执行动作 |
| 8 | Unified AI Gateway | p.12, Fig.5 | `crops/unified_gateway_p12_fig05.png` | `annotated/unified_gateway_p12_fig05.png` | TTFT speedup 随带宽、序列长度和 cache hit 变化 |
| 9 | Google CATS | p.2, Fig.1 | `crops/cats_p02_fig01.png` | `annotated/cats_p02_fig01.png` | Budget Tracker 与 BATS 的整体流程 |
| 9 | Google CATS 成本定义 | p.4, unified cost metric | `crops/cats_p04_unified_cost.png` | `annotated/cats_p04_unified_cost.png` | token cost 与 tool-call cost 的统一口径 |
| 10 | Google CATS | p.7, Fig.6 | `crops/cats_p07_fig06.png` | `annotated/cats_p07_fig06.png` | 预算、思考、工具调用、验证和继续/切换 |
| 11 | Google CATS | p.9, Fig.7 | `crops/cats_p09_fig07.png` | `annotated/cats_p09_fig07.png` | accuracy 与 tool calls / unified cost 的联合曲线 |
| 12 | OpenSquilla / Agentic Routing | p.6, Fig.2 | `crops/opensquilla_p06_fig02.png` | `annotated/opensquilla_p06_fig02.png` | rule、LLM、harness-native 路由的决策粒度差异 |
| 13 | OpenSquilla / Agentic Routing | p.2, Fig.1 | `crops/opensquilla_p02_fig01.png` | `annotated/opensquilla_p02_fig01.png` | single-model 与 multi-model ensemble 两种 regime |
| 14 | OpenSquilla / Agentic Routing | p.19, Fig.3 | `crops/opensquilla_p19_fig03.png` | `annotated/opensquilla_p19_fig03.png` | PinchBench 与 DRACO 的 cost–score frontier |
| 15 | Route-to-Reason | p.2, Fig.1 | `crops/rtr_p02_fig01.png` | `annotated/rtr_p02_fig01.png` | dynamic reasoning、model routing 与 RTR 的区别 |
| 16 | Route-to-Reason | p.4, Fig.4 | `crops/rtr_p04_fig04.png` | `annotated/rtr_p04_fig04.png` | model × strategy 编码、预测与 routing table |
| 17 | Route-to-Reason | p.8, Fig.7 | `crops/rtr_p08_fig07.png` | `annotated/rtr_p08_fig07.png` | performance–token trade-off；token 作为成本代理 |
| 18 | MTRouter 相关工作 | p.1, Fig.1 | `crops/mtrouter_p01_fig01.png` | `annotated/mtrouter_p01_fig01.png` | single-turn 与 multi-turn routing 的粒度差异 |
| 18 | MTRouter 结果对照 | p.6, Table 3 | `crops/mtrouter_p06_table03.png` | `annotated/mtrouter_p06_table03.png` | 多轮路由中的质量与总成本联合报告 |

素材的共同限制：这些图来自论文原文，图中的数字属于论文实验、仿真或技术报告结果，不代表本地调用数据的实测结果。当前截图素材已完成，P3–P5 的本地数据图表和全套 PPT 仍未生成。
