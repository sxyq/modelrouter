"""Batch the existing official Harbor runner; retain one independent episode per unit."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from dataclasses import asdict
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

from . import iterations
from .harbor_agent import legal_actions, mini_configuration
from .official_artifacts import audit_job
from modelrouter.providers.registry import MODEL_REGISTRY, V9_MODEL_IDS
from modelrouter.v9.capabilities.features import load_current


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
        definition = tomllib.loads((source / task["path"] / "task.toml").read_text())
        exposed = task["name"] in config["historically_exposed_tasks"]
        tasks.append({"task_id": task["name"], "path": task["path"],
                      "git_url": task["git_url"], "git_commit_id": task["git_commit_id"],
                      "original_subset": subsets[task["name"]], "historically_exposed": exposed,
                      "used_for_current_training": task["name"] in config["current_training_tasks"],
                      "used_for_model_selection": task["name"] in config["model_selection_tasks"],
                      "environment": definition["environment"], "agent": definition["agent"],
                      "verifier": definition["verifier"]})
    tasks.sort(key=lambda t: (t["agent"]["timeout_sec"], t["task_id"]))
    config.update(source_revision=revision, started_at=iterations.now(), tasks=tasks,
                  capability_snapshot=load_current(),
                  harbor_version=version("harbor"), mini_swe_version=version("mini-swe-agent"),
                  model_registry={k: asdict(MODEL_REGISTRY[k]) for k in V9_MODEL_IDS},
                  candidate_actions=legal_actions(V9_MODEL_IDS))
    units = [{"task_id": t["task_id"], "strategy_id": s["id"], "seed": seed,
              "unit_id": f"{t['task_id']}--{s['id']}--s{seed}", "status": "PENDING"}
             for t in tasks for s in config["strategies"] for seed in config["seeds"]]
    iterations.write_atomic(root / "config.json", config)
    iterations.write_atomic(root / "manifest.json", {
        "run_id": config["run_id"], "benchmark_name": "Terminal-Bench", "benchmark_version": "2.0",
        "source_revision": revision, "dataset": dataset, "tasks": tasks, "units": units,
        "protocol": {k: config[k] for k in ("max_steps", "max_output_tokens", "resources", "seeds")},
        "checkpoint_selection": "PREDECLARED_GLM_POOL_REPRESENTATIVES_NOT_PROVEN_STRONGEST",
        "capability_snapshot_id": config["capability_snapshot"]["snapshot_id"]})
    return root, config


def run_unit(root, config, unit, strategy, unavailable):
    if unit["strategy_id"] in unavailable:
        return dict(unit, status="UNAVAILABLE_PROVIDER_EFFORT", cause=unavailable[unit["strategy_id"]])
    path = root / ".private/episodes" / unit["task_id"] / unit["strategy_id"] / str(unit["seed"])
    job = path / "jobs" / unit["unit_id"]
    observed = audit_job(job)
    state = path / "resume_state.json"
    if observed["status"] == "OFFICIAL_ARTIFACT_VERIFIED" or state.exists() and json.loads(state.read_text())["status"] in ("EVALUATED", "PARTIAL"):
        return dict(unit, status="FINISHED", reused=True)
    if not state.exists():
        v9 = deepcopy(config["v9_config"])
        v9.update(teacher_enabled=strategy.get("teacher_enabled", False),
                  capability_snapshot=config["capability_snapshot"])
        actions = config["candidate_actions"]
        if strategy.get("model"):
            v9["fixed_model_id"] = strategy["model"]
            actions = [a for a in actions if a["model"] == strategy["model"] and a["native_effort"] == strategy["effort"]]
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
    args = parser.parse_args(argv)
    root, config = prepare(args.config, args.source_revision)
    config["router_socket"] = str(iterations.ROOT / ".runtime" / (config["run_id"] + "-router.sock"))
    units = json.loads((root / "manifest.json").read_text())["units"]
    from .rq1_analysis import export_batch_results
    if args.collect_only:
        export_batch_results(root, config)
        return 0
    worker = None
    unavailable = {r["strategy_id"]: r["unit_id"] for r in iterations.rows(root / "jobs.jsonl") if r.get("unsupported_effort")}
    try:
        for stage in ("fixed", "router"):
            strategies = [s for s in config["strategies"] if s["stage"] == stage]
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
            by_id = {s["id"]: s for s in strategies}
            pending = [u for u in units if u["strategy_id"] in by_id]
            with ThreadPoolExecutor(max_workers=config["concurrency"][stage]) as pool:
                futures = [pool.submit(run_unit, root, config, u, by_id[u["strategy_id"]], unavailable) for u in pending]
                for future in as_completed(futures):
                    record = future.result()
                    if record.get("unsupported_effort"):
                        unavailable[record["strategy_id"]] = record["unit_id"]
                    iterations.append(root / "jobs.jsonl", record)
                    print(json.dumps(record, ensure_ascii=False), flush=True)
                    export_batch_results(root, config)
    finally:
        if worker is not None:
            worker.terminate()
            worker.wait()
            Path(config["router_socket"]).unlink(missing_ok=True)
        export_batch_results(root, config)
    return 0
