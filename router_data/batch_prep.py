"""Prepare batch references and small typed Laya examples from saved V2.1 indexes."""
import csv
import gzip
import json
import os
import sys
import hashlib
import shutil
import itertools
from collections import Counter, defaultdict
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
    return {'provenance':{'source_id':src,'source_line':x['source_line'],'source_file':x['source_file'],'stable_record_id':x['stable_record_id'],'independent_unit_id':x['independent_unit_id'],'trajectory_id':x.get('trajectory_id'),'split':x['split']},'state':{'source_id':src,'pre_decision_state':state},'questions':{qid:{'type':typ,'instructions':'Predict this source-specific observed target: '+t+'. Observed actions are not optimal actions; prefix reuse is not physical cache hit.','criteria':criteria}},'expected':{qid:label},'_meta':{'supervision_class':x['primary_supervision_class'],'target':t,'label_evidence':evidence,'representative_only':True}}


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


def _matrix_materialize(args, out, run_id, refs_by_target, groups, val_root):
    wanted = defaultdict(lambda: defaultdict(list))
    for target, refs in refs_by_target.items():
        for ref in refs:
            wanted[ref['source_id']][ref['source_line']].append((target, ref))
    handles = {}
    stats = Counter()
    try:
        for src, lines in wanted.items():
            path = (os.path.join(args.cleaned_root, PUBLIC_FILES[src])
                    if src in PUBLIC_FILES else OWN_FILES[src])
            max_line = max(lines)
            for line_no, raw in _source_rows(path):
                if line_no > max_line: break
                for target, ref in lines.get(line_no, []):
                    row = _example(src, raw, ref, target)
                    if row is None: continue
                    s = ref['primary_supervision_class']
                    if s not in groups: continue
                    if s not in handles:
                        handles[s] = open(os.path.join(out, 'data', run_id, 'train', s + '.jsonl'), 'w', encoding='utf8')
                    handles[s].write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
                    stats[s] += 1
    finally:
        for f in handles.values(): f.close()
    for s in groups:
        src = os.path.join(val_root, 'val', s + '.jsonl')
        dst = os.path.join(out, 'data', run_id, 'val', s + '.jsonl')
        if os.path.exists(src): shutil.copyfile(src, dst)
        else: open(dst, 'w', encoding='utf8').close()
    return dict(stats)


def prepare_full_matrix(args):
    """Create the full B/C/Q/P manifest and materialize only the selected queue."""
    root = os.path.abspath(os.path.join(args.all_data_out_dir, 'quality_grading_v2_1'))
    out = os.path.abspath(args.matrix_out_dir or os.path.join(args.all_data_out_dir, '..', 'MR-FULL-GRADED-TRAINING'))
    os.makedirs(out, exist_ok=True)
    pool_limit = int(getattr(args, 'matrix_pool_limit', 6000))
    max_items = int(getattr(args, 'matrix_max_items', 4096))
    selected = [x for x in (getattr(args, 'matrix_run_ids', '') or '').split(',') if x]
    if not selected:
        selected = ['B01_C%02d_QB_PB' % i for i in range(1, 17)]
    counts = Counter(); source_counts = Counter(); unit_sets = defaultdict(set); reservoirs = defaultdict(list)
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
                if layer not in {'L1','L2','L3','L4'} or q not in {'Q1','Q2'}: continue
                for s, targets in MATRIX_TARGETS.items():
                    for target in targets:
                        if target not in (x.get('candidate_targets') or []): continue
                        key = (layer, q, s, target, src)
                        counts[key] += 1; source_counts[(layer, q, s, target, src)] += 1
                        unit_sets[(layer, q, s, target)].add(_matrix_unit(x, target))
                        bucket = reservoirs[key]
                        if len(bucket) < pool_limit: bucket.append(_matrix_ref(x, target))
    plans = {}; materialized = {}
    for b, layers in FULL_LAYERS.items():
        for c, (classes, weights) in FULL_COMBOS.items():
            for qcode, qset in FULL_QUALITY.items():
                for pcode in FULL_POLICIES:
                    run_id = f'{b}_{c}_{qcode}_{pcode}'
                    class_counts = {}
                    for s in classes:
                        class_counts[s] = sum(counts[(layer, q, s, target, src)]
                                              for layer in layers for q in qset
                                              for target in MATRIX_TARGETS[s] for src in MATRIX_ALLOWED_SOURCES)
                    available = all(class_counts.get(s, 0) > 0 for s in classes)
                    spec = {'run_id': run_id, 'batch_id': b, 'combo_id': c, 'quality_code': qcode,
                            'sampling_code': pcode, 'layers': layers, 'supervision_classes': classes,
                            'ratios': weights, 'status': 'ELIGIBLE' if available else 'BLOCKED',
                            'eligibility_reason': 'legal train rows for every requested supervision class' if available else 'no legal train rows for one or more requested supervision classes',
                            'materialized': False, 'data': None, 'counts': class_counts,
                            'independent_units': {s: sum(len(unit_sets[(layer, q, s, target)]) for layer in layers for q in qset for target in MATRIX_TARGETS[s]) for s in classes},
                            'train_origin': 'Base', 'seed': 42, 'groups': classes,
                            'max_len': 1024, 'head_max_len': 512, 'source_count': len(MATRIX_ALLOWED_SOURCES)}
                    if run_id in selected and available:
                        refs_by_target = defaultdict(list)
                        total_weight = sum(weights)
                        for s, weight in zip(classes, weights):
                            quota = max(1, int(max_items * weight / total_weight))
                            for target in MATRIX_TARGETS[s]:
                                refs = [r for (layer, q, ss, tt, src), rows in reservoirs.items()
                                        if ss == s and tt == target and layer in layers and q in qset for r in rows]
                                refs_by_target[target].extend(_matrix_select(refs, pcode, target, quota))
                        for d in ('train','val'):
                            os.makedirs(os.path.join(out, 'data', run_id, d), exist_ok=True)
                        val_root = os.path.join(root, 'batch_preparation', 'batch1')
                        materialized[run_id] = _matrix_materialize(args, out, run_id, refs_by_target, classes, val_root)
                        spec.update({'materialized': True, 'data': 'data/' + run_id,
                                     'materialized_counts': materialized[run_id], 'status': 'PLANNED'})
                    plans[run_id] = spec
    extras = []
    for prefix, n in [('CUR', 12), ('SEED', 40), ('ABL', 32)]:
        for i in range(1, n + 1):
            rid = f'{prefix}{i:02d}'
            plans[rid] = {'run_id': rid, 'status': 'PLANNED', 'materialized': False, 'data': None,
                          'eligibility_reason': 'reserved extension slot after base matrix', 'groups': [], 'seed': 42}
            extras.append(rid)
    manifest = {
        'experiment_id': 'MR-FULL-GRADED-TRAINING', 'output_root': out,
        'source': 'existing quality_grading_v2_1/by_source indexes; no reclassification',
        'theoretical_slots': len(plans), 'base_slots': 1008, 'extra_slots': len(extras),
        'plans': plans, 'selected_queue': selected, 'materialized': materialized,
        'generation': {'command': sys.argv, 'code_sha256': {p: hashlib.sha256(open(p,'rb').read()).hexdigest() for p in ('prepare_router_data.py', __file__, 'router_data/laya_batch_train.py')},
                       'pool_limit': pool_limit, 'max_items_per_class': max_items, 'test_used': False},
        'audit': {'route_001_002_training': False, 's2_observed_actions_are_not_model_choice': True,
                  's3_prefix_reuse_is_not_physical_cache_hit': True, 'validation_source': 'existing V2.1 Batch1 fixed validation'},
        'aggregate': {'eligible': sum(v['status'] == 'ELIGIBLE' or v.get('materialized') for v in plans.values() if v['run_id'].startswith('B')),
                      'blocked': sum(v['status'] == 'BLOCKED' for v in plans.values()), 'planned': sum(v['status'] == 'PLANNED' for v in plans.values()),
                      'materialized_runs': len(materialized)}
    }
    _dump(os.path.join(out, 'experiment_matrix.json'), manifest)
    _dump(os.path.join(out, 'matrix_counts.json'), {'row_counts': {str(k): v for k,v in counts.items()}, 'source_counts': {str(k): v for k,v in source_counts.items()}, 'materialized': materialized})
    print(json.dumps({'out': out, 'slots': len(plans), 'materialized': list(materialized), 'aggregate': manifest['aggregate']}, ensure_ascii=False), flush=True)
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
