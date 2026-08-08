from __future__ import annotations

from .collective_adaptive import CollectiveAdaptiveRuntime
from .collective_v11_dispatch import call as call_v11
from .collective_v11_protocol import COLLECTIVE_V11_TOOLS

V11_NAMES={t['name'] for t in COLLECTIVE_V11_TOOLS}


def call(prob,name,a):
    if name in V11_NAMES: return call_v11(CollectiveAdaptiveRuntime(prob),name,a)
    if name=='athena_gp_register': return prob.gp_register(a['context_key'],a['features'],a.get('length_scale',1.0),a.get('signal_variance',1.0),a.get('noise_variance',.05),a.get('metadata'),a.get('replace',False))
    if name=='athena_gp_state': return prob.gp_state(a['context_key'])
    if name=='athena_gp_observe': return prob.gp_observe(a['context_key'],a['features'],a['target'],a.get('evidence_ref',''),a.get('actor','agent'))
    if name=='athena_gp_predict': return prob.gp_predict(a['context_key'],a['features'],a.get('include_observation_noise',True))
    if name=='athena_pc_stable_discover': return prob.pc_stable_discover(a['samples'],a.get('variables'),a.get('alpha',.05),a.get('max_conditioning',2))
    if name=='athena_causal_tmle_binary': return prob.causal_tmle_binary(a['samples'],a['treatment'],a['outcome'],a.get('adjustment'),a.get('assumptions'),a.get('propensity_clip',.05))
    if name=='athena_sensitivity_evalue': return prob.sensitivity_evalue(a['risk_ratio'],a.get('ci_limit'))
    if name=='athena_pomdp_solve': return prob.pomdp_solve(a['states'],a['initial_belief'],a['actions'],a.get('horizon',3),a.get('discount',.95),a.get('max_nodes',100000))
    if name=='athena_evidence_dependence_observe': return prob.dependence_observe(a['scope'],a['features'],a['label'],a.get('weight',1.0),a.get('evidence_ref',''))
    if name=='athena_evidence_dependence_fit': return prob.dependence_fit(a['scope'],a.get('l2',.01),a.get('iterations',600))
    if name=='athena_evidence_dependence_predict': return prob.dependence_predict(a['scope'],a['features'])
    raise KeyError(name)
