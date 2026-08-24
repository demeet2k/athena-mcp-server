from __future__ import annotations

"""Concrete precondition verifier for planned ATHENA communication routes.

The route planner answers structural reachability. This verifier evaluates the
planner's declared preconditions against current runtime state without executing
any communication bridge. Some preconditions are inherently explicit caller
inputs (for example source_revision or an opaque actor binding reference); those
are recorded as DECLARED_REQUIRED, never upgraded to external truth.

Optional shared-frontier verification performs `git fetch` only through
PromptRemoteSync.status(fetch=True). It never fast-forwards or merges the working
branch. The local HEAD before/after the observation must remain identical.
"""

import hashlib
import json
import re
from typing import Any, Callable, Mapping

from .communication_route_planner import PLANES, plan_route
from .federation_ephemeral_bridge import decode_handoff_ref
from .message_board import MessageBoardRuntime
from .prompt_remote import PromptRemoteSync

VERSION = "ATHENA.COMMUNICATION.ROUTE.READINESS.1"
ARTIFACT = "ATHENA.COMMUNICATION.ROUTE.READINESS.V1.CANDIDATE"
TOOL_NAME = "athena_synapse_route_readiness"
RESOURCE_URI = "athena://synapse/readiness"

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_PASS = {"OBSERVED_PASS", "DECLARED_REQUIRED_PASS"}

LAWS = [
    "ROUTE_READINESS != ROUTE_EXECUTION",
    "OBSERVED_PRECONDITION != EXECUTION_AUTHORITY",
    "DECLARED_REQUIRED_PASS != EXTERNAL_TRUTH",
    "FRESH_REMOTE_CHECK_FETCHES_REFS_ONLY_AND_MUST_NOT_MOVE_LOCAL_HEAD",
    "LOCAL_TRACKING_REF_WITHOUT_FRESH_FETCH != SHARED_FRONTIER_WITNESS",
    "PACKET_IDENTITY_IS_PLANE_LOCAL_UNLESS_EXPLICIT_PROJECTION_BINDS_IT",
    "READINESS_HOLD_NARROWS_EXECUTABILITY_NOT_WORLD_TRUTH",
]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _result(condition: str, status: str, evidence: Any = None, *, note: str | None = None) -> dict[str, Any]:
    return {
        "condition": condition,
        "status": status,
        "satisfied": status in _PASS,
        "evidence": evidence,
        "note": note,
    }


def _liminal_runtime(server: Any):
    return getattr(server, "_liminal_beacon_mesh_runtime_v1", None)


def _fast_runtime(server: Any):
    development = getattr(server, "aor_development", None)
    surface = getattr(development, "ephemeral_coordination", None)
    return getattr(surface, "runtime", None)


def _liminal_packet(server: Any, packet_id: str | None) -> dict[str, Any] | None:
    runtime = _liminal_runtime(server)
    if runtime is None or not packet_id:
        return None
    with runtime._lock:
        packet = runtime._packets.get(packet_id)
        if not packet:
            return None
        now = float(runtime._now())
        expires = float(packet.get("expires_at") or 0.0)
        return dict(packet) if expires > now else None


def _liminal_receipt_exists(server: Any, packet_id: str | None, agent_id: str | None) -> bool:
    runtime = _liminal_runtime(server)
    if runtime is None or not packet_id:
        return False
    with runtime._lock:
        if agent_id:
            return (agent_id, packet_id) in runtime._receipts
        return any(key[1] == packet_id for key in runtime._receipts)


def _liminal_agent_active(server: Any, agent_id: str | None) -> dict[str, Any] | None:
    runtime = _liminal_runtime(server)
    if runtime is None or not agent_id:
        return None
    with runtime._lock:
        row = runtime._presence.get(agent_id)
        if not row:
            return None
        if str(row.get("liveness")) != "ACTIVE":
            return None
        if float(row.get("expires_at") or 0.0) <= float(runtime._now()):
            return None
        return {key: value for key, value in row.items() if not str(key).startswith("_")}


def _fast_presence(server: Any, aid: str | None) -> dict[str, Any] | None:
    runtime = _fast_runtime(server)
    if runtime is None or not aid:
        return None
    now = float(runtime._now())
    with runtime._lock:
        row = runtime.db.execute(
            "SELECT aid,presence_id,epoch,expires_at,cursor FROM ephemeral_presence WHERE aid=? AND expires_at>?",
            (aid, now),
        ).fetchone()
        return dict(row) if row else None


def _fast_packet(server: Any, packet_id: str | None) -> dict[str, Any] | None:
    runtime = _fast_runtime(server)
    if runtime is None or not packet_id:
        return None
    now = float(runtime._now())
    with runtime._lock:
        row = runtime.db.execute(
            "SELECT * FROM ephemeral_packets WHERE packet_id=? AND expires_at>?",
            (packet_id, now),
        ).fetchone()
        if not row:
            return None
        value = dict(row)
        value.pop("causal_parents_json", None)
        return value


def _local_board_active(server: Any) -> dict[str, dict[str, Any]]:
    git = getattr(server, "git", None)
    if git is None or not getattr(git, "enabled", False):
        return {}
    board = MessageBoardRuntime(git)
    return {str(row.get("agent_id")): row for row in board._active()}


def _frontier_observation(server: Any, remote: str, fresh: bool) -> dict[str, Any]:
    git = getattr(server, "git", None)
    if git is None or not getattr(git, "enabled", False):
        return {
            "status": "GIT_UNAVAILABLE",
            "shared_frontier_verified": False,
            "fresh_fetch_performed": False,
        }
    sync = PromptRemoteSync(git)
    before = git.head()
    try:
        state = sync.status(remote=remote, fetch=bool(fresh))
    except Exception as exc:
        return {
            "status": "REMOTE_FRONTIER_OBSERVATION_HOLD",
            "error": f"{type(exc).__name__}: {exc}",
            "local_head_before": before,
            "local_head_after": git.head(),
            "shared_frontier_verified": False,
            "fresh_fetch_performed": bool(fresh),
        }
    after = git.head()
    value = dict(state)
    value.update({
        "local_head_before": before,
        "local_head_after": after,
        "local_head_unchanged": before == after,
        "fresh_fetch_performed": bool(fresh),
    })
    if before != after:
        value["shared_frontier_verified"] = False
        value["status"] = "READINESS_LOCAL_HEAD_MOVED_HOLD"
    return value


def _packet_projection(packet: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not packet:
        return None
    raw = packet.get("packet_digest_or_ref")
    try:
        projection = decode_handoff_ref(str(raw or ""))
    except (TypeError, ValueError):
        return None
    return {
        "handoff_digest": projection.handoff_digest,
        "source_cursor_digest": projection.source_cursor_digest,
        "transport_ref": projection.transport_ref,
        "loss_class": projection.loss_class,
        "reconstruction_token": projection.reconstruction_token,
    }


def _valid_digest(value: Any) -> str | None:
    text = _text(value)
    return text if text and _DIGEST.fullmatch(text) else None


def _validate_synapse_envelope(envelope: Any, target_agent: str | None) -> tuple[bool, Any]:
    if not isinstance(envelope, Mapping):
        return False, "synapse_envelope object required"
    if not target_agent:
        return False, "target_liminal_agent_id required"
    try:
        from .synapse_liminal_adapter import synapse_to_liminal_ingress_plan

        plan = synapse_to_liminal_ingress_plan(envelope, agent_id=target_agent)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    return True, {
        "message_class": plan.get("message_class"),
        "source_event_id": envelope.get("event_id"),
        "law": "VALIDATION_PLAN != INGEST_EXECUTION",
    }


def verify_route_readiness(server: Any, args: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(args, Mapping):
        raise ValueError("arguments must be an object")
    source = str(args.get("source_plane") or "").strip().upper()
    destination = str(args.get("destination_plane") or "").strip().upper()
    if source not in PLANES or destination not in PLANES:
        raise ValueError(f"source_plane and destination_plane must be one of {sorted(PLANES)}")

    route = plan_route(server, {
        "source_plane": source,
        "destination_plane": destination,
        "max_hops": args.get("max_hops", 6),
        "allow_lossy": args.get("allow_lossy", True),
    })
    if route.get("route") is None:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "status": "ROUTE_READINESS_STRUCTURAL_HOLD",
            "route_plan": route,
            "readiness": [],
            "ready": False,
            "execution_authority": False,
            "bridge_execution_performed": False,
            "laws": list(LAWS),
        }

    context = {
        "packet_id": _text(args.get("packet_id")),
        "liminal_receipt_agent_id": _text(args.get("liminal_receipt_agent_id")),
        "target_liminal_agent_id": _text(args.get("target_liminal_agent_id")),
        "ephemeral_actor_aid": _text(args.get("ephemeral_actor_aid")),
        "board_agent_id": _text(args.get("board_agent_id")),
        "source_revision": _text(args.get("source_revision")),
        "actor_binding_ref": _text(args.get("actor_binding_ref")),
        "delivery_class": _text(args.get("delivery_class")),
        "handoff_digest": _text(args.get("handoff_digest")),
        "source_cursor_digest": _text(args.get("source_cursor_digest")),
        "synapse_envelope": args.get("synapse_envelope"),
        "remote": _text(args.get("remote")) or "origin",
        "fresh_remote_check": bool(args.get("fresh_remote_check", False)),
    }

    liminal_packet = _liminal_packet(server, context["packet_id"])
    fast_packet = _fast_packet(server, context["packet_id"])
    fast_projection = _packet_projection(fast_packet)
    board_active = _local_board_active(server)
    frontier: dict[str, Any] | None = None

    def eval_condition(condition: str) -> dict[str, Any]:
        nonlocal frontier
        if condition == "LIVE_LIMINAL_PACKET":
            return _result(condition, "OBSERVED_PASS" if liminal_packet else "OBSERVED_HOLD", {
                "packet_id": context["packet_id"],
                "sender_id": liminal_packet.get("sender_id") if liminal_packet else None,
            })
        if condition == "LIVE_LIMINAL_PACKET_OR_RECEIPT":
            receipt = _liminal_receipt_exists(server, context["packet_id"], context["liminal_receipt_agent_id"])
            return _result(condition, "OBSERVED_PASS" if (liminal_packet or receipt) else "OBSERVED_HOLD", {
                "packet_live": bool(liminal_packet),
                "receipt_observed": bool(receipt),
            })
        if condition == "LIMINAL_SENDER_HAS_ACTIVE_MESSAGE_BOARD_PRESENCE":
            sender = str((liminal_packet or {}).get("sender_id") or "")
            row = board_active.get(sender) if sender else None
            return _result(condition, "OBSERVED_PASS" if row else "OBSERVED_HOLD", {
                "liminal_sender_id": sender or None,
                "board_claim_id": row.get("claim_id") if row else None,
                "local_board_view_only": True,
            })
        if condition == "EXPLICIT_SOURCE_REVISION":
            return _result(
                condition,
                "DECLARED_REQUIRED_PASS" if context["source_revision"] else "OBSERVED_HOLD",
                {"source_revision": context["source_revision"]},
                note="explicit source revision is a required caller coordinate, not independently re-derived here",
            )
        if condition == "VALID_SYNAPSE_ENVELOPE":
            ok, evidence = _validate_synapse_envelope(context["synapse_envelope"], context["target_liminal_agent_id"])
            return _result(condition, "OBSERVED_PASS" if ok else "OBSERVED_HOLD", evidence)
        if condition == "TARGET_LIMINAL_AGENT_PRESENT":
            row = _liminal_agent_active(server, context["target_liminal_agent_id"])
            return _result(condition, "OBSERVED_PASS" if row else "OBSERVED_HOLD", {
                "agent_id": context["target_liminal_agent_id"],
                "session_epoch": row.get("session_epoch") if row else None,
                "instance_id": row.get("instance_id") if row else None,
            })
        if condition == "FEDERATION_HANDOFF_DIGEST_AVAILABLE":
            observed = (fast_projection or {}).get("handoff_digest")
            declared = _valid_digest(context["handoff_digest"])
            if observed:
                matches = declared in (None, observed)
                return _result(condition, "OBSERVED_PASS" if matches else "OBSERVED_HOLD", {
                    "observed": observed,
                    "declared": declared,
                    "matches": matches,
                })
            return _result(condition, "DECLARED_REQUIRED_PASS" if declared else "OBSERVED_HOLD", {
                "declared": declared,
                "runtime_projection_observed": False,
            })
        if condition == "FEDERATION_SOURCE_CURSOR_DIGEST_AVAILABLE":
            observed = (fast_projection or {}).get("source_cursor_digest")
            declared = _valid_digest(context["source_cursor_digest"])
            if observed:
                matches = declared in (None, observed)
                return _result(condition, "OBSERVED_PASS" if matches else "OBSERVED_HOLD", {
                    "observed": observed,
                    "declared": declared,
                    "matches": matches,
                })
            return _result(condition, "DECLARED_REQUIRED_PASS" if declared else "OBSERVED_HOLD", {
                "declared": declared,
                "runtime_projection_observed": False,
            })
        if condition == "EPHEMERAL_SENDER_PRESENT":
            row = _fast_presence(server, context["ephemeral_actor_aid"])
            return _result(condition, "OBSERVED_PASS" if row else "OBSERVED_HOLD", row)
        if condition == "MATERIAL_CANDIDATE":
            if fast_packet:
                actual = str(fast_packet.get("delivery_class") or "")
                return _result(condition, "OBSERVED_PASS" if actual == "MATERIAL_CANDIDATE" else "OBSERVED_HOLD", {
                    "packet_id": context["packet_id"],
                    "observed_delivery_class": actual,
                })
            declared = str(context["delivery_class"] or "").upper()
            return _result(condition, "DECLARED_REQUIRED_PASS" if declared == "MATERIAL_CANDIDATE" else "OBSERVED_HOLD", {
                "declared_delivery_class": declared or None,
                "runtime_packet_observed": False,
            })
        if condition == "EXPLICIT_EPHEMERAL_ACTOR_BINDING_REF":
            return _result(
                condition,
                "DECLARED_REQUIRED_PASS" if context["actor_binding_ref"] else "OBSERVED_HOLD",
                {"actor_binding_ref": context["actor_binding_ref"]},
                note="opaque binding reference presence is checked; identity equivalence is not proven",
            )
        if condition == "ACTIVE_MESSAGE_BOARD_ACTOR":
            row = board_active.get(context["board_agent_id"] or "")
            return _result(condition, "OBSERVED_PASS" if row else "OBSERVED_HOLD", {
                "board_agent_id": context["board_agent_id"],
                "claim_id": row.get("claim_id") if row else None,
                "local_board_view_only": True,
            })
        if condition == "FRESH_SHARED_MESSAGE_BOARD_FRONTIER":
            if frontier is None:
                frontier = _frontier_observation(server, context["remote"], context["fresh_remote_check"])
            if not context["fresh_remote_check"]:
                return _result(condition, "UNKNOWN", frontier, note="fresh_remote_check=false; stale tracking ref is not promoted")
            ok = bool(frontier.get("shared_frontier_verified")) and bool(frontier.get("local_head_unchanged"))
            return _result(condition, "OBSERVED_PASS" if ok else "OBSERVED_HOLD", frontier)
        return _result(condition, "UNKNOWN", None, note="no readiness evaluator registered for this precondition")

    required = list(route["route"].get("required_preconditions") or [])
    readiness = [eval_condition(condition) for condition in required]
    holds = [row for row in readiness if row["status"] == "OBSERVED_HOLD"]
    unknown = [row for row in readiness if row["status"] == "UNKNOWN"]
    declared = [row for row in readiness if row["status"] == "DECLARED_REQUIRED_PASS"]
    observed = [row for row in readiness if row["status"] == "OBSERVED_PASS"]
    ready = not holds and not unknown and len(readiness) == len(observed) + len(declared)

    basis = {
        "route_id": route.get("route_id"),
        "route_digest": route.get("route_digest"),
        "conditions": [{"condition": row["condition"], "status": row["status"]} for row in readiness],
        "packet_id": context["packet_id"],
        "target_liminal_agent_id": context["target_liminal_agent_id"],
        "ephemeral_actor_aid": context["ephemeral_actor_aid"],
        "board_agent_id": context["board_agent_id"],
    }
    readiness_id = "CRR-" + _digest(basis).split(":", 1)[1][:32]
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": (
            "ROUTE_READINESS_READY_OBSERVED_WITH_DECLARED_COORDINATES"
            if ready and declared
            else "ROUTE_READINESS_READY_OBSERVED"
            if ready
            else "ROUTE_READINESS_HOLD"
        ),
        "readiness_id": readiness_id,
        "route_plan": route,
        "readiness": readiness,
        "summary": {
            "required": len(readiness),
            "observed_pass": len(observed),
            "declared_required_pass": len(declared),
            "holds": len(holds),
            "unknown": len(unknown),
        },
        "ready": ready,
        "frontier_observation": frontier,
        "execution_authority": False,
        "bridge_execution_performed": False,
        "semantic_mutation_performed": False,
        "housekeeping": "optional git fetch updates remote-tracking refs only; no fast-forward/merge; no TTL GC invoked",
        "readiness_digest": _digest(basis),
        "laws": list(LAWS),
    }


READINESS_TOOL = {
    "name": TOOL_NAME,
    "description": (
        "Verify concrete runtime preconditions for an installed ATHENA communication route without executing any "
        "bridge. Distinguishes observed passes, required caller coordinates, holds and unknowns. Optional fresh "
        "remote checking performs git fetch only and refuses to move local HEAD."
    ),
    "inputSchema": {
        "type": "object",
        "required": ["source_plane", "destination_plane"],
        "properties": {
            "source_plane": {"type": "string", "enum": sorted(PLANES)},
            "destination_plane": {"type": "string", "enum": sorted(PLANES)},
            "max_hops": {"type": "integer", "minimum": 0, "maximum": 8},
            "allow_lossy": {"type": "boolean"},
            "packet_id": {"type": ["string", "null"], "maxLength": 256},
            "liminal_receipt_agent_id": {"type": ["string", "null"], "maxLength": 128},
            "target_liminal_agent_id": {"type": ["string", "null"], "maxLength": 128},
            "ephemeral_actor_aid": {"type": ["string", "null"], "maxLength": 256},
            "board_agent_id": {"type": ["string", "null"], "maxLength": 128},
            "source_revision": {"type": ["string", "null"], "maxLength": 256},
            "actor_binding_ref": {"type": ["string", "null"], "maxLength": 2048},
            "delivery_class": {"type": ["string", "null"], "maxLength": 64},
            "handoff_digest": {"type": ["string", "null"], "maxLength": 71},
            "source_cursor_digest": {"type": ["string", "null"], "maxLength": 71},
            "synapse_envelope": {"type": ["object", "null"]},
            "remote": {"type": "string", "maxLength": 256},
            "fresh_remote_check": {"type": "boolean"},
        },
        "additionalProperties": False,
    },
}

READINESS_RESOURCE = {
    "uri": RESOURCE_URI,
    "name": "ATHENA Communication Route Readiness V1",
    "mimeType": "application/json",
}


__all__ = [
    "VERSION",
    "ARTIFACT",
    "TOOL_NAME",
    "RESOURCE_URI",
    "LAWS",
    "verify_route_readiness",
    "READINESS_TOOL",
    "READINESS_RESOURCE",
]
