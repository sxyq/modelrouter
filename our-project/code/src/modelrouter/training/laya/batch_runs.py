"""Existing Laya configuration and sweep training routines."""
import json
import os
import sys
import time
from pathlib import Path

from modelrouter.training.common.checkpoint_retention import *
from .runner_support import (
    StopRun, _write, _save_ckpt_with_optim, _groups, _load_run_files,
    _load_named_groups, _sweep_public_run,
)
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
        best_epoch = run_meta.get('best_epoch')
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


def run_sweep_experiment(run_id, manifest_path, model_dir, out_root, data_root=None,
                         epochs=3, max_len=1024, head_max_len=512,
                         active_budget_bytes=DEFAULT_ACTIVE_BUDGET_BYTES,
                         s2_audit_passed=False, explicit_pinned=(),
                         validation_root=None, record_transform=None, training_paths=None, validation_paths=None):
    """Run one Sweep / FULL-GRADED plan with selective checkpoint retention and disk guard."""
    import torch
    from laya.train import (TrainConfig, load_checkpoint, optimizer_updates,
                            save_checkpoint, train_model)

    manifest = (manifest_path if isinstance(manifest_path, dict)
                else json.loads(Path(manifest_path).read_text(encoding='utf8')))
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
                if spec.get('v9_continuation'):
                    return existing
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
    input_exposure = None
    if spec.get('v9_continuation'):
        from modelrouter.v9.training.continuation import InputExposure
        input_exposure = InputExposure()
    train_groups, val_groups, load, val_rows = _load_named_groups(
        data_dir, group_names, tok, sys.modules['laya.train'], max_len, head_max_len,
        validation_root=validation_root, record_transform=record_transform,
        training_paths=training_paths, validation_paths=validation_paths, input_exposure=input_exposure)
    train_items = [item for name in group_names for item in train_groups[name]]
    parent_metrics = _groups(model, tok, val_groups, dev, sys.modules['laya.train'], cfg, max_len, head_max_len, val_rows=val_rows)

    config = TrainConfig(
        epochs=epochs, micro_batch=int(spec.get('micro_batch', 8)), grad_accum=int(spec.get('grad_accum', 8)),
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
        **({'v9_continuation': {**spec['v9_continuation'], 'input_exposure': input_exposure.summary(),
                               'feature_exposure_basis': 'ACTUAL_TRAIN_ENCODING'},
            'validation_root': str(validation_root),
            'encoder_context_limit': getattr(model.encoder.config, 'max_position_embeddings', None)}
           if spec.get('v9_continuation') else {}),
        'eligibility_reason': spec.get('eligibility_reason'),
        'command': sanitize_command_str(
            ('in-process router_data.laya_batch_train.run_sweep_experiment: run=%s prepared=%s out=%s epochs=%s'
             % (run_id, spec['v9_continuation']['data_identity']['prepared_metadata'], out_root, epochs))
            if spec.get('v9_continuation') else
            ('python router_data/laya_batch_train.py --sweep-run %s --sweep-manifest %s --out-root %s --epochs %s'
            % (run_id, manifest_path, out_root, epochs)
            )
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

    train_mod = sys.modules['laya.train']
    official_encode = train_mod.encode_item
    if input_exposure is not None:
        def encode_item(tok, item, max_len, head_max_len, option_order=None, parallel=False):
            encoded = official_encode(tok, item, max_len, head_max_len, option_order, parallel)
            if '_v9_source_id' in item:
                _, _, lengths = train_mod.build_sequence(
                    tok, None, item['q'], max_len, head_max_len, option_order=option_order,
                    state_ids=item['state_ids'], return_truncation_stats=True)
                retained = item['state_ids'][:lengths['state_tokens_used']]
                input_exposure.observe(item['_v9_source_id'], tok.decode(
                    retained, skip_special_tokens=False, clean_up_tokenization_spaces=False))
            return encoded
        train_mod.encode_item = encode_item

    def on_epoch_end(epoch, train_loss):
        if input_exposure is not None:
            run_meta['v9_continuation']['input_exposure'] = input_exposure.summary()
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
            save_fn=(lambda target_dir: save_checkpoint(model, tok, ckcfg, target_dir))
                    if spec.get('v9_continuation') else
                    (lambda target_dir: _save_ckpt_with_optim(model, tok, ckcfg, target_dir, optimizer, scheduler, scaler)),
            run_meta=run_meta,
            entry=entry,
            manifest=manifest,
        )
        best_epoch = run_meta.get('best_epoch')
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
        _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root, retention_mgr)
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
        if input_exposure is not None:
            run_meta['v9_continuation']['input_exposure'] = input_exposure.summary()
        retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest)
        _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root, retention_mgr)
        raise
    finally:
        train_mod.encode_item = official_encode
    run_meta['status'] = status
    run_meta['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    run_meta['best_epoch'] = best_epoch
    run_meta['current_epoch'] = len(run_meta['history'])
    if input_exposure is not None:
        from modelrouter.v9.training.continuation import feature_training_status
        run_meta['v9_continuation'].update(
            input_exposure=input_exposure.summary(),
            feature_training_status=feature_training_status(input_exposure.summary(), status in {'completed', 'early_stopped'}))
    retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest)
    _sweep_public_run(run_id, run_root, run_meta, run_meta['history'], manifest, out_root, retention_mgr)
    print(json.dumps({
        'event': 'run_complete', 'run_id': run_id, 'status': status,
        'best_epoch': best_epoch, 'epochs': len(run_meta['history']),
    }, ensure_ascii=False), flush=True)
    return run_meta

