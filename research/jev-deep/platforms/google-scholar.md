# Google Scholar 检索报告：TypeSafe AI Jev（System One 决策模型）

- 平台：google-scholar（tier=1, academic, deep）
- 检索时间：当前会话
- 检索脚本：`python3 /Users/sunyiyang/.codex/skills/research-router/scripts/fast_search.py --provider google-scholar`
- 检索词（全部执行）：Jev TypeSafe decision model；Jev typed decisions LLM replacement；Jev model training；Visual Jev；Jev in the wild ecosystem；decision model typed choices confidence；TypeSafe AI Jev；Jev judge agent；Jev low latency decision；Jev rubber stamp typed；RLCD reinforcement learning calibrated decisions Jev
- 增补：WebFetch 核对了 6 篇 arXiv 摘要页（2609.26550、2609.29429、2609.30216、2609.25845、2609.26758、2609.22753、2609.24574、2609.29769）

## 结论

Scholar 对 Jev 的覆盖已成规模：围绕 2026 年 9 月 TypeSafe 发布的 Jev，检索到约 20 篇直接相关文献（另有一批外围/对比文献），全部集中于 2026 年 9 月，引用数极低（0–2），属于发布后一个月内的新文献。覆盖主题包括：方法与输出接口（typed choices / 概率 / 置信度）、训练路线（RLCD，仅见厂商公开叙述，无一手训练细节）、与 LLM judge 的成本/延迟/精度对比、领域应用（边缘编排、法务、诈骗筛查、对齐失败检测、移动 GUI、渗透测试、交通事故文本等）、生态分析（GitHub 2170 个项目）以及一批安全与可靠性批评（选项命名翻转、提示注入、校准偏差）。

独立性判断：在本次 Scholar 结果中，未发现 TypeSafe AI 自家署名的论文；所有 Jev 相关条目均为第三方通过公开 API（typesafe-ai/jev，常见版本号 1.13.0）进行的评测、应用或批评。厂商信息均以"厂商公开规格/公告"形式被第三方引用（如 Jev、Jev-Ultrafast 规格，RLCD 这一训练名）。训练细节缺失：RLCD 只有名称与效果叙述，无数据、超参、架构隔离实验；SSRN 条目明确指出公开叙述无法把训练、架构、数据的贡献拆开。eScholarship 校准审计也写明无法查看 Jev 自身的训练数据。

检索噪声：通用词（training、ecosystem、rubber stamp、visual）大量命中 Japanese Encephalitis Virus（JEV）文献（如疫情生态学、CRISPR 检测，引用数十至数百），与本题无关，已在下表排除。

## 已确认事项

### 1. 方法与输出接口

- Jev 被一致描述为：接受自然语言问题 + 结构化输入，返回预定义类型上的选择（choices/binary judgments）、标签概率与置信度，不生成自由文本（JEV-as-a-Judge；Type-Safe Is Not Error-Free；Just Ask Jev；Jev in the Wild）。
- 调用形态：多个 typed 问题可在一次调用内对同一输入并行求解（Just Ask Jev；Control the Harness；Jev in the Wild）。Jev-Mem 摘要称单次调用内回答多题、查询延迟 0.93 秒（比对照低 36.7%）。
- 版本线索：评测常固定在 Jev 1.13.0（Meng 校准审计；JevOut）；Barbosa 论文提到厂商公开规格中的 Jev-Ultrafast 变体。

### 2. 训练方法

- 公开叙述的训练路线名为 RLCD（Reinforcement Learning for Calibrated Decisions）：Just Ask Jev、Control the Harness、SSRN Williams 论文、ResearchGate Ngoc 论文、Barbosa 论文均引用此名。
- Visual Jev 展示了厂商之外的一条可复现路线：对视觉 backbone 做 answer-supervised post-training（宏平均准确率 70.6%→76.1%），并指出 typed head 相对语言模型头读出没有稳定优势；这属于"Jev 风格"视觉选择模型研究，与专有 RLCD 的复现无关（From Text Decisions to Pixels 明确声明未复现专有 RLCD、未与 Visual Jev 做配对实验）。
- 缺失：无任何检索到的文献给出 Jev 本身的训练数据、模型规模、奖励设计、超参或消融。SSRN 条目原文要点："Its public account does not isolate the effects of training, architecture"（公开叙述未拆分训练与架构效应）。结论：训练细节在 Scholar 层面缺失，现有证据均为第三方对 API 行为的测量或对厂商公开说法的转述。

### 3. 与 LLM 的对比（按主题）

| 主题 | 文献 | 关键数字/主张 |
|---|---|---|
| Judge 成本与延迟 | JEV-as-a-Judge（Li et al., arXiv:2609.26550, 2026, 被引 2） | 16 个 generative/reward judges 对比；在可直接读出判定的任务上距 GPT-6 三个点内，费用为其 0.36%，中位延迟 0.15 秒；预先固定阈值后的级联比 GPT-6 准 0.9 点、费用 41%；在 math/code/logic 等需推导的任务落后；风格对抗与无参考散文上路由失效 |
| Rubric judge 替换 | JEV vs. LLMs as Rubric Judges（Rao & Callison-Burch, arXiv:2609.29769, 2026） | 9 个 panel、27 组配对中仅 8 组有显著差异；LLM judges 成本 29–325 倍、耗时 30–220 倍；LLM 大量重复 Jev 最自信的错误，级联最多再提升 ≤2.0 点 |
| 文本标注（CSS） | Evaluating Decision Models for Text Annotation（Ibrahim & Zaki, arXiv:2609.24574, 2026, 被引 1） | 18 任务/7977 条；决策模型在 15 个任务中 14 个落后于逐任务最优 LLM，中位差距 11.6 macro-F1，中位成本低约 44 倍；置信度校准好于 19 个 LLM 中的 16 个，但 3 个 frontier 模型中位校准误差更低；低置信度转 LLM 的级联成本为纯 LLM 的 1/4–1/2 |
| 边缘服务编排 | Replacing LLMs with Jev for Low-Latency Edge Service Orchestration（Li et al., arXiv:2609.22753, 2026, 被引 1） | 8280 条验证请求；33 个测试条件下相对最快 LLM 决策延迟降低 22.7–64.5%；四字段结构化输入上每次正确决策费用低 59.7–80.9%；宽输入是替换边界；实时路径上保持 0.91–0.95 按时精确，LLM 低于 0.1；重复描述缓存可让 LLM 追平延迟，Jev 的收益在新决策上 |
| 对齐失败检测 | Just Ask Jev（Guo et al., arXiv:2609.29429, 2026） | RLCDAlignBench：10 类对齐失败、44 benchmarks、5 个目标模型；单一通用问题零样本中位 AUROC 0.886，多数 benchmark 胜过有监督方法；问题措辞影响小、输入字段影响大；与参考打分器对人工标签的一致度相当；成本比 LLM-judge 低 63 倍；代码 github.com/sumleo/RLCDAlignBench |
| 法务文档理解 | Same Scores, Different Decisions（Zhang et al., arXiv:2609.27678, 2026） | Jev 与 9 个语言模型对比；Jev 成本与中位响应时间最低（摘要片段；细节未逐一核对） |
| 竞争/对照模型 | this-that-model-1.0（Cheng et al., arXiv:2609.23886, 2026） | 自称 30ms、极低成本的 typed decision model，以 Jev 为对比行之一 |

### 4. 应用与生态

- Jev in the Wild（Ling, Xue, Ye, arXiv:2609.30216, 2026）：截至 2026-09-22 的 2170 个 GitHub 公开项目；属性判定与打分使用最广，动作选择、内容过滤、模型/工具选择因领域而异；公众注意力集中在路由与界面 agent，与项目数不成比例。
- 交通事故文本（Rafe & Das, arXiv:2609.24052, 2026, 被引 2）：把警方事故叙述转成概率化事故变量，将 Jev 定位为带准入控制的 typed decisions；摘要注明 TypeSafe 于 2026 年 9 月发布 Jev。
- 电话诈骗筛查（Ren et al., arXiv:2609.23959, 2026）：CallScreenBench 上的 Open-Jev 判定研究（小模型 Jev 风格，与 LLM caller 转写对比）。
- 移动 GUI agent（Zhang, arXiv:2609.30186, 2026）：Jev-Mobile 作为执行器；当前候选接口无法处理树中缺失的视觉目标。
- 渗透测试 harness（Barbosa, arXiv:2609.28940, 2026）：JEV 与开源 Laya 作为 LLM pentest agent 的 System One 决策层；含"有/无 TypeSafe System One"的对照运行；评论了 RLHF/RLAIF/RLCD 等训练路线差异。
- 智能体记忆与控制（Jev-Mem arXiv:2609.23986 被引 2；REFLEX arXiv:2609.26532 被引 2；Control the Harness arXiv:2609.28919）：Jev 作为 agent 的快速 typed 决策层（记忆路由、选择性控制、企业编码 agent 的路由治理）。
- 科学语义选择（Deng et al., arXiv:2609.24965, 2026, 被引 2）：Jev 作为语义决策组件，完整语义正确率与其他配置持平，观测到的中位延迟最低。
- 6G 边缘意图编排（Li et al., arXiv:2609.23136, 2026, 被引 1）：与 2609.22753 同作者组的姊妹工作。

### 5. 安全与可靠性批评（独立证据）

- Type-Safe Is Not Error-Free（Sun, Xu, Shi, Yang, arXiv:2609.26758, 2026, 被引 2）：仅改选项名与 rubric 的绑定（0/1 → no/yes）即可让 AUC 从 .94 掉到 .23；托管模型 AUC .8146→.5806，翻转率是重测下限的 24 倍；type-error rate 全程 0%——类型安全不等于语义正确。
- Decision Hijacking（Wu, Lim, arXiv:2609.28613, 2026）：针对 Jev typed 概率决策的提示注入攻击研究。
- JevOut（Xu, arXiv:2609.30243, 2026）：自然上下文可使 Jev 1.13.0 等决策模型转向错误答案。
- 校准审计（Meng, eScholarship uc/item/4t4449jv, 2026）：对 Jev 1.13.0 做 3244 次评测、覆盖 2372 个不同条目；顶级标签校准与开源/通用分类器不同；无法查看 Jev 训练数据或预训练暴露。
- Typed Evaluation Models / Conflict vs Ignorance（Vázquez, fs.unm.edu NCML, 2026, 被引 2）：boolean/Noul 类型上，冲突样本概率约 0.50–0.57，"无知"样本约 0.46–0.48，说明 Jev 在证据不足与证据冲突之间的坍缩现象。
- Calibration-Aware RL 综述（Li, Miao, Krishnan, Padman, CMU kilthub, 2026）：把 TypeSafe Jev 列为"暴露决策与概率字段的 typed 决策服务"代表；与 JEV-as-a-Judge 同作者组（CMU Heinz 学院背景人名），属独立学术综述。
- Calibration Does Not Compose, Types Destroy Vagueness（Ngoc, ResearchGate PDF, 2026）：理论批评——校准不可组合；把 Jev 归入 memoryless typed calibrated heads 类。

### 6. 独立性与厂商关系

- 本次 Scholar 结果中没有 TypeSafe AI 署名条目；评测全部通过公开 API（typesafe-ai/jev）完成。
- 厂商痕迹仅出现在被引用的公开材料中：TypeSafe 2026-09 发布公告、Jev/Jev-Ultrafast 规格、RLCD 这一训练名、托管版本号 1.13.0。
- 未确认：作者单位与厂商的关联（arXiv 摘要页通常不列机构；个别作者名与厂商可能重合，本次未做作者消歧）。Visual Jev（Guanxu Yu, Yuhang Yao）与边缘编排组（Delong Li 等）是否与厂商合作，摘要中无声明，按独立处理但保留不确定。

### 7. 引用情况

- Scholar 显示的被引数普遍为 0–2（发布约一个月，正常）。最高 2 次的条目：JEV-as-a-Judge、Typed Evaluation Models、Calibrated Decisions at Scale、Type-Safe Is Not Error-Free、Visual Jev、Jev for scientific decisions、Jev-Mem、REFLEX。
- 无条目显示两位数以上被引；不存在"高被引 Jev 论文"。

## 证据与限制

- 证据等级：全部结果为 Google Scholar 公开 HTML 发现层（discovery），excerpt 为摘要片段；关键条目已用 arXiv 摘要页 WebFetch 核对（上表中标注 arXiv 的条目）。
- PDF 可用性：几乎所有相关条目均可通过 arXiv `/pdf/` 直接获取；例外：eScholarship（4t4449jv，页面内容抓取为空，仅凭 Scholar 片段）；SSRN 7495638（抓取失败，仅凭 Scholar 片段）；NCML（fs.unm.edu 文章页，片段显示可用 experimental_evaluate SDK 调用细节）；ResearchGate Ngoc 论文有直接 PDF 链接。
- 限制：
  1. 训练细节缺失（RLCD 仅名称，无配方）——已按停止条件确认。
  2. 未做作者机构消歧，独立性判断基于署名与"第三方评测公开 API"这一事实模式。
  3. "decision model typed choices confidence" 等泛词命中的多为心理学决策文献，与 Jev 无关，已排除。
  4. 引用数极低，不能据此判断长期影响。
  5. Ibrahim & Zaki 论文摘要写的是"the first commercial decision model"，片段中未直接拼出 Jev 字样；结合上下文高度可能指 Jev，但本次未打开全文逐字确认，标注为推断。

## 未确认事项

- Visual Jev、边缘编排组与 TypeSafe 的实际合作/雇佣关系。
- Jev 训练数据、模型规模、RLCD 具体算法与奖励设计（Scholar 层面无一手材料）。
- SSRN Williams 论文与 eScholarship 校准审计的全文结论（仅摘要片段）。
- Ibrahim & Zaki 论文中商业决策模型的具体名称（推断为 Jev）。
- 厂商自家技术报告/博客是否在 Scholar 外形成独立索引（本报告仅限 Scholar 平台）。

## 检索到的相关文献清单（按主题）

| # | 标题 | 作者 | 年 | 引用 | 链接 | PDF | 性质 |
|---|---|---|---|---|---|---|---|
| 1 | JEV-as-a-Judge: Accept When Confident, Escalate When Unsure | Y Li, Y Miao, R Krishnan, R Padman | 2026 | 2 | arXiv:2609.26550 | 有 | 独立评测 |
| 2 | Typed Evaluation Models and the Collapse Between Conflict and Ignorance: A Case Study on Jev | MYL Vázquez | 2026 | 2 | fs.unm.edu/NCML_2/article/view/186 | 有（期刊页） | 独立案例 |
| 3 | Calibrated Decisions at Scale: ... Police Crash Narratives ... (Jev) | A Rafe, S Das | 2026 | 2 | arXiv:2609.24052 | 有 | 应用 |
| 4 | Type-Safe Is Not Error-Free | Y Sun, J Xu, J Shi, Z Yang | 2026 | 2 | arXiv:2609.26758 | 有 | 独立批评 |
| 5 | Calibrated Decision Models for Autonomous Penetration-Testing Harnesses | JAS Barbosa | 2026 | — | arXiv:2609.28940 | 有 | 应用+训练评论 |
| 6 | Decision Hijacking: Prompt Injection Attacks on Jev | T Wu, WYB Lim | 2026 | — | arXiv:2609.28613 | 有 | 安全 |
| 7 | How far can a commercial decision model's probabilities be trusted? | L Meng | 2026 | — | escholarship.org/uc/item/4t4449jv | 有（片段） | 校准审计 |
| 8 | JevOut: Natural Context Can Flip Decision Models | Z Xu | 2026 | — | arXiv:2609.30243 | 有 | 可靠性 |
| 9 | Replacing LLMs with Jev ... Low-Latency Edge Service Orchestration | D Li, X Wang, H Gong, R Lang, G Yu | 2026 | 1 | arXiv:2609.22753 | 有 | LLM 替换 |
| 10 | Fast Intent-Driven Service Orchestration with Jev for 6G Edge Networks | 同上作者组 | 2026 | 1 | arXiv:2609.23136 | 有 | 应用 |
| 11 | JEV vs. LLMs as Rubric Judges | D Rao, C Callison-Burch | 2026 | — | arXiv:2609.29769 | 有 | LLM 对比 |
| 12 | Open-Jev Judgments on CallScreenBench | S Ren 等 | 2026 | — | arXiv:2609.23959 | 有 | 应用 |
| 13 | Jev-Mem: System-One-Controlled Agentic Memory | D Jiang, Y Li, B Li | 2026 | 2 | arXiv:2609.23986 | 有 | Agent 应用 |
| 14 | REFLEX with Jev for Efficient Selective Control in LLM Agents | T Wu, WYB Lim | 2026 | 2 | arXiv:2609.26532 | 有 | Agent 应用 |
| 15 | Jev for scientific decisions | B Deng, S Fan, H Zhang, X Xie | 2026 | 2 | arXiv:2609.24965 | 有 | 应用 |
| 16 | Visual Jev: Accurate and Efficient Decisions from Shared Visual Context | G Yu, Y Yao | 2026 | 2 | arXiv:2609.25845 | 有+代码 | 方法（Jev 风格视觉） |
| 17 | From Text Decisions to Pixels: Jev-Style Visual Choice Model | X Zhou, X Yang, L Zhao | 2026 | — | arXiv:2609.29283 | 有 | 对照研究 |
| 18 | Jev-Mobile: Jev as an Executor for Mobile GUI Agents | L Zhang | 2026 | — | arXiv:2609.30186 | 有 | 应用 |
| 19 | Jev at the Agent Authorization Boundary | J Williams | 2026 | — | SSRN 7495638 | SSRN（抓取失败） | 训练路线评论 |
| 20 | Just Ask Jev: RLCD as Zero-Shot Detector of AI Alignment Failures | R Guo 等 9 人 | 2026 | — | arXiv:2609.29429 | 有+代码 | 训练名+评测 |
| 21 | Jev in the Wild: Functionality, Applications and Ecosystem | G Ling, M Xue, Z Ye | 2026 | — | arXiv:2609.30216 | 有 | 生态 |
| 22 | this-that-model-1.0 | Z Cheng, W Dai, J Sun | 2026 | — | arXiv:2609.23886 | 有 | 竞品对照 |
| 23 | Evaluating Decision Models for Text Annotation in CSS | H Ibrahim, Y Zaki | 2026 | 1 | arXiv:2609.24574 | 有 | LLM 对比 |
| 24 | Control the Harness, Control the Cost | A Abbasi, A Aqrawi, T Kwartler | 2026 | — | arXiv:2609.28919 | 有 | 企业应用 |
| 25 | Calibration-Aware RL for LLMs（综述，提及 Jev） | Y Li 等（CMU） | 2026 | — | kilthub.cmu.edu | 有（PDF） | 综述 |
| 26 | Calibration Does Not Compose, Types Destroy Vagueness | AKD Ngoc | 2026 | — | ResearchGate PDF | 有 | 理论批评 |
| 27 | Same Scores, Different Decisions: JEV and LMs for Legal Docs | F Zhang 等 | 2026 | — | arXiv:2609.27678 | 有 | 应用 |

## 停止条件核对

- Scholar 对 Jev 方法/应用的覆盖：已确认（评测、应用、生态、安全批评四类齐备）。
- 独立 vs 厂商相关：已区分（本次结果全部为第三方评测/应用；厂商信息以被引用的公开材料形式出现；无 TypeSafe 署名论文）。
- 训练细节缺失：已确认（仅 RLCD 名称与效果叙述，无一手训练配方）。
