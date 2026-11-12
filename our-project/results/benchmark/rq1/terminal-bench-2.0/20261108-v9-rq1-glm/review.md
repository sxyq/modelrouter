# Terminal-Bench 2.0 RQ1

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：cb4371da0635d9d550314b6703af4cbe87f0b714。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共1513个任务/策略/seed位置；已结束1513，运行中0，未开始0，渠道档位不可用0。固定组已报告档位不符另列后，官方Reward 1/0为256/257，无官方Reward 899；Router组保留实际任务Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2333次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$34.97435329、教师$0.14386542，合计$35.11821871；1036次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟834545.118530秒，内含官方Trial累计818817.495873秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；89题已结束全部9个固定/简单策略；89题已结束全部17个策略。批次先执行固定阶段，再执行Router阶段。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 89 | 13 | 6 | 13/19 = 68.42% | 19/89 | 14.61%—93.26% | 67 | 0 | 0 | 0 | 0.40293753 |
| glm_high | 89 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 72 | 0 | 0 | 0 | 0.45995859 |
| glm_max | 89 | 6 | 5 | 6/11 = 54.55% | 11/89 | 6.74%—94.38% | 75 | 0 | 0 | 0 | 0.45319009 |
| luna_low | 89 | 14 | 34 | 14/48 = 29.17% | 48/89 | 15.73%—61.80% | 30 | 0 | 0 | 0 | 0.29601030 |
| luna_high | 89 | 21 | 23 | 21/44 = 47.73% | 44/89 | 23.60%—74.16% | 34 | 0 | 0 | 0 | 0.85722668 |
| luna_max | 89 | 21 | 20 | 21/41 = 51.22% | 41/89 | 23.60%—77.53% | 41 | 0 | 0 | 0 | 1.55918550 |
| terra_high | 89 | 34 | 18 | 34/52 = 65.38% | 52/89 | 38.20%—79.78% | 32 | 0 | 0 | 0 | 4.48918920 |
| luna_xhigh | 89 | 25 | 23 | 25/48 = 52.08% | 48/89 | 28.09%—74.16% | 33 | 0 | 0 | 0 | 1.41375102 |
| rule_sticky | 89 | 28 | 13 | 28/41 = 68.29% | 41/89 | 31.46%—85.39% | 40 | 0 | 0 | 0 | 3.35438690 |
| laya_original_off | 89 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 77 | 0 | 0 | 0 | 0.36278281 |
| laya_original_on | 89 | 3 | 6 | 3/9 = 33.33% | 9/89 | 3.37%—93.26% | 80 | 0 | 0 | 0 | 0.26023004 |
| laya_trained_off | 89 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 81 | 0 | 0 | 0 | 0.18498189 |
| laya_trained_on | 89 | 3 | 5 | 3/8 = 37.50% | 8/89 | 3.37%—94.38% | 81 | 0 | 0 | 0 | 0.27858662 |
| kev_original_off | 89 | 11 | 43 | 11/54 = 20.37% | 54/89 | 12.36%—51.69% | 21 | 0 | 0 | 0 | 0.24247332 |
| kev_original_on | 89 | 17 | 34 | 17/51 = 33.33% | 51/89 | 19.10%—61.80% | 28 | 0 | 0 | 0 | 0.28372402 |
| kev_trained_off | 89 | 16 | 6 | 16/22 = 72.73% | 22/89 | 17.98%—93.26% | 61 | 0 | 0 | 0 | 9.19439320 |
| kev_trained_on | 89 | 26 | 8 | 26/34 = 76.47% | 34/89 | 29.21%—91.01% | 46 | 0 | 0 | 0 | 11.02521100 |

实际执行跨度：2026-11-08T15:48:04.949644+00:00至2026-11-11T12:18:29.984449+00:00，246625.034805秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入222,158,587、输出6,585,204 Token；1,028次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Provider实际报告缓存读取176,142,912 Token；1292次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求473次，短评实际输入Router 886次；同一短评可由多次决策消费。

已记录Router输入截断4次，涉及3个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|
| gpt-6.1-terra | none | medium | 52 |

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 19 | 127 | 25 |
| EnvironmentStartTimeoutError | 0 | 0 | 45 |
| HTTPError | 0 | 0 | 424 |
| NO_RECORDED_ERROR | 237 | 231 | 0 |
| ProviderResponseError | 0 | 0 | 145 |
| RemoteDisconnected | 0 | 0 | 27 |
| RuntimeError | 0 | 0 | 112 |
| URLError | 0 | 0 | 82 |
| ValueError | 0 | 0 | 2 |
| VerifierTimeoutError | 0 | 0 | 37 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 6 | 3/3 | 5 | 3/3 | 0.11529809 / 0.11227356 |
| teacher | laya_trained_off → laya_trained_on | 5 | 3/3 | 5 | 3/3 | 0.09012806 / 0.13704358 |
| teacher | kev_original_off → kev_original_on | 41 | 10/12 | 19 | 6/7 | 0.06643734 / 0.07751724 |
| teacher | kev_trained_off → kev_trained_on | 15 | 11/13 | 10 | 7/8 | 0.65897720 / 0.89874770 |
| training | laya_original_off → laya_trained_off | 7 | 5/4 | 6 | 5/4 | 0.07787562 / 0.09658031 |
| training | laya_original_on → laya_trained_on | 5 | 3/3 | 4 | 3/3 | 0.07499469 / 0.12199358 |
| training | kev_original_off → kev_trained_off | 19 | 6/14 | 10 | 4/8 | 0.03239018 / 0.84991960 |
| training | kev_original_on → kev_trained_on | 25 | 11/21 | 13 | 8/11 | 0.05194438 / 1.21800562 |

## 实际Router动作

以下是已记录的Model×Native Effort选择次数；教师短评输入Router，不直接写入执行模型消息。

- laya_original_off: `{"glm-5.3-flash:high": 198, "gpt-6.1-terra:high": 89, "gpt-6-luna:high": 30}`
- laya_original_on: `{"glm-5.3-flash:high": 212, "gpt-6-luna:high": 23, "gpt-6.1-terra:high": 44}`
- laya_trained_off: `{"glm-5.3-flash:high": 192, "gpt-6.1-terra:high": 27, "gpt-6-luna:high": 24}`
- laya_trained_on: `{"glm-5.3-flash:high": 226, "gpt-6.1-terra:high": 37, "gpt-6-luna:high": 20}`
- kev_original_off: `{"gpt-6-luna:low": 736}`
- kev_original_on: `{"gpt-6-luna:low": 716}`
- kev_trained_off: `{"gpt-6.1-terra:max": 816, "gpt-6.1-terra:medium": 39, "gpt-6.1-terra:low": 144, "gpt-6.1-terra:none": 32, "gpt-6.1-terra:high": 10}`
- kev_trained_on: `{"gpt-6.1-terra:max": 945, "gpt-6.1-terra:low": 200, "gpt-6.1-terra:none": 21, "gpt-6.1-terra:high": 13, "gpt-6.1-terra:medium": 19}`
