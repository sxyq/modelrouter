# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束882，运行中2，未开始1252，渠道档位不可用0。有效官方任务评分1/0为241/108，缺有效评分 501，原Verifier依赖失败32位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 883次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$11.31481424、教师$0.14765606，合计$11.46247030；544次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟461727.895957秒，内含官方Trial累计441751.423835秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：37/89题已有结束记录；36题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 37 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 21 | 0 | 52 | 0 | 0.10578229 |
| laya_original_off_model_only_high | 37 | 14 | 1 | 14/15 = 93.33% | 15/89 | 15.73%—98.88% | 20 | 0 | 52 | 0 | 0.20510783 |
| laya_original_off_model_only_max | 37 | 9 | 4 | 9/13 = 69.23% | 13/89 | 10.11%—95.51% | 23 | 0 | 52 | 0 | 0.40353204 |
| laya_original_on_model_only_low | 37 | 9 | 3 | 9/12 = 75.00% | 12/89 | 10.11%—96.63% | 25 | 0 | 52 | 0 | 0.08966466 |
| laya_original_on_model_only_high | 37 | 8 | 4 | 8/12 = 66.67% | 12/89 | 8.99%—95.51% | 25 | 0 | 52 | 0 | 0.14857432 |
| laya_original_on_model_only_max | 37 | 6 | 6 | 6/12 = 50.00% | 12/89 | 6.74%—93.26% | 24 | 0 | 52 | 0 | 0.35890173 |
| laya_trained_off_model_only_low | 37 | 7 | 8 | 7/15 = 46.67% | 15/89 | 7.87%—91.01% | 21 | 0 | 52 | 0 | 0.11459742 |
| laya_trained_off_model_only_high | 37 | 10 | 3 | 10/13 = 76.92% | 13/89 | 11.24%—96.63% | 24 | 0 | 52 | 0 | 0.16022710 |
| laya_trained_off_model_only_max | 37 | 11 | 2 | 11/13 = 84.62% | 13/89 | 12.36%—97.75% | 23 | 0 | 52 | 0 | 0.34252154 |
| laya_trained_on_model_only_low | 37 | 8 | 7 | 8/15 = 53.33% | 15/89 | 8.99%—92.13% | 21 | 0 | 52 | 0 | 0.13372099 |
| laya_trained_on_model_only_high | 37 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 21 | 0 | 52 | 0 | 0.18850761 |
| laya_trained_on_model_only_max | 37 | 12 | 5 | 12/17 = 70.59% | 17/89 | 13.48%—94.38% | 19 | 0 | 52 | 0 | 0.39002771 |
| kev_original_off_model_only_low | 37 | 5 | 10 | 5/15 = 33.33% | 15/89 | 5.62%—88.76% | 19 | 0 | 52 | 0 | 0.06250294 |
| kev_original_off_model_only_high | 37 | 10 | 5 | 10/15 = 66.67% | 15/89 | 11.24%—94.38% | 18 | 0 | 52 | 0 | 0.11287140 |
| kev_original_off_model_only_max | 37 | 9 | 5 | 9/14 = 64.29% | 14/89 | 10.11%—94.38% | 22 | 0 | 52 | 0 | 0.23571384 |
| kev_original_on_model_only_low | 37 | 9 | 7 | 9/16 = 56.25% | 16/89 | 10.11%—92.13% | 18 | 0 | 52 | 0 | 0.05790728 |
| kev_original_on_model_only_high | 37 | 10 | 6 | 10/16 = 62.50% | 16/89 | 11.24%—93.26% | 19 | 0 | 52 | 0 | 0.12573470 |
| kev_original_on_model_only_max | 37 | 14 | 5 | 14/19 = 73.68% | 19/89 | 15.73%—94.38% | 17 | 0 | 52 | 0 | 0.20927598 |
| kev_trained_off_model_only_low | 36 | 14 | 1 | 14/15 = 93.33% | 15/89 | 15.73%—98.88% | 18 | 1 | 52 | 0 | 0.92437420 |
| kev_trained_off_model_only_high | 36 | 12 | 5 | 12/17 = 70.59% | 17/89 | 13.48%—94.38% | 17 | 1 | 52 | 0 | 1.12103240 |
| kev_trained_off_model_only_max | 36 | 9 | 6 | 9/15 = 60.00% | 15/89 | 10.11%—93.26% | 21 | 0 | 53 | 0 | 2.21780410 |
| kev_trained_on_model_only_low | 36 | 11 | 1 | 11/12 = 91.67% | 12/89 | 12.36%—98.88% | 22 | 0 | 53 | 0 | 0.68841500 |
| kev_trained_on_model_only_high | 36 | 13 | 0 | 13/13 = 100.00% | 13/89 | 14.61%—100.00% | 22 | 0 | 53 | 0 | 0.80029450 |
| kev_trained_on_model_only_max | 36 | 12 | 2 | 12/14 = 85.71% | 14/89 | 13.48%—97.75% | 21 | 0 | 53 | 0 | 2.26537872 |

实际执行跨度：2026-11-12T03:19:08.007951+00:00至2026-11-15T00:50:14.850614+00:00，250266.842663秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入55,000,896、输出3,219,007 Token；544次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入25,468,587、输出238,980 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取36,949,952 Token；889次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求603次，短评实际输入Router 1070次；同一短评可由多次决策消费。

Provider实际额外重试2205次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 32 | 47 | 92 |
| EnvironmentStartTimeoutError | 0 | 0 | 5 |
| HTTPError | 0 | 0 | 8 |
| JSONDecodeError | 0 | 0 | 1 |
| NO_RECORDED_ERROR | 209 | 61 | 34 |
| ProviderResponseError | 0 | 0 | 26 |
| RemoteDisconnected | 0 | 0 | 2 |
| URLError | 0 | 0 | 352 |
| VerifierTimeoutError | 0 | 0 | 13 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 11 | 10/8 | 10 | 10/8 | 0.07385039 / 0.06678743 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 11 | 8/5 | 8 | 6/5 | 0.05165244 / 0.02520919 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 14 | 9/9 | 13 | 9/9 | 0.07743622 / 0.08966418 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 11 | 9/11 | 11 | 9/11 | 0.46405990 / 0.43085990 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 11 | 7/9 | 11 | 7/9 | 0.05492839 / 0.05239172 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 13 | 6/7 | 10 | 5/6 | 0.04954661 / 0.04216976 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 12 | 4/5 | 12 | 4/5 | 0.03896320 / 0.04115536 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 12 | 11/11 | 9 | 8/8 | 0.51326580 / 0.45521990 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 9 | 7/5 | 5 | 4/5 | 0.08708049 / 0.13727857 |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 13 | 11/8 | 4 | 4/4 | 0.05784453 / 0.06915825 |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 13 | 8/9 | 13 | 8/9 | 0.17381290 / 0.12932188 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 11 | 8/10 | 7 | 7/6 | 0.92315090 / 0.91745930 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 11 | 10/9 | 9 | 9/8 | 0.04455826 / 0.05373912 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 10 | 7/5 | 8 | 6/5 | 0.05135348 / 0.05209199 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 11 | 6/8 | 11 | 6/8 | 0.07050658 / 0.69210210 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 9 | 5/9 | 6 | 3/6 | 0.04774198 / 0.25828660 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 12 | 7/5 | 12 | 7/5 | 0.06009329 / 0.05221209 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 11 | 8/5 | 9 | 7/5 | 0.04502892 / 0.03214226 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 9 | 2/8 | 9 | 2/8 | 0.04237714 / 0.48467620 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 10 | 4/9 | 8 | 3/7 | 0.02414830 / 0.41379740 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 10 | 7/9 | 5 | 4/5 | 0.11812642 / 0.07792263 |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 11 | 6/6 | 4 | 3/3 | 0.12705041 / 0.09730156 |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 9 | 5/4 | 7 | 3/4 | 0.10414232 / 1.25107270 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 13 | 10/11 | 7 | 6/6 | 0.06304742 / 0.91745930 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 89, "gpt-6-luna:low": 128}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 82, "gpt-6-luna:high": 161}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 301, "gpt-6-luna:max": 64}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 81, "gpt-6-luna:low": 103}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 42, "gpt-6-luna:high": 190}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 268, "gpt-6-luna:max": 33}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 108, "gpt-6-luna:low": 116}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 64, "gpt-6-luna:high": 181}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 323, "gpt-6-luna:max": 32}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 79, "gpt-6-luna:low": 137}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 51, "gpt-6-luna:high": 256}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 322, "gpt-6-luna:max": 48}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 166}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 237}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 260}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 145}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 236}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 251}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 195}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 206, "gpt-6-luna:high": 2}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 231, "gpt-6-luna:max": 3}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 173}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 186, "gpt-6-luna:high": 2}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 272, "gpt-6-luna:max": 6}`
