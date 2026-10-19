# ModelRouter · Harbor Official Benchmark Sandbox Gate & Diagnostic Audit

> **Date**: 2026-10-18 18:50 (CST)  
> **Status**: `BLOCKED_AWAITING_DOCKER_SOCKET_AUTHORIZATION`  
> **Protocol**: Official Harbor Docker Sandbox Isolation Protocol (V8 §7.4 & §8.2)

---

## 1. Executive Summary & Strict Scientific Honesty

In accordance with ModelRouter scientific integrity guidelines, **no unisolated host execution (Mac or Linux) or mock pass shall be recorded as an official benchmark score**. 

- **Official Benchmark Standard**: Requires containerized Harbor sandbox (`docker run` / Docker socket integration), official unaltered evaluators (e.g., `pytest-json-ctrf`), verified `trial_id`, and isolated container runtime logs.
- **Current Authorization Gate**:
  - **Mac Local Environment**: No Docker daemon (`docker: command not found`).
  - **A6000 Server (`k3s-infra-01`)**: Docker 29.4.1 is installed; however, socket `/var/run/docker.sock` is owned by `root:docker` (`srw-rw----`), and execution user `syy` is not currently in the `docker` group (`groups: syy sudo`).
  - **Rootless Container Alternative**: Evaluated `dockerd-rootless-setuptool.sh check`, which failed due to missing system package `uidmap` (`newuidmap`/`newgidmap`).
  - **Administrative Remedy**: Requires administrator to run:
    ```bash
    sudo usermod -aG docker syy
    ```
- **Current Formal Status**: Marked strictly as **`BLOCKED (AWAITING_DOCKER_SOCKET_AUTHORIZATION)`**.
- **Historical Unisolated Runs**: All 16 prior runs remain classified under `LOCAL_HOST_EXPERIMENTAL` (`HOST_PROCESS_UNISOLATED`) with 0.0 pass rate, and are never counted toward official paper baselines.

---

## 2. Infrastructure Readiness Checklist

All upstream sources, evaluators, and routing harnesses are 100% prepared to execute immediately upon granting Docker permissions:

| Component | Status | Source / Artifact Reference | Details |
| :--- | :---: | :--- | :--- |
| **Harbor Core Engine** | **READY** | `external/benchmarks/harbor` (Commit `36232c2`) | Official Python runner and trial environment |
| **Terminal-Bench 2.1 Tasks** | **READY** | `external/benchmarks/terminal-bench-2-1` (Commit `7131e43`) | 89 official standard tasks loaded |
| **Canary Evaluation Tasks** | **READY** | `fix-git`, `count-dataset-tokens` | Pre-staged for single-agent validation |
| **8-Policy Routing Harness** | **READY** | `experiments/agent_pilot/runner.py` | FixedStrong, FixedCheap, Random, RuleSticky, RouteLLM, SR-KNN, Laya, Kev |
| **Token Budget Telemetry** | **ACTIVE** | `experiments/agent_pilot/token_budget.json` | 368,520 / 1,000,000 tokens consumed (36.85%) |
| **Pricing Registry** | **READY** | `external/pricing/normalized_pricing_index.json` | 300+ models normalized from OpenRouter |

---

## 3. One-Click Trial Activation Protocol (Post-Authorization)

Once `syy` is added to group `docker`:
```bash
# 1. Verify Docker connection
docker ps

# 2. Launch Official Canary Trial with FixedStrong baseline
python -m experiments.agent_pilot.run_official_harbor_trial \
    --benchmark terminal-bench-2-1 \
    --task fix-git \
    --policy fixed_strong \
    --output runs/agent_pilot/official_trials/

# 3. Automatic Evaluator Validation
# Evaluator generates official CTRF json and container trial audit.
```
