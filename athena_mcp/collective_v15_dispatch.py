from __future__ import annotations

from .collective_v15_calibration import structural_reliability_calibrate
from .collective_v15_history import validate_longitudinal_baseline
from .collective_v15_longitudinal import longitudinal_tmle_crossfit
from .collective_v15_policy import sequential_dr_policy_crossfit


def call(calibrated, name, a):
    if name == 'athena_structural_reliability_calibrate':
        return structural_reliability_calibrate(
            a['calibration_examples'], a.get('supports'), a.get('folds', 5), a.get('seed', 0),
        )
    if name == 'athena_longitudinal_tmle_crossfit':
        baseline=validate_longitudinal_baseline(
            a.get('baseline'), a['treatment1'], a['intermediate'], a['treatment2'], a['outcome'],
        )
        return longitudinal_tmle_crossfit(
            calibrated, a['samples'], a['treatment1'], a['intermediate'], a['treatment2'], a['outcome'],
            baseline, a.get('regimes'), a.get('assumptions'), a.get('propensity_clip', .05),
            a.get('folds', 2), a.get('seed', 0),
        )
    if name == 'athena_sequential_dr_policy_crossfit':
        return sequential_dr_policy_crossfit(
            calibrated, a['samples'], a['treatment1'], a['intermediate'], a['treatment2'], a['outcome'], a['policies'],
            a.get('baseline'), a.get('assumptions'), a.get('propensity_clip', .05),
            a.get('folds', 2), a.get('seed', 0),
        )
    if name == 'athena_joint_gaussian_update':
        return calibrated.joint_gaussian_update(a['variables'], a['mean'], a['covariance'], a['observation'])
    if name == 'athena_joint_gaussian_control':
        return calibrated.joint_gaussian_control(
            a['variables'], a['mean'], a['covariance'], a['actions'], a.get('cvar_alpha', .1),
            a.get('risk_weight', 1.0), a.get('cost_weight', 1.0),
        )
    if name == 'athena_approx_error_transport':
        return calibrated.approx_error_transport(
            a['feature_order'], a['witnesses'], a['queries'], a['lipschitz_bound'],
            a.get('max_transport_radius'), a.get('margin_safety', .5),
        )
    if name == 'athena_multistage_tv_dro_plan':
        return calibrated.multistage_tv_dro_plan(
            a['states'], a['initial_state'], a['actions_by_state'], a['horizon'], a['tv_radius'],
            a.get('discount', 1.0),
        )
    raise KeyError(name)
