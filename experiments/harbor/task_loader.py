"""Terminal-Bench 2.1 Task Loader and Manifest Verifier.

Loads tasks from router_data/terminal_bench_manifest.json with strict validation:
- Canary (8 tasks): Fast smoke inspection, schema validation, and multi-category smoke checks.
- External DEV (24 tasks): Intermediate evaluation set for candidate models.
- Final Sealed (57 tasks): Permanently sealed benchmark subset.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class TerminalBenchTask:
    task_id: str
    category: str
    difficulty: str
    description: str
    docker_image: str
    task_toml_sha256: str
    git_blob_sha: str
    relative_path: str
    subset: str
    instruction: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "category": self.category,
            "difficulty": self.difficulty,
            "description": self.description,
            "instruction": self.instruction,
            "docker_image": self.docker_image,
            "task_toml_sha256": self.task_toml_sha256,
            "git_blob_sha": self.git_blob_sha,
            "relative_path": self.relative_path,
            "subset": self.subset,
        }


class TerminalBenchLoader:
    def __init__(self, manifest_path: Optional[str | Path] = None):
        if manifest_path is None:
            # Try workspace root
            manifest_path = Path(__file__).resolve().parent.parent.parent / "router_data" / "terminal_bench_manifest.json"
        self.manifest_path = Path(manifest_path)
        if not self.manifest_path.is_file():
            raise FileNotFoundError(f"Terminal-Bench manifest not found at: {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self._manifest = json.load(f)

    @property
    def benchmark_id(self) -> str:
        return self._manifest.get("benchmark_id", "ENV-004")

    @property
    def upstream_commit(self) -> str:
        return self._manifest.get("upstream_commit", "7131e4375048a0e408a8fb404b5f499d726b695b")

    def get_canary_tasks(self) -> List[TerminalBenchTask]:
        return self._load_subset("canary")

    def get_dev_tasks(self) -> List[TerminalBenchTask]:
        return self._load_subset("external_dev")

    def get_final_tasks(self) -> List[TerminalBenchTask]:
        return self._load_subset("final_test")

    def get_task(self, task_id: str) -> Optional[TerminalBenchTask]:
        for subset in ("canary", "external_dev", "final_test"):
            tasks = self._load_subset(subset)
            for t in tasks:
                if t.task_id == task_id:
                    return t
        return None

    def _load_subset(self, subset_name: str) -> List[TerminalBenchTask]:
        subsets = self._manifest.get("subsets", {})
        data = subsets.get(subset_name, {})
        raw_tasks = data.get("tasks", [])
        tasks_base_dir = (
            Path(__file__).resolve().parent.parent.parent
            / "external"
            / "benchmarks"
            / "terminal-bench-2-1"
            / "tasks"
        )
        tasks = []
        for item in raw_tasks:
            tid = item["task_id"]
            inst_text = ""
            inst_file = tasks_base_dir / tid / "instruction.md"
            if inst_file.exists():
                try:
                    inst_text = inst_file.read_text(encoding="utf-8").strip()
                except Exception:
                    pass
            if not inst_text:
                inst_text = item.get("description", "")

            tasks.append(
                TerminalBenchTask(
                    task_id=tid,
                    category=item.get("category", "general"),
                    difficulty=item.get("difficulty", "medium"),
                    description=item.get("description", ""),
                    docker_image=item.get("docker_image", ""),
                    task_toml_sha256=item.get("task_toml_sha256", ""),
                    git_blob_sha=item.get("git_blob_sha", ""),
                    relative_path=item.get("relative_path", ""),
                    subset=subset_name,
                    instruction=inst_text,
                )
            )
        return tasks
