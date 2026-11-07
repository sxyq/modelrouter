# ModelRouter Package

The formal Python package for the ModelRouter project.

## Installation

Install in editable mode:

```bash
pip install -e our-project/code
```

Or ensure `our-project/code/src` is included in `PYTHONPATH`:

```bash
export PYTHONPATH="/Users/sunyiyang/Desktop/Project/路由/our-project/code/src:$PYTHONPATH"
```

## Structure

- `modelrouter.agent`: 原单 Agent loop、状态管理和 Provider 接入；按模型生成边界请求路由。
- `modelrouter.baselines`: Fixed, random, sticky and explicitly named heuristic policies; Laya/Kev use real native inference. The old example-weight RouteLLM/SR-KNN implementations were removed and are not official comparator results.
- `modelrouter.benchmark`: Official Harbor trials, evaluation matrix, scoring.
- `modelrouter.common`: Shared schemas and utilities.
- `modelrouter.data_pipeline`: Data source extraction, cleaning, quality assurance.
- `modelrouter.datasets`: Training views, splits, feature extractors.
- `modelrouter.providers`: LLM Provider adapters, registry, pricing, token budget.
- `modelrouter.sandbox`: Harbor environment execution and task loading.
- `modelrouter.serving`: FastAPI serving endpoints, Laya and Kev model loaders.
- `modelrouter.telemetry`: Logging, ledger tracking, live telemetry collector.
- `modelrouter.training`: Training recipes, queue management, checkpoint retention.

当前代码中的 `V9_MODEL_IDS` 仍是上一轮 Luna/Terra/HY4 清单；GLM-5.3-Flash 与新 15 个 Provider 原生 Model×Effort 候选尚未接入代码。GLM 预期使用 Chat Completions 的 low/high/max，渠道未绑定，Provider 正在核对 `/models`，不写作已调用或已验证。AA 实际刷新正在进行，但刷新入口仍是手动脚本 `python -m modelrouter.v9.capabilities.refresh`；TTL 自动更新和 `--force` 尚未实现。精确身份、合法 Effort 和能力分数以 Provider/实测证据为准。

正式 Benchmark 只经 Harbor 官方 `DefaultAgent` 与原版 Evaluator。`runtime/development.py`、benchmark development 命令、`sandbox/canary_verifier.py` 和 `experiments/harbor` 同名 shim 已删除；旧 Mock `pwd`/`fix-git` 分数不是可运行或推荐的 smoke 入口。`agent/legacy.py` 仅留历史，不由 SingleAgent 包导出或正式调用。RQ4/RQ5 的模拟结果生成源码已删除，观察汇总入口为 `modelrouter.benchmark.rq1_analysis`。GLM 渠道授权与绑定待确认，尚无新固定 K=3 Harbor 实验。

## CLI Usage

```bash
# Read local status
python -m modelrouter status
```

Agent Benchmark execution uses Harbor's official `DefaultAgent` path. This package does not document a local routing demo as a benchmark entry point.
