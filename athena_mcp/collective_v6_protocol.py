from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V6_TOOLS=[
    _tool("athena_ood_observe","Update the empirical context distribution used to detect distribution shift for a regime. Observations only; no semantic authority.",( "features","regime"),{"features":OBJ,"regime":STR,"scope":STR}),
    _tool("athena_ood_score","Score a context against the empirical regime distribution using ridge-regularized Mahalanobis geometry plus unseen-feature pressure.",( "features","regime"),{"features":OBJ,"regime":STR,"scope":STR,"ridge":NUM}),
    _tool("athena_nonlinear_predict","Degree-2 polynomial-basis Bayesian prediction with full-covariance V5 posterior and OOD-dependent interval inflation. Not GP/neural universal inference.",( "features","regime","arm_id"),{"features":OBJ,"regime":STR,"arm_id":STR,"scope":STR,"target_coverage":NUM,"ridge":NUM,"ood_gain":NUM}),
    _tool("athena_nonlinear_observe","Update the degree-2 Bayesian model from an explicit observed reward and update the raw-feature OOD reference distribution.",( "features","reward","regime","arm_id"),{"features":OBJ,"reward":NUM,"regime":STR,"arm_id":STR,"scope":STR,"actor":STR,"weight":NUM,"target_coverage":NUM,"ridge":NUM}),
    _tool("athena_experiment_generate","Generate candidate experiments from caller-declared factor levels and hypothesis factor-effect models, then rank them by V5 expected information gain. DESIGN_ONLY.",( "hypotheses","factors"),{"hypotheses":{"type":"array","minItems":2,"maxItems":64,"items":{"type":"object"}},"factors":{"type":"array","minItems":1,"maxItems":12,"items":{"type":"object"}},"max_candidates":{"type":"integer","minimum":1,"maximum":4096},"sample_size":{"type":"integer","minimum":2,"maximum":100000},"cost_weight":NUM,"risk_weight":NUM}),
    _tool("athena_causal_identify","Search for a valid minimal back-door adjustment set in a caller-supplied causal DAG using d-separation. Identification is conditional on supplied graph/assumptions.",( "treatment","outcome","edges"),{"treatment":STR,"outcome":STR,"edges":{"type":"array","minItems":0,"maxItems":256,"items":{}},"observed_nodes":{"type":"array","items":{"type":"string"}},"assumptions":OBJ,"max_adjustment_size":{"type":"integer","minimum":0,"maximum":8},"actor":STR}),
    _tool("athena_interaction_higher_order","Compute order-2..4 factorial inclusion-exclusion contrasts. Every 2^k cell is required; missing cells remain UNIDENTIFIED.",( "experiments",),{"experiments":{"type":"array","minItems":1,"maxItems":5000,"items":{"type":"object"}},"max_order":{"type":"integer","minimum":2,"maximum":4},"design_confidence":NUM}),
    _tool("athena_transition_distribution","Return a multivariate empirical action-conditioned transition mean/covariance from V5 observed transition rows with shrinkage toward no change.",( "action_id","context"),{"action_id":STR,"context":OBJ,"prior_strength":NUM}),
    _tool("athena_mpc_plan","Receding-horizon risk-adjusted planning over caller-supplied actions using the learned multivariate transition surface. PLAN_ONLY and never self-training.",( "initial_context","actions"),{"initial_context":OBJ,"actions":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":6},"beam_width":{"type":"integer","minimum":1,"maximum":512},"discount":NUM,"risk_aversion":NUM,"prior_strength":NUM}),
    _tool("athena_schedule_certified","Exhaustively enumerate small finite schedules under dependencies, worker capability, horizon and explicit budgets. Returns an exact certificate only if search completes; otherwise degrades explicitly.",( "tasks","workers"),{"tasks":{"type":"array","minItems":1,"maxItems":32,"items":{"type":"object"}},"workers":{"type":"array","minItems":1,"maxItems":32,"items":{"type":"object"}},"horizon":{"type":"integer","minimum":1,"maximum":200},"budget":OBJ,"max_nodes":{"type":"integer","minimum":1,"maximum":2000000},"exact_task_limit":{"type":"integer","minimum":1,"maximum":10},"discount":NUM}),
    _tool("athena_witness_capsule","Execute a repository unittest only when bubblewrap namespace isolation is available; otherwise fail closed with HERMETIC_UNAVAILABLE. Never silently falls back.",( "regression_ref",),{"regression_ref":STR,"timeout_s":NUM}),
    _tool("athena_pareto_bandit_select","Identify the interval-possible Pareto frontier and choose an uncertainty-rich frontier candidate for experimentation. EXPERIMENT_SELECTION_ONLY.",( "candidates",),{"candidates":{"type":"array","minItems":1,"maxItems":1000,"items":{"type":"object"}},"directions":OBJ,"exploration_weight":NUM}),
    _tool("athena_discovery_claim_register","Register a V6 science-shadow claim record without mutating Y1 canonical claim authority.",( "claim_key","statement"),{"claim_key":STR,"statement":STR,"scope":STR}),
    _tool("athena_discovery_claim_witness","Attach a SUPPORTS/FALSIFIES/INCONCLUSIVE science-shadow witness with an explicit independence key. This never promotes Y1 authority.",( "claim_id","kind","result","independence_key"),{"claim_id":STR,"kind":STR,"result":STR,"independence_key":STR,"confidence":NUM,"evidence":OBJ,"actor":STR}),
    _tool("athena_discovery_claim_state","Summarize independent V6 science-shadow witness groups. Evidential metadata only; no Y1 canonical rewrite.",( "claim_id",),{"claim_id":STR,"min_independent_support":{"type":"integer","minimum":1,"maximum":100}}),
]

# V7 is a successor science/control layer over V6 discovery. It is chained through
# this registry so the existing V5->V6 compatibility path can advertise/route it
# without introducing another Server inheritance layer.
from .collective_v7_protocol import COLLECTIVE_V7_TOOLS
_existing={tool['name'] for tool in COLLECTIVE_V6_TOOLS}
COLLECTIVE_V6_TOOLS.extend(tool for tool in COLLECTIVE_V7_TOOLS if tool['name'] not in _existing)
COLLECTIVE_V6_TOOL_NAMES={tool['name'] for tool in COLLECTIVE_V6_TOOLS}

CLAIM_NAMESPACE_LAW={
    'canonical_authority_prefix':'athena_claim_',
    'discovery_shadow_prefix':'athena_discovery_claim_',
    'law':'V6/V7 science-shadow claims and Y1 canonical authority are distinct registries; shared RPC names are forbidden',
}
