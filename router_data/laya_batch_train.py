"""Small overnight runner around the official Laya training functions with intelligent checkpoint retention and disk budget guard."""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

try:
    from router_data.checkpoint_retention import (
        DEFAULT_ACTIVE_BUDGET_BYTES,
        GIB,
        LEGACY_PROTOCOL_VERSION,
        NEW_PROTOCOL_VERSION,
        STATUS_LEGACY_METADATA_ONLY,
        STATUS_METADATA_ONLY,
        STATUS_PINNED_PARENT,
        STATUS_PRUNED_DUPLICATE,
        STATUS_PRUNED_LOW_SCORE,
        STATUS_RETAINED_BEST,
        STATUS_RETAINED_TOP_K,
        STATUS_TEMP_RECOVERY,
        CheckpointRetentionManager,
        DiskBudgetExceededError,
        classification_metrics_from_records,
        enrich_s3_target_metrics,
        has_physical_weights,
        is_loadable_checkpoint_path,
        physical_dir_bytes,
        run_storage_policy_verification,
        sanitize_command_str,
        sync_server_metadata_and_build_dashboard,
    )
except ImportError:
    from checkpoint_retention import (
        DEFAULT_ACTIVE_BUDGET_BYTES,
        GIB,
        LEGACY_PROTOCOL_VERSION,
        NEW_PROTOCOL_VERSION,
        STATUS_LEGACY_METADATA_ONLY,
        STATUS_METADATA_ONLY,
        STATUS_PINNED_PARENT,
        STATUS_PRUNED_DUPLICATE,
        STATUS_PRUNED_LOW_SCORE,
        STATUS_RETAINED_BEST,
        STATUS_RETAINED_TOP_K,
        STATUS_TEMP_RECOVERY,
        CheckpointRetentionManager,
        DiskBudgetExceededError,
        classification_metrics_from_records,
        enrich_s3_target_metrics,
        has_physical_weights,
        is_loadable_checkpoint_path,
        physical_dir_bytes,
        run_storage_policy_verification,
        sanitize_command_str,
        sync_server_metadata_and_build_dashboard,
    )


class StopRun(Exception):
    pass


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')
    tmp.replace(path)


def _load_items(path, tok, train_mod, max_len, head_max_len):
    rows = train_mod.read_data(str(path))
    items, skipped = train_mod.items_from_rows(tok, rows, max_len=max_len, head_max_len=head_max_len)
    return items, {'rows': len(rows), 'items': len(items), 'skipped': skipped}


def _evaluate_records_list(records, train_mod, return_item_vectors=False):
    if not records:
        return {
            'items': 0, 'loss': None, 'accuracy': None, 'ece': None, 'brier': None,
            'balanced_accuracy': None, 'macro_f1': None, 'by_type': {},
        }
    res = train_mod.evaluate_records(records, [1.0, 1.0, 1.0], None)
    cls_metrics = classification_metrics_from_records(records, return_item_vectors=return_item_vectors)
    res.update(cls_metrics)
    return res


def _evaluate(model, tok, items, dev, train_mod, cfg, max_len, head_max_len, return_records=False, return_item_vectors=False):
    if not items:
        empty = {
            'items': 0, 'loss': None, 'accuracy': None, 'ece': None, 'brier': None,
            'balanced_accuracy': None, 'macro_f1': None, 'by_type': {},
        }
        return (empty, []) if return_records else empty
    records = train_mod.calibration_records(model, tok, items, dev, max_len, head_max_len)
    res = _evaluate_records_list(records, train_mod, return_item_vectors=return_item_vectors)
    return (res, records) if return_records else res


def _slice_records_by_key(rows, records, key_fn, train_mod):
    if len(rows) != len(records):
        return None
    buckets = {}
    for row, rec in zip(rows, records):
        buckets.setdefault(key_fn(row), []).append(rec)
    out = {}
    for k, rec_list in sorted(buckets.items()):
        ev = _evaluate_records_list(rec_list, train_mod, return_item_vectors=False)
        ev['skipped'] = {}
        out[k] = ev
    return out


def _groups(model, tok, val_groups, dev, train_mod, cfg, max_len, head_max_len, val_rows=None, return_s1_vectors=False):
    result = {}
    all_records = []
    records_by_group = {}
    for name, items in val_groups.items():
        want_vec = bool(return_s1_vectors and name == 'S1')
        ev, recs = _evaluate(model, tok, items, dev, train_mod, cfg, max_len, head_max_len,
                             return_records=True, return_item_vectors=want_vec)
        result[name] = ev
        records_by_group[name] = recs
        all_records.extend(recs)
    result['all'] = _evaluate_records_list(all_records, train_mod, return_item_vectors=False)

    if val_rows:
        if 'S1' in val_rows and 'S1' in records_by_group:
            s1_src = _slice_records_by_key(
                val_rows['S1'],
                records_by_group['S1'],
                lambda r: (r.get('provenance') or {}).get('source_id', 'unknown'),
                train_mod,
            )
            if s1_src is not None:
                result['S1_by_source'] = s1_src
        if 'S3' in val_rows and 'S3' in records_by_group:
            s3_tgt = _slice_records_by_key(
                val_rows['S3'],
                records_by_group['S3'],
                lambda r: '%s:%s' % ((r.get('provenance') or {}).get('source_id', 'unknown'),
                                     next(iter((r.get('questions') or {}).keys()), '')),
                train_mod,
            )
            if s3_tgt is not None:
                result['S3_by_source_target'] = enrich_s3_target_metrics(s3_tgt)
    return result


def compute_baseline_0(val_root, model_dir, out_root, seed=42, max_len=1024, head_max_len=512):
    """Evaluate un-finetuned Laya-421M on fixed new-protocol validation sets and freeze `baseline_0.json`."""
    import torch
    from laya.train import items_from_rows, load_checkpoint, read_data

    train_mod = sys.modules['laya.train']
    model, tok, cfg = load_checkpoint(model_dir)
    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(dev)

    val_dir = Path(val_root)
    if (val_dir / 'val').is_dir():
        val_dir = val_dir / 'val'

    val_groups = {}
    val_rows = {}
    skipped_map = {}
    for name in ('S1', 'S2', 'S3'):
        p = val_dir / f'{name}.jsonl'
        if not p.is_file():
            matches = sorted(Path(val_root).glob(f'data/*/val/{name}.jsonl'))
            if matches:
                p = matches[0]
        if not p.is_file():
            continue
        rows = read_data(str(p))
        items, skipped = items_from_rows(tok, rows, max_len=max_len, head_max_len=head_max_len)
        val_rows[name] = rows
        val_groups[name] = items
        skipped_map[name] = skipped

    metrics = _groups(
        model, tok, val_groups, dev, train_mod, cfg, max_len, head_max_len,
        val_rows=val_rows, return_s1_vectors=True,
    )
    s1_ev = dict(metrics.get('S1') or {})
    s1_losses = s1_ev.pop('item_losses', [])
    s1_correct = s1_ev.pop('item_correct', [])
    s2_ev = dict(metrics.get('S2') or {})
    s3_ev = dict(metrics.get('S3') or {})
    s1_by_src = dict(metrics.get('S1_by_source') or {})
    s3_by_tgt = dict(metrics.get('S3_by_source_target') or {})
    s1_ev['by_source'] = s1_by_src
    s3_ev['by_source_target'] = s3_by_tgt

    payload = {
        'baseline_id': 'BASELINE_0_LAYA_421M_FROZEN',
        'computed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'protocol_version': NEW_PROTOCOL_VERSION,
        'model_name': 'Laya-421M (un-finetuned base)',
        'frozen': True,
        'composite_scores': {'S1_score': 100.0, 'S2_score': 100.0, 'S3_score': 100.0},
        'validation': {
            'S1': s1_ev,
            'S1_by_source': s1_by_src,
            'S2': s2_ev,
            'S3': s3_ev,
            'S3_by_source_target': s3_by_tgt,
        },
        'S1': s1_ev,
        'S1_by_source': s1_by_src,
        'S2': s2_ev,
        'S3': s3_ev,
        'S3_by_source_target': s3_by_tgt,
        'skipped': skipped_map,
        's1_item_losses': s1_losses,
        's1_item_correct': s1_correct,
    }
    out_path = Path(out_root) / 'baseline_0.json'
    _write(out_path, payload)
    _write(Path(out_root) / 'R0' / 'run.json', {
        'run_id': 'R0',
        'status': 'completed',
        'protocol_version': NEW_PROTOCOL_VERSION,
        'seed': seed,
        'validation': {
            'S1': s1_ev,
            'S1_by_source': payload['S1_by_source'],
            'S2': s2_ev,
            'S3': s3_ev,
            'S3_by_source_target': payload['S3_by_source_target'],
        },
        'data': {k: len(v) for k, v in val_rows.items()},
    })
    return payload


def run_baseline(batch_root, model_dir, out_root, seed=42, max_len=1024, head_max_len=512):
    return compute_baseline_0(batch_root, model_dir, out_root, seed=seed, max_len=max_len, head_max_len=head_max_len)


def _load_run_files(batch_root, run, tok, train_mod, max_len, head_max_len):
    names = {'R1': ['S1'], 'R2': ['S1', 'S2'], 'R3': ['S1', 'S2', 'S3']}[run]
    train_groups, val_groups, load = {}, {}, {}
    for name in names:
        train_groups[name], load['train_' + name] = _load_items(Path(batch_root) / 'train' / (name + '.jsonl'), tok, train_mod, max_len, head_max_len)
        val_groups[name], load['val_' + name] = _load_items(Path(batch_root) / 'val' / (name + '.jsonl'), tok, train_mod, max_len, head_max_len)
    return train_groups, val_groups, load


def run_experiment(run, batch_root, model_dir, out_root, parent_checkpoint=None,
                   epochs=4, seed=42, max_len=1024, head_max_len=512,
                   active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
                   s2_audit_passed=False, explicit_pinned=()):
    import torch
    from laya.train import (TrainConfig, load_checkpoint, optimizer_updates,
                            save_checkpoint, train_model)

    retention_mgr = CheckpointRetentionManager(
        out_root=Path(out_root),
        active_budget_bytes=active_budget_bytes,
        s2_audit_passed=s2_audit_passed,
        explicit_pinned=explicit_pinned,
    )
    pre_check = retention_mgr.pre_run_disk_check(run_id=run)

    run_root = Path(out_root) / run
    run_root.mkdir(parents=True, exist_ok=True)
    model, tok, cfg = load_checkpoint(model_dir)
    dev = torch.device('cuda')
    model.to(dev)
    train_groups, val_groups, load = _load_run_files(batch_root, run, tok, sys.modules['laya.train'], max_len, head_max_len)
    train_items = [it for name in train_groups for it in train_groups[name]]
    parent_metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len)

    config = TrainConfig(
        epochs=epochs, micro_batch=8, grad_accum=8,
        encoder_lr=2.5e-5, head_lr=1e-4, min_lr=1e-6,
        weight_decay=0.01, grad_clip=1.0, loss='soft-ce',
        shuffle_options=('choice',), seed=seed, calib_seed=seed,
        max_len=max_len, head_max_len=head_max_len,
        amp=True, gradient_checkpointing=True, log_every=100,
    )
    config.validate()
    updates_per_epoch = optimizer_updates(len(train_items), config.micro_batch, config.grad_accum, 1)
    run_meta = {
        'run_id': run, 'parent_checkpoint_id': parent_checkpoint,
        'base_model': model_dir, 'seed': seed, 'epochs_max': epochs,
        'protocol_version': NEW_PROTOCOL_VERSION, 'legacy_input_protocol': False,
        'supervision_classes': sorted(train_groups.keys()),
        'train_groups': {k: len(v) for k, v in train_groups.items()},
        'val_groups': {k: len(v) for k, v in val_groups.items()},
        'loaded': load, 'config': vars(config),
        'max_len': max_len, 'head_max_len': head_max_len,
        'optimizer_updates_per_epoch': updates_per_epoch,
        'status': 'running', 'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'parent_metrics': parent_metrics,
        'pre_run_disk_check': pre_check,
        'code_commit': os.environ.get('MODELROUTER_CODE_COMMIT', 'unknown'),
    }
    _write(run_root / 'run.json', run_meta)
    history = []
    best_loss = float('inf')
    best_epoch = None
    no_improve = 0
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    def on_epoch_end(epoch, train_loss):
        nonlocal best_loss, best_epoch, no_improve
        started = time.time()
        metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len)
        s1_loss = metrics.get('S1', {}).get('loss')
        ckcfg = dict(cfg, max_len=max_len, head_max_len=head_max_len,
                     training_run={'run_id': run, 'epoch': epoch + 1,
                                   'parent_checkpoint_id': parent_checkpoint,
                                   'config': vars(config)})
        epoch_id = f'{run}-e{epoch + 1:02d}'
        improved = s1_loss is not None and (best_epoch is None or s1_loss < best_loss * 0.995)
        if improved:
            best_loss, best_epoch, no_improve = s1_loss, epoch + 1, 0
        else:
            no_improve += 1
        entry = {
            'checkpoint_id': epoch_id, 'epoch': epoch + 1, 'train_loss': train_loss,
            'validation': metrics, 'improved_0_5pct': improved,
            'best_epoch': best_epoch,
            'optimizer_updates': updates_per_epoch,
            'global_step': (epoch + 1) * updates_per_epoch,
            'learning_rate': {'encoder': config.encoder_lr, 'head': config.head_lr},
            'epoch_seconds': round(time.time() - started, 3),
            'gpu_memory_peak_mib': round(torch.cuda.max_memory_allocated() / 1048576, 2) if torch.cuda.is_available() else None,
        }
        history.append(entry)
        run_meta['history'] = history
        run_meta['best_epoch'] = best_epoch
        will_early_stop = bool(s1_loss is not None and epoch + 1 >= 2 and no_improve >= 2)
        is_final = (epoch + 1 >= epochs) or will_early_stop
        retention_mgr.handle_epoch_checkpoint(
            run_id=run,
            epoch=epoch + 1,
            is_final_epoch=is_final,
            save_fn=lambda target_dir: save_checkpoint(model, tok, ckcfg, target_dir),
            run_meta=run_meta,
            entry=entry,
        )
        if will_early_stop:
            raise StopRun('two epochs without 0.5% S1 validation-loss improvement')

    status = 'completed'
    try:
        train_model(model, tok, train_items, config, dev, max_len, head_max_len, on_epoch_end=on_epoch_end)
    except StopRun as exc:
        status = 'early_stopped'
        run_meta['stop_reason'] = str(exc)
    except Exception as exc:
        status = 'failed'
        run_meta['error'] = repr(exc)
        run_meta['status'] = status
        run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        run_meta['history'] = history
        retention_mgr.finalize_run_checkpoints(run, run_meta)
        raise
    run_meta['status'] = status
    run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    run_meta['history'] = history
    run_meta['best_epoch'] = best_epoch
    retention_mgr.finalize_run_checkpoints(run, run_meta)
    return run_meta


def _load_named_groups(data_root, group_names, tok, train_mod, max_len, head_max_len):
    train_groups, val_groups, load, val_rows = {}, {}, {}, {}
    for name in group_names:
        train_path = Path(data_root) / 'train' / (name + '.jsonl')
        val_path = Path(data_root) / 'val' / (name + '.jsonl')
        train_groups[name], load['train_' + name] = _load_items(train_path, tok, train_mod, max_len, head_max_len)
        val_groups[name], load['val_' + name] = _load_items(val_path, tok, train_mod, max_len, head_max_len)
        val_rows[name] = train_mod.read_data(str(val_path))
    return train_groups, val_groups, load, val_rows


def _s3_validation_breakdown(model, tok, rows, dev, train_mod, cfg, max_len, head_max_len):
    buckets = {}
    for row in rows:
        p = row.get('provenance', {})
        qid = next(iter(row.get('questions', {})), '')
        key = '%s:%s' % (p.get('source_id', 'unknown'), qid)
        buckets.setdefault(key, []).append(row)
    result = {}
    for key, bucket in sorted(buckets.items()):
        items, skipped = train_mod.items_from_rows(tok, bucket, max_len=max_len, head_max_len=head_max_len)
        result[key] = _evaluate(model, tok, items, dev, train_mod, cfg, max_len, head_max_len)
        result[key]['skipped'] = skipped
    return enrich_s3_target_metrics(result)


def _sweep_public_run(run_id, run_root, meta, history, manifest, out_root):
    """Build the small public dashboard payload without server paths or row text."""
    root = Path(out_root)
    retention_mgr = CheckpointRetentionManager(out_root=root)
    ckpt_manifest = retention_mgr.write_checkpoint_manifest(manifest=manifest)
    node_by_id = {n['checkpoint_id']: n for n in ckpt_manifest.get('checkpoints', [])}

    runs = {}
    for path in sorted(root.glob('*/run.json')):
        try:
            saved = json.loads(path.read_text(encoding='utf8'))
        except (OSError, json.JSONDecodeError):
            continue
        public = {k: saved.get(k) for k in (
            'run_id', 'status', 'parent_checkpoint_id', 'seed', 'epochs_max',
            'train_groups', 'val_groups', 'config', 'best_epoch', 'stop_reason',
            'started_at', 'finished_at', 'current_epoch', 'continuation_mode',
            'optimizer_updates_per_epoch', 'data_dir_label', 'train_origin',
            'batch_id', 'combo_id', 'quality_code', 'sampling_code', 'layers',
            'supervision_classes', 'ratios', 'counts', 'independent_units',
            'eligibility_reason', 'audit_flags', 'current_step', 'command',
            'protocol_version', 'legacy_input_protocol', 'best_checkpoint',
        ) if k in saved}
        if 'command' in public:
            public['command'] = sanitize_command_str(public['command'])
        pub_hist = []
        for entry in saved.get('history', []):
            cid = entry.get('checkpoint_id')
            node = node_by_id.get(cid, {})
            item = dict(entry)
            item['weights_saved'] = bool(node.get('weights_saved', False))
            item['loadable'] = bool(node.get('loadable', False))
            item['retention_status'] = node.get('retention_status', STATUS_METADATA_ONLY)
            item['retention_reason'] = node.get('retention_reason', '')
            item['retention_reasons'] = node.get('retention_reasons', [])
            item['actual_weight_bytes'] = int(node.get('actual_weight_bytes', 0))
            item['freed_bytes'] = int(node.get('freed_bytes', entry.get('freed_bytes', 0)))
            pub_hist.append(item)
        public['history'] = pub_hist
        public['checkpoint_root'] = '%s/checkpoints' % path.parent.name
        runs[path.parent.name] = public

    plan_data = manifest.get('plan_data', {})
    plans = manifest.get('plans', {})
    all_nodes = ckpt_manifest.get('checkpoints', [])
    best_loss = None
    best_id = None
    best_acc = None
    best_acc_id = None
    saved_weight_count = 0
    for name in runs:
        ckroot = root / name / 'checkpoints'
        if ckroot.exists():
            saved_weight_count += sum(
                1 for p in ckroot.iterdir()
                if p.is_dir() and not p.is_symlink() and has_physical_weights(p)
            )
    for node in all_nodes:
        if node.get('legacy_input_protocol'):
            continue
        s1 = node.get('validation', {}).get('S1', {})
        loss = s1.get('loss')
        acc = s1.get('accuracy')
        if isinstance(loss, (int, float)) and (best_loss is None or loss < best_loss):
            best_loss, best_id = loss, node.get('checkpoint_id')
        if isinstance(acc, (int, float)) and (best_acc is None or acc > best_acc):
            best_acc, best_acc_id = acc, node.get('checkpoint_id')

    starts = [r.get('started_at') for r in runs.values() if r.get('started_at')]
    current = next((name for name, r in runs.items() if r.get('status') == 'running'), None)
    current_epoch = runs.get(current, {}).get('current_epoch') if current else None
    generation = manifest.get('generation', {})
    if isinstance(generation, dict) and isinstance(generation.get('code_sha256'), dict):
        generation = dict(generation)
        generation['code_sha256'] = {
            ('prepare_router_data.py' if str(path).endswith('/prepare_router_data.py')
             else 'router_data/batch_prep.py' if str(path).endswith('/batch_prep.py')
             else Path(str(path)).name): digest
            for path, digest in generation['code_sha256'].items()
        }
    plan_status = Counter((p.get('status') or 'PLANNED') for p in plans.values())
    ret_summary = ckpt_manifest.get('retention_summary', {})
    payload = {
        'experiment_id': manifest.get('experiment_id', 'OVERNIGHT-LAYA-SWEEP-02'),
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'code_commit': os.environ.get('MODELROUTER_CODE_COMMIT', 'unknown'),
        'status': 'running' if current else ('completed' if runs else 'prepared'),
        'overview': {
            'completed_runs': sum(r.get('status') in {'completed', 'early_stopped'} for r in runs.values()),
            'planned_runs': len(plans),
            'eligible_runs': plan_status.get('ELIGIBLE', 0) + plan_status.get('CPU_MATERIALIZED', 0),
            'blocked_runs': plan_status.get('BLOCKED', 0),
            'skipped_runs': plan_status.get('SKIPPED', 0),
            'checkpoint_total': len(all_nodes),
            'saved_weight_count': saved_weight_count,
            'metadata_only_count': ret_summary.get('status_counts', {}).get(STATUS_METADATA_ONLY, 0)
                                   + ret_summary.get('status_counts', {}).get(STATUS_LEGACY_METADATA_ONLY, 0),
            'pruned_low_score_count': ret_summary.get('status_counts', {}).get(STATUS_PRUNED_LOW_SCORE, 0),
            'pinned_parent_count': len(ret_summary.get('pinned_parent_ids', {})),
            'freed_space_bytes': ret_summary.get('total_freed_bytes', 0),
            'current_run': current,
            'current_epoch': current_epoch,
            'current_step': runs.get(current, {}).get('current_step') if current else None,
            'best_s1_loss_checkpoint': best_id,
            'best_s1_loss': best_loss,
            'best_s1_accuracy_checkpoint': best_acc_id,
            'best_s1_accuracy': best_acc,
            'started_at': min(starts) if starts else None,
            'latest_sync_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'github_sync': 'pending_local_sync',
        },
        'plans': plans,
        'plan_data': plan_data,
        'matrix': manifest.get('aggregate', {}),
        'coverage': manifest.get('coverage', {}),
        'runs': runs,
        'checkpoint_tree': all_nodes,
        'comparable_groups': ckpt_manifest.get('comparable_groups', {}),
        'disk_status': ckpt_manifest.get('disk_status', {}),
        'retention_summary': ret_summary,
        'fixed_validation': manifest.get('fixed_validation', {}),
        'audit': manifest.get('audit', {}),
        'generation': generation,
    }
    _write(Path(out_root) / 'dashboard_data.json', payload)
    return payload


def run_sweep_experiment(run_id, manifest_path, model_dir, out_root, data_root=None,
                         epochs=3, max_len=1024, head_max_len=512,
                         active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
                         s2_audit_passed=False, explicit_pinned=()):
    """Run one Sweep / FULL-GRADED plan with selective checkpoint retention and disk guard."""
    import torch
    from laya.train import (TrainConfig, load_checkpoint, optimizer_updates,
                            save_checkpoint, train_model)

    manifest = json.loads(Path(manifest_path).read_text(encoding='utf8'))
    spec = manifest['plans'][run_id]
    if not spec.get('data'):
        raise ValueError('%s has no materialized data plan' % run_id)
    root = Path(data_root or manifest.get('output_root', '')).resolve()
    data_dir = root / spec['data']
    run_root = Path(out_root) / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    existing_path = run_root / 'run.json'
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding='utf8'))
            if existing.get('status') in {'completed', 'early_stopped'}:
                return {'run_id': run_id, 'status': 'skipped_existing', 'existing_status': existing.get('status')}
        except json.JSONDecodeError:
            pass

    retention_mgr = CheckpointRetentionManager(
        out_root=Path(out_root),
        active_budget_bytes=active_budget_bytes,
        s2_audit_passed=s2_audit_passed,
        explicit_pinned=explicit_pinned,
    )
    # P3: Perform pre-run disk and active weight budget check before loading GPU model
    pre_check = retention_mgr.pre_run_disk_check(run_id=run_id, manifest=manifest)

    model_path = str(spec.get('model_dir') or model_dir)
    parent_id = spec.get('parent_checkpoint_id')
    if spec.get('parent_model_dir'):
        model_path = str(spec['parent_model_dir'])
    model, tok, cfg = load_checkpoint(model_path)
    dev = torch.device('cuda')
    model.to(dev)
    group_names = list(spec.get('groups') or [])
    train_groups, val_groups, load, val_rows = _load_named_groups(
        data_dir, group_names, tok, sys.modules['laya.train'], max_len, head_max_len)
    train_items = [item for name in group_names for item in train_groups[name]]
    parent_metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len, val_rows=val_rows)

    config = TrainConfig(
        epochs=epochs, micro_batch=8, grad_accum=8,
        encoder_lr=float(spec.get('encoder_lr', 2.5e-5)),
        head_lr=float(spec.get('head_lr', 1e-4)), min_lr=1e-6,
        weight_decay=0.01, grad_clip=1.0, loss='soft-ce',
        shuffle_options=('choice',), seed=int(spec.get('seed', 42)), calib_seed=int(spec.get('seed', 42)),
        max_len=max_len, head_max_len=head_max_len,
        amp=True, gradient_checkpointing=True, freeze_encoder=bool(spec.get('freeze_encoder', False)),
        calib_frac=0.0, log_every=100,
    )
    config.validate()
    updates_per_epoch = optimizer_updates(len(train_items), config.micro_batch, config.grad_accum, 1)
    protocol_version = spec.get('protocol_version') or manifest.get('protocol_version') or NEW_PROTOCOL_VERSION
    legacy_flag = bool(spec.get('legacy_input_protocol', False))
    run_meta = {
        'run_id': run_id, 'base_run_id': spec.get('base_run_id') or (run_id[3:] if run_id.startswith('P0_') else run_id),
        'parent_checkpoint_id': parent_id,
        'base_model': sanitize_command_str(model_path), 'data_dir_label': spec['data'],
        'train_origin': spec.get('train_origin', 'Base'),
        'protocol_version': protocol_version,
        'legacy_input_protocol': legacy_flag,
        'seed': config.seed, 'epochs_max': epochs,
        'train_groups': {k: len(v) for k, v in train_groups.items()},
        'val_groups': {k: len(v) for k, v in val_groups.items()},
        'loaded': load, 'config': vars(config),
        'max_len': max_len, 'head_max_len': head_max_len,
        'status': 'running', 'current_epoch': 0,
        'continuation_mode': 'weight_only' if parent_id else 'base_initialization',
        'optimizer_updates_per_epoch': updates_per_epoch,
        'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'parent_metrics': parent_metrics,
        'pre_run_disk_check': pre_check,
        'audit_flags': {
            's2_100pct_not_generalization': not s2_audit_passed,
            's2_audit_passed': bool(s2_audit_passed),
            'validation_is_fixed': True,
            'test_used': False,
            'route_001_002_training': False,
        },
        'batch_id': spec.get('batch_id'), 'combo_id': spec.get('combo_id'),
        'quality_code': spec.get('quality_code'), 'sampling_code': spec.get('sampling_code'),
        'layers': spec.get('layers'), 'supervision_classes': spec.get('supervision_classes', group_names),
        'ratios': spec.get('ratios'), 'counts': spec.get('counts'),
        'independent_units': spec.get('independent_units'),
        'eligibility_reason': spec.get('eligibility_reason'),
        'command': sanitize_command_str(
            'python router_data/laya_batch_train.py --sweep-run %s --sweep-manifest %s --out-root %s --epochs %s'
            % (run_id, manifest_path, out_root, epochs)
        ),
        'code_commit': os.environ.get('MODELROUTER_CODE_COMMIT', 'unknown'),
        'current_step': 0,
    }
    _write(run_root / 'run.json', run_meta)
    history = []
    best_loss = float('inf')
    best_epoch = None
    no_improve = 0
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    epoch_train_started = time.time()

    def on_epoch_end(epoch, train_loss):
        nonlocal best_loss, best_epoch, no_improve, epoch_train_started
        epoch_boundary = time.time()
        train_seconds = epoch_boundary - epoch_train_started
        validation_started = time.time()
        metrics = _groups(
            model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len,
            val_rows=val_rows, return_s1_vectors=True,
        )
        s1_vec_losses = (metrics.get('S1') or {}).pop('item_losses', None)
        s1_vec_correct = (metrics.get('S1') or {}).pop('item_correct', None)
        validation_seconds = time.time() - validation_started
        s1_loss = metrics.get('S1', {}).get('loss')
        ckcfg = dict(cfg, max_len=max_len, head_max_len=head_max_len,
                     training_run={'run_id': run_id, 'epoch': epoch + 1,
                                   'parent_checkpoint_id': parent_id,
                                   'protocol_version': protocol_version,
                                   'config': vars(config),
                                   'continuation_mode': run_meta['continuation_mode']})
        epoch_id = f'{run_id}-e{epoch + 1:02d}'
        improved = s1_loss is not None and (best_epoch is None or s1_loss < best_loss * 0.995)
        if improved:
            best_loss, best_epoch, no_improve = s1_loss, epoch + 1, 0
        elif s1_loss is not None:
            no_improve += 1
        elif best_epoch is None:
            best_epoch = epoch + 1

        if (improved or epoch == 0) and s1_vec_losses is not None and s1_vec_correct is not None:
            _write(run_root / 's1_val_vectors.json', {
                'run_id': run_id,
                'checkpoint_id': epoch_id,
                'epoch': epoch + 1,
                'items': len(s1_vec_losses),
                'item_losses': s1_vec_losses,
                'item_correct': s1_vec_correct,
            })

        try:
            gpu_util = float(subprocess.check_output(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                text=True, timeout=3).strip().splitlines()[0])
        except Exception:
            gpu_util = None

        checkpoint_started = time.time()
        will_early_stop = bool(s1_loss is not None and epoch + 1 >= 2 and no_improve >= 2)
        is_final = (epoch + 1 >= epochs) or will_early_stop

        entry = {
            'checkpoint_id': epoch_id, 'epoch': epoch + 1, 'train_loss': train_loss,
            'validation': metrics, 'improved_0_5pct': improved,
            'best_epoch': best_epoch,
            'train_seconds': round(train_seconds, 3), 'validation_seconds': round(validation_seconds, 3),
            'checkpoint_seconds': 0.0,
            'epoch_total_seconds': round(train_seconds + validation_seconds, 3),
            'epoch_seconds': round(train_seconds + validation_seconds, 3),
            'optimizer_updates': updates_per_epoch,
            'learning_rate': {'encoder': config.encoder_lr, 'head': config.head_lr},
            'gradient_norm': None,
            'gpu_memory_peak_mib': round(torch.cuda.max_memory_allocated() / 1048576, 2) if torch.cuda.is_available() else None,
            'gpu_utilization_percent': gpu_util,
            'global_step': (epoch + 1) * updates_per_epoch,
        }
        history.append(entry)
        run_meta['history'] = history
        run_meta['current_epoch'] = epoch + 1
        run_meta['current_step'] = (epoch + 1) * updates_per_epoch
        run_meta['best_epoch'] = best_epoch

        ret_result = retention_mgr.handle_epoch_checkpoint(
            run_id=run_id,
            epoch=epoch + 1,
            is_final_epoch=is_final,
            save_fn=lambda target_dir: save_checkpoint(model, tok, ckcfg, target_dir),
            run_meta=run_meta,
            entry=entry,
            manifest=manifest,
        )
        checkpoint_seconds = time.time() - checkpoint_started
        epoch_total_seconds = time.time() - epoch_train_started
        entry['checkpoint_seconds'] = round(checkpoint_seconds, 3)
        entry['epoch_total_seconds'] = round(epoch_total_seconds, 3)
        entry['epoch_seconds'] = round(epoch_total_seconds, 3)
        if run_meta.get('history'):
            run_meta['history'][-1]['checkpoint_seconds'] = entry['checkpoint_seconds']
            run_meta['history'][-1]['epoch_total_seconds'] = entry['epoch_total_seconds']
            run_meta['history'][-1]['epoch_seconds'] = entry['epoch_seconds']

        _write(run_root / 'epoch_metrics.json', run_meta['history'])
        _write(run_root / 'epoch_status.json', {
            'run_id': run_id, 'epoch': epoch + 1,
            'checkpoint_id': epoch_id,
            'weights_saved': bool(entry.get('weights_saved', False)),
            'retention_status': entry.get('retention_status'),
            'retention_reason': entry.get('retention_reason'),
            'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        })
        _write(run_root / 'run.json', run_meta)
        _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root)
        print(json.dumps({
            'event': 'epoch_complete', 'run_id': run_id, 'epoch': epoch + 1,
            'checkpoint_id': epoch_id, 'best_epoch': best_epoch,
            'weights_saved': entry.get('weights_saved'),
            'retention_status': entry.get('retention_status'),
            'retention_reason': entry.get('retention_reason'),
            's1_loss': s1_loss, 's1_accuracy': metrics.get('S1', {}).get('accuracy'),
        }, ensure_ascii=False), flush=True)
        if will_early_stop:
            raise StopRun('two epochs without 0.5% S1 validation-loss improvement')
        epoch_train_started = time.time()

    status = 'completed'
    try:
        train_model(model, tok, train_items, config, dev, max_len, head_max_len, on_epoch_end=on_epoch_end)
    except StopRun as exc:
        status = 'early_stopped'
        run_meta['stop_reason'] = str(exc)
    except Exception as exc:
        status = 'failed'
        run_meta['error'] = repr(exc)
        run_meta['status'] = status
        run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        run_meta['history'] = history
        retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest)
        _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root)
        raise
    run_meta['status'] = status
    run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    run_meta['best_epoch'] = best_epoch
    run_meta['current_epoch'] = len(run_meta['history'])
    retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest)
    _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root)
    print(json.dumps({
        'event': 'run_complete', 'run_id': run_id, 'status': status,
        'best_epoch': best_epoch, 'epochs': len(run_meta['history']),
    }, ensure_ascii=False), flush=True)
    return run_meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-root', default='runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1/batch_preparation/batch1')
    parser.add_argument('--model-dir', default='models/laya-421m')
    parser.add_argument('--out-root', default='runs/OVERNIGHT-LAYA-TRAINING')
    parser.add_argument('--run', choices=['R0', 'R1', 'R2', 'R3'], default='R0')
    parser.add_argument('--sweep-run', default='')
    parser.add_argument('--sweep-manifest', default='')
    parser.add_argument('--sweep-data-root', default='')
    parser.add_argument('--parent-checkpoint', default='')
    parser.add_argument('--epochs', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--active-budget-gib', type=float, default=120.0)
    parser.add_argument('--s2-audit-passed', action='store_true')
    parser.add_argument('--pinned-checkpoints', default='')
    parser.add_argument('--compute-baseline0', action='store_true')
    parser.add_argument('--verify-storage-policy', action='store_true')
    parser.add_argument('--sync-dashboard', action='store_true')
    parser.add_argument('--project-root', default='.')
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    sys.path.insert(0, str(project_root / 'external' / 'laya'))

    if args.verify_storage_policy:
        result = run_storage_policy_verification(project_root=project_root, run_official_load=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

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


if __name__ == '__main__':
    main()
