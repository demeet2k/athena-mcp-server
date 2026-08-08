from __future__ import annotations


def _tool(name, description, required=(), properties=None):
    return {"name":name,"description":description,"inputSchema":{"type":"object","required":list(required),"properties":properties or {},"additionalProperties":False}}

STR={"type":"string"}; NUM={"type":"number"}; OBJ={"type":"object"}; BOOL={"type":"boolean"}; INT={"type":"integer"}

COLLECTIVE_V12_TOOLS=[
    _tool("athena_gp_hyperposterior","Compute a normalized posterior over a finite explicit GP hyperparameter candidate grid using marginal likelihood and visible priors. Read-only.",( "context_key",),{"context_key":STR,"candidates":{"type":"array","maxItems":256,"items":{"type":"object"}}}),
    _tool("athena_gp_bma_predict","Bayesian-model-average a GP prediction across the finite hyperparameter posterior, separating within-model and between-model variance.",( "context_key","features"),{"context_key":STR,"features":OBJ,"candidates":{"type":"array","maxItems":256,"items":{"type":"object"}},"include_observation_noise":BOOL}),
    _tool("athena_gp_sparse_predict","Approximate the current GP with a deterministic farthest-point subset of observed rows and compare the result to the exact bounded GP reference.",( "context_key","features"),{"context_key":STR,"features":OBJ,"inducing_count":{"type":"integer","minimum":1,"maximum":64},"include_observation_noise":BOOL}),
    _tool("athena_gp_bma_decision_evsi","Estimate decision value of candidate GP measurements while updating both finite-grid kernel weights and within-kernel posterior action means hypothetically. DESIGN_ONLY.",( "context_key","actions","experiments"),{"context_key":STR,"actions":{"type":"array","minItems":1,"maxItems":32,"items":{"type":"object"}},"experiments":{"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},"candidates":{"type":"array","maxItems":256,"items":{"type":"object"}},"samples":{"type":"integer","minimum":50,"maximum":2000},"seed":INT,"cost_weight":NUM,"risk_weight":NUM}),
    _tool("athena_pag_candidate_discover","Build a bounded PAG-like circle/arrow/tail candidate from observed Gaussian conditional independences and conservative collider propagation. Not full FCI/RFCI.",( "samples",),{"samples":{"type":"array","minItems":20,"maxItems":10000,"items":{"type":"object"}},"variables":{"type":"array","minItems":3,"maxItems":8,"items":{"type":"string"}},"alpha":NUM,"max_conditioning":{"type":"integer","minimum":0,"maximum":3}}),
    _tool("athena_longitudinal_gformula","Estimate static two-timepoint treatment-regime risks with a transparent parametric g-formula over one binary intermediate variable. Assumption-scoped.",( "samples","treatment1","intermediate","treatment2","outcome"),{"samples":{"type":"array","minItems":80,"maxItems":20000,"items":{"type":"object"}},"treatment1":STR,"intermediate":STR,"treatment2":STR,"outcome":STR,"baseline":{"type":"array","maxItems":16,"items":{"type":"string"}},"regimes":{"type":"array","maxItems":16,"items":{"type":"object"}},"assumptions":OBJ}),
    _tool("athena_chance_resource_select","Select a value-maximizing small finite candidate subset subject to independent-Gaussian one-sided resource chance constraints; exact only under declared finite-model assumptions.",( "candidates","budgets"),{"candidates":{"type":"array","minItems":1,"maxItems":24,"items":{"type":"object"}},"budgets":OBJ,"alpha":NUM,"exact_limit":{"type":"integer","minimum":1,"maximum":18}}),
]

from .collective_v13_protocol import COLLECTIVE_V13_TOOLS
COLLECTIVE_V12_TOOLS.extend(t for t in COLLECTIVE_V13_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V12_TOOLS})
