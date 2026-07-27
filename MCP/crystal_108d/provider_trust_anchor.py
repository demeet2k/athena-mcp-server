"""KC144 W18 provider-adapter trust-anchor and witness-return gate.

W18 adds a real detached-Ed25519 verification path, but the production
registry is intentionally empty.  A caller cannot supply a public key and
promote it to a trust anchor: only an adapter pinned in the repository
snapshot can verify a provider return.  The runtime remains non-networked,
nondispatching, secret-free, and nonpromotional.
"""

from __future__ import annotations

import base64
import binascii
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .evidence_provenance_gate import FrozenEvidenceProvenanceGate
from .replay_authority_ledger import (
    WITNESS_PLAN,
    _assert_secret_free,
    _bounded_text,
    _digest,
    _exact_object,
    _parsed_timestamp,
    _timestamp,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w18_provider_trust_registry.json"
SCHEMA = "athena.xnav-w18-provider-adapter-trust-anchor/v1"
PHASE = "KC144.XNAV.W18"
REGISTRY_SCHEMA = "athena.provider-trust-registry/v1"
ADAPTER_PROTOCOL = "athena.provider-adapter/ed25519-detached/v1"
RETURN_SCHEMA = "athena.provider-signed-return/v1"
SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")

RETURN_FIELDS = {
    "schema",
    "adapter_id",
    "provider_id",
    "account_scope",
    "environment",
    "evidence_origin",
    "activation_packet_digest",
    "provider_evidence_digest",
    "provenance_witness_digest",
    "authorization_ref",
    "observed_at",
    "signature",
}
SIGNATURE_FIELDS = {"algorithm", "key_id", "value"}
ADAPTER_FIELDS = {
    "adapter_id",
    "provider_id",
    "account_scope",
    "environment",
    "evidence_origin",
    "verification_method",
    "attests_authorization",
    "trust_anchor",
    "admission",
}
ANCHOR_FIELDS = {
    "kind",
    "key_id",
    "public_key_base64",
    "fingerprint",
}
ADMISSION_FIELDS = {"authority", "reference", "admitted_at", "commit"}


class ProviderTrustAnchorError(RuntimeError):
    """Raised when the frozen W18 registry or a provider return is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProviderTrustAnchorError(f"{path.name} must contain an object")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _origin(value: Any, field: str) -> str:
    text = _bounded_text(value, field)
    parsed = urlsplit(text)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError(f"{field} must be an HTTPS origin without path or credentials")
    host = parsed.hostname.lower()
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return f"https://{host}"


def _url_origin(value: Any, field: str) -> str:
    text = _bounded_text(value, field)
    parsed = urlsplit(text)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(f"{field} must be an HTTPS URL without credentials")
    host = parsed.hostname.lower()
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return f"https://{host}"


def _decode_base64(value: Any, field: str, expected_length: int) -> bytes:
    text = _bounded_text(value, field)
    try:
        decoded = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError(f"{field} must be canonical base64") from error
    if len(decoded) != expected_length:
        raise ValueError(f"{field} must decode to {expected_length} bytes")
    if base64.b64encode(decoded).decode("ascii") != text:
        raise ValueError(f"{field} must use canonical padded base64")
    return decoded


def _verify_ed25519_signature(
    public_key_base64: str,
    signature_base64: str,
    material: dict[str, Any],
) -> bool:
    """Verify an exact canonical-JSON return with a detached Ed25519 signature."""
    public_key = _decode_base64(public_key_base64, "public_key_base64", 32)
    signature = _decode_base64(signature_base64, "signature.value", 64)
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, _canonical_bytes(material)
        )
    except InvalidSignature:
        return False
    return True


def _signature_material(provider_return: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(value)
        for key, value in provider_return.items()
        if key != "signature"
    }


class FrozenProviderTrustRegistry:
    """Frozen W18 registry and fail-closed provider-return verifier."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        predecessor: FrozenEvidenceProvenanceGate,
        adapters: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.predecessor = predecessor
        self.adapters = adapters

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        predecessor: FrozenEvidenceProvenanceGate | None = None,
    ) -> "FrozenProviderTrustRegistry":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise ProviderTrustAnchorError("unexpected W18 schema or phase")
        predecessor = predecessor or FrozenEvidenceProvenanceGate.load()
        w17 = predecessor.status()
        expected_predecessor = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w17_head": "9ac6f97f1065280d027d13a43d8c9d68770184bd",
            "w17_schema": "athena.xnav-w17-evidence-provenance-dispatch-gate/v1",
            "w17_contract_digest": w17["contract_digest"],
            "w17_receipt_id": (
                "w17-provenance-gate:sha256:"
                "615fed4366cd2e06bc7773df8aa632f7a005c8ba25dda8728def9a59a0b95913"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise ProviderTrustAnchorError("W18 predecessor lineage mismatch")

        expected_registry = {
            "schema": REGISTRY_SCHEMA,
            "adapter_protocol": ADAPTER_PROTOCOL,
            "provider_return_schema": RETURN_SCHEMA,
            "canonicalization": "KC144.CANON.JSON.V1",
            "signature_algorithm": "ed25519",
            "signature_encoding": "base64",
            "trust_anchor_kind": "ed25519-public-key",
            "adapters": [],
        }
        if snapshot.get("trust_registry") != expected_registry:
            raise ProviderTrustAnchorError(
                "W18 production registry must remain empty until protected admission"
            )

        expected_admission = {
            "registry_is_authoritative": True,
            "self_supplied_trust_anchors_allowed": False,
            "provider_specific_adapter_required": True,
            "exact_provider_id_required": True,
            "exact_account_scope_required": True,
            "exact_environment_required": True,
            "exact_evidence_origin_required": True,
            "exact_key_id_required": True,
            "authorization_binding_required": True,
            "production_adapter_count": 0,
            "runtime_can_mutate_registry": False,
        }
        if snapshot.get("admission_contract") != expected_admission:
            raise ProviderTrustAnchorError("W18 adapter-admission contract drift")

        expected_return = {
            "workflow_path": ".github/workflows/p10-host-readiness.yml",
            "workflow_ref_policy": "EXACT_CANDIDATE_HEAD_REQUIRED",
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "execute_live_witness_default": False,
            "provider_return_must_precede_dispatch": True,
            "runtime_dispatch_capability": "NONE",
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if snapshot.get("persistent_witness_return") != expected_return:
            raise ProviderTrustAnchorError("W18 persistent-witness contract drift")

        expected_boundaries = {
            "production_provider_adapter_admitted": False,
            "production_trust_anchor_pinned": False,
            "provider_return_signature_verified": False,
            "authorization_externally_verified": False,
            "live_provider_fetch_executed": False,
            "submitted_inputs_persisted": False,
            "secret_material_accepted": False,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise ProviderTrustAnchorError("W18 boundaries must all remain false")
        if snapshot.get("successor") != (
            "KC144.XNAV.W19::AUTHORIZED-PROVIDER-ADAPTER-ADMISSION-"
            "AND-PERSISTENT-WITNESS-EXECUTION"
        ):
            raise ProviderTrustAnchorError("W18 successor drift")

        contract_material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(contract_material):
            raise ProviderTrustAnchorError("W18 contract digest mismatch")
        return cls(snapshot, predecessor, {})

    @classmethod
    def load(
        cls, path: Path = DATA_PATH
    ) -> "FrozenProviderTrustRegistry":
        return cls.from_snapshot(_load_json(path))

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "PROVIDER_TRUST_VERIFIER_READY__"
                "PRODUCTION_ADAPTER_AND_WITNESS_RETURN_OPEN"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w17_contract_digest": self.snapshot["predecessor"][
                "w17_contract_digest"
            ],
            "adapter_protocol": ADAPTER_PROTOCOL,
            "provider_return_schema": RETURN_SCHEMA,
            "crypto_verifier": "READY_ED25519_DETACHED_CANONICAL_JSON",
            "production_adapter_count": len(self.adapters),
            "registered_adapters": [],
            "self_supplied_trust_anchors_allowed": False,
            "runtime_can_mutate_registry": False,
            "persistent_witness_return": deepcopy(
                self.snapshot["persistent_witness_return"]
            ),
            "cross_navigation_state": (
                "W17_PROVENANCE_SCHEMA_AND_W18_CRYPTO_VERIFIER_CLOSED__"
                "PROVIDER_ADMISSION_AND_PERSISTENT_WITNESS_OPEN"
            ),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "successor": self.snapshot["successor"],
        }

    def _w17_context(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> tuple[dict[str, Any], dict[str, Any]] | tuple[None, dict[str, Any]]:
        inspected = self.predecessor.inspect_provenance(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
        )
        if not inspected["status"].startswith(
            "PASS_STRUCTURAL_EVIDENCE_PROVENANCE_BINDING"
        ):
            return None, inspected
        packet = json.loads(activation_packet_json)
        evidence = json.loads(provider_evidence_json)
        provenance = json.loads(provenance_witness_json)
        context = {
            "provider_id": packet["provider"]["id"],
            "account_scope": packet["provider"]["account_scope"],
            "environment": packet["witness"]["environment"],
            "evidence_origin": _url_origin(
                evidence["evidence_url"], "evidence.evidence_url"
            ),
            "authorization_ref": packet["authorization"]["ref"],
            "provenance_verified_at": provenance["verifier"]["verified_at"],
            "provenance_trust_fingerprint": provenance["trust_anchor"][
                "fingerprint"
            ],
            "activation_packet_digest": inspected["activation_packet_digest"],
            "provider_evidence_digest": inspected["provider_evidence_digest"],
            "provenance_witness_digest": inspected["provenance_witness_digest"],
            "provenance_binding_digest": inspected["provenance_binding_digest"],
        }
        return context, inspected

    def build_provider_return_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> dict[str, Any]:
        try:
            context, inspected = self._w17_context(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            if context is None:
                return {
                    **inspected,
                    "provider_return_status": "HOLD_W17_PROVENANCE_REJECTED",
                }
            matching = [
                adapter
                for adapter in self.adapters.values()
                if adapter["provider_id"] == context["provider_id"]
                and adapter["account_scope"] == context["account_scope"]
                and adapter["environment"] == context["environment"]
                and adapter["evidence_origin"] == context["evidence_origin"]
            ]
            template = {
                "schema": RETURN_SCHEMA,
                "adapter_id": (
                    matching[0]["adapter_id"] if len(matching) == 1 else None
                ),
                "provider_id": context["provider_id"],
                "account_scope": context["account_scope"],
                "environment": context["environment"],
                "evidence_origin": context["evidence_origin"],
                "activation_packet_digest": context[
                    "activation_packet_digest"
                ],
                "provider_evidence_digest": context["provider_evidence_digest"],
                "provenance_witness_digest": context[
                    "provenance_witness_digest"
                ],
                "authorization_ref": context["authorization_ref"],
                "observed_at": None,
                "signature": {
                    "algorithm": "ed25519",
                    "key_id": (
                        matching[0]["trust_anchor"]["key_id"]
                        if len(matching) == 1
                        else None
                    ),
                    "value": None,
                },
            }
            return {
                "status": (
                    "PROVIDER_RETURN_TEMPLATE_READY"
                    if len(matching) == 1
                    else "HOLD_PROVIDER_ADAPTER_NOT_ADMITTED"
                ),
                "template": template,
                "adapter_match_count": len(matching),
                "provenance_binding_digest": context[
                    "provenance_binding_digest"
                ],
                "self_supplied_trust_anchor_field_present": False,
                "provider_return_signature_verified": False,
                "authorization_externally_verified": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def inspect_provider_return(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_return_json: str,
    ) -> dict[str, Any]:
        try:
            context, inspected = self._w17_context(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            if context is None:
                return {
                    **inspected,
                    "provider_return_status": "HOLD_W17_PROVENANCE_REJECTED",
                }
            if (
                not isinstance(provider_return_json, str)
                or len(provider_return_json) > 32768
            ):
                raise ValueError("provider return must be bounded JSON text")
            submitted = json.loads(provider_return_json)
            _assert_secret_free(submitted, "provider_return")
            value = _exact_object(submitted, RETURN_FIELDS, "provider return")
            normalized = {
                "schema": _bounded_text(value.get("schema"), "schema"),
                "adapter_id": _bounded_text(
                    value.get("adapter_id"), "adapter_id"
                ),
                "provider_id": _bounded_text(
                    value.get("provider_id"), "provider_id"
                ),
                "account_scope": _bounded_text(
                    value.get("account_scope"), "account_scope"
                ),
                "environment": _bounded_text(
                    value.get("environment"), "environment"
                ),
                "evidence_origin": _origin(
                    value.get("evidence_origin"), "evidence_origin"
                ),
                "activation_packet_digest": _bounded_text(
                    value.get("activation_packet_digest"),
                    "activation_packet_digest",
                ),
                "provider_evidence_digest": _bounded_text(
                    value.get("provider_evidence_digest"),
                    "provider_evidence_digest",
                ),
                "provenance_witness_digest": _bounded_text(
                    value.get("provenance_witness_digest"),
                    "provenance_witness_digest",
                ),
                "authorization_ref": _bounded_text(
                    value.get("authorization_ref"), "authorization_ref"
                ),
                "observed_at": _timestamp(
                    value.get("observed_at"), "observed_at"
                ),
            }
            if normalized["schema"] != RETURN_SCHEMA:
                raise ValueError(f"schema must be {RETURN_SCHEMA}")
            for field in (
                "activation_packet_digest",
                "provider_evidence_digest",
                "provenance_witness_digest",
            ):
                if not SHA256_VALUE.fullmatch(normalized[field]):
                    raise ValueError(f"{field} must be sha256:<64 hex>")
            signature = _exact_object(
                value.get("signature"), SIGNATURE_FIELDS, "signature"
            )
            normalized["signature"] = {
                "algorithm": _bounded_text(
                    signature.get("algorithm"), "signature.algorithm"
                ),
                "key_id": _bounded_text(
                    signature.get("key_id"), "signature.key_id"
                ),
                "value": _bounded_text(
                    signature.get("value"), "signature.value"
                ),
            }
            if normalized["signature"]["algorithm"] != "ed25519":
                raise ValueError("signature.algorithm must be ed25519")

            adapter = self.adapters.get(normalized["adapter_id"])
            if adapter is None:
                return self._hold(
                    "HOLD_PROVIDER_ADAPTER_NOT_ADMITTED",
                    "adapter_id is not present in the commit-pinned registry",
                    context,
                )

            expected = {
                "provider_id": context["provider_id"],
                "account_scope": context["account_scope"],
                "environment": context["environment"],
                "evidence_origin": context["evidence_origin"],
                "activation_packet_digest": context[
                    "activation_packet_digest"
                ],
                "provider_evidence_digest": context[
                    "provider_evidence_digest"
                ],
                "provenance_witness_digest": context[
                    "provenance_witness_digest"
                ],
                "authorization_ref": context["authorization_ref"],
            }
            for field, expected_value in expected.items():
                if normalized[field] != expected_value:
                    raise ValueError(f"provider return {field} binding mismatch")
            for field in (
                "provider_id",
                "account_scope",
                "environment",
                "evidence_origin",
            ):
                if normalized[field] != adapter[field]:
                    raise ValueError(f"provider adapter {field} mismatch")
            anchor = adapter["trust_anchor"]
            if normalized["signature"]["key_id"] != anchor["key_id"]:
                raise ValueError("provider return key_id mismatch")
            if (
                context["provenance_trust_fingerprint"]
                != anchor["fingerprint"]
            ):
                raise ValueError("W17 provenance trust-anchor fingerprint mismatch")
            if _parsed_timestamp(normalized["observed_at"]) < _parsed_timestamp(
                context["provenance_verified_at"]
            ):
                raise ValueError("provider return precedes provenance verification")
            if not _verify_ed25519_signature(
                anchor["public_key_base64"],
                normalized["signature"]["value"],
                _signature_material(normalized),
            ):
                raise ValueError("provider return Ed25519 signature invalid")
            return {
                "status": "PASS_PINNED_PROVIDER_RETURN_SIGNATURE",
                "provider_return_digest": _digest(normalized),
                "provenance_binding_digest": context[
                    "provenance_binding_digest"
                ],
                "adapter_id": adapter["adapter_id"],
                "trust_anchor_fingerprint": anchor["fingerprint"],
                "provider_return_signature_verified": True,
                "authorization_externally_verified": bool(
                    adapter["attests_authorization"]
                ),
                "evidence_class": "EXTERNALLY_VERIFIED_PROVIDER_EVIDENCE",
                **self._negative_boundaries(),
            }
        except (
            binascii.Error,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            return self._rejected(str(error))

    def evaluate_persistent_witness_return(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_return_json: str,
    ) -> dict[str, Any]:
        inspection = self.inspect_provider_return(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_return_json,
        )
        provider_verified = inspection["status"].startswith(
            "PASS_PINNED_PROVIDER_RETURN_SIGNATURE"
        )
        authorization_verified = bool(
            inspection.get("authorization_externally_verified")
        )
        gates = {
            "w17_provenance_structurally_valid": bool(
                inspection.get("provenance_binding_digest")
            ),
            "provider_adapter_commit_pinned": provider_verified,
            "provider_return_signature_verified": provider_verified,
            "authorization_externally_verified": authorization_verified,
            "protected_environment_approved": False,
            "bearer_secret_available_at_job_runtime": False,
            "explicit_live_witness_dispatch": False,
            "persistent_witness_returned": False,
        }
        return {
            "status": (
                "HOLD_PERSISTENT_WITNESS_RETURN__"
                "PROVIDER_ADMISSION_AND_PROTECTED_EXECUTION_OPEN"
            ),
            "provider_return_inspection": inspection,
            "gates": gates,
            "passed_gates": [name for name, passed in gates.items() if passed],
            "open_gates": [name for name, passed in gates.items() if not passed],
            "workflow": deepcopy(self.snapshot["persistent_witness_return"]),
            "required_external_transition": [
                "admit one provider-specific adapter and public trust anchor by protected commit",
                "obtain a detached provider signature over the exact W17-bound return",
                "approve the exact candidate head in p10-persistent-host",
                "provision the bearer only at protected job runtime",
                "explicitly execute and return the three-sample persistent witness",
            ],
            **self._negative_boundaries(),
        }

    @staticmethod
    def _negative_boundaries() -> dict[str, Any]:
        return {
            "submitted_inputs_persisted": False,
            "provider_evidence_fetched_by_runtime": False,
            "secret_material_accepted": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "dispatch_allowed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }

    def _hold(
        self,
        status: str,
        reason: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "error": reason,
            "provenance_binding_digest": context["provenance_binding_digest"],
            "production_adapter_count": len(self.adapters),
            "provider_return_signature_verified": False,
            "authorization_externally_verified": False,
            "evidence_class": "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM",
            **self._negative_boundaries(),
        }

    def _rejected(self, reason: str) -> dict[str, Any]:
        return {
            "status": "HOLD_PROVIDER_RETURN_REJECTED",
            "error": reason,
            "provider_return_signature_verified": False,
            "authorization_externally_verified": False,
            "evidence_class": "UNVERIFIED_EXTERNAL_ASSERTION",
            **self._negative_boundaries(),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_provider_trust_anchor(mcp: Any) -> None:
    """Register W18 provider trust and persistent-witness return surfaces."""

    registry = FrozenProviderTrustRegistry.load()

    @mcp.tool()
    def athena_w18_provider_trust_status() -> str:
        """Report the commit-pinned provider registry and remaining trust gates."""
        return _render(registry.status())

    @mcp.tool()
    def build_athena_w18_provider_return_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> str:
        """Build an exact W17-bound provider-return template without a key."""
        return _render(
            registry.build_provider_return_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w18_provider_signed_return(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_return_json: str,
    ) -> str:
        """Verify only returns signed by a commit-pinned provider adapter."""
        return _render(
            registry.inspect_provider_return(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_return_json,
            )
        )

    @mcp.tool()
    def evaluate_athena_w18_persistent_witness_return(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_return_json: str,
    ) -> str:
        """Evaluate the W18 return gate without dispatching or contacting a host."""
        return _render(
            registry.evaluate_persistent_witness_return(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_return_json,
            )
        )

    @mcp.resource("athena://w18-provider-trust-anchor")
    def provider_trust_anchor_resource() -> str:
        """Expose the frozen W18 provider-trust registry and authority holds."""
        return _render(registry.status())
