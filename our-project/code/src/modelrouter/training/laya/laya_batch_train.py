"""Laya training command-line entry point and compatibility API."""
import argparse
import json
import sys
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
_SRC_ROOT = str(Path(__file__).resolve().parents[3])
for _path in (_WORKSPACE_ROOT, _SRC_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from modelrouter.training.common.checkpoint_retention import *
from modelrouter.training.laya.runner_support import (
    _save_ckpt_with_optim, compute_baseline_0, run_baseline,
    resolve_checkpoint_to_resume,
)
from modelrouter.training.laya.batch_runs import run_experiment, run_sweep_experiment
from modelrouter.training.laya.streaming_run import run_full_coverage_stream_run

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-root', default='runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1/batch_preparation/batch1')
    parser.add_argument('--model-dir', default='models/laya-421m')
    parser.add_argument('--out-root', default='runs/OVERNIGHT-LAYA-TRAINING')
    parser.add_argument('--run', choices=['R0', 'R1', 'R2', 'R3'], default='R0')
    parser.add_argument('--sweep-run', default='')
    parser.add_argument('--full-coverage-run', default='')
    parser.add_argument('--chunk-size', type=int, default=8192)
    parser.add_argument('--graded-root', default='runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1')
    parser.add_argument('--cleaned-root', default='data/公开数据/清洗数据')
    parser.add_argument('--sweep-manifest', default='')
    parser.add_argument('--sweep-data-root', default='')
    parser.add_argument('--parent-checkpoint', default='')
    parser.add_argument('--epochs', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--active-budget-gib', type=float, default=120.0)
    parser.add_argument('--s2-audit-passed', action='store_true')
    parser.add_argument('--regenerate-parent', action='store_true', help='Force regeneration of missing physical parent checkpoint')
    parser.add_argument('--pinned-checkpoints', default='')
    parser.add_argument('--compute-baseline0', action='store_true')
    parser.add_argument('--sync-dashboard', action='store_true')
    parser.add_argument('--project-root', default='.')
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    sys.path.insert(0, str(project_root / 'external' / 'laya'))

    if args.sync_dashboard:
        result = sync_server_metadata_and_build_dashboard(project_root=project_root, run_official_load=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    budget_bytes = int(args.active_budget_gib * GIB)
    pinned = [x.strip() for x in args.pinned_checkpoints.split(',') if x.strip()]

    import laya.train as train_mod  # noqa: F401
    if args.compute_baseline0:
        val_root = args.sweep_data_root or args.out_root
        result = compute_baseline_0(val_root, args.model_dir, args.out_root, seed=args.seed)
        print(json.dumps({k: v for k, v in result.items() if k not in ('s1_item_losses', 's1_item_correct')}, ensure_ascii=False, indent=2))
        return

    if args.full_coverage_run:
        result = run_full_coverage_stream_run(
            run_id=args.full_coverage_run,
            manifest_path=args.sweep_manifest,
            model_dir=args.model_dir,
            out_root=args.out_root,
            graded_root=args.graded_root,
            cleaned_root=args.cleaned_root,
            epochs=args.epochs,
            chunk_size=args.chunk_size,
            active_budget_bytes=budget_bytes,
            s2_audit_passed=args.s2_audit_passed,
            explicit_pinned=pinned,
            project_root=str(project_root),
            regenerate_parent=args.regenerate_parent,
        )
        try:
            sys.path.insert(0, str(project_root / 'our-project/code/src'))
            from modelrouter.v9.training.continuation import continue_laya
            continuation = continue_laya(
                project_root=project_root, out_root=args.out_root, completed_run_id=args.full_coverage_run,
                epochs=2, active_budget_gib=args.active_budget_gib, trainer=run_sweep_experiment)
            if continuation is not None:
                result['v9_continuation'] = continuation
                print(json.dumps({'event': 'v9_continuation_boundary', **continuation}, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({'event': 'v9_continuation_unavailable', 'run_id': args.full_coverage_run,
                              'error_type': type(exc).__name__, 'error': str(exc)}, ensure_ascii=False), flush=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.sweep_run:
        result = run_sweep_experiment(
            args.sweep_run, args.sweep_manifest,
            args.model_dir, args.out_root,
            args.sweep_data_root or None, args.epochs,
            active_budget_bytes=budget_bytes,
            s2_audit_passed=args.s2_audit_passed,
            explicit_pinned=pinned,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.run == 'R0':
        print(json.dumps(run_baseline(args.batch_root, args.model_dir, args.out_root, args.seed), ensure_ascii=False, indent=2))
    else:
        result = run_experiment(
            args.run, args.batch_root, args.model_dir,
            args.out_root, args.parent_checkpoint or None, args.epochs, args.seed,
            active_budget_bytes=budget_bytes,
            s2_audit_passed=args.s2_audit_passed,
            explicit_pinned=pinned,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
