from __future__ import annotations

"""Process-local causal correlation for Synapse -> Liminal ingress.

The native Liminal packet and receipt envelopes remain untouched.  This module
records the observed mapping from one foreign Synapse event to the newly emitted
local Liminal packet and can project that mapping as a *separate* shared Synapse
envelope.  The mapping is intentionally process-local: restart loss is reported
as UNOBSERVED rather than reconstructed from packet hashes.
"""

from copy import deepcopy
from hashlib import sha256
from threading import RLock
from typing import Any, Mapping

from .synapse_liminal_adapter import (
    LIMINAL_RESOURCE,
    _bridge_id,
    _canonical,
    _digest,
    _origin,
    _packet_bridge_id,
    _validate_envelope,
)

ARTIFACT = "ATHENA.LIMINAL.SYNAPSE.INGRESS.CORRELATION.V1"
VERSION = "1.0.0"
CORRELATION_PROFILE = "LIMINAL_INGRESS_CORRELATION_V1"
CORRELATION_NATIVE_SYSTEM = "ATHENA.LIMINAL.SYNAPSE.INGRESS.CORRELATION.V1"
AUTHORITY_CLASS = "ZERO_AUTHORITY_INTEROP"
TRUTH_CEILING = "PROCESS_LOCAL_INGRESS_CORRELATION_ONLY"
_LEDGER_ATTR = "_synapse_ingress_correlation_v1"
_LOCK_ATTR = "_synapse_ingress_correlation_v1_lock"

LAWS = (
    "SOURCE_EVENT_CORRELATION != NATIVE_RECEIPT_IDENTITY",
    "PROCESS_LOCAL_CORRELATION != DURABLE_CAUSAL_PROOF",
    "RETURN_ROUTE_PROPAGATION != DELIVERY",
    "FOREIGN_AUTHORITY != LOCAL_EXECUTION_AUTHORITY",
    "CORRELATION_ENVELOPE != CANONICAL_PACKET_OR_RECEIPT_ENVELOPE",
)


def _required(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} required")
    return text


def _ledger(server: Any) -> tuple[RLock, dict[str, dict[str, dict[str, Any]]]]:
    lock = getattr(server, _LOCK_ATTR, None)
    if lock is None:
        lock = RLock()
        setattr(server, _LOCK_ATTR, lock)
    rows = getattr(server, _LEDGER_ATTR, None)
    if rows is None:
        rows = {}
        setattr(server, _LEDGER_ATTR, rows)
    return lock, rows


def _identity_material(
    envelope: Mapping[str, Any],
    *,
    local_packet_id: str,
    agent_id: str,
) -> dict[str, str]:
    return {
        "source_event_id": _required(envelope.get("event_id"), "source event_id"),
        "source_envelope_digest": _digest(envelope),
        "local_packet_id": _required(local_packet_id, "local packet_id"),
        "local_agent_id": _required(agent_id, "local agent_id"),
    }


def _correlation_id(material: Mapping[str, Any]) -> str:
    return "SIC-" + sha256(_canonical(material).encode("utf-8")).hexdigest()[:32]


def _record_from_ingress(
    envelope: Mapping[str, Any],
    emitted: Mapping[str, Any],
    *,
    agent_id: str,
    observed_at: str,
) -> tuple[str, dict[str, Any]]:
    _validate_envelope(envelope)
    packet = emitted.get("packet") if isinstance(emitted, Mapping) else None
    if not isinstance(packet, Mapping):
        raise ValueError("INGRESS_CORRELATION_LOCAL_PACKET_REQUIRED_HOLD")
    packet_id = _required(packet.get("packet_id"), "local packet_id")
    observed_at = _required(observed_at, "correlation observed_at")
    material = _identity_material(envelope, local_packet_id=packet_id, agent_id=agent_id)
    correlation_id = _correlation_id(material)
    origin = envelope.get("origin") if isinstance(envelope.get("origin"), Mapping) else {}
    projection = envelope.get("projection") if isinstance(envelope.get("projection"), Mapping) else {}
    routing = envelope.get("routing") if isinstance(envelope.get("routing"), Mapping) else {}
    semantics = envelope.get("semantics") if isinstance(envelope.get("semantics"), Mapping) else {}
    clock = envelope.get("clock") if isinstance(envelope.get("clock"), Mapping) else {}
    return correlation_id, {
        "artifact": ARTIFACT,
        "version": VERSION,
        "correlation_id": correlation_id,
        "source_event_id": material["source_event_id"],
        "source_envelope_digest": material["source_envelope_digest"],
        "source_subject": _required(envelope.get("subject"), "source subject"),
        "source_profile": _required(projection.get("profile"), "source profile"),
        "source_origin": {
            "node_id": origin.get("node_id"),
            "repository": origin.get("repository"),
            "native_system": origin.get("native_system"),
            "native_event_id": origin.get("native_event_id"),
            "source_revision": origin.get("source_revision"),
        },
        "source_authority_class": semantics.get("authority_class"),
        "source_bridge_observed_at": clock.get("bridge_observed_at"),
        "source_return_routes": sorted(set(str(x) for x in routing.get("return_routes") or [] if str(x))),
        "source_route_keys": sorted(set(str(x) for x in routing.get("route_keys") or [] if str(x))),
        "local_packet_id": packet_id,
        "local_agent_id": material["local_agent_id"],
        "local_semantic_digest": packet.get("semantic_digest"),
        "observed_at": observed_at,
        "standing": "PROCESS_LOCAL_OBSERVED_CORRELATION_ONLY",
    }


def _observation(
    packet_id: str,
    rows: Mapping[str, Mapping[str, Any]],
    *,
    selected_id: str | None = None,
    replay: bool = False,
) -> dict[str, Any]:
    ids = sorted(rows)
    if not ids:
        status = "UNOBSERVED_PROCESS_LOCAL_CORRELATION"
        standing = "NO_PROCESS_LOCAL_SOURCE_CORRELATION"
    elif len(ids) > 1:
        status = "AMBIGUOUS_CORRELATION_HOLD"
        standing = "MULTIPLE_SOURCE_CORRELATIONS_PRESERVED_NOT_COLLAPSED"
    elif replay:
        status = "EXACT_CORRELATION_REPLAY"
        standing = "FIRST_OBSERVATION_REUSED_IDEMPOTENTLY"
    else:
        status = "CORRELATED_PROCESS_LOCAL"
        standing = "ONE_PROCESS_LOCAL_SOURCE_CORRELATION_OBSERVED"
    selected = rows.get(selected_id) if selected_id else (rows.get(ids[0]) if len(ids) == 1 else None)
    return {
        "artifact": "ATHENA.LIMINAL.SYNAPSE.INGRESS.CORRELATION.OBSERVATION.V1",
        "status": status,
        "packet_id": packet_id,
        "correlation_count": len(ids),
        "correlation_ids": ids,
        "correlation_id": selected.get("correlation_id") if selected else None,
        "source_event_id": selected.get("source_event_id") if selected else None,
        "record_digest": _digest(selected) if selected else None,
        "standing": standing,
        "durable": False,
        "laws": list(LAWS),
    }


def record_ingress_correlation(
    server: Any,
    envelope: Mapping[str, Any],
    emitted: Mapping[str, Any],
    *,
    agent_id: str,
    observed_at: str,
) -> dict[str, Any]:
    """Record one successful ingress mapping without overwriting contradictions."""
    correlation_id, record = _record_from_ingress(
        envelope,
        emitted,
        agent_id=agent_id,
        observed_at=observed_at,
    )
    packet_id = record["local_packet_id"]
    lock, ledger = _ledger(server)
    with lock:
        bucket = ledger.setdefault(packet_id, {})
        replay = correlation_id in bucket
        if not replay:
            bucket[correlation_id] = record
        return _observation(packet_id, bucket, selected_id=correlation_id, replay=replay)


def ingress_correlation_snapshot(server: Any, packet_id: str) -> dict[str, Any]:
    packet_id = _required(packet_id, "local packet_id")
    lock, ledger = _ledger(server)
    with lock:
        bucket = deepcopy(ledger.get(packet_id) or {})
    return _observation(packet_id, bucket)


def _unique_record(server: Any, packet_id: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    packet_id = _required(packet_id, "local packet_id")
    lock, ledger = _ledger(server)
    with lock:
        bucket = deepcopy(ledger.get(packet_id) or {})
    observation = _observation(packet_id, bucket)
    if len(bucket) != 1:
        return observation, None
    return observation, next(iter(bucket.values()))


def correlation_envelope(record: Mapping[str, Any], *, source_revision: str) -> dict[str, Any]:
    """Project one frozen process-local mapping as a sibling Synapse observation."""
    if record.get("artifact") != ARTIFACT or record.get("version") != VERSION:
        raise ValueError("unsupported ingress correlation record")
    source_revision = _required(source_revision, "source_revision")
    correlation_id = _required(record.get("correlation_id"), "correlation_id")
    local_packet_id = _required(record.get("local_packet_id"), "local packet_id")
    source_event_id = _required(record.get("source_event_id"), "source event_id")
    agent_id = _required(record.get("local_agent_id"), "local agent_id")
    observed_at = _required(record.get("observed_at"), "correlation observed_at")
    body = deepcopy(dict(record))
    body_digest = _digest(body)
    return_token = f"liminal-ingress-correlation:{body_digest}"
    origin = _origin(
        correlation_id,
        source_revision,
        native_system=CORRELATION_NATIVE_SYSTEM,
        actor_id=agent_id,
    )
    envelope = {
        "schema": "ATHENA.SYNAPSE.ENVELOPE.V1",
        "event_id": _bridge_id(origin, CORRELATION_PROFILE),
        "event_type": "OBSERVATION",
        "subject": _required(record.get("source_subject"), "source subject"),
        "projection": {
            "profile": CORRELATION_PROFILE,
            "loss_class": "LOSSLESS",
            "preserved": sorted(body),
            "lost": [],
            "return_token": return_token,
        },
        "origin": origin,
        "semantics": {
            "epistemic_class": "OBS",
            "authority_class": AUTHORITY_CLASS,
            "truth_ceiling": TRUTH_CEILING,
            "native_kind": "SYNAPSE_INGRESS_CORRELATION",
            "evidence_ceiling": "PROCESS_LOCAL_CORRELATION_STATE_ONLY",
        },
        "routing": {
            "return_routes": sorted(set([LIMINAL_RESOURCE, *list(record.get("source_return_routes") or [])])),
            "recipients": [],
            "route_keys": sorted({f"synapse:{source_event_id}", f"liminal:{local_packet_id}"}),
            "visibility": "COLONY",
        },
        "causality": {
            "parent_ids": sorted({source_event_id, _packet_bridge_id(local_packet_id, source_revision)}),
            "reply_to": source_event_id,
            "correction_of": None,
            "retraction_of": None,
            "supersedes": [],
        },
        "frontier": {
            "semantics": "NATIVE_SNAPSHOT",
            "native_digest": body_digest,
            "native_ref": return_token,
        },
        "clock": {
            "wall_time": observed_at,
            "bridge_observed_at": observed_at,
            "origin_sequence": None,
        },
        "payload": {
            "summary": f"Observed Synapse ingress {source_event_id} -> {local_packet_id}",
            "payload_ref": return_token,
            "body": body,
            "body_digest": body_digest,
            "evidence": sorted({
                _required(record.get("source_envelope_digest"), "source envelope digest"),
                f"synapse:{source_event_id}",
                f"liminal:{local_packet_id}",
            }),
            "residuals": [
                "PROCESS_LOCAL_MAPPING_LOST_ON_RESTART_UNLESS_SEPARATELY_PERSISTED",
                "CORRELATION_EVENT_DOES_NOT_MUTATE_CANONICAL_PACKET_OR_RECEIPT_ENVELOPE",
                "CORRELATION != DELIVERY != CONSUMPTION != INCORPORATION",
                *LAWS,
            ],
        },
        "receipt": None,
    }
    _validate_envelope(envelope)
    return envelope


def attach_ingress_correlation(
    server: Any,
    *,
    packet_id: str,
    source_revision: str,
    export_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Attach a sibling correlation event while preserving the canonical export."""
    result = deepcopy(dict(export_result))
    native_envelope = result.get("envelope")
    native_digest_before = _digest(native_envelope) if isinstance(native_envelope, Mapping) else None
    observation, record = _unique_record(server, packet_id)
    result["source_correlation"] = observation
    result["correlation_envelope"] = (
        correlation_envelope(record, source_revision=source_revision) if record is not None else None
    )
    if native_digest_before is not None and _digest(result.get("envelope")) != native_digest_before:
        raise AssertionError("CORRELATION_ATTACHMENT_MUTATED_CANONICAL_EXPORT_HOLD")
    result["correlation_law"] = "CANONICAL_EXPORT_IDENTITY_PRESERVED_CORRELATION_IS_SIBLING_EVENT"
    return result


__all__ = [
    "ARTIFACT",
    "AUTHORITY_CLASS",
    "CORRELATION_PROFILE",
    "TRUTH_CEILING",
    "attach_ingress_correlation",
    "correlation_envelope",
    "ingress_correlation_snapshot",
    "record_ingress_correlation",
]
