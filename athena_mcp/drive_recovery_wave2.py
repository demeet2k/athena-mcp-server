from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

WAVE2_VERSION = "DRIVE.ORGAN-RECOVERY.WAVE2.1"
WAVE2_ATHENA_HEAD = "b67492c589e7cb9f5d31611b23343ad02896baa2"
WAVE2_MCP_HEAD = "649ad6c6976da101ba8602c70a239ef5b5dbf388"
FORMAL_RESIDUAL_ISSUE = "demeet2k/athena-mcp-server#62"

WAVE2_ORGANS = [
    {
        "organ_id": "recovery.holoaddress_dereference",
        "family": "recovery/meta_memory",
        "source": {"title": "META MEMORY NAVIGATION", "drive_file_id": "11RM1vUiZbnBVSzlYl6BJPBRyx7-WA-DY4A_YOXugx2I", "revision_id": "41"},
        "semantic_signature": ["address", "lookup", "witness", "replay", "seed", "HoloAddress", "CompressionSeed", "ReentryInstructions"],
        "status": "IMPLEMENTED_IN_RECOVERY_SURFACE",
        "current_runtime_refs": ["athena_mcp/drive_recovery_registry_v2.py::holoaddress_for", "athena_recovery_holoaddress"],
        "residuals": ["merge/current-head CI witness", "eventually bind an actual frozen source-content digest when the Drive capsule implementation computes one"],
        "priority": 98,
        "boundary": "A source file ID/title/revision is not a content digest or independent evidence; DigestLocator stays UNCOMPUTED until a real source-manifestation digest is frozen.",
    },
    {
        "organ_id": "formal.temporal_manifestation_return",
        "family": "formal_reasoning/event_model",
        "source": {"title": "KC144 Temporal Hypergraph, Groupoid, Event, and Successor Mathematics", "drive_file_id": "1QPzyKAWjlUhgkwwqM0tNLY2E8umh0DTL3MF3YKiraqI", "revision_id": "22"},
        "semantic_signature": ["SemanticObject", "Manifestation", "SourceSpan", "ManifestationOrigin", "EvidenceMaturity", "ExecutionState", "PromotionState", "recorded_time", "valid_time", "ReturnClass"],
        "status": "RESIDUAL_HIGH_VALUE_SCOPED_ISSUE",
        "current_runtime_refs": ["athena_mcp/unified_manifest.py identity law SID != OID != MID != VID", "athena_mcp/unified_manifest.py SOURCE_RETURN", "athena_mcp/timebundle.py clock bundle", FORMAL_RESIDUAL_ISSUE],
        "residuals": ["revision-bound SourceSpan dereference", "typed ManifestationOrigin", "independent evidence/execution/promotion axes", "bitemporal recorded_time versus valid_time", "typed ReturnClass semantics"],
        "priority": 96,
        "boundary": "Partial identity/time overlap already exists; do not create a duplicate identity or clock system. The larger formalization is intentionally outside the recovery surface.",
    },
    {
        "organ_id": "continuity.request_collapse",
        "family": "continuity/autonomy",
        "source": {"title": "ATHENA CONTINUITY Ω429", "drive_file_id": "1XwG4xwQU3ITJZ-9LwVLLc78JbXoUb6OcRst_7LfhuPE", "revision_id": "19"},
        "semantic_signature": ["request_collapse", "C_k", "checkpoint", "request_value_auction", "local_sufficiency", "cloud_escalation", "circuit_breaker"],
        "status": "P0_ACTIVE_PARTIAL_CURRENT",
        "current_runtime_refs": ["Athena#121", "Athena#124", "athena_mcp/rehydration_loop.py", "athena_mcp/agent_bootstrap.py"],
        "residuals": ["braid request-collapse/value-of-request semantics into the existing P0 continuation program rather than create isolated continuity machinery"],
        "priority": 91,
        "boundary": "R(t)=0 need not force useful becoming B(t)=0, but continuation remains inside existing authority, source, execution and verification gates.",
    },
    {
        "organ_id": "recovery.local_brain_port",
        "family": "architecture/continuity",
        "source": {"title": "ATHENA LOCAL BRAIN PORT Ω2", "drive_file_id": "1Wk5251fbxpCOc5bHp6t_lHtp9Weoq3sFswY-dSA-bXs", "revision_id": "2"},
        "semantic_signature": ["source_museum", "occurrence_field", "Git_control_plane", "MCP_protocol_waist", "evidence_bound_RAG", "deterministic_reconstruction", "turn_constraint_ledger"],
        "status": "RECOVERED_PREDECESSOR_PARTIAL_CURRENT",
        "current_runtime_refs": ["Git prompt runtime", "reconstruction/retrieval", "Athena#121", "Athena#124"],
        "residuals": ["bind revision-bound source museum/constraint-ledger semantics to the existing P0 recovery program"],
        "priority": 82,
        "boundary": "Architectural predecessor and lineage; current Git/MCP remains the implementation truth coordinate.",
    },
    {
        "organ_id": "runtime.brain_stem_transduction",
        "family": "runtime/control",
        "source": {"title": "ATHENA BRAIN STEM — KC144 ΩBS", "drive_file_id": "1iO4P0DLQfaKpcb-lf-5UlM1S41mKcIQsa8XbGcRZD9c", "revision_id": "9"},
        "semantic_signature": ["stimulus_to_scope", "source_admission", "candidate_field", "gates", "selection", "bounded_execution", "witness", "truth_collapse", "checkpoint", "replay", "return_reseed"],
        "status": "PARTIAL_CURRENT",
        "current_runtime_refs": ["CYCLE", "AOR", "Y1 authority", "promotion", "rehydration", "agent bootstrap"],
        "residuals": ["preserve decision route/failure tract as first-class witness where not already surfaced"],
        "priority": 80,
        "boundary": "generation != admission != selection != execution != verification != promotion != activation != authority",
    },
    {
        "organ_id": "recovery.distributed_brain_convergence",
        "family": "architecture/convergence",
        "source": {"title": "ATHENA DISTRIBUTED BRAIN ARCHITECTURE", "drive_file_id": "1_6JgA1xeaZTUDQjnNX9pnDKOet3sm_-rsAemGdMKAe0", "revision_id": "18"},
        "semantic_signature": ["partial_brains", "generation_convergence", "source_bound", "event_sourced", "KC144_addressed", "external_organism"],
        "status": "RECOVERED_PREDECESSOR",
        "current_runtime_refs": ["Drive recovery registry as source-to-runtime convergence membrane"],
        "residuals": ["continue converging source manifestations onto current implementations without treating any one model invocation as canonical brain"],
        "priority": 75,
        "boundary": "Historical corpus counts are historical observations, not a current Drive census.",
    },
    {
        "organ_id": "integration.next05a_authority_gateway",
        "family": "integration/authority",
        "source": {"title": "NEXT-05A Independent Integration Gateway", "drive_file_id": "14frBOqD79UwrBr_lupq_nZIexg87Fu8jyjNH3cvMV-Q", "revision_id": "25"},
        "semantic_signature": ["independent_review", "authenticated_identity", "verified_competence", "signature", "authority_gate"],
        "status": "RECOVERED_PREDECESSOR",
        "current_runtime_refs": ["promotion verifier", "Y1 authority membrane"],
        "residuals": ["preserve historical non-equivalences as regression laws"],
        "priority": 70,
        "boundary": "review record != independent review; identity reference != authentication; digest != signature; accepted envelope != authority.",
    },
]


def _copy(row: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(row))
