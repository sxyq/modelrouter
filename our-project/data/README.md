# Data

数据分为三层：

- `source/`：已导出的来源统计文件；
- `cleaned/`：经过模型筛选和字段清理的明细；
- `summaries/`：按模型和推理档位汇总的结果。

当前数据以调用级统计为主，不能直接替代任务级账单。CCH 使用 USD，博客后台使用 quotaUnits，两者暂不合并成本数值。

## 数据源、模型能力与缓存政策的唯一详细台账

[DATA_SOURCE_AND_POLICY_REGISTRY.md](DATA_SOURCE_AND_POLICY_REGISTRY.md) 专门记录外部 Agent 轨迹、静态任务—模型比较、真实前缀复用/模拟缓存、长记忆、多 Agent、时间资源数据集，以及主要国内外模型供应商的 Effort、Cache、费用、可用性和使用条款的官方来源/待核项。

2026-10-10：现有 14 个公开清洗源共 6,600,628 行，Kev/Laya 静态选择导出共 84,310 行；唯一命令入口为 `prepare_router_data.py`，适配器保存在内部 `router_data/`。数据的真实用途、费用来源和独立性以 [科研数据收尾报告](科研数据收尾报告.md) 为准，不能把行数当成已可训练的动态路由标签。
