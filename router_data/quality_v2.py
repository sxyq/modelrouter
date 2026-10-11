"""Streaming V2 quality and supervision indexes for the existing data chain."""
import csv, gzip, hashlib, json, os
from collections import Counter, defaultdict

PUBLIC_FILES = {
    "TRA-001":"Agent轨迹/TRA-001_Open-SWE-Traces/cleaned_trajectories.jsonl",
    "TRA-002":"Agent轨迹/TRA-002_SWE-smith/cleaned_trajectories.jsonl",
    "TRA-004":"Agent轨迹/TRA-004_AgentSuite/cleaned_trajectories.jsonl",
    "ROUTE-001":"路由比较/ROUTE-001_LLMRouterBench/cleaned_evaluations.jsonl",
    "ROUTE-002":"路由比较/ROUTE-002_RouterBench/cleaned_routerbench.jsonl",
    "ROUTE-003":"路由比较/ROUTE-003_TwinRouterBench/cleaned_twin_bench.jsonl",
    "ROUTE-004":"路由比较/ROUTE-004_Arena/cleaned_arena_preference.jsonl",
    "ROUTE-005":"路由比较/ROUTE-005_FindingTheRightFit/cleaned_task_level.jsonl",
    "CACHE-001":"缓存与时间/CACHE-001_Mooncake/cleaned_mooncake_traces.jsonl",
    "TIME-001":"缓存与时间/TIME-001_BurstGPT/cleaned_burstgpt.jsonl",
    "ENV-001":"任务环境/ENV-001_SWE-Gym/cleaned_swe_gym.jsonl",
    "ENV-002":"任务环境/ENV-002_SWE-rebench-V2/cleaned_swe_rebench.jsonl",
    "MEM-003":"长期记忆/MEM-003_LongMemEval-V2/cleaned_longmemeval_v2.jsonl",
    "MEM-005":"长期记忆/MEM-005_MemoryCraft/cleaned_memorycraft.jsonl",
}
OWN_FILES={"OWN-001":"our-project/data/source/cch-model-cost-cache-statistics.csv", "OWN-002":"our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv", "OWN-003":"our-project/data/summaries/cch-sxyq-gpt-unified-summary.csv"}
VARIABLES=['Task/Subtask','Agent/Coordination','Context/Memory','Tool/Environment','Verification/Recovery','KV Cache/Continuity','Temporal/Execution','Provider/Availability']
RULES={
 'TRA-001':'Action type and task/trajectory identity required; missing resolved remains UNEVALUATED. No optimum action label.',
 'TRA-002':'Action nature INFERRED_COMMAND is indirect; missing resolved remains UNEVALUATED. Outcome counts once per trajectory.',
 'TRA-004':'Finite evaluation score and task/model/effort identity; effort observation does not establish a comparable pair.',
 'ROUTE-001':'Finite measured benchmark score with existing complete-prompt task identity; V1 known conflicting groups retained Q4; licence pending.',
 'ROUTE-002':'Finite candidate scores; all-zero vector has score observation only, no winner; oracle must match candidate identity; licence pending.',
 'ROUTE-004':'Two distinct candidates and winner model_a/model_b yield preference; ties retain weak preference; unknown winner invalid.',
 'CACHE-001':'Nonnegative input/output length; prefix reuse is estimated. Physical cache observation unknown irrespective of cleaner false.',
 'TIME-001':'Nonnegative prompt/response tokens and arrival identity; token arithmetic validated; no task outcome.',
 'OWN-002':'Observed nonnegative prompt/output/quota; zero/failed usage reference only; quota units separate from USD.',
 'OWN-001':'Aggregate actual observations Q2, never independent calls or training inputs.',
 'OWN-003':'Derived aggregate Q3; zero new observations.',
 'ROUTE-003':'Benchmark target and identity; evaluation only.',
 'ROUTE-005':'Finite reward observed; analysis only, costs retain source units.',
 'ENV-001/ENV-002':'Task identity plus problem text; test metadata stays evaluation only.',
 'MEM-003/MEM-005':'Question/history plus nonempty gold answer; evaluation identity retained.'}

def number(v):
 try:
  x=float(v); return x if __import__('math').isfinite(x) else None
 except (TypeError,ValueError):return None

def nonnegative(v):
 n=number(v); return n is not None and n>=0

def present(v):return v is not None and v!='' and v!=[] and v!={}

def field(r,path):
 for k in path.split('.'):
  if not isinstance(r,dict):return None
  r=r.get(k)
 return r

def rows(src,path,v1):
 with gzip.open(v1,'rt',encoding='utf8') as refs:
  if path.endswith('.csv'):
   data=open(path,encoding='utf-8-sig',newline=''); it=enumerate(csv.DictReader(data),2)
  else:
   data=open(path,encoding='utf8'); it=((i,json.loads(s)) for i,s in enumerate(data,1) if s.strip())
  try:
   for i,r in it:
    line=next(refs,None)
    if line is None:raise ValueError(f'{src}: missing prior identity at {i}')
    m=json.loads(line)
    if m['source_line']!=i:raise ValueError(f'{src}: identity line mismatch {i}')
    yield i,r,m
   if next(refs,None):raise ValueError(f'{src}: extra prior identity')
  finally:data.close()

def classify(src,r,m):
 p=r.get('provenance',{}); pre=r.get('pre_decision_state',{}); obs=r.get('observed_decision',{}); gt=r.get('ground_truth_outcome',{})
 q='Q3'; main='S4'; targets={}; unknown=[]; estimated=[]; reasons=[]
 def label(name,*paths):
  found=[k for k in paths if present(field(r,k))]
  if found:targets[name]=found
 if src.startswith('TRA-'):
  main='S2'
  if src=='TRA-004':
   if number(gt.get('eval_score')) is not None: label('observed_episode_evaluation','ground_truth_outcome.eval_score')
   label('effort_configuration_observation','provenance.reasoning_effort_mode')
   q='Q1' if 'observed_episode_evaluation' in targets else 'Q3'
  else:
   if obs.get('action_type') and obs.get('action_nature')!='INFERRED_COMMAND':label('observed_action','observed_decision.action_type')
   elif obs.get('action_type'): label('inferred_command','observed_decision.action_type'); reasons.append('action_inferred_from_text')
   if gt.get('task_resolved') is True:label('observed_success','ground_truth_outcome.task_resolved')
   elif gt.get('task_resolved') is False and gt.get('label_nature')=='POST_HOC_EVALUATOR':label('observed_failure','ground_truth_outcome.task_resolved')
   elif gt.get('task_resolved') is False:unknown.append('false_outcome_status_unknown'); reasons.append('false_outcome_needs_original_status')
   q='Q1' if 'observed_action' in targets and not unknown else ('Q2' if targets else 'Q3')
 elif src=='ROUTE-001':
  main='S1'
  if number(gt.get('score')) is not None:label('benchmark_model_score','ground_truth_outcome.score','provenance.model_name')
  q='Q1' if targets and present(pre.get('prompt_snippet')) else 'Q4'
 elif src=='ROUTE-002':
  main='S1'; c=r.get('candidate_evaluations',{}); valid={k:number(v.get('score')) for k,v in c.items() if isinstance(v,dict) and number(v.get('score')) is not None}
  if len(valid)>=2:targets['candidate_score_vector']=['candidate_evaluations']
  if valid and max(valid.values())>0:
   if len(set(valid.values()))>1:targets['quality_difference']=['candidate_evaluations']
   winner=obs.get('oracle_model_to_route_to')
   if winner in valid and valid[winner]==max(valid.values()):targets['score_cost_oracle']=['observed_decision.oracle_model_to_route_to','candidate_evaluations']
  else:reasons.append('no_positive_candidate_score_no_winner')
  q='Q1' if 'quality_difference' in targets else ('Q2' if targets else 'Q4')
 elif src=='ROUTE-004':
  main='S1'; a=pre.get('candidate_model_a'); b=pre.get('candidate_model_b'); w=gt.get('human_winner')
  if a and b and a!=b and w in ('model_a','model_b'):
   label('human_pairwise_preference','ground_truth_outcome.human_winner');q='Q1'
  elif w and 'tie' in str(w):label('human_tie','ground_truth_outcome.human_winner');q='Q2'
  else:q='Q4'; reasons.append('invalid_preference_candidates_or_winner')
 elif src=='CACHE-001':
  main='S3'; unknown.append('physical_provider_cache_hit'); estimated.append('prefix_reuse_opportunity')
  if nonnegative(pre.get('input_length')) and nonnegative(gt.get('output_length')):
   label('output_token_length','ground_truth_outcome.output_length'); label('prefix_reuse_opportunity','observed_decision.historical_prefix_hit_ratio');q='Q1'
  else:q='Q3'
  if src=='CACHE-001' and m.get('quality_grade')=='Q3':
   q='Q3'; reasons.append('preserved_v1_analysis_only_prefix_opportunity')
 elif src=='TIME-001':
  main='S3'
  if nonnegative(pre.get('prompt_tokens')) and nonnegative(gt.get('response_tokens')):
   label('request_response_tokens','ground_truth_outcome.response_tokens');q='Q1'
   if number(gt.get('total_tokens')) is not None and number(gt['total_tokens'])!=number(pre['prompt_tokens'])+number(gt['response_tokens']):q='Q4';reasons.append('token_total_mismatch')
 elif src=='OWN-002':
  main='S3'
  if r.get('status')=='success' and nonnegative(r.get('prompt_tokens')) and nonnegative(r.get('completion_tokens')) and number(r.get('total_tokens')) and nonnegative(r.get('quota_units')):
   label('call_quota_units','quota_units');label('cache_read_tokens','cache_read_tokens');label('call_output_tokens','completion_tokens');q='Q1'
  else:q='Q3';reasons.append('failed_zero_or_missing_usage')
 elif src=='OWN-001':
  main='S3';label('aggregate_usd_usage','n_calls','sum_cost_usd');q='Q2' if nonnegative(r.get('sum_cost_usd')) and nonnegative(r.get('n_calls')) else 'Q4'
 elif src=='OWN-003':
  main='S3';q='Q3';label('derived_summary_reference','n_calls');reasons.append('derived_not_new_observation')
 elif src=='ROUTE-005':
  main='S2';label('analysis_task_reward','ground_truth_outcome.reward');q='Q1' if number(gt.get('reward')) is not None else 'Q3'
 elif src=='ROUTE-003':
  label('benchmark_tier','observed_decision.target_tier');q='Q1' if targets else 'Q3'
 elif src.startswith('ENV-'):
  q='Q1' if present(pre.get('problem_snippet')) and m.get('task_id') else 'Q3';label('test_metadata','ground_truth_outcome.has_test_patch')
 elif src.startswith('MEM-'):
  label('memory_qa_answer','ground_truth_outcome.gold_answer');q='Q1' if targets and any(present(pre.get(k)) for k in ['question','question_snippet']) else 'Q3'
 if m.get('quality_grade')=='Q4':q='Q4';reasons.append('existing_known_invalid_or_conflict:'+str(m.get('quality_basis')))
 if not m.get('unit_id'):q='Q4';reasons.append('missing_stable_unit_identity')
 coverage={v:[k for k in m.get('variable_fields_present',{}).get(v,[]) if present(field(r,k))] for v in VARIABLES}
 if unknown and 'Verification/Recovery' in coverage: coverage['Verification/Recovery']=[k for k in coverage['Verification/Recovery'] if k!='ground_truth_outcome.task_resolved']
 # Policy and prior split are preserved independently of record quality.
 permission=not m.get('training_prohibited_by_source_policy') and src not in {'ROUTE-001','ROUTE-002','ROUTE-003','ROUTE-005','ENV-001','ENV-002','MEM-003','MEM-005','TRA-004','OWN-001','OWN-003'}
 usable=[t for t in targets if t not in {'inferred_command','effort_configuration_observation','derived_summary_reference','human_tie'}]
 eligible=permission and q in {'Q1','Q2'} and m.get('split_identity')=='train' and bool(usable)
 return dict(source_id=src,stable_record_id=m['record_id'],source_file=m['source_file'],source_line=m['source_line'],independent_unit_id=m['unit_id'],independent_unit_type=m['unit_type'],task_id=m.get('task_id'),trajectory_id=m.get('trajectory_id'),quality_grade=q,quality_reason=reasons or ['valid_source_specific_target'],primary_supervision_class=main,specific_supervision_targets=list(targets),label_evidence=targets,observed=[t for t in targets if t not in estimated],estimated=estimated,unknown=unknown,variable_coverage=coverage,split=m['split_identity'],license_status=m['license_status'],source_policy_train_allowed=permission,train_eligible=eligible,train_eligibility_reason='eligible_for_source_specific_auxiliary_or_preference_only' if eligible else 'quality_target_policy_or_preserved_split_excludes',candidate_targets=usable if eligible else [],direct_runtime_joint_route_label=False)

def group_layers(groups):
 # Each source is partitioned by independent units. Quality is the primary key;
 # a stable digest breaks ties so source order cannot determine a layer.
 ordered=sorted(groups,key=lambda u:(groups[u]['q'], hashlib.sha256((groups[u]['signature']+'|'+u).encode()).hexdigest(), u))
 n=len(ordered)
 cuts=[max(1,round(n*0.10)),max(1,round(n*0.20)),max(1,round(n*0.30))]
 while sum(cuts)>=n and n>=4:
  cuts[-1]-=1
  if cuts[-1]<1: cuts[-1]=1
  if sum(cuts)<n: break
 assigned={}; start=0
 for layer,count in zip(('L1','L2','L3'),cuts):
  for u in ordered[start:start+count]: assigned[u]=layer
  start+=count
 for u in ordered[start:]: assigned[u]='L4'
 return assigned

def dump(path,obj):
 with open(path,'w',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)

def run_quality_v2(args):
 out=os.path.join(args.all_data_out_dir,'quality_grading_v2_1'); v1=os.path.join(args.all_data_out_dir,'quality_grading')
 os.makedirs(out,exist_ok=True)
 for d in ['by_source','level1','level2','level3','level4']:os.makedirs(os.path.join(out,d),exist_ok=True)
 sources={s:os.path.join(args.cleaned_root,p) for s,p in PUBLIC_FILES.items()};sources.update(OWN_FILES)
 quality={}; supervision={}; matrix={}; candidates={}; layerstats={l:defaultdict(Counter) for l in ['L1','L2','L3','L4']}; validation={}; targetstats={}; sizes={}
 codefiles=['prepare_router_data.py',__file__]; codeversion={p:hashlib.sha256(open(p,'rb').read()).hexdigest() for p in codefiles}
 for src,path in sources.items():
  print('processing',src,flush=True); before=os.stat(path); ref=os.path.join(v1,'by_source',src+'.jsonl.gz'); groups={}; trajectories={}; unit_splits={}; duplicates=0; record_ids=set()
  for i,r,m in rows(src,path,ref):
   x=classify(src,r,m);u=x['independent_unit_id'];record_ids.add(x['stable_record_id'])
   if x.get('trajectory_id'):trajectories[x['trajectory_id']]=1
   old=unit_splits.setdefault(u,x['split'])
   if old!=x['split']:raise ValueError(f'{src}: mixed preserved splits')
   p=r.get('provenance',{});pre=r.get('pre_decision_state',{})
   length=number(pre.get('context_chars') or pre.get('prompt_tokens') or pre.get('input_length') or r.get('prompt_tokens')) or 0
   g=groups.setdefault(u,dict(q=4,n=0,length=0,scenario=str(m.get('scenario') or 'unknown'),signature=''))
   g['q']=min(g['q'],int(x['quality_grade'][1:]));g['n']+=1;g['length']=max(g['length'],length)
   g['signature']=str((g['scenario'],p.get('model_name') or r.get('model_normalized'),p.get('reasoning_effort_mode') or r.get('reasoning_effort'),int(length//1024),r.get('observed_decision',{}).get('action_type')))
  assignment=group_layers(groups); q=Counter();s=Counter();c=Counter(); vm={l:{v:Counter() for v in VARIABLES} for l in layerstats}; layer_units={l:set() for l in layerstats}; layer_candidate_units={l:set() for l in layerstats};ts=defaultdict(lambda:dict(rows=0,units=set(),eligible_rows=0,eligible_units=set()));seen_candidate=set(); actual_candidates=0
  handles={l:gzip.open(os.path.join(out,'level'+l[1:],src+'.jsonl.gz'),'wt',encoding='utf8',compresslevel=1) for l in layerstats}
  with gzip.open(os.path.join(out,'by_source',src+'.jsonl.gz'),'wt',encoding='utf8',compresslevel=1) as f:
   for i,r,m in rows(src,path,ref):
    x=classify(src,r,m);u=x['independent_unit_id'];l=assignment[u];x['assigned_layer']=l
    layer_units[l].add((x['independent_unit_type'],u))
    if x['train_eligible']: layer_candidate_units[l].add((x['independent_unit_type'],u))
    q[x['quality_grade']]+=1;s[x['primary_supervision_class']]+=1;c['source_policy_allowed_rows']+=int(x['source_policy_train_allowed']);c['eligible_rows']+=int(x['train_eligible']);c['supervised_rows']+=bool(x['specific_supervision_targets'])
    # One candidate per independent outcome unit; action steps retain their own observed action identities.
    for t in x['specific_supervision_targets']:
     targetunit=(x.get('trajectory_id') or u) if t=='observed_success' else (x['stable_record_id'] if t in {'observed_action','inferred_command'} else u)
     ts[t]['rows']+=1;ts[t]['units'].add(targetunit)
     if t in x['candidate_targets']:ts[t]['eligible_rows']+=1;ts[t]['eligible_units'].add(targetunit);seen_candidate.add((t,targetunit))
    for v,fields in x['variable_coverage'].items():vm[l][v]['nonempty' if fields else 'missing']+=1
    layerstats[l][src][x['quality_grade']]+=1;layerstats[l][src]['rows']+=1;layerstats[l][src][x['primary_supervision_class']]+=1
    f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
    handles[l].write(json.dumps({'source_id':src,'stable_record_id':x['stable_record_id'],'source_line':i,'independent_unit_id':u,'quality_grade':x['quality_grade'],'primary_supervision_class':x['primary_supervision_class'],'split':x['split'],'assigned_layer':l},ensure_ascii=False,separators=(',',':'))+'\n')
  for f in handles.values():f.close()
  after=os.stat(path); unchanged=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  quality[src]=dict(q,rows=sum(q.values()),independent_units=len(groups),independent_trajectories=len(trajectories),duplicate_record_ids=sum(q.values())-len(record_ids))
  supervision[src]=dict(s);matrix[src]=vm;candidates[src]=dict(c,deduplicated_target_units=len(seen_candidate));targetstats[src]={t:{k:len(v) if isinstance(v,set) else v for k,v in z.items()} for t,z in ts.items()}
  for l in layerstats:
   layerstats[l][src]['independent_units']=sum(1 for typ,u in layer_units[l] if u in assignment)
   layerstats[l][src]['candidate_independent_units']=sum(1 for typ,u in layer_candidate_units[l] if u in assignment)
  validation[src]=dict(source_unchanged=unchanged,rows=sum(q.values()),layer_rows=sum(layerstats[l][src]['rows'] for l in layerstats),primary_rows=sum(s.values()),preserved_split_conflicts=0,units=len(groups))
  if not unchanged:raise ValueError('input changed '+src)
  print(src,quality[src],candidates[src],flush=True)
 metadata={'entrypoint':'prepare_router_data.py --mode quality_v2','command':__import__('sys').argv,'code_sha256':codeversion,'rules':RULES,'identity_reference':v1+'/by_source/*.jsonl.gz','grouping':'Existing task/unit and split identity retained; observed outcome deduplicated per trajectory; action identity per source record','sorting':'Per-source quality, low group repetition, context length, stable unit identity; representatives by scenario, diversity by model/effort/length/tool; complex tail > source-group context p90; rest L4','random_sampling':False,'seed':None,'runtime_joint_route_labels':0}
 public=sum(quality[s]['rows'] for s in PUBLIC_FILES)
 summary={'generation':metadata,'public_rows':public,'own_rows':{s:quality[s]['rows'] for s in OWN_FILES},'quality_by_source':quality,'layer_details':{l:{s:dict(v) for s,v in ss.items()} for l,ss in layerstats.items()},'validation':validation,'target_statistics':targetstats}
 dump(os.path.join(out,'quality_summary.json'),summary);dump(os.path.join(out,'supervision_summary.json'),{'generation':metadata,'by_source':supervision,'specific_targets':targetstats});dump(os.path.join(out,'source_variable_matrix.json'),matrix);dump(os.path.join(out,'train_candidate_summary.json'),{'by_source':candidates,'by_target':targetstats,'runtime_joint_route_labels':0})
 v1q=json.load(open(os.path.join(v1,'quality_summary.json')))['quality_by_source']
 v2root=os.path.join(args.all_data_out_dir,'quality_grading_v2')
 v2q=json.load(open(os.path.join(v2root,'quality_summary.json')))['quality_by_source'] if os.path.exists(os.path.join(v2root,'quality_summary.json')) else {}
 with open(os.path.join(out,'tables.md'),'w',encoding='utf8') as f:
  f.write('# MR-DATA-GRADING-V2\n\n仅生成引用索引；真实联合路由标签为 0。\n\n|来源|记录|独立单位|Q1|Q2|Q3|Q4|S1|S2|S3|S4|候选记录|去重目标单位|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n')
  for src,z in quality.items():f.write('|'+src+'|'+ '|'.join(str(v) for v in [z['rows'],z['independent_units']]+[z.get(k,0) for k in ['Q1','Q2','Q3','Q4']]+[supervision[src].get(k,0) for k in ['S1','S2','S3','S4']]+[candidates[src]['eligible_rows'],candidates[src]['deduplicated_target_units']])+'|\n')
  f.write('\n## V1/V2/V2.1\n\n|来源|V1 Q1/Q2/Q3/Q4|V2 Q1/Q2/Q3/Q4|V2.1 Q1/Q2/Q3/Q4|\n|---|---|---|---|\n')
  for src,z in quality.items():f.write('|'+src+'|'+str([v1q[src].get(k,0) for k in ['Q1','Q2','Q3','Q4']])+'|'+str([v2q.get(src,{}).get(k,0) for k in ['Q1','Q2','Q3','Q4']])+'|'+str([z.get(k,0) for k in ['Q1','Q2','Q3','Q4']])+'|\n')
  f.write('\n## 四层来源与字段\n\n|层|来源|记录|独立单位|候选独立单位|八变量非空数量，按正式变量顺序|\n|---|---|---:|---:|---:|---|\n')
  for l,ss in layerstats.items():
   for src,z in ss.items():f.write(f"|{l}|{src}|{z['rows']}|{z['independent_units']}|{z['candidate_independent_units']}|{[matrix[src][l][v]['nonempty'] for v in VARIABLES]}|\n")
  f.write('\n## 具体目标\n\n|来源|目标|记录|独立单位|合法候选记录|候选独立单位|\n|---|---|---:|---:|---:|---:|\n')
  for src,tt in targetstats.items():
   for t,z in tt.items():f.write(f"|{src}|{t}|{z['rows']}|{z['units']}|{z['eligible_rows']}|{z['eligible_units']}|\n")
 if public!=6600628 or summary['own_rows']!={'OWN-001':110,'OWN-002':221128,'OWN-003':79}:raise ValueError('source row totals differ')
 print('completed',out,'public',public,flush=True)
