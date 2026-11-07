"""Canonical typed sample construction from saved source records."""

import csv
import json
import os

from modelrouter.data_pipeline.quality.quality_v2 import OWN_FILES, PUBLIC_FILES
from modelrouter.data_pipeline.sources.all_data_adapters import _map_action_category


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

def _rewrite_materialized_row(row):
    target = row.get('_meta', {}).get('target') if isinstance(row.get('_meta'), dict) else None
    if target:
        for question in row.get('questions', {}).values():
            if isinstance(question, dict):
                question['instructions'] = _neutral_instruction(target)
    return row
