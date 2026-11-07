"""Shared paths and prepared Trainer view names."""
from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parents[4] / "data" / "v9"
GROUPS = {"S1": "model_comparison", "S2": "agent_auxiliary", "S3": "system_auxiliary"}
PUBLIC_TRAJECTORIES = {"TRA-001", "TRA-002"}
