# ModelRouter V9 · 双子代理长周期 RQ 工作计划（不中断 Laya/Kev，2026-10-19）

> 本文结合 2026-10-19 17:25 CST 现场报告、GitHub `afd3af39e87b439fe1d651d6a918650c1e63e649`、V9 权威 `汇报/汇报三/ModelRouter论文实验与图表规划.md` 和 Q-019。**这是未完成科研工作安排，不是声称有真实 Agent Benchmark 结果。** 外部 Laya/Kev 的正式 GPU 训练已在跑，A6000 GPU ~99%，不得因有显存余量并发发起第三个大 GPU Job。

## 0. 状态验收与立即免返工项

- 17:25 报告：Laya F06 当前 Epoch2、Chunk 138/361、Step 63,804/92,280、Loss 0.4662；Kev C03 12,050/16,857、Loss ~1.032；与最新 GitHub `our-project/dashboard/live_status.json` 一致，前 100 分钟均推进。
- GitHub F06 Epoch1 已写入 `S1 0.6738、S2 0.5816、S3 0.6058`（来源运行记录声称 `F06/epoch_metrics.json`）；F06 S1 暂未超过历史 `P0_B03_C01` 的 0.6863，也略低于 Serving F05 0.6756。训练继续按自然 Run/固定验证和 Checkpoint 选择，不为单个 Epoch 未创新高返工。
- 看板报告已常驻 A6000 `http://10.16.15.202:8765/`（私有 LAN/VPN 地址）；只要负责人 Mac **实际访问正常**且图表刷新、Cursor 匹配即验收，**不要重做页面**。GitHub 快照是监控归档，不要求每五秒向 GitHub Push。
- 当前定量进度存在 ETA 不确定性，按 Step/s 和自然 Run 结果推算，不为不准的 ETA 重启训练。Kev 后续调度器 C04 等维持既有唯一任务，不新增第二调度服务。
- 本地 Generator Key 的唯一要求仍是**不进入 GitHub**，无须调整或审计用户已有费额上限。Harbor 仍因 Docker socket 访问被拒绝而 `BLOCKED`，无官方 Task Success 可报。

## 1. 两个子代理可以长时并行做什么？

### Agent A · 研究数据、模型池与消融准备（CPU/IO 任务，覆盖 RQ2/RQ4/RQ5）

从当前 `our-project/code`、`our-project/data` 和 `our-project/experiments` 现有工程继续，**不要另起 Python 包与新项目**。

1. **RQ2 Pool Registry**：核对真实可用 `provider/model/revision`、各模型自己的原生 Effort 菜单、计价版本和上下文/工具支持；构建实际允许的 `Pool P_K` 候选矩阵。区分模型身份数 K 与合法 `Σ_m |E_m|`；同 K 按不同成员组合、不同 K 按规模对照。没有可用具体模型的池标 `NOT_EVALUABLE`，不得把 gpt-6-luna 的错误别名转换为另一种模型。冻结 `model_pool_registry.json`、`pool_comparison_manifest.json` 与示例测试。
2. **RQ4-A Action**：列出合法 `fixed model+effort / model-only / effort-only / hierarchical / joint`；在统一合法动作过滤器后做单元测试；原生 Effort 只能选择 Provider 实际支持的组合，不能统一伪造 Low/Medium/High。
3. **RQ4-B State**：从真实决策前 AgentState Schema 整理 T(任务、子任务和已知 Agent 角色)、M(候选经济性/能力)、H(已发生上下文、KV 机会、Trace、验证反馈/预算)，实现合法特征遮蔽 T/M/H 7 种组合及关键单变量；任何时刻未来信息及模拟 KV 缓存命中不得进入真实状态。
4. **RQ4-C Supervision**：盘点冻结 S1/S2/S3 及新三视图来源、许可证、行数、独立任务、真实标签、train/val/test group leakage，验证哪些确实进入 Laya/Kev 的编码和梯度；可以完成**低资源 CPU 数据准备/配置/验证**，绝不在 A6000 99% GPU 时新启动完整大模型微调。V8 50-step `POINTER_HEAD_V8_PILOT` 与 Kev 4B 完整 LoRA 严格分离。
5. **RQ5 Stratification**：对官方任务可在执行前观察的元数据进行**预注册**，分类依据如技术领域/已知工具/任务指令长度/静态依赖结构或已有 Benchmark 官方难度；形成工作负载分层、独立 task count 和不可事后篡改的 manifest。不得以运行失败、后续 Step 数或 Trace 生成 `initial_difficulty`。独立测试 57 题封存且不看结局。
6. **统计模板**：基于真实 Episode Schema 先实现成功率/完整 USD/Router 成本/缓存计价/重试费用、配对任务 bootstrap CI 和成功率约束下 Savings，不填不存在的数。结果归属 Fig.5/T6、Fig.7/T4–5/T8/T11、Fig.8/T9；未获得实际 Episode 就只生成带 `NOT_EVALUATED` 标签的空表/可运行统计测试。

可提交路径：`our-project/code/src/modelrouter/{providers,telemetry,datasets}/`、`our-project/experiments/{configs,manifests,protocols}/`、`our-project/data/manifests/`，实际命名遵循现有包结构。每个提交带 3–5 个单元测试、完成/等待真数据状态。

### Agent B · Agent/Harbor 同一评测底座、RouteLLM/SR-KNN（CPU 编码/不收费调试，覆盖 RQ1/RQ3/RQ4）

1. **唯一真实 Sandbox**：复用官方 Harbor 当前锁定版本 `BaseAgent` / `BaseEnvironment.exec` / `Job Trial` 与官方未改评估器；不复制 Harbor 自己的 Docker 实现、不在宿主执行模型产生的 Shell，不用模拟 `trial_id` 当官方成功。现有 Docker socket 未授权则在 **单元契约、解析、纯 CPU dry-run** 范围持续建设，并标 `BLOCKED`；绝不要求擅自提权。
2. **RQ1 同一 Harness**：实现 FixedStrong、FixedCheap、BestFixedOnDev、RandomEpisodeMix、TaskOnly、Greedy/Sticky、Laya、Kev 的统一 Episode record schema：`task_id,pool_id,policy,G,F,effort,seed,trial_id,official_verifier,terminal_resolved,actual_tokens,actual_usd,retry_usd,router_ms,latency`。同任务冻结集合跑全部政策，无官方评分就 `NOT_EVALUATED`。
3. **外部真实方法**：RouteLLM 必须使用上游官方可复现模型或在合法开发数据上拟合、记录协议/权重/概率标定；SR-KNN 必须在干净已标注开发数据的 8D 表征拟合支持向量样本库，而不是静态手写 16 条样本。若缺所需标签/训练权重，标 `REPRO_BLOCKED`，保留 `length_heuristic` / `step_heuristic` 名称，不称“official”。
4. **RQ3 粒度实验**：在同一个真实 benchmark task_id 上构造**可复现** G0 单 Agent / G1 阶段 / G2 功能子任务 / G3 可验证细粒度（只有可行时），固定池/Router/合法 Effort/总任务预算；真实记录 agent_id/role、handoff、每个 F 路由边界、context transfer、总工具调用、成功、完整费用。完成纯逻辑/格式测试，不为凑题制造无法评分的合成目标。
5. **官方任务与结果**：严格保持 Terminal-Bench 2.1 的 8 Canary / 24 Dev / 57 Sealed；静态任务 SHA/许可证/镜像/Verifier 清单。完成 Harbor 首个官方 Trial 的全部不收费准备。仅在具备**合法授权、正式任务镜像、真实 Evaluator**后执行 Canary 小试；未获授权时不可用 64 Mock concurrency 替代。第一批有效 Dev 任务由主 Agent 决定何时授权真实 API 费用。
6. **结果归档**：Fig.3/T3/T10、Fig.6/T7 的 Schema、空结果表、CI 代码、异常轨迹分类器（PROVIDER_ERROR、SANDBOX_BLOCKED、TASK_TIMEOUT、TOOL_ERROR、REAL_FAIL 等）就绪，输出全路径与非原始内容脱敏 Manifest。

可提交路径：`our-project/code/src/modelrouter/{agent,sandbox,benchmark,baselines,telemetry}/`、`our-project/code/tests/`、`our-project/experiments/manifests/`；不得向 Git 提交原始敏感 Episode 内容。

### 主 Agent · GPU Run 保持与集成负责人

- **只观察、不干预** F06、Kev C03，适度抽查 Cursor 步数/训练 loss/GPU 及 Port 8000/8765；不高频提交重复快照到 GitHub。Laya F06 E1 已验证 S1 67.38%，按科学协议自然完成 E2 再与历史 68.63% 对比，不用因单次下降重跑。Kev C03 完训后验证 2,437 条 Kev 原固定 Val，再由当前唯一 Kev 调度器 C04 接续；确认退出码/Checksum/Val/LoRA rank 实效。
- 对 A/B 的研究接口与任务级实际实验矩阵做最终集成和验收，不新增下级子 Agent，不制造新 Watcher/CI/数据库、不要为短进度报告频繁唤醒 GPU。
- **真评测支付门禁**：在 Harbor 官方隔离 Verifier 通路完成并经批准的模型/费用/Token 窗口可控前，两个子代理**不得花真实 API Tokens 扫全矩阵**；已有全局 1M 预算要避免并发重复计费，检查现有硬 Token 预算原子预留；额度限制不要求变更用户 API Key。
- 结果评审顺序：RQ1 同 Harness 真实 Episode → RQ4 主要消融 → RQ2 同 K/不同 K → RQ3 同任务拆分 → RQ5 预定义分层/交互。**研发准备可以并行，收费的真实任务阶段要有依赖门禁**。
- 每个子代理至少完成一个可验证产物后继续下一个依赖任务，提交可运行源码、单元测试、必要图/表空白模板、真实 SHA 与与 V9 文档对应的覆盖清单。遇到权限/许可阻塞跳过等待动作转做 CPU 任务，不空转、不爆占 GPU。

## 2. 每个 RQ 的真正完成条件

| RQ | 目前共同阻塞 | 离线/CPU 先产出的验收物 | 等授权后的最终科学证据 |
|---|---|---|---|
| **RQ1 Overall** | 官方 Harbor Trial & 可比策略基线 | 策略/Harness/费用统一接口、任务清单、真实上游基线拟合 | 同任务终局 Success 与完整 Episode USD；Fig.3/T3/T10 |
| **RQ2 Pool** | 真实模型清单/合法 Effort 与同 Harness 运行 | Price+Effort 版本锁、同 K 多成员/不同 K 矩阵 | K/池成员的边际 Task Success–Cost；Fig.5/T6 |
| **RQ3 Decomposition** | 多 Agent 可复现的 G/F 同任务流程与官方评分 | G0–G3 固定模板、agent/handoff 日志、同任务 ID | 任务粒度 G 与净收益对照；Fig.6/T7 |
| **RQ4 Systematic Ablation** | 动作实际合法、T/M/H 编码与真实 S1/S2/S3 监督 | 受控 Feature Mask、Loss/数据来源冻结表与单测 | 三组消融的 Episode Success/USD；Fig.7/T4/T5/T8/T11 |
| **RQ5 Workload Boundary** | 先验任务分层与足够独立任务量 | Pre-registered workload task metadata、预定 CI/interaction | 固定池/G/Router 下按层与强基线比较、交互检验；Fig.8/T9 |

最重要：**只有真实官方 Episode 才回答 5 个 RQ，Laya/Kev 训练集 Accuracy、基座静态胜率、64 Mock 压测、无 Verifier 的 Agent Trace 不能填主结果表。**

## 3. 长周期推进的具体输出

第一阶段：A/B 现有代码静态检查、任务 Manifest、合法池/努力档位/成本与评测接口的具体可运行 PR/提交；主 Agent 不要求继续写新的大计划。

第二阶段：开发 G0–G3 可重放任务入口、真实 RouteLLM/SR-KNN 训练或诚实阻塞、T/M/H 消融与统计表，具有单元测试、测试输入 SHA、完全不付费/不动 GPU。

第三阶段：获取已授权原生 Harbor Sandbox 后，从 **1 个真 Canary** 开始，确认官方 Trial、官方 Verifier、真实 Terminal Outcome 后逐渐扩到 Dev；只能在预算和授权符合约定的情况下继续收费实验。未授权时继续完成准备，不能填假结果。

第四阶段：对已生成真实 Episode 计算 RQ1/RQ2/RQ3/RQ4/RQ5 结果及 Bootstrap CI、物化正式 Fig.3–8/T3–T11，负结果不隐藏，主 Agent 验证 source manifest 后按阶段 Push。

**完成标准**不是“两个 Agent 一直在线”，而是每个阶段产出可测试的研究资产，直到 RQ 研究矩阵可真实运行。等候 GPU 训练/Harbor 授权时应继续离线任务而不是无意义忙轮询。