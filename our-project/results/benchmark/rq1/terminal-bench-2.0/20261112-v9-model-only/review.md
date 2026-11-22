# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束2134，运行中2，未开始0，渠道档位不可用0。有效官方任务评分1/0为528/367，缺有效评分 1204，原Verifier依赖失败35位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2476次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$56.22767748、教师$0.35330152，合计$56.58097900；2579次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1639914.558640秒，内含官方Trial累计1612204.151256秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；88题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 89 | 13 | 18 | 13/31 = 41.94% | 31/89 | 14.61%—79.78% | 58 | 0 | 0 | 0 | 0.25257369 |
| laya_original_off_model_only_high | 89 | 21 | 9 | 21/30 = 70.00% | 30/89 | 23.60%—89.89% | 57 | 0 | 0 | 0 | 0.68691736 |
| laya_original_off_model_only_max | 89 | 19 | 17 | 19/36 = 52.78% | 36/89 | 21.35%—80.90% | 52 | 0 | 0 | 0 | 1.81109231 |
| laya_original_on_model_only_low | 89 | 12 | 15 | 12/27 = 44.44% | 27/89 | 13.48%—83.15% | 62 | 0 | 0 | 0 | 0.24414264 |
| laya_original_on_model_only_high | 89 | 13 | 14 | 13/27 = 48.15% | 27/89 | 14.61%—84.27% | 62 | 0 | 0 | 0 | 0.38515027 |
| laya_original_on_model_only_max | 89 | 17 | 20 | 17/37 = 45.95% | 37/89 | 19.10%—77.53% | 51 | 0 | 0 | 0 | 1.81113971 |
| laya_trained_off_model_only_low | 89 | 9 | 22 | 9/31 = 29.03% | 31/89 | 10.11%—75.28% | 57 | 0 | 0 | 0 | 0.22140097 |
| laya_trained_off_model_only_high | 89 | 20 | 11 | 20/31 = 64.52% | 31/89 | 22.47%—87.64% | 58 | 0 | 0 | 0 | 0.61987320 |
| laya_trained_off_model_only_max | 89 | 22 | 14 | 22/36 = 61.11% | 36/89 | 24.72%—84.27% | 52 | 0 | 0 | 0 | 1.61972775 |
| laya_trained_on_model_only_low | 89 | 16 | 20 | 16/36 = 44.44% | 36/89 | 17.98%—77.53% | 52 | 0 | 0 | 0 | 0.29886635 |
| laya_trained_on_model_only_high | 89 | 17 | 13 | 17/30 = 56.67% | 30/89 | 19.10%—85.39% | 58 | 0 | 0 | 0 | 0.56356920 |
| laya_trained_on_model_only_max | 89 | 22 | 16 | 22/38 = 57.89% | 38/89 | 24.72%—82.02% | 50 | 0 | 0 | 0 | 1.31690616 |
| kev_original_off_model_only_low | 89 | 8 | 23 | 8/31 = 25.81% | 31/89 | 8.99%—74.16% | 55 | 0 | 0 | 0 | 0.16304993 |
| kev_original_off_model_only_high | 89 | 16 | 14 | 16/30 = 53.33% | 30/89 | 17.98%—84.27% | 55 | 0 | 0 | 0 | 0.29559167 |
| kev_original_off_model_only_max | 88 | 15 | 10 | 15/25 = 60.00% | 25/89 | 16.85%—88.76% | 61 | 1 | 0 | 0 | 0.43301498 |
| kev_original_on_model_only_low | 89 | 12 | 18 | 12/30 = 40.00% | 30/89 | 13.48%—79.78% | 55 | 0 | 0 | 0 | 0.13757188 |
| kev_original_on_model_only_high | 88 | 18 | 13 | 18/31 = 58.06% | 31/89 | 20.22%—85.39% | 54 | 1 | 0 | 0 | 0.26405254 |
| kev_original_on_model_only_max | 89 | 22 | 11 | 22/33 = 66.67% | 33/89 | 24.72%—87.64% | 55 | 0 | 0 | 0 | 0.58106824 |
| kev_trained_off_model_only_low | 89 | 46 | 18 | 46/64 = 71.88% | 64/89 | 51.69%—79.78% | 22 | 0 | 0 | 0 | 4.56905720 |
| kev_trained_off_model_only_high | 89 | 42 | 17 | 42/59 = 71.19% | 59/89 | 47.19%—80.90% | 28 | 0 | 0 | 0 | 5.84066960 |
| kev_trained_off_model_only_max | 89 | 33 | 14 | 33/47 = 70.21% | 47/89 | 37.08%—84.27% | 42 | 0 | 0 | 0 | 13.86320096 |
| kev_trained_on_model_only_low | 89 | 41 | 17 | 41/58 = 70.69% | 58/89 | 46.07%—80.90% | 29 | 0 | 0 | 0 | 3.74633677 |
| kev_trained_on_model_only_high | 89 | 41 | 13 | 41/54 = 75.93% | 54/89 | 46.07%—85.39% | 34 | 0 | 0 | 0 | 5.57884213 |
| kev_trained_on_model_only_max | 89 | 33 | 10 | 33/43 = 76.74% | 43/89 | 37.08%—88.76% | 45 | 0 | 0 | 0 | 11.27716348 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-21T23:46:55.324294+00:00，851267.316343秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入314,172,855、输出10,267,175 Token；2,562次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入82,710,408、输出872,175 Token；108次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取251,247,126 Token；3145次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求1871次，短评实际输入Router 2160次；同一短评可由多次决策消费。

Provider实际额外重试11151次；已记录技术恢复341次，涉及341个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度214次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

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
| AgentTimeoutError | 50 | 125 | 363 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 5 |
| NO_RECORDED_ERROR | 478 | 219 | 33 |
| NonZeroAgentExitCodeError | 0 | 0 | 742 |
| OutputTokenExceededError | 0 | 23 | 2 |
| ProviderResponseError | 0 | 0 | 14 |
| RemoteDisconnected | 0 | 0 | 1 |
| RuntimeError | 0 | 0 | 14 |
| URLError | 0 | 0 | 37 |
| VerifierTimeoutError | 0 | 0 | 23 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 24 | 16/12 | 12 | 11/9 | 0.15087215 / 0.08625491 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 25 | 17/13 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 27 | 15/17 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 47 | 36/37 | 15 | 11/13 | 0.89874990 / 0.71582740 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 26 | 10/11 | 12 | 7/9 | 0.05613557 / 0.05385480 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 29 | 8/12 | 12 | 5/6 | 0.05340857 / 0.04677343 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 26 | 6/9 | 13 | 4/6 | 0.04198150 / 0.04457288 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 55 | 39/41 | 13 | 10/10 | 0.85350340 / 0.71799860 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 29 | 16/13 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 27 | 18/14 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 23 | 14/15 | 15 | 9/10 | 0.19307260 / 0.14507666 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 36 | 28/29 | 9 | 8/7 | 1.40086640 / 1.25152050 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 27 | 18/17 | 12 | 10/9 | 0.12355054 / 0.15023028 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 23 | 12/11 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 27 | 13/21 | 14 | 9/11 | 0.12617074 / 0.95369610 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 24 | 13/20 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 27 | 10/7 | 13 | 7/5 | 0.06187902 / 0.05304593 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 26 | 12/11 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 25 | 5/20 | 13 | 3/10 | 0.08235281 / 0.90461180 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 23 | 7/19 | 9 | 4/8 | 0.02756582 / 0.47967580 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 24 | 13/16 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 25 | 14/13 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 18 | 11/10 | 9 | 4/5 | 0.12340202 / 1.72878820 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 25 | 17/20 | 9 | 7/7 | 0.07880220 / 1.25152050 |
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
| fixed_vs_router | glm_low → laya_original_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00138287 |
| fixed_vs_router | glm_low → laya_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00255135 |
| fixed_vs_router | glm_low → laya_original_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_low → laya_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00262470 |
| fixed_vs_router | glm_low → laya_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00166075 |
| fixed_vs_router | glm_low → laya_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01134179 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00127141 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_high | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_low → laya_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01194385 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00143242 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00259735 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_max | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_low → kev_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_low → kev_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00186484 |
| fixed_vs_router | glm_low → kev_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00180800 |
| fixed_vs_router | glm_low → kev_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00171380 |
| fixed_vs_router | glm_low → kev_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00348850 |
| fixed_vs_router | glm_low → kev_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00410170 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01318740 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01590660 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.12910040 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.03532380 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.03429790 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.21456160 |
| fixed_vs_router | glm_high → laya_original_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00138287 |
| fixed_vs_router | glm_high → laya_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00255135 |
| fixed_vs_router | glm_high → laya_original_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → laya_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00262470 |
| fixed_vs_router | glm_high → laya_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00166075 |
| fixed_vs_router | glm_high → laya_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01134179 |
| fixed_vs_router | glm_high → laya_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00127141 |
| fixed_vs_router | glm_high → laya_trained_off_model_only_high | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → laya_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01194385 |
| fixed_vs_router | glm_high → laya_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00143242 |
| fixed_vs_router | glm_high → laya_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00259735 |
| fixed_vs_router | glm_high → laya_trained_on_model_only_max | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → kev_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → kev_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00186484 |
| fixed_vs_router | glm_high → kev_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00180800 |
| fixed_vs_router | glm_high → kev_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00171380 |
| fixed_vs_router | glm_high → kev_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00348850 |
| fixed_vs_router | glm_high → kev_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00410170 |
| fixed_vs_router | glm_high → kev_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01318740 |
| fixed_vs_router | glm_high → kev_trained_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01590660 |
| fixed_vs_router | glm_high → kev_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.12910040 |
| fixed_vs_router | glm_high → kev_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.03532380 |
| fixed_vs_router | glm_high → kev_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.03429790 |
| fixed_vs_router | glm_high → kev_trained_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.21456160 |
| fixed_vs_router | glm_max → laya_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_off_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_on_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_on_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_on_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_off_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_on_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_on_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_on_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_off_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_on_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_on_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_on_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_off_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_on_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_on_model_only_high | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_on_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_low → laya_original_off_model_only_low | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.00242127 |
| fixed_vs_router | luna_low → laya_original_off_model_only_high | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.00463366 |
| fixed_vs_router | luna_low → laya_original_off_model_only_max | 1 | 0/1 | 1 | 0/1 | 0.00459038 / 0.01794657 |
| fixed_vs_router | luna_low → laya_original_on_model_only_low | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.00432028 |
| fixed_vs_router | luna_low → laya_original_on_model_only_high | 2 | 1/1 | 2 | 1/1 | 0.00584564 / 0.00884055 |
| fixed_vs_router | luna_low → laya_original_on_model_only_max | 2 | 1/1 | 1 | 1/1 | 0.00125526 / 0.01134179 |
| fixed_vs_router | luna_low → laya_trained_off_model_only_low | 2 | 1/1 | 2 | 1/1 | 0.00584564 / 0.00234565 |
| fixed_vs_router | luna_low → laya_trained_off_model_only_high | 2 | 1/2 | 1 | 0/1 | 0.00459038 / 0.00624260 |
| fixed_vs_router | luna_low → laya_trained_off_model_only_max | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.01194385 |
| fixed_vs_router | luna_low → laya_trained_on_model_only_low | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00143242 |
| fixed_vs_router | luna_low → laya_trained_on_model_only_high | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00259735 |
| fixed_vs_router | luna_low → laya_trained_on_model_only_max | 2 | 1/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_low → kev_original_off_model_only_low | 1 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_low → kev_original_off_model_only_high | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00186484 |
| fixed_vs_router | luna_low → kev_original_off_model_only_max | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00180800 |
| fixed_vs_router | luna_low → kev_original_on_model_only_low | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00171380 |
| fixed_vs_router | luna_low → kev_original_on_model_only_high | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.00348850 |
| fixed_vs_router | luna_low → kev_original_on_model_only_max | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.00905588 |
| fixed_vs_router | luna_low → kev_trained_off_model_only_low | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.03871960 |
| fixed_vs_router | luna_low → kev_trained_off_model_only_high | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.04624140 |
| fixed_vs_router | luna_low → kev_trained_off_model_only_max | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.26640480 |
| fixed_vs_router | luna_low → kev_trained_on_model_only_low | 2 | 1/2 | 1 | 1/1 | 0.00125526 / 0.03532380 |
| fixed_vs_router | luna_low → kev_trained_on_model_only_high | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.05734710 |
| fixed_vs_router | luna_low → kev_trained_on_model_only_max | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.30910010 |
| fixed_vs_router | luna_high → laya_original_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.00242127 |
| fixed_vs_router | luna_high → laya_original_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.00463366 |
| fixed_vs_router | luna_high → laya_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.01148994 / 0.01794657 |
| fixed_vs_router | luna_high → laya_original_on_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.00432028 |
| fixed_vs_router | luna_high → laya_original_on_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.01336268 / 0.00884055 |
| fixed_vs_router | luna_high → laya_original_on_model_only_max | 2 | 2/1 | 1 | 1/1 | 0.00187274 / 0.01134179 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_low | 2 | 2/1 | 2 | 2/1 | 0.01336268 / 0.00234565 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.01148994 / 0.00624260 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.01194385 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00143242 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00259735 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_max | 2 | 2/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_high → kev_original_off_model_only_low | 1 | 1/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_high → kev_original_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00186484 |
| fixed_vs_router | luna_high → kev_original_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00180800 |
| fixed_vs_router | luna_high → kev_original_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00171380 |
| fixed_vs_router | luna_high → kev_original_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.00348850 |
| fixed_vs_router | luna_high → kev_original_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.00905588 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03871960 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.04624140 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.26640480 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00187274 / 0.03532380 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.05734710 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.30910010 |
| fixed_vs_router | luna_max → laya_original_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.00242127 |
| fixed_vs_router | luna_max → laya_original_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.00463366 |
| fixed_vs_router | luna_max → laya_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.02706230 / 0.01794657 |
| fixed_vs_router | luna_max → laya_original_on_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.00432028 |
| fixed_vs_router | luna_max → laya_original_on_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.03233184 / 0.00884055 |
| fixed_vs_router | luna_max → laya_original_on_model_only_max | 2 | 2/1 | 1 | 1/1 | 0.00526954 / 0.01134179 |
| fixed_vs_router | luna_max → laya_trained_off_model_only_low | 2 | 2/1 | 2 | 2/1 | 0.03233184 / 0.00234565 |
| fixed_vs_router | luna_max → laya_trained_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.02706230 / 0.00624260 |
| fixed_vs_router | luna_max → laya_trained_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.01194385 |
| fixed_vs_router | luna_max → laya_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00143242 |
| fixed_vs_router | luna_max → laya_trained_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00259735 |
| fixed_vs_router | luna_max → laya_trained_on_model_only_max | 2 | 2/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_max → kev_original_off_model_only_low | 1 | 1/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_max → kev_original_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00186484 |
| fixed_vs_router | luna_max → kev_original_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00180800 |
| fixed_vs_router | luna_max → kev_original_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00171380 |
| fixed_vs_router | luna_max → kev_original_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.00348850 |
| fixed_vs_router | luna_max → kev_original_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.00905588 |
| fixed_vs_router | luna_max → kev_trained_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.03871960 |
| fixed_vs_router | luna_max → kev_trained_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.04624140 |
| fixed_vs_router | luna_max → kev_trained_off_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.26640480 |
| fixed_vs_router | luna_max → kev_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00526954 / 0.03532380 |
| fixed_vs_router | luna_max → kev_trained_on_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.05734710 |
| fixed_vs_router | luna_max → kev_trained_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.30910010 |
| fixed_vs_router | terra_high → laya_original_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.00242127 |
| fixed_vs_router | terra_high → laya_original_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.00463366 |
| fixed_vs_router | terra_high → laya_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.07466300 / 0.01794657 |
| fixed_vs_router | terra_high → laya_original_on_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.00432028 |
| fixed_vs_router | terra_high → laya_original_on_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.09478440 / 0.00884055 |
| fixed_vs_router | terra_high → laya_original_on_model_only_max | 2 | 2/1 | 1 | 1/1 | 0.02012140 / 0.01134179 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_low | 2 | 2/1 | 2 | 2/1 | 0.09478440 / 0.00234565 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.07466300 / 0.00624260 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.01194385 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00143242 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00259735 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_max | 2 | 2/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | terra_high → kev_original_off_model_only_low | 1 | 1/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | terra_high → kev_original_off_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00186484 |
| fixed_vs_router | terra_high → kev_original_off_model_only_max | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00180800 |
| fixed_vs_router | terra_high → kev_original_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00171380 |
| fixed_vs_router | terra_high → kev_original_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.00348850 |
| fixed_vs_router | terra_high → kev_original_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.00905588 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_low | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03871960 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.04624140 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.26640480 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.02012140 / 0.03532380 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.05734710 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_max | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.30910010 |
| fixed_vs_router | luna_xhigh → laya_original_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00138287 |
| fixed_vs_router | luna_xhigh → laya_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00255135 |
| fixed_vs_router | luna_xhigh → laya_original_off_model_only_max | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_xhigh → laya_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00262470 |
| fixed_vs_router | luna_xhigh → laya_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00166075 |
| fixed_vs_router | luna_xhigh → laya_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01134179 |
| fixed_vs_router | luna_xhigh → laya_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00127141 |
| fixed_vs_router | luna_xhigh → laya_trained_off_model_only_high | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_xhigh → laya_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01194385 |
| fixed_vs_router | luna_xhigh → laya_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00143242 |
| fixed_vs_router | luna_xhigh → laya_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00259735 |
| fixed_vs_router | luna_xhigh → laya_trained_on_model_only_max | 1 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_xhigh → kev_original_off_model_only_low | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_xhigh → kev_original_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00186484 |
| fixed_vs_router | luna_xhigh → kev_original_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00180800 |
| fixed_vs_router | luna_xhigh → kev_original_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00171380 |
| fixed_vs_router | luna_xhigh → kev_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00348850 |
| fixed_vs_router | luna_xhigh → kev_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00410170 |
| fixed_vs_router | luna_xhigh → kev_trained_off_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01318740 |
| fixed_vs_router | luna_xhigh → kev_trained_off_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01590660 |
| fixed_vs_router | luna_xhigh → kev_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.12910040 |
| fixed_vs_router | luna_xhigh → kev_trained_on_model_only_low | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.03532380 |
| fixed_vs_router | luna_xhigh → kev_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.03429790 |
| fixed_vs_router | luna_xhigh → kev_trained_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.21456160 |

## 实际Router动作

以下登记实际选中模型及请求Native Effort；Model-only组固定档位、只选择模型。教师短评输入Router，不直接写入执行模型消息。

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 204, "gpt-6-luna:low": 330}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 235, "gpt-6-luna:high": 437}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 1044, "gpt-6-luna:max": 182}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 206, "gpt-6-luna:low": 303}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 150, "gpt-6-luna:high": 408}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 1008, "gpt-6-luna:max": 150}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 204, "gpt-6-luna:low": 310}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 212, "gpt-6-luna:high": 479}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 1105, "gpt-6-luna:max": 156}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 230, "gpt-6-luna:low": 300}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 196, "gpt-6-luna:high": 506}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 940, "gpt-6-luna:max": 170}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 410}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 497}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 485}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 382}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 488}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 480}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 1002, "gpt-6-luna:low": 3}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 1016, "gpt-6-luna:high": 8}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 1351, "gpt-6-luna:max": 20}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 950, "gpt-6-luna:low": 3}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 998, "gpt-6-luna:high": 11}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 1211, "gpt-6-luna:max": 21}`
