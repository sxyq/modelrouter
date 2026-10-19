# External Router Methods (Upstream Reference Catalog)

This directory tracks upstream router baselines and repositories used for comparative benchmarking against ModelRouter.

## Upstream Baselines

1. **RouteLLM**
   - **Repository**: [https://github.com/lm-sys/RouteLLM.git](https://github.com/lm-sys/RouteLLM.git)
   - **Locked Commit**: `0b64fdafe049e596a3f5657c219329f24af24198`
   - **Paper**: *RouteLLM: Learning to Route LLMs with Preference Data* (Ong et al., arXiv:2406.18665, 2024)
   - **Canonical Implementation & Adapter**: [`modelrouter.baselines.routellm`](../../code/src/modelrouter/baselines/routellm)

2. **State-Representation k-NN (SR-KNN / Semantic Router)**
   - **Repository**: [https://github.com/vllm-project/semantic-router.git](https://github.com/vllm-project/semantic-router.git)
   - **Locked Commit**: `2ae3f3d2450721867ad77ff2119f8641d9fa924f`
   - **Benchmark Source**: CommonstackAI/TwinRouterBench holdout evaluation
   - **Paper**: *Semantic Router: Fast, Dynamic and Highly Performant Vector Routing* (Aurelio et al., 2024)
   - **Canonical Implementation & Adapter**: [`modelrouter.baselines.sr_knn`](../../code/src/modelrouter/baselines/sr_knn)

## Independent Method Package Principle (Task A3)

Per architectural guidelines, each external router baseline is packaged as an independent unit containing:
- Mathematical adapter class
- Upstream configuration and locked commit
- Standalone CLI runner
- Dedicated unit tests
- Documentation mapping
