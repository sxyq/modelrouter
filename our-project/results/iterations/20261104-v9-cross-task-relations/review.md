# V9：跨任务质量关系与独立条件选择

## 本轮目标与研究范围

继续 K=2 Sol/Luna：真实动作前状态决定质量优先、费用次之的选择，最终用独立完整 Episode 证明包含 Router 开销的净收益。本批完成新状态恢复、真实配对、完整/局部关系与最终动作的增量评价；神经训练和完整 Dev 依据真实证据决定，不预设执行。

起点 main 为 `6459cf0be040ff0b0b2448aa6fbf22aafbc11f2d`。原 Chai/brutils/Boxwood/W3C、Shep/Narwhals/pgmpy/Sacred、Vuex/Dynaconf、STEP009/010训练、256/1024摘要实验和历史Dev没有重做。原38组训练接续与本批研究分开；不改其运行队列、共享Serving或权重。

## 新状态与环境依据

复用TRA-001既有2500条分片及ENV-002 Train规格，不下载全量原数据。五状态共恢复110条原工具动作，当前均由原Context/Prepare的已观察反馈判为Modify，不使用下一动作赋阶段。每个截止点都有成功源码写入；原固定测试与完整passed集合匹配口径保持。来源、许可、版本、截止、用途及资格见 [source_selection.json](source_selection.json)，环境对齐见 [state_analysis.json](state_analysis.json)。

| 任务 | 事前用途 | 恢复动作 | 固定F2P/P2P | 初始可信通过 |
|---|---|---:|---:|---:|
| Relé 160 | Train | 17 | 8/0 | 7/8 |
| Optax 467 | Train | 25 | 19/138 | 157/157 |
| APIFlask 178 | 仓库留出 | 16 | 1/24 | 24/25 |
| Datumaro 1138 | 仓库留出 | 41 | 133/0 | 131/133 |
| Hikari 2224 | 补充Train | 11 | 1/410 | 410/411 |

前四用途在14:52 UTC固定；Hikari在16:13 UTC、其请求之前补选。前四仓库资格索引仅L4，F11记录为原基座起训，已追踪Encoder来源是L1/L2全量及L3部分、不是L4；原S1未匹配这些任务。这里的独立性限定于可追踪祖先训练范围，不推断基座预训练语料。Hikari任务仅L4，但同仓库有185条L1、83条L2 Train资格记录及其他分割，实际成员未知，不能称整个仓库未见。两个仓库留出不参与拟合或梯度；今后已查看结果时应称研究观察，而不是新的最终测试。

本轮没有新的Recover；旧Narwhals P2P恢复观察继续保留。Optax固定全过，没有增量问题，所以不收费生成。四配对覆盖订阅阻塞、HTTP异常继承、VCS目录保护、REST参数删除，不是四次相同机制的修复。

### 两处源码目录与原评价

原轨迹中的安装目录与`/testbed`独立，不能链接成同一目录。本轮保留两处文件系统，按实际CWD重放，导出`/testbed`当前源码patch。初始验证及APIFlask恢复直接调用原上游`run_in_container()`，在鲜原镜像中应用该patch及原test_patch；其余候选沿原NativeStep，在独立状态容器的原安装目录使用同一源码patch、原test_patch、原test_cmd、原Parser和完整passed集合匹配。没有改上游函数、测试定义或固定ID。这些是可信原范围的一步比较，metrics仍保留`LOCAL_VERIFICATION_ONLY`；不冒称新的Harbor完整Episode或官方Reward。

APIFlask最初读安装目录时出现“未改码、双方24/25”的错误口径。保存的两条模型动作实际显式写`/testbed`；分别恢复原动作及源码patch，不重新生成。Sol确实改两个源码文件并25/25；Luna改一个源码文件而24/25。原工具均退出1，不能据此推断写入未发生。恢复评价口径不属于模型学习或泛化改善。旧错误结果与重放资料保留私有目录。

Datumaro第50条历史诊断原退出0，首次恢复因`/testbed`缺编译扩展而退出1。原镜像的安装目录有对应`_capi`和`rust_api`产物，本轮复制原产物，不改业务源码，原诊断再次退出0。已保存Sol动作在恢复环境重放后源码patch与原固定验证输入完全相同，复用其133/133结果；缺失Luna的定向补采使用相同恢复环境。没有把环境导入错误当成模型失败。

## 实际模型结果与监督

最终固定结果以 [summary.json](summary.json)、[local_evidence.json](local_evidence.json)、[formal_preferences.json](formal_preferences.json) 为准。

| 任务 | Sol | Luna | 完整关系 | 正式语义 |
|---|---:|---:|---|---|
| Relé | 7/8 | 7/8 | NEITHER_VERIFIED | 无赢家，双方无局部改善 |
| APIFlask | 25/25 | 24/25 | SOL_ONLY_VERIFIED | 留出Sol质量优势，修复1个F2P |
| Hikari | 411/411 | 410/411 | SOL_ONLY_VERIFIED | Train Sol质量优势，修复1个F2P |
| Datumaro | 133/133 | 131/133 | SOL_ONLY_VERIFIED | 留出Sol质量优势，修复2个F2P |

Relé的Sol在原端点两次502无生成，之后沿原Provider实例选择已有colink恢复；Luna原有效结果不重发。Hikari Luna原请求502，实际证明该状态发生在账户池，原切换列表缺502，故只在原Provider HTTP列表加入502一项；原工程账户、凭据与Serving不改。Datumaro启动控制器载入该改动之前的模块，Luna首请求502无结果，保留失败后仅补Luna。所有异常用量和实收保持未知，不记为0或质量失败。

Datumaro Luna补采HTTP200、身份相符、工具调用完整，但选择执行原镜像没有的shell `apply_patch`，补丁未应用；随后原诊断退出0掩盖前一命令错误。Schema只提供“Execute a bash command”，原历史没有承诺该程序。这里是已实际执行的候选动作使用不存在的程序，不是Provider无输出或漏恢复原承诺工具；不人工翻译补丁替模型完成任务。固定业务结果与动作失败原因分别记录，也不把一次行为推成长期成功概率。

本批新增局部记录保留每个目标F2P修复、初始P2P恢复及新增回归的实际ID集合。APIFlask/Hikari/Datumaro的局部优势与完整赢家重合，均无新增回归；Relé提供“双方未完成且双方没有改善”的完整/局部Train负例。既有Stingray双方未完成但Sol修复F2P、Narwhals恢复初始P2P，仍是超出完整单赢家的额外机制；不能把P2P恢复改称F2P或正式赢家。本批没有新的双方未完成但局部严格优势。

正式偏好37→40：新增Train Hikari1、仓库留出APIFlask/Datumaro2，三项均Sol质量。现有步骤质量23（Sol18/Luna5）、步骤等质量费用8和任务费用9；两类费用偏好均Luna。Hikari沿原Prepare/Serializer保存为私有S1，未用两个留出拟合或更新梯度。记录数不是独立任务数，所有旧来源身份保持。

## 关系学习、动作与独立性

复用STEP009/010现有Encoder和`continuation.fit_preference_reference()`，固定ridge=1，无参数搜索。A原单赢家22条扩为23条；B4完整关系27条扩为29条（ReléNEITHER及HikariSol质量）；F2P分轴8条扩为10条，相同/Sol优势由4/4变为5/5，没有Luna优势类别。P2P恢复仍仅一个Train任务，回归仍只有相同，不能宣称学会恢复/回归判断。

另直接复用`fit_candidate_outcome_reference()`分别学习每候选在记录的一步是否修复过至少一个初始F2P。旧8条Sol/Luna正例5/2，新10条6/2。这个最小辅助目标能区分相同关系中的“双方无改善”与“双方均修复一些”；不代表完整通过、未观察到的成功概率，也不参与正式动作映射。原机会集合用于标签与评价，不进入在线输入。

原生Head和A只输出模型动作，完整关系正确率不适用。B4独过对应质量模型、双方通过对应低参考费模型、双方未完成无正式赢家。局部优势单独评价，不改正式动作正确率。Optax没有候选真值，全部正确率为null。Train观察不加入独立成绩。

新结果前的原始预测在 [pre_outcome_predictions.json](pre_outcome_predictions.json)；CWD对齐及Hikari补充前向分别在其请求前完成，日志时间保留。`pre_outcome_aligned_predictions.json`最终保存的是16:46 UTC固定新增Train参照快照，已在APIFlask/Hikari结果之后、Datumaro有效结果之前，不能把文件名解释为所有结果前的盲预测。新增Train比较不使用留出梯度或调参，但不是新的未查看最终测试。

最终完整/局部/动作分开评价见 [model_evaluation.json](model_evaluation.json)。新增Train没有改变新状态的原生/A/B4选择类别；两Encoder在APIFlask原本就选Sol，在Datumaro原生/A选Luna、B4预测双方通过。两个研究留出可以证实这些事前预测的对错，不能据增加Train记录称学习已经改善。

| 两个事前仓库留出 | 009 | 010 | 加入新Train的变化 |
|---|---:|---:|---|
| 原生/A正式质量动作 | 1/2 | 1/2 | 不变 |
| B4完整关系 | 1/2 | 1/2 | 不变 |
| B4正式质量动作 | 1/2 | 1/2 | 不变 |
| F2P相对轴关系 | 1/2 | 1/2 | 不变 |
| 每候选是否有F2P修复，两候选联合正确 | 1/2 | 2/2 | 不变 |
| 固定Sol正式质量动作 | 2/2 | 2/2 | 固定参考 |
| 固定Luna正式质量动作 | 0/2 | 0/2 | 固定参考 |

010的候选修复辅助目标在两个新任务联合2/2，是有限的局部目标信号；它与“完整通过关系”或“最终动作”是不同目标，不能用2/2替代B4/动作的1/2，也不是新增10条Train相对旧8条的改善。两项真实赢家均Sol，费用动作没有新可评价样本，保持不适用。没有独立双方向优势。

## 动作前表示与资源

本轮保留原6000字符状态摘要和256字符命令摘要。初始4状态8次CPU前向，CWD对齐只补3状态6次，APIFlask原捕获输入不变而复用缓存，Hikari再补2次；合计16前向、61272本地编码Token、三段含模型载入362.385秒，GPU allocated为0。最终固定参照重拟合不再次Encoder前向。原生单次CPU约18–24秒不是完整Episode成本；详见 [representation_analysis.json](representation_analysis.json)。

8次有效生成、4次502无结果，已知266225生成Token、参考费$0.2841456；3个可信候选成功、5个可信未完成，最终候选UNKNOWN为0。Optax未生成，候选真值仍未知。四次早期容器启动失败、目录评价问题及原诊断环境差异均已恢复，失败原记录保留。reasoning已计入completion，不重复相加。供应商实收、失败请求用量、部分Sol缓存、CPU/VM美元费用和完整Router资源成本未知；请求/返回API身份相符，底层物理部署未独立确认。

源码安装目录与动作CWD的对齐是真实环境/输入依据，前四状态的原生选择及关系类别没有因此改变。它不能证明状态表示使新任务性能提升。本轮没有新Context/Prepare生产修改、不重做摘要扩长。记录的源码修复机会确实存在，但摘要是否丢失关键语义、Encoder是否保留了它、当前学习函数是否能用它，仍缺独立因果依据。

## 科研判断与后续条件

新合法Train足以做规定的固定参考增量分析，尚不足以支持STEP011。已有局部信息在完整赢家中确有损失，但独立迁移收益仍未证实；新样本持续单向、P2P/回归机制稀少，数据不足有实际依据。表示及学习方法谁主导总体失败，当前不能唯一归因；不以原生训练准确率或类别增加替代新任务选择证据。

本批不自动替换Serving、不重跑旧Val、训练或Dev。新完整Dev必须由同一事前方法的独立质量与同质量费用双方向优势支持，并优于固定策略；本批条件不成立，故没有STEP011或新完整Episode。单方成功、更低失败费用或动态只用一个模型不成立。K2仍需可靠独立条件选择及包含Router开销的完整净收益两项证据；完整V9五RQ仍需整体效果、模型池、任务拆分、系统消融与工作负载适用边界的完整任务证据。

Inspect、NativeEffort与K3正式监督仍为0；原公开轨迹许可、任务分割、教师关闭与供应商实收未知继续保留。下一批完整关联范围见 [next_execution.md](next_execution.md)，不是重复本轮请求或无依据加训。

01:27:06+08:00收尾现场：用户Docker29.9.2、容器0/镜像0、HTTP/HTTPS代理为空；本批11镜像及两个服务器临时控制脚本删除，客体/宿主临时代理配置撤除，仅重启自有客体Docker。Mac本批SSH反向代理和socket控制连接已关闭，控制目录和临时上游源码移至原废纸篓，可恢复；VM磁盘/身份、服务器Encoder缓存/权重、原失败/请求/测试证据保留。原Serving healthy/PID327621，原38组队列控制器1639711、F15 worker1639726仍运行，GPU10029/49140MiB、74%；本批没有改其训练或权重。详细范围见 [cleanup.json](cleanup.json)。
