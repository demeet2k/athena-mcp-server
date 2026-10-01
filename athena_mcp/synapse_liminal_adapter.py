from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .liminal_beacon_mesh import VERSION
from .liminal_beacon_mesh_protocol import MESSAGE_CLASSES, RECEIPT_STAGES, VISIBILITY_STATES

SYNAPSE_SCHEMA = "ATHENA.SYNAPSE.ENVELOPE.V1"
PACKET_PROFILE = "LIMINAL_BEACON_CAPSULE_V1"
RECEIPT_PROFILE = "LIMINAL_BEACON_RECEIPT_V1"
SOURCE_REPOSITORY = "demeet2k/athena-mcp-server"
LIMINAL_RESOURCE = "athena://liminal/beacon-mesh"

_PACKET_PRESERVED = (
    "packet_id", "event_seq", "sender_id", "instance_id", "session_epoch", "sender_seq",
    "lamport", "message_class", "summary", "payload_ref", "goal_ref", "evidence_ceiling",
    "urgency", "novelty", "created_at", "expires_at", "visibility", "recipients",
    "changed_refs", "affected_refs", "correction_of", "retraction_of", "reply_to",
    "parent_ids", "semantic_digest",
)
_PACKET_LOST = (
    "artifact", "ttl_seconds", "capabilities", "needs", "offers", "provides",
    "dependencies", "capacity_units", "needed_units", "_route_keys", "_reverse_targets",
)
_RECEIPT_FIELDS = (
    "agent_id", "packet_id", "stage", "stage_index", "updated_at", "disposition",
    "consumer_ref", "residual", "propagation_refs", "outcome_ref",
)
_CLASS_EVENT = {
    "CLAIM": "CLAIM",
    "CORRECTION": "CONTRADICTION",
    "RETRACTION": "SUPERSESSION",
    "BLOCKER": "HOLD",
    "INHIBIT": "HOLD",
    "RESULT": "RETURN",
    "HANDOFF": "RETURN",
}
_EVENT_CLASS = {
    "OBSERVATION": "DELTA",
    "PROPOSAL": "OFFER",
    "CLAIM": "CLAIM",
    "EFFECT": "RESULT",
    "RECEIPT": "RESULT",
    "WITNESS": "DISCOVERY",
    "CONTRADICTION": "CORRECTION",
    "HOLD": "BLOCKER",
    "RETURN": "RESULT",
    "SUPERSESSION": "RETRACTION",
}
_VALID_EVENTS = {
    "OBSERVATION", "PROPOSAL", "CLAIM", "EFFECT", "RECEIPT",
    "WITNESS", "CONTRADICTION", "HOLD", "RETURN", "SUPERSESSION",
}
_VALID_EPISTEMIC = {"OBS", "RET", "DER", "HYP", "SIM", "UNK", "CON"}


class SynapseLiminalError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _origin(native_event_id: str, source_revision: str, *, native_system: str, actor_id: str | None = None) -> dict[str, Any]:
    if not source_revision:
        raise SynapseLiminalError("source_revision is required")
    return {
        "node_id": "athena-mcp",
        "repository": SOURCE_REPOSITORY,
        "native_system": native_system,
        "native_event_id": native_event_id,
        "source_revision": source_revision,
        "native_ref": LIMINAL_RESOURCE,
        "actor_id": actor_id,
    }


def _bridge_id(origin: Mapping[str, Any], profile: str) -> str:
    material = {
        "schema": SYNAPSE_SCHEMA,
        "projection_profile": profile,
        "node_id": origin.get("node_id"),
        "repository": origin.get("repository"),
        "native_system": origin.get("native_system"),
        "native_event_id": origin.get("native_event_id"),
        "source_revision": origin.get("source_revision"),
    }
    return "SYN-" + hashlib.sha256(_canonical(material).encode("utf-8")).hexdigest()[:32]


def _packet_bridge_id(packet_id: str, source_revision: str) -> str:
    return _bridge_id(_origin(packet_id, source_revision, native_system=VERSION), PACKET_PROFILE)


def _receipt_native_id(agent_id: str, packet_id: str, stage: str) -> str:
    return f"{packet_id}:{agent_id}:{stage}"


def _receipt_bridge_id(agent_id: str, packet_id: str, stage: str, source_revision: str) -> str:
    native_id = _receipt_native_id(agent_id, packet_id, stage)
    return _bridge_id(
        _origin(native_id, source_revision, native_system="liminal-beacon-receipt-v1", actor_id=agent_id),
        RECEIPT_PROFILE,
    )


def _wall_time(value: Any) -> str | None:
    if value is None:
        return None
    return f"unix:{value}"


def _target_id(value: Any, source_revision: str) -> str | None:
    raw = str(value or "").strip()
    return _packet_bridge_id(raw, source_revision) if raw else None


def _validate_envelope(envelope: Mapping[str, Any]) -> None:
    if envelope.get("schema") != SYNAPSE_SCHEMA:
        raise SynapseLiminalError("unsupported Synapse schema")
    if envelope.get("event_type") not in _VALID_EVENTS:
        raise SynapseLiminalError("unsupported event_type")

    projection = envelope.get("projection")
    if not isinstance(projection, Mapping) or not projection.get("profile"):
        raise SynapseLiminalError("projection profile required")
    loss = projection.get("loss_class")
    preserved = projection.get("preserved")
    lost = projection.get("lost")
    token = projection.get("return_token")
    if loss not in {"LOSSLESS", "LOSSY_AUX", "NONRETURNABLE"}:
        raise SynapseLiminalError("invalid projection contract")
    for name, values in (("preserved", preserved), ("lost", lost)):
        if not isinstance(values, list) or len(values) != len(set(values)) or not all(isinstance(x, str) and x for x in values):
            raise SynapseLiminalError(f"projection.{name} must be a unique string array")
    if loss == "LOSSLESS" and (lost or not token):
        raise SynapseLiminalError("invalid LOSSLESS projection")
    if loss == "LOSSY_AUX" and (not lost or not token):
        raise SynapseLiminalError("invalid LOSSY_AUX projection")
    if loss == "NONRETURNABLE" and (not lost or token is not None):
        raise SynapseLiminalError("invalid NONRETURNABLE projection")

    origin = envelope.get("origin")
    if not isinstance(origin, Mapping):
        raise SynapseLiminalError("origin required")
    for key in ("node_id", "repository", "native_system", "native_event_id", "source_revision"):
        if not origin.get(key):
            raise SynapseLiminalError(f"origin.{key} required")
    if envelope.get("event_id") != _bridge_id(origin, str(projection["profile"])):
        raise SynapseLiminalError("bridge identity mismatch")

    semantics = envelope.get("semantics")
    if not isinstance(semantics, Mapping) or semantics.get("epistemic_class") not in _VALID_EPISTEMIC:
        raise SynapseLiminalError("invalid epistemic class")
    if not semantics.get("authority_class") or not semantics.get("truth_ceiling"):
        raise SynapseLiminalError("authority/truth ceiling required")

    routing = envelope.get("routing")
    routes = routing.get("return_routes") if isinstance(routing, Mapping) else None
    if not isinstance(routes, list) or not routes or len(routes) != len(set(routes)) or not all(isinstance(x, str) and x for x in routes):
        raise SynapseLiminalError("return route required")

    causality = envelope.get("causality")
    if not isinstance(causality, Mapping):
        raise SynapseLiminalError("causality required")
    for field in ("parent_ids", "supersedes"):
        values = causality.get(field, [])
        if not isinstance(values, list) or len(values) != len(set(values)) or not all(isinstance(x, str) and x for x in values):
            raise SynapseLiminalError(f"invalid causality.{field}")
    for field in ("reply_to", "correction_of", "retraction_of"):
        value = causality.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            raise SynapseLiminalError(f"invalid causality.{field}")
    if envelope.get("event_type") == "CONTRADICTION" and not causality.get("correction_of") and not causality.get("parent_ids"):
        raise SynapseLiminalError("CONTRADICTION requires an explicit target")
    if envelope.get("event_type") == "SUPERSESSION" and not causality.get("retraction_of") and not causality.get("supersedes"):
        raise SynapseLiminalError("SUPERSESSION requires an explicit target")

    frontier = envelope.get("frontier")
    if not isinstance(frontier, Mapping) or frontier.get("semantics") not in {
        "NATIVE_EVENT_FRONTIER", "NATIVE_SNAPSHOT", "BRIDGE_VECTOR", "UNKNOWN"
    }:
        raise SynapseLiminalError("frontier required")
    if frontier.get("semantics") == "UNKNOWN" and frontier.get("native_digest") is not None:
        raise SynapseLiminalError("UNKNOWN frontier cannot assert digest")
    if frontier.get("semantics") != "UNKNOWN" and not frontier.get("native_digest") and not frontier.get("native_ref"):
        raise SynapseLiminalError("known frontier requires native digest or reference")

    clock = envelope.get("clock")
    if not isinstance(clock, Mapping) or not clock.get("bridge_observed_at"):
        raise SynapseLiminalError("bridge observation time required")
    seq = clock.get("origin_sequence")
    if seq is not None and (isinstance(seq, bool) or not isinstance(seq, int) or seq < 0):
        raise SynapseLiminalError("clock.origin_sequence must be a non-negative integer")

    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise SynapseLiminalError("payload required")
    if payload.get("body") is not None and payload.get("body_digest") != _digest(payload["body"]):
        raise SynapseLiminalError("payload body digest mismatch")

    receipt = envelope.get("receipt")
    if envelope.get("event_type") == "RECEIPT":
        if not isinstance(receipt, Mapping) or receipt.get("stage") not in RECEIPT_STAGES:
            raise SynapseLiminalError("valid receipt stage required")

    _canonical(envelope)


def liminal_capsule_to_synapse(
    capsule: Mapping[str, Any],
    *,
    source_revision: str,
    bridge_observed_at: str,
) -> dict[str, Any]:
    packet_id = str(capsule.get("packet_id") or "").strip()
    message_class = str(capsule.get("message_class") or "").upper()
    if not packet_id or message_class not in MESSAGE_CLASSES:
        raise SynapseLiminalError("valid packet_id/message_class required")
    sender_id = str(capsule.get("sender_id") or "").strip()
    if not sender_id:
        raise SynapseLiminalError("sender_id required")

    origin = _origin(packet_id, source_revision, native_system=VERSION, actor_id=sender_id)
    event_type = _CLASS_EVENT.get(message_class, "OBSERVATION")
    parents = [_packet_bridge_id(str(x), source_revision) for x in capsule.get("parent_ids") or [] if str(x).strip()]
    correction = _target_id(capsule.get("correction_of"), source_revision)
    retraction = _target_id(capsule.get("retraction_of"), source_revision)
    reply = _target_id(capsule.get("reply_to"), source_revision)
    body = dict(capsule)
    residuals = [
        "PUBLIC_CAPSULE_OMITS_FULL_EPHEMERAL_PACKET_FIELDS",
        *[f"PROJECTION_LOSS:{field}" for field in _PACKET_LOST],
    ]

    envelope = {
        "schema": SYNAPSE_SCHEMA,
        "event_id": _bridge_id(origin, PACKET_PROFILE),
        "event_type": event_type,
        "subject": str(capsule.get("goal_ref") or f"liminal:{packet_id}"),
        "projection": {
            "profile": PACKET_PROFILE,
            "loss_class": "LOSSY_AUX",
            "preserved": list(_PACKET_PRESERVED),
            "lost": list(_PACKET_LOST),
            "return_token": LIMINAL_RESOURCE,
        },
        "origin": origin,
        "semantics": {
            "epistemic_class": "CON" if message_class in {"CORRECTION", "RETRACTION"} else "UNK",
            "authority_class": "NON_AUTHORITATIVE_COORDINATION",
            "truth_ceiling": "LIMINAL_ROUTING_STATE",
            "native_kind": message_class,
            "evidence_ceiling": capsule.get("evidence_ceiling"),
        },
        "routing": {
            "return_routes": [LIMINAL_RESOURCE],
            "recipients": list(capsule.get("recipients") or []),
            "route_keys": [],
            "visibility": capsule.get("visibility"),
        },
        "causality": {
            "parent_ids": parents,
            "reply_to": reply,
            "correction_of": correction,
            "retraction_of": retraction,
            "supersedes": [],
        },
        "frontier": {"semantics": "UNKNOWN", "native_digest": None, "native_ref": None},
        "clock": {
            "wall_time": _wall_time(capsule.get("created_at")),
            "bridge_observed_at": bridge_observed_at,
            "origin_sequence": capsule.get("event_seq"),
        },
        "payload": {
            "summary": str(capsule.get("summary") or ""),
            "payload_ref": capsule.get("payload_ref") or LIMINAL_RESOURCE,
            "body": body,
            "body_digest": _digest(body),
            "evidence": [],
            "residuals": residuals,
        },
        "receipt": None,
    }
    _validate_envelope(envelope)
    return envelope


def liminal_capsule_from_synapse(envelope: Mapping[str, Any]) -> dict[str, Any]:
    _validate_envelope(envelope)
    if envelope["projection"]["profile"] != PACKET_PROFILE:
        raise SynapseLiminalError("not a Liminal Beacon capsule projection")
    body = envelope["payload"].get("body")
    if not isinstance(body, Mapping):
        raise SynapseLiminalError("capsule body required")
    if str(body.get("packet_id")) != str(envelope["origin"]["native_event_id"]):
        raise SynapseLiminalError("capsule/native identity mismatch")
    return dict(body)


def liminal_receipt_to_synapse(
    receipt: Mapping[str, Any],
    *,
    source_revision: str,
    bridge_observed_at: str,
) -> dict[str, Any]:
    agent_id = str(receipt.get("agent_id") or "").strip()
    packet_id = str(receipt.get("packet_id") or "").strip()
    stage = str(receipt.get("stage") or "").upper()
    if not agent_id or not packet_id or stage not in RECEIPT_STAGES:
        raise SynapseLiminalError("valid receipt agent/packet/stage required")
    stage_index = RECEIPT_STAGES.index(stage)
    if receipt.get("stage_index") not in (None, stage_index):
        raise SynapseLiminalError("receipt stage_index disagrees with stage")

    native_id = _receipt_native_id(agent_id, packet_id, stage)
    origin = _origin(native_id, source_revision, native_system="liminal-beacon-receipt-v1", actor_id=agent_id)
    parents = [_packet_bridge_id(packet_id, source_revision)]
    if stage_index > 0:
        parents.append(_receipt_bridge_id(agent_id, packet_id, RECEIPT_STAGES[stage_index - 1], source_revision))
    body = dict(receipt)

    envelope = {
        "schema": SYNAPSE_SCHEMA,
        "event_id": _bridge_id(origin, RECEIPT_PROFILE),
        "event_type": "RECEIPT",
        "subject": f"liminal:{packet_id}",
        "projection": {
            "profile": RECEIPT_PROFILE,
            "loss_class": "LOSSLESS",
            "preserved": list(_RECEIPT_FIELDS),
            "lost": [],
            "return_token": LIMINAL_RESOURCE,
        },
        "origin": origin,
        "semantics": {
            "epistemic_class": "OBS",
            "authority_class": "NON_AUTHORITATIVE_COORDINATION",
            "truth_ceiling": "RECIPIENT_RECEIPT_STATE",
            "native_kind": "LIMINAL_RECEIPT",
            "evidence_ceiling": None,
        },
        "routing": {
            "return_routes": [LIMINAL_RESOURCE],
            "recipients": [],
            "route_keys": [f"liminal:{packet_id}"],
            "visibility": "COLONY",
        },
        "causality": {
            "parent_ids": parents,
            "reply_to": _packet_bridge_id(packet_id, source_revision),
            "correction_of": None,
            "retraction_of": None,
            "supersedes": [],
        },
        "frontier": {"semantics": "UNKNOWN", "native_digest": None, "native_ref": None},
        "clock": {
            "wall_time": _wall_time(receipt.get("updated_at")),
            "bridge_observed_at": bridge_observed_at,
            "origin_sequence": None,
        },
        "payload": {
            "summary": f"{agent_id} {stage} {packet_id}",
            "payload_ref": receipt.get("consumer_ref") or receipt.get("outcome_ref") or LIMINAL_RESOURCE,
            "body": body,
            "body_digest": _digest(body),
            "evidence": [],
            "residuals": [str(receipt["residual"])] if receipt.get("residual") else [],
        },
        "receipt": {
            "stage": stage,
            "recipient": agent_id,
            "disposition": receipt.get("disposition"),
            "outcome_ref": receipt.get("outcome_ref"),
        },
    }
    _validate_envelope(envelope)
    return envelope


def liminal_receipt_from_synapse(envelope: Mapping[str, Any]) -> dict[str, Any]:
    _validate_envelope(envelope)
    if envelope["projection"]["profile"] != RECEIPT_PROFILE:
        raise SynapseLiminalError("not a Liminal receipt projection")
    body = envelope["payload"].get("body")
    if not isinstance(body, Mapping):
        raise SynapseLiminalError("receipt body required")
    if body.get("stage") != envelope["receipt"]["stage"]:
        raise SynapseLiminalError("receipt body/stage mismatch")
    return dict(body)


def synapse_to_liminal_ingress_plan(
    envelope: Mapping[str, Any],
    *,
    agent_id: str,
) -> dict[str, Any]:
    """Translate a foreign envelope into LBM emit args without mutating runtime."""
    _validate_envelope(envelope)
    agent_id = str(agent_id or "").strip()
    if not agent_id:
        raise SynapseLiminalError("target agent_id required")

    semantics = envelope["semantics"]
    native_kind = str(semantics.get("native_kind") or "").upper()
    event_type = str(envelope["event_type"])
    message_class = native_kind if native_kind in MESSAGE_CLASSES else _EVENT_CLASS[event_type]
    payload = envelope["payload"]
    routing = envelope["routing"]
    projection = envelope["projection"]
    causality = envelope["causality"]
    source_ref = payload.get("payload_ref") or projection.get("return_token") or routing["return_routes"][0]

    causal_ids = []
    for field in ("parent_ids", "supersedes"):
        causal_ids.extend(str(x) for x in causality.get(field) or [])
    for field in ("reply_to", "correction_of", "retraction_of"):
        if causality.get(field):
            causal_ids.append(str(causality[field]))
    causal_refs = [f"synapse:{x}" for x in sorted(set(causal_ids))]

    residuals = [
        "INGRESS_IS_NEW_LIMINAL_SIGNAL_NOT_SOURCE_EVENT_IDENTITY",
        "FOREIGN_CAUSAL_IDS_RETAINED_AS_CAUSAL_REFS_NOT_NATIVE_PACKET_PARENTS",
    ]
    if routing.get("recipients"):
        residuals.append("FOREIGN_RECIPIENT_NAMESPACE_NOT_ASSUMED")
    if event_type in {"CONTRADICTION", "SUPERSESSION"}:
        residuals.append("FOREIGN_TARGET_NOT_INVERTED_TO_LOCAL_LIMINAL_PACKET_ID")
    visibility = str(routing.get("visibility") or "COLONY").upper()
    if visibility not in VISIBILITY_STATES:
        visibility = "COLONY"
        residuals.append("FOREIGN_VISIBILITY_NORMALIZED_TO_COLONY")

    summary = str(payload.get("summary") or envelope.get("subject") or envelope["event_id"])
    emit_args = {
        "agent_id": agent_id,
        "message_class": message_class,
        "summary": f"[SYNAPSE {envelope['event_id']}] {summary}",
        "payload_ref": str(source_ref),
        "goal_ref": str(envelope["subject"]),
        "evidence_ceiling": "SYNAPSE_ENVELOPE_ROUTING_STATE_ONLY",
        "work_refs": [str(envelope["subject"])],
        "object_refs": [f"synapse:{envelope['event_id']}"],
        "dependency_refs": [str(x) for x in routing["return_routes"]],
        "causal_refs": causal_refs,
        "semantic_tags": [
            f"synapse-profile:{projection['profile']}",
            f"synapse-event-type:{event_type}",
            f"synapse-epistemic:{semantics['epistemic_class']}",
        ],
        "changed_refs": [],
        "affected_refs": [str(envelope["subject"])],
        "recipients": [],
        "visibility": visibility,
    }
    return {
        "schema": "ATHENA.SYNAPSE.LIMINAL.INGRESS.PLAN.V1",
        "source_event_id": envelope["event_id"],
        "standing": "PROPOSAL_ONLY_NO_RUNTIME_MUTATION",
        "emit_args": emit_args,
        "residuals": residuals,
        "laws": [
            "FOREIGN_SYNAPSE_EVENT != LOCAL_LIMINAL_PACKET",
            "INGRESS_ROUTING != CONSUMPTION",
            "FOREIGN_AUTHORITY != LOCAL_EXECUTION_AUTHORITY",
        ],
    }


__all__ = [
    "PACKET_PROFILE", "RECEIPT_PROFILE", "SynapseLiminalError",
    "liminal_capsule_to_synapse", "liminal_capsule_from_synapse",
    "liminal_receipt_to_synapse", "liminal_receipt_from_synapse",
    "synapse_to_liminal_ingress_plan",
]
