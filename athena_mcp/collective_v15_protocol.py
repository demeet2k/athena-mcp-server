from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {
        'name': name,
        'description': description,
        'inputSchema': {
            'type': 'object',
            'required': list(required),
            'properties': properties or {},
            'additionalProperties': False,
        },
    }

STR={'type':'string'};NUM={'type':'number'};OBJ={'type':'object'};BOOL={'type':'boolean'};INT={'type':'integer'}
NONEMPTY_STR={'type':'string','minLength':1}

COLLECTIVE_V15_TOOLS=[
    _tool(
        'athena_structural_reliability_calibrate',
        'Calibrate structural support against externally labelled correctness with weighted out-of-fold isotonic reliability. Duplicate support coordinates are pooled before PAV. Read-only; calibrated reliability is not a causal graph posterior.',
        ('calibration_examples',),
        {
            'calibration_examples': {'type':'array','minItems':40,'maxItems':10000,'items':{'type':'object'}},
            'supports': {'type':'array','maxItems':512,'items':{'type':'number','minimum':0,'maximum':1}},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_longitudinal_tmle_crossfit',
        'Cross-fit the bounded binary two-timepoint sequential logistic TMLE across held-out folds with explicit baseline/time-order validation. Assumption-scoped; not a general longitudinal TMLE theorem.',
        ('samples','treatment1','intermediate','treatment2','outcome'),
        {
            'samples': {'type':'array','minItems':160,'maxItems':20000,'items':{'type':'object'}},
            'treatment1': NONEMPTY_STR,
            'intermediate': NONEMPTY_STR,
            'treatment2': NONEMPTY_STR,
            'outcome': NONEMPTY_STR,
            'baseline': {'type':'array','maxItems':16,'uniqueItems':True,'items':NONEMPTY_STR},
            'regimes': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'object'}},
            'assumptions': OBJ,
            'propensity_clip': {'type':'number','exclusiveMinimum':0,'exclusiveMaximum':0.5},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_sequential_dr_policy_crossfit',
        'Estimate deterministic two-timepoint dynamic-policy value with out-of-fold sequential AIPW nuisance predictions. A1 policies may use baseline only; A2 policies may use baseline+A1+L1 only. PLAN_ONLY and assumption-scoped.',
        ('samples','treatment1','intermediate','treatment2','outcome','policies'),
        {
            'samples': {'type':'array','minItems':180,'maxItems':20000,'items':{'type':'object'}},
            'treatment1': NONEMPTY_STR,
            'intermediate': NONEMPTY_STR,
            'treatment2': NONEMPTY_STR,
            'outcome': NONEMPTY_STR,
            'policies': {'type':'array','minItems':1,'maxItems':32,'items':{'type':'object'}},
            'baseline': {'type':'array','maxItems':16,'uniqueItems':True,'items':NONEMPTY_STR},
            'assumptions': OBJ,
            'propensity_clip': {'type':'number','exclusiveMinimum':0,'exclusiveMaximum':0.5},
            'folds': {'type':'integer','minimum':2,'maximum':10},
            'seed': INT,
        },
    ),
    _tool(
        'athena_joint_gaussian_update',
        'Perform the exact finite-dimensional multivariate-Gaussian posterior update for one declared linear-Gaussian observation. Unknown coefficient coordinates and non-finite state fail closed. Model state only; not general continuous Bayes.',
        ('variables','mean','covariance','observation'),
        {
            'variables': {'type':'array','minItems':1,'maxItems':16,'uniqueItems':True,'items':NONEMPTY_STR},
            'mean': {'type':'array','minItems':1,'maxItems':16,'items':NUM},
            'covariance': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'array','items':NUM}},
            'observation': OBJ,
        },
    ),
    _tool(
        'athena_joint_gaussian_control',
        'Rank unique linear actions under a declared multivariate Gaussian belief using exact moments, lower-tail Normal CVaR, cost and Pareto preservation. Unknown coefficient coordinates fail closed. PLAN_ONLY.',
        ('variables','mean','covariance','actions'),
        {
            'variables': {'type':'array','minItems':1,'maxItems':16,'uniqueItems':True,'items':NONEMPTY_STR},
            'mean': {'type':'array','minItems':1,'maxItems':16,'items':NUM},
            'covariance': {'type':'array','minItems':1,'maxItems':16,'items':{'type':'array','items':NUM}},
            'actions': {'type':'array','minItems':1,'maxItems':64,'items':{'type':'object'}},
            'cvar_alpha': {'type':'number','exclusiveMinimum':0,'maximum':0.5},
            'risk_weight': {'type':'number','minimum':0},
            'cost_weight': {'type':'number','minimum':0},
        },
    ),
    _tool(
        'athena_approx_error_transport',
        'Transport witnessed approximation error through a caller-declared Lipschitz envelope consistent with supplied witness pairs. Geometric nearest, global-envelope, and radius-eligible transport witnesses remain distinct; certificate is conditional on the declared bound.',
        ('feature_order','witnesses','queries','lipschitz_bound'),
        {
            'feature_order': {'type':'array','minItems':1,'maxItems':32,'uniqueItems':True,'items':NONEMPTY_STR},
            'witnesses': {'type':'array','minItems':2,'maxItems':4096,'items':{'type':'object'}},
            'queries': {'type':'array','minItems':1,'maxItems':512,'items':{'type':'object'}},
            'lipschitz_bound': {'type':'number','minimum':0},
            'max_transport_radius': {'type':'number','minimum':0},
            'margin_safety': {'type':'number','minimum':0,'maximum':1},
        },
    ),
    _tool(
        'athena_multistage_tv_dro_plan',
        'Solve a bounded finite-horizon robust dynamic program under state-action rectangular total-variation ambiguity around supplied transition distributions. Unknown state coordinates/non-finite transitions fail closed. PLAN_ONLY.',
        ('states','initial_state','actions_by_state','horizon','tv_radius'),
        {
            'states': {'type':'array','minItems':1,'maxItems':24,'uniqueItems':True,'items':NONEMPTY_STR},
            'initial_state': NONEMPTY_STR,
            'actions_by_state': OBJ,
            'horizon': {'type':'integer','minimum':1,'maximum':8},
            'tv_radius': {'type':'number','minimum':0,'maximum':1},
            'discount': {'type':'number','minimum':0,'maximum':1},
        },
    ),
]
