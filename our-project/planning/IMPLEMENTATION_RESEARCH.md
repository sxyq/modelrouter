# 路由实现调研与可发表、可开源方案

## 结论

建议实现一套“执行前一次选择 + 全量轨迹记账 + 可选在线扩展”的路由框架。第一版不要直接复刻某一篇论文，也不要把 KV 缓存、多 Agent 结构搜索和强化学习同时加入主方法。

推荐主线是：

```text
任务输入
  -> admission 特征提取
  -> 对每个 (model, effort) 预测成功率与任务费用分布
  -> 质量约束筛选
  -> 选择预计费用最低的配置
  -> 固定 harness 执行并记录整条轨迹
  -> 训练集追加新 episode，周期性更新模型
```

这个结构同时满足三件事：论文需要可辨认的问题定义，开源需要清楚的接口，商业部署需要模型供应商可替换。

## 已核实的开源实现

| 项目 | 本地位置 | 许可证 | 可以直接复用的部分 | 不应直接当作本论文方法 |
|---|---|---|---|---|
| MTRouter | `implementation/repos/mtrouter` | MIT | Agent 运行骨架、轨迹数据、XGBoost/Ridge 成本与效果预测、测试 | 它主要做逐 turn 路由；默认神经目标不是完整的执行前费用分布 |
| TwinRouterBench | `implementation/repos/twinrouterbench` | Apache-2.0 | RouterContext/RouterDecision 接口、provider usage 归一化、输入/缓存/输出费用计算、真实花费记账、动态评测 harness | 它的主轨是逐步路由；标签来自执行记录，不能替代执行前预测 |
| BEST-Route / HybridLLM | `implementation/repos/best-route-llm` | MIT | 模型与 test-time compute 的联合选择、ranker 训练流程 | 主要是单请求推理，不能直接代表长程 Agent |
| RouterBench | `implementation/repos/routerbench` | MIT | 统一路由接口、嵌入特征、MLP/KNN/SVM 路由、费用—效果曲线和 AIQ 计算 | 主要是单请求；费用不是整条 Agent 轨迹费用 |
| LLMRouterBench | `implementation/repos/llmrouterbench` | MIT | 数据采集、模型矩阵、统一评价和结果可视化 | 主要是 query 级路由，任务轨迹字段需要自行扩展 |
| AgentOpt | `implementation/repos/agentopt` | Apache-2.0 | provider 拦截、调用记录、价格表、模型选择和测试 | 更偏通用客户端优化；需补齐任务成功标签与任务级预测 |
| vLLM Semantic Router | `implementation/repos/semantic-router` | Apache-2.0 | 生产代理、会话路由、上下文连续性、缓存 token 观测、在线压测脚本 | 现有 agentic 脚本包含特定场景，不应直接当成论文数据 |
| LangGraph | `implementation/repos/langgraph` | MIT | 可选的状态化 Agent 执行图和工具节点 | 只提供运行时，不提供我们的费用预测方法 |

### 许可证判断

上述仓库的 MIT/Apache-2.0 许可证通常允许修改、分发和商业使用，但发布时仍要保留版权和许可证文本。真正商用前还需要分别核对：

- 依赖包的许可证；
- 模型权重和模型服务条款；
- SWE-bench、Terminal-Bench 等数据集的使用条件；
- API 供应商的价格、日志和数据留存条款；
- 论文代码中的第三方脚本和示例数据。

论文可以开源路由代码和匿名化日志格式，不应把密钥、闭源响应、受限数据和供应商内部价格文件提交到仓库。

## 推荐的系统结构

### 1. 运行层

用一个固定的 Agent harness 执行任务。harness 负责：

- 接收 `task_id`、repo 或工具环境；
- 为每次 LLM 调用生成 `episode_id` 和 `step_id`；
- 通过统一适配器调用 OpenAI-compatible、Anthropic、Gemini、vLLM 或本地服务；
- 捕获原始响应、usage、工具输入输出、错误、重试和终止原因；
- 根据环境测试、状态断言或人工评价生成 `resolved` 与质量分。

推荐参考 TwinRouterBench 的 `RouterContext`/`RouterDecision` 形状，但把第一版的 `select` 调用限制在任务开始处。之后再增加 step-level 模式，保证论文中的静态路由与动态扩展使用同一接口。

### 2. 费用层

每次调用保存供应商原始 usage，再归一化为：

```text
input_tokens
cache_read_tokens
cache_write_tokens
output_tokens
reasoning_tokens   # 若供应商提供
provider_cost_usd  # 若供应商提供
calculated_cost_usd
```

价目表必须带 `provider`、`model_id`、`effective_from`、`effective_to`、`input_per_million`、`output_per_million`、缓存价格和版本号。论文结果使用固定价目快照；在线服务使用当前价格，同时保留执行时采用的版本号。

### 3. 数据层

推荐的最小记录分成三张 JSONL 表：

```text
episode.jsonl
episode_id, task_id, split, scaffold_version, model, effort,
resolved, quality, total_cost_usd, total_latency_ms, stop_reason

call.jsonl
episode_id, step_id, model, effort, tool_name, retry_index,
input_tokens, cache_read_tokens, cache_write_tokens, output_tokens,
reasoning_tokens, cost_usd, latency_ms, error_type

task.jsonl
task_id, source, repo, issue_text, static_metadata, difficulty_bucket,
created_at, task_split, contamination_note
```

第一版不把终局字段放进 admission 特征。训练、验证和测试按 `task_id` 分开；同一任务的重复执行必须留在同一个切分中。

### 4. 预测层

候选动作：

```text
A = model x effort
```

输入只使用执行前可得到的信息：任务文本、仓库静态信息、工具集合、任务来源、模型和 effort 的公开属性、价格快照。

每个动作训练四个预测头：

```text
p_success(x, a)
q50_cost(x, a), q90_cost(x, a)
q50_calls(x, a), q90_calls(x, a)
q50_tokens(x, a), q90_tokens(x, a)
```

第一版采用文本嵌入 + GBDT/逻辑回归，输出校准后的成功概率和分位数。只有当简单方法与在线 bandit 对照后仍有稳定差距，才增加共享神经编码器或联合分布模型。

路由规则：

```python
eligible = [
    a for a in actions
    if p_success[a] >= quality_floor
    and q90_cost[a] <= budget_floor
]
if eligible:
    choice = min(eligible, key=lambda a: q50_cost[a])
else:
    choice = max(actions, key=lambda a: p_success[a] - risk_penalty[a])
```

主论文应同时报告点预测、区间覆盖和路由 regret，避免只展示平均费用下降。

## 研究方法与已有实现的组合关系

| 研究组件 | 最适合参考的实现 | 我们需要新增的内容 |
|---|---|---|
| 轨迹采集和 Agent 执行 | MTRouter、TwinRouterBench | 统一多供应商适配器、effort 维度、可重复任务切分 |
| 成本与缓存记账 | TwinRouterBench、AgentOpt、vLLM Semantic Router | reasoning token、失败成本、价格快照和任务级汇总 |
| 质量预测 | MTRouter、BEST-Route、RouterBench | 任务终局成功概率，而不是单次 response 分数 |
| 成本预测 | MTRouter 的 per-model XGBoost | 分位数、多次 rollout、调用数与费用的联合建模 |
| 选择策略 | BEST-Route、RouteLLM、WISERouter | 质量约束下的任务级选择，加入风险上界 |
| 评测 | TwinRouterBench、RouterBench、RouteGuard | share-matched 对照、任务聚类重采样、反转率和置信区间 |
| 商业服务 | vLLM Semantic Router、AgentOpt、LangGraph | API 中立、审计日志、超时回退、价格更新和租户隔离 |

## 论文版与商用版的共同接口

```python
class AdmissionRouter(Protocol):
    def select(self, task: TaskInput, actions: list[Action]) -> Decision:
        ...

class AgentExecutor(Protocol):
    def run(self, task: TaskInput, action: Action) -> EpisodeResult:
        ...

class CostLedger(Protocol):
    def record_call(self, record: CallRecord) -> None:
        ...
    def episode_total(self, episode_id: str) -> CostSummary:
        ...
```

论文实验可以用离线预测器实现 `AdmissionRouter`；商业服务可以换成远程模型或规则策略，执行层和记账层保持不变。这种边界能避免研究代码和生产代码互相依赖。

## 三阶段实现路线

### 阶段 A：费用与轨迹测量

范围：一个 SWE 或 Terminal 环境，3 个模型，2 个 effort，每个任务 2–3 次执行。

产出：统一 JSONL 日志、价格快照、固定 Agent harness、任务成功与费用统计、每个配置的 P50/P90 费用。

继续条件：固定策略之间存在稳定的任务条件差异；oracle 与固定策略之间有足够可利用的差距；差异不是少量任务造成的。

### 阶段 B：执行前静态路由

范围：任务文本和静态元数据；GBDT/逻辑回归预测器；质量阈值扫描。

产出：成功率预测、费用分位数预测、质量约束选择、always-cheap、always-strong、随机分配、share-matched 分配和在线 bandit 对照。

论文最低结果：至少一个主环境加一个泛化环境；真实成功率不下降或保持在预设范围；任务费用有稳定下降；预测区间覆盖率和置信区间完整。

### 阶段 C：在线扩展与服务化

可选内容：失败后升级、剩余费用估计、缓存状态、会话连续性和多租户预算。它们应作为独立实验，不改变阶段 B 的主结论。

商用服务需要增加：请求超时、供应商失败回退、成本上限、脱敏日志、租户配额、模型版本切换、审计导出和许可证清单。

## 论文可发表的最低证据包

1. 直接相关工作的正文证据表和完整本地 PDF 清单；
2. 至少一个 Agent 环境的多配置、多次执行数据；
3. 任务级费用、成功率、调用数、token、延迟和失败类型；
4. 与固定策略、随机分配、share-matched 分配和在线 bandit 的比较；
5. 按难度、模型对和质量阈值的排序分歧统计；
6. 预测误差、分位数覆盖、价格变化和任务分布变化实验；
7. 可运行 harness、路由器接口、价格表格式、日志 schema 和复现实验命令；
8. 许可证、模型条款和数据使用条件说明。

## 当前不建议做的事情

- 先实现强化学习，再寻找可解释的收益；
- 同时训练模型选择、Agent 拓扑、缓存策略和工具计划；
- 用任务完成后的调用数或质量作为执行前特征；
- 只报告一个平均 `$/resolved` 数字；
- 只依赖某个供应商的价格或某一批模型；
- 把论文仓库的 MIT/Apache-2.0 误解为模型权重、数据集和 API 都能自由商用。

## 本地实现材料

- 论文清单：[manifest.json](../literature/manifest.json)
- 直接相关证据表：[direct-evidence.md](../literature/evidence/direct-evidence.md)
- 论文 PDF：[pdfs/](../literature/pdfs/)
- 已核实开源实现：[repos/](repos/)
