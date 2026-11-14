# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束836，运行中2，未开始1298，渠道档位不可用0。有效官方任务评分1/0为215/108，缺有效评分 482，原Verifier依赖失败31位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 837次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$10.94777330、教师$0.13573376，合计$11.08350706；529次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟407602.683444秒，内含官方Trial累计387869.293803秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：35/89题已有结束记录；34题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 35 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 20 | 0 | 54 | 0 | 0.09280340 |
| laya_original_off_model_only_high | 35 | 13 | 1 | 13/14 = 92.86% | 14/89 | 14.61%—98.88% | 20 | 0 | 54 | 0 | 0.19114585 |
| laya_original_off_model_only_max | 35 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 22 | 0 | 54 | 0 | 0.36043247 |
| laya_original_on_model_only_low | 35 | 8 | 3 | 8/11 = 72.73% | 11/89 | 8.99%—96.63% | 24 | 0 | 54 | 0 | 0.08087480 |
| laya_original_on_model_only_high | 35 | 7 | 4 | 7/11 = 63.64% | 11/89 | 7.87%—95.51% | 24 | 0 | 54 | 0 | 0.14010994 |
| laya_original_on_model_only_max | 35 | 5 | 6 | 5/11 = 45.45% | 11/89 | 5.62%—93.26% | 23 | 0 | 54 | 0 | 0.31406417 |
| laya_trained_off_model_only_low | 35 | 5 | 8 | 5/13 = 38.46% | 13/89 | 5.62%—91.01% | 21 | 0 | 54 | 0 | 0.09251166 |
| laya_trained_off_model_only_high | 35 | 9 | 3 | 9/12 = 75.00% | 12/89 | 10.11%—96.63% | 23 | 0 | 54 | 0 | 0.13408000 |
| laya_trained_off_model_only_max | 35 | 10 | 2 | 10/12 = 83.33% | 12/89 | 11.24%—97.75% | 22 | 0 | 54 | 0 | 0.29406413 |
| laya_trained_on_model_only_low | 35 | 7 | 7 | 7/14 = 50.00% | 14/89 | 7.87%—92.13% | 20 | 0 | 54 | 0 | 0.12464162 |
| laya_trained_on_model_only_high | 35 | 8 | 6 | 8/14 = 57.14% | 14/89 | 8.99%—93.26% | 20 | 0 | 54 | 0 | 0.17820914 |
| laya_trained_on_model_only_max | 35 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 19 | 0 | 54 | 0 | 0.33145496 |
| kev_original_off_model_only_low | 35 | 3 | 10 | 3/13 = 23.08% | 13/89 | 3.37%—88.76% | 19 | 0 | 54 | 0 | 0.05855860 |
| kev_original_off_model_only_high | 35 | 8 | 5 | 8/13 = 61.54% | 13/89 | 8.99%—94.38% | 18 | 0 | 54 | 0 | 0.10745926 |
| kev_original_off_model_only_max | 35 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 22 | 0 | 54 | 0 | 0.20227736 |
| kev_original_on_model_only_low | 35 | 7 | 7 | 7/14 = 50.00% | 14/89 | 7.87%—92.13% | 18 | 0 | 54 | 0 | 0.04896082 |
| kev_original_on_model_only_high | 35 | 8 | 6 | 8/14 = 57.14% | 14/89 | 8.99%—93.26% | 19 | 0 | 54 | 0 | 0.11651790 |
| kev_original_on_model_only_max | 35 | 12 | 5 | 12/17 = 70.59% | 17/89 | 13.48%—94.38% | 17 | 0 | 54 | 0 | 0.19804206 |
| kev_trained_off_model_only_low | 35 | 14 | 1 | 14/15 = 93.33% | 15/89 | 15.73%—98.88% | 17 | 0 | 54 | 0 | 0.92437420 |
| kev_trained_off_model_only_high | 35 | 12 | 5 | 12/17 = 70.59% | 17/89 | 13.48%—94.38% | 16 | 0 | 54 | 0 | 1.12103240 |
| kev_trained_off_model_only_max | 34 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 19 | 1 | 54 | 0 | 2.21780410 |
| kev_trained_on_model_only_low | 34 | 11 | 1 | 11/12 = 91.67% | 12/89 | 12.36%—98.88% | 20 | 1 | 54 | 0 | 0.68841500 |
| kev_trained_on_model_only_high | 34 | 13 | 0 | 13/13 = 100.00% | 13/89 | 14.61%—100.00% | 20 | 0 | 55 | 0 | 0.80029450 |
| kev_trained_on_model_only_max | 34 | 12 | 2 | 12/14 = 85.71% | 14/89 | 13.48%—97.75% | 19 | 0 | 55 | 0 | 2.26537872 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-14T17:20:35.354115+00:00，223287.346164秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入50,561,572、输出2,974,233 Token；529次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入23,074,972、输出227,665 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取34,051,200 Token；785次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求550次，短评实际输入Router 976次；同一短评可由多次决策消费。

Provider实际额外重试1894次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 27 | 47 | 78 |
| EnvironmentStartTimeoutError | 0 | 0 | 5 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 188 | 61 | 33 |
| ProviderResponseError | 0 | 0 | 26 |
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
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 12 | 7/7 | 11 | 7/7 | 0.07202408 / 0.08044738 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 11 | 9/11 | 11 | 9/11 | 0.46405990 / 0.43085990 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 10 | 6/8 | 10 | 6/8 | 0.05170833 / 0.05055970 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 12 | 5/6 | 9 | 4/5 | 0.04670381 / 0.03859234 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 10 | 2/3 | 10 | 2/3 | 0.03501886 / 0.03220890 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 12 | 11/11 | 9 | 8/8 | 0.51326580 / 0.45521990 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 8 | 6/4 | 4 | 3/4 | 0.06801397 / 0.10891387 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 12 | 10/7 | 4 | 4/4 | 0.05784453 / 0.06915825 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 11 | 6/7 | 11 | 6/7 | 0.14037642 / 0.11808796 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 11 | 8/10 | 7 | 7/6 | 0.92315090 / 0.91745930 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 10 | 9/8 | 8 | 8/7 | 0.04070626 / 0.05172124 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 9 | 6/4 | 7 | 5/4 | 0.04638130 / 0.04998589 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 11 | 6/8 | 11 | 6/8 | 0.07050658 / 0.69210210 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 9 | 5/9 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 11 | 6/4 | 11 | 6/4 | 0.05687323 / 0.04936929 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 10 | 7/4 | 8 | 6/4 | 0.04319690 / 0.02856484 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 9 | 2/8 | 9 | 2/8 | 0.04237714 / 0.48467620 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 10 | 4/9 | 8 | 3/7 | 0.02414830 / 0.41379740 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 9 | 6/8 | 4 | 3/4 | 0.09905990 / 0.05784453 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 10 | 5/5 | 4 | 3/3 | 0.12705041 / 0.09730156 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 9 | 5/4 | 7 | 3/4 | 0.10414232 / 1.25107270 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 13 | 10/11 | 7 | 6/6 | 0.06304742 / 0.91745930 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 79, "gpt-6-luna:low": 109}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 77, "gpt-6-luna:high": 141}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 257, "gpt-6-luna:max": 56}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 78, "gpt-6-luna:low": 82}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 42, "gpt-6-luna:high": 174}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 235, "gpt-6-luna:max": 26}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 72, "gpt-6-luna:low": 106}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 46, "gpt-6-luna:high": 165}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 277, "gpt-6-luna:max": 28}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 76, "gpt-6-luna:low": 122}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 50, "gpt-6-luna:high": 232}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 279, "gpt-6-luna:max": 42}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 150}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 222}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 228}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 132}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 215}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 235}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 194}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 205, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 229, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 171}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 184, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 270, "gpt-6-luna:max": 6}`
