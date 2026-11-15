# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束920，运行中2，未开始1214，渠道档位不可用0。有效官方任务评分1/0为259/119，缺有效评分 510，原Verifier依赖失败32位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 921次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$12.69628171、教师$0.16105536，合计$12.85733707；549次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟508998.989405秒，内含官方Trial累计488819.107865秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：39/89题已有结束记录；38题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 39 | 10 | 7 | 10/17 = 58.82% | 17/89 | 11.24%—92.13% | 22 | 0 | 50 | 0 | 0.10964401 |
| laya_original_off_model_only_high | 39 | 14 | 2 | 14/16 = 87.50% | 16/89 | 15.73%—97.75% | 21 | 0 | 50 | 0 | 0.21035639 |
| laya_original_off_model_only_max | 39 | 9 | 5 | 9/14 = 64.29% | 14/89 | 10.11%—94.38% | 24 | 0 | 50 | 0 | 0.42371429 |
| laya_original_on_model_only_low | 39 | 9 | 4 | 9/13 = 69.23% | 13/89 | 10.11%—95.51% | 26 | 0 | 50 | 0 | 0.09454912 |
| laya_original_on_model_only_high | 39 | 9 | 5 | 9/14 = 64.29% | 14/89 | 10.11%—94.38% | 25 | 0 | 50 | 0 | 0.15750156 |
| laya_original_on_model_only_max | 39 | 7 | 7 | 7/14 = 50.00% | 14/89 | 7.87%—92.13% | 24 | 0 | 50 | 0 | 0.38697043 |
| laya_trained_off_model_only_low | 39 | 7 | 10 | 7/17 = 41.18% | 17/89 | 7.87%—88.76% | 21 | 0 | 50 | 0 | 0.11928450 |
| laya_trained_off_model_only_high | 39 | 11 | 4 | 11/15 = 73.33% | 15/89 | 12.36%—95.51% | 24 | 0 | 50 | 0 | 0.16874722 |
| laya_trained_off_model_only_max | 38 | 12 | 2 | 12/14 = 85.71% | 14/89 | 13.48%—97.75% | 23 | 1 | 50 | 0 | 0.35269500 |
| laya_trained_on_model_only_low | 38 | 8 | 8 | 8/16 = 50.00% | 16/89 | 8.99%—91.01% | 21 | 1 | 50 | 0 | 0.13583911 |
| laya_trained_on_model_only_high | 38 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 21 | 0 | 51 | 0 | 0.19291865 |
| laya_trained_on_model_only_max | 38 | 13 | 5 | 13/18 = 72.22% | 18/89 | 14.61%—94.38% | 19 | 0 | 51 | 0 | 0.40229299 |
| kev_original_off_model_only_low | 38 | 5 | 11 | 5/16 = 31.25% | 16/89 | 5.62%—87.64% | 19 | 0 | 51 | 0 | 0.06552124 |
| kev_original_off_model_only_high | 38 | 11 | 5 | 11/16 = 68.75% | 16/89 | 12.36%—94.38% | 18 | 0 | 51 | 0 | 0.11666204 |
| kev_original_off_model_only_max | 38 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 22 | 0 | 51 | 0 | 0.24149420 |
| kev_original_on_model_only_low | 38 | 10 | 7 | 10/17 = 58.82% | 17/89 | 11.24%—92.13% | 18 | 0 | 51 | 0 | 0.06132480 |
| kev_original_on_model_only_high | 38 | 11 | 6 | 11/17 = 64.71% | 17/89 | 12.36%—93.26% | 19 | 0 | 51 | 0 | 0.12977086 |
| kev_original_on_model_only_max | 38 | 15 | 5 | 15/20 = 75.00% | 20/89 | 16.85%—94.38% | 17 | 0 | 51 | 0 | 0.21389634 |
| kev_trained_off_model_only_low | 38 | 15 | 1 | 15/16 = 93.75% | 16/89 | 16.85%—98.88% | 19 | 0 | 51 | 0 | 1.11932420 |
| kev_trained_off_model_only_high | 38 | 14 | 5 | 14/19 = 73.68% | 19/89 | 15.73%—94.38% | 17 | 0 | 51 | 0 | 1.27585120 |
| kev_trained_off_model_only_max | 38 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 22 | 0 | 51 | 0 | 2.74248370 |
| kev_trained_on_model_only_low | 38 | 12 | 1 | 12/13 = 92.31% | 13/89 | 13.48%—98.88% | 23 | 0 | 51 | 0 | 0.85032070 |
| kev_trained_on_model_only_high | 38 | 14 | 0 | 14/14 = 100.00% | 14/89 | 15.73%—100.00% | 23 | 0 | 51 | 0 | 0.84453220 |
| kev_trained_on_model_only_max | 38 | 13 | 2 | 13/15 = 86.67% | 15/89 | 14.61%—97.75% | 22 | 0 | 51 | 0 | 2.44164232 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-15T07:26:35.233622+00:00，274047.225671秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入59,565,868、输出3,417,697 Token；549次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入28,131,886、输出265,302 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取40,102,016 Token；899次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求667次，短评实际输入Router 1179次；同一短评可由多次决策消费。

Provider实际额外重试2209次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 33 | 49 | 93 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 226 | 70 | 34 |
| ProviderResponseError | 0 | 0 | 26 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 19 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 12 | 10/8 | 10 | 10/8 | 0.07385039 / 0.06678743 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 12 | 9/6 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 15 | 10/10 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 12 | 10/12 | 12 | 10/12 | 0.53019130 / 0.47509760 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 12 | 7/9 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 14 | 6/7 | 11 | 5/6 | 0.05257473 / 0.04428788 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 13 | 4/6 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 13 | 12/12 | 10 | 9/9 | 0.58627620 / 0.52109830 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 10 | 7/5 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 14 | 12/9 | 5 | 5/5 | 0.06801799 / 0.08142353 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 14 | 9/10 | 14 | 9/10 | 0.17959326 / 0.13394224 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 12 | 9/11 | 8 | 8/7 | 1.18588170 / 1.09372290 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 12 | 10/9 | 10 | 9/8 | 0.04652878 / 0.05653962 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 11 | 8/6 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 13 | 8/10 | 13 | 8/10 | 0.07696922 / 0.84692090 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 10 | 6/10 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 13 | 7/5 | 12 | 7/5 | 0.06009329 / 0.05221209 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 11 | 8/5 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 10 | 2/9 | 10 | 2/9 | 0.04539544 / 0.55768660 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 11 | 5/10 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 10 | 7/9 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 12 | 7/7 | 5 | 4/4 | 0.13574549 / 0.10956684 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 10 | 6/5 | 8 | 4/5 | 0.10992268 / 1.51380350 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 14 | 11/12 | 8 | 7/7 | 0.06766778 / 1.09372290 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 89, "gpt-6-luna:low": 153}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 82, "gpt-6-luna:high": 183}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 304, "gpt-6-luna:max": 99}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 81, "gpt-6-luna:low": 128}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 42, "gpt-6-luna:high": 220}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 270, "gpt-6-luna:max": 71}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 108, "gpt-6-luna:low": 147}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 64, "gpt-6-luna:high": 219}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 323, "gpt-6-luna:max": 57}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 79, "gpt-6-luna:low": 147}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 51, "gpt-6-luna:high": 270}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 324, "gpt-6-luna:max": 70}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 181}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 253}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 275}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 157}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 252}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 263}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 234}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 242, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 276, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 219}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 200, "gpt-6-luna:high": 3}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 286, "gpt-6-luna:max": 6}`
