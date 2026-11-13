# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束553，运行中2，未开始1581，渠道档位不可用0。有效官方任务评分1/0为102/50，无官方Reward 387，原Verifier依赖失败14位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 553次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$4.36044239、教师$0.04889386，合计$4.40933625；420次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟173093.491540秒，内含官方Trial累计155849.857725秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：24/89题已有结束记录；23题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 24 | 5 | 2 | 5/7 = 71.43% | 7/89 | 5.62%—97.75% | 17 | 0 | 65 | 0 | 0.02040097 |
| laya_original_off_model_only_high | 23 | 6 | 1 | 6/7 = 85.71% | 7/89 | 6.74%—98.88% | 16 | 1 | 65 | 0 | 0.05758778 |
| laya_original_off_model_only_max | 23 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 17 | 1 | 65 | 0 | 0.16818913 |
| laya_original_on_model_only_low | 23 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 17 | 0 | 66 | 0 | 0.01862298 |
| laya_original_on_model_only_high | 23 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 17 | 0 | 66 | 0 | 0.03731772 |
| laya_original_on_model_only_max | 23 | 1 | 4 | 1/5 = 20.00% | 5/89 | 1.12%—95.51% | 17 | 0 | 66 | 0 | 0.11821408 |
| laya_trained_off_model_only_low | 23 | 3 | 3 | 3/6 = 50.00% | 6/89 | 3.37%—96.63% | 16 | 0 | 66 | 0 | 0.02041656 |
| laya_trained_off_model_only_high | 23 | 4 | 1 | 4/5 = 80.00% | 5/89 | 4.49%—98.88% | 18 | 0 | 66 | 0 | 0.03501166 |
| laya_trained_off_model_only_max | 23 | 4 | 1 | 4/5 = 80.00% | 5/89 | 4.49%—98.88% | 17 | 0 | 66 | 0 | 0.13238755 |
| laya_trained_on_model_only_low | 23 | 2 | 5 | 2/7 = 28.57% | 7/89 | 2.25%—94.38% | 16 | 0 | 66 | 0 | 0.01490573 |
| laya_trained_on_model_only_high | 23 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 17 | 0 | 66 | 0 | 0.04887982 |
| laya_trained_on_model_only_max | 23 | 5 | 2 | 5/7 = 71.43% | 7/89 | 5.62%—97.75% | 16 | 0 | 66 | 0 | 0.13009733 |
| kev_original_off_model_only_low | 23 | 2 | 4 | 2/6 = 33.33% | 6/89 | 2.25%—95.51% | 16 | 0 | 66 | 0 | 0.01188046 |
| kev_original_off_model_only_high | 23 | 3 | 2 | 3/5 = 60.00% | 5/89 | 3.37%—97.75% | 16 | 0 | 66 | 0 | 0.02872938 |
| kev_original_off_model_only_max | 23 | 3 | 2 | 3/5 = 60.00% | 5/89 | 3.37%—97.75% | 18 | 0 | 66 | 0 | 0.05902048 |
| kev_original_on_model_only_low | 23 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 16 | 0 | 66 | 0 | 0.01366898 |
| kev_original_on_model_only_high | 23 | 3 | 3 | 3/6 = 50.00% | 6/89 | 3.37%—96.63% | 17 | 0 | 66 | 0 | 0.02302024 |
| kev_original_on_model_only_max | 23 | 4 | 4 | 4/8 = 50.00% | 8/89 | 4.49%—95.51% | 15 | 0 | 66 | 0 | 0.05264140 |
| kev_trained_off_model_only_low | 23 | 6 | 0 | 6/6 = 100.00% | 6/89 | 6.74%—100.00% | 15 | 0 | 66 | 0 | 0.39478020 |
| kev_trained_off_model_only_high | 23 | 5 | 3 | 5/8 = 62.50% | 8/89 | 5.62%—96.63% | 14 | 0 | 66 | 0 | 0.52974950 |
| kev_trained_off_model_only_max | 23 | 5 | 4 | 5/9 = 55.56% | 9/89 | 5.62%—95.51% | 14 | 0 | 66 | 0 | 0.93190850 |
| kev_trained_on_model_only_low | 23 | 6 | 0 | 6/6 = 100.00% | 6/89 | 6.74%—100.00% | 15 | 0 | 66 | 0 | 0.23862660 |
| kev_trained_on_model_only_high | 23 | 7 | 0 | 7/7 = 100.00% | 7/89 | 7.87%—100.00% | 15 | 0 | 66 | 0 | 0.29629060 |
| kev_trained_on_model_only_max | 23 | 6 | 1 | 6/7 = 85.71% | 7/89 | 6.74%—98.88% | 15 | 0 | 66 | 0 | 1.02698860 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-13T03:25:01.383377+00:00，86753.375426秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入17,444,729、输出1,273,364 Token；420次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入10,345,572、输出108,153 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取12,765,248 Token；530次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求241次，短评实际输入Router 372次；同一短评可由多次决策消费。

Provider实际额外重试54次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 18 | 29 | 8 |
| HTTPError | 0 | 0 | 7 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 84 | 35 | 1 |
| ProviderResponseError | 0 | 0 | 23 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 340 |
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
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 3 | 2/1 | 2 | 1/1 | 0.01321976 / 0.00397828 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 4 | 2/2 | 3 | 2/2 | 0.00877920 / 0.01260878 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 6 | 4/6 | 6 | 4/6 | 0.20869510 / 0.19437920 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 6 | 4/5 | 6 | 4/5 | 0.01413069 / 0.01802118 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 5 | 3/1 | 4 | 3/1 | 0.01528216 / 0.00605435 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 4 | 1/2 | 4 | 1/2 | 0.00518098 / 0.00757072 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 6 | 6/6 | 4 | 4/4 | 0.13499900 / 0.12560060 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 4 | 3/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 5 | 4/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 5 | 3/2 | 4 | 2/2 | 0.03773048 / 0.03769772 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 7 | 5/6 | 4 | 4/3 | 0.57303250 / 0.59702770 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 5 | 4/4 | 4 | 4/4 | 0.00958271 / 0.01758260 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 4 | 3/2 | 3 | 2/2 | 0.00647640 / 0.00657563 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 5 | 3/4 | 5 | 3/4 | 0.01199980 / 0.25949080 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 5 | 2/5 | 3 | 1/3 | 0.00728468 / 0.11076550 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 6 | 4/3 | 6 | 4/3 | 0.01413069 / 0.01794764 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 5 | 4/1 | 4 | 3/1 | 0.01065838 / 0.00605435 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 4 | 2/4 | 4 | 2/4 | 0.00483264 / 0.11269280 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 5 | 4/5 | 4 | 3/4 | 0.00736992 / 0.12560060 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 4 | 3/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 4 | 1/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 5 | 3/2 | 3 | 1/2 | 0.03117006 / 0.29663050 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 7 | 4/6 | 5 | 3/4 | 0.03038656 / 0.70368314 |
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
| joint_vs_model_only | kev_original_off → kev_original_off_model_only_low | 1 | 1/0 | 1 | 1/0 | 0.00152466 / 0.00000000 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 12, "gpt-6-luna:low": 55}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 26, "gpt-6-luna:high": 66}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 150, "gpt-6-luna:max": 13}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 26, "gpt-6-luna:low": 33}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 11, "gpt-6-luna:high": 81}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 122, "gpt-6-luna:max": 15}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 15, "gpt-6-luna:low": 48}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 9, "gpt-6-luna:high": 86}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 140, "gpt-6-luna:max": 15}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 14, "gpt-6-luna:low": 50}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 12, "gpt-6-luna:high": 134}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 124, "gpt-6-luna:max": 12}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 57}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 91}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 88}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 54}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 74}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 84}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 111}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 118, "gpt-6-luna:high": 1}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 128, "gpt-6-luna:max": 1}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 94}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 99, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 154, "gpt-6-luna:max": 5}`
