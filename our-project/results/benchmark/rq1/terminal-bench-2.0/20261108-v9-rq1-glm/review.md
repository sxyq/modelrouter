# Terminal-Bench 2.0 RQ1

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：cb4371da0635d9d550314b6703af4cbe87f0b714。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共1513个任务/策略/seed位置；已结束1512，运行中1，未开始0，渠道档位不可用0。有效官方任务评分1/0为404/459，缺有效评分 597，原Verifier依赖失败52位置另列；固定组已报告档位不符另列，Router组保留实际Reward及内部请求/返回档位差异。

已保存原Harbor Trial 3028次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$52.95619505、教师$0.14386542，合计$53.10006047；1474次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部已结束尝试。逐Episode表的latest_trial_*字段单列最后一次运行的参考费和API Token。official_reward保留原分数；缺有效评分包含未返回Reward及已记录请求/资源故障的原0。官方测试依赖缺失且未执行任务断言的尝试另列。

Harbor命令累计墙钟1553290.677758秒，内含官方Trial累计1534049.797913秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；88题已结束全部9个固定/简单策略；88题已结束全部17个策略。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺有效评分不补0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺有效评分 | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 89 | 42 | 44 | 42/86 = 48.84% | 86/89 | 47.19%—50.56% | 3 | 0 | 0 | 0 | 2.48989393 |
| glm_high | 88 | 38 | 44 | 38/82 = 46.34% | 82/89 | 42.70%—50.56% | 5 | 1 | 0 | 0 | 3.88593190 |
| glm_max | 89 | 35 | 37 | 35/72 = 48.61% | 72/89 | 39.33%—58.43% | 17 | 0 | 0 | 0 | 3.42192357 |
| luna_low | 89 | 21 | 57 | 21/78 = 26.92% | 78/89 | 23.60%—35.96% | 10 | 0 | 0 | 0 | 0.43558043 |
| luna_high | 89 | 29 | 47 | 29/76 = 38.16% | 76/89 | 32.58%—47.19% | 12 | 0 | 0 | 0 | 1.20460446 |
| luna_max | 89 | 32 | 42 | 32/74 = 43.24% | 74/89 | 35.96%—52.81% | 14 | 0 | 0 | 0 | 2.78246697 |
| terra_high | 89 | 52 | 31 | 52/83 = 62.65% | 83/89 | 58.43%—65.17% | 6 | 0 | 0 | 0 | 11.10484360 |
| luna_xhigh | 89 | 39 | 39 | 39/78 = 50.00% | 78/89 | 43.82%—56.18% | 11 | 0 | 0 | 0 | 2.42927025 |
| rule_sticky | 89 | 29 | 13 | 29/42 = 69.05% | 42/89 | 32.58%—85.39% | 40 | 0 | 0 | 0 | 3.51316246 |
| laya_original_off | 89 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 77 | 0 | 0 | 0 | 0.36278281 |
| laya_original_on | 89 | 3 | 5 | 3/8 = 37.50% | 8/89 | 3.37%—94.38% | 81 | 0 | 0 | 0 | 0.26023004 |
| laya_trained_off | 89 | 4 | 3 | 4/7 = 57.14% | 7/89 | 4.49%—96.63% | 81 | 0 | 0 | 0 | 0.18498189 |
| laya_trained_on | 89 | 3 | 5 | 3/8 = 37.50% | 8/89 | 3.37%—94.38% | 81 | 0 | 0 | 0 | 0.27858662 |
| kev_original_off | 89 | 11 | 42 | 11/53 = 20.75% | 53/89 | 12.36%—52.81% | 21 | 0 | 0 | 0 | 0.24247332 |
| kev_original_on | 89 | 17 | 34 | 17/51 = 33.33% | 51/89 | 19.10%—61.80% | 28 | 0 | 0 | 0 | 0.28372402 |
| kev_trained_off | 89 | 16 | 4 | 16/20 = 80.00% | 20/89 | 17.98%—95.51% | 63 | 0 | 0 | 0 | 9.19439320 |
| kev_trained_on | 89 | 26 | 7 | 26/33 = 78.79% | 33/89 | 29.21%—92.13% | 47 | 0 | 0 | 0 | 11.02521100 |

实际执行跨度：2026-11-08T15:48:04.949644+00:00至2026-11-21T16:40:38.384472+00:00，1126353.434828秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

已报告输入456,262,158、输出13,927,786 Token；1,466次请求缺用量。推理包含在输出内，缓存读取包含在输入内，各只计一次；数值包含模型、教师及全部已发生尝试。

Router本地前向另报告输入34,619,004、输出1,158,807 Token；0次决策缺用量。其计算费用按A6000资源计量，美元单价未知。

Provider实际报告缓存读取379,542,716 Token；2112次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求473次，短评实际输入Router 886次；同一短评可由多次决策消费。

Provider实际额外重试3130次；已记录技术恢复696次，涉及404个位置。最多额外100次，原任务时限有效，4096输出耗尽不重试；逐尝试原因、耗时及已知消费沿PROVIDER_ATTEMPT和account_attempts保存。

Provider报告输出超过请求额度376次；其中2个额度终止位置单列渠道故障，原官方Reward及全部费用保留。请求额度内的正常length原0继续保留；不因本项重复已评分任务。

已记录Router输入截断4次，涉及3个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|
| gpt-6.1-terra | none | medium | 52 |

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺有效评分 |
|---|---:|---:|---:|
| AgentTimeoutError | 40 | 175 | 63 |
| EnvironmentStartTimeoutError | 0 | 0 | 28 |
| HTTPError | 0 | 0 | 294 |
| NO_RECORDED_ERROR | 364 | 264 | 34 |
| NonZeroAgentExitCodeError | 0 | 0 | 5 |
| OutputTokenExceededError | 0 | 20 | 3 |
| ProviderResponseError | 0 | 0 | 106 |
| RemoteDisconnected | 0 | 0 | 14 |
| RuntimeError | 0 | 0 | 30 |
| URLError | 0 | 0 | 30 |
| ValueError | 0 | 0 | 2 |
| VerifierTimeoutError | 0 | 0 | 41 |

## 同题训练、教师与消融对照

评分对只包含两侧均有有效任务评分的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 5 | 3/3 | 4 | 3/3 | 0.08898859 / 0.11227356 |
| teacher | laya_trained_off → laya_trained_on | 5 | 3/3 | 5 | 3/3 | 0.09012806 / 0.13704358 |
| teacher | kev_original_off → kev_original_on | 41 | 10/12 | 19 | 6/7 | 0.06643734 / 0.07751724 |
| teacher | kev_trained_off → kev_trained_on | 12 | 11/12 | 7 | 7/7 | 0.63499980 / 0.71903530 |
| training | laya_original_off → laya_trained_off | 7 | 5/4 | 6 | 5/4 | 0.07787562 / 0.09658031 |
| training | laya_original_on → laya_trained_on | 4 | 3/3 | 4 | 3/3 | 0.07499469 / 0.12199358 |
| training | kev_original_off → kev_trained_off | 17 | 6/14 | 9 | 4/8 | 0.03084862 / 0.84991960 |
| training | kev_original_on → kev_trained_on | 25 | 11/21 | 13 | 8/11 | 0.05194438 / 1.21800562 |
| fixed_vs_router | glm_low → laya_original_off | 12 | 8/7 | 4 | 3/3 | 0.08251028 / 0.06967313 |
| fixed_vs_router | glm_low → laya_original_on | 8 | 4/3 | 2 | 1/1 | 0.04227675 / 0.03723031 |
| fixed_vs_router | glm_low → laya_trained_off | 7 | 5/4 | 2 | 2/1 | 0.02393492 / 0.03696540 |
| fixed_vs_router | glm_low → laya_trained_on | 8 | 5/3 | 3 | 2/1 | 0.06114758 / 0.07356230 |
| fixed_vs_router | glm_low → kev_original_off | 52 | 28/11 | 9 | 7/2 | 0.14226416 / 0.02652834 |
| fixed_vs_router | glm_low → kev_original_on | 49 | 27/17 | 9 | 8/5 | 0.06997897 / 0.03290178 |
| fixed_vs_router | glm_low → kev_trained_off | 18 | 12/15 | 6 | 5/5 | 0.07586243 / 0.38610720 |
| fixed_vs_router | glm_low → kev_trained_on | 32 | 21/25 | 6 | 5/5 | 0.05607484 / 0.54069952 |
| fixed_vs_router | glm_high → laya_original_off | 11 | 6/7 | 2 | 1/1 | 0.04560641 / 0.05177554 |
| fixed_vs_router | glm_high → laya_original_on | 8 | 4/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → laya_trained_off | 6 | 4/4 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → laya_trained_on | 7 | 6/3 | 0 | 0/0 | UNKNOWN / UNKNOWN |
| fixed_vs_router | glm_high → kev_original_off | 47 | 24/10 | 4 | 2/1 | 0.10132981 / 0.01407712 |
| fixed_vs_router | glm_high → kev_original_on | 46 | 27/15 | 5 | 4/3 | 0.07217661 / 0.01289234 |
| fixed_vs_router | glm_high → kev_trained_off | 18 | 12/15 | 4 | 3/3 | 0.08095072 / 0.21023380 |
| fixed_vs_router | glm_high → kev_trained_on | 31 | 17/24 | 3 | 3/3 | 0.03944069 / 0.17267320 |
| fixed_vs_router | glm_max → laya_original_off | 12 | 6/7 | 4 | 4/3 | 0.08384967 / 0.06967313 |
| fixed_vs_router | glm_max → laya_original_on | 7 | 4/3 | 1 | 1/1 | 0.02156601 / 0.02143155 |
| fixed_vs_router | glm_max → laya_trained_off | 7 | 5/4 | 2 | 2/1 | 0.03714903 / 0.03696540 |
| fixed_vs_router | glm_max → laya_trained_on | 8 | 6/3 | 2 | 2/1 | 0.03714903 / 0.05654096 |
| fixed_vs_router | glm_max → kev_original_off | 43 | 24/10 | 5 | 3/1 | 0.11250134 / 0.01839356 |
| fixed_vs_router | glm_max → kev_original_on | 43 | 25/16 | 4 | 2/2 | 0.07571076 / 0.01927756 |
| fixed_vs_router | glm_max → kev_trained_off | 17 | 13/13 | 3 | 3/2 | 0.06826665 / 0.19350780 |
| fixed_vs_router | glm_max → kev_trained_on | 28 | 16/23 | 2 | 2/2 | 0.03431255 / 0.25431890 |
| fixed_vs_router | luna_low → laya_original_off | 11 | 6/7 | 10 | 5/6 | 0.02694966 / 0.21509818 |
| fixed_vs_router | luna_low → laya_original_on | 6 | 3/3 | 4 | 2/2 | 0.00797138 / 0.06266532 |
| fixed_vs_router | luna_low → laya_trained_off | 7 | 5/4 | 5 | 4/3 | 0.01082580 / 0.05293034 |
| fixed_vs_router | luna_low → laya_trained_on | 8 | 4/3 | 6 | 3/2 | 0.01571662 / 0.11392771 |
| fixed_vs_router | luna_low → kev_original_off | 49 | 12/11 | 18 | 6/5 | 0.05023642 / 0.04973600 |
| fixed_vs_router | luna_low → kev_original_on | 48 | 15/17 | 20 | 9/9 | 0.05493554 / 0.07630440 |
| fixed_vs_router | luna_low → kev_trained_off | 19 | 7/15 | 8 | 4/7 | 0.02689176 / 0.65006960 |
| fixed_vs_router | luna_low → kev_trained_on | 30 | 10/24 | 14 | 6/10 | 0.03786086 / 2.34515584 |
| fixed_vs_router | luna_high → laya_original_off | 10 | 5/6 | 9 | 4/5 | 0.11399640 / 0.19650939 |
| fixed_vs_router | luna_high → laya_original_on | 5 | 2/2 | 4 | 2/2 | 0.01932024 / 0.06266532 |
| fixed_vs_router | luna_high → laya_trained_off | 6 | 3/3 | 4 | 2/2 | 0.03764212 / 0.04647809 |
| fixed_vs_router | luna_high → laya_trained_on | 7 | 3/2 | 5 | 2/2 | 0.04511198 / 0.11079283 |
| fixed_vs_router | luna_high → kev_original_off | 50 | 19/10 | 18 | 7/4 | 0.27262882 / 0.06553768 |
| fixed_vs_router | luna_high → kev_original_on | 48 | 22/16 | 18 | 10/7 | 0.22937926 / 0.07538572 |
| fixed_vs_router | luna_high → kev_trained_off | 18 | 11/15 | 7 | 5/6 | 0.06143726 / 0.60758160 |
| fixed_vs_router | luna_high → kev_trained_on | 30 | 16/24 | 11 | 7/8 | 0.06313434 / 2.08250654 |
| fixed_vs_router | luna_max → laya_original_off | 11 | 5/7 | 7 | 4/5 | 0.13900242 / 0.19170243 |
| fixed_vs_router | luna_max → laya_original_on | 6 | 3/3 | 5 | 3/3 | 0.06183796 / 0.09478659 |
| fixed_vs_router | luna_max → laya_trained_off | 7 | 4/4 | 4 | 3/3 | 0.04903994 / 0.08396618 |
| fixed_vs_router | luna_max → laya_trained_on | 8 | 3/3 | 6 | 3/3 | 0.07671818 / 0.13553430 |
| fixed_vs_router | luna_max → kev_original_off | 49 | 22/11 | 16 | 6/4 | 0.35937274 / 0.06547444 |
| fixed_vs_router | luna_max → kev_original_on | 48 | 24/16 | 18 | 9/7 | 0.34134164 / 0.07415322 |
| fixed_vs_router | luna_max → kev_trained_off | 19 | 13/16 | 9 | 6/8 | 0.13113040 / 0.85565920 |
| fixed_vs_router | luna_max → kev_trained_on | 31 | 18/24 | 11 | 6/8 | 0.18060656 / 2.00818342 |
| fixed_vs_router | terra_high → laya_original_off | 12 | 9/7 | 10 | 7/6 | 0.26408060 / 0.25530884 |
| fixed_vs_router | terra_high → laya_original_on | 7 | 4/3 | 5 | 2/2 | 0.37004280 / 0.11574295 |
| fixed_vs_router | terra_high → laya_trained_off | 7 | 6/4 | 4 | 3/3 | 0.07482860 / 0.04676846 |
| fixed_vs_router | terra_high → laya_trained_on | 8 | 6/3 | 5 | 3/2 | 0.11418460 / 0.09226221 |
| fixed_vs_router | terra_high → kev_original_off | 51 | 37/11 | 18 | 11/5 | 0.60149940 / 0.06316214 |
| fixed_vs_router | terra_high → kev_original_on | 50 | 38/17 | 20 | 15/10 | 0.99532340 / 0.08961542 |
| fixed_vs_router | terra_high → kev_trained_off | 19 | 17/16 | 8 | 7/7 | 0.17945540 / 0.65006960 |
| fixed_vs_router | terra_high → kev_trained_on | 33 | 25/26 | 15 | 11/11 | 0.40650320 / 2.39262474 |
| fixed_vs_router | luna_xhigh → laya_original_off | 10 | 4/6 | 6 | 4/4 | 0.10109108 / 0.17018453 |
| fixed_vs_router | luna_xhigh → laya_original_on | 5 | 2/2 | 4 | 2/2 | 0.02107010 / 0.06266532 |
| fixed_vs_router | luna_xhigh → laya_trained_off | 6 | 3/3 | 3 | 3/3 | 0.02822126 / 0.02704014 |
| fixed_vs_router | luna_xhigh → laya_trained_on | 7 | 2/2 | 4 | 2/2 | 0.02581834 / 0.08185637 |
| fixed_vs_router | luna_xhigh → kev_original_off | 50 | 25/10 | 13 | 6/4 | 0.19017236 / 0.03508754 |
| fixed_vs_router | luna_xhigh → kev_original_on | 49 | 27/17 | 20 | 10/9 | 0.24784766 / 0.08309304 |
| fixed_vs_router | luna_xhigh → kev_trained_off | 19 | 13/15 | 6 | 5/6 | 0.05244240 / 0.51199620 |
| fixed_vs_router | luna_xhigh → kev_trained_on | 31 | 21/25 | 12 | 8/9 | 0.13872726 / 2.14146482 |

## 实际Router动作

以下登记实际选中模型及请求Native Effort；Model-only组固定档位、只选择模型。教师短评输入Router，不直接写入执行模型消息。

- laya_original_off: `{"glm-5.3-flash:high": 198, "gpt-6.1-terra:high": 89, "gpt-6-luna:high": 30}`
- laya_original_on: `{"glm-5.3-flash:high": 212, "gpt-6-luna:high": 23, "gpt-6.1-terra:high": 44}`
- laya_trained_off: `{"glm-5.3-flash:high": 192, "gpt-6.1-terra:high": 27, "gpt-6-luna:high": 24}`
- laya_trained_on: `{"glm-5.3-flash:high": 226, "gpt-6.1-terra:high": 37, "gpt-6-luna:high": 20}`
- kev_original_off: `{"gpt-6-luna:low": 736}`
- kev_original_on: `{"gpt-6-luna:low": 716}`
- kev_trained_off: `{"gpt-6.1-terra:max": 816, "gpt-6.1-terra:medium": 39, "gpt-6.1-terra:low": 144, "gpt-6.1-terra:none": 32, "gpt-6.1-terra:high": 10}`
- kev_trained_on: `{"gpt-6.1-terra:max": 945, "gpt-6.1-terra:low": 200, "gpt-6.1-terra:none": 21, "gpt-6.1-terra:high": 13, "gpt-6.1-terra:medium": 19}`
