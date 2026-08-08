from __future__ import annotations

"""V11-aware measured runtime truth overlay.

The original KC144 overlay is retained in ``runtime_truth_core`` as a
replayable source snapshot.  This module changes only the active integration
basis and expands the Collective capability contract through V11.  Surface
presence is still dispatch evidence only: it is not semantic truth, Y1
authority, merge authority, or deployment authority.
"""

from typing import Any, Iterable

from . import runtime_truth_core as _core

INTEGRATION_BASE_SHA = "0d7b50f43859a27b4e386e89e198adb4d477e118"
ACTIVE_PARENT_RUNTIME_SHA = INTEGRATION_BASE_SHA
STRUCTURAL_SOURCE_SNAPSHOT_SHA = _core.STRUCTURAL_SOURCE_SNAPSHOT_SHA

_V11_TOOLS = (
    "athena_belief_register",
    "athena_decision_evi",
    "athena_gaussian_belief_register",
    "athena_decision_evpi",
    "athena_structure_partial",
    "athena_gp_register",
    "athena_gp_predict",
    "athena_pc_stable_discover",
    "athena_causal_tmle_binary",
    "athena_pomdp_solve",
    "athena_gp_hyperfit",
    "athena_gp_decision_evsi",
    "athena_latent_project_admg",
    "athena_causal_tmle_ensemble",
    "athena_sensitivity_rr_surface",
    "athena_bapomdp_solve",
    "athena_evidence_dependence_interval",
)
_V11_RESOURCES = (
    "athena://collective/v8",
    "athena://collective/v9",
    "athena://collective/v10",
    "athena://collective/v11",
)


def _augment_collective(requirement: dict[str, Any]) -> dict[str, Any]:
    item = dict(requirement)
    if item.get("id") != "ORGAN.COLLECTIVE_RUNTIME":
        return item
    item["required_tools"] = tuple(
        dict.fromkeys((*item.get("required_tools", ()), *_V11_TOOLS))
    )
    item["required_resources"] = tuple(
        dict.fromkeys((*item.get("required_resources", ()), *_V11_RESOURCES))
    )
    item["live_state"] = "LIVE_UNIFIED_V1_V11"
    return item


ORGAN_CAPABILITY_REQUIREMENTS = tuple(
    _augment_collective(item) for item in _core.ORGAN_CAPABILITY_REQUIREMENTS
)
TRANSPORT_CAPABILITY_REQUIREMENTS = _core.TRANSPORT_CAPABILITY_REQUIREMENTS


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
    tool_names: Iterable[str], resource_uris: Iterable[str] = ()
) -> dict[str, dict[str, Any]]:
    return _overlay(ORGAN_CAPABILITY_REQUIREMENTS, tool_names, resource_uris)


def runtime_transport_overlay(
    tool_names: Iterable[str], resource_uris: Iterable[str] = ()
) -> dict[str, dict[str, Any]]:
    return _overlay(TRANSPORT_CAPABILITY_REQUIREMENTS, tool_names, resource_uris)


def overlay_summary(
    tool_names: Iterable[str], resource_uris: Iterable[str] = ()
) -> dict[str, Any]:
    overlay = runtime_organ_overlay(tool_names, resource_uris)
    return {
        "integration_base_sha": INTEGRATION_BASE_SHA,
        "active_parent_runtime_sha": ACTIVE_PARENT_RUNTIME_SHA,
        "structural_source_snapshot_sha": STRUCTURAL_SOURCE_SNAPSHOT_SHA,
        "collective_release": "V11",
        "organs": overlay,
        "live": sorted(key for key, value in overlay.items() if value["surface_pass"]),
        "not_live": sorted(key for key, value in overlay.items() if not value["surface_pass"]),
        "all_required_live": all(value["surface_pass"] for value in overlay.values()),
        "boundary": (
            "surface liveness is dispatch discovery, not evidence, authority, "
            "semantic truth, merge, or deployment"
        ),
    }


def transport_overlay_summary(
    tool_names: Iterable[str], resource_uris: Iterable[str] = ()
) -> dict[str, Any]:
    overlay = runtime_transport_overlay(tool_names, resource_uris)
    return {
        "integration_base_sha": INTEGRATION_BASE_SHA,
        "transports": overlay,
        "live": sorted(key for key, value in overlay.items() if value["surface_pass"]),
        "not_live": sorted(key for key, value in overlay.items() if not value["surface_pass"]),
        "all_required_live": all(value["surface_pass"] for value in overlay.values()),
        "boundary": (
            "transport liveness proves typed adapter availability only; each adapter "
            "retains its source, evidence, measurement, and authority firewall"
        ),
    }


__all__ = [
    "INTEGRATION_BASE_SHA",
    "ACTIVE_PARENT_RUNTIME_SHA",
    "STRUCTURAL_SOURCE_SNAPSHOT_SHA",
    "ORGAN_CAPABILITY_REQUIREMENTS",
    "TRANSPORT_CAPABILITY_REQUIREMENTS",
    "runtime_organ_overlay",
    "runtime_transport_overlay",
    "overlay_summary",
    "transport_overlay_summary",
]
