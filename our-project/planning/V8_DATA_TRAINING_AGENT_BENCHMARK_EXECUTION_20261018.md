# ModelRouter · V8 数据增补、Laya/Kev 双训练与 Agent Benchmark 长周期执行方案

> 日期：2026-10-18；阶段：**执行研究计划与数据源复核**，不是“已下载/已训练/已运行 Agent”的证据。本文件不重写 [V8 论文实验方案](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)，也不取代 [数据与许可唯一台账](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。已完成的 F05 / F03 进度以服务器最新 `run.json/cursor.json/queue_state.json` 为准。已确认用户授权在自有 A6000 上开展 Laya、Kev 的新训练以及本机 Benchmark 工程准备；**新付费 API 调用仍需等 URL/Key、明确额度后启用**。

## 0. 现在执行的两条工作线

- **服务器：数据→清洗→可用标签入库→逐阶段训练→收敛观察。** 保留既有 V2.1 正式 Laya 38 组原协议，新的数据/损失/KV 联合实验另外编号、另外输出。Kev-4B 优先按同源 V2.1 F05 L1+L2 进行第一阶段跨基模对照，再以合法补充数据做独立训练分支。单 A6000 试测双训练并发的**合计吞吐/显存/功耗/主任务延迟**，收益和安全共同决定长期策略。
- **本机 Mac：Benchmark 源码、外部路由方法源码、最简单 Agent、Laya 最优权重、策略接口、真实输入输出及账本。** 今晚不使用新付费 API。运行 **Oracle/Marker/Mock** 只算环境或接口烟测，不算 Agent 成功。

三名子代理可分别负责：A 服务器数据与训练；B 本机 Benchmark/单 Agent；C 外部 RouteLLM/SR-KNN/指标账本。主代理负责资源协调、进度与最终提交，**同一 SSH/GPU 队列仅由 A 管理**。

## 1. 已检索的公开数据：按“能够训练什么”而非“行数多少”分类

| 台账/来源 | 公开链接、确认字段 | 训练/用途 | 今晚动作 |
|---|---|---|---|
| **TRA-001 NVIDIA Open-SWE-Traces** | https://huggingface.co/datasets/nvidia/Open-SWE-Traces；真实 Agent 消息、工具轨迹、`repo/instance_id/trajectory_id/resolved`，`resolved=-1` 为未知；CC BY 4.0。源 v1.0 曾清理污染轨迹，v1.1/v1.2 有修订，**数量随 revision 变化** | 已执行动作、决策前状态、可核对终局结果；不是未选择模型的反事实真值 | 先盘点既有 TRA-001 文件和修订 SHA；仅下载未拥有的可用 shard。隔离 `resolved=-1`；去除未来文本与 solution |
| **TRA-002 SWE-smith-trajectories** | https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories；Parquet `messages/instance_id/resolved/model/traj_id/patch`，MIT；官方页有 `tool/xml/ticks` 多个视图 | 已执行轨迹及成功/失败监督，`patch` 只可做结束后标签/排查，不能进入决策前输入 | 原项目已部分/全量加工，优先核真实物理文件及视图重复；需要补缺才下载 |
| **TRA-004 AgentSuite multi_challenge** | https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories；30 模型×273 任务公开说明，`messages/eval_result/sampling_params/model_path`；数据仓库无清晰统一许可证声明，应按具体记录和来源再核 | 同任务不同模型及 thinking on/off 的**观察性**对照；不等于同一中途状态分支或原生 Effort 全空间 | 优先复用已加工 8 模型；核许可后才选可新增源。多模型 `task_id` 配对，禁止把模型变体混成相同权重的 effort |
| **CooperBench 双代理/团队轨迹（候选）** | https://huggingface.co/datasets/CooperBench/cooperator-dual-policy-sft-data 及 https://huggingface.co/datasets/CooperBench/team-trajectories；公开卡展示角色/agent_id、agent 日志、结果文件；许可需按各自具体版本核对 | 用于解析真实 agent role/subtask/handoff 与观察性结果；不是所有模型的最佳路由动作标签 | 本轮主要做字段级小样本清洗、角色 Schema；不要据此虚构 agent 最优模型 |
| **CACHE-001 Mooncake FAST'25** | https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release；`timestamp/input_length/output_length/hash_ids`，512-token 前缀块；匿名服务请求，不包含 Agent 任务结局；文档与 LICENSE 需随下载修订记录 | **OBSERVED_REUSE_OPPORTUNITY**：前缀块可复用机会、时序和容量策略，不是实际 provider cached_read，也不等于跨模型可迁移 KV | 先复用已登记 39,632 条与既有索引，避免与旧版 CACHE-002 重复计数；可训练“可复用前缀”辅助预测或做缓存模拟，独立 supervision type |
| **TIME-001 BurstGPT** | https://github.com/HPMLL/BurstGPT；请求到达负载与 Token 工作量，缺 Agent 最终成功 | 时间/负载特征及仿真先验，不能合成某一 Agent Episode 的费用 | 使用已加工数据，不为本轮重复下载 |
| **CACHE-005 真实模型调用 usage（未来新增）** | 仅在获授权的 Agent 回合中通过 provider 或本地引擎记录 `cached_read_tokens/cache_write_tokens/price_snapshot/provider/model/revision`；实际可得字段可能缺失 | 仅这一类可形成 **MEASURED** 的真实本项目缓存/费用监督，与同一 `episode_id/decision_id` 联结 | 本机账本提前保留字段；待明早 API 授权后实跑，不填估算为实测 |
| **ROUTE-003 TwinRouterBench** | https://github.com/CommonstackAI/TwinRouterBench；静态 970 标签 + 动态 SWE-bench Agent 评测，原台账已标 `EVAL_BENCHMARK_ONLY` | **禁止训练/调参泄漏**，只用作外部路由对照评测 | 本地单独克隆进 `external/benchmarks/`；不加入训练 |
| **ENV-004 Terminal-Bench 2.1** | https://github.com/harbor-framework/terminal-bench-2-1；项目锁定官方任务树 commit `7131e4375048a0e408a8fb404b5f499d726b695b`，89 题；项目划分 Canary=8、DEV=24、Final=57 | **严禁训练**；Final 57 永久封存至最终一次测试 | 本机只取官方源码/Harbor 环境，先跑 `fix-git` 与 `count-dataset-tokens` 的不付费 smoke |

**关键限制**：公开数据不存在已验证的、同时具备当前前决策状态、所有合法 `Model×Native Effort` 动作的真实反事实成败、同任务物理 KV 实测及最终 USD 的现成联合表。**不允许按 ID 或语义相似度横向拼接不同来源制造联合真值**。Route-001/002 的历史许可待核行不因本方案自动解禁，禁训/仅分析源不进入训练。随源记录版权/隐私、版本、hash、下载日期、单位和原始路径。

## 2. 服务器数据落地与清洗（复用现有位置）

服务器项目根目录按现有现场确定，历史常见为 `/home/syy/路由`；不可创建第二套项目/重复下载。先读取现有 `our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md`、`data/公开数据/原始数据`（若不存在则检查实际已有原始存储路径）、`data/公开数据/清洗数据`、`runs/MR-ALLDATA-PREP-20261011/` 下已有 `quality_grading_v2_1` 索引，建立 path/revision/sha/size 对账。新增只放已有同类原始/清洗目录，不以这里的示意目录覆盖现场真实路径。

新增派生数据单独存 `runs/MR-V8-DATA-EXTENSION-20261018/{manifests,views,stats}`；中间 I/O 在 `.tmp/modelrouter_v8/`，运行完可清理；大原始数据和权重不入 Git。每个新数据源只执行一次下载，尽量校验 immutable revision，原始 SHA256 与派生 manifest 做 lineage。

转换成三个**互不冒充**的训练视图：
1. `OBSERVED_AGENT_OUTCOME`：`task_id/repo_id/episode_id/step_id/observed_at/state_before/observed_model/observed_effort_or_unknown/known_terminal_outcome/provenance`；同仓库/同任务/同轨迹所有前缀必须在一个 Train/Val/Test 侧；`resolved=-1` 不用作负样本；不可见未来 evaluator 或最终 patch。
2. `CACHE_REUSE_OPPORTUNITY`：`timestamp/input_length/output_length/prefix_hash_ids/estimated_reusable_blocks/cache_policy_assumption`，证据标 `OBSERVED_REUSE`；独立缓存辅助学习或缓存模拟，不映射真实 `cached_read_tokens`，无 Agent task ID 则不与 Agent 轨迹强行 join。
3. `ROUTER_CHOICE`：只有合法单胜者、真实同题模型质量比较或可信成对反事实才监督模型 choice；静态人类偏好、规则成本决策和真实 Agent 终局分开标 provenance。KV/时序数据不能被强转为路由胜者。

逐源列出原始/去重后/真正训练可用条数、缺失率、Train/Val/Test、监督类型与许可，不需要再制作一轮全项目历史审计。

## 3. 模型训练分段：同源对照 → 新状态 → KV 辅助

- **A0：保留旧 Laya 38 组的协议**。正在运行的 F03/F06 等不停止、不改采样/数据；新 V8 增补数据走另外 Run ID 和 checkpoint 路径。F05 Epoch1 作为物理可用 Laya 多任务候选；F06_S1 的 68.09% 仍为历史较高 Accuracy，不将 F05 67.56% 写成最高。
- **A1：Kev-4B 同源首跑**：官方发布权重续训 `--init_from`，基座及 revisions 匹配；先 F05 同源、同许可、同标签 L1+L2（1,486,215/epoch 候选），Kev 官方 `state/questions/label` 格式，先 1 Epoch；对照 Laya 同固定验证集，区别不归因于单一架构因素。
- **A2：真实轨迹状态增补**：清洗出已观测 Agent 前缀＋执行结果；检查是否**确实进入模型的 state 编码**；用少量稳定独立 Run 比较 `V2.1` vs `V2.1+observed-state`，不要把观察性 resolved 变成所有候选的成功概率。验证改善才继续多轮，考虑温和 S1 权重而非无限堆数据。
- **A3：KV 辅助**：把 Mooncake 真实**前缀重复机会**放入独立 `CACHE_REUSE_OPPORTUNITY` 辅助任务；只有未来同 Episode 实测 provider usage 才启用 `MEASURED_CACHE` 监督。若 KV 特征与 Agent 终局没有正确可连接的实体 ID，不能宣称 KV 增强了 Agent 路由收益。实验至少一组 `without-KV` vs `with-valid-KV-feature` 的同数据受控比较。
- **收敛**：定期读取训练 EMA loss、S1/S2/S3 Val Accuracy/Loss/Brier/ECE、任务组切片和 best epoch；Epoch 末优先；避免把 train loss 下降当验证进步；保存指标最优实体与最新恢复点。若连续两个完整验证点主要指标无实质改善（例如 S1 变化在统计噪声附近），先停止该**新实验分支**的追加 Epoch，保留最好模型，转向 Agent 实测；不擅自改写历史 38 组。
- **并发**：单 A6000 先短跑真实 LoRA+Laya 并发，比较各自和合计 samples/sec、显存峰值、主任务 Chunk 耗时及 OOM。证明资源有收益才双正式训练；若显著抢占，独立 checkpoint、安全 Run 边界交替，不中断正在跑的正式 Laya；不用千问9B高负载第三方抢 GPU。

## 4. 本机工程与 Benchmark / 外部方法两类隔离

**Benchmark（题目+测试器）**，与**外部路由方法（算法实现）**分开存储；同一 Benchmark 允许比较全部路由策略。

| 类别 | 仓库 | 本机目标目录 | 用途 |
|---|---|---|---|
| Benchmark | https://github.com/harbor-framework/terminal-bench-2-1 | `external/benchmarks/terminal-bench-2-1/` | 先验证 `fix-git`、`count-dataset-tokens` 的容器/evaluator；其次 Canary 剩余 6 |
| Benchmark / 动态路由协议 | https://github.com/CommonstackAI/TwinRouterBench | `external/benchmarks/TwinRouterBench/` | 阅读 held-out SWE-bench 实时路由接口，先只跑无需 API 的 mock/static 工具；与训练完全隔离 |
| Benchmark 可选后续 | https://github.com/SWE-bench/SWE-bench | `external/benchmarks/SWE-bench/` | 原生 SWE-bench Verified，后续有实际模型预算再做；不优先克隆整个 Docker 镜像池 |
| 方法参考 1 | https://github.com/lm-sys/RouteLLM | `external/router_methods/RouteLLM/` | 强/弱双模型 query-level routing；确认本项目候选池及输入口径兼容后做真实 baseline，不冒充多模型原生 effort 策略 |
| 方法参考 2 | https://github.com/vllm-project/semantic-router | `external/router_methods/semantic-router/` | KNN 近邻模型选择；可复用现成训练/选择模块；若其本地复杂构建过重，先用 TwinRouterBench 提供的 SR-KNN 适配，保持算法与实际实现来源可追溯 |
| Agent 框架 | https://github.com/harbor-framework/harbor | 现有 `external/` 项目规范下固定版本依赖/源码 | 官方自定义 `BaseAgent` + 容器与评价器；不要重复造评测框架 |
| Agent 循环参考 | https://github.com/SWE-agent/mini-swe-agent | `external/agent_references/mini-swe-agent/`（如有必要） | 仅参考其单 Bash 工具/线性历史的简单循环，不再引入多个 Agent 框架 |

**外部对照首批**：Fixed-strong、Fixed-cheap、Rule/Sticky 作为本项目简单基线 + **RouteLLM 与 SR-KNN 至多两项**外部代码对照。若 RouteLLM 需要与模型池不兼容的权重/强弱 pair，明确列为 `NOT_RUN_INCOMPATIBLE`，不要花整晚做硬兼容；可替换一个仓库内已有且公平的 TwinRouterBench dynamic baseline。Oracle/gold-tier 只作**上界/环境诊断**，不能当普通可实现路由算法。

**最小单 Agent**：Harbor `BaseAgent.run(instruction, environment, context)`，一个执行 Agent + 一个 Router；只需 `bash` 工具（文件操作通过 sandbox shell）；主循环 `observe → snapshot pre-state → legal (model,effort) filter → route → provider generate → parse shell action → env.exec → feedback → repeat`。实现 max_steps/timeout/budget；G0 整任务、G1 固定阶段、G2 可验证子任务先当预设拆分，F 路由边界另记。明早拿到 URL/Key 后才能做真实生成式模型任务，今晚只能 mock/Oracle/Marker/本地 Laya 真实推理。

本机 Laya 选 **F05 Epoch1**（若实际能加载）下载配置、编码器、tokenizer、safetensors 到 `models/agent_pilot/laya/F05-e01/`；记录 sha256、原始 Run、checkpoint_id、加载/推理结果；不要下载无用 optimizer。若本机硬件无法运行不假称成功，保留服务器推理路径。

## 5. 目录、账本、费用和实验隔离

```text
路由/
├── external/
│   ├── benchmarks/              # 官方题目+测试框架版本（非训练）
│   ├── router_methods/           # 外部论文路由实现（非 Benchmark）
│   └── agent_references/         # 仅供读的最简 Agent 参考
├── experiments/agent_pilot/     # 自有 Agent/Router/provider/state/ledger/config，唯一实现
├── models/agent_pilot/laya/     # 本机候选推理权重（不进 git）
├── runs/
│   ├── MR-V8-DATA-EXTENSION-20261018/  # 服务器数据 manifest/派生索引/统计
│   ├── KEV-V8-*/                       # 服务器 Kev 新实验，独立于 Laya
│   └── agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/
│       ├── run_manifest.json          # version、commit、模型池/effort/价格快照
│       ├── decisions.jsonl            # 路由前状态/候选过滤/选择/理由/概率/延迟
│       ├── model_calls.jsonl          # 每次真实输入输出/usage/缓存字段/每次费用
│       ├── tools.jsonl                # 命令、退出码、stdout/stderr、环境信息
│       ├── events.jsonl               # 任务步骤/验证/重试/错误的 append-only 时间线
│       ├── episode.json               # resolved、总费用、时延、分项费用
│       └── official_evaluator/        # Harbor 原始评分产物，不覆盖
└── .runtime/agent_pilot/       # 所有临时缓存、下载中间产物、锁文件
```

- `model_calls.jsonl` 保留每次调用 **input/output** 的引用、哈希与获准留存的脱敏正文，敏感内容不直接公开；记录 `request_id/decision_id/episode_id/provider/model/revision/native_effort/usage_input_tokens/usage_output_tokens/reasoning_tokens/provider_reported_cached_read/write/latency_ms/price_snapshot/cost_usd/rate_unit/currency`；缺失留 `null`，estimated 与 measured 分开。禁止密钥、原文敏感信息与 Benchmark final answer 入 Git。
- `decisions.jsonl` 严格是调用**之前**可见的 `task/subtask/role/phase/tool_history/verifier_so_far/cache_history/budget/legal_candidates/selection/probability/fallback`；候选真实原生 effort 必须来自 Provider 能力表。
- `episode.json` 记录 **全任务**成功/失败、最终 evaluator 及其版本、每一模型调用成本、路由开销、失败重试费用、整体 wall-time；同一调用不可在 retry 与请求费用双计。
- 官方 Benchmark 任务 solution/tests 只能交给 evaluator，运行中 Agent 无权读取解决方案；`Final Test 57` 继续封存，不为调参启用。
- 大文件、密钥、缓存与含敏感 I/O 的 JSONL 不进 Git，`gitignore` 或已有忽略规则只纳入必要路径；只推代码、配置示例、去敏的简洁 `summary.json`、来源版本与运行指引。

## 6. 高并发快速实验，但科学口径不丢

本机并发首先用于**不同独立任务的 Docker 环境**，每个任务/策略/seed 的数据与输出目录完全独立。首轮 `n_concurrent=1` 烟测稳定后逐级 2→4；模型 Provider 的实际 RPM/TPM、预算、Mac CPU/RAM/Docker 限制优先。**不要并发执行同一环境中的多策略**，也不共享可变模型对话历史；固定任务、seed、相同生成模型池、Evaluator、预算和价格快照。

阶段里程碑：
1. 服务器核实增量数据与合法准入；A6000 Laya 不受影响、Kev 真实小段训练并尝试安全双跑；不重复下载已有数百 GB 文件。
2. 本机拉 Harbor/Terminal-Bench、至少一个官方任务容器 Oracle 烟测、Marker/Mock 单 Agent 工具循环、一个真实 Laya choice 推理。
3. 本机拉 RouteLLM/SR-KNN 并完成 import/adapter 与无需 API 的离线接口测试；不能把 mock 算作真实外部方法效果。
4. 训练至 Epoch 1/中段节点报告验证和硬件；仅在验证收益与资源允许时继续 2~3 Epoch；保留每阶段 best checkpoint。
5. 明早 API URL/Key 与额度到位后，选定 Canary 中 1–2 题做 Fixed vs Laya + 外部可跑 Router 的**真实** Agent rollout；扩展开发集和跨模型池后再做 RQ1–RQ3，最终 57 题只在冻结策略后一次性评测。

**停止条件**：主训练正在受损、OOM、数据许可/样本身份不清、训练与 Test 混用、模型候选原生 effort 不合法、未授权 API 费用；只停止对应新增支线，保留已有主线。工作日志不能宣布没有测量过的“真实缓存节省”“收敛已证实”或“成功率提升”。
