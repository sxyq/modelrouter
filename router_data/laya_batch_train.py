"""Small overnight runner around the official Laya training functions."""
import argparse
import json
import os
import sys
import time
import subprocess
from collections import Counter
from pathlib import Path


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


def _evaluate(model, tok, items, dev, train_mod, cfg, max_len, head_max_len):
    if not items:
        return {'items': 0, 'loss': None, 'accuracy': None, 'ece': None, 'brier': None, 'by_type': {}}
    records = train_mod.calibration_records(model, tok, items, dev, max_len, head_max_len)
    # Keep validation metrics on the same raw-logit scale for every run. Calibration is
    # recorded separately and never replaces the independent validation set.
    return train_mod.evaluate_records(records, [1.0, 1.0, 1.0], None)


def _groups(model, tok, val_groups, dev, train_mod, cfg, max_len, head_max_len):
    result = {}
    for name, items in val_groups.items():
        result[name] = _evaluate(model, tok, items, dev, train_mod, cfg, max_len, head_max_len)
    all_items = [it for group in val_groups.values() for it in group]
    result['all'] = _evaluate(model, tok, all_items, dev, train_mod, cfg, max_len, head_max_len)
    return result


def _load_run_files(batch_root, run, tok, train_mod, max_len, head_max_len):
    names = {'R1': ['S1'], 'R2': ['S1', 'S2'], 'R3': ['S1', 'S2', 'S3']}[run]
    train_groups, val_groups, load = {}, {}, {}
    for name in names:
        train_groups[name], load['train_' + name] = _load_items(Path(batch_root) / 'train' / (name + '.jsonl'), tok, train_mod, max_len, head_max_len)
        val_groups[name], load['val_' + name] = _load_items(Path(batch_root) / 'val' / (name + '.jsonl'), tok, train_mod, max_len, head_max_len)
    return train_groups, val_groups, load


def run_baseline(batch_root, model_dir, out_root, seed=42, max_len=1024, head_max_len=512):
    import torch
    from laya.train import calibration_records, evaluate_records, load_checkpoint

    model, tok, cfg = load_checkpoint(model_dir)
    dev = torch.device('cuda')
    model.to(dev)
    result = {'run_id': 'R0', 'status': 'completed', 'base_model': model_dir, 'seed': seed,
              'validation': {}, 'data': {}}
    for name in ('S1', 'S2', 'S3'):
        path = Path(batch_root) / 'val' / (name + '.jsonl')
        rows = json.loads('[]')
        with path.open(encoding='utf8') as f:
            rows = [json.loads(line) for line in f if line.strip()]
        result['data'][name] = len(rows)
        from laya.train import items_from_rows
        items, skipped = items_from_rows(tok, rows, max_len=max_len, head_max_len=head_max_len)
        rec = calibration_records(model, tok, items, dev, max_len, head_max_len)
        result['validation'][name] = evaluate_records(rec, [1.0, 1.0, 1.0], None)
        result['validation'][name]['skipped'] = skipped
    _write(Path(out_root) / 'R0' / 'run.json', result)
    return result


def run_experiment(run, batch_root, model_dir, out_root, parent_checkpoint=None,
                   epochs=4, seed=42, max_len=1024, head_max_len=512):
    import torch
    from laya.train import (TrainConfig, calibration_records, evaluate_records,
                            load_checkpoint, save_checkpoint, train_model)

    run_root = Path(out_root) / run
    run_root.mkdir(parents=True, exist_ok=True)
    model, tok, cfg = load_checkpoint(model_dir)
    dev = torch.device('cuda')
    model.to(dev)
    train_groups, val_groups, load = _load_run_files(batch_root, run, tok, sys.modules['laya.train'], max_len, head_max_len)
    train_items = [it for name in train_groups for it in train_groups[name]]
    val_all = [it for name in val_groups for it in val_groups[name]]
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
    run_meta = {
        'run_id': run, 'parent_checkpoint_id': parent_checkpoint,
        'base_model': model_dir, 'seed': seed, 'epochs_max': epochs,
        'train_groups': {k: len(v) for k, v in train_groups.items()},
        'val_groups': {k: len(v) for k, v in val_groups.items()},
        'loaded': load, 'config': vars(config),
        'max_len': max_len, 'head_max_len': head_max_len,
        'status': 'running', 'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'parent_metrics': parent_metrics,
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
        save_checkpoint(model, tok, ckcfg, str(run_root / 'checkpoints' / f'epoch_{epoch + 1:02d}'))
        save_checkpoint(model, tok, ckcfg, str(run_root / 'checkpoints' / 'latest'))
        improved = s1_loss is not None and (best_epoch is None or s1_loss < best_loss * 0.995)
        if improved:
            best_loss, best_epoch, no_improve = s1_loss, epoch + 1, 0
            save_checkpoint(model, tok, ckcfg, str(run_root / 'checkpoints' / 'best'))
        else:
            no_improve += 1
        entry = {
            'checkpoint_id': epoch_id, 'epoch': epoch + 1, 'train_loss': train_loss,
            'validation': metrics, 'improved_0_5pct': improved,
            'best_epoch': best_epoch, 'epoch_seconds': round(time.time() - started, 3),
            'gpu_memory_peak_mib': round(torch.cuda.max_memory_allocated() / 1048576, 2) if torch.cuda.is_available() else None,
        }
        history.append(entry)
        _write(run_root / 'epoch_metrics.json', history)
        if epoch + 1 >= 2 and no_improve >= 2:
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
        _write(run_root / 'run.json', run_meta)
        raise
    run_meta['status'] = status
    run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    run_meta['history'] = history
    run_meta['best_epoch'] = best_epoch
    run_meta['best_checkpoint'] = str(run_root / 'checkpoints' / 'best') if best_epoch else None
    _write(run_root / 'run.json', run_meta)
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
    return result


def _sweep_public_run(run_id, run_root, meta, history, manifest, out_root):
    """Build the small public dashboard payload without server paths or row text."""
    runs = {}
    root = Path(out_root)
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
        ) if k in saved}
        public['history'] = saved.get('history', [])
        public['checkpoint_root'] = '%s/checkpoints' % path.parent.name
        runs[path.parent.name] = public
    plan_data = manifest.get('plan_data', {})
    plans = manifest.get('plans', {})
    all_nodes = []
    best_loss = None
    best_id = None
    best_acc = None
    best_acc_id = None
    saved_weight_count = 0
    for name, run in runs.items():
        for entry in run.get('history', []):
            node = {
                'checkpoint_id': entry.get('checkpoint_id'),
                'run_id': name,
                'epoch': entry.get('epoch'),
                'parent_checkpoint_id': run.get('parent_checkpoint_id'),
                'path': '%s/checkpoints/epoch_%02d' % (name, int(entry.get('epoch', 0))),
                'validation': entry.get('validation', {}),
            }
            all_nodes.append(node)
            s1 = entry.get('validation', {}).get('S1', {})
            loss = s1.get('loss')
            acc = s1.get('accuracy')
            if isinstance(loss, (int, float)) and (best_loss is None or loss < best_loss):
                best_loss, best_id = loss, entry.get('checkpoint_id')
            if isinstance(acc, (int, float)) and (best_acc is None or acc > best_acc):
                best_acc, best_acc_id = acc, entry.get('checkpoint_id')
        ckroot = root / name / 'checkpoints'
        if ckroot.exists():
            saved_weight_count += sum(1 for p in ckroot.iterdir() if p.is_dir() and (p / 'model.safetensors').exists())
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
    payload = {
        'experiment_id': manifest.get('experiment_id', 'OVERNIGHT-LAYA-SWEEP-02'),
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'code_commit': os.environ.get('MODELROUTER_CODE_COMMIT', 'unknown'),
        'status': 'running' if current else ('completed' if runs else 'prepared'),
        'overview': {
            'completed_runs': sum(r.get('status') in {'completed', 'early_stopped'} for r in runs.values()),
            'planned_runs': len(plans),
            'eligible_runs': plan_status.get('ELIGIBLE', 0),
            'blocked_runs': plan_status.get('BLOCKED', 0),
            'skipped_runs': plan_status.get('SKIPPED', 0),
            'checkpoint_total': len(all_nodes),
            'saved_weight_count': saved_weight_count,
            'current_run': current,
            'current_epoch': current_epoch,
            'best_s1_loss_checkpoint': best_id,
            'best_s1_loss': best_loss,
            'best_s1_accuracy_checkpoint': best_acc_id,
            'best_s1_accuracy': best_acc,
            'started_at': min(starts) if starts else None,
            'latest_sync_at': None,
            'github_sync': 'pending_local_sync',
        },
        'plans': plans,
        'plan_data': plan_data,
        'matrix': manifest.get('aggregate', {}),
        'runs': runs,
        'checkpoint_tree': all_nodes,
        'fixed_validation': manifest.get('fixed_validation', {}),
        'audit': manifest.get('audit', {}),
        'generation': generation,
    }
    _write(Path(out_root) / 'dashboard_data.json', payload)
    return payload


def run_sweep_experiment(run_id, manifest_path, model_dir, out_root, data_root=None,
                         epochs=3, max_len=1024, head_max_len=512):
    """Run one N01-N14 Sweep-02 plan through the same official training loop."""
    import torch
    from laya.train import (TrainConfig, calibration_records, evaluate_records,
                            load_checkpoint, optimizer_updates, save_checkpoint, train_model)

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
    parent_metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len)
    if 'S3' in val_rows:
        parent_metrics['S3_by_source_target'] = _s3_validation_breakdown(
            model, tok, val_rows['S3'], dev, sys.modules['laya.train'], cfg, max_len, head_max_len)

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
    run_meta = {
        'run_id': run_id, 'parent_checkpoint_id': parent_id,
        'base_model': model_path, 'data_dir_label': spec['data'],
        'train_origin': spec.get('train_origin', 'Base'),
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
        'audit_flags': {
            's2_100pct_not_generalization': True,
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
        'command': 'python router_data/laya_batch_train.py --sweep-run %s --sweep-manifest %s --out-root %s --epochs %s' % (run_id, manifest_path, out_root, epochs),
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
        metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len)
        if 'S3' in val_rows:
            metrics['S3_by_source_target'] = _s3_validation_breakdown(
                model, tok, val_rows['S3'], dev, sys.modules['laya.train'], cfg, max_len, head_max_len)
        validation_seconds = time.time() - validation_started
        s1_loss = metrics.get('S1', {}).get('loss')
        ckcfg = dict(cfg, max_len=max_len, head_max_len=head_max_len,
                     training_run={'run_id': run_id, 'epoch': epoch + 1,
                                   'parent_checkpoint_id': parent_id,
                                   'config': vars(config),
                                   'continuation_mode': run_meta['continuation_mode']})
        epoch_id = f'{run_id}-e{epoch + 1:02d}'
        epoch_dir = run_root / 'checkpoints' / f'epoch_{epoch + 1:02d}'
        checkpoint_started = time.time()
        save_checkpoint(model, tok, ckcfg, str(epoch_dir))
        save_checkpoint(model, tok, ckcfg, str(run_root / 'checkpoints' / 'latest'))
        improved = s1_loss is not None and (best_epoch is None or s1_loss < best_loss * 0.995)
        if improved:
            best_loss, best_epoch, no_improve = s1_loss, epoch + 1, 0
            save_checkpoint(model, tok, ckcfg, str(run_root / 'checkpoints' / 'best'))
        else:
            no_improve += 1
        checkpoint_seconds = time.time() - checkpoint_started
        try:
            gpu_util = float(subprocess.check_output(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                text=True, timeout=3).strip().splitlines()[0])
        except Exception:
            gpu_util = None
        try:
            checkpoint_bytes = sum(p.stat().st_size for p in (run_root / 'checkpoints').rglob('*') if p.is_file())
        except OSError:
            checkpoint_bytes = None
        epoch_total_seconds = time.time() - epoch_train_started
        entry = {
            'checkpoint_id': epoch_id, 'epoch': epoch + 1, 'train_loss': train_loss,
            'validation': metrics, 'improved_0_5pct': improved,
            'best_epoch': best_epoch, 'epoch_seconds': round(epoch_total_seconds, 3),
            'train_seconds': round(train_seconds, 3), 'validation_seconds': round(validation_seconds, 3),
            'checkpoint_seconds': round(checkpoint_seconds, 3), 'epoch_total_seconds': round(epoch_total_seconds, 3),
            'optimizer_updates': updates_per_epoch,
            'learning_rate': {'encoder': config.encoder_lr, 'head': config.head_lr},
            'gradient_norm': None,
            'gpu_memory_peak_mib': round(torch.cuda.max_memory_allocated() / 1048576, 2) if torch.cuda.is_available() else None,
            'gpu_utilization_percent': gpu_util, 'checkpoint_size_bytes': checkpoint_bytes,
            'global_step': (epoch + 1) * updates_per_epoch,
            'weights_saved': True,
        }
        history.append(entry)
        run_meta['history'] = history
        run_meta['current_epoch'] = epoch + 1
        run_meta['current_step'] = (epoch + 1) * updates_per_epoch
        run_meta['best_epoch'] = best_epoch
        _write(run_root / 'epoch_metrics.json', history)
        _write(run_root / 'epoch_status.json', {'run_id': run_id, 'epoch': epoch + 1,
                                                 'checkpoint_id': epoch_id, 'weights_saved': True,
                                                 'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
        _write(run_root / 'run.json', run_meta)
        _sweep_public_run(run_id, run_root, run_meta, history, manifest, out_root)
        print(json.dumps({'event': 'epoch_complete', 'run_id': run_id, 'epoch': epoch + 1,
                          'checkpoint_id': epoch_id, 'best_epoch': best_epoch,
                          's1_loss': s1_loss, 's1_accuracy': metrics.get('S1', {}).get('accuracy')},
                         ensure_ascii=False), flush=True)
        if epoch + 1 >= 2 and no_improve >= 2:
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
        _write(run_root / 'run.json', run_meta)
        _sweep_public_run(run_id, run_root, run_meta, history, manifest, out_root)
        raise
    run_meta['status'] = status
    run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    run_meta['history'] = history
    run_meta['best_epoch'] = best_epoch
    run_meta['current_epoch'] = len(history)
    _write(run_root / 'run.json', run_meta)
    _sweep_public_run(run_id, run_root, run_meta, history, manifest, out_root)
    print(json.dumps({'event': 'run_complete', 'run_id': run_id, 'status': status,
                      'best_epoch': best_epoch, 'epochs': len(history)}, ensure_ascii=False), flush=True)
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
    args = parser.parse_args()
    sys.path.insert(0, os.path.abspath('external/laya'))
    import laya.train as train_mod
    if args.sweep_run:
        result = run_sweep_experiment(args.sweep_run, args.sweep_manifest,
                                      args.model_dir, args.out_root,
                                      args.sweep_data_root or None, args.epochs)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.run == 'R0':
        print(json.dumps(run_baseline(args.batch_root, args.model_dir, args.out_root, args.seed), ensure_ascii=False, indent=2))
    else:
        result = run_experiment(args.run, args.batch_root, args.model_dir,
                                args.out_root, args.parent_checkpoint or None, args.epochs, args.seed)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
