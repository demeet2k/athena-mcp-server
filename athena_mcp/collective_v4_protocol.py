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
BOOL = {"type": "boolean"}
ARR_OBJ = {"type": "array", "items": {"type": "object"}}

COLLECTIVE_V4_TOOLS = [
    _tool("athena_regime_resolve", "Resolve normalized task signals into a deterministic HIVE/SWARM/PACK/FLOCK/HERD/POD task-regime key for hierarchical learning.", ("signals",), {
        "signals": OBJ, "domain": STR,
    }),
    _tool("athena_bandit_select", "Select an organization/action experiment using a diagonal contextual-UCB posterior with local-regime evidence, cross-regime transfer, uncertainty, and a V3 policy prior.", ("arms","context"), {
        "arms": {"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}}, "context": OBJ,
        "regime": STR, "signals": OBJ, "exploration_alpha": NUM, "transfer_tau": NUM, "policy_scope": STR,
    }),
    _tool("athena_bandit_observe", "Update one regime/action posterior from an explicit observed reward; predictions never train themselves.", ("arm_id","reward","features","regime"), {
        "arm_id": STR, "reward": NUM, "features": OBJ, "regime": STR, "actor": STR, "global_transfer_weight": NUM,
    }),
    _tool("athena_credit_assign", "Assign uncertainty-bearing intervention credit from an observed outcome delta. Weak designs remain associational; residual outcome is preserved.", ("outcome_key","outcome_delta","interventions"), {
        "outcome_key": STR, "outcome_delta": NUM,
        "interventions": {"type":"array","minItems":1,"maxItems":128,"items":{"type":"object"}},
        "design": OBJ, "regime": STR, "actor": STR,
    }),
    _tool("athena_credit_summary", "Summarize persisted intervention credit and causal-confidence history.", (), {
        "intervention_id": STR, "regime": STR, "limit": {"type":"integer","minimum":1,"maximum":5000},
    }),
    _tool("athena_worker_cost_observe", "Persist measured per-worker resource use, normalized budget pressure, and useful-output efficiency for future scheduling.", ("worker_id","task_id","resources"), {
        "worker_id": STR, "task_id": STR, "resources": OBJ, "budget": OBJ, "useful_output": NUM, "scope": STR, "actor": STR,
    }),
    _tool("athena_budget_schedule", "Allocate tasks to workers using demand x capability fit x availability x measured efficiency subject to observable remaining budgets; unknown cost is penalized, not invented.", ("tasks","workers","remaining_budget"), {
        "tasks": {"type":"array","minItems":1,"maxItems":256,"items":{"type":"object"}},
        "workers": {"type":"array","minItems":1,"maxItems":256,"items":{"type":"object"}},
        "remaining_budget": OBJ, "scope": STR,
        "max_assignments_per_worker": {"type":"integer","minimum":1,"maximum":16}, "alpha": NUM, "beta": NUM,
    }),
    _tool("athena_diffusion_observe", "Record observed utility of pheromone transfer between two scales and update a shrinkage-learned diffusion coefficient.", ("source_scale","target_scale","transfer_utility"), {
        "source_scale": STR, "target_scale": STR, "transfer_utility": NUM, "evidence_weight": NUM, "causal_confidence": NUM, "actor": STR,
    }),
    _tool("athena_diffusion_matrix", "Return learned/shrunk token-artifact-module-domain-system diffusion coefficients with reliability and causal-weight metadata."),
    _tool("athena_pheromone_adaptive_reinforce", "Reinforce declared multiscale coordinates using learned diffusion coefficients rather than fixed scale attenuation.", ("source_scale","coordinates","observations"), {
        "source_scale": STR, "coordinates": OBJ, "observations": OBJ, "age": NUM, "evaporation_rate": NUM, "deposit_gain": NUM, "actor": STR,
    }),
    _tool("athena_antibody_execute_regressions", "Execute stored failure-antibody unittest witnesses in a restricted repository-owned subprocess; no arbitrary shell/command refs are accepted.", ("antibody_id",), {
        "antibody_id": STR, "timeout_s": NUM, "max_refs": {"type":"integer","minimum":1,"maximum":32}, "record_outcome": BOOL, "actor": STR,
    }),
    _tool("athena_rollout_simulate", "Run uncertainty-banded multi-step organization rollouts using explicit context transitions only. Always simulate-only; never commits topology.", ("trajectories",), {
        "trajectories": {"type":"array","minItems":1,"maxItems":64,"items":{"type":"object"}}, "initial_context": OBJ,
        "regime": STR, "discount": NUM, "exploration_alpha": NUM, "max_steps": {"type":"integer","minimum":1,"maximum":64},
    }),
    _tool("athena_projection_prepare", "Prepare and journal a topology-to-JSPACE projection plan against explicit topology/semantic/Git heads without mutating JSPACE.", ("topology_id","expected_topology_version"), {
        "topology_id": STR, "expected_topology_version": {"type":"integer","minimum":0}, "expected_semantic_eid": {"type":["string","null"]},
        "expected_git_head": {"type":["string","null"]}, "actor": STR,
    }),
    _tool("athena_projection_status", "Read one topology-to-JSPACE projection saga and its recovery state.", ("projection_id",), {"projection_id": STR}),
    _tool("athena_topology_project_jspace", "Apply a prepared topology projection to canonical JSPACE after topology+semantic CAS preflight, optionally checkpointing Git by expected-head CAS. This is a recoverable saga, not an atomic cross-store transaction.", ("topology_id","expected_topology_version","expected_semantic_eid"), {
        "topology_id": STR, "expected_topology_version": {"type":"integer","minimum":0}, "expected_semantic_eid": {"type":["string","null"]},
        "checkpoint_git": BOOL, "expected_git_head": {"type":["string","null"]}, "actor": STR, "dry_run": BOOL,
    }),
]

# V5 is deliberately chained through the V4 registry so older Server wiring remains
# compatible while the new science layer is lazily instantiated by the V4 dispatcher.
from .collective_v5_protocol import COLLECTIVE_V5_TOOLS
COLLECTIVE_V4_TOOLS.extend(t for t in COLLECTIVE_V5_TOOLS if t['name'] not in {x['name'] for x in COLLECTIVE_V4_TOOLS})
