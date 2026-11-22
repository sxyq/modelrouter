# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束2134，运行中2，未开始0，渠道档位不可用0。有效官方任务评分1/0为603/419，缺有效评分 1101，原Verifier依赖失败11位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2610次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$59.48279797、教师$0.37275577，合计$59.85555374；2663次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1708710.654112秒，内含官方Trial累计1680359.799307秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；88题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 89 | 14 | 21 | 14/35 = 40.00% | 35/89 | 15.73%—76.40% | 54 | 0 | 0 | 0 | 0.32724930 |
| laya_original_off_model_only_high | 89 | 23 | 13 | 23/36 = 63.89% | 36/89 | 25.84%—85.39% | 52 | 0 | 0 | 0 | 0.77303198 |
| laya_original_off_model_only_max | 89 | 24 | 19 | 24/43 = 55.81% | 43/89 | 26.97%—78.65% | 46 | 0 | 0 | 0 | 1.85669133 |
| laya_original_on_model_only_low | 89 | 17 | 19 | 17/36 = 47.22% | 36/89 | 19.10%—78.65% | 53 | 0 | 0 | 0 | 0.30832067 |
| laya_original_on_model_only_high | 89 | 17 | 17 | 17/34 = 50.00% | 34/89 | 19.10%—80.90% | 55 | 0 | 0 | 0 | 0.40452980 |
| laya_original_on_model_only_max | 89 | 21 | 23 | 21/44 = 47.73% | 44/89 | 23.60%—74.16% | 44 | 0 | 0 | 0 | 1.85040462 |
| laya_trained_off_model_only_low | 89 | 12 | 26 | 12/38 = 31.58% | 38/89 | 13.48%—70.79% | 51 | 0 | 0 | 0 | 0.26923554 |
| laya_trained_off_model_only_high | 89 | 21 | 15 | 21/36 = 58.33% | 36/89 | 23.60%—83.15% | 53 | 0 | 0 | 0 | 0.64054141 |
| laya_trained_off_model_only_max | 89 | 26 | 18 | 26/44 = 59.09% | 44/89 | 29.21%—79.78% | 44 | 0 | 0 | 0 | 1.66795812 |
| laya_trained_on_model_only_low | 89 | 18 | 22 | 18/40 = 45.00% | 40/89 | 20.22%—75.28% | 49 | 0 | 0 | 0 | 0.31883931 |
| laya_trained_on_model_only_high | 89 | 18 | 15 | 18/33 = 54.55% | 33/89 | 20.22%—83.15% | 56 | 0 | 0 | 0 | 0.57120077 |
| laya_trained_on_model_only_max | 89 | 24 | 19 | 24/43 = 55.81% | 43/89 | 26.97%—78.65% | 46 | 0 | 0 | 0 | 1.33877681 |
| kev_original_off_model_only_low | 89 | 10 | 25 | 10/35 = 28.57% | 35/89 | 11.24%—71.91% | 54 | 0 | 0 | 0 | 0.16922775 |
| kev_original_off_model_only_high | 89 | 19 | 15 | 19/34 = 55.88% | 34/89 | 21.35%—83.15% | 54 | 0 | 0 | 0 | 0.30354137 |
| kev_original_off_model_only_max | 89 | 18 | 11 | 18/29 = 62.07% | 29/89 | 20.22%—87.64% | 59 | 0 | 0 | 0 | 0.46980744 |
| kev_original_on_model_only_low | 89 | 13 | 19 | 13/32 = 40.62% | 32/89 | 14.61%—78.65% | 55 | 0 | 0 | 0 | 0.14014950 |
| kev_original_on_model_only_high | 89 | 21 | 14 | 21/35 = 60.00% | 35/89 | 23.60%—84.27% | 53 | 0 | 0 | 0 | 0.28008608 |
| kev_original_on_model_only_max | 89 | 24 | 12 | 24/36 = 66.67% | 36/89 | 26.97%—86.52% | 53 | 0 | 0 | 0 | 0.60693006 |
| kev_trained_off_model_only_low | 89 | 50 | 19 | 50/69 = 72.46% | 69/89 | 56.18%—78.65% | 19 | 0 | 0 | 0 | 4.70555840 |
| kev_trained_off_model_only_high | 89 | 45 | 17 | 45/62 = 72.58% | 62/89 | 50.56%—80.90% | 26 | 0 | 0 | 0 | 5.90377560 |
| kev_trained_off_model_only_max | 89 | 38 | 14 | 38/52 = 73.08% | 52/89 | 42.70%—84.27% | 37 | 0 | 0 | 0 | 14.42139216 |
| kev_trained_on_model_only_low | 88 | 46 | 19 | 46/65 = 70.77% | 65/89 | 51.69%—78.65% | 22 | 1 | 0 | 0 | 3.99082909 |
| kev_trained_on_model_only_high | 89 | 47 | 15 | 47/62 = 75.81% | 62/89 | 52.81%—83.15% | 27 | 0 | 0 | 0 | 6.21144103 |
| kev_trained_on_model_only_max | 88 | 37 | 12 | 37/49 = 75.51% | 49/89 | 41.57%—86.52% | 39 | 1 | 0 | 0 | 12.32603560 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-22T09:21:53.293779+00:00，885765.285828秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入326,752,488、输出10,945,769 Token；2,646次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入87,874,932、输出924,484 Token；112次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取260,195,675 Token；3229次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求2001次，短评实际输入Router 2312次；同一短评可由多次决策消费。

Provider实际额外重试11301次；已记录技术恢复475次，涉及475个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度220次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

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
| AgentTimeoutError | 54 | 137 | 283 |
| EnvironmentStartTimeoutError | 0 | 0 | 2 |
| HTTPError | 0 | 0 | 2 |
| NO_RECORDED_ERROR | 548 | 243 | 7 |
| NonZeroAgentExitCodeError | 0 | 0 | 749 |
| OutputTokenExceededError | 1 | 39 | 2 |
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
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 32 | 21/16 | 13 | 12/10 | 0.15411037 / 0.08725091 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 29 | 18/15 | 9 | 7/6 | 0.05737206 / 0.02962023 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 32 | 18/20 | 15 | 10/10 | 0.09434766 / 0.10279992 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 56 | 42/44 | 17 | 13/15 | 1.07391710 / 0.82136840 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 35 | 14/16 | 13 | 8/10 | 0.06240585 / 0.05617476 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 35 | 11/14 | 13 | 6/6 | 0.05695601 / 0.04980155 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 30 | 8/12 | 17 | 6/9 | 0.05501044 / 0.05484822 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 62 | 45/46 | 14 | 11/11 | 0.90135220 / 0.77315360 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 38 | 21/17 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 35 | 22/18 | 6 | 5/5 | 0.07046604 / 0.08377243 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 28 | 18/19 | 16 | 10/11 | 0.19672380 / 0.14892206 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 44 | 33/35 | 10 | 8/8 | 1.44344480 / 1.44001722 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 34 | 22/19 | 12 | 10/9 | 0.12355054 / 0.15023028 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 29 | 16/14 | 9 | 7/6 | 0.05598340 / 0.05650303 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 33 | 18/26 | 17 | 11/13 | 0.14813172 / 1.09490380 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 33 | 19/27 | 8 | 5/8 | 0.05701220 / 0.32804080 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 35 | 14/11 | 14 | 8/6 | 0.06814930 / 0.05659337 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 34 | 16/15 | 10 | 8/5 | 0.04734888 / 0.03517038 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 33 | 8/27 | 17 | 4/14 | 0.09529269 / 1.16029600 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 29 | 10/23 | 10 | 4/9 | 0.03066678 / 0.53483080 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 33 | 19/21 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 33 | 18/18 | 6 | 4/4 | 0.15511911 / 0.12221184 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 25 | 16/16 | 10 | 4/6 | 0.13292634 / 1.90964460 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 250, "gpt-6-luna:low": 352}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 269, "gpt-6-luna:high": 478}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 1096, "gpt-6-luna:max": 202}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 251, "gpt-6-luna:low": 340}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 158, "gpt-6-luna:high": 436}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 1028, "gpt-6-luna:max": 183}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 234, "gpt-6-luna:low": 326}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 237, "gpt-6-luna:high": 487}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 1142, "gpt-6-luna:max": 182}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 247, "gpt-6-luna:low": 317}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 205, "gpt-6-luna:high": 514}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 968, "gpt-6-luna:max": 179}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 435}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 523}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 526}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 393}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 533}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 509}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 1045, "gpt-6-luna:low": 3}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 1033, "gpt-6-luna:high": 8}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 1432, "gpt-6-luna:max": 20}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 1009, "gpt-6-luna:low": 3}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 1095, "gpt-6-luna:high": 11}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 1298, "gpt-6-luna:max": 21}`
