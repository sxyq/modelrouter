"""CLI and public interface for the ModelRouter training queues."""
import argparse
import json
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
_SRC_ROOT = str(Path(__file__).resolve().parents[3])
for _path in (_WORKSPACE_ROOT, _SRC_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from modelrouter.training.common.queue_support import (
    _now_iso, _write_json, check_gpu_available, materialize_plan_on_demand,
)
from modelrouter.training.common.checkpoint_retention import (
    DEFAULT_ACTIVE_BUDGET_BYTES, GIB, LEGACY_PROTOCOL_VERSION, NEW_PROTOCOL_VERSION,
    CheckpointRetentionManager, DiskBudgetExceededError, compute_run_dedup_signature,
    has_physical_weights, load_or_default_baseline_0,
)
from modelrouter.training.common.matrix_queue import build_ordered_queue, run_queue, _git_sync_dashboard
from modelrouter.training.common.full_coverage_queue import (
    FULL_COVERAGE_STAGE_MAP, build_ordered_full_coverage_queue,
    run_continuous_full_coverage_queue,
)

def main() -> None:
    parser = argparse.ArgumentParser(description="ModelRouter Automated Queue Controller")
    parser.add_argument("--mode", choices=["continuous_full_coverage", "config_exploration"], default="continuous_full_coverage",
                        help="Execution mode: continuous_full_coverage (Mode B) or config_exploration (Mode A)")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-root", default="runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012")
    parser.add_argument("--manifest", default="")
    parser.add_argument("--model-dir", default="models/laya-421m")
    parser.add_argument("--graded-root", default="runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1")
    parser.add_argument("--cleaned-root", default="data/公开数据/清洗数据")
    parser.add_argument("--chunk-size", type=int, default=8192)
    parser.add_argument("--max-runs", type=int, default=0, help="0 means unlimited (continuous run until all completed)")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--active-budget-gib", type=float, default=120.0)
    parser.add_argument("--stages", default="1,2,3,4,5,6,7")
    parser.add_argument("--sync-github-every", type=int, default=0)
    parser.add_argument("--allow-unmaterialized", action="store_true")
    parser.add_argument("--continue-matrix", action=argparse.BooleanOptionalAction, default=True,
                        help="Continue existing Mode A in the same controller after executable full runs finish")
    parser.add_argument("--dry-reconcile", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    out_root = (project_root / args.out_root).resolve()
    model_dir = (project_root / args.model_dir).resolve()
    graded_root = (project_root / args.graded_root).resolve()
    cleaned_root = (project_root / args.cleaned_root).resolve()
    stages = tuple(int(x.strip()) for x in args.stages.split(",") if x.strip())
    max_runs_opt = args.max_runs if args.max_runs > 0 else None

    if args.mode == "continuous_full_coverage":
        from router_data.batch_prep import prepare_full_coverage_manifest

        manifest_default = out_root / "full_coverage_manifest.json"
        manifest_path = (project_root / args.manifest).resolve() if args.manifest else manifest_default
        if not manifest_path.is_file():
            prepare_full_coverage_manifest(str(graded_root), str(out_root))

        if args.dry_reconcile:
            manifest = json.loads(manifest_path.read_text(encoding="utf8"))
            state_path = out_root / "queue_state.json"
            q_state = json.loads(state_path.read_text(encoding="utf8")) if state_path.is_file() else {}
            ordered, rec = build_ordered_full_coverage_queue(out_root, manifest, q_state, stages=stages)
            print(json.dumps({
                "mode": "continuous_full_coverage",
                "reconciliation": rec,
                "next_queue": [{"run_id": x["run_id"], "stage": x["_stage"], "category": x.get("category"), "layers": x.get("layers"), "sup": x.get("supervision_classes")} for x in ordered],
            }, ensure_ascii=False, indent=2))
            return

        res = run_continuous_full_coverage_queue(
            project_root=project_root,
            out_root=out_root,
            manifest_path=manifest_path,
            model_dir=model_dir,
            graded_root=graded_root,
            cleaned_root=cleaned_root,
            epochs=args.epochs,
            chunk_size=args.chunk_size,
            active_budget_gib=args.active_budget_gib,
            stages=stages,
            sync_github_every=args.sync_github_every,
            max_runs=max_runs_opt,
            continue_matrix=args.continue_matrix,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))

    else:
        # Mode A: Configuration Exploration (legacy 1092-matrix queue)
        manifest_default = out_root / "experiment_matrix.json"
        manifest_path = (project_root / args.manifest).resolve() if args.manifest else manifest_default

        if args.dry_reconcile:
            manifest = json.loads(manifest_path.read_text(encoding="utf8")) if manifest_path.is_file() else {}
            state_path = out_root / "queue_state.json"
            q_state = json.loads(state_path.read_text(encoding="utf8")) if state_path.is_file() else {}
            ordered, rec = build_ordered_queue(out_root, manifest, q_state, stages=stages)
            print(json.dumps({
                "mode": "config_exploration",
                "reconciliation": rec,
                "next_20_in_queue": [
                    {"run_id": x["run_id"], "stage": x["_stage"], "batch_id": x.get("batch_id"), "combo_id": x.get("combo_id"), "groups": x.get("groups")}
                    for x in ordered[:20]
                ],
                "skipped_identical_count": len(q_state.get("skipped_runs") or {}),
            }, ensure_ascii=False, indent=2))
            return

        res = run_queue(
            project_root=project_root,
            out_root=out_root,
            manifest_path=manifest_path,
            model_dir=model_dir,
            max_runs=args.max_runs if args.max_runs > 0 else 10,
            epochs=args.epochs,
            active_budget_gib=args.active_budget_gib,
            stages=stages,
            sync_github_every=args.sync_github_every,
            allow_unmaterialized=args.allow_unmaterialized,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
