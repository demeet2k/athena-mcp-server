from __future__ import annotations

"""Exact-head runtime capability overlay for the structural KC144 crystal.

The structural manifest is digest-bound to its original source snapshot. This
module separately records the active integration base and derives organ liveness
from the actually discovered MCP tool/resource surface, preventing branch drift
from being silently mislabeled as either live or absent.
"""

from typing import Any, Iterable

ACTIVE_PARENT_RUNTIME_SHA = "10f1dc39ffc6066ea00f880ef522050394fd5e3a"
STRUCTURAL_SOURCE_SNAPSHOT_SHA = "6b643134ee26ce117c2b548b5a89edf5cec55934"

ORGAN_CAPABILITY_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "ORGAN.EQ1",
        "required_tools": (
            "athena_equivalence_observe",
            "athena_equivalence_state",
            "athena_equivalence_resolve_conflict",
            "athena_equivalence_snapshot",
        ),
        "required_resources": ("athena://equivalence",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "NOT_SURFACED",
    },
    {
        "id": "ORGAN.SX1",
        "required_tools": (
            "athena_extraction_plan",
            "athena_extraction_task",
            "athena_extraction_complete",
            "athena_extraction_fail",
            "athena_extraction_result",
            "athena_extraction_expand_result",
            "athena_extraction_frontier",
            "athena_extraction_run",
        ),
        "required_resources": ("athena://extraction",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "NOT_SURFACED",
    },
    {
        "id": "ORGAN.RAG1",
        "required_tools": (
            "athena_retrieval_compile",
            "athena_retrieval_get",
            "athena_retrieval_replay",
            "athena_retrieval_recent",
        ),
        "required_resources": ("athena://retrieval",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "NOT_SURFACED",
    },
    {
        "id": "ORGAN.HUG_ABI1",
        "required_tools": (
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
        "required_resources": ("athena://hug",),
        "live_state": "LIVE_UNIFIED_FAIL_CLOSED",
        "missing_state": "CONTRACT_PRESENT_NOT_SURFACED",
    },
    {
        "id": "ORGAN.GAP1",
        "required_tools": (
            "athena_gap_compile",
            "athena_gap_get",
            "athena_gap_replay",
            "athena_gap_recent",
        ),
        "required_resources": ("athena://gap",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "STAGED_SOURCE_NOT_SURFACED",
    },
    {
        "id": "ORGAN.FIELD1",
        "required_tools": (
            "athena_field_compile",
            "athena_field_get",
            "athena_field_replay",
            "athena_field_recent",
        ),
        "required_resources": ("athena://field",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "STAGED_SOURCE_NOT_SURFACED",
    },
    {
        "id": "ORGAN.SURFACE1",
        "required_tools": ("athena_surface_audit",),
        "required_resources": ("athena://surface",),
        "live_state": "LIVE_UNIFIED",
        "missing_state": "STAGED_SOURCE_NOT_SURFACED",
    },
    {
        "id": "ORGAN.COMPOSITION1",
        "required_tools": ("athena_surface_audit",),
        "required_resources": ("athena://surface",),
        "live_state": "LIVE_UNIFIED_VIA_SURFACE_CERTIFICATE",
        "missing_state": "STAGED_SOURCE_NOT_SURFACED",
    },
    {
        "id": "ORGAN.PROMOTION1",
        "required_tools": (
            "athena_promotion_evaluate",
            "athena_promotion_get",
            "athena_promotion_replay",
            "athena_promotion_recent",
        ),
        "required_resources": ("athena://promotion",),
        "live_state": "LIVE_UNIFIED_FAIL_CLOSED",
        "missing_state": "STAGED_SOURCE_NOT_SURFACED",
    },
)


def runtime_organ_overlay(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, dict[str, Any]]:
    discovered_tools = set(tool_names)
    discovered_resources = set(resource_uris)
    result: dict[str, dict[str, Any]] = {}
    for requirement in ORGAN_CAPABILITY_REQUIREMENTS:
        required_tools = set(requirement["required_tools"])
        required_resources = set(requirement.get("required_resources", ()))
        present_tools = sorted(required_tools & discovered_tools)
        missing_tools = sorted(required_tools - discovered_tools)
        present_resources = sorted(required_resources & discovered_resources)
        missing_resources = sorted(required_resources - discovered_resources)
        surface_pass = not missing_tools and not missing_resources
        result[requirement["id"]] = {
            "id": requirement["id"],
            "state": requirement["live_state"] if surface_pass else requirement["missing_state"],
            "required_tools": sorted(required_tools),
            "present_tools": present_tools,
            "missing_tools": missing_tools,
            "required_resources": sorted(required_resources),
            "present_resources": present_resources,
            "missing_resources": missing_resources,
            "surface_pass": surface_pass,
            "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        }
    return result


def overlay_summary(
    tool_names: Iterable[str],
    resource_uris: Iterable[str] = (),
) -> dict[str, Any]:
    overlay = runtime_organ_overlay(tool_names, resource_uris)
    return {
        "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        "structural_source_snapshot_sha": STRUCTURAL_SOURCE_SNAPSHOT_SHA,
        "organs": overlay,
        "live": sorted(key for key, value in overlay.items() if value["surface_pass"]),
        "not_live": sorted(key for key, value in overlay.items() if not value["surface_pass"]),
    }
