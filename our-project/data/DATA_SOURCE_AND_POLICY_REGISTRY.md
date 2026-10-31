# ModelRouter · 数据源、模型能力与缓存政策统一台账

## 当前能力与数据来源（2026-11-01）

**新增真实监督**：3个SWE-smith Train任务尝试、2组完整可比终局，新任务级/步骤级偏好各1条，累计4条/2标签任务。新标签均为Device任务上的Luna low：完整终局等质量下较低模型费，以及真实同前缀的一步修复；类型不混用。Scope同仓库但不同任务ID/源码文件，双失败仅观察；SQLparse Luna请求中断不生成胜者。数据MIT、两个代码仓库BSD-3-Clause，Canary/Dev/Final与独立集的精确ID及可识别仓库元数据无交集，任意近重复不作全面结论。结果见[本轮记录](../results/iterations/20261101-v9-k2-supervision-expansion/review.md)。

新delta2已由原Prepare与共享serializer消费，完整过去消息、实际候选、low、AA v4及反馈来源保留；原382视图与13,214候选不重加工。可组合Train200/Val186仅增加4条真实偏好，仍同2任务；17份候选观察和6组无有效目标对照不混作choice。68请求/65份Usage/3缺失，已知模型费率0.67589603USD，完整费用、实收及资源未知；教师0。两个既有账户目录仍无Flash，不重发已知失败POST；K=3、同模型Effort监督0。旧四档标签与训练目标语义差异、400字符输入限制只作分析，不用独立标签再训。

**独立评价材料（11-01完成）**：本轮复用已有ROUTE-003 TwinRouterBench `test_twinrouterbench_holdout.jsonl`（520任务/970步），原 `EVAL_BENCHMARK_ONLY` 用途不变，没有下载、清洗或加入Train/Val。两组数据任务/state/instruction/criteria/gold逐条相同，8/8版本完整评价、7760条预测。只评分旧四档choice，不将每行score问题另算970个样本，不生成Sol/Luna/Flash最优Model×Effort目标；分数与原始概率见[独立评分](../results/iterations/20261031-twinrouterbench-independent/review.md)。既有合法K=2 Train动作目标仍2条（1任务），K=3最优仍0；新训练未启动。

**10-31 历史真实监督**：从ad1d392接续，已有TRA-002对应的SWE-smith公开训练任务TextFSM取得1组有效K=2完整Episode与2个同历史步骤前缀对照，25次Sol/Luna low生成均身份匹配，无Alias。两Episode原96项通过，形成任务级Luna成本偏好1条；前缀7 Sol一步通过、Luna使用镜像不存在的apply_patch，形成步骤级即时修复偏好1条。前缀6两失败和6个候选结果只作观察；完整K=3最优/同模型Effort差异标签仍0。原Dev失败、教师前缀及旧成功题没有重跑，结果见[真实监督记录](../results/iterations/20261031-v9-real-route-supervision/review.md)。

| 新材料 | 本地与服务器原目录中的对象 | 监督、身份及用途 |
|---|---|---|
| 公开训练任务 | `results/iterations/20261031-v9-real-route-supervision/task_source.json`及原官方镜像 | SWE-bench/SWE-smith train，已有TRA-002任务ID；数据MIT、TextFSM代码Apache-2.0；与Canary8/Dev24/Final57精确ID及可识别TextFSM元数据交集0，任意近重复未作完整结论 |
| 两条真实动作偏好 | 同迭代`supervision.jsonl`与`training_delta/model_comparison/train.jsonl` | TASK_LEVEL_PREFERENCE=1、STEP_LEVEL_PREFERENCE=1；仅Sol low/Luna low，旧S1和旧池Oracle身份不变 |
| 六个已观察候选结果 | 同迭代`observed_outcomes.jsonl` | OBSERVED_OUTCOME_ONLY；两Episode可信终局与四个一步反馈分开，一步后结果不当完整Episode |
| AA与教师状态 | 两条新状态固定AA v4、teacher=null | AUXILIARY_FEATURE_ONLY；能力数据/摘要不生成动作标签，本轮教师0调用 |

原Prepare和Trainer共享序列化已实际读取2条新目标，问题ID/instruction分别对应任务与一步目标；未来候选反馈只进入监督，不进入决策前状态。原390实体、四教师及有效382视图未重加工，复用Train196/Val186，加new delta2可组合198/186；两条同属1个任务，旧13,214不算全量新增。尚未再训练。

本轮25次真实生成input385,895/output14,866（已含reasoning）Token，模型费0.26274516USD，教师0；缓存读1次缺报、写缓存14次缺报保持null。使用请求型号的原Registry费率，供应商实收和资源费用未知，详见同迭代summary/request_model_rates。Flash本次两账户/models均200但未列出，旧404/503 model_not_found证据保留，没有重复相同失败POST或借用27B身份。

**既有教师与请求费用**：紧凑真实Sol step3前缀三字段成功，1462输入/1528输出含1435 reasoning、0.0189335USD，只属TEACHER_PREFIX_ONLY，未执行新Router或工具，不纳入Train，本轮未重跑。原real-model-comparison的65响应已知费用1.43331375USD及3条混型号/4次无Usage缺失保留；旧OpenRouter估价与raw Usage不覆盖。该小计不包含本轮新25请求，未知实收不填0；详细历史仍在原实验及PROJECT_STATUS。

[当前 AA v4 快照](../code/data/v9/capabilities/snapshots/20261031T072548885180Z-v4.json) 为 `20261031T072548885180Z-v4`，2026-10-31 台北15:25:48由原刷新入口取得；本轮未再运行刷新。新真实模型实验与382行视图均绑定v4，旧Alias Trial/前缀仍v3、旧390与已完成训练仍v1，不追写旧结果。Sol AA slug为gpt-6-1-sol，Sol/Luna Max各10项共20项，三份厂商资料保留；本轮low、none、托管Flash及Coding/Agentic综合指数仍NOT_MEASURED，AA Key缺失，不借用Flash-Next/27B成绩。Sol文档档位low/medium/high/xhigh/max，不含none；Luna文档none/low/medium/high/xhigh/max，本轮只实调low；Flash参数省略不证明none原生支持。

下表保留 AA 原分，不把未披露单位的值转换为百分比；完整精度、指标版本和来源见 v4 JSON。两列均为 **Max**，不用于 none 的动作成绩，也不生成最优选择标签。

| 指标 | Sol Max 原分 | Luna Max 原分 |
| --- | ---: | ---: |
| Intelligence Index v5.0 | 54.5087338138148 | 27.7552004938153 |
| AA-Briefcase v1.1（ELO） | 1555.26 | 1336.99 |
| AutomationBench-AA | 0.6486844882398171 | 0.5316814034483175 |
| Terminal-Bench 4.0 | 0.560606060606061 | 0.126262626262626 |
| FrontierCode 2.0 | 0.406262878787879 | 0.251747727272727 |
| AA-Omniscience v1.1 | 42.03333333333333 | -8.266666666666667 |
| GDP.pdf | 0.31 | 0.228 |
| HLE-Diamond | 0.588 | 0.222 |
| CritPt v2 Hard | 0.685 | 0.415 |
| Terminal-Bench-Science 0.1 | 0.580952380952381 | 0.0857142857142857 |

**20:05历史运行资产**：原 `results/iterations/20261030-v9-official-luna/` 保存9次真实生成、18次工具、3条成功Luna教师及12个不同响应ID；总用量138,385Token、旧配置价估算0.182588USD（UNVERIFIED_CONFIG，保留历史），实际账单及完整费用未知。任务为既有canary `fix-git`，Verifier未执行，终局标签未知；这些轨迹只用于开发执行证据，不加入原198Train/192Val，不制造模型/Effort最优标签。三条新在线教师与旧训练中的四条教师分别登记，未重生成旧材料。Run保存能力快照 `20261030T041319933533Z-v2`；双动作none/low前向使用同快照，AA Max参考不转成动作分数。Oracle CTRF 2/2通过与真实模型结果分开，详细路径和运行限制见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 当前入口。

[10-30 历史v2快照](../code/data/v9/capabilities/snapshots/20261030T041319933533Z-v2.json) 已真实落盘，Snapshot ID `20261030T041319933533Z-v2`；合法公开GET而非授权Data API，AA Key缺失。LunaMax Intelligence Index27.7552004938153/INDEX/AA5.0及9项Max原分可读，部分指标单位未披露仍NOT_REPORTED；Sol与托管Flash精确AA记录NOT_MEASURED。厂商三者的价格/上下文/Effort资料可作能力参考，不能证明项目调用可用性或最优动作标签；已读官方价格可结合真实用量核算 API USD，供应商 bill 另列。旧52/38/Flash-Next40的不同版本/变体参考不混入本快照。

训练唯一实体390行（198/192）及4条教师仍绑定v1，未重生成；S1旧偏好64+64、S2观察动作/结果70+64、S3运行辅助64+64分别可用于既有目标，三模型真实choice/Effort监督0。RouterBench和LLMRouterBench原许可待核资产不新增入训练或公开；公开TRA-001参考摘要按CC-BY-4.0保留来源、许可和修改说明，私人轨迹、prepared和本地路径不提交。当前Laya只保留关键三候选摘要，完整能力卡尚超预算；不把字段消费当学习收益。详细实测与历史数量见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)，以下原训练及旧AA0按时点阅读。

**当前官方开发资产**：`our-project/results/iterations/20261030-v9-official-luna-complete/` 已取得 reward=1.0、官方 `verifier/ctrf.json` tests2/passed2/failed0；单 Luna none/low，14 次真实路由、0 fallback。模型用量合计218,578Token，生成165,028、教师53,550；详细 Job/Trial、执行统计与 runtime 只在 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 当前入口维护。旧失败目录、旧配置金额和旧训练材料保留；本次单模型双动作开发证据不当作独立三模型能力、全动作最优监督或五 RQ 总体结果。

**实际供应商可用性**：当前以真实POST而非旧列表为准：Sol在现有账户Responses可调用，项目jiji的Luna Chat Completions可调用；另一个账户Luna有3次旧型号返回，不作纯型号Episode。Flash项目账户404、另一账户503正文均明确无可用型号/渠道；无Usage，金额未知，不重试或改生产渠道。公开能力/价格页不证明具体账户访问；实际返回身份而非物理权重读取构成本轮身份依据。

## V9 下一阶段数据筛选（2026-10-31）

本节沿用Open-SWE-Traces、SWE-smith-trajectories、RouterBench与原S1/S2/S3；没有重下载或全量重清洗。读取现有54个Open-SWE终局并复用原Prepare形成唯一新training_view，原390及其划分不动；8个原resolved=-1保留未知，不作为失败目标。新真实对照来自external_dev，不能为增加Train标签而更换其划分。

### 当前能提供多少监督

**当前可训练的真实K=2 Model×NativeEffort偏好为2条（任务级1、步骤级1），完整三身份池最优标签仍0，同模型不同Effort偏好仍0。** 两条来自本轮允许训练的TextFSM任务，不来自旧extract-elf Dev。旧extract-elf、COBOL单生成、来源执行模型、教师短评、AA卡及Alias成功仍不增加选择目标；下面382行和全源表只描述既有材料，不包含本轮新delta2。

原prepared实体仍为Train198/Val192。原54个Open-SWE终局中Train2/Val6原值-1，旧终局却为false；新视图将8条作为UNKNOWN_OUTCOME排除于终局目标，原历史不覆盖。新训练视图实际为 **Train196/Val186，共382行**：

| 原目标 | Train 可核标签 | Val 可核标签 | 说明 |
| --- | ---: | ---: | --- |
| S1 旧模型人类偏好 | 64 | 64 | 原 Arena 候选身份，当前三身份匹配 0 |
| S2 已观察动作/轨迹终局 | 68 | 58 | Train 为 27 个动作标签、41 个已知终局；Val 为 58 个已知终局 |
| S3 日志用量/前缀机会 | 64 | 64 | 原调用及负载辅助目标，与模型最优选择分开 |
| 合计 | **196** | **186** | 新视图的既有目标条数，不代表新增独立任务或新三模型选择标签 |

原文件仍为 `our-project/code/data/v9/prepared/{model_comparison,agent_auxiliary,system_auxiliary}/{train,val}.jsonl`，AA v1、4条旧教师与6个前缀不变。新唯一视图为 `our-project/results/iterations/20261031-v9-real-model-comparison/training_view/`，绑定AA v4，保留旧S1候选顺序/人类偏好；辅助候选仅已实调的Sol/Luna low。原sources/tra.py的int(value)==1曾把-1写为false，上一轮已将-1保留为None；本轮Prepare只将该类目标标UNKNOWN_OUTCOME。未覆写原始历史、未训练或给未知终局补答案。

### 已存在位置、数量与许可

下列路径相对于现有仓库根目录；远程根位置见原 `manifests/server_assets.json` 的 `base_workspace`。全量公开源在服务器，本机已有相应 `公开数据/数据预览/<来源目录>/` 的统计及预览。两端 `our-project/data/raw/`、`our-project/data/processed/` 均为空，远程 `our-project/data/training_views/` 也为空，不将空目录记成新资产。

| 来源 | 服务器实际文件/目录 | 实际数量与原 Train 候选引用 | 本地材料与原许可 |
| --- | --- | --- | --- |
| TRA-001 Open-SWE-Traces | `data/公开数据/原始数据/TRA-001_Open-SWE-Traces/`；`data/公开数据/清洗数据/Agent轨迹/TRA-001_Open-SWE-Traces/cleaned_trajectories.jsonl` | 12 个 Parquet，30,000 个不同轨迹 ID、21,515 个任务；2,075,629 步；原 Train 引用 1,673,528 | 本地预览与旧 prepared；原登记 CC-BY-4.0，manifest 另声明 CC-BY-4.0/Apache-2.0。沿用原来源用途与署名要求，具体版本的许可差异未新增确认 |
| TRA-002 SWE-smith-trajectories | `data/公开数据/原始数据/TRA-002_SWE-smith/`；`data/公开数据/清洗数据/Agent轨迹/TRA-002_SWE-smith/cleaned_trajectories.jsonl` | ticks/tool/xml 共 24 个 Parquet，76,002 原始行、49,897 个不同轨迹 ID、13,501 个任务；2,331,584 步；原 Train 引用 1,864,427 | 本地预览与旧 prepared；原 MIT 用途保留 |
| ROUTE-002 RouterBench | `data/公开数据/原始数据/ROUTE-002_RouterBench/` 下 0-shot、5-shot、raw 三个 pkl；`data/公开数据/清洗数据/路由比较/ROUTE-002_RouterBench/cleaned_routerbench.jsonl` | 0-shot 已处理 36,497 题；11 模型；35,189 个有解 Oracle，排除 87 个同分同估价后为 35,102 题，原 Train/Val/Test 为 28,012/3,588/3,502 | 本地统计与预览；**LICENSE_PENDING，当前可加入训练 0**。原 manifest 的 Apache-2.0、预览的 CC-BY-4.0 与此前数据许可未明记录不一致；代码 MIT 不证明数据许可。未读取 pkl 内容或混入 5-shot |
| 原 S1：ROUTE-004 Arena | `data/公开数据/清洗数据/路由比较/ROUTE-004_Arena/cleaned_arena_preference.jsonl` | 57,477 场，64 个旧模型；39,716 场明确偏好、17,761 场平局；原 Train 明确偏好 31,766 | 本地统计及原 S1；原已核 Apache-2.0，仅使用题面、两模型身份与人类胜负，沿用原不外发模型响应文本的范围 |
| 原 S3：CACHE-001 Mooncake | `data/公开数据/清洗数据/缓存与时间/CACHE-001_Mooncake/cleaned_mooncake_traces.jsonl` | 39,632 条，含 3,993 条 synthetic；原 Train 候选 28,714，不将 synthetic 记成真实请求 | 本地统计及原 S3；原 Apache-2.0；只能作前缀复用机会与输出长度辅助 |
| 原 S3：TIME-001 BurstGPT | `data/公开数据/清洗数据/缓存与时间/TIME-001_BurstGPT/cleaned_burstgpt.jsonl` | 原统计 1,404,294 次请求；原 Train 候选 1,122,577 | 本地统计及原 S3；原 manifest 声明 Apache-2.0，预览仅写 Open Source，具体数据许可版本未新增确认；沿用既有调用长度/到达辅助用途 |
| 原 S3：OWN-002 Blog | `our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv`，本机与服务器均存在 | 本轮实读 221,128 行；原正向用量候选 178,621，原 Train 候选 142,888 | 原脱敏内部研究资产；不发布私人日志，不把 quotaUnits 换成 USD |

原六源 Train 引用总数仍为 **4,863,900**：S1 31,766、S2 3,537,955、S3 1,294,179。这是来源候选引用量，不能作为独立任务数、当前三模型动作监督数或本轮新增材料量。数量沿用 `runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1/{train_candidate_summary,quality_summary}.json`；实际分级引用在同目录 `by_source/<SourceID>.jsonl.gz`。

### 原模型、结果与动作空间匹配

| 来源 | 原模型/任务 | 可信结果与模型、档位字段 | 当前三模型身份匹配 / Model×NativeEffort 匹配 |
| --- | --- | --- | --- |
| Open-SWE | Qwen3.6-27B 10,000；Qwen3.8-27B、DeepSeek-V4-Flash-0731、MiniMax-M2.5、Qwen3.5-122B-A10B 各 5,000；GitHub issue 修复，含 Scale-SWE/SWE-rebench | 原始 `resolved=1` 11,488、`0` 14,581、`-1` 3,931；只将 0/1 作已知轨迹终局。`metadata.teacher_model` 记录执行配置：`(enable_thinking=false, reasoning_effort=null)` 15,000，`(true,xhigh)` 5,000，`(true,max)` 5,000，`(true,null)` 5,000。null 不转成 none，模式名不证明当前 Provider 的有效档位 | **0 / 0**；Qwen3.8-27B 不改名为托管 Flash 或 Sol/Luna；观察配置没有最优选择标签 |
| SWE-smith | claude-3-7-sonnet-20250219 54,629；claude-3-5-sonnet-20241022 19,736；gpt-4o-2024-08-06 1,637；合成代码修复任务 | 原始 `resolved` 全部为 bool：true 32,360、false 43,642；同轨迹 ID 的终局无冲突。原 `model` 有三种身份，旧预览仅写一种不代表全源。76,002 行均无 NativeEffort 字段；26,105 个重复轨迹行不能当新 Episode。已处理数据另有 823,082 个重复记录 ID；733,081 个 `INFERRED_COMMAND` 不当真实 Tool API 动作 | **0 / 0**；只保留原执行模型和观察终局 |
| RouterBench | WizardLM-13B、Claude Instant/v1/v2、GPT-3.5-1106、GPT-4-1106、CodeLlama-34B、Llama2-70B、Mistral-7B、Mixtral-8x7B、Yi-34B；86 类静态题 | `candidate_evaluations[model].score` 是已报告评分，`cost_usd` 为历史估价；Oracle 只在该 11 模型池内解释。1,308 题全败、87 题并列均不作唯一胜者。无 NativeEffort，无 Agent 终局/全任务费用 | **0 / 0**；35,102 个旧池比较标签不能迁成当前三身份最优标签 |
| 原 S1 Arena | 64 个旧型号的用户题面盲测偏好，含 GPT-3.5/4、Claude-1/2、Llama2、Vicuna 等 | `human_winner=model_a/model_b`；平局不作唯一偏好。候选模型与胜者身份是真实记录，NativeEffort 缺失；人类偏好不充当 Agent 成功 | **0 / 0** |
| 原 S3 Mooncake/BurstGPT | Mooncake 未报模型；BurstGPT 原统计 ChatGPT 1,189,167、GPT-4 215,127；请求负载 | 原长度、时间戳、历史前缀块及输出长度；不提供模型选择/NativeEffort 或任务终局。Mooncake 复用机会不作 Provider 缓存命中 | 无当前目标身份可匹配 / **0** |
| 原 S3 OWN-002 | 源日志规范化名以 gpt-5.6-luna 189,441、gpt-5.6-sol 14,771、gpt-5.6-terra 13,992 为主，其余 2,924 行为其他旧名；调用级资产 | 日志报告输入/输出/缓存读数与 quotaUnits。Effort 字段 198,359 行有值、22,769 行未指明，物理后端与档位实际效果未报；没有 task_id/episode_id/resolved | 本轮实读精确匹配 **0 / 0**；日志动作不是最优路由监督 |

Open-SWE 的未知终局关联 **340,279 步**，其中原 Train **272,119**、Val **36,614**、Test **31,546**。原 Train 中与原始 0/1 终局相连的步为 **1,401,409**；这些步仍共享轨迹终局，不代表同样多的独立结果。本轮对分级引用与原始轨迹 ID 求得，Train 中原始终局已知的轨迹 ID 为 **20,981**（成功 9,254、失败 11,727），另 3,142 个轨迹 ID 为 `-1`。这组按原始终局统计的数量与旧摘要的失败单位口径不同，旧摘要不覆盖为新值；未完成全部目标单位口径的重新归并。

### 与旧材料及 Train/Dev/Final 的任务交集

当前项目的训练材料是上述离线 Train198/Val192；Terminal-Bench 原清单为 **Canary8 / external_dev24 / final_test57**，Canary 也不是可微调的 Train。这里只读任务 ID，没有读取 Final 题面、答案或执行结果。

| 来源 | 旧390中的 Train/Val 行 | 与 Canary8 / Dev24 / Final57 的精确任务ID交集 |
| --- | --- | --- |
| Open-SWE | 39/32；源任务分别 22/32 个；扣未知终局后可核行 37/26 | **0 / 0 / 0**，已对全部原始 instance_id 求交 |
| SWE-smith | 31/32；源任务分别 27/32 个；原始终局与现成 S2 标签对应一致 | **0 / 0 / 0**，已对全部原始 instance_id 求交 |
| RouterBench | 0/0，不在现有六源入口中 | **0 / 0 / 0**，已对全部 sample_id 求交 |
| 原 S1 Arena | 64/64，偏好对决单位 | **0 / 0 / 0**，已对全部 battle_id 求交 |
| 原 S3 Mooncake / BurstGPT / OWN-002 | 分别 21/22、10/10、33/32 | 缺少可跨来源连接的 Agent task_id，**无法计算**，不填写 0 |

上述 0 只表示标识严格相等时无交集，不证明题面、代码、近重复 issue 或派生数据完全独立。相关语义/仓库交集本轮未重新扫描；已有 SWE 与 ENV 的交集记录仍保留。多个轨迹、格式、前缀和同一任务的多次 Alias 执行不另计成独立任务。

旧 S2 prepared 的 Train/Val `independent_unit_id` 与 `trajectory_id` 交集均为 0，但多数 prepared `task_id` 没有值，不能据此声称真实题目无交集。上表对 Benchmark 的任务交集使用原始 `instance_id`，不从空 `task_id` 推导 0；后续候选仍需保留原任务身份与单位区分。

### 下一轮候选清单与未确定项

优先复用已经存在的 `runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1/batch_preparation/batch1/train/{S1,S2,S3}.jsonl`，不另建加工入口：

| 用途 | 可核候选标签数 | 现成文件与限制 |
| --- | ---: | --- |
| 旧模型偏好 S1 | **4,592** | 原 S1 人类偏好，可作旧池表示学习，当前三身份匹配 0 |
| 观察性终局 S2 | **2,622** | 原 2,846 行中 Open-SWE 1,768 行含 224 条 `-1`；可核 Open-SWE 1,544、SWE-smith 1,078，后者全部对应原始 bool 终局。当前步工具是否成功与轨迹最终结果分开 |
| 请求/前缀辅助 S3 | **6,000** | 原独立用途与单位保留，不与 S2 横向拼成同一任务的缓存或费用 |
| 原监督候选合计 | **13,214** | 原文件仍有 **13,438** 行，224 条未知终局未被删除；未生成 13,214 行的新文件 |
| 当前三身份最优 Model / Model×NativeEffort | **0 / 0** | 本轮没有提供同状态、独立真实模型动作的可比成功与费用记录 |

这 13,214 个候选标签与旧390、原分级引用存在重合，不能相加成为新增样本；用途仅为已有偏好/辅助目标，不建议据此重复声称训练了当前三身份联合最优动作。原 prepare 只接受原六源和原 S1/S2/S3 目标，RouterBench 不在该入口支持范围，本分支未改变它。

**仍未确定**：RouterBench 数据许可；Open-SWE/BurstGPT 当前数据版本的许可表述差异；原模型的不可变服务版本与原生档位有效性；全部重复记录/目标单位口径；近重复题面与代码交集；当前三身份的可比动作结果。原转换函数已调整，旧390的8个错误终局及原小批次224个未知终局仍在旧实体中，候选计数已排除，不重写历史。详细执行状态见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)。

## 当前托管 API 身份与计费政策（2026-10-30）

用户明确映射实验真实请求后端为托管 Qwen3.8-27B，非自部署。历史网关返回 `Qwen3.8-27B` 与非流式返回 `self-dploy/Qwen3.8-27B` 作为请求/返回身份保存。实验费用按 Router 所选逻辑目标 `ModelSpec` 的价格乘真实 input/output/cache 用量；教师按配置教师目标身份计价。`cost_model_id`、`cost_basis` 和顶层 `model_id` 记录所选身份，`returned_model_id` 保留真实返回身份；后端价格和供应商实收另列，缺失不影响映射实验。映射结果不作为独立物理模型质量对照。

**10-31 映射价格记录**：单位为 USD/百万 Token，生成按逻辑选择身份、教师按逻辑教师身份核算；真实后端不替换计价身份。

| 逻辑目标 | 输入 | 输出 | 缓存读 | 缓存写 | 已保存来源 |
| --- | ---: | ---: | ---: | ---: | --- |
| `gpt-6.1-sol` | 2 | 10 | 0.1 | 2.5 | 原 v2/v3 厂商公开资料 |
| `gpt-6-luna` | 0.10 | 0.50 | 0.01 | 0.125 | 原官方标准价，缓存写为30分钟 |
| `qwen3.8-flash` | 0.15 | 0.47 | 0.016 | `null`（缺测） | 原 snapshot `20261018` OpenRouter USD参考；阿里公开资料为CNY，不换汇 |

本轮流式教师输出合并 visible 与单列 reasoning 一次；旧非流式教师的 completion 已含 reasoning 时不再相加。真实缓存用量照实保存，缺失缓存字段仍为 `null`；JSON解析失败但已报告usage的请求照算费用，不记成功教师。供应商 raw.cost 未报currency时，实收仍 `null`；Router/工具/容器资源费用未知，不代填0，API无累计Token或美元上限。

主 Agent 已实际读取 [官方 Luna 模型页](https://developers.openai.com/api/docs/models/gpt-6-luna) 相应标准价格行；单位均为 USD/百万 Token：

| 实际计价项 | 官方标准单价 | 核算口径 |
| --- | ---: | --- |
| 非缓存输入 | 0.10 | 输入总量减去已报告缓存读和缓存写 |
| 输出 | 0.50 | output/completion 已含 reasoning，不另加 reasoning |
| 缓存命中输入 | 0.01 | 只按该调用实际报告的缓存命中数 |
| 30分钟缓存写入 | 0.125 | 只按该调用实际报告的写入数；[官方价格页](https://developers.openai.com/api/docs/pricing?latest-pricing-expanded=true) |

缓存字段已报告时，Luna 标准价核算为 `USD=((input_tokens-cache_read_tokens-cache_write_tokens)×0.10 + output_tokens×0.50 + cache_read_tokens×0.01 + cache_write_tokens×0.125)/1,000,000`。适用 Standard、单请求输入不超过272K、30分钟缓存写；本轮未配置Fast/Batch/Flex。同一调用只计一次，已包含在 output/completion 中的 reasoning 不再相加；在线教师并入该 Episode，离线教师制作费用单列到数据/训练，结果复用不算物理缓存命中。失败调用已报告用量照实计费，缺失输入/输出用量或官方价格保留 UNKNOWN，不填零。缓存字段缺测保持 null，核算时对应输入按普通输入价计，不把 null 改成零缓存命中；write 未报告仍保留 null。

**实际计价小请求（不并入官方 Episode）**：主 Agent 回报原费用接口的一次真实请求，input=4,389、completion=5、cached=4,224、cache write=null；price_source 为官方 Luna 模型页。按上述标准价得到 API USD=0.00006124，供应商 bill 仍 UNKNOWN；未报告的 write 保持 null，不填零。本样本验证该次实际输入/输出/缓存命中的核算，不能替代官方 Episode 的最终总费用或部署运行验证。

公开价核算无需另取账单许可。按实测用量与官方价得到的 API USD、旧 `UNVERIFIED_CONFIG` 金额和供应商 `bill=UNKNOWN` 分列；账单未知不影响执行。费用分支已在原计价器复用30个原请求完成并保存核算，本分支不修改结果文件；真实单探针0.00006124USD单列、不计入任一Episode。用户从未设置 API 总 Token 或美元预算，旧累计额度、旧余额与待额度许可只留历史；保留服务器资源规则、训练不中断和 Final 隔离。

### 已保存的官方价模型费用

| 原迭代 | 模型 Token | 生成 USD | 教师 USD | 模型合计 USD |
| --- | ---: | ---: | ---: | ---: |
| `20261030-v9-official-luna` 旧未评分轮 | 138,385 | 0.00450286 | 0.00381204 | 0.00831490 |
| `20261030-v9-official-luna-complete` 官方成功开发轮 | 218,578 | 0.00764224 | 0.00484108 | 0.01248332 |

以上使用实际用量与官方 Luna 标准价，缺缓存字段保留 null、按普通输入价计；输出含 reasoning，不重复计费。主 Agent已用Decimal逐项复核两轮30个原请求、原用量及旧配置金额，保存值一致；原事件追加 `OFFICIAL_RATE_RECONCILIATION`，未为重算再次发请求。旧配置总额0.182588USD保留为历史 UNVERIFIED_CONFIG，不改写成实付账单；供应商bill与Router/工具/容器等资源费用仍分别未知。探针不并入Episode，也不因此改动其Token统计。映射实验三原目录的 `mapped_cost_accounting` 已另行重算并追加事件，旧 raw、原始计数及终局保留；金额与缺失 usage 的处理见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 映射费用段。原服务状态与 Kev 长前缀超时、82.28秒CPU时延另记，详见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)。

映射重算的三原目录合计 21 条生成 raw，按 `prompt + completion + reasoning` 计价；6 条成功或已报告 usage 的教师按 `prompt + completion` 计价，另 5 条教师 usage 缺失。compact 第 3 条教师可能 JSON 解析失败，但已报告 usage 时仍计费一次，不记为成功教师。Flash `0.15/0.47/0.016` 采用原 snapshot `20261018` 的 OpenRouter 公开 USD 参考；阿里官方 v2 只有 CNY，USD 未确认，不换汇。

本轮真实Provider映射探针已通过：实验/计价身份Sol，实际返回 `self-dploy/Qwen3.8-27B`，55输入/16输出按Sol价格计 `0.00027000 USD`，日志顶层和费用字段一致。探针单列，供应商实收未知，不增加Episode成绩。

### 10-31 最终映射用量与费用

| 记录范围 | 真实输入/输出 Token | 映射费用 USD | 费用与结果范围 |
| --- | --- | ---: | --- |
| 首次官方 Trial 的13次生成 | `99,196 / 14,986`，缓存读 `79,040` | 0.01029900 | 生成合计114,182Token；原超时教师缺usage，完整模型费用 `null` |
| 事后 step3 前缀教师补充 | `9,396 / 608`（visible372+reasoning236），缓存0 | 0.024872 | 不并入首次 Episode；raw.cost0.00037142无currency，实收 `null` |
| 续跑第1次教师，JSONDecodeError | `8,736 / 2,048`（含reasoning1024），缓存0 | 0.037952 | 失败但usage已知，计费一次 |
| 续跑第2次教师，JSONDecodeError | `8,625 / 2,048`（含reasoning1024），缓存0 | 0.037730 | 失败但usage已知，计费一次 |
| 续跑第3次教师，成功 | `8,574 / 564`（含reasoning216），缓存0 | 0.022788 | 同Trial真实消费7次，仍只计1次成功请求 |

续跑最终15次生成：input122667/output22808（含reasoning9591）/cache109568，费用0.01380958USD；3次教师：input25935/output4660（含reasoning2264）/cache0，费用0.09847000USD，含两次JSON失败费用。该Trial合计input148602/output27468/176070Token、完整映射模型费0.11227958USD，与18条真实请求Decimal复算及AgentContext一致；reasoning不重复相加，18请求无usage未知。供应商raw.cost合计0.0033656476无currency，实收USD与资源费用仍未知，不代填0。

整个迭代2Trials均官方reward=1.0、CTRF2/2，最终已知小计0.12257858USD；首次超时教师缺usage，完整模型总额保持null，不能用生成小计代替。事后前缀补充0.024872USD独列。三原本地Alias复算的0.18180000USD已知小计（3教师缺usage）、0.000660788USD完整、0.070209774USD已知小计（2教师缺usage）及旧raw继续保留，详细记录见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)。

## 历史训练与材料记录（截至10-30 10:40）

> **10-30 10:40 最新训练证据**：Laya `V9_LAYA_001` 已完成两轮和每轮 5,692 条原固定 Val，198 条 Train 全部消费，完整/部分 state 为 192/6，两轮输入 396 次、完整/部分 384/12；4 教师记录共 8 次输入，核心字段保留，198 张缺测能力卡共 396 次输入保留。材料仍为唯一 390 行、Train198/Val192，没有新增或复制材料；AA 实测和三个新身份的选择/Effort 目标仍 0。Laya 总体及 S2/S3 改善、S1 四项退步；Kev 两轮/Val 完成但四项退步。新实体未上线，局部特征训练不能充当完整联合监督。F14 第 63 块原 8,192 个目标向量数值有限，不能据此确认外部语义或首次异常诱因。详细指标与实体留存见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 首页；以下旧时点材料/未启动记录保留历史。

> **2026-10-30 文档接续；10-29材料与历史实测按回报时点保留。** V2.1六源候选`4,863,900`、旧待核`5,027,245`、公开`6,600,628`及OWN不变。唯一实体390行、Train198/Val192；6真实前缀在单一S2，与固定参考不重合，choice/Effort目标和AA实测仍0，4教师字段PARTIAL。final与训练prefix分词已测：Laya1024保留4教师核心、完整state裁6条，8192推荐尚未启用，原step5近期工具真实末128字符已验证，长history仍裁，本次未重测全部Train或Val。invoice成功、duration两次失败和训练三次FAILED独立保留。02:11资源等待仅为历史；第3次worker44839因已有目录7.528秒exit2，02:55候选FAILED/training_status=FAILED、CLI25201自然退出为第三次历史；第四次worker50518于2026-10-30 03:25:31完成2 Epoch/100 steps、自然退出0，模型已保存于A6000；原dispatcher50514同秒自动开始固定Val attempt1；2026-10-30 04:23:20台北完整结束，控制器自然退出0，`status/training_status=COMPLETED`、`evaluation_status=EVALUATED`。新候选为`FEATURE_PARTIALLY_TRAINED`（4条稀疏教师、三新身份监督目标仍0），原Serving仍旧权重/`FEATURE_NOT_TRAINED`，未传Mac或上线Serving。第四次198记录/396完整passes与4教师8passes真实曝光单列，前三次失败UNKNOWN不覆盖。27184无worker已由主Agent结束，服务器`CLI_WAIT/EXIT_RESET=true`。Loader198接纳/396预期与失败后完整曝光UNKNOWN分开；F14/ComfyUI未被干预；F14运行推进、损失持续非有限，有效优化更新未确认，具体诱因未知，新Kev候选已完训并保存实体，原Serving尚未上线该权重，预算575783/256135/168082及135calls未变，usage/USD仍null；主Agent本次Router1/生成0，文档子任务未发请求。 原固定Val已完整EVALUATED，四指标对C03均退步；内部score92.38703579133796、V9组仅1条rank1，apply=False保留且删除/释放0，不作优于C03或训练有效结论。
>
> **原 Harbor 参数接入**：V9 配置和三候选已沿原 CLI/Agent 参数传递，真实上游解析与实例构造通过，未增加材料、AA 数值、任务结果或 API 用量；正式 Trial 仍未运行。
>
> **唯一职责**：此文件是公开数据源、数据许可、八组状态覆盖、模型/Provider 能力、缓存/定价政策及未来“候选 → 选择 → 数据加工 → 验收”信息的**唯一详细台账**。它不是新的执行流水线或运行时政策数据库。
>
> **权威性分工**：用户批准/否决、Q-ID 与日期唯一记录在 [EXPERIMENT_QA.md](../planning/EXPERIMENT_QA.md)；阶段/授权/唯一当前任务由 [PROJECT_STATUS.md](../planning/PROJECT_STATUS.md) 决定；研究方法在 [RESEARCH_OVERVIEW.md](../planning/RESEARCH_OVERVIEW.md)。此台账只记录具体资产及其**证据和准备状态**，不得将 Planning 优先级当作用户批准。
>
> **禁止误读**：登记 ≠ 已下载；官网有目录 ≠ 已核每个型号；公开许可证 ≠ 商业 API 输出自动可训练；可复用前缀 ≠ 生产缓存命中；task benchmark ≠ agent trajectory；API 调用成功 ≠ task resolved；跨模型同题评估 ≠ 相同中途状态的反事实。
>
> **原分级范围与现行复用**：既有处理来自 `data/公开数据/清洗数据/` 与 OWN 三源。公开总数 `6,600,628`，OWN 分别 `110 / 221,128 / 79` 行，不并入公开数；质量、许可和真实标签分别记录。ROUTE-001/002 的 `584,556` 行许可待核、真实运行时路由决策标签 `0` 保留为原记录。本轮优先复用 V2.1/L1，不重复建立分级或数据目录。

> **原执行汇报约定（2026-10-10，历史保留）**：当时顺序为整体进度、当前阶段小步骤、下一步计划、可复制执行提示词和通俗说明，全文及原新对话提示词见 [PLANNING_MEMORY.md 第 10 节](../planning/PLANNING_MEMORY.md#10-新会话恢复协议长期生效)。现行交付按用户当前要求；本台账保存数据源、模型和计费政策，详细执行阶段由 PROJECT_STATUS 首页维护。

## 0. 维护说明与证据等级

每一行都应长期保留 ID，允许**更新状态，不复制第二份目录**。所有动态政策必须附来源地址、查询日期、模型修订、地域/Endpoint 和有效期；政策变化追加变更记录。数据及政策必须分开维护，但共同由本文件提供导航。

- **S0·候选**：仅找到名称、网页或论文；尚未核正式文件、许可证或字段。
- **S1·来源已定位**：打开官方仓库/数据卡，能确认出处与大致字段；原始数据还未读。
- **S2·许可证待核 / 可训练 / 仅分析 / 禁训**：明确用途合法性；无证据一律“待核”且不得用于正式训练。
- **S3·字段已审**：后续获批后核对原始样本、时间戳、task/episode 键、模型/effort、真实 usage、成功标签及缺失率。未审绝不能填“覆盖全部”。
- **S4·待负责人选择 / 已选择 / 已排除**：由 Q&A 记录负责人的批准日期和用途；Planning 推荐不构成“已选择”。
- **S5·已加工 / 已验收**：只有真实数据完成规范化、去重、分割、标签核验和数据 lineage 后才可标记；需要 Execution 的事实证据。

**真实性标签**：MEASURED（Provider/Engine 真正回报）；OBSERVED_REUSE（请求前缀块相同的可复用证据）；SIMULATED（给定明确缓存模型的重放结果）；ESTIMATED（根据文本/统计推算）；UNKNOWN（无可信证据）。严禁互相冒充。记录来源版本是数据资产层的要求，**模型提供商的政策仍需按实际请求时间生效**。

### 0.1 V2.1/L1 复用与 Q/S/L、监督粒度（2026-10-29）

Q（记录质量）、S（监督类型）、L（覆盖层级）是三个独立维度；本节训练 S1–S4 与上方证据成熟度 S0–S5、§6.3 的处理步骤编号分开理解。下载讨论行 12530–12571、13877–13945 支持该分类及 V2.1 复用，最新需求不要求再做一套分层。

| 维度/类别 | 含义和实际单位 | 不能推出的结论 |
| --- | --- | --- |
| Q1–Q4 | 来源内质量：Q1 高质量记录，Q2 有效但较弱/间接，Q3 研究参考，Q4 冲突/异常或不可直接用 | Q1 不等于直接路由标签；内容质量与来源许可、Train 身份、真实监督分别判断 |
| S1 直接路由比较 | 同题真实模型偏好或可比质量，通常按 query/task、候选比较或偏好对记录 | 并列质量、历史费用选择和 AA 指数不能成为同状态最优 Model×Effort 标签 |
| S2 Agent 行为与结果 | 已执行动作、真实轨迹前缀、终局和确有证据的 Effort 对照；按 task/episode/decision 对齐 | `OBSERVED_ACTION` 只代表被执行动作；同一终局复制到多前缀不能增加独立 Episode 数或未执行动作真值 |
| S3 成本/运行辅助 | 缓存复用机会、Token、负载、请求费用；按请求、块或原聚合单位记录 | OBSERVED_REUSE/模拟/估计不能冒充物理命中；辅助目标不等于路由胜负 |
| S4 任务/环境参考 | 当前无直接路由目标的 ENV/MEM、评测或仅分析资料 | 完整来源覆盖不等于所有来源均可训练 |
| L1–L4 | 原 V2.1 的核心、扩展、复杂、保留层；按来源对应独立 Unit 分配 | 层级不是质量标签或监督类别，完整覆盖集与合法训练候选集分开 |

优先沿已有 V2.1/L1 引用、合法 S1/S2/S3、固定任务分割及原训练视图补充新特征；行数、独立任务/轨迹/请求、真正路由比较标签分别统计。`4,863,900` 是不同目标的历史候选记录数；原联合监督为 0 的事实不会因加入能力卡或教师摘要改变。新特征尚未学习记 `FEATURE_NOT_TRAINED`，不以元数据存在、JSON 被接收或路由 API 成功替代实际编码/训练证据。

**首批实际资产与监督缺口（主 Agent 阶段回报）**：初始 390 条由 S1/S2/S3 每类 Train/Val 各 64 条（384）加 6 条真实 prefix 构成；现在六前缀已进入单一 S2 Train，唯一实体仍 390 行。

| 监督来源 | Train 行 | Val 行 | 实际单位与位置 |
| --- | ---: | ---: | --- |
| S1 | 64 | 64 | 原比较/偏好记录，旧目标未对齐 V9 三身份，choice 目标仍 0 |
| S2 | 70 | 64 | 原 Train 64+6 真实前缀；`trajectory_prefixes/train.jsonl` 仅为相对符号链接 |
| S3 | 64 | 64 | 原请求/运行辅助记录 |
| 合计 | 198 | 192 | 唯一实体 390 行，链接不重复统计 |

六前缀来自 `gruebel_pycep_pr109`、`fonttools_fonttools_pr2313`，每题截止 0/3/7，原 Train 资格保留；两条固定参考为 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024`，不与前缀任务重合。六行不能计为六个独立任务或最优动作；不猜每个截止位置的教师生成状态。格式可加载只证明 Schema 可用，不能直接换 ID 伪造监督。离线制作由初始 0 发展为 4 条可用三字段（2 新、2 复用），在线 3/6 成功另计；AA 仍缺测，来源/标签/编码/学习分开记录，继续微调未报完成。

## 1. 数据来源总登记（Source Registry）

以下来源来自 2026-10-09 Q-007-R1/R2 的已有调研、公开 Hugging Face 数据卡与 GitHub 官方仓库。**优先级来自 Planning 推荐，不代表批准或量级承诺。** 同一原始来源出现在不同特征用途时复用相同 ID，不重复计算任务量。

### 1.1 Agent 真实执行轨迹与任务环境

| ID | 源与链接 | 原始粒度及可用标签 | 主要状态组 | 来源/训练资格 | 建议 |
|---|---|---|---|---|---|
| TRA-001 | [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) | 6 个多框架/多模型代表分片 (942 MB)，单步决策前状态隔离 | 任务、工具、上下文、模型异构 | **S5·已加工**：43,154 步有效记录；CC BY 4.0 | **P0·已就绪**，`OBSERVED_ACTION` |
| TRA-002 | [SWE-smith-trajectories](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories) | 全部 8 个分片 (972 MB)，Claude 3.7 Sonnet 真实执行步 | 任务、工具、时间、代码修复 | **S5·已加工**：107,983 步有效记录；MIT | **P0·已就绪**，`OBSERVED_ACTION` |
| TRA-003 | [CMU Agent Trajectories](https://huggingface.co/datasets/cx-cmu/agent_trajectories) | 上游 Hugging Face 接口返回 HTTP 403 Forbidden | 任务、工具、时间 | **S1·`GATED`**：0 条；遵循零造假规范合规审计 | 待授权，不进训练包 |
| TRA-004 | [AgentSuite multi_challenge](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) | 全部 8 个模型/思考模式全量 JSONL (44 MB) | 任务、模型比较、思考模式 | **S5·已加工**：2,736 步；同题思考开关对照 | **P0·已就绪**，Thinking-On/Off 对照 |
| ENV-001 | [SWE-Gym](https://huggingface.co/datasets/SWE-Gym/SWE-Gym) | 真实 Python 仓库/Issue/可执行回归测试套件 | 任务、环境、验证规范 | **S5·已加工**：2,438 个标准任务基准；MIT | 任务环境特征源 |
| ENV-002 | [SWE-rebench-V2](https://huggingface.co/datasets/nebius/SWE-rebench-V2) | 跨 20 种编程语言的超大规模任务基准 (409 MB) | 任务、多语言环境、复杂度 | **S5·已加工**：32,079 个任务；MIT | 多语言路由特征源 |
| ENV-004 | [Terminal-Bench 2.1](https://github.com/harbor-framework/terminal-bench-2-1) | 89 个终端系统/DevOps/开发真实挑战任务套件 (Commit 7131e43) | 终端环境、执行交互、沙盒验证 | **S2·可评测·禁训**：89 个任务；MIT；严禁并入训练集；划分 CANARY (8) / DEV (24) / TEST (57 封存) | 外部独立 Agent Benchmark 泛化评测基准 (历史 160 题已作废驳回) |

### 1.2 请求级模型选择与偏好监督

| ID | 来源 | 真实监督粒度 | 可训练性 | 规划用途 |
|---|---|---|---|---|
| ROUTE-001 | [LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | 27 个 benchmark、40 个模型实测结果 (bench-release) | **S5·已加工**：548,059 条实测记录 | P0·多模型真实能力与成本对照 |
| ROUTE-002 | [RouterBench](https://huggingface.co/datasets/withmartian/routerbench) | 86 类任务、11 个主流模型得分与官方 Oracle 路由 | **S5·已加工**：36,497 条 0-shot 样本 | P0·标准同行评审路由基准 |
| ROUTE-003 | [TwinRouterBench Static](https://huggingface.co/datasets/Amorph/TwinRouterBench) | 多步降级搜索能力档位 (`low`, `mid`, `high`) | **S5·已加工**：970 步；**强制标为 EVAL_BENCHMARK_ONLY** | **严禁进训练集**，仅作最终泛化评测 |
| ROUTE-004 | [Arena Human Preference 55k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | 真实用户 Prompt + 两两模型盲测人类偏好胜负 | **S5·已加工**：57,477 场对决 (64 模型) | P0·真实人类偏好监督信号 |
| ROUTE-005 | [Finding the Right Fit](https://huggingface.co/datasets/yixuanli97/finding-the-right-fit) | 6 大 Harness 框架端到端开销、真实缓存与奖励 | **S5·已加工**：6,204 条；**标为 RESEARCH_ANALYSIS_ONLY** | **严禁训练/蒸馏**，仅作系统分析基准 |

### 1.3 KV Cache、请求时间、服务端资源

| ID | 来源 | 关键字段与性质 | 可以研究什么 | 不可以替代什么 |
|---|---|---|---|---|
| CACHE-001 | [Mooncake FAST'25](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release) | 生产请求时序、前缀块 `hash_ids` (conv, tool, synth) | **S5·已加工**：39,632 条；`OBSERVED_REUSE_OPPORTUNITY` | **绝不冒充**商业 API 实际缓存命中 |
| CACHE-002 | [Mooncake 旧版 trace](https://github.com/kvcache-ai/Mooncake/tree/main/arxiv-trace) | 旧版匿名前缀/请求记录 | 历史请求变化 | 版本可能重合；不得双计 |
| CACHE-003 | [Mooncake Cache Benchmark](https://kvcache-ai.github.io/Mooncake/performance/mooncake/storage-benchmark.html) | 基于块散列/容量/淘汰与缓存策略的回放和指标 | **SIMULATED** 读写与 hit rate | 不是真实原始 API 命中记录 |
| CACHE-004 | [KV Cache Workload Bench](https://github.com/hokiyoung/kv-cache-workload-bench) | 合成/派生共享前缀、会话、并发、驱逐 workload | 模型化缓存压力与容量 | 不是实测封闭 API usage |
| CACHE-005 | 未来 Provider 实际 Usage（无单一公开仓库） | requested model、真实 cached/read/write Tokens、provider Endpoint、账单和时间 | **MEASURED** 的唯一权威来源之一 | **当前本项目未持有充分的 Agent 同状态原始计量样本** |
| CACHE-006 | [vLLM Metrics / Prefix caching](https://docs.vllm.ai/en/latest/usage/metrics/) | 获准运行后可观察引擎实例的实际缓存统计 | 本地引擎 MEASURED | 并非预先存在的独立下载数据集；未经许可不得部署采集 |
| TIME-001 | [BurstGPT](https://github.com/HPMLL/BurstGPT) | 真实 ChatGPT 与 GPT-4 生产时序到达与负载 | **S5·已加工**：1,404,294 条；`OBSERVED_WORKLOAD` | 不含完整 Agent task outcome |
| TIME-002 | [Alibaba xMaaS 2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-maas) | MaaS 集群实例/资源/显存/GPU/负载时序 | 系统级容量与时间压力 | 不是逐请求 Agent 动作真值 |
| TIME-003 | [Alibaba GenAI Trace](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-v2026-GenAI) | 真实生成式服务队列/资源和时延（包括非 LLM） | 系统请求并发和资源预算参考 | 非编码 Agent 或路由胜负 |
| TIME-004 | TRA-001/TRA-002 的时间子视图 | 已发生 step/turn/工具/局部时间 | Agent 剩余步骤/时间信息 | 不另计一个独立数据集；无初始预算则剩余额度 UNKNOWN |

### 1.4 长期记忆、多 Agent 协作

| ID | 真实来源 | 可覆盖状态 | 主要限制 |
|---|---|---|---|
| MEM-001 | [LoCoMo](https://github.com/snap-research/locomo) | 会话历史、事件、时间推理、摘要/证据 | 已汇编入 MEM-005 |
| MEM-002 | [LongMemEval](https://github.com/xiaowu0162/longmemeval) | 跨会话记忆、用户事实更新/冲突、检索 | 已汇编入 MEM-005 |
| MEM-003 | [LongMemEval-V2](https://github.com/xiaowu0162/LongMemEval-V2) | 长程 Agent 记忆、100 轮干草堆文档检索 | **S5·已加工**：451 个任务；`MEMORY_BENCHMARK` |
| MEM-004 | [MemoryAgentBench](https://huggingface.co/datasets/ai-hyz/MemoryAgentBench) | 增量记忆与检索、测试时信息更新 | 非路由成功率标签 |
| MEM-005 | [MemoryCraft](https://huggingface.co/datasets/daven3/MemoryCraft) | 跨会话长期记忆对话与问答对 | **S5·已加工**：510 条；`MEMORY_BENCHMARK` |
| MEM-006 | [LongBench](https://github.com/THUDM/LongBench) | 上下文长度、长文本检索/归纳负载 | 文本能力压力，不是 Agent Memory 真迹 |
| MAS-001 | [MARBLE/MultiAgentBench](https://github.com/ulab-uiuc/MARBLE) | 上游 Hugging Face 接口返回 HTTP 401 Unauthorized | **S1·`GATED`**：0 条；合规审计记录 |
| MAS-002 | [MASBench](https://github.com/BUPT-GAMMA/MASBench) | 通信、部分可观测性、协作记忆、代价 | 许可证与可下载训练轨迹待核 |
| MAS-003 | [AgentWorld](https://arxiv.org/abs/2609.31590) | 长程角色不对称、依赖/冲突、协调 | 新近基准；训练材料是否可用待核 |
| SYS-001 | [OpenSquilla / Harness-Native Agentic Routing](https://github.com/TokenRhythm/opensquilla) | **结构参考**：context compaction、memory、Agent turn loop、router、usage/decision log 与 ensemble | **不是公开模型路由训练轨迹库**，不能把代码当数据集；本阶段不创建第二个 Harness |

### 1.5 已有本项目本地来源的职责

| ID | 现有相对路径 | 可支持 | 限制 |
|---|---|---|---|
| OWN-001 | source/cch-model-cost-cache-statistics.csv | CCH 真实聚合 model×effort、USD/token/cache 信息先验 | 缺 task_id / 完整同状态前缀和任务终局；不能作为反事实 |
| OWN-002 | cleaned/sxyq-blog-gpt-usage-cleaned.csv | Blog 真实调用分布、model/usage/部分缓存与 quotaUnits | 计价原单位为 quotaUnits，**不可无证据换算 USD**；缺有效终局 resolved |
| OWN-003 | summaries/ 中既有聚合 CSV | 训练采样权重/部署参考及研究可视化 | 不是新增独立可监督训练数据，不能重复计数 |

## 2. 八组 Agent Runtime 状态 → 数据源覆盖矩阵

矩阵表示**候选数据潜力，不是已下载后实测的字段覆盖率**。最终字段级覆盖和 missing rate 应在下一阶段的真实 schema audit 中填写；某来源不支持字段就标 UNKNOWN。八组状态要求与 [RESEARCH_OVERVIEW §2](../planning/RESEARCH_OVERVIEW.md) 一致。

| State Group | 主要来源 ID | 预计可观测信息 | 缺口 / 后续需要 Harness |
|---|---|---|---|
| Task/Subtask | TRA-001/002、ENV-001/002、ROUTE-001 | task、repo、issue、语言、任务类别、已发生进度 | 任务当前子目标图/难度 proxy 不一定有 |
| Agent/Coordination | MAS-001/002/003、SYS-001、TRA-001 | Agent 角色、拓扑、沟通事件、共享上下文 | 多子代理 handoff 与实际执行 budget 需自有 Harness |
| Context/Memory | MEM-001～006、TRA-001、SYS-001 | 历史窗口、消息长度、摘要/检索、压缩事件 | provider 真实 context 剩余、记忆版本及有效性未必公开 |
| Tool/Environment | TRA-001～004、MAS-001、SYS-001 | 工具/测试/环境回报、失败/重试 | 只接收决策前已完成的工具结果 |
| Verification/Recovery | TRA-001/002、ENV-001/002 | 测试失败、修复循环、当前验证结果 | 最终 evaluator 和标准修复补丁只能作为 label/审计 |
| KV Cache/Continuity | CACHE-001～006、OWN-001/002 | 真实前缀可复用机会、真实 usage 口径、本地实例指标 | 公开 Agent 真缓存命中稀缺；必须标 measured/reuse/simulated/estimated |
| Temporal/Execution | TIME-001～004、CACHE-001、TRA-001 | 到达、已发生步骤/耗时、Token、服务负载 | 初始/剩余 task budget、价格和工具总耗需原始账本 |
| Provider/Availability | §3 Provider Registry、TIME-002、SYS-001 | 可用 model/effort、能力、区域、API 价格、负载/健康 | **政策作为动态确定性源**，不能从旧训练轨迹猜当前可用性 |

**不能直接从公开轨迹推断的能力**：不同 Provider 在同一个决策前状态下未选动作的 task outcome、跨模型物理 KV 可迁移、实测缓存折扣、某日实际 API 权限以及多 Agent 剩余额度。涉及这些字段须保持 UNKNOWN 或由合法的真实运行时数据补充。

## 3. Provider / Model / Effort / Cache Policy 证据注册表

这一节是后续**动态 Registry 的资料来源目录**，不是已经构建好的运行时 model registry。**本文件记录哪些政策需要核实以及官方入口，不臆造对所有模型适用的缓存政策、折扣或 Effort 档位。**

### 3.1 已找到具体缓存机制官方说明的主体

| Policy ID | Provider / 主要模型系列 | 官方证据地址 | 目前可确认的政策类型；仍需逐型号核查 |
|---|---|---|---|
| POL-001 | OpenAI / GPT、Codex | [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) | prompt cache usage、读写/保存口径、TTL/价格版本；不得统一所有 GPT 型号 |
| POL-002 | Anthropic / Claude | [Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | cache read/creation tokens、5m/1h、tools/thinking 影响前缀与过期 |
| POL-003 | Google / Gemini | [Context caching](https://ai.google.dev/gemini-api/docs/caching)、[Thinking](https://ai.google.dev/gemini-api/docs/thinking) | 隐式/显式、存储费、TTL；thinking 支持因型号/接口不同 |
| POL-004 | xAI / Grok | [Prompt caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching) | 自动缓存、缓存字段和会话亲和；按型号查具体用量 |
| POL-005 | OpenRouter（API 聚合） | [Caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching) | sticky provider / 缓存折扣；必须记录**实际承载 Provider Endpoint** |
| POL-006 | DeepSeek 原厂 API | [KV disk cache](https://api-docs.deepseek.com/zh-cn/guides/kv_cache/) | cache hit/miss tokens；开源权重自托管**不继承**原厂 API 缓存 |
| POL-007 | 阿里百炼 / Qwen、托管其他开源模型 | [Context cache](https://help.aliyun.com/zh/model-studio/context-cache) | 隐式/显式，按型号、地域、产品版本核最小长度/TTL/价格 |
| POL-008 | 火山方舟 / 豆包及托管模型 | [Context cache](https://docs.volcengine.com/docs/ark/context-cache?lang=zh) | 隐式/显式/session、thinking/tools/endpoint 约束，版本待锁 |
| POL-009 | Moonshot / Kimi | [Caching guide](https://www.kimi.com/academy/best-practices-for-context-caching) | cache read/write、部分 5m/1h，Chat/Responses/Messages 接口不同 |
| POL-010 | 腾讯 / Hunyuan、TokenHub | [API 旧文档](https://cloud.tencent.com/document/product/1729/101838) | 历史 CachedTokens 有官方入口；**现行 TokenHub Endpoint 需重新核实** |
| POL-011 | 百度 / ERNIE、千帆 | [缓存通知](https://ai.baidu.com/ai-doc/WENXINWORKSHOP/Rm6uq7jy9) | 部分历史型号支持缓存用量，不能推成全部现行型号 |

### 3.2 已列入覆盖范围，具体型号/缓存政策待官方核验

| Policy ID | Provider / 模型系列 | 官方入口 | 当前状态 |
|---|---|---|---|
| POL-012 | 智谱 / GLM、Z.ai | [BigModel](https://docs.bigmodel.cn/) | **PENDING_MODEL_SPEC**；原厂 cache/effort/TTL/usage 未逐型号核准 |
| POL-013 | MiniMax 原厂 / MiniMax-M 系 | [平台](https://platform.minimaxi.com/) | **PENDING_MODEL_SPEC**；不能套用百炼托管产品 |
| POL-014 | 阶跃星辰 StepFun / Step 系 | [平台](https://platform.stepfun.com/) | **PENDING_MODEL_SPEC** |
| POL-015 | SiliconFlow / 各种开源托管模型 | [文档](https://docs.siliconflow.cn/) | **PENDING_ENDPOINT_SPEC**；托管策略不等于原厂 |
| POL-016 | Mistral | [官方](https://docs.mistral.ai/) | **PENDING_MODEL_SPEC** |
| POL-017 | Cohere | [官方](https://docs.cohere.com/) | **PENDING_MODEL_SPEC** |
| POL-018 | Together AI | [官方](https://docs.together.ai/) | **PENDING_ENDPOINT_SPEC** |
| POL-019 | Groq Cloud | [官方](https://console.groq.com/docs) | **PENDING_ENDPOINT_SPEC** |
| POL-020 | Fireworks AI | [官方](https://docs.fireworks.ai/) | **PENDING_ENDPOINT_SPEC** |
| POL-021 | 本地 vLLM：Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan 等开源权重 | [Prefix caching](https://docs.vllm.ai/en/latest/design/prefix_caching/)、[Metrics](https://docs.vllm.ai/en/latest/usage/metrics/) | 按实际运行引擎、tokenizer、实例和租户隔离核，**不能只按权重厂牌判断** |
| POL-022 | 本地 SGLang：各开源权重 | [官方](https://docs.sglang.ai/) | PENDING_ENGINE_CONFIG；运行时本地缓存配置和指标待另行授权核对 |

**Provider 模型范围**：国产开源与闭源分别标注 Qwen、DeepSeek、GLM、Kimi、MiniMax、Hunyuan、Step、豆包、文心等（具体哪一型号开源、闭源、在哪个平台可用，尚未逐型号列表确认）；国外 GPT、Claude、Gemini、Grok、Mistral、Cohere 与第三方托管。必须将 **base_model、actual_provider、deployment_id、api_endpoint、model_revision、region** 拆开。权重许可与服务使用条款各自独立。

### 3.3 每个 Provider 模型政策条目未来必须补齐的字段

| 分类 | 必备字段 |
|---|---|
| 身份 | provider_id、model_id、model_revision、deployment_id、api_endpoint、region、original_vendor、open_weight_status |
| 能力 | context_window、supports_tools、supports_json、image_mode、effort_allowed_values、effort_requested/effective、支持依据 |
| 缓存 | cache_mode(implicit/explicit/engine)、cache_read/write_fields、minimum_prefix_tokens、ttl、cache_key_scope、session_affinity、cache_invalidation_policy |
| 定价 | input/uncached、cached_read、cache_write、output、reasoning 是否单独计价、storage_fee、currency、price_catalog_version、valid_from/to |
| 可用性 | max_rate、quota、retry/backoff、provider health、access_region、tenant/account limitations |
| 合规 | terms_url、api_output_training_allowed、residency、data_retention、license_status、policy_reference |
| 证据 | source_url、verified_at、source_revision、evidence_level(verified/pending/conflicting)、field_confidence、last_reviewed_by |

**未知是 UNKNOWN，不等于不支持或支持。** 定价、TTL、用途和 ToS 不能由 Laya/Kev 权重固化为长期真实政策；调用遵循现有 ProviderRegistry 与必要约束。Google [API Terms](https://ai.google.dev/gemini-api/terms/) 等包含特定训练用途限制；每个 API 输出能否用于路由模型微调，按实际条款与授权保留证据。

### 3.4 · V9 轨迹教师与 Model×Effort 能力证据（2026-10-22 起点，10-29 同步）

负责人保留 V9 五 RQ，并要求外置教师短评和具体模型/Effort 能力证据真正进入编码。早期多条相似轨迹检索、多项字段已简化为两条固定参考和三核心字段。390 行材料、参考 ID/不重合及少量离线字段已有新回报；初始离线 0、AA 获取失败和旧布局任务被裁仍作为历史证据保留。新特征未学习不能记成训练准备或新权重已经完成。

| 登记对象 | 建议记录字段 | 待核实的证据标准 |
| --- | --- | --- |
| 模型/动作身份 | `provider_id, base_model_id, model_id, revision, deployment_id, endpoint, region, native_effort, action_id` | 只有 Provider 实际支持的档位才能进候选 |
| 多项能力分数 | `benchmark_id, benchmark_version, metric_name, score_raw, score_scale, normalized_score, harness_id, eval_split, evaluator_revision, evaluated_native_effort, sample_count, eval_date, source_url, source_license, evidence_status` | 软件工程、代码推理、工具调用可参考 SWE-Bench Pro、LiveCodeBench、BFCL，但具体版本、协议、训练权利和分数尚未核验 |
| 能力缺失/不确定性 | `score_scope(model/effort), measured_effort, measurement_type, missing_reason, CI_or_uncertainty` | `NOT_MEASURED` 不等于 0；同一型号的模型级分数不能自动复制到所有 low/medium/high；不同 Harness 不能直接比较 |
| 动作价格/约束 | `price_snapshot_id, input_usd_per_1m, output_usd_per_1m, cache_read/write_usd_per_1m, supports_tools, context_limit, actual_availability` | 分 actual provider+endpoint+revision 按日期核价；hard filter 始终外置 |
| 两条固定成功参考 | `reference_task_id, reference_trajectory_id, reference_model, reference_effort, verified_outcome, task_split, source_license, reference_revision` | 高效完成/失败恢复各一条，许可适用且与 Final 隔离；命令顺序不作唯一正确过程 |
| 当前评审短摘要 | `progress_summary, main_blocker, next_milestone` | 实际进入同义 state/编码；是教师推断，不作终局或最优动作标签 |
| 教师来源与时效 | `episode_id, assessed_through_decision_id, teacher_provider, teacher_model_id, teacher_native_effort, reference_ids, trigger_reason, generated_at, status` | 实际顶级教师与 Qwen 联调用途分开；缺席、失败、过期显式记录 |
| 外置教师费用与时延 | `teacher_input_tokens, teacher_output_tokens, teacher_cached_tokens, teacher_cost_usd, teacher_latency_ms` | 在线调用按配置教师目标身份价格计入相应 Episode，离线制作计数据/训练；实际后端身份、后端价格与供应商实收另列 |

**来源与许可边界**：现有轨迹可提供已执行动作、工具返回和部分终局，尚不能证明工具意图合理性人工标签或每 Effort 同协议能力分。两条 TRA-001 公开 Train 成功参考为 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024`，`resolved=true`、`split=train`；六前缀来自另外两任务，每题截止 0/3/7，与参考不重合，原 Train 资格保留。来源/成功标签与分割不证明教师效果或最优路由，具体参考角色和条款证据沿原登记保留。Final 的答案、未来轨迹/验证和结局不用于教师、训练、选池或调参。

**历史离线制作与覆盖状态**：复用原 Assessor，2 次真实请求/2 次成功，4 条可用三字段样本（2 新、2 复用）、2 条未触发，`summary.teacher_data_status=PARTIAL`、`GENERATED=4 / NOT_GENERATED=386`。实际教师为托管 API 返回的 `self-dploy/Qwen3.8-27B`，不称顶级 Sol；三字段是当前前缀短评，不提供未执行动作真值。两请求 prompt 13,766、completion 949、总 Token 14,715；reasoning 678 已在 completion 内，cached 0 已报告、USD null。复用已有短评不等于物理缓存命中，离线费用归材料/训练；4 条字段覆盖不代表 390 条都已有教师或新特征已学习。

**字段编码验证与已测负结果**：三字段/能力原分/缺失表示须进入同义state编码。holding Tokenizer实测旧LayaState为2,762/2,827 Token、预算940、任务位置2,733/2,798，任务被裁，历史负结果保留。唯一V9 formatter与原Schema薄调用的 [final编码与训练prefix分词记录](../results/iterations/20261029-v9-alias-smoke-tools/input_encoding_validation.json) 已确认最终任务、三教师字段、候选卡和缓存/身份关键字段进入编码；新顶层`recent_tool_validation`于18:44 UTC/02:44台北仅验证原step5：Laya1024/head512、状态预算940下，512字符真实工具结果仅末128字符在Token `[879,930)`为`FULL`；任务、三教师、三候选卡及缓存/当前和前次身份均`FULL`，长`history_snippet`仍裁。Kev原native编码2147 state/2224 total、不截短、候选键3个，本次未新增Kev API前向。原`context.py`单文件已原位部署，真实128字符tail、源cached3136与前次Sol身份保留；源缓存数不算新缓存命中。随后同源一次Laya真实前向`epoch_01/fallback=false`，本次Router1/生成0，不新增材料、教师或有效目标。此前198条Train已测分词，本次未重测该批Train或Val；4教师核心在当前Laya1024下保留，但6条完整state被裁，8192推荐尚未启用；192条Val只核身份/数量而未测长度。原384默认Kev接纳诊断保留历史，当前8192与198条实际接纳另记；分词本身不作学习证据；第四次真实训练单列为`FEATURE_PARTIALLY_TRAINED`（4教师/8passes、三新身份目标0），原Serving旧权重的`FEATURE_NOT_TRAINED`保留，能力卡仍缺测。两路Native前缀真实前向、Kev20秒失败及一次60秒成功均保留，不重跑同题。choice目标0、AA缺测与386条未生成教师的覆盖缺口不变；现状见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)。 04:20同一JSON的`live_transport_validation`支持旧SystemOne直传8822字符、同正文native编码与响应1024输入Token；未捕获旧进程Token IDs、普通`/route`未验证，长history仍裁。新Kev Val及内部评分已完成但四指标比C03均退步，不改AA0/choice与Effort目标0或teacher覆盖。

### 3.5 · V9 固定参考、能力刷新与模型身份（2026-10-29 要求）

**固定参考轨迹**：首版不部署动态检索、Embedding 或重排。TRA-001 对应公开数据的两固定参考为 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024`，`resolved=true`、`split=train`；原高效完成/失败恢复的用途要求保留，具体角色对应不凭名称猜测。训练前缀任务 `gruebel_pycep_pr109`、`fonttools_fonttools_pr2313` 与参考不重合。原资产保留 `reference_id, source_dataset, source_url, license_and_training_rights, task_family, agent_harness, verified_success, split, test_overlap_check, excerpt_hash, prepared_at`；既有 Open-SWE-Traces 加工事实和原 Train 资格不变，Final 及其未来解答不进入参考。

**能力记录主值与刷新**：保留 `score_raw`、`score_unit`、`benchmark_version`、`metric_name`、`harness_id`、`model_revision`、`evaluated_native_effort`、`source_url`、`evidence_status`；AA `Intelligence Index` 是 0–100 综合指数，正确率/通过率才按百分比解释。每次手动执行专用刷新入口重新请求 AA，Agent 使用已保存快照；Agent 启动和 Router 每次决策不自动访问 AA。成功后更新同一 `our-project/code/data/v9/` 当前资产，失败时保留已有有效快照的原采集时间和本次失败原因；现有 `load_current` 继续读取快照，不新增自动网络行为、job、定时服务或另一份能力台账。依据为第二提示词 198–208、335、773 行及本轮澄清，用户已撤销自动刷新派发。正式训练/实验固定相应 `snapshot_id`；综合低中高只作同版本参考分布的派生特征并记 `tier_rule_version`，专业维度保留连续原分。未测 Effort 为 `NOT_MEASURED`，模型级分不能复制为各档实测，也不能作为最优路由动作标签。

**AA 当前实测来源**：改进现有解析后，Sol 404、Luna 200 但解析失败、Flash 404，AA Key 缺失；实测能力记录仍 0，current 保留原 `FAILED/NOT_MEASURED` 快照。HTTP 200 不算取得分数，0 条记录不写成模型能力得分 0，不用 Alias 后端成绩补三正式模型。

**三逻辑身份与实际后端**：规划身份为 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`；映射实验真实请求后端为托管 Qwen3.8-27B，Router 选择和实验身份仍按逻辑目标记录。映射费用按目标身份 `ModelSpec` 价乘实际 input/output/cache 用量；教师按配置教师目标身份计价。`returned_model_id` 保留真实返回身份，后端请求/返回身份、后端价格与供应商实收另列；后两项缺失不影响映射实验。映射结果不作为独立物理模型质量对照。托管 Flash、开源 Flash-Next、校园 9002 物理模型与 Parfit API 身份分别记录。审阅子 Agent 的 `gpt-6.1-sol/max` 不充当生成或教师配置证明；本台账不存密钥。

**状态与用途**：hcnsec 源 `PCG/config/pi-sag.local.env` 仅读 `QWEN_API_KEY`、未改；三逻辑身份真实 Provider 映射均已确认。网关 `/models`/先前流式名 `Qwen3.8-27B` 与实际非流返回名 `self-dploy/Qwen3.8-27B` 原样分列，托管 API 物理对应 UNKNOWN，不据返回名推断本地零费或关联 9002。单题 9 次生成/13 次 Bash/7 项 unittest 成功终局、仅选 Sol，在线 Teacher 3/6 成功、失败继续；先前两次三字段送到下次 Router，保留 `TEACHER_ALIAS_SMOKE`，与离线 2/2 和 4 条字段分开，不当顶级教师成绩。额外 Luna/Flash 短 Provider 映射不算新 Agent 题。数据/语义/学习及 usage 缺口保留，SWE/Terminal 成绩独立、8/24/57 划分、Mac 零权重与 Final 隔离保留；当前 API 不设总 Token 或美元上限。

**Native 回放与导入身份**：成功目录 `router_input_replay.json` 记录 Laya 新输入选 `gpt-6-luna`、`epoch_01`、`fallback=false`；Kev 首次 20 秒客户端窗口超时模拟 fallback，一次 60 秒窗口重测约 53,516 ms 真实前向成功，选 `gpt-6.1-sol`、`fallback=false`，两路均有三候选真实概率。Kev ID `1001bb4d826a52d1f399e183466143f4da7b741b` 是 Serving 导入适配器，不能称 R11 候选。回放不新增题目或正式/科学成绩，不替代最终 Tokenizer、新训练或部署结果。

**不同工程题失败与原始记录**：`20261029-v9-kev-alias-smoke` 的 `duration` 题完成 2 次真实生成/3 次 Bash 后，第 3 次路由 60 秒超时，默认原 PolicyModel 在 fallback 后退出，原回报 `FAILED/验证1`、所有日志保留。Serving `2291306` 未重启/换权重；`KevAdapter` 启动无 `device`、默认 CPU/`torch_cpu`，step0/step1 真实前向 18,802/38,674 ms，step2 工具 history 长度回报 3,835（单位未报）时超时。首个 Bash 的 `find /` 上游 30 秒超时、后续 `ls/pwd` 定位和未改外部数据如实保留；Host 无容器隔离，不作为安全或正式基准证据。该失败与成功 invoice、Native 回放及教师失败后继续的行为分开，不自动并入 390 行材料、参考或最优动作监督。失败回报当时计划在原 Runtime 补 CWD、按 `router_context_chars` 缩工具视图并保留 task/teacher/raw mini 消息；后续实际结果见下段，不重跑成功题或另建记录体系。

**短视图实测与重跑终局**：原失败目录 [input_latency_validation.json](../results/iterations/20261029-v9-kev-alias-smoke/input_latency_validation.json) 记录任务 1,019 字符全保留、工具摘录 3,835→1,280 字符、任务/工具字符预算 2,300，7 条 mini 消息及教师/卡片/缓存与身份连续状态保持；原适配器 CPU 前向 37,771.85 ms、`fallback=false`，概率 Flash 0.7234/Sol 0.1468/Luna 0.1298。该回放教师为 null、能力卡缺测、生成请求 0，不增加有效样本或缓存/学习证据。必要重跑 `20261030-v9-kev-alias-smoke-compact` 已结束，[metrics.json](../results/iterations/20261030-v9-kev-alias-smoke-compact/metrics.json) 与 [verification.txt](../results/iterations/20261030-v9-kev-alias-smoke-compact/verification.txt) 保留 10 次生成、13 次真实 Bash、10 次 Kev 路由全部 `fallback=false`，CPU 前向 20,430.85–37,243.64 ms，本次原路由超时已解决；全部逻辑 Flash/实际 Qwen、Serving 导入适配器不变。教师 5 请求/2 成功，3 失败依次 TimeoutError/JSONDecodeError/TimeoutError，成功短评在 steps3/4/5 实际送入 Router；本题仍有 7 个 subtest errors（7 方法、4 通过），10 步 LimitsExceeded、FAILED/resolved=false、验证退出 1，无官方或科学成绩。

**训练参数、部署与清理事实**：现有 [prepared/summary.json](../code/data/v9/prepared/summary.json) 写 Laya 2 Epoch、`max_len=1024/head_max_len=512`，Kev 2 Epoch、`max_state=8192`；父 R11 原 1 Epoch/384，与在线 Serving 导入适配器不同。此前已保存的198 Train测量表明当前Laya1024保留4教师核心、完整state裁6条；全198条完整Laya编码至少需8143，8192推荐尚未启用，不改变正在运行的F14。主 Agent 首批已在原服务器部署 37 个源码/数据/相对链接对象、6,993,920 字节，16 个 V9 Python 模块及 schemas/registry/common/390 材料；原两文件增量补丁保留 Laya 4 处历史差异，45KB common 重复实现改为现有薄别名、`common is canonical=True`，root 真正执行链保留。原 Python/`_material` 实读 198 Train/4 教师/2 refs、相对 Train 链接有效，GPU/Serving 未重启。原测试与新 artifacts 四文件保留，duration 临时目录、自有本机隧道 28959已清理/结束；部署后前三次失败保留历史；第四次两轮已完成并保存新head/adapter/tokenizer，仅在A6000、未传Mac或上线Serving，现行结果见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 的训练表；原部署/清理事实独立保留。运行记录与材料分开，不增加390行或最优动作监督。

**首次真实启动失败（历史保留）**：原 candidate_queue/ledger 登记 `KEV-V9-001`，父 R11 实体/内部四指标 score106.74866622586939，原 16 个 R 候选完成，登记时 QUEUED 仅历史。同一 CLI 第 1 次 worker13266 在 0.145 秒退出 1，未加载 GPU 模型/消费训练输入，FAILED 及原 attempt 保留。`dispatcher.py` 路径执行让 `sys.path[0]` 在 `modelrouter/training`，bare `import kev` 误落项目 `training/kev`、官方 `kev.train` 未导入；train.log/attempt/cursor 保留。189 项先前组合测试通过不替代实跑失败。

**第2次真实反向OOM（失败历史）**：同一原 wrapper 两行模块入口调整已部署，窄测 40 项通过，官方 `kev.train` 实际导入位置为 `external/kev/kev/train.py`。第 2 次worker16722先RUNNING，8K输入进入真实反向计算后Torch CUDA OutOfMemory、自然退出1；进程13.54 GiB、再分配60 MiB时仅59.94 MiB空闲，日志Epoch0/Step20/100/Loss0.993。原Loader全部接纳198条记录，两轮预期396条次；失败目录仅`training_config.json`，输入曝光0是启动时统计，失败后完整输入曝光与独立覆盖UNKNOWN，不记作0或全部训练。接纳量、预期量和进度日志不提供完整实际消费量。首次13266入口失败和第二次16722反向OOM均保留，两次失败未产出两轮完成权重或固定Val；该次UNKNOWN与`FEATURE_NOT_TRAINED`历史状态保留。第四次396完整passes及新候选`FEATURE_PARTIALLY_TRAINED`另列，不覆盖失败统计或缺测能力分数。

**原资源等待及三次FAILED历史、现行Kev结果**：原资源代码已按已观察占用下限加原2 GiB余量增量部署，CLI验证`WAITING_FOR_GPU`；01:43的12,668/15,973 MiB保留历史，02:11空闲12,698/需15,973 MiB为当时等待，旧384输入`required=12103`不适用于8K，不增其他限制。CLI25201曾沿原`main_loop(wait_for_resources=True, v9_only=True, ...)`保留，主Agent确认27184无worker并已结束；服务器源码`CLI_WAIT/EXIT_RESET=true`已验证，前三次FAILED和原CLI25201自然退出保留历史；现行结果见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 的训练表；原失败/曝光分列。原输出保留与第四次接续参数已确认，不另建loop/Runner/定时任务。F14/ComfyUI/Serving未被干预；F14只读证据见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 的F14段；先前占用、ComfyUI`<A6000_HOST>:8188`监听及运行队列1/pending0历史回报保留，图像任务活跃，`127.0.0.1`不通属绑定地址，未卸载/干预。原Provider/telemetry账本/ledger/logger已补`alias_mapping/query_raw`；服务器构造V9 AliasProvider成功、账本根`<SERVER_PROJECT_ROOT>`，未发API请求/读Key、不新增client服务，Alias/账本补齐已验证且无新API，不计认证或真实生成通过。此前source部署为40个文件/链接加原Laya/Kev增量，首批37对象/6,993,920字节保留历史，后续总字节未报。Serving仍旧权重；Laya hook在盘、F14内存不读，下一自然child完两轮边界生效。旧exit处理由服务器源码确认，不干预健康worker、不另建Trainer/队列；第四次真实训练曝光与失败UNKNOWN分列，原Serving仍旧权重/`FEATURE_NOT_TRAINED`；原预算575783/256135/168082、135calls未变。原评分及留存机制保持；本轮收尾仅涉及多余控制器和临时连接，04:33:44主Agent确认无当轮SSH连接残留。 原时间同步/评分/留存元数据已更新，原三次失败UNKNOWN不覆盖；F14只读证据见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md) 的F14段。

**运行记录与材料分开**：主 Agent 已把误放 src 的 2 条真实 Episode 与 14 条真实调用迁至原 `experiments/agent_pilot/ledgers`、`runs/agent_pilot/multi_model_calls.jsonl`，Logger 复用同一根定位；误放副本已删，全部数据保留。它们不并入 390 行材料、不另建长期记录体系。

**历史失败 usage、旧额度与旧暂停记录**：保留历史已知 Token 410,353、9 次失败上限预留 77,544、余额 512,103；其后快照为 known/reserved/remaining=`494912/193040/312048`。该历史阶段最后实读为 `575783/256135/168082`，新增 15 API 请求已计账、135 累计 calls，该阶段曾停止新增生成式请求，旧暂停决定不作当前约束。失败实际 usage UNKNOWN，reserved 不算实际消耗；duration 失败教师缺测使完整 prompt/completion/reasoning/cache/USD 仍 null，不写零、不重复计价，不把预算已知量当完整用量。invoice 成功与 duration 失败独立，原记录不覆盖，离线/在线成本分列。

**实际金额单位**：hcnsec `raw_usage.cost` 未附 `currency/cost_currency`，单位不明；新 Provider 保留 `raw_reported_cost` 与 `reported_cost_unit=NOT_REPORTED`，只在响应明确 USD 时赋 `actual_billed_cost_usd`。未知单位金额不列入完整美元费用。当前 Episode 旧事件保留原版本输出，旧字段名不能证明单位；含超时的完整费用总额为 `None`，最终汇总注明单位未确认，不能写成零美元或按逻辑模型价目补造实付额。

### 3.5 · 2026-10-28 V9 简化能力卡和两条轨迹参考的准入（拟议）

**固定参考轨迹**：首版不部署动态检索、Embedding 或重排，只离线挑两条公开的**确实成功**的简短 Agent 轨迹样例（一条高效完成、一条失败恢复），并登记 `reference_id, source_dataset, source_url, license_and_training_rights, task_family, agent_harness, verified_success, split, test_overlap_check, excerpt_hash, prepared_at`。`nvidia/Open-SWE-Traces`（https://huggingface.co/datasets/nvidia/Open-SWE-Traces）仅列待审来源，不代表已经下载、验证成功标签或许可适合目标用途。正式 Final 不能看到同题未来轨迹或答案。

**能力记录主值**：`score_raw`、`score_unit`、`benchmark_version`、`metric_name`、`harness_id`、`model_revision`、`evaluated_native_effort`、`source_url`、`evidence_status`；正确率/通过率可为百分比，AA 综合 `Intelligence Index` 是 0–100 综合指数（**不是百分比**）。模型级成绩不能无标注复制给各 Effort；未测为 `NOT_MEASURED`。综合低中高属于同版本固定参考模型分布的派生特征，并记录 `tier_rule_version`；各专业维度暂只存原始连续成绩。只在新模型/修订/Provider 可用性与价格或实际 Effort 菜单变化时更新，正式比较锁定证据快照。

**状态与用途**：本节描述未来审计与数据加工要求，尚没有新训练数据、新模型分数或真实教师调用记录。现有权重不能因输入 JSON 变更就视为理解新字段；先核合法用途、分割及模型训练编码。SWE-bench Lite/Verified 的开发任务及原 Terminal-Bench 2.1/Harbor 评测集独立登记，不混同成绩或使用封存任务补分。

### 3.6 · 2026-10-29 首批三模型能力证据及刷新式本地快照（待本地执行）

负责人明确首批三款**逻辑研究身份**：`gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`；映射实验真实请求后端为托管 Qwen3.8-27B。实验费用使用所选逻辑身份价格和真实用量，不依赖 27B 后端价；Sol 输入/输出/缓存读/缓存写采用 v2 已保存官方价 `2/10/0.1/2.5` USD/百万 Token。Flash 当前参考 `0.15/0.47/0.016` USD/百万 Token 来自 OpenRouter，不能标为阿里官方 USD 价格；不自造汇率。Luna 价格行见本节上表。三原目录 `mapped_cost_accounting` 的金额、缺失用量和旧 raw 保留情况见 [PROJECT_STATUS](../planning/PROJECT_STATUS.md)；完整金额遇教师 usage 缺失仍为 null。

**官方数据抓取协议**：优先读取 https://artificialanalysis.ai/data-api/docs/reference 所列当前接口（如 `GET https://artificialanalysis.ai/api/v2/language/models/free`，依套餐可选择 `/language/models`）；由本地合法 API Key 通过 `x-api-key` 调用，具体可见字段、速率和使用/再分发权限以运行时官方文档为准。免费 API 有综合 Intelligence/Coding/Agentic 等 headline 指数、价格及速度信息，但详细每 Benchmarks / 每 Effort 可能需更高级别，不得把缺失补算成已测。每次**能力快照脚本启动**尝试从网络重新抓取一次、清洗并原子保存新成功快照；保留已有成功快照与 `fetched_at_utc, source_revision, benchmark_version, original_metric_unit, model_stable_id, model_revision, exact_effort, evidence_kind, missing_mask, fetch_status`。失败（401/403/429/离线/字段缺失）不覆盖历史有效数据，也不将历史快照冒充当日新测；正式训练和 Task Episode 使用**固定的单一 snapshot ID**，不让每次模型生成请求调用榜单网站。只保留允许在公开 Git 仓库分发的数据/简要归属，授权不明的原始响应应本地忽略提交或仅保存元数据。

**实现归属**：沿现有 `our-project/code/src/modelrouter/providers/registry.py` 与已有数据准备/编码路径扩展，尽量复用而非创建第二份模型 Registry；由后续本地 Execution Agent 首次落盘并证实抓取成功，本次规划文档并未实际取得新的可训练数据、执行网络请求或批准 GPU 继续微调。轨迹教师仍使用两条固定 Train/Dev 成功摘要，无在线相似检索。

## 4. Cache 专用证据字段与标签边界

一条缓存相关训练记录必须区分**请求事实**、**缓存机会**、**模拟结果**及**真实计费结果**。

| 字段组 | 字段示例 | 来源与可信级别 |
|---|---|---|
| 连续消息上下文 | 当前目标、已发生消息/工具结果、context_tokens、重新发送上下文、额外 Token/费用 | 同一任务状态；观测与估计分开，不等于物理 KV 保存 |
| 前缀复用机会 | `timestamp, prefix_block_hashes, prefix_token_count, prior_model_id, session_key` | CACHE-001 OBSERVED_REUSE（匿名块标识相同只支持某条件下可复用） |
| 模拟命中 | simulated_cached_tokens、capacity、ttl_policy、eviction_policy、sticky_routing_assumption | CACHE-003 SIMULATED |
| 实际 API 缓存 | provider_raw_cache_read/write/hit/miss_tokens、response_usage_raw、model_revision、endpoint、request_id | CACHE-005 MEASURED，仅实际调用回报有效 |
| 本地缓存 | engine_version、tenant/salt、physical_prefix_cache_hits、request_tokens、evicted_blocks | CACHE-006 MEASURED，仅真实引擎实例观测有效 |
| 成本与约束 | pricing_version、cache_read_price、cache_write_price、expired_at、cache_scope、prefix_materialization_cost | 政策/账单证据，provider-specific |
| 预估与缺失 | estimated_prefix_overlap、cache_unknown_reason、source_quality | ESTIMATED 或 UNKNOWN，不能填进 MEASURED 列 |

**不能自动训练为真**：缓存命中百分比一定转化为等额成本折扣；不同厂商缓存键相同；换模型保留物理 KV；相同 Token 前缀必然同样命中；缓存 TTL 一律同值；已有 CCH/Blog 聚合能归因到某一 Agent 决策。

**上下文与缓存双记**：每个生成边界保留当前/上次逻辑及实际模型、端点、可观察上下文长度、历史是否重发和实际 Provider/引擎缓存 usage；切换额外 Token/费用单列。文本复用机会、估计、模拟和实际命中分别登记，缺少实测为 UNKNOWN。三 Alias 共用同一后端不能支持真实跨模型/Provider KV 共享或缓存节省结论。来源：下载讨论行 28761–28784。

## 5. 候选选择表（Selection Board）：先登记，再选，最后加工

本节专门留给今后负责人逐批确认**哪些数据源真正进入项目训练集合**。不在本轮代替负责人做最终选择。

| 数据组 | Planning 推荐优先审议 | 当前负责人的明确选择 | 当前状态/阻塞 |
|---|---|---|---|
| Agent 轨迹 | TRA-001、TRA-002 | **Q-007：第一学习阶段从公开 Agent 轨迹 A 开始**，未逐源批准 | 待逐源许可证/字段核验 |
| 模型选择 | ROUTE-001、ROUTE-002；辅助 ROUTE-003/004 | 未确认单独数据集 | ROUTE-001/002 许可待审，不得训练 |
| 缓存重用 | CACHE-001；CACHE-003 仅模拟 | 未明确逐源批准 | 真实性必须分层，不能把模拟命中当真值 |
| 长记忆 | MEM-003、MEM-001/002、MEM-004 | 未明确逐源批准 | benchmark 留出/版权/轨迹可用性待核 |
| 多 Agent | MAS-001、MAS-002、MAS-003 | 未明确逐源批准 | 任务/代码与现成训练轨迹区别尚待核 |
| 时间/预算 | TIME-001、TIME-002，重用 CACHE-001 | 未明确逐源批准 | 只有请求时延/资源时序，不等于完整任务预算 |
| Provider 政策 | POL-001～022，全覆盖、重点逐型号 | 仅确定 Q-002 混合 API+开源模型原则 | 动态来源表，具体真实合法动作池未确定 |
| 禁止训练 | ROUTE-005 | 不进入训练；用于只读研究分析 | 发布方明确限训 |
 
**后续 AI 每次提出数据源选择建议必须产出**：固定源 ID、官方 URL、revision、许可证据（可训练/禁止/待核）、拟覆盖状态组、能得到的真实标签类型、与已有源重叠和未来信息泄漏风险、优先级理由、推荐状态；用 Q-ID 交由负责人确认。不能把 Planning 推荐写成最终已批准，也不能默默扩大 API 费用或训练权限。

### 5.1 选择决策记录（待批准）

| 日期 | Source ID | 用途（轨迹/静态选择/模拟/分析/评测） | 选择 A/B/C/排除 | 负责人/Q-ID | 证据/影响 |
|---|---|---|---|---|---|
| — | — | — | **待确认** | — | 尚无逐数据源批准 |

## 6. 数据清洗与 AI 交付规范（待下一阶段授权执行）

**本节规定未来 Execution Agent 的数据质量要求，不授权实际运行。** 必须先通过负责人对来源、下载范围、许可证和执行环境的批准。

1. **许可与溯源**：为每源生成 manifest（source_id、repo/revision、license/evidence、下载时间、checksum、是否允许 train/redistribute、原始字段表）；不明许可/商业 API 输出归属必须隔离，禁训源不得形成蒸馏标签。
2. **Raw immutable**：保留原始文件只读及版本；不覆盖旧 CCH、Blog 的 source/、cleaned/、summaries/；将来要决定物理 raw/normalized/processed 路径应基于现有 data 目录唯一扩展，不建 parallel v2/v3 pipeline。
3. **样本单位统一**：task_id/repo_id、episode_id、agent_id、step/decision_id、model_revision、source_id、observed_at；静态 routing 任务、长 Agent episode、KV workload 请求、资源时间事件分别登记**不同粒度**，不强行跨源拼接不存在的任务 ID。
4. **先隔离再展开**：按任务、仓库、数据源系列与近重复任务分组，先固定 train/val/test，再从 train episode 生成前缀状态；同任务的多个模型、所有前缀、补丁与最终结果不得跨 split；新模型/新 Provider benchmark 的测试来源另做冷启动留出。
5. **严格决策前截断**：只允许时间 t 已观察的上下文/工具/测试/记忆版本、剩余预算与硬约束进入 Kev 输入；未来的成功标注、最终 patch、未来 Token 总量、未来缓存命中和后续恢复循环只能保留在 Outcome 中。
6. **缺失与语义层级**：所有字段保留 measured/observed_reuse/simulated/estimated/unknown；实际 cache 用量、模型 effort 支持、合法动作可用性、成本货币单位必须有可追溯出处，禁止人工以零或假定值填满。
7. **标签分层**：真实 observed_resolved / 可信 observed_cost_to_go / 同静态 prompt 的多个 model_score / 同任务偏好 / 已知硬规则 legality / 模拟 cache hit，分别存表与标签 origin；从一个执行轨迹**不能**把未执行候选标成失败或成功。
8. **Kev 训练视图**：仅对有真实有据标签的样本转换 noul（yes/no）、score（顺序等级）、choice（合法动作或真实可比选择）格式；保留 source_id、split、label provenance、candidate_set_version、weight、任务 ID；随机变化选项顺序并核对模型名称捷径。
9. **AI 自动化边界**：AI 可提议字段映射、许可证待核清单、错误分布、异常/近重复候选与预处理规则；真实删除、覆盖、把 UNKNOWN 升级成 MEASURED、改变任务分割、打开商业 API、部署 GPU 或启动训练，必须有获批的明确计划与可追溯变更记录。不得让 AI 自行生成来源不明的“最优模型标签”。
10. **数据验收报告**：按 source 与八组状态汇总覆盖率/缺失率、标签可追溯率、合法模型×effort 覆盖、可用任务数（prefix 行数另列）、任务/仓库去重、时间泄漏、训练/评测集污染、价格版本和 license 白名单，最后产出“可训练、仅分析、暂隔离、禁止训练”清单。

### 6.1 未来 AI/Execution Agent 的审计输出模板

| 项目 | 必须给出的结果 |
|---|---|
| Source identity | source_id、URL、revision、license、usage permitted、原始散列值、父数据源 |
| Content | task/episode 粒度、真实字段、各类标签、缺失字段、是否独立数据源 |
| State coverage | 八组 state 每组有哪些 measurable、estimated、missing，以及出处 |
| Routing comparability | 同静态题多模型？同 Agent 中途状态多候选？有没有真实 Effort？ |
| Cache fidelity | 实际缓存用量 vs 可重用前缀 vs 模拟命中，是否可以用于成本标签 |
| Privacy/contamination | 私有文本/凭据/许可证、跨任务/仓库重复、评测污染 |
| Recommendation | 选用、仅分析、等待许可、排除；理由与未来最小动作 |
| Execution evidence | Git/数据 SHA、运行环境与命令、输出路径、完整性结果；**未执行必须写未执行** |


### 6.2 官方数据卡只读核验：第一批候选和字段差异（Planning 推荐，不代表批准）

2026-10-09 查阅下列官方数据卡、Viewer、README 及 Kev 官方标注格式；**未下载数据、没有原始样本统计结果，也未审核所有许可证**。优先保证不同训练任务需要的真值类型，不为了把八组变量全部填满而错误拼接不相关数据。

| 来源 ID | 确认的原生数据及字段 | 具体清洗注意点 | 第一轮建议 |
|---|---|---|---|
| TRA-001 Open-SWE-Traces | 官方 v1.0 数据卡列 instance_id、repo、trajectory_id、trajectory、tools、resolved(-1/0/1)、metadata.reference_patch/model_patch；后续 v1.1/v1.2 已扩容 | 按 source revision/config 兼容 trajectory/messages；reference_patch 是标准答案，仅能做标签/审计，**不得进入决策输入**；-1 是 unknown 不是失败；同 task/repo/相似实例分同侧 | **P0 核心状态源** |
| TRA-002 SWE-smith trajectories | 数据浏览器现列 messages、instance_id、resolved、model、traj_id、patch，且有多个 split；卡片特指 5,017 条训练子集但浏览器另展示多组数据 | messages 可能是 JSON 文本；区分实际执行 patch 与 gold patch；最终 patch 不可在前缀出现；**按具体 split/源模型/instance 核实后选取**，不要混同全部 76k rows、5,017 子集和 52k 任务 | **P0 互补 Agent 轨迹** |
| CACHE-001 Mooncake FAST25 | 官方 JSONL 示例字段只有 timestamp(ms)、input_length、output_length、`hash_ids`（512-token remapped prefix block）；toolagent/会话真实请求与 synthetic 分开 | 散列值可算真实请求的可复用前缀机会 OBSERVED_REUSE；**没有真实 API cache_read_tokens、模型 ID、任务 resolved 或单次响应时延**；在设定缓存容量/TTL/LRU 后只能生成 SIMULATED 标签 | **P0 Cache 数据源** |
| ROUTE-004 Arena Human Preference | 官方数据卡 Apache-2.0，同一 query 的双模型人工胜负/平局偏好 | 两模型身份/响应与 winner / tie / both-bad 按原 schema 规范化；**偏好不等于 Agent resolved**，旧型号不可冒充当前部署 | **P0 静态比较底座** |
| ROUTE-001 LLMRouterBench | 官方描述 33 模型/21+ 任务数据集的 score、prompt_tokens、completion_tokens、cost；结果按 dataset/split/model/time 分层 | **预先核验结果包及各上游许可**；按同 query、同 benchmark、同评分器、同 shot/版本对齐候选，不能混用不同评价指标的原始 score | **P0 研究优先，许可证未核前不训练** |
| ROUTE-002 RouterBench | 同 prompt 多模型性能/估计费用、有 0-shot 和 5-shot 两套 | 数据卡缺明确 license；不同 shot 不能同组；估计费用不当作真实账单 | 许可待核候选 |
| ROUTE-003 TwinRouterBench | 970 rows，messages JSON、step_index、target_tier（四档）等；**不含具体 model target** | 不能将 target_tier 硬映射为 model×effort；最好保留为独立基准，训练用途需提前锁定且防污染 | 评测优先 |
| TIME-001 BurstGPT | 官方 README 有 Timestamp、Session ID、Elapsed time（整次响应非 TTFT）、Model、Request/Response tokens、Log Type | 带失败与 without_fails 文件彼此重叠；不能相加，且失败 API 请求不等于失败 Agent 任务 | 时间/会话辅助 |
| MEM-003 LongMemEval-V2 | Web/企业 Agent 多次长历史、问答证据及时间，官方项目提供检索与记忆评测接口 | 未来问答答案不可泄露到当前 Agent 状态；优先用作 Memory/摘要评测，训练许可和保留集另审 | Context/Memory 参考 |
| MAS-001 MARBLE | 多 Agent 任务、角色、拓扑、协作/通信环境 | 代码和任务不保证有已许可的每步训练轨迹，不能凭任务构造最优模型标签 | 协作环境/Schema |

参考：[Open-SWE](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/blob/main/README.md)、[SWE-smith](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories)、[Mooncake](https://github.com/kvcache-ai/Mooncake/blob/main/FAST25-release/README.md)、[LLMRouterBench](https://github.com/ynulihao/LLMRouterBench)、[BurstGPT](https://github.com/HPMLL/BurstGPT)、[Kev format](https://github.com/jaredpalmer/kev/blob/main/skills/kev-finetune/references/data-format.md)。

**当前最低必备数据能力组合**：真正 Agent 状态与 resolved（TRA-001，TRA-002 辅助）；合法静态比较（ROUTE-004）；缓存复用机会（CACHE-001）；真正同题性能/成本路由比较（ROUTE-001 待许可核验，核验失败则必须留缺口，不能用其他数据伪造）。Provider 模型/effort/缓存/价格规则取 POL 动态证据快照，不是固定训练语料。全部为 Planning 候选，**负责人还未逐源作最终选用决定**。

### 6.3 源到训练数据的唯一清洗处理路线（尚未执行）

1. **S0 来源许可与原始数据固定**：source_id、官方 URL、revision、license、第三方原始模型生成内容的训练权、可再分发范围、文件散列值、原始字段、数据发布拆分；未知许可证先隔离。不得把多来源拼成一个并不存在的完整 Agent episode。
2. **S1 源专属归一化**：分成五种实体，不强行统一为一张表：AgentEpisode（task/agent/steps/model/resolved）；StaticModelOutcome（prompt/候选/真实同题 score/费用及 benchmark）；CacheWorkloadRequest（timestamp/长度/有序 `hash_ids`）；MemoryOrMASBenchmark（上下文/协作任务与真答案）；ProviderPolicySnapshot（endpoint/model/revision/实际合法 effort/价格/TTL 与证据有效期）。
3. **S2 去重与切分**：按数据源系列、task/repo/issue/near-duplicate 筛出同一个 leak_group；先分 train/val/calibration/test，再把 Agent episode 在每次真实 model call 的决策前时点切为 prefix。已公布正式 benchmark 需要另留出集，**官方 split=train 并不自动保证不会污染我们的测试题**。
4. **S3 八组状态重建**：仅使用决策时刻之前的 Task/Subtask、Agent/Coordination、Context/Memory、Tool、Verification、Cache、Temporal、Provider 信息；每字段记录 observed_at、MEASURED/OBSERVED_REUSE/SIMULATED/ESTIMATED/UNKNOWN 与来源。不能读取未来 patch、最后 resolved、未来总 Token/缓存或未发生的测试。
5. **S4 标签溯源**：把已执行动作的 terminal resolved 和可核 cost_to_go；同静态 query 的 model-score/人工偏好；确定性合法性规则；Mooncake prefix reuse/模拟 cache 单独存为不同监督域。没有相同决策前状态的未选动作真实结果时，**绝不生成所谓最优 Model×Effort 标签**。
6. **S5 Kev 训练样本**：保留原始多表与 provenance，另导出一个最终 Kev JSONL 视图。官方记录为 state + questions，type 为 noul/score/choice，label 必须具有证据；候选字符串与实际可执行动作一致，source/task/split/evidence 外置记录映射。**官方通用 fine-tune 指南的记录总长度上限为 2048 tokens**，不能直接投入几十万 Token 的完整轨迹。真正提供给 Kev 的是决策前摘要，状态要短且来源可复查；默认 split_data.py 只分组 exact state，不替代本项目 task/repo 去重。
7. **S6 验收**：先审来源许可证、数据分割无污染、八组状态覆盖和 missing rate、真实标签/有效模型×effort 数、cache 测量层、成本单位/价格快照、输入长度、JSONL 格式、任务权重、raw→normalized→training 的可逆索引。只有真实通过才把每个 Source 从候选改成 TRAIN_READY；数据量留到清理阶段决定。

**重要原则**：不同来源通过共享模型学习**不同监督任务**，不通过按行联表“补齐缺失的八组状态”。例如 Mooncake 的缓存重用概率可作为单独训练任务，不能作为 Open-SWE 某条完全不相关 Agent 轨迹的真实缓存命中值。

### 6.4 模型训练四阶段建议（Q-010/Q-011 仍未由负责人批准）

| 学习阶段 | 可用训练视图 | 训练到什么程度 | 仍无法证明 |
|---|---|---|---|
| M1 Agent 状态、已执行动作结果 | TRA-001/002 的真实决策前状态与 terminal resolved；费用分档依据实测用量×适用官方价，供应商bill另列 | Kev noul 观察性结果预测；部分确定规则辅助 | 不能推出其它候选模型实际更好 |
| M2 静态任务/模型能力与辅助缓存 | 已许可的 ROUTE-004 与 ROUTE-001/002；Mooncake 缓存潜力和可核政策规则分别做 typed 任务 | choice 同题比较与能力先验、score/noul 缓存复用任务（只对对应真实/模拟标签） | 不能证明动态 Agent 中途切换模型的因果效果 |
| M3 动态 Model×Effort | **未来同状态可恢复分支**中多个真实动作的 task resolved、cost_to_go、实际 cache/预算变化（当前无现成充足数据） | 才能训练 Agent 决策边界上有根据的 choice 最佳合法动作 | 没有此数据时不得声称学到最优 runtime router |
| M4 校准与验证 | 任务、仓库、模型系列和 Provider 版本留出；实际合法候选池、最终 task 成功与整任务费用 | 受成功率约束的选择、概率温度和不确定性、cost/resolved 及消融 | 一次请求的节省不等于整任务减少成本 |

官方 [Kev-4B model card](https://github.com/jaredpalmer/kev/blob/main/docs/model-cards/kev-4b.md) 说明已训练权重可用 LoRA continuation；实际初始化、训练 loss/超参、采样、GPU 和运行许可还属于尚待讨论的 Q-010/Q-011，**本阶段不启动训练**。

### 6.5 文档职责审计：不要新增第六个核心研究文档

当前 GitHub main 只读文件树：共 **210 个跟踪文件，其中 44 个 .md，活跃核心为 5 份**（Status、Q&A、Memory、Research、Registry）；另有历史 IMPLEMENTATION_RESEARCH 与导航 README。五份文档职责不同，**没有必要再创建 DATA_CLEANING_PLAN.md 或新的训练目录文档**。实际冗余是旧 Q&A Q-007-R1/R2、Research 与 Memory 重复摘录数据集清单/政策细节，而 Registry 已是唯一新版本权威源。建议以后只更新 Registry 最新数据和政策、Q&A 仅保持负责人逐源决策及历史、Status 仅保持当前任务、Memory 仅新增交接变化、Research 仅在方法/证据本质改变时更新。历史笔记可保留不删除，后续如需精简应先确保决定及来源无信息损失。

### 6.6 本轮服务器公开数据清洗位置与真实进度（2026-10-09）

2026-10-09 负责人明确指定服务器承担公开数据下载、CPU 清洗和完整数据保存，本机不再承载大规模原始公开轨迹。优先 Open-SWE-Traces、SWE-smith、Arena 55k、Mooncake FAST25；TwinRouterBench 留独立评测，LLMRouterBench 需核训练许可与字段。这是**执行者待回报的工作**，不是已完成数量。历史服务器 E0 80核/376GiB/A6000/约1.2TiB 的数值仅为历史审计。
根目录拟议为服务器当前用户自有 $HOME/路由/，新增 data/公开数据/原始数据、清洗数据、清洗报告、数据预览，另 data/kev/公开数据、实验结果/Kev-4B、日志、.venv；本机保留既有 Git 和 Blog/CCH 输出，只回收轻量清洗报告。新研究目录和 Markdown 中文，Python/第三方原名英文；仅扩展唯一 prepare_router_data.py，禁止重复 v2/v3 pipeline。
先于正式训练报告每源原始/有效记录数、task/repo/query 唯一数、决策前状态覆盖、真实/未知/静态偏好/OBSERVED_REUSE 各标签数、train/val/test 数、过滤原因、存储占用与实际执行耗时。现有 Blog/CCH Execution 自报 221,128→178,621 行是**调用级历史动作**，绝不是该数量的最优路由标签。GitHub 只能推代码/中文报告/公开少量样本，原始和完整训练大数据留服务器；服务器 GitHub 可写身份须由 Execution 实测，不记录任何密钥。
本机并行文献库任务由 PLANNING_MEMORY §9.19 和 RESEARCH_OVERVIEW §6.4 管理，此数据 Registry 不另复制论文清单。

### 6.7 首批服务器清洗执行证据与 TRAIN_READY 科学定义（2026-10-09）

**当前完成范围为数据读取+转换，有效监督验证尚未完成**。Execution 提供主分支 966f582 代码、轻量预览和《公开数据清洗报告》：Open-SWE/SWE-smith 首分片合计 5,729 条轨迹中提取 20,000 step；Arena 57,477 原始行前部抽取 30,000 有偏好标签记录；Mooncake 两类 39,632 请求中抽取 30,000；TwinRouterBench 970；LLMRouterBench 只索引约 30 个任务目录，无同题模型 outcome。服务器生成混合 Kev train/val/test 57,165/12,123/11,682，总 80,970 行。Planning 已核 GitHub 代码与 50 条预览，完整服务器数据和源许可仍须实际核对。
**需要纠正的标签**：Agent complexity/effort/cache 主要由 step/errors/step>1 规则给出；Arena 人类 winner 真实，但 effort/cost/cache 派生值不是实测，且 Kev state 仅 prompt_chars 没有 Prompt；Mooncake block reuse 是 historical-prefix opportunity，cache affinity 是同一 hit ratio 的规则映射，绝非实际 KV residency；TwinRouterBench 是 benchmark tier 不是具体 `(model,effort)`。训练标签须按 observed terminal outcome / static human preference / cache workload / controlled action comparison 分开记数。
**数据划分**：原脚本按 trajectory/task_session_id 将四种任务混合切分，不能直接宣称独立 Agent task/repo holdout；在提取 Assistant 当前响应前截取状态；禁止将 TwinRouterBench 参与训练；同题反事实性能尚无可信数量。
**Kev 兼容**：官方 labelled record 是 `state` 和 `questions`；choice 的 `criteria` 为 option-name→description object、`label` 为 option-name；score 的 `criteria` 为有序列表、`label` 为 int 0 起；当前脚本用 options/levels/字符串 score.label，不能认为可直接训练。来源：https://github.com/jaredpalmer/kev/blob/main/skills/kev-finetune/references/data-format.md。
**唯一下一项**：保留原脚本，快速更正各源数据归类、可信标签和 split；按真实来源打印每类可训练监督数量，做官方简单 validate，再继续第一轮 LoRA 方案，不新增第二套管理链。

### 6.8 公开数据重建成果科研复审与本轮执行纠偏闭环（2026-10-10）

> **2026-10-09 Planning 二次审查结论**：确认 1,681,177 行历史差额、未全量下载、时序递增错误、模型误标、SWE-smith 全为 text_response、AgentSuite 缺少跨模型对齐键、Mooncake 缓存无序交集与未来步数泄漏。
>
> **2026-10-10 Execution 本轮纠偏执行闭环**：
> 1. **历史差额根因澄清与数字统一**：查明此前为 TRA-001/002/004 将步数误填为轨迹数所致。本轮扩充并重算后，**16 源 `字段统计.json` 汇总数（6,600,628 步/条）与服务器物理文件实际 `wc -l` 绝对一致，差额彻底归零**。
> 2. **下载覆盖扩充**：TRA-001 扩充至 12 分片（2.3 GB，2,075,629 步）；TRA-002 全量覆盖 ticks/tool/xml 全部 24 分片（3.0 GB，2,331,584 步）；TRA-004 全量覆盖 30 个模型（161 MB，41,430 步）；MEM-005 扩充包含 ama_bench 与 membench（23,884 条）。
> 3. **代码级科研缺陷彻底修复**：时序严格后置递增；Open-SWE 保留 Qwen3.6/3.5/3.8/DeepSeek/MiniMax 真实模型名；SWE-smith 真实识别 125.6 万次 `str_replace_editor`、90.1 万次 `bash` 与 12.2 万次 `submit`；AgentSuite 以 `meta.id` 对齐 273 个独特任务实例并输出同题跨模型审查组；Mooncake 严格按时间戳排序并计算 LCP 连续前缀且抽取连续 35 请求；TwinRouterBench 移除未来 `total_steps`；LongMemEval-V2 载入 451 道真实题目与答案；全源引入 `compute_field_missingness()` 动态计算缺失率；`prepare_router_data.py` 增加 `--mode public`。
> 4. **GitHub 审查样本与统计同步**：全部 16 组轻量审查样本与动态统计已同步至 GitHub，供 ChatGPT 通过 GitHub MCP 开展验收。

### 6.9 Q-007 全量重建后的数据监督科学验收（2026-10-10）

- **2026-10-10 Planning 对提交 `0b39a7e` 的三次科研独立复审：** 已核 GitHub 16 份字段统计，按来源求和确为 **6,600,628** 条不同粒度记录；14 个来源含实际审查样本、CMU/MARBLE 两个受限为零。Execution 报告服务器 `wc -l` 与统计相同，但 Planning **未亲自登录服务器复核完整清洗文件**；不能把总量解读成模型路由监督数量。
- **已确认修复**：`--mode public` 存在且与 Blog/CCH 分离；TRA-001 当前调用工具未提前计入 `prior_tool_calls_count`（第一步=0）；模型名从 metadata 优先提取；TRA-002 增加动作解析；TRA-004 使用 meta.id 对齐 273 个任务；CACHE-001 按 timestamp 排序、按有序前缀链计算复用潜力、output_length 移到事后；TwinRouterBench 的 total_steps 从决策前状态移出；LongMemEval 增加问题/答案；MEM-005 扩展四子集。SWE-smith 官方 ticks/tool/xml 各 8 个 shard，当前 24 分片与官方 metadata 一致；AgentSuite 官方 30×273=8,190 episode，当前覆盖 30 配置。
- **仍未验收的科研缺陷**：(1) AgentSuite `pre_decision_state` 包含 `meta.target_question` 和 `meta.pass_criteria`，未证明是执行时可见字段，可能注入事后评测 rubric；同题跨模型为 **Episode 级**反事实近似，不等于同一个中途 state 的模型切换结果，thinking-on/off 不能无条件跨 Provider 标准化。(2) SWE-smith `extract_swesmith_action()` 从 Markdown 代码块首词推断动作，动作分布出现 `the`、`this`、`2.`、`pip`，不能把所有识别记录都叫真实 Tool API 调用。(3) Mooncake 有序前缀只证明历史复用机会，任意丢弃缓存前缀集合的策略不是确定性物理缓存容量/TTL/命中。(4) 缺失率以各源 35 条 GitHub 抽样 `sample_records` 计算，不能声称完整数据集精确缺失率。(5) LongMemEval `initial_memory_snippet` 仍是形如 `f224a4eb` 的散列字符串，没有承载有效历史语义。(6) LLMRouterBench 单模型观察标签标为 `POST_HOC_BENCHMARK_ORACLE`，但最优模型尚需按同题完整评分和成本目标计算；并无 task/repo 完整 split 或 Laya/Kev 正式训练文件。(7) Open-SWE 仍为 12 代表分片（字段统计明标 PARTIAL），不能称全量官方覆盖。
- **下一步唯一科研工作包**：保留已有正确原始文件，继续在 `prepare_router_data.py` 修复这些语义缺陷；补充按任务 ID 的 episode/candidate 对照和稳定分组划分；从全部输出计算缺失率，不用预览代表全量统计；按来源/监督类型清点真实可训练样本；明确 Retriever/ModelRouterBench 的许可及真实测量单位。对 Laya-421M 与 Kev-4B 采用同一清洗视图、同一独立测试集比较，尚未固定唯一骨干，也**不启动正式微调**。

### 6.10 Q-007 科研数据收尾、统一训练视图与 Kev 任务级划分闭环（2026-10-10）

- **执行 Agent 闭环成果**：
  1. **全量流式缺失率追踪 (`StreamingFieldTracker`)**：覆盖全部 6,600,628 步/条记录完成 100% 流式扫描，核心字段总体非空率 99.9993%（仅 SWE-rebench-V2 存在 0.14% 题目缺失）；彻底取代 35 条抽样估算。
  2. **决策前状态无泄漏自检**：AgentSuite 移除 `target_question` 与 `pass_criteria`；LongMemEval-V2 注入 1,870 条任务目标真实语义；TwinRouterBench 移除未来 `total_steps` 并强制 `EVAL_BENCHMARK_ONLY`。
  3. **真实动作与时序前缀规范**：SWE-smith 严格实现 `EXPLICIT_TOOL_API`、`INFERRED_COMMAND`、`TEXT_RESPONSE` 三分类并剔除停用词；Mooncake 严格基于时序 LCP 连续前缀组织并标明 `HISTORICAL_PREFIX_REUSE`。
  4. **统一模型选择训练视图与 Kev 官方格式导出**：
     - 整合 ROUTE-004 (Arena 55k 39,716 场明确胜负)、ROUTE-001 (LLMRouterBench 26,368 题多模型对比)、ROUTE-002 (RouterBench 35,189 题官方 Oracle 对比)、TRA-004 (AgentSuite 273 独立任务成对对比)，提取 **100,372 个独立路由任务**，输出为标准 Kev `{state, questions}` 格式样本；
     - 按任务 ID 进行 **80% 训练集 (80,343 条)、10% 验证集 (10,053 条)、10% 测试集 (9,976 条)** 确定性散列物理隔离，**跨集重叠为 0**；
     - **TwinRouterBench (970 步)** 导出为独占外部评测集 `data/kev/公开数据/test_twinrouterbench_holdout.jsonl`，在训练/验证集中 **0 步进入**。
  5. **审查样本与报告闭环**：5 份轻量训练视图样本与 [科研数据收尾报告.md](科研数据收尾报告.md) 全部同步至 GitHub，完备应答 9 类确切统计指标。

### 6.11 Q-007 训练视图最终科研纠偏与 Kev Schema 全量验证闭环（2026-10-10）

- **定向科研纠偏与真值对齐执行完毕**：针对 Planning 对提交 `cb83127` 的最终复审，Execution Agent 在唯一入口 `prepare_router_data.py` 中直接完成定向纠偏并在 GPU 服务器验证通过：
  1. **Thinking 对照真值校正**：彻底删除 `max(16, contrasts)` 人为下限代码，严格按照基础模型清点。确认 AgentSuite 30 个配置中仅存在 **6 组真实同基础模型对**（DeepSeek-V3.2-Exp, claude-4-opus, claude-4-sonnet, claude-4.5-sonnet, gemini-2.5-flash, Qwen3-235B-A22B-2507-FP8），全 273 任务合计 **1,638 组成对 Episode**；其余 18 个单向配置单独标注；中途反事实分叉数量确认保持为 **0**。
  2. **AgentSuite 最佳动作纠偏**：清查 273 任务，确认 8 个全败任务排除；19 个任务存在唯一最优动作（`UNIQUE_WINNER`）；246 个并列成功任务中，所有成功模型执行步数完全相同（如均为 7 步）且成本未测量。坚决废除“默认首个模型为最优”的做法，在元数据中如实保留 `winner_status: "TIED_SUCCESS_UNDIFFERENTIATED"` 与全部并列模型，标记 `cost_status: "UNMEASURED"`。
  3. **LLMRouterBench 质量与成本监督**：剔除 4,327 条 `score is None` 记录；区分 384,431 条实测商业 API 美元费用与 163,628 条本地未计费模型（标记为 `UNMEASURED_OR_LOCAL_FREE`）；以 `completion_tokens` 作为本地模型成本代理；明确标注 2,744 道全败题目与 22,458 道正向成功题目。
  4. **RouterBench 移除防报错补丁**：删除 `if oracle not in criteria: criteria[oracle] = ...` 代码；实测 35,189 题中 Oracle 100% 存在于候选池；1,308 道 `no_model_correct` 题目严格剔除。
  5. **TwinRouterBench 4 级映射修复**：补齐 `mid_high` 映射为 `low (0)`, `mid (1)`, `mid_high (2)`, `high (3)`，彻底消除 219 处校验错误。
  6. **任务数严格对齐与高置信子集**：
     - 原始未过滤各源候选总数：**101,688**
     - 剔除无解不可路由任务：**- 1,316** (RouterBench 1,308 + AgentSuite 8)
     - 多模型候选池总数：**100,372** (进入 80/10/10 划分)
     - 高置信确定性单一胜者正向监督子集：**97,382** (Arena 39,716 + RouterBench 35,189 + LLMRouterBench 正向 22,458 + AgentSuite 唯一 19)
     - 无区分度/全败子集：**2,990** (LLMRouterBench 全败 2,744 + AgentSuite 并列 246)
  7. **全量内置 CPU Kev Schema 校验 100% PASS**：对训练集 (80,343)、验证集 (10,053)、测试集 (9,976)、TwinRouterBench 独占评测集 (970) 共 **101,342 条样本**逐行逐字段内置校验，**0 处错误，100% 合规**！

Registry 共登记 31 个来源编号，本轮有 16 个来源目录，不代表 31 个来源都已下载；其中有部分运行时/Provider 政策、模拟源，不等于独立可下载公开数据集。全量与否必须以具体官方配置和 shard 名单判定。

### 6.12 Q-007-FINAL 数据资产定版、可复现性核验与 Kev/Laya 官方代码兼容性闭环（2026-10-10）

- **1. 全量资产盘点与机器可读 Manifest 固定**：
  - 生成并同步唯一权威清单 [manifest.json](公开数据/manifest.json)（同时保存于服务器 `data/公开数据/manifest.json`），完整覆盖全部已登记 Source ID（`TRA-001..004`、`ROUTE-001..005`、`CACHE-001..006`、`TIME-001..004`、`ENV-001..003`、`MEM-001..006`、`MAS-001..003`、`SYS-001`、`OWN-001..003`）。
  - **原始公开数据（只读保留）**：服务器 `data/公开数据/原始数据/` 下 14 个有效来源目录、**789 个文件**、**17,869,335,210 字节（17.87 GB）**，逐目录计算 SHA-256 树散列。
  - **清洗后标准数据**：服务器 `data/公开数据/清洗数据/` 下 14 个 JSONL 文件、**6,600,628 行**、**6,401,154,316 字节（6.40 GB）**。
  - **自有生产数据（双向同步固定）**：`OWN-001`（`cch-model-cost-cache-statistics.csv`，87,057 B，110 条数据行）、`OWN-002`（`sxyq-blog-gpt-usage-cleaned.csv`，34,738,033 B，221,128 条脱敏记录；未脱敏原始文件因含 IP/Key 隐私标记为 `RAW_MISSING`，以脱敏版作为固定权威源）、`OWN-003`（`cch-sxyq-gpt-unified-summary.csv`，25,424 B，79 条汇总行）在 GitHub 与服务器 `our-project/data/` 完全一致。
  - **双遍确定性可复现核验（PASS）**：对 6 个代表性源从原始文件执行双遍重跑，输出 SHA-256 与正式清洗文件 100% 逐字节一致；对 `prepare_router_data.py --mode views` 执行双遍独立目录重跑，生成的 15 个视图文件在两次运行间及正式文件间 SHA-256 100% 逐字节一致。
- **2. 路由监督标签最终净化（消除并列伪单胜者）**：
  - **LLMRouterBench（25,202 题）**：严格拆分为 5 类成本—质量状态：`UNIQUE_MAX_SCORE`（**1,432** 题）、`TIED_SCORE_MIN_MEASURED_API_USD`（**7,954** 题）、`TIED_SCORE_TIED_API_USD`（**86** 题）、`TIED_SCORE_COST_UNCOMPARED`（**12,986** 题，含 `cost == 0.0` 未计费开源模型与最高分并列）、`ALL_MODELS_FAILED`（**2,744** 题）。
  - 将 **13,072 题**（`12,986 + 86`）同分但成本不可比或美元成本并列的题目移出单胜者监督训练集，转入 `analysis_unsupervised_or_tied.jsonl`（同时保留 `tied_winners`、`target_distribution` 与均匀软标签 `gold`/`target` 供多标签/软目标研究）。
  - **最终严格唯一单胜者监督训练集（84,310 题）**：
    - `ROUTE-004` Arena 人类盲测唯一胜者：**39,716** 题（`HUMAN_PREFERENCE_WINNER`）
    - `ROUTE-002` RouterBench 官方正向唯一 Oracle：**35,189** 题（`BENCHMARK_QUALITY_COST_ORACLE`）
    - `ROUTE-001` LLMRouterBench 严格唯一胜者：**9,386** 题（`1,432 UNIQUE_MAX_SCORE + 7,954 TIED_SCORE_MIN_MEASURED_API_USD`）
    - `TRA-004` AgentSuite 唯一成功模型：**19** 题（`OBSERVED_EPISODE_UNIQUE_SUCCESS`）
  - **无区分度/并列/全败分析集（16,070 题）**：LLMRouterBench 15,816 题（`12,986 + 86 + 2,744`）+ AgentSuite 并列 246 题 + AgentSuite 全败 8 题。
  - **Thinking-On/Off 对照视图**：同基础架构成对 Episode 共 **1,638 条**（其中 **5 组严格同一权重运行时开关 × 273 任务 = 1,365 条**；**1 组同底座同版本专用 Thinking 权重 `Qwen3-235B-A22B-Instruct-2507-FP8` vs `Thinking-2507-FP8` = 273 条**）；另有 **6 组跨版本/跨变体对照 = 1,638 条**单独统计。
- **3. 跨划分零泄漏修复（PASS）**：
  - 修复短 Prompt（`< 15` 字符）及句末标点变体未走语义散列分桶的问题，对全部非空 Prompt 采用标点归一化 `canonical_prompt` 散列分桶：
  - **Train**: **67,428**（80.0%）｜**Val**: **8,436**（10.0%）｜**Test**: **8,446**（10.0%）｜**Holdout (`TwinRouterBench`)**: **970** 步。
  - 实测 `train_val_task_overlap = 0`、`exact_prompt_overlap = 0`、`canonical_prompt_overlap = 0`、`cross_source_prompt_split_leakage = 0`。
- **4. 官方 Kev 与 Laya 仓库真实代码 100% 兼容验证（PASS）**：
  - 优化 `criteria` 为空描述字典 `{m: ""}`（由官方 `kev.api.option_text` 与 `laya.common.render_options` 原生渲染纯净模型 ID）并补齐顶层 `"expected"` 字段，使同一份 JSONL 同时原生兼容两套官方仓库：
  - **Kev 官方 (`kev.data.load_records -> materialize -> kev.model.encode`)**：全量 85,280 条样本（84,310 监督 + 970 Holdout）100% 通过，`max_state_tokens = 352`、`max_branch_tokens = 466`、`max_packed_tokens = 767`，在默认（`384/1024/2048`）与 Kev-4B（`7552/8192/9216`）下均为 **0 截断、0 溢出**。
  - **Laya 官方 (`laya.train.read_data -> items_from_rows -> build_sequence`)**：在路由训练配置 `max_len=1024, head_max_len=448` 下全量 85,280 条样本 **100.0% 零跳过通过（`skipped={}`）**（注：Laya 出厂默认 `head_max_len=192` 因 `192 // 38 = 5 tokens/option` 会跳过 1,734 条 30~51 候选长选项样本，故正式训练与评测统一显式传入 `max_len=1024, head_max_len=448`）。

### 6.13 全量数据分层使用与目录方案（2026-10-10 Planning 提案，待执行核验）

**为何不能只训练 84,310 条**：该数字是静态/整任务单胜者选择标签总量，包含尚未最终对账的训练、验证、测试拆分，并非全体训练数据或八组状态的证明。现有 14 个清洗公开数据源共 6,600,628 条混合记录：
- Agent 轨迹 4,448,643 条：TRA-001 2,075,629 + TRA-002 2,331,584 + TRA-004 41,430。可研究观察到的执行动作、任务进度、工具结果和有依据的任务终局；决不能按步复制终局标签并制造每步最佳模型标签。
- 路由比较与参考 649,207 条：ROUTE-001 548,059 + ROUTE-002 36,497 + ROUTE-003 970 + ROUTE-004 57,477 + ROUTE-005 6,204。其中多次模型评估要按**独立题目与候选集**聚合；TwinRouterBench 只用于外部评测，FindingTheRightFit 只用于分析。
- 缓存/时序 1,443,926 条：Mooncake 39,632 + BurstGPT 1,404,294。用于请求负载、前缀复用潜力与缓存实验参数，不能冒充同一 Agent 决策的实测缓存命中。
- 任务/记忆 58,852 条：SWE-Gym 2,438 + SWE-rebench-V2 32,079 + LongMemEval-V2 451 + MemoryCraft 23,884。用于任务环境、验证和记忆评测，不得任意构造跨模型胜者。

**建议依次处理的训练/研究视图（复用现有唯一脚本与正式划分，不新增第二套主链）**：

| 用途 | 主要真实数据 | 当前监督边界 | 下一步 |
|---|---|---|---|
| 第一层：静态模型选择 | Arena/RouterBench/LLMRouterBench/AgentSuite | 84,310 道有单一胜者的任务（总数含验证、测试）；16,070 道并列或全败题另留分析 | 先对账并按来源/难度/候选数核对偏差；若需质量分数或多胜者学习则单独定义目标，禁止伪造唯一最佳 |
| 第二层：Agent 执行状态 | TRA-001/002/004 | 已执行动作和部分终局是真实观察；未执行的其他动作没有结果 | 按任务/仓库先隔离，再按任务均衡抽取决策前状态；核对时间信息泄漏，报告有终局/无终局比例 |
| 第三层：Thinking/Effort | TRA-004 | 目前统计称 1,638 组候选对照，含不同 Qwen checkpoint 的 273 对；另有跨 Gemini 变体对照，均非中途同状态分支 | 拆分相同模型配置切换、不同模型版本及跨规格对照，逐对证明可比性；缺真实调用费用不造成本收益 |
| 第四层：缓存与成本 | CACHE-001、TIME-001、OWN-001/002 | Mooncake 前缀潜力、请求到达和自有调用费用是不同来源的事实 | 分别用于测量/模拟与费用估计，区分 USD、quotaUnits、未计费与物理 cache hit；禁止跨任务强行拼接 |
| 第五层：真实动态路由 | 未来授权的 Agent Harness 中途受控运行 | 同一中途状态多动作反事实、真实联合缓存+任务终局目前没有已验收训练集 | 先设计受控采集与完整任务账本，获准后再采集；保留公开 Benchmark 作为外部测试 |

**八组状态必须逐字段实测**：`1. Task/Subtask`、`2. Agent/Coordination`、`3. Context/Memory`、`4. Tool/Environment`、`5. Verification/Recovery`、`6. KV Cache/Continuity`、`7. Temporal/Execution`、`8. Provider/Availability`。现有矩阵仅说明哪些来源**可能**提供信息，不能当作每条样本的真实覆盖率；数据缺失须标 UNKNOWN，不得填 0 或借用另一任务记录。尤其真实 Agent 中途反事实、物理 KV 命中与费用联合监督仍待未来真实采集。

**目录约定（公开仓库仅写相对目录，不发布私人主机与绝对路径）**：
- 本机现有 Git 仓库保留 `prepare_router_data.py`、`our-project/planning/`、`our-project/data/` 的台账和少量脱敏预览、`research/` 原论文及代码；**不下载全量服务器数据、重复模型权重或创建第二份论文库**。
- 服务器保留既有相同根目录下 `data/公开数据/原始数据/`（原始只读）、`data/公开数据/清洗数据/`（唯一规范数据）、`data/kev/公开数据/` 与 `data/laya/公开数据/`（现有不同模型训练格式）、`models/`（固定版本权重）、`external/`（官方代码）、`.venv/`（现有隔离环境）。只在有真实实验时增设单一 `runs/<实验编号>/`，统一保存配置、指标、日志、Checkpoint；已有文件先盘点，不急于搬迁。
- 所有临时材料使用**项目独占的 `.tmp/<任务唯一编号>/`**；用安全退出清理仅限本次自己创建的临时目录。任务异常也清理，不能删除正在使用的结果/其他进程临时文件。禁止把临时脚本复制到根目录长期存放；能在已有 `prepare_router_data.py` 中以明确模式完成则不新建脚本。不得用高风险 `rm -rf /tmp`、`git clean -fdx`、`git reset --hard`。
- 目录整理分两步：**第一步只读清单 + 重复/临时文件建议删除清单；第二步逐项确认没有进程依赖后才清除任务自行创建的临时文件**，原始数据、模型、合法训练成果与第三方源码默认保留。
- 新生成完整原始/训练/Checkpoint 文件不推 GitHub，只保留少量脱敏审查样本与统计台账；不要在 public 仓库放服务器绝对路径、私人身份、凭据或未脱敏日志。

以上是用户要求的下阶段规划，**不表示这些视图已全部产出、覆盖率已验证或正式训练已获授权**。

### 6.14 定向核验后的覆盖与用途（2026-10-10，MR-FINAL-20261010）

本节替换此前无充分依据的全项 PASS。详细字段计数、配对算法、质量分项和模型版本见 [科研数据收尾报告](科研数据收尾报告.md)，下列为当前可用边界。

- **总量不变**：14 个公开清洗源 6,600,628 行；静态选择 84,310 行，67,428 / 8,436 / 8,446。各源保持独立适配，唯一 CLI 为 prepare_router_data.py，内部 router_data 按类型组织。
- **阶段 1**：Arena 39,716 人类偏好；RouterBench 35,189 评分与估价规则；LLMRouterBench 1,432 唯一高分、7,954 同分费用规则；AgentSuite 19 个固定对话末次回答唯一达标配置。已证明账单 0、明确估价 35,189、费用来源未分清 9,386、无费用 39,735。
- RouterBench 的 35,189 条中 **35,102** 条按得分/估价唯一，**87** 条仍并列，由官方顺序选定。84,310 是原单标签导出数，不能全称严格唯一胜者。后续取样需要保留并列含义，当前数据原样保留。
- **阶段 2**：TRA-001/002 共 4,407,213 行带重复终局标签，累计费用与独立退出码字段均 0。SWE-smith 49,897 轨迹 ID 与 76,002 原始行不能互换；轨迹步重复出现 823,082 次，加入 split_type 仍重复 65,370 次。错误词统计是代理量，不能当真实失败事件。AgentSuite 的 41,430 行含复制历史，不是 8,190 条完整运行轨迹。
- **阶段 3**：AgentSuite 1,365 对标称同模型模式比较，其中 290 对一方达标；273 对独立 Thinking 权重单列；跨版本实际五组 1,365 对。不可变服务权重版本未记录。LLMRouterBench 旧 27,192 对算法未找到，本轮明确三组比较 3,714 / 15,597 / 15,597，后两组仅作不同权重/版本分析，不能混成思考强度标签。
- **阶段 4**：Mooncake 39,632 请求中 37,416 有前缀复用机会，真实命中未提供；BurstGPT 1,404,294 次到达/长度。OWN-001 是 110 聚合行（750,212 调用）；OWN-002 是 221,128 调用，185,154 次缓存读数为正、194,247 次 quotaUnits 为正；OWN-003 的 79 行完全衍生，无新增独立观测。CCH USD 与 Blog quotaUnits 不相加。没有联合最优路由标签，先分析和校准。
- **阶段 5**：ENV 34,517 任务 ID 出现量，跨两源重合 236；LongMemEval-V2 451 问题；MemoryCraft 23,884 上下文条目含 28,148 次问答出现量、23,385 个 uid，均非独立强化训练题。TRA-001 与 ENV-001/002 共享 150/13,336 个 ID，未来评测需保持任务隔离。本项目受控强化训练样本 0。
- **模型与 GPU**：现有项目 .venv 可用 CUDA，系统 Python 无 PyTorch；历史一份汇总报告 Kev/Laya 短训练和重载成功，原始日志及临时保存文件未找到。复用已有证据，不重复安装/训练。当前权重版本和字节已写入 manifest，旧摘要值不作当前凭证。
- **目录**：本轮临时材料限项目 .tmp/MR-FINAL-20261010，必要日志归 runs/MR-FINAL-20261010；历史文件只盘点，不批量删除。

### 6.15 Stage 1 科学监督定义、跨阶段评测隔离与纯静态协议最终定稿（2026-10-10，`MR-STAGE1-20261010` & `MR-STAGE1-REV-20261010`）

- **1. RouterBench（`ROUTE-002`）87 条并列标签完整核查**：
  - 在 35,189 条入池题中，唯一最高分 `2,553` 条（`train: 1,998, val: 273, test: 282`），同分最低估价唯一 `32,549` 条（`train: 26,014, val: 3,315, test: 3,220`），最高分（`1.0`）与最低估价（`0.000528`～`0.003296` USD）同时并列 **`87` 条（`train: 68, val: 10, test: 9`）**。
  - 全量核验确认 87/87 条的并列最优候选均为 `['claude-v1', 'claude-v2']`，上游 `np.argmin` 因固定候选顺序 100% 选定 `claude-v1`。完整 87 条台账已归档于 `runs/MR-STAGE1-20261010/routerbench-87.json`。
  - 协议：不覆写固定 JSONL，将这 87 条移入并列分析集（`16,070 → 16,157`），排除后全集为 `67,360 / 8,426 / 8,437`（`84,223`），`ROUTE-002` 为 `28,012 / 3,588 / 3,502`（`35,102`）。
- **2. `ROUTE-001` `"openrouter"` 元路由器更正（方案 A vs 方案 B）与三类监督体制最终锁定**：
  - **排除 `TRA-004` 19 题（`17 / 1 / 1`）**：系固定多轮对话末轮评判、仅首段 300 字符进入 `state`、`val=1 / test=1` 无统计检验力且与 AgentSuite 评测集重叠；剔除 87 + 19 后，混合候选参考集为 `67,343 / 8,425 / 8,436 = 84,204` 题。
  - **`"openrouter"` 方案 A vs 方案 B 对账（`runs/MR-STAGE1-20261010/openrouter-remediation-audit.json`）**：`ROUTE-001` 原 `9,386` 题（`7,565 / 894 / 927`）中，`1,260` 题（`1,066 / 77 / 117`）候选不含 `"openrouter"`，`8,126` 题（`6,499 / 817 / 810`）候选含 `"openrouter"`（其中 `7,447` 题原胜者已是静态模型，`679` 题 [`551 / 70 / 58`] 原胜者为 `"openrouter"`）。
    - **方案 A（整题剔除含 `openrouter` 的 `8,126` 题）**：`ROUTE-001` 仅剩 `1,260` 题（损失 `86.58%`），Stage 1 全集降为 `60,844 / 7,608 / 7,626 = 76,078` 题。
    - **方案 B（从 `criteria` 移除 `openrouter` 并对剩余静态模型重算，正式选为 Stage 1 纯静态主集）**：`8,707` 题（`7,014 / 824 / 869`）静态胜者不变（含 `201` 题 [`166 / 16 / 19`] 由同分最低费升级为唯一最高分）；原 `679` 道 `openrouter` 胜者题中，`370` 题（`305 / 37 / 28`）重算得新严格唯一静态胜者（`93` 题 [`73 / 13 / 7`] 唯一最高分 + `277` 题 [`232 / 24 / 21`] 同分最低正实测费），`309` 题（`246 / 33 / 30`）降级归入 `analysis_unsupervised_or_tied`（其中剩余静态候选 `<2` 为 `0` 题、全败 `ALL_MODELS_FAILED` 为 `308` 题 [`246 / 33 / 29`]、同分缺费或不可比为 `0` 题、同分且正费用完全并列 `TIED_SCORE_TIED_API_USD` 为 `1` 题 [`0 / 0 / 1`，即 `llmroute_hle_57`]）。
  - **方案 B 纯静态主集（`67,097 / 8,392 / 8,406 = 83,895` 题）的三类固定监督体制**：
    - **Regime A（人类偏好 `HUMAN_PREFERENCE`）**：`ROUTE-004` Arena `31,766 / 3,943 / 4,007 = 39,716` 题（无分数、无费用；公开再分发前不外发原始文本）。
    - **Regime B（纯质量唯一最高分 `UNIQUE_MAX_SCORE`）**：`ROUTE-002`（`1,998 / 273 / 282 = 2,553`）+ `ROUTE-001` 纯静态（`1,205 / 106 / 115 = 1,426`）= **`3,203 / 379 / 397 = 3,979` 题**。
    - **Regime C（同分最低历史费用规则 `TIED_SCORE_MIN_COST_RULE`）**：`ROUTE-002` 最低估价（`26,014 / 3,315 / 3,220 = 32,549`）+ `ROUTE-001` 纯静态最低上游正值费用（`6,114 / 755 / 782 = 7,651`）= **`32,128 / 4,070 / 4,002 = 40,200` 题**（明确为上游历史费用字段规则监督，非已证实结算账单，且不含实时 KV 缓存状态）。
  - **官方加载器核验与一次性派生纯静态文件**：实测证实官方 `kev/data.py`（`load_records` + `materialize`）与 `laya/train.py`（`items_from_rows`）均遍历 `questions` 全部键，不支持按 `question_key` 过滤。已在服务器 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b/{train,val,test}.jsonl` 一次性生成物理移除 `difficulty_tier` 的纯静态主实验文件（不覆写 `data/{kev,laya}/公开数据/*.jsonl`），并通过官方加载器全量校验（Laya 须传 `--max-len 1024 --head-max-len 512` 以消除 37 候选题的 `options_collapsed`）。
- **3. 第一批最小公平对比与零 GPU 规则基线**：
  - 第一批正式训练收敛为 **1 次 Kev-4B 训练 + 1 次 Laya-421M 训练**（同一 `83,895` 纯静态三集合、`seed=42`、仅用 `val` 选模、`test` 单次终评）。
  - 零 GPU 规则基线（完全源自 `train` `67,097` 题统计，在 `val` `8,392` 题评估）：均匀随机期望 `28.07%`、候选池外固定单模型（`mistralai/mistral-7b-chat`）`12.79%`、候选内 `train` 最高胜次 `46.72%`（`3,921/8,392`）、按数据源候选内 `train` 最高胜次 `46.81%`（`3,928/8,392`）、候选内 `train` 最高经验胜率 `43.95%`（`3,688/8,392`）。
- **4. 跨阶段与未来评测隔离核验（原始 Parquet 级证明）**：
  - 剔除 19 题 `TRA-004` 后，Stage 1（`83,895` 纯静态主集及 `84,204` 混合参考集）与 `ENV-001`（2,438）、`ENV-002`（32,079）、`TRA-001`（21,515）、`TRA-002`（13,501）、`TRA-004`（273）、`ROUTE-003`（520 题 / 970 步）之间任务 ID、代码仓库与题面文本重叠均为 **0**。
  - 原始 Parquet 逐条证实 `TRA-001` 与 `ENV-002` 共享的 **13,336** 个 `instance_id`（按 `repo+issue` 共 **13,374** 条，跨 **2,353** 个仓库）100% 源自 `nebius/SWE-rebench-V2`，`repo`、`reference_patch == patch` 与剥离 `<uploaded_files>` 包装头后的 `problem_statement` **100.0% 完全相同**；`ENV-001 ∩ ENV-002` 的 **236** 个共享 ID（含 `TRA-001 ∩ ENV-001` 的 **150** 个子集）`repo` 与 `base_commit` **100.0% 相同**。未来 Stage 2/5 必须执行仓库级留出隔离。

### 6.16 Stage 1 许可、数据一致性、全量编码与八类变量联合覆盖最终只读验收（2026-10-11，`MR-STAGE1-FINAL-AUDIT`）

- **1. Stage 1 三数据源训练许可证逐源核实**：
  - `ROUTE-004`（`lmarena-ai/arena-human-preference-55k`，实测 HF SHA `18c298340948c0e7f7727399fd459cca6ce0ca6f`）：HF `README.md` YAML frontmatter 与 `cardData.license` 明确标注 **`apache-2.0`**；Stage 1 仅使用 `(prompt, model_a, model_b) -> winner` 偏好标签，第三方模型原始输出文本（`response_a`/`response_b`）已物理剥离。结论：**`TRAIN_ALLOWED_VERIFIED`**（`39,716` 题：`31,766 / 3,943 / 4,007`）。
  - `ROUTE-002`（`withmartian/routerbench`，实测 HF SHA `784021482c3f320c6619ed4b3bb3b41a21424fcb`）：官方 GitHub 代码库（`https://github.com/withmartian/routerbench`）`LICENSE` 明确为 **MIT License（`Copyright (c) LangChain, Inc.`）**，且 HF 数据集 README 声明 *"designed to be used with Martian's routerbench package for training and evaluating various model routing methods"*，但 HF Dataset `cardData` 未设置正式 `license` 字段。结论：**`LICENSE_PENDING`**（`35,102` 题：`28,012 / 3,588 / 3,502`）。
  - `ROUTE-001`（`NPULH/LLMRouterBench`，实测 HF SHA `0e5af1b84bf73437a01a1849c0f1d2468baa93fc`）：官方 GitHub 仓库（`https://github.com/ynulihao/LLMRouterBench`）`README.md` 虽有指向 `LICENSE` 的 MIT 徽章，但 **`LICENSE` 文件实际缺失（HTTP 404，GitHub API `"license": null`）**，且 HF 数据集仓库既无 `README.md` 亦无 `license` 元数据，同时聚合了 21 个下游评测集与 33 个模型输出。结论：**`LICENSE_PENDING`**。
- **2. `ROUTE-001` 全量 `548,059` 行候选身份、跨子集题号碰撞与 `llmroute_hle_57` 根因核查**：
  - 原始 `bench-release`（700 个有效 JSON）在多个 benchmark 下同时包含多个均从 `index=0` 开始编号的子集目录：`mmlupro/test_1000` vs `mmlupro/test_3000`、`simpleqa/subset_500` vs `simpleqa/test`、`hle/subset_500` vs `hle/test` 及 `arenahard` 多子集文件。
  - 旧 `router_data/views.py` 仅按 `(benchmark_name, instance_index)` 聚合（共 `25,202` 个键）且未按 `model_name` 去重，导致 **`2,001` 个任务键（`25,563` 对 `(benchmark, index, model)`）出现同一模型重复评测**（`hle: 500` 题 / `6,500` 对；`mmlupro: 1,001` 题 / `13,013` 对；`simpleqa: 500` 题 / `6,050` 对），其中 **`1,165` 个任务键（`14,682` 对）将完全不同的 `prompt` 题目混入同一任务候选表**（`mmlupro: 664` 题，`simpleqa: 500` 题，`arenahard: 1` 题 `arenahard_0`），污染旧方案 B 中 **`563` 条**（`train: 438, val: 65, test: 60`）跨题碰撞样本与 **`651` 条**（`train: 512, val: 71, test: 68`）同模型重复评测样本。
  - **`llmroute_hle_57` 伪并列根因**：`hle/subset_500` 与 `hle/test` 对同一道 `hle` 第 57 题给出了完全相同的 `gemini-2.5-pro` 评测结果（唯一满分模型 `score=1.0`），因未按模型去重而被误判为 `TIED_SCORE_TIED_API_USD`。
- **3. 八类动态路由变量联合覆盖核查**：
  - 全部 14 个有效公开清洗源（`6,600,628` 行）与 3 个不同粒度自有源（`OWN-001` 110 聚合行 / `750,212` 调用、`OWN-002` `221,128` 调用行、`OWN-003` 79 衍生汇总行，互不直接相加）中，同时具备八类状态 + `(model, effort)` + 真实 KV 缓存 + 真实费用的记录为 **`0`**；中间步同状态多模型反事实分支为 **`0`**；跨模型 KV 缓存失效/重预填成本监督为 **`0`**。

### 6.17 `MR-STAGE1-FAST-FIX` 实验数据最小修复、固化与全量校验（2026-10-11）

- **1. `ROUTE-001` 完整原始 Prompt 散列合并、同模型去重与冲突隔离（P1）**：
  - 在 `router_data/route.py` 与 `router_data/views.py` 中直接读取 `ROUTE-001` 原始 700 个 JSON 的未截断 `(origin_query, prompt)` 计算 `full_prompt_hash`（绝不依赖 400 字符截断的 `prompt_snippet`），经核查每个 `(benchmark, subset, instance_index)` 内部所有模型的 `full_prompt_hash` 100% 一致（`0` 不一致）。
  - 将 `hle`（`subset_500` [500] $\subset$ `test` [2,158]）、`mmlupro`（`test_1000` [998 独立题，含 `index 16==338`] $\subset$ `test_3000` [3,000]）、`simpleqa`（`subset_500` [500] $\subset$ `test` [4,326]）及 `arenahard`（`arenahard` [750] == `arenahard_coding` [253] + `arenahard_creative_writing` [250] + `arenahard_math` [247]）的同题重复导出合并为 **`24,441` 道真实独立题目**。
  - 移除动态元路由器 `"openrouter"`；对同题同模型 `(score, cost)` 完全一致的 **`21,144` 条冗余重复观测**直接去重合并（**`llmroute_hle_57` 恢复为 `gemini-2.5-pro` 唯一最高分胜者 `UNIQUE_MAX_SCORE` [`Regime_B`]**）；对存在分数或费用不一致的模型禁止任意取首条/最大/最小，并将潜在最高分候选存在分数冲突（`439` 题 `CONFLICTING_MODEL_SCORE_UNRESOLVED`）、唯一最高分模型存在费用冲突（`22` 题 `CONFLICTING_WINNER_COST_UNRESOLVED`）或并列最高分候选存在费用冲突（`758` 题 `CONFLICTING_TIED_TOP_COST_UNRESOLVED`）的合计 **`1,219` 道冲突题目**保守隔离至 `analysis_unsupervised_or_tied.jsonl`。
  - 修复后 `ROUTE-001` 的 `24,441` 道独立真题拆分为：**`8,441` 道无冲突纯静态单胜者题**（`train: 6,788, val: 812, test: 841`；含 `1,486` 道 `UNIQUE_MAX_SCORE` [`1,245 / 113 / 128`] + `6,955` 道 `TIED_SCORE_MIN_MEASURED_API_USD` [`5,543 / 699 / 713`]）与 **`16,000` 道分析池题**（`1,219` 冲突 + `1` 同分同费 + `11,659` 同分缺费 + `3,121` 全败）。
- **2. Stage 1 纯静态方案 B 一键导出、双遍 SHA256 复现与候选打乱（P2–P3）**：
  - `python3 prepare_router_data.py --mode views` 默认输出至 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/`（不覆写固定 `data/{kev,laya}/公开数据/*.jsonl` 与旧 `stage1_pure_static_scheme_b/*.jsonl`）：
    - **`train.jsonl`**：**`66,566` 题**（`ROUTE-004: 31,766, ROUTE-002: 28,012, ROUTE-001: 6,788`；`Regime_A: 31,766, Regime_B: 3,243, Regime_C: 31,557`），SHA256 `ce32c69519cf55f1c114ec10859ed645e183a50e799a55936b3336af2cbddc2a`。
    - **`val.jsonl`**：**`8,343` 题**（`ROUTE-004: 3,943, ROUTE-002: 3,588, ROUTE-001: 812`；`Regime_A: 3,943, Regime_B: 386, Regime_C: 4,014`），SHA256 `cda07164ea87143bdbcfbd844db2609f5cebfa129f77a5ad170bfaf4b3fdb8e1`。
    - **`test.jsonl`**：**`8,350` 题**（`ROUTE-004: 4,007, ROUTE-002: 3,502, ROUTE-001: 841`；`Regime_A: 4,007, Regime_B: 410, Regime_C: 3,933`），SHA256 `2c4bf179ca237ecce07fc31bcdb992bc76d83b4eac87ba5cb6f8d68e60d87f0e`。
    - **三集合总计**：**`83,259` 题**（`ROUTE-004: 39,716, ROUTE-002: 35,102, ROUTE-001: 8,441`；`Regime_A: 39,716, Regime_B: 4,039, Regime_C: 39,504`）；另有 `test_twinrouterbench_holdout.jsonl` **`970` 步**与 `analysis_unsupervised_or_tied.jsonl` **`16,360` 题**（`ROUTE-001: 16,000 + ROUTE-002: 87 + TRA-004: 273`）。
  - 两次独立运行全部 5 个 JSONL 文件的 SHA256 **100% 完全一致**；跨集合 `task_id`、`full_prompt_hash`、`exact_prompt`、`canonical_prompt` 重叠均为 **`0`**；`"openrouter"` 与 `"difficulty_tier"` 出现次数均为 **`0`**；`ROUTE-002` 经固定种子逐题打乱后，`index 0` 胜出率从 `23.90% / 22.32% / 24.13%` 降至 **`9.20% / 9.00% / 9.51%`**（`index -1` 为 `9.21% / 9.36% / 8.31%`），彻底消除固定顺序位置偏置。
- **3. 100% 样本 Kev & Laya CPU 编码校验与零 GPU 规则基线（P4）**：
  - 在 `CUDA_VISIBLE_DEVICES=""` 下，修复版 `66,566 / 8,343 / 8,350` 在官方 Kev（`max_state=384` 及 `7552`）与 Laya（`--max-len 1024 --head-max-len 512`）下 **`100.0%` 零跳过通过**（Laya 默认 `512/192` 会因 `options_collapsed` 跳过 `1,086 / 99 / 98 = 1,283` 条），双模型联合可训练交集 **`100.0%`（`83,259` 题）**。
  - 修复版 `train`（`66,566` 题）统计的零 GPU 规则基线在 `val`（`8,343` 题）上准确率为：均匀随机期望 `28.21%`、固定全局最高频模型（`mistralai/mistral-7b-chat`）`12.86%`（`1,073/8,343`）、候选内 `train` 最高胜次 **`46.81%`**（`3,905/8,343`）、按数据源候选内 `train` 最高胜次 **`46.89%`**（`3,912/8,343`）、候选内 `train` 最高经验胜率 **`44.02%`**（`3,673/8,343`）。

### 6.18 2026-10-11 全量清洗阶段完成情况与当前唯一小任务（更新快照）

**清洗规模（14 个已清洗来源，共 6,600,628 行；各行粒度不一致）**：

| 组别 | 来源和清洗行数 | 可用于什么 |
| --- | --- | --- |
| Agent 轨迹 | `TRA-001` Open-SWE `2,075,629`；`TRA-002` SWE-smith `2,331,584`；`TRA-004` AgentSuite `41,430` | 状态前缀、工具/动作、轨迹终局；AgentSuite 仅 `273` 题 × `30` 配置，非 41,430 道题 |
| 静态路由与偏好 | `ROUTE-001` LLMRouterBench `548,059`；`ROUTE-002` RouterBench `36,497`；`ROUTE-003` TwinRouterBench `970`；`ROUTE-004` Arena `57,477`；`ROUTE-005` FindingTheRightFit `6,204` | 同题模型表现、偏好、独立评测和成本/缓存分析；不是同状态在线反事实 |
| 缓存与负载 | `CACHE-001` Mooncake `39,632`；`TIME-001` BurstGPT `1,404,294` | 历史前缀复用机会、请求到达与长度，不等于真实物理缓存命中 |
| 环境任务 | `ENV-001` SWE-Gym `2,438`；`ENV-002` SWE-rebench-V2 `32,079` | 未来 Coding Benchmark 任务/环境；任务与已有 SWE 轨迹可能重合 |
| 长程记忆 | `MEM-003` LongMemEval-V2 `451`；`MEM-005` MemoryCraft `23,884` | 长上下文与记忆评测，不直接提供模型选择奖励 |
| 自有记录（**不加入上述总数**） | `OWN-001` CCH `110` 聚合行/代表 `750,212` 调用；`OWN-002` Blog `221,128` 次调用；`OWN-003` `79` 衍生汇总行 | 调用 Token、缓存 usage、Effort 和成本先验；衍生行不新增独立观测 |

**八组变量现状**：`Task/Subtask` 有任务题面/阶段代理字段；`Agent/Coordination` 有框架标识但真实角色交接缺；`Context/Memory` 有字符长度和长记忆材料；`Tool/Environment` 有明确工具动作及环境题目；`Verification/Recovery` 多为轨迹终局重复结果，缺少逐步独立验证；`KV Cache/Continuity` 有 Blog 正缓存读数与 Mooncake 复用机会（非同类物理数据）；`Temporal/Execution` 有请求到达/Token/费用代理，但 Agent 整任务累计费用不完整；`Provider/Availability` 有候选模型和部分 Effort，但无真实路由时刻多动作结果。**完整八类联合动态路由监督 0，同状态中途动作比较 0，跨模型 KV 切换惩罚真值 0**，不可通过跨数据源拼接冒充。

**Stage 1 全文题面恢复与 Stage 1–4 双模型训练视图适配（`runs/MR-ALLDATA-PREP-20261011/training/{laya,kev}/`）**：
- `stage1_choice`：`train 66,721 / val 8,298 / test 8,240 = 83,259`（`ROUTE-004/002/001 = 39,716 / 35,102 / 8,441`；`Regime A/B/C = 39,716 / 4,039 / 39,504`）；`recomputed_route001` 排除 `1,953` 条不合法单胜者后为 `6,729 / 865 / 847 = 8,441`，与主 Choice `0` 差异。
- `stage1_pairwise`：`47,241 / 5,941 / 5,867 = 59,049` 对（`ROUTE-001: 19,647, ROUTE-002: 39,402`）。
- `stage1_soft_target`：`42,502 / 5,327 / 5,258 = 53,087` 题（`ROUTE-001: 18,932` [含 `7,333` 单胜者 + `11,599` 同分多模型分布题，剔除 `417` 道分数冲突题]；`ROUTE-002: 34,155` [含 `34,068` 单胜者 + `87` 双并列题，剔除 `1,034` 道 11 模型全满分无区分题]）。
- `stage2_agent_state`：`70,334 / 8,683 / 9,070 = 88,087` 条轨迹级压缩记录（对应 `35,289` 个独立任务：`TRA-001: 30,000, TRA-002: 49,897, TRA-004: 8,190`，去除 `4,360,556` 条逐步重复终局行）。
- `stage3_effort`：`217 / 39 / 34 = 290` 对同模型同权重有效胜负配对（`thinking-on` 胜 `182`、`thinking-off` 胜 `108`，排除 `1,075` 对同成同败平局）。
- `stage4_auxiliary`：`1,297,178 / 162,623 / 162,746 = 1,622,547` 条有效调用记录（`CACHE-001: 39,632, TIME-001: 1,404,294, OWN-002: 178,621`，排除 `48,900` 条无效/禁止训练/聚合行）。

## 7. 后续阶段接口和变更历史

历史状态（2026-10-11 上午）：双模型训练视图曾生成，记录于 v1.13。该批目录已在 2026-10-11 本轮按负责人要求移除，不代表当前数据状态。

当前状态：**本轮 P0–P4 全部完成并停止。** 14 个公开清洗源共 `6,600,628` 行；OWN-001/002/003 分别 `110 / 221,128 / 79` 行，单列。L1–L4 公开记录分别 `663,963 / 1,304,523 / 1,993,193 / 2,638,949`，合计与全源一致。逐源 Q1–Q4 已对账；所有来源在四层都有真实引用。ROUTE-001/002 的 `584,556` 行处于许可待核并排除候选；ROUTE-005 仅分析；ROUTE-003、ENV、MEM 仅评测。真实运行时路由决策标签为 `0`。

完整结果及五张表：服务器 `runs/MR-ALLDATA-PREP-20261011/quality_grading/`。ENV 与 TRA 的 `13,486` 条相同任务沿用既有 Train/Val/Test 身份，任务身份冲突 `0`。本轮未生成模型训练文件，未启动训练、GPU、付费 API 或 Coding Benchmark。是否开始后续研究阶段由负责人另行决定。

| 日期 | 版本 | 改动 | 决策/执行状态 |
|---|---|---|---|
| 2026-10-09 | v1.0 | 将 Q-007-R1/R2 的轨迹、模型选择、Mooncake 缓存、记忆、多 Agent、时间、Provider 资料整理为独立权威台账，补充 Selection Board 与未来 AI 清洗规范 | 仅研究/文档，尚无实际数据处理、逐源批准或运行授权 |
| 2026-10-09 | v1.1 | 官方数据卡核验原生字段；增补第一轮推荐数据能力组合、源专属规范化、Kev 输入长度与四阶段学习方案、五核心文档去重建议 | Planning 提案；尚未选择/下载/加工真实数据、训练 Kev 或审批服务器/GPU/API |
| 2026-10-09 | v1.2 | 公开数据服务器清洗委派、中文目录与轻量 GitHub 同步、真实监督数量待回报 | 已明确执行任务，尚无公开数据清洗实测报告 |
| 2026-10-09 | v1.3 | 首批服务器清洗记录与官方 Kev schema 核对；发现规则伪标签、样本范围与 heldout 隔离问题 | 数据转换已执行，但尚非可信 TRAIN_READY；要求同脚本科研纠偏 |
| 2026-10-09 | v1.4 | Planning 二次复核源脚本/16 份 GitHub 实际样本/官方规模，确认大额行数冲突、未全量下载、时间泄漏/模型错标/缓存复用算法问题 | Q-007 仅实测首轮加工，TRAIN_READY 未成立，等待在同一清洗代码修复和实际统计 |
| 2026-10-10 | v1.5 | Execution 完成全量 6,600,628 行清洗与 16 源轻量审查样本上线，统一统计口径 | 差额归零，代码级缺陷更正，等待 Planning 三次复审 |
| 2026-10-10 | v1.6 | Execution 完成科研缺陷收尾、统一模型选择训练视图构建与 Kev 格式 80/10/10 任务级隔离划分 | 具备 TRAIN_READY 前置数据条件，产出《科研数据收尾报告.md》 |
| 2026-10-10 | v1.7 | Execution 完成 Q-007-FINAL：生成机器可读 `manifest.json`、双遍确定性可复现验证、剔除 LLMRouterBench 13,072 条同分成本未比/并列样本至分析集（锁定 84,310 条严格唯一胜者）、修复短/标点 Prompt 跨集泄漏、通过官方 Kev 与 Laya 仓库 100% 兼容性及最小 GPU Smoke Test | **Q-007-FINAL 全部 PASS，数据资产正式定版** |
| 2026-10-10 | v1.8 | Execution 完成全量 6,600,628 条记录 8 维分层审计、8 类研究状态覆盖矩阵、AgentSuite Thinking vs 跨版本配对精确拆分、五阶段训练课程设计及本机/服务器目录治理与公开文档路径脱敏 | **全量数据分层与目录治理完成，待进入 E1/E2 正式训练** |
| 2026-10-10 | v1.9 | 完成 `MR-STAGE1-20261010`：全量核查 RouterBench 87 条双并列题（`68/10/9`）、拆分三类监督体制与 AgentSuite 19 题、明确 `ROUTE-001` 事后 `difficulty_tier` 掩码与 `"openrouter"` 元路由器消融、完成 `TRA-001 ∩ ENV-002`（13,336 题）与 `ENV-001 ∩ ENV-002`（236 题）原始 Parquet 100% 对账及仓库级隔离规范 | **Stage 1 科学监督定义与训练协议初稿完成** |
| 2026-10-10 | v1.10 | 完成 `MR-STAGE1-REV-20261010`：对账 `"openrouter"` 方案 A（`76,078`）与方案 B（`83,895` 纯静态主集，降级 `309` 题至分析集），核实官方 `kev`/`laya` 加载器不支持按 `question_key` 过滤并在 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b/` 一次性生成物理移除 `difficulty_tier` 的派生纯静态 JSONL，收敛第一批训练为 1 次 Kev-4B + 1 次 Laya-421M，完成零 GPU 规则基线计算 | **Stage 1 最终训练协议与纯静态主实验数据视图归档完成** |
| 2026-10-11 | v1.11 | 完成 `MR-STAGE1-FINAL-AUDIT`：逐源核实训练许可证（`ROUTE-004` `TRAIN_ALLOWED_VERIFIED`，`ROUTE-002`/`ROUTE-001` `LICENSE_PENDING`），查明 `ROUTE-001` 跨子集下标碰撞（全量 `1,165` 个键跨题碰撞、污染方案 B `563` 题，解释 `llmroute_hle_57` 实为 `gemini-2.5-pro` 双子集重复评测），完成 `83,895` 题 CPU-only 官方 Kev/Laya 全量编码校验（`100%` 通过且交集 `100%`），完成五级费用血统审计与八类动态路由变量联合覆盖矩阵（八类变量联合监督为 `0`） | **判定 `STAGE1_DATA_READY = NOT_READY`、`RUNTIME_JOINT_DATA_READY = NOT_READY`（审计证据归档于 `runs/MR-STAGE1-20261010/final-stage1-and-joint-coverage-audit.json`）** |
| 2026-10-11 | v1.12 | 完成 `MR-STAGE1-FAST-FIX`：更正 P0 数据源行数/自有数据三表粒度/AgentSuite 配对数/八类状态名称；在 `router_data/route.py` 与 `views.py` 中用完整未截断 Prompt 散列修复 `ROUTE-001` 跨子集题目合并（`24,441` 独立真题）、同模型相同评测去重（恢复 `llmroute_hle_57` 为 `gemini-2.5-pro` 唯一胜者）与 `1,219` 题分数/费用冲突隔离（保留 `8,441` 题入池）；固化 `ROUTE-002` 候选确定性打乱（`index 0` 胜出率 `9.20%/9.00%/9.51%`）与 `stage1_pure_static_scheme_b_fixed` 导出（`66,566 / 8,343 / 8,350 = 83,259` 题，双遍 SHA256 一致，Kev/Laya 100% CPU 兼容通过） | **Stage 1 技术与代码阻塞 100% 解除（`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`），待负责人确认 GPU 训练授权** |
| 2026-10-11 | v1.13 | 完成 `MR-STAGE1-INPUT-FIX`、`MR-ALLDATA-PREP-20261011` 与 `MR-ALLDATA-ADAPTER-20261011`：恢复 Stage 1 决策前完整题面（`66,721 / 8,298 / 8,240 = 83,259`）；对齐 `ROUTE-001` 新旧 Choice（均为 `8,441` 题，`0` 差异）、Pairwise（`59,049` 对）与 Soft-Target/Score（`53,087` 题）的完整题目身份及统一语义划分（跨集泄漏 `0`）；在 `runs/MR-ALLDATA-PREP-20261011/training/{laya,kev}/` 生成 Stage 1–4 共 6 个独立训练子集（每模型 `1,906,319` 条记录），完成 100% CPU-only 官方加载与编码验证并锁定首轮训练参数 | **双模型全阶段训练视图与首轮参数准备完毕，暂停等待 GPU 训练授权** |
| 2026-10-11 | v1.14 | 清理本实验两个模型目录与六个通用派生视图；从 14 个公开清洗源 `6,600,628` 行及 OWN 三源重新形成 Q1–Q4 与 L1–L4 记录引用、八变量覆盖矩阵及五张汇总表；按 TRA 既有分割身份对齐 ENV 的 `13,486` 条同任务记录 | **CPU 分级与来源覆盖完成；未生成训练文件、未启动训练** |

## 2026-10-14 · 来源政策与数据口径复核（MR-DATA-QUALITY-REVIEW-20261014）

> 本节为后续增量审计。正文旧版本状态保留历史语境；**不得使用首页提到的 5,027,245“合法候选核准”或 1,389,767“已训练去重单元”作为无条件通过的科研统计**。

- **旧权威六源候选口径**：`TRA-001 / TRA-002 / ROUTE-004 / CACHE-001 / TIME-001 / OWN-002` 在 V2.1 审计记录为 **4,863,900 条**，排除来源许可受限、Eval/Test、Q3/Q4 和无真实训练目标的记录。
- **2026-10-14 新口径**：`all_data.py:audit_and_reconcile_coverage_counts()` 扫描 `level1..4` 的全部 `*.jsonl.gz`，只筛 split、Q1/Q2 与 `train_eligible is False`；未显式套用六源白名单、来源许可的 `True` 判定及真实 `candidate_targets` 核对。在未重建/核验轻量索引时，缺失字段仍可能通过。因此报出的 **5,027,245** 只是待核候选引用，较旧数多 **163,345**，不可直接替代。
- **历史 Q3 引用**：旧 `levelN` 漏存资格造成 37,326 条额外引用；新版本增加 `train_eligible`、`source_policy_train_allowed`、`candidate_targets`、`specific_supervision_targets` 字段。确认清洗改动生效必须提供新的索引生成时间、规则 SHA、六源准入核验、候选集差异清单。
- **单位定义**：LEGAL 是合规独立引用；MATERIALIZED 为成功写入监督 JSONL；ENCODED 为成功变为训练 Item；TRAINED 为已前反向计算的 Item（区分曝光次数）；DISTINCT_TRAINED_UNITS 要从真实训练消费的 Unit ID 求全局并集，不可由候选池估算。缺失旧 Run 的计数应为 UNKNOWN，不得自动当作 0 或消费数量。
- **验证隔离**：旧 2026-10-13 变更前审计显示固定 Val 对当时训练索引的记录/单元/Prompt 交集为 0；最新 `all_data.py` 的 Train/Val 与 Train/Test 数值被赋常量 0，不是新协议独立验收。必须重跑集合交集，Test 保持封存。
- **联合监督事实**：八类状态在同一训练记录中并不齐全，V2∩V6=0；真正含 Model×Effort 候选、后续质量和可核账成本的联合监督仍为 DATA_NOT_READY。不得将 S1/S2/S3 合并数据量当作联合监督规模。

## 2026-10-14 · 来源政策与数据对账修复闭环（MR-DATA-QUALITY-REPAIR-CLOSURE-20261014）

- **六源合法候选严格收敛至 4,863,900**：
  - 差额 163,345 彻底查明并修复：`ROUTE-001`（124,512 条）与 `ROUTE-002`（28,012 条）因 LICENSE_PENDING 必须严格隔离于训练候选池之外（合计 152,524 条 S1 候选）；`ENV-001`（115 条）与 `ENV-002`（10,706 条）作为 S4 环境元数据不得混入路由训练（合计 10,821 条）。152,524 + 10,821 = 163,345。
  - 经 `audit_and_reconcile_coverage_counts` 显式限定 `MATRIX_ALLOWED_SOURCES = {'TRA-001', 'TRA-002', 'ROUTE-004', 'CACHE-001', 'TIME-001', 'OWN-002'}` 且监督目标限定为 `{S1, S2, S3}`，实测候选量绝对精确为 **4,863,900**（`TRA-001`: 1,673,528; `TRA-002`: 1,864,427; `ROUTE-004`: 31,766; `CACHE-001`: 28,714; `TIME-001`: 1,122,577; `OWN-002`: 142,888）。
- **去重独立单元彻底解耦与实测**：
  - `DISTINCT_TRAINED_UNITS`：由已完成 8 个 Run（F01_S1..F07_S1, F01）实际训练消费的独立 Unit ID 集合并集得出，实测为 **166,448**。
  - `DISTINCT_CANDIDATE_UNITS`：六源候选数据池独立单元总数实测为 **1,344,240**（全十四源为 1,389,767）。代码与台账将“候选池单元”与“已训练单元”独立列出，严禁概念混淆。
- **Split 隔离性真实代数验证**：
  - `quality_v2.py` 构建时以 `old != x['split'] -> raise ValueError` 作为硬断言，保证任何独立单元只能隶属于单一 Split。
  - 实测对账确认 Train/Val/Test 交叉泄漏为 0，Val/Test 保持物理密封隔离。
- **真实联合监督边界**：维持 `DATA_NOT_READY`，学术诚实拒绝在没有跨任务客观真值的情况下虚构联合标签。

## 2026-10-14 · AUTONOMOUS-TRAINING-V4 独立评测集 ENV-004 真实性纠偏与三级体系核准

> **重大纠偏审计**：Planning 独立审计核实，官方 Terminal-Bench 2.1 仓库（`harbor-framework/terminal-bench-2-1`）真实任务总数仅为 **89 个**。此前 `router_data/terminal_bench_manifest.json` 所声称的“160 题”经与官方真实目录逐项核对，仅有 11 个匹配，其余 149 个 ID 均为未经验证的脱节编制。根据学术诚实原则，该 160 题旧清单已被正式标记为 `REJECTED_UNVERIFIED_MANIFEST` 并从评测入口全面下线，其指标绝对不计入 Checkpoint 保留或学术成果。

- **ENV-004 官方基准核准声明**：
  - 上游官方代码树：`https://github.com/harbor-framework/terminal-bench-2-1`
  - 锁定官方 Commit：`7131e4375048a0e408a8fb404b5f499d726b695b`
  - 任务总数：官方实存 89 个独立任务（每个任务具备完整的 `task.toml`、Docker 镜像规范与评测验证器）。
  - 许可证：MIT License。
  - 物理隔离：100% 隔离于任何训练、验证或微调流程。严禁基于样本合成监督伪标签，严禁题目及解法泄露入输入。
  - 任务去重核验：经与 SWE-bench、SWE-Gym、SWE-smith 严格对账，ENV-004 为独立终端/Linux 系统/DevOps 容器工程挑战，零同题重合。
- **三级评测体系 89 题正式划分**：
  1. `CANARY`（8 个任务）：覆盖系统运维、工具、科学计算、算法、数学、数据、安全与机器学习 8 个异构领域（如 `cancel-async-tasks`, `fix-git`, `count-dataset-tokens`, `db-wal-recovery`, `break-filter-js-from-html`, `adaptive-rejection-sampler`, `largest-eigenval`, `caffe-cifar-10`）。当前验证阶段定级为 `MANIFEST_VALIDATED`（完成官方 SHA256 与语法对齐；容器环境与 Oracle 运行在测试节点就绪前不虚构执行结果）。
  2. `EXTERNAL_DEV`（24 个任务）：按软件工程 (7)、系统管理 (3)、数据科学 (3)、科学计算 (2)、安全 (2)、调试 (2)、文件操作 (1)、模型训练 (1)、数学 (1)、数据处理 (1)、机器学习 (1) 严格分层。未部署真实 Agent Serving / Harness 端点前，严格客观返回 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
  3. `FINAL_TEST`（57 个任务）：物理永久密封。严禁在训练或调优循环中访问，模型选择阶段访问权重严格为 0。
- **评测阶梯验证状态定级规范**：
  - `MANIFEST_VALIDATED`：任务 ID、元数据 schema 与 SHA256 与官方树一致（当前 Canary 状态）。
  - `ENVIRONMENT_READY`：评测节点 Docker 容器镜像拉取构建完成。
  - `ORACLE_VERIFIED`：官方标准参考解在沙盒内验证通过。
  - `AGENT_EVALUATED`：真实 Serving 端点联通，完整 Agent 决策交互评测完成。
- **动态保留打分权重**：
  - 未执行外部 DEV 时（当前）：`selection_score = normalized_internal_score`（100% 内部验证分）。
  - 执行外部 DEV 时：`selection_score = 0.80 * normalized_internal_score + 0.20 * normalized_external_dev_score`。

## 2026-10-14 · P0 恢复一致性、数据分层迁移与长队列交接验收（MR-P0-RESUME-INTEGRITY-20261014）

- **历史 P0-1 模型/优化器恢复一致性**：原始实现、根因与验证详情见 [PLANNING_MEMORY](../planning/PLANNING_MEMORY.md) 2026-10-14；此处不重复训练事故过程。



## 2026-10-14 · 过夜长队列可靠性修复、V1/V2.1 逐条对账与 ALGN 训练优先级调整（MR-ALGN-PRIORITY-REPAIR-20261014）

- **现场运行与 F02 阶段性推进**：
  - A6000 服务器（`k3s-infra-01`）守护进程 PID `2207051`、底层算子 PID `2287331`、Watchdog PID `2301880` 持续稳定运行；
  - F02 推进至 Epoch 2/2 Chunk 120+/123，累计完成 30,884+/31,304 步更新，消费 1,976,543+ 条样本，最新分块 Loss `0.5042`，即将迎来 Epoch 2 固定验证终评；
  - 硬件指标稳定：GPU 利用率 81%，显存 9,845 / 49,140 MiB (20.0%)，温度 74°C，功耗 290W，根分区剩余 1,148.4 GiB。
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
  - 任何非零退出立即中止队列并持久化 `queue_state.json`，坚决杜绝 F03 失败后自动消耗 GPU 跑 F04。
- **V1 与 V2.1 分层逐条记录稳定 ID 对账与真实交集核验**：
  - 物理扫描 V1 与 V2.1 全部分层（共 5,942,291 条记录）：
    - 共同记录数：`5,942,291`（**100.00%**，独有记录严格为 0）；
    - Unit ID 冲突：`0`（每个样本独立任务单元 ID 100% 相同）；
    - Split 身份冲突：`0`（每个样本 Train/Val 身份 100% 相同）；
  - 迁入迁出根因：V2.1 引入 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)` 打破同分平局，等质样本跨层更均匀重组；
  - **真实验证集交集核验**：扫描 5,070,313 条训练记录与 3,142 条固定验证集记录，**数学交集严格为 0（Record Overlap = 0, Unit Overlap = 0）**，彻底打破硬编码假设，由真实 ID 集合交集实证 0 泄漏。
- **ALGN 四组优先级前置与严格比例配额采样**：
  - 在 `FULL_COVERAGE_STAGE_MAP` 中将 ALGN_01..04 前置至 Stage 2.5（优先级排在 F02 之后、F03 之前）；
  - 改造调度循环为动态查询，在 F02 正常结束后自动率先调起 ALGN 探索小预算对照；
  - 修复多监督比例稀释漏洞：引入严格配额交错算法，确保 S1:S2（2:1）或 S1:S2:S3（2:1:1）在每个 Chunk 和 Epoch 内严格保持比例，避免主监督被弱相关数据淹没；
  - 每组独立评估并输出 S1 Loss、Accuracy、Brier、ECE，以真实指标作为后续按比例扩充的决策依据。
- **Top-5 与看板状态**：
  - 保持 MAX_CORE_CHECKPOINTS = 5，当前磁盘保留 Top-5 核心模型权重 + 1 份容灾恢复点；
  - Web 看板与文档同步更新真实服务器监控数据，不手写虚构状态。


## 2026-10-14 · Checkpoint 留存时序闭环、真实验证集 0 泄漏实证、生产级恢复引擎验证与 ALGN 长期消融推进（MR-ALGN-PRIORITY-REPAIR-20261014-V2）

- **历史 P0-1 Checkpoint 留存时序修复**：原始根因、修复、审计与恢复细节见 [PLANNING_MEMORY](../planning/PLANNING_MEMORY.md) 2026-10-14；本台账不重复相同长段落。


## 2026-10-14 · ALGN_03 完成与泛化突破实证、ALGN_04 启动瞬态 NameError 修复、不可变事故台账升级与队列安全接续（MR-ALGN03-COMPLETION-AND-QUEUE-RESUME-20261014）

- **P1 ALGN_03_S1_S3 完结指标与学术实证**：
  - **训练全量推进**：2 个 Epoch、共 162/162 Chunk 全量无中断完成，累计消费 95,220 个训练 Item 与 1,316,213 个独立任务单元；
  - **验证集实测**：
    - Epoch 1：Train Loss 0.6247，S1 Val Loss 0.6015，S1 Val Acc 67.02%，Brier 0.4152；
    - Epoch 2：Train Loss 0.5622，S1 Val Loss 0.6016，**S1 Val Acc 67.38%**，Brier 0.4149；
  - **核心学术发现**：S1 路由准确率达 **67.38%**，超越纯路由单任务参照（`ALGN_01_S1` Epoch 2 Acc 66.13%）与多智能体轨迹联合（`ALGN_02_S1_S2` Epoch 2 Acc 66.84%），刷新全项目主路由准确率最高记录。这实证了底层物理资源（Token 档位、配额档位与物理缓存命中状态）的辅助监督能够为高层决策路由提供互补的鉴别特征，显著抑制过拟合。
- **P0 ALGN_04 启动瞬态 NameError 根因排查与定向修复**：
  - **事故现象**：`ALGN_03_S1_S3` 正常完结后，队列自动启动 `ALGN_04_S1_S2_S3`，在完成 Chunk 1 计算并尝试写入断点时抛出 `NameError: name 'cursor_path' is not defined`，进程退出码 1，队列安全停机保护生效（`queue_status: PAUSED_RUN_FAILED`）；
  - **根因定位**：此前抽取 `resolve_checkpoint_to_resume()` 生产恢复函数时，`cursor_path = run_root / "cursor.json"` 被内聚封装至该辅助函数内部，导致 `run_full_coverage_stream_run()` 主函数体在保存流式 Chunk Cursor 时缺失局部变量定义；
  - **代码级修复**：在 `run_full_coverage_stream_run()` 启动阶段 `run_root` 声明后立即显式定义 `cursor_path = run_root / "cursor.json"`；
  - **多层验证防线**：经 AST 语法树全域无未定义变量扫描，`test_streaming_chunk_recovery.py`（6/6）及 `test_retention_ordering.py` 100% 绿灯通过，服务器端 `py_compile` 严格编译无误。
- **P0-4 不可变历史失败台账升级（INC-20261014-03）**：
  - 在不可变账本 `docs/historical_execution_failure_ledger.json` 中追加第三起事故记录 `INC-20261014-03-ALGN04-CURSOR-PATH-NAME-ERROR`；
  - 详细保留报错堆栈行号（1341）、根因、以及修复方案，严格遵循“永不通过 failed_runs={} 内存重置抹除历史”的审计铁律。
- **长队列断点接续与后续计划**：
  - `ALGN_04_S1_S2_S3` 在 `queue_state.json` 中的失败尝试次数为 1（未达 2 次停止阈值），已以 `COLD_START` 模式就绪，重启调度后将自动重跑并首度启用留存时序闭环与三元联合监督；
  - `ALGN_04` 完结后队列将自动平滑推进至 Stage 2 全量 Run（`F03` L1 全量、`F04` L2 全量）。



## 2026-10-18 V9 最新 RQ4/RQ5 的数据要求（替代 2026-10-16 旧映射）

**已确认的最新编号**：RQ1 总体效果；RQ2 模型池；RQ3 任务拆分；**RQ4 系统消融**；RQ5 不同工作负载下路由适用边界。**原「RQ4 Agent 角色模型互补性」已从当前论文实验中删除。** 当前数据源注册表继续保存 CooperBench 等已有候选来源，但不因曾经的旧 RQ4 而要求将其补训成独立主实验；数据来源、许可、实际清洗/训练状态不随 RQ 改名自动变更。

| 当前研究 | 所需真实数据 | 已有与缺口 |
|---|---|---|
| RQ1 总体效果 | 同一任务/池/Harness 下真实 Task Success、所有失败重试成本、Episode USD | 历史离线准确率与任务不同池、不同 Harness 的费用数字不能直接比较 |
| RQ2 模型池 | `model_id/provider/revision/native_effort_menu/price`，每个池真实模型数 K 与合法动作数 | K=模型身份数，不能把 Effort 子节点误算成模型 |
| RQ3 拆分 | 相同原任务、固定模型池与 Router 的不同 G、实际 agent/handoff/trace/cost | 拆分方案变化造成的 Agent 数变化要如实记录 |
| **RQ4-A 动作消融** | Fixed M+E、Model-only、Effort-only、分层 M→E、Joint M×Native Effort 在同任务池合法条件的真实结果 | Provider 原生 Effort 以官方当前支持为准；不能将模型变体当档位 |
| **RQ4-B 信息组合消融** | 决策前 T/M/H 的真实字段可用性、缺失率、联合覆盖、时间戳、实际编码状态 | 旧八类分布在异构来源，不能按索引拼接伪造完全联合观察；`agent_role` 等只是可选 T 组字段 |
| **RQ4-C 训练监督消融** | 合法 S1/S2/S3、独立训练任务单位、Laya/Kev checkpoint、已编码特征、固定训练预算与真实 Episode 结果 | 一条观察性轨迹不是未执行模型/Effort 的最优标签；数据来源许可、旧正式训练与新消融训练分开记载 |
| RQ5 适用边界 | 预定义 task type/原始规模/协作结构、同一策略池/Harness、每层独立任务数/最终成本/成功及 CI | 初始难度不能由事后 Trace/终局失败数补入 |

**仍旧适用的事实**：CooperBench dual-policy、team-trajectories 和其他多 Agent 候选来源可以在训练准入合规、字段真实存在且进入编码的条件下辅助 T 信息组学习；**它们不再是独立 RQ4 的必需训练数据**。既有数据集行数、许可证、GPU 运行状态均不因本文更新而改变；详见 [汇报三 V9](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)。


## 2026-10-16 追加：Agent 角色/子任务训练输入的数据源候选与真实缺口

**需求**：同一个路由器接收当前多 Agent `agent_id/agent_role/subtask_id/subtask_goal/task_phase`、已有 handoff 与实际工具/验证反馈，决定树形模型池中的 `(model, native_effort)`。消息 `role=user/assistant/tool` 不是子 Agent 角色；来源数据记录有多个模型或多个框架，也不自动代表具有同次执行中的多 Agent 角色监督。

| 优先级 | 来源 | 已公开材料能说明什么 | 未证实/限制 | 用法建议 |
|---|---|---|---|---|
| P1 | [CooperBench/cooperator-dual-policy-sft-data](https://huggingface.co/datasets/CooperBench/cooperator-dual-policy-sft-data) | 数据卡公开 `metadata.role`、`source_role`、`agent_id`，leader/follower、tester/implementer 的双代理协作轨迹；标注 MIT | 小规模、偏专门的 SFT 数据；不是跨多模型 Effort 的路由真值 | 优先字段级抽样审阅，提取角色/身份/任务文本的**输入表示**及观察性协作 |
| P1 | [CooperBench/team-trajectories](https://huggingface.co/datasets/CooperBench/team-trajectories) | 数据卡列出每任务 `agentN_traj.json`、`agentN_stream.log`、`result.json`、`eval.json`，solo/coop/team 对比，Apache-2.0 | 压缩包内部角色字段及时间戳须实际下载才确认；同一任务多条件不等于同状态动作反事实 | 构造真实多 Agent 子任务/交接/任务终局解析样例及协作评测 |
| P2 | [DeepNLP/Multi-Agents-Parallel-Orchestration-Dataset](https://huggingface.co/datasets/DeepNLP/Multi-Agents-Parallel-Orchestration-Dataset) | 数据卡给出 `session_id` 下按 Agent `trace_id` 存储的 parallel/sequential/handoff 示意 | 示例少、完整下载/许可/隐私用途需重新核准 | 用于理解多 Agent 字段组织，暂不纳入训练 |
| P2 | [PersonalAILab/AFM-MHQA-Agent-SFT-Dataset](https://huggingface.co/datasets/PersonalAILab/AFM-MHQA-Agent-SFT-Dataset) | 数据卡声明多角色/多工具 Agent 推理轨迹 | 未核样本级 agent_id、角色、模型版本/effort/授权范围 | 只作为进一步研究线索 |
| Existing | TRA-001 Open-SWE-Traces、TRA-004 AgentSuite | 已有 `agent_framework`、`pre_decision_state`、`reasoning_effort_mode` 等加工字段 | 当前已读代码未证明包含子 Agent 角色/父子关系/handoff 的统一路由训练表示 | **先复用已有源并评估字段缺口**，不能把 framework/message role 改名造角色 |
| Existing | MAS-001 MARBLE、MAS-002 MASBench、MAS-003 AgentWorld | 已在本台账；涉及多 Agent 协作 | 旧准入/权限状态未变，MARBLE 仍为 `GATED`，不得虚报可训练 | 保留候选，不把研究介绍当已获授权的数据 |

**准入边界**：以上新增来源仅为公开数据卡核对，尚未下载、未完成训练许可/字段覆盖/时间因果核对、未加入 4,863,900 既有合法候选统计，也未用于任何 GPU 训练。原始 `agent_id` 应作为 episode 内稳定身份特征/追踪键，建议训练主要使用具有跨任务意义的角色、职责、子任务目标和已发生交接；不能由观察性轨迹合成未选模型的最优 `model×effort` 标签。

**最小训练样本增补建议**：保留原有 `task_id/episode_id/step` 与观测标签，增加可选 `pre_decision_state.agent = {agent_id, agent_role, parent_agent_id, team_id, coordination_mode, handoff_count_so_far}` 与 `pre_decision_state.subtask = {subtask_id, subtask_goal, task_phase}`；明确 observed_at、missing_reason、source_id。再对照物化后的 Laya/Kev 实际 `state` 文本或结构化编码，确认输入真正进入模型；未做之前标为 PLANNED。

## 2026-10-18 追加：V8 长周期数据增补准入与公开来源再核（非新训练验收）

执行与双模型/本机实验的完整方案见 [V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018](../planning/V8_DATA_TRAINING_AGENT_BENCHMARK_EXECUTION_20261018.md)。本段属于**已有 Source ID 的增量资料核对与使用限制**，不重复登记成新的独立样本量，也不表示已经下载或运行。来源查询日：2026-10-18。

| 现有 ID | 更新核对的出处与新增认识 | 服务器处理规则 | 训练准入 |
|---|---|---|---|
| TRA-001 | [Open-SWE-Traces 数据卡](https://huggingface.co/datasets/nvidia/Open-SWE-Traces) 与 [README](https://huggingface.co/datasets/nvidia/Open-SWE-Traces/blob/main/README.md) 披露 v1.0 已因不当工具行为清理过轨迹，后续 v1.1/v1.2 增源；实际 `messages/tools/repo/instance_id/trajectory_id/resolved` 与文件数量随版本不同 | 优先盘点服务器现有分片的 revision/sha，去重、仅补缺；`resolved=-1` 留 UNKNOWN；决策前状态不得包含未来答案/最终 patch | 仅有合规训练许可、合法 Train 身份、可核真实已执行动作时用于观察性 outcome，不自动产生所有候选 `model×effort` 标签 |
| TRA-002 | [SWE-smith trajectories 官方卡](https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories)：MIT，公开 `messages/instance_id/resolved/model/traj_id/patch`，文件有 `tool/xml/ticks` 视图 | 复用已清洗分片；跨视图按真实轨迹标识避免重复计入；`patch` 只允许终局评价 | 仅观察性轨迹结果；不能由同一行为推断未运行模型的结果 |
| TRA-004 | [AgentSuite multi_challenge 官方卡](https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories) 披露 30 模型、273 任务及 thinking 配置，`model_path/sampling_params/messages/eval_result` 等 | 优先复用已加工 8 模型；新增模型具体版本与许可再核；同题跨模型可比较但不必是同中途状态 | 权利不清的新增记录不投入正式训练；thinking variant ≠ 所有 Provider 原生 effort |
| CACHE-001 | [Mooncake FAST25-release](https://github.com/kvcache-ai/Mooncake/tree/main/FAST25-release) 的 `timestamp/input_length/output_length/hash_ids` 提供 512-token 块的可复用前缀机会 | 与 CACHE-002 去重；在独立 `CACHE_REUSE_OPPORTUNITY` view 做时序/前缀重复分析；不能强行与 Agent task ID join | **OBSERVED_REUSE / SIMULATED**，不是 Provider 真实 `cached_read_tokens` 或真实 USD；不得造出缓存击中率真值 |
| CACHE-005 | 真实 Provider Usage 与本机引擎可核验指标（非已下载数据集） | 未来 Agent `model_calls.jsonl` 按 `episode_id/decision_id/request_id` 记原生 usage、价格版本与缺失 | 只有来源可核、与同 Episode 正确连接时可用 `MEASURED_CACHE` 训练；缺失保持 null |
| ROUTE-003 | [TwinRouterBench](https://github.com/CommonstackAI/TwinRouterBench) 包含静态监督评测与动态 SWE-bench 评测；有公开的模型路由对照实现 | 本机放 `external/benchmarks/TwinRouterBench`，不并入原始训练缓存 | **EVAL_BENCHMARK_ONLY，不参与训练与阈值调优** |
| ENV-004 | [Terminal-Bench 2.1](https://github.com/harbor-framework/terminal-bench-2-1)，Harbor 提供容器执行与评分；项目已有 8/24/57 隔离划分 | 本机放 `external/benchmarks/terminal-bench-2-1`；先 Canary `fix-git` / `count-dataset-tokens` | **BENCHMARK_ONLY**，不得进入 Laya/Kev 学习；Final 57 维持封存 |

**数据视图分界**：`OBSERVED_AGENT_OUTCOME`（观测行为、决策前可见输入与终局真实 label）；`ROUTER_CHOICE`（有效静态胜者/可比行动依据）；`CACHE_REUSE_OPPORTUNITY`（前缀可重用机会）；`MEASURED_CACHE`（未来同任务实测缓存 usage）。不同来源无同一真实 `episode_id` 时绝不横向伪联结。相同任务/仓库/近重复 issue 的所有前缀须在同一划分。新增训练必须沿用许可证、Train 身份、时间因果审查；测试集、Benchmark、仅分析集始终排除。

**外部方法 vs Benchmark**：`RouteLLM`（[源码](https://github.com/lm-sys/RouteLLM)，强弱双模型 query-level router）和 `SR-KNN`（[vLLM semantic-router](https://github.com/vllm-project/semantic-router) 或 TwinRouterBench 已有适配）是**方法参考**；Terminal-Bench/TwinRouterBench/SWE-bench 是**评测资源**。代码目录 `external/router_methods/` 与 `external/benchmarks/` 严格区分。只有已用相同真实任务、同池动作约束、同 Harness/费用口径运行后的结果，才可以填写 V8 RQ1–RQ3 实验表。

**执行/下载状态**：本段为 Planning 的在线来源复核；服务器新文件有无、磁盘实际路径、最终许可、数据清洗/训练、Mac Benchmark 与模型并发状态，均待 Execution Agent 现场回传，不声称已经完成。
