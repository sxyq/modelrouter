# ModelRouter · 研究总纲、相关工作与方法设计

> **版本 v1.3｜研究基线：2026-10-09（第一批实验设计决策已记录；H1–H7 未变）**
>
> **目的**：为论文与开源实现建立可检验的研究命题、近邻工作边界、方法设计和实验协议。项目实际进度见 [PROJECT_STATUS.md](PROJECT_STATUS.md)，跨 Agent 决策记录见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据纪律**：论文/官方材料、现有仓库文献、E0 Agent 审计、我们提出的假设分开表述。**未运行的实验不得写成结果；“未见完全相同方案”不等于“首创”。**

## 摘要

ModelRouter 研究长程单 Agent 与多 Agent 工作流中的**状态感知、任务级模型与推理强度联合路由**。在 Agent 的每个合法决策边界，系统从真实运行时获取任务进度、上下文、工具、验证/恢复、协作、缓存连续性、时间预算及服务商可用性，构建当前可执行的 `(model, reasoning_effort)` 候选集合，并由**单一 Kev-4B 风格决策模型**选择下一动作。

与仅比较一次 API 请求的价格不同，研究关注动作对**整任务成功、后续执行路径、成本剩余量和缓存/会话连续性**的延迟影响。通过可重放 Agent Harness、真实 usage 账本、任务终局判定和同状态分支实验验证质量—成本收益。

**研究贡献须通过实验证明，而不是由状态字段数量或架构图本身成立。**

**E-DESIGN 负责人于 2026-10-09 已确认**：Q-001=A（直接使用公开真实 Coding Benchmark，不先自建独立合成任务集）、Q-002=B（商业 API + 本地开源混合动态动作池）、Q-003=B（分阶段预算原则，本地模型推理费用无预设固定上限，商业 API 按模型限额）。具体 benchmark/evaluator、型号/effort 能力、API 金额与全部实际资源许可未冻结；本地 GPU 使用与物理成本仍须单独记录、授权。详见 [EXPERIMENT_QA.md](EXPERIMENT_QA.md)。

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

**2026-10-09 Q-007 外部证据更新（仅方案，未训练）**：负责人要求第一学习阶段从 A（公开 Agent 轨迹）开始，不代表后续仅用公开数据。NVIDIA [Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) 官方卡片记录软件工程轨迹、消息/工具、任务 ID 与 resolved，并允许 SFT；可用于决策前状态及已执行动作条件下的结果学习，**不能直接提供所有 Model×Effort 候选的反事实与物理 KV 缓存账本**。[CMU agent_trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) 含多模型/benchmark/奖励，训练许可待核；[SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) 为真实任务与环境；[AgentSuite trajectories](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) 可研究异构模型配置，但 thinking on/off 不等于所有 effort；[Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) 明确禁止训练、蒸馏和微调，仅能分析。

**训练数据要求**：八组状态均纳入可选 Schema，字段标记 observed_at、真实值/估算值和缺失状态；同任务所有前缀与多模型记录统一 train/val/test 侧，未来最终结果/标准补丁不得做决策前特征。阶段 A 可以学观察性 P(resolved | 前缀、已执行动作、当时行为策略)，有可信账单才学已观察的剩余费用；真正 action choice 胜负需未来同状态合法动作比较标签，不能伪造未观察结果。完整变量矩阵与阶段学习建议见 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) Q-007。

### 5.1a Q-007-R1 数据分层与训练加工研究（2026-10-09）

训练数据分成 Agent 轨迹（Open-SWE-Traces、SWE-smith-trajectories）、静态任务-模型结果（LLMRouterBench、RouterBench、TwinRouterBench tier、Arena 双模型偏好）、缓存 usage/成本先验，以及按版本维护的厂商能力/价格/政策规则。LLMRouterBench/RouterBench 训练许可证未核实、CMU gated、Finding the Right Fit 禁训练。真实轨迹能学观察到的成败/成本，静态同题结果能学模型能力先验，但**不等于** Agent 同状态不同 model×effort 的反事实。

预处理：锁定来源 revision、许可和 hash → task/repo 去重与先划分后抽决策前 prefix → 八组 state + measured/estimated/missing → 合法动作与能力注册 → 已观察的成功/真实费用、静态模型评分、确定规则标签分层 → Kev typed noul/score/choice 数据视图；绝不从未来结果泄漏输入或伪造物理 KV 命中。缓存 TTL、effort 支持和价格/限流由动态外部注册表及硬约束保证，而不是依赖 Kev 参数记住。详情、来源与候选数据量见 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) Q-007-R1。此为研究方案，尚无实际训练数据。

### 5.1b Q-007-R2 多维数据来源与 Harness 边界（2026-10-09）

Mooncake FAST25 toolagent/conversation 的真实请求时间、输入/输出长度与匿名 hash 前缀是**可复用机会**，并非真实 provider cached-token 命中；只有实际 usage 属 measured，KV simulator 属 simulated，文本重叠属 estimated。BurstGPT/阿里 xMaaS 补时间服务负载，仍缺长程 Agent 的 task resolved。LoCoMo、LongMemEval / V2、MemoryAgentBench、LongBench 是 Context/Memory 候选；MARBLE、MASBench、AgentWorld 是多 Agent 协作候选。OpenSquilla Harness-Native Agentic Routing 的真正价值在于统一执行循环产出状态/选择/结果/成本数据，可研究借鉴但不新建本项目第二个 Agent 框架。

Provider registry 纳入 OpenAI、Anthropic、Google Gemini、xAI、OpenRouter、DeepSeek、阿里 Qwen/百炼、火山豆包、Moonshot Kimi、腾讯 Hunyuan/TokenHub、百度千帆、智谱 GLM、MiniMax、StepFun、硅基流动，以及 Mistral、Cohere、Together、Groq、Fireworks、自托管 vLLM/SGLang 的 Qwen/DeepSeek/GLM/Kimi 等。具体缓存/effort/TTL/价格要区分原厂 API、第三方托管与开源权重实例，保留 source verified/pending 状态，**未知不是不支持**。动态合同/模型可用性与价格在外部确定性 Registry 中生效，不由 Kev 参数固化。完整官方来源和状态见 EXPERIMENT_QA.md 的 Q-007-R2。

**当前只完成候选数据目录**：未确认所有训练许可、未处理真实数据、未确定样本数或启动任何工程/实验。

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

### 6.2 真实路由训练论文的方法链比较与后续学术写法（2026-10-09；仅研究建议）

负责人追问：数据先选/清洗/微调是否合理，其他路由论文怎么训练，Kev 与生成式微调如何区分、论文图与外部 Harness 怎样组织。**结论**：数据选择→清洗→训练是必要但不充分的三步，之前还必须定义路由决策、动作可行域、标签的实际因果/观察语义，训练后仍需受控同状态数据与 Agent 端到端验证。Q-007 仍是数据源审议阶段，以下方法**未获负责人批准执行**。

| 直接相关论文与出处 | 论文真实训练/数据流程 | 对 ModelRouter 的适用性与边界 |
|---|---|---|
| [FrugalGPT](https://arxiv.org/abs/2305.05176) (TMLR 2024) | 分析模型质量/费用后设计请求级多模型级联 | 成本/级联传统基线，不等于 Agent 全任务成本 |
| [RouteLLM](https://arxiv.org/html/2406.18665) (ICLR 2025) | Arena 成对偏好→矩阵分解/SW-ranking/BERT/causal classifier 训练；gold/judge 扩充、阈值选择及分布外测评 | 需在同任务同评价协议下形成真 model preference；训练模型不一定大；公开偏好≠长程 Agent 成功 |
| [BEST-Route](https://proceedings.mlr.press/v267/ding25d.html) (ICML 2025) | 动态选模型和重复采样计算预算 | 近邻 test-time compute，不可声称首次联合模型与计算 |
| [Route-to-Reason](https://arxiv.org/abs/2505.19435) (WWW 2026) | 共同学习 model 与 reasoning strategy 表征，预测成功/Token，按预算选动作 | **Model×Effort/推理策略联合选择直接近邻**，本项目须证明 Agent/Harness/cache 的新增效果 |
| [Budget-Aware Agentic Routing](https://arxiv.org/html/2602.21227) (2026 preprint) | always-small/large 边界 profiling → 难度分类/成本有效轨迹 → BoSFT → BoPO 在线优化 → hard budget decoding | 动态 Agent 序列决策和任务级成本最直接近邻；**不能只拿 SFT 当完整因果路由监督**；是否用 RL 尚未决定 |
| [TwinRouterBench](https://arxiv.org/html/2605.18859) (2026) | 强模型成功 Agent 轨迹→调用前缀→greedy sequential-locking 降档实验→执行验证 tier 标签→静态离线/动态真实执行两轨评测 | **标签构造近邻**；目标 tier 为固定 pool/协议下的局部估计，非任何 model×effort 的全局最优；静态 train 与正式 held-out 要隔离 |
| [OpenSquilla / Harness-Native Agentic Routing](https://arxiv.org/html/2607.11399) (2026 preprint) | Harness 状态→LightGBM 冷启动→日志 (q,h,action,trace,outcome,cost)→覆盖采样→离线/校正估计与下一代路由器；某些场景扩展 ensemble | 最直接系统设计近邻；[当前仓库 SquillaRouter docs](https://github.com/TokenRhythm/opensquilla/blob/main/docs/features/squilla-router.md) **已移除历史 self-learning/反馈提交 API**，不能把论文愿景当公开可运行训练流程 |
| [ProgRouter](https://arxiv.org/abs/2608.25992) (2026) | 多 Agent progress scoring、subtask 进展预测与动态 gate，考虑任务时间/费用 | 强对照，状态/协作/进度并非创新空白 |
| [HM-Router](https://arxiv.org/abs/2609.32213) (2026 preprint) | 联合选择 model+harness、可迁移候选表示/稀疏组合训练 | Harness 应先固定并记录，未批准训练时选择 Harness 作为新动作维度 |

**与普通生成式 SFT 的区别**：Kev 是 Qwen3.5-4B-Base 的 LoRA + pointer-head **类型化决策模型**，输入 state/questions，输出 choice/noul/score 概率而非开放文本；官方 [Kev model card](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md) 与 [标注格式](https://github.com/jaredpalmer/kev/blob/main/skills/kev-finetune/references/data-format.md) 有真实规则/文档/分类标注、增量 replay、温度校准。通用微调脚本单条状态/问题+选项 <=2048 tokens（模型长上下文 serving 能力不等于 trainer 限额），原始 Agent 长历史必须在数据层维护，训练输入只用**决策前压缩快照**。不能把 Kev 当 Jev 原厂公开权重，不能将仅使用 LoRA/QLoRA/DPO 当论文新贡献；这些已有 [LoRA ICLR 2022](https://arxiv.org/abs/2106.09685)、[QLoRA NeurIPS 2023](https://arxiv.org/abs/2305.14314)、[DPO NeurIPS 2023](https://arxiv.org/abs/2305.18290)。

**建议科学主流程（未批准）**：
1. 问题/决策接口：task-success 质量下限约束下最小整任务成本；约束先过滤真实可执行 (model, effort)，保存 provider/effort/price/cache snapshot。
2. 许可/来源/去重与 Benchmark 测试隔离；分源标签构造：Agent 已执行动作 outcome、静态 model preference、Cache reuse potential / 模拟与 measured tokens、确定性 rules，**不同事实不合成虚假的同状态反事实**。
3. **先建立最小 Harness state/usage/checkpoint 接口与可复核 evaluator 计划**（不必此时运行），明确调用前快照、tool/environment/version/budget、terminal resolved 和整任务记账；避免训练数据 schema 与未来 serving 错位。
4. 比较成本低的 rule/task-only/GBDT/MLP 初始基线与预训练 Kev 基线之后，拟定单一 Kev-4B LoRA continuation：观察条件结果辅助→经过许可的同题能力/成本比较+缓存复用任务→未来严格同状态真实候选数据才做最终运行时 choice→概率校准。
5. 用独立任务级 Agent end-to-end、强固定模型/弱固定模型、task-only、规则/cache-aware、GBDT/MLP、近邻论文等验证 H1–H7；报告成功率、任务级费用、恢复次数、真实缓存命中、路由延迟、冷启动/新候选/跨仓库泛化、可靠性和消融。不能仅给离线分类准确率。

**训练损失原则**：缺标签的任务 head 需 mask；observer success 仅代表实际 action+历史 continuation 下 outcome，不直接监督未见 action；静态 preference 对应 request-level，不等于动态 Agent；若以后做 policy/off-policy correction，必须实际记录 action 采样概率及探索覆盖，无 propensity 不能借名套用 IPS/DR。任务/仓库/来源 group split 在抽 prefix 前进行，并控制长轨迹对 loss 的过度加权。**Kev 只是科学研究的可替换建模选择，必须与简单排序/分类 baseline 公平比较。**

**论文方法架构建议画两张，且训练与运行闭环分开**：
- Fig. 1 系统在线推理：Agent Harness（任务、状态、工具、记忆、协作、检查点）→ 决策前八组状态快照；动态 Provider/Price/Cache Registry → 合法动作池；**单一 Kev router** → 合法 model+effort；Model Call Adapter → 国内外 API 或本地引擎；Tool/Verifier/Cost/Usage 返回 Harness 并独立记原始账。Memory summarization 是 Harness/Agent 职责，Kev 并不负责生成文本摘要。
- Fig. 2 离线学习：不同源(Agent trajectory、静态同题 model outcomes、缓存 workload、政策规则)→来源权利/时间与任务拆分→独立监督真值→typed state+questions→ Kev LoRA/pointer 决策头→未来同状态受控比较与校准→回到 Fig. 1；未批准的数据生成/训练模块必须画为 future/planned，而非“我们已完成”。
- Fig. 3 非方法架构而是实验：成功率—整任务成本 Pareto、分布外泛化、真实 vs 模拟 cache、按状态和 effort 的消融；没有真实结果前不能画数据点或声称有增益。

**外部 Harness 优先原则**：现阶段**不造第二套 Agent 工程**；以后可先选一个可读开源基础，例如 [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) 的 coding task/run/model/trajectory interface，或 [LangGraph](https://langchain-ai.github.io/langgraph/concepts/durable_execution/) 的多 Agent/持久 checkpoint/store，先结合 Benchmark 复现/恢复需求**最终只批准一个主执行框架**。统一 ModelCall hook 之前构造 StateSnapshot 并执行 hard filter / Kev choice；之后由原 Harness 持有 context summary、multi-agent coordination、tools/verifier、memory/usage、task_budget 与环境恢复。需要严格同状态 fork 时不只恢复消息，还需 repo/worktree、容器/工具、随机性、价格/模型快照和 continuation policy；否则不得自称 paired causal comparison。论文里的 ensemble 模式与动态 Harness 更换都不在当前已批准动作空间内。

**学术投稿纪律**：小模型微调可以构成论文组成部分，创新必须落在有效监督/序列优化/可执行约束/缓存连续性机制或可信新 benchmark，并以公平基线、组件消融、独立真实任务、费用/时延与统计检验证实；仅复制 Kev+LoRA 及拼数据不足以支撑算法创新主张。保持 E-DESIGN/Q-007 当前数据源优先，不提前解答 Q-010/Q-011 也不执行工程。

### 6.3 面向论文实验的最简执行规范与三段 Kev 微调（2026-10-09）

**执行风格按负责人本轮明确要求**：只做最小可运行科研实验，尽快产生真实数据和可检验结果。不要新增审批/冻结/哈希管理/CI/单元测试/防御性框架/双重代码入口/多版本重复清洗脚本；一个终端可看到 source、rows、epoch、step、loss、eval 和耗时。移除的是工程管理形式，不是论文上不可少的 train/test 不串集、禁止未来答案泄漏、标签有真实出处、模拟缓存不冒充实际命中和来源使用权。使用不属于本项目的计算资源或收费 API 不因去工程门禁而自动获准。

**唯一路线**：任务目标与合法动作定义 → 已登记公开源读取 → 分源最小清洗 → 同任务/仓库切分 → 决策前状态 → 可靠分类/偏好/缓存分层监督 → 已发布 Kev-4B checkpoint 的 LoRA 和 Pointer Head 领域微调 → 留出集检查和概率校准 → 复用同一个 Agent Harness 调用边界产生真实 usage/result → 同状态合法 model×effort 的可比较延续 → 动态选择精调 → 真实 Agent 总成本/成功率及消融。

**T1 领域适配**：Open-SWE/SWE-smith 只有实际执行策略条件下的 resolved，可做 observed-outcome 的 noul 监督，不能直接标注最优模型；Arena 和许可明确的 LLMRouterBench 可做同静态任务的 choice 偏好；成本 score 仅当有实际费用和统一口径时可用。Mooncake 前缀 hash 主要作为缓存复用特征/工作负载，不能直接代替 Provider 实测 cached_tokens，也不应在没有路由标签时硬塞成 choice。Provider model/effort/TTL/价目维持调用前外部状态。

**T2 动态选择精调**：未来固定一个 Agent Harness，从完全相同、可恢复的调用前状态真实执行多个合法 model+effort 动作并比较终局成功和整任务成本，才形成真正的步骤级 choice/ranking。先 SFT/成对监督，只有出现需要时才探索 RL/BoPO。

**T3 校准和学术评价**：基线最少含强固定模型、低价固定模型、简单路由规则、未经微调 Kev，以及轻量分类器；报告任务 resolved、总花费、cost/resolved、缓存实报数据、延迟、失败恢复和状态组/effort 消融。只报训练 loss/离线 accuracy 不足以证明论文贡献。

**现有脚本实际情况**：已查看本次上传的 prepare_router_data.py：当前会从一条 Agent episode 生成数个 prefix，却为它们赋相同 resolved 标签，语义只能是历史 continuation 的观察性 outcome；实际 model 对应决策点尚待核查。Arena 是静态人类偏好；Mooncake 输出档位由 prefix hash 确定，主要属于 cache opportunity。当前生成的混合 JSONL 不等于已经得到最优 (model,effort) 训练语料。以后只修改这一条原始数据清洗链，移除可选 mock/self-test 风格和冗余分支，改为打印真实处理行数/标签数/分割数。

**论文图**：Figure 1 在线：Harness/Context/Memory/Agent → StateSnapshot + Provider Registry → Kev 决策 → Model Call → Usage & Task Outcome；Figure 2 离线：Agent 状态源/静态模型比较/Cache workload → 分层标签和独立 split → Kev-4B LoRA 域适配 → 同状态真实动态比较 → 动态路由精调与校准。两图不虚构已完成实验。

**文献数据量**：[Kev 官方](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md) decision-v7 第一阶段 12,576，后续增量 1,425/5,219/11,320 条；[TwinRouterBench](https://arxiv.org/abs/2605.18859) 是 520 tasks 的 970 个执行验证档位前缀；[RouteLLM](https://arxiv.org/abs/2406.18665) 是偏好数据训练；[Boundary-Guided](https://arxiv.org/abs/2602.21227) 为先边界策略与 SFT 后策略优化。不能以其中任何一个行数当成本项目固定配额，独立任务/真标签更重要。

**一个终端入口**：未来以一个 run_experiment.py（尚不存在）调用已有 prepare_router_data.py 与 Kev 官方训练脚本，终端输出源数据数、训练轮次、loss、验证集指标和用时；示意为 python -u run_experiment.py 2>&1 | tee experiment.log。这只是拟议接口，未声称脚本已经可运行或模型已经训练。

### 6.4 文献研究主线、真实 Skill 与 Obsidian 论文知识库（2026-10-09）

现有研究证据库 research/task-level-cost-routing/literature/ 包含 58 份 PDF，但旧 manifest.json / index.md / README.md 只覆盖前 54 项，额外的 CATS、Harness-Native Agentic Routing、EET、Price Reversal 须补元数据与正文证据。论文知识库应使用原 literature 文件夹，新增中文 论文笔记/ 和 主题索引/，每篇一份 Markdown + 唯一 ID + YAML 来源元数据 + 原 PDF 链接 + 双向 [[WikiLinks]]；Obsidian 可直接将此文件夹打开为 Vault，不复制 58 份 PDF。写作仍以正文页码为依据，而非靠 AI 摘要推断数值。

已查到的 Skill 是 sxyq/skill- 中的 latest/skills/codex/paper-research-router/SKILL.md（本机一般为 ~/.codex/skills/paper-research-router/SKILL.md），专门针对已有 PDF 导入、精读、模型/方程/方法/训练/实验与限制提取；对引用做独立 evidence audit。外部论文搜索、作者/年份/论文更新属于 sxyq/research-router，不能假设两个 Skill 是同一个。paper-intake/reader 引用的 .research/schema 若本机缺失，可先用精简 Obsidian Markdown 而不创建复杂 Research Workspace。

研究优先级 A（Agent 在线路由与任务级真实监督）：SWE-Router、TRACE-Router、TACIT-Switch、TwinRouterBench、Boundary-Guided Agentic Routing、Harness-Native Agentic Routing、PROGROUTER、EvoRoute、EarlyEval。核查逐步骤路由、历史策略观测偏差、同状态分支、任务验证与任务级成本。
研究优先级 B（Model×Effort 和监督策略）：Route-to-Reason、Switchcraft、UNISCALE、BEST-Route、R2-Router、RouteLLM、RouterBench、LLMRouterBench、Router-R1、FrugalGPT。核查真实训练数据规模、pairwise/observed outcome/score 与 SFT/RL/分类器损失，分清调用级与任务级标签。
研究优先级 C（缓存/编排）：Unified AI Gateway、InfraMind、KVFlow、LMCache、TokenDance、AgentOpt、CASTER、CATS 与 Price Reversal。核查缓存可复用机会、物理 cache 命中、跨模型缓存兼容、成本/时间与多 Agent 协作状态的真实证据。
研究优先级 D（Jev/Kev 同类决策器）：结合 our-project/literature/jev-model-research.md、research/jev-deep/JEV深度调研报告.md 与 jaredpalmer/kev 的官方模型卡/训练格式，分开 TypeSafe Jev 托管闭源、Kev-4B Qwen 基座 LoRA+pointer-head 的开放训练、Laya/Visual Jev/Simple Jev/AnyJev 独立实现以及不同的 Meta JEPA。对 Jev 厂商公开程度和 RLCD 术语必须按官方可验证内容表述，不能推断未公开的训练细节；论文方法可不把 Kev 放在标题，但 Implementation Details 必须披露实际 checkpoint 与微调技术。

每篇笔记统一回答：研究问题；输入/动作/目标；原始数据与标注规模；模型骨干/训练损失；静态/在线评测协议；主要表格/图和页码；作者的限制；与 ModelRouter 的重合和可证伪差异；可复用数据/代码；尚不能确认的点。结论须明确区分论文作者声称、原文证据、我们的推断。

### 6.5 公开数据首批实测后的训练方法纠偏：区分观测、规则和路由因果（2026-10-09）

Execution 报告已落地 80,970 个多来源 JSONL 行；Planning 从 main 966f582 清洗代码和样本预览核实：Open-SWE/SWE-smith 只读各自首个 shard，Agent 的 low/mid/high 由 step/errors 阈值产生，并非真实模型努力/最佳选择；Arena winner 是真实比较标签，但生成的 Kev state **缺少原 Prompt 语义**，多余 effort/cost/cache 标签是模型名和长度阈值的派生；Mooncake prefix hash 可估历史复用，所谓 `cache_hit` 不等于 serving cached_read，`cache_affinity` 由同一 hit_ratio 阈值直接确定，放入 Choice 等于教模型重现阈值；TwinRouterBench 970 个 benchmark 标签被混进训练，不可再作为独立泛化测试。当前属于**初始多源数据转换成果，而非有 80,970 条最优 model×effort 标签的科研训练集**。

额外决策前泄漏：Agent 的 current assistant content 与 tool_calls 在保存状态前就纳入 context_chars/prior_tool_calls，真实在线路由不应看到将要发生的 assistant 响应和动作；TwinRouterBench state 包括整段 total_steps，也可能在执行前不可知。按轨迹 ID/人工 100 请求块划分不足以保证相同 instance/repo 和同题多次执行不跨集。科研统计不能用人工 session ID 的 31,235 当作真实独立 Agent 任务数。

**最短科学改正路线**：保留原始文件与现有单一 prepare_router_data.py；重提取仅决策前、真实文本及任务元数据；Agent resolved/continuation 只做 observed-outcome 标签，不把该策略当最优；Arena 保留真实 prompt + candidate model names + winner，优先训练真实 pairwise；Mooncake 仅做缓存负载特征与模拟研究数据；TwinRouterBench 仅独立 heldout；只有拥有相同状态多候选真实完成结果时才能训练 model×effort 优选标签。对 Kev 官方 `choice.criteria`、`score.criteria` 与整数 score.label 做最小兼容变换，并使用官方 CLI 验证一小批样本；不要重新构建工程化测试框架。完成后先记录真实各类可信标签数量，再选 Kev LoRA 适配。

论文中必须说明数据规模是 raw episodes/decision-prefixes/preference pairs/workload traces 各类不同单位，不能把四种行数加起来称为最优路由监督。消融要有真正的未见 task/repo holdout 和不含 benchmark 的训练版；否则高分只反映规则拟合或同题泄漏。

### 6.6 公共数据实际清洗后的方法学复审（2026-10-09）

> **2026-10-09 Planning 二次审查（覆盖本文件此前的“全量完成/训练就绪”说法）**：远端 main `48a6c14` 的 16 个 `字段统计.json` 合计 **3,963,661 行**，但 Execution 总报告、索引与 Status 写 **2,282,484 行**，差额 **1,681,177**；只有 TRA-001（1,040,564 vs 43,154）、TRA-002（783,438 vs 107,983）、TRA-004（11,048 vs 2,736）三处不同。不能在未核服务器实际完整输出前称任一数字为最终可信总量。

> **官方下载覆盖差异**：TRA-001 只处理 6 个代表分片/15,000 轨迹，官方约 521,712 轨迹；TRA-002 只处理 ticks 25,826 条，遗漏 tool 24,100 与 xml 26,076；TRA-004 仅 8/30 个模型配置、2,184/8,190 条 episode；受限 CMU/MARBLE 记 0。现阶段是**多源清洗已执行但不具备全量/训练数据验收结论**。

> **已核源码级缺陷**：Agent 当前工具调用先累加后记录 pre_decision_state（第一步可见 prior_tool_calls=1）；Open-SWE qwen36/qwen35 模型名被误标 Qwen2.5；SWE-smith 783,438 步全为 text_response；AgentSuite 只有 4 个 task_name 类别，未构造 273 实例的可比较跨模型键；Mooncake 未按时间明确排序且任意 hash 交集被称复用机会，output_length 被写成 requested；TwinRouter 的未来 total_steps 进入状态；LongMemEval-V2 保留的是任务/哈希等简化信息，非有效记忆文本；missing_rate=0.0 是硬编码不是统计。

> **代码与报告接口冲突**：当前 `prepare_router_data.py --mode public` 不存在；`all` 包含 Blog/CCH；还没有真实任务/仓库级 train/val/test 划分；多处 `TRAIN_ROUTER_CANDIDATE` 只是候选标记，不等于正确路由标签。不要启动 Laya/Kev 正式微调。保留合法已下载原始文件，只修原有唯一脚本、补缺失 split/shards、重处理受影响来源、更新 GitHub 每源真实预览及统计；无需再次全盘删除，也不新增 CI/复杂门禁。

**下一轮科学问题**：并非清洗行数越大越好。分别构造 (a) Agent observed continuation outcome（不能当 counterfactual routing），(b) Arena 真实人类偏好、RouterBench 有多候选评测（需许可/相同题目/正确成本口径），(c) AgentSuite 同题 across model/thinking 的**episode**级得分/真实任务键（同一任务下不能用 4 个 task_name 类别作为唯一 ID），(d) Mooncake真实到达顺序+最长前缀潜在复用（不能当实际物理缓存命中），(e) TIME/MEM/ENV 作为状态和工作负载，非最优路由标签。先做最小可验证输入与分割，再对照 Laya 与 Kev；不提前指定最终骨干，不因混合 `TRAIN_ROUTER_CANDIDATE` 标记而认为约 200 万训练标签存在。

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

### 8.1 顺序（实验预案，尚未冻结）

1. **E0 / E0.5**：环境、目录、数据与文档审计；MR-DIR-001/MR-SYNC-001 已验收，负责人确认未来隔离原则，E0.5 已完成（环境审计为历史快照）。
2. **E-DESIGN**：`EXPERIMENT_QA.md` 已建立；Q-001=A、Q-002=B、Q-003=B 预算原则已批准，后续逐项冻结具体 Benchmark、动作/effort、逐模型 API 额度、主指标、基线和受控统计协议；未完成不得进入 E1。
3. **E1**：按已确认实验协议实现最小 Schema、capability registry、hard constraint、usage ledger 与可测试 Router 接口。
4. **E2**：固定 Agent Harness 与自动任务终局 evaluator；固定模型/规则/sticky 基线。
5. **E3**：从相同状态快照受控分支，收集成对动作结果。
6. **E4**：Kev-4B LoRA/continuation 训练、消融与严格独立测试。
7. **E5**：跨任务/模型泛化分析、统计置信区间、论文图表和开源复现。

本节其余实验规模与对照为**待讨论的研究预案**，不是已执行实验或用户批准的预算。

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
- **已确认 Q-001=A**：直接使用经许可/复现/evaluator 检查的真实公开 Coding Benchmark；若需要小样本 Harness 技术验证，仍从真实 Benchmark 选任务，不强制独立合成小任务 Pilot；原“5 任务 pilot”只是历史规划，具体数量/seed 待 Q-008。
- **已确认 Q-002=B**：商业 API 与本地开源模型共用动态合法候选注册表，严格保留真实 effort 能力与缓存连续性约束。
- **已确认 Q-003=B 预算原则**：本地模型推理费用无预定上限但计算资源成本、GPU 时间照实记录；API 按具体模型设硬限额。实际额度、单任务停止条件和服务器/API/GPU 操作必须另行批准；
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
- **版本纪律**：默认在 `main` 本地频繁 commit，工作会话结束/重要里程碑或最长 24 小时工作周期内 push，不要求 PR；重要变更建议附任务编号。修改研究方法需在 Memory Decision Log 记录替换原因，Status 更新阶段与阻塞。
- **公开安全**：仅公开可审阅的抽象状态、脱敏统计、代码与公开文献；不泄漏私人主机和原始会话。
- **文档更新频率**：Memory/Status 随任务与决策事件更新；本研究总纲仅在证据、方法或实验协议变化时修改。未 push 的本地更新不在 GitHub 可见；不是自动后台刷新。
