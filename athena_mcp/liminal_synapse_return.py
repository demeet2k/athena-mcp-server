from __future__ import annotations

"""Causal bridge-receipt and propagation guard for the Liminal Beacon Mesh.

This extension is deliberately additive: the existing liminal mesh remains the
routing plane and Message Board/Cohesion remain the durable authorities. The
extension closes one semantic gap between those planes:

* a successful durable bridge receives an addressable bridge-receipt token;
* repeated bridge calls in one live mesh are idempotent;
* PROPAGATED cannot be asserted without an explicit propagation reference;
* bridge-receipt propagation references must resolve to a successful bridge
  receipt for the same packet;
* state/manifest expose bridge receipts without promoting them to truth.

A bridge receipt proves only that the transport returned success. It does not
prove that another agent consumed, incorporated, propagated, or benefited from
the packet.

The token name is intentionally distinct from ATHENA.SYNAPSE.ENVELOPE.V1's
`projection.return_token`, which is a projection return route/resource rather
than a local durable-bridge receipt identity.
"""

import hashlib
import json
import time
from typing import Any

VERSION = "LIMINAL.SYNAPSE.RETURN.1"
ARTIFACT = "ATHENA.LIMINAL.SYNAPSE.RETURN.V1.CANDIDATE"
BRIDGE_RECEIPT_REF_PREFIX = "bridge-receipt:"

LAWS = [
    "BRIDGE_SUCCESS => ADDRESSABLE_BRIDGE_RECEIPT_TOKEN",
    "BRIDGE_RECEIPT_TOKEN != SYNAPSE_PROJECTION_RETURN_TOKEN",
    "BRIDGE_RETRY_SAME_LIVE_PACKET_DESTINATION => IDEMPOTENT_RETURN",
    "PROPAGATED_REQUIRES_EXPLICIT_PROPAGATION_REF",
    "BRIDGE_RECEIPT_REF_MUST_RESOLVE_FOR_SAME_PACKET",
    "BRIDGE_RETURN != DELIVERY != CONSUMPTION != INCORPORATION != PROPAGATION != OUTCOME_IMPROVEMENT",
    "EPHEMERAL_BRIDGE_RECEIPT != CROSS_RESTART_DURABLE_DEDUPLICATION",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _resolved_kind(runtime: Any, packet_id: str, bridge_kind: str) -> str:
    kind = str(bridge_kind or "AUTO").upper()
    if kind != "AUTO":
        return kind
    packet = getattr(runtime, "_packets", {}).get(packet_id) or {}
    return "COHESION" if packet.get("message_class") in {"NEED", "OFFER"} else "MESSAGE_BOARD"


def _bridge_key(packet_id: str, bridge_kind: str, remote: str, role: str | None, allow_collaboration: bool) -> tuple[str, str, str, str, bool]:
    return (
        str(packet_id),
        str(bridge_kind).upper(),
        str(remote or "origin"),
        str(role or ""),
        bool(allow_collaboration),
    )


def _durable_refs(result: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    bridge_result = result.get("bridge_result") if isinstance(result, dict) else None
    if not isinstance(bridge_result, dict):
        return refs

    message_event = bridge_result.get("message_event")
    if isinstance(message_event, dict) and message_event.get("event_id"):
        refs.append(f"message-board:{message_event['event_id']}")

    for key, prefix in (
        ("request_id", "cohesion"),
        ("offer_id", "cohesion"),
        ("match_id", "cohesion"),
        ("event_id", "event"),
        ("eid", "event"),
        ("head", "git"),
        ("git_head", "git"),
    ):
        value = bridge_result.get(key)
        if value not in (None, ""):
            refs.append(f"{prefix}:{value}")

    git = bridge_result.get("git")
    if isinstance(git, dict) and git.get("head"):
        refs.append(f"git:{git['head']}")
    publish = bridge_result.get("remote_publish")
    if isinstance(publish, dict) and publish.get("remote_head"):
        refs.append(f"git-remote:{publish['remote_head']}")

    return sorted(set(refs))


def _ledger(runtime: Any) -> dict[tuple[str, str, str, str, bool], dict[str, Any]]:
    value = getattr(runtime, "_synapse_return_ledger_v1", None)
    if value is None:
        value = {}
        runtime._synapse_return_ledger_v1 = value
    return value


def _packet_bridge_receipts(runtime: Any, packet_id: str) -> list[dict[str, Any]]:
    return [
        dict(receipt)
        for key, receipt in _ledger(runtime).items()
        if key[0] == str(packet_id) and receipt.get("status") == "BRIDGED"
    ]


def _validate_bridge_receipt_refs(runtime: Any, packet_id: str, refs: list[str]) -> None:
    requested = {
        ref[len(BRIDGE_RECEIPT_REF_PREFIX):]
        for ref in refs
        if ref.startswith(BRIDGE_RECEIPT_REF_PREFIX) and ref[len(BRIDGE_RECEIPT_REF_PREFIX):]
    }
    if not requested:
        return
    valid = {
        str(row.get("bridge_receipt_id"))
        for row in _packet_bridge_receipts(runtime, packet_id)
        if row.get("bridge_receipt_id")
    }
    missing = sorted(requested - valid)
    if missing:
        raise ValueError(
            "PROPAGATION_BRIDGE_RECEIPT_HOLD: bridge-receipt ref does not resolve to a successful bridge for this packet: "
            + ",".join(missing)
        )


def install_liminal_synapse_return(runtime_cls: type) -> None:
    """Install once on a LiminalBeaconMeshRuntime-compatible class."""

    if getattr(runtime_cls, "_athena_liminal_synapse_return_v1_registered", False):
        return

    original_manifest = runtime_cls.manifest
    original_bridge = runtime_cls.bridge
    original_receipt = runtime_cls.receipt
    original_state = runtime_cls.state

    def manifest(self):
        value = dict(original_manifest(self))
        value["synapse_return"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "standing": "CANDIDATE_ADDITIVE_GUARD",
            "bridge_receipt_persistence": "PROCESS_LOCAL_EPHEMERAL",
            "cross_restart_deduplication": False,
            "bridge_receipt_ref_prefix": BRIDGE_RECEIPT_REF_PREFIX,
            "synapse_projection_return_token_semantics": "DISTINCT_RETURN_ROUTE_RESOURCE",
            "laws": list(LAWS),
        }
        return value

    def bridge(
        self,
        packet_id: str,
        bridge_kind: str = "AUTO",
        remote: str = "origin",
        allow_collaboration: bool = False,
        role: str | None = None,
    ):
        resolved = _resolved_kind(self, packet_id, bridge_kind)
        key = _bridge_key(packet_id, resolved, remote, role, allow_collaboration)
        ledger = _ledger(self)
        previous = ledger.get(key)
        if previous and previous.get("status") == "BRIDGED":
            return {
                "status": "ALREADY_BRIDGED",
                "bridge_kind": resolved,
                "packet_id": packet_id,
                "bridge_receipt": dict(previous),
                "durable_refs": list(previous.get("durable_refs") or []),
                "bridge_receipt_token": previous.get("bridge_receipt_id"),
                "idempotent": True,
                "law": "BRIDGE_RETRY_SAME_LIVE_PACKET_DESTINATION => IDEMPOTENT_RETURN",
            }

        result = original_bridge(
            self,
            packet_id=packet_id,
            bridge_kind=resolved,
            remote=remote,
            allow_collaboration=allow_collaboration,
            role=role,
        )
        if not isinstance(result, dict) or result.get("status") != "BRIDGED":
            return result

        refs = _durable_refs(result)
        basis = {
            "packet_id": str(packet_id),
            "bridge_kind": resolved,
            "remote": str(remote or "origin"),
            "role": str(role or ""),
            "allow_collaboration": bool(allow_collaboration),
            "durable_refs": refs,
        }
        receipt = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "bridge_receipt_id": "LSR." + _digest(basis)[:32],
            "status": "BRIDGED",
            **basis,
            "observed_at": float(getattr(self, "_now", time.time)()),
            "evidence_ceiling": "TRANSPORT_SUCCESS_ONLY",
            "law": "BRIDGE_RETURN != DELIVERY != CONSUMPTION != INCORPORATION != PROPAGATION",
        }
        ledger[key] = receipt
        enriched = dict(result)
        enriched["bridge_receipt"] = dict(receipt)
        enriched["durable_refs"] = list(refs)
        enriched["bridge_receipt_token"] = receipt["bridge_receipt_id"]
        return enriched

    def receipt(
        self,
        agent_id: str,
        packet_id: str,
        stage: str,
        *,
        disposition: str | None = None,
        consumer_ref: str | None = None,
        residual: str | None = None,
        propagation_refs=None,
        outcome_ref: str | None = None,
    ):
        stage_upper = str(stage or "").upper()
        refs = [str(x).strip() for x in (propagation_refs or []) if str(x).strip()]
        if stage_upper == "PROPAGATED":
            if not refs:
                raise ValueError(
                    "PROPAGATION_EVIDENCE_HOLD: PROPAGATED requires at least one explicit propagation_ref"
                )
            _validate_bridge_receipt_refs(self, packet_id, refs)
        value = original_receipt(
            self,
            agent_id=agent_id,
            packet_id=packet_id,
            stage=stage,
            disposition=disposition,
            consumer_ref=consumer_ref,
            residual=residual,
            propagation_refs=refs,
            outcome_ref=outcome_ref,
        )
        if stage_upper == "PROPAGATED" and isinstance(value, dict):
            value = dict(value)
            value["propagation_witness_refs"] = refs
        return value

    def state(self, agent_id: str | None = None, include_packets: bool = False, limit: int = 50):
        value = dict(original_state(self, agent_id=agent_id, include_packets=include_packets, limit=limit))
        receipts = list(_ledger(self).values())
        receipts.sort(key=lambda x: (float(x.get("observed_at") or 0), str(x.get("bridge_receipt_id"))), reverse=True)
        cap = max(1, min(int(limit or 50), 200))
        value["synapse_return"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "bridge_receipt_count": len(receipts),
            "bridge_receipts": [dict(row) for row in receipts[:cap]],
            "cross_restart_deduplication": False,
            "bridge_receipt_ref_prefix": BRIDGE_RECEIPT_REF_PREFIX,
            "synapse_projection_return_token_semantics": "DISTINCT_RETURN_ROUTE_RESOURCE",
            "laws": list(LAWS),
        }
        return value

    runtime_cls.manifest = manifest
    runtime_cls.bridge = bridge
    runtime_cls.receipt = receipt
    runtime_cls.state = state
    runtime_cls._athena_liminal_synapse_return_v1_registered = True


__all__ = [
    "VERSION",
    "ARTIFACT",
    "BRIDGE_RECEIPT_REF_PREFIX",
    "LAWS",
    "install_liminal_synapse_return",
]
