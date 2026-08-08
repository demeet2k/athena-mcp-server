from __future__ import annotations


def call(belief,name,a):
    if name=='athena_belief_register': return belief.belief_register(a['context_key'],a['models'],a.get('replace',False))
    if name=='athena_belief_state': return belief.belief_state(a['context_key'])
    if name=='athena_belief_observe': return belief.belief_observe(a['context_key'],a['outcome'],a['likelihoods'],a.get('evidence_ref',''),a.get('actor','agent'))
    if name=='athena_decision_evi': return belief.decision_evi(a['context_key'],a['actions'],a['experiments'],a.get('cost_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_belief_dual_control': return belief.belief_dual_control(a['context_key'],a['actions'],a.get('discount',.95),a.get('information_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_causal_effect_estimate': return belief.causal_effect_estimate(a['method'],a['samples'],a['treatment'],a['outcome'],a.get('adjustment'),a.get('mediator'),a.get('instrument'),a.get('assumptions'))
    if name=='athena_causal_structure_bootstrap': return belief.causal_structure_bootstrap(a['samples'],a.get('variables'),a.get('association_threshold',.15),a.get('resamples',50),a.get('support_threshold',.7),a.get('seed',0))
    if name=='athena_contingent_policy': return belief.contingent_policy(a['context_key'],a['actions'],a['experiment'])
    if name=='athena_evidence_spectral': return belief.evidence_spectral(a['claim_id'],a.get('dimensions'),a.get('min_confidence',.5))
    raise KeyError(name)
