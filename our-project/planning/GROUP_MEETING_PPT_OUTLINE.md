# ModelRouter 组会 PPT 全新分镜规划 v6：论文原图融入整页生图

> 2026-10-12｜目标 16 页、约 20–22 分钟。**这是一份制作规划，不是已经生成的 16 页 PPT。**
> 旧版 `our-project/汇报/PPT/deck.html` 的呈现方式：完整 PNG 画面 + 真实论文 Figure 融入构图，少字、留白、统一暖纸白风格。旧四篇：Unified AI Gateway、Google CATS、OpenSquilla、Route-to-Reason。
> **v6 相比 v5 的变化**：从“论文列举 + 我们的方法”改成“5 条直接相关研究线 → 研究缺口 → ModelRouter → 数据/实验”；新增 SWE-Router/TACIT、UniScale、动态评测对照。论文内容依据 `../汇报/ModelRouter组会/PAPER_NOTES_AND_FIGURES.md`，详细截图目录见 `../汇报/ModelRouter组会/assets/paper-figures/README.md`。
> 本轮**没有读取《汇报二.zip》内部内容**；用户若补传解压文件，需要以原笔记为依据更新相应页。禁止深度研究、训练、付费 API。

## 1. 视觉方案：真正复刻旧汇报的“原图融入生图”

- **画布**：16:9，建议 1920×1080；背景暖纸白 `#f5f3ee`，白卡 `#fffefa`，正文墨色 `#17202a`，注释灰 `#66727d`，强调锈红 `#b45739`、青绿 `#2e766b`、蓝 `#4b7795`、金 `#bd8a36`。大标题用衬线，说明文字用无衬线。
- **两层制作**：生图只负责页面视觉、场景插画、图框、留白和背景；真实论文 Figure、箭头、公式、精确标题/数据由**后期独立叠加**。最终导出为一张完整页面 PNG；不能让生图模型临摹论文原图。
- **论文页构图**：一张论文图占画面 55–65%，另一侧最多“核心问题、方法动作、局限”三个短块；两篇对照页可 48%+48%，但文字必须可读。脚注：论文名、年份、Fig./PDF 页、来源。
- **原创方法页**：最多 4 个主盒 + 1 个反馈环，真实箭头与动作标签用矢量层绘制；不放虚构的数值/实验结果。
- **数据页**：生成底版后，数据图和数字从真实仓库统计表绘制并合成；数据集总行数不是动态标签总数。
- **整套每页一句结论**，每张 Figure 有唯一论证任务；讲解词写到 notes，不把一页做成论文正文。

## 2. 16 页新页序（论文 Figure 具体落位）

| 页 | 题目与一句话结论 | 画面构图 / 要叠加的真实截图 | 时间 |
|---:|---|---|---:|
| **01** | **ModelRouter：面向长程 Agent 的状态感知模型×推理档位路由** | Agent 多步轨迹封面；末端是 success 和 total cost 两个目标 | 0:40 |
| **02** | **一次调用便宜，不等于整个任务便宜** | 左右两条原创示意轨迹：廉价但反复失败 vs 较贵但快速完成；标“概念示例，非实测” | 1:00 |
| **03** | **成本应沿 Episode 计账** | 主图：`cats_cost_definition_p04.png`；辅助：`price_reversal_eq2_p04.png`；右侧原创 call→tool→verify 费用累计条 | 1:00 |
| **04** | **缓存与基础设施状态已经有人联合路由** | 左：`gateway_fig2_p03.png`；右：**待补** INFRAMIND Fig.2；页脚“Gateway 是系统 cache action，InfraMind 是 infra-aware model/depth” | 1:30 |
| **05** | **History、Progress、Harness 都是已有路由信号** | 左：`mtrouter_fig2_p04.png`；右：**待补** ProgRouter Fig.2；小角标 `opensquilla_fig2_p06.png` 只在空间足够时使用 | 1:30 |
| **06** | **部分轨迹与失败风险决定何时升级** | 左：`swe_router_flow.png`；右：`tacit_switch_flow.png`；底部用短线区分 K 步后一次升级 vs 自适应永久 handoff | 1:30 |
| **07** | **模型×推理强度联合选择也不是首次提出** | 左：`rtr_fig1_p02.png`；右：我们自己画的合法 (model,native effort) 矩阵；UniScale 作为明确的近邻引用，不将其 TTS 参数等同原生 effort | 1:30 |
| **08** | **真实 Agent 评测不能被静态 benchmark 取代** | **待补** TwinRouterBench Fig.1（Static Track vs Live Dynamic Track）；右侧说明 success + realized spend + cache accounting | 1:15 |
| **09** | **我们的研究缺口不是“多加几个状态字段”** | 五列文献覆盖矩阵：infra/cache、history/progress、failure/recovery、model×effort、episode success/$；区分已有人做和待验证组合；可在角落用 `trace_router_key.png` 备选 | 1:15 |
| **10** | **主流程：每个合法调用边界选一次 (model,effort)** | **原创核心大图**：Agent Harness → State Snapshot + Feasible Action Filter → Kev 或 Laya Router → Generative LLM；底部 Tool→Verifier→History 回环；右下 episode 终局 | 1:45 |
| **11** | **八组可观测状态怎样进入决策** | 八组状态分层图，沿时间轴标出 t 前可见与 t+1 才可见；History 是表示方式而非第九组 | 1:15 |
| **12** | **Kev-4B 与 Laya-421M 是替代的 typed-choice Router** | 左右两模型并列卡，箭头指向同一合法候选集合；标明不是答案生成模型、尚未 GPU 微调 | 1:00 |
| **13** | **公开数据多，不等于真实动态监督充足** | 14 源 / 6,600,628 异构行；Stage1 Choice 83,259、Stage2 Agent State 88,087、Effort 290 有效对；来源与标签语义分色 | 1:00 |
| **14** | **冷启动训练 + History 表示仍是实验设计** | 上半：同许可样本→Kev/Laya→校准；下半：最近 K 步 / 结构化摘要 / hybrid；明确未正式训练、LICENSE_PENDING | 1:00 |
| **15** | **如何在真实 Agent 任务上证伪我们的方法** | 左：Fixed/Admission/Model-only/Cache-only/Full-state 的对照梯度；右：5 RQ 和 success、total USD、$/resolved、Pareto、router overhead | 1:30 |
| **16** | **目前完成什么，下一步需导师决定什么** | 左完成：数据/CPU 适配；右待完成：GPU、Harness、动态实验；底部四个决策卡 | 0:55 |

建议讲解时把 P04–P08 看成五条连续的相关工作证据链，每页只讲**问题—方法—边界**，不按旧版每篇三页铺开。若时间仅 15 分钟，合并 P03→P02、P06→P05、P14→P13。

## 3. 第 10 页主流程图的准确结构（当前只规划）

```text
             决策前 8 组 Runtime State
                         ↓
[Agent Harness / call t] → [State Snapshot + valid action filter] → [Kev 或 Laya] → [(model_t, effort_t) 的生成式 LLM 调用]
           ↑                                                                        │
           └──────── [History/Recovery 更新] ← [Test/Verifier] ← [Tool/Environment] ┘
                                                                                     ↓
                                                                            [Episode end: success, USD, latency]
```

- **Kev 与 Laya 二选一**：不能画成串联，也不是执行 coding 任务的生成式模型。
- **动作合法性**：先过滤 provider 能力、effort 可用性、上下文长度、预算、可用性，再选择 `(m_t,e_t)`；不暗示所有 provider 都有相同档位。
- **反馈时序**：本次 test/verifier 结果只能进入下一次 t+1 的状态，不能提前泄露。
- **缓存事实**：reported cache tokens、估算前缀重合、模拟命中分开标注；不画跨模型物理 KV 无条件复用。
- **任务目标**：质量/成功约束下看完整 episode USD 与 spend per resolved；所有未测效果标 Proposed。
- **画面生产**：生图先生成 4 个盒子+下方闭环的留白与视觉风格；箭头、框内文字和状态标签在后合成阶段矢量绘制。

## 4. 实际截图库存与缺口

**已复制到组会目录的 15 张原论文裁剪**：
Gateway Fig.2/Fig.4；CATS Fig.1/Cost；OpenSquilla Fig.2；MTRouter Fig.1/Fig.2/Table3；RTR Fig.1/Fig.4；Price Reversal Eq.2；SWE-Router flow；TACIT flow；TRACE key；EvoRoute trilemma。另有 TwinRouterBench PDF 第 1 页预览 1 张，**不能冒充 Fig.1**。

**真正缺少、尚未生成的 3 张必需原图**：
`inframind_fig2_p02.png`、`progrouter_fig2_pXX.png`、`twinrouterbench_fig1_p02.png`。PDF 都已在 `research/task-level-cost-routing/literature/pdfs/` 中，需本地 PDF 渲染与真实裁剪；见详细论文笔记第 12 节。

## 5. 最小制作顺序

1. 先用已保存的截图制作 **P06（SWE/TACIT 双论文）** 一张完整视觉样张：这页无需等新增截图，能直接验证“原图融入生图”的效果。
2. 并行做 **P10（我们主流程）** 一张样张：检查箭头逻辑、状态与模型角色；不让生图自由改文字。
3. 对缺少的 3 张原图，按官方 PDF 核实页码与 Fig.，真实裁剪后放到 `our-project/汇报/ModelRouter组会/assets/paper-figures/`；再做 P04、P05、P08。
4. 最后完成其它页面；所有页面输出 PNG，复用旧 `deck.html` 的播放器样式或轻量串联。**不用先做 PPTX，不启动训练/深度研究。**
5. 投影尺寸核对原论文图的可读性、真实数据与“Proposed”标记；一次性检查即可，不引入 PR/CI 或繁琐工程门禁。

## 6. 给本地 Agent 的直接提示词

> 先读 `our-project/汇报/ModelRouter组会/PAPER_NOTES_AND_FIGURES.md` 和本 v6 规划，打开旧 `our-project/汇报/PPT/deck.html`，实际观看旧 P7/P14/P16 的 PNG 页面。沿用旧版暖纸白、衬线标题、细线卡片与完整页面生图的风格。已复制的 15 张真实论文截图位于 `our-project/汇报/ModelRouter组会/assets/paper-figures/`。**先只做 P06（SWE-Router/TACIT-Switch 论文原图融合）与 P10（ModelRouter 自己的在线闭环）两张 1920×1080 样张**；论文 Figure 必须用原 PNG 后合成，禁止图像模型临摹或改动图中文字；P10 精确箭头和术语也后合成。三张缺图 INFRAMIND Fig.2、PROGROUTER Fig.2、TwinRouterBench Fig.1 需打开官方 PDF 真实裁剪，不要伪造。其它页面先不生成。不要深度研究、GPU 训练、付费模型或额外工程流程。

## 7. 进度与边界

- 本轮**已做**：读仓库现有详细论文笔记、定位旧原始截图、复制 15 张真实 PNG 与 1 张参考图到本组会目录、更新此分镜规划与详细论文笔记。
- 本轮**未做**：解压《汇报二.zip》、新增 3 张 PDF Figure 的裁剪、制作任何整页生图/PPT、训练与动态实验。
- 原始论文图与当前拟议系统分层标注，不用论文数值冒充我们的实验结论。
