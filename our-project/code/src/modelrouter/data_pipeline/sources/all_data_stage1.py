"""Export the aligned ROUTE-001/002 Stage 1 choice, score, and pairwise views."""

import hashlib
import json
import os
import random
import re
import shutil
import sys
from collections import Counter, defaultdict

from .all_data_shared import (PUBLIC_FILES, _dump, _load_stage1_reference, _route001_groups,
                              _routerbench_prompts, _semantic_split, _shuffled_criteria,
                              _soft_distribution, _stage_dir)


def _build_stage1_all_views(out_dir, stage1_dir, raw_root, cleaned_root):
    """Build aligned Stage 1 views (choice, recomputed_route001, pairwise, score, soft_target) for general + Laya + Kev."""
    r1_choice_by_key, r2_split_by_sid, r1_unsup_by_key, _ = _load_stage1_reference(stage1_dir)

    choice_dir = _stage_dir(out_dir, "stage1_choice")
    pair_dir = _stage_dir(out_dir, "stage1_pairwise")
    score_dir = _stage_dir(out_dir, "stage1_score")

    laya_choice_dir = _stage_dir(out_dir, "laya", "stage1_choice")
    laya_pair_dir = _stage_dir(out_dir, "laya", "stage1_pairwise")
    laya_soft_dir = _stage_dir(out_dir, "laya", "stage1_soft_target")

    kev_choice_dir = _stage_dir(out_dir, "kev", "stage1_choice")
    kev_pair_dir = _stage_dir(out_dir, "kev", "stage1_pairwise")
    kev_soft_dir = _stage_dir(out_dir, "kev", "stage1_soft_target")

    splits = ("train", "val", "test")
    stats = Counter()

    # 1. Stage 1 Choice (copy base + generate recomputed_route001 + Laya/Kev stage1_choice)
    recomp_handles = {sp: open(os.path.join(choice_dir, f"recomputed_route001_{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    laya_choice_h = {sp: open(os.path.join(laya_choice_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_choice_h = {sp: open(os.path.join(kev_choice_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}

    for sp in splits:
        src_fp = os.path.join(stage1_dir, f"{sp}.jsonl")
        dst_fp = os.path.join(choice_dir, f"{sp}.jsonl")
        shutil.copyfile(src_fp, dst_fp)
        with open(src_fp, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                prov = dict(r.get("provenance") or r.get("_meta") or {})
                source_id = prov.get("source_id") or prov.get("source") or "unknown"
                task_id = str(prov.get("task_id") or "")
                qdef = r["questions"]["model_choice"]
                winner = r.get("expected", {}).get("model_choice") or qdef.get("label") or prov.get("winner")
                criteria = qdef["criteria"]
                instructions = qdef["instructions"]
                meta = dict(prov, source=source_id, source_id=source_id, task_id=task_id, winner=winner, split=sp)
                if source_id == "ROUTE-001":
                    bm = str(prov.get("benchmark_name") or prov.get("benchmark") or "unknown")
                    prov["benchmark"] = bm
                    recomp_row = {
                        "provenance": prov,
                        "state": r["state"],
                        "questions": {"model_choice": {"type": "choice", "instructions": instructions, "criteria": criteria, "label": winner}},
                        "expected": {"model_choice": winner},
                        "_meta": meta,
                    }
                    _dump(recomp_handles[sp], recomp_row)
                    stats[f"recomputed_route001_{sp}"] += 1
                    stats["recomputed_route001_total"] += 1

                laya_row = {
                    "provenance": prov,
                    "state": r["state"],
                    "questions": {"model_choice": {"type": "choice", "instructions": instructions, "criteria": criteria}},
                    "expected": {"model_choice": winner},
                    "_meta": meta,
                }
                kev_row = {
                    "provenance": prov,
                    "state": r["state"],
                    "questions": {"model_choice": {"type": "choice", "instructions": instructions, "criteria": criteria, "label": winner}},
                    "_meta": meta,
                }
                _dump(laya_choice_h[sp], laya_row)
                _dump(kev_choice_h[sp], kev_row)
                stats[f"choice_{sp}"] += 1

    for h in (*recomp_handles.values(), *laya_choice_h.values(), *kev_choice_h.values()):
        h.close()

    # 2. Stage 1 Score, Soft-Target, and Pairwise (ROUTE-001 + ROUTE-002 aligned)
    r1_groups = _route001_groups(raw_root, out_dir)
    r1_score_h = {sp: open(os.path.join(score_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    r2_score_h = {sp: open(os.path.join(score_dir, f"route002_{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    r1_pair_h = {sp: open(os.path.join(pair_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    r2_pair_h = {sp: open(os.path.join(pair_dir, f"route002_{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}

    laya_soft_h = {sp: open(os.path.join(laya_soft_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_soft_h = {sp: open(os.path.join(kev_soft_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    laya_pair_h = {sp: open(os.path.join(laya_pair_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_pair_h = {sp: open(os.path.join(kev_pair_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}

    for (bm, h), g in sorted(r1_groups.items()):
        unsup_info = r1_unsup_by_key.get((bm, h))
        if unsup_info and unsup_info.get("selection_rule") == "CONFLICTING_MODEL_SCORE_UNRESOLVED":
            stats["r1_excluded_score_conflict"] += 1
            continue
        scores_map = {m: float(s) for m, s in g["scores"].items() if m != "openrouter" and math.isfinite(float(s))}
        if len(scores_map) < 2:
            stats["r1_excluded_fewer_than_two"] += 1
            continue
        max_s = max(scores_map.values())
        if max_s <= 0.0:
            stats["r1_excluded_all_failed"] += 1
            continue
        if len(set(scores_map.values())) <= 1:
            stats["r1_excluded_all_tied_score"] += 1
            continue

        state_str = f"Benchmark: {bm}.\nTask Prompt: {g['prompt']}"
        if (bm, h) in r1_choice_by_key:
            sp, task_id, choice_rec = r1_choice_by_key[(bm, h)]
            c_prov = choice_rec.get("provenance") or choice_rec.get("_meta") or {}
            sel_rule = c_prov.get("selection_rule", "SINGLE_WINNER")
            sup_regime = c_prov.get("supervision_regime", "Regime_B")
            stats["r1_multi_score_from_choice"] += 1
        else:
            task_id = unsup_info["task_id"] if unsup_info else f"llmroute_{bm}_{h}"
            sel_rule = unsup_info["selection_rule"] if unsup_info else "TIED_SCORE_COST_UNCOMPARED"
            sup_regime = "Score_Comparison_Only"
            sp = _semantic_split(state_str, task_id, seed=42)
            stats["r1_multi_score_from_non_unique"] += 1
            stats[f"r1_non_unique_{sel_rule}"] += 1

        cands_sorted = sorted(scores_map.keys())
        prov = {
            "source_id": "ROUTE-001",
            "task_id": task_id,
            "benchmark": bm,
            "full_prompt_hash": h,
            "selection_rule": sel_rule,
            "supervision_regime": sup_regime,
            "split": sp,
        }
        _dump(r1_score_h[sp], {
            "provenance": prov,
            "state": state_str,
            "scores": {m: scores_map[m] for m in cands_sorted},
            "candidates": cands_sorted,
        })
        stats[f"r1_score_{sp}"] += 1
        stats["r1_score_total"] += 1

        crit = _shuffled_criteria(cands_sorted, task_id)
        dist, best_m = _soft_distribution(scores_map, list(crit.keys()))
        meta_soft = {
            "source": "ROUTE-001",
            "source_id": "ROUTE-001",
            "task_id": task_id,
            "benchmark": bm,
            "full_prompt_hash": h,
            "selection_rule": sel_rule,
            "supervision_regime": sup_regime,
            "supervision_type": "soft_target_score_distribution",
        }
        _dump(laya_soft_h[sp], {
            "provenance": prov,
            "state": state_str,
            "questions": {"model_choice": {"type": "choice", "instructions": "Select the best model for this benchmark task based on expected quality.", "criteria": crit}},
            "gold": {"model_choice": {"probabilities": dist}},
            "_meta": meta_soft,
        })
        _dump(kev_soft_h[sp], {
            "provenance": prov,
            "state": state_str,
            "questions": {"model_choice": {"type": "choice", "instructions": "Select the best model for this benchmark task based on expected quality.", "criteria": crit, "label": best_m, "target": dist}},
            "_meta": meta_soft,
        })
        stats[f"soft_target_{sp}"] += 1

        ranked = sorted(scores_map.items(), key=lambda x: (-x[1], x[0]))
        for (ma, sa), (mb, sb) in zip(ranked, ranked[1:]):
            if sa <= sb:
                continue
            pair_id = f"{task_id}:{ma}:{mb}"
            p_prov = dict(prov, pair_id=pair_id)
            _dump(r1_pair_h[sp], {
                "provenance": p_prov,
                "state": state_str,
                "question": {"type": "pairwise", "preferred": ma, "rejected": mb, "score_delta": round(sa - sb, 6)},
            })
            p_crit = _shuffled_criteria([ma, mb], pair_id)
            p_meta = dict(meta_soft, pair_id=pair_id, preferred=ma, rejected=mb, score_delta=round(sa - sb, 6), supervision_type="pairwise_quality_preference")
            _dump(laya_pair_h[sp], {
                "provenance": p_prov,
                "state": state_str,
                "questions": {"pairwise_choice": {"type": "choice", "instructions": "Select the higher-quality model between the two candidates for this task.", "criteria": p_crit}},
                "expected": {"pairwise_choice": ma},
                "_meta": p_meta,
            })
            _dump(kev_pair_h[sp], {
                "provenance": p_prov,
                "state": state_str,
                "questions": {"pairwise_choice": {"type": "choice", "instructions": "Select the higher-quality model between the two candidates for this task.", "criteria": p_crit, "label": ma}},
                "_meta": p_meta,
            })
            stats[f"r1_pair_{sp}"] += 1
            stats["r1_pair_total"] += 1
            stats[f"pairwise_{sp}"] += 1

    # ROUTE-002 Score, Soft-Target, and Pairwise (including the 87 tied-top-score&cost tasks)
    prompt_by_id = _routerbench_prompts(raw_root, stage1_dir)
    r2_cleaned_path = os.path.join(cleaned_root, PUBLIC_FILES["ROUTE-002"])
    with open(r2_cleaned_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            p = r.get("provenance", {})
            sid = str(p.get("sample_id") or "unknown")
            ev = r.get("candidate_evaluations") or {}
            scores_map = {m: float(v.get("score") or 0.0) for m, v in ev.items() if m != "openrouter"}
            if len(scores_map) < 2 or max(scores_map.values()) <= 0.0:
                continue
            if len(set(scores_map.values())) <= 1:
                stats["r2_excluded_all_tied_score"] += 1
                continue
            eval_name = str(r.get("pre_decision_state", {}).get("eval_name") or p.get("eval_name") or "routerbench")
            raw_p = prompt_by_id.get(sid, r.get("pre_decision_state", {}).get("prompt_snippet", ""))
            state_str = f"Evaluation task: {eval_name}.\nProblem input: {raw_p}"
            task_id = f"routerbench_{sid}"
            if sid in r2_split_by_sid:
                sp, task_id, choice_state = r2_split_by_sid[sid]
                if choice_state:
                    state_str = choice_state
                sel_rule = "SINGLE_WINNER"
                sup_regime = "Regime_B" if sum(1 for s in scores_map.values() if s == max(scores_map.values())) == 1 else "Regime_C"
                stats["r2_multi_score_from_choice"] += 1
            else:
                sp = _semantic_split(state_str, task_id, seed=42)
                sel_rule = "TIED_MAX_SCORE_AND_MIN_COST"
                sup_regime = "Score_Comparison_Only"
                stats["r2_multi_score_from_87_ties"] += 1

            cands_sorted = sorted(scores_map.keys())
            prov = {
                "source_id": "ROUTE-002",
                "task_id": task_id,
                "sample_id": sid,
                "benchmark": eval_name,
                "selection_rule": sel_rule,
                "supervision_regime": sup_regime,
                "split": sp,
            }
            _dump(r2_score_h[sp], {
                "provenance": prov,
                "state": state_str,
                "scores": {m: scores_map[m] for m in cands_sorted},
                "candidates": cands_sorted,
            })
            stats[f"r2_score_{sp}"] += 1
            stats["r2_score_total"] += 1

            crit = _shuffled_criteria(cands_sorted, task_id)
            dist, best_m = _soft_distribution(scores_map, list(crit.keys()))
            meta_soft = {
                "source": "ROUTE-002",
                "source_id": "ROUTE-002",
                "task_id": task_id,
                "sample_id": sid,
                "benchmark": eval_name,
                "selection_rule": sel_rule,
                "supervision_regime": sup_regime,
                "supervision_type": "soft_target_score_distribution",
            }
            _dump(laya_soft_h[sp], {
                "provenance": prov,
                "state": state_str,
                "questions": {"model_choice": {"type": "choice", "instructions": "Select the best model for this benchmark task based on expected quality.", "criteria": crit}},
                "gold": {"model_choice": {"probabilities": dist}},
                "_meta": meta_soft,
            })
            _dump(kev_soft_h[sp], {
                "provenance": prov,
                "state": state_str,
                "questions": {"model_choice": {"type": "choice", "instructions": "Select the best model for this benchmark task based on expected quality.", "criteria": crit, "label": best_m, "target": dist}},
                "_meta": meta_soft,
            })
            stats[f"soft_target_{sp}"] += 1

            ranked = sorted(scores_map.items(), key=lambda x: (-x[1], x[0]))
            for (ma, sa), (mb, sb) in zip(ranked, ranked[1:]):
                if sa <= sb:
                    continue
                pair_id = f"{task_id}:{ma}:{mb}"
                p_prov = dict(prov, pair_id=pair_id)
                _dump(r2_pair_h[sp], {
                    "provenance": p_prov,
                    "state": state_str,
                    "question": {"type": "pairwise", "preferred": ma, "rejected": mb, "score_delta": round(sa - sb, 6)},
                })
                p_crit = _shuffled_criteria([ma, mb], pair_id)
                p_meta = dict(meta_soft, pair_id=pair_id, preferred=ma, rejected=mb, score_delta=round(sa - sb, 6), supervision_type="pairwise_quality_preference")
                _dump(laya_pair_h[sp], {
                    "provenance": p_prov,
                    "state": state_str,
                    "questions": {"pairwise_choice": {"type": "choice", "instructions": "Select the higher-quality model between the two candidates for this task.", "criteria": p_crit}},
                    "expected": {"pairwise_choice": ma},
                    "_meta": p_meta,
                })
                _dump(kev_pair_h[sp], {
                    "provenance": p_prov,
                    "state": state_str,
                    "questions": {"pairwise_choice": {"type": "choice", "instructions": "Select the higher-quality model between the two candidates for this task.", "criteria": p_crit, "label": ma}},
                    "_meta": p_meta,
                })
                stats[f"r2_pair_{sp}"] += 1
                stats["r2_pair_total"] += 1
                stats[f"pairwise_{sp}"] += 1

    for h in (*r1_score_h.values(), *r2_score_h.values(), *r1_pair_h.values(), *r2_pair_h.values(),
              *laya_soft_h.values(), *kev_soft_h.values(), *laya_pair_h.values(), *kev_pair_h.values()):
        h.close()

    return stats
