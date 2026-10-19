# External Benchmarks Catalog

This directory tracks the upstream benchmark repositories used for Agent Pilot evaluation and baseline validation.

## Benchmarks Catalog

| Benchmark | Upstream Repository | Commit / Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Harbor** | [harbor-framework/harbor](https://github.com/harbor-framework/harbor.git) | `main` | Official Docker-isolated execution harness |
| **Terminal-Bench 2.1** | [harbor-framework/terminal-bench-2-1](https://github.com/harbor-framework/terminal-bench-2-1.git) | `7131e437` | Canonical terminal coding tasks (e.g., `fix-git`, `count-dataset-tokens`) |
| **TwinRouterBench** | [CommonstackAI/TwinRouterBench](https://github.com/CommonstackAI/TwinRouterBench.git) | `main` | Holdout routing task bank & SR-KNN state representations |
| **SWE-bench** | [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench.git) | `main` | Full repository bug-fixing benchmark |

## Evaluator Integrity Gate
- Without verified Docker container isolation, benchmark trials must fail-closed and register `NOT_EVALUATED`.
- Zero synthetic mock scores (1.0 or 0.0) may masquerade as official benchmark results.
