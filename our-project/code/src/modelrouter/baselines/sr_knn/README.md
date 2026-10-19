# SR-KNN Independent Baseline Package

This package encapsulates the State-Representation k-NN (SR-KNN) algorithm derived from vLLM semantic-router and TwinRouterBench.

## Upstream Metadata
- **Repository**: [https://github.com/vllm-project/semantic-router.git](https://github.com/vllm-project/semantic-router.git)
- **Locked Commit**: `2ae3f3d2450721867ad77ff2119f8641d9fa924f`
- **Benchmark Source**: CommonstackAI/TwinRouterBench holdout evaluation framework
- **Citation**: Aurelio et al., *Semantic Router: Fast, Dynamic and Highly Performant Vector Routing* (2024)

## Architecture
Extracts an 8-dimensional normalized state representation vector:
1. `step_ratio` (step / max_steps)
2. `phase_encoding` (0.0=inspect, 0.5=modify, 1.0=verify)
3. `last_exit_code` (0.0=success, 1.0=error)
4. `context_token_ratio` (capped at 16k tokens)
5. `budget_remaining_ratio`
6. `tool_error_rate` (errors / step)
7. `historical_fail_fraction`
8. `task_difficulty_score`

Calculates Euclidean distance to calibrated reference exemplars and applies distance-weighted $k$-NN voting to select the optimal model tier (`Fast`, `Standard`, `Strong`, `Reasoning`).

## CLI Usage
```bash
python -m modelrouter.baselines.sr_knn.runner -k 3 --phase modify --context-tokens 5000
```
