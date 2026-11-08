# 下一批完整关联 Execution 工作包

## 正式范围

Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。

沿最新main、本地未提交成果与A6000 /home/syy/路由/ 接续。唯一正式链是Harbor→ModelRouterMiniSweAgent→DefaultAgent。Registry登记15个联合动作，实际请求、返回模型/Effort、工具、官方Reward和计价分别记录。

## 已有成果

- 1491行既有测试已按五项职责拆分，52原函数语义保持；245个自有Python文件最大982行。现有状态、Serializer、两个原生Encoder、Registry、AA、教师、Provider用量与原Verifier直接复用。
- 新池17行=1条五候选联合偏好+16条原辅助。Laya V9-K3-GLM-LAYA-20261108完成17更新/736.337秒；Kev V9-K3-GLM-KEV-20261108于05:58保存LoRA与Head，17更新/13420.549秒。两版本按事前单Epoch规则确定，不按评价终局换权重。
- 原始实体为models/laya-421m与models/kev-4b-adapter。11-07各18更新实体属于旧HY4池；F05、R11与F15不自动成为新GLM代表。
- GLM Low在开发configure-git-webserver以非流式/4096输出取得30次生成、原Reward1、参考模型费$0.02080905。独立constraints-scheduling的GLM Low/High/Max正常提交、Reward1，参考费$0.00806607/$0.00712319/$0.00968241；返回Effort未报告。旧429、空流、4096全部推理、Luna Max返回xhigh的记录保持。
- constraints-scheduling在训练实体确定后才运行。固定Luna High、Terra High、规则、原始Laya均Reward1。CPU原始/训练/教师关闭与GLM三档分别保存；后续GPU批次不合并为同设备因果比较。
- large-scale-text-editing与sanitize-git-repo已完成事前独立评价，现在均为已观察任务；sanitize Laya原始/训练1/0、修复后Kev0/0，text五有效终局全0、三项无Reward。git-multibranch是已暴露开发题，JSON/GPU T/M/H、教师和粒度对照已结束；原训练Laya终局Verifier超时，晚到reward不改原结果。
- 49尝试全部结束，33有效终局/21个1/12个0、16无Reward；68成功教师，模型+教师已知参考$1.45700272，完整费用未知。[详细成果](../20261108-v9-k3-training/review.md)和49条结果为下一批起点，不重发已保存Episode。
- 241真实前缀Laya截断48→0、最长8173/8192，AA分数及来源保持；四实体同前缀CUDA原生前向成功。原49 Episode保持当时编码，不称为修复后T/M/H效果。下一批Train/Prepare与在线均使用唯一收敛后的Serializer。
- polyglot已观察，Luna Low/High=0/1、Terra Low/High=0/0。query-optimize三臂进入原业务评价后在1800秒处超时，无Reward；不作模型质量零分、不重发已保存模型轨迹。

## 第一：多机制真实联合监督与原Trainer

从既有合法Train来源选择尚有质量或费用信息增量的多个任务和截止，复用原环境、镜像、保存前缀及原Tester。按实际已执行候选质量优先、同质量参考费用次之形成监督；未执行、身份/返回档位不符及无有效终局保持原类别。用收敛后的唯一Serializer和原生Encoder沿原Prepare/Trainer形成两最终实体，保留本轮17更新代表作为历史，不由已观察独立题选择参数。

当前联合偏好来自Dynaconf一个截止，覆盖五个观察动作，赢家为明确请求并返回的Luna Xhigh；其余10个登记动作缺联合选择监督。AA、旧HY4、旧40条Model-only与独立评价终局不作为新标签。新信息形成后沿同一Prepare/Serializer及原Trainer更新，不重复17行同一Epoch制造进展。

## 第二：四实体、教师、输入与粒度完整比较

保留本批两训练实体与两原始实体，按实际设备、协议、AA版本及任务用途归组。默认非流式生成；GPU前向复用既有Checkpoint路径与/home/syy/ai-serving/state/gpu.lock，结束后回到CPU。Serving不换版，不建第二GPU队列。

复用已保存完整Episode，只补真实缺项或明确改变的研究条件。新比较采用收敛后表示及新监督实体、事前独立任务；原始/训练、固定三模型有效Effort、规则与教师关闭均完整执行并归同设备/协议/AA条件。教师关闭、T/M/H遮蔽、task_start/phase/generation用既有配置；M遮蔽保留输出必需的合法动作ID。取消后返回的Router计资源，不算已发送生成动作。

RQ3保持单Agent任务开始、实际阶段、真实子任务边界及路由粒度。阶段和三种粒度结果不称自动拆分；真实子任务边界的决策前可观察来源及完整对照仍需补齐，不引入角色协作或handoff。

## 第三：五RQ连续证据

| RQ | 接续动作 |
|---|---|
| RQ1 | 同任务官方质量、正常提交/时限事件、模型/教师/Router/工具/资源费用与真实墙钟 |
| RQ2 | 精确模型和请求Effort，实际返回/工具/Reward/缓存/费用，不把登记菜单写成渠道逐档独立确认 |
| RQ3 | 复用开始/阶段/逐生成，补真实子任务边界对照 |
| RQ4 | 同实体T/M/H、教师关闭及训练前后，在不同独立任务补成对观察 |
| RQ5 | 保持已观察评价身份，扩展事前独立工作负载和同配置重复，记录有收益/无收益/无法定价区域 |

AA v7/130指标/Intelligence Index5.0.1：Luna/Terra各六档，GLM仅Max，Low/High缺测。唯一配置及本机/远端环境无授权AA API Key；没有新授权成绩时保留缺测。沿TTL/force/STALE，在批次开始更新，同一比较批固定snapshot_id，不逐生成联网。

缓存分实际报告读取、前缀连续性估计、模型/端点变化与未知物理KV共享。参考模型/教师费、供应商逐请求实收、Router与CPU/GPU/VM资源分别列出；未知不填零。Token、Loss、概率、切换次数不作完整任务净收益。

## 资源与最终交付

F15物理epoch_01/61180，原38组25完成，当前无原Controller/F15训练进程。原始/研究权重、优化器恢复、私有轨迹与唯一配置保持；Serving仍原PID327621和原加载权重。所有真实候选和Docker只在A6000，Mac仅源码、分析与SSH控制。

本轮49尝试及原生前向均结束；任务容器0、GPU锁无持有者、研究进程与临时17898/SSH/memfd已关闭。镜像按合法Train和后续科研用途保留，模型不删；剩余工作不转定时任务。

下一批交付顺序：多任务合法联合监督 → 同义编码与两Trainer最终实体 → 事前独立完整四实体/固定模型/规则/教师开关比较 → 真实子任务边界及T/M/H/缓存消融 → 足够独立工作负载与完整费用。每段保留真实失败、缺Reward和无法定价项，不用Loss、AA、概率或切换次数代替五RQ结论。

发布必要源码/配置、脱敏结果与实质规划变化，定向提交推送main并报告完整SHA。最终八部分：目标/本轮推进，版本/源码/模型/训练/服务器，K=3/五RQ缺项，前三任务，真实实验，独立判断，通俗解释，下一完整工作包。
