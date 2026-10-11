"""Prepare batch references and small typed Laya examples from saved V2.1 indexes."""
import csv
import gzip
import json
import os
import sys
import hashlib
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
    return {'provenance':{'source_id':src,'source_line':x['source_line'],'source_file':x['source_file'],'stable_record_id':x['stable_record_id'],'independent_unit_id':x['independent_unit_id'],'trajectory_id':x.get('trajectory_id'),'split':x['split']},'state':{'source_id':src,'pre_decision_state':state},'questions':{qid:{'type':typ,'instructions':'Predict this source-specific observed target: '+t+'. Observed actions are not optimal actions; prefix reuse is not physical cache hit.','criteria':criteria}},'expected':{qid:label},'_meta':{'supervision_class':x['primary_supervision_class'],'target':t,'label_evidence':x['label_evidence'].get(t,[]),'representative_only':True}}


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
