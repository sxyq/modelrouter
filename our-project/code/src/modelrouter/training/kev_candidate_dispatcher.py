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
from collections import Counter
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
SOURCE_SHA = os.environ.get("MODELROUTER_SOURCE_SHA")

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
    queue = None
    if QUEUE_FILE.is_file():
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to read queue file: {e}")
    new_queue = queue is None
    if new_queue:
        queue = copy.deepcopy(DEFAULT_CANDIDATES)
    for candidate in queue:
        if (candidate["candidate_id"] == "KEV-V8-C09"
                and candidate.get("status") in ("QUEUED", "PENDING", "WAITING_FOR_GPU")
                and not candidate.get("started_at") and not candidate.get("training_attempts")):
            candidate["pilot_checkpoint_path"] = f"runs/{candidate['name']}/checkpoint"
            candidate["checkpoint_path"] = f"runs/{candidate['name']}/formal_run"
            candidate["training_kind"] = "FORMAL_LORA"
            config_path = PROJECT_ROOT / "our-project/data/configs/training/KEV-V8-EXT-01.json"
            if config_path.is_file():
                config = json.loads(config_path.read_text(encoding="utf-8"))
                candidate["init_from"] = config["init_from"]
                for name, value in config["training_knobs"].items():
                    candidate["lora" if name == "lora_rank" else name] = str(value)
                candidate["extra_args"] = ["--checkpointing", "1", "--max_state", "384"]
                material = PROJECT_ROOT / "data/kev/v8_extension/materialization.json"
                if material.is_file():
                    candidate["materialization"] = json.loads(material.read_text())
                typed_material = PROJECT_ROOT / "data/kev/v8_extension/materialization_typed_auxiliary.json"
                if typed_material.is_file():
                    candidate["materialization"] = json.loads(typed_material.read_text())
                    candidate["data_path"] = str(Path(candidate["materialization"]["data_paths"]["train"]).relative_to(PROJECT_ROOT))
                    candidate["coverage_analysis"] = candidate["materialization"]
                    candidate["retention_group"] = "V8_EXTENSION"
                    candidate["research_scope"] = "New observed S2/S3 auxiliary targets; no repeated C03 S1 or unselected-model outcome labels"
                candidate["configuration_source"] = str(config_path)
    if new_queue:
        save_queue(queue)
    return queue

def save_queue(queue: List[Dict[str, Any]]):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    for path, payload in ((QUEUE_FILE, queue), (QUEUE_FILE.with_name(LEDGER_FILE.name), {
        "updated_at": _now(), "candidates": [{k: c.get(k) for k in (
            "candidate_id", "name", "status", "training_status", "evaluation_status",
            "pending_reason", "failure_reason", "recipe", "training_attempts", "evaluation_attempts",
            "training_metrics", "metrics", "comparison_to_c03", "selection", "retention",
            "checkpoint_path", "init_from", "coverage_analysis") } for c in queue]})):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(path)


def complete_candidate_plan(queue):
    """Add the already defined C-series slots without changing executed recipes."""
    template = copy.deepcopy(DEFAULT_CANDIDATES[2])
    plans = [
        ("KEV-V8-C06", "KEV-V8-ABL-FULLSTATE", "data/kev/公开数据/train_fullstate.jsonl", "16", "2e-5",
         "Eight real state fields are not available in the current typed training records"),
        ("KEV-V8-C08", "KEV-V8-ABL-LORA32", "data/kev/公开数据/train.jsonl", "32", "1e-5", None),
        ("KEV-V8-C10", "KEV-V8-S1-W2", "data/kev/公开数据/train.jsonl", "16", "2e-5", None),
    ]
    for cid, name, data, rank, lr, reason in plans:
        if any(c["candidate_id"] == cid for c in queue):
            continue
        item = {**copy.deepcopy(template), "candidate_id": cid, "name": name,
                "data_path": data, "lora": rank, "lr": lr, "status": "PENDING" if reason else "QUEUED",
                "checkpoint_path": f"runs/{name}/checkpoint", "seed": 42}
        item["description"] = name
        if reason:
            item.update(pending_reason=reason, material_status="PENDING")
        if cid == "KEV-V8-C10":
            item["question_loss_weights"] = {"model_choice": 2.0}
            item["retention_group"] = "S1_WEIGHT_ABLATION"
            item.update(status="PENDING", material_status="PENDING",
                        pending_reason="Original train contains 35,645 ROUTE-001/002 rows excluded by current policy and 17 TRA-004 rows outside the legal source set; difficulty_tier is historical auxiliary supervision")
        queue.append(item)
    if not any(c["candidate_id"] == "KEV-V8-C11" for c in queue):
        queue.append({"candidate_id": "KEV-V8-C11", "name": "KEV-V8-VAL-BEST",
                      "candidate_kind": "SELECTION", "status": "PENDING",
                      "pending_reason": "Selection uses comparable completed Val results; no new training"})
    queue.sort(key=lambda c: c["candidate_id"])
    save_queue(queue)


def record_recipe(candidate, command):
    init = PROJECT_ROOT / candidate["init_from"]
    config = init / "training_config.json"
    parent = json.loads(config.read_text()) if config.is_file() else {}
    data = PROJECT_ROOT / candidate["data_path"]
    upstream = subprocess.run(["git", "-C", str(PROJECT_ROOT / "external/kev"), "rev-parse", "HEAD"],
                              capture_output=True, text=True)
    candidate["recipe"] = {
        "run_id": candidate["name"], "candidate_id": candidate["candidate_id"],
        "source_git_sha": SOURCE_SHA, "upstream_git_sha": upstream.stdout.strip() or None,
        "base_model": "models/qwen3.5-4b-base", "base_revision": parent.get("base_revision"),
        "init_from": candidate["init_from"], "parent_init_source": parent.get("init_source"),
        "data_path": candidate["data_path"], "data_bytes": data.stat().st_size if data.is_file() else None,
        "data_identity": candidate.get("coverage_analysis"),
        "validation_set": FIXED_VAL_PATH, "test_used": False,
        "command": command, "question_loss_weights": candidate.get("question_loss_weights", {}),
        "loss_formula": "mean(weight[qid] * official_question_loss) * variant_share; unchanged record normalization",
        "checkpoint_path": candidate["checkpoint_path"],
        "retraining": "Use the recorded command and same initialization/data; numeric equality is not promised",
        "unrecorded_data_digest": "N/A; no new content digest was computed",
    }


def train_with_question_weights(candidate_id, train_args):
    """Use the official main loop with a per-question loss multiplier."""
    from kev import train
    candidate = next(c for c in load_queue() if c["candidate_id"] == candidate_id)
    weights = candidate["question_loss_weights"]
    exposure = Counter()
    official_loss, official_write = train.question_loss, train.write_json
    def question_loss(logits, question, *args, **kwargs):
        qid = question["qid"]
        exposure[qid] += 1
        return official_loss(logits, question, *args, **kwargs) * weights.get(qid, 1.0)
    def write_json(path, value):
        if Path(path).name in ("training_config.json", "training_metrics.json"):
            if Path(path).name == "training_config.json":
                candidate["recipe"].update(official_args=value["args"],
                                           init_source=value.get("init_source"), base_revision=value.get("base_revision"))
            value = {**value, "modelrouter_source_sha": SOURCE_SHA,
                     "question_loss_weights": weights, "question_exposure": dict(exposure),
                     "recipe": candidate["recipe"]}
        return official_write(path, value)
    train.question_loss, train.write_json = question_loss, write_json
    sys.argv = ["kev.train", *train_args]
    train.main()


def scientific_selection(queue):
    selection = next((c for c in queue if c.get("candidate_kind") == "SELECTION"), None)
    if selection is None:
        return
    candidates = [c for c in queue if c.get("status") == "COMPLETED"
                  and c.get("metrics", {}).get("evaluation_status") == "EVALUATED"
                  and (c["candidate_id"] == "KEV-V8-C03"
                       or c.get("comparison_to_c03", {}).get("status") == "COMPARABLE")]
    outstanding = [c["candidate_id"] for c in queue if c.get("candidate_kind") != "SELECTION"
                   and c.get("status") != "COMPLETED"]
    scored = [c for c in candidates if c.get("selection", {}).get("score") is not None]
    best_score = min(scored, key=lambda c: (-c["selection"]["score"], c["metrics"]["clean"]["nll"],
                                           -c["metrics"]["clean"]["acc"], c["candidate_id"])) if scored else None
    selection.update(status="PENDING" if outstanding else "COMPLETED",
                     training_status="NOT_APPLICABLE", selection={
                         "observed_at": _now(), "outstanding": outstanding,
                         "best_accuracy": max(candidates, key=lambda c: (c["metrics"]["clean"]["acc"], c["candidate_id"]))["candidate_id"] if candidates else None,
                         "best_nll": min(candidates, key=lambda c: (c["metrics"]["clean"]["nll"], c["candidate_id"]))["candidate_id"] if candidates else None,
                         "best_score": best_score["candidate_id"] if best_score else None,
                         "selected_checkpoint_path": best_score["checkpoint_path"] if best_score else None,
                         "new_training": False})
    save_queue(queue)

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
        if metrics.get("recipe"):
            candidate["recipe"] = metrics["recipe"]
        elif "recipe" not in candidate:
            config_file = PROJECT_ROOT / candidate["checkpoint_path"] / "training_config.json"
            config = json.loads(config_file.read_text()) if config_file.is_file() else {}
            candidate["recipe"] = {"run_id": candidate["name"], "candidate_id": candidate["candidate_id"],
                "source_git_sha": config.get("modelrouter_source_sha"), "official_args": config.get("args"),
                "init_source": config.get("init_source"), "base_revision": config.get("base_revision"),
                "data_path": candidate["data_path"], "validation_set": FIXED_VAL_PATH,
                "checkpoint_path": candidate["checkpoint_path"], "historical_identity": "Only existing metadata is used; unrecorded source/data identifiers remain N/A"}
        config_file = PROJECT_ROOT / candidate["checkpoint_path"] / "training_config.json"
        if config_file.is_file():
            candidate["training_parameters"] = json.loads(config_file.read_text()).get("args", {})
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


def update_retention(queue, apply=False):
    from router_data.checkpoint_retention import evaluate_kev_retention
    result = evaluate_kev_retention(queue, project_root=PROJECT_ROOT, apply=apply, persist=save_queue,
        protected_paths=("models/kev-4b-adapter", "models/qwen3.5-4b-base"))
    scientific_selection(queue)
    logger.info("Kev retention: released %s bytes", result["released_bytes"])
    return result


def main_loop(validation_only=False, validation_device="auto", validation_timeout=None, wait_for_resources=False,
              apply_retention=False):
    logger.info("=== Kev candidate queue ===")
    deferred = set()
    while True:
        queue = load_queue()
        candidate = next((c for c in queue if c.get("candidate_kind") != "SELECTION"
                          and c.get("status") != "COMPLETED" and c["candidate_id"] not in deferred), None)
        if candidate is None:
            if apply_retention:
                update_retention(queue, apply=True)
            else:
                scientific_selection(queue)
            return 1 if deferred else 0
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
            if candidate["candidate_id"] in ("KEV-V8-C03", "KEV-V8-C04"):
                return 1
            deferred.add(candidate["candidate_id"])
            continue
        if candidate["training_status"] == "COMPLETED":
            ok = validate_candidate(candidate, queue, validation_device, validation_timeout)
            if ok and apply_retention:
                update_retention(queue, apply=True)
            if validation_only:
                return 0 if ok else 1
            if not ok:
                deferred.add(candidate["candidate_id"])
            continue
        if validation_only:
            logger.info("%s has no completed training to validate", candidate["candidate_id"])
            return 1
        if candidate.get("status") == "RUNNING" or candidate["training_status"] == "FAILED":
            candidate.update(status="FAILED", failure_reason="Training exited without successful completion")
            save_queue(queue)
            deferred.add(candidate["candidate_id"])
            continue
        if candidate.get("material_status") == "PENDING":
            deferred.add(candidate["candidate_id"])
            continue
        data = PROJECT_ROOT / candidate["data_path"]
        if candidate["candidate_id"] == "KEV-V8-C09" and candidate.get("materialization", {}).get("configuration_status") == "PARTIAL_MATERIAL_NOT_FULL_C09":
            candidate.update(status="PENDING", configuration_status="PARTIAL_MATERIAL",
                             pending_reason="Arena export contains only existing C03 training records; configured cache/outcome typed targets unavailable")
            save_queue(queue)
            deferred.add(candidate["candidate_id"])
            continue
        if not data.is_file():
            candidate.update(status="PENDING", pending_reason=f"Missing training data: {data}")
            save_queue(queue)
            deferred.add(candidate["candidate_id"])
            continue
        init = PROJECT_ROOT / candidate["init_from"]
        if not init.exists():
            candidate.update(status="PENDING", pending_reason=f"Missing init_from: {init}")
            save_queue(queue)
            deferred.add(candidate["candidate_id"])
            continue
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
            deferred.add(candidate["candidate_id"])
            continue
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
            if wait_for_resources:
                time.sleep(30)
                continue
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
                     "--epochs", str(candidate["epochs"]), "--seed", str(candidate.get("seed", 42))] + candidate.get("extra_args", [])
        if candidate["candidate_id"] == "KEV-V8-C04":
            parameters = {**source_args, "lr": float(candidate["lr"]),
                          "init_from": str(init), "out": str(out_ckpt)}
            candidate["training_parameters"] = parameters
            candidate["training_parameters_source"] = str(training_config)
            train_cmd = [str(PROJECT_ROOT / ".venv/bin/python"), "-u", "-m", "kev.train"]
            for name, value in parameters.items():
                if value is not None:
                    train_cmd.extend([f"--{name}", str(value)])
        if candidate.get("question_loss_weights"):
            train_cmd = [str(PROJECT_ROOT / ".venv/bin/python"), "-u", str(Path(__file__).resolve()),
                         "--train-candidate", candidate["candidate_id"], "--", *train_cmd[4:]]
        record_recipe(candidate, train_cmd)
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join((str(PROJECT_ROOT), str(PROJECT_ROOT / "external/kev")))
        started = time.monotonic()
        with (run_dir / "train.log").open("a", encoding="utf-8") as log:
            proc = subprocess.Popen(train_cmd, cwd=str(PROJECT_ROOT), env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
            candidate.update(status="RUNNING", training_status="RUNNING", evaluation_status="NOT_EVALUATED",
                             training_kind="FORMAL_LORA", pid=proc.pid, started_at=_now(), code_commit=SOURCE_SHA)
            attempt = {"command": train_cmd, "pid": proc.pid, "started_at": candidate["started_at"]}
            candidate.setdefault("training_attempts", []).append(attempt)
            cursor = {"run_id": candidate["name"], "candidate_id": candidate["candidate_id"],
                      "pid": proc.pid, "status": "TRAINING", "step": None, "epoch": None, "loss": None}
            cursor_file = (out_ckpt if candidate["candidate_id"] == "KEV-V8-C09" else run_dir) / "cursor.json"
            save_queue(queue)
            if cursor_file.parent.is_dir():
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
        if cursor_file.parent.is_dir():
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
    parser.add_argument("--train-candidate", help="Official trainer with the candidate's question loss weights")
    parser.add_argument("--apply-retention", action="store_true", help="Apply authorized Kev retention after completed fixed Val")
    parser.add_argument("train_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.train_candidate:
        return train_with_question_weights(args.train_candidate, args.train_args[1:] if args.train_args[:1] == ["--"] else args.train_args)
    if not args.validation_only:
        queue = load_queue()
        for candidate in queue:
            if candidate.get("status") == "COMPLETED" and candidate.get("candidate_kind") != "SELECTION":
                refresh_training(candidate)
        complete_candidate_plan(queue)
        update_retention(queue, apply=args.apply_retention)
    return main_loop(args.validation_only, args.validation_device, args.validation_timeout,
                     **({"wait_for_resources": True, "apply_retention": args.apply_retention} if not args.validation_only else {}))


if __name__ == "__main__":
    sys.exit(main())
