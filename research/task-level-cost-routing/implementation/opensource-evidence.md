# 开源实现证据

以下判断来自已拉取的 Git 仓库、许可证文件、README 和入口代码。许可证是代码仓库的证据，不代表论文数据、模型权重或供应商服务可以按同一条件使用。

| 项目 | 官方仓库 | 许可证证据 | 入口与可复用代码 | 当前判断 |
|---|---|---|---|---|
| MTRouter | [ZhangYiqun018/MTRouter](https://github.com/ZhangYiqun018/MTRouter) | [`LICENSE.md`](https://github.com/ZhangYiqun018/MTRouter/blob/main/LICENSE.md)，MIT | `scripts/train_q_function.py`、`scripts/train_per_model_xgboost.py`、`scripts/collect_data.py`、`tests/` | 最适合拿来做 Agent 采集和预测器对照；逐 turn 选择需要改成 admission 模式 |
| BEST-Route / HybridLLM | [microsoft/best-route-llm](https://github.com/microsoft/best-route-llm) | [`LICENSE.md`](https://github.com/microsoft/best-route-llm/blob/main/LICENSE.md)，MIT | `train_router.py`、`hybrid_llm/` | 可复用模型与 test-time compute 联合选择；任务轨迹字段需要自行增加 |
| TwinRouterBench | [CommonstackAI/TwinRouterBench](https://github.com/CommonstackAI/TwinRouterBench) | [`LICENSE`](https://github.com/CommonstackAI/TwinRouterBench/blob/main/LICENSE)，Apache-2.0 | `swerouter/router.py`、`swerouter/usage.py`、`swerouter/trace_cost_audit.py`、`main/pricing.py` | 最适合复用费用、缓存和动态评测接口 |
| AgentOpt | [AgentOptimizer/agentopt](https://github.com/AgentOptimizer/agentopt) | [`LICENSE`](https://github.com/AgentOptimizer/agentopt/blob/main/LICENSE)，Apache-2.0 | `src/agentopt/model_selection/`、调用记录与 provider 测试 | 最适合参考客户端拦截、价格表和调用记录 |
| vLLM Semantic Router | [vllm-project/semantic-router](https://github.com/vllm-project/semantic-router) | [`LICENSE`](https://github.com/vllm-project/semantic-router/blob/main/LICENSE)，Apache-2.0 | `bench/agentic_routing_live_benchmark.py`、`bench/cache_token_probe.py` | 最适合参考生产代理、会话连续性和缓存可观测性 |
| RouterBench | [withmartian/routerbench](https://github.com/withmartian/routerbench) | [`LICENSE`](https://github.com/withmartian/routerbench/blob/main/LICENSE)，MIT | `routers/abstract_router.py`、`routers/mlp_router.py`、`evaluation/AIQ.py` | 适合单请求路由与费用—效果曲线对照 |
| LLMRouterBench | [ynulihao/LLMRouterBench](https://github.com/ynulihao/LLMRouterBench) | [`LICENSE`](https://github.com/ynulihao/LLMRouterBench/blob/main/LICENSE)，MIT | `data_collector/`、`evaluation/`、`baselines/` | 适合数据采集与统一评价参考，主要面向 query 路由 |
| LangGraph | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | [`LICENSE`](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)，MIT | 状态化执行图、工具节点和持久化接口 | 作为可选执行层，不承担路由算法 |

## 需要特别标出的缺口

- CASTER PDF 没有找到随论文给出的可确认代码仓库，因此不能把 CASTER 声称为可复用实现。
- `inphotoo/earlyeval` 的当前 README 题目是 RouterBench，内容与 EarlyEval 论文不一致；本地没有把它列为 EarlyEval 的官方代码。
- Route-to-Reason 的 README 提供了代码仓库，但本轮没有发现许可证文件，因此商用整合前需要单独确认许可。
- 论文 PDF 与代码仓库的版本日期可能不同；复现实验要记录 commit、模型版本、价格版本和运行配置。
