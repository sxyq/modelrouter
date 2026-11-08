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

当前候选为 `gpt-6-luna`、`glm-5.3-flash` 与 `gpt-6.1-terra`，Registry登记15个Model×Native Effort组合。GLM已绑定唯一私人配置的Colink，Chat Completions使用low/high/max；三档均已有实际工具和完整Harbor官方Reward 1，返回Effort未报告。Luna Max返回xhigh及Terra none返回medium的原记录保持。每批动作由统一Registry和Provider派生，登记数量不代表渠道逐档独立确认。旧HY4结果保留历史身份。

AA沿现有TTL自动更新、force刷新、STALE和同批固定snapshot_id机制，Registry派生目标并进入Laya/Kev的M输入，不逐生成联网。本批固定v7/130指标/Intelligence Index5.0.1；Luna/Terra各六档，GLM仅Max，Low/High缺测。授权AA API Key尚缺，没有借用其他模型或档位成绩。

实验结果必须区分模型执行、教师、Router 与环境费用；供应商 Usage、返回身份、终局和不完整费用按原记录表达。旧 Model-only、HY4、映射和多 Agent 相关数据保留原始身份，不重写为新池联合监督。

## 目录

- `code/`：ModelRouter Python 包及现有执行、Provider、训练和能力代码。
- `data/`：数据来源和已保存材料；大型原始数据及模型权重按各自实体位置管理。
- `experiments/`：实验配置与协议。
- `results/`：真实运行记录与报告；历史结果保持原样。
- `planning/`：研究问题、当前状态及注明历史性质的早期方案。
- `external/`：第三方仓库、Benchmark 与文献资料。

2026-10-18 的 V8 执行协议、目录迁移清单、双子代理计划和旧候选矩阵仅供追溯，不能覆盖本 README 和上述现行入口。正式实验只经 Harbor `DefaultAgent` 与原 Evaluator；旧 `agent/legacy.py` 留作历史但不导出或调用，已删除的 development 命令、`sandbox/canary_verifier.py` 和 `experiments/harbor` 同名 shim 不是入口。旧 Mock `pwd`/`fix-git` 分数只保留历史记录，不推荐为 smoke 命令。
