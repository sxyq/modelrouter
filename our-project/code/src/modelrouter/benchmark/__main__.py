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


_write_atomic = iterations.write_atomic



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
    planned = [(task["task_id"], policy, agent, subset.upper()) for task in tasks for policy in policies]
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
    p.add_argument("--agent", choices=["oracle", "modelrouter"], default="modelrouter")
    p.add_argument("--policies", default="fixed_strong,fixed_cheap,random,rule_sticky,joint_laya,joint_kev")
    p.add_argument("--model", help="Verified provider/model name; do not supply unverified aliases")
    p.add_argument("--v9-config", type=Path, help="Existing V9 JSON configuration for the routed mini agent")
    p.add_argument("--environment", choices=["docker", "daytona", "modal", "e2b"], default="docker")
    p.add_argument("--docker-host", help="Docker endpoint for this run; overrides runtime config")
    p.add_argument("--force-build", action="store_true", help="Build the task environment from its upstream Dockerfile")
    p.add_argument("--artifact", action="append", default=[], help="Environment path retained by Harbor after the trial")
    p.add_argument("--execute", action="store_true", help="Actually start a real Harbor task")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--iteration-dir", type=Path)
    p.add_argument("--source-revision", help="Deployed Git revision when the server source directory has no .git")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-steps", type=int, default=30)
    p.add_argument("--max-output-tokens", type=int, default=2048)
    p.add_argument("--cost-limit", type=float, default=0.0)
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
    for command in ("summarize", "export"):
        p = sub.add_parser(command, help="Compute results from original official trials")
        p.add_argument("job_dir", type=Path, nargs="?")
    args = parser.parse_args(argv)

    if args.command == "preflight":
        result = preflight(args.environment, args.docker_host)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "READY_FOR_ORACLE" else 2

    if args.command == "run":
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
        path = args.iteration_dir or iterations.ITERATIONS / iterations.iteration_name()
        path = path.resolve()
        if (path / "run_config.json").exists():
            print(f"Use resume {path} to retain this iteration's records", file=sys.stderr)
            return 2
        config = {"git_sha": args.source_revision or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=iterations.ROOT, text=True).strip(),
                  "dataset": "terminal-bench/terminal-bench-2-1", "dataset_version": manifest["version"],
                  "dataset_git_sha": manifest["upstream_commit"], "tasks": tasks, "subset": subset,
                  "task_source": str(iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks"),
                  "agent": args.agent, "mini_swe_version": "2.4.6", "harbor_version": "0.24.0",
                  "environment": args.environment, "model": args.model or "openai/gpt-6-luna",
                  "custom_agent": "modelrouter.benchmark.harbor_agent:ModelRouterMiniSweAgent" if args.agent == "modelrouter" else None, "policies": policies,
                  "seed": args.seed, "max_steps": args.max_steps, "max_output_tokens": args.max_output_tokens,
                  "cost_limit": args.cost_limit, "reasoning_effort": "low",
                  "units": units, "token_budget_path": str(iterations.ROOT / "experiments/agent_pilot/token_budget.json")}
        config.update(runtime)
        config["single_episode"] = args.single_episode
        config["force_build"] = args.force_build
        config["artifacts"] = args.artifact
        config["docker_host"] = _runtime_env(docker_host).get("DOCKER_HOST")
        os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "true"
        from modelrouter.providers.registry import ModelRegistry
        from .harbor_agent import mini_configuration, legal_actions
        from modelrouter.providers.registry import MODEL_REGISTRY
        config["model_registry"] = {k: asdict(v) for k, v in MODEL_REGISTRY.items()}
        config["harness_config"] = mini_configuration(args.max_steps, args.cost_limit)
        config["legal_actions"] = {policy: legal_actions() for policy in policies}
        config["credential_source"] = "EXTERNAL_TEXT_MODEL_CONFIG or ~/.agent-global/外部文本模型.local.json; secret values excluded"
        if args.v9_config is not None:
            from modelrouter.providers.registry import V9_MODEL_IDS
            from modelrouter.serving.schemas import LegalAction

            v9_config = json.loads(args.v9_config.read_text())
            config["strategy_configs"] = v9_config.pop("strategy_configs", {})
            v9_config["selection_scope"] = "MODEL_NATIVE_EFFORT"
            if "capability_snapshot" not in v9_config:
                from modelrouter.v9.capabilities.refresh import ensure_current, DEFAULT_MAX_AGE_SECONDS

                v9_config["capability_snapshot"] = ensure_current(
                    max_age_seconds=v9_config.get("capability_max_age_seconds", DEFAULT_MAX_AGE_SECONDS),
                    force=v9_config.get("capability_force_refresh", True))
            candidates = v9_config.get("candidate_actions")
            if candidates is None:
                candidate_actions = legal_actions(v9_config.get("formal_model_ids", V9_MODEL_IDS))
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


def run_iteration(path: Path, resume=False, docker_host: Optional[str] = None) -> int:
    config = json.loads((path / "run_config.json").read_text())
    state = json.loads((path / "resume_state.json").read_text())
    runtime = _runtime_config()
    docker_host = docker_host if docker_host is not None else config.get("docker_host", runtime.get("docker_host"))
    if not state["units"]:
        print("No pending benchmark units; retain this development iteration and its next plan")
        return 2
    env = _runtime_env(docker_host)
    env["MODELROUTER_ITERATION"] = str(path)
    env["LITELLM_LOCAL_MODEL_COST_MAP"] = "true"
    if config.get("router_endpoint"):
        env["ROUTER_SERVING_ENDPOINT"] = config["router_endpoint"]
    for unit in state["units"]:
        if unit["status"] == "EVALUATED" or (resume and unit["status"] == "NOT_EVALUATED"):
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
            custom = "modelrouter.benchmark.harbor_agent:ModelRouterMiniSweAgent" if unit["agent"] == "modelrouter" else None
            task_source = config.get("task_source") or str(iterations.ROOT / "external/benchmarks/terminal-bench-2-1/tasks")
            cmd = build_harbor_command(unit["task_id"], unit["agent"], None if unit["agent"] == "oracle" else config["model"], config.get("environment_import_path", config["environment"]), custom, task_source)
            cmd += ["--jobs-dir", str(path / "jobs"), "--job-name", unit["job_name"], "--max-retries", "0"]
            for artifact in config.get("artifacts", []):
                cmd += ["--artifact", artifact]
            if config.get("force_build"):
                cmd += ["--force-build"]
            if custom:
                strategy = config.get("strategy_configs", {}).get(unit["policy"], {})
                for key, value in {"policy": strategy.get("policy", unit["policy"]), "seed": config["seed"], "max_steps": config["max_steps"], "max_output_tokens": config["max_output_tokens"], "cost_limit": config.get("cost_limit", 0.0)}.items():
                    cmd += ["--agent-kwarg", f"{key}={value}"]
                if "v9_config" in config:
                    for key in ("v9_config", "candidate_actions"):
                        value = {**config[key], **strategy.get(key, {})} if key == "v9_config" else config[key]
                        if key == "v9_config":
                            value["capability_snapshot"] = config[key]["capability_snapshot"]
                        cmd += ["--agent-kwarg", f"{key}={json.dumps(value)}"]
            for key, value in config.get("environment_kwargs", {}).items():
                cmd += ["--environment-kwarg", f"{key}={json.dumps(value)}"]
        unit["status"] = "RUNNING"
        state.update(status="RUNNING", updated_at=iterations.now())
        iterations.write_atomic(path / "resume_state.json", state)
        iterations.event(path, "JOB_START", **unit)
        try:
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
            continue
    iterations.write_atomic(path / "resume_state.json", state)
    complete = all(unit["status"] == "EVALUATED" for unit in state["units"])
    iterations.finish(path, "EVALUATED" if complete else "PARTIAL")
    return 0 if complete else 2


if __name__ == "__main__":
    sys.exit(main())
