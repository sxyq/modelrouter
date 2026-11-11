# 下一批完整关联 Execution 工作包

## 正式范围

Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。

唯一正式执行链为Harbor→ModelRouterMiniSweAgent→DefaultAgent→原官方Verifier。复用/home/syy/路由/、原用户Docker、原Registry、Provider、教师、Trainer与共享GPU锁。

## 已完成的科研起点

- [正式2.0 RQ1](../../benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)：89题×17策略×seed42全部结束；614位置有官方评分、899缺评分，2333原Trial、2339条Harbor命令，模型+教师已知参考费$35.11821871。全部368个Router恢复位置结束；原父进程1436024、观察连接、临时反向代理均已退出。
- 原始实体models/laya-421m、models/kev-4b-adapter；当前GLM训练代表runs/V9-K3-GLM-LAYA-20261108、runs/V9-K3-GLM-KEV-20261108各17更新，来自1条五候选联合偏好+16辅助，事前确定。11-07各18更新为HY4历史；F05/R11/F15的原研究身份保持。
- [收尾H编码](../../benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/metrics/h_encoding_followup.json)：生成/历史/最后观察按JSON内容呈现800/880/800字符摘要，原四条截断输入分别7489/7177/8189/8188 Token；T/M/H、教师状态及15候选全部FULL。原Episode及其4次H截断保持原版本；新编码尚无新训练或完整Episode。
- 6600628行公开数据、125份训练元数据、36参数保存目录及75历史迭代已分类；245个自有Python文件最大982行，1491行既有测试的52原函数已按五职责拆分。
- [旧49尝试](../20261108-v9-k3-training/review.md)与2.1历史结果分别保存；constraints-scheduling、sanitize-git-repo、large-scale-text-editing及本轮89题均保留已观察身份。

## 第一：多任务合法联合监督与必要训练

2026-11-12本项已取得实际增量：[两个合法截止](../20261111-v9-rq4-joint/joint_supervision.json)新增6请求、5有效原评价器结果，合并原候选形成2条七候选偏好+16辅助。Laya/Kev新实体各18更新保存，15.193/252.463秒，代表按单轮规则在评价前确定；原11-08实体不改写。

沿原合法Train任务、保存前缀、镜像、Harbor和Verifier取得多个真实截止的Model×Native Effort质量及费用。质量优先，同质量费用次之；监督只读取该截止之前的T/M/H与教师短评。

保留真实请求与返回模型/Effort。GLM Low/High/Max已有工具及官方Reward，但返回Effort未报告；本批Terra none→medium共52次，Luna历史max→xhigh保持原标签。不同返回、未知身份和缺Reward分别保存；AA与本轮正式终局不作训练标签。

有真实联合信息增量后沿原Laya/Kev Trainer开展必要更新，统一使用当前Serializer；保留原始、11-08研究实体和新保存点的实际来源。训练完成后事前确定每架构一个新代表，不依据已观察89题挑权重，不重做此前241前缀与数据盘点。

## 第二：独立完整Agent比较及单Agent阶段研究

当前沿[同批配置](../../../experiments/configs/v9_joint_followup.json)执行2题×27策略×seed43=54个完整Episode，保留历史已观察身份；固定模型、四实体Teacher OFF/ON、两新实体开始/阶段粒度及各T/M/H遮蔽一起比较。结果归入正式2.0结果体系中的`20261111-v9-joint-followup`，不并入原89题seed42结果。

使用未参与新训练与权重选择的独立工作负载，明确历史暴露属性。成对保持任务、seed、权重、池、Effort菜单、预算、AA、Encoder和GPU条件；固定Luna/GLM/Terra、简单规则、两架构原始/新训练代表及Teacher OFF/ON均沿原Harbor执行完整Episode。

同批关联执行task_start、真实阶段转折、per_generation与真实子任务边界对照，以及T/M/H遮蔽。子任务边界只用决策前可观察事实；M遮蔽保留输出必需的合法动作ID。教师仍为Luna低频三字段短评，单独记录请求、身份、消费与费用。

现有同题且费用齐全集合中，训练Kev OFF/ON相对固定Terra High均少通过3题且参考费更高；训练Laya OFF由5题通过降为4题。后续研究优先解释这些负结果及有效生成覆盖差异，不改变过去终局或重选旧权重。

## 第三：成本、缓存与工作负载收益边界

| RQ | 尚需取得的实际结果 |
|---|---|
| RQ1 | 独立任务质量及完整实收、Router/工具/CPU/GPU/VM费用；本批899位置缺评分的原因沿原记录保留 |
| RQ2 | 精确模型与请求档位的同题质量/费用、实际返回及缓存；GLM Low/High精确AA与渠道档位确认缺项 |
| RQ3 | 开始/阶段/逐生成及真实子任务边界的完整Episode对照 |
| RQ4 | 同权重T/M/H与教师开关、合法监督及训练前后的可比结果 |
| RQ5 | 事前独立工作负载、同配置重复及有收益/无收益/无法定价区域 |

AA v7固定快照20261107T134704898459Z-v7、130真实指标、Intelligence Index5.0.1：Luna/Terra各六档，GLM仅Max，Low/High缺测。授权完整API数据尚缺；沿原TTL/force/STALE更新，在每批开始取得快照，同批固定版本，不逐生成联网。

实际缓存读取、前缀重用估计、端点切换与物理KV共享分别记录。供应商逐请求实收、Router及工具/资源单价缺失时保持UNKNOWN；缓存折扣与Reasoning各计一次。训练成本单列，在线费用及并发资源分摊采用同一可知口径。

## 连续执行与资源

复用原modelrouter.benchmark rq1入口和配置批量运行；固定任务四并发、Router两并发，原任务时限、4096输出及官方Verifier。需要等待时沿原--watch-pids <实际父PID> --watch-interval 1200每20分钟汇总，父进程退出后取末次结果并结束，不建立新的Runner或定时服务。

F15物理epoch_01/61180、3915484条，模型与优化器保存点在、无F15进程；Serving PID327621仍为原F05/导入Kev。GPU继续共享/home/syy/ai-serving/state/gpu.lock，健康训练与共享服务保持。原用户Docker同qcow2为16核40GiB，任务容器随Harbor结束移除，关联RQ所需镜像保留。

唯一私人配置沿SSH输入/memfd读取，原权重、私有请求、轨迹与结果保护。公开源码、脱敏结果和实质规划分批提交推送；结束后清理本批临时对象并报告完整main SHA。最终按整体目标、真实进度、五RQ缺项、前三任务、真实结果、独立判断、通俗解释、下一关联工作包八部分汇报。
