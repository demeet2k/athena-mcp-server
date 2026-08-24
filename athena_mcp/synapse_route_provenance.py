from __future__ import annotations

"""Typed Liminal route-provenance projection across ATHENA Synapse envelopes.

This adapter is additive around the already-qualified Synapse Liminal bridge. It
preserves typed native route references as auxiliary routing metadata while the
private Liminal route index remains intentionally unexported. On ingress, typed
refs are admitted only when their provenance digest exactly reconstructs from the
origin native packet id, typed refs and flattened route-key set.

Integrity here is not trust or authority: a valid provenance digest proves only
internal consistency of the projected routing metadata.
"""

import hashlib
import json
from typing import Any, Mapping

from .liminal_route_provenance import ALL_REF_FIELDS, CAPABILITY_REF_FIELDS, ROUTE_REF_FIELDS

VERSION = "SYNAPSE.LIMINAL.ROUTE.PROVENANCE.1"
ARTIFACT = "ATHENA.SYNAPSE.LIMINAL.ROUTE.PROVENANCE.V1.CANDIDATE"

_PREFIX = {
    "work_refs": "work",
    "object_refs": "object",
    "dependency_refs": "dep",
    "causal_refs": "causal",
    "semantic_tags": "sem",
    "kc_refs": "kc",
    "party_refs": "party",
}

LAWS = [
    "TYPED_ROUTE_PROVENANCE != PACKET_OR_OBJECT_IDENTITY",
    "ROUTE_PROVENANCE_DIGEST != SIGNATURE_TRUST_OR_AUTHORITY",
    "PRIVATE_LIMINAL_ROUTE_INDEX_NOT_EXPORTED",
    "TYPED_ROUTE_BASIS_PRESERVED_ACROSS_PROJECTION",
    "INGRESS_PRESERVES_NATIVE_ROUTE_REFS_AS_NONAUTHORITATIVE_METADATA",
    "TAMPERED_ROUTE_PROVENANCE => INGRESS_HOLD",
    "ROUTE_PROVENANCE_PRESERVATION != DELIVERY_CONSUMPTION_OR_EXECUTION",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _names(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _typed_refs(capsule: Mapping[str, Any]) -> dict[str, list[str]]:
    return {field: _names(capsule.get(field)) for field in ALL_REF_FIELDS}


def _route_keys(typed: Mapping[str, list[str]]) -> list[str]:
    keys: set[str] = set()
    for field in ROUTE_REF_FIELDS:
        prefix = _PREFIX[field]
        for raw in typed.get(field) or []:
            atom = " ".join(str(raw).strip().casefold().split())
            if atom:
                keys.add(f"{prefix}:{atom}")
    for field in CAPABILITY_REF_FIELDS:
        for raw in typed.get(field) or []:
            atom = " ".join(str(raw).strip().casefold().split())
            if atom:
                keys.add(f"cap:{atom}")
    return sorted(keys)


def _provenance_digest(packet_id: str, typed: Mapping[str, list[str]], route_keys: list[str]) -> str:
    return _digest({
        "packet_id": str(packet_id),
        "typed_refs": {field: list(typed.get(field) or []) for field in ALL_REF_FIELDS},
        "native_route_keys": sorted(route_keys),
    })


def _merge(left: Any, right: Any) -> list[str]:
    out, seen = [], set()
    for raw in [*(left or []), *(right or [])]:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return sorted(out)


def install_synapse_route_provenance() -> None:
    from . import synapse_liminal_adapter as adapter
    from . import synapse_liminal_extension as extension

    if getattr(adapter, "_athena_synapse_route_provenance_v1_registered", False):
        return

    previous_export = adapter.liminal_capsule_to_synapse
    previous_plan = adapter.synapse_to_liminal_ingress_plan

    def export_with_route_provenance(
        capsule: Mapping[str, Any],
        *,
        source_revision: str,
        bridge_observed_at: str,
    ) -> dict[str, Any]:
        envelope = previous_export(
            capsule,
            source_revision=source_revision,
            bridge_observed_at=bridge_observed_at,
        )
        typed = _typed_refs(capsule)
        route_keys = _route_keys(typed)
        native = capsule.get("route_provenance")
        native = dict(native) if isinstance(native, Mapping) else {}
        digest = str(native.get("digest") or "").strip() or None
        if digest:
            expected = _provenance_digest(str(capsule.get("packet_id") or ""), typed, route_keys)
            if digest != expected:
                raise adapter.SynapseLiminalError(
                    "SYNAPSE_ROUTE_PROVENANCE_SOURCE_MISMATCH_HOLD: native typed route provenance does not roundtrip"
                )

        value = dict(envelope)
        projection = dict(value["projection"])
        preserved = list(projection.get("preserved") or [])
        for field in [*ALL_REF_FIELDS, "route_provenance"]:
            if field not in preserved:
                preserved.append(field)
        projection["preserved"] = preserved
        value["projection"] = projection

        routing = dict(value["routing"])
        routing["route_keys"] = route_keys
        routing["native_route_refs"] = typed
        routing["route_provenance"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "digest": digest,
            "standing": native.get("standing") or "UNOBSERVED",
            "private_route_index_exported": False,
            "typed_route_basis_preserved": True,
            "integrity_authority": "INTERNAL_CONSISTENCY_ONLY",
            "laws": list(LAWS),
        }
        value["routing"] = routing

        payload = dict(value["payload"])
        residuals = list(payload.get("residuals") or [])
        marker = "PRIVATE_ROUTE_INDEX_OMITTED_TYPED_ROUTE_BASIS_PRESERVED"
        if marker not in residuals:
            residuals.append(marker)
        payload["residuals"] = residuals
        value["payload"] = payload
        adapter._validate_envelope(value)
        return value

    def plan_with_route_provenance(envelope: Mapping[str, Any], *, agent_id: str) -> dict[str, Any]:
        plan = previous_plan(envelope, agent_id=agent_id)
        routing = envelope.get("routing") if isinstance(envelope, Mapping) else None
        native = routing.get("native_route_refs") if isinstance(routing, Mapping) else None
        if native is None:
            return plan
        if not isinstance(native, Mapping):
            raise adapter.SynapseLiminalError("routing.native_route_refs must be an object")
        unknown = sorted(set(native) - set(ALL_REF_FIELDS))
        if unknown:
            raise adapter.SynapseLiminalError(
                "SYNAPSE_ROUTE_PROVENANCE_UNKNOWN_FIELD_HOLD: " + ",".join(unknown)
            )
        typed = {field: _names(native.get(field)) for field in ALL_REF_FIELDS}
        route_keys = _names(routing.get("route_keys"))
        expected_keys = _route_keys(typed)
        if route_keys != expected_keys:
            raise adapter.SynapseLiminalError(
                "SYNAPSE_ROUTE_PROVENANCE_ROUTE_KEY_MISMATCH_HOLD"
            )

        provenance = routing.get("route_provenance")
        if not isinstance(provenance, Mapping) or not str(provenance.get("digest") or "").strip():
            raise adapter.SynapseLiminalError(
                "SYNAPSE_ROUTE_PROVENANCE_DIGEST_REQUIRED_HOLD"
            )
        expected_digest = _provenance_digest(
            str((envelope.get("origin") or {}).get("native_event_id") or ""),
            typed,
            route_keys,
        )
        if str(provenance.get("digest")) != expected_digest:
            raise adapter.SynapseLiminalError(
                "SYNAPSE_ROUTE_PROVENANCE_DIGEST_MISMATCH_HOLD"
            )

        value = dict(plan)
        emit_args = dict(value["emit_args"])
        for field in ROUTE_REF_FIELDS:
            emit_args[field] = _merge(typed[field], emit_args.get(field) or [])
        for field in CAPABILITY_REF_FIELDS:
            emit_args[field] = _merge(typed[field], emit_args.get(field) or [])
        value["emit_args"] = emit_args

        residuals = list(value.get("residuals") or [])
        residual = "TYPED_NATIVE_ROUTE_PROVENANCE_PRESERVED_AS_NONAUTHORITATIVE_INGRESS_METADATA"
        if residual not in residuals:
            residuals.append(residual)
        value["residuals"] = residuals
        laws = list(value.get("laws") or [])
        for law in LAWS:
            if law not in laws:
                laws.append(law)
        value["laws"] = laws
        value["route_provenance"] = {
            "artifact": ARTIFACT,
            "version": VERSION,
            "source_digest": expected_digest,
            "typed_refs": typed,
            "route_keys": route_keys,
            "ingress_effect": "PRESERVED_PLUS_EXISTING_SYNTHETIC_SYNAPSE_REFS",
            "authority": "NONE",
        }
        return value

    adapter.liminal_capsule_to_synapse = export_with_route_provenance
    adapter.synapse_to_liminal_ingress_plan = plan_with_route_provenance
    # synapse_liminal_extension imported the functions by name, so update those
    # bound references as part of the same installation transaction.
    extension.liminal_capsule_to_synapse = export_with_route_provenance
    extension.synapse_to_liminal_ingress_plan = plan_with_route_provenance
    adapter._athena_synapse_route_provenance_v1_registered = True


__all__ = ["VERSION", "ARTIFACT", "LAWS", "install_synapse_route_provenance"]
