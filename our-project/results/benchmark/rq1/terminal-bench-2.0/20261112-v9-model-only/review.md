# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束481，运行中1，未开始1654，渠道档位不可用0。固定组已报告档位不符另列后，官方Reward 1/0为71/17，无官方Reward 379；Router组保留实际任务Reward及内部请求/返回档位差异。

已保存原Harbor Trial 481次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$2.68240498、教师$0.02447496，合计$2.70687994；399次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟102546.581764秒，内含官方Trial累计96611.368042秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：21/89题已有结束记录；89题已结束全部0个固定/简单策略；20题已结束全部24个策略。批次先执行固定阶段，再执行Router阶段。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 21 | 4 | 1 | 4/5 = 80.00% | 5/89 | 4.49%—98.88% | 16 | 0 | 68 | 0 | 0.01733381 |
| laya_original_off_model_only_high | 20 | 4 | 0 | 4/4 = 100.00% | 4/89 | 4.49%—100.00% | 16 | 1 | 68 | 0 | 0.01645444 |
| laya_original_off_model_only_max | 20 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 17 | 0 | 69 | 0 | 0.08265952 |
| laya_original_on_model_only_low | 20 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 17 | 0 | 69 | 0 | 0.00614945 |
| laya_original_on_model_only_high | 20 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 17 | 0 | 69 | 0 | 0.02319749 |
| laya_original_on_model_only_max | 20 | 1 | 1 | 1/2 = 50.00% | 2/89 | 1.12%—98.88% | 17 | 0 | 69 | 0 | 0.05795456 |
| laya_trained_off_model_only_low | 20 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 16 | 0 | 69 | 0 | 0.00602260 |
| laya_trained_off_model_only_high | 20 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 18 | 0 | 69 | 0 | 0.01424962 |
| laya_trained_off_model_only_max | 20 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 16 | 0 | 69 | 0 | 0.07580352 |
| laya_trained_on_model_only_low | 20 | 2 | 2 | 2/4 = 50.00% | 4/89 | 2.25%—97.75% | 16 | 0 | 69 | 0 | 0.00775781 |
| laya_trained_on_model_only_high | 20 | 4 | 0 | 4/4 = 100.00% | 4/89 | 4.49%—100.00% | 16 | 0 | 69 | 0 | 0.02734770 |
| laya_trained_on_model_only_max | 20 | 4 | 1 | 4/5 = 80.00% | 5/89 | 4.49%—98.88% | 15 | 0 | 69 | 0 | 0.07689552 |
| kev_original_off_model_only_low | 20 | 1 | 2 | 1/3 = 33.33% | 3/89 | 1.12%—97.75% | 16 | 0 | 69 | 0 | 0.00669948 |
| kev_original_off_model_only_high | 20 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 16 | 0 | 69 | 0 | 0.01956396 |
| kev_original_off_model_only_max | 20 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 18 | 0 | 69 | 0 | 0.02309800 |
| kev_original_on_model_only_low | 20 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 16 | 0 | 69 | 0 | 0.00781206 |
| kev_original_on_model_only_high | 20 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 17 | 0 | 69 | 0 | 0.01105482 |
| kev_original_on_model_only_max | 20 | 3 | 2 | 3/5 = 60.00% | 5/89 | 3.37%—97.75% | 15 | 0 | 69 | 0 | 0.01904538 |
| kev_trained_off_model_only_low | 20 | 4 | 0 | 4/4 = 100.00% | 4/89 | 4.49%—100.00% | 14 | 0 | 69 | 0 | 0.20880480 |
| kev_trained_off_model_only_high | 20 | 2 | 3 | 2/5 = 40.00% | 5/89 | 2.25%—96.63% | 14 | 0 | 69 | 0 | 0.29629990 |
| kev_trained_off_model_only_max | 20 | 4 | 2 | 4/6 = 66.67% | 6/89 | 4.49%—97.75% | 14 | 0 | 69 | 0 | 0.58005880 |
| kev_trained_on_model_only_low | 20 | 4 | 0 | 4/4 = 100.00% | 4/89 | 4.49%—100.00% | 14 | 0 | 69 | 0 | 0.17307290 |
| kev_trained_on_model_only_high | 20 | 5 | 0 | 5/5 = 100.00% | 5/89 | 5.62%—100.00% | 14 | 0 | 69 | 0 | 0.20964310 |
| kev_trained_on_model_only_max | 20 | 5 | 0 | 5/5 = 100.00% | 5/89 | 5.62%—100.00% | 14 | 0 | 69 | 0 | 0.73990070 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-12T17:37:32.218506+00:00，51504.210555秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入9,577,862、输出664,632 Token；399次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Provider实际报告缓存读取6,871,744 Token；476次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求125次，短评实际输入Router 194次；同一短评可由多次决策消费。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 11 | 12 | 2 |
| HTTPError | 0 | 0 | 6 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 60 | 19 | 0 |
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
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |

## 实际Router动作

以下是已记录的Model×Native Effort选择次数；教师短评输入Router，不直接写入执行模型消息。

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 12, "gpt-6-luna:low": 41}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 15, "gpt-6-luna:high": 39}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 94, "gpt-6-luna:max": 13}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 17, "gpt-6-luna:low": 17}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 10, "gpt-6-luna:high": 49}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 73, "gpt-6-luna:max": 11}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 9, "gpt-6-luna:low": 29}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 7, "gpt-6-luna:high": 43}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 97, "gpt-6-luna:max": 6}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 14, "gpt-6-luna:low": 26}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 12, "gpt-6-luna:high": 55}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 67, "gpt-6-luna:max": 10}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 38}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 57}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 44}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 35}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 39}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 40}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 70}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 73, "gpt-6-luna:high": 1}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 91}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 72}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 75, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 115, "gpt-6-luna:max": 2}`
