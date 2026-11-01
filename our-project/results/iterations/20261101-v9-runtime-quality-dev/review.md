# V9运行与质量步骤结果 · 2026-11-02

新增有效步骤偏好2条、2个标签任务；新Laya取得官方Dev成功，但没有自然切换或优于固定Sol的费用/质量证据。Episode内重复加载已移除。本轮没有新训练、没有替换Serving。

起点：main `62d7bb98326af035512ffb089aba03f366e7924f`。结构化结果见[summary.json](summary.json)，训练材料见[training_delta/summary.json](training_delta/summary.json)，现场见[server_snapshot.json](server_snapshot.json)。目录日期沿本轮开始的11-01，不新建平行目录。

## 1. 编码与运行

| 实际差异 | 原位处理及证据 |
|---|---|
| 在线route_decision与训练step_model_preference | 在线沿用已有步骤说明及ID；内部字段仅t/ins/crit，QID本身不进入Token，说明会进入 |
| 候选顺序 | 移除在线按名称排序，保持配置和训练的Sol→Luna；同保存状态改变28个Token位置、序列长度不变 |
| 真实状态被再次压缩 | 原8步骤中6条重建文本与捕获在线视图不同；Prepare仅处理公共TRAJECTORY_PREFIX，真实比较保留捕获文本 |
| 重复准备请求档位 | 保留已存在requested_native_effort=low；实际模型目标native_effort仍null，不监督未知应用档位 |
| 每次SSH重载 | 一个Episode一个懒启动进程和原LayaAdapter，JSON-lines通信，结束沿现有client.close释放；无第二Serving |

已保存训练行的原native/Trainer序列均3707 Token、IDs与选项marker相同，见[encoding_native_vs_trainer.json](encoding_native_vs_trainer.json)。该证据不代表所有历史训练批次都与新状态处理一致；本轮没有重新训练原Checkpoint。新两行Schema/Mido分别3874/3962 Token，5120/head512完整保留捕获的任务/工具/卡片视图，见[new_input_encoding.json](new_input_encoding.json)。原始完整Agent消息另存，不把短视图当全部历史。

| 运行范围 | Router总秒 | 前向秒 | 前向外秒 |
|---|---:|---:|---:|
| 旧heap-crash保存的7次决策 | 363.6763 | 141.2585 | 222.4178 |
| 新distribution-search成功的5次决策 | 79.2293 | 49.8694 | 29.3598 |

新Episode首次初始化28.6191秒，之后4次复用的前向外开销总0.047701秒；同保存状态复用样本分别9.8/11.1ms前向外开销。两Episode工作负载不同，不报告总耗时加速倍数；前向本身未证明加速。新教师Episode也只初始化一次。

## 2. 新步骤监督

本轮实际比较3个已有Train任务、8对前缀，没有重下数据。每对共享已发生消息与可恢复环境，关闭教师，真实Sol/Luna请求，实际执行一步，再用原项目同范围测试。所有请求均为low配置，但实际Effort未知，目标为MODEL_ONLY。

| 任务/前缀 | Sol结果与模型费USD | Luna结果与模型费USD | 训练资格 |
|---|---|---|---|
| Schema / 5 | 原验证通过；0.0667135 | 原验证通过；0.00053786 | STEP_LEVEL_PREFERENCE，Luna等质量成本 |
| Mido / 5 | 继续读取，原验证退出1；0.053721 | 改parser，原验证退出0；0.00089895 | STEP_LEVEL_PREFERENCE，Luna一步质量 |
| PrettyTable / 4、5、6、7、8、9 | 六对均未全通过 | 六对均未全通过 | OBSERVED_OUTCOME_ONLY，无赢家 |

Mido旧元数据的仓库外测试路径在镜像不存在；本轮用镜像中原项目实际tests，执行前恢复原tests，命令`python -m pytest -q tests`。标签仅代表这个真实验证范围，不声称完整任务语义或Episode胜负。PrettyTable曾从75 failed/130 passed/2 errors推进到1 failed/206 passed，仍有失败，不能据此造Sol或Luna质量赢家。早期两条观察前缀的phase与最新工具phase不同，它们未进入Train；后续前缀使用截至该步的真实phase和连续状态。PrettyTable许可证由原镜像/testbed/LICENSE确认BSD-3-Clause，原文保留；Schema/Mido为MIT。

| 累计范围 | 数量 |
|---|---:|
| 新增标签任务 / 新增有效步骤 | 2 / 2 |
| 本轮Sol / Luna步骤目标 | 0 / 2（质量1、成本1） |
| 累计Model-only目标 | 19 |
| 任务级 / 步骤级 | 9 / 10 |
| 标签任务 / 步骤标签任务 | 11 / 10 |
| 标签仓库 / 步骤标签仓库 | 10 / 9 |
| 全部Sol / Luna | 4 / 15 |
| 步骤Sol / Luna | 4 / 6 |
| 确认的Native Effort / 完整K=3 | 0 / 0 |

当前19条已含此前17条，不再重复加旧delta。原Train196/Val186可组合215/186，未生成完整215行；已准备64旧S1+10步骤的74行定向材料，任务级成本不混为步骤目标。共享Serializer实际消费19条并保留捕获文本，38个requested low保留为输入，实际Effort目标均null。旧382行及13,214候选保留原用途和身份。

本轮两新标签任务对应两新标签仓库。TinyDB两个不同任务共享仓库，累计任务ID数不代表独立仓库数；PrettyTable六前缀只算一个任务，它和此前已标注的另一PrettyTable任务共享仓库。服务器原Serializer也实际消费19行，任务/步骤问题分别9/10、38个requested low、教师0及AA v4保留，没有加载权重或执行优化。

## 3. 独立Dev：官方终局与费用

原Harbor、mini-SWE-agent 2.4.6、30步、4096输出额度、30秒工具窗口，保存/app；上游Verifier未修改，Dev不进入Train。均REAL_API，非Alias。请求/返回型号匹配只能确认API身份，物理后端仍为API_IDENTITY_ONLY_UNVERIFIED_PHYSICAL_BACKEND。

| 任务 / 策略 | 完成生成 | 官方Verifier | 全部已知模型费USD | Trial秒 |
|---|---:|---|---:|---:|
| COBOL / 固定Sol | 11 | 工具30秒超时，未执行 | 0.4150422 | 376.1773 |
| COBOL / 固定Luna | 5 | reward1，3/3 | 0.00140699 | 146.9475 |
| COBOL / 新Laya，教师关 | 16 | AgentTimeout900秒后reward0，1/3 | 0.8735645 | 930.2048 |
| distribution-search / 固定Sol | 4 | reward1，4/4 | 0.0866944 | 254.6800 |
| distribution-search / 固定Luna | 8 | reward0，3/4 | 0.00228552 | 225.3238 |
| distribution-search / 新Laya首次 | 1 | API断连，未执行 | ≥0.002884，另1请求Usage未知 | 239.8172 |
| distribution-search / 新Laya一次API重试 | 5 | reward1，4/4 | 0.1362464 | 421.3882 |
| distribution-search / 新Laya，教师开 | 5 | reward1，4/4 | 0.111619（生成0.091913+教师0.019706） | 365.6178 |

瞬时RemoteDisconnected只作一次同协议重试，首个失败保留。三策略完整可比终局目前只有distribution-search这一题；固定Sol与新Laya均成功，固定Sol更便宜、更快。COBOL固定Sol无可信终局，不能自动记作质量失败或构造完整三方胜负。没有因任务失败继续改同题产物或改变Verifier。

新Laya本轮28次实际决策全部Sol，Luna0，fallback0、自然切换0；其中COBOL两次在官方截止后开始，为原取消问题额外调用，不作协议内动态证据。成功的教师关闭Episode概率如下，所有其他决策见summary与原events：

| 步骤 | Sol概率 | Luna概率 |
|---|---:|---:|
| 0 | 0.5663 | 0.4337 |
| 1 | 0.5526 | 0.4474 |
| 2 | 0.5347 | 0.4653 |
| 3 | 0.5357 | 0.4643 |
| 4 | 0.5326 | 0.4674 |

未改权重、温度或选择规则来制造切换。旧F05的一次自然切换仍是旧证据，不当本轮新权重收益。

## 4. 工具超时、取消和产物

COBOL固定Sol最后工具命令创建并运行批量差分脚本，对编译COBOL与Python反复启动子进程，整体超过原30秒窗口。没有采到具体耗时子例，不能确定是单个子进程问题还是批量总时间；不增加窗口或人工补模型代码。失败命令、异常、真实轨迹和/app/program.py（7613字节）保留，artifact manifest为ok。

COBOL新Laya暴露原Harbor取消asyncio等待但后台Agent继续的问题。官方Agent截止2026-11-01T16:19:22.640857Z：当时已完成13请求、费用0.5245117USD；一个此前发出的请求随后返回，两个新请求在截止后发出，三条返回费0.3490528USD，全部16次实际消费0.8735645USD。第14步又初始化一次，属于该取消问题，不把它计作正常权重复用。

原HarborAgent收到CancelledError后沿AgentState.finish(TIMEOUT)，在Router、Provider、工具的实际调用边界退出并关闭本Episodeclient；已知工具RuntimeError保存命令/耗时/异常，未知output/exit_code保持null并原样抛出。后续成功Dev使用这份源码，但没有再造900秒失败验证新取消分支。

原Harbor artifact-only regrade因shared模式需要活环境而退出1，没有运行Agent或Verifier；不能把失败重评分当新增reward。未重建旧成功题、改task.toml模式、改Verifier或补写产物。

## 5. 教师、Effort与能力卡

新distribution-search教师step3按INITIAL_THREE_GENERATIONS触发1次，成功1次，短评只描述此前脚本与数组输出，经1次Router消费后沿原信号变化失效。未修改mini-SWE-agent Prompt、计划或工具，未选模型。两固定参考、三字段、低频规则和额度不改。

输入1331、输出1638（含reasoning1552）、cache-read0、cache-write1328，费0.019706USD、延迟29.052秒。reasoning在输出内，只计一次。教师开/关都reward1，总费0.111619/0.1362464USD，观察差-0.0246274USD；随机轨迹、缓存不同，单题不能证明因果或稳定净收益。下一次需独立可比Agent条件上的成功率与总成本，而不是重复该前缀请求。

现有授权OneAPI目录HTTP200，Sol/Luna可见、正式qwen3.8-flash不可见；没有新渠道，不重发旧404/503，不用DeepSeek Flash或Qwen27B替代。Sol发送reasoning.effort=low仍报告max，Luna不报告应用档位；原因未知，停止无效探测，不制造Native Effort标签。

AA固定20261031T072548885180Z-v4，Sol/Luna Max各10项，Intelligence v5为54.5087338138148/27.7552004938153。low/none/托管Flash仍NOT_MEASURED，本轮没刷新，不把Max当low实测。正式三身份和五RQ保持。

## 6. 训练现场与下一轮条件

01:08:59台北只读取样：F14独立维护PID808492、running/COLD_START；首轮241/420块（57.38%），总30848/107404更新（28.72%），consumed1974272/6873816，最新Loss0.48724648，块230–241有限。首轮/固定Val未完成，旧NON_FINITE_LOSS归档保留，F14不作父。旧queue_state仍PAUSED_USER_REQUEST、时间10-31；既有handoff817520等待F14退出，本轮不干预或创建新调度。

Serving health/models200、PID327621，F05-e01与原Kev Adapter保持。V9_LAYA_STEP_001-e01实体仍在，上一轮F11接续1轮/9次pointer head更新，本轮更新0；固定S1 Val561项Accuracy0.6898、Loss0.5938、Brier0.4083、ECE0.0362沿用，不重跑。Kev R01–R16完成、R11代表保持，本轮无新LoRA/head更新。

新增仅1质量+1成本，步骤累计10个任务且新Laya仍恒选Sol；74行材料具备格式消费条件，不足以自动开始下一轮。后续需更广独立质量步骤、按监督类型分离的head目标与S1保留、可确认Effort/Flash，以及完整独立Dev上的动态/教师净收益。原八图十二表不变，本轮有限K=2结果不当正式K=3主表。

## 7. 已知成本、源码及公开范围

| 范围 | 完成请求 / Usage | 模型费率USD |
|---|---:|---:|
| Train采集与步骤比较 | 20 / 20 | 0.37132183 |
| Dev生成 | 55 / 55，另1失败无Usage | 1.61003701 |
| 教师 | 1 / 1 | 0.019706 |
| 全工作包 | 77尝试 / 76Usage | 已知2.00106484，完整未知 |

供应商实收、Router CPU和工具/容器资源USD仍未计量。费用按真实请求型号费率及Usage，缓存分别计价，全部实际调用含超时后消费；不沿用Alias映射费用作正式真实模型费用。

本轮源码限checkpoint.py、prepare.py、real_supervision.py、harbor_agent.py、benchmark/__main__.py；原六规划、两训练报告更新。原私人账本、用户Trainer改动、tests和用户删除不提交。公开运行记录仅去除本机/服务器身份路径，不改变响应、Usage、概率、工具反馈或验证结果；完整源码dirty快照及worktree状态留在本地不公开。原失败、权重和训练历史保留，本轮无用采集脚本/配置及临时容器快照清理，原基础镜像保留。
