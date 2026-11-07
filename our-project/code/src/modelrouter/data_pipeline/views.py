"""Build the canonical unified training and evaluation views."""

import json
import os
import random
import sys
from collections import Counter

from modelrouter.data_pipeline.sources.shared import write_jsonl
from .view_reporting import write_stage1_report
from .view_validation import validate_kev_exports


def build_unified_training_and_evaluation_views(args):
    """
    统一训练视图构建与 Kev 格式导出：
    1. 零造假提取真实模型选择监督信号：
       - ROUTE-004 (Arena 55k): 39,716 场明确胜负人类评测盲测对决（排除 17,761 场平局）
       - ROUTE-001 (LLMRouterBench): 26,368 题多模型实测对比，提取有能力/成本区分度的 Oracle 胜者
       - ROUTE-002 (RouterBench): 35,189 题多模型实测对比与官方 Oracle 胜者（排除 1,308 题全错）
       - TRA-004 (AgentSuite): 273 独立任务 × 30 候选模型完整 Episode 对比（步数最少/成功胜者）
    2. 严格按独立任务/题目 (task_id / instance_id / question hash) 进行 80/10/10 隔离划分：
       - train.jsonl (80%), val.jsonl (10%), test.jsonl (10%)
       - 绝不跨划分泄漏（同一题目的所有候选模型和评测记录严格归属于同一划分）
       - ROUTE-003 (TwinRouterBench): 970 步，严格保持 EVAL_BENCHMARK_ONLY，完全隔离输出为
         test_twinrouterbench_holdout.jsonl，0 条进入 train/val！
    3. 生成 5 份轻量训练视图预览样本与统计 (存入 data/公开数据/数据预览/训练视图/):
       - 同题模型比较样本.jsonl (抽取 35 题多模型比较全貌)
       - AgentSuite整任务模型对照样本.jsonl (抽取 35 任务多模型及 thinking 开关对比，标明中途反事实分叉为 0)
       - Agent决策前状态样本.jsonl (抽取 35 条洁净决策前状态，验证无标签与未来信息泄漏)
       - 模型选择训练样本.jsonl (抽取 35 条符合 Kev 官方 choice 格式的训练样本)
       - 数据划分统计.json (详尽的划分统计、来源占比、候选模型分布与零造假核查)
    """
    import hashlib
    import re
    from collections import defaultdict

    print("\n" + "=" * 70)
    print("  [训练视图] 构建 Stage 1 纯静态 Scheme B 模型选择训练视图与 Kev / Laya 任务级划分")
    print("=" * 70)

    raw_root = getattr(args, "raw_root", "data/公开数据/原始数据")
    cleaned_root = args.cleaned_root
    preview_root = args.preview_root
    kev_root = args.kev_root
    laya_root = getattr(args, "laya_root", "data/laya/公开数据")
    stage1_out_dir = getattr(args, "stage1_out_dir", "runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed")
    views_dir = os.path.join(preview_root, "训练视图")
    os.makedirs(stage1_out_dir, exist_ok=True)

    random.seed(args.seed)

    task_pool = {}
    task_pool_training = {}
    task_pool_unsupervised = {}
    candidate_distribution_unfiltered = Counter()
    candidate_distribution_filtered = Counter()
    arena_stats = {"model_a_won": 0, "model_b_won": 0, "total_non_tie": 0, "ties_excluded": 0}
    llmroute_selection_counts = Counter()
    routerbench_selection_counts = Counter()
    agentsuite_selection_counts = Counter()
    agentsuite_thinking_contrasts = 0

    # -------------------------------------------------------------
    # A. ROUTE-004: Arena 55k 人类盲测偏好对决 (39,716 场明确胜负, Regime A)
    # -------------------------------------------------------------
    arena_file = os.path.join(cleaned_root, "路由比较", "ROUTE-004_Arena", "cleaned_arena_preference.jsonl")
    if os.path.exists(arena_file):
        print(f"[Views] 读取 ROUTE-004 Arena 偏好对决: {arena_file}")
        arena_prompt_by_id = {}
        arena_raw_file = os.path.join(raw_root, "ROUTE-004_Arena", "train.csv")
        if os.path.exists(arena_raw_file):
            import csv
            csv.field_size_limit(sys.maxsize)
            with open(arena_raw_file, "r", encoding="utf-8") as raw_f:
                for raw_row in csv.DictReader(raw_f):
                    raw_prompt = raw_row.get("prompt") or ""
                    if raw_prompt.startswith("["):
                        try:
                            import ast
                            try:
                                messages = json.loads(raw_prompt)
                            except Exception:
                                messages = ast.literal_eval(raw_prompt)
                            if isinstance(messages, list):
                                user_messages = [m.get("content", "") for m in messages if isinstance(m, dict) and m.get("role") == "user"]
                                raw_prompt = user_messages[0] if user_messages else (messages[0] if messages else "")
                        except Exception:
                            pass
                    arena_prompt_by_id[str(raw_row.get("id") or "unknown")] = str(raw_prompt).replace("\u2028", "").replace("\u2029", "").replace("\n", " ").strip()
        with open(arena_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                battle_id = r["provenance"]["battle_id"]
                obs = r["observed_decision"]
                winner_choice = obs.get("winner_choice")
                winner_model = obs.get("winner_model")
                pre = r["pre_decision_state"]
                model_a = pre["candidate_model_a"]
                model_b = pre["candidate_model_b"]
                prompt = arena_prompt_by_id.get(str(battle_id), pre["prompt_snippet"])

                if winner_choice == "tie":
                    arena_stats["ties_excluded"] += 1
                    continue
                elif winner_choice == "model_a":
                    arena_stats["model_a_won"] += 1
                    arena_stats["total_non_tie"] += 1
                elif winner_choice == "model_b":
                    arena_stats["model_b_won"] += 1
                    arena_stats["total_non_tie"] += 1
                else:
                    continue

                task_id = f"arena_{battle_id}"
                candidate_distribution_unfiltered[2] += 1
                candidate_distribution_filtered[2] += 1

                choice_criteria = {
                    model_a: "",
                    model_b: ""
                }
                label_model = winner_model if (winner_model and winner_model in choice_criteria) else (model_a if winner_choice == "model_a" else model_b)

                kev_record = {
                    "provenance": {
                        "source_id": "ROUTE-004",
                        "source_name": "Arena-Human-Preference-55k",
                        "raw_file": "ROUTE-004_Arena/train.csv",
                        "source_record_id": str(battle_id),
                        "selection_rule": "HUMAN_BLIND_PAIRWISE_PREFERENCE",
                        "label_nature": "pairwise_human_preference",
                        "supervision_regime": "Regime_A",
                        "battle_id": battle_id,
                        "task_id": task_id,
                    },
                    "state": f"Task: General conversation assistant.\nPrompt: {prompt}",
                    "questions": {
                        "model_choice": {
                            "type": "choice",
                            "instructions": "Select the preferred model for this user query based on human evaluation.",
                            "criteria": choice_criteria,
                            "label": label_model
                        }
                    },
                    "expected": {
                        "model_choice": label_model
                    },
                    "_meta": {
                        "source_id": "ROUTE-004",
                        "num_candidates": 2,
                        "candidates": [model_a, model_b],
                        "winner": label_model,
                        "is_deterministic_oracle": True,
                        "selection_rule": "HUMAN_BLIND_PAIRWISE_PREFERENCE",
                        "label_nature": "pairwise_human_preference",
                        "supervision_regime": "Regime_A"
                    }
                }
                task_pool[task_id] = kev_record
                task_pool_training[task_id] = kev_record

    # -------------------------------------------------------------
    # B. ROUTE-001: LLMRouterBench (真实题目哈希分组 + 同模型重复评测去重 + 冲突隔离 + 移除 openrouter)
    # -------------------------------------------------------------
    llmroute_raw_dir = os.path.join(raw_root, "ROUTE-001_LLMRouterBench", "bench-release")
    llmroute_file = os.path.join(cleaned_root, "路由比较", "ROUTE-001_LLMRouterBench", "cleaned_evaluations.jsonl")
    if os.path.exists(llmroute_raw_dir) or os.path.exists(llmroute_file):
        import glob as _glob
        problems = defaultdict(lambda: {
            "prompt": "",
            "benchmark": "",
            "raw_benchmarks": set(),
            "subsets": set(),
            "indices": [],
            "full_prompt_hash": "",
            "by_model": defaultdict(list),
            "openrouter_present": False
        })

        raw_json_files = sorted(_glob.glob(os.path.join(llmroute_raw_dir, "**", "*.json"), recursive=True)) if os.path.exists(llmroute_raw_dir) else []
        if raw_json_files:
            print(f"[Views] 从 ROUTE-001 原始评测集 ({len(raw_json_files)} 个 JSON 文件) 提取完整原始 Prompt 哈希与真实 subset...")
            for jpath in raw_json_files:
                try:
                    with open(jpath, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                except Exception:
                    continue
                rel_parts = os.path.relpath(jpath, llmroute_raw_dir).split(os.sep)
                subset_name = rel_parts[1] if len(rel_parts) >= 4 else str(data.get("split") or "test")
                mname = str(data.get("model_name") or "unknown")
                bname = str(data.get("dataset_name") or "unknown")
                canon_bname = "arenahard" if bname.startswith("arenahard") else bname
                for rec_i, rec in enumerate(data.get("records", [])):
                    idx = str(rec.get("index", rec_i))
                    oq_raw = str(rec.get("origin_query") or "")
                    pq_raw = str(rec.get("prompt") or "")
                    norm_oq = " ".join(oq_raw.replace("\u2028", "").replace("\u2029", "").strip().split())
                    norm_pq = pq_raw.replace("\u2028", "").replace("\u2029", "").strip()
                    if norm_pq.endswith("/no_think"):
                        norm_pq = norm_pq[:-9].strip()
                    norm_pq = " ".join(norm_pq.split())
                    full_prompt_hash = hashlib.sha256((norm_oq + "\n" + norm_pq).encode("utf-8")).hexdigest()[:16]
                    prompt_raw = oq_raw if oq_raw else pq_raw
                    prompt_snippet = prompt_raw.replace("\u2028", "").replace("\u2029", "").replace("\n", " ").strip()

                    raw_score = rec.get("score")
                    score_val = float(raw_score) if raw_score is not None else None
                    raw_cost = rec.get("cost")
                    cost_val = round(float(raw_cost), 8) if raw_cost is not None else None
                    raw_tokens = rec.get("completion_tokens")
                    tokens_val = int(raw_tokens) if raw_tokens is not None else 0

                    key = (canon_bname, full_prompt_hash)
                    p_entry = problems[key]
                    if not p_entry["prompt"]:
                        p_entry["prompt"] = prompt_snippet
                        p_entry["benchmark"] = canon_bname
                        p_entry["full_prompt_hash"] = full_prompt_hash
                    p_entry["raw_benchmarks"].add(bname)
                    p_entry["subsets"].add(subset_name)
                    p_entry["indices"].append((subset_name, idx, bname))
                    if mname == "openrouter":
                        p_entry["openrouter_present"] = True
                        continue
                    p_entry["by_model"][mname].append({
                        "model": mname,
                        "score": score_val,
                        "cost": cost_val,
                        "tokens": tokens_val,
                        "subset": subset_name,
                        "index": idx,
                        "raw_benchmark": bname
                    })
        else:
            print(f"[Views] 读取 ROUTE-001 LLMRouterBench 清洗文件: {llmroute_file}")
            with open(llmroute_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    prov = r["provenance"]
                    bname = prov["benchmark_name"]
                    canon_bname = prov.get("canonical_benchmark") or ("arenahard" if bname.startswith("arenahard") else bname)
                    subset_name = prov.get("subset_name", "default")
                    idx = str(prov["instance_index"])
                    mname = prov["model_name"]
                    pre = r["pre_decision_state"]
                    prompt_snippet = pre.get("prompt_snippet", "").replace("\u2028", "").replace("\u2029", "")
                    full_prompt_hash = prov.get("full_prompt_hash") or hashlib.sha256(prompt_snippet.encode("utf-8")).hexdigest()[:16]
                    out = r["ground_truth_outcome"]
                    raw_score = out.get("score")
                    score_val = float(raw_score) if raw_score is not None else None
                    raw_cost = out.get("cost_usd")
                    cost_val = round(float(raw_cost), 8) if raw_cost is not None else None
                    raw_tokens = out.get("completion_tokens")
                    tokens_val = int(raw_tokens) if raw_tokens is not None else 0

                    key = (canon_bname, full_prompt_hash)
                    p_entry = problems[key]
                    if not p_entry["prompt"]:
                        p_entry["prompt"] = prompt_snippet
                        p_entry["benchmark"] = canon_bname
                        p_entry["full_prompt_hash"] = full_prompt_hash
                    p_entry["raw_benchmarks"].add(bname)
                    p_entry["subsets"].add(subset_name)
                    p_entry["indices"].append((subset_name, idx, bname))
                    if mname == "openrouter":
                        p_entry["openrouter_present"] = True
                        continue
                    p_entry["by_model"][mname].append({
                        "model": mname,
                        "score": score_val,
                        "cost": cost_val,
                        "tokens": tokens_val,
                        "subset": subset_name,
                        "index": idx,
                        "raw_benchmark": bname
                    })

        used_task_ids = set()
        for (bname, fhash), pdata in sorted(problems.items()):
            # 选择稳定主索引（优先使用完整测试子集 test / test_3000 / hybrid / verified / v1 的 index）
            idx_candidates = sorted(
                set(pdata["indices"]),
                key=lambda x: (0 if x[0] in ("test", "test_3000", "hybrid", "verified", "v1") else 1, x[0], int(x[1]) if x[1].isdigit() else 999999, x[1])
            )
            primary_idx = idx_candidates[0][1] if idx_candidates else fhash[:8]
            base_task_id = f"llmroute_{bname}_{primary_idx}"
            if base_task_id in used_task_ids:
                task_id = f"llmroute_{bname}_{primary_idx}_{fhash[:8]}"
            else:
                task_id = base_task_id
            used_task_ids.add(task_id)

            # 对每个候选静态模型进行重复评测去重与冲突检测 (Rule 5 & Rule 6)
            dedup_evals = []
            for mname in sorted(pdata["by_model"].keys()):
                obs_list = [o for o in pdata["by_model"][mname] if o["score"] is not None]
                if not obs_list:
                    continue
                unique_sc = sorted(set((o["score"], o["cost"] if o["cost"] is not None else 0.0) for o in obs_list))
                scores_only = sorted(set(sc[0] for sc in unique_sc))
                costs_only = sorted(set(sc[1] for sc in unique_sc))
                if len(unique_sc) == 1:
                    s_val, c_val = unique_sc[0]
                    c_type = "ACTUAL_MEASURED_API_USD" if c_val > 0.0 else "UNMEASURED_OR_LOCAL_FREE"
                    dedup_evals.append({
                        "model": mname,
                        "score": s_val,
                        "score_min": s_val,
                        "score_max": s_val,
                        "score_conflict": False,
                        "score_status": "VALID_MEASURED_DEDUP" if len(obs_list) > 1 else "VALID_MEASURED",
                        "cost": c_val,
                        "cost_min": c_val,
                        "cost_max": c_val,
                        "cost_conflict": False,
                        "cost_type": c_type,
                        "observations_count": len(obs_list)
                    })
                else:
                    # 同一模型存在不同评分或不同费用冲突：严禁任意取首条、最大分或最低价 (Rule 6)
                    dedup_evals.append({
                        "model": mname,
                        "score": scores_only[0] if len(scores_only) == 1 else None,
                        "score_min": min(scores_only),
                        "score_max": max(scores_only),
                        "score_conflict": len(scores_only) > 1,
                        "score_status": "CONFLICTING_SCORE_OBSERVATIONS" if len(scores_only) > 1 else "VALID_SCORE_CONFLICTING_COST",
                        "cost": costs_only[0] if len(costs_only) == 1 else None,
                        "cost_min": min(costs_only),
                        "cost_max": max(costs_only),
                        "cost_conflict": len(costs_only) > 1,
                        "cost_type": "CONFLICTING_COST_OBSERVATIONS" if len(costs_only) > 1 else ("ACTUAL_MEASURED_API_USD" if costs_only[0] > 0.0 else "UNMEASURED_OR_LOCAL_FREE"),
                        "observations_count": len(obs_list),
                        "conflicting_pairs": unique_sc
                    })

            num_cand = len(dedup_evals)
            candidate_distribution_unfiltered[num_cand] += 1
            if num_cand < 2:
                llmroute_selection_counts["FEWER_THAN_2_MODELS"] += 1
                continue

            max_score = max(e["score_max"] for e in dedup_evals)
            top_evals = [e for e in dedup_evals if e["score_max"] == max_score]
            is_all_failed = (max_score <= 0.0)
            is_strictly_unique_winner = False
            tied_group = []
            supervision_regime = None

            if is_all_failed:
                best_eval = top_evals[0]
                best_model = best_eval["model"]
                selection_rule = "ALL_MODELS_FAILED"
                cost_comparison_status = "ALL_FAILED"
            elif any(e["score_conflict"] for e in top_evals):
                # 潜在最高分模型存在评分冲突，无法确定合法胜者，转入分析集合 (Rule 7)
                best_eval = top_evals[0]
                best_model = best_eval["model"]
                selection_rule = "CONFLICTING_MODEL_SCORE_UNRESOLVED"
                cost_comparison_status = "SCORE_CONFLICT_IN_TOP_CANDIDATES"
                tied_group = top_evals
            elif len(top_evals) == 1:
                best_eval = top_evals[0]
                best_model = best_eval["model"]
                if best_eval["cost_conflict"]:
                    # 唯一最高分模型自身存在费用冲突，保守隔离至分析集 (Rule 6 & Rule 7)
                    selection_rule = "CONFLICTING_WINNER_COST_UNRESOLVED"
                    cost_comparison_status = "COST_CONFLICT_IN_UNIQUE_TOP_CANDIDATE"
                    is_strictly_unique_winner = False
                    tied_group = [best_eval]
                else:
                    selection_rule = "UNIQUE_MAX_SCORE"
                    cost_comparison_status = "MEASURED_API_USD" if best_eval["cost_type"] == "ACTUAL_MEASURED_API_USD" else "LOCAL_UNMEASURED_COST"
                    is_strictly_unique_winner = True
                    supervision_regime = "Regime_B"
                    tied_group = [best_eval]
            else:
                if any(e["cost_conflict"] for e in top_evals):
                    # 并列最高分模型中存在费用冲突，禁止任意取最低价或首条，转入分析集 (Rule 6 & Rule 7)
                    best_eval = top_evals[0]
                    best_model = best_eval["model"]
                    selection_rule = "CONFLICTING_TIED_TOP_COST_UNRESOLVED"
                    cost_comparison_status = "COST_CONFLICT_IN_TIED_TOP_CANDIDATES"
                    is_strictly_unique_winner = False
                    tied_group = top_evals
                else:
                    all_api_usd = all(e["cost_type"] == "ACTUAL_MEASURED_API_USD" and e["cost"] is not None and e["cost"] > 0 for e in top_evals)
                    if all_api_usd:
                        min_cost = min(e["cost"] for e in top_evals)
                        min_cost_evals = [e for e in top_evals if e["cost"] == min_cost]
                        best_eval = min_cost_evals[0]
                        best_model = best_eval["model"]
                        tied_group = min_cost_evals
                        if len(min_cost_evals) == 1:
                            selection_rule = "TIED_SCORE_MIN_MEASURED_API_USD"
                            cost_comparison_status = "MEASURED_API_USD_LOWEST"
                            is_strictly_unique_winner = True
                            supervision_regime = "Regime_C"
                        else:
                            selection_rule = "TIED_SCORE_TIED_API_USD"
                            cost_comparison_status = "MEASURED_API_USD_TIED"
                            is_strictly_unique_winner = False
                    else:
                        best_eval = top_evals[0]
                        best_model = best_eval["model"]
                        tied_group = top_evals
                        selection_rule = "TIED_SCORE_COST_UNCOMPARED"
                        cost_comparison_status = "COST_UNCOMPARED_UNMEASURED_LOCAL"
                        is_strictly_unique_winner = False

            llmroute_selection_counts[selection_rule] += 1
            best_score = best_eval["score"]
            best_cost = best_eval["cost"]
            best_cost_type = best_eval["cost_type"]

            criteria = {e["model"]: "" for e in dedup_evals}
            tied_models = [e["model"] for e in tied_group]
            target_dist = None
            if not is_strictly_unique_winner and len(tied_models) > 1:
                tied_set = set(tied_models)
                w = round(1.0 / len(tied_models), 6)
                target_dist = {e["model"]: (w if e["model"] in tied_set else 0.0) for e in dedup_evals}

            label_nature = "multi_model_quality_then_measured_api_cost" if is_strictly_unique_winner else (
                "multi_model_all_failed_unsupervised" if is_all_failed else "multi_model_tied_or_conflicted_analysis"
            )

            model_choice_q = {
                "type": "choice",
                "instructions": f"Select the optimal model for this {bname} problem balancing score and cost.",
                "criteria": criteria,
                "label": best_model
            }
            if target_dist is not None:
                model_choice_q["target"] = target_dist

            # P2.3: Stage 1 纯静态导出不得把事后多模型解出率生成的 difficulty_tier 作为主训练问题
            kev_record = {
                "provenance": {
                    "source_id": "ROUTE-001",
                    "source_name": "LLMRouterBench",
                    "raw_file": f"ROUTE-001_LLMRouterBench/{bname}",
                    "source_record_id": f"{bname}_{primary_idx}_{fhash}",
                    "selection_rule": selection_rule,
                    "label_nature": label_nature,
                    "supervision_regime": supervision_regime,
                    "benchmark_name": bname,
                    "raw_benchmarks_merged": sorted(pdata["raw_benchmarks"]),
                    "subsets_merged": sorted(pdata["subsets"]),
                    "instance_index": primary_idx,
                    "full_prompt_hash": fhash,
                    "task_id": task_id,
                },
                "state": f"Benchmark: {bname}.\nTask Prompt: {pdata['prompt']}",
                "questions": {
                    "model_choice": model_choice_q,
                },
                "expected": {
                    "model_choice": best_model,
                },
                "_meta": {
                    "source_id": "ROUTE-001",
                    "num_candidates": len(dedup_evals),
                    "candidates": [e["model"] for e in dedup_evals],
                    "evals_summary": dedup_evals[:10],
                    "winner": best_model if is_strictly_unique_winner else None,
                    "tied_winners": tied_models if len(tied_models) > 1 else ([best_model] if is_strictly_unique_winner else []),
                    "num_tied_winners": len(tied_models),
                    "target_distribution": target_dist,
                    "winner_score": best_score,
                    "winner_cost": best_cost,
                    "winner_cost_type": best_cost_type,
                    "cost_comparison_status": cost_comparison_status,
                    "all_models_failed": is_all_failed,
                    "is_deterministic_positive_oracle": is_strictly_unique_winner,
                    "selection_rule": selection_rule,
                    "label_nature": label_nature,
                    "supervision_regime": supervision_regime
                }
            }
            if target_dist is not None:
                kev_record["gold"] = {
                    "model_choice": {"probabilities": target_dist},
                }

            task_pool[task_id] = kev_record
            if is_strictly_unique_winner:
                candidate_distribution_filtered[len(dedup_evals)] += 1
                task_pool_training[task_id] = kev_record
            else:
                task_pool_unsupervised[task_id] = kev_record

    # -------------------------------------------------------------
    # C. ROUTE-002: RouterBench 0-shot (排除 87 条同分同费并列 + 固定种子确定性打乱候选顺序)
    # -------------------------------------------------------------
    routerbench_file = os.path.join(cleaned_root, "路由比较", "ROUTE-002_RouterBench", "cleaned_routerbench.jsonl")
    if os.path.exists(routerbench_file):
        print(f"[Views] 读取 ROUTE-002 RouterBench 官方路由评测: {routerbench_file}")
        routerbench_prompt_by_id = {}
        routerbench_raw_file = os.path.join(raw_root, "ROUTE-002_RouterBench", "routerbench_0shot.pkl")
        if os.path.exists(routerbench_raw_file):
            import pickle
            with open(routerbench_raw_file, "rb") as raw_f:
                raw_df = pickle.load(raw_f)
            for _, raw_row in raw_df.iterrows():
                raw_prompt = raw_row.get("prompt")
                prompt_text = ""
                if isinstance(raw_prompt, str):
                    try:
                        import ast
                        parsed = ast.literal_eval(raw_prompt)
                        if isinstance(parsed, (list, tuple)) and parsed:
                            prompt_text = str(parsed[-1]).strip()
                        else:
                            prompt_text = raw_prompt.strip()
                    except Exception:
                        prompt_text = raw_prompt.strip()
                elif isinstance(raw_prompt, (list, tuple)) and raw_prompt:
                    prompt_text = str(raw_prompt[-1]).strip()
                else:
                    prompt_text = str(raw_prompt or "").strip()
                routerbench_prompt_by_id[str(raw_row.get("sample_id") or "unknown")] = prompt_text.replace("\u2028", "").replace("\u2029", "").replace("\n", " ").strip()
        with open(routerbench_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                sid = r["provenance"]["sample_id"]
                ename = r["provenance"]["eval_name"]
                obs = r["observed_decision"]
                oracle = obs.get("oracle_model_to_route_to")
                cand_evals = r.get("candidate_evaluations") or {}
                prompt = routerbench_prompt_by_id.get(sid, r["pre_decision_state"]["prompt_snippet"])

                candidate_distribution_unfiltered[len(cand_evals)] += 1
                if oracle == "no_model_correct" or not oracle or not cand_evals:
                    routerbench_selection_counts["NO_MODEL_CORRECT_EXCLUDED"] += 1
                    continue
                if oracle not in cand_evals:
                    routerbench_selection_counts["ORACLE_NOT_IN_CANDIDATES"] += 1
                    continue

                max_score = max(float(v.get("score") or 0.0) for v in cand_evals.values())
                if max_score <= 0.0:
                    routerbench_selection_counts["NO_MODEL_CORRECT_EXCLUDED"] += 1
                    continue

                top_cands = [m for m, v in cand_evals.items() if float(v.get("score") or 0.0) == max_score]
                min_cost = min(float(cand_evals[m].get("cost_usd") or 0.0) for m in top_cands)
                min_cost_cands = [m for m in top_cands if float(cand_evals[m].get("cost_usd") or 0.0) == min_cost]

                task_id = f"routerbench_{sid}"
                # P2.4: 对 ROUTE-002 的固定候选列表做确定性随机打乱，消除固定首尾位置偏置
                shuffled_cands = list(cand_evals.keys())
                cand_rng_seed = int(hashlib.sha256(f"r002_cand_shuffle_{task_id}_{args.seed}".encode("utf-8")).hexdigest()[:16], 16)
                random.Random(cand_rng_seed).shuffle(shuffled_cands)
                criteria = {m: "" for m in shuffled_cands}

                if len(min_cost_cands) > 1:
                    # P1 (历史已定稿): 排除 87 条同分同费并列样本，归入分析池
                    routerbench_selection_counts["ROUTERBENCH_TIED_SCORE_TIED_COST_EXCLUDED"] += 1
                    w = round(1.0 / len(min_cost_cands), 6)
                    target_dist = {m: (w if m in min_cost_cands else 0.0) for m in shuffled_cands}
                    kev_record = {
                        "provenance": {
                            "source_id": "ROUTE-002",
                            "source_name": "RouterBench",
                            "raw_file": "ROUTE-002_RouterBench/routerbench_0shot.pkl",
                            "source_record_id": str(sid),
                            "selection_rule": "ROUTERBENCH_TIED_SCORE_TIED_COST_EXCLUDED",
                            "label_nature": "tied_score_tied_cost_soft_or_analysis",
                            "supervision_regime": None,
                            "sample_id": sid,
                            "eval_name": ename,
                            "task_id": task_id,
                        },
                        "state": f"Evaluation task: {ename}.\nProblem input: {prompt}",
                        "questions": {
                            "model_choice": {
                                "type": "choice",
                                "instructions": f"Select the optimal cost-effective model for this {ename} problem.",
                                "criteria": criteria,
                                "label": min_cost_cands[0],
                                "target": target_dist
                            }
                        },
                        "expected": {
                            "model_choice": min_cost_cands[0]
                        },
                        "_meta": {
                            "source_id": "ROUTE-002",
                            "num_candidates": len(criteria),
                            "candidates": shuffled_cands,
                            "evals_summary": cand_evals,
                            "winner": None,
                            "tied_winners": min_cost_cands,
                            "num_tied_winners": len(min_cost_cands),
                            "is_deterministic_oracle": False,
                            "selection_rule": "ROUTERBENCH_TIED_SCORE_TIED_COST_EXCLUDED",
                            "label_nature": "tied_score_tied_cost_soft_or_analysis"
                        }
                    }
                    task_pool[task_id] = kev_record
                    task_pool_unsupervised[task_id] = kev_record
                    continue

                winner_model = min_cost_cands[0]
                is_unique_max = (len(top_cands) == 1)
                sel_rule = "ROUTERBENCH_UNIQUE_MAX_SCORE" if is_unique_max else "ROUTERBENCH_TIED_SCORE_MIN_COST"
                sup_regime = "Regime_B" if is_unique_max else "Regime_C"
                routerbench_selection_counts["ROUTERBENCH_OFFICIAL_ORACLE"] += 1
                routerbench_selection_counts[sel_rule] += 1
                candidate_distribution_filtered[len(cand_evals)] += 1

                kev_record = {
                    "provenance": {
                        "source_id": "ROUTE-002",
                        "source_name": "RouterBench",
                        "raw_file": "ROUTE-002_RouterBench/routerbench_0shot.pkl",
                        "source_record_id": str(sid),
                        "selection_rule": sel_rule,
                        "label_nature": "official_oracle_cost_effective",
                        "supervision_regime": sup_regime,
                        "sample_id": sid,
                        "eval_name": ename,
                        "task_id": task_id,
                    },
                    "state": f"Evaluation task: {ename}.\nProblem input: {prompt}",
                    "questions": {
                        "model_choice": {
                            "type": "choice",
                            "instructions": f"Select the optimal cost-effective model for this {ename} problem.",
                            "criteria": criteria,
                            "label": winner_model
                        }
                    },
                    "expected": {
                        "model_choice": winner_model
                    },
                    "_meta": {
                        "source_id": "ROUTE-002",
                        "num_candidates": len(criteria),
                        "candidates": shuffled_cands,
                        "evals_summary": cand_evals,
                        "winner": winner_model,
                        "is_deterministic_oracle": True,
                        "selection_rule": sel_rule,
                        "label_nature": "official_oracle_cost_effective",
                        "supervision_regime": sup_regime
                    }
                }
                task_pool[task_id] = kev_record
                task_pool_training[task_id] = kev_record

    # -------------------------------------------------------------
    # D. TRA-004: AgentSuite 273 独立任务 × 30 模型全 Episode 对比 (Stage 1 纯静态全部隔离至分析池)
    # -------------------------------------------------------------
    agentsuite_file = os.path.join(cleaned_root, "Agent轨迹", "TRA-004_AgentSuite", "cleaned_trajectories.jsonl")
    agentsuite_episodes_by_task = defaultdict(list)
    agentsuite_step_samples = []
    if os.path.exists(agentsuite_file):
        print(f"[Views] 读取 TRA-004 AgentSuite 任务级 Episode 对照 (Stage 1 纯静态隔离至分析集): {agentsuite_file}")
        episodes_map = defaultdict(lambda: {"steps": 0, "success": False, "score": 0.0, "axis": "", "prompt": "", "model": "", "thinking": ""})
        with open(agentsuite_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                prov = r["provenance"]
                inst_id = prov["instance_id"]
                mname = prov["model_name"]
                tmode = prov["reasoning_effort_mode"]
                step_idx = prov["step_index"]
                pre = r["pre_decision_state"]
                out = r["ground_truth_outcome"]

                if len(agentsuite_step_samples) < 50:
                    agentsuite_step_samples.append(r)

                ep_key = (inst_id, mname, tmode)
                ep = episodes_map[ep_key]
                ep["steps"] = max(ep["steps"], step_idx)
                if out.get("is_success") is True:
                    ep["success"] = True
                score_v = out.get("eval_score")
                if score_v is not None and score_v > ep["score"]:
                    ep["score"] = score_v
                ep["axis"] = prov.get("task_axis", "")
                ep["prompt"] = pre.get("initial_prompt_snippet", "")
                ep["model"] = mname
                ep["thinking"] = tmode

        for (inst_id, mname, tmode), ep in episodes_map.items():
            agentsuite_episodes_by_task[inst_id].append({
                "model": mname,
                "thinking_mode": tmode,
                "is_success": ep["success"],
                "score": ep["score"],
                "total_steps": ep["steps"],
                "axis": ep["axis"],
                "prompt": ep["prompt"]
            })

        STRICT_SAME_CHECKPOINT_THINKING_SWITCH_PAIRS = [
            ("DeepSeek-V3.2-Exp", "thinking-off", "DeepSeek-V3.2-Exp", "thinking-on"),
            ("claude-4-opus", "thinking-off", "claude-4-opus", "thinking-on-10k"),
            ("claude-4-sonnet", "thinking-off", "claude-4-sonnet", "thinking-on-10k"),
            ("claude-4.5-sonnet", "thinking-off", "claude-4.5-sonnet", "thinking-on-10k"),
            ("gemini-2.5-flash", "thinking-off", "gemini-2.5-flash", "thinking-on"),
        ]
        DEDICATED_THINKING_CHECKPOINT_PAIRS = [
            ("Qwen3-235B-A22B-Instruct-2507-FP8", "standard", "Qwen3-235B-A22B-Thinking-2507-FP8", "thinking-on"),
        ]
        GENUINE_THINKING_PAIRS = STRICT_SAME_CHECKPOINT_THINKING_SWITCH_PAIRS + DEDICATED_THINKING_CHECKPOINT_PAIRS

        CROSS_VERSION_OR_VARIANT_PAIRS = [
            ("DeepSeek-V3", "standard", "DeepSeek-R1", "thinking-on"),
            ("glm-4.5-air", "thinking-on", "glm-4.5", "thinking-on"),
            ("claude-4-sonnet", "thinking-off", "claude-4.5-sonnet", "thinking-off"),
            ("claude-4-sonnet", "thinking-on-10k", "claude-4.5-sonnet", "thinking-on-10k"),
            ("Kimi-K2-0711", "standard", "Kimi-K2-0905", "standard"),
            ("Qwen3-235B-A22B-FP8", "thinking-on", "Qwen3-235B-A22B-Thinking-2507-FP8", "thinking-on"),
        ]

        strict_switch_contrasts = 0
        dedicated_ckpt_contrasts = 0
        cross_version_contrasts = 0

        for inst_id, eps in agentsuite_episodes_by_task.items():
            candidate_distribution_unfiltered[len(eps)] += 1
            ep_lookup = {(e["model"], e["thinking_mode"]): e for e in eps}
            task_contrasts = 0
            for (m1, t1, m2, t2) in STRICT_SAME_CHECKPOINT_THINKING_SWITCH_PAIRS:
                if (m1, t1) in ep_lookup and (m2, t2) in ep_lookup:
                    task_contrasts += 1
                    strict_switch_contrasts += 1
            for (m1, t1, m2, t2) in DEDICATED_THINKING_CHECKPOINT_PAIRS:
                if (m1, t1) in ep_lookup and (m2, t2) in ep_lookup:
                    task_contrasts += 1
                    dedicated_ckpt_contrasts += 1
            for (m1, t1, m2, t2) in CROSS_VERSION_OR_VARIANT_PAIRS:
                if (m1, t1) in ep_lookup and (m2, t2) in ep_lookup:
                    cross_version_contrasts += 1
            agentsuite_thinking_contrasts += task_contrasts

            task_id = f"agentsuite_{inst_id}"
            criteria = {f"{e['model']}_{e['thinking_mode']}": "" for e in eps}
            success_eps = [e for e in eps if e["is_success"]]

            if not success_eps:
                winner_status = "ZERO_SUCCESS"
                selection_rule = "AGENTSUITE_ALL_FAILED"
                agentsuite_selection_counts[selection_rule] += 1
                placeholder_label = list(criteria.keys())[0]
                label_nature = "episode_all_failed_unsupervised"
            else:
                min_steps = min(e["total_steps"] for e in success_eps)
                max_score = max(e["score"] for e in success_eps)
                top_eps = [e for e in success_eps if e["total_steps"] == min_steps and e["score"] == max_score]
                if len(top_eps) == 1:
                    winner_status = "UNIQUE_WINNER_STAGE2_ISOLATED"
                    selection_rule = "AGENTSUITE_UNIQUE_SUCCESSFUL_MODEL_STAGE2_ISOLATED"
                    agentsuite_selection_counts["AGENTSUITE_UNIQUE_SUCCESSFUL_MODEL"] += 1
                    placeholder_label = f"{top_eps[0]['model']}_{top_eps[0]['thinking_mode']}"
                    label_nature = "episode_unique_success_stage2_only"
                else:
                    winner_status = "TIED_SUCCESS_UNDIFFERENTIATED"
                    selection_rule = "TIED_MULTI_SUCCESS_UNDIFFERENTIATED"
                    agentsuite_selection_counts[selection_rule] += 1
                    placeholder_label = f"{top_eps[0]['model']}_{top_eps[0]['thinking_mode']}"
                    label_nature = "episode_tied_winners_soft_or_analysis"

            kev_record = {
                "provenance": {
                    "source_id": "TRA-004",
                    "source_name": "AgentSuite multi_challenge",
                    "raw_file": "TRA-004_AgentSuite/multi_challenge_*.jsonl",
                    "source_record_id": str(inst_id),
                    "selection_rule": selection_rule,
                    "label_nature": label_nature,
                    "instance_id": inst_id,
                    "task_axis": eps[0]["axis"] if eps else "unknown",
                    "task_id": task_id,
                },
                "state": f"Task domain: multi_challenge_agent. Task ID: {inst_id}.\nPrompt: {eps[0]['prompt'] if eps else ''}",
                "questions": {
                    "model_choice": {
                        "type": "choice",
                        "instructions": "Select the optimal agent model and thinking mode for this task.",
                        "criteria": criteria,
                        "label": placeholder_label
                    }
                },
                "expected": {
                    "model_choice": placeholder_label
                },
                "_meta": {
                    "source_id": "TRA-004",
                    "num_candidates": len(eps),
                    "candidates": list(criteria.keys()),
                    "winner": placeholder_label if "UNIQUE_SUCCESSFUL" in selection_rule else None,
                    "winner_status": winner_status,
                    "is_deterministic_oracle": "UNIQUE_SUCCESSFUL" in selection_rule,
                    "cost_status": "UNMEASURED_AGENT_EXECUTION_COST",
                    "selection_rule": selection_rule,
                    "label_nature": label_nature
                }
            }
            task_pool[task_id] = kev_record
            # Stage 1 纯静态路由隔离全部 273 条多步 (model, thinking_mode) 轨迹任务
            task_pool_unsupervised[task_id] = kev_record

    # -------------------------------------------------------------
    # E. ROUTE-003: TwinRouterBench (970 步) 强制作为 EVAL_BENCHMARK_ONLY 隔离评测集
    # -------------------------------------------------------------
    twin_file = os.path.join(cleaned_root, "路由比较", "ROUTE-003_TwinRouterBench", "cleaned_twin_bench.jsonl")
    twin_holdout_records = []
    if os.path.exists(twin_file):
        print(f"[Views] 读取 ROUTE-003 TwinRouterBench 隔离评测基准: {twin_file}")
        with open(twin_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                prov = r["provenance"]
                pre = r["pre_decision_state"]
                obs = r["observed_decision"]
                target_tier = obs.get("target_tier", "mid")
                tier_id = obs.get("target_tier_id", 1)
                inst_id = prov.get("instance_id", "unknown")
                step_idx = prov.get("step_index", 1)

                h_record = {
                    "provenance": {
                        "source_id": "ROUTE-003",
                        "source_name": "TwinRouterBench",
                        "raw_file": "ROUTE-003_TwinRouterBench/swebench_rates.json",
                        "source_record_id": f"{inst_id}_step_{step_idx}",
                        "selection_rule": "TWINROUTERBENCH_STEP_TIER_ORACLE",
                        "label_nature": "step_capability_tier_oracle",
                        "instance_id": inst_id,
                        "step_index": step_idx,
                        "split": "test_twinrouterbench_holdout",
                        "policy_tag": "EVAL_BENCHMARK_ONLY",
                    },
                    "state": f"Benchmark: {pre.get('benchmark', 'swebench')}, Step: {pre.get('step_index', 1)}.\nContext: {pre.get('messages_snippet', '')}",
                    "questions": {
                        "routing_tier_choice": {
                            "type": "choice",
                            "instructions": "Select the optimal LLM capability tier for this SWE-bench step.",
                            "criteria": {
                                "low": "Tier 0: Fast / lightweight model for simple shell commands",
                                "mid": "Tier 1: Mid-sized model for standard edits and search",
                                "mid_high": "Tier 2: Advanced model for complex logic and tool calling",
                                "high": "Tier 3: Flagship model for difficult code comprehension and patches"
                            },
                            "label": target_tier
                        },
                        "routing_tier_score": {
                            "type": "score",
                            "instructions": "Routing tier level from 0 (low) to 3 (high).",
                            "criteria": ["low", "mid", "mid_high", "high"],
                            "label": tier_id
                        }
                    },
                    "expected": {
                        "routing_tier_choice": target_tier,
                        "routing_tier_score": tier_id
                    }
                }
                twin_holdout_records.append(h_record)

        write_jsonl(os.path.join(stage1_out_dir, "test_twinrouterbench_holdout.jsonl"), twin_holdout_records)
        print(f"[Stage1] TwinRouterBench 隔离评测集导出: {len(twin_holdout_records)} 条 -> {stage1_out_dir} (0 条进入 train/val)")

    # -------------------------------------------------------------
    # 2. 严格按规范化 Prompt 语义指纹与完整题目哈希进行 80 / 10 / 10 隔离划分
    # -------------------------------------------------------------
    train_records = []
    val_records = []
    test_records = []

    split_counts = {
        "train": {"total": 0, "by_source": Counter(), "by_regime": Counter(), "tasks": set(), "exact_prompts": set(), "canon_prompts": set(), "full_hashes": set()},
        "val": {"total": 0, "by_source": Counter(), "by_regime": Counter(), "tasks": set(), "exact_prompts": set(), "canon_prompts": set(), "full_hashes": set()},
        "test": {"total": 0, "by_source": Counter(), "by_regime": Counter(), "tasks": set(), "exact_prompts": set(), "canon_prompts": set(), "full_hashes": set()},
        "holdout": {"total": len(twin_holdout_records), "by_source": Counter({"ROUTE-003": len(twin_holdout_records)}), "tasks": {r["provenance"]["instance_id"] for r in twin_holdout_records}}
    }

    def extract_raw_prompt_from_state(state_str):
        for sep in ("Task Prompt: ", "Problem input: ", "Prompt: "):
            if sep in state_str:
                return state_str.split(sep, 1)[-1]
        return state_str

    def normalize_prompt_pair(state_str):
        p_text = extract_raw_prompt_from_state(state_str).replace("\u2028", "").replace("\u2029", "")
        norm_exact = " ".join(p_text.strip().lower().split())
        word_canon = re.sub(r"[\s\.,!\?;:\"'`~]+", " ", norm_exact).strip()
        canon_key = word_canon if len(word_canon) >= 2 else norm_exact
        return norm_exact, canon_key

    def get_semantic_split_key(item):
        norm_exact, canon_key = normalize_prompt_pair(item.get("state", ""))
        if canon_key:
            return f"sem_{hashlib.sha256(canon_key.encode('utf-8')).hexdigest()[:16]}"
        return item["provenance"].get("task_id", str(id(item)))

    prompt_to_sources = defaultdict(set)
    prompt_to_splits = defaultdict(set)

    print(f"\n[Split] 开始执行 80/10/10 严格单胜者哈希隔离划分 (Stage 1 纯静态 Scheme B 监督子集: {len(task_pool_training):,} 任务)...")
    for task_id in sorted(task_pool_training.keys()):
        item = task_pool_training[task_id]
        src_id = item["provenance"]["source_id"]
        sup_regime = item["provenance"].get("supervision_regime", "UNKNOWN")
        fhash = item["provenance"].get("full_prompt_hash")
        norm_exact, canon_key = normalize_prompt_pair(item.get("state", ""))
        split_key = get_semantic_split_key(item)
        h_val = int(hashlib.sha256(f"{split_key}_{args.seed}".encode("utf-8")).hexdigest()[:8], 16) / 0xffffffff

        clean_item = {
            "provenance": {**item["provenance"]},
            "state": item["state"],
            "questions": item["questions"],
            "expected": item["expected"]
        }

        if h_val < 0.80:
            split_name = "train"
            clean_item["provenance"]["split"] = "train"
            train_records.append(clean_item)
        elif h_val < 0.90:
            split_name = "val"
            clean_item["provenance"]["split"] = "val"
            val_records.append(clean_item)
        else:
            split_name = "test"
            clean_item["provenance"]["split"] = "test"
            test_records.append(clean_item)

        split_counts[split_name]["total"] += 1
        split_counts[split_name]["by_source"][src_id] += 1
        split_counts[split_name]["by_regime"][sup_regime] += 1
        split_counts[split_name]["tasks"].add(task_id)
        if fhash:
            split_counts[split_name]["full_hashes"].add(fhash)
        if norm_exact:
            split_counts[split_name]["exact_prompts"].add(norm_exact)
            prompt_to_sources[norm_exact].add(src_id)
            prompt_to_splits[norm_exact].add(split_name)
        if canon_key:
            split_counts[split_name]["canon_prompts"].add(canon_key)

    write_jsonl(os.path.join(stage1_out_dir, "train.jsonl"), train_records)
    write_jsonl(os.path.join(stage1_out_dir, "val.jsonl"), val_records)
    write_jsonl(os.path.join(stage1_out_dir, "test.jsonl"), test_records)
    with open(os.path.join(stage1_out_dir, "analysis_unsupervised_or_tied.jsonl"), "w", encoding="utf-8") as f:
        for tid in sorted(task_pool_unsupervised.keys()):
            f.write(json.dumps(task_pool_unsupervised[tid], ensure_ascii=False) + "\n")

    print(f"[Stage1] 修复版纯静态 Scheme B 导出目录: {stage1_out_dir}")
    print(f"[Stage1] 训练集 (train.jsonl): {len(train_records):,} 样本 (By source: {dict(split_counts['train']['by_source'])}, By regime: {dict(split_counts['train']['by_regime'])})")
    print(f"[Stage1] 验证集 (val.jsonl):   {len(val_records):,} 样本 (By source: {dict(split_counts['val']['by_source'])}, By regime: {dict(split_counts['val']['by_regime'])})")
    print(f"[Stage1] 测试集 (test.jsonl):  {len(test_records):,} 样本 (By source: {dict(split_counts['test']['by_source'])}, By regime: {dict(split_counts['test']['by_regime'])})")
    print(f"[Stage1] 全败/并列/冲突/Stage2隔离分析集: {len(task_pool_unsupervised):,} 任务 -> {stage1_out_dir}/analysis_unsupervised_or_tied.jsonl")

    # 执行全量内置 CPU 校验（Kev & Laya 100% 样本官方编码器校验，Laya 显式验证 --max-len 1024 --head-max-len 512）
    compat_report = validate_kev_exports(stage1_out_dir, laya_root=stage1_out_dir)

    return write_stage1_report(
        args, stage1_out_dir, split_counts, prompt_to_sources, prompt_to_splits,
        candidate_distribution_unfiltered, routerbench_selection_counts, task_pool,
        task_pool_training, task_pool_unsupervised, train_records, val_records, test_records,
        twin_holdout_records, llmroute_selection_counts, compat_report,
    )
