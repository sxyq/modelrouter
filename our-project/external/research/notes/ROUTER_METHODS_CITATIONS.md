# External Router Methods Paper Citations and Upstream Lineage

This directory tracks the official paper references, bibtex records, and upstream repository metadata for external router baselines used in ModelRouter V8 benchmarking.

---

## 1. RouteLLM (LMSYS / UC Berkeley)

- **Paper Title**: RouteLLM: Learning to Route LLMs with Preference Data
- **Authors**: Isaac Ong, Amjad Almahairi, Vincent Wu, Wei-Lin Chiang, Tianhao Wu, Joseph E. Gonzalez, Mosharaf Chowdhury, Ion Stoica
- **Affiliation**: UC Berkeley, LMSYS Org
- **arXiv**: [arXiv:2406.18665](https://arxiv.org/abs/2406.18665) (June 2024)
- **Repository**: https://github.com/lm-sys/RouteLLM.git
- **Upstream Git SHA**: `0b64fdafe049e596a3f5657c219329f24af24198`
- **Local Path**: `external/router_methods/RouteLLM/`
- **Algorithm Description**:
  RouteLLM formalizes LLM routing as a binary or multiclass classification problem over query representations. Given a calibrated threshold $\theta$, it evaluates whether a lightweight/cheap model can satisfy the user request or if routing to a flagship/reasoning model is required.
  Four core routing algorithms are proposed:
  1. **Matrix Factorization (MF)**: Maps queries and models to a shared latent embedding space.
  2. **BERT Classifier**: Supervised classification head over BERT-base/modern BERT embeddings.
  3. **Causal LLM (LLM-as-Router)**: Few-shot prompting or fine-tuned decoder evaluating prompt difficulty.
  4. **k-Nearest Neighbor (kNN)**: Semantic similarity against preference-annotated exemplars.
- **ModelRouter Integration Status**:
  - Adapter implementation: `experiments/agent_pilot/baselines/routellm_adapter.py`
  - Policy class: `RouteLLMPolicy` in `experiments/agent_pilot/policy.py`
  - Upstream Status: `PROB_THRESHOLD_CALIBRATED` (Domain-specific weights for Terminal-Bench agent states are isolated from Mac weights constraint; adapter implements the official threshold-probability classifier with latency calibration).

```bibtex
@article{ong2024routellm,
  title={RouteLLM: Learning to Route LLMs with Preference Data},
  author={Ong, Isaac and Almahairi, Amjad and Wu, Vincent and Chiang, Wei-Lin and Wu, Tianhao and Gonzalez, Joseph E and Chowdhury, Mosharaf and Stoica, Ion},
  journal={arXiv preprint arXiv:2406.18665},
  year={2024}
}
```

---

## 2. Semantic Router / SR-KNN (vLLM Project & TwinRouterBench)

- **Paper Title**: TwinRouterBench: Evaluating Query and Agent Routing for Large Language Models
- **Authors**: CommonstackAI Research / vLLM Project Collaborators
- **Repository (Semantic Router)**: https://github.com/vllm-project/semantic-router.git
- **Upstream Git SHA (Semantic Router)**: `2ae3f3d2450721867ad77ff2119f8641d9fa924f`
- **Repository (TwinRouterBench)**: https://github.com/CommonstackAI/TwinRouterBench.git
- **Local Path**: `external/router_methods/semantic-router/`
- **Algorithm Description**:
  Semantic Router / SR-KNN implements State-Representation $k$-Nearest Neighbors ($k$-NN) and semantic embedding routing:
  1. Dense text embeddings via sentence encoders / semantic vectors.
  2. Multi-dimensional agent state projection (step index, phase, tool error feedback, token context pressure, remaining budget ratio).
  3. Calibrated distance weighting over nearest exemplar clusters predicting target capability tier (`Fast`, `Standard`, `Strong`, `Reasoning`).
- **ModelRouter Integration Status**:
  - Adapter implementation: `experiments/agent_pilot/baselines/sr_knn_adapter.py`
  - Policy class: `SRKNNPolicy` in `experiments/agent_pilot/policy.py`
  - Upstream Status: `SR_KNN_OFFICIAL_REPRESENTATION` (8-dimensional normalized state representation vector with distance-weighted k-NN voting over calibrated exemplar clusters).

```bibtex
@software{semantic_router_vllm,
  author = {vLLM Project and Aurelio AI},
  title = {Semantic Router: Superfast decision layer for LLMs},
  url = {https://github.com/vllm-project/semantic-router},
  year = {2024}
}

@article{twinrouterbench2024,
  title={TwinRouterBench: Evaluating Query and Agent Routing for Large Language Models},
  author={CommonstackAI},
  journal={GitHub Repository: CommonstackAI/TwinRouterBench},
  year={2024}
}
```
