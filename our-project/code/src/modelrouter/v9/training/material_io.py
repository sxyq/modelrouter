"""Read saved supervision rows and encode the canonical Trainer views."""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import Counter
from pathlib import Path

from modelrouter.data_pipeline.batch_prep import _source_rows
from .constants import DATA_ROOT, GROUPS
from .prefix_replay import router_input_text
from .supervision import decision_state


def iter_rows(path):
    """Read existing files without loading weights or whole source tables."""
    path = Path(path)
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        source = pq.ParquetFile(path)
        columns = [name for name in (
            "instance_id", "trajectory_id", "traj_id", "messages", "resolved",
            "dataset_revision", "hf_dataset_name",
        ) if name in source.schema_arrow.names]
        index = 0
        for batch in source.iter_batches(batch_size=16, columns=columns):
            for row in batch.to_pylist():
                index += 1
                yield index, row
        return
    if str(path) == "-" or path.suffix == ".gz":
        stream = sys.stdin if str(path) == "-" else gzip.open(path, "rt", encoding="utf8")
        try:
            for index, line in enumerate(stream, 1):
                if line.strip():
                    yield index, json.loads(line)
        finally:
            if stream is not sys.stdin:
                stream.close()
        return
    yield from _source_rows(str(path))


def reencode_prepared(out_dir=DATA_ROOT / "prepared"):
    """Retain raw records and serialize physical S2 prefixes with the shared formatter."""
    out_dir = Path(out_dir)
    summary_path = out_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf8"))
    legacy_prefixes = {}
    for split in summary["trainer_views"]:
        alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        if alias.is_file() and not alias.is_symlink():
            legacy_prefixes[split] = [row for _, row in iter_rows(alias)]
    counts, sources, statuses, models, prefixes = Counter(), Counter(), Counter(), Counter(), Counter()
    trainer_views = {}
    for split in summary["trainer_views"]:
        for name, group in GROUPS.items():
            key = f"{group}/{split}.jsonl"
            path = out_dir / key
            if not path.is_file():
                continue
            rows = [row for _, row in iter_rows(path)]
            if name == "S2" and split in legacy_prefixes:
                existing = {row["provenance"]["stable_record_id"] for row in rows
                            if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX"}
                rows.extend(row for row in legacy_prefixes[split]
                            if row["provenance"]["stable_record_id"] not in existing)
            with path.open("w", encoding="utf8") as stream:
                for row in rows:
                    decision = decision_state(row["pre_decision_state"], row["provenance"].get("task_id"))
                    row["state"] = router_input_text(row, decision)
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    counts[key] += 1
                    sources[f"{key}:{row['provenance']['source_id']}:{row['_meta']['target']}"] += 1
                    teacher = row["offline_teacher_state"]
                    statuses[teacher["status"]] += 1
                    if teacher["assessment"]:
                        models[teacher["assessment"]["teacher_model_id"]] += 1
                    if row["_meta"].get("input_kind") == "TRAJECTORY_PREFIX":
                        prefixes[split] += 1
            trainer_views.setdefault(split, {})[name] = str(Path(split) / f"{name}.jsonl")
        alias = out_dir / "trajectory_prefixes" / f"{split}.jsonl"
        target = Path("..") / "agent_auxiliary" / f"{split}.jsonl"
        if prefixes[split] and (not alias.is_symlink() or Path(os.readlink(alias)) != target):
            if alias.is_file() or alias.is_symlink():
                alias.unlink()
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to(target)
    eligible = summary.get("eligible_counts", {})
    for split in trainer_views:
        old_key = f"trajectory_prefixes/{split}.jsonl"
        if old_key in eligible:
            key = f"agent_auxiliary/{split}.jsonl"
            eligible[key] = eligible.get(key, 0) + eligible.pop(old_key)
    references = summary.get("references_path")
    if references and Path(references).is_absolute():
        references = os.path.relpath(references, out_dir)
    summary.update(counts=dict(counts), source_target_counts=dict(sources),
                   eligible_counts=eligible, trainer_root=".", trainer_views=trainer_views,
                   limited_counts={key: value - counts[key] for key, value in eligible.items() if value > counts[key]},
                   references_path=references, trajectory_prefix_count=sum(prefixes.values()),
                   teacher_status_counts=dict(statuses), teacher_model_ids=dict(models),
                   teacher_data_status=("GENERATED" if counts and statuses["GENERATED"] == sum(counts.values())
                                        else "PARTIAL" if statuses["GENERATED"] else "NOT_GENERATED"),
                   router_serializer="modelrouter.v9.runtime.context.format_router_payload")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf8")
    return summary
