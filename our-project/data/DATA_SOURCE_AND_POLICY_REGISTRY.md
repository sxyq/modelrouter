# ModelRouter · 数据源、模型能力与缓存政策统一台账

> **版本 v1.1｜建立：2026-10-09；官方数据结构只读核验与清洗/训练方案更新：2026-10-09｜阶段：E-DESIGN / Q-007 第一大阶段｜状态：候选目录，未完成清洗和训练许可核验**
>
> **唯一职责**：此文件是公开数据源、数据许可、八组状态覆盖、模型/Provider 能力、缓存/定价政策及未来“候选 → 选择 → 数据加工 → 验收”信息的**唯一详细台账**。它不是新的执行流水线或运行时政策数据库。
>
> **权威性分工**：用户批准/否决、Q-ID 与日期唯一记录在 [EXPERIMENT_QA.md](../planning/EXPERIMENT_QA.md)；阶段/授权/唯一当前任务由 [PROJECT_STATUS.md](../planning/PROJECT_STATUS.md) 决定；研究方法在 [RESEARCH_OVERVIEW.md](../planning/RESEARCH_OVERVIEW.md)。此台账只记录具体资产及其**证据和准备状态**，不得将 Planning 优先级当作用户批准。
>
> **禁止误读**：登记 ≠ 已下载；官网有目录 ≠ 已核每个型号；公开许可证 ≠ 商业 API 输出自动可训练；可复用前缀 ≠ 生产缓存命中；task benchmark ≠ agent trajectory；API 调用成功 ≠ task resolved；跨模型同题评估 ≠ 相同中途状态的反事实。
>
> **当前授权**：仅对公开资料进行只读核查并更新本台账，不启动数据大规模下载、清洗、训练、服务器/GPU、付费 API 或新的 Harness 执行链。全部候选默认未获用户逐源批准。

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
| TRA-001 | [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | SWE 任务/Agent 轨迹、消息、工具、repo、resolved；2026 v1.1/v1.2 已扩展，版本待锁 | 任务、工具、验证/恢复、上下文、时间 | S1；数据卡 CC BY 4.0，后续锁定子集/检查字段与署名 | **P0·候选**，观察到的执行动作/成功标签 |
| TRA-002 | [SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories) | 公开训练轨迹子集；任务、工具、模型执行历史；不可将 SWE-smith 任务数当轨迹数 | 任务、工具、时间、验证 | S1；数据卡 MIT，生成模型输出/源任务条款仍需再审 | **P0·候选** |
| TRA-003 | [CMU Agent Trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 多 Benchmark/多模型 episode、逐步消息、reward、部分 Token/时间 | 任务、工具、时间、模型异构 | S1；**gated/训练许可不明** | 待核，不进训练包 |
| TRA-004 | [AgentSuite multi_challenge](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 多模型同任务轨迹、messages、eval_result、部分 thinking 开关 | 任务、模型比较、工具、时间 | S1；许可证待核；thinking 开关不等于标准 effort | 待核 |
| ENV-001 | [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | 真实 repo/issue/测试/可执行任务环境 | 任务、验证/恢复 | S1；主要是**任务**不是完整路由轨迹 | 未来任务源候选 |
| ENV-002 | [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | 软件工程多语言任务环境及评测输入 | 任务、验证、复杂度 | S1；任务用途与 train/test 污染待核 | 未来任务源候选 |
| ENV-003 | [SWE-smith Tasks](https://huggingface.co/datasets/SWE-bench/SWE-smith) | 批量软件工程 task/环境，非等量成功轨迹 | 任务、环境 | S1；与 TRA-002 上游有关联、需同任务去重 | 未来任务源候选 |

### 1.2 请求级模型选择与偏好监督

| ID | 来源 | 真实监督粒度 | 可训练性 | 规划用途 |
|---|---|---|---|---|
| ROUTE-001 | [LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | 同一静态任务的多模型回复、评分、Token/费用 | **数据包及原数据许可尚未核清**，隔离 | P0·模型能力与成本先验；**不能**推断 Agent 中途换模型的 outcome |
| ROUTE-002 | [RouterBench](https://huggingface.co/datasets/withmartian/routerbench) | 同 Prompt 的多个模型回答、性能评分、估计成本 | **数据卡许可标签不清楚，待审** | 静态模型胜负；不包含连续 Agent 状态 |
| ROUTE-003 | [TwinRouterBench Static](https://huggingface.co/datasets/Amorph/TwinRouterBench) | Agent 可见前缀 → 抽象能力 tier 标签 | S1；Apache-2.0；需防与最终对照基准泄漏 | 抽象能力档位训练候选；不是 model×effort |
| ROUTE-004 | [Arena Human Preference 55k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | 同题两模型人类胜负/平局偏好 | S1；数据卡 Apache-2.0；用途仍需复核 | RouteLLM 类偏好预训练；**不是 task resolved** |
| ROUTE-005 | [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | model×harness 任务得分、Token、成本 | **原数据发布者禁止训练/微调/蒸馏** | 仅分析和研究，不进入训练，也不转成蒸馏标签 |

### 1.3 KV Cache、请求时间、服务端资源

| ID | 来源 | 关键字段与性质 | 可以研究什么 | 不可以替代什么 |
|---|---|---|---|---|
| CACHE-001 | [Mooncake FAST'25](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release) | 匿名生产请求时间、输入/输出长度、前缀块 hash_ids；conversation 与 toolagent 负载、合成负载分开 | **P0·OBSERVED_REUSE**、潜在命中、会话连续性、到达模式 | **不是**商业 Provider 实报 cached_token |
| CACHE-002 | [Mooncake 旧版 trace](https://github.com/kvcache-ai/Mooncake/tree/main/arxiv-trace) | 旧版匿名前缀/请求记录 | 历史请求变化 | 版本可能重合；不得双计 |
| CACHE-003 | [Mooncake Cache Benchmark](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html) | 基于块哈希/容量/淘汰与缓存策略的回放和指标 | **SIMULATED** 读写与 hit rate | 不是真实原始 API 命中记录 |
| CACHE-004 | [KV Cache Workload Bench](https://github.com/hokiyoung/kv-cache-workload-bench) | 合成/派生共享前缀、会话、并发、驱逐 workload | 模型化缓存压力与容量 | 不是实测封闭 API usage |
| CACHE-005 | 未来 Provider 实际 Usage（无单一公开仓库） | requested model、真实 cached/read/write Tokens、provider Endpoint、账单和时间 | **MEASURED** 的唯一权威来源之一 | **当前本项目未持有充分的 Agent 同状态原始计量样本** |
| CACHE-006 | [vLLM Metrics / Prefix caching](https://docs.vllm.ai/en/latest/usage/metrics/) | 获准运行后可观察引擎实例的实际缓存统计 | 本地引擎 MEASURED | 并非预先存在的独立下载数据集；未经许可不得部署采集 |
| TIME-001 | [BurstGPT](https://github.com/HPMLL/BurstGPT) | 匿名生产服务请求、时间、Token、会话/耗时 | **P0·真实时间与服务负载** | 不含可靠完整 Agent task outcome 与 KV 命中 |
| TIME-002 | [Alibaba xMaaS 2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas) | MaaS 集群实例/资源/显存/GPU/负载时序 | 系统级容量与时间压力 | 不是逐请求 Agent 动作真值 |
| TIME-003 | [Alibaba GenAI Trace](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) | 真实生成式服务队列/资源和时延（包括非 LLM） | 系统请求并发和资源预算参考 | 非编码 Agent 或路由胜负 |
| TIME-004 | TRA-001/TRA-002 的时间子视图 | 已发生 step/turn/工具/局部时间 | Agent 剩余步骤/时间信息 | 不另计一个独立数据集；无初始预算则剩余额度 UNKNOWN |

### 1.4 长期记忆、多 Agent 协作

| ID | 真实来源 | 可覆盖状态 | 主要限制 |
|---|---|---|---|
| MEM-001 | [LoCoMo](https://github.com/snap-research/locomo) | 会话历史、事件、时间推理、摘要/证据 | 长记忆 QA，不提供 Kev 最优动作 |
| MEM-002 | [LongMemEval](https://github.com/xiaowu0162/longmemeval) | 跨会话记忆、用户事实更新/冲突、检索 | benchmark 留出与训练许可需核 |
| MEM-003 | [LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) | 长期 Web Agent 历史、记忆、流程、变化环境 | P0·长期执行/记忆候选；训练可用 split 与许可证仍需确认 |
| MEM-004 | [MemoryAgentBench](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) | 增量记忆与检索、测试时信息更新 | 非路由成功率标签 |
| MEM-005 | [MemoryCraft](https://huggingface.co/datasets/daven3/MemoryCraft) | 多记忆数据源统一结构 | **集合/汇编**，与上游任务重合；按源许可证去重 |
| MEM-006 | [LongBench](https://github.com/THUDM/LongBench) | 上下文长度、长文本检索/归纳负载 | 文本能力压力，不是 Agent Memory 真迹 |
| MAS-001 | [MARBLE/MultiAgentBench](https://github.com/ulab-uiuc/MARBLE) | 角色、协作拓扑、共享记忆、里程碑 | P0·任务/Schema 源；预先存在的逐步轨迹量待核 |
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

## 7. 后续阶段接口和变更历史

当前唯一大阶段：**Q-007 数据来源候选目录**，先按本台账登记、核证与选定；数量、实际清洗、Kev 训练方式、Provider 部署和正式评测后议。

建议的后续分界：SOURCE-REVIEW（确认源和使用权）→ SELECT（负责人明确用途/来源）→ DATA-CLEAN（正式授权后规范化/校验）→ TRAIN-DATA-READY（数据验收）→ Kev training design（Q-010/Q-011）→ E1～E5 按既有里程碑与授权推进。此为**数据管理工作流**，不是第二条可运行 Agent/Router 工程链。

| 日期 | 版本 | 改动 | 决策/执行状态 |
|---|---|---|---|
| 2026-10-09 | v1.0 | 将 Q-007-R1/R2 的轨迹、模型选择、Mooncake 缓存、记忆、多 Agent、时间、Provider 资料整理为独立权威台账，补充 Selection Board 与未来 AI 清洗规范 | 仅研究/文档，尚无实际数据处理、逐源批准或运行授权 |
| 2026-10-09 | v1.1 | 官方数据卡核验原生字段；增补第一轮推荐数据能力组合、源专属规范化、Kev 输入长度与四阶段学习方案、五核心文档去重建议 | Planning 提案；尚未选择/下载/加工真实数据、训练 Kev 或审批服务器/GPU/API |
