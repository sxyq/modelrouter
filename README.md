# ModelRouter

ModelRouter 研究长程 **单 Agent** 执行中的模型与 Provider 原生推理档位联合路由，并以真实任务成功率和完整执行成本评价阶段、实际子任务边界及生成决策粒度。当前方法与结果入口见 [研究总纲](our-project/planning/RESEARCH_OVERVIEW.md)、[项目现状](our-project/planning/PROJECT_STATUS.md) 和 [实验决策记录](our-project/planning/EXPERIMENT_QA.md)。旧目录迁移和双子代理计划仅为历史资料。

ModelRouter 是面向长程 Agent 任务的模型、推理档位与成本研究项目。

仓库分为两部分：

- `our-project/`：本项目的研究报告、文献笔记、清洗数据、汇总数据和规划文档。
- `external-projects/`：外部项目的来源登记，仅用于说明文献和实验参考，不包含外部仓库源码。

**数据来源与 Provider 政策台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md)：公开轨迹、模型比较、缓存、时间/预算与 Provider 来源状态。台账是来源登记，不代表已有原生档位实测分数或新实验结果。

原始服务器日志、凭据、浏览器调试文件和外部仓库源码不纳入本仓库。

## 外部文本模型配置

当前联合候选为 GPT-6 Luna、GLM-5.3-Flash 与 GPT-6.1 Terra。精确 `model_id`、Provider、协议、原生 Effort 菜单和当前可用条件按 Registry 与实际 Provider 能力记录，不假设不同模型支持相同档位，也不将旧 HY4 结果改写为 GLM 结果。

GLM 已沿唯一私人配置绑定 Colink，精确请求与返回为 `glm-5.3-flash`。Low/High 已有真实工具输出；返回 Effort 未报告，High 长请求曾耗尽输出额度，本轮部分请求返回 429。11-07 历史结果保持原身份，新完整 Episode 按原 Harbor 终局记录。

候选动作是实际支持的 `(model, native_effort)` 组合；请求与返回身份、档位分别记录，未知保持未知。15 个联合候选是本轮规划目标，实际每批动作集合按 Provider 支持、工具与上下文条件生成；不支持或未证实的组合不补齐成可运行候选。

AA 能力证据按精确模型和原生档位保存实际测量、版本、来源和时间；没有同档测量的字段保持 `NOT_MEASURED`，不复制模型级分数。TTL、强制刷新、STALE及同批固定 `snapshot_id` 已实现，路由决策不逐次联网。v7共有130项真实指标，Luna/Terra各六档、GLM仅Max；GLM Low/High、授权API完整数据、模型revision和官方发布时间仍缺。

ModelRouter与Code Generation统一读取本机 `~/.agent-global/外部文本模型.local.json`。URL、Key、供应商池及模型账户绑定仅在此文件维护；`EXTERNAL_TEXT_MODEL_CONFIG`只指定文件位置。账户统一列在 `providers`，各组默认账户在 `defaults`，ModelRouter模型账户绑定在 `account_endpoints`，并发及输出等运行参数在 `provider_settings`。

旧项目凭据JSON、env和示例已删除。实验JSON只保留模型、协议、预算、费率及Router地址。统一文件为私人文件，不提交Git；后续接入也使用同一来源，现有进程在下一次正常启动时加载，不为迁移重启健康任务。此范围不包含图像、视频或客户端登录凭据。

实验直接请求选中的精确模型 ID，生成和教师调用均不替换为其他模型。同模型账户切换不改变模型身份；旧映射调用仅保留历史数据。正式 Agent Benchmark 只使用 Harbor `DefaultAgent` 与原 Evaluator；本地 development 命令、`sandbox/canary_verifier.py` 和 `experiments/harbor` 同名 shim 已删除。旧 Mock `pwd`/`fix-git` 分数仅作历史记录，不是可运行或推荐的 smoke 入口。

## 当前研究与跨对话恢复入口

**当前研究入口**（以共享工作树中的现行文件为准）：

1. **[PROJECT_STATUS.md · 唯一实时状态源](our-project/planning/PROJECT_STATUS.md)**：当前阶段、任务、授权、阻塞及唯一下一行动。
2. **[EXPERIMENT_QA.md · 问答批准记录](our-project/planning/EXPERIMENT_QA.md)**：实验 Q-ID、用户明确确认的决策、未答事项及影响。
3. **[RESEARCH_OVERVIEW.md · 研究方法与证据](our-project/planning/RESEARCH_OVERVIEW.md)**：五个 RQ、单 Agent 方法、评测和证据范围。
4. **[汇报三 · 论文实验与图表规划](汇报/汇报三/ModelRouter论文实验与图表规划.md)**：Fig.1–8、Table 1–12 及各结果位置。

**状态顺序**：项目现状 → 决策记录 → 研究总纲 → 论文图表规划。历史协作草案不覆盖当前方法。

旧 `our-project/planning/IMPLEMENTATION_RESEARCH.md` 与 `our-project/literature/report.md` 仅是历史参考，不代表现在唯一实现方案。坚持一个研究主线，不因开启新聊天而新建重复工程链。

2026-10-19 双子代理长周期文档保留为历史计划，不是当前协作或研究方法。

## 论文实验方案专题与汇报资料

现有**数据来源台账 + 上述四份正式规划文档**保持原有职责与新对话必读顺序。下面的资料排在这些入口之后，主要用于论文实验设计和组会展示，**不是新的实验状态源**：

- **[汇报三 · 论文实验方案专题](汇报/汇报三/README.md)**：V9 五个 RQ、8 图和 12 表；RQ3 研究单 Agent 阶段、真实子任务边界与生成决策粒度，阶段识别不等于任务拆分。
- **[全部汇报目录](汇报/README.md)**：汇报一、汇报二、汇报三的主题与入口。

**提醒**：实验方案内的结果数值单元格有意留空，不以预测值或空白的“0”代替未运行的实验。
