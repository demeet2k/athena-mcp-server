from __future__ import annotations

"""Read-only cross-plane observer for ATHENA communication metabolism.

The observer joins durable Message Board coordination with process-local Liminal
Beacon presence without flattening their semantics.  It exists to reveal gaps,
not to turn absence in one plane into evidence about the other.
"""

from typing import Any

from .liminal_beacon_mesh import LiminalBeaconMeshRuntime
from .message_board import MessageBoardRuntime

VERSION = "ATHENA.SYNAPSE.OBSERVER.1"
ARTIFACT = "ATHENA.SYNAPSE.OBSERVER.V1.CANDIDATE"
TOOL_NAME = "athena_synapse_observe"

LAWS = [
    "SYNAPSE_OBSERVER != CLAIM_OR_ASSIGNMENT_AUTHORITY",
    "BOARD_CLAIM != LIMINAL_PRESENCE",
    "AGENT_ID_MATCH != PROCESS_INSTANCE_IDENTITY",
    "MISSING_LIMINAL_PRESENCE != PROCESS_ABSENCE",
    "MISSING_DURABLE_CLAIM != WORK_ABSENCE",
    "ROUTE_OVERLAP != COMMUNICATION_SUCCESS",
    "SHARED_FRONTIER_UNVERIFIED => DURABLE_VIEW_QUALIFIED",
]

_ROUTE_FIELDS = (
    "work_refs",
    "object_refs",
    "dependency_refs",
    "causal_refs",
    "semantic_tags",
    "kc_refs",
    "party_refs",
    "capabilities",
    "needs",
    "offers",
    "provides",
)


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _liminal_route_atoms(row: dict[str, Any]) -> set[str]:
    atoms: set[str] = set()
    for field in _ROUTE_FIELDS:
        for value in row.get(field) or []:
            atom = _norm(value)
            if atom:
                atoms.add(f"{field}:{atom}")
    return atoms


def _liminal_edges(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    ordered = sorted(rows, key=lambda row: str(row.get("agent_id") or ""))
    for index, left in enumerate(ordered):
        left_atoms = _liminal_route_atoms(left)
        if not left_atoms:
            continue
        for right in ordered[index + 1 :]:
            shared = sorted(left_atoms & _liminal_route_atoms(right))
            if not shared:
                continue
            edges.append(
                {
                    "agents": [left.get("agent_id"), right.get("agent_id")],
                    "shared_route_atoms": shared[:32],
                    "shared_route_atom_count": len(shared),
                    "standing": "TOPOLOGICAL_RENDEZVOUS_POTENTIAL_ONLY",
                }
            )
    return edges


def build_synapse_map(
    board: dict[str, Any],
    liminal: dict[str, Any],
    *,
    agent_id: str | None = None,
) -> dict[str, Any]:
    durable_rows = list(board.get("active") or [])
    liminal_rows = list(liminal.get("active_presence") or [])
    durable = {str(row.get("agent_id")): row for row in durable_rows if row.get("agent_id")}
    ephemeral = {str(row.get("agent_id")): row for row in liminal_rows if row.get("agent_id")}
    all_ids = sorted(set(durable) | set(ephemeral))

    agents: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for aid in all_ids:
        board_row = durable.get(aid)
        liminal_row = ephemeral.get(aid)
        if board_row and liminal_row:
            standing = "CROSS_PLANE_VISIBLE"
        elif liminal_row:
            standing = "LIMINAL_ONLY"
            gaps.append(
                {
                    "agent_id": aid,
                    "kind": "EPHEMERAL_ONLY_NO_DURABLE_CLAIM",
                    "evidence": "OBSERVED_LIMINAL_PRESENCE_ONLY",
                    "interpretation": "does not prove unclaimed work; presence and claim have different semantics",
                }
            )
        else:
            standing = "DURABLE_ONLY"
            gaps.append(
                {
                    "agent_id": aid,
                    "kind": "DURABLE_CLAIM_NO_OBSERVED_LIMINAL_PRESENCE",
                    "evidence": "OBSERVED_DURABLE_CLAIM_ONLY",
                    "interpretation": "liminal process presence is unobserved, not proven absent",
                }
            )

        agents.append(
            {
                "agent_id": aid,
                "standing": standing,
                "durable": None
                if board_row is None
                else {
                    "claim_id": board_row.get("claim_id"),
                    "mode": board_row.get("mode"),
                    "task": board_row.get("task"),
                    "work_key": board_row.get("work_key"),
                    "targets": list(board_row.get("targets") or []),
                    "expires_at": board_row.get("expires_at"),
                },
                "liminal": None
                if liminal_row is None
                else {
                    "instance_id": liminal_row.get("instance_id"),
                    "session_epoch": liminal_row.get("session_epoch"),
                    "activity": liminal_row.get("activity"),
                    "focus": liminal_row.get("focus"),
                    "last_seen": liminal_row.get("last_seen"),
                    "expires_at": liminal_row.get("expires_at"),
                    "work_refs": list(liminal_row.get("work_refs") or []),
                    "object_refs": list(liminal_row.get("object_refs") or []),
                    "kc_refs": list(liminal_row.get("kc_refs") or []),
                    "party_refs": list(liminal_row.get("party_refs") or []),
                    "capabilities": list(liminal_row.get("capabilities") or []),
                    "needs": list(liminal_row.get("needs") or []),
                    "offers": list(liminal_row.get("offers") or []),
                },
                "identity_join": "AGENT_ID_ONLY_NOT_PROCESS_IDENTITY" if board_row and liminal_row else None,
            }
        )

    selected_unread = []
    if agent_id:
        selected_unread = list(board.get("unread_messages") or [])

    bridge_state = liminal.get("synapse_return") if isinstance(liminal.get("synapse_return"), dict) else {}
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "OK" if str(board.get("status") or "").startswith("OK") else "QUALIFIED",
        "shared_frontier_verified": bool(board.get("shared_frontier_verified")),
        "durable_view_status": board.get("status"),
        "agents": agents,
        "observability_gaps": gaps,
        "durable_exact_overlap_edges": list(board.get("exact_overlaps") or []),
        "durable_potential_overlap_edges": list(board.get("potential_overlaps") or []),
        "liminal_topology_edges": _liminal_edges(liminal_rows),
        "selected_agent_id": agent_id,
        "selected_unread_messages": selected_unread,
        "synapse_return": {
            "bridge_receipt_count": int(bridge_state.get("bridge_receipt_count") or 0),
            "cross_restart_deduplication": bridge_state.get("cross_restart_deduplication"),
        },
        "metrics": {
            "durable_active": len(durable),
            "liminal_active": len(ephemeral),
            "cross_plane_visible": sum(1 for aid in all_ids if aid in durable and aid in ephemeral),
            "liminal_only": sum(1 for aid in all_ids if aid not in durable and aid in ephemeral),
            "durable_only": sum(1 for aid in all_ids if aid in durable and aid not in ephemeral),
            "selected_unread": len(selected_unread),
        },
        "laws": list(LAWS),
    }


class SynapseObserverRuntime:
    def __init__(self, server: Any):
        self.server = server

    def _liminal(self) -> LiminalBeaconMeshRuntime:
        runtime = getattr(self.server, "_liminal_beacon_mesh_runtime_v1", None)
        if runtime is None:
            runtime = LiminalBeaconMeshRuntime(self.server)
            self.server._liminal_beacon_mesh_runtime_v1 = runtime
        return runtime

    def observe(
        self,
        *,
        agent_id: str | None = None,
        remote: str = "origin",
        shared_remote_mode: str = "BEST_EFFORT",
        limit: int = 100,
    ) -> dict[str, Any]:
        git = getattr(self.server, "git", None)
        if git is None or not getattr(git, "enabled", False):
            raise ValueError("ATHENA_GIT_ROOT is required for synapse observation")
        board = MessageBoardRuntime(git).read(
            agent_id=agent_id,
            limit=max(1, min(int(limit or 100), 500)),
            include_stale=False,
            remote=remote,
            shared_remote_mode=shared_remote_mode,
        )
        liminal = self._liminal().state(
            agent_id=None,
            include_packets=False,
            limit=max(1, min(int(limit or 100), 200)),
        )
        return build_synapse_map(board, liminal, agent_id=agent_id)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name != TOOL_NAME:
            raise KeyError(name)
        return self.observe(**arguments)


SYNAPSE_OBSERVER_TOOLS = [
    {
        "name": TOOL_NAME,
        "description": (
            "Read-only cross-plane synapse observer joining durable Message Board claims/messages with process-local "
            "Liminal Beacon presence. Reports observability gaps and topology without treating absence, routing, or "
            "agent-id equality as process identity, execution authority, or truth."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": ["string", "null"], "maxLength": 128},
                "remote": {"type": "string"},
                "shared_remote_mode": {
                    "type": "string",
                    "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "additionalProperties": False,
        },
    }
]
SYNAPSE_OBSERVER_TOOL_NAMES = {TOOL_NAME}


def install_synapse_observer() -> None:
    from . import protocol
    from .server import Server

    if getattr(Server, "_athena_synapse_observer_v1_registered", False):
        return

    existing = {tool["name"] for tool in protocol.TOOLS}
    for tool in SYNAPSE_OBSERVER_TOOLS:
        if tool["name"] not in existing:
            protocol.TOOLS.append(tool)
            existing.add(tool["name"])

    previous_call = Server.call_tool

    def call_with_synapse_observer(self, name, arguments):
        if name in SYNAPSE_OBSERVER_TOOL_NAMES:
            runtime = getattr(self, "_synapse_observer_runtime_v1", None)
            if runtime is None:
                runtime = SynapseObserverRuntime(self)
                self._synapse_observer_runtime_v1 = runtime
            return runtime.call_tool(name, arguments)
        return previous_call(self, name, arguments)

    Server.call_tool = call_with_synapse_observer
    Server._athena_synapse_observer_v1_registered = True


__all__ = [
    "VERSION",
    "ARTIFACT",
    "TOOL_NAME",
    "LAWS",
    "build_synapse_map",
    "SynapseObserverRuntime",
    "SYNAPSE_OBSERVER_TOOLS",
    "SYNAPSE_OBSERVER_TOOL_NAMES",
    "install_synapse_observer",
]
