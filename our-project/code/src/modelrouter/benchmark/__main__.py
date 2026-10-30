"""CPU-only official benchmark preflight, artifact audit, and live trial progress.

Example: python -m modelrouter.benchmark preflight
         python -m modelrouter.benchmark audit ~/.cache/harbor/jobs/job-X
         python -m modelrouter.benchmark watch ~/.cache/harbor/jobs/job-X --once
Actual benchmark tasks are launched with the INSTALLED harbor CLI, not faked here.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from contextlib import nullcontext
from dataclasses import asdict
from importlib.metadata import version
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from .official_artifacts import audit_job
from . import iterations


def _runtime_config() -> dict:
    return json.loads((iterations.ROOT / "our-project/experiments/configs/benchmark_runtime.json").read_text())


def _runtime_env(docker_host: Optional[str] = None) -> dict:
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    if docker_host is not None:
        env["DOCKER_HOST"] = docker_host
    return env


def _docker_socket_problem(env: dict) -> Optional[dict]:
    docker_host = env.get("DOCKER_HOST", "")
    if docker_host.startswith("unix://"):
        socket_path = Path(docker_host.removeprefix("unix://"))
        if not socket_path.exists():
            return {"status": "BLOCKED", "reason": f"Docker socket missing: {socket_path}"}


def _probe(cmd: list[str], timeout: float = 6, *, env: Optional[dict] = None) -> dict:
    env = _runtime_env() if env is None else env
    socket_problem = _docker_socket_problem(env) if cmd[0] == "docker" else None
    if socket_problem:
        return socket_problem
    resolved = shutil.which(cmd[0], path=env.get("PATH", ""))
    if not resolved:
        return {"status": "MISSING", "reason": cmd[0] + " not found"}
    cmd = [resolved, *cmd[1:]]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLOCKED", "reason": type(exc).__name__}
    details = (result.stdout or result.stderr or "").strip().splitlines()
    return {
        "status": "READY" if result.returncode == 0 else "BLOCKED",
        "reason": details[0][:160] if details else "exit " + str(result.returncode),
    }


def preflight(environment: str = "docker", docker_host: Optional[str] = None) -> dict:
    """Local checks; never reads or prints the API key."""
    docker_host = docker_host if docker_host is not None else _runtime_config().get("docker_host")
    env = _runtime_env(docker_host)
    harbor = _probe(["harbor", "--version"], env=env)
    sandbox = _probe(["docker", "info"], env=env) if environment == "docker" else {
        "status": "NOT_CHECKED",
        "reason": "Check authorized cloud provider environment independently",
    }
    from minisweagent.agents.default import DefaultAgent
    from harbor.agents.installed.mini_swe_agent import MiniSweAgent
    from harbor.models.task.task import Task

    task_root = iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks"
    task = Task(task_root / "fix-git")
    evidence_dir = iterations.ITERATIONS / "20261019-v10-integration"
    evidence = {}
    for name in ("provider_evidence.json", "router_evidence.json", "harbor_evidence.json"):
        path = evidence_dir / name
        if path.exists():
            recorded = json.loads(path.read_text())
            evidence[name] = {"status": recorded["status"], "path": str(path),
                              "scope": "Previously recorded evidence; no new paid request"}
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": "terminal-bench/terminal-bench-2-1",
        "agent_recommended": "mini-swe-agent",
        "environment": environment,
        "docker_host": env.get("DOCKER_HOST"),
        "harbor": harbor,
        "sandbox": sandbox,
        "mini_swe_agent": {"version": version("mini-swe-agent"),
                           "agent_class": DefaultAgent.__module__ + ".DefaultAgent",
                           "harbor_class": MiniSweAgent.__module__ + ".MiniSweAgent"},
        "dataset": {"id": "terminal-bench/terminal-bench-2-1", "local_source": str(task_root),
                    "loaded_task": task.name, "version": "2.1",
                    "task_count": 89, "scope": "local upstream task parsing, not sandbox execution"},
        "existing_evidence": evidence,
        "status": "READY_FOR_ORACLE" if harbor["status"] == "READY" and sandbox["status"] == "READY"
                  else "BLOCKED_OR_UNVERIFIED",
        "official_trials": 0,
    }


def progress(job_dir: Path) -> dict:
    result = audit_job(job_dir)
    trials = result["trials"]
    verified = [r for r in trials if r["status"] == "OFFICIAL_ARTIFACT_VERIFIED"]
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_dir": str(job_dir),
        "status": result["status"],
        "observed_trials": len(trials),
        "verified_trials": len(verified),
        "verified_reward_sum": sum(float(x["reward"]) for x in verified),
        "verified_reward_mean": (
            sum(float(x["reward"]) for x in verified) / len(verified) if verified else None
        ),
        "remaining_unverified": len(trials) - len(verified),
        "counts": result["counts"],
        "missing_job_files": result["missing_job_files"],
    }


def _write_atomic(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)



def build_harbor_command(
    task: str,
    agent: str = "oracle",
    model: Optional[str] = None,
    environment: str = "docker",
    custom_agent: Optional[str] = None,
    task_source: Optional[str] = None,
) -> list[str]:
    """Build a one-task command for the real upstream Harbor CLI; never a mock."""
    if not task or any(ch.isspace() for ch in task):
        raise ValueError("A single verified task identifier is required")
    if agent != "oracle" and not model and not custom_agent:
        raise ValueError("A verified provider/model ID is required for non-oracle agent")
    cmd = [
        "harbor", "run",
        *(["-p", str(Path(task_source) / task)] if task_source else ["-d", "terminal-bench/terminal-bench-2-1"]),
        "--include-task-name", task,
        "-n", "1", "-k", "1",
        "--env", environment,
    ]
    if custom_agent:
        cmd.extend(["-a", custom_agent])
    else:
        cmd.extend(["-a", agent])
    if model:
        cmd.extend(["-m", model])
    return cmd


def _task_in_subset(task: str, subset: str) -> bool:
    """Require exact IDs from our frozen 8/24/57 project-owned manifest."""
    p = Path(__file__).resolve().parents[5] / "router_data" / "terminal_bench_manifest.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        subset_key = {"canary": "canary", "dev": "external_dev", "sealed": "final_test"}[subset]
        records = data["subsets"][subset_key]["tasks"]
    except (OSError, ValueError, KeyError):
        return False
    return task in {row["task_id"] for row in records if isinstance(row, dict) and "task_id" in row}


def execution_units(tasks, policies, agent, seed, manifest, subset, *, single_episode=False):
    if single_episode and (len(tasks) != 1 or len(policies) != 1 or not policies[0].strip()):
        raise ValueError("Single Episode planning requires exactly one task and one policy")
    planned = []
    if not single_episode and agent != "oracle":
        planned.append(("fix-git", "oracle", "oracle", "ORACLE_SINGLE"))
    if not single_episode and agent == "modelrouter":
        planned.extend([("fix-git", "mini-swe-agent", "mini-swe-agent", "NATIVE_SINGLE"),
                        ("fix-git", "fixed_strong", "modelrouter", "ROUTED_SINGLE")])
        if subset == "dev":
            for task in manifest["subsets"]["canary"]["tasks"]:
                planned.extend((task["task_id"], policy, agent, "CANARY") for policy in policies)
    planned.extend((task["task_id"], policy, agent, subset.upper()) for task in tasks for policy in policies)
    unique = {}
    for task, policy, harness, stage in planned:
        name = f"{task}--{policy}--s{seed}"
        if name not in unique:
            unique[name] = {"task_id": task, "policy": policy, "agent": harness,
                            "job_name": name, "status": "PENDING", "pipeline_stage": stage}
    return list(unique.values())

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="ModelRouter official Harbor evidence CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("preflight", help="Check Harbor and Docker, with no API calls")
    p.add_argument("--environment", choices=["docker", "daytona", "modal", "e2b"], default="docker")
    p.add_argument("--docker-host", help="Docker endpoint for this command; overrides runtime config without changing the shell")
    p = sub.add_parser("run", help="Run official Harbor tasks and record an experiment iteration")
    p.add_argument("--task")
    p.add_argument("--single-episode", action="store_true",
                   help="Plan only the explicit --task and one --policies value; no added baselines or canary")
    p.add_argument("--canary", action="store_true")
    p.add_argument("--dev", action="store_true")
    p.add_argument("--subset", choices=["canary", "dev", "sealed"], default="canary")
    p.add_argument("--agent", choices=["oracle", "mini-swe-agent", "modelrouter"], default="modelrouter")
    p.add_argument("--policies", default="fixed_strong,fixed_cheap,random,rule_sticky,routellm,sr_knn,laya_v2,kev_4b,joint_laya,joint_kev")
    p.add_argument("--custom-agent", help="Official Harbor import path; requires installed adapter")
    p.add_argument("--model", help="Verified provider/model name; do not supply unverified aliases")
    p.add_argument("--v9-config", type=Path, help="Existing V9 JSON configuration for the routed mini agent")
    p.add_argument("--environment", choices=["docker", "daytona", "modal", "e2b"], default="docker")
    p.add_argument("--docker-host", help="Docker endpoint for this run; overrides runtime config")
    p.add_argument("--execute", action="store_true", help="Actually start a real Harbor task")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--iteration-dir", type=Path)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-steps", type=int, default=30)
    p.add_argument("--max-output-tokens", type=int, default=2048)
    p.add_argument("--cost-limit", type=float, default=3.0)
    p.add_argument("--allow-sealed", action="store_true", help="Explicitly acknowledge sealed-test run authorization")
    p = sub.add_parser("resume", help="Continue the saved iteration without rerunning completed trials")
    p.add_argument("job_dir", type=Path, nargs="?")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--docker-host", help="Docker endpoint for this resume; leaves the saved endpoint unchanged")
    p = sub.add_parser("audit", help="Verify original job/trial/lock/verifier artifacts")
    p.add_argument("job_dir", type=Path)
    p.add_argument("--output", type=Path)
    p = sub.add_parser("watch", help="Report verified trial progress in the terminal")
    p.add_argument("job_dir", type=Path, nargs="?")
    p.add_argument("--once", action="store_true")
    p.add_argument("--interval", type=float, default=10.0)
    p.add_argument("--output", type=Path, help="Optional progress JSON file for the dashboard")
    p = sub.add_parser("alias-smoke", help="Run the original mini agent in a local development workspace")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--instruction-file", type=Path, required=True)
    p.add_argument("--verify-command", required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--policy", choices=["laya_v2", "kev_4b"], default="laya_v2")
    p.add_argument("--iteration-dir", type=Path)
    p.add_argument("--max-steps", type=int, default=15)
    p.add_argument("--max-output-tokens", type=int, default=4096)
    for command in ("summarize", "export"):
        p = sub.add_parser(command, help="Compute results from original official trials")
        p.add_argument("job_dir", type=Path, nargs="?")
    args = parser.parse_args(argv)

    if args.command == "alias-smoke":
        from modelrouter.v9.runtime.development import run_development
        result = run_development(
            workspace=args.workspace, instruction=args.instruction_file.read_text(),
            verify_command=args.verify_command, config=json.loads(args.config.read_text()),
            record_dir=args.iteration_dir or iterations.ITERATIONS / iterations.iteration_name(),
            task_id=args.task_id, policy=args.policy, max_steps=args.max_steps,
            max_output_tokens=args.max_output_tokens,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "RUNTIME_VERIFIED" else 2

    if args.command == "preflight":
        result = preflight(args.environment, args.docker_host)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "READY_FOR_ORACLE" else 2

    if args.command == "run":
        if args.subset == "sealed" and not args.allow_sealed:
            print("BLOCKED: sealed tasks need explicit separate authorization", file=sys.stderr)
            return 2
        subset = "dev" if args.dev else args.subset
        manifest = json.loads((iterations.ROOT / "router_data/terminal_bench_manifest.json").read_text())
        key = {"canary": "canary", "dev": "external_dev", "sealed": "final_test"}[subset]
        tasks = manifest["subsets"][key]["tasks"]
        if args.task:
            tasks = [t for t in tasks if t["task_id"] == args.task]
        if not tasks or not (args.task or args.canary or args.dev):
            print("Provide --task from the project split, --canary or --dev", file=sys.stderr)
            return 2
        policies = args.policies.split(",") if args.agent == "modelrouter" else [args.agent]
        if args.single_episode and (not args.task or args.canary or args.dev):
            parser.error("--single-episode requires --task without --canary or --dev; use --subset to select its split")
        try:
            units = execution_units(tasks, policies, args.agent, args.seed, manifest, subset,
                                    single_episode=args.single_episode)
        except ValueError as exc:
            parser.error(str(exc))
        runtime = _runtime_config()
        docker_host = args.docker_host if args.docker_host is not None else runtime.get("docker_host")
        previous = iterations.latest()
        if previous and (previous / "next_iteration.json").exists():
            plan = json.loads((previous / "next_iteration.json").read_text())
            resolution = resolve_previous_failure(plan, args.environment, docker_host,
                                                  runtime.get("reported_resolution"))
            if not args.dry_run and resolution["status"] == "UNRESOLVED":
                iterations.event(previous, "PREVIOUS_PROBLEM_ASSESSED", **resolution)
                print(json.dumps({"status": "BLOCKED", "previous_iteration": str(previous),
                                  "next_command": plan.get("next_command"), **resolution}, ensure_ascii=False))
                return 2
        path = args.iteration_dir or iterations.ITERATIONS / iterations.iteration_name()
        path = path.resolve()
        if (path / "run_config.json").exists():
            print(f"Use resume {path} to retain this iteration's records", file=sys.stderr)
            return 2
        config = {"git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=iterations.ROOT, text=True).strip(),
                  "dataset": "terminal-bench/terminal-bench-2-1", "dataset_version": manifest["version"],
                  "dataset_git_sha": manifest["upstream_commit"], "tasks": tasks, "subset": subset,
                  "task_source": str(iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks"),
                  "agent": args.agent, "mini_swe_version": "2.4.6", "harbor_version": "0.24.0",
                  "environment": args.environment, "model": args.model or "openai/gpt-6-luna",
                  "custom_agent": args.custom_agent, "policies": policies,
                  "seed": args.seed, "max_steps": args.max_steps, "max_output_tokens": args.max_output_tokens,
                  "cost_limit": args.cost_limit, "reasoning_effort": "low",
                  "units": units, "token_budget_path": str(iterations.ROOT / "experiments/agent_pilot/token_budget.json")}
        config.update(runtime)
        config["single_episode"] = args.single_episode
        config["docker_host"] = _runtime_env(docker_host).get("DOCKER_HOST")
        from modelrouter.providers.registry import ModelRegistry
        from .harbor_agent import mini_configuration, legal_actions
        from modelrouter.providers.registry import MODEL_REGISTRY
        config["model_registry"] = {k: asdict(v) for k, v in MODEL_REGISTRY.items()}
        config["experiment_model_registry"] = json.loads((iterations.ROOT / "our-project/experiments/configs/model_registry.json").read_text())
        config["harness_config"] = mini_configuration(args.max_steps, args.cost_limit)
        config["legal_actions"] = {policy: legal_actions(policy.startswith("joint_")) for policy in policies}
        config["credential_source"] = "experiments/agent_pilot/configs/generator_credentials.json; secret values excluded"
        if args.v9_config is not None:
            from modelrouter.providers.registry import V9_MODEL_IDS
            from modelrouter.serving.schemas import LegalAction

            v9_config = json.loads(args.v9_config.read_text())
            candidates = v9_config.get("candidate_actions")
            if candidates is None:
                registry = ModelRegistry()
                candidate_actions = [LegalAction(provider=registry.get_spec(model).provider, model=model,
                                                 native_effort="none").model_dump() for model in V9_MODEL_IDS]
            else:
                candidate_actions = [LegalAction.model_validate(action).model_dump() for action in candidates]
            config.update(v9_config=v9_config, candidate_actions=candidate_actions,
                          v9_config_source=str(args.v9_config.resolve()))
            config["legal_actions"] = {policy: candidate_actions for policy in policies}
        if args.dry_run:
            print(json.dumps({"status": "DRY_RUN", **config}, ensure_ascii=False, indent=2))
            return 0
        iterations.start(path, config)
        return run_iteration(path)

    if args.command == "resume":
        args.job_dir = args.job_dir or iterations.latest()
        if args.job_dir is None:
            print("No saved iteration")
            return 2
        if (args.job_dir / "resume_state.json").exists():
            plan = json.loads((args.job_dir / "next_iteration.json").read_text()) if (args.job_dir / "next_iteration.json").exists() else {}
            iterations.event(args.job_dir, "RESUME_PLAN_READ", plan=plan)
            if args.dry_run:
                print(json.dumps(plan, ensure_ascii=False, indent=2))
                return 0
            return run_iteration(args.job_dir, resume=True, docker_host=args.docker_host)
        cmd = ["harbor", "jobs", "resume", "--job-path", str(args.job_dir)]
        print(json.dumps({"status": "DRY_RUN" if args.dry_run else "RESUMING_REAL_HARBOR",
                          "argv": cmd}, ensure_ascii=False), flush=True)
        if args.dry_run:
            return 0
        if not args.job_dir.is_dir() or not (args.job_dir / "config.json").is_file():
            print("BLOCKED: original Harbor job config missing", file=sys.stderr)
            return 2
        docker_host = args.docker_host if args.docker_host is not None else _runtime_config().get("docker_host")
        return subprocess.call(cmd, env=_runtime_env(docker_host))

    if args.command in ("summarize", "export"):
        path = args.job_dir or iterations.latest()
        if path is None:
            print("No saved iteration")
            return 2
        metrics = iterations.summarize(path)
        if args.command == "export":
            from .rq1_analysis import export_official_results
            export_official_results(path)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        return 0

    if args.command == "audit":
        result = audit_job(args.job_dir)
        if args.output:
            _write_atomic(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else 2

    if not 5 <= args.interval <= 15:
        parser.error("--interval must be between 5 and 15 seconds")
    try:
        while True:
            args.job_dir = args.job_dir or iterations.latest()
            if args.job_dir is None:
                print("No saved iteration")
                return 2
            if (args.job_dir / "resume_state.json").exists():
                result = iterations.publish(args.job_dir, args.output or iterations.DASHBOARD)
                if args.once or result["status"] != "RUNNING":
                    return 0 if result["status"] == "EVALUATED" else 2
                time.sleep(args.interval)
                continue
            result = progress(args.job_dir)
            if args.output:
                _write_atomic(args.output, result)
            print(
                "{time} | {status} | official {done}/{total} | mean reward {reward}".format(
                    time=result["timestamp"],
                    status=result["status"],
                    done=result["verified_trials"],
                    total=result["observed_trials"],
                    reward=("N/A" if result["verified_reward_mean"] is None
                            else "{:.4f}".format(result["verified_reward_mean"])),
                ),
                flush=True,
            )
            if args.once:
                return 0 if result["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else 2
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 130


def resolve_previous_failure(plan, environment, docker_host=None, reported_resolution=None):
    reason = plan.get("reason", "")
    if plan.get("status") != "BLOCKED":
        return {"status": "NO_REPEATED_FAILURE", "problem": reason}
    if any(term in reason.lower() for term in ("docker", "rootless", "newuidmap", "newgidmap", "uid_map")):
        sandbox = _probe(["docker", "info"], env=_runtime_env(docker_host)) if environment == "docker" else {
            "status": "NOT_CHECKED", "reason": "Saved Docker run cannot resume in a different environment"}
        return {"status": "RESOLVED" if sandbox["status"] == "READY" else "UNRESOLVED",
                "problem": reason, "sandbox": sandbox}
    report = reported_resolution if reported_resolution is not None else plan.get("reported_resolution")
    if (isinstance(report, dict) and report.get("status") == "RESOLVED"
            and report.get("problem") == reason and report.get("evidence")):
        return {"status": "RESOLVED", "problem": reason,
                "resolution_source": "reported_resolution", "evidence": report["evidence"]}
    return {"status": "UNRESOLVED", "problem": reason,
            "action": "Retain the original job; provide reported_resolution with matching problem, RESOLVED status and evidence"}


def run_iteration(path: Path, resume=False, docker_host: Optional[str] = None) -> int:
    config = json.loads((path / "run_config.json").read_text())
    state = json.loads((path / "resume_state.json").read_text())
    runtime = _runtime_config()
    docker_host = docker_host if docker_host is not None else config.get("docker_host", runtime.get("docker_host"))
    if resume and state["status"] == "BLOCKED":
        plan = json.loads((path / "next_iteration.json").read_text())
        resolution = resolve_previous_failure(plan, config.get("environment", "docker"), docker_host,
                                              config.get("reported_resolution", runtime.get("reported_resolution")))
        iterations.event(path, "PREVIOUS_PROBLEM_ASSESSED", **resolution)
        if resolution["status"] == "UNRESOLVED":
            print(json.dumps(resolution, ensure_ascii=False), flush=True)
            return 2
    if not state["units"]:
        print("No pending benchmark units; retain this development iteration and its next plan")
        return 2
    env = _runtime_env(docker_host)
    env["MODELROUTER_ITERATION"] = str(path)
    env["MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT"] = "1"
    env["LITELLM_LOCAL_MODEL_COST_MAP"] = "true"
    if config.get("router_endpoint"):
        env["ROUTER_SERVING_ENDPOINT"] = config["router_endpoint"]
    for unit in state["units"]:
        if unit["status"] == "EVALUATED":
            continue
        job_path = path / "jobs" / unit["job_name"]
        prior = audit_job(job_path)
        if prior["status"] == "OFFICIAL_ARTIFACT_VERIFIED":
            unit["status"] = "EVALUATED"
            continue
        socket_problem = _docker_socket_problem(env) if config["environment"] == "docker" else None
        if socket_problem:
            unit["status"] = "BLOCKED"
            iterations.write_atomic(path / "resume_state.json", state)
            iterations.event(path, "ERROR", category="DOCKER", error=socket_problem["reason"],
                             docker_host=env.get("DOCKER_HOST"))
            iterations.finish(path, "BLOCKED", socket_problem["reason"])
            return 2
        if resume and (job_path / "config.json").exists():
            cmd = ["harbor", "jobs", "resume", "--job-path", str(job_path)]
        else:
            custom = config.get("custom_agent")
            if unit["agent"] == "modelrouter":
                custom = custom or "modelrouter.benchmark.harbor_agent:ModelRouterMiniSweAgent"
            task_source = config.get("task_source") or str(iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks")
            cmd = build_harbor_command(unit["task_id"], unit["agent"], None if unit["agent"] == "oracle" else config["model"], config["environment"], custom, task_source)
            cmd += ["--jobs-dir", str(path / "jobs"), "--job-name", unit["job_name"], "--max-retries", "0"]
            if custom:
                for key, value in {"policy": unit["policy"], "seed": config["seed"], "max_steps": config["max_steps"], "max_output_tokens": config["max_output_tokens"], "cost_limit": config.get("cost_limit", 3.0)}.items():
                    cmd += ["--agent-kwarg", f"{key}={value}"]
                if "v9_config" in config:
                    for key in ("v9_config", "candidate_actions"):
                        cmd += ["--agent-kwarg", f"{key}={json.dumps(config[key])}"]
            elif unit["agent"] == "mini-swe-agent":
                from .harbor_agent import mini_configuration
                from modelrouter.providers.registry import ModelRegistry
                spec = ModelRegistry().get_spec(config["model"].removeprefix("openai/"))
                pricing = {config["model"]: {"input_cost_per_token": spec.input_price_per_1m / 1e6,
                           "output_cost_per_token": spec.output_price_per_1m / 1e6,
                           "cache_read_input_token_cost": spec.cache_read_price_per_1m / 1e6,
                           "supports_reasoning": True, "supports_function_calling": True,
                           "litellm_provider": "openai", "mode": "chat"}}
                cmd += ["--agent-kwarg", "version=2.4.6", "--agent-env", "MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT=1",
                        "--agent-kwarg", "reasoning_effort=low",
                        "--agent-kwarg", f"max_tokens={config['max_output_tokens']}",
                        "--agent-kwarg", f"cost_limit={config.get('cost_limit', 3.0)}",
                        "--agent-kwarg", "config=" + json.dumps(mini_configuration(config["max_steps"], config.get("cost_limit", 3.0))),
                        "--agent-kwarg", "litellm_model_registry=" + json.dumps(pricing)]
        unit["status"] = "RUNNING"
        state.update(status="RUNNING", updated_at=iterations.now())
        iterations.write_atomic(path / "resume_state.json", state)
        iterations.event(path, "JOB_START", **unit)
        try:
            from modelrouter.providers.provider import native_generator_relay
            relay_context = native_generator_relay(path) if unit["agent"] == "mini-swe-agent" else nullcontext()
            with relay_context as relay:
                if relay:
                    relay_host = config.get("native_relay_host", "host.docker.internal")
                    env["MODELROUTER_NATIVE_RELAY_KEY"] = relay["api_key"]
                    relay_url = f"http://{relay_host}:{relay['port']}/v1"
                    if cmd[1:3] == ["jobs", "resume"]:
                        saved = json.loads((job_path / "config.json").read_text())
                        for agent_config in saved["agents"]:
                            agent_config.update(model_base_url=relay_url,
                                                model_api_key_name="MODELROUTER_NATIVE_RELAY_KEY",
                                                model_api_format="openai_chat_completions")
                        iterations.write_atomic(job_path / "config.json", saved)
                        iterations.event(path, "NATIVE_RELAY_RECONNECTED", job_name=unit["job_name"], port=relay["port"])
                    else:
                        cmd += ["--base-url", relay_url, "--api-key-name", "MODELROUTER_NATIVE_RELAY_KEY",
                                "--api-format", "openai_chat_completions"]
                code = iterations.execute(path, cmd, env=env, label=unit["job_name"])
        except KeyboardInterrupt:
            unit["status"] = "INTERRUPTED"
            iterations.write_atomic(path / "resume_state.json", state)
            iterations.finish(path, "INTERRUPTED", "Terminal interrupted; retain the original Harbor job for resume")
            return 130
        except OSError as exc:
            iterations.event(path, "ERROR", category="RUNTIME", error=str(exc))
            unit["status"] = "BLOCKED"
            iterations.write_atomic(path / "resume_state.json", state)
            iterations.finish(path, "BLOCKED", str(exc))
            return 2
        result = audit_job(job_path)
        unit["status"] = "EVALUATED" if result["status"] == "OFFICIAL_ARTIFACT_VERIFIED" else "NOT_EVALUATED"
        unit["exit_code"] = code
        iterations.write_atomic(path / "resume_state.json", state)
        iterations.event(path, "JOB_END", **unit)
        if unit["status"] != "EVALUATED":
            reason = f"Harbor exit={code}; official verifier result absent in {job_path}"
            logs = sorted((path / "commands").glob(unit["job_name"] + "-*.log"))
            if logs:
                output = logs[-1].read_text()
                if "Docker is not installed" in output:
                    reason += "; Docker is not installed or not on PATH"
                elif "permission denied" in output.lower() and "docker" in output.lower():
                    reason += "; Docker socket permission denied"
            iterations.event(path, "ERROR", category="HARBOR", error=reason)
            iterations.finish(path, "BLOCKED", reason)
            return 2
    iterations.write_atomic(path / "resume_state.json", state)
    iterations.finish(path, "EVALUATED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
