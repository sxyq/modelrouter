"""Legacy script imports use the existing package implementation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project/code/src"))

from modelrouter.data_pipeline.sources.env_memory import (
    process_env_001, process_env_002, process_mem_003, process_mem_005,
    process_mas_001, run_mem_mas_env_batch,
)
