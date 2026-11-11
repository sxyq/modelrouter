# Terminal-Bench 2.0 RQ1

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：0a9998aeb260f5e2a501212ed79d5904682afa87。

## 本批科研范围与已结束状态

本工作包以RQ4的新联合监督与两原Trainer更新为起点，完整任务质量/费用属于RQ1，模型×档位属于RQ2，开始/阶段/逐生成属于RQ3，训练/教师/T/M/H属于RQ4；RQ5仍需更多事前确定的工作负载与重复。两任务为历史已观察的`openssl-selfsigned-cert`、`regex-log`，独立于这次训练和代表选择。

2题×27策略×seed43全部54位置结束：42通过、2失败、10缺评分；74次原Harbor Trial与74条命令全部结束。固定阶段12通过、1失败、5缺评分；八个主Router组13通过、1失败、2缺评分；十个粒度/信息消融17通过、3缺评分。20分钟观察脚本与控制连接均正常退出。

核心Agent版本保持上方Commit；正则下载环境为`efd56feffaa1295e7e7d641e2bbe00e6783dc0a2`，汇总为`a5c34e005cd692386018c1f016996bdb6068a9c5`，图表为`7eb1d078f5595fca6d587d66dd19742e38d4d02f`。本批没有改变官方镜像、任务资源、测试代码或Ubuntu包签名验证。20个此前正则Trial写出原Reward0，但均缺`ctrf.json`且`uvx: command not found`；这些原记录及费用保留在各位置的`previous_attempts`。

两架构代表为`runs/V9-K3-GLM-LAYA-20261111`、`runs/V9-K3-GLM-KEV-20261111`，各18更新，训练时间15.193/252.463秒；2条七候选偏好加16辅助，两个截止均为验证阶段。实体参数及本批实际前向见[model_entities.json](model_entities.json)，训练不使用本批终局。

## 同题最后Episode质量与参考费用

下表费用包含该最后Episode的执行模型与教师，各组均运行这两题；`UNKNOWN`表示至少一题存在缺费请求。上方依赖下载处理发生过的支出另计入下方全尝试主表。

| 策略 | 通过/失败/缺评分 | 最后两Episode参考USD |
|---|---|---:|
| 固定Luna High | 2/0/0 | 0.00757392 |
| 固定Luna Max | 2/0/0 | 0.01401738 |
| 固定Terra High | 2/0/0 | 0.03751220 |
| 简单sticky规则 | 2/0/0 | 0.01333686 |
| 原始Laya OFF / ON | 2/0/0；2/0/0 | 0.03605180 / 0.03337800 |
| 新训练Laya OFF / ON | 1/0/1；2/0/0 | UNKNOWN / 0.02466572 |
| 原始Kev OFF / ON | 1/0/1；1/1/0 | UNKNOWN / 0.00300610 |
| 新训练Kev OFF / ON | 2/0/0；2/0/0 | 0.02944120 / 0.03183710 |

新训练Laya ON与Kev OFF/ON的同题通过数均为2，比固定Terra High的参考费低34.25%/21.52%/15.13%，比固定Luna High高225.67%/288.72%/320.35%。完整实收、Router/工具/资源单价仍缺，现金净收益为UNKNOWN。

训练对照：Laya ON两版均2/2，参考费下降26.10%，两Episode累计墙钟增加593.650秒、Router增加65.441秒；Kev ON原始1/2→训练2/2，参考费0.00300610→0.03183710。原始Kev14次主组决策均Luna Low，新训练主组21次均Terra Medium；新训练Laya两个主组包含GLM High、Luna High与Terra High。

教师对照的六个有效同题对均未增加通过数。原始Laya两题总参考费下降7.42%，新训练Kev两题增加8.14%；训练Laya和原始Kev各只有一个有效评分对，实际缺评分位置分别保留，教师独立贡献还缺同条件重复。

## RQ3与RQ4的实际关联结果

新训练Kev task_start两题均通过，Router累计30.893秒，逐生成ON为139.748秒；任务开始策略实际教师请求0，逐生成ON为3，所以这一对同时呈现粒度与实际教师调用变化。两组均选Terra Medium，参考费0.03110300/0.03183710。phase有一题连接断开、缺Reward；上游没有真实subtask_id，本批仅研究开始、阶段与逐生成。

新训练Laya phase、without_T/M/H两题均通过；task_start一题HTTP502。without_T/M参考费比完整ON高0.00412818/0.00459358，但累计任务墙钟少644.544/632.031秒。新训练Kev without_T/H两题均通过，参考费低0.00595360/0.00527090；without_M一题HTTP502，其余题通过。缺费和缺评分的对照集合分别列在`metrics/comparisons.json`，不由较少请求或切换次数赋任务分数。

## Provider、AA、缓存与资源事实

本批513个执行模型请求、32个Luna Low教师请求；短评实际消费45次，Router输入截断0。Luna Low/High/Max/Xhigh和Terra High/Medium/Xhigh已有返回档位相符记录；GLM返回档位未报告。历史Luna Max→Xhigh记录保持，不改成新批标签。GLM Low/High在证书任务取得Reward1，Max两题缺Reward。

AA固定`20261107T134704898459Z-v7`，130公开指标、Index5.0.1，Luna/Terra各六档，GLM仅Max，Low/High缺测。两架构实际首个原生输入的T/M/H及15候选均完整；AA仅为能力先验。

全部尝试实际报告缓存读1,964,032 Token，47请求缺读取、197请求缺写入；已报告写入合计0。前缀记录74个FIRST_REQUEST、430个EXACT_PREVIOUS_MESSAGES；40次逻辑模型变化与40次端点变化分列，跨模型物理KV共享未知。

模型参考费0.72700200、教师0.00702650，共0.73402850美元，12请求缺费用；另6次新监督请求已知0.09683890美元、1请求缺费用。两次训练单独报告资源，不混入在线账单。批次跨度8648.372秒，累计Harbor命令25536.700秒、原Trial25157.791秒；Router累计1392.554秒、请求CPU2525.256秒，完整资源美元价缺失。

末次A6000取样02:32台北：GPU989/49140MiB、0%，Serving327621 healthy；原用户VM16核40GiB、任务容器0。F15物理epoch_01为61180步/3915484条，模型及优化器仍在、无F15进程。本批Router socket与临时17898反向代理已退出，Mac及服务器运行配置中的临时镜像设置已撤去；同批实验配置保留。详情见[资源记录](metrics/resource_observations.json)。

## 下一批关联Execution

1. 沿原合法Train前缀补任务开始、阶段转折、修改/恢复状态；只对现有候选之外的信息增量开展真实质量—费用比较，再按事前单轮规则沿两原Trainer更新。
2. 在同一批次事前确定跨机制任务与重复；固定三模型、四Router实体、教师开关、task_start/phase/generation及T/M/H沿原Harbor成对运行。保留任务已观察身份，不根据终局改权重或任务集合。
3. 将可取得的供应商实收与CPU/GPU/VM计价接入原费用定义，按工作负载分开计算质量—总成本；未取得的字段保持UNKNOWN。AA每批固定快照，资源继续共享原锁。

以下为唯一汇总程序生成的逐策略、全部尝试费用及成对数据。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共54个任务/策略/seed位置；已结束54，运行中0，未开始0，渠道档位不可用0。固定组已报告档位不符另列后，官方Reward 1/0为42/2，无官方Reward 10；Router组保留实际任务Reward及内部请求/返回档位差异。

已保存原Harbor Trial 74次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$0.72700200、教师$0.00702650，合计$0.73402850；12次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

费用主表包含全部尝试；latest_trial_reference_usd单列最后Episode参考费。原Verifier写出的0保留；已确认uvx缺失且没有测试报告的尝试单列，不计入任务质量对照。

Harbor命令累计墙钟25536.700316秒，内含官方Trial累计25157.790697秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：2/2题已有结束记录；2题已结束全部9个固定/简单策略；2题已结束全部27个策略。批次先执行固定阶段，再执行Router阶段。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

本批2题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 2题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.02921835 |
| glm_high | 2 | 1 | 0 | 1/1 = 100.00% | 1/2 | 50.00%—100.00% | 1 | 0 | 0 | 0 | 0.03298917 |
| glm_max | 2 | 0 | 0 | 未评分 | 0/2 | 0.00%—100.00% | 2 | 0 | 0 | 0 | 0.02288510 |
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

Provider实际报告缓存读取1,964,032 Token；47次请求未报告缓存读取；跨模型物理KV共享未知。

教师请求32次，短评实际输入Router 45次；同一短评可由多次决策消费。

已记录Router输入截断0次，涉及0个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| HTTPError | 0 | 0 | 7 |
| NO_RECORDED_ERROR | 42 | 2 | 0 |
| ProviderResponseError | 0 | 0 | 1 |
| RemoteDisconnected | 0 | 0 | 2 |

## 同题训练、教师与消融对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

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

以下是已记录的Model×Native Effort选择次数；教师短评输入Router，不直接写入执行模型消息。

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
