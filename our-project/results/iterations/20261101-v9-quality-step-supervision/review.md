# V9：质量步骤监督、Laya定向接续与独立Dev

从GitHub main `63057a4a7586e9a9b717ccf53697d1e448c029a6`接续；运行时包含本轮源码改动。复用原Provider、mini-SWE-agent 2.4.6、DockerEnvironment、Harbor、Prepare、Trainer及LayaAdapter。正式三模型身份和五RQ、八图十二表保持；实际采集范围为 **K=2 / MODEL_ONLY**，无Alias。

## 1. 新增质量步骤证据

使用四个已经执行过的SWE-smith Train任务的新失败前缀，同一已发生消息历史及可恢复工具环境分别交给真实Sol/Luna，实际执行一步工具并运行原任务验证。任务身份、原提交、前缀、环境恢复和两候选反馈保留在各任务目录。教师关闭，候选未来反馈不进入决策前状态。

| 训练任务与截止前缀 | Sol原验证 | Luna原验证 | 有效目标 | Sol / Luna模型费USD |
|---|---:|---:|---|---:|
| Autograd / 4 | 585/585 | 583通过、2失败 | Sol，质量差异 | 0.061636 / 0.0042136 |
| PyASN1 ChoiceDecoder / 6 | 1179/1179 | 1175通过、4失败 | Sol，质量差异 | 0.0732235 / 0.0046768 |
| async-timeout / 6 | 32/32 | 29通过、3失败 | Sol，质量差异 | 0.0451635 / 0.0020758 |
| TinyDB cache / 5 | 204/204 | 204/204 | Luna，等质量低模型费 | 0.059211 / 0.0049644 |

本轮新增来源任务 **0**，四个新前缀覆盖 **4个已有训练任务、4个仓库**；新增步骤偏好 **4条，Sol3/Luna1**，新增任务级偏好0。它们只监督该步及相应验证范围，不代表完整Episode胜负。原任务隔离证据沿用已保存的Train来源和Canary/Dev/Final及可识别派生题元数据，不把同任务新前缀另算独立任务。

唯一当前动作视图为 [training_delta/model_comparison/train.jsonl](training_delta/model_comparison/train.jsonl)，17条已含上一轮13条，不再另加旧delta：

| 当前监督 | 数量与用途 |
|---|---|
| TASK_LEVEL_PREFERENCE | 9条，均为等终局质量成本偏好；本轮接续不使用 |
| STEP_LEVEL_PREFERENCE | 8条，Sol4/Luna4；7条质量差异、1条等质量成本 |
| 独立身份 | 全部偏好9个任务；步骤偏好8个任务、7个仓库，TinyDB有两个不同任务 |
| 全部Model标签 | Sol4 / Luna13；17条允许Train，Dev不进入此视图 |
| Model×Native Effort / 同模型Effort / K=3 | 0 / 0 / 0 |
| 原材料组合 | Train196 + 17 = 213；prepared Val186保持；本轮实际训练72条另见下节 |

首轮Sol401、Luna仅文本而无工具动作、一次中断等记录保留为OBSERVED_OUTCOME_ONLY或UNLABELED，不生成胜者。四份有效 `comparison-oneapi.json` 已被原Prepare消费；完整比较和用量见 [supervision_analysis.json](supervision_analysis.json)。原390实体、有效382视图、13,214历史候选没有重新加工或改写为新动作监督。

## 2. Effort、Flash、能力卡与教师

Provider现在保存实际发送参数：Sol发送 `reasoning.effort=low`，返回报告max；Luna发送 `reasoning_effort=low`，未报告应用档位。供应商是否替换参数、忽略参数或仅报告方式不同仍未知。训练及MODEL_ONLY运行卡中 `native_effort=null`，请求low另列，不作为目标；未继续同条件无效Effort探测。

11:50台北，现有OneAPI账户 `/models` HTTP200，目录5型号，Sol/Luna存在、Flash不存在，见 [provider_availability.json](provider_availability.json)。没有重复旧Flash404/503请求，也未以27B替代。AA固定 `20261031T072548885180Z-v4`：Sol/Luna Max各10项，Intelligence Index v5.0分别54.5087338138148、27.7552004938153；low、none、托管Flash及缺测综合项仍NOT_MEASURED，没有刷新或借用Max作low成绩。

本轮教师0调用、费用0，Assessor/Trigger未改；两固定参考、低频触发与短评失效规则保留。上一轮真实教师1成功、4次Router消费、0.013086USD，仍未证明成本净收益。保存的旧Dev教师输入仅用于编码读取，三字段及截止step3完整，不加入Train。

## 3. 训练输入与一次实际接续

原Context/Serializer现在统一用于真实比较：任务优先，最近工具的命令与输出一起保留、最新反馈先排，候选摘要提前放价格；Prepare与Trainer共享同一文本生成函数。完整原始消息保留在 `observed_messages`，canonical输入仍为原6k字符任务/工具视图，不声称它等于全部原始消息。

[encoding_effective.json](encoding_effective.json) 的17条真实状态显示：Laya原1024窗口全部裁剪，完整历史8/17、候选摘要9/17、最近反馈14/17；4096仍裁2条。5120窗口保留 **17/17完整canonical状态及两模型选项**，最长状态4252Token，encoder支持8192。Kev最大状态3700Token，8K可容纳，R11父384窗口不适配；本轮Kev未训练。两类问题ID分开，新模型目标不与旧四档choice混用。

沿原 `run_sweep_experiment` 实际完成 **V9_LAYA_STEP_001**：

| 项目 | 实际值 |
|---|---|
| 父权重 | F11-e01，weight_only接续 |
| 数据 | 原64条S1人类模型偏好 + 8条真实步骤Model-only；共72条，未使用9条任务成本偏好 |
| 更新 | 1 epoch、9次优化器更新；micro_batch2、grad_accum4、seed42 |
| 参数 | freeze_encoder=true，仅原pointer head；head_lr2e-5，max_len5120/head512 |
| 信息 | AA v4，教师目标0、Effort目标0；实际72/72状态及能力信息完整保留、拒收0 |
| 实体 | `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/V9_LAYA_STEP_001/checkpoints/epoch_01`；best指向该实体 |
| 大小 | model.safetensors 842609220字节，完整checkpoint846196996字节；仅在服务器 |
| 有效保存时间 | 2026-11-01T04:13:14Z–04:13:37Z |
| 训练 / Val / epoch秒 | 7.948 / 12.678 / 22.8；GPU峰值2493.08MiB |

原固定 **S1 Val561项**（不是prepared Val186）的结果：

| 版本 | Accuracy | Loss | Brier | ECE |
|---|---:|---:|---:|---:|
| 父F11-e01 | 0.6898 | 0.5941 | 0.4085 | 0.0378 |
| V9_LAYA_STEP_001-e01 | 0.6898 | 0.5938 | 0.4083 | 0.0362 |

未观察到该固定S1的Accuracy退步，其他指标仅小幅变化；这不证明动态路由收益。训练Loss0.644704312086。记录见 [laya_step_training.json](laya_step_training.json)。

第一次计算完成后，原15%新候选额度将本组唯一权重移除，原因 `outside_new_core_pool_15pct_quota(1/2)`：两个单候选组按原分配只有一个额度，本组额度0。该尝试原元数据和缺权重Dev失败均保留；不是NaN，也不是协议未被识别。沿同一Run从F11恢复产物，使用原 `explicit_pinned`，并使原public摘要复用调用方的RetentionManager，不再丢弃显式保留参数。最终实体为PINNED_PARENT。两次计算不累计成18步，最终模型仍为从F11的9次更新；未创建新候选、另一套留存逻辑或恢复旧队列。

## 4. 独立Dev：没有可信质量胜者

新公开Dev `custom-memory-heap-crash`，同seed42、初始role/content、原mini/Harbor、30步、输出4096，教师关闭；内部供应商上下文及物理缓存同一性未知。三策略结果见 [dev_comparison.json](dev_comparison.json)：

| 策略 | 生成 / 完整工具结果 | 原Verifier与终局 | 模型费USD | Trial秒 |
|---|---:|---|---:|---:|
| 固定Sol | 7 / 6 | 工具30秒超时，Verifier未运行，reward未知 | 0.1367668 | 553.177141 |
| 固定Luna | 7 / 6 | reward0，CTRF5/6，Release失败 | 0.00188939 | 113.584711 |
| 新Laya | 7 / 6 | 工具30秒超时，Verifier未运行，reward未知 | 0.1809328 | 601.404901 |

各策略7次Agent工具动作请求；Luna末次提交，两个Sol路径末次超时，均只有6份完整工具结果。新Laya真实CPU前向 **7次、全Sol、切换0、fallback0**，checkpoint身份为V9_LAYA_STEP_001-e01。Sol概率按步骤为 **.5393/.5476/.5258/.5152/.5192/.5088/.5042**，阶段inspect/inspect/modify/recover/recover/modify/modify；未改继承温度或概率。

新Laya Router共363.676257秒，其中真实前向141.258480秒，其余主要来自原Adapter每次加载与SSH开销；Agent593.070983秒。最后验证命令超过原30秒工具窗口，Harbor抛RuntimeError而未运行Verifier。此前工具中的Release/Debug/Valgrind通过只是观察，不能替代官方Episode终局。原artifact manifest为空，没有保存真实/app修改，现有regrade不能恢复此Trial；没有重建产物、加长窗口或重跑该题。

原缺权重Trial保存在 `dev-custom-memory-heap-crash-laya/failed_trials/custom-memory-heap-crash__UdyTKDt`，0路由、0生成；空resume不计新Episode。实际新权重Trial为 `custom-memory-heap-crash__KPdAsZZ` / `91528f8a-0ddf-49bf-844c-40a31ffd0b52`。两份未知终局不填0；固定Luna已验证失败1/1，新Laya和固定Sol成功率不可计算。三份Dev只作观察，不进入Train或生成质量偏好，不能证明新权重优于父权重或固定策略。

## 5. 成本、服务器状态与接续缺口

P0共16请求、11份Usage、5次未知；有效8请求0.2551646USD，首轮三份无效文本响应0.0007873USD，已知小计 **0.2559519USD**。中断用量已沿原账本记未知一次，没有重复补记。Dev21请求均有Usage，已知 **0.31958899USD**。本轮总计 **37请求、32份Usage、5未知，已知模型费率0.57554089USD**；教师0，完整模型费、供应商实收和工具/容器资源USD未知。费用按真实请求型号费率与Provider Usage，不使用Alias映射价格。

12:57:52台北读取现行Run与PID：另项维护已经冷启原F14，PID808492、started_at=2026-11-01T03:31:49Z，Epoch1块25/420、step3200/107404、consumed204800/6873816、最新Loss0.5952016992741846；最近12块有限，未完成固定Val、不作父权重。旧failed_attempt_0001中的failed/NON_FINITE_LOSS和结束2026-10-31T09:01:02Z保留，先前12:32读到该归档不能代表当前F14状态。原queue_state.json仍PAUSED_USER_REQUEST/current_run=null、时间为10-31，但已有handoff817520等待F14退出后接原队列；本轮未创建、重启或操作它，也不覆盖维护任务的Trainer入口改动。本轮V9已结束、Kev没有活动训练，R01–R16全COMPLETED/EVALUATED。Serving health/models均200、PID327621及F05-e01/原Kev Adapter保持，未替换或重启；12:56 GPU9929/49140MiB、0%、75°C，现含F14训练，未干预。F11-e01/R11继续为研究代表，新Laya为实验候选，Mac没有模型权重。

本轮移除4个临时前缀Docker快照、误放根目录的重复summary和临时采集/编码/训练/Dev脚本目录，原镜像、真实失败、训练记录和正式结果保留。私人路径在公开结果中用占位值表示，原私人运行log和包含用户其他修改的source_changes.patch不公开；没有新测试、CI、服务、训练队列或未来任务。

本轮9个源码对象、六规划、两训练报告和238份公开结果已定向同步原服务器工程，未整文件覆盖服务器Trainer的其他差异。服务器不是Git checkout，不能用本次GitHub提交描述旧Serving运行版本。

| 源码位置 | 本轮必要变化 |
|---|---|
| [Provider](../../../code/src/modelrouter/providers/provider.py) | 留存实际effort参数，中断请求按原账本记录未知后继续抛出 |
| [Context](../../../code/src/modelrouter/v9/runtime/context.py)、[Prepare](../../../code/src/modelrouter/v9/training/prepare.py)、[Serializer](../../../code/src/modelrouter/v9/training/continuation.py) | 最新工具反馈、候选价格顺序及同一canonical编码 |
| [原Laya Trainer](../../../../router_data/laya_batch_train.py) | 复用spec的batch参数与原RetentionManager；用户两处初始化变化保留、不提交 |
| [checkpoint接点](../../../code/src/modelrouter/v9/runtime/checkpoint.py)、[RouterDecision](../../../code/src/modelrouter/agent/router_clients.py)、[Harbor](../../../code/src/modelrouter/benchmark/harbor_agent.py)、[DecisionHook](../../../code/src/modelrouter/v9/runtime/decision_hook.py) | 实验权重使用原CPU Adapter，记录真实身份，MODEL_ONLY卡实际Effort为空；旧Serving不替换 |

下一阶段仍需更多不同训练任务中的双向质量步骤差异、可确认的Native Effort、真实Flash渠道、独立Dev的完整Verifier终局，以及Router成本和教师净收益证据。8个步骤任务支持这次有限head接续，不足以证明联合动作泛化或全面启动Kev新训练。TwinRouterBench八版本不重评、不调参、不用于新监督；本轮新权重未在该独立静态集评价。
