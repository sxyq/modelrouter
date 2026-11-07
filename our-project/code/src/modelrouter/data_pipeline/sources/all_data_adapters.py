"""Materialize the single-agent, effort, and cache/cost adapter views."""

import csv
import json
import os
import re
import shutil
from collections import Counter, defaultdict

from .all_data_shared import PUBLIC_FILES, _dump, _split, _stage_dir


def _map_action_category(raw_action):
    a = str(raw_action or "").strip().lower()
    if a in ("bash", "execute_bash"):
        return "bash"
    if a == "str_replace_editor":
        return "str_replace_editor"
    if a in ("submit", "finish"):
        return "submit"
    if a in ("think", "text_response", "fetch"):
        return "other"
    return None

def _build_stage2_adapters(cleaned_root, out_dir):
    """Build Stage 2 Agent State auxiliary datasets (1 representative step per trajectory across 88,087 trajectories / 35,289 tasks)."""
    general_dir = _stage_dir(out_dir, "stage2_agent_state")
    laya_dir = _stage_dir(out_dir, "laya", "stage2_agent_state")
    kev_dir = _stage_dir(out_dir, "kev", "stage2_agent_state")

    splits = ("train", "val", "test")
    general_exist = all(os.path.exists(os.path.join(general_dir, f"{sp}.jsonl")) and os.path.getsize(os.path.join(general_dir, f"{sp}.jsonl")) > 0 for sp in splits)
    if not general_exist:
        files = [PUBLIC_FILES[x] for x in ("TRA-001", "TRA-002", "TRA-004")]
        task_counts = defaultdict(Counter)
        for rel in files:
            path = os.path.join(cleaned_root, rel)
            for line in open(path, encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                p = r["provenance"]
                key = str(p.get("instance_id") or p.get("task_id") or p.get("trajectory_id") or "unknown")
                task_counts[p.get("source_id", "unknown")][key] += 1
        handles = {s: open(os.path.join(general_dir, f"{s}.jsonl"), "w", encoding="utf-8") for s in splits}
        for rel in files:
            source = next(k for k, v in PUBLIC_FILES.items() if v == rel)
            path = os.path.join(cleaned_root, rel)
            for line in open(path, encoding="utf-8"):
                if not line.strip():
                    continue
                r = json.loads(line)
                p = r["provenance"]
                key = str(p.get("instance_id") or p.get("task_id") or p.get("trajectory_id") or "unknown")
                sp = _split(source + ":" + key)
                _dump(handles[sp], {
                    "provenance": p,
                    "state": r.get("pre_decision_state", {}),
                    "action": r.get("observed_decision", {}),
                    "outcome": r.get("ground_truth_outcome", {}),
                    "sample_weight": 1.0 / max(1, task_counts[source][key]),
                })
        for f in handles.values():
            f.close()

    # Now build trajectory-level deduplicated adapter views (88,087 trajectories across 35,289 tasks)
    laya_h = {sp: open(os.path.join(laya_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_h = {sp: open(os.path.join(kev_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    stats = Counter()

    action_criteria = {
        "bash": "Execute shell or bash command",
        "str_replace_editor": "Inspect or edit file with str_replace_editor",
        "submit": "Submit or finish patch",
        "other": "Internal reasoning, text response, or fetch",
    }
    resolved_criteria = {
        "false": "Trajectory execution does not resolve the task",
        "true": "Trajectory execution successfully resolves the task",
    }

    re_inst = re.compile(r'"instance_id":\s*"([^"]+)"')
    re_traj = re.compile(r'"trajectory_id":\s*"([^"]+)"')
    for source_id in ("TRA-001", "TRA-002", "TRA-004"):
        path = os.path.join(cleaned_root, PUBLIC_FILES[source_id])
        traj_rep = {}
        traj_len = Counter()
        task_trajs = defaultdict(set)
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                stats[f"raw_rows_{source_id}"] += 1
                stats["raw_rows_total"] += 1
                if source_id != "TRA-004":
                    head = line[:350]
                    mt = re_traj.search(head)
                    mi = re_inst.search(head)
                    if mt and mi:
                        traj_id = mt.group(1)
                        inst_id = mi.group(1)
                        traj_len[traj_id] += 1
                        if traj_id in traj_rep:
                            continue
                        task_trajs[inst_id].add(traj_id)
                        traj_rep[traj_id] = json.loads(line)
                        continue
                r = json.loads(line)
                p = r.get("provenance", {})
                inst_id = str(p.get("instance_id") or p.get("task_id") or "unknown")
                if source_id == "TRA-004":
                    traj_id = f"{inst_id}::{p.get('model_name')}::{p.get('reasoning_effort_mode')}"
                else:
                    traj_id = str(p.get("trajectory_id") or inst_id)
                traj_len[traj_id] += 1
                task_trajs[inst_id].add(traj_id)
                if traj_id not in traj_rep:
                    traj_rep[traj_id] = r

        for traj_id, r in sorted(traj_rep.items()):
            p = r.get("provenance", {})
            pre = r.get("pre_decision_state", {})
            obs = r.get("observed_decision", {})
            out = r.get("ground_truth_outcome", {})
            inst_id = str(p.get("instance_id") or p.get("task_id") or "unknown")
            sp = _split(source_id + ":" + inst_id)
            n_trajs = max(1, len(task_trajs[inst_id]))
            weight = round(1.0 / n_trajs, 6)

            state_obj = {
                "source_id": source_id,
                "task_domain": pre.get("task_domain", "software_engineering"),
                "agent_framework": p.get("agent_framework", "agent"),
                "executed_model": p.get("model_name", "unknown"),
                "reasoning_effort_mode": p.get("reasoning_effort_mode", "default"),
                "step_index": pre.get("step_index", 1),
                "context_chars": pre.get("context_chars", 0),
                "prior_tool_calls_count": pre.get("prior_tool_calls_count", 0),
                "prior_error_signals_count": pre.get("prior_error_signals_count", 0),
                "initial_prompt_snippet": str(pre.get("initial_prompt_snippet") or "")[:1200],
            }
            resolved_val = bool(out.get("task_resolved") if "task_resolved" in out else out.get("is_success", False))
            act_cat = _map_action_category(obs.get("action_type"))

            laya_q = {}
            laya_exp = {}
            kev_q = {}

            if act_cat is not None:
                laya_q["observed_action_type"] = {
                    "type": "choice",
                    "instructions": "Given the current agent execution state, predict the next observed tool/action category executed in this trajectory.",
                    "criteria": action_criteria,
                }
                laya_exp["observed_action_type"] = act_cat
                kev_q["observed_action_type"] = {
                    "type": "choice",
                    "instructions": "Given the current agent execution state, predict the next observed tool/action category executed in this trajectory.",
                    "criteria": action_criteria,
                    "label": act_cat,
                }

            laya_q["trajectory_resolved"] = {
                "type": "noul",
                "instructions": "Conditioned on the current agent state and the executed model, predict whether this trajectory resolves the task.",
                "criteria": resolved_criteria,
            }
            laya_exp["trajectory_resolved"] = resolved_val
            kev_q["trajectory_resolved"] = {
                "type": "noul",
                "instructions": "Conditioned on the current agent state and the executed model, predict whether this trajectory resolves the task.",
                "criteria": resolved_criteria,
                "label": resolved_val,
            }

            meta = {
                "source": source_id,
                "source_id": source_id,
                "instance_id": inst_id,
                "trajectory_id": traj_id,
                "trajectory_steps": traj_len[traj_id],
                "sample_weight": weight,
                "supervision_type": "observed_agent_action_and_outcome_auxiliary",
                "split": sp,
            }
            _dump(laya_h[sp], {"provenance": p, "state": state_obj, "questions": laya_q, "expected": laya_exp, "_meta": meta})
            _dump(kev_h[sp], {"provenance": p, "state": state_obj, "questions": kev_q, "_meta": meta})
            stats[f"adapted_{source_id}_{sp}"] += 1
            stats[f"adapted_{sp}"] += 1
            stats["adapted_total"] += 1

    for h in (*laya_h.values(), *kev_h.values()):
        h.close()
    stats["deduplicated_intra_trajectory_steps"] = stats["raw_rows_total"] - stats["adapted_total"]
    return stats

def _build_stage3_adapters(cleaned_root, out_dir):
    """Build Stage 3 Effort pairs (1,365 total pairs -> 290 decisive non-tied pairs in training/laya and training/kev)."""
    general_dir = _stage_dir(out_dir, "stage3_effort")
    laya_dir = _stage_dir(out_dir, "laya", "stage3_effort")
    kev_dir = _stage_dir(out_dir, "kev", "stage3_effort")
    splits = ("train", "val", "test")

    rows = defaultdict(list)
    path = os.path.join(cleaned_root, PUBLIC_FILES["TRA-004"])
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            rows[str(r["provenance"].get("instance_id"))].append(r)

    general_fp = os.path.join(general_dir, "agent_suite_effort_pairs.jsonl")
    gf = open(general_fp, "w", encoding="utf-8")
    laya_h = {sp: open(os.path.join(laya_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_h = {sp: open(os.path.join(kev_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    stats = Counter()

    effort_criteria = {
        "thinking-off": "Standard non-thinking mode (lower reasoning token overhead)",
        "thinking-on": "Extended thinking mode (deliberate reasoning chain enabled)",
    }

    for inst_id, rs in sorted(rows.items()):
        rs = sorted(rs, key=lambda r: (str(r["provenance"].get("model_name")), str(r["provenance"].get("reasoning_effort_mode"))))
        for a, b in zip(rs, rs[1:]):
            pa, pb = a["provenance"], b["provenance"]
            if pa.get("model_name") != pb.get("model_name") or pa.get("reasoning_effort_mode") == pb.get("reasoning_effort_mode"):
                continue
            oa, ob = a["ground_truth_outcome"], b["ground_truth_outcome"]
            pair_rec = {
                "provenance": {"source_id": "TRA-004", "instance_id": inst_id, "model_name": pa.get("model_name")},
                "state": a["pre_decision_state"],
                "low_effort": pa.get("reasoning_effort_mode"),
                "high_effort": pb.get("reasoning_effort_mode"),
                "outcomes": [oa, ob],
            }
            _dump(gf, pair_rec)
            stats["total_effort_pairs"] += 1

            sa = float(oa.get("eval_score") or 0.0)
            sb = float(ob.get("eval_score") or 0.0)
            succ_a = bool(oa.get("is_success"))
            succ_b = bool(ob.get("is_success"))
            if sa == sb and succ_a == succ_b:
                if succ_a:
                    stats["excluded_tied_both_success"] += 1
                else:
                    stats["excluded_tied_both_failed"] += 1
                continue

            raw_winner = pa.get("reasoning_effort_mode") if (sa > sb or (succ_a and not succ_b)) else pb.get("reasoning_effort_mode")
            winner_effort = "thinking-off" if (sa > sb or (succ_a and not succ_b)) else "thinking-on"
            sp = _split("TRA-004:" + inst_id)
            state_obj = dict(a["pre_decision_state"], model_name=pa.get("model_name"), source_id="TRA-004")
            meta = {
                "source": "TRA-004",
                "source_id": "TRA-004",
                "instance_id": inst_id,
                "model_name": pa.get("model_name"),
                "raw_low_effort": pa.get("reasoning_effort_mode"),
                "raw_high_effort": pb.get("reasoning_effort_mode"),
                "raw_winner_effort": raw_winner,
                "low_score": sa,
                "high_score": sb,
                "winner_effort": winner_effort,
                "supervision_type": "same_model_same_checkpoint_effort_choice",
                "split": sp,
            }
            _dump(laya_h[sp], {
                "provenance": pair_rec["provenance"],
                "state": state_obj,
                "questions": {"effort_choice": {"type": "choice", "instructions": "For the given model and multi-turn agent task, select the reasoning effort mode that achieves strictly higher task success.", "criteria": effort_criteria}},
                "expected": {"effort_choice": winner_effort},
                "_meta": meta,
            })
            _dump(kev_h[sp], {
                "provenance": pair_rec["provenance"],
                "state": state_obj,
                "questions": {"effort_choice": {"type": "choice", "instructions": "For the given model and multi-turn agent task, select the reasoning effort mode that achieves strictly higher task success.", "criteria": effort_criteria, "label": winner_effort}},
                "_meta": meta,
            })
            stats[f"decisive_{sp}"] += 1
            stats["decisive_total"] += 1
            stats[f"winner_{winner_effort}"] += 1

    gf.close()
    for h in (*laya_h.values(), *kev_h.values()):
        h.close()
    return stats

def _build_stage4_adapters(cleaned_root, out_dir):
    """Build Stage 4 Cache/Cost auxiliary views (separating historical prefix reuse, observed tokens, physical cache hits, and quota units)."""
    general_dir = _stage_dir(out_dir, "stage4_cache_cost")
    laya_dir = _stage_dir(out_dir, "laya", "stage4_auxiliary")
    kev_dir = _stage_dir(out_dir, "kev", "stage4_auxiliary")
    splits = ("train", "val", "test")
    stats = Counter()

    for source in ("CACHE-001", "TIME-001", "ROUTE-005"):
        out_fp = os.path.join(general_dir, f"{source}.jsonl")
        if not (os.path.exists(out_fp) and os.path.getsize(out_fp) > 0):
            path = os.path.join(cleaned_root, PUBLIC_FILES[source])
            with open(out_fp, "w", encoding="utf-8") as out, open(path, encoding="utf-8") as inp:
                for line in inp:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    _dump(out, {
                        "provenance": r["provenance"],
                        "state": r.get("pre_decision_state", {}),
                        "observed": r.get("observed_decision", {}),
                        "outcome": r.get("ground_truth_outcome", {}),
                        "supervision_type": "observed_or_historical",
                    })
        stats[f"raw_{source}"] = sum(1 for _ in open(out_fp, encoding="utf-8"))

    for source, rel in (
        ("OWN-001", "our-project/data/source/cch-model-cost-cache-statistics.csv"),
        ("OWN-002", "our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv"),
        ("OWN-003", "our-project/data/summaries/cch-sxyq-gpt-unified-summary.csv"),
    ):
        dst_fp = os.path.join(general_dir, f"{source}.csv")
        if not (os.path.exists(dst_fp) and os.path.getsize(dst_fp) > 0):
            src = os.path.join(os.path.dirname(os.path.dirname(cleaned_root)), rel)
            if not os.path.exists(src):
                src = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(cleaned_root))), rel)
            if os.path.exists(src):
                shutil.copyfile(src, dst_fp)
        if os.path.exists(dst_fp):
            stats[f"raw_{source}"] = sum(1 for _ in open(dst_fp, encoding="utf-8")) - 1

    laya_h = {sp: open(os.path.join(laya_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}
    kev_h = {sp: open(os.path.join(kev_dir, f"{sp}.jsonl"), "w", encoding="utf-8") for sp in splits}

    reuse_levels = [
        "0% historical prefix reuse (no block match)",
        "1% to 49% partial historical prefix reuse",
        "50% to 79% moderate historical prefix reuse",
        "80% to 100% high historical prefix reuse",
    ]
    out_tok_levels = [
        "Short output (<= 128 tokens)",
        "Medium output (129 to 512 tokens)",
        "Long output (513 to 2048 tokens)",
        "Extended output (> 2048 tokens)",
    ]
    burst_tok_levels = [
        "Brief response (<= 64 tokens)",
        "Standard response (65 to 256 tokens)",
        "Detailed response (257 to 1024 tokens)",
        "Long-form response (> 1024 tokens)",
    ]
    phys_cache_criteria = {
        "false": "No physical provider KV cache read (cache_read_tokens == 0)",
        "true": "Physical provider KV cache hit (cache_read_tokens > 0)",
    }
    quota_levels = [
        "Low gateway quota consumption (<= 2000 quota units)",
        "Moderate gateway quota consumption (2001 to 5000 quota units)",
        "High gateway quota consumption (5001 to 15000 quota units)",
        "Very high gateway quota consumption (> 15000 quota units)",
    ]

    # 1. CACHE-001 (39,632 valid records)
    with open(os.path.join(general_dir, "CACHE-001.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            p = r["provenance"]
            st = r["state"]
            obs = r["observed"]
            out = r["outcome"]
            in_len = int(st.get("input_length") or 0)
            out_len = int(out.get("output_length") or 0)
            if in_len <= 0 or out_len <= 0:
                stats["excluded_CACHE-001_invalid"] += 1
                continue
            ratio = float(obs.get("historical_prefix_hit_ratio") or 0.0)
            r_lvl = 0 if ratio <= 0.0 else (1 if ratio < 0.5 else (2 if ratio < 0.8 else 3))
            o_lvl = 0 if out_len <= 128 else (1 if out_len <= 512 else (2 if out_len <= 2048 else 3))
            req_id = f"CACHE-001:{p.get('trace_type')}:{p.get('request_index')}"
            sp = _split(req_id)
            state_str = f"Source: CACHE-001 | Trace: {st.get('trace_type')} | InputLength: {in_len} | PrefixBlocks: {st.get('prefix_block_count', 0)}"
            meta = {"source": "CACHE-001", "source_id": "CACHE-001", "request_id": req_id, "supervision_type": "historical_prefix_reuse_and_output_length", "split": sp}
            _dump(laya_h[sp], {
                "provenance": p,
                "state": state_str,
                "questions": {
                    "historical_prefix_reuse_tier": {"type": "score", "instructions": "Predict the historical prefix block reuse tier for this request.", "criteria": reuse_levels},
                    "observed_output_token_tier": {"type": "score", "instructions": "Predict the observed output token length tier for this request.", "criteria": out_tok_levels},
                },
                "expected": {"historical_prefix_reuse_tier": r_lvl, "observed_output_token_tier": o_lvl},
                "_meta": meta,
            })
            _dump(kev_h[sp], {
                "provenance": p,
                "state": state_str,
                "questions": {
                    "historical_prefix_reuse_tier": {"type": "score", "instructions": "Predict the historical prefix block reuse tier for this request.", "criteria": reuse_levels, "label": r_lvl},
                    "observed_output_token_tier": {"type": "score", "instructions": "Predict the observed output token length tier for this request.", "criteria": out_tok_levels, "label": o_lvl},
                },
                "_meta": meta,
            })
            stats[f"adapted_CACHE-001_{sp}"] += 1
            stats[f"adapted_{sp}"] += 1
            stats["adapted_total"] += 1

    # 2. TIME-001 (1,404,294 valid records)
    with open(os.path.join(general_dir, "TIME-001.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            p = r["provenance"]
            st = r["state"]
            out = r["outcome"]
            ptok = int(st.get("prompt_tokens") or 0)
            rtok = int(out.get("response_tokens") or 0)
            if ptok <= 0 or rtok <= 0:
                stats["excluded_TIME-001_invalid"] += 1
                continue
            t_lvl = 0 if rtok <= 64 else (1 if rtok <= 256 else (2 if rtok <= 1024 else 3))
            req_id = f"TIME-001:{p.get('request_index')}"
            sp = _split(req_id)
            state_str = f"Source: TIME-001 | Model: {st.get('requested_model')} | LogType: {st.get('log_type')} | PromptTokens: {ptok}"
            meta = {"source": "TIME-001", "source_id": "TIME-001", "request_id": req_id, "supervision_type": "observed_workload_response_tokens", "split": sp}
            _dump(laya_h[sp], {
                "provenance": p,
                "state": state_str,
                "questions": {"observed_response_token_tier": {"type": "score", "instructions": "Predict the observed response token tier for this workload request.", "criteria": burst_tok_levels}},
                "expected": {"observed_response_token_tier": t_lvl},
                "_meta": meta,
            })
            _dump(kev_h[sp], {
                "provenance": p,
                "state": state_str,
                "questions": {"observed_response_token_tier": {"type": "score", "instructions": "Predict the observed response token tier for this workload request.", "criteria": burst_tok_levels, "label": t_lvl}},
                "_meta": meta,
            })
            stats[f"adapted_TIME-001_{sp}"] += 1
            stats[f"adapted_{sp}"] += 1
            stats["adapted_total"] += 1

    # 3. OWN-002 (178,621 valid status=="success" & prompt_tokens>0 records; 42,507 failed/0-token excluded)
    own2_fp = os.path.join(general_dir, "OWN-002.csv")
    if os.path.exists(own2_fp):
        with open(own2_fp, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ptok = int(float(row.get("prompt_tokens") or 0))
                if row.get("status") != "success" or ptok <= 0:
                    stats["excluded_OWN-002_failed_or_zero_input"] += 1
                    continue
                cread = int(float(row.get("cache_read_tokens") or 0))
                quota = float(row.get("quota_units") or 0.0)
                phys_hit = bool(cread > 0)
                q_lvl = 0 if quota <= 2000 else (1 if quota <= 5000 else (2 if quota <= 15000 else 3))
                rid = f"OWN-002:{row.get('row_id')}"
                sp = _split(rid)
                state_str = f"Source: OWN-002 | Model: {row.get('model_normalized')} | Effort: {row.get('reasoning_effort')} | Stream: {row.get('is_stream')} | PromptTokens: {ptok}"
                prov = {"source_id": "OWN-002", "row_id": row.get("row_id"), "model": row.get("model_normalized"), "reasoning_effort": row.get("reasoning_effort")}
                meta = {"source": "OWN-002", "source_id": "OWN-002", "row_id": row.get("row_id"), "supervision_type": "observed_physical_cache_hit_and_gateway_quota_tier", "split": sp}
                _dump(laya_h[sp], {
                    "provenance": prov,
                    "state": state_str,
                    "questions": {
                        "physical_cache_hit": {"type": "noul", "instructions": "Predict whether this gateway call achieves a physical provider KV cache read hit.", "criteria": phys_cache_criteria},
                        "observed_quota_tier": {"type": "score", "instructions": "Predict the observed gateway quota consumption tier (in gateway quota_units, not USD).", "criteria": quota_levels},
                    },
                    "expected": {"physical_cache_hit": phys_hit, "observed_quota_tier": q_lvl},
                    "_meta": meta,
                })
                _dump(kev_h[sp], {
                    "provenance": prov,
                    "state": state_str,
                    "questions": {
                        "physical_cache_hit": {"type": "noul", "instructions": "Predict whether this gateway call achieves a physical provider KV cache read hit.", "criteria": phys_cache_criteria, "label": phys_hit},
                        "observed_quota_tier": {"type": "score", "instructions": "Predict the observed gateway quota consumption tier (in gateway quota_units, not USD).", "criteria": quota_levels, "label": q_lvl},
                    },
                    "_meta": meta,
                })
                stats[f"adapted_OWN-002_{sp}"] += 1
                stats[f"adapted_{sp}"] += 1
                stats["adapted_total"] += 1

    stats["excluded_OWN-001_aggregate_rows"] = stats.get("raw_OWN-001", 110)
    stats["excluded_OWN-003_aggregate_rows"] = stats.get("raw_OWN-003", 79)
    stats["excluded_ROUTE-005_analysis_only_rows"] = stats.get("raw_ROUTE-005", 6204)

    for h in (*laya_h.values(), *kev_h.values()):
        h.close()
    return stats
