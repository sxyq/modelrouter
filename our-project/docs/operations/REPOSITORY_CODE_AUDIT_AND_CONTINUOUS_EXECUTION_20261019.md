# ModelRouter · 全仓代码分类审查、逐步物理迁移与 RQ 长时研发测试令
> **检查日期**：2026-10-19；GitHub 源树基线 `381dcb25e0a8e9ee2ed4e145b83fdb83c9f7b8b4` 之前的全部 **813 个 Git 跟踪文件**（不含本次新建清单），Tree `truncated=false`。本次已逐文件登记路径/Blob SHA/大小与**建议**归类至 [GIT_TRACKED_CLASSIFICATION_20261019.csv](GIT_TRACKED_CLASSIFICATION_20261019.csv)。
>
> 审查涵盖所有受 Git 管理的路径、抽查关键模块源码和 API Schema。**不能代表通过 SSH 直接检查了 Mac/A6000 上 Git 忽略的大文件、第三方 upstream、虚拟环境或当前正在执行的进程**；这部分必须由已具备 SSH 的执行 Agent 使用现有 `our-project/code/cli/inventory_repo.py` 联合服务器现场再核对。CSV `proposed_canonical_path` 是迁移建议，不是“已移动”的证据；`ACTIVE_HOLD` 按运行重要性保守预标，PID/实际消费者以现场为准。

## 1. 全树事实：尚未全面分类完成

| 范围 | Git 文件数 | 分类结论/具体缺口 |
|---|---:|---|
| `our-project/` | 357 | 规范主目录部分建成，自有 Python `src/modelrouter/` 已覆盖 Agent/基线/Serving/Provider/Sandbox/Telemetry/训练少数入口，**Laya 主训练与多数数据清洗代码仍未搬入** |
| `experiments/` | 44 | 历史 Agent Runner、Provider、8 策略、Harbor、Serving 仍有代码，被线上历史脚本 import；不等于新包已取代 |
| `router_data/` | 31 | 25 个 Python + 1 Shell，包括 `all_data,tra,cache_time,env_memory,shared,views,quality_v2,batch_prep,laya_batch_train,run_full_graded_queue,run_kev_continuous_train,checkpoint_retention` |
| `scripts/` | 12 | Dashboard 启动/采集/渲染/浏览器验证、Benchmark 工具、历史一次性交接混合 |
| `docs/` | 19 | 旧训练看板和报告仍处仓库根；与规范 `our-project/dashboard/` **有 15 个文件 SHA 完全相同**，且旧站另有 1 个 `index_verbose_backup.html` 待归档 |
| `research/` | 146 | 其中 **58 份 PDF Git Blob SHA 与 `our-project/external/research/papers/` 的 58 份完全相同**；有独立附图/索引需要按内容合并，不可整目录删除 |
| `external-projects/` | 9 | **9/9 与 `our-project/external/research/project_catalog/` Blob 完全相同**，适合去重/兼容链接 |
| `汇报/` | 183 | 包含多版本汇报 HTML/JS/CSS、静态素材、运行脚本、打包产物；与 `our-project/汇报/` 42 项仅 12 项 SHA 重合；**不能盲删旧展示资源** |
| `papers/`、`runs/`、根目录临时入口 | 7 | 部分研究索引、历史实验摘要与 `prepare_router_data.py` 等入口应建立唯一归属与 CLI 兼容 |
| Git 忽略的服务器 `/external,/models,/data,/runs` | Git 不可盘点 | 已有 37 冷文件迁移/18 保护记录只覆盖当时现场；再次扫盘需核实是否仍有新的活动进程及外部源码依赖 |

**当前两套已存在 `src/modelrouter` 和旧 `experiments/`、`router_data/` 并行。** 切忌凭同名文件认定代码相同：实验旧 Serving 与新 Serving 的 5 个同名 Python Git SHA **5/5 不同**，Harbor/Sandbox 的 5 个同名文件也不同。谁是真实入口必须从 `ps -eo args`、`/proc/PID/cwd`、`sys.path`、调用栈、Git source SHA 查实。

## 2. 用户要求的规范目录：保留 `路由/` Git 根，`our-project/` 为唯一项目主目录

```text
路由/                                  # 保留现有 git 根、现场进程绝对路径
  our-project/
    code/
      pyproject.toml
      src/modelrouter/
        baselines/
          routellm/{adapter,tests,upstream_ref}
          sr_knn/{adapter,tests,upstream_ref}
          fixed_random_rule/
        agent/{state,policy,runner,step_loop,roles}
        sandbox/{harbor_adapter,task_loader,canary_verifier}
        benchmark/{official_trial,episodes,metrics}
        data_pipeline/{sources,cleaning,quality,views}
        datasets/{schemas,adapters,splits,manifests}
        training/{laya,kev,queue,checkpoints}
        serving/{laya_adapter,kev_adapter,schemas,server}
        providers/{registry,api_client,pricing,effort}
        telemetry/{dashboard_sync,ledger,metrics}
      cli/                              # 真实可安装 CLI + 兼容入口
      tools/{dashboard,benchmark,ops}
      tests/{unit,integration,contract,smoke}
    data/{sources,raw,interim,processed,training_views,manifests,summaries,pricing}
    experiments/{configs/{training,agent,pools,ablation},manifests,protocols}
    results/{training/{laya,kev},baselines,benchmark,agent_trials,serving}
    external/
      router_methods/{routellm,sr_knn,other_methods}/
      benchmarks/{harbor,terminal_bench,twinrouterbench,swe_bench}
      research/{papers,notes,figures,project_catalog}
    dashboard/
    docs/{planning,architecture,operations,reports,paper}
    .runtime/
```

**每个第三方方法单独命名空间，明确 `upstream/README+commit+license`（本地 ignore 的第三方源码/软链接）与 `adapter`（自有可提交代码）**。不可将第三方整个 Git clone 或数 GB 权重误提交。沿用服务器正在使用的 `/home/syy/路由/external/` 实际实体，通过 manifest/symlink 规范索引，训练自然边界以后才考虑移动。不存在的目录按有真实代码时创建，拒绝空壳层层嵌套。

## 3. 代码级实际发现：先写回归测试再替换

| 缺口 | 证据位置 | 必须补的最小测试/修复 |
|---|---|---|
| 自有 `modelrouter` 安装边界不完整 | `our-project/code/pyproject.toml` 引用 `README.md`，但目前 `code/README.md` 未受 Git 跟踪；`training/`、`benchmark/`、`data_pipeline/` 当前无 `__init__.py` | CPU 隔离虚拟环境 `python -m pip install -e ./our-project/code` 与构建 Wheel、安装后逐模块 import；仅在必要处补包入口，验证 import 不走意外旧路径 |
| CLI 请求结构与 API Schema 不一致 | `modelrouter/cli.py` 的 `cmd_route` 用 `model_requested`、顶层 `prompt`，但 FastAPI `RouteRequest` 需要 `router_family`、`pre_decision_state.prompt`；解析时还存在 `decision_latency_ms` vs `routing_latency_ms` 的潜在消费者差异 | 用 FastAPI TestClient 测 Laya/Kev `modelrouter route --model kev` 确实选 Kev、含合法动作并解析返回，不允许默认静默跑 Laya |
| 旧 Agent Runner 仍用 Mock | `experiments/agent_pilot/runner.py` 显式 `env=MockSandboxEnvironment()`，旧的 run_real_matrix 依赖旧入口 | 给旧脚本 `MOCK_ONLY/LOCAL_HOST_EXPERIMENTAL` 明确地位；官方评测唯一入口必须走官方 Harbor Job/Verifier，不在旧脚本上换名字冒充正式 |
| Harbor 代码还未形成原生 Job 调度 | 新 `benchmark/harbor_agent.py` 确有继承 BaseAgent 并实现 async run，**但在官方不可 import 时有 fallback stub**；`run_official_harbor_trial.py` 对 Docker 拒绝后 `NOT_EVALUATED`，未看到真实官方 Job/Trial + Verifier 完整执行调用 | 在锁定的 upstream Harbor 做 `BaseAgent` 真正导入契约测试，脱离 Stub；调用官方 Trial/Verifier 的受权限门禁入口；不得把本地 UUID trial_id、真实 API 请求或 Mock 算官方得分 |
| 第三方算法的名称与数学不能划等号 | `harbor_agent.py` 中 `routellm_official` 以 prompt length sigmoid 计算、`sr_knn_official` 以 step 门限返回；自有 adapter 的实际权重/fit 还需核验 | 规则改为 `length_heuristic/step_heuristic`；真正 RouteLLM 用官方算法及可溯源训练/公开权重，SR-KNN 用真实已标记库 fit + 特征归一化与距离检索；与伪基线结果隔离 |
| Kev 候选执行的科学性 | `training/kev_candidate_dispatcher.py` 以 PID 存活判断完成，当前 `run_fixed_validation` 仅存 `raw_output` 尾部并返回成功，未真正结构化 Accuracy/NLL/Brier/ECE | 在 C03 未结束前做离线 mock process+真实 stdout fixtures 测试；取训练实际 exit code、完整 tokenizer/adapter 物理检查、评估解析与停止队列；C04 Cosine 不可只用减小 LR 替代 |
| 新 V8 全模型训练口径 | `v8_real_finetune.py` 50 步确改旧 Kev Pointer `q/k`；但只用 token embedding 均值编码，未通过完整 Qwen Transformer/LoRA 更新；每视图采样上限目前 100 Train/30 Val | 标为 `POINTER_HEAD_V8_PILOT`；需要同一 Kev 固定 Val 与实际 Serving 加载验证，下一 C09 跑生产态编码/LoRA 才能标 4B V8 正式训练；Laya 新 V8 训练独立实现 |
| 指标与真相源 | `generate_metrics_and_asset_index.py` 预填写 16 历史 Epoch、7 Checkpoint 大小、训练 PID/Step，而非全部实际扫盘；`CANDIDATE_PROGRESSION_MATRIX.md` 仍保留旧 F06 进度 | 通过 `epoch_metrics.json`、`run.json`、checkpoint manifest/实体可加载、`/health` 和 Cursor 动态生成；实体 checkpoint、历史验证、Serving、Queued 分列 |
| 多模型 Provider 与 Token 账本 | 已有本地 generator URL/Key、Responses SSE Mock 和 OpenRouter 定价索引；Provider 真实模型/Native Effort 能力需源端验证，Token 账本请求后计数不是完整并发预留 | 可在已授权本地凭证下跑**少量、真实、带 usage 的** API 探针；标注 unsupported 为 UNSUPPORTED，不擅自将 gpt-6-luna 改成别的模型。真并发实验先以有界预算、唯一账本避免多代理双扣 |
| Dashboard 重复目录/过时页面字面内容 | 15 个老 `docs/training-dashboard` 文件与 `our-project/dashboard` 完全相同，旧 `index_verbose_backup.html` 独有；HTML 仍包含写死 PID、127.0.0.1 链接与样例数字 | 先核对 IP:8765 真站能从负责人浏览器打开，成功就不重新设计 UI；旧 Dashboard 做薄向导或只保留有链接的归档，真实数据从服务器唯一站点来，静态内容标注 `HISTORICAL_STATIC` |
| 结果目录纳入统一查找 | `our-project/results/` 当前在 .gitignore 整体排除；现有 `runs/` 写真实试验，`docs/operations/` 又保存独立 JSON 索引 | 原始结果/权重可以保持本地不提交，但要为每个真实实验在 `results/{training,agent_trials,benchmark,...}` 下建规范引用与 Run Manifest；Git 仅提交小型脱敏结果摘要，不能把论文重要结论埋在运行目录 |
| 论文图像/汇报副本 | 两份 58 PDF 完全相同，9 个项目卡片相同，汇报大量复制图片和打包构建资源 | 先以 SHA 和 HTML/Markdown/JS 引用关系出依赖图，迁移唯一版后用引用替换；可重生 build 分离输出；无测试证明不删除任何一方 |

## 4. 长时执行的工作阶段（只有主 Agent + 两个子代理）

### 阶段 M0：现场冻结读数与两机完整盘点（优先，当下 CPU-only）

1. 拉取最新 main，在 Mac 和 A6000 均运行**现有只读 `inventory_repo.py`**，补上 Git 忽略的大模型、数据、真实克隆、运行目录、快捷方式、实际解释器和进程消费者，输出大小/目录/归属/是否 Git tracked 等结构化 inventory；只报告路径，不读取凭证正文。
2. 读 `ps`、`nvidia-smi`、训练 pid/args/cwd、Laya F06/ Kev C03 的 Cursor、服务 8000/8765，建立 ACTIVE_HOLD。现行 Laya 和 Kev PID 一旦变化按实时读数，不硬编码旧 PID。
3. 将 CSV 全量 813 项与两机实际清单合并去重，给每项 `KEEP/CANONICAL/MOVE_WITH_SHIM/ACTIVE_HOLD/DEDUP_CANDIDATE/UPSTREAM_LOCAL/RESULT_REFERENCE/LEGACY_ARCHIVE`，记录 consumer(import/CLI/slides/API/dashboard) 与测试命令。
4. 建立 import/entrypoint 调用图（至少静态 `ripgrep` + 关键进程命令 + `python -c import`）；识别同名不同源码，确定唯一真实代码 owner。不要把 GitHub Blob 相同误称所有本地文件都相同。
5. **即时测试基线**：Python import/build/CLI 单测，Router 8000 health、8765 首页+实时 JSON、Laya/Kev 训练 Step 增长。保存 M0 可复现结果，不因个别旧测试已过时而停止有效训练。

### 阶段 M1：实际整理代码（先冷文件，后兼容，活跃训练保留）

6. **第三方方法**：每个 RouteLLM/SR-KNN/未来方法单独 `external/router_methods/<method>/` 和 `code/src/modelrouter/baselines/<method>/` 对应，一份 upstream SHA/LICENSE、1 份自有 adapter、一套完整接口/回归测试；保持服务器官方源码原位置的引用直到自然边界。再将所有已有 Agent/benchmark baseline configs 归 `experiments/configs`。
7. **自有 Laya 代码**：整理 `laya_batch_train`、`run_full_graded_queue`、`checkpoint_retention`、模型加载与固定 Val 入口至 `training/laya`、`training/queue`、`training/checkpoints`；**活跃 PID 的当前文件不 git mv 或覆盖**，自然 Run 边界才正式切换，现有旧路径保留薄 shim。
8. **Kev 代码**：整理 `run_kev_continuous_train, run_kev_homologous_train, kev_candidate_dispatcher, v8_real_finetune` 至 `training/kev`，实验配置和队列 JSON 分开；C03 结束前仅在独立测试工作区修改下一候选入口，不在当前服务器复制覆盖运行模块。
9. **数据脚本**：对 `all_data,tra,cache_time,env_memory,quality_v2,route,shared,views,batch_prep,build_v8_data_extension` 按来源抓取、清洗、质量、视图、Schema/划分拆出；数据许可/样本隔离和真实 label origin 有明确测试，不能把缓存复用“机会”算已发生费用命中。
10. **Agent/Sandbox/Provider**：以 `src/modelrouter` 为最终唯一代码 owner，将 `experiments/agent_pilot` 老入口重定向到新代码或明确仅保留历史 Mock；新版 Harbor 保持官方代码契约，Provider/RouterClients/Registry/Policies 只能有一个真实现，重复文件标注 shim。
11. **Serving 与 Telemetry**：整理 Router 8000 的 model adapters、API Schema、推理延迟与服务开关；Dashboard 8765 保留仅一个权威目录，`scripts/serve_dashboard.py` 与 `fetch_live_status.py` 归 `tools/dashboard,telemetry`，提供旧调用 shim。
12. **测试/CLI**：测试集中到 `code/tests/{unit,integration,contract,smoke}`；根 `prepare_router_data.py` 和 `modelrouter.cli` 最终支持正确的命令/参数，所有常用路径用 `python -m modelrouter ...` 或安装后的 CLI 调用；保留历史调用参数兼容。
13. **研究与汇报**：58 PDF 复制、9 项项目卡片、旧研究摘录、旧版 Markdown/HTML/图片/视频只做 SHA 去重和引用修复，不对未确认唯一的原文删改；组会 `汇报三` 与 `汇报三 第二个版本` 的完整可运行页面/打包播放器和图像引用都必须保持可用。
14. **服务器大实体/结果**：对 `models,raw/cleaned data,runs` 只登记 Asset SHA/相对 URI + 已有实体路径、训练数据视图、Checkpoint/Val 映射，活动权重原地持有，绝不把 50+ GiB 复制成两份；冷小文件实际迁移并记录前后 checksum、shim、import、Pid Step。

**M1 验收**：旧脚本数量逐批减少，所有新代码/归档“已分类”有本地可执行测试，`git grep` 的旧绝对引用逐项标注完成或 ACTIVE_HOLD；PID/Step 前后继续推进，Router 8000 和看板 8765 可用；台账每项有实际操作/验证而不是只有拟议路径。只提交必要无 Secret 的自有小文件。

### 阶段 D1：CPU/本地凭证能实测的研发（在 GPU 满载期间持续推进）

15. **本地 URL+Key 真探针**：使用已有 `experiments/agent_pilot/configs/generator_credentials.json`（或现有环境变量），先真实 `GET /models`（若支持），再已验证模型 ID 的小样本 `chat/completions` 与 `responses` 流式 SSE/非流式、工具调用回合、多轮关联、真实 native effort(按支持菜单)、usage、Provider 异常和 fallback。**不能只跑 Mock**；每次明确模型、endpoint、请求耗时、官方返回 usage 与实际 USD/Quota 报价/失败原因。不在 README/Git/日志输出 Key、带 Authorization header 的命令或完整敏感对话。利用用户现有总体金额上限，轻量短批即可，不每秒重试。
16. **资源竞争测试**：真实 Laya/Kev Router API 分别少量调用验证输出/动作合法性/无 fallback，Kev CPU 延迟至少 P50/P95，统计显著耗时来自 Tokenization、编码、Checkpoint 还是 CPU；只做 CPU 测试，不强行并发上 GPU。
17. **模型池与 Effort**：从已验证 Provider 能力生成 `provider/model/revision/native_effort/legal_actions` 注册表、价格版本快照、模型 Tool/Cache 支持及故障降级，支持不同模型具有不同原生 Effort 菜单；写合法动作过滤单测与用户预算/会话上下文测试。
18. **RQ1 真基线**：FixedStrong、FixedCheap、BestFixedOnDev、RandomEpisodeMix、TaskOnly、Greedy/Sticky、已可复现的 RouteLLM/SR-KNN、Laya、Kev 共用同一 HARNESS/Episode Ledger，不同策略同 Task IDs；任务 Score 未经官方 Verifier 为空/NOT_EVALUATED。
19. **RQ2 模型池科学矩阵**：同 K 不同池成员、不同 K、真实合法 Model×Effort 计数、随机池/价格先验/能力先验与真实开发集选择，避免用 Test 选池。
20. **RQ3 多 Agent 粒度**：在任务可支持时实现相同原任务 G0–G3 拆分/路由边界 F0–F3、真实角色/hand-off/工具、共享预算与可复现实验模板；多 Agent 的成功判定必须同原任务的官方 verifier。
21. **RQ4 三组系统消融**：A 固定/Model-only/Effort-only/分层/Joint；B T/M/H 单双三组+关键 KV/Trace 等特征；C S1/S2/S3、Laya/Kev 数据/监督合法消融。合法约束不允许被 feature mask 去掉；没有实验后结果则图表为空。
22. **RQ5 事前工作负载**：只使用真实任务执行前可观察元数据做预设 strata（Coding/Research/Data 需真的有对应任务/evaluator；大小、已知协作结构、Benchmark 官方标签）；不得事后选成功与失败组，Bootstrap/交互置信区间按独立任务聚类。
23. **实验可复现分析**：实现 `Task Success, Mean Complete Episode USD, Cost per Resolved, input/output/cache/retries/router overhead, P50/P95, confidence interval, cost-success Pareto`，保留负结果；单位、Provider 账单与缓存真实字段必须明示。
24. **Harbor 被 Docker 权限阻挡的离线工作**：无需空转，完成官方 BaseAgent/Job/Task/Trial/Verifier 真实包版本/接口、任务 manifest、8 Canary/24 Dev/57 Sealed、完整成本 Ledger 与失败分类的单元测试；只有合法 Docker/受限容器访问及真实原版 Verifier 才启动首个官评。纯 API 真测试可以跑 Provider/工具协议，不能说是官方 Harbor Task。
25. **实验与部署边界**：不改变原 key/URL、CC Switch 与用户金额上限，仅防止凭证推 Git。新候选大 GPU 训练只在 F06/C03 自然完成、候选矩阵真实准备好后安排；原 Kev 候选队列唯一控制器继续使用。
26. **其他可产出 CPU 工作**：全项目 import/CLI/Schema/数值解析的单元测试、第三方方法版本 SHA 与 LICENSE、Price 计算快照复现、科研结果/运行资产自动索引、时序日志转 Dashboard、组会图表模板由真实数据自填、不影响训练的 CI 安装与静态链接检查。

### 阶段 D2：真的得到官方任务结果后

27. 在 Harbor 官方环境合法授权后，仅先跑 **一个真实 Canary** 作为 E3 任务闭环：Container、官方工具、实际 Provider Usage、真实 Verifier、合法 Task ID/Trial、结果 `resolved` 与成本全链条。任务解不出来允许报告 0 分，但必须原版 Evaluator 给 0。
28. 验收后按 Stage 递增 RQ1 主对照 → RQ4 主要系统消融 → RQ2 池 → RQ3 G → RQ5 先验分层结果；真实结果直接填 [汇报三 V9](../../../汇报/汇报三/ModelRouter论文实验与图表规划.md) Fig.3–8/T3–T11。任何 Mock、Host、Pilot、不同 Val 不混入官方主表。
29. 单独保存完整可复现 Run Manifest、固定随机种子、数据/模型版本、任务/Verifier SHA、API 返回真实 token/cost/error、官方最终分数；敏感原文仅本地，脱敏汇总同步 GitHub。

## 5. 两名子代理的长时间自主分工（不再制造新的看板/调度框架）

- **子代理 A（结构整理 + 数据/训练研究）**：先 M0/M1 的源码归类和相互 import/测试、原始数据/训练/Checker 的路径整理；完成后不停下来，继续 D1(17、19、21、22、23、26) 负责合法 Pool/Effort、RQ2、RQ4、RQ5、统计和数据/监督准备，测试严格 CPU 优先。
- **子代理 B（真实 Agent/Provider/Benchmark 工程）**：先 M0/M1 的 Agent/Harbor/Serving/基线/看板重复代码归类与导入测试；随后做 D1(15、16、18、20、24、26)，在本地真实 URL/Key 下跑小规模 Provider 契约验证、修复 RouteLLM/SR-KNN 与官方 Harbor 的差距、准备 RQ1/RQ3 同任务执行；Docker 阻塞时永远有下一项 CPU 工作。
- **主 Agent（唯一集成/现场保护）**：盘点服务器真实进程和 data/runs 外部文件、监测 F06/C03 和 Kev 调度器、审核每次 git mv/shim 回归、按自然边界切换新入口，汇总测试与完整结果。各子代理要串行或分支提交自己模块，避免同时改同一入口；主 Agent 做集成 merge、失败回滚与关键信息最终确认。
- **长期工作策略**：每完成一个实测功能提交一次 Git，记 `DONE/BLOCKED/RUNNING`；被 Docker/许可证/训练阶段阻塞马上切下一个 CPU 功能；无新增科研价值的空轮询、批量创建空目录、无限生成方案/状态 Markdown 和高频重复 Git 状态提交禁止。**长期推进的是当前 Executive Agent，不是 ChatGPT 在本次会话外声称已经启动了子代理。**

## 6. 结束前必须交付的可数验收

1. Git + Mac + A6000 三份 inventory 与 **813 行起始分类台账**对照，实际物理迁移数、重复去重数、ACTIVE_HOLD、未完成缺口数；至少 **66 个旧可执行文件逐个有唯一代码 owner、测试入口及迁移或保留理由**。
2. `pip install -e`、源码 Wheel build、`modelrouter status/route`、旧 CLI shim、Laya/Kev 现有训练入口、API 8000、8765 页面、GPU/Checkpoint、真实哈希的迁移前后验收矩阵。
3. **真 URL/Key 协议探针**：至少一项真正成功的 SDK/API 文本请求（服务端有能力时）、SSE、Tool roundtrip、native Effort 的实际支持/拒绝矩阵，以及真实 usage/响应延迟；费用有界、真实 Token 记账，不借 Mock 伪造支持。
4. RouteLLM/SR-KNN 的 `UPSTREAM_REPRODUCED`、`FITTED_ON_DEV` 或 `BLOCKED` 逐项标识；Heuristic 与第三方官方模型清楚隔离。
5. 1 套可执行的 Terminal-Bench 官方 Agent/Trial/Verifier 集成入口，Docker 权限仍不通则 `BLOCKED_PERMISSION_REQUIRED`，不报告伪 Trial。
6. RQ1–RQ5 可执行 `manifest+config+statistic+table schema`，测试覆盖强基线、模型池、G0–G3、T/M/H、训练监督、工作负载 strata，不冒充已经得到 Episode 结果。
7. 当前 Laya F06/ Kev C03 的最新 Step/Val/Checkpoint 与原固定 Val 对比，真实指标一页输出；不打断训练；Serving 的实载权重与训练候选不可混。
8. 所有关键 README/论文 V9 RQ1–RQ5/本地服务器文档/展示页面链接正常；`our-project/` 是唯一可追踪入口，Mac 与服务器不再各有一套互不兼容的路径。
9. 在报告中明确列出哪些任务**真正完成、哪些只代码就绪、哪些因 Docker 授权或计算资源而等待**；提供每批 Commit SHA、源文件/新文件映射和可重放测试命令。

**核心验收主张**：先让**一个规范项目**同时服务真实数据、训练、推理、Agent 与 5 个 RQ；再有计划地让模型完成验证与官方 Episode 实验。不要用目录整齐、代码存在或真实付费 API 调用冒充论文科研结果。
