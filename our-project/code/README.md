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

- `modelrouter.agent`: SingleAgent loop, state management, provider bridging.
- `modelrouter.baselines`: External baselines (RouteLLM, SR-KNN, heuristics).
- `modelrouter.benchmark`: Official Harbor trials, evaluation matrix, scoring.
- `modelrouter.common`: Shared schemas and utilities.
- `modelrouter.data_pipeline`: Data source extraction, cleaning, quality assurance.
- `modelrouter.datasets`: Training views, splits, feature extractors.
- `modelrouter.providers`: LLM Provider adapters, registry, pricing, token budget.
- `modelrouter.sandbox`: Harbor environment execution and task loading.
- `modelrouter.serving`: FastAPI serving endpoints, Laya and Kev model loaders.
- `modelrouter.telemetry`: Logging, ledger tracking, live telemetry collector.
- `modelrouter.training`: Training recipes, queue management, checkpoint retention.

## CLI Usage

```bash
# Check status
python -m modelrouter status

# Test routing decision
python -m modelrouter route --model laya --prompt "Fix merge conflicts in git"
python -m modelrouter route --model kev --prompt "Design a thread-safe cache"
```
