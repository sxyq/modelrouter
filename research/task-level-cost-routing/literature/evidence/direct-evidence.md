# 直接相关论文证据表

本表只收录当前课题最直接的 19 篇工作。每条证据来自本地 PDF 的正文首页、引言或方法页；论文 PDF 位于同目录下的 `../pdfs/`。表中的“差异判断”是基于正文内容的研究定位，不等同于论文作者的原话。

| 编号 | 论文 | 正文证据（页码） | 已覆盖的能力 | 我们仍可能研究的差异 | 本地 PDF |
|---:|---|---|---|---|---|
| 1 | MTRouter: Cost-Aware Multi-Turn LLM Routing with History–Model Joint Embeddings | p.2: “multi-turn routing, where the agent adaptively switches between models at each step”; p.3 将单次 episode 选择与逐 turn 选择区分 | 多轮、轨迹历史、逐步模型选择、成本约束 | 执行前一次选择；未来调用数、工具路径和费用分布的联合预测 | [PDF](../pdfs/01_Cost-Aware_Multi-Turn_LLM_Routing_with_History-Model_Joint_Embeddings.pdf) |
| 2 | BiCSRouter: Bi-Level Cross-System Routing for Utility-Aware LLM Inference | p.2: “optimizing the configuration within each regime before selecting the optimal system between regimes” | 系统配置级 performance/cost 选择；单 Agent 与多 Agent 方案切换 | 开放式工具环路、随机重试和整条轨迹资源分布 | [PDF](../pdfs/02_Bi-Level_Cross-System_Routing_for_Utility-Aware_LLM_Inference.pdf) |
| 3 | SWE-Router: Routing in Multi-turn Agentic Software Engineering Tasks | p.2: “K exploration steps of code base using cheap … Partial trajectory”; value head 预测 weak model success | 执行若干步后升级；部分轨迹成败预测 | k=0 的整任务配置选择；调用数、token、重试联合预测 | [PDF](../pdfs/03_SWE-Router_Routing_in_Multi-turn_Agentic_Software_Engineering_Tasks.pdf) |
| 4 | EvoRoute: Experience-Driven Self-Routing LLM Agent Systems | p.2 将累计模型调用和工具使用费用作为 agent 系统成本 | 在线逐步路由；经验反馈；性能、费用、速度联合权衡 | 静态 admission 路由和跨配置反事实轨迹预测 | [PDF](../pdfs/04_EvoRoute_Experience-Driven_Self-Routing_LLM_Agent_Systems.pdf) |
| 5 | PROGROUTER: Online Progress-Guided Orchestration for Multi-Agent LLM Workflows under Quality-Cost Tradeoffs | p.3 以结构化 workflow ledger 表示目标、进度和中间状态 | 工作流状态感知；逐步选择模型 | 不改变执行策略的整任务资源预测与一次性选择 | [PDF](../pdfs/05_PROGROUTER_Online_Progress-Guided_Orchestration_for_Multi-Agent_LLM_Workflows_under_Quality-Cost_Tradeoffs.pdf) |
| 6 | TRACE-Router: Task-Consistent and Adaptive Online Routing for Agentic AI | p.2: “The unit of routing should match the unit of feedback”; admission 时为整个任务选择并固定后端 | 任务级在线 bandit；延迟/效果反馈 | 监督式事前预测成功、调用数、token 和美元费用 | [PDF](../pdfs/06_TRACE-Router_Task-Level_Contextual_Routing_for_Long-Horizon_Agents.pdf) |
| 7 | TwinRouterBench: Fast Static and Live Dynamic Evaluation for Realistic Agentic LLM Routing | p.3 动态轨道每次请求选择锁定模型池中的具体模型，并按真实 provider spend 和 cache 计账 | 长程 Agent 路由评测；真实费用；缓存计账 | 执行前预测而非执行回放标签；模型×推理档位的联合选择 | [PDF](../pdfs/07_TwinRouterBench_Fast_Static_and_Live_Dynamic_Evaluation_for_Realistic_Agentic_LLM_Routing.pdf) |
| 8 | TACIT-Switch: Cost-Aware Model Escalation for LLM Agents from Censored Supervision | p.2 对比 task routing、固定前缀升级、逐步延迟和累积风险升级 | cheap→strong 的永久 handoff；风险估计 | 一开始不执行 cheap rollout 的静态选择；最小费用而非固定预算最大成功 | [PDF](../pdfs/08_TACIT-Switch_Cost-Aware_Model_Escalation_for_LLM_Agents_from_Censored_Supervision.pdf) |
| 9 | Budget-Aware Agentic Routing via Boundary-Guided Training | p.3 将历史和工具输出作为 POMDP 状态，每步在 small/large 模型间选择 | 逐步 RL；严格任务预算；难度边界训练 | 执行前分布预测；无需在线探索的静态路由 | [PDF](../pdfs/09_Budget-Aware_Agentic_Routing_via_Boundary-Guided_Training.pdf) |
| 10 | CASTER: Breaking the Cost-Performance Barrier in Multi-Agent Orchestration via Context-Aware Strategy for Task Efficient Routing | p.1 提出图式多 Agent 系统中的动态模型选择；dual-signal router 使用语义和结构特征估计难度 | 多 Agent 图工作流；在线模型选择；按任务难度分配 | 结构未知的交互式 Agent；调用/重试/上下文增长的完整资源分布 | [PDF](../pdfs/10_CASTER_Breaking_the_Cost-Performance_Barrier_in_Multi-Agent_Orchestration_via_Context-Aware_Strategy_for_Task_Efficient_.pdf) |
| 11 | Learning Agent Routing From Early Experience | p.1 研究轻量 LLM 直接回答与完整 Agent 执行之间的路由，并使用早期行为经验 | direct LLM 与 Agent 的冷启动路由 | 同一 Agent 配置之间的完整任务费用预测 | [PDF](../pdfs/11_Learning_Agent_Routing_From_Early_Experience.pdf) |
| 12 | Route to Reason: Adaptive Routing for LLM and Reasoning Strategy Selection | p.2 联合优化 LLM 与 reasoning strategy，预测组合的性能和输出 token | 模型×推理策略的静态选择 | 长程工具交互、失败重试和美元级整任务成本 | [PDF](../pdfs/12_Route_to_Reason_Adaptive_Routing_for_LLM_and_Reasoning_Strategy_Selection.pdf) |
| 13 | Switchcraft: AI Model Router for Agentic Tool Calling | p.3 训练 DistilBERT 路由器，选择“预测正确且成本最低”的模型 | 工具调用；模型正确性评分；成本核算 | 多步任务中的调用数、失败链和终局成功概率 | [PDF](../pdfs/13_Switchcraft_Cost-Aware_Routing_with_Reasoning_Token_Accounting.pdf) |
| 14 | EarlyEval: Cheaper Agent Evaluation via Early Outcome Prediction | p.2 根据中间行为尽早推断最终评价结果，减少完整评测费用 | 轨迹中途成败预测；跨历史轨迹学习 | 预测尚未开始的整条轨迹，而不是提前停止评测 | [PDF](../pdfs/14_EarlyEval_Cheaper_Agent_Evaluation_via_Early_Outcome_Prediction.pdf) |
| 15 | WISERouter: LLM Routing with Workload Budget Constraint | p.2 指出真实部署受 workload 级 token 配额或月度订阅费约束 | 受约束 contextual bandit；工作负载预算 | 单任务质量约束下的整任务成本分布与静态选择 | [PDF](../pdfs/15_WISERouter_LLM_Routing_with_Workload_Budget_Constraint.pdf) |
| 16 | LLMs Can Predict Failure Risk, But Struggle to Predict Which Collaboration Protocol Pays Off | p.1 固定 solver 后比较多个 collaboration protocol，研究额外协作是否值得成本 | 失败风险预测；协作协议成本—收益路由 | 不同模型×effort 的长程 Agent 轨迹资源预测 | [PDF](../pdfs/16_LLMs_Can_Predict_Failure_Risk_But_Struggle_to_Predict_Which_Collaboration_Protocol_Pays_Off_Cost-Aware_Protocol_Routing_.pdf) |
| 17 | Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey | p.3 提出按决策时点、路由对象和反馈组织动态路由设计空间 | 路由与级联的统一术语和分类 | 为 Agent 整轨迹资源预测补充专门测量协议 | [PDF](../pdfs/17_Dynamic_Model_Routing_and_Cascading_A_Survey.pdf) |
| 18 | RouteGuard: Certifying Routing Gain in LLM Multi-Agent Systems When Complementarity Is Not Enough | p.3 定义 router、advisor correctness 和 routing gain，并给出有限样本认证框架 | 路由收益评估；任务聚类与采样敏感性 | 将认证指标扩展到成本、成功率和整任务费用 | [PDF](../pdfs/18_RouteGuard_Certifying_Routing_Gain_in_LLM_Multi-Agent_Systems_When_Complementarity_Is_Not_Enough.pdf) |
| 19 | Task- and Session-Level Model Routing: A Common-Interface Hybrid Evaluation of Four Open-Source Routers Across Four Benchmarks | p.2 要求统一接口、跨领域基准和多指标；p.3 报告按内容匹配的路由器未必超过固定层级 | 统一评测、固定层级和内容盲分配对照 | 将同样的 share-matched 对照用于任务成本路由，避免把层级比例差异误认成路由收益 | [PDF](../pdfs/19_Task-_and_Session-Level_Model_Routing_A_Common-Interface_Hybrid_Evaluation_of_Four_Open-Source_Routers_Across_Four_Bench.pdf) |

## 证据边界

- CASTER 的正确 arXiv 编号是 `2601.19793`；`2602.19793` 对应材料学论文，已从本地库移除。
- `inphotoo/earlyeval` 的当前 README 实际展示 RouterBench 内容，因此没有把它列为 EarlyEval 的官方代码实现。
- 论文 PDF 已下载并完成文件类型核对；逐条方法结论仍应在写论文时回到对应页码复读，不把题名或摘要当作方法证明。
