from __future__ import annotations


def call(discovery,name,a):
    if name=='athena_ood_observe': return discovery.ood_observe(a['features'],a['regime'],a.get('scope','global'))
    if name=='athena_ood_score': return discovery.ood_score(a['features'],a['regime'],a.get('scope','global'),a.get('ridge',.05))
    if name=='athena_nonlinear_predict': return discovery.nonlinear_predict(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('target_coverage',.90),a.get('ridge',1.0),a.get('ood_gain',1.5))
    if name=='athena_nonlinear_observe': return discovery.nonlinear_observe(a['features'],a['reward'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('actor','agent'),a.get('weight',1.0),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_experiment_generate': return discovery.experiment_generate(a['hypotheses'],a['factors'],a.get('max_candidates',256),a.get('sample_size',20),a.get('cost_weight',.10),a.get('risk_weight',.20))
    if name=='athena_causal_identify': return discovery.causal_identify(a['treatment'],a['outcome'],a['edges'],a.get('observed_nodes'),a.get('assumptions'),a.get('max_adjustment_size',4),a.get('actor','agent'))
    if name=='athena_interaction_higher_order': return discovery.higher_order_interactions(a['experiments'],a.get('max_order',4),a.get('design_confidence',.5))
    if name=='athena_transition_distribution': return discovery.transition_distribution(a['action_id'],a['context'],a.get('prior_strength',5.0))
    if name=='athena_mpc_plan': return discovery.mpc_plan(a['initial_context'],a['actions'],a.get('horizon',3),a.get('beam_width',64),a.get('discount',.95),a.get('risk_aversion',.25),a.get('prior_strength',5.0))
    if name=='athena_schedule_certified': return discovery.schedule_certified(a['tasks'],a['workers'],a.get('horizon',24),a.get('budget'),a.get('max_nodes',200000),a.get('exact_task_limit',8),a.get('discount',.97))
    if name=='athena_witness_capsule': return discovery.witness_capsule(a['regression_ref'],a.get('timeout_s',20.0))
    if name=='athena_pareto_bandit_select': return discovery.pareto_bandit_select(a['candidates'],a.get('directions'),a.get('exploration_weight',.5))
    if name=='athena_discovery_claim_register': return discovery.claim_register(a['claim_key'],a['statement'],a.get('scope','global'))
    if name=='athena_discovery_claim_witness': return discovery.claim_witness(a['claim_id'],a['kind'],a['result'],a['independence_key'],a.get('confidence',1.0),a.get('evidence'),a.get('actor','agent'))
    if name=='athena_discovery_claim_state': return discovery.claim_state(a['claim_id'],a.get('min_independent_support',2))
    raise KeyError(name)
