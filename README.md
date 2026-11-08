# ModelRouter

ModelRouter 研究长程 **单 Agent** 执行中的模型与 Provider 原生推理档位联合路由，并以真实任务成功率和完整执行成本评价阶段、实际子任务边界及生成决策粒度。当前方法与结果入口见 [研究总纲](our-project/planning/RESEARCH_OVERVIEW.md)、[项目现状](our-project/planning/PROJECT_STATUS.md) 和 [实验决策记录](our-project/planning/EXPERIMENT_QA.md)。旧目录迁移和双子代理计划仅为历史资料。

ModelRouter 是面向长程 Agent 任务的模型、推理档位与成本研究项目。

**正式RQ1正在运行（2026-11-09）**：[Terminal-Bench 2.0批次](our-project/results/benchmark/rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)，官方89题、17策略、seed42，共1513个任务/策略位置。固定模型阶段四并发，随后四Router实体各Teacher OFF/ON两并发；最新通过/失败/无Reward、运行中与未开始数量由该批次原记录更新。[旧2.1覆盖](our-project/results/benchmark/README.md)单独保留。

## 项目目录分类

| 职责 | 当前目录 | 主要入口与内容 |
|---|---|---|
| 正式源码 | `our-project/code/src/modelrouter/` | [包职责](our-project/code/README.md)：Harbor适配、状态、Provider、联合路由、AA、教师、训练与Serving |
| 当前自有测试 | `our-project/code/tests/` | 按正式模块分类；原`router_data/`七文件归入training/telemetry，旧Pilot文件归入operations/legacy |
| 保留的命令入口 | `router_data/`、`scripts/`、根目录Python入口 | 复用已有包及训练路径；[脚本分类](scripts/README.md)，历史脚本单列 |
| 科研规划 | `our-project/planning/` | 四份现行核心规划，旧方案按日期保留 |
| 数据与来源 | `our-project/data/`、`data/` | [数据总入口](our-project/data/README.md)：公开来源、自有调用、训练材料、用途；大型全量保留A6000原位置 |
| 完整任务结果 | `our-project/results/benchmark/rq1/terminal-bench-2.0/`、`our-project/results/iterations/` | 正式2.0 RQ1唯一批次；[75历史批次索引](our-project/results/README.md#全项目迭代目录索引)保留原Harbor/Verifier |
| 任务覆盖与历史图表 | `our-project/results/benchmark/`、`benchmarks/` | [89题进度、Pass率与费用](our-project/results/benchmark/README.md)；预填图表列为历史 |
| 训练结果与参数 | `our-project/results/training/`、`runs/`、A6000 `models/` | [版本与训练](our-project/results/training/training_research.md)；原始、新池、旧参考、Serving及F15恢复分别保留 |
| 实验配置 | `our-project/experiments/`、`experiments/` | 现行模型/协议配置、原实验参数；私人用量与凭据不公开 |
| 文献与外部参考 | `our-project/literature/`、`our-project/external/`、`research/`、`papers/`、`external-projects/` | 论文、笔记、来源登记、历史研究；根`external/`保存本机上游仓库，不纳入Git |
| 汇报与展示 | `汇报/`、`our-project/汇报/`、`our-project/dashboard/`、`docs/training-dashboard/` | 论文图表方案、组会资料和已有看板；展示数值按原来源解释 |
| 历史运行资料 | `our-project/docs/`、`docs/` | 日期化报告及[旧Docker资料](our-project/docs/operations/legacy/HARBOR_DOCKER_STATUS_20261018.md)，不作当前执行指令 |
| 本地运行与生成产物 | `.runtime/`、`our-project/.runtime/`、`.tmp/`、`output/`、Python缓存 | 环境、私有请求与生成文件，保留本地；`.git/`及旧`.workbuddy/`资料保持原位置 |

**数据来源与 Provider 政策台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md)：公开轨迹、模型比较、缓存、时间/预算与 Provider 来源状态。台账是来源登记，不代表已有原生档位实测分数或新实验结果。

**全项目数据与成果**：[数据总入口](our-project/data/README.md)列出已探索来源、取得的数据、训练材料和用途；[模型版本与训练进度](our-project/results/training/training_research.md)区分原始版、新GLM研究版、旧固定Val参考、Serving和F15恢复。当前两新池代表各17更新已完成，原38组25完成，F15保存61180步，19:10台北取样无训练进程。

**完整任务成果**：[89题清单与费用](our-project/results/benchmark/README.md)：Agent尝试29题，22题有官方Reward，7题尝试但无Reward，60题尚无Agent运行；神经Router参与25题。当前GLM池三题中Laya原始/训练通过2/3、1/3，Kev两版各1通过/1失败/1缺Reward。模型+教师已知参考费分别$0.13532442/$0.11108159、$0.03250188/$0.17776966，除原始Kev外均有请求费用缺失；全部实收及资源价未知。[75批次](our-project/results/README.md#全项目迭代目录索引)的198记录保留旧池、映射和Oracle身份。

原始服务器日志、凭据、浏览器调试文件和外部仓库源码不纳入本仓库。

## 外部文本模型配置

当前联合候选为 GPT-6 Luna、GLM-5.3-Flash 与 GPT-6.1 Terra。精确 `model_id`、Provider、协议、原生 Effort 菜单和当前可用条件按 Registry 与实际 Provider 能力记录，不假设不同模型支持相同档位，也不将旧 HY4 结果改写为 GLM 结果。

GLM沿唯一私人配置绑定Colink，精确请求与返回为`glm-5.3-flash`。Low/High/Max均已有实际工具及原Harbor官方Reward 1，返回Effort未报告；旧High额度耗尽、429与空流保持。49次最新尝试已结束，33有效终局/21个1/12个0，16无Reward；训练收益及完整现金净收益仍缺。

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
