# Terminal-Bench 2.0 · Joint selection paired continuation

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：213d4469。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共957个任务/策略/seed位置；已结束261，运行中0，未开始696，渠道档位不可用0。有效官方任务评分1/0为143/107，缺有效评分 11，原Verifier依赖失败0位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 404次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$17.87105198、教师$0.00000000，合计$17.87105198；209次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟357669.724801秒，内含官方Trial累计355663.684891秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：87/87题已有结束记录；87题已结束全部3个固定/简单策略；0题已结束全部11个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批87题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 87题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 87 | 42 | 36 | 42/78 = 53.85% | 78/87 | 48.28%—58.62% | 9 | 0 | 0 | 0 | 4.67163201 |
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

实际执行跨度：2026-11-14T11:29:06.657325+00:00至2026-11-22T00:36:20.617238+00:00，652033.959913秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/87；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入174,537,102、输出3,274,084 Token；208次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入0、输出0 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取153,691,686 Token；570次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求0次，短评实际输入Router 0次；同一短评可由多次决策消费。

Provider实际额外重试2377次；已记录技术恢复143次，涉及119个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

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
| fixed_vs_router | glm_low → laya_original_off_model_only_low | 33 | 21/13 | 15 | 13/8 | 0.12048501 / 0.05534284 |
| fixed_vs_router | glm_low → laya_original_off_model_only_high | 34 | 21/21 | 14 | 14/12 | 0.10948467 / 0.15155643 |
| fixed_vs_router | glm_low → laya_original_off_model_only_max | 39 | 23/23 | 11 | 11/10 | 0.06112457 / 0.24459076 |
| fixed_vs_router | glm_low → laya_original_on_model_only_low | 34 | 22/16 | 10 | 8/9 | 0.10072038 / 0.04867473 |
| fixed_vs_router | glm_low → laya_original_on_model_only_high | 32 | 19/17 | 12 | 11/10 | 0.12788904 / 0.08004478 |
| fixed_vs_router | glm_low → laya_original_on_model_only_max | 41 | 25/20 | 9 | 8/6 | 0.08670468 / 0.20727087 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_low | 36 | 23/12 | 13 | 12/6 | 0.14836450 / 0.06633588 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_high | 34 | 21/19 | 13 | 11/9 | 0.18530743 / 0.35224659 |
| fixed_vs_router | glm_low → laya_trained_off_model_only_max | 42 | 25/24 | 11 | 9/8 | 0.09527452 / 0.17753246 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_low | 37 | 24/16 | 14 | 13/8 | 0.11066502 / 0.05088584 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_high | 30 | 19/16 | 11 | 10/8 | 0.08823407 / 0.04314608 |
| fixed_vs_router | glm_low → laya_trained_on_model_only_max | 40 | 22/22 | 8 | 8/6 | 0.06277511 / 0.13119777 |
| fixed_vs_router | glm_low → kev_original_off_model_only_low | 32 | 21/9 | 17 | 15/6 | 0.19908254 / 0.09556415 |
| fixed_vs_router | glm_low → kev_original_off_model_only_high | 31 | 21/17 | 17 | 15/13 | 0.18363690 / 0.13394326 |
| fixed_vs_router | glm_low → kev_original_off_model_only_max | 27 | 19/16 | 12 | 11/8 | 0.14162746 / 0.12651492 |
| fixed_vs_router | glm_low → kev_original_on_model_only_low | 28 | 19/11 | 14 | 13/8 | 0.15420765 / 0.03787802 |
| fixed_vs_router | glm_low → kev_original_on_model_only_high | 31 | 19/19 | 12 | 11/9 | 0.11412703 / 0.07390806 |
| fixed_vs_router | glm_low → kev_original_on_model_only_max | 32 | 22/20 | 15 | 13/12 | 0.14634921 / 0.13179584 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_low | 62 | 33/43 | 32 | 20/24 | 1.12801273 / 2.03264740 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_high | 55 | 33/38 | 30 | 19/21 | 1.12938283 / 2.80690300 |
| fixed_vs_router | glm_low → kev_trained_off_model_only_max | 46 | 27/32 | 22 | 15/17 | 0.58272252 / 3.81880390 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_low | 59 | 31/40 | 12 | 9/11 | 0.21678749 / 0.50903010 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_high | 55 | 30/40 | 14 | 11/13 | 0.23390914 / 0.68232840 |
| fixed_vs_router | glm_low → kev_trained_on_model_only_max | 44 | 25/32 | 9 | 8/8 | 0.08354726 / 1.29433656 |
| fixed_vs_router | luna_high → laya_original_off | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03605180 |
| fixed_vs_router | luna_high → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03337800 |
| fixed_vs_router | luna_high → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.01148994 / 0.01114295 |
| fixed_vs_router | luna_high → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.02466572 |
| fixed_vs_router | luna_high → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.00187274 / 0.00152466 |
| fixed_vs_router | luna_high → kev_original_on | 2 | 2/1 | 2 | 2/1 | 0.01336268 / 0.00300610 |
| fixed_vs_router | luna_high → kev_trained_off | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.02944120 |
| fixed_vs_router | luna_high → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.01336268 / 0.03183710 |
| fixed_vs_router | luna_high → laya_original_off_model_only_low | 35 | 19/14 | 3 | 3/3 | 0.01446218 / 0.00368824 |
| fixed_vs_router | luna_high → laya_original_off_model_only_high | 36 | 20/23 | 3 | 3/3 | 0.01446218 / 0.00597012 |
| fixed_vs_router | luna_high → laya_original_off_model_only_max | 43 | 24/24 | 1 | 1/1 | 0.01148994 / 0.01794657 |
| fixed_vs_router | luna_high → laya_original_on_model_only_low | 36 | 20/17 | 3 | 3/3 | 0.01446218 / 0.00554765 |
| fixed_vs_router | luna_high → laya_original_on_model_only_high | 34 | 19/17 | 3 | 3/2 | 0.01446218 / 0.01072316 |
| fixed_vs_router | luna_high → laya_original_on_model_only_max | 44 | 24/21 | 1 | 1/1 | 0.00187274 / 0.01134179 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_low | 38 | 21/12 | 3 | 3/2 | 0.01446218 / 0.00355368 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_high | 36 | 19/21 | 2 | 2/2 | 0.01258944 / 0.00814146 |
| fixed_vs_router | luna_high → laya_trained_off_model_only_max | 44 | 24/26 | 1 | 1/1 | 0.00187274 / 0.01194385 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_low | 40 | 22/18 | 2 | 2/1 | 0.00297224 / 0.00241099 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_high | 32 | 19/17 | 2 | 2/2 | 0.00297224 / 0.00377197 |
| fixed_vs_router | luna_high → laya_trained_on_model_only_max | 42 | 26/23 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | luna_high → kev_original_off_model_only_low | 34 | 18/9 | 2 | 2/2 | 0.00378666 / 0.00538690 |
| fixed_vs_router | luna_high → kev_original_off_model_only_high | 33 | 18/18 | 3 | 3/3 | 0.00565940 / 0.00857048 |
| fixed_vs_router | luna_high → kev_original_off_model_only_max | 28 | 16/17 | 1 | 1/1 | 0.00187274 / 0.00180800 |
| fixed_vs_router | luna_high → kev_original_on_model_only_low | 31 | 17/12 | 1 | 1/1 | 0.00187274 / 0.00171380 |
| fixed_vs_router | luna_high → kev_original_on_model_only_high | 34 | 19/20 | 1 | 1/1 | 0.00187274 / 0.00348850 |
| fixed_vs_router | luna_high → kev_original_on_model_only_max | 35 | 22/23 | 3 | 3/2 | 0.01446218 / 0.01173330 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_low | 68 | 33/49 | 3 | 3/3 | 0.01446218 / 0.05154140 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_high | 61 | 31/44 | 3 | 3/2 | 0.01446218 / 0.05637600 |
| fixed_vs_router | luna_high → kev_trained_off_model_only_max | 51 | 28/37 | 3 | 3/3 | 0.01446218 / 0.30960480 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_low | 65 | 30/46 | 1 | 1/1 | 0.00187274 / 0.03532380 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_high | 61 | 30/46 | 3 | 3/3 | 0.01446218 / 0.06776670 |
| fixed_vs_router | luna_high → kev_trained_on_model_only_max | 49 | 27/37 | 2 | 2/2 | 0.01336268 / 0.30910010 |
| fixed_vs_router | terra_high → laya_original_off | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03605180 |
| fixed_vs_router | terra_high → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03337800 |
| fixed_vs_router | terra_high → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.07466300 / 0.01114295 |
| fixed_vs_router | terra_high → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.02466572 |
| fixed_vs_router | terra_high → kev_original_off | 1 | 1/1 | 1 | 1/1 | 0.02012140 / 0.00152466 |
| fixed_vs_router | terra_high → kev_original_on | 2 | 2/1 | 2 | 2/1 | 0.09478440 / 0.00300610 |
| fixed_vs_router | terra_high → kev_trained_off | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.02944120 |
| fixed_vs_router | terra_high → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.09478440 / 0.03183710 |
| fixed_vs_router | terra_high → laya_original_off_model_only_low | 35 | 26/14 | 14 | 13/8 | 1.04585300 / 0.04779351 |
| fixed_vs_router | terra_high → laya_original_off_model_only_high | 36 | 26/23 | 14 | 13/12 | 0.78581600 / 0.14788498 |
| fixed_vs_router | terra_high → laya_original_off_model_only_max | 43 | 32/24 | 9 | 9/8 | 0.49252440 / 0.20525116 |
| fixed_vs_router | terra_high → laya_original_on_model_only_low | 36 | 27/17 | 11 | 10/10 | 0.91177480 / 0.04976566 |
| fixed_vs_router | terra_high → laya_original_on_model_only_high | 34 | 25/17 | 12 | 11/9 | 0.84563560 / 0.08313901 |
| fixed_vs_router | terra_high → laya_original_on_model_only_max | 44 | 33/21 | 9 | 8/5 | 1.15485300 / 0.23135221 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_low | 38 | 28/12 | 14 | 13/6 | 1.03596600 / 0.06577535 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_high | 36 | 26/21 | 13 | 12/10 | 0.96069600 / 0.16472858 |
| fixed_vs_router | terra_high → laya_trained_off_model_only_max | 44 | 32/26 | 8 | 8/6 | 0.56663060 / 0.12141666 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_low | 40 | 29/18 | 14 | 12/6 | 1.45456840 / 0.09184631 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_high | 32 | 23/17 | 11 | 10/8 | 0.76604340 / 0.04221460 |
| fixed_vs_router | terra_high → laya_trained_on_model_only_max | 42 | 31/23 | 8 | 7/6 | 1.09001120 / 0.16772572 |
| fixed_vs_router | terra_high → kev_original_off_model_only_low | 34 | 25/9 | 16 | 14/6 | 1.67861760 / 0.08085881 |
| fixed_vs_router | terra_high → kev_original_off_model_only_high | 33 | 24/18 | 16 | 14/13 | 1.66994800 / 0.13761830 |
| fixed_vs_router | terra_high → kev_original_off_model_only_max | 28 | 22/17 | 11 | 10/7 | 1.41500920 / 0.13488274 |
| fixed_vs_router | terra_high → kev_original_on_model_only_low | 31 | 23/12 | 13 | 12/7 | 1.54879540 / 0.03806046 |
| fixed_vs_router | terra_high → kev_original_on_model_only_high | 34 | 23/20 | 10 | 9/8 | 1.23249960 / 0.06860462 |
| fixed_vs_router | terra_high → kev_original_on_model_only_max | 35 | 27/23 | 15 | 13/11 | 1.57049720 / 0.12311584 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_low | 68 | 48/49 | 28 | 23/23 | 2.21137500 / 1.56944640 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_high | 61 | 44/44 | 24 | 20/17 | 2.06102940 / 1.51382440 |
| fixed_vs_router | terra_high → kev_trained_off_model_only_max | 51 | 39/37 | 21 | 17/16 | 1.86411660 / 3.16892790 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_low | 65 | 45/46 | 11 | 10/10 | 1.36046840 / 0.58660690 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_high | 61 | 44/46 | 14 | 13/14 | 1.01713840 / 0.62907520 |
| fixed_vs_router | terra_high → kev_trained_on_model_only_max | 49 | 36/37 | 10 | 10/9 | 0.73995020 / 1.38887506 |
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
