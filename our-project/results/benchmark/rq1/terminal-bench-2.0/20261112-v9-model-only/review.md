# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束2107，运行中2，未开始27，渠道档位不可用0。有效官方任务评分1/0为379/223，缺有效评分 1473，原Verifier依赖失败32位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2108次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$44.35952744、教师$0.25782601，合计$44.61735345；2281次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1371719.754114秒，内含官方Trial累计1345796.569945秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：88/89题已有结束记录；87题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 88 | 10 | 9 | 10/19 = 52.63% | 19/89 | 11.24%—89.89% | 69 | 0 | 1 | 0 | 0.13827167 |
| laya_original_off_model_only_high | 88 | 14 | 4 | 14/18 = 77.78% | 18/89 | 15.73%—95.51% | 68 | 0 | 1 | 0 | 0.46251463 |
| laya_original_off_model_only_max | 88 | 15 | 9 | 15/24 = 62.50% | 24/89 | 16.85%—89.89% | 63 | 0 | 1 | 0 | 1.65034809 |
| laya_original_on_model_only_low | 88 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 73 | 0 | 1 | 0 | 0.14299404 |
| laya_original_on_model_only_high | 88 | 9 | 8 | 9/17 = 52.94% | 17/89 | 10.11%—91.01% | 71 | 0 | 1 | 0 | 0.23933430 |
| laya_original_on_model_only_max | 88 | 13 | 11 | 13/24 = 54.17% | 24/89 | 14.61%—87.64% | 63 | 0 | 1 | 0 | 1.64554615 |
| laya_trained_off_model_only_low | 88 | 7 | 11 | 7/18 = 38.89% | 18/89 | 7.87%—87.64% | 69 | 0 | 1 | 0 | 0.14370391 |
| laya_trained_off_model_only_high | 88 | 11 | 6 | 11/17 = 64.71% | 17/89 | 12.36%—93.26% | 71 | 0 | 1 | 0 | 0.38411949 |
| laya_trained_off_model_only_max | 88 | 15 | 9 | 15/24 = 62.50% | 24/89 | 16.85%—89.89% | 63 | 0 | 1 | 0 | 1.39475007 |
| laya_trained_on_model_only_low | 88 | 10 | 12 | 10/22 = 45.45% | 22/89 | 11.24%—86.52% | 65 | 0 | 1 | 0 | 0.20067250 |
| laya_trained_on_model_only_high | 88 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 69 | 0 | 1 | 0 | 0.35731302 |
| laya_trained_on_model_only_max | 88 | 19 | 10 | 19/29 = 65.52% | 29/89 | 21.35%—88.76% | 58 | 0 | 1 | 0 | 1.16828890 |
| kev_original_off_model_only_low | 88 | 5 | 13 | 5/18 = 27.78% | 18/89 | 5.62%—85.39% | 67 | 0 | 1 | 0 | 0.06820436 |
| kev_original_off_model_only_high | 88 | 11 | 6 | 11/17 = 64.71% | 17/89 | 12.36%—93.26% | 67 | 0 | 1 | 0 | 0.12089308 |
| kev_original_off_model_only_max | 88 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 71 | 0 | 1 | 0 | 0.25497354 |
| kev_original_on_model_only_low | 88 | 10 | 9 | 10/19 = 52.63% | 19/89 | 11.24%—89.89% | 66 | 0 | 1 | 0 | 0.06554620 |
| kev_original_on_model_only_high | 88 | 11 | 9 | 11/20 = 55.00% | 20/89 | 12.36%—89.89% | 66 | 0 | 1 | 0 | 0.16609855 |
| kev_original_on_model_only_max | 87 | 16 | 6 | 16/22 = 72.73% | 22/89 | 17.98%—93.26% | 64 | 1 | 1 | 0 | 0.23927868 |
| kev_trained_off_model_only_low | 88 | 34 | 16 | 34/50 = 68.00% | 50/89 | 38.20%—82.02% | 35 | 0 | 1 | 0 | 3.84374500 |
| kev_trained_off_model_only_high | 88 | 30 | 16 | 30/46 = 65.22% | 46/89 | 33.71%—82.02% | 40 | 0 | 1 | 0 | 5.08808140 |
| kev_trained_off_model_only_max | 87 | 25 | 10 | 25/35 = 71.43% | 35/89 | 28.09%—88.76% | 52 | 1 | 1 | 0 | 10.28898900 |
| kev_trained_on_model_only_low | 87 | 29 | 14 | 29/43 = 67.44% | 43/89 | 32.58%—84.27% | 42 | 0 | 2 | 0 | 3.09433870 |
| kev_trained_on_model_only_high | 87 | 29 | 10 | 29/39 = 74.36% | 39/89 | 32.58%—88.76% | 47 | 0 | 2 | 0 | 4.54069835 |
| kev_trained_on_model_only_max | 87 | 26 | 6 | 26/32 = 81.25% | 32/89 | 29.21%—93.26% | 54 | 0 | 2 | 0 | 8.91864982 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-20T08:57:50.588104+00:00，711522.580153秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入245,776,454、输出7,910,598 Token；2,264次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入63,018,967、输出666,224 Token；79次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取203,241,612 Token；2846次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求1413次，短评实际输入Router 1523次；同一短评可由多次决策消费。

Provider实际额外重试9872次；已记录技术恢复0次，涉及0个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度191次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|
| gpt-6.1-terra | max | xhigh | 6 |

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 42 | 79 | 299 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 10 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 337 | 136 | 34 |
| NonZeroAgentExitCodeError | 0 | 0 | 733 |
| OutputTokenExceededError | 0 | 8 | 2 |
| ProviderResponseError | 0 | 0 | 26 |
| RemoteDisconnected | 0 | 0 | 2 |
| RuntimeError | 0 | 0 | 14 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 25 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 14 | 10/8 | 11 | 10/8 | 0.08617201 / 0.06919549 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 13 | 9/6 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 16 | 10/10 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 33 | 24/26 | 13 | 10/12 | 0.66151930 / 0.58588480 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 14 | 7/9 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 16 | 6/7 | 12 | 5/6 | 0.05340857 / 0.04677343 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 14 | 4/6 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 40 | 27/29 | 11 | 9/9 | 0.69389400 / 0.64950570 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 16 | 11/9 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 19 | 13/11 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 15 | 9/10 | 15 | 9/10 | 0.19307260 / 0.14507666 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 26 | 21/22 | 9 | 8/7 | 1.40086640 / 1.25152050 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 14 | 10/9 | 11 | 9/8 | 0.05885040 / 0.07103216 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 13 | 8/6 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 14 | 8/10 | 13 | 8/10 | 0.07696922 / 0.84692090 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 12 | 6/11 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 15 | 7/5 | 13 | 7/5 | 0.06187902 / 0.05304593 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 14 | 9/6 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 12 | 2/9 | 12 | 2/9 | 0.04807856 / 0.79889000 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 13 | 5/11 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 14 | 9/11 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 16 | 10/9 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 11 | 6/5 | 9 | 4/5 | 0.12340202 / 1.72878820 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 15 | 11/13 | 9 | 7/7 | 0.07880220 / 1.25152050 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 151, "gpt-6-luna:low": 204}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 191, "gpt-6-luna:high": 250}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 913, "gpt-6-luna:max": 122}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 159, "gpt-6-luna:low": 177}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 115, "gpt-6-luna:high": 275}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 853, "gpt-6-luna:max": 104}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 175, "gpt-6-luna:low": 192}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 177, "gpt-6-luna:high": 278}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 939, "gpt-6-luna:max": 94}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 183, "gpt-6-luna:low": 204}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 147, "gpt-6-luna:high": 341}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 827, "gpt-6-luna:max": 120}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 240}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 317}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 341}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 219}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 338}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 340}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 808, "gpt-6-luna:low": 3}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 855, "gpt-6-luna:high": 8}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 1045, "gpt-6-luna:max": 15}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 785, "gpt-6-luna:low": 3}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 805, "gpt-6-luna:high": 10}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 978, "gpt-6-luna:max": 15}`
