# ModelRouter 全项目数据与成果入口

**Model-only接续**：[89题×24组×seed43](../results/benchmark/rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)使用11-11各18更新代表，固定Low/High/Max、教师OFF/ON；完整官方任务结果、模型/教师Token及Router本地Token分别保存。连接失败恢复和[87题×8联合主组](../experiments/configs/v9_joint_paired.json)沿同一脚本顺序接续，原两题联合结果复用。

**2026-11-12增量**：[新联合监督](../results/iterations/20261111-v9-rq4-joint/joint_supervision.json)复用两个合法Train截止，新增6个真实请求、5个原评价器有效结果；合并原候选后形成2条七候选偏好，加16辅助共18行。Laya/Kev均完成18次更新，新权重在A6000；[后续完整比较](../results/benchmark/rq1/terminal-bench-2.0/20261111-v9-joint-followup/review.md)的54位置全部结束，42通过/2失败/10缺评分、74原Trial，模型+教师已知参考费$0.73402850。2题历史已观察，原660万行及旧17行数据保持原身份。

**2026-11-09增量**：[正式Terminal-Bench 2.0 RQ1](../results/benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)已启动，89题×17策略、固定四并发。此批次独立保存官方结果/费用，不并入以下2.1历史覆盖或重复统计已有660万清洗行。四实体身份与实际原生前向见[model_entities](../results/benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/model_entities.json)。当前不新增训练，两个研究代表仍各17更新。

整理时间：2026-11-08，A6000现场取样19:10台北；源码HEAD为`688479af67b5b0682d67d43415af64a1011ecfe4`。公开清洗行数沿已保存统计，模型实体、进程和队列由本轮服务器文件取得。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

## 1. 现在有什么

| 成果 | 已有数量 | 性质与主要入口 |
|---|---:|---|
| 探索来源目录 | 35项来源/用途ID | 包含公开数据、自产调用、系统资料及未取得来源；[详细来源](DATA_SOURCE_AND_POLICY_REGISTRY.md) |
| 公开清洗数据 | 14源，6,600,628行 | 按步、回答、请求或任务计数，原始/清洗全量在A6000；[原统计](manifests/dataset_audit_report.json) |
| CCH／Blog／衍生汇总 | 110聚合行／221,128调用行／79衍生行 | 单位、粒度分别保留，不相加为独立任务 |
| 历史静态选择导出 | 83,259行 | 66,566 Train／8,343 Val／8,350 Test；分析16,360行；旧84,310版是历史 |
| 原S1/S2/S3训练候选 | 4,863,900条来源引用 | 31,766偏好／3,537,955观察动作／1,294,179资源辅助；原模型身份 |
| 原固定Val | S1 561／S2 337／S3 4,794问题 | S3来自2,244条记录；问题数和记录数分别保存 |
| 历史V9 Model-only偏好 | 40条 | 步骤质量23／等质量成本8／任务成本9，不是新K=3联合标签 |
| 当前GLM池训练输入 | 18行 | 2个七候选联合偏好截止＋16辅助；Hikari选Terra High、Dynaconf选Luna Xhigh；[新联合监督](../results/iterations/20261111-v9-rq4-joint/joint_supervision.json)。[11-08的17行](../results/iterations/20261108-v9-k3-training/joint_supervision.json)保留历史身份 |
| 真实实验目录 | 75个 | 其中43目录有原Harbor记录，合计198个不同trial_id、31个官方任务ID；[全部批次](../results/README.md#全项目迭代目录索引) |
| 正式Terminal-Bench 2.0 | 89题×17策略 | 全部1513位置结束，256通过／358失败／899缺评分，2333个Harbor Trial；[逐题Pass率与费用](../results/benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md) |
| 新训练与粒度/信息消融 | 2题×27策略 | 全部54位置结束，42通过／2失败／10缺评分、74原Trial；[独立批次终局](../results/benchmark/rq1/terminal-bench-2.0/20261111-v9-joint-followup/review.md) |
| Model-only完整任务消融 | 89题×24策略 | 18:38台北396位置结束；[本批逐任务结果](../results/benchmark/rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)。原始/18更新权重、三个固定档位与教师开关分别登记 |
| 历史Terminal-Bench 2.1 | 89题 | 29题有Agent尝试、22题有官方Reward、7题无终局、60题尚无Agent运行；[历史覆盖](../results/benchmark/README.md) |
| 11-08新池开发与三题比较 | 49次尝试 | 33有效终局：21个1／12个0；16无Reward；[逐条结果](../results/iterations/20261108-v9-k3-training/episode_results.json) |
| 当前AA能力 | v7，130指标 | Luna/Terra各六档，GLM仅Max；Low/High缺测，Index5.0.1 |
| 模型实体与训练历史 | 36个可见保存目录，125份run.json | 目录存在、历史训练记录、当前研究代表分别解释；[模型总报告](../results/training/training_research.md) |
| 文献材料 | 本地59个PDF文件 | 按文件计；论文、笔记和重复素材仍按各原索引追溯 |

## 2. 已取得并探索的14个公开源

数量采用10-19保存统计及后续原来源记录；本轮确认A6000全量目录仍在。

| 数据源 | 清洗行数 | 已研究的内容 | 当前用途 |
|---|---:|---|---|
| TRA-001 Open-SWE-Traces | 2,075,629 | 30,000轨迹ID、21,515任务；动作、已发生消息、终局及未知终局 | 观察性动作/结果、合法Train前缀、教师参考 |
| TRA-002 SWE-smith | 2,331,584 | 49,897轨迹ID、13,501任务；跨tool/xml/ticks重复、真实修复前缀 | 观察性动作及真实模型比较的任务来源 |
| TRA-004 AgentSuite | 41,430 | 273固定对话×30配置末次回答；严格thinking差异对290 | 回答/思考模式分析，不当完整Agent Episode |
| ROUTE-001 LLMRouterBench | 548,059 | 24,441完整问题；成绩冲突、同分费用及静态选择 | 历史静态分析；费用与数据许可未确定项保持 |
| ROUTE-002 RouterBench | 36,497 | 35,102唯一选择；87同分同估价、1,308无模型正确 | 历史静态导出；数据许可不一致未解决，不新增入当前训练 |
| ROUTE-003 TwinRouterBench | 970 | 520任务、八版本7,760预测，旧能力档位评价 | 仅外部评价，原结果不改为新模型/Effort答案 |
| ROUTE-004 Arena | 57,477 | 39,716明确人类偏好、17,761平局/双方差 | 原S1旧模型偏好 |
| ROUTE-005 FindingTheRightFit | 6,204 | Harness开销、缓存和费用 | 研究分析；原许可禁止训练/蒸馏 |
| CACHE-001 Mooncake | 39,632 | 37,416历史前缀复用机会；含3,993 synthetic记录 | 前缀机会与长度辅助；实际Provider读取另存 |
| TIME-001 BurstGPT | 1,404,294 | 到达时序、请求/响应长度、负载 | 原S3资源辅助 |
| ENV-001 SWE-Gym | 2,438 | Python任务、环境与原评价定义；已形成候选/关联材料 | 环境来源，新增轨迹许可未知部分只作观察 |
| ENV-002 SWE-rebench-V2 | 32,079 | 多语言任务、版本与环境恢复条件 | 任务环境；数据卡CC-BY-4.0，各仓库许可另保留 |
| MEM-003 LongMemEval-V2 | 451 | 长程记忆、会话和检索字段 | 记忆能力分析，未形成新池联合赢家 |
| MEM-005 MemoryCraft | 23,884 | 会话序列、问答与片段覆盖 | 记忆分析，未当动态路由标签 |

CMU TRA-003原403、MARBLE MAS-001原401，已有清洗记录均0。MAS相关资料仅保留研究历史，正式Single-Agent不执行角色协作。

其余已探索资料：CACHE-002旧Mooncake、CACHE-003/004缓存回放与合成负载、CACHE-006 vLLM指标、TIME-002 xMaaS、TIME-003 GenAI、MEM-001/002/004/006记忆基准、MAS-002/003历史协作资料及SYS-001结构参考。TIME-004复用原轨迹，不另计数据；CACHE-005现已积累真实Provider Usage。

## 3. 自有调用与科研执行数据

| 对象 | 位置 | 已取得信息 |
|---|---|---|
| OWN-001 CCH | [source/cch-model-cost-cache-statistics.csv](source/cch-model-cost-cache-statistics.csv) | 110聚合行，代表750,212调用；网关USD计账，不是逐任务供应商账单 |
| OWN-002 Blog | [cleaned/sxyq-blog-gpt-usage-cleaned.csv](cleaned/sxyq-blog-gpt-usage-cleaned.csv) | 221,128请求；198,359显式effort、185,154正缓存读取；费用单位quotaUnits |
| OWN-003 汇总 | [summaries/cch-sxyq-gpt-unified-summary.csv](summaries/cch-sxyq-gpt-unified-summary.csv) | 79衍生行，无新增独立观察 |
| 真实模型请求账本 | 仓库外发范围之外的原experiments/agent_pilot/token_budget.json | 请求身份、用量与缺测累计；不公开正文或私人凭据 |
| 原Harbor记录 | results/iterations原批次 | 每条trial_id、任务/设备/协议/参数、时间、工具、Verifier、Reward和异常 |
| 11-08模型/教师费 | [49条结果](../results/iterations/20261108-v9-k3-training/episode_results.json) | 已知参考$1.45700272；实收与计算资源价未知 |
| 11-08缓存 | 同一原事件和49条结果 | 读取5,572,672 Token；66条缺读取数，560次消息前缀连续；物理KV未知 |
| 11-08教师 | 同一原事件 | 68次触发/成功短评；训练17行只有1条复用真实教师，其余缺失状态 |
| 原生表示 | [native_encoding.json](../results/iterations/20261108-v9-k3-training/native_encoding.json) | 原34训练编码、241保存前缀48→0截断、四实体实际CUDA前向；原Episode版本不改 |

## 4. 从探索到训练的成果演变

| 阶段 | 取得的数据与研究结果 |
|---|---|
| 10-09至10-11公开数据 | 来源统计、14源清洗、静态选择、分析集、工具/记忆/缓存字段及真实单位差异 |
| 10-12至10-29原训练 | L1–L4、S1/S2/S3、ALGN及Kev R01–R16；固定Val、训练曲线、恢复和实体记录 |
| 10-29至10-31执行接入 | 原映射/Oracle记录、Provider实际响应、真实Sol/Luna前缀比较和Twin独立评价 |
| 11-01至11-05真实监督 | Model-only累计40；修复/恢复/同质量费用、任务关系及STEP_002–010；负结果与未知反馈保持 |
| 11-06至11-07旧HY4池 | 13组合、两架构各18更新、原官方三题及跟进；原任务已经观察 |
| 11-07至11-08新GLM池 | 15登记组合、AA v7、GLM实际工具、17行新池训练与独立完整Episode |
| 11-08最终编码 | 共享指标定义、实际前缀截断消除、四实体原生前向；新表示的完整训练/评价仍缺 |

83,259静态导出、4,863,900来源候选、40 Model-only和17新池训练材料各有重合及不同目标，不能相加成新池监督量。AA是能力先验，原Verifier未来结果只进入目标或终局报告。

## 5. 数据实际放在哪里

| 目录 | 实际职责 |
|---|---|
| A6000 /home/syy/路由/data/公开数据/原始数据 | 14公开源原始全量 |
| A6000 /home/syy/路由/data/公开数据/清洗数据 | 五类公开清洗全量 |
| 本机/服务器 our-project/data/公开数据/数据预览 | 来源统计与小预览，非另一份全量 |
| our-project/data/source、cleaned、summaries | 自有调用、清洗和衍生统计 |
| A6000 runs/MR-ALLDATA-PREP-20261011 | 原分级、批次、来源引用与同义训练视图 |
| A6000 runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012 | 原38组、固定Val、曲线与恢复 |
| our-project/code/data/v9/prepared | 旧390行实体及兼容导出；不同目录重复表示不累加 |
| results/iterations/.../training_view及training_delta | 已排除未知终局的382视图、真实40条目标及当前17行；各自版本保持 |
| results/iterations | 完整Episode、合法训练、编码、异常及私有原轨迹的原位置 |
| our-project/data/raw/v9-task-links | 后续任务关联材料；旧文“raw始终为空”已过时 |
| our-project/data/processed、training_views | A6000当前为空，不作新增成果 |
| A6000 models及runs各checkpoint | 原始、历史训练、新池研究和F15恢复参数；Mac不保存两Router权重 |

## 6. 模型已经确定到哪一步

当前原始实体为`models/laya-421m`和`models/kev-4b-adapter`；本次成对比较训练代表为`V9-K3-GLM-LAYA-20261111`与`V9-K3-GLM-KEV-20261111`，各18更新已完成，训练墙钟15.193/252.463秒。11-08各17更新代表用于旧89题seed42批次，历史结果与新seed43比较分开。旧固定Val参考仍Laya F11-e01、Kev R11；Serving仍F05-e01/原导入Kev。论文最终净收益版本待完整任务对照确定。

当前没有Laya/Kev训练进程。F15完成第1轮并保存61,180/122,360更新；游标曾记第2轮39/478块、66,172步，但当前不是活动训练，恢复实体仍61,180步。原38组25完成，F15半程、另外12组未完成。详细26个Kev候选、36保存目录与125份run.json见[训练总报告](../results/training/training_research.md)及同名JSON的`project_inventory_current`。

当前已取得两个合法截止的七候选联合偏好和新编码训练，54位置完整比较结束；仍缺早期/转折/恢复阶段的更多联合监督、GLM返回档位、全量成对任务评分、真实子任务边界对照、完整实收/资源价及多工作负载收益边界。
