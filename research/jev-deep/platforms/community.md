# Community Evidence: TypeSafe Jev (System One / typed decision model)

- platform_id: community
- tier: 2 / scene: community / depth: deep
- scope: linux.do, v2ex, 52pojie, hacker-news, reddit/zhihu via public discovery
- Q0: Jev = TypeSafe AI System One typed decision model
- collection window observed in sources: ~2026-09-15 (launch) to ~2026-09-29
- note: forums are experience and public discussion, not ground truth

---

## 结论

社区里关于 Jev 的实操证据已经超过 5 条可用条目，但密度分布很不均匀：

1. **Codex 集成**是中文社区最热的实操话题；正确路径是官方 TypeSafe Skill / Agent Skill，而不是把 Jev 当聊天模型后端换进 Codex。
2. **训练/自训**：官方模型权重闭源、无客户微调接口；社区讨论主要集中在开源复刻、在参数不动的 LLM 上读 logits、以及 Laya 一类开放决策模型的微调对比。
3. **编码之外的用例**很多：浏览器操作、PR 审查、安全管道、内容审核、SEO 批处理、论文筛选、字幕质检、智能家居、游戏状态选择等。
4. **批评意见**集中在四点：官网倍数与独立实测差距大；“零幻觉”是类型安全而非事实正确；waitlist 门槛高；社区里大量 CSDN/SEO 文把 Jev 错当成编码大模型，造成信息污染。

---

## 官方主张（与社区经验分开）

| 项目 | 官方/首发材料 | 来源 |
| --- | --- | --- |
| 产品定位 | System One 模型：state + typed questions → Choice / Score / Noul + 概率/置信度 | docs.typesafe.ai; typesafe.ai/blog/introducing-system-one-models-and-jev |
| 模型版本 | `jev-1.13.0`；别名 `jev-latest` / `jev-preview` | docs.typesafe.ai/models; awesome list 快照 |
| 接口 | `POST /v1/systemone` | docs |
| 定价 | $0.042 / 1M input tokens；output 免费 | 官方模型页 |
| 延迟 | 官方称 70–500 ms | 官方首页/博客 |
| 性能主张 | 首页约 193.6× 更快、444.6× 更便宜；launch thread 称 20–200× / 40–400× | 官方博客（社区独立分析会对照这些数字） |
| 训练方法 | RLCD（Reinforcement Learning for Calibrated Decisions）；架构未公开 | 官方博客 + HN 创始人回复 |
| 微调 | 审阅材料中无客户 fine-tune / LoRA；权重不开放 | 多方社区材料一致 |
| Agent 集成 | 官方 Skill：`typesafe-ai/skills`，Claude Code / Codex / PI 等 | github.com/typesafe-ai/skills; 社区实测文 |
| 模态 | 文本/JSON state；图像、音频、视频不支持 | docs / awesome list |

> 这些是 vendor claims。社区经验在下面单独列出。

---

## 证据总表（社区/第三方）

| # | 主题 | 来源 | 类型 | 日期 | 核心内容 | 证据可信度 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | HN 发布讨论 | [HN 49717558](https://news.ycombinator.com/item?id=49717558) | 主帖+520 评论；约 1988 点 | 2026-09-15 起 | RLCD/校准讨论；“zero-shot classifier” 被创始人认可；“can’t hallucinate” 争议；waitlist 抱怨；用户 porridgeraisin 称已获准入并提醒 OOD 行为可能更差 | 高（一线讨论） |
| 2 | Codex 实操 | [掘金 · 沉默王二](https://juejin.cn/post/7688401277182066738) | 中文开发者实测 | 2026-09-23 | 官方 Skill 安装；Jev Choice 决定下一步动作；`confidence≥0.8` 执行；实测返回 `jev-1.13.0`，token 495/63，choice=`web_search` conf=0.99 | 高（有截图与 JSON） |
| 3 | Codex 内容农场噪声 | [CSDN 多篇 “Jev 接入 Codex”](https://blog.csdn.net/weixin_29032337/article/details/166717132) 等 | 大量同质博文 | 2026-09-26~27 密集发布 | 把 Jev 描述成编码/聊天后端，指导用 OpenAI 协议把 Codex 换成 “Jev 主力模型”；与官方 System One 定位冲突；典型 SEO 批发文 | 低（错误信息/营销型） |
| 4 | 分类 vs 微调 | [LinkedIn pulse](https://www.linkedin.com/pulse/can-typesafe-jev-replace-large-llms-fine-tuned-bert-classifying-ning-ew3ne) | 第三方实验叙述 | launch 期 | 小数据集、不愿训模型时，Jev 接口可替代本地 LLM 与 fine-tune BERT；结论偏“小数据用 API” | 中（页面被 LinkedIn 451，依赖搜索摘要） |
| 5 | 失败案例/批评 | [backnotprop poker eval](https://backnotprop.com/blog/jev-poker/) | 独立行为评测 | 2026-09-17 | 30 spots 与 solver top action 约 63% 一致；明显 nuts spot 上 Jev 16/16 全下注；作者批评 TypeSafe 本次发布缺公开 eval，担心 naive 部署 | 高（方法可复述） |
| 6 | 推文统计拆分 | [OpenChamber](https://openchamber.dev/blog/jev-typesafe-ai/) | 12,759 tweets 分析 | 2026-09-17/19 | 厂商 193.6× vs 用户报告中位约 7×（215 数）；成本中位约 30×；延迟中位 76ms；waitlist 提及远多于价格抱怨；批评者称 “really smart switch statement” | 高（方法与限制写明） |
| 7 | 独立核验 | [The Jev File](https://jev.novcog.us.com/) | 独立分析 | 2026-09-16 | 独立测试约 5× 快于 Mistral Small 4、8.6× 更便宜；“can’t hallucinate” 对形状成立、对事实不成立；CEO 对 “zero-shot classifier” 回 “exactly right!”；无 paper/无校准曲线 | 中高（独立站，引用官方数字并核验） |
| 8 | 开源替代与微调 | [DEV · Laya vs Jev](https://dev.to/vishalmysore/what-is-laya-laya-vs-jev-with-live-demo-4j6e) | 开源实验 | 2026-09-26 | Laya 421M ModernBERT + decision head，Apache-2.0；Jev 在大数据标签集上更强；Laya 需 fine-tune 与 temperature 重拟合；共享盲区：文本-only、不可靠算术 | 高（可复现实验 + 免责声明） |
| 9 | 接口级复刻实验 | [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | preregistered 参数不动模型实验 | launch 后 | 在 Qwen3-4B 上读选项字母 logits，而非生成 JSON；闭集分类精度与 grammar-constrained JSON 基本持平（0.907 vs 0.909），短文本约 4× 快；明确“不是复刻 Jev 权重” | 高（预注册+可复现） |
| 10 | 用例目录 | [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) | 社区 awesome | 快照 2026-09-19 | 大量路由/审核/抽样/agent 技能；含 Codex skill、Paper Radar、JEV Case 等 | 中高（集合索引，需抽查） |
| 11 | Codex/agent 生态仓 | GitHub 搜索 | 仓库 | 2026-09-21~29 | `teempai/jev-in-codex`、`leepokai/jev-guard`、`win4r/jev-skill-suggester`、`455-dIAO/jev-codex-router-skill`、`EthanSMC/jev-codex`、`kerpopule/hermes-jev-skills` | 中（证明活跃度，不等于生产质量） |
| 12 | 开源训练/复刻仓 | GitHub 搜索 | 仓库 | 2026-09-29 前后 | `TheoLeeCJ/SemIf-OpenJev`、`Heman10x-NGU/openJev-verdict-2.0`（自称 151M 非自回归引擎，typed-decisions 指标）、社区 “jevlikes” 训练讨论 | 中（社区自称指标，未独立复核） |
| 13 | 论坛线索 | DDGS | 标题级 | launch 期 | linux.do “TypeSafe AI 发布 Jev - 只做判断的模型 - 前沿快讯”；知乎 “告别字符串幻觉…”；链接字段为空 | 低-中（有标题，无正文） |
| 14 | 灰色操作 | [Futureppo/typesafe_register](https://github.com/Futureppo/typesafe_register) | GitHub 仓库 | 2026-09-29 | “typesafe.ai注册机…无限jev”，社区为绕 waitlist/额度制造账号 | 低质量实践证据，但反映准入压力 |

---

## 主题一：人们如何训练 / 使用

### 官方模型如何“训练”（社区认知）

- TypeSafe 说 Jev 用 **RLCD**，即针对校准概率的强化学习；不是传统 RLHF 生成偏好文本。
- HN 上创始人（CompleteSkeptic）确认架构“先保密”，并把重点放在数据。
- 用户 `porridgeraisin` 解释 RLCD 直觉：对错误答案的高置信概率施加更大惩罚；同时提醒 **OOD 行为可能与 LLM 不同，理论上可能更差**。
- OpenChamber 记录：截至发布窗口 **API 无 fine-tune 选项**；也有人提议“用 Jev 标注，再训小模型”。

### 社区实际在“训”什么

| 路径 | 做法 | 结果/含义 |
| --- | --- | --- |
| 接口复刻 | mini-jev：参数不动的 LLM，读字母选项 logits | 证明“typed decision 接口”部分可用现有模型 + 好的提问设计逼近，不必等 Jev 权重 |
| 开源决策模型 | Laya / openjev 系 | 需要 specialising（fine-tune 或 expert heads）+ 本地概率重拟合；不适合零样本硬切阈值 |
| 自建引擎 | openJev-verdict-2.0 等 | 自称在 LocalLLaMA/typed-decisions 上超 Jev/Laya；属社区自称，未复核 |
| 标注+二次训练 | 推文讨论 | 用 Jev 打标，再训小模型；需要防标签误差放大 |

**使用上社区共识（来自可用经验）：**

- 把 Jev 放在“判断层”，LLM/代码放在“执行层”。
- 有可评估的重复判断（路由、筛选、分类）先试；不可逆动作用置信度阈值转人工。
- 先拿自己数据测校准，再谈阈值自动化。
- 闭源权重 + 无微调，意味着“定制”只能通过 state/问题设计与外围代码。

---

## 主题二：Codex 集成

### 正确路径（有实测）

1. 官方 Skill 安装（掘金实测给出的命令）：
   - Claude Code: `claude plugin marketplace add typesafe-ai/skills` + `claude plugin install typesafe@typesafe-ai`
   - 其他 Coding Agent: `npx skills add typesafe-ai/skills --skill typesafe-ai`
2. 设置 `TYPESAFE_API_KEY`
3. 任务提示词强制：下一步动作由 Jev Choice 决定；`confidence ≥ 0.8` 执行，否则 `human_review`
4. 实测响应示例（社区）：
   - model: `jev-1.13.0`
   - usage: input 495 / output 63（输出免费）
   - choice: `web_search`, confidence 0.99

作者感受：Jev 把 Agent 的“判断”和“执行”拆开；在意图路由上 token 消耗远低于大模型；并认为能减少 Codex 额度压力。

### 社区里的其他 Codex/agent 集成形态

- **模型/努力度路由**：`JevRouter`、`jev-codex-router-skill` — 用 Jev 选模型或 reasoning effort。
- **工具/技能选择**：`jev-skill-suggester`、`jev-in-codex` — Jev 推荐已安装 skill 或工具。
- **安全层**：`jev-guard` — 对 tool call 打风险分 deny/ask/allow；检测结果里的 prompt injection。
- **上下文压缩**：`codex-jev-compaction` 等 — 用 Jev 判断历史 tool call 是否还需要。
- **浏览器自动化**：`EthanSMC/jev-codex` — Jev 选动作，Codex 当前对话写字段文本。

### 必须区分的错误用法

CSDN 在 9/26–27 出现大量“Jev 模型接入 Codex”模板文，常见错误包括：

- 把 Jev 说成编码/聊天主力模型，用 `chat/completions` 当 Codex 后端；
- 描述成“长上下文编码智能体”；
- 部分文称权重已开源/部分开放，与“托管 API + 闭源权重”冲突。

这些文适合当作 **社区误解与 SEO 噪声样本**，不适合当产品事实。

---

## 主题三：编码之外的用例（社区报告）

OpenChamber 对 launch 四天推文的整理，以及 GitHub/awesome 列表，显示用例远超 coding：

| 类别 | 代表场景 | 社区报告（作者自述，未复测） |
| --- | --- | --- |
| Agent 决策 | 浏览器 flight-search、computer use、tool-call 替代 | 7s/$0.0039；155× 便宜于 Opus 5 一类数字（自述） |
| 代码周边 | PR review、ESLint 规则、agent CI 作弊检测 | ~$0.00007/PR；90% 与规则自身结论一致 |
| 安全/审核 | security pipeline、safety classifier、email fraud | 比小模型更便宜且自述准确率更高 |
| 数据批处理 | 论文分类、YouTube 评论、SQL 扩展、DuckDB | 1018 篇论文 $0.08；20700 评论 2m27s/$0.20 |
| 内容/媒体 | 字幕质检（GeekLink）、SEO audit、ad DOM 移除 | 字幕按 cue 做 Noul 判定，低置信转人工 |
| 本地/家居 | Home Assistant、DroidJev 点击器 | 把 Choice/Score/Noul 暴露为自动化实体 |
| 游戏/实时 | Othello、Snake、Mario、Doom、Wikiracing | 状态结构化后每 tick 选动作；Doom 约 $7/小时（官方 demo） |
| 非编码判断 | 招聘简历打分、约会资料评分、模拟客户问卷 | HiringCafe 一类测试；Hinge 评分 70ms/$0.0001（自述） |
| LLM 评测 | Arize：decision model 替代部分 LLM judge | 文章主张可省成本；属分析文而非独立复测 |

社区 awesome 里还出现 Paper Radar（arXiv 筛选）、JEV Case、OpenTelemetry 日志标注、量化交易 dry-run 等。

**重要边界（社区反复出现）：**

- Jev 无图像输入；Doom/driving 一类 demo 的环境是文本/结构化预处理。
- 选择合法选项 ≠ 选择最优选项（poker 评测、魔方 94 步 vs 参考 22 步一类例子）。
- OCR、检索、执行器仍是瓶颈；Jev 只加速被替换的那一小步。

---

## 主题四：批评与争议

### 1. 倍数营销 vs 独立测量

| 指标 | TypeSafe 首页/launch | OpenChamber 用户自述中位 | novcog 独立测试 |
| --- | --- | --- | --- |
| 加速 | 193.6× / 20–200× | 约 7×（Q1=2×, Q3=20×） | 约 5× vs Mistral Small 4 |
| 成本 | 444.6× / 40–400× | 约 30×（Q1=5×, Q3=85×） | 8.6× vs Mistral Small 4；1.6× vs DeepSeek V4.1 Flash |
| 延迟 | 70–500ms | 中位 76ms（Q1=2ms, Q3=270ms） | 未作为主结论 |

推文里最常见被复读的数字是首页的 193×，几乎没有独立验证。

### 2. “零幻觉”措辞

HN 主线批评：

- 类型安全保证输出形状，不保证事实正确。
- 高置信错误仍是错误。
- 创始人自己也承认可能 “confidently wrong”。
- “0% hallucination” 图被 novcog 指出对应 schema 匹配，而非实证错误率。
- 有人指出 noul 在 OOD 上会被迫给出 yes/no，缺少弃权语义；另一方认为可通过问题设计补上 Choice 选项。

### 3. 与既有分类器/编码器的关系

- `@NathanFlurry`（高浏览批评）：Jev 像 “really smart switch statement”。
- `@alexisgallagher`：开发者对 encoder-only classifier 陌生。
- novcog：被问是否 “basically a zero-shot classifier” 时 CEO 答 “exactly right!”。
- HN 也有人指出：LLM 也能返回短标签；比较基线应是“你已有的最短可靠调用”。

### 4. 训练/校准主张未公开

- 无 paper、无公开校准曲线、无 ablation。
- TypeSafe 说公开 eval 会 “reward bad actors”，因此会弱化公开基准（创始人公开发言，见 OpenChamber 引述）。
- 社区普遍建议：阈值必须用自己数据验证；0.95 置信度不会自动等于 95% 正确率。
- Laya 对照材料也显示：即便开源模型，ECE 在温度重拟合前后可差很多；“高置信”本身不是保证。

### 5. 准入与信息污染

- OpenChamber：waitlist 提及 507，无访问 363，远多于信任/价格讨论。
- GitHub 出现 “typesafe 注册机 / 无限 jev” 一类灰色工具，说明资源稀缺被试图绕过。
- 中文社区 CSDN 模板文密集，且经常把 Jev 定位说错。

### 6. 非编码实验中的失败与意外

- **Poker**：简单 draw 场景接近 solver，明显 nuts 场景系统性错误（check 0% vs 实际应 check）。
- **魔方**：报告 94 步 vs 参考 22 步，说明“合法动作”不等于“好策略”。
- **假命题 yes-bias**：`@mattn_jp` 用 LLM 模仿实验提示可能的偏置，但该实验本身不是对 Jev 的直接测量。
- **本地替代性能**：有开发者报 DGX Spark 上 40ms/decision 的独立实现，**不是** Jev 本地跑通。

---

## 中国社区（linux.do / v2ex / 52pojie / zhihu）

| 站点 | 检索结果 | 说明 |
| --- | --- | --- |
| linux.do | DDGS 出现标题 “TypeSafe AI 发布 Jev - 只做判断的模型 - 前沿快讯 - LINUX DO” | URL 字段为空；discourse API 返回 403；无法读正文 |
| zhihu | 出现标题 “告别字符串幻觉：TypeSafe 发布 System One 决策智能大模型 Jev - 知乎” | URL 字段为空，正文未取到 |
| v2ex | 未检索到实质性 Jev 讨论条目 | discourse `/search.json` 404 |
| 52pojie | 未检索到实质性 Jev 讨论条目 | 公开索引无命中 |
| 掘金 | 沉默王二 Codex 实测；杜克文官方博客中文整理 | 实操 + 官方叙事转译 |
| CSDN | 大量 “Jev 接入 Codex” 同质文 | 内容农场/误解样本 |
| SegmentFault / juejin / xugj520 等 | Codex skill、官方博客解读、应用案例汇总 | 混杂官方转述与社区体验 |

中文社区的高价值部分是 **掘金 Codex 实操**；低价值部分是 **CSDN 批发教程**。linux.do/zhihu 线索存在但本轮未取到正文。

---

## 真实体验 vs 营销/转述：如何分层

| 层级 | 例子 | 使用建议 |
| --- | --- | --- |
| A. 可复述实测 | 沉默王二 Codex Choice 调用；backnotprop poker；mini-jev preregistered；Laya 开源实验 | 可作为设计参考，仍需自测 |
| B. 二手测量汇总 | OpenChamber 推文统计；novcog 独立分析；LinkedIn BERT 对比摘要 | 看中位数与方法限制，勿抄首页倍数 |
| C. 索引/转述 | awesome lists、掘金官方博客整理、DataCamp/教程站 | 用来发现项目，不当性能证据 |
| D. 内容农场/误解 | CSDN “Jev 当 Codex 主力模型”系列 | 当反例；勿按其配置操作 |
| E. 官方主张 | typesafe.ai / docs / launch blog | 单独列出；与社区对照 |

---

## 对使用/训练/Codex/超编码用例的综合判断

1. **怎么用**：官方 Skill 或直接 `POST /v1/systemone`；state + 少量原子问题；代码持有阈值与副作用。
2. **怎么“训”**：官方模型不可微调；社区路径是 (a) 问题/state 设计逼近任务，(b) 用 Jev 打标再训小模型，(c) 走 Laya/openjev 等开源决策模型自己微调。
3. **Codex**：Skill 路由/守卫/工具选择是合理用法；把 Jev 当聊天编码后端是错误用法。
4. **超编码**：任何“重复、闭集、可评估”的判断都值得试；不可逆动作与高风险分类必须自己测校准。
5. **采信策略**：独立实验（poker、mini-jev、Laya）> 汇总统计（OpenChamber、novcog）> awesome/教程 > 内容农场。

---

## 查询与工具痕迹

已执行的公开检索/抓取（只读）：

- `fast_search.py --provider hacker-news --query 'Jev TypeSafe' / 'TypeSafe Jev' / 'Jev TypeSafe model'`
- `fast_search.py --provider ddgs`：community-site 组合词、training/fine-tune、codex 实操、批评/review、linux.do 等
- `fast_search.py --provider github`：training/reimplementations、codex integrations
- `fast_search.py --provider discourse`：linux.do（403）、v2ex（404）
- WebFetch：掘金 Codex 实测、掘金官方解读、CSDN 模板文、backnotprop、OpenChamber、jev.novcog.us.com、DEV Laya vs Jev、mini-jev、awesome-jev、HN 49717558 等

本轮未修改工程源码；本报告为唯一新增/写入文件（见下）。

---

## 报告输出

- Path: `/Users/sunyiyang/Desktop/Project/路由/research/jev-deep/platforms/community.md`
