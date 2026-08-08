from __future__ import annotations


def _partial(inference,a):
    out=inference.structure_partial(a['samples'],a.get('variables'),a.get('association_threshold',.15),a.get('resamples',50),a.get('support_threshold',.7),a.get('seed',0))
    if not out.get('collider_candidates'):
        out['collider_candidates']=list((out.get('bootstrap') or {}).get('stable_v_structure_candidates') or [])
    return out


def call(inference,name,a):
    if name=='athena_gaussian_belief_register': return inference.gaussian_belief_register(a['context_key'],a['parameters'],a.get('mean'),a.get('prior_variance',1.0),a.get('noise_variance',1.0),a.get('metadata'),a.get('replace',False))
    if name=='athena_gaussian_belief_state': return inference.gaussian_belief_state(a['context_key'])
    if name=='athena_gaussian_belief_observe': return inference.gaussian_belief_observe(a['context_key'],a['features'],a['target'],a.get('weight',1.0),a.get('noise_variance'),a.get('evidence_ref',''),a.get('actor','agent'))
    if name=='athena_decision_evpi': return inference.decision_evpi(a['context_key'],a['actions'],a.get('samples',500),a.get('seed',0))
    if name=='athena_decision_evsi': return inference.decision_evsi(a['context_key'],a['actions'],a['experiments'],a.get('samples',300),a.get('seed',0),a.get('cost_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_belief_policy_multistage': return inference.belief_policy_multistage(a['context_key'],a['actions'],a.get('horizon',2),a.get('discount',.95),a.get('information_weight',0.0))
    if name=='athena_causal_aipw': return inference.causal_aipw(a['samples'],a['treatment'],a['outcome'],a.get('adjustment'),a.get('assumptions'),a.get('propensity_clip',.05))
    if name=='athena_causal_robustness': return inference.causal_robustness(a['samples'],a['treatment'],a['outcome'],a['adjustment'],a.get('assumptions'))
    if name=='athena_structure_partial': return _partial(inference,a)
    if name=='athena_evidence_dependence_probability': return inference.evidence_dependence_probability(a['claim_id'],a.get('coefficients'),a.get('dimensions'),a.get('min_confidence',.5))
    raise KeyError(name)
