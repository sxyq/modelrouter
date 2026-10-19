# Scripts Directory Status & Governance Registry

This registry tracks the status and canonical destinations of all scripts in `scripts/` according to REPOSITORY_STRUCTURE_MIGRATION_20261018.md §IV and §VII.

| Script | Classification | Canonical Destination | Description / Active Process Binding |
|---|---|---|---|
| `serve_dashboard.py` | `ACTIVE_HOLD` | `our-project/code/src/modelrouter/telemetry/serve_dashboard.py` | Active on A6000 (PID 2349761). Serves `our-project/dashboard/` at port 8765. |
| `fetch_live_status.py` | `ACTIVE_HOLD` | `our-project/code/src/modelrouter/telemetry/fetch_live_status.py` | Active on A6000 (PID 2494953). Continuous status poller. Supports `--source local` and `--source mac`. |
| `oneshot_f05_to_f03_handover.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/oneshot_f05_to_f03_handover.py` | One-shot handover script (F05->F03). Execution-guarded to prevent accidental rerun. |
| `build_clean_chart_dashboard.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical dashboard generator script. |
| `build_clean_dashboard.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical dashboard builder. |
| `build_upgraded_dashboard.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical dashboard builder. |
| `generate_cds_dashboard.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical monolith HTML generator. Canonical dashboard is in `our-project/dashboard/`. |
| `benchmark_ollama_impact.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical GPU interference test script. |
| `val_benchmark_compare.py` | `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical comparison script. |
| `jev_laya_kev_typed_demo_v2.py`| `ARCHIVE_LEGACY` | `our-project/docs/operations/legacy/` | Historical typed system demonstration script. |
| `capture_dashboard_screenshots.py` | `TEST_TOOL` | `our-project/code/tests/` | Playwright screenshot verification tool. |
| `verify_dashboard_browser.py` | `TEST_TOOL` | `our-project/code/tests/` | Headless browser verification tool. |
