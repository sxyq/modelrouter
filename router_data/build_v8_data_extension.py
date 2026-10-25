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
import random
import sys
from collections import Counter, defaultdict
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path


def _kev_source_targets():
    from router_data.batch_prep import MATRIX_TARGETS

    return {
        "ROUTE-004": MATRIX_TARGETS["S1"],
        "TRA-001": MATRIX_TARGETS["S2"], "TRA-002": MATRIX_TARGETS["S2"],
        "CACHE-001": ["prefix_reuse_opportunity", "output_token_length"],
        "TIME-001": ["request_response_tokens"],
        "OWN-002": ["call_quota_units", "cache_read_tokens", "call_output_tokens"],
    }


def _kev_labeled_question(question, label, target):
    from router_data.batch_prep import _neutral_instruction

    typ, criteria = question["type"], question["criteria"]
    valid = ((typ == "choice" and label in criteria)
             or (typ == "noul" and type(label) is bool)
             or (typ == "score" and type(label) is int and 0 <= label < len(criteria)))
    if valid:
        return {**question, "label": label, "instructions": _neutral_instruction(target)}
    return None


def export_kev_auxiliary(typed_data_root, project_root=".", configuration_source=None):
    """Reuse saved S2/S3 views and their labels; do not copy the C03 S1 material."""
    from router_data.batch_prep import MATRIX_TARGETS

    root = Path(project_root)
    source_root = root / typed_data_root
    source_targets = _kev_source_targets()
    destination = root / "data/kev/v8_extension"
    stats = {"configuration_source": configuration_source, "typed_data_root": str(source_root),
             "test_used": False, "splits": {}, "input_files": {}, "data_paths": {},
             "training_scope": "Existing observed S2/S3 auxiliary labels only; no S1 re-export",
             "model_choice_labels_created": 0}
    for split in ("train", "val"):
        counts, target_counts, labels, seen = Counter(), Counter(), Counter(), set()
        units = defaultdict(set)
        output_path = destination / (split + "_typed_auxiliary.jsonl")
        output = None
        with ExitStack() as stack:
            for group in ("S2", "S3"):
                path = source_root / split / (group + ".jsonl")
                if not path.is_file():
                    counts["missing_input_files"] += 1
                    continue
                input_counts = Counter()
                stats["input_files"][str(path)] = {"bytes": path.stat().st_size, "counts": input_counts}
                with path.open(encoding="utf-8") as source:
                    for line in source:
                        row = json.loads(line)
                        input_counts["records"] += 1
                        provenance, meta = row["provenance"], row["_meta"]
                        target, source_id = meta["target"], provenance["source_id"]
                        if (provenance["split"] != split or target not in MATRIX_TARGETS[group]
                                or target not in source_targets.get(source_id, ())):
                            counts["excluded_split_or_target"] += 1
                            continue
                        questions = {}
                        for qid, question in row["questions"].items():
                            label = question["label"] if "label" in question else row["expected"][qid]
                            converted = _kev_labeled_question(question, label, target)
                            if converted is None:
                                counts["excluded_unknown_or_invalid_label"] += 1
                                continue
                            key = (source_id, provenance["source_file"], provenance["source_line"], qid)
                            if key in seen:
                                counts["excluded_repeated_supervision"] += 1
                                continue
                            seen.add(key)
                            units[group].add((source_id, provenance["independent_unit_id"]))
                            questions[qid] = converted
                            counts["questions_" + group] += 1
                            counts["qid_" + qid] += 1
                            target_key = "|".join((source_id, target, qid, question["type"]))
                            target_counts[target_key] += 1
                            labels[target_key + "|" + json.dumps(label)] += 1
                        if not questions:
                            continue
                        if output is None:
                            destination.mkdir(parents=True, exist_ok=True)
                            output = stack.enter_context(output_path.open("w", encoding="utf-8"))
                            stats["data_paths"][split] = str(output_path)
                        output.write(json.dumps({**row, "questions": questions}, ensure_ascii=False) + "\n")
                        input_counts["written_records"] += 1
                        counts["written_records"] += 1
        stats["splits"][split] = {**dict(counts), "question_target_counts": dict(target_counts),
                                 "label_counts": dict(labels),
                                 "independent_units_by_class": {group: len(values) for group, values in units.items()}}
    stats["new_train_questions_vs_c03"] = sum(
        stats["splits"]["train"].get("questions_" + group, 0) for group in ("S2", "S3"))
    stats["configuration_status"] = "TYPED_AUXILIARY_READY" if stats["new_train_questions_vs_c03"] else "PENDING_NO_NEW_TYPED_LABELS"
    if stats["data_paths"]:
        (destination / "materialization_typed_auxiliary.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(stats, ensure_ascii=False))
    return stats


def _kev_coverage_rows(source_root, split, group, counts):
    """Stream the saved typed rows using the same source, split and label rules."""
    from router_data.batch_prep import MATRIX_TARGETS

    path = source_root / split / (group + ".jsonl")
    if not path.is_file():
        counts["missing_input_files"] += 1
        return
    seen, allowed = set(), _kev_source_targets()
    with path.open(encoding="utf-8") as source:
        for line_no, line in enumerate(source, 1):
            row = json.loads(line)
            counts["input_records"] += 1
            provenance, meta = row["provenance"], row["_meta"]
            target, source_id = meta["target"], provenance["source_id"]
            if (provenance["split"] != split or meta["supervision_class"] != group
                    or target not in MATRIX_TARGETS[group] or target not in allowed.get(source_id, ())):
                counts["excluded_split_or_source_target"] += 1
                continue
            questions = {}
            for qid, question in row["questions"].items():
                label = question["label"] if "label" in question else row["expected"][qid]
                converted = _kev_labeled_question(question, label, target)
                if converted is None:
                    counts["excluded_unknown_or_invalid_label"] += 1
                    continue
                key = (source_id, provenance["source_file"], provenance["source_line"], qid)
                if key in seen:
                    counts["excluded_repeated_supervision"] += 1
                    continue
                seen.add(key)
                questions[qid] = converted
            if questions:
                counts["legal_records"] += 1
                yield line_no, {**row, "questions": questions}


def export_kev_coverage(typed_data_root, project_root=".", seed=42, configuration_source=None):
    """Materialize R01-R16 ratios only; the existing dispatcher owns training."""
    from router_data.batch_prep import FULL_COMBOS

    root = Path(project_root).resolve()
    source_root = (root / typed_data_root).resolve()
    destination = root / "data/kev/v8_extension"
    manifest_path = destination / "materialization_coverage.json"
    groups, splits = ("S1", "S2", "S3"), ("train", "val")
    ratios = {"R" + key[1:]: dict(zip(names, weights)) for key, (names, weights) in FULL_COMBOS.items()}
    inputs = {}
    for split in splits:
        for group in groups:
            path = source_root / split / (group + ".jsonl")
            inputs[f"{split}/{group}"] = {"path": str(path), "exists": path.is_file()}
            if path.is_file():
                info = path.stat()
                inputs[f"{split}/{group}"].update(bytes=info.st_size, mtime_ns=info.st_mtime_ns)
    configuration = {"configuration_source": configuration_source, "typed_data_root": str(source_root),
                     "seed": seed, "ratios": ratios, "source_targets": _kev_source_targets(),
                     "selection": "MAX_INTEGER_RATIO_WITHOUT_REPLACEMENT_PER_SPLIT", "input_files": inputs}
    if manifest_path.is_file():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing["configuration"] != configuration:
            result = {"status": "PENDING", "reason": "Existing coverage has different configuration or inputs; historical material unchanged",
                      "materialization_path": str(manifest_path)}
        else:
            missing = [path for run in existing["runs"].values() for path in run["dataPaths"].values() if not Path(path).is_file()]
            result = existing if not missing else {"status": "PENDING", "reason": "Recorded coverage material is missing; historical record unchanged", "missing_paths": missing}
        print(json.dumps(result, ensure_ascii=False))
        return result

    result = {"configuration": configuration, "test_used": False, "pools": {}, "runs": {},
              "materialization_path": str(manifest_path),
              "ratio_unit": "original typed record; no replacement within each run and class",
              "validation_scope": "material split only; dispatcher retains its original fixed Kev Val"}
    orders = {}
    for split in splits:
        result["pools"][split] = {}
        for group in groups:
            counts, units, sources, targets = Counter(), set(), Counter(), Counter()
            order = []
            for line_no, row in _kev_coverage_rows(source_root, split, group, counts):
                order.append(line_no)
                prov = row["provenance"]
                units.add((prov["source_id"], prov["independent_unit_id"]))
                sources[prov["source_id"]] += 1
                targets[prov["source_id"] + "|" + row["_meta"]["target"]] += 1
            random.Random(seed).shuffle(order)
            orders[split, group] = order
            result["pools"][split][group] = {**dict(counts), "independent_units": len(units),
                                           "source_counts": dict(sources), "target_counts": dict(targets)}

    wanted, summaries = defaultdict(lambda: defaultdict(list)), {}
    for run_id, ratio in ratios.items():
        run = {"run_id": run_id, "ratio": ratio, "seed": seed, "status": "READY", "splits": {}, "dataPaths": {}}
        result["runs"][run_id] = run
        absent = [group for group, weight in ratio.items() if len(orders["train", group]) < weight]
        if absent:
            run.update(status="PENDING", reason="Not enough legal training targets for a complete ratio: " + ",".join(absent))
            continue
        paths = {split: destination / run_id / (split + ".jsonl") for split in splits}
        if any(path.exists() for path in paths.values()):
            run.update(status="PENDING", reason="Existing run material has no matching coverage record; unchanged")
            continue
        for split in splits:
            multiplier = min(len(orders[split, group]) // weight for group, weight in ratio.items())
            summary = {"ratio_multiplier": multiplier, "records_by_class": {group: 0 for group in ratio},
                       "questions_by_class": Counter(), "source_counts": Counter(), "target_counts": Counter(),
                       "question_target_counts": Counter(), "units": defaultdict(set)}
            summaries[run_id, split] = summary
            if not multiplier:
                run["splits"][split] = {"status": "PENDING", "reason": "No complete legal ratio in this split", "ratio_multiplier": 0, "records_by_class": summary["records_by_class"]}
                continue
            run["dataPaths"][split] = str(paths[split])
            for group, weight in ratio.items():
                for line_no in orders[split, group][:multiplier * weight]:
                    wanted[split, group][line_no].append(run_id)

    with ExitStack() as stack:
        handles = {}
        for split in splits:
            for group in groups:
                if not wanted[split, group]:
                    continue
                for line_no, row in _kev_coverage_rows(source_root, split, group, Counter()):
                    recipients = wanted[split, group].get(line_no, ())
                    if not recipients:
                        continue
                    text = json.dumps(row, ensure_ascii=False) + "\n"
                    prov, target = row["provenance"], row["_meta"]["target"]
                    for run_id in recipients:
                        key = run_id, split
                        if key not in handles:
                            path = Path(result["runs"][run_id]["dataPaths"][split])
                            path.parent.mkdir(parents=True, exist_ok=True)
                            handles[key] = stack.enter_context(path.open("x", encoding="utf-8"))
                        handles[key].write(text)
                        summary = summaries[key]
                        summary["records_by_class"][group] += 1
                        summary["questions_by_class"][group] += len(row["questions"])
                        summary["source_counts"][prov["source_id"]] += 1
                        summary["target_counts"][prov["source_id"] + "|" + target] += 1
                        summary["units"][group].add((prov["source_id"], prov["independent_unit_id"]))
                        for qid, question in row["questions"].items():
                            summary["question_target_counts"]["|".join((prov["source_id"], target, qid, question["type"]))] += 1
    for (run_id, split), summary in summaries.items():
        if not summary["ratio_multiplier"]:
            continue
        units = summary.pop("units")
        summary["independent_units_by_class"] = {group: len(values) for group, values in units.items()}
        summary["total_records"] = sum(summary["records_by_class"].values())
        result["runs"][run_id]["splits"][split] = summary
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return result


def export_kev_training(config_path, project_root=".", typed_data_root=None):
    """Use observed Arena labels within the existing project train/Val split."""
    if typed_data_root is not None:
        return export_kev_auxiliary(typed_data_root, project_root, str(config_path))
    root = Path(project_root)
    config = json.loads((root / config_path).read_text())
    split_ids = {}
    for split in ("train", "val"):
        records = {}
        with (root / f"data/kev/公开数据/{split}.jsonl").open(encoding="utf-8") as source:
            for line in source:
                row = json.loads(line)
                provenance = row.get("provenance") or {}
                if provenance.get("source_id") == "ROUTE-004":
                    records[str(provenance["battle_id"])] = row
        split_ids[split] = records
    destination = root / "data/kev/v8_extension"
    destination.mkdir(parents=True, exist_ok=True)
    stats = {"configuration_source": config_path, "test_used": False,
             "label_nature": "HUMAN_PAIRWISE_PREFERENCE", "splits": {},
             "unsupported_views": {
                 "cache_reuse_opportunity": "continuous opportunity target; no existing typed label mapping in this formal configuration",
                 "observed_agent_outcome": "only the observed model outcome is available; no pairwise model-choice label"}}
    for split, field in (("train", "data_views"), ("val", "validation_views")):
        counts = Counter()
        tmp = destination / (split + ".jsonl.tmp")
        with gzip.open(root / config[field]["router_choice"], "rt", encoding="utf-8") as source, tmp.open("w", encoding="utf-8") as output:
            for line in source:
                view = json.loads(line)
                counts["source_records"] += 1
                identity = str(view["battle_id"])
                if identity not in split_ids[split]:
                    counts["excluded_project_split_mismatch"] += 1
                    continue
                models = view["candidate_models"]
                if view.get("winner_choice") not in ("model_a", "model_b"):
                    counts["excluded_tie_or_missing_label"] += 1
                    continue
                winner = models[0 if view["winner_choice"] == "model_a" else 1]
                if winner != view.get("winner_model") or not all(models) or len(set(models)) != 2:
                    counts["excluded_inconsistent_candidates"] += 1
                    continue
                record = split_ids[split][identity]
                # Preserve the original typed record, task content, labels and split.
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                counts["written_records"] += 1
        tmp.replace(destination / (split + ".jsonl"))
        stats["splits"][split] = dict(counts)
    stats["training_scope"] = "Arena router_choice only; cache/outcome views remain unsupported, not trained"
    stats["new_train_records_vs_c03"] = 0
    stats["configuration_status"] = "PARTIAL_MATERIAL_NOT_FULL_C09"
    (destination / "materialization.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(stats, ensure_ascii=False))
    return stats


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
    parser.add_argument("--export-kev", action="store_true")
    parser.add_argument("--kev-coverage", action="store_true", help="Export the existing 16 S1/S2/S3 ratios without training")
    parser.add_argument("--typed-data-root", help="Saved train/val S1/S2/S3 views with original labels and provenance")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--config", default="our-project/data/configs/training/KEV-V8-EXT-01.json")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    if args.kev_coverage:
        if args.typed_data_root is None:
            parser.error("--kev-coverage requires --typed-data-root")
        export_kev_coverage(args.typed_data_root, args.project_root, args.seed, args.config)
    elif args.export_kev:
        export_kev_training(args.config, args.project_root, args.typed_data_root)
    else:
        build_views(args.cleaned_root, args.out_root, args.max_rows)
