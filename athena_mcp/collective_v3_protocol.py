from __future__ import annotations

def _tool(name, description, required=(), properties=None):
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "required": list(required),
            "properties": properties or {},
            "additionalProperties": False,
        },
    }

OBJ = {"type": "object"}
STR = {"type": "string"}
NUM = {"type": "number"}

COLLECTIVE_V3_TOOLS = [
    _tool("athena_budget_record", "Persist one measured organization/resource budget observation. Token/compute dimensions are accepted only when supplied by an observable client.", ("run_key","resources"), {
        "run_key": STR, "resources": OBJ, "budget": OBJ, "outcome": OBJ, "scope": STR, "actor": STR,
    }),
    _tool("athena_budget_summary", "Summarize persistent resource observations plus automatically metered MCP tool-call wall time.", (), {
        "scope": STR, "limit": {"type":"integer","minimum":1,"maximum":5000},
    }),
    _tool("athena_policy_state", "Return the versioned bounded organization-policy state and empirical reliability for a scope.", (), {"scope": STR}),
    _tool("athena_policy_score", "Score a normalized feature vector with the current bounded learned organization policy.", ("features",), {"features": OBJ, "scope": STR}),
    _tool("athena_policy_update", "Versioned bounded online policy update from an observed reward. Rejects stale expected_version and records rollback history.", ("expected_version","features","observed_reward"), {
        "expected_version": {"type":"integer","minimum":0}, "features": OBJ, "observed_reward": NUM,
        "scope": STR, "actor": STR, "learning_rate": NUM, "l2": NUM,
    }),
    _tool("athena_policy_rollback", "Rollback one organization-policy transaction as a new versioned transaction; history is preserved.", ("txid","expected_version"), {
        "txid": STR, "expected_version": {"type":"integer","minimum":0}, "scope": STR, "actor": STR,
    }),
    _tool("athena_counterfactual_simulate", "Rank candidate organizations using base RGO, empirical calibration, bounded learned policy, risk and budget pressure without committing topology.", ("candidates",), {
        "candidates": {"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}},
        "context": OBJ, "scope": STR,
    }),
    _tool("athena_elder_observe", "Update longitudinal evidence-backed authority for an entity from reuse/prediction/repair/regression/generalization outcomes.", ("entity_id","outcomes"), {
        "entity_id": STR, "outcomes": OBJ, "scope": STR, "actor": STR,
    }),
    _tool("athena_elder_rank", "Rank evidence-backed elder/cultural authority within a scope; age alone confers no authority.", (), {
        "scope": STR, "limit": {"type":"integer","minimum":1,"maximum":500}, "min_observations": {"type":"integer","minimum":1},
    }),
    _tool("athena_antibody_record_outcome", "Record success, failure, false positive, regression pass or regression failure for a known failure antibody.", ("antibody_id","outcome"), {
        "antibody_id": STR, "outcome": STR, "actor": STR,
    }),
    _tool("athena_antibody_evolve", "Create a distinct antibody variant within the parent's family with optional expiry.", ("parent_id","signature","detector","repair"), {
        "parent_id": STR, "signature": STR, "detector": OBJ, "repair": OBJ, "trigger": OBJ, "evidence": OBJ,
        "regression_refs": {"type":"array","items":{"type":"string"}}, "ttl_hours": NUM, "scope": STR, "actor": STR,
    }),
    _tool("athena_antibody_select", "Rank matching antibody variants by semantic match, empirical repair/regression reliability, status and expiry.", ("event",), {
        "event": STR, "tags": {"type":"array","items":{"type":"string"}}, "scope": STR,
        "threshold": NUM, "limit": {"type":"integer","minimum":1,"maximum":100},
    }),
    _tool("athena_pheromone_multiscale_reinforce", "Reinforce a source coordinate and declared token/artifact/module/domain/system relatives with scale-distance attenuation.", ("source_scale","coordinates","observations"), {
        "source_scale": STR, "coordinates": OBJ, "observations": OBJ, "upward_decay": NUM, "downward_decay": NUM,
        "age": NUM, "evaporation_rate": NUM, "deposit_gain": NUM, "actor": STR,
    }),
    _tool("athena_pheromone_multiscale_field", "Return the persistent multiscale pheromone field grouped by token/artifact/module/domain/system scale.", (), {
        "min_score": NUM, "limit": {"type":"integer","minimum":1,"maximum":1000},
    }),
]
