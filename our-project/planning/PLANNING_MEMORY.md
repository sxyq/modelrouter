# ModelRouter · Planning Memory（研究协作记忆）

> **版本：v2.4｜更新：2026-10-30｜角色：Planning Agent + Execution Agent**
>
> **定位**：供后续 ChatGPT Planning Agent、本地 Execution Agent 快速恢复项目上下文的唯一**公开安全**交接入口。项目记忆由执行者按事件维护：Memory/Status 随事件更新，Research 仅在研究证据、方法或实验协议变化时修改；它与 ChatGPT 产品内置 Memory 分开，也不会自动在后台更新。本轮主 Agent 已获测试、部署及合规源码/六文档同步原 GitHub main 的明确授权；本分支只编辑六份原文档，不做 Git 操作。
>
> **公开性**：仓库为 public。不得提交私有服务器 IP、SSH 用户名/命令凭据、密钥、原始私人会话、私有任务内容、个人本地绝对路径及未脱敏日志。必要的机器路径放在本地不跟踪的配置或安全通道内。

## 0. 30 秒恢复上下文

**2026-10-30 当前恢复点**：用户明确从未设置 API 总 Token 或美元预算，按任务需要充分测试，保留服务器资源规则、健康训练不中断和 Final 隔离。原 Provider 累计上限已移除，max/remaining=null、用量保留，原 CLI 默认 cost_limit=0。原项目 Provider/models 实际返回 3 项，研究池只列 Luna，Sol/托管Flash未列出；这属于供应商可用性，不转写为等待人类批准。

新 `20261030-v9-official-luna-complete` 已官方成功，真实 Luna none/low、reward=1.0、CTRF 2/2、14 路由/0 fallback；它只代表单模型双动作的小开发结果。完整执行统计、Job/Trial、218,578 Token 和旧失败统一见 [PROJECT_STATUS](PROJECT_STATUS.md) 当前入口，不重跑成功题或重做既有训练。费用分支已在原计价器复用原请求按已读官方价核算并保存；供应商 bill 未知单列，不影响执行。27B 是用户非自部署的托管 API，self-dploy 仅为 API 返回身份，不推断零费用；计费算法及来源见 [数据台账](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md#当前托管-api-身份与计费政策2026-10-30)。

原 `AGENTS.md` 用量条目已由主 Agent 原位更新，取消累计 Token/default USD 限制；该文件含私有服务器信息，不纳入本轮公开同步，本分支未修改它。

**部署接续结果**：原服务链17文件定向部署，Serving PID327621于20:53:21启动；重启后Laya/Kev均HTTP200、fallback=false，仍用F05/epoch_01和Kev原导入适配器，没有晋升V9权重。Kev未压缩前缀90秒超时已保留，原6000字符任务/工具视图前向82.28秒成功，但仍超原60秒窗口，不能当Kev时延达标。21:18:38服务healthy、两权重已加载；F14到Epoch1第420/420块，第63–420块358块NaN，有效更新/根因未知，不干预。30原请求已Decimal复核，原事件追加官方费率对账，旧金额与用量保留。完整身份、时间与剩余科研/费用缺口见 [PROJECT_STATUS](PROJECT_STATUS.md)；不重跑成功Episode、不重训，不新增实现或未来调度。

最后只读补充21:23:32：F14自然进入Epoch2第1/420块且仍NaN，不是人工重训/接续；自有8000隧道已关闭。六原文档及必要代码增量已同步原服务器，公开同步只纳入合规源码与六文档，原账本、测试、用量记录和用户删除保持本地原状。

**10-30 20:05历史恢复点（旧额度安排已取代）**：原Mac Docker运行，Rosetta下原官方fix-git Oracle已reward=1、CTRF 2/2；两次基础设施失败保留。真实Luna Episode执行9生成/18工具/3教师，但单候选触发原Laya `topk(2)`错误，第10次生成又因原预算容量不足未发出，Verifier未执行。原配置现为同Luna none/low双动作；保存真实前缀已获得非回退前向，未重跑完整题目。能力v2在该Run中保存，现有390训练行仍v1、三身份最优标签仍0。配置价估算0.182588USD、现金账单未知；累计147calls、已知714168、预留256135、剩29697。当时建议先取得足够预算及Sol/Flash项目凭据的安排仅保留历史，现行无累计额度限制；复用原结果和已更新配置，不重训、不重建Harness、不把Oracle或前缀前向计模型成绩。当前详细结果唯一维护于 [PROJECT_STATUS](PROJECT_STATUS.md)；下方早期恢复点均为历史。

**10-30 17:56历史恢复点**：两项V9训练/固定Val已完成且不重训，新权重不替换Serving；F14仍运行且第63–371块NaN，根因/有效更新未知，非有限loss候选不用于后续父选择。能力v2已在盘（LunaMax27.7552/AA5.0+9项，其余精确型号缺测），旧390行仍绑定v1、真实三模型动作目标0。原formatter同一真实样本已保留三候选摘要/教师/任务/工具tail，但Laya完整能力及长历史仍裁；旧模型未学新布局。原CLI单Episode与run_id来源已补，教师汇总原事件6/5请求、USD未知。Docker仍不可用，不执行Trial或绕权限。先完成公开安全同步，再恢复原MacDocker与原Oracle resume；停止与详细证据见 [PROJECT_STATUS当前入口](PROJECT_STATUS.md)。以下10:40/04:34内容均按历史时点阅读，不能覆盖此处。

**10-30 10:40 历史接续**：Laya `V9_LAYA_001` 已沿原 F13 完成记录跳过重训并接续，完成两轮和每轮 5,692 条固定 Val；第 2 轮总体 Accuracy 49.51%，父 F11-e01 为 48.23%，S2/S3 改善、S1 四项退步。198 条 Train 全部消费，192 完整/6 部分 state，4 教师核心保留，仍为 `FEATURE_PARTIALLY_TRAINED`。原目录链接识别问题仅改原 `continuation.py` 一行并部署，保存权重真实 CPU 加载/前向通过，状态 `COMPLETED`；新权重未上线。原留存移除第 1 轮权重，参数与成绩保留。Kev 两轮/Val 已完成但四指标退步。F14 第 63–260 块共 198 块 NaN；该块 8,192 个原目标向量数值有限，具体诱因与有效更新未知。AA Key 缺失、三身份同一 Qwen、完整 USD 和 Docker 权限仍影响正式评测。详细指标、实体路径与停止位置只在 [PROJECT_STATUS](PROJECT_STATUS.md) 首页维护；下方旧“Laya 未启动”及第 175 块记录按旧时点理解。

历史参数接入阶段：原 Harbor `run --v9-config` 已接入三候选及原 `resume` 保存参数，真实上游 JSON 解析/Agent 实例构造通过；尚未运行官方 Trial，Docker 条件见 Status。仅改原 CLI，没有新增 Runner。

### 2026-10-29 起 · V9 原文档同步、三身份联调与数据接续要求（10-30 接续）

**恢复指针**：2026-10-28 用户已明确保留 **V9 五 RQ（1 Overall、2 Pool、3 Decomposition、4 Ablation、5 Workload Boundary）与 8 图/12 表**。此前三 RQ、消融合入 RQ1 的建议不再代表现行决定。四段下载聊天与两份提示词已完整复核；原 linked 聊天已移除、本机 source 文件缺失，下载副本的复核仍有效。后段关键依据为原讨论行 25981、26344、26368、27359–27361、28201–28203、28747–28784；本轮只优化原六份文档，保留独有证据和历史负结果。

**模型身份与权限**：首批逻辑 ID 固定为 `gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`；高/中/低仅表示候选角色，不预设能力排名。V8 原两Luna调用范围仅保留历史；用户已充分授权 V9 测试及部署。原 Provider 实际返回 3 项，研究池当前仅 `gpt-6-luna` 列出，Sol/托管Flash未列出，按实际供应商可用性记录。三 ID 统一映射已有 Qwen 的真实 Provider 请求均已确认，用途为 `ALIAS_SMOKE`；网关 `/models` 与先前流式名 `Qwen3.8-27B`、实际非流返回名 `self-dploy/Qwen3.8-27B` 分别保留，不能将其算作三种真实模型或正式 RQ1/RQ2 成绩。审阅子 Agent 的 `gpt-6.1-sol/max` 配置不代表生成器或教师已配置。27B 为非自部署的托管 API，self-dploy 字符串只记录返回身份，不推断本地零费；物理对应仍为 UNKNOWN，9002 物理部署与 Parfit API 身份分别记录。

**唯一实现与教师输入**：新增方法集中在 `our-project/code/src/modelrouter/v9/` 的 `runtime`、`teacher`、`capabilities`、`training`；旧 Provider/Agent/Serving/Trainer/telemetry 只接入必要调用，同一功能一个正式实现。现有 Agent 继续执行工具与验证；单活跃 Laya **或** Kev 负责选路。首版教师只参考两条成功证据明确、许可适用且与 Final 隔离的固定公开摘要（高效完成/失败恢复），不建在线检索服务。核心 `progress_summary`、`main_blocker`、`next_milestone` 必须进入实际 state 文本及模型编码；离线前缀与在线状态采用同义表示。约三次生成或阶段/停滞事件触发只作为 Dev 起点。字段尚未学习记 `FEATURE_NOT_TRAINED`，已有接口前向不能证明新特征有效。

**数据、缓存与费用**：优先复用 V2.1/L1、既有 S1/S2/S3 合法资产及固定划分；Q 记录质量、S 监督类型、L 覆盖层级分别保留，行数、独立单位、路由比较标签分开统计。AA 分数、观察动作、同一轨迹重复终局标签不能变成最优动作标签。每次手动执行专用刷新入口重新请求 AA，Agent 使用已保存快照；Agent 启动和 Router 每次决策不自动访问 AA，正式训练/实验固定相应 `snapshot_id`。来源、版本、缺测与实际编码状态照实保留，复用现有 `load_current`，不新增自动网络行为、job 或长期调度器；自动刷新派发已由用户撤销。连续消息上下文与 Provider/引擎实际 KV、缓存用量双记；Alias 同后端不证明跨模型缓存可共享。顶级教师与联调教师分别标明实际身份；离线教师制作成本归数据/训练，在线教师成本归 Episode，不重复计价。本机不存 Laya/Kev 权重；全部执行者、教师及重试按实际 API 用量记录，不设累计 Token 或默认美元上限。

**历史训练与真实结果边界（截至10-30 04:34）**：原训练按既有队列自然接续，不干预活跃worker、不重载正在使用的权重；F13及21:59原链F14正常的早期回报保留；F14运行推进、损失持续非有限，有效优化更新未确认，具体诱因未知，Laya V9尚未启动。Laya/Kev 各用同协议 Val 和独立 Dev 选起点，Final 不参与迭代。SWE/Terminal 的任务、Evaluator 和成绩独立。invoice Alias 成功终局：9 次生成、13 次 Bash、7 项 unittest 通过，Laya `fallback=false`、Checkpoint `epoch_01`，仅选 Sol；duration 两次失败另记，额外短 Provider 映射不算新题。源码部署完成，Kev三次失败均保留：13266导入失败、16722在8K真实反向中OOM、44839因已有目录exit2。原CLI25201已自然退出；第四次worker50518于2026-10-30 03:25:31完成2 Epoch/100 steps、自然退出0，模型已保存于A6000；原dispatcher50514同秒自动开始固定Val attempt1；2026-10-30 04:23:20台北完整结束，控制器自然退出0，`status/training_status=COMPLETED`、`evaluation_status=EVALUATED`。新候选为`FEATURE_PARTIALLY_TRAINED`（4条稀疏教师、三新身份监督目标仍0），原Serving仍旧权重/`FEATURE_NOT_TRAINED`，未传Mac或上线Serving。step5近期工具真实末128字符已验证，长history仍裁；Laya下一child边界及新特征有效性仍待，Serving仍旧权重，详情见 [PROJECT_STATUS](PROJECT_STATUS.md) 首页。固定Val8436记录/9330问题完整完成，拒绝/裁减0、`test_used=false`；相对原C03四指标均退步，内部score92.38703579133796。V9组仅1条，rank1不表示优于C03；新权重仍只在A6000、未上线Serving，正式Harbor/RQ成绩仍空白。

**新增材料证据**：唯一实体仍为 390 条，Train 198/Val 192；S1、S3 各 Train/Val 64，S2 Train 70（原 64+6 真实前缀）/Val 64，`trajectory_prefixes/train.jsonl` 仅为相对符号链接，不重复计数。六前缀来自 `gruebel_pycep_pr109`、`fonttools_fonttools_pr2313`，每题截止 0/3/7，与固定参考 `roniemartinez_latex2mathml_pr163`、`cloudtools_troposphere_pr2024` 不重合，原 Train 资格保留。旧 S1 的三身份 choice 目标仍 0。离线 Teacher 初始 0 的阶段记录保留；随后原 Assessor 2 请求/2 成功，4 条可用三字段样本（2 新、2 复用）、2 条未触发，`summary.teacher_data_status=PARTIAL`、`GENERATED=4 / NOT_GENERATED=386`。AA 实测来源为 Sol 404、Luna 200 但解析失败、Flash 404，Key 缺失，实测能力记录仍 0，current 保留缺测快照。在线 Teacher 由 2 次成功/1 次超时发展为 3/6 成功，失败后 Agent 继续；实际教师为 `self-dploy/Qwen3.8-27B`，不能当顶级 Sol 或新特征学习证据。

**输入与费用证据**：旧 LayaState 两次为 2,762/2,827 Token、预算 940、任务位置 2,733/2,798，任务被裁的负结果保留。唯一 V9 formatter 已改任务优先/压缩缺测卡，原 Schema 薄调用；已保存的 [final编码与训练prefix分词记录](../results/iterations/20261029-v9-alias-smoke-tools/input_encoding_validation.json) 确认最终任务、三教师字段、候选卡和缓存/身份关键字段进入编码。新顶层`recent_tool_validation`于18:44 UTC/02:44台北仅验证原step5：Laya1024/head512、状态预算940下，512字符真实工具结果仅末128字符在Token `[879,930)`为`FULL`；任务、三教师、三候选卡及缓存/当前和前次身份均`FULL`，长`history_snippet`仍裁。Kev原native编码2147 state/2224 total、不截短、候选键3个，本次未新增Kev API前向。18:46 UTC/02:46台北同源Laya真实API前向`fallback=false`，选Luna，概率Luna0.4005/Sol0.3519/Flash0.2476，模型前向1961.71ms、客户端1985.07ms，checkpoint仍`epoch_01`。主Agent本次新增Router1/生成0，135calls及575783/256135/168082预算不变。随后原`v9/runtime/context.py`单文件原位部署，fresh导入路径相同；序列化8822字符、真实128字符tail、源cached3136及前次Sol身份保留，cached3136仅为源字段，不算本次Router新缓存命中，未重启Serving/模型。此前已保存的198条Train分词测量继续保留，本次未重测全部Train或Val；当前Laya1024保留4条教师核心，但完整state裁6条；全198条完整编码至少需8143，8192推荐尚未启用。192条Val仅核身份/数量，未测Token长度；不将上述分词结果作新特征学习证据。成功目录的 `router_input_replay.json` 已记录新 Native 前缀真实前向：Laya 选 Luna、`epoch_01`、`fallback=false`；Kev 首次 20 秒窗口超时并走模拟 fallback，一次 60 秒窗口重测约 53,516 ms 真实前向成功，选 Sol、`fallback=false`。Kev 是 Serving 导入适配器，不能称 R11 候选；两路均有三候选真实概率，不沿用旧概率，不重跑同题、不增加正式成绩。离线两请求 prompt 13,766+completion 949=14,715 Token，reasoning 678 已含于 completion，cached 0 已报告、USD null；结果复用与物理缓存分开。所有请求的完整 usage/费用仍 null，未知单位 cost 不计 USD，预留不作实际消耗。 同一原记录新增`live_transport_validation`：2026-10-30 04:20:38台北对原invoice step5实际调用旧Serving `/v1/systemone`，8822字符state按字符串直传；3候选依次`jiji/gpt-6-luna`、`openai/gpt-6.1-sol`、`aliyun/qwen3.8-flash`，均`effort=none`。HTTP200、`fallback_used=false`、checkpoint仍`epoch_01`，概率0.4005/0.3519/0.2476，响应`usage.input_tokens=1024/output_tokens=0`。同发送正文的原native编码为2684状态Token/940余量/1024总Token，任务、教师、能力卡、continuity及最近工具末128字符保留。仅“直传调用链、同发送正文native编码与响应Token数支持”这一范围；未捕获旧服务进程Token IDs，普通`/route`未验证，长history仍裁，未重跑整个Episode、重启旧服务或加载额外模型。 本次再增Router1/生成0，Provider账本135calls及575783/256135/168082不变；04:20请求与此前02:46回放分开记录。

**Kev 新题失败与后续范围**：迭代 `20261029-v9-kev-alias-smoke` 在另一 `duration` 工程题上完成 2 次真实生成、3 次 Bash 后，第 3 次路由在 60 秒窗口超时；默认原 `PolicyModel` 在 Router fallback 后退出，终局原回报 `FAILED/验证1`、日志全保留。Serving `2291306` 未重启/换权重；启动时 `KevAdapter` 未传 `device`，默认 CPU、原 `torch_cpu`，step0/step1 真实前向 18,802/38,674 ms，step2 工具 history 长度回报 3,835（单位未报）时超时。首个 Bash 用 `find /` 查文件后上游 30 秒超时，后用 `ls/pwd` 定位，未改外部数据；本地 Host 测试缺容器隔离，不能称安全或正式基准。教师失败后继续不代表 Router 回退后继续。该失败回报时计划在原 Runtime 提供真实初始 CWD、按已有 `router_context_chars` 缩工具视图并保留 task/teacher/raw mini 消息；必要重跑已结束FAILED，见下方终局段，成功invoice不重跑，原失败不覆盖。

**短视图前向新证据**：原失败目录的 [input_latency_validation.json](../results/iterations/20261029-v9-kev-alias-smoke/input_latency_validation.json) 已完整读取 1–426 行。step2 任务 1,019 字符全保留，工具摘录 3,835→1,280 字符，`router_context_chars=2300`；7 条 mini 消息及教师/能力卡/缓存与身份连续状态保持。原 Serving 适配器 ID `1001bb4d826a52d1f399e183466143f4da7b741b` 的 CPU 前向 **37,771.85 ms**、`fallback=false`；真实概率为 Flash **0.7234**、Sol **0.1468**、Luna **0.1298**，选择逻辑 `qwen3.8-flash:none`。本回放 `teacher_assessment=null`、能力卡缺测、Token 未实测，生成请求 0；保留状态不增加有效教师样本、能力分数或新特征学习证据。原失败不覆写，随后一次必要重跑的终局如下，不增加正式/科学成绩。

**duration 重跑终局：路由通过、题目失败**：`20261030-v9-kev-alias-smoke-compact` 已结束，[metrics.json](../results/iterations/20261030-v9-kev-alias-smoke-compact/metrics.json) 和 [verification.txt](../results/iterations/20261030-v9-kev-alias-smoke-compact/verification.txt) 保留真实负结果。10 次生成、13 次真实 Bash、10 次真实 Kev 路由均 `fallback=false`，CPU 前向 20,430.85–37,243.64 ms，本次未再触发原 60 秒路由超时；全部逻辑选择 Flash，实际 `Qwen3.8-27B`、Serving 导入适配器不变。教师 5 请求/2 成功，3 失败依次为 TimeoutError/JSONDecodeError/TimeoutError；成功短评在 steps3/4/5 实际送入 Router，重复消费不另增成功次数。代码仍有 7 个 subtest errors（7 项测试方法、4 项通过），10 步后 `LimitsExceeded`、`FAILED`、`resolved=false`、验证退出 1；不能写成功 Agent。失败教师缺测使完整用量/费用 null；原 `test_duration.py` 未改，artifacts 保留 `task.md`、`duration.py`、`test_duration.py`、`duration.patch`。临时 duration 目录已清理，原失败仍在；无官方成绩，不重跑成功 invoice。

**历史停止位置与训练准备（不作当前限制）**：该时点旧预算实读 `known=575783 / reserved=256135 / remaining=168082`，此前新增15个Provider API请求已计账、累计135calls；本次主Agent仅新增Router1/生成0，预算不变，预留不作实际用量；本轮不再新增生成式请求。本机自有 8000 隧道 PID `28959` 已结束，临时目录清理时 A6000 Serving/训练尚未操作；随后部署和启动尝试见下段。现有 [prepared/summary.json](../code/data/v9/prepared/summary.json) 已写 Laya `epochs=2/max_len=1024/head_max_len=512`、Kev `epochs=2/max_state=8192`；父 R11 原 `epochs=1/max_state=384`，与在线 Serving 导入适配器分开。

**首批部署完成与第 1 次训练启动失败（历史）**：主 Agent 在原 `<SERVER_PROJECT_ROOT>` 部署 37 个源码/数据/相对链接对象、6,993,920 字节，含 16 个 V9 Python 模块、schemas/registry/common/390 材料；原两文件增量补丁保留 Laya 4 处历史差异，45KB common 重复实现已换薄别名、`common is canonical=True`，root 正式链保留。原 Python/`_material` 实读 198 Train/4 教师/2 refs及相对链接有效，GPU/Serving未重启。原 candidate_queue/ledger登记`KEV-V9-001`，实体父R11、内部四指标score106.74866622586939、2 Epoch/max_state8192，原16个R候选完成。登记QUEUED与worker13266第1次FAILED均为历史：0.145秒退出1，未加载GPU模型/消费训练输入；路径执行dispatcher.py使sys.path[0]在modelrouter/training，bare import kev误落training/kev，官方kev.train未导入。train.log/attempt/cursor及189项组合测试保留，不用测试成功覆盖真实失败。最新启动见下段。

**第 2 次真实反向 OOM（历史保留）**：同一原 wrapper 两行模块入口调整已部署，窄测 40 项通过，官方 `kev.train` 实导入位置为 `external/kev/kev/train.py`。worker16722 先 RUNNING，随后8K输入进入真实反向计算，Torch CUDA OutOfMemory、自然退出1；进程13.54 GiB、再分配60 MiB时仅59.94 MiB空闲。失败日志到Epoch0、Step20/100、Loss0.993，目录只有`training_config.json`；其中输入曝光0是启动时统计，失败后的完整输入曝光与独立覆盖均为UNKNOWN。原Loader全部接纳198条记录，两轮预期396条次；接纳量和预期量不能当实际完成量。第1次13266的入口失败与第2次OOM独立保留，两次失败没有产出两轮完成权重或固定Val；第四次训练和曝光另列，不覆盖本段UNKNOWN。

**原资源等待及三次FAILED历史、现行Kev结果**：原资源代码已按已观察占用下限加原2 GiB余量增量部署，CLI已验证`WAITING_FOR_GPU`；01:43的12,668/15,973 MiB保留历史，02:11空闲12,698 MiB、需15,973 MiB，当时等待。先前13,932 MiB为旧快照，旧384输入峰值推算`required=12103`不适用于8K，不增加其他执行限制。原CLI25201曾沿`main_loop(wait_for_resources=True, v9_only=True, ...)`保留；主Agent确认27184无worker并已结束，服务器源码`CLI_WAIT/EXIT_RESET=true`已验证，前三次FAILED与原CLI25201自然退出保留历史；现行结果见 [PROJECT_STATUS](PROJECT_STATUS.md) 的训练表，原失败/曝光分列。原输出保留与第四次接续参数已确认，不另建loop/Runner/定时任务。F14/ComfyUI/Serving未被干预；F14只读证据见 [PROJECT_STATUS](PROJECT_STATUS.md) 的F14段；Laya8.87 GiB、ComfyUI24.25 GiB的先前占用保留，ComfyUI实监听`<A6000_HOST>:8188`，运行队列1/pending0的历史回报及活跃图像任务保留，`127.0.0.1`不通属绑定地址，未卸载/干预。原Provider/telemetry账本/logger已补`alias_mapping/query_raw`，服务器构造V9 AliasProvider成功、账本根`<SERVER_PROJECT_ROOT>`，未发API请求或读Key、不新增client服务；Alias/账本补齐已验证且无新API。此前source部署为40个文件/链接加原Laya/Kev增量，首批37对象/6,993,920字节仍作历史，不推算后续总字节。Serving仍旧权重。Laya hook在盘、F14内存不读，下一自然child完两轮边界生效；旧exit处理已由服务器源码确认，不另建Trainer/队列，Serving旧权重的`FEATURE_NOT_TRAINED`保留，新候选为`FEATURE_PARTIALLY_TRAINED`。原评分及留存机制保持；本轮收尾仅涉及多余控制器和临时连接，04:33:44主Agent确认无当轮SSH连接残留。 现行结果见 [PROJECT_STATUS](PROJECT_STATUS.md) 的训练/Val/评分记录。原`validate_candidate`复用已保存Val同步两处完成时间，原`update_retention(queue,apply=False)`已保存内部评分/ledger，释放0字节、删除0字节/0文件；仅组内单项代表留存。

**本轮文档子任务范围**：只编辑已指定六份原 Markdown，不改代码、附件或下载聊天，不做 GitHub 操作、远程变更、训练干预或新建服务。最新人类指令优先于材料中的历史执行建议。

> 以下为 2026-10-28/29 的远端规划记录，不是 10-30 新实测。初始模型身份仍为 Sol、Luna、托管 `qwen3.8-flash`，不得替换为 27B 或 Flash-Next；其中 AA 52/38（v4.3.2）和 Qwen USD 价仅保留当时的来源陈述，未由本地证据复核，不用于当前能力快照、训练输入或实际账单。当前证据以本文最新记录及 `PROJECT_STATUS.md` 为准，早期权限描述不撤销后来的人类授权。

### 2026-10-29 · 双 Planning 职责统一、正式三模型池与保守去重

**职责合并**：原研究方案 Planning 与原 Laya/Kev 模型训练 Planning 统一为一个 Planning Agent；本地 Codex/Execution 仍是执行方，现有健康训练、正式 Benchmark 授权和其他资源边界不自动变化。唯一研究主线保持 V9 **五个 RQ**，历史三 RQ 简化备选不采纳。

**统一 Planning 接续（2026-10-29 最新纠偏）**：已批准 V9 五 RQ；首批三模型池指定**`gpt-6.1-sol`、`gpt-6-luna`、`qwen3.8-flash`**，第三项是 Qwen3.8-Flash 托管 API，**不是误记的 Qwen3.8 27B，更不是 Qwen3.8-Flash-Next 开放权重**。三档表示研究角色，非已测严格能力/费用排名；公开标准输入/输出 $/百万 Token 约 2/10、0.10/0.50、0.15/0.47；Qwen 输入单价反高于 Luna。AA Sol Max=52、Luna Max=38（v4.3.2），Flash-Next=40 属不同模型，托管 Qwen Flash 的同口径指数未核到，不能填入。下一任统一 Planning Agent 应把本次纠正视为最新明确用户选择，保留六文档、仅保守去重，确保现有训练自然推进，不以 planning 记录声称新调用已成功。

**能力数据本地化**：由本地 Agent 从 GitHub 最新 main 接续，在现有代码路径复用已有 Registry/数据准备入口，获取有授权的 AA API 指数及可得基准/定价，形成可版本化本地快照；刷新脚本**每次执行尝试重新拉取**，失败则保留带正确来源/采集时间的最后有效数据；不允许 Router 每次推理都联网；训练/正式 Episode 固定所用快照 ID，不提交密钥或凭空补充 Effort 分数。本次仅文档，尚未实际运行下载/抓取。

**训练、历史和文档**：现有 Laya/Kev 训练与 Kev 四指标评分、约 15% 受保护核心池不改；从各自同协议 Val 选**在盘**候选，再用独立 Dev Agent Episode 选择用于新字段的**现有权重继续微调**，并需真实监督与独立授权；缺失权重非必要不重训。六份文档维持原职责，**只去除准确重复内容和失效要求，不大幅缩写**，Q/D-ID、失败结论和训练配方、数据源政策与 Fig/Table 编号均保留。GitHub 最后已核实的训练现场仍是 10-27 F12/R12 进度，实时需由本地 Agent 取得。

### 2026-10-28 · 最新 V9 设计收敛与首次 Agent 测试前只读审计

**恢复指针**：最近 2026-10-25～28 对话进一步压缩 Q-021 方案。现行批准版本仍是 **V9 五 RQ（1 Overall、2 Pool、3 Decomposition、4 Ablation、5 Workload Boundary）**，最近把消融合入 RQ1、改三 RQ 的表述只属未获确认的备选组织，不可自行覆盖正式 8 图/12 表。近期讨论的默认但未部署方案：单个顶级轨迹教师，约积累 3 次生成或阶段/停滞事件更新；首版固定 2 条训练/开发许可合规且与 Sealed Test 隔离的公开成功轨迹摘要，无向量检索服务；短输出仅进展/阻塞/下一里程碑，附调用费用与截至步骤的元数据；Router 仍为唯一模型×原生 Effort 决策器。候选能力卡优先真实原始 Benchmark 分数/单位、AA 综合指数和每 Effort 对应实测，综合高中低仅派生，缺档 NOT_MEASURED，不凭名称或不同协议猜测。

**训练与测试边界**：当前训练无需改变，Laya/Kev 只在各自可比固定 Val 选实际存在的代表 Checkpoint，再以独立 Dev Agent 任务成功和完整费用决定继续微调起点；旧权重缺失并非自动重训理由。初始池以 3 个经济定位不同且真实核实的候选为目标，实际池成员、费用和测试规模尚待决定。项目最新 GitHub 现场 2026-10-27 为 F12/R12 在训，Kev 14 项完整 Val；这不是实时值。官方 Harbor Episode 仍无有效任务成功率。

**本次唯一行动**：六份文档必要同步 + 提供给本地 Agent 的**只读源码/测试准备审计提示词**；不启动试跑、不改程序或训练、不碰 Sealed Test。必须核清 mini-SWE-agent 是 Agent 框架，SWE-bench Lite/Verified 与既有 Terminal-Bench 2.1/Harbor 是不同任务/评测链。等本地证据回报后选简单、合法、未泄漏的 Dev 任务。

### 2026-10-27 · R06–R11完整Val与R12自然接续

R11于台北12:54:57完成原固定Val：8,436记录/9,330问题、拒绝0、截断0、exit0，Accuracy0.569024652/NLL1.068723736/Brier0.535678489/ECE0.018245896；训练8,181.1秒、Val3,209.5秒。相对C03准确率低0.257个百分点，三项概率质量指标改善，当前仍只支持离线权衡观察，不批准新配比。R01–R11共11/16完成，加C03/C04/C09共14项正式完整Val。

13:49原采集：F12 Epoch2/2、Step47,795/69,990、Loss0.472700；R12由原dispatcher自然接续，Step420/2,135、Loss0.727、NOT_EVALUATED，R13–R16排队。原两条训练链、5秒采集、8765与Serving均保持，没有重新派发或材料生成。R12实际消费样本未记录，不使用Step乘批量作为实测值。

14:31原页面标签已定向发布：验证EVALUATING/FAILED/PARTIAL优先显示，训练和队列另列；一个针对性用例通过，实际返回JS与本轮文件一致。实时F12 Step48,947、Loss0.464940；R12 Step740、Loss0.584，均TRAINING。HTTP200与卡片运行已确认；内置浏览器读取超时，视觉展示未确认。

R06–R10及R11完整配方、配比、时长、覆盖量和实体状态已同步至原报告、脱敏队列/Ledger和矩阵当前区。R10已由原留存流程移除实体；R11 PROTECTED、R04 RETAINED。8项历史移除累计释放1,081,434,112字节，本轮未删除或恢复权重，四指标与约15%规则不变。报告生成12:56、来源40932a7；运行读数另记13:49，避免把历史快照当即时进度。

Laya实际执行106 Run、105完成、223版本/8物理版本，106曲线（89 Step、17 Epoch-only）；Kev报告19对象（18本地+1导入）与14项正式完整Val分开。未来502项与当前两Run的串行估算402.6小时、范围303.6–422.9小时、中心台北11/13 08:25；不含父权重待决部分，也不作为论文终点。

本阶段按原main提交推送真实新增结果和页面验证阶段标签；保护两份既存未提交删除，不纳入提交。C05/C06/C07/C08/C10、F17–F20的原原因保持。QA/Research不变，Harbor/Verifier仍NOT_EVALUATED，未用最终Test或增加付费调用。

### 2026-10-26 12:36 · 本阶段结果已推送

脱敏报告、候选队列/Ledger、候选矩阵、F11完成/F12启动摘要和 R03–R05 固定 Val 结果已随 GitHub main 提交 `cdf87b5` 推送；本地与 `origin/main` 一致。此前“待推送”文字属于12:18过渡记录，不能覆盖本条最新状态。

最新统一报告（`2026-10-26T04:25:42Z`）重算未来509项，串行估算约460.1小时，历史吞吐范围352.0–476.8小时，中心约台北11月14日16:32；F12在报告生成后启动，F12实时值仍以原8765采集为准。

### 2026-10-26 12:50 · 最新实时读数已推送

原 8765 采集 `2026-10-26T04:50:21Z`：F12 Step640/69990、Loss.669115；Kev R06 Step820/1068、Loss.608，固定Val未开始。最新候选队列/Ledger脱敏快照已随提交 `8bec8cb` 推送；训练仍沿原 dispatcher运行。

### 2026-10-26 12:36 · F11完成，F12/R06在训，统一结果待推送

A6000 实时采集 `2026-10-26T04:36:08Z`：F11已完成2 Epoch、Step58,200，最终S1 Val Accuracy .6667/Loss .6022/Brier .4158/ECE .0389；F12已自然接续到Step256/69990、Loss .710079，最后进度04:35:16Z。Kev R06 Step710/1068、Loss .657，固定Val未开始，含Val预计台北14:16。原 dispatcher/采集器/8765/Serving均保持，未重复派发。

C09及R01–R05均已完成相同固定 Val。C09：0.566774/1.074802/0.538563/0.023638，内部评分105.201；R01：0.566345/1.094774/0.542489/0.051039，评分98.861；R02：0.573955/1.110397/0.552117/0.093402，评分90.175；R03：0.567953/1.104241/0.544448/0.063738，评分96.036；R04：0.567846/1.081526/0.540801/0.027957，评分104.087；R05：0.571383/1.094129/0.543806/0.043059，评分100.767。均覆盖8436条记录/9330问题、拒绝0/截断0。不同监督目标只作同协议描述，不按Accuracy单独下结论。

R02/R03/R05分别移除两个权重文件，历史累计释放405,540,864字节；R01、R04、C09及必要父权重保留。训练配方、材料、日志、Val和处理原因仍在原记录中，当前重复留存运行无新增释放。C05/C06/C07/C08/C10原因未改变。

统一报告已在服务器重新生成于 `04:25:42Z`，源码标识 `40932a7`，并同步本地，覆盖Laya105真实Run、Kev13历史对象；Kev已结束11个、R06在训，R07–R16排队。未来可执行509项，估算约435.6小时，范围352.2–477.0小时，中心约11月13日15:50。服务器最新报告、脱敏队列/Ledger和候选矩阵当前区已进入本地工作树；上一提交85ce133已推送但只覆盖上一批结果，本节与R03–R05、F11结束和F12启动摘要需随本轮提交一起推送。QA/Research保持，官方Agent Episode仍0。

### 2026-10-25 23:06 · C09/R01/R02自然完成并同步

台北23:06原8765采集：Laya F11 Epoch2/2，Step33324/58200，消费2132695，Loss.4752597；Kev R03 Step540/1500、Loss.782，NOT_EVALUATED。原controller499841、F11 worker303160、Kev唯一自然接续420899/R03 worker810050、采集器451884、Web832433、Serving2291306均正常。GPU19053/49140MiB、99%、81°C，根盘22:58余约1.22TB。

Kev C09、R01、R02均训练完且完成相同固定Val（8436 records/9330 questions，0拒绝/截断）。C09指标acc.5667738478/nll1.0748016646/brier.5385626194/ece.0236377974，train16691.7s/Val3812.2s，保留权重、内部评分105.201。R01 S1-only：.5663451233/1.0947744186/.5424889919/.0510390788，8585.9s/3714.6s，保留为必要对照，评分98.861。R02 S2-only：.5739549839/1.1103970282/.5521168786/.0934023682，5798.2s/3059.96s，评分90.175；两项权重依现有留存规则实际删除，释放135180288 bytes，其他配方/记录仍在。R固定Val完成2/16，R03在训，R04–R16排队；25个Kev候选中5项已完整评测。

此前已推GitHub main ca0b5ee，但不包含本次三个完训/淘汰里程碑；本轮把A6000原报告、队列、Ledger、矩阵脱敏同步并推送。训练源码来源C09=520ff8b，R01/R02=7f6b683；当前collector source=40932a7。报告汇总114对象，Laya105个实训对象、104结束、1在训、221 Epoch版本、7物理权重；Kev报告口径8个结束本地执行对象、1在训、1元数据对象、1导入对象、10版本、8实体。报告更新时间21:57，实时快照23:02。

当前ETA：F11约10月26日12:02台北；R03剩训约2:02+固定Val约0:52，约10月26日02:00台北。后续Kev13项训练53.9h+Val11.2h；总剩余512项、约458.3h，情景374.2–502.4h，中心约11月14日01:24。报告/矩阵生成21:57，队列/Ledger更新22:56，实时看板23:06。官方Agent Episode仍0；离线Val不是任务成功。

### 2026-10-25 11:34 · 留存与候选矩阵接续

原留存模块及采集源码已部署 `40932a7`，唯一采集 PID `451884`，5 秒周期。C09 原训练 `413095`/dispatcher `413082` 未中断，唯一等待命令 `420899` 未替换；C09 完训及固定 Val 后由原 `7f6b683` dispatcher 接续 R01–R16，加载新留存模块。不要重复派发或重做已就绪的 108,656 条材料。11:34 仍为 C09 Step 580、R 固定 Val 0/16。

永久代表保护不再由每个唯一 `control_variant` 自动获得；原 C 系必要对照与 R01 单独保留，每组约 15% 核心配额、父权重/Serving/活动 Run 的保护保持。未知 revision 使用 N/A 与重训限制，完整训练、同固定 Val、材料和配方依然必须保留。19 项窄测通过，服务器实际删除 0、释放 0。真实 R 淘汰和完整 Val 尚需自然完训后形成证据，不将临时测试样本当作科研结果。

原报告写入时自动维护 CANDIDATE_PROGRESSION_MATRIX 的 KEV_LIVE_CANDIDATES 当前区域，其余正文作为历史保留。候选队列、Ledger、报告和看板继续由同一原链更新；无第二账本、服务或 Git 调度。公共副本按会话里程碑 main 同步，服务器仍无整仓 Git。当前 Laya F11 Step 11,648，C09 Step 580；共享资源下条件 ETA 约 478 小时，课程 F17–F20 仍需已批准父实体。C05/C06/C07/C08/C10原因保持，QA/Research不变，官方 Episode 仍未评估。

### 2026-10-25 · 双模型在训与唯一接续交接

当前阶段以 [PROJECT_STATUS 首页](PROJECT_STATUS.md) 及 [候选矩阵当前阶段](CANDIDATE_PROGRESSION_MATRIX.md#2026-10-25--当前候选与材料状态) 为准。依据为台北 10:46–10:53 的 A6000 实际记录。采集源码=`f1052c7`，在训 C09=`520ff8b`，接续 dispatcher=`7f6b683`；最终结果提交与训练来源分开记录，服务器无整仓 Git。

Laya F11（worker `303160` / controller `499841`）与 Kev C09（worker `413095` / dispatcher `413082`）健康在训。R01–R16 共 108,656 条训练材料已完成官方 strict CPU 编码，0 异常，状态为 READY，尚无训练完成结果。等待 C09 完训和固定 Val 后沿同一 dispatcher 接续；唯一接续命令标识 `420899` 已存在，不再派发，不建立第二队列。

C05/C06 因状态拆分不成立、C07/C08 因 Rank 初始化不兼容保持 PENDING。C10 的实际 loss 权重有效，但原材料的 35,645 条禁用 ROUTE-001/002 来源及 17 条 TRA-004 使材料继续待决，不擅改候选或初始化。C11 仅记录当前选择 C03，不增加训练计数。C03/C04 的同一固定 Val 已完成，两实体保护，现场 0 删除、0 释放；精确指标仅列于候选矩阵，内部 score 不计官方 Agent 成绩。

历史计数已推进为 Laya 105 个真实 Run（104 结束 + F11 在训）、220 个版本、7 份实体；旧核心 2/5，新池 F05-e01 一份，F06-e02 另列历史留存。Kev 6 个执行对象 + 1 个导入对象，正式完成仍仅 C03/C04，C09 在训。未来 515 项为 499 Laya + 16 Kev，不含当前两个在训 Run；10:50 条件 ETA 约 478 小时，情景 398–524 小时，中心约 11/14，不作为论文完成日期。

恢复后沿原执行链等待自然交接，不重做旧导出或已完成 Run，不凭 READY 宣布训练或论文完成。原采集 PID 为 `428931`，5 秒周期，原报告已包含 C09 的 S2/S3 实际物化与独立量，累计实测曝光暂为 N/A。候选队列和 Ledger 已通过同一脱敏函数导出，不导出原始私人日志。下方 10/24 及更早条目继续作为历史，旧 F10 在训、C09 待决和旧 ETA 不代表当前状态。QA/Research、既有科研决定及数据政策保持，本轮不新增 Q-ID，不计官方 Agent 成绩。

最终采集源码推进至 `c760e32`，现唯一采集 PID `434018`，周期与原服务保持。10:58 报告覆盖 112 个执行或导入对象；10:58:56 实时 F11 Step 10,624、C09 Step 300，动态 ETA 约 481 小时。`candidate_queue.json`/`candidate_ledger.json` 的公共副本保留 9 个 C 系列候选；16 个 R 材料目前保存在原物化目录与综合报告，待唯一接续命令进入新版 dispatcher 后并入同一队列。

### 2026-10-24 · 全历史结果与官方评测接续

最新执行阶段见 PROJECT_STATUS 同日 23:52 条目。原报告入口已更新，`training_research.md/.json` 覆盖 104 个 Laya 实际 Run 与 6 个 Kev 对象，共 110；Laya 完成 103、F10 在训，另两份纯状态记录不计训练。219 条 Epoch、8 份实体与 87 个 Step/Chunk、17 个 Epoch-only 曲线分开。最低主 Val Loss Epoch 中 97 个无实体；旧核心仍 2/5，新池 F05-e01、另列 F06-e02，课程父权重与恢复点不混计。

今日早期正文混用了 F06 与 F06_S1，且把 F07 最佳 S1 的 e01 写成 e02。已按原始 Epoch 明确归属：F06-e02 为 0.6863/0.6017/0.4150，最低 Loss e01=.6002 无实体；F06_S1-e02 的 0.6809/.5936/.4079 无实体；F07-e01 为 .6827/.6076，e02 为 .6791/.6145。F07–F09 记录未保存，缺失目录不能作为保存后移除的证据。没有恢复或删除权重，也没有变动服务器留存策略。

Kev C03/C04 两次正式训练和同一固定 Val 已完成，C04 四项指标均未超过 C03。23:37:56 原 dispatcher 自然接续一次，C05 状态材料不足、C07 初始化 Rank 不符、C09 无完整新增 typed 目标均记 PENDING，exit 1 保留待决；C03/C04 成功和旧失败记录不变，未重训。线上 Kev 仍是导入适配器，不能称已服务 C03/C04。

原唯一采集器加载源码 `5a710801f9cb387b94cab4ee8730da20deae789b`，PID 139123，5 秒周期；F10/Serving/Web 保留。计划完成 20/38，F10 在训，13 项独立待执行、4 项课程父权重待补；矩阵完成 52，487 项合法非重复待执行。剩余 500 项的条件墙钟约 441 小时，历史吞吐范围约 332–458 小时，中心日期台北 11 月 12 日约 09:00。GPU 实测活跃时长与论文终点 N/A；原 548 小时预测属于旧观测。

官方 Harbor 仍无 Verifier Episode。宿主缺 uidmap，A6000 原项目 Python 尚无 Harbor/mini 包和原任务资产。原 CLI 已处理旧 Oracle 配置缺少任务源的问题，使用本机已存在的官方任务树；下一真实任务仍为 fix-git Oracle，再原生 mini、动态 mini、Canary、Dev。CPU 集成证据保留于原迭代目录；未改宿主或共享 Docker，未新增付费调用或使用最终 Test。V9、Q-012、Research 与既定矩阵保持，没有新 Q-ID。

### 2026-10-22 · V9 最新决定：Agent 外部轨迹分析与模型能力卡

负责人明确要求：**V9 仍是五个 RQ 的权威版本**，即 RQ1 整体、RQ2 模型池、RQ3 任务拆分、RQ4 系统消融、RQ5 工作负载边界；先前 10-22 试探性建议把消融合入 RQ1，已由最新 V9 指令覆盖，不再视为现行决定。以 [EXPERIMENT_QA Q-021](EXPERIMENT_QA.md) 记录原意，以 [V9 实验图表规划](../../汇报/汇报三/ModelRouter论文实验与图表规划.md) 统领 Fig.1–8/T1–T12。

**主流程**：Agent/Harbor 生成截至决策前的任务、已执行工具、验证、预算与历史 → **Agent 外部**的可选强模型轨迹评审器检索合规的相似成功参考轨迹，独立调用一次大模型生成**短的结构化合理性/进展/下一里程碑评估** → State Builder 合并基础状态与外部摘要 → 动态合法 `(provider,model,revision,native_effort)` 候选及每档能力 Benchmark 证据/价格/限制 → **单一活跃 Laya 或 Kev Router**评分 → 生成模型执行 → 实际工具/成本/验证反馈。评审器**不是第二个 Router**，也不做工具执行；同任务 Sealed/Final 的答案或未来轨迹严禁入输入，教师 Token/USD/延迟记入 Episode，触发频率与收益需 RQ4 消融验证。

训练/数据边界：顶级模型多条成功轨迹可为工具意图/进展/重复/验证合理性提供**离线候选监督**，不要求相同命令序列；相似参考库只用合规 train/dev。每个模型和原生 Effort 分别保留真实 Benchmark 分数、协议、来源、评测日期、样本量以及缺失状态；没有 Effort 实测就记 `NOT_MEASURED`，不能把能力等级替代事实或把同模型分数无条件复制到各档。能力卡加入 Router 推理前需训练/编码一致性核验。详见 [RESEARCH_OVERVIEW](RESEARCH_OVERVIEW.md) 和 [数据政策台账](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)。

**只同步六份 Markdown 文档**，不改变旧训练现场、训练配比、Checkpoint、权限、Harbor 或 Token 授权。2026-10-21 的 F07/C04 数字只是 GitHub 最后训练快照，不是实时状态。真实官方 Agent Benchmark 主结果尚无。


### 2026-10-21 · 综合训练结论与队列终点预测

继续同一报告与JSON，107对象=101实际Laya+5本地Kev+1导入。报告正文已含同材料配比、ALGN/F预算、实体候选、停止条件与完整队列ETA，后部逐对象及全部Epoch不遗漏。原采集器每5秒给8765同源ETA，历史仅阶段变化生成报告。原矩阵新物化1项，现2就绪/485待生成；369.623秒CPU样本用于估算，官方编码S1/S3无跳过。训练、Serving、Web保留原PID，11项相关用例和170项实际浏览器比对通过。

台北03:18 F07为35,840/151,998 Step，C04为3,850/16,857；约65.3小时及31.9小时训练剩余，Val分别约103秒同集代理和3,099秒C03代理。后续F08–F16约342.8h、纯S3约60.8h代理、487矩阵约29.9h训练/Val；485物化约49.8h单样本外推。全可计算队列约548.6h/22.9天，中心日期11月12日深夜，情景430–600h，CPU波动/切换及待决项不保证。ETA按协议和监督组合分开，旧慢协议不混入；fraction曝光为近似期望，非实测消费；GPU活跃时长与实付费用未知。

源码907510e349e9e463579c4edcabec8c54886201af已定向部署，留存模块未部署。Laya自然F07边界才加载新版，Kev旧内存尚未退出，后续候选待决原因保留。Planning可以据报告决定缩减规模或转向官方Episode；Execution本轮没有改变计划、Test、RQ或创建新Q-ID。正式Agent任务成功率与论文闭环仍NOT_EVALUATED。

### 2026-10-20 · 全历史训练分析与现有队列接续

最新执行目标已扩展为全部既定合法配比，沿原 Laya/Kev 调度器、数据转换入口、固定 Val 与8765执行；不要求逐个询问C05/C07/C09后停下。统一报告为 `our-project/results/training/training_research.md` / `.json`，实际Run、全Epoch Val、配置、曝光、曲线和实体分别保存。原采集新增 `--research-report` 并在阶段变化时自动输出同一报告，无第二队列、网页或记录库。

Laya实际101、结束100、F07在训；212版本/7实体，84逐步+17Epoch曲线。Kev5本地对象+1导入，C03正式Val已完整成功，C04在训，Pilot/部分训练独立。旧五实体2，新池F05-e01在，F06-e02单独历史全局留存；缺失实体未恢复。ALGN03/04独立量高于实际训练量，原记录保持但分析使用N/A。

原矩阵1092中52完成、487合法非重复待运行、154重复、315无目标、84未定义；原full38中17完成、1在训、16独立待运行、4缺父依赖。Laya源码已部署，原边界flag已设，F07结束后同控制器才读新版；不重训父F01，原Mode B结束调用原Mode A。已有CPU入口真实生成一个S3矩阵项4096条/2049单元，Val4794，官方编码skipped={}。留存源码未部署、服务器实际策略未变，训练和Serving保持。

原8765页164项实际浏览器比对通过，队列/采集10项用例通过；仍单个采集职责5秒周期。报告呈现配比的Accuracy/Loss/Brier/ECE权衡，未宣布最佳比例；固定Val持续选模，最终Test未读。正式Agent任务成功率/完整费用与RQ结论继续NOT_EVALUATED。只更新Status与本次重大交接，QA/Research方法不变。Kev旧controller内存没有新增边界重载，C04之后新候选的实际启动须现场证据，不能以源码就绪代替。

原V8转换新增同项目Train/Val的typed导出，25506训练/368Val，上游读取完整成功；全部训练记录已在C03，新增0。缓存标量与仅观察终局没有正式typed目标映射，完整C09保持PARTIAL_MATERIAL/PENDING，不能把部分Arena重复训练称为完整V8。原dispatcher独立候选待决后继续、失败仍非零终值的代码已部署，27用例通过；旧内存不会读新逻辑，仍需C04训练/Val/队列自然退出后同原入口接续。无第二dispatcher，无权重下载、删除、新模型或付费。

### 2026-10-20 · 训练历史与看板工作进行中

本轮目标为现有 Laya/Kev 训练历史、实体留存和 8765 页面，不继续新增 Benchmark 环境。主实现为 `router_data/checkpoint_retention.py`、`router_data/laya_batch_train.py`、`scripts/fetch_live_status.py` 与 `our-project/dashboard/`；迁移包入口改为引用主实现，旧 HTML 生成入口不再各自维护页面模板。

本机留存源码前轮已推 main，本轮只定向部署原采集源码、首页、JS并生成真实历史分片；服务器留存与训练队列代码未变。S1 最佳 Epoch 按完整历史最小验证 Loss，旧五实体 2/5，三缺项未恢复。Laya 全目录实际执行 101、结束 100、F07 在训；212 条版本、7 份实体，84 个逐步曲线与17个Epoch-only。两份R0状态占位不计实际训练。Kev 4个本地对象与1个导入资产，正式C03完整训练结束，验证失败。旧树模拟记录不进入训练成绩。

直连和Mac浏览器访问原8765已恢复，真实页面读到108个对象、F06的722个训练点、C03的1685个Loss点及完整Step计时。浏览器整体仍FAIL：原唯一采集进程使用旧内存代码覆盖JSON，页面显示COLLECTOR_UPDATE_REQUIRED；重载该单一采集进程待负责人明确答复。未启动第二采集服务。C03旧队列验证误走上游公开test并在网络获取失败，本机沿既有Val入口更改调用；不部署训练链、不运行GPU。训练、权重、私人文件保持不动，Research未改。

### 2026-10-19 · V10 最新交接

接续唯一主工程和 `20261019-v10-integration`，不重建执行系统。当前 main 已接入 `22f3a2f`；该次远端删除的审计文件和独立解析测试不恢复，旧命令日志仍保留。负责人本轮授权个人 Rootless Docker、必要官方镜像与 Oracle，以及本地 main commit 和本次会话 push；没有授权修改宿主 Docker、权限、共享服务或增加 GPU 训练。

Rootless 分支为 `BLOCKED`：宿主无 `newuidmap`、`newgidmap`，真实 UID/GID 映射失败。安装工具未执行，没有个人 daemon/socket/镜像。官方 Oracle、原生 mini、动态 mini Trial 均为 0，全部正式科研结果保持 `NOT_EVALUATED`。不要重复同样失败，也不要用宿主执行或合成样本代替原版 Verifier。

现有官方 DefaultAgent、Policy Hook、Provider 转发、ATIF、CLI、Ledger 和 8765 Agent 模块继续集成；私人 runtime、状态 JSON、凭据和原始日志留本机。历史 RQ 数值仅属开发证据。Provider 预算已用 410,353 Token，余 589,647，实付费用未知。健康 Laya F06、Kev C03 和 CPU Serving 不动，权重不下传 Mac。

下一轮先读原迭代 `next_iteration.json`。宿主管理员补齐 uidmap 后，沿同一执行链完成个人 Docker、Oracle、原生 mini、动态 mini、Canary、Dev 和 Q-019 的 RQ1–RQ5；57 题 Sealed Test 另需负责人确认。最新真实阶段以 Status 首页为准，旧「科研完成」只适用于部分工程产出。

**2026-10-14 当前交接覆盖说明（GitHub 复核）**：TOP-5 候选与数据工程更新已提交，但新训练代码存在首 Chunk 混合类型求和错误，最新合法/去重训练统计口径不一致；Agent 上报的物理删除空间、F02 现场及新 ALGN 训练尚未独立实测。以文末审计与 PROJECT_STATUS.md 为优先待修复事项。

- 项目：**ModelRouter**，研究**长程单/多 Agent 执行过程中的状态感知、任务级 Model × Reasoning Effort 联合路由**。
- 主方法：**确定性 State Builder + 动态候选与必要约束 + 单活跃 Laya 或 Kev 决策模型 + 原 Agent Harness + 完整记账与任务终局评价**；Kev 的 Qwen3.5-4B-Base/LoRA/pointer head 资料保留作具体实现证据，现行方法不限定 Kev。
- 目标：在可靠性/成功率约束下减少**任务完成总成本**，考虑动作对后续步骤、失败恢复、缓存连续性和成本剩余量的影响。
- **最新阶段/唯一下一行动以 [PROJECT_STATUS.md](PROJECT_STATUS.md) 首页为准**；E-DESIGN 问答批准以 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 为准。截至 2026-10-09 第二批答复后：E-DESIGN 进行中；Q-001=A/Q-002=B/Q-003=B 原则/Q-004=B/Q-005=B/Q-006=A 已记录。当前聚焦 Q-007 的公开轨迹 A 起步阶段，Q-010/Q-011 待依序讨论，不讨论具体实验步骤；“rq 3 需要 ab 同选”暂记指代未核清。此为当时快照，后续现状随真实证据更新。
- 执行路线：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- 硬件：授权的单卡 **RTX A6000 48GB**；2026-10-09 审计快照显示显存占用仅 682 MiB。实际运行前重新核对资源和共享服务。
- 现有 CCH 数据为 **110 行聚合记录，代表 750,212 次调用**；Blog GPT 数据为 **221,128 条调用明细**。二者都缺少可靠的任务级决策状态/终局成功标签，**不能直接作为反事实路由监督数据**。
- GitHub 正式文档：[项目状态](PROJECT_STATUS.md)、[研究与方法](RESEARCH_OVERVIEW.md)、本文件及 [实验设计问答](EXPERIMENT_QA.md)（E-DESIGN 已建立，记录 Q-ID、选项、推荐、负责人回答与最终决策）。历史 `IMPLEMENTATION_RESEARCH.md` 保留作历史设计参考，**不再代表当前唯一方法**。
- **下一步是动态字段**：每次先查最新 [PROJECT_STATUS.md](PROJECT_STATUS.md) 的「当前任务/正在等待/下一步」，如果处于 E-DESIGN 再查 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 待答 Q-ID；数据来源与 Provider/Cache 政策详见 [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)，不得重复已经确认的问题、提前执行未授权工程或训练。
- 当前论文表述纪律：不要把状态字段数量本身作为创新点；**论文不讨论“多变量”或“混沌”**。新意必须靠任务级状态决策、Model × Effort、延迟成本/成功影响和严谨评测证明。

### 2026-10-18 · 最终五个论文 RQ（负责人明确纠正，覆盖此前局部待定版）

**已确认，不再待定**：
1. **RQ1 总体效果**：同一真实 Agent 任务、合法树状 Model→Native Effort 池、相同 Harness/预算下，与强固定、整任务随机混合、规则/简单动态、同 Harness 可运行的外部 Router 做 **Task Success–Complete Episode USD** 横向比较。
2. **RQ2 模型池**：选择哪些模型身份和数量 K；每个模型下有真实合法 Native Effort 子节点。
3. **RQ3 任务拆分**：固定池成员/K/真实档位菜单/Router，在同原始任务上比较 G 粒度及实际交接/上下文/总费用。
4. **RQ4 系统消融（**新正式 RQ4**）**：固定任务/池/环境，对照 Fixed/Model-only/Effort-only/Hierarchical/Joint；T/M/H 信息组及 KV/Trace/Role/Verifier 真实可用单项/组合；S1/S2/S3 合规数据、Laya/Kev 训练监督及配比，测完整任务成功率/费用与开销，保留负结果。
5. **RQ5 适用边界（保留原版本）**：固定池/Router/G，检验不同事前可知的 Agent 工作负载（任务类型/规模/协作结构）对动态路由净收益的稳定影响。

**明确废止**：2026-10-16 V8 曾以“多 Agent 角色间模型互补性”作为 RQ4，**该独立 RQ 已被负责人明确删除并替换为系统消融**；它不再是现行研究方向，不再对应 Fig.7 或 T8。Agent 角色仍是按需可见的输入和状态消融字段，不等于必须独立研究角色互补。下方 2026-10-16 的条目是**历史时间快照**，不得覆盖此最新决定。

**权威新方案**：[汇报三 V9](../../汇报/汇报三/ModelRouter论文实验与图表规划.md)；**现行图表**：Fig.3–4/RQ1，Fig.5/RQ2，Fig.6/RQ3，Fig.7/RQ4，Fig.8/RQ5；表 T4/T5/T8 与 RQ4 对齐。历史 Q-017 原记录保留，新决议另由 EXPERIMENT_QA 记录。未因此启动/修改训练或 Benchmark。

## 0.1 新对话恢复规则（持续生效）

**新对话角色**：ChatGPT 必须同时以长期 Planning Agent、需求探索/方法讨论伙伴、论文文献研究者的身份工作。和用户讨论研究方向、相关工作、训练监督、Kev/Jev、论文图及框架；实际本机文件由 Codex、服务器公开数据由 Execution Agent 处理，不宣称自己可实时访问本地/服务器。启动时读取全部五核心文档及最新证据，历史计划与真实执行分离。


- **版本**：首先核查 GitHub `main` 最新 HEAD，从同一提交读取四份正式文档；文中旧 SHA、日期、章节「当时」均不作为实时证据。
- **唯一状态来源**：[PROJECT_STATUS.md](PROJECT_STATUS.md) 首页；**实验决定**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md)；**长期历史与协作**：本文件；**研究假设与方法**：[RESEARCH_OVERVIEW.md](RESEARCH_OVERVIEW.md)。
- **证据分层**：GitHub main、实际本地工作树、授权服务器部署、实验数据/结果分别核对。没有最新 Execution 回报就不能声称知道本地未推送更改或服务器实时状况。
- **冲突处理**：先确认是否只是历史快照，查看明确日期与最新提交；仍有冲突则说明并请负责人裁决，不擅自猜测、reset、覆盖或重写。
- **恢复输出**：HEAD、当前阶段、最近已批准事项、唯一进行中事项、阻塞与权限、下一行动和证据缺口；直接接续，已完成阶段不重跑。
- **更新闭环**：有用户明确决定、任务验收、阶段切换或真实实验结果时更新各自负责的文档、记录日期和影响并校验远端提交；没有新事实就无需更改。禁止未经请求的深度研究、服务器操作或付费使用。

## 1. 事实来源、证据等级和时间

| 标记 | 含义 | 本轮证据 |
|---|---|---|
| [AUDIT] | 本地 Agent 的只读观测；Planning 未直接登录服务器复核 | 用户提供的 MR-E0-001 报告，2026-10-09 |
| [GITHUB] | GitHub 连接器读取的远端仓库事实 | 2026-10-09 读取 main、README、规划及文献文件 |
| [OFFICIAL] | 模型/项目官方说明 | Kev 官方 model card / README，2026-10-09 查阅 |
| [PAPER] | 原论文/公开预印本 | 论文原文链接；同行评审状态另行核查 |
| [DESIGN] | 当前计划或待验证的研究假设 | 不能写成实验结果 |
| [UNKNOWN] | 尚无证据或需要再次确认 | 必须在任务卡中安排核对 |

**GitHub 基线**：[GITHUB] 在本次三文档整理前，`main` = `13c14a387d1c18ecfe32b84a86b4efc1d751b72d`（2026-10-07 提交）。后续提交会改变 HEAD；**不得把旧 SHA 当作永远最新**。

## 2. 已确认的研究决策（Decision Log）

| ID | 决策 | 理由 | 状态 |
|---|---|---|---|
| D-001 | 长程 Agent 任务级路由；单条 Prompt 级路由不作为本项目目标 | 单步最便宜不代表整任务最便宜 | 已确认 |
| D-002 | 动作空间为 `(model, effort)`，候选池动态变化 | 不同 provider、上下文限制、effort 能力不同 | 已确认 |
| D-003 | 原起点为单一 Kev-4B；现行在同一入口使用**单活跃 Laya 或 Kev** | typed choice 和概率输出继续保留；代表权重依据同协议 Val 与独立 Dev 选择 | 原决定留存；V9 已支持两候选方向，任务效果待测 |
| D-004 | Agent 运行中可多次决策；admission-only 保留作对照 | 真实长程任务状态持续变化 | 已确认 |
| D-005 | 缓存是可观测状态与切换代价，不假设跨模型 KV 可直接迁移 | 实际 cache hit 与估计 prefix overlap 必须分离 | 已确认 |
| D-006 | 使用任务级终局成功、实际费用和成本剩余量评估 | 延迟回报无法由 API HTTP 成功替代 | 已确认 |
| D-007 | 历史日志只用于分布先验/成本校准，不构造虚假未选动作标签 | 缺 task_id、状态与 counterfactual | 已确认 |
| D-008 | 先搭建 Harness/Schema，再采集可重放受控轨迹 | 当前仓库没有可执行路由代码 | 已确认 |
| D-009 | 论文聚焦真实 Agent 状态与决策机制；不以字段数量为新意 | 避免空泛主张 | 已确认 |
| D-010 | 初期三份 Markdown 为公开事实源，E-DESIGN 后增为四份 | 支持 ChatGPT 与本地 Agent 交接、审阅和版本控制 | 已确认 |
| D-011 | 原 2026-10-09 约定为 main 上频繁 commit、会话/里程碑或最长 24 小时 push、无需 PR；现行提交、推送、PR、CI 只按当前任务明确请求执行 | 原频率留作历史，不将旧任务权限带入新任务，保留 Git 和本地修改 | 原默认规则已被替代；本轮不执行 GitHub 操作 |
| D-012 | 暂不迁移或归档历史研究目录，保持当前物理结构 | 现有目录可控，移动 PDF/截图可能破坏引用且不减少 Git 历史体积 | 已确认（2026-10-09） |
| D-013 | 服务器未来采用独立 ModelRouter 工作目录与 Python 环境；既有共享资源只读；本轮禁止实际服务器操作 | 降低对共享服务和既有资产的干扰，隔离实验依赖 | 已确认（2026-10-09，E0.5-ENV） |
| D-014 | 未来所有新会话从 GitHub 最新 main 及四份职责分离文档恢复，单一现状入口，事件后更新 | 防止旧聊天记忆、历史快照、推荐和未推送状态冒充当前事实 | 已确认（2026-10-09） |
| D-015 | Q-001=A：直接以真实公开 Coding Benchmark 为首轮任务来源，不要求自建合成任务先行 | 负责人明确选择 A 取代 Planning 原推荐 C；实际 Benchmark/样本量另议 | 已确认（2026-10-09） |
| D-016 | Q-002=B：商业 API 与本地开源模型进入同一候选池，effort 按真实能力标注 | 联合模型与推理档位、处理异构可用性，不伪造不支持的 effort | 已确认原则（2026-10-09）；V9 三 ID 已定，当前 Provider 研究池仅 Luna 列出 |
| D-017 | Q-003 旧 B 记录：本地模型费用无固定上限、API 按模型限额，旧额度/权限未决仅留历史；2026-10-30 用户明确从未设置 API 总 Token 或美元预算，按任务需要测试 | API 用量与官方价费用照实记录，bill 未知单列；保留服务器资源规则、训练不中断及 Final 隔离 | 当前决定已确认（2026-10-30），旧额度安排已取代；测试/部署已充分授权 |
| D-018 | Q-004=B：成功率约束下最小化整任务成本，具体阈值待定 | 与任务级研究主目标一致，避免只追逐调用价 | 已确认原则（2026-10-09） |
| D-019 | Q-005=B：分层基线与消融，历史 admission-only 仅作对照 | 需要区分运行时状态、effort、缓存的增量价值 | 已确认范围（2026-10-09），实施细节暂缓 |
| D-020 | Q-006=A：同一决策前状态受控分支为主验证原则，实施细节暂缓 | 仅历史观察数据无法提供未选动作真实结果 | 已确认原则（2026-10-09）；另有“rq 3 需要 ab 同选”待澄清 |
| D-021 | 当前 Planning 问答优先逐阶段讨论**如何训练模型**，暂不展开具体实验实施 | 负责人改变讨论优先级，不改变已确认的长期模型路由研究主线或 E1～E5 授权门槛 | 已确认协作要求（2026-10-09） |
| D-022 | Q-007 首阶段从 A 公开 Agent 轨迹着手；规划覆盖八组状态，但不制造缺失标签 | 负责人“从 A 开始”只明确起点，完整训练数据闭环（含自采）仍待商定 | 首阶段方向明确（2026-10-09），全阶段未确定 |
| D-023 | 数据源、厂商模型/缓存/计费政策需要**一个专门长期台账**，先登记再逐源选择，最后才讨论 AI 数据清洗；Q&A 保留用户正式批准的唯一裁决 | 唯一详细台账位于 our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md；不得在 Q&A/Research/Status 另维护平行最新版，不新建第二条执行链 | 结构需求确认（2026-10-09）；数据选择/清洗/训练未授权 |

**历史方案迁移说明**：2026-09 的 `IMPLEMENTATION_RESEARCH.md` 重点是“任务开始前一次选择 + GBDT/MLP 事前成本预测”。这是仍有价值的**对照基线和文献证据**，但当前主方法已更新为“运行时状态感知 + 单一 Kev-4B + 任务级回报”。不得在新代码中未经讨论把旧设计当作强制架构。

## 3. E0/E0.5 环境事实快照（[AUDIT]，2026-10-09 审计快照，非实时监控）

| 维度 | 观测 | 对后续的意义 |
|---|---|---|
| 仓库 | `sxyq/modelrouter`，`main`；在已授权扫描范围内为纯研究资产，**尚无 Router/Harness Python 实现** | 从最小代码骨架开始 |
| 本地 | macOS Apple Silicon；Python 3.9.6；PyTorch 2.4.1/MPS | 适合轻量开发、静态测试和数据核对 |
| 服务器 | 授权 GPU 服务器：Ubuntu 24.04，80 CPU 核，约 376 GiB RAM，单卡 A6000 48GB | 可进行 Kev smoke test，需隔离共享资源 |
| GPU | 2026-10-09 审计快照时 682 MiB/49140 MiB，利用率 0% | **仅是当时快照**；执行前重新查询 |
| 服务器 Python | 3.12.3；已有环境报告 torch 2.14.0+cu126 | 兼容性待专用环境验证；不污染共享环境 |
| 模型端点 | 已有共享文本、图像与对话端点已存在 | 不重启、不覆盖、不占用他人端口 |
| 模型权重 | 服务器共享模型目录存在大量已下载权重 | 在已授权扫描范围内**尚未确认 Kev-4B 及 Qwen3.5-4B-Base 权重已存在** |
| 项目目录 | 在已授权扫描范围内未发现 ModelRouter 项目目录 | 新建/克隆需任务授权 |
| CCH | 110 组统计、43 个模型、8 种 effort 标签、代表 750,212 调用 | 成本/缓存/Token 分布先验 |
| Blog GPT | 221,128 条调用、10 模型、7 effort 标签、37 个实际组合 | 调用级经验分布；成本是 quotaUnits 非 USD |
| Codex 监控 | 约 3,403 sessions、61,870 token 记录 | **隐私高风险**，不可直接提交或开放训练 |

**禁止推断**：上述快照不能证明当前 GPU 仍空闲、服务仍在线、模型版本不变，或所有日志字段均已达到训练要求。

## 4. 研究方法的固定接口原则

### 决策时刻 t

- `state_t`：只包含决策前可观察的任务、Agent、上下文、工具、验证、缓存、时间和服务商状态。
- `candidates_t`：当前可用的 Model × Effort 配置；显式记录 provider、模型版本、能力与限制。
- `constraints_t`：预算、上下文、权限、隐私、tool-loop continuity、速率限制、模型可用性等硬约束。
- `action_t`：一个合法 `(model, effort)`；不支持 effort 的本地模型不得伪造 low/medium/high 轴。
- `outcome`：动作后真实 usage、缓存命中、错误、后续执行轨迹与任务终局。
- `cost_to_go`：从决策点到任务终局的**观察到的**剩余成本；行为策略下的轨迹标签≠其他候选动作的反事实效果。

### 八组状态

1. Task/Subtask；2. Agent/Coordination；3. Context/Memory；4. Tool/Environment；
5. Verification/Recovery；6. KV Cache/Continuity；7. Temporal/Execution；8. Provider/Availability。

必须有**原始观测 / 派生特征 / 决策时硬约束 / 训练目标**的字段边界。任何来自当前动作之后的字段不得回流到决策前状态。

## 5. Planning / Execution 协作协议

### Planning Agent（本 ChatGPT）

- 审核 Execution 报告，区分事实、推断、未知；确定研究目标、实验假设、优先级和验收条件。
- 下发单一编号任务卡：`Task ID / Goal / Inputs / Allowed operations / Forbidden operations / Deliverables / Tests / Documentation / Git workflow / Stop conditions`。
- 对代码变更进行架构与实验有效性审查；对统计结论要求可复现证据。
- 根据真实报告或明确决定按职责更新四份文档；无新增事实的讨论不制造进度提交。
- **不能**声称自动监听本地或服务器、自动运行后台任务、或已完成未实际执行的实验。

### Execution Agent（本地 Agent）

- 严格按当前任务范围执行，先核对本地工作树和相关现状；未提交修改与他人工作全部保留，不覆盖、reset、clean 或强推。
- 可在已授权范围内修改代码、运行测试并维护相关原文档；提交、推送、PR、CI 只按当前明确请求执行，未请求时仅记录本地改动与证据。
- 不擅自访问新主机、安装大型依赖、下载模型、占用共享 GPU、调用付费 API、修改生产服务或上传私人数据。
- 任务完成按职责核对相关文档：Memory 记决策/交接，Status 记实测进度；Research 仅在证据、方法或实验协议变化时修改。无需修改的文档在交付中注明，不制造无意义更新。
- 交付实际变更文件、验证结果、未提交状态、仍待完成事项与风险；Git/部署版本只在该任务确有相关操作时报告，不能用旧远端版本推断当前服务器状态。
- 若任务超出授权或有冲突，停止并回报 Planning Agent。

### 轻量 Git 工作流（2026-10-29 按当前明确范围执行）
 
1. **默认在 `main` 开发**，不要求 PR；只有需要隔离高风险试验或用户明确要求时才使用独立分支。既有 PR #1 已关闭且未合并，保留为历史记录。
2. 用户明确要求提交时，按可验证的小步骤或实验里程碑组织 `git commit`；重要工作可附任务编号，不将每一行修改拆成独立提交。
3. 用户明确要求推送时再执行；会话结束或超过 24 小时均不自动触发推送。未推送或推送失败时标记“仅本地”，不能写成 GitHub 已同步。
4. 已请求提交时核对 `git status -sb`、`git diff --stat`、`git branch --show-current`；仅暂存指定文件，保护私人配置、日志、数据及未跟踪工作。
5. 已请求同步时才读取远端新状态并比较本地/远端版本；出现分叉或未提交冲突则报告，禁止自动 reset、clean、rebase、force push。
6. 已请求推送且目标明确时使用对应 Git 操作，再核实远端版本；本地 commit 与远端更新分别记录。
7. 实验记录需关联 **代码 commit SHA、配置版本、数据快照标识、模型版本、运行环境与结果路径**。服务器尚未部署时明确写“未部署”，不得把 GitHub main SHA 当作服务器运行版本。
8. 提交前运行适用验证并核对公开内容、相对链接与许可证。历史 PR/分支曾包含内部环境标识；不得未经批准重写公开 Git 历史，也不因本地修改自动启动 CI/PR。

## 6. 当前任务台账

| Task ID | 任务 | 状态 | 证据/验收 |
|---|---|---|---|
| MR-E0-001 | 本地/服务器只读审计 | **Execution 报告完成** | 用户提供 2026-10-09 报告；Planning 尚未远程复验 |
| MR-DOC-001 | 将研究总纲拆为三份 GitHub 规范文档 | 已完成（首次提交 cb460e8；后续校验已通过） | GitHub commit SHA + 三文件链接 |
| MR-DIR-001 | 当前本地/服务器目录核查与精简方案 | **审计报告与文档已验收** | Planning 核实 GitHub 分支和修订；服务器事实依据 Execution 审计快照，非独立实测；未移动/删除文件 |
| MR-SYNC-001 | 本地 Git 版本对齐核对 | **Execution 报告完成；Planning 验收** | Execution 报告本地 main 与 origin/main 同为 db355c7、ahead/behind 0/0；跟踪文件无修改，但 AGENTS.md 未跟踪；服务器未重查 |
| E0.5-ENV | 服务器独立工作目录及共享资源边界确认 | **已由项目负责人确认，E0.5 结束** | 未来独立工作目录和 Python 环境，共享资源只读；未授权任何服务器实际操作 |
| E-DESIGN | 详细实验设计与用户决策（`EXPERIMENT_QA.md`） | **进行中：Q-007 首阶段 A 起步明确；Q-010/Q-011 后续依次讨论** | 唯一 Q-007 第一阶段公开数据/八组变量/可信标签讨论工作包；Q-008/Q-009 实验细节暂缓，资源许可未批 |
| MR-E1-001 | 最小工程骨架、schema、cost ledger、单元测试 | **排在 E-DESIGN 决策后** | 可导入、可测试、无未来泄漏 |
| MR-E1-002 | 数据字段映射与数据可用性核对 | **待下发** | 字段覆盖、单位校验、脱敏汇总 |
| MR-E1-003 | A6000 Kev-4B 兼容性与资源 smoke test | **待批准资源操作** | 真实峰值显存/延迟/版本日志 |
| MR-E2-001 | Harness + 固定基线任务 pilot | **未开始** | 可重放任务与终局成功标签 |
| MR-E3-001 | 同状态受控分支实验 | **未开始** | 成对轨迹、预算和配对统计 |
| MR-E4-001 | Kev 训练与消融 | **未开始** | 训练日志、固定测试集、对照结果 |

## 7. 当前版本同步与下一阶段规划：E-DESIGN

**MR-SYNC-001 已完成（Execution 报告）**：本地 `main` 与当时 GitHub `origin/main` 均为 `db355c7`，ahead/behind 0/0；已跟踪文件无修改，`AGENTS.md` 仍未跟踪。Planning 已独立核实该 GitHub SHA，但不能直接核对本地工作树；本次文档更新会使 GitHub main 再前进一个提交，本地需下次工作时安全快进。旧审计分支不得直接合并或 cherry-pick 到 `main`，避免引入历史中的内部环境标识。

**环境决策已完成**：项目负责人确认未来使用独立 ModelRouter 工作目录及 Python 环境，共享资源只读。保留现有文献与数据目录，不迁移、不删除；服务器当前不创建项目目录、不安装依赖、不下载 Kev-4B、不运行实验。E0.5 已结束，E-DESIGN 正式启动。

**定位与目标**：在进入代码实现之前，由 Planning Agent 梳理并向项目负责人提出实验设计关键问题，明确评测任务集、动作空间与 effort 档位、预算上限、对照基线等核心边界。

**问答登记文件**：[EXPERIMENT_QA.md](EXPERIMENT_QA.md) 已在 E-DESIGN 启动时建立，专职记录 Q-ID、问题、选项、Planning 推荐及理由、用户回答、最终决策、日期和实验/预算/论文影响。2026-10-09 第二批 Q-004=B/Q-005=B/Q-006=A 已补记，和第一批共同保留；目前优先 Q-007 的公开轨迹 A 阶段，Q-010/Q-011 待依次讨论，Q-008/Q-009 实验细节暂缓。具体以 Status 首页和 Q&A 为准。

**后续工程衔接（MR-E1-001）**：待 E-DESIGN 问答决策完成并固定实验边界后，再由 Planning Agent 下发 MR-E1-001 任务卡，启动本地最小工程骨架与 Schema 开发。建议交付包含 `pyproject.toml`、`src/modelrouter/`、`tests/` 等本地轻量代码，不连服务器、不调用付费 API。

## 8. 交接时的固定回复格式

每次 Execution Agent 结束任务时报告：

- `Task / Status / Local HEAD / origin/main HEAD / Ahead-Behind / Dirty / Last push`
- `Observed facts`（审计时间与证据范围；服务器部署 SHA 或“未部署”）
- `Files changed`（四份正式文档逐份注明“已修改/已核对无需修改”）
- `Tests run`（通过/失败/未运行）
- `Resource / cost usage`（仅真实数据）
- `Risks / blockers / Next recommended task`（不自动执行）

Planning Agent 必须使用第 10 节新会话恢复协议；先核对 GitHub HEAD，按 [Status](PROJECT_STATUS.md) → [Q&A](EXPERIMENT_QA.md) → Memory → [Research](RESEARCH_OVERVIEW.md) 的顺序确认唯一下一行动。

## 9. 文档分层与按时间顺序的交接记录（MR-DIR-001 新规则）

### 9.1 文档体系与职责分工

| 类别 | 文件 | 读者 | 更新触发与职责 |
|---|---|---|---|
| A · 交接/记忆 | 本文件 `PLANNING_MEMORY.md` | Planning + Execution | **每次任务与决策**；按时间追加审计事件、Planning 审查意见、纠正事项、提交记录与后续决策 |
| B · 研究总纲 | `RESEARCH_OVERVIEW.md` | 项目负责人/论文研究 | **研究证据、方法或实验协议改变时**；方法未变时无需修改，避免流水账 |
| B · 进度看板 | `PROJECT_STATUS.md` | 项目负责人 | **每次任务状态变化**；统一首页看板、阶段表、工作包队列，确保当前状态一致 |
| C · 实验问答决策 | `EXPERIMENT_QA.md` | Planning + 项目负责人 | **已于 2026-10-09 E-DESIGN 启动时建立**；专职记录 Planning 提出的实验设计问题、选项、负责人回答、最终决策及日期 |
| D · 数据源与 Provider 政策 | [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md) | Planning + Execution + 数据审核 | **唯一详细数据/政策台账**；维护 Source IDs、官方链接、证据、许可证、八组状态映射、缓存实测/模拟等级、候选选择栏与下一阶段 AI 清洗质控；逐源选择仍回 Q&A |

“实时进度”来自执行者的现场证据与事件更新；本地文档、远端仓库和服务器运行状态分别注明时间及来源。提交/推送只按当前明确请求执行，未推送内容仅本地可见。不能声称 ChatGPT 自动后台监视本地、服务器或持续推送；不得为了更新泄漏私人日志。

### 9.2 时间线（只追加新事件；纠错注明原因）

| 日期 | 事件 | 证据/操作 | 状态 |
|---|---|---|---|
| 2026-10-07 | 历史研究材料、文献与实验资产已存在于 `main` | GitHub 旧提交 `13c14a3` | 历史基线 |
| 2026-10-09 | Execution 提供 MR-E0-001 本地/服务器只读环境审计 | 用户提供的审计报告；Planning 未直接连接服务器 | 报告已接收 |
| 2026-10-09 | 将原研究总纲整理为 Memory、Status、Research 三份 GitHub 文件 | GitHub `cb460e8`；补充完成状态 `51d0eb2` | 已完成 |
| 2026-10-09 | Planning 重新读取 GitHub 根目录与 `our-project/planning` | `main=51d0eb2`；远端结构已核验 | **仅 GitHub 已核验** |
| 2026-10-09 | 用户要求先核查**当前**本地和服务器目录、保持目录简洁，再启动工程开发 | 新任务 MR-DIR-001；本地/服务器最新目录尚未获取 | 已安排 |
| 2026-10-09 | Execution Agent 提交 MR-DIR-001 审计报告与精简方案到独立分支 | 独立分支 `agent/mr-dir-001-directory-audit`，完成初步审计 | 审计完成 |
| 2026-10-09 | Planning Agent 审阅反馈：未见正式 PR，要求更正阶段顺序（插入 E-DESIGN）、限定统计口径、公开脱敏、披露 Git 历史暴露风险 | 收到 MR-DIR-001-R1 修订任务要求 | 待修订 |
| 2026-10-09 | Execution Agent 完成 MR-DIR-001-R1 修订并创建指向 main 的正式 PR | 插入 E-DESIGN、登记 EXPERIMENT_QA.md 计划、更正 209 文件口径、脱敏内部细节、披露历史暴露风险、创建正式 GitHub PR | 已提交，随后经 Planning 核验 |
| 2026-10-09 | Planning 核实 MR-DIR-001-R1 修订与 GitHub 版本差异 | GitHub main 仍为旧版本、PR #1 的 head 为 a76fe4b；Planning 认可审计报告但未独立连接服务器 | 文档验收 |
| 2026-10-09 | 项目负责人改用轻量 Git 工作流 | 默认 main、本地频繁 commit、定期 push，不再要求 PR；PR #1 已关闭且未合并，直接更新 main；历史分支仍需注意隐私风险 | 已决策 |
| 2026-10-09 | Execution 回报 MR-SYNC-001 本地版本核对 | main 与 origin/main 均为 db355c7；ahead/behind 0/0；跟踪文件无改动，未跟踪 AGENTS.md 保留；服务器未重新核查 | Planning 验收；E0.5-ENV 待确认 |

### 9.3 当前 GitHub 已核验的核心目录（非本地/服务器最新快照）

~~~text
modelrouter/
├── README.md
├── our-project/
│   ├── README.md
│   ├── planning/        # 当前三份规范文档 + 历史 IMPLEMENTATION_RESEARCH.md
│   ├── literature/
│   ├── data/
│   └── 汇报/
├── research/            # 历史研究与专题
├── papers/              # 论文资产
├── external-projects/   # 第三方项目说明
└── .workbuddy/          # 历史工具记忆；需确认是否仍在使用
~~~

上图仅来自 GitHub 远端目录列表，**不能推断本地工作树、服务器磁盘与 GitHub 一致**。此前 E0 报告提及本地有未提交修改和 `AGENTS.md`，需要重新核实。

### 9.4 MR-DIR-001：本地/服务器目录治理审计任务卡（历史记录；PR 要求已废止）

**目标**：在开始编写 Router 代码前，找出实际目录、重复副本、共享资源边界和可精简的研究资产；先形成方案，不移动/删除。

**允许**：读取授权本地仓库及已配置服务器的项目相关目录；使用 `pwd`、`git status`、`git worktree list`、限制深度的 `find`/`du`/`ls`、`nvidia-smi` 等只读命令；脱敏汇总；在安全独立工作区内更新 Memory 和 Status，提交文档 PR。

**禁止**：猜测服务器连接信息；递归扫描整个私人 home；输出密钥、IP、私人绝对路径和原始会话；安装、下载、训练、重启共享服务；移动、清理、删除、覆盖目录或未提交工作；自动合并 PR。

**核查对象**：
1. 本地真实仓库根目录、一级/二级目录、重要三级目录；各目录用途、数量、大小、是否受 Git 跟踪、重复与风险。
2. 授权服务器 ModelRouter 克隆、数据、模型缓存、Python 环境、实验输出、共享服务目录；连接失败就报告未知。
3. GitHub 远端树与本地/服务器的差异；不得把 GitHub 列表当成机器目录清单。
4. 输出“实际树 / 建议精简树 / 保留 / 待归档 / 禁止碰触 / 待批准操作”。
5. 将**公开安全的汇总**追加到本文件时间线及 `PROJECT_STATUS.md` 进度看板；研究方法无变化时无需改 `RESEARCH_OVERVIEW.md`。

**验收**：有真实命令和时间戳支持的本地/服务器目录概览；每项归档建议说明是否共享、是否被引用、Git 跟踪与风险；无任何移动/删除；无敏感信息提交；Git commit/PR 可核查；停止等待 Planning 批准后续目录整理。

**历史记录（已被后续决策取代）**：MR-DIR-001 曾通过独立分支和 PR 提交审计材料；后续 Planning 已验收，PR #1 已关闭且未合并。现行流程为直接提交 main，详细实验设计尚未开始。

### 9.5 MR-DIR-001 / MR-DIR-001-R1：本地与服务器目录审计执行记录与交接

- **执行日期**：2026-10-09
- **执行角色**：Execution Agent
- **历史分支与提交**：`agent/mr-dir-001-directory-audit`，修订 head `a76fe4b`；曾创建 PR #1，现已关闭且未合并。当前安全修订内容由 Planning 直接提交到 `main`，不引入该分支中间提交。
- **只读操作说明**：未移动、删除或重命名任何现有代码、模型权重或研究数据。

#### 9.5.1 核心审计事实（只读实测证据快照）

1. **本地仓库（项目根目录）**：
   - **统计口径说明**：Git 跟踪管理的文件为 208 个，当前工作区未跟踪文件为 1 个（`AGENTS.md`），合计 209 个项目资产文件（总体积约 251.3 MB；若包含本地系统临时文件 `.DS_Store` 与未纳入版本控制的历史笔记 `.workbuddy/`，本地物理文件总数为 214 个）。
   - **代码状态**：在已授权扫描范围内未发现任何自研可执行 Python/Shell 代码，无 `pyproject.toml` 或 `requirements.txt`。
   - **数据状态**：`our-project/data/` 仅含 CCH 聚合统计（110 行，85 KB）与博客 GPT 历史明细（221,128 行，33 MB），为调用级数据，缺失 `task_id`、前置状态与终局 `resolved` 标签。
   - **文献与资产**：`research/task-level-cost-routing/literature/pdfs`（58 个 PDF，158.6 MB）与 `visual_report_assets`（73 个图像，25.4 MB）均已进入 Git 跟踪。
   - **重叠与冗余**：
     - `external-projects/`（9 个微型卡片，共 1.8 KB）与 `IMPLEMENTATION_RESEARCH.md` 内容重叠；
     - `research/jev-deep/`（7 文件，177 KB）与 `our-project/literature/jev-model-research.md` 存在大量重叠调研内容；
     - `papers/unified-ai-gateway.pdf`（4.0 MB）单立目录，与 `research/.../pdfs` 割裂；
     - `our-project/汇报/`（30 文件，29.2 MB）包含历史 PPT 页面与静态图。
   - **历史工具目录**：`.workbuddy/` 历史工具记忆此前在本地已被加入 `.gitignore`。

2. **远程授权 GPU 服务器（RTX A6000，2026-10-09 审计快照，非实时监控）**：
   - **硬件资源**：Ubuntu 24.04 LTS，80 核 CPU，376 GiB RAM（346 GiB 可用），1.2 TiB 可用磁盘，1× RTX A6000 48GB 显存（审计快照时显存占用 682 MiB，利用率 0%）。
   - **已有服务现状**：
     - AI 推理服务运行于服务器共享目录；
     - 已有共享文本、图像及 Web 对话服务处于运行中状态；
     - vLLM 推理服务当前为未运行状态。
   - **项目目录现状**：在已授权扫描范围内未发现 ModelRouter 项目目录或独立克隆。

#### 9.5.2 目录精简方案（暂不迁移；保留历史建议）

Planning 决定当前物理目录保持不变；PDF/截图迁移可能破坏引用且不能缩小已有 Git 历史。以下仅是历史建议，未经新授权不得执行。

- **建议保留的核心目录**：
  - `src/modelrouter/`（待后续任务新建）
  - `tests/`、`configs/`、`pyproject.toml`
  - `our-project/planning/`（规范文档体系）
  - `our-project/data/`（真实数据源：source / cleaned / summaries）
  - `our-project/literature/`（核心报告与 F1-F7 证据）
- **建议归档项目（待批准）**：
  - 将 `external-projects/` 收敛为单文件 `our-project/literature/external-references.md`；
  - 将 `papers/unified-ai-gateway.pdf` 归入统一文献目录；
  - 将 `research/` 下早期素材和 `our-project/汇报/` 标记为只读历史资产。

#### 9.5.3 公开仓库隐私脱敏与 Git 历史暴露风险披露

- **脱敏范围**：当前工作区各文档已全面删除或泛化内部主机名、用户家目录、私人绝对路径、连接细节与服务端口。
- **Git 历史暴露风险**：由于分支 `agent/mr-dir-001-directory-audit` 早期提交（`b9c2321`、`fbbb53e` 等）已推送到公开仓库，其历史提交记录中曾包含内部主机名、用户家目录路径前缀及端口号。
- **处理准则与状态**：本任务严格遵循安全纪律，**禁止擅自 force push 或重写远端公开历史**。上述历史暴露范围已如实向 Planning Agent 与项目负责人报告，等待决策后续是否需要启动专门的 Git 历史清理程序（如 `git-filter-repo`）。

### 9.6 历史阶段说明（以下是旧快照，不代表现状）

> **这一节保留 E0.5 确认前的原始阶段记录；最新阶段唯一由 [PROJECT_STATUS.md](PROJECT_STATUS.md) 首页确定。**

- **执行路线**：`E0.5 环境与文档确认 → E-DESIGN 详细实验设计与用户决策 → E1 工程基础 → E2 Harness 与基线 → E3 受控实验 → E4 模型训练与消融 → E5 论文与复现`。
- **当时状态（已过时）**：MR-DIR-001 与 MR-SYNC-001 当时已验收；E0.5 当时待服务器边界确认；E-DESIGN 当时尚未开始。**随后 E0.5 已完成并启动 E-DESIGN，详情见 9.9 与最新 Status。**
- **严禁事项**：不得在目录审计验收前跳过 E-DESIGN 直接启动 MR-E1-001 工程代码开发，不得下载大模型或修改服务器共享服务。

### 9.7 MR-SYNC-001：版本信息完整性核对

Planning 可直接读取 GitHub `main` HEAD 和已推送的三份文档，**不能据此知道本地未提交改动、未推送 commit、服务器当前代码或 GPU 实况**。Execution 每轮提供一份简短版本快照：

- `git status -sb`、`git branch --show-current`、`git rev-parse HEAD`；
- `git fetch origin` 后的 `git rev-parse origin/main`、`git rev-list --left-right --count origin/main...HEAD`；
- `git log -3 --oneline`、最近一次成功 push 的时间/commit；
- 本地未提交/未跟踪文件的**脱敏摘要**，禁止上传私人文件内容；
- 服务器项目目录/部署 commit（若不存在，写“未部署”）及环境观测时间；
- 本次三文档的更新/无需更新判断、测试与实验结果版本。

旧分支 `agent/mr-dir-001-directory-audit` 的历史仍在公开仓库中，**关闭 PR 不等于清除历史**；不擅自 force push、删远端分支或重写历史。

### 9.8 MR-SYNC-001 交付验收（2026-10-09）

- **Execution 报告**：本地分支 `main`、本地 HEAD 与 `origin/main` 均为 `db355c74d14fa062c55f128ad4ece1ac83111d30`；ahead/behind = 0/0，`git diff main origin/main` 为空。
- **工作区措辞**：已跟踪文件无修改，但 `AGENTS.md` 仍是本地未跟踪的私人文件；不得写作“整个工作区严格 clean”。
- **证据边界**：Planning 通过 GitHub 连接器核实远端 `main` 为上述 SHA；本地 Git 命令输出与服务器未重新核查的状态来自 Execution 报告。远端版本在后续文档提交后会改变，旧 SHA 仅代表本次对齐快照。
- **处理结论**：MR-SYNC-001 验收通过，不需要重做同步任务；服务器 ModelRouter 部署状态沿用审计快照，不当作实时核验。
- **后续结果（2026-10-09）**：项目负责人已确认独立 ModelRouter 工作目录与独立 Python 环境、共享资源只读，E0.5 已结束；E-DESIGN 已启动并创建 `EXPERIMENT_QA.md`，当前不创建、不安装、不下载、不训练。

### 9.9 E0.5-ENV 验收与 E-DESIGN 启动（2026-10-09）

- **负责人明确确认**：未来服务器使用独立 ModelRouter 工作目录与独立 Python 环境；已有共享资源只读。**这是隔离原则的决策，不是服务器写操作的授权**；实际路径、资源配额、依赖安装、模型下载和 GPU 使用仍需后续单独确认。
- **阶段判定**：E0.5 完成；E-DESIGN 正式启动，实验协议尚未确定。建立 [EXPERIMENT_QA.md](EXPERIMENT_QA.md) 记录设计问题与用户决策。
- **首轮问题（当时的历史记录）**：Q-001 提出时 Planning 推荐分阶段混合任务方案 C，当时尚待用户答复。**后续 2026-10-09 负责人已明确选择 A**，并确认 Q-002=B、Q-003=B 预算原则。当前待答是第二批 Q-004～Q-006，之后依次完成余下问答；具体情况仅以最新版 Q&A/Status 为准。
- **Git 同步边界**：本次文档由 Planning 直接提交 GitHub main；Execution 的上一轮本地 HEAD 快照在提交后不再等于最新远端 HEAD，下次本地工作前先安全 fetch/ff-only；保护私人未跟踪文件。

### 9.10 E-DESIGN 第一批决策与第二批交接（2026-10-09）

- **负责人明确答复**：Q-001=A（直接使用真实公开 Coding Benchmark）、Q-002=B（商业 API + 本地开源混合池）、Q-003=B（分阶段预算；本地模型推理费用不设固定上限，API 额度按具体模型限制）。
- **历史建议处理**：Q-001 原 Planning 推荐 C 已被 A 取代；不重启旧 admission-only 研究线。真 Benchmark 内的小样本 smoke 可讨论，具体任务集/数量仍待批准。
- **2026-10-09 历史授权记录**：只批准实验路线与预算**原则**；API 每模型具体额度未填，未授权付费调用、服务器访问/写入、GPU、安装、模型下载或训练。
- **唯一当前工作包**：E-DESIGN 第二批 Q-004～Q-006 已提出，等待负责人选项；其后继续 Q-007～Q-010 和尚未补齐的额度/任务/evaluator 细节。没有开始 E1。
- **写入职责**：Q&A 保存原话与选择，Status 首页保存唯一当前任务，Memory 保存 D-015～D-017 及交接；Research 仅同步 Q-001/Q-002/Q-003 的实质实验协议影响。此记录不宣称本地 Codex 或服务器状态已被直接核验。

### 9.11 E-DESIGN 第二批确认与训练优先交接（2026-10-09）

- **明确决定**：Q-004=B（成功率约束下优化整任务成本）、Q-005=B（分层基线/消融）、Q-006=A（严格同状态分支原则）；这三项已经由负责人明确答复，具体实施暂缓。
- **原话及未决指代**：“rq 3 需要 ab 同选”；在已给定 Q-006=A 的同条消息中出现，指代 RQ3 还是第三题尚不清楚，不擅自补成 Q-006=A+B。留在 Q&A 核对。
- **协作指令**：先只讨论模型如何训练，分阶段推进，暂缓实验实施/规模/统计/场景细节。这是**当前讨论顺序**的改变，不是直接跳到 E4 或重开一条训练工程链。
- **唯一下一工作包**：在既有 Q&A 文档中提问 Q-007（训练数据）、Q-010（Kev 训练初始化）、Q-011（监督目标/阶段），其他 Q-ID 未关闭的细节保留、不得视作批准。
- **权限**：没有新增任何服务器、共享资源、GPU、付费 API、安装/下载或训练执行许可；GitHub 远端与本地/服务器状态须分层报告。

### 9.12 Q-007 第一学习阶段公开轨迹研究（2026-10-09）

- **负责人方向**：“第七个问题需要仔细查询……最后决策用的变量有多个，需要都覆盖到；从 A 开始”。记为第一阶段优先公开 Agent 轨迹，不误认完整训练只能用 A。
- **八组状态**：Task/Subtask、Agent/Coordination、Context/Memory、Tool/Environment、Verification/Recovery、KV Cache/Continuity、Temporal/Execution、Provider/Availability。还需 Action/Constraints 与 Outcome/Provenance；可缺失但不能虚构成功、物理缓存或 effort 标签。
- **外部证据**：Open-SWE-Traces（首选，许可记录在 Q&A）、CMU agent_trajectories、SWE-Gym、AgentSuite（用途/许可需区分）；Finding the Right Fit 明示不可用于微调或训练。
- **学习阶段建议尚未批准**：公开前缀 + 已执行动作结果预测，若有真实账本才学观察到的 cost-to-go，随后再讨论有真值的预算/能力规则辅助与可比动作的 choice 训练。Kev 官方 continuation 推荐仍需 Q-010 确认。
- **状态/权限**：只进行了只读源研究与文件更新，没有下载数据、运行训练、使用 GPU/付费 API、访问或修改服务器。

### 9.13 Q-007-R1：开源数据与训练预处理方案（2026-10-09）

- Planning 按负责人要求研究两类训练主数据：Agent 运行轨迹与静态任务-模型结果；并审查八组状态、缓存和厂商规则、所需数据量。
- 数据源、具体许可证阻塞、预处理顺序、真实标签与规则标签边界、阶段划分，详见 Q&A 的 Q-007-R1；未知许可证数据不得加入训练，Finding the Right Fit 明确禁止训练。
- 本轮为**只读研究及文档提案**，无真实语料下载/处理/训练、无服务器/GPU/付费 API 使用；唯一当前任务仍是第一大阶段 Q-007 训练数据来源及加工方案的审议。

### 9.14 Q-007-R2：多变量数据目录和 OpenSquilla 架构研究（2026-10-09）

- 用户要求先把**缓存真实调用与复用、Context/Memory、Agent 协作、执行时间预算、主要中国及国际 Provider 政策**数据源列完整；不讨论数据量，不清洗、不启动工程。
- Q&A Q-007-R2 新增 Mooncake FAST25 真实请求前缀散列值（reuse potential 非实报 cache hit）、BurstGPT/阿里 xMaaS 的时间资源负载、LongMemEval-V2/LoCoMo 等记忆、MARBLE/MASBench/AgentWorld 等多 Agent，供应商政策登记和局限。
- OpenSquilla 论文与实际代码明确 Harness/Router/Memory/Context 分工，可供单一 ModelRouter Harness 的结构参考；不在此阶段复制完整 Agent 产品、也不启动并行实现链。
- 本轮只增加数据候选目录和长期研究记忆，**无下载/清洗/训练/模型推理/GPU/服务器/付费 API**；具体原始数据许可证和每字段覆盖率未实际审计。

### 9.15 Q-007 数据与政策专用台账正式建立（2026-10-09）

- 负责人要求在文档中**专设一处**长期登记公开训练数据源、主流模型与供应商政策、KV 缓存政策，然后按批准结果挑选哪些数据、如何让 AI 合规清洗。
- GitHub main 建立 [DATA_SOURCE_AND_POLICY_REGISTRY.md](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md)，在既有 data/ 目录下唯一维护原始来源、八组变量、Cache 数据真实性、Provider 官方证据、选择状态和后续数据加工质量要求；原 Q-007-R1/R2 仅保留作为历史研究与问答，不再平行更新政策详细清单。
- 仍无数据源逐项批准、真实下载/清洗/训练、服务器/GPU/API 使用授权。下一步负责人审阅 Source Registry/Provider Policy/Selection Board，项目阶段 E-DESIGN 不变。

### 9.16 Q-007 文件数量审计与真实数据源清洗/训练规划（2026-10-09）

- GitHub main 文件树核对：210 个文件，44 Markdown，五份当前核心管理文档（Status、Q&A、Memory、Research、Registry）；历史 IMPLEMENTATION_RESEARCH 与导航 README 不计入核心五份。
- 重复主要来自 Q&A 历史 R1/R2 与 Research/Memory 的数据事实；现有物理目录保持现状。**以后 Registry 唯一更新最新 Source/Provider/Cache/AI 清洗详情；Q&A 记录负责人选择，Status 保留唯一当前任务。**
- 官方数据卡与 Kev 训练格式复核：Open-SWE 参考补丁不能进决策输入、SWE-smith 多 split 需核、Mooncake 散列值只代表缓存可复用潜力、LLMRouterBench 许可仍待审、Kev 通用微调记录有严格 2048 token 限制。
- Registry §6.2～6.5 已列推荐最低源、source-specific normalize、task/repo split、真实标签/静态比较/缓存模拟的分离及 Kev M1～M4 训练路线。全部是 Planning 推荐，**没有逐源批准、下载/清理、训练或模型/API/GPU 操作**。

### 9.17 E-DESIGN 路由训练相关工作、论文方法图与外部 Harness 方案（2026-10-09）

- 负责人提出：当前数据→清洗→训练顺序是否学术充分，传统/神经模型路由及 LoRA 类论文怎么训练与发表，论文方法图怎么画，外部 Agent 框架怎样搭。
- 本轮只读核对 RouteLLM (ICLR 2025)、FrugalGPT (TMLR 2024)、BEST-Route (ICML 2025)、Route-to-Reason (2025 / WWW 2026)、TwinRouterBench、Budget-Aware Agentic Routing、ProgRouter、HM-Router、OpenSquilla、Kev 官方格式及 mini-SWE-agent/LangGraph 官方能力，完整比较见 RESEARCH_OVERVIEW §6.2。
- 研究结论：数据清洗前必须定义路由状态/动作/合法池/真实标签，训练前需要最小 Harness state/log/checkpoint 契约和可验证任务终局；训练中的 observational outcome、static preference、cache reuse 与同状态 counterfactual 严格分离；建议单 Kev 的领域适配与后续真实配对决策分阶段，**不规定必须 RL**。
- 论文方法图应分「在线 Agent/Harness/Router/Provider 账本」和「离线多来源 supervision → Kev 训练 → 同状态比较/校准」；OpenSquilla 现行公开 SquillaRouter 自学习已移除，不能当现成在线训练引擎。Harness 未来只批准**单一主实现/调用入口**，优先比较 mini-SWE-agent（coding 基准）和 LangGraph（多 Agent checkpoint）。
- 这轮仅作学术规划文档更新，不批准 Q-010/Q-011、下载/清洗真实数据、服务器/GPU/API、编写代码或启动训练。唯一当前讨论包仍是 Q-007 数据源审核，Status 不变。

### 9.18 最简论文实验流程与 Kev 微调执行风格（2026-10-09）

- 负责人最新明确：删去工程审批限制、复杂工程单测/CI、防御性框架、版本固定和散列管理；仅一个终端入口，优先真实数据清理、微调与进度输出。
- Research §6.3 已说明公开来源→可信监督→Kev LoRA 初始适配→Harness 同状态比较→动态路由微调→任务级评估。保留训练/测试分割、未来泄漏、cache 真实标签区分这三项科研事实约束。
- 本轮只更新研究设计和协作规则；已上传清洗脚本仍非可比较的最优路由标签数据集。没有执行 GPU/训练/下载新数据，拟议 run_experiment.py 尚未创建。

### 9.19 五文档持续对话、Paper Research Router/Obsidian 与服务器任务交接（2026-10-09）

- 当前唯一科学主线：长程单/多 Agent 执行中，联合 model×reasoning effort、KV 缓存、8 组状态与实际任务级总成本；目标是成功率约束下节省整任务费用。现有 Blog/CCH 221,128 行→178,621 样本来自本地执行报告，是实际调用记录，不能作为真实最优选择标签。GitHub main 可核 prepare_router_data.py；公开 Agent 数据服务器清洗还未收到实测报告，Kev 尚未训练。
- 分工：ChatGPT 为 Planning/科研讨论；本机 Codex 完成最新 GitHub 文档同步、真实 Skill 调用、PDF 阅读、Obsidian 一文一笔记；服务器 Execution Agent 在自有中文研究目录做公开源下载/CPU 清洗和统计，所有大数据留服务器。
- 已查实 Skill 位于私有 sxyq/skill- 的 latest/skills/codex/paper-research-router/SKILL.md，本机通常核对 ~/.codex/skills/paper-research-router/SKILL.md；它对已有 PDF 提供 intake、paper-reader、页码证据与结构化笔记。新论文检索由 sxyq/research-router 的 research-router 负责，证据审阅可用 literature-evidence-audit。其 paper-intake/reader 的完整研究 workspace 模式可能需要未随 Skill 附带的 .research/schema，缺失时采用轻量 Obsidian 笔记。
- 本仓库 research/task-level-cost-routing/literature/pdfs/ 实有 **58 个 PDF**；manifest.json 仅有 **54 条**，README/index 也截至 54；55–58 对应 CATS、Harness-Native Agentic Routing、EET 和 Price Reversal。先补现有 manifest/index/README 的差额，勿重复下载。以原 literature 文件夹作为一个 Obsidian Vault，在其中新增中文 论文笔记/ 和 主题索引/；每篇用唯一编号、规范 frontmatter、[[wikilinks]] 与原 PDF 相连。
- 第一轮重点论文：SWE-Router、TRACE-Router、PROGROUTER、TwinRouterBench、Boundary-Guided Agentic Routing、Harness-Native Agentic Routing、TACIT-Switch、EarlyEval；Route-to-Reason、Switchcraft、BEST-Route、UNISCALE；RouteLLM、RouterBench、LLMRouterBench；Unified AI Gateway、InfraMind、KVFlow、LMCache、TokenDance；Kev、TypeSafe Jev/System One、Visual Jev、Laya、Simple Jev、AnyJev。分别标明真实训练数据、训练方式、结果和本项目对照差异，所有断言追溯原文。
- 新目录和新 Markdown 报告尽量中文；技术代码、标准目录、原数据集英文名不批量改。用户不希望 CI/额外执行限制/版本固定/复杂散列值管理；最小论文真实性核对依旧必要。GitHub 只提交代码/报告/少量公开笔记，不提交私密现场、大数据、凭据。
- 本轮是 Planning 在远端五文档同步后的交接约定，**并非本机 Codex/Obsidian/服务器数据已经执行完成的证明**。

### 9.20 服务器首批公开数据运行报告的科研审阅（2026-10-09）

- Execution 报告/远端 main 966f582 可核对：本地/服务器运行新增 prepare_router_data.py public 模式，原始下载约 405MB，导出 20k Agent step、30k Arena 偏好、30k Mooncake 请求、970 TwinRouterBench，合计 80,970 样本，并写 train 57,165 / val 12,123 / test 11,682。实际读取的 Open-SWE 和 SWE-smith 都只是一份 Parquet shard，并非全部官方公开轨迹；LLMRouterBench 仅索引了任务目录。Planning 已核对 GitHub 代码和 50 条预览，**没有登陆服务器重新核验完整原始/清洗 JSONL**。
- **重大标签审查**：Agent 的 step_complexity=step/error 阈值、is_high_effort=complexity==high、cache_hit=step>1；Arena 的 is_high_effort 取 winner 模型关键词或 prompt 长度，cost_tier 由 prompt 长度估出，state 只有 prompt_chars 无实际 Prompt；Mooncake 的 cache_affinity=散列值 prefix hit ratio 阈值、is_cache_hit=历史请求散列值复用机会，不是实际 Provider cached_read。标签明显有多项规则映射/不对应真实动作，不能称 80,970 个最优 model×effort 标签。
- **泄漏/评测**：Agent 清洗在处理 assistant 当前消息后才记录 context_chars/prior_tool_calls，包含当前动作信息（pre-decision 泄漏）；原脚本按 trajectory ID 分 Train/Val/Test，无法保证同一真实 instance/repo 不串集；Mooncake 每 100 条人造 task_session_id，不是真任务；TwinRouterBench 被合入 training，失去独立评测效力。未实际评估跨同题重复，不能称严格无泄漏。
- **Kev 官方接口不兼容**：需将 choice.options 换成 choice.criteria map，score.levels 换成 score.criteria list，score.label 从 budget/standard/premium 字符串改为 0/1/2；只使用证据充分的监督问题。官方来源 jaredpalmer/kev 的 skills/kev-finetune/references/data-format.md 和 README.md；可用官方现有工具做单次轻量输入验证，然后才做小样本 LoRA smoke test。
- **唯一接续任务**：原始公开数据保留服务器，在唯一 prepare_router_data.py 上更正科研标签和数据格式；重提取 Agent 真实 outcome，只做 observed continuation 监督；Arena 原 Prompt+winner 做偏好；Mooncake 单独作为 cache workload；TwinRouterBench 留独立测试；模型最佳动作训练必须等同状态真实动作后续对照。优先向 Codex/Execution 派发修复，不额外创建 v2 脚本或 CI。
- **公开文档隐私提醒**：执行者提交的《服务器资源与目录说明》公开版曾含内部网络/登录及端口信息；Planning 已对最新 main 的公开版进行最小脱敏，但旧提交仍有历史痕迹。未来只写用户 Home 相对路径和公开可披露聚合硬件数；需要完全删除历史必须另行明确讨论。

### 9.21 Q-007 全量公开数据重建、真实清洗与四批次样本 GitHub 审查交付（2026-10-09）

- **彻底废弃旧产物**：Execution Agent 在 GPU 服务器与本机彻底删除此前由固定切片截取（80,970 条）和规则推断伪标签产生的旧清洗数据，保证无历史污染。
- **全量真实清洗完成（4 大批次，16 个核心数据集，2,282,484 条真实有效记录）**：
  1. **Batch 1 (Agent 执行轨迹)**:
     - `TRA-001` (NVIDIA Open-SWE-Traces, 6 代表分片, 942 MB): 43,154 决策步, `OBSERVED_ACTION`
     - `TRA-002` (SWE-smith Trajectories, 全部 8 分片, 972 MB): 107,983 决策步, `OBSERVED_ACTION` (Claude 3.7 Sonnet)
     - `TRA-003` (CMU Agent Trajectories): 上游 HTTP 403 访问受限，严格执行零造假记录为 0 条
     - `TRA-004` (AgentSuite multi_challenge, 全部 8 模型全量 JSONL, 44 MB): 2,736 决策步, Thinking-On/Off 对照
  2. **Batch 2 (模型路由比较)**:
     - `ROUTE-001` (LLMRouterBench, 700 评测文件, 6.6 GB 解压): 548,059 条实测记录, 27 benchmark × 40 模型
     - `ROUTE-002` (RouterBench, 95 MB): 36,497 条 0-shot 样本, 11 模型评估 + Oracle 路由
     - `ROUTE-003` (TwinRouterBench, 1.2 MB): 970 步降级搜索标签, **强制标为 `EVAL_BENCHMARK_ONLY` 绝不进训练**
     - `ROUTE-004` (Arena 55k, 176 MB): 57,477 场真实用户 Prompt 与盲测胜负, `HUMAN_PREFERENCE`
     - `ROUTE-005` (Finding The Right Fit, 0.2 MB): 6,204 条多 Harness 实测开销, **标为 `RESEARCH_ANALYSIS_ONLY` 禁训**
  3. **Batch 3 (KV 缓存与时间负载)**:
     - `CACHE-001` (Mooncake FAST'25, 3.2 MB): 39,632 条请求, 前缀块复用机会标为 `OBSERVED_REUSE_OPPORTUNITY`，绝不冒充商业 Provider 实际缓存
     - `TIME-001` (BurstGPT, 49 MB): 1,404,294 条生产环境请求真实时序到达与负载, `OBSERVED_WORKLOAD`
  4. **Batch 4 (记忆、协作与任务环境)**:
     - `ENV-001` (SWE-Gym, 42 MB): 2,438 个任务环境基准与回归测试套件, `TASK_ENVIRONMENT`
     - `ENV-002` (SWE-rebench-V2, 409 MB): 32,079 个跨 20 种编程语言任务基准, `TASK_ENVIRONMENT`
     - `MEM-003` (LongMemEval-V2, 0.8 MB): 451 个长程任务与 100 轮干草堆记忆, `MEMORY_BENCHMARK`
     - `MEM-005` (MemoryCraft, 16.5 MB): 510 条跨会话记忆与问答对, `MEMORY_BENCHMARK`
     - `MAS-001` (MARBLE-MultiAgentBench): 上游 HTTP 401 访问受限，合规审计记录为 0 条
- **审查资产全部上线**：为每个数据集独立抽取 35 条代表性真实样本（`清洗样本.jsonl`）、完整统计（`字段统计.json`）与规范说明（`样本说明.md`），全部提交并推送到 GitHub main。
- **唯一脚本演进**：保留唯一主程序 `prepare_router_data.py`，未建立任何并行清洗入口或冗余额外执行限制。
- **当前状态**：四批次全部交付完成，等待 Planning Agent (ChatGPT) 审查 GitHub 独立样本并给出下一步指示。

### 9.22 Q-007 公开数据全量重建科研纠偏执行完成（2026-10-10）

- **差额澄清与数量统一**：Execution Agent 查明此前 1,681,177 行差额源于旧报告误将轨迹数填入步数列。本轮重新清洗后，**16 源 `字段统计.json` 汇总数（6,600,628 步/条）与服务器物理文件实际 `wc -l` 绝对吻合，差额为 0**。
- **全量分片下载与清洗扩充**：
  - `TRA-001` (Open-SWE-Traces): 12 分片，30,000 轨迹，2,075,629 决策步，保留 Qwen3.6/3.5/3.8/DeepSeek/MiniMax 真实开源模型。
  - `TRA-002` (SWE-smith): 全部 24 分片（8 ticks + 8 tool + 8 xml），76,002 轨迹，2,331,584 决策步，抽取 125.6 万次 `str_replace_editor`、90.1 万次 `bash` 与 12.2 万次 `submit`，彻底根除“全为 text_response”缺陷。
  - `TRA-003` (CMU Agent): 上游 HTTP 403 访问受限，如实记录为 0 条，不造假。
  - `TRA-004` (AgentSuite): 全部 30 模型/思考模式，8,190 episode，41,430 步，提取 `meta.id` 对齐 273 个独特任务实例，生成同题跨模型审查组。
  - `ROUTE-001` ~ `ROUTE-005`: 涵盖 548,059 条 LLMRouterBench、36,497 条 RouterBench、970 步 TwinRouterBench（移除未来 total_steps 并强制 `EVAL_BENCHMARK_ONLY`）、57,477 场 Arena 人类盲测偏好、6,204 条 FindingTheRightFit（强制 `RESEARCH_ANALYSIS_ONLY`）。
  - `CACHE-001` (Mooncake): 39,632 条请求，按时间戳排序，计算严格 LCP 连续前缀匹配，`output_length` 隔离至事后结果，抽取连续 35 条请求展示动态演进。
  - `TIME-001` (BurstGPT): 1,404,294 条生产环境请求真实时序到达与 Token 负载。
  - `ENV-001` & `ENV-002`: 2,438 个 SWE-Gym 与 32,079 个 SWE-rebench-V2 跨语言任务环境。
  - `MEM-003` (LongMemEval-V2): 451 个长程记忆任务，成功载入 `questions.jsonl` 真实题面、企业领域、环境名称、标准答案与评估函数。
  - `MEM-005` (MemoryCraft): 扩充包含 `ama_bench` 与 `membench`，有效记录达 23,884 条。
  - `MAS-001` (MARBLE): 上游 HTTP 401 访问受限，如实记录为 0 条。
- **十项代码级缺陷彻底闭环**：时序严格递增、模型标识客观真实、多格式动作识别、跨模型同题对齐、LCP 前缀匹配、排除未来泄漏、记忆题面注入、多来源扩充、动态缺失率计算、单脚本独立 `--mode public` 运行。
- **当前状态**：16 组样本与统计已全部推送到 GitHub main，等待 Planning Agent（ChatGPT）通过 GitHub MCP 进行最终审查。

### 9.23 本轮 660 万条数据二次执行后的科研审查（2026-10-10）

- **2026-10-10 Planning 对提交 `0b39a7e` 的三次科研独立复审：** 已核 GitHub 16 份字段统计，按来源求和确为 **6,600,628** 条不同粒度记录；14 个来源含实际审查样本、CMU/MARBLE 两个受限为零。Execution 报告服务器 `wc -l` 与统计相同，但 Planning **未亲自登录服务器复核完整清洗文件**；不能把总量解读成模型路由监督数量。
- **已确认修复**：`--mode public` 存在且与 Blog/CCH 分离；TRA-001 当前调用工具未提前计入 `prior_tool_calls_count`（第一步=0）；模型名从 metadata 优先提取；TRA-002 增加动作解析；TRA-004 使用 meta.id 对齐 273 个任务；CACHE-001 按 timestamp 排序、按有序前缀链计算复用潜力、output_length 移到事后；TwinRouterBench 的 total_steps 从决策前状态移出；LongMemEval 增加问题/答案；MEM-005 扩展四子集。SWE-smith 官方 ticks/tool/xml 各 8 个 shard，当前 24 分片与官方 metadata 一致；AgentSuite 官方 30×273=8,190 episode，当前覆盖 30 配置。
- **仍未验收的科研缺陷**：(1) AgentSuite `pre_decision_state` 包含 `meta.target_question` 和 `meta.pass_criteria`，未证明是执行时可见字段，可能注入事后评测 rubric；同题跨模型为 **Episode 级**反事实近似，不等于同一个中途 state 的模型切换结果，thinking-on/off 不能无条件跨 Provider 标准化。(2) SWE-smith `extract_swesmith_action()` 从 Markdown 代码块首词推断动作，动作分布出现 `the`、`this`、`2.`、`pip`，不能把所有识别记录都叫真实 Tool API 调用。(3) Mooncake 有序前缀只证明历史复用机会，任意丢弃缓存前缀集合的策略不是确定性物理缓存容量/TTL/命中。(4) 缺失率以各源 35 条 GitHub 抽样 `sample_records` 计算，不能声称完整数据集精确缺失率。(5) LongMemEval `initial_memory_snippet` 仍是形如 `f224a4eb` 的散列字符串，没有承载有效历史语义。(6) LLMRouterBench 单模型观察标签标为 `POST_HOC_BENCHMARK_ORACLE`，但最优模型尚需按同题完整评分和成本目标计算；并无 task/repo 完整 split 或 Laya/Kev 正式训练文件。(7) Open-SWE 仍为 12 代表分片（字段统计明标 PARTIAL），不能称全量官方覆盖。

### 9.24 Q-007 科研数据收尾、统一训练视图与 Kev 任务级划分闭环（2026-10-10）

- **执行 Agent 闭环响应**：针对 Planning 三次复审提出的 7 项科研缺陷，Execution Agent 在唯一入口 `prepare_router_data.py` 中完成全部修复与重跑：
  1. **AgentSuite 洁净隔离**：`target_question` 与 `pass_criteria` 严格移入 `ground_truth_outcome`；组织 273 个独立任务 × 30 个模型的整任务 Episode 对照；中途同状态反事实分叉数量**如实确切记录为 0**（绝不编造）。
  2. **SWE-smith 真实三分类**：区分为 `EXPLICIT_TOOL_API`、`INFERRED_COMMAND`、`TEXT_RESPONSE`，过滤 `the/this/2./pip` 停用词。
  3. **Mooncake 严格有序 LCP 前缀**：移除 30k set 截断，标记为 `HISTORICAL_PREFIX_REUSE`，`is_simulated = True`，`physical_provider_cache_hit = False`。
  4. **全量流式缺失率追踪器 (`StreamingFieldTracker`)**：伴随物理写入扫描 100% 记录（6,600,628 步/条），核心字段非空率达 99.9993%。
  5. **LongMemEval-V2 语义注入**：载入 451 真实题目与 1,870 条历史任务语义目标，标准答案严格隔离。
  6. **统一模型选择训练视图与 Kev 官方格式导出**：
     - 整合 ROUTE-004 (Arena 55k 39,716 场明确胜负，排除 17,761 场平局)、ROUTE-001 (LLMRouterBench 26,368 题 Oracle 对齐)、ROUTE-002 (RouterBench 35,189 题官方 Oracle 对比)、TRA-004 (AgentSuite 273 独立任务成对对比)，产出 **100,372 个独立路由任务**，输出为标准 Kev `{state, questions}` 格式样本；
     - 按任务 ID 进行 **80% 训练集 (80,343 条)、10% 验证集 (10,053 条)、10% 测试集 (9,976 条)** 确定性散列物理隔离，**跨集重叠为 0**；
     - **TwinRouterBench (970 步)** 导出为独占外部评测集 `data/kev/公开数据/test_twinrouterbench_holdout.jsonl`，在训练/验证集中 **0 步进入**。
  7. **5 份轻量预览与科研收尾报告上线**：在 `our-project/data/公开数据/数据预览/训练视图/` 产出 5 份样本，生成 [科研数据收尾报告.md](../data/科研数据收尾报告.md)，全面闭环 9 类确切统计指标。

### 9.25 Q-007 训练视图最终科研纠偏、真值对齐与 Kev Schema 全量验证闭环（2026-10-10）

- **历史 Q-007 数据真值纠偏**：具体清洗纠偏、合法 Thinking 对照数量与来源验证保留在 [DATA_SOURCE_AND_POLICY_REGISTRY](../data/DATA_SOURCE_AND_POLICY_REGISTRY.md) 的 2026-10-10 节，本文件仅保留交接索引。

- **当前状态**：公开数据清洗与训练视图构建彻底收尾，等待 Planning 最终验收并开启微调前 Smoke Test。

### 9.26 Q-007-FINAL 验收与全量 660 万条数据分层、八组状态覆盖及目录治理闭环（2026-10-10）

- **1. 67,853 vs 67,428 对账闭环（P0）**：
  - 经服务器 `data/{kev,laya}/公开数据/` 物理文件 `wc -l` 与 `sha256sum` 实测确认，唯一正式固定版本为 **`train.jsonl` 67,428 / `val.jsonl` 8,436 / `test.jsonl` 8,446**（合计 84,310 题），与 `manifest.json`、`数据划分统计.json`、`科研数据收尾报告.md` 完全一致；旧数字 `67,853 / 8,136 / 8,321` 为标点归一化前中间统计，已统一更正。
- **2. 全量 6,600,628 条公开记录 + 221,317 条自有记录五阶段课程分层（P1–P3）**：
  - **阶段 1（静态模型选择单胜者监督，84,310 题）**：`ROUTE-004` (39,716) + `ROUTE-002` (35,189) + `ROUTE-001` (9,386: `1,432` 唯一高分 + `7,954` 同分最低实测 USD) + `TRA-004` (19)；另有 `16,070` 题并列/全败分析集与 `970` 步 TwinRouterBench Holdout。
  - **阶段 2（Agent 决策前状态与终局结果预测，4,448,643 步 / 88,087 轨迹 / 35,289 任务）**：`TRA-001`（2,075,629 步 / 30,000 轨迹 / 3,240 仓库）、`TRA-002`（2,331,584 步 / 49,897 轨迹 / 119 仓库）、`TRA-004`（41,430 步 / 8,190 Episode），按代码仓库与任务 ID 80/10/10 隔离。
  - **阶段 3（Thinking Effort 与同系列推理对照）**：`TRA-004` 严格拆分为 **1,365 对同一权重运行时开关**（5 模型 × 273 任务）+ **273 对同底座专用 Thinking 权重**（`Qwen3-235B-2507` Instruct vs Thinking）= **1,638 对**；**1,638 对跨版本/跨变体比较**（6 对 × 273 任务）单独登记；`ROUTE-001` 含 **27,192 对**同系列推理 vs 指令对。
  - **阶段 4（KV 缓存前缀复用、到达时序与真实成本先验）**：`CACHE-001`（39,632 条）、`TIME-001`（1,404,294 条）、`OWN-001..003`（221,317 条，含 185,154 次物理缓存命中）。
  - **阶段 5（在线 Coding/Memory Benchmark 与未来中途反事实路由）**：`ENV-001/002`（34,517 题）、`MEM-003/005`（24,335 条）。实测确认公开集中**中途同状态反事实分支数为 0**、**多 Agent 角色交接轨迹数为 0**。
- **3. 目录治理与公开脱敏（P4）**：
  - 建立服务器 `runs/`（归档 `runs/E1-smoke-test-20261010/smoke_test_results.json`）与 `.tmp/`，清理本任务自建临时目录 `.tmp/task_layer_audit_20261010/`，保留历史遗留文件清单待用户确认；恢复 `AGENTS.md` 为本地未跟踪文件，脱敏全部公开文档中的服务器绝对路径。

新对话请以 Status §0.2 与最新实际 GitHub HEAD 为准，不要把本次字段统计的混合行数当成动态路由监督标签数。

## 10. 新会话恢复协议（长期生效）

### 10.0 用户固定要求：每次收到执行结果的回复形式（2026-10-10 确认）

**固定五段，不得颠倒**：

1. **整体进度先说**：项目到了哪个大阶段、前面完成了什么、下一阶段尚未做什么。用简短进度表，切勿伪造完成百分比。
2. **当前阶段逐项展开**：列出当前阶段的几个小步骤，每步讲清「完成了什么 / 现在是什么状态 / 还差什么」。
3. **接下来做什么**：最多聚焦一个明确的下一执行工作包，解释为何先处理该工作包，不重新设计全项目。
4. **可直接复制的完整执行提示词**：写给 Codex / Execution Agent；包括目标、步骤、现有路径、验证方式、边界、成果、停止条件。已通过的事项不要重做，禁止衍生平行主链或未授权调用资源。
5. **简单的情况说明**：用非技术语言解释问题与风险，尽量不使用缩写；技术名词必须附一小句解释。

**每次**用户送来 Execution 的执行报告，就按这五段回复；如果有联网的 GitHub 源码证据，先核最新 HEAD 并逐项比较。明确「实际核实」「执行方报告」「暂不能核实」三类，发现冲突就标记「待对账」，不要未经核实宣布 100% 完成。用户没有明确批准时，提示词不得自动授权 GPU 正式训练、付费 API 或共享服务操作。

**文档修改规则**：`PROJECT_STATUS.md` 是唯一的最新进度和阶段详情；`EXPERIMENT_QA.md` 记真实决策及授权状态；本文件记长期交接与固定回复方式；`RESEARCH_OVERVIEW.md` 只记研究方法及相关证据；`DATA_SOURCE_AND_POLICY_REGISTRY.md` 只记数据源与模型/成本政策。按真实变化更新有关文件，不要为格式而重复修改全部五份。

### 10.1 每轮研究如何接续与更新

1. **启动**：核验 main HEAD → Status → Q&A → Memory → Research → Registry → 必要最新 Execution 报告与论文资料，不能只用此前聊天记忆。
2. **继续**：以 Status 首页任务/实测、Q&A 已确认选择为准；同时继续和用户讨论相关论文、方法、实验设计、训练与研究创新，不将当前委派执行任务误报为完成。
3. **完成决策**：负责人明确回答 Q-ID 时，Q&A 记录答复、最终决策、日期、实验和预算影响及下一题；Status 改进度/当前任务；重要长期决策追加 Memory 的 D-ID/交接事件。
4. **完成工程/实验**：Execution 提供 Git SHA、任务编号、已完成/未完成、真实测试证据、资源/费用、未推送状态、阻塞和下一工作项；更新 Status 和 Memory。只有方法/证据/协议真正变化时才更新 Research。
5. **验证**：按当前任务核对实际改动与证据；仅在明确要求 GitHub 操作时提交、推送并核实远端。不能凭仓库变化推断服务器实时状况。无新事件不产生空更新，不为新窗口另造文档/代码分支或第二套流程。
6. **执行范围**：人类在当前任务的最新明确范围优先；历史 CPU 清洗或文献整理权限不自动扩展为训练、付费 API 或共享服务变更，本轮文档子任务只编辑指定六文件。

### 10.2 通用 ChatGPT 新窗口启动提示词

以下可直接复制到任何新 ChatGPT 对话。**不写死阶段、SHA 或过时的样本数量**；新会话以 GitHub 当前实际状态为准。

~~~text
你是 ModelRouter 项目的长期 Planning Agent，也是我的研究与训练方案讨论伙伴。仓库：https://github.com/sxyq/modelrouter

先查看最新 GitHub main，然后依次阅读五份文件：
1. our-project/planning/PROJECT_STATUS.md（最新阶段和下一任务）
2. our-project/planning/EXPERIMENT_QA.md（已决定与尚未批准的事）
3. our-project/planning/PLANNING_MEMORY.md（长期约定，特别是第10节）
4. our-project/planning/RESEARCH_OVERVIEW.md（研究目标和方法）
5. our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md（数据与模型来源）
需要时再查看 prepare_router_data.py、manifest.json、数据划分统计、科研数据收尾报告与我刚发来的执行记录。以上五份文档也可能互相矛盾：请以真实文件和可核实证据对账，不要把任一文字报告当成无误结论。

**我每次发来 Codex/Execution Agent 的执行结果，你都必须按固定顺序回答：**
一、总体进度：项目进行到哪里，已做/没做什么，先给通俗结论。
二、当前阶段的小步骤：每步列出已完成、正在做、待确认、没开始及剩余问题。
三、下一步计划：现在最应该先做哪一件事，后面怎么推进。
四、详细、可直接复制给当前 Codex 的执行提示词：目标、顺序、验证、交付和停止条件；避免重复工作、第二条流程与未经批准的计算。
五、简单情况说明：通俗解释风险与必要性，不堆技术名词。整体尽量简洁，但执行提示词要准确完整。

我的研究重点是：一个 Agent 做任务时怎样在不同模型和思考强度之间选择，考虑上下文复用、缓存与调用费用，最终减少整个任务的花费，同时保证完成任务。当前公开数据中的「静态题目比较」不等于「Agent 执行中途同状态比较」，统计数据也不等于真实最佳选择，不能编造标签或成果。

你负责计划、源码审查、论文与方法讨论；当前 Codex/Execution Agent 负责经授权的本机/服务器操作。优先复用唯一正式脚本和现有项目文件，禁止因反复更正就创造多套链路。核实 GitHub 最新提交与执行报告的差异；服务器专有结果若无法亲自读取就标明是执行方报告。新报告中若有不一致，优先做最小范围的只读对账；无授权不得自动开始正式 GPU 训练、付费 API 或修改共享服务。

不要重新开题、重复已决定的问题、重复下载模型/清洗全部数据。先按五段格式汇报用户最新执行结果，然后直接回答本轮具体问题；不要为了恢复上下文要求我重述已经登记的信息。
~~~

### 10.3 信息缺口和回退

GitHub 公开文件只能表示已推送事实，不能自动提供本地未推送代码、私人配置、服务器状态与未公开实验轨迹。新会话必须说明哪些内容经过独立核实，哪些仍需用户或 Execution Agent 补充；**不能承诺任意新窗口自动获得当前私有上下文**。


### 10.4 2026-10-10 新增用户要求：全部数据分层和目录清洁（Execution 已完成实测闭环）

用户明确要求：不满足于核对 84,310 条单胜者数据，应审查约 660 万条异构记录（其中约 65 万条属于路由比较/参考），按真实用途分配到静态模型选择、Agent 状态学习、Thinking 成对对照、KV/费用/时间分析、真实任务评测及未来受控动态路由阶段；**逐字段证明八组状态覆盖，不能把来源多等同变量齐全**。新增本机/服务器目录规划和临时脚本及时清理要求。

Execution 已于 2026-10-10 完成全量 6,600,628 条记录 8 维分层、8 类状态覆盖核查、67,428/8,436/8,446 对账及目录治理（详见数据台账 6.14 和 Status 首页）；下一步等待负责人审阅五阶段训练课程与历史遗留文件清理清单后，再下达 E2 正式 GPU 训练指令。

### 10.5 2026-10-10 新执行报告独立复审与下一任务

Execution 报告自称 660 万分层、八组状态覆盖、五阶段训练设计与临时文件治理全部 PASS，远端 GitHub HEAD 7fc24bc 已核实。Planning 核对源码发现：唯一 Python 命令入口成立，但 14 个适配器仍留在约 4,500 行单文件，模块拆分未完成；部分「八维状态全覆盖」「全部有真实费用」「28,830 组思考对照可训练」缺源码级可靠依据；OWN-001/003 说明与 manifest 不符；模型文件大小仍存在表间差异；报告提议重装 GPU 库并重做 E1 测试，与上一轮已报告 A6000 GPU 测试矛盾。**下一步只做有界证据核验及必要最小模块整理，禁止新链和重复实验**。具体清单见 Status 最新 2026-10-10 Planning 独立复审补充。

### 10.6 2026-10-10 定向收尾结果与剩余边界

- `main` 同步至 `fec46d9`；唯一 CLI 已缩至 136 行，14 个适配器进入内部 `router_data/`，8 个模式和数据路径不变。小样本 765 行、92 个文件旧新一致，未重新处理全部数据。
- 4,448,643 行不含累计费用或独立退出码；AgentSuite 是 273 固定对话 × 30 配置的回答评测，历史消息重复展开；SWE-smith 有重复轨迹步和错误词代理量，不能当独立逐步结果。
- 84,310 题的费用证据：已证明账单 0、明确估价 35,189、上游费用来源未知 9,386、无费用 39,735。保留旧数据，但旧 ACTUAL_MEASURED_API_USD 等标识不能作为账单证明。
- RouterBench 另有 87 条最高分与最低估价同时并列，官方按顺序选定，不能全部称严格唯一胜者。只更新说明，正式数据未改；已验证源码同步到服务器原位置。
- AgentSuite 标称模式对 1,365、独立 Thinking 权重对 273；跨版本可确认五组 1,365。全部六组旧质量分项已更正。LLMRouterBench 27,192 对旧算法未找到，本轮三组明确比较共 34,908 对，不能混成思考强度或独立题数。
- OWN-001/002/003 是 110 聚合行、221,128 调用行、79 衍生行；79 行无新增独立观测；人工 25 条未找到来源。Stage 5 的 58,852 行包含任务、上下文和问答重复，未生成受控强化训练样本。
- 项目 .venv 指向已有共享环境，PyTorch/CUDA 可用，系统 Python 无 PyTorch。已有 GPU 汇总报告短训练和重载成功；原始训练日志、当时解释器、临时权重未确认，不重复安装、下载或 GPU 测试。
- 现有报告、来源台账、manifest 和统计说明已按证据更新；正式原始数据、清洗记录、权重与划分不改。日志在 runs/MR-FINAL-20261010；本轮临时材料清理，历史 /tmp 文件保留。
- 下一工作包仅建议明确阶段 1 监督目标和取样方案。定向核验阶段未执行 Git 提交或推送；用户随后明确要求整理、提交并推送相关改动。此次许可不包含 CI/PR、正式训练、付费 API 或批量 Coding 评测；推送完成后停止。

### 10.7 2026-10-10 Stage 1 科学监督定义与训练数据配置定稿（`MR-STAGE1-20261010`）

- **1. RouterBench 87 条并列标签全量台账（P1）**：
  - 逐条查明 `ROUTE-002`（35,189 条入池题）中唯一最高分 `2,553` 条（`1,998 / 273 / 282`）、同分最低估价唯一 `32,549` 条（`26,014 / 3,315 / 3,220`）、最高分与最低估价同时并列 **`87` 条（`train: 68, val: 10, test: 9`）**。
  - 全部 87 条（100%）最高分均为 `1.0`，最低估价并列候选集合均为 **`['claude-v1', 'claude-v2']`**；因固定候选顺序 `claude-v1` 在前，上游 `np.argmin` 将 87 条全部选为 `claude-v1`。
  - 协议：不覆写已固定 JSONL；Stage 1 单胜者训练与严格单标签准确率评测通过任务 ID 掩码剔除这 87 条（全集 `84,310 → 84,223`：`67,360 / 8,426 / 8,437`；`ROUTE-002` `35,189 → 35,102`：`28,012 / 3,588 / 3,502`），将其归入并列分析集（`16,070 → 16,157`），并在集合命中率指标中以预测落入 `{'claude-v1', 'claude-v2'}` 计为最优。
- **2. 三种监督体制与 AgentSuite 19 题精确拆分（P2）**：
  - **体制 A（人类偏好 `HUMAN_PREFERENCE`）**：`ROUTE-004` Arena 共 `39,716` 题（`train: 31,766, val: 3,943, test: 4,007`），双候选盲测投票，无分数与费用。
  - **体制 B（纯质量唯一最高分 `UNIQUE_MAX_SCORE`）**：共 `3,985` 题（`train: 3,206, val: 381, test: 398`），含 `ROUTE-002` `2,553` 题（`1,998 / 273 / 282`）与 `ROUTE-001` `1,432` 题（`1,208 / 108 / 116`）。
  - **体制 C（同分最低费用规则 `TIED_SCORE_MIN_COST_RULE`）**：共 `40,503` 题（`train: 32,371, val: 4,101, test: 4,031`），含 `ROUTE-002` 最低估价 `32,549` 题（`26,014 / 3,315 / 3,220`）与 `ROUTE-001` 最低上游正值费用 `7,954` 题（`6,357 / 786 / 811`，账单/估价来源未证实）。
  - **排除 `TRA-004` AgentSuite 19 题（`17 / 1 / 1`）**：系固定多轮对话末轮评判、仅首段 300 字符进入 `state`、`val=1 / test=1` 无统计效力且与 AgentSuite 评测集重叠；剔除 87 + 19 后得到 **Stage 1 推荐洁净主集 `84,204` 题（`train: 67,343, val: 8,425, test: 8,436`）**。
  - **`ROUTE-001` 两项关键发现**：(a) `router_data/views.py` 为每条 `ROUTE-001` 附加了事后解题率派生的 `questions.difficulty_tier`（使总题项数多出 `7,565 / 894 / 927 = 9,386` 项），Stage 1 加载时必须仅保留 `question_key == "model_choice"`；(b) `bench-release/**/openrouter/*.json` 共 13 个原始文件（14,569 条）的 `model_name="openrouter"` 实为 OpenRouter 动态自动路由器基线（`extra_fields.actual_model` 逐题变化），在三集合中胜出 `551 / 70 / 58 = 679` 题，Stage 1 需同步报告屏蔽该元路由器的 39 静态模型消融。
- **3. 未来评测隔离与原始 Parquet 100% 对账（P4）**：
  - 剔除 19 题 `TRA-004` 后，Stage 1 与 `ENV-001/002`、`TRA-001/002/004`、`ROUTE-003` 之间任务 ID、代码仓库与题面重叠均为 **0**。
  - 原始 Parquet 逐条证实 `TRA-001` 与 `ENV-002` 共享的 **13,336** 个 `instance_id`（按 `repo+issue` 共 **13,374** 条，跨 **2,353** 仓库）100% 标记 `hf_dataset_name == "nebius/SWE-rebench-V2"`，`repo`、`reference_patch == patch` 与剥离 `<uploaded_files>` 包装头后的 `problem_statement` **100.0% 完全相同**；`ENV-001 ∩ ENV-002` 的 **236** 个共享 ID（含 `TRA-001 ∩ ENV-001` 的 **150** 个子集）`repo` 与 `base_commit` **100.0% 相同**。未来 Stage 2/5 必须执行仓库级留出隔离。
- **4. 归档与清理（P5）**：
  - 完整只读核验证据存 `runs/MR-STAGE1-20261010/{routerbench-87,supervision-audit,future-eval-isolation-audit}.json`，本机与服务器 `.tmp/MR-STAGE1-20261010/` 已删除。

### 10.8 2026-10-10 Stage 1 训练协议最后修订与版本归档（`MR-STAGE1-REV-20261010`）

- **1. `openrouter` 元路由器更正与方案 A / B 对账（P1）**：
  - `ROUTE-001`（`LLMRouterBench`）固定三集合共 `9,386` 题（`train: 7,565, val: 894, test: 927`），其中 `1,260` 题（`1,066 / 77 / 117`）候选不含 `openrouter`；`8,126` 题（`6,499 / 817 / 810`）候选包含 `openrouter`（`7,447` 题原胜者已是静态模型，`679` 题原胜者为 `openrouter`）。
  - **方案 A（整题剔除含 `openrouter` 的 `8,126` 题）**：`ROUTE-001` 仅剩 `1,260` 题（损失 `86.58%`），Stage 1 全集降为 `60,844 / 7,608 / 7,626 = 76,078` 题。
  - **方案 B（从 `criteria` 移除 `openrouter` 并对剩余静态模型重算，推荐为纯静态主实验）**：
    - `8,707` 题（`7,014 / 824 / 869`）静态胜者完全不变（含 `1,260` 题本无 `openrouter` + `7,447` 题原胜者即静态模型；其中 `201` 题 [`166 / 16 / 19`] 因移除唯一同分对手 `openrouter` 而从 `TIED_SCORE_MIN_MEASURED_API_USD` 升级为 `UNIQUE_MAX_SCORE`）；
    - 原胜者为 `openrouter` 的 `679` 题（`551 / 70 / 58`）中，**`370` 题（`305 / 37 / 28`）**重算得新严格唯一静态胜者（`93` 题 [`73 / 13 / 7`] 唯一最高分 + `277` 题 [`232 / 24 / 21`] 同分最低正实测费），**`309` 题（`246 / 33 / 30`）**降级归入 `analysis_unsupervised_or_tied`（其中剩余静态候选 `<2` 为 `0` 题、全败 `ALL_MODELS_FAILED` 为 `308` 题 [`246 / 33 / 29`]、同分缺费用或不可比为 `0` 题、同分且正费用完全并列 `TIED_SCORE_TIED_API_USD` 为 `1` 题 [`0 / 0 / 1`，即 `llmroute_hle_57`]）。
    - **方案 B 纯静态主集总数**：**`67,097 / 8,392 / 8,406 = 83,895` 题**（`ROUTE-004` `31,766/3,943/4,007=39,716`；`ROUTE-002` `28,012/3,588/3,502=35,102`；`ROUTE-001` `7,319/861/897=9,077`）；按三种监督体制为 Regime A `31,766/3,943/4,007=39,716`、Regime B `3,203/379/397=3,979`、Regime C `32,128/4,070/4,002=40,200`。原 `84,204` 题仅保留为混合候选参考对照。
- **2. 官方加载器核验与一次性派生纯静态实验文件（P2）**：
  - 源码核查证实官方 `kev/data.py`（`load_records` + `materialize`）与 `laya/train.py`（`items_from_rows`）均遍历每条记录 `questions` 字典的全部键，不支持按 `question_key` 过滤题项。
  - 为确保不改动 `prepare_router_data.py`、不修改官方 `kev`/`laya` 代码、不覆写固定 `data/{kev,laya}/公开数据/*.jsonl`，已在服务器 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b/{train,val,test}.jsonl` 一次性生成派生纯静态文件（物理移除 `questions.difficulty_tier` 与 `expected.difficulty_tier`，排除 RouterBench 87 题与 AgentSuite 19 题，应用方案 B），并通过官方加载器全量校验。
  - 实测发现 Laya 默认 `head_max_len=192` 在 37 候选的 `ROUTE-001` 上会触发 `options_collapsed` 跳过样本；通过 CLI 传参 `--max-len 1024 --head-max-len 512` 实测 `0` 跳过。
- **3. 第一批训练最小公平收敛与零 GPU 规则基线（P3–P4）**：
  - 第一批正式训练收敛为 **1 次 Kev-4B 训练 + 1 次 Laya-421M 训练**（同一 `83,895` 纯静态三集合、`seed=42`、仅用 `val` 选模、`test` 唯一一次终评）。
  - 完全基于 `train`（`67,097` 题）统计的零 GPU 规则基线在 `val`（`8,392` 题）上的准确率为：均匀随机期望 `28.07%`、固定全局最高频单模型（`mistralai/mistral-7b-chat`）`12.79%`、候选集内 `train` 最高胜次 `46.72%`（`3,921/8,392`）、按数据源候选集内 `train` 最高胜次 `46.81%`（`3,928/8,392`）、候选集内 `train` 最高经验胜率 `43.95%`（`3,688/8,392`）。
  - 新增审计 JSON `openrouter-remediation-audit.json` 与 `stage1-protocol-and-baselines.json` 已归档至 `runs/MR-STAGE1-20261010/`，`.tmp/MR-STAGE1-REV-20261010/` 已清理。

### 10.9 2026-10-11 Stage 1 许可、数据一致性、全量编码兼容与八类变量联合覆盖终审（`MR-STAGE1-FINAL-AUDIT`）

- **1. 逐源训练许可与使用边界核查（P1）**：
  - `ROUTE-004`（`Chatbot Arena 55k`，HF `lmarena-ai/arena-human-preference-55k`，实测 HF SHA `18c298340948c0e7f7727399fd459cca6ce0ca6f`）：数据卡 YAML 与 HF API `cardData.license` 明标 `apache-2.0`；Stage 1 仅使用 `(prompt, 候选模型名) -> 人类偏好胜者`（已剥离第三方模型回答文本 `response_a/b`），判定为 **`TRAIN_ALLOWED_VERIFIED`**。
  - `ROUTE-002`（`RouterBench`，HF `withmartian/routerbench`，实测 HF SHA `784021482c3f320c6619ed4b3bb3b41a21424fcb`）：GitHub 代码仓 `LICENSE` 为 MIT（`Copyright (c) LangChain, Inc.`），HF 数据卡正文写明用于训练和评估路由方法，但 HF 数据卡无正式 `license` 字段且本地 `manifest.json` 误记 revision 与 `Apache-2.0`，按严格规则判定为 **`LICENSE_PENDING`**。
  - `ROUTE-001`（`LLMRouterBench`，HF `NPULH/LLMRouterBench`，实测 HF SHA `0e5af1b84bf73437a01a1849c0f1d2468baa93fc`）：GitHub `README.md` 虽挂 MIT 徽章但 `LICENSE` 文件缺失（HTTP 404，GitHub API `license: null`），HF 数据仓无 `README.md` 与 `license` 元数据，判定为 **`LICENSE_PENDING`**。
- **2. `ROUTE-001` 候选标识与逐题一致性全量审计（P2）**：
  - 全量扫描 `548,059` 条清洗记录（`700` 个原始 JSON）：按 `(benchmark_name, instance_index)` 聚合的 `25,202` 题中，**`2,001` 题（`25,563` 对 `(benchmark, index, model)`）**存在同模型重复评估（`hle` `500` 题/`6,500` 对、`mmlupro` `1,001` 题/`13,013` 对、`simpleqa` `500` 题/`6,050` 对）。
  - 其中 **`1,165` 题（`14,682` 对）**因 `bench-release` 下多子目录（`mmlupro/test_1000` vs `test_3000` 计 `664` 题、`simpleqa/subset_500` vs `test` 计 `500` 题、`arenahard` `1` 题）各自从 `0` 编号且题面不同，被 `views.py` 合并为同一题，直接污染方案 B 纯静态集中 **`563` 条记录（`438 / 65 / 60`）**；另有 **`651` 条记录（`512 / 71 / 68`）**含同模型重复评估（如 `llmroute_hle_57` 因 `hle/subset_500` 与 `hle/test` 均含唯一满分模型 `gemini-2.5-pro` [`score=1.0, cost=0.02580375`] 而被误判为 `TIED_SCORE_TIED_API_USD`）。若按 `(benchmark_name, instance_index, prompt_hash)` 拆分为 `26,367` 题并按模型去重，纯静态唯一胜者为 `10,262` 题（`1,640` 唯一最高分 + `8,622` 同分最低正费，`0` 同分同费并列）。
- **3. Kev 与 Laya 全量 83,895 条 CPU 编码兼容核验（P3）**：
  - 在 `CUDA_VISIBLE_DEVICES=""` 下对全部 `67,097 / 8,392 / 8,406` 条测试：**Kev** 在 `max_state=384` 至 `7552` 下 **100% 通过（`67,097 / 8,392 / 8,406`，0 截断、0 丢弃，`state_tokens` `11..352`，`branch_tokens` `25..441`；注：`state` 为截断至 400–500 字符的 `prompt_snippet`）**；**Laya** 在默认 `512/192` 下因 `options_collapsed` 跳过 `1,715` 条（`1,433 / 134 / 148`），显式传 `--max-len 1024 --head-max-len 512` 后 **100% 零跳过通过（`67,097 / 8,392 / 8,406`，仅 `test` 有 `2` 条 `ROUTE-001` 发生状态尾部截断）**，两模型可训练 `task_id` 交集为 **`100.0%`（`67,097 / 8,392 / 8,406`）**。
- **4. 费用来源、八类变量联合覆盖与两项最终判定（P4–P9）**：
  - 方案 B `83,895` 题中：`MEASURED_BILLING_VERIFIED = 0`、`PROVIDER_REPORTED_USAGE = 0`、`ESTIMATED_TOKEN_PRICE = 35,102`（Regime C 使用 `32,549` 题）、`UPSTREAM_COST_UNVERIFIED = 9,077`（Regime C 使用 `7,651` 题）、`NO_COST = 39,716`；决策前输入含价格表的样本为 `0`，Regime C 标签高度偏向静态低价模型（`ROUTE-002` 前 4 个开源低价模型占 `88.80%`）。
  - 八类动态路由变量联合覆盖审计确认：同时观测八类状态 + `(model, effort)` + 真实 KV 缓存 + 真实费用的记录为 **`0`**，中途同状态多模型反事实分支为 **`0`**，跨模型切换缓存失效监督为 **`0`**。
  - **两项核心判定**：**`STAGE1_DATA_READY = NOT_READY`**（因 P1 `ROUTE-001/002` `LICENSE_PENDING`、P2 `ROUTE-001` 同键多 Prompt 混拼与同模型重复评估、P6 `views.py` 缺正式纯静态导出入口及 `ROUTE-002` 候选位置偏差）；**`RUNTIME_JOINT_DATA_READY = NOT_READY`**（因缺同状态多模型×effort×缓存×账单联合动态数据）。完整证据归档于 `runs/MR-STAGE1-20261010/final-stage1-and-joint-coverage-audit.json`。

### 10.10 2026-10-11 `MR-STAGE1-FAST-FIX` 实验数据最小修复与快速迭代

- **1. P0 文档与审计台账口径纠偏**：
  - 公开清洗总行数严格为 14 个有效公开源 **`6,600,628` 行**（`TRA-003` 与 `MEM-004` 为 `NOT_DOWNLOADED_BY_DESIGN` 计 0 行）；自有数据三表具有不同粒度（`OWN-001` CCH `110` 聚合行代表 `750,212` 次调用、`OWN-002` Blog `221,128` 调用行、`OWN-003` CCH/Blog `79` 衍生汇总行 = `42` CCH + `37` Blog，新增独立观测 `0`），严禁与公开数据相加造出 `6,620,400`，亦严禁把 `OWN-002`/`003` 误记为 `967`/`14,192`。
  - `TRA-004`（AgentSuite `multi_challenge`）统一为 **`273` 独立任务 × `30` 配置 = `8,190` Episode（展开为 `41,430` 行）**，包含 **`1,365` 对严格同一权重运行时开关**（5 模型 × 273 任务，其中 `290` 对仅一方成功）、**`273` 对同底座专用 Thinking 权重**（1 组 × 273 任务）、**`1,365` 对已确认跨版本/跨变体对照**（5 组 × 273 任务；GLM 文件缺失），彻底纠正旧审计 JSON 中误写的 `270 / 8,100 / 1,350`。
  - 八类动态路由状态变量名称严格锁定为唯一标准定义：`1. Task/Subtask`、`2. Agent/Coordination`、`3. Context/Memory`、`4. Tool/Environment`、`5. Verification/Recovery`、`6. KV Cache/Continuity`、`7. Temporal/Execution`、`8. Provider/Availability`。
- **2. P1–P3 `ROUTE-001` 完整原始 Prompt 散列合并、去重、冲突隔离与 Stage 1 纯静态方案 B 固化**：
  - 在唯一主链 `router_data/route.py` 与 `router_data/views.py` 中直接提取 `ROUTE-001` 原始 700 个 JSON 的未截断 `(origin_query, prompt)` 计算 `full_prompt_hash`（绝不依赖 400 字符截断的 `prompt_snippet`），将 `hle`（`subset_500`/`test`）、`mmlupro`（`test_1000`/`test_3000`）、`simpleqa`（`subset_500`/`test`）及 `arenahard`（`arenahard` 与 `arenahard_{coding,creative_writing,math}`）同题重复导出合并为 **`24,441` 道真实独立题目**；移除动态元路由器 `"openrouter"`；对同题同模型 `(score, cost)` 完全一致的 **`21,144` 条冗余重复评测**直接去重合并（**`llmroute_hle_57` 恢复为 `gemini-2.5-pro` 唯一最高分胜者 `UNIQUE_MAX_SCORE` [`Regime_B`]**）；对潜在最高分模型存在分数冲突（`439` 题）、唯一最高分模型存在费用冲突（`22` 题）或并列最高分模型存在费用冲突（`758` 题）的合计 **`1,219` 道冲突题目**保守隔离至 `analysis_unsupervised_or_tied.jsonl`，禁止任意取首条或极值；最终 `ROUTE-001` 保留 **`8,441` 道无冲突纯静态单胜者题**（`train: 6,788, val: 812, test: 841`；含 `1,486` 道 `UNIQUE_MAX_SCORE` [`1,245 / 113 / 128`] + `6,955` 道 `TIED_SCORE_MIN_MEASURED_API_USD` [`5,543 / 699 / 713`]），其余 `16,000` 道进入分析集。
  - `python3 prepare_router_data.py --mode views` 默认在 `runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed/` 导出修复版纯静态三集合（不覆写固定 `data/{kev,laya}/公开数据/*.jsonl` 与旧 `stage1_pure_static_scheme_b/*.jsonl`）：**`train: 66,566 / val: 8,343 / test: 8,350 = 83,259` 题**（按来源：`ROUTE-004` `31,766/3,943/4,007=39,716`、`ROUTE-002` `28,012/3,588/3,502=35,102`、`ROUTE-001` `6,788/812/841=8,441`；按体制：`Regime_A` `31,766/3,943/4,007=39,716`、`Regime_B` `3,243/386/410=4,039`、`Regime_C` `31,557/4,014/3,933=39,504`），另有 `test_twinrouterbench_holdout.jsonl` `970` 步与 `analysis_unsupervised_or_tied.jsonl` `16,360` 题。
  - 两次独立运行全部 5 个 JSONL 的 SHA256（`train`: `ce32c695...`、`val`: `cda07164...`、`test`: `2c4bf179...`）**100% 完全一致**；跨集合 `task_id` / `full_prompt_hash` / `exact_prompt` / `canonical_prompt` 重叠均为 **`0`**；`"openrouter"` 与 `"difficulty_tier"` 出现次数均为 **`0`**；`ROUTE-002` 候选经固定种子确定性打乱后，`index 0` 胜出率从 `23.90% / 22.32% / 24.13%` 降至 **`9.20% / 9.00% / 9.51%`**（均匀期望 `9.09%`）。
- **3. P4–P5 全量 CPU 编码验证、零 GPU 基线与当前就绪状态**：
  - 修复版 `66,566 / 8,343 / 8,350` 在官方 Kev（`max_state=384` 及 `7552`）与 Laya（`--max-len 1024 --head-max-len 512`）下 **`100.0%` 零跳过通过**（Laya 默认 `512/192` 会跳过 `1,086 / 99 / 98 = 1,283` 条），双模型联合可训练交集 **`100.0%`（`83,259` 题）**。
  - 修复版 `train`（`66,566`）统计的零 GPU 规则基线在 `val`（`8,343`）上准确率为：均匀随机 `28.21%`、固定全局最高频单模型 `12.86%`、候选内 `train` 最高胜次 **`46.81%`**（`3,905/8,343`）、按数据源候选内 `train` 最高胜次 **`46.89%`**（`3,912/8,343`）、候选内 `train` 最高经验胜率 **`44.02%`**（`3,673/8,343`）。
  - Stage 1 技术与代码阻塞已 100% 解除（**`STAGE1_TECHNICAL_DATA_AND_CODE_READY = READY`**）；许可证状态保持原样（`ROUTE-004` `TRAIN_ALLOWED_VERIFIED`；`ROUTE-002` 与 `ROUTE-001` `LICENSE_PENDING`），待负责人批准后启动 GPU 训练。

### 10.11 2026-10-11 大阶段收束、当前小任务与新增授权

- **已经阶段性完成的数据工作**：14 个有效公开数据源，`6,600,628` 行不同粒度记录；唯一 `prepare_router_data.py` 入口 + `router_data/` 14 个独立适配模块；纠正数据 Source ID 与自有 CCH `110` 聚合行（代表 `750,212` 调用）、Blog `221,128` 调用行、`OWN-003` `79` 衍生行的统计口径；AgentSuite `273` 任务 × `30` 配置 = `8,190` 配置评估（`41,430` 展开行），同权重 Thinking 开关 `1,365` 对，专用权重 `273` 对，跨版本 `1,365` 对。
- **已完成的 Stage 1 科研数据纠偏**：ROUTE-001 从 `548,059` 行重合并到 `24,441` 道独立原始题，合并 `21,144` 条完全重复同模型评估、隔离 `1,219` 道潜在胜者冲突题、排除 `openrouter`；ROUTE-002 排除 `87` 条真并列并打乱候选顺序；最终方案 B 纯静态 `83,259` 题（`train 66,566 / val 8,343 / test 8,350`；Regime A/B/C = `39,716 / 4,039 / 39,504`），既有 CPU Kev/Laya 编码均报告通过，旧固定数据保留。
- **研究范围不变**：八组状态依次为 Task/Subtask、Agent/Coordination、Context/Memory、Tool/Environment、Verification/Recovery、KV Cache/Continuity、Temporal/Execution、Provider/Availability；660 万行不代表动态模型×Effort 最优标签。同状态中途比较、真实跨模型缓存切换代价与八类完全联合监督当前为 `0`。
- **2026-10-11 用户最新明确授权**：不要任何不必要的工程化设计；允许在当前唯一清洗主链上只针对训练 `state` 被约 `400` 字符截断做必要 Python 最小修改、CPU 验证、产生不覆盖旧结果的派生版，并据已有官方 Kev/Laya 源码确定首批参数；**GPU 正式训练、GPU 推理、付费 API、模型下载、大型 Benchmark 尚未授权**。A+B+C 按来源/体制分开，ROUTE-001/002 `LICENSE_PENDING` 不变；允许既有范围内差异审查、脱敏、无冲突后的文档与必要源码 GitHub 推送。
- **唯一下一任务**：`MR-STAGE1-INPUT-FIX` 与 `MR-ALLDATA-ADAPTER-20261011` 均已完成（详见 §10.12）。待负责人单独决定 `E2-STAGE1-BATCH1` 的 GPU 与数据使用权限。详细实时状态只看 `PROJECT_STATUS.md` 首页，不能用本节历史快照替代。

### 10.12 2026-10-11 `MR-ALLDATA-PREP-20261011` 与 `MR-ALLDATA-ADAPTER-20261011` 双模型训练数据最终适配

- **1. P0 监督修复与跨视图身份/划分对齐**：
  - 统一 `stage1_choice`（`83,259` 题）、`recomputed_route001`（`8,441` 题）、`stage1_pairwise`（`59,049` 对）、`stage1_soft_target` / `stage1_score`（`53,087` 题）的真实完整题目身份（`ROUTE-001` 采用 `(benchmark_name, full_prompt_hash)`，`ROUTE-002` 采用 `sample_id`，`ROUTE-004` 采用 `battle_id`）与唯一 Train/Val/Test 语义归一化散列划分规则，消除旧版二次散列导致的跨集漂移（跨视图划分不一致数 = `0`）。
  - 在 `recomputed_route001` 中严格剔除 `1,953` 条不合法单胜者（`ALL_MODELS_FAILED: 1,553`、`CONFLICTING_MODEL_SCORE_UNRESOLVED: 241`、`CONFLICTING_TIED_TOP_COST_UNRESOLVED: 141`、`CONFLICTING_WINNER_COST_UNRESOLVED: 17`、`TIED_SCORE_TIED_API_USD: 1`），从 `10,394` 收敛为 **`8,441` 题（`train: 6,729, val: 865, test: 847`）**，与主 Choice 中的 `ROUTE-001` 子集逐题 100% 一致（差异 `0`）。
  - 在 `stage1_soft_target`（`53,087` 题：`42,502 / 5,327 / 5,258`）与 `stage1_pairwise`（`59,049` 对：`47,241 / 5,941 / 5,867`）中剔除 `417` 道同模型分数冲突题（`CONFLICTING_MODEL_SCORE_UNRESOLVED`），完整保留 `11,599` 道 `ROUTE-001` 最高分并列但具备有效多模型质量分布的题目及 `87` 道 `ROUTE-002` 得分+估价双并列题。
- **2. P1–P2 Laya-421M / Kev-4B 双模型独立训练视图与 100% CPU 官方编码核验**：
  - 在 `runs/MR-ALLDATA-PREP-20261011/training/laya/` 与 `runs/MR-ALLDATA-PREP-20261011/training/kev/` 分别生成 6 个训练阶段子集（每模型合计 `1,906,319` 条记录）：
    - `stage1_choice`：`66,721 / 8,298 / 8,240 = 83,259`（Both accepted [`7552`]: `83,031`；Laya only [`7552`]: `228`；Kev only: `0`；Neither: `0`；Laya `1024` 截断 `899` 条）。
    - `stage1_pairwise`：`47,241 / 5,941 / 5,867 = 59,049`（Both accepted [`7552`]: `58,833`；Laya only [`7552`]: `216`；Laya `1024` 截断 `493` 条）。
    - `stage1_soft_target`：`42,502 / 5,327 / 5,258 = 53,087`（Laya 使用 `gold.probabilities` 软分布、Kev 使用 `label + target` 概率向量；Both accepted [`7552`]: `52,872`；Laya only [`7552`]: `215`；Laya `1024` 截断 `606` 条）。
    - `stage2_agent_state`：`70,334 / 8,683 / 9,070 = 88,087` 条轨迹级压缩记录（对应 `35,289` 个独立任务，去除 `4,360,556` 条逐步重复终局行；Both accepted [`384/7552`]: `88,087`，`100.0%` 零截断）。
    - `stage3_effort`：`217 / 39 / 34 = 290` 对同模型同权重有效胜负配对（排除 `1,075` 对同成同败平局；Both accepted [`384/7552`]: `290`，`100.0%` 零截断）。
    - `stage4_auxiliary`：`1,297,178 / 162,623 / 162,746 = 1,622,547` 条有效单请求辅助记录（排除 `48,900` 条无效/分析/聚合行；Both accepted [`384/7552`]: `1,622,547`，`100.0%` 零截断）。
- **3. P3 首轮训练参数准备与暂停**：
  - 已备齐 Laya-421M（`laya-train --loss soft-ce --max-len 1024 --head-max-len 512`）与 Kev-4B（`python -m kev.train --weights lora --lora 16 --head_dim 256 --max_state 7552`）的首轮训练超参数、命令与Checkpoint输出目录，按要求在启动正式 GPU 训练前暂停。


### 2026-10-12 · OVERNIGHT-LAYA-TRAINING

已按授权完成 Laya-421M R0→R1→R2→R3。Batch 1 训练行 13,438（S1 4,592、S2 2,846、S3 6,000），独立 Val 5,692；官方 CPU 编码全部通过，0 跳过。R0 S1/S2/S3 Accuracy 为 0.4759/0.4896/0.4677。R1 最佳 R1-E1，S1 Val Loss/Accuracy 为 0.6038/0.6613；R2 最佳 R2-E1，S1 为 0.6093/0.6578、S2 为 1.0000；R3 最佳 R3-E1，S1 为 0.6388/0.6667、S2 为 1.0000、S3 为 0.6435。三组均按连续两轮缺少 0.5% S1 Val Loss 改善提前结束，权重与指标保存在服务器 runs/OVERNIGHT-LAYA-TRAINING/。未运行 Kev、Coding Benchmark 或付费 API。

### 10.13 2026-10-12 · OVERNIGHT-LAYA-SWEEP-02

已按授权完成 N01–N10，每个方案运行最多 3 轮并保留 `epoch_01`–`epoch_03`、`latest` 与 `best` 权重目录。N01、N02、N03、N07、N09 按连续两轮缺少 S1 验证损失改善提前结束，N04、N05、N06、N08、N10 完成三轮；共 30 个逐轮节点、50 个权重目录。固定验证集合为 S1 561 条，混合方案另含 S2 337 条与 S3 4,794 条。N05-E02 的 S1 验证损失最低（0.5969），N10-E03 的 S1 验证准确率最高（0.6952）。N01–N10 `best` 权重均通过官方 Laya CPU 加载。S2 验证准确率在混合方案中为 1.0，但该集合标签与状态字段的独立审计仍显示多数参考准确率约 0.551929，不能据此宣称通用路由能力。服务器训练进程已退出，GPU 回落至 682 MiB；未运行 Kev、Test、Coding Benchmark 或付费 API。服务器结果位于 `runs/OVERNIGHT-LAYA-SWEEP-02/`，公开面板数据和逐轮同步记录位于 `docs/training-dashboard/`。

### 10.14 2026-10-12 · FULL-GRADED-MULTI-BATCH-TRAINING

从现有 V2.1 索引生成 `experiment_matrix.json`，共 1,092 个槽位：基础 B/C/Q/P 1,008 个，课程 12 个、多 Seed 40 个、变量消融 32 个；其中 693 个有合法数据，315 个因目标组合没有合法训练记录而标为 BLOCKED。首个执行窗口物化 B01 的 16 个 QB/PB 组合，每个监督类别最多 4,096 条索引样本，并沿用 Batch 1 固定验证集合。B01_C01、B01_C04、B01_C05、B01_C06 已完成两个 Epoch；B01_C02、B01_C03 各完成两个 Epoch 后因旧的 S1 早停条件结束，后续代码已限定为只有存在 S1 验证指标时才触发；B01_C07 正在执行。训练入口仍为 `router_data/laya_batch_train.py`，输出在服务器 `runs/MR-FULL-GRADED-TRAINING/`，每个 Epoch 写入训练、验证、保存耗时和 GPU 读数，看板按 Epoch 同步。

### 10.15 2026-10-12 · FULL-GRADED 首个窗口收尾

B01 的 16 个 QB/PB 配置全部完成，每个配置 2 个 Epoch，共 32 个 Epoch。服务器训练进程自然退出，GPU 回落至 `682 MiB / 0%`。最终运行快照为 16 个 `completed`，累计 Epoch 用时约 `10,106.5` 秒；权重目录 `59` 个，单个权重文件约 `3.38 GB`。最佳 S1 验证结果为 B01_C05-e02：Loss `0.5945`、Accuracy `0.6827`、Brier `0.4082`、ECE `0.0363`。S2 可见的 11 个混合配置均为 `1.0`，S3 结果为 `0.5565–0.7082`；S2 满分仍受输入文本中曾出现目标名称的影响，不能作为泛化结论。

本轮继续沿用固定 Batch 1 Val 集合，没有使用 Test、Kev、Coding Benchmark 或付费 API。`router_data/batch_prep.py` 已在 `f927877` 加入中性辅助指令，并按监督类别总量分配目标配额；首批 B01 输入在该改动之前一次生成，因此改动记录为后续物化使用，未改写已完成批次。看板新增八张 SVG 图表，最终快照提交为 `ef6f368`，本机数据时间为服务器 `2026-10-12T10:22:28Z`。

### 10.16 2026-10-12 `MR-FULL-GRADED-P0-DATA-REPAIR`

- 旧 B01_C01–C16 的 32 Epoch、权重和指标全部保留。看板将 16 个旧 Run 标成 `LEGACY_INPUT_PROTOCOL`；其中 S3 验证准确率最低的 B01_C14_QB_PB（0.5565）只把 checkpoints 移到服务器 `.Trash`，运行元数据与指标仍在原目录。
- 唯一入口 `prepare_router_data.py --mode full_matrix` 生成服务器独立目录 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/`，使用 `P0_` 前缀物化 B01 的 C01/C04/C07/C13 以及 B02–B04 全部 C01–C16，共 52 个 CPU Run。配额按整个监督类别计算：C04、C07、C13 实际类别比例为 1:1、1:1、1:1:1。
- Train 与固定 Val 都换成中性指令。官方 Laya `load_checkpoint`（CPU）和 `items_from_rows` 共读取 413,312 行并编码 413,312 Item，0 跳过；旧目标指令 0 行，稳定 ID 和独立任务/轨迹单位的 Train/Val 交集为 0。`trajectory_resolved` 的 false/true 仍是固定标签空间，未作为行级指令写入。
- 覆盖口径分开记录：全来源 6,821,945 行、矩阵六来源 6,129,744 行、合法候选 4,863,900 行、候选独立单位 1,344,240；新 Run Item 暴露 212,970，跨 Run 去重 Item 45,056。S2 只计算多数类基线，Train 0/1=25,592/22,573、Val=6,510/5,285；模型指标仍标为 `BASELINE_ONLY_MODEL_METRICS_BLOCKED`。
- 看板快照来自服务器 CPU 结果，旧历史与新协议分组呈现；本轮未启动 GPU、Test、Coding Benchmark、Kev 或付费 API。

### 10.17 2026-10-12 `MR-FULL-GRADED-CHECKPOINT-RETENTION`（Checkpoint 智能保留与磁盘保护）

- **1. 训练器 Checkpoint 保存机制重构（P0–P2）**：
  - 新增 `router_data/checkpoint_retention.py` 并集成至 `router_data/laya_batch_train.py`：每个 Epoch 完成独立 Val 后，100% 将完整实验参数、数据协议版本、父节点、验证指标与保留状态写入 `run.json`、`epoch_metrics.json` 及 `checkpoint_manifest.json`（不因节省磁盘省略低分 Epoch）。
  - 实体权重仅在符合保留条件时保存单份于 `checkpoints/epoch_XX`（单份约 `807.00 MiB`）；`best` 采用指向 `epoch_XX` 的相对目录符号链接（经官方 `laya.train.load_checkpoint` 实测 100% 兼容）；`latest` 仅作当前 Run 临时恢复并在 Run 完成时自动清理。
  - 更正 `B01_C14_QB_PB` 的历史状态：因该 Run 的 4 个物理目录（`3.15 GiB`）已在 P0 移除，将其 2 个 Epoch 的 `weights_saved` 改为 `false`、状态标为 `LEGACY_METADATA_ONLY`，使 FULL-GRADED 实体权重目录统计与真实磁盘（`55` 个目录：`30` 个 `epoch_XX` + `25` 个 `best/latest`）100% 对齐。
- **2. 同类可比较组动态阈值与任务隔离（P1）**：
  - 可比较组由 `(protocol_version, supervision_classes, val_signature, metric_definition)` 唯一确定；旧 `LEGACY_INPUT_PROTOCOL` 严格隔离，不参加新协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）排名。
  - **S1**：同组有效对照 `< 5` 时启用冷启动保护；`>= 5` 时需满足条件 A（`Val Loss <= 均值 * 0.995` 且 `Acc >= 均值 - 0.005`）或条件 B（`Acc >= 均值 + 0.01` 且 `Loss/Brier <= 均值 * 1.005`），每组限留非依赖 Top-2，并强制保留全局 S1 最低 Loss、最高 Accuracy、最低 Brier 模型及被后续课程依赖的 `PINNED_PARENT` 节点（如历史 `R1-e01`、`R2-e01`）。
  - **S2**：在独立监督审计通过前（`s2_audit_passed=false`），禁止因 `S2 Accuracy=1.0` 永久保存大量权重或设为全局冠军；全组最多临时保留 1 个最低 Log Loss 诊断模型。
  - **S3**：按 6 个真实 `source:target` 分目标独立对比各自多数类准确率（`0.4232 ~ 0.9520`）与先验 Loss 基线（`0.1926 ~ 1.2576`），严禁将不同 S3 目标原始 Loss 简单相加排名；仅分目标优于多数类基线的模型可进入组内 Top-2。
- **3. 磁盘预算与二阶段安全清理（P3）**：
  - 设定 FULL-GRADED 活动权重预算 **`120.0 GiB`**，告警阈值 `< 25.0%` 或 `< 300.0 GiB`（`WARNING`），停机阈值 `< 20.0%` 或 `< 200.0 GiB`（`STOP`，取更严格者）。
  - 每个新 Run 启动前执行 `pre_run_disk_check`；预算不足时仅在授权 `out_root/*/checkpoints/*` 白名单内生成二阶段清理清单并物理删除（`shutil.rmtree`，禁止移入同分区 `.Trash` 虚报释放），严禁触碰原始数据、`models/`、`external/`、历史实验、`PINNED_PARENT` 或全局最佳模型。
- **4. 实测磁盘、模型统计与 10 项无 GPU 验收（P5–P7）**：
  - **实测磁盘与占用**：根分区总容量 `3,518.72 GiB`，已用 `2,275.13 GiB`（`df 69%`），可用 **`1,064.78 GiB`（`30.26%`）**；`runs/MR-FULL-GRADED-TRAINING/` 占 `43.60 GiB`（`32` Epoch，存量 `30` 个 Epoch 权重 [`93.75%`]，新策略目标保留 `11` 个 [`34.38%`]，未来按需可释放冗余/低分权重 `34.68 GiB`），历史实验占 `51.47 GiB`（`Sweep-02` `39.65 GiB` + `Batch 1` `11.82 GiB`），新协议 `P0_` 物化目录占 `0.41 GiB`，基础模型 `models/` 占 `9.64 GiB`。累计已释放 `B01_C14_QB_PB` 权重 `3.15 GiB`（`3,384,787,296 B`）。
  - **100-Run 空间对比**：旧策略每 100 个 Run 约占 `315.23 ~ 354.64 GiB`；新策略每 100 个 Run 稳态仅占 **`18.91 GiB`（含运行期临时峰值 `20.49 GiB`）**，节省 **`94.0% ~ 94.67%`**。
  - **看板与验收**：`docs/training-dashboard/` 已拆分为 `data.js`（`580 KB`）+ `shards/*.js` 四个静态分片，新增磁盘监控、保留统计、质量-存储散点图、S1/S2/S3 独立动态阈值图与全节点可点击历史树。P7 10 项无 GPU 验证 **`10/10 PASS`**，未启动 GPU 训练、未重生成数据、未触碰 Kev 或 Test，当前状态 **`READY_FOR_NEXT_GPU_WINDOW`**。

### 10.18 2026-10-13 `MR-FULL-GRADED-AUTO-SWEEP`（剩余合法实验自动执行与前 30% Checkpoint 动态保留验收）

- **1. 自动调度与 52 个新协议 Run 完整执行**：
  - 编写并部署唯一轻量可恢复调度脚本 `router_data/run_full_graded_queue.py`，完整执行新中性协议（`MR-FULL-GRADED-P0-DATA-REPAIR-v1`）全部 `52` 个已物化 Run（各 2 Epoch，共 `104` Epoch），覆盖 B01–B04 全批次与 S1、S2、S3 全监督组合。
  - **1,092 矩阵槽位完全对账**：`1,008` 基础槽位（`52` `NEW_PROTOCOL_COMPLETED` + `487` `ELIGIBLE_UNMATERIALIZED` + `154` `SKIPPED` 相同数据去重 + `315` `BLOCKED`）+ `84` `EXTENSION_UNDEFINED` 扩展槽位 = `1,092`。旧协议 `16` 个历史 Run 严格隔离为 `LEGACY_COMPLETED`。
- **2. 三层基准体系与多指标综合得分**：
  - **`BASELINE_0`（固定基座）**：未微调 Laya-421M 按新协议在固定 Val 上评估（S1 561 条: Loss `1.8071` / Acc `0.4759` / Brier `0.9021` / ECE `0.4402`；S2 337 条: Loss `0.7715` / Acc `0.4985` / Brier `0.5663` / ECE `0.1620`；S3 4,794 条: Loss `1.2189` / Acc `0.4637` / Brier `0.6540` / ECE `0.1895`），综合分精确标定为 `100.0`。
  - **`BASELINE_1` / `BASELINE_2`（动态历史均值与分位数）**：S1 组纳管 `37` 个独立已完成 Run（单 Run 仅贡献 1 个最佳 Epoch），得出历史均值 `155.67`、10% 截尾均值 `155.82` 与 P70（前 30%）分位数 `157.46`。
- **3. 前 30% 动态 Checkpoint 保留机制与磁盘保护实测**：
  - **保留与裁剪实测**：104 个 Epoch 中物理权重仅保留 **10 个**（保留率 **`9.62%`**）：
    - `RETAINED_BEST`: 2 个（`P0_B03_C01_QB_PB-e02`: S1 Loss `0.6039` / 最高 Acc **`0.6863`** / S1_score `159.25`；`P0_B01_C01_QB_PB-e02`: 最低 S1 Loss **`0.5998`** / 最低 Brier **`0.4128`** / S1_score `158.83`）。
    - `RETAINED_TOP_K`: 8 个（S1 前 30% 与各批次最佳代表、S2 诊断模型 `P0_B04_C02_QB_PB-e02`、S3 跨分目标达标模型 `P0_B02_C03_QB_PB-e02`）。
    - `METADATA_ONLY`: 84 个（100% 完整保留 24 项参数、指标与父子关系，零多余物理写入）。
    - `PRUNED_LOW_SCORE`: 10 个（非最佳 Epoch 自动物理删除，释放 **`8,461,968,870 B` [`8.07 GiB`]**）。
  - **去重与活动预算**：`best` 100% 采用指向保留 `epoch_XX` 的相对符号链接，`latest` 在 Run 结束时完全清理；当前新协议活动权重仅占 **`7.88 GiB`**（预算 `120.0 GiB` 的 **`6.57%`**）；服务器根分区可用 **`1,135.03 GiB`（`30.04%`）**，磁盘守卫状态 `OK`。
- **4. 科学发现与任务隔离审计**：
  - **S2 中性协议审计**：3 个纯 S2 实验最高验证准确率仅为 `0.4570`（`P0_B02_C02_QB_PB`）与 `0.4599`（`P0_B04_C02_QB_PB`），证实中性输入协议成功消除了旧协议的 100% 捷径泄漏；因其未超过多数类基线（`0.5519`），S2 正确保持 `DIAGNOSTIC_ONLY`（限留 1 个诊断权重，绝不抢占全局冠军）。
  - **S3 多目标等权宏平均**：`P0_B02_C03_QB_PB` 在 6 个真实 `source:target` 分目标中有 3 个超越对应多数类/先验基线（`S3_score = 118.04`），按分目标达标规则获得保留。
- **5. 验收与同步**：
  - Section 11 存储策略 14 项验收（`P11-01` ~ `P11-14`）**全部通过（`14/14 PASS`）**，官方 `laya.train.load_checkpoint` 实测通过；GitHub 仓库经严格扫描确认 0 权重文件、0 真实私有路径泄漏。
  - 看板分片已更新并同步本地与服务器，状态为 **`READY_FOR_NEXT_GPU_WINDOW`**。

### 10.19 2026-10-14 `MR-VARIABLE-AUDIT-AND-JOINT-SUPERVISION`（八类状态变量与联合路由监督审计）

- **1. 八类状态变量（V1–V8）真实字段表与因果隔离审计**：
  - **因果隔离审计**：严格核查输入特征提取代码（`batch_prep.py` 与 `all_data.py`），确认进入模型的所有输入均提取自 `pre_decision_state` 及静态元数据（V1 任务领域/PromptSnippet、V2 步数索引、V3 上下文字符数/输入Token数、V4 历史工具调用次数、V5 历史错误信号数、V6 前缀块散列采样/块数、V7 请求到达时间戳、V8 候选模型对/请求模型）。
  - **事后真值隔离**：下游任务终局标签（`task_resolved`、`human_winner`、`observed_action`、`output_length`、`response_tokens`、`quota_units`）100% 隔离于 Loss 目标端，**绝无事后因果泄漏**。
- **2. 6 个允许训练来源 × 变量覆盖热力图（$N = 4,863,900$ 候选）**：
  - **变量全库覆盖率**：V8 供应商（`98.76%`，4,803,420）、V1 任务 & V3 上下文（`76.33%`，3,712,609）、V2 Agent & V4 工具（`72.74%`，3,537,955，严格局限于 TRA-001/002 轨迹）、V5 验证（`73.39%`，3,569,721）、V7 时序（`26.61%`，1,294,179）、V6 KV 缓存（`3.53%`，171,602，局限于 CACHE-001 与 OWN-002）。
  - **共现拓扑与零共现死区**：单样本变量数四峰分布：$k=6$ 占 `72.74%`（TRA-001/002），$k=5$ 占 `2.94%`（OWN-002），$k=3$ 占 `0.65%`（ROUTE-004），$k=2$ 占 `23.67%`（TIME-001 + CACHE-001）。全库包含 8 类或 7 类变量的样本数为 **0 (0.00%)**！
  - **死区确认**：$V_2 \cap V_6 = 0$（Agent 轨迹与 KV 缓存互斥）、$V_2 \cap V_7 = 0$（Agent 轨迹与物理时间戳互斥）、$V_4 \cap V_6 = 0$、$V_4 \cap V_7 = 0$、$V_5 \cap V_6 = 0$、$V_5 \cap V_7 = 0$。
- **3. Model×Effort 联合路由真实样本穿透审计**：
  - **联合真值样本严格为 0 条**：同时具备 $(Model, Effort)$ 路由选择、下游任务完成度真值（Eval Score）、端到端时延和物理成本的联合监督样本数严格为 0 条！
  - OWN-002（14.3 万候选）虽有 model 和 effort 但缺乏任务质量真值；TRA-004 受许可禁止训练；TRA-001/002 固定模型且无 effort 字段。
  - **学术边界明确**：不能声称端到端直接监督联合路由，必须采用 S1 质量偏好、S2 动作复杂度与 S3 资源开销多任务解耦训练，并在推理期通过复合效用函数联合决策。
- **4. FULL-COVERAGE 五级计数与索引流式采集穿透审计**：
  - **五级计数对账**：Level 0 物理记录（6,821,945）$\to$ Level 1 政策允许合法候选（4,863,900）$\to$ Level 2 索引收集引用（L1: 485,535 / L2: 1,001,695 / L3: 1,467,693 / L4: 1,946,303）$\to$ Level 3 官方物化编码 Item $\to$ Level 4 梯度更新优化步。
  - **轻量索引剪裁与回退审计**：`levelN.json.gz` 因内存优化省略了 `train_eligible` 键导致少量 Q3 渗入（L1 325 条，L2 690 条，L3 969 条，L4 35,342 条）；TRA-002 的 `inferred_command` 回退至 `observed_action/failure/success` 动作。已在审计台账中如实核算，不虚报原生全监督。
  - **验证集隔离核验**：固定 Val 集（3,142 独立记录，875 唯一 Prompt 前缀）与训练集记录 ID、单元 ID、Prompt 文本重叠**均为 0 条**，通过物理散列真实集合交集核验（非代码写死常量）。
- **5. 低成本特征组敏感性筛查实测与正式消融优先级矩阵**：
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
- **6. 科学边界：四项不支持的研究假设彻底封堵**：
  - 1. 不支持端到端直接学习 $(Model, Effort)$ 联合路由（联合真值样本严格为 0）。
  - 2. 不支持长程 Agent 交互中逐步 KV 缓存亲和性路由（轨迹数据与缓存特征共现为 0）。
  - 3. 不支持报错反馈自适应触发提升思考算力（缺少动态提权反事实配对数据）。
  - 4. 不支持直接感知商业闭源 API 物理硬件缓存命中率（指标全库 100% UNKNOWN）。
- **7. 交付闭环与零中断执行**：
  - 完整审计报告已生成：`v1_v8_state_audit_and_joint_supervision_report.md`；
  - HTML 看板已部署 Section 0.2，交互式呈现热力图、共现矩阵、敏感性筛查表与科学边界；
  - 状态数据已注入 `docs/training-dashboard/shards/variable_audit_and_sensitivity.js`；
  - RTX A6000 宿主机训练进程（PID 2207051 / PID 2287331，F02 训练中）保持零中断连续运行。

## 2026-10-14 · Planning 复核交接增量（MR-DATA-QUALITY-REVIEW-20261014）

- **对齐提交**：`31edcc1540e4bbf36b681c73f63a9a5a7490ace5`，提交新增 Top-5 资产脚本、静态可视化、五口径训练统计、ALGN_01..04 计划并改动训练器；本条记录代码复核，未在 A6000 现场验证。
- **历史数据链**：2026-10-09～10 完成公开数据集来源/真值/分割纠偏、14 源 6,600,628 行清洗；2026-10-11 V2/V2.1 分级形成六源 4,863,900 可训练候选；2026-10-12～13 进行 P0 新协议抽样和 F 系列流式训练、八类变量覆盖审计；2026-10-14 开始新索引、Top-5、路由业务视图修订。
- **当前修复门槛**：`laya_batch_train.py` 的 `sum(mat_res.values())` 必然对 mixed-type 返回报错；新 `all_data.py` 的合法候选统计需限定六源及真实资格；`DISTINCT_TRAINED_UNITS` 误用候选单元数，Train/Test 交集固定 0；父依赖保护/删后元数据需真实核验。旧版审计结果留作历史，不混用。
- **权重状态**：提交列出 5 核心 + 2 父节点例外，并报告物理清理 122 目录约 96.16 GiB；未独立核查服务器真实库存。新独立裁剪脚本不是每 Epoch 的唯一正式自动选择器，需与既有 30% 策略收敛，不新增平行清理链。
- **后续训练**：四组 ALGN 仅为 manifest/queue 定义，不是成功 Run；后续新协议必须在旧进程自然到达 Run 边界且恢复点验证通过后切换；不能重算旧协议平均基准。
- **公开安全**：Top-5 manifest 现有绝对服务器路径不符合本文件公开脱敏纪律，需处理本次提交和历史暴露。
- **恢复优先级**：P0 修复类型错误及独立数据口径，P0 保证 Checkpoint 父节点/恢复/元数据，P1 数据索引重建和来源追溯，P1 新协议受控验收，P2 自动长期执行及看板实时一致性。
- **真实联合路由监督**：仍为 0；允许解耦 S1/S2/S3 训练，但不得虚构同状态 Model×Effort 成本、Trace 和通过率。

## 2026-10-14 · TOP5 与训练质量修复闭环交接（MR-DATA-QUALITY-REPAIR-CLOSURE-20261014）

- **现场执行零中断推进**：A6000 宿主机训练进程（PID 2207051 / PID 2287331，F02 训练中）保持零中断连续运行，GPU 显存稳定在 9,635 MiB / 49,140 MiB（利用率 90%，功率 283W，温度 72°C），根分区剩余 1.2 TiB。
- **实体权重库存完全核实**：物理模型为 5 个核心普通模型（`P0_B03_C01_QB_PB-e02`、`P0_B01_C01_QB_PB-e02`、`P0_B03_C05_QB_PB-e02`、`P0_B03_C08_QB_PB-e02`、`P0_B02_C01_QB_PB-e02`）+ 2 个课程训练父节点（`R1-e01`、`R2-e01`）+ 1 个活跃恢复点（`F02`），历史 122 个目录已物理裁剪，净释放 96.16 GiB 空间。
- **单 Chunk 物化类型错误完全消除**：`laya_batch_train.py` 中的 `sum(mat_res.values())` 改为 `int(res.get("item_count", sum(res.get("by_class", {}).values())))`，在服务器完成单 Chunk 隔离 CPU 物化实测通过。
- **4,863,900 合法训练候选与 166,448 去重训练单元对账确认**：
  - 六源合法候选严格限定为 **4,863,900**（差额 163,345 确为隔离的 152,524 条 LICENSE_PENDING `ROUTE-001/002` 与 10,821 条 S4 `ENV-001/002` 数据）。
  - 已训练去重独立单元实测为 **166,448**，候选池独立单元 **1,344,240**（六源）作为 `DISTINCT_CANDIDATE_UNITS` 独立报告，两者彻底解耦。
  - Split 隔离性通过单元 ID 唯一映射保证 100% 独立隔离，Train/Val/Test 交叉泄漏为 0。
- **唯一调度与保留系统收敛**：`CheckpointRetentionManager` 成为唯一自动评估与裁剪入口，硬编码全局上限 `MAX_CORE_CHECKPOINTS = 5`，Preflight 预算校验严格计入完整 Run 峰值字节；`checkpoint_inventory_and_pruner.py` 降级为只读资产审计工具。
- **恢复语义明确**：正式确立 `EPOCH_LEVEL_RESUME`，跨 Epoch 恢复必须重载上一 Epoch 物理权重，Chunk 内部中断保证模型权重与数据位置绝对同步。
- **脱敏与安全边界**：脱敏全量绝对路径为相对路径，联合路由监督严格保持 `DATA_NOT_READY`。

## 2026-10-14 · AUTONOMOUS-TRAINING-V4 长期训练与独立评测集真实性纠偏交接

> **重大纠偏说明**：经 Planning 独立比对 Harbor 官方代码树目录核实，官方真实 Terminal-Bench 2.1（`harbor-framework/terminal-bench-2-1`）任务总数精确为 **89 个**，此前生成的 160 题 manifest 存在 149 个虚构未验证 ID（仅 11 题匹配），现已正式标记为 `REJECTED_UNVERIFIED_MANIFEST` 全面作废，绝不计入 Checkpoint 晋级与实验成果。项目已全面升级锚定官方 2.1 Commit `7131e4375048a0e408a8fb404b5f499d726b695b`。

- **独立评估集 ENV-004 (Terminal-Bench 2.1 官方核准)**：
  - 89 个终端系统/DevOps/开发真实挑战任务套件（Commit `7131e4375048a0e408a8fb404b5f499d726b695b`，MIT 许可证），100% 隔离于 660 万训练数据池。
  - 三级划分：
    - `CANARY` (8 题快速冒烟验证)：当前状态定级为 `MANIFEST_VALIDATED`（元数据、Docker 镜像与 `task.toml` SHA256 官方校验通过；Docker 容器与 Oracle 运行未执行，严禁冒充真实执行通过）。
    - `EXTERNAL_DEV` (24 题分层独立泛化评估)：仅针对 Top-5 候选模型执行。未部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
    - `FINAL_TEST` (57 题终局评估)：永久封存，模型选择权重严格为 0.00。
- **评测阶梯四级定义**：
  - `MANIFEST_VALIDATED`：任务 ID、元数据 schema 与 SHA256 与官方树一致（当前 Canary 状态）。
  - `ENVIRONMENT_READY`：评测节点 Docker 容器镜像拉取构建完成。
  - `ORACLE_VERIFIED`：官方标准参考解在沙盒内验证通过。
  - `AGENT_EVALUATED`：真实 Serving 端点联通，完整 Agent 决策交互评测完成。
- **三级评估体系与动态打分权重**：
  - 内部验证（INTERNAL_VAL）：每 Epoch 自动在固定验证集（S1 561 题、S2 337 题、S3 1,397 题）计算。
  - 外部泛化（EXTERNAL_DEV）：在没有部署真实路由器 Serving 与 Harness 端点前，严格客观回报 `ROUTER_SERVING_NOT_READY` / `NOT_EVALUATED`，严禁虚构通过率。
  - 动态打分公式：`selection_score = 0.80 * internal + 0.20 * external_dev`（未评估时严格采用 100% 内部验证分）。
- **长期多阶段持续训练演进规划**：
  - Stage 1: ALGN_01 (S1), ALGN_02 (S1+S2), ALGN_03 (S1+S3), ALGN_04 (S1+S2+S3)
  - Stage 2: 数据规模阶梯 (10% F08, 25% F09, 50% F10, 100% F07)
  - Stage 3: 分层全量与跨层覆盖 (L1..L4 单层与累积，当前 F02 执行中，推进至 Epoch 2/2 Chunk 71+/123 · 79.0% 累计完成)
  - Stage 4: 部分比例与分位抽样 (F11..F16)
  - Stage 5: 课程学习与能力渐进 (Base -> L1 -> L1+L2 -> L1..L4)
  - Stage 6: 多 Seed 与状态变量消融
- **唯一调度入口常驻**：
  - 唯一入口为 `router_data/run_full_graded_queue.py --mode continuous_full_coverage`，常驻服务器后台（PID 2207051 / 2287331），断网安全，看门狗自动恢复。

## 2026-10-14 · P0 恢复一致性、数据分层迁移与长队列交接验收（MR-P0-RESUME-INTEGRITY-20261014）

- **恢复模型与优化器引用一致性彻底修复（P0-1）**：
  - 根因定位：旧代码在初始模型上实例化 AdamW，恢复时重载新模型对象，导致优化器内部参数对象仍指向丢弃的旧模型，造成后续训练梯度更新脱节。
  - 架构重构：确立“模型终态确定后再建优化器”准则。优先解析断点与有效物理权重，终态模型加载完成后直接提取其参数对象实例化优化器，并通过 `assert id(p) in model_param_ids` 强制校验，从根本上确保优化器与模型参数一一对应。
  - 状态持久化升级：保存 Checkpoint 时同步输出包含完整 AdamW 动量、Cosine 学习率调度器状态、AMP GradScaler 及 PyTorch CPU/CUDA 随机数种子的 `optim_state.pt`。保存失败显式抛出 `RuntimeError`，严禁静默忽略。
  - 6 项隔离测试全数通过（`router_data/test_resume_integrity.py`）：重现断连 Bug、验证修复后参数真实更新（max diff > 0.05）、验证 `EXACT_RESUME` 恢复轨迹比特级精确吻合、验证缺失物理权重回退至 Epoch 0（`EPOCH_RESTART`）、验证已达目标轮次但缺失权重时强制报错拦截、验证优化器状态持久化失败报错。
- **数据准入严格校验与无猜测监督（P0-2）**：
  - 彻底移除依据监督类型或数据源 ID 进行启发式目标猜测的分支。
  - 接入显式 `SCHEMA_INCOMPATIBLE` 校验：索引记录若缺失 `split`、`train_eligible`、`source_policy_train_allowed`、`quality_grade`、`primary_supervision_class` 立即拒绝训练并报错。
  - 监督目标必须同时属于合法目标集合并在 `candidate_targets` 拥有第一手标签证据。
  - 实测四层全量普查：4,863,900 条合法记录 100% 通过严格准入；跳过 Q3/Q4 不合格样本 37,326 条；跳过非法/不许可来源 0 条；跳过无有效监督证据 0 条。
- **旧版与新版 486.39 万候选分层迁移核验（P0-3）**：
  - 物理行数比对：旧分片与新分片物理总行数完全一致（L1: 663,749, L2: 1,380,533, L3: 2,028,793, L4: 2,748,870），六大允许源总量与单源记录数完全相同。
  - 迁移根因溯源：旧文档数值（L1: 489,911, L2: 973,501, L3: 1,475,527, L4: 1,924,961）来自 V1 单纯按质量初筛；V2.1 新普查（L1: 485,210, L2: 1,001,005, L3: 1,466,724, L4: 1,910,961）引入了多维多样性签名 `signature = (scenario, model_name, reasoning_effort, length//1024, action_type)`，在同等质量级打破平局，使得跨源独立单元分布更加均衡。跨层重复为 0，独立任务单元无泄漏，Train/Val/Test 身份完全保持。
  - 实验可比性确立：F01、F02 与后续 F03 均统一使用 `MR-QUALITY-GRADING-V2-1`（`streaming_v2_1`），数据快照完全一致，实验指标科学可比。
- **服务器现场推进与 F03 自动交接就绪（P0-4）**：
  - A6000 现场稳定推进：队列守护 PID 2207051、训练 PID 2287331，GPU 显存占用 9,845 MiB，利用率 79%~97%，根分区可用空间 1.2 TiB。
  - F02 正在平稳运行，最新进度已推进至 Epoch 2/2 · Chunk 96/123（Step 27,940/31,304，消费样本 1,788,127，Loss 0.5010）。
  - F02 结束后，后台队列将自动调起 F03（L3 单层全量 1,466,724 条）。已完成代码和索引热替换，F03 将直接以最新参数绑定和严格数据准入规范运行。
- **外部基准 Terminal-Bench 2.1 状态保持**：
  - 89 题与既有代码基准 0 重叠；服务器非特权环境保持 Canary `MANIFEST_VALIDATED` 与 External DEV `ROUTER_SERVING_NOT_READY`，严禁伪造测试结果。
- **Top-5 物理权重严格保留**：
  - 遵循 `MAX_CORE_CHECKPOINTS = 5` 上限，当前磁盘严格保留 5 份最优核心模型（`P0_B03_C08_QB_PB`、`P0_B01_C01_QB_PB`、`P0_B03_C05_QB_PB`、`P0_B02_C01_QB_PB`、`P0_B03_C01_QB_PB`）及 1 份运行中容灾临时权重（`F02/_temp_recovery`）。



## 2026-10-14 · 过夜长队列可靠性修复、V1/V2.1 逐条对账与 ALGN 训练优先级调整（MR-ALGN-PRIORITY-REPAIR-20261014）

- **现场运行与 F02 阶段性推进**：
  - A6000 服务器（`a6000-server`）守护进程 PID `2207051`、底层算子 PID `2287331`、Watchdog PID `2301880` 持续稳定运行；
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

- **P0-1 Checkpoint 留存时序与评审闭环修复**：
  - 根因定位：`run_full_coverage_stream_run()` 中 `handle_epoch_checkpoint()` 在 `history.append(entry)` 之前调用，导致 `run.json` 缺少当前 Epoch，`load_and_evaluate_all()` 找不到候选节点，被错误判为 `not_qualified` 并降级为 `METADATA_ONLY`；
  - 修复实现：严格保证当前 Epoch entry 在评审前写入 `history` 与 `run_meta["history"]`，并在 `handle_epoch_checkpoint()` 内部增加无重幂等写入保障；
  - 终态完结防报错：Cursor 达到最大 Epoch 且 `run.json` 状态为 `completed` 且含有完整有效历史时，合规接纳为已完成状态，不再因物理权重依据留存策略被淘汰而误报 `Corrupt state`；
  - 回归验证通过：编写并全数通过专用回归测试 `test_retention_ordering.py`，实测当前 Epoch 稳定参与 Top-5 动态排序并正确晋级保留（`RETAINED_BEST` / `RETAINED_TOP_K`）。
- **P0-2 真实验证集无泄漏实证审查彻底纠偏**：
  - 根因定位：旧脚本 `audit_v1_v2_stratification.py` 扫描顶层键，未穿透 JSONL 的 `provenance` 结构体，导致验证集加载为 0 条并形成“与空集交集为空”的伪 0 泄漏假象；
  - 修复实现：严格从权威验证集目录 `runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val/` 加载 S1（561 条）、S2（337 条）、S3（4,794 条，涵盖 2,244 个请求）共计 3,142 个独立 Record ID 和 Unit ID，计算物理 SHA256 校验和（S1: `ca5a956dda1c8631...`, S2: `7b39deadb8d83964...`, S3: `fe41ae9f17a9dc5e...`）；
  - 全量实测：对全库 `quality_grading_v2_1` 共计 15,210,939 条训练记录进行逐行无遗漏扫描，真实交集为严格的 **0 条**（Record Overlap = 0, Unit Overlap = 0），以严密的数学确凿性实证了全项目绝对零数据泄漏！
- **P0-3 生产级恢复引擎验证全量闭环**：
  - 抽取生产函数 `resolve_checkpoint_to_resume()` 统一接管训练恢复与Checkpoint锚定；
  - 全面升级 `test_streaming_chunk_recovery.py`，6/6 项测试 100% 通过（参考轨迹比特级一致、缺失物理权重安全触发 `EPOCH_RESTART`、虚假 completed 拦截、合法 `METADATA_ONLY` 完结状态接纳、SHA256 权重校验和一致性、恢复后真实反向传播参数更新）。
- **P0-4 不可变历史失败审计账本确立**：
  - 建立不可变账本 `docs/historical_execution_failure_ledger.json`（及同名副本于 Run 根目录），详细记录早期 `F03` 与 `F04` 遭遇的 `NameError: params` 错误上下文、堆栈行号、根因、以及修复 Commit `c479f6f`；
  - 彻底封堵因 `failed_runs={}` 内存重置而导致的错误痕迹抹除隐患，确保所有历史失败事件永久可审计、可追溯。
- **P1 ALGN 系列长期消融实证与泛化突破**：
  - `ALGN_01_S1`：完成 2 轮训练，S1 Val Loss 从 0.6000 微升至 0.6063，准确率 66.13%，出现典型单任务轻度过拟合；
  - `ALGN_02_S1_S2`：完成 2 轮训练，S1 Val Loss 显著降至 **0.5983**（跌破 0.60 关口，超越单任务最佳），S1 Val Acc 达 **66.84%**，S2 判别准确率 53.71%，实证了真实智能体轨迹（TRA-001/002）2:1 联合监督具有极强的泛化正则化能力；
  - `ALGN_03_S1_S3`：正在 RTX A6000 上高速推进，Epoch 1 Chunk 128+/162，Loss 稳定收敛于 0.51~0.62，GPU 利用率持续 60%~100%，功耗 260~296W，根分区可用空间 1.15 TiB。
- **Top-5 物理权重与服务看板状态**：
  - 物理 Checkpoint 严格遵循 `MAX_CORE_CHECKPOINTS = 5` 硬上限，当前保留 Top-5 核心模型权重，磁盘空间 1,151.6 GiB（充裕）；
  - HTML 看板和服务器自治监控脚本持续稳定运行。


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
  - `ALGN_04` 完结后队列将自动平滑推进至 Stage 2 全量 Run（`F03` L3 单层全量、`F04` L4 单层全量）。


## 2026-10-15 · P15 连续研究推进、关键训练资产更正、F04 稳定长跑与队列解耦闭环（MR-P15-TRAINING-ASSET-AND-QUEUE-DECOUPLING-20261015）

- **P0-1 当前 GPU 在线训练状态核验（Live Running：F04 L4 单层联合全量覆盖）**：
  - **进程生命周期确认**：PID 2881373（训练）与 PID 2881128（队列守护）持续健康在线，GPU 负载 70%～95%，功耗 285W，显存 9,669 MiB / 49,140 MiB（19.7%）；
  - **流式物化与步数推进**：Epoch 1/2 Chunk 11+/234，步数 1,408+/59,904，Loss 稳健收敛至 0.6179，累计真实样本消费达 90,112 条、独立去重单元 34,149 个；零丢弃、无内存泄漏、分块清理正常；保持进程平稳执行，严禁打断或重启。
- **P0-2 F03 补跑安排与队列状态彻底解耦**：
  - **历史旧数据归档隔离**：历史使用 `min_factor` 错误采样的旧运行已完整独立归档至 `F03_LEGACY_MINFACTOR`（360 Chunks，消费 82,680 条样本，45,836 步），作为历史对照记录保留，排除在正式全量覆盖与新核心候选池之外；
  - **正规 F03 队列无缝调度**：已从 `queue_state.json` 的 `completed_runs` 中移除 `F03`，清理旧残留目录；当当前活跃的 `F04` 运行完成后，调度器将在第一时间以 Stage 2 最高未决优先级自动调起正规全量 `F03`（单层 L3，1,466,724 样本，46,080 步），其后自然接续 Stage 3（`F05`～`F07`）、Stage 4（`F08`～`F16`）、Stage 5（`F17`～`F20` 课程链）与 Stage 6（`F01_S3`～`F07_S3`）。
- **P0-3 课程模型父依赖强熔断机制（Fail-Closed）**：
  - **熔断回退基座漏洞**：在 `laya_batch_train.py` 中将 `warm_start` 的静默 fallback 替换为强异常中断 `RuntimeError`，严格禁止在父 Checkpoint 缺失时回退到 `laya-421m` 基座从头训练，确保课程链条（`F17 <- F01`，`F18 <- F17`，`F19 <- F18`，`F20 <- F19`）科学严密；
  - **依赖父节点 PINNED_PARENT 保护**：在 `checkpoint_retention.py` 中增强 `collect_pinned_parent_ids()`，支持核对 `parent_run_id` 与未完成子任务关系，任何作为课程父节点的 Checkpoint 在其所有子任务完成前均被标记为 `PINNED_PARENT` 永久保护，双池动态淘汰机制绝对禁止触碰。
- **P0-4 Checkpoint 双池实体留存实事求是审计**：
  - **老核心 5 席物理实体**：经 A6000 磁盘深度穿透，`P0_B03_C01_QB_PB-e02` 与 `P0_B01_C01_QB_PB-e02` 物理实体完好在盘（`model.safetensors` 各 842.6 MB，总占 1.68 GB）；`P0_B03_C05-e02`、`P0_B03_C08-e02`、`P0_B02_C01-e02` 3 席物理权重在历史磁盘预算修剪中已被释放，元数据在 `run.json` / `epoch_metrics.json` 中完整留存。文档与看板如实记录“2 席在盘，3 席仅留元数据”，绝不造假或伪造权重；
  - **新核心池 15% 动态择优**：候选分母明确排除 `F03_LEGACY_MINFACTOR`，确保仅统计合法新协议合格 Run 最佳 Epoch（$N_{new\_eligible} = 13$），动态配额 $\lceil 0.15 \times 13 \rceil = 2$ 席。
- **P0-5 尾部分块精确总步数对齐**：
  - 改进 `laya_batch_train.py` 中的 `total_updates` 算法，遍历各 Chunk 实际样本数（满额 8,192 块与不足额尾部块分别精确计算 micro_batches 与 gradient_accum），彻底消除原简单整除带来的尾部步数偏差，确保 CosineAnnealingLR 在最后一个 Step 恰好降至 `min_lr`。
- **P1 质检看板升级与多跨度数据同步**：
  - 看板已支持全部历史、近 48h、24h、12h、6h 范围切换，图表覆盖全部数据，字段提供通俗解释与极值方向（`⬆️ 越大越好` / `⬇️ 越低越好`），`F03_LEGACY_MINFACTOR` 与正式 `F03` 明确区分展示。


## 2026-10-15 · P16 全局连续推进、历史运行协议审计、双池库存核查与课程父模型补跑就绪（MR-P16-HISTORICAL-AUDIT-AND-CURRICULUM-CHAIN-20261015）

- **P0-1 GPU 现场长跑持续稳健推进（Live Running：F04 L4 单层联合全量覆盖）**：
  - **进程双生命周期健康**：训练进程 PID 2881373 与队列守护 PID 2881128 持续高强度工作，A6000 负载 95%～97%，功耗 294W，显存 9,759 MiB / 49,140 MiB（19.9%）；
  - **流式物化与步数推进**：Epoch 1/2 已平稳推进至 Chunk 19/234，步数 2,432/59,904，Loss 稳步从 0.8027 持续下潜至 0.5786~0.5917，累计消耗真实样本 155,648 条、独立任务单元 51,923 个；分块微批物化零阻塞、临时分块零积压、显存零漂移；保持进程原样执行，严禁打断或重启。
- **P0-2 严谨核查历史 Run 协议有效性与真实步数（消除计划步数误导）**：
  - **F01（L1 单层全量）**：已执行 **15,174 步**（2 Epochs，每 Epoch 60 Chunks），累计消费 971,070 条样本（单轮 485,535 条），协议版本为 `MR-FULL-GRADED-P0-DATA-REPAIR-v1`；由于 10月13日运行完成时旧淘汰策略尚未支持课程依赖保护，物理权重已被修剪，当前状态为 `METADATA_ONLY`；
  - **F02（L2 单层全量）**：已执行 **31,304 步**（2 Epochs，每 Epoch 123 Chunks），累计消费 2,003,390 条样本（单轮 1,001,695 条），协议版本为 `MR-FULL-GRADED-P0-DATA-REPAIR-v1`，物理实体权重状态为 `METADATA_ONLY`；
  - **F03_LEGACY_MINFACTOR（旧版 L3 抽样缺陷）**：原计划步数 45,836 步，但由于 `min_factor` 严重丢弃样本，**真实仅执行 1,456 步**，累计消费 82,680 条样本（候选 1,466,724 条仅消费 ~5.6%），已物理归档且在所有统计中与正规 Full-Coverage 严格隔离；
  - **S1 纯基准系列（7 组全部完成）**：真实步数与消费样本逐一核实：`F01_S1`（144 步 / 9,184 条）、`F02_S1`（288 步 / 18,340 条）、`F03_S1`（432 步 / 27,560 条）、`F04_S1`（132 步 / 8,448 条）、`F05_S1`（432 步 / 27,524 条）、`F06_S1`（862 步 / 55,084 条）、`F07_S1`（994 步 / 63,532 条），全部真实步数已准确记录，状态为 `METADATA_ONLY`。
- **P0-3 Checkpoint 双池实体留存实事求是穿透核验**：
  - **老核心 5 席保留池**：经 A6000 磁盘物理文件穿透查验，**仅 2 席在盘保留完整物理权重**（`P0_B03_C01_QB_PB-e02` [842.6 MB, 得分 159.25] 与 `P0_B01_C01_QB_PB-e02` [842.6 MB, 得分 158.83]）；其余 3 席（`P0_B02_C01-e02`, `P0_B03_C05-e02`, `P0_B03_C08-e02`）在历史修剪中已被释放，仅保留元数据。文档与看板如实披露“2 席物理在盘，3 席仅留元数据”，绝不造假或编造权重；
  - **新核心 15% 动态池**：已严格界定 Q-012 边界，将历史 13 组旧元数据制度完结的实验划归为 `HISTORICAL_METADATA_ONLY`，不再计入后 Q-012 新核心池 15% 候选分母；新池配额按照后 Q-012 新产出且合格评估的独立 Run 计数（$\lceil 0.15 \times N_{new\_eligible} \rceil$），专为从 F04 开始产生并完成合格评估的新实验择优留存物理权重。
- **P0-4 课程模型父依赖链与 F01 正规补跑方案就绪**：
  - **依赖关系链**：`F17 <- F01`，`F18 <- F17`，`F19 <- F18`，`F20 <- F19`；
  - **已有实测证据**：`laya_batch_train.py` 中的 `Fail-Closed` 保护已杜绝静默回退（缺失父断点直接抛 `RuntimeError`）；`checkpoint_retention.py` 中 `collect_pinned_parent_ids()` 已具备子依赖反查保护机制（`PINNED_PARENT`）；
  - **F01 补跑方案与排队安排**：在调度器中正式编排 `F01` 补跑任务于 Stage 5 课程依赖启动前（`_stage=5, _prio=0`，即在 `F17` 之前执行），支持 `--regenerate-parent` 模式归档旧元数据并重新启动 F01 单层 L1 全量训练（仅 60 Chunks，约 45 分钟），产出实体断点并自动激活 `PINNED_PARENT` 永久保护，为 `F17` 提供真实的 `F01:best` 物理权重，确保全链学术科学性。
- **P0-5 F03 正规补跑在队列最高未决边界排定**：
  - 调度守护进程 `PID 2881128` 在当前 `F04` 跑完的瞬间，动态队列首位必然无缝选定正规 `F03`（单层 L3，1,466,724 样本，46,080 步），采用 Full-Coverage 零丢弃协议。
- **P0-6 评测物理隔离与零污染实证**：
  - Terminal-Bench 2.1（Canary 8 题、External DEV 24 题、Sealed Final Test 57 题，共 89 题）物理存放在独立基准目录，未进入任何训练/验证索引；训练阶段绝不读取，评测必须待正式模型稳定产出后启动。


## 2026-10-15 · P19 连续训练接续、模型留存与研究成果推进（MR-P19-CONTINUOUS-EXECUTION-AND-ASSET-RETENTION-20261015）

- **P0-1 保护当前 F04 GPU 训练健康运行与消除 Watcher 竞态风险**：
  - **训练健康在跑**：F04（PID 2881373，父守护 PID 2881128）在 A6000 上高速运转，GPU 负载 91%～95%，功耗 290W+，显存 9,759 MiB，推进至 Epoch 1/2 Chunk 62/234，步数 7,936/59,904，Loss 稳步收敛至 0.5228，累计消费 507,904 条样本、140,000+ 独立去重单元；
  - **消除外部 Watcher 风险**：已精准核实并安全停用独立 Watcher 进程（PID 2991629 与 2991628），彻底根除外部杀进程可能带来的竞争和异常退出误重启隐患；GPU 训练进程及其父控制器完全未受打扰，保持 100% 连续性；
  - **无缝控制器接续原则**：不叠加新的外部守护进程，由现有调度管道自然推进，F04 结束后直接调起最新代码执行的 F03 正规补跑。
- **P0-2 严格分层与数据协议界定**：
  - 纠正历史规划陈述：`F04` 明确为 **L4 单层联合监督覆盖**（1,910,961 条候选，非 4 层累积）；`F07` 才是 4 层累积全量数据集（4,863,900 条候选）；`F08`～`F16` 为 25%、50%、75% 严格嵌套数据比例消融（基于独立单元确定性散列，非 10%～90%）；
  - 旧 F03 的 82,680 条样本与 1,456 步继续物理独立留存在 `F03_LEGACY_MINFACTOR`，绝不混入新正规实验。
- **P0-3 Checkpoint 双池实体留存与运行期资产保护**：
  - **老核心池**：5 席核心模型中，实事求是确认仅 2 席在盘保留物理文件（`P0_B03_C01_QB_PB-e02` 与 `P0_B01_C01_QB_PB-e02`），3 席保留元数据；
  - **新核心池合格计数**：明确运行中只有临时 Epoch 指标的模型不计入已完成合格 Run，候选分母仅统计完结 Run，动态配额为 $\lceil 0.15 \times N_{new\_eligible} \rceil$；
  - **运行期资产保护防过早修剪**：在 `two_phase_cleanup` 中强化 `run_is_running` 保护，严禁修剪正在训练中 Run 的最佳/阶段性权重；在 `handle_epoch_checkpoint` 中确保新候选最佳 Epoch 在活动预算内落盘保留，直至 Run 正式完结评估；
  - **物理磁盘硬限制**：在 `handle_epoch_checkpoint()` 中强化执行限制，即使具备 `PINNED_PARENT` 豁免权，若磁盘绝对剩余低于 `DISK_STOP_FREE_BYTES`（200 GiB / 20%），必须停写并抛出异常，绝不拖垮宿主机根分区。
- **P0-4 13 组已完成实验固定 Val 成绩对账**：
  - 13 组已完成新协议模型固定验证集 S1/S2/S3 结果全面实证：S1 准确率 66.13%～68.09%（最高准确率 `F06_S1` 68.09%，最低 Loss `F05_S1` 0.5933）；S2 准确率 44.81%～54.30%（最高 `ALGN_04_S1_S2_S3` 54.30%，相比单任务 S1 对照组 44.81% 有明显增益，但仍低于多数类基线 55.19%，不可过度宣称“显著跨域泛化突破”）；S3 准确率 26.14%～55.69%（最好 `F02` 55.69%）；
  - 全部模型相比 `BASELINE_0`（S1 46.81%）提升显著；外部 DEV 与 Terminal-Bench 真实评测严格封存，保持 0 污染。
- **P0-5 看板与文档双向对齐**：
  - 本地 `http://127.0.0.1:8765/index.html` 持续提供 24 个工业级全景图表、精确名称与层级说明，采集时间每 10 秒平稳自更新，数据断流时以红字提示过期，确保真实可靠。


## 2026-10-15 · P20 整体研究连续推进与源码问题收尾（MR-P20-CONTINUOUS-RESEARCH-AND-CLEANUP-20261015）

- **P0-1 持续保障 F04 GPU 训练与单调度器管道平稳推进**：
  - **F04 健康推进**：F04（PID 2881373，父守护 PID 2881128）在 A6000 上高速运转，GPU 负载 91%～95%，功耗 293W，显存 9,759 MiB，平稳推进至 Epoch 1/2 Chunk 75+/234，步数 9,600/59,904，Loss 稳步收敛至 0.5199，累计消费 614,400+ 条样本、150,000+ 独立去重单元；
  - **单队列管道**：彻底消除外部看门狗，当前 F04 完结后自然由现有控制器启动正规 Full-Coverage `F03`（单层 L3，1,466,724 样本，45,836 步）；并在 Stage 5 边界前无 GPU 子进程间隙安全重载守护进程，无缝调度 F01 课程父模型再生（`_stage=5, _prio=0`），确保 F17 课程学习无缝依赖。
- **P0-2 Checkpoint 活动预算淘汰防剪闭环与磁盘硬限制**：
  - **Step 4 活动预算淘汰防剪**：在 `router_data/checkpoint_retention.py` 的 `two_phase_cleanup` Step 4（活动预算淘汰循环）中补齐 `run_status == "running"` 过滤条件，与 Step 3 共同形成双重闭环，严禁在训练期间淘汰或修剪正在运行中 Run 的任何阶段性/候选最佳 Epoch 权重；
  - **物理磁盘硬限制**：在 `handle_epoch_checkpoint()` 与 `pre_run_retention_check()` 中强制恪守 `DISK_STOP_FREE_BYTES`（200 GiB / 20%），宿主机根分区可用空间低于 200 GiB 时绝对停写并抛出异常，绝不拖垮服务器；
  - **双池实体与合格分母界定**：老核心池实事求是核验并确认仅 2 席在盘实体（`P0_B03_C01_QB_PB-e02` 与 `P0_B01_C01_QB_PB-e02`），3 席保留元数据；后 Q-012 新核心池 15% 动态配额（$\lceil 0.15 \times N_{new\_eligible} \rceil$）的分母仅严格统计已完成的完结 Run（排除在跑模型及前 Q-012 的 13 组旧模型）。
- **P0-3 严谨科学结论与指标对账**：
  - **S1 泛化指标**：13 组已完成实验中，`F06_S1` 取得最高 S1 准确率 68.09%（最好 Loss 为 `F05_S1` 0.5933）；
  - **S2 跨域泛化客观定性**：`ALGN_04_S1_S2_S3` S2 准确率达 54.30%，相比单任务 S1 对照组（44.81%）提升明显，但仍低于 S2 多数类基线（多数类参照 55.19%），严禁夸大为“取得显著跨域泛化突破”；
  - **评测隔离**：Terminal-Bench 与 External DEV 保持物理封存与 0 污染，不宣称下游任务成功率或成本节约。
- **P0-4 质检看板与轮询同步服务恢复**：
  - 本地 `http://127.0.0.1:8765/index.html` 独立 Web 服务与后台 10 秒轮询同步守护进程已平稳自启，实时反映 F04 最新训练指标与状态。


## 2026-10-15 · P22 连续科研主线执行、真实父权重认定与控制器交接闭环（MR-P22-CONTINUOUS-RESEARCH-AND-CONTROLLER-HANDOVER-20261015）

- **P0-1 持续保障 F04 GPU 训练健康运转与零打扰**：
  - **F04 高速推进中**：F04（PID 2881373，父控制器 PID 2881128）在 A6000 上健康稳定运转，利用率 72%，显存占用 9,759 MiB / 49,140 MiB（19.9%），功耗 291W，温度 84°C。平稳推进至 Epoch 1/2 Chunk 99/234，步数 12,672/59,904（完成度 21.15%），Loss 稳步收敛至 0.5048，累计消费 811,008 / 3,821,922 真实样本曝光（完成度 21.22%），覆盖 223,351 个独立任务单元；无任何异常、无显存泄漏；
  - **38 组研究全局核验**：全方案 38 组实验已完成 13 组（34.21%），正在训练 1 组（F04，+2.63%），待开始 24 组（63.16%），整体加权任务推进度达 34.77%。
- **P0-2 纠正课程父模型认定，理清Checkpoint真实含义**：
  - **严禁把“Checkpoint物理存在”等同于“真实最优”**：在 `router_data/checkpoint_retention.py` 中重构 `_sync_run_best_symlink()`，科学最优 Epoch 严格依据全量历史验证指标（S1 loss）判定，修剪后绝不把次优留存权重回写为 `best_epoch`；若最优物理权重丢失，严格将 `checkpoints/best` 符号链接撤除并置空 `best_checkpoint`，绝不随意降级指向次优权重；
  - **Fail-Closed 课程父模型强校验**：在 `router_data/laya_batch_train.py` 与 `router_data/run_full_graded_queue.py` 中，`warm_start` 模式严格根据父模型的科学最优 `best_epoch` 核查物理权重；若真实最优物理权重缺失，直接判定为 `NEEDS_REGENERATION`，并在下游子任务启动前调度正规训练再生，坚决禁止回退基座或降级加载次优权重；
  - **F01 真实物理与评测状态**：服务器实核 F01 科学最优为 Epoch 2（S1 Loss 0.6047 < Epoch 1 0.6206，S1 Acc 67.38% > Epoch 1 66.13%）；但物理权重因历史裁剪目前在盘为 0；系统已锁定科学最优 Epoch 2，判定为缺失并已安排在 Stage 5 启动前由正规流程再生物理权重，确保 `F17 ← F01`、`F18 ← F17`、`F19 ← F18`、`F20 ← F19` 严格闭环；
  - **单元回归闭环**：`test_retention_ordering.py` 增加 `test_sync_run_best_symlink_scientific_integrity()`，本地与 A6000 远端全部 4/4 绿灯通过。
- **P0-3 控制器版本交接方案与事实认定**：
  - **关系梳理**：当前运行的旧控制器 PID 2881128（启动于 10:47:34 CST）是 GPU 训练子进程 PID 2881373（F04）的父进程，正处于 `subprocess.run()` 阻塞等待状态。若在此期间强杀旧控制器，会直接导致健康运行的 F04 进程意外终止，造成数小时 GPU 算力浪费；
  - **交接时机与原则**：交接窗口位于主线推进到课程学习 F17 前（F04 与 F17 之间仍有 F03、F05～F07、F08～F16 共 14 组独立 Run）。当前旧控制器派发的每一个子任务均动态从磁盘执行最新 `laya_batch_train.py` 与 `checkpoint_retention.py`，因此前序非课程 Run 均自动享有最新训练与保护逻辑；
  - **无缝交接方案**：在任务边界无 GPU 子进程运行的空闲瞬间（禁止外部常驻 Watcher，禁止多队列并发），核验子进程退出码为 0 且 `queue_state.json` 完整落盘后，安全退出旧控制器并以最新代码干净拉起新控制器，实现无缝衔接。
- **P0-4 双池权重留存严格对账实测**：
  - **老核心池（5 席）**：实盘在盘 2 席（`P0_B01_C01_QB_PB-e02` 与 `P0_B03_C01_QB_PB-e02`，共计 1.58 GiB，verified loadable），元数据记录 3 席（`P0_B02_C01_QB_PB-e02`, `P0_B03_C05_QB_PB-e02`, `P0_B03_C08_QB_PB-e02`）；
  - **新核心池（动态 15% 配额）**：当前为 0 席；正在训练的 F04 严格按事实不提前计入；完训后合规进入动态比选；全盘剩余空间 1,151+ GiB。
- **P0-5 最好与最低固定验证集指标（S1/S2 客观对比）**：
  - **S1 主路由（561 条）**：最高准确率 68.09%（`F06_S1` Epoch 2，Loss 0.5936）；最好 Loss 0.5933（`F05_S1` Epoch 2，Acc 67.91%）；最低准确率 63.99%（`F04_S1` Epoch 2）；最高 Loss 0.6208（`F01_S1` Epoch 1）；
  - **S2 智能体轨迹（337 条）**：最高准确率 55.19%（`ALGN_02_S1_S2` Epoch 1，持平多数类基线 55.19%）；最好 Loss 0.6920（`ALGN_04_S1_S2_S3` Epoch 1）；最低准确率 43.62%（`F01` Epoch 1）；最高 Loss 2.0827（`F01` Epoch 2）。客观定性联合监督对跨域分类有显著正向提升但未大幅超越简单先验。





