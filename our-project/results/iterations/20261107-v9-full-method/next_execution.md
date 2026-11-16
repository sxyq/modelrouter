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

按负责人最新要求，先执行[Model-only配置](../../../experiments/configs/v9_model_only.json)：全部89题×24组×seed43，Laya/Kev原始及11-11各18更新实体、教师OFF/ON、固定Low/High/Max。每次仅在三个同档模型中选择，沿原Harbor/DefaultAgent及原Verifier，所有任务保持已观察身份，不作新训练或选权重。当前与终局数量、有效评分、依赖失败、模型/教师及Router Token沿[本批结果](../../benchmark/rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)读取，不使用入口旧快照。

旧54位置seed43联合选择结果已与openssl-selfsigned-cert/regex-log逐题配对；原分析器同时纳入同档位Model-only训练/教师及固定模型对照，实际评分和费用齐全的task/seed分别登记。其余87题相同权重/seed的八个联合主组696位置和三固定模型参照261位置，共957，已按[联合接续配置](../../../experiments/configs/v9_joint_paired.json)排在当前矩阵和已处理网络失败的一次恢复之后；新配置直接读取Model-only保存的AA快照，保持Encoder、教师、Harbor、Verifier、输出及任务时限。旧89题seed42训练版为11-08实体，保留其历史身份；不重复首两题和旧批次。

2026-11-16沿固定脚本our-project/code/cli/run_rq1_a6000.py及原rq1入口接续：11:22:56原联合固定261位置全部结束，闲置3205488／3575811退出；六项既定固定技术恢复于12:00:58结束。3993622持有原私有描述符并等待实际Model-only1696641结束，再执行Model-only技术恢复、696联合Router、联合与历史必要恢复；有效官方1/0直接保留。观察123359／123360／123364每1200秒复用原.runtime导出，代理98294跟随1696641／3993622，原共享GPU锁保持。四权重、11-11各18更新、AA v7、模型/档位/4096/Seed及原时限保持；所有模型及教师请求最多额外100次，长度耗尽不网络重试，Reasoning/缓存各计一次。

现行观察123359／123360／123364只跟随原Controller与有限接续，每20分钟复用原.runtime导出目录，已加载分析c6b2a7b1；旧闲置4041864／4041865／4041866退出。02:22代理98294在76902自然结束后接管；原首失败、费用、有效1/0和权重保留。gpu.lock共享READ与训练及Breeze独占锁保持。需要等待使用纯20分钟wait，期间不重复读取未变状态。

16:09 Model-only／13:39—13:46联合与历史原Model-only1195/2136结束，287有效1／160有效0／716缺分／32依赖故障，2运行、939未开始；联合固定261/957结束，84有效1／55有效0／122缺分、696原Router位置尚未开始。历史2599 Trial、308有效1／344有效0／795缺分／66依赖故障，累计266恢复涉及196位置，原2333首次Trial保留。新增CLI/Terra官方1与Pipeline/Terra官方0均来自独立完整恢复；Query九次正常生成后Verifier900秒仍无分，保留未知。第4个GLM Low请求4096返回128000的额度终止已入原Verifier，原0与费用保留、不重跑；正常请求额度内length终局仍待原矩阵自然出现。Luna401现行/实际绑定相同且同模型备用0；其认证问题与旧额度403分列，保持完整原条件和既定队列。

03:31共享GPU可用47444MiB，H3后端stopped、活动请求0；11条路由返回前超时、2条CUDA OOM及338条连接拒绝／14条SSL EOF沿原3993622技术恢复，保持同任务、策略与seed43、首次日志及费用。新raman-fitting训练Kev ON Low获官方1、3断言全过、实际GPU等待0.023336秒；两次教师403且短评消费0，教师生效集合需按实际短评使用单列。当前原固定段未结束，后续696个联合Router位置仍待原顺序接续。

gcode-to-text终局：训练Kev Model-only OFF/High实际执行2条断言、1通过/1失败，完整任务Reward0；1064.319秒、26生成/26工具结果、模型参考费$0.15098180且缺费用0，请求/返回均Terra High。Low的原0来自Debian下载502、uvx未安装，未执行断言；783.051秒、20生成/20工具及$0.07798260保留，任务质量另列。原始Kev ON的Luna High/Max前序工具有效、终局INCOMPLETE_RESPONSE且缺Reward。联合接续同时补三固定参照GLM Low/Luna High/Terra High的87题×3=261位置，联合主组696，合计957；旧两题seed43结果复用，旧seed42不替代。

## 后续一：补任务开始、转折与恢复状态（RQ4，关联RQ2）

本轮只完成现有2136位置、957位置及历史必要技术恢复，保留11-11各18更新代表，不重新训练或选权重。下列监督增量与Trainer更新属于后续科研阶段。

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
| RQ1 | 完成现有全量矩阵及必要技术恢复，取得跨机制成对结果、完整实收与Router/工具/CPU/GPU/VM费用；当前数量读取各批正式报告，首次缺分事实保留 |
| RQ2 | 精确模型与请求档位的同题质量/费用、实际返回及缓存；GLM Low/High精确AA与渠道档位确认缺项 |
| RQ3 | 已运行开始/阶段/逐生成；补真实子任务边界与跨机制重复，实际教师调用变化分列 |
| RQ4 | 已运行训练/教师/T/M/H；补非验证阶段合法监督及可重复的条件选择收益 |
| RQ5 | 事前独立工作负载、同配置重复及有收益/无收益/无法定价区域 |

AA v7固定快照20261107T134704898459Z-v7、130真实指标、Intelligence Index5.0.1：Luna/Terra各六档，GLM仅Max，Low/High缺测。授权完整API数据尚缺；沿原TTL/force/STALE更新，在每批开始取得快照，同批固定版本，不逐生成联网。

实际缓存读取、前缀重用估计、端点切换与物理KV共享分别记录。供应商逐请求实收、Router及工具/资源单价缺失时保持UNKNOWN；缓存折扣与Reasoning各计一次。训练成本单列，在线费用及并发资源分摊采用同一可知口径。

## 连续执行与资源

23:11:54同一VM已切换KVM，QEMU3832028及监控确认kvm support: enabled；原16CPU／40960MiB、200GiB磁盘、101镜像、9p共享目录保持。此前六个Episode自然结束、容器0后才关闭原TCG VM；原Controller1696641／3205488已恢复，GPU锁及Native worker3708428保持。使用原私有维护记录中的已有sudo凭据开放syy的/dev/kvm读写ACL，实际API版本12；start.sh.previous为此前启动版本，当前唯一源码回退包为8db统计变更前的1d645126四源码。后续Episode由原Agent日志记录真实QEMU身份；query-optimize原始Kev High／Max在KVM下仍首项900秒超时，6包安装1.00／1.36秒，两条因Luna额度故障未执行工具、没有Reward，SQL等待仍待定位。新Kev High真实CUDA/fallback=false、19.102秒，选Luna High后接口故障与路由前向分别保存。

当前e05caa115ed00e68ba26abf9aed72847440b4fde在原GPU共享读锁内按模型实际张量字节等待显存，保留Router原时限；四原权重CPU预加载后再接受任务。Worker3708428／有限持有3708420已接同一入口，旧闲置2496626／2496618退出，实际Laya CUDA/fallback=false日志已取得。qemu-startup训练Kev教师ON High／Max两条CUDA OOM由原技术恢复入口接续，原记录及费用独立保留；有效1/0不重复。

当前Agent8db98d081d186a216b8772f3a22a6d7645ed23e3保留Harbor预算类别并调用原Verifier；分析c6b2a7b1c30dc1295c01640b47cd6d657f52f9d3已从三个超额输出完整Episode验证该调用，渠道4096执行问题仍未解决。403等技术故障继续独立，正常请求额度内length仍待原矩阵；有效1/0不重复，旧NonZero缺有效分沿原恢复入口。唯一源码回退保存Agent8db与分析e1四源码。

Luna已记录额度403与SQLite教师五次401 invalid token，现行唯一绑定与原Model-only／有限持有配置一致；401请求0重试、0短评消费，不将教师ON配置直接归为实际干预。Terra High在新Windows与regex-chess完整Episode恢复正常生成，分别官方0／1，前者44次、后者6次HTTP200且档位一致。此前502位置沿原恢复范围，已评分1/0保留；MTEB-leaderboard五固定组、MTEB-retrieve三有效失败组也直接复用，Low／High依赖故障使用原缓存恢复。原Harbor错误政策、评分及失败记录保持。

新Tensor完整Episode的31包安装17.91秒后进入13项官方测试，900秒Verifier仍无终局；该次14生成请求、151644 API Token和$0.06207760参考费另记，不把3次累计用量称为一次运行。宿主机/dev/kvm存在、syy无读写权限、sudo需密码，硬件加速需要管理员设备授权；原QEMU2744271仍为q35,accel=tcg、16核40GiB，现有健康实验继续原配置。CPU等待与生成代码的贡献保持未知，不修改官方测试或时限。

复用原modelrouter.benchmark rq1入口和配置批量运行；固定任务四并发、Router两并发，原任务时限、4096输出及官方Verifier。需要等待时沿原--watch-pids <实际父PID> --watch-interval 1200每20分钟汇总，父进程退出后取末次结果并结束，不建立新的Runner或定时服务。

2026-11-12 02:32台北历史快照：F15物理epoch_01/61180、3915484条，模型842609220字节、优化器3368412933字节，无F15进程；Serving PID327621为原F05/导入Kev。该快照GPU989/49140MiB、0%，用户VM16核40GiB、任务容器0，前一批临时代理及Socket已撤去。当前批次代理、Router与容器状态见上文及[现行资源记录](../../benchmark/rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)，不沿旧快照推断训练或任务状态。

唯一私人配置沿SSH输入/memfd读取，原权重、私有请求、轨迹与结果保护。公开源码、脱敏结果和实质规划分批提交推送；结束后清理本批临时对象并报告完整main SHA。最终按整体目标、真实进度、五RQ缺项、前三任务、真实结果、独立判断、通俗解释、下一关联工作包八部分汇报。
