from __future__ import annotations

"""Read-only typed inventory of ATHENA communication planes and bridge seams.

This inventory is navigation/observability state. It deliberately does not
collapse identities, cursors, receipt ladders, durability, or authority across
planes simply because two surfaces can exchange a reference.
"""

import importlib
from typing import Any

VERSION = "ATHENA.COMMUNICATION.PLANE.INVENTORY.1"
ARTIFACT = "ATHENA.COMMUNICATION.PLANE.INVENTORY.V1.CANDIDATE"
RESOURCE_URI = "athena://synapse/planes"
MAX_FAST_PRESENCE = 64

LAWS = [
    "COMMUNICATION_PLANE != IDENTITY_NAMESPACE",
    "SAME_ID_STRING_ACROSS_PLANES != IDENTITY_PROOF",
    "ROUTE != DELIVERY != PRESENTATION != CONSUMPTION != INCORPORATION",
    "MESSAGE_BOARD_DURABILITY != LIMINAL_OR_EPHEMERAL_LIVENESS",
    "MCP_PROCESS_CURSOR != FEDERATION_SOURCE_CURSOR",
    "SYNAPSE_ENVELOPE_ID != NATIVE_PACKET_IDENTITY",
    "IMPORTABLE_MODULE != INSTALLED_RUNTIME_ORGAN",
    "BRIDGE_INSTALLED != BRIDGE_USED != OUTCOME_IMPROVEMENT",
    "PLANE_INVENTORY != CLAIM_ASSIGNMENT_EXECUTION_OR_PROMOTION_AUTHORITY",
]


def _source_probe(module_name: str, *, version_attr: str = "VERSION") -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            return {
                "source_available": False,
                "installed": False,
                "standing": "OPTIONAL_PLANE_OR_BRIDGE_SOURCE_UNOBSERVED",
                "module": module_name,
            }
        raise
    return {
        "source_available": True,
        "installed": False,
        "standing": "SOURCE_AVAILABLE_RUNTIME_UNVERIFIED",
        "module": module_name,
        "version": getattr(module, version_attr, None),
    }


def _fast_runtime(server: Any):
    development = getattr(server, "aor_development", None)
    surface = getattr(development, "ephemeral_coordination", None)
    return getattr(surface, "runtime", None)


def _bridge_runtime(surface: Any):
    return getattr(getattr(surface, "bridge", None), "runtime", None)


def _fast_plane(server: Any, limit: int) -> dict[str, Any]:
    runtime = _fast_runtime(server)
    if runtime is None:
        return {
            "installed": False,
            "standing": "EPHEMERAL_RUNTIME_UNOBSERVED",
            "authority": "NONE",
        }
    snapshot = runtime.snapshot({
        "scope": "global",
        "cursor": 0,
        "freshness_bound_ms": 60000,
    })
    rows = sorted(snapshot.get("fresh_presence") or [], key=lambda row: str(row.get("aid") or ""))
    cap = max(1, min(int(limit or 100), MAX_FAST_PRESENCE))
    pressure = sorted(snapshot.get("queue_pressure") or [], key=lambda row: str(row.get("aid") or ""))
    needs = sorted(snapshot.get("need_offer_index") or [], key=lambda row: str(row.get("aid") or ""))
    return {
        "installed": True,
        "standing": "PROCESS_LOCAL_EPHEMERAL_RUNTIME_OBSERVED",
        "transport": "REQUEST_POLL_PROCESS_LOCAL_SQLITE",
        "fresh_presence_count": len(rows),
        "fresh_presence": rows[:cap],
        "presence_truncated": len(rows) > cap,
        "queue_pressure": pressure[:cap],
        "need_offer_index": needs[:cap],
        "cursor_floor": snapshot.get("cursor_floor"),
        "next_cursor": snapshot.get("next_cursor"),
        "replay_truncated": snapshot.get("replay_truncated"),
        "authority": snapshot.get("authority", "NONE"),
        "identity_join_policy": "NO_IMPLICIT_JOIN_TO_LIMINAL_OR_MESSAGE_BOARD",
        "housekeeping": "SNAPSHOT_MAY_RUN_EXISTING_EPHEMERAL_TTL_GC_ONLY",
    }


def build_plane_inventory(server: Any, synapse: dict[str, Any] | None = None, *, limit: int = 100) -> dict[str, Any]:
    synapse = dict(synapse or {})
    metrics = synapse.get("metrics") if isinstance(synapse.get("metrics"), dict) else {}
    fast = _fast_plane(server, limit)
    fast_runtime = _fast_runtime(server)
    development = getattr(server, "aor_development", None)

    envelope = _source_probe("athena_mcp.synapse_liminal_adapter", version_attr="SYNAPSE_SCHEMA")
    if envelope.get("source_available"):
        module = importlib.import_module("athena_mcp.synapse_liminal_adapter")
        live = bool(getattr(type(server), "_athena_synapse_liminal_v1_registered", False))
        envelope.update({
            "installed": live,
            "schema": getattr(module, "SYNAPSE_SCHEMA", None),
            "packet_profile": getattr(module, "PACKET_PROFILE", None),
            "receipt_profile": getattr(module, "RECEIPT_PROFILE", None),
            "resource": getattr(module, "LIMINAL_RESOURCE", None),
            "standing": "SYNAPSE_ENVELOPE_ADAPTER_INSTALLED" if live else "SYNAPSE_ENVELOPE_SOURCE_ONLY_INSTALLER_HOLD",
        })

    federation = _source_probe("athena_mcp.federation_ephemeral_bridge")
    if federation.get("source_available"):
        surface = getattr(development, "federation_ephemeral_bridge", None)
        runtime = _bridge_runtime(surface)
        live = surface is not None and runtime is not None
        shared = live and fast_runtime is not None and runtime is fast_runtime
        federation.update({
            "installed": bool(live and shared),
            "runtime_present": live,
            "shared_fast_runtime_identity": shared,
            "standing": (
                "FEDERATION_EPHEMERAL_PROJECTION_INSTALLED_SHARED_RUNTIME"
                if live and shared
                else "FEDERATION_EPHEMERAL_RUNTIME_IDENTITY_HOLD" if live
                else "FEDERATION_EPHEMERAL_SOURCE_ONLY_INSTALLER_HOLD"
            ),
            "loss_class": "LOSSY_AUX",
            "source_currentness_proven": False,
        })

    durable_escalation = _source_probe("athena_mcp.ephemeral_durable_bridge")
    if durable_escalation.get("source_available"):
        surface = getattr(development, "ephemeral_durable_bridge", None)
        runtime = _bridge_runtime(surface)
        live = surface is not None and runtime is not None
        shared = live and fast_runtime is not None and runtime is fast_runtime
        durable_escalation.update({
            "installed": bool(live and shared),
            "runtime_present": live,
            "shared_fast_runtime_identity": shared,
            "standing": (
                "EPHEMERAL_DURABLE_ESCALATION_INSTALLED_SHARED_RUNTIME"
                if live and shared
                else "EPHEMERAL_DURABLE_RUNTIME_IDENTITY_HOLD" if live
                else "EPHEMERAL_DURABLE_SOURCE_ONLY_INSTALLER_HOLD"
            ),
            "auto_escalation": False,
        })

    planes = [
        {
            "plane_id": "MESSAGE_BOARD",
            "persistence": "GIT_DURABLE_SHARED_FRONTIER",
            "identity_namespace": "MESSAGE_BOARD_AGENT_ID",
            "active_count": int(metrics.get("durable_active") or 0),
            "authority": "PRESENCE_CLAIM_AND_MESSAGE_ROUTING_ONLY",
            "standing": synapse.get("durable_view_status") or "UNOBSERVED",
        },
        {
            "plane_id": "LIMINAL_BEACON",
            "persistence": "PROCESS_LOCAL_EPHEMERAL_TTL",
            "identity_namespace": "LIMINAL_AGENT_ID + INSTANCE_ID + SESSION_EPOCH",
            "active_count": int(metrics.get("liminal_active") or 0),
            "authority": "NON_AUTHORITATIVE_COORDINATION",
            "standing": "OBSERVED" if "liminal_active" in metrics else "UNOBSERVED",
        },
        {
            "plane_id": "EPHEMERAL_SQLITE",
            "persistence": "PROCESS_LOCAL_SQLITE_BOUNDED_TTL",
            "identity_namespace": "EPHEMERAL_AID + EPOCH",
            "active_count": int(fast.get("fresh_presence_count") or 0),
            "authority": "NONE",
            "standing": fast.get("standing"),
        },
        {
            "plane_id": "SYNAPSE_ENVELOPE",
            "persistence": "PROJECTION_ONLY_NATIVE_STORAGE_EXTERNAL",
            "identity_namespace": "ATHENA.SYNAPSE.ENVELOPE EVENT_ID",
            "authority": "NONE",
            "standing": envelope.get("standing"),
        },
        {
            "plane_id": "FEDERATION_SOURCE_CURSOR",
            "persistence": "EXTERNAL_SOURCE_PREFIX_SEMANTICS",
            "identity_namespace": "FEDERATION_HANDOFF_DIGEST + SOURCE_CURSOR_DIGEST",
            "authority": "EXTERNAL_NOT_MINTED_HERE",
            "standing": federation.get("standing"),
        },
    ]

    edges = [
        {
            "src": "LIMINAL_BEACON",
            "dst": "MESSAGE_BOARD",
            "mechanism": "athena_liminal_beacon_bridge MESSAGE_BOARD",
            "standing": "INSTALLED_EXPLICIT_BRIDGE",
            "loss": "SUMMARY/REF_COMPACTION",
            "authority": "MESSAGE_BOARD_EXISTING_WRITE_PATH_ONLY",
            "law": "BRIDGE_RETURN != CONSUMPTION_OR_PROPAGATION",
        },
        {
            "src": "LIMINAL_BEACON",
            "dst": "SYNAPSE_ENVELOPE",
            "mechanism": "athena_synapse_liminal_export_packet / export_receipt",
            "standing": "INSTALLED_EXPLICIT_PROJECTION" if envelope.get("installed") else "UNOBSERVED_OR_INSTALLER_HOLD",
            "loss": "PACKET=LOSSY_AUX; RECEIPT=LOSSLESS_RELATIVE_TO_EXPLICIT_RECEIPT",
            "authority": "NONE",
            "law": "EXPORT != DELIVERY",
        },
        {
            "src": "SYNAPSE_ENVELOPE",
            "dst": "LIMINAL_BEACON",
            "mechanism": "athena_synapse_liminal_ingest",
            "standing": "INSTALLED_EXPLICIT_INGRESS" if envelope.get("installed") else "UNOBSERVED_OR_INSTALLER_HOLD",
            "loss": "FOREIGN_CAUSAL_IDS_REMAIN_CAUSAL_REFS",
            "authority": "NONE",
            "law": "INGEST != SOURCE_EVENT_IDENTITY",
        },
        {
            "src": "FEDERATION_SOURCE_CURSOR",
            "dst": "EPHEMERAL_SQLITE",
            "mechanism": "athena_ephemeral_federation_post/poll",
            "standing": "INSTALLED_EXPLICIT_PROJECTION" if federation.get("installed") else "OPTIONAL_BRIDGE_UNOBSERVED_OR_INSTALLER_HOLD",
            "loss": "LOSSY_AUX",
            "authority": "NONE",
            "law": "MCP_PROCESS_CURSOR != FEDERATION_SOURCE_CURSOR",
        },
        {
            "src": "EPHEMERAL_SQLITE",
            "dst": "MESSAGE_BOARD",
            "mechanism": "athena_ephemeral_durable_escalate",
            "standing": "INSTALLED_EXPLICIT_ESCALATION" if durable_escalation.get("installed") else "DECLARED_MATERIAL_ESCALATION_RESIDUAL_OR_INSTALLER_HOLD",
            "loss": "REFERENCE_AND_TYPED_METADATA_ONLY",
            "authority": "MESSAGE_BOARD_EXISTING_WRITE_PATH_ONLY" if durable_escalation.get("installed") else "NONE",
            "law": "MATERIAL_CANDIDATE != DURABLE_CLAIM_OR_TRUTH",
        },
    ]

    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "OK",
        "planes": planes,
        "bridge_edges": edges,
        "fast_plane": fast,
        "optional_components": {
            "synapse_envelope": envelope,
            "federation_ephemeral": federation,
            "ephemeral_durable_escalation": durable_escalation,
        },
        "identity_join_policy": "NO_AUTOMATIC_CROSS_PLANE_IDENTITY_JOIN",
        "authority": "READ_ONLY_NAVIGATION_OBSERVER",
        "laws": list(LAWS),
    }


__all__ = [
    "VERSION",
    "ARTIFACT",
    "RESOURCE_URI",
    "LAWS",
    "build_plane_inventory",
]
