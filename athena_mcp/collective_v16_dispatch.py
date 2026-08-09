from __future__ import annotations

from .collective_generalized import (
    approx_error_field,
    coupled_model_robust_policy,
    gaussian_mixture_update,
    longitudinal_dr_multistage_crossfit,
    ordered_dag_posterior,
)


def call(generalized, name, a):
    if name == 'athena_ordered_dag_posterior':
        return ordered_dag_posterior(
            a['samples'], a['order'], a.get('prior_edge_probability', .25), a.get('top_k', 16), a.get('calibration_examples'),
        )
    if name == 'athena_longitudinal_dr_multistage_crossfit':
        return longitudinal_dr_multistage_crossfit(
            a['samples'], a['stages'], a['outcome'], a['policies'], a.get('folds', 2), a.get('seed', 0), a.get('propensity_clip', .05),
        )
    if name == 'athena_gaussian_mixture_update':
        return gaussian_mixture_update(a['variables'], a['components'], a['observation'])
    if name == 'athena_approx_error_field':
        return approx_error_field(
            a['feature_order'], a['witnesses'], a['queries'], a.get('bandwidth', 1.0), a.get('ridge', 1e-3),
            a.get('folds', 5), a.get('coverage', .9), a.get('seed', 0), a.get('max_support_distance'),
        )
    if name == 'athena_coupled_model_robust_policy':
        return coupled_model_robust_policy(
            a['states'], a['initial_state'], a['models'], a['policies'], a['horizon'], a.get('discount', 1.0),
        )
    raise KeyError(name)
