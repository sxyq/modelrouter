# RouteLLM Independent Baseline Package

This package encapsulates the official RouteLLM matrix factorization / logistic win-rate routing algorithm.

## Upstream Metadata
- **Repository**: [https://github.com/lm-sys/RouteLLM.git](https://github.com/lm-sys/RouteLLM.git)
- **Locked Commit**: `0b64fdafe049e596a3f5657c219329f24af24198`
- **Citation**: Ong et al., *RouteLLM: Learning to Route LLMs with Preference Data*, arXiv:2406.18665 (2024)

## Architecture
Calculates the strong model win rate $P(\text{Strong} \mid \text{state})$ via calibrated logistic projection over normalized state dimensions:
1. Instruction length
2. Context token count
3. Step progress ratio
4. Last tool exit code
5. Tool error rate
6. Budget remaining ratio

If $P(\text{Strong}) \ge \theta$ (default $\theta = 0.55$), the request routes to the Strong model; otherwise to the Cheap model.

## CLI Usage
```bash
python -m modelrouter.baselines.routellm.runner --threshold 0.55 --instruction "Fix git repo bug"
```
