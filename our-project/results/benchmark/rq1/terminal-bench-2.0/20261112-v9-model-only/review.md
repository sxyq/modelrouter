# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束651，运行中0，未开始1485，渠道档位不可用0。有效官方任务评分1/0为128/68，无官方Reward 435，原Verifier依赖失败20位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 652次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$7.71928326、教师$0.08556414，合计$7.80484740；472次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟257492.417010秒，内含官方Trial累计238712.970474秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：28/89题已有结束记录；27题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 28 | 6 | 3 | 6/9 = 66.67% | 9/89 | 6.74%—96.63% | 19 | 0 | 61 | 0 | 0.04859112 |
| laya_original_off_model_only_high | 28 | 8 | 1 | 8/9 = 88.89% | 9/89 | 8.99%—98.88% | 18 | 0 | 61 | 0 | 0.11209945 |
| laya_original_off_model_only_max | 28 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 21 | 0 | 61 | 0 | 0.28162216 |
| laya_original_on_model_only_low | 27 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 21 | 0 | 62 | 0 | 0.04510080 |
| laya_original_on_model_only_high | 27 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 21 | 0 | 62 | 0 | 0.07675551 |
| laya_original_on_model_only_max | 27 | 1 | 6 | 1/7 = 14.29% | 7/89 | 1.12%—93.26% | 19 | 0 | 62 | 0 | 0.20086026 |
| laya_trained_off_model_only_low | 27 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 19 | 0 | 62 | 0 | 0.06109001 |
| laya_trained_off_model_only_high | 27 | 5 | 2 | 5/7 = 71.43% | 7/89 | 5.62%—97.75% | 20 | 0 | 62 | 0 | 0.09150044 |
| laya_trained_off_model_only_max | 27 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 20 | 0 | 62 | 0 | 0.22165120 |
| laya_trained_on_model_only_low | 27 | 3 | 6 | 3/9 = 33.33% | 9/89 | 3.37%—93.26% | 18 | 0 | 62 | 0 | 0.09131987 |
| laya_trained_on_model_only_high | 27 | 6 | 3 | 6/9 = 66.67% | 9/89 | 6.74%—96.63% | 18 | 0 | 62 | 0 | 0.12594554 |
| laya_trained_on_model_only_max | 27 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 17 | 0 | 62 | 0 | 0.23679728 |
| kev_original_off_model_only_low | 27 | 2 | 4 | 2/6 = 33.33% | 6/89 | 2.25%—95.51% | 19 | 0 | 62 | 0 | 0.02054876 |
| kev_original_off_model_only_high | 27 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 17 | 0 | 62 | 0 | 0.06358356 |
| kev_original_off_model_only_max | 27 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 20 | 0 | 62 | 0 | 0.10513454 |
| kev_original_on_model_only_low | 27 | 5 | 3 | 5/8 = 62.50% | 8/89 | 5.62%—96.63% | 17 | 0 | 62 | 0 | 0.02414508 |
| kev_original_on_model_only_high | 27 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 19 | 0 | 62 | 0 | 0.05572900 |
| kev_original_on_model_only_max | 27 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 17 | 0 | 62 | 0 | 0.10099870 |
| kev_trained_off_model_only_low | 27 | 9 | 1 | 9/10 = 90.00% | 10/89 | 10.11%—98.88% | 15 | 0 | 62 | 0 | 0.64007460 |
| kev_trained_off_model_only_high | 27 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 14 | 0 | 62 | 0 | 0.86913800 |
| kev_trained_off_model_only_max | 27 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 15 | 0 | 62 | 0 | 1.73586190 |
| kev_trained_on_model_only_low | 27 | 7 | 1 | 7/8 = 87.50% | 8/89 | 7.87%—98.88% | 17 | 0 | 62 | 0 | 0.50757940 |
| kev_trained_on_model_only_high | 27 | 8 | 1 | 8/9 = 88.89% | 9/89 | 8.99%—98.88% | 17 | 0 | 62 | 0 | 0.56879190 |
| kev_trained_on_model_only_max | 27 | 7 | 2 | 7/9 = 77.78% | 9/89 | 7.87%—97.75% | 17 | 0 | 62 | 0 | 1.51992832 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-13T16:14:14.522028+00:00，132906.514077秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入36,443,539、输出1,939,331 Token；472次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入15,756,305、输出159,408 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取26,065,472 Token；657次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求368次，短评实际输入Router 664次；同一短评可由多次决策消费。

Provider实际额外重试621次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 20 | 41 | 33 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 108 | 41 | 15 |
| ProviderResponseError | 0 | 0 | 25 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 5 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 6 | 5/4 | 5 | 5/4 | 0.01213406 / 0.02191035 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 5 | 3/2 | 3 | 2/2 | 0.01549592 / 0.00651924 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 6 | 3/3 | 5 | 3/3 | 0.03285502 / 0.03062776 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 8 | 5/7 | 8 | 5/7 | 0.45152570 / 0.38154840 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 6 | 4/5 | 6 | 4/5 | 0.01413069 / 0.01802118 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 6 | 4/2 | 4 | 3/1 | 0.01528216 / 0.00605435 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 4 | 1/1 | 4 | 1/1 | 0.00859822 / 0.01000546 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 8 | 7/7 | 6 | 5/5 | 0.28748620 / 0.30273920 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 3 | 3/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 6 | 5/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 6 | 3/3 | 6 | 3/3 | 0.06980580 / 0.06280564 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 8 | 6/6 | 6 | 5/4 | 1.16010090 / 0.78282670 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 5 | 4/4 | 4 | 4/4 | 0.00958271 / 0.01758260 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 4 | 3/2 | 3 | 2/2 | 0.00647640 / 0.00657563 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 7 | 4/4 | 7 | 4/4 | 0.03607562 / 0.48737870 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 5 | 2/4 | 3 | 1/2 | 0.02284530 / 0.20897510 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 6 | 4/3 | 6 | 4/3 | 0.01413069 / 0.01794764 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 5 | 4/1 | 4 | 3/1 | 0.01065838 / 0.00605435 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 4 | 2/3 | 4 | 2/3 | 0.00824988 / 0.20037660 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 6 | 4/5 | 5 | 3/4 | 0.01151846 / 0.26131670 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 3 | 3/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 6 | 1/2 | 1 | 0/0 | 0.05244604 / 0.03887685 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 6 | 3/2 | 5 | 2/2 | 0.06324538 / 0.84418830 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 8 | 5/6 | 6 | 4/4 | 0.05745004 / 0.78282670 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 38, "gpt-6-luna:low": 76}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 45, "gpt-6-luna:high": 94}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 189, "gpt-6-luna:max": 48}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 51, "gpt-6-luna:low": 44}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 26, "gpt-6-luna:high": 112}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 165, "gpt-6-luna:max": 21}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 49, "gpt-6-luna:low": 61}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 35, "gpt-6-luna:high": 102}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 210, "gpt-6-luna:max": 16}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 57, "gpt-6-luna:low": 71}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 41, "gpt-6-luna:high": 169}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 203, "gpt-6-luna:max": 17}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 85}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 155}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 144}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 81}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 134}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 147}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 145}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 158, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 180, "gpt-6-luna:max": 2}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 131}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 138, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 203, "gpt-6-luna:max": 6}`
