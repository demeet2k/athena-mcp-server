from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from .liminal_beacon_mesh import LiminalBeaconMeshRuntime, _packet_capsule
from .synapse_liminal_adapter import (
    liminal_capsule_to_synapse,
    liminal_receipt_to_synapse,
    synapse_to_liminal_ingress_plan,
)
from .synapse_liminal_protocol import SYNAPSE_LIMINAL_TOOLS, SYNAPSE_LIMINAL_TOOL_NAMES


def _observed_at() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_revision(arguments: dict[str, Any]) -> str:
    value = str(arguments.get("source_revision") or os.getenv("ATHENA_MCP_SOURCE_REVISION") or "").strip()
    if not value:
        raise ValueError(
            "SYNAPSE_SOURCE_REVISION_REQUIRED_HOLD: pass source_revision or set ATHENA_MCP_SOURCE_REVISION"
        )
    return value


def _liminal(server: Any) -> LiminalBeaconMeshRuntime:
    runtime = getattr(server, "_liminal_beacon_mesh_runtime_v1", None)
    if runtime is None:
        runtime = LiminalBeaconMeshRuntime(server)
        server._liminal_beacon_mesh_runtime_v1 = runtime
    return runtime


def _read_packet_capsule(runtime: LiminalBeaconMeshRuntime, packet_id: str) -> dict[str, Any]:
    """Read one current public capsule without pruning or mutating the mesh."""
    packet_id = str(packet_id or "").strip()
    with runtime._lock:
        row = runtime._packets.get(packet_id)
        if not row:
            raise ValueError("LIMINAL_PACKET_NOT_FOUND_HOLD")
        return _packet_capsule(row)


def _read_receipt_record(runtime: LiminalBeaconMeshRuntime, agent_id: str, packet_id: str) -> dict[str, Any]:
    """Read one explicit native receipt record without advancing its stage."""
    key = (str(agent_id or "").strip(), str(packet_id or "").strip())
    with runtime._lock:
        row = runtime._receipts.get(key)
        if not row:
            raise ValueError("LIMINAL_RECEIPT_NOT_FOUND_HOLD")
        return dict(row)


class SynapseLiminalRuntime:
    def __init__(self, server: Any):
        self.server = server

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in SYNAPSE_LIMINAL_TOOL_NAMES:
            raise KeyError(name)
        runtime = _liminal(self.server)

        if name == "athena_synapse_liminal_export_packet":
            source_revision = _source_revision(arguments)
            capsule = _read_packet_capsule(runtime, str(arguments["packet_id"]))
            envelope = liminal_capsule_to_synapse(
                capsule,
                source_revision=source_revision,
                bridge_observed_at=_observed_at(),
            )
            return {
                "status": "SYNAPSE_PACKET_EXPORTED",
                "envelope": envelope,
                "standing": "PUBLIC_CAPSULE_PROJECTION_LOSSY_AUX",
                "law": "EXPORT != DELIVERY != CONSUMPTION",
            }

        if name == "athena_synapse_liminal_export_receipt":
            source_revision = _source_revision(arguments)
            receipt = _read_receipt_record(
                runtime,
                str(arguments["agent_id"]),
                str(arguments["packet_id"]),
            )
            envelope = liminal_receipt_to_synapse(
                receipt,
                source_revision=source_revision,
                bridge_observed_at=_observed_at(),
            )
            return {
                "status": "SYNAPSE_RECEIPT_EXPORTED",
                "envelope": envelope,
                "standing": "EXPLICIT_NATIVE_RECEIPT_STAGE_ONLY",
                "law": "RECEIPT_STAGE != OUTCOME_IMPROVEMENT",
            }

        if name == "athena_synapse_liminal_plan_ingress":
            return synapse_to_liminal_ingress_plan(
                arguments["envelope"],
                agent_id=str(arguments["agent_id"]),
            )

        if name == "athena_synapse_liminal_ingest":
            plan = synapse_to_liminal_ingress_plan(
                arguments["envelope"],
                agent_id=str(arguments["agent_id"]),
            )
            emitted = runtime.emit(**plan["emit_args"])
            return {
                "status": "SYNAPSE_INGESTED_TO_LIMINAL",
                "source_event_id": plan["source_event_id"],
                "emitted": emitted,
                "residuals": plan["residuals"],
                "standing": "NEW_EPHEMERAL_COORDINATION_SIGNAL_ONLY",
                "laws": [
                    "INGEST != SOURCE_EVENT_IDENTITY",
                    "INGEST != CONSUMPTION",
                    "INGEST != EXECUTION_AUTHORITY",
                ],
            }

        raise KeyError(name)


def install_synapse_liminal_extension() -> None:
    from . import protocol
    from .server import Server

    if getattr(Server, "_athena_synapse_liminal_v1_registered", False):
        return

    existing = {tool["name"] for tool in protocol.TOOLS}
    for tool in SYNAPSE_LIMINAL_TOOLS:
        if tool["name"] not in existing:
            protocol.TOOLS.append(tool)
            existing.add(tool["name"])

    previous_call = Server.call_tool

    def server_call_with_synapse_liminal(self, name, arguments):
        if name in SYNAPSE_LIMINAL_TOOL_NAMES:
            runtime = getattr(self, "_synapse_liminal_runtime_v1", None)
            if runtime is None:
                runtime = SynapseLiminalRuntime(self)
                self._synapse_liminal_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)

    Server.call_tool = server_call_with_synapse_liminal
    Server._athena_synapse_liminal_v1_registered = True


__all__ = ["SynapseLiminalRuntime", "install_synapse_liminal_extension"]
