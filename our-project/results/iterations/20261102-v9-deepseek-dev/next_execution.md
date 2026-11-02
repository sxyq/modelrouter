# V9 Model-only 接口与质量前缀准备

## 2026-11-02 15:21 · 当前：A1/A2已执行，不再按下文作为未执行候选

负责人已明确授权并拉取两份原基础镜像；从main909f3fc完成4次请求、4候选分支和6次原范围验证，原14:49缺镜像限制已被新授权解决。[本轮结果](quality_prefix_execution.md)和[结构化数据](quality-prefix-execution/late_prefix_completion_summary.json)为当前入口。Records前后均23/24，timeout前后均29/32；1完整工具动作、3FormatError、Usage2/4，新有效标签0，两组不能当可信质量双失败。

下一项优先是**生成有效性离线定位**，而非继续采集相同类型前缀。可直接使用以下提示词：

> 继续最新main，仅使用A1/A2保存的四份request.json、provider_responses、metrics、Agent消息与原Provider/mini-SWE-agent源码，定位Luna空正文/缺Usage与Sol输出截断发生在哪个现有边界。Records Sol有效但只读取；两次Luna没有工具/finish_reason/Usage；timeout Sol4096输出含3624 reasoning并留下未完成function_call。区分已有源码能确定的行为和供应商尚未知原因，不从组装JSON猜测未保存SSE事件。不要重复原4次请求、提高Token、调用新API、训练、跑Agent、访问服务器或部署权重保留代码。只有真实源码与已保存数据足以证明问题时才原位修改必要函数，不加第二个调用器、自动重试或新监测系统。给出下一次能取得完整动作的最小真实比较配置与具体请求数量，新的收费范围在下一任务单独明确；已有本轮A授权不重复询问。

原一步目标保留；若负责人决定路线B，可选固定F2P修复集合严格包含、无P2P新增回归且单项状态完整的独立部分质量目标，不按通过数量排序。本轮修复集合均为空，B未获批准，旧19条/74行/215与186不变。当前不启动训练、CPU对照或新Dev/Final；基础镜像保留且可用，不再提出重复拉取。以下各节为旧准备或缺镜像历史，不作为新执行许可或任务队列。

## 历史：14:49原基础镜像缺失

## 2026-11-02 14:49 · A已授权，现因原基础镜像缺失停止

负责人已明确授权本轮A（Docker、最多4次真实Sol/Luna生成、4分支、6次原验证），不再询问此范围许可。[本次真实环境结果](quality_prefix_execution.md)及 [环境证据](quality-prefix-execution/late_prefix_environment.json)确认Docker可响应，但desktop-linux/default两个现有本机context镜像列表均为空，两份原基础镜像inspect报No such image。

A1/A2截止、task_source故障patch与原验证命令都在，候选没有替换；生成、工具、验证、费用、新标签均0。没有新的双失败，也没有路线B单项前后数据。按当前“缺资产即停、不下载/安装/重建”范围，本轮不恢复镜像或调用模型。

直接缺项为 `jyangballin/swesmith.x86_64.kennethreitz_1776_records.5941ab27` 与 `jyangballin/swesmith.x86_64.aio-libs_1776_async-timeout.d0baa9f1`。下一项需要这两个精确原镜像恢复可用；当前下载/环境重建未在范围内，不把已给出的A许可误记为未授权。镜像恢复后再沿下表两前缀与原4/6范围完成实际比较，不重跑旧六对、不扩大任务、训练或服务器操作。

以下“待批准”的字样属于上一轮准备历史；本轮A已明确授权，但实际实验尚未发生。原19条与74行保持，STEP精确权重仍缺失，CPU与服务器不属于本轮。

## 2026-11-02 · 当前推荐：两份较晚 Train 前缀，旧六组不重跑

从main `db65d3476c4709cd8b43e2c31ab40c1ace3671df`继续本地分析，[权重与质量研究](step_quality_research.md)确认两份未比较前缀。旧C1–C6已执行且全双失败；以下历史六项清单不再是待执行队列。SQLparse cutoff5也已比较，未列入下一轮。STEP_001实体已删除，同权重CPU对照仍0/12，不使用替代权重。

| 下一轮候选 | 原来源 | 精确截止与状态 | 原验证 |
|---|---|---|---|
| A1 Records | [task_source](../20261101-v9-overnight-real-supervision/t18-records/task_source.json)；TRA-002 Train | `t18-records-sol-low / 4`；[trajectory](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/mini-swe-agent.trajectory.json) messages[0:10]；[events](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/events.jsonl)第18行，verify | 24项（1 FAIL_TO_PASS / 23 PASS_TO_PASS）；原[run_config.verify_command](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/run_config.json) |
| A2 async-timeout | [task_source](../20261101-v9-overnight-real-supervision/t15-async-timeout/task_source.json)；TRA-002 Train | `t15-async-timeout-sol-low / 5`；[trajectory](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/mini-swe-agent.trajectory.json) messages[0:12]；[events](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/events.jsonl)第22行，verify | 32项（3 FAIL_TO_PASS / 29 PASS_TO_PASS）；原[run_config.verify_command](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/run_config.json) |

两项均已有真实复现与失败测试反馈、尚未修改源码或测试；阶段verify来自保存状态，不重标成modify。完整消息与已有比较无结构相同记录，原准备入口恢复消息/生成/工具计数一致。来源为两个已有任务/两个仓库，不新增来源任务，仍UNLABELED。旧19条与74行不增加；路线B仅推荐，不改现行标签条件。

### 下一轮执行提示词（资源范围待负责人批准）

继续最新main，仅执行上表A1、A2两份不同历史前缀，不重新选任务，不重跑旧六对、旧Episode、Twin或训练。

申请的最小执行范围是本机已有Docker/基础镜像和现有付费Provider：每前缀真实Sol low/Luna low各一步，最多4次生成、4个隔离工具分支。每前缀恢复后取一次原范围前值，两分支各运行一次原验证，共6次原验证。教师关闭；不访问服务器、下载模型/依赖、占GPU、训练、启动完整Agent Episode、修改Serving/F14/handoff或接触Dev/Final答案。本文件本身不授予这些资源权限。

复用原Provider、DefaultAgent/DockerEnvironment、工具解析/执行、反馈保存和real_supervision/prepare。按原environment/task_source恢复同任务初始版本，只重放截止前已发生命令；同一截止历史、同一环境、同一工具窗口/测试范围，不把原后续动作、解答或终局放进输入。现存基础镜像未知是否齐全；资产缺失时报告具体缺项，不自动安装、下载或重建。

从实际容器读取uname，使用原Agent变量描述当前工具环境。保存的Darwin历史文件不改；若直接恢复已渲染历史，两候选共同追加同一条真实环境事实说明并保存完整新请求消息，明确区分原历史与当前说明。不要指导修复计划、指定下一工具命令或给单个模型安装rg/apply_patch。

逐候选保存实际请求/返回身份、请求Effort与供应商应用档位证据、Usage/缓存/费率、原命令、工具退出状态/反馈、原测试结果和未知原因。应用Effort未确认时为UNKNOWN，仅允许MODEL_ONLY；AA沿原v4，Max分不当low实测。恢复后的前值与新结果只作验证依据，不加入此前截止输入。

原Verifier/测试文件与run_config.verify_command保持。只在一步后原范围一方可信通过而另一方未通过时产生原步骤质量偏好；双方通过且费用可确认时产生等质量费用偏好；双失败、未知、API/身份/环境异常只保留观察。不按测试通过总数、仅读取或教师判断造赢家。

保存原固定测试ID的前后结果、已知修复项和新增回归供路线B研究，日志缺单项状态时为UNKNOWN；不新增报告依赖、变更Verifier或为部分改善创建新训练标签。Records额外全suite的7个errors、timeout的2个skip与原24/32项分开记录。

四次生成及原验证结束即报告真实质量/费用/观察数量；如果仍双失败，停止扩大同类收费采集，提交负责人决定独立质量进展目标。不要自动训练或开展CPU对照。保存原始结果并按范围更新现有报告；及时移除本次自有容器和无用临时文件，不建备份、不删基础镜像/研究权重/真实失败。GitHub与服务器状态分别报告。

## 历史准备：75bad09（以下各节不作为当前执行任务）

从 main `75bad09780d559fc5027be8cd0818e9d6b61637e` 接续。本轮完成一个原入口的候选覆盖处理，筛出六个未比较前缀，并确定三份 CPU 对照输入。新模型调用、工具分支、CPU 模型前向、训练和服务器访问均为 0；新增有效监督为 0。

原 124 次诊断、19 次 DeepSeek Episode、独立 TwinRouterBench、历史训练和真实比较均不重跑。原结果见 [离线分析](offline_router_analysis.md) 和 [summary.json](summary.json)，本轮事实在 `local_followup_preparation`。

## 1. Model-only 接口

`CheckpointRouterClient.route` 用 `action["model"]` 建立字典。同一模型的 low/high 等合法候选会共享键，后者覆盖前者；问题说明和输出标签又只有模型身份，不能表达联合动作。已有 `RouteRequest` 只拒绝重复 `action_id`，所以两个不同档位可以通过该 Schema。原 Harbor 的成员判定只能确认选中动作属于候选集，不能找出被丢掉的候选。

只在 `v9/runtime/checkpoint.py:CheckpointRouterClient.route` 比较原候选数量与模型字典数量；不一致时在启动推理进程前抛出 `ValueError`，说明这个 Checkpoint 的 MODEL_ONLY 入口每模型只能有一个动作，不支持同模型多档 Native Effort。保留原问题、说明、候选顺序、概率计算、排序、权重和输出字段。

少量离线确认已完成：

- 使用 [build-pmars 原事件](alias-build-pmars/events.jsonl) 的 Sol/Luna/Flash 三个候选，原顺序、保存的 Top-1 与全部排序动作仍映射到同一原始候选；没有产生新的概率。
- 使用该记录中的 Luna low 与原 Registry 合法的 Luna high，普通 `RouteRequest` 保留四个不同动作，Checkpoint Model-only 明确报错，`process` 仍为 `None`。这只证明接口行为，不证明供应商实际应用了档位。
- 原文件语法有效；未使用模型实体、SSH、模拟 Router 或新测试文件。不同模型正常路径的完整前向未执行。

职责和调用方已读取：`checkpoint.py`、`benchmark/harbor_agent.py`、`serving/schemas.py`、`v9/runtime/decision_hook.py`。普通 Serving 联合动作、Harbor 原候选成员判定、Provider、教师和 Trainer 均未修改。

## 2. 六个未比较的 Train 前缀

六个前缀来自六个**已有**公开训练任务、五个仓库；OAuthlib 两题共享代码版本，分别涉及 RFC6749 工具函数与 RFC8628 endpoint，不能计为两个独立仓库。阶段为 inspect 2、modify 3、recover 1，来自原事件启发式状态，不是新人工标签。本轮新执行任务数为 0。

来源均为已保存 `TRA-002 / SWE-bench/SWE-smith / train`，数据许可 MIT。沿用各批次 `task_isolation.json` 的精确任务 ID、可识别仓库/镜像证据：Canary8、Dev24、Final57 及 TwinRouterBench 交集均为 0；不据此声称所有语义近重复都已排除，也没有读取 Final 答案或验证器。源码许可证仍以原任务环境记录为准。

| 候选 | 任务 ID | 截止阶段与实际可见信息 | 已发生工具数 / 末次退出码 |
|---|---|---|---:|
| C1 OAuth2 scope | `oauthlib__oauthlib.1fd52536.combine_file__09vlzwgc` | inspect；已读 `rfc6749/utils.py`，任务描述包含顺序、空值和 URI scope 处理异常；还没有产生下一步命令 | 1 / 0 |
| C2 Device authorization | `oauthlib__oauthlib.1fd52536.combine_file__0mvyid7d` | inspect；已读 `rfc8628/endpoints/device_authorization.py` 并定位原 device 测试目录，尚未编辑 | 1 / 0 |
| C3 SQL output formatters | `andialbrecht__sqlparse.e57923b3.combine_file__kep88kh8` | modify；已见 Python/PHP formatter、formatter/filter_stack、入口及原输出测试；适合判断跨文件调用与输出状态，尚未写后续复现脚本 | 4 / 0 |
| C4 Records parameters | `kennethreitz__records.5941ab27.lm_rewrite__letryq82` | modify；已读 `records.py` 的连接/query 路径及原测试；此前已见 SQLAlchemy 2.0.36，尚未执行后续复现和修改 | 3 / 0 |
| C5 Autograd Sylvester | `HIPS__autograd.ac044f0d.func_pm_ctrl_shuffle__fhf7s9be` | modify；已读 `autograd/scipy/linalg.py` 中 VJP 的实际赋值/返回顺序及原梯度测试；下一条修改尚未发生 | 3 / 0 |
| C6 Timeout recovery | `aio-libs__async-timeout.d0baa9f1.lm_rewrite__kqd6t1mb` | recover；已读取 timeout 实现和原测试，组合读取命令末尾因镜像没有 `rg` 返回 127；保留实际失败和此前输出，不伪造测试败因 | 2 / 127 |

### 精确历史与状态位置

路径都引用原资产，不复制完整消息、环境、任务 patch 或新训练视图。`messages[0:N]` 是零起点、末端不包含 N，包含截止前全部真实消息；下一条 assistant 及其工具结果不在输入内。

| 候选 | 原 Episode 与截止 | 完整消息引用 | 原决策前状态 |
|---|---|---|---|
| C1 | `oauth2-scope-sol / 1` | [trajectory](../20261101-v9-k2-supervision-expansion/oauth2-scope/episodes/oauth2-scope-sol/mini-swe-agent.trajectory.json)，`messages[0:4]` | [events](../20261101-v9-k2-supervision-expansion/oauth2-scope/episodes/oauth2-scope-sol/events.jsonl) 第 6 行 |
| C2 | `oauthlib-sol / 1` | [trajectory](../20261101-v9-k2-supervision-expansion/oauthlib/episodes/oauthlib-sol/mini-swe-agent.trajectory.json)，`messages[0:4]` | [events](../20261101-v9-k2-supervision-expansion/oauthlib/episodes/oauthlib-sol/events.jsonl) 第 6 行 |
| C3 | `sqlparse-sol / 4` | [trajectory](../20261101-v9-k2-supervision-expansion/sqlparse/episodes/sqlparse-sol/mini-swe-agent.trajectory.json)，`messages[0:10]` | [events](../20261101-v9-k2-supervision-expansion/sqlparse/episodes/sqlparse-sol/events.jsonl) 第 18 行 |
| C4 | `t18-records-sol-low / 3` | [trajectory](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/mini-swe-agent.trajectory.json)，`messages[0:8]` | [events](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/events.jsonl) 第 14 行 |
| C5 | `t19-autograd-luna-low / 3` | [trajectory](../20261101-v9-overnight-real-supervision/t19-autograd/episodes/t19-autograd-luna-low/mini-swe-agent.trajectory.json)，`messages[0:8]` | [events](../20261101-v9-overnight-real-supervision/t19-autograd/episodes/t19-autograd-luna-low/events.jsonl) 第 14 行 |
| C6 | `t15-async-timeout-sol-low / 2` | [trajectory](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/mini-swe-agent.trajectory.json)，`messages[0:6]` | [events](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/events.jsonl) 第 10 行 |

已用原 `v9/training/prepare.py:build_offline_prefix_input` 在内存恢复六份截止历史；生成数、工具数、末次退出码与保存状态全部对应，4/4/10/8/8/6 条消息均截止正确。六份教师值均为 null，能力快照均为 `20261031T072548885180Z-v4`。没有运行工具、原任务测试或 Tokenizer/模型前向，也没有把轨迹终局写入这些状态。

### 原环境、验证范围与资源

六题均沿用 `minisweagent.environments.docker.DockerEnvironment`、mini-SWE-agent 2.4.6、`/testbed` 和原 bash 协议。下表的配置文件给出完整 `verify_command`、原初始镜像版本 `initial_environment_version`、模型协议和输出参数；命令按原字段执行，不人工替换或删减测试。

| 候选 | 任务与环境依据 | 原验证范围与完整命令来源 |
|---|---|---|
| C1 | [task_source](../20261101-v9-k2-supervision-expansion/oauth2-scope/task_source.json)、[environment](../20261101-v9-k2-supervision-expansion/oauth2-scope/environment.json)；OAuthlib 1fd52536、scope 任务初始版本 | 673 项；[run_config.verify_command](../20261101-v9-k2-supervision-expansion/oauth2-scope/episodes/oauth2-scope-sol/run_config.json) |
| C2 | [task_source](../20261101-v9-k2-supervision-expansion/oauthlib/task_source.json)、[environment](../20261101-v9-k2-supervision-expansion/oauthlib/environment.json)；同仓库版本、不同任务初始镜像 | 673 项；[run_config.verify_command](../20261101-v9-k2-supervision-expansion/oauthlib/episodes/oauthlib-sol/run_config.json) |
| C3 | [task_source](../20261101-v9-k2-supervision-expansion/sqlparse/task_source.json)、[environment](../20261101-v9-k2-supervision-expansion/sqlparse/environment.json)；SQLparse e57923b3 | 331 项；[run_config.verify_command](../20261101-v9-k2-supervision-expansion/sqlparse/episodes/sqlparse-sol/run_config.json) |
| C4 | [task_source](../20261101-v9-overnight-real-supervision/t18-records/task_source.json)、[environment](../20261101-v9-overnight-real-supervision/t18-records/environment.json)；Records 5941ab27 | 24 项；[run_config.verify_command](../20261101-v9-overnight-real-supervision/t18-records/episodes/t18-records-sol-low/run_config.json) |
| C5 | [task_source](../20261101-v9-overnight-real-supervision/t19-autograd/task_source.json)、[environment](../20261101-v9-overnight-real-supervision/t19-autograd/environment.json)；Autograd ac044f0d | 585 项；[run_config.verify_command](../20261101-v9-overnight-real-supervision/t19-autograd/episodes/t19-autograd-luna-low/run_config.json) |
| C6 | [task_source](../20261101-v9-overnight-real-supervision/t15-async-timeout/task_source.json)、[environment](../20261101-v9-overnight-real-supervision/t15-async-timeout/environment.json)；async-timeout d0baa9f1 | 32 项；[run_config.verify_command](../20261101-v9-overnight-real-supervision/t15-async-timeout/episodes/t15-async-timeout-sol-low/run_config.json) |

原清理已移除临时初始/分支快照，不能假定这些旧 tag 现在存在。后续复用原基础镜像与保存的初始化操作：恢复同一任务的原问题状态，仅重放截至上述截止的原命令，保存实际反馈，再为两个候选建立同一环境起点。原测试恢复方式、结果和 Artifact 保存沿既有实现。任务 patch 只供原环境构造/验证使用，不进入模型状态。当前本机 Docker 和基础镜像是否仍可用未取样；本轮没有启动 Docker、恢复快照或下载任何资产。

C1–C6 都是 **UNLABELED / 可准备同状态候选对 / 未执行新比较**。原任务终局和旧比较是 `OBSERVED_OUTCOME_ONLY` 或既有监督，不能成为这六个新前缀的答案；没有一条新真实赢家。原 `real_supervision.prepare_comparison` 对 UNLABELED 不产生路由目标，不能把这些引用混入现有 74 行训练材料。

本轮还看到 h11、python-json-logger、boltons、dotenv、addict、xmltodict 等目录只有元数据获取失败，不具备本地真实历史和完整环境依据，未列入这六项。没有因候选不足重下载原始轨迹或访问服务器。

### 取得授权后的最小真实比较

六个前缀各比较真实 `gpt-6.1-sol:low`、`gpt-6-luna:low`：共 12 次候选一步生成、12 个隔离工具分支及同范围原验证，不运行完整新 Episode。沿原 Provider、DefaultAgent 工具解析、DockerEnvironment、反馈/费用保存和 `v9/training/real_supervision.py → prepare.py`。

两个候选必须看到同一截止消息、同一问题说明、Sol→Luna 候选身份/价格及上述 AA v4；采集关闭教师。请求 low 仅为配置，应用档位仍未知，目标只允许 MODEL_ONLY，Native Effort 不产生答案。只在原验证有可信差异时产生一步质量偏好；双方通过且费用可计量时才产生等质量费用偏好。双方失败、未知、API/身份/环境问题均只存观察。

特别是 inspect：如果两方只完成有效读取、原任务验证仍失败，不把定位说明或教师评价升级为质量赢家。现有步骤目标是“该步后立即通过原范围验证”，没有改成长程收益或主观进展评分。本轮选择依据是可见问题和阶段覆盖，未根据后续赢家安排模型标签比例。

## 3. CPU 对照准备，未实测

现行实际路径为 `CheckpointRouterClient.route → checkpoint.main → LayaAdapter.system_one → 原生 RLAgent.system_one`。`LayaAdapter.route` 的联合问题不是这批 124 次调用入口。客户侧 `PreDecisionState.router_text` 在请求 payload 构造时执行，原客户端路由计时从 payload 构造之后开始；不能将这个状态格式化段误当服务器 encoder 时间。

| 待计时段 | 现有边界与记录方法 |
|---|---|
| 输入整理与原生 Token 编码 | Adapter 的 `formatted_questions` 到原生问题/state 转换、Tokenizer 与 build_sequence 完成；状态布局生成单列，原总段不包含客户侧 formatter |
| Batch / Collate | 原生编码项到 padded batch、mask 与选项位置完成，保留同一 CPU 张量与窗口 |
| Transformer Encoder | 原 DecisionModel 的 ModernBERT encoder 实际 forward 进入/返回；用该模块临时 forward hook 计时，输出原样继续 |
| Transformer Head | 原两层全序列 Transformer head 实际进入/返回；与后续候选 gather/logits 分清，不把整个模型 forward 重复相加 |
| 输出概率转换 | 原 logits/act 到既有 softmax、标签、置信度与 JSON 概率；原算法及精度保持 |
| 完整 system_one | 沿 Adapter 已有 `perf_counter` 入口到返回；问题整理、原生编码/模型/解码均包含，初始化另列，段间剩余时间单列 |

原生参考来自上一轮已读取的 [RLAgent](https://huggingface.co/convaiinnovations/laya/blob/7b928d828b7b0e022f929d9bd2e44165aa270148/rl_agent_api.py) 和 [DecisionModel](https://huggingface.co/convaiinnovations/laya/blob/7b928d828b7b0e022f929d9bd2e44165aa270148/rl_common.py)，本轮没有重新下载。授权后应实读原服务器实际导入版本再确定段内函数/模块名称；当前没有把公开参考称为服务器源码实读。原 Trainer 编码入口及 encoder/head 分组只读，用户已有修改未动。

### 三份保存输入

全部来自旧结果、只用于 CPU 对照；Dev/Alias 不进入 Train，也不调用生成模型。

| 输入 | 精确状态位置 | 原保存 system_one 秒 | 原保存概率 Sol / Luna / Flash |
|---|---|---:|---|
| S1 短历史：build-pmars / 0 | [events](alias-build-pmars/events.jsonl) 第 4 行，history 为空；授权后记录实际 Token 数 | 8.565615 | 0.3885 / 0.3229 / 0.2886 |
| S2 长窗口：build-pov-ray / 20 | [events](alias-build-pov-ray/events.jsonl) 第 84 行；原离线分析属于触及 5120 且工具 history 仍裁减的状态 | 34.282088 | 0.4100 / 0.2776 / 0.3125 |
| S3 最小 Sol 领先：financial-document-processor / 15 | [events](alias-financial-document-processor/events.jsonl) 第 64 行，原领先差 0.0290 | 24.367438 | 0.3821 / 0.3531 / 0.2648 |

获明确授权后：同一服务器 CPU、同一 `V9_LAYA_STEP_001-e01` 实体，仅加载一次 Adapter；三份状态分别进行旧/新布局 × no_grad/inference_mode，共 12 次真实 system_one。旧布局从已有 Git 历史的 formatter 在内存取得，新布局使用当前唯一 formatter，原状态字段值、候选及问题说明保持。不改 attention、模型、窗口、概率、线程或 Serving。记录实际 CPU/PyTorch 线程、Checkpoint 元数据、调用次序、Token/候选位置、原概率和选择、各段及总耗时；初始化另列，不将单次样本当稳定速度结论。

仅在这一个临时进程内，对实际原函数边界加少量 `perf_counter` 与模块 hook，使用完移除；不添加长期计时选项、第二套推理程序、服务或依赖。没有必要在未接触服务器实际实现前给产品加入 profiling 分支。

当前已保存 3081.16 秒及 r≈0.98694 仍只有整段/输入相关证据；encoder/head 占比、新旧概率差、inference_mode 耗时差均未知。本轮 CPU 前向为 0，没有性能改善结论。

## 4. 接续判断与权限

优先实施上述真实质量前缀比较，并在独立 CPU 范围测量开销；当前没有新增动作答案，不能仅凭 74 行再训。Laya 保留 F11-e01、STEP_001；Kev 保留 R11，无新参数更新。原 S1 固定 Val 与独立真实 Dev 的用途保持，任务级成本和步骤级质量不混用。正式 K=3、确认的 Native Effort 和教师净收益仍未具备证据。

下一次最小资源范围分开授权：

1. 本机原 Docker/既有基础镜像及现有两模型付费 Provider：六前缀、12 次一步生成和分支原验证，教师关闭；若资产缺失，另说明具体缺项，不自行下载依赖或访问服务器。
2. 原服务器 CPU：只读实际导入源码/指定 Checkpoint，在单独短生命周期进程执行三状态共12次前向；不占 GPU、不操作 F14/handoff、Serving、队列或健康服务，不运行 Agent/外部生成 API。

两项本轮均未获得资源授权、未执行。F14/Serving 实时状态未刷新；最后保存快照仍是 2026-11-02 03:36:36 台北，F14 独立维护首轮 284/420、Val 未完，Serving F05-e01/原 Kev。不能把这个历史取样写成当前在线状态。

本轮改善的是接口覆盖与可追溯训练条件；没有使模型已经更会选择。原始实验、失败、训练报告、用户 Trainer/tests、私人文件和用户删除全部保留；没有临时模型/依赖或运行环境需要清理。
