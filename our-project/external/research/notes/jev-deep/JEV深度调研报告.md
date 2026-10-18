# Jev 模型深度调研报告

- 调研方式：`research-router` 深度检索（deep），一平台一代理并行
- 调研日期：2026-09-30
- 平台报告目录：`research/jev-deep/platforms/`
- 本报告路径：`research/jev-deep/JEV深度调研报告.md`

---

## 一、结论

| 问题 | 结论 |
| --- | --- |
| Jev 是什么 | TypeSafe AI 的 System One 决策模型：输入 state + 类型化问题，输出 choice / noul / score 的带概率决策，不生成自由文本 |
| 官方如何制作与训练 | 方法名 RLCD（Reinforcement Learning for Calibrated Decisions）；公开学术与 GitHub 侧**没有**官方训练数据、架构、超参或权重 |
| 我能否自己训一个 | 可以训 **Jev-like** 决策模型；不能从公开源复现官方 Jev 权重。公开可复现路线：Visual Jev（LoRA answer SFT）、Kev（`kev.train`）、Laya（开放权重 + 微调笔记本）、Simple Jev RFDT、AnyJev（几乎不训） |
| 能否用在 ModelRouter | **能，且很贴**。Jev 生态里注意力最集中的用法就是路由与 agent 判断层；可作为任务级「模型 × 档位」事前选择器或守卫，也可自托管同类决策端点做对照 |
| 能否放进 Codex | **不能**把 Jev 写成 Codex 的 `model_provider` 替换 coder。正确路径是：官方 agent skill / hooks 旁路决策；或自托管 Kev/Laya/Simple-Jev 的 `/v1/systemone`，再用 TypeSafe 兼容客户端调用 |
| 还能用在哪 | Agent 权限与工具选择、模型/effort 路由、审核与安全判定、批量分类打分、语音候选重排、边缘服务编排、移动 GUI、科学/法务判断等 |

**一句话**：Jev 是「快速校准的类型化决策层」，不是聊天编码模型；官方训练黑箱，复刻要走社区开源栈；放进 Codex 走 skill/hook/旁路 API；放进 ModelRouter 走决策组件与路由实验。

---

## 二、核查范围与路由

| 平台 | 子代理 | 状态 | 报告 |
| --- | --- | --- | --- |
| Academic (arXiv/OpenAlex/Crossref) | explore-1 | 完成 | `platforms/academic.md` |
| Google Scholar | explore-3 | 完成 | `platforms/google-scholar.md` |
| GitHub | explore-2 | 完成 | `platforms/github.md` |
| Stack Overflow + Codex/TypeSafe 文档 | explore-4 | 完成 | `platforms/stackoverflow-codex.md` |
| Community（HN/掘金/独立评测/中文社区） | explore-5 | 完成 | `platforms/community.md` |
| Wiki/Web 官方面 | explore-6 | 超时未写报告 | 主代理用 Wikipedia 发现层 + TypeSafe 博客 + awesome-jev 直接补齐 |

**路由状态**：`partial`（wiki 平台代理未落盘；其余五路已完成并合并）。

**执行 Skill / 路径**：
- `fast_search.py`（github / arxiv / openalex / google-scholar / hacker-news / stackoverflow / wikipedia）
- WebFetch：arXiv 摘要/正文、awesome-jev、Visual-Jev、AnyJev、Laya、simple-jev、codex-jev-router、TypeSafe 博客
- leaf skills：`research-router` 主入口；社区侧用公开检索，未登录 52pojie 登录态

---

## 三、Jev 是什么（身份确认）

| 项 | 证据 |
| --- | --- |
| 开发方 | TypeSafe AI（旧金山，约 2024 创立） |
| 发布 | 约 2026-09-15，早期访问 |
| 产品形态 | 托管 API；版本常见 `jev-1.13.0`，别名 `jev-latest` / `jev-preview` |
| 接口 | `POST https://api.typesafe.ai/v1/systemone` |
| 输入 | `state`（文本/JSON）+ `questions` map |
| 输出类型 | **Choice**（选项分布 + argmax + 置信度）、**Noul**（P(yes)）、**Score**（档位分布/期望分） |
| 是否聊天模型 | 官方明确：**不是** chat / 代码补全模型 |
| 定价（公开材料） | 输入约 `$0.042 / 1M tokens`；输出计费标为免费（价格动态，使用前需再核对） |
| 上下文 | 材料中常见约 64k；state + 最长 question 约 32k |
| 模态 | 仅文本/JSON state（无图像/音视频输入） |
| 微调 | TypeSafe 文档：**不按客户数据** fine-tune / LoRA；同一权重服务所有账户 |

命名来源：System One 对应 Kahneman 的快思考；Jev 取 William Stanley Jevons（厂商 FAQ）。创始人 Diogo Almeida，公开访谈中提到此前与 OpenAI instruction-following 工作相关。

Wikipedia 发现层存在 [Jev (AI model)](https://en.wikipedia.org/wiki/Jev_%28AI_model%29) 条目，摘要有 TypeSafe AI / limited release 等信息；正文抓取本轮未稳定取到，细节以厂商文档 + 第三方论文交叉为准。

**辨识噪声**：`JEV` 也指 Japanese Encephalitis Virus（日本脑炎病毒）。学术检索中大量命中病毒文献，本报告已排除。

---

## 四、官方如何「制作并训练」

### 4.1 公开可确认的部分

| 维度 | 公开信息 | 证据 |
| --- | --- | --- |
| 训练方法名 | RLCD = Reinforcement Learning for Calibrated Decisions | TypeSafe 博客；Just Ask Jev (arXiv:2609.29429) 引用 docs.typesafe.ai |
| 目标 | 输出校准概率：分配概率 p 的决策，正确比例接近 p | Just Ask Jev |
| 与 RLHF 的区别 | 公开材料强调面向校准决策，区别于偏好文本 RLHF；并注意与同缩写「contrastive distillation」无关 | Just Ask Jev 脚注 |
| 架构 | 厂商称「新架构 + 并行采样器」；**具体结构、参数量未公开** | TypeSafe 博客；HN 创始人回复称架构先保密 |
| 权重 | 闭源；无 HuggingFace 官方 Jev 权重 | GitHub typesafe-ai org 11 个公开仓库盘点 |
| 训练代码 | 无官方训练仓库 | GitHub 核查 |
| 训练数据 | FAQ 有「训练数据从哪来」标题，公开正文未给出配方 | TypeSafe 博客抓取 + 论文侧一致 |
| 客户微调 | 无 | TypeSafe docs；多篇第三方评测 |

**学术结论**：Scholar 约 20 篇 2026-09 相关文献均为第三方对 API 的评测/应用/批评；**未发现 TypeSafe 署名训练论文**。SSRN 等条目明确写：公开叙述无法拆开训练、架构、数据各自贡献。

### 4.2 独立可复现的「怎么训一个 Jev-like 模型」

#### A. Visual Jev（最强论文级配方）

来源：[arXiv:2609.25845](https://arxiv.org/abs/2609.25845) + [github.com/guanxuyu-sv/Visual-Jev](https://github.com/guanxuyu-sv/Visual-Jev)

| 组件 | 配方 |
| --- | --- |
| Backbone | Qwen3-VL-4B-Instruct（bf16）；对照 8B |
| 视觉塔 | 固定参数 |
| 适配 | 语言塔 LoRA：r=16, α=32, dropout=0.05 |
| 数据 | GQA Choice 30,416 + SNLI-VE Claim 9,000；选项数 2–8，选项顺序打乱 |
| 训练 | Answer SFT：在固定 `Answer:` 读出位置对候选字母 token 做下一 token 交叉熵 |
| 超参 | 3,000 steps；batch 8；AdamW + cosine；warmup 100；LoRA LR 1e-4；grad clip 1.0 |
| 硬件 | 1× RTX 5090 32GB；约 45 分钟/变体；峰值约 14.4 GiB |
| 读出 | LM head 上候选 token logits 的 softmax，只在合法选项上归一 |
| 附加头 | 类型化决策头对照实验：**无稳定准确率优势** |
| 结果 | 宏平均准确率 0.706 → 0.761；增益集中在训练覆盖过的任务类型 |
| 许可 | 代码 Apache-2.0；适配器 Apache-2.0（backbone/数据集各自条款） |

**设计含义**：先改 backbone 提质量；读出复用 LM head；多问题共享前缀 + 批处理后缀提吞吐；不必先上专门 decision head。

#### B. Kev（社区最强可训 Jev-like 栈）

来源：[github.com/jaredpalmer/kev](https://github.com/jaredpalmer/kev)

- 架构：Qwen3.5/3.8 上 rank-16 LoRA + 小 pointer head
- 权重：HF `jaredpalmer/kev-0.8b/4b/9b/27b`，Apache-2.0
- 训练入口：`python -m kev.train --data train.jsonl --base Qwen/...`
- 数据格式：JSONL，`state` + `questions` + 每题 label
- 基础训练集：`decision-v7`（约 10k，多公开数据集 + 生成策略/规则样例）
- 微调成本（作者自报）：Kev-4B 在 H100 上约 `$1` 量级
- 服务：`python -m kev.serve` 暴露 `POST /v1/systemone`
- TypeSafe SDK 指到本地：`TypeSafeClient(api_key="local", base_url="http://127.0.0.1:8009", model="kev-latest")`
- 明确声明：训练未使用 Jev 输出；Kev 是同类，不是 Jev 蒸馏
- 限制：知识题弱于托管 Jev；微调可能伤部分任务；选项顺序仍可能翻转答案

#### C. Laya（同一产品线的开放 System One）

来源：[github.com/NandhaKishorM/laya](https://github.com/NandhaKishorM/laya)

- 非自回归决策引擎；公开权重 `convaiinnovations/laya*`
- 训练叙述：对严格 proper scoring rule 的 RLCD；社区/论文侧可见架构线索为 ModernBERT-large 约 421M
- 微调笔记本：`notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb`（Kaggle 免费 2×T4）
- 声称：typed-decisions 微调后 0.362 → 0.766
- `laya-serve` 实现 `POST /v1/systemone`，客户端可改 baseUrl 对接
- 注意：confidence 公式与托管 Jev 不同，阈值不能直接照搬；独立复现显示系统性偏保守（ECE 约 0.214），温度重拟合有帮助

#### D. Simple Jev + RFDT

来源：[github.com/featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev)

- 任意开源 LM 的 logits 读出 → 类型化决策端点（`/v1/classifier`，别名 `/v1/systemone`）
- RFDT：`prepare.py` → `train.py`（对合法答案 token logits 做交叉熵，LoRA 或全参）→ `export.py`
- 公开 demo API 无鉴权，限流；生产用 Featherless 付费或自托管
- 明确：不复刻 TypeSafe 架构与训练

#### E. AnyJev（几乎不训）

来源：[github.com/nokia-applied-research/AnyJev](https://github.com/nokia-applied-research/AnyJev)

- L0：零标签，选项轮换抵消顺序偏置
- L1：100–500 标签 → 温度标定
- L2：100–300 标签 → 闭式 head 读 hidden state，权重不动
- 用 vLLM embed 服务；作者声明与 TypeSafe 无隶属
- 适合快速原型与校准研究，不等于官方 Jev

#### F. 其他线索

- `this-that-model-1.0`（arXiv:2609.23886）：2B 参数、隐状态读出、约 30ms、开源对照
- `TheoLeeCJ/SemIf-OpenJev`：开放模型上的接口复刻 + 温度标定
- `LocalLLaMA/typed-decisions`：社区决策数据集
- 推理侧复刻 `mini-jev`：参数固定的 LLM 读选项字母 logits，证明接口部分不依赖官方权重

---

## 五、如何在当前项目（ModelRouter）中使用

本仓库定位：长程 Agent 的模型、推理档位与成本研究（见根 `README.md`）。Jev 与该问题的接口面很宽。

| 使用点 | 具体用法 | 证据/判断 |
| --- | --- | --- |
| 事前配置选择器 | 任务启动时用 typed Choice 选「模型 × effort」配置；Noul 问「该配置在质量约束下是否足够」 | 生态研究指出公众注意力集中在 routing 与 interface agents（Jev in the Wild, arXiv:2609.30216） |
| 成本守卫 | 低置信度时升级到强模型或人工；高置信才走便宜档 | REFLEX 等论文用 Jev 作快速决策层，低置信再调用强 LLM（arXiv:2609.26532） |
| 执行中护栏 | tool call / 审批旁路判定（可撤销？是否服务当前任务？） | OpenRouter cookbook 覆盖 Codex hooks；社区 jev-guard 类项目 |
| 数据标注回流 | 用 Jev 打标，再训练本地路由头/分类器 | 社区讨论常见路径；需防标签误差放大 |
| 本地对照实验 | 自托管 Kev/Laya/Simple-Jev，与托管 Jev、纯 LLM 路由器对比 | 许可多为 Apache-2.0 |
| 统一接口 | `system-one-adapter-python` 可用 OpenAI/Anthropic 等模拟 `system_one(state, questions)` | 官方 adapter；便于在无 TypeSafe 账号时先跑通链路 |

**适配判断（分析，非外部事实）**：

- ModelRouter 的核心问题是任务级成本与成功率的配置选择。Jev 类决策层恰好是「快速、可设阈值、可旁路强模型」的组件，适合作为 **router 决策节点** 或 **对照组**，不适合替代编码执行模型。
- 若数据侧已有调用级账本（模型/档位/成本/成功），可把 episode 特征压成 `state`，问题拆成 Choice（选配置）+ Noul（质量是否达标）+ Score（成本风险），在代码里做硬约束与记账。
- 社区已有 `jev-router`、`harness-router`、`miniLV/Jev-Auto-Router` 等路由实验；其中 `suenot/codex-jev-router` 的基准提醒：Jev 选子代理未必比单一高 effort 智能体便宜——**路由收益必须实测，不能从首页倍数外推**。

**落地建议顺序**：

1. 不接托管账号，先用 `system-one-adapter-python` 或 Simple-Jev 在本地跑通 typed question 接口。
2. 用自有调用/episode 数据做只读评估：配置选择准确率、成本 P90、失败转人工比例。
3. 再决定是否引入托管 Jev 或训练 Kev/Laya 专用于路由。
4. 所有阈值在自己的验证集上重标定；不同实现的 confidence 公式不通用。

---

## 六、如何把 Jev 模型放入 Codex 使用

### 6.1 不能做的事

| 错误做法 | 原因 |
| --- | --- |
| 在 `~/.codex/config.toml` 写 `model_provider` 指向 TypeSafe Jev，当 coder | 官方 coding-agents 文档：不存在 `model = "jev-latest"` 这种配置 |
| 把 Jev 的 `/v1/systemone` 填进 `base_url` 并期望 Codex 对话 | Jev 是 typed-decision HTTP；Codex 自定义 provider 当前 `wire_api` 文档写明仅 `"responses"` |
| 按 CSDN 等模板把 Jev 当「编码聊天后端」 | 与官方 System One 定位冲突，属社区误解/SEO 噪声 |

### 6.2 可落地路径

#### 路径 A：官方 skill + 应用侧调用（推荐首选）

```bash
# Claude Code 示例
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai

# 含 Codex 等其他 agent
npx skills add typesafe-ai/skills --skill typesafe-ai
export TYPESAFE_API_KEY=...
```

- skill 让 Codex 学会写 TypeSafe 调用代码，并在 agent 工作流里插入 decision 问题。
- skill **不**替换 Codex 的 coder 模型。

#### 路径 B：Codex hooks 旁路决策（permission / tool 层）

参考 OpenRouter cookbook（覆盖 Codex CLI）与官方 hooks 文档：

1. 高风险命令静态名单（递归删除、force push、硬重置、凭据路径等）**不**调 Jev，直接人工确认。
2. 其余审批用 Jev Noul：命令是否可撤销、是否服务当前任务。
3. 所有概率 ≥ 阈值（示例 `0.9`）才 allow；否则保持原审批流。
4. Codex hook 事件：`PermissionRequest` / `PreToolUse`；返回 JSON `decision.behavior: allow|deny`。

示例（官方文档形态）：

```toml
[[hooks.PermissionRequest]]
matcher = "^Bash$"

[[hooks.PermissionRequest.hooks]]
type = "command"
command = "bun /absolute/path/jev-permission-hook.ts"
timeout = 30
statusMessage = "Asking Jev about reversibility"
```

实现时注意：Codex 审批问题文案常不适合直接当任务文本；OpenRouter 作者记录用 `turn_id` 识别，且误用审批文本时置信度会偏低。

#### 路径 C：自托管 Jev-like + TypeSafe 兼容 API

| 栈 | 服务命令 | 用途 |
| --- | --- | --- |
| Kev | `python -m kev.serve --run jaredpalmer/kev-4b --port 8009` | 可训练、有权重 |
| Laya | `laya-serve` | 开放权重 + 微调笔记本 |
| Simple Jev | `python hf-server/hf_server.py --model ...` | 任意开源 LM 决策层 |

客户端仍可按 TypeSafe `system_one` 形状调用；Codex 继续用正常 coder，由应用/hook/MCP 去打决策端点。

#### 路径 D：真·自定义 coder（与 Jev 是两条线）

若目标是换掉 Codex 背后的模型：

```toml
[model_providers.my_local]
name = "local"
base_url = "http://127.0.0.1:8000/v1"
wire_api = "responses"
```

需要上游能讲 Responses API。这与 Jev 决策 API 无关；不要混用配置。

#### 路径 E：OpenRouter 中转

- Decisions API：`POST https://openrouter.ai/api/alpha/decisions`
- System One API：`POST https://openrouter.ai/api/v1/systemone`
- 模型 ID 示例：`typesafe/jev-1.13` / `typesafe/jev-router`

注意：OpenRouter 整站有 chat surface，但 Jev 的正式决策面仍是 Decisions/System One；不要把 questions 硬塞进 chat-completions。

### 6.3 实测参考

掘金社区实测（2026-09-23，作者沉默王二）：安装官方 skill 后，任务提示由 Jev Choice 决定下一步动作，`confidence ≥ 0.8` 才执行；响应可见 `model: jev-1.13.0`，usage 例 input 495 / output 63，choice=`web_search`，confidence=0.99。

社区同时观察到：CSDN 大量「Jev 接入 Codex」模板文把产品定位说错，不宜照抄。

---

## 七、JEV / Jev 还能用在哪些地方

### 7.1 论文与生态层

| 场景 | 代表证据 | 作用 |
| --- | --- | --- |
| 模型/工具/effort 路由 | Jev in the Wild；开源 jev-router 系 | 事前选配置或工具 |
| Agent 权限与安全 | Decision Hijacking；penetst harness；JEV as Judge | 注入防护、审批、trace 风险分类 |
| 审核与 rubric | Rubric Judges；ABSA typed decisions | 便宜第一阶段 judge；与 LLM 级联 |
| 边缘服务编排 | arXiv:2609.22753 | 低延迟意图/契约准入 |
| 语音神经假肢候选重排 | arXiv:2609.33538 | 用 typed 概率替换 7B LM 重排 |
| 移动 GUI agent | Jev-Mobile | 高频执行层，低频仍用 VLM 规划 |
| 视觉多问题决策 | Visual Jev | 共享图像前缀 + 批量 typed 问题 |
| 法务/科学/事故文本 | ContractNLI；scientific decisions；crash narratives | 把长文本压成 typed 判断 |

### 7.2 社区实践层（作者自述，未在本轮全部复测）

- 浏览器自动化、PR 审查、内容安全流水线
- 批量论文/评论分类、SEO 批处理
- Home Assistant 一类智能家居自动化
- 游戏状态动作选择（Othello/Mario 等 demo；边界是选择合法 ≠ 选择最优）
- 非编码判断：简历/资料打分等

### 7.3 风险与批评（必须读）

| 批评 | 说明 |
| --- | --- |
| 营销倍数 | 首页/launch 叙述的加速与省钱倍数很高；用户自述中位与独立测试明显更低（约 7×/30× 量级 vs 独立约 5×/8.6× 对照） |
| 「零幻觉」 | 类型安全保证输出形状，不保证事实正确；高置信仍可错 |
| 校准 | 第三方研究：阈值上 ECE 不理想；选项名/极性绑定可大幅拉低 AUC；概率在分解/重组时可能不协调 |
| 注入与自然上下文 | schema 输出降低自由发挥，但仍可被注入或自然语境翻转决策 |
| 准入 | waitlist 与 API 限制在发布初期被大量讨论 |
| 路由收益不确定 | 有基准显示 Jev 路由子代理成本高于单一高 effort agent |
| 信息污染 | 中文内容农场大量错误教程（把 Jev 当聊天编码后端） |

**采信顺序建议**：可复述的独立实验 > 汇总统计（注明方法限制）> awesome/教程索引 > 内容农场。

---

## 八、证据表（关键论断 → 来源）

| 论断 | 来源 | 级别 |
| --- | --- | --- |
| Jev 是 TypeSafe System One，typed decisions | 厂商博客 + 多篇 arXiv + docs | 高（多源） |
| 官方训练名为 RLCD，细节不公开 | TypeSafe 博客；Just Ask Jev；Scholar 全景 | 高（一致） |
| 官方无公开训练代码/权重 | typesafe-ai org 仓库盘点 | 高 |
| Visual Jev 可复现训练配方 | arXiv:2609.25845 + Visual-Jev README/REPRODUCE | 高（含代码/适配器） |
| Kev 可训且暴露 `/v1/systemone` | jaredpalmer/kev README | 高（代码） |
| Laya 开放权重 + 微调路径 | NandhaKishorM/laya + arXiv:2609.33843 | 高 |
| 官方 Jev 不可客户微调 | TypeSafe docs（经多平台引用） | 高 |
| Codex 不能把 Jev 当 model_provider | TypeSafe coding-agents 文档 | 高 |
| Codex hooks + Jev 可做 permission 旁路 | OpenRouter cookbook + OpenAI Codex hooks 文档 | 高（文档） |
| 生态路由是热点 | arXiv:2609.30216 | 中高（第三方分析） |
| 校准/顺序偏置/注入是实风险 | Type-Safe Is Not Error-Free；Decision Hijacking；校准审计等 | 中高（第三方） |
| ModelRouter 可作决策节点使用 | 本报告对照分析 | 判断 |

---

## 九、最终回答结构（对应你的问题）

1. **制作与训练**：官方公开层只有 RLCD 名称与 API 行为；权重与训练配方闭源。  
2. **如何自训**：走 Visual Jev / Kev / Laya / RFDT / AnyJev；预算参考 Visual Jev（单卡约 1 小时级，约 3.9 万决策样本）。  
3. **ModelRouter 能否用**：能。用作配置选择器、守卫、对照实验节点；不要指望它替代编码模型。  
4. **Codex 如何用**：skill + hooks + 兼容 API；不要改 `model_provider` 塞 Jev。  
5. **其他用途**：路由、审核、边缘编排、批量分类、语音重排、GUI 执行层等。  
6. **平台与子代理**：六路并行（学术/Scholar/GitHub/StackOverflow+文档/社区/Web）；本报告由主代理合并。  

---

## 十、平台报告索引

| 文件 | 内容 |
| --- | --- |
| `platforms/academic.md` | arXiv 论文清单、训练证据、应用、缺口 |
| `platforms/google-scholar.md` | Scholar 文献全景、LLM 对比、安全批评 |
| `platforms/github.md` | 官方 org、Kev/Laya/AnyJev/simple-jev、Codex 仓库 |
| `platforms/stackoverflow-codex.md` | Codex provider 约束、hooks 方案、OpenRouter |
| `platforms/community.md` | HN/掘金/独立评测/中文社区与批评 |
| 本文件 | 合并结论、ModelRouter/Codex 落地、证据表 |

---

## 十一、未确认事项与风险

- 官方 Jev 的 RLCD 细节、训练数据、backbone 公开材料缺失。
- wiki-web 平台代理本轮未写出独立报告；相关结论来自主代理直接抓取。
- 中国论坛正文（linux.do/zhihu）仅有标题线索，v2ex/52pojie 本轮无实质命中。
- 社区 README 性能数字多为作者自报，本轮未独立复现。
- TypeSafe 价格、waitlist、模型条款在文档/控制台侧，可能随时变化，使用前需再核对。
- 许可：托管 Jev 条款 ≠ 开源模型条款；训练用第三方数据需单独看数据集许可。

---

*报告结束。*
