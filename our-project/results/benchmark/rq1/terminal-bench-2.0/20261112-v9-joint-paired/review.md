# Terminal-Bench 2.0 · Joint selection paired continuation

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：213d4469。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共957个任务/策略/seed位置；已结束261，运行中0，未开始696，渠道档位不可用0。有效官方任务评分1/0为143/107，缺有效评分 11，原Verifier依赖失败0位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 403次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$17.86228316、教师$0.00000000，合计$17.86228316；209次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟355062.383656秒，内含官方Trial累计353060.975823秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：87/87题已有结束记录；87题已结束全部3个固定/简单策略；0题已结束全部11个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批87题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 87题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 87 | 42 | 36 | 42/78 = 53.85% | 78/87 | 48.28%—58.62% | 9 | 0 | 0 | 0 | 4.66286319 |
| luna_high | 87 | 38 | 48 | 38/86 = 44.19% | 86/87 | 43.68%—44.83% | 1 | 0 | 0 | 0 | 1.36614357 |
| terra_high | 87 | 63 | 23 | 63/86 = 73.26% | 86/87 | 72.41%—73.56% | 1 | 0 | 0 | 0 | 11.83327640 |
| laya_original_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_original_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_trained_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| laya_trained_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_original_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_original_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_trained_off | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |
| kev_trained_on | 0 | 0 | 0 | 缺有效评分 | 0/87 | 0.00%—100.00% | 0 | 0 | 87 | 0 | UNKNOWN |

实际执行跨度：2026-11-14T11:29:06.657325+00:00至2026-11-21T15:13:25.902854+00:00，618259.245529秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/87；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入174,348,946、输出3,270,661 Token；208次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入0、输出0 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取153,515,302 Token；570次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求0次，短评实际输入Router 0次；同一短评可由多次决策消费。

Provider实际额外重试2377次；已记录技术恢复142次，涉及119个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度54次；其中4个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 6 | 34 | 3 |
| NO_RECORDED_ERROR | 137 | 69 | 0 |
| NonZeroAgentExitCodeError | 0 | 0 | 2 |
| OutputTokenExceededError | 0 | 4 | 4 |
| VerifierTimeoutError | 0 | 0 | 2 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

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
| fixed_vs_router | glm_low → laya_original_off | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00907836 |
| fixed_vs_router | glm_low → laya_original_on | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01894490 |
| fixed_vs_router | glm_low → laya_trained_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_low → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00779292 |
| fixed_vs_router | glm_low → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00152466 |
| fixed_vs_router | glm_low → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.00174950 |
| fixed_vs_router | glm_low → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01547080 |
| fixed_vs_router | glm_low → kev_trained_on | 1 | 1/1 | 1 | 1/1 | 0.00219704 / 0.01004740 |
| fixed_vs_router | glm_low → laya_original_off_model_only_low | 29 | 19/12 | 14 | 12/8 | 0.11859958 / 0.05432010 |
| fixed_vs_router | glm_low → laya_original_off_model_only_high | 28 | 18/19 | 13 | 13/12 | 0.09816025 / 0.13311815 |
| fixed_vs_router | glm_low → laya_original_off_model_only_max | 32 | 18/18 | 10 | 10/9 | 0.04980015 / 0.20664262 |
| fixed_vs_router | glm_low → laya_original_on_model_only_low | 25 | 16/11 | 8 | 7/7 | 0.07596758 / 0.03072162 |
| fixed_vs_router | glm_low → laya_original_on_model_only_high | 25 | 14/13 | 11 | 10/9 | 0.12754115 / 0.07904878 |
| fixed_vs_router | glm_low → laya_original_on_model_only_max | 33 | 20/16 | 9 | 8/6 | 0.08670468 / 0.20727087 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_low | 29 | 19/9 | 12 | 11/5 | 0.13704008 / 0.06278844 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_high | 28 | 18/18 | 13 | 11/9 | 0.18530743 / 0.35224659 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_max | 33 | 20/20 | 11 | 9/8 | 0.09527452 / 0.17753246 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_low | 32 | 21/14 | 13 | 12/7 | 0.11031713 / 0.04799512 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_high | 27 | 18/16 | 11 | 10/8 | 0.08823407 / 0.04314608 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_max | 35 | 20/21 | 7 | 7/5 | 0.04655713 / 0.11228692 |
| fixed_vs_router | glm_low → kev_original_off_model_only_low | 28 | 18/8 | 14 | 12/5 | 0.18461692 / 0.08431651 |
| fixed_vs_router | glm_low → kev_original_off_model_only_high | 27 | 19/15 | 14 | 13/11 | 0.16849440 / 0.11198228 |
| fixed_vs_router | glm_low → kev_original_off_model_only_max | 24 | 18/14 | 12 | 11/8 | 0.14162746 / 0.12651492 |
| fixed_vs_router | glm_low → kev_original_on_model_only_low | 26 | 18/11 | 13 | 12/8 | 0.15295188 / 0.03477706 |
| fixed_vs_router | glm_low → kev_original_on_model_only_high | 28 | 17/17 | 11 | 10/8 | 0.10280261 / 0.06996194 |
| fixed_vs_router | glm_low → kev_original_on_model_only_max | 30 | 21/19 | 15 | 13/12 | 0.14634921 / 0.13179584 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_low | 58 | 30/40 | 31 | 19/23 | 1.11179475 / 1.90489840 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_high | 53 | 31/36 | 30 | 19/21 | 1.12938283 / 2.80690300 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_max | 42 | 24/28 | 20 | 14/15 | 0.56394223 / 3.41676850 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_low | 52 | 26/35 | 11 | 8/10 | 0.21553172 / 0.45387510 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_high | 48 | 26/35 | 12 | 9/11 | 0.21643539 / 0.57678740 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_max | 38 | 22/28 | 8 | 7/7 | 0.08166183 / 1.10583984 |
| fixed_vs_router | luna_high → laya_original_off | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03605180 |
| fixed_vs_router | luna_high → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03337800 |
| fixed_vs_router | luna_high → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.01148994 / 0.01114295 |
| fixed_vs_router | luna_high → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.02466572 |
| fixed_vs_router | luna_high → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00187274 / 0.00152466 |
| fixed_vs_router | luna_high → kev_original_on | 2 | 2/1 | 2 | 2/1 | 0.01336268 / 0.00300610 |
| fixed_vs_router | luna_high → kev_trained_off | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.02944120 |
| fixed_vs_router | luna_high → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03183710 |
| fixed_vs_router | luna_high → laya_original_off_model_only_low | 31 | 17/13 | 3 | 3/3 | 0.01446218 / 0.00368824 |
| fixed_vs_router | luna_high → laya_original_off_model_only_high | 30 | 17/21 | 3 | 3/3 | 0.01446218 / 0.00597012 |
| fixed_vs_router | luna_high → laya_original_off_model_only_max | 36 | 19/19 | 1 | 1/1 | 0.01148994 / 0.01794657 |
| fixed_vs_router | luna_high → laya_original_on_model_only_low | 27 | 14/12 | 3 | 3/3 | 0.01446218 / 0.00554765 |
| fixed_vs_router | luna_high → laya_original_on_model_only_high | 27 | 14/13 | 3 | 3/2 | 0.01446218 / 0.01072316 |
| fixed_vs_router | luna_high → laya_original_on_model_only_max | 36 | 19/17 | 1 | 1/1 | 0.00187274 / 0.01134179 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_low | 31 | 17/9 | 3 | 3/2 | 0.01446218 / 0.00355368 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_high | 30 | 16/20 | 2 | 2/2 | 0.01258944 / 0.00814146 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_max | 35 | 20/22 | 1 | 1/1 | 0.00187274 / 0.01194385 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_low | 35 | 20/16 | 2 | 2/1 | 0.00297224 / 0.00241099 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_high | 29 | 19/17 | 2 | 2/2 | 0.00297224 / 0.00377197 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_max | 37 | 25/22 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_high → kev_original_off_model_only_low | 30 | 15/8 | 2 | 2/2 | 0.00378666 / 0.00538690 |
| fixed_vs_router | luna_high → kev_original_off_model_only_high | 29 | 16/16 | 3 | 3/3 | 0.00565940 / 0.00857048 |
| fixed_vs_router | luna_high → kev_original_off_model_only_max | 25 | 15/15 | 1 | 1/1 | 0.00187274 / 0.00180800 |
| fixed_vs_router | luna_high → kev_original_on_model_only_low | 29 | 16/12 | 1 | 1/1 | 0.00187274 / 0.00171380 |
| fixed_vs_router | luna_high → kev_original_on_model_only_high | 31 | 17/18 | 1 | 1/1 | 0.00187274 / 0.00348850 |
| fixed_vs_router | luna_high → kev_original_on_model_only_max | 33 | 21/22 | 3 | 3/2 | 0.01446218 / 0.01173330 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_low | 64 | 31/46 | 3 | 3/3 | 0.01446218 / 0.05154140 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_high | 59 | 29/42 | 3 | 3/2 | 0.01446218 / 0.05637600 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_max | 47 | 26/33 | 3 | 3/3 | 0.01446218 / 0.30960480 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_low | 58 | 26/41 | 1 | 1/1 | 0.00187274 / 0.03532380 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_high | 54 | 27/41 | 3 | 3/3 | 0.01446218 / 0.06776670 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_max | 43 | 24/33 | 2 | 2/2 | 0.01336268 / 0.30910010 |
| fixed_vs_router | terra_high → laya_original_off | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03605180 |
| fixed_vs_router | terra_high → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03337800 |
| fixed_vs_router | terra_high → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.07466300 / 0.01114295 |
| fixed_vs_router | terra_high → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.02466572 |
| fixed_vs_router | terra_high → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.02012140 / 0.00152466 |
| fixed_vs_router | terra_high → kev_original_on | 2 | 2/1 | 2 | 2/1 | 0.09478440 / 0.00300610 |
| fixed_vs_router | terra_high → kev_trained_off | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.02944120 |
| fixed_vs_router | terra_high → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03183710 |
| fixed_vs_router | terra_high → laya_original_off_model_only_low | 31 | 23/13 | 13 | 12/8 | 0.99225420 / 0.04677077 |
| fixed_vs_router | terra_high → laya_original_off_model_only_high | 30 | 21/21 | 13 | 12/12 | 0.67706860 / 0.12944670 |
| fixed_vs_router | terra_high → laya_original_off_model_only_max | 36 | 26/19 | 8 | 8/7 | 0.38377700 / 0.16730302 |
| fixed_vs_router | terra_high → laya_original_on_model_only_low | 27 | 19/12 | 9 | 8/8 | 0.74809400 / 0.03181255 |
| fixed_vs_router | terra_high → laya_original_on_model_only_high | 27 | 18/13 | 12 | 11/9 | 0.84563560 / 0.08313901 |
| fixed_vs_router | terra_high → laya_original_on_model_only_max | 36 | 26/17 | 9 | 8/5 | 1.15485300 / 0.23135221 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_low | 31 | 22/9 | 13 | 12/5 | 0.92721860 / 0.06222791 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_high | 30 | 21/20 | 13 | 12/10 | 0.96069600 / 0.16472858 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_max | 35 | 25/22 | 8 | 8/6 | 0.56663060 / 0.12141666 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_low | 35 | 25/16 | 14 | 12/6 | 1.45456840 / 0.09184631 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_high | 29 | 21/17 | 11 | 10/8 | 0.76604340 / 0.04221460 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_max | 37 | 27/22 | 7 | 6/5 | 0.93624580 / 0.14881487 |
| fixed_vs_router | terra_high → kev_original_off_model_only_low | 30 | 22/8 | 13 | 11/5 | 1.49123260 / 0.06961117 |
| fixed_vs_router | terra_high → kev_original_off_model_only_high | 29 | 21/16 | 14 | 12/11 | 1.53616180 / 0.12074542 |
| fixed_vs_router | terra_high → kev_original_off_model_only_max | 25 | 20/15 | 11 | 10/7 | 1.41500920 / 0.13488274 |
| fixed_vs_router | terra_high → kev_original_on_model_only_low | 29 | 22/12 | 12 | 11/7 | 1.52375660 / 0.03495950 |
| fixed_vs_router | terra_high → kev_original_on_model_only_high | 31 | 21/18 | 9 | 8/7 | 1.12375220 / 0.06465850 |
| fixed_vs_router | terra_high → kev_original_on_model_only_max | 33 | 26/22 | 15 | 13/11 | 1.57049720 / 0.12311584 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_low | 64 | 45/46 | 27 | 22/22 | 2.05760960 / 1.44169740 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_high | 59 | 42/42 | 24 | 20/17 | 2.06102940 / 1.51382440 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_max | 47 | 35/33 | 20 | 16/15 | 1.71035120 / 2.98807150 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_low | 58 | 39/41 | 10 | 9/9 | 1.33542960 / 0.53145190 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_high | 54 | 39/41 | 12 | 11/12 | 0.83833420 / 0.52353420 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_max | 43 | 32/33 | 9 | 9/8 | 0.68635140 / 1.20037834 |
| fixed_vs_router | glm_high → laya_original_off | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00907836 |
| fixed_vs_router | glm_high → laya_original_on | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01894490 |
| fixed_vs_router | glm_high → laya_trained_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00779292 |
| fixed_vs_router | glm_high → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00152466 |
| fixed_vs_router | glm_high → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.00174950 |
| fixed_vs_router | glm_high → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01547080 |
| fixed_vs_router | glm_high → kev_trained_on | 1 | 1/1 | 1 | 1/1 | 0.02341415 / 0.01004740 |
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
| fixed_vs_router | glm_max → laya_original_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_original_on | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → laya_trained_on | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_original_on | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_max → kev_trained_on | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
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
| fixed_vs_router | luna_low → laya_original_off | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.03605180 |
| fixed_vs_router | luna_low → laya_original_on | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.03337800 |
| fixed_vs_router | luna_low → laya_trained_off | 1 | 0/1 | 1 | 0/1 | 0.00459038 / 0.01114295 |
| fixed_vs_router | luna_low → laya_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.02466572 |
| fixed_vs_router | luna_low → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00125526 / 0.00152466 |
| fixed_vs_router | luna_low → kev_original_on | 2 | 1/1 | 2 | 1/1 | 0.00584564 / 0.00300610 |
| fixed_vs_router | luna_low → kev_trained_off | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.02944120 |
| fixed_vs_router | luna_low → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00584564 / 0.03183710 |
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
| fixed_vs_router | luna_max → laya_original_off | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.03605180 |
| fixed_vs_router | luna_max → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.03337800 |
| fixed_vs_router | luna_max → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02706230 / 0.01114295 |
| fixed_vs_router | luna_max → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.02466572 |
| fixed_vs_router | luna_max → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00526954 / 0.00152466 |
| fixed_vs_router | luna_max → kev_original_on | 2 | 2/1 | 2 | 2/1 | 0.03233184 / 0.00300610 |
| fixed_vs_router | luna_max → kev_trained_off | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.02944120 |
| fixed_vs_router | luna_max → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03233184 / 0.03183710 |
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
| fixed_vs_router | luna_xhigh → laya_original_off | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00907836 |
| fixed_vs_router | luna_xhigh → laya_original_on | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01894490 |
| fixed_vs_router | luna_xhigh → laya_trained_off | 0 | 0/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_xhigh → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00779292 |
| fixed_vs_router | luna_xhigh → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00152466 |
| fixed_vs_router | luna_xhigh → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.00174950 |
| fixed_vs_router | luna_xhigh → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01547080 |
| fixed_vs_router | luna_xhigh → kev_trained_on | 1 | 1/1 | 1 | 1/1 | 0.00246240 / 0.01004740 |
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

- laya_original_off: `{}`
- laya_original_on: `{}`
- laya_trained_off: `{}`
- laya_trained_on: `{}`
- kev_original_off: `{}`
- kev_original_on: `{}`
- kev_trained_off: `{}`
- kev_trained_on: `{}`
