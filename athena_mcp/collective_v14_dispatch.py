from __future__ import annotations


def call(synthesis, name, a):
    if name == 'athena_joint_factor_belief':
        return synthesis.joint_factor_belief(a['axes'], a.get('compatibility'), a.get('likelihood_by_state'))
    if name == 'athena_structural_bootstrap_ensemble':
        return synthesis.structural_bootstrap_ensemble(
            a['samples'], a.get('variables'), a.get('bootstrap_runs', 32), a.get('alpha', .05),
            a.get('max_conditioning', 2), a.get('stable_threshold', .7), a.get('seed', 0),
        )
    if name == 'athena_joint_science_evi':
        return synthesis.joint_science_evi(
            a['joint_states'], a['actions'], a['experiments'], a.get('information_weight', 1.0),
            a.get('decision_weight', 1.0), a.get('cost_weight', 1.0), a.get('risk_weight', 1.0),
        )
    if name == 'athena_sequential_dr_policy_value':
        return synthesis.sequential_dr_policy_value(
            a['samples'], a['treatment1'], a['intermediate'], a['treatment2'], a['outcome'], a['policies'],
            a.get('baseline'), a.get('assumptions'), a.get('propensity_clip', .05),
        )
    if name == 'athena_joint_policy_robust':
        return synthesis.joint_policy_robust(
            a['joint_states'], a['policies'], a.get('cvar_alpha', .1), a.get('risk_weight', 1.0),
            a.get('regret_weight', 1.0), a.get('cost_weight', 1.0),
        )
    if name == 'athena_gp_resolution_route':
        return synthesis.gp_resolution_route(
            a['context_key'], a['actions'], a.get('inducing_counts'), a.get('margin_safety', .5),
            a.get('include_observation_noise', True),
        )
    if name == 'athena_two_stage_resource_plan':
        return synthesis.two_stage_resource_plan(
            a['first_stage'], a['scenarios'], a.get('risk_weight', 0.0), a.get('exact_limit', 16),
        )
    raise KeyError(name)
