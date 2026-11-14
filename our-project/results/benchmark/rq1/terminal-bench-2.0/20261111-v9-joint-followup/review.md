# Terminal-Bench 2.0 RQ1

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：0a9998aeb260f5e2a501212ed79d5904682afa87。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共54个任务/策略/seed位置；已结束54，运行中0，未开始0，渠道档位不可用0。有效官方任务评分1/0为42/2，缺有效评分 10，原Verifier依赖失败0位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 74次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$0.72700200、教师$0.00702650，合计$0.73402850；12次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。uvx缺失且没有测试报告的尝试另列，不计入正常任务质量对照。

Harbor命令累计墙钟25536.700316秒，内含官方Trial累计25157.790697秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：2/2题已有结束记录；2题已结束全部9个固定/简单策略；2题已结束全部27个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批2题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 2题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.02921835 |
| glm_high | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.03298917 |
| glm_max | 2 | 0 | 0 | 缺有效评分 | 0/2 | 0.00%—100.00% | 2 | 0 | 0 | 0 | 0.02288510 |
| luna_low | 2 | 1 | 1 | 1/2 = 50.00% | 2/2 | 50.00%—50.00% | 0 | 0 | 0 | 0 | 0.00584564 |
| luna_high | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.01336268 |
| luna_max | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03233184 |
| terra_high | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.09478440 |
| luna_xhigh | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.02299790 |
| rule_sticky | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.05821832 |
| laya_original_off | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03605180 |
| laya_original_on | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03337800 |
| laya_trained_off | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.01344669 |
| laya_trained_on | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02466572 |
| kev_original_off | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.00152466 |
| kev_original_on | 2 | 1 | 1 | 1/2 = 50.00% | 2/2 | 50.00%—50.00% | 0 | 0 | 0 | 0 | 0.00300610 |
| kev_trained_off | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02944120 |
| kev_trained_on | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03183710 |
| laya_trained_task_start | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.01878278 |
| laya_trained_phase | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02897511 |
| laya_trained_without_T | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02879390 |
| laya_trained_without_M | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02925930 |
| laya_trained_without_H | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03279433 |
| kev_trained_task_start | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.03110300 |
| kev_trained_phase | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.01750130 |
| kev_trained_without_T | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02588350 |
| kev_trained_without_M | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.00838441 |
| kev_trained_without_H | 2 | 2 | 0 | 2/2 = 100.00% | 2/2 | 100.00%—100.00% | 0 | 0 | 0 | 0 | 0.02656620 |

实际执行跨度：2026-11-11T15:59:42.521300+00:00至2026-11-11T18:23:50.893438+00:00，8648.372138秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/2；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入2,805,948、输出325,179 Token；12次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入1,216,085、输出23,867 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取1,964,032 Token；47次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求32次，短评实际输入Router 45次；同一短评可由多次决策消费。

Provider实际额外重试0次；本次技术恢复0位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| HTTPError | 0 | 0 | 7 |
| NO_RECORDED_ERROR | 42 | 2 | 0 |
| ProviderResponseError | 0 | 0 | 1 |
| RemoteDisconnected | 0 | 0 | 2 |

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
| granularity | laya_trained_on → laya_trained_task_start | 1 | 1/1 | 1 | 1/1 | 0.00779292 / 0.01836841 |
| granularity | laya_trained_on → laya_trained_phase | 2 | 2/2 | 1 | 1/1 | 0.00779292 / 0.01365537 |
| information | laya_trained_on → laya_trained_without_T | 2 | 2/2 | 2 | 2/2 | 0.02466572 / 0.02879390 |
| information | laya_trained_on → laya_trained_without_M | 2 | 2/2 | 2 | 2/2 | 0.02466572 / 0.02925930 |
| information | laya_trained_on → laya_trained_without_H | 2 | 2/2 | 1 | 1/1 | 0.01687280 / 0.02182617 |
| granularity | kev_trained_on → kev_trained_task_start | 2 | 2/2 | 2 | 2/2 | 0.03183710 / 0.03110300 |
| granularity | kev_trained_on → kev_trained_phase | 1 | 1/1 | 1 | 1/1 | 0.01004740 / 0.00987630 |
| information | kev_trained_on → kev_trained_without_T | 2 | 2/2 | 2 | 2/2 | 0.03183710 / 0.02588350 |
| information | kev_trained_on → kev_trained_without_M | 1 | 1/1 | 1 | 1/1 | 0.02178970 / 0.00568519 |
| information | kev_trained_on → kev_trained_without_H | 2 | 2/2 | 2 | 2/2 | 0.03183710 / 0.02656620 |

## 实际Router动作

以下登记实际选中模型及请求Native Effort；Model-only组固定档位、只选择模型。教师短评输入Router，不直接写入执行模型消息。

- laya_original_off: `{"glm-5.3-flash:high": 14, "gpt-6.1-terra:high": 5}`
- laya_original_on: `{"glm-5.3-flash:high": 4, "gpt-6.1-terra:high": 8}`
- laya_trained_off: `{"glm-5.3-flash:high": 9, "gpt-6.1-terra:high": 3, "gpt-6-luna:high": 2}`
- laya_trained_on: `{"glm-5.3-flash:high": 10, "gpt-6-luna:high": 3, "gpt-6.1-terra:high": 6}`
- kev_original_off: `{"gpt-6-luna:low": 6}`
- kev_original_on: `{"gpt-6-luna:low": 8}`
- kev_trained_off: `{"gpt-6.1-terra:medium": 10}`
- kev_trained_on: `{"gpt-6.1-terra:medium": 11}`
- laya_trained_task_start: `{"glm-5.3-flash:high": 2}`
- laya_trained_phase: `{"glm-5.3-flash:high": 4, "gpt-6-luna:high": 2, "gpt-6.1-terra:high": 4}`
- laya_trained_without_T: `{"gpt-6.1-terra:high": 10}`
- laya_trained_without_M: `{"gpt-6.1-terra:high": 11}`
- laya_trained_without_H: `{"glm-5.3-flash:high": 17, "gpt-6-luna:high": 1, "gpt-6.1-terra:high": 5}`
- kev_trained_task_start: `{"gpt-6.1-terra:medium": 2}`
- kev_trained_phase: `{"gpt-6.1-terra:medium": 5}`
- kev_trained_without_T: `{"gpt-6.1-terra:medium": 9}`
- kev_trained_without_M: `{"glm-5.3-flash:max": 10, "gpt-6-luna:medium": 3, "gpt-6-luna:high": 1, "gpt-6-luna:max": 1}`
- kev_trained_without_H: `{"gpt-6.1-terra:medium": 10}`
