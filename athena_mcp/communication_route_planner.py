from __future__ import annotations

"""Deterministic read-only route planner over the communication-plane inventory."""

import hashlib
import json
from collections import deque
from typing import Any, Mapping

from .communication_plane_inventory import build_plane_inventory

VERSION = "ATHENA.COMMUNICATION.ROUTE.PLANNER.1"
ARTIFACT = "ATHENA.COMMUNICATION.ROUTE.PLAN.V1.CANDIDATE"
TOOL_NAME = "athena_synapse_route_plan"
RESOURCE_URI = "athena://synapse/routes"

PLANES = {
    "MESSAGE_BOARD",
    "LIMINAL_BEACON",
    "EPHEMERAL_SQLITE",
    "SYNAPSE_ENVELOPE",
    "FEDERATION_SOURCE_CURSOR",
}

EDGE_CONTRACTS: dict[tuple[str, str], dict[str, Any]] = {
    ("LIMINAL_BEACON", "MESSAGE_BOARD"): {
        "loss_class": "LOSSY_AUX",
        "loss_rank": 2,
        "preconditions": [
            "LIVE_LIMINAL_PACKET",
            "LIMINAL_SENDER_HAS_ACTIVE_MESSAGE_BOARD_PRESENCE",
            "FRESH_SHARED_MESSAGE_BOARD_FRONTIER",
        ],
        "return_semantics": "NO_AUTOMATIC_REVERSE_ROUTE",
    },
    ("LIMINAL_BEACON", "SYNAPSE_ENVELOPE"): {
        "loss_class": "PROFILE_DEPENDENT_PACKET_LOSSY_AUX_RECEIPT_LOSSLESS",
        "loss_rank": 1,
        "preconditions": ["LIVE_LIMINAL_PACKET_OR_RECEIPT", "EXPLICIT_SOURCE_REVISION"],
        "return_semantics": "ENVELOPE_CAN_BE_EXPLICITLY_INGESTED_AS_NEW_SIGNAL_NOT_IDENTITY",
    },
    ("SYNAPSE_ENVELOPE", "LIMINAL_BEACON"): {
        "loss_class": "LOSSY_AUX_NEW_NATIVE_SIGNAL",
        "loss_rank": 2,
        "preconditions": ["VALID_SYNAPSE_ENVELOPE", "TARGET_LIMINAL_AGENT_PRESENT"],
        "return_semantics": "INGESTED_PACKET_ID_DIFFERS_FROM_SOURCE_EVENT_ID",
    },
    ("FEDERATION_SOURCE_CURSOR", "EPHEMERAL_SQLITE"): {
        "loss_class": "LOSSY_AUX",
        "loss_rank": 2,
        "preconditions": [
            "FEDERATION_HANDOFF_DIGEST_AVAILABLE",
            "FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE",
            "EPHEMERAL_SENDER_PRESENT",
        ],
        "return_semantics": "TRANSPORT_REF_CAN_RECONSTRUCT_HANDOFF_AND_SOURCE_CURSOR_DIGESTS",
    },
    ("EPHEMERAL_SQLITE", "MESSAGE_BOARD"): {
        "loss_class": "LOSSY_AUX_REFERENCE_AND_TYPED_METADATA",
        "loss_rank": 2,
        "preconditions": [
            "MATERIAL_CANDIDATE",
            "EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF",
            "ACTIVE_MESSAGE_BOARD_ACTOR",
            "FRESH_SHARED_MESSAGE_BOARD_FRONTIER",
        ],
        "return_semantics": "DURABLE_EVENT_IDEMPOTENT_FOR_EXACT_ESCALATION_BASIS",
    },
}

LAWS = [
    "ROUTE_PLAN != EXECUTION",
    "INSTALLED_BRIDGE != SATISFIED_RUNTIME_PRECONDITIONS",
    "CALLER_DECLARED_PRECONDITION != VERIFIED_PRECONDITION",
    "SHORTEST_ROUTE != HIGHEST_TRUTH_OR_AUTHORITY",
    "LOSS_CLASS_COMPOSES_MONOTONICALLY_ACROSS_HOPS",
    "NO_REVERSE_PATH != SOURCE_NONRETURNABILITY_PROOF_BEYOND_INSTALLED_GRAPH",
    "PLANE_ID != IDENTITY_NAMESPACE",
]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _normalize(args: Mapping[str, Any]) -> dict[str, Any]:
    source = str(args.get("source_plane") or "").strip().upper()
    destination = str(args.get("destination_plane") or "").strip().upper()
    if source not in PLANES or destination not in PLANES:
        raise ValueError(f"source_plane and destination_plane must be one of {sorted(PLANES)}")
    try:
        max_hops = int(args.get("max_hops", 6))
    except (TypeError, ValueError):
        raise ValueError("max_hops must be an integer") from None
    if not 0 <= max_hops <= 8:
        raise ValueError("max_hops must be between 0 and 8")
    satisfied_raw = args.get("satisfied_preconditions") or []
    if not isinstance(satisfied_raw, (list, tuple)):
        raise ValueError("satisfied_preconditions must be an array")
    satisfied = sorted({str(value).strip().upper() for value in satisfied_raw if str(value).strip()})
    return {
        "source_plane": source,
        "destination_plane": destination,
        "max_hops": max_hops,
        "satisfied_preconditions": satisfied,
        "allow_lossy": bool(args.get("allow_lossy", True)),
    }


def _edge_contract(edge: Mapping[str, Any]) -> dict[str, Any]:
    key = (str(edge.get("src")), str(edge.get("dst")))
    contract = dict(EDGE_CONTRACTS.get(key) or {})
    contract.update({
        "src": key[0],
        "dst": key[1],
        "mechanism": edge.get("mechanism"),
        "standing": edge.get("standing"),
        "authority": edge.get("authority"),
        "inventory_loss": edge.get("loss"),
    })
    contract.setdefault("loss_class", "UNKNOWN")
    contract.setdefault("loss_rank", 9)
    contract.setdefault("preconditions", [])
    contract.setdefault("return_semantics", "UNKNOWN")
    contract["installed"] = str(edge.get("standing") or "").startswith("INSTALLED_")
    return contract


def _find_path(edges: list[dict[str, Any]], source: str, destination: str, max_hops: int, *, installed_only: bool, allow_lossy: bool) -> list[dict[str, Any]] | None:
    if source == destination:
        return []
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        if installed_only and not edge["installed"]:
            continue
        if not allow_lossy and edge["loss_class"] != "LOSSLESS":
            continue
        adjacency.setdefault(edge["src"], []).append(edge)
    for rows in adjacency.values():
        rows.sort(key=lambda row: (int(row["loss_rank"]), str(row["dst"]), str(row["mechanism"])))

    queue = deque([(source, [])])
    best_depth = {source: 0}
    candidates: list[list[dict[str, Any]]] = []
    best_hops: int | None = None
    while queue:
        node, path = queue.popleft()
        if best_hops is not None and len(path) >= best_hops:
            continue
        if len(path) >= max_hops:
            continue
        for edge in adjacency.get(node, []):
            if any(step["src"] == edge["dst"] for step in path):
                continue
            next_path = [*path, edge]
            if edge["dst"] == destination:
                best_hops = len(next_path) if best_hops is None else min(best_hops, len(next_path))
                candidates.append(next_path)
                continue
            depth = len(next_path)
            if depth <= best_depth.get(edge["dst"], max_hops + 1):
                best_depth[edge["dst"]] = depth
                queue.append((edge["dst"], next_path))
    if not candidates:
        return None
    candidates.sort(key=lambda path: (
        len(path),
        sum(int(step["loss_rank"]) for step in path),
        tuple(str(step["mechanism"]) for step in path),
    ))
    return candidates[0]


def _path_packet(path: list[dict[str, Any]]) -> dict[str, Any]:
    preconditions = sorted({condition for edge in path for condition in edge.get("preconditions") or []})
    loss_rank = sum(int(edge.get("loss_rank") or 0) for edge in path)
    return {
        "hop_count": len(path),
        "steps": [
            {
                "ordinal": index + 1,
                "src": edge["src"],
                "dst": edge["dst"],
                "mechanism": edge["mechanism"],
                "standing": edge["standing"],
                "loss_class": edge["loss_class"],
                "loss_rank": edge["loss_rank"],
                "preconditions": list(edge.get("preconditions") or []),
                "return_semantics": edge["return_semantics"],
                "authority": edge["authority"],
            }
            for index, edge in enumerate(path)
        ],
        "required_preconditions": preconditions,
        "composed_loss_rank": loss_rank,
        "loss_standing": "LOSSLESS" if path and loss_rank == 0 else ("IDENTITY_ROUTE" if not path else "LOSSY_COMPOSITION"),
    }


def plan_route(server: Any, args: Mapping[str, Any]) -> dict[str, Any]:
    norm = _normalize(args)
    inventory = build_plane_inventory(server, {}, limit=32)
    edges = [_edge_contract(edge) for edge in inventory.get("bridge_edges") or []]
    installed = _find_path(
        edges,
        norm["source_plane"],
        norm["destination_plane"],
        norm["max_hops"],
        installed_only=True,
        allow_lossy=norm["allow_lossy"],
    )
    potential = installed or _find_path(
        edges,
        norm["source_plane"],
        norm["destination_plane"],
        norm["max_hops"],
        installed_only=False,
        allow_lossy=norm["allow_lossy"],
    )

    basis = {
        "version": VERSION,
        "source_plane": norm["source_plane"],
        "destination_plane": norm["destination_plane"],
        "max_hops": norm["max_hops"],
        "allow_lossy": norm["allow_lossy"],
        "installed_path": [step["mechanism"] for step in (installed or [])] if installed is not None else None,
        "potential_path": [step["mechanism"] for step in (potential or [])] if potential is not None else None,
    }
    route_id = "CRP-" + _digest(basis).split(":", 1)[1][:32]

    if installed is None:
        candidate = _path_packet(potential) if potential is not None else None
        missing = []
        if potential is not None:
            missing = [
                {
                    "src": step["src"],
                    "dst": step["dst"],
                    "mechanism": step["mechanism"],
                    "standing": step["standing"],
                }
                for step in potential
                if not step["installed"]
            ]
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "SYNAPSE_ROUTE_BRIDGE_INSTALLATION_HOLD" if candidate else "SYNAPSE_ROUTE_NOT_FOUND_HOLD",
            "route_id": route_id,
            "source_plane": norm["source_plane"],
            "destination_plane": norm["destination_plane"],
            "candidate_route": candidate,
            "missing_bridges": missing,
            "execution_authority": False,
            "mutation": False,
            "laws": list(LAWS),
        }

    packet = _path_packet(installed)
    satisfied = set(norm["satisfied_preconditions"])
    missing_preconditions = sorted(set(packet["required_preconditions"]) - satisfied)
    reverse = _find_path(
        edges,
        norm["destination_plane"],
        norm["source_plane"],
        norm["max_hops"],
        installed_only=True,
        allow_lossy=True,
    )
    packet["declared_satisfied_preconditions"] = norm["satisfied_preconditions"]
    packet["missing_preconditions"] = missing_preconditions
    packet["preconditions_verified"] = False
    packet["precondition_standing"] = (
        "CALLER_DECLARED_COMPLETE_NOT_VERIFIED" if not missing_preconditions else "MISSING_DECLARED_PRECONDITIONS"
    )
    packet["roundtrip_route_installed"] = reverse is not None
    packet["roundtrip"] = _path_packet(reverse) if reverse is not None else None

    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": "SYNAPSE_ROUTE_STRUCTURALLY_AVAILABLE" if not missing_preconditions else "SYNAPSE_ROUTE_PRECONDITION_HOLD",
        "route_id": route_id,
        "source_plane": norm["source_plane"],
        "destination_plane": norm["destination_plane"],
        "route": packet,
        "execution_authority": False,
        "mutation": False,
        "route_digest": _digest(packet),
        "laws": list(LAWS),
    }


ROUTE_PLANNER_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Plan a deterministic read-only route across installed ATHENA communication planes. Returns ordered bridge "
        "tools, composed loss, missing bridge installations and unverified runtime preconditions. Planning never "
        "executes a bridge or promotes identity, evidence, consumption, or authority."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["source_plane", "destination_plane"],
        "properties": {
            "source_plane": {"type": "string", "enum": sorted(PLANES)},
            "destination_plane": {"type": "string", "enum": sorted(PLANES)},
            "max_hops": {"type": "integer", "minimum": 0, "maximum": 8},
            "allow_lossy": {"type": "boolean"},
            "satisfied_preconditions": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "uniqueItems": True,
            },
        },
        "additionalProperties": False,
    },
}

ROUTE_PLANNER_RESOURCE = {
    "uri": RESOURCE_URI,
    "name": "ATHENA Communication Route Planner V1",
    "mimeType": "application/json",
}


__all__ = [
    "VERSION",
    "ARTIFACT",
    "TOOL_NAME",
    "RESOURCE_URI",
    "PLANES",
    "EDGE_CONTRACTS",
    "LAWS",
    "plan_route",
    "ROUTE_PLANNER_TOOL",
    "ROUTE_PLANNER_RESOURCE",
]
