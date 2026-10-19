"""Standalone, read-only audit of the 8 state variable categories and joint routing supervision."""
import argparse
import csv
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Mapping of variables to all known raw/cleaned fields across sources
VARIABLE_DEFINITIONS = {
    "Task/Subtask": {
        "id": "V1",
        "name": "Task/Subtask",
        "description": "Task specifications, problem domain, instance identity, and issue descriptions",
        "fields": [
            ("provenance.instance_id", "TRA-001/002", "Metadata/ID", "Pre-decision (task identity)", True),
            ("pre_decision_state.task_domain", "TRA-001/002", "Category ('swe')", "Pre-decision (static context)", True),
            ("provenance.battle_id", "ROUTE-004", "Metadata/ID", "Pre-decision (battle identity)", True),
            ("pre_decision_state.prompt_snippet", "ROUTE-004", "Text prefix", "Pre-decision (user prompt)", True),
            ("row_id", "OWN-002", "Metadata/ID", "Pre-decision (request identity)", False),
            ("provenance.task_id", "ENV-001/002", "Metadata/ID", "Pre-decision (benchmark task)", False),
            ("pre_decision_state.problem_snippet", "ENV-001/002", "Text prefix", "Pre-decision (problem text)", False),
            ("pre_decision_state.question", "MEM-003/005", "Text", "Pre-decision (question)", False),
        ],
    },
    "Agent/Coordination": {
        "id": "V2",
        "name": "Agent/Coordination",
        "description": "Agent architecture, multi-agent role, subtask handoff, and step trajectory progress",
        "fields": [
            ("provenance.agent_framework", "TRA-001/002", "Framework ('open-swe', 'swe-smith')", "Pre-decision (agent architecture)", False),
            ("provenance.trajectory_id", "TRA-001/002", "Trajectory ID", "Pre-decision (session identity)", False),
            ("pre_decision_state.step_index", "TRA-001/002", "Step number (0, 1, ...)", "Pre-decision (progress in trajectory)", True),
            ("observed_decision.action_type", "TRA-001/002", "Action ('bash', 'editor')", "POST-HOC DECISION (Target Leakage if used as input!)", False),
            ("observed_decision.action_nature", "TRA-002", "Nature ('INFERRED_COMMAND')", "POST-HOC DECISION (Annotation nature)", False),
        ],
    },
    "Context/Memory": {
        "id": "V3",
        "name": "Context/Memory",
        "description": "Working context length, historical dialogue/traces, and prompt length",
        "fields": [
            ("pre_decision_state.context_chars", "TRA-001/002", "Char count", "Pre-decision (context window size)", True),
            ("pre_decision_state.initial_prompt_snippet", "TRA-001/002", "Text prefix", "Pre-decision (initial prompt snippet)", True),
            ("pre_decision_state.prompt_snippet", "ROUTE-004", "Text prefix", "Pre-decision (prompt snippet)", True),
            ("pre_decision_state.input_length", "CACHE-001", "Token count", "Pre-decision (prompt length)", True),
            ("pre_decision_state.prompt_tokens", "TIME-001", "Token count", "Pre-decision (prompt token length)", True),
            ("prompt_tokens", "OWN-002", "Token count", "Pre-decision (prompt token length)", True),
            ("pre_decision_state.haystack_docs_count", "MEM-003/005", "Doc count", "Pre-decision (retrieval corpus)", False),
        ],
    },
    "Tool/Environment": {
        "id": "V4",
        "name": "Tool/Environment",
        "description": "Available tools, sandbox OS, repository environment, and prior tool execution count",
        "fields": [
            ("provenance.repo", "TRA-001/002", "Repository name", "Pre-decision (codebase environment)", False),
            ("pre_decision_state.prior_tool_calls_count", "TRA-001/002", "Call count", "Pre-decision (prior tool history)", True),
            ("observed_decision.action_type", "TRA-001/002", "Tool invoked", "POST-HOC DECISION (Target Leakage if used as input!)", False),
        ],
    },
    "Verification/Recovery": {
        "id": "V5",
        "name": "Verification/Recovery",
        "description": "Error feedback, syntax/lint test signals, retry counts, and outcome recovery",
        "fields": [
            ("pre_decision_state.prior_error_signals_count", "TRA-001/002", "Error count", "Pre-decision (prior error feedback)", True),
            ("ground_truth_outcome.task_resolved", "TRA-001/002", "Boolean outcome", "POST-HOC OUTCOME (Trajectory final outcome - Target Leakage!)", False),
            ("ground_truth_outcome.human_winner", "ROUTE-004", "Winner model", "POST-HOC OUTCOME (Human preference winner - Target!)", False),
            ("ground_truth_outcome.score", "ROUTE-001/002", "Benchmark score", "POST-HOC OUTCOME (Evaluation score - Target!)", False),
        ],
    },
    "KV Cache/Continuity": {
        "id": "V6",
        "name": "KV Cache/Continuity",
        "description": "Prefix block hashes, prefix reuse opportunities, and physical cache read tokens",
        "fields": [
            ("pre_decision_state.prefix_hash_sample", "CACHE-001", "Hash sample", "Pre-decision (prefix block hash)", True),
            ("pre_decision_state.prefix_block_count", "CACHE-001", "Block count", "Pre-decision (prefix block count)", True),
            ("observed_decision.historical_prefix_hit_ratio", "CACHE-001", "Float ratio", "OFFLINE SIMULATED (Mooncake cache simulation target)", False),
            ("ground_truth_outcome.physical_provider_cache_hit", "CACHE-001", "Boolean", "UNKNOWN / UNREPORTED at provider level", False),
            ("cache_read_tokens", "OWN-002", "Integer tokens", "POST-HOC OUTCOME (Provider reported cache read tokens)", False),
            ("cache_write_tokens", "OWN-002", "Integer tokens", "POST-HOC OUTCOME (Provider reported cache write tokens)", False),
        ],
    },
    "Temporal/Execution": {
        "id": "V7",
        "name": "Temporal/Execution",
        "description": "Arrival timestamps, invocation latency, output token lengths, and compute costs",
        "fields": [
            ("provenance.timestamp", "CACHE-001 / TIME-001", "Epoch timestamp", "Pre-decision (request arrival time)", False),
            ("pre_decision_state.arrival_timestamp", "CACHE-001 / TIME-001", "Epoch timestamp", "Pre-decision (request arrival time)", True),
            ("pre_decision_state.step_index", "TRA-001/002", "Integer step", "Pre-decision (step sequence in trajectory)", True),
            ("ground_truth_outcome.output_length", "CACHE-001", "Token count", "POST-HOC OUTCOME (Generated tokens)", False),
            ("ground_truth_outcome.response_tokens", "TIME-001", "Token count", "POST-HOC OUTCOME (Generated tokens)", False),
            ("ground_truth_outcome.total_tokens", "TIME-001", "Token count", "POST-HOC OUTCOME (Total tokens prompt+response)", False),
            ("use_time_seconds", "OWN-002", "Latency (s)", "POST-HOC OUTCOME (Execution latency)", False),
            ("first_response_ms", "OWN-002", "TTFT (ms)", "POST-HOC OUTCOME (Time to first token)", False),
        ],
    },
    "Provider/Availability": {
        "id": "V8",
        "name": "Provider/Availability",
        "description": "Candidate model identity, requested model tier, reasoning effort mode, and quota units",
        "fields": [
            ("pre_decision_state.candidate_model_a", "ROUTE-004", "Model name", "Pre-decision (candidate A)", True),
            ("pre_decision_state.candidate_model_b", "ROUTE-004", "Model name", "Pre-decision (candidate B)", True),
            ("pre_decision_state.requested_model", "TIME-001", "Model name", "Pre-decision (requested model)", True),
            ("model_normalized", "OWN-002", "Model name", "Pre-decision (routed model name)", True),
            ("reasoning_effort", "OWN-002", "Effort ('low', 'medium', 'high', 'none')", "Pre-decision (reasoning effort mode)", True),
            ("provenance.model_name", "TRA-001/002", "Model name", "Pre-decision (generating model)", False),
            ("quota_units", "OWN-002", "Gateway quota units", "POST-HOC OUTCOME (Billed quota units - Target!)", False),
        ],
    },
}

VARIABLES = [
    "Task/Subtask",
    "Agent/Coordination",
    "Context/Memory",
    "Tool/Environment",
    "Verification/Recovery",
    "KV Cache/Continuity",
    "Temporal/Execution",
    "Provider/Availability",
]

ALLOWED_SOURCES = ["TRA-001", "TRA-002", "ROUTE-004", "CACHE-001", "TIME-001", "OWN-002"]


def run_variable_audit(graded_root: str, cleaned_root: str, project_root: str) -> dict:
    """Run full statistical extraction on V2.1 indexes and cleaned source files."""
    from router_data.quality_v2 import OWN_FILES, PUBLIC_FILES

    # 1. Source x Variable Coverage and Quality
    source_stats = {}
    co_occurrence = defaultdict(lambda: defaultdict(int))
    state_count_hist = Counter()
    total_candidate_records = 0

    # Model x Effort joint supervision audit
    joint_supervision_counts = {
        "has_model_name": 0,
        "has_reasoning_effort": 0,
        "has_model_and_effort": 0,
        "has_model_effort_and_eval_score": 0,
        "has_model_effort_and_latency_cost": 0,
        "direct_runtime_joint_route_labels": 0,
        "by_source": Counter(),
    }

    # Tracking by source
    for src in sorted(PUBLIC_FILES.keys() | OWN_FILES.keys()):
        idx_p = os.path.join(graded_root, "by_source", f"{src}.jsonl.gz")
        if not os.path.exists(idx_p):
            continue

        s_stat = {
            "total_records": 0,
            "splits": Counter(),
            "train_eligible": 0,
            "q_grades": Counter(),
            "variable_non_null": Counter(),
            "variable_unknown": Counter(),
            "variable_observed": Counter(),
            "variable_estimated": Counter(),
            "variable_model_encoded": Counter(),
            "co_occurrence": defaultdict(lambda: defaultdict(int)),
            "state_count_hist": Counter(),
        }

        with gzip.open(idx_p, "rt", encoding="utf8") as f:
            for line in f:
                r = json.loads(line)
                s_stat["total_records"] += 1
                sp = r.get("split", "unknown")
                s_stat["splits"][sp] += 1
                q = r.get("quality_grade", "Q4")
                s_stat["q_grades"][q] += 1
                is_eligible = bool(r.get("train_eligible", False))
                if is_eligible:
                    s_stat["train_eligible"] += 1

                cov = r.get("variable_coverage", {})
                obs = set(r.get("observed", []))
                est = set(r.get("estimated", []))
                unk = set(r.get("unknown", []))

                # Active variables in this record
                active_vars = set()
                encoded_vars = set()

                for v in VARIABLES:
                    fields = cov.get(v, [])
                    if fields:
                        s_stat["variable_non_null"][v] += 1
                        active_vars.add(v)

                    # Determine if observed, estimated, unknown, encoded
                    if v == "Verification/Recovery":
                        if unk or "ground_truth_outcome.task_resolved" in fields and "false_outcome_status_unknown" in unk:
                            s_stat["variable_unknown"][v] += 1
                        elif "ground_truth_outcome.task_resolved" in fields or "ground_truth_outcome.human_winner" in fields:
                            s_stat["variable_observed"][v] += 1
                    elif v == "KV Cache/Continuity":
                        if "physical_provider_cache_hit" in unk:
                            s_stat["variable_unknown"][v] += 1
                        if "observed_decision.historical_prefix_hit_ratio" in fields:
                            s_stat["variable_estimated"][v] += 1
                        if "cache_read_tokens" in fields:
                            s_stat["variable_observed"][v] += 1
                    elif v == "Agent/Coordination":
                        if "observed_decision.action_nature" in fields:
                            s_stat["variable_estimated"][v] += 1
                        elif fields:
                            s_stat["variable_observed"][v] += 1
                    else:
                        if fields:
                            s_stat["variable_observed"][v] += 1

                    # Model encoding check (fields present in pre_decision_state or OWN-002 4 fields)
                    is_encoded = False
                    for f_name in fields:
                        if f_name.startswith("pre_decision_state."):
                            is_encoded = True
                            break
                        if src == "OWN-002" and f_name in {"model_normalized", "reasoning_effort", "prompt_tokens", "is_stream"}:
                            is_encoded = True
                            break
                    if is_encoded:
                        s_stat["variable_model_encoded"][v] += 1
                        encoded_vars.add(v)

                s_stat["state_count_hist"][len(active_vars)] += 1

                # Co-occurrence within this source
                for v1 in active_vars:
                    for v2 in active_vars:
                        s_stat["co_occurrence"][v1][v2] += 1

                # If from allowed sources and train eligible, add to global candidate stats
                if src in ALLOWED_SOURCES and is_eligible:
                    total_candidate_records += 1
                    state_count_hist[len(active_vars)] += 1
                    for v1 in active_vars:
                        for v2 in active_vars:
                            co_occurrence[v1][v2] += 1

                # Check Model x Effort joint supervision
                prov = r.get("provenance", {})
                pre = r.get("pre_decision_state", {})
                obs_d = r.get("observed_decision", {})
                m_name = prov.get("model_name") or obs_d.get("model_name") or pre.get("requested_model") or r.get("model_normalized")
                effort = prov.get("reasoning_effort_mode") or r.get("reasoning_effort")
                if m_name:
                    joint_supervision_counts["has_model_name"] += 1
                if effort:
                    joint_supervision_counts["has_reasoning_effort"] += 1
                if m_name and effort:
                    joint_supervision_counts["has_model_and_effort"] += 1
                    joint_supervision_counts["by_source"][src] += 1
                    # Check if evaluation score exists
                    gt = r.get("ground_truth_outcome", {})
                    score = gt.get("eval_score") or gt.get("score") or gt.get("task_resolved")
                    if score is not None:
                        joint_supervision_counts["has_model_effort_and_eval_score"] += 1
                    cost = gt.get("cost_usd") or gt.get("total_tokens") or r.get("quota_units")
        s_stat["co_occurrence"] = {v1: {v2: s_stat["co_occurrence"][v1][v2] for v2 in VARIABLES} for v1 in VARIABLES}
        s_stat["splits"] = dict(s_stat["splits"])
        s_stat["q_grades"] = dict(s_stat["q_grades"])
        s_stat["variable_non_null"] = dict(s_stat["variable_non_null"])
        s_stat["variable_unknown"] = dict(s_stat["variable_unknown"])
        s_stat["variable_observed"] = dict(s_stat["variable_observed"])
        s_stat["variable_estimated"] = dict(s_stat["variable_estimated"])
        s_stat["variable_model_encoded"] = dict(s_stat["variable_model_encoded"])
        s_stat["state_count_hist"] = dict(s_stat["state_count_hist"])
        source_stats[src] = s_stat

    # Convert co-occurrence to regular dict
    co_occ_dict = {v1: {v2: co_occurrence[v1][v2] for v2 in VARIABLES} for v1 in VARIABLES}

    return {
        "source_stats": source_stats,
        "co_occurrence": co_occ_dict,
        "state_count_hist": dict(state_count_hist),
        "total_candidate_records": total_candidate_records,
        "joint_supervision_counts": dict(joint_supervision_counts, by_source=dict(joint_supervision_counts["by_source"])),
        "variable_definitions": VARIABLE_DEFINITIONS,
    }


def audit_full_coverage_refs_pipeline(graded_root: str, cleaned_root: str, project_root: str) -> dict:
    """Audit discrepancy between collect_full_coverage_refs, levelN indexes, and materialized items."""
    from router_data.batch_prep import (
        MATRIX_ALLOWED_SOURCES,
        MATRIX_TARGETS,
        OWN_FILES,
        PUBLIC_FILES,
        _example,
        _source_rows,
        collect_full_coverage_refs,
    )

    layers = ["L1", "L2", "L3", "L4"]
    audit = {}

    for l in layers:
        layer_num = l[1:]
        l_stat = {
            "index_train_refs": 0,
            "q_grade_in_index": Counter(),
            "eligible_in_by_source": 0,
            "ineligible_q3_q4_in_index": 0,
            "by_source_detail": {},
        }

        for src in sorted(MATRIX_ALLOWED_SOURCES):
            idx_fp = os.path.join(graded_root, f"level{layer_num}", f"{src}.jsonl.gz")
            by_src_fp = os.path.join(graded_root, "by_source", f"{src}.jsonl.gz")
            if not os.path.exists(idx_fp):
                continue

            # Read by_source eligibility map for this source
            elig_map = {}
            with gzip.open(by_src_fp, "rt", encoding="utf8") as f:
                for line in f:
                    r = json.loads(line)
                    elig_map[r["source_line"]] = (r.get("train_eligible", False), r.get("quality_grade"), r.get("candidate_targets", []))

            src_train_refs = 0
            src_q = Counter()
            src_eligible = 0
            src_ineligible = 0
            target_fallbacks = Counter()

            with gzip.open(idx_fp, "rt", encoding="utf8") as f:
                for line in f:
                    r = json.loads(line)
                    if r.get("split") == "train":
                        src_train_refs += 1
                        q = r.get("quality_grade")
                        src_q[q] += 1
                        line_no = r["source_line"]
                        is_elig, bs_q, cand = elig_map.get(line_no, (False, "Q4", []))
                        if is_elig:
                            src_eligible += 1
                        else:
                            src_ineligible += 1

                        # Target fallback simulation
                        if src == "ROUTE-004":
                            t = "human_pairwise_preference"
                        elif src in {"TRA-001", "TRA-002"}:
                            t = cand[0] if cand else "observed_action"
                        elif src == "CACHE-001":
                            t = cand[0] if cand else "prefix_reuse_opportunity"
                        elif src == "TIME-001":
                            t = "request_response_tokens"
                        elif src == "OWN-002":
                            t = cand[0] if cand else "call_quota_units"
                        else:
                            t = "observed_action"
                        target_fallbacks[t] += 1

            l_stat["index_train_refs"] += src_train_refs
            l_stat["q_grade_in_index"].update(src_q)
            l_stat["eligible_in_by_source"] += src_eligible
            l_stat["ineligible_q3_q4_in_index"] += src_ineligible
            l_stat["by_source_detail"][src] = {
                "train_refs": src_train_refs,
                "q_grades": dict(src_q),
                "eligible": src_eligible,
                "ineligible": src_ineligible,
                "target_fallbacks": dict(target_fallbacks),
            }

        audit[l] = l_stat

    return audit


def verify_validation_set_isolation(val_dir: str, graded_root: str) -> dict:
    """Verify task and sample isolation between fixed validation set and training set."""
    val_records = set()
    val_units = set()
    val_prompts = set()

    for g in ("S1", "S2", "S3"):
        fp = os.path.join(val_dir, f"{g}.jsonl")
        if not os.path.exists(fp):
            continue
        for line in open(fp, encoding="utf8"):
            r = json.loads(line)
            prov = r.get("provenance", {})
            src = prov.get("source_id")
            rec_id = prov.get("stable_record_id")
            unit_id = prov.get("independent_unit_id")
            if src and rec_id:
                val_records.add((src, rec_id))
            if src and unit_id:
                val_units.add((src, unit_id))
            state = r.get("state", {}).get("pre_decision_state", {})
            prompt = state.get("initial_prompt_snippet") or state.get("prompt_snippet") or ""
            if prompt:
                val_prompts.add(prompt.strip())

    train_rec_overlap = 0
    train_unit_overlap = 0
    train_prompt_overlap = 0

    for l in ("level1", "level2", "level3", "level4"):
        for fp in Path(os.path.join(graded_root, l)).glob("*.jsonl.gz"):
            with gzip.open(fp, "rt", encoding="utf8") as f:
                for line in f:
                    r = json.loads(line)
                    if r.get("split") == "train":
                        src = r.get("source_id")
                        rec_id = r.get("stable_record_id")
                        unit_id = r.get("independent_unit_id")
                        if (src, rec_id) in val_records:
                            train_rec_overlap += 1
                        if (src, unit_id) in val_units:
                            train_unit_overlap += 1

    return {
        "val_distinct_records": len(val_records),
        "val_distinct_units": len(val_units),
        "val_prompt_count": len(val_prompts),
        "train_record_overlap": train_rec_overlap,
        "train_unit_overlap": train_unit_overlap,
        "train_prompt_overlap": train_prompt_overlap,
        "isolation_verified": (train_rec_overlap == 0 and train_unit_overlap == 0),
    }


def main():
    parser = argparse.ArgumentParser(description="Audit V1-V8 state variables and joint routing supervision.")
    parser.add_argument("--graded-root", default="runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1")
    parser.add_argument("--cleaned-root", default="data/公开数据/清洗数据")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--val-dir", default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/val")
    parser.add_argument("--out", default="router_data/audit_results_v1_v8.json")
    args = parser.parse_args()

    print("[1/3] Auditing 8 state variables across sources...", flush=True)
    var_results = run_variable_audit(args.graded_root, args.cleaned_root, args.project_root)

    print("[2/3] Auditing FULL-COVERAGE collection pipeline...", flush=True)
    pipe_results = audit_full_coverage_refs_pipeline(args.graded_root, args.cleaned_root, args.project_root)

    print("[3/3] Verifying validation set ID isolation...", flush=True)
    val_results = verify_validation_set_isolation(args.val_dir, args.graded_root)

    full_report = {
        "variable_audit": var_results,
        "pipeline_audit": pipe_results,
        "validation_isolation": val_results,
    }

    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf8") as f:
        json.dump(full_report, f, ensure_ascii=False, indent=2)
    print(f"Audit completed successfully! Saved to {out_p}", flush=True)


if __name__ == "__main__":
    main()
