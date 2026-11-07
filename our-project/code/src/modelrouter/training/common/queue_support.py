"""Shared filesystem, GPU, and matrix-materialization operations for training queues."""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Tuple

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
_SRC_ROOT = str(Path(__file__).resolve().parents[3])
for _path in (_WORKSPACE_ROOT, _SRC_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _write_json(path: Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    tmp.replace(path)

def check_gpu_available(reserve_mib: int = 4096) -> Tuple[bool, Dict[str, Any]]:
    """Allow the next sequential Laya run with its observed 11.6 GiB peak rounded to 12 GiB."""
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        ).strip()
        line = out.splitlines()[0]
        parts = [p.strip() for p in line.split(",")]
        used_mib = float(parts[3])
        free_mib = float(parts[4])
        util_pct = float(parts[5])
        required_mib = 12288 + reserve_mib
        info = {
            "gpu_index": int(parts[0]),
            "gpu_name": parts[1],
            "memory_total_mib": float(parts[2]),
            "memory_used_mib": used_mib,
            "utilization_pct": util_pct,
            "memory_free_mib": free_mib,
            "required_free_mib": required_mib,
        }
        return free_mib >= required_mib, info
    except Exception as exc:
        return False, {"error": repr(exc)}


def materialize_plan_on_demand(
    project_root: Path,
    out_root: Path,
    manifest: Dict[str, Any],
    manifest_path: Path,
    run_id: str,
) -> bool:
    """Materialize an eligible unmaterialized plan using `router_data/batch_prep.py`."""
    plans = manifest.get("plans") or {}
    spec = plans.get(run_id)
    if not spec:
        return False
    base_id = spec.get("base_run_id") or (run_id[3:] if run_id.startswith("P0_") else run_id)
    p0_id = run_id if run_id.startswith("P0_") else f"P0_{base_id}"

    data_dir = out_root / "data" / p0_id
    groups = list(spec.get("groups") or spec.get("supervision_classes") or [])
    if all((data_dir / "train" / f"{g}.jsonl").is_file() for g in groups):
        return True

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from router_data.batch_prep import prepare_full_matrix

    graded_root = project_root / "runs" / "MR-ALLDATA-PREP-20261011" / "quality_grading_v2_1"
    if not graded_root.is_dir():
        return False
    generation = manifest.get("generation") or {}
    materialization_started = time.monotonic()
    # Stage only new data; the existing preparation function writes a complete matrix.
    # Keep its temporary metadata away from the current plans and completed-run material.
    with tempfile.TemporaryDirectory(prefix="_matrix_prep_", dir=out_root) as prep_dir:
        prepared = prepare_full_matrix(argparse.Namespace(
            all_data_out_dir=str(graded_root.parent),
            cleaned_root=str(project_root / "data" / "公开数据" / "清洗数据"),
            matrix_out_dir=prep_dir,
            matrix_run_prefix="P0_",
            matrix_run_ids=base_id,
            matrix_source_manifest=str(manifest_path),
            matrix_pool_limit=int(generation.get("pool_limit", 6000)),
            matrix_max_items=int(generation.get("max_items_per_class", 4096)),
        ))
        materialized_spec = prepared["plans"][p0_id]
        if not materialized_spec.get("materialized"):
            return False
        materialized_spec.setdefault("materialization_audit", {})["materialization_seconds"] = time.monotonic() - materialization_started
        data_dir.parent.mkdir(parents=True, exist_ok=True)
        (Path(prep_dir) / "data" / p0_id).rename(data_dir)
        plans[run_id] = materialized_spec
        manifest.setdefault("materialized", {})[run_id] = prepared["materialized"][p0_id]
        manifest.setdefault("materialization_audit", {})[run_id] = prepared["materialization_audit"][p0_id]
        manifest.setdefault("aggregate", {})["materialized_runs"] = len(manifest["materialized"])
        _write_json(manifest_path, manifest)
    return True

