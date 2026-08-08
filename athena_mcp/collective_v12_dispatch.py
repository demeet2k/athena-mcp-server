from __future__ import annotations

from .collective_robust import CollectiveRobustRuntime
from .collective_v13_dispatch import call as call_v13
from .collective_v13_protocol import COLLECTIVE_V13_TOOLS

V13_NAMES={t['name'] for t in COLLECTIVE_V13_TOOLS}


def call(joint,name,a):
    if name in V13_NAMES:return call_v13(CollectiveRobustRuntime(joint),name,a)
    if name=='athena_gp_hyperposterior': return joint.gp_hyperposterior(a['context_key'],a.get('candidates'))
    if name=='athena_gp_bma_predict': return joint.gp_bma_predict(a['context_key'],a['features'],a.get('candidates'),a.get('include_observation_noise',True))
    if name=='athena_gp_sparse_predict': return joint.gp_sparse_predict(a['context_key'],a['features'],a.get('inducing_count',16),a.get('include_observation_noise',True))
    if name=='athena_gp_bma_decision_evsi': return joint.gp_bma_decision_evsi(a['context_key'],a['actions'],a['experiments'],a.get('candidates'),a.get('samples',300),a.get('seed',0),a.get('cost_weight',1.0),a.get('risk_weight',1.0))
    if name=='athena_pag_candidate_discover': return joint.pag_candidate_discover(a['samples'],a.get('variables'),a.get('alpha',.05),a.get('max_conditioning',2))
    if name=='athena_longitudinal_gformula': return joint.longitudinal_gformula(a['samples'],a['treatment1'],a['intermediate'],a['treatment2'],a['outcome'],a.get('baseline'),a.get('regimes'),a.get('assumptions'))
    if name=='athena_chance_resource_select': return joint.chance_resource_select(a['candidates'],a['budgets'],a.get('alpha',.05),a.get('exact_limit',18))
    raise KeyError(name)
