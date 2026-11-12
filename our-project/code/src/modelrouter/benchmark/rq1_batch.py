"""Batch the existing official Harbor runner; retain one independent episode per unit."""
from __future__ import annotations

import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import asdict
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

from . import iterations
from .harbor_agent import legal_actions, mini_configuration
from .official_artifacts import audit_job
from modelrouter.providers.registry import MODEL_REGISTRY, V9_MODEL_IDS
from modelrouter.v9.capabilities.features import load_current
from modelrouter.providers.base import ProviderResponseError
from modelrouter.providers.provider import OpenAICompatibleProvider


def prepare(config_path, revision):
    config = json.loads(config_path.read_text())
    root = iterations.ROOT / config["result_dir"]
    if (root / "manifest.json").exists():
        return root, json.loads((root / "config.json").read_text())
    registry = json.loads((iterations.ROOT / config["registry_path"]).read_text())
    dataset = next(d for d in registry if d["name"] == "terminal-bench" and d["version"] == "2.0")
    original = json.loads((iterations.ROOT / "router_data/terminal_bench_manifest.json").read_text())
    subsets = {t["task_id"]: subset for subset, group in original["subsets"].items() for t in group["tasks"]}
    source = iterations.ROOT / config["task_source"]
    tasks = []
    for task in dataset["tasks"]:
        if "task_ids" in config and task["name"] not in config["task_ids"]:
            continue
        definition = tomllib.loads((source / task["path"] / "task.toml").read_text())
        exposed = task["name"] in config["historically_exposed_tasks"]
        tasks.append({"task_id": task["name"], "path": task["path"],
                      "git_url": task["git_url"], "git_commit_id": task["git_commit_id"],
                      "original_subset": subsets[task["name"]], "historically_exposed": exposed,
                      "used_for_current_training": task["name"] in config["current_training_tasks"],
                      "used_for_model_selection": task["name"] in config["model_selection_tasks"],
                      "environment": definition["environment"], "agent": definition["agent"],
                      "verifier": definition["verifier"]})
    priority = {task: index for index, task in enumerate(config.get("task_priority", []))}
    tasks.sort(key=lambda t: (priority.get(t["task_id"], len(priority)), t["agent"]["timeout_sec"], t["task_id"]))
    config.update(source_revision=revision, started_at=iterations.now(), tasks=tasks,
                  capability_snapshot=(json.loads((iterations.ROOT / config["capability_snapshot_path"]).read_text())["capability_snapshot"]
                                       if config.get("capability_snapshot_path") else load_current()),
                  harbor_version=version("harbor"), mini_swe_version=version("mini-swe-agent"),
                  model_registry={k: asdict(MODEL_REGISTRY[k]) for k in V9_MODEL_IDS},
                  candidate_actions=legal_actions(V9_MODEL_IDS))
    units = [{"task_id": t["task_id"], "strategy_id": s["id"], "seed": seed,
              "unit_id": f"{t['task_id']}--{s['id']}--s{seed}", "status": "PENDING"}
             for t in tasks for s in config["strategies"] for seed in config["seeds"]]
    iterations.write_atomic(root / "config.json", config)
    (root / "jobs.jsonl").touch()
    iterations.write_atomic(root / "manifest.json", {
        "run_id": config["run_id"], "benchmark_name": "Terminal-Bench", "benchmark_version": "2.0",
        "source_revision": revision, "dataset": dataset, "tasks": tasks, "units": units,
        "protocol": {k: config[k] for k in ("max_steps", "max_output_tokens", "resources", "seeds")},
        "checkpoint_selection": "PREDECLARED_GLM_POOL_REPRESENTATIVES_NOT_PROVEN_STRONGEST",
        "capability_snapshot_id": config["capability_snapshot"]["snapshot_id"]})
    return root, config


def recovery_reason(path):
    """Recover technical interruptions only; never repeat a valid official score."""
    observed = [t for job in (path / "jobs").glob("*") for t in audit_job(job)["trials"]]
    if any(t["status"] == "OFFICIAL_ARTIFACT_VERIFIED" and t["reward"] in (0, 1) for t in observed):
        return None
    if not observed:
        return None
    trial = max(observed, key=lambda t: t.get("finished_at") or "")
    error = trial.get("error") or {}
    kind, message = error.get("exception_type"), error.get("exception_message", "")
    if "dependency uvx absent" in trial.get("reason", "") or "CTRF report absent" in trial.get("reason", ""):
        return "VERIFIER_DEPENDENCY"
    if kind in ("URLError", "RemoteDisconnected", "ConnectionResetError", "TimeoutError", "IncompleteRead"):
        return "PROVIDER_TRANSPORT"
    if kind == "HTTPError" and any(str(code) in message for code in (408, 429, 500, 502, 503, 504, 509, 520, 522, 524)):
        return "PROVIDER_HTTP"
    if kind in ("ProviderResponseError", "JSONDecodeError"):
        request = next((e for e in reversed(iterations.rows(path / "events.jsonl"))
                        if e.get("episode_id") == trial["trial_id"] and e.get("event") == "GENERATOR_END"), {})
        if kind == "JSONDecodeError" and "Unterminated string" in message or kind == "ProviderResponseError" and OpenAICompatibleProvider._retryable(ProviderResponseError(message, {}, request), request):
            return "PROVIDER_INTERRUPTED_RESPONSE"
    if kind == "VerifierTimeoutError":
        stdout = Path(trial["trial_dir"]) / "verifier/test-stdout.txt"
        output = stdout.read_text() if stdout.exists() else ""
        if "test session starts" in output:
            return None
        if any(s in output.lower() for s in ("downloading", "apt-get", "fetch", "failed to connect")):
            return "VERIFIER_DOWNLOAD_TIMEOUT"
    if kind == "EnvironmentStartTimeoutError":
        return kind
    if kind == "RuntimeError" and any(s in message for s in ("failed to fetch anonymous token", "connection refused", "502 Bad Gateway")):
        return "ENVIRONMENT_NETWORK"
    return None


def run_unit(root, config, unit, strategy, unavailable, recover_infrastructure=False):
    if unit["strategy_id"] in unavailable:
        return dict(unit, status="UNAVAILABLE_PROVIDER_EFFORT", cause=unavailable[unit["strategy_id"]])
    path = root / ".private/episodes" / unit["task_id"] / unit["strategy_id"] / str(unit["seed"])
    job = path / "jobs" / unit["unit_id"]
    observed = audit_job(job)
    state = path / "resume_state.json"
    if recover_infrastructure:
        reason = recovery_reason(path)
        if reason is None:
            return dict(unit, status="FINISHED", reused=True)
        saved = json.loads(state.read_text())
        episode = json.loads((path / "run_config.json").read_text())
        recovery = dict(saved["units"][-1], job_name=unit["unit_id"] + f"--infrastructure-recovery-{len(saved['units'])}",
                        environment_source_revision=config.get("environment_source_revision"), status="PENDING",
                        recovery_reason=reason, provider_retry_limit=100)
        saved["units"].append(recovery)
        saved.update(status="PENDING", updated_at=iterations.now())
        episode["units"].append(recovery)
        episode["environment_kwargs"].update(config.get("environment_kwargs", {}))
        iterations.write_atomic(path / "run_config.json", episode)
        iterations.write_atomic(state, saved)
        job = path / "jobs" / recovery["job_name"]
        observed = audit_job(job)
    if observed["status"] == "OFFICIAL_ARTIFACT_VERIFIED" or state.exists() and json.loads(state.read_text())["status"] in ("EVALUATED", "PARTIAL"):
        return dict(unit, status="FINISHED", reused=True)
    if not state.exists():
        v9 = deepcopy(config["v9_config"])
        v9.update(strategy.get("v9_config", {}))
        v9.update(teacher_enabled=strategy.get("teacher_enabled", False),
                  capability_snapshot=config["capability_snapshot"])
        actions = config["candidate_actions"]
        if strategy.get("model"):
            v9["fixed_model_id"] = strategy["model"]
            actions = [a for a in actions if a["model"] == strategy["model"] and a["native_effort"] == strategy["effort"]]
        elif strategy.get("effort"):
            actions = [a for a in actions if a["native_effort"] == strategy["effort"]]
        if strategy.get("checkpoint"):
            v9["router_checkpoint"] = {**strategy["checkpoint"], "socket_path": config["router_socket"]}
        runtime = json.loads((iterations.ROOT / "our-project/experiments/configs/benchmark_runtime.json").read_text())
        runtime.pop("dashboard_ssh", None)
        episode = {**runtime, "run_id": config["run_id"], "git_sha": config["source_revision"],
                   "dataset": "terminal-bench@2.0", "dataset_version": "2.0",
                   "dataset_git_sha": config["dataset_commit"], "task_source": str(iterations.ROOT / config["task_source"]),
                   "seed": unit["seed"], "agent": "modelrouter", "environment": "docker",
                   "model": "openai/gpt-6-luna", "max_steps": config["max_steps"],
                   "max_output_tokens": config["max_output_tokens"], "cost_limit": 0.0,
                   "harness_config": mini_configuration(config["max_steps"], 0.0),
                   "model_registry": config["model_registry"], "v9_config": v9,
                   "candidate_actions": actions, "policies": [unit["strategy_id"]],
                   "strategy_configs": {unit["strategy_id"]: {"policy": strategy["policy"]}},
                   "dashboard_output": str(path / "progress.json"),
                   "ledger_runs_root": str(path / "ledger-runs"), "ledger_root": str(path / "ledgers"),
                   "units": [{"task_id": unit["task_id"], "policy": unit["strategy_id"], "agent": "modelrouter",
                              "job_name": unit["unit_id"], "status": "PENDING", "pipeline_stage": "RQ1"}]}
        episode["environment_kwargs"].update(config.get("environment_kwargs", {}))
        iterations.start(path, episode)
    iterations.append(root / "jobs.jsonl", dict(unit, status="RUNNING", timestamp=iterations.now()))
    with (path / "batch.log").open("a") as output:
        result = subprocess.run([sys.executable, "-m", "modelrouter.benchmark", "resume", str(path)],
                                stdout=output, stderr=subprocess.STDOUT, env=dict(os.environ))
    observed = audit_job(job)
    mismatch = next((e for e in iterations.rows(path / "events.jsonl")
                     if e.get("native_effort_status") == "PROVIDER_REPORTED_MISMATCH"), None)
    return dict(unit, status="FINISHED" if observed["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else "UNKNOWN",
                exit_code=result.returncode, reward=[t.get("reward") for t in observed["trials"]],
                timestamp=iterations.now(), evidence_path=str(path),
                unsupported_effort=bool(strategy.get("model") and mismatch),
                returned_effort=mismatch.get("returned_native_effort") if mismatch else None)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Official Terminal-Bench 2.0 RQ1 batch")
    parser.add_argument("config", type=Path)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--stage", choices=("fixed", "router"), help="Execute one existing stage of the same comparison batch")
    parser.add_argument("--export-dir", type=Path, help="Public output directory")
    parser.add_argument("--watch-pids", type=int, nargs="+", help="Observe these existing batch processes without launching episodes")
    parser.add_argument("--watch-interval", type=int, default=1200, help="Seconds between batch snapshots; default 20 minutes")
    parser.add_argument("--recover-infrastructure", action="store_true", help="One separate attempt after a recorded technical fault; retain valid scores")
    parser.add_argument("--task", action="append", help="Select existing task IDs without changing the matrix")
    parser.add_argument("--strategy", action="append", help="Select existing strategy IDs without changing the matrix")
    parser.add_argument("--after-pids", type=int, nargs="+", help="Wait for existing batches before executing this batch")
    parser.add_argument("--then-config", type=Path, action="append", help="Continue with another saved batch after this one")
    args = parser.parse_args(argv)
    if args.after_pids:
        # Keep the same private memfd open across the preceding holder's natural exit.
        fd = os.open(os.environ["EXTERNAL_TEXT_MODEL_CONFIG"], os.O_RDONLY)
        os.environ["EXTERNAL_TEXT_MODEL_CONFIG"] = f"/proc/{os.getpid()}/fd/{fd}"
        async def await_batches():
            while any(Path(f"/proc/{pid}").exists() for pid in args.after_pids):
                await asyncio.sleep(20)
        asyncio.run(await_batches())
    root, config = prepare(args.config, args.source_revision)
    config["router_socket"] = str(iterations.ROOT / ".runtime" / (config["run_id"] + "-router.sock"))
    units = json.loads((root / "manifest.json").read_text())["units"]
    units = [u for u in units if (not args.task or u["task_id"] in args.task)
             and (not args.strategy or u["strategy_id"] in args.strategy)]
    from .rq1_analysis import export_batch_results
    if args.watch_pids:
        destination = args.export_dir or Path(tempfile.mkdtemp(prefix="rq1-watch-export.", dir=iterations.ROOT / ".runtime"))
        async def watch():
            while True:
                result = export_batch_results(root, config, destination)
                groups = [r for r in result["strategies"] if r["subset"] == "all"]
                live = [pid for pid in args.watch_pids if Path(f"/proc/{pid}").exists()]
                fields = ("tasks", "attempted", "harbor_trial_count", "reward_1", "reward_0", "no_official_reward", "running", "not_started")
                print(json.dumps({"observed_at": iterations.now(), "controllers_running": live,
                                  "export_dir": str(destination), "interval_sec": args.watch_interval,
                                  **{field: sum(r[field] for r in groups) for field in fields}}, ensure_ascii=False), flush=True)
                if not live:
                    return 0
                await asyncio.sleep(args.watch_interval)
        return asyncio.run(watch())
    if args.collect_only:
        export_batch_results(root, config, args.export_dir)
        return 0
    if args.recover_infrastructure:
        selected = []
        for unit in units:
            path = root / ".private/episodes" / unit["task_id"] / unit["strategy_id"] / str(unit["seed"])
            if not (path / "resume_state.json").exists():
                continue
            saved_units = json.loads((path / "resume_state.json").read_text())["units"]
            attempted_recovery = any(u.get("provider_retry_limit") == 100 for u in saved_units)
            if not attempted_recovery and recovery_reason(path):
                selected.append(unit)
        units = selected
    worker = None
    unavailable = {r["strategy_id"]: r["unit_id"] for r in iterations.rows(root / "jobs.jsonl") if r.get("unsupported_effort")}
    try:
        for stage in ([args.stage] if args.stage else ("fixed", "router")):
            strategies = [s for s in config["strategies"] if s["stage"] == stage]
            by_id = {s["id"]: s for s in strategies}
            pending = [u for u in units if u["strategy_id"] in by_id]
            if not pending:
                continue
            if stage == "router":
                socket_path = Path(config["router_socket"])
                socket_path.unlink(missing_ok=True)
                command = strategies[0]["checkpoint"]["command"] + ["--socket", str(socket_path)]
                worker = subprocess.Popen(command, stdout=subprocess.DEVNULL)
                # Readiness comes from the worker, not a model generation or a separate demo.
                import select
                while not socket_path.exists():
                    if worker.poll() is not None:
                        raise RuntimeError("Native Router worker exited before accepting requests")
                    select.select([], [], [], .1)
            with ThreadPoolExecutor(max_workers=config["concurrency"][stage]) as pool:
                futures = [pool.submit(run_unit, root, config, u, by_id[u["strategy_id"]], unavailable, args.recover_infrastructure) for u in pending]
                for future in as_completed(futures):
                    try:
                        record = future.result()
                    except Exception as exc:
                        unit = pending[futures.index(future)]
                        record = dict(unit, status="UNKNOWN", error_type=type(exc).__name__,
                                      error=str(exc), timestamp=iterations.now())
                    if record.get("unsupported_effort"):
                        unavailable[record["strategy_id"]] = record["unit_id"]
                    iterations.append(root / "jobs.jsonl", record)
                    print(json.dumps(record, ensure_ascii=False), flush=True)
                    if not record.get("reused"):
                        export_batch_results(root, config, args.export_dir)
    finally:
        if worker is not None:
            worker.terminate()
            worker.wait()
            Path(config["router_socket"]).unlink(missing_ok=True)
        export_batch_results(root, config, args.export_dir)
    for following in args.then_config or []:
        main([str(following), "--source-revision", args.source_revision,
              *(["--recover-infrastructure"] if args.recover_infrastructure else [])])
    return 0
