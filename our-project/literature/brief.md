# Research Brief — 任务级成本感知模型路由（长程 Agent 任务）

Date: 2026-09-15
Depth: deep
Slug: task-level-cost-routing
Workspace: /Users/sunyiyang/Desktop/Project/路由/research/task-level-cost-routing/

## Refined question

面向尚未执行的长程 Agent 任务，在多个候选模型 × 推理档位中，**事前**预测整任务完成所需的
成功概率、调用次数、input/output/reasoning token、失败重试概率、最终质量、总费用与总延迟，
并在质量约束下选择预计总费用最低的配置——该研究问题被已有工作覆盖到什么程度？
“任务级成本反转”（单次更贵的模型可能 $/success 更低）是否已有系统证据？
贡献空间、方法风险、实验可行性与最小可行版本应如何设计？

## Scope boundaries

In scope:
- 查询级 / token 级 / Agent 轨迹级 / 系统级 LLM 路由（2023–2026，重点 2024–2026）
- cost-aware routing、cascades、adaptive/budgeted inference、reasoning-effort selection
- multi-model agents、agent orchestration 中的模型分配、执行成本、成功率
- 事前预测成功/调用次数/token/质量的方法；数据泄露与切分设计
- 评测基准与成本指标（$/resolved、Pareto 等）
- 核实“新意风险”表述；至少 10 篇相关工作详表

Out of scope:
- 具体写代码实现系统（仅设计 MVP 与路线图）
- 把博客/新闻稿当主证据
- KV-cache 服务优化为主线（可作条件变量/扩展）

## Assumptions

- 今天：2026-09-15。优先 arXiv 原文、会议正式页、开源代码。
- 本地已有材料：`相关论文表.md`（初稿定位表）、`papers/unified-ai-gateway.{pdf,txt}`（华为 Unified AI Gateway）。
- 用户目标会：Agent / LLM Systems / ML / NLP 会议。
- 明确区分“论文写明” vs “推断”；不用“首次/完全没人做过”。

## Existing local evidence (seed)

- Unified AI Gateway (arXiv 2609.06940)：请求级联合模型×位置×KV 动作；解析仿真；无任务级成功概率×调用数路由。
- 种子列表：AutoMix 2310.12963、Hybrid LLM 2404.14618、FrugalGPT 2305.05176、RouteLLM 2406.18665、Route-to-Reason 2505.19435、InfraMind 2606.11440、NOMA 2512.11001、MASS 2502.02533 等——需原文核实而非只信表。

## Angles (wave 1: F1–F3; wave 2: F4–F6; wave 3: F7–F8 if gaps)

- F1 查询级 LLM routing 主线原文核实（RouteLLM / Hybrid LLM / FrugalGPT / Route-on-Graph / RouterBench 等）
- F2 Agent 轨迹级 / multi-model agent 路由与编排（最可能撞车区）
- F3 cost-aware cascade / budgeted inference / reasoning-effort 联合选择 / 成本反转与 $/success
- F4 事前预测（成功/调用数/token/质量）方法与泄露控制
- F5 任务基准与实验可行性（SWE / 终端 / 网页 / 工具调用）
- F6 2025–2026 最新 agent router / task-level cost 论文补漏
- F7 成本指标定义与统计（$/resolved、Pareto、反转检验）
- F8 MVP 系统组件与基线设计对照已有系统

## Deliverable

REPORT.md：一页内结论 + 详细证据表（≥10 篇，≥5 篇最直接相关，逐篇 12 字段）+ 方法/实验/基线/消融/路线图 + 最终判断。写入本工作区 REPORT.md，并在回复中给用户完整版。
