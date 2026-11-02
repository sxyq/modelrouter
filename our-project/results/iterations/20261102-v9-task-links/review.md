# ModelRouter V9 · 真实来源关联与动作前状态执行记录

## 当前执行结果（接续 e222deadc19854d2a7a32a731c5f0e4610f6690e）

任务关联、原环境和新STEP训练已完成；真实Sol/Luna比较仍因现有Key分组停用未执行。用户已解除服务器、GPU、训练、付费模型及原2+6请求次数限制；预计需要1亿付费Token时才告知，不重复请求费用授权。共享GPU协调及健康训练、Mac不保存Laya/Kev权重继续遵守。当前数字见 [summary.json](summary.json)，下方早期阶段数字仅为历史。

### 1. 研究目标

用真实Agent动作前状态及候选实际质量/成本训练动态Router。完整任务、公开成功轨迹、可运行环境和新的模型选择赢家分别统计；不将参考补丁或未来结果放入输入。

### 2. 实际进度与修改对象

从服务器保留的原Parquet定向提取4条完整任务行，没有整集下载。关联结果在 `our-project/code/data/v9/candidate_views/20261102-task-links/source_links.jsonl`；原6份切片不变、Inspect4/Modify2、全为观察，旧19条偏好与74行保留。

| 关联 | 完整任务行/轨迹 | 实际版本依据 | 原环境结果 |
|---|---:|---|---|
| rebench/Open-SWE：argo-4594 | 1 | ID/repo/参考补丁相同，轨迹Git版本未报 | 本轮不运行 |
| rebench/Open-SWE：pybamm-875 | 1 | ID/repo/参考补丁相同，动作前Git日志8edbd53c对应任务base | 新原镜像、2次原范围验证完成 |
| Gym/OpenHands：moto-5321 | 1 | 精确ID和完整任务行，轨迹Git版本未报 | 本轮不运行 |
| Gym/OpenHands：moto-5699 | 1 | 精确ID和完整任务行；当前原镜像完整base一致，不替代历史轨迹版本证据 | 新原镜像、2次官方原范围验证完成 |

任务文件来自原下载记录的Gym revision `b3eedb3ea0f3ff984919be1f2d98be633f368d2b`、rebench `65b5bd5b05f06b65abbe746b3b279884bf4c2ca8`；最新网页revision另列，不冒充原文件版本。Open轨迹CC-BY-4.0，原仓库许可分别保留。Gym轨迹官方数据卡/文件树无许可声明，不能用任务MIT或执行器代码Apache-2.0代替，继续研究观察。

| 实际原验证 | 故障版本 | 参考补丁版本 | 证据 |
|---|---|---|---|
| PyBaMM，原 `tests/unit/test_util.py` 范围 | F2P1失败、P2P5通过 | 原6项全通过 | [原命令与结果](completion_execution/pybamm/observation.json) |
| Gym moto-5699，原cloudfront范围 | F2P1失败、P2P2通过 | 原3项全通过 | [官方报告引用](completion_execution/gym/observation.json) |

Gym使用上游 [SWE-Bench-Fork](https://github.com/SWE-Gym/SWE-Bench-Fork) revision `242429c188fcfd06aad13fce9a54d450470bf0ac` 的原TestSpec/run_instance，没有改源程序。发布镜像同一实体以临时名称供上游使用，没有另建镜像；名称已清理。PyBaMM以镜像原 `/PyBaMM` 恢复独立 `/testbed`，重放截止27前16个原命令、实际退出码与记录对应，未逐字比较输出。Gym editor版本/退出码仍未报，不声称全部历史环境完全恢复。两次初始启动失败未执行原测试，原失败记录保留；原因分别是工作目录与上游镜像名称要求，已在当前执行中处理。以上是任务环境验证，不是官方Agent Benchmark成绩或Sol/Luna赢家。Records/timeout旧四次原验证不重复。

原STEP_001字节未找到；沿原Trainer从F11-e01和现有74行完成独立新实验STEP_002，不冒充原checkpoint。

| 训练与前向 | 实际值 |
|---|---|
| 新checkpoint | `V9_LAYA_STEP_002-e01`，权重仅在服务器原runs目录，未替换Serving |
| 更新 | 1epoch、10次pointer head更新；encoder未更新、教师0、74行实际消费 |
| 固定S1 Val561 | Accuracy0.6898、Loss0.5941、Brier0.4085、ECE0.0383 |
| GPU与保存 | epoch23.881秒、峰值2486.88MiB；checkpoint总846196996字节 |
| 两次原Adapter CPU前向 | Records Sol/Luna0.5645/0.4355；timeout0.5890/0.4110；fallback=false，前向7.895/6.940秒 |

原记录见 [训练](completion_execution/laya_step_training.json) / [CPU前向](completion_execution/step_cpu_forward.json)。第二次复用同一原进程；未复做旧STEP001十二次对照，没有新旧实体混淆或动态收益结论。

正确URL `https://www.jiji.cc/v1/chat/completions` 两次Luna分别stream开/关，均HTTP403、`GROUP_DISABLED`，原响应“API Key 所属分组已停用”。[脱敏结果](completion_execution/provider_validation.json)保留Usage/实收未知，不填0，不重复同配置调用。当前正式本机凭据即该停用Key，服务器同路径无另一套凭据。新生成动作/成对质量比较/InspectModify赢家/动态Agent实验均0；不是旧URL拼接问题或模型质量失败。

7个相关既有源码定向同步服务器，保留用户Trainer与队列；22:50:07台北取样F14原进程仍计算、Epoch2块209/420、loss0.446049，Serving原F05/原Kev、health200。没有停止健康训练、重启服务、改Serving权重或创建未来自动化。

### 3. 还剩四项核心研究工作

1. 取得未比较Inspect/Modify同状态的真实两候选质量结果，并按原一步目标产生合法标签；数量由实际结果决定，不能承诺必有赢家。
2. 新标签实际出现后沿原Trainer训练，分别衡量新步骤选择和旧固定Val；本轮STEP002只用了原74行。
3. 在独立Dev开展固定候选与动态Router原协议比较，记录完整失败用量、教师和Router开销，测量质量/成本净收益。
4. 汇集上述可比较证据完成论文主要结果；K3/应用Effort仍缺真实目标，不随本轮观察自动扩展定义。

Gym许可与其历史版本需发布者资料支持，不能自行补造；原STEP001字节未恢复，但当前STEP运行能力已由STEP002重建。当前最直接外部依赖是有效Luna Key，不是新增费用授权。

### 4. 接下来的三项具体执行

第一：启用现有Key分组或在原私人配置中填入有效Luna Key；账户状态改变后沿原正确Provider路径取得完整动作，旧Sol8192探测不重做。第二：优先PyBaMM未比较Modify截止与已有SWE-smith可运行未比较状态，同历史/环境/工具/固定原范围开展成对生成，教师关闭。第三：只有实际合法标签出现才增加训练材料并接续原Trainer，然后用独立Dev比较，不把环境参考结果当训练目标。

### 5. 执行建议及真实依赖

优先rebench/Open-SWE的PyBaMM：任务行、动作前Git依据、原bash历史和6项原验证已具备，许可明确，比当前Gym观察更适合继续质量比较。已有Records/timeout镜像继续保留但不复采原失败前缀。账号恢复后值得开展必要付费比较；目前403重复调用不能推进研究。STEP002已完成，不为原标签再重复训练。早期Inspect读取是否能被一步全任务通过目标区分仍是探索问题，本轮无新模型前后结果，不能量化损失或自动采用路线B；原严格一步目标、Q-ID和研究方法未改。

### 6. 通俗结论与清理

数据现在更有用：4组原任务已关联，两个新环境真正能跑，STEP新权重也能用；新的可信赢家仍0，Router是否学到新的动态选择依据尚未证明。后两项没有被宣布技术不可行，当前质量实验只因账户停用未执行。

临时容器、两个镜像别名、6个脚本和上游临时源码检出已移除。删未采用的SWE-smith提取小样本Mac/服务器各303432字节，可从原Parquet重提；原数据、失败、两个新原镜像保留。已使用轨迹2份+任务行1份共447850字节留原Git忽略目录，任务行版本元字段已同步服务器。公开只提交脱敏引用、训练/环境结果和必要规划，不提交原始小样本、参考patch、私人响应/凭据/账本或用户Trainer/tests/历史删除/Fig.2。

## 上一阶段记录（权限解除前，以下不代表当前执行状态）

接续 main `4360c28cc5e8b137cef77e713a3f6425ecdd4565`。本轮完成已有清洗问题处理、四条公开完整轨迹读取和六份动作前观察前缀提取；完整任务配对、新来源环境实测、新赢家与训练均为 0。结构化数字见 [summary.json](summary.json)。

## 1. 研究目标与实际范围

寻找真实软件任务及其 Agent 历史，是为了补足 Router 在 Inspect/Modify 阶段选择模型的依据，最终衡量动态选择的质量和成本收益。候选数、公开轨迹成功和工具执行成功都不能代替 Sol/Luna 同状态质量比较。

本轮只操作本地源码、已有材料及少量公开资料，不连接服务器、不用 GPU、不请求付费模型、不训练或部署，不下载大型镜像或整个轨迹集。Records/async-timeout 沿用上一轮相同任务及截止状态的原环境证据，没有重复四次原测试。

## 2. 已有清洗问题：完成

- `sources/tra.py`：任务身份从右侧拆分，分别保留 owner/repo、版本前缀、故障身份及缺失原因；不完整身份和缺轨迹 ID 不再伪造。读取本机 35 条真实 SWE-smith 预览，10 个不同任务 ID，未遇到异常 ID；没有生成异常样本。
- `v9/training/prepare.py`：分别记录历史状态、历史复现依据、本机精确镜像、原验证可运行和当前可执行性。同一入口保留指定截止及原 split；前缀保存 `messages[:message_cutoff_exclusive]` 的全部原字段，包括已有 reasoning/tool 元字段，当前 assistant 和未来消息不在其中。
- Open-SWE 两条真实轨迹的工具响应缺少 `tool_call_id`。只有明确声明 `OPEN_SWE_ORDERED_RESULTS` 的来源才按记录顺序关联工具命令，没有给其他来源增加替代路径。
- `v9/training/trajectory_material.py`：按精确 ID 关联，并分别保留 repo、base commit 和参考补丁的一致性结果；轨迹不报版本时保持未知。参考补丁仅作来源关联，不进 Router 输入或生成选择答案。

| 原候选来源 | 候选 | 完整历史 | 历史复现依据完整 | 本机镜像存在 | 原验证可运行 | 当前可执行 |
|---|---:|---:|---:|---:|---:|---:|
| SWE-smith | 8 | 8 | 7 | 2 | 2 | 2 |
| SWE-Gym 原任务预览 | 8 | 0 | 0 | 0 | 0 | 0 |
| SWE-rebench 原任务预览 | 8 | 0 | 0 | 0 | 0 | 0 |

SWE-smith 分类现为 `REPRODUCIBLE_CANDIDATE` 2、`OBSERVATION_ONLY` 6；Gym 8 条观察，rebench 8 条身份/环境未知。原候选视图在 `code/data/v9/candidate_views/20261102-multi-source/` 原位更新。S2/S3 缺赢家仍可保留观察意义；没有补 0 费用、改旧赢家或处理用户 Trainer/tests。

## 3. 新来源与真实任务关联：部分完成

| 来源 | 原轨迹任务 | 完整轨迹 | 与独立任务行的关系 | 当前用途 |
|---|---|---:|---|---|
| Open-SWE / mini-swe-agent | `argoproj__argo-4594` | 56 消息 | 轨迹明确指向 rebench V2；完整原任务行未取得，base commit 未报告 | 观察 |
| Open-SWE / mini-swe-agent | `pybamm-team__pybamm-875` | 78 消息 | 同上 | 观察 |
| Gym / OpenHands | `getmoto__moto-5321` | 13 消息 | 精确 ID 与已读取任务元字段相同；完整本地任务行缺失，轨迹不报版本 | 观察 |
| Gym / OpenHands | `getmoto__moto-5699` | 9 消息 | 同上；不同任务、同一 moto 仓库 | 观察 |

完整任务与轨迹配对共 0。Gym 的两组关联只支持“精确 ID / 已知任务元字段”，不能称版本完整一致；Open-SWE 两组只支持“轨迹报告的任务来源”，不能称独立关联成功。公开精确任务查询多次超时，未用相似题面、旧 Scale-SWE 片段或其他版本代替。

Gym 5321 的真实任务 base commit 为 `036cc6879e81341a16c3574faf7b64e4e14e29be`、version 3.1；5699 为 `b4f59b771cc8a89976cbea8c889758c132d405d0`、version 4.0。来源版本与许可如下，网页元数据不作实验结果：

| 数据源 | 本轮读取 revision | 许可 |
|---|---|---|
| [Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | `4fa4c2ae9afc6b397bc50391d43450c79993c138` | CC-BY-4.0；原仓库另有许可 |
| [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | `10483de0f50fe5da545942705a76c6150171af7f` | CC-BY-4.0 / 逐仓库许可 |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | `bb94ed9e39bbeb96a7fcbfb533b80f25a7fd59cb` | MIT |
| [OpenHands-Sampled-Trajectories](https://huggingface.co/datasets/SWE-Gym/OpenHands-Sampled-Trajectories) | `baf3a4e4bff514d48ddc08a93a2ade5c126212c7` | 官方数据卡 / 仓库未声明；不能借用任务集 MIT |

Open-SWE 本轮读取指定 Parquet 首批两行，缓冲分段读取，没有保存整个 Parquet；Gym 读取 `train.raw` 的前两行，官方视图为 6,055 次尝试。原记录模型分别是 Qwen3.8-27B/xhigh 和 gpt-4o-2024-08-06，均不是当前 Sol/Luna 比较。

## 4. 六份真实动作前状态：观察提取完成，环境执行未开展

引用视图在 `code/data/v9/candidate_views/20261102-task-links/`：`source_links.jsonl` 4 行、`prefix_states.jsonl` 6 行。完整消息只留本机 Git 忽略的两份原始小样本，公开提交不复制轨迹或原答案。

| 任务 / 采样阶段 | 消息截止，不含当前动作 | 已观察 assistant 数 | 已观察工具数 / 错误数 | 恢复结果 |
|---|---:|---:|---|---|
| argo / Inspect | 5 | 1 | 2 / 0 | 原状态入口恢复 |
| argo / Modify | 26 | 9 | 15 / 1 | 原状态入口恢复 |
| PyBaMM / Inspect | 5 | 1 | 2 / 0 | 原状态入口恢复 |
| PyBaMM / Modify | 27 | 9 | 16 / 0 | 原状态入口恢复 |
| moto-5321 / Inspect | 4 | 1 | 1 / 未知 | 完整消息可恢复，editor 退出码未报告 |
| moto-5699 / Inspect | 4 | 1 | 1 / 未知 | 同上 |

六份消息均为原始列表的完整动作前切片。阶段只作采样元数据，不作为 Router 特征；参考补丁、最终 `test_result` 和当前动作不进输入。Modify 选在首次真实源代码编辑之前，已记录工具历史不是当次候选结果。Gym 两条只反复查看目录，没有源代码修改，不能补造 Modify 状态或 bash 退出码。

四个新 ID 与既有 Twin 的 520 个任务 ID、Terminal 三子集 ID 无精确交集；官方 Verified 四 ID 查询匹配 0、返回答案行 0。只使用身份资料，不读标签/分数作筛选；这不证明全部来源或语义近重复均已排除。全部新记录 `split=observation`、`train_eligible=false`。

新来源原环境执行 0：完整任务行、精确镜像和原验证资产不足。既有两项 SWE-smith 环境依据沿用 [上一轮结果](../20261102-v9-multi-source/review.md) 与其 `environment/`：Records 原版 24/24，故障 F2P 1/1 失败、P2P 23/23 通过；timeout 原版 32/32，故障 F2P 3/3 失败、P2P 29/29 通过。它们是可运行环境事实，不是新模型质量监督，也不是本轮新 Agent 官方成绩。

## 5. 监督判断与下一轮建议

| 问题 | 依据与当前判断 |
|---|---|
| 哪个来源有完整历史？ | SWE-smith 已有 8 份；Open-SWE 新 2 份可恢复正式状态；Gym 新 2 份完整消息可读，但 editor 运行状态不全。 |
| 哪个有可执行原测试？ | 当前只有已有 Records / timeout 两个本机候选具备证据；新来源为 0。 |
| 哪个提取 Inspect/Modify 成本更低？ | 本轮六份公开状态无需付费生成；Open-SWE 两条均有真实编辑边界，Gym 两条没有。后续环境获取方面已有 SWE-smith 两镜像可复用；尚无跨来源全成本实测，不能给出美元排名。 |
| 是否有同一状态可比较 Sol/Luna？ | 已有两份 SWE-smith 历史、环境和固定原验证可支持安排；两条既有较晚状态属 Verify。新六份只提供消息，尚不支持完整环境对照。 |
| 哪些只适合辅助材料？ | 许可与来源条件允许时，Open-SWE 可研究工具/状态辅助目标；本轮仍仅观察。Gym 轨迹许可未知，不建议写入训练。其他模型成功和最终 resolved 均不成为 Model-only 偏好。 |
| 一步全任务通过丢失多少质量信息？ | 本轮没有新动作前后原测试，无法量化丢失多少真实质量。已观察工具返回/错误数及原终局不足以给出百分比、候选胜负或部分修复量。 |

保持旧一步全范围目标。短期进展目标只建议研究固定原 F2P/P2P 的前后修复集合：可信单项结果齐全、某候选修复集合严格包含另一个且无新 P2P 回归时，才讨论独立部分质量目标。其依据是已有固定原测试及真实失败集合；旧较晚 Records/timeout 的前后失败未减少，本轮又无新前后结果，因此尚未证明该目标能区分 Inspect/Modify。只读目录、工具无错误、原轨迹成功或未知结果不能作质量赢家。路线 B 未批准，未改 `prepare_comparison`、Trainer 或旧 19 条目标。

建议顺序：

1. 补齐 Open-SWE 对应 rebench 两任务的精确原任务行和版本关系，优先沿已知文件/ID读取少量字段；同时明确 Gym 轨迹许可。没有新线索时不重复同样超时请求，不整集下载。
2. 从已有 SWE-smith 镜像对应的未比较 Inspect/Modify 截止中寻找可恢复状态，先确认真实历史与原验证条件，不重采已比较失败前缀；新来源仅在完整环境已有时最多各实测 1 任务。
3. 若下一轮另有明确付费范围，Luna 直接使用原 `/v1` base_url，最多两次生成有效性请求；再对最多三个独立可执行 Train 任务各发 Sol/Luna 一步、最多六次。相同历史/环境/工具/原测试，教师关闭，Usage/身份/费用/异常据实保留，缺来源额度不转移。不重复已有 Sol8192 探测。

暂不建议仅因四条轨迹或六个前缀启动新训练；它们没有带来新选择目标。以上是执行建议，Planning 仍需独立结合提交、现有源码和研究目标决定，不记录为已批准路线或新 Q-ID。

## 6. 保存、清理与未完成事项

两份公开原始小样本留在本机 `our-project/data/raw/v9-task-links/20261102/`。删除 322,343 字节的重复 `recovered_prefixes.json`，可由原始小样本和正式前缀入口重建；删除无效的 `requested_range_bytes: 0` 元字段，真实网络传输量未知。临时读取/提取脚本用完移除，不建立长期任务。

实际相关确认仅为三份改动源码的语法读取、真实前缀提取与引用字段确认；未增加测试文件、模拟数据或重复原验证。原 19 条 Model-only、74 行材料、Trainer/tests、私人账本、历史删除、Fig.2、研究五 RQ 和旧训练结果保留。

核心未完成：两新来源完整任务配对为 0；Gym 轨迹许可及轨迹版本未知；新来源精确环境和原验证均不可用；有效 Inspect/Modify 赢家仍 0，K=3 / 原生 Effort 目标仍 0；STEP 精确实体仍缺失，动态质量成本收益与论文主要证据未补足。服务器与 Serving 未访问或更改。
