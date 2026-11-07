"""Build fixed Sweep 02 pools from saved source indexes and Batch 1 views."""

import json
import os
from collections import Counter, defaultdict

from modelrouter.data_pipeline.quality.quality_v2 import OWN_FILES, PUBLIC_FILES
from .batch_examples import _example


def _sweep_rows(path):
    with open(path, encoding='utf8') as f:
        return [json.loads(line) for line in f if line.strip()]

def _sweep_write_rows(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')

def _sweep_sample(rows, count, group_fields=()):
    rows = sorted(rows, key=lambda x: x.get('provenance', {}).get('stable_record_id', ''))
    if count >= len(rows):
        return rows
    if not group_fields:
        return rows[:count]
    buckets = defaultdict(list)
    for row in rows:
        p = row.get('provenance', {})
        qid = next(iter(row.get('questions', {})), '')
        key = tuple(p.get(field) if field != 'question_id' else qid for field in group_fields)
        buckets[key].append(row)
    ordered = [buckets[key] for key in sorted(buckets)]
    selected = []
    while len(selected) < count and ordered:
        next_round = []
        for bucket in ordered:
            if bucket:
                selected.append(bucket.pop(0))
                if len(selected) >= count:
                    break
            if bucket:
                next_round.append(bucket)
        ordered = next_round
    return sorted(selected, key=lambda x: x.get('provenance', {}).get('stable_record_id', ''))

def _sweep_audit(root):
    base = os.path.join(root, 'batch_preparation', 'batch1')
    audit = {'s2': {}, 'identity_overlap': {}, 's3_label_counts': {}}
    loaded = {}
    for name in ('S1', 'S2', 'S3'):
        for split in ('train', 'val'):
            loaded[(name, split)] = _sweep_rows(os.path.join(base, split, name + '.jsonl'))

    direct_outcome_keys = {
        'ground_truth_outcome', 'task_resolved', 'terminal', 'reward',
        'final_answer', 'outcome', 'resolved',
    }
    for split in ('train', 'val'):
        rows = loaded[('S2', split)]
        labels = Counter(str(next(iter(row.get('expected', {}).values()), '')) for row in rows)
        source_labels = Counter(
            (row.get('provenance', {}).get('source_id'), str(next(iter(row.get('expected', {}).values()), '')))
            for row in rows
        )
        state_keys = Counter()
        pre_keys = Counter()
        direct_rows = 0
        state_values = Counter()
        for row in rows:
            state = row.get('state', {})
            pre = state.get('pre_decision_state', {}) if isinstance(state, dict) else {}
            state_keys.update(state.keys() if isinstance(state, dict) else ())
            pre_keys.update(pre.keys() if isinstance(pre, dict) else ())
            if isinstance(pre, dict) and direct_outcome_keys.intersection(pre):
                direct_rows += 1
            state_values[json.dumps(pre, sort_keys=True, ensure_ascii=False)] += 1
        counts = list(labels.values())
        audit['s2'][split] = {
            'rows': len(rows),
            'labels': dict(labels),
            'source_label_counts': {src + ':' + label: n for (src, label), n in source_labels.items()},
            'state_keys': dict(state_keys),
            'pre_decision_state_keys': dict(pre_keys),
            'direct_outcome_key_rows': direct_rows,
            'exact_state_duplicate_extra_rows': sum(n - 1 for n in state_values.values() if n > 1),
            'majority_accuracy': round(max(counts) / len(rows), 6) if rows else None,
        }
    for name in ('S1', 'S2', 'S3'):
        train = loaded[(name, 'train')]
        val = loaded[(name, 'val')]
        for field in ('stable_record_id', 'independent_unit_id', 'trajectory_id'):
            train_ids = {row.get('provenance', {}).get(field) for row in train
                         if row.get('provenance', {}).get(field) is not None}
            val_ids = {row.get('provenance', {}).get(field) for row in val
                       if row.get('provenance', {}).get(field) is not None}
            audit['identity_overlap'][name + ':' + field] = len(train_ids & val_ids)
    for split in ('train', 'val'):
        counts = Counter()
        for row in loaded[('S3', split)]:
            p = row.get('provenance', {})
            qid = next(iter(row.get('questions', {})), '')
            label = str(next(iter(row.get('expected', {}).values()), ''))
            counts['%s:%s:%s' % (p.get('source_id'), qid, label)] += 1
        audit['s3_label_counts'][split] = dict(counts)
    return audit

def prepare_sweep02(args):
    """Build the fixed data pools for the second Laya comparison round.

    This reads the existing V2.1 references and Batch 1 views only. It does not
    reclassify any source or touch the original cleaned files.
    """
    root = os.path.abspath(os.path.join(args.all_data_out_dir, 'quality_grading_v2_1'))
    base = os.path.join(root, 'batch_preparation', 'batch1')
    out = os.path.abspath(args.sweep_out_dir or os.path.join(args.all_data_out_dir, 'sweep02_data'))
    os.makedirs(out, exist_ok=True)

    # Collect legal S1 candidate references by assigned layer.
    refs = defaultdict(list)
    for src in PUBLIC_FILES:
        if src in {'ROUTE-001', 'ROUTE-002'}:
            continue
        index_path = os.path.join(root, 'by_source', src + '.jsonl.gz')
        if not os.path.exists(index_path):
            continue
        with gzip.open(index_path, 'rt', encoding='utf8') as f:
            for line in f:
                x = json.loads(line)
                if x.get('assigned_layer') not in {'L1', 'L2', 'L3', 'L4'}:
                    continue
                if x.get('split') != 'train' or not x.get('train_eligible'):
                    continue
                if not x.get('source_policy_train_allowed'):
                    continue
                if 'human_pairwise_preference' not in (x.get('candidate_targets') or []):
                    continue
                refs[(src, x['source_line'])].append(x)

    rows_by_layer = defaultdict(list)
    for src in sorted({key[0] for key in refs}):
        path = os.path.join(args.cleaned_root, PUBLIC_FILES[src])
        max_line = max(key[1] for key in refs if key[0] == src)
        for line_no, raw in _source_rows(path):
            if line_no > max_line:
                break
            for x in refs.get((src, line_no), []):
                row = _example(src, raw, x, 'human_pairwise_preference')
                if row is None:
                    continue
                row['_meta']['sweep02_layer'] = x['assigned_layer']
                row['_meta']['sweep02_source_line'] = x['source_line']
                rows_by_layer[x['assigned_layer']].append(row)

    rank = {'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4}
    pool_counts = {}
    fixed_val_s1 = _sweep_rows(os.path.join(base, 'val', 'S1.jsonl'))
    for pool, max_rank in (('A', 1), ('B', 2), ('C', 3), ('D', 4)):
        rows = [row for layer, layer_rows in rows_by_layer.items() if rank[layer] <= max_rank for row in layer_rows]
        rows = sorted(rows, key=lambda x: x.get('provenance', {}).get('stable_record_id', ''))
        pool_dir = os.path.join(out, 'pools', pool)
        _sweep_write_rows(os.path.join(pool_dir, 'train', 'S1.jsonl'), rows)
        _sweep_write_rows(os.path.join(pool_dir, 'val', 'S1.jsonl'), fixed_val_s1)
        pool_counts[pool] = {'train_s1': len(rows), 'fixed_val_s1': len(fixed_val_s1),
                             'layers': [layer for layer, n in rank.items() if n <= max_rank]}

    # The auxiliary pools are the already audited Batch 1 views.
    shared = os.path.join(out, 'shared')
    for name in ('S2', 'S3'):
        for split in ('train', 'val'):
            _sweep_write_rows(os.path.join(shared, split, name + '.jsonl'),
                              _sweep_rows(os.path.join(base, split, name + '.jsonl')))
    _sweep_write_rows(os.path.join(shared, 'val', 'S1.jsonl'), fixed_val_s1)

    s2_train = _sweep_rows(os.path.join(shared, 'train', 'S2.jsonl'))
    s2_val = _sweep_rows(os.path.join(shared, 'val', 'S2.jsonl'))
    s3_train = _sweep_rows(os.path.join(shared, 'train', 'S3.jsonl'))
    s3_val = _sweep_rows(os.path.join(shared, 'val', 'S3.jsonl'))
    s1_a = _sweep_rows(os.path.join(out, 'pools', 'A', 'train', 'S1.jsonl'))

    def compose(run_id, groups, val_groups):
        run_dir = os.path.join(out, 'experiments', run_id)
        for name, rows in groups.items():
            _sweep_write_rows(os.path.join(run_dir, 'train', name + '.jsonl'), rows)
        for name, rows in val_groups.items():
            _sweep_write_rows(os.path.join(run_dir, 'val', name + '.jsonl'), rows)
        return {'train': {name: len(rows) for name, rows in groups.items()},
                'val': {name: len(rows) for name, rows in val_groups.items()}}

    plan_data = {}
    for run_id, pool in (('N01', 'A'), ('N05', 'B'), ('N06', 'C'), ('N07', 'D')):
        pool_rows = _sweep_rows(os.path.join(out, 'pools', pool, 'train', 'S1.jsonl'))
        plan_data[run_id] = compose(run_id, {'S1': pool_rows}, {'S1': fixed_val_s1})
    plan_data['N02'] = compose('N02', {'S1': list(s1_a)}, {'S1': fixed_val_s1})
    plan_data['N03'] = compose('N03', {'S1': list(s1_a)}, {'S1': fixed_val_s1})
    plan_data['N04'] = compose('N04', {'S1': list(s1_a)}, {'S1': fixed_val_s1})

    s2_equal = _sweep_sample(s2_train, len(s2_train))
    s3_equal = _sweep_sample(s3_train, len(s2_train), ('source_id', 'question_id'))
    plan_data['N08'] = compose('N08', {'S1': _sweep_sample(s1_a, len(s2_train)), 'S2': s2_equal},
                                {'S1': fixed_val_s1, 'S2': s2_val})
    plan_data['N09'] = compose('N09', {'S1': list(s1_a), 'S3': _sweep_sample(s3_train, len(s1_a), ('source_id', 'question_id'))},
                                {'S1': fixed_val_s1, 'S3': s3_val})
    plan_data['N10'] = compose('N10', {'S1': _sweep_sample(s1_a, len(s2_train)), 'S2': s2_equal, 'S3': s3_equal},
                               {'S1': fixed_val_s1, 'S2': s2_val, 'S3': s3_val})
    half = len(s1_a) // 2
    plan_data['N11'] = compose('N11', {'S1': list(s1_a), 'S2': _sweep_sample(s2_train, half),
                                       'S3': _sweep_sample(s3_train, half, ('source_id', 'question_id'))},
                               {'S1': fixed_val_s1, 'S2': s2_val, 'S3': s3_val})

    plans = {
        'N01': {'data': 'experiments/N01', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1']},
        'N02': {'data': 'experiments/N02', 'seed': 43, 'train_origin': 'Base', 'groups': ['S1']},
        'N03': {'data': 'experiments/N03', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1'], 'freeze_encoder': True},
        'N04': {'data': 'experiments/N04', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1'], 'encoder_lr': 1e-5, 'head_lr': 5e-5},
        'N05': {'data': 'experiments/N05', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1']},
        'N06': {'data': 'experiments/N06', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1']},
        'N07': {'data': 'experiments/N07', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1']},
        'N08': {'data': 'experiments/N08', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1', 'S2'], 'ratio': '1:1'},
        'N09': {'data': 'experiments/N09', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1', 'S3'], 'ratio': '1:1'},
        'N10': {'data': 'experiments/N10', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1', 'S2', 'S3'], 'ratio': '1:1:1'},
        'N11': {'data': 'experiments/N11', 'seed': 42, 'train_origin': 'Base', 'groups': ['S1', 'S2', 'S3'], 'ratio': '2:1:1'},
        'N12': {'data': None, 'seed': 42, 'train_origin': 'selected_checkpoint', 'groups': [], 'status': 'planned_after_N01_N11'},
        'N13': {'data': None, 'seed': 44, 'train_origin': 'selected_pure_s1', 'groups': [], 'status': 'planned_after_N01_N07'},
        'N14': {'data': None, 'seed': 44, 'train_origin': 'selected_multi_supervision', 'groups': [], 'status': 'planned_after_N08_N11'},
    }
    manifest = {
        'experiment_id': 'OVERNIGHT-LAYA-SWEEP-02',
        'source': 'existing V2.1 by_source indexes and Batch 1 views',
        'output_root': out,
        'fixed_validation': {'S1': 'shared/val/S1.jsonl', 'S1_rows': len(fixed_val_s1),
                             'S2': 'shared/val/S2.jsonl', 'S2_rows': len(s2_val),
                             'S3': 'shared/val/S3.jsonl', 'S3_rows': len(s3_val)},
        'pool_counts': pool_counts,
        'plan_data': plan_data,
        'plans': plans,
        'audit': _sweep_audit(root),
        'generation': {'reclassified_sources': False, 'test_used': False},
    }
    _dump(os.path.join(out, 'sweep_manifest.json'), manifest)
    print(json.dumps({'sweep_out': out, 'pool_counts': pool_counts,
                      'plan_data': plan_data, 'audit': manifest['audit']}, ensure_ascii=False), flush=True)
    return manifest
