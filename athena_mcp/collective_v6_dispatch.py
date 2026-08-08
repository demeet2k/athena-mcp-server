from __future__ import annotations

import itertools

from .collective_dual_control import CollectiveDualControlRuntime
from .collective_v7_dispatch import call as call_v7
from .collective_v7_protocol import COLLECTIVE_V7_TOOLS

V7_NAMES={t['name'] for t in COLLECTIVE_V7_TOOLS}


def _dual(discovery):
    return CollectiveDualControlRuntime(discovery)


def _experiment_generate(discovery,a):
    hypotheses=a['hypotheses']; factors=a['factors']
    if len(hypotheses)<2: raise ValueError('need at least two hypotheses')
    if not factors: raise ValueError('factors must not be empty')
    parsed=[]
    for f in factors:
        name=str(f.get('name','')).strip();levels=list(f.get('levels',[]))
        if not name or not levels: raise ValueError('each factor needs name and non-empty levels')
        parsed.append((name,levels,f))
    experiments=[];limit=max(1,min(int(a.get('max_candidates',256)),4096))
    for idx,values in enumerate(itertools.product(*[x[1] for x in parsed])):
        if idx>=limit: break
        assignment={parsed[i][0]:values[i] for i in range(len(parsed))}
        cost=0.0;risk=0.0;ethical=True;feasibility=1.0
        for name,_,meta in parsed:
            v=assignment[name];key=str(v)
            cost+=float((meta.get('costs') or {}).get(key,meta.get('cost',0.0)) or 0.0)
            risk=max(risk,float((meta.get('risks') or {}).get(key,meta.get('risk',0.0)) or 0.0))
            if v in set(meta.get('forbidden_levels',[])): ethical=False
            fm=meta.get('feasibility',1.0)
            feasibility*=max(0.0,min(1.0,float(fm.get(key,1.0) if isinstance(fm,dict) else fm)))
        pp={}
        for h in hypotheses:
            hid=str(h.get('id'));p=float(h.get('base_p',.5));effects=h.get('factor_effects') or {}
            for name,value in assignment.items(): p+=float(effects.get(f'{name}={value}',0.0))
            pp[hid]=max(0.0,min(1.0,p))
        experiments.append({'id':'GEN:'+','.join(f'{k}={assignment[k]}' for k in sorted(assignment)),'assignment':assignment,
                            'positive_probability':pp,'cost':cost,'risk':max(0.0,min(1.0,risk)),
                            'feasibility':max(0.0,min(1.0,feasibility)),'ethical':ethical})
    out=discovery.science.experiment_design(hypotheses,experiments,a.get('sample_size',20),.5,a.get('cost_weight',.10),a.get('risk_weight',.20))
    return {**out,'generated_count':len(experiments),'factor_space':[x[0] for x in parsed],
            'law':'candidate experiments are generated only from declared factor levels/effect models; expected information gain remains DESIGN_ONLY'}


def call(discovery,name,a):
    if name in V7_NAMES: return call_v7(_dual(discovery),name,a)
    if name=='athena_ood_observe': return discovery.ood_observe(a['features'],a['regime'],a.get('scope','global'))
    if name=='athena_ood_score': return discovery.ood_score(a['features'],a['regime'],a.get('scope','global'),a.get('ridge',.05))
    if name=='athena_nonlinear_predict': return discovery.nonlinear_predict(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('target_coverage',.90),a.get('ridge',1.0),a.get('ood_gain',1.5))
    if name=='athena_nonlinear_observe': return discovery.nonlinear_observe(a['features'],a['reward'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('actor','agent'),a.get('weight',1.0),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_experiment_generate': return _experiment_generate(discovery,a)
    if name=='athena_causal_identify': return discovery.causal_identify(a['treatment'],a['outcome'],a['edges'],a.get('observed_nodes'),a.get('assumptions'),a.get('max_adjustment_size',4),a.get('actor','agent'))
    if name=='athena_interaction_higher_order': return discovery.higher_order_interactions(a['experiments'],a.get('max_order',4),a.get('design_confidence',.5))
    if name=='athena_transition_distribution': return discovery.transition_distribution(a['action_id'],a['context'],a.get('prior_strength',5.0))
    if name=='athena_mpc_plan': return discovery.mpc_plan(a['initial_context'],a['actions'],a.get('horizon',3),a.get('beam_width',64),a.get('discount',.95),a.get('risk_aversion',.25),a.get('prior_strength',5.0))
    if name=='athena_schedule_certified':
        budget=a.get('budget') or {}
        if budget:
            missing=[str(t.get('id','?')) for t in a['tasks'] if any(k not in (t.get('resource_cost') or {}) for k in budget)]
            if missing:
                fallback=discovery.science.schedule_multiperiod(a['tasks'],a['workers'],a.get('horizon',24),budget,128,'global',a.get('discount',.97))
                return {**fallback,'certificate':'NONE_UNKNOWN_RESOURCE_COST','incomplete_cost_tasks':missing,'law':'exact certification requires every constrained resource dimension to be declared for every task; UNKNOWN_COST != ZERO_COST'}
        return discovery.schedule_certified(a['tasks'],a['workers'],a.get('horizon',24),budget,a.get('max_nodes',200000),a.get('exact_task_limit',8),a.get('discount',.97))
    if name=='athena_witness_capsule': return discovery.witness_capsule(a['regression_ref'],a.get('timeout_s',20.0))
    if name=='athena_pareto_bandit_select': return discovery.pareto_bandit_select(a['candidates'],a.get('directions'),a.get('exploration_weight',.5))
    if name=='athena_claim_register': return discovery.claim_register(a['claim_key'],a['statement'],a.get('scope','global'))
    if name=='athena_claim_witness': return discovery.claim_witness(a['claim_id'],a['kind'],a['result'],a['independence_key'],a.get('confidence',1.0),a.get('evidence'),a.get('actor','agent'))
    if name=='athena_claim_state': return discovery.claim_state(a['claim_id'],a.get('min_independent_support',2))
    raise KeyError(name)
