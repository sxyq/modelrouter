#!/usr/bin/env python3
"""
inventory_repo.py - Read-Only Project Directory Inventory & Migration Manifest Generator
Strictly adheres to REPOSITORY_STRUCTURE_MIGRATION_20261018.md Section V:
1. Performs read-only inventory on Mac and/or A6000 server.
2. Inspects git status, tracked, untracked, ignored, file sizes, extensions, and process bindings.
3. Generates structured migration manifest:
   old_path, new_path, category, consumer, process_active, move_status, compatible_entry, verification_result
4. Excludes API keys, credentials, and private prompt/completion data.
5. Outputs inventory_{platform}_{timestamp}.json.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


# Critical patterns that must NEVER have their contents read or dumped
SECRET_PATTERNS = ["*credential*", "*.key", "*.secret", "id_ed25519*"]


def is_secret_file(path_str: str) -> bool:
    lower = path_str.lower()
    return any(p in lower for p in ["credential", ".key", ".secret", "id_ed25519", "token_budget"])


def get_git_info(repo_root: Path) -> Dict[str, Any]:
    info = {"is_git": False, "head": "", "branch": "", "status_short": []}
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root, text=True).strip()
        status = subprocess.check_output(["git", "status", "--short"], cwd=repo_root, text=True).strip().splitlines()
        info.update({"is_git": True, "head": head, "branch": branch, "status_short": status[:50]})
    except Exception as e:
        info["error"] = str(e)
    return info


def classify_path(rel_path: str) -> Dict[str, str]:
    """Classifies a relative path into category and prospective destination under our-project/."""
    p = Path(rel_path)
    parts = p.parts
    if not parts:
        return {"category": "ROOT", "new_path": rel_path, "consumer": "general"}

    top = parts[0]

    if top == "our-project":
        return {"category": "CANONICAL", "new_path": rel_path, "consumer": "canonical"}

    if top == "router_data":
        if any(x in rel_path for x in ["run_full_graded_queue", "laya_batch_train", "run_kev"]):
            return {"category": "TRAINING_CORE", "new_path": f"our-project/code/src/modelrouter/training/{p.name}", "consumer": "a6000_training_daemon"}
        elif any(x in rel_path for x in ["checkpoint_inventory", "checkpoint_retention", "server_monitor"]):
            return {"category": "TRAINING_OPS", "new_path": f"our-project/code/src/modelrouter/training/checkpoints/{p.name}", "consumer": "a6000_monitoring"}
        elif any(x in rel_path for x in ["audit_"]):
            return {"category": "AUDIT", "new_path": f"our-project/code/src/modelrouter/data_pipeline/quality/{p.name}", "consumer": "audit"}
        elif any(x in rel_path for x in ["test_"]):
            return {"category": "TEST", "new_path": f"our-project/code/tests/{p.name}", "consumer": "ci_test"}
        else:
            return {"category": "DATA_PIPELINE", "new_path": f"our-project/code/src/modelrouter/data_pipeline/sources/{p.name}", "consumer": "data_prep"}

    if top == "experiments":
        if "router_serving" in parts:
            return {"category": "SERVING", "new_path": f"our-project/code/src/modelrouter/serving/{p.name}", "consumer": "fastapi_server"}
        elif "agent_pilot" in parts:
            if "baselines" in parts:
                return {"category": "BASELINES", "new_path": f"our-project/code/src/modelrouter/baselines/{p.name}", "consumer": "benchmark_matrix"}
            elif "pricing" in parts:
                return {"category": "PRICING", "new_path": f"our-project/code/src/modelrouter/providers/pricing/{p.name}", "consumer": "provider_cost"}
            else:
                return {"category": "AGENT_PILOT", "new_path": f"our-project/code/src/modelrouter/agent/{p.name}", "consumer": "agent_eval"}
        elif "harbor" in parts:
            return {"category": "SANDBOX_BENCHMARK", "new_path": f"our-project/code/src/modelrouter/sandbox/{p.name}", "consumer": "harbor_eval"}
        return {"category": "EXPERIMENTS", "new_path": f"our-project/experiments/{rel_path}", "consumer": "experiments"}

    if top == "scripts":
        if "fetch_live_status" in rel_path:
            return {"category": "TELEMETRY", "new_path": "our-project/code/src/modelrouter/telemetry/fetch_live_status.py", "consumer": "dashboard_sync"}
        return {"category": "SCRIPTS_LEGACY", "new_path": f"our-project/docs/operations/legacy/{p.name}", "consumer": "legacy_ops"}

    if top == "docs":
        if "training-dashboard" in parts:
            return {"category": "DASHBOARD", "new_path": f"our-project/dashboard/{'/'.join(parts[2:])}", "consumer": "dashboard_8765"}
        return {"category": "DOCS", "new_path": f"our-project/docs/{rel_path}", "consumer": "documentation"}

    if top == "research" or top == "papers":
        return {"category": "RESEARCH_LITERATURE", "new_path": f"our-project/external/research/{rel_path}", "consumer": "literature_review"}

    if top == "external-projects":
        return {"category": "EXTERNAL_PROJECTS", "new_path": f"our-project/external/research/project_catalog/{p.name}", "consumer": "reference"}

    if top == "external":
        return {"category": "EXTERNAL_REPOS", "new_path": f"our-project/external/{'/'.join(parts[1:])}", "consumer": "upstream_benchmarks"}

    if top == "汇报":
        return {"category": "REPORTS", "new_path": f"our-project/docs/reports/{'/'.join(parts[1:])}", "consumer": "group_presentations"}

    if top == "prepare_router_data.py":
        return {"category": "DATA_ENTRY", "new_path": "our-project/code/cli/prepare_router_data.py", "consumer": "pipeline_cli"}

    if top == "runs":
        return {"category": "RUNS_RESULTS", "new_path": f"our-project/results/{'/'.join(parts[1:])}", "consumer": "evaluation_results"}

    return {"category": "OTHER", "new_path": f"our-project/{rel_path}", "consumer": "general"}


def scan_directory(root_dir: Path, active_pids: List[str]) -> List[Dict[str, Any]]:
    manifest = []
    
    # Check running processes to see if scripts are active
    active_cmdlines = ""
    try:
        active_cmdlines = subprocess.check_output(["ps", "aux"], text=True)
    except Exception:
        pass

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Prune heavy hidden or checkout dirs from deep walk, but log top-level
        rel_dir = os.path.relpath(dirpath, root_dir)
        if any(p in rel_dir for p in [".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"]):
            continue

        for f in filenames:
            full_path = Path(dirpath) / f
            rel_path = os.path.relpath(full_path, root_dir)

            try:
                stat = full_path.stat()
                size_bytes = stat.st_size
                ext = full_path.suffix.lower()
            except Exception as e:
                manifest.append({
                    "old_path": rel_path,
                    "new_path": "",
                    "category": "UNREADABLE",
                    "error": str(e),
                    "move_status": "SKIPPED_UNREADABLE"
                })
                continue

            # Classify
            classification = classify_path(rel_path)
            
            # Check process active
            is_active = f in active_cmdlines and ext in [".py", ".sh"]

            # Safe move status
            if classification["category"] == "CANONICAL":
                move_status = "CANONICAL_ALREADY"
            elif is_active:
                move_status = "HOLD_ACTIVE_PROCESS"
            elif classification["category"] in ["TRAINING_CORE", "SERVING"]:
                move_status = "HOLD_REQUIRES_SHIM"
            else:
                move_status = "ELIGIBLE_MIGRATE"

            manifest.append({
                "old_path": rel_path,
                "new_path": classification["new_path"],
                "category": classification["category"],
                "consumer": classification["consumer"],
                "size_bytes": size_bytes,
                "extension": ext,
                "process_active": is_active,
                "move_status": move_status,
                "compatible_entry": f"{rel_path} -> shim" if move_status.startswith("HOLD") else "direct",
                "verification_result": "PENDING"
            })

    return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Inventory repository files for our-project migration")
    parser.add_argument("--platform", choices=["mac", "a6000"], default="mac")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-dir", default="our-project/docs/operations")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"inventory_{args.platform}_{timestamp}.json"

    print(f"Starting inventory on {args.platform} at {repo_root}...")
    git_info = get_git_info(repo_root)
    manifest = scan_directory(repo_root, [])

    summary = {
        "platform": args.platform,
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "git": git_info,
        "total_files": len(manifest),
        "by_category": {},
        "by_move_status": {},
        "manifest": manifest
    }

    for item in manifest:
        cat = item.get("category", "UNKNOWN")
        status = item.get("move_status", "UNKNOWN")
        summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1
        summary["by_move_status"][status] = summary["by_move_status"].get(status, 0) + 1

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Inventory completed: {len(manifest)} files indexed.")
    print(f"Summary by category: {json.dumps(summary['by_category'], indent=2)}")
    print(f"Summary by move status: {json.dumps(summary['by_move_status'], indent=2)}")
    print(f"Manifest written to {out_file}")


if __name__ == "__main__":
    main()
