# ModelRouter研究结果总览

当前主线：真实K=3，Luna／GLM-5.3-Flash／Terra，Single-Agent、Model×Native Effort、T/M/H、AA逐档能力、缓存连续性、Laya／Kev原始与训练版、Luna轨迹教师，以及含全部开销的完整Episode收益。RQ3为单Agent阶段、真实子任务边界与路由粒度。历史HY4实验保持原处；以下分类不改写旧成绩。

| 实验性质 | 入口 | 证据范围 |
|---|---|---|
| `ALIAS_OR_SINGLE_BACKEND` | [早期三身份联调](iterations/20261029-v9-alias-smoke-tools/)、[DeepSeek开发运行](iterations/20261102-v9-deepseek-dev/) | Agent、Router、工具和记录链路；不支持三个独立模型质量或跨模型物理缓存结论 |
| `REAL_API_IDENTITY` | [真实步骤比较](iterations/20261101-v9-quality-step-supervision/review.md)、[历史完整任务与费用](iterations/20261105-v9-global-value/review.md) | 真实Sol／Luna API身份、动作与原验证；不证明供应商底层权重。旧正式40条为Model-only，不是新K=3联合监督 |
| `ROUTER_TRAINING_AND_STATIC_EVALUATION` | [Laya／Kev训练汇总](training/training_research.md)、[原候选记录](../planning/CANDIDATE_PROGRESSION_MATRIX.md) | 父权重、参数、合法来源、更新、固定Val与可加载性；不同协议不合并排名，STEP009/010不升级为新池效果 |
| `SYNTHETIC` | [RQ4原Demo](benchmarks/rq4_data.json)、[权重与方法核对](iterations/20261106-v9-routing-granularity/review.md) | 预填演示，不是正式消融成绩 |
| `UNKNOWN_OR_ENVIRONMENT_FAILURE` | [原Trial与终态验证区别](iterations/20261106-v9-complete-opportunities/review.md) | 原Reward缺失、环境失败、身份不符分别保留；终态后来通过不改变原完整Episode结果 |
| `REAL_K3_DEVELOPMENT` | [本批配置与结果](iterations/20261106-v9-k3-real/) | 两个已开发暴露任务，原Harbor／Evaluator、真实请求、原始与训练代表、Effort与缓存；有效性按实际返回身份和终局分别报告，不作为最终盲测 |
| `REAL_K3_FORMAL_SUBSET_AND_TRAINING` | [完整方法、Train及官方子集](iterations/20261107-v9-full-method/review.md) | T/M/H与Luna教师原生消费、有限新联合监督、原Trainer更新、Terminal-Bench 2.1事前子集的原始/更新完整Episode；跟进与异常分列，不证明完整K=3净收益 |
| `GLM_REFACTOR_AND_REAL_DEVELOPMENT` | [本批八部分结果](iterations/20261107-v9-full-method/v9_refactor_review.md) | 唯一执行链、精确GLM渠道、AA v7与原生输入；新开发题10尝试、4个官方零分、6个无有效Reward。未证明新池训练或净收益 |
| `GLM_POOL_PREFIX_TRAINING_AND_EPISODES` | [合法联合监督](iterations/20261108-v9-k3-training/joint_supervision.json)、[Laya训练](iterations/20261108-v9-k3-training/laya_training.json)、[Kev训练](iterations/20261108-v9-k3-training/kev_training.json)、[前批polyglot](iterations/20261108-v9-polyglot-independent/analysis/official_results.json) | 1条五候选联合偏好+16辅助，两架构各17更新已保存；polyglot为已观察任务，旧429保持 |
| `GLM_POOL_49_OFFICIAL_ATTEMPTS` | [本轮八部分结果](iterations/20261108-v9-k3-training/review.md)、[49条脱敏终局与费用](iterations/20261108-v9-k3-training/episode_results.json)、[训练及最终原生输入](iterations/20261108-v9-k3-training/native_encoding.json) | 49尝试已结束，33有效终局/21个1/12个0，16无Reward；GLM开发和constraints三档官方1。sanitize Laya1→0、Kev0→0；text有效终局全0。模型+教师已知参考费$1.45700272，完整实收/资源价未知。241保存前缀48→0截断及四实体原生前向成功，原Episode输入版本不改；修复后完整比较和净收益仍缺 |

完整私人响应、请求正文、账单、凭据和物理权重不进入公开目录。模型参考费、供应商实收、Router／教师／CPU／GPU／VM资源费用分别保留未知项。官方Reward、单步结果、终态恢复、静态预测和模拟结果不能互相替代。

## 完整任务进度与结果入口

[Terminal-Bench 2.1.0的89题逐项清单](benchmark/README.md)：29题有Agent尝试，22题有官方Reward，7题尝试但没有Reward，60题未由Agent运行；神经Router参与25题。另有2题仅Oracle，共31题有Harbor记录、58题无任何记录。全历史187个Agent记录为67个1、39个0、81个缺Reward，另11个Oracle；不跨池合成现行Pass率。

当前GLM池三题完整比较：Laya原始/训练为2/3、1/3通过；Kev两版各1通过、1失败、1缺Reward。模型+教师已知参考费合计分别$0.13532442/$0.11108159和$0.03250188/$0.17776966；原始Kev三题参考费齐全，其他三实体有请求费用缺失。完整实收/资源USD均未知。逐题费用、墙钟、固定模型和教师关闭结果集中在上述89题入口，原Trial不改动。

## 全项目迭代目录索引

整理时间2026-11-08。75个迭代目录中43个含原Harbor记录，按trial_id合计198个不同记录，涉及官方manifest中31个任务ID。这里包含历史Oracle、映射、Sol/Luna、旧HY4与新GLM池，不将跨池数字合成当前方法成功率。无Harbor记录的目录仍可能有真实步骤、训练、编码或分析成果；完整用途以各批次原报告为准。

break-filter-js-from-html与filter-js-from-html是两个官方任务ID，前者仅Oracle。31题中Agent参与29题；其中各任务的重复运行、用途和已经观察身份保留。

| 原批次 | Harbor记录 | Reward1 | Reward0 | 无Reward | 已观察任务 |
|---|---:|---:|---:|---:|---|
| [20261019-v10-integration](iterations/20261019-v10-integration/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261019-v10-oracle](iterations/20261019-v10-oracle/) | 1 | 0 | 0 | 1 | fix-git |
| [20261029-v9-alias-smoke](iterations/20261029-v9-alias-smoke/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261029-v9-alias-smoke-sse](iterations/20261029-v9-alias-smoke-sse/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261029-v9-alias-smoke-tools](iterations/20261029-v9-alias-smoke-tools/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261029-v9-kev-alias-smoke](iterations/20261029-v9-kev-alias-smoke/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261030-v9-kev-alias-smoke-compact](iterations/20261030-v9-kev-alias-smoke-compact/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261030-v9-official-luna](iterations/20261030-v9-official-luna/) | 1 | 0 | 0 | 1 | fix-git |
| [20261030-v9-official-luna-complete](iterations/20261030-v9-official-luna-complete/) | 1 | 1 | 0 | 0 | fix-git |
| [20261030-v9-oracle-native](iterations/20261030-v9-oracle-native/) | 1 | 0 | 0 | 1 | fix-git |
| [20261030-v9-oracle-rosetta](iterations/20261030-v9-oracle-rosetta/) | 1 | 1 | 0 | 0 | fix-git |
| [20261031-twinrouterbench-independent](iterations/20261031-twinrouterbench-independent/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261031-v9-db-wal-recovery](iterations/20261031-v9-db-wal-recovery/) | 1 | 1 | 0 | 0 | db-wal-recovery |
| [20261031-v9-official-alias](iterations/20261031-v9-official-alias/) | 2 | 2 | 0 | 0 | fix-git |
| [20261031-v9-real-model-comparison](iterations/20261031-v9-real-model-comparison/) | 5 | 1 | 1 | 3 | cobol-modernization、extract-elf |
| [20261031-v9-real-route-supervision](iterations/20261031-v9-real-route-supervision/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261101-v9-k2-supervision-expansion](iterations/20261101-v9-k2-supervision-expansion/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261101-v9-overnight-real-supervision](iterations/20261101-v9-overnight-real-supervision/) | 5 | 0 | 4 | 1 | configure-git-webserver、filter-js-from-html |
| [20261101-v9-quality-step-supervision](iterations/20261101-v9-quality-step-supervision/) | 3 | 0 | 1 | 2 | custom-memory-heap-crash |
| [20261101-v9-runtime-quality-dev](iterations/20261101-v9-runtime-quality-dev/) | 8 | 4 | 2 | 2 | cobol-modernization、distribution-search |
| [20261102-v9-deepseek-dev](iterations/20261102-v9-deepseek-dev/) | 19 | 7 | 2 | 10 | build-cython-ext、build-pmars、build-pov-ray、filter-js-from-html、financial-document-processor、git-leak-recovery、hf-model-inference、mteb-leaderboard、pytorch-model-cli |
| [20261102-v9-multi-source](iterations/20261102-v9-multi-source/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261102-v9-task-links](iterations/20261102-v9-task-links/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-candidate-outcomes](iterations/20261103-v9-candidate-outcomes/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-cross-task-quality](iterations/20261103-v9-cross-task-quality/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-encoder-migration](iterations/20261103-v9-encoder-migration/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-independent-train](iterations/20261103-v9-independent-train/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-labels-and-learning](iterations/20261103-v9-labels-and-learning/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-local-relations](iterations/20261103-v9-local-relations/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-modify-quality](iterations/20261103-v9-modify-quality/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-offline-online](iterations/20261103-v9-offline-online/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-quality-supervision](iterations/20261103-v9-quality-supervision/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-separation-cost](iterations/20261103-v9-separation-cost/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-state-conditions](iterations/20261103-v9-state-conditions/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261103-v9-step010-transfer](iterations/20261103-v9-step010-transfer/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261104-v9-cross-task-relations](iterations/20261104-v9-cross-task-relations/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261104-v9-local-quality-learning](iterations/20261104-v9-local-quality-learning/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261104-v9-modify-candidates](iterations/20261104-v9-modify-candidates/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261104-v9-recover-modify](iterations/20261104-v9-recover-modify/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261104-v9-repair-quality](iterations/20261104-v9-repair-quality/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261105-v9-global-value](iterations/20261105-v9-global-value/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261105-v9-quality-action](iterations/20261105-v9-quality-action/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261106-v9-complete-opportunities](iterations/20261106-v9-complete-opportunities/) | 4 | 0 | 0 | 4 | fix-code-vulnerability、log-summary-date-ranges、nginx-request-logging |
| [20261106-v9-k3-real](iterations/20261106-v9-k3-real/) | 13 | 5 | 1 | 7 | extract-elf、git-leak-recovery |
| [20261106-v9-routing-granularity](iterations/20261106-v9-routing-granularity/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261107-v9-full-method](iterations/20261107-v9-full-method/) | 36 | 22 | 3 | 11 | break-filter-js-from-html、cancel-async-tasks、db-wal-recovery、openssl-selfsigned-cert、regex-log、sqlite-db-truncate |
| [20261107-v9-glm-development](iterations/20261107-v9-glm-development/) | 9 | 0 | 4 | 5 | circuit-fibsqrt |
| [20261107-v9-glm-high-4096](iterations/20261107-v9-glm-high-4096/) | 1 | 0 | 0 | 1 | circuit-fibsqrt |
| [20261108-v9-constraints-glm](iterations/20261108-v9-constraints-glm/) | 3 | 3 | 0 | 0 | constraints-scheduling |
| [20261108-v9-constraints-kev](iterations/20261108-v9-constraints-kev/) | 3 | 2 | 1 | 0 | constraints-scheduling |
| [20261108-v9-constraints-laya](iterations/20261108-v9-constraints-laya/) | 3 | 3 | 0 | 0 | constraints-scheduling |
| [20261108-v9-constraints-luna_high](iterations/20261108-v9-constraints-luna_high/) | 1 | 1 | 0 | 0 | constraints-scheduling |
| [20261108-v9-constraints-rule_sticky](iterations/20261108-v9-constraints-rule_sticky/) | 1 | 1 | 0 | 0 | constraints-scheduling |
| [20261108-v9-constraints-terra_high](iterations/20261108-v9-constraints-terra_high/) | 1 | 1 | 0 | 0 | constraints-scheduling |
| [20261108-v9-glm-json-development](iterations/20261108-v9-glm-json-development/) | 1 | 0 | 0 | 1 | git-multibranch |
| [20261108-v9-glm-tool-generation](iterations/20261108-v9-glm-tool-generation/) | 1 | 1 | 0 | 0 | configure-git-webserver |
| [20261108-v9-k3-development](iterations/20261108-v9-k3-development/) | 3 | 0 | 1 | 2 | git-multibranch |
| [20261108-v9-k3-network-recovery](iterations/20261108-v9-k3-network-recovery/) | 7 | 3 | 1 | 3 | git-multibranch |
| [20261108-v9-k3-training](iterations/20261108-v9-k3-training/) | — | — | — | — | 步骤/训练/编码/分析，见原目录 |
| [20261108-v9-kev-original-development](iterations/20261108-v9-kev-original-development/) | 1 | 0 | 1 | 0 | git-multibranch |
| [20261108-v9-kev-original-granularity](iterations/20261108-v9-kev-original-granularity/) | 2 | 0 | 2 | 0 | git-multibranch |
| [20261108-v9-kev-trained-development](iterations/20261108-v9-kev-trained-development/) | 4 | 0 | 2 | 2 | git-multibranch |
| [20261108-v9-laya-comparison](iterations/20261108-v9-laya-comparison/) | 9 | 2 | 0 | 7 | git-multibranch |
| [20261108-v9-laya-granularity](iterations/20261108-v9-laya-granularity/) | 2 | 1 | 1 | 0 | git-multibranch |
| [20261108-v9-laya-json-ablation](iterations/20261108-v9-laya-json-ablation/) | 8 | 5 | 1 | 2 | git-multibranch |
| [20261108-v9-polyglot-high-kev](iterations/20261108-v9-polyglot-high-kev/) | 3 | 1 | 2 | 0 | polyglot-c-py |
| [20261108-v9-polyglot-independent](iterations/20261108-v9-polyglot-independent/) | 6 | 1 | 2 | 3 | polyglot-c-py |
| [20261108-v9-polyglot-rule-control](iterations/20261108-v9-polyglot-rule-control/) | 1 | 0 | 0 | 1 | polyglot-c-py |
| [20261108-v9-query-independent](iterations/20261108-v9-query-independent/) | 3 | 0 | 0 | 3 | query-optimize |
| [20261108-v9-sanitize-independent](iterations/20261108-v9-sanitize-independent/) | 8 | 4 | 1 | 3 | sanitize-git-repo |
| [20261108-v9-sanitize-kev-device](iterations/20261108-v9-sanitize-kev-device/) | 2 | 0 | 0 | 2 | sanitize-git-repo |
| [20261108-v9-sanitize-kev-network](iterations/20261108-v9-sanitize-kev-network/) | 2 | 0 | 2 | 0 | sanitize-git-repo |
| [20261108-v9-sanitize-kev-runtime](iterations/20261108-v9-sanitize-kev-runtime/) | 2 | 0 | 0 | 2 | sanitize-git-repo |
| [20261108-v9-sanitize-kev-sdpa](iterations/20261108-v9-sanitize-kev-sdpa/) | 2 | 0 | 0 | 2 | sanitize-git-repo |
| [20261108-v9-text-editing-independent](iterations/20261108-v9-text-editing-independent/) | 8 | 0 | 5 | 3 | large-scale-text-editing |
