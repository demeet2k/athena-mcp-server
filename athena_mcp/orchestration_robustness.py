from __future__ import annotations
import math
from typing import Any,Dict,Iterable,Mapping

SUCCESSOR_FACTOR_COUNT=5

def _score(row:Mapping[str,Any]):
    packet=(row.get('scores') or {}).get('successor') or {}
    if packet.get('status')!='KNOWN':return None
    try:value=float(packet.get('value'))
    except (TypeError,ValueError):return None
    return value if math.isfinite(value) else None

def _critical_relative_perturbation(top:float,challenger:float):
    if top<=0 or challenger<=0 or top<challenger:return None
    if top==challenger:return 0.0
    q=top/challenger;root=q**(1.0/SUCCESSOR_FACTOR_COUNT);return (root-1.0)/(root+1.0)

def successor_robustness(rows:Iterable[Mapping[str,Any]],relative_perturbation:float=0.05)->Dict[str,Any]:
    try:eps=float(relative_perturbation)
    except (TypeError,ValueError):raise ValueError('relative_perturbation must be numeric')
    if not math.isfinite(eps) or eps<0 or eps>=1:raise ValueError('relative_perturbation must be in [0,1)')
    scored=[];unknown=[]
    for row in rows:
        value=_score(row)
        if value is None:unknown.append(str(row.get('id')))
        else:scored.append((str(row.get('id')),value))
    scored.sort(key=lambda x:(-x[1],x[0]))
    if not scored:return {'status':'UNKNOWN','winner':None,'challenger':None,'critical_relative_perturbation':None,'tested_relative_perturbation':eps,'stable_under_tested_perturbation':None,'unknown_candidates':unknown,'boundary':'robustness is rank sensitivity, not truth probability'}
    winner,wscore=scored[0]
    if len(scored)==1:return {'status':'SINGLE_CANDIDATE','winner':winner,'winner_score':wscore,'challenger':None,'critical_relative_perturbation':None,'tested_relative_perturbation':eps,'stable_under_tested_perturbation':None,'unknown_candidates':unknown,'boundary':'no known challenger exists; not a robustness proof'}
    challenger,cscore=scored[1];margin=wscore-cscore;rel=margin/abs(wscore) if wscore!=0 else (0.0 if margin==0 else None);critical=_critical_relative_perturbation(wscore,cscore)
    if critical is None:status='NONPOSITIVE_UNCERTIFIED';stable=None
    elif critical==0:status='TIE_FRAGILE';stable=eps==0
    else:stable=eps<critical;status='STABLE' if stable else 'FRAGILE'
    return {'status':status,'winner':winner,'winner_score':wscore,'challenger':challenger,'challenger_score':cscore,'absolute_margin':margin,'relative_margin':rel,'critical_relative_perturbation':critical,'tested_relative_perturbation':eps,'stable_under_tested_perturbation':stable,'factor_count':SUCCESSOR_FACTOR_COUNT,'unknown_candidates':unknown,'law':'q*((1-eps)/(1+eps))^5; eps*=(q^(1/5)-1)/(q^(1/5)+1)','boundary':'local multiplicative rank sensitivity only; not truth probability, confidence, or causal evidence'}

def elasticity_packet(row:Mapping[str,Any])->Dict[str,Any]:
    value=_score(row)
    if value is None:return {'status':'UNKNOWN','candidate':str(row.get('id')),'elasticities':None}
    return {'status':'KNOWN','candidate':str(row.get('id')),'score':value,'elasticities':{'delta_j':1.0,'information_gain':1.0,'bridge':1.0,'option_value':1.0,'cost':-1.0},'interpretation':'d ln(S) / d ln(metric) under declared multiplicative successor law'}
