# ModelRouter · 论文研究问题、实验与图表规划（V9｜2026-11-07 更新）

> **2026-11-08 当前方法定义**：只研究Single-Agent，链为Harbor→ModelRouterMiniSweAgent→DefaultAgent。RQ3为阶段、真实子任务边界与路由粒度；Inspect/Modify/Verify/Recover只表示阶段。RQ2固定Luna/GLM-5.3-Flash/Terra，Registry登记15个Model×Native Effort。GLM已绑定Colink，短文本正常，长High4096耗尽推理额度，返回Effort未报告。AA v7包含Luna/Terra各六档及GLM Max共130项，Low/High缺测，TTL/force/STALE及同批固定版本已实现。T/M/H和三字段教师沿共享Serializer进入原生Laya/Kev。开发题circuit-fibsqrt已有10尝试：4官方零分、6无有效Reward；旧HY4结果保持历史身份。
>
> 当前能力链为Registry→AA统一快照→逐档候选卡→M→共享Serializer→原生Tokenizer。v7取得时间2026-11-07T13:47:04.783836Z，Intelligence Index 5.0.1；13条独立实测动作共130项。8个真实状态的16项双原生编码均FULL，工具/生成摘要上限1000/800字符。Laya总输入6524–8092 Token、Kev6727–8194 Token；原始历史另存。正式批次保持同一snapshot_id，过期和强制刷新沿原capabilities入口。

> **11-02最新Dev批次**：9个公开Dev任务19 Episode全部结束，原Harbor Verifier9次，7成功/2失败/10未知。实际请求DeepSeek，动态三身份为ALIAS_SMOKE，正式K=3质量结果仍缺。Git/HF/POV-Ray三组同协议完整对照固定3/3、动态2/3；参考模型费按成功数分摊0.006153744/0.006720942USD，Trial合计738.50/1805.48秒，动态收益未证明。财务/MTEB跨处理版本只观察。详见[批次结果](../../our-project/results/iterations/20261102-v9-deepseek-dev/review.md)。
>
> **路由与成本**：124次真实CPU路由全Sol、无切换/fallback，10初始化/114复用，前向仍主要耗时。教师1成功/4次实际消费，仅三字段进入Router，映射0.009158USD；开启后同题总费/时长增加，净收益未证。227请求/223Usage/4未知，DeepSeek公开同系列参考费已知0.10950165USD、逻辑映射1.0058892USD，实收/资源/完整费用未知。原工具30秒、30步/4096输出与Verifier保持，超时反馈版本6次均有原Verifier。
>
> **研究接续**：Dev/Alias新增Train标签0，有效Model-only仍19、任务9/步骤10、11标签任务，74行未训练、215/186仅可组合，Effort/K=3目标0。AA v4和low/none/Flash缺测保持。03:36:36 F14独立维护284/420块、36352/107404步、最新Loss0.50280873、首轮/Val未完，旧归档/既有handoff不动；本轮训练0、Serving仍F05/原Kev、STEP_001/F11/R11不晋升。五RQ八图十二表、Fig.2和独立Twin旧评价不改；SWE-bench Verified原生入口仍待实现。

> **11-02前一工作包真实结果**：三个既有Train任务8对前缀新增有效步骤2条、2个新标签任务：Mido质量Luna1、Schema等质量成本Luna1；PrettyTable六对双失败只存观察。累计19 Model-only、任务9/步骤10、11标签任务，总Sol4/Luna15、步骤Sol4/Luna6；215/186只是可组合数量，74行S1+步骤材料已准备但未训练。Effort/K=3仍0，AA v4与缺测保持。详见[本轮结果](../../our-project/results/iterations/20261101-v9-runtime-quality-dev/review.md)。
>
> **输入及路由成本**：QID不进入模型，但问题说明、顺序及状态进入；在线沿用步骤目标/Sol→Luna，Prepare保留捕获视图，新两条3874/3962 Token完整进入5120。新Checkpoint未重训。成功Dev5路由仅一次初始化28.62秒、后4次前向外0.0477秒；未证明前向加速。原取消状态用于停止超时后新增请求，30秒工具窗口/Verifier不变，保存/app；取消分支未另造旧900秒失败验证。
>
> **Dev与收益范围**：distribution-search固定Sol/Luna/新Laya关闭教师reward1/0/1，CTRF4/4、3/4、4/4，费0.0866944/0.00228552/0.1362464USD。COBOL Luna成功，Sol无Verifier，新LayaAgentTimeout后Verifier reward0。本轮新Laya28次实际选择全Sol、无切换/fallback，含2次旧取消问题截止后额外调用。教师开/关同题都成功，1成功/1消费/0.019706USD，合计费0.111619/0.1362464USD；单题轨迹与缓存不同，不证明净收益。77请求/76Usage/1未知，已知2.00106484USD，完整费用及实收/资源未知。
>
> **训练现场**：01:08:59台北F14另项维护241/420块、30848/107404步，最新Loss0.48724648、最近12块有限，首轮/Val未完成，不作父；既有handoff等待，本轮未干预。Serving仍F05/原Kev、V9_LAYA_STEP_001-e01不晋升，F11/R11研究代表保持。独立静态八版本不重评、不训练；五RQ、八图十二表沿用，有限K=2与单题教师结果不能填成正式三模型主表。

## 2026-11-01 · 以下为原时点执行记录

> **本轮真实增量（11-01）**：四个已有Train任务的新失败前缀新增步骤偏好4条（Sol质量3、Luna等质量成本1），新增来源任务0。累计17条MODEL_ONLY目标、9任务、任务级9/步骤级8、Sol4/Luna13；步骤覆盖8任务/7仓库、Sol4/Luna4，7质量差异/1成本。唯一视图含旧13条，可组合213/186，旧382与13,214候选不重加工。实际effort发送参数已保存，但Sol请求low报告max、Luna未报告应用档位，确认的Native Effort/同模型Effort/K=3仍0。11:50现有目录仍无Flash，AA固定v4、Max不作low成绩；五RQ、八图十二表保持，训练任务结果不填正式效果表。详情见[本轮结果](../../our-project/results/iterations/20261101-v9-quality-step-supervision/review.md)。
>
> **动态与教师**：新Dev custom-memory-heap-crash三策略各7生成/6完整工具结果。新Laya7真实CPU路由全Sol、切换0/fallback0、概率0.5042–0.5476；和固定Sol均工具30秒超时、原Verifier未运行，reward未知。固定Luna reward0/CTRF5/6，三份仅观察、不入Train或生成质量赢家。模型费Laya/Sol/Luna为0.1809328/0.1367668/0.00188939USD，Trial601.404901/553.177141/113.584711秒；本轮37请求/32Usage/5未知、已知0.57554089USD，完整费用未知。教师本轮0，上一轮1成功/4消费/0.013086USD净收益未证明，原三字段、两参考及低频机制保持。工具验证通过不替代Episode成功，artifact为空，未重建或重跑。
>
> **输入与有限接续**：Laya原1024裁17/17状态，5120完整保留17/17 canonical视图、候选价格和两选项；完整原消息另存。Kev最大状态3700Token在8K可容纳，R11父384不适配。Laya从F11-e01用64旧S1+8步骤目标72行、1轮/9更新，仅pointer head/lr2e-5，encoder保持，任务成本/教师/Effort目标不训练。固定S1 Val561项Accuracy0.6898保持，Loss/Brier/ECE至0.5938/0.4083/0.0362；真实checkpoint在服务器，首次原额度移除记录保留。12:57现行F14另项冷启到块25/420、3200/107404步，最新Loss0.5952、最近12块有限，旧failed归档、不作父；原队列文件仍暂停，已有handoff等待F14退出，本轮未创建或操作。Kev未新训练，F11/R11代表与旧Serving保持。旧四档偏置分析和独立八版本不重评、不调参，本轮新权重未在该集评价。有限接续未证明动态收益，联合档位、Flash、完整Dev及教师净收益仍待。

> **独立静态评分完成（11-01）**：用户已选TwinRouterBench 520题/970步，两组微调前与原Val前三8/8在CPU完成。F11-e01为20.515464分，比微调前高13.505155个百分点；R11为18.969072分，比微调前高5.670103个百分点，全部版本低于恒选low71.030928分。此为旧四档精确步骤分，不是Agent终局、三模型选择标签或正式五RQ效果；不按Test重选、不晋升Serving、不填原正式效果表。01:43:44服务器无活动训练、F14归档failed/NON_FINITE_LOSS，旧V9加训完成但382/v4与新2条后未加训。结果见[独立评分](../../our-project/results/iterations/20261031-twinrouterbench-independent/review.md)，原五RQ、八图十二表保持。

> **历史结果资格（2026-10-31）**：本轮从ad1d392接续，在已有SWE-smith公开训练任务TextFSM上取得有效K=2 Episode对照1组、真实步骤前缀2组。Sol/Luna low两Episode均通过原96项，任务级成本偏好Luna；前缀7 Sol一步通过而Luna使用不存在的apply_patch，形成即时修复偏好Sol。新合法选择目标2条，同1任务，前缀6两失败只作观察；完整三模型最优标签仍0。原mini/Harbor及正式五RQ不变，不将训练任务、一步成功或单题差异填正式效果表。结果见[真实监督记录](../../our-project/results/iterations/20261031-v9-real-route-supervision/review.md)。
>
> **教师证据**：旧五次失败与新真实Sol low/2048空正文均说明reasoning可用尽额度。原Assessor缩短固定参考/观察视图，仅做事实摘要；low/4096、context8000，首次约3生成、后续至少间隔3，验证/重复错误优先阶段变化。新真实step3三字段JSON成功，input1462/output1528含reasoning1435、模型费0.0189335USD；未执行新Router或工具，且该价格仍约为Luna本次Episode的4.23倍。单次有效输出不证明稳定收益，旧短评随信号变化清除并保留截止范围；不改变Agent计划、执行工具或指定模型。
>
> **AA、费用与监督**：两条新目标绑定v4，任务级/步骤级有不同问题ID和instruction，原Prepare/Trainer序列化已实际消费；完整过去状态保留，候选结果不进入决策输入。旧390、四教师与有效382视图不重加工，Train196/Val186加新2条可组合198/186；同1任务不能计为2个独立题，旧13,214非全量新增。25生成模型费0.26274516USD、教师0，供应商实收与资源费用未知。Flash两个账户本次/models仍未列出，实际K=2；AA low/none/Flash等缺测保持NOT_MEASURED，不借用其他型号成绩。
>
> **当前两组训练（台北20:42）**：两组活动训练0，原控制器已退出、队列PAUSED_USER_REQUEST。F01–F13、Kev R01–R16及固定Val完成；旧F14非有限失败归档保留，新F14/F15初始化run_meta未赋值、F16进入训练前停止另记。F11-e01/R11代表与Serving原权重不变，旧V9两轮8/100更新和负结果保留，本轮未加训。可加载前三为Laya F11-e01/P0_B03_C01_QB_PB-e02/F05-e01；Kev全部19个同Val正式候选为R11/R12/C09，若仅看R系列则为R11/R12/R01。原固定Val不当最终Test，最终Test尚未执行。新2条仅1任务，还不具备有意义继续微调条件；原参数接点、旧S1、截止前教师与AA编码保留。详见[训练报告](../../our-project/results/training/training_research.md)和[PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md)，五RQ、八图十二表不变。
>
> **10-30 历史结果资格**：新 `20261030-v9-official-luna-complete` 已取得官方 reward=1.0、CTRF tests2/passed2/failed0，真实 Luna none/low、14 路由/0 fallback。此为 K=1、同模型双动作的小开发结果；独立三模型与五 RQ 总体效果仍未得到证明，正式总体对照表保持空白。真实 Luna 官方 Episode 与映射实验分开。三原目录的 `mapped_cost_accounting` 已本地重算，旧 raw 与终局保留；金额和缺失 usage 的处理见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md)。Flash 使用原 snapshot `20261018` 的 OpenRouter 公开 USD 参考价；阿里官方 v2 只有 CNY，USD 未确认，不换汇。当前文档只记录本地结果，不新增请求、探针或部署状态。五 RQ、八图、十二表结构及旧失败不变；完整统计、F14第420块NaN与剩余项只在 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 当前入口维护。
>
> **历史结果资格（10-30 20:05，旧额度已取消）**：Docker已恢复，官方Oracle reward=1、CTRF 2/2通过，只记环境核验。真实Luna Episode保留9生成/18工具/3教师，Laya单候选回退且预算容量不足，未执行官方Verifier；配置价估算0.182588USD不作现金账单。已保存前缀的K=1 none/low真实路由通过，尚无完整双动作Episode。AA v2的LunaMax27.7552/AA5.0及9项只作参考，Sol/托管Flash缺测；新Laya/Kev仍为内部训练/消融候选，完整三模型目标0。Fig.2保留短摘要/完整卡区分，Laya完整卡仍裁；教师触发不等于成功率收益。五RQ/八图/十二表不变，正式模型结果格继续空白；详细实测仅维护于 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 当前入口，以下按历史时点理解。

> **10-30 10:40 历史训练更新**：Laya `V9_LAYA_001` 两轮及每轮 5,692 条固定 Val 完成，保存的第 2 轮真实 CPU 加载/前向通过；总体 Accuracy 48.23% → 49.51%，S2/S3 改善、S1 四项退步。Kev 两轮/固定 Val 完成，四项相对 C03 退步。4 条教师核心与缺测能力卡真实消费，Laya 仍裁 6 条完整状态，新实体未上线。AA 实测、独立三模型、完整 USD 和官方 Harbor 结果仍缺；这些内部训练指标只作辅助证据，五 RQ/八图/十二张正式结果表继续留空。详细统计与权重留存见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 首页；下方旧“Laya 未启动”等记录按原时点理解。

> **历史正式执行参数接入**：原 Harbor CLI/Agent 已接入 V9 配置和三候选，参数解析与真实实例构造通过，该时点尚无官方 Trial；后续单 Luna 双动作已取得官方成功。三逻辑身份共用 Qwen 的配置联调不计 K=3 独立模型；五 RQ 的正式表格仍留空。

> **图表结构：五个 RQ、八张图、十二张结果表。** 2026-11-07 当前定义见文首；以下早期批次事实按发生时间作为历史证据保留，不覆盖现行方法。
>
> **现行五个 RQ**：**RQ1 整体效果**（完整策略与固定/混合/同类策略比较）；**RQ2 固定 K=3 目标池中的 Model×Native Effort 候选**（按 Provider 实际能力确定联合动作，不做扩 K 或换池比较）；**RQ3 单 Agent 阶段识别、真实子任务边界与生成决策粒度**；**RQ4 系统消融**（Model×Native Effort、T/M/H、教师和训练监督）；**RQ5 工作负载适用边界**（按事前可观察任务属性研究净收益）。不含多 Agent、角色、协作、handoff 或 Agent 数量变量。
>
> **导师汇报 / PPT 大纲（V8｜14 页，约 12–15 分钟）**：[汇报提纲.md](汇报提纲.md)——逐页标题、讲述重点、主方法 Fig.2 的每个模块/变量/箭头、各 RQ 图的坐标和对照、12 张空白表的用途、后续生图素材数量。**当前只规划，不制作 PPT 或图片**。
>
> **旧交互式视觉原型**：[交互式原型（V7，未同步 V8）](交互式原型/index.html)；不能作为本轮最新 RQ 的权威依据。

> **10-30 历史方法演进与输入证据**：成功 invoice、失败 duration 原题与必要重跑独立记录；invoice 教师 3/6、duration 教师 2/5，不混成同一 Episode 统计。唯一材料实体 390 行（Train 198/Val 192），S2 Train 70 含 6 条真实前缀，不与两条固定公开 Train 成功参考重合；离线原 Assessor 2 请求/2 成功、4 条可用三字段（2 新、2 复用）、2 条未触发，状态 PARTIAL，实际教师 `self-dploy/Qwen3.8-27B`。旧 LayaState 2,762/2,827 Token、预算 940、任务位置 2,733/2,798 被裁的负结果保留；唯一 formatter 与短工具视图的实际结果另记，不把接口通过当新特征学习。Fig.2实际编码/同义训练要求保留；新Kev候选两轮完成、`FEATURE_PARTIALLY_TRAINED`，原Serving旧权重的`FEATURE_NOT_TRAINED`保留，未得正式结果的表格继续空白。 现行结果见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 的训练表；Laya V9已完训，F14有效优化更新仍未知。

> **三身份与实施范围**：逻辑身份为 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`；映射实验真实请求后端为托管 Qwen3.8-27B，Router 选择与实验身份保留逻辑目标。费用按真实 input/output/cache 用量乘所选目标身份价格，教师按配置教师目标身份计价；`cost_model_id`、`cost_basis` 和顶层 `model_id` 记目标身份，`returned_model_id` 保留真实返回身份。后端价格、供应商实收另列，缺失不影响映射实验；映射结果不作独立物理模型质量对照。Qwen 网关 `/models` 与流式名 `Qwen3.8-27B`、非流返回 `self-dploy/Qwen3.8-27B` 分别保存。三原目录重算详见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md)。

> **真实回放与已完成分词范围**：成功目录`router_input_replay.json`记录Laya选`gpt-6-luna`、`epoch_01`、`fallback=false`；Kev20秒客户端窗口失败和一次60秒窗口约53,516 ms真实前向成功、选`gpt-6.1-sol`及三候选真实概率保留。Kev ID `1001bb4d826a52d1f399e183466143f4da7b741b`为Serving导入适配器，不能称R11候选。已保存的 [final编码与训练prefix分词记录](../../our-project/results/iterations/20261029-v9-alias-smoke-tools/input_encoding_validation.json) 确认任务、三教师字段、候选卡及缓存/身份关键字段进入最终编码；新顶层`recent_tool_validation`于18:44 UTC/02:44台北仅验证原step5：Laya1024/head512、状态预算940下，512字符真实工具结果仅末128字符在Token `[879,930)`为`FULL`；任务、三教师、三候选卡及缓存/当前和前次身份均`FULL`，长`history_snippet`仍裁。Kev原native编码2147 state/2224 total、不截短、候选键3个，本次未新增Kev API前向。18:46 UTC/02:46台北同源Laya真实API前向`fallback=false`，选Luna，概率Luna0.4005/Sol0.3519/Flash0.2476，模型前向1961.71ms、客户端1985.07ms，checkpoint仍`epoch_01`。主Agent本次新增Router1/生成0，135calls及575783/256135/168082预算不变。原`context.py`单文件已原位部署，源cached3136仅为字段保留。此前198条Train分词已测，本次未重测该批Train或Val；Laya1024保留4教师核心、完整state裁6条，8192推荐尚未启用；192条Val仅核身份/数量、未测长度。分词范围、模型学习与正式实验分别记录，不重跑同题、不填科学成绩，不报告新权重上线。 同一JSON新`live_transport_validation`记录04:20旧SystemOne直传调用链、同发送正文native编码及响应1024输入Token；未采集旧进程Token IDs、普通`/route`未验证，长history仍裁，未重跑整个Episode或换Serving权重。

> **新增负结果与环境限制**：另一 `duration` 题 `20261029-v9-kev-alias-smoke` 完成 2 次真实生成/3 次 Bash 后，第 3 次路由 60 秒超时，默认原 PolicyModel 在 fallback 后退出，`FAILED/验证1`、日志全保留。原 Serving `2291306` 未重启/换权重，`KevAdapter` 启动未传 `device`、默认 CPU/`torch_cpu`，step0/step1 前向 18,802/38,674 ms，step2 工具 history 长度回报 3,835（单位未报）时超时。首个 Bash `find /` 上游 30 秒超时，后用 `ls/pwd` 定位，未改外部数据；Host 无容器隔离，不称安全或正式基准，不填 RQ 成绩/正式时延统计。教师失败后继续与 Router fallback 后退出分别记录。该失败回报当时计划在原 Runtime 补真实初始 CWD、按 `router_context_chars` 缩工具视图并保留 task/teacher/raw mini 消息；后续一次参数调整、窄重跑本题的实际终局见下段，成功 invoice 不重跑，原失败保留。

> **短视图解决路由超时，任务仍失败**：原 [input_latency_validation.json](../../our-project/results/iterations/20261029-v9-kev-alias-smoke/input_latency_validation.json) 记录任务 1,019 字符全保留、工具摘录 3,835→1,280 字符、任务/工具字符预算 2,300，7 条 mini 消息与教师/能力/连续状态保持，CPU 前向 37,771.85 ms、`fallback=false`，概率 Flash 0.7234/Sol 0.1468/Luna 0.1298；该单次回放教师 null、卡片缺测、生成请求 0。随后 `20261030-v9-kev-alias-smoke-compact` 的 [metrics.json](../../our-project/results/iterations/20261030-v9-kev-alias-smoke-compact/metrics.json)/[verification.txt](../../our-project/results/iterations/20261030-v9-kev-alias-smoke-compact/verification.txt) 记录 10 次生成、13 次真实 Bash、10 次 Kev 真实路由全部 `fallback=false`，CPU 前向 20,430.85–37,243.64 ms；全部逻辑 Flash/实际 Qwen、原 Serving 导入适配器。教师 5 请求/2 成功，3 失败依次 TimeoutError/JSONDecodeError/TimeoutError，成功短评在 steps3/4/5 实际送入 Router。代码仍有 7 个 subtest errors（7 方法、4 通过），10 步 LimitsExceeded、FAILED/resolved=false、验证退出 1，不能写成功 Agent或官方成绩。完整用量/费用因失败教师缺测为 null，原测试与失败保留，源码/任务/patch 已存 artifacts、临时目录已清理。

> **10-30 历史停止与训练准备（不作当前执行条件）**：原预算known/reserved/remaining=`575783/256135/168082`及135calls未变，15次新增请求仍属此前计账，不当作本次新增；预留不作实际用量，不再新增生成式请求，自有本机8000隧道28959已结束。现有 [prepared/summary.json](../../our-project/code/data/v9/prepared/summary.json) 写Laya2 Epoch、`max_len=1024/head_max_len=512`，Kev2 Epoch、`max_state=8192`；父R11原1 Epoch/384，与在线导入适配器分开。此前已保存的198 Train测量表明Laya当前1024保留4教师核心但裁6条完整state，全198条完整编码至少需8143，8192推荐尚未启用。源码部署、三次FAILED与原GPU等待历史分别记录；原CLI25201自然退出；第四次worker50518于2026-10-30 03:25:31完成2 Epoch/100 steps、自然退出0，模型已保存于A6000；原dispatcher50514同秒自动开始固定Val attempt1；2026-10-30 04:23:20台北完整结束，控制器自然退出0，`status/training_status=COMPLETED`、`evaluation_status=EVALUATED`；新候选为`FEATURE_PARTIALLY_TRAINED`（4条稀疏教师、三新身份监督目标仍0），原Serving旧权重的`FEATURE_NOT_TRAINED`保留，未传Mac或上线Serving，不新增Trainer或长期方案。 固定Val8436记录/9330问题完整完成，拒绝/裁减0、`test_used=false`；相对原C03四指标均退步，内部score92.38703579133796。V9组仅1条，rank1不表示优于C03；新权重仍只在A6000、未上线Serving，正式Harbor/RQ成绩仍空白。原validate_candidate完成时间同步及update_retention(apply=False)评分保存已实测完成、释放/删除0；五RQ八图十二表和正式空白结果保留。

> **首批部署完成与首次 FAILED（历史保留）**：主 Agent 已部署 37 个源码/数据/相对链接对象、6,993,920 字节，含 16 个 V9 Python 模块及 schemas/registry/common/390 材料；原两文件增量补丁保留 Laya 4 处历史差异，45KB common 重复实现改薄别名，实导入 `common is canonical=True`，root 真正执行链保留。原 Python/`_material` 实读 198 训练行/4 教师/2 refs 及相对 Train 链接有效，GPU/Serving 未重启。`KEV-V9-001` 在原 candidate_queue/ledger 登记，父 R11 实体与内部四指标 score106.74866622586939、16 原 R 候选完成，登记时 QUEUED 仅历史。原 CLI 第 1 次 worker13266 在 0.145 秒退出 1，未加载 GPU 模型/消费训练输入，FAILED 保留；路径执行 `dispatcher.py` 使 `sys.path[0]` 位于 `modelrouter/training`，bare `import kev` 误落 `training/kev`，官方 `kev.train` 未导入。train.log/attempt/cursor 保留，189 项先前组合测试通过不能替代实跑失败；不填新训练/Val 或官方成绩。

> **第2次真实反向OOM（历史保留）**：同一原wrapper两行模块入口调整已部署、40项窄测通过，官方 `kev.train` 实导入位置为 `external/kev/kev/train.py`。worker16722先RUNNING，8K输入进入真实反向计算后Torch CUDA OutOfMemory、自然退出1；进程13.54 GiB、再分配60 MiB时仅59.94 MiB空闲，训练日志Epoch0/Step20/100/Loss0.993。原Loader全部接纳198条记录，两轮预期396条次；失败目录只有`training_config.json`，输入曝光0为启动时统计，失败后完整输入曝光与独立覆盖UNKNOWN。0、198或396均不能当作失败后的实际训练完成量。13266入口失败与16722反向OOM均保留，两次失败没有产出两轮完成权重或固定Val；UNKNOWN不由第四次的396完整passes覆盖，仍不填正式结果格。

> **原资源等待及三次FAILED历史、现行Kev结果**：原资源代码已按已观察占用下限加原2 GiB余量增量部署，CLI验证`WAITING_FOR_GPU`；01:43的12,668/15,973 MiB保留历史，02:11空闲12,698/需15,973 MiB为当时等待，旧384输入`required=12103`不适用于8K，不增其他限制。CLI25201曾沿原`main_loop(wait_for_resources=True, v9_only=True, ...)`保留，主Agent确认27184无worker并已结束；服务器源码`CLI_WAIT/EXIT_RESET=true`已验证，前三次FAILED和原CLI25201自然退出保留历史；第四次两轮完成/实体已保存/固定Val已完成，训练、曝光与保存证据见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 训练表。不另建loop/Runner/定时任务。F14/ComfyUI/Serving未被干预；F14只读证据见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 的F14段；先前占用、ComfyUI`<A6000_HOST>:8188`监听及运行队列1/pending0历史回报保留，图像任务活跃，`127.0.0.1`不通属绑定地址，未卸载/干预。原Provider/telemetry账本/ledger/logger已补`alias_mapping/query_raw`；V9 AliasProvider构造成功、账本根`<SERVER_PROJECT_ROOT>`，未发API请求/读Key、不新增client服务，Alias/账本补齐已验证且无新API，不计认证或真实生成成功。此前source部署为40个文件/链接加原Laya/Kev增量，首批37对象/6,993,920字节保留历史，后续总字节未报。Serving仍旧权重；Laya hook在盘、F14内存不读，下一自然child完两轮边界生效；旧exit处理已由服务器源码确认，不干预健康worker、不另建Trainer/队列，原Serving旧权重的`FEATURE_NOT_TRAINED`保留，新候选为`FEATURE_PARTIALLY_TRAINED`，现行结果见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 的训练表；正式三模型成绩仍空白。原评分及留存机制保持；本轮收尾仅涉及多余控制器和临时连接，04:33:44主Agent确认无当轮SSH连接残留。 现行结果见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 的训练/Val/评分记录。F14只读证据见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) 的F14段；Laya未启动、AA0、三新身份目标0、校园9002物理对应UNKNOWN、USD缺测与duration失败仍保留。

> **2026-10-28 V9 最近讨论简化补充（拟议，未实现）**：正式权威仍是 **5 个 RQ + 8 图/12 表**；聊天里“改三核心 RQ、消融合入 RQ1”的组织建议尚未正式批准，不自动修改原 RQ/Fig/Table 编号。Fig.2 外置教师简化为**单个顶级推理模型 + 固定两条来自合法 TRAIN/DEV 的公开成功轨迹摘要**（高效完成/失败恢复），不建实时相似度检索；约积累三次模型生成或关键阶段/停滞事件时，在下一次 Router 决策前生成 `progress_summary, main_blocker, next_milestone`，另记录截止步骤、参考 ID、教师完整 Token/美元费用/时延。模型能力卡优先软件工程/代码/工具 Benchmark 的原始分和原始单位、AA 综合 Intelligence Index（不是正确率百分比）、对应真实 Effort 证据；只派生综合低中高，缺失档位 `NOT_MEASURED`。健康训练继续；Laya/Kev 各按同协议 Val 选可加载候选，再用独立 Dev Agent 完整 Episode 比较后决定继续微调主线，初始研究池暂以 K=3 个可用模型为目标。mini-SWE-agent 是 Agent 框架，SWE-bench Lite/Verified 和 Terminal-Bench 2.1/Harbor 评测任务不同，结果不得混用。本轮文档同步不是新训练、付费调用、测试或图表实测授权。

> **2026-10-29｜初始 K=3 逻辑身份与能力资料**：V9 五 RQ、Fig.1–8、T1–T12 不变。逻辑身份为 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`；映射实验真实请求后端为 Qwen3.8-27B。实验费用按所选目标身份价乘真实用量。Sol 使用 v2 已保存官方 `2/10/0.1/2.5`；Flash 采用原 snapshot `20261018` 的 OpenRouter 公开 USD 参考 `0.15/0.47/0.016`，阿里官方 v2 只有 CNY，USD 未确认，不换汇。三原目录金额及缺失 usage 见 [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md)。独立物理模型质量数据另列；映射结果不能充当这类对照。

## 0. 研究定位与版本

### 0.1 新的统一思路

**选择实际可用的模型与原生档位候选，在单 Agent 执行中研究任务阶段、真实子任务边界和生成决策粒度，并用完整任务成功率及全成本检验路由是否带来净收益。**

- **配置层**：`provider / model / revision / native_effort`；同一模型的不同原生 Effort 是不同可执行动作，同模型不同 Provider 属部署/价格/可用性差异。
- **模型池层**：本轮固定用户选定的 K=3 目标池 Luna/GLM-5.3-Flash/Terra；RQ2 记录实际 Provider 身份、Effort 菜单与 Model×Native Effort 合法候选，不扩 K 或替换池成员。公开能力—成本 Pareto 仅作能力来源，不当作已验证的任务结果。
- **单 Agent 粒度层**：G 仅指原任务及其资料中实际存在的子任务边界；F 指模型生成路由粒度（每次生成、任务开始、真实阶段转折、真实子任务边界）。阶段识别不等于任务拆分，不研究 Agent 架构、角色或协作数量。
- **决策层**：单一 Router 在真实执行前观测状态与合法动作，选择 `Model×Native Effort`。执行后的真实费用、缓存和成败反馈成为下一决策输入。
- **经济层**：主指标是同任务完整 Episode 成功率与平均实际成本。目标是**在观测到的固定/随机混合前沿之外获得新有效点**，不是宣称超越理论所有策略的最优边界。
- **学术层**：模型池、任务粒度、Model×Effort、缓存历史各自建立可否证对照；最终端到端结果作为总评，不以 Laya/Kev 的训练 Accuracy 替代。

**当前正式主线（V9）**：**Overall Performance → Fixed-K=3 Model×Native-Effort Candidate Pool → Single-Agent Stage/Subtask/Generation Granularity → Systematic Ablation → Workload Applicability**。用户选定的三个目标身份保持固定；实际可用动作随 Provider 证据，不做扩 K 或成员替换实验。不包含多 Agent 设计、角色、协作、handoff 或 Agent 数量变量。

### 0.2 与项目现有资产的关系

| 文件 / 资产 | 本文如何使用 | 不在本文维护的事项 |
|---|---|---|
| [RESEARCH_OVERVIEW](../../our-project/planning/RESEARCH_OVERVIEW.md) | 方法总纲、H1–H7、受控状态、作用域 | 实时实验进度、最新 GPU 状态 |
| [EXPERIMENT_QA](../../our-project/planning/EXPERIMENT_QA.md) | Q-001=A 真实 Coding Benchmark；Q-002=B 商业+本地；Q-004=B 成功率约束；Q-005=B 分层基线；Q-006=A 同状态分支 | 未经负责人确认擅自改变决策或预算 |
| [PROJECT_STATUS](../../our-project/planning/PROJECT_STATUS.md) | 唯一实际执行状态和下一授权动作 | 历史对话中的计划当作已完成 |
| [PLANNING_MEMORY](../../our-project/planning/PLANNING_MEMORY.md) | 历史研究决定与跨 Agent 交接 | 将本文每个草案设成正式决定 |
| [GROUP_MEETING_RESEARCH_BRIEF](../../our-project/planning/GROUP_MEETING_RESEARCH_BRIEF.md) | 早期 RQ 命名与组会对照 | 将旧版 RQ 与本文版本混为同一正式版本 |
| [PAPER_NOTES_AND_FIGURES](../../our-project/汇报/ModelRouter组会/PAPER_NOTES_AND_FIGURES.md) | 已有论文**原图**资料与相关工作边界 | 把别人的论文截图当成本项目实验结果 |
| [训练看板](../../docs/training-dashboard/index.html) | 已完成 Laya 离线训练指标/Checkpoint 历史 | 冒充任务级经济评测 |


### 0.3 版本演进

| 版本 | 五个 RQ 的主要划分 | 关系 |
|---|---|---|
| V3 | 整体收益、任务结构、联合分配、长期成本、泛化 | 保留原任务粒度问题 |
| V4 讨论建议 | 任务级目标、决策粒度、联合分配、缓存、状态/复杂度 | 未单独落库 |
| V5 | 模型池前沿、全局收益、联合分配、缓存、重新路由 | 增加模型池，但任务拆分降为附属 |
| V6 历史草案 | 模型池、任务拆分/频率、联合分配、缓存/历史、端到端前沿收益 | 当时同时保留模型池与多子代理问题，5 个 RQ 不扩张 |
| V7 历史 | 模型池、任务结构、候选泛化、稀疏反馈、整任务经济收益 | 2026-10-13 方案，已被 V8 的 RQ 编号替代 |
| V8 历史 | 总体效果/机制、模型池、任务拆分、角色模型互补性、任务适用边界 | 2026-10-16 版本，原 RQ4 已废止，历史记录保留 |
| **V9 当前** | **总体效果、模型池、单 Agent 阶段/真实子任务边界/生成粒度、系统消融、任务适用边界** | 保留五 RQ、八图、十二表；RQ3 当前定义见文首 |

**V9 修订**：RQ1 只回答完整方法与强基线的总体表现；联合 Model×Native Effort、KV/Trace/反馈、输入信息组和监督/数据配方的**受控消融移入 RQ4**。完整 Episode 费用既是全部 RQ 的计量口径，也是 RQ1 主表和 RQ4 消融的共同评价指标。正式 Q-ID/H1–H7 不因论文重编号而改变。


## 1. 前沿定义与方法边界

### 1.1 三种前沿，三个不同对象

| 前沿 | 横轴 | 纵轴 | 数据与作用 | 可比较对象 |
|---|---|---|---|---|
| 公开能力—费用前沿 | 来源实际使用的 Cost per Task 或 Token Price | 来源 Intelligence / Benchmark Score | 同日、同版本来源快照；选池先验 | 同一公开指标内的配置 |
| 真实 Agent 固定配置前沿 | 所有任务的平均完整 Episode 费用 | 相同任务集 Resolved% | 固定 Harness、每个配置真实执行 | 同坐标的固定配置与混合 |
| 真实 Agent 动态策略前沿 | 含路由开销的平均完整 Episode 费用 | 相同任务集 Resolved% | 动态策略真实执行 | 同池、同任务的固定/动态策略 |

Artificial Analysis 是第三方，厂商自己的评测声明单独登记来源；两者均只在各自任务、版本和计价条件下定义前沿，本文不将它们混称为厂商造假。
Artificial Analysis 当前方法区分 Token Price、混合单价和它自身工作负载的 Cost per Task，后者包含真实消耗 Token；因此不能笼统说公开前沿都只是 Token 单价图，也不能把公开 Cost per Task 当作我们的 Agent Episode 费用。
两个面板的模型标签可以对齐，坐标数值与纵轴不能直接合并；实验证明的是外部指标迁移性和本任务域的策略增益。

### 1.2 何谓向左上改善

- Pareto 支配：费用不更高且成功率不更低，至少一项严格改善
- 同费用收益：ΔSuccess@Cost
- 同成功率收益：Savings@Success
- 固定配置之外的强对照：任务无关随机混合包络
- 数据范围：只比较实测支持重叠区间；成功率容忍度事前确定
- 不能成立的推断：低于最贵配置费用 → 整条前沿已经被支配

动态策略能够创造新的非支配点，但仍属于扩展策略集合自身的前沿，不能声称突破了所有可能策略的理论最优界。

### 1.3 最小方法闭环

```mermaid
flowchart LR
  PUB["AA/Public Static Frontier"] --> SELECT["Dev-only portfolio P_K"]
  PDATA["Existing Provider sources"] --> CAP["v9/capabilities: identity, scores, prices, missing values"]
  CAP --> SELECT
  CAP --> LEGAL["Existing constraints: legal Model × Native Effort"]
  SELECT --> LEGAL
  TASK["Original Single-Agent task"] --> G["Whole task or source-defined real subtask boundary"]
  STAGE["Observed phase label"] --> SNAP["Pre-decision state at generation boundary"]
  G --> SNAP
  EXEC["Existing Agent Harness: Generation / Tools / Verifier"] --> HIST["Observed tools, progress, verification, usage"]
  HIST --> SNAP
  REF["Two fixed successful TRAIN/DEV reference excerpts"] --> JUDGE["v9/teacher: optional EXTERNAL assessment"]
  HIST --> JUDGE
  SNAP --> JUDGE
  JUDGE --> SHORT["progress_summary / main_blocker / next_milestone + cutoff and provenance"]
  SHORT --> ENCODE["Actual shared state text / encoding; offline and online same meaning"]
  SNAP --> ENCODE
  CAP --> ENCODE
  ENCODE --> ROUTER["Single active Laya OR Kev Router"]
  LEGAL --> ROUTER
  ROUTER --> EXEC
  JUDGE --> COST["Online teacher + Agent USD / tokens / latency"]
  EXEC --> COST
  COST --> OUT["Episode Resolved / Complete USD / Latency"]
```

用户选定的目标池固定为 K=3；RQ2 研究该固定池中每个身份的真实 Model×Native Effort 候选及其 Provider 能力。RQ3 **固定池/Router，比较原任务整体或真实子任务边界 G 与生成决策粒度 F**，RQ4 **固定池/任务/评测口径改动作、可选信息或训练监督**，RQ5 **固定 Router/池/生成粒度比较预定义工作负载条件**。同一单活跃 Laya **或** Kev 负责联合候选选择，教师只加工状态，原单 Agent 继续执行。实际动作数由 Provider 证据确定，不将 15 个规划候选或缺失 GLM 绑定写成已可执行。`v9/training` 复用原 Trainer/控制器，把离线真实前缀、三字段和合法监督送入同义编码；不新增 Agent 循环、训练队列或监测状态来源。当前图表达要求，新特征未学习标 `FEATURE_NOT_TRAINED`。

### 1.3a · 输入字段和模块接口：三字段、实际编码与能力卡（2026-10-29）

**结构定位**：外置教师在原 Agent Harness 之外、Router 之前，参考当前 `decision_id` 截止的真实前缀与两条固定成功公开摘要（高效完成/失败恢复）。输出三核心字段及来源/费用，实际进入 state/编码；不执行工具、不选生成模型、不提供隐藏解答。顶级教师与 Qwen 联调分别注明实际身份和用途；审阅子 Agent 配置不能替代教师配置。约三次生成或阶段/恢复/停滞触发是 Dev 起点，尚无效果验证。

| 输入对象 | 字段（拟议） | 解释和来源 |
| --- | --- | --- |
| `task_state` | `task_id, task_summary, task_domain, source_defined_subtask_id, stage, step_index, remaining_steps, context_tokens, remaining_time_seconds, remaining_budget_usd` | 单 Agent 当前任务与已知预算；子任务边界须有原始来源 |
| `tool_trace` | `recent_tool_events[{tool_name, tool_intent, args_digest, observed_result, observed_at}], progress_milestones, verification_status, recovery_attempts` | 只记录已经发生的行为，退出码不是合理性结论 |
| `external_trajectory_assessment` | `progress_summary, main_blocker, next_milestone` | 教师推断实际进入 state 文本/编码，离线/在线同义；不能作终局或最优动作标签 |
| `assessment_provenance` | `assessed_through_decision_id, teacher_provider, teacher_model_id, teacher_native_effort, reference_trajectory_ids, reference_split, trigger_reason, generated_at, teacher_input/output_tokens, teacher_cost_usd, teacher_latency_ms, status` | 固定两参考；实际顶级/联调教师分开，离线制作与在线 Episode 费用分开 |
| `continuity` | `previous_model_id, previous_native_effort, context_tokens, reported_cached_tokens, estimated_prefix_overlap, session_affinity, estimated_switch_penalty` | 同一连续消息上下文、额外重发 Token/费用与 Provider/引擎实际 KV/缓存双记 |
| `legal_actions[]` | `provider, model_id, revision, deployment_id, native_effort, action_id, available_now, supports_tools, context_limit, price_snapshot_id, capability_evidence[]` | 先硬过滤；动作是具体型号+该 Provider 真正支持的档位 |
| `capability_evidence[]` | `benchmark_id, version, metric, score_raw, score_normalized, harness, evaluator_revision, eval_split, evaluated_effort, sample_count, eval_date, source_url, evidence_status` | 每档 Effort 的实测分数仅在确有同协议结果时填；未测=NOT_MEASURED |
| 模型映射与学习状态 | 逻辑 ID、实际 Provider/API 模型/端点/部署、`ALIAS_SMOKE`、`FEATURE_NOT_TRAINED` | Alias 不填正式三模型比较；API 前向不证明新特征已学习，9002 与 Parfit API 身份分开 |

**Benchmark 能力维度**：M保存每个独立Benchmark的原分、单位、评测Effort、模型/AA身份、来源及版本。v7各实测动作有10项，GLM Low/High仅有其他档位Max参考；Coding/Agentic Index、revision和官方发布时间尚缺。Index版本5.0.1，能力先验与Terminal-Bench 2.1真实任务结果分别记录。TTL86400秒、force、STALE及同批固定snapshot_id已实现。

**实验和安全边界**：Final 的未来轨迹、答案、最终 verifier 或结局不得进入教师、训练、选池和调参。无教师标 `NOT_USED`，调用失败标 `FAILED`；不把缺失或回退算有效评审。现有 F05/F06/C03 和当前服务权重尚无新特征学习证据，记 `FEATURE_NOT_TRAINED`。RQ4 比无评审/确定性摘要/独立教师、名称+Effort/能力分数、工具返回/真实行为进展；只有正式真实 Episode 才填任务效果。教师制作、权重编码/学习与 API 前向证据分别记录。

### 1.4 证据要求

- `E0` 公共能力/价格表：只支持公开静态指标，不能直接推断 Agent Episode 结局。
- `E1` CCH/Blog 观察调用：支持已记录的单次成本/缓存/Token；缺少真实 task_id 的不能推断整任务成功。
- `E2` 历史 Agent 轨迹：只支持已执行动作的观察结果，不能给未执行动作伪造未来标签。
- `E3` 真实同任务 Episode：支持路由策略成本—成功率比较。
- `E4` 同一决策前状态的可恢复分支：支持受控动作间后续费用/成功差异。
- `E5` 固定策略的独立 held-out：支持预设质量约束下的泛化与置信区间。

### 1.5 成本边界

完整任务 API USD 按真实 input/output/cache 用量乘所选逻辑目标身份价格，覆盖生成、在线教师及失败调用中已报告的 usage；同一调用只计一次。生成输出按 `completion + reasoning` 计一次，教师输出按 `completion` 计。离线教师制作费用归数据/训练，单独记录。映射实验真实请求后端为 Qwen3.8-27B；后端身份、后端价格和供应商实收另列，缺失不影响映射实验。教师按配置教师目标身份计价。Sol 使用 v2 已保存官方 `2/10/0.1/2.5`；Flash 使用原 snapshot `20261018` 的 OpenRouter 公开 USD 参考 `0.15/0.47/0.016`，阿里官方 v2 只有 CNY，USD 未确认，不换汇。Mac 不存 Laya/Kev 权重。缓存用量缺失保留 null，按普通输入价处理。当前不设 API 总 Token 或美元上限。真实 Luna 官方 Episode 与映射实验分开；完整金额需要相关 usage 齐备。

**历史实际单位与状态（旧金额保留，当前计费政策见上段）**：hcnsec `raw_usage.cost` 无 `currency/cost_currency`，新请求保留 `raw_reported_cost`、`reported_cost_unit=NOT_REPORTED`，仅明确 USD 才赋 `actual_billed_cost_usd`；未知单位不计美元、旧事件留版本。离线两请求 prompt 13,766+completion 949=14,715 Token，reasoning 678 已包含于 completion，cached 0 已报告、USD null，结果复用与物理缓存分开；这笔制作费用归数据/训练，不进入在线 Episode。单题 9 次生成/13 次 Bash/7 项 unittest 成功终局、Laya 全程 `fallback=false`、Checkpoint `epoch_01`，仍仅 Sol 逻辑选择的控制链证据；额外短 Provider 验证和 Native 回放不算新题。所有请求完整 prompt/completion/cache/USD 因失败 usage 缺失仍 null，不写零，正式表继续空白。390 行唯一材料、choice 目标 0、`GENERATED=4 / NOT_GENERATED=386`、AA 仍 0 条实测能力记录分别保留；AA 来源 Sol 404/Luna 200 解析失败/Flash 404、Key 缺失，不把响应成功或缺测数当能力分。原已知 Token/失败预留属历史时点，不推算最终余额，不报新训练已就绪。

## 2. 五个研究问题（V9，最新确认）

> 本节为当前**正式确定**的 RQ1–RQ5。现行方法只研究单 Agent；旧 V8 角色互补性和多 Agent 组织仅作为历史。

| RQ | 白话问法 | 主要变化轴 | 图 | 表 |
|---|---|---|---|---|
| **RQ1 Overall Performance** | **我们的动态 ModelRouter 与相同任务环境中的其他路由方法相比，整体成功率—成本表现如何？** | 相同工作负载/模型池/Harness/预算下改变路由策略 | Fig.3–4 | T3、T10（成本账本） |
| **RQ2 Fixed Pool Model×Effort** | **在固定 K=3 目标池中，Provider 实际支持哪些 Model×Native Effort 候选？** | 固定用户目标身份；按 Provider 证据记录合法联合动作，不扩 K/换成员 | Fig.5 | T6 |
| **RQ3 Single-Agent Granularity** | **单 Agent 的阶段识别、真实子任务边界与生成决策粒度如何影响完整任务？** | 同一任务的实际 G 边界及生成决策粒度 F | Fig.6 | T7 |
| **RQ4 Systematic Ablation** | **Router 究竟靠哪些设计发挥作用？联合模型与档位、状态信息、训练数据/监督，哪些必要，哪些组合有效？** | 固定任务/池/评测，仅改变受控组件、输入信息组或训练配置 | Fig.7 | T4–T5、T8、T11 |
| **RQ5 Workload Boundary** | **哪些事前可观察的单 Agent 工作负载更适合动态路由？** | 任务类别、难度/长度及原始材料中真实存在的子任务结构 | Fig.8 | T9 |

### 2.1 动作树、状态与训练的边界

- **Model pool**：K 统计不同模型身份，池成员为 `provider/model/revision` 的实际候选；每个模型有不同且真实存在的原生 Effort 集合 `E_m`，不能由用户提前规定每个 Agent 固定用哪个模型。
- **Single Router**：每个合法调用边界，由一个路由策略在可变长 `{(m,e):m∈P,e∈E_m,legal(m,e,s_t)}` 中**同时选择模型与这个模型自己的 Effort**。树按“模型→原生档位”组织，不能把几十个固定组合当成永远不变的类别。缓存、角色和历史信息属于状态/候选条件特征。
- **Single-Agent state**：任务目标、原始资料中的真实子任务边界、当前阶段、上下文、KV/Usage、已发生工具和验证反馈、剩余预算。阶段标签不自动变成拆分，不记录 Agent 角色、协作或 handoff。
- **证据**：S1 偏好、S2 观察性轨迹、S3 缓存辅助不是同状态、全候选 `(m,e)` 的最优反事实标签；不能从一个成功轨迹推断未执行模型会失败。

### 2.2 RQ1：完整 Router 的总体性能（已确认局部调整）

**科学问题**：在可复现的真实 Agent 任务中，相同模型身份池、真实原生 Effort 菜单、Harness、预算与最终验证规则下，ModelRouter 是否优于具有竞争力的固定、混合、简单动态以及可兼容的公开路由方法？本 RQ 仅做最终方法横向比较；机制、输入变量、训练配方归正式 **RQ4 系统消融**。

- **主对照**：固定强/低价配置、开发集最优固定策略、整任务固定策略随机混合、Task-only、Greedy、Rule/Sticky、轻量 Router；只纳入在同一单 Agent 执行接口可运行的真实算法。
- **共同条件**：相同任务 ID、原始任务集合、工具/容器/终局 Evaluator、候选模型身份和每个模型自己的合法原生 Effort、可比 API 预算/成本计价与路由频率规则；对不支持动态 Effort 的外部方法明确注释动作能力差异。
- **主指标**：Task Success Rate、Mean Complete Episode USD、Cost per Resolved；补充真实 Router 费用/延迟、P95 Episode Time、按独立任务计算的置信区间。失败任务和已发生的失败重试费用全部计入总费用，不能重复计价。
- **核心结果图表**：Fig.3 成功率—Episode USD Pareto，Table 3 同环境横向对照；费用 ledger 用 T10 作为任务级总成本口径说明，并不在此宣称任何模块有贡献。
- **可证伪性**：Full 可能无法超越认真选择的双模型整任务随机混合或开发集最佳固定，也可能被自身路由开销抵消；均须如实报告。

### 2.2A 消融实验索引（正式归属为 RQ4，详细定义见 §2.5）

> 本节是 RQ4 系统消融的索引；更早独立的角色互补性研究只保留为历史，不属于现行因素。

- **A｜动作结构消融**：Fixed Model+Effort、Model-only（模型动态、每模型合法 Effort 预先固定）、Effort-only（模型固定）、Hierarchical Model→Effort、Joint Model×Native Effort；考察联合动作在实际任务上是否产生净收益，并分别说明候选动作空间是否相同。
- **B｜决策输入消融**：T（任务/来源中真实存在的子任务边界/阶段）、M（模型能力和候选经济性）、H（上下文/KV/已发生 Trace 和验证反馈）的单组、双组、三组组合；根据开发集再细分关键字段。**所有模型合法性、Effort 支持、工具/权限硬约束保持启用**；去掉某组评分特征不是允许非法调用。
- **C｜训练证据消融（新增讨论方向）**：在确实能合法训练与配对的前提下，对比 S1 静态偏好、S2 观察性 Agent 轨迹、S3 缓存/调用辅助及其合规组合的作用，或 Laya/Kev Checkpoint/数据配比的真实影响。固定任务、池、评测条件，对照离线指标和真实 Episode 表现；绝不将异构观察数据当作同状态所有未选动作的反事实真值。
- **D｜运行开销与费用解释**：实际 token、reasoning、缓存读写、失败重试、路由器本身成本与延迟单独计账；这部分也可作为全论文共有的成本测量，不一定占一个消融子题。
- **实验组织**：先分组，不穷举全部原始变量；对测过的负结果做汇总，依据开发集定最终模型、独立测试不参与事后筛选；端到端成功率与 Episode USD 才能确认最终经济价值。



### 2.3 RQ2：固定 K=3 目标池中的 Model×Native Effort 候选

**科学问题**：在用户选定的固定 K=3 目标池中，每个 Provider 实际支持哪些原生 Effort，组成怎样的联合候选集合？这些模型与档位的真实能力证据和终局效果如何记录？

- 目标身份固定为 Luna、GLM-5.3-Flash、Terra；不开展扩 K、换成员或替换成其他池的对照。
- 每批记录精确 Provider/model ID、真实原生 Effort、实际支持条件及合法 Model×Native Effort 数；15 是规划数，不补造缺失组合。
- GLM 渠道尚未绑定，精确 ID/能力结果待 Provider `/models` 返回；不把 GLM 记为已可用或已实测。
- AA 分数按精确 model×effort 保留实测来源；当前刷新进行中，未返回项目保持空白或 `NOT_MEASURED`。模型级指数不复制成逐档成绩。
- 真实任务成功率、完整 Episode USD 与每个动作的覆盖在有 Harbor 执行结果后填入；固定目标池不是 3 个 Provider 已全部可用的声明。

### 2.4 RQ3：单 Agent 阶段、真实子任务边界与生成决策粒度

**科学问题**：固定模型池、Router、单 Agent Harness 和评价协议，任务中的真实子任务边界 G 与路由决策粒度 F 是否改变完整任务质量和成本？

- G 只来自原任务定义或已保存材料中可证实的实际子任务边界；没有明确边界时记为整任务，不人为拆分。
- F 比较任务起点、实际阶段转折、实际子任务边界和每次模型生成等粒度；阶段标签本身不是任务拆分。
- 在相同任务/工具/Router/候选动作/官方终局下比较；记录真实决策次数、成功率、完整费用和路由耗时，不增加 Agent 数/角色/handoff 变量。
- Inspect、Modify、Verify、Recover 仅作阶段状态；不能单独作为 G，也不能从阶段名称推断任务需要多个步骤或多个决策。

### 2.5 RQ4：哪些设计与训练信息真正决定 ModelRouter 的任务级效果？（系统消融）

**2026-10-22 新增 RQ4 对照**：外置轨迹评审（无/确定性摘要/独立教师短评）与教师费用/时延；工具合理性（仅看错误码 vs 参考成功轨迹引导的阶段/工具意图/重复/进展/验证）；候选输入（仅真实型号+原生 Effort vs 额外有来源的每档 Benchmark 能力卡）。固定同一合法候选池、任务、Harness、预算和验证协议，比较真实完整 Episode 费用与成功率；未证明有效前不把教师短评和能力分数写成最终方法必要项。


**科学问题**：在固定的实际 Agent 任务、模型身份池、各模型原生 Effort 菜单、Harness 和真实终局评测下，完整 Router 的性能来源于哪些组成部分？联合动作选择、决策前状态信息和训练数据/监督是否有独立贡献或组合交互，是否值得其额外运行成本？

**RQ4-A｜路由动作维度**（表 T5）：
- 固定 Model+Effort；Model-only（模型动态，Effort 用每模型合法默认档位）；Effort-only（固定同一模型，动态选择该模型合法 Effort）；分层 Model→Effort；完整**单一共享评分器联合 Model×Native Effort**。
- 每模型 Effort 档位必须来自 Provider 实际支持，不用人为设定统一 Low/Medium/High；明确行动空间变化可能带来上限变化，不把动作空间扩张误当路由器训练优势。

**RQ4-B｜决策信息与组合贡献**（表 T4）：
- 分组 T=任务需求/Agent 子任务（可含已知角色）；M=候选模型能力与经济性；H=决策前已有 Trace/上下文/KV/验证反馈/预算。
- 最小矩阵：T、M、H、T+M、T+H、M+H、T+M+H（在合法过滤、官方价格/权限/工具/context 硬规则始终存在的条件下）；再对真实共现、允许训练的 KV/Trace/Agent role 等子字段开展有重点的单项剔除。
- 信息组本身不是动作类别；当前大规模异构训练数据不具备完整八类状态同一条真实联合监督，无法把缺测字段硬填成“所有变量均可用”。允许无效变量从最终实现中删除，但已测负结果须保留记录。

**RQ4-C｜训练数据与监督方式**（表 T8、附录 T11）：
- 比较真实合法 S1 人类偏好、S2 已执行 Agent 轨迹、S3 缓存/调用辅助，以及**经许可、时间截断并实际进入输入编码的**组合；报告独立训练单元、样本覆盖、数据来源/许可证、固定训练预算、验证指标与最终任务级收益。
- Laya / Kev 的不同训练阶段、代表性 Checkpoint/数据配比可在同条件下对照，但不能把异质数据行当独立决策标签，更不能由已执行轨迹生成未选动作的最优答案。
- 训练配方本身与学习器架构差异应分开对照；若资源不足先做最能判别因果的重点对照，不为 92 种组合穷举而耗费大量 API。

**RQ4-D｜净费用与必要性**（Fig.7）：
- 汇总每个消融配置的 Task Success、完整 Episode USD、Cost/Resolved、Router 延迟与额外费用；真实 token、reasoning、cache、失败重试费用可从 T10 复用。
- 只在开发集选变量，独立 Final 评价已选定策略；不隐匿无显著收益或变差的结果。某变量在当前实验中没有净收益，结论只适用于已测条件。

**RQ1 与 RQ4 的严格分工**：RQ1 只证明最终完整方法与外部/简单基线的横向差异；RQ4 固定外部条件，改变 Router 自身动作、输入或训练数据来解释这种差异。即使总体无收益，RQ4 仍可报告各模块的真实影响。

**主图**：Fig.7 为三面板（A 联合动作、B 信息组、C 训练数据/监督）；必要时另以小面板列 Router/Cache 开销。不画虚假提升曲线。**主表**：T4、T5、T8；补充 T10/T11。


### 2.6 RQ5：哪些单 Agent 工作负载值得动态路由？

**科学问题**：动态路由相对于有竞争力的简单策略，其**任务级净收益**是否随任务类别、预先可观察的任务规模，以及原始任务中已有的子任务结构发生系统变化？能否识别没有路由收益空间的场景？

所有任务均可经过原 Router；RQ5 研究不同条件下的实际收益，不给正常任务增加调用限制。依据：下载讨论行 28868–28876。

- **实验**：固定 Router、池和生成决策粒度，按事前可观察的单 Agent 任务类型、规模/难度及来源中真实存在的子任务边界分层；不根据阶段标签制造子任务。
- **主对照**：每个工作负载分层重用 RQ1 的固定、随机 Episode Mix、Rule/Sticky 和其他可比强基线，与 Full Router 对比；计算每层在相同成功率条件下的任务费用差和不确定性。
- **预定义工作负载与收益交互**：事前规定可观察的工作负载特征，检验 `policy × workload` 的收益交互；以跨类型复测和足够独立任务支撑“适用边界”，不能靠观察到好结果再筛选任务类型。任务完成后的实际 Trace/失败次数只能用于机制解释，不能冒充任务开始前的条件。
- **RQ1 区别**：RQ1 回答整体上有没有收益；RQ5 回答**在什么任务条件下有收益/无收益且是否稳定**。
- **RQ3 区别**：RQ3 比较阶段识别、真实子任务边界与生成决策粒度；RQ5 固定所选粒度，比较**工作负载原有差异**，不把不存在的拆分作为处理条件。
- **证伪情况**：收益与所选任务特征没有稳定关系，或样本过少以致无法可靠划定边界；必须如实报告。
- **主图**：不同预定义工作负载（任务类型×复杂度/真实子任务结构）的`Full vs 强基线`净经济收益矩阵和分层置信区间。不要为了作图捏造任务类型覆盖。

### 2.7 论文逻辑与必要数据

- **数据优先**：RQ1–RQ5 均需要真实完整单 Agent Episode、终局成功标签、当时合法池及完整费用；**RQ4** 额外要求每种训练监督/信息组的真实覆盖、可比 Checkpoint 和合法输入编码证据；**RQ5** 要有预定义的独立任务工作负载分层。
- **现有训练缺口**：已加工轨迹含 `agent_framework`、消息 role、step/context 及部分 thinking mode；这些字段不构成研究中的 Agent 角色变量，不能据此补造任务拆分或最佳 Model×Effort 标签。
- **微调定位**：Laya / Kev 的 S1/S2/S3 联合训练和 Checkpoint 比选是 Router 的训练证据，继续作为方法、训练记录和附录；离线 Accuracy 不是 RQ1–RQ5 的任务级成绩。


## 3. 实验安排与已有资产

### 3.1 Benchmark 来源：先真实任务，后逐层扩大

遵循已确认 Q-001=A：技术试跑选真实开发任务，不另造合成任务。mini-SWE-agent 是框架；SWE-bench Lite/Verified 与原 Terminal-Bench 2.1 + Harbor + mini-swe-agent 的任务、Evaluator、环境和成绩独立，TwinRouterBench 是另一评测资源，SWE-Gym 等是训练环境/轨迹源。Terminal 保留 **Canary 8 / Dev 24 / Final 57**；SWE 划分另按任务/repo/近重复内容登记。早期 10 个烟测、约 50 个开发任务、100+ 评测任务只留作预算讨论锚点，不替代当前 Terminal 划分或表示已执行；多策略/模型/seed 的调用费用照实累计。

- Split 单位：task/repo/近重复 issue；同一任务的轨迹前缀不能跨 Train/Val/Test。
- Terminal outcome：可执行 evaluator、补丁/测试规则、timeout、环境版本、成功/失败/中断原因。
- 模型池：商业 + 本地混合（Q-002=B），官方实际可用 Native Effort、上下文、工具、缓存计价和故障 fallback。
- 用量与费用：用户明确从未设置 API 总 Token 或美元预算，按任务需要充分测试及部署，保留服务器资源规则；生成/教师/重试照实累计用量并按适用官方价核算。三逻辑身份已确定，当前 Provider 研究池只列 Luna，Sol/托管Flash未列出；实际供应商可用性不转写为等待人类批准。非劣容忍度仍待研究方案明确，bill 未知单列、不作执行条件。
- Final 与训练/Dev 分开；仅作独立最终评测，不用于训练、选池、调参、教师输入或反复挑权重。本轮不运行 Final。


### 3.2 V9 实验安排（以科研必要性排序）

| 顺序 | 目的 | 对应 | 结果图表 |
|---|---|---|---|
| A | 对齐 Harbor `DefaultAgent` 与原 Evaluator、固定 K=3 目标身份、真实原生 Effort 和完整费用口径；GLM 授权确认前不启动新 K=3 实验 | Setup | Fig.1–2, T1–2 |
| B | 同池同任务运行固定/随机混合/简单/可比 Agent Router/Full，完成主要任务级横向对照 | RQ1 | Fig.3–4, T3/T10 |
| C | 固定池与任务做联合动作、T/M/H 信息单双三组合、训练数据/监督与费用开销的系统消融 | **RQ4** | **Fig.7, T4–5、T8、T10–11** |
| D | 固定用户目标池 K=3，依实际 Provider 能力记录 Model×Native Effort 联合候选及真实覆盖 | RQ2 | Fig.5, T6 |
| E | 固定模型池身份/K=3/原生 Effort/Router，比较真实子任务边界与生成决策粒度 | RQ3 | Fig.6, T7 |
| F | 对照合法训练数据/监督的真实效果，核验动态输入编码并报告独立样本、训练开销和最终任务级效果 | **RQ4（训练消融）** | **Fig.7, T8/T11** |
| G | 固定池/Router/G，预先定义工作负载分层，比较 Full 相对强基线的任务级收益边界 | RQ5 | Fig.8, T9 |
| H | 报告费用分解、真实训练证据和代表性任务轨迹；独立 Test 不用于事后挑池/变量 | 全部 | T10–12 |

**讲述顺序**先 RQ1，再解释固定 K=3 池内的 Model×Native Effort 候选、单 Agent 生成粒度、系统消融和工作负载边界。实际采集可复用同一 Episode 与账本；不能将不同任务拼成假配对，Alias 前向/联调不能充当正式新池结果。

正式执行只沿 Harbor `DefaultAgent` 与原版 Evaluator；已删除的 `sandbox/canary_verifier.py`、`experiments/harbor` 同名 shim 和本地 Demo 均不是入口。旧 Mock 分数仅作历史记录，不提供 smoke 命令。原始报告中的 Mock 环境和分数不改名、不改写。正式 RQ1–RQ5 在真实身份/协议下另作比较，不重复建设底层 Router/Provider。


### 3.3 微调支撑路由研究，论文主体关注方法与任务效果

- Laya 的 Batch 1、Sweep-02、Full-Graded 属**离线监督能力与数据方案探索**，训练指标可放附录 T10/T11 及补充曲线，不宣称 Cost-per-Resolved 改善。
- 原研究起点以 Kev-4B 为候选；现行使用同一入口的单活跃 Laya 或 Kev，代表权重各用同协议 Val 与独立 Dev 选择。V2.1/L1 及 S1 偏好、S2 已观测 Agent、S3 请求/缓存辅助分别保留；Q/S/L、行数、独立单位和路由比较标签不能混合。教师三字段与能力特征须真实编码，新特征未学习记 `FEATURE_NOT_TRAINED`。
- 已分级的 660 万异构行和约 486 万合法候选，属于数据资产，不能当作 486 万独立路由标签；训练覆盖率和路由成功率完全不同。
- 只有同状态多动作真实结果（或明确标示为估计并承认偏差）才支持相对动作选择监督；测试集和许可证待核内容不能训练。
- 是否需要更复杂学习目标取决于真实 Benchmark 与简单规则的比较，不以 Checkpoint 个数决定论文质量。



## 4. 八张图的 V9 设计（结果点全部留空）


### Fig.2 · 单 Agent 方法主图（当前可编辑图源）

**图的定位**：只表达原任务与真实子任务边界、单 Agent 阶段/决策前状态、可选教师、Provider 合法候选、单一 Router、原 Mini-SWE 执行循环、下一生成前反馈和 Harbor 官方终局。不得画多个 Agent、角色分工、协作、handoff 或数量变量。可编辑 Mermaid 图源唯一维护在[研究总纲 2026-11-07 Fig.2 节](../../our-project/planning/RESEARCH_OVERVIEW.md#2026-11-07--现行-fig2-方法定义)。

**RQ3 真实循环与粒度**：G 只取原任务或已有真实执行材料能够确认的子任务边界；F 记录生成路由时机。`inspect/modify/verify/recover` 仅作阶段识别，不能单独变成任务拆分。工具命令不等于模型生成。教师读取截止前前缀并输出三字段，进入同一状态编码；下一次模型生成仍经过同一个 Router。

**模型与证据范围**：目标候选为 Luna、GLM-5.3-Flash、Terra，规划 15 个 Model×Native Effort 动作；精确 ID、Effort 和可用性按 Provider 实际证据，不将历史 HY4 执行改写成新池结果。图中不填虚构能力、价格或实验结论。AA 每档能力须来自真实测量；TTL/force 刷新与 GLM 可用性仍在获取/实现过程中。Laya/Kev 可替代，但单次只活跃一个 Router。



> **逐页制作说明**：参见 [导师汇报 V8 详细提纲](汇报提纲.md)。建议只有封面与 Agent 工作流两张 AI 场景插画（另可选一张训练/证据概念插画）；**Fig.2 已采用中文生图方式制作初稿；投稿前须按本节完整语义修正小字、箭头和模型证据，不能把图像生成误差视为真实方法**；Fig.1、Fig.3–8 的统计图当前保留精确轴、对照组和空白结果区域。

| 图 | 对应 | 坐标/结构与最终要回答的问题 |
|---|---|---|
| Fig.1 | Motivation | 静态 AA Intelligence–Price 与真实 Agent Success–Episode USD **两个独立面板**，不能把 AA 结果当 Agent 任务结果 |
| **Fig.2** | Method | **Model→Native Effort**、连续 AgentState/真实前缀→两条固定成功公开摘要与外置教师三字段→**实际 state 编码**；能力/价格/合法动作同义输入→**单活跃 Laya 或 Kev**→原 Agent 执行→真实费用/验证/上下文与物理缓存反馈 |
| **Fig.3** | **RQ1 主结果** | X=Mean Complete Episode USD，Y=Task Success Rate；固定、随机整任务混合、简单、同 Harness 学术 Router、Full；真实实测后绘 Pareto |
| Fig.4 | RQ1 结果解释 | 完整 Episode 生成/缓存/在线教师/Router 费用分解及成功率—费用对照包络；失败重试是已计调用的子集，不重复相加，离线教师制作另列；不重复 Fig.7 消融 |
| Fig.5 | RQ2 | 固定 K=3 目标池内各 Model×Native Effort 候选的真实覆盖与 Success–Episode Cost；标明 Provider 支持状态和合法动作数 |
| Fig.6 | RQ3 | 分别展示 G（原任务/真实子任务边界）与 F（生成决策粒度），比较成功率/完整 Episode USD；阶段识别单独记录，不含角色、Agent 数或 handoff |
| **Fig.7** | **RQ4 系统消融** | 三面板：A 固定/Model-only/Effort-only/分层/Joint；B T/M/H 单双三组与**外置 LLM 轨迹短评/候选分数**的有无及规则摘要对照；C S1/S2/S3 合法数据与监督配置；真实 Success/完整 USD（含教师费用）衡量，结果待测 |
| **Fig.8** | **RQ5** | X=预定义单 Agent 任务属性/规模及真实子任务边界分层，Y=在可比成功率下 Full 相对强基线的**任务级费用改善**及不确定性；无收益区域同样保留 |

**不得填假坐标点或预设正收益**。Case trajectory、Provider cached-read 细节和失败案例可作补充图；图 8 不得简单重复图 3 的总体平均数。


## 5. 十二张空白结果表（V9）

> PPT 表格展示策略：P06 缩略展示 T1/T2 的 Benchmark/池/协议；P07 展示 T3；P08 展示 T4/T5/T10；P09–P12 分别展示 T6–T9；T11/T12 留在备用/附录页。各表行、列的口径与讲述逻辑见 [详细汇报提纲](汇报提纲.md)。

**全部结果单元格空白，不意味着零。** 第一列只是计划对照条件，实际有没有该 benchmark/模型、能否运行需以之后的执行证据为准。数据采集只需一套共享 Episode/Agent/Decision 账本，结果表从同一事实派生；没有真实结果不填数字。

### Table 1 · 固定 K=3 目标池与 Provider 能力（Setup）

| Model Identity | Provider / Revision | Allowed Native Efforts | Context | Tools | Input $/M | Output $/M | Cache Policy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-6 Luna（目标身份） |   |   |   |   |   |   |   |
| GLM-5.3-Flash（渠道未绑定；精确 ID 待查） |   |   |   |   |   |   |   |
| GPT-6.1 Terra（目标身份） |   |   |   |   |   |   |   |

> **T1 补充**：三者是固定目标池身份，不表示均已绑定或可调用。GLM 私有渠道尚未绑定，Provider 正在查询 `/models`；low/high/max 是待核对的预期档位。15 个 Model×Native Effort 候选是规划数；表内只填实际 Provider 证据。AA 刷新正在进行，未返回数据留空；不将模型级分数复制到档位，也不把旧 HY4 结果写作 GLM。

### Table 2 · Harbor 单 Agent Benchmark / 协议（Setup）

| Benchmark / Task Set | Independent Tasks | Source-defined Subtask Boundaries | Single-Agent Harness / Evaluator | Development / Test Split | Cost Scope |
| --- | --- | --- | --- | --- | --- |
| Terminal-Bench 2.1 Canary / Dev / Final |   |   | Harbor `DefaultAgent` / official Evaluator |   |   |
| Other authorized single-agent task set |   |   |   |   |   |

### Table 3 · RQ1 同类 Router 主结果

| Policy | Task Success ↑ | Mean Episode USD ↓ | Cost / Resolved ↓ | P95 Time ↓ | Router Overhead ↓ | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Fixed-Strong |   |   |   |   |   |   |
| Fixed-Cheap |   |   |   |   |   |   |
| Best-Fixed-on-Dev |   |   |   |   |   |   |
| Random Whole-Episode Mix |   |   |   |   |   |   |
| Task-only Router |   |   |   |   |   |   |
| Greedy / Rule / Sticky |   |   |   |   |   |   |
| Adapted Agent Router (named algorithm) |   |   |   |   |   |   |
| Full ModelRouter |   |   |   |   |   |   |

### Table 4 · RQ4 信息组单/双/三组合消融

| Information Used | Valid Action Space | Task Success ↑ | Mean Episode USD ↓ | Δ vs Full | Router Cost |
| --- | --- | --- | --- | --- | --- |
| T: Task/Stage/Real Subtask |   |   |   |   |   |
| M: Candidate Economics |   |   |   |   |   |
| H: Execution History |   |   |   |   |   |
| T+M |   |   |   |   |   |
| T+H |   |   |   |   |   |
| M+H |   |   |   |   |   |
| T+M+H |   |   |   |   |   |
| Full minus KV |   |   |   |   |   |
| Full minus Verifier feedback |   |   |   |   |   |
| Full minus external LLM trajectory assessment |   |   |   |   |   |
| Deterministic tool-history summary (no teacher LLM) |   |   |   |   |   |
| Full minus per-effort Benchmark ability evidence |   |   |   |   |   |
| Full minus both teacher and capability evidence |   |   |   |   |   |

教师/能力卡重点比较**无二者、仅教师、仅能力卡、两者共同使用**，复用上述条件和同一实际编码。价格、授权、上下文等必要约束保留；新增特征未学习记 `FEATURE_NOT_TRAINED`，不能把相同旧权重接受不同 JSON 记作有效训练消融。依据：下载讨论行 28858–28866。

### Table 5 · RQ4 Model×Native Effort 联合动作消融

| Action Policy | Model Dynamic? | Effort Dynamic? | Task Success ↑ | Mean Episode USD ↓ | Reasoning Tokens | P95 Time |
| --- | --- | --- | --- | --- | --- | --- |
| Fixed Model+Effort |   |   |   |   |   |   |
| Model-only |   |   |   |   |   |   |
| Effort-only |   |   |   |   |   |   |
| Hierarchical M→E |   |   |   |   |   |   |
| Joint M×E |   |   |   |   |   |   |

### Table 6 · RQ2 固定 K=3 池内 Model×Native Effort 证据与结果

| Fixed Pool Model | Native Effort | Provider Evidence | Legal Action in Batch | Task Success ↑ | Mean Episode USD ↓ | Evidence / Coverage |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-6 Luna |   |   |   |   |   |   |
| GLM-5.3-Flash |   |   |   |   |   |   |
| GPT-6.1 Terra |   |   |   |   |   |   |
| Fixed K=3 pool summary |   |   |   |   |   |   |

### Table 7 · RQ3 单 Agent 阶段、子任务边界与生成粒度

| Task / Same Task Set | G: Whole or Source-Defined Subtask | Stage Label (observed) | Generation Granularity F | Policy | Task Success ↑ | Episode USD ↓ |
| --- | --- | --- | --- | --- | --- | --- |
| Coding: Whole Task |   |   | Task-start | Fixed |   |   |
| Coding: Whole Task |   |   | Every generation | Full |   |   |
| Coding: Source-defined Subtask |   |   | Subtask boundary | Full |   |   |
| Coding: Same Task |   | `inspect/modify/verify/recover` | Actual stage transition | Full |   |   |

### Table 8 · RQ4 合法训练数据/监督与微调策略消融

| Training Variant | Source / S1-S2-S3 | Independent Train Units | Input Feature Coverage | Fixed Training Budget | Offline Validation | Task Success ↑ | Episode USD ↓ |
|---|---|---|---|---|---|---|---|
| S1-only（合规子集） |  |  |  |  |  |  |  |
| S1 + S2（合规且真实已观察） |  |  |  |  |  |  |  |
| S1 + S3（仅经准入辅助） |  |  |  |  |  |  |  |
| S1 + S2 + S3（可真实共现/分层） |  |  |  |  |  |  |  |
| Representative Laya checkpoint |  |  |  |  |  |  |  |
| Representative Kev checkpoint |  |  |  |  |  |  |  |

> 行只代表拟比较的合法配置，不证明它们当前可训练、已完成或具有匹配反事实标签。结果字段保持空白；各样本准入与角色/缓存字段是否进入编码均需按真实资产说明。


### Table 9 · RQ5 工作负载收益边界

| Predefined Workload Stratum | Independent Tasks | Best Comparable Reference | Reference Success | Full Success | Reference Episode USD | Full Episode USD | Net Difference / CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Task type: Coding |   |   |   |   |   |   |   |
| Task type: Research (if runnable) |   |   |   |   |   |   |   |
| Task type: Data (if runnable) |   |   |   |   |   |   |   |
| Predefined task size: Small |   |   |   |   |   |   |   |
| Predefined task size: Large |   |   |   |   |   |   |   |
| Source-defined subtask boundary (if present) |   |   |   |   |   |   |   |

### Table 10 · 在线 Episode 费用与连续性（支持 RQ1/RQ4）

| Policy | Generation Input/Output USD | Generation Cache USD | Retry/Failed Subset | Online Teacher USD | Router Cost | Trace / Task | Switches / Task | Total Episode USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed policy |   |   |   |   |   |   |   |   |
| Random Mix |   |   |   |   |   |   |   |   |
| Greedy / Sticky |   |   |   |   |   |   |   |   |
| Full ModelRouter |   |   |   |   |   |   |   |   |

Online Teacher 按配置教师目标身份价格计入实际输入/输出/缓存费用；6 条成功或已报告 usage 的教师按 `prompt + completion`，另 5 条教师 usage 缺失。compact 第 3 条教师可能 JSON 解析失败，但已报告 usage 时仍计费一次，不记为成功教师。生成费用只含生成调用，Retry/Failed 为已计调用子集，不重复相加。Total 只汇总单位明确、usage 完整的映射实验美元费用；缺失项的完整总额保持 `None`，不把已知小计当完整费用。旧事件留原版本，新请求按新 Provider 记录；离线制作与本地资源估计分列，不进入实付 Episode USD。

### Table 11 · 微调监督与 Checkpoint（Appendix）

| Checkpoint / Learner | Supervision Source | Independent Train Units | Validation Split | Val Loss | Accuracy | Brier/ECE | Eligible for Online Evaluation? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Laya / Stage1 |   |   |   |   |   |   |   |
| Laya / Full Graded |   |   |   |   |   |   |   |
| Kev / Original |   |   |   |   |   |   |   |
| Kev / Finetuned |   |   |   |   |   |   |   |

### Table 12 · 真实 Episode 与系统开销（Appendix）

| Task / Policy | Single-Agent Phase Sequence | Selected Logical / Actual M×E | Trace | Continuous Context / Resent Tokens | Measured Physical Cache | Resolved? | Episode USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Representative Case A |   |   |   |   |   |   |   |
| Representative Case B |   |   |   |   |   |   |   |
| Failure Case |   |   |   |   |   |   |   |
| Full Router |   |   |   |   |   |   |   |
| Fixed reference |   |   |   |   |   |   |   |

上下文消息连续与实际 KV/缓存各列记录；重发、估计复用、模拟和 Provider/引擎实测分开。Alias 同后端不能证明跨模型缓存效果，API 路由前向不填 Resolved 或 Episode 成绩。来源：下载讨论行 27359–27361、28747–28784。


## 6. 结果关联字段（按真实观测，不制造反事实）

| 层级 | 必需字段与因果边界 |
|---|---|
| Model Registry | `provider/model_id/revision/native_effort_set/capabilities/price/cache_policy`；原生档位以 Provider 实际支持为准 |
| Pool | `pool_id/K=3/model_ids/legal_model_effort_actions/provider_evidence`；实际动作集合按 Provider 证据记录 |
| Task / Single-Agent | `task_id/task_type/repo/source_defined_subtask_id/subtask_goal/stage`，并标 `observed_at` |
| G/F | `source_boundary_id/G/decision_boundary_F/context_copy`；阶段状态与真实子任务边界分开记录 |
| Decision | `pre_decision_state/model/effort/legal_candidates/policy/router_time`；不得读取未来验证或未来 Trace |
| Evidence | `supervision_regime/task_group/observed_action/true_matched_branch`；历史单轨迹不是最优反事实标签 |
| Usage | `actual_input/output/reasoning/cache_read/cache_write/retries/router_overhead/price_snapshot`；估计和实测分离 |
| Episode | `task_id/task_type/G/pool/policy/seed/terminal_resolved/total_USD/wall_time/evaluator_version` |
| RQ4 | `ablation_group/action_policy/feature_mask/supervision_sources/train_units/checkpoint/actual_encoded_fields/terminal_resolved/episode_USD`；训练信息及动作/状态消融与全程 Episode 同口径，缺少真实反事实不补造 |
| RQ5 | `predefined_workload_stratum/independent_task_count/baseline/full/cost_delta/uncertainty`；事后 Trace 仅用于解释 |

不基于缺失的真实分支制造角色×模型“最优 oracle”；不因一次负结果就从训练/论文历史删除测试过的因素。


## 7. 论文章节与图表定位（V9）

| 章节 | Figure | Table |
|---|---|---|
| Motivation / Method / Setup | Fig.1–2 | T1–2 |
| **RQ1 Overall Performance** | **Fig.3** | **T3（主表）** |
| **RQ1 Results & Accounting** | **Fig.3–4** | **T3、T10** |
| RQ2 Fixed-K=3 Model×Effort | Fig.5 | T6 |
| RQ3 Single-Agent Granularity | Fig.6 | T7 |
| **RQ4 Systematic Ablation** | **Fig.7** | **T4–5、T8、T11** |
| **RQ5 Workload Boundary** | **Fig.8** | **T9** |
| Appendix: Laya/Kev, Case Traces | Supplementary | T11–12 |


## 8. 适用边界与结果填写

- 固定 K=3 目标身份；实际候选动作按 Provider 能力记录。独立任务用于效果评估，不依据最终测试结果改换池。
- 本次文档修改不新增 API、GPU、训练或 Harbor Episode；11-07 执行事实以原完整报告为准。
- 泛化分析可覆盖未见仓库/任务、供应商故障及缓存 TTL；不进行扩 K 或替换池成员比较。
- 即使公开前沿可以迁移、前沿外模型无增量或动态路由收益不成立，也记录结果并收紧贡献，不把预期写成事实。
- 后续填表直接使用同口径实测，不要求新增 PR、CI、审批或反复复核流程。

## 9. 来源与相关工作

- [Artificial Analysis 方法学](https://artificialanalysis.ai/methodology)：Price、Cost per Task、Provider 和模型定义
- [Artificial Analysis 模型榜单](https://artificialanalysis.ai/leaderboards/models)：同日期配置与公开指标
- [FrugalGPT](https://arxiv.org/abs/2305.05176)、[RouteLLM](https://arxiv.org/abs/2406.18665)：成本优化与路由参考
- [既有相关工作及原图](../汇报二/论文笔记.md)：相关方法边界
- [研究总纲](../../our-project/planning/RESEARCH_OVERVIEW.md)、[正式实验决策](../../our-project/planning/EXPERIMENT_QA.md)：现有研究依据

来源快照读取日期为 2026-10-13，未在本文录入当前榜单数值或宣称哪个具体型号已经最适合本项目。

- [Artificial Analysis 当前模型指数方法与 Cost per Task 定义](https://artificialanalysis.ai/zh/methodology/intelligence-benchmarking)：公开指标并非相同 Coding Harness 的完整任务费用。
- [Claude Haiku 5.5 / GPT-6.1 Sol 档位与费用](https://artificialanalysis.ai/models/comparisons/claude-haiku-5-5-high-vs-gpt-6-1-sol-low)、[Claude Opus 5.5 不同推理档位](https://artificialanalysis.ai/models/comparisons/claude-opus-5-5-vs-claude-opus-5)：仅作候选池调研入口，正式采样时以同日可用性及价格为准。



## 2026-10-16 V8 决策落款

**2026-10-18 最新明确决定（V9）**：负责人要求**消融直接成为新的 RQ4，原 V8 的 RQ4 角色互补性删除**；**RQ5 动态路由适用边界保持不变**。现行顺序为 RQ1 总体、RQ2 模型池、RQ3 任务粒度、RQ4 系统消融、RQ5 适用边界。V8/V7 的旧角色互补性编号仅在 Git 历史与 Q-ID 审批历史中可查，不属于当前论文方案。

**更新范围**：仅论文实验研究设计及空白图表口径，没有新增 API/GPU 训练、下载、跑 Benchmark 或产生任何结果。八张图和十二张表的实际数据留空；独立外部最终评测集继续遵守现有隔离规则。
