from __future__ import annotations

import copy,hashlib,json
from typing import Any,Iterable,Mapping,Optional
from .orchestration import compile_orchestration
from .orchestration_authority_gate import authority_gate
from .orchestration_budget import allocate_budget
from .orchestration_explain import decision_explanation,pareto_successor_frontier


def _digest(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def _apply_authority(rows):
    authority_frontier=[];authority_plan=[]
    for row in rows:
        gate=authority_gate(row.get('source') or {});row.setdefault('gate',{}).setdefault('gates',{})['authority']=gate
        if not gate['promotion_allowed']:
            row['gate']['status']='BLOCKED';blocked=row['gate'].setdefault('blocked_by',[])
            if 'authority' not in blocked:blocked.append('authority')
            row['rankable_frontier']=False;row['rankable_successor']=False;row['allocation']=[gate['route']];authority_frontier.append(row);authority_plan.append({'candidate':row['id'],'route':gate['route'],'reason':gate['reason'],'minimum':gate.get('minimum'),'current':gate.get('current'),'authority_status':gate.get('authority_status')})
    return authority_frontier,sorted(authority_plan,key=lambda x:x['candidate'])

def compile_authority_orchestration(seed:Any,candidates:Optional[Iterable[Mapping[str,Any]]]=None,residuals:Optional[Iterable[Mapping[str,Any]]]=None,budget:Optional[Mapping[str,Any]]=None,metric_contract:Optional[Mapping[str,Any]]=None):
    result=copy.deepcopy(compile_orchestration(seed=seed,candidates=candidates,residuals=residuals,budget=budget,metric_contract=metric_contract));rows=result['frontier'];authority_frontier,authority_plan=_apply_authority(rows);executable=[r for r in rows if r.get('rankable_frontier')];eligible={r['id'] for r in rows if r.get('rankable_successor')};base_order=[r['id'] for r in result['successor_frontier']];by_id={r['id']:r for r in rows};successor=[by_id[i] for i in base_order if i in eligible];pareto_ids=pareto_successor_frontier(successor);allocation=allocate_budget(executable,budget);budget_active=bool((budget or {}).get('total_cost') is not None or (budget or {}).get('max_branches') is not None);allocated=set(allocation.get('selected',[]))
    if allocation.get('status')=='INVALID_BUDGET':budgeted=[]
    elif budget_active:budgeted=[r for r in successor if r['id'] in allocated]
    else:budgeted=successor
    next_row=budgeted[0] if budgeted else None;next_id=next_row['id'] if next_row else None;explanation=decision_explanation(rows,next_id,allocated,budget_active)
    snapshot={r['id']:{'claim_id':(r.get('source') or {}).get('claim_id'),'min_authority':(r.get('source') or {}).get('min_authority'),'authority_state':copy.deepcopy((r.get('source') or {}).get('authority_state')),'gate':copy.deepcopy(r['gate']['gates']['authority'])} for r in rows if (r.get('source') or {}).get('claim_id') or (r.get('source') or {}).get('min_authority') is not None}
    result.update({'frontier':rows,'executable_frontier':executable,'successor_frontier':successor,'budgeted_successor_frontier':budgeted,'pareto_successor_frontier':pareto_ids,'authority_frontier':authority_frontier,'authority_plan':authority_plan,'authority_snapshot':snapshot,'allocation_plan':allocation,'next':next_row,'decision_explanation':explanation})
    decision={'metric_basis':result.get('metric_contract'),'budget_allocation':{k:allocation.get(k) for k in ('status','solver','optimality','capacity','max_branches','selected','used','remaining','utility')},'authority_snapshot':snapshot,'executable_frontier':[r['id'] for r in executable],'successor_frontier':[r['id'] for r in successor],'budgeted_successor_frontier':[r['id'] for r in budgeted],'pareto_successor_frontier':pareto_ids,'measurement_frontier':[r['id'] for r in result.get('measurement_frontier',[])],'calibration_frontier':[r['id'] for r in result.get('calibration_frontier',[])],'grow':(result.get('grow') or {}).get('id'),'next':next_id,'dependency_cycles':result.get('dependency_graph',{}).get('cycles',[])};result['decision_digest']=_digest(decision);return result
