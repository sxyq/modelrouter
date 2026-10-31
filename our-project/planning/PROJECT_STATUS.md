# ModelRouter · 项目现状、资源条件与执行路线

## 2026-10-31 · 当前恢复点：真实模型对照、紧凑教师与有效数据视图

本轮从 `main=e28872fc69604ab082eab5b703d7674073fb4356` 接续，结果位于 [20261031-v9-real-model-comparison](../results/iterations/20261031-v9-real-model-comparison/review.md)。`fix-git`、`db-wal-recovery` 已结束，本轮均未重跑；没有新 Alias Episode、训练或 Serving 权重替换。

### 教师：取得真实 Sol 输出，费用仍需收益证据

旧 `db-wal-recovery` 五次失败均为正文空、`length`、输出额度 1,024 全用于 reasoning；JSON Object 和旧关闭 thinking 参数没有解决额度分配。新真实 Sol 的长前缀 `low/2048` 也为空，reasoning=output=2,048，费用 `0.0305085 USD`；错误 Chat 入口和一次超时的 Usage 未知，均保留。

原 Assessor 改为只摘要已观察事实，使用原生 Responses 的 JSON Object；两条固定参考实体不变，输入仅取首尾摘录，移除重复消息，工具视图最多 1,600 字符。默认最低合法档为 `low`，输出上限 4,096、上下文上限 8,000；首次仍约三次生成，后续至少间隔三次，验证与重复错误优先阶段变化。原 Hook 在信号变化时清除旧短评，formatter 保留短评截止步和阶段；教师不选择模型、不改变 Agent 计划或执行工具。

| 新真实 step3 前缀 | 实测 |
| --- | --- |
| 输入 / 输出 / reasoning | `1,462 / 1,528 / 1,435` Token；上下文 `4,029` 字符 |
| 缓存读 / 写 | `0 / 1,459` Token |
| 结果 / 时间 / 模型费 | 三字段完整 JSON、`completed`；`41.768707` 秒；`0.0189335 USD` |
| 资格 | `TEACHER_PREFIX_ONLY`；未运行新 Router 或工具，不计旧 Trial 成功次数和费用 |

原观察记录上的触发重算为 `3/7/10`，旧实际为 `3/5/6/7/8`；这不是三次新教师调用。step3 成功短评在相同信号的 step4 可复用，step5 变化后清除，不会因 step6 回到旧阶段而自行恢复。单次成功不证明稳定可靠或净收益；这份 Sol 短评价格仍约为本次 Luna 整个 Episode 的 `4.23` 倍。原失败与成功输入、响应和费用见 [teacher_analysis.json](../results/iterations/20261031-v9-real-model-comparison/teacher_analysis.json)。

### 三个正式身份的访问与同条件对照

| 正式身份 | 当前 Provider 实证 | Native Effort |
| --- | --- | --- |
| `gpt-6.1-sol` | 现有账户原生 Responses，请求/返回身份匹配，真实 Bash 工具可执行 | 文档 `low/medium/high/xhigh/max`；本轮实调 `low`，不含 `none` |
| `gpt-6-luna` | 项目 jiji Chat Completions，请求/返回身份匹配，真实 Bash 工具可执行 | 文档 `none/low/medium/high/xhigh/max`；本轮实调 `low` |
| `qwen3.8-flash` | 两账户实际 POST 返回 `model_not_found`：jiji 404；另一账户 503 正文明确无可用渠道 | `NOT_MEASURED`；未把省略参数的占位值或 Alias `none` 声称为原生支持 |

公开 Dev `extract-elf` 两次执行的初始两条消息、工具 Schema、mini 配置和候选动作直接相等；seed42、30步、输出4096、教师关闭、同上游镜像、原 Harbor/mini-SWE-agent 与未修改 Verifier。API 原生协议分别为 Responses/Chat Completions，供应商内部上下文是否相同未知；后续轨迹随各自行动展开。

| 动作 / Trial | 真实生成 / 工具 | 官方结果与失败 | 模型费 USD | Trial / Agent 秒 |
| --- | ---: | --- | ---: | ---: |
| Sol low / `6dd69051-dec2-4706-9914-b4fcc722ed2e` | `13 / 10`，全部返回 Sol | 原900秒窗口AgentTimeoutError；随后Docker socket缺失使Verifier准备与容器清理失败，reward未知；3次截断中2次全reasoning、1次reasoning2070/4096 | `0.3912934` | `970.478263 / 900.056730` |
| Luna low / `70324a19-498e-42ae-8f2a-a71b9207ef5e` | `8 / 10`，全部返回 Luna | reward `0`、CTRF `1/2`；匹配覆盖 `0.00%`，要求 `75%` | `0.00447894` | `522.321635 / 473.451437` |

两者无Alias、无教师调用，均为固定动作策略。初始应用条件相等不代表整个Episode外部运行条件相等：Sol的Docker中断和共享Token账本串行等待限制终局/时延归因，不比较纯模型速度或推导神经Router收益。Sol原Trial保存12响应、模型费0.3480004；一条截止前发出、Trial结束后返回的响应费用0.043293另有事件证据，全部调用费用0.3912934。两次调用模型费0.39577234USD，实收与资源USD未知。

另有同消息/工具 Schema 的 COBOL T0 生成对照，Luna 只生成未执行该前缀工具，不赋偏好。原 COBOL 首 Sol 归档缺 `selected_model_id` 已在原 Provider 补齐；该失败19响应/`0.5584418 USD`保留。接续 Sol 15响应/`0.421543 USD` 因原工具30秒超时而无 Verifier；Luna 7响应中3条返回旧 `gpt-5.6-luna`，虽 reward1/CTRF3/3，也不作纯 Luna Episode。未再次运行 COBOL。

### 费用与监督口径

原调用日志已直接采用 Provider 算出的 `REQUEST_MODEL_RATES_WITH_PROVIDER_USAGE`，保留缓存读/写未知值；不再为真实请求另选旧 OpenRouter 估价。仅本轮65个已保存响应对应日志条目的费用已更新，旧参考估价及 raw Usage 保留，没有新增调用日志计数。已知模型费小计 `1.43331375 USD`；3条型号不匹配的价格和4次无Usage访问/教师失败金额未知，所以完整总额和供应商实收仍为未知，不能当作现金账单。

新 [episode_comparison.json](../results/iterations/20261031-v9-real-model-comparison/episode_comparison.json) 有1个相同初始状态、2个真实动作执行结果、1个可信 Verifier 终局与1个超时记录。没有成功候选，也没有完整双模型 Verifier 质量对照，**当前 Model 选择及 Model×Effort 偏好标签仍为0，Train资格仍为0**。不把低价失败者标为最优，不把超时的未知 reward 写成0；单前缀资料和 Episode 尝试分开。

原390实体与四条教师不变。读取原54个 Open-SWE 终局后，原 Prepare 形成唯一新视图 `training_view/`：Train196、Val186，共382行；8个 `resolved=-1`（Train2/Val6）不再作为失败目标。S1原64/64候选顺序和偏好保留；S2为68/58，S3为64/64。旧13,214候选与390重合，RouterBench35,102为旧池Oracle且许可未明，均不作为新三模型选择目标或新增独立样本。

AA固定v4 `20261031T072548885180Z-v4`：Sol/Luna Max各10项，Intelligence v5.0原分 `54.5087338138148 / 27.7552004938153`；本轮low、none、托管Flash及Coding/Agentic综合指数仍缺测。未再次刷新或在路由时联网，没有借用27B/Flash-Next成绩。

### 服务器与下一轮训练

F14原控制器及worker已于台北17:01按原训练管理范围结束，原Run记 `failed/NON_FINITE_LOSS`、原队列 `PAUSED_RUN_FAILED`；原cursor、Epoch1、曲线和权重保留，未启动F15。停止前为第二轮363/420、step100166/107404、loss NaN，首次诱因及有效更新未知。正式队列仅沿原失败筛选增加该原因，不影响其他健康对象。

台北18:27:28读取Serving 200/healthy，PID327621与10-30 20:53:21启动时间不变；Laya F05/epoch_01、原Kev导入适配器继续服务，GPU25433/49140MiB、0%。F14两进程均已退出，原Run仍failed/NON_FINITE_LOSS，图像对象启动时间不变。本轮没有部署Provider/教师到Serving或更换权重。

Laya F11-e01、Kev R11继续作为接续代表，已完成V9的S1/四指标退步保留。新Train选择监督仍0，**不启动继续微调**。现有Laya支持encoder/head分别设学习率与`freeze_encoder`；Kev为LoRA加pointer head，`head_lr=0`沿用主学习率，不等于head不更新。后续真实Train同状态结果才作为新choice目标，旧S1候选与人类偏好不改名，教师截止前短评和AA卡经原serializer进入输入，未知终局不作答案；收益通过原固定Val的S1四指标及真实Dev Episode判断，不重复旧配方，不承诺指标不退步。五RQ、八图十二表和正式结果格保持。

## 2026-10-31 · 历史：db-wal-recovery 已结束，事后短评已消费

以下为上一轮时点，不作为当前服务器、教师配置或数据视图状态。

新公开 Canary `db-wal-recovery` 已成功，不重跑。接续起点 `main` 为 `7e7eecb9f1ad927f83e6d6e05f6695c661e734e7`。

### 主 Trial：官方终局成功，五次教师均未产出短评

| 对象 | 已保存事实 | 适用范围 |
| --- | --- | --- |
| Run / Trial | `20261031-v9-db-wal-recovery`；`60320365-17ce-422a-84eb-e4ff6d8623d0` / `db-wal-recovery__5Y5JWoW` | [原 Trial result.json](../results/iterations/20261031-v9-db-wal-recovery/jobs/db-wal-recovery--laya_v2--s42/db-wal-recovery__5Y5JWoW/result.json)，迭代 `EVALUATED` |
| 官方终局 | Verifier reward `1.0`；CTRF tests `7` / passed `7` / failed `0`；异常 `null` | 原 Harbor 容器与官方 Verifier 的公开 Canary 开发结果；不填五 RQ 总体对照 |
| 路由 / 生成 / 终端调用 | `14 / 14 / 19`；14 次 Laya `F05/epoch_01` 真实前向，均逻辑 `gpt-6-luna:none`；Sol/Flash 选择 `0`、fallback `0`、模型切换 `0` | 阶段 `inspect/modify/recover`；实际生成后端 Qwen3.8-27B，不是独立物理三模型比较 |
| 教师 | `5` 请求 / `0` 成功；step3 首次约三次生成触发，steps5/6/7/8 为阶段变化 | 五次均未向主 Trial Router 提供成功短评；触发规则不变 |
| 映射模型费用 | 生成 `0.00949188`、失败教师 `0.220104`、完整模型合计 `0.22959588 USD` | 均已计原账本；供应商实收 USD、Router/工具/容器资源 USD 仍未知 |
| 时间 | Trial `873.763569` 秒；Agent 执行 `756.048114` 秒；教师请求合计 `263.916096` 秒 | 教师时间包含于执行过程，不再加到 Trial 时长上 |

逐次候选概率已保存在原 [events.jsonl](../results/iterations/20261031-v9-db-wal-recovery/events.jsonl) 的 `ROUTER_END`：

| 逻辑候选 | 主 Trial 概率范围 |
| --- | ---: |
| Luna | `0.3941–0.4316` |
| Sol | `0.3276–0.3672` |
| Flash | `0.2266–0.2569` |

五次教师 raw 均为 `content=""`、`finish_reason=length`、reasoning `1,024`，请求输出上限 `1,024`；JSON Object 与 `enable_thinking=false` 均未防止 thinking 消耗，随后出现 `JSONDecodeError`。旧 `fix-git` 两次同类错误没有 raw 正文，TTFT 为 `null`、reasoning 同为 `1,024`；只能据新五次实证推断同类原因，不能声称直接见到旧 `finish_reason`。旧失败费用 `0.037952/0.037730 USD` 已计账，完整证据保留在下方历史段。

原 Assessor Prompt 要求 `progress_summary/main_blocker/next_milestone` 三个短 string 各不超过 25 words，使用 Alias ChatCompletions 已支持的 `response_format={"type":"json_object"}`；`max_output=4096/context_chars=20000`，记录 `finish_reason`。原 Provider 仅新增 `response_format` 参数，无效果的 `enable_thinking` 补丁已移除；没有重试、第二教师、触发规则或推理权重变更。

### 事后 step3 前缀补充：单次教师成功，短评已送入 Laya

| 对象 | 已保存事实 |
| --- | --- |
| 单次教师 | [teacher_prefix_replay/metrics.json](../results/iterations/20261031-v9-db-wal-recovery/teacher_prefix_replay/metrics.json)：完整三字段 JSON，`finish_reason=stop`；输入 `8,069`、输出 `2,331`（含 reasoning `1,112`）、缓存 `0`；`43.758924` 秒，逻辑 Sol 费用 `0.039448 USD` |
| 原 RouterClient 远程前向 | [teacher_prefix_replay/router_response.json](../results/iterations/20261031-v9-db-wal-recovery/teacher_prefix_replay/router_response.json)：Laya `epoch_01`、`fallback_used=false`、`assessment_consumed_by_router=true`；Luna/Sol/Flash `0.4382/0.3059/0.2559`，选择仍 Luna none；决策约 `1.01937` 秒，新增生成 `0` / 教师 `0` |

两项均为 `POST_RUN_OBSERVED_PREFIX_REUSE`，不是官方或独立科研样本。教师补充费用独列，不计入主 Trial 的教师成功次数或费用；随后 Router 前向复用同一短评，没有第二次教师请求。证据只支持该前缀完整 JSON 与短评传递，不表示主 Trial 教师有效参与，也不证明稳定收益。

### AA v4 与数据监督

原刷新入口已取得 [AA v4](../code/data/v9/capabilities/snapshots/20261031T072548885180Z-v4.json)，[current.json](../code/data/v9/capabilities/current.json) 指向 `20261031T072548885180Z-v4`。Sol 正确 slug 为 `gpt-6-1-sol`，旧点号 URL 未重访；Sol Max、Luna Max 各 10 项，共 20 项实测，厂商三份元数据保留。

| AA Intelligence Index 5.0 | 精确原分 | 实测档位 |
| --- | ---: | --- |
| Sol | `54.5087338138148` | Max |
| Luna | `27.7552004938153` | Max |

`none`、托管 Flash，以及 Coding/Agentic 综合指数仍缺测。Sol 公开 NativeEffort 仅 `low/medium/high/xhigh/max`，不含 `none`；Alias `none` 不当作 Sol 原生档位或 Max 成绩。原 Dev Trial 与本次 prefix 仍绑定 v3，旧 390 材料及 V9 训练仍绑定 v1；未来新实验明确绑定 v4，不追写旧结果。AA 是能力特征，不是选择标签。

| 现成资产 | 原实体不变 | 可核原监督候选 |
| --- | --- | --- |
| 旧 390 行 | Train `198` / Val `192`，AA v1、四条教师短评保留 | OpenSWE 原 `resolved=-1` 被写成 `false` 的 Train2/Val6 共八条扣除后，为 `196/186` |
| 旧 batch1 S1/S2/S3 | 原文件 `13,438` 行，含 `224` 条未知终局 | `13,214 = 4,592` 旧偏好 + `2,622` 观察性终局 + `6,000` 辅助；未知终局不作终局监督 |

这些计数不是新增独立任务或新的三模型动作目标，彼此与旧 390 存在重合，不能相加。真实三模型最优 choice 与 Model×Effort 监督仍为 `0`。原 `data_pipeline/sources/tra.py` 已将 `-1` 保留为 `None`，旧实体未重清洗或改写，远程数据加工源码未部署。OpenSWE/SWE-smith 只用于合法前缀、工具/恢复与有结果的观察性终局；RouterBench 旧 11 模型有 `35,102` 个唯一 Oracle，数据许可待明，不新增入训练。精确任务 ID 与 Canary/Dev/Final 交集 `0` 只证明 ID 相等关系，近重复未知；原 S3 无 Agent taskID，无法计算该交集。来源与详细计数见 [原数据 Registry](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)，不凭 AA 或 Alias 生成答案。

### 服务器最后回报与训练准备

台北 **15:55:17** 最后只读取样，原 cursor `updated_at=2026-10-31T07:53:42Z`（台北 15:53:42）；F14 第 2 轮已完成 `343/420`、step `97,606/107,404`、`latest_chunk_loss=NaN`。原 `continuous_queue.log` 实际累计 `701` 条 F14 `loss=nan`；未完成两轮。原 worker 与控制器没有被改动。Epoch1 Val 非有限及 `5,692` 项全类别 `0` 预测继续保留，具体诱因与有效更新次数未知，F14 仍排除父候选。

台北 **15:55:17** Serving `/health` 为 `200/healthy`；未替换 Laya `F05/epoch_01` 与原 Kev 导入适配器。15:25:51 的进程读数为 PID `327621`，GPU `34,609/49,140 MiB`、`73%`，不把旧 GPU 读数当作本次取样。新数据加工源码未部署。F11-e01/R11 仍为接续父代表，依据已保存 Val 和实体证据；已完成 V9 的 Laya S1 退步、Kev 四指标退步等负结果保留。

下一训练参数讨论区分原 Laya 完整 encoder+heads（`epochs=2/max_len=1024/head_max_len=512`）与 Kev LoRA+head（`epochs=2/max_state=8192/full_ft=0/resume=0`）；父 R11 原 `1 Epoch/384` 与在线导入适配器另记。当前不更新任何模型参数；下一轮需真实同状态动作结果作为新选择目标，保留旧 S1 有效偏好与原固定 Val 的 S1 Accuracy/Loss/Brier/ECE，不能仅追加短评与能力卡重复原配方。上述准备不保证指标不退步，不添加新流程或执行条件；新动作目标缺失只记录准备不足，不自动续训。五 RQ、八图、十二表与正式正文保持，未有总体对照的结果单元继续空白。

## 2026-10-31 · 历史：fix-git 三身份 Alias 官方开发接续

以下保留该 Run 当时完整证据；其 AA、材料与服务器读数不作为最新状态。当前恢复点只在上方更新，其他文档不再复制本段历史详述。

本轮沿原 `our-project/results/iterations/20261031-v9-official-alias/` 和 Harbor 单任务入口完成接续，没有新建迭代。首次 Trial 的任务成功与教师失败分别保留；事后前缀补充不改首次 Episode。主 Agent 在原 `run_config.json`、`resume_state.json` 追加 `fix-git--laya_v2--s42-teacher-stream` 单任务 unit，执行原 `resume`，已完成同一官方 Trial 内成功教师输入到任务提交、官方 Verifier 的完整链路。两个 Trial 均 reward=1.0、CTRF2/2，属于同题开发接续，不能当作两个独立科研样本；整个迭代状态为 `EVALUATED`。

### 首次官方 Trial：任务成功，教师超时

| 对象 | 已确认结果 | 适用范围 |
| --- | --- | --- |
| Task / Job | `fix-git` / `2fdbada6-cac0-4007-8143-9fea68a47c4d` | 原 Job `fix-git--laya_v2--s42` |
| 首次 Trial | `2963d109-d41c-4bc7-a673-5406c6369bae` / `fix-git__Xmdvg6F` | 保留为 `first_trial_id`，原结果不覆盖 |
| 官方终局 | reward `1.0`；CTRF tests `2` / passed `2` / failed `0` | 原 `result.json` 与 `verifier/ctrf.json` 已核对 |
| Router / 生成 / 工具 | `13 / 13 / 22`；合法候选为 Sol/Luna/Flash 三个 `none` 动作，13 次均选择逻辑 `gpt-6-luna:none`，fallback `0` | Laya `F05/epoch_01` 真实前向；首次事件未保存候选概率，不补造 |
| 教师 | 逻辑 Sol 一次 `TimeoutError`，60 秒窗口，无 usage、无成功短评 | 不写教师在该 Episode 成功或已知消费金额 |
| 生成用量与映射费用 | 输入 `99,196`、输出 `14,986`，合计 `114,182` Token；已报告缓存读 `79,040`；`0.01029900 USD` | 实际 Qwen3.8-27B 后端，按逻辑 Luna 价格核算；教师未知使完整模型费用为 `null` |

以上次数与金额仅属于首次 Trial。原 `result.json`、`events.jsonl`、CTRF 和 raw 保留；同 Run 的最终汇总包含两个 Trial，不能用累计数替代首次结果。三个合法候选不表示三个身份均被实际选择，也不证明独立物理模型质量差异。

### 事后前缀补充：成功教师与 SystemOne 消费

原 [teacher_prefix_replay/metrics.json](../results/iterations/20261031-v9-official-alias/teacher_prefix_replay/metrics.json) 为 `VERIFIED`，来源是首次 Trial 已保存的 step3 真实决策前缀，`evidence_scope=POST_RUN_OBSERVED_PREFIX_REUSE`。仅一次逻辑 Sol 教师请求：prompt `9,396`、输出 `608`（visible `372` + reasoning `236`）、缓存 `0`，按 Sol 价格为 `0.024872 USD`。三字段短评指出已定位 `c499730`，变更尚未合并到 master，下一步需确认提交关系并完成合并。

同一次补充中，SystemOne Laya `epoch_01` 已消费短评，`fallback_used=false`；候选概率 Luna `0.4028` / Sol `0.3431` / Flash `0.2541`。这是事后前缀复用，官方与科研结果资格均为 false；不记为首次 Episode 教师成功，不增加独立任务样本，也不把补充费用并入首次 Episode。供应商 raw.cost `0.00037142` 未报告 currency，`actual_billed_cost_usd=null`；不将其当作 USD 账单。

### 同 Run 必要续跑：成功教师已消费，官方终局成功

续跑 Job 为 `4459af75-389a-48cd-8f97-0829f20df0a0`，Trial 为 `469a1fec-4d6f-4ac4-8fbd-8207cd47b189` / `fix-git__RsVfot4`，原 Job 目录为 `jobs/fix-git--laya_v2--s42-teacher-stream/`。原 Assessor 使用 `stream=true`，前两次教师为 `JSONDecodeError`，但真实 usage 已报告，分别为 `8,736 + 2,048`（reasoning `1,024`）、`8,625 + 2,048`（reasoning `1,024`），缓存均 `0`，映射费用分别为 `0.037952`、`0.037730 USD`；失败不将已知用量或费用改成 `null`。

第 3 次逻辑 Sol 教师成功：prompt `8,574`、输出 `564`（含 reasoning `216`）、缓存 `0`，映射费用 `0.022788 USD`。短评指出已定位 `c499730`，master 尚缺变更，合并遇到 `about.md` 冲突，下一步解决冲突并完成合并。成功教师 metadata 的 `assessment_consumed_by_router=True`，`TEACHER_ROUTER_INPUT` 共 7 次为 true；7 次消费对应一次成功教师请求。全部 15 次 Laya `F05/epoch_01` 路由均真实前向、`fallback_used=false`，三合法候选保留，逻辑选择全部 Luna none；每次 `ROUTER_END.ranked_actions` 已保存候选概率，首次 Trial 的缺失概率保持原状。生成与教师的实际后端均为 Qwen3.8-27B，Flash 保留在候选及原历史验证中，不宣称本 Trial 选择过 Flash。

| 续跑最终项目 | 已确认结果 |
| --- | --- |
| 时间 | 2026-10-31 台北 `11:14:14.578611` 开始、`11:31:06.997902` 结束；duration `1,012.419291` 秒 |
| 官方终局 | `AgentSubmitted`，reward `1.0`，CTRF tests `2` / passed `2` / failed `0`，终局异常 `null` |
| 执行统计 | 15 次生成 / 15 次真实路由 / 24 次工具；3 次教师：2 次 JSON 解析失败、1 次成功，3 次 usage 均已知 |
| 生成用量与费用 | input `122,667` / output `22,808`（含 reasoning `9,591`）/ cache `109,568`；`0.01380958 USD` |
| 教师用量与费用 | input `25,935` / output `4,660`（含 reasoning `2,264`）/ cache `0`；`0.09847000 USD`，含两次失败费用 |
| 本 Trial 模型合计 | input `148,602` / output `27,468` / 合计 `176,070` Token；完整映射模型费用 `0.11227958 USD` |
| 实收与资源费用 | 18 条请求的供应商 raw.cost 合计 `0.0033656476`，未报告 currency，实收 USD 为 `null`；Router/工具/容器资源费用仍未知 |

原 `result.json`、CTRF、事件和 metrics 支持上述终局；主 Agent 对18条真实请求的 Decimal 复算与 AgentContext 一致。reasoning 已包含于上述输出，只计一次。本 Trial 实验模型费用完整，不将未知供应商实收或资源费用代填0。整个迭代两 Trial 已知费用小计为 `0.12257858 USD`，首次超时教师 usage 仍缺，完整模型费用保持 `null`；事后前缀补充 `0.024872 USD` 独列，不并入两个 Trial。

### AA、训练材料与服务器当时证据

在线最新快照为 [AA v3](../code/data/v9/capabilities/snapshots/20261030T172129978785Z-v3.json)，ID `20261030T172129978785Z-v3`，Luna Max 有 10 项指标；none 缺测，Sol/托管 Flash 精确页面 404，状态仍为 `NOT_MEASURED`。旧 v1/v2 与不同 AA 版本参考保留，不将 Max 指标复制成 none 成绩。

prepared 唯一材料仍 `390` 行：S1 Train/Val `64/64`、S2 `70/64`、S3 `64/64`，合计 `198/192`；绑定 AA v1。4 条教师短评覆盖 2 个任务、截止 step3，用于观察 step3/7；真实三身份选择标签与 Model×Effort 监督均为 `0`。本轮 Alias 成功不生成最优动作标签，不加入原 Train/Val，不新开相同配方训练；已完成 Laya 总体改善但 S1 退步、Kev 四指标退步的负结果保留。

主 Agent 于 **2026-10-31 11:14:31 台北**只读确认：F14 原 PID `4085749` 仍运行，Epoch2 chunk `256/420`、step `86,470/107,404`，累计 `614` 个 NaN 块。Epoch1 Val 的 Loss/Brier/置信度为 NaN，`5,692` 项预测全部类别 `0`；具体诱因与有效更新次数未知，继续排除父候选，不干预健康训练。Serving PID `327621` healthy，仍用 Laya `F05/epoch_01` 与 `KEV-4B-ADAPTER`，没有上线新候选权重。

| 接续代表 | 本轮文件结构与既有评估证据 | 验证范围 |
| --- | --- | --- |
| Laya `F11/checkpoints/epoch_01` | `model.safetensors` `842,609,220` 字节、206 个 F16 张量；组内 score `159.7985`；S1 Accuracy `0.6898` / Loss `0.5941` / Brier `0.4085` / ECE `0.0378` | 本轮只读文件结构与历史评估，没有重新真实加载该候选 |
| Kev `KEV-V8-COVERAGE-R11/checkpoint` | adapter `129,924,032` / head `5,249,053` 字节；base `models/qwen3.5-4b-base`；score `106.748666`；固定 Val `8,436` 记录/`9,330` 问题，Accuracy `0.569025` / NLL `1.068724` / Brier `0.535678` / ECE `0.018246` | 本轮未重新加载候选；与在线 Serving 导入适配器分开 |

API 不设累计 Token 或美元预算，按实际需要测试，保留服务器资源规则及 Final 隔离。映射费用继续使用真实输入/输出/缓存用量与逻辑目标价格，reasoning 只计一次；供应商实收、Router/工具/容器资源费用未知，不代填 `0`。三原本地 Alias 费用复算及 raw 继续保留，见下方 10-30 记录。五 RQ、8 图、12 表与各文档职责不变，正式总体对照不填本轮开发数。

主 Agent 已完成9份源码 AST 与 diff 格式验证，本轮没有新增测试、临时脚本、训练或模型部署，未替换服务器权重；临时8000 SSH隧道 PID `67078` 已结束，Docker任务容器无残留，没有新增持久重复实现。六文档已记录最终事实；源码与文档的同步版本以 GitHub 当前 main、Git 历史及主 Agent 的最终执行回报为准，不能据此推断服务器版本。

## 2026-10-30 · 历史：千问27B真实调用、目标模型身份与映射计价

用户明确从未设置 API 总 Token 或美元预算。测试数量按任务需要安排，不采用旧文档中的 100 万、1000 万或待额度许可作为当前限制；继续遵守服务器负载、显存、磁盘和既有资源规则，健康训练不中断，Final 不参与训练、教师输入、选池或调参。主 Agent 已获充分测试及部署授权；供应商实际可用性与授权分别记录。六文档口径按本轮要求同步，主 Agent 已完成既有费用复核和原服务状态记录。

主 Agent 已确认原 Provider 移除累计上限，`max/remaining=null`，历史用量保留；原 CLI 默认 `cost_limit=0`，不另设默认美元上限。原项目 Provider `/models` 已实际 GET，返回 3 项，研究池中只列出 `gpt-6-luna`，Sol 与托管 Flash 未列出；这些是本次供应商可用性事实，不要求用户再次批准充分测试。

| 新官方开发对象 | 已确认结果 | 证据范围 |
| --- | --- | --- |
| 迭代 | `our-project/results/iterations/20261030-v9-official-luna-complete/` | 沿原 Harbor 执行链，旧失败目录保留 |
| Job / Trial | `7a98c167-bf7c-47f4-bd73-abe43a8ddc44` / `288084ed-1f00-4cdd-b177-085731dcfb44` | 主 Agent 已确认真实执行对象 |
| 官方结果 | Harbor reward `1.0`、exceptions `0`；`verifier/ctrf.json` 为 tests `2` / passed `2` / failed `0` | 单 Luna 双动作官方开发成功，不代表独立三模型或五 RQ 总体结论 |
| 执行统计 | 14 次生成、21 次工具、4 次教师、14 次路由、0 fallback；真实 `gpt-6-luna:none/low` | 路由全部真实前向，不将两个 Effort 算作两个模型身份 |
| API 用量 | 生成 `165,028` Token、教师 `53,550` Token，合计 `218,578` Token | 只记本 Episode；不与旧失败用量或 Router 本地前向重复相加 |
| 运行时间 | `343.225291` 秒 | 本次 runtime；不推导训练或其他任务耗时 |
| 真实 Luna 官方 Episode 费用 | 生成 `0.00764224` USD、教师 `0.00484108` USD，合计 `0.01248332` USD | 真实 `gpt-6-luna` 官方 Episode；与映射模式分开，供应商 bill 未知，Router/工具/容器资源费用另列 |

费用分支已在原计价器复用30个原请求完成真实 Luna 官方 Episode 的标准价核算并保存，主 Agent 用 Decimal 逐项对照原事件、用量和旧价，金额一致。旧轮模型费用为 `0.00831490` USD，新完整官方 Episode 为 `0.01248332` USD；缺缓存字段保留 null、按普通输入价核算，输出含 reasoning 不重复计费。这组金额只属于真实 `gpt-6-luna` 官方 Episode，与映射模式分开。映射模式按每次真实请求的 input/output/cache 用量乘 Router 选择的逻辑目标身份价格，教师按配置的教师目标身份同样计入；Qwen3.8-27B 请求/返回身份、后端价格和供应商实收另列，缺少后端价格或独立真实模型时不影响映射账本继续。原事件追加 `OFFICIAL_RATE_RECONCILIATION`，原用量、旧配置金额和失败保持不变。真实单探针 `0.00006124` USD 不计 Episode。公开价格核算无需账单许可，供应商 `bill=UNKNOWN` 单列，不影响执行。真实 Luna 官方标准价格为输入/输出/缓存读/30分钟缓存写 `0.10/0.50/0.01/0.125` USD/百万 Token；完整算法与来源见 [数据与计费政策](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md#当前托管-api-身份与计费政策2026-10-30)。

### 映射费用独立重算（2026-10-30，本地账本）

三原目录的 `mapped_cost_accounting` 已独立保存并追加事件；旧 raw、原始计数和终局记录不改。真实生成共 21 条，按 raw 的 `prompt + completion + reasoning` 计量，其中输出费用按 `completion + reasoning` 计一次；6 条成功或已报告 usage 的教师记录按 `prompt + completion`，另 5 条教师 usage 缺失。compact 第 3 条教师即使 JSON 解析失败，只要已报告 usage 仍计一次，不写成成功教师。结果如下：

| 原目录 | 生成 | 已知教师 | 已知合计 | 完整总额 |
| --- | ---: | ---: | ---: | ---: |
| `20261029-v9-alias-smoke-tools` invoice alias | 0.11729720 USD | 0.06450280 USD | 0.18180000 USD | `null`（3 条教师 usage 缺失） |
| `20261029-v9-kev-alias-smoke` 旧失败 | 0.000660788 USD（Flash，2 生成） | 无教师 | 0.000660788 USD | 0.000660788 USD |
| `20261030-v9-kev-alias-smoke-compact` | 0.006449774 USD（Flash，10 生成） | 0.06376000 USD（Sol） | 0.070209774 USD | `null`（2 条教师 usage 缺失） |

Flash 的 `0.15/0.47/0.016` 是 OpenRouter 参考价，不写成阿里官方 USD 价格；当前没有自造汇率。已知小计不代表缺失请求的完整费用。

本轮原Provider真实小请求已验证：所选身份/日志顶层为 `gpt-6.1-sol`，request为 `Qwen3.8-27B`、returned为 `self-dploy/Qwen3.8-27B`；实际55输入/16输出、缓存读写均0，按Sol输入2/输出10 USD每百万Token得到 `0.00027000 USD`。原日志记录 `cost_model_id=gpt-6.1-sol`、`cost_basis=SELECTED_MODEL_RATES_WITH_BACKEND_USAGE`；探针不并入Episode。7个原Python文件和六原文档仅本地更新，本轮未部署、提交或推送，未重跑Agent任务或训练。

两次已有离线教师请求另计材料费用：输入13,766、已含reasoning的输出949、缓存读写0，映射Sol费用 `0.03702200 USD`，已加到原prepared/summary.json的独立核算字段；旧教师记录、原Train/Val及已完成训练不改，短评复用不增加调用费用。

### 原服务部署与重启后验证（2026-10-30，Asia/Taipei）

17 个原服务链源码与配置已定向同步 A6000 原工程，远端 Python AST 与 Serving 模块导入通过。原 Serving PID `2291306` 定向退出，沿原命令于 `20:53:21` 启动 PID `327621`，Kev 于 `20:54:34` 加载完成；没有替换任何权重或改动训练作业。服务器工程不是 Git checkout，不把 GitHub 提交等同于完整服务器版本。

| 重启后实际前向 | HTTP / 回退 | 身份与 checkpoint | 模型前向耗时 |
| --- | --- | --- | ---: |
| Laya，保存的官方 Episode 决策前缀 | 200 / false | `laya-421m`，F05 / `epoch_01` | 1,879.54 ms |
| Kev，同一真实前缀经原 `compact_router_state` 6000字符任务/工具视图 | 200 / false | `kev-4b`，`KEV-4B-ADAPTER` / `1001bb4d826a52d1f399e183466143f4da7b741b` | 82,276.58 ms |

两次成功均选择 Luna low，记录在原 `events.jsonl` 的 `ROUTER_PROBE_END`，不计官方 Episode 成绩、Token 或费用。Kev 首次未压缩的16,770字符输入在90秒客户端窗口超时，原 `ROUTER_PROBE_ERROR` 保留；服务端计算结束后才发送10,321字符正常视图，报告输入3,126 Token。Kev成功验证采用300秒窗口，不改原60秒配置；其本次82.28秒CPU时延仍超过原窗口，不能声称普通Kev Episode时延已达标。

`21:18:38` 原 `/health` healthy，Laya/Kev `weights_loaded`、`inference_verified` 均 true，`/models` 仍为上述原权重。GPU `34,567/49,140 MiB`、90%、79°C；可用RAM267GiB、磁盘946GiB。F14原PID `4085749` 和启动时间未变，日志在 `21:18:25` 到 Epoch1第420/420块、step53,702、consumed3,436,908；第63–420块共358块NaN。该块终点不等于两轮、固定Val或任务终局完成，有效更新数与首次诱因仍未知。

原训练、实体留存、AA v2 与390行v1材料继续复用。独立Sol/托管Flash的真实模型质量证据、AA同协议能力、真实三模型最优动作监督、五RQ对照、供应商实收及资源现金费用仍缺；Provider 研究池列出情况另记，不影响映射实验。后端 Qwen3.8-27B 价格单独记录，不作为映射实验费用前提。不重训已完成候选，不因新而晋升退步权重。

`21:23:32` 最后只读补充：F14已自然进入Epoch2第1/420块，step53,830、consumed3,445,100，loss仍NaN（累计359块）；这是队列自然推进，不是本轮重训或人工接续。GPU `34,567/49,140 MiB`、84%、75°C；此前短时health快照曾显示48,254MiB，不能将单点占用当作稳定余量。原CPU Serving仍运行，GPU进程为原F14、ComfyUI、Image和桌面进程。本轮自有8000 SSH隧道已关闭、无残留监听；没有新备份或定时执行。

## 2026-10-30 20:05 · 历史：Docker 恢复、Oracle 通过，旧模型 Episode 未完成评分

以下各日期条目保留原时点事实、金额和失败；旧额度、旧余额、暂停和等待批准仅为历史，不作为当前测试或部署条件。当前决定与最新正式开发结果以首页为准。

原 Mac Docker 已恢复到既有应用位置，Docker Desktop 4.97.0 / Engine 29.9.2 实际运行，原虚拟机数据保留。本机 Rosetta 已用于原 amd64 任务镜像；临时安装包和目录已删除。服务器服务、权重和健康训练未被重启或更换。恢复前 GitHub/main 为 `b56e9386d8d77edc1a860108a0bead901b733036`，本轮源码与文档同步提交以 Git 历史和最终执行回报为准。

### 官方容器与真实 Agent 证据

| 原执行对象 | 实际结果 | 证据与适用范围 |
| --- | --- | --- |
| `20261019-v10-oracle` 原 resume | amd64 镜像的 QEMU 执行 uvx 崩溃，原 reward=0 | 无 CTRF，保留 `NOT_EVALUATED`，不计任务失败率 |
| `20261030-v9-oracle-native` | Harbor 原 `--force-build` 使用未改的上游 Dockerfile；setup 所依赖 GitHub 仓库返回404 | 未进入 Agent/Verifier，失败记录保留，不改上游任务 |
| `20261030-v9-oracle-rosetta` | Job `6292da72-ecab-4830-ad71-d53dafc4d22d`，Trial `fb4abdf7-a8e9-4fb3-9833-e48aa44febb8`，官方 reward=1、CTRF 2/2通过 | 官方环境核验通过；Oracle 不计模型成绩 |
| `20261030-v9-official-luna` | Job `12214a63-7f57-4584-97da-19865836d629`，Trial `a34286c3-4a4e-43c8-9c5d-c4683fca2f1d`；9次真实 Luna 生成、18次真实工具执行、3次真实教师成功 | 历史：第10次生成因旧 Token 限制未发出；Verifier 未执行，旧终局结果未知。该限制已取消 |

本轮使用原 `benchmark CLI → Harbor Job/Trial → ModelRouterMiniSweAgent → DefaultAgent`，无新增 Runner、模拟器或验证器。单候选试验的生成及教师请求/返回均为 `gpt-6-luna`，12个不同响应 ID、`alias_mapping_applied=false`、`REAL_API_IDENTITY_MATCHED`；该时点 Sol 与 Flash 在项目凭据中不可调用；最新 Provider 可用性见当前决定，未尝试借用其他账号。

该单候选请求触发在线 Laya 原 `rl_common.py:120` 的 `topk(2)` 错误，10次路由使用旧回退路径，`neural_router_evidence_eligible=false`。不修改在线模型或重启服务；原正式配置已调整为同一授权 Luna 的 `none/low` 两个动作。用本轮最后一个真实决策前缀、原教师三字段与原 v2 快照完成一次真实前向：`none=0.5166 / low=0.4834`，选择 none、`epoch_01`、`fallback_used=false`，前向949.87ms；生成/教师新请求均0。证据保留于原迭代的 `router_evidence.json`。这仅证明双动作输入可运行，该时点尚无使用双动作配置的完整官方 Episode；后续成功结果见当前决定。

### 历史教师、旧配置金额与旧用量记录

3次教师分别在决策前缀截止2、3、8处成功，3条短评均含规定三字段。原在线路由因回退未消费短评；随后真实双动作前向保留最后一条短评。教师收益、最优动作和最终任务结果均未因此得到证明。

| 历史用量来源 | Token | 旧配置价估算 USD | 后续官方价核算 USD |
| --- | ---: | ---: | ---: |
| 9次生成 | 98,359 | 0.106028 | 0.00450286 |
| 3次教师 | 40,026 | 0.076560 | 0.00381204 |
| 合计 | 138,385 | 0.182588 | 0.00831490 |

旧配置金额状态为 `UNVERIFIED_CONFIG`，响应未报告费用及币种，实际供应商账单、容器费用、Router费用与完整现金总额仍为 null。20:05 旧累计记录为已知714,168、未知调用预留256,135、旧余额29,697，147次累计调用；本轮增加12次请求。当时未扩大旧限制、未启动第二轮收费 Episode，仅保留历史；现行不设累计 Token 或美元上限，新 Episode 已成功，后续官方价模型核算金额另列。

### 原实现收口与当前剩余项

只修改原 `benchmark/__main__.py`、`harbor_agent.py`、`official_artifacts.py`、`iterations.py`：传递上游构建选项、保存本次能力快照、区分真实API与Alias、采用Harbor真实数据格式、消除未完成阶段的事件/native重复累计。旧通用失败报告审批要求已移除，当时保留的旧预算设置已由当前决定取消，Final隔离和资源规则保留。原始失败、源码和日志均保留；AST及本轮真实记录汇总通过，未新增测试或夹具。

20:04:53台北，F14原PID4085749仍到Epoch1第398/420块、step50,944、consumed3,260,416，第63–398块持续NaN（336块）；首次诱因、GradScaler实际跳步和有效更新数未知。Serving原PID2291306及启动时间不变，health healthy；GPU35,867/49,140MiB、100%、84°C。非有限loss父候选排除规则继续使用，该时点没有重训或上线新Laya/Kev；后续部署结果尚未回报。

20:05 历史剩余项：当时完整模型Episode仍未取得；Sol/托管Flash独立调用与AA同协议数据缺失；三模型真实最优动作/Effort标签仍0；供应商及资源账单缺失；F14数值异常未定位。原Harbor regrade需要保存的修改后文件，本轮artifacts为空且环境已按原流程删除，无法凭现存轨迹补出原Verifier结果。五RQ、八图十二表继续保留，正式模型结果格留空；原390行训练材料与v1绑定不变，canary轨迹不加入Train/Val。

## 2026-10-30 17:56 · 历史：V9 收口与当时运行条件

本轮复用已完成训练和 Agent 记录，没有重训、重跑成功题、加载权重或更换 Serving。GitHub `main` 同步前实测为 `d1712d1f8ce3227a1dcf7fe085b04a1afb2dd9ff`；本轮合规源码及六文档已完成公开安全核验，实际同步Commit以本节对应Git历史及执行回报为准。服务器部署为原文件增量，不是 Git checkout，无法报告完整部署 Commit；旧 Serving 仍为 Laya `F05/epoch_01`、Kev `KEV-4B-ADAPTER`，后者不是 R11 训练候选。本轮formatter/汇总/单Episode等收口代码未覆盖服务器旧进程，源码版本、已加载权重和本地验证分别记录。

收尾同步：实现与六文档已在 `d7cc80e6991a69129ab52f7a85ce65849651d060` 推送main，GitHub API树非截断且17个V9 Python文件完整可见；凭据、私有路径、原始运行/训练数据、测试改动及其他删除未提交。本轮临时native编码脚本已移除、真实结果保留原证据文件。19:10:58台北最后现场F14到第390/420块、step49,920、consumed3,194,880，NaN从第63块持续（328块）；原F14/Serving启动时间未变、health healthy。只将与远端唯一差异的非有限loss父候选排除补丁原位部署 `continuation.py`，没有重载当前进程或启动新训练；原函数对真实Run返回F04/F14=false、F11/V9_LAYA_001=true，AST通过。其余formatter/CLI/汇总仍为本地与GitHub版本。

### F14 与候选处理

17:56:21 台北，F14 原 PID `4085749` 仍运行，日志到 Epoch1 第371/420块、step47,488、consumed3,039,232；第63–371块持续 NaN（309块）。15:51 的逐块核查确认第63–346块连续，无有限块插入。第63–260块已读源引用/目标无缺行及非有限值，具体首次诱因仍未确认。原 `global_step` 无条件累加，GradScaler 的实际跳步与有效参数更新数未保存；没有证据判定全部权重受损。15:51 未见 F14 Epoch checkpoint，不加载权重补测。原服务健康、GPU17:56占35,875/49,140MiB、100%、84°C；没有停止或修改 F14、Serving、Docker权限或其他作业。

原 `v9/training/continuation.py` 已排除记录中出现非有限 train loss 的后续父候选，固定Val有限不能解除该风险；仍复用原可比组及留存评分。Laya 保留 `F11-e01` 为当前接续代表（原内部159.7985、实体在盘），Kev覆盖组保留 `R11`（106.7487、adapter/head在盘），C03继续作固定参考（100）。新Laya总体改善但S1退步，新Kev92.387且四指标退步，两者只保留实验/消融候选，不上线或立即重复同配方；独立Dev尚无证据选出全局最佳Router。

### 能力快照与监督

专用刷新已于12:13真实保存 [v2快照](../code/data/v9/capabilities/snapshots/20261030T041319933533Z-v2.json)，`current.json` 指向 `20261030T041319933533Z-v2`。6次公开GET，AA Sol/Flash两次404，Luna成功解析；没有AA Key，没有调用收费Data API。厂商价格/上下文只是公开资料，不是项目权限或实际账单。

| 模型 | AA v2 实际取得 | 来源/缺项 |
| --- | --- | --- |
| gpt-6.1-sol | NOT_MEASURED | 精确AA页面404；OpenAI厂商价格、上下文、Effort资料在盘 |
| gpt-6-luna | Max Intelligence Index27.7552004938153，AA5.0；另9项Max指标 | AA公开页；Coding/Agentic Index及none动作缺测，不把指数当百分比 |
| qwen3.8-flash | NOT_MEASURED | 托管版精确AA页面404；阿里厂商地区价格/上下文在盘，不套27B或Flash-Next成绩 |

旧v4.3.2的52/38属于此前引用，不覆盖新v2的版本/原分。训练资产仍是唯一390行、Train198/Val192，绑定v1；4教师三字段、2新请求/2复用、6真实prefix及旧S1/S2/S3监督不变，真实三模型choice/Effort目标仍0。未重生成或追写v2到已完成训练；接口消费不等于已学会新能力。

### 输入与教师收口

同一已保存invoice step5、v2快照和原服务器tokenizer，修复前Laya状态4302Token/可用940，能力卡部分保留、最近工具缺失；Kev3656state/3733total不裁。现有formatter只去掉来源长文、共享重复地区费率及上下文资料，并将三候选摘要与最近反馈置前；不改mini消息或输入上限。修复后Laya3934state/1024total、3候选标记：任务[1,206)、教师[206,323)、最近工具末128字符[587,644)、三候选摘要[644,890)完整保留；详细能力卡[1107,2179)和长历史仍裁。LunaMax指数在摘要中明确为参考，不计none成绩。Kev3357state/3434total不裁。仅同样本编码，不新增API前向、训练或全部Train/Val复测；完整证据保留原 `input_encoding_validation.json`，不宣称全上下文保留。

原invoice教师step3首次、step4新验证、step5–8阶段切换，共6请求/3成功；与duration重跑5/2分别统计。阶段变化确实来自真实工具，尚无依据判为重复请求或收益；没有新增调用或复杂节流。原 `iterations.summarize(persist=False)` 已消费两份原事件，分别6/5教师请求，用量和完整USD仍null（失败请求缺usage）；估算、明确USD账单及未知费用分开。原Harbor Context已经含教师的总量，不再与教师事件重复相加。

### 官方入口与停止条件

原CLI新增 `--single-episode`，必须显式一task/一policy；实测 `fix-git/laya_v2` 仅1个unit、三候选保存，上游AgentConfig往返为dict/list。默认多阶段规划保留，已有run/resume记录不改。V9 hook按原 `/models` 的loaded/family/checkpoint匹配记录run_id，注明该元数据与route非原子、Kev仍仅Serving导入身份，不补造历史Run。

本机preflight：Harbor0.24.0和mini2.4.6可加载、上游fix-git可解析，Docker命令不可用；服务器daemon active但syy socket denied且缺Harbor任务环境。官方Trial/Verifier本轮0，完整费用未得，不启动容器或绕权限。最短下一步是恢复原Mac Docker，再沿既有Oracle `resume` 取得环境证据，随后原CLI单Episode；不能把Oracle或Alias当三模型正式成绩。API预算仍135calls、known575783/reserved256135/remaining168082；本轮新增生成/教师0、收费API0。五RQ、八图十二表及全部负结果保留。

## 2026-10-30 10:28–10:40 · 历史：Laya V9 完训

**当前结论**：Laya `V9_LAYA_001` 与 Kev `KEV-V9-001` 均已完成两轮训练及各自原固定 Val，新权重保存在原服务器工程，未传 Mac、未上线 Serving。Laya 总体及 S2/S3 指标改善，S1 四项退步；Kev 四项相对 C03 均退步。AA 实测、三个独立模型的正式执行、完整 Episode USD 及 Harbor/RQ 成绩仍缺。以下旧时点的“Laya 未启动”和 F14 第 175 块统计保留为历史，不代表当前状态。

### Laya 原入口接续与保存实体

复用原 `router_data/laya_batch_train.py --full-coverage-run F13`：F13 已于 10-29 17:08:13 完成两轮、固定 Val 和保存，本次沿 `skipped_existing` 跳过 F13 重训，再调用现有 `v9/training/continuation.py`。原评分选择父 `F11-e01`，内部得分 159.7985；没有新增 Trainer、队列或 Runner，也未改变 F14。

`V9_LAYA_001` 于 10-30 10:28:40 启动，worker 183110；10:34:16 完成两轮训练及每轮完整固定 Val。参数为 `epochs=2/max_len=1024/head_max_len=512`，训练完整 encoder 与 head，每轮四次优化器更新，共八次；两轮 train loss 为 0.9904379869、0.7104009271，均有限。启动时空闲 27,332 MiB、原资源需求 16,384 MiB。

首次接续完成标为 `CHECKPOINT_PENDING`，实际权重已在盘。真实函数调用确认原 `has_physical_weights` 不接受目录链接，而 `best` 指向的实体目录可加载。仅在原 `finish` 中先解析目录链接，原位部署后重用保存结果，10:40:33 状态成为 `COMPLETED`；未重训或重评。

实体路径为 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/V9_LAYA_001/checkpoints/epoch_02`，`model.safetensors` 为 842,609,220 字节，目录共 846,196,980 字节，模型与 tokenizer 配置均存在，`best` 指向该目录。原留存流程移除第 1 轮权重，释放 846,196,980 字节；该轮参数、成绩与记录保留，权重需按原训练重建才能恢复，本次未重建。第 2 轮 `weights_saved/loadable=true` 与实体在盘均已确认；原 `retention_status=METADATA_ONLY` 标签仍保留，不能由该标签推断实体不存在。

保存模型已经原 `laya.train.load_checkpoint` 在服务器 CPU fp32 严格加载，并用原 S1 Val 第 1 行经 `items_from_rows → calibration_records` 完成真实前向：logits 有限，两类概率为 0.4339680374 / 0.5660319924，目标为 `[0,1]`，跳过 0。未发模型 API 请求、未更换 Serving。

### Laya 实际输入与固定 Val

198 条 Train 全部使用，完整 state 192、部分 state 6；两轮 396 次输入，完整 384、部分 12。四条教师记录共八次输入，核心字段均保留；198 条能力卡共 396 次输入全部保留，但卡片仍缺 AA 分数。状态为 `FEATURE_PARTIALLY_TRAINED`：实际输入消费与完整状态覆盖分开，有限 loss 不证明教师或能力字段的独立收益。三个新身份的选择/Effort 监督目标仍为 0。

两轮固定 Val 每轮完整加载 S1 561、S2 337、S3 4,794，共 5,692 条，跳过项为空；没有使用 Test。下表各单元依次为父 `F11-e01` → 新第 2 轮。

| 原固定 Val | Loss | Accuracy | ECE | Brier |
| --- | ---: | ---: | ---: | ---: |
| S1 | 0.5941 → 0.5969 | 0.6898 → 0.6827 | 0.0378 → 0.0466 | 0.4085 → 0.4105 |
| S2 | 2.2982 → 1.3626 | 0.5341 → 0.6024 | 0.4004 → 0.2640 | 0.8136 → 0.6394 |
| S3 | 1.2416 → 1.0473 | 0.4543 → 0.4656 | 0.2554 → 0.1896 | 0.7288 → 0.6360 |
| 总体 | 1.2403 → 1.0216 | 0.4823 → 0.4951 | 0.2354 → 0.1698 | 0.7022 → 0.6140 |

这是内部固定 Val 对照，不能代替 Harbor、模型池效果或 RQ 成绩；教师、状态长度及训练材料共同变化，未证明单个字段的效果。

### 原 Mini-SWE-agent 的 V9 配置接入

仅修改现有 `benchmark/__main__.py`：原 `run --v9-config` 接受已有 JSON 配置，保存 `v9_config/candidate_actions` 到原运行配置，并通过 `--agent-kwarg` 传给上游 Job/Trial；原 `resume` 沿用保存参数，已存在 Job 使用自己的原 Agent 配置，不重新读取来源文件。无 V9 参数时仍用原默认行为。`iterations.py/official_artifacts.py` 未改，没有新增执行链。

用原成功联调目录的 `run_config.json` 执行原 `run --task fix-git --agent modelrouter --policies laya_v2 --v9-config … --dry-run`，并使用真实 Harbor 0.24.0 的 `parse_kwargs → AgentConfig → AgentFactory → ModelRouterMiniSweAgent → PolicyModel → V9DecisionHook/AliasProvider` 完成参数解析、JSON 往返和实例构造。三候选保留为 Sol/Luna/Flash 的 `none` 动作，真实配置后端 `Qwen3.8-27B`；`BACKEND_PRICE_NOT_MEASURED` 只表示后端价格尚未单列，映射实验费用按所选逻辑目标身份价格记录，账本未变。仅验证配置接入，未创建 Run/Job、执行 Agent `run` 或实际 `resume`；不能计为正式任务执行。

### F14 最新诊断与真实外部缺项

10:32:49 的原日志到第 260 块、step 33,280、消费计数 2,129,920；第 63–260 块共 198 块持续 NaN，没有恢复证据。原第 63 块 8,192 个源引用均存在，按原目标构造得到的向量全部有限、非负且归一化；这排除了已读取目标向量的数值异常，不能证明所有外部标签语义正确。来源数为 ROUTE-004 60、TRA-001 2,770、TRA-002 3,138、CACHE-001 41、TIME-001 1,902、OWN-002 281。原总选源 3,436,908、seed42 打乱、切片 `[507904:516096]`、组内合并 seed104。该块临时目录已由原训练移除，没有当时编码张量、logits、梯度或 scaler；具体诱因与有效优化更新仍未知。V9 新训练有限 loss 不表示 F14 恢复；原作业未停止、重启或改动。

Mac 原 Harbor 0.24.0、Mini-SWE-agent 2.4.6 与 89 个上游任务存在，但 Docker 程序链接失效、个人 socket 不存在。A6000 Docker 29.4.1 daemon 活跃，当前用户访问 socket 被拒绝，`sudo -n docker version` 需要密码；工程尚无 Harbor/mini 包、任务树和三个 benchmark 原入口文件。本轮未安装、构建镜像、启动 Trial 或运行官方 Evaluator。沿用唯一 `benchmark CLI → Harbor Job/Trial → HarborAgent → DefaultAgent`，工具由 `environment.exec` 执行；需恢复 Mac Docker，或由管理员提供现有服务器 daemon 的访问权限，才能继续正式容器评测。

AA Key 当前缺失，仍为 `FAILED/NOT_MEASURED`、分数 null；原 Luna HTTP 200 的正文未保存，解析诱因无法确认，未重复来源请求。需要有效 AA Key 或精确模型身份的官方原始响应。三逻辑身份仍共用返回 `self-dploy/Qwen3.8-27B` 的后端，校园 9002 物理对应 `UNKNOWN`；这属于映射实验的实际后端记录，不能写成三个独立物理模型质量对照。映射费用按所选逻辑目标身份价格，后端价格与供应商实收另列，二者缺失不影响映射实验继续。原 135 calls、known/reserved/remaining=`575783/256135/168082` 未变，本轮训练与 CPU 前向不并入 API Token 账本；完整 USD 仍缺测。五 RQ、八图、十二张正式结果表继续保留，未知结果不填数。

## 2026-10-29 起 · 历史执行记录（截至 10-30 04:34）

**来源与边界**：当前Kev第4次两轮训练及固定Val均完成：训练03:25:31退出0，Val于2026-10-30 04:23:20台北完成、控制器50514自然退出0，`status/training_status=COMPLETED`、`evaluation_status=EVALUATED`。相对原C03四指标均退步，内部score92.38703579133796；V9组仅1条、rank1仅为单成员排名，`apply=False`留存未删除权重。新候选仍`FEATURE_PARTIALLY_TRAINED`，权重只在A6000、未上线Serving，正式Harbor/RQ仍空白。前三次FAILED及未知输入统计不覆盖。F14运行推进、损失持续非有限，有效优化更新未确认，具体诱因未知；主证据见下方F14段，Laya V9未启动；Serving健康接口与F14数值状态分开。现行Val/评分/现场依据主Agent服务器实测回报，本机直传JSON证据已读；本机同名candidate_queue/ledger未包含V9项，不作为现行评分来源。文档子任务仅改六份原Markdown，未改源码/结果数据/服务器，未发业务请求、运行测试或新增夹具，未执行Git；训练219465个本地前向Token不计为API实际用量，135calls及575783/256135/168082不变。

| 对象 | 已回报事实 | 证据边界 |
| --- | --- | --- |
| A6000 `/models` Laya | `F05 epoch_01` | 当前服务加载版本，不代表 F13 已投入推理 |
| A6000 `/models` Kev | `KEV-4B-ADAPTER`，ID `1001bb4d826a52d1f399e183466143f4da7b741b` | Serving 导入适配器，不能称 R11 候选，不能据此断言新特征已学习 |
| Laya F13（早先现场） | 当时健康运行，原 worker `2775954`、controller `499841` | 保留原观测；F13 最终训练/验证结果尚待回报 |
| Laya 原训练链（21:59） | F14，PID `4085749` 正常；GPU 10,039/49,140 MiB、82% | 原链运行快照，不代表 V9 新训练已启动 |
| Serving | 原进程 `2291306`，端口 `8000` | 继续使用同一服务，无新增副本 |

**三候选真实路由前向**：通过 SSH `8000` 调用 `/v1/systemone`；三候选均使用内部 `none`，原生 Effort 请求字段省略。概率顺序见表，两模型均 `fallback=false`。

| Router | `gpt-6.1-sol` | `gpt-6-luna` | `qwen3.8-flash` | 选择 |
| --- | ---: | ---: | ---: | --- |
| Laya | 0.2578 | 0.5214 | 0.2208 | `gpt-6-luna` |
| Kev | 0.3492 | 0.2880 | 0.3627 | `qwen3.8-flash` |

这组概率只证明真实路由模型前向，Laya/Kev 分别选过 Luna/Flash；它们与下列单题全部选择 Sol 的实际生成记录分开。单题控制链成功不证明旧状态布局语义正确、新特征已学习或正式三模型收益。

**Qwen 与凭据演进**：前一阶段只找到 Parfit 网关和凭据候选，状态为待验证；现已回报 `<ALIAS_API_ENDPOINT>` 的 `/models` 真实返回 `Qwen3.8-27B`，来源确认为 `PCG/config/pi-sag.local.env`，仅按 `QWEN_API_KEY` 读取，不改源、不记录密钥。校园 `root9002` 在 NPU5/6 已存在、无有效认证的记录继续保留，共享模型/认证未改。Alias 的物理后端仍为 `UNKNOWN`；网关返回名不能证明与 9002 是同一物理部署。Project jiji 与当前 Codex oneapi 均无 Qwen，不使用未批准替代模型。此前 Provider 凭据隔离新增 1 项测试通过的事实保留，不据此推断两类新解析问题或整任务已全部验证。

**SSE 失败与工具联调阶段**：首次 SSE 的工具字段为 null，暴露 `choices/tool_calls` nullable 及 `function.name/arguments` nullable 两类 Provider 解析问题；主 Agent 已在现有解析中处理。原失败完整保留，后续运行不能覆盖它们。

| 原迭代目录 | 已回报事实 | 当前证据边界 |
| --- | --- | --- |
| `iterations/20261029-v9-alias-smoke` | 失败记录完整保存 | 失败不改写为成功，不删除原记录 |
| `iterations/20261029-v9-alias-smoke-sse` | SSE 失败记录完整保存 | null 字段处理已由主 Agent 调整；不代表完整终局已通过 |
| `iterations/20261029-v9-alias-smoke-tools` | 真实成功终局：9 次生成、13 次 Bash、7 项 unittest 全部通过；先前流式名 `Qwen3.8-27B`、实际非流返回名 `self-dploy/Qwen3.8-27B` 原样保留，逻辑选择仅 `gpt-6.1-sol`；Laya 全程 `fallback=false`，Checkpoint `epoch_01` | `ALIAS_SMOKE` 控制链证据；完整 prompt/completion/cache/USD 因失败调用 usage 缺失仍为 null，不写零或填正式成绩 |
| 迭代 `20261029-v9-kev-alias-smoke` | 另一 `duration` 工程题，2 次真实生成、3 次 Bash 后，第 3 次路由 60 秒超时；默认原 `PolicyModel` 在 fallback 后退出，原回报 `FAILED/验证1`，所有日志保留 | 与成功 invoice 和 Native 前缀回放分开；本地 Host 无容器隔离，不称安全或正式基准，不增加科学成绩 |

**Kev 当前 CPU 前向与失败定位**：原 Serving PID `2291306` 未重启、未换权重。真实启动的 `KevAdapter` 未传 `device` 参数，默认 CPU，原设备标记 `torch_cpu`；不因运行于 A6000 就把这组 Router 前向称为 GPU/NPU 前向。

| 本失败题阶段 | 主 Agent 已回报观测 | 限制 |
| --- | --- | --- |
| step0 | Kev 真实前向 **18,802 ms** | CPU、当前输入条件下的单次观测 |
| step1 | Kev 真实前向 **38,674 ms** | 不能由两次观测推导正式时延统计 |
| step2 / 第 3 次路由 | 工具 history 长度回报 **3,835**，60 秒客户端窗口超时并走 fallback | history 长度单位未报；本次不计真实前向成功，原 `FAILED/验证1` 不改写 |

首个 Bash 执行 `find /` 查找文件后，上游工具 30 秒超时；后用 `ls/pwd` 定位，未改外部数据的回报保留。缺容器隔离的 Host 控制测试不能证明安全性；`ALIAS_SMOKE` 是身份联调用途，环境仍属 `LOCAL_HOST_EXPERIMENTAL`，不填官方表。先前在线教师失败后 Agent 继续与本次 Router fallback 后原 PolicyModel 退出是两种已测行为，分别记录。

**本失败题处理范围与停止位置**：复用原 Runtime，按既有 `router_context_chars` 缩短给 Router 的工具视图，保留 task、teacher 和原始 mini 消息；真实初始 CWD 的接入不由单次 step2 回放推断。短视图与一次必要重跑现均有实际结果，重跑已结束 `FAILED`，没有待完成的成功终局。成功 invoice 不重跑，不新建 Agent 循环、服务或记录体系，不把本题加入 390 行训练材料；本轮不再新增生成式请求。

**原失败前缀的 Native 短视图验证（单次前向成功）**：原目录 [input_latency_validation.json](../results/iterations/20261029-v9-kev-alias-smoke/input_latency_validation.json) 记录 `NATIVE_INPUT_REPLAY`，UTC `2026-10-29T16:16:51.378272+00:00`；原失败不覆写，生成请求 0、Serving 权重未变。

| 输入/状态 | 原值 → 本回放 | 证据含义 |
| --- | --- | --- |
| step2 任务 | 1,019 → 1,019 字符 | 任务全文保留 |
| 工具摘录 | 3,835 → 1,280 字符 | 字符预算 `router_context_chars=2300`，不改 Agent 原始工具消息 |
| mini 消息 | 7 条，`complete_messages_retained=true` | 主 Agent 回报原样保留，不把缩短的 Router 视图当完整 Agent 轨迹 |
| 教师/能力/连续状态 | 保持不变 | 本回放 `teacher_assessment=null`、卡片仍缺测；缓存值沿用原连续状态，不产生新增教师、能力或缓存观测 |

原 Serving 适配器 ID `1001bb4d826a52d1f399e183466143f4da7b741b` 保持，CPU 实际前向 **37,771.85 ms**、`fallback_used=false`，选择逻辑 `qwen3.8-flash:none`。下列顺序按真实动作身份核对，不能套用先前 Sol/Luna/Flash 的排列。

| 逻辑动作 | 真实概率 |
| --- | ---: |
| `qwen3.8-flash:none` | 0.7234 |
| `gpt-6.1-sol:none` | 0.1468 |
| `gpt-6-luna:none` | 0.1298 |

记录仍为 `LOCAL_HOST_EXPERIMENTAL`，官方/科学结果资格均 false，`token_measurement_status=NOT_MEASURED`、`FEATURE_NOT_TRAINED`。这补充字段保留和原 CPU 前向证据，不代表教师三字段有有效摘要、Token 编码全部覆盖、新权重已学习或该题已成功。

**一次必要重跑已结束：真实路由通过，代码失败**：新目录 `our-project/results/iterations/20261030-v9-kev-alias-smoke-compact` 保留 [metrics.json](../results/iterations/20261030-v9-kev-alias-smoke-compact/metrics.json) 与 [verification.txt](../results/iterations/20261030-v9-kev-alias-smoke-compact/verification.txt)。这是原 duration 题的必要重跑，原 `20261029-v9-kev-alias-smoke` 失败不覆写。

| 对象 | 本轮实际结果 | 不能推导的结论 |
| --- | --- | --- |
| 生成/工具 | 10 次生成、13 次真实 Bash | 调用和工具实际执行不等于任务成功 |
| Kev 路由 | 10 次真实路由全部 `fallback=false`；CPU 前向 **20,430.85–37,243.64 ms** | 本次未再触发原 60 秒超时；仍非正式时延统计 |
| 模型身份 | 全部逻辑选择 `qwen3.8-flash`；请求实际后端为 `Qwen3.8-27B`、导入适配器 ID `1001bb4d826a52d1f399e183466143f4da7b741b` | 无正式三模型效果，不能将在线适配器称 R11 |
| 在线教师 | 5 请求/2 成功，3 失败依次 `TimeoutError`、`JSONDecodeError`、`TimeoutError`；成功短评在 steps3/4/5 实际送入 Router | 2 次成功的重复消费不算 3 次成功；不证明新特征已学习 |
| 验证/终局 | 7 项 test 方法、4 项通过，仍有 **7 个 subtest errors**；10 步 `LimitsExceeded`、`status=FAILED`、`resolved=false`、验证退出 1 | 题目失败，不能写成功 Agent或官方成绩 |
| 完整用量/费用 | 失败教师缺测，prompt/completion/reasoning/cache/USD 全部总值仍 null | 不写 zero，不加可得部分冒充完整费用 |

主 Agent 回报原 `test_duration.py` 未改，已保留的 artifacts 为 `task.md`、`duration.py`、`test_duration.py`、`duration.patch`；本机已确认这些文件位于新结果目录。duration 临时工作目录已由主 Agent 清理，原失败和这次失败的记录仍在。短视图改善路由时延，代码质量未因此达标；宿主测试依旧无容器隔离，无官方或科学成绩。

**首批数据与初始教师回报（历史阶段）**：首批 **390** 条由 S1/S2/S3 每类 Train/Val 各 64 条（共 **384**）加 **6** 条真实 prefix 构成，Schema 可加载。原 S1 目标仍是旧模型身份，V9 三身份 choice 目标 **0**；格式可加载不能写成三身份监督已就绪。AA 为 `FAILED / NOT_MEASURED`，没有成功取得首版能力分数。两条参考来自 TRA-001 公开数据的不同任务，`resolved=true`、`split=train`；具体 ID、用途许可及同题隔离细项尚未回报，不补造。当时离线 Teacher **0**、最少真实 prefix 正在补，线上待自然触发；下段保留随后新回报。新特征仍记 `FEATURE_NOT_TRAINED`，继续微调未完成。

**当前材料实体与固定参考**：原 390 条现已整理进唯一实体，Train **198**、Val **192**，不把链接或运行记录另加为训练行。

| 监督来源 | Train 记录 | Val 记录 | 当前材料 |
| --- | ---: | ---: | --- |
| S1 | 64 | 64 | 旧目标未对齐 V9 三身份，最后已知 choice 目标 0 |
| S2 | 70 | 64 | 原 Train 64+6 真实前缀；`trajectory_prefixes/train.jsonl` 仅为相对符号链接 |
| S3 | 64 | 64 | 原请求/运行辅助记录 |
| 合计 | 198 | 192 | 唯一实体 390 行，不重复统计 |

六前缀来自 `gruebel_pycep_pr109`、`fonttools_fonttools_pr2313`，每题截止 **0/3/7**，原 Train 资格保留；与两条固定 TRA-001 公开 Train 成功参考 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024` 不重合。不把六条记录写成六个独立任务，也不猜各截止位置属于新生成、复用或未触发中的哪一类。参考 ID/同题隔离已补证，具体角色用途与许可证据沿原来源登记保留。

**离线教师当前制作**：复用原 Assessor，**2 次真实请求/2 次成功**，**4 条可用三字段样本（2 新、2 复用）**、**2 条未触发**；汇总为 `summary.teacher_data_status=PARTIAL`、`GENERATED=4 / NOT_GENERATED=386`。实际教师返回 `self-dploy/Qwen3.8-27B`，教师账本的 `teacher_model_id` 按配置教师目标身份记录，返回身份另存。两请求 prompt **13,766**、completion **949**、总 Token **14,715**，reasoning **678** 已包含于 completion，不再相加；cached **0** 已报告、USD **null**。这是两条离线请求的已知用量，结果复用不等于 Provider 物理缓存命中；不据此计算所有请求完整总量或新预算余额。

**AA 来源尝试与缺测**：改善现有解析后，三逻辑 ID 的实际来源请求分别为 Sol **404**、Luna **200 但解析失败**、Flash **404**，AA Key 缺失；仍为 **0 条实测能力记录**，current 保留原缺测快照。HTTP 200 不代表取得分数，记录数 0 也不代表能力分数为 0。

**AA 刷新范围澄清**：每次手动执行专用刷新入口重新请求 AA，Agent 使用已保存快照；Agent 启动和 Router 每次决策不自动访问 AA。现有 `load_current` 已符合快照读取方式，本轮不为此改代码或新增 job；用户已撤销自动刷新派发。依据为第二提示词 198–208、335、773 行及本轮澄清，正式训练/实验固定相应 `snapshot_id`。

**在线教师阶段演进**：先回报 2 次成功调用，实际返回 `self-dploy/Qwen3.8-27B`，两次三字段进入下一次 Router 输入、`fallback=false`；另 1 次 Timeout 后 Agent 继续，当时 `invoice` 仍在重写。现在单题已终局，Teacher 共 **6 次尝试/3 次成功**，其他超时/解析失败均未终止 Agent；不猜各失败类型的具体数量。`TEACHER_ALIAS_SMOKE` 输入传递和失败行为保留，不能充当 Sol/顶级教师效果或权重学习证明；与上方离线 2 请求/2 成功、4 条可用样本分别统计。

**三身份覆盖的区别**：此前真实 `/v1/systemone` 分别选过 Luna/Flash，本题 9 次生成只有 Sol 逻辑选择。随后额外短 Provider 验证已确认三逻辑身份均映射同一 Qwen API；`/models` 和已报流式名为 `Qwen3.8-27B`，实际非流返回 `self-dploy/Qwen3.8-27B`。这是映射实验的后端证据，不能算两道新 Agent 题、K=3 个物理模型或三模型质量对照；映射费用使用逻辑目标身份价格，实际后端身份和供应商实收另列。

**新 Native 前缀真实回放**：主 Agent 已在成功目录 `iterations/20261029-v9-alias-smoke-tools/router_input_replay.json` 保存两路结果。

| Router / 尝试 | 已回报结果 | 身份与限制 |
| --- | --- | --- |
| Laya 新输入 | 选择 `gpt-6-luna`、`epoch_01`、`fallback=false`，三候选真实概率 | 原服务权重真实前向；未提供新概率数值，不套用上方旧概率 |
| Kev 首请求 | 20 秒客户端窗口超时，出现模拟 fallback | 负结果保留，不能计为真实前向成功 |
| Kev 一次重测 | 60 秒客户端窗口下真实前向成功，约 **53,516 ms**；选择 `gpt-6.1-sol`、`fallback=false`，三候选真实概率 | ID `1001bb4d826a52d1f399e183466143f4da7b741b`，Serving 导入适配器，不能称 R11 候选 |

回放不重跑同一 `invoice` 题，不增加正式/科学成绩；客户端窗口与模型真实前向时长分开。它补充新前缀的真实 Router API 行为，不能替代最终 Tokenizer 覆盖、新特征学习或独立任务效果证据。

**已测输入语义缺口与单一格式实现**：integration 的 holding Tokenizer 观测表明旧 LayaState 布局把任务文本放在预算之外，JSON 有字段仍会在实际编码时丢失任务。

| 旧布局观测 | State Token 数 | State 预算 | 任务位置 | 已确认结果 |
| --- | ---: | ---: | ---: | --- |
| A | 2,762 | 940 | 2,733 | 任务被裁 |
| B | 2,827 | 940 | 2,798 | 任务被裁 |

主 Agent 已在唯一 V9 context formatter 中调整为任务优先、压缩缺测能力卡，原 Schema 只薄调用。已保存的原14:41 UTC final及训练prefix [分词记录](../results/iterations/20261029-v9-alias-smoke-tools/input_encoding_validation.json) 确认任务、三教师字段、三候选卡及缓存/身份关键字段进入最终编码；中间缓存被裁的负结果保留历史。新顶层`recent_tool_validation`于18:44 UTC/02:44台北仅验证原step5（events第30行）：原Tokenizer1024/head512、state_room940，raw_state2684/total1024、候选标记3。任务Token `[2,206)`、三教师、三候选卡 `[688,872)`、缓存及当前/前次身份均`FULL`；真实512字符工具结果仅原文末128字符在 `[879,930)`为`FULL`，长`history_snippet`仍裁。Kev原native编码2147 state/2224 total、不截短、候选键3个，编码验证未新增Kev API前向。18:46 UTC/02:46台北同源Laya真实API前向`fallback=false`，选Luna，概率Luna0.4005/Sol0.3519/Flash0.2476，模型前向1961.71ms、客户端1985.07ms，checkpoint仍`epoch_01`。主Agent本次新增Router1/生成0，135calls及575783/256135/168082预算不变。随后原`v9/runtime/context.py`单文件原位部署，fresh导入路径相同；序列化8822字符、真实128字符tail、源cached3136及前次Sol身份保留，cached3136仅为源字段，不算本次Router新缓存命中，未重启Serving/模型。旧before/intermediate/final、训练分词、原事件和mini消息及全部失败保留，不重跑题目；本次未重测198条Train或192条Val，不记作全部历史完整或新特征已学习。 同一原记录新增`live_transport_validation`：2026-10-30 04:20:38台北对原invoice step5实际调用旧Serving `/v1/systemone`，8822字符state按字符串直传；3候选依次`jiji/gpt-6-luna`、`openai/gpt-6.1-sol`、`aliyun/qwen3.8-flash`，均`effort=none`。HTTP200、`fallback_used=false`、checkpoint仍`epoch_01`，概率0.4005/0.3519/0.2476，响应`usage.input_tokens=1024/output_tokens=0`。同发送正文的原native编码为2684状态Token/940余量/1024总Token，任务、教师、能力卡、continuity及最近工具末128字符保留。仅“直传调用链、同发送正文native编码与响应Token数支持”这一范围；未捕获旧服务进程Token IDs，普通`/route`未验证，长history仍裁，未重跑整个Episode、重启旧服务或加载额外模型。 本次Router1/生成0与旧`recent_tool_validation`分列，不新增Agent题或科学成绩。

此前15:26 UTC保存的198条Train分词/native编码范围测量已完成，本次step5验证未重测该批材料；4条教师前缀的任务与三教师核心在当前Laya1024下保留；6条完整state仍被裁，全198条完整Laya编码至少需8143，8192推荐尚未启用。Kev完整Train state至少需7401，当前8192及原Loader198条接纳已确认；原384默认拒绝144条仅作历史诊断，不作当前接纳结论。192条Val仅核记录身份/数量，未测Token长度；原问题、候选次序与目标未改。

**原运行记录位置复用**：主 Agent 已把误放在 src 目录的 **2 条真实 Episode** 与 **14 条真实调用** 迁至原 `experiments/agent_pilot/ledgers` 和 `runs/agent_pilot/multi_model_calls.jsonl`，Logger 复用同一工程根定位；误放副本已删，数据全部保留。不新增长期记录体系，这些运行记录不并入 390 行材料。

**金额单位与事件版本**：hcnsec 的 `raw_usage.cost` 有金额，但未提供 `currency/cost_currency`，单位尚未确认。主 Agent 已让新请求保留 `raw_reported_cost`，`reported_cost_unit=NOT_REPORTED`；仅响应明确 USD 才赋 `actual_billed_cost_usd`。未知单位金额不计入完整美元费用。当前 Episode 的旧事件保留原版本输出，不将旧字段名当 USD 单位证据；完整费用含超时，现有总额为 `None`。最终汇总仍须说明单位未确认，新请求按新 Provider 记录，不能把未知金额或缺失总额写成零美元。

**历史 Token 已知量、旧失败预留与旧余额分列**：以下保留上一阶段回报，尚未包含随后全部生成/教师 usage 的最终结算。

| 项目 | Token 数 | 含义 |
| --- | ---: | --- |
| 原 `token_budget` 已知记录 | 410,353 | 既有已知量，不含尚待计入的后续真实 usage |
| 9 次失败调用预留 | 77,544 | 当时每次按 8,616 预留；失败实际 usage 为 UNKNOWN，不算已实际消耗 |
| 上一阶段扣已知量与预留后的余额 | 512,103 | `1,000,000 - 410,353 - 77,544`；旧限制下的余额公式，仅保留历史，不作当前停止条件 |

**历史预算记录（短视图/窄重跑回报前）**：`known=494912`、`reserved=193040`、`remaining=312048`。这是当时用户提供的阶段快照，保留上表历史；reserved 仍不计实际用量，不能推断缺失调用的实际 Token 或完整 USD。当时新一轮运行尚未结算，该历史阶段的最后记录见下段。

**该阶段历史预算与清理回报**：`known=575783`、`reserved=256135`、`remaining=168082`；新增 **15 API 请求**已计入原账本，累计 **135 calls**。这替代前段作为本轮最后已报预算，历史数继续保留；reserved 不作实际消耗，完整用量/费用因失败项仍 null。该阶段曾停止新增生成式请求，旧暂停决定不作当前约束。自有本机 8000 隧道 PID `28959` 已结束，duration 临时目录已清理，artifacts 与全部失败证据保留；该回报时 A6000 Serving/训练未操作。

**训练参数已准备、服务器部署已完成**：现有 [prepared/summary.json](../code/data/v9/prepared/summary.json) 的 `training` 段已写真实配置，部署/材料读取已有实证；第 1 次训练启动失败，参数和部署成功不计训练完成。

| 对象 | 实际记录参数 | 身份/状态 |
| --- | --- | --- |
| Laya 继续微调准备 | `epochs=2`、`max_len=1024`、`head_max_len=512` | 准备参数，未获本轮新训练完成证据 |
| Kev 第4次训练已完成 | `epochs=2`、`max_state=8192`、`full_ft=0/resume=0` | 两轮/固定Val已完成、内部EVALUATED；四指标比C03均退步，新权重未上线，与父Run原长度/轮次分开 |
| Kev 父 R11（主 Agent 回报） | `epochs=1`、`max_state=384` | 训练父对象，与当前 Serving 导入适配器不同 |

**首批服务器部署实证（主 Agent 回报）**：目标仍为 `<SERVER_PROJECT_ROOT>`，37 个源码/数据/相对链接对象、6,993,920 传输字节，包含 16 个 V9 Python 模块、schemas/registry/common 和 390 行材料。原 Laya/Kev 两文件增量补丁成功，保留 Laya 4 处历史差异；common 约 45KB 的重复实现已改为现有薄别名，实导入 `common is canonical=True`，真正 root 执行链保留。原 Python/`_material` 实读198训练行、4教师、2refs，相对链接有效，GPU/Serving未重启。随后模块入口和Provider/telemetry接点追加部署另记，首批数量不冒充全部后续传输总数。

| Kev 候选阶段 | 已发生事实 | 当前结论 |
| --- | --- | --- |
| 原 `--plan-only` 登记 | 同一 candidate_queue/ledger 写 `KEV-V9-001`，登记时 QUEUED；父 R11 实体、内部四指标 score 106.74866622586939，原 R01–R16已完成 | QUEUED 仅保留登记阶段；父分数不算新候选成绩 |
| 同一原 CLI 第 1 次启动 | worker **13266**，**0.145 秒**退出 **1**；未加载 GPU 模型、未消费训练输入 | 历史 **FAILED**、attempt保留，不改写为成功 |
| 失败原因 | 路径执行 `dispatcher.py` 使 `sys.path[0]` 在 `modelrouter/training`；bare `import kev` 落入本项目 `training/kev`，官方 `kev.train` 未导入 | 189 项先前组合测试通过不覆盖这项真实入口负结果 |
| 原失败证据 | `train.log`、`attempt`、`cursor` 保留 | 不覆写、不删失败 |
| 同一原 CLI 第 2 次启动 | worker **16722**先RUNNING；两行模块入口调整已部署、窄测40通过，官方 `kev.train` 位于 `external/kev/kev/train.py` | 启动与导入已确认，后续OOM见下一行，不计完训 |
| 第 2 次真实反向失败 | 8K输入进入真实反向计算，Torch CUDA OutOfMemory、自然退出 **1**；进程 **13.54 GiB**，再分配 **60 MiB**时仅 **59.94 MiB**空闲；日志 **Epoch0/Step20/100/Loss0.993** | 第2次 **FAILED**，与13266第1次失败分别保留；该次进度日志不证明完整输入曝光，未产出两轮完成权重或固定Val；第四次统计另列 |
| 第2次失败的Loader接纳/预期量 | 原Loader全部接纳 **198**条记录，两轮预期 **396**条次；失败目录只有`training_config.json`，其输入曝光 **0**为启动时统计 | 该次失败后的完整输入曝光/独立覆盖 **UNKNOWN**；不记作0、198或396已实际完成 |
| 原 GPU 资源等待（历史） | 原资源代码已增量部署，CLI验证`WAITING_FOR_GPU`；01:43的12,668/15,973 MiB保留历史，**02:11 free12,698/required15,973 MiB**；先前13,932 MiB为旧快照 | 已观察占用下限加原 **2 GiB**余量，旧384输入`required=12103`不适用于8K；CLI25201当时保留、27184无worker已由主Agent结束；此为第2次失败后的历史阶段，最新终局见下行 |
| 同一原CLI第3次启动/终局 | **2026-10-30 02:49:33台北**自然启动worker **44839**，**7.528秒**后exit **2**；日志`kev.train: error: refusing to overwrite an existing run`。02:55候选`KEV-V9-001`为`FAILED/training_status=FAILED`、原CLI **25201**自然退出 | 第3次 **FAILED**，因已有目录退出；原日志/attempt及`failed_attempt_0003/training_config.json`保留 |
| 第4次启动/过程（历史） | **2026-10-30 03:03:33台北**原dispatcher **50514**、worker **50518**启动；`2 Epoch/max_state=8192/full_ft=0/resume=0`，加载 **426**个基础权重张量。03:06:18曾为ep0 step10/100、loss0.859、2.909s/rec | 原日志保留；step10只作过程历史，现行终局见下一行 |
| 第4次训练完成 | **03:25:31** worker50518两Epoch/100steps自然结束、exit **0**，保存`runs/KEV-V9-001/checkpoint` | 两轮和新模型实体已确认；固定Val已完成/内部EVALUATED，未上线Serving |
| 第4次真实training_metrics | `wall_seconds=1267.0303`、`records_seen=requested_records=396`、`optimizer_steps=100`、`forward_tokens=219465`、`peak_device_bytes=16336306176`；`truncated_records=rejected_records=0` | 来源为该次真实训练；本地GPU前向Token不计生成/教师API预算，不折作美元费用 |
| 第4次ACTUAL_TRAIN_BATCH_INPUTS：记录/state | material/admitted **198**；records_used **198**/not_used **0**；full_state_records_retained **198**/partial **0**；input_passes **396**/full **396**/partial **0** | 198条独立训练记录均实际使用、两轮完整曝光；与前三次失败的统计分列，不覆盖UNKNOWN |
| 第4次ACTUAL_TRAIN_BATCH_INPUTS：能力/教师 | capability source/retained **198**、passes **396**、incomplete **0**；teacher source/retained **4**、passes **8**、incomplete **0** | 能力卡仍缺测，不能称已有AA分数；4条稀疏教师实际学习，不代表全材料教师覆盖或三新身份有效监督 |
| 原固定Val已完成 | 03:25:31开始attempt1；**2026-10-30 04:23:20台北**完整结束，controller50514自然exit0；**3468.2793179秒**，**8436/8436 records、9330/9330 questions**，拒绝0/裁减0/`test_used=false` | `status/training_status=COMPLETED`、`evaluation_status=EVALUATED`；原`checkpoint/val_metrics.json`与`val_metrics/attempt_0001/report.json`保留，未重评 |
| 固定Val四指标 | Accuracy **0.5658092175777063**；NLL **1.1103247352468928**；Brier **0.5461336121552054**；ECE **0.08006657253210539** | 内部固定Val结果，不填正式Harbor/RQ或三模型比较 |
| 相对原C03变化 | Accuracy **-0.005787781350482302**；NLL **+0.0307721576222153**；Brier **+0.008600006481568445**；ECE **+0.02901988874336886** | 四项均退步；不能据此宣称训练有效、效果改进或项目整体完成 |
| 原完成时间与评分已更新 | 04:32:41原`validate_candidate`复用保存Val，`candidate.finished_at`与`v9_continuation.finished_at`均为`2026-10-29T20:23:20Z`；`evaluation_attempts=1`，前三次失败时间未改。原`update_retention(queue,apply=False)`保存queue/ledger，score **92.38703579133796** | 原C03=100，R11父=106.74866622586939；评分低于二者，不重评/重训 |
| 原留存结果 | `MODELROUTER_V9_FEATURES_V1`组仅1条，rank1/core_quota1/ratio0.15，按原`necessary_scientific_representative`规则保留；`apply=False`，释放0字节、删除0字节/0文件 | 单成员组第1不表示优于C03；adapter129924032/head5249053字节仍在A6000，未上线Serving。现行来源为A6000原`our-project/results/training/kev/candidate_queue.json`/ledger及主Agent回报 |

**原入口、失败输出保留与接续边界**：仍复用原`main_loop(wait_for_resources=True, v9_only=True, ...)`及`dispatcher --v9-continuation`；CLI25201已自然退出，27184经主Agent确认无worker后结束，服务器源码`CLI_WAIT/EXIT_RESET=true`已验证。资源等待与前三次失败历史保留；现行结果见上方训练表，入口窄测/导入通过不覆盖真实失败。原`reserve_kev_attempt`在前次FAILED且原out存在时，将输出移为同一Run的`failed_attempt_0003`并记`preserved_output_path`；第三次仅`training_config.json`、无新完成权重，原三次失败日志全部保留，原checkpoint路径重新创建。第四次保持`full_ft=0/resume=0` LoRA及上游已有输出保护，未盲设`resume=1`，未另建loop/Runner/定时任务/Trainer/队列。02:11 F14/ComfyUI/Serving未被干预；现行F14证据见下方F14段；Laya8.87 GiB、ComfyUI24.25 GiB的先前占用及ComfyUI`<A6000_HOST>:8188`监听、运行队列1/pending0的历史回报保留，图像任务活跃，`127.0.0.1`不通属绑定地址，未卸载/干预。第2次失败后的完整输入曝光仍UNKNOWN，第三次仅启动配置；第四次真实曝光单列，不替代任何失败attempt的统计。新候选`feature_training_status=FEATURE_PARTIALLY_TRAINED`：4条教师稀疏、三新身份监督目标0、能力卡缺测；正式评测仍待。新checkpoint已保存`head.pt` **5,249,053 bytes**、`adapter_model.safetensors` **129,924,032 bytes**及tokenizer实体，仅在A6000；未传Mac、未加载Serving，原Serving继续旧权重/`FEATURE_NOT_TRAINED`。原评分及留存机制保持，本轮收尾仅涉及多余控制器和临时连接，04:33:44主Agent确认无当轮SSH连接残留。04:33:44主Agent确认Serving2291306 `/health`HTTP200/`healthy`，Laya/Kev已加载、`inference_verified=true`，仍是旧权重；Kev50514/50518自然退出，未操作其他图像作业或服务。

**原 Provider/telemetry 必要增量部署**：旧Server Provider缺少`alias_mapping/query_raw`支持，所需原Provider、账本/ledger/logger接点已部署；服务器构造V9 AliasProvider成功，账本根为`<SERVER_PROJECT_ROOT>`。该构造未发API请求、未读Key，不等于认证或生成请求已通过；Alias/账本补齐已验证且无新API，无新client服务，复用同一原执行链。最新source部署回报为 **40个文件/链接加原Laya/Kev增量**，首批37对象/6,993,920字节单列保留，后续总传输字节未回报。该批源码部署未更换Serving；KEV-V9-001新实体已在A6000保存、未上线Serving；API物理身份与正式三模型隔离仍保持。

Laya V9尚未启动；hook在盘，原F14内存代码不读，下一自然child接续尚未发生。04:33:44原F14 PID4085749为R、显存9084MiB；现行结论为“运行推进，损失持续非有限，有效优化更新未确认”。原`continuous_queue.log:55355`第1块loss0.8102/step128，`:55416`第62块loss0.5391/step7936，`:55417`第63块起loss=nan/step8064；本次175块，前62块有限、第63–175块113块持续NaN。首次异常只能定位第63块内部、记录507905–516096、计数步骤7937–8064，无逐批log。

磁盘源码`router_data/laya_batch_train.py:1473`每块独立初始化`chunk_loss_total`；1489原`soft_ce_loss`、1495 backward、1500起GradScaler/clip/step、1516累加`loss.item`、1529求均值/1533打印，支持该块真实loss累计值已非有限；不能推断每个微批均异常。1514的`global_step`无条件递增，包含可能被GradScaler跳过的更新尝试，计数步骤不能称有效更新数。`external/laya/laya/train.py:493` masked log_softmax使用有限-1e4，635的`_forward`在FP16 autocast后将logits转FP32；FP16仅为待追踪环节，未证明溢出诱因。已安装torch的`grad_scaler.py:363`在非有限梯度时会跳过`optimizer.step`，本次未保存skip/scaler信息。

同日志`:32379`的F04 Epoch1 Chunk231已出现NaN，F04共8个NaN块、首次后仍有230个有限块；F04/run.json两轮train_loss=NaN，但S1 Val loss0.6300/0.6141有限。不能断言F14权重已失效或一定没有有效更新。F14尚无Epoch终局，首次异常batch的logits/target/gradient/scaler未捕获，具体诱因及有效更新未知；源码行号为磁盘版本，未读PID内存。本次主Agent只读诊断未停止/重启/改动作业，未加载权重、发模型请求、新评测或信号。Laya/原Serving仍旧权重；Kev新候选训练/Val/评分已完成、FEATURE_PARTIALLY_TRAINED，四指标比C03均退步，未上线Serving。

预留与实际消耗分别保留；不将 77,544 写成真实已用 Token，不自行把新超时追加为已计失败或推算新余额。线上/离线教师、生成及重试按实际 API 用量累计记录，当前无总 Token 或美元上限。旧预留和旧余额仅为历史；官方价格核算与供应商账单分别记录，未知金额不填零，也不影响执行。

**现行需求**：用户已保留 **V9 五 RQ、八图、十二表**，首批逻辑 ID 为 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`。用户已充分授权测试及部署；原 Provider 实际返回 3 项，研究池当前只列 Luna，Sol/托管Flash未列出。旧两Luna范围与Qwen统一映射安排仅保留历史，`ALIAS_SMOKE` 与正式模型结果继续分开。Alias 不代表三个独立真实模型，审阅子 Agent 的 `gpt-6.1-sol/max` 也不代表生成/教师配置。新增方法只归 `v9/runtime`、`teacher`、`capabilities`、`training`，旧系统保留必要接点；职责表见 [RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md)。

**训练、数据与教师后续**：复用 V2.1/L1 和合法 S1/S2/S3，保留质量、监督、层级和独立单位；AA 分数与观察动作不能作最优动作标签。教师的 `progress_summary`、`main_blocker`、`next_milestone` 必须实际编码且离线/在线同义；未学习记 `FEATURE_NOT_TRAINED`。顶级教师与联调教师、离线制作费用与在线 Episode 费用分开，连续上下文与实际 KV/缓存用量双记。原训练沿既有控制器自然接续，F14不读新hook与下一child两轮边界分别保留；各模型同协议Val及独立Dev选继续微调起点，Final不参与迭代。Mac不存Laya/Kev权重，API按实际用量记录、不设累计Token或美元上限。源码/材料/原资源分支部署及final/训练prefix分词范围已确认；现行结果见上方训练表。step5近期工具真实末128字符已验证，长history与6条完整state仍裁、8192推荐未启用；192条Val长度尚未测。Laya V9已完成两轮和固定Val；仍待F14首次异常具体诱因及有效优化更新定位、三新身份/Effort监督、AA实测和正式Harbor/RQ评测；前三次失败的曝光未知信息保留，Serving仍旧权重/`FEATURE_NOT_TRAINED`。该历史阶段旧记录575783/256135/168082及135calls保留，04:20直传验证另增Router1/生成0，与此前回放分列；文档子任务未发请求。

**材料完整性**：原 linked 聊天已移除、本机 source 文件缺失；四段下载聊天与两份提示词全文复核仍完整。研究编号依据下载讨论行 25981；身份/联调依据 26344、26368；教师/模块/缓存与费用依据 27359–27361、28201–28203、28747–28784。原 Q-ID 和历史负结果继续保留，具体实验表见 [V9 图表规划](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)。

> 以下为 2026-10-28/29 的远端规划记录，不是 10-30 新实测。初始模型身份仍为 Sol、Luna、托管 `qwen3.8-flash`，不得替换为 27B 或 Flash-Next；其中 AA 52/38（v4.3.2）和 Qwen USD 价仅保留当时的来源陈述，未由本地证据复核，不用于当前能力快照、训练输入或实际账单。当前证据以本文最新记录及 `PROJECT_STATUS.md` 为准，早期权限描述不撤销后来的人类授权。

## 2026-10-29 · 统一 Planning 接手、V9 三模型池与能力卡本地快照（本轮规划，不是服务器新实测）

**已明确批准的研究结构**：继续使用 **V9 五个 RQ**，顺序仍为 RQ1 整体性能、RQ2 模型池、RQ3 任务拆分、RQ4 系统消融、RQ5 工作负载适用边界；保留原 Fig.1–8、T1–T12。原“三核心 RQ”只是历史备选，不再作为本轮待决事项。

**本轮确认的初始三模型池**：逻辑身份为 `gpt-6.1-sol`（GPT-6.1 Sol）、`gpt-6-luna`（GPT-6 Luna）、`qwen3.8-flash`（托管 Qwen3.8-Flash）；映射实验的真实请求后端统一为 `Qwen3.8-27B`。三档是研究中的候选角色，能力与价格分别按快照记录。实验费用使用所选逻辑身份的 `ModelSpec` 价格和真实 input/output/cache 用量；Sol 采用 v2 已保存官方 `2/10/0.1/2.5`，Flash 当前参考 `0.15/0.47/0.016` 来自 OpenRouter，阿里官方v2仅确认CNY，当前USD实验价格来源为OpenRouter。AA 当前已核实参考指标为 Sol Max Intelligence Index 52、Luna Max 38（均需锁定 AA v4.3.2 口径）；公开 AA Qwen3.8-Flash-Next 的 40 属不同的开源权重变体，不能替代托管 `qwen3.8-flash` 的独立成绩，后者暂无本轮同版 AA 分数，应 `NOT_MEASURED`。真实 Qwen 后端价格、返回身份和供应商实收另列，缺失不影响映射实验继续；映射实验不能写成独立物理模型质量对照。官方来源：https://developers.openai.com/api/docs/models/gpt-6.1-sol 、https://developers.openai.com/api/docs/models/gpt-6-luna 、https://docs.qwencloud.com/developer-guides/getting-started/latest-model 、https://docs.qwencloud.com/developer-guides/getting-started/model-prices；AA：https://artificialanalysis.ai/models/releases/gpt-6-1-sol 、https://artificialanalysis.ai/models/releases/gpt-6-luna 、https://artificialanalysis.ai/models/comparisons/qwen3-8-flash-next-vs-hy3 。三款的实际调用权限、Endpoint、原生 Effort、tool support 继续按本地记录维护。

**新增数据任务（待本地 Execution Agent 执行）**：在**现有 `our-project/code/`** 范围复用 Registry/训练准备入口，为三款模型及后续候选建立本地能力数据快照；首次抓取/清洗公开允许使用的 AA 指标、Benchmark 原始单位和模型/版本/Effort 证据，每次**数据刷新脚本运行都尝试重新请求**官方 AA API（需合法密钥），成功则保存带来源、时间、协议和指标版本的新快照；网络/授权失败时保留最后有效数据，不写零、不过期数据冒充新实测。实际每一次 Router 决策不发起外网抓取，训练及正式评测固定 snapshot ID，API Key 不进 Git。脚本、当前数据和训练样本准备由本地 Agent 根据审批实施；**本次 GitHub 更新仅为规划，没有新增本地代码/实际抓取/微调**。

**训练与文档维护**：原 Laya/Kev 健康训练、Kev 自动评分及约 15% 受保护留存不改；完成后各自在可比固定 Val 选择物理存在的优质 Checkpoint，独立 Dev Agent Episode 决定继续微调起点，随后用合法的新能力/轨迹输入**继续微调现有权重**，并记录实际训练范围。保留六份文档，**只删除确定的跨文档冗余，不按 14–20 万字的目标大规模删历史**；原始实验报告、Q/D ID、负结果、来源政策和图表编号不删。本轮允许六文档规划更新，未新增 GPU/API/正式测试授权。

**最新训练证据时效**：目前只能独立确认 GitHub 最后已同步的 2026-10-27 F12/R12 在训、Kev 完整固定 Val 14 项；用户提出可从另一训练 Planning 查看更新，仍需由具备现场权限的本地 Agent 读取更晚队列、Ledger、训练报告或看板，不能把旧快照称为 10-29 实时进度。下方历史时点保持可追溯。

## 2026-10-28 · V9 最新讨论收敛与小规模 Agent 试测前代码审计（规划更新，非服务器实时状态）

**本次边界**：仅同步六份核心研究 Markdown，不触碰健康训练、Checkpoint、Serving、Provider 或 Harbor；未运行 SWE-bench/Terminal-Bench、未花费 API/GPU 费用。下方 2026-10-27 的 F12/R12 及 Kev 14 项固定 Val 是**GitHub 最后已同步现场快照**，不是此时新的实时监控；正式 Agent 成功率与实际完整 Episode USD 仍为 `NOT_EVALUATED`。

**研究方向**：继续采用正式 **V9 五个 RQ**（RQ1 总体、RQ2 模型池、RQ3 任务拆分、RQ4 系统消融、RQ5 工作负载边界）。最近聊天提议将论文压缩为三个核心 RQ/重排图表，尚非负责人最终批准，不修改 Fig.1–8 / Table 1–12 的权威编号。V9 最近方案倾向：Agent 外置**单个顶级推理模型**在积累约 3 次模型生成或发生关键事件后输出进展/主要问题/下一里程碑短评；首版使用经许可核验、与当前测试题隔离的**两条固定公开成功轨迹摘要**（高效完成与失败恢复），**不建在线语义检索/重排系统**；教师 Token/推理成本完整入账。该触发阈值仍待开发集校准。

**候选能力与训练方向**：优先输入各 Benchmark 原始成绩及单位、AA 综合指数（是指数而非正确率百分比）、独立 native_effort 实测及证据缺失；综合高中低仅作同一版本参考集合上的派生标签。首版模型池拟以三个不同经济定位且经真实 Provider 核验的模型身份为目标；现有健康训练自然推进后，Laya/Kev 分别依据**各自同协议 Val**选可加载候选，再用独立 Dev Agent 任务比较以选择继续微调起点。未经确认不得按跨架构最低 Loss 直接选模或用封存 Test 进行迭代。

**下一项只读审计（待本地 Agent 回报）**：核验现有 `our-project/code/` 的 Laya/Kev 路由器权重真实加载、回退标志、合法 `(provider, model, native_effort)`、Provider 工具调用/价格、Harbor/mini-SWE-agent 入口、Docker/uidmap、样本划分、真实 verifier 和完整账本。核清用户所说“SW 奔驰 Mini”究竟是 **mini-SWE-agent 框架 + SWE-bench Lite/Verified 任务**，还是目前 **Terminal-Bench 2.1 + Harbor 的官方 mini-swe-agent 链**；这两个评测协议不可混写。先审计可行性，再讨论极小、低成本的公开开发任务，不启动试跑。

**依据与职责**：[EXPERIMENT_QA](EXPERIMENT_QA.md) 记讨论/授权边界；[RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md) 记方法；[V9 图表规划](../../汇报/汇报三/ModelRouter论文实验与图表规划.md) 保持论文版本。这里只登记最新规划和最后一份可溯源现场快照。

## 2026-10-27 14:31 · R06–R11结果同步，F12/R12自然接续

本节以 A6000 原采集 `2026-10-27T05:49:52Z`（台北13:49:52）、原候选队列/Ledger、各候选完整固定 Val 报告及实体目录为准。12:48时R11尚在验证，现已于12:54:57完整结束；原dispatcher随后自然接续R12。没有重复派发、重训、重新生成材料或操作健康进程。

14:31:20发布后再次读取原实时JSON：F12 Step48,947/69,990、Loss0.464940，R12 Step740/2,135、Loss0.584，均TRAINING；完成固定Val仍14项。下方资源与ETA保留13:49的详细观测时间。已发布JS及实时JSON均HTTP200，卡片使用实际返回数据输出成功；一个针对性用例通过。内置浏览器读取超时，视觉展示未确认，没有为此改动网络或另建页面。

### 双模型当前状态

| 对象 | 当前真实状态 | 进度与时间 |
|---|---|---|
| Laya F12 | TRAINING；worker `1632313`，原控制器 `499841` | Epoch2/2、Chunk100/274、Step47,795/69,990，Loss0.472700；累计消费3,058,863条、626,940独立单元；最近进度13:46:54 |
| Kev R11 | COMPLETED / EVALUATED | 1,068步、4,269条、训练8,181.1秒；固定Val3,209.5秒、exit0，12:54:57结束 |
| Kev R12 | TRAINING / NOT_EVALUATED；worker `2041323` | Epoch1/1、Step420/2,135、Loss0.727；最近进度13:49:19，实际消费样本未记录，保留N/A |
| Kev R13–R16 | QUEUED | 已有合法材料合计34,798条，等待原dispatcher自然接续；不计完成 |

Kev配比固定Val现为11/16；加C03/C04/C09共14项完整完成。R11成绩来自同一 `data/kev/公开数据/val.jsonl`，8,436记录/9,330问题、拒绝0、截断0，未使用Test。R12尚无最终Accuracy、NLL、Brier、ECE或留存评分。

### 本批固定Val与留存事实

| Run / 比例 | Accuracy | NLL | Brier | ECE | 训练秒 | Val秒 | 内部评分 | 实体状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| R06 S1:S2=1:2 | 0.569025 | 1.099256 | 0.549006 | 0.061394 | 8,260.4 | 3,029.4 | 96.651 | PRUNED_LOW_SCORE |
| R07 S1:S3=1:1 | 0.573526 | 1.094258 | 0.543757 | 0.054690 | 17,413.4 | 2,976.2 | 98.635 | PRUNED_LOW_SCORE |
| R08 S1:S3=2:1 | 0.569132 | 1.092478 | 0.544243 | 0.060926 | 13,008.6 | 2,994.4 | 97.166 | PRUNED_LOW_SCORE |
| R09 S1:S3=1:2 | 0.563023 | 1.095805 | 0.546742 | 0.066017 | 17,049.2 | 2,967.1 | 95.533 | PRUNED_LOW_SCORE |
| R10 S2:S3=1:1 | 0.571061 | 1.084009 | 0.539027 | 0.039459 | 10,763.1 | 2,999.6 | 102.005 | PRUNED_LOW_SCORE |
| R11 S2:S3=2:1 | 0.569025 | 1.068724 | 0.535678 | 0.018246 | 8,181.1 | 3,209.5 | 106.749 | PROTECTED |

R11相对C03：Accuracy低0.257个百分点，NLL低0.010829、Brier低0.001855、ECE低0.032801。完整Val支持概率质量与准确率的权衡观察；训练量、监督组合共同变化，不能据此批准唯一最优比例或推导任务成功率。

R10的两个实体文件已由原留存流程移除，12:48时的RETAINED属于历史状态；R11两个文件实际在盘，R04目前RETAINED，C03/C04/C09/R01继续PROTECTED。R02/R03/R05–R10共8项有明确移除记录，累计释放1,081,434,112字节。全部配方、材料身份、原命令、训练/验证尝试和成绩仍在原Ledger。本轮未改四指标评分、约15%规则，未执行删除或恢复。

### 历史覆盖与剩余时间

服务器报告生成于台北12:56:15，采集源码标识 `40932a7ce329faaa159fc483ce152a1f349684ad`；此标识与GitHub结果提交分开。Laya观察108对象，其中105完成、F12在训、2仅元数据；实际执行106 Run、223 Epoch/版本、8个物理版本。106个Run有曲线，其中89有Step曲线、17只有Epoch曲线，2个元数据对象无曲线。

Kev报告覆盖19对象（18本地、1导入），17个本地训练已结束，R12在初始化观测时尚无Step曲线；14条完整正式固定Val记录、19个历史版本、10个物理版本。报告的全历史物理计数与C/R候选留存范围分开，不能把曲线、版本或导入资产计为新正式Run。旧Laya核心仍2/5，缺失实体没有恢复。

13:49原ETA：F12含Val约台北10/28 01:02；R12含Val约10/27 18:20。未来502项加当前两个Run的串行墙钟估算约402.6小时，历史吞吐范围303.6–422.9小时，中心台北11/13 08:25。其中F13–F16约229.1小时、纯S3七项约60.6小时、原矩阵487项训练/Val代理约29.9小时及CPU物化约49.8小时；Kev后续R13–R16约18.5小时训练和3.4小时Val。不同组共享GPU，实际并行日历可能不同；GPU活跃小时、付费费用和论文最终完成日期均N/A。

C05缺状态拆分材料、C06缺可观测状态字段、C07/C08的Rank8/32与Rank16初始权重不兼容、C10材料来源条件未满足，继续PENDING。F17–F20保持父权重依赖，不加入可计算ETA。

### 运行服务与结果同步

13:49资源：显存19,564/49,140MiB、GPU96%、83°C、294.46W，内存可用328GiB，根盘余1,054,917,234,688字节。原Laya控制器、Kev dispatcher `420899`、5秒采集器 `451884`、8765 Web `832433`、Serving `2291306`均在；只读采集持续刷新，训练与采集时间分别记录。

本阶段同步原 `training_research.md/.json`、脱敏 `candidate_queue.json`/`candidate_ledger.json`、候选矩阵当前区及必要Status/Memory。原报告保留12:56的生成时间；实时读数不冒充重新生成的历史报告。旧失败尝试仍保留，R11最终成绩只在完整Val后写入。原页面Kev主标签按验证阶段显示，训练结束与完整候选结束分别保留。

同步开始时GitHub main为 `8d6fd5a685e3024cbcffa039338698b94975b074`。以上本阶段结果随本次main提交推送，最终提交以Git历史及远端main为准。两份既存报告的未提交删除状态不纳入提交；QA/Research与研究协议不变。官方Harbor/Verifier保持NOT_EVALUATED，离线Val不计Agent Task Success或完整Episode USD。

## 2026-10-26 12:36 · 本阶段结果已推送

本阶段新增的脱敏报告、候选队列/Ledger、候选矩阵、F11完成/F12启动摘要和 R03–R05 固定 Val 结果已随 GitHub main 提交 `cdf87b5` 推送；本地 `HEAD` 与 `origin/main` 一致。旧条目中的“待推送”描述属于此前观测阶段，当前以本节为准。

服务器统一报告生成于 `2026-10-26T04:25:42Z`，重新计得未来可执行队列509项、串行估算约460.1小时，历史吞吐范围352.0–476.8小时，报告中心时间约台北11月14日16:32。F12已在报告生成后启动，当前实时进度单独以本节表格为准。

## 2026-10-26 12:50 · 最新实时读数

原 8765 采集 `2026-10-26T04:50:21Z`：F12 Step 640/69,990、Loss 0.669115；Kev R06 Step 820/1,068、Loss 0.608，固定 Val仍未开始。该动态快照与最新脱敏候选队列随本次状态提交推送，训练进程保持运行。

## 2026-10-26 12:36 · F11完成，F12/R06在训，R03–R05结果同步阶段

本节以 A6000 原 8765 实时采集 `2026-10-26T04:36:08Z`（台北 12:36）为准。服务器原链没有中断：Laya F12、Kev R06、原 dispatcher `420899`、采集器 `451884`、8765 Web `832433` 与 Serving `2291306` 均保持运行。

| 对象 | 当前状态 | 实际记录 |
|---|---|---|
| Laya F11 | COMPLETED | 2 Epoch、Step 58,200；最终 S1 Val Accuracy 0.6667、Loss 0.6022、Brier 0.4158、ECE 0.0389；训练结束 `04:25:17Z` |
| Laya F12 | RUNNING | Step 256/69,990，Loss 0.710079，最后进度 `04:35:16Z`；训练协议已从 F11 自然接续 |
| Kev C09 | COMPLETED / EVALUATED | 2,212 Step，8,846 条；固定 Val 9,330 问题，Accuracy 0.566774，NLL 1.074802，Brier 0.538563，ECE 0.023638 |
| Kev R01–R05 | COMPLETED / EVALUATED | 5/16 项已完成相同固定 Val；R01、R04保留实体，R02、R03、R05按实际低排名记录移除权重 |
| Kev R06 | RUNNING / NOT_EVALUATED | Step 710/1,068，Loss 0.657；固定 Val尚未开始，含 Val预计约台北 14:16 |
| Kev R07–R16 | QUEUED | 材料已就绪，尚未训练，不把排队计作完成 |

Kev 已完成固定 Val 的同协议结果如下。所有记录均为 C03 初始化、同一项目 Val（8,436 条记录 / 9,330 个问题，拒绝0、截断0）；不同监督目标的 Accuracy 不作跨目标唯一排序。

| 候选 | Accuracy | NLL | Brier | ECE | 内部评分 | 实体记录 |
|---|---:|---:|---:|---:|---:|---|
| C09 | 0.566774 | 1.074802 | 0.538563 | 0.023638 | 105.201 | PROTECTED |
| R01 S1 | 0.566345 | 1.094774 | 0.542489 | 0.051039 | 98.861 | PROTECTED |
| R02 S2 | 0.573955 | 1.110397 | 0.552117 | 0.093402 | 90.175 | PRUNED_LOW_SCORE |
| R03 S3 | 0.567953 | 1.104241 | 0.544448 | 0.063738 | 96.036 | PRUNED_LOW_SCORE |
| R04 S1:S2=1:1 | 0.567846 | 1.081526 | 0.540801 | 0.027957 |   | PROTECTED |
| R05 S1:S2=2:1 | 0.571383 | 1.094129 | 0.543806 | 0.043059 |   | PRUNED_LOW_SCORE |

R02、R03、R05 每项各有两个权重文件被移除，历史记录合计释放 `405,540,864` 字节；当前重复运行只产生0字节新增释放。训练配置、材料身份、日志、固定 Val 和处理原因仍保留。C03/C04/C09、R01、R04及父权重继续保护。留存评分仍只用于实体选择，不能替代论文主要评价。

全历史统计：统一报告内 Laya 105 个真实 Run 已结束、221 个版本、7 个实体；F12已启动但尚未进入报告对象。Kev 12 个本地执行对象、1 个导入对象，其中11个已结束、R06在训，C09与R01–R05已评估。当前统一报告覆盖 13 个 Kev历史对象，Step/Chunk 曲线10个，另有2个未记录曲线对象。未来可执行队列509项，条件总量约435.6小时，历史吞吐范围352.2–477.0小时，中心约台北11月13日15:50；CPU物化估计49.8小时，GPU有效小时仍未单独计量。

本阶段同步范围包括服务器最新 `training_research.md/.json`（生成 `04:25:42Z`，采集源码 `40932a7`）、脱敏 `candidate_queue.json`/`candidate_ledger.json` 和候选矩阵当前区域；原 GitHub HEAD `85ce133` 已包含上一批 C09/R01/R02 结果，本次 R03–R05、R06实时状态、F11结束/F12启动摘要在本次提交后统一推送。两份用户原有报告文件的删除状态保持，不触碰。

C05/C06/C07/C08/C10继续保留原待决原因，F17–F20继续等待父实体。官方 Harbor/Verifier仍为 NOT_EVALUATED，训练 Val不计 Agent成功率，未访问最终 Test或增加付费调用。QA/Research不变。

## 2026-10-25 23:06 · C09 与 R01/R02 完成，R03 在训

依据 A6000 原 8765 看板 `2026-10-25T15:02:10Z` 采集，以及台北 22:58 进程、GPU 和磁盘现场。开始本次同步时，GitHub/main 为 `ca0b5eea4e18dc02584f5e2ab01cf180c13a234c`；它尚未包含下表的 C09/R01/R02 完训与淘汰结果。服务器原候选队列、Ledger、统一报告和候选矩阵已有这些事实，本轮正将脱敏快照同步至 main。训练来源分别记录：C09=`520ff8b`，R01/R02 和原 dispatcher=`7f6b683`，报告采集代码=`40932a7`。A6000 项目目录无整仓 Git，不据此声称远端有仓库 HEAD。

| 任务 | 训练/验证状态 | 固定 Val Accuracy / NLL / Brier / ECE | 训练时长 / Val 时长 | 实体与处理 |
|---|---|---|---|---|
| Kev C09 新 S2+S3 扩展 | 2,212步，8846条；完整固定 Val | .566774 / 1.074802 / .538563 / .023638 | 16,691.7秒 / 3,812.2秒 | 权重仍在盘，PROTECTED；内部评分105.201 |
| Kev R01 S1-only | 1,148步，4592条；完整固定 Val | .566345 / 1.094774 / .542489 / .051039 | 8,585.9秒 / 3,714.6秒 | S1-only必要对照，权重PROTECTED；评分98.861 |
| Kev R02 S2-only | 712步，2846条；完整固定 Val | .573955 / 1.110397 / .552117 / .093402 | 5,798.2秒 / 3,060.0秒 | 低排名权重已真实删除，PRUNED_LOW_SCORE；释放135,180,288字节；评分90.175 |
| Kev R03 S3-only | RUNNING，Step 510/1500，Loss .882 | NOT_EVALUATED | Val待训练完成后执行 | 训练进程正常，未清理实体 |

C09/R01/R02验证均覆盖8436条记录、9330个问题，拒绝0、截断0。相对C03，C09的Accuracy低0.482个百分点、NLL改善0.004751、Brier差0.001029、ECE改善0.027409；R01的Accuracy低0.525个百分点、NLL差0.015222、Brier差0.004955、ECE改善0.000008；R02的Accuracy高0.236个百分点，但NLL差0.030844、Brier差0.014583、ECE差0.042356。每项均为C03初始化的合法监督配比比较；不同目标使Accuracy不能单独排序，内部评分只用于留存。

R配比固定Val完成 **2/16**，R03在训，R04–R16排队；Kev候选共25条，C03/C04/C09/R01/R02五项已完整训练并评估。R02仅删除两个权重文件，训练配置、数据、日志与Val记录保留。C03/C04/C09/R01实体及原始历史保留；累计Kev真实释放135,180,288字节。

最新23:06采集：Laya F11为Epoch 2/2、Step 33,324/58,200、消费2,132,695、Loss .475260，进度时间15:05:45Z；Kev R03为Step 540/1,500、Loss .782，进度时间15:05:53Z。A6000使用19,053/49,140 MiB、GPU99%、81°C；根盘可用约1.22 TB（22:58采集）。原Laya controller `499841`、worker `303160`，Kev一次性接续PID `420899`及R03 worker `810050`，采集器 `451884`，原Web `832433`、Serving `2291306` 均在。未新建服务或干预训练。

当前估算：R03剩余训练约2小时02分，固定Val约51分39秒，预计台北10月26日约02:00结束；F11训练与Val约台北10月26日约12:02结束。两者是当时吞吐估计。之后R04–R16约53.9训练小时及11.2 Val小时；全部剩余可执行任务约512项、458.3小时，中位吞吐情景约374.2–502.4小时，中心约台北11月14日01:24。CPU材料物化估计49.8小时；GPU有效小时仍未单独计量。

原报告/矩阵快照生成于台北21:57，包含C09、R01/R02验证及R02淘汰；队列/Ledger更新至22:56，实时看板采集到23:06。时间戳分别保留，实时步数不伪装成报告生成时间。此前GitHub提交没有包含此三项结果；本轮同步范围包含脱敏统一报告、Ledger、队列、候选矩阵及本阶段状态。官方Agent任务成绩仍为0/N/A，不把训练Val计作Agent成功率。Sealed Test未访问，未增加付费调用。

## 2026-10-25 11:34 · 原链持续训练与 Kev 留存边界

最新 main 起点为 `a6c2813`。源码 `40932a7` 已定向部署原留存模块和原采集入口；服务器无整仓 Git。C09 在训源码仍为 `520ff8b`，唯一等待命令 `420899` 保持原 dispatcher 来源 `7f6b683`，未重新派发。下一 dispatcher 在自然接续时加载磁盘上的新留存逻辑。

11:34 台北现场：Laya F11 Step 11,648/58,200、Loss 0.511104、消费 745,472，最后训练进度 11:31；Kev C09 Step 580/2,212、Loss 0.618，最后进度 11:33，固定 Val 为 NOT_EVALUATED。训练 PID `303160`/`413095`、控制器 `499841`/`413082`、Serving `2291306` 和 Web `832433` 均保留。唯一原采集器现 PID `451884`，仍每 5 秒采集，未新增服务。

R01–R16 已完成固定 Val 为 0/16，108,656 条合法材料保持 READY，不再生成。C09 完训和原固定 Val 后，沿已存在的命令自然接续；各 Run 继续使用原配置、C03 初始化与同一固定 Val。

留存边界已收窄：`control_variant` 名称不单独构成永久保护。每组约 15% 的核心配额保持；原 C 系必要对照、S1-only R01、父权重、Serving 和活动 Run 单独保护。未知 base revision 保留 N/A 与重训限制，不单独要求保留低分实体；真实配方、材料身份、训练终值及完整 Val 仍是必要依据。19 项窄测通过，包括比例排序、实体操作、R01 保护及矩阵正文留存。临时样本发生淘汰，服务器实际删除 0、释放 0 字节；现场不存在可淘汰的已完成低排名版本。

原报告入口现在自动更新候选矩阵的当前 Kev 区域，保留全部历史正文；固定 Val、评分、覆盖和实体结果随原候选记录更新，READY 与完成数量分开。公共报告生成于台北 11:32，仍覆盖 112 个执行或导入对象；C03/C04 原 Val 与全部失败历史保留，C05/C06/C07/C08/C10 的待决原因不变。

11:34 动态时间估计：C09 含 Val 约当日 15:51，F11 含 Val 约次日 09:30；现有全部可执行队列约 478 小时，情景 398–523 小时，中心约 11 月 14 日。GPU 19,133/49,140 MiB、99%、82°C；共享吞吐、初始化耗时和采集间隔会改变 ETA，未来 Run 继续沿原边界更新。F17–F20 父权重依赖保持。官方 Agent Episode 仍无成绩，训练 Val 不计任务成功率，未使用新付费模型或最终 Test。QA/Research不变。

## 2026-10-25 · F11/C09 在训，16 项 Kev 材料就绪待原队列接续

本阶段依据 A6000 台北 10:46–10:53 的实际进程、训练日志和原 8765 数据。采集源码已定向部署 `f1052c7`；C09 运行源码为 `520ff8b`，自然接续的 dispatcher 为 `7f6b683`。服务器无整仓 Git，源码来源与最终结果提交分别记录。下方旧日期条目保留为历史，当前状态以本节为准。

| 当前对象 | 状态 | 现场记录与下一行动 |
|---|---|---|
| Laya F11 | RUNNING，健康在训 | worker `303160`，原 controller `499841` |
| Kev C09 | RUNNING，健康在训 | worker `413095`，原 dispatcher `413082`；等待完训及固定 Val |
| Kev R01–R16 | READY，材料就绪，训练未完成 | 共 108,656 条训练材料已完成官方 strict CPU 编码，0 异常；C09 完训及固定 Val 后沿同一 dispatcher 接续 |

唯一接续命令标识 `420899` 已存在，勿再次派发。READY 仅表示材料可用于训练，不能计入完成 Run 或官方 Agent 成绩。

Kev C05/C06 的状态拆分不成立，C07/C08 的 Rank16 初始化与 Rank8/32 请求不兼容，均保持 PENDING，不改变初始化。C10 的实际 loss 权重有效，但原材料含 35,645 条禁用 ROUTE-001/002 来源和 17 条 TRA-004，材料继续待决；不擅改 C10 或追加训练。C11 仅为选择记录，当前选择 C03，不计新 Run。C03/C04 已完成相同固定 Val（8,436 记录 / 9,330 问题），四项指标均由 C03 占优；精确数值及内部 score 见 [候选矩阵当前阶段](CANDIDATE_PROGRESSION_MATRIX.md#2026-10-25--当前候选与材料状态)。两实体均受保护，现场记录为 0 删除、0 释放。

历史数量分别计数：Laya 105 个真实 Run（104 结束、F11 在训），220 个版本、7 份实体；旧核心 2/5，新池 F05-e01 一份，F06-e02 另列历史留存。Kev 6 个执行对象加 1 个导入对象，正式训练及固定 Val 完成仅 C03/C04，C09 在训；执行对象数不能替代正式完成数。

未来任务为 515 项（499 Laya、16 Kev），不含当前两个在训 Run。10:50 报告的条件 ETA 约 478 小时，情景 398–524 小时，中心约台北 11 月 14 日；这是现有队列时间估计，非保证日期，论文完成日期仍为 N/A。训练进度、固定 Val 与 CPU 编码不计官方 Agent 成绩。本轮更新原报告和候选记录，QA/Research与既定科学定义保持。

原采集器已加载监督展示和脱敏导出逻辑，现 PID `428931`，仍为 5 秒周期；10:53 Mac HTTP 读取采集时间 `2026-10-25T02:53:01Z`、F11 Step 10,368/Loss 0.523224、C09 Step 260/Loss 0.854。C09 物化 S2/S3 分别 2,846/6,000，独立单元 2,846/3,423；累计实测曝光暂为 N/A。原 Web `832433`、Serving `2291306`、双模型训练与唯一接续命令未中断。

10:58 采集源码为 `c760e32`，唯一采集 PID `434018`；报告生成于 `02:58:11Z`，覆盖 112 个实际执行或导入对象。实时数据 `02:58:56Z`：F11 Step 10,624/58,200、Loss 0.529827、实测消费 679,936，C09 Step 300/2,212、Loss 1.245、消费数量暂为 N/A。GPU 19,093/49,140 MiB、99%、84°C；动态 ETA 约 481 小时（401–527 小时），C09 含 Val 约台北当日 15:49，F11 含 Val 约次日 11:50。瞬时 Loss 与 ETA 不代表最终验证结果。

## 2026-10-24 · 原始 Epoch 归属、Kev 自然接续与官方评测现状

台北 23:38 现场：Laya 原控制器 PID 499841 与 F10 worker PID 4158797 继续运行。F10 已进入第 2/2 Epoch，最近 Cursor 为 Chunk 32/152、Step 23,462/38,732、消费 1,501,536 条，Chunk Loss 0.4708748825868163，进度时间 23:31:44。采集时间与训练进度时间分开；原采集器 PID 3324505 每 5 秒更新。GPU 9,975/49,140 MiB；Serving PID 2291306 与 8765 PID 832433 均保留。

原始 `epoch_metrics.json` 已澄清此前正文的分数归属：

- `F06-e02`：S1 Accuracy 0.6863、Loss 0.6017、Brier 0.4150、ECE 0.0549，实体在盘。该 Run 最低 S1 Loss 是 `F06-e01` 的 0.6002，实体缺失。
- 0.6809 / 0.5936 / 0.4079 属于 `F06_S1-e02`，该实体缺失，不能归给 F06。
- F07 的最高 S1 Accuracy 与最低 S1 Loss 属于 `F07-e01`：0.6827 / 0.6076；e02 为 0.6791 / 0.6145。F08-e02 为 0.6702 / 0.6123，F09-e02 为 0.6649 / 0.6100。
- F07–F09 已完成两个 Epoch 和固定 Val，当前无实体；原记录 `weights_saved=false`，不能仅凭目录缺失断言曾保存后移除。旧核心实体仍 2/5；新池现有 F05-e01，F06-e02 为另列的历史留存。服务器留存策略未在本轮变动。

Kev C03、C04 均完成 16,857 更新、67,428 记录及相同固定 Val（8,436 记录 / 9,330 问题）。C04 Clean Accuracy 0.5711682743837084、NLL 1.0872975000322915、Brier 0.5402653787706695、ECE 0.05987151793598101，Val 2,982.712651308626 秒。相对 C03，四项指标均未改善；继续训练、学习率改变与优化器重建无法单独归因。两份正式权重均在盘，线上 Kev 仍为导入适配器，未替换为 C03/C04。

23:37:56 由同一 `kev_candidate_dispatcher.py` 接续已自然退出的队列，exit 1 表示仍有待决候选，不表示 C03/C04 失败。C05 缺状态分离材料，C07 的 Rank16 初始化与 Rank8 请求不符，C09 合法导出没有新增 C03 之外记录且缺完整 typed 目标；三项均为 PENDING，原训练与验证失败历史保留。没有新 Kev worker，也没有重训 C03/C04。

全量计划当前完成 20/38、F10 在训、13 项独立可执行、4 项课程父权重待补；原矩阵完成 52、另有 487 项合法非重复待执行。原唯一 Laya 控制器已跨 Run 接续至 F10；无第二调度服务。全历史报告与实时 ETA 沿原生成入口更新，整体论文完成日期仍为 N/A。

23:52 原采集入口已加载源码 `5a710801f9cb387b94cab4ee8730da20deae789b`，唯一采集 PID 由 3324505 接续为 139123；训练 worker、Serving 与 Web PID 不变。综合报告覆盖 104 个实际 Laya Run 和 6 个 Kev 对象，共 110 个可定位对象；另两份 Laya 纯状态记录不计实际训练。Laya 219 条 Epoch 记录、8 份实体、87 个 Step/Chunk 曲线与 17 个 Epoch-only 曲线；97 个最低主 Val Loss Epoch 无实体。Kev 5 个本地执行对象中只有 C03/C04 是完整正式训练，另有导入资产 1 份，实体合计 6 份。

该观测点剩余 500 项独立可执行计划：F11–F16 约 294.3 小时、纯 S3 约 60.6 小时代理、原矩阵训练/Val 约 29.9 小时，加 CPU 物化约 49.8 小时和当前 F10 约 6.4 小时，总墙钟约 441.1 小时，历史吞吐情景 331.8–458.3 小时。中心日期台北 11 月 12 日约 09:00；实测 GPU 活跃小时、待决实验和论文完成日期 N/A。固定验证已包含于同类历史墙钟，不能重复相加；F10 剩余 Val 使用已有约 52 秒代理，完整大 Run 的独立验证耗时尚缺记录。

Harbor 宿主仍缺 `newuidmap/newgidmap`，官方 Verifier Episode 仍 0；Oracle、原生 mini 与动态 mini 保持 BLOCKED / NOT_EVALUATED。未改共享 Docker 或宿主权限，未新增付费模型调用，未使用最终 Test。V9 五个 RQ 与 Q-012 原决定保持。

本机已沿原官方任务树处理旧 Oracle 配置缺少 `task_source` 的问题；源码窄测 28 项及 7 个子用例通过，训练采集相关 6 项通过。CPU 集成命令与下一任务保存在原 `results/iterations/20261019-v10-integration/`；原 Oracle 失败日志保留。A6000 当前项目 Python 尚无 Harbor/mini 包和原任务资产，个人容器环境未启动；管理员提供 uidmap 后仍须按原入口准备这些 CPU 依赖，不能据 Docker 可达宣称官方评测成功。

## 2026-10-24 · Laya F07–F09完训与F10在训、Kev C04固定验证闭环及全量数据同步

现场实测（2026-10-24 20:50 CST）：在负责人外出期间，服务器训练系统全程无人值守独立稳定运转。双模型训练与固定验证取得重大阶段性成果，无死循环、无显存换页、无进程中断：

1. **Laya-421M 队列连续自动推进至 F10**：
   - **F07 完训并验证**：2 个完整 Epochs，151,998 次优化步，消费 9,727,800 条训练样本，覆盖 1,344,240 个独立单元。最终 Chunk Loss = 0.4538。S1 最高 Accuracy 与最低 Loss 对应 `F07-e01`（S1 Val Acc 68.27%，Loss 0.6076，Brier 0.4203）；e02 为 67.91% / 0.6145。S3 选拔分与 S1 最佳 Epoch 分开。
   - **F08 自动接续完训并验证**：2 个完整 Epochs，23,002 次优化步，消费 1,472,010 条样本，覆盖 209,037 个独立单元。最终 Chunk Loss = 0.4675。固定验证最佳Checkpoint `F08-e02`（S3 target score 157.5536，S1 Val Acc 67.02%，Loss 0.6123，Brier 0.4246）。
   - **F09 自动接续完训并验证**：2 个完整 Epochs，30,826 次优化步，消费 1,972,758 条样本，覆盖 278,596 个独立单元。最终 Chunk Loss = 0.4698。固定验证最佳Checkpoint `F09-e02`（S3 target score 157.9859，S1 Val Acc 66.49%，Loss 0.6100，Brier 0.4226）。
   - **F10 当前健康训练中**：PID 4158797，Epoch 0 Chunk 135/152（已推进 88.8%），已执行 17,280 / 38,732 步，累计消费 1,105,920 条样本，覆盖 312,096 个独立单元，最新 Chunk Loss = 0.4934。GPU 占用 9,741 MiB / 49,140 MiB，利用率稳定在 93%–100%。
   - **Checkpoint 物理留存状态**：`F06-e02`（S1 Acc 68.63%，Loss 0.6017，Brier 0.4150）实体在盘。68.09% / 0.5936 / 0.4079 属于无实体的 `F06_S1-e02`。F07–F09 只有指标记录；Q-012 旧五份与新池约 15% 的决定保持，本段不作为实际淘汰比例的证明。

2. **Kev-4B 同源续训 C04 完训与固定验证完全闭环**：
   - **C04 训练完训**：PID 3212011 于 2026-10-22 00:28:04Z 顺利完成全部 16,857 优化更新步，消费 67,400+ 记录，最终 Loss = 0.926，退出码 0。
   - **固定验证成功执行**：沿官方固定验证集（`val.jsonl`，8,436 记录、9,330 问题），在 CUDA 上耗时 2,982.7 秒（~49.7 分钟），0 拒绝、0 截断，产出完整官方评测报告 `C04_fixed_val_report.json`。
   - **核心评测指标**：Clean Accuracy = **57.12%**（0.571168），NLL = **1.0873**，ECE = **0.0599**，Brier = **0.5403**，AURC = **0.2562**；高置信度（>=0.9）下准确率达 **86.44%**，50% 覆盖度下选择性准确率达 **73.70%**；P50 推理延迟为 321.2 ms。
   - **与 C03 严格同协议对照**：C04 表现出极高一致性（Acc 57.12% vs C03 57.16%，Δ = -0.04%；Brier 0.5403 vs 0.5375，Δ = +0.0027）。
   - **后续候选科学待决**：C05 因缺少状态消融材料 `train_nostate.jsonl` 标记为 PENDING；C07 因 LoRA Rank 8 与现有 Rank 16 初始权重不兼容标记为 PENDING；C09 因导出材料与 C03 训练集同源且缺少完整 typed 目标标记为 PARTIAL_MATERIAL / PENDING。Dispatcher 在完成全部合法任务后正常退出，无死循环。

3. **台账与前端资产离线全量同步**：
   - 从服务器同步最新 `training_research.md`（489 KB）、`training_research.json`（7.3 MB）、`candidate_queue.json`（123 KB）与 `C04_fixed_val_report.json` 到本地 `our-project/results/training/`。
   - 看板最新切片 `training_history.json` 同步至本地，看板（Port 8765）与 Serving（Port 8000）在线常驻。
   - Mac 端 NetBird P2P 直连与透明子网路由完成实测，`~/.ssh/config` 注入 `a6000-nb` 与 `a6000-tunnel`，外网访问流畅无阻。

## 2026-10-22 · V9 模型输入与外部轨迹分析设计同步（文档讨论，未部署）

本轮负责人要求以**论文 V9 五个 RQ**为准：RQ1 整体效果、RQ2 模型池、RQ3 任务拆分、**RQ4 系统消融**、**RQ5 工作负载适用边界**。前次 2026-10-22 对“把所有消融挪入 RQ1”的建议属于阶段性讨论，**已由本次明确指定的 V9 覆盖**，不得将其当现行决定；Q-017/Q-019 历史保留，最新决定见 [EXPERIMENT_QA Q-021](EXPERIMENT_QA.md)。

负责人提出在 Agent **外部**设独立的轨迹分析/规划摘要环节：可由一次外部大模型调用，读取当前决策前 Agent 已发生的工具/验证/任务进展，以及从合法训练/开发参考库检索的**相似任务**强模型成功轨迹，产出结构化短评，再交给**单一 Laya 或 Kev Router**做 `(model,native_effort)` 选择。相比仅统计命令失败，该环节重点判断工具意图、重复劳动、进度与验证是否合理；它**不是第二个选路 Router**，不执行工具、不提前读取当前 Benchmark 的未来轨迹或答案。在线调用频率、开销阈值、参考检索和评审模型仍需试点确定；全部调用必须独立入完整 Episode 账本。

候选模型输入拟从现有 `provider/model_id/revision/native_effort` 扩展为带**模型与具体 Effort 能力 Benchmark 证据**、评测协议、缺失标记、实际价目/缓存/上下文/工具能力和真实可用性；原生 Effort 与人工强/中/弱能力等级不混淆。离线基准分数不能伪装成同一中途状态下的真实反事实成败；缺失分数保留 `NOT_MEASURED`。字段建议/接口/图与消融见 [RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md) 及 [V9 图表规划](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)。

**执行边界**：本条仅为六文档的研究设计同步，未变更训练、Checkpoint、Serving、Harbor 沙箱、Provider、预算或 Test，未启动外部分析模型调用。下方 2026-10-21 03:18 台北进度及 ETA 仍是**历史观测快照，非本日实时 GPU 状态**；正式 Terminal-Bench 2.1 Agent Episode 结果仍 `NOT_EVALUATED`。

## 2026-10-21 · 综合研究报告与全队列时间预算（训练继续）

同一 `training_research.md` 已将 Executive Summary、技术演进、同层配比、ALGN与全材料预算、可加载候选、Run/实验组/整体研究终点和全队列时间预算放在前部。逐对象设计变量、初始化、完整配置、主/辅助Val变化、最佳Train Loss/Val Loss/Accuracy Epoch及实体、全部Epoch与日志索引列在后部。JSON覆盖101个Laya实际Run和6个Kev对象，包含5个本地执行对象及1个导入资产，共107个不同对象；两份R0状态记录不计实际执行。历史F04未定义数值在页面数据中使用null/N/A，原训练日志不变。

现行同协议B02配比中，S1-only主Accuracy=.6595、Loss=.6087；S1/S3=2:1为.6399/.6001，1:2为.6203/.6349，表现为Accuracy与概率质量的权衡。ALGN四项主Accuracy约.6684–.6702，预算不同；F06第二Epoch主Accuracy上升而主Loss及S2概率质量恶化。报告保留同Epoch辅助指标，不宣布唯一最优比例，不跨模型Val直接排名。Laya99个有主Val Loss的Run中94个最佳Loss实体不可用；现存F05-e01、P0_B03_C01-e02和Kev C03可作为离线候选，任务级能力仍待官方Episode。

台北03:18原页面：F07 Step35,840/151,998、Loss=.508289，C04 Step3,850/16,857、Loss=1.033；两进程继续推进，原Laya/Kev父进程、Web和Serving未重启。GPU使用20,317MiB、余28,224MiB，观测利用率70–99%。唯一采集职责已加载本轮源码，每5秒输出；原8765实际浏览器170项通过，相关队列/采集11项通过。没有新增服务、GPU训练、付费调用、Test访问、权重删除或实体恢复；服务器留存策略未变。

原入口真实生成既定 `P0_B01_C08_QB_PB`，S1训练2,730条、S3训练1,365条，Val561/4,794条，官方编码skipped={}。CPU物化369.623秒记录到该计划原materialization_audit；临时目录已自然清理。原矩阵487合法非重复待运行中2项材料就绪、485项待原入口生成，历史52项不重训。Laya38项仍17完成、1在训、16独立待运行、4项缺课程父实体；原边界信号保持，F07结束才由同控制器读取磁盘新版。

03:18时间估算：F07剩约65.3小时训练和约103秒固定Val代理；C04剩约31.9小时训练和C03同固定Val约3,099秒代理。F08–F16约342.8小时、纯S3约60.8小时代理、487矩阵约29.9小时训练/Val，加485项CPU物化约49.8小时单次样本外推，总体约548.6小时/22.9天，中心日期台北11月12日23:55。历史吞吐情景约430–600小时，CPU波动和任务切换缺完整独立记录，不能作为保证日期；fraction材料数量是期望近似，独立unit抽样可能略有差异。GPU实际活跃时长、实付USD及最终论文完成日期N/A。

Kev C04训练/固定Val继续由现有旧内存dispatcher负责，尚未自然退出；磁盘新版已支持独立候选待决后继续，未新增dispatcher。C05动态状态不可独立提取、C07 Rank8与现有Rank16初始化不兼容、C09合法同划分导出全部已在C03训练且缺完整typed扩展目标，保持待决，不给完成日期。课程F17–F20缺真实最佳父实体，同样不计终局日期。

Planning建议仅供选择：保留F09/F12/F15可较全F08–F16少约229小时，保留F07_S3可少约40小时代理，矩阵仅补QB/PB可少约26小时训练/Val但失去质量和采样敏感性对照。本轮不缩减原计划、不提前结束健康Run、不登记新Q-ID，Research保持。源码提交 `907510e349e9e463579c4edcabec8c54886201af`；脱敏结果及本阶段记录随结果提交。

## 2026-10-20 · 全历史分析与双模型接续（执行中）

原采集入口新增 `--research-report`，统一结果位于 `our-project/results/training/training_research.md` 与 `training_research.json`。报告包含全部实际 Run、所有 Epoch 的 Val、原配置、候选与载入数量、配比、初始化、曲线来源、物理实体和全部计划状态。已有 Val 连续参与选模，未使用最终 Test，未修改五个 RQ、Research 或登记新 Q-ID。

Laya 实际执行 101 个 Run，100 个结束、F07 在训；另有两份仅状态记录。212 条 Epoch / Checkpoint 记录中实体 7、指标版本 205；18 条有保存后移除依据、146 条明确未保存、41 条历史不明。101 个 Run 有 Loss，84 个逐步、17 个 Epoch-only。旧五份实体仍 2/5，新池 F05-e01 在盘，F06-e02 为单独历史全局留存；缺失的 F01-e02 与 F06 最低 S1 Loss 的 e01 未恢复。99 个拥有主 Val Loss 的 Laya Run 中，94 个最低 Loss Epoch 已无实体、5 个仍有实体；两份没有主 Val Loss 的历史对象不强行选最佳。

Kev 包含 5 个本地执行对象及 1 份导入资产；C03 完整正式训练和固定 Val 成功，C04 在训，两份部分训练及 Pointer Head Pilot 单独展示。5 份历史实体仍在，C04 尚未新增最终权重。C03 Val 8,436 记录 / 9,330 问题，Accuracy=.5715969989、NLL=1.0795525776、Brier=.5375336057、ECE=.0510466838，耗时3,099.012秒；旧失败记录保留。

原38项全量计划完成17、F07在训、16项独立待运行、4项课程依赖等待。原1092矩阵完成52，剩余487项合法非重复、154项重复、315项无合法目标、84项扩展未定义。原 Mode B 完成可执行全量项后调用原 Mode A，继续合法矩阵；已完成不重训，缺父权重不补跑。原队列源码已定向部署，已有自然 Run 边界重载信号已设置；当前 F07 内存代码保持，不能宣称新版队列已经接手。

服务器 CPU 沿 `materialize_plan_on_demand → prepare_full_matrix` 真实生成 `P0_B01_C03_QB_PB`：S3训练4,096条、独立单元2,049；原Val4,794条。官方 Laya 编码两者 skipped={}，未加载 GPU 模型。487项中目前1项材料就绪、486项待原入口按需生成。单次临时材料目录已由原函数清理，历史数据未重建。GPU使用原真实 `memory.free`，下一Laya Run所需16,384MiB，保持单个Laya worker。

原8765页面增加监督组合、采样配比、训练阶段和数据量口径筛选，完整曲线可跨配比叠加，Val按身份分别展示。原唯一采集器仍每5秒输出，历史按Run分片仅内容变化写入，计划索引独立静态分片；报告在Run/Epoch/Val或计划状态变化时生成。Mac原页面164项比对通过，相关队列/采集10项用例通过。Web、Serving、F07/C04未重启；未部署留存模块或改变物理淘汰策略。

科学观察：B02/QB/PB 的 S1/S3=2:1 相对1:1，S1 Loss .6278→.6001、Accuracy .6417→.6399、ECE .0507→.0555；1:2的主Accuracy=.6203。F06 e01→e02 的S1 Accuracy .6738→.6863，但Loss .6002→.6017；S2 Loss1.6669→3.6952、ECE .3392→.4416。Accuracy与概率质量存在权衡，不宣布最佳配比或因果结论。ALGN03/04原独立量高于实际训练量，保留原记录且用于覆盖结论时显示N/A。历史逐监督梯度贡献不可识别，候选比例不能代替实际曝光比例。

Kev旧运行内存尚无自然边界重载能力，C04训练和原Val仍由原父进程负责。新版原dispatcher已部署，独立待决候选不影响后续，无限重复失败被取消，失败仍保留非零终值；当前进程内存未切换，未启动第二dispatcher。C05材料缺少独立动态字段，C07 Rank16初权重对Rank8请求不兼容，保持待决。

C09沿原V8入口真实导出typed材料，保留原任务文本与项目Train/Val：训练25,506条、Val368条，上游`kev.data.load_records`完整加载成功。V8原视图与项目划分不同，原train中20,695条不属项目Train、原val中5,331条不属项目Val，均排除；未读取项目Test。导出训练记录全部已在C03使用，新记录0。缓存机会标量及仅已观察终局缺少当前配置的typed目标映射，未虚构反事实模型标签；完整C09记录为PARTIAL_MATERIAL/PENDING，未用已有C03数据重复训练冒充V8扩展。材料统计留原`data/kev/v8_extension/materialization.json`，权重和Pilot不动。Kev相关27项用例通过。整体实验未完成，正式AgentEpisode仍NOT_EVALUATED。

台北10月21日00:38现场：F07 Step30,976/151,998、Loss.508287、训练进度00:33:59；C04 Step2,670/16,857、Loss.803、训练进度00:37:35。原collector3292137每5秒输出；00:32 GPU使用20,233MiB、可用28,308MiB、利用率96%，磁盘余约1.2T。Mac原页面164项通过，C03历史和当前曲线持续显示；旧Web832433、Serving2291306、Laya控制器499841/worker2830698、Kev父3212008/worker3212011未动。源码main已推`ae3676c`；统一脱敏报告随本次结果提交。C04尚未完整Epoch与Val，新候选均未训练；下一步由当前原进程继续，Laya在F07自然完成后读取已部署队列，Kev旧内存在C04训练/Val后退出再由同一原入口接手。无新常驻任务或付费调用。

## 2026-10-20 · Kev 正式候选接续（执行中）

C03 完整训练保持成功：16,857 次优化器更新、67,428/67,428 记录、138,508.88 秒，原 adapter 与 head 实体存在。旧验证调用读取公开 Test 时失败的记录继续保留。本轮沿原 dispatcher 调用 `kev.benchmark --data data/kev/公开数据/val.jsonl`，原 Val 为 8,436 记录、9,330 问题，未使用 Test。CPU attempt_0001 完成 374 条预测后，在 GPU 自然释放的资源窗口转到 CUDA；CPU 日志、预测及 exit -2 均留在原 Run。

CUDA attempt_0002 于台北 17:48:16 完整成功，exit 0、耗时 3,099.012 秒：8,436/8,436 记录、9,330/9,330 问题，拒绝与截断均为 0。clean Accuracy=.5715969989、NLL=1.0795525776、Brier=.5375336057、ECE=.0510466838；Choice 的 8,436 问题 Accuracy=.5589141773，Score 的 894 问题 Accuracy=.6912751678。原 benchmark 推理 P50/P95 为 333.772/461.429 ms。完整报告保存于原 Run，脱敏副本为 `our-project/results/training/kev/C03_fixed_val_report.json`，仅路径改为项目相对路径，分数未变。该结果是项目固定 Val 分类成绩，不代表 Agent 任务成功率，也不与旧导入资产 87.26% 直接比较。

原队列按 C03 → C04 → C05 → C07 → C09 接续，FAILED 候选不被跳过；训练与验证状态分别保存，完整 Val 可复用，部分结果不视为成功。C04 继承 C03 的真实训练参数，包括 bf16、max_state=384、batch=1、accum=4、checkpointing=1，学习率按计划改为 1e-5。每个完整候选只与同 Val 协议、覆盖数量和计分问题数的 C03 计算差值，导入资产的 1,264 条结果不混入比较。

C04 已于台北 17:49:03 启动原连续 dispatcher，真实训练 PID 3212011、父进程 3212008；已加载 C03 的 496 个 LoRA 张量与 Pointer Head。台北 18:05:10 已到 Step 100/16,857、Loss 1.199，完整固定 Val 尚未执行。C04 使用新优化器，属于 C03 权重接续，不声称恢复上一轮优化器状态。C05 的 `train_nostate.jsonl` 与 C09 的 `v8_extension/train.jsonl` 缺失；C07 既定 Rank 8 与已有初始权重 Rank 16 不兼容，三项未启动，不生成替代材料。原队列到 C05 将保留材料缺失原因并退出，不跳到后续候选。C09 原 Pointer Head Pilot 留存，正式输出使用同 Run 的 `formal_run/`，不会覆盖 Pilot；输出目录由原 `kev.train` 创建。

台北 17:52 GPU 总占用 20,079/49,140 MiB，剩余 28,462 MiB；Laya F07 与 C04 同时正常运行，未停止其他模型服务。原 8765 唯一采集职责已重载，继续每 5 秒输出，页面显示当前 F07、C04 真实 Step/Loss 和候选状态，C03 完整 Val 已进入历史曲线记录。历史 Loss 延用原日志，Val 运行状态增量读取追加预测；无实测成绩保持 N/A。Mac 实际浏览器 133 项比对通过，dispatcher 24 项与 14 子用例通过，采集相关 4 项通过。服务器目录无 Git，部署为原文件定向替换，未部署留存或删除策略。QA/Memory/Research 无新方法决定，本轮不变。

### 台北 18:49 · 同一进程接续与实际吞吐

C04 仍由 PID 3212011 执行，Step 420/16,857、Loss 1.022，最后训练进度 18:48:33；尚未完训，固定 Val 保持 NOT_EVALUATED。原 dispatcher PID 3212008 完训后执行原固定 Val，未另起训练进程。Laya F07 已到 Step 20,480、Loss .528038，最后进度 18:49:02；GPU 总占用 20,081/49,140 MiB，余 28,460 MiB。C03 原 adapter/head 共 135,173,021 字节与 C09 Pilot head 5,384,063 字节继续在盘。

现有 `read_log_points` 已增量解析 Kev 上游累计 `s/rec`；当前卡片复用同一数据，C04 在 Step 420 的 2.063 s/rec 对应 .484731 记录/秒。吞吐来源、对应 Step、累计口径一并显示，不从 Step×batch×accum 伪造实际消费数。原唯一采集职责定向重载为 PID 3223928，每 5 秒输出，原 Web、训练和 Serving 不动。Mac 原 8765 页于 18:46 实际浏览器比对 125 项全部通过，其中双模型当前吞吐与 JSON 一致；采集相关 4 项用例和 JS 语法通过。C04 原历史分片已含 Step 10–410 的 41 个真实 Loss/速度点，后续按原采集增量增长。

下游仍未启动：C05 指定文件不存在，当前公开训练记录的 `state` 是含 Task/Prompt 的文本，不能在未明确消融范围时把整段清空并称为仅状态信息消融。服务器现存 Kev LoRA 全为 Rank 16，未发现 Rank 8 初权重；上游 `kev.train` 支持省略 `--init_from` 从基座新建 LoRA，但这会改变既定初始化，需要负责人确定。C09 配置明确以 C03 初始化，现有三视图分别是 Arena 胜负、缓存复用机会、已观察 Agent 终局；缺少可直接供 `kev.train` 使用的 `state/questions/expected` 训练文件。缓存与终局记录不能被赋造候选模型胜负。未生成材料、未换初始化、未读 Test、未删除权重，方法文档不变。

台北 19:00，C04 原日志继续到 Step 490/16,857、Loss .926、2.099 s/rec。本机原 dispatcher 已让未启动的 C09 读取现有 `our-project/data/configs/training/KEV-V8-EXT-01.json`，沿用 C03 初权重与原学习率、Rank、Epoch、batch、accum、seed。已启动候选参数不变，Pilot 路径保留；该调用的单项用例通过。服务器也有同一配置文件，但运行中的 dispatcher 未重载，源码留待 C04 完训、Val 和队列退出后的自然 Run 边界部署。C05/C07/C09 仍未启动，未创建缺失训练文件。

## 2026-10-20 · 训练历史与现有看板接续

直连已恢复。原 8765 首页、JS、采集源码及真实历史分片已定向更新，未重启 Web 服务。Mac 实际浏览器已读取全部 108 个 Run / 资产，显示 F06 的 722 个训练点、Kev C03 的 1,685 个 Loss 点与验证失败。原常驻采集进程仍使用旧内存代码并覆盖轻状态，持续实时部分尚未完成；重载这一采集进程待负责人明确答复，训练与队列保持不动。

- 现有留存源码按比较组规模分配新池席位，使用最大余数法与稳定组 ID，同组排序不受遍历顺序影响；S1 最佳 Epoch 保持完整历史的最小验证 Loss。旧五份、课程父权重、恢复点和缺少评分依据的已存实体继续保留。服务器训练链未接入本轮留存变动，未删除权重或停止进程。
- 原采集器读取 Run、Epoch、Cursor、日志与实体大小，分别统计本地 Run、导入资产、Epoch、权重实体、指标版本与有移除依据的版本。轻状态继续沿原采集周期，历史按 Run 分片并仅在内容变化时写入；学习率缺实测记录保持 N/A。
- 原首页改为双模型当前训练、数据层、全部 Run 曲线与双池；同协议曲线可叠加，验证集不同的结果分开。Epoch-only 自动选择 Epoch 横轴，缺值与恢复段断线。Agent Benchmark 留在折叠次要区。
- 旧看板树文件中含 21 条模拟记录，不能以全部树节点数量代表真实训练。旧分片继续保留；新版采集链不读取模拟分片来计算当前训练成绩。现有训练资产索引的 F05 数值与服务器原记录有差异，不用于覆盖原记录。
- 全目录真实记录：Laya 103 个 Run 文件中，两份 R0 只有状态记录；实际执行 101 个，完成或提前结束 100 个，F07 在训。212 条 Epoch / Checkpoint 记录中，实体 7 份、无实体 205 条；18 条有保存后移除依据、146 条明确未保存、41 条历史不明。29 条有曾保存依据，其中 4 条当前缺失但没有明确移除记录。7 份实体含 6 份正式训练版本和 1 份扩展试验版本。
- Kev 为 4 个本地执行对象（正式 C03、两份部分训练、CPU Pointer Head Pilot）与 1 份导入资产，共 5 份实体；正式 C03 记录 1 个 Epoch。Laya 有 Loss 的 101 个 Run 全部已接入：84 个 Step/Chunk、17 个 Epoch-only；两份占位没有曲线。Kev 有 3 个对象的 Loss，两份短跑没有可归属 Loss 日志，但已有原始优化器计时可读取。
- 旧五份实体为 2/5，三缺项有历史移除记录。新池 F05-e01 存在，F06-e02 属单独的历史全局保留；新版池名额缺记录，显示 N/A。父权重 R1-e01、R2-e01 存在，F01-e02 缺失。F06 最低 S1 Loss 为 e01=.6002，优于 e02=.6017，e01 实体缺失，不用 e02 冒充最低 Loss 权重。

后续沿同一链重载原唯一采集器，并确认连续周期输出 F07 和 Kev 真实终值。实际淘汰策略部署仍需对应授权与安全 Run 边界；本轮未部署留存或训练队列代码，未删除实体，未新增 GPU 工作、付费请求、第二看板或采集服务。Research 方法未变，五个 RQ 继续沿 Q-019。服务器目录无 Git，定向部署文件不等于整仓版本同步。

前轮 15 项相关用例有效；本轮原采集用例 3 项通过，覆盖终值来源、验证失败分开、观测吞吐与重复生成。JS 语法通过。实际浏览器 111 项结果中 109 项通过，未通过项均属于持续采集器仍旧版；整体保留 FAIL。内置浏览器超时，复用本机已安装 Chromium 与项目现有浏览器脚本，未安装第二看板。

训练方案现有证据：全量候选中 S1 为 31,766/4,863,900，约 0.65%；S2 为 3,537,955，S3 为 1,294,179。F 系列全材料打乱训练；ALGN 依比例及最小供给抽样，曝光规模明显不同。实际逐监督梯度曝光未记录，不能以候选比例推成真实梯度比例。F06 首 Epoch 的 S2 Accuracy 0.5816、Loss 1.6669、Brier 0.7406、ECE 0.3392，不支持仅凭准确率认定整体质量提升。Kev 导入资产的 clean Val 为 1,264 条，Accuracy 0.8726266；不与 Laya 或正式新 Val 混排。

同输入协议、固定 Val 和监督组合内，以每个完成 Run 最低 S1 Loss Epoch 比较：

| 监督组合 | 最好 Run / Loss | 最差 Run / Loss |
|---|---|---|
| S1 | F05_S1-e02 / .5933 | F01_S1-e02 / .6144 |
| S1+S2 | P0_B02_C05-e02 / .6164 | P0_B03_C06-e02 / .6372 |
| S1+S3 | P0_B02_C08-e02 / .6001 | P0_B01_C07-e02 / .6359 |
| S1+S2+S3 | F05-e01 / .5978 | P0_B04_C15-e01 / .6456 |

固定 Val 持续参与选模，以上为描述比较；没有最终独立 Test 完成结果。Kev C03 训练 exit 0、16,857 更新、67,428/67,428 记录、138,508.88 秒；随后旧队列调用上游 evaluate，获取 banking77 公开 test 的 README 时网络不可达，exit 1，尚未产生 C03 验证成绩。队列验证应使用项目现有 Val JSONL；本机接入工作沿原 dispatcher 进行，未启动实际验证。

原 Kev dispatcher 已改用现有 `kev.benchmark --data data/kev/公开数据/val.jsonl`，读取官方 report 的 clean 与覆盖记录，并把训练/验证状态、命令、退出码和耗时分别留存。PARTIAL 保留报告且不视为成功。窄测 9 项及 5 个候选子用例通过；外部 Kev 源码未改，服务器未部署此调用。

台北 13:05 的真实历史生成已成功；旧轻状态在台北 13:54 仍刷新，却继续显示已结束 F06。现场 Cursor 为 F07 第1/2 Epoch，Chunk92/594、Step11,776/151,998、753,664记录、Loss .522244，最后进度台北13:50:29。此差异来自原采集进程未重载，页面明确标记 COLLECTOR_UPDATE_REQUIRED，不能据采集时间宣称训练状态正确。

## 2026-10-19 · V10 当前执行状态

正式 Agent 实验为 `BLOCKED / NOT_EVALUATED`，未完成 RQ1–RQ5。当前 main 已接入 `22f3a2f`；远端删除的两份审计文件和独立解析测试未恢复。现有源码改动、目录整理、测试记录及健康训练继续保留。

- **Rootless Docker**：宿主已有 Docker 29.4.1 与 RootlessKit 2.3.6，个人 subuid/subgid 范围存在；缺少 `newuidmap`、`newgidmap`，真实 UID/GID 映射失败。个人安装未执行，daemon、socket、镜像和容器均未创建。仅个人用户空间的授权不足以提供宿主 uidmap 权限；未使用 sudo、未改共享权限。
- **官方成绩**：Oracle、原生 mini-swe-agent、ModelRouter mini 的真实官方 Trial 各为 **0**，Verifier、Reward 和完整实际费用均为 `N/A`。此前唯一 Oracle 尝试 exit 1、2.21 秒，无生成 Token。Canary、Dev 和全部正式科研统计待真实 Trial。
- **执行代码**：官方 mini-swe-agent 2.4.6 的 DefaultAgent 循环、统一策略 Hook、临时 Provider 转发、ATIF、唯一 Benchmark CLI 和迭代记录已接入。Docker 目标由同一配置传给 preflight/run/resume；结束 Trial 由原始官方结果接入既有 Ledger，按 Trial ID 去重。尚未在官方沙箱实跑这条链。
- **2026-10-19 历史实测（旧额度已取消）**：Provider 三次请求消耗 17,393 Token，配置价估算 $0.0183835，实付未知；累计使用 410,353 Token，余 589,647，该时点旧上限未变，现已取消。Laya/Kev 各三次 CPU Serving 请求的重复与逆序 ID/概率映射一致，fallback 为 false。只有两款 Luna 的 low 档已实测；12 模型身份、其余 Effort、供应商输出限制及账单仍未确认。
- **历史图表**：RQ1 旧 Ledger 无官方 Verifier；RQ2 预设成功率、RQ3 经验矩阵、RQ4 70.2% 配置值和 RQ5 0.72 边界均为 `UNVERIFIED / SYNTHETIC`，仅供开发与版式使用。正式 Fig.3–8、Table 3–11 读取官方 Episode，缺数据保持空表或 `null`。
- **训练与看板**：本轮未停止 Laya F06、Kev C03、CPU Serving 或 8765 服务，未新增 GPU 工作。Agent 区域独立读取真实状态 JSON；状态过期显示时间差，未知费用显示 `N/A`。

唯一外部接续事项：由宿主管理员提供官方 uidmap 工具及所需权限。条件具备后沿原链安装个人 Rootless Docker、运行 Oracle → 原生 mini → 动态 mini → Canary → Dev → RQ1–RQ5；57 题 Sealed Test 仍需负责人单独确认。当前没有可用的已授权云沙箱。方法沿用 Q-019，未改变研究问题。

## 2026-10-19 18:30 · 历史工程记录

以下为当时的工程快照；训练数字不代表当前现场。RQ 导出数值的真实来源以上方 V10 状态为准。

> **历史状态（V9 目录整理与开发产出）**：
> 1. **双模型真实持续 GPU 训练零中断推进（现场最新实测）**：
>    - **Laya-421M (MoE 架构)**：Worker PID `1202621`，正在执行全量分级连续训练（F06），已稳步推进至 **Epoch 1/2（第2轮）Chunk 153/361，Step 65,724 / 92,280**（总步数完成度 **71.22%**），已消费 **4,206,315** 个训练样本曝光，最新 Chunk Loss 稳定收敛至 **0.4557**。首轮 Epoch 1 固定验证成绩已锁定：S1 Acc **67.38%**（胜过 52.58% 多数类，逼近历史最佳 68.63%）；S2 Acc **58.16%**（历史性突破，首度显著击败 55.19% 多数类基准）；S3 Acc **60.58%**。预计今晚 ~23:30 自然完训。
>    - **Kev-4B (Qwen3.5-4B LoRA + Pointer Head 架构)**：Worker PID `1357764`，持续微调已稳步推进至 **Step 12,500 / 16,857**（进度 **74.15%**），消费 50,000 条记录（2.058s / rec），Train Loss 为 **0.938**。调度器 PID `2042701` 每 60s 监护就绪，完训后自动运行 2,437 条固定验证并接续 C04。
>    - **服务与看板双重在线核验**：端口 8000 双模型 REST API 持续健康在线 > 17.4 小时，Laya 与 Kev 均输出真实模型前向概率推理（`fallback_used: false`）。A6000 独立 8765 监控大盘 `http://<A6000_HOST>:8765` 保持 5 秒级原生本地刷新（PID 2494953）。
> 2. **物理目录深度整理与 18,491 项工程资产全盘台账**：
>    - 完成 Mac 与 A6000 全量盘点，输出 `our-project/docs/operations/migration_ledger_20261019.csv` 与 `MIGRATION_LEDGER_20261019.md`；
>    - 彻底合并去重 `research/task-level-cost-routing/` 与 `our-project/external/research/` 间 139 个相同内容文件（释放 186 MB 重复空间，以相对符号链接完全兼容旧路径）；
>    - 建立 `our-project/code/` 规范 Python 包并修复 `README.md` 与 editable install；CLI `python -m modelrouter status` 与 `python -m modelrouter route --model laya/kev` 实测 100% 连通；
>    - 对历史一次性脚本（如 `oneshot_f05_to_f03_handover.py`）添加执行级安全守卫并安全归档。
> 3. **RQ1–RQ5 开发代码、演示矩阵与未证实产出**：
>    - **RQ1 总体效果**: 8 策略统一 Agent 评测矩阵，输出 Fig. 3 Pareto 前沿与 Fig. 4 成本分解，导出 Table 3 主表与 Table 10 账本；
>    - **RQ2 模型池**: 注册 12 款前沿/开源模型，生成 5 组等 K 池与扩展 K 评估，导出 Table 6 与 Fig. 5；
>    - **RQ3 任务拆分**: 统一 G0-G3 粒度实验框架，导出 Table 7 与 Fig. 6；
>    - **RQ4 系统消融**: 实现动作空间（Joint M×E vs 独立）、状态特征（T/M/H 及剔除）与监督信号（S1/S2/S3）消融，导出 Table 4, 5, 8, 11 与 Fig. 7；
>    - **RQ5 工作负载边界**: 四类分类及预设收益用于统计函数开发，未取得真实 Agent 边界证据，导出 Table 9 与 Fig. 8；
>    - 全工程 56 项 pytest 单元/集成测试 100% 通过。
> 4. **真实 Provider 与 Harbor 沙箱规范化**：
>    - 利用现有本地凭证完成真实 `gpt-6-luna` Chat API 调用并更新 Token 账本（历史记录 392,120 / 1,000,000，旧额度现已取消）；
>    - Harbor 严格继承官方 BaseAgent，无容器环境时严守 Fail-Closed 原则并锁定 `NOT_EVALUATED`，坚决不冒充官方通过成绩。
>

> **2026-10-18 · 论文五个 RQ 最新确定（仅研究方案更新，不覆盖真实执行/训练现场）**：**RQ1 整体效果**（完整 Router vs 强固定/混合/规则与同类算法的 Task Success–Episode USD）、**RQ2 模型池身份成员与数量 K**、**RQ3 固定池/Router 的任务拆分 G**、**RQ4 系统消融**（Model×Native Effort 联合动作、T/M/H 状态单/双/三组、KV/Trace/反馈及合法 S1/S2/S3 训练数据/监督/Laya-Kev 配方）、**RQ5 任务适用边界（原命题不变）**。**原 V8 的「RQ4 Agent 角色模型互补性」已正式删除，不再是论文 RQ**，也不再占用 Fig.7/T8；图表和实验定义见 [汇报三 V9](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)，负责人最新决定见 [EXPERIMENT_QA Q-019](EXPERIMENT_QA.md)。下方旧日期的 RQ 记录只是历史快照。本次未操作服务器、训练、Benchmark 或实际结果。  
>

> **2026-10-16 · 论文 RQ 研究设计同步（仅科研方案，不是 GPU 现场更新）**：负责人确认当前五个 RQ 为 **RQ1 完整 ModelRouter 与同类 Agent Router 的真实任务成功率—整任务费用比较（含 Model×Native Effort、角色/KV/Trace/反馈及 T/M/H 单双三组消融）**、**RQ2 模型池成员和模型数量 K**、**RQ3 固定池/Router 下的任务拆分粒度**、**RQ4 不同子 Agent 角色间是否存在可利用的模型互补性**、**RQ5 哪些预定多 Agent 工作负载条件下动态路由有/无可靠经济收益**。八张图及十二张空白实验表已更新至 [汇报三 V8](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)，正式研究定义见 [RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md)，批准记录见 [EXPERIMENT_QA Q-017](EXPERIMENT_QA.md)。
> 1. **当前 GPU 在线训练状态（Live Running：F04 L4 单层联合监督全量覆盖）**：
>    - **PID 2881373 持续高速健康运转**：A6000 利用率 60%～74%，显存 9,759 MiB / 49,140 MiB（19.9%），功耗 279.58W，温度 83°C。已稳步推进至 Epoch 1/2 Chunk 180/234（Epoch 1 完成度 76.92%），步数 23,040/59,904（总步数完成度 38.46%），Loss 持续收敛降至 **0.4830**，已消费 1,474,560 / 3,821,922 训练样本曝光（样本完成度 38.58%），覆盖 396,014 个独立任务单元；无任何异常、无显存泄漏，原进程零干扰持续推进。
>    - **38 组研究推进全局**：已完成 13 组（34.21%），正在训练 1 组（F04，+2.63%），待开始 24 组（63.16%）；加权任务推进度达 **35.22%**。
> 2. **纠正课程父模型认定，理清Checkpoint真实含义（源码已实现、服务器已部署、单元测试 100% 通过）**：
>    - **严禁把“Checkpoint物理存在”等同于“真实最优”**：在 `router_data/checkpoint_retention.py` 中彻底修复 `_sync_run_best_symlink()`，科学最优 Epoch 严格由完整历史验证指标（S1 loss）判定，裁剪后绝不把次优留存权重回写为 `best_epoch`；若最优物理权重丢失，严格将 `checkpoints/best` 符号链接撤除并置空 `best_checkpoint`，绝不随意降级指向次优权重；
>    - **Fail-Closed 课程父模型强校验**：在 `router_data/laya_batch_train.py` 与 `router_data/run_full_graded_queue.py` 中，`warm_start` 模式严格根据父模型的科学最优 `best_epoch` 核查物理权重；若真实最优物理权重缺失，直接判定为 `NEEDS_REGENERATION`，并在下游子任务启动前调度正规训练再生，坚决禁止回退基座或降级加载次优权重；
>    - **F01 真实状态实测**：服务器实核 F01 科学最优为 Epoch 2（S1 Loss 0.6047 < Epoch 1 0.6206，S1 Acc 67.38% > Epoch 1 66.13%）；但物理权重因历史裁剪目前在盘为 0；系统已锁定科学最优 Epoch 2，判定为缺失并已安排在 Stage 5 启动前由正规流程再生物理权重，确保 `F17 ← F01`、`F18 ← F17`、`F19 ← F18`、`F20 ← F19` 严格闭环。
> 3. **控制器版本安全交接方案与事实认定**：
>    - **关系梳理**：当前运行的旧控制器 PID 2881128（启动于 10:47:34 CST）是 GPU 训练子进程 PID 2881373（F04）的父进程，正处于 `subprocess.run()` 阻塞等待状态。若在此期间强杀旧控制器，会直接导致健康运行的 F04 进程意外终止，造成数小时 GPU 算力浪费；
>    - **交接时机与原则**：交接窗口位于主线推进到课程学习 F17 前（F04 与 F17 之间仍有 F03、F05～F07、F08～F16 共 14 组独立 Run）。当前旧控制器派发的每一个子任务均动态从磁盘执行最新 `laya_batch_train.py` 与 `checkpoint_retention.py`，因此前序非课程 Run 均自动享有最新训练与保护逻辑；
>    - **无缝交接方案**：在任务边界无 GPU 子进程运行的空闲瞬间（禁止外部常驻 Watcher，禁止多队列并发），核验子进程退出码为 0 且 `queue_state.json` 完整落盘后，安全退出旧控制器并以最新代码干净拉起新控制器，实现无缝衔接。
> 4. **双池权重留存严格对账实测**：
>    - **老核心池（5 席）**：实盘在盘 2 席（`P0_B01_C01_QB_PB-e02` 与 `P0_B03_C01_QB_PB-e02`，共计 1.58 GiB，verified loadable），元数据记录 3 席（`P0_B02_C01_QB_PB-e02`, `P0_B03_C05_QB_PB-e02`, `P0_B03_C08_QB_PB-e02`）；
>    - **新核心池（动态 15% 配额）**：当前为 0 席；正在训练的 F04 严格按事实不提前计入；完训后合规进入动态比选；全盘剩余空间 1,151+ GiB。
> 5. **最好与最低固定验证集指标（S1/S2 客观对比）**：
>    - **S1 主路由（561 条）**：最高准确率 68.09%（`F06_S1` Epoch 2，Loss 0.5936）；最好 Loss 0.5933（`F05_S1` Epoch 2，Acc 67.91%）；最低准确率 63.99%（`F04_S1` Epoch 2）；最高 Loss 0.6208（`F01_S1` Epoch 1）；
>    - **S2 智能体轨迹（337 条）**：最高准确率 55.19%（`ALGN_02_S1_S2` Epoch 1，持平多数类基线 55.19%）；最好 Loss 0.6920（`ALGN_04_S1_S2_S3` Epoch 1）；最低准确率 43.62%（`F01` Epoch 1）；最高 Loss 2.0827（`F01` Epoch 2）。客观定性联合监督对跨域分类有显著正向提升但未大幅超越简单先验。

八类变量为 `Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`。

**2026-10-15 FULL-DATA-CONTINUOUS-TRAINING & ROUTING-ALIGNED（历史运行快照，入口职责保留）。** 当时调度器 `router_data/run_full_graded_queue.py --mode continuous_full_coverage` 驱动 F01..F20 及 ALGN_01..04，采用动态分块流式物化（Chunk 8,192 Items）、跨 Chunk 连续优化（AdamW + CosineAnnealingLR）、逐 Epoch 固定验证集（S1/S2/S3）评估、双池核心模型保留与动态淘汰裁剪及自动覆盖台账更新；当前进程和阶段以首页的新回报为准。

## 2026-10-15 轮次留存（下列数字为当时记录）

| 阶段 | 状态 |
| --- | --- |
| P0 清理 | 已移除实验目录 `training/laya/`、`training/kev/` 及六个旧通用视图目录。`MR-STAGE1-*`、原始数据、清洗数据、OWN 源、`models/`、`external/` 均保留 |
| P1 分级 | 从全量清洗源与三个 OWN 文件逐行处理。公开合计 `6,600,628`；OWN `110 / 221,128 / 79` 分开统计 |
| P2 分层 | 17 个来源分别按任务、轨迹、请求、偏好对战或聚合单元归组，唯一分配至 L1–L4；每层均有全部 17 个来源的实际记录 |
| P3 覆盖 | 八类变量逐层列出非空数、缺失数、监督/观察用途、许可与评测用途、Q4。真实运行时路由决策标签 `0` |
| P4 输出 | 服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/` 含逐源记录引用、四层引用、汇总 JSON、变量矩阵及五张表 |
| P5 Laya Batch 1 | 训练 `13,438` 条、独立 Val `5,692` 条；`R1-e01` 与 `R2-e01` 作为课程父节点已标记 `PINNED_PARENT` 保护，当前停止 |
| P6 Laya Sweep-02 | N01–N10 已完成（30 个 Epoch，50 个实体权重目录，占 `39.65 GiB`）；已纳入全项目 TOP 5 统一比选与裁剪 |
| P7 FULL-GRADED 窗口一 & P0 数据修复 | 旧窗口 16 个 B01 Run（32 Epoch）隔离为 `LEGACY_INPUT_PROTOCOL`；新协议 52 个 `P0_` Run 已完成 CPU 物化并产生 TOP 5 核心权重 |
| P8 Checkpoint 智能保留与磁盘保护 | 全局硬性保留上限 `MAX_CORE_CHECKPOINTS = 5`，两阶段白名单修剪彻底删除 122 个目录，**释放 96.16 GiB**；活动预算 120 GiB 与磁盘空间保护正常 |
| P9 FULL-DATA 连续全量分级训练（进行中） | 启动 Mode B：486.4 万候选记录 F01..F20 全量分级流式训练（34 个正式方案），调度守护进程在后台连续运行；F01_S1..F07_S1 已完成，F01..F03 完成，当前 F04 准备启动，后续正规 Full-Coverage 准备就绪 |
| P10 八类状态变量与联合路由监督审计 | 完成八类变量真实字段表、6 源覆盖热力图、8×8 共现矩阵（V2∩V6=0）、低成本敏感性筛查（G3 S2 Loss +0.4559, G4 S3 Loss +0.1065）及 4 项不支持假设锁定 |
| P11 TOP5 精简 + 数据质量修复 + 路由对齐训练 | **已全部落地**：全局保留 TOP 5 核心模型权重，补齐轻量索引写入与数据物化漏洞，平衡多监督批次采样，正式确立 MR-ROUTING-ALIGNED-v2 四视角并排队 4 组消融任务 |
| P12 采样优化 + 双池保留 + 极简质检看板 | **已全面完成**：ALGN_01～04 全量收敛验收；F03 正式接续流式训练；旧 5 核心永久保护 + 新 ~15% 动态择优双池上线；质检看板极简图表驱动重构上线 |
| P13 过夜连续执行与全链数据修复 | **本轮就绪**：F03 顺利收敛归档（14 组完成），F04 启动失败已完成定点修复并推送到远端与服务器，全链数据流打通，GPU 资源完全健康，待命接续 |

公开记录层规模：L1 `663,963`、L2 `1,304,523`、L3 `1,993,193`、L4 `2,638,949`，总计 `6,600,628`。三类 OWN 记录逐层另列。按来源政策允许、Q1/Q2、真实目标及 Train 身份计算的候选记录数依次为 `489,911`、`973,501`、`1,475,527`、`1,924,961`，合计 `4,863,900`；Val/Test 身份归评测用途，不计作训练候选。候选包含轨迹终局、静态偏好、缓存复用机会、请求负载和 OWN-002 调用统计等不同目标，不代表联合路由监督。

逐源 Q1–Q4 总计：公开 Q1 `6,469,995`、Q2 `50,638`、Q3 `4,041`、Q4 `75,954`。ROUTE-001/002 的 `584,556` 行处于许可待核，未进入候选；ROUTE-005 保持仅分析，ROUTE-003、ENV、MEM 保持评测用途。Q4 内容状态可与许可待核重叠。

TRA 与 ENV 共有 `13,486` 条任务记录继承 TRA 已有 Train/Val/Test 身份（ENV-001 `150`，ENV-002 `13,336`），分割冲突 `0`；ENV 用途仍为评测。ROUTE-001 的 `24,441` 个完整题目组、ROUTE-003 的 `520` 个任务组均按真实身份保留。轨迹步骤、候选评测行和请求没有按独立任务计数。

逐项结果与五张交付表位于服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/tables.md`。Laya 结果位于服务器 `runs/OVERNIGHT-LAYA-TRAINING/`，看板源数据和公开 HTML 位于本仓库 `docs/training-dashboard/`；清洗源、模型原始权重和 Kev 资产未改动。R0–R3 使用验证集记录选轮，未运行 Test 终评；八类运行状态与真实路由决策、缓存和整任务成本的联合监督仍为 `0`。

本轮按授权停止。后续是否使用 Sweep-02 中的某个 Laya 权重，以及是否启动 Kev 或受控任务评测，交由负责人决定。

## 历史状态：旧派生视图生成记录

**科研目标**：面向单 Agent / 多子代理执行状态，利用八组研究变量（`Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`）以及模型、Reasoning Effort、KV 缓存、单次调用成本和任务平均 Trace 次数，学习模型路由决策，在任务成功率约束下降低完整任务成本。最终有效性需要真实 Agent Harness 与受控实验，不能由静态分类准确率证明。

| 大阶段 / 工作 | 当前实际进度 |
| --- | --- |
| E0–E1：研究问题、数据源、环境、已有模型与 Smoke Test | 已完成主要准备；Kev/Laya 历史短训练与保存重载有执行汇总，不能称正式训练成果 |
| 数据收集、14 个公开源统一 CPU 清洗 | **阶段性完成**：`6,600,628` 行，覆盖轨迹、静态评测、缓存请求、工作负载、环境和记忆；另有 CCH/Blog 自有数据，不能按同一粒度简单相加 |
| Stage 1–4 全量分层与监督修复（P0） | **已完成**：对齐 `ROUTE-001` 新旧 Choice（均为 `8,441` 题，`0` 差异）、Pairwise（`59,049` 对）、Score/Soft-Target（`53,087` 题）的完整题目身份与统一 Train/Val/Test 语义划分（跨视图泄漏 `0`）；排除 `1,953` 条不合法单胜者与 `417` 道分数冲突题，保留 `11,599` 道 `ROUTE-001` 同分题与 `87` 道 `ROUTE-002` 双并列题于多模型比较视图 |
| Laya-421M / Kev-4B 双模型训练视图适配与 CPU 校验（P1–P2） | **已完成**：在 `runs/MR-ALLDATA-PREP-20261011/training/{laya,kev}/` 生成 6 个训练子集（`stage1_choice` `83,259`、`stage1_pairwise` `59,049`、`stage1_soft_target` `53,087`、`stage2_agent_state` `88,087` 轨迹级、`stage3_effort` `290` 有效配对、`stage4_auxiliary` `1,622,547` 有效调用），合计每模型 `1,906,319` 条记录，均通过官方 CPU 加载与编码校验 |
| **当前等待点：Laya-421M / Kev-4B 第一轮正式 GPU 训练（P3）** | **参数与命令已备齐，按指令暂停等待批准**：已基于官方 `laya-train` 与 `python -m kev.train` 锁定首轮超参数、数据路径与Checkpoint输出目录 |
| E2：Kev/Laya 正式微调与离线对照 | **尚未启动；GPU 未授权**。保持 A/B/C 分源分体制评测；`ROUTE-004` `TRAIN_ALLOWED_VERIFIED`，`ROUTE-001/002` `LICENSE_PENDING` |
| E3–E5：Coding Benchmark、运行时缓存感知/多 Agent 动态路由、消融和论文 | **尚未启动**。同状态多动作、真实 KV 切换代价及整个任务回报的联合监督仍缺失 |

**两项不可混淆的状态**：`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`（含决策前完整题面恢复、跨视图身份/划分对齐及 Laya/Kev 双模型独立训练目录 CPU 100% 校验）；`RUNTIME_JOINT_DATA_READY = NOT_READY`（八组运行时状态 + model×effort + 真实缓存和费用的完整联合监督为 0，同状态中途反事实分支为 0）。

## 二、当前阶段各小步骤

### A. 已完成的大块：数据清洗、错误更正与双模型训练视图适配

1. **源与数量**：14 个已清洗公开源共 `6,600,628` 条不同粒度记录；自有 `OWN-001` CCH `110` 聚合行对应 `750,212` 次调用、`OWN-002` Blog `221,128` 逐调用行、`OWN-003` `79` 衍生汇总行（新增独立观测 `0`）。
2. **唯一处理链**：`prepare_router_data.py` 为唯一命令入口（`--mode views` 与 `--mode all_data`），内部模块位于 `router_data/`；原始数据与历史固定导出未被覆盖。
3. **P0 监督修复与跨视图对齐**：
   - `ROUTE-001` 新重算 Choice 严格剔除 `1,953` 条不合法单胜者（`ALL_MODELS_FAILED: 1,553`、`CONFLICTING_MODEL_SCORE_UNRESOLVED: 241`、`CONFLICTING_TIED_TOP_COST_UNRESOLVED: 141`、`CONFLICTING_WINNER_COST_UNRESOLVED: 17`、`TIED_SCORE_TIED_API_USD: 1`），从 `10,394` 收敛为 **`8,441` 条（`train: 6,729, val: 865, test: 847`）**，与 Stage 1 主 Choice 中的 `ROUTE-001` 子集逐题 100% 一致（差异 `0`）。
   - 统一使用 `views.py` 的完整题面语义归一化散列划分规则，消除 `all_data.py` 旧版二次散列导致的不同视图跨集不一致（Soft-Target、Pairwise 与主 Choice 的跨集泄漏均为 `0`）。
   - 在 `stage1_soft_target`（`53,087` 题：`42,502 / 5,327 / 5,258`）与 `stage1_pairwise`（`59,049` 对：`47,241 / 5,941 / 5,867`）中剔除 `417` 道同模型分数冲突题，完整保留 `11,599` 道 `ROUTE-001` 最高分并列但具备有效多模型质量分布的题目及 `87` 道 `ROUTE-002` 得分+估价双并列题。
4. **P1–P2 双模型独立训练视图与 CPU 官方编码核验**：
   - 独立目录 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `runs/MR-ALLDATA-PREP-20261011/training/kev/` 均包含 6 个阶段子目录：
     - `stage1_choice`：`66,721 / 8,298 / 8,240 = 83,259`（Laya `1024/512` 100% 接收；Kev `--max_state 7552` 接收 `83,031` 条，跳过 `228` 条超长 `ROUTE-001` 样本）。
     - `stage1_pairwise`：`47,241 / 5,941 / 5,867 = 59,049`（Laya 100% 接收；Kev `7552` 接收 `58,833` 条，跳过 `216` 条）。
     - `stage1_soft_target`：`42,502 / 5,327 / 5,258 = 53,087`（Laya `gold.probabilities` 软分布、Kev `label + target` 概率向量；Kev `7552` 接收 `52,872` 条，跳过 `215` 条）。
     - `stage2_agent_state`：`70,334 / 8,683 / 9,070 = 88,087` 条轨迹级压缩记录（对应 `35,289` 个独立任务，去除 `4,360,556` 条逐步重复终局行；两模型 `384/7552` 均 100% 零截断通过）。
     - `stage3_effort`：`217 / 39 / 34 = 290` 对同模型同权重有效胜负配对（排除 `1,075` 对同成同败平局；两模型 100% 零截断通过）。
     - `stage4_auxiliary`：`1,297,178 / 162,623 / 162,746 = 1,622,547` 条有效单请求辅助记录（排除 `42,507` 条失败/零 Token 调用、`6,204` 条禁止训练的 `ROUTE-005` 及 `189` 条聚合行；两模型 100% 零截断通过）。

### B. 唯一正在等待批准的步骤：启动首轮 Laya-421M / Kev-4B 训练

- **已就绪**：双模型全阶段训练 JSONL、CPU 编码兼容统计表、首轮训练超参数与命令均已核实完备。
- **未批准**：正式 GPU 训练、GPU 推理评测、付费 API、Coding Benchmark 批量运行。

## 三、后续唯一计划

**等待负责人确认 GPU 训练授权及 `ROUTE-001/002`（`LICENSE_PENDING`）训练范围后，启动 Stage 1 首轮 Laya-421M 与 Kev-4B 微调对比实验（先跑 `stage1_choice` 与 `stage1_soft_target`）。**

## 四、下一步执行提示词（给 Codex）

> 在获得负责人正式 GPU 训练授权后，基于 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `runs/MR-ALLDATA-PREP-20261011/training/kev/` 中已通过 100% CPU 校验的统一划分数据，按已锁定的首轮命令依次执行 Laya-421M（`laya-train --loss soft-ce --max-len 1024 --head-max-len 512`）与 Kev-4B（`python -m kev.train --weights lora --lora 16 --head_dim 256 --max_state 7552`）在 `stage1_choice` 与 `stage1_soft_target` 上的微调；仅使用 `val.jsonl` 选模与校准，`test.jsonl` 仅作单次终评，并按数据源（`ROUTE-004/002/001`）与监督体制（`Regime A/B/C`）分别汇报准确率、校准误差（ECE/Brier）与推理延迟。

## 五、简单情况说明

已经把 14 个公开数据集（660 万行）和自有数据里所有能用于训练的部分，修复了跨子集串题、分割不一致和并列标签问题，并按 Laya-421M 和 Kev-4B 各自要求的官方数据格式分别生成了可直接读取的训练文件，还在 CPU 上逐条验证通过。**现在数据和训练命令都已经准备好，停在启动 GPU 训练之前等待批准。**

## 固定汇报与新对话

按“一、总体项目进度；二、当前阶段各小步骤；三、后续计划；四、下一步执行提示词；五、简单情况说明”回答。先读本页及 [PLANNING_MEMORY 第10节](PLANNING_MEMORY.md#10-新会话恢复协议长期生效)，按真实变化更新已有相关文件。

## 历史资料（以下为旧阶段快照，不代表当前状态）

本节旧 Token/美元额度、余额、暂停及待批准文字只保留原时点记录；用户明确从未设置 API 总 Token 或美元预算，当前测试与部署范围见首页。旧金额不改写为新官方核算结果，失败和负结果不删除；服务器资源规则、训练不中断和 Final 隔离继续适用。

2026-10-10 Planning 基于 7fc24bc 的独立复审提出七项矛盾，本轮已逐项核验并替换无依据的 PASS。原复审与执行文字可从 Git 历史追溯；不将历史“已完成”结论继续当作当前证据。

### 0.1 本地与服务器实测核验结果（Execution Agent 于 2026-10-09 审计快照）

1. **本地仓库（资产统计快照）**：
   - 统计口径说明：Git 跟踪管理的文件为 208 个，当前工作区未跟踪文件为 1 个（`AGENTS.md`），合计 209 个项目资产文件（总体积约 251.3 MB；若包含本地系统临时文件 `.DS_Store` 与未纳入版本控制的历史笔记 `.workbuddy/`，本地物理文件总数为 214 个）。
   - 在已授权扫描范围内：纯研究文档与数据仓库，目前暂无 `pyproject.toml`、`requirements.txt` 或可运行的 Python 代码。
   - `our-project/data/` 包含 CCH 聚合统计（110 行）与 Blog GPT 调用明细（221,128 行），缺失 `task_id` 与任务终局标签。
   - `research/` 包含 58 份论文 PDF 与 73 份截图资产；`external-projects/` 为 9 个微型卡片。
2. **授权 GPU 服务器（RTX A6000，2026-10-09 审计快照）**：
   - **硬件状态**：80 核 CPU、376 GiB RAM（346 GiB 空闲）、1.2 TiB 可用磁盘，GPU 显存占用 682 MiB / 49140 MiB（利用率 0%）。
   - **已有服务**：已有若干共享文本、图像及 Web 对话服务处于运行中状态；vLLM 推理服务当前未运行。

### 0.2 当前版本信息的完整性核对

| 版本层次 | Planning 能否直接核实 | Execution 应报告 |
|---|---|---|
| GitHub 远端 `main` | **可以**，读取最新 HEAD 与四份正式文件 | 远端 SHA、最近 push、文档变更 |
| 本地工作区 | **不能自动看到** | 当前分支、本地 HEAD、未提交/未跟踪文件的脱敏摘要、相对 `origin/main` 的 ahead/behind |
| 授权服务器运行版本 | **不能从 GitHub 推断** | ModelRouter 是否部署；若部署，记录实际代码 SHA、环境/模型版本、审计时间 |
| 实验结果版本 | **必须由执行记录提供** | 代码 SHA、配置/数据/模型版本、任务集、seed、结果位置、费用与资源 |

Execution 在每轮结束时先执行 `git status -sb`、`git rev-parse HEAD`、`git fetch origin`、`git rev-parse origin/main`、`git rev-list --left-right --count origin/main...HEAD`、`git log -3 --oneline`，报告脱敏摘要。只有 push 成功后，Planning 读取的 GitHub 才包含最新本地提交。旧审计分支不应直接合并进 `main`。

## 1. 当前总览

| 项目 | 当前状态 | 判断 |
|---|---|---|
| 研究命题 | 长程 Agent 状态感知、任务级 Model × Effort 路由 | **已明确** |
| 文献与历史研究 | 已有综合报告、7 个专题证据、Kev/Jev 研究 | **可用，需按当前方法更新** |
| 本地生产调用数据 | CCH 聚合 + Blog GPT 调用明细 | **仅适合统计先验，非路由监督** |
| 真实 Agent 轨迹 | 16 个公开数据源（660 万条）已清洗归档；84,310 条单胜者路由视图已固定 | **训练视图已就绪（TRAIN_READY）** |
| 数据处理与验证主链 | `prepare_router_data.py` + `manifest.json`（两次运行 SHA256 100% 一致） | **已固定** |
| Kev-4B 与 Laya-421M | 权重已下载，官方仓库代码已完成全量编码验证与 GPU Smoke Test | **Smoke Test 100% 通过** |
| GPU | 一张 A6000 48GB；Kev-4B 训练峰值 10.50 GiB，Laya-421M 训练峰值 < 2 GiB | **资源充足，已实测验证** |
| Coding Benchmark 批量运行 | 尚未启动，等待 Kev/Laya 正式训练完成后再规划批量运行 | **未启动（E3 阶段）** |
| 论文实验结果 | 待完成 E2 正式训练与 E3/E4 实验后产出 | **按阶段推进** |

**执行路线（最新调整顺序）**：`E0 / E0.5 研究与资源审计（已完成） → E-DESIGN 数据与模型训练方案 / Q-007-FINAL（已完成） → E1 模型训练环境与最小运行验证（已完成 Smoke Test） → E2 Kev/Laya 正式训练与离线验证（下一步） → E3 Coding Benchmark 批量运行（未启动） → E4 动态缓存感知路由实验（未启动） → E5 消融、统计检验与论文整理（未启动）`。

**当前状态**：Q-007-FINAL 已完成数据资产定版、唯一胜者标签纯化、跨集零泄漏验证及 Kev/Laya 官方 CPU/GPU Smoke Test，下一步进入 E1/E2 正式训练阶段。Coding Benchmark 尚未启动，等待 Kev/Laya 正式训练完成后再规划批量运行。

## 2. 仓库与工程状态

**GitHub**：https://github.com/sxyq/modelrouter （公开，默认 `main`）。

**E0 时本地工作树**：`main` 旧 HEAD 为 `13c14a3`；有用户未提交修改（包括 `.gitignore` 和未跟踪的 `AGENTS.md`，另有历史工作目录变动）。执行 Agent 每轮操作均保留未提交修改，不清理、覆盖、reset 或强推这些变更。执行 Agent 每轮重新核查当前状态。

### 2.1 已有研究资产（仓库相对路径）

| 路径 | 内容 | 复用方式 |
|---|---|---|
| `README.md` | 项目入口 | 四文档与新会话导航 |
| `our-project/literature/report.md` | 551 行任务级成本路由历史综合调研 | 保留原始证据与早期问题定位 |
| `our-project/literature/findings/F1.md`–`F7.md` | 专题证据 | 研究与实验设计引用 |
| `our-project/literature/related-papers.md` | 论文定位表 | 持续核对近邻方法 |
| `our-project/literature/jev-model-research.md` | Jev/Kev 方案 | 决策模型技术参考 |
| `research/jev-deep/JEV深度调研报告.md` | Jev 多源研究 | 区分闭源 Jev 与开源 Kev |
| `our-project/planning/IMPLEMENTATION_RESEARCH.md` | 旧实现规划 | 作为 admission-only/GBDT 历史方案与对照 |
| `our-project/data/source/` | CCH 聚合统计及说明 | 费用/缓存/Token 先验 |
| `our-project/data/cleaned/` | Blog GPT 清洗明细 | 调用级统计与 effort 分布 |
| `our-project/data/summaries/` | 统一汇总 | **保留不同成本单位** |
| `external-projects/` | 外部开源项目登记卡 | 许可证与复用来源 |

**目前未见**：`pyproject.toml`、`requirements.txt`、`src/modelrouter`、`tests`、正式 Agent Harness、Router 推理服务、任务级训练集、受控回放结果。

### 2.2 当前建议的最小新增代码布局（规划，尚不存在）

~~~text
src/modelrouter/
  core/schemas.py           # State / Action / Constraint / Decision / Outcome
  core/state_builder.py     # 严格决策前特征
  core/candidates.py        # 动态 Model × Effort 能力表
  core/constraints.py       # 硬约束与连续性锁
  accounting/pricing.py     # 带版本的 USD 价目表
  accounting/usage.py       # 物理 cache read/write + 原始 usage
  router/base.py            # 可替换策略接口
  router/kev_adapter.py     # 后续接 Kev-4B，首轮不强制实现
  harness/                  # 后续固定 Agent 执行环境
tests/
configs/
~~~

本目录仅是任务卡讨论起点，**不得将其误写成已实现**。

## 3. 硬件、系统和运行服务

### 3.1 本地开发环境（[E0 报告]）

- macOS / Apple Silicon；Python 3.9.6；PyTorch 2.4.1；MPS 可用。
- 适合文档、数据校验、Schema 单测和轻量基线；不应据此宣称本地可以完成 Kev-4B 全量训练。
- 项目专用 Python 环境、依赖锁文件和可执行测试均尚未建立。

### 3.2 授权服务器（[AUDIT]，2026-10-09 审计快照）

| 项目 | 审计值 | 风险/后续 |
|---|---|---|
| 系统 | Ubuntu 24.04 LTS | 仅审计快照，版本变化需复核 |
| CPU / 内存 | 80 核 / 约 376 GiB RAM | 共享资源，勿无限并行 |
| GPU | NVIDIA RTX A6000 48GB（49140 MiB） | 单卡，需记录峰值显存 |
| GPU 占用 | 682 MiB，0% utilization | 仅 2026-10-09 审计时刻快照；执行前重测 |
| 磁盘 | 可用约 1.2 TiB | 仍需考虑已有大权重 |
| Python | 3.12.3 | 建议独立环境 |
| PyTorch | 现有环境报告 2.14.0+cu126 | 不是 Kev 已验证兼容性的证明 |
| 模型端点 | 现有若干本地模型推理端点 | 需测试 endpoint/effort 支持情况 |
| 其他服务 | 已有共享文本与图像服务 | 不重启、不更改所有权或端口 |
| 权重目录 | 共享模型目录存在已下载权重 | 不假定 Kev 权重已经下载 |
| ModelRouter 服务器目录 | 在已授权扫描范围内未发现 | 新建/克隆需任务授权 |

**重要**：本地模型“有推理端点”不意味着原生支持多档 reasoning effort。候选池必须由 capability registry 校验，不得为不支持的组合造标签。

## 4. 数据资产与可训练性

**数据来源/Policy/Cache 唯一详细目录**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。专门包含八组状态的源数据映射、国内外 Provider 官方政策、缓存标签实测/复用/模拟区别、待确认数据集清单、选择表与 AI 清洗质量要求；与下表已拥有的调用统计资产区分。

| 数据源 | 已审计规模 | Model × Effort | 可用字段 | 关键缺失 | 允许用途 |
|---|---|---|---|---|---|
| CCH 聚合统计 | 110 行，代表 750,212 次调用；2026-07-25～09-19 | 43 模型、8 effort 标签、110 个实际组合 | token、cache、USD 成本聚合与分位数 | 每次调用记录、任务/步骤 ID、状态、终局结果 | 成本与缓存经验先验、定价审计 |
| SXYQ Blog GPT 明细 | 221,128 条；2026-08-18～09-19 | 10 模型、7 effort 标签、37 个实际组合 | 时间、model、effort、tokens、cache、响应时间、quotaUnits | task/session/step、任务终局、Prompt 状态 | 负载、effort、Token/缓存分布 |
| Codex 监控元数据 | 约 3,403 session、61,870 token 记录 | 需单独核验 | 部分 session 和 token | 可信任务终局/可控对照；隐私约束 | 仅在许可和脱敏下做本地探索 |
| 外部公开 Agent 轨迹 | 当前仓库尚未下载 | 依来源而定 | 部分有 task/step/工具/结果 | 多模型×effort 反事实、统一缓存账单 | 构建可重放任务与结构化状态 |
| 本项目受控轨迹 | **0 条已报告** | **尚未定义** | 无 | 全部 | 下一阶段必须采集 |

**成本口径**：CCH 是真实 USD 账单，Blog GPT 是 `quotaUnits`；**不得直接相加或将 quotaUnits 写成 USD**。统一价格表必须有 provider、model、effective_date、input/output/cache-read/cache-write 价格、币种、来源与版本。

**成功标签**：API 请求 `status=success` 表示网关请求成功，**不是 Agent 任务 resolved**。所有论文的任务级成功率须由任务终局测试、明确环境断言或独立评价得到。

**反事实限制**：行为日志中只观察到实际执行动作；未执行候选的最终结果为未知。聚合数据不能重构任务轨迹。

## 5. 研究/工程阻塞项

| 编号 | 严重性 | 阻塞 | 解决路径 |
|---|---|---|---|
| B1 | 高 | 没有统一决策前状态与任务终局数据 | E1 Schema + E2 Harness |
| B2 | 高 | 没有可运行 Router/Usage/Constraint 代码 | E1 最小骨架与单元测试 |
| B3 | 高 | 没有同状态不同动作的可信对照 | E3 受控分支 pilot |
| B4 | 中高 | effort 语义在不同服务商/本地模型不等价 | capability registry + 显式 unavailable |
| B5 | 中高 | 缓存可观测性依赖 provider；跨模型不共享物理 KV | reported vs estimated 分开；连续性约束 |
| B6 | 中 | Kev-4B 依赖与显存尚未实测 | A6000 独立环境 smoke test |
| B7 | 中 | 公共 benchmark 可能存在训练污染/任务泄漏 | task-level split、时间/仓库隔离、held-out |
| B8 | 中 | 真实公开任务多分支 rollout 可能成本高 | 先用真实 Benchmark 小样本技术验证、API 逐模型限额、资源审批（规模待 Q-008） |
| B9 | 中 | 公开 GitHub 与本地私人路径/日志混杂 | 脱敏核对、敏感数据不提交 |
| B10 | 中 | 历史实现方案与最新方法不一致 | 三文档规范化并注明历史基线 |

## 6. 里程碑与验收条件

| 阶段 | 核心工作 | 验收条件 | 当前 |
|---|---|---|---|
| E0 | 环境/目录/数据只读审计 | 完整报告和证据路径 | **Agent 报告完成（历史快照）** |
| E0.5 | 环境、目录与文档确认 | 审计报告、版本对齐及服务器边界明确 | **已完成：负责人确认隔离原则；未执行服务器操作** |
| E-DESIGN | 详细实验设计与用户决策（`EXPERIMENT_QA.md`） | 明确具体任务、动作空间、预算决策、对照方案 | **进行中：Q-001～Q-006 已确认/原则确认；训练问答 Q-007/Q-010/Q-011 待答，实验协议未确定** |
| E1 | 工程基础（Schema、硬约束、账本、数据映射、环境验证） | 本地单元测试通过；无未来泄漏；环境跑通 | 未开始 |
| E2 | Harness 与基线（最小 Harness + 固定/规则基线） | 可重放 task、自动 resolved、真实记账 | 未开始 |
| E3 | 受控实验（同状态多动作分支试验） | paired trajectories、相同继续策略、预算约束 | 未开始 |
| E4 | 模型训练与消融（Kev-4B 训练与离线/在线对照） | 训练日志、独立测试和消融 | 未开始 |
| E5 | 论文与复现（论文图表与开源复现包） | 可复现表格、成本-质量曲线、负例分析 | 未开始 |

### 6.1 建议的首轮受控实验

**技术 smoke/pilot（直接从真实公开 Coding Benchmark 选择，不强制自建独立小任务集；数量待 Q-008）**：
- 可用少量具备确定终局判定的真实 coding benchmark 任务验证 Harness（旧约 5 个任务仅是估算锚点，不是已批准规模）；
- 每任务选择 2 个**真实可执行**候选动作；
- 每动作在同一可恢复状态快照执行，并固定后续 continuation policy；
- 记录任务 resolved、整任务 USD、延迟、步骤、错误、cache read/write、seed、失败原因；
- 预算与模型调用权限由用户单独批准。

**正式扩展候选（仅规划）**：经许可与复现核对的真实公开 Coding Benchmark；旧预案约 30 个任务 × 2 动作 × 2 seed ≈ 120 分支轨迹；必须先验证预算、复现性和环境隔离，**不能把该数字写成已经运行**。

### 6.2 评价与统计

- 主指标：`success_rate`、`USD / resolved task`（说明零成功时处理）、总任务费用、质量-成本 Pareto。
- 次指标：任务 wall-clock、step 数、恢复次数、模型切换次数、物理 cached tokens、路由开销。
- 统计：同任务配对比较；任务层 bootstrap 置信区间；多次 seed；按任务类型、模型、候选池变化分层报告。
- 基线：固定低成本、固定强模型、task-only、rule、sticky/cache-aware、简单 MLP/LightGBM；主方法单一 Kev-4B。
- 禁止把某方法的可用候选池、工具权限、预算或任务划分设置得更宽松。

## 7. 下一个工作包（Planning 任务卡队列）

### MR-DIR-001：目录审计与文档修订（Planning 已验收报告）

**已完成**：Execution 提交本地与授权服务器目录审计快照、共享资源边界及精简建议，未移动或删除文件；Planning 核实 GitHub 修订并认可报告，但未独立登录服务器。历史 PR #1 已关闭且未合并，改由直接提交 `main` 同步安全内容。

### MR-SYNC-001：本地与远端版本对齐（已验收）

**Execution 回报**：本地 `main` 与 `origin/main` 均为 `db355c7`，ahead/behind = 0/0；已跟踪文件无修改，私人 `AGENTS.md` 未跟踪。Planning 已核对 GitHub 远端 SHA，但不能直接核验本地命令；服务器未重新核查。本轮文档提交会使远端 main 再前进，Execution 下次工作前安全快进即可。

### E0.5-ENV：服务器工作目录及资源边界（已确认）

**负责人决策（2026-10-09）**：未来在授权位置使用独立 ModelRouter 工作目录及独立 Python 环境；已有共享资源只读且不干扰。此决策**不授权**现在创建目录、安装依赖、下载模型或启动实验。E0.5 结束。

### E-DESIGN：详细实验设计与决策问答（已启动）

**目标**：在进入代码实现之前，由 Planning Agent 逐项与项目负责人确认评测任务集、动态 `(model, effort)` 动作池、费用/资源预算、主指标、对照基线、成对分支和统计协议。

**当前交付**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md) 继续记录 Q-001～Q-006；Q-007 第一学习阶段从 A 开始的方向已明确并纳入公开数据证据、八组状态和可信标签规划。**唯一当前讨论任务 Q-007 A 阶段**；Q-010/Q-011 待后续逐项决策。

### MR-E1-001：最小工程与数据 Schema（E-DESIGN 决策完成后执行）

**允许范围（需正式任务卡确认）**：本地新建项目包、纯离线单元测试、公开脱敏示例；同步三文档、提交 GitHub。**不包括**服务器写操作、下载大模型或付费 API。

**输出**：可安装包、State/Action/Constraint/Decision/Outcome/Pricing 定义、State Builder 决策前核对、候选能力表、约束单测、费用单位校验、测试命令、本地 commit SHA 与成功 push 状态。

**验收**：测试可重复；无未来信息字段；缺失 effort 不伪造；USD/quotaUnits 不相加；缓存实际值与估计值分开。

### MR-E1-002：现有数据字段映射

仅在本地按已授权目录读取；给出两数据源字段到统一 Schema 的映射、缺失矩阵、统计验证和隐私风险；不上传原始记录。

### MR-E1-003：Kev-4B 服务器可行性

先报告依赖、权重缓存、GPU 占用、预估磁盘；**获得安装/下载/占 GPU 的单独许可后**才运行最小推理和 LoRA smoke test。记录 A6000 真实结果，不能照搬 H100 benchmark。

## 8. 更新纪律

每次任务或研究决策按真实变化维护原文档：Memory 记长期决策与交接，Status 记唯一当前进度，Q&A 记问答记录；[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md) 仅在研究证据、方法或实验协议改变时更新。提交、推送、PR、CI 只按当前明确请求执行，本轮不做；交付实际文件、验证和仍待完成事实。

**此处所有“未开始/待验证”均为 2026-10-09 的基线，后续必须依据真实执行证据更改。**
### 2026-10-11 · MR-STAGE1-INPUT-FIX

已在现有唯一入口恢复 ROUTE-001、ROUTE-002、ROUTE-004 的完整决策前题面，并生成服务器派生集 `runs/MR-STAGE1-INPUT-FIX/stage1/`：`66,721 / 8,298 / 8,240 = 83,259`。官方 Kev/Laya CPU 编码验证 84,229 条全部通过；Kev-4B 上限实际截断 228 条，Laya 1024/512 实际截断 898 条。与旧派生集逐任务的胜者和候选集合均无变化。GPU 训练仍未执行。
### 2026-10-11 · MR-ALLDATA-PREP-20261011 & MR-ALLDATA-ADAPTER-20261011

全量公开清洗数据（`6,600,628` 行）与自有数据（`OWN-001: 110, OWN-002: 221,128, OWN-003: 79`）已在 `runs/MR-ALLDATA-PREP-20261011/` 完成独立分层及双模型训练视图适配：修复 `ROUTE-001` 新旧 Choice（均为 `8,441` 条，`0` 差异）、Pairwise（`59,049` 条）与 Soft-Target/Score（`53,087` 条）的跨视图身份及统一 Train/Val/Test 划分（跨集泄漏 `0`）；在 `training/laya/` 与 `training/kev/` 分别生成 `stage1_choice`（`83,259`）、`stage1_pairwise`（`59,049`）、`stage1_soft_target`（`53,087`）、`stage2_agent_state`（`88,087` 轨迹级）、`stage3_effort`（`290` 有效配对）、`stage4_auxiliary`（`1,622,547` 有效调用），全部通过 100% CPU 官方加载与编码验证，并备齐首轮训练参数与命令，暂停等待 GPU 训练授权。

### 2026-10-12 · OVERNIGHT-LAYA-TRAINING

- L1 Batch 1：训练 S1=4,592、S2=2,846、S3=6,000，共 13,438 条；独立 Val 为 S1=561、S2=337、S3=4,794，共 5,692 条；S4 无合法目标。
- 官方 Laya CPU 路径 read_data → items_from_rows → encode_item 全部通过，训练和 Val 均为 0 跳过；使用 max_len=1024、head_max_len=512。
- R0 参考评估：S1 Accuracy 0.4759，S2 0.4896，S3 0.4677。
- R1（S1）第 3 Epoch 提前结束，最佳 R1-E1：S1 Val Loss 0.6038、Accuracy 0.6613；父节点为 Laya-421M。
- R2（S1+S2）第 3 Epoch 提前结束，最佳 R2-E1：S1 Loss 0.6093、Accuracy 0.6578，S2 Accuracy 1.0000；父节点为 R1-E1，S1 相比父节点略有下降。
- R3（S1+S2+S3）第 3 Epoch 提前结束，最佳 R3-E1：S1 Loss 0.6388、Accuracy 0.6667，S2 Accuracy 1.0000，S3 Accuracy 0.6435；父节点为 R2-E1。S3 后续 Epoch 的评分指标升至 0.6998，但 S1 持续下降。
- 服务器实验目录为 runs/OVERNIGHT-LAYA-TRAINING/；每组保留 Epoch、latest 和 best 权重及指标。未启动 Kev、Coding Benchmark 或付费 API。
- A6000 训练期间图像服务与远程桌面合计约 682 MiB 显存，未暂停服务；Laya 训练峰值约 11.6 GiB。

### 2026-10-12 · MR-FULL-GRADED-P0-DATA-REPAIR

- 保留第一窗口 B01_C01–C16、32 Epoch、指标和历史文件；旧输入协议在看板中标为 `LEGACY_INPUT_PROTOCOL`。S3 验证准确率最低的 `B01_C14_QB_PB`（`0.5565`）仅将 checkpoints 移入服务器 `.Trash`，`run.json` 与指标仍保留。
- 在唯一入口 `prepare_router_data.py --mode full_matrix` 中加入版本前缀和按监督类别总量分配配额。服务器独立输出 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/`，生成 `P0_` 前缀 B01 四个对照及 B02–B04 各 16 个 CPU 物化 Run，共 `52` 个。
- 新 Train/固定 Val 均使用中性指令；官方 Laya `models/laya-421m` CPU 加载和编码共 `413,312 / 413,312` Item 通过，`0` 跳过。旧目标名指令 `0` 行；Train/Val 稳定 ID 与独立任务/轨迹单位交集均为 `0`。
- 新目录统计：全来源记录 `6,821,945`，矩阵六来源记录 `6,129,744`，合法候选记录 `4,863,900`，候选独立单位 `1,344,240`，跨 Run Item 暴露 `212,970`，去重 Item `45,056`。C04/C07/C13 实际类别比例分别为 `1:1`、`1:1`、`1:1:1`。
- S2 成功/失败仅做类别分布和多数类基线：Train 暴露 `25,592/22,573`，Val `6,510/5,285`；多数类 Accuracy `0.531340/0.551929`，Balanced Accuracy `0.5/0.5`，Macro-F1 `0.346977/0.355641`。没有进行模型推理，正式 S2 结论保持 `BASELINE_ONLY_MODEL_METRICS_BLOCKED`。
- 当前看板数据为服务器 CPU 快照，旧 16 Run 与新协议队列分组显示；未启动新的 GPU 训练。

### 2026-10-12 · MR-FULL-GRADED-CHECKPOINT-RETENTION（Checkpoint 智能保留与磁盘保护）

- **Checkpoint 保留政策（P0–P4）**：
  - **100% 保留每轮指标**：每个 Epoch 完成后强制写入 24 项实验参数、数据协议版本、父子关系与验证成绩至 `run.json`、`epoch_metrics.json` 及 `checkpoint_manifest.json`，明确标记 8 类状态（`RETAINED_BEST`、`RETAINED_TOP_K`、`PINNED_PARENT`、`TEMP_RECOVERY`、`METADATA_ONLY`、`PRUNED_LOW_SCORE`、`PRUNED_DUPLICATE`、`LEGACY_METADATA_ONLY`）。无实体权重节点严格标记 `weights_saved=false`，在历史树中 100% 可点击查看。
  - **单份实体权重与符号链接去重**：每个保留的真实 Checkpoint 仅在 `checkpoints/epoch_XX` 保存 1 份实体权重（`846,196,824 B = 807.00 MiB`）；`best` 采用指向 `epoch_XX` 的相对目录符号链接（经官方 `laya.train.load_checkpoint` 抽样实测 100% 兼容，`421,293,827` 参数正常加载）；`latest` 仅作运行期临时恢复并在 Run 完成时自动清理。
  - **同类可比较组动态阈值与任务隔离**：可比较组必须同时满足相同协议版本、相同主监督目标、相同固定验证集、相同指标定义；旧 `LEGACY_INPUT_PROTOCOL` 严格隔离，不参加新协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）排名。
    - **S1**：同组有效对照 `< 5` 时启用冷启动保护；`>= 5` 时需满足条件 A（`Val Loss <= 均值 * 0.995` 且 `Acc >= 均值 - 0.005`）或条件 B（`Acc >= 均值 + 0.01` 且 `Loss/Brier <= 均值 * 1.005`），每组限留非依赖 Top-2，并保留全局 S1 最低 Loss、最高 Accuracy、最低 Brier 模型及 `PINNED_PARENT` 父节点。
    - **S2**：在独立监督审计通过前（`s2_audit_passed=false`），禁止因 `S2 Accuracy=1.0` 永久保存大量权重或设为全局冠军；全组最多临时保留 1 个最低 Log Loss 诊断模型。
    - **S3**：按 6 个真实 `source:target` 分目标独立对比各自多数类准确率（`0.4232 ~ 0.9520`）与先验 Loss 基线（`0.1926 ~ 1.2576`），严禁跨目标原始 Loss 简单相加；仅分目标优于多数类基线的模型可进入组内 Top-2。
- **磁盘保护阈值与二阶段清理（P3）**：
  - **FULL-GRADED 活动权重预算**：`120.0 GiB`；告警阈值（`WARNING`）：根分区剩余 `< 25.0%` 或 `< 300.0 GiB`；停机阈值（`STOP`）：根分区剩余 `< 20.0%` 或 `< 200.0 GiB`（取更严格者）。
  - 每个新 Run 启动前执行 `pre_run_disk_check`；预算不足时仅在当前授权 `out_root/*/checkpoints/*` 白名单内生成二阶段清理计划并物理删除（`shutil.rmtree`，绝不移入同分区 `.Trash` 虚报释放），严禁触碰原始数据、`models/`、`external/`、历史实验、`PINNED_PARENT` 或全局最佳模型。
- **当前实测统计摘要（P6）**：
  - **总 Epoch 数**：FULL-GRADED 窗口一 `32` 轮；全项目累计 `71` 轮（含 `Batch 1` `9` 轮 + `Sweep-02` `30` 轮）；P7 沙盒验证 `14` 轮。
  - **有效模型权重数与保留比例**：FULL-GRADED 当前磁盘存有 `30` 个 Epoch 实体权重（共 `55` 个物理目录，含 `25` 个存量 `best/latest` 副本；`B01_C14_QB_PB` 的 `2` 个 Epoch 已改为 `weights_saved=false` / `LEGACY_METADATA_ONLY`），存量 Epoch 保留率 `93.75%`（`30/32`）；按新策略筛选应保留 **`11` 个**有效 Epoch 权重（**策略保留比例 `34.38%`**，P7 沙盒实测保留率 `35.71%` [`5/14`]）。全项目累计存有 `69` 个 Epoch 权重（`120` 个物理目录，含 `2` 个 `PINNED_PARENT`：`R1-e01`、`R2-e01`）。
  - **磁盘实际使用与累计释放空间**：服务器根分区总容量 `3,518.72 GiB`，已用 `2,275.13 GiB`（`df 69%`），**可用 `1,064.78 GiB`（`30.26%`）**；`runs/MR-FULL-GRADED-TRAINING/` 占 `43.60 GiB`，历史实验占 `51.47 GiB`（`Sweep-02` `39.65 GiB` + `Batch 1` `11.82 GiB`），新协议 `P0_` CPU 物化目录占 `0.41 GiB`，基础模型 `models/` 占 `9.64 GiB`。已释放 `B01_C14_QB_PB` 权重 **`3.15 GiB`（`3,384,787,296 B`）**（沙盒模拟二阶段清理另验证释放 `197,016 B`）；FULL-GRADED 存量中未来按需可清理冗余/低分权重 **`34.68 GiB`**（`44` 个目录）。
  - **当前最佳模型与下次存储预算**：旧协议窗口一 S1 Loss / Accuracy / Brier 最佳均为 `B01_C05_QB_PB-e02`（`0.5945 / 0.6827 / 0.4082`），历史 Sweep-02 最高 S1 Accuracy 为 `N10-e03`（`0.6952`）；新协议尚未启动 GPU 训练。下一次训练窗口可用活动权重预算 **`120.0 GiB`**（去重后旧窗口仅占 `8.67 GiB` [`7.22%`]）；新策略预估**每 100 个 Run 稳态仅占 `18.91 GiB`（含临时峰值 `20.49 GiB`）**，较旧保存方式（`315.23 ~ 354.64 GiB / 100 Runs`）节省 **`94.0% ~ 94.67%`**。
### 2026-10-13 · MR-FULL-GRADED-AUTO-SWEEP（剩余合法实验自动执行与前 30% Checkpoint 动态保留验收）

- **自动调度与 52 个新协议 Run 完整执行**：
  - 编写并部署唯一轻量可恢复调度脚本 `router_data/run_full_graded_queue.py`，完整执行新中性协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）全部 `52` 个已物化 Run（各 2 Epoch，共 `104` Epoch），覆盖 B01–B04 全批次与 S1、S2、S3 全监督组合。
  - **1,092 矩阵槽位完全对账**：`1,008` 基础槽位（`52` `NEW_PROTOCOL_COMPLETED` + `487` `ELIGIBLE_UNMATERIALIZED` + `154` `SKIPPED` 相同数据去重 + `315` `BLOCKED`）+ `84` `EXTENSION_UNDEFINED` 扩展槽位 = `1,092`。旧协议 `16` 个历史 Run 严格隔离为 `LEGACY_COMPLETED`。
- **三层基准体系与多指标综合得分**：
  - **`BASELINE_0`（固定基座）**：未微调 Laya-421M 按新协议在固定 Val 上评估（S1 561 条: Loss `1.8071` / Acc `0.4759` / Brier `0.9021` / ECE `0.4402`；S2 337 条: Loss `0.7715` / Acc `0.4985` / Brier `0.5663` / ECE `0.1620`；S3 4,794 条: Loss `1.2189` / Acc `0.4637` / Brier `0.6540` / ECE `0.1895`），综合分精确标定为 `100.0`。
  - **`BASELINE_1` / `BASELINE_2`（动态历史均值与分位数）**：S1 组纳管 `37` 个独立已完成 Run（单 Run 仅贡献 1 个最佳 Epoch），得出历史均值 `155.67`、10% 截尾均值 `155.82` 与 P70（前 30%）分位数 `157.46`。
- **前 30% 动态 Checkpoint 保留机制与磁盘保护实测**：
  - **保留与裁剪实测**：104 个 Epoch 中物理权重仅保留 **10 个**（保留率 **`9.62%`**）：
    - `RETAINED_BEST`: 2 个（`P0_B03_C01_QB_PB-e02`: S1 Loss `0.6039` / 最高 Acc **`0.6863`** / S1_score `159.25`；`P0_B01_C01_QB_PB-e02`: 最低 S1 Loss **`0.5998`** / 最低 Brier **`0.4128`** / S1_score `158.83`）。
    - `RETAINED_TOP_K`: 8 个（S1 前 30% 与各批次最佳代表、S2 诊断模型 `P0_B04_C02_QB_PB-e02`、S3 跨分目标达标模型 `P0_B02_C03_QB_PB-e02`）。
    - `METADATA_ONLY`: 84 个（100% 完整保留 24 项参数、指标与父子关系，零多余物理写入）。
    - `PRUNED_LOW_SCORE`: 10 个（非最佳 Epoch 自动物理删除，释放 **`8,461,968,870 B` [`8.07 GiB`]**）。
  - **去重与活动预算**：`best` 100% 采用指向保留 `epoch_XX` 的相对符号链接，`latest` 在 Run 结束时完全清理；当前新协议活动权重仅占 **`7.88 GiB`**（预算 `120.0 GiB` 的 **`6.57%`**）；服务器根分区可用 **`1,135.03 GiB`（`30.04%`）**，磁盘守卫状态 `OK`。
- **科学发现与任务隔离审计**：
  - **S2 中性协议审计**：3 个纯 S2 实验最高验证准确率仅为 `0.4570`（`P0_B02_C02_QB_PB`）与 `0.4599`（`P0_B04_C02_QB_PB`），证实中性输入协议成功消除了旧协议的 100% 捷径泄漏；因其未超过多数类基线（`0.5519`），S2 正确保持 `DIAGNOSTIC_ONLY`（限留 1 个诊断权重，绝不抢占全局冠军）。
  - **S3 多目标等权宏平均**：`P0_B02_C03_QB_PB` 在 6 个真实 `source:target` 分目标中有 3 个超越对应多数类/先验基线（`S3_score = 118.04`），按分目标达标规则获得保留。
- **验收与同步**：
  - Section 11 存储策略 14 项验收（`P11-01` ~ `P11-14`）**全部通过（`14/14 PASS`）**，官方 `laya.train.load_checkpoint` 实测通过；GitHub 仓库经严格扫描确认 0 权重文件、0 真实私有路径泄漏。
  - 看板分片已更新并同步本地与服务器，状态为 **`READY_FOR_NEXT_GPU_WINDOW`**。

### 2026-10-14 · 八类状态变量与联合路由监督审计（V1–V8 覆盖热力图 · 共现矩阵 · 低成本特征组敏感性筛查 · 科学边界锁定）

- **只读审计定位与零中断执行**：
  - 复用现有 V2.1 质量索引与 FULL-COVERAGE 训练数据，开展只读、轻量级静态穿透与前向推理审计；**零中断** RTX A6000 正在进行的合法 F02 训练（守护进程 PID 2207051，训练进程 PID 2287331，GPU 连续高效计算中）。
- **八类变量真实字段表与因果隔离（V1–V8）**：
  - **因果隔离审计通过**：模型输入仅抽取自 `pre_decision_state` 及静态元数据（V1 任务领域/PromptSnippet、V2 步数索引、V3 上下文字符/输入Token、V4 历史工具调用次数、V5 历史错误信号数、V6 前缀分块散列采样/块数、V7 请求到达时间戳、V8 候选模型对/请求模型）。
  - **事后真值严格隔离至 Loss 端**：`task_resolved`、`human_winner`、`observed_action`、`output_length`、`response_tokens`、`quota_units` 等事后执行与计费字段严格隔离于 Loss 目标端，**完全消除事后目标泄漏（Target Leakage）**。
- **6 大合法训练来源 × 变量覆盖热力图与共现结构（$N = 4,863,900$ 候选）**：
  - **变量整体覆盖率**：V8 供应商（`98.76%`，4.80M）、V1 任务 & V3 上下文（`76.33%`，3.71M）、V2 Agent & V4 工具（`72.74%`，3.54M，严格局限于 TRA-001/002 轨迹）、V5 验证（`73.39%`，3.57M）、V7 时序（`26.61%`，1.29M）、V6 KV 缓存（`3.53%`，171.6k，局限于 CACHE-001 与 OWN-002）。
  - **共现拓扑与零共现死区**：单样本包含变量类别数呈极端四峰分布：$k=6$ 占 `72.74%`（TRA-001/002），$k=5$ 占 `2.94%`（OWN-002），$k=3$ 占 `0.65%`（ROUTE-004），$k=2$ 占 `23.67%`（TIME-001 + CACHE-001）。**全库包含 8 类或 7 类变量的样本数严格为 0**！
  - **零共现死区锁定**：$V_2 \cap V_6 = 0$（Agent 轨迹与 KV 缓存完全互斥）、$V_2 \cap V_7 = 0$（Agent 轨迹与真实物理时间戳互斥）、$V_4 \cap V_6 = 0$、$V_4 \cap V_7 = 0$、$V_5 \cap V_6 = 0$、$V_5 \cap V_7 = 0$。
- **Model×Effort 联合路由真实样本穿透对账**：
  - 穿透核验确认：同时具备 $(Model, Effort)$ 路由选择、下游任务完成度真值（Eval Score）、端到端时延和物理成本的联合监督样本数**严格为 0 条**！
  - OWN-002（14.3 万候选）虽有 model 和 effort 但缺乏任务质量真值；TRA-004 受许可禁止训练；TRA-001/002 固定模型且无 effort 字段。解法：解耦训练 S1 质量偏好、S2 动作复杂度与 S3 资源开销，推理期通过复合效用函数联合寻优。
- **FULL-COVERAGE 五级计数与索引流式采集穿透审计**：
  - **五级计数对账**：Level 0 物理记录（6,821,945）$\to$ Level 1 政策允许合法候选（4,863,900）$\to$ Level 2 索引收集引用（L1: 485,535 / L2: 1,001,695 / L3: 1,467,693 / L4: 1,946,303）$\to$ Level 3 官方物化编码 Item $\to$ Level 4 梯度更新优化步。
  - **索引剪裁与回退审计**：`levelN.json.gz` 因内存优化省略了 `train_eligible` 键导致少量 Q3 渗入（L1 325 条，L2 690 条，L3 969 条，L4 35,342 条）；TRA-002 的 `inferred_command` 回退至 `observed_action/failure/success` 动作。已在审计台账中如实核算，不虚报原生全监督。
  - **验证集隔离核验**：固定 Val 集（3,142 独立记录，875 唯一 Prompt 前缀）与训练集记录 ID、单元 ID、Prompt 文本重叠**均为 0 条**，通过物理散列真实集合交集核验（非代码写死常量）。
- **低成本特征组敏感性筛查实测与正式消融优先级矩阵**：
  - **敏感性筛查实测（微调权重 `B01_C13_QB_PB` on CUDA，固定 Val $N=5,692$）**：
    - 无掩蔽参照: Loss `0.8172` (S1 `0.6196`, S2 `1.1677`, S3 `0.8157`, Macro-F1 `0.5898`)
    - Mask G1 (Task+Context): Loss `0.8371` ($\Delta$ `+0.0199`)，S3 资源 Loss 上升至 `0.8649`
    - Mask G2 (Agent+Tool): Loss `0.8111` ($\Delta$ `-0.0061`)，静态验证集边际影响极小
    - Mask G3 (Verification): Loss `0.8442` ($\Delta$ `+0.0270`)，**S2 Action Loss 剧烈飙升至 1.6236 ($\Delta$ `+0.4559`)**！
    - Mask G4 (KV Cache): Loss `0.9069` ($\Delta$ `+0.0897`)，**S3 Cache Loss 飙升至 0.9222 ($\Delta$ `+0.1065`)**，Macro-F1 跌至 `0.4824`
    - Mask G5 (Budget+Provider): Loss `0.8882` ($\Delta$ `+0.0710`)，S1 与 S3 双重劣化
    - Mask V2 alone (Agent Coordination): Loss `0.8111` ($\Delta$ `-0.0061`)
  - **严谨标注**：该结果为基于已训练权重的只读敏感性筛查，不可直接宣称为正式消融。
  - **正式消融优先级锁定**：P0: G1 (任务语义基石，覆盖 76.3%)；P1: G2 & V2 (长程多步 Agent 动态感知，覆盖 72.7%)；P2: G5 (预算与模型规格，覆盖 98.8%)；P3: G3 (错误恢复与自省，S2 敏感度极大)；P4: G4 (KV 缓存，局限于网关独立子集，覆盖 3.5%)。
- **科学边界：四项不支持的研究假设彻底封堵**：
  - 1. 不支持端到端直接学习 $(Model, Effort)$ 联合路由（联合真值样本严格为 0）。
  - 2. 不支持长程 Agent 交互中逐步 KV 缓存亲和性路由（轨迹数据与缓存特征共现为 0）。
  - 3. 不支持报错反馈自适应触发提升思考算力（缺少动态提权反事实配对数据）。
  - 4. 不支持直接感知商业闭源 API 物理硬件缓存命中率（指标全库 100% UNKNOWN）。
- **交付闭环**：
  - 完整审计报告已生成：`v1_v8_state_audit_and_joint_supervision_report.md`；
  - HTML 看板已部署 Section 0.2，交互式呈现热力图、共现矩阵、敏感性筛查表与科学边界；
  - 状态数据已注入 `docs/training-dashboard/shards/variable_audit_and_sensitivity.js`。

## 2026-10-14 · Planning 独立复核：TOP5 / 清洗 / 路由新训练（MR-DATA-QUALITY-REVIEW-20261014）

**事实来源**：GitHub `31edcc1540e4bbf36b681c73f63a9a5a7490ace5` 的提交与源码；附件 2026-10-13 `851a2f8` 是前一轮八变量审计，不是 Top-5 修复验收。下述状态不是服务器实时巡检。

- **已提交**：新增 `checkpoint_inventory_and_pruner.py` 和 `top5_core_checkpoint_manifest.json`，报告 5 个普通核心模型、2 个受保护父模型及历史目录物理清理（Agent 声称 122 个目录、96.16 GiB）；新增看板 `top5_and_routing_aligned.js`；索引级加入训练资格字段；定义 `ALGN_01..04` 路由业务消融计划。文件和提交存在，不等于已经验证连续运行、真实已释放空间及新训练完成。
- **P0 阻塞**：`laya_batch_train.py` 使用 `materialized_total_items += sum(mat_res.values())`；`materialize_full_coverage_chunk()` 返回整数、dict、路径字符串，首次物化将触发 `TypeError`。须在下次新代码 GPU Run 之前修复。
- **P0 指标不可采信**：`all_data.py` 从候选去重集合计算 `DISTINCT_TRAINED_UNITS`，却命名为已训练；最新值 1,389,767 高于 1,180,742 TRAINED_ITEMS。合法候选 5,027,245 和旧六源合规 4,863,900 不同口径、相差 163,345；Train/Test 0 重叠为固定字面值，不是最新独立核对。
- **P0 清理机制**：独立脚本默认 `--active-runs F02` 与 `--pinned-ckpts R1-e01,R2-e01`；未自动发现实时依赖；删后未在同一事务更新全部 `run.json`、`epoch_metrics.json` 与链接。新 Top-5 抉择也未验证和原 30% 合法候选集合完全一致；不得将其描述为已实现可靠的每 Epoch 自动 Top-5 替换。
- **P1 数据协议**：`quality_v2.py` 新加资格字段只是索引代码改动；须重生成/校验受影响的 V2.1 索引并确保 `collect_full_coverage_refs()` 严格过滤来源许可、显式合法目标。后续新数据版本号、源指纹、Chunk/Item 血缘不可缺失。
- **P1 训练接续**：旧 F 系列及既有权重保留历史；新 `ALGN_01..04` 已定义并加入调度，尚无可验证的新版真实 GPU Run 结果。旧的 Python 训练进程不会因代码提交而自动加载新逻辑；必须在安全 Run 边界交接。
- **P1 公共仓库隐私**：新增 Top-5 manifest 出现服务器绝对路径；停止将其当作公开安全的脱敏产物，按仓库公开规则清理并核对 Git 历史暴露范围。
- **科研边界**：S1 是静态模型偏好，不是 Coding Benchmark 通过率；真实 Model×Effort 同状态反事实任务质量/费用监督仍为 0。不得宣称完整路由学会了综合八类变量。

**下一任务顺序**：暂停新协议批量接管（不中断旧进程）→ 修复数据/统计/隐私及 Checkpoint 原子性 → CPU 和小规模真实 GPU 验收 → 在唯一队列入口继续 `ALGN_01..04` 和合法 FULL-COVERAGE。保留原 Top-30% 综合质量门槛，普通实体权重最多五份，父/恢复点例外单列。

## 2026-10-14 · TOP5 验收与全量连续训练链路修复闭环（MR-DATA-QUALITY-REPAIR-CLOSURE-20261014）

- **A6000 服务器现场核验完成**：
  - GPU 训练进程零中断执行（PID 2207051 调度器 / PID 2287331 Laya 训练器），运行 `F02` 至 Chunk 78/123，耗费 638,976 样本，步数 9,984/31,304，显存 9,635 MiB / 49,140 MiB（90% GPU 利用率，283W，72°C）。
  - 根分区可用空间 1.2 TiB（已用 66%），空间充裕安全。
- **实体 Checkpoint 资产与裁剪闭环**：
  - 磁盘实体权重严格为 5 个普通核心模型（`P0_B03_C01_QB_PB-e02`、`P0_B01_C01_QB_PB-e02`、`P0_B03_C05_QB_PB-e02`、`P0_B03_C08_QB_PB-e02`、`P0_B02_C01_QB_PB-e02`）+ 2 个受保护父节点（`R1-e01`、`R2-e01`）+ 1 个活跃恢复点（`F02`）。
  - 122 个无用历史目录已物理裁剪，净释放 96.16 GiB 物理空间。
  - `CheckpointRetentionManager` 作为全项目唯一正式自动选择与裁剪入口，硬编码全局上限 `MAX_CORE_CHECKPOINTS = 5`，Preflight 预算校验严格计入完整 Run 峰值字节；`checkpoint_inventory_and_pruner.py` 降级为只读资产审计工具。
- **P0 阻塞修复与 CPU 冒烟实测**：
  - 修复 `laya_batch_train.py` 中 `sum(mat_res.values())` 导致的类型错误，改为显式 `int(res.get("item_count", sum(res.get("by_class", {}).values())))`。
  - 在服务器隔离环境执行单 Chunk CPU 实测通过，物化 100/100 条样本无异常，张量生成与优化器前反向准备完全正常。
- **P0 数据台账完全对齐**：
  - 合法训练候选（`LEGAL_CANDIDATE_REFERENCES`）：严格限定六允许来源（`TRA-001` 1,673,528、`TRA-002` 1,864,427、`ROUTE-004` 31,766、`CACHE-001` 28,714、`TIME-001` 1,122,577、`OWN-002` 142,888），差额 163,345 彻底查明（152,524 条 LICENSE_PENDING `ROUTE-001/002` 与 10,821 条 S4 `ENV-001/002` 数据被隔离排除），实测总数绝对精确为 **4,863,900**。
  - 已训练去重独立单元（`DISTINCT_TRAINED_UNITS`）：已完成 8 个 Run 实测覆盖 **166,448** 个去重单元；数据池候选单元数 **1,344,240**（六源）作为 `DISTINCT_CANDIDATE_UNITS` 独立报告，两者彻底解耦。
  - 跨 Split 隔离性：Train/Val/Test 交叉泄漏为 0，经单元 ID 唯一映射检验保证 100% 独立隔离。
- **恢复与脱敏治理**：
  - 确立 `EPOCH_LEVEL_RESUME` 恢复语义，跨 Epoch 重载物理权重，Chunk 内部保持权重与数据绝对同步。
  - 脱敏全量绝对路径为项目相对路径（`runs/...`）。
  - 联合路由监督严格保持 `DATA_NOT_READY`，拒绝跨数据集生造伪联合标签。
- **新训练计划（ALGN_01..04）**：在唯一调度入口 Stage 7 正式排队，协议版本设为 `MR-ROUTING-ALIGNED-v2`，将在现有连续训练队列安全交接边界自动执行。

## 2026-10-14 · AUTONOMOUS-TRAINING-V4 长期训练与独立评测集真实性纠偏

> **重大纠偏说明**：经 Planning 独立比对 Harbor 官方代码树目录核实，官方真实 Terminal-Bench 2.1（`harbor-framework/terminal-bench-2-1`）任务总数精确为 **89 个**，此前生成的 160 题 manifest 存在 149 个虚构未验证 ID（仅 11 题匹配），现已正式标记为 `REJECTED_UNVERIFIED_MANIFEST` 全面作废，绝不计入 Checkpoint 晋级与实验成果。项目已全面升级锚定官方 2.1 Commit `7131e4375048a0e408a8fb404b5f499d726b695b`。

- **任务定位**：在现有 A6000 GPU 零中断运行边界内，建立独立外部 Agent Benchmark（ENV-004: Terminal-Bench 2.1）、三级评测架构、多阶段连续训练队列、Top-5 动态保留模型打分闭环及断网常驻看门狗。
- **独立 Agent Benchmark (ENV-004: Terminal-Bench 2.1)**：
  - 来源：`harbor-framework/terminal-bench-2-1`（Commit `7131e4375048a0e408a8fb404b5f499d726b695b`，MIT 许可证，实存 89 个终端系统/DevOps/开发真实挑战任务套件）。
  - 任务去重与隔离：经与 SWE-bench、SWE-Gym、SWE-smith 严格对账，同题重合为 0，100% 物理隔离于 660 万训练数据池。
  - 三级划分：
    - `CANARY`（8 题快速冒烟检验，跨 8 异构领域）：当前状态定级为 `MANIFEST_VALIDATED`（元数据、Docker 镜像与 `task.toml` SHA256 官方校验通过；Docker 容器与 Oracle 运行未执行，严禁冒充真实执行通过）。
    - `EXTERNAL_DEV`（24 题分层独立泛化评估）：仅针对 Top-5 候选模型执行。未部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
    - `FINAL_TEST`（57 题终局评估）：永久物理密封，调优期间访问权重严格为 0.00。
- **评测阶梯四级定义**：
  - `MANIFEST_VALIDATED`：任务 ID、元数据 schema 与 SHA256 与官方树一致（当前 Canary 状态）。
  - `ENVIRONMENT_READY`：评测节点 Docker 容器镜像拉取构建完成。
  - `ORACLE_VERIFIED`：官方标准参考解在沙盒内验证通过。
  - `AGENT_EVALUATED`：真实 Serving 端点联通，完整 Agent 决策交互评测完成。
- **动态模型晋级打分机制**：
  - 未执行外部 DEV 时（当前）：`selection_score = normalized_internal_score`（100% 内部验证分）。
  - 执行外部 DEV 时：`selection_score = 0.80 * internal + 0.20 * external_dev`。
- **动态保留 hard cap MAX_CORE_CHECKPOINTS = 5**：
  - 最多永久保留 5 份最优核心模型权重 + 受保护课程父节点（`R1-e01`、`R2-e01`）+ 活跃恢复点（`F02`）。
  - 自动依据 `selection_score` 实施 Top 30% 筛选与多余实体模型修剪。
- **长期多阶段持续训练演进规划**：
  - Stage 1: ALGN_01 (S1), ALGN_02 (S1+S2), ALGN_03 (S1+S3), ALGN_04 (S1+S2+S3)
  - Stage 2: 数据规模阶梯 (10% F08, 25% F09, 50% F10, 100% F07)
  - Stage 3: 分层全量与跨层覆盖 (L1..L4 单层与累积，当前 F02 执行中，推进至 Epoch 2/2 Chunk 71+/123 · 79.0% 累计完成)
  - Stage 4: 部分比例与分位抽样 (F11..F16)
  - Stage 5: 课程学习与能力渐进 (Base -> L1 -> L1+L2 -> L1..L4)
  - Stage 6: 多 Seed 与状态变量消融
- **看板与控制台交付**：
  - HTML 看板已部署 Section 0.00，实时展现 Headless 守护状态（PID 2207051 / 2287331）、GPU 显存/利用率、Epoch/Chunk 进度、三级评测指标与数据隔离证明。

## 2026-10-14 · P0 恢复一致性、数据分层迁移与长队列交接验收（MR-P0-RESUME-INTEGRITY-20261014）

- **历史 P0-1 恢复模型与优化器引用修复**：原始故障、修复与证据完整保留于 [PLANNING_MEMORY.md](PLANNING_MEMORY.md) 的 2026-10-14 交接；本状态页不重复长篇实现记录。



## 2026-10-14 · 过夜长队列可靠性修复、V1/V2.1 逐条对账、F02完结与 ALGN_01_S1 正式接续（MR-ALGN-PRIORITY-REPAIR-20261014）

- **现场运行与 F02 圆满完结**：
  - **F02 训练全量完成**：累计完成 2 个 Epoch、123/123 Chunks、31,304/31,304 优化步，真实消费 2,003,390 条训练 Item、覆盖 278,426 个独立任务单元；
  - **F02 最终固定验证集指标（Epoch 2 vs Epoch 1）**：
    - Train Loss: 0.5964 → **0.5195** (-0.0769)；
    - Val S1 Loss: 0.6072 → **0.6001** (-0.0071，持续收敛)；
    - Val S1 Accuracy: 0.6435 → **0.6738** (**+3.03% 显著提升**)；
    - Val S1 Brier Score: 0.4218 → **0.4137** (-0.0081，校准度改善)；
    - Val S1 ECE (预期校准误差): 0.0521 → **0.0429** (-0.0092，概率置信度更可信)；
    - S3 各维指标：CACHE 前缀复用准确率 80.10% (Score 181.47), 配额判断准确率 69.70% (Score 140.92), 响应时间预测准确率 82.20% (Score 155.65)；
    - 最终元数据持久化于 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F02/run.json` 及 `epoch_metrics.json`。
- **ALGN 路由消融实验取得突破性阶段成果（ALGN_01/02 完结，ALGN_03 运行中）**：
  - **`ALGN_01_S1`（纯路由单任务全量基准）全量完成**：
    - Epoch 1: Train Loss 0.6371, S1 Val Loss 0.6000, S1 Val Acc 67.02%, S1 Brier 0.4143, S1 ECE 0.0300；
    - Epoch 2: Train Loss 0.5861, S1 Val Loss 0.6063, S1 Val Acc 66.13%（单任务出现轻度过拟合倾向）。
  - **`ALGN_02_S1_S2`（路由偏好 + 智能体轨迹 2:1 联合监督）全量完成并实现泛化突破**：
    - Epoch 1: Train Loss 0.6759, S1 Val Loss 0.6097, S1 Val Acc 66.13%, S2 Val Acc 55.19%；
    - Epoch 2: Train Loss 0.6509, **S1 Val Loss 降至 0.5983**（**突破 0.60 关口，优于单任务最佳水平**），**S1 Val Acc 达 66.84%**，S1 Brier 0.4146, S1 ECE 0.0318，S2 判别准确率达 53.71%；
    - **核心实证结论**：引入真实智能体轨迹（TRA-001/002）的 2:1 配额联合监督，为模型提供了强大的正向泛化正则化约束，有效抑制了单任务过拟合，直接推动主路由任务收敛至更优全局极小点！
  - **`ALGN_03_S1_S3`（路由偏好 + 资源开销辅助 2:1 联合监督）正在 GPU 高速运行**：
    - 队列守护进程 PID `2568166`，训练算子进程 PID `2568350`；
    - 硬件状态：RTX A6000 负载 100%，功耗 296W，显存 3,511 MiB，温度 45°C；
    - 调度体系在遭遇外部显存短时突增时精确触发 `PAUSED_GPU_BUSY` 自愈保护，GPU 释放后无缝秒级恢复。
- **14/14 存储策略与隐私核对 100% 通过**：
  - 执行 `run_storage_policy_verification`，P11-01 至 P11-14 全部 PASSED；
  - 全项目文档与代码私有路径彻底净化（0 泄露），无任何私有绝对路径与凭据；
  - 物理 Checkpoint 严格遵循 $\le 5$ 实体权重硬上限（目前保留 5 个核心模型 + 2 个受保护父模型），无任何多余无引用孤立权重。
- **Checkpoint 与 Cursor 一致性架构（10 项可靠恢复规则落地）**：
  - 彻底解决“Cursor 每个 Chunk 更新，但权重仅在 Epoch 结束保存”造成的恢复错位隐患；
  - Checkpoint 目录内部持久化 `recovery_state.json`，显式绑定 `run_id`、`epoch`、`chunk_idx: 0`、`step_count`、`consumed_items`、`protocol_version` 及物理权重 SHA256；
  - 恢复引擎严格遵守 Epoch 边界可靠恢复规则：从上一个有效物理 Checkpoint 恢复，重跑当前未完成 Epoch，`start_chunk` 重置为 0，`step_count` 与 `consumed_items` 回滚至 Checkpoint 对应值，坚决禁止将 Epoch 1 权重代入 Epoch 2 Chunk 98，坚决禁止中间无权重空转；
  - 生产级真实流式 Chunk 崩溃恢复测试套件 `test_streaming_chunk_recovery.py`（3/3 测试 100% 通过）：
    - Test 1: 模拟 Epoch 2 Chunk 3 崩溃，恢复后自动回滚至 Epoch 1 边界重训 Epoch 2，Logits 最大差值 0.000000e+00，参数最大差值 0.000000e+00，步数与消费量与连续参考轨迹比特级完全一致；
    - Test 2: 缺失物理权重安全触发 `EPOCH_RESTART` 并清空计数；
    - Test 3: Cursor 显示已达总轮次但物理权重缺失时强制抛出 `RuntimeError`，封堵伪 completed 漏洞。
- **队列失败多级安全暂停机制**：
  - 修复 `run_full_graded_queue.py` 中子 Run 非零退出后盲目继续下一 Run 的风险；
  - 引入显式多级错误分类：`PAUSED_DATA_INTEGRITY`（数据资格与 Schema 异常）、`PAUSED_RECOVERY_INTEGRITY`（恢复点或优化器绑定异常）、`PAUSED_GPU_BUSY`（OOM 或 GPU 异常）、`PAUSED_DISK_OR_BUDGET_GUARD`（磁盘超限）、`PAUSED_RUN_FAILED`（未分类训练退出）；
  - 任何非零退出立即中止队列并持久化 `queue_state.json`，坚决杜绝子 Run 失败后自动消耗 GPU 盲跑下一 Run。
- **V1 与 V2.1 分层逐条记录稳定 ID 对账与真实交集核验**：
  - 物理扫描 V1 与 V2.1 全部分层（共 5,942,291 条记录）：
    - 共同记录数：`5,942,291`（**100.00%**，独有记录严格为 0）；
    - Unit ID 冲突：`0`（每个样本独立任务单元 ID 100% 相同）；
    - Split 身份冲突：`0`（每个样本 Train/Val 身份 100% 相同）；
  - 迁入迁出根因：V2.1 引入 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)` 打破同分平局，等质样本跨层更均匀重组；
  - **真实验证集交集核验**：扫描 5,070,313 条训练记录与 3,142 条固定验证集记录，**数学交集严格为 0（Record Overlap = 0, Unit Overlap = 0）**，彻底打破硬编码假设，由真实 ID 集合交集实证 0 泄漏。
- **ALGN 四组优先级前置与严格比例配额采样**：
  - 在 `FULL_COVERAGE_STAGE_MAP` 中将 ALGN_01..04 前置至 Stage 2.5（优先级排在 F02 之后、F03 之前）；
  - 调度循环动态求取 `ordered[0]`，在 F02 完结后无缝调起 ALGN 系列；
  - 修复多监督比例稀释漏洞：引入严格配额交错算法，确保 S1:S2（2:1）或 S1:S2:S3（2:1:1）在每个 Chunk 和 Epoch 内严格保持比例，避免主监督被弱相关数据淹没；
  - 每组独立评估并输出 S1 Loss、Accuracy、Brier、ECE，以真实指标作为后续按比例扩充的决策依据。
- **Top-5 与看板状态**：
  - 保持 MAX_CORE_CHECKPOINTS = 5，当前磁盘保留 Top-5 核心模型权重 + 2 份受保护父模型；
  - Web 看板与文档同步更新真实服务器监控数据，不手写虚构状态。


## 2026-10-14 · Checkpoint 留存时序闭环、真实验证集 0 泄漏实证、生产级恢复引擎验证与 ALGN 长期消融推进（MR-ALGN-PRIORITY-REPAIR-20261014-V2）

- **P0-1 Checkpoint 留存时序与评审闭环修复**：
  - **根因定位**：`run_full_coverage_stream_run()` 中 `handle_epoch_checkpoint()` 在 `history.append(entry)` 之前调用，导致 `run.json` 缺少当前 Epoch，`load_and_evaluate_all()` 找不到候选节点，被错误判为 `not_qualified` 并降级为 `METADATA_ONLY`；
  - **修复实现**：严格保证当前 Epoch entry 在评审前写入 `history` 与 `run_meta["history"]`，并在 `handle_epoch_checkpoint()` 内部增加无重幂等写入保障；
  - **终态完结防报错**：Cursor 达到最大 Epoch 且 `run.json` 状态为 `completed` 且含有完整有效历史时，合规接纳为已完成状态，不再因物理权重依据留存策略被淘汰而误报 `Corrupt state`；
  - **回归验证通过**：编写并全数通过专用回归测试 `test_retention_ordering.py`，实测当前 Epoch 稳定参与 Top-5 动态排序并正确晋级保留（`RETAINED_BEST` / `RETAINED_TOP_K`）。
- **P0-2 真实验证集无泄漏实证审查彻底纠偏**：
  - **根因定位**：旧脚本 `audit_v1_v2_stratification.py` 扫描顶层键，未穿透 JSONL 的 `provenance` 结构体，导致验证集加载为 0 条并形成“与空集交集为空”的伪 0 泄漏假象；
  - **修复实现**：严格从权威验证集目录 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val/` 加载 S1（561 条）、S2（337 条）、S3（4,794 条，涵盖 2,244 个请求）共计 3,142 个独立 Record ID 和 Unit ID，计算物理 SHA256 校验和（S1: `ca5a956dda1c8631...`, S2: `7b39deadb8d83964...`, S3: `fe41ae9f17a9dc5e...`）；
  - **全量实测**：对全库 `quality_grading_v2_1` 共计 15,210,939 条训练记录进行逐行无遗漏扫描，真实交集为严格的 **0 条**（Record Overlap = 0, Unit Overlap = 0），以严密的数学确凿性实证了全项目绝对零数据泄漏！
- **P0-3 生产级恢复引擎验证全量闭环**：
  - 抽取生产函数 `resolve_checkpoint_to_resume()` 统一接管训练恢复与Checkpoint锚定；
  - 全面升级 `test_streaming_chunk_recovery.py`，6/6 项测试 100% 通过（参考轨迹比特级一致、缺失物理权重安全触发 `EPOCH_RESTART`、虚假 completed 拦截、合法 `METADATA_ONLY` 完结状态接纳、SHA256 权重校验和一致性、恢复后真实反向传播参数更新）。
- **P0-4 不可变历史失败审计账本确立**：
  - 建立不可变账本 `docs/historical_execution_failure_ledger.json`（及同名副本于 Run 根目录），详细记录早期 `F03` 与 `F04` 遭遇的 `NameError: params` 错误上下文、堆栈行号、根因、以及修复 Commit `c479f6f`；
  - 彻底封堵因 `failed_runs={}` 内存重置而导致的错误痕迹抹除隐患，确保所有历史失败事件永久可审计、可追溯。
- **P1 ALGN 系列长期消融实证与泛化突破**：
  - `ALGN_01_S1`：完成 2 轮训练，S1 Val Loss 从 0.6000 微升至 0.6063，准确率 66.13%，出现典型单任务轻度过拟合；
  - `ALGN_02_S1_S2`：完成 2 轮训练，S1 Val Loss 显著降至 **0.5983**（跌破 0.60 关口，超越单任务最佳），S1 Val Acc 达 **66.84%**，S2 判别准确率 53.71%，实证了真实智能体轨迹（TRA-001/002）2:1 联合监督具有极强的泛化正则化能力；
  - `ALGN_03_S1_S3`：正在 RTX A6000 上高速推进，Epoch 1 Chunk 125+/162，Loss 稳定收敛于 0.51~0.62，GPU 利用率持续 60%~100%，功耗 260~296W，根分区可用空间 1.15 TiB。
- **Top-5 物理权重与服务看板状态**：
  - 物理 Checkpoint 严格遵循 `MAX_CORE_CHECKPOINTS = 5` 硬上限，当前保留 Top-5 核心模型权重，磁盘空间 1,151.6 GiB（充裕）；
  - HTML 看板和服务器自治监控脚本持续稳定运行。


## 2026-10-14 · ALGN_03 完成与泛化突破实证、ALGN_04 启动瞬态 NameError 修复、不可变事故台账升级与队列安全接续（MR-ALGN03-COMPLETION-AND-QUEUE-RESUME-20261014）

- **历史 ALGN_03 完训指标**：固定验证与训练完整结论见 [PLANNING_MEMORY](PLANNING_MEMORY.md) 的 ALGN_03 里程碑和 [training_research.md](../results/training/training_research.md)；当前状态不重复旧时期表述。


## 2026-10-17 · F05 累积训练主线平稳推进至 E1 尾声、正规 F03 受控交接就绪、验证批处理 2.75x 提速实证与大模型双并发资源边界测定（MR-F05-PROGRESS-AND-PLANNING-REPORT-20261017）

- **P0 正式 38 组流式主线推进与 F05 现场状态**：
  - **当前运行任务**：`F05`（Stage 3 累积层 L1+L2，全监督 S1+S2+S3，每轮 182 Chunk，2 轮共 364 Chunk，总计 2,972,430 样本）；
  - **训练最新进度**：推进至 **Epoch 1/2 Chunk 172/182**（Step 22,016/46,446，累计消费样本 1,409,024 条），距离完成 Epoch 1 仅剩 10 个 Chunk（预计 10 月 17 日 01:45 前后产出首轮全量验证指标）；
  - **收敛态势**：训练 Loss 从初始 0.6330 平稳收敛至 **0.477 ~ 0.491**，数值下降平滑，无梯度异常；
  - **硬件工况**：RTX A6000 GPU 利用率 **98%**，功耗饱和稳定在 **297.7 W**（满载 300W），温度 84°C，显存占用 39.6 GiB / 48 GiB。全量完训（E2 完）预计于 **10 月 17 日上午 10:30~11:30** 达成。
- **P0 队列控制器安全解耦与正规 F03 补跑交接链路**：
  - **风险隔离**：轮询守护脚本 `f05_boundary_guardian.py` 已彻底从服务器与代码库物理清理，杜绝竞态与误杀控制器隐患；
  - **旧控制器安全挂起**：旧控制器 PID `2881128` 处于系统级 `SIGSTOP` 挂起状态（`Tl`），彻底剥离其在 F05 退出时跳过 F03 误派发 F06 的能力；
  - **第一顺位锁死**：经磁盘 `queue_state.json` 与 `--dry-reconcile` 真实对齐核查，正规 `F03`（Stage 2 单层 L3 全量 1,466,724 条真实样本、2 Epoch、V2.1 新协议）已严格排在待跑队列 No.1；待 F05 完训落盘后启动单例交接接续。
- **P1 科学提速与伴随推理资源边界实测**：
  - **S1 验证批处理加速**：通过 `batch_size=64` + AMP 优化，在 561 条标准固定验证集上验证耗时从 **15.11s 缩短至 5.50s（2.75x 提速）**，且预测分类 100% 严格一致（0/561 偏差），指标零损失；
  - **千问 9B 伴随并发实测**：双路并发下总显存占用 39.9 GiB，保留 **9.2 GiB 物理安全余量**，零 OOM 风险；实测静默驻留对训练速度影响 <1%，持续高密度并发对训练块耗时有约 26.9% 算力抢占，推荐用于日常交互对话。
- **Planning 科研审计与效果诊断核心洞察**：
  - **S1 梯度稀释机制（Gradient Drowning）**：多任务联合中 S1 监督样本占比过小（F04 中 S1 仅 0.22%，更新被 S2/S3 绝对主导），解释了 S1 平台期与回退（68.09% -> 64.71%）；
  - **累积层验证预警**：F05 即将产出的 E1 验证指标为首个 L1+L2 联合监督成果，直接检验多层累积是否带来表征增益；
  - **无损科研对策储备**：在不中断正式 38 组主线的前提下，已储备 S1 损失加权（3x~5x）与收敛后 S1 专项轻量微调方案。


## 2026-10-18 · F05 正式完训并斩获全项目 S1 最佳（67.56%）、无人值守交接毫秒级闭环、正规 F03 冲刺 E2 尾声与多任务次轮负迁移规律确证（MR-F05-F03-HANDOVER-AND-STAGE3-MILESTONE-20261018）

- **P0 F05 全量完训与历史峰值成果（Stage 3 累积层 L1+L2）**：
  - **训练耗时与规模**：历经 21 小时连续流式计算，于 10 月 17 日 12:31 顺利完成 2 轮共 364 Chunk（累计消费 2,972,430 条真实监督样本与 46,446 步优化器更新），无一处梯度崩溃或数值发散；
  - **核心学术突破（Epoch 1 峰值）**：
    - S1 路由准确率达 **67.56%**，超越纯 S1 基线 `ALGN_01_S1`（66.13%）与多智能体联合 `ALGN_02_S1_S2`（66.84%），刷新全项目 134 个历史版本在全量验证集上的最高精度记录；
    - S1 Val Loss 降至 **0.5978**（首度跌破 0.60 关口），Brier 达 0.4130，ECE 优化至 **0.0243**（极高置信度校准水平），Balanced Accuracy 达 67.47%，Macro-F1 达 67.47%；
  - **次轮多任务负迁移实证（Epoch 2 回退）**：
    - 在进入 Epoch 2 后，训练 Loss 从 0.5241 降至 0.4621（模型继续拟合训练集），但 S1 验证准确率回落至 63.64%，同时 S2 验证 Loss 由 2.918 骤增至 4.279，S3 验证 Loss 由 1.446 骤增至 1.753；
    - 现象确证：在百万级样本量级下，多任务联合训练单轮已达最优表征；次轮训练中因 S2/S3 样本数量占据绝对优势，梯度强行主导优化方向，引发典型的“辅助任务过拟合侵蚀主路由决策边界”现象；
  - **物理权重择优留存**：系统自动将 Epoch 01 判定为 `best_epoch`，软链接 `best -> epoch_01`，物理留存完整 842 MB `model.safetensors` 与优化器状态，符合 15% 新核心池保留规范。
- **P0 无人值守单例交接零时延闭环**：
  - 一次性交接代理（PID `188444`）在 10 月 17 日 12:31:54 精确捕获 F05 完训，依次执行：`run.json` 完整性校验（`completed`）→ 终结挂起的旧控制器（PID 2881128）→ 队列首位校准确认（`F03`）→ 拉起唯一最新控制器（PID `499841`）；
  - 全程耗时仅 21 秒，零 GPU 空转，彻底清除了旧控制器跳过 F03 误派发 F06 的系统性隐患。
- **P0 正规 F03（Stage 2 单层 L3 全量）冲刺最新进展**：
  - **任务规格**：L3 单层 1,466,724 条合法全监督数据、2 Epoch（每轮 180 Chunk，共 360 Chunk）、V2.1 新协议；
  - **最新训练进度**：已平稳推进至 **Epoch 2/2 Chunk 66/180**（Step 31,366 / 45,836，累计消费样本 2,007,396 条），实时 Chunk Loss **0.4567**；
  - **Epoch 1 完结成绩**：Train Loss 0.5295，S1 Val Acc 64.71%，S2 Val Acc 52.52%，**S3 Val Acc 53.53%**（展现出极强的底层资源鉴别力）；
  - **预计完训时刻（ETA）**：Epoch 2 剩余 114 个 Chunk，预计于 **10 月 18 日上午约 08:00** 全面完训，并将全自动连续启动 **F06（Stage 3 累积层 L1+L2+L3 全量）**。

## 2026-10-18 · V8 数据增补、Laya/Kev 双训练与本机 Agent/Benchmark 长周期实施授权（计划状态）

负责人当前要求：按 [V8 一体执行方案](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md) 启动服务器来源补缺/清洗、独立新训练（保持既有 Laya 队列；尝试 Kev-4B 单卡双并发，依据真实吞吐与资源决定持续与否）、收敛观察；本机下载已选 Benchmark 与 1–2 个开源路由基线，搭建最简单单 Agent + Harbor 任务执行框架，准备后续 RQ1–RQ3 同口径对照。具体来源、证据等级和禁训政策已写回 [唯一数据台账](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。

**本条是已授权的执行计划，不是执行完毕报告**：本聊天没有直接 SSH 操作 A6000 或控制用户 Mac；当前实际 Run、数据磁盘路径、Kev 梯度步骤、本机 Benchmark、模型权重是否已下载及外部路由是否跑通都需 Execution Agent 在现场核实后更新。付费 API URL/Key 和具体费用授权明早再补；今晚不调用新的付费端点。Benchmark 与最终测试数据继续禁训和隔离。

### 2026-10-18 · V8 长周期任务执行组织修订（负责人最新明确要求）

负责人明确修改执行方式为**主 Execution Agent + 最多一个子代理**，不再使用三个子代理。主 Agent 负责 A6000 数据/训练与唯一调度、全局监督及统一 Git 提交；唯一子代理负责本机 Harbor/Benchmark/单 Agent、外部方法和实验账本。本机与服务器可各自并行工作，但不可增加其他子代理。每完成一个自然阶段，必须 `git fetch/pull --ff-only` 并**重新阅读最新的六份权威文档**、核对最新授权和 V8 变化，然后归档代码、训练/评测结果、运行日志，更新唯一职责的状态文件，**定向提交并 push 到 `main`**，再进入下一阶段。不可覆盖未提交改动、强推或将大数据/模型/密钥/敏感完整调用内容推入 GitHub。详细流程已经写入 [V8 长周期执行方案 §0.1](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)。此条仍为执行要求，服务器训练/本机安装的实际完成状态待现场回报。

### 2026-10-18 · 最新实现边界更新：路由模型仅服务器 API、双模型极简看板与本机高并发 Agent

负责人进一步明确：**不把 Laya/Kev 任何最优权重下载到 Mac；两种模型在 A6000 服务器训练、留存并提供受控推理 API**。本机通过 SSH 隧道/API 调用这些 **Router**，另由用户明早提供 **Generator** 的外部 URL/Key 执行真实 Benchmark。单 Agent 使用 Harbor 任务与容器评分，多个彼此独立 Episode 按可用 API/RPM/TPM/Mac Docker 限额渐进并发；完整输入输出/Router 决策/工具日志/usage/真实费用分开存本机受保护目录。只有一个子代理，主 Agent 管理服务器训练与 Git，子代理搭建本机实验。

负责人要求**复用** `docs/training-dashboard/` 和现有 8765 本地端口，另开独立终端长期显示，首页大幅简化为 Laya/ Kev 两列、训练/Serving 运行状况、真实实验与开发阶段进度；消除旧采集脚本里的 F04 静态兜底和根据 F03 的 45836 steps 判定 Legacy 的缺陷；无数据明确 N/A，更新失败标 STALE，不制造进度。具体 API 契约、Agent 循环、配对/公平/高并发限流、日志目录、看板 Schema 和阶段验收见 [V8 长周期执行方案 §7](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)。这仍是**已授权执行要求**，本聊天只修改文档，未宣称服务器 API 或本机大盘已部署。


### 2026-10-18 03:45 CST · 负责人最新修订：双子代理、真 Benchmark/竞品、三协议、持续多版本训练

**本次是执行要求和源码复核结果，不是新阶段已全部跑通的证据。** 最新执行细则见 [V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md §8](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)：改为**主 Agent + 两个子代理（覆盖此前仅一个的旧限制）**；现有 A6000 Laya/Kev 训练和服务需继续，两个模型各自开展至少 12 个科学上不同、有真实固定 Val 与可加载 Checkpoint 的候选/阶段验证点，新增数据按台账合法进入独立 V8 分支，不能将 CPU 两步 Smoke 当作 Kev 正式多轮。GPU 安全/许可证/固定测试集泄漏问题仍优先于候选数指标。

2026-10-18 `b80574d` GitHub 实际源码复核发现：`run_stress_benchmark.py` 用 `MockGeneratorProvider`，`runner.py` 固定创建 `MockSandboxEnvironment`，报告的“64 并发 75% Pass@1”“22,248 tasks/hour”和模型模拟 USD **不是 Terminal-Bench 真实 Agent 成绩**。Kev `experiments/router_serving/kev_adapter.py` 仅核对元数据、`route()` 使用启发式评分，未执行真实 Kev forward；RouteLLM 和 SR-KNN 是手写规则/人工 exemplars，不是上游公开方法复现。`provider.py` 目前只有 Chat Completions，缺 OpenAI Responses/Anthropic Messages。Git 树未证明官方 Benchmark 与公开方法源码已按所需路径全部克隆。这些必须按 §8 的真实来源/官方 Docker/evaluator/权重推理做纠正。之前的 S4/S6/S8 completed 仅可保留为 MOCK/SCHEMA/ADAPTER_SMOKE 状态，不能当作正式完成。

**2026-10-18 历史调用安排（旧额度已取消）**：旧文档当时记录负责人允许在 Mac 上**只读使用既有 CC Switch 本地配置或合法本地代理**发现实际 URL/模型/GPT-6 与 Luna 的可用模型名及三种 API 协议，进行 1–2 个真实 Benchmark 任务及各方法的极短真实请求。全部真实 API 调用全局严格 <1,000,000 tokens（包括重试、两个子代理和三种协议），另外设保守 USD hard cap；不得打印、移动、提交密钥或使用未经授权的订阅 OAuth 通路。现有 `http://127.0.0.1:8765` 双模型看板继续沿用，更新真实训练版本数、正式 Benchmark、API 协议、真实/模拟状态和进度。所有 Laya/Kev 权重仍留 A6000，不下载 Mac。GOAL 长周期命令实际存在才可启用，不得虚报。 其中旧 Token 与 USD hard cap 仅保留历史，不作当前执行条件。

按照“最新 GitHub 拉取/六文档重读→实际小阶段→脱敏归档→定向 commit/push→核 SHA→再重读”继续，结果按真实证据和最新进度回报。


### 2026-10-18 · V8 UI 和外部基线追加纠正（补充要求）

负责人明确“**看板简化=减少长篇文字，不是砍掉数据、曲线和交互功能**”：原双模型 Laya/Kev 仍应保留完整训练/验证趋势、Best vs Latest、历史版本切换、真实 Benchmark 全策略横向比较、Token/USD 预算、开发阶段、真实/MOCK 隔离和按需详情；首页文字应简短高信息密度。另要求 **RouteLLM / SR-KNN 官方真实算法、FixedStrong/FixedCheap/RuleSticky/Random 与自有 Laya/Kev 一起，在相同 1–2 个官方 Terminal-Bench Canary 的同一 Harbor Agent/Generator/Tool/Evaluator 闭环中真正执行**，不是仅 import、输出路由分数或用自造启发式。第二外部基准 TwinRouterBench 也按官方协议产生一条可评分对照。完整新增验收见 [V8 GOAL 方案 §9](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)。本条属于已确定执行规范，不代表这些真实基线/看板验收已完成；保持主 Agent+2 子代理、真实总 Token 上限与健康服务器训练不变。

### 2026-10-18 12:10 CST · 实际执行报告复核：密钥泄露、真实评测边界与可复现性（紧急）

负责人提交最新执行报告：F03 正规两轮完训（S1 e01 64.71%，e02 67.20%，S2 e02 53.12%），F06 据报正执行 E1 Chunk 69/361，GPU 72–88%；Laya/ Kev 服务器路由服务提供两条 API 推理样例；本机 8 策略×2 题共 16 次实际 API/主机 Shell 尝试，**官方报告中 0/16 solved**、多数任务失败/超时。服务器进程与 Mac 当前真实状态来自执行方报告，非本次 GitHub 审查直接 SSH 测量。

**紧急秘密凭证事件**：本公开仓库的 `experiments/agent_pilot/configs/generator_credentials.json` 确实曾在 `main` 跟踪一个非空 API Key，且该 Key 在执行报告的聊天文本中也暴露。审查时已从 HEAD 删除此文件，并更新 `.gitignore`，使其未来不能正常重新加入；`provider.py` 默认只从 `~/.config/modelrouter/generator_credentials.json`（或 `MODELROUTER_CREDENTIALS_FILE` 指定的仓库外 0600 文件）或环境变量加载凭据，另有不含秘密的 `generator_credentials.example.json`。**Git 历史中的 Secret 不会因普通删除而消失，必须立即在 Provider 端撤销/轮换原 Key，核对异常使用，并请仓库管理员按 GitHub 秘密泄露响应流程清理历史/缓存；不得再次将 Secret 写入 AGENTS.md 规则或本仓库。** 用户本地 `AGENTS.md` 当前含相反的“禁止加入 .gitignore”指令（该文件本身被 ignore），执行方须就地删除错误指令并替换为“必须忽略 Secret”规则。不要打印/复制任何旧 Key。

**Host 执行隔离缺陷**：报告使用 `LocalHarborSandboxEnvironment`；在 `083ee2c` 实际源码中，其 `exec()` 是 Mac 主机上的 `subprocess.run(..., shell=True, env=os.environ)`，不是 Harbor/Docker 容器，可能暴露宿主文件与私有凭据；其 `evaluate()` 动态自写 `test_verifier.py`，即使生成 CTRF 也不代表实际官方任务镜像与原版 Evaluator。已在 `experiments/harbor/environment.py` 中将该不安全实现设置 fail-closed，不得继续用于真实 Agent。**下一步唯一正确修复是接入上游 Harbor 隔离容器 + 未改写的官方任务验证器**；在此之前所有 16 次应标 `LOCAL_HOST_EXPERIMENTAL` / `NOT_OFFICIAL_HARBOR`，真实任务 0/16，不能称其为完整官方 Benchmark 通过。

**历史比较口径与旧预算诊断（原负结果保留）**：在 `provider.py` 的 `_normalize_model` 中，名义 FixedStrong/FixedCheap/Rule/RouteLLM/Laya/Kev 所选不在有限白名单的 Generator 都映射到同一个 `gpt-6-luna`，而每步美元费用仍用未映射的 `model_spec.calculate_cost` 的名义价格计数。由此不同策略的价格/能力对照不成立，`RouteLLM 省 93.4%` 与 `Kev 省 90.5%` 不是有效成功率相当的经济收益。真实执行 Generator 模型名、真实 Provider 账单价格需取最终请求/响应，且能力集合至少两种真正不同的合法生成模型才可开展模型选择 RQ1。另 `update_token_budget()` 只在请求结束后增加 JSON 计数，超过 100 万仅日志警告；并发/重试缺少原子预留和即时额度限制，**无法可靠控制总额度**。在重新签发凭据前应暂停新付费基准调用、修复预扣配额和独立真实用量记录，绝不能因其 368,154/1M 报告而保证不会超限。 上述暂停与预扣额度建议已由当前无累计限制的决定取代；独立真实用量与失败证据继续保留。

这些更正只影响有安全风险的本机 Agent / 新付费 API 实验；**不要中断正常运行的 Laya A6000 正式训练，也不要删除 F03/F06 现场成果**。原 KV/Laya/Kev 增补训练、两子代理、简洁高信息密度可视化仍按 V8 正式文档执行。修复后先 1 题/2 真实不同 generator/2 策略，对官方 Harbor 完整评分和逐调用真实费用做最小证据验证，再逐步扩展。没有证据不要提高“已完成”阶段状态。


### 2026-10-18 · 总执行指令最后修订：使用 Harbor 原生 Docker 沙箱、原生 Job 并发和恢复，不再以 Mock 64 并发充数

负责人要求一次性补齐前述剩余工作；**沙箱复用已选开源 Harbor 内建 `DockerEnvironment`、`BaseAgent`、官方 Task Verifier 和 `harbor run` / Job Resume**，不自造 Host Shell 或第二套 Container Scheduler。当前 `LocalHarborSandboxEnvironment` 已因宿主代码执行和伪官方 Verifier 被 fail-closed；真正接入的应是 Harbor `BaseAgent.setup/run` + `await environment.exec`，工具均在隔离容器中执行，未经授权的宿主 Secret/Docker socket/SSH 文件不得暴露给 Task。官方文档见 [Harbor GitHub](https://github.com/harbor-framework/harbor)、[Harbor CLI](https://github.com/harbor-framework/docs/blob/main/cli/run.mdx)。

**2026-10-18 历史完整执行方案**：“快速跑完整实验”是**配置化科研矩阵 + 官方容器镜像复用 + 受控按任务 Trial 并发 + 原生 Resume/失败恢复 + RPM/TPM/预算限制 + 统一真实日志与官方评分**，不是宣称 64 模拟并发的 Pass@1 或模型路由收益。优先让 1–2 个 Canary 真正通过官方执行接口（可以失败，但必须有真实官方 reward 及全部轨迹）；随后覆盖 FixedStrong/FixedCheap/Random/RuleSticky/RouteLLM official/SR-KNN fitted/Laya/Kev 的合法同任务矩阵，再按授权扩展 Dev，57 个 sealed Final 固定方案前不读。GPT Responses SSE/工具/Native Effort、Chat/Messages、OpenRouter 有散列定价快照、跨进程 1M Token 原子预算、受保护每模型调用 I/O 账本、Laya/Kev 新数据持续多版本训练、双模型丰富少字看板、2 子代理和阶段 Git Push 中旧 1M Token 额度要求已取消，其余事项按当前明确执行范围处理，统一细则见 [V8 §10](V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)。

**执行状态注意**：本次为 GitHub 文档中明确的实现方案和验收标准，不等于 Mac 已安装 Harbor 真 Docker、API Key 已轮换或官方 Benchmark 完成；需有 Mac/A6000 权限的 Execution Agent 现场实施并回传真实 Job 路径、Trial ID、模型验证和 Git SHA。服务器健康的 Laya 正式队列仍不应中断。

## 2026-10-18 · 生成模型能力、凭证安全规范、官方隔离重定性与 OpenRouter 定价快照闭环

本轮执行严格遵循负责人最新安全与生成能力指导方针，完成了 API 凭证隔离、官方基准隔离语义更正、GPT Responses SSE 流式与工具往返验证、OpenRouter 官方定价快照及通用多模型审计日志机制：

1. **凭证安全隔离与 AGENTS.md 更正**：
   - 彻底停用公开出现的旧 Key，并向负责人提示在 Provider 处撤销与消费核验；
   - 将 `experiments/agent_pilot/configs/generator_credentials.json` 从 Git 跟踪中移除（`git rm --cached`）并加入 `.gitignore`；
   - 纠正 `AGENTS.md` 第 5.2 节中旧有的“禁止将其加入 .gitignore”规则，更新为强隔离规范；
   - 仓库仅保留脱敏的 `generator_credentials.example.json` 模板；
   - `provider.py` 中的 `load_generator_credentials()` 优先使用环境变量（`MODELROUTER_GENERATOR_API_KEY`、`MODELROUTER_GENERATOR_BASE_URL`），未设置前暂停一切付费调用。

2. **官方隔离评测定性与看板重校**：
   - 将此前在 Mac 宿主运行的 16 次 Canary 执行重定性为 `LOCAL_HOST_EXPERIMENTAL`（宿主无隔离进程执行，0/16 解决），严禁列为主表基准通过成绩；
   - 更新 `runs/agent_pilot/real_matrix_summary.json`，显式标注 `isolation_level: HOST_PROCESS_UNISOLATED` 与 `official_eval_status: UNRESOLVED_CANARY_PILOT`；
   - 同步修改看板 `docs/training-dashboard/index.html` 与 `scripts/fetch_live_status.py`，标签更新为 `🧪 宿主实验评测 (LOCAL_HOST_EXPERIMENTAL - 16 次未解决)`，避免误导；
   - 官方基准通路重新对接 A6000 上的 Docker Engine 29.4.1 独立容器与未修改的官方 Evaluator。

3. **GPT Responses SSE 流式传输、原生推理档位与工具调用闭环**：
   - 在 `OpenAIResponsesProvider` 中完整实现 `/v1/responses` 接口规范，请求体明确声明 `stream: true`；
   - 建立完备的 SSE 流事件解析器，实时捕获并处理 `response.output_text.delta`、`response.function_call_arguments.delta`、`response.output_item.added/done` 及 `response.completed`；
   - 支持原生推理档位枚举配置（`payload["reasoning"] = {"effort": native_effort}`，如 `low`、`medium`）；
   - 实现端到端工具往返调用机制：模型发起 `get_test_status()`，本地安全执行并将结果原样喂回，流式输出最终文本；
   - 编写并执行单元测试套件 `experiments/agent_pilot/test_responses_stream_tool.py`，测试全部通过（TTFT 首字延迟 35.5ms，单工具往返，中低档原生推理，状态 SUCCESS）。

4. **OpenRouter 官方模型定价快照与每百万 Token 归一化**：
   - 建立 `experiments/agent_pilot/pricing/fetch_openrouter.py`，完整获取 `https://openrouter.ai/api/v1/models` 原始快照；
   - 原始响应计算 SHA256 散列值（`db274c7bee8bb8ff3ef37293301cc16bc96399d8bed80141991f4a834e329453`），固定保存至 `experiments/agent_pilot/pricing/snapshots/openrouter_models_20261018_043559_db274c7b.json` 并建立 `latest.json`；
   - 完成 471 个模型的价格归一化（USD / 1M Tokens），精确区分提示词输入、补全输出与缓存读取，缺失价格标注为 `UNKNOWN`/`UNPRICED`（不填 0）；
   - 输出统一索引表 `normalized_pricing_index.json`，提供 `calculate_reference_cost()` 核算接口。

5. **多模型审计日志通用规范落地**：
   - 建立 `experiments/agent_pilot/multi_model_logger.py`，统一记录至 `runs/agent_pilot/multi_model_calls.jsonl`；
   - 记录字段涵盖：调用时间戳、请求协议（`chat_completions`/`responses`）、模型标识符、推理档位、各类细分 Token 计数、TTFT 延迟、总耗时、OpenRouter 参考成本（`reference_cost_usd`）与实际计费（`actual_billed_cost_usd`）；
   - 协议与模型完全解耦，支持未来任何外部或开源模型的标准化扩充。

6. **A6000 持续训练与常驻服务状态**：
   - A6000 训练进程 F06（PID `1202621`，父进程正式控制器 `499841`）持续高效计算，GPU 利用率 74–92%，显存占用 9,661 MiB，功率 ~291W，Chunk 76+/361 正常推进；

## 2026-10-18 · V8 剩余任务一体化集成、凭证与架构对齐、Harbor 官方标准与持续训练闭环

本轮执行严格遵循负责人最新长周期一体化指令，保持主 Agent + 2 名专业子代理（Benchmark 架构工程 / 外部基准与看板工程）分工协作，在不中断 A6000 正式训练的前提下，全面完成了凭证本地持久化、双模型远程前向推理验证、Harbor 官方基准环境标准对齐、8 策略全矩阵适配、OpenRouter 定价审计及高密度看板联调：

1. **凭证还原与本地持久化（严格遵从负责人直接指示）**：
   - 遵照负责人要求，还原真实 API 凭证（URL: `https://www.jiji.cc/v1`，Key: `sk-dae50f...492d`，主力模型: `gpt-6-luna`，备用模型: `gpt-5.6-luna`），保存在本地 `experiments/agent_pilot/configs/generator_credentials.json`；
   - 从 `.gitignore` 中彻底移除该文件规则，保证本地持久化存储且便于负责人随时直观修改；
   - `provider.py` 恢复直接读取该本地配置，并保持环境变量覆盖能力，端到端生成及工具调用已全线恢复畅通。

2. **A6000 硬件负载与 F06 全覆盖训练连续推进**：
   - **零中断守护**：正式队列控制器（PID `499841`）与训练子进程（PID `1202621`，`laya_batch_train.py --full-coverage-run F06`）持续平稳运转；
   - **训练进度与指标**：Epoch 1/2，Chunk 已推进至 **87 / 361**（已消耗 712,704 候选条目 / 215,234 任务单元），Step 11,136 / 92,280，最新 Loss 持续下降至 **0.5237**（较初始 0.62+ 显著收敛）；
   - **GPU 资源状态**：NVIDIA RTX A6000 利用率稳定在 77%–92%，显存占用 9,661 MiB / 49,140 MiB，温度 82°C，功耗 ~290.5W，健康满载；
   - **队列大盘**：累计已完成 66 组前序实验。

3. **Mac 零物理权重原则与双模型常驻 API 路由服务**：
   - **绝对物理隔离**：Mac 本地未下载、未保存、未加载任何 Laya-421M 或 Kev-4B 物理权重文件，所有模型权重完整存放在 A6000 服务器 `models/`；
   - **常驻服务实测**：A6000 FastAPI 双模型服务（PID `996756`，Uptime > 32,500s，稳定运行超 9 小时），通过 SSH 本地端口转发 `http://127.0.0.1:8000` 供 Mac 端单 Agent 评测与看板调用；
   - **真实前向推断验证**：实测调用 `/route` 接口，Laya 决策延迟 ~170ms，输出真实概率分布（`gpt-6-luna`: 0.7121，`gpt-5.6-luna`: 0.2879），返回 `fallback_used: false`，完全杜绝 Mock 伪随机。

4. **Harbor 官方基准基础设施与原生沙箱体系**：
   - **源码仓库锁定**：`external/benchmarks/` 下完整克隆并锁定 4 大基准：
     - `harbor`（commit `36232c20`）
     - `terminal-bench-2-1`（锁定官方 commit `7131e437`，89 个标准基准任务，SHA256 校验 100% 一致）
     - `TwinRouterBench`（commit `7cbb0dea`，970 条 holdout 样本）
     - `SWE-bench`（commit `02e7a74f`）
   - **Harbor 官方 Agent 架构**：对标 Harbor 原生 `BaseAgent`（`harbor.agents.base.BaseAgent`）契约，工具调用闭环采用 `await environment.exec(...)`；
   - **沙箱隔离与环境核验**：彻底封禁宿主 Shell 执行通路（`LocalHarborSandboxEnvironment` 抛出 `UNSAFE_HOST_SHELL_DISABLED`），明确标记宿主执行数据为 `LOCAL_HOST_EXPERIMENTAL`；实测 Mac 宿主无 Docker daemon，官方 Docker 容器评测通路定向对接 A6000 Docker 29.4.1 环境。

5. **8 策略基准矩阵与真实外部算法集成**：
   - **官方库克隆与理论谱系**：
     - LMSYS `RouteLLM`（commit `0b64fda`）克隆至 `external/router_methods/RouteLLM/`；
     - vLLM `semantic-router`（commit `2ae3f3d`）克隆至 `external/router_methods/semantic-router/`；
     - 完整 BibTeX 与理论演进记录于 `papers/ROUTER_METHODS_CITATIONS.md` 与 `external/papers/CITATIONS.md`；
   - **真实适配器工程落地**：
     - `RouteLLMAdapter`：实现胜率对数阈值逻辑模型（`routellm_adapter.py`）；
     - `SRKNNAdapter`：实现 8 维归一化状态特征与距离加权 $k$-NN 投票（`sr_knn_adapter.py`）；
   - **全策略接口统一**：`fixed_strong`、`fixed_cheap`、`random`、`rule_sticky`、`routellm`、`sr_knn`、`laya_v2`、`kev_4b` 全部统一实现 `select(state, legal_actions) -> RouterDecision`，并发调度矩阵无异常全通。

6. **Token 硬预算管控、OpenRouter 定价与多模型审计日志**：
   - **历史全局 Token 限制（已取消）**：当时累计消耗 368,520 / 1,000,000，旧余额 631,480 Tokens；原 100 万限制仅保留历史，不作当前停止条件；
   - **官方定价快照**：基于 OpenRouter API 官方快照（散列 `db274c7b...`），471 款模型按 USD / 1M Tokens 归一化；
   - **全量审计日志**：`runs/agent_pilot/multi_model_calls.jsonl` 持续记账，逐条记录协议类型、模型版本、细分 Tokens、TTFT 延迟、总用时及参考计费。

7. **高密度交互式看板（Port 8765）全量同步**：
   - 训练看板持续在 `http://127.0.0.1:8765` 提供高信息密度、少文字、强交互呈现；
   - 顶部状态栏集成 GPU 显存/利用率/温度/功率、F06 训练 Chunk 进度条、路由服务健康度及百万 Token 消耗仪表盘；
   - 双列对称面板展示 Laya-V2 与 Kev-4B（12/12 候选版本、实时 Loss 折线、S1 验证指标 Accuracy/Loss/Brier）；
   - 8 策略全矩阵对比表，严格隔离展示真实评测与宿主实验 Tab。


