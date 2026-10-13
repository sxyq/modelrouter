# 汇报三 · ModelRouter 论文实验方案（V6）

> **专题**：从公开静态 Pareto 选模型池，到任务拆分、Model×Effort 与 KV 历史联合决策，最后检验真实 Agent Episode 的成功率—成本前沿。
>
> 五个 RQ、8 张正文图、12 张只有表头与第一列的空白实验表。**尚无本轮新 Benchmark 结果；不能预填虚构成功率、价格优势或最优路由轨迹**。

## 阅读入口

1. [论文实验与图表规划（正式设计草案 V6）](ModelRouter论文实验与图表规划.md)
2. [HTML 交互式原型](交互式原型/index.html)
3. [专题汇报提纲](汇报提纲.md)

GitHub 源码视图不会执行 HTML；可本地下载 `index.html` 并在浏览器打开，无需依赖。

## 五个 RQ

| RQ | 核心研究问题 | 图 | 表 |
|---|---|---|---|
| RQ1 | 静态前沿能否迁移到真实 Agent，哪些模型组合有互补价值？ | Fig. 1、Fig. 4 | T1、T4 |
| RQ2 | 任务拆分 G × 路由频率 F 的最佳决策粒度是什么？ | **Fig. 7** | **T8** |
| RQ3 | Model × Native Effort 联合分配是否比单因素有效？ | Fig. 5 | T5 |
| RQ4 | 缓存、上下文和恢复历史何时改变 Stay/Switch 的最优选择？ | Fig. 6 | T6、T7 |
| **RQ5** | **完整路由能否扩展真实任务的成功率—成本前沿？** | **Fig. 3** | **T3** |

## 研究边界

选池与路由收益分开测；任务拆分与路由频率分开控制；仅使用真实合法模型与 Effort。真实 KV 使用报告与前缀估算分开，不推断未执行动作的反事实结果。

[汇报一](../汇报一/) 负责原始经济动机，[汇报二](../汇报二/) 负责相关论文。研究方法总纲见 [RESEARCH_OVERVIEW](../../our-project/planning/RESEARCH_OVERVIEW.md)，正式预算/执行决策见 [EXPERIMENT_QA](../../our-project/planning/EXPERIMENT_QA.md)，最新实际实验状态见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md)。
