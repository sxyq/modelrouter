"""Small overnight runner around the official Laya training functions."""
import argparse
import json
import os
import sys
import time
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-root', default='runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1/batch_preparation/batch1')
    parser.add_argument('--model-dir', default='models/laya-421m')
    parser.add_argument('--out-root', default='runs/OVERNIGHT-LAYA-TRAINING')
    parser.add_argument('--run', choices=['R0', 'R1', 'R2', 'R3'], default='R0')
    parser.add_argument('--parent-checkpoint', default='')
    parser.add_argument('--epochs', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    sys.path.insert(0, os.path.abspath('external/laya'))
    import laya.train as train_mod
    if args.run == 'R0':
        print(json.dumps(run_baseline(args.batch_root, args.model_dir, args.out_root, args.seed), ensure_ascii=False, indent=2))
    else:
        result = run_experiment(args.run, args.batch_root, args.model_dir,
                                args.out_root, args.parent_checkpoint or None, args.epochs, args.seed)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
