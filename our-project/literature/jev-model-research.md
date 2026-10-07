# JEV 模型深度调研：制作训练、自训路径、ModelRouter 适配与 Codex 接入

- 检索方式：research-router `deep`（一平台一代理，并行 5 路）
- 平台：Academic（arXiv/OpenAlex/Crossref）、Google Scholar、GitHub、Stack Overflow、中文社区（linux.do / V2EX / 52pojie 公开检索）
- 查询变体：约 40 组（含失败与限流查询）
- 文档性质：本项目内**唯一**调研产出

---

## 1. 结论先行

1. **「JEV 模型」没有单一学术定义。** 检索到两条几乎不重叠的线，按你的使用语境（路由 + Codex）优先取线 A。
2. **线 A（主）：TypeSafe Jev（System One）** — 2026 年前后的**决策模型**，输入状态与结构化问题，输出 Choice / Score / 概率与置信度；非自回归文本生成器。官方**闭源托管**，无公开权重、无官方训练代码。Codex 生态里已有专门路由项目。
3. **线 B（次）：Meta JEPA / V-JEPA** — Joint-Embedding Predictive Architecture，自监督视觉/视频表征学习。若你原意是这个，训练代码完全开源（`facebookresearch/jepa`，CC BY-NC 4.0）。
4. **「我如何训练这样一个模型」：** 官方 Jev **无法**按官方配方训练（资料未公开）。可复现的是开源对齐物 **Laya**（421M，Apache-2.0）及配套微调仓库；若指 JEPA，则走 I-JEPA/V-JEPA 官方训练入口。
5. **能否用于当前 ModelRouter 项目：** 可以，定位是**任务启动时的配置选择器**（在 `(model, effort)` 空间上做 Choice/Score），不作为执行用 LLM。与项目已有「执行前一次选择 + 质量约束 + 费用最小」主线兼容；需自备协议适配与成功率校准。
6. **如何放入 Codex：** 官方明确**没有** `model: "jev-latest"` 去替换 coding model。路径是：TypeSafe agent skill，或社区项目 `0xNatoshi/jev-codex-router` 做每轮 model+effort 路由。Codex CLI 只认 **OpenAI Responses** 协议，`~/.codex/config.toml` 配置；ChatGPT 账号模式下自定义模型名会 400。
7. **其他用途：** 自动化流程低延迟决策、多模型仲裁式选择、结构化打分/阈值策略、与 LLM 组成「LLM 整理选项 → Jev 选择 → LLM 解读」三段式；线 B 的 JEPA 另用于视觉/视频/世界模型/RL 表征。

---

## 2. 身份辨析（Q0）

| 线 | 正式名称 | 类型 | 开源? | 与你问题的贴合度 |
| --- | --- | --- | --- | --- |
| A | TypeSafe **Jev**（System One） | 结构化决策/判断模型 | 权重与训练闭源；周边 SDK/Skill 开源 | **高**（Codex、路由、中文社区热点） |
| B | Meta **I-JEPA / V-JEPA / V-JEPA 2** | 自监督表征（图像/视频） | 训练代码开源，许可证 CC BY-NC 4.0 | 中（若你原意是 JEPA/自监督训练） |
| — | 学术库里名为「JEV」的神经架构 | — | — | **未命中**（Crossref 仅命中日本脑炎病毒等同名） |

社区侧独立佐证：linux.do 2026-09 帖子把 Jev 描述为「放弃传统自回归、只能做决策」的模型，与 TypeSafe 文档一致；同社区把 V-JEPA 2 当作另一话题讨论，**未见二者技术关联**。

---

## 3. 线 A：Jev 是如何制作并训练的（Q1–Q3）

### 3.1 官方公开信息（可确认）

| 项 | 内容 | 来源类型 |
| --- | --- | --- |
| 形态 | 托管 API / System One；输入 state + 类型化问题（Choice / Score / Noul），输出结构化答案 + confidence | docs.typesafe.ai |
| 架构细节 | **未公开**（无参数量、无训练数据、无框架、无超参） | 官方无 training 章节 |
| 权重 | 无公开权重 | GitHub typesafe-ai org 无训练仓库 |
| 官方接入姿态 | 文档写明不存在 `jev-latest` 这类「替掉 coding LLM」的 model 配置 | 官方文档 |
| 周边开源 | `typesafe-ai/skills`（MIT，2.3k+★）、`typesafe-sdk-python`/`-js`、`system-one-adapter-python` | GitHub |

### 3.2 社区/旁证中的「制作理解」（需降级对待）

- 知乎教程主张 Jev 本质接近「大号通用 BERT」，只做判断/选择/打分三类输出，并给出自训步骤——**平台外旁证，未在官方或复现仓库中验证**。
- SemIf-OpenJev README 明确写：**不复现 Jev 未公开的模型与训练**，只独立实现其接口/评分使用方式。
- 结论：**官方 Jev 的制作与训练配方 = 未公开**；任何「教程教你训出 Jev」只能训出风格类似的选择器，不能宣称是同一模型。

### 3.3 开源可复现的「同类训练」路径

| 路径 | 仓库 / 权重 | 许可 | 训练入口 | 预期 |
| --- | --- | --- | --- | --- |
| Laya 全流程 | `omkarghugarkar007/system-one-model-finetuning` | Apache-2.0 | `make install` → `make weights`（约 1.7GB，421M）→ `make quickstart` | 笔记本可跑，仓库称 84 tests |
| Laya 微调流水线 | `devjothish/laya-forge` | Apache-2.0 | `forge.yaml`：微调 → 温度校准 → 阈值策略 → 导出 checkpoint | 面向对齐 Jev 线协议的 open weights |
| Laya 权重 | HuggingFace `convaiinnovations/laya` | Apache-2.0 | — | 421M |
| 接口模式独立实现 | `TheoLeeCJ/SemIf-OpenJev`（原 OpenJev） | MIT | 推理评分，无训练 | 演示如何在不复制未公开模型的前提下使用同类接口 |
| 另一开源 System One 叙述 | `wfzyx/von` | Apache-2.0 | 未核实训练细节 | 自述 sub-15ms 决策 |

**自训结论：** 想「训出你自己的这类模型」→ 走 Laya / laya-forge（决策器）或 JEPA 官方栈（表征模型）；**不要**指望拿到 TypeSafe 官方训练脚本。

---

## 4. 线 B：若你指的是 JEPA / V-JEPA（Q1–Q6 备份）

| 项 | I-JEPA (2023) | V-JEPA (2024) | V-JEPA 2 (2025) |
| --- | --- | --- | --- |
| 论文 | arXiv:2301.08243 | arXiv:2404.08471 | arXiv:2506.09985 |
| 核心思想 | 掩码后在潜空间预测目标块表征 | 纯特征预测，无重建/文本/负样本 | >100 万小时无标注视频预训练 + LLM 对齐 |
| 公开训练规模线索 | ImageNet + ViT-H/14，**16×A100，<72 小时** | 200 万公开视频 | >1M 小时；后续 V-JEPA 2-AC 用 <62h Droid 数据后训练 |
| 代码 | `facebookresearch/jepa`（原 v-jepa 归档于此） | 同左 | 同左 |
| 许可 | **CC BY-NC 4.0（禁止商用）** | 同左 | 同左 |
| 训练入口 | `app/main.py`、`app/main_distributed.py`，`configs/`、`src/`、`evals/` | 同左 | 同左 |
| 详细超参 | 摘要级已确认算力与数据；**lr/batch/epoch 级仍需读附录全文** | 同左 | 同左 |

学术侧延伸用途（摘要级）：VL-JEPA（视觉语言）、LLM-JEPA（LLM 目标）、JEPA for RL、音频 A-JEPA/Audio-JEPA、图表征、临床轨迹、世界模型 LeWorldModel 等。

---

## 5. ModelRouter 项目能否使用（Q8）

当前项目主线（见 `our-project/planning/IMPLEMENTATION_RESEARCH.md`）：

```text
任务输入 → admission 特征 → 对每个 (model, effort) 预测成功率与费用
        → 质量约束筛选 → 选预计费用最低配置 → 固定 harness 执行记账
```

| 适配点 | 怎么用 Jev / Laya | 需要自备什么 | 风险 |
| --- | --- | --- | --- |
| 选择步 | 把候选 `(model, effort, cache 状态)` 编成 Choice/Score 问题，交给 Jev 决策器出分 | 状态编码器、类型化 schema、与 `RouterDecision` 形状对齐 | 决策器置信度 ≠ 你的成功率校准，需在自有 episode 数据上做温度/阈值 |
| 每轮/任务级路由 | 对标 `jev-codex-router` 的 routing policy，挂到统一适配器前 | 策略接口、回放评测（项目已有 859k 调用级数据可做离线回测） | README 自述 −60% quota 为历史模拟，**不能**当实测 |
| 执行层 | **不合适**当生成模型 | — | Jev 不产出普通 token，无法替代 GPT/Claude 执行 |
| 作为对照基线 | 与「盲选最便宜/最强、在线 bandit、事前预测器」并列 | 训练特征与标签口径对齐 | 许可与 API 条款需在商用前单核 |

**判断：** 项目内**可以**把 Jev/Laya 放在「配置选择」位置做实验与对照；**不应该**指望它替代轨迹执行模型。线 B 的 JEPA 与本项目任务级成本路由**无直接接口**，只在你要自研视觉/视频特征时才相关。

---

## 6. 如何把 Jev 放入 Codex（Q7）

### 6.1 官方与社区路径

| 方式 | 代表 | 说明 |
| --- | --- | --- |
| Agent Skill（官方生态） | `github.com/typesafe-ai/skills`（MIT） | 在 agent 流程里调用 TypeSafe System One 做类型化决策；**不是**替换 Codex 主模型 |
| 每轮路由（社区主力） | `github.com/0xNatoshi/jev-codex-router`（MIT，277★） | 内嵌 router、`routing_policy.py`、本地 `jev_server.py`（127.0.0.1:4319）；issues 里有 replay、quota、attestation 等集成修复 |
| 直接设 model 名 | — | 官方：**不存在** `jev-latest` 这种替代 coding model 的配置 |

### 6.2 Codex 接入的硬约束（社区多源一致）

1. Codex CLI 接受的是 **OpenAI Responses 协议**，不是简单 `chat/completions`；中转站若只模拟 chat，常见 404。
2. 配置落点：`~/.codex/config.toml`（模型、provider/base URL）。
3. **ChatGPT 账号登录**时手填自定义模型名可能直接 400（`model not supported when using Codex with a ChatGPT account`）。
4. 本地/中转常见形态：CC Switch、NewAPI/sub2api 等把兼容端点接进 Codex——适用于「能说 Responses 的生成模型」，**Jev 决策 API 不属于此类**，所以只能走 Skill/Router 插件，而不是 `config.toml` 换模型。
5. Stack Overflow 上**没有** `model_providers`/自定义 base_url 的直接问答；该问题应以 OpenAI/Codex 官方文档 + GitHub issues + V2EX/linux.do 实践为准。

### 6.3 实操建议（按你已有东西排）

1. **只想让 Codex 流程里出现 Jev 决策：** 装 `typesafe-ai/skills` 或跑 `jev-codex-router`，保持 Codex 主模型不变。
2. **想完全本地化同类决策：** Laya 起 OpenAI 兼容服务仍解决不了「Codex 要 Responses + 生成式 coding model」的问题；Laya 只能当路由侧旁路服务，不能当 `model = ...`。
3. **想训完再接 Codex：** 先 laya-forge 导出 checkpoint，再按第 6.2 条把**生成模型**留给 Responses 端点，决策器旁挂。

---

## 7. Jev / JEPA 还能用在哪些地方（Q9）

**线 A（决策器）— 来自公开社区与文档的用法：**

- 自动化流水线：社区实测把决策压到约 300ms 量级，用于减少整段编排等待（帖称 10s 级 → 1s 级；**单帖自述，未独立复测**）。
- 「答案之书」三段式：LLM 整理问题与选项 → Jev 选择 → LLM 解读。
- 多模型共同决策 / 每轮 model+effort 路由（与你 ModelRouter 同类问题）。
- 类型化 agent 决策：Choice/Score/Noul + confidence，适合接入需要强 schema 的工具链。
- 争议用法讨论：智能驾驶决策（社区提问阶段）；是否强于文本推理 SOTA（存在明确质疑与 API 实测翻车帖）。

**线 B（JEPA）：** 自监督视觉/视频表征、动作预测与世界模型、机器人操作（V-JEPA 2-AC）、视觉语言、RL、音频与图结构——与「文本 Agent 路由」不同赛道。

---

## 8. 风险与限制（Q10）

| 风险 | 说明 |
| --- | --- |
| 身份歧义 | 你若本意是 JEPA，本文主线 A 的结论不适用；反亦然 |
| 闭源 | 官方 Jev 训练细节、权重、价格与留存条款均未在本轮取证中公开 |
| 许可 | `facebookresearch/jepa` 为 CC BY-NC；Laya 系为 Apache-2.0；typesafe 周边多为 MIT——分件核对 |
| 性能数字 | −60% quota、300ms、10s→1s 均来自 README/帖文自述，缺统一实测 |
| 协议 | Codex 只吃 Responses；决策模型不能靠改 `config.toml` 的 model 名接入 |
| 同名干扰 | 「JEV」在学术检索中大量落到日本脑炎病毒（Japanese encephalitis virus） |
| 生态噪音 | awesome-* 列表批量 PR「Add Codex Jev Router」，列表自声明不代表背书 |

---

## 9. 证据表（主来源）

| # | 论断 | 来源 | 级别 |
| --- | --- | --- | --- |
| 1 | 无名为 JEV 的通行 ML 架构；学术命中为 JEPA 家族与同名无关项 | arXiv/OpenAlex/Crossref/Scholar 多轮查询 | 发现+摘要 |
| 2 | I-JEPA 训练算力 ImageNet ViT-H 16×A100&lt;72h | https://arxiv.org/abs/2301.08243 | 摘要 |
| 3 | V-JEPA 200 万视频与三项 benchmark | https://arxiv.org/abs/2404.08471 | 摘要 |
| 4 | V-JEPA 2 &gt;1M 小时视频与后续机器人后训练 | https://arxiv.org/abs/2506.09985 | 摘要 |
| 5 | JEPA 综述教程存在 | OpenReview `Zr4PUe0ZNl`（Monemi et al. 2025） | 索引 |
| 6 | Jev = TypeSafe System One，闭源托管，无 `jev-latest` 替换 | https://docs.typesafe.ai + typesafe-ai org | 官方文档/仓库 |
| 7 | Codex 每轮 Jev 路由存在及集成问题 | https://github.com/0xNatoshi/jev-codex-router | 仓库 README/issues |
| 8 | JEPA 官方代码与 NC 许可、训练入口 | https://github.com/facebookresearch/jepa | 仓库 |
| 9 | Laya 可训路径 | system-one-model-finetuning / laya-forge / HF convaiinnovations/laya | 仓库/HF |
| 10 | 社区对 Jev 定位与用法、质疑 | linux.do topics 2917108 / 2924658 / 2921660 / 2929612 / 2935817 等 | 公开摘要 |
| 11 | Codex 仅 Responses 协议、config.toml、账号模式 400 | V2EX 1213127 / 1233012、linux.do 2944349 等 | 公开摘要 |
| 12 | SO 对 Codex 自定义 provider 无直接覆盖 | 12 组 stackoverflow 查询 | 负面结果 |

---

## 10. 路由记录与未确认项

| 字段 | 值 |
| --- | --- |
| 场景 | academic + open-source + community |
| 深度 | deep |
| 并行代理 | 5（Academic / Scholar / GitHub / StackOverflow / 社区） |
| 路由状态 | **partial**（官方 Jev 训练全文与线程回帖未取得；GitHub provider 限流；linux.do/V2EX 正文反爬） |
| 未确认 | ① 你口中的 JEV 具体是线 A 还是线 B；② Jev 官方超参/数据/架构；③ 各自述数字的独立复现；④ JEPA 附录级训练超参 |
| 停止原因 | 各平台达到命中阈值或变体穷尽；正文抓取失败不绕过登录 |

**下一步（可选）：** 你确认 JEV 指线 A 还是线 B 后，可以只加深对应一支（例如读 JEPA 论文附录超参，或逐条读 jev-codex-router 的 issues 与 policy 源码）。
