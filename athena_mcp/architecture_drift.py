from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence

ORGAN_INVENTORY_VERSION = "ATHENA.ORGAN.INVENTORY.1"
ARCHITECTURE_DRIFT_VERSION = "ATHENA.ARCHITECTURE.DRIFT.1"

# Explicit mature-organ registry. This is intentionally not filesystem discovery:
# helper modules, experimental code and historical compatibility files must never
# become canonical organs merely because a .py file exists.
MATURE_ORGANS: tuple[dict[str, Any], ...] = (
    {
        "id": "MESSAGE_BOARD_V1",
        "version": "ATHENA.MESSAGE.BOARD.V1",
        "integration_class": "PROMPT_RUNTIME_PUBLIC",
        "authority_plane": "COORDINATION_PRESENCE_CLAIM_MESSAGE",
        "manifest_layer": "MESSAGE_BOARD_V1",
        "omega_key": "coordination",
        "tools": ["athena_message_board"],
        "resources": [],
        "critical_tests": [
            "tests/test_message_board.py",
            "tests/test_message_board_registration.py",
            "tests/test_agent_bootstrap_message_board.py",
        ],
        "spec_refs": ["spec/AGENT_BOOT_MESSAGE_BOARD_V1.json"],
        "source_refs": [
            "athena_mcp/message_board.py",
            "athena_mcp/agent_bootstrap_message_board.py",
            "athena_mcp/agent_bootstrap_message_board_activation.py",
        ],
        "laws": [
            "MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY",
            "MESSAGE_BOARD != Y1_CANONICAL_SEMANTIC_AUTHORITY",
            "BOARD_STATE != EXECUTION_AUTHORITY != WORLD_TRUTH",
        ],
    },
    {
        "id": "COHESION_MESH_V1",
        "version": "COHESION.MESH.MATCHMAKING.1",
        "integration_class": "PUBLIC_GIT_BACKED_LAZY",
        "authority_plane": "ADVISORY_COORDINATION",
        "manifest_layer": "COHESION_MESH_V1",
        "omega_key": "coordination",
        "tools": [
            "athena_cohesion_request_offer",
            "athena_cohesion_matchmake",
            "athena_cohesion_coalition",
            "athena_cohesion_solo_party_compare",
        ],
        "resources": ["athena://cohesion/v1"],
        "critical_tests": ["tests/test_cohesion_matchmaking.py"],
        "spec_refs": [],
        "source_refs": [
            "athena_mcp/cohesion_mesh.py",
            "athena_mcp/cohesion_matchmaking.py",
            "athena_mcp/cohesion_mesh_protocol.py",
        ],
        "laws": [
            "COHESION != CLAIM_AUTHORITY",
            "COHESION != ASSIGNMENT_AUTHORITY",
            "COHESION != EXECUTION_AUTHORITY",
        ],
    },
    {
        "id": "COHESION_DUPLICATE_GUARD_V1",
        "version": "ATHENA.COHESION.DUPLICATE.GUARD.V1",
        "integration_class": "PUBLIC_READ_ONLY_MEMBRANE",
        "authority_plane": "READ_ONLY_STEERING",
        "manifest_layer": "COHESION_DUPLICATE_GUARD_V1",
        "omega_key": "coordination",
        "tools": ["athena_cohesion_duplicate_guard"],
        "resources": [],
        "critical_tests": ["tests/test_cohesion_duplicate_guard.py"],
        "spec_refs": ["spec/COHESION_DUPLICATE_GUARD_V1.json"],
        "source_refs": [
            "athena_mcp/cohesion_duplicate_guard.py",
            "athena_mcp/cohesion_duplicate_guard_protocol.py",
        ],
        "laws": [
            "DUPLICATE_GUARD != CLAIM_MUTATION",
            "FUZZY_SIMILARITY != DUPLICATE_PROOF",
            "TREATMENT_OPTION != TREATMENT_EXECUTION",
        ],
    },
    {
        "id": "COHESION_EVIDENCE_GUARD_V1",
        "version": "ATHENA.COHESION.EVIDENCE.GUARD.V1",
        "integration_class": "INTERNAL_FAIL_CLOSED_MEMBRANE",
        "authority_plane": "EVIDENCE_COVERAGE_ONLY",
        "manifest_layer": "COHESION_EVIDENCE_GUARD_V1",
        "omega_key": "coordination",
        "tools": [],
        "resources": [],
        "critical_tests": ["tests/test_cohesion_evidence_guard.py"],
        "spec_refs": [],
        "source_refs": ["athena_mcp/cohesion_evidence_guard.py"],
        "laws": [
            "PARTIAL_MATCHED_SUBSET_OR_REUSED_EVIDENCE != SUFFICIENT_COMPARATIVE_EVIDENCE",
            "CAUSAL_EFFECT = UNKNOWN",
            "PROMOTION_AUTHORITY = FALSE",
        ],
    },
    {
        "id": "AGENT_BOOT_COHESION_TREATMENT_V1",
        "version": "ATHENA.AGENT.BOOT.COHESION.TREATMENT.V1",
        "integration_class": "BOOTSTRAP_ONLY_READ_ONLY_PROJECTION",
        "authority_plane": "BOOTSTRAP_STEERING",
        "manifest_layer": "AGENT_BOOT_COHESION_TREATMENT_V1",
        "omega_key": "coordination",
        "tools": [],
        "resources": [],
        "critical_tests": ["tests/test_agent_bootstrap_cohesion_treatment.py"],
        "spec_refs": ["spec/AGENT_BOOT_COHESION_TREATMENT_V1.json"],
        "source_refs": ["athena_mcp/agent_bootstrap_cohesion_treatment.py"],
        "laws": [
            "BOOT_HOLD != TREATMENT_EXECUTION",
            "TREATMENT_PROJECTION != CLAIM_MUTATION",
            "COHESION_GUARD = READ_ONLY_STEERING",
        ],
    },
)


def _set(values: Iterable[str] | None) -> set[str]:
    return {str(value) for value in (values or []) if str(value)}


def inventory_manifest() -> dict[str, Any]:
    return {
        "version": ORGAN_INVENTORY_VERSION,
        "organs": [dict(organ) for organ in MATURE_ORGANS],
        "law": (
            "maturity is explicit, never inferred from file existence; each mature organ declares its "
            "runtime class, authority plane, public surfaces, manifest coordinate, OMEGA coordinate and critical witnesses"
        ),
    }


def audit_architecture(
    *,
    observed_tools: Iterable[str],
    observed_resources: Iterable[str],
    manifest_layers: Iterable[str],
    surface_required_tools: Iterable[str],
    surface_required_resources: Iterable[str],
    omega_components: Iterable[str],
    ci_text: str = "",
    available_paths: Iterable[str] | None = None,
    organs: Sequence[Mapping[str, Any]] = MATURE_ORGANS,
) -> dict[str, Any]:
    tools = _set(observed_tools)
    resources = _set(observed_resources)
    layers = _set(manifest_layers)
    surface_tools = _set(surface_required_tools)
    surface_resources = _set(surface_required_resources)
    omega = _set(omega_components)
    paths = _set(available_paths)
    ci = str(ci_text or "")
    rows: list[dict[str, Any]] = []
    defects: list[dict[str, Any]] = []

    for raw in organs:
        organ = dict(raw)
        oid = str(organ["id"])
        required_tools = _set(organ.get("tools"))
        required_resources = _set(organ.get("resources"))
        required_tests = [str(path) for path in organ.get("critical_tests") or []]
        required_paths = [str(path) for path in (organ.get("source_refs") or []) + (organ.get("spec_refs") or [])]

        runtime_missing_tools = sorted(required_tools - tools)
        runtime_missing_resources = sorted(required_resources - resources)
        surface_missing_tools = sorted(required_tools - surface_tools)
        surface_missing_resources = sorted(required_resources - surface_resources)
        manifest_missing = str(organ.get("manifest_layer")) not in layers
        omega_missing = str(organ.get("omega_key")) not in omega
        ci_missing = sorted(path for path in required_tests if path not in ci) if ci else []
        file_missing = sorted(path for path in required_paths if paths and path not in paths)

        organ_defects: list[dict[str, Any]] = []
        for kind, values in (
            ("RUNTIME_TOOL_MISSING", runtime_missing_tools),
            ("RUNTIME_RESOURCE_MISSING", runtime_missing_resources),
            ("SURFACE_TOOL_MISSING", surface_missing_tools),
            ("SURFACE_RESOURCE_MISSING", surface_missing_resources),
            ("CRITICAL_WITNESS_MISSING", ci_missing),
            ("SOURCE_OR_SPEC_MISSING", file_missing),
        ):
            if values:
                organ_defects.append({"kind": kind, "values": values})
        if manifest_missing:
            organ_defects.append({"kind": "MANIFEST_LAYER_MISSING", "values": [organ.get("manifest_layer")]})
        if omega_missing:
            organ_defects.append({"kind": "OMEGA_COORDINATE_MISSING", "values": [organ.get("omega_key")]})

        status = "PASS" if not organ_defects else "DRIFT"
        row = {
            "id": oid,
            "version": organ.get("version"),
            "integration_class": organ.get("integration_class"),
            "authority_plane": organ.get("authority_plane"),
            "status": status,
            "defects": organ_defects,
            "laws": list(organ.get("laws") or []),
        }
        rows.append(row)
        for defect in organ_defects:
            defects.append({"organ_id": oid, **defect})

    return {
        "version": ARCHITECTURE_DRIFT_VERSION,
        "status": "PASS" if not defects else "ARCHITECTURE_DRIFT",
        "organ_inventory_version": ORGAN_INVENTORY_VERSION,
        "organ_count": len(rows),
        "drift_count": sum(1 for row in rows if row["status"] != "PASS"),
        "organs": rows,
        "defects": defects,
        "law": (
            "a mature organ is not integrated merely because code, tools or unit tests exist; runtime discovery, "
            "SURFACE, manifest, OMEGA and critical witnesses must agree according to the organ's declared class"
        ),
        "boundary": (
            "unregistered helper/experimental modules are outside this audit; maturity must be declared explicitly "
            "before an organ can influence promotion"
        ),
    }
