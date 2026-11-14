# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束771，运行中2，未开始1363，渠道档位不可用0。有效官方任务评分1/0为204/103，缺有效评分 444，原Verifier依赖失败20位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 772次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$10.00096500、教师$0.12766856，合计$10.12863356；499次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。uvx缺失且没有测试报告的尝试另列，不计入正常任务质量对照。

Harbor命令累计墙钟345732.165178秒，内含官方Trial累计326348.682645秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：33/89题已有结束记录；32题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 33 | 8 | 6 | 8/14 = 57.14% | 14/89 | 8.99%—93.26% | 19 | 0 | 56 | 0 | 0.09127264 |
| laya_original_off_model_only_high | 33 | 12 | 1 | 12/13 = 92.31% | 13/89 | 13.48%—98.88% | 19 | 0 | 56 | 0 | 0.18790763 |
| laya_original_off_model_only_max | 33 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 20 | 0 | 56 | 0 | 0.36043247 |
| laya_original_on_model_only_low | 32 | 8 | 3 | 8/11 = 72.73% | 11/89 | 8.99%—96.63% | 21 | 1 | 56 | 0 | 0.07938784 |
| laya_original_on_model_only_high | 32 | 7 | 4 | 7/11 = 63.64% | 11/89 | 7.87%—95.51% | 21 | 1 | 56 | 0 | 0.14010994 |
| laya_original_on_model_only_max | 32 | 5 | 7 | 5/12 = 41.67% | 12/89 | 5.62%—92.13% | 19 | 0 | 57 | 0 | 0.31406417 |
| laya_trained_off_model_only_low | 32 | 5 | 8 | 5/13 = 38.46% | 13/89 | 5.62%—91.01% | 18 | 0 | 57 | 0 | 0.09251166 |
| laya_trained_off_model_only_high | 32 | 9 | 3 | 9/12 = 75.00% | 12/89 | 10.11%—96.63% | 20 | 0 | 57 | 0 | 0.13408000 |
| laya_trained_off_model_only_max | 32 | 10 | 2 | 10/12 = 83.33% | 12/89 | 11.24%—97.75% | 19 | 0 | 57 | 0 | 0.29406413 |
| laya_trained_on_model_only_low | 32 | 7 | 7 | 7/14 = 50.00% | 14/89 | 7.87%—92.13% | 18 | 0 | 57 | 0 | 0.12385786 |
| laya_trained_on_model_only_high | 32 | 8 | 6 | 8/14 = 57.14% | 14/89 | 8.99%—93.26% | 18 | 0 | 57 | 0 | 0.17250920 |
| laya_trained_on_model_only_max | 32 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 17 | 0 | 57 | 0 | 0.33145496 |
| kev_original_off_model_only_low | 32 | 3 | 8 | 3/11 = 27.27% | 11/89 | 3.37%—91.01% | 19 | 0 | 57 | 0 | 0.04006498 |
| kev_original_off_model_only_high | 32 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 17 | 0 | 57 | 0 | 0.09195786 |
| kev_original_off_model_only_max | 32 | 7 | 4 | 7/11 = 63.64% | 11/89 | 7.87%—95.51% | 21 | 0 | 57 | 0 | 0.18923442 |
| kev_original_on_model_only_low | 32 | 7 | 6 | 7/13 = 53.85% | 13/89 | 7.87%—93.26% | 17 | 0 | 57 | 0 | 0.04394334 |
| kev_original_on_model_only_high | 32 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 19 | 0 | 57 | 0 | 0.09551720 |
| kev_original_on_model_only_max | 32 | 11 | 4 | 11/15 = 73.33% | 15/89 | 12.36%—95.51% | 17 | 0 | 57 | 0 | 0.16199454 |
| kev_trained_off_model_only_low | 32 | 12 | 1 | 12/13 = 92.31% | 13/89 | 13.48%—98.88% | 17 | 0 | 57 | 0 | 0.82791820 |
| kev_trained_off_model_only_high | 32 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 16 | 0 | 57 | 0 | 1.04451420 |
| kev_trained_off_model_only_max | 32 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 17 | 0 | 57 | 0 | 2.01576830 |
| kev_trained_on_model_only_low | 32 | 10 | 1 | 10/11 = 90.91% | 11/89 | 11.24%—98.88% | 19 | 0 | 57 | 0 | 0.65618170 |
| kev_trained_on_model_only_high | 32 | 12 | 1 | 12/13 = 92.31% | 13/89 | 13.48%—98.88% | 18 | 0 | 57 | 0 | 0.76577290 |
| kev_trained_on_model_only_max | 32 | 10 | 3 | 10/13 = 76.92% | 13/89 | 11.24%—96.63% | 18 | 0 | 57 | 0 | 1.87411342 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-14T05:03:43.620616+00:00，179075.612665秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入49,167,838、输出2,737,944 Token；499次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入21,990,483、输出207,318 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取33,522,816 Token；755次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求521次，短评实际输入Router 936次；同一短评可由多次决策消费。

Provider实际额外重试1072次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 25 | 53 | 39 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 179 | 64 | 15 |
| ProviderResponseError | 0 | 0 | 25 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 8 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 10 | 9/7 | 9 | 9/7 | 0.06999839 / 0.06181525 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 10 | 7/4 | 7 | 5/4 | 0.04963456 / 0.02310309 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 11 | 7/7 | 10 | 7/7 | 0.06122932 / 0.07041596 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 11 | 8/10 | 11 | 8/10 | 0.62690190 / 0.53451290 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 10 | 6/8 | 10 | 6/8 | 0.05170833 / 0.05055970 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 12 | 5/6 | 9 | 4/5 | 0.04670381 / 0.03859234 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 9 | 2/3 | 9 | 2/3 | 0.02811444 / 0.02980372 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 11 | 10/10 | 8 | 7/7 | 0.45187860 / 0.42298660 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 9 | 6/4 | 5 | 3/4 | 0.12723654 / 0.11320391 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 12 | 10/7 | 4 | 4/4 | 0.05784453 / 0.06915825 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 10 | 6/7 | 10 | 6/7 | 0.12910238 / 0.10101274 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 11 | 8/9 | 8 | 7/6 | 1.42813030 / 1.00590080 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 10 | 9/8 | 8 | 8/7 | 0.04070626 / 0.05172124 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 9 | 6/4 | 7 | 5/4 | 0.04638130 / 0.04998589 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 10 | 6/7 | 10 | 6/7 | 0.05971182 / 0.66275490 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 9 | 5/8 | 6 | 3/5 | 0.05327118 / 0.36193960 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 11 | 6/4 | 11 | 6/4 | 0.05687323 / 0.04936929 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 10 | 7/4 | 8 | 6/4 | 0.04319690 / 0.02856484 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 7 | 2/6 | 7 | 2/6 | 0.02441948 / 0.38822020 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 9 | 4/8 | 7 | 3/6 | 0.02174312 / 0.38156410 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 9 | 6/8 | 4 | 3/4 | 0.09905990 / 0.05784453 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 11 | 5/6 | 5 | 3/4 | 0.13134045 / 0.10803510 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 9 | 5/4 | 7 | 3/4 | 0.10239260 / 1.11221770 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 12 | 9/9 | 8 | 6/6 | 0.08422284 / 1.00590080 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 78, "gpt-6-luna:low": 104}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 76, "gpt-6-luna:high": 134}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 255, "gpt-6-luna:max": 56}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 75, "gpt-6-luna:low": 77}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 40, "gpt-6-luna:high": 174}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 233, "gpt-6-luna:max": 26}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 70, "gpt-6-luna:low": 106}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 44, "gpt-6-luna:high": 165}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 275, "gpt-6-luna:max": 28}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 74, "gpt-6-luna:low": 118}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 47, "gpt-6-luna:high": 223}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 276, "gpt-6-luna:max": 42}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 121}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 204}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 214}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 119}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 191}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 206}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 178}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 188, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 212, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 163}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 176, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 244, "gpt-6-luna:max": 6}`
