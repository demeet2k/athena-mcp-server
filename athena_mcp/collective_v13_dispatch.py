from __future__ import annotations

from .collective_longitudinal_v13 import longitudinal_tmle as longitudinal_tmle_v13
from .collective_synthesis import CollectiveSynthesisRuntime
from .collective_v14_dispatch import call as call_v14
from .collective_v14_protocol import COLLECTIVE_V14_TOOLS

V14_NAMES={t['name'] for t in COLLECTIVE_V14_TOOLS}


def call(robust,name,a):
    if name in V14_NAMES:return call_v14(CollectiveSynthesisRuntime(robust),name,a)
    if name=='athena_gp_hyperqmc':return robust.gp_hyperqmc(a['context_key'],a.get('bounds'),a.get('samples',96),a.get('seed',0))
    if name=='athena_gp_fitc_predict':return robust.gp_fitc_predict(a['context_key'],a['features'],a.get('inducing_count',16),a.get('include_observation_noise',True))
    if name=='athena_gp_joint_design':return robust.gp_joint_design(a['context_key'],a['actions'],a['experiments'],a.get('bounds'),a.get('hyper_samples',64),a.get('mc_samples',200),a.get('seed',0),a.get('information_weight',1.0),a.get('decision_weight',1.0),a.get('cost_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_fci_lite_discover':return robust.fci_lite_discover(a['samples'],a.get('variables'),a.get('alpha',.05),a.get('max_conditioning',2))
    if name=='athena_longitudinal_tmle':return longitudinal_tmle_v13(robust,a['samples'],a['treatment1'],a['intermediate'],a['treatment2'],a['outcome'],a.get('baseline'),a.get('regimes'),a.get('assumptions'),a.get('propensity_clip',.05))
    if name=='athena_dynamic_policy_value':return robust.dynamic_policy_value(a['samples'],a['treatment1'],a['intermediate'],a['treatment2'],a['outcome'],a['policies'],a.get('baseline'),a.get('assumptions'))
    if name=='athena_dro_resource_select':return robust.dro_resource_select(a['candidates'],a['budgets'],a['covariances'],a.get('ambiguity_radius',0.0),a.get('alpha',.05),a.get('exact_limit',18))
    raise KeyError(name)
