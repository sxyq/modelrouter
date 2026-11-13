# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束672，运行中1，未开始1463，渠道档位不可用0。有效官方任务评分1/0为142/73，无官方Reward 437，原Verifier依赖失败20位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 673次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$8.48398341、教师$0.09527584，合计$8.57925925；477次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟273825.970569秒，内含官方Trial累计254940.270252秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：28/89题已有结束记录；28题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 28 | 6 | 3 | 6/9 = 66.67% | 9/89 | 6.74%—96.63% | 19 | 1 | 60 | 0 | 0.04859112 |
| laya_original_off_model_only_high | 28 | 8 | 1 | 8/9 = 88.89% | 9/89 | 8.99%—98.88% | 18 | 0 | 61 | 0 | 0.11209945 |
| laya_original_off_model_only_max | 28 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 21 | 0 | 61 | 0 | 0.28162216 |
| laya_original_on_model_only_low | 28 | 5 | 1 | 5/6 = 83.33% | 6/89 | 5.62%—98.88% | 22 | 0 | 61 | 0 | 0.04684932 |
| laya_original_on_model_only_high | 28 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 22 | 0 | 61 | 0 | 0.10020504 |
| laya_original_on_model_only_max | 28 | 1 | 7 | 1/8 = 12.50% | 8/89 | 1.12%—92.13% | 19 | 0 | 61 | 0 | 0.20515030 |
| laya_trained_off_model_only_low | 28 | 4 | 4 | 4/8 = 50.00% | 8/89 | 4.49%—95.51% | 19 | 0 | 61 | 0 | 0.06557843 |
| laya_trained_off_model_only_high | 28 | 6 | 2 | 6/8 = 75.00% | 8/89 | 6.74%—97.75% | 20 | 0 | 61 | 0 | 0.09926452 |
| laya_trained_off_model_only_max | 28 | 6 | 1 | 6/7 = 85.71% | 7/89 | 6.74%—98.88% | 20 | 0 | 61 | 0 | 0.23237830 |
| laya_trained_on_model_only_low | 28 | 4 | 6 | 4/10 = 40.00% | 10/89 | 4.49%—93.26% | 18 | 0 | 61 | 0 | 0.10134737 |
| laya_trained_on_model_only_high | 28 | 6 | 4 | 6/10 = 60.00% | 10/89 | 6.74%—95.51% | 18 | 0 | 61 | 0 | 0.12909894 |
| laya_trained_on_model_only_max | 28 | 7 | 4 | 7/11 = 63.64% | 11/89 | 7.87%—95.51% | 17 | 0 | 61 | 0 | 0.24753082 |
| kev_original_off_model_only_low | 28 | 2 | 5 | 2/7 = 28.57% | 7/89 | 2.25%—94.38% | 19 | 0 | 61 | 0 | 0.02204488 |
| kev_original_off_model_only_high | 28 | 5 | 3 | 5/8 = 62.50% | 8/89 | 5.62%—96.63% | 17 | 0 | 61 | 0 | 0.06854410 |
| kev_original_off_model_only_max | 28 | 5 | 3 | 5/8 = 62.50% | 8/89 | 5.62%—96.63% | 20 | 0 | 61 | 0 | 0.11536208 |
| kev_original_on_model_only_low | 28 | 5 | 4 | 5/9 = 55.56% | 9/89 | 5.62%—95.51% | 17 | 0 | 61 | 0 | 0.02601798 |
| kev_original_on_model_only_high | 28 | 5 | 3 | 5/8 = 62.50% | 8/89 | 5.62%—96.63% | 19 | 0 | 61 | 0 | 0.06433448 |
| kev_original_on_model_only_max | 28 | 7 | 4 | 7/11 = 63.64% | 11/89 | 7.87%—95.51% | 17 | 0 | 61 | 0 | 0.10987344 |
| kev_trained_off_model_only_low | 28 | 10 | 1 | 10/11 = 90.91% | 11/89 | 11.24%—98.88% | 15 | 0 | 61 | 0 | 0.73681080 |
| kev_trained_off_model_only_high | 28 | 8 | 5 | 8/13 = 61.54% | 13/89 | 8.99%—94.38% | 14 | 0 | 61 | 0 | 0.95118940 |
| kev_trained_off_model_only_max | 28 | 8 | 5 | 8/13 = 61.54% | 13/89 | 8.99%—94.38% | 15 | 0 | 61 | 0 | 1.92886950 |
| kev_trained_on_model_only_low | 28 | 8 | 1 | 8/9 = 88.89% | 9/89 | 8.99%—98.88% | 17 | 0 | 61 | 0 | 0.58032760 |
| kev_trained_on_model_only_high | 28 | 9 | 1 | 9/10 = 90.00% | 10/89 | 10.11%—98.88% | 17 | 0 | 61 | 0 | 0.64537350 |
| kev_trained_on_model_only_max | 28 | 8 | 2 | 8/10 = 80.00% | 10/89 | 8.99%—97.75% | 17 | 0 | 61 | 0 | 1.66079572 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-13T19:04:30.140718+00:00，143122.132767秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入39,391,805、输出2,037,253 Token；477次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入17,296,296、输出177,982 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取27,874,496 Token；672次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求410次，短评实际输入Router 742次；同一短评可由多次决策消费。

Provider实际额外重试627次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 20 | 42 | 33 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 122 | 45 | 15 |
| ProviderResponseError | 0 | 0 | 25 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 7 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 6 | 5/4 | 5 | 5/4 | 0.01213406 / 0.02191035 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 6 | 4/2 | 4 | 3/2 | 0.02326000 / 0.00967264 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 7 | 4/4 | 6 | 4/4 | 0.03781556 / 0.03923324 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 9 | 6/8 | 9 | 6/8 | 0.53357710 / 0.45813000 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 6 | 4/5 | 6 | 4/5 | 0.01413069 / 0.01802118 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 7 | 4/3 | 5 | 3/2 | 0.01977058 / 0.01608185 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 5 | 1/1 | 5 | 1/1 | 0.01009434 / 0.01187836 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 9 | 8/8 | 7 | 6/6 | 0.38422240 / 0.37548740 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 4 | 3/0 | 1 | 0/0 | 0.05922257 / 0.00429004 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 7 | 6/4 | 1 | 1/1 | 0.01072710 / 0.01073354 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 7 | 4/4 | 7 | 4/4 | 0.08003334 / 0.07168038 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 9 | 7/7 | 7 | 6/5 | 1.35310850 / 0.92369410 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 6 | 5/5 | 5 | 5/5 | 0.02072777 / 0.02534668 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 4 | 3/2 | 3 | 2/2 | 0.00647640 / 0.00657563 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 8 | 5/5 | 8 | 5/5 | 0.04103616 / 0.56943010 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 6 | 3/5 | 4 | 2/3 | 0.03145078 / 0.28555670 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 7 | 4/3 | 7 | 4/3 | 0.01929559 / 0.02243606 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 5 | 4/1 | 4 | 3/1 | 0.01065838 / 0.00605435 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 5 | 2/4 | 5 | 2/4 | 0.00974600 / 0.29711280 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 7 | 4/6 | 6 | 3/5 | 0.01339136 / 0.33406490 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 4 | 3/4 | 1 | 0/1 | 0.05922257 / 0.01072710 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 7 | 1/3 | 2 | 0/1 | 0.05673608 / 0.04961039 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 7 | 4/3 | 6 | 3/3 | 0.07347292 / 1.03719590 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 9 | 6/7 | 7 | 5/5 | 0.06632478 / 0.92369410 |
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
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 51, "gpt-6-luna:low": 50}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 27, "gpt-6-luna:high": 136}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 166, "gpt-6-luna:max": 25}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 49, "gpt-6-luna:low": 71}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 35, "gpt-6-luna:high": 123}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 220, "gpt-6-luna:max": 27}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 62, "gpt-6-luna:low": 90}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 41, "gpt-6-luna:high": 179}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 206, "gpt-6-luna:max": 37}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 94}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 174}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 170}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 88}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 156}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 167}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 160}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 172, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 199, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 147}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 153, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 220, "gpt-6-luna:max": 6}`
