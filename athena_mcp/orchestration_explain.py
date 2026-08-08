from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional
from .orchestration_score import finite_number

BENEFIT_METRICS=("delta_j","information_gain","bridge","option_value")

def _successor_vector(row:Mapping[str,Any]):
    src=row.get('scoring_source') or row.get('source') or {};values={}
    for name in BENEFIT_METRICS+('cost',):
        value=finite_number(src.get(name))
        if value is None:return None
        values[name]=value
    return values

def dominates(a:Mapping[str,Any],b:Mapping[str,Any])->bool:
    va=_successor_vector(a);vb=_successor_vector(b)
    if va is None or vb is None:return False
    weak=all(va[n]>=vb[n] for n in BENEFIT_METRICS) and va['cost']<=vb['cost'];strict=any(va[n]>vb[n] for n in BENEFIT_METRICS) or va['cost']<vb['cost']
    return weak and strict

def pareto_successor_frontier(rows:Iterable[Mapping[str,Any]])->list[str]:
    eligible=[r for r in rows if r.get('rankable_successor')];result=[]
    for row in eligible:
        if not any(other['id']!=row['id'] and dominates(other,row) for other in eligible):result.append(str(row['id']))
    return sorted(result)

def measurement_requests(rows:Iterable[Mapping[str,Any]])->list[Dict[str,Any]]:
    requests=[]
    for row in rows:
        blocked=[];missing=set()
        for formula in ('frontier','successor','reward'):
            score=row['scores'][formula]
            if score.get('status')=='UNKNOWN':blocked.append(formula);missing.update(score.get('missing',[]))
        if blocked:requests.append({'candidate':row['id'],'missing_metrics':sorted(missing),'blocked_formulas':sorted(blocked),'measurement_pressure':len(blocked)})
    return sorted(requests,key=lambda x:(-x['measurement_pressure'],x['candidate']))

def decision_explanation(rows:Iterable[Mapping[str,Any]],next_id:str|None,allocated_ids:Optional[set[str]]=None,budget_active:bool=False)->Dict[str,Any]:
    rows=list(rows);by_id={str(r['id']):r for r in rows};chosen=by_id.get(next_id) if next_id is not None else None;chosen_value=None
    if chosen is not None and chosen['scores']['successor'].get('status')=='KNOWN':chosen_value=chosen['scores']['successor']['value']
    allocated_ids=set(allocated_ids or set());rejected=[]
    for row in rows:
        if next_id is not None and row['id']==next_id:continue
        reasons=[]
        if row.get('resolved'):reasons.append('already_resolved')
        if not row.get('dependency',{}).get('ready',True):reasons.extend(row['dependency'].get('blockers',[]))
        if row.get('gate',{}).get('status')=='BLOCKED':reasons.extend('gate:'+x for x in row['gate'].get('blocked_by',[]))
        calibration=(row.get('metric_calibration') or {}).get('successor') or {}
        if calibration.get('status')=='BLOCKED':reasons.append('metric_calibration_blocked')
        score=row['scores']['successor']
        if score.get('status')=='UNKNOWN':reasons.append('successor_score_unknown')
        elif score.get('status')=='INVALID':reasons.append('successor_score_invalid')
        elif not row.get('rankable_successor'):reasons.append('not_successor_eligible')
        elif budget_active and str(row['id']) not in allocated_ids:reasons.append('not_budget_allocated')
        elif chosen_value is not None and float(score['value'])<float(chosen_value):reasons.append('lower_successor_score')
        elif chosen_value is not None and float(score['value'])==float(chosen_value):reasons.append('tie_broken_by_frontier_then_id')
        if not reasons:reasons.append('not_selected')
        rejected.append({'candidate':row['id'],'reasons':sorted(set(reasons))})
    return {'selected':next_id,'selection_rule':'highest KNOWN successor score on declared basis among unresolved dependency-ready gate-passing calibration-allowed candidates, constrained to budget allocation when active; frontier score then id break ties','selected_successor_score':chosen_value,'rejected':sorted(rejected,key=lambda x:x['candidate'])}
