# ModelRouter研究结果总览

当前主线：真实K=3，Luna／HY4／Terra，Model×Native Effort、缓存连续性、Laya／Kev原始与训练版、Luna轨迹教师，以及含全部开销的完整Episode收益。历史实验保持原处；以下分类不改写旧成绩。

| 实验性质 | 入口 | 证据范围 |
|---|---|---|
| `ALIAS_OR_SINGLE_BACKEND` | [早期三身份联调](iterations/20261029-v9-alias-smoke-tools/)、[DeepSeek开发运行](iterations/20261102-v9-deepseek-dev/) | Agent、Router、工具和记录链路；不支持三个独立模型质量或跨模型物理缓存结论 |
| `REAL_API_IDENTITY` | [真实步骤比较](iterations/20261101-v9-quality-step-supervision/review.md)、[历史完整任务与费用](iterations/20261105-v9-global-value/review.md) | 真实Sol／Luna API身份、动作与原验证；不证明供应商底层权重。旧正式40条为Model-only，不是新K=3联合监督 |
| `ROUTER_TRAINING_AND_STATIC_EVALUATION` | [Laya／Kev训练汇总](training/training_research.md)、[原候选记录](../planning/CANDIDATE_PROGRESSION_MATRIX.md) | 父权重、参数、合法来源、更新、固定Val与可加载性；不同协议不合并排名，STEP009/010不升级为新池效果 |
| `SYNTHETIC` | [RQ4原Demo](benchmarks/rq4_data.json)、[权重与方法核对](iterations/20261106-v9-routing-granularity/review.md) | 预填演示，不是正式消融成绩 |
| `UNKNOWN_OR_ENVIRONMENT_FAILURE` | [原Trial与终态验证区别](iterations/20261106-v9-complete-opportunities/review.md) | 原Reward缺失、环境失败、身份不符分别保留；终态后来通过不改变原完整Episode结果 |
| `REAL_K3_DEVELOPMENT` | [本批配置与结果](iterations/20261106-v9-k3-real/) | 两个已开发暴露任务，原Harbor／Evaluator、真实请求、原始与训练代表、Effort与缓存；有效性按实际返回身份和终局分别报告，不作为最终盲测 |
| `REAL_K3_FORMAL_SUBSET_AND_TRAINING` | [完整方法、Train及官方子集](iterations/20261107-v9-full-method/review.md) | T/M/H与Luna教师原生消费、有限新联合监督、原Trainer更新、Terminal-Bench 2.1事前子集的原始/更新完整Episode；跟进与异常分列，不证明完整K=3净收益 |

完整私人响应、请求正文、账单、凭据和物理权重不进入公开目录。模型参考费、供应商实收、Router／教师／CPU／GPU／VM资源费用分别保留未知项。官方Reward、单步结果、终态恢复、静态预测和模拟结果不能互相替代。
