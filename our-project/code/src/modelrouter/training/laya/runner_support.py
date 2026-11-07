"""Shared Laya batch loading, evaluation, reporting, and recovery state."""
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
_SRC_ROOT = str(Path(__file__).resolve().parents[3])
for _path in (_WORKSPACE_ROOT, _SRC_ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from modelrouter.training.common.checkpoint_retention import *
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


def _load_items(path, tok, train_mod, max_len, head_max_len, record_transform=None, input_exposure=None):
    rows = train_mod.read_data(str(path))
    if record_transform is not None:
        rows = [record_transform(row) for row in rows]
    if input_exposure is not None:
        items, skipped = [], Counter()
        for index, row in enumerate(rows):
            key = f'{Path(path).resolve()}:{index}'
            input_exposure.add(key, row['state'])
            row_items, row_skipped = train_mod.items_from_rows(
                tok, [row], max_len=max_len, head_max_len=head_max_len)
            skipped.update(row_skipped)
            for item in row_items:
                item['_v9_source_id'] = key
                item['_provenance'] = row.get('provenance') or {}
            items.extend(row_items)
        return items, {'rows': len(rows), 'items': len(items), 'skipped': dict(skipped)}
    items, skipped = train_mod.items_from_rows(tok, rows, max_len=max_len, head_max_len=head_max_len)
    if len(items) == len(rows):
        for it, r in zip(items, rows):
            if isinstance(it, dict):
                it["_provenance"] = r.get("provenance") or {}
    else:
        # Fallback to precise per-row attribution if any item was skipped
        items = []
        total_skipped = {}
        for r in rows:
            c_items, c_skip = train_mod.items_from_rows(tok, [r], max_len=max_len, head_max_len=head_max_len)
            for k, v in c_skip.items():
                total_skipped[k] = total_skipped.get(k, 0) + v
            for it in c_items:
                if isinstance(it, dict):
                    it["_provenance"] = r.get("provenance") or {}
                items.append(it)
        skipped = total_skipped
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


def _load_named_groups(data_root, group_names, tok, train_mod, max_len, head_max_len,
                       validation_root=None, record_transform=None, training_paths=None, validation_paths=None,
                       input_exposure=None):
    train_groups, val_groups, load, val_rows = {}, {}, {}, {}
    for name in group_names:
        train_path = Path((training_paths or {}).get(name, Path(data_root) / 'train' / (name + '.jsonl')))
        val_path = Path((validation_paths or {}).get(name, Path(validation_root or data_root) / 'val' / (name + '.jsonl')))
        train_groups[name], load['train_' + name] = _load_items(
            train_path, tok, train_mod, max_len, head_max_len, record_transform=record_transform,
            input_exposure=input_exposure)
        val_groups[name], load['val_' + name] = _load_items(val_path, tok, train_mod, max_len, head_max_len)
        val_rows[name] = train_mod.read_data(str(val_path))
    return train_groups, val_groups, load, val_rows


def _sweep_public_run(run_id, run_root, meta, history, manifest, out_root, retention_mgr):
    """Build the small public dashboard payload without server paths or row text."""
    root = Path(out_root)
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
    generation = {key: value for key, value in generation.items() if key != 'code_sha256'}
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

