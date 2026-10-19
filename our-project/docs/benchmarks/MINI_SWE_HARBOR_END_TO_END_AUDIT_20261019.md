# ModelRouter · 最小 Agent、原生 Harbor、模型信息与迭代式终端实验全链路核验（2026-10-19）

> 证据界限：核验 GitHub `cdb1398e7e2b6d56e105152450bab2774bb16d52` 的源码/结果与外部官方 Harbor、Terminal-Bench 2.1、mini-swe-agent 文档。**没有 SSH 读取此刻的 A6000、没有运行本机配置的 API、没有实际启动官方 Harbor Trial**。不能据此称整条链路已成功完成。

## 0. 概要结论与最重要的即时纠偏

1. 当前项目**不是 mini-swe-agent**，而是自研 `modelrouter.agent.agent.SingleAgent` ReAct/Reflexion 和单独的 `modelrouter.benchmark.harbor_agent.ModelRouterHarborAgent`（Harbor import 失败时还落入本地 Stub）。
2. **建议实验主 Harness 改用上游 mini-swe-agent v2 的官方 Harbor 集成作为固定、最小执行循环**；将自身 Laya/Kev 或对照政策仅插到每次 Generator 调用前（Policy/Model adapter），统一 Prompt、工具解析、失败处理、终止条件、命令执行与官方 Verifier。当前自研 Agent 只作兼容/附加实验，不能与正式 mini Agent 混合主表。
3. 官方 `harbor run` 支持内置 `mini-swe-agent`，官方 **Terminal-Bench 2.1** Dataset ID 是 `terminal-bench/terminal-bench-2-1`，而不是 2.0 的 `terminal-bench@2.0`。官方 2.1 仓库 https://github.com/harbor-framework/terminal-bench-2-1；运行文档 https://github.com/harbor-framework/terminal-bench-docs/blob/main/content/docs/run-terminal-bench-2-1.mdx；Harbor CLI https://github.com/harbor-framework/docs/blob/main/cli/run.mdx；mini-swe-agent v2 https://github.com/swe-agent/mini-swe-agent 。`8 Canary / 24 Dev / 57 Sealed` 是**项目自己的** 89 题任务切分，如未在上游对应切分证明中出现，不得冠以“官方切分”。
4. `modelrouter.benchmark.run_official_harbor_trial.run_trial` 在 Docker 为 True 时也将 `official_evaluator_executed=False` 写死，记录 `PENDING_OFFICIAL_VERIFIER`；其代码尚**没有执行 Harbor 正式 Job/Trial 和 Verifier**。只有 Docker 许可仍 `BLOCKED_PERMISSION_REQUIRED` 的证据；此前 63 项 pytest 全绿不是官方任务全链路通过。
5. **报告声称 RQ1–RQ5 的精确百分比是科研高风险**：`rq3_analysis.py` 的 `empirical_matrix` 固定数组写入 57.5% 与 $0.0058；`rq2_analysis.py` 直接根据 pool_id 指派模拟 Pass@1；`rq4_analysis.py` 读预先填有 0.702 等数的配置；`rq5_analysis.py` 从 Manifest 直接读取预填的 baseline/router Success，再以既定 0.72 写 Phase boundary。RQ1 从 `experiments/agent_pilot/ledgers/experiments_ledger.csv` 算，里面的 Episode 没有官方 Verifier/Job 路径且部分 0.001s 的任务“成功”来自非官方或 Mock 测试。故全部这些**不是论文正式官方任务效果**。现有输出仅保留 `DEMO_SYNTHETIC_OR_UNVERIFIED`，不得在正文报告为真实结论。
6. **模型注册体系至少两套**：`our-project/code/src/modelrouter/providers/registry.py` 含实际基础模型/别名与价格，而 `our-project/experiments/configs/model_registry.json` 包含另外 12 个拟议池成员。名称不一致（例如 `deepseek-chat` vs `deepseek-chat-v3`）、价格和 Native Effort 可能陈旧；实际 `gpt-6-luna`/`gpt-5.6-luna` 经代理商 `jiji` 对接，并非可凭名字认定 OpenAI 官方 API 模型。必须 **以服务商返回、真实支持能力、计费来源和冻结版本为准**。
7. 在 `RouterClient` 请求失败时目前默认调用 `MockRouter` 作为 fallback；这种 Episode 必须标 `ROUTER_FALLBACK`，正式“神经路由真实效果”与其剥离。Laya `criteria` 的 `opt_N_provider_model_effort` 动态排序映射、Kev `admit` 内 `label=0` 哑标签和模型 `probs` 的输出类别顺序需要逐项人工/测试对齐。不能把真实前向概率本身当作已证明正确的动作预测。

## 1. 最小 Agent 决策与三个真正可测层次

- **Level A：内置 `mini-swe-agent` + 一种已验证的真实模型**：验证环境、官方工具、Agent 基础 loop、Verifier；这不是动态路由实验。
- **Level B：固定同一 mini-swe-agent + 自己的 RouterPolicy Hook**：每次生成之前按 `AgentState` 建立冻结决策前快照，POST /route 得到 `provider/model/revision/native_effort` 并执行真实 Generator 请求；与 Level A 相同的 Prompt、Tool、状态和资源约束；定义 `modelrouter.benchmark.mini_swe_harbor_agent:ModelRouterMiniSweAgent` 作为 Harbor `--agent-import-path`，按**实际安装** Harbor/minisweagent API 版本实现，不可复制/伪造其 BaseAgent 或主 loop。
- **Level C：同任务、同 Seed、相同环境及 Harness 的 Fixed/Random/TaskOnly/Laya/Kev 等策略矩阵**；每 Trial 要有官方 Verifier、原始 Usage、计费、延迟、配置 SHA、模型/Agent/Sandbox 版本。不能将 Harbor 预设固定单模型 Agent 与不同自研 Agent 的运行结果直接归因于 Router 政策。

### 推荐官方 CLI 最小真实验收序列（在 Docker/授权 Sandbox 可用后）

以下命令是**官方推荐或遵循官方文档的待服务器实测例子**，并不表示目前已运行。每条先做 `harbor --help`、`harbor run --help` 确认安装版参数、数据源权限与模型真实名称。

```bash
harbor --version
harbor run --help
harbor datasets list
# 一题官方 Oracle，无付费 Generator：先验证任务、环境和官方 Verifier
harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 1 -n 1
# 内置 mini-swe-agent，使用本地已验证可用的 OpenAI-compatible endpoint 所支持的模型别名
# 此处 openai/<VERIFIED_MODEL> 是 CLI 格式示意，绝不可原样当成真实可用模型
harbor run -d terminal-bench/terminal-bench-2-1 -a mini-swe-agent \
  -m 'openai/<VERIFIED_MODEL>' --include-task-name '<VERIFIED_CANARY_TASK>' -n 1 -k 1
# 自定义本项目路由版 mini-swe-agent (仅完成真实 BaseAgent 契约代码后可启用)
harbor run -d terminal-bench/terminal-bench-2-1 \
  --agent-import-path 'modelrouter.benchmark.mini_swe_harbor_agent:ModelRouterMiniSweAgent' \
  --include-task-name '<VERIFIED_CANARY_TASK>' -n 1 -k 1
harbor view jobs/<REAL_JOB_ID>
harbor jobs resume --job-path <REAL_JOB_DIRECTORY>
```

API URL 与 Key 从本机既有配置映射到实际客户端环境，不改变/打印密钥；尽可能保留已有用户费用限额。不要将令牌通过 `--ae KEY=value` 放到易泄露的 Shell 历史中。不同提供商的 LiteLLM 模型前缀、responses/chat 请求与 effort 必须先使用低成本请求真实探测。

## 2. Terminal 可观测、复跑与速度/费用指标

实现一个**真正的唯一入口** `python -m modelrouter.benchmark run|preflight|watch|resume|summarize|export`（或 `modelrouter experiment ...`），可在 Mac SSH 启动 A6000 已授权的 Harbor 任务，且不干预正在满载的 Laya/Kev 训练。

```
[19:14:00] PREFLIGHT  harbor=... dataset_sha=... sandbox=AUTHORIZED api=VERIFIED agent=mini-swe-agent@...
[19:14:03] JOB_START  job_id=... policy=fixed_strong pool=... task=... trial=1/1
[19:14:45] AGENT_STEP episode=... step=2 model=... effort=... route_ms=... ttft_ms=... decode_tps=... in=... out=...
[19:14:51] TOOL       step=2 cmd_type=shell exit=0 duration_ms=... sandbox=harbor
[19:15:10] TRIAL_END  official_reward=... complete_usd=... latency_s=... verifier=real
[19:15:11] ITERATION_SUMMARY complete=... failed=... cost=... speed=... next=...
```

支持 `--dry-run`、`--canary`、`--dev`、`--sealed`（Sealed 默认禁止执行，须明确负责人授权）、`--n-concurrent`、`--max-usd`、`--max-tokens`、`--timeout`、`--resume`、`--job-name`、`--log-dir`，所有配置生效前先校验与写一份完整脱敏 `run_config.json`。项目实验状态必须有可重放 `run_id`、单一数据源 `task_manifest SHA`、唯一 `policy/config SHA`。

**进度**：总任务数、已完成/真实成功/失败/超时/Blocked、最近 Trial 和 ETA（从实际已完成任务统计）；5–15s 写一份原子 `progress.json` 供 8765 Dashboard 读取，客户端终端不断展示滚动事件。中断后 Resume 只对未终局任务继续，保留已有 Trial 幂等不重计费。

**速度**：区分 `router_p50/p95_ms`、`generator_ttft_ms`、`generator_output_tokens_per_s`（含/不含 reasoning 的定义）、`tool_exec_ms`、`episode_wall_s`、`episodes_per_hour`、`cost_per_resolved`、`model_throughput_per_provider`。如果非流式 API 或没有准确 Usage/TTFT，记录 `N/A`，不能伪造采样。Router Laya/Kev 的 **纯前向** 延迟与远端生成模型的 **解码速度** 分开，不能把 Kev 3.2s 当成 Generator TPS。

**进度来源**：Harbor 官方 Job/trials/traces、ATIF、Router/Provider 实际带单调钟的日志，禁止人工写 `success_rate` 作为监控值。

## 3. 每次迭代结束的固定复盘机制（强制）

每批 1 / 8 / 24 个 Trial 或每个真实功能增量完成后，自动输出 `our-project/results/iterations/<iteration_id>/`：

- `run_config.json`：所用代码 SHA、官方 Dataset 版本、任务 ID+SHA、Agent/Harness/模型池/政策及成本表版本、环境隔离、Seed、配置；
- `events.jsonl` 与 `tool_calls.jsonl`：每次 Agent 工具执行的命令/耗时/退出码和原始 Harbor Trace 关联（大量敏感原文留本地），包含每步模型身份/Effort、Router Decision、费用；
- `official_trials.jsonl`：每个 Trial 与真正 Harbor Job、Verifier Artifact 的一一对应。无证明就必须 `NOT_EVALUATED`；
- `metrics.json`：成功、成本、延迟、吞吐、工具开销、样本及 CI 的可再计算数据；
- `review.md`：这轮做了什么、调用了哪些工具、哪些成功/失败、发现的原因、对五个 RQ 的信息增量；
- `next_iteration.json`：未解决问题、下轮假设、最小验证计划、依赖、已发现性能瓶颈和新风险；
- `resume_state.json`：原子保存 Job/Trial 当前状态和续跑位置；
- `artifact_manifest.json`：所有文件哈希、路径、生成脚本、是否官方；GitHub 只提交脱敏小型摘要。

**持续实验不等于静默循环**：每轮都必须能根据失败类型（SANDBOX, DATASET, API, ROUTER, AGENT, VERIFIER, COST, SCIENTIFIC_DESIGN）选择下一动作；遇同一确定阻塞不可一直重试/重复花费 API Token。未经允许不能靠更换冻结测试集或私自改标注提高指标。下轮必须显式读取上一轮的 `next_iteration.json`，确认解决/保留哪些遗留项。

## 4. 模型信息输入与路由端到端字段审计

由两个子代理协同，从 **URL/Key 私有配置 → 模型/能力注册 → LegalAction → PreDecisionState → Router → Generator → Harbor Exec → Verifier → Ledger**，逐字段核验：

- 模型标识：`provider_id`、`provider_model_id`、`user_alias`、`canonical_model_id`、`version/revision`、`base_url_id`、`api_protocol`、`availability`；返回模型身份不一致必须单列别名映射和证据；
- 能力：Chat/Responses/Stream/Tool、`native_efforts` 真支持列表、模型上下文/max output、结构化函数调用、重试/超时/429；
- 费用：官方/代理计价来源和截面时间，input/output/reasoning/cache_read/cache_write 单位和去重（**不能把 reasoning 既算进 completion 又再计一次**）、每次实际 Usage 与推算成本偏差，缺字段应 `UNKNOWN`；
- 路由：`request_id/episode_id/decision_id/policy/checkpoint/pre_decision_state/legal_actions/budget`，收到选择的 action 必须与已验证支持集完全一致；固定 Seed/同任务 action mapping 稳定；**绝不泄漏未来 verifier/tool outcome**；
- Laya/ Kev Encoder：Laya `opt_N_...` 动态顺序与训练 target class 一致；Kev dummy `label:0` 不影响推理概率，`probs` 输出维度/顺序与 LegalAction 完全对齐；合法动作 1、2、4、K+Effort、非法/不支持 Effort 都做 Golden Test；选择错误或 MockFallback 的 Episode 不能进入主要真实对照；
- 并发与续跑：预算/账本写入原子、一致性、不重复收费；超时/重复请求/同 episode 重放合法且不可泄漏状态；真正的 Token usage from provider 与预估量分别保存；
- 速度：路由模型 checkpoint/device/tokenizer+input_length/batching 与路由耗时，生成模型的 TTFT、模型 tokens/s 和全 Episode 速度分别显示。

**关键源码问题**：`modelrouter.providers.registry.ModelSpec.calculate_cost` 对 `completion_tokens` 和 `reasoning_tokens` 单独计价，若 upstream 的 completion 已包括 reasoning 就会重复计算；必须依据 provider 字段语义修正并有黄金账单测试。 `modelrouter.agent.router_clients.RouterClient` 目前默认 MockRouter fallback；不能作为正式成功 Episode。

## 5. 官方其他 Benchmark 的逐个真实验收

**主论文标准**：Terminal-Bench 2.1，必须锁定本研究所用上游版本和题目 Manifest，严守 8/24/57 自定义 Canary/Dev/Sealed 管理。

**辅助 / 外部对照**：同一 Harbor 安装的 `harbor datasets list` 中选择项目声明要覆盖的**官方可用** SWE-Bench 及 Aider Polyglot（需确认各自版本、许可证、官方适配、任务容器/Verifier、mini-swe-agent 是否适用）；其他 TwinRouterBench/LLMRouterBench 主要是静态路由或不同协议，必须有各自真实官方运行脚本，不能把静态 Accuracy 当 Terminal-Bench Agent Success。

对于每个 Benchmark 建 `benchmark_registry.json`：`upstream_url/commit/dataset_id/release/checksum/runner/official_verifier/sandbox/agent_compatibility/task_count/partition/evaluation_unit/metric/real_trial_id/artifact/status`。

每个 Benchmark 的最小验收：`list/download/sanity oracle/one REAL mini Agent/one REAL Router Agent/official verifier/export reproducibility`。缺官方适配/权限/任务镜像时明确记录 `BLOCKED`。

## 6. 工作分配 / 关卡

**主 Agent**：维护唯一 Harbor/mini-swe-agent 入口；管理官方 Docker 或已授权云 Sandbox；保护 A6000 99% GPU 训练和 8000/8765 现役服务；回看每个阶段真日志、阻塞和下轮任务；最终写 Git SHA。

**子 Agent A（Agent/Benchmark）**： mini-swe-agent v2 可复现接入、真实统一模型/动作路由、官方 2.1 / SWE-Bench / Aider Polyglot 任务与评估器、Harbor CLI、自动运行/断点续跑；先做权限前可运行的 CPU/Unit、官方 Oracle 后再一题真 Agent。

**子 Agent B（数据/模型/监控）**： 2 套 registry 和 Provider URL 模型能力真实性、状态特征编码、Laya/Kev 训练映射 Golden Test、Token/费用正确性、TPS/TTFT/Router latency、Dashboard 实时链路、RQ1–RQ5 图表证据追溯。

**验收门禁**：
`UNIT_CONTRACT_PASS` → `MODEL_PROVIDER_REAL_PASS` → `HARBOR_SANDBOX_ORACLE_PASS` → `MINI_AGENT_OFFICIAL_VERIFIER_PASS` → `MODELROUTER_MINI_OFFICIAL_VERIFIER_PASS` → `CANARY_8_TASK_VALID` → `DEV_24_TASK_VALID` → `RQ1..5_REAL_EPISODE_RESULTS`。失败或 BLOCKED 停在相应阶段且继续其他 CPU 有效工作，不得直接标“ALL_DONE”。

本说明**不许可**自动跑 57 题 Sealed，更不支持私自把硬编码百分比当作官方发现。先将所有现有 Fig.3–8/Table3–11 按来源隔离到 `DEMO/UNVERIFIED`，在真正 Harbor Trial 后再自动替换成可溯源正式图表。
