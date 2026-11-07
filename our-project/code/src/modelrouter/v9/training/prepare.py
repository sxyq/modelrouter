"""Prepare existing typed supervision and two extractive public trajectory references."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import sys
from collections import Counter
from itertools import islice, zip_longest
from pathlib import Path

# Load the existing pure data module without importing unrelated training audits.
_quality_name = "modelrouter.data_pipeline.quality.quality_v2"
if _quality_name not in sys.modules:
    _quality_path = Path(__file__).resolve().parents[2] / "data_pipeline/quality/quality_v2.py"
    _quality_spec = importlib.util.spec_from_file_location(_quality_name, _quality_path)
    _quality_module = importlib.util.module_from_spec(_quality_spec)
    sys.modules[_quality_name] = _quality_module
    _quality_spec.loader.exec_module(_quality_module)

from modelrouter.data_pipeline.v8_extension_loader import V8ExtensionDataset
from modelrouter.datasets.public_sources import PublicDatasetLoader
from modelrouter.serving.schemas import PreDecisionState
from modelrouter.training.supervision_loaders import MultiViewSupervisionLoader
from modelrouter.v9.capabilities.features import (
    DEFAULT_DATA_DIR, candidate_action, load_current,
)
from modelrouter.providers.registry import V9_MODEL_IDS
from .constants import DATA_ROOT, GROUPS, PUBLIC_TRAJECTORIES
from .material_io import iter_rows, reencode_prepared
from .prefix_replay import build_offline_prefix_input, router_input_text as _router_input_text
from .real_supervision import (
    ACTION_POOL, ACTION_POOL_ID, ACTION_POOL_IDS, prepare_action_pool_comparison,
    prepare_candidate_outcomes, prepare_candidate_view, prepare_comparison,
)
from .supervision import (
    NEW_FEATURE_FIELDS, SOURCE_PRE_FIELDS, TEACHER_FIELDS, TEACHER_METADATA,
    candidate_inputs, decision_state, offline_teacher_state, prepare_action_pool_record, prepare_record,
)
from .teacher_material import generate_offline_teacher_material
from modelrouter.v9.training.trajectory_material import (
    action_excerpt, reference_candidate, text_content, tool_result, trajectory, trajectory_prefixes,
)


def v8_records(views_dir, split, dataset_revision=None, skipped=None):
    """Reuse the V8 loader, retaining the original record's identity and evidence."""
    dataset = V8ExtensionDataset(Path(views_dir), split)
    methods = {"S1": ("router_choice", dataset.iter_router_choice),
               "S2": ("observed_agent_outcome", dataset.iter_agent_outcome),
               "S3": ("cache_reuse_opportunity", dataset.iter_cache_reuse)}
    for group, (name, method) in methods.items():
        path = Path(views_dir) / f"{name}_{split}.jsonl.gz"
        if not path.is_file():
            continue
        for (line_number, original), loaded in zip(iter_rows(path), method()):
            provenance = {**original.get("provenance", {}), "split": original.get("split", split),
                          "task_id": original.get("task_id"), "source_file": str(path),
                          "source_line": line_number,
                          "episode_id": original.get("episode_id"),
                          "trajectory_id": original.get("episode_id"),
                          "dataset_revision": original.get("provenance", {}).get("dataset_revision") or dataset_revision}
            provenance.setdefault("stable_record_id", original.get("battle_id") or
                                  f"{provenance.get('source_id')}:{path.name}:{line_number}")
            pre = original.get("state_before", {})
            if group == "S1":
                pre = {"prompt": loaded["prompt"]}
                criteria = dict.fromkeys(loaded["candidates"], "")
                questions = {"model_choice": {"type": "choice", "criteria": criteria}}
                expected = {"model_choice": loaded["winner"]}
                target = "human_pairwise_preference"
            elif group == "S2":
                outcome = loaded["outcome"]
                if outcome not in ("SUCCESS", "FAILURE"):
                    if skipped is not None:
                        skipped["UNKNOWN_OUTCOME"] += 1
                    continue
                pre = {**pre, "step_index": original.get("step_id")}
                questions = {"trajectory_resolved": {"type": "noul", "criteria": {"false": "Unresolved", "true": "Resolved"}}}
                expected = {"trajectory_resolved": outcome == "SUCCESS"}
                target = "observed_success" if outcome == "SUCCESS" else "observed_failure"
            else:
                provenance.setdefault("source_id", "CACHE-001")
                pre = {name: original.get(name) for name in
                       ("input_length", "prefix_block_count", "prefix_hash_sample")}
                pre.update(arrival_timestamp=original.get("timestamp"),
                           trace_type=provenance.get("trace_type"))
                if original.get("estimated_reusable_blocks") is None or original.get("prefix_block_count") is None:
                    if skipped is not None:
                        skipped["MISSING_TARGET"] += 1
                    continue
                ratio = loaded["reusable_ratio"]
                questions = {"historical_prefix_reuse_tier": {"type": "score", "criteria": ["none", "under 50%", "under 80%", "80% or more"]}}
                expected = {"historical_prefix_reuse_tier": 0 if ratio <= 0 else 1 if ratio < .5 else 2 if ratio < .8 else 3}
                target = "prefix_reuse_opportunity"
            yield {"provenance": provenance, "state": pre, "questions": questions,
                   "expected": expected, "_meta": {"supervision_class": group,
                   "target": target, "input_kind": "V8_VIEW", "source_view": original.get("view_type"),
                   "label_evidence": original.get("label_nature", original.get("evidence_label"))}}

def prepare(typed_root=None, *, inputs=(), v8_views=None, preview_root=None, trajectories=(),
            out_dir=DATA_ROOT / "prepared", references_path=DATA_ROOT / "references" / "two_references.json",
            splits=("train", "val"), limit_per_view=64, max_episodes=1000, dataset_revision=None,
            capabilities_dir=DEFAULT_DATA_DIR, candidates=()):
    out_dir, references_path = Path(out_dir), Path(references_path)
    counts, eligible, skipped, saved_sources = Counter(), Counter(), Counter(), Counter()
    missing, pools, anchors, seen, references = [], {}, {}, set(), {}
    snapshot = load_current(capabilities_dir)
    candidates = [candidate_action(action) for action in candidates]
    teacher_statuses, teacher_models, target_scopes, prefix_counts = Counter(), Counter(), Counter(), Counter()
    supervision_types = Counter()
    comparison_axes = Counter()
    comparison_tasks = {}
    inline_trajectories, inline_counts = [], Counter()
    fixed_reference_kinds = set()
    if references_path.is_file():
        for ref in json.loads(references_path.read_text(encoding="utf8")):
            if (ref.get("reference_kind") in ("efficient_success", "failure_recovery")
                    and ref.get("source_id") in PUBLIC_TRAJECTORIES and ref.get("split") == "train"
                    and ref.get("success_evidence", {}).get("value") is True):
                references[ref["reference_kind"]] = ref
                fixed_reference_kinds.add(ref["reference_kind"])

    def save(row, split):
        prepared, reason = prepare_record(row, split, dataset_revision,
                                          capability_snapshot=snapshot, candidates=candidates)
        if prepared is None:
            skipped[reason] += 1
            return
        provenance, meta = prepared["provenance"], prepared["_meta"]
        if (split == "train" and meta["supervision_class"] == "S2"
                and meta.get("input_kind") not in ("TRAJECTORY_PREFIX", "V8_VIEW")
                and provenance["source_id"] in PUBLIC_TRAJECTORIES and provenance.get("trajectory_id")):
            anchors.setdefault((provenance["source_id"], provenance["trajectory_id"]), {
                **provenance, "typed_outcome": prepared["expected"].get("trajectory_resolved"),
            })
        group = GROUPS[meta["supervision_class"]]
        is_prefix = meta.get("input_kind") == "TRAJECTORY_PREFIX"
        identity = (split, provenance["source_id"], provenance.get("stable_record_id"),
                    provenance.get("task_id"), provenance.get("trajectory_id"),
                    provenance.get("dataset_revision"),
                    json.dumps(prepared["questions"], ensure_ascii=False), prepared["state"])
        if identity in seen:
            skipped["DUPLICATE"] += 1
            return
        seen.add(identity)
        key = f"{group}/{split}.jsonl"
        eligible[key] += 1
        bucket = pools.setdefault(key, {}).setdefault((provenance["source_id"], meta["target"], is_prefix), [])
        if not limit_per_view or len(bucket) < limit_per_view:
            bucket.append(prepared)

    for split in splits:
        if typed_root:
            for group in GROUPS:
                path = Path(typed_root) / split / f"{group}.jsonl"
                if path.is_file():
                    for _, row in iter_rows(path):
                        save(row, split)
                else:
                    missing.append(str(path))
        if v8_views:
            for row in v8_records(v8_views, split, dataset_revision, skipped):
                save(row, split)
    for path in inputs:
        if str(path) != "-" and not Path(path).is_file():
            missing.append(str(path))
            continue
        for row_number, row in iter_rows(path):
            if "trajectory_record" in row:
                inline_counts[str(path)] += 1
                if inline_counts[str(path)] <= max_episodes:
                    inline_trajectories.append((row.get("source_id"), path, row_number, row["trajectory_record"]))
                else:
                    skipped["TRAJECTORY_LIMIT_REACHED"] += 1
                continue
            split = row.get("candidate_reference", row.get("provenance", {})).get("split")
            if split in splits:
                save(row, split)
    if preview_root:
        loader = MultiViewSupervisionLoader(PublicDatasetLoader(Path(preview_root)))
        for method in (loader.get_s1_records, loader.get_s2_records, loader.get_s3_records):
            for row in method(limit=limit_per_view or None):
                split = row.get("provenance", {}).get("split")
                if not row.get("questions"):
                    skipped["UNTYPED_PREVIEW"] += 1
                elif split in splits:
                    save(row, split)
    def raw_episodes():
        yield from inline_trajectories
        for source_id, path in trajectories:
            if str(path) != "-" and not Path(path).is_file():
                missing.append(str(path))
                continue
            for row_number, row in iter_rows(path):
                if row_number > max_episodes:
                    break
                yield source_id, path, row_number, row

    for source_id, path, row_number, row in raw_episodes():
        if source_id not in PUBLIC_TRAJECTORIES:
            skipped["SOURCE_OR_TARGET_NOT_SUPPORTED"] += 1
            continue
        episode_id = row.get("trajectory_id", row.get("traj_id"))
        anchor = anchors.get((source_id, episode_id))
        if anchor is None:
            skipped["NO_TYPED_TRAIN_ANCHOR"] += 1
            continue
        episode = trajectory(row, source_id, path, row_number, anchor)
        if episode is None:
            skipped["MISSING_TRAJECTORY_MESSAGES"] += 1
            continue
        if (anchor.get("typed_outcome") is not None and episode["resolved"] is not None
                and anchor["typed_outcome"] != episode["resolved"]):
            skipped["PUBLIC_OUTCOME_CONFLICT"] += 1
            continue
        for sample in trajectory_prefixes(episode):
            save(sample, "train")
        candidate = reference_candidate(episode)
        if candidate:
            kind = candidate["reference_kind"]
            previous = references.get(kind)
            if kind not in fixed_reference_kinds and (
                    previous is None or candidate["observed_through_step"] < previous["observed_through_step"]):
                references[kind] = candidate

    for key, buckets in pools.items():
        streams = []
        for is_prefix in (False, True):
            bundles = [bucket for (_, _, prefix), bucket in buckets.items() if prefix == is_prefix]
            rows = (row for bundle in zip_longest(*bundles) for row in bundle if row is not None)
            streams.append(islice(rows, limit_per_view) if limit_per_view else rows)
        path = out_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf8") as stream:
            for row in (row for stream_rows in streams for row in stream_rows):
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                counts[key] += 1
                saved_sources[f"{key}:{row['provenance']['source_id']}:{row['_meta']['target']}"] += 1
                teacher = row["offline_teacher_state"]
                if row["_meta"].get("supervision_type"):
                    kind = row["_meta"]["supervision_type"]
                    supervision_types[kind] += 1
                    comparison_axes[row["_meta"]["comparison_axis"]] += 1
                    comparison_tasks.setdefault(kind, set()).add(
                        (row["provenance"]["source_id"], row["provenance"]["task_id"]))
                if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX":
                    prefix_counts[row["provenance"]["split"]] += 1
                teacher_statuses[teacher["status"]] += 1
                if teacher["assessment"]:
                    teacher_models[teacher["assessment"]["teacher_model_id"]] += 1
                if row["_meta"]["supervision_class"] == "S1":
                    for label in row["expected"].values():
                        action = candidate_action(label)
                        if (row["_meta"].get("action_pool_id") == ACTION_POOL_ID
                                and action["model_id"] in V9_MODEL_IDS
                                and action["action_id"] in ACTION_POOL_IDS):
                            target_scopes["v9_model_choice"] += 1
                            target_scopes["v9_model_effort_choice"] += 1
                else:
                    target_scopes["auxiliary_not_model_choice"] += 1

    trainer_views = {}
    for split in splits:
        for group in GROUPS.values():
            key = f"{group}/{split}.jsonl"
            path = out_dir / key
            if key not in counts and (path.is_file() or path.is_symlink()):
                path.unlink()
                if not any(path.parent.iterdir()):
                    path.parent.rmdir()
        for name, group in GROUPS.items():
            key = f"{group}/{split}.jsonl"
            alias = out_dir / split / f"{name}.jsonl"
            if alias.is_file() or alias.is_symlink():
                alias.unlink()
            if key in counts:
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.symlink_to(Path("..") / key)
                trainer_views.setdefault(split, {})[name] = str(Path(split) / f"{name}.jsonl")
            elif alias.parent.is_dir() and not any(alias.parent.iterdir()):
                alias.parent.rmdir()
        prefix_alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        if prefix_alias.is_file() or prefix_alias.is_symlink():
            prefix_alias.unlink()
        if prefix_counts[split]:
            prefix_alias.parent.mkdir(parents=True, exist_ok=True)
            prefix_alias.symlink_to(Path("..") / "agent_auxiliary" / f"{split}.jsonl")
        elif prefix_alias.parent.is_dir() and not any(prefix_alias.parent.iterdir()):
            prefix_alias.parent.rmdir()
    kinds = ("efficient_success", "failure_recovery")
    missing_kinds = [kind for kind in kinds if kind not in references]
    if not missing_kinds and len(fixed_reference_kinds) != 2:
        references_path.parent.mkdir(parents=True, exist_ok=True)
        references_path.write_text(json.dumps([references[kind] for kind in kinds], ensure_ascii=False, indent=2), encoding="utf8")
    summary = {"counts": dict(counts), "skipped": dict(skipped), "missing_inputs": missing,
               "eligible_counts": dict(eligible), "source_target_counts": dict(saved_sources),
               "limited_counts": {key: count - counts[key] for key, count in eligible.items() if count > counts[key]},
               "trainer_root": ".", "trainer_views": trainer_views,
               "trajectory_prefix_count": sum(prefix_counts.values()),
               "references_status": "READY" if not missing_kinds else "MISSING",
               "fixed_references_reused": len(fixed_reference_kinds),
               "missing_reference_kinds": missing_kinds,
               "references_path": os.path.relpath(references_path, out_dir) if not missing_kinds else None,
               "dataset_revision": dataset_revision,
               "teacher_data_status": ("GENERATED" if teacher_statuses["GENERATED"] == sum(counts.values()) and counts
                                       else "PARTIAL" if teacher_statuses["GENERATED"] else "NOT_GENERATED"),
               "offline_teacher_schema_version": 1, "teacher_status_counts": dict(teacher_statuses),
               "teacher_model_ids": dict(teacher_models), "teacher_generation_requests": 0,
               "capability_snapshot_id": snapshot.get("snapshot_id"),
               "capability_evidence_status": snapshot.get("capability_evidence_status", "NOT_MEASURED"),
               "capability_measured_metric_count": snapshot.get("measured_metric_count", 0),
               "supplied_auxiliary_candidates": candidates,
               "v9_model_choice_target_count": target_scopes["v9_model_choice"],
               "v9_model_effort_target_count": target_scopes["v9_model_effort_choice"],
               "v9_native_effort_target_count": target_scopes["v9_native_effort_choice"],
               "supervision_type_counts": dict(supervision_types),
               "comparison_axis_counts": dict(comparison_axes),
               "comparison_task_count": len(set().union(*comparison_tasks.values())),
               "comparison_tasks_by_supervision_type": {
                   kind: len(tasks) for kind, tasks in comparison_tasks.items()},
               "auxiliary_not_model_choice_count": target_scopes["auxiliary_not_model_choice"],
               "supervision_qualification": "PRESERVED_SOURCE_TARGETS_AND_SPLITS",
               "feature_training_status": "FEATURE_NOT_TRAINED",
               "schema_fields_missing": [name for name in NEW_FEATURE_FIELDS if name not in PreDecisionState.model_fields],
               "formal_action_pool_id": ACTION_POOL_ID,
               "formal_action_pool_action_count": len(ACTION_POOL),
               "legacy_v9_k3_scope": "LEGACY_LUNA_HY4_TERRA_CANDIDATE_POOL_RESEARCH_ONLY",
               "formal_action_pool_note": "The legacy pool is not remapped to GLM-5.3-Flash; only complete paired verifier outcomes prepared by prepare_action_pool_record are current-pool supervision."}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--typed-root", type=Path)
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--v8-views", type=Path)
    parser.add_argument("--preview-root", type=Path)
    parser.add_argument("--trajectory", action="append", default=[], metavar="SOURCE_ID=PATH")
    parser.add_argument("--out-dir", type=Path, default=DATA_ROOT / "prepared")
    parser.add_argument("--reencode-prepared", action="store_true",
                        help="Reencode current physical views and link prefixes to S2; no teacher or network requests.")
    parser.add_argument("--references-path", type=Path, default=DATA_ROOT / "references" / "two_references.json")
    parser.add_argument("--split", choices=("train", "val"), action="append")
    parser.add_argument("--limit-per-view", type=int, default=64,
                        help="Maximum rows per view; source/target buckets are interleaved. Use 0 for all typed rows.")
    parser.add_argument("--max-episodes", type=int, default=1000,
                        help="Maximum raw trajectory rows scanned per input file.")
    parser.add_argument("--dataset-revision")
    parser.add_argument("--capabilities-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="Existing capability directory or current.json; preparation never refreshes it.")
    parser.add_argument("--candidate-action", action="append", default=[], metavar="MODEL[:EFFORT]",
                        help="Candidate input for auxiliary views only; original S1 choices remain unchanged.")
    args = parser.parse_args(argv)
    if args.reencode_prepared:
        print(json.dumps(reencode_prepared(args.out_dir), ensure_ascii=False))
        return 0
    summary = prepare(args.typed_root, inputs=args.input, v8_views=args.v8_views,
        preview_root=args.preview_root, trajectories=[item.split("=", 1) for item in args.trajectory],
        out_dir=args.out_dir, references_path=args.references_path, splits=args.split or ("train", "val"),
        limit_per_view=args.limit_per_view, max_episodes=args.max_episodes, dataset_revision=args.dataset_revision,
        capabilities_dir=args.capabilities_dir, candidates=args.candidate_action)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
