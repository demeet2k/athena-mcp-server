from __future__ import annotations


def call(runtime, name, a):
    if name == 'athena_regime_resolve':
        return runtime.resolve_regime(a['signals'], a.get('domain'))
    if name == 'athena_bandit_select':
        return runtime.bandit_select(a['arms'], a['context'], a.get('regime'), a.get('signals'), a.get('exploration_alpha',0.35), a.get('transfer_tau',8.0), a.get('policy_scope','global'))
    if name == 'athena_bandit_observe':
        return runtime.bandit_observe(a['arm_id'], a['reward'], a['features'], a['regime'], a.get('actor','agent'), a.get('global_transfer_weight',1.0))
    if name == 'athena_credit_assign':
        return runtime.assign_credit(a['outcome_key'], a['outcome_delta'], a['interventions'], a.get('design'), a.get('regime','GLOBAL'), a.get('actor','agent'))
    if name == 'athena_credit_summary':
        return runtime.credit_summary(a.get('intervention_id'), a.get('regime'), a.get('limit',500))
    if name == 'athena_worker_cost_observe':
        return runtime.worker_cost_observe(a['worker_id'], a['task_id'], a['resources'], a.get('budget'), a.get('useful_output'), a.get('scope','global'), a.get('actor','agent'))
    if name == 'athena_budget_schedule':
        return runtime.budget_schedule(a['tasks'], a['workers'], a['remaining_budget'], a.get('scope','global'), a.get('max_assignments_per_worker',1), a.get('alpha',1.0), a.get('beta',1.0))
    if name == 'athena_diffusion_observe':
        return runtime.diffusion_observe(a['source_scale'], a['target_scale'], a['transfer_utility'], a.get('evidence_weight',1.0), a.get('causal_confidence',0.0), a.get('actor','agent'))
    if name == 'athena_diffusion_matrix':
        return runtime.diffusion_matrix()
    if name == 'athena_pheromone_adaptive_reinforce':
        return runtime.pheromone_adaptive_reinforce(a['source_scale'], a['coordinates'], a['observations'], a.get('age'), a.get('evaporation_rate',0.08), a.get('deposit_gain',0.35), a.get('actor','agent'))
    if name == 'athena_antibody_execute_regressions':
        return runtime.execute_antibody_regressions(a['antibody_id'], a.get('timeout_s',20.0), a.get('max_refs',8), a.get('record_outcome',True), a.get('actor','agent'))
    if name == 'athena_rollout_simulate':
        return runtime.rollout_simulate(a['trajectories'], a.get('initial_context'), a.get('regime','GLOBAL'), a.get('discount',0.92), a.get('exploration_alpha',0.20), a.get('max_steps',16))
    if name == 'athena_projection_prepare':
        return runtime.projection_prepare(a['topology_id'], a['expected_topology_version'], a.get('expected_semantic_eid'), a.get('expected_git_head'), a.get('actor','agent'))
    if name == 'athena_projection_status':
        return runtime.projection_status(a['projection_id'])
    raise KeyError(name)
