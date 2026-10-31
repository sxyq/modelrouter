"""Experiment records, live progress and restart state for the benchmark CLI."""
from __future__ import annotations

import json
import math
import os
import queue
import subprocess
import threading
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .official_artifacts import audit_job
from modelrouter.providers.registry import ModelRegistry
from modelrouter.telemetry.ledger import ExperimentLedger

ROOT = Path(__file__).resolve().parents[5]
ITERATIONS = ROOT / "our-project/results/iterations"
DASHBOARD = ROOT / "our-project/dashboard/agent_benchmark_status.json"
_write_lock = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


def iteration_name():
    return datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y%m%d-%H%M%S")


def write_atomic(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False, encoding="utf-8") as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        tmp = Path(stream.name)
    tmp.replace(path)


def append(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock, path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(data, ensure_ascii=False) + "\n")


def rows(path: Path):
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            # A writer may still be finishing the last JSONL line.
            continue
    return result


def latest(root: Path = ITERATIONS):
    paths = sorted(root.glob("*/run_config.json"), key=lambda p: p.stat().st_mtime)
    return paths[-1].parent if paths else None


def start(path: Path, config: dict):
    previous = latest(path.parent)
    prior_plan = None
    if previous and (previous / "next_iteration.json").exists():
        prior_plan = json.loads((previous / "next_iteration.json").read_text())
    config = dict(config, iteration_id=path.name, started_at=now(),
                  previous_iteration=str(previous) if previous else None,
                  previous_next_iteration=prior_plan)
    path.mkdir(parents=True, exist_ok=True)
    write_atomic(path / "run_config.json", config)
    for name in ("tool_calls.jsonl", "events.jsonl", "official_trials.jsonl"):
        (path / name).touch(exist_ok=True)
    write_atomic(path / "resume_state.json", {
        "status": "RUNNING", "units": config.get("units", []), "updated_at": now(),
    })
    record_source(path)
    event(path, "ITERATION_START", previous_next_iteration=prior_plan)
    return config


def record_source(path):
    for name, argv in (("source_changes.patch", ["git", "diff", "--binary", "HEAD"]),
                       ("working_tree_status.txt", ["git", "status", "--short"])):
        started = time.perf_counter()
        result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
        (path / name).write_text(result.stdout, encoding="utf-8")
        append(path / "tool_calls.jsonl", {"kind": "source_record", "argv": argv,
                                           "duration_ms": (time.perf_counter() - started) * 1000,
                                           "exit_code": result.returncode, "timestamp": now()})
    argv = ["git", "ls-files", "--others", "--exclude-standard", "our-project/code/src", "our-project/code/tests", "our-project/dashboard/agent_benchmark.js"]
    additions = subprocess.check_output(argv, cwd=ROOT, text=True).splitlines()
    with (path / "source_changes.patch").open("a", encoding="utf-8") as stream:
        for name in additions:
            diff = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", name], cwd=ROOT, text=True, capture_output=True)
            stream.write(diff.stdout)


def event(path: Path, event_type: str, **data):
    record = {"timestamp": now(), "event": event_type, **data}
    append(path / "events.jsonl", record)
    return record


def percentile(values, p):
    values = sorted(v for v in values if isinstance(v, (int, float)) and math.isfinite(v))
    if not values:
        return None
    return values[max(0, math.ceil(len(values) * p) - 1)]


def collect_trials(path: Path):
    config = json.loads((path / "run_config.json").read_text())
    units = {u["job_name"]: u for u in config.get("units", [])}
    trials = []
    for job in sorted((path / "jobs").glob("*")):
        if not job.is_dir():
            continue
        for row in audit_job(job)["trials"]:
            unit = units.get(job.name, {})
            trials.append({**unit, **row, "job_name": job.name, "job_dir": str(job)})
    recorded_tools = {(r.get("episode_id"), r.get("tool_call_id")) for r in rows(path / "tool_calls.jsonl") if r.get("kind") == "agent_tool"}
    for trial in trials:
        for step in trial.get("trace", {}).get("steps", []):
            for call in step.get("tool_calls", []):
                identity = (str(trial["trial_id"]), call.get("tool_call_id"))
                if identity in recorded_tools:
                    continue
                append(path / "tool_calls.jsonl", {"kind": "agent_tool", "episode_id": identity[0],
                       "job_id": trial.get("job_id"), "trial_id": trial.get("trial_id"),
                       "task_id": trial.get("task_id"), "job_name": trial.get("job_name"),
                       "tool_call_id": identity[1], "timestamp": step.get("timestamp"),
                       "step": step["step_id"], "command": (call.get("arguments") or {}).get("command"),
                       "exit_code": call.get("exit_code"), "duration_ms": call.get("duration_ms"),
                       "source": step["trace_file"], "observation": call.get("observation")})
                recorded_tools.add(identity)
    terminal = [trial for trial in trials if trial.get("trial_id") and trial.get("finished_at")]
    if terminal:
        ledger = ExperimentLedger(runs_root=config.get("ledger_runs_root"),
                                  ledgers_root=config.get("ledger_root"))
        for trial in terminal:
            ledger.record_official_trial(trial, events_path=path / "events.jsonl")
    # Rebuild from the immutable original results, never increment counters on resume.
    with tempfile.NamedTemporaryFile(mode="w", dir=path, prefix="official_trials.", suffix=".tmp", delete=False, encoding="utf-8") as stream:
        stream.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in trials))
        tmp = Path(stream.name)
    tmp.replace(path / "official_trials.jsonl")
    return trials


def summarize(path: Path, *, persist=True):
    trials = collect_trials(path) if persist else rows(path / "official_trials.jsonl")
    events = rows(path / "events.jsonl")
    benchmark_events = [e for e in events if e.get("sample_kind", "benchmark").lower() == "benchmark"]
    calls = [e for e in benchmark_events if e["event"] == "GENERATOR_END"]
    teachers = [e for e in benchmark_events if e["event"] in ("TEACHER_END", "TEACHER_ERROR")
                and e.get("provider_request_attempted", True)]
    verified = [r for r in trials if r["status"] == "OFFICIAL_ARTIFACT_VERIFIED"]
    binary = [r for r in verified if r.get("reward") in (0, 1)]
    success = sum(r["reward"] == 1 for r in binary)
    tools = [r for r in rows(path / "tool_calls.jsonl") if r.get("kind") == "agent_tool"]
    state_path = path / "resume_state.json"
    state = json.loads((state_path if state_path.exists() else path / "metrics.json").read_text())
    state.setdefault("units", [])
    model_calls = defaultdict(list)
    router_calls = defaultdict(list)
    for e in benchmark_events:
        if e["event"] == "ROUTER_END":
            router_calls[e.get("router_family", "unknown")].append(e.get("router_latency_ms"))
    costs = [c.get("cost_usd") for c in calls]
    # Reuse original Harbor request records without counting an event twice.
    event_ids = {str(c.get("episode_id")) for c in calls}
    native_only = [r for r in trials if r.get("agent") != "oracle"]
    # Routed V9 contexts already total generator and teacher usage. Recover their
    # original per-request rows when events are unavailable, never add both totals.
    native_teachers = []
    native_contexts = []
    recorded_requests = {(row["episode_id"], row["decision_id"]) for row in calls}
    for trial in native_only:
        metadata = trial.get("agent_metadata") or {}
        provider_metrics = metadata.get("provider_metrics")
        if provider_metrics is not None:
            for row in provider_metrics:
                key = (row["episode_id"], row["decision_id"])
                if key not in recorded_requests:
                    calls.append(row)
                    recorded_requests.add(key)
            native_teachers.extend(row for row in (metadata.get("v9") or {}).get("teacher_metrics", [])
                                   if row.get("provider_request_attempted", True))
        elif str(trial.get("trial_id")) not in event_ids:
            native_contexts.append(trial)
    teacher_ids = {str(row.get("episode_id")) for row in teachers}
    teachers.extend(row for row in native_teachers if str(row.get("episode_id")) not in teacher_ids)
    calls = [dict(row) for row in calls]
    teachers = [dict(row) for row in teachers]
    luna_spec = ModelRegistry().get_spec("gpt-6-luna")
    for row in calls + teachers:
        if (row.get("request_model_id") == luna_spec.model_id
                and row.get("returned_model_id") == luna_spec.model_id
                and row.get("usage_status") == "REPORTED"):
            row["official_rate_cost_usd"] = luna_spec.calculate_cost(
                row["prompt_tokens"], row["completion_tokens"],
                row.get("reasoning_tokens") or 0, row.get("cached_tokens") or 0,
                row.get("cache_write_tokens") or 0)
            row["official_rate_cost_status"] = luna_spec.pricing_status
    # Recompute costs from the recovered generator rows, not combined contexts.
    costs = [c.get("official_rate_cost_usd", c.get("cost_usd")) for c in calls]
    native_only = native_contexts
    for c in calls:
        model = c.get("selected_model_id") or c.get("returned_model") or c.get("returned_model_id") or c.get("model", "unknown")
        model_calls[model + " / " + c.get("protocol", "chat_completions")].append(c)
    native_costs = [r.get("cost_usd") for r in native_only]
    all_costs = costs + native_costs
    known_cost = round(sum(v for v in all_costs if isinstance(v, (int, float))), 10)
    complete_cost = bool(all_costs) and all(isinstance(v, (int, float)) for v in all_costs)
    durations = [r.get("duration_sec", r.get("episode_wall_s")) for r in verified]
    billed_calls = [c.get("actual_billed_cost_usd") for c in calls]
    native_billed = [r.get("actual_billed_cost_usd") for r in native_only]
    all_billed = billed_calls + native_billed
    billed_generator = sum(all_billed) if all_billed and all(v is not None for v in all_billed) else None
    teacher_costs = [c.get("official_rate_cost_usd", c.get("cost_usd")) for c in teachers]
    teacher_billed = [c.get("actual_billed_cost_usd") for c in teachers]
    teacher_cost = round(sum(teacher_costs), 10) if all(v is not None for v in teacher_costs) else None
    billed_teacher = sum(teacher_billed) if all(v is not None for v in teacher_billed) else None
    sandbox_costs = [(r.get("agent_metadata") or {}).get("sandbox_cost_usd") for r in trials]
    router_costs = [(r.get("agent_metadata") or {}).get("router_compute_cost_usd") for r in trials]
    sandbox_cost = sum(sandbox_costs) if sandbox_costs and all(v is not None for v in sandbox_costs) else None
    router_cost = sum(router_costs) if router_costs and all(v is not None for v in router_costs) else None
    full_cost = (billed_generator + billed_teacher + sandbox_cost + router_cost
                 if all(v is not None for v in (billed_generator, billed_teacher, sandbox_cost, router_cost)) else None)
    started = datetime.fromisoformat(json.loads((path / "run_config.json").read_text())["started_at"])
    elapsed = (datetime.fromisoformat(state.get("finished_at", now())) - started).total_seconds()
    current = next((u for u in state["units"] if u["status"] == "RUNNING"), None)
    unit = current or (state["units"][-1] if state["units"] else {})
    unit_trials = [r for r in trials if r.get("job_name") == unit.get("job_name")]
    current_trial = next((r for r in unit_trials if not r.get("finished_at")),
                         unit_trials[-1] if unit_trials else None)
    current_id = str(current_trial["trial_id"]) if current_trial and current_trial.get("trial_id") else None
    last_generator = next((c for c in reversed(calls) if current_id and c.get("episode_id") == current_id), None)
    last_tool = next((t for t in reversed(tools) if current_id and t.get("episode_id") == current_id), None)
    native_tokens = [r.get("n_input_tokens") + r.get("n_output_tokens")
                     if r.get("n_input_tokens") is not None and r.get("n_output_tokens") is not None else None
                     for r in native_only]
    call_tokens = [c["prompt_tokens"] + c["completion_tokens"]
                   if c.get("prompt_tokens") is not None and c.get("completion_tokens") is not None else None for c in calls]
    token_values = call_tokens + native_tokens
    teacher_token_values = [c["prompt_tokens"] + c["completion_tokens"]
                           if c.get("prompt_tokens") is not None and c.get("completion_tokens") is not None
                           else None for c in teachers]
    model_tokens = token_values + teacher_token_values
    model_costs = all_costs + teacher_costs
    mapped_requests = [dict(row, role=role) for role, group in (("generator", calls), ("teacher", teachers))
                       for row in group if row.get("cost_basis") == "SELECTED_MODEL_RATES_WITH_BACKEND_USAGE"]
    mapped_costs = [row.get("cost_usd") for row in mapped_requests]
    mapped_specs = {row["cost_model_id"]: ModelRegistry().get_spec(row["cost_model_id"])
                    for row in mapped_requests}
    metrics = {
        "timestamp": now(), "iteration_id": path.name, "status": state["status"],
        "reason": state.get("reason"),
        "observed_trials": len(trials), "verified_trials": len(verified), "successes": success,
        "success_rate": success / len(binary) if binary else None,
        "total_units": len(state["units"]),
        "finished_units": sum(u["status"] in ("EVALUATED", "FAILED", "BLOCKED", "NOT_EVALUATED") for u in state["units"]),
        "current": current, "current_trial": current_trial,
        "generator_tokens": sum(token_values) if token_values and all(v is not None for v in token_values) else None,
        "teacher_calls": len(teachers),
        "teacher_tokens": sum(teacher_token_values) if all(v is not None for v in teacher_token_values) else None,
        "total_model_tokens": sum(model_tokens) if model_tokens and all(v is not None for v in model_tokens) else None,
        "generator_cost_usd": known_cost if complete_cost else None,
        "known_generator_cost_usd": known_cost if any(v is not None for v in all_costs) else None,
        "teacher_cost_usd": teacher_cost,
        "known_teacher_cost_usd": round(sum(v for v in teacher_costs if v is not None), 10) if any(v is not None for v in teacher_costs) else None,
        "episode_model_cost_usd": round(sum(model_costs), 10) if model_costs and all(v is not None for v in model_costs) else None,
        "execution_mode": "ALIAS_SMOKE" if mapped_requests else "REAL_API",
        "mapped_cost_accounting": {
            "cost_basis": "SELECTED_MODEL_RATES_WITH_BACKEND_USAGE",
            "requests": mapped_requests,
            "known_cost_usd": round(sum(v for v in mapped_costs if v is not None), 10) if mapped_costs else None,
            "total_cost_usd": round(sum(mapped_costs), 10) if mapped_costs and all(v is not None for v in mapped_costs) else None,
            "missing_usage_requests": sum(row.get("usage_status") != "REPORTED" for row in mapped_requests),
            "model_rates": {model: {
                "source": spec.pricing_source, "pricing_status": spec.pricing_status,
                "usd_per_1m_tokens": {
                    "input": spec.input_price_per_1m, "output": spec.output_price_per_1m,
                    "cache_read": spec.cache_read_price_per_1m, "cache_write": spec.cache_write_price_per_1m,
                },
            } for model, spec in mapped_specs.items()},
        } if mapped_requests else None,
        "cost_source": "provider_usage_and_registry_rates; not an invoice",
        "official_rate_accounting": {
            "model": luna_spec.model_id,
            "pricing_status": luna_spec.pricing_status,
            "price_source": luna_spec.pricing_source,
            "cache_write_price_source": "https://developers.openai.com/api/docs/pricing?latest-pricing-expanded=true",
            "usd_per_1m_tokens": {
                "input": luna_spec.input_price_per_1m, "output": luna_spec.output_price_per_1m,
                "cache_read": luna_spec.cache_read_price_per_1m,
                "cache_write_30m": luna_spec.cache_write_price_per_1m,
            },
            "service_tier": "standard", "input_context": "<=272K",
            "cache_policy": "Raw missing counts stay null; corresponding input charged at ordinary input rate",
            "reasoning_policy": "Completion includes reasoning; counted once",
            "requests": [{
                "role": role, "episode_id": c.get("episode_id"), "response_id": c.get("response_id"),
                "prompt_tokens": c["prompt_tokens"], "completion_tokens": c["completion_tokens"],
                "reasoning_tokens": c.get("reasoning_tokens"), "cached_tokens": c.get("cached_tokens"),
                "cache_write_tokens": c.get("cache_write_tokens"),
                "recorded_cost_usd": c.get("cost_usd"), "official_rate_cost_usd": c["official_rate_cost_usd"],
            } for role, group in (("generator", calls), ("teacher", teachers))
              for c in group if "official_rate_cost_usd" in c],
        } if not mapped_requests else None,
        "actual_generator_cost_usd": billed_generator,
        "actual_teacher_cost_usd": billed_teacher,
        "sandbox_cost_usd": sandbox_cost, "router_compute_cost_usd": router_cost,
        "complete_cost_usd": full_cost,
        "generator_cost_per_success_usd": known_cost / success if complete_cost and success else None,
        "actual_cost_per_success_usd": full_cost / success if full_cost is not None and success else None,
        "router_latency_ms": {k: {"n": len(v), "p50": percentile(v, .5), "p95": percentile(v, .95)} for k, v in router_calls.items()},
        "router_inference_latency_ms": {k: {
            "p50": percentile([e.get("inference_latency_ms") for e in benchmark_events if e["event"] == "ROUTER_END" and e.get("router_family") == k], .5),
            "p95": percentile([e.get("inference_latency_ms") for e in benchmark_events if e["event"] == "ROUTER_END" and e.get("router_family") == k], .95),
        } for k in router_calls},
        "generator_request_time_ms": sum(c["latency_ms"] for c in calls) if calls and all(
            c.get("latency_ms") is not None for c in calls) else None,
        "teacher_request_time_ms": sum(c["latency_ms"] for c in teachers) if teachers and all(
            c.get("latency_ms") is not None for c in teachers) else None,
        "router_total_time_ms": {k: sum(v) if all(x is not None for x in v) else None
                                 for k, v in router_calls.items()},
        "container_time_resources": [{
            "trial_id": r.get("trial_id"), "episode_wall_s": r.get("episode_wall_s"),
            "phase_wall_s": r.get("phase_wall_s"),
        } for r in trials],
        "models": {k: {
            "actual_backend_model_ids": sorted({x.get("actual_backend_model_id") or x.get("returned_model_id") for x in v
                                                if x.get("actual_backend_model_id") or x.get("returned_model_id")}),
            "calls": len(v), "ttft_p50_ms": percentile([x.get("ttft_ms") for x in v], .5),
            "ttft_p95_ms": percentile([x.get("ttft_ms") for x in v], .95),
            "output_tokens_per_s": percentile([x.get("output_tokens_per_s") for x in v], .5),
            "stream_output_tokens_per_s_estimate": percentile([x.get("stream_output_tokens_per_s") for x in v], .5),
        } for k, v in model_calls.items()},
        "tool_exec_p50_ms": percentile([t["duration_ms"] for t in tools], .5),
        "tool_exec_p95_ms": percentile([t["duration_ms"] for t in tools], .95),
        "episode_p50_s": percentile(durations, .5), "episode_p95_s": percentile(durations, .95),
        "episodes_per_hour": len(verified) * 3600 / elapsed if verified and elapsed > 0 else None,
        "failure_classes": dict(Counter(e.get("category", "UNKNOWN") for e in events if e["event"] == "ERROR")),
        "last_event": events[-1] if events else None,
        "last_generator": last_generator,
        "last_tool": last_tool,
        "measurement_counts": dict(Counter(c.get("sample_kind", "benchmark") for c in events if c["event"] == "GENERATOR_END")),
        "last_unit": state["units"][-1] if state["units"] else None,
        "measurement_scope": "Benchmark metrics exclude provider/router probes; original probe events remain in events.jsonl",
        "ttft_scope": "Upstream provider timing; native relay buffers the response before returning it",
        "publication_status": "ALIAS_SMOKE_ONLY" if mapped_requests else "NOT_EVALUATED" if not verified else "AWAITING_PAIRED_SCIENTIFIC_ANALYSIS",
        "missing_measurements": ["sandbox billing", "router infrastructure cost", "provider invoice reconciliation"],
    }
    if persist:
        write_atomic(path / "metrics.json", metrics)
    return metrics


def display(metrics):
    current = metrics.get("current") or metrics.get("last_unit") or {}
    trial = metrics.get("current_trial") or {}
    call = metrics.get("last_generator") or {}
    tool = metrics.get("last_tool") or {}
    show = lambda value: "N/A" if value is None else str(value)
    return (
        f"{metrics['timestamp']} | {metrics['status']} | Job={show(trial.get('job_id'))} "
        f"JobName={show(current.get('job_name'))} Trial={show(trial.get('trial_id'))} "
        f"Task={current.get('task_id', '-')} Policy={current.get('policy', '-')} "
        f"Step={show(call.get('step', tool.get('step')))} Model={show(call.get('selected_model_id', call.get('model')))} "
        f"Backend={show(call.get('returned_model_id', call.get('returned_model')))} "
        f"Effort={show(call.get('effort'))} TTFT={show(call.get('ttft_ms'))}ms "
        f"TPS={show(call.get('output_tokens_per_s'))} Tokens={show(metrics['generator_tokens'])} "
        f"LastTool={show(tool.get('command'))} TrialStatus={trial.get('status', 'NOT_EVALUATED')} "
        f"VerifierSource={show(trial.get('verifier_path'))} Reward={show(trial.get('reward'))} "
        f"Verifier={metrics['verified_trials']} Success={metrics['successes']} "
        f"GeneratorUSD={show(metrics['generator_cost_usd'])} TeacherUSD={show(metrics['teacher_cost_usd'])} "
        f"ModelUSD={show(metrics['episode_model_cost_usd'])} TotalUSD={show(metrics['complete_cost_usd'])} "
        f"Progress={metrics['finished_units']}/{metrics['total_units']}"
        f" | Router={json.dumps(metrics['router_latency_ms'], ensure_ascii=False)} "
        f"ToolExit={show(tool.get('exit_code'))} ToolMs={show(tool.get('duration_ms'))} "
        f"ToolP95={show(metrics['tool_exec_p95_ms'])}ms EpisodeP95={show(metrics['episode_p95_s'])}s "
        f"Episodes/h={show(metrics['episodes_per_hour'])}"
    )


def publish(path: Path, output: Path = DASHBOARD):
    metrics = summarize(path)
    write_atomic(output, metrics)
    config = json.loads((path / "run_config.json").read_text())
    if config.get("dashboard_ssh"):
        target = config["dashboard_ssh"]
        remote_path = config["dashboard_remote_path"]
        import shlex
        command = f"cat > {shlex.quote(remote_path + '.tmp')} && mv {shlex.quote(remote_path + '.tmp')} {shlex.quote(remote_path)}"
        try:
            result = subprocess.run([
                "ssh", "-i", config["dashboard_ssh_key"], "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=4", target, command,
            ], input=json.dumps(metrics, ensure_ascii=False), text=True, capture_output=True, timeout=8)
            if result.returncode:
                print(f"Dashboard upload failed: exit {result.returncode}", flush=True)
        except subprocess.TimeoutExpired:
            print("Dashboard upload timed out; local experiment records remain available", flush=True)
    print(display(metrics), flush=True)
    return metrics


def execute(path: Path, argv: list[str], *, env=None, label="command", interval=10, output=DASHBOARD):
    """Run one command, retain its full output, and publish progress while it runs."""
    command_id = f"{label}-{time.time_ns()}"
    log = path / "commands" / f"{command_id}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    event(path, "COMMAND_START", argv=argv, command_id=command_id)
    lines = queue.Queue()
    proc = subprocess.Popen(argv, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, bufsize=1)

    def reader():
        for line in proc.stdout:
            lines.put(line)
        lines.put(None)

    threading.Thread(target=reader, daemon=True).start()
    finished = False
    next_tick = 0.0
    interrupted = False
    try:
        with log.open("w", encoding="utf-8") as stream:
            while not finished:
                try:
                    line = lines.get(timeout=.25)
                    if line is None:
                        finished = True
                    else:
                        stream.write(line)
                        stream.flush()
                        print(line, end="", flush=True)
                except queue.Empty:
                    pass
                if time.monotonic() >= next_tick:
                    publish(path, output)
                    next_tick = time.monotonic() + interval
        code = proc.wait()
    except KeyboardInterrupt:
        interrupted = True
        # Only stop the command owned by this iteration, never a training service.
        proc.terminate()
        code = proc.wait()
    record = {"kind": "terminal_command", "argv": argv, "exit_code": code,
              "duration_ms": (time.monotonic() - t0) * 1000, "log": str(log),
              "command_id": command_id, "timestamp": now()}
    append(path / "tool_calls.jsonl", record)
    event(path, "COMMAND_END", **record)
    if interrupted:
        raise KeyboardInterrupt
    return code


def finish(path: Path, status: str, reason: str = ""):
    config = json.loads((path / "run_config.json").read_text())
    state = json.loads((path / "resume_state.json").read_text())
    state.update(status=status, updated_at=now(), finished_at=now(), reason=reason)
    write_atomic(path / "resume_state.json", state)
    record_source(path)
    metrics = summarize(path)
    unresolved = [u for u in state["units"] if u["status"] not in ("EVALUATED",)]
    errors = [e for e in rows(path / "events.jsonl") if e["event"] == "ERROR"]
    source_problems = []
    for name in ("provider_evidence.json", "router_evidence.json", "harbor_evidence.json"):
        evidence_path = path / name
        if evidence_path.exists():
            evidence = json.loads(evidence_path.read_text())
            source_problems.extend(evidence.get("limitations", evidence.get("remaining", [])))
    plan = {
        "status": status, "reason": reason, "pending_units": unresolved,
        "unresolved_problems": ([reason] if reason else []) + source_problems,
        "hypotheses": ["The same official mini-swe-agent can isolate policy effects on paired tasks."],
        "required_config": str(path / "run_config.json"),
        "priority": "Resolve the recorded cause before another paid attempt" if reason else "Continue the recorded task order",
        "failure_categories": list(metrics["failure_classes"]),
        "completed_units": [u for u in state["units"] if u["status"] == "EVALUATED"],
        "next_command": f"python -m modelrouter.benchmark resume {path}",
        "sealed_test": "REQUIRES_OWNER_CONFIRMATION",
    }
    if config.get("kind") == "DEVELOPMENT_AND_PROVIDER_PROBES":
        plan["next_command"] = "python -m modelrouter.benchmark run --canary"
        plan["execution_order"] = ["Oracle single", "native mini single", "routed mini single", "Canary", "Dev", "RQ1-RQ5 observed experiments", "Sealed with owner authorization"]
        plan["priority"] = "Restore an authorized sandbox path; retain existing probes and original failed Oracle record"
    plan["completed_development"] = config.get("completed_development", [])
    write_atomic(path / "next_iteration.json", plan)
    commands = rows(path / "tool_calls.jsonl")
    command_summary = "\n".join(
        f"- {' '.join(c.get('argv', [])) or c.get('command', c.get('kind', 'tool'))}: "
        f"exit={c.get('exit_code', 'N/A')}, duration_ms={c.get('duration_ms', 'N/A')}"
        for c in commands if c.get("kind") != "agent_tool")
    error_summary = "\n".join(f"- {e.get('category')}: {e.get('error')}" for e in errors)
    completion_summary = "\n".join(f"- {item}" for item in config.get("completed_development", []))
    report = (
        f"# {path.name}\n\n状态：{status}。\n\n"
        f"官方已评分 Trial：{metrics['verified_trials']}；成功：{metrics['successes']}。\n\n"
        f"记录工具调用与终端命令：{len(commands)} 条，详见 tool_calls.jsonl 和 commands/。\n\n"
        f"原因：{reason or '无新增运行问题'}。\n\n"
        f"本轮完成事项：\n\n{completion_summary or '详见已评分任务与命令结果'}\n\n"
        f"实际命令与结果：\n\n{command_summary or '无终端命令'}\n\n"
        f"已记录的问题：\n\n{error_summary or '无新增错误'}\n\n"
        "RQ1–RQ5：仅原始官方 Trial 可提供结果证据；缺少成对任务、费用或消融数据时不产生科研结论。\n\n"
        "RQ1：统一 Harness 与费用字段；RQ2：真实 pool 分组；RQ3：真实 granularity 分组；"
        "RQ4：实际消融与 checkpoint 分组；RQ5：运行前 workload 标签与成对收益。统计通路可用，正式数据仍待运行。\n\n"
        "下一轮读取 next_iteration.json，保留原 Job 与 Trial，沿用 run_config.json。\n"
    )
    (path / "review.md").write_text(report, encoding="utf-8")
    return publish(path)
