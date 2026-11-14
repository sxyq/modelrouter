# Terminal-Bench 2.0 · Joint selection paired continuation

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：213d4469。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共957个任务/策略/seed位置；已结束3，运行中0，未开始954，渠道档位不可用0。有效官方任务评分1/0为1/1，缺有效评分 1，原Verifier依赖失败0位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 3次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$0.04081750、教师$0.00000000，合计$0.04081750；1次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。uvx缺失且没有测试报告的尝试另列，不计入正常任务质量对照。

Harbor命令累计墙钟1790.523253秒，内含官方Trial累计1775.184661秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：1/87题已有结束记录；1题已结束全部3个固定/简单策略；0题已结束全部11个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批87题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 87题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 1 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 1 | 0 | 86 | 0 | UNKNOWN |
| luna_high | 1 | 1 | 0 | 1/1 = 100.00% | 1/87 | 1.15%—100.00% | 0 | 0 | 86 | 0 | 0.00109950 |
| terra_high | 1 | 0 | 1 | 0/1 = 0.00% | 1/87 | 0.00%—98.85% | 0 | 0 | 86 | 0 | 0.03971800 |
| laya_original_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_original_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_trained_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_trained_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_original_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_original_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_trained_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_trained_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |

实际执行跨度：2026-11-14T11:29:06.657325+00:00至2026-11-14T11:43:11.797185+00:00，845.139860秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/87；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入46,925、输出2,140 Token；1次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入0、输出0 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取7,680 Token；1次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求0次，短评实际输入Router 0次；同一短评可由多次决策消费。

Provider实际额外重试22次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 1 | 1 | 0 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.00242127 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.00463366 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01794657 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.00432028 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.03337800 / 0.00884055 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.01894490 / 0.01134179 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_low | 1 | 1/0 | 1 | 1/0 | 0.01114295 / 0.00107424 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.00624260 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_max | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| joint_vs_model_only | laya_trained_on → laya_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00779292 / 0.00143242 |
| joint_vs_model_only | laya_trained_on → laya_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00779292 / 0.00259735 |
| joint_vs_model_only | laya_trained_on → laya_trained_on_model_only_max | 2 | 2/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| joint_vs_model_only | kev_original_off → kev_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| joint_vs_model_only | kev_original_off → kev_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00186484 |
| joint_vs_model_only | kev_original_off → kev_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00180800 |
| joint_vs_model_only | kev_original_on → kev_original_on_model_only_low | 2 | 1/2 | 1 | 1/1 | 0.00174950 / 0.00171380 |
| joint_vs_model_only | kev_original_on → kev_original_on_model_only_high | 2 | 1/2 | 1 | 1/1 | 0.00174950 / 0.00348850 |
| joint_vs_model_only | kev_original_on → kev_original_on_model_only_max | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.00905588 |
| joint_vs_model_only | kev_trained_off → kev_trained_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03871960 |
| joint_vs_model_only | kev_trained_off → kev_trained_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.04624140 |
| joint_vs_model_only | kev_trained_off → kev_trained_off_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.26640480 |
| joint_vs_model_only | kev_trained_on → kev_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.01004740 / 0.03532380 |
| joint_vs_model_only | kev_trained_on → kev_trained_on_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03183710 / 0.05734710 |
| joint_vs_model_only | kev_trained_on → kev_trained_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.03183710 / 0.30910010 |

## 实际Router动作

以下登记实际选中模型及请求Native Effort；Model-only组固定档位、只选择模型。教师短评输入Router，不直接写入执行模型消息。

- laya_original_off: `{}`
- laya_original_on: `{}`
- laya_trained_off: `{}`
- laya_trained_on: `{}`
- kev_original_off: `{}`
- kev_original_on: `{}`
- kev_trained_off: `{}`
- kev_trained_on: `{}`
