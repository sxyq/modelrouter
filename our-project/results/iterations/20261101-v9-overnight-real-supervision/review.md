# ModelRouter V9 · 连续执行工作包结果

运行范围为真实 Provider K=2 模型比较，正式池仍为 Sol、Luna、Flash；本轮无 Alias，Flash未接通。请求low不等于实际low，当前有效目标仅为 `MODEL_ONLY_UNDER_RECORDED_PROVIDER_CONFIGURATION`。起点main为 `ea2987d2244ed978903a45c364ef944c3345a826`，原mini-SWE-agent 2.4.6、Harbor 0.24.0、Provider、Docker工具与准备入口复用。

## 1. 新训练任务与有效目标

| 项目 | 本轮结果 |
|---|---:|
| 来源候选 / 元数据获取失败、未启动Agent | 22 / 10 |
| 实际执行的不同Train任务 / 仓库 | 12 / 9 |
| 原Verifier可用的任务 | 9 |
| 双候选可信完整终局 / 双成功任务 | 7 / 7 |
| 双候选可信步骤比较 | 3；其中1组双方均未修复，无偏好 |
| 新任务级Model偏好 / 新步骤级Model偏好 | 7 / 2 |
| 新偏好覆盖的不同训练任务 | 7 |
| 本轮比较记录 / 无有效目标的比较 | 25 / 16 |
| 候选观察记录 | 44；含单边中断，不能当作44条动作目标 |
| 当前视图任务级 / 步骤级Model偏好 | 9 / 4 |
| 当前视图目标总数 / 不同任务数 | 13 / 9 |
| 当前视图Luna / Sol标签 | 12 / 1 |
| 确认的Model×Native Effort / 同模型Effort / 完整K=3目标 | 0 / 0 / 0 |

当前13条已包含历史TextFSM和Device的4条，只新增9条，不能再加旧delta。原Train196/Val186与当前视图可组合为209/186，原382行视图和13,214候选没有重加工。Train任务源为TRA-002、SWE-bench/SWE-smith train/MIT；原instance_id、repo、镜像版本、工具反馈与结果保留。任务身份及与Canary8/Dev24/Final57、TwinRouterBench和可识别派生题的关系见[task_isolation.json](task_isolation.json)；同仓库任务关联不丢弃，未知近重复不作全面结论。

`TASK_LEVEL_PREFERENCE`只使用完整Episode终局；`STEP_LEVEL_PREFERENCE`只描述原决策前缀之后的一步即时验证。未验证、身份不符、超时、中断及双方均失败记录为`OBSERVED_OUTCOME_ONLY`，不自动生成赢家。辅助轨迹和AA卡仍为辅助输入，不凭排行榜补选择标签。

## 2. 七组完整双成功终局

输入/输出为Provider真实Usage，输出已含reasoning，不能再次相加。动作列中的low均为请求参数：Sol返回max，Luna应用档位未报告。费用是原Registry模型费率估值，不是供应商账单。下列14个可用Episode全部通过，只描述已选择的简单训练任务，不能外推总体成功率。

| 任务 | 请求模型 | 原Verifier | 输入/输出Token | 模型费USD | 资源USD | 监督用途 |
|---|---|---:|---:|---:|---|---|
| t13 TinyDB AND | Sol low | 204/204 | 143388/8721 | 0.15343230 | 未计量 | 任务模型比较 |
| t13 TinyDB AND | Luna low | 204/204 | 334744/1482 | 0.00758944 | 未计量 | 等结果低费用偏好 |
| t14 PrettyTable | Sol low | 193/193 | 59731/5375 | 0.09166470 | 未计量 | 任务模型比较 |
| t14 PrettyTable | Luna low | 193/193 | 227964/1424 | 0.00832801 | 未计量 | 等结果低费用偏好 |
| t15 async-timeout | Sol low | 32/32 | 126206/7784 | 0.13588090 | 未计量 | 任务模型比较 |
| t15 async-timeout | Luna low | 32/32 | 261731/3451 | 0.00742081 | 未计量 | 等结果低费用偏好 |
| t16 PyASN1 ChoiceDecoder | Sol low | 1179/1179 | 120710/8364 | 0.14694320 | 未计量 | 任务模型比较 |
| t16 PyASN1 ChoiceDecoder | Luna low | 1179/1179 | 203359/1289 | 0.00563513 | 未计量 | 等结果低费用偏好 |
| t18 Records | Sol low | 24/24 | 96469/13034 | 0.17975430 | 未计量 | 任务模型比较 |
| t18 Records | Luna low | 24/24 | 363851/2533 | 0.00789112 | 未计量 | 等结果低费用偏好 |
| t19 Autograd | Sol low | 585/585 | 68808/6123 | 0.12608190 | 未计量 | 任务模型比较 |
| t19 Autograd | Luna low | 585/585 | 193865/2015 | 0.00582507 | 未计量 | 等结果低费用偏好 |
| t21 TinyDB cache | Sol low | 204/204 | 142785/9662 | 0.17286580 | 未计量 | 任务模型比较 |
| t21 TinyDB cache | Luna low | 204/204 | 250330/1461 | 0.00633763 | 未计量 | 等结果低费用偏好 |

七个新任务目标全部偏好Luna，依据仅为该次相同原Verifier结果下的模型费用。缓存读写、Provider协议和账户分别记录；没有把物理缓存状态或供应商内部上下文说成已相同。

| 其余实际任务 | 真实结果与限制 | 标签 |
|---|---|---|
| t01 Schema | Sol 11生成、116/116、0.23518810USD；Luna多个请求/格式/身份问题，无可信终局 | 无 |
| t12 Mido | Sol 10生成、已知0.16463220USD；原测试路径为仓库外`../dev/tests/...`，恢复原验证文件退出128，Verifier未运行 | 无，终局未知 |
| t17 gTTS | 原完整验证依赖Google网络、超时；Luna还出现Provider失败 | 无，终局未知 |
| t20 gTTS-lang | 双方原完整验证网络超时，未删减测试或换验证器 | 无，终局未知 |
| t22 PyASN1 bitstring | Luna 1179/1179、0.00671302USD；Sol首请求TimeoutError，无返回身份或Usage | 无，不把超时当质量败者 |

另有t13早期Luna中断和t14步骤Luna八分钟无返回响应；原失败、未知用量与单边执行保留，没有重发这些请求。

## 3. 新步骤监督

两组分支均使用相同已发生消息和真实环境快照，结果只归对应的一步目标，不复制任务级成本赢家到所有步骤。候选未来反馈不进入此前状态，采集教师关闭。

| 同一前缀 | 候选请求 | 一步后原Verifier | 输入/输出Token | 模型费USD | 结果 |
|---|---|---:|---:|---:|---|
| TinyDB恢复前缀7 | Sol low | 200/204 | 10051/437 | 0.00948000 | 未即时修复 |
| TinyDB恢复前缀7 | Luna low | 204/204 | 37171/291 | 0.00051748 | 步骤Model偏好 |
| Records恢复前缀6 | Sol low | 23/24 | 7492/576 | 0.02198050 | 未即时修复 |
| Records恢复前缀6 | Luna low | 24/24 | 62298/648 | 0.00099144 | 步骤Model偏好 |

TinyDB前缀6双方200/204，不生成赢家。PrettyTable新前缀Sol191/193、Luna中断，只作观察；预定Autograd步骤未启动，不计尝试。历史TextFSM步骤Sol即时修复偏好仍保留，没有为了统一成本标签而改成Luna。

## 4. Native Effort与Flash

训练采集的109份Sol low和1份Sol medium原响应均报告`reasoning.effort=max`；88份Luna low和1份Luna none不报告应用档位。执行忽略参数还是返回元数据有误仍未知，启用Sol渠道的`param_override`为空不能确定原因。

| 尝试 | 结果 | Effort监督 |
|---|---|---:|
| Schema同前缀Sol low/medium | 两者均报告max，缓存不同 | 0 |
| TinyDB同前缀Luna low/none | 应用档位未报告，缓存不同；reasoning出现本身不证明档位生效 | 0 |
| Records同前缀Sol Chat low/medium | 两次HTTP400，无工具或可信终局 | 0 |

不把Alias none用于Sol，不把返回max改写成新的训练动作。目标选项只保留模型身份，`native_effort=null`；`requested_native_effort`作为此前已知配置输入保留。正式原生菜单仍以原Registry/厂商资料为依据，供应商是否实际执行该档位另记。

06:03的两个已有账户只读目录均HTTP200，OneAPI有Sol/Luna、项目账户只有Luna，均无Flash；本轮Flash生成探测0，没有重发旧404/503。见[provider_availability.json](provider_availability.json)、[native_effort_analysis.json](native_effort_analysis.json)。正式K=3池不变，不以K=2冒充K=3。

## 5. 两个真实Dev与教师

原公开Dev、同一工具协议和原官方Verifier继续复用，全部不进入Train。当前Router为Serving F05-e01，没有学过本轮新目标；固定策略通过原入口执行，不人为扰动Router概率。

| Dev任务 / 策略 | 生成 / 已记录工具结果 | Sol/Luna选择 | 原Verifier | 模型费USD（含教师） | 完整Trial秒 |
|---|---:|---:|---|---:|---:|
| configure-git-webserver / F05无教师 | 30 / 30 | 0/30 | reward0，CTRF0/1 | 0.01776893 | 877.831667 |
| configure-git-webserver / 固定Sol | 4 / 2 | 4/0 | 安装工具超时，未运行Verifier，reward未知 | 0.07442100 | 199.337526 |
| configure-git-webserver / F05有教师 | 7 / 7 | 0/7 | reward0，CTRF0/1 | 0.01712057 | 146.896552 |
| filter-js-from-html / F05无教师 | 15 / 9 | 3/12 | reward0，CTRF0/2 | 0.07949004 | 1349.535347 |
| filter-js-from-html / 固定Luna | 3 / 3 | 0/3 | reward0，CTRF0/2 | 0.00111207 | 856.316198 |

“已记录工具结果”只计真实TOOL_END，不把格式错误生成或尚未返回的工具尝试算为已完成工具执行。动态HTML任务以RepeatedFormatError退出，固定Luna为Submitted；两者原XSS与clean-HTML两个测试均失败，均改变5/12份合法HTML。保留原测试，不人工修改模型产物或生成质量赢家。

三个F05 Episode共52次真实路由，fallback0。Git无教师的Luna概率0.5052–0.5657，有教师为0.5052–0.5928，均无切换。HTML任务发生一次自然Sol→Luna切换，原概率如下；阶段来自此前已记录工具命令的原启发式，不是人工阶段标签。

| 决策step | 此前工具阶段 | P(Sol) | P(Luna) | 选择 |
|---:|---|---:|---:|---|
| 0 | 无此前工具 | 0.5269 | 0.4731 | Sol |
| 1 | verify | 0.5071 | 0.4929 | Sol |
| 2 | verify | 0.5048 | 0.4952 | Sol |
| 3 | verify | 0.4749 | 0.5251 | Luna |
| 4 | modify | 0.4798 | 0.5202 | Luna |
| 5 | modify | 0.4230 | 0.5770 | Luna |
| 6 | modify | 0.4325 | 0.5675 | Luna |
| 7 | modify | 0.4445 | 0.5555 | Luna |
| 8 | modify | 0.4218 | 0.5782 | Luna |
| 9 | modify | 0.4316 | 0.5684 | Luna |
| 10 | modify | 0.4375 | 0.5625 | Luna |
| 11 | modify | 0.4097 | 0.5903 | Luna |
| 12 | modify | 0.4369 | 0.5631 | Luna |
| 13 | modify | 0.4441 | 0.5559 | Luna |
| 14 | modify | 0.4434 | 0.5566 | Luna |

新教师1请求/1成功、无重试；首次3生成后触发，短评进入steps3/4/5/6共4次。输入983、输出1112含reasoning1034，23.281411秒、0.013086USD；请求Sol low、返回max。三字段完整JSON，只评估此前事实并进入Router，不改变Agent Prompt、计划、工具或模型选择。教师Episode生成费用0.00403457USD，教师费用0.013086USD。

既有JSON失败主要是reasoning耗尽输出额度、`finish_reason=length`后正文为空；JSON Object只能约束正文格式，不能保证reasoning后仍有完整正文。本轮沿用紧凑三字符串Prompt、4096输出/context8000、首次3生成及低频信号触发，只去掉未经证据确认的effective low元数据，没有再增加上限或建设重试体系。旧失败费用与未知Usage账本保留，没有重复请求。

教师开/关都失败；模型费用接近但轨迹7/30生成、缓存和共享锁等待不同，无教师首请求约630秒包含等待。HTML两个策略也都失败，费用低不等于质量赢家。当前不能证明动态Router或教师净收益。全部候选概率、工具与费用见[dev_comparison.json](dev_comparison.json)及各原events/Provider响应/Harbor产物。

## 6. 费用与能力快照

| 范围 | 请求 | Usage与缺测 | 已知模型费率USD |
|---|---:|---|---:|
| Train采集 | 209 | 199份Usage，10次用量缺失；3份已返回响应无法计价 | 1.85298918 |
| 五个Dev Episode及教师 | 60（59生成+1教师） | 实际Usage与原Provider费率 | 0.18991261 |
| 本工作包 | 269 | 完整模型费、供应商实收和资源USD仍未知 | 2.04290179 |

Train已知输入3958403/输出127710Token，reasoning69992已包含在输出中；缓存、reasoning缺报字段不填0，详见[request_usage.jsonl](request_usage.jsonl)。本轮未设置累计Token或美元限制；中断请求既有未知用量记账不重复。费率见[request_model_rates.json](request_model_rates.json)，不是27B Alias映射价。供应商实收、Router CPU和Docker资源USD均未计量，不把已知小计写成完整成本。

全部新增视图及Dev绑定AA `20261031T072548885180Z-v4`，本轮未运行刷新。Sol/Luna **Max**各10项，共20项；Intelligence Index v5.0原分54.5087338138148/27.7552004938153。low、none、托管Flash及缺失专业综合项继续NOT_MEASURED，不给low套Max分数或借用Flash-Next/27B成绩。三份厂商资料与原来源保留。

## 7. 训练接续与独立四档

原Prepare生成13条S1模型视图和相对链接，本机/服务器原serialize_training_record均成功消费13条，task_model_preference与step_model_preference分别编码；完整过去消息保留，候选未来结果仅供目标。teacher=null，AA v4、requested_native_effort保留，状态文本5069–11079字符。序列化成功不代表两模型原窗口完整保留所有内容，输入覆盖仍须在具体继续微调配方中明确。

Laya F11-e01、Kev R11继续作为研究代表。本轮无新训练、参数更新、候选注册或Serving替换；旧V9两轮Laya8更新/Kev100更新及负结果保留。原Laya encoder/head按freeze_encoder配置，原Kev LoRA/pointer head沿父配置接续；旧S1与新task/step目标分开，不能用当前模型目标训练未确认的Effort。13条来自9任务但12条选Luna、步骤只有4条、联合档位目标0，当前不复用已退步配方启动微调。收益仍由原固定Val Accuracy/Loss/Brier/ECE及独立真实Dev的任务成功和完整成本判断。

独立TwinRouterBench八份结果未重跑，也未用标签训练或调参。gold为689/62/49/170，F11为173/788/2/7，R11为13/53/588/316。旧S1模型候选偏好、S2终局与S3资源档位不等于外部能力四档；R11继续训练4269行只有S2/S3，Laya导入权重已经950次预测mid。原前400字符编码使970步只有318个不同Context、58个多步任务输入不变。现有材料未证明选项索引错位，各因素因果贡献及导入权重原训练分布未知。F11 20.515464、R11 18.969072较各自微调前改善，但仍低于恒选low71.030928；不按独立集重选前三或晋升。原[独立评分](../20261031-twinrouterbench-independent/review.md)和[四档分析](../20261101-v9-k2-supervision-expansion/four_tier_analysis.json)继续作为唯一结果。

## 8. 服务器、源码与清理

06:26:47服务器实读：原队列PAUSED_USER_REQUEST/current_run=null、两组活动训练0；F01–F13及Kev R01–R16完训、R系列固定Val全EVALUATED。F14归档failed/NON_FINITE_LOSS，结束2026-10-31T09:01:02Z；不恢复旧队列。Serving仍PID327621、F05-e01/原Kev Adapter，没有重启、换权重或干预共享GPU。

10份相关源码和新视图已定向传入原服务器工程，06:33:55原serializer消费13条成功；六份规划、两份训练报告及完整结果已完成定向同步。07:04:32实读仍无活动训练，原队列暂停、F14失败归档、Kev R01–R16全完训/评估，Serving仍PID327621及原权重。服务器不是完整Git checkout，材料同步不代表Serving运行版本更新。openrsync误生成的绝对路径前缀副本已在正确传输后移除。17个本轮Docker临时快照、临时采集工具与自有SSH隧道已清理；原任务镜像、定义、真实响应、Verifier、失败和训练记录保留，环境可依据这些材料重建。

修改仅在原Provider的分模型端点/协议与返回Effort记录、原Harbor运输解析和产物读取、V9验证文件恢复、原教师Effort元数据，以及现有prepare/real_supervision/能力卡/状态编码接点；没有第二套Harness、Provider、Trainer、Ledger或监测服务，没有新增/运行项目测试或定时任务。六份规划与原训练报告同步实际结果，正式五RQ、八图十二表不改。

公开结果中的个人机器路径按用途改为项目相对路径或本地标记，响应正文、Usage、模型身份、原Verifier结果及失败事实保留；带私人路径的运行日志、整工作树diff和服务器原取样不公开，原件在本地保留。

剩余主研究工作：供应商可确认的Native Effort、真实Flash，更多不同任务且具有Sol/Luna差异的步骤监督，保留旧S1并覆盖真实状态的继续微调，以及独立Dev上的动态路由和教师净收益。当前真实差异、未知终局和负结果均保留，不把K=2/Model-only成果写成完整三模型联合研究完成。
