# 下一批完整关联 Execution 工作包

## 正式范围

Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。

唯一正式执行链为Harbor→ModelRouterMiniSweAgent→DefaultAgent→原官方Verifier。复用/home/syy/路由/、原用户Docker、原Registry、Provider、教师、Trainer与共享GPU锁。

## 已完成的科研起点

- [正式2.0 RQ1](../../benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)：89题×17策略×seed42全部结束；614位置有原始Reward、899缺评分，101个原0来自uvx未安装且无测试报告，有效任务评分513位置。2333原Trial、2339条Harbor命令，模型+教师已知参考费$35.11821871，已报告228743791 Token、1028请求缺用量。原结果、费用与全部尝试保持。
- 原始实体models/laya-421m、models/kev-4b-adapter；本批GLM训练代表runs/V9-K3-GLM-LAYA-20261111、runs/V9-K3-GLM-KEV-20261111各18更新，来自两个验证阶段的七候选偏好+16辅助，事前确定；11-08各17更新及11-07各18更新分别保留其原池/批次身份。F05/R11/F15的原研究身份保持。
- [收尾H编码](../../benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/metrics/h_encoding_followup.json)：生成/历史/最后观察按JSON内容呈现800/880/800字符摘要，原四条输入分别7489/7177/8189/8188 Token；T/M/H、教师状态及15候选全部FULL。原89题Episode及其4次H截断保持原版本；新编码已用于本批18更新与54位置，实际Router截断0。
- [新训练与54项完整结果](../../benchmark/rq1/terminal-bench-2.0/20261111-v9-joint-followup/review.md)：2个已观察任务×27策略×seed43全部结束，42通过、2失败、10缺评分，74原Trial；模型+教师已知参考费$0.73402850、12请求缺费用，跨度8648.372秒。两个0均为真实日期匹配失败；此前20个未执行测试的原0和费用保持。控制、观察、临时代理与任务容器已结束。
- 6600628行公开数据、125份训练元数据、36参数保存目录及75历史迭代已分类；245个自有Python文件最大982行，1491行既有测试的52原函数已按五职责拆分。
- [旧49尝试](../20261108-v9-k3-training/review.md)与2.1历史结果分别保存；constraints-scheduling、sanitize-git-repo、large-scale-text-editing及本轮89题均保留已观察身份。

## 当前优先：Model-only全量对照（RQ2，关联RQ1/RQ4）

按负责人最新要求，先执行[Model-only配置](../../../experiments/configs/v9_model_only.json)：全部89题×24组×seed43，Laya/Kev原始及11-11各18更新实体、教师OFF/ON、固定Low/High/Max。每次仅在三个同档模型中选择，沿原Harbor/DefaultAgent及原Verifier，所有任务保持已观察身份，不作新训练或选权重。18:38台北396位置结束，53通过/8失败/335缺评分；2运行、1738未开始，17题有结束记录。已报告4,440,557模型+教师Token、346次缺用量、已知模型+教师参考费$1.23215771；Router本地另报告3,508,964输入/34,622输出Token。当前与终局状态沿[本批结果](../../benchmark/rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)读取。

旧54位置seed43联合选择结果已与openssl-selfsigned-cert/regex-log逐题配对；原分析器同时纳入同档位Model-only训练/教师及固定模型对照，实际评分和费用齐全的task/seed分别登记。其余87题相同权重/seed的八个联合主组共696位置，已按[联合接续配置](../../../experiments/configs/v9_joint_paired.json)排在当前矩阵和一次连接恢复之后；新配置直接读取Model-only批次保存的AA能力快照，沿相同Encoder、教师、Harbor、Verifier、输出及任务时限执行。旧89题seed42训练版为11-08实体，保留其历史身份；不重复首两题和旧批次。

固定脚本`our-project/code/cli/run_rq1_a6000.py`已接上原父2373109，使用`--attach-pid 2373109 --recover-infrastructure`和Model-only、Joint-paired两个配置顺序执行。原控制SSH断开后316请求记录连接拒绝，18:31按本机Clash实际17897端口恢复原17898代理；旧观察已退出，现观察每1200秒汇总。原GPU锁、用户Docker和唯一SSH/memfd凭据沿用；本次全部批次结束后退出并清理临时导出。完整API Token按已报告输入+输出登记，Router本地另计；缓存读取与Reasoning各计一次。连接失败及费用保持，只有已记录且没有成功生成/教师/工具的相应位置沿原机制恢复一次，不重做Provider额度耗尽或已有Reward。

19:05当前运行事实：持有进程2806615、观察2806620仍在；单批代理SSH44998跟随该持有进程结束，观察输出已接回原controller.log。原三个模型域名经现有TCP出口HTTP200，gcode-to-text的Luna High/Max已有实际生成和工具结果，终局待原Verifier；18:58快照412结束、2运行、1722未开始，1个Verifier依赖失败与349缺Reward分别登记。中断后不重建矩阵或重复首两题。

## 后续一：补任务开始、转折与恢复状态（RQ4，关联RQ2）

2026-11-12：[两个合法截止](../20261111-v9-rq4-joint/joint_supervision.json)新增6请求、5有效原评价器结果，合并原候选形成2条七候选偏好+16辅助；两者均为验证阶段。Laya/Kev新实体各18更新保存，15.193/252.463秒；18行及现有六请求不重做。下一增量定位原合法Train前缀中的任务开始、修改、真实阶段转折及恢复，质量优先、等质量费用次之。

沿原合法Train任务、保存前缀、镜像、Harbor和Verifier取得多个真实截止的Model×Native Effort质量及费用。质量优先，同质量费用次之；监督只读取该截止之前的T/M/H与教师短评。

保留真实请求与返回模型/Effort。GLM Low/High在本批证书任务有Reward1、Max两题缺Reward；原constraints-scheduling三档Reward1保持历史身份，返回Effort未报告。旧89题Terra none→medium52次、Luna历史max→xhigh保持原标签；新批已返回的Luna Max为Max。不同返回、未知身份和缺Reward分别保存；AA与正式终局不作训练标签。

有真实联合信息增量后沿原Laya/Kev Trainer开展必要更新，统一使用当前Serializer；保留原始、11-08研究实体和新保存点的实际来源。训练完成后事前确定每架构一个新代表，不依据已观察89题挑权重，不重做此前241前缀与数据盘点。

## 后续二：跨机制成对完整Agent与阶段研究（RQ1/RQ3/RQ4）

沿[同批配置](../../../experiments/configs/v9_joint_followup.json)的54位置已结束，保留历史已观察身份；固定模型、四实体Teacher OFF/ON、两新实体开始/阶段及各T/M/H遮蔽已经共同执行。新训练Laya ON、Kev OFF/ON两题均通过，相对固定Luna High最后Episode参考费高225.67%/288.72%/320.35%；新Kev主组全选Terra Medium，原始Kev全选Luna Low。下一比较事前确定不同任务机制与重复，沿同一结果体系另记批次，不重跑本批54位置或原1513矩阵。

使用未参与新训练与权重选择的独立工作负载，明确历史暴露属性。成对保持任务、seed、权重、池、Effort菜单、预算、AA、Encoder和GPU条件；固定Luna/GLM/Terra、简单规则、两架构原始/新训练代表及Teacher OFF/ON均沿原Harbor执行完整Episode。

本批task_start/phase/generation与T/M/H已取得完整Episode：粒度/信息20位置为17通过、3缺评分。上游无subtask_id，真实子任务边界尚缺实际来源；后续只用决策前可观察事实，不以phase替代。task_start实际教师请求0，逐生成Kev ON为3，粒度与教师触发变化同时报告。M遮蔽保留输出必需的合法动作ID；教师仍为Luna低频三字段短评。

原89题同题费用齐全集合中，11-08训练Kev OFF/ON相对Terra High均少通过3题且更贵；训练Laya OFF由5题通过降为4题。本批Laya ON训练后参考费下降26.10%但累计墙钟多593.650秒；Kev ON由1/2升至2/2但更贵。六个有效教师对未增加通过数，原始Laya参考费下降7.42%。后续研究优先解释阶段覆盖、静态选择及时间—费用差异，不依据这些终局重选权重。

## 后续三：成本、缓存与工作负载收益边界

| RQ | 尚需取得的实际结果 |
|---|---|
| RQ1 | 跨机制成对重复及完整实收、Router/工具/CPU/GPU/VM费用；原89题899缺评分、本批10缺评分的原因分别保持 |
| RQ2 | 精确模型与请求档位的同题质量/费用、实际返回及缓存；GLM Low/High精确AA与渠道档位确认缺项 |
| RQ3 | 已运行开始/阶段/逐生成；补真实子任务边界与跨机制重复，实际教师调用变化分列 |
| RQ4 | 已运行训练/教师/T/M/H；补非验证阶段合法监督及可重复的条件选择收益 |
| RQ5 | 事前独立工作负载、同配置重复及有收益/无收益/无法定价区域 |

AA v7固定快照20261107T134704898459Z-v7、130真实指标、Intelligence Index5.0.1：Luna/Terra各六档，GLM仅Max，Low/High缺测。授权完整API数据尚缺；沿原TTL/force/STALE更新，在每批开始取得快照，同批固定版本，不逐生成联网。

实际缓存读取、前缀重用估计、端点切换与物理KV共享分别记录。供应商逐请求实收、Router及工具/资源单价缺失时保持UNKNOWN；缓存折扣与Reasoning各计一次。训练成本单列，在线费用及并发资源分摊采用同一可知口径。

## 连续执行与资源

复用原modelrouter.benchmark rq1入口和配置批量运行；固定任务四并发、Router两并发，原任务时限、4096输出及官方Verifier。需要等待时沿原--watch-pids <实际父PID> --watch-interval 1200每20分钟汇总，父进程退出后取末次结果并结束，不建立新的Runner或定时服务。

02:32台北F15物理epoch_01/61180、3915484条，模型842609220字节、优化器3368412933字节仍在，无F15进程；Serving PID327621原F05/导入Kev healthy。GPU989/49140MiB、0%，继续共享原锁，用户VM16核40GiB、任务容器0。临时17898代理、Router socket与运行镜像设置已撤去；实验配置、关联镜像、权重及原私有轨迹保留。

唯一私人配置沿SSH输入/memfd读取，原权重、私有请求、轨迹与结果保护。公开源码、脱敏结果和实质规划分批提交推送；结束后清理本批临时对象并报告完整main SHA。最终按整体目标、真实进度、五RQ缺项、前三任务、真实结果、独立判断、通俗解释、下一关联工作包八部分汇报。
