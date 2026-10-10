# ModelRouter · 数据源、模型能力与缓存政策统一台账

> **版本 v1.5｜建立：2026-10-09；官方数据结构只读核验与清洗/训练方案更新：2026-10-09｜阶段：E-DESIGN / Q-007 第一大阶段｜状态：候选目录，未完成清洗和训练许可核验**
>
> **唯一职责**：此文件是公开数据源、数据许可、八组状态覆盖、模型/Provider 能力、缓存/定价政策及未来“候选 → 选择 → 数据加工 → 验收”信息的**唯一详细台账**。它不是新的执行流水线或运行时政策数据库。
>
> **权威性分工**：用户批准/否决、Q-ID 与日期唯一记录在 [EXPERIMENT_QA.md](../planning/EXPERIMENT_QA.md)；阶段/授权/唯一当前任务由 [PROJECT_STATUS.md](../planning/PROJECT_STATUS.md) 决定；研究方法在 [RESEARCH_OVERVIEW.md](../planning/RESEARCH_OVERVIEW.md)。此台账只记录具体资产及其**证据和准备状态**，不得将 Planning 优先级当作用户批准。
>
> **禁止误读**：登记 ≠ 已下载；官网有目录 ≠ 已核每个型号；公开许可证 ≠ 商业 API 输出自动可训练；可复用前缀 ≠ 生产缓存命中；task benchmark ≠ agent trajectory；API 调用成功 ≠ task resolved；跨模型同题评估 ≠ 相同中途状态的反事实。
>
> **新委派任务边界**：负责人已要求 Execution Agent 在自有服务器目录下载并 CPU 清洗公开数据（本机存储不足），但未回传真实清洗报告；本机 Codex 同步研究文档并组织 Obsidian 笔记。此任务委派并非已获 GPU 训练、付费 API 或修改共享服务许可；各数据集的实际条款和标签真实性仍需核实。

> **执行汇报的固定格式（2026-10-10 用户确认）**：向用户汇报新一轮执行结果时，先说明项目整体进度，再按当前阶段小步骤逐项展开，接着给出下一步计划、可复制的详细执行提示词和简短通俗说明。唯一完整约定与新对话启动提示词在 [PLANNING_MEMORY.md 第 10 节](../planning/PLANNING_MEMORY.md#10-新会话恢复协议长期生效)；本台账仅保存数据源、模型和计费政策，不重复维护项目最新进度。

## 0. 维护说明与证据等级

每一行都应长期保留 ID，允许**更新状态，不复制第二份目录**。所有动态政策必须附来源地址、查询日期、模型修订、地域/Endpoint 和有效期；政策变化追加变更记录。数据及政策必须分开维护，但共同由本文件提供导航。

- **S0·候选**：仅找到名称、网页或论文；尚未核正式文件、许可证或字段。
- **S1·来源已定位**：打开官方仓库/数据卡，能确认出处与大致字段；原始数据还未读。
- **S2·许可证待核 / 可训练 / 仅分析 / 禁训**：明确用途合法性；无证据一律“待核”且不得用于正式训练。
- **S3·字段已审**：后续获批后检查原始样本、时间戳、task/episode 键、模型/effort、真实 usage、成功标签及缺失率。未审绝不能填“覆盖全部”。
- **S4·待负责人选择 / 已选择 / 已排除**：由 Q&A 记录负责人的批准日期和用途；Planning 推荐不构成“已选择”。
- **S5·已加工 / 已验收**：只有真实数据完成规范化、去重、分割、标签核验和数据 lineage 后才可标记；需要 Execution 的事实证据。

**真实性标签**：MEASURED（Provider/Engine 真正回报）；OBSERVED_REUSE（请求前缀块相同的可复用证据）；SIMULATED（给定明确缓存模型的重放结果）；ESTIMATED（根据文本/统计推算）；UNKNOWN（无可信证据）。严禁互相冒充。记录来源版本是数据资产层的要求，**模型提供商的政策仍需按实际请求时间生效**。

## 1. 数据来源总登记（Source Registry）

以下来源来自 2026-10-09 Q-007-R1/R2 的已有调研、公开 Hugging Face 数据卡与 GitHub 官方仓库。**优先级是 Planning 推荐，而非批准或量级承诺。** 同一原始来源出现在不同特征用途时复用相同 ID，不重复计算任务量。

### 1.1 Agent 真实执行轨迹与任务环境

| ID | 源与链接 | 原始粒度及可用标签 | 主要状态组 | 来源/训练资格 | 建议 |
|---|---|---|---|---|---|
| TRA-001 | [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | 6 个多框架/多模型代表分片 (942 MB)，单步决策前状态隔离 | 任务、工具、上下文、模型异构 | **S5·已加工**：43,154 步有效记录；CC BY 4.0 | **P0·已就绪**，`OBSERVED_ACTION` |
| TRA-002 | [SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories) | 全部 8 个分片 (972 MB)，Claude 3.7 Sonnet 真实执行步 | 任务、工具、时间、代码修复 | **S5·已加工**：107,983 步有效记录；MIT | **P0·已就绪**，`OBSERVED_ACTION` |
| TRA-003 | [CMU Agent Trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 上游 Hugging Face 接口返回 HTTP 403 Forbidden | 任务、工具、时间 | **S1·GATED**：0 条；遵循零造假规范合规审计 | 待授权，不进训练包 |
| TRA-004 | [AgentSuite multi_challenge](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 全部 8 个模型/思考模式全量 JSONL (44 MB) | 任务、模型比较、思考模式 | **S5·已加工**：2,736 步；同题思考开关对照 | **P0·已就绪**，Thinking-On/Off 对照 |
| ENV-001 | [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | 真实 Python 仓库/Issue/可执行回归测试套件 | 任务、环境、验证规范 | **S5·已加工**：2,438 个标准任务基准；MIT | 任务环境特征源 |
| ENV-002 | [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | 跨 20 种编程语言的超大规模任务基准 (409 MB) | 任务、多语言环境、复杂度 | **S5·已加工**：32,079 个任务；MIT | 多语言路由特征源 |
| ENV-003 | [SWE-smith Tasks](https://huggingface.co/datasets/SWE-bench/SWE-smith) | 批量软件工程 task/环境，非等量成功轨迹 | 任务、环境 | S1；与 TRA-002 上游有关联、需同任务去重 | 未来任务源候选 |

### 1.2 请求级模型选择与偏好监督

| ID | 来源 | 真实监督粒度 | 可训练性 | 规划用途 |
|---|---|---|---|---|
| ROUTE-001 | [LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | 27 个 benchmark、40 个模型实测结果 (bench-release) | **S5·已加工**：548,059 条实测记录 | P0·多模型真实能力与成本对照 |
| ROUTE-002 | [RouterBench](https://huggingface.co/datasets/withmartian/routerbench) | 86 类任务、11 个主流模型得分与官方 Oracle 路由 | **S5·已加工**：36,497 条 0-shot 样本 | P0·标准同行评审路由基准 |
| ROUTE-003 | [TwinRouterBench Static](https://huggingface.co/datasets/Amorph/TwinRouterBench) | 多步降级搜索能力档位 (`low`, `mid`, `high`) | **S5·已加工**：970 步；**强制标为 EVAL_BENCHMARK_ONLY** | **严禁进训练集**，仅作最终泛化评测 |
| ROUTE-004 | [Arena Human Preference 55k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | 真实用户 Prompt + 两两模型盲测人类偏好胜负 | **S5·已加工**：57,477 场对决 (64 模型) | P0·真实人类偏好监督信号 |
| ROUTE-005 | [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | 6 大 Harness 框架端到端开销、真实缓存与奖励 | **S5·已加工**：6,204 条；**标为 RESEARCH_ANALYSIS_ONLY** | **严禁训练/蒸馏**，仅作系统分析基准 |

### 1.3 KV Cache、请求时间、服务端资源

| ID | 来源 | 关键字段与性质 | 可以研究什么 | 不可以替代什么 |
|---|---|---|---|---|
| CACHE-001 | [Mooncake FAST'25](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release) | 生产请求时序、前缀块 hash_ids (conv, tool, synth) | **S5·已加工**：39,632 条；`OBSERVED_REUSE_OPPORTUNITY` | **绝不冒充**商业 API 实际缓存命中 |
| CACHE-002 | [Mooncake 旧版 trace](https://github.com/kvcache-ai/Mooncake/tree/main/arxiv-trace) | 旧版匿名前缀/请求记录 | 历史请求变化 | 版本可能重合；不得双计 |
| CACHE-003 | [Mooncake Cache Benchmark](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html) | 基于块哈希/容量/淘汰与缓存策略的回放和指标 | **SIMULATED** 读写与 hit rate | 不是真实原始 API 命中记录 |
| CACHE-004 | [KV Cache Workload Bench](https://github.com/hokiyoung/kv-cache-workload-bench) | 合成/派生共享前缀、会话、并发、驱逐 workload | 模型化缓存压力与容量 | 不是实测封闭 API usage |
| CACHE-005 | 未来 Provider 实际 Usage（无单一公开仓库） | requested model、真实 cached/read/write Tokens、provider Endpoint、账单和时间 | **MEASURED** 的唯一权威来源之一 | **当前本项目未持有充分的 Agent 同状态原始计量样本** |
| CACHE-006 | [vLLM Metrics / Prefix caching](https://docs.vllm.ai/en/latest/usage/metrics/) | 获准运行后可观察引擎实例的实际缓存统计 | 本地引擎 MEASURED | 并非预先存在的独立下载数据集；未经许可不得部署采集 |
| TIME-001 | [BurstGPT](https://github.com/HPMLL/BurstGPT) | 真实 ChatGPT 与 GPT-4 生产时序到达与负载 | **S5·已加工**：1,404,294 条；`OBSERVED_WORKLOAD` | 不含完整 Agent task outcome |
| TIME-002 | [Alibaba xMaaS 2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas) | MaaS 集群实例/资源/显存/GPU/负载时序 | 系统级容量与时间压力 | 不是逐请求 Agent 动作真值 |
| TIME-003 | [Alibaba GenAI Trace](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) | 真实生成式服务队列/资源和时延（包括非 LLM） | 系统请求并发和资源预算参考 | 非编码 Agent 或路由胜负 |
| TIME-004 | TRA-001/TRA-002 的时间子视图 | 已发生 step/turn/工具/局部时间 | Agent 剩余步骤/时间信息 | 不另计一个独立数据集；无初始预算则剩余额度 UNKNOWN |

### 1.4 长期记忆、多 Agent 协作

| ID | 真实来源 | 可覆盖状态 | 主要限制 |
|---|---|---|---|
| MEM-001 | [LoCoMo](https://github.com/snap-research/locomo) | 会话历史、事件、时间推理、摘要/证据 | 已汇编入 MEM-005 |
| MEM-002 | [LongMemEval](https://github.com/xiaowu0162/longmemeval) | 跨会话记忆、用户事实更新/冲突、检索 | 已汇编入 MEM-005 |
| MEM-003 | [LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) | 长程 Agent 记忆、100 轮干草堆文档检索 | **S5·已加工**：451 个任务；`MEMORY_BENCHMARK` |
| MEM-004 | [MemoryAgentBench](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) | 增量记忆与检索、测试时信息更新 | 非路由成功率标签 |
| MEM-005 | [MemoryCraft](https://huggingface.co/datasets/daven3/MemoryCraft) | 跨会话长期记忆对话与问答对 | **S5·已加工**：510 条；`MEMORY_BENCHMARK` |
| MEM-006 | [LongBench](https://github.com/THUDM/LongBench) | 上下文长度、长文本检索/归纳负载 | 文本能力压力，不是 Agent Memory 真迹 |
| MAS-001 | [MARBLE/MultiAgentBench](https://github.com/ulab-uiuc/MARBLE) | 上游 Hugging Face 接口返回 HTTP 401 Unauthorized | **S1·GATED**：0 条；合规审计记录 |
| MAS-002 | [MASBench](https://github.com/BUPT-GAMMA/MASBench) | 通信、部分可观测性、协作记忆、代价 | 许可证与可下载训练轨迹待核 |
| MAS-003 | [AgentWorld](https://arxiv.org/abs/2609.31590) | 长程角色不对称、依赖/冲突、协调 | 新近基准；训练材料是否可用待核 |
| SYS-001 | [OpenSquilla / Harness-Native Agentic Routing](https://github.com/TokenRhythm/opensquilla) | **结构参考**：context compaction、memory、Agent turn loop、router、usage/decision log 与 ensemble | **不是公开模型路由训练轨迹库**，不能把代码当数据集；本阶段不创建第二个 Harness |

### 1.5 已有本项目本地来源的职责

| ID | 现有相对路径 | 可支持 | 限制 |
|---|---|---|---|
| OWN-001 | source/cch-model-cost-cache-statistics.csv | CCH 真实聚合 model×effort、USD/token/cache 信息先验 | 缺 task_id / 完整同状态前缀和任务终局；不能作为反事实 |
| OWN-002 | cleaned/sxyq-blog-gpt-usage-cleaned.csv | Blog 真实调用分布、model/usage/部分缓存与 quotaUnits | 计价原单位为 quotaUnits，**不可无证据换算 USD**；缺有效终局 resolved |
| OWN-003 | summaries/ 中既有聚合 CSV | 训练采样权重/部署参考及研究可视化 | 不是新增独立可监督训练数据，不能重复计数 |

## 2. 八组 Agent Runtime 状态 → 数据源覆盖矩阵

矩阵表示**候选数据潜力，不是已下载后实测的字段覆盖率**。最终字段级覆盖和 missing rate 应在下一阶段的真实 schema audit 中填写；某来源不支持字段就标 UNKNOWN。八组状态要求与 [RESEARCH_OVERVIEW §2](../planning/RESEARCH_OVERVIEW.md) 一致。

| State Group | 主要来源 ID | 预计可观测信息 | 缺口 / 后续需要 Harness |
|---|---|---|---|
| Task/Subtask | TRA-001/002、ENV-001/002、ROUTE-001 | task、repo、issue、语言、任务族、已发生进度 | 任务当前子目标图/难度 proxy 不一定有 |
| Agent/Coordination | MAS-001/002/003、SYS-001、TRA-001 | Agent 角色、拓扑、沟通事件、共享上下文 | 多子代理 handoff 与实际执行 budget 需自有 Harness |
| Context/Memory | MEM-001～006、TRA-001、SYS-001 | 历史窗口、消息长度、摘要/检索、压缩事件 | provider 真实 context 剩余、记忆版本及有效性未必公开 |
| Tool/Environment | TRA-001～004、MAS-001、SYS-001 | 工具/测试/环境回报、失败/重试 | 只接收决策前已完成的工具结果 |
| Verification/Recovery | TRA-001/002、ENV-001/002 | 测试失败、修复循环、当前验证结果 | 最终 evaluator 和标准修复补丁只能作为 label/审计 |
| KV Cache/Continuity | CACHE-001～006、OWN-001/002 | 真实前缀可复用机会、真实 usage 口径、本地实例指标 | 公开 Agent 真缓存命中稀缺；必须标 measured/reuse/simulated/estimated |
| Temporal/Execution | TIME-001～004、CACHE-001、TRA-001 | 到达、已发生步骤/耗时、Token、服务负载 | 初始/剩余 task budget、价格和工具总耗需原始账本 |
| Provider/Availability | §3 Provider Registry、TIME-002、SYS-001 | 可用 model/effort、能力、区域、API 价格、负载/健康 | **政策作为动态确定性源**，不能从旧训练轨迹猜当前可用性 |

**不能直接从公开轨迹推断的能力**：不同 Provider 在同一个决策前状态下未选动作的 task outcome、跨模型物理 KV 可迁移、实测缓存折扣、某日实际 API 权限以及多 Agent 剩余额度。涉及这些字段须保持 UNKNOWN 或由合法的真实运行时数据补充。

## 3. Provider / Model / Effort / Cache Policy 证据注册表

这一节是后续**动态 Registry 的资料来源目录**，不是已经构建好的运行时 model registry。**本文件记录哪些政策需要核实以及官方入口，不臆造对所有模型适用的缓存政策、折扣或 Effort 档位。**

### 3.1 已找到具体缓存机制官方说明的主体

| Policy ID | Provider / 主要模型族 | 官方证据地址 | 目前可确认的政策类型；仍需逐型号核查 |
|---|---|---|---|
| POL-001 | OpenAI / GPT、Codex | [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | prompt cache usage、读写/保存口径、TTL/价格版本；不得统一所有 GPT 型号 |
| POL-002 | Anthropic / Claude | [Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | cache read/creation tokens、5m/1h、tools/thinking 影响前缀与过期 |
| POL-003 | Google / Gemini | [Context caching](https://ai.google.dev/gemini-api/docs/caching)、[Thinking](https://ai.google.dev/gemini-api/docs/thinking) | 隐式/显式、存储费、TTL；thinking 支持因型号/接口不同 |
| POL-004 | xAI / Grok | [Prompt caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching) | 自动缓存、缓存字段和会话亲和；按型号查具体用量 |
| POL-005 | OpenRouter（API 聚合） | [Caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching) | sticky provider / 缓存折扣；必须记录**实际承载 Provider Endpoint** |
| POL-006 | DeepSeek 原厂 API | [KV disk cache](https://api-docs.deepseek.com/zh-cn/guides/kv_cache/) | cache hit/miss tokens；开源权重自托管**不继承**原厂 API 缓存 |
| POL-007 | 阿里百炼 / Qwen、托管其他开源模型 | [Context cache](https://help.aliyun.com/zh/model-studio/context-cache) | 隐式/显式，按型号、地域、产品版本核最小长度/TTL/价格 |
| POL-008 | 火山方舟 / 豆包及托管模型 | [Context cache](https://docs.volcengine.com/docs/ark/context-cache?lang=zh) | 隐式/显式/session、thinking/tools/endpoint 约束，版本待锁 |
| POL-009 | Moonshot / Kimi | [Caching guide](https://www.kimi.com/academy/best-practices-for-context-caching) | cache read/write、部分 5m/1h，Chat/Responses/Messages 接口不同 |
| POL-010 | 腾讯 / Hunyuan、TokenHub | [API 旧文档](https://cloud.tencent.com/document/product/1729/101838) | 历史 CachedTokens 有官方入口；**现行 TokenHub Endpoint 需重新核实** |
| POL-011 | 百度 / ERNIE、千帆 | [缓存通知](https://ai.baidu.com/ai-doc/WENXINWORKSHOP/Rm6uq7jy9) | 部分历史型号支持缓存用量，不能推成全部现行型号 |

### 3.2 已列入覆盖范围，具体型号/缓存政策待官方核验

| Policy ID | Provider / 模型族 | 官方入口 | 当前状态 |
|---|---|---|---|
| POL-012 | 智谱 / GLM、Z.ai | [BigModel](https://docs.bigmodel.cn/) | **PENDING_MODEL_SPEC**；原厂 cache/effort/TTL/usage 未逐型号核准 |
| POL-013 | MiniMax 原厂 / MiniMax-M 系 | [平台](https://platform.minimaxi.com/) | **PENDING_MODEL_SPEC**；不能套用百炼托管产品 |
| POL-014 | 阶跃星辰 StepFun / Step 系 | [平台](https://platform.stepfun.com/) | **PENDING_MODEL_SPEC** |
| POL-015 | SiliconFlow / 各种开源托管模型 | [文档](https://docs.siliconflow.cn/) | **PENDING_ENDPOINT_SPEC**；托管策略不等于原厂 |
| POL-016 | Mistral | [官方](https://docs.mistral.ai/) | **PENDING_MODEL_SPEC** |
| POL-017 | Cohere | [官方](https://docs.cohere.com/) | **PENDING_MODEL_SPEC** |
| POL-018 | Together AI | [官方](https://docs.together.ai/) | **PENDING_ENDPOINT_SPEC** |
| POL-019 | Groq Cloud | [官方](https://console.groq.com/docs) | **PENDING_ENDPOINT_SPEC** |
| POL-020 | Fireworks AI | [官方](https://docs.fireworks.ai/) | **PENDING_ENDPOINT_SPEC** |
| POL-021 | 本地 vLLM：Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan 等开源权重 | [Prefix caching](https://docs.vllm.ai/en/latest/design/prefix_caching/)、[Metrics](https://docs.vllm.ai/en/latest/usage/metrics/) | 按实际运行引擎、tokenizer、实例和租户隔离核，**不能只按权重厂牌判断** |
| POL-022 | 本地 SGLang：各开源权重 | [官方](https://docs.sglang.ai/) | PENDING_ENGINE_CONFIG；运行时本地缓存配置和指标待另行授权检查 |

**Provider 模型范围**：国产开源与闭源分别标注 Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan、Step、豆包、文心等（具体哪一型号开源、闭源、在哪个平台可用，尚未逐型号列表确认）；国外 GPT、Claude、Gemini、Grok、Mistral、Cohere 与第三方托管。必须将 **base_model、actual_provider、deployment_id、api_endpoint、model_revision、region** 拆开。权重许可与服务使用条款各自独立。

### 3.3 每个 Provider 模型政策条目未来必须补齐的字段

| 分类 | 必备字段 |
|---|---|
| 身份 | provider_id、model_id、model_revision、deployment_id、api_endpoint、region、original_vendor、open_weight_status |
| 能力 | context_window、supports_tools、supports_json、image_mode、effort_allowed_values、effort_requested/effective、支持依据 |
| 缓存 | cache_mode(implicit/explicit/engine)、cache_read/write_fields、minimum_prefix_tokens、ttl、cache_key_scope、session_affinity、cache_invalidation_policy |
| 定价 | input/uncached、cached_read、cache_write、output、reasoning 是否单独计价、storage_fee、currency、price_catalog_version、valid_from/to |
| 可用性 | max_rate、quota、retry/backoff、provider health、access_region、tenant/account limitations |
| 合规 | terms_url、api_output_training_allowed、residency、data_retention、license_status、policy_reference |
| 证据 | source_url、verified_at、source_revision、evidence_level(verified/pending/conflicting)、field_confidence、last_reviewed_by |

**未知是 UNKNOWN，不等于不支持或支持。** 定价、TTL、准入和 ToS 不能通过 Kev 权重固化为长期真实的运行时政策；真正调用之前必须以当前版本化 ProviderRegistry/硬约束为准。Google [API Terms](https://ai.google.dev/gemini-api/terms/) 等模型服务协议包含特定训练用途限制；每个 API 输出能否被用于公开路由模型微调，必须另审合同与授权。

## 4. Cache 专用证据字段与标签边界

一条缓存相关训练记录必须区分**请求事实**、**缓存机会**、**模拟结果**及**真实计费结果**。

| 字段组 | 字段示例 | 来源与可信级别 |
|---|---|---|
| 前缀复用机会 | timestamp、prefix_block_hashes、prefix_token_count、prior_model_id、session_key | CACHE-001 OBSERVED_REUSE（匿名 hash 的相等表示某条件下可复用） |
| 模拟命中 | simulated_cached_tokens、capacity、ttl_policy、eviction_policy、sticky_routing_assumption | CACHE-003 SIMULATED |
| 实际 API 缓存 | provider_raw_cache_read/write/hit/miss_tokens、response_usage_raw、model_revision、endpoint、request_id | CACHE-005 MEASURED，仅实际调用回报有效 |
| 本地缓存 | engine_version、tenant/salt、physical_prefix_cache_hits、request_tokens、evicted_blocks | CACHE-006 MEASURED，仅真实引擎实例观测有效 |
| 成本与约束 | pricing_version、cache_read_price、cache_write_price、expired_at、cache_scope、prefix_materialization_cost | 政策/账单证据，provider-specific |
| 预估与缺失 | estimated_prefix_overlap、cache_unknown_reason、source_quality | ESTIMATED 或 UNKNOWN，不能填进 MEASURED 列 |

**不能自动训练为真**：缓存命中百分比一定转化为等额成本折扣；不同厂商缓存键相同；换模型保留物理 KV；相同 Token 前缀必然同样命中；缓存 TTL 一律同值；已有 CCH/Blog 聚合能归因到某一 Agent 决策。

## 5. 候选选择表（Selection Board）：先登记，再选，最后加工

本节专门留给今后负责人逐批确认**哪些数据源真正进入项目训练集合**。不在本轮代替负责人做最终选择。

| 数据组 | Planning 推荐优先审议 | 当前负责人的明确选择 | 当前状态/阻塞 |
|---|---|---|---|
| Agent 轨迹 | TRA-001、TRA-002 | **Q-007：第一学习阶段从公开 Agent 轨迹 A 开始**，未逐源批准 | 待逐源许可证/字段核验 |
| 模型选择 | ROUTE-001、ROUTE-002；辅助 ROUTE-003/004 | 未确认单独数据集 | ROUTE-001/002 许可待审，不得训练 |
| 缓存重用 | CACHE-001；CACHE-003 仅模拟 | 未明确逐源批准 | 真实性必须分层，不能把模拟命中当真值 |
| 长记忆 | MEM-003、MEM-001/002、MEM-004 | 未明确逐源批准 | benchmark 留出/版权/轨迹可用性待核 |
| 多 Agent | MAS-001、MAS-002、MAS-003 | 未明确逐源批准 | 任务/代码与现成训练轨迹区别尚待核 |
| 时间/预算 | TIME-001、TIME-002，重用 CACHE-001 | 未明确逐源批准 | 只有请求时延/资源时序，不等于完整任务预算 |
| Provider 政策 | POL-001～022，全覆盖、重点逐型号 | 仅确定 Q-002 混合 API+开源模型原则 | 动态来源表，具体真实合法动作池未冻结 |
| 禁止训练 | ROUTE-005 | 不进入训练；用于只读研究分析 | 发布方明确限训 |
 
**后续 AI 每次提出数据源选择建议必须产出**：固定源 ID、官方 URL、revision、许可证据（可训练/禁止/待核）、拟覆盖状态组、能得到的真实标签类型、与已有源重叠和未来信息泄漏风险、优先级理由、推荐状态；用 Q-ID 交由负责人确认。不能把 Planning 推荐写成最终已批准，也不能默默扩大 API 费用或训练权限。

### 5.1 选择决策记录（待批准）

| 日期 | Source ID | 用途（轨迹/静态选择/模拟/分析/评测） | 选择 A/B/C/排除 | 负责人/Q-ID | 证据/影响 |
|---|---|---|---|---|---|
| — | — | — | **待确认** | — | 尚无逐数据源批准 |

## 6. 数据清洗与 AI 交付规范（待下一阶段授权执行）

**本节是对未来 Execution Agent 的质量合同，不是运行指令。** 必须先通过负责人对来源、下载范围、许可证和执行环境的批准。

1. **许可与溯源**：为每源生成 manifest（source_id、repo/revision、license/evidence、下载时间、checksum、是否允许 train/redistribute、原始字段表）；不明许可/商业 API 输出归属必须隔离，禁训源不得形成蒸馏标签。
2. **Raw immutable**：保留原始文件只读及版本；不覆盖旧 CCH、Blog 的 source/、cleaned/、summaries/；将来要决定物理 raw/normalized/processed 路径应基于现有 data 目录唯一扩展，不建 parallel v2/v3 pipeline。
3. **样本单位统一**：task_id/repo_id、episode_id、agent_id、step/decision_id、model_revision、source_id、observed_at；静态 routing 任务、长 Agent episode、KV workload 请求、资源时间事件分别登记**不同粒度**，不强行跨源拼接不存在的任务 ID。
4. **先隔离再展开**：按任务、仓库、数据源家族与近重复任务分组，先固定 train/val/test，再从 train episode 生成前缀状态；同任务的多个模型、所有前缀、补丁与最终结果不得跨 split；新模型/新 Provider benchmark 的测试来源另做冷启动留出。
5. **严格决策前截断**：只允许时间 t 已观察的上下文/工具/测试/记忆版本、剩余预算与硬约束进入 Kev 输入；未来的成功标注、最终 patch、未来 Token 总量、未来缓存命中和后续恢复循环只能保留在 Outcome 中。
6. **缺失与语义层级**：所有字段保留 measured/observed_reuse/simulated/estimated/unknown；实际 cache 用量、模型 effort 支持、合法动作可用性、成本货币单位必须有可追溯出处，禁止人工以零或假定值填满。
7. **标签分层**：真实 observed_resolved / 可信 observed_cost_to_go / 同静态 prompt 的多个 model_score / 同任务偏好 / 已知硬规则 legality / 模拟 cache hit，分别存表与标签 origin；从一个执行轨迹**不能**把未执行候选标成失败或成功。
8. **Kev 训练视图**：仅对有真实有据标签的样本转换 noul（yes/no）、score（顺序等级）、choice（合法动作或真实可比选择）格式；保留 source_id、split、label provenance、candidate_set_version、weight、任务 ID；随机变化选项顺序并检查模型名称捷径。
9. **AI 自动化边界**：AI 可提议字段映射、许可证待核清单、错误分布、异常/近重复候选与预处理规则；真实删除、覆盖、把 UNKNOWN 升级成 MEASURED、改变任务分割、打开商业 API、部署 GPU 或启动训练，必须有获批的明确计划与可追溯变更记录。不得让 AI 自行生成来源不明的“最优模型标签”。
10. **数据验收报告**：按 source 与八组状态汇总覆盖率/缺失率、标签可追溯率、合法模型×effort 覆盖、可用任务数（而非仅 prefix 行数）、任务/仓库去重、时间泄漏、训练/评测集污染、价格版本和 license 白名单，最后产出“可训练、仅分析、暂隔离、禁止训练”清单。

### 6.1 未来 AI/Execution Agent 的审计输出模板

| 项目 | 必须给出的结果 |
|---|---|
| Source identity | source_id、URL、revision、license、usage permitted、原始 hash、父数据源 |
| Content | task/episode 粒度、真实字段、各类标签、缺失字段、是否独立数据源 |
| State coverage | 八组 state 每组有哪些 measurable、estimated、missing，以及出处 |
| Routing comparability | 同静态题多模型？同 Agent 中途状态多候选？有没有真实 Effort？ |
| Cache fidelity | 实际缓存用量 vs 可重用前缀 vs 模拟命中，是否可以用于成本标签 |
| Privacy/contamination | 私有文本/凭据/许可证、跨任务/仓库重复、评测污染 |
| Recommendation | 选用、仅分析、等待许可、排除；理由与未来最小动作 |
| Execution evidence | Git/数据 SHA、运行环境与命令、输出路径、完整性结果；**未执行必须写未执行** |


### 6.2 官方数据卡只读核验：第一批候选和字段差异（Planning 推荐，不代表批准）

2026-10-09 查阅下列官方数据卡、Viewer、README 及 Kev 官方标注格式；**未下载数据、没有原始样本统计结果，也未审核所有许可证**。优先保证不同训练任务需要的真值类型，不为了把八组变量全部填满而错误拼接不相关数据。

| 来源 ID | 确认的原生数据及字段 | 具体清洗注意点 | 第一轮建议 |
|---|---|---|---|
| TRA-001 Open-SWE-Traces | 官方 v1.0 数据卡列 instance_id、repo、trajectory_id、trajectory、tools、resolved(-1/0/1)、metadata.reference_patch/model_patch；后续 v1.1/v1.2 已扩容 | 按 source revision/config 兼容 trajectory/messages；reference_patch 是标准答案，仅能做标签/审计，**不得进入决策输入**；-1 是 unknown 不是失败；同 task/repo/相似实例分同侧 | **P0 核心状态源** |
| TRA-002 SWE-smith trajectories | 数据浏览器现列 messages、instance_id、resolved、model、traj_id、patch，且有多个 split；卡片特指 5,017 条训练子集但浏览器另展示多组数据 | messages 可能是 JSON 文本；区分实际执行 patch 与 gold patch；最终 patch 不可在前缀出现；**按具体 split/源模型/instance 核实后选取**，不要混同全部 76k rows、5,017 子集和 52k 任务 | **P0 互补 Agent 轨迹** |
| CACHE-001 Mooncake FAST25 | 官方 JSONL 示例字段只有 timestamp(ms)、input_length、output_length、hash_ids（512-token remapped prefix block）；toolagent/会话真实请求与 synthetic 分开 | hash 可算真实请求的可复用前缀机会 OBSERVED_REUSE；**没有真实 API cache_read_tokens、模型 ID、任务 resolved 或单次响应时延**；在设定缓存容量/TTL/LRU 后只能生成 SIMULATED 标签 | **P0 Cache 数据源** |
| ROUTE-004 Arena Human Preference | 官方数据卡 Apache-2.0，同一 query 的双模型人工胜负/平局偏好 | 两模型身份/响应与 winner / tie / both-bad 按原 schema 规范化；**偏好不等于 Agent resolved**，旧型号不可冒充当前部署 | **P0 静态比较底座** |
| ROUTE-001 LLMRouterBench | 官方描述 33 模型/21+ 任务数据集的 score、prompt_tokens、completion_tokens、cost；结果按 dataset/split/model/time 分层 | **预先核验结果包及各上游许可**；按同 query、同 benchmark、同评分器、同 shot/版本对齐候选，不能混用不同评价指标的原始 score | **P0 研究优先，许可证未核前不训练** |
| ROUTE-002 RouterBench | 同 prompt 多模型性能/估计费用、有 0-shot 和 5-shot 两套 | 数据卡缺明确 license；不同 shot 不能同组；估计费用不当作真实账单 | 许可待核候选 |
| ROUTE-003 TwinRouterBench | 970 rows，messages JSON、step_index、target_tier（四档）等；**不含具体 model target** | 不能将 target_tier 硬映射为 model×effort；最好保留为独立基准，训练用途需提前锁定且防污染 | 评测优先 |
| TIME-001 BurstGPT | 官方 README 有 Timestamp、Session ID、Elapsed time（整次响应非 TTFT）、Model、Request/Response tokens、Log Type | 带失败与 without_fails 文件彼此重叠；不能相加，且失败 API 请求不等于失败 Agent 任务 | 时间/会话辅助 |
| MEM-003 LongMemEval-V2 | Web/企业 Agent 多次长历史、问答证据及时间，官方项目提供检索与记忆评测接口 | 未来问答答案不可泄露到当前 Agent 状态；优先用作 Memory/摘要评测，训练许可和保留集另审 | Context/Memory 参考 |
| MAS-001 MARBLE | 多 Agent 任务、角色、拓扑、协作/通信环境 | 代码和任务不保证有已许可的每步训练轨迹，不能凭任务构造最优模型标签 | 协作环境/Schema |

参考：[Open-SWE](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/blob/main/README.md)、[SWE-smith](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories)、[Mooncake](https://github.com/kvcache-ai/Mooncake/blob/main/FAST25-release/README.md)、[LLMRouterBench](https://github.com/ynulihao/LLMRouterBench)、[BurstGPT](https://github.com/HPMLL/BurstGPT)、[Kev format](https://github.com/jaredpalmer/kev/blob/main/skills/kev-finetune/references/data-format.md)。

**当前最低必备数据能力组合**：真正 Agent 状态与 resolved（TRA-001，TRA-002 辅助）；合法静态比较（ROUTE-004）；缓存复用机会（CACHE-001）；真正同题性能/成本路由比较（ROUTE-001 待许可核验，核验失败则必须留缺口，不能用其他数据伪造）。Provider 模型/effort/缓存/价格规则取 POL 动态证据快照，不是固定训练语料。全部为 Planning 候选，**负责人还未逐源作最终选用决定**。

### 6.3 源到训练数据的唯一清洗处理路线（尚未执行）

1. **S0 来源许可与原始数据冻结**：source_id、官方 URL、revision、license、第三方原始模型生成内容的训练权、可再分发范围、文件 hash、原始字段、数据发布拆分；未知许可证先隔离。不得把多来源拼成一个并不存在的完整 Agent episode。
2. **S1 源专属归一化**：分成五种实体，不强行统一为一张表：AgentEpisode（task/agent/steps/model/resolved）；StaticModelOutcome（prompt/候选/真实同题 score/费用及 benchmark）；CacheWorkloadRequest（timestamp/长度/有序 hash_ids）；MemoryOrMASBenchmark（上下文/协作任务与真答案）；ProviderPolicySnapshot（endpoint/model/revision/实际合法 effort/价格/TTL 与证据有效期）。
3. **S2 去重与切分**：按数据源家族、task/repo/issue/near-duplicate 筛出同一个 leak_group；先分 train/val/calibration/test，再把 Agent episode 在每次真实 model call 的决策前时点切为 prefix。已公布正式 benchmark 需要另留出集，**官方 split=train 并不自动保证不会污染我们的测试题**。
4. **S3 八组状态重建**：仅使用决策时刻之前的 Task/Subtask、Agent/Coordination、Context/Memory、Tool、Verification、Cache、Temporal、Provider 信息；每字段记录 observed_at、MEASURED/OBSERVED_REUSE/SIMULATED/ESTIMATED/UNKNOWN 与来源。不能读取未来 patch、最后 resolved、未来总 Token/缓存或未发生的测试。
5. **S4 标签溯源**：把已执行动作的 terminal resolved 和可核 cost_to_go；同静态 query 的 model-score/人工偏好；确定性合法性规则；Mooncake prefix reuse/模拟 cache 单独存为不同监督域。没有相同决策前状态的未选动作真实结果时，**绝不生成所谓最优 Model×Effort 标签**。
6. **S5 Kev 训练样本**：保留原始多表与 provenance，另导出一个最终 Kev JSONL 视图。官方记录为 state + questions，type 为 noul/score/choice，label 必须具有证据；候选字符串与实际可执行动作一致，source/task/split/evidence 外置记录映射。**官方通用 fine-tune 指南的记录总长度上限为 2048 tokens**，不能直接投入几十万 Token 的完整轨迹。真正提供给 Kev 的是决策前摘要，状态要短且来源可复查；默认 split_data.py 只分组 exact state，不替代本项目 task/repo 去重。
7. **S6 验收**：先审来源许可证、数据分割无污染、八组状态覆盖和 missing rate、真实标签/有效模型×effort 数、cache 测量层、成本单位/价格快照、输入长度、JSONL 格式、任务权重、raw→normalized→training 的可逆索引。只有真实通过才把每个 Source 从候选改成 TRAIN_READY；数据量留到清理阶段决定。

**重要原则**：不同来源通过共享模型学习**不同监督任务**，不通过按行联表“补齐缺失的八组状态”。例如 Mooncake 的缓存重用概率可作为单独训练任务，不能作为 Open-SWE 某条完全不相关 Agent 轨迹的真实缓存命中值。

### 6.4 模型训练四阶段建议（Q-010/Q-011 仍未由负责人批准）

| 学习阶段 | 可用训练视图 | 训练到什么程度 | 仍无法证明 |
|---|---|---|---|
| M1 Agent 状态、已执行动作结果 | TRA-001/002 的真实决策前状态与 terminal resolved；有真账单才成本分档 | Kev noul 观察性结果预测；部分确定规则辅助 | 不能推出其它候选模型实际更好 |
| M2 静态任务/模型能力与辅助缓存 | 已许可的 ROUTE-004 与 ROUTE-001/002；Mooncake 缓存潜力和可核政策规则分别做 typed 任务 | choice 同题比较与能力先验、score/noul 缓存复用任务（只对对应真实/模拟标签） | 不能证明动态 Agent 中途切换模型的因果效果 |
| M3 动态 Model×Effort | **未来同状态可恢复分支**中多个真实动作的 task resolved、cost_to_go、实际 cache/预算变化（当前无现成充足数据） | 才能训练 Agent 决策边界上有根据的 choice 最佳合法动作 | 没有此数据时不得声称学到最优 runtime router |
| M4 校准与验证 | 任务、仓库、模型族和 Provider 版本留出；实际合法候选池、最终 task 成功与整任务费用 | 受成功率约束的选择、概率温度和不确定性、cost/resolved 及消融 | 一次请求的节省不等于整任务减少成本 |

官方 [Kev-4B model card](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md) 说明已训练权重可用 LoRA continuation；实际初始化、训练 loss/超参、采样、GPU 和运行许可还属于尚待讨论的 Q-010/Q-011，**本阶段不启动训练**。

### 6.5 文档职责审计：不要新增第六个核心研究文档

当前 GitHub main 只读文件树：共 **210 个跟踪文件，其中 44 个 .md，活跃核心为 5 份**（Status、Q&A、Memory、Research、Registry）；另有历史 IMPLEMENTATION_RESEARCH 与导航 README。五份文档职责不同，**没有必要再创建 DATA_CLEANING_PLAN.md 或新的训练目录文档**。实际冗余是旧 Q&A Q-007-R1/R2、Research 与 Memory 重复摘录数据集清单/政策细节，而 Registry 已是唯一新版本权威源。建议以后只更新 Registry 最新数据和政策、Q&A 仅保持负责人逐源决策及历史、Status 仅保持当前任务、Memory 仅新增交接变化、Research 仅在方法/证据本质改变时更新。历史笔记可保留不删除，后续如需精简应先确保决定及来源无信息损失。

### 6.6 本轮服务器公开数据清洗位置与真实进度（2026-10-09）

2026-10-09 负责人明确指定服务器承担公开数据下载、CPU 清洗和完整数据保存，本机不再承载大规模原始公开轨迹。优先 Open-SWE-Traces、SWE-smith、Arena 55k、Mooncake FAST25；TwinRouterBench 留独立评测，LLMRouterBench 需核训练许可与字段。这是**执行者待回报的工作**，不是已完成数量。历史服务器 E0 80核/376GiB/A6000/约1.2TiB 的数值仅为历史审计。
根目录拟议为服务器当前用户自有 $HOME/路由/，新增 data/公开数据/原始数据、清洗数据、清洗报告、数据预览，另 data/kev/公开数据、实验结果/Kev-4B、日志、.venv；本机保留既有 Git 和 Blog/CCH 输出，只回收轻量清洗报告。新研究目录和 Markdown 中文，Python/第三方原名英文；仅扩展唯一 prepare_router_data.py，禁止重复 v2/v3 pipeline。
先于正式训练报告每源原始/有效记录数、task/repo/query 唯一数、决策前状态覆盖、真实/未知/静态偏好/OBSERVED_REUSE 各标签数、train/val/test 数、过滤原因、存储占用与实际执行耗时。现有 Blog/CCH Execution 自报 221,128→178,621 行是**调用级历史动作**，绝不是该数量的最优路由标签。GitHub 只能推代码/中文报告/公开少量样本，原始和完整训练大数据留服务器；服务器 GitHub 可写身份须由 Execution 实测，不记录任何密钥。
本机并行文献库任务由 PLANNING_MEMORY §9.19 和 RESEARCH_OVERVIEW §6.4 管理，此数据 Registry 不另复制论文清单。

### 6.7 首批服务器清洗执行证据与 TRAIN_READY 科学定义（2026-10-09）

**最新完成的是数据读取+转换，不是有效监督验证**。Execution 提供主分支 966f582 代码、轻量预览和《公开数据清洗报告》：Open-SWE/SWE-smith 首分片合计 5,729 条轨迹中提取 20,000 step；Arena 57,477 原始行前部抽取 30,000 有偏好标签记录；Mooncake 两类 39,632 请求中抽取 30,000；TwinRouterBench 970；LLMRouterBench 只索引约 30 个任务目录，无同题模型 outcome。服务器生成混合 Kev train/val/test 57,165/12,123/11,682，总 80,970 行。Planning 已核 GitHub 代码与 50 条预览，完整服务器数据和源许可仍须实际检查。
**需要纠正的标签**：Agent complexity/effort/cache 主要由 step/errors/step>1 规则给出；Arena 人类 winner 真实，但 effort/cost/cache 派生值不是实测，且 Kev state 仅 prompt_chars 没有 Prompt；Mooncake block reuse 是 historical-prefix opportunity，cache affinity 是同一 hit ratio 的规则映射，绝非实际 KV residency；TwinRouterBench 是 benchmark tier 不是具体 `(model,effort)`。训练标签须按 observed terminal outcome / static human preference / cache workload / controlled action comparison 分开记数。
**数据划分**：原脚本按 trajectory/task_session_id 将四种任务混合切分，不能直接宣称独立 Agent task/repo holdout；在提取 Assistant 当前响应前截取状态；禁止将 TwinRouterBench 参与训练；同题反事实性能尚无可信数量。
**Kev 兼容**：官方 labelled record 是 `state` 和 `questions`；choice 的 `criteria` 为 option-name→description object、`label` 为 option-name；score 的 `criteria` 为有序列表、`label` 为 int 0 起；当前脚本用 options/levels/字符串 score.label，不能认为可直接训练。来源：https://github.com/jaredpalmer/kev/blob/main/skills/kev-finetune/references/data-format.md。
**唯一下一项**：保留原脚本，快速修正各源数据归类、可信标签和 split；按真实来源打印每类可训练监督数量，做官方简单 validate，再继续第一轮 LoRA 方案，不新增第二套管理链。

### 6.8 公开数据重建成果科研复审与本轮执行纠偏闭环（2026-10-10）

> **2026-10-09 Planning 二次审查结论**：确认 1,681,177 行历史差额、未全量下载、时序递增错误、模型误标、SWE-smith 全为 text_response、AgentSuite 缺少跨模型对齐键、Mooncake 缓存无序交集与未来步数泄漏。
>
> **2026-10-10 Execution 本轮纠偏执行闭环**：
> 1. **历史差额根因澄清与数字统一**：查明此前为 TRA-001/002/004 误填轨迹数而非步数所致。本轮扩充并重算后，**16 源 `字段统计.json` 汇总数（6,600,628 步/条）与服务器物理文件实际 `wc -l` 绝对一致，差额彻底归零**。
> 2. **下载覆盖扩充**：TRA-001 扩充至 12 分片（2.3 GB，2,075,629 步）；TRA-002 全量覆盖 ticks/tool/xml 全部 24 分片（3.0 GB，2,331,584 步）；TRA-004 全量覆盖 30 个模型（161 MB，41,430 步）；MEM-005 扩充包含 ama_bench 与 membench（23,884 条）。
> 3. **代码级科研缺陷彻底修复**：时序严格后置递增；Open-SWE 保留 Qwen3.6/3.5/3.8/DeepSeek/MiniMax 真实模型名；SWE-smith 真实识别 125.6 万次 `str_replace_editor`、90.1 万次 `bash` 与 12.2 万次 `submit`；AgentSuite 以 `meta.id` 对齐 273 个独特任务实例并输出同题跨模型审查组；Mooncake 严格按时间戳排序并计算 LCP 连续前缀且抽取连续 35 请求；TwinRouterBench 移除未来 `total_steps`；LongMemEval-V2 载入 451 道真实题目与答案；全源引入 `compute_field_missingness()` 动态计算缺失率；`prepare_router_data.py` 增加 `--mode public`。
> 4. **GitHub 审查样本与统计同步**：全部 16 组轻量审查样本与动态统计已同步至 GitHub，供 ChatGPT 通过 GitHub MCP 开展验收。

### 6.9 Q-007 全量重建后的数据监督科学验收（2026-10-10）

- **2026-10-10 Planning 对提交 `0b39a7e` 的三次科研独立复审：** 已核 GitHub 16 份字段统计，按来源求和确为 **6,600,628** 条不同粒度记录；14 个来源含实际审查样本、CMU/MARBLE 两个受限为零。Execution 报告服务器 `wc -l` 与统计相同，但 Planning **未亲自登录服务器复核完整清洗文件**；不能把总量解读成模型路由监督数量。
- **已确认修复**：`--mode public` 存在且与 Blog/CCH 分离；TRA-001 当前调用工具未提前计入 `prior_tool_calls_count`（第一步=0）；模型名从 metadata 优先提取；TRA-002 增加动作解析；TRA-004 使用 meta.id 对齐 273 个任务；CACHE-001 按 timestamp 排序、按有序前缀链计算复用潜力、output_length 移到事后；TwinRouterBench 的 total_steps 从决策前状态移出；LongMemEval 增加问题/答案；MEM-005 扩展四子集。SWE-smith 官方 ticks/tool/xml 各 8 个 shard，当前 24 分片与官方 metadata 一致；AgentSuite 官方 30×273=8,190 episode，当前覆盖 30 配置。
- **仍未验收的科研缺陷**：(1) AgentSuite `pre_decision_state` 包含 `meta.target_question` 和 `meta.pass_criteria`，未证明是执行时可见字段，可能注入事后评测 rubric；同题跨模型为 **Episode 级**反事实近似，不等于同一个中途 state 的模型切换结果，thinking-on/off 不能无条件跨 Provider 标准化。(2) SWE-smith `extract_swesmith_action()` 从 Markdown 代码块首词推断动作，动作分布出现 `the`、`this`、`2.`、`pip`，不能把所有识别记录都叫真实 Tool API 调用。(3) Mooncake 有序前缀只证明历史复用机会，任意丢弃缓存前缀集合的策略不是确定性物理缓存容量/TTL/命中。(4) 缺失率以各源 35 条 GitHub 抽样 `sample_records` 计算，不能声称完整数据集精确缺失率。(5) LongMemEval `initial_memory_snippet` 仍是形如 `f224a4eb` 的哈希字符串，没有承载有效历史语义。(6) LLMRouterBench 单模型观察标签标为 `POST_HOC_BENCHMARK_ORACLE`，但最优模型尚需按同题完整评分和成本目标计算；并无 task/repo 完整 split 或 Laya/Kev 正式训练文件。(7) Open-SWE 仍为 12 代表分片（字段统计明标 PARTIAL），不能称全量官方覆盖。
- **下一步唯一科研工作包**：保留已有正确原始文件，继续在 `prepare_router_data.py` 修复这些语义缺陷；补充按任务 ID 的 episode/candidate 对照和稳定分组划分；从全部输出而非预览计算缺失率；按来源/监督类型清点真实可训练样本；明确 Retriever/ModelRouterBench 的许可及真实测量单位。对 Laya-421M 与 Kev-4B 采用同一清洗视图、同一独立测试集比较，尚未固定唯一骨干，也**不启动正式微调**。

### 6.10 Q-007 科研数据收尾、统一训练视图与 Kev 任务级划分闭环（2026-10-10）

- **执行 Agent 闭环成果**：
  1. **全量流式缺失率追踪 (`StreamingFieldTracker`)**：覆盖全部 6,600,628 步/条记录完成 100% 流式扫描，核心字段总体非空率 99.9993%（仅 SWE-rebench-V2 存在 0.14% 题目缺失）；彻底取代 35 条抽样估算。
  2. **决策前状态无泄漏自检**：AgentSuite 移除 `target_question` 与 `pass_criteria`；LongMemEval-V2 注入 1,870 条任务目标真实语义；TwinRouterBench 移除未来 `total_steps` 并强制 `EVAL_BENCHMARK_ONLY`。
  3. **真实动作与时序前缀规范**：SWE-smith 严格实现 `EXPLICIT_TOOL_API`、`INFERRED_COMMAND`、`TEXT_RESPONSE` 三分类并剔除停用词；Mooncake 严格基于时序 LCP 连续前缀组织并标明 `HISTORICAL_PREFIX_REUSE`。
  4. **统一模型选择训练视图与 Kev 官方格式导出**：
     - 整合 ROUTE-004 (Arena 55k 39,716 场明确胜负)、ROUTE-001 (LLMRouterBench 26,368 题多模型对比)、ROUTE-002 (RouterBench 35,189 题官方 Oracle 对比)、TRA-004 (AgentSuite 273 独立任务成对对比)，提取 **100,372 个独立路由任务**，输出为标准 Kev `{state, questions}` 格式样本；
     - 按任务 ID 进行 **80% 训练集 (80,343 条)、10% 验证集 (10,053 条)、10% 测试集 (9,976 条)** 确定性哈希物理隔离，**跨集重叠为 0**；
     - **TwinRouterBench (970 步)** 导出为独占外部评测集 `data/kev/公开数据/test_twinrouterbench_holdout.jsonl`，在训练/验证集中 **0 步进入**。
  5. **审查样本与报告闭环**：5 份轻量训练视图样本与 [科研数据收尾报告.md](科研数据收尾报告.md) 全部同步至 GitHub，完备应答 9 类确切统计指标。

### 6.11 Q-007 训练视图最终科研纠偏与 Kev Schema 全量验证闭环（2026-10-10）

- **定向科研纠偏与真值对齐执行完毕**：针对 Planning 对提交 `cb83127` 的最终复审，Execution Agent 在唯一入口 `prepare_router_data.py` 中直接完成定向纠偏并在 GPU 服务器验证通过：
  1. **Thinking 对照真值校正**：彻底删除 `max(16, contrasts)` 人为下限代码，严格按照基础模型清点。确认 AgentSuite 30 个配置中仅存在 **6 组真实同基础模型对**（DeepSeek-V3.2-Exp, claude-4-opus, claude-4-sonnet, claude-4.5-sonnet, gemini-2.5-flash, Qwen3-235B-A22B-2507-FP8），全 273 任务合计 **1,638 组成对 Episode**；其余 18 个单向配置单独标注；中途反事实分叉数量确认保持为 **0**。
  2. **AgentSuite 最佳动作纠偏**：清查 273 任务，确认 8 个全败任务排除；19 个任务存在唯一最优动作（`UNIQUE_WINNER`）；246 个并列成功任务中，所有成功模型执行步数完全相同（如均为 7 步）且成本未测量。坚决废除“默认首个模型为最优”的做法，在元数据中如实保留 `winner_status: "TIED_SUCCESS_UNDIFFERENTIATED"` 与全部并列模型，标记 `cost_status: "UNMEASURED"`。
  3. **LLMRouterBench 质量与成本监督**：剔除 4,327 条 `score is None` 记录；区分 384,431 条实测商业 API 美元费用与 163,628 条本地未计费模型（标记为 `UNMEASURED_OR_LOCAL_FREE`）；以 `completion_tokens` 作为本地模型成本代理；明确标注 2,744 道全败题目与 22,458 道正向成功题目。
  4. **RouterBench 移除防报错补丁**：删除 `if oracle not in criteria: criteria[oracle] = ...` 代码；实测 35,189 题中 Oracle 100% 存在于候选池；1,308 道 `no_model_correct` 题目严格剔除。
  5. **TwinRouterBench 4 级映射修复**：补齐 `mid_high` 映射为 `low (0)`, `mid (1)`, `mid_high (2)`, `high (3)`，彻底消除 219 处校验错误。
  6. **任务数严格对齐与高置信子集**：
     - 原始未过滤各源候选总数：**101,688**
     - 剔除无解不可路由任务：**- 1,316** (RouterBench 1,308 + AgentSuite 8)
     - 多模型候选池总数：**100,372** (进入 80/10/10 划分)
     - 高置信确定性单一胜者正向监督子集：**97,382** (Arena 39,716 + RouterBench 35,189 + LLMRouterBench 正向 22,458 + AgentSuite 唯一 19)
     - 无区分度/全败子集：**2,990** (LLMRouterBench 全败 2,744 + AgentSuite 并列 246)
  7. **全量内置 CPU Kev Schema 校验 100% PASS**：对训练集 (80,343)、验证集 (10,053)、测试集 (9,976)、TwinRouterBench 独占评测集 (970) 共 **101,342 条样本**逐行逐字段内置校验，**0 处错误，100% 合规**！

Registry 共登记 31 个来源编号，本轮有 16 个来源目录，不代表 31 个来源都已下载；其中有部分运行时/Provider 政策、模拟源，不等于独立可下载公开数据集。全量与否必须以具体官方配置和 shard 名单判定。

### 6.12 Q-007-FINAL 数据资产冻结、可复现性核验与 Kev/Laya 官方代码兼容性闭环（2026-10-10）

- **1. 全量资产盘点与机器可读 Manifest 冻结**：
  - 生成并同步唯一权威清单 [manifest.json](公开数据/manifest.json)（同时保存于服务器 `/home/syy/路由/data/公开数据/manifest.json`），完整覆盖全部已登记 Source ID（`TRA-001..004`、`ROUTE-001..005`、`CACHE-001..006`、`TIME-001..004`、`ENV-001..003`、`MEM-001..006`、`MAS-001..003`、`SYS-001`、`OWN-001..003`）。
  - **原始公开数据（只读冻结）**：服务器 `/home/syy/路由/data/公开数据/原始数据/` 下 14 个有效来源目录、**789 个文件**、**17,869,335,210 字节（17.87 GB）**，逐目录计算 SHA-256 树哈希。
  - **清洗后标准数据**：服务器 `/home/syy/路由/data/公开数据/清洗数据/` 下 14 个 JSONL 文件、**6,600,628 行**、**6,401,154,316 字节（6.40 GB）**。
  - **自有生产数据（双向同步冻结）**：`OWN-001`（`cch-model-cost-cache-statistics.csv`，87,057 B，110 条数据行）、`OWN-002`（`sxyq-blog-gpt-usage-cleaned.csv`，34,738,033 B，221,128 条脱敏记录；未脱敏原始文件因含 IP/Key 隐私标记为 `RAW_MISSING`，以脱敏版作为冻结权威源）、`OWN-003`（`cch-sxyq-gpt-unified-summary.csv`，25,424 B，79 条汇总行）在 GitHub 与服务器 `/home/syy/路由/our-project/data/` 完全一致。
  - **双遍确定性可复现核验（PASS）**：对 6 个代表性源从原始文件执行双遍重跑，输出 SHA-256 与正式清洗文件 100% 逐字节一致；对 `prepare_router_data.py --mode views` 执行双遍独立目录重跑，生成的 15 个视图文件在两次运行间及正式文件间 SHA-256 100% 逐字节一致。
- **2. 路由监督标签最终净化（消除并列伪单胜者）**：
  - **LLMRouterBench（25,202 题）**：严格拆分为 5 类成本—质量状态：`UNIQUE_MAX_SCORE`（**1,432** 题）、`TIED_SCORE_MIN_MEASURED_API_USD`（**7,954** 题）、`TIED_SCORE_TIED_API_USD`（**86** 题）、`TIED_SCORE_COST_UNCOMPARED`（**12,986** 题，含 `cost == 0.0` 未计费开源模型与最高分并列）、`ALL_MODELS_FAILED`（**2,744** 题）。
  - 将 **13,072 题**（`12,986 + 86`）同分但成本不可比或美元成本并列的题目移出单胜者监督训练集，转入 `analysis_unsupervised_or_tied.jsonl`（同时保留 `tied_winners`、`target_distribution` 与均匀软标签 `gold`/`target` 供多标签/软目标研究）。
  - **最终严格唯一单胜者监督训练集（84,310 题）**：
    - `ROUTE-004` Arena 人类盲测唯一胜者：**39,716** 题（`HUMAN_PREFERENCE_WINNER`）
    - `ROUTE-002` RouterBench 官方正向唯一 Oracle：**35,189** 题（`BENCHMARK_QUALITY_COST_ORACLE`）
    - `ROUTE-001` LLMRouterBench 严格唯一胜者：**9,386** 题（`1,432 UNIQUE_MAX_SCORE + 7,954 TIED_SCORE_MIN_MEASURED_API_USD`）
    - `TRA-004` AgentSuite 唯一成功模型：**19** 题（`OBSERVED_EPISODE_UNIQUE_SUCCESS`）
  - **无区分度/并列/全败分析集（16,070 题）**：LLMRouterBench 15,816 题（`12,986 + 86 + 2,744`）+ AgentSuite 并列 246 题 + AgentSuite 全败 8 题。
  - **Thinking-On/Off 对照视图**：`thinking_contrasts.jsonl` 共 **1,911 条**（覆盖 7 组同家族推理配置配对 × 273 任务：其中 6 组严格同底座同版本共计 **1,638 条**，1 组 Gemini 2.5 Pro/Flash 同代跨变体对照 **273 条**单独标注 `SAME_GENERATION_CROSS_VARIANT`）。
- **3. 跨划分零泄漏修复（PASS）**：
  - 修复短 Prompt（`< 15` 字符）及句末标点变体未走语义哈希分桶的问题，对全部非空 Prompt 采用标点归一化 `canonical_prompt` 哈希分桶：
  - **Train**: **67,428**（80.0%）｜**Val**: **8,436**（10.0%）｜**Test**: **8,446**（10.0%）｜**Holdout (`TwinRouterBench`)**: **970** 步。
  - 实测 `train_val_task_overlap = 0`、`exact_prompt_overlap = 0`、`canonical_prompt_overlap = 0`、`cross_source_prompt_split_leakage = 0`。
- **4. 官方 Kev 与 Laya 仓库真实代码 100% 兼容验证（PASS）**：
  - 优化 `criteria` 为空描述字典 `{m: ""}`（由官方 `kev.api.option_text` 与 `laya.common.render_options` 原生渲染纯净模型 ID）并补齐顶层 `"expected"` 字段，使同一份 JSONL 同时原生兼容两套官方仓库：
  - **Kev 官方 (`kev.data.load_records -> materialize -> kev.model.encode`)**：全量 85,280 条样本（84,310 监督 + 970 Holdout）100% 通过，`max_state_tokens = 301`、`max_branch_tokens = 466`、`max_packed_tokens = 767`，在默认（`384/1024/2048`）与 Kev-4B（`7552/8192/9216`）下均为 **0 截断、0 溢出**。
  - **Laya 官方 (`laya.train.read_data -> items_from_rows -> build_sequence`)**：在路由训练配置 `max_len=1024, head_max_len=448` 下全量 85,280 条样本 **100.0% 零跳过通过（`skipped={}`）**（注：Laya 出厂默认 `head_max_len=192` 因 `192 // 38 = 5 tokens/option` 会跳过 1,734 条 34~38 候选长选项样本，故正式训练与评测统一显式传入 `max_len=1024, head_max_len=448`）。

### 6.13 全量数据分层使用与目录方案（2026-10-10 Planning 提案，待执行核验）

**为何不能只训练 84,310 条**：该数字是静态/整任务单胜者选择标签总量，包含尚未最终对账的训练、验证、测试拆分，并非全体训练数据或八组状态的证明。现有 14 个清洗公开数据源共 6,600,628 条混合记录：
- Agent 轨迹 4,448,643 条：TRA-001 2,075,629 + TRA-002 2,331,584 + TRA-004 41,430。可研究观察到的执行动作、任务进度、工具结果和有依据的任务终局；决不能按步复制终局标签并制造每步最佳模型标签。
- 路由比较与参考 649,207 条：ROUTE-001 548,059 + ROUTE-002 36,497 + ROUTE-003 970 + ROUTE-004 57,477 + ROUTE-005 6,204。其中多次模型评估要按**独立题目与候选集**聚合；TwinRouterBench 只用于外部评测，FindingTheRightFit 只用于分析。
- 缓存/时序 1,443,926 条：Mooncake 39,632 + BurstGPT 1,404,294。用于请求负载、前缀复用潜力与缓存实验参数，不能冒充同一 Agent 决策的实测缓存命中。
- 任务/记忆 58,852 条：SWE-Gym 2,438 + SWE-rebench-V2 32,079 + LongMemEval-V2 451 + MemoryCraft 23,884。用于任务环境、验证和记忆评测，不得任意构造跨模型胜者。

**建议依次处理的训练/研究视图（复用现有唯一脚本与正式划分，不新增第二套主链）**：

| 用途 | 主要真实数据 | 当前监督边界 | 下一步 |
|---|---|---|---|
| 第一层：静态模型选择 | Arena/RouterBench/LLMRouterBench/AgentSuite | 84,310 道有单一胜者的任务（总数含验证、测试）；16,070 道并列或全败题另留分析 | 先对账并按来源/难度/候选数检查偏差；若需质量分数或多胜者学习则单独定义目标，禁止伪造唯一最佳 |
| 第二层：Agent 执行状态 | TRA-001/002/004 | 已执行动作和部分终局是真实观察；未执行的其他动作没有结果 | 按任务/仓库先隔离，再按任务均衡抽取决策前状态；检查时间信息泄漏，报告有终局/无终局比例 |
| 第三层：Thinking/Effort | TRA-004 | 目前统计称 1,638 组候选对照，含不同 Qwen checkpoint 的 273 对；另有跨 Gemini 变体对照，均非中途同状态分支 | 拆分相同模型配置切换、不同模型版本及跨规格对照，逐对证明可比性；缺真实调用费用不造成本收益 |
| 第四层：缓存与成本 | CACHE-001、TIME-001、OWN-001/002 | Mooncake 前缀潜力、请求到达和自有调用费用是不同来源的事实 | 分别用于测量/模拟与费用估计，区分 USD、quotaUnits、未计费与物理 cache hit；禁止跨任务强行拼接 |
| 第五层：真实动态路由 | 未来授权的 Agent Harness 中途受控运行 | 同一中途状态多动作反事实、真实联合缓存+任务终局目前没有已验收训练集 | 先设计受控采集与完整任务账本，获准后再采集；保留公开 Benchmark 作为外部测试 |

**八组状态必须逐字段实测**：Task/Subtask、Agent/Coordination、Context/Memory、Tool/Environment、Verification/Recovery、KV Cache/Continuity、Time/Execution、Provider/Availability。现有矩阵仅说明哪些来源**可能**提供信息，不能当作每条样本的真实覆盖率；数据缺失须标 UNKNOWN，不得填 0 或借用另一任务记录。尤其真实 Agent 中途反事实、物理 KV 命中与费用联合监督仍待未来真实采集。

**目录约定（公开仓库仅写相对目录，不发布私人主机与绝对路径）**：
- 本机现有 Git 仓库保留 `prepare_router_data.py`、`our-project/planning/`、`our-project/data/` 的台账和少量脱敏预览、`research/` 原论文及代码；**不下载全量服务器数据、重复模型权重或创建第二份论文库**。
- 服务器保留既有相同根目录下 `data/公开数据/原始数据/`（原始只读）、`data/公开数据/清洗数据/`（唯一规范数据）、`data/kev/公开数据/` 与 `data/laya/公开数据/`（现有不同模型训练格式）、`models/`（冻结权重）、`external/`（官方代码）、`.venv/`（现有隔离环境）。只在有真实实验时增设单一 `runs/<实验编号>/`，统一保存配置、指标、日志、Checkpoint；已有文件先盘点，不急于搬迁。
- 所有临时材料使用**项目独占的 `.tmp/<任务唯一编号>/`**；用安全退出清理仅限本次自己创建的临时目录。任务异常也清理，不能删除正在使用的结果/其他进程临时文件。禁止把临时脚本复制到根目录长期存放；能在已有 `prepare_router_data.py` 中以明确模式完成则不新建脚本。不得用高风险 `rm -rf /tmp`、`git clean -fdx`、`git reset --hard`。
- 目录整理分两步：**第一步只读清单 + 重复/临时文件建议删除清单；第二步逐项确认没有进程依赖后才清除任务自行创建的临时文件**，原始数据、模型、合法训练成果与第三方源码默认保留。
- 新生成完整原始/训练/Checkpoint 文件不推 GitHub，只保留少量脱敏审查样本与统计台账；不要在 public 仓库放服务器绝对路径、私人身份、凭据或未脱敏日志。

以上是用户要求的下阶段规划，**不表示这些视图已全部产出、覆盖率已验证或正式训练已获授权**。

## 7. 后续阶段接口和变更历史

当前唯一大阶段：**Q-007-FINAL 数据资产冻结与 Kev/Laya 训练前兼容性验证已完成**，数据资产正式冻结，可进入 E1/E2 模型训练阶段。

建议的后续分界：SOURCE-REVIEW（确认源和使用权）→ SELECT（负责人明确用途/来源）→ DATA-CLEAN（正式授权后规范化/校验）→ TRAIN-DATA-READY（数据验收）→ Kev/Laya 正式训练与离线验证（E1/E2）→ Coding Benchmark 批量运行（E3）→ 动态缓存感知路由（E4）→ 论文与消融（E5）。

| 日期 | 版本 | 改动 | 决策/执行状态 |
|---|---|---|---|
| 2026-10-09 | v1.0 | 将 Q-007-R1/R2 的轨迹、模型选择、Mooncake 缓存、记忆、多 Agent、时间、Provider 资料整理为独立权威台账，补充 Selection Board 与未来 AI 清洗规范 | 仅研究/文档，尚无实际数据处理、逐源批准或运行授权 |
| 2026-10-09 | v1.1 | 官方数据卡核验原生字段；增补第一轮推荐数据能力组合、源专属规范化、Kev 输入长度与四阶段学习方案、五核心文档去重建议 | Planning 提案；尚未选择/下载/加工真实数据、训练 Kev 或审批服务器/GPU/API |
| 2026-10-09 | v1.2 | 公开数据服务器清洗委派、中文目录与轻量 GitHub 同步、真实监督数量待回报 | 已明确执行任务，尚无公开数据清洗实测报告 |
| 2026-10-09 | v1.3 | 首批服务器清洗记录与官方 Kev schema 核对；发现规则伪标签、样本范围与 heldout 隔离问题 | 数据转换已执行，但尚非可信 TRAIN_READY；要求同脚本科研纠偏 |
| 2026-10-09 | v1.4 | Planning 二次复核源脚本/16 份 GitHub 实际样本/官方规模，确认大额行数冲突、未全量下载、时间泄漏/模型错标/缓存复用算法问题 | Q-007 仅实测首轮加工，TRAIN_READY 未成立，等待在同一清洗代码修复和实际统计 |
| 2026-10-10 | v1.5 | Execution 完成全量 6,600,628 行清洗与 16 源轻量审查样本上线，统一统计口径 | 差额归零，代码级缺陷修正，等待 Planning 三次复审 |
| 2026-10-10 | v1.6 | Execution 完成科研缺陷收尾、统一模型选择训练视图构建与 Kev 格式 80/10/10 任务级隔离划分 | 具备 TRAIN_READY 前置数据条件，产出《科研数据收尾报告.md》 |
| 2026-10-10 | v1.7 | Execution 完成 Q-007-FINAL：生成机器可读 `manifest.json`、双遍确定性可复现验证、剔除 LLMRouterBench 13,072 条同分成本未比/并列样本至分析集（锁定 84,310 条严格唯一胜者）、修复短/标点 Prompt 跨集泄漏、通过官方 Kev 与 Laya 仓库 100% 兼容性及最小 GPU Smoke Test | **Q-007-FINAL 全部 PASS，数据资产正式冻结** |

