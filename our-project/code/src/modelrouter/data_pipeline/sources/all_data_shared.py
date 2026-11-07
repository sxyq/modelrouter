"""Shared source identity and serialization helpers for canonical data views."""

import hashlib
import json
import os
import pickle
import random
import re
from collections import defaultdict


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

def _stage_dir(out_dir, *parts):
    path = os.path.join(out_dir, "training", *parts)
    os.makedirs(path, exist_ok=True)
    return path

def _split(key):
    n = int(hashlib.sha256(str(key).encode()).hexdigest()[:8], 16) % 100
    return "train" if n < 80 else ("val" if n < 90 else "test")

def _semantic_split(prompt_text, fallback_id, seed=42):
    p = (prompt_text or "").strip().lower()
    if p.startswith("benchmark:") and "task prompt:" in p:
        p = p.split("task prompt:", 1)[1].strip()
    elif p.startswith("evaluation task:") and "problem input:" in p:
        p = p.split("problem input:", 1)[1].strip()
    elif p.startswith("[arena battle]") and "prompt:" in p:
        p = p.split("prompt:", 1)[1].strip()
    p = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", p)
    canon = re.sub(r"\s+", " ", p).strip()
    sem_key = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16] if canon else str(fallback_id)
    h = int(hashlib.sha256(f"sem_{sem_key}_{seed}".encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "train" if h < 0.80 else ("val" if h < 90 / 100.0 else "test")

def _prompt(text):
    return " ".join(str(text or "").replace("\u2028", "").replace("\u2029", "").split()).strip()

def _shuffled_criteria(candidates, seed_key, desc=""):
    cands = list(candidates)
    rng = random.Random(f"42_{seed_key}")
    rng.shuffle(cands)
    return {m: desc for m in cands}

def _soft_distribution(scores_dict, criteria_keys):
    pos = {m: max(0.0, float(scores_dict.get(m, 0.0))) for m in criteria_keys}
    tot = sum(pos.values())
    if tot <= 0:
        u = round(1.0 / len(criteria_keys), 6)
        dist = {m: u for m in criteria_keys}
    else:
        dist = {m: round(pos[m] / tot, 6) for m in criteria_keys}
    diff = round(1.0 - sum(dist.values()), 6)
    best_m = max(criteria_keys, key=lambda m: (pos[m], m))
    dist[best_m] = round(max(0.0, dist[best_m] + diff), 6)
    return dist, best_m

def _load_stage1_reference(stage1_dir):
    """Load canonical splits and task_ids from MR-STAGE1-INPUT-FIX/stage1."""
    r1_choice_by_key = {}
    r2_split_by_sid = {}
    r1_unsupervised_by_key = {}
    r2_tied_rows = {}
    for sp in ("train", "val", "test"):
        fp = os.path.join(stage1_dir, f"{sp}.jsonl")
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                prov = r.get("provenance") or r.get("_meta") or {}
                src = prov.get("source_id") or prov.get("source")
                tid = str(prov.get("task_id") or "")
                if src == "ROUTE-001":
                    bm = str(prov.get("benchmark_name") or prov.get("benchmark") or "unknown")
                    h = str(prov.get("full_prompt_hash") or "")
                    r1_choice_by_key[(bm, h)] = (sp, tid, r)
                elif src == "ROUTE-002":
                    sid = str(prov.get("sample_id") or (tid[len("routerbench_"):] if tid.startswith("routerbench_") else tid))
                    r2_split_by_sid[sid] = (sp, tid, r.get("state", ""))
    unsup_fp = os.path.join(stage1_dir, "analysis_unsupervised_or_tied.jsonl")
    if os.path.exists(unsup_fp):
        with open(unsup_fp, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                p = r.get("provenance", {})
                src = p.get("source_id")
                if src == "ROUTE-001":
                    bm = str(p.get("benchmark_name") or "unknown")
                    srid = str(p.get("source_record_id") or "")
                    h = p.get("full_prompt_hash") or (srid.split("_")[-1] if "_" in srid else "")
                    idx = p.get("instance_index") or "0"
                    r1_unsupervised_by_key[(bm, h)] = {
                        "selection_rule": p.get("selection_rule"),
                        "task_id": f"llmroute_{bm}_{idx}_{h[:8]}",
                        "record": r,
                    }
                elif src == "ROUTE-002":
                    sid = str(p.get("sample_id") or p.get("source_record_id") or "unknown")
                    r2_tied_rows[sid] = r
    return r1_choice_by_key, r2_split_by_sid, r1_unsupervised_by_key, r2_tied_rows

def _route001_groups(raw_root, out_dir):
    """Load ROUTE-001 multi-model evaluations per (canonical_benchmark, full_prompt_hash)."""
    score_dir = os.path.join(out_dir, "training", "stage1_score")
    cached_files = [os.path.join(score_dir, f"{sp}.jsonl") for sp in ("train", "val", "test")]
    if all(os.path.exists(p) and os.path.getsize(p) > 0 for p in cached_files):
        groups = {}
        for p in cached_files:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    prov = r.get("provenance", {})
                    if prov.get("source_id") != "ROUTE-001":
                        continue
                    bm = prov["benchmark"]
                    h = prov["full_prompt_hash"]
                    st = r.get("state", "")
                    if st.startswith("Benchmark:") and "\nTask Prompt: " in st:
                        st = st.split("\nTask Prompt: ", 1)[1]
                    groups[(bm, h)] = {
                        "benchmark": bm,
                        "prompt": st,
                        "scores": {m: float(s) for m, s in (r.get("scores") or {}).items() if m != "openrouter"},
                    }
        if groups:
            return groups

    root = os.path.join(raw_root, "ROUTE-001_LLMRouterBench", "bench-release")
    raw_groups = defaultdict(lambda: {"prompt": "", "benchmark": "", "records": []})
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
            for i, rec in enumerate(data.get("records", [])):
                oq = str(rec.get("origin_query") or "")
                pq = str(rec.get("prompt") or "")
                norm_oq = _prompt(oq)
                norm_pq = _prompt(pq)
                if norm_pq.endswith("/no_think"):
                    norm_pq = norm_pq[:-9].strip()
                h = hashlib.sha256((norm_oq + "\n" + norm_pq).encode()).hexdigest()[:16]
                g = raw_groups[(canonical, h)]
                g["benchmark"] = canonical
                if not g["prompt"]:
                    g["prompt"] = _prompt(oq if oq else pq)
                score = rec.get("score")
                if score is None:
                    continue
                cost = rec.get("cost")
                g["records"].append({
                    "model": str(data.get("model_name") or "unknown"),
                    "score": float(score),
                    "cost": float(cost) if cost is not None else 0.0,
                })
    groups = {}
    for (bm, h), g in raw_groups.items():
        by_m = defaultdict(list)
        for x in g["records"]:
            if x["model"] == "openrouter":
                continue
            by_m[x["model"]].append(x)
        scores = {}
        for m, xs in sorted(by_m.items()):
            u = {(round(x["score"], 6), round(x["cost"], 8)) for x in xs}
            if len(u) == 1:
                s, _ = next(iter(u))
                scores[m] = s
        groups[(bm, h)] = {"benchmark": bm, "prompt": g["prompt"], "scores": scores}
    return groups

def _routerbench_prompts(raw_root, stage1_dir=None):
    prompts = {}
    if stage1_dir:
        for sp in ("train", "val", "test"):
            fp = os.path.join(stage1_dir, f"{sp}.jsonl")
            if not os.path.exists(fp):
                continue
            with open(fp, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    prov = r.get("provenance") or r.get("_meta") or {}
                    if (prov.get("source_id") or prov.get("source")) == "ROUTE-002":
                        sid = str(prov.get("sample_id") or "")
                        st = str(r.get("state") or "")
                        if ".\nProblem input: " in st:
                            st = st.split(".\nProblem input: ", 1)[1]
                        elif ".\nTask Prompt: " in st:
                            st = st.split(".\nTask Prompt: ", 1)[1]
                        if sid:
                            prompts[sid] = st
    if not raw_root:
        return prompts
    raw_file = os.path.join(raw_root, "ROUTE-002_RouterBench", "routerbench_0shot.pkl")
    if not os.path.exists(raw_file):
        return prompts
    try:
        import ast
        with open(raw_file, "rb") as f:
            df = pickle.load(f)
        for _, raw_row in df.iterrows():
            sid = str(raw_row.get("sample_id") or "unknown")
            if sid in prompts:
                continue
            raw_prompt = raw_row.get("prompt")
            if isinstance(raw_prompt, str):
                try:
                    parsed = ast.literal_eval(raw_prompt)
                    prompt = str(parsed[-1]).strip() if isinstance(parsed, (list, tuple)) and parsed else raw_prompt.strip()
                except Exception:
                    prompt = raw_prompt.strip()
            elif isinstance(raw_prompt, (list, tuple)) and raw_prompt:
                prompt = str(raw_prompt[-1]).strip()
            else:
                prompt = str(raw_prompt or "").strip()
            prompts[sid] = prompt.replace("\u2028", "").replace("\u2029", "").replace("\n", " ").strip()
    except Exception:
        pass
    return prompts
