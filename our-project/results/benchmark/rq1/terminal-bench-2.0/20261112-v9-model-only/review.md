# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束729，运行中2，未开始1405，渠道档位不可用0。有效官方任务评分1/0为180/92，无官方Reward 437，原Verifier依赖失败20位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 730次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$9.28420169、教师$0.11444026，合计$9.39864195；491次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟320019.110992秒，内含官方Trial累计300846.901514秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：31/89题已有结束记录；30题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 31 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 19 | 0 | 58 | 0 | 0.07487999 |
| laya_original_off_model_only_high | 31 | 11 | 1 | 11/12 = 91.67% | 12/89 | 12.36%—98.88% | 18 | 0 | 58 | 0 | 0.16186457 |
| laya_original_off_model_only_max | 31 | 7 | 3 | 7/10 = 70.00% | 10/89 | 7.87%—96.63% | 20 | 0 | 58 | 0 | 0.32943571 |
| laya_original_on_model_only_low | 31 | 7 | 3 | 7/10 = 70.00% | 10/89 | 7.87%—96.63% | 21 | 0 | 58 | 0 | 0.07392240 |
| laya_original_on_model_only_high | 31 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 21 | 0 | 58 | 0 | 0.13210992 |
| laya_original_on_model_only_max | 31 | 4 | 7 | 4/11 = 36.36% | 11/89 | 4.49%—92.13% | 19 | 0 | 58 | 0 | 0.27406589 |
| laya_trained_off_model_only_low | 31 | 5 | 7 | 5/12 = 41.67% | 12/89 | 5.62%—92.13% | 18 | 0 | 58 | 0 | 0.08843014 |
| laya_trained_off_model_only_high | 31 | 9 | 2 | 9/11 = 81.82% | 11/89 | 10.11%—97.75% | 20 | 0 | 58 | 0 | 0.12617000 |
| laya_trained_off_model_only_max | 31 | 9 | 2 | 9/11 = 81.82% | 11/89 | 10.11%—97.75% | 19 | 0 | 58 | 0 | 0.27568143 |
| laya_trained_on_model_only_low | 30 | 6 | 6 | 6/12 = 50.00% | 12/89 | 6.74%—93.26% | 18 | 1 | 58 | 0 | 0.10867758 |
| laya_trained_on_model_only_high | 30 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 18 | 1 | 58 | 0 | 0.16265475 |
| laya_trained_on_model_only_max | 30 | 8 | 5 | 8/13 = 61.54% | 13/89 | 8.99%—94.38% | 17 | 0 | 59 | 0 | 0.29290825 |
| kev_original_off_model_only_low | 30 | 3 | 6 | 3/9 = 33.33% | 9/89 | 3.37%—93.26% | 19 | 0 | 59 | 0 | 0.02635366 |
| kev_original_off_model_only_high | 30 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 17 | 0 | 59 | 0 | 0.07371600 |
| kev_original_off_model_only_max | 30 | 6 | 3 | 6/9 = 66.67% | 9/89 | 6.74%—96.63% | 21 | 0 | 59 | 0 | 0.15309938 |
| kev_original_on_model_only_low | 30 | 6 | 5 | 6/11 = 54.55% | 11/89 | 6.74%—94.38% | 17 | 0 | 59 | 0 | 0.03307356 |
| kev_original_on_model_only_high | 30 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 19 | 0 | 59 | 0 | 0.07713354 |
| kev_original_on_model_only_max | 30 | 9 | 4 | 9/13 = 69.23% | 13/89 | 10.11%—95.51% | 17 | 0 | 59 | 0 | 0.13799796 |
| kev_trained_off_model_only_low | 30 | 11 | 1 | 11/12 = 91.67% | 12/89 | 12.36%—98.88% | 16 | 0 | 59 | 0 | 0.76026200 |
| kev_trained_off_model_only_high | 30 | 9 | 5 | 9/14 = 64.29% | 14/89 | 10.11%—94.38% | 15 | 0 | 59 | 0 | 0.97427980 |
| kev_trained_off_model_only_max | 30 | 8 | 6 | 8/14 = 57.14% | 14/89 | 8.99%—93.26% | 16 | 0 | 59 | 0 | 1.94074650 |
| kev_trained_on_model_only_low | 30 | 9 | 1 | 9/10 = 90.00% | 10/89 | 10.11%—98.88% | 18 | 0 | 59 | 0 | 0.60868250 |
| kev_trained_on_model_only_high | 30 | 11 | 1 | 11/12 = 91.67% | 12/89 | 12.36%—98.88% | 17 | 0 | 59 | 0 | 0.72058970 |
| kev_trained_on_model_only_max | 30 | 9 | 3 | 9/12 = 75.00% | 12/89 | 10.11%—96.63% | 17 | 0 | 59 | 0 | 1.79190672 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-14T01:29:24.995850+00:00，166216.987899秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入44,627,980、输出2,525,750 Token；491次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入20,001,142、输出190,415 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取31,053,632 Token；717次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求475次，短评实际输入Router 845次；同一短评可由多次决策消费。

Provider实际额外重试840次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 25 | 52 | 32 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 155 | 54 | 15 |
| ProviderResponseError | 0 | 0 | 25 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 8 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 9 | 8/6 | 8 | 8/6 | 0.06189918 / 0.05381523 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 8 | 6/3 | 5 | 4/3 | 0.02839320 / 0.01324864 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 9 | 5/5 | 8 | 5/5 | 0.04298746 / 0.05203230 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 10 | 7/9 | 10 | 7/9 | 0.55666750 / 0.48932970 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 9 | 6/7 | 9 | 6/7 | 0.04041956 / 0.04509426 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 10 | 5/5 | 7 | 4/4 | 0.03443025 / 0.02341206 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 7 | 2/2 | 7 | 2/2 | 0.01440312 / 0.01893394 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 10 | 9/9 | 7 | 6/6 | 0.38422240 / 0.37548740 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 8 | 5/3 | 4 | 2/3 | 0.10703612 / 0.07320563 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 10 | 8/5 | 2 | 2/2 | 0.02336841 / 0.03061154 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 8 | 5/5 | 8 | 5/5 | 0.09296734 / 0.07701616 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 10 | 7/8 | 7 | 6/5 | 1.35310850 / 0.92369410 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 9 | 8/8 | 7 | 7/7 | 0.03260705 / 0.04381124 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 7 | 4/3 | 5 | 3/3 | 0.02866090 / 0.04013144 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 9 | 5/6 | 9 | 5/6 | 0.04346892 / 0.59252050 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 8 | 4/7 | 5 | 2/4 | 0.03720824 / 0.31675640 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 10 | 6/4 | 10 | 6/4 | 0.04558446 / 0.04528777 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 8 | 5/3 | 6 | 4/3 | 0.03103693 / 0.01338456 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 6 | 2/5 | 6 | 2/5 | 0.01171744 / 0.32056400 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 8 | 4/7 | 6 | 3/5 | 0.01339136 / 0.33406490 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 8 | 5/7 | 3 | 2/3 | 0.07885948 / 0.03946183 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 9 | 3/4 | 3 | 1/2 | 0.08117173 / 0.06948839 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 8 | 5/3 | 6 | 3/3 | 0.07347292 / 1.03719590 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 11 | 8/8 | 7 | 5/5 | 0.06632478 / 0.92369410 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 59, "gpt-6-luna:low": 94}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 58, "gpt-6-luna:high": 122}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 230, "gpt-6-luna:max": 54}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 74, "gpt-6-luna:low": 68}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 39, "gpt-6-luna:high": 166}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 212, "gpt-6-luna:max": 25}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 68, "gpt-6-luna:low": 92}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 43, "gpt-6-luna:high": 152}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 259, "gpt-6-luna:max": 28}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 74, "gpt-6-luna:low": 94}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 46, "gpt-6-luna:high": 203}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 238, "gpt-6-luna:max": 37}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 104}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 184}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 190}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 100}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 171}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 185}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 167}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 177, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 203, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 154}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 166, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 233, "gpt-6-luna:max": 6}`
