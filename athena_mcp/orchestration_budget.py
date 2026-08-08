from __future__ import annotations

from itertools import combinations
from typing import Any, Dict, Iterable, Mapping
from .orchestration_score import finite_number

EXACT_LIMIT=18

def _utility(row:Mapping[str,Any]):
    src=row.get('scoring_source') or row.get('source') or {};values=[finite_number(src.get(n)) for n in ('readiness','gain','independence','bridge')]
    if any(v is None for v in values):return None
    readiness,gain,independence,bridge=values;return float(readiness*gain*independence*bridge)

def _resource_cost(row:Mapping[str,Any],cost_field:str):
    src=row.get('source') or {};value=src.get(cost_field)
    if value is None and cost_field!='cost':value=src.get('cost')
    value=finite_number(value)
    if value is None or value<0:return None
    return float(value)

def _candidate_records(rows,cost_field):
    records=[];unknown=[]
    for row in rows:
        utility=_utility(row);cost=_resource_cost(row,cost_field)
        if utility is None or cost is None:
            unknown.append({'candidate':row['id'],'missing':[name for name,value in (('allocation_utility',utility),(cost_field,cost)) if value is None]});continue
        records.append({'id':str(row['id']),'utility':utility,'cost':cost})
    return records,unknown

def _better(candidate,incumbent):
    if incumbent is None:return True
    cu,cc,cids=candidate;iu,ic,iids=incumbent
    if cu!=iu:return cu>iu
    if cc!=ic:return cc<ic
    return cids<iids

def _exact(records,capacity,max_branches):
    best=None;n=len(records);limit=min(max_branches,n)
    for size in range(limit+1):
        for combo in combinations(records,size):
            cost=sum(i['cost'] for i in combo)
            if cost>capacity+1e-12:continue
            utility=sum(i['utility'] for i in combo);ids=tuple(sorted(i['id'] for i in combo));candidate=(utility,cost,ids)
            if _better(candidate,best):best=candidate
    return best or (0.0,0.0,tuple())

def _greedy(records,capacity,max_branches):
    def key(item):
        density=item['utility']/item['cost'] if item['cost']>1e-12 else float('inf')
        return (-density,-item['utility'],item['cost'],item['id'])
    selected=[];used=0.0
    for item in sorted(records,key=key):
        if len(selected)>=max_branches:break
        if item['utility']<=0:continue
        if used+item['cost']<=capacity+1e-12:selected.append(item);used+=item['cost']
    return sum(i['utility'] for i in selected),used,tuple(sorted(i['id'] for i in selected))

def allocate_budget(rows:Iterable[Mapping[str,Any]],budget:Mapping[str,Any]|None)->Dict[str,Any]:
    rows=list(rows);budget=dict(budget or {});cost_field=str(budget.get('cost_field') or 'resource_cost');unit=str(budget.get('unit') or 'declared-cost-unit');capacity=finite_number(budget.get('total_cost'));raw_max=budget.get('max_branches')
    try:max_branches=int(raw_max) if raw_max is not None else len(rows)
    except (TypeError,ValueError):max_branches=-1
    if max_branches<0:return {'status':'INVALID_BUDGET','reason':'max_branches must be a nonnegative integer','selected':[],'deferred':[row['id'] for row in rows]}
    if capacity is not None and capacity<0:return {'status':'INVALID_BUDGET','reason':'total_cost must be nonnegative','selected':[],'deferred':[row['id'] for row in rows]}
    records,unknown=_candidate_records(rows,cost_field);record_ids={i['id'] for i in records}
    if capacity is None and raw_max is None:
        selected=[i['id'] for i in sorted(records,key=lambda x:(-x['utility'],x['id'])) if i['utility']>0]
        return {'status':'UNBOUNDED','solver':'NONE','optimality':'N/A','unit':unit,'cost_field':cost_field,'capacity':None,'max_branches':None,'selected':selected,'deferred':[r['id'] for r in rows if r['id'] not in selected],'unknown_cost_or_utility':unknown,'used':None,'remaining':None,'utility':sum(i['utility'] for i in records if i['id'] in selected)}
    if capacity is None:capacity=sum(i['cost'] for i in records)
    max_branches=min(max_branches,len(records))
    if len(records)<=EXACT_LIMIT:utility,used,ids=_exact(records,capacity,max_branches);solver='EXACT_ENUMERATION';optimality='PROVEN_FOR_DECLARED_UTILITY'
    else:utility,used,ids=_greedy(records,capacity,max_branches);solver='GREEDY_DENSITY_FALLBACK';optimality='HEURISTIC_NOT_PROVEN'
    selected=list(ids)
    return {'status':'ALLOCATED','solver':solver,'optimality':optimality,'unit':unit,'cost_field':cost_field,'capacity':capacity,'max_branches':max_branches,'selected':selected,'deferred':[r['id'] for r in rows if r['id'] not in selected],'unknown_cost_or_utility':unknown,'used':used,'remaining':max(0.0,capacity-used),'utility':utility,'candidate_count':len(rows),'costed_candidate_count':len(record_ids),'exact_limit':EXACT_LIMIT,'utility_law':'readiness * gain * independence * bridge on scoring_source; resource constraint uses raw resource_cost (fallback raw cost)'}
