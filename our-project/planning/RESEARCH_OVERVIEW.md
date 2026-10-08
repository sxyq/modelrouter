# ModelRouter · 研究总纲、相关工作与方法设计

> **版本 v0.3｜研究基线：2026-10-09**
>
> **目的**：为论文与开源实现建立可检验的研究命题、近邻工作边界、方法设计和实验协议。项目实际进度见 [PROJECT_STATUS.md](PROJECT_STATUS.md)，跨 Agent 决策记录见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据纪律**：论文/官方材料、现有仓库文献、E0 Agent 审计、我们提出的假设分开表述。**未运行的实验不得写成结果；“未见完全相同方案”不等于“首创”。**

## 摘要

ModelRouter 研究长程单 Agent 与多 Agent 工作流中的**状态感知、任务级模型与推理强度联合路由**。在 Agent 的每个合法决策边界，系统从真实运行时获取任务进度、上下文、工具、验证/恢复、协作、缓存连续性、时间预算及服务商可用性，构建当前可执行的 `(model, reasoning_effort)` 候选集合，并由**单一 Kev-4B 风格决策模型**选择下一动作。

与仅比较一次 API 请求的价格不同，研究关注动作对**整任务成功、后续执行路径、成本剩余量和缓存/会话连续性**的延迟影响。通过可重放 Agent Harness、真实 usage 账本、任务终局判定和同状态分支实验验证质量—成本收益。

**研究贡献须通过实验证明，而不是由状态字段数量或架构图本身成立。**

## 1. 研究问题和形式化

给定任务 `T`，在步骤 `t` 的路由器观测 `s_t`，从可用候选 `A_t` 中选择 `a_t=(m_t,e_t)`，并满足约束集合 `G_t`。路由器不决定工具的语义正确性，Agent Harness 继续执行任务并产生下一状态与终局 `Y`。

- `s_t`：决策前已知的 Agent Runtime 观测与派生信息。
- `A_t`：带 provider/model/revision/effort/capability/price/context 的动态动作列表。
- `G_t`：可用性、预算、上下文、隐私、权限、工具循环/会话连续性等硬约束。
- `a_t`：一个真实可执行的候选动作。
- `Y`：终局任务是否成功、质量分、整任务费用、时延及执行轨迹。

### 1.1 任务级目标

主评价是**在质量与安全约束下减少整任务成本**，不是“每次都选便宜模型”。可以将策略目标表达为：

~~~text
minimize_policy   E[ C_episode | policy ]
subject to        P(task_resolved | policy) >= quality_floor
                  every action in valid_candidates(state)
                  privacy / budget / continuity constraints
~~~

任务级 `C_episode` 是从开始到终止的真实调用与执行费用；可同时报告 `cost_per_resolved = total_cost / number_resolved`、成功率与 Pareto 曲线。训练中的 `cost_to_go(t)` 是决策点后观察到的剩余费用，不等于尚未执行动作的真实反事实值。

**边界**：主路由器是 Model × Effort 选择器，不等于 vLLM worker 负载均衡器、Agent 拓扑搜索器或跨模型 KV 转换系统。相关技术可用于状态和硬约束，但不能混淆贡献。

### 1.2 Admission-only 与运行时路由

- **Admission-only**：任务开始时 `t=0` 选一次配置并固定全程；作为历史方案和强基线。
- **Runtime state-aware**：在允许的模型调用边界根据新状态重新选择；这是当前主线。
- **Safe switch**：工具循环或 provider 有状态约束时，不能任意换模型；必须通过 hard constraint 或安全 reset 边界执行。

## 2. 真实 Agent 状态表示

| 状态组 | 决策前可观察内容 | 典型数据源 | 需防止的错误 |
|---|---|---|---|
| Task/Subtask | 类型、阶段、进度、依赖、剩余工作估计 | Harness task graph | 把最终 resolved 作为当前进度 |
| Agent/Coordination | 当前角色、活跃子 Agent、handoff、协作轮次 | Agent runtime | 用未来 handoff 预测当前动作 |
| Context/Memory | 输入 token、窗口占用、增长、压缩次数、摘要状态 | provider usage / context manager | 读取未来总 token |
| Tool/Environment | 最近工具类型、错误、重试、环境变化 | tool trace | 事后测试结果回流 |
| Verification/Recovery | 当前测试失败、验证结果、失败连续性、恢复阶段 | CI / tests / evaluator | 将最终评测标签混入状态 |
| KV Cache/Continuity | 当前物理模型/会话、reported cached tokens、估计 prefix overlap、切换成本、锁 | provider/harness | 假定跨模型 KV 可直接共享 |
| Temporal/Execution | 已走步数、elapsed time、剩余预算、截止时间 | scheduler/ledger | 使用未来完成时长 |
| Provider/Availability | model/effort 能力、限流、延迟观测、上下文上限、价格版本 | capability registry | 选择不存在的配置 |

**工程原则**：State Builder 应确定性、可测试、可回放；状态字段必须记录观测时刻与来源。敏感文本可由脱敏统计或本地 embedding 替代，是否保留原文必须由数据许可决定。

## 3. 动态候选动作与硬约束

### 3.1 Candidate Registry

每个候选至少包括：

- `provider`、`model_id`、`revision`、`effort_label`（可为 null/unsupported）；
- 支持的上下文长度、工具调用、结构化输出、流式能力；
- 实际可用状态、并发/速率限制、部署位置；
- 输入/输出/缓存读取/写入的价格快照与单位；
- 物理缓存会话/路由 sticky 规则；
- capability evidence 和最后核验时间。

**不能把不同 provider 的 low/medium/high/xhigh 当作天然等间距数值，也不能把不支持 effort 的 Ollama 模型虚拟扩成多个动作。** 训练可学习语义，但必须保留 provider-specific 标识。

### 3.2 硬约束优先于模型偏好

先执行合法性过滤，再调用 Kev-4B 选择。预算、权限、隐私、上下文、可用性和安全连续性锁都属于硬约束；不能靠模型“学会遵守”。无合法动作时应有明确 fail-closed/fallback 策略并记录原因。

### 3.3 缓存/切换代价

- `reported_cache_read_tokens`：provider 实际回报的缓存读取；**物理事实**。
- `estimated_prefix_overlap`：路由器可估计的文本/前缀重合；**估计值**。
- `cache_write_tokens`、`cache_age`、`session_affinity`、`switch_penalty_estimate` 分开记录。
- 缓存命中率依赖 provider、模型、前缀、TTL、部署实例和工具循环状态；**不假定 KV 跨模型、跨后端可直接迁移**。
- 缓存带来的收益必须计入真实任务账本，并对比无缓存状态或无 sticky 规则的消融。

## 4. 单一 Kev-4B 主路由器

### 4.1 为什么选择 Kev-4B

[Kev-4B 官方模型卡](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md)确认：

- 基座：`Qwen/Qwen3.5-4B-Base`，32 层（24 Gated DeltaNet + 8 full attention）。
- 冻结基座 + LoRA（rank 16、alpha 32，约 33.8M 可训练参数）+ pointer head。
- 输入：一个 state 文档 + 类型化问题及候选选项；输出：选项概率分布，**非自由文本生成**。
- 以 prefill-only 方式运行；每个问题独立 row，state 可共享；不能假定任意增加问题/候选不增加开销。
- 官方模型卡注明 Kev 1.0 权重修订；早期 `@qwen3` 是旧代 checkpoint，不应混用。
- 官方 serving 显存约 14.3GB；训练 H100 的显存/时间数据**不能直接外推到 A6000**。
- 模型可服务长状态，但**官方经实验验证的有效上下文长度为 8,192 tokens**；不得把 65k serving 支持写成同等质量已验证。

因此 Kev-4B 是**合理的起点**，不是已证明最优。A6000 的精度、延迟、候选规模敏感性、显存和 LoRA 训练仍需本项目实测。

### 4.2 计划架构

~~~text
Agent Runtime (task / tool / verifier / usage / session)
        |
Deterministic State Builder + provenance
        |
Candidate Registry -----> Hard Constraint Filter
        |                           |
        +------ valid (model, effort) actions
                                    |
                          Single Kev-4B Router
                                    |
                         selected valid action
                                    |
                   Agent Harness + provider adapter
                                    |
               usage ledger + trajectory + final resolved
                                    |
                 evaluation / controlled data collection
                                    |
                  supervised continuation fine-tuning
~~~

可考虑成功概率、剩余成本分位数、切换风险等**辅助任务**，但必须先有可信监督信号和消融证据；不为复杂度而强制增加 GNN、RL、Bandit 或多个预测头。

### 4.3 训练策略（尚未实施）

1. 从真实 Harness 产生带决策前状态的样本；
2. 构建候选集合和合法性标记；对 option 顺序做随机化防位置偏差；
3. 仅用可观测动作的真实终局与 cost-to-go 监督已选动作的 outcome 模型；未选动作保持 missing；
4. 若要学习跨动作选择，优先用**同状态分支 rollout**获取配对动作结果，或用有明确假设的离线策略估计并报告偏差；
5. 使用官方 Kev continuation/LoRA 入口做小规模 smoke test，再决定正式训练超参；
6. 冻结 held-out task 集与 calibration split，报告 Brier/ECE、任务级质量成本指标和候选泛化。

**不能**将一个行为策略采集的单条轨迹直接复制为所有候选动作的监督标签。

## 5. 数据策略

### 5.1 三层数据

| 层 | 来源 | 可以做什么 | 不能做什么 |
|---|---|---|---|
| 生产调用先验 | CCH 聚合、Blog GPT 明细 | 价格/Token/effort/cache/latency 分布，部署可行性 | 推断未选模型在同任务的 resolved |
| 开放 Agent 轨迹 | Open-SWE-Traces、SWE-Gym、TwinRouterBench 等 | 任务/步骤/工具/终局结构、离线协议 | 假定存在完整 Model × Effort 成对反事实 |
| 本项目受控轨迹 | 固定 Harness、任务快照、不同合法动作分支 | 直接比较动作对后续任务成功与成本影响 | 无预算、无固定 continuation 的无控制对比 |

数据使用前固定版本、任务 ID、许可证、价格快照、模型版本、工具环境与时间窗口。

### 5.2 最小 Schema

~~~text
Task: task_id, task_type, repo_or_env_id, split, success_evaluator
Episode: episode_id, task_id, agent_harness_version, seed, start/end
Decision: episode_id, step_id, observed_at, state_snapshot,
          candidate_actions, hard_constraints, behavior_policy,
          selected_model, selected_effort
Usage: provider_raw_usage, input_tokens, output_tokens,
       reported_cache_read_tokens, cache_write_tokens,
       estimated_prefix_overlap, cost_value, cost_currency,
       price_catalog_version, latency_ms
Outcome: tool_status, verifier_status, final_resolved,
         episode_cost, episode_latency, observed_cost_to_go
Provenance: source, schema_version, model_revision, privacy_flags
~~~

**成本计量**：输入、缓存读取、缓存写入、输出、reasoning tokens 的收费规则按 provider 区分；使用带日期/版本的价目表。没有可靠 USD 单价时保留原单位，不强行换算。

### 5.3 防泄漏

- 按 task/repository/时间切分，不能只按调用行随机切分；
- 同一任务的全部轨迹前缀不能跨 train/validation/test；
- 训练集构造必须以 `observed_at` 截断可见信息；
- 不能用最终总 token、最终 resolved、后续失败/修复次数作为决策前特征；
- 对跨模型、跨 Harness、跨任务类别和动态候选池设置外推测试；
- 独立校准集，不在测试集上调阈值、选超参或重写任务；
- 审计 benchmark 污染和模型先前见过的代码库。

## 6. 相关研究与差异定位（截至 2026-10-09）

| 工作 | 公开来源 | 核心内容 | 与本项目差异/需要对照 |
|---|---|---|---|
| FrugalGPT | https://arxiv.org/abs/2305.05176 | 级联/成本优化 | 以请求级为主；作为经济性基线 |
| RouteLLM | https://arxiv.org/abs/2406.18665 | 强弱模型请求路由 | 缺真实长程状态与任务后续影响 |
| Route-to-Reason | https://arxiv.org/abs/2505.19435 | 模型与推理策略联合选择 | Model × Effort 近邻，需对照 Agent 状态与任务级成本 |
| TwinRouterBench | https://arxiv.org/abs/2605.18859 | 静态前缀 + 动态 SWE-bench 任务级路由评测 | **重要评测基线**；已覆盖真实 Agent 逐步路由，不能声称这一点新 |
| Harness-Native Agentic Routing | https://arxiv.org/abs/2607.11399 | Harness 状态、数据飞轮、冷启动 ranker | **最直接问题近邻之一**；本项目须证明 Kev + effort + cache/cost-to-go 的额外价值 |
| ProgRouter | https://arxiv.org/abs/2608.25992 | 多 Agent 进度驱动的在线选择 | 已覆盖状态/进度/成本；需正面比较 |
| HM-ROUTER | https://arxiv.org/abs/2609.32213 | 联合选择模型与 Harness，组合泛化 | 本项目不是 Harness 路由；但可借鉴候选组合泛化评测 |
| Unified AI Gateway | https://arxiv.org/abs/2609.06940 | 模型、位置、KV 处理联合系统决策 | 系统/请求级 KV 优化；本项目是任务级 Agent 模型决策 |
| vLLM Session-Aware Agentic Routing | https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-06-02-session-aware-agentic-routing.md | 会话锁、工具循环与缓存切换成本 | 连续性工程约束与缓存观测重要参考 |
| NVIDIA Dynamo KV-aware Routing | https://docs.dynamo.nvidia.com/dynamo/knowledge-base/concepts/system-architecture/kv-aware-routing | worker 放置、KV 重叠和负载 | 不等于跨模型 Model × Effort 选择 |
| EarlyEval | https://arxiv.org/abs/2609.02783 | 轨迹前缀成败预测、早停与防泄漏协议 | 借鉴 task split / prefix split / 校准；不是主路由器 |
| LLMRouterBench | https://github.com/ynulihao/LLMRouterBench | 多模型请求级路由数据与评价 | 适合能力先验，缺完整 Agent 任务轨迹 |
| Kev-4B | https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md | 开放的 typed decision/pointer 模型 | 作为模型实现底座，不可将原架构归为本项目发明 |

**重要学术风险**：2026 年多篇工作已研究 harness state、Agent step routing、质量—成本权衡。新意不能表述为“首次在 Agent 中考虑状态”或“首次研究任务级成本”。合理主张应是**联合 Model × Effort、可执行动态候选池、缓存/连续性与延迟任务回报的统一决策和严格验证**，并通过消融和最近邻基线支持。

### 6.1 旧研究报告与当前方法的关系

`our-project/literature/report.md`（2026-09-15）重点研究 **admission-time 事前预测总费用分布**；`IMPLEMENTATION_RESEARCH.md` 给出 GBDT/MLP MVP。它们仍是高价值的**历史证据和 admission-only 对照设计**。当前主方法已转向**运行时状态 + Kev-4B**。不要直接复制旧报告中“KV 缓存延后、动态 handoff 延后”作为最新方法决策；但可以保留其关于成本重尾、分位数、泄漏和评测偏差的警示。

## 7. 可证伪的研究假设

| ID | 假设 | 对照/验证 |
|---|---|---|
| H1 | Agent 当前运行状态优于 task-only 路由 | 完整状态 vs task-only，固定候选/预算 |
| H2 | Model × Effort 联合选择优于 Model-only | 允许 effort 变化的真实动作池；控制额外候选优势 |
| H3 | 任务级回报目标优于单次调用价格目标 | cost-to-go/终局质量 vs one-step cost |
| H4 | 缓存与连续性状态减少无效切换和总成本 | 完整 vs 去 cache/sticky；报告实际 cache hits |
| H5 | 单一 Kev 决策器能处理动态候选池 | unseen candidates / option order / provider outage |
| H6 | 协作、验证和恢复状态在多 Agent/失败场景提供额外收益 | 去除对应状态组，按任务类型分层 |
| H7 | 状态构建和路由开销小于节约的任务成本 | 路由延迟/显存/调用成本计入整任务 |

所有假设均**未由本项目实验验证**。若 H1–H7 不成立，需如实报告并缩小主张。

## 8. 实验设计

### 8.1 顺序

1. **E0**：审计代码/数据/服务器（Execution 报告已完成）。
2. **E1**：最小 Schema、capability registry、hard constraint、usage ledger、可测试 Router 接口。
3. **E2**：固定 Agent Harness 与自动任务终局 evaluator；固定模型/规则/sticky 基线。
4. **E3**：从相同状态快照受控分支，收集成对动作结果。
5. **E4**：Kev-4B LoRA/continuation 训练与严格独立测试。
6. **E5**：消融、候选池变化、跨任务/模型泛化、统计置信区间和论文图表。

### 8.2 最小对照与公平性

- **固定策略**：always-cheap、always-strong、随机但能力匹配。
- **无状态策略**：task-only、仅静态文本/模型能力。
- **工程策略**：rule-based、sticky/cache-aware。
- **学习策略**：MLP/LightGBM、admission-only predictor。
- **主方法**：单一 Kev-4B 完整状态与联合动作。

相同任务、工具权限、候选池、时间/费用预算、终局 evaluator、价格快照与后续 continuation policy。**若某个 baseline 无法处理动态候选池，应明确记录不适用或适配方式**。

### 8.3 受控分支与成本预算

- 从同一可恢复状态 `s_t` 选择两个真实合法动作；
- 尽量固定工具环境、下游策略、seed、模型版本和预算；
- 记录分支失败、超时、无法复现、污染、模型服务变化；
- 5 任务 pilot 后才决定 30×2×2 等扩展规模；
- 若无法可靠恢复完全相同的状态，不能称为严格反事实实验；
- 付费 API、服务器 GPU 长时占用和模型下载必须单独审批。

### 8.4 评价指标与不确定性

| 指标 | 定义/警示 |
|---|---|
| Task success | 终局自动测试或环境断言，不是 HTTP 成功 |
| Total task USD | 实际 usage × 版本化价目；缺计费字段需注明 |
| USD / resolved | 组内总 USD / 成功任务数；零成功要单独处理 |
| Pareto frontier | 在成功率、总成本、延迟之间比较 |
| Decision overhead | Router 本身耗时、显存、推理开销 |
| Cache effect | 实际 cached tokens、模型切换次数、cache write |
| Reliability | 失败恢复、重试、工具错误、不可用 fallback |
| Generalization | 不同任务类别、未见模型/effort、动态候选池 |

统计使用任务层配对 bootstrap/分层分析，报告样本数、CI、seed 和失败案例。不要只报告均值、挑最好 seed 或仅展示成功任务的低成本。

## 9. 当前待解决的研究难点

1. **监督信号缺失**：已有 CCH/Blog 数据不能直接训练 state-aware router。
2. **延迟效应与混杂**：当前动作影响未来轨迹；观测 cost-to-go 来自行为策略，不能冒充所有动作的因果标签。
3. **受控执行代价**：多模型×effort×任务×seed 的 API/算力开销需要分阶段控制。
4. **effort 语义不统一**：跨服务商/本地端点需保留原始能力声明。
5. **缓存真实可测性**：prefix overlap 与物理 KV 命中不同；连续性安全边界先于学习选择。
6. **Kev 泛化与延迟**：预训练决策任务不保证 Agent 路由适配；必须校准和测试。
7. **论文新意拥挤**：Harness-Native、ProgRouter、TwinRouterBench 已是强近邻；必须有直接对照和明确独立贡献。
8. **隐私与开源复现**：私有 Agent 日志不能直接公开；需可发布的脱敏 Schema、公开任务和复现脚本。

## 10. 论文贡献的暂定表达（待结果支持）

- **问题/协议**：在真实 Agent Runtime 的可观察状态和硬约束下，联合选择 Model × Effort，面向整任务成功和总成本。
- **方法**：单一 Kev-4B 风格路由器与动态候选、会话连续性/缓存状态的组合，避免额外模型堆叠。
- **实验**：以任务终局和真实记账为准的可重放评估、同状态分支、候选池变化和消融。
- **分析**：明确哪些状态/动作/缓存条件有收益，何时不值得路由，并报告失败情形。

**不得提前使用“显著优于”“首次提出”“达到 SOTA”等结果性表述。**

## 11. 文献与材料导航

- 项目旧综合调研：[`our-project/literature/report.md`](../literature/report.md)
- 相关论文表：[`related-papers.md`](../literature/related-papers.md)
- Kev/Jev 调研：[`jev-model-research.md`](../literature/jev-model-research.md)
- 防泄漏证据：[`findings/F4.md`](../literature/findings/F4.md)
- 历史实现规划：[`IMPLEMENTATION_RESEARCH.md`](IMPLEMENTATION_RESEARCH.md)
- 官方 Kev：[GitHub](https://github.com/jaredpalmer/kev) · [Kev-4B Model Card](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md)
- Agent 轨迹：[NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces)
- 任务级评估：[TwinRouterBench](https://github.com/CommonstackAI/TwinRouterBench)

## 12. 持续更新规则

- **Planning**：新研究决定、文献证据、实验假设改变时，更新本文件并同步 Memory/Status。
- **Execution**：每个任务完成后提交真实实验结果、代码/数据版本、失败与负例；不得只写“实验已完成”。
- **版本纪律**：每次 Git commit/PR 附 Task ID；修改研究方法需在 Memory Decision Log 记录替换原因，Status 更新阶段与阻塞。
- **公开安全**：仅公开可审阅的抽象状态、脱敏统计、代码与公开文献；不泄漏私人主机和原始会话。
- **文档更新频率**：每个任务/决策事件同步；不是自动后台刷新。
