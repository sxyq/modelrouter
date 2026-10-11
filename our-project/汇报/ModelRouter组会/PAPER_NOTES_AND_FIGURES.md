# 组会论文详细笔记 × 原始 Figure 对应表

> 2026-10-12；依据仓库 `our-project/literature/findings/F2.md`、`F3.md`、`F6.md`、`F7.md`、`our-project/planning/GROUP_MEETING_RESEARCH_BRIEF.md`、`research/task-level-cost-routing/literature/evidence/direct-evidence.md`、旧汇报讲稿与旧截图清单。**没有解压读取用户本轮的《汇报二.zip》**，其中可能存在的新增论文笔记与截图尚未并入。
> 下述“论文原图”指原 PDF 截图/裁剪资产；本轮仅将仓库中已有的真实 PNG 复制到本组会目录，不把新绘制的示意图伪称为论文原图。个别旧截图文件名未标 Figure 编号，需在正式投影前按原 PDF 核对。

## 1. Unified AI Gateway｜模型切换的隐藏缓存代价

- **问题**：传统 gateway 单独按模型性能/价格路由，模型切换可能使 KV 前缀不能直接复用，增加 prefill 与 TTFT。
- **方法**：联合考虑模型、执行位置、cache action（reuse / mapping / transfer / re-prefill）；是请求/系统控制平面的方案。
- **证据性质**：解析仿真与系统工作负载；不代表已在长程 Coding Agent 上证实任务成功率与真实总费用下降。
- **对应真实截图**：`assets/paper-figures/gateway_fig2_p03.png`（旧 PDF 物理 p.3 Fig.2）；`gateway_fig4_p05.png`（p.5 Fig.4）。
- **新版 PPT P04**：只展示 Fig.2 的传统 vs 联合对照，配 INFRAMIND 原图；Fig.4 作为备用放大。
- **我们的边界**：不假设跨 provider 或跨模型的物理 KV 可直接复用；将 reported cache usage、估算前缀重合、模拟命中严格分开。
- PDF：`research/task-level-cost-routing/literature/pdfs/38_Unified_AI_Gateway_A_Framework_for_Joint_Model_Routing_and_KV_Cache_Management.pdf`；https://arxiv.org/abs/2609.06940

## 2. INFRAMIND｜基础设施感知的多 Agent 编排

- **问题**：Agent 级编排若忽略队列、cache pressure、延迟和预算，会把质量和服务 SLO 目标割裂。
- **方法**：planner 选择 topology/roles；executor 在每步观察 queue depths、cache utilization、response latency 来选模型与推理深度；scheduler 做预算感知队列调度。
- **结果**：仓库 F2 记载论文在低负载下最高 +7.6pp 准确率与最多 7× 延迟改善，高负载 SLO compliance 最高 99.9%；这些是**论文原条件**，不能当作我们的结果。
- **图**：**待新增** `inframind_fig2_p02.png`，官方 PDF 物理 p.2 Fig.2（传统 MAS vs InfraMind）；p.5 Fig.3 备用。不能从旧 Gateway 图片伪造。
- **PPT P04**：与 Gateway 并列，强调“基础设施状态 + 逐步选模型/深度”已有先例。
- **重要差异**：文中 Flash/Concise/DeepThink 为 prompting/strategy 级设置，**不等于 provider 原生 reasoning_effort 参数**。
- PDF：`.../pdfs/39_InfraMind_Infrastructure-Aware_Multi-Agent_Orchestration.pdf`；https://arxiv.org/abs/2606.11440

## 3. MTRouter｜History–Model 联合表示

- **问题**：单轮 query router 看不到前几轮交互历史，不能据此判断后续模型成本/质量。
- **方法**：联合编码历史与候选模型，逐轮评估与选择；显式讨论 multi-turn 质量与费用。
- **图**：`mtrouter_fig1_p01.png`（p.1 Fig.1 单轮 vs 多轮），`mtrouter_fig2_p04.png`（p.4 Fig.2 History/Model encoder 与 outcome estimator），`mtrouter_table3_p06.png`（p.6 Table 3）。
- **PPT P05**：以 Fig.2 为主，说明 History 是路由输入而不是我们首创的第九组状态。
- **研究边界**：其多轮路由与我们的 Agent harness/tool/verifier 状态、provider 合法 effort 和终局 cost 目标并不完全相同。
- PDF：https://aclanthology.org/2026.acl-long.2045.pdf

## 4. PROGROUTER｜用进度账本做在线路由

- **问题**：固定一次性 query/cascade 路由无法跟踪多 Agent workflow 的中间目标和剩余时间/费用。
- **方法**：progress scorer + predictor + meta-gate；结构化 workflow ledger；逐步平衡 progress gain、time budget 和 long-term cost。
- **图**：**待新增** `progrouter_fig2_pXX.png`，官方 PDF Fig.2，**物理页未确认，不能臆造**。
- **PPT P05**：与 MTRouter Fig.2 对照：history embedding vs structured progress ledger。
- **我们的边界**：验证恢复、缓存连续性、合法 (model, native effort) 与完整任务 USD 是否增益需要单独消融；不是声称论文没做动态路由。
- PDF：https://arxiv.org/pdf/2608.25992

## 5. SWE-Router｜先探索 K 步再决定升级

- **问题**：prompt-only 对软件 Agent 成败难度判断有信息不足；部分轨迹提供增量信息。
- **方法**：弱模型先跑 K 个 exploration steps，读部分轨迹后判断继续弱模型还是升级强模型（通常是一次 continue/restart 决策）。
- **证据**：F2 记录在 SWE-bench Verified 的 Route-AUC 0.780（某模型对），比 K=0 非时序基线 +15.3pp；不能套用到我们的任务/模型池。
- **图**：`swe_router_flow.png`，原仓库已有 `visual_report_assets/crops/swe-flow.png`；**原 Fig.号需复核**。
- **PPT P06**：画面左侧，明确“已经付出 K 步探索成本”，不是每次调用都重新选模型。
- PDF：https://arxiv.org/pdf/2607.00053

## 6. TACIT-Switch｜何时把控制权永久交给强模型

- **问题**：便宜模型在轨迹中反复无效尝试，何时升级才能兼顾预算与成功率？
- **方法**：使用执行中的重复、停滞、异常等累积风险，预测 strong 能救回的概率/交接时点；**一旦 handoff 就永久升级**。
- **证据**：F2 记载论文相同成本附近较若干 task/step/fixed-prefix 基线提高 7.4–11.1pp 成功率；不可视为我们的实测。
- **图**：`tacit_switch_flow.png`，旧源 `visual_report_assets/crops/tacit-flow.png`；**原 Fig.号待复核**。
- **PPT P06**：右侧与 SWE-Router 对照。突出“何时切换”和“切换是否可逆”。
- **我们的边界**：我们拟议的是每个合法模型调用边界可重新选择 (model,effort)，不是单向永久 handoff；但恢复风险可借鉴。
- PDF：https://arxiv.org/pdf/2608.27911

## 7. Route-to-Reason｜模型 × 推理策略联合选择

- **问题**：只选 LLM 而固定 reasoning strategy，可能 overthink 或欠推理。
- **方法**：联合选择 (model, reasoning strategy)，估计组合的质量与输出 token。
- **图**：`rtr_fig1_p02.png`（PDF p.2 Fig.1，动态推理 vs 模型路由 vs RTR），`rtr_fig4_p04.png`（p.4 Fig.4，组合编码与 routing table）。
- **PPT P07**：主放 Fig.1；右侧画我们自己的 provider-valid model×effort 候选矩阵。
- **我们的边界**：论文的 reasoning strategy 与 API 原生 effort **不能直接画等号**；主要是 query-level，成本用 token 代理。
- PDF：https://arxiv.org/pdf/2505.19435

## 8. UniScale｜联合动作空间的更近先例

- **问题**：模型路由与 test-time scaling 被割裂优化。
- **方法**：将 (M, QP, CP, BS) 统一为推理时动作，LinUCB 在线学习质量–eFLOPs 奖励。
- **证据**：F6/F7 记载 ICML 2026 接收、单请求 QA / 数学推理，非长程 Agent 任务 USD 计费。
- **图**：**待核实是否需要截原 PDF 方法图**；目前仓库无单独裁剪 PNG，不冒充已有截图。
- **PPT P07**：作为右侧论文卡/引文，**不能写“首次提出 Model×Effort”**。
- PDF：https://arxiv.org/pdf/2605.30898

## 9. TwinRouterBench｜静态轨和真实动态轨

- **问题**：one-shot router benchmark 不足以代表 Agent 中途状态、失败与全任务真实账单。
- **方法**：静态 track 含 970 个 router-visible prefixes（520 instances）；动态 track 在 SWE-bench Verified harness 上运行，记录 official resolve 与 realized API spend。
- **图**：**待新增** `twinrouterbench_fig1_p02.png`，PDF 物理 p.2 Fig.1；当前只复制了 `assets/reference/twinrouterbench_pdf_p01_preview.png`（PDF 第 1 页预览，**不是 Fig.1 成品**）。
- **PPT P08**：将原 Fig.1 占左 60%，右侧写我们要用同一任务集/预算做真实 Agent 动态路由实验。
- **我们的边界**：其静态标签是条件 per-call tier，不等于完整任务最优联合 policy；动态结果也不是我们的结果。
- PDF：https://arxiv.org/pdf/2605.18859

## 10. 旧四篇与辅助证据：哪些不必再重做

- **Google CATS**：`cats_fig1_p02.png`、`cats_cost_definition_p04.png`；任务成本含工具使用/轨迹分配的证据。放 P03 只讲成本账本，旧版三页无需重做。
- **OpenSquilla / Agentic Routing**：`opensquilla_fig2_p06.png`；harness-native routing 已有先例，放 P05/P09 小图，不能宣称“我们首次看 Agent 状态”。
- **TRACE-Router**：`trace_router_key.png`（原 Fig.号未确认），其 admission 时选择固定后端的任务级 bandit 与当前逐次动态策略不同，可放 P09 备选。
- **EvoRoute**：`evo_route_trilemma.png`（原 Fig.号未确认），在线经验路由近邻，备选。
- **Price Reversal**：`price_reversal_eq2_p04.png`；成本计量公式来源，P03 小图。公式属于论文，不是本地实验。
- **MTRouter Table 3**：`mtrouter_table3_p06.png`；若结果页需要学术参考可用，注意不能当我们的数据。

## 11. 从这些论文导出的可检验研究定位

- 已有先例分别覆盖 cache-aware gateway、infra-aware model/depth selection、history/progress、temporal escalation、model×reasoning、真实动态评测。**我们不宣称首次做上述任何单项**。
- 拟议研究：每个**合法模型调用边界**，用决策前八组可观测 Agent 状态和合法候选 (model, native effort)，由 Kev-4B 或 Laya-421M 的 typed-choice router 做决策；最终以 **Episode Success、Total USD、Spend per Resolved、Latency** 与路由开销评测。
- 仍需实验回答：增量状态是否有效？joint action 是否比 model-only 好？缓存/History 是否有价值？完整任务目标是否改变策略？Kev/Laya 哪个在准确率、校准和开销上更合适？
- **状态口径**：八组是 Task/Subtask、Agent/Coordination、Context/Memory、Tool/Environment、Verification/Recovery、KV/Continuity、Temporal/Execution、Provider/Availability；History 是输入表示方案，不是第九组。
- **执行事实**：当前只有公开数据整理与 CPU 格式/加载检查，正式 GPU 微调、动态 Agent 评测尚未开始。

## 12. 新截图的准确补齐清单

| 缺图 | 目标 | 官方 PDF | 物理页 | 状态 |
|---|---|---|---|---|
| INFRAMIND | Fig.2 Traditional MAS vs InfraMind | https://arxiv.org/pdf/2606.11440 | p.2（待本地确认） | **未裁剪** |
| PROGROUTER | Fig.2 Progress-guided workflow | https://arxiv.org/pdf/2608.25992 | **未核实** | **未裁剪** |
| TwinRouterBench | Fig.1 Static vs Live Dynamic | https://arxiv.org/pdf/2605.18859 | p.2（待本地确认） | **未裁剪** |
| UniScale（可选） | 选最清晰的联合配置方法图 | https://arxiv.org/pdf/2605.30898 | 未核实 | **可选** |

请先在本地打开 PDF 核实 Fig.号、caption、PDF 物理页和截图裁切范围；真实裁剪保存到 `assets/paper-figures/`，与本表相同命名。**不要用生图模型重新画原图。**
