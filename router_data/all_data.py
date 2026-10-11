"""Full cleaned-data preparation for the one-off ModelRouter study run."""

import csv
import hashlib
import json
import math
import os
import pickle
import shutil
from collections import Counter, defaultdict


PUBLIC_FILES = {
    "TRA-001": "Agent轨迹/TRA-001_Open-SWE-Traces/cleaned_trajectories.jsonl",
    "TRA-002": "Agent轨迹/TRA-002_SWE-smith/cleaned_trajectories.jsonl",
    "TRA-004": "Agent轨迹/TRA-004_AgentSuite/cleaned_trajectories.jsonl",
    "ROUTE-001": "路由比较/ROUTE-001_LLMRouterBench/cleaned_evaluations.jsonl",
    "ROUTE-002": "路由比较/ROUTE-002_RouterBench/cleaned_routerbench.jsonl",
    "ROUTE-003": "路由比较/ROUTE-003_TwinRouterBench/cleaned_twin_bench.jsonl",
    "ROUTE-004": "路由比较/ROUTE-004_Arena/cleaned_arena_preference.jsonl",
    "ROUTE-005": "路由比较/ROUTE-005_FindingTheRightFit/cleaned_task_level.jsonl",
    "CACHE-001": "缓存与时间/CACHE-001_Mooncake/cleaned_mooncake_traces.jsonl",
    "TIME-001": "缓存与时间/TIME-001_BurstGPT/cleaned_burstgpt.jsonl",
    "ENV-001": "任务环境/ENV-001_SWE-Gym/cleaned_swe_gym.jsonl",
    "ENV-002": "任务环境/ENV-002_SWE-rebench-V2/cleaned_swe_rebench.jsonl",
    "MEM-003": "长期记忆/MEM-003_LongMemEval-V2/cleaned_longmemeval_v2.jsonl",
    "MEM-005": "长期记忆/MEM-005_MemoryCraft/cleaned_memorycraft.jsonl",
}


def _dump(f, row):
    f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _split(key):
    n = int(hashlib.sha256(str(key).encode()).hexdigest()[:8], 16) % 100
    return "train" if n < 80 else ("val" if n < 90 else "test")


def _prompt(text):
    return " ".join(str(text or "").replace("\u2028", "").replace("\u2029", "").split()).strip()


def _route001(raw_root):
    root = os.path.join(raw_root, "ROUTE-001_LLMRouterBench", "bench-release")
    groups = defaultdict(lambda: {"prompt": "", "benchmark": "", "records": []})
    for dirpath, _, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".json"):
                continue
            try:
                data = json.load(open(os.path.join(dirpath, name), encoding="utf-8"))
            except Exception:
                continue
            benchmark = str(data.get("dataset_name") or "unknown")
            canonical = "arenahard" if benchmark.startswith("arenahard") else benchmark
            subset = os.path.relpath(os.path.join(dirpath, name), root).split(os.sep)[1] if len(os.path.relpath(os.path.join(dirpath, name), root).split(os.sep)) >= 4 else str(data.get("split") or "test")
            for i, rec in enumerate(data.get("records", [])):
                oq = str(rec.get("origin_query") or "")
                pq = str(rec.get("prompt") or "")
                norm_oq = _prompt(oq)
                norm_pq = _prompt(pq)
                if norm_pq.endswith("/no_think"):
                    norm_pq = norm_pq[:-9].strip()
                h = hashlib.sha256((norm_oq + "\n" + norm_pq).encode()).hexdigest()[:16]
                key = (canonical, h)
                g = groups[key]
                g["benchmark"] = canonical
                g["prompt"] = _prompt(oq if oq else pq)
                score = rec.get("score")
                if score is None:
                    continue
                cost = rec.get("cost")
                g["records"].append({"model": str(data.get("model_name") or "unknown"), "score": float(score), "cost": float(cost) if cost is not None else None, "subset": subset, "index": str(rec.get("index", i))})
    return groups


def _route002(cleaned_file):
    groups = {}
    for line in open(cleaned_file, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        p = r["provenance"]
        sid = str(p.get("sample_id") or "unknown")
        groups[sid] = r
    return groups


def _route001_views(groups, out_dir):
    choice = {"train": open(os.path.join(out_dir, "stage1_choice", "recomputed_route001_train.jsonl"), "w", encoding="utf-8"), "val": open(os.path.join(out_dir, "stage1_choice", "recomputed_route001_val.jsonl"), "w", encoding="utf-8"), "test": open(os.path.join(out_dir, "stage1_choice", "recomputed_route001_test.jsonl"), "w", encoding="utf-8")}
    pair = {k: open(os.path.join(out_dir, "stage1_pairwise", k + ".jsonl"), "w", encoding="utf-8") for k in choice}
    score = {k: open(os.path.join(out_dir, "stage1_score", k + ".jsonl"), "w", encoding="utf-8") for k in choice}
    stats = Counter()
    for (benchmark, h), g in sorted(groups.items()):
        by_model = {}
        for x in g["records"]:
            if x["model"] == "openrouter":
                continue
            by_model.setdefault(x["model"], []).append(x)
        evals = []
        for model, xs in sorted(by_model.items()):
            unique = {(x["score"], x["cost"] or 0.0) for x in xs}
            if len(unique) == 1:
                s, c = next(iter(unique))
                evals.append({"model": model, "score": s, "cost": c})
            else:
                stats["conflicting_model_observations"] += 1
        if len(evals) < 2:
            stats["fewer_than_two_models"] += 1
            continue
        task = f"llmroute_{benchmark}_{h}"
        split = _split(task)
        ordered = sorted(evals, key=lambda x: (-x["score"], x["cost"], x["model"]))
        max_score = ordered[0]["score"]
        top = [x for x in ordered if x["score"] == max_score]
        positive_cost = [x["cost"] for x in top if x["cost"] > 0]
        winner = top[0] if len(top) == 1 else (min(top, key=lambda x: (x["cost"], x["model"])) if len(positive_cost) == len(top) else None)
        if winner is not None:
            choice_row = {"provenance": {"source_id": "ROUTE-001", "task_id": task, "benchmark": benchmark, "full_prompt_hash": h, "supervision_regime": "Regime_B" if len(top) == 1 else "Regime_C"}, "state": f"Benchmark: {benchmark}.\nTask Prompt: {g['prompt']}", "questions": {"model_choice": {"type": "choice", "instructions": "Select the best model for this task.", "criteria": {x["model"]: "" for x in evals}, "label": winner["model"]}}, "expected": {"model_choice": winner["model"]}, "_meta": {"source_id": "ROUTE-001", "candidates": [x["model"] for x in evals], "winner": winner["model"], "selection_rule": "UNIQUE_MAX_SCORE" if len(top) == 1 else "TIED_SCORE_MIN_COST_RULE"}}
            _dump(choice[split], choice_row); stats["single_winner"] += 1
        scored = [x for x in evals if math.isfinite(x["score"])]
        if len(scored) >= 2 and len({x["score"] for x in scored}) > 1:
            _dump(score[split], {"provenance": {"source_id": "ROUTE-001", "task_id": task, "benchmark": benchmark, "full_prompt_hash": h}, "state": g["prompt"], "scores": {x["model"]: x["score"] for x in scored}, "candidates": [x["model"] for x in scored]})
            stats["score_tasks"] += 1
        ranked = sorted(scored, key=lambda x: (-x["score"], x["model"]))
        for a, b in zip(ranked, ranked[1:]):
            if a["score"] <= b["score"]:
                continue
            _dump(pair[split], {"provenance": {"source_id": "ROUTE-001", "task_id": task, "pair_id": f"{task}:{a['model']}:{b['model']}", "full_prompt_hash": h}, "state": g["prompt"], "question": {"type": "pairwise", "preferred": a["model"], "rejected": b["model"], "score_delta": a["score"] - b["score"]}})
            stats["pairwise"] += 1
    for f in [*choice.values(), *pair.values(), *score.values()]:
        f.close()
    return stats


def _route002_views(groups, out_dir):
    stats = Counter()
    handles = {name: open(os.path.join(out_dir, "stage1_score", "route002_" + name + ".jsonl"), "w", encoding="utf-8") for name in ("train", "val", "test")}
    pairs = {name: open(os.path.join(out_dir, "stage1_pairwise", "route002_" + name + ".jsonl"), "w", encoding="utf-8") for name in handles}
    for sid, r in groups.items():
        ev = r.get("candidate_evaluations") or {}
        vals = [(m, float(v.get("score") or 0), float(v.get("cost_usd") or 0)) for m, v in ev.items()]
        if len(vals) < 2 or len({x[1] for x in vals}) <= 1:
            continue
        split = _split("routerbench_" + sid)
        state = r["pre_decision_state"].get("prompt_snippet", "")
        _dump(handles[split], {"provenance": {"source_id": "ROUTE-002", "task_id": "routerbench_" + sid, "sample_id": sid}, "state": state, "scores": {m: s for m, s, _ in vals}, "candidates": [m for m, _, _ in vals]})
        stats["score_tasks"] += 1
        ranked = sorted(vals, key=lambda x: (-x[1], x[0]))
        for a, b in zip(ranked, ranked[1:]):
            if a[1] > b[1]:
                _dump(pairs[split], {"provenance": {"source_id": "ROUTE-002", "task_id": "routerbench_" + sid, "pair_id": f"routerbench_{sid}:{a[0]}:{b[0]}"}, "state": state, "question": {"type": "pairwise", "preferred": a[0], "rejected": b[0], "score_delta": a[1] - b[1]}})
                stats["pairwise"] += 1
    for f in [*handles.values(), *pairs.values()]:
        f.close()
    return stats


def _copy_choice(out_dir, stage1_dir):
    target = os.path.join(out_dir, "stage1_choice")
    os.makedirs(target, exist_ok=True)
    for name in ("train.jsonl", "val.jsonl", "test.jsonl"):
        shutil.copyfile(os.path.join(stage1_dir, name), os.path.join(target, name))


def _stage2(cleaned_root, out_dir):
    target = os.path.join(out_dir, "stage2_agent_state")
    os.makedirs(target, exist_ok=True)
    files = [PUBLIC_FILES[x] for x in ("TRA-001", "TRA-002", "TRA-004")]
    counts = Counter()
    task_counts = defaultdict(Counter)
    for rel in files:
        path = os.path.join(cleaned_root, rel)
        for line in open(path, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line); p = r["provenance"]; key = str(p.get("instance_id") or p.get("task_id") or p.get("trajectory_id") or "unknown")
            task_counts[p.get("source_id", "unknown")][key] += 1
    hs = {k: {s: open(os.path.join(target, s + ".jsonl"), "a", encoding="utf-8") for s in ("train", "val", "test")} for k in ()}
    handles = {s: open(os.path.join(target, s + ".jsonl"), "w", encoding="utf-8") for s in ("train", "val", "test")}
    for rel in files:
        source = next(k for k, v in PUBLIC_FILES.items() if v == rel)
        path = os.path.join(cleaned_root, rel)
        for line in open(path, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line); p = r["provenance"]; key = str(p.get("instance_id") or p.get("task_id") or p.get("trajectory_id") or "unknown")
            split = _split(source + ":" + key)
            _dump(handles[split], {"provenance": p, "state": r.get("pre_decision_state", {}), "action": r.get("observed_decision", {}), "outcome": r.get("ground_truth_outcome", {}), "sample_weight": 1.0 / max(1, task_counts[source][key])})
            counts[source] += 1
    for f in handles.values(): f.close()
    return counts


def _stage3(cleaned_root, out_dir):
    target = os.path.join(out_dir, "stage3_effort"); os.makedirs(target, exist_ok=True)
    rows = defaultdict(list); path = os.path.join(cleaned_root, PUBLIC_FILES["TRA-004"])
    for line in open(path, encoding="utf-8"):
        r = json.loads(line); p = r["provenance"]; rows[str(p.get("instance_id"))].append(r)
    f = open(os.path.join(target, "agent_suite_effort_pairs.jsonl"), "w", encoding="utf-8"); n = 0
    for key, rs in rows.items():
        rs = sorted(rs, key=lambda r: (str(r["provenance"].get("model_name")), str(r["provenance"].get("reasoning_effort_mode"))))
        for a, b in zip(rs, rs[1:]):
            pa, pb = a["provenance"], b["provenance"]
            if pa.get("model_name") == pb.get("model_name") and pa.get("reasoning_effort_mode") != pb.get("reasoning_effort_mode"):
                _dump(f, {"provenance": {"source_id": "TRA-004", "instance_id": key, "model_name": pa.get("model_name")}, "state": a["pre_decision_state"], "low_effort": pa.get("reasoning_effort_mode"), "high_effort": pb.get("reasoning_effort_mode"), "outcomes": [a["ground_truth_outcome"], b["ground_truth_outcome"]]}); n += 1
    f.close(); return Counter(effort_pairs=n)


def _stage4(cleaned_root, out_dir):
    target = os.path.join(out_dir, "stage4_cache_cost"); os.makedirs(target, exist_ok=True); counts = Counter()
    for source in ("CACHE-001", "TIME-001", "ROUTE-005"):
        path = os.path.join(cleaned_root, PUBLIC_FILES[source]); out = open(os.path.join(target, source + ".jsonl"), "w", encoding="utf-8")
        for line in open(path, encoding="utf-8"):
            if not line.strip(): continue
            r = json.loads(line); _dump(out, {"provenance": r["provenance"], "state": r.get("pre_decision_state", {}), "observed": r.get("observed_decision", {}), "outcome": r.get("ground_truth_outcome", {}), "supervision_type": "observed_or_historical"}); counts[source] += 1
        out.close()
    for source, rel in (("OWN-001", "our-project/data/source/cch-model-cost-cache-statistics.csv"), ("OWN-002", "our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv"), ("OWN-003", "our-project/data/summaries/cch-sxyq-gpt-unified-summary.csv")):
        src = os.path.join(os.path.dirname(os.path.dirname(cleaned_root)), rel) if rel.startswith("our-project") else rel
        if not os.path.exists(src): src = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(cleaned_root))), rel)
        if not os.path.exists(src): continue
        out = open(os.path.join(target, source + ".csv"), "w", encoding="utf-8"); shutil.copyfileobj(open(src, encoding="utf-8"), out); out.close(); counts[source] = sum(1 for _ in open(src, encoding="utf-8")) - 1
    return counts


def _variable_refs(cleaned_root, out_dir):
    target = os.path.join(out_dir, "by_variable"); os.makedirs(target, exist_ok=True)
    names = ("Task_Subtask", "Agent_Coordination", "Context_Memory", "Tool_Environment", "Verification_Recovery", "KV_Cache_Continuity", "Temporal_Execution", "Provider_Availability")
    fs = {n: open(os.path.join(target, n + ".jsonl"), "w", encoding="utf-8") for n in names}; counts = Counter()
    for source, rel in PUBLIC_FILES.items():
        path = os.path.join(cleaned_root, rel)
        for line_no, line in enumerate(open(path, encoding="utf-8"), 1):
            if not line.strip(): continue
            r = json.loads(line); p = r.get("provenance", {}); pre = r.get("pre_decision_state", {}); obs = r.get("observed_decision", {}); out = r.get("ground_truth_outcome", {})
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
                if any(x not in (None, "", "unknown") for x in xs): _dump(fs[n], ref); counts[n] += 1
    for f in fs.values(): f.close()
    return counts


def prepare_all_data(args):
    raw_root = args.raw_root; cleaned_root = args.cleaned_root; out_dir = args.all_data_out_dir
    os.makedirs(out_dir, exist_ok=True)
    for d in ("by_source", "by_variable", "stage1_choice", "stage1_pairwise", "stage1_score", "stage2_agent_state", "stage3_effort", "stage4_cache_cost", "evaluation", "analysis_only"):
        os.makedirs(os.path.join(out_dir, d), exist_ok=True)
    source_counts = {}
    for source, rel in PUBLIC_FILES.items():
        path = os.path.join(cleaned_root, rel); n = 0
        with open(os.path.join(out_dir, "by_source", source + ".jsonl"), "w", encoding="utf-8") as f:
            for line_no, line in enumerate(open(path, encoding="utf-8"), 1):
                if not line.strip(): continue
                r = json.loads(line); p = r.get("provenance", {}); _dump(f, {"source_id": source, "source_file": rel, "line": line_no, "record_id": p.get("instance_id") or p.get("task_id") or p.get("sample_id") or p.get("request_index"), "status": "cleaned"}); n += 1
        source_counts[source] = n
    stage1_dir = os.path.join(os.path.dirname(out_dir), "MR-STAGE1-INPUT-FIX", "stage1")
    stage1_dir = os.path.normpath(stage1_dir)
    _copy_choice(out_dir, stage1_dir)
    r1 = _route001(os.path.join(raw_root)); r2 = _route002(os.path.join(cleaned_root, PUBLIC_FILES["ROUTE-002"]))
    route_stats = _route001_views(r1, out_dir); route_stats.update({"ROUTE-002_" + k: v for k, v in _route002_views(r2, out_dir).items()})
    stage2 = _stage2(cleaned_root, out_dir); stage3 = _stage3(cleaned_root, out_dir); stage4 = _stage4(cleaned_root, out_dir); variables = _variable_refs(cleaned_root, out_dir)
    summary = {"experiment": "MR-ALLDATA-PREP-20261011", "source_counts": source_counts, "route_independent_questions": len(r1), "route001_stats": dict(route_stats), "stage2_counts": dict(stage2), "stage3_counts": dict(stage3), "stage4_counts": dict(stage4), "variable_reference_counts": dict(variables), "stage1_choice_counts": {n: sum(1 for _ in open(os.path.join(out_dir, "stage1_choice", n + ".jsonl"))) for n in ("train", "val", "test")}, "notes": ["ROUTE-003 is evaluation-only", "ROUTE-005 is analysis-only", "No GPU, API, model download, or Coding Benchmark execution"]}
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f: json.dump(summary, f, ensure_ascii=False, indent=2)
    return summary
