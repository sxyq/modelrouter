# ModelRouter · Physical Directory Inventory & Migration Ledger (2026-10-19)

> Generated autonomously by ModelRouter Execution Agent conforming to V9 specifications and `REPOSITORY_STRUCTURE_MIGRATION_20261018.md`.

---

## 1. Executive Summary

| Action Code | Count | Meaning & Operational Policy |
|---|---:|---|
| `KEEP_CANONICAL` | 1,126 | Already located in canonical `our-project/` structure. Verified and actively maintained. |
| `DEDUPLICATE_VERIFIED` | 139 | Deduplicated files in `research/task-level-cost-routing/`. Replaced 186 MB of duplicate binaries with relative symlinks to canonical `our-project/external/research/`. Zero broken links. |
| `REFERENCE_EXTERNAL` | 17,137 | External Git benchmark/framework checkouts (`harbor`, `terminal-bench-2-1`, `TwinRouterBench`, `SWE-bench`, `routellm`, `semantic-router`). Retained under `our-project/external/`. |
| `MOVE_SAFE` | 37 | Non-active code, tests, and configuration assets eligible for safe relocation to `our-project/code/` and `our-project/experiments/`. |
| `KEEP_COMPAT_SHIM` | 43 | Crucial transition scripts (`experiments/agent_pilot/*.py`, `experiments/router_serving/*.py`, `router_data/*.py`). Provide thin backward-compatibility shims forwarding to `modelrouter.*`. |
| `ARCHIVE_LEGACY` | 5 | Historical one-shot transition scripts (`oneshot_f05_to_f03_handover.py`, historical dashboard generators). Execution-guarded to prevent accidental execution. |
| `ACTIVE_HOLD` | 4 | Actively running processes on A6000 GPU/CPU (`laya_batch_train.py`, `run_kev_continuous_train.py`, `serve_dashboard.py`, `fetch_live_status.py`). Protected from any movement or termination during active runs. |
| **Total Tracked & Audited Assets** | **18,491** | Complete physical filesystem mapping across Mac and A6000. |

---

## 2. Active Training & Serving Protection (`ACTIVE_HOLD`)

The following files are actively held by live OS processes and must not be renamed, moved, or deleted until natural completion:

1. **`router_data/laya_batch_train.py`**: Held by A6000 PID `1202621` (Laya F06 training, Chunk 151/361, Step 65,468/92,280).
2. **`router_data/run_kev_continuous_train.py`**: Held by A6000 PID `1357763` / `1357764` (Kev C03 training, Step 12,460/16,857).
3. **`router_data/kev_candidate_dispatcher.py`**: Held by A6000 PID `2042701` (Polling every 60s to transition Kev candidates).
4. **`scripts/serve_dashboard.py`**: Held by A6000 PID `2349761` (Serving `our-project/dashboard/` at `http://10.16.15.202:8765/`).
5. **`scripts/fetch_live_status.py`**: Held by A6000 PID `2494953` (Local telemetry collector updating `live_status.json` every 5s).

---

## 3. Detailed CSV Ledger

Full machine-readable ledger is persisted at:
[migration_ledger_20261019.csv](file:///Users/sunyiyang/Desktop/Project/路由/our-project/docs/operations/migration_ledger_20261019.csv)
