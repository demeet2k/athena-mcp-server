from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V8_TOOLS=[
    _tool("athena_belief_register","Register/reset a finite discrete model belief state with normalized priors. Model belief is not canonical truth.",( "context_key","models"),{"context_key":STR,"models":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"replace":BOOL}),
    _tool("athena_belief_state","Read the current finite model belief distribution and entropy.",( "context_key",),{"context_key":STR}),
    _tool("athena_belief_observe","Bayes-update a finite belief from explicit per-model likelihoods for one actual declared observation.",( "context_key","outcome","likelihoods"),{"context_key":STR,"outcome":STR,"likelihoods":OBJ,"evidence_ref":STR,"actor":STR}),
    _tool("athena_decision_evi","Rank finite candidate experiments by expected improvement in downstream decision utility under the current belief. DESIGN_ONLY.",( "context_key","actions","experiments"),{"context_key":STR,"actions":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"experiments":{"type":"array","minItems":1,"maxItems":512,"items":{"type":"object"}},"cost_weight":NUM,"risk_weight":NUM}),
    _tool("athena_belief_dual_control","One-step finite-belief controller combining immediate utility, expected next decision utility and information value. PLAN_ONLY.",( "context_key","actions"),{"context_key":STR,"actions":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"discount":NUM,"information_weight":NUM,"risk_weight":NUM}),
    _tool("athena_causal_effect_estimate","Estimate an assumption-scoped linear BACKDOOR, IV-Wald, or FRONTDOOR mediation effect from explicit numeric samples. Estimation never proves identification.",( "method","samples","treatment","outcome"),{"method":STR,"samples":{"type":"array","minItems":6,"maxItems":10000,"items":{"type":"object"}},"treatment":STR,"outcome":STR,"adjustment":{"type":"array","items":{"type":"string"},"maxItems":16},"mediator":STR,"instrument":STR,"assumptions":OBJ}),
    _tool("athena_causal_structure_bootstrap","Bootstrap the V7 heuristic association skeleton and return stable undirected/v-structure candidates. Stability is not causal probability.",( "samples",),{"samples":{"type":"array","minItems":8,"maxItems":5000,"items":{"type":"object"}},"variables":{"type":"array","items":{"type":"string"},"maxItems":16},"association_threshold":NUM,"resamples":{"type":"integer","minimum":5,"maximum":300},"support_threshold":NUM,"seed":INT}),
    _tool("athena_contingent_policy","Build a depth-1 outcome-contingent action policy under the current finite belief and one supplied experiment. DESIGN_ONLY.",( "context_key","actions","experiment"),{"context_key":STR,"actions":{"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},"experiment":OBJ}),
    _tool("athena_evidence_spectral","Compute metadata-similarity effective-N and spectral participation-ratio diversity for a science-shadow claim's witnesses.",( "claim_id",),{"claim_id":STR,"dimensions":{"type":"array","items":{"type":"string"},"maxItems":16},"min_confidence":NUM}),
]

from .collective_v9_protocol import COLLECTIVE_V9_TOOLS
COLLECTIVE_V8_TOOLS.extend(t for t in COLLECTIVE_V9_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V8_TOOLS})
