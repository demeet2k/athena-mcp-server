from __future__ import annotations

"""Explicit durable escalation for the process-local ephemeral coordination plane.

The fast SQLite membrane already marks MATERIAL_CANDIDATE packets as requiring
explicit durable escalation. This organ closes that declared seam by creating an
idempotent Git Message Board MESSAGE event only when the caller explicitly asks
for it and an active durable Message Board actor exists.

No namespace or evidence laundering occurs:

* ephemeral AID != Message Board agent identity;
* actor_binding_ref is caller-supplied and remains unverified;
* ROUTED/PRESENTED/CONSUMED remain distinct;
* Message Board routing != recipient consumption;
* Federation source cursor != MCP process cursor;
* durable escalation does not mint a claim, assignment, truth, or execution
  authority.
"""

import hashlib
import json
from typing import Any, Mapping

from .ephemeral_coordination import RECEIPT_RANK
from .federation_ephemeral_bridge import decode_handoff_ref
from .message_board import MessageBoardRuntime, _json_text, _require_id

VERSION = "ATHENA.EPHEMERAL.DURABLE.ESCALATION.1"
ARTIFACT = "ATHENA.EPHEMERAL.DURABLE.ESCALATION.V1.CANDIDATE"
EVENT_FIELD = "ephemeral_escalation_id"

_STAGE_RANK = {"ROUTED": 0, **{name: int(rank) for name, rank in RECEIPT_RANK.items()}}
_ROLES = {"SENDER", "RECIPIENT"}

LAWS = [
    "EPHEMERAL_AID != MESSAGE_BOARD_AGENT_ID",
    "CALLER_BINDING_REF != IDENTITY_PROOF",
    "MATERIAL_CANDIDATE != DURABLE_CLAIM_OR_TRUTH",
    "ROUTED != DELIVERED != PRESENTED != CONSUMED != INCORPORATED != DECISION_CHANGED",
    "MESSAGE_BOARD_ROUTE != CONSUMPTION",
    "FEDERATION_SOURCE_CURSOR != MCP_PROCESS_CURSOR",
    "FEDERATION_PROJECTION != SOURCE_CURRENTNESS_PROOF",
    "ESCALATION_REPLAY_SAME_BASIS => IDEMPOTENT_DURABLE_MESSAGE",
    "DURABLE_ESCALATION != CLAIM != ASSIGNMENT != EXECUTION_AUTHORITY",
]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _text(value: Any, field: str, *, maximum: int | None = None) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{field} must be non-empty")
    if maximum is not None and len(out) > maximum:
        raise ValueError(f"{field} exceeds {maximum} characters")
    return out


def _board_ids(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ValueError("board_recipients must be an array")
    rows = sorted({_require_id(str(value), "board_recipient") for value in values})
    if not rows:
        raise ValueError("board_recipients must be non-empty")
    if len(rows) > 32:
        raise ValueError("board_recipients exceeds 32 unique items")
    return rows


def _federation_projection(packet_ref: str) -> dict[str, Any] | None:
    try:
        row = decode_handoff_ref(packet_ref)
    except (TypeError, ValueError):
        return None
    return {
        "handoff_digest": row.handoff_digest,
        "source_cursor_digest": row.source_cursor_digest,
        "transport_ref": row.transport_ref,
        "loss_class": row.loss_class,
        "reconstruction_token": row.reconstruction_token,
        "source_currentness_proven": False,
        "authority": "NONE",
        "laws": [
            "FEDERATION_SOURCE_CURSOR != MCP_PROCESS_CURSOR",
            "MCP_ROUTE != FEDERATION_ADMISSION",
        ],
    }


class EphemeralDurableBridge:
    def __init__(self, server: Any, runtime: Any):
        self.server = server
        self.runtime = runtime

    def _board(self) -> MessageBoardRuntime:
        git = getattr(self.server, "git", None)
        if git is None or not getattr(git, "enabled", False):
            raise ValueError("ATHENA_GIT_ROOT is required for durable escalation")
        return MessageBoardRuntime(git)

    @staticmethod
    def _normalized(args: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(args, Mapping):
            raise ValueError("args must be an object")
        role = _text(args.get("actor_role"), "actor_role").upper()
        if role not in _ROLES:
            raise ValueError("actor_role must be SENDER or RECIPIENT")
        minimum = str(args.get("minimum_receipt_stage") or "ROUTED").upper()
        if minimum not in _STAGE_RANK:
            raise ValueError("invalid minimum_receipt_stage")
        if role == "SENDER" and minimum != "ROUTED":
            raise ValueError("SENDER escalation cannot assert recipient receipt stages")
        note_raw = args.get("note")
        note = None if note_raw in (None, "") else _text(note_raw, "note", maximum=1200)
        return {
            "packet_id": _text(args.get("packet_id"), "packet_id", maximum=128),
            "ephemeral_actor_aid": _text(args.get("ephemeral_actor_aid"), "ephemeral_actor_aid", maximum=256),
            "actor_role": role,
            "actor_binding_ref": _text(args.get("actor_binding_ref"), "actor_binding_ref", maximum=2048),
            "board_agent_id": _require_id(str(args.get("board_agent_id") or ""), "board_agent_id"),
            "board_recipients": _board_ids(args.get("board_recipients")),
            "minimum_receipt_stage": minimum,
            "note": note,
            "remote": _text(args.get("remote") or "origin", "remote", maximum=256),
        }

    @staticmethod
    def _basis(norm: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "version": VERSION,
            "packet_id": norm["packet_id"],
            "ephemeral_actor_aid": norm["ephemeral_actor_aid"],
            "actor_role": norm["actor_role"],
            "actor_binding_ref": norm["actor_binding_ref"],
            "board_agent_id": norm["board_agent_id"],
            "board_recipients": list(norm["board_recipients"]),
            "minimum_receipt_stage": norm["minimum_receipt_stage"],
            "note": norm["note"],
        }

    @classmethod
    def _identity(cls, norm: Mapping[str, Any]) -> tuple[str, str]:
        full = _digest(cls._basis(norm))
        return "EDE-" + full[:32], "sha256:" + full

    def _source(self, norm: Mapping[str, Any]) -> dict[str, Any]:
        runtime = self.runtime
        now = float(runtime._now())
        with runtime._lock, runtime.db:
            runtime._gc(now)
            packet = runtime.db.execute(
                "SELECT * FROM ephemeral_packets WHERE packet_id=? AND expires_at>?",
                (norm["packet_id"], now),
            ).fetchone()
            if not packet:
                raise ValueError("EPHEMERAL_SOURCE_PACKET_NOT_LIVE_HOLD")
            if str(packet["delivery_class"]) != "MATERIAL_CANDIDATE":
                raise ValueError("EPHEMERAL_SOURCE_NOT_MATERIAL_CANDIDATE_HOLD")
            deliveries = runtime.db.execute(
                "SELECT recipient_aid,route_state,cursor,expires_at FROM ephemeral_deliveries "
                "WHERE packet_id=? AND expires_at>? ORDER BY recipient_aid",
                (norm["packet_id"], now),
            ).fetchall()
            recipients = [str(row["recipient_aid"]) for row in deliveries]
            actor = norm["ephemeral_actor_aid"]
            role = norm["actor_role"]
            if role == "SENDER":
                if actor != str(packet["sender_aid"]):
                    raise ValueError("EPHEMERAL_ACTOR_NOT_SOURCE_SENDER_HOLD")
                observed_stage = "ROUTED"
            else:
                if actor not in recipients:
                    raise ValueError("EPHEMERAL_ACTOR_NOT_PACKET_RECIPIENT_HOLD")
                observed_stage = str(runtime._stage(norm["packet_id"], actor) or "ROUTED")
                if _STAGE_RANK[observed_stage] < _STAGE_RANK[norm["minimum_receipt_stage"]]:
                    raise ValueError(
                        "EPHEMERAL_RECEIPT_STAGE_HOLD "
                        f"observed={observed_stage} required={norm['minimum_receipt_stage']}"
                    )
            source = {
                "packet_id": str(packet["packet_id"]),
                "sender_aid": str(packet["sender_aid"]),
                "delivery_class": str(packet["delivery_class"]),
                "salience": float(packet["salience"]),
                "ttl_ms": int(packet["ttl_ms"]),
                "packet_digest_or_ref": str(packet["packet_digest_or_ref"]),
                "lamport": int(packet["lamport"]),
                "causal_parents": json.loads(packet["causal_parents_json"]),
                "created_at": float(packet["created_at"]),
                "expires_at": float(packet["expires_at"]),
                "recipient_aids": recipients,
                "actor_observed_receipt_stage": observed_stage,
                "actor_minimum_receipt_stage": norm["minimum_receipt_stage"],
                "authority": "NONE",
            }
        source["federation_projection"] = _federation_projection(source["packet_digest_or_ref"])
        return source

    @staticmethod
    def _existing(board: MessageBoardRuntime, escalation_id: str) -> dict[str, Any] | None:
        for event in reversed(board._events()):
            if event.get("kind") != "MESSAGE":
                continue
            payload = event.get("payload") or {}
            if isinstance(payload, dict) and payload.get(EVENT_FIELD) == escalation_id:
                return event
        return None

    def _packet(self, norm: Mapping[str, Any], source: Mapping[str, Any], *, board_claim_id: str | None, inactive_recipients: list[str]) -> dict[str, Any]:
        escalation_id, escalation_digest = self._identity(norm)
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "ephemeral_escalation_id": escalation_id,
            "escalation_digest": escalation_digest,
            "source_packet": dict(source),
            "ephemeral_actor": {
                "aid": norm["ephemeral_actor_aid"],
                "role": norm["actor_role"],
                "binding_ref": norm["actor_binding_ref"],
                "binding_standing": "CALLER_SUPPLIED_OPAQUE_REFERENCE_NOT_IDENTITY_PROOF",
            },
            "durable_route": {
                "board_agent_id": norm["board_agent_id"],
                "board_claim_id": board_claim_id,
                "board_recipients": list(norm["board_recipients"]),
                "inactive_recipients": list(inactive_recipients),
            },
            "note": norm["note"],
            "identity_equivalence_proven": False,
            "source_currentness_proven": False if source.get("federation_projection") else "NOT_APPLICABLE_OR_UNKNOWN",
            "claim_authority": False,
            "assignment_authority": False,
            "execution_authority": False,
            "laws": list(LAWS),
        }

    def plan(self, args: Mapping[str, Any]) -> dict[str, Any]:
        try:
            norm = self._normalized(args)
            escalation_id, escalation_digest = self._identity(norm)
            board = self._board()
            mode = str(args.get("shared_remote_mode") or "REQUIRED").upper()
            snapshot = board.read(
                agent_id=norm["board_agent_id"],
                limit=100,
                include_stale=False,
                remote=norm["remote"],
                shared_remote_mode=mode,
            )
            existing = self._existing(board, escalation_id)
            if existing:
                payload = existing.get("payload") or {}
                if payload.get("escalation_digest") != escalation_digest:
                    return {
                        "status": "EPHEMERAL_DURABLE_IDENTITY_CONFLICT_HOLD",
                        "ephemeral_escalation_id": escalation_id,
                        "authority": "NONE",
                        "laws": list(LAWS),
                    }
                return {
                    "status": "EPHEMERAL_MATERIAL_ALREADY_ESCALATED",
                    "ephemeral_escalation_id": escalation_id,
                    "message_event": existing,
                    "idempotent": True,
                    "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
                    "authority": "EXISTING_MESSAGE_BOARD_EVENT_ONLY",
                    "laws": list(LAWS),
                }
            source = self._source(norm)
            active = {str(row.get("agent_id")): row for row in (snapshot.get("active") or [])}
            board_actor = active.get(norm["board_agent_id"])
            if not board_actor:
                return {
                    "status": "EPHEMERAL_DURABLE_BOARD_AGENT_NOT_ACTIVE_HOLD",
                    "ephemeral_escalation_id": escalation_id,
                    "source_packet": source,
                    "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
                    "authority": "NONE",
                    "laws": list(LAWS),
                }
            inactive = sorted(set(norm["board_recipients"]) - set(active))
            packet = self._packet(norm, source, board_claim_id=board_actor.get("claim_id"), inactive_recipients=inactive)
            return {
                "status": "EPHEMERAL_DURABLE_PLAN_READY" if snapshot.get("shared_frontier_verified") else "EPHEMERAL_DURABLE_PLAN_UNVERIFIED",
                "ephemeral_escalation_id": escalation_id,
                "escalation_digest": escalation_digest,
                "plan": packet,
                "shared_frontier_verified": bool(snapshot.get("shared_frontier_verified")),
                "identity_binding_proven": False,
                "mutation": False,
                "authority": "NONE",
                "laws": list(LAWS),
            }
        except ValueError as exc:
            return {
                "status": "EPHEMERAL_DURABLE_PLAN_HOLD",
                "reason": str(exc),
                "mutation": False,
                "authority": "NONE",
                "laws": list(LAWS),
            }

    def escalate(self, args: Mapping[str, Any]) -> dict[str, Any]:
        try:
            norm = self._normalized(args)
        except ValueError as exc:
            return {
                "status": "EPHEMERAL_DURABLE_ESCALATION_HOLD",
                "reason": str(exc),
                "durable_return": False,
                "laws": list(LAWS),
            }
        escalation_id, escalation_digest = self._identity(norm)
        try:
            board = self._board()
        except ValueError as exc:
            return {
                "status": "EPHEMERAL_DURABLE_ESCALATION_HOLD",
                "reason": str(exc),
                "durable_return": False,
                "laws": list(LAWS),
            }

        def build(base: str):
            existing = self._existing(board, escalation_id)
            if existing:
                payload = existing.get("payload") or {}
                if payload.get("escalation_digest") != escalation_digest:
                    return {
                        "return": {
                            "status": "EPHEMERAL_DURABLE_IDENTITY_CONFLICT_HOLD",
                            "ephemeral_escalation_id": escalation_id,
                            "durable_return": False,
                        }
                    }
                return {
                    "return": {
                        "status": "EPHEMERAL_MATERIAL_ALREADY_ESCALATED",
                        "ephemeral_escalation_id": escalation_id,
                        "message_event": existing,
                        "durable_ref": f"message-board:{existing.get('event_id')}",
                        "idempotent": True,
                        "claim_authority": False,
                        "assignment_authority": False,
                        "execution_authority": False,
                    }
                }
            source = self._source(norm)
            active = {str(row.get("agent_id")): row for row in board._active()}
            board_actor = active.get(norm["board_agent_id"])
            if not board_actor:
                return {
                    "return": {
                        "status": "EPHEMERAL_DURABLE_BOARD_AGENT_NOT_ACTIVE_HOLD",
                        "ephemeral_escalation_id": escalation_id,
                        "durable_return": False,
                    }
                }
            inactive = sorted(set(norm["board_recipients"]) - set(active))
            packet = self._packet(norm, source, board_claim_id=board_actor.get("claim_id"), inactive_recipients=inactive)
            message = (
                f"Ephemeral MATERIAL_CANDIDATE escalated: {source['packet_id']}\n"
                f"ref={source['packet_digest_or_ref']}\n"
                f"ephemeral_actor={norm['ephemeral_actor_aid']} role={norm['actor_role']}"
            )
            if norm["note"]:
                message += "\nnote=" + norm["note"]
            payload = {
                "message_kind": "INFO",
                "message": message,
                "claim_id": board_actor.get("claim_id"),
                EVENT_FIELD: escalation_id,
                "escalation_digest": escalation_digest,
                "ephemeral_durable_bridge": packet,
            }
            event_rel, event = board._event(
                "MESSAGE",
                norm["board_agent_id"],
                payload,
                recipients=list(norm["board_recipients"]),
            )
            return {
                "files": {event_rel: _json_text(event)},
                "message": f"ephemeral durable escalation {escalation_id}",
                "result": {
                    "status": "EPHEMERAL_MATERIAL_ESCALATED",
                    "ephemeral_escalation_id": escalation_id,
                    "message_event": event,
                    "durable_ref": f"message-board:{event['event_id']}",
                    "source_packet": source,
                    "inactive_recipients": inactive,
                    "delivery": "DURABLY_ROUTED_NOT_CONSUMED",
                    "identity_binding_proven": False,
                    "claim_authority": False,
                    "assignment_authority": False,
                    "execution_authority": False,
                },
            }

        try:
            result = board._mutate(
                agent_id=norm["board_agent_id"],
                remote=norm["remote"],
                build_files=build,
            )
        except ValueError as exc:
            return {
                "status": "EPHEMERAL_DURABLE_ESCALATION_HOLD",
                "reason": str(exc),
                "ephemeral_escalation_id": escalation_id,
                "durable_return": False,
                "laws": list(LAWS),
            }
        result = dict(result)
        result.setdefault("laws", list(LAWS))
        return result

    def describe(self) -> dict[str, Any]:
        return {
            "artifact": ARTIFACT,
            "version": VERSION,
            "source_plane": "ATHENA.EPHEMERAL.COORDINATION.MEMBRANE.V0",
            "destination_plane": "ATHENA.MESSAGE.BOARD.V1",
            "accepted_delivery_class": "MATERIAL_CANDIDATE",
            "operations": ["athena_ephemeral_durable_plan", "athena_ephemeral_durable_escalate"],
            "idempotency": "DETERMINISTIC_ESCALATION_ID + DURABLE_MESSAGE_EVENT_LOOKUP",
            "federation_projection_awareness": True,
            "identity_binding_authority": "CALLER_SUPPLIED_OPAQUE_REFERENCE_ONLY",
            "claim_authority": False,
            "assignment_authority": False,
            "execution_authority": False,
            "laws": list(LAWS),
        }

    def benchmark(self) -> dict[str, Any]:
        return {
            "ephemeral_durable_bridge_version": VERSION,
            "ephemeral_durable_bridge_authority": "EXISTING_MESSAGE_BOARD_WRITE_PATH_ONLY",
            "ephemeral_durable_bridge_auto_escalation": False,
        }


class EphemeralDurableBridgeSurface:
    def __init__(self, server: Any, runtime: Any):
        self.bridge = EphemeralDurableBridge(server, runtime)

    def call_tool(self, name: str, args: Mapping[str, Any]):
        fn = {
            "athena_ephemeral_durable_plan": self.bridge.plan,
            "athena_ephemeral_durable_escalate": self.bridge.escalate,
        }.get(name)
        return (True, fn(args)) if fn else (False, None)

    def read_resource(self, uri: str):
        from .ephemeral_durable_bridge_protocol import EPHEMERAL_DURABLE_RESOURCE

        if uri != EPHEMERAL_DURABLE_RESOURCE["uri"]:
            raise KeyError(uri)
        return self.bridge.describe()

    def benchmark(self):
        return self.bridge.benchmark()


__all__ = [
    "VERSION",
    "ARTIFACT",
    "LAWS",
    "EphemeralDurableBridge",
    "EphemeralDurableBridgeSurface",
]
