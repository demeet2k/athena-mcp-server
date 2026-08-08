from __future__ import annotations

"""Measured runtime capability and transport overlays for the KC144 crystal.

The digest-bound structural manifest remains an immutable source snapshot. This
module separately derives current organ and transport liveness from the actual
MCP tool/resource surface. Discovery proves dispatch exposure only; it never
promotes evidence, authority, empirical truth, release, merge or deployment.
"""

from typing import Any, Iterable

INTEGRATION_BASE_SHA = "6e9f9cc57564c80e29874c276d21addb0c99d530"
ACTIVE_PARENT_RUNTIME_SHA = INTEGRATION_BASE_SHA  # compatibility alias
STRUCTURAL_SOURCE_SNAPSHOT_SHA = "6b643134ee26ce117c2b548b5a89edf5cec55934"


def _requirement(
    identifier: str,
    tools: tuple[str, ...],
    resources: tuple[str, ...],
    live_state: str = "LIVE_UNIFIED",
    missing_state: str = "NOT_SURFACED",
) -> dict[str, Any]:
    return {
        "id": identifier,
        "required_tools": tools,
        "required_resources": resources,
        "live_state": live_state,
        "missing_state": missing_state,
    }


ORGAN_CAPABILITY_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    _requirement(
        "ORGAN.GIT_LEDGER",
        ("athena_git_status", "athena_session_start", "athena_session_end"),
        ("athena://state/head",),
    ),
    _requirement(
        "ORGAN.CRYSTAL_RUNTIME",
        (
            "athena_crystallize_output",
            "athena_finalize_output",
            "athena_verify_emission",
            "athena_dense_navigate",
        ),
        ("athena://crystals", "athena://emissions"),
    ),
    _requirement(
        "ORGAN.COLLECTIVE_RUNTIME",
        (
            "athena_collective_plan",
            "athena_collective_allocate",
            "athena_pheromone_field",
            "athena_bandit_select",
            "athena_bayes_predict",
            "athena_ood_score",
            "athena_dual_control_plan",
        ),
        (
            "athena://collective/runtime",
            "athena://collective/growth",
            "athena://collective/v2",
            "athena://collective/v3",
            "athena://collective/v4",
            "athena://collective/v5",
            "athena://collective/v6",
            "athena://collective/v7",
        ),
    ),
    _requirement(
        "ORGAN.AOR_CORE",
        (
            "athena_orchestrate",
            "athena_orchestration_get",
            "athena_orchestration_replay",
            "athena_orchestration_recent",
            "athena_orchestration_robustness",
        ),
        (
            "athena://orchestration/law",
            "athena://orchestration/recent",
            "athena://orchestration/robustness",
        ),
    ),
    _requirement(
        "ORGAN.BRANCH_EVOLUTION",
        (
            "athena_branch_observe",
            "athena_branch_state",
            "athena_branch_list",
            "athena_branch_review",
        ),
        ("athena://branches",),
    ),
    _requirement(
        "ORGAN.AUTHORITY_Y1",
        (
            "athena_claim_register",
            "athena_claim_state",
            "athena_claim_list",
            "athena_claim_promote",
            "athena_claim_challenge",
        ),
        ("athena://authority",),
    ),
    _requirement(
        "ORGAN.EQ1",
        (
            "athena_equivalence_observe",
            "athena_equivalence_state",
            "athena_equivalence_resolve_conflict",
            "athena_equivalence_snapshot",
        ),
        ("athena://equivalence",),
    ),
    _requirement(
        "ORGAN.SX1",
        (
            "athena_extraction_plan",
            "athena_extraction_task",
            "athena_extraction_complete",
            "athena_extraction_fail",
            "athena_extraction_result",
            "athena_extraction_expand_result",
            "athena_extraction_frontier",
            "athena_extraction_run",
        ),
        ("athena://extraction",),
    ),
    _requirement(
        "ORGAN.RAG1",
        (
            "athena_retrieval_compile",
            "athena_retrieval_get",
            "athena_retrieval_replay",
            "athena_retrieval_recent",
        ),
        ("athena://retrieval",),
    ),
    _requirement(
        "ORGAN.HUG_ABI1",
        (
            "athena_hug_register",
            "athena_hug_state",
            "athena_hug_list",
            "athena_hug_promote",
            "athena_hug_plan",
            "athena_hug_complete",
            "athena_hug_fail",
            "athena_hug_invocation",
            "athena_hug_verify_packet",
        ),
        ("athena://hug",),
        "LIVE_UNIFIED_FAIL_CLOSED",
        "CONTRACT_PRESENT_NOT_SURFACED",
    ),
    _requirement(
        "ORGAN.GAP1",
        (
            "athena_gap_compile",
            "athena_gap_get",
            "athena_gap_replay",
            "athena_gap_recent",
        ),
        ("athena://gap",),
    ),
    _requirement(
        "ORGAN.FIELD1",
        (
            "athena_field_compile",
            "athena_field_get",
            "athena_field_replay",
            "athena_field_recent",
        ),
        ("athena://field",),
    ),
    _requirement(
        "ORGAN.TRANSPORT1",
        (
            "athena_transport_pheromone_attention",
            "athena_transport_alarm_to_gap",
            "athena_transport_aor_to_collective",
            "athena_transport_rgo_to_reward",
            "athena_transport_bridge_to_collective",
            "athena_transport_antibody_to_repair",
            "athena_transport_get",
            "athena_transport_replay",
            "athena_transport_recent",
        ),
        ("athena://aor-collective/transport",),
    ),
    _requirement(
        "ORGAN.CYCLE1",
        (
            "athena_cycle_start",
            "athena_cycle_advance",
            "athena_cycle_state",
            "athena_cycle_replay",
            "athena_cycle_recent",
        ),
        ("athena://cycle",),
        "LIVE_UNIFIED_FAIL_CLOSED",
    ),
    _requirement(
        "ORGAN.STATE_FOUNDATION1",
        (
            "athena_schema_status",
            "athena_schema_plan",
            "athena_schema_migrate",
            "athena_schema_verify",
            "athena_omega_state",
            "athena_reconstruct_state",
            "athena_reconstruction_get",
            "athena_reconstruction_verify",
            "athena_reconstruction_recent",
        ),
        ("athena://schema", "athena://state/omega", "athena://reconstruction"),
    ),
    _requirement(
        "ORGAN.SELFTEST1",
        ("athena_self_test",),
        ("athena://self-test",),
    ),
    _requirement(
        "ORGAN.STARTUP1",
        ("athena_startup_health",),
        ("athena://startup-health",),
    ),
    _requirement(
        "ORGAN.SURFACE1",
        ("athena_surface_audit",),
        ("athena://surface",),
    ),
    _requirement(
        "ORGAN.COMPOSITION1",
        ("athena_surface_audit",),
        ("athena://surface",),
        "LIVE_UNIFIED_VIA_SURFACE_CERTIFICATE",
    ),
    _requirement(
        "ORGAN.PROMOTION1",
        (
            "athena_promotion_evaluate",
            "athena_promotion_get",
            "athena_promotion_replay",
            "athena_promotion_recent",
        ),
        ("athena://promotion",),
        "LIVE_UNIFIED_FAIL_CLOSED",
    ),
    _requirement(
        "ORGAN.UNIFIED_MANIFEST1",
        ("athena_runtime_manifest", "athena_maxdev_law"),
        ("athena://runtime/unified-manifest", "athena://runtime/maxdev"),
    ),
    _requirement(
        "ORGAN.SYSTEM_UPGRADE1",
        (
            "athena_system_upgrade_manifest",
            "athena_system_upgrade_plan",
            "athena_system_upgrade_state",
            "athena_system_upgrade_observe",
            "athena_system_upgrade_refresh",
            "athena_system_upgrade_replay",
            "athena_system_upgrade_recent",
            "athena_system_release_certificate",
            "athena_system_release_get",
            "athena_system_release_replay",
            "athena_system_release_recent",
        ),
        (
            "athena://system/upgrade",
            "athena://system/upgrade/frontier",
            "athena://system/release",
        ),
        "LIVE_UNIFIED_WITNESS_GATED",
    ),
    _requirement(
        "ORGAN.TOPOLOGICAL_COMMAND_HUB",
        (
            "athena_kc144_hub_status",
            "athena_kc144_hub_manifest",
            "athena_kc144_hub_seat",
            "athena_kc144_hub_inventory",
            "athena_kc144_hub_graph",
            "athena_kc144_hub_route",
            "athena_kc144_hub_datasets",
            "athena_kc144_hub_communication",
            "athena_kc144_hub_readiness",
            "athena_kc144_hub_validate",
        ),
        (
            "athena://kc144/hub",
            "athena://kc144/hub/manifest",
            "athena://kc144/hub/inventory",
            "athena://kc144/hub/graphs",
            "athena://kc144/hub/datasets",
            "athena://kc144/hub/communication",
            "athena://kc144/hub/readiness",
            "athena://kc144/hub/validation",
        ),
    ),
    _requirement(
        "ORGAN.KC144_REGISTRY_PACK",
        (
            "athena_kc144_registry_status",
            "athena_kc144_registry_catalog",
            "athena_kc144_registry_query",
            "athena_kc144_registry_cross_search",
            "athena_kc144_registry_source_bundle",
            "athena_kc144_registry_cell_bundle",
            "athena_kc144_completion_frontier",
            "athena_kc144_registry_verify",
        ),
        (
            "athena://kc144/registry/status",
            "athena://kc144/registry/catalog",
            "athena://kc144/registry/manifest",
            "athena://kc144/registry/verification",
            "athena://kc144/completion/frontier",
        ),
    ),
    _requirement(
        "ORGAN.KC144_POLYATLAS",
        (
            "athena_kc144_polyatlas_status",
            "athena_kc144_polyatlas_manifest",
            "athena_kc144_polyatlas_seat",
            "athena_kc144_polyatlas_rosetta",
            "athena_kc144_resolution_transport",
            "athena_kc144_resolution_family",
            "athena_kc144_sphere_atlas",
            "athena_kc144_polyatlas_route",
            "athena_kc144_polyatlas_validate",
        ),
        (
            "athena://kc144/polyatlas/status",
            "athena://kc144/polyatlas/manifest",
            "athena://kc144/polyatlas/sources",
            "athena://kc144/polyatlas/sphere",
            "athena://kc144/polyatlas/family",
            "athena://kc144/polyatlas/validation",
        ),
    ),
)


TRANSPORT_CAPABILITY_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    _requirement(
        "TRANSPORT.PHEROMONE_TO_RAG",
        ("athena_transport_pheromone_attention",),
        ("athena://aor-collective/transport",),
        "LIVE_ROUTING_PRIOR_NOT_EVIDENCE",
    ),
    _requirement(
        "TRANSPORT.ALARM_TO_GAP",
        ("athena_transport_alarm_to_gap",),
        ("athena://aor-collective/transport",),
        "LIVE_TYPED_INVALIDATION_PRESSURE",
    ),
    _requirement(
        "TRANSPORT.RGO_TO_REWARD",
        ("athena_transport_rgo_to_reward",),
        ("athena://aor-collective/transport",),
        "LIVE_WITNESSED_OUTCOME_GATED",
    ),
    _requirement(
        "TRANSPORT.AOR_TO_COLLECTIVE",
        ("athena_transport_aor_to_collective",),
        ("athena://aor-collective/transport",),
        "LIVE_UNMEASURED_RESOURCE_FIREWALL",
    ),
    _requirement(
        "TRANSPORT.BRIDGE_TO_COLLECTIVE",
        ("athena_transport_bridge_to_collective",),
        ("athena://aor-collective/transport",),
        "LIVE_EXPLICIT_ECONOMICS_REQUIRED",
    ),
    _requirement(
        "TRANSPORT.ANTIBODY_TO_REPAIR",
        ("athena_transport_antibody_to_repair",),
        ("athena://aor-collective/transport",),
        "LIVE_UNMEASURED_REPAIR_ONLY",
    ),
    _requirement(
        "TRANSPORT.FIELD_TO_PROMOTION",
        ("athena_field_compile", "athena_promotion_evaluate"),
        ("athena://field", "athena://promotion"),
        "LIVE_GATE_SEPARATED",
    ),
    _requirement(
        "TRANSPORT.PROMOTION_TO_RETURN",
        ("athena_promotion_replay", "athena_system_release_certificate"),
        ("athena://promotion", "athena://system/release"),
        "LIVE_EXACT_HEAD_RECEIPT_GATED",
    ),
)


def _overlay(
    requirements: Iterable[dict[str, Any]],
    tool_names: Iterable[str],
    resource_uris: Iterable[str],
) -> dict[str, dict[str, Any]]:
    discovered_tools = set(tool_names)
    discovered_resources = set(resource_uris)
    result: dict[str, dict[str, Any]] = {}
    for requirement in requirements:
        required_tools = set(requirement["required_tools"])
        required_resources = set(requirement.get("required_resources", ()))
        missing_tools = sorted(required_tools - discovered_tools)
        missing_resources = sorted(required_resources - discovered_resources)
        surface_pass = not missing_tools and not missing_resources
        result[requirement["id"]] = {
            "id": requirement["id"],
            "state": (
                requirement["live_state"]
                if surface_pass
                else requirement.get("missing_state", "NOT_SURFACED")
            ),
            "required_tools": sorted(required_tools),
            "present_tools": sorted(required_tools & discovered_tools),
            "missing_tools": missing_tools,
            "required_resources": sorted(required_resources),
            "present_resources": sorted(required_resources & discovered_resources),
            "missing_resources": missing_resources,
            "surface_pass": surface_pass,
            "integration_base_sha": INTEGRATION_BASE_SHA,
        }
    return result


def runtime_organ_overlay(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, dict[str, Any]]:
    return _overlay(ORGAN_CAPABILITY_REQUIREMENTS, tool_names, resource_uris)


def runtime_transport_overlay(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, dict[str, Any]]:
    return _overlay(TRANSPORT_CAPABILITY_REQUIREMENTS, tool_names, resource_uris)


def overlay_summary(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, Any]:
    overlay = runtime_organ_overlay(tool_names, resource_uris)
    return {
        "integration_base_sha": INTEGRATION_BASE_SHA,
        "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        "structural_source_snapshot_sha": STRUCTURAL_SOURCE_SNAPSHOT_SHA,
        "organs": overlay,
        "live": sorted(key for key, value in overlay.items() if value["surface_pass"]),
        "not_live": sorted(key for key, value in overlay.items() if not value["surface_pass"]),
        "all_required_live": all(value["surface_pass"] for value in overlay.values()),
        "boundary": "surface liveness is dispatch discovery, not evidence, authority or semantic truth",
    }


def transport_overlay_summary(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, Any]:
    overlay = runtime_transport_overlay(tool_names, resource_uris)
    return {
        "integration_base_sha": INTEGRATION_BASE_SHA,
        "transports": overlay,
        "live": sorted(key for key, value in overlay.items() if value["surface_pass"]),
        "not_live": sorted(key for key, value in overlay.items() if not value["surface_pass"]),
        "all_required_live": all(value["surface_pass"] for value in overlay.values()),
        "boundary": (
            "transport liveness proves typed adapter availability only; each adapter retains "
            "its source/evidence/measurement/authority firewall"
        ),
    }
