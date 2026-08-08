from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

VERSION = "DRIVE.ORGAN-RECOVERY.1"
SOURCE_ATHENA_HEAD = "24f260134d978d5314ee729e8f1dd59df0226a59"
SOURCE_MCP_HEAD = "1c526bb16575192040d634c1dad244cc9cb35132"

LAWS = [
    "TITLE_MATCH != SEMANTIC_EQUIVALENCE",
    "SEARCH_MISS != CAPABILITY_ABSENCE",
    "DRIVE_SOURCE_CLAIM != CURRENT_RUNTIME_TRUTH",
    "HISTORICAL_GREEN_RUN != CURRENT_HEAD_REPLAY",
    "SPECIFICATION != IMPLEMENTATION",
    "PRESENT_COMPONENT != COMPLETE_ORGAN",
    "RETRIEVED_MEMORY != EXTERNAL_EVIDENCE",
    "RECOVERY_OUTPUT != CANONICAL_PROMOTION",
]

ORGANS = [
    {
        "organ_id": "recovery.boot.harness",
        "family": "boot/retrieval",
        "source": {"title": "HARNESS — DEEP GOOGLE DOCS SYNTHESIS", "drive_file_id": "1w5fjzD3DAO2GIS5l3Mv44AcG3sSRuaeN-PekGLBGuSw", "revision_id": "18"},
        "semantic_signature": ["constitution", "typed_state", "operator_library", "route_graph", "measurement", "adversarial_test", "receipt", "replay", "repair", "learning", "return_seed"],
        "status": "RECOVERED_BOOT_LAW",
        "current_runtime_refs": ["Athena:prompts/ORCHESTRATION_CORE.md", "Athena:prompts/modules/EPISTEMIC_LEARNING.md"],
        "residuals": ["make corpus recovery an explicit reusable boot/retrieval routine", "require semantic-signature dedup before declaring an organ missing"],
        "priority": 100,
        "boundary": "Harness sophistication is not evidence of target improvement; promotion requires observed effect.",
    },
    {
        "organ_id": "recovery.boot.know_self",
        "family": "boot/continuity",
        "source": {"title": "KNOW SELF Ω1 — HARD-LIMITATION MAP OF ATHENA/CODEX", "drive_file_id": "1-H7-rJoSKkRpsAoi2TMRqEcvyViWToxdYpARGfuCjR4", "revision_id": "26"},
        "semantic_signature": ["reconstructive_identity", "boot_order", "selective_retrieval", "capability_auth_execution_verification_ladder", "canonical_external_memory"],
        "status": "RECOVERED_BOOT_LAW",
        "current_runtime_refs": ["Athena:prompts/PROMPT.manifest.json", "Athena:prompts/modules/GIT_ORGANISM.md"],
        "residuals": ["persist compact recovery index so later invocations can discover unresident organs without title recall"],
        "priority": 100,
        "boundary": "External artifacts support reconstruction; they do not imply continuous resident cognition or hidden-weight modification.",
    },
    {
        "organ_id": "kc144.command_hub",
        "family": "navigation/command",
        "source": {"title": "KC144 Topological Git/MCP Command Hub — Sealed", "drive_file_id": "16UOg_DBKAQNC5v1Ktms-7cEQ2TWYFt2NviNp6hJToFk", "revision_id": None},
        "semantic_signature": ["KC144", "typed_graph", "polyatlas", "CAS", "snapshot_replay", "command_surface"],
        "status": "PRESENT_CURRENT",
        "current_runtime_refs": ["PR#28 merged", "athena_mcp/kc144.py", "athena_mcp/polycoord.py", "athena_mcp/crystal_runtime.py"],
        "residuals": ["preserve Drive source lineage in runtime recovery registry"],
        "priority": 20,
        "boundary": "The Drive source is lineage; current runtime head is the implementation truth coordinate.",
    },
    {
        "organ_id": "qhug.ultimate",
        "family": "integration/governance",
        "source": {"title": "⟦ ATHENA :: QHUG ΩULTIMATE :: V1 ⟧", "drive_file_id": "1521VwHC2nw-VWjj_KGCXSWDX5Pgg3L0SSDYMu77COa4", "revision_id": "25"},
        "semantic_signature": ["explicit_alternatives", "countermodel", "authority_gate", "transport", "quarantine", "handoff", "replay", "pareto", "proof_carrying_commit"],
        "status": "PARTIAL_CURRENT",
        "current_runtime_refs": ["athena_mcp/qhug_pareto_kernel.py", "athena_mcp/qhug_pareto_kernel_protocol.py", "athena_mcp/qhug_pareto_kernel_surface.py"],
        "residuals": ["map Q00-Q0F lifecycle beyond Pareto selection", "add observation/countermodel/transport/quarantine/handoff receipts where not already represented by neighboring organs"],
        "priority": 85,
        "boundary": "Existing QHUG Pareto kernel is current code; lifecycle residuals must not be inferred from title search alone.",
    },
    {
        "organ_id": "navlearn.future_state_cartography",
        "family": "developmental_control",
        "source": {"title": "KC144 NAVIGATION-LEARNING ENGINE 2", "drive_file_id": "1kQbwgifB6fH0fGI8h_p5ggaHs_0EgZwDJ-VrCfUO4E0", "revision_id": "8"},
        "semantic_signature": ["architecture_state_graph", "future_reachability", "option_value", "lock_in", "path_order", "curvature", "gateway_capability", "critical_path"],
        "status": "RESIDUAL_HIGH_VALUE",
        "current_runtime_refs": ["athena_mcp/orchestration.py", "athena_mcp/orchestration_robustness.py", "athena_mcp/frontier_runtime.py"],
        "residuals": ["explicit future-state transition graph", "option-value and lock-in terms in successor evaluation", "noncommutative intervention-order/curvature witness", "gateway/dependency leverage metric"],
        "priority": 95,
        "boundary": "Current AOR/frontier overlap does not establish semantic equivalence without operator-level tests.",
    },
    {
        "organ_id": "cross_zoom.belief_control",
        "family": "decision/navigation",
        "source": {"title": "CROSS–ZOOM SYSTEM Ω2", "drive_file_id": "1HVL4alGzFYutYl0o8C0YZkOghMheIN0--GmKICNsDf8", "revision_id": "11"},
        "semantic_signature": ["belief_state", "POMDP", "EVSI", "information_gain", "zoom_channel", "Blackwell_order", "value_of_zoom", "adaptive_resolution"],
        "status": "PARTIAL_CURRENT",
        "current_runtime_refs": ["athena_mcp/collective_belief.py", "athena_mcp/collective_inference.py", "athena_mcp/collective_probabilistic.py::pomdp_solve"],
        "residuals": ["typed zoom channels as sensing actions", "Blackwell dominance certificate", "value-of-zoom versus cost", "KC27/odd-resolution transport binding"],
        "priority": 88,
        "boundary": "General POMDP/EVI machinery is present; resolution/zoom semantics remain a narrower residual.",
    },
    {
        "organ_id": "output.atomization_fitness",
        "family": "output/learning",
        "source": {"title": "KC144 OUTPUT-MAPPING / TIME / FITNESS CONSTITUTION — v1.0", "drive_file_id": "1btaUkNqRKj6q2zB0KYPbyHSOW3QwucoC8NCUoE2seK8", "revision_id": "5"},
        "semantic_signature": ["output_registration", "typed_atomization", "multicoordinate_event", "sheaf_glue", "selection_fitness", "repair_braid_quarantine_retire"],
        "status": "PARTIAL_OR_RESIDUAL",
        "current_runtime_refs": ["athena_mcp/crystal_runtime.py", "athena_mcp/timebundle.py", "athena_mcp/collective_learning.py"],
        "residuals": ["first-class output atom ontology", "overlap-gluing/conflict witness", "fitness selection tied to observed downstream outcomes"],
        "priority": 92,
        "boundary": "Current output crystallization and learning do not by themselves prove the full atomization/sheaf/fitness constitution.",
    },
    {
        "organ_id": "reaction.event_sourced",
        "family": "event/collective",
        "source": {"title": "ATHENA Ω4 — KC144 EVENT-SOURCED REACTION ENGINE", "drive_file_id": "1fnH1rmIKeq1YAB3y-y75gKDPY7NO9WHUWVKmFJycMEE", "revision_id": "7"},
        "semantic_signature": ["immutable_event_stream", "recipient_delivery", "recipient_consumption", "causal_credit", "allocation_policy", "vector_clock", "lamport", "hash_chain", "replay"],
        "status": "PARTIAL_CURRENT",
        "current_runtime_refs": ["athena_mcp/store.py", "athena_mcp/core.py", "athena_mcp/collective_memory.py", "athena_mcp/collective_learning.py", "athena_mcp/rehydration_loop.py"],
        "residuals": ["audit delivery versus actual consumption semantics", "audit causal-credit linkage to event witnesses", "preserve reaction-source lineage in runtime manifest"],
        "priority": 80,
        "boundary": "Historical design and current event components overlap; exact recipient-consumption semantics require current-head verification.",
    },
    {
        "organ_id": "reaction.signed_dual_trust",
        "family": "security/trust",
        "source": {"title": "ATHENA Ω6 — DUAL-TRUST-DOMAIN SIGNED REACTION FABRIC", "drive_file_id": "1E-loTR5BrHOwJVnlrhT5IVN7y8PcBaq_SPIfEktw8uA", "revision_id": "9"},
        "semantic_signature": ["root_key", "operational_certificate", "Ed25519", "signed_event", "freshness", "causal_readiness", "semantic_admissibility", "authority_separation"],
        "status": "HISTORICAL_EXECUTION_NEEDS_CURRENT_REPLAY",
        "current_runtime_refs": ["current-head implementation equivalence not certified by this recovery pass"],
        "residuals": ["locate or rebuild current cryptographic trust-domain implementation", "replay tests at current head before promotion", "keep authenticity/freshness/readiness/admissibility/authority as separate gates"],
        "priority": 83,
        "boundary": "The source reports a historical local execution; that is not current-runtime fact without current-head replay.",
    },
    {
        "organ_id": "set_relation.theory_kernel",
        "family": "formal_reasoning",
        "source": {"title": "ΩSET-144 — SET - RELATION - LATTICE KERNEL 2", "drive_file_id": "10-GpqTFo1KczYAW2p0IV5vMloWbdwpj634cX5QALF18", "revision_id": "14"},
        "semantic_signature": ["concept_claim_axiom_theorem_separation", "syntactic_semantic_consequence", "closure_operator", "model_class", "axiom_independence", "proof_hypergraph", "blast_radius"],
        "status": "RESIDUAL_HIGH_VALUE",
        "current_runtime_refs": ["athena_mcp/crystal_graph.py", "athena_mcp/orchestration_gap.py", "athena_mcp/orchestration_equivalence.py"],
        "residuals": ["typed theory object and closure operator", "separate formal authority from empirical evidence", "axiom-independence and proof-dependency/blast-radius tools"],
        "priority": 86,
        "boundary": "Graph reachability is not logical entailment; any theory closure must declare inference semantics.",
    },
    {
        "organ_id": "cmg.root_relation_logic",
        "family": "formal_reasoning/identity",
        "source": {"title": "KC144 COMPLETE COORDINATE/MATHEMATICS/GRAPH SPECIFICATION 2", "drive_file_id": "1KYmDH45AkQgh1U3igj-BjoH5UmWCFxNFOismYh1f3I4", "revision_id": "10"},
        "semantic_signature": ["partial_identity", "equality_disequality", "DSU", "proper_coloring", "SAT_pair_classification", "unknown_not_placeholder"],
        "status": "RESIDUAL_HIGH_VALUE",
        "current_runtime_refs": ["athena_mcp/orchestration_equivalence.py"],
        "residuals": ["proof-carrying SAME/DIFFERENT/UNKNOWN classifier", "DSU+disequality fast path", "SAT-backed fallback and witness packets"],
        "priority": 84,
        "boundary": "UNKNOWN is first-class; absence of proof may not collapse identity.",
    },
    {
        "organ_id": "theta4.whole_system_game",
        "family": "self_engineering/evaluation",
        "source": {"title": "ATHENA Θ⁴ RUNTIME Ω2", "drive_file_id": "1c13k4K28cpJzUcXVxnb2Qtq9wpjsj_TEKdMEUw3vhb8", "revision_id": None},
        "semantic_signature": ["heterogeneous_task_adapters", "shared_whole_state", "adversarial_swarm", "coalition_replay", "shapley_credit", "whole_target_lock", "forced_regression_rollback"],
        "status": "HISTORICAL_EXECUTION_NEEDS_CURRENT_MAPPING",
        "current_runtime_refs": ["athena_mcp/collective_*", "athena_mcp/orchestration_*"],
        "residuals": ["map Θ⁴ operators to current collective/AOR implementation", "retain Whole-Target Lock as promotion invariant", "update learning only from independently observed current outcomes"],
        "priority": 82,
        "boundary": "Reported historical test counts remain historical evidence unless replayed at a bound current implementation.",
    },
    {
        "organ_id": "rh16.process_memory_recovery",
        "family": "math/quantum",
        "source": {"title": "%%KC144 HYPERCRYSTAL — RIEMANN–HILBERT 16-ATLAS NAVIGATION SYSTEM 2", "drive_file_id": "1iQAMLBqjAcQDhMbrrY-KR0VnQtYVptT0QFFuTQk_QIo", "revision_id": None},
        "semantic_signature": ["process_tensor", "quantum_comb", "causal_normalization", "Markov_order", "memory_cut", "MPO_operator_Schmidt_rank", "recovery_syndrome"],
        "status": "THEORY_SOURCE_NOT_RUNTIME_REQUIREMENT",
        "current_runtime_refs": [],
        "residuals": ["index equations/provenance into math registry before deciding whether an executable MCP organ is justified"],
        "priority": 55,
        "boundary": "Scientific/theoretical content is not automatically an orchestration runtime feature; literature claims require verification before theorem promotion.",
    },
    {
        "organ_id": "sourcebound.deep_search_crystal",
        "family": "recovery/meta_registry",
        "source": {"title": "ATHENA Ω144 — DEEP-SEARCH, SOURCE-BOUND KC144 CRYSTAL", "drive_file_id": "17ZCbD16Y0XPCq6-HqgOEgbbnVEdUHPkL9iD4BfAmBdY", "revision_id": "14"},
        "semantic_signature": ["source_manifestations", "replay_equivalence", "six_dimensional_packet", "typed_lineage", "source_bound_synthesis", "claim_ceiling"],
        "status": "RECOVERED_PREDECESSOR",
        "current_runtime_refs": ["this registry supersedes title-only recovery with revision-bound operator-level mapping"],
        "residuals": ["continue recursive functional searches over older corpus and append only novel semantic signatures"],
        "priority": 90,
        "boundary": "A deep synthesis is a map of accessible sources, not a cryptographic census or independent witness.",
    },
]

_ORGAN_BY_ID = {row["organ_id"]: row for row in ORGANS}
_FRONTIER_STATUSES = {
    "RESIDUAL_HIGH_VALUE",
    "PARTIAL_CURRENT",
    "PARTIAL_OR_RESIDUAL",
    "HISTORICAL_EXECUTION_NEEDS_CURRENT_REPLAY",
    "HISTORICAL_EXECUTION_NEEDS_CURRENT_MAPPING",
}


def _copy(row: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(row))


def get_organ(organ_id: str) -> dict[str, Any]:
    key = str(organ_id)
    if key not in _ORGAN_BY_ID:
        raise ValueError(f"recovered organ not found: {key}")
    return {"version": VERSION, "organ": _copy(_ORGAN_BY_ID[key])}


def list_organs(status: str | None = None, family: str | None = None, query: str | None = None, limit: int = 100) -> dict[str, Any]:
    rows = list(ORGANS)
    if status:
        rows = [r for r in rows if r["status"] == str(status)]
    if family:
        f = str(family).lower()
        rows = [r for r in rows if f in r["family"].lower()]
    if query:
        q = str(query).lower().strip()
        if q:
            def haystack(r: Mapping[str, Any]) -> str:
                source = r.get("source") or {}
                values = [r.get("organ_id", ""), r.get("family", ""), r.get("status", ""), source.get("title", ""), " ".join(r.get("semantic_signature") or []), " ".join(r.get("residuals") or []), " ".join(r.get("current_runtime_refs") or [])]
                return " ".join(str(x) for x in values).lower()
            rows = [r for r in rows if q in haystack(r)]
    cap = max(1, min(int(limit), 100))
    rows = sorted(rows, key=lambda r: (-int(r["priority"]), r["organ_id"]))[:cap]
    return {"version": VERSION, "count": len(rows), "organs": [_copy(r) for r in rows], "law": "search/list returns recovery registry state; it does not prove current implementation absence or semantic equivalence"}


def residual_frontier(limit: int = 10, include_theory: bool = False) -> dict[str, Any]:
    allowed = set(_FRONTIER_STATUSES)
    if include_theory:
        allowed.add("THEORY_SOURCE_NOT_RUNTIME_REQUIREMENT")
    rows = [r for r in ORGANS if r["status"] in allowed and r.get("residuals")]
    rows = sorted(rows, key=lambda r: (-int(r["priority"]), r["organ_id"]))
    cap = max(1, min(int(limit), 50))
    return {
        "version": VERSION,
        "source_heads": {"athena": SOURCE_ATHENA_HEAD, "mcp": SOURCE_MCP_HEAD},
        "count": min(len(rows), cap),
        "frontier": [{"organ_id": r["organ_id"], "family": r["family"], "status": r["status"], "priority": r["priority"], "source": deepcopy(r["source"]), "residuals": deepcopy(r["residuals"]), "boundary": r["boundary"]} for r in rows[:cap]],
        "law": "frontier priority is a recovered-development heuristic, not autonomous authority to mutate or promote",
    }


class DriveRecoveryRegistryRuntime:
    def describe(self) -> dict[str, Any]:
        status_counts: dict[str, int] = {}
        pinned = 0
        for row in ORGANS:
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
            if (row.get("source") or {}).get("revision_id") is not None:
                pinned += 1
        return {
            "version": VERSION,
            "source_heads": {"athena": SOURCE_ATHENA_HEAD, "mcp": SOURCE_MCP_HEAD},
            "organ_count": len(ORGANS),
            "revision_pinned_count": pinned,
            "status_counts": dict(sorted(status_counts.items())),
            "laws": list(LAWS),
            "boundary": "read-only recovered lineage/index; no tool in this surface mutates Git, Drive, runtime authority, or prompt activation",
        }

    def list(self, **kwargs: Any) -> dict[str, Any]:
        return list_organs(**kwargs)

    def get(self, organ_id: str) -> dict[str, Any]:
        return get_organ(organ_id)

    def frontier(self, limit: int = 10, include_theory: bool = False) -> dict[str, Any]:
        return residual_frontier(limit=limit, include_theory=include_theory)
