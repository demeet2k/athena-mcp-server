from __future__ import annotations

WAVE3_VERSION = "DRIVE.ORGAN-RECOVERY.WAVE3.1"
WAVE3_ATHENA_HEAD = "b67492c589e7cb9f5d31611b23343ad02896baa2"
WAVE3_MCP_HEAD = "ce316e28e6de50b278b30ca77c0cd07da0896912"
AUTOWEAVE_ISSUE = "demeet2k/athena-mcp-server#67"

WAVE3_ORGANS = [
    {
        "organ_id": "autoweave.lateral_consequence_transport",
        "family": "navigation/integration",
        "source": {"title": "CRYSTAL Δ — THE ACTUAL FAILURE", "drive_file_id": "1fJMUhqLeJ3XOZBfBWY_dkWtgmGfwEOfdK3kOOmNWaiA", "revision_id": "24"},
        "semantic_signature": ["material_delta", "spore_signature", "automatic_consequence_transport", "seam_search", "bridge_test", "bounded_propagation", "holonomy_classification", "frontier_revaluation"],
        "status": "RESIDUAL_HIGH_VALUE_SCOPED_ISSUE",
        "current_runtime_refs": ["athena_mcp/rehydration_terminal.py", "athena_mcp/aor_collective_transport.py", "athena_mcp/collective_discovery.py", AUTOWEAVE_ISSUE],
        "residuals": ["encode material delta as deterministic cross-organ signature", "bounded candidate seam search", "compile and test legal bridge before propagation", "classify loop/holonomy residual", "handoff verified propagated residuals to existing GAP/FIELD/AOR/continuation"],
        "priority": 99,
        "boundary": "Forward continuation and explicit typed transport already exist; this is only the missing bounded seam compiler. Similarity is not a bridge, and propagation does not elevate evidence, authority, or execution permission.",
    },
    {
        "organ_id": "federated_jspace.typed_bridge_geometry",
        "family": "navigation/transport_geometry",
        "source": {"title": "FEDERATED J-SPACE CRYSTAL", "drive_file_id": "1iV7l7UqjFvmInm9-0FEC4pOmVQvH718zjrFWhajRbJ8", "revision_id": "13"},
        "semantic_signature": ["local_crystal", "overlap_interface", "partial_transport", "domain_range", "invariant_preservation", "loss_distortion", "covariant_delta", "holonomy", "return_route"],
        "status": "THEORY_OPERATOR_SOURCE_SCOPED_ISSUE",
        "current_runtime_refs": ["athena_mcp/aor_collective_transport.py", "athena_mcp/orchestration_equivalence.py", AUTOWEAVE_ISSUE],
        "residuals": ["supply legal bridge packet semantics and loop classification to issue #67 without creating a parallel transport bus"],
        "priority": 93,
        "boundary": "SIMILARITY != TRANSPORT; nonzero holonomy may encode path dependence, loss, topology, phase, inconsistent assumptions, missing cells, or a genuine defect and must be classified rather than blindly minimized.",
    },
    {
        "organ_id": "engineering.ggct_master_compiler",
        "family": "engineering/formalization",
        "source": {"title": "GGCT MASTER TOME", "drive_file_id": "1wa2YcOuVahRlOYjsix-iw01bh5v_ZHyI-92zr3Qpndg", "revision_id": "25"},
        "semantic_signature": ["FIELD", "CONSTRAINT", "CONTACT", "PROGRAM", "path_separation", "unknown_ledger", "witness", "return"],
        "status": "THEORY_PREDECESSOR_PARTIAL_CURRENT",
        "current_runtime_refs": ["BNMK", "existing evidence/authority/safety membranes"],
        "residuals": ["retain as engineering-compiler lineage and use only when a concrete current engineering/path defect survives dedup"],
        "priority": 70,
        "boundary": "symbolic != mathematical != physical != certified; component rating != assembly != system permission; structural completeness != truth/safety/authority.",
    },
    {
        "organ_id": "authority.immutable_release_manifest",
        "family": "authority/release",
        "source": {"title": "AUTHORIZATION DECISION BOARD Ω1", "drive_file_id": "1YIb459lb4huzrHUc271fiVqykNR_-qfwTo_2HnY-kfk", "revision_id": "4"},
        "semantic_signature": ["explicit_authorization", "immutable_release_artifact", "digest_drift", "authorize", "draft", "revise", "hold", "reject"],
        "status": "RECOVERED_PREDECESSOR_PARTIAL_CURRENT",
        "current_runtime_refs": ["Y1 authority", "promotion verifier", "immutable Git artifacts"],
        "residuals": ["preserve immutable release-target regression law for communication/mutation authorization paths"],
        "priority": 68,
        "boundary": "silence, repeated NEXT, priority, public channel, and expected benefit are not authorization.",
    },
    {
        "organ_id": "goalforge.verified_intelligence_yield",
        "family": "goal/optimization",
        "source": {"title": "Ω-GOALFORGE 4098", "drive_file_id": "1s7pv6otq85b8KftJa2rvUggEyeyU4FeSAP3ScrXZ-Ks", "revision_id": "9"},
        "semantic_signature": ["verified_intelligence_yield", "goal_ladder", "goal_contract", "observed_outcome_calibration", "stopping", "continuation", "return"],
        "status": "RECOVERED_PREDECESSOR_PARTIAL_CURRENT",
        "current_runtime_refs": ["MAXDEV core", "AOR", "witnessed continuation/closure runtime"],
        "residuals": ["retain as goal-contract and measurement vocabulary; add runtime structure only after a concrete uncovered decision defect"],
        "priority": 66,
        "boundary": "predicted setter value does not update learned state; only observed outcomes do.",
    },
]
