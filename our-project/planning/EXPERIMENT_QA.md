# ModelRouter · E-DESIGN 实验设计问答与决策记录

> **版本 v1.4｜建立：2026-10-09｜更新：2026-10-31｜V9 五 RQ 已确定，部分执行配置待明确**
>
> **职责**：记录每项实验设计的 Q-ID、问题、选项、Planning 推荐及理由、项目负责人回答、最终决策、日期，以及对实验设计、资源/预算和论文结论的影响。研究方法总览见 [RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)，实时阶段见 [PROJECT_STATUS.md](PROJECT_STATUS.md)，交接历史见 [PLANNING_MEMORY.md](PLANNING_MEMORY.md)。
>
> **证据边界**：Planning 推荐、待回答事项、预案任务数量和费用均不代表执行已获批准或已经完成。历史数据清洗、训练和评测要求按对应日期保留；实际操作遵循当前人类明确范围。

## 0. 阶段入口与决策规则

**2026-10-31 当前决定（沿 Q-003/Q-021）**：本轮从e28872f接续，五RQ、八图十二表、三正式身份和两固定教师参考不变；不重跑fix-git/db-wal Alias题、不新建Harness、不启动训练。真实Sol Responses和项目jiji Luna Chat Completions均实调low；Flash两账户明确无型号渠道，不以27B代替。公开Dev extract-elf初始消息/工具/mini配置相等，Sol原900秒超时无Verifier，Luna reward0/CTRF1/2；保留同条件生成/执行观测，不赋失败者最优标签。真实调用、费用与COBOL混型号详见 [PROJECT_STATUS](PROJECT_STATUS.md)。

**教师决定与实证**：只摘要已观察事实，两个参考输入缩为摘录，去掉重复消息；使用Sol最低合法low、JSON Object、输出4096/context8000。保留首次约3生成与阶段/验证/重复错误触发，后续最少间隔3生成；不增加重试或第二教师。新真实step3前缀三字段成功，1462输入/1528输出含1435 reasoning、0.0189335USD；未执行新Router或工具，不计旧Trial。旧观察机会重算3/7/10而非旧3/5/6/7/8，不等于收益；新短评仍比Luna本次Episode贵约4.23倍。旧短评随信号变化清除并保留截止范围，不改变Agent行动或指定模型；新Episode教师关闭。

**AA、费用与监督决定**：新实验/视图固定v4，Sol/Luna Max共20项；low/none/托管Flash及Coding/Agentic综合指数缺测，不借用其他变体成绩。Sol正式合法档不含none，Flash支持未知；本轮只用了实调low。新382行196/186保留旧S1目标和四条旧教师，八个原未知终局不作失败；390/v1和旧13214保持、候选不算新增独立样本。当前三模型choice/Model×Effort及Train资格仍0，AA/Alias/低价失败不生成答案，Dev超时的reward未知。调用日志采用原Provider费率，旧估价/raw Usage保留，实收与未计量资源分开；RouterBench许可及近重复/S3交集未知。

**训练讨论与运行事实**：F14已按原管理范围结束，failed/NON_FINITE_LOSS、原队列PAUSED_RUN_FAILED；旧实体和异常记录保留，未启动F15。F11-e01/R11与Serving权重不变，健康对象未受影响。没有新增Train选择标签，不启动微调；后续明确真实Train同状态choice目标，旧S1候选/偏好保留，教师截止前短评与AA卡经原serializer进入输入。Laya使用原encoder/head学习率和freeze_encoder，Kev为LoRA/pointer head、head_lr=0沿用主lr。原固定Val S1四指标和真实Dev Episode判断收益，不重复旧配方，不承诺指标不退步或添加执行条件；最新事实见 [PROJECT_STATUS](PROJECT_STATUS.md)。

**10-31 fix-git 历史决定与结果**：同题两Trial及事后补充已完成，任务成功、教师失败、原费用与缺测证据保留于 [PROJECT_STATUS历史段](PROJECT_STATUS.md#2026-10-31--历史fix-git-三身份-alias-官方开发接续)，不继续复制详述，不写成独立科研两样本。

**2026-10-30 历史决定（沿 Q-003/Q-021）**：用户明确从未设置 API 总 Token 或美元预算，旧累计额度与等待费用批准的安排已撤销；测试按任务需要和服务器实际负载执行，保留资源规则、训练不中断及 Final 隔离。新单 Luna none/low 官方开发 Episode 已 reward=1.0、CTRF 2/2，通过范围仅限该次开发任务；真实 Luna 官方 Episode 费用与映射实验分开。映射实验真实请求统一走 Qwen3.8-27B，Router 选择仍记录三逻辑身份，费用按所选 `ModelSpec` 价格乘真实 input/output/cache 用量；教师按配置教师目标身份计价，实际返回身份和供应商实收另列。三原目录的 `mapped_cost_accounting` 已本地独立重算，结果和缺失 usage 对完整总额的影响见 [PROJECT_STATUS](PROJECT_STATUS.md)；旧 raw 与终局未改。原服务代码配置已部署，重启后两模型真实非回退前向通过，权重不变；Kev长前缀超时与82.28秒CPU时延保留，不改写成原60秒窗口达标。原 Provider 累计上限已移除、原 CLI 默认 cost_limit=0；部署身份、F14第420块NaN及剩余项见 [PROJECT_STATUS](PROJECT_STATUS.md) 当前入口。

**10-30 20:05历史执行记录（继续Q-021，旧额度现已取消）**：已恢复原Docker并通过官方Oracle的CTRF 2/2和reward=1；这一结果只核验环境。真实Luna单候选Episode保留9生成、18工具、3教师，Laya上游`topk(2)`错误与预算容量不足使其没有正式终局评分。原配置改为同Luna `none/low` 双动作，已用保存前缀获得真实非回退前向；没有继续收费试验，预算仅余29,697且未扩大。原失败报告审批要求已移除；该时点尚保留旧预算设置，现已取消，Final/资源规则保持。Sol/Flash研究身份、五RQ和原训练决定不变；完整Episode、独立后端、真实监督及账单仍需实际输入。详细结果见 [PROJECT_STATUS](PROJECT_STATUS.md) 当前入口。

**10-30历史接续决定（沿原Q-021，不新增Q-ID）**：该阶段附件要求合规源码/六文档同步main；已完成Laya/Kev不重训、不把内部Val或Alias计官方成绩。v2已取得LunaMax指数27.7552（AA5.0）及9项，其余精确型号缺测，旧52/38只属先前版本参考。原CLI显式 `--single-episode` 仅一task/一policy，不自动加基线；原教师6/3与5/2分别复核、费用未知。Laya当前仅关键短摘要保留，不称全部能力卡进入编码；三模型真实目标仍0，F14有效更新未知，不选其为父。Docker条件与当前状态统一见 [PROJECT_STATUS](PROJECT_STATUS.md) 首页；下方文档子任务“未改源码/只本地”仅描述历史范围。

**10-30 10:40 历史执行要求的完成范围**：原 F13 已完成，本次沿原 CLI 的 `skipped_existing` 接续 Laya `V9_LAYA_001`，两轮和固定 Val 完成，状态 `COMPLETED`；第 2 轮总体 Accuracy 49.51%，S2/S3 改善、S1 四项退步，未上线。Kev 已完训但四项退步。两者新特征均为局部训练，未形成三个新身份的选择/Effort 监督或正式任务成绩；不从本次内部指标推导唯一最佳训练配方。原训练接点只解析已有目录链接，不新增控制器或执行条件；F14 未被改变。AA Key、Docker 访问、独立模型对应和完整费用仍缺，具体指标与证据见 [PROJECT_STATUS](PROJECT_STATUS.md) 首页。下方旧待启动描述仅保留历史，不撤回当前仍有效的执行范围。

历史参数接入阶段：原 Harbor CLI 的 V9 配置和三候选已传入既有 Agent，run 保存、resume 复用；仅配置解析/实例构造通过，没有正式 Trial。恢复 Docker 或提供现有 daemon 访问后继续同一入口，不另建执行框架。

### 2026-10-29 · Q-021 后续明确决定与执行配置（不新增 Q-ID）

**研究版本**：用户在下载讨论行 25981 明确保留正式 V9 五 RQ；RQ1 Overall、RQ2 Pool、RQ3 Decomposition、RQ4 Systematic Ablation、RQ5 Workload Boundary 及 Fig.1–8/T1–T12 不变。此前三 RQ/将消融归 RQ1 的建议已被该决定替代；Q-017→Q-019→Q-021 的历史答复仍完整留存。

**三逻辑身份**：行 26344 指定 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`，行 26368 允许三 ID 统一映射已有 Qwen 联调，三身份真实 Provider 映射均已确认。映射实验真实请求统一走 `Qwen3.8-27B`，Router 和实验身份仍保存三逻辑 ID；`ALIAS_SMOKE` 不进入独立三模型质量比较。网关 `/models`/已报流式名 `Qwen3.8-27B`、实际非流返回 `self-dploy/Qwen3.8-27B` 分别保留，返回字符串只记录实际 API 身份，物理对应 UNKNOWN。映射实验费用使用所选逻辑目标身份价格，后端价格或独立真实模型缺失均不影响映射实验；实际后端请求/返回身份、供应商实收另列。用户已充分授权测试及部署，研究池可用性单独登记；审阅子 Agent 的 `gpt-6.1-sol/max` 不等于生成或教师设置。逻辑 ID、实际 Provider/API 模型、部署及价格证据分别登记。

**教师与能力输入**：首版单个顶级教师对照两条固定成功公开摘要（高效完成/失败恢复），无需在线检索；约三次生成或阶段/停滞事件触发只作 Dev 起点。核心 `progress_summary / main_blocker / next_milestone` 必须真实进入 state 和编码，离线/在线含义相同；未学习标 `FEATURE_NOT_TRAINED`，不妨碍已有接口联调，但不能声称新特征有效。教师只加工当前前缀，不选模型、不执行工具；顶级教师与联调用 Qwen 分别记录。能力卡优先原分、单位、版本及实际 Effort 证据，AA Intelligence Index 是综合指数，不能生成最优动作标签；综合低中高仅作固定参考分布的派生特征，未测档位保持 `NOT_MEASURED`。

**数据、训练和成本**：复用 V2.1/L1、原 S1/S2/S3 与固定划分，Q/S/L 各自保留；观察动作、重复终局与静态偏好不能拼成同状态全动作最优监督。每次手动执行专用刷新入口重新请求 AA，Agent 使用已保存快照；Agent 启动和 Router 每次决策不自动访问 AA，复用现有 `load_current`，正式训练/实验固定相应 `snapshot_id`，不新增 job 或自动网络行为。第二提示词 198–208、335、773 行及用户本轮澄清支持该范围，自动刷新派发已撤销。健康训练按原控制器自然完成后接续，不新建 Trainer/队列。Laya/Kev 各用同协议 Val 和独立 Dev 选可加载起点，历史缺失权重只在关键对照不可替代时考虑重训。离线教师制作费用归数据/训练，在线教师费用归完整 Episode；上下文消息与实际 KV/缓存双记。Mac 零 Laya/Kev 权重；全部执行者、教师及重试按实际 API 用量记录，不设累计 Token 或默认美元上限，Final 不作训练、选池、调参或教师输入。

**本轮范围与证据**：文档子任务只改六原文档。单题 Alias 已真实成功终局：9 次生成、13 次 Bash、7 项 unittest 通过，Laya 全程 `fallback=false`、Checkpoint `epoch_01`；本题选择仅 Sol。此前双路由选过 Luna/Flash，额外两次短 Provider 映射验证不算新 Agent 题。Teacher 从已知 2 次三字段输入传递/1 次超时后继续，发展为 3/6 成功；失败未终止任务，Qwen 联调教师不能算 Sol/顶级教师。原 SSE 失败、物理后端 UNKNOWN 及正式成绩隔离保留，详细事实只在 [PROJECT_STATUS](PROJECT_STATUS.md) 首页。

**已确认的状态语义问题与回放**：holding Tokenizer观测旧LayaState为2,762/2,827 Token、预算940，任务位置2,733/2,798，任务被裁，历史负结果保留。唯一V9 formatter和Schema薄调用的 [final编码与训练prefix分词记录](../results/iterations/20261029-v9-alias-smoke-tools/input_encoding_validation.json) 已确认任务、三教师字段、候选卡及缓存/身份关键字段进入最终编码。新顶层`recent_tool_validation`于18:44 UTC/02:44台北仅验证原step5：Laya1024/head512、状态预算940下，512字符真实工具结果仅末128字符在Token `[879,930)`为`FULL`；任务、三教师、三候选卡及缓存/当前和前次身份均`FULL`，长`history_snippet`仍裁。Kev原native编码2147 state/2224 total、不截短、候选键3个，本次未新增Kev API前向。同源一次Laya真实前向仍`epoch_01`、`fallback=false`；概率与时延见 [PROJECT_STATUS](PROJECT_STATUS.md) 的本次编码段。原`context.py`单文件已原位部署，源cached3136仅为字段保留。此前198条Train已测分词，本次未重测该批Train或Val；Laya1024保留4教师核心但完整state裁6条，8192推荐尚未启用。192条Val只核身份/数量、未测长度，不把分词或字段传递当新特征学习。Native 前缀回放已记录 Laya 选 Luna、`epoch_01`、`fallback=false`；Kev 首次 20 秒窗口超时并走模拟 fallback，一次 60 秒窗口重测约 53,516 ms 真实前向成功，选 Sol、`fallback=false`，两路均有三候选真实概率。Kev ID `1001bb4d826a52d1f399e183466143f4da7b741b` 属 Serving 导入适配器，不能称 R11 候选。回放不重跑同题、不增加正式/科学成绩，不新增第二格式实现。 同一JSON的`live_transport_validation`已保存04:20原step5旧`/v1/systemone`字符串直传8822字符、HTTP200/fallback=false/epoch_01及1024输入Token；同正文native编码支持核心字段与末128字符保留。旧进程Token IDs未直接采集、普通`/route`未验证、长history仍裁；未重跑Episode或加载新权重。

**新题失败、默认行为与宿主限制**：另一 `duration` 题迭代 `20261029-v9-kev-alias-smoke` 已回报 2 次真实生成/3 次 Bash 后第 3 次路由 60 秒超时，默认原 PolicyModel 在 fallback 后退出，`FAILED/验证1` 及日志保留；教师失败后继续的已测行为不适用于这次 Router fallback。原 Serving `2291306` 未重启/换权重，启动 `KevAdapter` 无 `device`、默认 CPU/`torch_cpu`，step0/step1 前向 18,802/38,674 ms，step2 工具 history 长度回报 3,835（单位未报）时超时。首个 Bash `find /` 上游 30 秒超时，后用 `ls/pwd` 定位，未改外部数据；Host 测试无容器隔离，不能称安全或正式基准。该失败回报时计划在原Runtime补CWD、按`router_context_chars`缩工具视图并保留task/teacher/raw mini消息；必要重跑已结束FAILED，终局见下段，成功invoice不重跑，原失败不覆盖，不新增Q-ID、Agent循环或服务。

**短视图单次验证**：原失败目录 [input_latency_validation.json](../results/iterations/20261029-v9-kev-alias-smoke/input_latency_validation.json) 已记录 step2 任务 1,019 字符保留、工具摘录 3,835→1,280 字符，任务/工具字符预算 2,300；7 条 mini 消息及教师/卡片/缓存与身份连续状态不变。原适配器 CPU 前向 37,771.85 ms、`fallback=false`，真实概率 Flash 0.7234/Sol 0.1468/Luna 0.1298，选择逻辑 Flash。该回放 `teacher_assessment=null`、卡片缺测、Token 未实测、生成请求 0，不能增加有效教师样本、能力分数或新特征学习结论。原失败不覆写，成功 invoice 不重跑。

**一次必要重跑终局已确定为失败**：`20261030-v9-kev-alias-smoke-compact` 的 [metrics.json](../results/iterations/20261030-v9-kev-alias-smoke-compact/metrics.json)/[verification.txt](../results/iterations/20261030-v9-kev-alias-smoke-compact/verification.txt) 保留 10 次生成、13 次真实 Bash、10 次 Kev 真实路由全部 `fallback=false`，CPU 前向 20,430.85–37,243.64 ms；本次不再有原 60 秒路由超时。全部逻辑 Flash/实际 Qwen、原 Serving 导入适配器。教师 5 请求/2 成功，3 失败依次 TimeoutError/JSONDecodeError/TimeoutError；成功短评在 steps3/4/5 实际送入 Router，2 次成功不能按消费步骤计成 3 次。最终代码仍有 7 个 subtest errors（7 方法、4 通过），10 步 `LimitsExceeded`、`FAILED`、`resolved=false`、验证退出 1；不能写成功 Agent或官方成绩。原测试未改、artifacts 四文件保留、临时目录已清理；完整用量/费用因失败教师缺测仍 null。

**历史停止与准备状态（旧暂停不作当前约束）**：该阶段旧预算实读 `known=575783/reserved=256135/remaining=168082`，新增 15 API 请求已计账、135 累计 calls，预留不算实际消耗；本轮不再新增生成式请求，自有 8000 隧道 `28959` 已结束。现有 [prepared/summary.json](../code/data/v9/prepared/summary.json) 写 Laya 2 Epoch、`max_len=1024/head_max_len=512`，Kev 2 Epoch、`max_state=8192`；父 R11 原 1 Epoch/384，与在线导入适配器分开。源码部署完成；现行结果见 [PROJECT_STATUS](PROJECT_STATUS.md) 的训练表，原参数/旧预算记录与前三次失败及曝光分别保留，不新增 Trainer、Q-ID 或自动 AA 请求。 原评分/留存更新已实际完成，apply=False未删权重；F14运行推进且损失持续非有限，有效优化更新/具体诱因未知，Laya自然接续仍待。

**首批部署和首次 FAILED（历史保留）**：37个源码/数据/相对链接对象、6,993,920字节，16个V9 Python模块及schemas/registry/common/390行材料已部署；Laya4处历史差异保留，common改薄别名、`common is canonical=True`、root链保留。原Python/`_material`实读198 Train/4教师/2refs及相对链接有效，GPU/Serving未重启。候选`KEV-V9-001`父R11实体、内部四指标score106.74866622586939、16原R候选完成，登记QUEUED仅历史。首次worker13266在0.145秒退出1、无GPU模型加载或训练输入消费，FAILED保留；dispatcher.py路径执行导致sys.path[0]在modelrouter/training，bare import kev误落training/kev、官方kev.train未导入。原train.log/attempt/cursor与189项测试保留，不覆盖真实失败。

**第2次真实反向OOM（历史保留）**：原wrapper两行模块入口调整已部署，窄测40通过，官方 `kev.train` 真实导入位置为 `external/kev/kev/train.py`。worker16722先RUNNING，8K输入进入真实反向计算后Torch CUDA OutOfMemory、自然退出1；进程13.54 GiB、再分配60 MiB时仅59.94 MiB空闲，日志Epoch0/Step20/100/Loss0.993。原Loader全部接纳198条记录，两轮预期396条次；失败目录只有`training_config.json`，输入曝光0是启动时统计，失败后完整输入曝光/独立覆盖UNKNOWN，不把0、接纳量或预期量作真实训练完成量。13266首次入口失败与16722第二次反向OOM均保留；两次失败未产出两轮完成权重或固定Val，UNKNOWN不由第四次真实曝光替代。

**原资源等待及三次FAILED历史、现行Kev结果**：原资源代码已按已观察占用下限加原2 GiB余量增量部署，CLI验证`WAITING_FOR_GPU`；01:43的12,668/15,973 MiB保留历史，02:11空闲12,698/需15,973 MiB为当时等待，旧384输入`required=12103`不适用于8K，不增其他限制。CLI25201曾沿原`main_loop(wait_for_resources=True, v9_only=True, ...)`保留，主Agent确认27184无worker并已结束；服务器源码`CLI_WAIT/EXIT_RESET=true`已验证，前三次FAILED分别为导入、8K反向显存不足、已有目录，原CLI25201已自然退出。2026-10-30 03:03:33原dispatcher50514/worker50518启动第四次，参数`2 Epoch/max_state=8192/full_ft=0/resume=0`，加载426个基础权重张量；03:25:31 worker50518完成2 Epoch/100steps、exit0，checkpoint实体已保存；dispatcher50514同秒自动开始原固定Val attempt1，2026-10-30 04:23:20台北完整完成、自然exit0；8436/8436记录、9330/9330问题、拒绝/裁减0、test_used=false，内部COMPLETED/EVALUATED。第四次实际使用198记录、396完整passes、拒绝/截短0，4教师完整8passes；能力卡仍缺测，三新身份监督目标仍0，新候选`FEATURE_PARTIALLY_TRAINED`。训练指标/曝光/保存及原Val日志见 [PROJECT_STATUS](PROJECT_STATUS.md) 训练表。不另建loop/Runner/定时任务。F14/ComfyUI/Serving未被干预；F14只读主证据见本节末F14段；先前Laya8.87 GiB、ComfyUI24.25 GiB占用及ComfyUI`<A6000_HOST>:8188`监听、运行队列1/pending0历史回报保留，图像任务活跃，`127.0.0.1`不通属绑定地址，未卸载/干预。原Provider/telemetry账本/logger已补`alias_mapping/query_raw`；V9 AliasProvider构造成功、账本根`<SERVER_PROJECT_ROOT>`，未发API请求/读Key、不新增client服务，Alias/账本补齐已验证且无新API，不计认证或真实生成成功。此前source部署为40个文件/链接加原Laya/Kev增量，首批37对象/6,993,920字节保留历史，后续总字节未报。Serving仍旧权重；Laya hook在盘、F14内存不读，下一自然child完两轮边界生效，不另建Trainer/队列。原评分及留存机制保持；本轮收尾仅涉及多余控制器和临时连接，04:33:44主Agent确认无当轮SSH连接残留。原`reserve_kev_attempt`将第三次输出移为同一Run的`failed_attempt_0003`并记`preserved_output_path`，其中保留原`training_config.json`；原checkpoint路径已重新创建。本次为LoRA、`resume=0`，同一原CLI/上游输出保护保留；新head/adapter/tokenizer仅在A6000、未传Mac或上线Serving，原Serving仍旧权重/`FEATURE_NOT_TRAINED`。未新增实现或测试。 固定Val8436记录/9330问题完整完成，拒绝/裁减0、`test_used=false`；相对原C03四指标均退步，内部score92.38703579133796。V9组仅1条，rank1不表示优于C03；新权重仍只在A6000、未上线Serving，正式Harbor/RQ成绩仍空白。04:32原validate_candidate时间同步与update_retention(apply=False)评分保存已完成，前三次失败时间/UNKNOWN原样。

**F14只读诊断与限制**：原`continuous_queue.log:55355/55416/55417`分别为第1块loss0.8102/step128、第62块loss0.5391/step7936、第63块loss=nan/step8064；本次175块，前62有限、后113块持续NaN。首次只定位到第63块内部记录507905–516096、计数步骤7937–8064，没有逐批log。磁盘`laya_batch_train.py:1473/1489/1495/1500/1514/1516/1529/1533`显示每块独立loss累计、soft_ce/backward及GradScaler路径；这是块级真实累计非有限，不能推断每微批异常或将无条件递增的step称有效更新数。`external/laya/laya/train.py:493/635`的有限-1e4 mask与FP16→FP32 logits路径只提供待追踪环节，未证明FP16溢出；torch `grad_scaler.py:363`可跳过非有限梯度的optimizer.step，但skip/scaler未保存。F04历史8个NaN块后仍230块有限、两轮train_loss=NaN而S1 Val0.6300/0.6141有限，不能断言F14权重失效或一定无有效更新。F14无Epoch终局/首次异常batch的logits、target、gradient、scaler记录，具体诱因与有效更新未知；源码是磁盘版本、未读PID内存，作业未停/重启/改动。主证据集中 [PROJECT_STATUS](PROJECT_STATUS.md) 的F14段，原调用链/历史保留。

**材料与监督缺口**：唯一实体 390 行，Train 198/Val 192；S1/S3 各 Train/Val 64，S2 Train 70（原 64+6 真实前缀）/Val 64，`trajectory_prefixes/train.jsonl` 仅为相对符号链接，不重复计数。六前缀来自 `gruebel_pycep_pr109`、`fonttools_fonttools_pr2313`，每题截止 0/3/7，与固定公开 Train 成功参考 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024` 不重合，原 Train 资格保留。旧 S1 未对齐 V9 三身份，choice 目标仍 0。离线初始 0 的记录保留；原 Assessor 新回报为 2 请求/2 成功、4 条可用三字段（2 新、2 复用）、2 条未触发，`summary.teacher_data_status=PARTIAL`、`GENERATED=4 / NOT_GENERATED=386`，实际教师 `self-dploy/Qwen3.8-27B`。AA 实际来源为 Sol 404、Luna 200 但解析失败、Flash 404，Key 缺失，实测能力记录仍 0、current 保留缺测快照；不能把 HTTP 200、数据可加载或三字段输入传递当有效能力分数/最优动作监督。

**费用的已知子集与缺口**：离线两请求 prompt 13,766+completion 949=14,715 Token，reasoning 678 已包含于 completion，cached 0 已报告、USD null；2 条结果复用与 Provider 物理缓存分开。hcnsec `cost` 无 currency，新请求只保留 `raw_reported_cost`、`reported_cost_unit=NOT_REPORTED`；响应明确 USD 才赋 `actual_billed_cost_usd`。旧事件保留版本，含超时的完整费用为 `None`；未知单位金额不计美元，失败预留 Token 不计实际消耗。14,715 仅是离线两请求的已知用量，所有请求完整 prompt/completion/cache/USD 仍 null，不推算新预算余额。

**仍待明确或补证**：Laya长history及6条完整state裁减的后续处理（8192推荐未启用）、192条Val长度、Laya自然接续、F14具体诱因及有效优化更新、前三次失败后的未知曝光、Laya下一自然child边界和新特征学习，以及正式生成/顶级教师配置、AA分数与完整用量/有单位费用。final/训练prefix分词范围、CLI等待及服务器旧exit处理已确认，不再列作未实施；step5近期工具真实末128字符及一次Laya前向已验证，长history仍裁；三次训练失败和duration失败均保留，第四次两轮/固定Val/内部评分已完成，不新增同题生成。189/40历史测试、配置或接口通过不替代真实训练；第四次的198实际记录/396完整passes与4教师8passes已确认，新候选为`FEATURE_PARTIALLY_TRAINED`（稀疏教师、三新身份目标0），现行结果见 [PROJECT_STATUS](PROJECT_STATUS.md) 的训练表；正式Harbor/RQ仍待。原Serving仍旧权重/`FEATURE_NOT_TRAINED`，未上线新模型；前三次FAILED及UNKNOWN不覆盖。原预算575783/256135/168082、135calls未变，不把预留或缺测总值作实际用量/零美元；主Agent本次Router1/生成0；本轮文档子任务未运行测试或发请求。

> 以下为 2026-10-28/29 的远端规划记录，不是 10-30 新实测。初始模型身份仍为 Sol、Luna、托管 `qwen3.8-flash`，不得替换为 27B 或 Flash-Next；其中 AA 52/38（v4.3.2）和 Qwen USD 价仅保留当时的来源陈述，未由本地证据复核，不用于当前能力快照、训练输入或实际账单。当前证据以本文最新记录及 `PROJECT_STATUS.md` 为准，早期权限描述不撤销后来的人类授权。

### 2026-10-29 · 负责人最新决定：固定初始 K=3、能力数据可刷新、现有训练后继续微调、六文档保守去重

负责人最新明确选择：正式 **V9 五个 RQ** 不变；首批池身份为 `gpt-6.1-sol`（高档研究角色）、`gpt-6-luna`（中档）、`qwen3.8-flash`（第三档托管 Qwen3.8-Flash），映射实验真实请求统一走 `Qwen3.8-27B`。实验费用按所选逻辑目标身份的 `ModelSpec` 价格乘真实 input/output/cache 用量；Sol 采用 v2 已保存官方 `2/10/0.1/2.5`，Flash 当前参考 `0.15/0.47/0.016` 来自 OpenRouter，阿里官方v2仅确认CNY，当前USD实验价格来源为OpenRouter。教师按配置教师目标身份计价，`returned_model_id` 保留真实后端身份。后端价格或独立真实模型缺失不影响映射实验继续；映射结果不能写成独立物理模型质量对照。三原目录的 `mapped_cost_accounting` 已独立重算，完整总额仅在所需 usage 齐备时给数；详见 [PROJECT_STATUS](PROJECT_STATUS.md)。AA 参考 Sol Max 52、Luna Max 38（v4.3.2 口径）；`Qwen3.8-Flash-Next` 的历史 40 分不能作为生产托管 `qwen3.8-flash` 的独立实测，托管分数暂标 `NOT_MEASURED`。软件工程、工具等逐 Benchmark/逐 Effort 数据继续附原始证据；RQ2 仍研究其他 K/组合。

**模型能力源同步决定**：由本地 Execution Agent 先查已有数据/Registry/脚本，复用原入口取得 AA 官方 Data API 和公开 Benchmark 可合法获取的真实指标，保存**首版带日期的本地数据快照**及来源/指标单位/评测版本/每 Effort 缺失标记，并将能力卡编码接入**原有代码路径**而非新建平行服务。后续该既有数据刷新脚本每次被明确执行时尝试重新抓取更新；不代表 Router 每个 inference 请求都联网。抓取失败沿用明确标识为上次成功版本的快照，不谎报实时数值；遵守授权、速率限制、API 套餐数据字段与再分发条款，不把密钥写进仓库。此决定**不授权**本轮 Planning 自动访问本地私有配置、下载受限数据或调用新的付费 API。

**2026-10-29 历史训练时序**：当前已授权 Laya/Kev 训练继续，不更改健康队列或抢占 GPU；先把实际能力数据、可合法的参考轨迹和训练输入格式整理在本地原项目代码/数据路径，**待现有代表候选按同协议 Val 与独立 Dev 选定后**，基于已存在可加载权重继续微调，不直接从零重训，也不把 JSON 字段加入等同于旧权重已学会；当时新训练要求真实监督和单独执行授权；当前测试/部署范围按第 0 节最新决定处理。首次最小 Agent 试测和正式 Terminal-Bench 结果严格分开。

**六文档维护选择**：保留六份及现有职责，仅做**保守去重**，避免按字符数目标大规模裁剪；可删除重复历史执行段和被新正式方案取代的重复要求，但保留 Q/D-ID、训练负结果、协议、数据政策、Checkpoint 配方与可追溯事实。新的统一 Planning Agent 负责提议/核对去重范围，未得到进一步明确请求前不大范围删文。

**备注**：用户已明确选择三款研究候选的型号；**尚未核实可调用性/套餐/真价及具体 Provider ID**，不能把已选择型号写成已验证上线或已经部署。六份文档的真实大幅精简和新训练执行仍未发生。

### 2026-10-28 · Q-021 后续讨论：精简轨迹教师、能力卡与试测准备（设计建议，未新增 Q-ID）

**研究版本纪律**：本轮讨论支持以 V9 原五 RQ 为暂时权威；2026-10-26 聊天中出现“把论文改为三个核心 RQ、消融归 RQ1”的**建议**，尚未获得新的正式 RQ 决定，因此保留 Q-019 的独立 RQ4 系统消融、RQ5 工作负载边界及 Fig.1–8/T1–T12。若负责人未来明确批准重排，另记决策、日期和对应图表改动，不以聊天建议直接覆盖。

**近期倾向性设计，均非已部署**：A. Agent 外部用一个真实顶级推理模型对照当前已发生轨迹与两条固定的成功公开参考摘要（高效路径/失败恢复），不建在线检索数据库；约第 3 次模型生成之后或关键阶段变化/明显停滞时按需更新，数值阈值在 Dev 校准。B. 教师输出简短 `progress_summary / main_blocker / next_milestone`，另有截止 step、参考来源、教师版本、真实 token/费用/延迟的可审计元数据；不是第二个选路 Router。C. 模型卡以 SWE 软件工程、代码、工具 Benchmark 原始分/真实量纲及 AA Intelligence Index 为主，后者不叫百分比；综合低中高只作固定参考分布上的派生标签，专业能力暂不独立三级分档；未测 native_effort 保持 `NOT_MEASURED`。D. 模型发布、版本/价格/可用 Effort 变化时更新；模型池先尝试三款经济定位不同的**已验证可调用**模型，最终组合由 RQ2 Dev 研究后固定。E. 健康训练继续；Laya/Kev 各自同协议 Val 选可加载候选，独立 Dev Agent Episode 选后续微调起点；不以不同架构 Loss 硬比较、不用 Sealed Final 选模，历史缺失权重只为不可替代的关键对照考虑重训。

**本轮请求与授权范围**：负责人明确要求先更新六文档，随后交给本地 Agent **只读核对源码和最小真实测试准备度**，并回报证据；不要现在执行 Codex 修改、GPU/付费调用、Benchmark 试跑、数据集下载、服务重启或封存 Test。需要分别核验现有 Terminal-Bench 2.1/Harbor/mini-swe-agent 接口和可能新增的 SWE-bench Lite/Verified + mini-SWE-agent 路线；二者评测任务集、结果、Evaluator 和泄漏边界独立。

**2026-10-28 历史待定项（旧费用上限与批准等待已取代）**：确切教师型号/调用频率、两个参考轨迹的授权和身份、AA 分档边界及 Effort 缺失来源、实际模型池 K 和型号、真实试测费用上限、最小 Dev 任务选择与谁批准执行。以上不得记为已授权、已测成功或已写入训练。

### 2026-10-24 · 双模型阶段性完训与固定验证闭环（Q-012 留存与固定验证执行）

服务器双模型训练系统在无人值守下持续推进：
1. **Laya-421M**：F07、F08、F09 连续自然完训并通过固定验证；20:50 的 F10 首 Epoch 状态属于历史观测，23:38 已进入第二 Epoch。原始记录中 `F06-e02` 的 S1 Accuracy/Loss/Brier 为 0.6863/0.6017/0.4150，实体在盘；0.6809/0.5936/0.4079 属于无实体的 `F06_S1-e02`。F07 的 S1 最佳 Epoch 是 e01。F07–F09 无实体且记录未保存，不能据此声称保存后移除或认定新的保留比例；Q-012 原决定不变。
2. **Kev-4B**：C04（`KEV-V8-HOMO-e02`）以退出码 0 完成 16,857 步训练并成功执行项目固定验证集（`val.jsonl`，8,436 记录、9,330 问题），耗时 2,982.7 秒，Clean Acc 57.12%，NLL 1.0873，Brier 0.5403，ECE 0.0599，AURC 0.2562。与 C03（Acc 57.16%，NLL 1.0796）表现高度一致。
3. **后续候选状态**：23:37:56 原 dispatcher 在自然退出后接续一次，C05 缺状态分离材料、C07 Rank16 初始化不适用 Rank8 请求、C09 缺完整新增 typed 目标，三项均实际写为 PENDING；exit 1 保留待决状态，C03/C04 的训练成功与固定 Val 成功不变。没有新研究决定或 Q-ID。

### 2026-10-22 · Q-021：以 V9 为准，外置轨迹评审摘要 + Model×Effort 能力证据（新明确方向；字段细则待试验）

**负责人最新指令**：以 V9 为准并同步六份文档；既有完整结构图中的轨迹总结/判断环节放在 Agent 外部。建议单独调用一次大模型，让它参考顶级模型的成功轨迹与当前 Agent 截至决策前的历史轨迹，生成简短的当前轨迹评估与下一步规划，作为 Router 输入。对新加入的模型，提供若干独立 Benchmark 能力分数，并尽可能细化到每个真实支持的 native reasoning effort。

**现行 RQ 编号恢复并保持 V9**：RQ1=Overall；RQ2=Pool；RQ3=Decomposition；**RQ4=Systematic Ablation**（动作/信息组/数据监督/外部轨迹摘要等机制）；**RQ5=Workload Boundary**。2026-10-22 前一条“将系统消融并入 RQ1”的意见是被本次 V9 指令覆盖的讨论快照，非现行 RQ。不要新造 RQ6；八张图、十二张结果表沿 V9。

**已明确的输入设计方向**：

- `task_state`：决策前任务目标/子任务、Agent 角色和阶段、步数、上下文、预算与剩余时间；保留当前可观测真实值与缺失。`tool_trace`：已执行工具名称/使用意图/返回/测试验证/重复工作/已证实里程碑，**不能只凭退出码判合理性**。
- `external_trajectory_assessment`：2026-10-22 初稿的工具意图/进展对齐、重复、验证缺口、风险和置信度细项留作历史设计；首版已简化为 `progress_summary`、`main_blocker`、`next_milestone`。现行仅用两条许可适用、成功证据明确、与 Final 隔离的固定公开参考摘要；记录触发原因、截止 `decision_id`、实际教师/参考身份、token/USD/时延和缺失状态。短评必须真正进入模型编码；教师只加工状态，现有 Agent 继续执行。约三次生成/阶段/停滞触发尚待 Dev 实测。
- `candidate_actions`：对每个真实合法 `(provider,model_id,revision,actual_endpoint,native_effort)` 保留型号身份、版本化能力卡；每个 Benchmark 附 `benchmark_id/version, protocol/harness, split, timestamp, effort, raw_score, normalized_score, sample_count, source, status`。维度建议软件工程修复、代码推理、工具调用及可选综合能力，但**具体来源及指标仍待最终确定**。同模型不同档位不能直接复制分数；未知为 `NOT_MEASURED`，不人为假造高/中/低的质量标签。
- 候选经济与硬约束：真实输入/输出/缓存读写价格快照、上下文/工具/地区/速率/可用性，前缀复用估计与 Provider 回报的 cached tokens 分开；先确定性过滤非法动作再打分。

**2026-10-22 历史实验与实施边界**：外置分析模型应对照 `无分析器/确定性工具摘要/外置 teacher 摘要`，记录端到端任务成功率、完整 Episode USD（包括 teacher 自身费用）和延迟；新模型输入对照 `名称+effort` 与 `名称+effort+能力证据`，未见模型泛化属于 RQ2 研究/扩展；动作、状态、训练监督分别在 RQ4 独立受控消融。新增字段尚未实现、未进入 Laya/Kev 训练，不得把文档当代码部署证明；现有 Terminal-Bench 2.1 正式官方 Trial 仍未验证。此决定不批准修改运行中 GPU 任务、花费新外部 API、解封 Test 或绕过 Harbor 沙箱。 当前测试及部署授权见第 0 节；旧范围不撤销后续明确授权。


### 2026-10-22 · Router 输入与 RQ 归属修订讨论（历史快照，已由 Q-021 的 V9 指令覆盖）

**记录性质**：负责人在 2026-10-21～22 的后续研究讨论；不是新的训练/付费评测授权，不声称新字段已实现或已经得到真实 Benchmark 结果。保留 Q-017/Q-019 历史原文与日期，新的明确决定在后续同步时覆盖旧方案，而不删除历史。

1. **RQ4 归属纠偏**：负责人明确表示独立“变量/系统消融 RQ4”没有必要，希望把 T/M/H 单组、双组、三组及关键字段的消融纳入 **RQ1**。Model-only/Effort-only/Joint 动作、S1/S2/S3 训练监督配比以及 KV/Trace 等应分开设计控制实验。V9 的独立 RQ4 不再代表最新讨论意见。最终 RQ 数量/编号与 Fig.7、T4/T5/T8/T11 归属仍需统一，已测负结果须如实保留。
2. **RQ5 不得误改**：现有 Q-019/V9 RQ5 研究“动态路由在哪些事前定义的工作负载条件下有/无净收益”；替换为“新模型/新任务零样本泛化”尚未获批准。未见模型池的泛化可在 RQ2 或扩展实验中讨论，是否独立成 RQ 待定。
3. **工具轨迹评价方向**：只看工具退出码或失败不足以评价工具使用合理性。拟利用**顶级模型的多条已验证成功参考任务轨迹**进行离线辅助监督，考察工具意图、阶段/顺序、重复劳动、有效进展、验证与恢复行为，不把某条参考命令顺序当唯一正确解。这个参考监督方案尚未完成数据可用性审计、标签定义或训练。在线只能使用当前决策前已有的轨迹；不得读取测试任务未来步骤、封存答案或验证结局。如在线另请教师模型，费用必须算入完整 Episode。
4. **新模型候选能力卡（拟议，具体字段待确认）**：仍以真实 provider/model_id/revision/native_effort 为候选身份，补充有来源的多项 Benchmark 能力分数、具体原生 Effort 的同协议分数、输入输出/缓存价格、上下文与工具能力、可用性。Benchmark 选型未确定；应保存每项分数的原始值、可比标准化值、评测版本/日期/Harness/样本量/来源/对应 Effort 和缺失/可信度。不以人为低中高等级替代实测分数；未测档位维持 UNKNOWN，不按名称猜分数；硬合法动作过滤与学习型打分分离。更改输入字段需验证实际训练覆盖及线上推理编码一致性，不能只修改推理 JSON。
5. **证据与同步原则**：既有代码确有部分 AgentState、名称+Effort 候选和 Registry，但不代表参考轨迹合理性监督、每档 Benchmark 分数和真实缓存价格已进入训练/线上评分。六份核心文档按“已确认方向、待定字段、已实现代码、真实评测”四种状态同步；当前健康队列、原始数据与封存 Test 不因本讨论改变。

### 2026-10-20 · 本轮执行范围与 Q-012 延续

负责人要求沿既有实现更新训练历史、Checkpoint 双池与原 8765 页面，不重训、不新增 GPU 工作、不付费、不删除实体或中断健康训练。代码级留存更新可进行；服务器实际淘汰策略变动须单独获得对应授权并在安全 Run 边界执行。

Q-012 的旧五份独立保护与新合格独立 Run 最佳 Epoch 约 15% 原则保持。组间名额按候选组规模用最大余数法分配，同余数按稳定组 ID；各组仅使用同协议有效指标比较。Q-016 的 S1 最佳定义继续为完整历史最小验证 Loss，不因留存状态或缺失其他指标改写最佳 Epoch。

历史训练指标、实际文件、曾保存与移除记录分别报告；导入 Kev 资产、CPU Pointer Head Pilot、短跑与正式 C 系列分开。现有目录和日志未能证明的指标显示 N/A。固定 Val 被连续用于选模，当前成绩仅提供同验证集描述比较；最终独立测试的实际使用状态尚待现场证据。五个 RQ 与研究方法未变。

直连恢复后已读到 Laya 实际执行 101、结束 100、F07 在训；212 条版本记录与 7 份实体分开显示。Kev C03 完整训练结束，验证的数据获取失败；旧 dispatcher 调用上游公开 test，缺项目固定 Val 参数。沿现有 labelled-JSONL Benchmark 入口更新本机验证调用，不启动 GPU 验证、不部署或重载训练队列。C03 当前仍无正式验证成绩。

旧五实体 2/5、新池 F05-e01 一份、F06-e02单独历史保留；缺失实体未恢复。原页面已部署真实历史，但原唯一采集进程仍覆盖旧轻状态，需负责人答复仅重载该采集进程的请求。留存算法部署与任何实体淘汰仍未执行。

> **协作汇报偏好（2026-10-10 用户已确认）**：每次收到执行结果，Planning 必须先给「整体进度」，再展开「当前阶段的小步骤」，接着给「下一步计划」「直接可复制的执行提示词」及「简短通俗说明」。完整规则在 [PLANNING_MEMORY.md 第 10 节](PLANNING_MEMORY.md#10-新会话恢复协议长期生效)。这是**回复形式的约定**，不构成任何研究 Q-ID、GPU 训练或付费 API 新授权。

- **E0.5 历史原则（2026-10-09）**：负责人确认未来在授权服务器使用独立 ModelRouter 工作目录与独立 Python 环境，现有共享资源只读；当时仅确认原则，尚未部署。2026-10-10 已核实现有项目环境，具体区别见 Q-010。
- **E-DESIGN 历史进度（2026-10-09）**：Q-001=A、Q-002=B、Q-003=B 预算原则、Q-004=B、Q-005=B、Q-006=A 已确认。Q-007 公开数据优先路线现已委派服务器清洗；本机 Codex 被要求同步 GitHub 五核心文档及构建 Obsidian 论文笔记。Q-010/Q-011 微调细节仍待研究；文献整理和数据 CPU 清洗无需重新请示。
- **2026-10-10 P1/P3 当前范围**：本轮用户已授权定向核验、现有清洗入口模块化及相关文档更新。环境、模型文件、官方源码与历史 GPU 汇总的只读核验已完成。用户随后明确要求整理、提交并推送相关改动；不启动训练、付费 API 或任务评测，不安装或下载，不改服务器服务，不操作 CI/PR。Q-010 已有硬件短训练汇总可复用；Q-011 的监督目标与训练顺序仍未决。旧授权记录按各自日期理解。
- **2026-10-11 最新授权（优先于历史快照）**：数据清洗及 `MR-STAGE1-FAST-FIX` 完成；当前仅批准 `MR-STAGE1-INPUT-FIX` 的必要 CPU 源码最小修复和训练参数核对；A+B+C 保留、GPU 正式训练未授权。详见下方 Q-011 与当前 Status 首页。
- **研究问题**：长程单/多 Agent 执行中，依据决策前可观测状态，在动态合法候选池中选择 `(model, reasoning_effort)`，能否在成功率约束下降低整任务成本。
- **E-DESIGN 记录项**：记录任务/划分与终局 evaluator、候选池与 effort 支持、预算范围、主次指标、基线公平性、成对实验可恢复性、数据训练/验证/测试隔离、统计协议和停止条件。
- **纪律**：任务成功 ≠ API 成功；实际缓存读取 ≠ 可迁移 KV；调用聚合数据 ≠ 任务级标签；CCH USD ≠ Blog GPT quotaUnits；已观察的行为轨迹 ≠ 未执行动作的反事实结果。决策时刻不得使用未来信息。
- **维护**：每次用户答复后补齐原话或忠实摘要、最终决策、日期和影响；改变旧决策时保留原记录并注明替代关系。公开内容先脱敏；提交、推送、PR、CI 只在当前任务明确要求时执行。

### 0.1 问答状态机与跨对话恢复

- `待提问`：尚未提出；`已提出待答`：Planning 推荐但用户未批准；`已确认`：用户明确确认并记录日期与影响；`暂缓/待证据`：保留阻塞；`已取代/撤销`：保留历史并说明新决策来源。
- 在新会话先读 [PROJECT_STATUS.md](PROJECT_STATUS.md) 当前任务，再核对本文件对应 Q-ID 的「用户回答/最终决策/日期」，只继续未关闭的问题。用户要求审查报告、比较方案或延续研究不自动构成对推荐的批准。
- 以后提出 Q-011 等新问题，继续维护这一个问答文档；明确决定后记录原答复、批准日期、最终状态、实验影响、预算与权限边界、下一依赖，并同步最新 Status/Memory。回答实验问题不等于自动批准模型下载、服务器操作、GPU、训练或付费 API。
- 必须区分真实任务 benchmark（如 SWE-bench 系列）、Agent 训练环境/公开轨迹（SWE-Gym、Open-SWE-Traces）、路由评测框架（TwinRouterBench）和本项目新采集的受控分支轨迹；已有轨迹不自动具备未选动作的反事实结果，许可与 evaluator 等尚需核验。

## 1. 决策队列（未回答的问题不视为批准）

| Q-ID | 主题 | 状态 | 对应关键假设 |
|---|---|---|---|
| Q-001 | 评测任务集、任务类型与 pilot 组成 | **已确认 A，2026-10-09** | H1/H3/H6 |
| Q-002 | 真实可用的 Model × Effort 候选动作与 provider 能力 | **V9 三逻辑 ID 已定；测试/部署已充分授权；Provider 实际 3 项中研究池仅 Luna，Sol/托管Flash未列出** | H2/H5 |
| Q-003 | API 用量、费用记录与服务器资源 | **2026-10-30 已明确：从未设置 API 总 Token 或美元预算；按任务需要测试，保留服务器资源规则、训练不中断及 Final 隔离** | H3/H7 |
| Q-004 | 主要 estimand：成功率约束、总 USD、每成功任务成本与延迟 | **已确认 B，2026-10-09；成功率阈值待定** | H1/H3/H7 |
| Q-005 | 固定、task-only、规则/sticky、MLP/GBDT、admission-only 基线 | **已确认 B，2026-10-09；实现细节暂缓** | H1/H2/H4 |
| Q-006 | 相同决策状态的受控分支、后续 continuation policy 与复现边界 | **已确认 A，2026-10-09；“rq 3 需要 ab 同选”指代待澄清** | H3/H4 |
| Q-007 | 数据采集、训练/验证/测试隔离、任务泄漏与隐私 | **第一学习阶段 A 方向明确；全阶段数据路线待确认** | H1/H5 |
| Q-008 | Pilot/正式规模、seed、任务层配对统计与停止准则 | **暂缓，负责人要求先讨论模型训练** | H1–H7 |
| Q-009 | 多 Agent、失败恢复、缓存与动态 provider 场景的分层 | **暂缓实验分层细节** | H4/H5/H6 |
| Q-010 | Kev-4B 训练起点与 A6000 可行性 | **已有环境与历史短训练汇总；训练起点仍待答，本轮无需重复安装或测试** | H5/H7 |
| Q-011 | 路由器监督目标与分阶段训练顺序 | **2026-10-10 仍未决；官方能力核验不代替负责人选择** | H3/H5 |

## 2. Q-001｜首批评测任务集与 pilot 构成

**提出日期**：2026-10-09  
**状态**：负责人 2026-10-09 已确认 A；具体 benchmark/evaluator/split 未确定\
**核心问题**：首轮是否优先使用可复现、自动验证终局的真实 Agent 任务，如何平衡 Harness 可靠性、外部有效性与可控实验成本？

### 选项

- **A｜直接使用公开真实 coding benchmark**：例如经许可证/环境核对后选取可复现的真实仓库修复任务；优势是外部有效性较强；风险是环境恢复、依赖、测试和模型费用高，初期很难把 Harness 故障与路由效应分离。
- **B｜只用小型自建可验证 Agent 任务**：本地沙箱中的 coding、工具调用、失败恢复任务；优势是可控、可重复、低成本；风险是任务分布狭窄，容易高估方法效果，单独用于论文主结论不足。
- **C｜分阶段混合（原 Planning 推荐，现已由负责人批准的 A 取代）**：先用约 **5 个**低成本、终局可自动判定的沙箱 coding/tool-use Agent 任务验证 Harness、ledger、恢复与状态快照；通过 pilot 门槛后，再引入经过复现性与许可核对的**公开真实 coding Agent 任务**作为正式主评测，并预留少量多 Agent/失败恢复分层任务。扩展到约 30 个任务 × 2 个动作 × 2 seeds 只是初始预算估算锚点，**不代表批准规模**。

### Planning 推荐及理由

**原 Planning 推荐 C（历史提案，现已由负责人批准的 A 取代）**。它把工程可靠性 pilot 与论文效度分开：先验证任务级成功判定、全链路 USD、相同状态恢复和失败记录；随后用真实任务验证是否能泛化，避免只在合成任务上得出过强结论。首轮不强制上复杂多 Agent 框架，但正式评测必须覆盖可观察的工具、验证、恢复状态；多 Agent 扩展须保证权限和可重放性。

**拟议准入条件（尚未批准）**：任务有可记录的起始快照、明确成功/失败/超时判据、隔离工具权限、可重跑的环境/依赖版本、完整任务级费用账本；同任务多策略使用一致的 evaluator、预算、候选池和工具条件。不能从旧 CCH/Blog GPT 调用日志伪造这些任务标签。

### 用户回答

**2026-10-09 负责人明确答复：Q-001=A。** 直接使用公开真实 Coding Benchmark，不采用独立自建小任务集先行的 C 路线。

### 最终决策与日期

**2026-10-09 历史决定：已确认 A。** 首轮以经过许可证、版本、自动终局 evaluator 和环境可复现性核验的真实公开 Coding Benchmark 为主。可以先对真实 Benchmark 的少量任务进行 Harness smoke/pilot，但不强制先开发独立的合成任务集；具体 benchmark、规模、分割、evaluator 和执行费用尚待确认。本选择不批准安装/下载/API/GPU/服务器操作。

### 对实验设计、预算和论文的影响

- **实验设计**：A 更重真实仓库复现；B 更重 Harness 内部有效性；C 先小 pilot，再真实 benchmark 与复杂场景分层。
- **资源与费用**：本问只决定任务类型与分阶段原则；当前测试按任务需要安排，资源规则继续适用，Q-003 不再要求补充 API 总额度或费用批准。
- **论文**：若只选 B，必须限制外部有效性主张；若选 A/C，需公开任务筛选、失败/排除和污染核对规则。
- **后续依赖**：Q-002 动作池必须与选定任务的工具、上下文和 provider 能力兼容。

## 3. Q-002｜真实 Model × Effort 候选池

**负责人答复与日期**：2026-10-09，**Q-002=B**。  
**原选项**：A 仅商业 API；B 商业 API + 本地开源模型（已选）；C 仅本地开源模型。

**2026-10-09 历史决定及影响**：混合候选池，按 provider/model/version 的实际工具、上下文、effort 和可用性建立 registry；不支持 effort 的本地模型不能虚构档位。需区分 API 费用与本地计算资源消耗；保持任务、权限和评价器一致。**具体模型清单、effort 支持、版本、候选数量和价格均待核验。** 不授权付费 API、下载或 GPU。

## 4. Q-003｜API 用量、费用记录与服务器资源

**2026-10-09 旧文档记载（保留历史原文）**：**“Q-003=B；初步预算：本地模型的预算不限制，API 额度根据模型进行限制。”**
**历史选项**：A 零付费 API；B 分阶段硬预算管理（旧文档所记安排，现行已取代）；C 等待价格证据。

**2026-10-09 历史决定及影响**：**已确认 B 预算管理原则；2026-10-09，具体金额及资源权限仍未确认。**
- **历史本地模型安排**：模型推理费用不设预先固定的预算上限，但仍需记录 GPU 时长、显存、延迟及合理的计算资源成本；不等于 GPU、显存、服务并发无限可用或已获使用许可，也不能把本地资源成本简单记作零。
- **API 旧安排（历史，已撤销）**：当时拟按具体模型设置硬上限并在到达限额时停止；**逐模型金额、单任务上限、总体费用边界、价格版本均未明确**，只保留当时待定记录，不作为当前执行条件，不补造预算。
- **当时权限（2026-10-09 历史记录）**：未授权实际服务器访问/写入、安装依赖、下载权重、GPU、训练、付费 API 或工程启动。批准预算原则不等于批准具体执行。待具体模型名单与 Q-004 指标确定后再细化额度和停止条件。当前范围见第 0 节。

**当前决定（2026-10-30）**：用户明确从未设置 API 总 Token 或美元预算；旧文档的 100 万、1000 万及待额度许可安排均不适用。测试数量按任务需要安排，服务器负载够即可继续；资源规则、健康训练不中断和 Final 隔离仍适用。主 Agent 的充分测试/部署授权与 Provider 实际可用模型分开记录，Sol/托管Flash未列出不转写为待用户批准。原 Provider 已移除累计上限，max/remaining 为 null、用量保留；原 CLI 默认 cost_limit=0。

**费用与托管身份**：27B 为真实执行的托管 API；先前返回的 self-dploy 字符串记录实际 API 身份。映射实验费用按真实 input/output/cache 用量乘所选逻辑目标身份价格；Luna 输出含 reasoning，不重复相加，教师使用配置教师目标身份价格。Sol 采用 v2 已保存官方 `2/10/0.1/2.5`，Flash 当前参考 `0.15/0.47/0.016` 来自 OpenRouter，阿里官方v2仅确认CNY，当前USD实验价格来源为OpenRouter。实际请求/返回身份、后端价格和供应商 bill 另列，缺失不影响映射实验；真实 Luna 官方 Episode 单独记录。

## 5. Q-004｜评价主目标（第二批，已提出待答）

**选项**：
- **A**：成功率与任务费用并列主指标，不预设成功率约束；容易展示，可能出现取舍和排序歧义。
- **B（Planning 推荐）**：先设成功率下限或相对强基线的非劣容忍度，再优化**整任务成本**；同时报告 success rate、总费用、cost/resolved、延迟、Pareto 与任务级置信区间。
- **C**：以质量–费用–延迟 Pareto 曲线为唯一主结果，不设单一优先目标；范围完整但论文主命题较分散。

**2026-10-09 历史回答：`Q-004=B`。最终确认**在成功率约束下优化整任务成本**；具体成功率下限/非劣容忍度、API 与本地资源费用可比口径尚待证据和后续批准。API USD 与本地 GPU 使用仍分开记账。此为目标原则的确认，不授权实验。**具体阈值暂缓。**

## 6. Q-005｜需要哪些公平基线（第二批，已提出待答）

**选项**：
- **A**：固定低成本、固定强模型、随机合法动作；低工程成本但贡献归因不足。
- **B（Planning 推荐）**：固定低成本/强模型 + task-only + rule/sticky/cache-aware + admission-only + 轻量 MLP/GBDT；另外做 Model-only、移除 state/cache 等消融，并按可复现性选少数直接相关工作对照。
- **C**：优先复现全部最近邻方法；覆盖多但工程开销与环境一致性风险高。

**负责人回答（2026-10-09）：`Q-005=B`。最终确认分层基线及消融范围：固定模型、task-only、rule/sticky/cache-aware、admission-only、MLP/GBDT 和必要的少数最近邻方法；具体复现与实验实施步骤依负责人新指示**暂缓讨论**。不得将历史 admission-only 恢复为主方法。

## 7. Q-006｜同状态分支与轨迹可恢复性（第二批，已提出待答）

**选项**：
- **A（Planning 推荐）**：从相同可恢复决策前状态快照出发，对两个真实合法动作分别 rollout，并固定后续 continuation policy、工具权限、预算、环境版本与 evaluator。
- **B**：只做历史轨迹的离线观察性回放；缺少未执行动作的真实反事实，不能声称因果对照。
- **C**：从任务开头多次重跑但不固定相同中间状态；可用于整体策略评估，不能替代局部严格同状态配对。

**负责人回答（2026-10-09）：`Q-006=A`。** 正式确认严格同一决策前状态分支作为后续主要受控比较原则，真实 Benchmark 恢复性及 continuation policy 等具体实现暂缓；本决定不授权实际 rollout。

**同一条消息的额外原话**：“rq 3 需要 ab 同选”。当前文档并无名为 RQ3 的已确认独立决策。它可能指第三个问题 Q-006 的 A+B，也可能指研究问题 RQ3 或后续批次的第三题。由于明确同时给出 `Q-006=A`，在指代核清之前**保留 Q-006=A 不自动改写为 A+B**。若确指 Q-006，则可将 A 的同状态受控分支与 B 的历史轨迹观察性分析作为互补证据，但二者的证据级别不可混同；这是待澄清的解释，尚未获得新的批准。

## 8. 第三批训练规划问答（仅规划，不涉及实验实施）

**自 2026-10-09 起的唯一数据源与政策台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。Q-007-R1/R2 以下为**历史研究取证记录**，来源/模型/缓存政策后续更新仅在台账维护，避免同一信息出现多个“最新”版本；但负责人对具体源的批准、变更、日期和影响仍只能在本 Q&A 决策记录中生效。台账现仅候选，未批准下载/清洗/训练。

**负责人 2026-10-09 历史要求**：“现在先不讨论具体如何实验 只讨论如何训模型一个阶段一个阶段的来”。保留现有 E0.5 → E-DESIGN → E1～E5 总路线，不提前启动 E4；当前只在 E-DESIGN 内依次讨论训练数据、训练起点、监督信号。Q-008/Q-009 的实验规模/场景协议待重新开启，该时点 Q-003 额度和资源授权未解决；2026-10-30 当前决定已取代旧额度及等待费用批准安排。

### Q-007｜训练数据从哪里来？（第一学习阶段 A 已明确；整体方案未确定）

- **A**：优先使用经许可证和隐私核查的公开 Agent 轨迹，作为可用的**已执行动作**监督；承认缺少同状态未选动作标签。
- **B**：优先规划未来从真实 Coding Benchmark 自采高质量 Agent 状态与终局标签；暂不依赖公开轨迹作初始训练集，但采集本身需另行授权。
- **C（Planning 推荐）**：公开轨迹用于理解状态、初始化可学特征或已执行动作的有限监督；未来再用同状态受控轨迹补足比较标签并精调路由器；训练/验证/测试按任务、仓库隔离。旧 CCH/Blog 仅做调用统计先验，不伪造反事实标签。

**2026-10-09 阶段性答复**：负责人提出“从 A 开始”，表示先用公开轨迹研究模型如何学习；完整 B/C 后续是否使用尚未作出排他性选择。

**负责人 2026-10-09 本轮原话**：“第七个问题需要你仔细查询并给出对应的规划……最后决策用的变量有多个，需要都覆盖到；从 A 开始，模型学习阶段你推荐怎么做。”

**已明确范围**：第一学习阶段按 A，**以公开 Agent 轨迹起步**。这只决定起步顺序，**没有**批准“后续只用公开轨迹、不自采轨迹”，因此 Q-007 全阶段数据路线仍待最终确定。也没有批准数据下载、模型训练或服务器/GPU/API 操作。

#### 只读公开数据证据（正式训练前需再次固定版本及许可）

| 数据资源 | 已核实内容 | 第一阶段用途/限制 |
|---|---|---|
| [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | 官方卡片记录 207,489 条轨迹（某版本）；任务/仓库/Agent scaffold、消息/工具与 resolved，CC BY 4.0 且说明可用于训练 | **首选**，学习真实前缀与已执行动作结果；缺完整 Model×Effort 反事实、物理 KV/缓存计费 |
| [CMU Agent Trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 8,653 条、5 个源模型、6 类任务，含完整轨迹、reward、部分 token/timing | 可补充多领域；需逐项核验使用许可；同任务从头重跑 ≠ 相同中间状态分支 |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | 2,438 个真实仓库任务和可执行环境 | 更适合作未来数据采集环境，任务集合本身不构成路由监督 |
| [AgentSuite trajectories](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 多模型/同任务数据，含一些 thinking on/off 配置 | 可分析 effort 类差异；训练许可待核，thinking 配置并不等于任意 provider 的 effort |
| [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | 6,204 条模型×Harness 评分轨迹，含 token/cache/cost | **仅分析，不能训练**；发布者明确禁止训练、微调、蒸馏 |

#### 覆盖最终路由决策所需的八组状态

| 状态组（RESEARCH_OVERVIEW §2） | 公开轨迹是否可支持 | 阶段 A 的诚实用法 |
|---|---|---|
| 1. Task/Subtask | 任务、repo、语言与已发生步骤通常有；子任务图不一定有 | 任务类型/阶段、已观测进度；缺失子任务信息保留 unknown |
| 2. Agent/Coordination | scaffold/执行 agent 通常有；多子 Agent 关系未必有 | 角色/协作轮次/handoff 字段保留；无证据不虚构多 Agent |
| 3. Context/Memory | 有历史消息和近似上下文长度；token/压缩未必可靠 | 实际上报值与估算值分离，缺失掩码 |
| 4. Tool/Environment | 工具调用、返回与已发生错误较充分 | 只使用当前时间以前的工具调用和环境反馈 |
| 5. Verification/Recovery | 有已发生的测试/失败/重试迹象 | 历史测试结果入 state；最终 evaluator/标准补丁仅作为监督或审计，不进输入 |
| 6. KV Cache/Continuity | 物理 cache read/write、TTL、sticky 通常缺失 | 保留字段及 missing 标志；不能用文本重合冒充物理缓存命中 |
| 7. Temporal/Execution | step/turn 与部分时长可见；预算通常不全 | 使用已发生耗时/调用数，不使用未来总耗时/总 token |
| 8. Provider/Availability | 已用模型可见，真实候选能力/effort/价格表不全 | 单独保留动态动作注册表，未知标 unknown，不伪造候选 |

**还需贯穿所有训练样本的两层**：① Action/Constraints（model、provider、revision、真实 effort、候选合法性、上下文、价格、缓存/切换约束）；② Outcome/Provenance（已执行动作、最终 resolved、可用时真实 cost-to-go、数据/模型版本、task/repo、observed_at、许可与缺失标记）。八组状态全部进入设计不代表八组都有可学习的真实监督。

#### 建议的阶段 A 学习目标与后续顺序（后续尚未获批准）

1. **A0 数据/Schema 审查**：优先公开数据许可、轨迹完整度、决策前前缀提取、八组状态覆盖率和 missingness；不得下载或训练。
2. **A1 真实 Agent 前缀 → 已执行动作的结果预测**：把未来终局 resolved 作为 label，仅将其对应时刻之前的状态及当时实际采取的动作作为输入；Kev 可以用 noul 学是否最终 resolved。对 resolved=-1 或不可信结局不生成硬标签。同一任务的全部轨迹与前缀须在相同 train/val/test 侧，避免重叠和未来信息泄漏。
3. **A1 成本目标有条件开启**：只有轨迹存在同一账本范围内真实 usage、时间与价格，才可学习观察到的剩余 token/费用区间（可用有序 score）；缺失时不制造 USD 标签。这里仅学习行为策略下结果，不推出其他动作的效果。
4. **A2 能力/预算/缓存规则辅助**：后续可用具有确定真值的能力表、费用计算和明确缓存/连续性规则产生 typed choice/noul/score 的辅助训练样本，以覆盖公开轨迹薄弱状态；这是规则监督，不是伪造真实模型成功率或缓存效果。
5. **B 真实动作比较（未来）**：只有相同恢复状态下多个真实合法 (model, effort) 的可比终局与成本，才能训练有依据的候选胜者 choice/pointer；单条行为轨迹的其他候选结果保持 unknown。
6. **C 路由校准（未来）**：在成功率约束下取舍，独立校准集选阈值和温度，保留硬约束优先；校准后的概率不可宣称自动是另一模型反事实成功率。

**Kev 官方依据**：项目 https://github.com/jaredpalmer/kev 的训练说明提供已训练 Kev-4B 权重的 init_from + LoRA/pointer continuation，并支持 choice/noul/score 的有监督样本；是否采用官方 checkpoint 为唯一训练起点属于尚待回答的 Q-010。这里只提供学习阶段推荐，不批准 GPU、权重下载、实验规模、种子、训练超参或新实现链。



#### Q-007-R1｜开源训练数据来源与处理方案（2026-10-09）

**本轮只处于第一大阶段：训练数据来源与加工规范研究。** 用户要求覆盖两类监督数据（运行轨迹、不同任务的模型选择）、全部八组状态、缓存、供应商规则、数据量；尚未批准下载/清洗/训练，以下均为 Planning 方案，不是已产出的训练集。

| 来源 | 可提供的证据 | 许可/限制 |
|---|---|---|
| [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | v1.0 约 207k 软件 Agent 轨迹，v1.1/v1.2 已扩容；任务/工具/消息/resolved；轨迹主源 | CC BY 4.0，固定实际 revision，-1 结局不作成功标签；没有同状态未选动作反事实 |
| [SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories) | 5017 条公开训练轨迹子集；其它 SWE-smith 任务与轨迹不能混作该子集 | MIT 数据卡，核对生成模型输出的训练用途 |
| [LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | 33 models/21+ datasets/400k+ benchmark 记录；同题模型输出、性能、Token、费用 | **数据许可证未核实，暂不纳入训练**；大多请求级，并非长程 Agent |
| [RouterBench](https://huggingface.co/datasets/withmartian/routerbench) | 30k+ Prompts、11 模型的回答/质量/估算成本 | **数据集许可标签不明，暂不纳入训练**；请求级比较 |
| [TwinRouterBench Static](https://huggingface.co/datasets/Amorph/TwinRouterBench) | 970 个 Agent 前缀 → 四级 tier，Apache-2.0 | tier 不是具体 model×effort；防正式对照集泄漏 |
| [Arena Human Preference 55k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | 同题两模型偏好，Apache-2.0，参考 RouteLLM | 人类偏好不是终局软件任务成功 |
| [CMU agent_trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 8653 个多领域/多模型轨迹 | 访问受限 且训练许可待核 |
| [AgentSuite](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 30 模型 × 273 任务、thinking 配置和评估结果 | 许可待核；thinking 开关不等于通用 effort |
| [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) / [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | 真实代码修复任务及可执行环境 | 任务不是天然的已标注模型选择轨迹 |
| [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | model×harness 数据及成本 | **发布条款明确禁止训练、微调和蒸馏** |

**相关训练思路**：RouteLLM 从同题双模型 human preference 训练模型胜负；RouterBench 和 LLMRouterBench 提供按任务的多模型真实得分/成本来拟合静态模型路由；Kev 官方基础决策训练集约 12,576 个 typed 选择/规则样本，后续分阶段添加真实文档及开发工具标签并校准。以上来源均不能从单条 Agent 历史轨迹凭空推断未选 model×effort 的结局。

**加工规范 / 顺序**：

1. Source manifest：repo/dataset revision、license、训练用途权、任务和原始数据散列值；未知许可进入 quarantine，商业 API 输出的模型训练权限需单独核对。
2. Task/Episode：task/repo、harness、模型版本、实际 effort、工具、时序、可信 resolved；-1 不作为成败监督。**先按 task/repo/近重复任务去重并固定 train/validation/test，再抽轨迹前缀**。
3. DecisionPrefix：在每个真实模型调用前截断，保留 Research 八组状态及 observed_at、provenance、measured/estimated/missing；标准修复补丁、最终测试、未来 token/调用/失败不得进入输入；同任务前缀采样加权防伪独立。
4. Actions：provider/model/revision/effort requested/effective、候选合法性、上下文、工具、价格和缓存/会话条件；缺失为 unknown，不伪造多 Agent handoff、effort、缓存。
5. Outcome：严格区分 observed task resolved、真实计费时的 observed cost-to-go、同静态 Prompt 的 model score/preference、由能力表确定的合法性标签。未执行候选 outcome 始终 missing；API status != task resolved。
6. Kev train JSONL：noul（实际观察的成败或规则真值）、score（有可信计量的有序成本类别）、choice（真实可比较的动作或确定性规则）；保留 task/source/split/label provenance 和 option permutation；无真实反事实时不能标注最优中途 model×effort。
7. 训练数据 ready 记录项：许可证完整、去重分割无泄漏、字段/八组状态覆盖率与缺失率、真实成功标签可用率、effort 与模型组合覆盖、缓存观测覆盖、USD/quotaUnits 保真、JSONL 可验证和 checksum。

**Cache 与厂商政策**：公开轨迹通常只有 estimated prefix overlap，缺少实际 physical cache read/write。CCH/Blog 是成本先验不能作同状态缓存效果监督；未来实际 Provider usage/vLLM metrics 才能给缓存真标签。官方缓存差异见 [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching)、[Claude](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)、[Gemini](https://ai.google.dev/gemini-api/docs/caching)、[DeepSeek](https://api-docs.deepseek.com/api/create-chat-completion/)、[vLLM](https://docs.vllm.ai/en/latest/usage/metrics/)。effort 支持、缓存 TTL、计价、限流、工具、隐私/ToS 等**不能只训练进 Kev 权重**，应由版本化 Registry+硬约束执行，样本只用于学习稳定的状态与动作效果。Google [Gemini API Terms](https://ai.google.dev/gemini-api/terms/) 对竞争模型训练有条款限制，不能默认商业 API 输出可用于训练。

**样本量**：Kev 官方基础约 12,576 个决策样本，RouteLLM 采用万级偏好，说明不必无差别全量喂 20 万轨迹。但对任务级路由并无证明足够的固定 N。可先**规划**审计约 1k–3k 独立任务、数千～数万条有真实结局的代表性前缀及合法静态模型比较，按 task/repo/model/effort 独立覆盖、学习曲线和标签质量决定扩张；缺乏同状态多动作真值时增加 prefix 数不能补救。

**大阶段（仅讨论结构）**：D-PREP 当前来源/许可证/Schema → D-BUILD 经批准实际加工数据 → M-INIT Kev 对观察到的动作结果学习 → M-CHOICE 只有真可比结果时学选择 → M-CAL 可靠性校准 → EVAL 最后讨论实验。仍遵守既有 E-DESIGN/E1–E5 和所有权限，不创建第二条执行链。


#### Q-007-R2：数据候选全集 V1（缓存、记忆、多 Agent、时间与 Provider；2026-10-09）

**负责人本轮明确范围**：先把可取得的数据集、相关科研工作及主要国内外厂商官方政策尽量搜齐；**先不决定数据量、不做数据清洗，也不新建 Agent 执行框架**。本节只扩充已有 Q-007 的数据候选目录，**尚未完成训练许可证/原始字段的最终审计，也没有下载样本**。

##### A. KV 缓存、真实调用和时间成本

| 候选编号 | 源及关键数据 | 研究用途/不能宣称的内容 |
|---|---|---|
| CACHE-01 | [Mooncake FAST25 traces](https://github.com/kvcache-ai/Mooncake/blob/main/FAST25-release/README.md)：真实 conversation 12,031 条、toolagent 23,608 条；另有 synthetic 3,993 条。匿名 timestamp、input_length、output_length、512-token 前缀 `hash_ids` | **P0 首选**：真实调用里的前缀块可复用机会 + 真实到达时间；**没有实际生产 cache_read_tokens、cache_hit 标签** |
| CACHE-02 | [Mooncake 旧版 arxiv trace](https://github.com/kvcache-ai/Mooncake/tree/main/arxiv-trace) | 旧版本比较；可能与 FAST25 重叠，不能当独立新样本数 |
| CACHE-03 | [Mooncake KV cache simulator](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html) | 用真实块散列值重放，可模拟不同容量/淘汰条件下的缓存读取与 hit rate；**模拟数据不是生产实际命中** |
| CACHE-04 | [KV Cache Workload Bench](https://github.com/hokiyoung/kv-cache-workload-bench) | ShareGPT 派生多轮/并发/增长/驱逐的合成 workload；无 Provider 真实账单 |
| TIME-01 | [BurstGPT](https://github.com/HPMLL/BurstGPT) | 数百万条真实请求、session ID、耗时与 Token，研究服务压力、会话增长、延迟预算；无原始 Agent task-resolved |
| TIME-02 | [Alibaba xMaaS 2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas) | 真实 LLM MaaS 服务集群的资源/模型实例/显存/时间负载，**多数为实例级，不是每次 prompt 或 KV hit** |
| TIME-03 | [Alibaba GenTD26](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) | 包括图像生成等的队列/QPS/延迟/资源工作负载；仅系统时间行为补充，不当成 LLM 任务路由标签 |
| TIME-04 | 既有 Open-SWE-Traces、SWE-smith 与 Mooncake toolagent | Agent 已发生阶段、时间和 Token 等作为时间状态；同一原始数据只登记一次，剩余预算必须有原任务预算减真实已耗才可靠 |

**缓存标签定义（非可互换）**：provider/vLLM 报告的 read/write/hit token 才是 measured；Mooncake 共享散列值仅为真实请求可复用 prefix potential；配置缓存 TTL/容量/路由后推演的是 simulated hit；文本最长公共前缀只是 estimated overlap。**不可将散列值匹配、模拟命中训练成商业 API 真实物理命中标签。** 跨模型、跨实例、跨账户/租户共享 KV 的技术和权限不能假设存在。

##### B. 上下文、记忆、协作与执行状态

| 来源 | 已核实特点 | 训练相关性及限制 |
|---|---|---|
| [LoCoMo](https://github.com/snap-research/locomo) | 10 个超长、多会话对话、时间、会话摘要、QA 证据 | 记忆压缩、跨会话更新、信息保持；不是路由胜者 |
| [LongMemEval](https://github.com/xiaowu0162/longmemeval) | 500 问答，历史会话、时间与证据，多会话更新/冲突 | 记忆特征/检索候选，需防止把官方 test 用作训练 |
| [LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) | 451 问题，数百条 web Agent 轨迹组成长历史，记忆、工作流、环境失误 | **P0 长程 Agent 历史**；是否开放训练用途及实际记录结构另核 |
| [MemoryAgentBench](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) | 增量多轮、检索与记忆更新 | P1，非任务模型选择真值 |
| [MemoryCraft collection](https://huggingface.co/datasets/daven3/MemoryCraft) | 汇编 LoCoMo/LongMemEval/MemoryAgentBench/AMA-bench/Membench | P2 转换参考，沿用各上游许可证、不可重复样本计数 |
| [LongBench](https://github.com/THUDM/LongBench) | 长上下文检索/理解基准 | 上下文压力和能力的可选辅助数据 |
| [MARBLE / MultiAgentBench](https://github.com/ulab-uiuc/MARBLE) | multi-agent 角色、star/chain/tree/graph、共享记忆、milestones | **P0 多 Agent 协作环境/Schema**，开源任务不表示全量动作轨迹已发布 |
| [MASBench](https://github.com/BUPT-GAMMA/MASBench) | 部分可观测的协议、记忆、路由与通信成本 | P1，训练轨迹和许可证待核 |
| [AgentWorld](https://arxiv.org/abs/2609.31590) | 长程多智能体、非对称角色和真实协作依赖 | P1，刚发表的新基准；具体记录与许可证待核 |
| [OpenSquilla](https://github.com/TokenRhythm/opensquilla) | 完整 Harness、ContextBudget、Memory、Router、可选 Ensemble | **软件/论文参考，不是公开训练轨迹数据集**；参考 [路由文档](https://github.com/TokenRhythm/opensquilla/blob/main/docs/features/squilla-router.md) 和 [Memory 文档](https://github.com/TokenRhythm/opensquilla/blob/main/docs/features/memory.md) |

**OpenSquilla 的具体研究含义**：[Harness-Native Agentic Routing](https://arxiv.org/abs/2607.11399) 将 query、Harness state、model decision、execution trace、outcome 与 cost 串成数据飞轮。[ContextBudget 源码](https://github.com/TokenRhythm/opensquilla/blob/main/src/opensquilla/engine/context_budget.py) 管理压缩与上下文预算，[Decision Record 源码](https://github.com/TokenRhythm/opensquilla/blob/main/src/opensquilla/engine/steps/router_decision_record.py) 记录实际选用动作。用户的设想应写成**单一 Agent Harness 在模型请求前组织 Context/Memory、Agent 协作、Tool、时间和预算的 StateSnapshot；外部 Kev Router 只接收状态和动态合法候选，选实际 (model, effort)；Provider Adapter 执行并回传 usage，形成训练账本**。现阶段不要复刻 OpenSquilla，也不允许新建第二条 Agent 主调用链。OpenSquilla 的多模型 proposer→aggregator ensemble 是**复合动作**，不自动等于现有 Q-002 已批准单个 (model, effort) 候选。

##### C. 官方 Provider 规则数据源（国内主要模型、国际闭源与开源托管）

| Provider 或模型/部署系列 | 官方证据 | 本轮认定与后续字段 |
|---|---|---|
| OpenAI / GPT、Codex | https://developers.openai.com/api/docs/guides/prompt-caching | 缓存 input read/write、TTL、写入收费随新旧模型不同；按 API/型号/地区/组织保存 |
| Anthropic / Claude | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | cache_read_input_tokens、cache_creation_input_tokens、5m/1h、breakpoint；effort/tool 前缀约束要验证 |
| Google / Gemini | https://ai.google.dev/gemini-api/docs/caching | 隐式和显式缓存、TTL/存储价格；thinking 按实际型号 |
| xAI / Grok | https://docs.x.ai/developers/advanced-api-usage/prompt-caching | 自动前缀缓存、cached_tokens 和会话 ID 粘性 |
| OpenRouter（聚合） | https://openrouter.ai/docs/guides/best-practices/prompt-caching | provider sticky/session_id、真实承载 endpoint；同模型跨实际供应商不必有共同缓存 |
| DeepSeek 原厂 API / 自托管开源 | https://api-docs.deepseek.com/zh-cn/guides/kv_cache/ | hit_tokens/miss_tokens、尽力命中；**开源权重不继承 API 的缓存定价** |
| 阿里百炼：Qwen、托管 GLM/DeepSeek/MiniMax | https://help.aliyun.com/zh/model-studio/context-cache | 隐式/显式、模型/地域/版本相关 TTL、折扣和 cached_tokens |
| 火山方舟 / 豆包 | https://docs.volcengine.com/docs/ark/context-cache?lang=zh | 隐式/显式/Session cache，thinking/tools 的连续性和字段 |
| Kimi / Moonshot | https://www.kimi.com/academy/best-practices-for-context-caching | 5m/1h、cache read/write，随 Chat/Responses/Messages API 字段变化 |
| 腾讯 Hunyuan / TokenHub | https://cloud.tencent.com/document/product/1729/101838 | 旧 API 的 CachedTokens；业务迁移到 TokenHub，现行端点/型号单独核 |
| 百度 Qianfan / ERNIE | https://ai.baidu.com/ai-doc/WENXINWORKSHOP/Rm6uq7jy9 | 官方证实部分型号 cached_tokens，**不是全系列自动同能力** |
| 智谱原厂 GLM / Z.ai | https://docs.bigmodel.cn/ | 厂商入口确认，cache/effort/价目具体型号与字段本轮**未核**；不能套用百炼托管 GLM |
| MiniMax 原厂 | https://platform.minimaxi.com/ | 厂商入口确认；原厂 cache/read/effort 逐型号**待核** |
| 阶跃星辰 StepFun | https://platform.stepfun.com/ | 厂商入口确认；具体模型参数与缓存**待核** |
| 硅基流动 SiliconFlow | https://docs.siliconflow.cn/ | 托管服务规则按实际 endpoint，不按模型权重名推断；cache **待核** |
| 国际其它及转售 | https://docs.mistral.ai/ 、https://docs.cohere.com/ 、https://docs.together.ai/ 、https://console.groq.com/docs 、https://docs.fireworks.ai/ | 纳入 provider 候选全集，但 per-model cache/effort/价格本轮**待核** |
| 自托管开源 Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan 等 | https://docs.vllm.ai/en/latest/design/prefix_caching/ 、https://docs.sglang.ai/ | 缓存由真实 inference engine/实例/tokenizer/tenant 隔离决定，不由权重名称决定 |

**Registry 建议字段**：source_url/verified_at/evidence_level、provider/model/deployment/revision/region、open/closed/hosted、supported_context/tools/effort_requested/effort_effective、cache_mode/read/write/TTL/min_prefix、price_version/currency、health/rate_limit、tenant/session_affinity、data_retention/training_output_terms/effective_dates。政策未知记 unknown，不记 false。厂商政策、effort 支持和价格作为动态合法性及计价**外部硬约束**，不通过训练 Kev 权重当作永久真值。缓存和时间类数据只是补充有证据的输入或条件监督。

**阶段关闭边界**：本轮已汇集 candidate source catalog V1，但**没有宣称全部通过许可证审计**，没有指定样本量，没有下载、清洗、生成 Kev JSONL、使用 GPU/服务器/API，亦没有构建 Agent 框架。下一步才按用户另行指示开展逐个数据源许可与字段核对；随后再讨论真实数据加工。

### Q-010｜Kev-4B 训练从哪个基础开始？（已提出待答）

- **A（Planning 推荐）**：以官方版本明确的 Kev-4B 权重为起点，优先研究官方 continuation/LoRA + pointer 选择头适配；先定训练方法，不操作 GPU。
- **B**：从其底层 Qwen3.5-4B-Base 出发初始化 Kev 风格决策头并重新训练；与已确认的“Kev-4B 为起点”有迁移影响，若选择须再论证权重、标签需求与可行性。
- **C**：两种初始化方式均保留为候选研究方向，先做只读证据核查再决定唯一训练起点；不启动双套实现。

**2026-10-10 P1 已确认事实**：项目 `.venv/bin/python` 为 Python 3.12.3，已有 PyTorch `2.14.0+cu126`，CUDA 编译版本 12.6，`torch.cuda.is_available() == True`；系统 `python3` 导入 PyTorch 失败。项目 `.venv` 实际链接到已有 CodeLlama 环境，未建立独立环境。此前“缺 GPU 依赖”的结论只适用于系统解释器。本轮无需重复安装、下载或重跑 GPU 测试。

**已有汇总及限制**：服务器 `runs/E1-smoke-test-20261010/smoke_test_results.json` 与系统临时目录中的 `p5_smoke_test_results.json` 均为 3,169 字节，内容完全相同，计为一份历史记录。该记录报告两模型 `PASS`：Kev 使用 16 条记录完成 2 次参数更新，峰值显存 11,270,153,216 字节；Laya 使用 16 个训练项、4 个标定项；两者均报告重载概率差为 0。本轮未追溯齐全当次原始 stdout/stderr、解释器与实际保存文件，不能独立确认全部执行细节，也不能据模型重载宣称优化器状态恢复。

**效果与兼容性仍有限**：汇总所列 Kev 8 个损失值的均值为 `2.327849 → 2.458256`，Laya 4 个评估项的准确率保持 25%，均不足以证明路由能力提升。现有环境也未满足 [Kev 当前声明的全部依赖版本](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/pyproject.toml#L21-L29)，短训练记录不代表所有训练与缓存推理路径均可用。官方方式与未实现范围见 [研究总纲第 4.4 节](RESEARCH_OVERVIEW.md#44-2026-10-10-p3官方训练支持与方法范围)。

**待答**：A/B/C，仅决定正式训练起点；已有记录可用于资源判断，正式训练范围与参数尚未确定。

### Q-011｜首先学习什么监督目标，如何分阶段？（新问题，已提出待答）

**2026-10-11 负责人最新范围决定（Stage 1 具体层面）**：用户确认继续保留 **Regime A+B+C**，按来源及监督类型分别评价；`MR-STAGE1-FAST-FIX` 已完成、修复版为 `83,259` 题。用户明确**暂不授权正式 GPU 训练**，仅允许在原唯一 `prepare_router_data.py --mode views` 内最小修复训练题面约 400 字符截断、必要 CPU 验证并确定 Kev/Laya 第一批实际支持的参数；这一新输入修复**尚未收到完成报告**，不得当作已经执行。既往有条件 GitHub 文档/必要源码推送授权有效，但不包括训练、API、模型下载、覆盖原始与固定文件或新建链路。ROUTE-004 `TRAIN_ALLOWED_VERIFIED`；ROUTE-001/002 `LICENSE_PENDING` 原样保留。此决定只锁定 Stage 1 **静态 A+B+C 的数据使用方向**，**不代表**已经最终选择 Q-011 的未来同状态动态训练顺序 A/B/C，也不代替 Q-010 的初始化选择或 GPU 许可。



- **A**：先只预测已执行动作对应的任务最终成功与观察到的剩余成本（outcome / cost-to-go），待有可比数据再决定是否做动作排序。
- **B（Planning 推荐）**：训练路线分为“已执行动作的 outcome/cost-to-go 监督 → 同状态成对标签训练动作选择/pointer head → 受约束路由校准”三步；各步是否能启动由数据真实性与权限决定，不假定配对数据现成。
- **C**：一开始直接学习模型×effort 最优选择；仅在已具有同状态合法动作可比较标签时才合理，否则不能从单条行为轨迹推导最佳动作。

**待答（2026-10-11 P3 仍未决；负责人已批准 `MR-STAGE1-FAST-FIX` 最小修复并完成全量 CPU 校验，当前 Stage 1 技术与代码阻塞已 100% 解除 `STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`、许可状态保持待决、`RUNTIME_JOINT_DATA_READY = NOT_READY`）**：A/B/C。在 `MR-STAGE1-FAST-FIX`（证据归档于 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/stage1_manifest.json` 与 `runs/MR-STAGE1-20261010/final-stage1-and-joint-coverage-audit.json`）中已完成：(1) **P0 数字与口径纠偏**：公开数据总量严格为 14 个有效源 **`6,600,628` 行**（不与自有数据 `OWN-001` 110 聚合行、`OWN-002` `221,128` 调用行、`OWN-003` 79 衍生汇总行混加为 `6,620,400`），AgentSuite 统一为 **`273` 任务 × `30` 配置 = `8,190` Episode**（`1,365` 对严格同权重开关 + `273` 对同底座专用 Thinking 权重 + `1,365` 对已确认跨版本对照），八类状态统一为唯一标准名称（`Task/Subtask`、`Agent/Coordination`、`Context/Memory`、`Tool/Environment`、`Verification/Recovery`、`KV Cache/Continuity`、`Temporal/Execution`、`Provider/Availability`）；(2) **`ROUTE-001` 完整原始 Prompt 散列合并、去重与冲突隔离（P1）**：按未截断原始 `(origin_query, prompt)` 的 `full_prompt_hash` 将跨子集同题导出合并为 **`24,441` 道独立真题**，去重 `21,144` 条完全一致的同模型重复评测（恢复 `llmroute_hle_57` 为 `gemini-2.5-pro` 唯一最高分胜者），并将 `1,219` 道潜在胜者分数或费用冲突题（`439 + 22 + 758`）隔离至分析集，保留 **`8,441` 道无冲突纯静态单胜者题**（`6,788 / 812 / 841`）；(3) **方案 B 一键可复现导出与候选打乱（P2–P4）**：`prepare_router_data.py --mode views` 在 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/` 生成 **`83,259` 题纯静态主集（`train: 66,566, val: 8,343, test: 8,350`）**，两次独立运行 SHA256 100% 一致，`ROUTE-002` 首位置 `index 0` 胜出率降至均匀的 `9.20% / 9.00% / 9.51%`，且在官方 Kev（`384/7552`）与 Laya（`--max-len 1024 --head-max-len 512`）下 `100%` 零跳过通过（交集 `100%`）；(4) **许可证与动态联合覆盖状态**：`ROUTE-004`（`39,716` 题）为 `TRAIN_ALLOWED_VERIFIED`（`apache-2.0`），`ROUTE-002`（`35,102` 题）与 `ROUTE-001`（`8,441` 题）保持 `LICENSE_PENDING`；八类状态 + `(model, effort)` + 真实缓存 + 真实费用的联合动态记录仍为 **`0`**。待负责人明确 GPU 训练及 `LICENSE_PENDING` 范围授权后即可启动正式微调。

## 2026-10-16 · Q-017：论文五个 RQ 研究定位（负责人明确确认）

**问题**：早期 V7 将 Model×Native Effort、动态候选与历史监督拆成独立 RQ，且完整任务经济性排在末位，无法突出主目标；RQ1 机制与 RQ5 的长期成本题重复。如何重排并为多 Agent 场景提出独立 RQ4、RQ5？

**负责人原意（忠实摘要）**：确认选用前次候选 **B「多 Agent 任务究竟有多少可利用的模型互补性」** 与 **C「为什么某些多 Agent 任务不适合动态路由」**，分别设为 RQ4、RQ5。原本独立的 **Model×Native Effort 联合选择 RQ4 放入新的 RQ1**。要求具体讨论 RQ1 包括什么，将五个 RQ 的最新研究想法、图表与空白表格同步到六份相关 GitHub 文档；其中实验详细定义以「汇报三」专用文档为主。

**最终决定（2026-10-16，研究方案级；不是新 API/GPU 运行授权）**：
- **RQ1：完整 ModelRouter 的真实任务成功率—完整 Episode 费用横向比较与机制**。对固定强/便宜/开发集最优、Role-static、随机整任务混合、Task-only、Greedy/Sticky、可比 Agent Router 与 Full；内部包括 Model-only/Effort-only/Joint、T/M/H 单/双/三组信息与 Role/KV/Trace/Verifier 重点消融、费用分解和 Router 自身开销。所有调用动作必须实际合法；不从不同 Harness 原论文数字冒充直接对照。
- **RQ2：固定 Router 的模型池 K/成员选择**。K 是不同模型身份数；另报每模型真实 Native Effort 菜单与总合法动作数。
- **RQ3：固定模型池身份/K/原生 Effort/Router 的任务拆分粒度**。对同一原任务比较 G，并记录实际 Agent 数、F、handoff 与费用；跨任务类型分别报告。
- **RQ4：不同子 Agent 角色之间的可利用模型互补性**。固定池和 G，检验角色×模型配置表现差异，并比较 Role-static 与 Role-aware 的完整任务经济结果；历史观测不能等于未选动作反事实。
- **RQ5：动态路由的工作负载适用边界**。固定池/G/Router，事先定义多 Agent 任务类型、规模/复杂度及协作结构等层，核对在可比成功率条件下 Full 相对强简单基线的**增益与无增益区域**；仅分层汇总 RQ1 结果不足以宣称独立科学贡献，须有可检验的条件交互和不确定性。

**执行/论文影响**：维持历史 Q-001～Q-016 的权限、数据协议与 GPU 训练事实。RQ 调整不重启、不打断现有 P22 队列；不下载未审核数据、不运行收费评测。本轮只同步六份文档。**八张图和十二张空白结果表**改以 V8 对应，全部数值留空（详见 [汇报三 V8](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)）。未来论文如实报告消融负结果，开发集选择和独立测试集分离。


## 2026-10-18 · Q-019：论文 RQ4 正式改为系统消融（取代 Q-017 的旧 RQ4）

**负责人本轮明确指令（最新优先）**：“让它变为成新的 RQ4，原来版的 RQ5，原来版的 RQ4 就直接删掉”。这不是候选或待讨论项。

**正式决定**：
- **RQ1** 整体效果：完整 Router vs 同类路由方法，Task Success–Complete Episode USD。
- **RQ2** 模型池：池成员与模型身份数量 K。
- **RQ3** 任务拆分：同一池与 Router 下的可复现粒度 G。
- **RQ4 新正式主题：系统消融**：把之前在 RQ1 内部的 Model×Native Effort 联合/单独选择、任务与候选经济性/历史 T/M/H 信息组单组/双组/三组、KV/Trace/已发生反馈及合规 S1/S2/S3 训练监督、Laya/Kev 代表性数据配方拆分为独立 RQ。固定任务/池/Harness，完整 Episode 费用与成功率是真实主要评价，训练离线 Accuracy 仅为辅助。
- **RQ5** 延续原 V8“动态路由工作负载适用边界”，不改基本科研问题。
- **原 V8「RQ4 不同 Agent 角色是否存在模型互补性」从当前论文计划中删除**，Fig.7/T8 重新用于系统消融。历史 Q-017 的原始批准记录只保留可追溯意义，不再是最新 RQ4 定义。多 Agent 角色仅在 Harness 真能提供时作为路由状态和消融候选，不作为独立 RQ。

**影响范围**：更新汇报三最新论文方案、汇报提纲、研究总纲、长期记忆、项目状态和数据台账的现行 RQ 映射；不修改原有运行中的训练或测试、许可证、预算和实际完成记录。八张图、十二张结果表数量不变，数据格继续待真实结果。

## 2026-10-19 · Q-020：V10 个人 Rootless Docker 与同一实验链执行授权

2026-10-19 历史授权：在 A6000 个人用户空间复用官方 Rootless 组件、下载必要官方镜像并执行 Harbor Oracle；当时沿用既有 Provider 与旧 Token 额度（现已取消）；由主 Agent 在 main 提交并按本次工作会话推送。禁止改宿主 Docker、系统权限、共享服务、GPU 训练与私人凭据；不运行 CI/PR 或未获单独批准的 Sealed Test。

执行结果：Docker 29.4.1、RootlessKit 2.3.6 和 subuid/subgid 范围存在，但缺少 `newuidmap`、`newgidmap`，真实 UID/GID 映射失败。个人安装分支按负责人要求停止，没有使用 sudo 或减少隔离要求。官方 Trial 仍为 0。后续需由宿主管理员提供官方 uidmap 工具及相应权限；期间继续已授权的代码与记录工作。

研究决定不变：沿用 Q-019。旧 RQ 预设数值仅用于开发，正式数据必须来自原始官方 Episode。同一任务、Harness、候选池与预算用于对照；费用未知保留 `N/A`，Router fallback 单独披露。没有新的科学结论，不更新 Research。

## 9. 决策变更记录

以下保留各时点的决定与执行方表述；历史 `PASS` 记录的证据范围，以本轮 Q-010 补充为准，不作为新增训练或 API 授权。

| 日期 | Q-ID | 变更 | 证据 |
|---|---|---|---|
| 2026-10-09 | Q-001 | 首次提出 A/B/C 方案；Planning 推荐 C；用户回答及最终决策待定 | E-DESIGN 启动的历史记录 |
| 2026-10-09 | Q-001 | 负责人批准 A，直接从真实公开 Coding Benchmark 开始，取代原推荐 C | 本轮明确答复 |
| 2026-10-09 | Q-002 | 负责人批准 B，API+本地模型混合候选，具体能力待核验 | 本轮明确答复 |
| 2026-10-09 | Q-003 | 历史记载 B 原则：本地模型预算不限制、API 按模型限额；旧待定金额/权限仅保留历史，2026-10-30 已取代 | 本轮明确答复 |
| 2026-10-09 | Q-004～Q-006 | 第二批三个 A/B/C 问题正式提出，均无用户答复 | 当时提案，后有正式答复 |
| 2026-10-09 | Q-004 | 负责人批准 B：成功率约束下优化整任务成本 | 本轮明确答复 |
| 2026-10-09 | Q-005 | 负责人批准 B：分层基线/消融；具体实施暂缓 | 本轮明确答复 |
| 2026-10-09 | Q-006 | 负责人批准 A：同状态受控分支；另记“rq 3 需要 ab 同选”指代待澄清 | 本轮明确答复与补充原话 |
| 2026-10-09 | 研究协作顺序 | 负责人要求先只讨论怎样训练模型、逐阶段推进，不讨论具体实验实施 | 本轮明确要求 |
| 2026-10-09 | Q-007、Q-010、Q-011 | 第三批训练导向三个问题已提出待答；Q-008/Q-009 暂缓 | Planning 提案，不是批准 |
| 2026-10-09 | Q-007 | 负责人指明第一学习阶段从 A 公开轨迹开始；补充公开数据检索、八组状态与学习阶段边界；全阶段数据选择仍开放 | 本轮答复与只读资料核验，未授权执行 |
| 2026-10-09 | Q-007 台账治理 | 负责人要求专门登记数据集来源、Provider/Cache 政策并为后续 AI 筛选清洗留结构；建立 DATA_SOURCE_AND_POLICY_REGISTRY.md 作为唯一详细台账 | 本轮明确文档结构需求；未批准具体源或执行 |
| 2026-10-09 | 论文实验简化执行 | 负责人要求最少可执行代码、单终端实时进度，移除额外工程流程和版本固定 | 最新执行风格，科学数据隔离与真实标签仍需保持；不代表已有训练成果或第三方计算/付费 API 授权 |
| 2026-10-09 | 公开数据清洗位置 | 本机存储不足，选定自有服务器作为 Open-SWE/SWE-smith/Arena/Mooncake 等公开数据下载、CPU 清洗及存储环境；中文目录优先；完整数据不推 GitHub | 用户已委派执行，实测报告未回传，GPU/付费 API 未因此获批 |
| 2026-10-09 | 本机 Codex 论文知识库 | 要求同步 GitHub 五核心文档，用 Paper Research Router 整理 58 篇现有 PDF，Obsidian 中一篇一笔记、双向链接并补充直接相关路由/Jev/Kev 资料 | 明确交付任务；本 ChatGPT 负责 Planning 和需求学术讨论，本机 Codex 执行 |
| 2026-10-09 | 论文引用与模型公开 | 允许将论文创新叙事放在任务级状态、缓存与 model×effort 决策，使用 Kev 已发布权重仍须在 Implementation/Experiments 披露 | 不能将闭源 Jev 训练方案或 Kev LoRA 架构写为原创 |
| 2026-10-09 | Q-007 首批数据科研审查 | Execution 在服务器产出 80,970 混合样本并提供 GitHub 966f582 源码与 50 条预览；Planning 核对到 Arena 真实 winner 30k，但 Agent effort/complexity、Mooncake dispatch/缓存、成本 tier 大量为规则标签；且 TwinRouterBench 已混进 train/val/test | 已执行数据解析≠真实最优路由监督；禁止以 80,970 直接证明 TRAIN_READY；同一 prepare_router_data.py 更正、TwinRouterBench 留外部评测 |
| 2026-10-09 | Kev 官方格式核对 | 官方数据样本要求 questions.choice.criteria 对象与 choice 字符串标签、score.criteria 等级数组与整数索引标签；现有输出为 options、levels 及字符串 score 标签，且补充 provenance 需确认不影响官方解析 | 在进入微调前最简改造与 validate 即可，不增加额外执行限制；训练/评测按 task/repo/group 隔离，不以单个 trajectory 为隔离单位 |
| 2026-10-09 | Q-007 重建成果二次科研复审 | Planning 核对 16 个 GitHub 字段统计与唯一清洗程序，核出 **3,963,661 vs 报告 2,282,484** 总量冲突；Open-SWE 6 分片仅部分、SWE-smith 仅 ticks、AgentSuite 8/30 模型；前决策状态混入当前工具动作、模型名错映射、Mooncake 复用计算非有序 prefix 与其它字段问题 | 这是 Planning 源码与公开数据审查，**不是负责人新增批准/否决**；当前不应以 TRAIN_READY 开始正式微调；只修改既有脚本，不再全盘删原始文件 |
| 2026-10-10 | Q-007 第三次科研复审（0b39a7e） | GitHub 16 源字段统计和=6,600,628，与 Execution 报告一致；多项代码更改已确认，但 AgentSuite pass_criteria/target_question 可能含评测 rubric、SWE-smith 代码块误判工具动作、Mooncake 只有前缀复用潜力、missing_rate 仅按预览样本、缺真正同状态路由标签与 Train/Val/Test 物理切分、TRA-001 官方仍部分下载 | **Planning 审查意见，非负责人新批准**；保留已下载原始数据，继续原脚本定向科研纠偏；不得宣布 TRAIN_READY 或启动微调 |
| 2026-10-10 | Q-007-FINAL 数据资产定版与 Kev/Laya 兼容验证 | 完成全部已登记 Source ID 资产盘点与机器可读 `manifest.json`、双遍确定性可复现验证；将 LLMRouterBench 13,072 道同分成本未比/并列题移入分析集，锁定 **84,310 道严格唯一单胜者监督题**（Train 67,428 / Val 8,436 / Test 8,446）与 970 步 Holdout；修复短/标点 Prompt 跨集泄漏（0 重叠）；通过官方 `kev` 与 `laya` 仓库 100% 全量兼容性及 A6000 最小训练/保存恢复 Smoke Test | **Q-007-FINAL 全部 PASS，数据资产正式定版**；下一阶段为 E1/E2 Kev/Laya 正式训练与离线验证，E3 Coding Benchmark 批量运行尚未启动 |
| 2026-10-10 | 全量 660 万条数据分层、八组状态覆盖与目录治理 | 对账确认服务器唯一正式固定划分为 `67,428 / 8,436 / 8,446`；完成 16 公开源 + 3 自有源 8 维逐行清点、8 类研究状态覆盖矩阵及五阶段训练课程设计；精确拆分 AgentSuite Thinking 同一权重运行时开关（1,365 对）、专用 Thinking 权重（273 对）与跨版本对比（1,365 对已确认）；建立 `runs/` 与 `.tmp/`，清理本任务临时目录，脱敏全部公开文档中的服务器绝对路径 | **全量数据分层与目录治理完成**；等待负责人确认五阶段训练课程与历史遗留文件清理后进入 E1/E2 正式训练 |
| 2026-10-10 | Stage 1 科学监督定义与训练数据配置定稿（`MR-STAGE1-20261010`） | 只读查明 RouterBench 全部 87 条得分+估价双并列题（`68/10/9`，均为 `['claude-v1','claude-v2']` 并列，顺序选 `claude-v1`）；将 Stage 1 精确拆分为人类偏好（`39,716`）、纯质量唯一最高分（`3,985`）、同分最低费用规则（`40,503`），排除 87 条双并列与 19 条 AgentSuite 固定对话题后锁定 **84,204 题洁净主集（`67,343 / 8,425 / 8,436`）**；查明 `ROUTE-001` 需在加载时屏蔽事后 `difficulty_tier` 辅助题项并做 `"openrouter"`（679 题胜出）静态候选消融；原始 Parquet 逐条证实 `TRA-001 ∩ ENV-002` 的 13,336 个共享 ID（13,374 条 `repo+issue`）与 `ENV-001 ∩ ENV-002` 的 236 个 ID 100% 为同一任务，确立仓库级留出隔离规则 | **Stage 1 实验协议初稿完成**（证据归档于 `runs/MR-STAGE1-20261010/`） |
| 2026-10-10 | Stage 1 训练协议最后修订与版本归档（`MR-STAGE1-REV-20261010`） | 对账 `ROUTE-001` `"openrouter"` 元路由器更正方案 A（整题剔除 `8,126` 题，剩 `76,078` 题）与方案 B（从 `criteria` 移除 `"openrouter"` 并重算：`8,707` 题不变、`370` 题获新唯一静态胜者、`309` 题降级归入分析集），正式选用**方案 B 作为 Stage 1 纯静态主实验集，共 `83,895` 题（`67,097 / 8,392 / 8,406`）**，原 `84,204` 题仅作混合候选参考对照；核实官方 `kev`/`laya` 加载器不支持按 `question_key` 过滤，在 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b/` 一次性生成物理移除 `difficulty_tier` 的派生纯静态 JSONL 并通过官方加载器校验（发现 Laya 须传 `--max-len 1024 --head-max-len 512` 以避免 37 候选题 `options_collapsed`）；将第一批训练收敛为 **1 次 Kev-4B 训练 + 1 次 Laya-421M 训练**，并完成零 GPU 规则基线（`val` 最高 `46.81%`） | **Stage 1 最终训练协议与纯静态主实验数据视图归档完成**（新增 `openrouter-remediation-audit.json` 与 `stage1-protocol-and-baselines.json`）；等待负责人批准后执行 `E2-STAGE1-BATCH1` |
| 2026-10-11 | Stage 1 许可、数据一致性、全量编码与八类变量联合覆盖最终只读验收（`MR-STAGE1-FINAL-AUDIT`） | 负责人批准决策 1（保留 Regime A+B+C 并分桶评估）、决策 2（仅做训练前只读 CPU 验收，不启动 GPU）、决策 3（修订文档脱敏后推送 GitHub）；逐源核实发现 `ROUTE-004`（`39,716` 题）为 `TRAIN_ALLOWED_VERIFIED`（HF 声明 `apache-2.0`），而 `ROUTE-002`（`35,102` 题，HF 缺 `license` 标记）与 `ROUTE-001`（`9,077` 题，GitHub `LICENSE` 404 且 HF 无数据卡）均为 `LICENSE_PENDING`；全量核查 `ROUTE-001` 548,059 行发现 `(benchmark_name, instance_index)` 在 `mmlupro`、`simpleqa`、`hle` 等跨子集中发生 `2,001` 题重复评测与 `1,165` 题不同 `prompt` 跨题碰撞（污染方案 B `563` 题跨题碰撞、`651` 题重复模型评测，并解释 `llmroute_hle_57` 实为 `gemini-2.5-pro` 双子集重复，未构成真实双模型并列）；完成 `83,895` 题 CPU-only 官方 Kev（`max_state=384`）与 Laya（`1024/512`）全量编码验证（`100%` 通过且交集 `100%`）；完成费用血统五级核查（实测账单 `0`）与八类动态路由变量联合覆盖矩阵（同时具备八类状态+`model×effort`+真实缓存+真实费用的记录为 **`0`**） | **判定 `STAGE1_DATA_READY = NOT_READY`、`RUNTIME_JOINT_DATA_READY = NOT_READY`**（完整审计证据归档于 `runs/MR-STAGE1-20261010/final-stage1-and-joint-coverage-audit.json`） |
| 2026-10-11 | `MR-STAGE1-FAST-FIX` 实验数据最小修复与快速迭代 | 负责人授权在唯一主链 `prepare_router_data.py`（`router_data/route.py` 与 `views.py`）执行最小 CPU 修复并重导出派生集：更正 P0 文档与审计 JSON 的行数、自有数据三表粒度、AgentSuite 配对数（`273` 题 / `1,365` 同权重对 / `273` 专用权重对 / `1,365` 跨版本对）及八类状态名称；用未截断原始 `(origin_query, prompt)` 的 `full_prompt_hash` 合并 `ROUTE-001` 跨子集同题导出为 `24,441` 道独立真题，去重 `21,144` 条完全一致的同模型重复评测（恢复 `llmroute_hle_57` 为 `gemini-2.5-pro` 唯一胜者 `UNIQUE_MAX_SCORE`），并将 `1,219` 道潜在胜者分数或费用冲突题（`439 + 22 + 758`）隔离至分析池，保留 `8,441` 道无冲突纯静态单胜者题（`6,788 / 812 / 841`）；对 `ROUTE-002` 候选按固定种子确定性打乱（`index 0` 胜出率降至 `9.20% / 9.00% / 9.51%`）；在 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/` 导出修复版纯静态三集合 **`83,259` 题（`66,566 / 8,343 / 8,350`）**，通过双遍 SHA256 100% 一致性校验及 Kev（`384/7552`）与 Laya（`1024/512`）100% 样本 CPU 编码核验 | **Stage 1 技术与代码阻塞 100% 解除（`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`）；许可证保持 `ROUTE-004` `TRAIN_ALLOWED_VERIFIED`、`ROUTE-002`/`ROUTE-001` `LICENSE_PENDING`；待负责人批准后启动 GPU 微调** |
| 2026-10-11 | `MR-ALLDATA-PREP-20261011` & `MR-ALLDATA-ADAPTER-20261011` 全量双模型训练数据最终适配 | 在唯一主链 `prepare_router_data.py --mode all_data`（`router_data/all_data.py`）中对齐 Stage 1 主 Choice（`83,259`）、`ROUTE-001` 新重算 Choice（剔除 `1,953` 条不合法单胜者后收敛为 `8,441` 条，与主 Choice `0` 差异）、Pairwise（`59,049` 对）与 Soft-Target/Score（`53,087` 题）的真实完整题目身份与统一 Train/Val/Test 语义划分（跨视图泄漏 `0`）；在 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `training/kev/` 分别生成 6 个训练子集（`stage1_choice` `83,259`、`stage1_pairwise` `59,049`、`stage1_soft_target` `53,087`、`stage2_agent_state` `88,087` 轨迹级、`stage3_effort` `290` 有效配对、`stage4_auxiliary` `1,622,547` 有效调用），完成每模型 `1,906,319` 条记录的 100% CPU-only 官方加载与编码核验，并锁定首轮训练超参数与命令 | **Laya-421M 与 Kev-4B 全阶段训练视图与首轮训练参数已 100% 就绪，按要求暂停等待 GPU 训练授权** |
| 2026-10-15 | Q-012 | 负责人批准 Checkpoint 双池留存策略（旧 5 核心永久保护 + 新合格候选 ~15% 动态择优）；采样区分 ALGN 消融受控比例与 F 系列全量连续流式覆盖；重构质检看板为极简图表架构 | 策略版本升级为 DUAL_POOL_RETENTION_V2；已在唯一主链落地并同步 |
| 2026-10-15 | Q-013 | 负责人明确授权 P14 连续训练恢复与整体研究推进：恢复现有 A6000 连续训练队列，推进 F04 及后续 24 组正式实验，在合适边界补跑正确采样协议的 F03，拒绝不必要的工程流程 | 全队列正式恢复执行；F04 已启动并验证首 Chunk 8,192 条全量无丢弃训练；旧 F03 归档至 F03_LEGACY_MINFACTOR 待边界补跑 |
| 2026-10-15 | Q-014 | 负责人明确要求推进 P15 连续研究推进与关键训练资产更正：保持 F04 GPU 训练健康运行，彻底解耦并安排正规 F03 补跑，修复课程模型父依赖强熔断核对（Fail-Closed）禁止回退基座，实事求是审计老核心 5 席物理实体（2 席在盘，3 席仅留元数据），精确对齐尾部 Chunk 步数，升级看板多跨度与全数据图表 | 已在唯一正式主链全面落地并同步远端与服务器；F04 稳定长跑，F03 排队就绪，资产如实记录 |
| 2026-10-15 | Q-015 | 负责人明确要求推进 P16 全局连续推进、历史运行协议审计、双池库存核查与课程父模型补跑就绪：保持 F04 原进程高速运行（Chunk 19/234，步数 2,432/59,904，Loss 0.5786~0.5917）；严谨核查历史 Run 真实已执行 Optimizer 步数（F01 15,174 步、F02 31,304 步、F03 旧版实际仅 1,456 步，S1 纯基准 7 组 144~994 步）；穿透核实 Checkpoint 双池实体留存（老核心 5 席中仅 2 席在盘、3 席留存元数据；新核心 15% 动态配额 2 席）；解决课程父模型依赖链（F17<-F01<-...）并在 Stage 5 课程依赖启动前排定 F01 物理断点正规补跑（Stage 5 Prio 0）；实证 Terminal-Bench 2.1 物理隔离与 0 泄漏 | 代码与调度已全面落地并同步远端与 A6000 服务器；F04 持续长跑，F03 紧随其后，F01 父模型补跑无缝编排，学术防线严密闭环 |
| 2026-10-15 | Q-016 | 负责人明确要求推进 P22 连续科研主线执行、真实父权重认定与控制器交接闭环：保持 F04 GPU 进程（PID 2881373，推进至 Epoch 1 Chunk 99/234，Loss 0.5048，811k 样本）零干扰长跑；纠正课程父模型认定逻辑，严禁因任意物理文件存在而篡改最佳 Epoch，严格依据历史验证指标确定科学最优（F01 最优为 Epoch 2），物理缺失判定为 NEEDS_REGENERATION 并在 F17 启动前正规再生；彻底梳理旧控制器 PID 2881128 与 GPU 子进程关系，确定在 F17 之前的非 GPU 计算空闲间隙完成单控制器无缝交接，严禁常驻 Watcher 与多队列并发；严格核查双池实体（老核心 2 席实盘、3 席元数据；新核心 0 席，F04 未完训不抢占）；实证 S1/S2 最好与最差对比 | 源码已全面修复、单元测试 100% 通过（新增 test_sync_run_best_symlink_scientific_integrity）、最新代码已同步 A6000 服务器；F04 持续健康长跑，调度接续方案已闭环 |
| 2026-10-16 | Q-017 | 负责人确认 RQ1 总体效果含 Model×Native Effort 及状态消融；RQ2 模型池；RQ3 任务拆分；RQ4 多 Agent 跨角色模型互补性；RQ5 工作负载适用边界。完成六份文档研究方案同步，未启动新训练 | 负责人最新明确指令；详细设计见汇报三 V8 |
| 2026-10-18 | Q-018 | 负责人明确要求推进 V8 长周期完整执行（服务器双模型 API + 本机高并发 Agent + 双栏实时看板）：Laya 与 Kev 权重 100% 留驻 A6000，Mac 本机 0 权重；今晚无付费 API，全流程使用 Mock/Oracle 进行零成本验证；A6000 部署 FastAPI 路由服务（端口 8000）并建立 Mac 本地 SSH 隧道，Laya (F05 epoch_01) 与 Kev 真实路由已通；V8 数据扩展完成 440 万 Agent 轨迹、3.9 万缓存复用、5.7 万模型选择三大物理视图落盘；Kev-4B 完成同源 LoRA 训练验证（optimizer_steps > 0）且与 F03 主训练完全互不干扰；Mac 端单 Agent 框架落地并通过 64 并发 Canary 压测（Pass@1 75%），双栏看板上线（http://127.0.0.1:8765）；等待明早 API Key 启动正式生成式评测 | 负责人最新长指令；代码与受保护账本全量闭环，文档同步归档 |
| 2026-10-18 | Q-019 | 负责人最终明确确认：**RQ4=系统消融**（Model×Native Effort、状态 T/M/H 组合、训练数据/监督），**删除旧 RQ4 角色互补性**；RQ1 只做总体对照，RQ2 模型池，RQ3 任务拆分；RQ5 适用边界维持不变 | 最新用户明确纠正，详细实验与空白图表见汇报三 V9；Q-017 为历史记录 |
| 2026-10-30 | Q-003/Q-021 | 用户明确从未设置 API 总 Token 或美元预算；按任务需要测试，资源规则/训练不中断/Final隔离保留。真实请求后端为托管 Qwen3.8-27B，映射费用按所选逻辑目标身份价格和真实用量核算，教师按配置身份计价，后端价格与 bill 另列 | 用户本轮明确决定；真实 Luna 官方 Episode 与映射实验分开，三原目录重算结果见 PROJECT_STATUS；raw 与终局保留 |



