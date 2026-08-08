from __future__ import annotations


def call(adaptive,name,a):
    if name=='athena_gp_hyperfit': return adaptive.gp_hyperfit(a['context_key'],a.get('length_scales'),a.get('signal_variances'),a.get('noise_variances'),a.get('apply',False),a.get('expected_observation_count'))
    if name=='athena_gp_decision_evsi': return adaptive.gp_decision_evsi(a['context_key'],a['actions'],a['experiments'],a.get('samples',300),a.get('seed',0),a.get('cost_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_latent_project_admg': return adaptive.latent_project_admg(a['edges'],a['latent_nodes'],a.get('observed_nodes'))
    if name=='athena_causal_tmle_ensemble': return adaptive.causal_tmle_ensemble(a['samples'],a['treatment'],a['outcome'],a.get('adjustment'),a.get('assumptions'),a.get('propensity_clip',.05))
    if name=='athena_sensitivity_rr_surface': return adaptive.sensitivity_rr_surface(a['observed_rr'],a['exposure_confounder_rrs'],a['outcome_confounder_rrs'])
    if name=='athena_bapomdp_solve': return adaptive.bapomdp_solve(a['states'],a['initial_state_belief'],a['models'],a.get('horizon',3),a.get('discount',.95),a.get('max_nodes',150000))
    if name=='athena_evidence_dependence_interval': return adaptive.evidence_dependence_interval(a['scope'],a['features'],a.get('confidence_z',1.96),a.get('l2',1e-4))
    raise KeyError(name)
