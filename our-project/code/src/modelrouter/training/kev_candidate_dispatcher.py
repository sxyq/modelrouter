#!/usr/bin/env python3
"""Continue Kev candidates in order using recorded training and project Val results.

Completed training resumes at Val through upstream kev.benchmark. Attempts,
commands, progress and terminal outcomes remain in the existing run and queue.
Missing material or incompatible rank leaves a candidate pending; insufficient
GPU memory returns WAITING_FOR_GPU without launching a training process.
"""

import argparse
import copy
import os
import re
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("kev_dispatcher")

PROJECT_ROOT = Path("/home/syy/路由")
KEV_RUNS_ROOT = PROJECT_ROOT / "runs"
QUEUE_FILE = PROJECT_ROOT / "our-project" / "results" / "training" / "kev" / "candidate_queue.json"
LEDGER_FILE = PROJECT_ROOT / "our-project" / "results" / "training" / "kev" / "candidate_ledger.json"
FIXED_VAL_PATH = "data/kev/公开数据/val.jsonl"

DEFAULT_CANDIDATES = [
    {
        "candidate_id": "KEV-V8-C03",
        "name": "KEV-V8-HOMOLOGOUS-20261018",
        "description": "Homologous run Ep 1 (LoRA r16, lr=2e-5, active)",
        "status": "RUNNING",
        "init_from": "models/kev-4b-adapter",
        "data_path": "data/kev/公开数据/train.jsonl",
        "lr": "2e-5",
        "lora": "16",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": ["--checkpointing", "1"],
        "checkpoint_path": "runs/KEV-V8-HOMOLOGOUS-20261018/formal_run",
        "metrics": {}
    },
    {
        "candidate_id": "KEV-V8-C04",
        "name": "KEV-V8-HOMO-e02",
        "description": "Homologous continuation Ep 2 with cosine decay lr=1e-5",
        "status": "QUEUED",
        "init_from": "runs/KEV-V8-HOMOLOGOUS-20261018/formal_run",
        "data_path": "data/kev/公开数据/train.jsonl",
        "lr": "1e-5",
        "lora": "16",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": ["--checkpointing", "1"],
        "checkpoint_path": "runs/KEV-V8-HOMO-e02/checkpoint",
        "metrics": {}
    },
    {
        "candidate_id": "KEV-V8-C05",
        "name": "KEV-V8-ABL-NOSTATE",
        "description": "State ablation: Zeroed/masked state features",
        "status": "QUEUED",
        "init_from": "models/kev-4b-adapter",
        "data_path": "data/kev/公开数据/train_nostate.jsonl",
        "lr": "2e-5",
        "lora": "16",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": ["--checkpointing", "1"],
        "checkpoint_path": "runs/KEV-V8-ABL-NOSTATE/checkpoint",
        "metrics": {}
    },
    {
        "candidate_id": "KEV-V8-C07",
        "name": "KEV-V8-ABL-LORA8",
        "description": "Capacity ablation: LoRA rank 8",
        "status": "QUEUED",
        "init_from": "models/kev-4b-adapter",
        "data_path": "data/kev/公开数据/train.jsonl",
        "lr": "5e-5",
        "lora": "8",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": ["--checkpointing", "1"],
        "checkpoint_path": "runs/KEV-V8-ABL-LORA8/checkpoint",
        "metrics": {}
    },
    {
        "candidate_id": "KEV-V8-C09",
        "name": "KEV-V8-EXT-01",
        "description": "V8 Extension: Arena human pairwise preference + agent traces",
        "status": "QUEUED",
        "init_from": "models/kev-4b-adapter",
        "data_path": "data/kev/v8_extension/train.jsonl",
        "lr": "2e-5",
        "lora": "16",
        "epochs": "1",
        "batch": "1",
        "accum": "4",
        "extra_args": ["--checkpointing", "1"],
        "checkpoint_path": "runs/KEV-V8-EXT-01/formal_run",
        "pilot_checkpoint_path": "runs/KEV-V8-EXT-01/checkpoint",
        "training_kind": "FORMAL_LORA",
        "metrics": {}
    }
]

def load_queue() -> List[Dict[str, Any]]:
    if QUEUE_FILE.is_file():
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            for candidate in queue:
                if candidate["candidate_id"] == "KEV-V8-C09":
                    candidate["pilot_checkpoint_path"] = f"runs/{candidate['name']}/checkpoint"
                    candidate["checkpoint_path"] = f"runs/{candidate['name']}/formal_run"
                    candidate["training_kind"] = "FORMAL_LORA"
            return queue
        except Exception as e:
            logger.warning(f"Failed to read queue file: {e}")
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    queue = copy.deepcopy(DEFAULT_CANDIDATES)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    return queue

def save_queue(queue: List[Dict[str, Any]]):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2), encoding="utf-8")

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def check_checkpoint_integrity(ckpt_dir: Path) -> tuple[bool, str]:
    """Verifies that head.pt and tokenizer/adapter files exist and are valid."""
    if not ckpt_dir.is_dir():
        return False, f"Directory does not exist: {ckpt_dir}"
    
    head_file = ckpt_dir / "head.pt"
    if not head_file.is_file() or head_file.stat().st_size < 1024:
        return False, f"Missing or corrupted head.pt in {ckpt_dir}"
    
    # Check adapter weights
    adapter_bin = ckpt_dir / "adapter_model.bin"
    adapter_safe = ckpt_dir / "adapter_model.safetensors"
    if not (adapter_bin.is_file() or adapter_safe.is_file()):
        return False, f"Missing adapter weights (adapter_model.bin / safetensors) in {ckpt_dir}"
    
    # Check tokenizer files
    has_tok = any((ckpt_dir / f).is_file() for f in ["tokenizer.json", "vocab.json", "tokenizer_config.json"])
    if not has_tok:
        return False, f"Missing tokenizer files in {ckpt_dir}"
        
    return True, "Integrity OK"

def run_fixed_validation(ckpt_dir: Path, out_file: Path, device: str = "auto",
                         timeout: Optional[float] = None) -> tuple[bool, Dict[str, Any]]:
    """Score the existing project Val through Kev's labelled-JSONL entry point."""
    logger.info(f"Running formal evaluation on checkpoint: {ckpt_dir}")
    attempts_dir = out_file.with_suffix("")
    attempts_dir.mkdir(parents=True, exist_ok=True)
    if out_file.is_file():
        prior = json.loads(out_file.read_text(encoding="utf-8"))
        prior_file = attempts_dir / f"attempt_{prior.get('attempt_id', 0):04d}.json"
        if not prior_file.exists():
            prior_file.write_text(json.dumps(prior, indent=2), encoding="utf-8")
    previous_ids = [int(p.name[8:12]) for p in attempts_dir.iterdir() if re.fullmatch(r"attempt_\d{4}(\.json)?", p.name)]
    attempt_id = max(previous_ids, default=0) + 1
    report_dir = attempts_dir / f"attempt_{attempt_id:04d}"
    val_path = PROJECT_ROOT / FIXED_VAL_PATH
    eval_cmd = [
        str(PROJECT_ROOT / ".venv" / "bin" / "python"),
        "-u", "-m", "kev.benchmark",
        "--run", str(ckpt_dir),
        "--data", str(val_path),
        "--out", str(report_dir),
        "--device", device,
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "external" / "kev")
    if device == "cpu":
        env.update(OMP_NUM_THREADS="8", CUDA_VISIBLE_DEVICES="")
    log_file = attempts_dir / f"attempt_{attempt_id:04d}.log"
    
    started = time.monotonic()
    metrics = {
        "evaluation_status": "EVALUATING",
        "validation_set": str(val_path),
        "validation_protocol": "KEV_FIXED_VAL_JSONL",
        "dataset_split": "val",
        "test_used": False,
        "command": eval_cmd,
        "report_path": str(report_dir / "report.json"),
        "exit_code": None,
        "attempt_id": attempt_id,
        "device": device,
        "timeout_sec": timeout,
        "log_path": str(log_file),
    }
    attempt_file = attempts_dir / f"attempt_{attempt_id:04d}.json"
    serialized = json.dumps(metrics, indent=2)
    attempt_file.write_text(serialized, encoding="utf-8")
    out_file.write_text(serialized, encoding="utf-8")
    logger.info("Val attempt %s, progress log: %s", attempt_id, log_file)
    try:
        with log_file.open("w", encoding="utf-8") as output:
            res = subprocess.run(eval_cmd, cwd=str(PROJECT_ROOT), env=env, stdout=output,
                                 stderr=subprocess.STDOUT, text=True, timeout=timeout)
        raw_output = log_file.read_text(encoding="utf-8")
        metrics.update(exit_code=res.returncode, raw_output=raw_output)
        if res.returncode != 0:
            logger.error("Evaluation process failed with code %s; log: %s", res.returncode, log_file)
            metrics.update(evaluation_status="FAILED", error=raw_output)
        else:
            report = json.loads((report_dir / "report.json").read_text(encoding="utf-8"))
            coverage = report["coverage"]
            metrics.update(report=report, clean=report["clean"], coverage=coverage)
            metrics["evaluation_status"] = (
                "EVALUATED" if coverage["evaluated_records"] == coverage["requested_records"]
                else "PARTIAL"
            )
    except Exception as e:
        logger.error(f"Evaluation execution exception: {e}")
        metrics.update(evaluation_status="FAILED", error=str(e))
    metrics.update(
        duration_sec=time.monotonic() - started,
        evaluated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    out_file.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(metrics, indent=2)
    attempt_file.write_text(serialized, encoding="utf-8")
    out_file.write_text(serialized, encoding="utf-8")
    return metrics["evaluation_status"] == "EVALUATED", metrics

def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _progress(line):
    match = re.search(r"ep(\d+)\s+step\s+(\d+)/(\d+)\s+loss\s+([-+\deE.]+)", line)
    if not match:
        return {}
    return dict(epoch=int(match[1]), step=int(match[2]), total_steps=int(match[3]),
                loss=float(match[4]), loss_step=int(match[2]))


def refresh_training(candidate):
    run_dir = KEV_RUNS_ROOT / candidate["name"]
    cursor_file = (PROJECT_ROOT / candidate["checkpoint_path"] if candidate["candidate_id"] == "KEV-V8-C09" else run_dir) / "cursor.json"
    cursor = json.loads(cursor_file.read_text()) if cursor_file.is_file() else {}
    log_file = run_dir / "train.log"
    if log_file.is_file():
        with log_file.open(encoding="utf-8") as stream:
            for line in stream:
                cursor.update(_progress(line))
    training_file = PROJECT_ROOT / candidate["checkpoint_path"] / "training_metrics.json"
    metrics = json.loads(training_file.read_text()) if training_file.is_file() else {}
    exit_code = cursor.get("exit_code")
    pid = cursor.get("pid", candidate.get("pid"))
    alive = bool(pid and is_pid_alive(pid))
    candidate["training_status"] = (
        "RUNNING" if alive else "FAILED" if exit_code is not None and exit_code != 0
        else "COMPLETED" if exit_code == 0 or metrics else "UNKNOWN"
    )
    candidate.update(pid=pid, training_exit_code=exit_code,
                     training_source=str(training_file if metrics else cursor_file),
                     training_metrics={k: metrics.get(k) for k in
                        ("optimizer_steps", "records_seen", "requested_records", "wall_seconds")})
    if metrics:
        cursor.update(step=metrics.get("optimizer_steps"), consumed_records=metrics.get("records_seen"))
    candidate.update({k: cursor[k] for k in ("step", "total_steps", "epoch", "loss", "loss_step") if k in cursor})
    return alive


def record_c03_comparison(candidate, queue):
    comparison = {"reference_candidate_id": "KEV-V8-C03", "status": "NOT_EVALUATED",
                  "direction": "candidate_minus_c03",
                  "deltas": {name: None for name in ("acc", "nll", "brier", "ece")}}
    candidate["comparison_to_c03"] = comparison
    if candidate["candidate_id"] == "KEV-V8-C03":
        comparison.update(status="REFERENCE", reason="C03 is the reference; no self-comparison")
        return
    reference = next((c for c in queue if c["candidate_id"] == "KEV-V8-C03"), None)
    ours = candidate.get("metrics", {})
    theirs = reference.get("metrics", {}) if reference else {}
    if ours.get("evaluation_status") != "EVALUATED" or theirs.get("evaluation_status") != "EVALUATED":
        comparison["reason"] = "Both candidates need completed project Val results"
        return
    for field in ("validation_protocol", "validation_set"):
        if not ours.get(field) or ours[field] != theirs.get(field):
            comparison["reason"] = f"Different or missing {field}"
            return
    coverage = ours.get("coverage", {})
    required = ("requested_records", "evaluated_records", "requested_questions", "evaluated_questions")
    if (any(coverage.get(k) is None for k in required) or coverage != theirs.get("coverage")
            or coverage["requested_records"] != coverage["evaluated_records"]
            or coverage["requested_questions"] != coverage["evaluated_questions"]):
        comparison["reason"] = "Different, incomplete or missing coverage"
        return
    our_clean, their_clean = ours.get("clean", {}), theirs.get("clean", {})
    if our_clean.get("n") != their_clean.get("n") or our_clean.get("n") is None:
        comparison["reason"] = "Different or missing scored question count"
        return
    if any(not isinstance(clean.get(k), (int, float)) for clean in (our_clean, their_clean)
           for k in comparison["deltas"]):
        comparison["reason"] = "Missing clean metrics"
        return
    comparison.update(status="COMPARABLE", validation_protocol=ours["validation_protocol"],
                      validation_set=ours["validation_set"], coverage=copy.deepcopy(coverage),
                      candidate_report_path=ours.get("report_path"), reference_report_path=theirs.get("report_path"),
                      deltas={k: our_clean[k] - their_clean[k] for k in comparison["deltas"]})


def validate_candidate(candidate, queue, device="auto", timeout=None):
    ckpt = PROJECT_ROOT / candidate["checkpoint_path"]
    val_file = ckpt / "val_metrics.json"
    current = candidate.get("metrics", {})
    saved = json.loads(val_file.read_text()) if val_file.is_file() else {}
    if saved.get("evaluation_status") == "EVALUATED" and saved.get("validation_set") == str(PROJECT_ROOT / FIXED_VAL_PATH):
        if candidate.get("failure_reason"):
            candidate.setdefault("evaluation_attempts", []).append({
                "type": "PRIOR_RESULT", "status": candidate.get("status"),
                "failure_reason": candidate["failure_reason"], "metrics": copy.deepcopy(current)})
        current = saved
        candidate["metrics"] = saved
    if current.get("evaluation_status") == "EVALUATED" and current.get("validation_set") == str(PROJECT_ROOT / FIXED_VAL_PATH):
        candidate.update(status="COMPLETED", evaluation_status="EVALUATED")
        candidate.pop("failure_reason", None)
        record_c03_comparison(candidate, queue)
        save_queue(queue)
        return True
    attempts = candidate.setdefault("evaluation_attempts", [])
    if candidate.get("failure_reason") or current:
        attempts.append({"type": "PRIOR_RESULT", "status": candidate.get("status"),
                         "failure_reason": candidate.get("failure_reason"), "metrics": copy.deepcopy(current)})
    attempt = {"type": "VALIDATION", "started_at": _now(), "status": "EVALUATING", "device": device}
    attempts.append(attempt)
    candidate.update(evaluation_status="EVALUATING", validation_set=str(PROJECT_ROOT / FIXED_VAL_PATH))
    save_queue(queue)
    ok, metrics = run_fixed_validation(ckpt, val_file, device=device, timeout=timeout)
    attempt.update(status=metrics["evaluation_status"], metrics=copy.deepcopy(metrics), finished_at=_now())
    candidate.update(metrics=metrics, evaluation_status=metrics["evaluation_status"],
                     status="COMPLETED" if ok else "FAILED", finished_at=_now())
    if not ok:
        candidate["failure_reason"] = "Validation evaluation failed"
    else:
        candidate.pop("failure_reason", None)
    record_c03_comparison(candidate, queue)
    save_queue(queue)
    return ok


def main_loop(validation_only=False, validation_device="auto", validation_timeout=None):
    logger.info("=== Kev candidate queue ===")
    while True:
        queue = load_queue()
        candidate = next((c for c in queue if c.get("status") != "COMPLETED"), None)
        if candidate is None:
            return 0
        alive = refresh_training(candidate)
        save_queue(queue)
        if alive:
            if validation_only:
                logger.info("Training is active; no validation started")
                return 1
            time.sleep(60)
            continue
        prior_val = candidate.get("metrics", {})
        saved_val_file = PROJECT_ROOT / candidate["checkpoint_path"] / "val_metrics.json"
        if saved_val_file.is_file():
            saved_val = json.loads(saved_val_file.read_text())
            if saved_val.get("evaluation_status") == "EVALUATED":
                prior_val = saved_val
        successful_val = prior_val.get("evaluation_status") == "EVALUATED" and prior_val.get("validation_set") == str(PROJECT_ROOT / FIXED_VAL_PATH)
        if candidate.get("status") == "FAILED" and not validation_only and not successful_val:
            logger.error("%s remains FAILED: %s", candidate["candidate_id"], candidate.get("failure_reason"))
            return 1
        if candidate["training_status"] == "COMPLETED":
            ok = validate_candidate(candidate, queue, validation_device, validation_timeout)
            if not ok or validation_only:
                return 0 if ok else 1
            continue
        if validation_only:
            logger.info("%s has no completed training to validate", candidate["candidate_id"])
            return 1
        if candidate.get("status") == "RUNNING" or candidate["training_status"] == "FAILED":
            candidate.update(status="FAILED", failure_reason="Training exited without successful completion")
            save_queue(queue)
            return 1
        data = PROJECT_ROOT / candidate["data_path"]
        if not data.is_file():
            candidate.update(status="PENDING", pending_reason=f"Missing training data: {data}")
            save_queue(queue)
            return 1
        init = PROJECT_ROOT / candidate["init_from"]
        if not init.exists():
            candidate.update(status="PENDING", pending_reason=f"Missing init_from: {init}")
            save_queue(queue)
            return 1
        adapter_config = init / "adapter_config.json"
        training_config = init / "training_config.json"
        source_args = json.loads(training_config.read_text(encoding="utf-8"))["args"] if training_config.is_file() else {}
        init_rank = source_args.get("lora")
        rank_source = training_config
        if init_rank is None and adapter_config.is_file():
            init_rank = json.loads(adapter_config.read_text(encoding="utf-8")).get("r")
            rank_source = adapter_config
        candidate["init_lora"] = init_rank
        candidate["init_lora_source"] = str(rank_source) if init_rank is not None else None
        if init_rank is not None and int(candidate["lora"]) != int(init_rank):
            candidate.update(status="PENDING", configuration_status="INCOMPATIBLE",
                             pending_reason=f"warm_start lora: source rank {init_rank}, requested rank {candidate['lora']}")
            save_queue(queue)
            return 1
        peak_source = PROJECT_ROOT / DEFAULT_CANDIDATES[0]["checkpoint_path"] / "training_metrics.json"
        peak_metrics = json.loads(peak_source.read_text(encoding="utf-8"))
        peak_bytes = peak_metrics["peak_device_bytes"]
        required_mib = (peak_bytes + 1048575) // 1048576 + 2048
        gpu_cmd = ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits", "--id=0"]
        gpu_result = subprocess.run(gpu_cmd, capture_output=True, text=True, check=True)
        free_mib = int(gpu_result.stdout.strip())
        candidate["gpu_resource"] = {"source": str(peak_source), "peak_device_bytes": peak_bytes,
                                     "margin_mib": 2048, "required_mib": required_mib,
                                     "free_mib": free_mib, "observed_at": _now(), "command": gpu_cmd}
        if free_mib < required_mib:
            candidate.update(status="WAITING_FOR_GPU", training_status="WAITING_FOR_GPU")
            save_queue(queue)
            logger.info("%s WAITING_FOR_GPU: free %s MiB, required %s MiB",
                        candidate["candidate_id"], free_mib, required_mib)
            return 1
        candidate.pop("pending_reason", None)
        run_dir = KEV_RUNS_ROOT / candidate["name"]
        run_dir.mkdir(parents=True, exist_ok=True)
        out_ckpt = PROJECT_ROOT / candidate["checkpoint_path"]
        train_cmd = [str(PROJECT_ROOT / ".venv/bin/python"), "-u", "-m", "kev.train",
                     "--base", str(PROJECT_ROOT / "models/qwen3.5-4b-base"),
                     "--init_from", str(init), "--data", str(data), "--out", str(out_ckpt),
                     "--device", "cuda", "--dtype", "bf16", "--weights_dtype", "bf16",
                     "--batch", str(candidate.get("batch", "1")), "--accum", str(candidate.get("accum", "4")),
                     "--lr", str(candidate["lr"]), "--lora", str(candidate["lora"]),
                     "--epochs", str(candidate["epochs"]), "--seed", "42"] + candidate.get("extra_args", [])
        if candidate["candidate_id"] == "KEV-V8-C04":
            parameters = {**source_args, "lr": float(candidate["lr"]),
                          "init_from": str(init), "out": str(out_ckpt)}
            candidate["training_parameters"] = parameters
            candidate["training_parameters_source"] = str(training_config)
            train_cmd = [str(PROJECT_ROOT / ".venv/bin/python"), "-u", "-m", "kev.train"]
            for name, value in parameters.items():
                if value is not None:
                    train_cmd.extend([f"--{name}", str(value)])
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "external/kev")
        started = time.monotonic()
        with (run_dir / "train.log").open("a", encoding="utf-8") as log:
            proc = subprocess.Popen(train_cmd, cwd=str(PROJECT_ROOT), env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
            candidate.update(status="RUNNING", training_status="RUNNING", evaluation_status="NOT_EVALUATED",
                             training_kind="FORMAL_LORA", pid=proc.pid, started_at=_now())
            attempt = {"command": train_cmd, "pid": proc.pid, "started_at": candidate["started_at"]}
            candidate.setdefault("training_attempts", []).append(attempt)
            cursor = {"run_id": candidate["name"], "candidate_id": candidate["candidate_id"],
                      "pid": proc.pid, "status": "TRAINING", "step": None, "epoch": None, "loss": None}
            cursor_file = (out_ckpt if candidate["candidate_id"] == "KEV-V8-C09" else run_dir) / "cursor.json"
            cursor_file.parent.mkdir(parents=True, exist_ok=True)
            save_queue(queue)
            cursor_file.write_text(json.dumps(cursor, indent=2))
            for line in proc.stdout:
                log.write(line)
                log.flush()
                progress = _progress(line)
                if progress:
                    cursor.update(progress, updated_at=_now())
                    candidate.update(progress)
                    cursor_file.write_text(json.dumps(cursor, indent=2))
                    save_queue(queue)
            exit_code = proc.wait()
        cursor.update(status="COMPLETED" if exit_code == 0 else "FAILED", exit_code=exit_code, updated_at=_now())
        cursor_file.write_text(json.dumps(cursor, indent=2))
        attempt.update(exit_code=exit_code, duration_sec=time.monotonic() - started, finished_at=_now())
        refresh_training(candidate)
        if exit_code != 0:
            candidate.update(status="FAILED", failure_reason=f"Training exit code {exit_code}")
        save_queue(queue)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Continue the existing Kev candidate queue")
    parser.add_argument("--validation-only", action="store_true")
    parser.add_argument("--validation-device", default="auto", choices=("auto", "cpu", "cuda", "mps"))
    parser.add_argument("--validation-timeout", type=float, default=None, help="Seconds; omitted means no timeout")
    args = parser.parse_args(argv)
    return main_loop(args.validation_only, args.validation_device, args.validation_timeout)


if __name__ == "__main__":
    sys.exit(main())
