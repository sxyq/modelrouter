# ModelRouter Results · Provenance and Publication Status

**These existing result files are NOT verified official Harbor benchmark results.** See the machine-readable [RQ1–RQ5 provenance audit](../experiments/manifests/scientific_result_provenance_audit_20261019.json). Do not copy their precision values, CIs, speedups, or conclusions into formal paper claims unless the original official Harbor job/trials are supplied and independently audited.

| Result folder | Current status | Why |
|---|---|---|
| benchmark/rq1 | UNVERIFIED_LEGACY_EPISODE_LEDGER | Historical episode CSV lacks original official Harbor verifier proof; policy task counts differ |
| benchmark/rq3 | HARDCODED_EXAMPLE_MATRIX | Analysis has in-source empirical_matrix constants |
| benchmarks/rq2_data.json | SYNTHETIC_POOL_HEURISTICS | Pool scores are hardcoded by pool ID |
| benchmarks/rq4_data.json | PREFILLED_CONFIG_NUMBERS | Percentage comparisons are read from static configurations |
| benchmarks/rq5_data.json | PREFILLED_MANIFEST_HYPOTHESIS | Success, USD, and 0.72 cutoff are not estimated from official trials |

The actual Laya and Kev fixed-validation training results are separately tracked and must not be conflated with agent task-success results.

## Official Harbor artifact audit (new, CPU-only)

From an installed ModelRouter package:

    python -m modelrouter.benchmark preflight
    python -m modelrouter.benchmark audit /path/to/actual/harbor/jobs/job_name
    python -m modelrouter.benchmark watch /path/to/actual/harbor/jobs/job_name --interval 10 --output /path/to/local/progress.json

No command above starts a paid model run. The auditor checks the original job config/lock/result and each trial's config/lock/result and original verifier reward. Actual Harbor trial generation still requires an authorized sandbox and the official Harbor runner. Missing verifier evidence is NOT_EVALUATED; a **real official zero reward** is a graded failure, not missing data. A structural check cannot prove all files are genuinely from a trusted Harbor run; the locked source, task digest, and environment must also be checked.

## Promotion to paper result

Only after the same-task policies finish a genuine Harbor Job, with source/dataset hashes, real model identity and usage, unique trial IDs, original verifier results, and matched experimental parameters, may an aggregator emit an OFFICIAL_EVALUATED paper statistic. Existing synthetic/demo artifacts remain available for renderer development but are not scientific findings.
