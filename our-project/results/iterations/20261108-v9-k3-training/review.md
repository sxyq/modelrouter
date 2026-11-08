# V9 新GLM池训练、49次Harbor尝试与科研接续

## 一、整体目标与本轮推进

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

复用已完成的职责整理、17行合法训练和AA v7，没有重建研究架构。49次完整Harbor尝试已结束：33个有效原官方终局，21个Reward 1、12个Reward 0；16个无有效Reward。49包括41个原位置及实际运行故障处理后的8次两臂尝试，不能视为49个独立任务。原Trial、异常和晚到产物保持原貌。

脱敏逐条结果、时间与费用见[episode_results.json](episode_results.json)；完整原始证据保留在各iterations目录，不公开私人响应或任务正文。

## 二、版本、职责、训练与服务器

本轮起点main为`208689e37d107f32c4dab9dc93f3683356a4a664`，已晚于负责人列出的`e46726266fc64db9d624059aae928491ad26d3eb`。A6000主工程没有Git元数据，原run_config保存实际起点与接续说明；发布提交不能冒充各Episode运行时版本。

唯一执行链为`Harbor → ModelRouterMiniSweAgent → DefaultAgent`。状态/时间由AgentState提供，T/M/H由runtime/context序列化，Registry提供动作及计价，capabilities管理AA，teacher/trigger与assessor管理低频教师，protocols/usage保存原生响应与真实用量，官方Verifier保持上游实现。

既有1491行文件早已按保留算法、入口、队列、汇总及Kev职责拆成五文件，52原函数语义保持；本轮不重复拆分。自有Python共245文件，最大982行。

| 实体 | 新池更新 | 训练墙钟 | 身份 |
|---|---:|---:|---|
| models/laya-421m | 0 | 不属于本轮训练 | 原始可执行Laya |
| models/kev-4b-adapter | 0 | 不属于本轮训练 | 原始可执行Kev |
| V9-K3-GLM-LAYA-20261108 | 17 | 736.337秒 | 本轮Laya研究代表 |
| V9-K3-GLM-KEV-20261108 | 17 | 13420.549秒 | 本轮Kev研究代表，CPU/FP32 LoRA+Head |

17行是1条五候选联合偏好及16辅助，只有一个有效偏好截止；明确赢家Luna Xhigh。其余10个登记动作缺联合偏好监督。两代表按事前单Epoch规则确定，没有依据独立任务终局挑权重；11-07两18更新实体、F05/R11保持历史身份。Kev于11-08 05:58台北保存，99745前向Token、峰值RSS238751465472字节。原始权重只在A6000。

本轮原位处理实际CUDA问题：Laya专用导入移回对应分支；Kev参数与DecisionModel.device同步，使用原Transformers SDPA以消除eager注意力显存耗尽；Responses SSE错误保留原code。没有产品自动重试或替代模型。

最终用户Docker任务容器0，GPU锁无持有者，GPU31423/49140MiB、利用率0%；所有研究进程结束，任务内17898转发和memfd已关闭。Serving PID327621健康200，仍F05-e01/原导入Kev。F15无Controller或训练进程，物理epoch_01/step61180、保存时间2026-11-05T17:22:48Z，原38组25完成。唯一上版源码包为693606字节；更旧包已被部署前源码替换，更旧源码由Git历史恢复。合法Train与后续成对研究需要的镜像保留。

## 三、K=3与五RQ缺项

| RQ | 实际新增 | 仍缺证据 |
|---|---|---|
| RQ1质量—总成本 | 三模型官方结果、四实体与规则完整尝试 | 供应商逐请求实收、Router/工具/CPU/GPU/VM/训练美元价；同配置可重复净收益 |
| RQ2 Model×Effort | GLM Low/High/Max均工具生成且官方1 | GLM返回档位、10动作联合偏好、Luna Max及Terra none返回差异、独立互补选择 |
| RQ3单Agent粒度 | task_start/phase/generation真实Episode | 真实子任务边界的决策前来源与完整成对执行；不能用阶段标签当任务拆分 |
| RQ4消融 | 原始/训练、T/M/H遮蔽、教师开关 | 编码改动后的完整Episode与训练、独立成对消融、合法监督增量 |
| RQ5适用边界 | 三独立评价任务的观察及失败 | 足够独立工作负载、同条件重复和可定价收益边界 |

## 四、下一阶段前三项

1. 使用已收敛的完整T/M/H表示，从多个合法Train任务截止形成质量优先、等质量费用次之的真实联合偏好；不复训原17行制造进展，不将AA或评价终局转成标签。
2. 沿同一Prepare/Trainer获得可代表新监督的两最终版本，固定原始实体、AA、设备、协议和事前独立任务，执行完整四实体/固定模型/规则/教师关闭比较。
3. 在上述同一研究链补真实子任务边界及成对T/M/H、教师、缓存连续性消融，并扩展独立工作负载；逐项补全实收与资源费用。

## 五、真实模型、Effort、AA、教师、缓存和Episode

| 独立任务 | 固定Luna High | 固定Terra High | GLM Low/High/Max | 规则 | Laya原始/训练/无教师 | Kev原始/训练/无教师 |
|---|---|---|---|---|---|---|
| constraints-scheduling | 1 | 1 | 1/1/1 | 1 | CPU 1/1/1 | CPU 1/1/0 |
| sanitize-git-repo | 1 | 1 | Low 1；其余未运行 | 无Reward，上游流错误 | GPU 1/0；无教师未运行 | 修复后GPU 0/0；无教师未运行 |
| large-scale-text-editing | 无Reward，Verifier超时 | 0 | Low 0；其余未运行 | 0 | GPU 0/0；均Agent超时 | 原始Verifier超时/训练档位不符；无Reward |

constraints CPU Kev原始、训练触及1200秒Agent时限，但原Verifier仍给1；教师关闭臂正常结束0，并非三臂全部超时。sanitize训练Kev900秒Agent超时且原Verifier0，原始Kev正常结束0。text训练Kev此前已有19条工具事件，在第7个生成请求Terra none、返回medium后终止；差异请求参考费$0.00992，完整Episode模型+教师参考费$0.047913。差异请求未作为合法动作执行，但不抹去此前动作。

| 参考费用对照，USD | 原始 | 训练 | 教师关闭 |
|---|---:|---:|---:|
| constraints CPU Laya | 0.01053198 | 0.01409152 | 0.00418989 |
| constraints CPU Kev | 0.00227770 | 完整未知；已知0.02600102 | 0.02869620 |
| sanitize GPU Laya | 0.06904899 | 0.03659973 | 未运行 |
| sanitize修复后GPU Kev | 0.01131672 | 0.10385564 | 未运行 |

开发configure-git-webserver的GLM Low JSON4096完成30次生成、Reward1、参考模型费$0.02080905。GLM可达、Reasoning、有效工具、返回Effort和官方Reward分别报告；三档已有工具与Reward1，返回Effort仍NOT_REPORTED，物理后端未知。旧High4096全部推理/finish=length、429、空流及Luna Max→xhigh保留；不改标签或增加输出额度。

开发git-multibranch的GPU Laya：原始1；训练原Verifier900秒超时/无Reward，晚到reward.txt=1不替换；无教师1；去T0且Agent超时；去M1；去H1；task_start无Reward；phase1。CPU训练Kev逐生成/phase为0/0，task_start超时无Reward，无教师Terra none→medium无Reward。开发与独立任务、CPU/流式与GPU/非流式不混为同条件因果比较。

固定AA快照`20261107T134704898459Z-v7`，130公开指标、Intelligence Index5.0.1。Registry派生目标，逐档数据进入M及两个原生Encoder；TTL/force/STALE和同批固定版本保留，没有逐生成联网。授权API Key仍缺。

| AA Intelligence Index | none | low | medium | high | xhigh | max |
|---|---:|---:|---:|---:|---:|---:|
| Luna | 9.4424 | 9.6661 | 18.4542 | 21.4290 | 23.4509 | 27.8552 |
| Terra | 30.5159 | 29.4169 | 38.1652 | 42.4345 | 45.2501 | 51.3265 |
| GLM | 不支持 | 缺测 | 不支持 | 缺测 | 不支持 | 27.8039 |

49尝试共601个GENERATOR_END、68次Luna教师触发及68次成功短评；8个Provider记录用量和参考费未知。已知模型参考费$1.42361320、教师$0.03338952，共$1.45700272。供应商实收及全部资源美元价未知，完整费用不填零。

模型及教师请求实际报告缓存读取5572672 Token，66个记录缺读取数；已报告写入合计0，256个记录缺写入数。601个上下文事件中41次FIRST_REQUEST、560次EXACT_PREVIOUS_MESSAGES。后者是输入消息前缀连续性，不能替代缓存读取；端点变化与物理KV共享单列，物理KV始终未知。

### 最终原生输入

49尝试均保留当时输入版本。为消除实际截断，共享指标定义只保留一份，移除重复顶层AA及训练标签/快照ID的神经输入副本；原分数、单位、版本、来源和各档身份仍在M及原状态记录。

241个保存前缀的原Laya build_sequence测量：48截断降为0，最长8173 Token，8192/512窗口不变；AA数值/来源不符0。T/M/H分别228/224/219 FULL，其余13/17/22为原遮蔽；教师状态区241 FULL，包含缺失/关闭标记，不是241条短评。

同一真实前缀四实体A6000 CUDA前向均无截断，T/M/H及教师状态FULL：

| 实体 | 输入Token | 前向ms | 含首次加载/转移总ms |
|---|---:|---:|---:|
| 原始Laya | 8173 | 2407.12 | 12235.79 |
| 训练Laya | 8173 | 2428.79 | 12490.15 |
| 原始Kev | 8409 | 4949.91 | 69904.46 |
| 训练Kev | 8409 | 4781.80 | 68429.80 |

[native_encoding.json](native_encoding.json)保留原34训练编码，并追加241前缀及四实体结果。该前向不产生新Reward或联合标签；修复后尚无新的完整Episode比较。

## 六、独立科研判断

当前没有可归因于新池训练的质量或总成本净收益。sanitize Laya由1降0；Kev0→0且训练参考费约为原始9.18倍。constraints Laya同为1，训练参考费增加$0.00355954、约33.8%。text五个有效终局全0，三臂无Reward；不能把无Reward补为质量零分。

低频phase和教师关闭在开发题通过，只能提供下一成对研究的信息；完整训练臂的原终局缺失、输入有旧截断、设备和协议分批，不能据此归因教师有益/有害或宣称低频普遍更好。编码容量问题已实际处理，但表示变化的学习及完整任务效应仍缺。

## 七、通俗说明

三个生成模型已真正做题，两种Router也各得到一个新池训练版本并完成真实比较；现在Router能完整读入已保存的任务、能力和工具历史摘要。结果显示“训过、读全、会切换”尚未变成“任务更好且总费用更低”。距离论文核心结论主要差多任务有效监督、修复后完整独立比较和全部费用。

## 八、下一批完整关联工作包

沿原[next_execution.md](../20261107-v9-full-method/next_execution.md)接续：合法Train多截止监督 → 同编码两Trainer最终版 → 事前独立四实体/固定模型/规则/教师关闭Episode → 真实子任务边界与T/M/H、教师、缓存消融 → 独立多工作负载及完整费用。已经观察的constraints、sanitize、text和开发题保持已观察身份；原49次不重发、不改名、不用于挑最终权重。
