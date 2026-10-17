# ModelRouter · V8 数据增补、Laya/Kev 双训练与 Agent Benchmark 长周期执行方案

> 日期：2026-10-18；阶段：**执行研究计划与数据源复核**，不是“已下载/已训练/已运行 Agent”的证据。本文件不重写 [V8 论文实验方案](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)，也不取代 [数据与许可唯一台账](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。已完成的 F05 / F03 进度以服务器最新 `run.json/cursor.json/queue_state.json` 为准。已确认用户授权在自有 A6000 上开展 Laya、Kev 的新训练以及本机 Benchmark 工程准备；**新付费 API 调用仍需等 URL/Key、明确额度后启用**。

## 0. 现在执行的两条工作线

- **服务器：数据→清洗→可用标签入库→逐阶段训练→收敛观察。** 保留既有 V2.1 正式 Laya 38 组原协议，新的数据/损失/KV 联合实验另外编号、另外输出。Kev-4B 优先按同源 V2.1 F05 L1+L2 进行第一阶段跨基模对照，再以合法补充数据做独立训练分支。单 A6000 试测双训练并发的**合计吞吐/显存/功耗/主任务延迟**，收益和安全共同决定长期策略。
- **本机 Mac：Benchmark 源码、外部路由方法源码、最简单单 Agent、服务器 Laya/Kev Router API 客户端、真实输入输出及费用账本与双模型简化看板。** **不下载 Laya/Kev 权重到本机，不在 Mac 本地加载路由模型。** 今晚无新增付费 API，Oracle/Marker/Mock 只算环境或接口烟测，不算 Agent 成功。

**2026-10-18 03:45 CST 最新组织授权：主 Execution Agent + 恰好 2 名子代理（覆盖旧“仅 1 名子代理”限制）。** 主 Agent 独占 A6000 数据、Laya/Kev 训练、模型 Serving 调度和统一 Git 合并/推送；子代理 A 负责 Mac 本机 Benchmark 官方源码与官方 Harbor Agent 环境、真实 1–2 题、三协议生成 Provider 及限额并发；子代理 B 负责外部论文路由方法复现、Mock/真实结果区分、受保护实验账本和双模型精简看板。两子代理不得再次派生子代理，也不得并发修改同一文件/训练控制器。

## 0.1 本轮新增负责人强制要求：每阶段重新同步最新 GitHub（2026-10-18）

**远端 GitHub `main` 上的最新 V8 文档是执行要求的唯一持续更新入口。不能只在任务开始时读一次，也不能把最初收到的长提示词永久当作不变命令。** 本轮负责人特别要求“每完成一部分就重新读、及时更新 Git、规范整理目录”。具体闭环如下：

1. **开始每个阶段前**（至少是数据盘点与下载、清洗、Kev 同源训练、增补 Agent 状态、KV 训练、首次验证/收敛节点、本机环境、Agent 接口、外部方法、Benchmark smoke、运行结果归档这些边界），在本机及服务器各自已有工作树查看 `git status` / `git rev-parse HEAD`；保护未提交改动后执行 `git fetch origin main`，在可安全快进时 `git pull --ff-only origin main`。不能强制 reset/覆盖别人或本轮子代理正在写的文件。
2. **每次拉取后重新阅读**本文件、`our-project/planning/PROJECT_STATUS.md`、`our-project/planning/RESEARCH_OVERVIEW.md`、`our-project/planning/EXPERIMENT_QA.md`、`our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md` 和 `汇报/汇报三/ModelRouter论文实验与图表规划.md` 的最新相关段落，尤其是任何新授权、否决、更改范围、Benchmark/Test 隔离、训练数据与模型池限定；记下读取到的 Git SHA。若负责人新要求与正在执行的非安全性工作冲突，安全停止**对应新阶段**并按新决定调整，避免重跑已完成健康训练；不触碰其他正常运行的 GPU 子进程。
3. **每完成一个可验证阶段**就更新原有对应文档：实际当前进度/下一步到 `PROJECT_STATUS.md`；数据源许可/清洗/字段事实到唯一数据台账；已确认决定到 `EXPERIMENT_QA.md`；只有科学方法发生实质变化时才改 `RESEARCH_OVERVIEW.md`；本文件只记执行计划/阶段协议及必要修订。记录已完成、未完成、实测命令/样本/输出路径/版本、当前阻塞和资源占用，不把计划当成结果。
4. **阶段完成马上 Git 提交并推送**可公开的源码、配置、Markdown、脱敏统计和简洁结果清单：`git status`→针对性 `git add <明确路径>`→`git diff --cached`→`git commit -m '<阶段成果>'`→`git push origin main`→再次核对远端 SHA。阶段无实际改变时不制造空提交；若网络失败保留本地 commit，真实汇报 `PUSH_PENDING`，待网络恢复再同步。不要把训练未完成/测试未运行说成完成；主 Agent 是**唯一统一提交负责人**，子代理产物交由主 Agent 审阅并合并，不各自竞争推送 `main`。
5. **每个阶段收尾都整理目录**：服务器仅用已存在的 `data/公开数据`、`runs/`、`.tmp/` 归类数据、模型与阶段临时文件；本机区分 `external/benchmarks`（题目/评分器）、`external/router_methods`（外部论文方法）、`experiments/agent_pilot`（自有代码）、`experiments/agent_pilot/configs`（仅端点配置，不存模型实体）、`runs/agent_pilot`（实验结果/日志）、`.runtime/agent_pilot`（临时物）。禁止根目录散落 `test.py`/`tmp*.json`/下载模型、遍地 `nohup.out` 或随机脚本；运行失败临时证据先归档再清理，不能删历史数据/有效 checkpoint。
6. **Git 和隐私边界**：密钥、Token、原始大数据、模型权重、完整可能敏感的 prompt/completion、Benchmark 封存答案、Docker 镜像与大批完整日志不进入 Git；仅提交脱敏 `summary.json`、manifest、路径索引、版本哈希、调用字段 Schema 和必要可复现代码。真实每次输入/输出、工具 stdout/stderr、usage、价格快照、缓存计量和完整 evaluator 结果必须持久化在**受保护的本地/服务器运行结果目录**，并在索引中注明路径/权限。不要为追求及时提交直接 `git add -A`。
7. **单一主线、长周期运行**：服务器训练继续无人值守，本地子代理可同时准备 Agent；每到自然阶段边界自动执行上述刷新/提交/继续，无需等待负责人逐段确认；仅未授权的付费 API、禁训数据、Test 解封等仍不可擅自执行。不要把本机 Benchmark 与服务器训练强制串行，也不要用新 Watcher/第二正式队列破坏已有连续控制器。

**操作顺序约定**：`刷新仓库与重读最新要求 → 执行本阶段 → 实测/落盘/分类归档 → 更新唯一权威文档 → 定向 commit/push → 记录 SHA → 再次拉取并重读最新要求 → 下一阶段`。

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

**服务器选择并固定 Laya F05 Epoch1 或经核验的更优物理候选作为推理版本**，Kev 使用经固定验证且可加载的相应候选。模型权重、Tokenizer、优化器和 Checkpoint 只存服务器；服务端提供带 `checkpoint_id/revision` 的只读 `health/models/route` API，本机用受控 SSH 隧道访问，记录真实请求/响应及耗时；不得下载路由模型权重到 Mac。若服务器由于 GPU 资源紧张无法保持推理服务常驻，要记录 `SERVING_WAITING_FOR_GPU` 并采用单独推理窗口，不得假装本机已完成真实 Router 推理。

## 5. 目录、账本、费用和实验隔离

```text
路由/
├── external/
│   ├── benchmarks/              # 官方题目+测试框架版本（非训练）
│   ├── router_methods/           # 外部论文路由实现（非 Benchmark）
│   └── agent_references/         # 仅供读的最简 Agent 参考
├── experiments/agent_pilot/     # 自有 Agent/Router/provider/state/ledger/config，唯一实现
├── experiments/agent_pilot/configs/  # Router API 端点与示例配置，无权重
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
2. 本机拉 Harbor/Terminal-Bench、至少一个官方任务容器 Oracle 烟测、Marker/Mock 单 Agent 工具循环；通过服务器 Router API 发起一次真实 Laya Choice 推理，真实服务不可用则记录 WAITING，不以 Mock 替代。
3. 本机拉 RouteLLM/SR-KNN 并完成 import/adapter 与无需 API 的离线接口测试；不能把 mock 算作真实外部方法效果。
4. 训练至 Epoch 1/中段节点报告验证和硬件；仅在验证收益与资源允许时继续 2~3 Epoch；保留每阶段 best checkpoint。
5. 明早 API URL/Key 与额度到位后，选定 Canary 中 1–2 题做 Fixed vs Laya + 外部可跑 Router 的**真实** Agent rollout；扩展开发集和跨模型池后再做 RQ1–RQ3，最终 57 题只在冻结策略后一次性评测。

**停止条件**：主训练正在受损、OOM、数据许可/样本身份不清、训练与 Test 混用、模型候选原生 effort 不合法、未授权 API 费用；只停止对应新增支线，保留已有主线。工作日志不能宣布没有测量过的“真实缓存节省”“收敛已证实”或“成功率提升”。


## 7. 2026-10-18 最新负责人调整：**服务器 API 推理 + 本机 Agent 高并发 + 极简双模型实时看板**

> **本节优先于本文前面任何与它冲突的旧文字。** 最明确的改动：**禁止把 Laya/Kev 最优模型权重下发 Mac。** Laya 与 Kev 都在 A6000 上训练、保留实体、推理并暴露受控 API；本机仅存 API 客户端、Benchmark 任务/基线代码及真实结果。仅允许主 Execution Agent + 一名子代理。今晚独立完成基础框架，无付费生成模型调用；明早负责人给 Provider URL/Key 和费用上限之后再运行正式任务。须在安全 Run 边界/已空闲资源中安排 Serving，不强杀健康训练。

### 7.1 数据面与控制面严格分离

- **控制面（主 Agent）**：唯一写入服务器训练队列、Kev 分支、服务启动/暂停和模型版本切换；服务器根目录使用现有 `/home/syy/路由` 或现场真实根目录。新增 `experiments/router_serving/` 存服务源码和加载适配器；`runs/router_serving/` 存仅服务器的请求/服务日志；`models/` 或现有 Run checkpoint 实体**留服务器**。新增 API 服务不是新训练控制器，不得创建第二条 Laya 正式队列。
- **数据面**：Mac `experiments/agent_pilot/` 是单 Agent 和 Benchmark 客户端；只按受控 URL 与服务器路由选择 API 通信；后续另接外部生成式 Provider API。这两个 API **角色不同**：`Router API` 只返回合法 `(model,native_effort)` 的决策或概率；`Generator API` 接收上下文并生成执行动作/代码。不能把 Laya/Kev 当作 Terminal-Bench 执行生成模型。
- **网络**：服务端默认监听 `127.0.0.1`、不在公网暴露；Mac 通过既有 `ssh a6000` 的受限本地端口转发访问。使用实际可用的隧道端口，检测冲突后再选；仅对授权终端开放。模型服务应鉴别可用角色或本地隧道来源，超时/断连要可诊断；API key 只能由环境变量/私有配置提供，不写仓库与前端。
- **路由服务版本**：每次加载记录 `router_family`（laya/kev）、`run_id`、`checkpoint_id`、`epoch`、`dataset_protocol`、`source_revision`、`loadable`、`loaded_at`，**原子地将当前请求绑定不可变 checkpoint**；新模型上线先检查能加载和输入 schema，不能切换到尚未验证或已被修剪的权重。
- **最小端点契约**：`GET /health`（服务自身、GPU/CPU 负载/版本、错误状态）；`GET /models`（两个 router 的已发布版本和可用性）；`POST /route`（详见下）；可选 `GET /metrics` 只暴露不含敏感数据的计数。服务器可共享单个轻量 FastAPI 服务进程/两个隔离加载器，也可各独立端口，**以实际模型库的加载能力及显存为准**，不要为了“统一接口”重复占用显存。
- **`POST /route` 请求**：`request_id,episode_id,decision_id,policy_version,router_family,pre_decision_state,legal_actions:[{provider,model,revision,native_effort}],budget_remaining,features_presence_mask`。响应：`request_id,router_family,checkpoint_id,selected_action,ranked_actions_or_scores_if_available,decision_latency_ms,fallback_used,fallback_reason,confidence_if_defined`。服务端验证所选动作属于请求的 `legal_actions`；非法/不支持的 Effort 不得隐式映射为别的等级。请求、响应需版本化 JSON schema 并配最小真实可重复样例；错误码包括 `NO_MODEL_LOADED`、`INCOMPATIBLE_STATE`、`NO_LEGAL_ACTION`、`RESOURCE_BUSY`、`ROUTER_TIMEOUT`。
- **概率与分数边界**：已有 S1/S2/S3 并不自动是任意多模型树的 Choice 输出。先在固定合法 action 集上实测 Laya/Kev 是否支持该请求；模型语义不足时明确 `NOT_SUPPORTED` 或有限可解释映射，并使用可追踪 Rule/Fixed fallback，**不可伪造“全空间最优路由”**。

### 7.2 单卡三类负载隔离与双模型并发训练

- 服务器保留 Laya 正式连续训练和 Kev 独立 LoRA 训练；后者首发必须为同源 V2.1 L1+L2 可核对数据。每一实验有独立 `run_id/cursor/optim_state/metrics`，不改变正在运行的 Laya 38 组协议。
- 单张 A6000 的训练高利用率不是低负载；双训练先短时对照：分别计 `Laya updates/s, Kev updates/s, each samples/s, weighted useful throughput, end-to-end walltime, GPU memory peak, power, temperature, OOM/retries, primary chunk slowdown`。不同参数模型的样本/秒不能直接无权相加当“总收益”，以完成实际目标所需 GPU 墙钟与主线减速为主。
- 如果持续双训练使主线严重变慢、显存有风险或完成时间不改善，**并行保留 CPU 数据准备、独立 CUDA 训练按安全 Run/Checkpoint 边界交替**。不因负责人要求“双模型都训练”就强制保持两个满负载 GPU 进程。
- Serving 与训练会竞争同一张 GPU：先实测小批量路由推理服务的 P50/P95、显存和训练吞吐影响；Serving 只在余量允许时常驻，或在本机真正要测试时安排限定推理窗口；服务繁忙返回可观测状态并重试/排队，**绝不抢杀训练或暗中复制大权重到 Mac**。
- 停止新分支追加 Epoch 的条件是预先记录的预算、固定 Val 多个节点的改善与统计噪声比较，而非 train loss 连续下降/单个 Accuracy 阈值；保存 `best` 和 `latest_resume` 两类物理有效引用及来源。

### 7.3 最简可扩展单 Agent（本机）

- 复用固定版本 [Harbor](https://github.com/harbor-framework/harbor) `BaseAgent` 外部 Agent 接口作为 Runner；任务/容器/evaluator 交给 Harbor，参考官方 `examples/agents/marker_agent.py` 的最小调用方式；如需执行循环结构仅借鉴 `mini-swe-agent`，**不引入 LangGraph、多 Agent orchestration、长期状态数据库或第二套独立 Bench 框架**。
- 唯一 Agent Loop：`load task → init sandbox → observe(task + tool history + budget) → derive G and legal F boundary → build immutable pre_decision snapshot → list legal (model,native_effort) pairs → policy.route(Fixed/Rule/RouteLLM/SR-KNN/Laya/Kev) → call Generator API → parse single shell action → environment.exec in sandbox → append trace/usage/feedback → repeat → Harbor official evaluator`。终止条件：`agent_done`、`max_steps`、`time_budget`、`usd_budget`、`tool_error_budget`、`provider_unavailable`。模型输出不是真实 shell 命令时严守协议/合理重试，失败照实保留。
- **拆分与路由频率分开**：`G0` 原任务整体、`G1` 可复现固定阶段（inspect/modify/verify）、`G2` 官方可验证子任务；`F0` 每完整任务一次、`F1` 阶段边界、`F2` 合法模型调用前等。今晚只实现单 Agent，G2 若任务无可信可验证子任务则为 `NOT_APPLICABLE`，不能伪造。RQ3 主试运行的单 Agent 结论不能代替 V8 后续多 Agent 工作负载。
- **工具**：初期只有 Harbor 隔离 Shell；读写文件、git、测试、查看错误均通过相同 sandbox shell 实现，明示工作目录、超时、输出截断标记、exit code、重试是否新调用；绝不直接在 Mac 宿主执行不可信任务脚本。Verifier 独立于 Agent，不泄露标准解和隐藏 Test 到模型上下文。
- **策略适配器统一协议**：`FixedStrong`、`FixedCheap`、`RuleSticky`、`RouteLLM`（实际兼容性验证）、`SRKNN`（以真实出处/版本为准）、`LayaServerRouter`、`KevServerRouter` 都只实现 `select(state,legal_actions)->decision`。失败 fallback 必须显式记录所用固定策略、原因与成本；不得把 fallback 计成成功的动态路由。
- **Provider Registry**：每个可执行生成式模型记录 `provider/model/revision/context/max_output/tool_support/native_efforts/rpm/tpm/price_units/price_snapshot/availability`；**K=模型身份数**，合法动作数量为各模型合法 native effort 的总和。不可凭路由建议强行对供应商发送不支持的 effort；输出 Token 和原生 reasoning Token 分开记录。
- **Benchmark 两类与方法两类**：`external/benchmarks/` 下单独固定 Terminal-Bench 2.1（89题、项目已冻结 8 Canary/24 Dev/57 Sealed）和 TwinRouterBench；`external/router_methods/` 下 RouteLLM / SR-KNN。先 `fix-git` 与 `count-dataset-tokens` Canary 单任务官方容器/Oracle 环境烟测；再只对 1–2 题做 Mock 适配；待明早授权 API 才能跑生成式模型成功率。别人的论文发表分数不能与我们不同评测协议的 Agent 成绩直接并表。
- **实验配对原则**：同一个 `task_id` 在不同 policy 下独立 sandbox、相同基础任务版本、可核对 evaluator、相同预算/时间上限和生成模型候选池；预先固定任务/策略/seed 的组合，记录未执行/失败/超时；Policy 不得共享可变上下文状态或其他策略未来输出。

### 7.4 高并发实验执行协议（并发任务 ≠ 同一任务并行 Agent）

- 本机仅用一个 `ExperimentRunner` 调度独立的 `(benchmark_revision,task_id,policy_id,seed)` **Episode**，每个 Episode 始终是**单 Agent 串行多步**；不同 Episode 可并发。不要把一个 Agent 的工具历史拆到多个异步 Worker；不引入额外子代理。
- `asyncio` 任务调度 + bounded queue + 两层令牌/信号量：`max_active_episodes` 管 Docker/Mac CPU/RAM；`router_api_limit` 管 A6000 服务吞吐；按 Provider/模型分别使用 `rpm/tpm/max_inflight` 令牌桶和预算闸门；另控 `max_active_builds` 防止本机 Docker 镜像并发编译 OOM。生成式 API 的并行调用遵守供应商实际限额，不自作设定无限 concurrency。
- **渐进并发**：`concurrency=1` 完成真实可回放烟测，提升到 2、4、再视 CPU/RAM、Docker 和 API 响应决定是否 8；每级记录 `throughput tasks/hour, mean/p95 wall_time, error_rate, queue_wait, rate_limit_429, timeouts, actual cost, completed/evaluated count`。阈值按实际资源预算/测量确定，不在方案中许诺固定倍数加速。若 429/5xx/OOM/价格异常增长则自动降低新增任务并发（不抹去失败）。
- 同一请求 `request_id` 贯穿 Router→Generator→Tool；Provider 的重试保留 **每一次实际收费尝试**，指数退避+抖动且有限次数；对不确定是否已执行的调用不得无账单重复计费，记录是否可确认。输入输出要绑定 checkpoint/revision、模型价格版本和 Agent 代码 Git SHA。
- 每个 Episode 独立不可覆盖运行目录，`task:policy:seed` 唯一键经安全文件名编码；进程重启扫描 `run_manifest.json` 与 `episode.json`，完成的跳过、未完成的只在容器/远端费用状态可核时安全续跑，不能将部分完成任务算成功。随机种子只能控制可控随机源，不能保证非确定性 API 完全复现。
- 首次阶段不进行大规模 Benchmark 全量调用；先完成 1–2 个任务的环境/接口证据，获得预算授权后用 8 Canary → 24 Dev → 独立冻结策略的 57 Final。真实正式测试次数、重复 seeds 和总费用需按实际授权额度约束，Final 在策略未冻结前不得触碰。

### 7.5 受保护运行账本与分析口径

受保护本机目录 `runs/agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/`，每个任务至少落：
`run_manifest.json`（版本/模型池/费用表 SHA/Env/evaluator/seed）、`decisions.jsonl`（决策前 snapshot、合法池/选项、Laya 或 Kev 的 checkpoint/延迟/fallback）、`model_calls.jsonl`（每个生成模型**实际输入与输出引用**、请求响应时间、真实 usage 和费用）、`router_calls.jsonl`（远程 Laya/Kev 请求响应、版本与延迟）、`tools.jsonl`（沙盒命令/退出码/stdout/stderr 引用）、`events.jsonl`（append-only 步骤、限流、重试、失败）、`episode.json`（Harbor resolved/timeout、全部调用总价、成功与否、时延）、`official_evaluator/`（官方评分原样记录），`inputs/`、`outputs/` 下按 `request_id` 保存权限受限的原始/脱敏内容。按来源许可和个人信息政策，可能敏感数据只存 hash+安全引用，不出现在 Git。
- 单次 USD 使用**当次 Provider 真实 token usage × 当时生效版本化价格单位**；未上报缓存/推理 token 留 null，`MEASURED / ESTIMATED / UNKNOWN` 严格分层；若 Provider 返回实际账单优先于估算。输入、输出、reasoning、缓存 read/write、工具、Router 服务计算 GPU-hours 分项，失败重试照单入账、不重复相加。路由服务自有 GPU-hours 与生成式 API USD **不同单位分开报告**。
- `summary.json` 从原始事件账本生成，拒绝手工覆盖：任务级 Success、Mean Episode USD、Cost/Resolved（零成功定义为不可计算）、P50/P95 延迟、Router fallback_rate、真实完成分母、分组/种子、缺失费用占比；跑 RQ1 时同任务配对比较并按任务自举置信区间；只对 Dev 做选择，Final 不用于训练/选阈值。Mock/Oracle/Marker 分别记 `ENV_SMOKE` / `ADAPTER_SMOKE`，不得进入真实成功率统计。

### 7.6 大幅简化原有实时可视化，并在本机独立终端运行

**复用已有** `docs/training-dashboard/` 和 `scripts/fetch_live_status.py`，不新开第三套大盘。现有 `index.html` 超过 6,000 行且 `live_status.json` 超过 500 KB，包含大量历史树、占位以及 F04 硬编码；本轮把主页实质重做成简洁 2 模型 + 开发进度图。原始历史 Epoch/Checkpoint 继续保存磁盘，可放独立静态归档链接（需要时看），不在首页加载庞大 JS shards。

**首页只允许四个区域：**
1. 顶部一排：最近成功刷新时间、Fresh/Stale/Disconnected 及刷新滞后秒数、服务器 GPU 利用率/显存/训练优先状态、本地 Agent/Benchmark 启动状态；
2. **Laya 左列**：在训/完成/等待/Serving 就绪、当前 Run/Epoch/Chunk/Step、训练 Loss（标当前 chunk）、Best Epoch+S1/S2/S3 固定 Val、最佳 checkpoint 是否实体可加载、Router API 健康与最近 P95 延迟；
3. **Kev 右列**：相同字段，但没有结果时显示 `NOT_STARTED / NO_DATA / NOT_EVALUATED`，**绝不能拿 Laya 值填 Kev**；
4. 底部开发进度：数据盘点→新源清洗→Kev 同源训练→KV 独立分支→两路 Serving→Harbor Ready→单 Agent Smoke→外部基线→有授权的真实 Canary；每段 `planned/running/completed/blocked`、最近 Git SHA 和阶段输出路径；紧凑最近 8 条真实事件。选择性显示最近一次 Benchmark 已跑任务数、真实成功数、已知费用合计及 Mock/Oracle 分开计数。

**源数据实现**：`scripts/fetch_live_status.py` 读服务器 Laya 当前 `run.json/cursor.json/epoch_metrics.json`、Kev 对应独立 `run.json`、GPU 和 Serving `/health`；本机侧读 `runs/agent_pilot/` 的 `summary` 与阶段 `development_status.json`（这是事实记录，由阶段任务写入，不是编辑一个字符串就算完成），输出两个有版本号的瘦身 JSON：`docs/training-dashboard/live_status.json`（服务器双模型及指标）和 `docs/training-dashboard/development_status.json`（本机开发进度/Agent 统计）。采集时间、源更新时间、字段来源分别保留；读取失败不沿用旧数字装“在线”，显示 STALE+原时间；无有效 Epoch 验证则显示 N/A。避免每 10 秒全量遍历巨型日志、重写 580KB JSON 或把本地实时数据每次都 push GitHub。
- **必须修正**旧同步脚本的 F04 静态 fallback 与 `if r == "F03" and int(s_tot)==45836 → LEGACY` 错误：正规 F03 恰有 45836 steps。按 `run.json/protocol_version/run_id` 判别，不按 step 数猜测 Legacy。确认指标引用来自真实 `epoch_metrics.json` 而非 Chunk Loss / 最后 Epoch 冒充 Best；处理每个训练任务可能没有 Cursor 的情况。
- **启动要求**：本地 Mac 用单独终端窗口继续服务旧地址 `http://127.0.0.1:8765`。先检查 `lsof -i :8765` 和现有 `http.server`、`fetch_live_status.py` 同步进程；若已运行且健康则沿用，需替换时优雅停旧服务后单例启动。不占用主 Agent 的终端，也不产生重复 HTTP/同步服务。HTTP 可采用 `python3 -m http.server 8765 --bind 127.0.0.1 --directory docs/training-dashboard`，同步器用现有受控运行方式，进程日志单独放 `.runtime/dashboard/`。如果本机 GUI 终端无法自动打开，输出可复制的确切命令并如实报告未打开，不能声称成功。
- **前端原则**：仅静态 HTML/CSS/vanilla JS（已够用）；读 `live_status.json`、`development_status.json`，每 5–10 秒轻量刷新；无前端 token、SSH key、绝对私有路径、原始用户 prompt 或费用明细。手机版/电脑简洁两栏布局，实时更新不重绘整个页面；仅保留必要 2–3 条趋势，页面文件大幅压缩，删除静态历史数据对首页的耦合。刷新器不影响 GPU 训练。

### 7.7 目录与阶段提交纪律（主 Agent + 两名子代理，以 §8 最新指令为准）

```text
路由/
├── data/公开数据/                    # 复用服务器已有原始和清洗分级布局
├── router_data/                      # 已有正式 Laya 数据与训练实现，不混新实验
├── experiments/
│   ├── router_serving/              # 服务端只读路由 API + 模型加载/服务压测
│   └── agent_pilot/                 # Mac: agent.py/router_clients.py/registry.py/runner.py/ledger.py/configs/
├── external/
│   ├── benchmarks/                  # Terminal-Bench 2.1, TwinRouterBench, 可选 SWE-bench
│   ├── router_methods/              # RouteLLM, SR-KNN
│   └── agent_references/            # 官方 Harbor 或 mini-swe-agent 源参考
├── docs/training-dashboard/         # 原地址首页，双模型+开发进度瘦身 JSON
├── scripts/                          # 原 fetch_live_status 与运行所需唯一脚本入口
├── runs/
│   ├── MR-.../                       # 原 Laya 正式 Run，不触碰
│   ├── KEV-V8-.../                   # 服务器 Kev 独立训练
│   ├── MR-V8-DATA-EXTENSION-.../     # 服务器新增数据导出/manifest
│   ├── router_serving/              # 服务器服务请求/错误/模型加载与日志
│   └── agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/
└── .runtime/
    ├── agent_pilot/                  # 沙盒下载缓存/临时任务
    └── dashboard/                    # 本机采集与 http 服务日志
```

不同机器不要求存一模一样的实体：**服务器存 Laya/Kev 权重，本机绝不存这两种权重**；本机仅保留端点配置和模型版本 ID。原始模型请求和完整日志保存在有访问权限控制的运行目录；Git 仅上传代码、Schema、必要摘要、脱敏结果和 Git SHA。每完成一个自然阶段，按 §0.1 的 `fetch latest → read six docs → run → real verify → organize directories → update status → targeted commit/push → verify remote SHA → re-read` 闭环推进。不得使用 `git add -A` 把大文件混进公开仓库，也不制造空提交。

### 7.8 长周期任务的分阶段验收（不能因无 Key 停掉 CPU 工作）

| 阶段 | 负责人 | 最小可核结果（未通过写 BLOCKED） |
|---|---|---|
| S0 最新仓库、服务器/本机资产盘点 | 主 | 源版本、活跃训练/模型实体、磁盘/GPU、既有目录路径与下一个阶段 |
| S1 合法数据补缺/清洗/映射 | 主 | lineage+Train/Val/Test+标签证据与真实已接纳样本数 |
| S2 Kev 同源真实梯度+双训练吞吐 | 主 | Kev 优化器步数>0，完整恢复验证、GPU 性能 A/B 与正式 Laya 不受损 |
| S3 服务器 Laya/Kev `/health/models/route` | 主 | 两个 Router 对**实际可加载**的权重做真实合法 Choice API 测试，若 GPU 紧张明确状态 |
| S4 Harbor / Terminal-Bench 本机 | 子 | 隔离 Docker+官方 1 题 evaluator/Oracle 真实环境烟测 |
| S5 单 Agent + Registry + Router API client | 子 | Mock 工具循环和在服务可用时真实 Laya/Kev 远程路由请求，账本可复现 |
| S6 RouteLLM / SR-KNN 方法与独立 Benchmark | 子 | 实际可 import、同一动作格式和兼容性/不可用原因记录，不伪造效果 |
| S7 极简双模型看板在独立终端运行 | 子 | 浏览器在 8765 可打开；两个训练/Serving 各自显示真实状态，开发阶段刷新且 STALE 正确 |
| S8 受保护 I/O/费用汇总及并发烟测 | 子 | 1→2→4 episode 并发与限流记录、每请求/Tool/Router 调用追踪、Mock 标识 |
| S9 明早正式 Agent Run（待 API 授权） | 主+子 | 有效 URL/Key、价格与额度授权后，1–2 Canary Fixed/Rule/Laya/Kev 按公平配对执行、官方 evaluator + 真实 USD；授权前明确 WAITING_FOR_GENERATOR_API |

S0–S8 可交织执行但**主 Agent 只管理两名明确分工的子代理**，服务器唯一控制器不变。每段结束提交真实结果并拉最新指令；不能因 S9 缺明早 API 就让 S1–S8 不执行。**实现条件达不到时如实停止对应新增分支，训练正常则继续。**


## 8. 2026-10-18 03:45 CST 最新负责人补充：真正可运行的 1–2 题、三协议、双模型 ≥12 版本研究和双子代理

> **最新优先级最高。** 本节覆盖本文件旧版“仅 1 子代理”“仍等待明早 Generator URL/Key”“把 Kev/竞品/Mock 写作已跑通”等已过时要求。具体真实 CC Switch 凭据访问与费用使用只通过 Mac 本机安全配置，不许显示/提交密钥。**本节是授权执行计划，不意味着任何真实付费测试已完成**。

### 8.1 最新 GitHub b80574d 实际源码复核：当前证据级别

| 声称完成 | 源码真实现状 | 必须补的实测 |
|---|---|---|
| Laya Serving | `experiments/router_serving/laya_adapter.py` 确实加载 Laya 物理权重并调用 `RLAgent.system_one` | 固定 checkpoint，记录两次真实线上 route，验证选择合法、非静态/回退；需要检查任意选项集与训练选项空间兼容性 |
| Kev Serving | `kev_adapter.py` 只检查 `Checkpoint(...).meta`，`is_loaded=True`，但 `route()` 是人工规则/伪造 8.5ms，`self.model` 从未加载 | **必须真正加载 Kev base+adapter+pointer head 并真实前向；未就绪时 `MODEL_NOT_LOADED/HEURISTIC_ONLY`，不得声称 Kev Model Inference** |
| Kev 训练 | `router_data/run_kev_homologous_train.py` 默认 CPU 5 optimizer steps，报告仅 2 步；默认 `data/kev/公开数据/train.jsonl`，尚无证据与 V2.1 F05 一一对齐；head 目前新初始化且未参与 logits | 真正同源 V2.1 对齐清单、可加载可恢复正式 Kev Run、验证指标、至少多候选 Epoch/策略研究 |
| 64 并发“75% Pass@1” | `run_stress_benchmark.py` 显式使用 `MockGeneratorProvider`；`runner.py` 无条件 `MockSandboxEnvironment()`，并非 Docker 官方 evaluator；Mock 自带脚本、模拟 tokens/USD | 清楚标 `MOCK_STRESS_ONLY`，不得算真实 Pass@1、真实 USD、真实 task/hour；新增真正 Harbor Docker Episode Runner |
| RouteLLM/SR-KNN | 当前 `policy.py` 的 RouteLLM/SR-KNN 是手写阈值/规则；`baselines/routellm_adapter.py` 仍是关键词规则，`sr_knn_adapter.py` 示例为人工 exemplars；Git 树没有 `external/router_methods/` 官方源码 | 下载并固定论文/源码/权重或训练数据；接入**真实公开算法**，支持少量真实任务的 route 决策，不可沿用同名伪复现 |
| Benchmark | `experiments/harbor/task_loader.py` 和 `canary_verifier.py` 的 Schema/Mock 不等于官网任务真实容器与官方 grader 已跑；Git 树不存在完整 `external/benchmarks/` 第三方源码 | 固定 SHA 克隆全部**选定 Benchmark** 源码，单独官方容器/Evaluator/Agent 证据，1–2 真题 |
| Provider | `provider.py` 只有 `/chat/completions` 实际请求，缺 `/responses` 与 `/v1/messages`、模型目录真实性与精确 usage 差异处理 | 同一 `GeneratorResponse` 下实现并真实 smoke 三种协议与模型 GPT-6、Luna |

`docs/training-dashboard/development_status.json` 中 `S4/S6/S8 completed` 必须加 `evidence_level`，**改成“MOCK/ADAPTER_SMOKE 完成，OFFICIAL_REAL 不满足”**，并将模拟 75% 与 22,248 tasks/h 从论文真实指标区删除/分区。Kev /health 的 `loaded` 不得以仅加载元数据充当真实可推理状态；`GET /models` 不显示假静态分数。安全检查已有服务监听：默认应 `127.0.0.1` 并通过 SSH 隧道，不保留 `0.0.0.0` 裸服务与开放 CORS。

### 8.2 最新执行人员组织与 Git 重读

- **主 Agent**：唯一拥有 A6000 的 SSH 写权限及 GPU 训练/Checkpoint/Serving 写权限，负责清洗数据版本、12+ 训练候选规划与续跑、源数据合法准入、Serve 真正的 Kev 推理、GPU 资源管理、唯一 Push/提交。
- **子代理 A**：Mac `external/benchmarks` 官方下载锁版、Harbor 官方 Docker 与 Official Verifier、单 Agent 真 Agent Loop、CC Switch 只读接入、OpenAI Responses/Chat Completions/Anthropic Messages、模型可用性检查、真正 1–2 task 烟测和全局 <1m Tokens 闸门。
- **子代理 B**：Mac `external/router_methods` 官方论文/源码、RouteLLM/SR-KNN 真实可跑或清楚不可用，固定/Rule/随机基线、`docs/training-dashboard` 双模型看板以及 append-only 账本/价格。
- 主 Agent 对子代理的文件区域做单一 ownership，不许互相覆盖；2 个子代理均不得再创建下级代理。自然阶段结束后全部停止写同一文件，由主 Agent 定向复核/合并/Push、确认远端 SHA、所有人员 `git fetch origin main` 再重读 §8 + 六份已有权威文档，进入下一阶段。不得丢失子代理未提交工作，不为迁就 Git 同步中断健康 GPU 进程。
- **GOAL 长周期命令**：用户要求开启 `GOAL`。先检查当前 Execution Agent 实际已安装的 GOAL 命令、语法与权限；若存在，按当前正式 Goal/Long-running Job 接口启动持续任务，报告真实命令、目标和日志路径；**若不存在不可捏造已执行**，使用现有可持续工作的任务/终端机制实现，并记录 `GOAL_COMMAND_NOT_AVAILABLE`。不得将聊天命令文本或启动前条件错写成已启动。

### 8.3 两套 Router：不是“训练两步”就结束

- 对 Laya 和 Kev **各规划至少 12 个不同的、可复现且有结果的候选版本/阶段验证点**；`candidate_id` 包含 base checksum、数据视图 SHA、训练源码 SHA、采样/监督目标、loss weighting、seed/epoch 和 checkpoint SHA，选少量成本可控的**科学上有意义**消融（如源/目标配比、S1 loss 权重、状态 T/H/KV 加与不加、训练轮次/早停、seed）。12 不等于必须跑 12 次数百万样本完整多轮训练；先 12 个小型 pilot 与逐步扩大真实有效候选，结合 GPU/时间/存储和数据证据预算，而不是盲目暴力堆硬件。不得把重读同一个 Epoch 命名为 12 个版本。
- 既有 Laya 38 组正式连续队列维持原协议，已经运行的 Run 自然完成；新数据/新损失分支只能独立 `runs/LAYA-V8-*` 与 `runs/KEV-V8-*`，有独立复现 manifest/checkpoint/cursor/optimizer。Kev 必须有真实 GPU LoRA + Pointer Head 后向，**不是 cpu smoke、不是旧 Kev JSONL 假扮同源**。状态字段要真正输入编码器，不能仅保存 JSON。
- 阶段数据工作：盘点 TRA-001/002/004、CooperBench、Mooncake、BurstGPT 的已下载 revision/sha/许可；复用已有 clean 源；`OBSERVED_AGENT_OUTCOME`/真正 `ROUTER_CHOICE`/`CACHE_REUSE_OPPORTUNITY`/`MEASURED_CACHE` 分证据视图，`resolved=-1` 不是失败；同 task/repo/near-duplicate ID 做 split 隔离。实体数量与“独立训练样本数”不能混称。新增数据必须生成兼容 Laya 与 Kev 的输入目标，并证明数据真正进入训练。
- 固定 Val 的 `S1 Accuracy/LogLoss/Brier/ECE`（还有 S2/S3 与每源切片）＋已发生的真实 Agent DEV Outcome 双通道观察。**不能将自造 Mock 成绩“明显上升”当作模型继续训/停训指标。** 训练可推进追加 Epoch/合法 S1 reweight/阶段式 fine-tune，比较 paired val、置信区间和实际效果。至少在每个模型候选池达到 12 个有效版本并有稳定验证后，才允许**基于科学证据考虑**停止探索；没有改进时必须如实记录 plateau/negative result，而不是无限循环直到指标人为升高。
- 记录启动日期/正常结束条件、具体硬件资源预算和试验数量上限；当 OOM、超存储/超运行预算、数据源许可或 Test 泄漏、明显训练发散时只停对应新增任务，保留物理 best 与可恢复 latest。服务请求可配置优先级/QPS，不以后台训练为由泄漏 Test 或争抢 GPU；单 A6000 双训练是否可持续仍必须测有效任务完成时间。

### 8.4 全部选定 Benchmark 和真正的对手方法

- **Benchmark 源码**必须本机物理下载、独立固定完整 revision，并记录 `git rev-parse HEAD`、许可、大小和官方任务数量：Terminal-Bench 2.1 `harbor-framework/terminal-bench-2-1` 且 lock `7131e4375048a0e408a8fb404b5f499d726b695b`；TwinRouterBench `CommonstackAI/TwinRouterBench`；SWE-bench `SWE-bench/SWE-bench`（必要轻量拉官方代码/数据加载，避免一次性拉多百 GB 镜像）；Harbor `harbor-framework/harbor`。在 `external/benchmarks/` 下**真实 checkout** 或对第三方做正确 submodule/ignored checkout，不能以自建 manifest 文件当下载完成。原始 Benchmark 任务/测试数据绝对不训练；89 题的 8 Canary/24 Dev/57 sealed 原划分仍生效。
- **外部方法** `lm-sys/RouteLLM` 和 TwinRouterBench 实际 SR-KNN 实现或原出处 `vllm-project/semantic-router` 分别在 `external/router_methods/` 拉取源码并固定 SHA，同时归档公开论文的 BibTeX/DOI/官方 PDF 的获取说明与原方法配置。若仓库不提供可独立复现的预训练路由器或需不可得权重，就在允许 DEV 上训练必要公开模型并标 `REPRODUCED_TRAINED`；不能简单以自写关键词阈值/8 个人工 exemplars 冒充论文方法。**所有能合法实现的选定方法都进行 1–2 个同协议真实决策/真实 Agent 测试**；有权重/环境限制的如实 `BLOCKED`，不虚报。
- 至少 `FixedStrong, FixedCheap, RuleSticky, RouteLLM-real, SRKNN-real, Laya-real, Kev-real` 采用一致 `select(state,legal_actions)`。Laya/Kev 接服务器 API，而非 Mac 权重。测试选 `fix-git` 与 `count-dataset-tokens` 优先：先官方 Docker 容器和评分器真实工作，再 1–2 题代理执行。TwinRouterBench 和 SWE-bench 若可做廉价 smoke，至少验证官方数据加载/一个 API/环境入口，不把 `LOADED_ONLY` 称任务真正完成；官方对比评测需生成实际 evaluator 文件。
- 验收台账对每个方法/Benchmark 分 `SOURCE_DOWNLOADED, IMPORT_OK, OFFICIAL_ENV_READY, REAL_API_CALL, REAL_AGENT_EVALUATED, BLOCKED` 和完整命令、上游 revision、测试输出路径。

### 8.5 CC Switch、GPT-6/Luna 与三种协议的真实集成

- **CC Switch 是用户 Mac 上已有的配置，不是给模型联网搜索出来的公用 URL**；优先查看本地 `~/.cc-switch/`、`~/.codex/config.toml`、`~/.claude/settings.json` 的**必要非秘密字段**并确认已启用的 CC Switch Local Routing。不要 print/cat 整个 Secret JSON/TOML，不修改/覆盖用户现有配置，不将 Key 复制到仓库、Shell 历史、看板、运行日志或提交内容。优先直接使用 CC Switch 已有本地代理（如运行中 `127.0.0.1:15721`，**仅当真实检测到才使用**），让其转发认证，或使用不回显的本地钥匙链/环境/权限受控文件。注意订阅型 Codex OAuth/ChatGPT 凭证并不等于获准复用为第三方 API 密钥；只使用当前已有权限和 CC Switch 官方支持的本地代理/Provider，若服务不允许外部实验调用则不绕过。
- **模型名**：选择用户要的 GPT-6 和 Luna；用实际 `GET /models`、CC Switch Catalog 或公开 Provider 映射核对最终 API `model_id` 与可用协议（Luna 可能是 `gpt-5.6-luna` 或 CC Switch 内部的 `gpt-6-luna`，**绝不臆造同一 ID 或假设用户账户可访问**）；只有真实模型返回成功的 `model_id` 可写为 VERIFIED。按所选 Provider 的实际模型支持过滤 native effort。
- 新建 3 个独立但共享 `GeneratorResponse`、`UsageRecord` 的协议适配器：`OpenAIResponsesProvider` → `POST /v1/responses`，正确解析 output 的多种 `message/tool_call` 块和 `usage.input_tokens/output_tokens`；`OpenAIChatCompletionsProvider` → `POST /v1/chat/completions`，解析 `choices/message/tool_calls`、`usage.prompt_tokens/completion_tokens`；`AnthropicMessagesProvider` → `POST /v1/messages`，根据上游要求使用 `x-api-key` 或 Bearer + `anthropic-version`，解析 `content[].text/tool_use` 和 `usage.input_tokens/output_tokens/cache_read_input_tokens/cache_creation_input_tokens`。不支持的 reasoning_effort 不发送；messages 与 responses 的 system/tool/stream 处理按官方协议，不能把三种 API 简单替换路径当兼容。
- 每个 Provider 配 `base_url,api_format,model_id,auth_ref,max_output_tokens,timeout_s,max_inflight,rpm,tpm,retries,price_snapshot,effort_map`；兼容非流式至少成功 1 次，若需要 streaming 再做真实 stream 的 chunk 组装验证；同时测试正常/401/429/5xx/超时/缺 usage/工具调用的单元或 Mock 合约，错误时不会泄漏密钥。
- **今晚总真实 API Token 上限是 1,000,000（严格小于，不可超过）**：一个全局持久化 `token_budget.json`，所有主/子代理、Benchmark/竞品/协议/重试/Router 服务调用占用同一个累加器。对有 token usage 的每次尝试核 `input + output`，包括 reasoning 部分若已包含在 output **不再重复加**，真实未知 usage 用预留 upper bound 冻结后补账；发请求前预留 `estimated_prompt_tokens + max_output_tokens` 并考虑历史与最坏重试额度，超过余额一律阻断；全局还有 `max_usd` 和单 task/模型限额。Mock 统计永不混入真实 token 已消耗，但单独显示模拟 tokens。明早之前若 CC Switch 本地已有合法可用 Provider 并允许小额 smoke，可以先进行**几次短连接与极少数真实任务**，须严格费用上限和用户授权，不将大额/无上限真实跑分自动扩容。
- 每次完整请求/响应正文及权限受控附件存 `runs/agent_pilot/.../inputs/outputs`，Git 仅脱敏摘要和来源 SHA；不可记录 CC Switch 原密钥。逐调用的协议、实际模型、usage、缓存、原生 effort、错误/退避次数及当时成本以 append-only 账本保留。

### 8.6 真实 Episode 并发和路由服务正确性

- 当前 Runner 的 `MockSandboxEnvironment()` 必须换成 Harbor 官方任务容器 `environment`、真实 `BaseAgent` 运行路径与官方 evaluator，保持 `Mock` 独立测试入口。Episode 并行（1→2→4…可配置），**单 Episode 内仍只有一个 Agent 顺序执行**。Sandbox 创建/镜像 build 限额独立控制，Mac 资源、Router API 和各 Provider RPM/TPM 并行配额独立 Semaphore/令牌桶；及时记录等待、429、timeout、Provider 重试。
- 单个任务/策略/seed 与依赖版本固定，每次 shell/call 都有唯一 `episode_id/decision_id/request_id`，模型输出工具动作→Harbor 执行→返回 observation→下一步；唯一官方 evaluator 记录 resolved。mock Oracle 的 `FINISH`/假成功不能写入真实成功数。费用统计仅真实调用，模拟成本在独立 `simulated_cost` 字段。
- Laya / Kev 的 Serving `GET /health` 必须分别返回 `weights_loaded` 与 `inference_verified`，实际 route 需要可确认经过正式模型 forward，否则 `HEURISTIC_FALLBACK`；不要在同一报表把 Kev 规则 fallback 写为“Kev 真实推理通过”。纠正 `0.0.0.0` 裸监听与 wildcard CORS，私有端口 + SSH tunnel，并加入请求超时与最小批量/限流以防服务器训练受损。
- 两模型和竞品在相同 1–2 正式任务中控制 `same task, same generator pool, same native effort legal mapping, same harness, same budget, same evaluator`；不同 Router 选择导致实际生成调用不同是真实策略效应，但固定别人的能力不支持的 Feature，不允许“升级对手方法”才显得公平。
- 首页 `docs/training-dashboard/` 保留两列 **Laya / Kev**，开发阶段显示 `ACTUAL/SMOKE/MOCK/BLOCKED` 状态；单独显示真实进度、真实上线模型 Checkpoint、版本≥12候选完成数、API 协议适配 3/3、下载 Bench 3/3、路由方法 2/2、真实 Canary 已执行数与准确区分的模拟与真实费用。看板订阅实时数据但不得把密钥/原文 I/O 推送 Git。

### 8.7 标准目录、成果和自然阶段执行循环

```text
路由/
├── external/
│   ├── benchmarks/{harbor,terminal-bench-2-1,TwinRouterBench,SWE-bench}/  # 克隆的上游 Benchmark / Runner
│   ├── router_methods/{RouteLLM,semantic-router}/                       # 克隆的真实论文方法
│   └── papers/                                                          # 合法公开论文索引/BibTeX/必要官方 PDF
├── experiments/
│   ├── agent_pilot/{agent.py,provider_responses.py,provider_chat.py,provider_anthropic.py,runner.py,configs/,baselines/}
│   └── router_serving/{server.py,laya_adapter.py,kev_adapter.py,schemas.py}
├── router_data/                              # 历史 Laya 主训练 + V8 数据转化 / Kev 可恢复训练代码
├── docs/training-dashboard/                 # Laya / Kev + 开发状态（真实与模拟分开）
├── runs/
│   ├── MR-V8-DATA-EXTENSION-*/               # 服务器源视图/lineage/stats
│   ├── LAYA-V8-*/                            # 服务器新增 Laya 候选 / 恢复点
│   ├── KEV-V8-*/                             # 服务器新增 Kev 候选 / 恢复点
│   └── agent_pilot/<date>/<benchmark>/<policy>/<task>/<seed>/{run_manifest.json,decisions.jsonl,router_calls.jsonl,model_calls.jsonl,tools.jsonl,events.jsonl,episode.json,official_evaluator/,inputs/,outputs/}
└── .runtime/
    ├── dashboard/                            # 采集/网页服务日志
    └── agent_pilot/                          # Sandbox 缓存、下载中间文件、锁与 Secret 引用
```

必须保留现有 `PROJECT_STATUS.md` 和数据唯一台账。阶段分别：`S0 源码与凭据安全检查 → S1 全量 Bench/方法源码下载 → S2 三协议短 smoke → S3 真实 Kev 推理 → S4 两模型≥12 候选训练与数据融合 → S5 Harbor 官方 Docker 1–2 题 → S6 真 RouteLLM/SRKNN 1–2 题 → S7 真 Laya/Kev Router 1–2 题 → S8 并发/账本/看板 → S9 阶段总结`，可并行重叠但每部分需可核的 manifest + 日志 + 回滚路径。Git 上线只保存可复现代码、真实脱敏结果和出处，完整 I/O 与密钥永不 Push。每完成一阶段：检查工作树→保护未提交工作→从 origin/main 安全快进→**重读六份最新文档及本节 §8**→验收证据→整理服务器与本机目录→更新正确权威文件→定向 commit/push→再次核 SHA→继续。新实验出错仅停止该新分支，不中断健康的历史正式训练。

**最终硬验收**：① 官方 Benchmark 源码+SHA 真正下载且官方任务环境可运行，② 2 个外部方法真实算法而非规则伪装至少各 1–2 个同协议样例，③ GPT-6/Luna 在可用 CC Switch Provider 上完成短调用，Responses/Chat/Anthropic 各至少一段实际可用协议路径或标明确不可用，④ 所有真实 API 请求累加计量严格 < 1,000,000 tokens，⑤ Laya/Kev 均获得来自合法增补数据的阶段性验证，≥12 个有效不同候选（如不能在一个夜晚做完继续长周期，不准假报），⑥ Kev 必须是实际权重推理且真 GPU 训练，⑦ Harbor 官方 1–2 Task 真 Agent+官方 grader 闭环，⑧ 受保护账本与双模型看板真实/模拟分离，⑨ 主 Agent+恰好两个子代理，阶段性 Git 复读/提交同步，⑩ 所有训练可恢复、合规、不抢断健康主线。对外展示任何无法通过的步骤用 `BLOCKED + cause + next bounded action`，不要直接宣称项目完整完成。
