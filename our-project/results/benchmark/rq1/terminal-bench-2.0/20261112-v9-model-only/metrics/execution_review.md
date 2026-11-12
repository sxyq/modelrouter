# 单次Token、完成状态与实际执行流程

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

## 单次运行

89题、一个策略、一个seed的完整整轮Token未知：旧17策略均遍历89题，但没有89/89有效评分组，最高54/89；请求Usage也有缺项。以下均为git-leak-recovery的单次正常提交、官方Reward1，无重跑累计。

| 策略 | 执行模型Token | 教师Token | API合计Token |
|---|---:|---:|---:|
| Laya原始 Model-only OFF High | 59355 | 0 | 59355 |
| Laya原始 Model-only OFF Max | 44941 | 0 | 44941 |
| Kev微调 Model-only OFF Max | 188563 | 0 | 188563 |
| Kev微调 Model-only ON High | 66237 | 3899 | 70136 |

Token按同一trial_id的真实输入＋输出计量；推理已含输出，缓存读取已含输入。Router本地Token另列，不按商业APIToken计价。4096为每次生成的输出上限，整题输入与生成次数不同，整题消费随之变化。

## 当前Model-only

2026-11-12 23:39台北快照。每档为八个Laya/Kev原始/微调/教师开关组合，各89题，共712位置。

| 固定Effort | 已结束位置 | 有效官方评分 | 运行中 | 未开始 |
|---|---:|---:|---:|---:|
| Low | 156/712 | 25 | 0 | 556 |
| High | 155/712 | 24 | 1 | 556 |
| Max | 155/712 | 26 | 1 | 556 |

75个有效评分位置中13个有AgentTimeoutError；另379个缺Reward，12个Verifier依赖失败原0另列。三档都已运行，三档全量均未完成。

## 教师和执行流程

没有显式子任务列表、subtask_id及子任务完成日志。inspect/modify/verify/recover来自已观察命令、退出状态和输出的规则识别。

教师为gpt-6-luna、Low、每请求4096输出上限、8000字符上下文；读取两条固定成功轨迹的报告摘要和当前观察，返回progress_summary/main_blocker/next_milestone。提示词要求状态短评，禁止解题、详细计划和代替Agent选模型。

第3次生成后首次触发；之后按阶段变化、新验证结果、重复错误触发，最短间隔3次生成。短评进入Router输入，执行模型继续接收原任务和真实工具历史。主组每次生成都路由，Model-only保持固定Effort、只选模型。

## 可追溯日志

[episode_flow.jsonl](episode_flow.jsonl)是原私有事件的字段摘录，保留50条记录、8个三候选排序、8次生成及其请求/返回模型和Effort、16个工具反馈、2次教师请求、3次教师信息消费及官方Reward。Episode为941ee53f-3e63-4ea6-bcdd-93c5249aaeaf；微调Kev Model-only ON High；8次都选Terra High，fallback_used=false，T/M/H均FULL。H为真实工具历史摘要，完整原始工具输出留在私有tool_calls.jsonl。

| 台北时间 | 决策 | 原事件与事实 |
|---|---:|---|
| 20:11:43 | 3 | TEACHER_START，INITIAL_THREE_GENERATIONS |
| 20:12:25 | 3 | TEACHER_END，SUCCESS，三字段输出 |
| 20:12:39 | 3 | TEACHER_ROUTER_INPUT，FULL/true；随后ROUTER_END选Terra High |
| 20:13:03 | 4 | CARRIED_ASSESSMENT，沿用短评，消费true |
| 20:13:44 | 6 | TEACHER_START，PHASE_CHANGED |
| 20:14:25 | 6 | 短评FULL/true；随后选Terra High |
| 20:15:04 | — | AGENT_END，SUBMITTED |
| 20:19:28 | — | 原官方Verifier完成，Reward1 |

TEACHER_END时尚未发生Router消费；实际消费沿后续TEACHER_ROUTER_INPUT记录。

## 已发现的Token摘要差值

同任务Kev微调 Model-only ON Max：900秒Agent超时，官方仍有Reward1。21:31:32.557191的AGENT_END为TIMEOUT；最后响应在21:31:32.675539到达，18379输入＋853输出，共19232 Token。

官方agent_result摘要为221312输入＋16366输出＝237678；逐请求账本为239691输入＋17219输出＝256910。摘要在Agent结束时取值，随后线程响应到达、追加共享provider_metrics列表，形成上述差值；完整已发生消费沿逐请求账本计量。

## 复用范围

同Harbor任务可复用DefaultAgent循环、ModelRouter、教师、工具反馈与日志。新任务提供题面、task.toml、镜像和原Verifier；当前RQ1批量入口固定Terminal-Bench2.0的Registry和任务元数据，新增任务需接入这些材料。其他Benchmark还需接入其工具环境与官方评分器；当前完整Agent的实跑范围为Terminal-Bench2.0/2.1。
