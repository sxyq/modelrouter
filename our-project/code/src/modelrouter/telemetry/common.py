"""Shared state and value helpers for telemetry collectors."""
from __future__ import annotations

import json
import math
import re
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5]
OLD_CORE_IDS = {
    "P0_B03_C01_QB_PB-e02", "P0_B01_C01_QB_PB-e02", "P0_B03_C05_QB_PB-e02",
    "P0_B03_C08_QB_PB-e02", "P0_B02_C01_QB_PB-e02",
}
_JSON_CACHE = {}
_LOG_CACHE = {}
_HISTORY = {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def finite_values(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite_values(v) for k, v in value.items()}
    if isinstance(value, list):
        return [finite_values(v) for v in value]
    return value


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(finite_values(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def public_training_record(value, project_root=PROJECT_ROOT):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, str):
        return value.replace(str(project_root) + "/", "").replace(str(project_root), ".")
    if isinstance(value, dict):
        return {public_training_record(k, project_root): public_training_record(v, project_root)
                for k, v in value.items() if k not in ("raw_output", "error")}
    if isinstance(value, list):
        return [public_training_record(v, project_root) for v in value]
    return value


def read_json(path, default=None):
    path = Path(path)
    if not path.is_file():
        return default
    st = path.stat()
    identity = (st.st_mtime_ns, st.st_size)
    saved = _JSON_CACHE.get(str(path))
    if saved and saved[0] == identity:
        return saved[1]
    value = json.loads(path.read_text(encoding="utf-8"))
    _JSON_CACHE[str(path)] = (identity, value)
    return value


def age_seconds(value):
    if not value:
        return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return max(0, time.time() - dt.timestamp())


def relative(path, root):
    return str(Path(path).relative_to(root))


def run_key(family, path, root):
    return family + "--" + re.sub(r"[^a-zA-Z0-9_.-]", "--", relative(path, root))


def kev_cursor(directory):
    directory = Path(directory)
    return directory / "cursor.json" if (directory / "cursor.json").is_file() else directory.parent / "cursor.json"
