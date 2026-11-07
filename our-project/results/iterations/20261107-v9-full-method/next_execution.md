# 下一批完整关联Execution工作包

## 正式目标与接续起点

Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。

沿实际最新main、本地未提交成果及A6000主工程继续。已完成的重构、AA v7、编码、原训练和完整Episode复用，不重新运行。正式链唯一为Harbor→ModelRouterMiniSweAgent→DefaultAgent。Registry登记Luna/Terra各六档及GLM Low/High/Max共15动作；实际返回档位、可执行工具和用量分别记录。

GLM已绑定唯一私人config的Colink。短SSE两客户端成功；High4096真实历史非流式333.097秒返回200，4096输出全用于推理、finish=length，无文本/工具。正式Provider已用Harbor实际剩余时间，length记INCOMPLETE_RESPONSE。Low4096此前两次429没有对照结果。新采集选择不同真实Train前缀，不补发相同失败，不无限提高输出额度。

AA v7取得时间2026-11-07T13:47:04.783836Z，Index 5.0.1、130项独立指标。Luna/Terra各六档，GLM仅Max；Low/High缺测。沿原TTL/force/STALE入口在正式启动取得最新数据，同一比较批次固定snapshot_id。授权API完整数据、revision和官方发布时间尚缺；不借其他模型或档位填值。

## 第一：复用已完成的新池监督与训练

Dynaconf/Hikari四截止的新GLM采集已完成六请求、三实际工具生成，另三429。保留原GPT结果与Verifier；唯一新联合偏好为Dynaconf继续截止的五个实际观察候选，赢家Luna Xhigh。其余截止无合法完整一步赢家，未知不填失败。新17行=1联合偏好+16原辅助，34项双原生编码FULL、15动作/130当前AA指标保留。不要重采这些已完成位置或将AA/HY4标签改成GLM答案。

Laya新实体V9-K3-GLM-LAYA-20261108已按原Head Trainer完成17更新、736.337秒并实际加载。Kev原Trainer在CPU40、LoRA+Head、同17行/1epoch健康计算，已经写第10/17次更新；取得最终物理参数和training_metrics后再做该实体的真实比较，不停止或重开，不创建第二训练队列。

后续需要新的真实任务/截止和候选结果信息增量才继续梯度更新。单步监督描述该步原验证，不冒称完整Episode或15动作最优。所有决策状态沿原Serializer，最终Verifier只用于合法标签，不进入当前输入。多步执行继续沿DefaultAgent。

## 第二：原Trainer和四实体比较

11-07的V9-K3-LAYA/KEV各18次更新属于旧HY4池，保留历史实体。当前两原始实体是models/laya-421m和models/kev-4b-adapter；本批新GLM实体均按事前指定的17行单Epoch选定，不根据polyglot或已看三题换权重。F05/R11、旧V9及F15恢复权重不删除、不自动换Serving。

训练版本在独立终局前确定，不按已观察regex-log/sqlite-db-truncate/openssl-selfsigned-cert三题挑权重。circuit-fibsqrt是已观察开发题。constraints-scheduling仍为独立评价，在模型选择和训练完成前不看其终局或用于调参。

已结束git-multibranch开发固定七臂、Laya九臂、去M粒度两臂及原始Kev，原结果不重跑。Luna Low/High=0/1、Terra Low/High=1/1；去M逐生成/开始/阶段=1/1/0；原始Kev0且Agent超时。完整主方法和GLM固定臂429无Reward。polyglot原六臂已结束，Low固定0/0、规则1；教师关规则臂SSL EOF后重复SSE文件失败，原证据保留，正式适配已移除该重复重试。High与原始Kev正在同任务接续。

Kev完训后完成新训练版、教师关、任务开始/阶段开发与polyglot比较。保持同v7、同30步/4096输出、原环境/Verifier和CPU40记录；CPU训练并行时，不将墙钟差单归因训练或路由粒度。constraints-scheduling在模型/训练实体确定后再进行事前独立比较，不提前查看终局用于选择。

## 第三：RQ1–RQ5连续推进

RQ1：完整Agent质量、成功与模型/教师/Router/工具/资源/墙钟总成本。
RQ2：真实K=3模型与档位结果，保留返回Effort不符和未报告状态。
RQ3：Single-Agent任务开始、实际阶段变化、真实子任务边界和逐生成粒度；Inspect/Modify/Verify/Recover只表示阶段。
RQ4：同权重T/M/H遮蔽、教师关闭及合法监督训练前后对照，复用现有字段。
RQ5：事前定义独立工作负载，研究有收益及无收益区域。

缓存报告实际cached tokens、历史前缀连续性、模型/端点切换；物理KV共享与额外切换费用缺测保持未知。渠道累计USD无逐请求关联时不摊为Episode实收。Loss、概率和切换只作为机制材料；主结果来自完整原Evaluator。

## 资源与交付

所有容器和真实候选在A6000已有用户Docker执行，Mac只编辑/分析/SSH控制。共享GPU锁和原队列保持。F15当前无训练进程；恢复实体按物理recovery_state确认，旧cursor不当保存进度。健康Serving仍原加载代码与权重，磁盘部署不表示进程换版。

沿唯一私人config通过SSH/memfd传递凭据，不另存Key。只清理本轮无用途临时对象；保留镜像、轨迹、响应、账本及模型材料的实际科研用途。发布必要源码、脱敏结果和实质规划变动，定向提交推送main并报告完整SHA。

最终按八部分汇报：整体目标/本轮进展、真实版本/源码/训练/服务器、K=3与五RQ缺项、前三任务、真实实验、独立判断、通俗解释、下一批关联Execution。
