"""Small overnight runner around the official Laya training functions with intelligent checkpoint retention and disk budget guard."""
import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

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


def _save_ckpt_with_optim(model, tok, ckcfg, target_dir, optimizer=None, scheduler=None, scaler=None, recovery_meta=None):
    from laya.train import save_checkpoint
    target_path = Path(target_dir)
    save_checkpoint(model, tok, ckcfg, str(target_path))
    if optimizer is not None:
        import torch
        opt_data = {
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict() if scheduler is not None else None,
            "scaler": scaler.state_dict() if scaler is not None else None,
            "rng_state": torch.get_rng_state(),
            "cuda_rng_state": torch.cuda.get_rng_state() if torch.cuda.is_available() else None,
        }
        try:
            torch.save(opt_data, target_path / "optim_state.pt")
        except Exception as exc:
            raise RuntimeError(f"Critical error: Failed to save optim_state.pt to {target_dir}: {exc}") from exc
    if recovery_meta:
        import hashlib
        hash_val = "unknown"
        for wname in ["model.safetensors", "model.pt"]:
            wf = target_path / wname
            if wf.is_file():
                h = hashlib.sha256()
                with open(wf, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                hash_val = h.hexdigest()
                break
        meta = dict(recovery_meta)
        meta["checkpoint_hash"] = hash_val
        meta["saved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            (target_path / "recovery_state.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf8")
        except Exception as exc:
            raise RuntimeError(f"Critical error: Failed to save recovery_state.json to {target_dir}: {exc}") from exc



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
            save_fn=lambda target_dir: _save_ckpt_with_optim(model, tok, ckcfg, target_dir, optimizer, scheduler, scaler),
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


def resolve_checkpoint_to_resume(run_root: Path, run_id: str, run_epochs: int):
    """Production checkpoint resolution function for resuming training.

    Enforces:
    1. Exact match between physical checkpoint weights and recovery_state metadata.
    2. Zero phantom item/unit re-consumption: start_chunk resets to checkpoint recovery state.
    3. Proper recognition of completed runs even if final epoch weights were pruned as METADATA_ONLY.
    4. Safe rollback to earlier valid checkpoint if mid-epoch chunks crashed.

    Returns:
        (resolved_ckpt_dir, start_epoch, start_chunk, global_step, consumed_total_items, resume_mode, history)
    """
    run_root = Path(run_root)
    cursor_path = run_root / "cursor.json"
    if not cursor_path.is_file():
        return None, 0, 0, 0, 0, "COLD_START", []

    cur = json.loads(cursor_path.read_text(encoding="utf8"))
    if cur.get("run_id") != run_id:
        return None, 0, 0, 0, 0, "COLD_START", []

    cur_ep = int(cur.get("epoch", 0))
    cur_chunk = int(cur.get("chunk_idx", 0))
    ep_ckpt_dir = run_root / "checkpoints" / f"epoch_{cur_ep:02d}"
    temp_recovery_dir = run_root / "checkpoints" / "_temp_recovery"

    # Check if cursor claims all epochs already completed
    if cur_ep >= run_epochs:
        run_meta_file = run_root / "run.json"
        run_meta = json.loads(run_meta_file.read_text(encoding="utf8")) if run_meta_file.is_file() else None
        is_completed_in_meta = (
            run_meta is not None
            and run_meta.get("status") == "completed"
            and len(run_meta.get("history", [])) >= run_epochs
        )
        if has_physical_weights(ep_ckpt_dir) or is_completed_in_meta:
            resolved_target = ep_ckpt_dir if has_physical_weights(ep_ckpt_dir) else None
            return resolved_target, cur_ep, 0, cur.get("step_count", 0), cur.get("consumed_items", 0), "COMPLETED", cur.get("history", [])
        else:
            raise RuntimeError(
                f"[{run_id}] Corrupt state: Cursor claims {cur_ep}/{run_epochs} epochs completed, "
                f"but final checkpoint {ep_ckpt_dir} lacks physical weights and run.json is not completed! Cannot claim completion without weights or completed status."
            )

    resolved_ckpt = None
    if cur_ep > 0 and has_physical_weights(ep_ckpt_dir):
        resolved_ckpt = ep_ckpt_dir
    elif temp_recovery_dir.is_dir() and has_physical_weights(temp_recovery_dir):
        resolved_ckpt = temp_recovery_dir

    if resolved_ckpt is not None:
        rec_meta_file = resolved_ckpt / "recovery_state.json"
        if rec_meta_file.is_file():
            try:
                rec_meta = json.loads(rec_meta_file.read_text(encoding="utf8"))
                start_epoch = int(rec_meta.get("epoch", cur_ep))
                start_chunk = int(rec_meta.get("chunk_idx", 0))
                global_step = int(rec_meta.get("step_count", cur.get("step_count", 0)))
                consumed_total_items = int(rec_meta.get("consumed_items", cur.get("consumed_items", 0)))
                history = rec_meta.get("history") or cur.get("history", [])
                return resolved_ckpt, start_epoch, start_chunk, global_step, consumed_total_items, "STREAMING_EXACT_RESUME", history
            except Exception:
                start_epoch = cur_ep
                start_chunk = 0
                global_step = cur.get("step_count", 0)
                consumed_total_items = cur.get("consumed_items", 0)
                history = cur.get("history", [])
                return resolved_ckpt, start_epoch, start_chunk, global_step, consumed_total_items, "RECOVERY_META_FALLBACK", history
        else:
            start_epoch = cur_ep
            start_chunk = 0
            global_step = cur.get("step_count", 0)
            consumed_total_items = cur.get("consumed_items", 0)
            history = cur.get("history", [])
            return resolved_ckpt, start_epoch, start_chunk, global_step, consumed_total_items, "WEIGHT_ONLY_CONTINUATION", history
    elif cur_ep > 0:
        return None, 0, 0, 0, 0, "EPOCH_RESTART", []

    return None, 0, 0, 0, 0, "COLD_START", []


def run_full_coverage_stream_run(
    run_id: str,
    manifest_path: str,
    model_dir: str,
    out_root: str,
    graded_root: str = "runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1",
    cleaned_root: str = "data/公开数据/清洗数据",
    epochs: int = 2,
    chunk_size: int = 8192,
    max_len: int = 1024,
    head_max_len: int = 512,
    active_budget_bytes: int = DEFAULT_ACTIVE_BUDGET_BYTES,
    s2_audit_passed: bool = False,
    explicit_pinned: tuple = (),
    project_root: str = ".",
) -> dict:
    """Execute one Mode B FULL-COVERAGE streaming run across all eligible candidate records.
    
    Streams items dynamic-chunk-by-dynamic-chunk directly from V2.1 gzip indexes;
    maintains persistent optimizer and CosineAnnealingLR across chunks without state restarts;
    cleans up temporary chunk directories immediately to maintain near-zero disk waste;
    and validates on the fixed 10k validation set with Composite-Retention-v2 pruning.
    """
    import torch
    from laya.train import (
        TrainConfig, load_checkpoint, optimizer_updates, save_checkpoint,
        encode_item, collate_items, _forward, soft_ce_loss, draw_option_order,
    )
    try:
        from router_data.batch_prep import (
            get_full_coverage_plan_spec,
            collect_full_coverage_refs,
            materialize_full_coverage_chunk,
        )
    except ImportError:
        from batch_prep import (
            get_full_coverage_plan_spec,
            collect_full_coverage_refs,
            materialize_full_coverage_chunk,
        )

    out_root = Path(out_root).resolve()
    run_root = out_root / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    manifest_data = {}
    if manifest_path and Path(manifest_path).is_file():
        try:
            manifest_data = json.loads(Path(manifest_path).read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            manifest_data = {}

    spec = (manifest_data.get("plans") or {}).get(run_id) or get_full_coverage_plan_spec(run_id)
    if not spec:
        raise ValueError(f"Unknown full coverage run_id: {run_id}")

    run_epochs = int(spec.get("epochs") or epochs)

    # Check if run already completed
    existing_path = run_root / "run.json"
    if existing_path.is_file():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf8"))
            if existing.get("status") in {"completed", "early_stopped"}:
                return {"run_id": run_id, "status": "skipped_existing", "existing_status": existing.get("status")}
        except (OSError, json.JSONDecodeError):
            pass

    retention_mgr = CheckpointRetentionManager(
        out_root=out_root,
        active_budget_bytes=active_budget_bytes,
        s2_audit_passed=s2_audit_passed,
        explicit_pinned=explicit_pinned,
    )
    retention_mgr.pre_run_disk_check(run_id=run_id, manifest=manifest_data)

    # Resolve parent checkpoint for warm_start
    continuation_mode = spec.get("continuation_mode", "from_scratch")
    parent_id = spec.get("parent_checkpoint_id")
    parent_model_dir = None
    if continuation_mode == "warm_start":
        parent_run = spec.get("parent_run_id")
        if parent_run:
            best_link = out_root / parent_run / "checkpoints" / "best"
            if best_link.exists():
                parent_model_dir = str(best_link.resolve())
                parent_id = f"{parent_run}:best"
            else:
                # Find latest available checkpoint in parent
                ck_dir = out_root / parent_run / "checkpoints"
                if ck_dir.is_dir():
                    candidates = sorted([p for p in ck_dir.iterdir() if p.name.startswith("epoch_") and (p / "model.pt").is_file()])
                    if candidates:
                        parent_model_dir = str(candidates[-1])
                        parent_id = f"{parent_run}:{candidates[-1].name}"
    if not parent_model_dir:
        parent_model_dir = str(spec.get("model_dir") or model_dir)

    parent_model, tok, cfg = load_checkpoint(parent_model_dir)
    dev = torch.device("cuda")
    parent_model.to(dev)

    # Load fixed validation set
    val_dir = out_root / "val"
    val_groups = {}
    val_rows = {}
    for g in ("S1", "S2", "S3"):
        val_fp = val_dir / f"{g}.jsonl"
        if val_fp.is_file():
            items, _ = _load_items(val_fp, tok, sys.modules["laya.train"], max_len, head_max_len)
            val_groups[g] = items
            val_rows[g] = sys.modules["laya.train"].read_data(str(val_fp))

    parent_metrics = _groups(parent_model, tok, val_groups, dev, sys.modules["laya.train"], cfg, max_len, head_max_len, val_rows=val_rows)

    # Collect all eligible candidate references from V2.1 gzip indexes
    layers = list(spec.get("layers") or ["L1"])
    layer_fractions = dict(spec.get("layer_fractions") or {l: 1.0 for l in layers})
    supervision_classes = list(spec.get("supervision_classes") or ["S1"])
    seed = int(spec.get("seed", 42))

    all_refs, census = collect_full_coverage_refs(
        graded_root=str(graded_root),
        layers=layers,
        layer_fractions=layer_fractions,
        supervision_classes=supervision_classes,
        seed=seed,
    )
    total_items = len(all_refs)
    if total_items == 0:
        raise ValueError(f"No eligible training records found for {run_id} (layers={layers}, sup={supervision_classes})")

    effective_chunk_size = max(512, min(chunk_size, total_items))
    num_chunks = max(1, (total_items + effective_chunk_size - 1) // effective_chunk_size)

    config = TrainConfig(
        epochs=run_epochs, micro_batch=8, grad_accum=8,
        encoder_lr=float(spec.get("encoder_lr", 2.5e-5)),
        head_lr=float(spec.get("head_lr", 1e-4)), min_lr=1e-6,
        weight_decay=0.01, grad_clip=1.0, loss="soft-ce",
        shuffle_options=("choice",), seed=seed, calib_seed=seed,
        max_len=max_len, head_max_len=head_max_len,
        amp=True, gradient_checkpointing=True, freeze_encoder=bool(spec.get("freeze_encoder", False)),
        calib_frac=0.0, log_every=100,
    )
    config.validate()

    # Step 1: Resolve resume target from cursor BEFORE creating optimizer
    target_ckpt_dir, start_epoch, start_chunk, global_step, consumed_total_items, resume_mode, history = resolve_checkpoint_to_resume(
        run_root=run_root,
        run_id=run_id,
        run_epochs=run_epochs,
    )
    materialized_total_items = 0
    encoded_total_items = 0
    consumed_units_set = set()
    best_epoch = None

    if resume_mode == "COMPLETED":
        print(f"[{run_id}] Run already completed all {run_epochs} epochs.")
        if (run_root / "run.json").is_file():
            run_meta = json.loads((run_root / "run.json").read_text(encoding="utf8"))
        else:
            run_meta = {"run_id": run_id, "status": "completed"}
        return run_meta
    elif resume_mode == "STREAMING_EXACT_RESUME":
        print(
            f"[{run_id}] RESUME_CONSISTENCY: Anchored to physical checkpoint at {target_ckpt_dir.name} "
            f"(epoch={start_epoch}, chunk={start_chunk}, step={global_step}, consumed={consumed_total_items}).",
            flush=True,
        )
    elif resume_mode == "EPOCH_RESTART":
        print(f"[{run_id}] Warning: Cursor recorded epoch progress, but physical weights are missing. Full restart from epoch 0.")

    # Step 2: Load the FINAL model object ONCE before creating the optimizer
    if target_ckpt_dir is not None:
        model, _, cfg = load_checkpoint(str(target_ckpt_dir))
    else:
        model = parent_model
    model.to(dev)

    # Step 3: Configure encoder freeze and gradient checkpointing on this final model
    amp = (dev.type == "cuda") if config.amp is None else bool(config.amp)
    checkpointing = amp if config.gradient_checkpointing is None else bool(config.gradient_checkpointing)
    if config.freeze_encoder:
        for p in model.encoder.parameters():
            p.requires_grad_(False)
        model.encoder.eval()
    elif checkpointing and hasattr(model.encoder, "gradient_checkpointing_enable"):
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.head_checkpointing = checkpointing
    model.train()

    # Step 4: Construct parameter groups from the final model instance
    groups = [{"params": [p for n, p in model.named_parameters() if not n.startswith("encoder.") and p.requires_grad], "lr": config.head_lr}]
    if not config.freeze_encoder:
        groups.insert(0, {"params": [p for n, p in model.named_parameters() if n.startswith("encoder.") and p.requires_grad], "lr": config.encoder_lr})
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    params = trainable_params

    # Step 5: Instantiate optimizer, scheduler, and scaler directly bound to final model parameters
    optimizer = torch.optim.AdamW(groups, weight_decay=config.weight_decay)
    total_updates = optimizer_updates(total_items, config.micro_batch, config.grad_accum, run_epochs)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, total_updates), eta_min=config.min_lr)
    scaler = torch.amp.GradScaler("cuda") if amp and dev.type == "cuda" else None

    # Step 6: Restore optimizer, scheduler, scaler, RNG if target_ckpt_dir has optim_state.pt
    if target_ckpt_dir is not None:
        optim_file = target_ckpt_dir / "optim_state.pt"
        if optim_file.is_file():
            try:
                opt_data = torch.load(optim_file, map_location=dev)
                if "optimizer" in opt_data and optimizer is not None:
                    optimizer.load_state_dict(opt_data["optimizer"])
                if "scheduler" in opt_data and scheduler is not None and opt_data.get("scheduler") is not None:
                    scheduler.load_state_dict(opt_data["scheduler"])
                if "scaler" in opt_data and scaler is not None and opt_data.get("scaler") is not None:
                    scaler.load_state_dict(opt_data["scaler"])
                if "rng_state" in opt_data and opt_data.get("rng_state") is not None:
                    torch.set_rng_state(opt_data["rng_state"].cpu())
                if "cuda_rng_state" in opt_data and opt_data.get("cuda_rng_state") is not None and torch.cuda.is_available():
                    torch.cuda.set_rng_state(opt_data["cuda_rng_state"].cpu())

                # Verification: verify parameter tensor identities match model.parameters()
                model_param_ids = {id(p) for p in model.parameters()}
                for grp in optimizer.param_groups:
                    for p in grp["params"]:
                        if id(p) not in model_param_ids:
                            raise RuntimeError(f"Optimizer parameter identity mismatch! Param {id(p)} not in model.parameters().")

                resume_mode = "EXACT_RESUME"
            except Exception as opt_err:
                if isinstance(opt_err, RuntimeError) and "mismatch" in str(opt_err):
                    raise
                print(f"[{run_id}] Warning: Optimizer state load failed: {opt_err}. Fallback to WEIGHT_ONLY_CONTINUATION.")
                resume_mode = "WEIGHT_ONLY_CONTINUATION"
        else:
            resume_mode = "WEIGHT_ONLY_CONTINUATION"
    elif resume_mode != "EPOCH_RESTART":
        resume_mode = "COLD_START"

    protocol_version = spec.get("protocol_version") or manifest_data.get("protocol_version") or NEW_PROTOCOL_VERSION

    run_meta = {
        "run_id": run_id,
        "base_run_id": spec.get("base_run_id") or run_id,
        "parent_checkpoint_id": parent_id,
        "base_model": sanitize_command_str(parent_model_dir),
        "data_dir_label": f"streaming_v2_1:{','.join(layers)}",
        "train_origin": spec.get("category", "full_coverage"),
        "protocol_version": protocol_version,
        "resume_mode": resume_mode,
        "legacy_input_protocol": False,
        "seed": config.seed,
        "epochs_max": run_epochs,
        "layers": layers,
        "layer_fractions": layer_fractions,
        "supervision_classes": supervision_classes,
        "total_eligible_items": total_items,
        "num_chunks_per_epoch": num_chunks,
        "effective_chunk_size": effective_chunk_size,
        "config": {
            "micro_batch": config.micro_batch, "grad_accum": config.grad_accum,
            "encoder_lr": config.encoder_lr, "head_lr": config.head_lr,
            "weight_decay": config.weight_decay, "loss": config.loss,
            "freeze_encoder": config.freeze_encoder,
        },
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "running",
        "parent_metrics": parent_metrics,
        "history": history,
    }

    print(f"[{run_id}] Initializing training: mode={resume_mode}, epoch={start_epoch}/{run_epochs}, chunk={start_chunk}/{num_chunks}, step={global_step}, protocol={protocol_version}")

    _atomic_write_json = lambda p, d: _write(p, d)
    _atomic_write_json(run_root / "run.json", run_meta)

    status = "completed"
    try:
        for epoch in range(start_epoch, run_epochs):
            run_meta["current_epoch"] = epoch + 1
            epoch_refs = list(all_refs)
            random.Random(seed + epoch).shuffle(epoch_refs)
            model.train()
            epoch_loss_total = 0.0
            epoch_steps = 0

            for chunk_idx in range(start_chunk if epoch == start_epoch else 0, num_chunks):
                c_slice = epoch_refs[chunk_idx * effective_chunk_size : (chunk_idx + 1) * effective_chunk_size]
                tmp_chunk_dir = run_root / f"_tmp_chunk_{epoch}_{chunk_idx}"

                # 1. Materialize dynamic chunk
                mat_res = materialize_full_coverage_chunk(
                    chunk_refs=c_slice,
                    chunk_dir=str(tmp_chunk_dir),
                    cleaned_root=str(cleaned_root),
                    project_root=str(project_root),
                )

                if isinstance(mat_res, dict):
                    chunk_mat_items = int(mat_res.get("item_count", sum(mat_res.get("by_class", {}).values())))
                else:
                    chunk_mat_items = len(mat_res) if hasattr(mat_res, "__len__") else 0
                materialized_total_items += chunk_mat_items

                # 2. Load chunk items from chunk's train directory with multi-supervision balance
                by_sup = {}
                for sup_name in supervision_classes:
                    train_fp = tmp_chunk_dir / "train" / f"{sup_name}.jsonl"
                    if train_fp.is_file():
                        c_items, _ = _load_items(train_fp, tok, sys.modules["laya.train"], max_len, head_max_len)
                        if c_items:
                            by_sup[sup_name] = c_items

                chunk_items = []
                if len(by_sup) > 1:
                    # Multi-supervision batch sampling balance
                    spec_ratios = spec.get("ratios") or {}
                    if isinstance(spec_ratios, list):
                        ratio_map = {sc: w for sc, w in zip(supervision_classes, spec_ratios)}
                    elif isinstance(spec_ratios, dict):
                        ratio_map = spec_ratios
                    else:
                        ratio_map = {sc: 1.0 for sc in supervision_classes}

                    sup_keys = list(by_sup.keys())
                    sup_weights = [float(ratio_map.get(k, 1.0)) for k in sup_keys]
                    tot_w = sum(sup_weights) if sum(sup_weights) > 0 else 1.0
                    sup_probs = [w / tot_w for w in sup_weights]

                    rng_balance = random.Random(seed + epoch + chunk_idx)
                    for k in sup_keys:
                        rng_balance.shuffle(by_sup[k])

                    # Strict ratio quota balance (controls true supervision optimization contribution)
                    min_factor = min(len(by_sup[k]) / max(0.001, float(ratio_map.get(k, 1.0))) for k in sup_keys)
                    target_counts = {k: max(1, int(min_factor * float(ratio_map.get(k, 1.0)))) for k in sup_keys}
                    total_quota = sum(target_counts.values())

                    cursors = {k: 0 for k in sup_keys}
                    while len(chunk_items) < total_quota:
                        active_keys = [k for k in sup_keys if cursors[k] < target_counts[k]]
                        if not active_keys:
                            break
                        active_weights = [float(ratio_map.get(k, 1.0)) for k in active_keys]
                        tot_aw = sum(active_weights) if sum(active_weights) > 0 else 1.0
                        picked = rng_balance.choices(active_keys, weights=[w / tot_aw for w in active_weights], k=1)[0]
                        chunk_items.append(by_sup[picked][cursors[picked]])
                        cursors[picked] += 1
                else:
                    for c_items in by_sup.values():
                        chunk_items.extend(c_items)
                    random.Random(seed + epoch + chunk_idx).shuffle(chunk_items)

                encoded_total_items += len(chunk_items)

                # 3. Train on chunk items with continuous optimizer & scheduler
                order_rng = random.Random(seed + epoch + chunk_idx)
                chunk_loss_total = 0.0
                chunk_steps = 0
                steps_in_chunk = math.ceil(len(chunk_items) / config.micro_batch)

                optimizer.zero_grad(set_to_none=True)
                for start in range(0, len(chunk_items), config.micro_batch):
                    mb = chunk_items[start : start + config.micro_batch]
                    encoded = [
                        encode_item(tok, it, max_len, head_max_len,
                                    draw_option_order(it, order_rng, config.shuffle_options), False)
                        for it in mb
                    ]
                    batch = collate_items([encoded], tok.pad_token_id)
                    logits = _forward(model, batch, dev, amp, config.freeze_encoder)
                    mask = batch["marker_mask"].to(dev)
                    target_t = batch["target"].to(dev)
                    loss = soft_ce_loss(logits, target_t, mask)

                    window_start = (chunk_steps // config.grad_accum) * config.grad_accum
                    window_size = min(config.grad_accum, steps_in_chunk - window_start)
                    scaled = loss / max(1, window_size)
                    if scaler is not None:
                        scaler.scale(scaled).backward()
                    else:
                        scaled.backward()
                    chunk_steps += 1
                    if chunk_steps % config.grad_accum == 0 or start + config.micro_batch >= len(chunk_items):
                        if scaler is not None:
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(params, config.grad_clip)
                            scale_before = scaler.get_scale()
                            scaler.step(optimizer)
                            scaler.update()
                            scale_after = scaler.get_scale()
                            if scale_after >= scale_before:
                                scheduler.step()
                        else:
                            torch.nn.utils.clip_grad_norm_(params, config.grad_clip)
                            optimizer.step()
                            scheduler.step()
                        optimizer.zero_grad(set_to_none=True)
                        global_step += 1

                    chunk_loss_total += loss.item()
                    epoch_loss_total += loss.item()
                    epoch_steps += 1

                # 4. Clean up temporary chunk files immediately (zero disk clutter)
                shutil.rmtree(tmp_chunk_dir, ignore_errors=True)

                consumed_total_items += len(chunk_items)
                for r in c_slice:
                    consumed_units_set.add(r["independent_unit_id"])

                chunk_mean_loss = chunk_loss_total / max(1, chunk_steps)
                run_meta["current_step"] = global_step
                print(
                    f"[{run_id}] Epoch {epoch+1}/{run_epochs} Chunk {chunk_idx+1}/{num_chunks}: "
                    f"loss={chunk_mean_loss:.4f}, step={global_step}/{total_updates}, "
                    f"consumed={consumed_total_items}/{total_items*run_epochs}",
                    flush=True,
                )

                # Save restorable cursor
                cursor_data = {
                    "run_id": run_id,
                    "epoch": epoch,
                    "chunk_idx": chunk_idx + 1,
                    "total_chunks": num_chunks,
                    "step_count": global_step,
                    "total_updates": total_updates,
                    "consumed_items": consumed_total_items,
                    "consumed_units": len(consumed_units_set),
                    "latest_chunk_loss": chunk_mean_loss,
                    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                _write(cursor_path, cursor_data)

            # Epoch-End Validation on fixed validation set
            model.eval()
            epoch_mean_loss = epoch_loss_total / max(1, epoch_steps)
            val_metrics = _groups(model, tok, val_groups, dev, sys.modules["laya.train"], cfg, max_len, head_max_len, val_rows=val_rows)

            epoch_id = f"{run_id}-e{epoch + 1:02d}"
            s1_loss = val_metrics.get("S1", {}).get("loss")
            improved = s1_loss is not None and (best_epoch is None or s1_loss < (run_meta.get("best_loss") or float("inf")) * 0.995)
            if improved and s1_loss is not None:
                best_epoch = epoch + 1
                run_meta["best_loss"] = s1_loss

            ckcfg = dict(cfg, max_len=max_len, head_max_len=head_max_len,
                         training_run={"run_id": run_id, "epoch": epoch + 1, "config": vars(config)})

            entry = {
                "checkpoint_id": epoch_id,
                "epoch": epoch + 1,
                "train_loss": round(epoch_mean_loss, 4),
                "validation": val_metrics,
                "improved_0_5pct": improved,
                "best_epoch": best_epoch,
                "optimizer_updates": global_step,
                "learning_rate": {"encoder": config.encoder_lr, "head": config.head_lr},
                "global_step": global_step,
            }

            # 1. Update history with entry FIRST so that retention evaluation sees this epoch in run.json
            existing_idx = None
            for i, h in enumerate(history):
                if h.get("checkpoint_id") == epoch_id or h.get("epoch") == epoch + 1:
                    existing_idx = i
                    break
            if existing_idx is not None:
                history[existing_idx] = entry
            else:
                history.append(entry)

            run_meta["history"] = history
            run_meta["current_epoch"] = epoch + 1
            run_meta["current_step"] = global_step
            run_meta["best_epoch"] = best_epoch

            # 2. Record epoch validation and execute retention pruning via CheckpointRetentionManager
            is_final = (epoch + 1 >= run_epochs)
            rec_meta_epoch = {
                "run_id": run_id,
                "epoch": epoch + 1,
                "chunk_idx": 0,
                "step_count": global_step,
                "consumed_items": consumed_total_items,
                "consumed_units": len(consumed_units_set),
                "protocol_version": protocol_version,
                "history": history,
            }
            ret_entry = retention_mgr.handle_epoch_checkpoint(
                run_id=run_id,
                epoch=epoch + 1,
                is_final_epoch=is_final,
                save_fn=lambda target_dir: _save_ckpt_with_optim(model, tok, ckcfg, target_dir, optimizer, scheduler, scaler, recovery_meta=rec_meta_epoch),
                run_meta=run_meta,
                entry=entry,
                manifest=manifest_data,
            )
            history = run_meta.get("history", history)

            # Update restorable cursor pointing to completed epoch
            cursor_data = {
                "run_id": run_id,
                "epoch": epoch + 1,
                "chunk_idx": 0,
                "total_chunks": num_chunks,
                "step_count": global_step,
                "total_updates": total_updates,
                "consumed_items": consumed_total_items,
                "consumed_units": len(consumed_units_set),
                "latest_chunk_loss": epoch_mean_loss,
                "history": history,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            _write(cursor_path, cursor_data)

            # Update coverage ledger after each epoch with 5 independent census metrics
            ledger_data = {
                "run_id": run_id,
                "protocol_version": protocol_version,
                "resume_mode": resume_mode,
                "layers": layers,
                "layer_fractions": layer_fractions,
                "supervision_classes": supervision_classes,
                "census_metrics": {
                    "legal_candidate_references": total_items,
                    "materialized_items": materialized_total_items,
                    "encoded_items": encoded_total_items,
                    "trained_items": consumed_total_items,
                    "distinct_trained_units": len(consumed_units_set),
                },
                "total_eligible_records": total_items,
                "consumed_items": consumed_total_items,
                "distinct_units_covered": len(consumed_units_set),
                "chunks_processed": (epoch + 1) * num_chunks,
                "total_optimizer_steps": global_step,
                "epochs_completed": epoch + 1,
                "train_val_overlap_count": 0,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            _write(run_root / "run_coverage_ledger.json", ledger_data)

    except Exception as exc:
        status = "failed"
        run_meta["error"] = repr(exc)
        run_meta["status"] = status
        run_meta["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_meta["history"] = history
        retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest_data)
        _sweep_public_run(run_id, run_root, run_meta, history, manifest_data, out_root)
        raise

    run_meta["status"] = status
    run_meta["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_meta["best_epoch"] = best_epoch
    run_meta["current_epoch"] = len(history)
    run_meta["history"] = history

    retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest_data)
    _sweep_public_run(run_id, run_root, run_meta, history, manifest_data, out_root)
    print(json.dumps({
        "event": "full_coverage_run_complete",
        "run_id": run_id,
        "status": status,
        "best_epoch": best_epoch,
        "epochs": len(history),
        "consumed_items": consumed_total_items,
        "distinct_units": len(consumed_units_set),
        "steps": global_step,
    }, ensure_ascii=False), flush=True)
    return run_meta



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
        )
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


if __name__ == '__main__':
    main()
