# ModelRouter

> **2026-10-18 项目目录升级（实施中）**：将 [`our-project/`](our-project/README.md) 作为正式代码、数据、实验和科研文档的主目录。当前 `router_data/`、`experiments/`、`research/`、`docs/` 等旧位置仍有活跃消费者，**尚未物理迁移**。详见 [完整文件分类与安全迁移实施清单](our-project/planning/REPOSITORY_STRUCTURE_MIGRATION_20261018.md)。最新 RQ1 已调整为整体任务收益对照，系统消融题编号暂未定，以 [EXPERIMENT_QA](our-project/planning/EXPERIMENT_QA.md) 为准。

ModelRouter 是面向长程 Agent 任务的模型、推理档位与成本研究项目。

仓库分为两部分：

- `our-project/`：本项目的研究报告、文献笔记、清洗数据、汇总数据和规划文档。
- `external-projects/`：外部项目的来源登记，仅用于说明文献和实验参考，不包含外部仓库源码。

**训练数据/Provider 政策唯一详细台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md)：公开轨迹、静态模型比较、KV Cache、长记忆、多 Agent、时间/预算、国内外 Provider 能力与缓存/定价政策，包含来源状态、选择栏及未来数据清洗质量合同。**具体选择批准仍以 EXPERIMENT_QA.md 为准；台账是来源登记，不代表已下载或获准训练。**

原始服务器日志、凭据、浏览器调试文件和外部仓库源码不纳入本仓库。

## 外部文本模型配置

当前私人配置保留原DeepSeek，并接入负责人重新提供的Luna、Terra和HY4三个渠道。Luna/Terra使用Responses，HY4使用Chat Completions；ModelRouter按Router选中的精确模型及原生档位请求，渠道默认档位不覆盖路由动作，不改变旧Serving权重。发布输出额度是上限，实验的明确输出预算不会被自动升高。

Luna/Terra按官方105万上下文、12.8万输出配置，保留最大输出时输入额度为92.2万；HY4按腾讯TokenHub的1024k上下文、960k输入、64k输出配置。Luna/Terra可选 `none/low/medium/high/xhigh/max`，普通客户端的Max默认值与Router的本次选择分开。HY4沿负责人要求不传思考强度，动作中的 `native_effort=none` 表示服务默认，不表示关闭思考。三者登记文本/图像输入、文本输出；发布容量、文档档位和供应商实际应用情况分开记录。

后续动态实验统一使用Model×Native Effort，不再运行只选模型的Checkpoint或在线B17分支。原 `v9_real_comparison.json` 默认展开三个新模型的13个组合，输出 `selected_action.model/native_effort/action_id` 及组合概率；调用和返回档位分别记录，未知保持未知。旧40条Model-only偏好、STEP009/010、历史配置与结果保留原语义，不改成联合监督。接口支持组合选择不代表权重已经学会选择档位，正式效果仍需真实独立实验。

ModelRouter与Code Generation统一读取本机 `~/.agent-global/外部文本模型.local.json`。URL、Key、供应商池及模型账户绑定仅在此文件维护；`EXTERNAL_TEXT_MODEL_CONFIG`只指定文件位置。账户统一列在 `providers`，各组默认账户在 `defaults`，ModelRouter模型账户绑定在 `account_endpoints`，并发及输出等运行参数在 `provider_settings`。

旧项目凭据JSON、env和示例已删除。实验JSON只保留模型、协议、预算、费率及Router地址。统一文件为私人文件，不提交Git；后续接入也使用同一来源，现有进程在下一次正常启动时加载，不为迁移重启健康任务。此范围不包含图像、视频或客户端登录凭据。

实验直接请求选中的精确模型ID，生成和教师调用均不再替换为Qwen或默认Luna。同模型账户切换保留，不改变模型；旧映射配置和实现已删除，历史轨迹与费用仍按原事实保存。原 `alias-smoke` 命令已改为 `development`，使用现有真实模型配置，不作为官方完整成绩。

## 当前研究与跨对话恢复入口

**每次新开 ChatGPT 对话先读取 GitHub `main` 当前 HEAD 的以下四份正式文档**，不依赖旧会话摘要或写死的 SHA：

1. **[PROJECT_STATUS.md · 唯一实时状态源](our-project/planning/PROJECT_STATUS.md)**：当前阶段、任务、授权、阻塞及唯一下一行动。
2. **[EXPERIMENT_QA.md · 问答批准记录](our-project/planning/EXPERIMENT_QA.md)**：实验 Q-ID、用户明确确认的决策、未答事项及影响。
3. **[PLANNING_MEMORY.md · 长期交接与新会话启动提示词](our-project/planning/PLANNING_MEMORY.md)**：长期研究决定、历史、Agent 协作规范；第 10 节包含**长期通用的新窗口启动提示词**。
4. **[RESEARCH_OVERVIEW.md · 研究方法与证据](our-project/planning/RESEARCH_OVERVIEW.md)**：学术问题、Kev 路线、假设、数据与评测方法。

**恢复顺序**：本地 `main` HEAD → Status → Q&A → Memory → Research。当前任务以最新版 Status 为准；推荐和历史章节分开记录，避免把旧资料当成当前进度。

旧 `our-project/planning/IMPLEMENTATION_RESEARCH.md` 与 `our-project/literature/report.md` 仅是历史参考，不代表现在唯一实现方案。坚持一个研究主线，不因开启新聊天而新建重复工程链。

**协作**：ChatGPT = Planning Agent，本地 Agent = Execution Agent。默认直接 `main`，本地频繁 commit；任务或决定发生真实变化时按职责更新相关文档。公开仓库不得提交私人地址、密钥或原始私人日志。

## 论文实验方案专题与汇报资料

现有**数据来源台账 + 上述四份正式规划文档**保持原有职责与新对话必读顺序。下面的资料排在这些入口之后，主要用于论文实验设计和组会展示，**不是新的实验状态源**：

- **[汇报三 · 论文实验方案专题](汇报/汇报三/README.md)**：V5 五个 RQ：模型池与公开前沿迁移、真实路由前沿、Model×Effort、缓存历史、决策时机与状态；[详细论文设计（8 图、12 张结果空白表）](汇报/汇报三/ModelRouter论文实验与图表规划.md)；[纯 HTML 交互式原型](汇报/汇报三/交互式原型/index.html)。
- **[全部汇报目录](汇报/README.md)**：汇报一、汇报二、汇报三的主题与入口。

**提醒**：实验方案内的结果数值单元格有意留空，不以预测值或空白的“0”代替未运行的实验。
