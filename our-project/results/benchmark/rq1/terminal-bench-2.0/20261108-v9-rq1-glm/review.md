# Terminal-Bench 2.0 RQ1

官方版本：69671fbaac6d67a7ef0dfec016cc38a64ef7a77c；源码：cb4371da0635d9d550314b6703af4cbe87f0b714。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

共1513个任务/策略/seed位置；已结束1513，运行中0，未开始0，渠道档位不可用0。固定组已报告档位不符另列后，官方Reward 1/0为256/358，无官方Reward 899；Router组保留实际任务Reward及内部请求/返回档位差异。

已保存原Harbor Trial 2333次。恢复尝试保留原Trial、原失败及费用；逐位置终局取最后结束的Trial，费用与墙钟合计包含全部尝试。

已知模型参考费$34.97435329、教师$0.14386542，合计$35.11821871；1036次请求费用未知。供应商实收、Router、工具、CPU/GPU和VM美元价缺失，完整现金费用未知。

Harbor命令累计墙钟834545.118530秒，内含官方Trial累计818817.495873秒；差值包含CLI启动、退出及已发生的等待。以上是并发尝试时长之和。

按逐题表：89/89题已有结束记录；89题已结束全部9个固定/简单策略；89题已结束全部17个策略。批次先执行固定阶段，再执行Router阶段。

GLM Low/High/Max按请求档位分组，返回档位未报告；Luna/Terra的请求与返回档位逐次登记。

完整89题，旧2.1不计入。独立于训练/选择和历史暴露分别列出；缺Reward不填0，完整实收与资源USD保持未知。已报告档位冲突的官方结果保留在逐Episode表，并从按请求档位主比较中另列。通过率分母仅为该策略已取得的有效官方评分任务。

| 策略 | 已结束 | Reward1 | Reward0 | 有效评分通过率 | 评分覆盖 | 89题通过率区间 | 缺Reward | 运行中 | 未开始 | 渠道档位不可用 | 已知模型+教师USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm_low | 89 | 13 | 9 | 13/22 = 59.09% | 22/89 | 14.61%—89.89% | 67 | 0 | 0 | 0 | 0.40293753 |
| glm_high | 89 | 7 | 10 | 7/17 = 41.18% | 17/89 | 7.87%—88.76% | 72 | 0 | 0 | 0 | 0.45995859 |
| glm_max | 89 | 6 | 8 | 6/14 = 42.86% | 14/89 | 6.74%—91.01% | 75 | 0 | 0 | 0 | 0.45319009 |
| luna_low | 89 | 14 | 45 | 14/59 = 23.73% | 59/89 | 15.73%—49.44% | 30 | 0 | 0 | 0 | 0.29601030 |
| luna_high | 89 | 21 | 34 | 21/55 = 38.18% | 55/89 | 23.60%—61.80% | 34 | 0 | 0 | 0 | 0.85722668 |
| luna_max | 89 | 21 | 27 | 21/48 = 43.75% | 48/89 | 23.60%—69.66% | 41 | 0 | 0 | 0 | 1.55918550 |
| terra_high | 89 | 34 | 23 | 34/57 = 59.65% | 57/89 | 38.20%—74.16% | 32 | 0 | 0 | 0 | 4.48918920 |
| luna_xhigh | 89 | 25 | 31 | 25/56 = 44.64% | 56/89 | 28.09%—65.17% | 33 | 0 | 0 | 0 | 1.41375102 |
| rule_sticky | 89 | 28 | 21 | 28/49 = 57.14% | 49/89 | 31.46%—76.40% | 40 | 0 | 0 | 0 | 3.35438690 |
| laya_original_off | 89 | 7 | 5 | 7/12 = 58.33% | 12/89 | 7.87%—94.38% | 77 | 0 | 0 | 0 | 0.36278281 |
| laya_original_on | 89 | 3 | 6 | 3/9 = 33.33% | 9/89 | 3.37%—93.26% | 80 | 0 | 0 | 0 | 0.26023004 |
| laya_trained_off | 89 | 4 | 4 | 4/8 = 50.00% | 8/89 | 4.49%—95.51% | 81 | 0 | 0 | 0 | 0.18498189 |
| laya_trained_on | 89 | 3 | 5 | 3/8 = 37.50% | 8/89 | 3.37%—94.38% | 81 | 0 | 0 | 0 | 0.27858662 |
| kev_original_off | 89 | 11 | 57 | 11/68 = 16.18% | 68/89 | 12.36%—35.96% | 21 | 0 | 0 | 0 | 0.24247332 |
| kev_original_on | 89 | 17 | 44 | 17/61 = 27.87% | 61/89 | 19.10%—50.56% | 28 | 0 | 0 | 0 | 0.28372402 |
| kev_trained_off | 89 | 16 | 12 | 16/28 = 57.14% | 28/89 | 17.98%—86.52% | 61 | 0 | 0 | 0 | 9.19439320 |
| kev_trained_on | 89 | 26 | 17 | 26/43 = 60.47% | 43/89 | 29.21%—80.90% | 46 | 0 | 0 | 0 | 11.02521100 |

实际执行跨度：2026-11-08T15:48:04.949644+00:00至2026-11-11T12:18:29.984449+00:00，246625.034805秒；按最早COMMAND_START与最晚COMMAND_END计算，包含批次间等待。


评分覆盖是已取得有效官方评分的任务数/89；通过率区间把其余位置分别按全部未通过或全部通过计算。

Provider实际报告缓存读取176,142,912 Token；1292次请求未报告缓存读取；跨模型物理KV共享未知。

教师为Luna Low，请求473次，短评实际输入Router 886次；请求身份451相符、18缺返回身份、4未知，同一短评可由多次决策消费。

缓存写入3185次未报告。前缀连续性估计有12649次消息前缀完整延续、957次首次请求；逻辑模型与端点变化各674次，分别保留原字段。

AA同批使用20261107T134704898459Z-v7，130真实公开指标、Intelligence Index5.0.1；Luna/Terra各六档，GLM仅Max，Low/High缺测。AA为能力先验，授权完整API数据及供应商物理模型版本仍缺。

已记录Router输入截断4次，涉及3个位置；原输入及官方结果保留在逐Episode表。


## 已报告Native Effort差异

以下保留实际请求与返回档位，不改请求标签；登记菜单不代表渠道逐档已经确认。

| 请求模型 | 请求Effort | 返回Effort | 请求次数 |
|---|---|---|---:|
| gpt-6.1-terra | none | medium | 52 |

## Episode结束事件

按每个位置最后结束的原Harbor Trial记录；超时且取得Reward的两项事实同时保留。

| 原异常类型 | Reward1 | Reward0 | 缺Reward |
|---|---:|---:|---:|
| AgentTimeoutError | 19 | 127 | 25 |
| EnvironmentStartTimeoutError | 0 | 0 | 45 |
| HTTPError | 0 | 0 | 424 |
| NO_RECORDED_ERROR | 237 | 231 | 0 |
| ProviderResponseError | 0 | 0 | 145 |
| RemoteDisconnected | 0 | 0 | 27 |
| RuntimeError | 0 | 0 | 112 |
| URLError | 0 | 0 | 82 |
| ValueError | 0 | 0 | 2 |
| VerifierTimeoutError | 0 | 0 | 37 |

## 同题训练与教师对照

评分对只包含两侧均有官方Reward的同题同seed；费用对是其中两侧请求参考费均齐全的子集。通过数差异与费用差异分别按对应集合报告。

| 因素 | 左侧 → 右侧 | 评分对 | 通过数左/右 | 费用齐全对 | 费用对通过数左/右 | 参考费左/右USD |
|---|---|---:|---:|---:|---:|---|
| teacher | laya_original_off → laya_original_on | 6 | 3/3 | 5 | 3/3 | 0.11529809 / 0.11227356 |
| teacher | laya_trained_off → laya_trained_on | 6 | 3/3 | 5 | 3/3 | 0.09012806 / 0.13704358 |
| teacher | kev_original_off → kev_original_on | 55 | 10/15 | 30 | 6/10 | 0.09726728 / 0.11050570 |
| teacher | kev_trained_off → kev_trained_on | 21 | 12/14 | 13 | 8/8 | 1.81995500 / 2.17498340 |
| training | laya_original_off → laya_trained_off | 8 | 5/4 | 6 | 5/4 | 0.07787562 / 0.09658031 |
| training | laya_original_on → laya_trained_on | 5 | 3/3 | 4 | 3/3 | 0.07499469 / 0.12199358 |
| training | kev_original_off → kev_trained_off | 26 | 6/16 | 16 | 4/10 | 0.05159106 / 1.86150440 |
| training | kev_original_on → kev_trained_on | 32 | 12/21 | 18 | 9/11 | 0.06883062 / 2.89973682 |

## 实际Router动作

以下是已记录的Model×Native Effort选择次数；教师短评输入Router，不直接写入执行模型消息。

- laya_original_off: `{"glm-5.3-flash:high": 198, "gpt-6.1-terra:high": 89, "gpt-6-luna:high": 30}`
- laya_original_on: `{"glm-5.3-flash:high": 212, "gpt-6-luna:high": 23, "gpt-6.1-terra:high": 44}`
- laya_trained_off: `{"glm-5.3-flash:high": 192, "gpt-6.1-terra:high": 27, "gpt-6-luna:high": 24}`
- laya_trained_on: `{"glm-5.3-flash:high": 226, "gpt-6.1-terra:high": 37, "gpt-6-luna:high": 20}`
- kev_original_off: `{"gpt-6-luna:low": 736}`
- kev_original_on: `{"gpt-6-luna:low": 716}`
- kev_trained_off: `{"gpt-6.1-terra:max": 816, "gpt-6.1-terra:medium": 39, "gpt-6.1-terra:low": 144, "gpt-6.1-terra:none": 32, "gpt-6.1-terra:high": 10}`
- kev_trained_on: `{"gpt-6.1-terra:max": 945, "gpt-6.1-terra:low": 200, "gpt-6.1-terra:none": 21, "gpt-6.1-terra:high": 13, "gpt-6.1-terra:medium": 19}`

## 同题质量与费用判断

| 固定Terra High → 训练Kev | 同题且费用齐全 | 通过数左/右 | 参考费左/右USD |
|---|---:|---:|---:|
| OFF | 13 | 10/7 | 0.46087360 / 1.28865280 |
| ON | 19 | 14/11 | 0.70459560 / 2.05335254 |

上述集合中训练Kev少通过且更贵。训练Kev相对原始Kev有增质增费；训练Laya OFF的费用齐全6题中通过5→4、参考费0.07787562→0.09658031美元。两架构的完整现金净收益尚缺供应商实收及资源单价。

原始Kev两教师组始终选Luna Low，教师短评只进入Router；成绩差异的模型采样、资源等待与教师贡献尚未分离。训练Kev教师开关的13个费用齐全对均通过8题，参考费由1.81995500增至2.17498340美元。

## 批次收尾的原生H编码

原批次方法与评分保持cb4371da0635d9d550314b6703af4cbe87f0b714。收尾Serializer为24a66dec601b461aba7b0ba162f2f7de5277f5f0，沿JSON内容呈现长度保留生成800、历史880、最后观察800字符，原轨迹不变；原4条截断输入仅用于原生编码测量。

| 保存输入 | 原丢失Token | 新序列Token/8192 | 新丢失 | T/M/H及15候选 |
|---|---:|---:|---:|---|
| build-cython-ext / 训练Laya OFF / step10 | 161 | 7489 | 0 | FULL |
| count-dataset-tokens / 原始Laya ON / step5 | 805 | 7177 | 0 | FULL |
| sam-cell-seg / 原始Laya ON / step23 | 90 | 8189 | 0 | FULL |
| sam-cell-seg / 原始Laya ON / step24 | 89 | 8188 | 0 | FULL |

原8192/512窗口、两个保存Tokenizer及原build_sequence/state_room直接复用；前两条原Episode缺评分，sam-cell-seg原Episode为0。新编码未用于本批重跑、重新选权重或新增训练。完整测量与早期仍截断的结果见[同一编码记录](metrics/h_encoding_followup.json)。

## 当前后续研究

多任务合法Train联合监督与必要训练 → 事前确定新代表 → 独立完整Agent的固定/动态、教师、T/M/H及单Agent阶段/真实子任务边界/粒度对照 → 实收与资源价格、缓存及工作负载收益边界。既有四实体和全部原结果保留，[下一完整工作包](../../../../iterations/20261107-v9-full-method/next_execution.md)沿原实现执行。

## 运行资源与清理

原用户Docker任务容器已为0，VM保留16核/40GiB配置；Serving PID327621健康，原F05/导入Kev保持。F15物理保存61180更新、3915484条，无F15进程；模型与优化器文件在。14:42 UTC共享GPU为18747/49140MiB、100%，主要为已有sgl_diffusion::scheduler进程，未作为本批资源费用。

末次结果已传回服务器原正式目录；两个临时公开导出目录合计318979911字节已移除，可沿原私有Harbor记录再次派生。源码回退合并至唯一modelrouter-previous-source.tar.gz，352文件、1386380字节。原请求、权重、原Trial、镜像及GPU共享服务保持；观察和控制SSH连接返回255，父进程最终退出码缺记录，368恢复位置状态均已结束。
