# Terminal-Bench 2.0 · RQ2 Model-only

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：b9fba0a4488731c76718221e0572e5e7f2e8f936。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共2136个任务/策略/seed位置；已结束412，运行中2，未开始1722，渠道档位不可用0。有效官方任务评分1/0为53/9，无官方Reward 349，原Verifier依赖失败1位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 412次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$1.22693427、教师$0.01127140，合计$1.23820567；360次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟54218.144200秒，内含官方Trial累计51350.968258秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：18/89题已有结束记录；17题已结束全部24个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| laya_original_off_model_only_low | 18 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 15 | 0 | 71 | 0 | 0.00368824 |
| laya_original_off_model_only_high | 18 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 15 | 0 | 71 | 0 | 0.00597012 |
| laya_original_off_model_only_max | 18 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 16 | 0 | 71 | 0 | 0.04864646 |
| laya_original_on_model_only_low | 18 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 15 | 0 | 71 | 0 | 0.00554765 |
| laya_original_on_model_only_high | 17 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 14 | 1 | 71 | 0 | 0.01092446 |
| laya_original_on_model_only_max | 17 | 1 | 1 | 1/2 = 50.00% | 2/89 | 1.12%—98.88% | 15 | 1 | 71 | 0 | 0.03384522 |
| laya_trained_off_model_only_low | 17 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 14 | 0 | 72 | 0 | 0.00355368 |
| laya_trained_off_model_only_high | 17 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 15 | 0 | 72 | 0 | 0.00863602 |
| laya_trained_off_model_only_max | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.06779328 |
| laya_trained_on_model_only_low | 17 | 1 | 1 | 1/2 = 50.00% | 2/89 | 1.12%—98.88% | 15 | 0 | 72 | 0 | 0.00261199 |
| laya_trained_on_model_only_high | 17 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 15 | 0 | 72 | 0 | 0.01524458 |
| laya_trained_on_model_only_max | 17 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 14 | 0 | 72 | 0 | 0.05387129 |
| kev_original_off_model_only_low | 17 | 1 | 2 | 1/3 = 33.33% | 3/89 | 1.12%—97.75% | 14 | 0 | 72 | 0 | 0.00364148 |
| kev_original_off_model_only_high | 17 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 14 | 0 | 72 | 0 | 0.00879406 |
| kev_original_off_model_only_max | 17 | 1 | 0 | 1/1 = 100.00% | 1/89 | 1.12%—100.00% | 16 | 0 | 72 | 0 | 0.00808468 |
| kev_original_on_model_only_low | 17 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 15 | 0 | 72 | 0 | 0.00426668 |
| kev_original_on_model_only_high | 17 | 2 | 0 | 2/2 = 100.00% | 2/89 | 2.25%—100.00% | 15 | 0 | 72 | 0 | 0.00759958 |
| kev_original_on_model_only_max | 17 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 14 | 0 | 72 | 0 | 0.01173330 |
| kev_trained_off_model_only_low | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.05154140 |
| kev_trained_off_model_only_high | 17 | 2 | 1 | 2/3 = 66.67% | 3/89 | 2.25%—98.88% | 14 | 0 | 72 | 0 | 0.05637600 |
| kev_trained_off_model_only_max | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.30960480 |
| kev_trained_on_model_only_low | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.07498780 |
| kev_trained_on_model_only_high | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.06776670 |
| kev_trained_on_model_only_max | 17 | 3 | 0 | 3/3 = 100.00% | 3/89 | 3.37%—100.00% | 14 | 0 | 72 | 0 | 0.37347620 |

评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入4,168,203、输出374,488 Token；360次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入3,613,682、输出37,145 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取2,866,624 Token；419次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求58次，短评实际输入Router 86次；同一短评可由多次决策消费。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 7 | 3 | 0 |
| HTTPError | 0 | 0 | 5 |
| NO_RECORDED_ERROR | 46 | 7 | 0 |
| ProviderResponseError | 0 | 0 | 12 |
| URLError | 0 | 0 | 330 |
| VerifierTimeoutError | 0 | 0 | 2 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 2 | 2/2 | 2 | 2/2 | 0.03605180 / 0.03337800 |
| teacher | laya_trained_off → laya_trained_on | 1 | 1/1 | 1 | 1/1 | 0.01114295 / 0.01687280 |
| teacher | kev_original_off → kev_original_on | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.00174950 |
| teacher | kev_trained_off → kev_trained_on | 2 | 2/2 | 2 | 2/2 | 0.02944120 / 0.03183710 |
| teacher | laya_original_off_model_only_high → laya_original_on_model_only_high | 3 | 3/2 | 3 | 3/2 | 0.00597012 / 0.01072316 |
| teacher | laya_trained_off_model_only_high → laya_trained_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00189886 / 0.00117462 |
| teacher | kev_original_off_model_only_high → kev_original_on_model_only_high | 1 | 1/1 | 1 | 1/1 | 0.00186484 / 0.00348850 |
| teacher | kev_trained_off_model_only_high → kev_trained_on_model_only_high | 3 | 2/3 | 3 | 2/3 | 0.05637600 / 0.06776670 |
| teacher | laya_original_off_model_only_low → laya_original_on_model_only_low | 3 | 3/3 | 3 | 3/3 | 0.00368824 / 0.00554765 |
| teacher | laya_trained_off_model_only_low → laya_trained_on_model_only_low | 2 | 2/1 | 2 | 2/1 | 0.00247944 / 0.00241099 |
| teacher | kev_original_off_model_only_low → kev_original_on_model_only_low | 1 | 0/1 | 1 | 0/1 | 0.00000000 / 0.00171380 |
| teacher | kev_trained_off_model_only_low → kev_trained_on_model_only_low | 3 | 3/3 | 1 | 1/1 | 0.01318740 / 0.03532380 |
| teacher | laya_original_off_model_only_max → laya_original_on_model_only_max | 1 | 1/0 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | laya_trained_off_model_only_max → laya_trained_on_model_only_max | 3 | 3/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| teacher | kev_original_off_model_only_max → kev_original_on_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00180800 / 0.00410170 |
| teacher | kev_trained_off_model_only_max → kev_trained_on_model_only_max | 3 | 3/3 | 2 | 2/2 | 0.26640480 / 0.30910010 |
| training | laya_original_off → laya_trained_off | 1 | 1/1 | 1 | 1/1 | 0.02697344 / 0.01114295 |
| training | laya_original_on → laya_trained_on | 2 | 2/2 | 2 | 2/2 | 0.03337800 / 0.02466572 |
| training | kev_original_off → kev_trained_off | 1 | 1/1 | 1 | 1/1 | 0.00152466 / 0.01547080 |
| training | kev_original_on → kev_trained_on | 2 | 1/2 | 2 | 1/2 | 0.00300610 / 0.03183710 |
| training | laya_original_off_model_only_high → laya_trained_off_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.00341877 / 0.00814146 |
| training | laya_original_on_model_only_high → laya_trained_on_model_only_high | 2 | 2/2 | 2 | 2/2 | 0.00354336 / 0.00377197 |
| training | kev_original_off_model_only_high → kev_trained_off_model_only_high | 2 | 2/1 | 2 | 2/1 | 0.00283438 / 0.02604120 |
| training | kev_original_on_model_only_high → kev_trained_on_model_only_high | 2 | 2/2 | 1 | 1/1 | 0.00348850 / 0.03429790 |
| training | laya_original_off_model_only_low → laya_trained_off_model_only_low | 3 | 3/2 | 3 | 3/2 | 0.00368824 / 0.00355368 |
| training | laya_original_on_model_only_low → laya_trained_on_model_only_low | 2 | 2/1 | 2 | 2/1 | 0.00385207 / 0.00241099 |
| training | kev_original_off_model_only_low → kev_trained_off_model_only_low | 2 | 1/2 | 2 | 1/2 | 0.00134390 / 0.02600920 |
| training | kev_original_on_model_only_low → kev_trained_on_model_only_low | 2 | 2/2 | 1 | 1/1 | 0.00171380 / 0.03532380 |
| training | laya_original_off_model_only_max → laya_trained_off_model_only_max | 2 | 2/2 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| training | laya_original_on_model_only_max → laya_trained_on_model_only_max | 2 | 1/1 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| training | kev_original_off_model_only_max → kev_trained_off_model_only_max | 1 | 1/1 | 1 | 1/1 | 0.00180800 / 0.12910040 |
| training | kev_original_on_model_only_max → kev_trained_on_model_only_max | 3 | 2/3 | 2 | 2/2 | 0.00905588 / 0.30910010 |
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
| joint_vs_model_only | kev_original_off → kev_original_off_model_only_low | 1 | 1/0 | 1 | 1/0 | 0.00152466 / 0.00000000 |
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

- laya_original_off_model_only_low: `{"glm-5.3-flash:low": 9, "gpt-6-luna:low": 19}`
- laya_original_off_model_only_high: `{"glm-5.3-flash:high": 9, "gpt-6-luna:high": 22}`
- laya_original_off_model_only_max: `{"glm-5.3-flash:max": 70, "gpt-6-luna:max": 4}`
- laya_original_on_model_only_low: `{"glm-5.3-flash:low": 17, "gpt-6-luna:low": 13}`
- laya_original_on_model_only_high: `{"glm-5.3-flash:high": 9, "gpt-6-luna:high": 24}`
- laya_original_on_model_only_max: `{"glm-5.3-flash:max": 51, "gpt-6-luna:max": 1}`
- laya_trained_off_model_only_low: `{"glm-5.3-flash:low": 9, "gpt-6-luna:low": 18}`
- laya_trained_off_model_only_high: `{"glm-5.3-flash:high": 7, "gpt-6-luna:high": 26}`
- laya_trained_off_model_only_max: `{"glm-5.3-flash:max": 86, "gpt-6-luna:max": 1}`
- laya_trained_on_model_only_low: `{"glm-5.3-flash:low": 12, "gpt-6-luna:low": 13}`
- laya_trained_on_model_only_high: `{"glm-5.3-flash:high": 10, "gpt-6-luna:high": 26}`
- laya_trained_on_model_only_max: `{"glm-5.3-flash:max": 47, "gpt-6-luna:max": 1}`
- kev_original_off_model_only_low: `{"gpt-6-luna:low": 27}`
- kev_original_off_model_only_high: `{"gpt-6-luna:high": 32}`
- kev_original_off_model_only_max: `{"gpt-6-luna:max": 25}`
- kev_original_on_model_only_low: `{"gpt-6-luna:low": 25}`
- kev_original_on_model_only_high: `{"gpt-6-luna:high": 29}`
- kev_original_on_model_only_max: `{"gpt-6-luna:max": 27}`
- kev_trained_off_model_only_low: `{"gpt-6.1-terra:low": 30}`
- kev_trained_off_model_only_high: `{"gpt-6.1-terra:high": 30}`
- kev_trained_off_model_only_max: `{"gpt-6.1-terra:max": 50}`
- kev_trained_on_model_only_low: `{"gpt-6.1-terra:low": 33}`
- kev_trained_on_model_only_high: `{"gpt-6.1-terra:high": 32}`
- kev_trained_on_model_only_max: `{"gpt-6.1-terra:max": 59}`
