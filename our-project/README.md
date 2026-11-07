# ModelRouter 自有项目目录

`our-project/` 汇集项目代码、数据规范、真实实验结果和科研文档。当前研究以单 Agent 执行中的模型×Provider 原生档位联合选择为中心；完整任务仍由原 Harbor、Mini-SWE 与 Evaluator 链路执行。

## 当前研究入口

- [项目现状](planning/PROJECT_STATUS.md)：最新真实执行、训练状态和仍缺结果。
- [研究总纲](planning/RESEARCH_OVERVIEW.md)：五个 RQ、单 Agent 方法与证据边界。
- [论文实验与图表规划](../汇报/汇报三/ModelRouter论文实验与图表规划.md)：保留 Fig.1–8、Table 1–12 结构。
- [结果入口](results/README.md)：按实验批次查看原始报告与结果。
- [数据来源及许可](data/DATA_SOURCE_AND_POLICY_REGISTRY.md)：来源登记与使用信息。

RQ3 正式研究单 Agent 阶段识别、真实子任务边界及生成决策粒度。`inspect/modify/verify/recover` 是执行阶段标签，本身不是任务拆分；只有原任务或现有执行记录中可辨认的子任务边界才作为拆分单位。取消多 Agent 架构、角色分工、handoff 和 Agent 数量变量。

## 模型候选与能力证据

当前目标候选为 GPT-6 Luna、GLM-5.3-Flash 与 GPT-6.1 Terra，共规划 15 个 Model×Native Effort 组合。GLM 预期使用 Chat Completions 与 low/high/max 原生档位；渠道授权、绑定和精确模型 ID 尚待确认，当前不得写成已验证或可调用。确认前不启动新的固定 K=3 Harbor 实验。每批可用动作以实际 Registry/Provider 的精确模型 ID、原生档位、工具支持与上下文条件为准；不以规划数量填补未支持或未证实动作。旧 HY4 及其真实结果只作为历史，不替代新池候选证据。

AA 记录按精确模型和 Effort 保存真实测量及来源。目标刷新方式为 TTL 自动更新、显式 force 刷新和批次固定 `snapshot_id`；不在单次 Router 决策中联网。目前真实刷新正在进行，结果待写回；现有代码仍是手动刷新，TTL/force 与 GLM 新池逐档能力结果尚未完成，不能作为已交付能力描述。

实验结果必须区分模型执行、教师、Router 与环境费用；供应商 Usage、返回身份、终局和不完整费用按原记录表达。旧 Model-only、HY4、映射和多 Agent 相关数据保留原始身份，不重写为新池联合监督。

## 目录

- `code/`：ModelRouter Python 包及现有执行、Provider、训练和能力代码。
- `data/`：数据来源和已保存材料；大型原始数据及模型权重按各自实体位置管理。
- `experiments/`：实验配置与协议。
- `results/`：真实运行记录与报告；历史结果保持原样。
- `planning/`：研究问题、当前状态及注明历史性质的早期方案。
- `external/`：第三方仓库、Benchmark 与文献资料。

2026-10-18 的 V8 执行协议、目录迁移清单、双子代理计划和旧候选矩阵仅供追溯，不能覆盖本 README 和上述现行入口。正式实验只经 Harbor `DefaultAgent` 与原 Evaluator；旧 `agent/legacy.py` 留作历史但不导出或调用，已删除的 development 命令、`sandbox/canary_verifier.py` 和 `experiments/harbor` 同名 shim 不是入口。旧 Mock `pwd`/`fix-git` 分数只保留历史记录，不推荐为 smoke 命令。
