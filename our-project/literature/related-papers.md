# 模型路由与 KV 缓存相关论文表

整理范围：围绕“任务级成本感知的模型与推理档位路由”，并纳入最直接的 KV 缓存、Agent 执行和编排相关工作。论文定位依据标题、摘要和可获得的正文内容整理；“与你的关系”用于界定研究边界，不等于完整的文献优先权结论。

## 一、最直接相关

| 论文 | 时间 / 来源 | 研究对象 | 核心做法 | 与你的方案的关系 |
|---|---|---|---|---|
| [Unified AI Gateway: A Framework for Joint Model Routing and KV Cache Management](https://arxiv.org/abs/2609.06940) | 2026-09 / arXiv | 端—边—云 AI Gateway | 请求级联合选择模型、执行位置和 KV 缓存动作；覆盖直接复用、跨模型映射、传输、压缩、边缘 prefill 和重新 prefill；用解析仿真评估 TTFT 与输入成本 | 最接近的系统框架。它把缓存状态和模型选择放在一起，但目标是延迟/输入成本/资源约束下的系统联合决策；没有建立“预计完成轨迹数 × 单次成本 × 成功概率”的任务级路由，也没有验证在线模型路由器 |
| [InfraMind: Infrastructure-Aware Multi-Agent Orchestration](https://arxiv.org/abs/2606.11440) | 2026-06 / arXiv | 多 Agent 编排 | 在 Agent step 观测模型队列、KV cache 利用率和延迟，再决定模型与推理深度；采用分层受限 MDP 与强化学习 | 与你的缓存状态路由和 Agent 场景相邻；它偏基础设施状态与在线编排，你偏任务完成成本、调用轨迹和质量—成本权衡 |
| [Serving agentic workloads at scale with vLLM x Mooncake](https://vllm.ai/blog/2026-05-06-mooncake-store) | 2026-05 / 工程报告 | 长程 Agent 服务 | 分离 prefill/decode，并利用 Mooncake Store 管理长上下文 KV 状态 | 为你的缓存实验提供系统背景和长程 Agent 场景；没有提出任务级模型选择方法 |

## 二、模型路由与任务级成本

| 论文 | 时间 / 来源 | 研究对象 | 核心做法 | 与你的方案的关系 |
|---|---|---|---|---|
| [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963) | 2023-10 / NeurIPS 2024 | 查询级模型选择 | 先用小模型生成，再依据自验证结果决定是否调用大模型 | 代表“查询难度/置信度”路由；缺少完成任务所需调用次数和缓存状态 |
| [Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing](https://arxiv.org/abs/2404.14618) | 2024-04 / ICLR 2024 | 查询级路由 | 估计不同模型的质量差距，在质量约束下分配查询 | 与你的质量—成本约束相近；粒度仍是单次查询，未刻画长程任务轨迹 |
| [FrugalGPT: How to Use Large Language Models While Reducing Cost](https://arxiv.org/abs/2305.05176) | 2023-05 / 论文 | 级联与模型组合 | 通过模型级联、提示优化和选择器降低调用费用 | 说明成本感知路由已有成熟主线；你的差异要落在任务完成成本和轨迹预测，而不是再做一个普通选择器 |
| [RouteLLM: Learning to Route LLMs with Preference Data](https://arxiv.org/abs/2406.18665) | 2024-06 / 论文 | 偏好驱动路由 | 用人类偏好数据训练路由器，在质量与费用之间切换模型 | 代表偏好/质量信号路由；没有显式建模调用次数、失败重试和任务总成本 |
| [Route-to-Reason: Efficient LLM Routing for Reasoning Tasks](https://arxiv.org/html/2505.19435v1) | 2025-05 / arXiv | 模型与推理策略选择 | 联合选择模型和推理策略，面向推理任务控制成本与效果 | 与“模型 × 推理档位”直接相关；你的工作需要进一步证明任务级轨迹成本是额外且必要的信号 |
| [TRACE-Router](https://arxiv.org/abs/2607.22465) | 2026-07 / arXiv | 任务级在线路由 | admission 时 contextual UCB 选模型并 pin 整条轨迹；延迟 reward=(acc, latency) | **任务级粒度最近邻**；不做事前成功/token/$ 预测，无 effort 轴，质量以标量化偏好表达 |
| [SWE-Router](https://arxiv.org/abs/2607.00053) | 2026-06 / arXiv | SWE Agent | 弱模型跑 K 步后按部分轨迹 continue/escalate；Route-AUC 0.780 | 非 k=0 事前；c_i 视为常数；Table 1 显示更强模型 $/success 更高（与“成本反转”方向相反的证据） |
| [TACIT-Switch](https://arxiv.org/abs/2608.27911) | 2026-08 / arXiv | 多环境 Agent | 自适应时点一次性 cheap→strong handoff；max 成功 s.t. 预算 | 约束方向与“质量约束下最小成本”对偶；需 teacher 删失标注 |
| [TwinRouterBench](https://arxiv.org/abs/2605.18859) | 2026-05 / arXiv | Agent 路由评测 | 步级前缀 tier 分类 + SWE-bench Verified 动态轨 realized spend | 最贴近的公开评测协议；标签来自执行回放，非事前总成本预测 |
| [Route-to-Reason](https://arxiv.org/abs/2505.19435) | 2025-05 / WWW 2026 | 推理任务 | 联合选模型×推理策略，预测 token 成本代理 | 与“模型×推理档位”直接相关；非 API reasoning.effort，无整任务美元 |

## 三、多 Agent 编排与模型分配

| 论文 | 时间 / 来源 | 研究对象 | 核心做法 | 与你的方案的关系 |
|---|---|---|---|---|
| [MASS: Multi-Agent System Search](https://arxiv.org/abs/2502.02533) | 2025-02 / ICLR 2026 | 多 Agent 结构搜索 | 搜索提示词、构建块和工作流连接方式 | 适合作为“结构固定、模型选择未纳入”的编排参照；你的主线可以暂时脱离结构搜索，专注在线路由 |
| [NOMA: Multi-Agent System Optimization](https://arxiv.org/abs/2512.11001) | 2025-12 / arXiv | Agent 系统联合优化 | 联合考虑拓扑、模型和执行引擎 | 说明模型分配已进入部分编排工作；你的差异应放在运行时任务级成本预测与动态选择 |
| [AgentOpt](https://arxiv.org/abs/2604.06296) | 2026-04 / arXiv | 固定角色的模型池选择 | 为不同 Agent 角色选择模型，比较成本和任务效果 | 与模型分配相邻，但更偏静态角色配置；你的问题是同一任务执行过程中如何按预期完成成本动态选择 |
| [EvoMAS](https://arxiv.org/abs/2602.06511) | 2026-02 / arXiv | 多 Agent 配置进化 | 在结构化配置中搜索 backbone、角色和协作方式 | 适合作为离线模型分配参照；没有直接回答在线任务级成本反转 |

## 四、KV 缓存与服务系统背景

| 论文 / 系统 | 时间 / 来源 | 研究对象 | 核心做法 | 与你的方案的关系 |
|---|---|---|---|---|
| [LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference](https://arxiv.org/abs/2510.09665) | 2025-10 / arXiv | KV 缓存层 | 在推理引擎之外管理 KV 缓存的存储、复用和移动 | 提供缓存复用基础设施；不负责模型选择 |
| [Mooncake: Trading More Storage for Less Computation](https://www.usenix.org/conference/fast25/presentation/qin) | 2025 / FAST 2025 | KV-centric 服务架构 | 以分布式 KV 存储换取更少的重复计算 | 支撑长上下文服务与缓存复用；你的方案可把它作为缓存可观测实验底座 |
| [KVFlow: Efficient Prefix Caching for Large Language Model Serving](https://arxiv.org/abs/2507.07400) | 2025-07 / arXiv | 前缀缓存调度 | 管理请求与缓存块的调度关系，提高复用率和服务效率 | 解决缓存生命周期与调度问题；不回答缓存状态如何改变模型选择 |
| [TokenDance: Unified KV Cache Management for Multi-Agent Workflows](https://arxiv.org/abs/2604.03143) | 2026-04 / arXiv | 多 Agent 缓存生命周期 | 面向多 Agent 工作流进行 KV 缓存保存、传输和复用 | 与你的补充场景有关；关注缓存管理，不以任务级成功成本为核心目标 |
| [CacheGen: KV Cache Compression and Streaming](https://arxiv.org/) | 2024 / 论文条目待补 | KV 压缩与传输 | 压缩并流式传送 KV 状态，降低移动开销 | 可用于估计切换和缓存准备费用；当前本地材料未保留完整出处，正式引用前需补全 |

## 五、对你的论文定位的直接启示

| 维度 | 目前最稳妥的表述 |
|---|---|
| 核心问题 | 单次价格、单步质量和最终完成成本可能出现排序差异，长程 Agent 任务尤其明显 |
| 方法 | 预测候选模型/推理档位的成功概率、调用轨迹长度和实际费用，再进行任务级路由 |
| 关键机制 | 成本反转：标价更高的模型可能凭借更高成功率或更短轨迹降低每个已解决任务的平均费用 |
| 与华为论文的边界 | 华为工作关注模型、执行位置和 KV 缓存动作的系统联合；你的主线关注任务完成成本的动态模型选择。缓存可以作为条件变量或补充实验，不宜继续承担全部论文主张 |
| 需要避免的表述 | 在未完成系统检索前，不宜直接写“首篇”“完全没人做过”；应写成限定范围的差异，并逐项给出实验依据 |

## 华为论文的本地证据

- 本地 PDF：[unified-ai-gateway.pdf](papers/unified-ai-gateway.pdf)
- 本地文本抽取：[unified-ai-gateway.txt](papers/unified-ai-gateway.txt)
- 论文明确描述 Global Control Plane 在请求时联合选择目标模型、执行位置和 KV 缓存动作。
- 论文的实验是八类工作负载上的解析仿真，报告 TTFT 加速约 1.25×–13.28×、输入成本收益约 1.20×–6.16×；这些数字反映其设定下的模型结果，不等同于真实在线路由器的实测收益。
- 论文把缓存命中、跨模型映射、传输、压缩、边缘 prefill 和目标侧重新 prefill 纳入候选路径；任务级“预计轨迹数 × 单次费用 × 成功概率”不在其核心公式中。
