# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束1899，运行中1，未开始236，渠道档位不可用0。有效官方任务评分1/0为356/189，无官方Reward 1334，原Verifier依赖失败20位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 1900次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$33.31907916、教师$0.17324836，合计$33.49232752；1899次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟1164917.984943秒，内含官方Trial累计1139999.892540秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：80/89题已有结束记录；78题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 80 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 62 | 0 | 9 | 0 | 0.12400307 |
| laya_original_off_model_only_high | 80 | 14 | 3 | 14/17 = 82.35% | 17/89 | 15.73%—96.63% | 62 | 0 | 9 | 0 | 0.24002793 |
| laya_original_off_model_only_max | 80 | 15 | 7 | 15/22 = 68.18% | 22/89 | 16.85%—92.13% | 57 | 0 | 9 | 0 | 1.00382741 |
| laya_original_on_model_only_low | 80 | 10 | 4 | 10/14 = 71.43% | 14/89 | 11.24%—95.51% | 66 | 0 | 9 | 0 | 0.10745769 |
| laya_original_on_model_only_high | 79 | 9 | 5 | 9/14 = 64.29% | 14/89 | 10.11%—94.38% | 65 | 0 | 10 | 0 | 0.17947291 |
| laya_original_on_model_only_max | 79 | 12 | 11 | 12/23 = 52.17% | 23/89 | 13.48%—87.64% | 55 | 0 | 10 | 0 | 0.80880745 |
| laya_trained_off_model_only_low | 79 | 7 | 10 | 7/17 = 41.18% | 17/89 | 7.87%—88.76% | 61 | 0 | 10 | 0 | 0.12548431 |
| laya_trained_off_model_only_high | 79 | 11 | 5 | 11/16 = 68.75% | 16/89 | 12.36%—94.38% | 63 | 0 | 10 | 0 | 0.19047790 |
| laya_trained_off_model_only_max | 79 | 14 | 4 | 14/18 = 77.78% | 18/89 | 15.73%—95.51% | 60 | 0 | 10 | 0 | 0.87670924 |
| laya_trained_on_model_only_low | 79 | 10 | 11 | 10/21 = 47.62% | 21/89 | 11.24%—87.64% | 58 | 0 | 10 | 0 | 0.15454584 |
| laya_trained_on_model_only_high | 79 | 10 | 7 | 10/17 = 58.82% | 17/89 | 11.24%—92.13% | 62 | 0 | 10 | 0 | 0.21917176 |
| laya_trained_on_model_only_max | 79 | 19 | 8 | 19/27 = 70.37% | 27/89 | 21.35%—91.01% | 52 | 0 | 10 | 0 | 0.99690743 |
| kev_original_off_model_only_low | 79 | 5 | 13 | 5/18 = 27.78% | 18/89 | 5.62%—85.39% | 59 | 0 | 10 | 0 | 0.06820436 |
| kev_original_off_model_only_high | 79 | 11 | 7 | 11/18 = 61.11% | 18/89 | 12.36%—92.13% | 58 | 0 | 10 | 0 | 0.12089308 |
| kev_original_off_model_only_max | 79 | 10 | 7 | 10/17 = 58.82% | 17/89 | 11.24%—92.13% | 62 | 0 | 10 | 0 | 0.25497354 |
| kev_original_on_model_only_low | 79 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 59 | 0 | 10 | 0 | 0.06332390 |
| kev_original_on_model_only_high | 79 | 11 | 7 | 11/18 = 61.11% | 18/89 | 12.36%—92.13% | 60 | 0 | 10 | 0 | 0.13393332 |
| kev_original_on_model_only_max | 79 | 15 | 6 | 15/21 = 71.43% | 21/89 | 16.85%—93.26% | 58 | 0 | 10 | 0 | 0.22503076 |
| kev_trained_off_model_only_low | 79 | 30 | 12 | 30/42 = 71.43% | 42/89 | 33.71%—86.52% | 35 | 0 | 10 | 0 | 3.19096840 |
| kev_trained_off_model_only_high | 79 | 28 | 12 | 28/40 = 70.00% | 40/89 | 31.46%—86.52% | 38 | 0 | 10 | 0 | 4.26500640 |
| kev_trained_off_model_only_max | 79 | 21 | 11 | 21/32 = 65.62% | 32/89 | 23.60%—87.64% | 47 | 0 | 10 | 0 | 7.63047220 |
| kev_trained_on_model_only_low | 79 | 26 | 9 | 26/35 = 74.29% | 35/89 | 29.21%—89.89% | 42 | 0 | 10 | 0 | 2.49178590 |
| kev_trained_on_model_only_high | 79 | 26 | 8 | 26/34 = 76.47% | 34/89 | 29.21%—91.01% | 44 | 0 | 10 | 0 | 3.57039580 |
| kev_trained_on_model_only_max | 78 | 22 | 6 | 22/28 = 78.57% | 28/89 | 24.72%—93.26% | 49 | 1 | 10 | 0 | 6.45044692 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-19T03:57:41.744835+00:00，607113.736884秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入153,445,905、输出5,855,899 Token；1,882次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入49,632,828、输出540,550 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取119,081,846 Token；2398次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求1124次，短评实际输入Router 1316次；同一短评可由多次决策消费。

Provider实际额外重试9289次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|
| gpt-6.1-terra | max | xhigh | 6 |

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 40 | 74 | 290 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 10 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 316 | 108 | 34 |
| NonZeroAgentExitCodeError | 0 | 0 | 593 |
| OutputTokenExceededError | 0 | 7 | 0 |
| ProviderResponseError | 0 | 0 | 26 |
| RemoteDisconnected | 0 | 0 | 2 |
| RuntimeError | 0 | 0 | 14 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 25 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 13 | 10/8 | 11 | 10/8 | 0.08617201 / 0.06919549 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 13 | 9/6 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 17 | 10/10 | 14 | 9/9 | 0.08020612 / 0.09885380 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 29 | 22/23 | 14 | 10/12 | 0.85370850 / 0.72405940 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 13 | 7/9 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 15 | 6/7 | 12 | 5/6 | 0.05340857 / 0.04677343 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 14 | 4/6 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 33 | 23/26 | 11 | 9/9 | 0.69389400 / 0.64950570 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 15 | 11/9 | 6 | 4/5 | 0.14630306 / 0.14156861 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 16 | 12/11 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 16 | 9/11 | 16 | 9/11 | 0.19325540 / 0.16165436 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 22 | 16/18 | 10 | 8/7 | 1.90584580 / 1.33996200 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 13 | 10/9 | 11 | 9/8 | 0.05885040 / 0.07103216 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 11 | 8/6 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 15 | 8/11 | 14 | 8/11 | 0.07973912 / 0.89409190 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 12 | 6/10 | 7 | 3/6 | 0.06330260 / 0.39646120 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 14 | 7/5 | 13 | 7/5 | 0.06187902 / 0.05304593 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 13 | 9/6 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 12 | 2/9 | 12 | 2/9 | 0.04807856 / 0.79889000 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 12 | 5/10 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 12 | 9/11 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 16 | 9/10 | 7 | 4/5 | 0.15940915 / 0.13294538 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 12 | 5/5 | 11 | 4/5 | 0.13310914 / 1.79196900 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 15 | 10/12 | 10 | 7/7 | 0.09997762 / 1.33996200 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 119, "gpt-6-luna:low": 197}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 107, "gpt-6-luna:high": 242}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 688, "gpt-6-luna:max": 111}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 109, "gpt-6-luna:low": 170}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 63, "gpt-6-luna:high": 262}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 567, "gpt-6-luna:max": 91}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 134, "gpt-6-luna:low": 185}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 88, "gpt-6-luna:high": 271}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 656, "gpt-6-luna:max": 91}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 119, "gpt-6-luna:low": 197}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 71, "gpt-6-luna:high": 329}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 686, "gpt-6-luna:max": 113}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 233}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 310}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 333}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 205}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 308}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 321}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 654, "gpt-6-luna:low": 1}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 681, "gpt-6-luna:high": 5}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 743, "gpt-6-luna:max": 11}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 627, "gpt-6-luna:low": 2}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 609, "gpt-6-luna:high": 8}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 720, "gpt-6-luna:max": 12}`
