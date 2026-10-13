"""Prepare batch references and small typed Laya examples from saved V2.1 indexes."""
import csv
import gzip
import json
import os
import sys
import time
import hashlib
import shutil
import itertools
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple
from .quality_v2 import PUBLIC_FILES, OWN_FILES, VARIABLES
from .all_data import _map_action_category


def _dump(path, value):
    with open(path, 'w', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def _source_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        if path.endswith('.csv'):
            yield from enumerate(csv.DictReader(f), 2)
        else:
            for i, line in enumerate(f, 1):
                if line.strip():
                    yield i, json.loads(line)


def _use(x):
    src=x['source_id']
    if src in {'ROUTE-001','ROUTE-002'}: return 'license_pending'
    if src in {'TRA-004','ROUTE-005','OWN-001','OWN-003'}: return 'analysis_only'
    if src in {'ROUTE-003','ENV-001','ENV-002','MEM-003','MEM-005'} or x['split'] in {'val','test','evaluation_only'}: return 'evaluation_only'
    if x.get('train_eligible'): return 'eligible'
    return 'reference_not_trainable'


def _unit(x,t):
    if t in {'observed_success','observed_failure'}: return x.get('trajectory_id') or x['independent_unit_id']
    if t in {'observed_action','inferred_command'}: return x['stable_record_id']
    return x['independent_unit_id']


def _neutral_instruction(target):
    if target == 'human_pairwise_preference':
        return 'Select the preferred candidate model for this decision record using the pre-decision information.'
    if target == 'observed_action':
        return 'Predict the observed action category for this record. This is an observed action, not an optimal model choice.'
    if target in {'observed_success', 'observed_failure'}:
        return 'Predict the observed trajectory outcome category for this record. This is an observed outcome, not an optimal model choice.'
    if target == 'prefix_reuse_opportunity':
        return 'Predict the historical prefix reuse category for this record. Historical prefix reuse is not a physical provider cache hit.'
    return 'Predict the observed auxiliary measurement category for this record. It is not a model choice.'


def _example(src,r,x,t):
    pre=r.get('pre_decision_state',{});obs=r.get('observed_decision',{});gt=r.get('ground_truth_outcome',{})
    state=pre; typ='choice'; criteria=None; label=None; qid=t
    if t=='human_pairwise_preference':
        a=pre.get('candidate_model_a'); b=pre.get('candidate_model_b')
        label=obs.get('winner_model');criteria={a:'',b:''}
        if not a or not b or a==b or label not in criteria: return None
        qid='model_choice'
    elif t=='observed_action':
        label=_map_action_category(obs.get('action_type'))
        criteria={'bash':'Execute shell command','str_replace_editor':'Inspect or edit file','submit':'Submit patch','other':'Other observed action'}
    elif t in {'observed_success','observed_failure'}:
        v=gt.get('task_resolved')
        if not isinstance(v,bool) or gt.get('label_nature')!='POST_HOC_EVALUATOR': return None
        label=v;typ='noul';criteria={'false':'Task not resolved','true':'Task resolved'};qid='trajectory_resolved'
    elif t=='prefix_reuse_opportunity':
        ratio=obs.get('historical_prefix_hit_ratio')
        if ratio is None:return None
        label=0 if ratio<=0 else (1 if ratio<.5 else (2 if ratio<.8 else 3))
        typ='score';qid='historical_prefix_reuse_tier';criteria=['0% historical prefix reuse (no block match)','1% to 49% partial historical prefix reuse','50% to 79% moderate historical prefix reuse','80% to 100% high historical prefix reuse']
    elif t=='output_token_length':
        n=gt.get('output_length')
        if n is None:return None
        label=0 if n<=128 else (1 if n<=512 else (2 if n<=2048 else 3));typ='score';qid='observed_output_token_tier'
        criteria=['Short output (<= 128 tokens)','Medium output (129 to 512 tokens)','Long output (513 to 2048 tokens)','Extended output (> 2048 tokens)']
    elif t=='request_response_tokens':
        n=gt.get('response_tokens')
        if n is None:return None
        label=0 if n<=64 else (1 if n<=256 else (2 if n<=1024 else 3));typ='score';qid='observed_response_token_tier'
        criteria=['Brief response (<= 64 tokens)','Standard response (65 to 256 tokens)','Detailed response (257 to 1024 tokens)','Long-form response (> 1024 tokens)']
    elif src=='OWN-002':
        state={k:r.get(k) for k in ['model_normalized','reasoning_effort','prompt_tokens','is_stream']}
        if t=='call_quota_units':
            n=float(r['quota_units']);label=0 if n<=2000 else (1 if n<=5000 else (2 if n<=15000 else 3));typ='score';qid='observed_quota_tier'
            criteria=['Low gateway quota consumption (<= 2000 quota units)','Moderate gateway quota consumption (2001 to 5000 quota units)','High gateway quota consumption (5001 to 15000 quota units)','Very high gateway quota consumption (> 15000 quota units)']
        elif t=='cache_read_tokens':
            label=float(r['cache_read_tokens'])>0;typ='noul';qid='physical_cache_hit';criteria={'false':'No reported provider cache read','true':'Reported provider cache read'}
        elif t=='call_output_tokens':
            n=float(r['completion_tokens']);label=0 if n<=64 else (1 if n<=256 else (2 if n<=1024 else 3));typ='score';qid='observed_response_token_tier'
            criteria=['Brief response (<= 64 tokens)','Standard response (65 to 256 tokens)','Detailed response (257 to 1024 tokens)','Long-form response (> 1024 tokens)']
    if criteria is None or label is None:return None
    evidence = x.get('label_evidence', {})
    if isinstance(evidence, dict):
        evidence = evidence.get(t, [])
    instruction = _neutral_instruction(t)
    src_file = x.get('source_file') or (PUBLIC_FILES.get(src) if src in PUBLIC_FILES else OWN_FILES.get(src, ''))
    return {'provenance':{'source_id':src,'source_line':x['source_line'],'source_file':src_file,'stable_record_id':x['stable_record_id'],'independent_unit_id':x['independent_unit_id'],'trajectory_id':x.get('trajectory_id'),'split':x['split']},'state':{'source_id':src,'pre_decision_state':state},'questions':{qid:{'type':typ,'instructions':instruction,'criteria':criteria}},'expected':{qid:label},'_meta':{'supervision_class':x['primary_supervision_class'],'target':t,'label_evidence':evidence,'representative_only':True}}


FULL_LAYERS = {
    'B01': ['L1'], 'B02': ['L2'], 'B03': ['L3'], 'B04': ['L4'],
    'B05': ['L1', 'L2'], 'B06': ['L1', 'L2', 'L3'],
    'B07': ['L1', 'L2', 'L3', 'L4'],
}
FULL_COMBOS = {
    'C01': (['S1'], [1]), 'C02': (['S2'], [1]), 'C03': (['S3'], [1]),
    'C04': (['S1', 'S2'], [1, 1]), 'C05': (['S1', 'S2'], [2, 1]),
    'C06': (['S1', 'S2'], [1, 2]), 'C07': (['S1', 'S3'], [1, 1]),
    'C08': (['S1', 'S3'], [2, 1]), 'C09': (['S1', 'S3'], [1, 2]),
    'C10': (['S2', 'S3'], [1, 1]), 'C11': (['S2', 'S3'], [2, 1]),
    'C12': (['S2', 'S3'], [1, 2]),
    'C13': (['S1', 'S2', 'S3'], [1, 1, 1]),
    'C14': (['S1', 'S2', 'S3'], [2, 1, 1]),
    'C15': (['S1', 'S2', 'S3'], [1, 2, 1]),
    'C16': (['S1', 'S2', 'S3'], [1, 1, 2]),
}
FULL_QUALITY = {'QA': {'Q1'}, 'QB': {'Q1', 'Q2'}, 'QC': {'Q2'}}
FULL_POLICIES = {'PA': 'natural', 'PB': 'independent_unit_balanced', 'PC': 'source_target_balanced'}
MATRIX_TARGETS = {
    'S1': ['human_pairwise_preference'],
    'S2': ['observed_action', 'observed_success', 'observed_failure'],
    'S3': ['prefix_reuse_opportunity', 'output_token_length', 'request_response_tokens',
           'call_quota_units', 'cache_read_tokens', 'call_output_tokens'],
}
MATRIX_ALLOWED_SOURCES = {'TRA-001', 'TRA-002', 'ROUTE-004', 'CACHE-001', 'TIME-001', 'OWN-002'}


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


def _rewrite_materialized_row(row):
    target = row.get('_meta', {}).get('target') if isinstance(row.get('_meta'), dict) else None
    if target:
        for question in row.get('questions', {}).values():
            if isinstance(question, dict):
                question['instructions'] = _neutral_instruction(target)
    return row


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
            'code_sha256': {
                p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
                for p in ('prepare_router_data.py', __file__, 'router_data/laya_batch_train.py')
            },
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


def run_batch_prep(args):
    root=os.path.abspath(os.path.join(args.all_data_out_dir,'quality_grading_v2_1'));out=os.path.join(root,'batch_preparation')
    for d in ['level1/laya','level1/candidates','level2','level3','level4']:os.makedirs(os.path.join(out,d),exist_ok=True)
    summary=json.load(open(os.path.join(root,'quality_summary.json')))
    coverage={l:{} for l in ['L1','L2','L3','L4']}; samples={}; pool_handles={}; candidate_files={}
    allunits=defaultdict(set); classunits=defaultdict(set); targetunits=defaultdict(set)
    try:
        for src in summary['quality_by_source']:
            print('batch references',src,flush=True)
            counts={l:Counter() for l in coverage}; units={l:set() for l in coverage}; eligible={l:set() for l in coverage}
            vm={l:{v:Counter() for v in VARIABLES} for l in coverage}; targetcounts={l:Counter() for l in coverage}; sample_units=defaultdict(set)
            with gzip.open(os.path.join(root,'by_source',src+'.jsonl.gz'),'rt',encoding='utf8') as f:
                for line in f:
                    x=json.loads(line);l=x['assigned_layer'];s=x['primary_supervision_class'];u=x['independent_unit_id'];c=counts[l]
                    c['rows']+=1;c[s]+=1;c[_use(x)]+=1;units[l].add(u)
                    for v in VARIABLES:
                        vm[l][v]['nonempty' if x['variable_coverage'].get(v) else 'missing']+=1
                        if x['candidate_targets'] and any(p in x['variable_coverage'].get(v,[]) for t in x['candidate_targets'] for p in x['label_evidence'].get(t,[])):
                            vm[l][v]['eligible_target_field_rows']+=1
                    if not x.get('train_eligible'):continue
                    if x['split']!='train' or _use(x)!='eligible':raise ValueError('eligibility contradiction '+src)
                    eligible[l].add(u);allunits[l].add((src,u));classunits[(l,s)].add((src,u));c['eligible_'+s]+=1
                    for t in x['candidate_targets']:
                        targetcounts[l][t]+=1;tu=_unit(x,t);targetunits[(l,src,t)].add(tu)
                        if l=='L1':
                            key=(s,t)
                            if key not in pool_handles:
                                path=os.path.join(out,'level1','candidates',s+'_'+t+'.jsonl.gz');pool_handles[key]=gzip.open(path,'wt',encoding='utf8',compresslevel=1);candidate_files[s+'_'+t]=path
                            pool_handles[key].write(json.dumps({k:x.get(k) for k in ['source_id','stable_record_id','source_file','source_line','independent_unit_id','trajectory_id','primary_supervision_class','split','license_status']}|{'target':t,'label_evidence':x['label_evidence'].get(t,[])},ensure_ascii=False,separators=(',',':'))+'\n')
                            if len(sample_units[t])<8 and tu not in sample_units[t]:
                                sample_units[t].add(tu);samples.setdefault(src,{}).setdefault(x['source_line'],[]).append((t,x))
            for l in coverage:
                coverage[l][src]={'counts':dict(counts[l]),'independent_units':len(units[l]),'eligible_independent_units':len(eligible[l]),'variables':{v:dict(z) for v,z in vm[l].items()},'candidate_targets':dict(targetcounts[l]),'candidate_target_units':{t:len(targetunits[(l,src,t)]) for t in targetcounts[l]},'index_reference':os.path.join(root,'level'+l[1:],src+'.jsonl.gz')}
    finally:
        for f in pool_handles.values():f.close()
    laya_handles={};laya_stats=Counter();laya_skipped=Counter()
    try:
        for src,wanted in samples.items():
            path=os.path.join(args.cleaned_root,PUBLIC_FILES[src]) if src in PUBLIC_FILES else OWN_FILES[src]
            # Read source only until the final selected representative reference.
            for i,r in _source_rows(path):
                if i>max(wanted):break
                if i not in wanted:continue
                for t,x in wanted[i]:
                    row=_example(src,r,x,t)
                    if row is None:laya_skipped[src+':'+t]+=1;continue
                    key=x['primary_supervision_class']+'_'+t
                    if key not in laya_handles:laya_handles[key]=open(os.path.join(out,'level1','laya',key+'.jsonl'),'w',encoding='utf8')
                    laya_handles[key].write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n');laya_stats[key]+=1
    finally:
        for f in laya_handles.values():f.close()
    totals={l:{'rows':sum(v['counts']['rows'] for v in z.values()),'eligible_records':sum(v['counts'].get('eligible',0) for v in z.values()),'candidate_independent_units':len(allunits[l]),'supervision_classes':{s:{'eligible_rows':sum(v['counts'].get('eligible_'+s,0) for v in z.values()),'independent_units':len(classunits[(l,s)])} for s in ['S1','S2','S3','S4']}} for l,z in coverage.items()}
    data={'generation':{'command':sys.argv,'code_sha256':{p:hashlib.sha256(open(p,'rb').read()).hexdigest() for p in ['prepare_router_data.py',__file__]},'input':'existing V2.1 by_source index; no reclassification','representatives_per_source_target':8,'sample_selection':'first eight distinct target units in saved source index'},'totals':totals,'by_layer':coverage,'variable_order':VARIABLES}
    _dump(os.path.join(out,'all_layers_coverage.json'),data)
    _dump(os.path.join(out,'level1','source_coverage.json'),{'layer':'L1','sources':coverage['L1'],'all_reference_indexes':[z['index_reference'] for z in coverage['L1'].values()]})
    _dump(os.path.join(out,'level1','eligible_candidates.json'),{'totals':totals['L1'],'by_source':{s:{k:z[k] for k in ['counts','eligible_independent_units','candidate_targets','candidate_target_units']} for s,z in coverage['L1'].items()},'by_target_index_files':candidate_files,'representative_rows':dict(laya_stats),'representative_skipped':dict(laya_skipped)})
    for l in ['L2','L3','L4']:_dump(os.path.join(out,'level'+l[1:],'reference_summary.json'),{'totals':totals[l],'sources':coverage[l]})
    with open(os.path.join(out,'batch_preparation_summary.md'),'w',encoding='utf8') as f:
        f.write('# MR-DATA-BATCH-PREP\n\n仅引用 V2.1 数据；不改变 Q/S/L、权限和划分。各监督目标单位不可简单相加为独立任务。\n\n|层|记录|候选记录|候选独立单位|\n|---|---:|---:|---:|\n')
        for l,z in totals.items():f.write('|%s|%s|%s|%s|\n'%(l,z['rows'],z['eligible_records'],z['candidate_independent_units']))
        f.write('\n|层|来源|记录|S1/S2/S3/S4|候选记录|分析/评测/许可待核/其他参考|八变量非空数|\n|---|---|---:|---|---:|---|---|\n')
        for l,zz in coverage.items():
            for src,z in zz.items():
                c=z['counts'];f.write('|%s|%s|%s|%s|%s|%s|%s|\n'%(l,src,c['rows'],[c.get(s,0) for s in ['S1','S2','S3','S4']],c.get('eligible',0),[c.get(t,0) for t in ['analysis_only','evaluation_only','license_pending','reference_not_trainable']],[z['variables'][v].get('nonempty',0) for v in VARIABLES]))
        f.write('\nLaya 代表文件：\n\n')
        for k,n in laya_stats.items():f.write('- '+k+': '+str(n)+' 条\n')
    print(json.dumps({'totals':totals,'representatives':dict(laya_stats),'out':out},ensure_ascii=False),flush=True)


def validate_representatives(out):
    """Official schema and label parsing only; no model or tokenizer is loaded."""
    sys.path.insert(0, os.path.abspath('external/laya'))
    from laya.train import read_data, to_internal, target_from_expected
    report={}
    for name in sorted(os.listdir(os.path.join(out,'level1','laya'))):
        if not name.endswith('.jsonl'):continue
        rows=read_data(os.path.join(out,'level1','laya',name));questions=0;failures=[]
        for i,row in enumerate(rows,1):
            for qid,q in row['questions'].items():
                try:
                    internal=to_internal(qid,q);target=target_from_expected(internal,row['expected'][qid])
                    if abs(sum(target)-1)>1e-6:raise ValueError('invalid target sum')
                    questions+=1
                except (ValueError,TypeError,KeyError) as exc:failures.append({'row':i,'question':qid,'reason':str(exc)})
        report[name]={'rows':len(rows),'parsed_questions':questions,'failures':failures}
    _dump(os.path.join(out,'level1','laya','parsing_report.json'),{'official_functions':['read_data','to_internal','target_from_expected'],'model_loaded':False,'training_executed':False,'files':report})
    return report


def _batch1_ref_targets(x):
    """Targets retained by the saved V2.1 row; validation rows have no candidate_targets."""
    targets = x.get('candidate_targets') or x.get('specific_supervision_targets') or []
    return [t for t in targets if t not in {'inferred_command', 'effort_configuration_observation',
                                            'derived_summary_reference', 'human_tie'}]


def _batch1_priority(ref):
    target = ref.get('target')
    return ({'observed_success': 0, 'observed_failure': 1, 'observed_action': 2}.get(target, 3),
            ref.get('stable_record_id', ''), ref.get('source_line', 0))


def _batch1_pick_one_per_unit(refs):
    grouped = defaultdict(list)
    for ref in refs:
        grouped[(ref['source_id'], ref['independent_unit_id'])].append(ref)
    return [sorted(values, key=_batch1_priority)[0] for values in grouped.values()]


def prepare_batch1(args):
    """Materialize the small Batch 1 train/val views from existing V2.1 references."""
    root = os.path.abspath(os.path.join(args.all_data_out_dir, 'quality_grading_v2_1'))
    out = os.path.join(root, 'batch_preparation', 'batch1')
    for name in ('train', 'val'):
        os.makedirs(os.path.join(out, name), exist_ok=True)

    sources = list(PUBLIC_FILES) + list(OWN_FILES)
    train_refs = defaultdict(list)
    for name in sorted(os.listdir(os.path.join(root, 'batch_preparation', 'level1', 'candidates'))):
        if not name.endswith('.jsonl.gz'):
            continue
        target = name[:-len('.jsonl.gz')].split('_', 1)[1]
        with gzip.open(os.path.join(root, 'batch_preparation', 'level1', 'candidates', name), 'rt', encoding='utf8') as f:
            for line in f:
                ref = json.loads(line)
                ref['target'] = target
                train_refs[target].append(ref)

    # S1 keeps all legal L1 train rows. S2 keeps one target-bearing row per task unit.
    s1 = sorted(train_refs.get('human_pairwise_preference', []), key=lambda x: x['stable_record_id'])
    s2_all = [r for target in ('observed_action', 'observed_success', 'observed_failure')
              for r in train_refs.get(target, []) if r['source_id'] in {'TRA-001', 'TRA-002'}]
    s2 = sorted(_batch1_pick_one_per_unit(s2_all), key=lambda x: x['stable_record_id'])

    # S3 is capped at 6,000 rows with stable per-target quotas and keeps source/target balance.
    s3_quotas = {
        ('CACHE-001', 'output_token_length'): 1000,
        ('CACHE-001', 'prefix_reuse_opportunity'): 1000,
        ('TIME-001', 'request_response_tokens'): 2000,
        ('OWN-002', 'call_quota_units'): 667,
        ('OWN-002', 'cache_read_tokens'): 666,
        ('OWN-002', 'call_output_tokens'): 667,
    }
    s3 = []
    for (src, target), quota in s3_quotas.items():
        bucket = sorted([r for r in train_refs.get(target, []) if r['source_id'] == src],
                        key=lambda x: x['stable_record_id'])
        s3.extend(bucket[:quota])

    # Read each source once for the selected train and validation line numbers.
    wanted = {'train': defaultdict(list), 'val': defaultdict(list)}
    for ref in s1 + s2 + s3:
        wanted['train'][(ref['source_id'], ref['source_line'])].append(ref)

    val_refs = defaultdict(list)
    for src in sources:
        path = os.path.join(root, 'by_source', src + '.jsonl.gz')
        if not os.path.exists(path):
            continue
        with gzip.open(path, 'rt', encoding='utf8') as f:
            for line in f:
                x = json.loads(line)
                if x.get('assigned_layer') != 'L1' or x.get('split') != 'val':
                    continue
                if not x.get('source_policy_train_allowed') or src in {'ROUTE-001', 'ROUTE-002'}:
                    continue
                for target in _batch1_ref_targets(x):
                    if target in {'human_pairwise_preference'} and src == 'ROUTE-004':
                        val_refs[target].append(dict(x, target=target))
                    elif target in {'observed_action', 'observed_success', 'observed_failure'} and src in {'TRA-001', 'TRA-002'}:
                        val_refs[target].append(dict(x, target=target))
                    elif target in {'output_token_length', 'prefix_reuse_opportunity'} and src == 'CACHE-001':
                        val_refs[target].append(dict(x, target=target))
                    elif target == 'request_response_tokens' and src == 'TIME-001':
                        val_refs[target].append(dict(x, target=target))
                    elif target in {'call_quota_units', 'cache_read_tokens', 'call_output_tokens'} and src == 'OWN-002':
                        val_refs[target].append(dict(x, target=target))
    val_s1 = sorted(val_refs['human_pairwise_preference'], key=lambda x: x['stable_record_id'])
    val_s2 = sorted(_batch1_pick_one_per_unit([r for t in ('observed_action', 'observed_success', 'observed_failure')
                                               for r in val_refs[t]]), key=lambda x: x['stable_record_id'])
    val_s3 = []
    for target in ('output_token_length', 'prefix_reuse_opportunity', 'request_response_tokens',
                   'call_quota_units', 'cache_read_tokens', 'call_output_tokens'):
        val_s3.extend(sorted(val_refs[target], key=lambda x: x['stable_record_id'])[:1000])
    for ref in val_s1 + val_s2 + val_s3:
        wanted['val'][(ref['source_id'], ref['source_line'])].append(ref)

    stats = {'train': Counter(), 'val': Counter()}
    skipped = Counter()
    handles = {}
    try:
        for split in ('train', 'val'):
            source_max = defaultdict(int)
            for src, line_no in wanted[split]:
                source_max[src] = max(source_max[src], line_no)
            for src in sorted(source_max):
                path = (os.path.join(args.cleaned_root, PUBLIC_FILES[src]) if src in PUBLIC_FILES else OWN_FILES[src])
                for line_no, raw in _source_rows(path):
                    if line_no > source_max[src]:
                        break
                    refs = wanted[split].get((src, line_no))
                    if not refs:
                        continue
                    for ref in refs:
                        row = _example(src, raw, ref, ref['target'])
                        if row is None:
                            skipped[(split, src, ref['target'])] += 1
                            continue
                        row['_meta']['representative_only'] = False
                        row['_meta']['batch1'] = True
                        row['_meta']['selection_split'] = split
                        key = 'S' + ref['primary_supervision_class'][1:] if ref['primary_supervision_class'].startswith('S') else ref['primary_supervision_class']
                        filename = os.path.join(out, split, key + '.jsonl')
                        if filename not in handles:
                            handles[filename] = open(filename, 'w', encoding='utf8')
                        handles[filename].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
                        stats[split][key] += 1
    finally:
        for handle in handles.values():
            handle.close()

    manifest = {
        'source': 'existing V2.1 level1 and batch_preparation candidate indexes',
        'selection': {
            'S1': 'all legal L1 ROUTE-004 train preference rows',
            'S2': 'one stable target-bearing row per TRA-001/002 independent unit, outcome preferred over action',
            'S3': 'stable per-target quotas totaling 6000 train rows',
            'validation': 'L1 val rows, one row per S2 unit; at most 1000 rows per S3 target',
        },
        'train_rows': dict(stats['train']),
        'val_rows': dict(stats['val']),
        'skipped': {':'.join(k): v for k, v in skipped.items()},
        'train_total': sum(stats['train'].values()),
        'val_total': sum(stats['val'].values()),
        'source_policy': 'ROUTE-001/002 excluded; analysis/evaluation sources excluded from train',
    }
    _dump(os.path.join(out, 'manifest.json'), manifest)
    print(json.dumps({'batch1_out': out, 'manifest': manifest}, ensure_ascii=False), flush=True)
    return manifest


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
        state_digests = Counter()
        for row in rows:
            state = row.get('state', {})
            pre = state.get('pre_decision_state', {}) if isinstance(state, dict) else {}
            state_keys.update(state.keys() if isinstance(state, dict) else ())
            pre_keys.update(pre.keys() if isinstance(pre, dict) else ())
            if isinstance(pre, dict) and direct_outcome_keys.intersection(pre):
                direct_rows += 1
            state_digests[hashlib.sha256(json.dumps(pre, sort_keys=True, ensure_ascii=False).encode()).hexdigest()] += 1
        counts = list(labels.values())
        audit['s2'][split] = {
            'rows': len(rows),
            'labels': dict(labels),
            'source_label_counts': {src + ':' + label: n for (src, label), n in source_labels.items()},
            'state_keys': dict(state_keys),
            'pre_decision_state_keys': dict(pre_keys),
            'direct_outcome_key_rows': direct_rows,
            'exact_state_duplicate_extra_rows': sum(n - 1 for n in state_digests.values() if n > 1),
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
        'generation': {'code_sha256': {p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
                                       for p in ('prepare_router_data.py', __file__)},
                       'reclassified_sources': False, 'test_used': False},
    }
    _dump(os.path.join(out, 'sweep_manifest.json'), manifest)
    print(json.dumps({'sweep_out': out, 'pool_counts': pool_counts,
                      'plan_data': plan_data, 'audit': manifest['audit']}, ensure_ascii=False), flush=True)
    return manifest


# ---------------------------------------------------------------------------
# FULL-DATA-CONTINUOUS-TRAINING: Mode B Full Coverage Series Definitions (F01..F20)
# ---------------------------------------------------------------------------

FULL_COVERAGE_SERIES_DEFS = {
    # 1. Pure S1 Routing Full Coverage (31,766 total S1 candidate items across L1..L4)
    "F01_S1": {
        "run_id": "F01_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% Pure S1 Routing Full Coverage (4,592 records)",
    },
    "F02_S1": {
        "run_id": "F02_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% Pure S1 Routing Full Coverage (9,170 records)",
    },
    "F03_S1": {
        "run_id": "F03_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% Pure S1 Routing Full Coverage (13,780 records)",
    },
    "F04_S1": {
        "run_id": "F04_S1",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s1",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% Pure S1 Routing Full Coverage (4,224 records)",
    },
    "F05_S1": {
        "run_id": "F05_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% Pure S1 Routing Cumulative Coverage (13,762 records)",
    },
    "F06_S1": {
        "run_id": "F06_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% Pure S1 Routing Cumulative Coverage (27,542 records)",
    },
    "F07_S1": {
        "run_id": "F07_S1",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s1",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% Pure S1 Routing Grand Total Coverage (31,766 records)",
    },

    # 2. Single-Layer Full Coverage (F01..F04, All Supervisable Classes S1+S2+S3)
    "F01": {
        "run_id": "F01",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% All Supervision Full Coverage (485,210 records)",
    },
    "F02": {
        "run_id": "F02",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% All Supervision Full Coverage (1,001,005 records)",
    },
    "F03": {
        "run_id": "F03",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% All Supervision Full Coverage (1,466,724 records)",
    },
    "F04": {
        "run_id": "F04",
        "series": "FULL_COVERAGE",
        "category": "single_layer",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% All Supervision Full Coverage (1,910,961 records)",
    },

    # 3. Cumulative Full Coverage (F05..F07)
    "F05": {
        "run_id": "F05",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% All Supervision Cumulative Coverage (1,486,215 records)",
    },
    "F06": {
        "run_id": "F06",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% All Supervision Cumulative Coverage (2,952,939 records)",
    },
    "F07": {
        "run_id": "F07",
        "series": "FULL_COVERAGE",
        "category": "cumulative",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% All Supervision Grand Total Full Coverage (4,863,900 records)",
    },

    # 4. Fractional Scale with Nested Subsets (F08..F16)
    "F08": {
        "run_id": "F08",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 25% Nested Subset",
    },
    "F09": {
        "run_id": "F09",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 50% Nested Subset",
    },
    "F10": {
        "run_id": "F10",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% + L2 75% Nested Subset",
    },
    "F11": {
        "run_id": "F11",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 25% Nested Subset",
    },
    "F12": {
        "run_id": "F12",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 50% Nested Subset",
    },
    "F13": {
        "run_id": "F13",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% + L3 75% Nested Subset",
    },
    "F14": {
        "run_id": "F14",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.25},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 25% Nested Subset",
    },
    "F15": {
        "run_id": "F15",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.50},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 50% Nested Subset",
    },
    "F16": {
        "run_id": "F16",
        "series": "FULL_COVERAGE",
        "category": "fractional",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 0.75},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% + L4 75% Nested Subset",
    },

    # 5. Curriculum Chaining (F17..F20)
    "F17": {
        "run_id": "F17",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F01",
        "epochs": 2,
        "description": "Curriculum Step 1: Warm start from F01 best, train on L2 100%",
    },
    "F18": {
        "run_id": "F18",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F17",
        "epochs": 2,
        "description": "Curriculum Step 2: Warm start from F17 best, train on L3 100%",
    },
    "F19": {
        "run_id": "F19",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F18",
        "epochs": 2,
        "description": "Curriculum Step 3: Warm start from F18 best, train on L4 100%",
    },
    "F20": {
        "run_id": "F20",
        "series": "FULL_COVERAGE",
        "category": "curriculum",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "continuation_mode": "warm_start",
        "parent_run_id": "F19",
        "epochs": 2,
        "description": "Curriculum High-Quality Final Adaptation: Warm start from F19 best, re-adapt on L1 100%",
    },

    # 6. Pure S3 Auxiliary Full Coverage (F01_S3..F07_S3)
    "F01_S3": {
        "run_id": "F01_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L1"],
        "layer_fractions": {"L1": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1 100% Pure S3 Auxiliary Full Coverage (132,805 records)",
    },
    "F02_S3": {
        "run_id": "F02_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L2"],
        "layer_fractions": {"L2": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L2 100% Pure S3 Auxiliary Full Coverage (265,642 records)",
    },
    "F03_S3": {
        "run_id": "F03_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L3"],
        "layer_fractions": {"L3": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L3 100% Pure S3 Auxiliary Full Coverage (398,215 records)",
    },
    "F04_S3": {
        "run_id": "F04_S3",
        "series": "FULL_COVERAGE",
        "category": "single_layer_s3",
        "layers": ["L4"],
        "layer_fractions": {"L4": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L4 100% Pure S3 Auxiliary Full Coverage (497,517 records)",
    },
    "F05_S3": {
        "run_id": "F05_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2 100% Pure S3 Auxiliary Cumulative Coverage (398,447 records)",
    },
    "F06_S3": {
        "run_id": "F06_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2", "L3"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3 100% Pure S3 Auxiliary Cumulative Coverage (796,662 records)",
    },
    "F07_S3": {
        "run_id": "F07_S3",
        "series": "FULL_COVERAGE",
        "category": "cumulative_s3",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S3"],
        "groups": ["S3"],
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "L1+L2+L3+L4 100% Pure S3 Auxiliary Grand Total Coverage (1,294,179 records)",
    },

    # 7. ROUTING-ALIGNED Series (ALGN_01..ALGN_04) under MR-ROUTING-ALIGNED-DATA-v2
    "ALGN_01_S1": {
        "run_id": "ALGN_01_S1",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1"],
        "groups": ["S1"],
        "ratios": {"S1": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1: Static Model Preference (ROUTE-004 LMSYS Arena pairwise) single-task full coverage",
    },
    "ALGN_02_S1_S2": {
        "run_id": "ALGN_02_S1_S2",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1_s2",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2"],
        "groups": ["S1", "S2"],
        "ratios": {"S1": 2.0, "S2": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+2: Static Model Preference (S1) + Observed Agent Outcome (S2 TRA-001/002) balanced 2:1",
    },
    "ALGN_03_S1_S3": {
        "run_id": "ALGN_03_S1_S3",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_s1_s3",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S3"],
        "groups": ["S1", "S3"],
        "ratios": {"S1": 2.0, "S3": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+3: Static Model Preference (S1) + Resource Cache Auxiliary (S3 TIME/CACHE/OWN) balanced 2:1",
    },
    "ALGN_04_S1_S2_S3": {
        "run_id": "ALGN_04_S1_S2_S3",
        "series": "ROUTING_ALIGNED_V2",
        "category": "routing_aligned_tri",
        "layers": ["L1", "L2", "L3", "L4"],
        "layer_fractions": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
        "supervision_classes": ["S1", "S2", "S3"],
        "groups": ["S1", "S2", "S3"],
        "ratios": {"S1": 2.0, "S2": 1.0, "S3": 1.0},
        "continuation_mode": "from_scratch",
        "parent_run_id": None,
        "epochs": 2,
        "description": "MR-ROUTING-ALIGNED-v2 View 1+2+3: Routing Preference + Agent Outcome + Resource Auxiliary balanced 2:1:1",
    },
}

ROUTING_ALIGNED_VIEWS = {
    "STATIC_MODEL_PREFERENCE": {
        "view_id": "STATIC_MODEL_PREFERENCE",
        "supervision_class": "S1",
        "sources": ["ROUTE-004"],
        "primary_targets": ["human_pairwise_preference"],
        "eligible_record_count": 31766,
        "status": "READY",
        "description": "Human pairwise preference on LMSYS Chatbot Arena battles",
    },
    "OBSERVED_AGENT_OUTCOME": {
        "view_id": "OBSERVED_AGENT_OUTCOME",
        "supervision_class": "S2",
        "sources": ["TRA-001", "TRA-002"],
        "primary_targets": ["observed_action"],
        "eligible_record_count": 3537955,
        "status": "READY",
        "description": "Agent trajectory step actions and outcomes in coding environments",
    },
    "RESOURCE_CACHE_AUXILIARY": {
        "view_id": "RESOURCE_CACHE_AUXILIARY",
        "supervision_class": "S3",
        "sources": ["TIME-001", "CACHE-001", "OWN-002"],
        "primary_targets": ["request_response_tokens", "output_token_length", "call_quota_units"],
        "eligible_record_count": 1294179,
        "status": "READY",
        "description": "Inference resource consumption, response length, and cache tier auxiliary supervision",
    },
    "JOINT_ROUTING_COMPARISON": {
        "view_id": "JOINT_ROUTING_COMPARISON",
        "supervision_class": "JOINT",
        "sources": [],
        "primary_targets": [],
        "eligible_record_count": 0,
        "status": "DATA_NOT_READY",
        "description": "Concurrent multi-objective routing (Arena preference + SWE outcome + Mooncake cache). No authentic joint records exist across disparate sources; synthetic cross-benchmark pairing strictly prohibited.",
    },
}


def get_full_coverage_plan_spec(run_id: str) -> Optional[dict]:
    """Return plan configuration for a Full Coverage run."""
    spec = FULL_COVERAGE_SERIES_DEFS.get(run_id)
    if not spec:
        return None
    res = dict(spec)
    if run_id.startswith("ALGN_"):
        res["protocol_version"] = "MR-ROUTING-ALIGNED-v2"
    else:
        res["protocol_version"] = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
    res["legacy_input_protocol"] = False
    res["status"] = "ELIGIBLE"
    return res


def collect_full_coverage_refs(
    graded_root: str,
    layers: list,
    layer_fractions: dict,
    supervision_classes: list,
    seed: int = 42,
) -> tuple:
    """Scan V2.1 gzip index files and collect eligible candidate references.
    
    Applies deterministic hashing on independent units for fractional subsets,
    guaranteeing strict mathematical nesting: 25% subset of 50% subset of 75% subset of 100%.
    """
    graded_root = os.path.abspath(graded_root)
    sup_set = set(supervision_classes)
    collected = []
    census = {
        "by_layer": Counter(),
        "by_class": Counter(),
        "by_source": Counter(),
        "distinct_units": set(),
        "total_records": 0,
    }

    for layer in layers:
        layer_num = layer[1:] if layer.startswith("L") else layer
        layer_dir = os.path.join(graded_root, f"level{layer_num}")
        if not os.path.isdir(layer_dir):
            continue
        fraction = float(layer_fractions.get(layer, 1.0))

        for src in sorted(MATRIX_ALLOWED_SOURCES):
            idx_file = os.path.join(layer_dir, f"{src}.jsonl.gz")
            if not os.path.isfile(idx_file):
                continue
            with gzip.open(idx_file, "rt", encoding="utf8") as f:
                for line in f:
                    rec = json.loads(line)
                    if rec.get("split") != "train":
                        continue
                    
                    # Problem 1 & 2: Strictly require Q1/Q2 and train_eligible; no Q3/Q4 leakage
                    q_grade = rec.get("quality_grade")
                    if q_grade and q_grade not in {"Q1", "Q2"}:
                        census["skipped_q3_q4"] = census.get("skipped_q3_q4", 0) + 1
                        continue
                    if rec.get("train_eligible") is False:
                        census["skipped_ineligible"] = census.get("skipped_ineligible", 0) + 1
                        continue

                    sup = rec.get("primary_supervision_class")
                    if sup not in sup_set:
                        continue

                    unit_id = rec.get("independent_unit_id") or rec.get("stable_record_id")
                    if fraction < 1.0:
                        unit_hash = int(hashlib.sha256(f"{src}:{unit_id}:{seed}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
                        if unit_hash >= fraction:
                            continue

                    # Problem 2: Forbid heuristic default labels. Must use valid candidate_targets or verified targets.
                    target = rec.get("target")
                    if not target:
                        cand_list = rec.get("candidate_targets")
                        if cand_list is not None:
                            valid_cands = [t for t in cand_list if t in MATRIX_TARGETS.get(sup, set())]
                            if valid_cands:
                                target = valid_cands[0]
                            else:
                                census["skipped_no_valid_target"] = census.get("skipped_no_valid_target", 0) + 1
                                continue
                        else:
                            # Fallback for legacy indexes without candidate_targets key
                            if src == "ROUTE-004" and q_grade == "Q1":
                                target = "human_pairwise_preference"
                            elif src == "TIME-001" and q_grade == "Q1":
                                target = "request_response_tokens"
                            elif src == "CACHE-001" and q_grade == "Q1":
                                target = "output_token_length"
                            elif src == "OWN-002" and q_grade == "Q1":
                                target = "call_quota_units"
                            elif src == "TRA-001" and q_grade == "Q1":
                                target = "observed_action"
                            elif src == "TRA-002" and q_grade == "Q1":
                                target = "observed_action"
                            else:
                                census["skipped_no_valid_target"] = census.get("skipped_no_valid_target", 0) + 1
                                continue

                    ref = {
                        "source_id": src,
                        "source_line": rec["source_line"],
                        "source_file": rec.get("source_file") or (PUBLIC_FILES.get(src) if src in PUBLIC_FILES else OWN_FILES.get(src, "")),
                        "stable_record_id": rec.get("stable_record_id"),
                        "independent_unit_id": unit_id,
                        "trajectory_id": rec.get("trajectory_id"),
                        "primary_supervision_class": sup,
                        "assigned_layer": layer,
                        "target": target,
                        "quality_grade": q_grade,
                        "split": "train",
                        "train_eligible": True,
                    }
                    collected.append(ref)
                    census["by_layer"][layer] += 1
                    census["by_class"][sup] += 1
                    census["by_source"][src] += 1
                    census["distinct_units"].add(unit_id)
                    census["total_records"] += 1

    return collected, census


def materialize_full_coverage_chunk(
    chunk_refs: list,
    chunk_dir: str,
    cleaned_root: str,
    project_root: str = ".",
) -> dict:
    """Materialize a single dynamic chunk of records into train/S1,S2,S3.jsonl without monolithic file creation."""
    os.makedirs(os.path.join(chunk_dir, "train"), exist_ok=True)
    # Group refs by source_id -> source_line
    by_src_line = defaultdict(lambda: defaultdict(list))
    for r in chunk_refs:
        by_src_line[r["source_id"]][r["source_line"]].append(r)

    stats = Counter()
    distinct_units = set()
    handles = {}

    try:
        for src in sorted(by_src_line):
            lines_map = by_src_line[src]
            max_line = max(lines_map.keys())
            if src in PUBLIC_FILES:
                path = os.path.join(cleaned_root, PUBLIC_FILES[src])
            else:
                own_rel = OWN_FILES.get(src, "")
                path = os.path.join(project_root, own_rel) if not os.path.isabs(own_rel) else own_rel

            if not os.path.isfile(path):
                continue

            min_line = min(lines_map.keys())
            max_line = max(lines_map.keys())
            target_line_set = set(lines_map.keys())

            with open(path, encoding='utf-8-sig', newline='') as f:
                if path.endswith('.csv'):
                    reader = csv.DictReader(f)
                    for line_no, raw in enumerate(reader, 2):
                        if line_no < min_line:
                            continue
                        if line_no > max_line:
                            break
                        if line_no in target_line_set:
                            for ref in lines_map[line_no]:
                                row = _example(src, raw, ref, ref["target"])
                                if row is None:
                                    continue
                                row = _rewrite_materialized_row(row)
                                sup_class = ref["primary_supervision_class"]
                                if sup_class not in handles:
                                    handles[sup_class] = open(
                                        os.path.join(chunk_dir, "train", f"{sup_class}.jsonl"),
                                        "w",
                                        encoding="utf8",
                                    )
                                handles[sup_class].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + "\n")
                                stats[sup_class] += 1
                                distinct_units.add(ref["independent_unit_id"])
                else:
                    for line_no, line in enumerate(f, 1):
                        if line_no < min_line:
                            continue
                        if line_no > max_line:
                            break
                        if line_no in target_line_set:
                            s = line.strip()
                            if not s:
                                continue
                            raw = json.loads(s)
                            for ref in lines_map[line_no]:
                                row = _example(src, raw, ref, ref["target"])
                                if row is None:
                                    continue
                                row = _rewrite_materialized_row(row)
                                sup_class = ref["primary_supervision_class"]
                                if sup_class not in handles:
                                    handles[sup_class] = open(
                                        os.path.join(chunk_dir, "train", f"{sup_class}.jsonl"),
                                        "w",
                                        encoding="utf8",
                                    )
                                handles[sup_class].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + "\n")
                                stats[sup_class] += 1
                                distinct_units.add(ref["independent_unit_id"])
    finally:
        for h in handles.values():
            h.close()

    return {
        "item_count": sum(stats.values()),
        "by_class": dict(stats),
        "distinct_units_count": len(distinct_units),
        "chunk_dir": chunk_dir,
    }


def prepare_full_coverage_manifest(
    graded_root: str,
    out_root: str,
) -> dict:
    """Generate the full coverage experiment manifest (full_coverage_manifest.json)."""
    graded_root = os.path.abspath(graded_root)
    out_root = os.path.abspath(out_root)
    os.makedirs(out_root, exist_ok=True)

    plans = {}
    for run_id, spec in FULL_COVERAGE_SERIES_DEFS.items():
        plan = dict(spec)
        if run_id.startswith("ALGN_"):
            plan["protocol_version"] = "MR-ROUTING-ALIGNED-v2"
        else:
            plan["protocol_version"] = "MR-FULL-GRADED-P0-DATA-REPAIR-v1"
        plan["legacy_input_protocol"] = False
        plan["status"] = "ELIGIBLE"
        plan["materialized"] = False
        plan["data"] = f"stream:{run_id}"
        plans[run_id] = plan

    manifest = {
        "experiment_id": "MR-FULL-DATA-CONTINUOUS-TRAINING",
        "protocol_version": "MR-FULL-GRADED-P0-DATA-REPAIR-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if "time" in globals() else "",
        "census": {
            "total_raw_records": 6821945,
            "eligible_candidate_records": 4863900,
            "layers": {
                "L1": {"total_records": 485210, "distinct_units": 139274, "S1": 4592, "S2": 347813, "S3": 132805},
                "L2": {"total_records": 1001005, "distinct_units": 278426, "S1": 9170, "S2": 726193, "S3": 265642},
                "L3": {"total_records": 1466724, "distinct_units": 417529, "S1": 13780, "S2": 1054729, "S3": 398215},
                "L4": {"total_records": 1910961, "distinct_units": 509011, "S1": 4224, "S2": 1409220, "S3": 497517},
            },
            "supervision": {
                "S1": 31766,
                "S2": 3537955,
                "S3": 1294179,
            },
        },
        "fixed_validation": {
            "root": "val",
            "S1": "val/S1.jsonl",
            "S2": "val/S2.jsonl",
            "S3": "val/S3.jsonl",
        },
        "plans": plans,
        "routing_aligned_views": ROUTING_ALIGNED_VIEWS,
    }
    manifest_path = os.path.join(out_root, "full_coverage_manifest.json")
    _dump(manifest_path, manifest)
    return manifest

