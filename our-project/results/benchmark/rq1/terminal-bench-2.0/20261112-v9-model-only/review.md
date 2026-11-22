# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束2134，运行中2，未开始0，渠道档位不可用0。有效官方任务评分1/0为579/399，缺有效评分 1134，原Verifier依赖失败22位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2566次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$59.04438318、教师$0.36918797，合计$59.41357114；2634次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1683663.991307秒，内含官方Trial累计1655524.755347秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；88题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 89 | 14 | 20 | 14/34 = 41.18% | 34/89 | 15.73%—77.53% | 55 | 0 | 0 | 0 | 0.32505130 |
| laya_original_off_model_only_high | 89 | 23 | 12 | 23/35 = 65.71% | 35/89 | 25.84%—86.52% | 53 | 0 | 0 | 0 | 0.77083398 |
| laya_original_off_model_only_max | 89 | 23 | 18 | 23/41 = 56.10% | 41/89 | 25.84%—79.78% | 48 | 0 | 0 | 0 | 1.85339841 |
| laya_original_on_model_only_low | 89 | 16 | 18 | 16/34 = 47.06% | 34/89 | 17.98%—79.78% | 55 | 0 | 0 | 0 | 0.30541715 |
| laya_original_on_model_only_high | 89 | 16 | 16 | 16/32 = 50.00% | 32/89 | 17.98%—82.02% | 57 | 0 | 0 | 0 | 0.40133580 |
| laya_original_on_model_only_max | 88 | 20 | 21 | 20/41 = 48.78% | 41/89 | 22.47%—76.40% | 46 | 1 | 0 | 0 | 1.83998915 |
| laya_trained_off_model_only_low | 88 | 11 | 24 | 11/35 = 31.43% | 35/89 | 12.36%—73.03% | 53 | 1 | 0 | 0 | 0.26015824 |
| laya_trained_off_model_only_high | 89 | 20 | 13 | 20/33 = 60.61% | 33/89 | 22.47%—85.39% | 56 | 0 | 0 | 0 | 0.63300641 |
| laya_trained_off_model_only_max | 89 | 25 | 16 | 25/41 = 60.98% | 41/89 | 28.09%—82.02% | 47 | 0 | 0 | 0 | 1.65025097 |
| laya_trained_on_model_only_low | 89 | 17 | 20 | 17/37 = 45.95% | 37/89 | 19.10%—77.53% | 51 | 0 | 0 | 0 | 0.30321960 |
| laya_trained_on_model_only_high | 89 | 17 | 13 | 17/30 = 56.67% | 30/89 | 19.10%—85.39% | 58 | 0 | 0 | 0 | 0.56356920 |
| laya_trained_on_model_only_max | 89 | 23 | 17 | 23/40 = 57.50% | 40/89 | 25.84%—80.90% | 48 | 0 | 0 | 0 | 1.33068723 |
| kev_original_off_model_only_low | 89 | 9 | 25 | 9/34 = 26.47% | 34/89 | 10.11%—71.91% | 54 | 0 | 0 | 0 | 0.16798241 |
| kev_original_off_model_only_high | 89 | 18 | 14 | 18/32 = 56.25% | 32/89 | 20.22%—84.27% | 55 | 0 | 0 | 0 | 0.30030459 |
| kev_original_off_model_only_max | 89 | 16 | 11 | 16/27 = 59.26% | 27/89 | 17.98%—87.64% | 60 | 0 | 0 | 0 | 0.45693488 |
| kev_original_on_model_only_low | 89 | 12 | 19 | 12/31 = 38.71% | 31/89 | 13.48%—78.65% | 55 | 0 | 0 | 0 | 0.13873072 |
| kev_original_on_model_only_high | 89 | 20 | 14 | 20/34 = 58.82% | 34/89 | 22.47%—84.27% | 53 | 0 | 0 | 0 | 0.27835046 |
| kev_original_on_model_only_max | 89 | 23 | 12 | 23/35 = 65.71% | 35/89 | 25.84%—86.52% | 53 | 0 | 0 | 0 | 0.60547926 |
| kev_trained_off_model_only_low | 89 | 49 | 19 | 49/68 = 72.06% | 68/89 | 55.06%—78.65% | 19 | 0 | 0 | 0 | 4.69426540 |
| kev_trained_off_model_only_high | 89 | 44 | 17 | 44/61 = 72.13% | 61/89 | 49.44%—80.90% | 26 | 0 | 0 | 0 | 5.88735000 |
| kev_trained_off_model_only_max | 89 | 36 | 14 | 36/50 = 72.00% | 50/89 | 40.45%—84.27% | 39 | 0 | 0 | 0 | 14.19867316 |
| kev_trained_on_model_only_low | 89 | 45 | 19 | 45/64 = 70.31% | 64/89 | 50.56%—78.65% | 24 | 0 | 0 | 0 | 3.96358259 |
| kev_trained_on_model_only_high | 89 | 45 | 15 | 45/60 = 75.00% | 60/89 | 50.56%—83.15% | 29 | 0 | 0 | 0 | 6.15896463 |
| kev_trained_on_model_only_max | 89 | 37 | 12 | 37/49 = 75.51% | 49/89 | 41.57%—86.52% | 40 | 0 | 0 | 0 | 12.32603560 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-22T05:49:13.808914+00:00，873005.800963秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入325,600,101、输出10,770,423 Token；2,617次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入86,805,571、输出912,874 Token；112次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取259,499,995 Token；3200次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求1978次，短评实际输入Router 2286次；同一短评可由多次决策消费。

Provider实际额外重试11152次；已记录技术恢复431次，涉及431个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度218次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

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
| AgentTimeoutError | 51 | 137 | 315 |
| EnvironmentStartTimeoutError | 0 | 0 | 7 |
| HTTPError | 0 | 0 | 2 |
| NO_RECORDED_ERROR | 527 | 234 | 14 |
| NonZeroAgentExitCodeError | 0 | 0 | 749 |
| OutputTokenExceededError | 1 | 28 | 2 |
| ProviderResponseError | 0 | 0 | 11 |
| RuntimeError | 0 | 0 | 14 |
| URLError | 0 | 0 | 24 |
| VerifierTimeoutError | 0 | 0 | 20 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 30 | 20/15 | 12 | 11/9 | 0.15087215 / 0.08625491 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 26 | 17/14 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 30 | 17/19 | 14 | 10/10 | 0.08925956 / 0.09361030 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 54 | 40/42 | 17 | 13/15 | 1.07391710 / 0.82136840 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 33 | 13/15 | 13 | 8/10 | 0.06240585 / 0.05617476 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 32 | 10/13 | 13 | 6/6 | 0.05695601 / 0.04980155 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 29 | 7/11 | 16 | 5/8 | 0.05322914 / 0.05156654 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 61 | 44/45 | 14 | 11/11 | 0.90135220 / 0.77315360 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 35 | 20/16 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 32 | 21/17 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 26 | 16/17 | 15 | 9/10 | 0.19307260 / 0.14507666 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 43 | 32/34 | 10 | 8/8 | 1.44344480 / 1.44001722 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 31 | 21/18 | 12 | 10/9 | 0.12355054 / 0.15023028 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 26 | 15/13 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 31 | 17/24 | 16 | 11/12 | 0.14304362 / 1.04773280 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 31 | 18/25 | 8 | 5/8 | 0.05701220 / 0.32804080 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 32 | 13/10 | 14 | 8/6 | 0.06814930 / 0.05659337 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 31 | 15/14 | 10 | 8/5 | 0.04734888 / 0.03517038 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 32 | 7/26 | 17 | 4/14 | 0.09529269 / 1.16029600 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 29 | 10/23 | 10 | 4/9 | 0.03066678 / 0.53483080 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 30 | 18/20 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 30 | 17/17 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 23 | 14/14 | 10 | 4/6 | 0.13292634 / 1.90964460 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 31 | 20/24 | 10 | 8/8 | 0.08273470 / 1.44001722 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 249, "gpt-6-luna:low": 352}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 268, "gpt-6-luna:high": 478}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 1090, "gpt-6-luna:max": 202}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 250, "gpt-6-luna:low": 336}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 157, "gpt-6-luna:high": 432}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 1020, "gpt-6-luna:max": 179}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 225, "gpt-6-luna:low": 321}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 224, "gpt-6-luna:high": 482}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 1132, "gpt-6-luna:max": 175}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 237, "gpt-6-luna:low": 302}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 196, "gpt-6-luna:high": 507}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 960, "gpt-6-luna:max": 175}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 427}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 513}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 510}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 387}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 526}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 504}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 1038, "gpt-6-luna:low": 3}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 1026, "gpt-6-luna:high": 8}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 1398, "gpt-6-luna:max": 20}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 1000, "gpt-6-luna:low": 3}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 1079, "gpt-6-luna:high": 11}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 1298, "gpt-6-luna:max": 21}`
