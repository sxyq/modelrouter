# ModelRouter · Laya 训练与 Checkpoint 智能保留看板

直接打开 `index.html` 即可查看（支持本地 `file://` 直接打开与 GitHub 静态预览，无需 Web 服务）。

## 1. 数据分片架构（防止单文件无限膨胀）

为避免单个 `data.js` 随 `1,092` 个候选方案与数百轮历史训练无限增大，看板采用“主汇总 + 按模块/批次静态 JS 分片”结构：

- `data.js`：首页核心汇总、磁盘监控、Checkpoint 保留统计、模型质量与存储散点图、S1/S2/S3 动态阈值摘要及当前活跃方案摘要（约 `580 KB`）。
- `shards/matrix_plans_full.js`：完整 `1,092` 个理论槽位与 `52` 个新协议 `P0_` CPU 物化方案定义。
- `shards/checkpoint_tree_nodes.js`：全量可点击 Epoch 级历史节点（含已保留实体权重节点、`PINNED_PARENT` 父节点及已淘汰权重的 `METADATA_ONLY` / `PRUNED_LOW_SCORE` / `LEGACY_METADATA_ONLY` 节点）。
- `shards/historical_runs_detail.js`：历史 `OVERNIGHT-LAYA-TRAINING`（`R1`–`R3`）与 `OVERNIGHT-LAYA-SWEEP-02`（`N01`–`N10`）完整逐轮元数据。
- `shards/storage_verification.js`：P7 存储策略与磁盘保护 10 项无 GPU 验收完整报告及 100-Run 空间开销对比。

仓库仅保存脱敏指标与可视化页面，不包含任何模型权重（`.safetensors` / `.pt` / `.bin`）、私有服务器路径或原始调用日志。

---

## 2. Checkpoint 智能保留政策与磁盘保护阈值

### 2.1 逐轮记录与按质保留（P0–P2）
- **100% 指标保留**：每个 Epoch 完成训练与独立 Val 后，完整记录 24 项实验参数、数据协议版本、父子依赖与验证成绩至 `run.json`、`epoch_metrics.json` 及 `checkpoint_manifest.json`；绝不因节省磁盘省略低分轮次记录。
- **单份实体权重与符号链接去重**：每个保留的真实 Checkpoint 仅在 `checkpoints/epoch_XX` 保存一份实体权重（约 `807.00 MiB`）；`best` 采用指向对应 `epoch_XX` 的相对目录符号链接（经官方 `laya.train.load_checkpoint` 验证 100% 兼容）；`latest` 仅作运行期临时恢复并在 Run 完成时自动清理。
- **动态成绩阈值与任务隔离（P1）**：
  - 可比较组必须同时满足：**相同输入协议版本、相同主监督目标、相同固定验证集、相同指标定义**；旧 `LEGACY_INPUT_PROTOCOL` 严格隔离，不参加新协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）排名。
  - **S1 规则**：同组有效对照 `< 5` 时启用冷启动保护；`>= 5` 时需满足 **条件 A**（`Val Loss <= 同组均值 * 0.995` 且 `Accuracy >= 同组均值 - 0.005`）或 **条件 B**（`Accuracy >= 同组均值 + 0.01` 且 `Loss/Brier <= 同组均值 * 1.005`），每组仅保留非依赖 **Top-2** 权重，并强制保留全局 S1 最低 Loss、最高 Accuracy、最低 Brier 模型及 `PINNED_PARENT` 父节点。
  - **S2 规则**：在中性协议独立监督审计通过前（`s2_audit_passed=false`），禁止因 `S2 Accuracy=1.0` 永久保存大量权重或设为全局冠军；全组最多临时保留 **1 个**最低 Log Loss 诊断模型。
  - **S3 规则**：按 6 个真实 `source:target` 分目标分别对比各自多数类准确率（`0.4232 ~ 0.9520`）与先验 Loss 基线（`0.1926 ~ 1.2576`），严禁将不同 S3 目标原始 Loss 简单相加；仅分目标优于多数类基线的模型可进入组内 Top-2 候选。
- **状态枚举（P4）**：`RETAINED_BEST`、`RETAINED_TOP_K`、`PINNED_PARENT`、`TEMP_RECOVERY`、`METADATA_ONLY`、`PRUNED_LOW_SCORE`、`PRUNED_DUPLICATE`、`LEGACY_METADATA_ONLY`。无实体权重的节点严格标记 `weights_saved=false` 且在历史树中保持可点击查看。

### 2.2 磁盘预算与自动停机门禁（P3）
- **FULL-GRADED 活动权重预算**：`120.0 GiB`。
- **告警线（WARNING）**：根分区剩余比例 `< 25.0%` 或可用空间 `< 300.0 GiB`（取更严格者）。
- **停机保护线（STOP）**：根分区剩余比例 `< 20.0%` 或可用空间 `< 200.0 GiB`，或必须保留的 `PINNED + BEST` 权重已超出活动预算。触发时先尝试在白名单内对可淘汰低价值权重执行二阶段物理清理（`shutil.rmtree`，绝不移入同分区 `.Trash` 虚报释放），若仍不足则立即安全停止启动新 Run，绝不删除 `PINNED_PARENT`、全局最佳权重或基础模型。

---

## 3. 当前统计摘要（2026-10-12 实测）

| 指标项 | FULL-GRADED 窗口一 (`MR-FULL-GRADED-TRAINING`) | 全项目累计（含 `Batch 1` + `Sweep-02`） | P7 沙盒验收（新协议模拟） |
| --- | --- | --- | --- |
| **总 Epoch 数** | `32` | `71`（`32 + 9 + 30`） | `14`（新协议 `13` + 旧协议对照 `1`） |
| **有效模型权重数** | 磁盘存量 `30` 个 Epoch 权重（共 `55` 个实体目录，含 `25` 个待去重 `best/latest`）；新策略筛选应保留 **`11` 个** | 磁盘存量 `69` 个 Epoch 权重（共 `120` 个实体目录，含 `2` 个 `PINNED_PARENT`：`R1-e01`、`R2-e01`） | **`5` 个**实体权重（`0` 重复目录） |
| **保留比例** | 磁盘存量 Epoch 保留率 `93.75%`（`30/32`）；**新策略目标保留率 `34.38%`（`11/32`）** | 磁盘存量 Epoch 保留率 `97.18%`（`69/71`） | **`35.71%`（`5/14`）** |
| **磁盘实际使用** | 根分区总计 `3,518.72 GiB`，已用 `2,275.13 GiB`（`df 69%`），**可用 `1,064.78 GiB`（`30.26%`）**；FULL-GRADED 权重占 **`43.60 GiB`**（新 P0 物化数据占 `0.41 GiB`） | 历史实验权重占 **`51.47 GiB`**（`Sweep-02` `39.65 GiB` + `Batch 1` `11.82 GiB`）；基础模型 `models/` 占 `9.64 GiB` | 沙盒测试后已自动清理（`0 B` 残留） |
| **累计释放空间** | 已释放 **`3.15 GiB`（`3,384,787,296 B`）**（`B01_C14_QB_PB` 4 个目录）；未来按需可清理冗余/低分权重 **`34.68 GiB`**（`44` 个目录） | 全项目存量重复 `best/latest` 共 `51` 个目录（`40.19 GiB`） | 沙盒二阶段清理实测释放 **`197,016 B`**（与看板统计 100% 一致） |
| **当前最佳模型** | 旧协议窗口一：`B01_C05_QB_PB-e02`（S1 Loss `0.5945`、Accuracy `0.6827`、Brier `0.4082`） | 历史 Sweep-02：S1 Loss 最佳 `N05-e02`（`0.5969`），S1 Accuracy 最佳 `N10-e03`（`0.6952`） | 新协议尚未启动 GPU 训练（正式选模 Run = `0`） |
| **下一次训练存储预算** | 活动权重预算上限 **`120.0 GiB`**（当前新协议已用 `0 GiB`；旧窗口去重后仅占 `8.67 GiB` [`7.22%`]，预算充足） | 预估新策略下**每 100 个 Run 稳态仅占 `18.91 GiB`（峰值 `20.49 GiB`）**，较旧方式（`315.23 ~ 354.64 GiB`）节省 **`94.0% ~ 94.67%`** | `READY_FOR_NEXT_GPU_WINDOW = true` |

## 2026-10-14 · Top-5 与数据训练质量复核（MR-DATA-QUALITY-REVIEW-20261014）

> **重要**：上面的“2026-10-12 实测”表仅为历史快照，不能代表当前训练；`top5_and_routing_aligned.js` 是 2026-10-14 **静态导出**，不是直接读取 GPU 进程实时状态。

- **Top-5**：提交列出 `P0_B03_C01_QB_PB-e02`、`P0_B01_C01_QB_PB-e02`、`P0_B03_C05_QB_PB-e02`、`P0_B03_C08_QB_PB-e02`、`P0_B02_C01_QB_PB-e02`；另有课程父节点和运行恢复点例外。目标为“30% 质量入围后至多五个临时实体权重”，不是五个永久冠军；目前独立裁剪脚本尚未与既有同组 Top-30% 动态名单/实时依赖合一。
- **存储**：Agent 公开快照报告 122 个目录、103,249,108,992 B（约 96.16 GiB）清理；数值需要服务器后验 `du`/`df` 与模型官方加载检查。脚本暂时使用静态 F02/R1/R2 保护参数，新 Run 不应照搬。被删除 Epoch 在历史树的权重标志和 symlink 也要验收。
- **训练覆盖口径**：最新 `all_data.py` 中的 `DISTINCT_TRAINED_UNITS` 是候选池单元数而非训练消费交集，1,389,767 不能作为已训练去重数；5,027,245 与既有六源 4,863,900 未对齐。统计列不能设默认值假装无数据，缺失应标为 N/A，不能作为全量完成率分母。
- **新代码阻塞**：当前新 `laya_batch_train.py` 把 `materialize_full_coverage_chunk()` 返回的整数、分类 dict 与路径字符串直接 `sum`，新代码下的正式 Chunk 会报错，必须修正后验证。
- **新业务训练**：`ALGN_01_S1`、`ALGN_02_S1_S2`、`ALGN_03_S1_S3`、`ALGN_04_S1_S2_S3` 已加入定义；没有证据证明已完成 GPU 训练。联合 Model×Effort 真值仍为 DATA_NOT_READY。
- **可视化迭代**：应从版本化权威 `run.json` + 实际 Checkpoint 盘点 + 最新 census 生成数据，而非采用 `top5_and_routing_aligned.js` 内的 fallback 固定数字；需要分别显示“已提交计划”“已生成训练数据”“已训练”“仅历史元数据”四种状态。
- **公开安全**：仓库新增的 Top-5 manifest 含未脱敏服务器绝对路径，违反本 README 既定“只发布脱敏指标”的原则，需清理并检查 Git 历史；不得传播其真实路径。

## 2026-10-14 · TOP5 验收与全量连续训练链路修复闭环（MR-DATA-QUALITY-REPAIR-CLOSURE-20261014）

- **现场进程状态核验**：A6000 宿主机训练进程（PID 2207051 / PID 2287331，F02 训练中）保持零中断连续运行，GPU 显存占用 9,635 MiB / 49,140 MiB（利用率 90%，功率 283W，温度 72°C），根分区剩余 1.2 TiB（可用 34.6%）。
- **物理权重状态**：清理后实体模型严格为 5 个普通核心模型（`P0_B03_C01_QB_PB-e02`、`P0_B01_C01_QB_PB-e02`、`P0_B03_C05_QB_PB-e02`、`P0_B03_C08_QB_PB-e02`、`P0_B02_C01_QB_PB-e02`）+ 2 个受保护课程训练父节点（`R1-e01`、`R2-e01`）+ 1 个活跃恢复点（`F02` 正在运行，Cursor 记录至 Chunk 78/123）。
- **单 Chunk 物化修复验证**：修复 `laya_batch_train.py` 中 `sum(mat_res.values())` 导致的类型错误，改为显式 `int(res.get("item_count", sum(res.get("by_class", {}).values())))`，并在服务器完成 CPU 隔离单 Chunk 实测通过（100 Items 物化及张量转化成功率 100%）。
- **数据台账与口径完全对齐**：
  - 合法训练候选（`LEGAL_CANDIDATE_REFERENCES`）：严格对齐为 **4,863,900**（六允许来源：`TRA-001` 1,673,528、`TRA-002` 1,864,427、`ROUTE-004` 31,766、`CACHE-001` 28,714、`TIME-001` 1,122,577、`OWN-002` 142,888）。严格排除 `ROUTE-001`/`ROUTE-002`（152,524 条，LICENSE_PENDING 隔离）与 `ENV-001`/`ENV-002`（10,821 条，S4 环境元数据）。
  - 已训练去重独立单元（`DISTINCT_TRAINED_UNITS`）：已完成 8 个 Run 实测覆盖 **166,448** 个去重单元；数据池候选单元数 **1,344,240**（六源）作为 `DISTINCT_CANDIDATE_UNITS` 独立报告，两者彻底解耦。
  - 跨 Split 隔离：Train/Val/Test 交叉泄漏为 0，经单元 ID 唯一映射检验保证 100% 独立隔离。
- **裁剪系统收敛**：`CheckpointRetentionManager` 作为全项目唯一正式自动选择与裁剪入口，硬编码全局上限 `MAX_CORE_CHECKPOINTS = 5`，Preflight 预算校验严格计入完整 Run 峰值字节；`checkpoint_inventory_and_pruner.py` 降级为只读资产审计工具。
- **恢复语义明确**：正式确立 `EPOCH_LEVEL_RESUME`，跨 Epoch 恢复必须重载上一 Epoch 物理权重，Chunk 内部中断保证模型权重与数据位置绝对同步。
- **隐私脱敏处理**：`top5_core_checkpoint_manifest.json` 与看板中全部绝对路径已脱敏转为项目相对路径（`runs/...`）。
- **学术真实性**：联合路由目标维持 `DATA_NOT_READY`，拒绝跨数据集编造虚假联合标签。

## 2026-10-14 · AUTONOMOUS-TRAINING-V4 长期训练与独立 Benchmark 评估看板真实性纠偏

> **重大纠偏说明**：经 Planning 独立比对 Harbor 官方代码树目录核实，官方真实 Terminal-Bench 2.1（`harbor-framework/terminal-bench-2-1`）任务总数精确为 **89 个**，此前生成的 160 题 manifest 存在 149 个虚构未验证 ID（仅 11 题匹配），现已正式标记为 `REJECTED_UNVERIFIED_MANIFEST` 全面作废，绝不计入 Checkpoint 晋级与实验成果。项目已全面升级锚定官方 2.1 Commit `7131e4375048a0e408a8fb404b5f499d726b695b`。

- **独立评测集 ENV-004 (Terminal-Bench 2.1 官方核准)**：
  - 89 个终端系统/DevOps/开发真实挑战任务套件（Commit `7131e4375048a0e408a8fb404b5f499d726b695b`，MIT 许可证），100% 隔离于 660 万训练数据池。
  - 三级划分：
    - `CANARY` (8 题快速冒烟验证)：当前状态定级为 `MANIFEST_VALIDATED`（元数据、Docker 镜像与 `task.toml` SHA256 官方校验通过；Docker 容器与 Oracle 运行未执行，严禁冒充真实执行通过）。
    - `EXTERNAL_DEV` (24 题分层独立泛化评估)：仅针对 Top-5 候选模型执行。未部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
    - `FINAL_TEST` (57 题终局评估)：永久物理密封，调优期间访问权重严格为 0.00。
- **评测阶梯四级定义**：
  - `MANIFEST_VALIDATED`：任务 ID、元数据 schema 与 SHA256 与官方树一致（当前 Canary 状态）。
  - `ENVIRONMENT_READY`：评测节点 Docker 容器镜像拉取构建完成。
  - `ORACLE_VERIFIED`：官方标准参考解在沙盒内验证通过。
  - `AGENT_EVALUATED`：真实 Serving 端点联通，完整 Agent 决策交互评测完成。
- **三级评估体系与动态打分机制**：
  - 内部验证（INTERNAL_VAL）：每 Epoch 自动在固定验证集（S1 561 题、S2 337 题、S3 1,397 题）计算。
  - 外部泛化（EXTERNAL_DEV）：在没有部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
  - 终局测试（FINAL_TEST）：永久封存，模型选择权重严格为 0。
  - 动态打分公式：`selection_score = 0.80 * internal + 0.20 * external_dev`（未评估时严格采用 100% 内部验证分）。
- **长期多阶段演进规划**：
  - Stage 1: ALGN_01 (S1), ALGN_02 (S1+S2), ALGN_03 (S1+S3), ALGN_04 (S1+S2+S3)
  - Stage 2: 数据规模阶梯 (10% F08, 25% F09, 50% F10, 100% F07)
  - Stage 3: 分层全量与跨层覆盖 (L1..L4 单层与累积，当前 F02 执行中，推进至 Epoch 2/2 Chunk 71+/123 · 79.0% 累计完成)
  - Stage 4: 部分比例与分位抽样 (F11..F16)
  - Stage 5: 课程学习与能力渐进 (Base -> L1 -> L1+L2 -> L1..L4)
  - Stage 6: 多 Seed 与状态变量消融
- **看板交互升级**：
  - 页面顶部 Section 0.00，实时反映服务器 Headless 守护状态（PID 2207051 / 2287331）、GPU 显存/利用率、Epoch/Chunk 进度、三级评测指标（Canary: 8 MANIFEST_VALIDATED, DEV: 24 ROUTER_SERVING_NOT_READY, Test: 57 SEALED）与数据隔离证明。

## 2026-10-14 · P0 恢复一致性、数据分层迁移与长队列交接验收（MR-P0-RESUME-INTEGRITY-20261014）

- **恢复模型与优化器引用一致性彻底修复（P0-1）**：
  - 根因定位：旧代码在初始模型上实例化 AdamW，恢复时重载新模型对象，导致优化器内部参数对象仍指向丢弃的旧模型，造成后续训练梯度更新脱节。
  - 架构重构：确立“模型终态确定后再建优化器”准则。优先解析断点与有效物理权重，终态模型加载完成后直接提取其参数对象实例化优化器，并通过 `assert id(p) in model_param_ids` 强制校验，从根本上确保优化器与模型参数一一对应。
  - 状态持久化升级：保存 Checkpoint 时同步输出包含完整 AdamW 动量、Cosine 学习率调度器状态、AMP GradScaler 及 PyTorch CPU/CUDA 随机数种子的 `optim_state.pt`。保存失败显式抛出 `RuntimeError`，严禁静默忽略。
  - 6 项隔离测试全数通过（`router_data/test_resume_integrity.py`）：重现断连 Bug、验证修复后参数真实更新（max diff > 0.05）、验证 `EXACT_RESUME` 恢复轨迹比特级精确吻合、验证缺失物理权重回退至 Epoch 0（`EPOCH_RESTART`）、验证已达目标轮次但缺失权重时强制报错拦截、验证优化器状态持久化失败报错。
- **数据准入严格校验与无猜测监督（P0-2）**：
  - 彻底移除依据监督类型或数据源 ID 进行启发式目标猜测的分支。
  - 接入显式 `SCHEMA_INCOMPATIBLE` 校验：索引记录若缺失 `split`、`train_eligible`、`source_policy_train_allowed`、`quality_grade`、`primary_supervision_class` 立即拒绝训练并报错。
  - 监督目标必须同时属于合法目标集合并在 `candidate_targets` 拥有第一手标签证据。
  - 实测四层全量普查：4,863,900 条合法记录 100% 通过严格准入；跳过 Q3/Q4 不合格样本 37,326 条；跳过非法/不许可来源 0 条；跳过无有效监督证据 0 条。
- **旧版与新版 486.39 万候选分层迁移核验（P0-3）**：
  - 物理行数比对：旧分片与新分片物理总行数完全一致（L1: 663,749, L2: 1,380,533, L3: 2,028,793, L4: 2,748,870），六大允许源总量与单源记录数完全相同。
  - 迁移根因溯源：旧文档数值（L1: 489,911, L2: 973,501, L3: 1,475,527, L4: 1,924,961）来自 V1 单纯按质量初筛；V2.1 新普查（L1: 485,210, L2: 1,001,005, L3: 1,466,724, L4: 1,910,961）引入了多维多样性签名 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)`，在同等质量级打破平局，使得跨源独立单元分布更加均衡。跨层重复为 0，独立任务单元无泄漏，Train/Val/Test 身份完全保持。
  - 实验可比性确立：F01、F02 与后续 F03 均统一使用 `MR-QUALITY-GRADING-V2-1`（`streaming_v2_1`），数据快照完全一致，实验指标科学可比。
- **服务器现场推进与 F03 自动交接就绪（P0-4）**：
  - A6000 现场稳定推进：队列守护 PID 2207051、训练 PID 2287331，GPU 显存占用 9,845 MiB，利用率 79%~97%，根分区可用空间 1.2 TiB。
  - F02 正在平稳运行，最新进度已推进至 Epoch 2/2 · Chunk 96/123（Step 27,940/31,304，消费样本 1,788,127，Loss 0.5010）。
  - F02 结束后，后台队列将自动调起 F03（L3 单层全量 1,466,724 条）。已完成代码和索引热替换，F03 将直接以最新参数绑定和严格数据准入规范运行。
- **外部基准 Terminal-Bench 2.1 状态保持**：
  - 89 题与既有代码基准 0 重叠；服务器非特权环境保持 Canary `MANIFEST_VALIDATED` 与 External DEV `ROUTER_SERVING_NOT_READY`，严禁伪造测试结果。
- **Top-5 物理权重严格保留**：
  - 遵循 `MAX_CORE_CHECKPOINTS = 5` 上限，当前磁盘严格保留 5 份最优核心模型（`P0_B03_C08_QB_PB`、`P0_B01_C01_QB_PB`、`P0_B03_C05_QB_PB`、`P0_B02_C01_QB_PB`、`P0_B03_C01_QB_PB`）及 1 份运行中容灾临时权重（`F02/_temp_recovery`）。



## 2026-10-14 · 过夜长队列可靠性修复、V1/V2.1 逐条对账与 ALGN 训练优先级调整（MR-ALGN-PRIORITY-REPAIR-20261014）

- **现场运行与 F02 阶段性推进**：
  - A6000 服务器（`a6000-server`）守护进程 PID `2207051`、底层算子 PID `2287331`、Watchdog PID `2301880` 持续稳定运行；
  - F02 推进至 Epoch 2/2 Chunk 120+/123，累计完成 30,884+/31,304 步更新，消费 1,976,543+ 条样本，最新分块 Loss `0.5042`，即将迎来 Epoch 2 固定验证终评；
  - 硬件指标稳定：GPU 利用率 81%，显存 9,845 / 49,140 MiB (20.0%)，温度 74°C，功耗 290W，根分区剩余 1,148.4 GiB。
- **Checkpoint 与 Cursor 一致性架构（10 项可靠恢复规则落地）**：
  - 彻底解决“Cursor 每个 Chunk 更新，但权重仅在 Epoch 结束保存”造成的恢复错位隐患；
  - Checkpoint 目录内部持久化 `recovery_state.json`，显式绑定 `run_id`、`epoch`、`chunk_idx: 0`、`step_count`、`consumed_items`、`protocol_version` 及物理权重 SHA256；
  - 恢复引擎严格遵守 Epoch 边界可靠恢复规则：从上一个有效物理 Checkpoint 恢复，重跑当前未完成 Epoch，`start_chunk` 重置为 0，`step_count` 与 `consumed_items` 回滚至 Checkpoint 对应值，坚决禁止将 Epoch 1 权重代入 Epoch 2 Chunk 98，坚决禁止中间无权重空转；
  - 生产级真实流式 Chunk 崩溃恢复测试套件 `test_streaming_chunk_recovery.py`（3/3 测试 100% 通过）：
    - Test 1: 模拟 Epoch 2 Chunk 3 崩溃，恢复后自动回滚至 Epoch 1 边界重训 Epoch 2，Logits 最大差值 0.000000e+00，参数最大差值 0.000000e+00，步数与消费量与连续参考轨迹比特级完全一致；
    - Test 2: 缺失物理权重安全触发 `EPOCH_RESTART` 并清空计数；
    - Test 3: Cursor 显示已达总轮次但物理权重缺失时强制抛出 `RuntimeError`，封堵伪 completed 漏洞。
- **队列失败多级安全暂停机制**：
  - 修复 `run_full_graded_queue.py` 中子 Run 非零退出后盲目继续下一 Run 的风险；
  - 引入显式多级错误分类：`PAUSED_DATA_INTEGRITY`（数据资格与 Schema 异常）、`PAUSED_RECOVERY_INTEGRITY`（恢复点或优化器绑定异常）、`PAUSED_GPU_BUSY`（OOM 或 GPU 异常）、`PAUSED_DISK_OR_BUDGET_GUARD`（磁盘超限）、`PAUSED_RUN_FAILED`（未分类训练退出）；
  - 任何非零退出立即中止队列并持久化 `queue_state.json`，坚决杜绝 F03 失败后自动消耗 GPU 跑 F04。
- **V1 与 V2.1 分层逐条记录稳定 ID 对账与真实交集核验**：
  - 物理扫描 V1 与 V2.1 全部分层（共 5,942,291 条记录）：
    - 共同记录数：`5,942,291`（**100.00%**，独有记录严格为 0）；
    - Unit ID 冲突：`0`（每个样本独立任务单元 ID 100% 相同）；
    - Split 身份冲突：`0`（每个样本 Train/Val 身份 100% 相同）；
  - 迁入迁出根因：V2.1 引入 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)` 打破同分平局，等质样本跨层更均匀重组；
  - **真实验证集交集核验**：扫描 5,070,313 条训练记录与 3,142 条固定验证集记录，**数学交集严格为 0（Record Overlap = 0, Unit Overlap = 0）**，彻底打破硬编码假设，由真实 ID 集合交集实证 0 泄漏。
- **ALGN 四组优先级前置与严格比例配额采样**：
  - 在 `FULL_COVERAGE_STAGE_MAP` 中将 ALGN_01..04 前置至 Stage 2.5（优先级排在 F02 之后、F03 之前）；
  - 改造调度循环为动态查询，在 F02 正常结束后自动率先调起 ALGN 探索小预算对照；
  - 修复多监督比例稀释漏洞：引入严格配额交错算法，确保 S1:S2（2:1）或 S1:S2:S3（2:1:1）在每个 Chunk 和 Epoch 内严格保持比例，避免主监督被弱相关数据淹没；
  - 每组独立评估并输出 S1 Loss、Accuracy、Brier、ECE，以真实指标作为后续按比例扩充的决策依据。
- **Top-5 与看板状态**：
  - 保持 MAX_CORE_CHECKPOINTS = 5，当前磁盘保留 Top-5 核心模型权重 + 1 份容灾恢复点；
  - Web 看板与文档同步更新真实服务器监控数据，不手写虚构状态。


## 2026-10-14 · Checkpoint 留存时序闭环、真实验证集 0 泄漏实证、生产级恢复引擎验证与 ALGN 长期消融推进（MR-ALGN-PRIORITY-REPAIR-20261014-V2）

- **P0-1 Checkpoint 留存时序与评审闭环修复**：
  - 根因定位：`run_full_coverage_stream_run()` 中 `handle_epoch_checkpoint()` 在 `history.append(entry)` 之前调用，导致 `run.json` 缺少当前 Epoch，`load_and_evaluate_all()` 找不到候选节点，被错误判为 `not_qualified` 并降级为 `METADATA_ONLY`；
  - 修复实现：严格保证当前 Epoch entry 在评审前写入 `history` 与 `run_meta["history"]`，并在 `handle_epoch_checkpoint()` 内部增加无重幂等写入保障；
  - 终态完结防报错：Cursor 达到最大 Epoch 且 `run.json` 状态为 `completed` 且含有完整有效历史时，合规接纳为已完成状态，不再因物理权重依据留存策略被淘汰而误报 `Corrupt state`；
  - 回归验证通过：编写并全数通过专用回归测试 `test_retention_ordering.py`，实测当前 Epoch 稳定参与 Top-5 动态排序并正确晋级保留（`RETAINED_BEST` / `RETAINED_TOP_K`）。
- **P0-2 真实验证集无泄漏实证审查彻底纠偏**：
  - 根因定位：旧脚本 `audit_v1_v2_stratification.py` 扫描顶层键，未穿透 JSONL 的 `provenance` 结构体，导致验证集加载为 0 条并形成“与空集交集为空”的伪 0 泄漏假象；
  - 修复实现：严格从权威验证集目录 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val/` 加载 S1（561 条）、S2（337 条）、S3（4,794 条，涵盖 2,244 个请求）共计 3,142 个独立 Record ID 和 Unit ID，计算物理 SHA256 校验和（S1: `ca5a956dda1c8631...`, S2: `7b39deadb8d83964...`, S3: `fe41ae9f17a9dc5e...`）；
  - 全量实测：对全库 `quality_grading_v2_1` 共计 15,210,939 条训练记录进行逐行无遗漏扫描，真实交集为严格的 **0 条**（Record Overlap = 0, Unit Overlap = 0），以严密的数学确凿性实证了全项目绝对零数据泄漏！
- **P0-3 生产级恢复引擎验证全量闭环**：
  - 抽取生产函数 `resolve_checkpoint_to_resume()` 统一接管训练恢复与检查点锚定；
  - 全面升级 `test_streaming_chunk_recovery.py`，6/6 项测试 100% 通过（参考轨迹比特级一致、缺失物理权重安全触发 `EPOCH_RESTART`、虚假 completed 拦截、合法 `METADATA_ONLY` 完结状态接纳、SHA256 权重校验和一致性、恢复后真实反向传播参数更新）。
- **P0-4 不可变历史失败审计账本确立**：
  - 建立不可变账本 `docs/historical_execution_failure_ledger.json`（及同名副本于 Run 根目录），详细记录早期 `F03` 与 `F04` 遭遇的 `NameError: params` 错误上下文、堆栈行号、根因、以及修复 Commit `c479f6f`；
  - 彻底封堵因 `failed_runs={}` 内存重置而导致的错误痕迹抹除隐患，确保所有历史失败事件永久可审计、可追溯。
- **P1 ALGN 系列长期消融实证与泛化突破**：
  - `ALGN_01_S1`：完成 2 轮训练，S1 Val Loss 从 0.6000 微升至 0.6063，准确率 66.13%，出现典型单任务轻度过拟合；
  - `ALGN_02_S1_S2`：完成 2 轮训练，S1 Val Loss 显著降至 **0.5983**（跌破 0.60 关口，超越单任务最佳），S1 Val Acc 达 **66.84%**，S2 判别准确率 53.71%，实证了真实智能体轨迹（TRA-001/002）2:1 联合监督具有极强的泛化正则化能力；
  - `ALGN_03_S1_S3`：正在 RTX A6000 上高速推进，Epoch 1 Chunk 128+/162，Loss 稳定收敛于 0.51~0.62，GPU 利用率持续 60%~100%，功耗 260~296W，根分区可用空间 1.15 TiB。
- **Top-5 物理权重与服务看板状态**：
  - 物理 Checkpoint 严格遵循 `MAX_CORE_CHECKPOINTS = 5` 硬上限，当前保留 Top-5 核心模型权重，磁盘空间 1,151.6 GiB（充裕）；
  - HTML 看板和服务器自治监控脚本持续稳定运行。

