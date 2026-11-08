# ModelRouter正式源码职责

现行正式包位于`src/modelrouter/`。唯一Agent执行链为 **Harbor → ModelRouterMiniSweAgent → DefaultAgent**，完整任务使用原官方Verifier。结果入口为[89题任务进度与费用](../results/benchmark/README.md)，版本与训练入口为[训练总报告](../results/training/training_research.md)。

## Installation

Install in editable mode:

```bash
pip install -e our-project/code
```

Or ensure `our-project/code/src` is included in `PYTHONPATH`:

```bash
export PYTHONPATH="/Users/sunyiyang/Desktop/Project/路由/our-project/code/src:$PYTHONPATH"
```

## 职责与唯一事实来源

| 包/文件 | 职责 |
|---|---|
| `benchmark/harbor_agent.py` | `ModelRouterMiniSweAgent`复用上游`DefaultAgent`，无第二套正式Agent循环 |
| `benchmark/__main__.py`、`iterations.py`、`official_artifacts.py` | 原Harbor命令入口、时间事件、官方结果读取 |
| `benchmark/rq1_analysis.py`、`rq3_analysis.py` | 从保存事实派生质量、费用和粒度分析 |
| `agent/state.py` | Agent任务、工具历史、缓存、进度和时间状态 |
| `v9/runtime/context.py` | T/M/H决策前序列化；训练与原生前向使用同义表示 |
| `v9/runtime/decision_hook.py`、`checkpoint.py` | 单Agent路由时机、合法Model×Native Effort评分及两Router原生前向 |
| `providers/registry.py` | 精确模型、原生档位、组合ID、能力目标和参考价格 |
| `providers/provider.py`、`protocols.py`、`usage.py` | 实际调用、Responses/Chat原生参数、返回身份、缓存读取及费用 |
| `v9/capabilities/` | AA精确模型/档位的TTL、force、STALE与同批版本 |
| `v9/teacher/trigger.py`、`assessor.py` | 低频Luna触发、短评和真实教师用量 |
| `v9/training/` | 原任务截止、联合监督、训练材料和原Trainer接续 |
| `training/laya/`、`kev/`、`common/` | 原Laya/Kev训练、队列、参数保存及恢复 |
| `data_pipeline/`、`datasets/` | 已有公开来源、清洗和来源引用、训练视图 |
| `baselines/` | 固定模型、随机和具名规则；结果只记实际执行 |
| `serving/` | 原FastAPI和Laya/Kev加载；研究版不自动替换Serving |
| `sandbox/` | 原Harbor环境与任务加载 |
| `telemetry/` | 原事件派生账本、资源、报告与看板 |

当前Registry为`gpt-6-luna`、`glm-5.3-flash`、`gpt-6.1-terra`共15登记组合。GLM Chat的Low/High/Max均已有有效工具及完整Harbor官方Reward 1，返回Effort未报告；Luna Max→xhigh、Terra none→medium保留原记录，不改请求标签。旧HY4仅在历史配置、训练和结果中保留。

AA的TTL自动更新、force、STALE和同批固定版本已经实现；Registry派生模型/档位目标，并进入Laya/Kev的M输入。当前v7为130指标、Intelligence Index5.0.1，Luna/Terra各六档，GLM仅Max有独立成绩，Low/High缺测。在线路由不逐次请求AA。

新池两研究版各完成17更新，当前三题完整比较及全部异常保留原Episode版本。最终编码去重后241保存前缀由48截断降为0、四实体真实前向完成，该输入版本尚无完整Episode。源码职责整理已完成，自有Python245个、最大982行，详细出处见[原执行报告](../results/iterations/20261108-v9-k3-training/review.md)。

`agent/legacy.py`仅留历史，不由正式包导出或调用；已删除的独立Agent Pilot、development执行、Alias、重复logger、原生mini中继和模拟RQ生成器不是入口。旧Mock图表与展示工具按历史用途保存。RQ3只研究单Agent任务开始、阶段、真实子任务边界和生成粒度。

## CLI Usage

```bash
# Read local status
python -m modelrouter status
```

Agent Benchmark execution uses Harbor's official `DefaultAgent` path. This package does not document a local routing demo as a benchmark entry point.
