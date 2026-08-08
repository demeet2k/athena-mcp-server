from __future__ import annotations


def call(science, core, name, a):
    if name=='athena_bayes_predict': return science.bayes_predict(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_bayes_observe': return science.bayes_observe(a['features'],a['reward'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('actor','agent'),a.get('weight',1.0),a.get('target_coverage',.90),a.get('ridge',1.0))
    if name=='athena_uncertainty_calibrate': return science.uncertainty_calibration(a.get('scope','global'),a.get('regime'),a.get('arm_id'),a.get('target_coverage',.90))
    if name=='athena_experiment_design': return science.experiment_design(a['hypotheses'],a['experiments'],a.get('sample_size',20),a.get('control_fraction',.5),a.get('cost_weight',.10),a.get('risk_weight',.20))
    if name=='athena_interaction_credit': return science.interaction_credit(a['analysis_key'],a['experiments'],a.get('actor','agent'))
    if name=='athena_delayed_credit_record': return science.delayed_credit_record(a['action_id'],a['outcome_key'],a['outcome_delta'],a['delay_cycles'],a['causal_confidence'],a.get('discount',.95),a.get('regime','GLOBAL'),a.get('actor','agent'))
    if name=='athena_delayed_credit_summary': return science.delayed_credit_summary(a.get('action_id'),a.get('regime'),a.get('limit',1000))
    if name=='athena_transition_observe': return science.transition_observe(a['action_id'],a['before'],a['after'],a.get('evidence_weight',1.0),a.get('actor','agent'))
    if name=='athena_transition_predict': return science.transition_predict(a['action_id'],a['context'],a.get('prior_strength',5.0))
    if name=='athena_rollout_learned': return science.rollout_learned(a['initial_context'],a['trajectories'],a.get('discount',.95),a.get('uncertainty_alpha',1.0),a.get('prior_strength',5.0))
    if name=='athena_schedule_multiperiod': return science.schedule_multiperiod(a['tasks'],a['workers'],a.get('horizon',12),a.get('budget'),a.get('beam_width',128),a.get('scope','global'),a.get('discount',.97))
    if name=='athena_witness_cell': return science.execute_witness_cell(a['regression_ref'],a.get('timeout_s',20.0),a.get('memory_mb',512),a.get('cpu_s',10),a.get('actor','agent'))
    if name=='athena_regime_geometry_observe': return science.regime_geometry_observe(a['signals'],a['reward'],a.get('cluster_id'),a.get('domain'),a.get('weight',1.0))
    if name=='athena_regime_geometry_resolve': return science.regime_geometry_resolve(a['signals'],a.get('top_k',5),a.get('domain'))
    if name=='athena_pareto_frontier': return science.pareto_frontier(a['candidates'],a.get('directions'),a.get('epsilon',0.0),a.get('robust',False))
    if name=='athena_projection_compensate': return science.projection_compensate(core,a['projection_id'],a.get('expected_semantic_eid'),a.get('actor','agent'))
    raise KeyError(name)
