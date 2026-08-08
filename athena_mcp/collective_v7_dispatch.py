from __future__ import annotations

from .collective_belief import CollectiveBeliefRuntime
from .collective_v8_dispatch import call as call_v8
from .collective_v8_protocol import COLLECTIVE_V8_TOOLS

V8_NAMES={t['name'] for t in COLLECTIVE_V8_TOOLS}


def _belief(dual):
    return CollectiveBeliefRuntime(dual)


def call(dual,name,a):
    if name in V8_NAMES: return call_v8(_belief(dual),name,a)
    if name=='athena_uncertainty_decompose': return dual.uncertainty_decompose(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('target_coverage',.90),a.get('ridge',1.0),a.get('ood_gain',1.5))
    if name=='athena_prequential_interval': return dual.prequential_interval(a['features'],a['regime'],a['arm_id'],a.get('scope','global'),a.get('coverage',.90),a.get('min_scores',8),a.get('ood_gain',1.5))
    if name=='athena_causal_skeleton_discover': return dual.causal_skeleton_discover(a['samples'],a.get('variables'),a.get('association_threshold',.15),a.get('max_conditioning',1))
    if name=='athena_state_transition_model': return dual.state_transition_model(a['action_id'],a['context'],a.get('ridge',1.0),a.get('max_features',8))
    if name=='athena_scenario_evaluate': return dual.scenario_evaluate(a['initial_context'],a['actions'],a['trajectories'],a.get('discount',.95),a.get('scenario_sigma',1.0),a.get('cvar_alpha',.20),a.get('risk_aversion',.25),a.get('ridge',1.0))
    if name=='athena_dual_control_plan': return dual.dual_control_plan(a['initial_context'],a['actions'],a.get('horizon',3),a.get('beam_width',64),a.get('discount',.95),a.get('risk_aversion',.25),a.get('information_weight',.20),a.get('ridge',1.0))
    if name=='athena_causal_identify_extended': return dual.causal_identify_extended(a['method'],a['treatment'],a['outcome'],a['edges'],a.get('observed_nodes'),a.get('mediators'),a.get('instruments'),a.get('assumptions'),a.get('max_adjustment_size',4),a.get('actor','agent'))
    if name=='athena_replication_independence': return dual.replication_independence(a['claim_id'],a.get('dimensions'),a.get('min_confidence',.5))
    if name=='athena_replication_design': return dual.replication_design(a['claim_id'],a['candidates'],a.get('mode','REPLICATION'),a.get('dimensions'),a.get('cost_weight',.10),a.get('risk_weight',.20))
    raise KeyError(name)
