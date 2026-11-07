"""Training matrix selection, coverage, and row materialization."""

import gzip
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

from modelrouter.data_pipeline.quality.quality_v2 import OWN_FILES, PUBLIC_FILES, VARIABLES
from .batch_constants import FULL_COMBOS, FULL_LAYERS, FULL_POLICIES, FULL_QUALITY, MATRIX_ALLOWED_SOURCES, MATRIX_TARGETS
from .batch_examples import _dump, _example, _rewrite_materialized_row, _source_rows


def _matrix_unit(ref, target):
    if target in {'observed_success', 'observed_failure'}:
        return ref.get('trajectory_id') or ref.get('independent_unit_id')
    return ref.get('independent_unit_id') or ref.get('stable_record_id')

def _matrix_ref(x, target):
    return {k: x.get(k) for k in (
        'source_id', 'source_line', 'source_file', 'stable_record_id',
        'independent_unit_id', 'trajectory_id', 'primary_supervision_class',
        'split', 'license_status', 'label_evidence', 'variable_coverage') } | {
        'target': target, 'quality_grade': x.get('quality_grade'),
        'assigned_layer': x.get('assigned_layer')}

def _matrix_select(refs, policy, target, quota):
    refs = sorted(refs, key=lambda x: (x.get('stable_record_id') or '', x.get('source_line', 0)))
    if policy == 'PB':
        seen = set(); refs = [r for r in refs if not (_matrix_unit(r, target) in seen or seen.add(_matrix_unit(r, target)))]
    elif policy == 'PC':
        buckets = defaultdict(list)
        for r in refs: buckets[r.get('source_id')].append(r)
        refs = [r for group in itertools.zip_longest(*[buckets[k] for k in sorted(buckets)]) for r in group if r]
    return refs[:quota]

def _copy_rewritten_jsonl(src, dst):
    rows = rewritten = old_protocol = 0
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf8') as out_f:
        if not os.path.exists(src):
            return {'rows': 0, 'rewritten': 0, 'old_protocol_rows': 0}
        with open(src, encoding='utf8') as in_f:
            for line in in_f:
                if not line.strip():
                    continue
                row = json.loads(line)
                rows += 1
                before = json.dumps(row.get('questions', {}), ensure_ascii=False, sort_keys=True)
                if 'Predict this source-specific observed target:' in before:
                    old_protocol += 1
                row = _rewrite_materialized_row(row)
                after = json.dumps(row.get('questions', {}), ensure_ascii=False, sort_keys=True)
                rewritten += before != after
                out_f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    return {'rows': rows, 'rewritten': rewritten, 'old_protocol_rows': old_protocol}

def _matrix_materialize(args, out, run_id, refs_by_target, groups, val_root, audit=None):
    wanted = defaultdict(lambda: defaultdict(list))
    audit = audit if audit is not None else {}
    selected_by_target = Counter()
    for target, refs in refs_by_target.items():
        selected_by_target[target] += len(refs)
        for ref in refs:
            wanted[ref['source_id']][ref['source_line']].append((target, ref))
    handles = {}
    stats = Counter()
    encoded_by_target = Counter()
    encoded_units_by_target = defaultdict(set)
    encoded_units_by_class = defaultdict(set)
    encoded_breakdown = Counter()
    encoded_keys = set()
    encoded_source_keys = defaultdict(set)
    encoded_group_keys = defaultdict(set)
    skipped_by_target = Counter()
    try:
        for src, lines in wanted.items():
            path = (os.path.join(args.cleaned_root, PUBLIC_FILES[src])
                    if src in PUBLIC_FILES else OWN_FILES[src])
            max_line = max(lines)
            for line_no, raw in _source_rows(path):
                if line_no > max_line: break
                for target, ref in lines.get(line_no, []):
                    row = _example(src, raw, ref, target)
                    if row is None:
                        skipped_by_target[target] += 1
                        continue
                    s = ref['primary_supervision_class']
                    if s not in groups: continue
                    if s not in handles:
                        handles[s] = open(os.path.join(out, 'data', run_id, 'train', s + '.jsonl'), 'w', encoding='utf8')
                    handles[s].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
                    stats[s] += 1
                    encoded_by_target[target] += 1
                    encoded_units_by_target[target].add(_matrix_unit(ref, target))
                    encoded_units_by_class[s].add(_matrix_unit(ref, target))
                    encoded_breakdown[(ref.get('assigned_layer'), ref.get('quality_grade'), s, src, target)] += 1
                    encoded_keys.add((src, ref.get('stable_record_id'), target))
                    encoded_source_keys[src].add((ref.get('stable_record_id'), target))
                    encoded_group_keys[(ref.get('assigned_layer'), ref.get('quality_grade'), s)].add(
                        (ref.get('stable_record_id'), target))
    finally:
        for f in handles.values(): f.close()
    for s in groups:
        src = os.path.join(val_root, 'val', s + '.jsonl')
        dst = os.path.join(out, 'data', run_id, 'val', s + '.jsonl')
        val_audit = _copy_rewritten_jsonl(src, dst)
        audit.setdefault('val', {})[s] = val_audit
    audit['selected_items_by_target'] = dict(selected_by_target)
    audit['encoded_items_by_target'] = dict(encoded_by_target)
    audit['encoded_units_by_target'] = {k: len(v) for k, v in encoded_units_by_target.items()}
    audit['encoded_items_by_class'] = dict(stats)
    audit['encoded_units_by_class'] = {k: len(v) for k, v in encoded_units_by_class.items()}
    audit['repeated_sampling_by_target'] = {k: max(0, encoded_by_target[k] - len(v)) for k, v in encoded_units_by_target.items()}
    audit['skipped_by_target'] = dict(skipped_by_target)
    audit['encoded_breakdown'] = {'|'.join(str(y) for y in k): v for k, v in encoded_breakdown.items()}
    audit['_encoded_keys'] = encoded_keys
    audit['_encoded_source_keys'] = encoded_source_keys
    audit['_encoded_group_keys'] = encoded_group_keys
    return dict(stats)

def _build_matrix_coverage(root, allowed_sources):
    """Summarize source rows, legal candidates, units, variables and run-ready groups."""
    summary_path = os.path.join(root, 'quality_summary.json')
    summary = json.load(open(summary_path, encoding='utf8'))
    source_ids = list(summary.get('quality_by_source', {}))
    layer_details = summary.get('layer_details', {})
    source_cov = {}
    layer_cov = {}
    group_counts = Counter()
    group_units = defaultdict(set)
    source_group_counts = Counter()
    source_group_units = defaultdict(set)
    source_units = defaultdict(set)
    layer_units = defaultdict(set)
    for src in source_ids:
        src_summary = summary.get('quality_by_source', {}).get(src, {})
        source_cov[src] = {
            'raw_records': int(src_summary.get('rows', 0)),
            'raw_independent_units': int(src_summary.get('independent_units', 0)),
            'matrix_source': src in allowed_sources,
            'matrix_source_records': int(src_summary.get('rows', 0)) if src in allowed_sources else 0,
            'eligible_candidate_records': 0,
            'eligible_independent_units': 0,
            'actual_encoded_items': 0,
            'run_item_exposure': 0,
            'dedup_encoded_items': 0,
            'variables_nonempty': {v: 0 for v in VARIABLES},
        }
        for layer in ('L1', 'L2', 'L3', 'L4'):
            z = layer_details.get(layer, {}).get(src, {})
            layer_cov.setdefault(layer, {})[src] = {
                'raw_records': int(z.get('rows', 0)),
                'raw_independent_units': int(z.get('independent_units', 0)),
                'eligible_independent_units_source_summary': int(z.get('candidate_independent_units', 0)),
                'eligible_candidate_records': 0,
                'eligible_independent_units': 0,
                'actual_encoded_items': 0,
                'run_item_exposure': 0,
                'variables_nonempty': {v: 0 for v in VARIABLES},
            }
    try:
        for src in source_ids:
            path = os.path.join(root, 'by_source', src + '.jsonl.gz')
            with gzip.open(path, 'rt', encoding='utf8') as f:
                for line in f:
                    x = json.loads(line)
                    layer = x.get('assigned_layer')
                    quality = x.get('quality_grade')
                    supervision = x.get('primary_supervision_class')
                    if layer not in {'L1', 'L2', 'L3', 'L4'}:
                        continue
                    for v in VARIABLES:
                        if x.get('variable_coverage', {}).get(v):
                            source_cov[src]['variables_nonempty'][v] += 1
                            layer_cov[layer][src]['variables_nonempty'][v] += 1
                    legal = (x.get('split') == 'train' and x.get('train_eligible')
                             and x.get('source_policy_train_allowed') and quality in {'Q1', 'Q2'}
                             and supervision in {'S1', 'S2', 'S3', 'S4'})
                    if not legal:
                        continue
                    source_cov[src]['eligible_candidate_records'] += 1
                    layer_cov[layer][src]['eligible_candidate_records'] += 1
                    key = (layer, quality, supervision)
                    group_counts[key] += 1
                    source_group_counts[(src,) + key] += 1
                    unit = x.get('independent_unit_id')
                    if unit is not None:
                        source_units[src].add(unit)
                        layer_units[layer].add((src, unit))
                        group_units[key].add(unit)
                        source_group_units[(src,) + key].add(unit)
    finally:
        pass
    for src in source_ids:
        source_cov[src]['eligible_independent_units'] = len(source_units[src])
    grouped = {}
    for layer in ('L1', 'L2', 'L3', 'L4'):
        layer_total = {
            'raw_records': sum(v['raw_records'] for v in layer_cov[layer].values()),
            'eligible_candidate_records': sum(v['eligible_candidate_records'] for v in layer_cov[layer].values()),
            'eligible_independent_units': len(layer_units[layer]),
            'actual_encoded_items': 0,
            'run_item_exposure': 0,
            'dedup_encoded_items': 0,
            'variables_nonempty': {v: sum(z['variables_nonempty'][v] for z in layer_cov[layer].values()) for v in VARIABLES},
            'by_quality_supervision': {},
            'by_source': layer_cov[layer],
        }
        for quality in ('Q1', 'Q2'):
            for supervision in ('S1', 'S2', 'S3', 'S4'):
                k = quality + '|' + supervision
                layer_total['by_quality_supervision'][k] = {
                    'eligible_candidate_records': group_counts[(layer, quality, supervision)],
                    'eligible_independent_units': len(group_units[(layer, quality, supervision)]),
                    'actual_encoded_items': 0,
                    'run_item_exposure': 0,
                }
        grouped[layer] = layer_total
    source_cov['__totals__'] = {
        'raw_records': sum(v['raw_records'] for k, v in source_cov.items() if k != '__totals__'),
        'matrix_source_records': sum(v['matrix_source_records'] for k, v in source_cov.items() if k != '__totals__'),
        'eligible_candidate_records': sum(v['eligible_candidate_records'] for k, v in source_cov.items() if k != '__totals__'),
        'eligible_independent_units': sum(v['eligible_independent_units'] for k, v in source_cov.items() if k != '__totals__'),
        'actual_encoded_items': 0,
        'run_item_exposure': 0,
        'dedup_encoded_items': 0,
    }
    return {'source_ids': source_ids, 'sources': source_cov, 'by_layer': grouped,
            'group_units': group_units, 'source_group_units': source_group_units}

def prepare_full_matrix(args):
    """Create a versioned matrix manifest and materialize only the requested queue."""
    root = os.path.abspath(os.path.join(args.all_data_out_dir, 'quality_grading_v2_1'))
    out = os.path.abspath(args.matrix_out_dir or os.path.join(args.all_data_out_dir, '..', 'MR-FULL-GRADED-TRAINING'))
    os.makedirs(out, exist_ok=True)
    pool_limit = int(getattr(args, 'matrix_pool_limit', 6000))
    max_items = int(getattr(args, 'matrix_max_items', 4096))
    prefix = getattr(args, 'matrix_run_prefix', '') or ''
    raw_selected = [x.strip() for x in (getattr(args, 'matrix_run_ids', '') or '').split(',') if x.strip()]
    if not raw_selected:
        raw_selected = ['B01_C%02d_QB_PB' % i for i in range(1, 17)]
    selected_base = set(raw_selected)
    selected_run_ids = [x if x.startswith(prefix) else prefix + x for x in raw_selected]
    counts = Counter()
    source_counts = Counter()
    unit_sets = defaultdict(set)
    reservoirs = defaultdict(list)
    index_root = os.path.join(root, 'by_source')
    for src in sorted(MATRIX_ALLOWED_SOURCES):
        path = os.path.join(index_root, src + '.jsonl.gz')
        with gzip.open(path, 'rt', encoding='utf8') as f:
            for line in f:
                x = json.loads(line)
                if x.get('split') != 'train' or not x.get('train_eligible') or not x.get('source_policy_train_allowed'):
                    continue
                q = x.get('quality_grade')
                layer = x.get('assigned_layer')
                if layer not in {'L1', 'L2', 'L3', 'L4'} or q not in {'Q1', 'Q2'}:
                    continue
                for s, targets in MATRIX_TARGETS.items():
                    for target in targets:
                        if target not in (x.get('candidate_targets') or []):
                            continue
                        key = (layer, q, s, target, src)
                        counts[key] += 1
                        source_counts[key] += 1
                        unit_sets[(layer, q, s, target)].add(_matrix_unit(x, target))
                        if len(reservoirs[key]) < pool_limit:
                            reservoirs[key].append(_matrix_ref(x, target))

    plans = {}
    materialized = {}
    materialization_audit = {}
    global_encoded_keys = set()
    global_source_keys = defaultdict(set)
    global_group_keys = defaultdict(set)
    base_ready = base_blocked = 0
    for b, layers in FULL_LAYERS.items():
        for c, (classes, weights) in FULL_COMBOS.items():
            for qcode, qset in FULL_QUALITY.items():
                for pcode in FULL_POLICIES:
                    base_run_id = f'{b}_{c}_{qcode}_{pcode}'
                    run_id = prefix + base_run_id
                    class_counts = {}
                    class_units = {}
                    for s in classes:
                        class_counts[s] = sum(
                            counts[(layer, q, s, target, src)]
                            for layer in layers for q in qset
                            for target in MATRIX_TARGETS[s] for src in MATRIX_ALLOWED_SOURCES
                        )
                        class_units[s] = len({
                            unit
                            for layer in layers for q in qset
                            for target in MATRIX_TARGETS[s]
                            for unit in unit_sets[(layer, q, s, target)]
                        })
                    available = all(class_counts.get(s, 0) > 0 for s in classes)
                    if available:
                        base_ready += 1
                    else:
                        base_blocked += 1
                    spec = {
                        'run_id': run_id,
                        'base_run_id': base_run_id,
                        'batch_id': b,
                        'combo_id': c,
                        'quality_code': qcode,
                        'sampling_code': pcode,
                        'layers': layers,
                        'supervision_classes': classes,
                        'ratios': weights,
                        'status': 'ELIGIBLE' if available else 'BLOCKED',
                        'eligibility_reason': 'legal train rows for every requested supervision class' if available else 'no legal train rows for one or more requested supervision classes',
                        'materialized': False,
                        'data': None,
                        'counts': class_counts,
                        'independent_units': class_units,
                        'train_origin': 'Base',
                        'seed': 42,
                        'groups': classes,
                        'max_len': 1024,
                        'head_max_len': 512,
                        'source_count': len(MATRIX_ALLOWED_SOURCES),
                        'protocol_version': 'MR-FULL-GRADED-P0-DATA-REPAIR-v1',
                        'legacy_input_protocol': False,
                    }
                    if base_run_id in selected_base or run_id in selected_base:
                        if available:
                            refs_by_target = defaultdict(list)
                            audit = {
                                'planned_ratios': {s: weight / max(1, sum(weights)) for s, weight in zip(classes, weights)},
                                'available_items_by_class': dict(class_counts),
                                'class_quota_by_class': {},
                                'shortfall_by_class': {},
                                'selection_policy': 'class-level quota; stable unit-aware target allocation',
                            }
                            total_weight = sum(weights)
                            for s, weight in zip(classes, weights):
                                class_quota = max(1, int(max_items * weight / max(1, total_weight)))
                                audit['class_quota_by_class'][s] = class_quota
                                target_refs = {}
                                for target in MATRIX_TARGETS[s]:
                                    target_refs[target] = [
                                        r for (layer, q, ss, tt, src), rows in reservoirs.items()
                                        if ss == s and tt == target and layer in layers and q in qset
                                        for r in rows
                                    ]
                                target_pool = {
                                    t: _matrix_select(rows, pcode, t, len(rows))
                                    for t, rows in target_refs.items() if rows
                                }
                                total_available = sum(len(rows) for rows in target_pool.values())
                                remaining = class_quota
                                target_names = sorted(target_pool)
                                for index, target in enumerate(target_names):
                                    if remaining <= 0:
                                        break
                                    if index == len(target_names) - 1:
                                        target_quota = min(len(target_pool[target]), remaining)
                                    else:
                                        target_quota = min(
                                            len(target_pool[target]),
                                            max(0, round(class_quota * len(target_pool[target]) / max(1, total_available))),
                                        )
                                        if target_quota == 0 and remaining > 0:
                                            target_quota = 1
                                    chosen = _matrix_select(target_pool[target], pcode, target, target_quota)
                                    refs_by_target[target].extend(chosen)
                                    remaining -= len(chosen)
                                if remaining > 0:
                                    for target in target_names:
                                        if remaining <= 0:
                                            break
                                        already = {r.get('stable_record_id') for r in refs_by_target[target]}
                                        extra = [r for r in target_pool[target] if r.get('stable_record_id') not in already]
                                        chosen = _matrix_select(extra, pcode, target, min(remaining, len(extra)))
                                        refs_by_target[target].extend(chosen)
                                        remaining -= len(chosen)
                                if remaining > 0:
                                    audit['shortfall_by_class'][s] = {
                                        'items': remaining,
                                        'reason': 'available source/quality/target reservoir smaller than class quota',
                                    }
                            for d in ('train', 'val'):
                                os.makedirs(os.path.join(out, 'data', run_id, d), exist_ok=True)
                            val_root = os.path.join(root, 'batch_preparation', 'batch1')
                            materialized[run_id] = _matrix_materialize(
                                args, out, run_id, refs_by_target, classes, val_root, audit=audit
                            )
                            materialization_audit[run_id] = audit
                            global_encoded_keys.update(audit.pop('_encoded_keys', set()))
                            for src, keys in audit.pop('_encoded_source_keys', {}).items():
                                global_source_keys[src].update(keys)
                            for key, keys in audit.pop('_encoded_group_keys', {}).items():
                                global_group_keys[key].update(keys)
                            actual_items = dict(audit.get('encoded_items_by_class', materialized[run_id]))
                            total_actual = sum(actual_items.values())
                            audit['actual_item_ratios'] = {
                                s: (actual_items.get(s, 0) / total_actual if total_actual else 0.0)
                                for s in classes
                            }
                            audit['actual_item_counts'] = actual_items
                            audit['effective_optimization_items'] = total_actual
                            audit['actual_independent_units'] = dict(audit.get('encoded_units_by_class', {}))
                            audit['status'] = 'CPU_MATERIALIZED'
                            spec.update({
                                'materialized': True,
                                'data': 'data/' + run_id,
                                'materialized_counts': materialized[run_id],
                                'materialization_audit': audit,
                                'status': 'CPU_MATERIALIZED',
                            })
                    plans[run_id] = spec

    extras = []
    for extra_prefix, n in [('CUR', 12), ('SEED', 40), ('ABL', 32)]:
        for i in range(1, n + 1):
            base_extra = f'{extra_prefix}{i:02d}'
            rid = prefix + base_extra
            plans[rid] = {
                'run_id': rid,
                'base_run_id': base_extra,
                'status': 'PLANNED',
                'materialized': False,
                'data': None,
                'eligibility_reason': 'reserved extension slot after base matrix',
                'groups': [],
                'seed': 42,
                'protocol_version': 'MR-FULL-GRADED-P0-DATA-REPAIR-v1',
                'legacy_input_protocol': False,
            }
            extras.append(rid)

    coverage = _build_matrix_coverage(root, MATRIX_ALLOWED_SOURCES)
    for run_id, audit in materialization_audit.items():
        for encoded_key, count in audit.get('encoded_breakdown', {}).items():
            layer, quality, supervision, src, target = encoded_key.split('|', 4)
            coverage['sources'][src]['run_item_exposure'] += count
            coverage['by_layer'][layer]['run_item_exposure'] += count
            coverage['by_layer'][layer]['by_quality_supervision'][quality + '|' + supervision]['run_item_exposure'] += count
            coverage['by_layer'][layer]['by_source'][src]['run_item_exposure'] += count
    for src, keys in global_source_keys.items():
        coverage['sources'][src]['actual_encoded_items'] = len(keys)
        coverage['sources'][src]['dedup_encoded_items'] = len(keys)
    for layer in ('L1', 'L2', 'L3', 'L4'):
        for quality in ('Q1', 'Q2'):
            for supervision in ('S1', 'S2', 'S3', 'S4'):
                key = (layer, quality, supervision)
                value = len(global_group_keys[key])
                coverage['by_layer'][layer]['by_quality_supervision'][quality + '|' + supervision]['actual_encoded_items'] = value
                coverage['by_layer'][layer]['by_quality_supervision'][quality + '|' + supervision]['dedup_encoded_items'] = value
        coverage['by_layer'][layer]['actual_encoded_items'] = sum(
            len(global_group_keys[(layer, q, s)]) for q in ('Q1', 'Q2') for s in ('S1', 'S2', 'S3', 'S4')
        )
        coverage['by_layer'][layer]['dedup_encoded_items'] = coverage['by_layer'][layer]['actual_encoded_items']
    coverage['sources']['__totals__']['actual_encoded_items'] = len(global_encoded_keys)
    coverage['sources']['__totals__']['run_item_exposure'] = sum(
        v['run_item_exposure'] for k, v in coverage['sources'].items() if k != '__totals__'
    )
    coverage['sources']['__totals__']['dedup_encoded_items'] = len(global_encoded_keys)
    coverage['totals'] = {
        'raw_records': coverage['sources']['__totals__']['raw_records'],
        'matrix_source_records': coverage['sources']['__totals__']['matrix_source_records'],
        'eligible_candidate_records': coverage['sources']['__totals__']['eligible_candidate_records'],
        'eligible_independent_units': coverage['sources']['__totals__']['eligible_independent_units'],
        'actual_encoded_items': len(global_encoded_keys),
        'run_item_exposure': coverage['sources']['__totals__']['run_item_exposure'],
        'dedup_encoded_items': len(global_encoded_keys),
    }
    coverage.pop('group_units', None)
    coverage.pop('source_group_units', None)

    old_manifest = getattr(args, 'matrix_source_manifest', '') or ''
    manifest = {
        'experiment_id': 'MR-FULL-GRADED-P0-DATA-REPAIR',
        'protocol_version': 'MR-FULL-GRADED-P0-DATA-REPAIR-v1',
        'legacy_input_protocol': False,
        'output_root': out,
        'source': 'existing quality_grading_v2_1/by_source indexes; no reclassification',
        'source_manifest': old_manifest,
        'theoretical_slots': len(plans),
        'base_slots': 1008,
        'extra_slots': len(extras),
        'plans': plans,
        'selected_queue': selected_run_ids,
        'selected_base_queue': sorted(selected_base),
        'materialized': materialized,
        'materialization_audit': materialization_audit,
        'generation': {
            'command': sys.argv,
            'pool_limit': pool_limit,
            'max_items_per_class': max_items,
            'test_used': False,
            'gpu_used': False,
            'model_loaded': False,
        },
        'audit': {
            'route_001_002_training': False,
            's2_observed_actions_are_not_model_choice': True,
            's3_prefix_reuse_is_not_physical_cache_hit': True,
            'validation_source': 'existing V2.1 Batch1 fixed validation, rewritten with neutral instructions',
            'val_protocol_rewritten': True,
        },
        'coverage': coverage,
        'aggregate': {
            'eligible': base_ready,
            'blocked': base_blocked,
            'planned': len(extras),
            'materialized_runs': len(materialized),
            'raw_source_records': coverage['totals']['raw_records'],
            'matrix_source_records': coverage['totals']['matrix_source_records'],
            'eligible_candidate_records': coverage['totals']['eligible_candidate_records'],
            'eligible_independent_units': coverage['totals']['eligible_independent_units'],
            'actual_encoded_items': coverage['totals']['actual_encoded_items'],
            'run_item_exposure': coverage['totals']['run_item_exposure'],
            'dedup_encoded_items': coverage['totals']['dedup_encoded_items'],
        },
    }
    _dump(os.path.join(out, 'experiment_matrix.json'), manifest)
    _dump(os.path.join(out, 'matrix_counts.json'), {
        'protocol_version': manifest['protocol_version'],
        'row_counts': {str(k): v for k, v in counts.items()},
        'source_counts': {str(k): v for k, v in source_counts.items()},
        'materialized': materialized,
        'materialization_audit': materialization_audit,
        'coverage_summary': coverage['totals'],
    })
    print(json.dumps({
        'out': out,
        'slots': len(plans),
        'materialized': list(materialized),
        'aggregate': manifest['aggregate'],
    }, ensure_ascii=False), flush=True)
    return manifest
