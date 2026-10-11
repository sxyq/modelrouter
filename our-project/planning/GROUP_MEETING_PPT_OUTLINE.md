# ModelRouter 组会 PPT 提纲（讨论版）

> 2026-10-11｜建议 15 页、约 18–20 分钟；**本文件只是内容故事板，不是 PPT 成品**。
> 研究事实和实验边界见 [组会研究内容简纲](GROUP_MEETING_RESEARCH_BRIEF.md)、[研究总纲](RESEARCH_OVERVIEW.md)、[最新项目状态](PROJECT_STATUS.md)。
> 汇报目标：向导师说明“研究想法为什么变化、别人做到哪里、我们做了什么、下一步如何证伪”，不是宣称已经得到动态路由实验成果。

## 一、整场汇报的叙事

**问题与研究演变（1–5 页） → 方法与决策模型（6–7 页） → 数据与微调进展（8–10 页） → 未决 History、相关工作、实测与 RQ（11–14 页） → 当前进度和导师讨论（15 页）。**

一句话题目：**面向长程 Agent 任务的多状态感知模型与推理强度联合路由**。

开场核心问题：**单次调用价格最低，是否意味着整个 Agent 任务完成成本最低？** 这只是待实测的研究动机，不预先宣称成本反转普遍存在。

## 二、逐页 PPT 故事板

| 页 | 标题 / 要回答的问题 | 主图和应讲内容 | 论文或项目依据 | 时间 |
| --- | --- | --- | --- | --- |
| **01** | **封面：ModelRouter**——我们研究什么？ | 简洁的 Agent → 状态 → (Model, Effort) → 任务结果概念图；点明成功率约束下的任务总成本 | 项目研究总纲 | 0.5 分 |
| **02** | **研究初衷：为什么考虑 KV Cache？** | 原始两模型切换示意：保持缓存可省前充，换模型可能重读上下文；区分 reported cache 与估计重合 | Unified AI Gateway、Mooncake | 1 分 |
| **03** | **已有两篇工作做到了什么？** | **并列原论文图**：Unified AI Gateway 联合模型/缓存控制平面；INFRAMIND 基础设施感知 Agent 编排。对比决策粒度、输入、动作、目标与实验 | [Unified AI Gateway](https://arxiv.org/abs/2609.06940)、[INFRAMIND](https://arxiv.org/abs/2606.11440) | 2 分 |
| **04** | **为什么从少量状态扩展到八组？** | “缓存局部节省 vs 工具失败、重试、任务未完成”的概念对照；八组状态按任务/交互/系统三层分布 | 两篇核心论文、SWE-Router、EarlyEval | 1.5 分 |
| **05** | **八组状态如何在决策前获得？** | 八组状态卡片 + 一条“决策时刻 t”的时间轴；标记 observed / estimated / missing，明确未来信息不可用 | 项目八组 Schema、MTRouter、PROGROUTER | 1 分 |
| **06** | **完整拟议方法：在线 Model×Effort 路由** | **我们自己的方法图**：Agent Harness → 决策前 State Snapshot → Provider/Cache/Price 约束过滤 → Kev 决策 → 模型调用 → Tool/Verifier/Usage → 下一状态；成功率与总成本在任务终局评价 | RESEARCH_OVERVIEW；Route-to-Reason | 1.5 分 |
| **07** | **为什么选 Kev-4B 和 Laya-421M？** | Kev Qwen3.5 混合骨干+pointer head vs Laya ModernBERT 编码器+决策头；都属于 typed、非生成式决策器，**不是“Jev vs Transformer”**；比较容量/延迟/校准 | [Kev 官方模型卡](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md)、[Laya](https://github.com/NandhaKishorM/laya) | 1.5 分 |
| **08** | **已有数据：14 个公开源、660 万异构记录** | **真实项目数据柱状图**：Agent 轨迹 4,448,643；缓存负载 1,443,926；路由偏好 649,207；Coding 环境 34,517；记忆 24,335。强调不同粒度，不是 660 万动态选择标签 | DATA_SOURCE_AND_POLICY_REGISTRY | 1.5 分 |
| **09** | **数据清洗后真正可用于什么？** | 6 个训练视图的真实数量：Choice 83,259、Pairwise 59,049、Soft Target 53,087、Agent State 88,087、Effort 290、Auxiliary 1,622,547；另注 Kev/Laya 各 1,906,319 适配行、CPU 已通过 | PROJECT_STATUS、PLANNING_MEMORY | 1 分 |
| **10** | **第一轮微调计划：怎样训练和比较？** | Stage 1 A/B/C 三种标签来源图 + Kev/Laya 同数据训练→val 校准→test 终评；说明 Kev 长样本跳过、Laya 截断；RouterBench/LLMRouterBench 许可未定；**GPU 尚未授权** | 项目训练视图、RouteLLM、RouterBench | 1 分 |
| **11** | **未决问题：Agent History 应怎样表示？** | 三选一比较：最近 K 步、结构化事件摘要、摘要+短窗口；建议结构化摘要作为首轮候选，**待导师讨论，不写成已实现** | MTRouter、SWE-Router、EarlyEval、PROGROUTER | 1.5 分 |
| **12** | **其他人怎样做路由？我们的边界在哪里？** | 四条文献研究线的紧凑矩阵：请求级（RouteLLM）；Agent 动态（MTRouter、SWE-Router、PROGROUTER、TwinRouterBench、Harness-Native）；Model×Reasoning（Route-to-Reason、R2-Router）；缓存系统（Gateway、INFRAMIND） | 仓库 19 篇直接证据表及新增调研 | 1.5 分 |
| **13** | **后续如何真实实测？** | **拟议实验图**：一个 Coding Agent Harness + SWE-Gym 任务 → 任务级对照运行 → 决策前日志/真实费用/测试结果 → 少量关键同状态受控分支；静态数据不能代替动态结果 | TwinRouterBench、SWE-Gym、TRACE-Router | 1.5 分 |
| **14** | **RQ 和消融：什么结果才算证明方法有价值？** | 五个 RQ 的 5 行矩阵：状态增量、Model×Effort、任务级目标、Cache/History、Kev vs Laya；主指标 Success、Total Cost、Total Spend / #Resolved、Pareto；对照 Task-only、Cache-only、Fixed、Model-only | 项目研究假设、相关论文 | 1.5 分 |
| **15** | **当前进度与下一步讨论** | **已完成**数据清洗/标签修正/训练适配/CPU 检查；**未完成**正式微调、Agent History、动态 Harness、受控实验；向导师提出四个决策问题 | PROJECT_STATUS | 1 分 |

**讲述顺序重点**：第 03 页证明“我们知道别人已做什么”；第 04 页解释“为什么扩展状态”；第 07–10 页说明“为什么选这两个模型、我们已经完成了多少实际工作”；第 11–14 页明确“真正需要实验回答什么”。

## 三、原论文关键图：后续提取清单（不是已提取）

| 优先级 | 原论文 / 官方 PDF | 希望提取的图 | 组会用途 |
| --- | --- | --- | --- |
| P0 | [Unified AI Gateway](https://arxiv.org/pdf/2609.06940) | 联合模型路由与 KV 管理的控制平面/系统架构图 | 第 03 页：证明“缓存+模型”已被联合研究 |
| P0 | [INFRAMIND](https://arxiv.org/pdf/2606.11440) | Infrastructure-aware planner/executor/scheduler 方法图，或缓存压力与高负载对比图 | 第 03 页：证明“基础设施状态+Agent 步级选择”已有先例 |
| P0 | [TwinRouterBench](https://arxiv.org/pdf/2605.18859) | 静态评测与 Live Dynamic 评测的对比框架图 | 第 13 页：为什么不能只用静态准确率 |
| P0 | [Route-to-Reason](https://arxiv.org/pdf/2505.19435) | 模型与推理策略联合选择的方法图 | 第 06/12 页：Model×Reasoning 已有研究 |
| P1 | [MTRouter](https://arxiv.org/pdf/2604.23530) | History–Model Joint Embeddings / 多轮路由框架图 | 第 11 页：History 表示依据 |
| P1 | [SWE-Router](https://arxiv.org/pdf/2607.00053) | 前 K 步探索、部分轨迹判断、升级/继续流程图 | 第 11/12 页：动态升级近邻 |
| P1 | [PROGROUTER](https://arxiv.org/pdf/2608.25992) | 任务进度与在线路由架构图 | 第 05/12 页：状态和进度已被使用 |
| P1 | [R2-Router](https://arxiv.org/pdf/2602.02823) | 模型—推理预算—质量/成本关系图 | 第 12/14 页：联合计算预算的先例 |

**提取纪律**：本表只规定“要找哪类图”，不提前锁定 Figure 编号和 PDF 页码。新增调研报告给出的图号、图题、页码仍需在实际 PDF 中逐一核对后写入幻灯片。尽量使用 PDF 原始矢量图或高分辨率裁剪；保留坐标轴、图例、原作者、论文名和引用。论文图不允许用生图重新生成并冒充原图。

## 四、我们自己需要制作的图

1. **研究演变图（第 02–04 页）**：KV-only → 两篇相关工作 → 多维 Agent 状态。用示意图，不能画成已验证的性能结果。
2. **八组状态与在线决策架构（第 05–06 页）**：原创方法示意，明确“拟议”。
3. **Kev 与 Laya 架构比较（第 07 页）**：基于官方源码和模型卡重绘；不得把 Kev 画成完全非 Transformer。
4. **数据清洗与训练视图图表（第 08–10 页）**：严格使用仓库真实数量和不同数据粒度；图表最好原生可编辑。
5. **Agent History 候选方案（第 11 页）**：三种设计的比较示意，标注“尚未决定”。
6. **动态实验与 RQ 图（第 13–14 页）**：展示预期采集流程和实验对照，不放任何虚构的降本曲线。

**生图的合理用途**：视觉统一、背景、抽象工作流、原创概念插画；不用于生成伪造论文 Figure、假实验柱状图、假缓存命中数据或含不准确文字的架构截图。

## 五、相关工作讲法：每篇只回答一个问题

- **为什么原本的 KV 方案不够新？** Unified AI Gateway + INFRAMIND（两篇必须单独讲）。
- **Agent 逐步选择和 History 是否有人做过？** MTRouter、SWE-Router、PROGROUTER、EvoRoute、Harness-Native。
- **Model×Reasoning 是否有人做过？** Route-to-Reason、BEST-Route、R2-Router；不能混淆策略、token budget 与 provider 原生 effort。
- **为什么一定要动态实测？** TwinRouterBench、TRACE-Router；任务级反馈与动态执行路径不能由静态单条轨迹替代。
- **Kev/Laya 是否是算法创新？** 不是；它们是待比较的开源决策器底座，贡献须来自新的真实监督、决策问题和受控验证。

## 六、汇报结尾：四个希望导师讨论的问题

1. 八组状态先重点做哪几组的增量消融，如何避免把状态数量当作创新？
2. Agent History 是否先采用结构化事件摘要，再比较短窗口和混合方案？
3. 是否同意 Kev 主研究、Laya 轻量对照先做许可范围内的静态冷启动？
4. 后续选择哪个现有 Coding Harness、哪些真实支持的 Model×Effort 动作、怎样控制任务量与预算？

## 七、状态与边界

- 当前仓库事实：14 个公开来源 6,600,628 条异构记录；六个训练视图与双模型 CPU 格式适配完成。
- 尚未完成：正式 GPU 微调、在线路由系统、真实 Agent 任务级降本、同状态反事实、Agent History 最终方案。
- 本轮只形成 Markdown 讨论提纲；不创建 PPT、不抠图、不生图、不运行训练和付费 API。
- 正式制图前需要复核原论文 Figure 号、原始 PDF 页码、图表引用与展示许可。

拒绝任何不必要的工程化设计与流程，包括 PR/CI、工程门禁、可信基线建立、反复复核等。
