# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束1163，运行中2，未开始971，渠道档位不可用0。有效官方任务评分1/0为279/159，缺有效评分 693，原Verifier依赖失败32位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 1164次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$15.49742486、教师$0.17324836，合计$15.67067322；844次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟674882.351813秒，内含官方Trial累计653487.286144秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：49/89题已有结束记录；48题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 49 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 31 | 0 | 40 | 0 | 0.12287418 |
| laya_original_off_model_only_high | 49 | 14 | 3 | 14/17 = 82.35% | 17/89 | 15.73%—96.63% | 30 | 0 | 40 | 0 | 0.23985883 |
| laya_original_off_model_only_max | 49 | 13 | 6 | 13/19 = 68.42% | 19/89 | 14.61%—93.26% | 29 | 0 | 40 | 0 | 0.59687840 |
| laya_original_on_model_only_low | 49 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 34 | 0 | 40 | 0 | 0.10234138 |
| laya_original_on_model_only_high | 49 | 9 | 7 | 9/16 = 56.25% | 16/89 | 10.11%—92.13% | 33 | 0 | 40 | 0 | 0.17931817 |
| laya_original_on_model_only_max | 49 | 11 | 8 | 11/19 = 57.89% | 19/89 | 12.36%—91.01% | 29 | 0 | 40 | 0 | 0.56929964 |
| laya_trained_off_model_only_low | 49 | 7 | 11 | 7/18 = 38.89% | 18/89 | 7.87%—87.64% | 30 | 0 | 40 | 0 | 0.12536714 |
| laya_trained_off_model_only_high | 49 | 11 | 5 | 11/16 = 68.75% | 16/89 | 12.36%—94.38% | 33 | 0 | 40 | 0 | 0.19047790 |
| laya_trained_off_model_only_max | 49 | 13 | 5 | 13/18 = 72.22% | 18/89 | 14.61%—94.38% | 30 | 0 | 40 | 0 | 0.47002367 |
| laya_trained_on_model_only_low | 49 | 9 | 10 | 9/19 = 47.37% | 19/89 | 10.11%—88.76% | 29 | 0 | 40 | 0 | 0.14960861 |
| laya_trained_on_model_only_high | 49 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 30 | 0 | 40 | 0 | 0.21917176 |
| laya_trained_on_model_only_max | 48 | 16 | 7 | 16/23 = 69.57% | 23/89 | 17.98%—92.13% | 24 | 1 | 40 | 0 | 0.59193156 |
| kev_original_off_model_only_low | 48 | 5 | 13 | 5/18 = 27.78% | 18/89 | 5.62%—85.39% | 27 | 1 | 40 | 0 | 0.06820436 |
| kev_original_off_model_only_high | 48 | 11 | 6 | 11/17 = 64.71% | 17/89 | 12.36%—93.26% | 27 | 0 | 41 | 0 | 0.12089308 |
| kev_original_off_model_only_max | 48 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 31 | 0 | 41 | 0 | 0.25497354 |
| kev_original_on_model_only_low | 48 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 27 | 0 | 41 | 0 | 0.06332390 |
| kev_original_on_model_only_high | 48 | 11 | 7 | 11/18 = 61.11% | 18/89 | 12.36%—92.13% | 28 | 0 | 41 | 0 | 0.13393332 |
| kev_original_on_model_only_max | 48 | 15 | 6 | 15/21 = 71.43% | 21/89 | 16.85%—93.26% | 26 | 0 | 41 | 0 | 0.22503076 |
| kev_trained_off_model_only_low | 48 | 16 | 5 | 16/21 = 76.19% | 21/89 | 17.98%—94.38% | 24 | 0 | 41 | 0 | 1.42015620 |
| kev_trained_off_model_only_high | 48 | 15 | 8 | 15/23 = 65.22% | 23/89 | 16.85%—91.01% | 23 | 0 | 41 | 0 | 1.59943800 |
| kev_trained_off_model_only_max | 48 | 11 | 8 | 11/19 = 57.89% | 19/89 | 12.36%—91.01% | 29 | 0 | 41 | 0 | 3.30141680 |
| kev_trained_on_model_only_low | 48 | 14 | 3 | 14/17 = 82.35% | 17/89 | 15.73%—96.63% | 29 | 0 | 41 | 0 | 1.11098150 |
| kev_trained_on_model_only_high | 48 | 15 | 1 | 15/16 = 93.75% | 16/89 | 16.85%—98.88% | 31 | 0 | 41 | 0 | 1.02339420 |
| kev_trained_on_model_only_max | 48 | 14 | 4 | 14/18 = 77.78% | 18/89 | 15.73%—95.51% | 29 | 0 | 41 | 0 | 2.79177632 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-16T06:45:29.730422+00:00，357981.722471秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入75,792,562、输出4,174,573 Token；844次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入35,156,103、输出319,266 Token；42次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取53,198,912 Token；1311次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求824次，短评实际输入Router 1316次；同一短评可由多次决策消费。

Provider实际额外重试3385次；已记录技术恢复0次，涉及0个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度105次；其中0个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 36 | 72 | 140 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 10 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 243 | 87 | 34 |
| NonZeroAgentExitCodeError | 0 | 0 | 129 |
| ProviderResponseError | 0 | 0 | 26 |
| RemoteDisconnected | 0 | 0 | 2 |
| RuntimeError | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 22 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 13 | 10/8 | 11 | 10/8 | 0.08617201 / 0.06919549 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 13 | 9/6 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 16 | 10/10 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 14 | 11/13 | 13 | 10/12 | 0.66151930 / 0.58588480 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 13 | 7/9 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 16 | 6/7 | 12 | 5/6 | 0.05340857 / 0.04677343 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 14 | 4/6 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 17 | 13/14 | 11 | 9/9 | 0.69389400 / 0.64950570 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 13 | 10/8 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 16 | 12/9 | 5 | 5/5 | 0.06801799 / 0.08142353 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 15 | 9/10 | 15 | 9/10 | 0.19307260 / 0.14507666 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 14 | 10/12 | 9 | 8/7 | 1.40086640 / 1.25152050 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 13 | 10/9 | 11 | 9/8 | 0.05885040 / 0.07103216 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 13 | 8/6 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 14 | 8/10 | 13 | 8/10 | 0.07696922 / 0.84692090 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 11 | 6/10 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 14 | 7/5 | 13 | 7/5 | 0.06187902 / 0.05304593 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 14 | 8/6 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 12 | 2/9 | 12 | 2/9 | 0.04807856 / 0.79889000 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 12 | 5/10 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 12 | 8/10 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 15 | 9/9 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 11 | 6/5 | 9 | 4/5 | 0.12340202 / 1.72878820 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 15 | 11/12 | 9 | 7/7 | 0.07880220 / 1.25152050 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 111, "gpt-6-luna:low": 171}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 104, "gpt-6-luna:high": 213}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 469, "gpt-6-luna:max": 105}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 92, "gpt-6-luna:low": 146}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 60, "gpt-6-luna:high": 235}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 419, "gpt-6-luna:max": 84}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 128, "gpt-6-luna:low": 161}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 86, "gpt-6-luna:high": 244}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 447, "gpt-6-luna:max": 84}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 106, "gpt-6-luna:low": 173}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 69, "gpt-6-luna:high": 301}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 483, "gpt-6-luna:max": 107}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 203}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 280}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 303}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 175}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 278}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 291}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 312}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 324, "gpt-6-luna:high": 3}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 347, "gpt-6-luna:max": 5}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 294}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 259, "gpt-6-luna:high": 4}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 344, "gpt-6-luna:max": 6}`
