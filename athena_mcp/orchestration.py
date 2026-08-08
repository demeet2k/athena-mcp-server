from __future__ import annotations

import hashlib,json
from typing import Any,Dict,Iterable,List,Mapping,Optional

from .orchestration_budget import allocate_budget
from .orchestration_explain import decision_explanation,measurement_requests,pareto_successor_frontier
from .orchestration_gate import promotion_gate
from .orchestration_graph import candidate_id,dependency_graph
from .orchestration_metric import calibration_requests,contract_summary,formula_calibration,normalize_item
from .orchestration_reward import reallocation_plan
from .orchestration_score import REWARD_NEGATIVE,REWARD_POSITIVE,frontier_score,rank_key,residual_score,reward_score,successor_score
from .orchestration_successor import successor_packet
from .orchestration_test import validation_bundle

AOR_VERSION='AOR.3.1'
TRANSFORMS=('decompose','formalize','dual','invert','compose','recur','edge','contradict','fail','falsify','bridge','implement','test','compress','reconstruct','successor')
EDGE_TYPES=('define','derive','depend','support','contradict','test','fail','implement','bridge','reconstruct','fork','merge','next')
RUN_STAGES=('reconstruct','extract','retrieve','hug','graph','gap','compile','measure','calibrate','validate_test','validate_persistence','test','observe','repair','retest','verify','reward','reallocate','allocate_budget','output','successor','replay')
TEST_BRANCHES=('main','counter','edge','fail')
COORDINATE_FIBER=('KC144','JSPACE_GRAPH','LINEAGE','SEMANTIC','TIME_NATIVE')

def _numeric_positive(value):
    if isinstance(value,bool):return value
    try:return float(value)>0
    except (TypeError,ValueError):return False

def _allocation(item,reward,reward_calibration,gate,dep,validation):
    if not dep.get('ready',True):return ['resolve_dependency']
    if gate.get('status')=='BLOCKED' or validation.get('status')=='BLOCKED':return ['branch','repair','retest']
    if not reward_calibration.get('ranking_allowed',True):return ['calibrate_metrics']
    if reward.get('status')!='KNOWN':return ['measure']
    if float(reward['value'])>0:return ['deepen','replicate','braid']
    if _numeric_positive(item.get('duplicate')):return ['hibernate']
    return ['retain','measure']

def _candidate_row(raw,scoring,report,index,dep):
    ident=candidate_id(raw,index);frontier=frontier_score(scoring);successor=successor_score(scoring);reward=reward_score(scoring);gate=promotion_gate(raw);validation=validation_bundle(raw)
    calibration={name:formula_calibration(report,name) for name in ('frontier','successor','reward')};unresolved=not bool(raw.get('resolved',False))
    rankable_frontier=unresolved and dep.get('ready',True) and gate['status']=='PASS' and validation['promotion_allowed'] and calibration['frontier']['ranking_allowed'] and frontier['status']=='KNOWN'
    rankable_successor=unresolved and dep.get('ready',True) and gate['status']=='PASS' and validation['promotion_allowed'] and calibration['successor']['ranking_allowed'] and successor['status']=='KNOWN'
    unknown=sorted(set(frontier.get('missing',[])+successor.get('missing',[])+reward.get('missing',[])))
    return {'id':ident,'resolved':not unresolved,'dependency':dep,'gate':gate,'validation':validation,'metric_calibration':calibration,'metric_report':dict(report),'scores':{'frontier':frontier,'successor':successor,'reward':reward},'rankable_frontier':rankable_frontier,'rankable_successor':rankable_successor,'unknown_metrics':unknown,'allocation':_allocation(raw,reward,calibration['reward'],gate,dep,validation),'source':dict(raw),'scoring_source':dict(scoring)}

def _frontier_sort(row):return rank_key(row['scores']['frontier'],str(row['id']))
def _successor_sort(row):
    s=row['scores']['successor'];f=row['scores']['frontier'];sv=float(s['value']) if s.get('status')=='KNOWN' else 0.0;fv=float(f['value']) if f.get('status')=='KNOWN' else 0.0
    return (0 if s.get('status')=='KNOWN' else 1,-sv,-fv,str(row['id']))
def _decision_digest(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def orchestration_law()->Dict[str,Any]:
    return {'version':AOR_VERSION,'run':list(RUN_STAGES),'seed_law':'SX+ = dedup(SX U T(SX))','transform_bank':list(TRANSFORMS),'graph':{'edge_types':list(EDGE_TYPES),'dependency_law':'ready iff prerequisites exist+resolved and candidate is not in an unresolved dependency cycle'},'coordinates':{'fiber':list(COORDINATE_FIBER),'law':'coordinate != identity; UNKNOWN preserved; required gaps block promotion'},'unknown_law':'UNKNOWN != 0; incomplete formulas are non-rankable and route to measurement','metric_law':"cross-candidate arithmetic uses one declared basis; x'=(x-offset)/abs(scale); strict mode blocks uncalibrated operands",'gap_law':'grow = argmax(severity*leverage*information_gain/cost) over KNOWN comparable residuals','frontier_law':'F = argmax(readiness*gain*independence*bridge/cost) over eligible comparable candidates','successor_law':'next = structured highest successor route among budget-allocated eligible comparable candidates; no textual fallback','pareto_law':'preserve nondominated successor alternatives on same scoring basis','budget_law':'exact allocation <=18 costed candidates; larger fallback explicitly heuristic','reward':{'positive':list(REWARD_POSITIVE),'negative':list(REWARD_NEGATIVE),'reallocation':'positive reward deepens/replicates/braids; duplicate low reward hibernates without erasure; unknown routes to measurement'},'test':{'branches':list(TEST_BRANCHES),'claim_requires':['procedure','observation','result','witness'],'invalid_claim':'BLOCK_PROMOTION'},'transaction':{'persisted_claim_requires':['commit','receipt','verify'],'invalid_claim':'BLOCK_PROMOTION','fake_success':False},'continuation':{'deadend':['backtrack','nearest_live_branch','reseed_from_residual'],'stop':'only when requested object complete and no actionable pressure remains'}}

def compile_orchestration(seed:Any,candidates:Optional[Iterable[Mapping[str,Any]]]=None,residuals:Optional[Iterable[Mapping[str,Any]]]=None,budget:Optional[Mapping[str,Any]]=None,metric_contract:Optional[Mapping[str,Any]]=None)->Dict[str,Any]:
    source=[dict(x) for x in (candidates or [])];unique={};duplicate_ids=[]
    for i,item in enumerate(source):
        ident=candidate_id(item,i)
        if ident in unique:duplicate_ids.append(ident);continue
        unique[ident]=item
    source=list(unique.values());deps=dependency_graph(source);rows=[];calibration_plan=[]
    for i,raw in enumerate(source):
        ident=candidate_id(raw,i);scoring,report=normalize_item(raw,metric_contract);row=_candidate_row(raw,scoring,report,i,deps['readiness'].get(ident,{'ready':True,'blockers':[]}));rows.append(row);calibration_plan.extend(calibration_requests(ident,report))
    frontier=sorted(rows,key=_frontier_sort);executable=[r for r in frontier if r['rankable_frontier']];successor_frontier=sorted((r for r in rows if r['rankable_successor']),key=_successor_sort);measurement_frontier=[r for r in frontier if r['unknown_metrics']];calibration_frontier=[r for r in frontier if any(r['metric_calibration'][n]['status']=='BLOCKED' for n in ('frontier','successor','reward'))];validation_frontier=[r for r in frontier if r['validation']['status']=='BLOCKED'];measurement_plan=measurement_requests(frontier);pareto_ids=pareto_successor_frontier(successor_frontier)
    allocation_plan=allocate_budget(executable,budget);budget_active=bool((budget or {}).get('total_cost') is not None or (budget or {}).get('max_branches') is not None);allocated_ids=set(allocation_plan.get('selected',[]))
    if allocation_plan.get('status')=='INVALID_BUDGET':budgeted=[]
    elif budget_active:budgeted=[r for r in successor_frontier if r['id'] in allocated_ids]
    else:budgeted=successor_frontier
    residual_rows=[]
    for i,raw0 in enumerate(residuals or []):
        raw=dict(raw0);ident=str(raw.get('id') or raw.get('name') or f'residual:{i:04d}');scoring,report=normalize_item(raw,metric_contract);cal=formula_calibration(report,'residual');residual_rows.append({'id':ident,'score':residual_score(scoring),'metric_calibration':cal,'metric_report':report,'source':raw,'scoring_source':scoring})
        for req in calibration_requests(ident,report):
            if req['formula']=='residual':calibration_plan.append(req)
    residual_frontier=sorted(residual_rows,key=lambda r:rank_key(r['score'],r['id']));known_residuals=[r for r in residual_frontier if r['score']['status']=='KNOWN' and r['metric_calibration']['ranking_allowed']]
    next_row=budgeted[0] if budgeted else None;next_id=next_row['id'] if next_row else None;explanation=decision_explanation(frontier,next_id,allocated_ids,budget_active);metric_summary=contract_summary(metric_contract);reward_reallocation=reallocation_plan(frontier);calibration_plan=sorted(calibration_plan,key=lambda x:(not x['strict_block'],x['candidate'],x['formula']));successor=successor_packet(next_row,budgeted,known_residuals,measurement_plan,calibration_plan,deps['cycles'],(budget or {}).get('return_coordinate'))
    decision={'metric_basis':metric_summary,'budget_allocation':{k:allocation_plan.get(k) for k in ('status','solver','optimality','capacity','max_branches','selected','used','remaining','utility')},'executable_frontier':[r['id'] for r in executable],'successor_frontier':[r['id'] for r in successor_frontier],'budgeted_successor_frontier':[r['id'] for r in budgeted],'pareto_successor_frontier':pareto_ids,'measurement_frontier':[r['id'] for r in measurement_frontier],'calibration_frontier':[r['id'] for r in calibration_frontier],'validation_frontier':[r['id'] for r in validation_frontier],'grow':known_residuals[0]['id'] if known_residuals else None,'next':next_id,'successor_status':successor['status'],'dependency_cycles':deps['cycles'],'reallocation':{'active':reward_reallocation['active'],'blocked':reward_reallocation['blocked'],'dormant':reward_reallocation['dormant']}}
    result={'kernel':AOR_VERSION,'seed':seed,'budget':dict(budget or {}),'allocation_plan':allocation_plan,'reward_reallocation':reward_reallocation,'metric_contract':metric_summary,'law':orchestration_law(),'extraction_plan':[{'transform':t,'seed':seed} for t in TRANSFORMS],'candidate_dedup':{'mode':'explicit_identity_only','duplicate_ids':duplicate_ids},'dependency_graph':deps,'frontier':frontier,'executable_frontier':executable,'successor_frontier':successor_frontier,'budgeted_successor_frontier':budgeted,'pareto_successor_frontier':pareto_ids,'measurement_frontier':measurement_frontier,'measurement_plan':measurement_plan,'calibration_frontier':calibration_frontier,'calibration_plan':calibration_plan,'validation_frontier':validation_frontier,'residual_frontier':residual_frontier,'grow':known_residuals[0] if known_residuals else None,'next':next_row,'successor':successor,'decision_explanation':explanation,'return':{'required':['result','math','graph','coordinates','evidence','residuals','witnesses','delta','next'],'missing_witness':'downgrade_and_block_claimed_test','missing_coordinate':'repair_before_promotion','unknown_metric':'measure_not_zero','uncalibrated_metric':'calibrate_before_ranking_when_strict','dependency_blocked':'resolve_dependency','invalid_budget':'block_budgeted_successor','invalid_persistence_claim':'block_promotion_until_commit_receipt_verify','error':['rollback','branch'],'high_residual':'continue'}};result['decision_digest']=_decision_digest(decision);return result
