#!/usr/bin/env python3
"""
ModelRouter V8 Data Extension & View Builder (Phase 3 / S1).
Generates three strictly isolated training views complying with V8 §2 & §7:
1. OBSERVED_AGENT_OUTCOME (TRA-001, TRA-002)
2. CACHE_REUSE_OPPORTUNITY (CACHE-001 Mooncake)
3. ROUTER_CHOICE (ROUTE-004 Arena human preference)
Outputs to runs/MR-V8-DATA-EXTENSION-20261018/{manifests,views,stats}
"""

import argparse
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone


def get_split(key: str, train_ratio=0.8, val_ratio=0.1) -> str:
    """Deterministic hash split by key (e.g. task_id/repo_id/battle_id)"""
    h = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    if h < train_ratio:
        return "train"
    elif h < train_ratio + val_ratio:
        return "val"
    return "test"


def build_views(cleaned_root: str, out_root: str, max_rows: int = None):
    print(f"[*] Starting V8 Data Extension View Generation...")
    print(f"[*] Cleaned Root: {cleaned_root}")
    print(f"[*] Output Root:  {out_root}")

    manifests_dir = os.path.join(out_root, "manifests")
    views_dir = os.path.join(out_root, "views")
    stats_dir = os.path.join(out_root, "stats")
    os.makedirs(manifests_dir, exist_ok=True)
    os.makedirs(views_dir, exist_ok=True)
    os.makedirs(stats_dir, exist_ok=True)

    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "views": {},
        "lineage": {}
    }

    # =========================================================================
    # 1. OBSERVED_AGENT_OUTCOME (TRA-001 & TRA-002)
    # =========================================================================
    print("\n--- [View 1] Processing OBSERVED_AGENT_OUTCOME ---")
    agent_sources = [
        ("TRA-001", os.path.join(cleaned_root, "Agent轨迹", "TRA-001_Open-SWE-Traces", "cleaned_trajectories.jsonl"), "CC-BY-4.0"),
        ("TRA-002", os.path.join(cleaned_root, "Agent轨迹", "TRA-002_SWE-smith", "cleaned_trajectories.jsonl"), "MIT"),
    ]

    view1_writers = {
        "train": gzip.open(os.path.join(views_dir, "observed_agent_outcome_train.jsonl.gz"), "wt", encoding="utf-8"),
        "val": gzip.open(os.path.join(views_dir, "observed_agent_outcome_val.jsonl.gz"), "wt", encoding="utf-8"),
        "test": gzip.open(os.path.join(views_dir, "observed_agent_outcome_test.jsonl.gz"), "wt", encoding="utf-8"),
    }
    view1_samples = []

    v1_counts = Counter()
    v1_splits = Counter()
    v1_outcomes = Counter()

    for src_id, file_path, license_name in agent_sources:
        if not os.path.exists(file_path):
            print(f"[-] Warning: {file_path} not found, skipping {src_id}")
            continue

        print(f"[*] Reading {src_id} from {file_path}...")
        line_count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                line_count += 1
                if max_rows and line_count > max_rows:
                    break
                row = json.loads(line)
                prov = row.get("provenance", {})
                pre = row.get("pre_decision_state", {})
                obs = row.get("observed_decision", {})
                gt = row.get("ground_truth_outcome", {})

                task_id = prov.get("instance_id") or prov.get("task_id") or "unknown_task"
                repo_id = prov.get("repo") or "unknown_repo"
                episode_id = prov.get("trajectory_id") or prov.get("traj_id") or "unknown_ep"
                step_id = prov.get("step_index") or pre.get("step_index") or 0
                observed_model = prov.get("model_name") or obs.get("observed_model") or "unknown_model"
                observed_effort = prov.get("effort") or "unknown_effort"

                # Terminal outcome check
                resolved = gt.get("resolved")
                if resolved is None:
                    resolved = obs.get("terminal_outcome")

                # Classification: resolved == -1 is unknown/unverified
                if resolved == -1 or resolved is None:
                    terminal_status = "UNKNOWN"
                elif resolved in (1, True, "1", "true"):
                    terminal_status = "SUCCESS"
                else:
                    terminal_status = "FAILURE"

                # Split strictly by instance_id / task_id
                split = get_split(f"{repo_id}_{task_id}")

                record = {
                    "view_type": "OBSERVED_AGENT_OUTCOME",
                    "task_id": task_id,
                    "repo_id": repo_id,
                    "episode_id": episode_id,
                    "step_id": step_id,
                    "split": split,
                    "state_before": {
                        "prompt_snippet": pre.get("initial_prompt_snippet", "")[:300],
                        "prior_tool_calls_count": pre.get("prior_tool_calls_count", 0),
                        "prior_error_signals_count": pre.get("prior_error_signals_count", 0),
                        "context_chars": pre.get("context_chars", 0),
                    },
                    "observed_model": observed_model,
                    "observed_effort": observed_effort,
                    "known_terminal_outcome": terminal_status,
                    "provenance": {
                        "source_id": src_id,
                        "license": license_name,
                        "framework": prov.get("agent_framework", "unknown"),
                    }
                }

                view1_writers[split].write(json.dumps(record, ensure_ascii=False) + "\n")
                v1_counts[src_id] += 1
                v1_splits[split] += 1
                v1_outcomes[terminal_status] += 1

                if len(view1_samples) < 35:
                    view1_samples.append(record)

        print(f"[+] {src_id} parsed {v1_counts[src_id]} records.")

    for w in view1_writers.values():
        w.close()

    with open(os.path.join(views_dir, "sample_observed_agent_outcome.jsonl"), "w", encoding="utf-8") as f:
        for s in view1_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    stats["views"]["OBSERVED_AGENT_OUTCOME"] = {
        "total_records": sum(v1_counts.values()),
        "by_source": dict(v1_counts),
        "by_split": dict(v1_splits),
        "by_outcome": dict(v1_outcomes)
    }

    # =========================================================================
    # 2. CACHE_REUSE_OPPORTUNITY (CACHE-001 Mooncake)
    # =========================================================================
    print("\n--- [View 2] Processing CACHE_REUSE_OPPORTUNITY ---")
    cache_file = os.path.join(cleaned_root, "缓存与时间", "CACHE-001_Mooncake", "cleaned_mooncake_traces.jsonl")
    v2_counts = 0
    v2_splits = Counter()
    view2_samples = []

    if os.path.exists(cache_file):
        view2_writers = {
            "train": gzip.open(os.path.join(views_dir, "cache_reuse_opportunity_train.jsonl.gz"), "wt", encoding="utf-8"),
            "val": gzip.open(os.path.join(views_dir, "cache_reuse_opportunity_val.jsonl.gz"), "wt", encoding="utf-8"),
            "test": gzip.open(os.path.join(views_dir, "cache_reuse_opportunity_test.jsonl.gz"), "wt", encoding="utf-8"),
        }

        with open(cache_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                v2_counts += 1
                if max_rows and v2_counts > max_rows:
                    break
                row = json.loads(line)
                prov = row.get("provenance", {})
                pre = row.get("pre_decision_state", {})
                obs = row.get("observed_decision", {})

                req_idx = prov.get("request_index", v2_counts)
                trace_type = prov.get("trace_type", "conversation")
                split = get_split(f"mooncake_{trace_type}_{req_idx}")

                record = {
                    "view_type": "CACHE_REUSE_OPPORTUNITY",
                    "evidence_label": "OBSERVED_REUSE",
                    "timestamp": prov.get("timestamp", 0),
                    "input_length": pre.get("input_length", 0),
                    "output_length": pre.get("output_token_length", 0),
                    "prefix_block_count": pre.get("prefix_block_count", 0),
                    "prefix_hash_sample": pre.get("prefix_hash_sample", []),
                    "estimated_reusable_blocks": obs.get("historical_prefix_hit_blocks", 0),
                    "cache_policy_assumption": "LRU_512_CHUNK_PREFIX",
                    "provenance": {
                        "source_id": "CACHE-001",
                        "trace_type": trace_type,
                        "license": "Research Use",
                    }
                }

                view2_writers[split].write(json.dumps(record, ensure_ascii=False) + "\n")
                v2_splits[split] += 1

                if len(view2_samples) < 35:
                    view2_samples.append(record)

        for w in view2_writers.values():
            w.close()

        with open(os.path.join(views_dir, "sample_cache_reuse_opportunity.jsonl"), "w", encoding="utf-8") as f:
            for s in view2_samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    stats["views"]["CACHE_REUSE_OPPORTUNITY"] = {
        "total_records": v2_counts,
        "by_split": dict(v2_splits)
    }

    # =========================================================================
    # 3. ROUTER_CHOICE (ROUTE-004 Arena Human Preference)
    # =========================================================================
    print("\n--- [View 3] Processing ROUTER_CHOICE ---")
    arena_file = os.path.join(cleaned_root, "路由比较", "ROUTE-004_Arena", "cleaned_arena_preference.jsonl")
    v3_counts = 0
    v3_splits = Counter()
    view3_samples = []

    if os.path.exists(arena_file):
        view3_writers = {
            "train": gzip.open(os.path.join(views_dir, "router_choice_train.jsonl.gz"), "wt", encoding="utf-8"),
            "val": gzip.open(os.path.join(views_dir, "router_choice_val.jsonl.gz"), "wt", encoding="utf-8"),
            "test": gzip.open(os.path.join(views_dir, "router_choice_test.jsonl.gz"), "wt", encoding="utf-8"),
        }

        with open(arena_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                v3_counts += 1
                if max_rows and v3_counts > max_rows:
                    break
                row = json.loads(line)
                prov = row.get("provenance", {})
                pre = row.get("pre_decision_state", {})
                obs = row.get("observed_decision", {})

                battle_id = prov.get("battle_id", str(v3_counts))
                split = get_split(f"arena_battle_{battle_id}")

                record = {
                    "view_type": "ROUTER_CHOICE",
                    "battle_id": battle_id,
                    "prompt_snippet": pre.get("prompt_snippet", "")[:300],
                    "candidate_models": [pre.get("candidate_model_a"), pre.get("candidate_model_b")],
                    "winner_choice": obs.get("winner_choice"),
                    "winner_model": obs.get("winner_model"),
                    "label_nature": "HUMAN_PAIRWISE_PREFERENCE",
                    "provenance": {
                        "source_id": "ROUTE-004",
                        "license": "LMSYS Terms of Use",
                    }
                }

                view3_writers[split].write(json.dumps(record, ensure_ascii=False) + "\n")
                v3_splits[split] += 1

                if len(view3_samples) < 35:
                    view3_samples.append(record)

        for w in view3_writers.values():
            w.close()

        with open(os.path.join(views_dir, "sample_router_choice.jsonl"), "w", encoding="utf-8") as f:
            for s in view3_samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    stats["views"]["ROUTER_CHOICE"] = {
        "total_records": v3_counts,
        "by_split": dict(v3_splits)
    }

    # =========================================================================
    # Write Manifests & Statistics
    # =========================================================================
    manifest_data = {
        "manifest_version": "V8-20261018",
        "description": "Lineage manifest for ModelRouter V8 data extension views",
        "sources": {
            "TRA-001": {"name": "Open-SWE-Traces", "license": "CC-BY-4.0", "target_view": "OBSERVED_AGENT_OUTCOME"},
            "TRA-002": {"name": "SWE-smith-trajectories", "license": "MIT", "target_view": "OBSERVED_AGENT_OUTCOME"},
            "CACHE-001": {"name": "Mooncake-FAST25", "license": "Research Use", "target_view": "CACHE_REUSE_OPPORTUNITY"},
            "ROUTE-004": {"name": "Arena-55k", "license": "LMSYS Terms of Use", "target_view": "ROUTER_CHOICE"},
        },
        "output_files": {
            "OBSERVED_AGENT_OUTCOME": [
                "views/observed_agent_outcome_train.jsonl.gz",
                "views/observed_agent_outcome_val.jsonl.gz",
                "views/observed_agent_outcome_test.jsonl.gz",
            ],
            "CACHE_REUSE_OPPORTUNITY": [
                "views/cache_reuse_opportunity_train.jsonl.gz",
                "views/cache_reuse_opportunity_val.jsonl.gz",
                "views/cache_reuse_opportunity_test.jsonl.gz",
            ],
            "ROUTER_CHOICE": [
                "views/router_choice_train.jsonl.gz",
                "views/router_choice_val.jsonl.gz",
                "views/router_choice_test.jsonl.gz",
            ]
        }
    }

    with open(os.path.join(manifests_dir, "data_lineage_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    with open(os.path.join(stats_dir, "v8_dataset_statistics.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n[+] V8 Data Extension completed successfully.")
    print(f"[+] Manifest: {manifests_dir}/data_lineage_manifest.json")
    print(f"[+] Stats:    {stats_dir}/v8_dataset_statistics.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build V8 Data Extension Views")
    parser.add_argument("--cleaned-root", default="data/公开数据/清洗数据")
    parser.add_argument("--out-root", default="runs/MR-V8-DATA-EXTENSION-20261018")
    parser.add_argument("--max-rows", type=int, default=None, help="Limit rows for fast validation")
    args = parser.parse_args()

    build_views(args.cleaned_root, args.out_root, args.max_rows)
