#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive ID-level reconciliation between V1 and V2.1 quality stratification."""

import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


def audit_stratification(project_root: Path):
    prep_dir = project_root / "runs" / "MR-ALLDATA-PREP-20261011"
    v1_root = prep_dir / "quality_grading"
    v2_root = prep_dir / "quality_grading_v2_1"

    print(f"Auditing V1 ({v1_root}) vs V2.1 ({v2_root}) at ID-Level...", flush=True)

    levels = ["level1", "level2", "level3", "level4"]

    # 1. Read V1 records
    print("Reading V1 records...", flush=True)
    v1_records = {} # rec_id -> (level, unit_id, source_id, quality_grade, split)
    v1_level_counts = Counter()
    v1_sources = Counter()
    v1_grades = Counter()

    for lvl in levels:
        lvl_dir = v1_root / lvl
        for gz_file in sorted(lvl_dir.glob("*.jsonl.gz")):
            with gzip.open(gz_file, "rt", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    rec_id = data.get("record_id")
                    unit_id = data.get("unit_id")
                    src = data.get("source_id")
                    q = data.get("quality_grade")
                    sp = data.get("split_identity") or "train"
                    v1_records[rec_id] = (lvl, unit_id, src, q, sp)
                    v1_level_counts[lvl] += 1
                    v1_sources[src] += 1
                    v1_grades[q] += 1

    print(f"Total V1 records read: {len(v1_records):,}", flush=True)

    # 2. Read V2.1 records
    print("Reading V2.1 records...", flush=True)
    v2_records = {} # rec_id -> (level, unit_id, source_id, quality_grade, split)
    v2_level_counts = Counter()
    v2_sources = Counter()
    v2_grades = Counter()

    for lvl in levels:
        lvl_dir = v2_root / lvl
        for gz_file in sorted(lvl_dir.glob("*.jsonl.gz")):
            with gzip.open(gz_file, "rt", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    rec_id = data.get("stable_record_id")
                    unit_id = data.get("independent_unit_id")
                    src = data.get("source_id")
                    q = data.get("quality_grade")
                    sp = data.get("split") or "train"
                    v2_records[rec_id] = (lvl, unit_id, src, q, sp)
                    v2_level_counts[lvl] += 1
                    v2_sources[src] += 1
                    v2_grades[q] += 1

    print(f"Total V2.1 records read: {len(v2_records):,}", flush=True)

    # 3. Intersections and unique counts
    v1_keys = set(v1_records.keys())
    v2_keys = set(v2_records.keys())
    common_keys = v1_keys.intersection(v2_keys)
    only_v1 = v1_keys - v2_keys
    only_v2 = v2_keys - v1_keys

    print(f"Common records: {len(common_keys):,} ({len(common_keys)/max(1, len(v1_keys))*100:.2f}%)")
    print(f"Only V1: {len(only_v1):,}")
    print(f"Only V2.1: {len(only_v2):,}")

    # 4. Level Migration Matrix (4x4)
    migration_matrix = {l1: {l2: 0 for l2 in levels} for l1 in levels}
    split_mismatches = 0
    unit_mismatches = 0

    migration_by_source = defaultdict(lambda: Counter())

    for k in common_keys:
        lvl1, u1, s1, q1, sp1 = v1_records[k]
        lvl2, u2, s2, q2, sp2 = v2_records[k]

        migration_matrix[lvl1][lvl2] += 1
        if lvl1 != lvl2:
            migration_by_source[s1][f"{lvl1}->{lvl2}"] += 1

        if sp1 != sp2:
            split_mismatches += 1
        if u1 != u2:
            unit_mismatches += 1

    # 5. Fixed validation set intersection audit
    print("Auditing Train vs Fixed Validation true intersection...", flush=True)
    val_ids = set()
    val_units = set()
    val_file_hashes = {}
    val_file_counts = {}

    # Read from canonical validation directory
    val_dirs = [
        project_root / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "val",
        project_root / "runs" / "MR-ALLDATA-PREP-20261011" / "evaluation",
    ]
    val_dirs.extend(sorted(project_root.glob("runs/*/val")))

    checked_dirs = []
    for vdir in val_dirs:
        if not vdir.is_dir() or vdir in checked_dirs:
            continue
        checked_dirs.append(vdir)
        for vf in sorted(vdir.glob("*.jsonl*")):
            opener = gzip.open if vf.name.endswith(".gz") else open
            # Calculate SHA256
            import hashlib
            h = hashlib.sha256()
            with open(vf, "rb") as f_bin:
                for chunk in iter(lambda: f_bin.read(65536), b""):
                    h.update(chunk)
            val_file_hashes[vf.name] = h.hexdigest()

            count = 0
            try:
                with opener(vf, "rt", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        count += 1
                        d = json.loads(line)
                        prov = d.get("provenance", {}) if isinstance(d.get("provenance"), dict) else {}
                        rid = prov.get("stable_record_id") or d.get("stable_record_id") or d.get("record_id")
                        uid = prov.get("independent_unit_id") or d.get("independent_unit_id") or d.get("unit_id")
                        if rid:
                            val_ids.add(rid)
                        if uid:
                            val_units.add(uid)
                val_file_counts[vf.name] = count
            except Exception as e:
                print(f"Warning reading validation file {vf}: {e}")

    # Fallback to validation manifest if jsonl not found
    val_manifest_path = project_root / "runs" / "MR-FULL-GRADED-P0-DATA-REPAIR-20261012" / "fixed_validation_manifest.json"
    if val_manifest_path.is_file():
        try:
            val_m = json.loads(val_manifest_path.read_text())
            for task_fam, tdata in val_m.get("task_families", {}).items():
                for row in tdata.get("items", []):
                    if "record_id" in row:
                        val_ids.add(row["record_id"])
                    if "independent_unit_id" in row:
                        val_units.add(row["independent_unit_id"])
        except Exception as e:
            print(f"Error reading fixed val manifest: {e}")

    if len(val_ids) == 0:
        raise ValueError(
            "Audit failure: Fixed validation set is empty or missing! "
            "Cannot claim zero data leakage without non-empty validation set."
        )

    train_ids = {k for k, v in v2_records.items() if v[4] == "train"}
    train_units = {v[1] for k, v in v2_records.items() if v[4] == "train"}

    train_val_id_intersection = sorted(list(train_ids.intersection(val_ids)))
    train_val_unit_intersection = sorted(list(train_units.intersection(val_units)))
    zero_leakage_verified = (len(train_val_id_intersection) == 0 and len(train_val_unit_intersection) == 0)

    print(f"Fixed Validation Files Scanned: {val_file_counts}")
    print(f"Fixed Validation Record IDs found: {len(val_ids):,}")
    print(f"Fixed Validation Unit IDs found: {len(val_units):,}")
    print(f"Train vs Val Record ID Intersection: {len(train_val_id_intersection)}")
    print(f"Train vs Val Unit ID Intersection: {len(train_val_unit_intersection)}")
    print(f"Zero Leakage Verified: {zero_leakage_verified}")

    report = {
        "generated_at": _now_iso(),
        "summary": {
            "v1_total": len(v1_records),
            "v2_1_total": len(v2_records),
            "common_records": len(common_keys),
            "only_v1_records": len(only_v1),
            "only_v2_records": len(only_v2),
            "unit_id_mismatches": unit_mismatches,
            "split_mismatches": split_mismatches,
        },
        "v1_level_counts": dict(v1_level_counts),
        "v2_1_level_counts": dict(v2_level_counts),
        "migration_matrix": migration_matrix,
        "migration_by_source": {s: dict(c) for s, c in migration_by_source.items()},
        "validation_leakage_audit": {
            "status": "PASS" if zero_leakage_verified else "FAIL_LEAKAGE_DETECTED",
            "val_files": val_file_counts,
            "val_file_sha256": val_file_hashes,
            "total_val_records": len(val_ids),
            "total_val_units": len(val_units),
            "train_val_record_overlap": len(train_val_id_intersection),
            "train_val_unit_overlap": len(train_val_unit_intersection),
            "zero_leakage_verified": zero_leakage_verified,
        }
    }

    out_file = project_root / "router_data" / "v1_v2_stratification_audit.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Wrote audit report to {out_file}", flush=True)
    return report

def _now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    audit_stratification(root)
