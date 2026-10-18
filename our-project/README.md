# Our Project · ModelRouter 自有项目主目录

本目录是 **ModelRouter 代码、数据规范、科研实验及研究文档的唯一目标主目录**。本仓库的 Git 根目录仍为上一层 `路由/`；现有 `router_data/`、`experiments/`、`docs/` 和 `research/` 等旧入口目前仍有训练和脚本在使用，**尚未完成物理迁移**。

**最新目录盘点与逐步迁移手册**：[REPOSITORY_STRUCTURE_MIGRATION_20261018.md](planning/REPOSITORY_STRUCTURE_MIGRATION_20261018.md)。执行前先核对 Mac 和 A6000 实体位置，保护正在运行的正式训练，先迁本机非训练文件，后在安全 Run 边界迁服务器训练入口。

## 规范目录（渐进实施）

- `code/`：自有代码，按 `baselines/agent/sandbox/data_pipeline/datasets/training/serving/benchmark/providers/telemetry` 分类。
- `data/`：数据来源政策、清洗后的数据、训练视图、哈希与样本清单；大型原始数据保存在受保护实体存储。
- `external/`：外部算法的原始源码/版本、官方 Benchmark 及论文、项目登记与文献笔记。
- `experiments/`：RQ1–RQ3 及未来其他研究问题的配置、冻结实验矩阵与协议。
- `results/`：Laya/Kev 训练、竞品路由、Harbor 官方 Trial、评分、每请求使用量及费用；详细敏感原文不入 Git。
- `dashboard/`：现有训练与 Benchmark 图表及监控的规范目标位置，保留本地端口 8765 的旧入口。
- `docs/`：Planning、系统架构、运维、论文及组会文档；迁移过渡时 `planning/` 仍是当前权威目录。
- `.runtime/`：模型和 API 服务之外的短期缓存/临时文件/锁与进程日志，不入 Git。

## 当前唯一权威文档

- [最新运行与交接状态](planning/PROJECT_STATUS.md)
- [研究问题/用户批准](planning/EXPERIMENT_QA.md)
- [科学方法总览](planning/RESEARCH_OVERVIEW.md)
- [数据来源及许可](data/DATA_SOURCE_AND_POLICY_REGISTRY.md)
- [V8 长周期执行协议](planning/V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)
- [目录结构重构执行清单](planning/REPOSITORY_STRUCTURE_MIGRATION_20261018.md)

此 README 描述**目标归属**，不表示已经搬动服务器运行目录、完成 12 组实体模型训练或通过官方 Harbor Benchmark。保留所有能复现历史研究的原有路径和结果，直到迁移验收。
