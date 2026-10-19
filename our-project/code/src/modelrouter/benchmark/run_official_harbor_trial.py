"""Historical module entry delegates to the single benchmark CLI.

Harbor commands, iteration state and execution are owned by __main__.
"""
from __future__ import annotations

import sys
from pathlib import Path


def run_trial(
    task_id: str = "fix-git", policy: str = "fixed_strong", *,
    iteration_dir: Path | None = None, agent: str = "modelrouter",
    model: str | None = None, environment: str = "docker",
    execute: bool = True,
) -> int:
    """Preserve the callable entry without another task execution path."""
    from .__main__ import main

    argv = ["run", "--task", task_id, "--agent", agent,
            "--policies", policy, "--environment", environment]
    if iteration_dir is not None:
        argv.extend(["--iteration-dir", str(iteration_dir)])
    if model is not None:
        argv.extend(["--model", model])
    if not execute:
        argv.append("--dry-run")
    return main(argv)


if __name__ == "__main__":
    from .__main__ import main
    raise SystemExit(main(["run", *sys.argv[1:]]))
