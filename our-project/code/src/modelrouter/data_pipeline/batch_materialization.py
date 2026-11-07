"""Materialize the saved V2.1 batch and representative views."""

import gzip
import json
import os
import sys
from collections import Counter, defaultdict

from modelrouter.data_pipeline.quality.quality_v2 import OWN_FILES, PUBLIC_FILES, VARIABLES
from .batch_examples import _dump, _example, _source_rows, _unit, _use


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
    data={'generation':{'command':sys.argv,'input':'existing V2.1 by_source index; no reclassification','representatives_per_source_target':8,'sample_selection':'first eight distinct target units in saved source index'},'totals':totals,'by_layer':coverage,'variable_order':VARIABLES}
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
