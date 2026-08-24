from __future__ import annotations

"""Typed auxiliary route provenance for Liminal Beacon packets.

The native mesh already routes on work/object/dependency/causal/semantic/KC/
party/capability atoms, but historically retained only the flattened private
`_route_keys` on emitted packets. Public capsules therefore lost the typed
coordinates that caused rendezvous.

This extension preserves the exact typed route basis as AUXILIARY metadata after
native packet identity and route indexing have already been computed. It does
not add any field to the packet identity basis, sender sequence, Lamport clock,
semantic digest, routing score, receipt ladder, or authority model.
"""

import hashlib
import json
from typing import Any

from . import liminal_beacon_mesh as mesh

VERSION = "LIMINAL.ROUTE.PROVENANCE.1"
ARTIFACT = "ATHENA.LIMINAL.ROUTE.PROVENANCE.V1.CANDIDATE"

ROUTE_REF_FIELDS = tuple(mesh._ROUTE_FIELDS)
CAPABILITY_REF_FIELDS = tuple(mesh._CAP_FIELDS)
ALL_REF_FIELDS = ROUTE_REF_FIELDS + CAPABILITY_REF_FIELDS

LAWS = [
    "TYPED_ROUTE_PROVENANCE != PACKET_IDENTITY",
    "TYPED_ROUTE_PROVENANCE != OBJECT_IDENTITY_OR_TRUTH",
    "ROUTE_PROVENANCE_DIGEST != SEMANTIC_DIGEST",
    "PRIVATE_ROUTE_INDEX_CAN_BE_LOST_WHEN_TYPED_ROUTE_BASIS_IS_PRESERVED",
    "PROVENANCE_INJECTION_REQUIRES_EXACT_ROUTE_KEY_ROUNDTRIP",
    "ROUTING_METADATA_PRESERVATION != DELIVERY_CONSUMPTION_OR_AUTHORITY",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _typed_basis(sender: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, list[str]]:
    basis: dict[str, list[str]] = {}
    for field in ROUTE_REF_FIELDS:
        basis[field] = mesh._names(kwargs.get(field)) or list(sender.get(field) or [])
    for field in CAPABILITY_REF_FIELDS:
        basis[field] = mesh._names(kwargs.get(field)) or list(sender.get(field) or [])
    return basis


def _public_route_provenance(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": ARTIFACT,
        "version": VERSION,
        "standing": row.get("route_provenance_standing") or "UNOBSERVED",
        "digest": row.get("route_provenance_digest"),
        "identity_effect": "NONE_AUXILIARY_METADATA_ONLY",
        "typed_refs": {field: list(row.get(field) or []) for field in ALL_REF_FIELDS},
        "laws": list(LAWS),
    }


def install_liminal_route_provenance(runtime_cls: type) -> None:
    if getattr(runtime_cls, "_athena_liminal_route_provenance_v1_registered", False):
        return

    previous_emit = runtime_cls.emit
    previous_manifest = runtime_cls.manifest
    previous_capsule = mesh._packet_capsule

    def route_aware_capsule(row: dict[str, Any], score: float | None = None) -> dict[str, Any]:
        value = dict(previous_capsule(row, score))
        for field in ALL_REF_FIELDS:
            value[field] = list(row.get(field) or [])
        value["route_provenance"] = _public_route_provenance(row)
        return value

    # Class methods resolve the module global at call time, and the Synapse
    # adapter imports this function only after this installer runs in package
    # boot. One wrapper therefore covers emit/rendezvous/state/export capsules.
    mesh._packet_capsule = route_aware_capsule

    def emit_with_route_provenance(self, agent_id: str, message_class: str, summary: str, **kwargs):
        agent_id = str(agent_id or "").strip()
        with self._lock:
            sender = self._presence.get(agent_id) or {}
            typed = _typed_basis(sender, kwargs)
            result = previous_emit(
                self,
                agent_id=agent_id,
                message_class=message_class,
                summary=summary,
                **kwargs,
            )
            if not isinstance(result, dict):
                return result
            capsule = result.get("packet")
            packet_id = str((capsule or {}).get("packet_id") or "")
            row = self._packets.get(packet_id)
            if not row:
                return result

            expected_route_keys = sorted(mesh._route_keys(typed))
            native_route_keys = sorted(row.get("_route_keys") or [])
            if expected_route_keys != native_route_keys:
                row["route_provenance_standing"] = "ROUTE_KEY_ROUNDTRIP_MISMATCH_HOLD"
                row["route_provenance_digest"] = None
                enriched = dict(result)
                enriched["packet"] = route_aware_capsule(row)
                enriched["route_provenance_status"] = "ROUTE_KEY_ROUNDTRIP_MISMATCH_HOLD"
                enriched["route_provenance_mismatch"] = {
                    "expected": expected_route_keys,
                    "native": native_route_keys,
                }
                return enriched

            basis = {
                "packet_id": packet_id,
                "typed_refs": typed,
                "native_route_keys": native_route_keys,
            }
            provenance_digest = _digest(basis)
            for field, values in typed.items():
                row[field] = list(values)
            row["route_provenance_version"] = VERSION
            row["route_provenance_digest"] = provenance_digest
            row["route_provenance_standing"] = "TYPED_ROUTE_BASIS_PRESERVED_AUXILIARY"

            enriched = dict(result)
            enriched["packet"] = route_aware_capsule(row)
            enriched["route_provenance_status"] = "PRESERVED_AUXILIARY"
            enriched["route_provenance_digest"] = provenance_digest
            enriched["route_provenance_identity_effect"] = "NONE"
            return enriched

    def manifest_with_route_provenance(self):
        value = dict(previous_manifest(self))
        value["route_provenance"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "standing": "CANDIDATE_AUXILIARY_TYPED_ROUTE_PROVENANCE",
            "typed_fields": list(ALL_REF_FIELDS),
            "packet_identity_effect": "NONE",
            "routing_score_effect": "NONE",
            "receipt_effect": "NONE",
            "laws": list(LAWS),
        }
        return value

    runtime_cls.emit = emit_with_route_provenance
    runtime_cls.manifest = manifest_with_route_provenance
    runtime_cls._athena_liminal_route_provenance_v1_registered = True


__all__ = [
    "VERSION",
    "ARTIFACT",
    "ROUTE_REF_FIELDS",
    "CAPABILITY_REF_FIELDS",
    "ALL_REF_FIELDS",
    "LAWS",
    "install_liminal_route_provenance",
]
