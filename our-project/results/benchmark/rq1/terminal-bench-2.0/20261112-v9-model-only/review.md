# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束2134，运行中2，未开始0，渠道档位不可用0。有效官方任务评分1/0为407/249，缺有效评分 1446，原Verifier依赖失败32位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2180次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$47.65098166、教师$0.27874039，合计$47.92972205；2368次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1440948.186350秒，内含官方Trial累计1414681.556736秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；88题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 89 | 10 | 12 | 10/22 = 45.45% | 22/89 | 11.24%—86.52% | 67 | 0 | 0 | 0 | 0.17443699 |
| laya_original_off_model_only_high | 89 | 15 | 5 | 15/20 = 75.00% | 20/89 | 16.85%—94.38% | 67 | 0 | 0 | 0 | 0.54402543 |
| laya_original_off_model_only_max | 89 | 16 | 10 | 16/26 = 61.54% | 26/89 | 17.98%—88.76% | 62 | 0 | 0 | 0 | 1.68098564 |
| laya_original_on_model_only_low | 89 | 10 | 8 | 10/18 = 55.56% | 18/89 | 11.24%—91.01% | 71 | 0 | 0 | 0 | 0.17409410 |
| laya_original_on_model_only_high | 89 | 10 | 9 | 10/19 = 52.63% | 19/89 | 11.24%—89.89% | 70 | 0 | 0 | 0 | 0.27005675 |
| laya_original_on_model_only_max | 89 | 13 | 14 | 13/27 = 48.15% | 27/89 | 14.61%—84.27% | 61 | 0 | 0 | 0 | 1.66907776 |
| laya_trained_off_model_only_low | 89 | 8 | 13 | 8/21 = 38.10% | 21/89 | 8.99%—85.39% | 67 | 0 | 0 | 0 | 0.17597271 |
| laya_trained_off_model_only_high | 88 | 14 | 6 | 14/20 = 70.00% | 20/89 | 15.73%—93.26% | 68 | 1 | 0 | 0 | 0.47471364 |
| laya_trained_off_model_only_max | 88 | 17 | 9 | 17/26 = 65.38% | 26/89 | 19.10%—89.89% | 61 | 1 | 0 | 0 | 1.47079079 |
| laya_trained_on_model_only_low | 89 | 12 | 13 | 12/25 = 48.00% | 25/89 | 13.48%—85.39% | 63 | 0 | 0 | 0 | 0.23673803 |
| laya_trained_on_model_only_high | 89 | 11 | 9 | 11/20 = 55.00% | 20/89 | 12.36%—89.89% | 68 | 0 | 0 | 0 | 0.43189058 |
| laya_trained_on_model_only_max | 89 | 19 | 10 | 19/29 = 65.52% | 29/89 | 21.35%—88.76% | 59 | 0 | 0 | 0 | 1.17164815 |
| kev_original_off_model_only_low | 89 | 6 | 15 | 6/21 = 28.57% | 21/89 | 6.74%—83.15% | 65 | 0 | 0 | 0 | 0.10747895 |
| kev_original_off_model_only_high | 89 | 13 | 7 | 13/20 = 65.00% | 20/89 | 14.61%—92.13% | 65 | 0 | 0 | 0 | 0.18025922 |
| kev_original_off_model_only_max | 89 | 12 | 6 | 12/18 = 66.67% | 18/89 | 13.48%—93.26% | 70 | 0 | 0 | 0 | 0.29879535 |
| kev_original_on_model_only_low | 89 | 10 | 10 | 10/20 = 50.00% | 20/89 | 11.24%—88.76% | 66 | 0 | 0 | 0 | 0.08183440 |
| kev_original_on_model_only_high | 89 | 13 | 9 | 13/22 = 59.09% | 22/89 | 14.61%—89.89% | 65 | 0 | 0 | 0 | 0.18339210 |
| kev_original_on_model_only_max | 89 | 16 | 7 | 16/23 = 69.57% | 23/89 | 17.98%—92.13% | 65 | 0 | 0 | 0 | 0.45469887 |
| kev_trained_off_model_only_low | 89 | 36 | 16 | 36/52 = 69.23% | 52/89 | 40.45%—82.02% | 34 | 0 | 0 | 0 | 4.04317440 |
| kev_trained_off_model_only_high | 89 | 32 | 16 | 32/48 = 66.67% | 48/89 | 35.96%—82.02% | 39 | 0 | 0 | 0 | 5.26468520 |
| kev_trained_off_model_only_max | 89 | 26 | 12 | 26/38 = 68.42% | 38/89 | 29.21%—86.52% | 51 | 0 | 0 | 0 | 11.53005560 |
| kev_trained_on_model_only_low | 89 | 31 | 15 | 31/46 = 67.39% | 46/89 | 34.83%—83.15% | 41 | 0 | 0 | 0 | 3.22117050 |
| kev_trained_on_model_only_high | 89 | 31 | 11 | 31/42 = 73.81% | 42/89 | 34.83%—87.64% | 46 | 0 | 0 | 0 | 4.74676927 |
| kev_trained_on_model_only_max | 89 | 26 | 7 | 26/33 = 78.79% | 33/89 | 29.21%—92.13% | 55 | 0 | 0 | 0 | 9.34297762 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-20T19:07:37.479007+00:00，748109.471056秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入265,734,496、输出8,681,138 Token；2,351次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入67,646,612、输出713,888 Token；82次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取216,692,344 Token；2933次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求1498次，短评实际输入Router 1664次；同一短评可由多次决策消费。

Provider实际额外重试10213次；已记录技术恢复45次，涉及45个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度193次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

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
| AgentTimeoutError | 42 | 82 | 308 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 365 | 152 | 34 |
| NonZeroAgentExitCodeError | 0 | 0 | 741 |
| OutputTokenExceededError | 0 | 15 | 2 |
| ProviderResponseError | 0 | 0 | 15 |
| RemoteDisconnected | 0 | 0 | 2 |
| RuntimeError | 0 | 0 | 14 |
| URLError | 0 | 0 | 325 |
| VerifierTimeoutError | 0 | 0 | 23 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 16 | 11/9 | 12 | 11/9 | 0.15087215 / 0.08625491 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 16 | 12/8 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 19 | 12/13 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 36 | 26/28 | 15 | 11/13 | 0.89874990 / 0.71582740 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 17 | 7/9 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 19 | 7/9 | 12 | 5/6 | 0.05340857 / 0.04677343 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 16 | 4/7 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 43 | 29/31 | 13 | 10/10 | 0.85350340 / 0.71799860 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 19 | 13/9 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 19 | 13/11 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 17 | 11/11 | 15 | 9/10 | 0.19307260 / 0.14507666 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 27 | 21/22 | 9 | 8/7 | 1.40086640 / 1.25152050 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 16 | 12/11 | 12 | 10/9 | 0.12355054 / 0.15023028 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 15 | 9/7 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 17 | 10/13 | 14 | 9/11 | 0.12617074 / 0.95369610 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 15 | 8/13 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 18 | 7/6 | 13 | 7/5 | 0.06187902 / 0.05304593 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 17 | 10/8 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 15 | 3/12 | 13 | 3/10 | 0.08235281 / 0.90461180 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 14 | 5/12 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 15 | 10/12 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 17 | 10/10 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 13 | 8/6 | 9 | 4/5 | 0.12340202 / 1.72878820 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 16 | 11/13 | 9 | 7/7 | 0.07880220 / 1.25152050 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.00242127 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.00463366 |
| joint_vs_model_only | laya_original_off → laya_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01794657 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.00432028 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.03337800 / 0.00884055 |
| joint_vs_model_only | laya_original_on → laya_original_on_model_only_max | 2 | 2/1 | 1 | 1/1 | 0.01894490 / 0.01134179 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_low | 1 | 1/0 | 1 | 1/0 | 0.01114295 / 0.00107424 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.00624260 |
| joint_vs_model_only | laya_trained_off → laya_trained_off_model_only_max | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| joint_vs_model_only | laya_trained_on → laya_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00779292 / 0.00143242 |
| joint_vs_model_only | laya_trained_on → laya_trained_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00779292 / 0.00259735 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 180, "gpt-6-luna:low": 230}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 204, "gpt-6-luna:high": 291}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 947, "gpt-6-luna:max": 128}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 171, "gpt-6-luna:low": 211}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 120, "gpt-6-luna:high": 306}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 898, "gpt-6-luna:max": 104}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 188, "gpt-6-luna:low": 230}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 179, "gpt-6-luna:high": 333}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 983, "gpt-6-luna:max": 106}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 188, "gpt-6-luna:low": 232}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 155, "gpt-6-luna:high": 388}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 841, "gpt-6-luna:max": 121}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 280}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 361}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 380}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 247}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 370}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 363}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 857, "gpt-6-luna:low": 3}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 886, "gpt-6-luna:high": 8}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 1153, "gpt-6-luna:max": 15}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 818, "gpt-6-luna:low": 3}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 848, "gpt-6-luna:high": 10}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 1019, "gpt-6-luna:max": 16}`
