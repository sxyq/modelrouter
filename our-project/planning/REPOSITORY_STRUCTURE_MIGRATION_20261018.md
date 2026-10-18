# ModelRouter · 仓库全盘目录审查与 `our-project/` 主目录迁移实施清单

> 2026-10-18，基于 GitHub `main` 完整递归 Tree 核查（本轮扫描可见 546 个条目、455 个被 Git 跟踪的文件，未截断）。本清单**不是**声称已扫描 Mac 的未跟踪文件、服务器原始数据/权重或已完成物理迁移；这些必须由本地有权限的 Execution Agent 实际盘点。不得因目录迁移打断 A6000 正在运行的 Laya/正式控制器，不要再次创建新项目或重复技术框架。

## 一、负责人最新已确定的边界

1. **将现有仓库内 `our-project/` 作为唯一正式项目主目录**，仓库顶层 `路由/` 暂时仍然是 Git 根。代码、数据处理、训练集构建、模型训练、单 Agent、外部算法实验、Benchmark 及结果、文档有独立、唯一的规范分类。先建立新目录与迁移表，再经验证的分段迁移；**不要直接 `mv router_data` / `mv runs` 破坏服务器运行中的绝对路径、Python import、现有 CLI 与 dashboard 8765**。
2. 本机 CC Switch/Generator Key 用户已有费用总额度限制：**不围绕密钥另开安全审计或强制重配本地凭证**；唯一硬要求是凭证及完整私有调用记录**不得被 Git 跟踪、暂存和 Push**。可以保留当前本机合法配置和 URL，不复制到 GitHub/公开报告。
3. 模型权重全部留在 A6000；Mac 通过受控 Router API 访问 Laya、Kev；Mac 只有 Agent、Benchmark、外部方法和实验记录。当前单 Agent 使用 Harbor 官方 Docker `BaseEnvironment.exec`；正常训练继续。主 Execution Agent + 最多两名子代理，无下级分裂。
4. 本次调整**不得**改变已批准的研究协议、RQ 的具体含义、既有正式 Laya 38 组、任何已运行的验证值或 Benchmark 封存划分。**最新 Q-019（2026-10-18）已正式批准 V9 研究编排**：RQ1 专注完整 Episode 成功率—成本对照，RQ2 模型池，RQ3 任务拆分，**RQ4 正式为系统消融（Model×Native Effort、状态/数据/监督）**，RQ5 工作负载适用边界；原 V8 的“RQ4 多 Agent 角色互补性”已从正式独立研究问题中删除。迁移时按最新 `EXPERIMENT_QA.md` / `RESEARCH_OVERVIEW.md` 与 `汇报/汇报三/ModelRouter论文实验与图表规划.md` V9 同步，历史文档仅保留溯源。

## 二、GitHub 可见的现状与实际问题

截至本轮 Tree：
- 根目录目前有约 455 个跟踪文件；主要顶级目录文件数：`research/` 146、`our-project/` 128、`汇报/` 66、`experiments/` 44、`router_data/` 30、`docs/` 17、`external-projects/` 9、`scripts/` 5；根部还有 `prepare_router_data.py` 和 `papers/`。
- 正式训练/队列放在 `router_data/`；新 Kev 与增补 V8 数据仍混在一起；`experiments/agent_pilot/` 同时放 Agent、Provider、KNN/RouteLLM、定价、CLI 测试和 Ledger；`experiments/harbor/` 有 Mock 与已禁用的不安全宿主执行器；`experiments/router_serving/` 与现有 dashboard 两处各自分离。
- 对外研究分散在 `research/`（含大量 PDF/截图）、`papers/`、`external-projects/`、`our-project/literature/`、`汇报/汇报二/笔记/`；存在相同论文截图在研究素材和报告素材间重复。图片归档首先按 hash + 使用方引用审计，不能直接删除/合并。
- `runs/` 只有极少脱敏汇总在 Git 中；**真实** checkpoint、原始 Trial traces、Benchmark 上游 checkout、训练集和服务日志主要存于 Mac/A6000 未跟踪位置，因此 GitHub Tree 不能回答“整块磁盘总空间和文件实际位置”。必须现场补清单。
- `our-project/planning/CANDIDATE_PROGRESSION_MATRIX.md` 存在陈旧/不一致：F05 e02 列为 67.91%，与此前正式执行验证报告的 63.64% 不符；F03 被标 live/queued 而后续已完训。其 Kev `12/12` 多为 planned/served/smoke，**不是 12 个真正完成训练且固定验证的物理候选**；后续看板须以实体 Manifest/metrics 为数据源，不用手写表格填默认成绩。
- 2026-10-18 上传的两份执行报告：第一份完成价格快照、通用日志和 Mock SSE/Tool 回合；第二份报告 F06 仍训练，Laya/Kev API 正常，官方上游源码下载且 A6000 有 Docker Engine；**未证实官方 Harbor 真容器 Trial + 原版 Verifier 真实执行成功**，Mac 当前报告无 Docker daemon；所谓 16 次 8 策略运行是宿主实验且 0/16 solved。应只做缺失的真实闭环，不再重复已完成的 Mock。

## 三、目标：`our-project/` 是规范主目录，而不是重新 clone 第二个项目

```text
路由/                                  # 现有 Git root，临时保留兼容入口；不是第二项目
├── README.md                         # 指向 our-project/README.md 与运行入口
├── pyproject.toml / requirements...  # 可选兼容入口
├── router_data/, experiments/, scripts/, docs/  # 过渡期只保留薄兼容入口，安全迁移后才收缩
└── our-project/                     # 唯一正式项目主目录
    ├── README.md                    # 首页：架构、目录、任务、训练、运行入口
    ├── code/
    │   ├── pyproject.toml            # editable install; Python 包 src/modelrouter
    │   ├── src/modelrouter/
    │   │   ├── baselines/             # 外部方法与我们适配的基线实验入口
    │   │   │   ├── fixed_random_rule/
    │   │   │   ├── routellm/          # adapter.py, train_or_load.py, run.py, upstream.lock, README
    │   │   │   └── sr_knn/            # adapter.py, fit.py, run.py, upstream.lock, README
    │   │   ├── agent/                 # 单 Agent loop, state, tools, provider bridge
    │   │   ├── sandbox/               # Harbor 官方 BaseEnvironment 适配，不造新 Docker Manager
    │   │   ├── data_pipeline/         # 源数据抓取/清洗/脱敏/质量与 lineage
    │   │   │   ├── sources/
    │   │   │   ├── cleaning/
    │   │   │   └── quality/
    │   │   ├── datasets/              # Train/Val/Test split, Label、训练视图/数据集构建器
    │   │   ├── training/              # laya/, kev/, queue/, checkpoints/, common/
    │   │   ├── serving/               # server API; laya/kev 真模型装载器
    │   │   ├── benchmark/             # Harbor trials, TwinRouterBench, evaluator adapter, matrix
    │   │   ├── providers/             # Responses/Chat/Messages, model registry, pricing, budget
    │   │   ├── telemetry/             # server status collector、model calls、ledger、summary
    │   │   └── common/                # 稳定共享 Schema 和配置
    │   ├── cli/                      # 固定 run_train, run_benchmark, refresh_dashboard 等正式入口
    │   └── tests/                    # 独立 unit, smoke, integration；Mock 不混正式 Eval
    ├── data/
    │   ├── sources/                  # 唯一数据来源/许可台账、源 Manifest
    │   ├── raw/                      # 大原始数据，Mac/服务器本地，Git ignore
    │   ├── interim/                  # 清洗中间结果，Git ignore
    │   ├── processed/                # 统一清洗视图
    │   ├── training_views/           # 独立可追溯训练数据快照
    │   ├── manifests/                # 版本/来源/列定义/哈希；可公开时 commit
    │   └── summaries/                # 脱敏统计、样本数、拆分结果
    ├── external/                     # 所有外部代码/Benchmark/科研材料统一登记
    │   ├── router_methods/
    │   │   ├── routellm/upstream/    # 官方代码镜像/Checkout；adapter 在 code/baselines
    │   │   └── semantic_router/upstream/
    │   ├── benchmarks/
    │   │   ├── harbor/
    │   │   ├── terminal_bench_2_1/
    │   │   ├── twinrouterbench/
    │   │   └── swe_bench/
    │   └── research/
    │       ├── papers/               # PDF及来源ID，原论文不乱删
    │       ├── notes/                # 文献阅读笔记、实验借鉴
    │       ├── project_catalog/      # 原 external-projects 登记
    │       └── figures/              # 研究原图、截图；汇报素材引用不随意删除
    ├── experiments/
    │   ├── configs/                  # RQ1/RQ2/RQ3、候选池、Effort、预算
    │   ├── manifests/                # 科学冻结矩阵、外部版本锁与环境哈希
    │   └── protocols/                # 当前 V8 实验定义；不存原始运行结果
    ├── results/
    │   ├── training/{laya,kev}/      # 新实验 Run IDs、metrics、checkpoint 引用
    │   ├── baselines/{routellm,sr_knn,fixed_rule}/
    │   ├── benchmarks/{terminal_bench_2_1,twinrouterbench,swe_bench}/
    │   ├── agent_trials/             # Trial/episode_id 级 I/O、tool traces、官方 evaluator
    │   └── serving/                  # API 健康/路由时延/错误率
    ├── dashboard/                    # 简洁文字、丰富图表；本机 8765，按需历史
    ├── docs/
    │   ├── planning/                # 项目现有唯一状态/Q&A/研究方案/执行协议
    │   ├── architecture/            # API、模型、Agent、数据流、工程结构
    │   ├── operations/              # Mac/A6000/GOAL/故障恢复与运行手册
    │   └── reports/                 # 组会/论文图表/阶段研究总结
    └── .runtime/                    # 临时下载、后台日志、建镜像缓存、锁，Git ignore
```

**兼容原则**：`our-project` 带连字符，**不能直接当 Python package 名**；使用 `our-project/code/src/modelrouter`、`pip install -e our-project/code` 或可验证的 PYTHONPATH/正式 CLI。外部仓库保留其 license/revision，不重写上游源码；每个基线目录要清楚区分 `upstream`（第三方）与 `adapter`（我们的科研代码）。`our-project/results/` 不复刻旧大目录，使用新 Run 为 canonical，旧 `runs/MR-...` 留原地只存地址/Manifest，除非停机安全迁移且验证全部引用后再更新。

## 四、旧路径 → 新代码职责对照（按现有 Git Tree）

| 已有入口 | 新的唯一代码归属 | 注意事项 |
|---|---|---|
| `prepare_router_data.py`, `router_data/all_data.py`, `tra.py`, `env_memory.py`, `cache_time.py` | `code/src/modelrouter/data_pipeline/sources/` | 根目录保留调用兼容脚本；不重下载数据 |
| `router_data/quality_v2.py`, `audit_v1_v2_stratification.py`, `build_v8_data_extension.py` | `data_pipeline/quality/` / `cleaning/` | `audit` 不混正式训练入口；证据类型独立 |
| `router_data/batch_prep.py`, `views.py`, `shared.py`, `our-project/data/公开数据/训练视图/` | `code/src/modelrouter/datasets/` + `data/training_views/` | 代码/数据分离；测试集冻结 |
| `router_data/laya_batch_train.py`, `run_kev_homologous_train.py` | `training/laya/`, `training/kev/` | 原训练进程未退出前绝不重命名或删除脚本 |
| `router_data/run_full_graded_queue.py`, `checkpoint_retention.py`, `checkpoint_inventory_and_pruner.py` | `training/queue/`, `training/checkpoints/` | 运行中的旧队列与日志输出根绝不改；安全边界后再切 CLI |
| `experiments/router_serving/{server,laya_adapter,kev_adapter,schemas}.py` | `serving/` | 确保 Mac SSH 隧道和 API schema 不变 |
| `experiments/agent_pilot/{agent,state,policy,registry,router_clients}.py` | `agent/`, `baselines/`, `providers/` | 一个 Agent；真实 router/Generator 分离 |
| `experiments/agent_pilot/baselines/{routellm_adapter,sr_knn_adapter}.py` | `baselines/routellm/`, `baselines/sr_knn/` | 源代码/实际训练或拟合数据/适配器分离；不假称官方复现 |
| `experiments/harbor/{environment,task_loader,twinrouterbench,canary_verifier}.py` | `sandbox/`, `benchmark/` | 保留 Host Shell fail-closed；评测只能官方 Harbor 容器 |
| `experiments/agent_pilot/{provider,multi_model_logger,ledger,token_budget}.py` | `providers/`, `telemetry/` | 多协议/真实模型 ID/Token预算/费用标签 |
| `experiments/agent_pilot/pricing/` | `providers/pricing/` + 版本化价格 Manifest | OpenRouter snapshot 不随新 Run 自动覆盖旧 Run |
| `experiments/agent_pilot/{runner,run_real_benchmark_matrix,run_stress_benchmark,run_canary_real_evaluation}.py` | `benchmark/`, `cli/`, `tests/` | 真 Harbor 调度 vs Mock 压测完全分离 |
| `scripts/{fetch_live_status,generate_cds_dashboard}.py`, `docs/training-dashboard/` | `telemetry/`, `dashboard/` | 保留 8765 旧 URL 兼容层/可用采集器 |
| `scripts/oneshot_f05_to_f03_handover.py`, `router_data/server_watchdog.sh` | `docs/operations/legacy/` 或 `code/cli/legacy/` | 先查当前进程/引用，旧一次性脚本不要重启 |
| `external-projects/`, `research/`, `papers/`, `our-project/literature/` | `external/research/` | 用 Git MV 保留来源，先去重清单后改所有文档相对链接 |
| 根 `汇报/`, `docs/MODEL_ROUTER_...md`, `our-project/汇报/` | `docs/reports/` | 保留现有图表引用与 PDF/图片资源链接，先迁未引用文件 |

## 五、本地/服务器真实磁盘检查（执行 Agent 必做，不得凭 Git Tree 伪称“全盘完成”）

在 Mac 实际 `路由/` 工作目录及 A6000 项目根分别执行一次**只读** Inventory（脚本放 `our-project/code/cli/inventory_repo.py`，不要随手放桌面或仓库根），包括：

1. `git status --short`, `git ls-files`, `git ls-files --others --exclude-standard`, 当前 Git HEAD/分支；根目录一级二级 tree、目录体积 `du`、文件数/扩展名、大小文件前若干、空目录/临时脚本、权限与符号链接、是否有嵌套 Git checkout。没有权限读取的目录明确 `UNREADABLE`，不列出个人秘密内容。
2. 解析 Python import、Shell 命令、`subprocess.Popen`、`sys.path`、`nohup`/service、dashboard/static root、SSH/tunnel、run manifests、训练队列运行命令中的路径；建立 `path → consumers → process_active → destination → compatibility_action` 显式迁移表。**不要盲目全局 `sed` 替换绝对路径或 import 名称**。
3. 将结果分别保存 `our-project/docs/operations/inventory_mac_{timestamp}.json`、`inventory_a6000_{timestamp}.json`（完整可含私有路径的文件只放本地受保护运行目录；Git 仅脱敏汇总）；扫描时不要输出/提交 API Key、原始 prompt、用户文件内容。
4. 验证 Mac 的外部上游源码 checkout 的 Git SHA、许可证和占用空间；Server 的大数据/模型/Run 原地资产表；记录引用是否真实存在，不要为了“目录整齐”复制几 TB。
5. **复核两份最新执行报告**：第一份定价/Responses 是否仅 Mock；第二份 Mac 没有 Docker daemon、A6000 Docker 当前用户是否可创建实际 Sandbox；`12/12` 对应的 `checkpoint+run.json+fixed val+source SHA` 数；报告的 SSH tunnel/API 不代表真实官方 Eval。报告差异只修明确错误，不再无限扩展审计。

## 六、无中断分阶段物理迁移步骤

**M0 Inventory only（可在训练运行中进行）**：先输出完整 path manifest 和风险清单；记录基线状态，检查 live PID/open-file/queue，既有训练保持 100% 不受影响。

**M1 新骨架 + 包入口（不中断）**：建立 `our-project/code/src/modelrouter`、`pyproject.toml`、README、数据/外部/实验/结果/文档职责；已有旧实现暂不移动，先可运行地 import 新 package。新功能从此直接写入唯一新位置。

**M2 先迁本机非训练代码**：按功能 `git mv` 用户自有 `experiments/agent_pilot`、`experiments/harbor`、外部算法适配与本机实验入口；第三方 checkout 只迁索引或可再 clone 的目录；保留必要的旧 CLI shim/wrapper，仅在运行/官方 eval通过后删除旧重复实现。每小批做 import/Mock/真实 Harbor 小验证，若失败 revert 该批。

**M3 迁统一文献和 Dashboard**：先建立 `external/research` 唯一索引、内容哈希与交叉引用；只对非运行中研究文本 `git mv`，修 Markdown/PDF/图片引用，少量历史别名保留链接；Dashboard 保留 `http://127.0.0.1:8765` 的旧命令/目录有效，双模型实际曲线与策略结果不能回退。

**M4 训练代码在安全 Run 边界迁移**：在服务器正式 F-series 运行中不动文件/队列；先用同版本代码复制/包安装验证参数、resume、Data SHA、Validation 一致性及路径；**仅在自然 Run 边界并已有真实恢复点、旧控制器不再持有相关模块时**切换新 CLI。失败立即回旧入口，原 PID 训练不得因迁移杀掉；原历史 Run 保持原位置，新的训练写入 canonical `our-project/results/`。

**M5 数据目录与成果目录归类**：对实际存在的大原始数据和模型实体优先**保留物理位置 + 注册 immutable manifest / 挂载引用**；不要跨文件系统大规模复制、重压缩、删除。新 Train Views 与结果从新目录开始；如果必须移动，用校验和/磁盘余量/唯一进程持有关系确认，再做原子替换。Git 只跟踪 schemas/configs/index/脱敏统计，不直接跟踪完整输出与私有 I/O。

**M6 完整回归与文档收尾**：验证 Laya 正式队列连续、Kev 真训练/恢复、双 Router API、Responses/Tool、本机 Harbor 官方 Trial、外部基线 1–2 题、OpenRouter 价表、真实 Episode 账本、看板 8765；检查 `rg` 的旧路径引用，保留少量必需兼容入口，去掉确认无消费者的失效脚本。更新根 README、`our-project/README.md`、所有权威六文档、Mac 和服务器操作手册、实验/目录索引，按阶段小 Commit/Push 并重读 GitHub。最终报告“已物理迁移 / 兼容保留 / 未迁（运行中）”，不得把只有方案的文件标为已迁。

## 七、完成标准与进度控制

- `our-project/code/` 内所有**自有** Python 代码按 `baselines,agent,data_pipeline,datasets,training,serving,benchmark,providers,telemetry` 分类，可复现 import、CLI 与测试。每一种外部方法明确上游源码/版本/适配器/合法训练数据与运行指引。
- `our-project/external/` 汇聚所有外部方法、Benchmark checkout、研究笔记/论文/索引；`our-project/data/` 将数据源码、原始实体、清洗数据、训练集版本和许可证分清；`our-project/results/` 按训练模型、Benchmark、策略、任务、种子分类并保留原始结果与官方评价引用。
- `our-project/docs/` 是唯一当前文档入口；`our-project/dashboard/` 是正式可视化源，但保留旧 8765 入口与真实刷新。
- 保持两个长期训练任务科学推进：Laya 正式历史队列不破坏；Kev 实际 GPU/LoRA/Head 与 Val、Checkpoint 可核；本次不以目录重构为由启动新的大数据全量训练或重复下载。
- 不删除本机 CC Switch 凭证，也不要求负责人重新配置 Key；只做 Git 暂存前的**路径拦截**：`generator_credentials.json` 等私有配置不能 `git add` / Push，必要时 `.gitignore`（仅影响 Git，不改本地文件）；基于 Git 历史检查只关注**本轮新增泄露**，不另开无关密钥专项工程。
- **工程负责人：主 Agent + 两名子代理**。子 A 扫本机代码/Agent/Benchmark & `our-project/code/`；子 B 外部论文/Benchmark 索引、文档/结果/看板 & 外部目录；主 Agent 亲自管理 A6000 训练与服务的兼容迁移、最终 Git 提交。所有工程迁移可拆小阶段，但每段具备实测和版本记录，无人等待、无新 Watcher/CI/PR/重复框架。

**本文件是目录重构的实施规范，非已经完成 Mac/A6000 物理迁移的证明。**
