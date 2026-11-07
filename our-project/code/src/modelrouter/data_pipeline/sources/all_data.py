"""Coordinate canonical source materialization and adapter exports."""

import json
import os
from collections import Counter

from .all_data_shared import PUBLIC_FILES, _dump
from .all_data_stage1 import _build_stage1_all_views
from .all_data_adapters import (
    _build_stage2_adapters, _build_stage3_adapters, _build_stage4_adapters,
    _map_action_category,
)
from .coverage_audit import audit_and_reconcile_coverage_counts


def _variable_refs(cleaned_root, out_dir):
    target = os.path.join(out_dir, "by_variable")
    os.makedirs(target, exist_ok=True)
    names = ("Task_Subtask", "Agent_Coordination", "Context_Memory", "Tool_Environment", "Verification_Recovery", "KV_Cache_Continuity", "Temporal_Execution", "Provider_Availability")
    if all(os.path.exists(os.path.join(target, n + ".jsonl")) and os.path.getsize(os.path.join(target, n + ".jsonl")) > 0 for n in names):
        return Counter({n: sum(1 for _ in open(os.path.join(target, n + ".jsonl"), encoding="utf-8")) for n in names})
    fs = {n: open(os.path.join(target, n + ".jsonl"), "w", encoding="utf-8") for n in names}
    counts = Counter()
    for source, rel in PUBLIC_FILES.items():
        path = os.path.join(cleaned_root, rel)
        for line_no, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip():
                continue
            r = json.loads(line)
            p = r.get("provenance", {})
            pre = r.get("pre_decision_state", {})
            obs = r.get("observed_decision", {})
            out = r.get("ground_truth_outcome", {})
            vals = {
                "Task_Subtask": [p.get("instance_id"), p.get("task_id"), p.get("sample_id"), p.get("instance_index"), pre.get("task_domain"), pre.get("eval_name")],
                "Agent_Coordination": [p.get("agent_framework"), p.get("model_name"), obs.get("action_type")],
                "Context_Memory": [pre.get("context_chars"), pre.get("prompt_tokens_est"), pre.get("question_type"), pre.get("haystack_docs_count")],
                "Tool_Environment": [p.get("environment"), obs.get("action_type"), pre.get("prior_tool_calls_count")],
                "Verification_Recovery": [out.get("task_resolved"), out.get("score"), out.get("human_winner")],
                "KV_Cache_Continuity": [pre.get("prefix_hash_sample"), pre.get("prefix_block_count"), out.get("physical_provider_cache_hit"), out.get("historical_prefix_hit_ratio")],
                "Temporal_Execution": [p.get("timestamp"), pre.get("arrival_timestamp"), out.get("completion_tokens"), out.get("cost_usd")],
                "Provider_Availability": [p.get("model_name"), p.get("provider"), p.get("reasoning_effort_mode"), pre.get("requested_model")],
            }
            ref = {"source_id": source, "source_file": rel, "line": line_no, "record_id": p.get("instance_id") or p.get("task_id") or p.get("sample_id") or p.get("request_index")}
            for n, xs in vals.items():
                if any(x not in (None, "", "unknown") for x in xs):
                    _dump(fs[n], ref)
                    counts[n] += 1
    for f in fs.values():
        f.close()
    return counts


def prepare_all_data(args):
    raw_root = args.raw_root
    cleaned_root = args.cleaned_root
    out_dir = args.all_data_out_dir
    os.makedirs(out_dir, exist_ok=True)
    for d in ("by_source", "by_variable", "evaluation", "analysis_only", "training"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)

    source_counts = {}
    for source, rel in PUBLIC_FILES.items():
        by_src_fp = os.path.join(out_dir, "by_source", source + ".jsonl")
        if os.path.exists(by_src_fp) and os.path.getsize(by_src_fp) > 0:
            source_counts[source] = sum(1 for _ in open(by_src_fp, encoding="utf-8"))
            continue
        path = os.path.join(cleaned_root, rel)
        n = 0
        with open(by_src_fp, "w", encoding="utf-8") as f:
            for line_no, line in enumerate(open(path, encoding="utf-8"), 1):
                if not line.strip():
                    continue
                r = json.loads(line)
                p = r.get("provenance", {})
                _dump(f, {"source_id": source, "source_file": rel, "line": line_no, "record_id": p.get("instance_id") or p.get("task_id") or p.get("sample_id") or p.get("request_index"), "status": "cleaned"})
                n += 1
        source_counts[source] = n

    stage1_dir = os.path.normpath(os.path.join(os.path.dirname(out_dir), "MR-STAGE1-INPUT-FIX", "stage1"))
    stage1_stats = _build_stage1_all_views(out_dir, stage1_dir, raw_root, cleaned_root)
    stage2_stats = _build_stage2_adapters(cleaned_root, out_dir)
    stage3_stats = _build_stage3_adapters(cleaned_root, out_dir)
    stage4_stats = _build_stage4_adapters(cleaned_root, out_dir)
    variables = _variable_refs(cleaned_root, out_dir)

    summary = {
        "experiment": "MR-ALLDATA-PREP-20261011",
        "source_counts": source_counts,
        "stage1_stats": dict(stage1_stats),
        "stage2_stats": dict(stage2_stats),
        "stage3_stats": dict(stage3_stats),
        "stage4_stats": dict(stage4_stats),
        "variable_reference_counts": dict(variables),
        "notes": [
            "Unified question identity and semantic prompt split enforced across Stage 1 Choice, recomputed_route001, Pairwise, Score, and Soft-Target",
            "Model-specific training views written to training/laya/ and training/kev/",
            "ROUTE-003 is evaluation-only; ROUTE-005 is analysis-only",
            "No GPU, API, model download, or Coding Benchmark execution",
        ],
    }
    for model_name in ("laya", "kev"):
        adapter_meta = {
            "model": model_name,
            "stage1_choice": {sp: stage1_stats[f"choice_{sp}"] for sp in ("train", "val", "test")},
            "stage1_pairwise": {sp: stage1_stats[f"pairwise_{sp}"] for sp in ("train", "val", "test")},
            "stage1_soft_target": {sp: stage1_stats[f"soft_target_{sp}"] for sp in ("train", "val", "test")},
            "stage2_agent_state": {sp: stage2_stats[f"adapted_{sp}"] for sp in ("train", "val", "test")},
            "stage3_effort": {sp: stage3_stats[f"decisive_{sp}"] for sp in ("train", "val", "test")},
            "stage4_auxiliary": {sp: stage4_stats[f"adapted_{sp}"] for sp in ("train", "val", "test")},
        }
        with open(os.path.join(out_dir, "training", model_name, "adapter_summary.json"), "w", encoding="utf-8") as f:
            json.dump(adapter_meta, f, ensure_ascii=False, indent=2)

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary
