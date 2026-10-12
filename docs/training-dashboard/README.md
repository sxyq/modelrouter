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
