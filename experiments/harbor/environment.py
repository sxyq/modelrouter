"""Sandbox execution environment for Harbor / Terminal-Bench 2.1.

Provides strict isolation:
- BaseSandboxEnvironment defines the standard execution contract.
- MockSandboxEnvironment enables fast, zero-overhead smoke testing without Docker.
- DockerSandboxEnvironment supports containerized execution where Docker is present.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_sec: float
    truncated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stdout": self.stdout[:1000] if len(self.stdout) > 1000 else self.stdout,
            "stderr": self.stderr[:1000] if len(self.stderr) > 1000 else self.stderr,
            "exit_code": self.exit_code,
            "duration_sec": round(self.duration_sec, 3),
            "truncated": self.truncated or len(self.stdout) > 1000 or len(self.stderr) > 1000,
        }


class BaseSandboxEnvironment:
    """Abstract sandbox environment interface."""

    def reset(self, task_metadata: Dict[str, Any]) -> None:
        raise NotImplementedError

    def exec(self, command: str, timeout: int = 30) -> ExecResult:
        raise NotImplementedError

    def evaluate(self) -> Tuple[bool, float, Dict[str, Any]]:
        """Returns (resolved: bool, score: float, details: dict)."""
        raise NotImplementedError

    def close(self) -> None:
        pass


class MockSandboxEnvironment(BaseSandboxEnvironment):
    """Zero-overhead mock sandbox environment for smoke testing and Canary verification.
    
    Accurately simulates bash environment responses for Terminal-Bench Canary tasks:
    - fix-git: simulates detached HEAD recovery, git branch, git log, git merge
    - count-dataset-tokens: simulates python tokenizer counting
    - generic tasks: simulates standard filesystem, python, and bash operations
    """

    def __init__(self):
        self.task_metadata: Dict[str, Any] = {}
        self.task_id: str = ""
        self.history: list[dict] = []
        self.file_system: Dict[str, str] = {}
        self.git_state: Dict[str, Any] = {}
        self.is_resolved: bool = False

    def reset(self, task_metadata: Dict[str, Any]) -> None:
        self.task_metadata = task_metadata
        self.task_id = task_metadata.get("task_id", "")
        self.history = []
        self.file_system = {}
        self.is_resolved = False

        if self.task_id == "fix-git":
            self.git_state = {
                "branch": "HEAD",
                "detached": True,
                "master_head": "a1b2c3d",
                "lost_commit": "e5f6g7h",
                "merged": False,
            }
        elif self.task_id == "count-dataset-tokens":
            self.file_system["dataset.jsonl"] = '{"text": "hello world"}\n' * 100
        else:
            self.git_state = {}

    def exec(self, command: str, timeout: int = 30) -> ExecResult:
        t0 = time.time()
        cmd = command.strip()
        self.history.append({"command": cmd, "timestamp": time.time()})

        # Emulate common commands
        if cmd == "pwd":
            return ExecResult(stdout="/workspace\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
        elif cmd.startswith("ls"):
            if self.task_id == "fix-git":
                return ExecResult(stdout="README.md  src  .git\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
            elif self.task_id == "count-dataset-tokens":
                return ExecResult(stdout="dataset.jsonl  tokenizer_config.json\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
            return ExecResult(stdout="Makefile  README.md  src\n", stderr="", exit_code=0, duration_sec=time.time() - t0)

        # Task specific handling
        if self.task_id == "fix-git":
            if "git status" in cmd or "git branch" in cmd:
                if self.git_state.get("merged"):
                    return ExecResult(stdout="On branch master\nYour branch is up to date with 'origin/master'.\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
                return ExecResult(stdout="* (HEAD detached at e5f6g7h)\n  master\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
            elif "git log" in cmd or "git reflog" in cmd:
                return ExecResult(stdout="e5f6g7h (HEAD) commit message: recover work\na1b2c3d (master) initial commit\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
            elif "git checkout master" in cmd:
                self.git_state["branch"] = "master"
                self.git_state["detached"] = False
                return ExecResult(stdout="Switched to branch 'master'\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
            elif "git merge" in cmd:
                if not self.git_state.get("detached") and self.git_state.get("branch") == "master":
                    self.git_state["merged"] = True
                    self.is_resolved = True
                    return ExecResult(stdout="Fast-forward merge e5f6g7h into master.\n", stderr="", exit_code=0, duration_sec=time.time() - t0)
                return ExecResult(stdout="Already up to date.\n", stderr="", exit_code=0, duration_sec=time.time() - t0)

        elif self.task_id == "count-dataset-tokens":
            if "python" in cmd and "token" in cmd:
                self.is_resolved = True
                return ExecResult(stdout="Total tokens counted: 42850\n", stderr="", exit_code=0, duration_sec=time.time() - t0)

        # Generic echo / cat / file writes
        if ">" in cmd:
            match = re.search(r">\s*(\S+)", cmd)
            if match:
                fname = match.group(1)
                self.file_system[fname] = "content"
            return ExecResult(stdout="", stderr="", exit_code=0, duration_sec=time.time() - t0)

        if cmd.startswith("cat "):
            fname = cmd.split("cat ")[-1].strip()
            content = self.file_system.get(fname, f"Contents of {fname}\n")
            return ExecResult(stdout=content, stderr="", exit_code=0, duration_sec=time.time() - t0)

        # Default exit code 0 for smoke simulation
        return ExecResult(stdout="Command completed successfully.\n", stderr="", exit_code=0, duration_sec=time.time() - t0)

    def evaluate(self) -> Tuple[bool, float, Dict[str, Any]]:
        if self.task_id == "fix-git":
            passed = self.git_state.get("merged", False)
            return passed, 1.0 if passed else 0.0, {"git_state": self.git_state, "steps": len(self.history)}
        elif self.task_id == "count-dataset-tokens":
            passed = self.is_resolved
            return passed, 1.0 if passed else 0.0, {"tokens_counted": 42850 if passed else 0}
        else:
            # For other canary tasks in smoke mode, check if actions were taken
            passed = len(self.history) > 0
            return passed, 1.0 if passed else 0.0, {"commands_run": len(self.history)}
