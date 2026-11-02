# V9 权重保留根因与步骤质量采集建议

从 main `db65d3476c4709cd8b43e2c31ab40c1ace3671df` 接续。本轮只做本地源码与已有真实材料分析；API、Docker 执行、服务器、训练、GPU、CPU 模型前向及 Serving 操作均为 0。源码提交为 `26321fedaa6bb970b378a029131d2f139d8cd499`，尚未部署服务器。没有新增标签或模型效果。

## 1. STEP_001 为什么丢失

| 证据时点 | 实际记录 | 能说明什么 |
|---|---|---|
| 2026-11-01 12:13:38 台北 | [原训练报告](../20261101-v9-quality-step-supervision/laya_step_training.json)的 e01 写明 `pinned_parent_for:EXPLICIT_PIN; global_best_s1_composite_score; global_best_s1_accuracy; pinned_parent_protected(EXPLICIT_PIN)`；原 manifest 写 PINNED_PARENT/loadable | 当时确有明确保留声明，不只是普通父子依赖 |
| 2026-11-02 11:05:32 台北 | [此前服务器取样](cpu_forward_measurements.json)保存非 dry-run 清理记录：`outside_new_core_pool_15pct_quota(1/2)`，删除 846196996 字节；run/epoch history 改为 weights_saved/loadable=false | 物理 e01 被额度清理删除，不是本轮 CPU 任务删除 |
| 2026-11-02 11:28:14 台北 | 同一取样确认 e01、权重和配置均缺失；未记录归档去向或发起者 | 同权重 CPU 前向无法执行，不能换 F11 冒充 |

真实实现位于 [router_data/checkpoint_retention.py](../../../../router_data/checkpoint_retention.py)。[training/common/checkpoint_retention.py](../../../code/src/modelrouter/training/common/checkpoint_retention.py)只转发到它；[旧 inventory/pruner](../../../code/src/modelrouter/training/common/checkpoint_inventory_and_pruner.py)是另一旧手动入口，没有找到原 Trainer 调用方，也不产生本次 15% 原因字段。本轮未运行任何清理入口。

现有源码可确定的丢失路径：

1. 原 `collect_pinned_parent_ids` 只读取本次 explicit_pinned、run.parent_checkpoint_id 和 plans 父关系。STEP_001 的父字段保护 F11，不保护 STEP_001 自身；原实现不读取其历史 EXPLICIT_PIN 声明。
2. 被识别的 pin 在 15% 候选池之前单独保留。未被识别时，已完成、原范围 Val 完整的每 run 最佳 epoch 可进入池；配额为 `ceil(0.15*N)`，按组大小分配席位，再在组内排序。
3. 未入席位的节点会被改为不保留，并清除此前 global-best/top-k 标记；清理入口使用本次 pinned_map，而非旧 manifest 的 PINNED_PARENT 字符串。
4. `1/2` 只表示两个候选共一个席位；没有当时完整候选列表、组分配或排序，不能声称 STEP_001 因跨组性能最差而被删除。

历史清理发起者、实际调用参数和当时服务器源码版本没有保存，本轮也未访问服务器。因此“哪一个进程没有传 pin”仍未知；确定的问题是当前实现会丢失已经写入训练历史的明确保留声明。不能只根据两时点状态不同认定错误。

### 原位改动

- `collect_pinned_parent_ids` 读取 history.retention_reason 中明确的 EXPLICIT_PIN，继续使用原 pinned_map；普通 PINNED_PARENT/父子依赖仍从当前关系生成，不把所有历史状态永久保留。
- `two_phase_cleanup` 实际删除后调用原 `write_checkpoint_manifest`。原入口只更新 run/epoch_metrics/audit，直接调用时会留下旧 manifest；这与“两个记录时点不同”是两个问题。
- `finalize_run_checkpoints` 在清理已写 manifest 时不重复写；无删除时仍写完成状态。没有改变 15% 配额、组内评分、共享资源规则或增加第二套清理系统。

用原 STEP 训练报告、无 explicit_pinned 参数调用原函数，结果 STEP_001-e01 仍为 EXPLICIT_PIN，F11-e01 仍由 STEP_001 的父关系保留。文件语法有效；未构造假权重或执行删除。仅写在 Markdown 的研究选择并不会自动成为 pin，仍需原训练元数据中的明确声明或实际依赖。

### 能否恢复

限定读取本机已有 runs、.runtime 和 STEP 结果目录后，只找到训练配置、指标与实验记录，没有精确 e01 权重副本线索；已有清理记录也没有归档路径。当前不能恢复，但不能排除未获授权范围外的副本。物理权重已删除时，保留逻辑改动不会把它重新生成。没有重训、下载、替换版本或修改历史训练指标；源码同步到 GitHub 不等于服务器已应用。

## 2. 六组比较为什么没有新标签

[已完成的六组结果](quality_prefix_execution.md)全部在一步后未通过原范围验证；12 次生成、13 条模型工具命令、12 次原验证与 0.13404708 USD 费率估算保留，不重跑。

原 [real_supervision.py](../../../code/src/modelrouter/v9/training/real_supervision.py)要求至少一个候选在该步后通过原任务验证；两者均通过才比较费用。读取、复现、解释或提出尚未执行的修复都不能满足该目标。上轮 SQLparse/Records 等实际继续读取或复现，OAuth 缺 rg、Autograd Luna 缺 apply_patch；这几项工具问题是真实观察，但不能据此解释全部失败。

主要测量限制是“一步贡献”和“整项测试已通过”之间的距离：inspect 通常只取得信息，modify 可能还需要后续动作；全范围二值结果对这些进展不敏感。较晚 verify 状态已有具体错误与修复范围，因而此前能产生质量偏好。当前19条仍为任务9/步骤10；步骤质量Sol4/Luna4、等质量费用Luna2，verify9/recover1，inspect/modify0。本轮不改 `STEP_LEVEL_PREFERENCE` 或 `prepare_comparison`，不把双失败改成赢家。

## 3. 路线 A：两份未比较的较晚 Train 前缀

两项均来自已有 TRA-002 / SWE-bench/SWE-smith / train、两个任务、两个仓库，新增来源任务为 0。沿用原 [task_isolation.json](../20261101-v9-overnight-real-supervision/task_isolation.json)：Canary/Dev/Final 精确 ID、可识别仓库/镜像及 TwinRouterBench 交集为 0，不声称所有语义派生题都已排除。

| 候选 | 精确任务与截止 | 当前真实可见信息 | 原范围与测量价值 |
|---|---|---|---|
| A1 Records | `kennethreitz__records.5941ab27.lm_rewrite__letryq82`；`t18-records-sol-low / 4`；verify | 已读取 query/连接路径并执行真实复现和原 suite；出现 ResourceClosedError、参数绑定异常；1 failed/23 passed/7 errors。此前只写 /tmp 复现文件，没有修改源码或测试 | 原 FAIL_TO_PASS 1、PASS_TO_PASS 23，共24项；测量一步能否修复原失败且保留23项。额外7个全 suite errors 不并入原24项，也不隐藏 |
| A2 async-timeout | `aio-libs__async-timeout.d0baa9f1.lm_rewrite__kqd6t1mb`；`t15-async-timeout-sol-low / 5`；verify | 已复现 EXIT/TIMEOUT 生命周期错误并运行测试，3 failed/29 passed/2 skipped；已看到具体错误消息和状态转换，尚未修改源码或原测试 | 原 FAIL_TO_PASS 3、PASS_TO_PASS 29，共32项；测量一步是否修复三个既有异常且不新增回归。额外两个 skip 不当通过项 |

### 精确来源，不复制轨迹或题目解答

| 候选 | 截止消息与真实状态 | 环境、任务及原命令 |
|---|---|---|
| A1 | [trajectory](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/mini-swe-agent.trajectory.json) `messages[0:10]`，4条assistant/4条工具反馈；[events](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/events.jsonl)第18行 | [task_source](../20261101-v9-overnight-real-supervision/t18-records/task_source.json)、[environment](../20261101-v9-overnight-real-supervision/t18-records/environment.json)、[run_config.verify_command](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/run_config.json) |
| A2 | [trajectory](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/mini-swe-agent.trajectory.json) `messages[0:12]`，5条assistant/5条工具反馈；[events](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/events.jsonl)第22行 | [task_source](../20261101-v9-overnight-real-supervision/t15-async-timeout/task_source.json)、[environment](../20261101-v9-overnight-real-supervision/t15-async-timeout/environment.json)、[run_config.verify_command](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/run_config.json) |

两份完整 observed_messages 与原10条步骤材料、已有质量比较、上轮六对及任务内比较按结构比较，均无同前缀记录。Records旧比较为cutoff3/6，async-timeout为cutoff2/6，不能把同任务的新前缀计作新任务。SQLparse cutoff5已有一次失败比较，已剔除。Records原step5包含输出额度中断，和已完成assistant数不同，因此使用无计数歧义的step4，不把中断当第五次完成动作。

原 `prepare.build_offline_prefix_input` 与真实 AgentState 恢复两份截止历史：消息10/12、生成4/5、工具4/5、末次退出码0/1，均与原状态对应；教师为null，能力快照为 `20261031T072548885180Z-v4`。Records最后组合命令的退出码0来自最后的输出命令，不代表内含pytest通过。

两项只是 UNLABELED / 可以恢复并验证的候选对，没有执行新比较或产生赢家。源码修复后的一步仍可能用于继续读取或添加测试；尤其 async-timeout 的原后续动作只加测试，不能把历史成功当作下一步修复保证。当前缺少可信、未比较且具有一步验证区分能力的 inspect 前缀，未凑数量。

## 4. 路线 B：短期质量进展，仅为推荐研究选择

| 观察类型 | 可测量内容 | 与现有19条的关系 |
|---|---|---|
| 完整任务成功 | 可信完整Episode及原Verifier | 任务级目标，不能复制给每步 |
| 一步完整修复 | 一步后原范围全部通过 | 沿现有步骤质量/等质量费用条件 |
| 部分测试改善 | 固定测试ID的before/after状态、真实修复项及新增回归 | 单独质量进展证据，尚无批准的训练目标 |
| 读取、定位、口头解释 | 原命令、反馈与可见信息 | 仅观察/辅助状态，不产生质量赢家 |
| 费用 | 两候选同等可信质量下的实际模型费率 | 原标签仍要求两方通过，不把双失败费用当质量 |
| 未知或不可比较 | API/身份/环境异常、缺验证、不同测试范围 | 保留观察 |

可实施的最小方向是固定原 FAIL_TO_PASS 与 PASS_TO_PASS 的测试ID，记录每项 pass/fail/error/skip/unknown。比较具体修复集合与回归集合，不按通过总数排序；不同测试的重要性不假定相同。若一个候选修复集合严格包含另一个且没有新增回归，可作为部分改善研究证据；集合交叉、失败转成skip、出现新回归或缺单项状态时，不能自动选赢家。原命令没有给出单项状态时保留UNKNOWN，不安装新报告依赖或更换验证器。

固定后续多步范围可以测量信息获取的延迟贡献，但需要相同后续策略/资源，增加调用与混杂因素；本轮不实施。旧六对只有失败结果与汇总计数，不能补成部分改善赢家。路线B若获批准，需要与现有二值步骤目标明确分开进入Trainer，不改变旧19条的身份和含义；五RQ结构不变。

| 路线 | 真实性与实现 | 获取效率和结论范围 |
|---|---|---|
| A：一步原验证 | 已有标签条件，环境/验证/费用链可复用；与旧19条同目标 | 少量较晚状态可能直接区分修复；仍偏verify，不解决inspect信息价值 |
| B：固定范围质量进展 | 需单项前后真实证据，研究定义与训练目标待负责人决定 | 可观察部分modify贡献；读取步骤通常仍无即时差异，不能据此声称完整任务收益 |

**明确推荐：先做路线A的两前缀、最多4次生成，保持现有目标；同次运行保存原验证的细粒度观察供路线B研究，不生成B标签。** 这比再跑六份早期状态更接近可测量修复，也避免立即改变方法。若两组仍无法区分质量，先由负责人决定是否采用独立质量进展目标，再开展收费采集；不继续堆积同类双失败或只为费用偏好训练。

## 5. 工具环境提示的来源与当前状态

本机已有 mini-SWE-agent 2.4.6 的 `environments/docker.py:get_template_vars` 合并 `platform.uname()._asdict()`，读取的是Mac宿主。原DefaultAgent把这些变量渲染进instance_template，因此直接Docker采集历史含Darwin和Mac专用 `sed -i ''` 示例；实际命令仍在Docker /testbed运行。这是提示与工具环境不一致，不代表工具在Mac执行。

当前正式 [Harbor入口](../../../code/src/modelrouter/benchmark/harbor_agent.py)已由 `environment.exec` 执行 `uname -s && uname -r && uname -v && uname -m`，HarborEnvironment返回实际system_info；保存的build-pmars setup也确为Linux/x86_64。本轮不重复修改这个正确入口，不改上游安装目录或建立新Docker封装。

原 `real_supervision.py`、`prepare.py`负责监督准备，不是第二个Agent执行循环；此前直接Docker采集的临时驱动已删除。未来沿原DefaultAgent的extra_template_vars提供实际容器变量，只影响新渲染的消息，不能让已保存的Darwin文字自动消失。恢复历史消息时保留原文件，两个候选可共同追加一条实际容器事实说明并保存新请求的完整消息；说明只描述环境，不改变任务计划或替模型指定工具动作。该共同说明之后才是本轮候选对的完整比较前缀。

rg/apply_patch在原镜像中缺失的反馈仍保留；不安装工具、修改Verifier或单独给某模型额外工具。当前Harbor bash工具接口、模型调用入口与原行动Prompt均未修改；提示问题的影响大小仍未知。

## 6. 下一轮范围与本轮结束状态

可直接使用 [next_execution.md的当前提示词](next_execution.md)。下一轮推荐资源：本机已有Docker/基础镜像、真实Sol low与Luna low，2前缀×2候选=最多4次一步生成、4个隔离分支；每前缀一次原范围前值加两次分支原验证，共6次原验证。教师关闭，不占GPU、不依赖服务器或权重、不启动Episode、不接触Dev/Final答案。镜像或既有资产缺失时记录具体缺项，不自动下载、安装或重建。

本轮新增有效监督0、新训练0；原19条、74行和215/186可组合视图不变。F11-e01/R11继续作为研究接续代表，STEP_001仅保留历史结果且实体不可用。F14/Serving没有刷新，最后服务器事实仍为11:28:14台北的F14独立维护Epoch2第7/420块与F05-e01/原Kev Serving；不写成当前在线状态。CPU0/12、encoder/head比例及inference_mode收益仍未知。

只新增这份研究说明并更新原next_execution、summary、Status/Memory/QA/训练报告；Research Overview没有方法获批变化，保持不动。本轮没有权重、镜像、备份或临时构建产物需要清理；原实验、失败、用户Trainer/tests/私人内容、原删除、Fig.2与handoff均保留。
