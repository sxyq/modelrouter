# ModelRouter · 全仓代码分类、重复资产与研发缺口审查（2026-10-19）

> GitHub main 2026-10-19 截图为 `381dcb2` 后增补审计清单 `e4deeda`。对象是 **完整非截断 Git Tree（813 个 blob）+ 116 个受跟踪 Python/Shell/pyproject 路径 + 关键运行入口实际源码**；不是 SSH 对 Mac/A6000 未跟踪/被忽略文件的全面物理巡检，也不是声称已逐行验证 813 文件。执行代理必须再盘点两台机器的 Git-untracked/ignored、软链接、运行命令、引用消费者和共享虚拟环境。可机器读取清单：[code_classification_inventory_20261019.csv](code_classification_inventory_20261019.csv)。

## 1. 明确结论：功能分类已建立，但还没有完成

- 全仓受跟踪文件 **813**；`our-project/code/` **41** 个文件（含 **38** 个受跟踪 Python/pyproject），规范包 `code/src/modelrouter/` 已有 `agent/baselines/benchmark/data_pipeline/providers/sandbox/serving/telemetry/training`。它是**已建雏形**而非完全迁移。
- `router_data/` **~28 个传统 Python 模块与脚本**仍是根部正式数据流水线/训练控制器的真实执行依赖；`prepare_router_data.py` 仍在根目录。`training/` 规范包仅有 Kev Dispatcher 和 V8 小实验相关文件；**Laya 正式训练、Kev 原训练、Checkpoint 选择、全覆盖队列、主要 data_pipeline、dataset/view 代码尚未物理迁入规范包**。
- `experiments/agent_pilot`、`experiments/harbor`、`experiments/router_serving` 大部分旧核心入口已降级为到 `modelrouter` 的薄 Shim，**但** `experiments/agent_pilot/runner.py`、`run_real_benchmark_matrix.py`、`run_canary_real_evaluation.py`、`run_stress_benchmark.py`、`test_responses_stream_tool.py` 仍独立存在；应按 Mock/host/真实/测试属性分离归类，不可直接搬进“官方真实 Benchmark”。
- `scripts/` 仍有站点 `serve_dashboard.py`、采集 `fetch_live_status.py`、多个旧版 Dashboard Builder、截图脚本、实验比较脚本与**有 SIGKILL 历史进程逻辑的** `oneshot_f05_to_f03_handover.py`。后者是永久历史归档对象，不能在新环境再次执行。
- `our-project/experiments/` 与 `our-project/results/` 当前**没有 Git-tracked 文件**：这是 .gitignore/磁盘大结果不入 Git 的归档约定，不代表服务器不存在真实实验。需要在项目规范路径维护小型可提交的 `configs/manifests/protocols` 及脱敏成绩摘要，同时大日志/权重继续不入 Git。
- `our-project/external/` 目前主要含 `research/`，真正 `external/router_methods` 的上游源码在服务器/Mac 根级 Git-ignored `external/`。需要**按方法建立同级说明、上游引用、适配器和运行入口**，不能将第三方源码无脑复制进本项目 Python 包或不记 Licence/Commit。

### 真实文件重复证据（Git blob SHA 完全相同，不是根据文件名猜测）

| 原目录 | 规范目录/镜像 | SHA 完全相同数 | 重复 Git blob 总体积 | 动作 |
|---|---|---:|---:|---|
| `research/task-level-cost-routing/`（139 文件） | `our-project/external/research/`（157 文件） | **138** | **194,415,591 B** | 逐个核引用，优先保留规范位置；历史路径 README/相对链接兼容后逐步移除重复 Git-tracked 副本，不能丢唯一那 1 个原文件；不重写 Git 历史 |
| `docs/training-dashboard/`（16 文件） | `our-project/dashboard/`（15 文件） | **15** | **7,230,298 B** | 服务器规范看板 `our-project/dashboard/` 唯一源，旧 docs 兼容只读入口按静态站点要求保留最小文件/重定向；不得造成 Mac/服务器采集写两份冲突数据 |
| `汇报/汇报三` 与 `汇报/汇报三 第二个版本` | 多份源/生成 `dist` 和图 | 交集至少 11 个 SHA 文件 | 需逐版核查 | 用户需要的现有汇报播放功能先保留；源码/构建产物/发行快照按版本归档，不拆正在使用的播放器 |

**重大提示**：只是从 HEAD 去掉重复文件，并不自动从 Git 历史移除大 blob；此次不做破坏性 Git history rewrite，也不在服务器对大权重做复制/去重清理。

## 2. 对用户原始要求的分类目标与落地路径（先移动冷文件）

```text
路由/our-project/                          # 唯一项目主目录；Git root仍在父目录
├── code/
│   ├── pyproject.toml  README.md
│   ├── src/modelrouter/
│   │   ├── baselines/                      # 竞品方法，每个方法独立
│   │   │   ├── routellm/{adapter,runner,config,tests,UPSTREAM.md}
│   │   │   ├── sr_knn/{adapter,runner,config,tests,UPSTREAM.md}
│   │   │   └── fixed_random_rule/
│   │   ├── agent/                          # AgentState、执行引擎、角色/handoff
│   │   ├── sandbox/                        # 真Harbor原生隔离环境适配
│   │   ├── benchmark/                      # 真实Harness、Episode、计分、任务
│   │   ├── data_pipeline/
│   │   │   ├── sources/                    # 公开源+自有源解析
│   │   │   ├── cleaning/quality/           # 消洗、许可/标签、去重审计
│   │   │   └── views/                      # 联合S1/S2/S3和V8视图
│   │   ├── datasets/                       # manifest/split/format/loader
│   │   ├── training/
│   │   │   ├── laya/                       # F01–F06/后续队列/实际训练
│   │   │   ├── kev/                        # C03–C11/正式LoRA与PointerHead
│   │   │   └── common/                     # 断点恢复/训练指标/Retention
│   │   ├── serving/                        # 真实模型路由API
│   │   ├── providers/                      # LocalURL+Key，Chat/Responses/原生Effort/定价
│   │   └── telemetry/                      # 真实GPU、Cursor、账本、Dashboard数据
│   ├── cli/  tools/  examples/
│   └── tests/{unit,integration,contracts,smoke,golden}/
├── data/{sources,raw,cleaned,training_views,manifests,configs}
├── external/
│   ├── router_methods/{routellm,sr_knn,laya,kev,...}/ # 每个方法: upstream(引用/实体) + adapter指向 + 运行协议 + 版本许可
│   ├── benchmarks/{harbor,terminal_bench,swe_bench,twinrouterbench}/
│   └── research/{papers,notes,figures,project_catalog}/
├── experiments/{rq1,rq2,rq3,rq4,rq5,configs,protocols,manifests}
├── results/{training/{laya,kev},baselines,benchmark,agent_trials,serving}
├── dashboard/                          # 8765 真站点，不移动正在运行的进程
├── docs/{planning,architecture,operations,reports}
└── .runtime/
```

以上层次中的每个目录不必为了目录图而建空目录。**以真实文件/可运行代码为主**；旧系统入口应当只有兼容薄包装（Shim），不能有“两个可编辑的业务真实实现”。`our-project` 含连字符，不得当 Python import 包名，实际可导入包是 `code/src/modelrouter`。

**用户特殊要求**：各个竞品方法的“上游代码 + 我们的适配/运行代码”在同一方法目录的**逻辑单元**中可查找；如上游不宜 Git 提交或体积大，使用固定 SHA 的源码资产链接/Manifest，而不是将上游包复制进自有代码后冒充原创。最简单的 Agent 实验、数据清洗、中转/调用数据处理、训练数据制备、模型训练、结果、外部论文/笔记，都要能通过上面的分类直接找到。

## 3. 源码读查揭示的实际缺陷（修复后自动回归）

1. **正式打包不完整**：`our-project/code/pyproject.toml` 设置 `readme="README.md"`，而当前 Git Tree 没有 `our-project/code/README.md`；只声明 `fastapi/uvicorn/requests/pydantic`，训练/Harbor/测试等依赖尚未按可选组件管理。独立新环境里先做 `pip install -e ...` 和 `import modelrouter` 验收，再认为正式包可用。
2. **CLI 与服务 Schema 脱节**：`modelrouter.cli.cmd_route` 发送 `model_requested`，而 `modelrouter.serving.schemas.RouteRequest` 接收 `router_family`；`--model kev` 可能仍按默认 Laya 路由。修正后用真实 Port 8000 响应的 `router_family` / `checkpoint_id` 验证，不动现行 Serving 进程。
3. **大量冷代码还没有按责任迁入**：现行 `router_data/laya_batch_train.py`、`run_full_graded_queue.py` 直接引用旧模块和 `router_data/laya_batch_train.py` 路径；**F06 正在运行期间不得移动或替换**。只在进程自然结束与恢复验证后用单一 `modelrouter.training.laya` 规范源 + 旧 Shim；`router_data/run_kev...` 同理。
4. **候选测试仅测影子参数**：`our-project/code/tests/training/test_kev_candidates_dry_run.py` 多处构造自定义 `cand={...}`/命令字符串，却不调用真实 Dispatcher。`C04` 的 LR 下降 `--lr` 不等于 Cosine schedule；C05 必须测真实输入状态屏蔽，C07 必须测实体 LoRA 形状，C09 必须测真实 V8 Loader 和固定验证。
5. **真正 Benchmark 核心未集中**：`experiments/agent_pilot/runner.py` 默认 `MockGeneratorProvider` 且调用 `MockSandboxEnvironment()`；`run_real_benchmark_matrix.py` 旧宿主路径也仍存在。需要有同名风险消除、Mock 专用命名、正式 Harbor 单一入口和绝对真实 Episode 验收。当前 `benchmark/run_official_harbor_trial.py` 即使 Docker 可用仍返回 `PENDING_OFFICIAL_VERIFIER`，没有真正启动官方任务 Job/Verifier，不得根据脚本名字判定 RQ1 已具备官方数据。
6. **竞品仍是近似启发式**：当前 `modelrouter.baselines.routellm_adapter` 的 logistic 特征权重为代码固定数组，`sr_knn_adapter` 的示例参考向量是手工常量；不能命名正式可复现上游 `official` 算法。每方法下应建立上游版本、配置、加载/拟合、运行、测试、实际结果报告。
7. **训练真实性**：F06 Epoch1 `S1=67.38%`，低于历史 `P0_B03=68.63%`；最新现场 F06 E2 Step 63804/92280，Kev C03 Step 12050/16857。两条持续运转无需打断；看板数 `data.js` 历史硬编码可能与 `live_status.json` 冲突，需只对当前指标使用实时权威数据。Kev 旧 87.26% 与 V8 Pointer Head Pilot 83.33% 非同固定 Val；没有 C03 终验前不得宣布改善。
8. **Smoke vs 真实**：`test_harbor_contract.py` 测试进口可能通过 fallback `BaseAgent` Stub 而没有真正安装的 Harbor；浏览器验证 `verify_dashboard_browser.py` 最末无论是否检测到 console failed requests 都打印“100% Succeeded”。对真正失败设非零退出码，并将无需官方后端的 mock 单测与必须在 A6000/Mac 权限下完成的真实集成测试分开。
9. **脚本生命周期**：`scripts/oneshot_f05_to_f03_handover.py` 含固定历史 PID 与 SIGKILL；必须标 **DO_NOT_RUN_LEGACY**。旧 `server_watchdog.sh`、多个 Dashboard Builder 要先查谁在运行/引用，再保留当前唯一 Collector + 只读服务器的规范入口。
10. **配置/数据目录**：`our-project/data/configs` 等已具备，但 `experiments/rq1..rq5` 的正式任务 manifest、`results` 的用户可查公开索引尚无已跟踪权威产物。自有 CSV/外部论文可入 Git 的小型报告与私有重原始数据须分层；已经提交的 `our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv` 约 34.7MB，应标明作用与授权/归属，不能简单挪进 Git-ignored 路径而无可复现替代索引。

## 4. 实际迁移操作原则与交付

1. 执行代理主 Agent 先在 Mac 和 A6000 只读盘点所有磁盘实存文件（tracked/untracked/ignored）、symlink、`cwd`、`sys.path`、`ps` 命令行/打开文件、当前 PID/Queue/Cursor、`df/du`；与这份 Git CSV diff 形成 **server + Mac File Mapping**。GitHub 没有存放的权重、数据和上游仓库**必须扫描本地本物理环境**，不能臆断不存在。
2. 主 Agent 在**健康的 F06/C03 自然结束前**不重启训练、不迁其真实执行文件、`models/data/runs/external` 运行实体、不动共有 `.venv`；正在使用/被新任务热加载的模块不搬。主 Agent 负责验收与统一 Git。
3. 子 A 先完成冷数据清洗/Views/Datasets/训练辅助模块的 `git mv`、`__init__` 和小 Shim；更新 import、pytest、CLI、文件路径与 Manifest。子 B 同时处理 Agent、Baseline、Harbor、Provider、Benchmark 冷脚本、兼容旧 runner 的停用告警与真实测试。禁止两个子代理同时编辑同一文件或把同一脚本当两个规范入口。
4. **外部重复文件**：先批量比较 Git SHA、引用、许可证、用户汇报播放器需求；仅对真正重复的文献静态镜像和不在用的副本去重。**汇报第三版已有两个在用演示版本，不因为“整理”贸然改其路径或删除已有可播放产品。**
5. 每一批迁移设最小运行验收：`python -m compileall`/单元测试，`pip install -e`、CLI、数据加载行数/哈希、旧入口导入一致性、服务器 8000/8765 健康、双训练游标持续推进、未破坏自然 Checkpoint/队列、`git status` 清晰。每阶段 commit 明确变更和测试结果，不做一口气全盘 `mv`。
6. 将所有 `docs/planning`、数据来源台账、架构图、服务器资产和运行手册、GitHub 主 README、当前真实 Dashboard 引用统一到规范路径。不改写历史 RQ 决策；**Q-019 正式 RQ4=系统消融，RQ5=任务适用边界**，旧角色互补性 RQ4 已废止。
7. 用户提供本地 Generator URL + Key，允许**小规模真实 API 烟测**：两模型每种真实支持的接口/原生 Effort、Streaming/tool-call、错误返回、费用/Token/latency；采用实际 Provider 成功响应记录脱敏证据，控制账本/避免并发重复计费；URL、Key 保留在本地，不入 Git。官方 Harbor Docker 授权未解决时真实 API 烟测 **不等于** Terminal-Bench 真实评分；不为模拟 Benchmark 浪费 Token。
8. 统计与科研开发必须优先支持 V9 五个 RQ：RQ1 相同 Harness Episode Success–USD；RQ2 真实模型池K；RQ3 G0-G3；RQ4 联合Model×Effort、T/M/H、S1/S2/S3；RQ5 预注册工作负载分层及配对置信区间。**CPU 开发/测试并行，真实 GPU 和外部收费实验按现有运行/预算门禁分别推进**。
9. 里程碑分为 `STRUCTURE_AUDITED`、`COLD_MIGRATED`、`PACKAGE_TESTED`、`REAL_PROVIDER_SMOKE_VERIFIED`、`RQ_MATRIX_PREPARED`、`HARBOR_OFFICIAL_CANARY`、`RQ_RESULTS_MEASURED`；阶段未完成不能合并称 `ALL_DONE`。

**本次已完成的审查资产**：代码分类 CSV（116 路径）+ 本文。**尚未执行** Mac/A6000 物理文件迁移、官方 Sandbox、模型最终 Val 或线上试跑；由有 SSH/Mac 权限的 Execution Agent 按文档实际完成。
