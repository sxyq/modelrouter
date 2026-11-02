# V9 六个 Train 前缀真实比较与 CPU 实测状态

## 2026-11-02 18:05 · 可选原始响应记录已准备，新增三请求未获单独授权

接续main `dfa1992c2e054d8713454cbacacabde4dc6b3eed`，本轮只完成已授权的本地工作；代码提交 `06bb7fe35efb3e46777a3c6963a273e50aa4f2ea`。没有本轮三次新增付费请求的单独明确授权，因此停止在请求前，模型/工具/Verifier/新Episode/服务器/GPU/训练均0。原始四请求、六组比较、Dev、Router诊断和Twin未重跑。

原query_raw新增可选raw_response_path，默认关闭，仅指定的这一次请求记录。两个原流读取器在解码/组装前写入实际读取的响应字节并及时flush，保留event/data顺序、[DONE]、终局与错误数据；非流式记录实际读取的JSON实体。只保存响应，不保存请求认证头；供应商原样回显当前请求Key时遮蔽该值。HTTP错误实体也能保存，原HTTPError仍抛出且原调用者仍可读取同一实体；没有追加请求或重试。

建议实际诊断仅使用`.runtime/diagnostics/20261102-v9-provider-validity/`，该路径已被原Git忽略规则覆盖，不增加新忽略体系。文件以0600创建，不覆盖旧证据；目录/持久原始文件当前均未创建。公开Git只写必要的脱敏配置、统计与结论，不能提交完整请求、原始SSE或私人配置。新增安全HTTP状态/Content-Type及诊断开关信息进入原metrics，不改变Usage、身份、Effort或费用口径；本地文件创建失败不记作已发出的Provider请求。

仅以三份原组装JSON做离线读回和临时字节记录：C4 Luna仍COMPLETE，A1 Luna仍EMPTY_RESPONSE，A2 Sol仍INCOMPLETE_TOOL_CALL；三份最终响应与捕获字节均保持，Usage/模型名不变，原费用为0.0027985/UNKNOWN/0.074136USD。这些是旧费用，不是本轮新增消费。临时文件随句柄关闭删除，未创建测试文件、SSE模拟或新客户端；语法有效。没有原始SSE，故真实流写入、HTTP错误捕获及Key回显遮蔽尚未经过供应商实测。

Harbor和Native Relay原ProviderResponseError传递路径已读：原响应/metrics先保留，费用及模型身份继续进入原记录，异常保持失败状态，不进入工具或伪造成功SSE；这两处本轮无需再次修改。教师三字段、Trainer、Verifier、研究定义与原19条/74行不动。

| 对象 | 完整响应 | 可解析工具动作 | 结束状态 | Usage | 费用 |
|---|---|---|---|---|---|
| Luna stream=true，A1/4，4096/low | 未执行 | 未执行 | 未请求 | 未产生 | 未发生请求 |
| Luna stream=false，A1/4，4096/low | 未执行 | 未执行 | 未请求 | 未产生 | 未发生请求 |
| Sol Responses stream=true，A2/5，8192/low | 未执行 | 未执行 | 未请求 | 未产生 | 未发生请求 |

结构化记录为原summary.provider_generation_validation，三项结果均NOT_EXECUTED，不能借用旧返回写成实测。Luna空流和Sol预算问题是否改善仍未知，不能排除供应商原因或声称Agent恢复。下一项仍是负责人单独明确授权这三次请求后，仅生成/解析并保存私人原始证据；无需Docker、服务器、GPU、教师、工具执行或Verifier。得到完整生成实证后，再另定小范围工具质量对照。

新增Model-only/Effort/K=3标签均0；STEP精确权重仍缺失，CPU0/12、Serving/F14/handoff不处理，路线B仍待决。Research五RQ八图十二表不变，没有新备份、构建、权重或其他持久临时产物。

## 2026-11-02 17:20 · 本地生成异常处理已实施，供应商有效生成仍待实证

接续main `27c84277bb550b450d73040d8a3ce432197c7e98`，只分析源码与原保存数据，代码提交 `c0989d1f3edd64563d91a0629b1209a8f8cb342f`。模型请求、工具执行、Docker/服务器、训练、GPU和新Episode均0；旧A1/A2、六组比较、Dev、Twin与原始响应不重跑或改写。结构化记录在原summary.generation_validity_analysis。

### Luna：已确定的是本地处理问题，上游空流原因未知

两份请求归档均为gpt-6-luna、Chat Completions、stream=true、max_tokens=4096、reasoning_effort=low、include_usage=true及原bash(command)工具。原解析器按choice/tool索引累计delta.content、reasoning_content、工具name/arguments并保留finish_reason与Usage；流结束时却直接返回，没有记录[DONE]，也没有把空choice或缺结束原因作为生成异常。

两份组装结果都只有匹配模型名、空assistant、finish_reason=null，Usage/TTFT均缺失。旧query_raw返回普通响应，原mini的parse_toolcall_actions因没有工具调用报FormatError，随后原Agent可以进入格式反馈流程。这只能证明本地错误分类过晚，不能说明供应商究竟发送了什么SSE帧、为何空输出，或推断Luna任务能力。

对照为同一实际端点的[C4 Luna完整返回](quality-prefix-execution/C4/luna/provider_responses/20261102-C4-prefix-3-3.json)：正文也为空，但工具参数完整、finish_reason=tool_calls、Usage已报。空正文本身不是错误，完整工具动作仍按原行为接受。当前mini的_prepare_messages_for_api会去掉历史extra；请求归档字符与原生整理后的字段应分开，缺失的Luna Token不由归档长度估算。

### Sol：截断发生在上游生成，不是本地丢掉完整命令

[A2 Sol原生返回](quality-prefix-execution/A2/sol/provider_responses/20261102-A2-late-prefix-5-5.json)明确status=incomplete、原因max_output_tokens，工具项status=incomplete、JSON参数停在字符串中间。4096输出包含3624 reasoning，留给其他输出的报告差值为472；原Responses解析器拿到的终局对象已不完整。旧Agent桥接把状态转成length，mini因此报FormatError，未执行该命令。

请求是单一原bash Schema，4096输出上限与reasoning.effort=low；供应商返回strict工具Schema及reasoning.effort=max。模型名匹配，实际应用档位仍UNKNOWN，无法凭此确定参数替换或内部预算分配。本轮不改上限、Effort、Schema或Prompt；reasoning仍只计一次。

### 实际源码与离线结果

原Provider加入ProviderResponseError，携带原响应和metrics；query_raw在原Usage/费用记录完成后区分EMPTY_RESPONSE、INCOMPLETE_RESPONSE、INCOMPLETE_TOOL_CALL、INVALID_TOOL_ARGUMENTS，异常不进入动作消费。两个流解析器只追加实际观察到的结束标志记录；缺[DONE]本身不替代finish_reason/Responses状态，也不虚构旧结束事件。status继续表示原费用记录状态，response_status表示生成有效性，两者分开。

原PolicyModel先按已有路径保存异常响应、身份、费用与GENERATOR_END，再在桥接或工具解析前抛出异常。异常继承RuntimeError，命中原abort_exceptions；原Benchmark CLI的单次重试配置保持，未增加请求。原native_generator_relay也保留这些记录并返回明确错误，不向客户端拼造成功SSE。教师只补异常时已知Usage/原响应的传递，三字段职责与触发规则不变。

使用本机现有mini-swe-agent2.4.6/LiteLLM1.106.0对保存数据离线解析，没有伪造SSE、调用Provider、执行工具或新建测试文件：

| 保存对象 | 新Provider分类 | 原mini解析 | Usage/费用 |
|---|---|---|---|
| A1 Luna | EMPTY_RESPONSE | FormatError，0动作 | UNKNOWN |
| A2 Luna | EMPTY_RESPONSE | FormatError，0动作 | UNKNOWN |
| A2 Sol | INCOMPLETE_TOOL_CALL | FormatError，0动作 | 原13271/4096/3624与0.074136USD保留 |
| A1 Sol | COMPLETE | 1动作 | 原0.037901USD保留 |
| C4 Luna | COMPLETE | 1动作 | 原0.0027985USD保留 |

异常对象保留原响应/metrics，原Agent中止类型匹配；三修改文件语法有效。原始SSE没有保存，故本轮没有直接验证流读取新增结束字段、真实HTTP异常回传或供应商已恢复生成。

### 下一项仅推荐3请求，不自动执行

先验证生成有效性，不恢复质量比较：A1相同截止状态给Luna各1次stream=true/false，其他请求字段与4096输出保持；流式请求须定向保存原SSE含结束事件。A2给Sol1次Responses stream=true、仅把输出上限提议为8192、low保持，记录终局/完整工具参数/Usage/应用Effort是否仍未知。保存SSE沿原Provider，不创建第二客户端；这3次需下一轮明确新增收费范围，本轮没有实施参数变化或请求。

只判断是否完整可解析，不执行工具，因而不需Docker、服务器、GPU或新Agent Episode；也不能据此产生训练标签。8192可能给工具输出更多空间，但不能保证生成完成。若接口有效，再另行恢复同状态工具分支与原验证比较。

原19 Model-only目标、74行材料、原一步标签条件和路线B待决状态保持；STEP_001实体仍缺失、CPU0/12，F14/Serving/handoff及权重保留部署不处理。没有新增备份、构建、镜像或持久驱动，临时计时/重放文件未创建；Research方法与五RQ八图十二表不变。

## 2026-11-02 15:21 · A1/A2有限运行结束，原验证齐全，新增标签0

从实际main `909f3fcde6922d856957fc59fe9459ae445b6a78`接续。负责人明确追加原基础镜像拉取与继续A的授权；两份指定SWE-smith镜像已拉取，未重复询问，也没有扩大4次请求/4候选分支/6次原范围验证。原14:49缺镜像记录保留为之前的尝试，不再代表当前状态。

本轮实际4次正式Sol/Luna请求、6次原范围验证，均未使用Alias或启动完整Episode。4/4请求与返回模型字符串匹配，但只有1次完整可执行Agent动作，另外3次FormatError；**两组均不具备有效偏好资格，新增选择标签0。** 完整数据见 [late_prefix_completion_summary.json](quality-prefix-execution/late_prefix_completion_summary.json)。

| 前缀 | 新取得的原前值 | Sol一步后的原验证与状态 | Luna一步后的原验证与状态 | Sol模型费率USD | Luna模型费率USD |
|---|---|---|---|---:|---|
| A1 Records cutoff4，verify | 23/24，1 failed | 23/24；完整一步但只读取/复现，没有源码修改 | 23/24；空正文、无工具调用/finish_reason/Usage，FormatError；不当可信修复失败 | 0.037901 | UNKNOWN |
| A2 async-timeout cutoff5，verify | 29/32，3 failed | 29/32；4096输出含3624 reasoning，function_call未完整生成，FormatError | 29/32；空正文、无工具调用/finish_reason/Usage，FormatError | 0.074136 | UNKNOWN |

每题先取一次真实原范围前值，再为两候选分别用同一基础镜像、原task_source故障patch和截至cutoff的原命令恢复环境。两方当前源码/故障提交、完整消息、状态、工具协议和原测试范围一致；原Darwin历史文件不改，两方共同追加实际Linux容器说明。不是复用旧23/24或29/32作为新验证结果，也不声称重建的环境与已删除临时镜像字节相同。

原24/32项的六份输出全部可信、原测试文件与verify_command保持。Records原全suite额外7个errors、timeout额外2个skip属于恢复历史中的范围，不并入原24/32项；历史工具中已有的pytest命令只用于恢复，另有27条截止前命令重放记录，不能作为候选新增监督。实际候选工具调用只有Records Sol的1条，耗时2.321829秒，继续读query/事务文档、复现脚本及原失败摘要。

### 失败发生在哪里

- Records Sol收到完整工具调用并真实执行，但没有修复原失败，是可信单候选一步失败观察。
- 两次Luna的Provider组装响应均有匹配模型名，assistant为空、无工具调用、无finish_reason和Usage；延迟141.219743/166.214070秒。原Agent拒绝这样的输出是正常行为，不能据此宣称Luna修复能力低。供应商具体结束原因未知，单条原始SSE事件没有保存，不能猜测为某一种超时或模型替换。
- async-timeout Sol响应为incomplete/max_output_tokens，4096输出中3624为reasoning，带未完成的function_call；未人工补齐参数、执行截断命令、追加请求或提高上限。它不是完成一步修复后的可信失败终局。

原 [prepare_comparison](../../../code/src/modelrouter/v9/training/real_supervision.py)与prepare_record均未修改，两组因trusted_outcomes不齐而返回COMPARISON_NOT_VALID，保存为OBSERVED_OUTCOME_ONLY。不能写成两组“可信双失败”，也不能将它们作为两个模型的质量胜负或低费用偏好。

### 费用、档位及原始证据

已知Sol模型费率合计 **0.112037USD**；两次Luna缺Usage，完整模型费用UNKNOWN，不是0。已知输入24604、输出5053、其中reasoning4374、缓存读取0/写入24598，仅覆盖Sol两请求；reasoning已包含在completion，不重复计价。四请求生成延迟合计480.730640秒，教师0；供应商实收、工具/容器/镜像资源USD未计量。

Sol两次发送reasoning.effort=low但仍报告max，Luna发送reasoning_effort=low且不报告应用档位。实际应用Effort继续UNKNOWN，仅MODEL_ONLY范围，Effort/K=3标签0，AA沿原v4。返回型号是API身份记录，不是物理权重实读。

[A1 comparison](quality-prefix-execution/A1/comparison.json)、[A2 comparison](quality-prefix-execution/A2/comparison.json)分别指向两题原始请求body、原Provider组装响应、metrics、Agent消息、实际工具反馈、环境重放、前后验证和固定测试ID状态。原比较集合追加两行，旧六对不覆盖；没有创建空训练增量或新调用器/Agent Loop。保留59份新执行文件共2312129字节，约2.3MB；请求不含授权密钥。

### 监督判断与下一项

新增任务级/步骤质量/步骤费用目标均0；原19条仍任务9/步骤10，质量Sol4/Luna4、费用Luna2、有效阶段verify9/recover1，inspect/modify0；74行及215/186可组合视图保持。当前两题来自两个已有Train任务/两个仓库，新增来源任务0。六次固定验证前后修复集合/新增回归均为空，不把读取或空输出转成标签。

原一步目标仍可用于具备真实可执行动作和原验证终局的比较，已有19条含义不变；本轮首先暴露生成有效性问题，没有提供否定原目标的新可信对照。**停止当前同通道同配置的收费采集，先利用已保存请求/响应定位Luna空流及Sol输出截断，再决定有限真实比较范围。** 不重试本轮四次、不启动训练或Dev/Final。

路线B仍仅待负责人选择：固定原FAIL_TO_PASS/PASS_TO_PASS测试ID，若一个候选实际修复集合严格包含另一个、没有新增原PASS_TO_PASS回归且单项状态完整，才考虑独立的“部分质量进展偏好”；集合交叉、skip/error/未知、仅读取均无赢家。它与现有一步全范围通过目标分开；本轮没有批准新目标、修改Trainer或给旧双失败补标签。当前修复集合为空，采用这条规则也不能制造新答案。

### 清理与其他状态

6个本轮容器全部移除，Docker剩余容器0；另删两Records分支自动生成的28份字节码和records.egg-info副本，原untracked_files.json清单保留，这些内容可由原环境重新生成。没有构建初始/分支镜像、备份、长期驱动或下载研究权重。保留两份指定原基础镜像供原实验复用，Docker报告总镜像6.503GB；build cache/volume为0。没有删除原始请求、验证结果、用户文件或其他研究资产。

源码无永久修改，只有原数据/报告与必要规划更新。服务器/F14/Serving/handoff/训练/GPU/CPU模型前向均未访问或执行，权重保留代码仍未部署；STEP精确权重仍缺失，F11/R11研究代表及历史负结果保留。最后服务器状态仍为11:28:14台北历史取样，不写成当前在线。RESEARCH_OVERVIEW、五RQ、八图十二表、用户Trainer/tests/私人账本/原删除/Fig.2不改。

## 历史：14:49缺镜像尝试（已由后续授权拉取解决）

## 2026-11-02 14:49 · A1/A2已授权，原基础镜像缺失，生成前停止

接续main `8fb6e16a442fa73451a5a3e6c989ebb167627ba7`，负责人末尾明确要求“让你做就是授权直接做”，本轮A的Docker/真实Sol、Luna最多4次一步生成、4分支及6次原验证已授权；没有再次询问。实际环境证据见 [late_prefix_environment.json](quality-prefix-execution/late_prefix_environment.json)。

Docker Desktop当前context为desktop-linux、Server29.9.2且可响应。两个现有本机context（desktop-linux/default）的镜像列表均为空；原Records与async-timeout基础镜像inspect均报No such image，原临时initial tag也不存在。未确定镜像何时、因何丢失，不归因到本轮或某个维护者。

| 对象 | 许可Train历史与截止 | 原范围 | 本轮Sol/Luna | 本轮前值/分支验证 | 新标签 |
|---|---|---:|---|---|---:|
| A1 Records | `t18-records-sol-low / 4`，messages[0:10]，events第18行，verify | 24项 | 均未请求；原基础镜像缺失 | 未执行 | 0 |
| A2 async-timeout | `t15-async-timeout-sol-low / 5`，messages[0:12]，events第22行，verify | 32项 | 均未请求；原基础镜像缺失 | 未执行 | 0 |

精确任务ID、原环境和命令来源仍使用 [next_execution.md](next_execution.md) 与 [step_quality_research.md](step_quality_research.md)。本轮确认两个task_source故障patch、完整截止消息与原run_config.verify_command都在；没有重新选任务、改写问题或复制原后续答案。

缺失对象为 `jyangballin/swesmith.x86_64.kennethreitz_1776_records.5941ab27`、`jyangballin/swesmith.x86_64.aio-libs_1776_async-timeout.d0baa9f1`。按“缺原资产停止，不自行下载/安装/重建”的范围，未创建容器或发付费请求。不是API失败、模型双失败或未获许可，不能把此前23/24、29/32写成本轮结果，也没有新的固定测试ID前后观察。

本轮请求/工具/验证/可信候选对均0，新增Model-only/Effort/K=3目标0；原19条（任务9/步骤10）和74行待训练材料保持。未发生模型调用费用；逐候选Usage、返回身份、应用Effort、实收与结果不存在，保持null，不填虚构Token或成绩。没有触发两组双失败后的路线B研究结论；原一步目标的早期适用限制仍沿上一轮证据，不能从本次环境缺项得出新模型质量判断。

下一项实质工作是恢复这两个精确原基础镜像的可用性，然后在原A范围完成未执行的4次生成及6次验证。当前范围不包含下载/环境重建，故本轮不执行恢复；也不重问已经给出的A许可。未访问服务器/F14/Serving/handoff/权重或GPU，没有训练/新Episode、临时脚本、镜像、备份或构建产物；本轮无需删除任何研究资产，原结果和用户修改保持。

## 历史：此前六组已完成结果（不重跑）

从 main `be716e8341a043c9ce29c066290cf0a270bea3b1` 接续。用户已分别授权 A 的本机 Docker/真实 Sol、Luna 一步比较和 B 的原服务器 CPU 前向。本轮 A 完成 12 次生成、13 条模型工具命令和 12 次原范围验证；六组均未通过，新增路由答案 0。B 因指定 e01 权重已被此前清理删除，实际前向 0/12。没有新 Episode、训练、GPU 计算、Serving 部署或旧实验重跑。

## 1. 项目与执行范围

正式三模型身份、五 RQ、八图十二表、mini-SWE-agent/Harbor、两条教师参考和 AA v4 均沿用。本轮真实执行为 K=2：Sol 原生 Responses、Luna Chat Completions；12/12 请求与返回型号匹配，未使用 Alias。教师关闭，费用 0。

Sol 六次均实际发送 `reasoning.effort=low`，响应仍报告 `max`；Luna 六次发送 `reasoning_effort=low`，没有报告应用档位。两者实际 Native Effort 均保持 UNKNOWN。现有账户目录没有正式 Flash，未重发旧失败探测，不增加完整 K=3 或 Effort 目标。

## 2. 六前缀逐项结果

来源、任务 ID、完整截止消息和原命令引用见 [next_execution.md](next_execution.md)。六题均为允许训练的 `TRA-002 / SWE-bench/SWE-smith / train`，来自六个已有任务、五个仓库；新增来源任务 0。OAuth 两题同仓库关系保留，独立 Dev/Final 和 TwinRouterBench 不进入这些状态或答案。

| 前缀 | 决策前阶段 | Sol 原验证通过数 | Luna 原验证通过数 | Sol 模型费率 USD | Luna 模型费率 USD | 监督资格 |
|---|---|---:|---:|---:|---:|---|
| C3 SQLparse | modify | 328/331 | 328/331 | 0.04011850 | 0.00433390 | 仅观察 |
| C4 Records | modify | 23/24 | 23/24 | 0.02169600 | 0.00279850 | 仅观察 |
| C5 Autograd | modify | 583/585 | 583/585 | 0.01724100 | 0.00325938 | 仅观察 |
| C6 async-timeout | recover | 29/32 | 29/32 | 0.01658350 | 0.00250390 | 仅观察 |
| C1 OAuth2 scope | inspect | 655/673 | 655/673 | 0.00897100 | 0.00217060 | 仅观察 |
| C2 Device authorization | inspect | 660/673 | 660/673 | 0.01201600 | 0.00235480 | 仅观察 |

每候选单独使用已有原基础镜像、保存的故障引入 patch 和截至该步的历史命令恢复 `/testbed`；重放退出状态与历史相符。没有下载、构建镜像或恢复旧临时快照，也不声称与已删除快照字节相同。两方看到同一截止历史，使用原 bash 协议和 30 秒工具窗口。模型一步后恢复原测试文件，再逐字执行原 `run_config.verify_command`，没有人工修改验证范围或补写任务解答。

实际失败原因：

- C3 两方继续读取或复现；原输出 formatter 的 `AttributeError` 仍在。
- C4 两方复现连接/query 问题，原 1 项失败仍在，没有完成该步修复。
- C5 Sol读取和复现；Luna提出局部修改，但原镜像没有 `apply_patch`，命令未应用。原两个 VJP 测试仍为 `UnboundLocalError`。
- C6 两方继续读取 timeout 状态与测试；读取成功不等于修复，原三项异常消息测试仍失败。
- C1 两方都请求镜像没有的 `rg`，命令退出 127；18 项原失败仍在。
- C2 Sol继续读取，Luna一次生成给出两个读取命令，两条均因 `rg` 缺失退出 127；13 项原失败仍在。

阶段标记描述决策前状态，并不要求生成动作马上修改代码。没有把口头定位、拟议 patch 或测试通过项数量当成赢家。所有比较保持 `OBSERVED_OUTCOME_ONLY`，不能进入 S1 选择目标；本轮没有创建空的监督/训练增量文件。

初次临时驱动缺少原 `LitellmModelConfig.model_name`，12 个分支都在模型构造时退出，付费请求 0；补齐原调用参数 `model_name="openai/" + selected_model` 后完成上述 12 次真实生成。每分支的 `setup_failure.json` 保留真实构造错误，重复的成功重放日志已移除。没有自动重试模型请求或新增永久调用器。

### 费用、用量与证据

Sol 合计 **0.11662600 USD**，Luna **0.01742108 USD**，模型费率估算共 **0.13404708 USD**。12/12 Usage 已由原 Provider 记入原本地用量记录；供应商实收和工具/容器资源 USD 未计量，不能把费率估算称作现金账单。

输入 220,325、输出 4,911 Token；输出已含 1,706 reasoning，不能再相加。缓存读取 23,998、缓存写入 36,968，分别按原 Provider 成本规则处理。生成延迟合计 145.867689 秒，新模型工具命令合计 20.402755 秒；没有单独测量容器初始化和原验证耗时，完整运行时延不作估算。

结构化逐任务统计见 [quality-prefix-execution/summary.json](quality-prefix-execution/summary.json)；原始比较见 [comparisons.jsonl](quality-prefix-execution/comparisons.jsonl)。每个 C*/sol、luna 目录保存原 Provider 响应、Usage、请求参数、消息、工具命令及反馈、环境重放和原验证输出，后续无需重跑本批获取这些事实。

## 3. 监督数量与 CPU 结果

新增质量偏好 0、等质量费用偏好 0，inspect/modify/recover 各阶段新增目标均 0。累计仍为 Model-only 19：任务级 9、步骤级 10；步骤质量 Sol4/Luna4，步骤费用 Luna2。有效步骤仍为 verify9/recover1，inspect/modify 为 0。74 行定向材料、可组合 Train215/Val186 和原 382 行历史用途不变，没有新微调依据。

CPU [原始状态及12个未执行组合](cpu_forward_measurements.json)记录：

- 原服务器清理记录于 **2026-11-02 11:05:32 台北**删除 `V9_LAYA_STEP_001/checkpoints/epoch_01`，标记 `PRUNED_LOW_SCORE`，理由 `outside_new_core_pool_15pct_quota(1/2)`，释放 846,196,996 字节。
- 同时更新的 run 报告保留曾保存事实，但现为 `weights_saved=false/loadable=false`；前一天 manifest 的 `PINNED_PARENT/loadable=true` 已不代表现场实体。
- 原目录没有对应权重或配置，清理记录没有归档去向，限定的现有目录内没有可恢复实体。发起者未记录，不能归因到具体维护者或 handoff；这次删除早于本轮 B，不是本轮清理动作。
- 已读取实际导入的 Adapter、RLAgent、序列/collate 和 DecisionModel 源码，但没有改用 F11 或基座。原 ModernBERT 运行类、各段耗时、概率、Top-1、Token 位置差与 inference_mode 收益均未测得。

11:28:14 台北只读取样：F14 独立维护仍运行，Epoch2 第7/420块、54,598/107,404步，最新 Loss0.4703；不把部分有限块当成整轮恢复，也不作父权重。Serving PID327621 健康，仍为 F05-e01 与原 Kev Adapter。F11/R11研究代表保留，STEP_001只保留历史训练与预测事实，当前实体不可加载；本轮 Laya/Kev 参数更新均 0。

## 4. 下一轮判断

本轮不足以启动新的有限 K=2 head 接续。原“一步后立即通过整项原验证”目标无法仅凭本批读取/复现动作给予 inspect 质量标签；是否引入不同的步骤质量定义或原协议下的固定后续验证范围，需要负责人决定，本轮未改变协议。下一批不能照搬这六个已失败前缀增加调用，也不能根据主观分析补标签。

B 首先需要找回精确 STEP_001-e01 实体，并解决原额度清理与指定研究候选的关系，才可继续原三状态共12次 CPU 前向。没有可恢复实体时，本轮权限不能自动变成重训授权；也不能用父权重的测量代替该任务。新的收费前缀比较需要另定具体前缀、数量和范围，当前 A 的12次已经完成。

## 5. 改变了什么与清理

本轮没有使 Router 更会选择，没有新训练或动态 Agent 收益证据。推进的是六个真实同状态比较、一步目标局限和精确 CPU 权重缺失原因；原恒选 Sol 的原因仍不能从本批归为模型能力差异，encoder/head 耗时比例和稳定提速继续未知。

本轮24个容器全部删除，Docker取样剩余容器0；临时驱动与12份重复成功重放日志已移除，没有新增镜像、备份、依赖或服务器临时构建。真实失败、原任务基础镜像、训练历史和其他权重保留。永久源码、Trainer/tests、私人账本、用户删除、F14/handoff和Fig.2并行内容未改；只同步本轮公开结果与必要 Status/QA/Memory/训练报告，GitHub更新不等于服务器部署。
