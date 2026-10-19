# ModelRouter · Harbor / mini-swe-agent terminal runbook

Status at writing: CLI code and offline tests are committed. **A6000 production commands and pytest suite have not been run by this assistant**. Server Docker authorization and model-provider mini-swe-agent configuration remain to be checked by the Execution Agent. Do not claim an official Trial from this README.

## 1. Non-paying checks

Run from the repository root using the existing interpreter:

    export PYTHONPATH="$PWD/our-project/code/src"
    python -m modelrouter.benchmark preflight
    python -m modelrouter.benchmark run --task fix-git --agent oracle

The run command defaults to DRY_RUN and prints the exact official Harbor invocation. Cross-check against the installed 'harbor run --help' and 'harbor datasets list' on the machine.

## 2. Official Oracle on authorized sandbox

    python -m modelrouter.benchmark run --task fix-git --agent oracle --execute

It delegates actual execution to upstream Harbor. Resolve the generated Job directory from the console and installed Harbor configuration.

After verifying true model aliases and native tool calling under the existing private API URL/Key:

    python -m modelrouter.benchmark run --task fix-git \
      --agent mini-swe-agent --model 'openai/YOUR_VERIFIED_PROVIDER_MODEL' --execute

Do not literally use the placeholder model. mini-swe-agent v2 defaults to native tool calling. Oracle passing tests only the sandbox/verifier, not model correctness or dynamic routing. A custom ModelRouter dynamic mini-swe-agent class is not implemented by this CLI.

## 3. Original Job/Trial audit and continuous terminal watch

    python -m modelrouter.benchmark audit /REAL/HARBOR/JOBS/JOB_DIR
    python -m modelrouter.benchmark watch /REAL/HARBOR/JOBS/JOB_DIR --once
    python -m modelrouter.benchmark watch /REAL/HARBOR/JOBS/JOB_DIR \
      --interval 10 --output /PRIVATE/PROGRESS.json

Every verified trial requires its own config/lock/result and the on-disk original verifier reward. A matching original 0.0 is an official graded failure, not missing evidence. Project-generated trial identifiers are NOT proof of an official Job.

To resume a genuine existing Job:

    python -m modelrouter.benchmark resume /REAL/HARBOR/JOBS/JOB_DIR
    python -m modelrouter.benchmark resume /REAL/HARBOR/JOBS/JOB_DIR --execute

Resume is also dry-run unless --execute is explicit. Verify installed Harbor CLI version and 'harbor jobs resume --help' first; reconcile all old trial IDs to avoid duplicate paid calls.

## 4. Frozen scientific task partition

The project's router_data/terminal_bench_manifest.json defines its OWN canary (8), external_dev (24), and final_test (57), not an upstream official partition. CLI flags are --subset canary|dev|sealed. Sealed also requires --allow-sealed; actual sealed runs still need explicit human authorization. Never claim a dry run to be a benchmark.

## 5. Required 2-agent continuation

Agent A: Pin real Harbor and mini-swe-agent v2 versions; implement a genuine official BaseAgent-compatible mini model/Policy hook with identical Prompt/Tools/termination across Fixed/Laya/Kev. Collect original Verifier, ATIF and Job ID plus per-step route / TTFT / output TPS / tool walltime. Do not replace isolated Harbor with Mac or A6000 host shell.

Agent B: Audit provider/model aliases and native efforts using the existing local API config; verify Laya/Kev actions map to training class IDs; monitor actual usage and price; generate RQ1–RQ5 statistics ONLY from paired official verified task Episodes. Keep old synthetic examples separately labeled.

Each completed phase produces run_config.json, events.jsonl, tool_calls.jsonl, metrics.json, review.md, next_iteration.json, resume_state.json, and independent frozen task/config SHA. Next iteration reads the previous plan; do not repeat expensive completed tasks. Preserve Port 8000/8765 and live Laya/Kev training.

## 6. This milestone's limits

These new CLI commands perform preflight, guarded launch delegation, audit, progress watch and resume delegation; they DO NOT yet themselves implement a full dynamic mini-swe-agent or TTFT/TPS instrumentation. Build those only against actually installed upstream APIs. The audit is a structural evidence check; publication also requires validating Harbor version, locked task digests, and actual original Job integrity.

Tests committed but NOT run on server by this assistant:

    python -m pytest our-project/code/tests/benchmark/test_official_artifacts.py \
      our-project/code/tests/benchmark/test_benchmark_cli.py -q

Official docs: https://harbor-index.org/docs/run-terminal-bench-2-1 ;
https://github.com/harbor-framework/docs/blob/main/cli/run.mdx ;
https://github.com/SWE-agent/mini-swe-agent/blob/main/docs/advanced/v2_migration.md .
