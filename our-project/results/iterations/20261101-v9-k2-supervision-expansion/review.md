# V9 K=2 真实监督增量（2026-11-01）

| 统计 | 本轮新增 | 累计 |
|---|---:|---:|
| 尝试的不同 Train 任务 | 3 | 不作为有效标签数 |
| 完整、可比的任务对照 | 2 | 3 |
| 有效任务级偏好 | 1 | 2 |
| 有效步骤级偏好 | 1 | 2 |
| 提供有效偏好的不同任务 | 1 | 2 |
| 完整 K=3 / 同模型 Effort 偏好 | 0 / 0 | 0 / 0 |

实际动作固定为 Sol low、Luna low；教师关闭，AA 固定 v4。两条新增目标均来自 DeviceAuthorizationEndpoint 任务，Scope 与它属于同一仓库，关联保留。原独立评测标签未用于训练、调参或重新选版本。

| 新任务及原始验证 | Sol | Luna | 监督资格 |
|---|---|---|---|
| OAuthlib DeviceAuthorizationEndpoint | Submitted，673/673，$0.1069349，148.68 秒 | Responses：Submitted，673/673，$0.0045224，142.13 秒 | 等验证结果下的 Luna 费用偏好 |
| SQLparse 输出格式 | Submitted，331/331，$0.2730552，386.96 秒 | Responses：3 次返回后 response.failed，原验证 328/331；已知 $0.0034449，完整费用未知 | 环境请求中断，只作观察 |
| OAuth2 scope/URI 工具函数 | Submitted，670/673，$0.1373102，337.47 秒 | Submitted，668/673，$0.00873728，73.04 秒 | 完整可比，两边均失败，无胜者 |

| 同前缀步骤 | 实际反馈 | 目标 |
|---|---|---|
| OAuthlib Sol 历史 prefix5 | 两边继续读取，均未通过 | 无 |
| OAuthlib Sol 分支 prefix6 | Sol 只改测试；Luna 调用不存在的 apply_patch，均未通过 | 无 |
| SQLparse prefix5 | Sol 达到 4096 输出额度，函数参数不完整；Luna response.failed | 无 |
| OAuthlib Luna 历史 prefix6，首次 Sol 请求 | Sol RemoteDisconnected、无工具；Luna 一步 673/673 | 首次失败只作观察 |
| 同一 Luna 历史 prefix6，一次后续 Sol 请求 | Sol 执行一步但未改源码，660/673、$0.0278585；复用已保存 Luna 一步 673/673、$0.00062815 | 有效即时步骤偏好 Luna；不描述完整 Episode 胜负 |

Sol 连接断开的请求、未知 Usage 和原始失败单独保留，没有将它当质量败者。后续请求使用相同过去消息、原快照与原输出额度。时间包含共享 Token 账本等待，不能解释为纯模型速度差异。

| 费用与输入 | 实测 |
|---|---|
| 生成请求 / 有 Usage 返回 / 无 Usage 请求 | 68 / 65 / 3 |
| 已知模型费率小计 | $0.67589603；完整模型费、供应商实收与资源 USD 未知 |
| 教师 | 0 请求、$0；原有效教师 $0.0189335 不重复计入本轮 |
| 新 Train 增量 | 2 条，原 Prepare 与共享序列化已消费；两个问题 ID 分开 |
| 可组合材料 | 原 Train196/Val186 + 旧偏好2 + 新偏好2 = Train200/Val186；旧视图未重加工 |
| 能力与教师输入 | v4、teacher=null；low/none/Flash 缺测，Max 不作为 low 分数 |
| 当前训练 | 03:21:31 台北无活动训练，F14 仍 failed/NON_FINITE_LOSS；接续代表 F11-e01/R11，Serving F05-e01/原 Kev Adapter |

## 已保存四档材料的分析

| 四档 | 独立标签 | F11-e01 预测 | R11 预测 |
|---|---:|---:|---:|
| low | 689 | 173 | 13 |
| mid | 62 | 788 | 53 |
| mid_high | 49 | 2 | 588 |
| high | 170 | 7 | 316 |

旧 S1 人类候选偏好、S2 观察终局和 S3 Token/复用/quota 档位，与外部能力四档语义不同。R11 本次继续训练的 4269 行只有 S2/S3，没有四档 choice；Laya 微调前已在 950/970 步预测 mid。原外部入口截取前 400 字符，970 步只有 318 个不同 Context，58 个多步任务的 Context 不变。目标和输入差异已确认，各因素对偏置的独立因果贡献仍未知。八版本未重评。

## 原文件

- [精确统计](summary.json)、[原始四档分析](four_tier_analysis.json)、[任务隔离](task_isolation.json)、[Provider 目录](provider_availability.json)。
- [新增真实偏好](supervision.jsonl)、[观察结果](observed_outcomes.jsonl)、[全部新请求](requests.jsonl)、[训练增量](training_delta/summary.json)、[实际序列化](training_delta/encoding_observation.json)。
- [原请求失败及完整 Episode](oauthlib/episodes/)、[步骤响应](oauthlib/steps/)、[SQLparse](sqlparse/)、[Scope](oauth2-scope/)、[服务器取样](server_snapshot.json)。

下一轮训练尚未启动：当前仅两个提供标签的任务、均为 low；独立任务覆盖、新动作 Val/Dev 和完整 K=3 仍缺。保持原 S1，分别使用 task/step 目标；教师截止前摘要与 AA 卡沿原 formatter，Laya encoder/head、Kev LoRA/pointer head 的具体更新配方仍待这些真实目标支撑。独立真实 Dev 的动态 Router、教师净收益及五 RQ 正式比较尚未完成。
