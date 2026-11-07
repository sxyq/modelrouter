"""Training research reports and ETA calculations."""
from __future__ import annotations

import json
import math
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

from modelrouter.telemetry.common import (
    PROJECT_ROOT, atomic_json, now_iso, public_training_record, read_json, relative,
)

def training_eta(history, plans, live, plan_rows):
    """Estimate the original queue from recorded wall time and configured exposure."""
    root_runs = [r for r in history["runs"] if r["root"].startswith("runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/")]
    samples = []
    for run in root_runs:
        records, seconds = run["exposure"].get("trained_records"), run.get("training_seconds")
        if run["protocol"] == "MR-FULL-GRADED-P0-DATA-REPAIR-v1" and run["status"] in ("COMPLETED", "EARLY_STOPPED") and records and seconds and seconds > 0:
            samples.append({"run_id": run["run_id"], "mode": run["sampling"]["mode"],
                            "supervision": run.get("supervision_classes"), "records_per_second": records / seconds,
                            "records": records, "wall_seconds": seconds, "source": run["source"]})
    full_rates = [s["records_per_second"] for s in samples if s["mode"] == "FULL_COVERAGE" and s["supervision"] == ["S1", "S2", "S3"]]
    matrix_rates = [s["records_per_second"] for s in samples if s["mode"] == "MATRIX_RATIO"]
    val_samples = [e["validation_seconds"] for r in root_runs if r.get("supervision_classes") == ["S1", "S2", "S3"]
                   for e in r.get("epoch_records", []) if e.get("validation_seconds") is not None]
    current = {}
    for family in ("laya", "kev"):
        observed = live.get(family) or {}
        step, total = observed.get("step"), observed.get("total_steps")
        rate = observed.get("samples_per_s")
        method = "recent observed records/s under current GPU sharing"
        if family == "laya":
            remaining = None
            spec = (plans.get("full_coverage") or {}).get(observed.get("run_id"), {})
            census = (history.get("data_census") or {}).get("layers", {})
            total_records = sum(sum(census.get(layer, {}).get(s, 0) for s in spec.get("supervision_classes", []))
                                * fraction for layer, fraction in spec.get("layer_fractions", {}).items()) * spec.get("epochs", 2)
            if rate and observed.get("consumed_records") is not None and total_records:
                remaining = max(0, total_records - observed["consumed_records"]) / rate
            elif step and total and observed.get("elapsed_s"):
                remaining = max(0, total - step) * observed["elapsed_s"] / step
                method = "current process elapsed/optimizer-step; includes initialization"
            remaining_epochs = max(0, spec.get("epochs", 2) - observed.get("epoch_index", 0)) if observed.get("epoch_index") is not None else None
            validation = median(val_samples) * remaining_epochs if val_samples and remaining_epochs is not None else None
        else:
            proc = (live.get("process") or {}).get("kev") or {}
            batch, accum = proc.get("batch"), proc.get("accum")
            remaining = max(0, total - step) * int(batch) * int(accum) / rate if (
                rate and step is not None and total is not None and batch and accum) else None
            method = "upstream cumulative seconds/record × configured batch × accumulation"
            run = next((r for r in history["runs"] if r["family"] == "kev" and r["run_id"] == observed.get("run_id")), {})
            fixed_val = next((v for v in run.get("validation", []) if v["stream"] == "clean"), {})
            if not fixed_val and proc.get("train_pid"):
                fixed_val = next((v for r in history["runs"] if r["family"] == "kev" and r["protocol"] == "KEV_FORMAL_LORA"
                                  for v in r.get("validation", []) if v["stream"] == "clean"
                                  and str(v.get("validation_set", "")).endswith("data/kev/公开数据/val.jsonl")), {})
            timed = [{"run_id": r["run_id"], "seconds": r["evaluation_seconds"], "source": v["source"]}
                     for r in history["runs"] if r["family"] == "kev" and r["protocol"] == run.get("protocol")
                     and r.get("evaluation_status") == "EVALUATED" and r.get("evaluation_seconds")
                     for v in r.get("validation", []) if v["stream"] == "clean"
                     and fixed_val.get("validation_set") is not None and fixed_val.get("items") is not None
                     and v.get("validation_set") == fixed_val["validation_set"] and v.get("items") == fixed_val["items"]]
            validation = median(t["seconds"] for t in timed) if timed else None
            completed = observed.get("status") == "COMPLETED" and not observed.get("is_training") and not proc.get("train_pid")
            if completed:
                remaining, validation = 0, 0
                method = "completed run; no active training worker"
        current[family] = {"run_id": observed.get("run_id"), "status": observed.get("status"),
            "evaluation_status": observed.get("evaluation_status"),
            "remaining_training_seconds": remaining, "validation_seconds": validation,
            "estimated_finish_at": datetime.fromtimestamp(time.time() + remaining + (validation or 0), timezone.utc).isoformat() if remaining is not None and not (family == "kev" and completed) else None,
            "method": method, "validation_in_finish_estimate": validation is not None and not (family == "kev" and completed),
            "validation_method": "same fixed Laya Val timed matrix epochs as a proxy; all remaining epochs" if family == "laya" else
                f"median of {len(timed)} same fixed Kev Val observed durations" + ("; completed run has no pending Val time" if completed else "")}
        if family == "kev":
            current[family]["validation_samples"] = timed
    groups = []
    pending = []
    cpu_times = [p["materialization_audit"]["materialization_seconds"] for p in (plans.get("matrix") or {}).values()
                 if (p.get("materialization_audit") or {}).get("materialization_seconds") is not None]
    census = (history.get("data_census") or {}).get("layers", {})
    for name, category in (("F08–F16", "full_coverage"), ("纯 S3", "full_coverage"), ("原矩阵", "matrix")):
        selected = [p for p in plan_rows if p["category"] == category and p["status"] in ("ELIGIBLE", "CPU_MATERIALIZED")
                    and (category == "matrix" or (p["run_id"].endswith("_S3") if name == "纯 S3" else not p["run_id"].endswith("_S3")))]
        records = 0
        task_times = []
        for p in selected:
            spec = plans[category][p["run_id"]]
            if category == "matrix":
                counts = spec.get("materialized_counts")
                if counts is None:
                    budget = (plans.get("matrix_generation") or {}).get("max_items_per_class")
                    weights = spec.get("ratios") or []
                    if budget is None or not weights:
                        pending.append({"group": p["run_id"], "count": 1, "reason": "recorded materialization budget unavailable"})
                        continue
                    counts = {s: min((spec.get("counts") or {}).get(s, 0), max(1, int(budget * w / sum(weights))))
                              for s, w in zip(spec.get("supervision_classes", []), weights)}
                task_records = sum(counts.values()) * spec.get("epochs", 2)
                records += task_records
                comparable_rates = [s["records_per_second"] for s in samples if s["mode"] == "MATRIX_RATIO"
                                    and s["supervision"] == spec.get("supervision_classes")]
                if comparable_rates:
                    task_times.append((task_records / median(comparable_rates), task_records / max(comparable_rates), task_records / min(comparable_rates)))
            else:
                records += sum(math.floor(sum(census.get(layer, {}).get(s, 0) for s in spec.get("supervision_classes", [])) * fraction)
                               for layer, fraction in spec.get("layer_fractions", {}).items()) * spec.get("epochs", 2)
        rates = matrix_rates if category == "matrix" else full_rates
        rate = median(rates) if rates else None
        wall = records / rate if rate else None
        if category == "matrix" and len(task_times) == len(selected):
            wall = sum(t[0] for t in task_times)
            rate = records / wall if wall else None
        needs_cpu = sum(not p["materialized"] for p in selected) if category == "matrix" else 0
        cpu_seconds = needs_cpu * median(cpu_times) if cpu_times else None
        groups.append({"group": name, "count": len(selected), "run_ids": [p["run_id"] for p in selected],
            "remaining_records": records, "training_seconds": wall, "validation_seconds": None,
            "materialization_seconds": cpu_seconds, "records_per_second": rate,
            "method": "configured full-pass exposure / same-protocol wall throughput; matrix weighted by supervision; validation included" + ("; tri-supervision full runs are a speed surrogate for S3-only" if name == "纯 S3" else "") + ("; fractional records are approximate expectations, unit-based selection may differ" if name == "F08–F16" else ""),
            "fast_seconds": sum(t[1] for t in task_times) if task_times and len(task_times) == len(selected) else records / max(rates) if rates else None,
            "slow_seconds": sum(t[2] for t in task_times) if task_times and len(task_times) == len(selected) else records / min(rates) if rates else None,
            "needs_materialization": needs_cpu})
    pending += [{"group": p["run_id"], "count": 1, "reason": p["reason"]} for p in plan_rows if p["status"] == "PENDING_PARENT"]
    kev_plans = history["experiment_plans"]["kev_queue"]
    queued_kev = [c for c in kev_plans if c["status"] == "QUEUED" and c.get("coverage_analysis")]
    coverage_material = read_json(PROJECT_ROOT / "data/kev/v8_extension/materialization_coverage.json", {})
    queued_kev += [{"candidate_id": "KEV-V8-" + rid, "coverage_analysis": run}
                   for rid, run in coverage_material.get("runs", {}).items() if run["status"] == "READY"
                   and not any(c["candidate_id"] == "KEV-V8-" + rid for c in kev_plans)]
    kev_rates = [r["terminal_metrics"]["records_seen"] / r["terminal_metrics"]["wall_seconds"]
                 for r in history["runs"] if r["family"] == "kev" and r["protocol"] == "KEV_FORMAL_LORA"
                 and r.get("terminal_metrics", {}).get("records_seen") and r["terminal_metrics"].get("wall_seconds")]
    val_times = [r["evaluation_seconds"] for r in history["runs"] if r["family"] == "kev"
                 and r["protocol"] == "KEV_FORMAL_LORA" and r.get("evaluation_status") == "EVALUATED"
                 and r.get("evaluation_seconds")]
    if queued_kev:
        total_records = sum(sum(c["coverage_analysis"]["splits"]["train"]["records_by_class"].values()) for c in queued_kev)
        validation_seconds = len(queued_kev) * median(val_times) if val_times else None
        groups.append({"group": "Kev合法typed配比", "count": len(queued_kev),
            "run_ids": [c["candidate_id"] for c in queued_kev], "remaining_records": total_records,
            "training_seconds": total_records / median(kev_rates) if kev_rates else None,
            "validation_seconds": validation_seconds, "materialization_seconds": 0, "needs_materialization": 0,
            "records_per_second": median(kev_rates) if kev_rates else None,
            "fast_seconds": total_records / max(kev_rates) + (validation_seconds or 0) if kev_rates else None,
            "slow_seconds": total_records / min(kev_rates) + (validation_seconds or 0) if kev_rates else None,
            "method": "legal material counts / observed formal Kev training throughput plus one original fixed Val per run; target mix may change throughput"})
    for candidate in history["experiment_plans"]["kev_queue"]:
        if candidate["status"] not in ("COMPLETED", "RUNNING", "TRAINING") and candidate not in queued_kev:
            pending.append({"group": candidate["candidate_id"], "count": 1,
                            "reason": candidate.get("pending_reason") or candidate.get("failure_reason") or "candidate method/material/initialization unresolved; no launch assumed"})
    live_seconds = [c["remaining_training_seconds"] + (c["validation_seconds"] or 0)
                    for c in current.values() if c["remaining_training_seconds"] is not None]
    cpu_total = sum(g["materialization_seconds"] or 0 for g in groups)
    wall = sum((g["training_seconds"] or 0) + (g["validation_seconds"] or 0) for g in groups) + max(live_seconds, default=0) + cpu_total
    low = sum(g["fast_seconds"] or 0 for g in groups) + max(live_seconds, default=0)
    high = sum(g["slow_seconds"] or 0 for g in groups) + sum(live_seconds) + cpu_total
    return {"observed_at": live.get("collected_at_iso", now_iso()), "current": current, "groups": groups,
        "totals": {"serial_wall_seconds": wall, "lower_bound_wall_seconds": low, "range_seconds": [low, high],
                   "estimated_finish_at": datetime.fromtimestamp(time.time() + wall, timezone.utc).isoformat(),
                   "planned_executable_runs": sum(g["count"] for g in groups), "measured_gpu_active_hours": None,
                   "unestimated_cpu_materialization": sum(g["needs_materialization"] for g in groups if g["materialization_seconds"] is None),
                   "estimated_cpu_materialization_seconds": cpu_total if cpu_times else None},
        "blocked": pending, "throughput_samples": samples,
        "assumptions": ["Wall-time GPU-hours are a scheduling estimate, not measured GPU-active time or USD cost.",
            "Current two runs overlap on one GPU; their remaining time is max(), future Laya runs remain sequential.",
            "Completed-run wall throughput includes validation and recorded pauses; no extra validation time is added twice.",
            "CPU materialization uses recorded original-entry durations when available; one sample cannot identify task-to-task variation. Unrecorded switching time remains excluded.",
            "Fast/slow range uses observed same-mode extrema; it is a scenario range, not a statistical confidence interval.",
            "Unresolved parent weights and Kev candidates have no completion date; paper completion is not estimated."]}


def write_training_research_report(history, project_root=PROJECT_ROOT, live=None):
    """Summarize the existing observations; never launch training or read Test."""
    root = Path(project_root)
    plans = read_json(root / "our-project/dashboard" / history["experiment_plans"]["index"], {})
    runs = history["runs"]
    queue = history["experiment_plans"]["laya_queue"]
    by_id = {r["run_id"]: r for r in runs if r["root"].startswith("runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/")}
    plan_rows = []
    for category in ("full_coverage", "matrix"):
        for rid, plan in (plans.get(category) or {}).items():
            observed = by_id.get(rid)
            reason = (queue.get("skipped_runs") or {}).get(rid)
            state = observed["status"] if observed and observed["execution_evidence"] else (
                "SKIPPED" if reason else plan.get("status", "PLANNED"))
            failed = (queue.get("failed_runs") or {}).get(rid) or {}
            if not observed and failed.get("attempts", 0) >= 2:
                state, reason = "FAILED", failed
            parent_id = plan.get("parent_run_id")
            if not observed and parent_id:
                parent = by_id.get(parent_id)
                valid = [v for v in (parent or {}).get("validation", []) if v["stream"] == "S1" and v.get("loss") is not None]
                best = min(valid, key=lambda v: v["loss"]) if valid else None
                physical = any(c["physical"] and best and c["epoch"] == best["epoch"] for c in (parent or {}).get("checkpoints", []))
                if not parent or parent["status"] not in ("COMPLETED", "EARLY_STOPPED") or not physical:
                    state, reason = "PENDING_PARENT", "required completed parent best-epoch weights unavailable: " + parent_id
            plan_rows.append({"category": category, "run_id": rid, "status": state,
                "reason": reason or plan.get("eligibility_reason"), "supervision_classes": plan.get("supervision_classes"),
                "ratios": plan.get("ratios"), "layers": plan.get("layers"),
                "counts": plan.get("counts"), "materialized": plan.get("materialized"),
                "parent_run_id": plan.get("parent_run_id"), "parent_checkpoint_id": plan.get("parent_checkpoint_id")})
    observations = []
    for run in runs:
        if not run["execution_evidence"] and run["origin"] != "IMPORTED_ADAPTER":
            continue
        primary = ("S1" if "S1" in {v["stream"] for v in run["validation"]} else
                   next(iter(run.get("supervision_classes") or []), "S1")) if run["family"] == "laya" else (
                       "clean" if any(v["stream"] == "clean" for v in run["validation"]) else "choice")
        candidates = [v for v in run["validation"] if v["stream"] == primary and v.get("loss") is not None]
        chosen = min(candidates, key=lambda v: v["loss"]) if candidates else None
        accuracy_candidates = [v for v in run["validation"] if v["stream"] == primary and v.get("accuracy") is not None]
        best_accuracy = max(accuracy_candidates, key=lambda v: v["accuracy"]) if accuracy_candidates else None
        values = [v for v in run["validation"] if chosen and v["epoch"] == chosen["epoch"]]
        cp = next((c for c in run["checkpoints"] if chosen and c["epoch"] == chosen["epoch"]), None)
        if run["family"] == "kev" and chosen:
            cp = next(iter(run["checkpoints"]), None)
        accuracy_cp = next((c for c in run["checkpoints"] if best_accuracy and c["epoch"] == best_accuracy["epoch"]), None)
        detail = read_json(root / "our-project/dashboard" / run["curve_path"], {})
        loss_points = [p for p in detail.get("points", []) if isinstance(p.get("train_loss"), (int, float)) and math.isfinite(p["train_loss"])]
        epochs = run.get("epoch_records", [])
        train_epochs = [e for e in epochs if isinstance(e.get("train_loss"), (int, float)) and math.isfinite(e["train_loss"])]
        stage = run.get("stage") or run.get("training_kind")
        meaning = {"ALGN": "按受控比例抽样，比较监督组合与训练预算；与全材料覆盖分别解释。",
                   "MATRIX": "原矩阵的层级、质量、抽样、监督配比对照；仅同材料和预算支持配比比较。",
                   "N_SERIES": "早期训练规模与参数探索；与现行输入协议分别解释。",
                   "COURSE": "从已完成父模型接续，比较课程次序；初始化与额外训练共同改变。",
                   "FORMAL_LORA": "官方 Kev typed state/questions 正式 LoRA；固定项目 Val 单独比较。",
                   "SHORT_TRAINING": "短训练用于通路验证，不能视为正式模型能力。",
                   "IMPORTED": "上游导入资产，不计为本地新增训练。"}.get(stage,
                       "全材料层级/规模对照。" if run["sampling"]["mode"] == "FULL_COVERAGE" else "历史探索或扩展 Pilot；协议与正式训练分别解释。")
        observations.append({"run_id": run["run_id"], "family": run["family"], "protocol": run["protocol"],
            "key": run["key"], "origin": run["origin"], "training_kind": run["training_kind"],
            "design": {"description": run.get("design_description"), "interpretation": meaning,
                       "variables": {"layers": run.get("layers"), "layer_fractions": run.get("layer_fractions"),
                                     "sampling": run.get("sampling"), "config": run.get("config"), "initialization": run.get("initialization")}},
            "status": run["status"], "stage": run.get("stage"), "supervision": run.get("supervision_classes"),
            "sampling": run.get("sampling"), "initialization": run.get("initialization"),
            "config": run.get("config"), "exposure": run["exposure"], "epochs": run["epochs"],
            "training_seconds": run.get("training_seconds"), "best_loss_epoch": chosen,
            "best_accuracy_epoch": best_accuracy, "best_accuracy_physical": accuracy_cp.get("physical") if accuracy_cp else None,
            "best_train_loss_epoch": min(train_epochs, key=lambda e: e["train_loss"]).get("epoch") if train_epochs else None,
            "epoch_records": epochs,
            "evaluation_seconds": run.get("evaluation_seconds"), "evaluation_status": run.get("evaluation_status"),
            "failure_reason": run.get("failure_reason"),
            "loss_trajectory": {"points": len(loss_points), "granularity": run["curve_granularity"],
                                "first": loss_points[0]["train_loss"] if loss_points else None,
                                "last": loss_points[-1]["train_loss"] if loss_points else None,
                                "minimum": min(p["train_loss"] for p in loss_points) if loss_points else None,
                                "maximum_step": max((p.get("step") or 0 for p in detail.get("points", [])), default=0) or None,
                                "segments": len({str(p.get("segment")) for p in detail.get("points", [])})},
            "primary_stream": primary, "validation_all_epochs": run["validation"],
            "loss_definition": run.get("loss_definition"), "validation_coverage": run.get("validation_coverage"),
            "comparison_to_c03": run.get("comparison_to_c03"),
            "candidate_by_stream": run.get("candidate_by_stream"),
            "independent_units_by_stream": run.get("independent_units_by_stream"),
            "materialization_audit": run.get("materialization_audit"),
            "code_commit": run.get("code_commit"), "command": run.get("command"),
            "data_path": run.get("data_path"), "started_at": run.get("started_at"), "finished_at": run.get("finished_at"),
            "training_seconds_scope": run.get("training_seconds_scope", "recorded upstream training wall time"),
            "validation_at_selected_epoch": values, "selected_epoch_physical": cp.get("physical") if cp else None,
            "source": run["source"], "curve_path": run["curve_path"], "checkpoints": run["checkpoints"],
            "actual_cost_usd": None})
    for row in observations:
        trajectory = {}
        for stream in sorted({v["stream"] for v in row["validation_all_epochs"]}):
            values = [v for v in row["validation_all_epochs"] if v["stream"] == stream]
            first, last = values[0], values[-1]
            trajectory[stream] = {"first_epoch": first.get("epoch"), "last_epoch": last.get("epoch"),
                "changes": {k: last[k] - first[k] if len(values) > 1 and isinstance(last.get(k), (int, float)) and isinstance(first.get(k), (int, float)) else None
                            for k in ("accuracy", "loss", "nll", "brier", "ece")},
                "interpretation": "within-run observed change, not isolated causal effect"}
        row["validation_changes"] = trajectory
        peers = [r for r in observations if r["key"] != row["key"] and r["family"] == row["family"] and r["protocol"] == row["protocol"]
                 and r["best_loss_epoch"] and row["best_loss_epoch"]
                 and r["primary_stream"] == row["primary_stream"] and r["loss_definition"] == row["loss_definition"]
                 and r["best_loss_epoch"].get("validation_set") == row["best_loss_epoch"].get("validation_set")
                 and r["best_loss_epoch"].get("items") == row["best_loss_epoch"].get("items")
                 and r["design"]["variables"]["layers"] == row["design"]["variables"]["layers"]
                 and r["initialization"] == row["initialization"]]
        control = next((r for r in peers if r["supervision"] == ["S1"] and r["stage"] == row["stage"]), None)
        row["comparison"] = {"control_key": control["key"] if control else None,
            "accuracy_delta": row["best_loss_epoch"]["accuracy"] - control["best_loss_epoch"]["accuracy"] if control and row["best_loss_epoch"].get("accuracy") is not None and control["best_loss_epoch"].get("accuracy") is not None else None,
            "loss_delta": row["best_loss_epoch"]["loss"] - control["best_loss_epoch"]["loss"] if control else None,
            "stream": row["primary_stream"],
            "scope": "same model/protocol/Val/target/loss definition/layers/initialization; exposure, budget and selected epoch may differ"}
        has_physical = any(c["physical"] for c in row["checkpoints"])
        row["candidate_role"] = ("短训练或Pilot实体，正式能力待评测" if has_physical and row["training_kind"] in ("LORA_SMOKE", "POINTER_HEAD_PILOT") else
                                 "辅助目标实体，S1选模能力无实测" if has_physical and row["family"] == "laya" and row["primary_stream"] != "S1" else
                                 "可加载的离线候选，任务级能力待评测" if row["selected_epoch_physical"] else
                                 "可加载的其他Epoch候选，最低Loss实体不可用，指标按实际Epoch呈现" if has_physical else
                                 "历史消融或负结果；主Val最佳实体不可用" if row["best_loss_epoch"] else "证据不足，保留历史对象")
        row["missing_evidence"] = [label for label, missing in (
            ("逐监督梯度贡献", True), ("实付费用", True), ("独立任务成功率/完整Episode费用", True),
            ("完整训练耗时", row["training_seconds"] is None), ("主Val", row["best_loss_epoch"] is None),
            ("最佳Loss实体", not row["selected_epoch_physical"])) if missing]
    loadable = []
    trends = {}
    metric_fields = ("epoch", "step", "stream", "accuracy", "loss", "nll", "brier", "ece", "items", "validation_set", "source")
    for row in observations:
        for checkpoint in row["checkpoints"]:
            if not checkpoint["physical"]:
                continue
            validation = [{k: v.get(k) for k in metric_fields} for v in row["validation_all_epochs"] if v["epoch"] == checkpoint["epoch"]]
            loadable.append({"key": row["key"], "run_id": row["run_id"], "family": row["family"],
                "protocol": row["protocol"], "training_kind": row["training_kind"], "primary_stream": row["primary_stream"],
                "checkpoint_id": checkpoint["checkpoint_id"], "epoch": checkpoint["epoch"],
                "path": checkpoint["path"], "evidence": checkpoint["evidence"], "validation": validation,
                "primary_validation": next((v for v in validation if v["stream"] == row["primary_stream"]), None),
                "is_best_loss_epoch": bool(row["best_loss_epoch"] and checkpoint["epoch"] == row["best_loss_epoch"]["epoch"]),
                "is_best_accuracy_epoch": bool(row["best_accuracy_epoch"] and checkpoint["epoch"] == row["best_accuracy_epoch"]["epoch"]),
                "candidate_role": row["candidate_role"], "source": row["source"]})
        selected = row["best_loss_epoch"]
        if not selected or selected.get("validation_set") is None or selected.get("items") is None:
            continue
        identity = (row["family"], row["protocol"], json.dumps(selected["validation_set"], ensure_ascii=False, sort_keys=True),
                    row["primary_stream"], selected["items"], row["loss_definition"])
        group = trends.setdefault(identity, {"family": row["family"], "protocol": row["protocol"],
            "validation_set": selected["validation_set"], "stream": row["primary_stream"], "items": selected["items"],
            "loss_definition": row["loss_definition"], "observations": [],
            "scope": "same model/protocol/fixed Val/target/loss definition; descriptive history, budgets and initialization may differ"})
        group["observations"].append({"key": row["key"], "run_id": row["run_id"], "status": row["status"],
            "started_at": row["started_at"], "supervision": row["supervision"], "sampling": row["sampling"],
            "initialization": row["initialization"], "trained_records": row["exposure"].get("trained_records"),
            "training_seconds": row["training_seconds"], "best_loss_epoch": {k: selected.get(k) for k in metric_fields},
            "selected_epoch_physical": row["selected_epoch_physical"],
            "best_accuracy_epoch": {k: row["best_accuracy_epoch"].get(k) for k in metric_fields} if row["best_accuracy_epoch"] else None,
            "best_accuracy_physical": row["best_accuracy_physical"], "source": row["source"]})
    for group in trends.values():
        group["observations"].sort(key=lambda r: (r["started_at"] is None, r["started_at"] or "", r["run_id"]))
        group["order"] = "recorded start time; undated runs follow in Run ID order"
    def public(value):
        return public_training_record(value, root)
    result = public({"generated_at": now_iso(), "code_commit": os.environ.get("MODELROUTER_CODE_COMMIT"),
        "counts": history["counts"], "plans": plan_rows, "observations": observations,
        "loadable_candidates": loadable, "objective_trends": list(trends.values()),
        "retention": history["retention"], "comparisons": history["comparisons"],
        "kev_candidates": history["experiment_plans"]["kev_queue"], "data_census": history.get("data_census"),
        "laya_queue": {k: queue.get(k) for k in ("queue_status", "current_run", "next_run", "failed_runs", "blocked_runs")},
        "kev_materialization": read_json(root / "data/kev/v8_extension/materialization.json", {}),
        "kev_typed_auxiliary": read_json(root / "data/kev/v8_extension/materialization_typed_auxiliary.json", {}),
        "kev_coverage_material": read_json(root / "data/kev/v8_extension/materialization_coverage.json", {}),
        "selection": "One minimum primary validation Loss epoch per run; highest Accuracy epoch is independent; loadable candidates use their actual epoch metrics",
        "limitations": history["limitations"]})
    live = live if live is not None else read_json(root / "our-project/dashboard/live_status.json", {})
    result["live_observation"] = public({k: live.get(k) for k in ("collected_at_iso", "server_connected", "gpu", "process", "laya", "kev")})
    result["training_eta"] = public(training_eta(history, plans, live, plan_rows))
    result["continuation"] = {
        "laya_boundary_reload_requested": (root / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/.reload_queue_daemon").is_file(),
        "laya_order": [p["run_id"] for p in plan_rows if p["category"] == "full_coverage" and p["status"] in ("TRAINING", "ELIGIBLE")],
        "kev_boundary": "The original dispatcher owns training and Val; terminal results and pending reasons remain in the original records",
        "kev_retention_applied": any((c.get("retention") or {}).get("applied") for c in result["kev_candidates"]),
        "kev_pruned_weight_bytes": sum((c.get("retention") or {}).get("total_released_bytes", 0) for c in result["kev_candidates"]),
    }
    destination = root / "our-project/results/training"
    atomic_json(destination / "training_research.json", result)
    def cell(v):
        return "N/A" if v is None else json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    def table(headers, records):
        return ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] + [
            "| " + " | ".join(cell(v).replace("|", "/").replace("\n", " ") for v in record) + " |" for record in records]
    lines = ["# Laya / Kev 全历史训练研究报告", "", "生成时间：" + result["generated_at"], "",
        "本报告来自原 Run、Epoch、Cursor、训练日志、队列和权重目录；当前训练仍在执行，全部计划尚未完成。",
        "仅使用训练记录和项目 Val，不读取最终 Test。Loss 最佳 Epoch 与 Accuracy 最佳 Epoch分别识别；本表按主任务最低 Val Loss选择同一 Epoch，辅助成绩沿用该 Epoch。", "",
        "## 1. 历史对象与物理实体", ""]
    lines += table(["模型", "实际本地 Run", "结束 Run", "运行 Run", "导入资产", "Epoch", "版本", "实体", "Step/Chunk曲线", "Epoch曲线"], [
        [family, c["executed_runs"], c["completed_runs"], c["running_runs"], c["imported_assets"], c["recorded_epochs"], c["checkpoint_versions"], c["physical_checkpoints"], c["step_curve_runs"], c["epoch_only_runs"]]
        for family, c in result["counts"].items()])
    lines += ["", "旧五份实体：" + str(sum(bool(c["physical"]) for c in result["retention"]["old_core"])) + "/5。新池、课程父权重与恢复点分别见 JSON；缺失实体没有被恢复。", "",
        "## 2. 现有计划执行情况", ""]
    lines += table(["计划", "状态", "数量"], [[category, status, count] for category in ("full_coverage", "matrix")
        for status, count in sorted(Counter(p["status"] for p in plan_rows if p["category"] == category).items())])
    lines += ["", "全部计划 ID、组合、配比、层级、材料数量和原原因保存在 training_research.json 的 plans，未执行不代表完成。", "",
        "## 3. 同协议描述比较", "", "模型、协议、Val身份、问题数量与监督组合分别分组。组内仍可能包含数据量、初始化、预算和层级差异，排名不能解释为配比的因果效应。", ""]
    lines += table(["模型/协议", "Val/监督", "指标", "Run数", "最好", "最差"], [[c["family"] + "/" + c["protocol"], c["validation_set"] + "/" + c["supervision"], c["metric"], c["observations"], c["best"], c["worst"]] for c in result["comparisons"] if c["observations"] > 1])
    lines += ["", "## 4. 全部已执行版本", ""]
    lines += table(["模型/Run", "协议/阶段", "组合/配比", "训练量/独立量", "Epoch/时间s", "主Val最低Loss Epoch", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "该Epoch实体"], [
        [r["family"] + "/" + r["run_id"], r["protocol"] + "/" + cell(r["stage"]), cell(r["supervision"]) + "/" + cell((r["sampling"] or {}).get("ratio_label")),
         cell(r["exposure"].get("trained_records")) + "/" + cell(r["exposure"].get("distinct_units")), cell(r["epochs"]) + "/" + cell(r["training_seconds"]),
         (r["best_loss_epoch"] or {}).get("epoch"), [{k: v.get(k) for k in ("stream", "accuracy", "loss", "nll", "brier", "ece")} for v in r["validation_at_selected_epoch"]], r["selected_epoch_physical"]] for r in result["observations"]])
    lines += ["", "## 5. 同材料范围配比对照", "",
        "B02/QB/PB 保持原材料范围、初始化、种子与两Epoch预算。主Val按每Run最低主Loss选择；选中Epoch不同会影响比较，全部Epoch均保存在JSON。", ""]
    ratio_rows = [r for r in result["observations"] if r["run_id"].startswith("P0_B02_C") and r["run_id"].endswith("QB_PB") and r["protocol"] == "MR-FULL-GRADED-P0-DATA-REPAIR-v1"]
    lines += table(["Run/监督", "主目标", "配比", "载入/stream", "所选Epoch", "主Val Accuracy", "Loss", "Brier", "ECE", "辅助Val"], [
        [r["run_id"] + "/" + str(r["supervision"]), r["primary_stream"], (r["sampling"] or {}).get("ratio_label"), r["exposure"].get("train_groups"),
         (r["best_loss_epoch"] or {}).get("epoch"), (r["best_loss_epoch"] or {}).get("accuracy"), (r["best_loss_epoch"] or {}).get("loss"),
         (r["best_loss_epoch"] or {}).get("brier"), (r["best_loss_epoch"] or {}).get("ece"),
         [{k: v.get(k) for k in ("stream", "accuracy", "loss", "brier", "ece")} for v in r["validation_at_selected_epoch"] if v["stream"] != r["primary_stream"]]] for r in ratio_rows])
    lines += ["", "上表分别呈现Accuracy与概率质量，不宣布唯一最优比例。", "",
        "F06完整轨迹：" + cell([{k: v.get(k) for k in ("epoch", "stream", "accuracy", "loss", "brier", "ece")} for r in result["observations"] if r["run_id"] == "F06" for v in r["validation_all_epochs"]]), "",
        "曝光数量异常：" + cell([{ "run_id": r["run_id"], "exposure": r["exposure"]} for r in result["observations"] if r["exposure"].get("distinct_units_issue")]), "",
        "## 6. Kev 候选与材料", "",
        "正式Kev的实际训练状态与全部固定Val：" + cell([{ "run_id": r["run_id"], "status": r["status"], "validation": r["validation_all_epochs"]} for r in result["observations"] if r["family"] == "kev" and r["stage"] == "FORMAL_LORA"]),
        "C05原文本state含任务与Prompt，没有可单独移除的动态字段，未创建无效状态消融。C07既定Rank8与现有Rank16初权重不兼容，从基座重建会同时改变初始化，未擅自启动。",
        "C09原Arena导出均已在C03使用，历史视图保留。原转换入口新增合法typed辅助视图，仅使用实际观察的S2终局与S3缓存、输出Token及quota类别，不创建未选模型胜负。C09当前训练与Val状态见候选表；训练材料统计：" + cell((result["kev_typed_auxiliary"].get("splits") or {}).get("train")) + "。新增视图与原Pilot分别保存。", "",
        "材料统计：" + cell(result["kev_materialization"]), "",
        "Kev训练与Val沿用原入口，当前状态见实时观测；候选方法与材料待决原因保留在原队列。", "",
        "## 7. 科学解释与当前限制", "",
        "1. 候选规模、物化、编码、实际训练量和独立量分别保留。由载入条目×Epoch派生的数带 scope说明，不能当实测计数。逐监督梯度贡献没有历史记录，无法直接识别。",
        "2. S1与加入S2/S3的比较使用同Val的Accuracy、Loss、Brier和ECE。Laya没有单独保存的NLL使用N/A；不得擅自把不同标签的Loss合并为主路由收益。",
        "3. S1/S3的1:1、2:1、1:2及三监督配比均保留原参数。只有初始化、材料范围、预算和Val都一致时才支持受控比较。",
        "4. F全量自然材料覆盖与ALGN按最小供给的受控抽样存在曝光与优化器预算差异；两者不能用于单独证明监督组合效应。",
        "5. 层级、规模、种子和课程变化保留逐Run轨迹；缺失课程父权重的子项不能通过改用基座或重训已完成父Run来补齐。",
        "6. Accuracy与概率质量可能发生权衡。饱和、过拟合和负迁移应结合完整Val轨迹及同协议对照判断，不能由最小Train Loss直接推断。",
        "7. Kev正式LoRA、导入模型、部分训练及Pointer Head Pilot分开。C04使用C03权重与新优化器；收益同时包含更多训练及不同学习率。C05状态不可分离、C07 Rank与初始化不兼容时保留待决原因。",
        "8. 固定Val连续参与选模，结果为开发期描述；不能代替独立最终Test，也不直接比较Laya与Kev不同Val的Accuracy。",
        "9. 各Run主Val最佳Epoch的实体状态逐行展示，元数据不能代替可加载权重。留存策略源码与服务器实际部署状态分别报告。",
        "10. 本轮可支持RQ4训练监督与概率质量的离线消融准备。正式任务成功率、完整Episode费用、Model×Effort效果与RQ1–RQ5结论仍需原版Verifier的真实AgentEpisode。", "",
        "训练实付费用N/A；本地权重没有Token按量费用。原日志路径、配置、曝光和每个版本实体状态见同目录JSON，曲线仍由原shards/training_runs提供。", ""]
    def compact_metric(r):
        v = r["best_loss_epoch"] or {}
        return [r["run_id"], r["primary_stream"], (r["sampling"] or {}).get("ratio_label"), r["exposure"].get("trained_records"),
                r["training_seconds"], v.get("epoch"), *[v.get(k) for k in ("accuracy", "loss", "nll", "brier", "ece")],
                r["selected_epoch_physical"]]
    eta = result["training_eta"]
    overview = ["## Executive Summary", "",
        "Laya 实际执行 " + str(result["counts"]["laya"]["executed_runs"]) + " 个 Run；Kev本地执行与导入资产分别统计，完整对象见附录。历史完成项目沿用原结果。",
        "当前双模型进度：" + cell([{ "model": family, "run_id": eta["current"][family]["run_id"], "status": eta["current"][family]["status"], "evaluation_status": eta["current"][family]["evaluation_status"]} for family in ("laya", "kev")]) + "。观测时间：" + cell(eta["observed_at"]) + "。",
        "B02 同层级配比对照显示，增加辅助监督没有稳定提高 S1 Accuracy。S1+S3 的 2:1 存在主Loss改善与Accuracy下降的权衡；S2+S3缺少直接S1监督，主任务结果较弱。具体值与预算见下表。",
        "ALGN四项在主Val上的差异较小，但训练曝光和时间不同。F系列增加全材料覆盖后的主任务Accuracy可能上升，辅助概率质量可能恶化。无法由单次开发期Val确定最优比例或模型架构。",
        "旧五份实体只剩 " + str(sum(c["physical"] is True for c in result["retention"]["old_core"])) + " 份。主Val最低Loss模型与当前可加载模型分开。Kev实体处理见下方同协议记录，Laya原策略保持。",
        "建议先完成原定当前Run和代表性对照，再由Planning决定是否减少新增矩阵。离线证据已支持监督与概率质量分析，任务成功率和真实费用仍需官方AgentEpisode。",
        "现有可计算队列预计墙钟 " + str(round(eta["totals"]["serial_wall_seconds"] / 3600, 1)) + " 小时；CPU物化、共享GPU波动和待决候选的限制见时间预算。整体论文完成日期N/A。", "",
        "## 技术演进与研究变量", "",
        "早期N系列和旧输入协议探索训练规模、参数和输入表达；旧协议16项与现行P0协议分别统计。P0矩阵把监督组合、比例、层级、质量和采样拆为已有参数，实际完成的槽位支持开发期对照。",
        "ALGN采用受控配比与有限抽样；F系列逐层、累计层、比例子集采用全材料覆盖。课程Run改变初始化及训练次序。V8扩展中的Pointer Head Pilot与正式LoRA分别记录，不能用Pilot代表完整Kev训练。",
        "Kev C03通过官方typed state/questions接口完成正式训练和项目固定Val；C04从C03接续，学习率与训练预算共同改变。不同模型Val和输出标签并不一致，当前没有跨架构因果对照。", "",
        "## 可观察的配比、预算与任务权衡", "",
        "下表按最低主Val Loss的同一Epoch取Accuracy、Brier、ECE；完整Epoch在附录。S1-only可作为同层主监督参考，辅助任务仍分别呈现。S2/S3主目标衡量各自标签，不能用于S1模型选择能力排序；缺少S1实测保留N/A。小样本单种子差异未作显著性或因果宣称。", ""]
    overview += table(["B02 Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"], [compact_metric(r) for r in ratio_rows])
    overview += ["", "ALGN受控配比：", ""]
    overview += table(["Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"],
                      [compact_metric(r) for r in result["observations"] if r["stage"] == "ALGN"])
    overview += ["", "全材料及纯监督按层级/规模保留各自预算；下表不能单独隔离监督比例的影响。", ""]
    overview += table(["Run", "主目标", "比例", "训练曝光", "时间s", "Epoch", "Accuracy", "Loss", "NLL", "Brier", "ECE", "实体"],
                      [compact_metric(r) for r in result["observations"] if r["family"] == "laya" and r["sampling"]["mode"] == "FULL_COVERAGE"])
    overview += ["", "F06最低S1 Loss与最高S1 Accuracy独立列出，同列的其他指标均来自对应Epoch：", ""]
    overview += table(["Run", "选择依据", "Epoch", "Accuracy", "Loss", "Brier", "ECE", "实体"],
                      [[r["run_id"], label, *[(r[field] or {}).get(k) for k in ("epoch", "accuracy", "loss", "brier", "ece")], r[physical]]
                       for r in result["observations"] if r["run_id"] == "F06"
                       for label, field, physical in (("最低S1 Loss", "best_loss_epoch", "selected_epoch_physical"),
                                                      ("最高S1 Accuracy", "best_accuracy_epoch", "best_accuracy_physical"))])
    overview += ["", "F06的主任务/辅助任务逐Epoch值：", ""]
    overview += table(["Epoch", "监督", "Accuracy", "Loss", "Brier", "ECE"],
                      [[v.get(k) for k in ("epoch", "stream", "accuracy", "loss", "brier", "ece")]
                       for r in result["observations"] if r["run_id"] == "F06" for v in r["validation_all_epochs"] if v["stream"] in ("S1", "S2", "S3")])
    overview += ["", "F06第二Epoch主Accuracy上升但主Loss没有改善，S2 Loss/ECE恶化；主Accuracy、校准、辅助任务收益应分别解释。现有记录不足以区分更多数据、训练时间和共享表征造成的影响。",
        "全量候选统计：" + cell(result["data_census"]) + "。这是候选材料规模；ALGN抽样、矩阵quota、编码跳过和重复曝光均会改变优化器实际输入。逐监督梯度贡献没有记录，不能从原材料比例推断。", "",
        "## 同固定Val、同目标的历史趋势", "",
        "各组按原记录的开始时间排列，未记录时间的Run按ID列在后面。最低Loss与最高Accuracy各自选择Epoch，实体状态分别列出；层级、配比、初始化和训练预算可能不同，趋势仅作描述。S1、S2、S3与Kev clean分别呈现，未将辅助目标当作S1收益。", ""]
    for group in result["objective_trends"]:
        if len(group["observations"]) < 2:
            continue
        overview += ["", cell({k: group[k] for k in ("family", "protocol", "validation_set", "stream", "items", "loss_definition")}), ""]
        overview += table(["Run/状态", "监督/比例", "训练曝光/时间s", "最低Loss Epoch", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "Loss实体", "最高Accuracy Epoch", "Accuracy", "Accuracy实体"],
                          [[r["run_id"] + "/" + r["status"], {"streams": r["supervision"], "ratio": r["sampling"]["ratio_label"]},
                            "/".join(cell(r[k]) for k in ("trained_records", "training_seconds")), r["best_loss_epoch"]["epoch"],
                            "/".join(cell(r["best_loss_epoch"].get(k)) for k in ("accuracy", "loss", "nll", "brier", "ece")), r["selected_epoch_physical"],
                            (r["best_accuracy_epoch"] or {}).get("epoch"), (r["best_accuracy_epoch"] or {}).get("accuracy"), r["best_accuracy_physical"]]
                           for r in group["observations"]])
    overview += ["", "## 可加载实体与最终候选", "",
        "以下候选仅来自采集时有实体的记录，指标使用实体对应Epoch；最低Loss实体缺失时不挪用其成绩。短训练、Pilot、导入资产与正式训练分别标明，任务级能力仍待评测。", ""]
    overview += table(["模型/Run", "协议/类别", "主目标", "Epoch", "最低Loss/最高Accuracy Epoch", "Val/数量", "同Epoch Accuracy/Loss/NLL/Brier/ECE", "用途", "实体位置"],
                      [[c["family"] + "/" + c["run_id"], c["protocol"] + "/" + c["training_kind"], c["primary_stream"], c["epoch"],
                        [c["is_best_loss_epoch"], c["is_best_accuracy_epoch"]],
                        "/".join(cell((c["primary_validation"] or {}).get(k)) for k in ("validation_set", "items")),
                        "/".join(cell((c["primary_validation"] or {}).get(k)) for k in ("accuracy", "loss", "nll", "brier", "ece")), c["candidate_role"], c["path"]]
                       for c in result["loadable_candidates"]])
    missing_best = [r for r in result["observations"] if r["family"] == "laya" and r["best_loss_epoch"] and not r["selected_epoch_physical"]]
    overview += ["", "Laya有主Val Loss的实际Run中，" + str(len(missing_best)) + " 个最佳Loss Epoch没有物理实体。可使用现存候选做任务级实验，历史最优成绩只能用于离线分析；替代实体不能标成相同Epoch。",
        "Kev正式固定Val和coverage：" + cell([{ "run_id": r["run_id"], "metrics": r["validation_all_epochs"], "coverage": r["validation_coverage"], "comparison_to_c03": r["comparison_to_c03"], "training_seconds": r["training_seconds"], "evaluation_seconds": r["evaluation_seconds"]}
                                              for r in result["observations"] if r["family"] == "kev" and r["stage"] == "FORMAL_LORA"]), "",
        "### Kev候选、模型内评分与实体留存", "",
        "评分只用于同一固定Val下的内部实体选择，论文主指标保持原始Accuracy、NLL、Brier、ECE。C11是现有候选选择记录，不新增训练或复制权重。", ""]
    overview += table(["候选", "执行/Val", "Accuracy/NLL/Brier/ECE", "内部评分", "实体状态/释放字节", "尚缺条件"],
                      [[c["candidate_id"], [c.get("status"), c.get("evaluation_status")],
                        (c.get("metrics") or {}).get("clean"), c.get("selection"), c.get("retention"),
                        c.get("pending_reason") or c.get("failure_reason")]
                       for c in result["kev_candidates"]])
    overview += ["", "配方、原训练命令、父实体与验证记录保留在candidate_queue.json、candidate_ledger.json和本报告JSON；未记录的数据内容标识与历史源码提交使用N/A，不承诺遗失材料可精确重建。", "",
        "### Kev已物化的合法配比", "",
        "下表是原数据入口实际生成的材料。READY表示材料就绪，训练是否开始以候选队列和原始Run为准；全部使用同一C03初始化及原固定Val，样本总量随比例变化，不能单独归因于比例。", ""]
    overview += table(["材料ID", "监督比例", "状态", "训练记录/S", "独立单元/S", "训练文件"],
                      [[rid, r["ratio"], r["status"], r["splits"].get("train", {}).get("records_by_class"),
                        r["splits"].get("train", {}).get("independent_units_by_class"), r["dataPaths"].get("train")]
                       for rid, r in result["kev_coverage_material"].get("runs", {}).items()])
    overview += ["", "C10原全量数据中存在当前政策排除的来源，保持待决。广覆盖使用已有Batch1合法目标，不将历史difficulty_tier当作新S3，也不生成未选动作的胜负。", "",
        "## 终点与Planning建议", "",
        "Run级：全材料入口按原定Epoch完成，当前运行状态见实时观测，Kev已完成Val不计入待运行耗时。矩阵/历史小训练入口已有连续两Epoch未达0.5%主Loss改善的结束条件；该条件不适用于全材料入口，不新增结束规则。",
        "实验组级：结合所有Epoch观察Accuracy、Loss、Brier、ECE。F06的权衡及B02辅助监督的负结果支持减少机械扩张的建议，不能据此提前结束健康Run。当前缺多种子误差与独立Test，尚不能宣布性能平台期或唯一最优比例。",
        "整体研究级：代表性主监督、受控双/三监督、层级与规模已有离线结果。建议Planning优先保留能隔离预算和初始化的关键对照，并尽早转向官方Episode；原矩阵缩减只作为建议，执行计划本轮不变。",
        "缩减情景以本次ETA下表的剩余Run和组预算为依据；已完成Run的耗时不可再节省。保留哪些对照尚未确定，部分缩减的可节省时间N/A；原计划本轮不变。",
        "若Planning取消全部尚未运行原矩阵，可节省下表该组的估算墙钟，但会失去质量/采样/层级扩展及未运行配比重复对照；若取消纯S3，将失去辅助目标单独训练的完整规模对照。建议不把课程缺父实体转成新的重训计划。", "",
        "## 全剩余队列时间预算", "", "最后观测时间：" + cell(eta["observed_at"]) + "。", ""]
    overview += table(["当前Run", "剩余训练h", "Val h", "预计结束UTC", "依据"],
                      [[c["run_id"], round(c["remaining_training_seconds"] / 3600, 2) if c["remaining_training_seconds"] is not None else None,
                        round(c["validation_seconds"] / 3600, 2) if c["validation_seconds"] is not None else None,
                        c["estimated_finish_at"], c["method"]] for c in eta["current"].values()])
    overview += ["", "下面训练预算包含历史同类墙钟中的固定验证，未重复计入Val；GPU实际活跃时间N/A。", ""]
    overview += table(["组", "剩余Run", "预计曝光", "历史吞吐records/s", "预计墙钟h", "最快/最慢h", "待物化"],
                      [[g["group"], g["count"], g["remaining_records"], g["records_per_second"],
                        round(g["training_seconds"] / 3600, 2) if g["training_seconds"] is not None else None,
                        [round(g[k] / 3600, 2) if g[k] is not None else None for k in ("fast_seconds", "slow_seconds")],
                        g["needs_materialization"]] for g in eta["groups"]])
    overview += ["", "总体估计：" + cell(eta["totals"]), "",
        "CPU物化使用已有材料日志中的实际耗时作估算，合计秒数见总体 estimated_cpu_materialization_seconds；没有记录的部分和任务切换耗时使用N/A。原矩阵待物化数量不视为已就绪。当前两Run取较长剩余时间估算重叠阶段，后续各模型沿原队列串行。最快/最慢来自历史有效吞吐极值，属于情景范围，无法保证未来GPU资源稳定。",
        "课程父权重、Kev状态标签/Rank初始化/V8材料待决：" + cell(eta["blocked"]), "",
        "完整吞吐样本及原文件位置在training_research.json的training_eta.throughput_samples，每Run自然边界和原采集器轻量状态更新ETA。训练矩阵结束、待决实验结束与论文科研闭环是三个不同时间范围。", "",
        "## 附录：对象、原始Epoch与日志索引", ""]
    # Readable conclusions precede the existing complete historical tables.
    lines = lines[:7] + [""] + overview + lines[7:]
    lines += ["", "### 逐对象设计、关系、用途与缺证", ""]
    lines += table(["对象/类别", "设计与变量", "初始化/配置", "合理对照/变化", "Train轨迹", "最佳Train/Loss/Accuracy Epoch", "用途", "缺证/来源"],
        [[r["family"] + "/" + r["run_id"] + "/" + r["origin"] + "/" + r["training_kind"], r["design"],
          {"initialization": r["initialization"], "config": r["config"]}, {"control": r["comparison"], "within_run": r["validation_changes"]}, r["loss_trajectory"],
          {"train": r["best_train_loss_epoch"], "loss": (r["best_loss_epoch"] or {}).get("epoch"), "accuracy": (r["best_accuracy_epoch"] or {}).get("epoch"), "accuracy_physical": r["best_accuracy_physical"]},
          r["candidate_role"], {"missing": r["missing_evidence"], "source": r["source"], "curve": r["curve_path"]}] for r in result["observations"]])
    lines += ["", "### 全部Epoch指标", ""]
    lines += table(["对象", "Epoch", "Step", "Train Loss", "训练/验证/保存秒", "监督", "Accuracy", "Loss", "NLL", "Brier", "ECE", "来源"],
        [[r["family"] + "/" + r["run_id"], v.get("epoch"), v.get("step"),
          next((e.get("train_loss") for e in r["epoch_records"] if e.get("epoch") == v.get("epoch")), None),
          next(({k: e.get(k) for k in ("train_seconds", "validation_seconds", "checkpoint_seconds", "epoch_seconds")} for e in r["epoch_records"] if e.get("epoch") == v.get("epoch")), None),
          *[v.get(k) for k in ("stream", "accuracy", "loss", "nll", "brier", "ece", "source")]] for r in result["observations"] for v in r["validation_all_epochs"]])
    report = destination / "training_research.md"
    temporary = report.with_suffix(".md.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(report)
    matrix_path = root / "our-project/planning/CANDIDATE_PROGRESSION_MATRIX.md"
    if matrix_path.is_file():
        begin, end = "<!-- KEV_LIVE_CANDIDATES_BEGIN -->", "<!-- KEV_LIVE_CANDIDATES_END -->"
        candidates = result["kev_candidates"]
        coverage_runs = result["kev_coverage_material"].get("runs", {})
        completed_ratios = sum(c.get("status") == "COMPLETED" and c.get("evaluation_status") == "EVALUATED"
                               for c in candidates if c["candidate_id"].startswith("KEV-V8-R"))
        live_lines = [begin, "## 当前 Kev 候选（原队列自动更新）", "",
                      "来源：原候选队列、固定 Val 和实体留存记录。生成时间 UTC：" + result["generated_at"] + "。",
                      "配比固定 Val 已完成 " + str(completed_ratios) + "/" + str(len(coverage_runs)) +
                      "；材料 READY 不计训练完成。以下为当前状态，下方带日期的条目保留历史。", ""]
        rows = []
        for c in candidates:
            metrics, selection, retained = c.get("metrics") or {}, c.get("selection") or {}, c.get("retention") or {}
            material = c.get("coverage_analysis") or {}
            rows.append([c["candidate_id"], material.get("ratio"), c.get("status"), c.get("evaluation_status"),
                         *[metrics.get("clean", {}).get(k) for k in ("acc", "nll", "brier", "ece")],
                         metrics.get("coverage", {}).get("evaluated_questions"), selection.get("score"),
                         retained.get("status"), retained.get("total_released_bytes", 0),
                         c.get("pending_reason") or c.get("failure_reason")])
        for rid, material in coverage_runs.items():
            if not any(c["candidate_id"] == "KEV-V8-" + rid for c in candidates):
                rows.append(["KEV-V8-" + rid, material["ratio"], "MATERIAL_READY", "NOT_EVALUATED",
                             None, None, None, None, None, None, None, 0, "等待原 dispatcher 自然接续"])
        live_lines += table(["候选", "监督比例", "执行", "固定 Val", "Accuracy", "NLL", "Brier", "ECE",
                             "计分问题", "内部评分", "实体状态", "累计释放字节", "尚缺条件"], rows)
        live_lines += ["", "内部评分只用于实体选择；固定 Val 不计官方 Agent 成功率。完整配方、材料、命令与原始指标见 training_research.json 和 candidate_ledger.json。", end]
        existing = matrix_path.read_text(encoding="utf-8")
        section = "\n".join(live_lines)
        if begin in existing:
            before, remainder = existing.split(begin, 1)
            _, after = remainder.split(end, 1)
            updated = before + section + after
        else:
            before, after = existing.split("\n## ", 1)
            updated = before + "\n" + section + "\n\n## " + after
        if updated != existing:
            temporary = matrix_path.with_suffix(".md.tmp")
            temporary.write_text(updated, encoding="utf-8")
            temporary.replace(matrix_path)
    return {"report": relative(report, root), "data": "our-project/results/training/training_research.json", "counts": result["counts"]}
