"""KC144 W18 provider-adapter and persistent-witness return contract.

W18 closes the *shape* of the external execution path.  It introduces exact,
secret-free schemas for a provider-specific adapter profile, the adapter's
trust-verification receipt, an exact-head protected-dispatch envelope, and the
three-sample persistent MCP witness returned by that dispatch.

The runtime deliberately has no provider credential, network adapter,
signature-verification trust bundle, workflow-dispatch authority, protected
secret, endpoint access, or external persistence adapter.  Consequently it can
prove structural continuity from W17 through a submitted return, but cannot
upgrade submitted signatures or assertions into externally verified authority.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .evidence_provenance_gate import FrozenEvidenceProvenanceGate
from .replay_authority_ledger import (
    IMAGE,
    RUNTIME_P09_HEAD,
    SOURCE_COMMIT,
    WITNESS_PLAN,
    _assert_secret_free,
    _bounded_text,
    _digest,
    _exact_object,
    _https_url,
    _parsed_timestamp,
    _timestamp,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w18_provider_adapter_witness_return.json"
SCHEMA = "athena.xnav-w18-provider-adapter-persistent-witness-return/v1"
PHASE = "KC144.XNAV.W18"
PROFILE_SCHEMA = "athena.provider-adapter-profile/v1"
TRUST_RECEIPT_SCHEMA = "athena.provider-trust-verification-receipt/v1"
DISPATCH_ENVELOPE_SCHEMA = "athena.protected-witness-dispatch-envelope/v1"
WITNESS_RETURN_SCHEMA = "athena.persistent-mcp-witness-return/v1"
ADMISSION_SCHEMA = "athena.persistent-witness-return-admission/v1"

SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT_VALUE = re.compile(r"^[0-9a-f]{40}$")
ADAPTER_ID = re.compile(r"^[a-z0-9][a-z0-9._/-]{2,127}$")

PROFILE_FIELDS = {
    "schema",
    "provider_id",
    "adapter",
    "identity_binding",
    "trust_anchor",
    "authorization_binding",
    "capabilities",
    "secret_material_recorded",
    "profile_digest",
}
ADAPTER_FIELDS = {
    "id",
    "version",
    "kind",
    "retrieval_mode",
    "verification_method",
}
IDENTITY_FIELDS = {
    "account_scope",
    "deployment_id",
    "evidence_origin",
    "endpoint_origin",
}
TRUST_ANCHOR_FIELDS = {
    "kind",
    "issuer",
    "reference",
    "fingerprint",
    "signature_algorithm",
}
AUTHORIZATION_FIELDS = {"ref", "actor", "authorized_at"}
CAPABILITY_FIELDS = {
    "read_deployment_evidence",
    "verify_evidence_signature",
    "verify_account_scope",
    "verify_authorization",
    "dispatch_protected_workflow",
    "access_bearer_secret",
    "contact_endpoint",
}

TRUST_RECEIPT_FIELDS = {
    "schema",
    "adapter_profile_digest",
    "provenance_binding_digest",
    "provider_evidence_digest",
    "provider_id",
    "provider_account_scope",
    "deployment_id",
    "trust_anchor_fingerprint",
    "verification",
    "assertions",
    "receipt_digest",
}
TRUST_VERIFICATION_FIELDS = {
    "method",
    "signature_algorithm",
    "signed_payload_digest",
    "verified_at",
    "verifier_identity",
    "external_run_ref",
}
TRUST_ASSERTION_FIELDS = {
    "provider_adapter_executed",
    "evidence_signature_verified",
    "account_scope_verified",
    "authorization_verified",
    "trust_anchor_verified",
    "secret_material_recorded",
}

DISPATCH_FIELDS = {
    "schema",
    "candidate_head",
    "workflow",
    "provider_binding",
    "target",
    "witness_plan",
    "constraints",
    "compiled_at",
    "envelope_digest",
}
WORKFLOW_FIELDS = {"path", "ref_policy", "protected_environment"}
PROVIDER_BINDING_FIELDS = {
    "provider_id",
    "account_scope",
    "deployment_id",
    "activation_packet_digest",
    "provider_evidence_digest",
    "provenance_binding_digest",
    "adapter_profile_digest",
    "trust_receipt_digest",
}
DISPATCH_TARGET_FIELDS = {
    "endpoint",
    "image",
    "source_commit",
    "runtime_p09_head",
    "authorization_ref",
}
WITNESS_PLAN_FIELDS = {
    "sample_count",
    "interval_seconds",
    "minimum_span_seconds",
    "protocol",
}
CONSTRAINT_FIELDS = {
    "secret_material_recorded",
    "execute_live_witness_default",
    "runtime_can_promote",
    "promotion_claimed",
    "ic10_required",
}

RETURN_FIELDS = {
    "schema",
    "dispatch_envelope_digest",
    "candidate_head",
    "provider_id",
    "provider_account_scope",
    "deployment_id",
    "endpoint",
    "image",
    "source_commit",
    "runtime_p09_head",
    "started_at",
    "completed_at",
    "observations",
    "provider_trust_receipt_digest",
    "execution",
    "assertions",
    "return_digest",
}
OBSERVATION_FIELDS = {
    "sequence",
    "observed_at",
    "health_ready",
    "mcp_authenticated",
    "protocol",
    "endpoint_path",
    "source_commit",
    "tool_count",
    "resource_count",
    "tool_inventory_digest",
    "resource_inventory_digest",
}
EXECUTION_FIELDS = {
    "workflow_run_ref",
    "job_ref",
    "protected_environment",
    "external_persistence_ref",
    "return_signature_algorithm",
    "return_signature",
    "signer_identity",
    "signer_trust_anchor_fingerprint",
}
RETURN_ASSERTION_FIELDS = {
    "provider_trust_verified",
    "authorization_verified",
    "bearer_secret_available_at_runtime",
    "endpoint_contacted",
    "persistent_witness_executed",
    "external_return_persisted",
    "secret_material_recorded",
    "promotion_claimed",
}


class ProviderAdapterWitnessReturnError(RuntimeError):
    """Raised when the frozen W18 contract or submitted return is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProviderAdapterWitnessReturnError(
            f"{path.name} must contain an object"
        )
    return value


def _digest_without(value: dict[str, Any], field: str) -> str:
    return _digest(
        {key: deepcopy(nested) for key, nested in value.items() if key != field}
    )


def provider_adapter_profile_digest(profile: dict[str, Any]) -> str:
    return _digest_without(profile, "profile_digest")


def provider_trust_receipt_digest(receipt: dict[str, Any]) -> str:
    return _digest_without(receipt, "receipt_digest")


def dispatch_envelope_digest(envelope: dict[str, Any]) -> str:
    return _digest_without(envelope, "envelope_digest")


def persistent_witness_return_digest(witness_return: dict[str, Any]) -> str:
    return _digest_without(witness_return, "return_digest")


def _origin(value: str, path: str) -> str:
    normalized = _https_url(value, path)
    parts = urlsplit(normalized)
    return urlunsplit((parts.scheme, parts.netloc, "", "", "")).rstrip("/")


def _sha(value: Any, path: str) -> str:
    candidate = _bounded_text(value, path)
    if not SHA256_VALUE.fullmatch(candidate):
        raise ValueError(f"{path} must be sha256:<64 lowercase hex>")
    return candidate


def _commit(value: Any, path: str) -> str:
    candidate = _bounded_text(value, path)
    if not COMMIT_VALUE.fullmatch(candidate):
        raise ValueError(f"{path} must be an exact 40-hex commit")
    return candidate


def _positive_count(value: Any, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{path} must be a positive integer")
    return value


class FrozenProviderAdapterWitnessReturn:
    """Frozen W18 contract and non-authoritative return-admission engine."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        predecessor: FrozenEvidenceProvenanceGate,
    ) -> None:
        self.snapshot = snapshot
        self.predecessor = predecessor

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        predecessor: FrozenEvidenceProvenanceGate | None = None,
    ) -> "FrozenProviderAdapterWitnessReturn":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise ProviderAdapterWitnessReturnError(
                "unexpected W18 schema or phase"
            )
        predecessor = predecessor or FrozenEvidenceProvenanceGate.load()
        w17 = predecessor.status()
        expected_predecessor = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w17_head": "9ac6f97f1065280d027d13a43d8c9d68770184bd",
            "w17_tree": "86ba629b62a2f91b42b0f035638ff82d80b05699",
            "w17_schema": "athena.xnav-w17-evidence-provenance-dispatch-gate/v1",
            "w17_contract_digest": w17["contract_digest"],
            "w17_receipt_id": (
                "w17-provenance-gate:sha256:"
                "615fed4366cd2e06bc7773df8aa632f7a005c8ba25dda8728def9a59a0b95913"
            ),
            "w16_ledger_root": w17["w16_ledger_root"],
            "activation_handoff_head": (
                "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
            ),
            "canonical_hardening_head": (
                "b4e24de38788ecdf30f43514ece279d1270b998b"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise ProviderAdapterWitnessReturnError(
                "W18 predecessor lineage mismatch"
            )

        expected_adapter = {
            "profile_schema": PROFILE_SCHEMA,
            "trust_receipt_schema": TRUST_RECEIPT_SCHEMA,
            "profile_binding_class": (
                "PROVIDER_ADAPTER_PROFILE_STRUCTURALLY_BOUND"
            ),
            "trust_receipt_binding_class": (
                "STRUCTURALLY_BOUND_PROVIDER_TRUST_RECEIPT"
            ),
            "required_execution_class": (
                "PROVIDER_ADAPTER_TRUST_ANCHOR_EXTERNALLY_VERIFIED"
            ),
            "adapter_kind_allowlist": [
                "credentialed-provider-api",
                "provider-signed-attestation",
            ],
            "signature_algorithm_allowlist": [
                "ed25519",
                "ecdsa-p256-sha256",
                "rsa-pss-sha256",
            ],
            "provider_registry_mode": "EXPLICIT_PROFILE_REQUIRED",
            "committed_provider_profiles": [],
            "cryptographic_registry_schema": (
                "athena.provider-trust-registry/v1"
            ),
            "cryptographic_registry_contract_digest": (
                "sha256:0f7f62e6e0ea83d6ee89d961ca880254"
                "cd1535ff40c794b81a1f46a1f3bfb571"
            ),
            "crypto_verifier": (
                "READY_ED25519_DETACHED_CANONICAL_JSON"
            ),
            "runtime_has_crypto_verifier": True,
            "trust_receipt_requires_pinned_provider_return": True,
            "provider_selected": False,
            "runtime_has_network_adapter": False,
            "runtime_has_provider_credentials": False,
            "runtime_verifies_external_signatures": False,
            "runtime_verifies_external_authority": False,
            "submitted_inputs_persisted": False,
        }
        if snapshot.get("provider_adapter_contract") != expected_adapter:
            raise ProviderAdapterWitnessReturnError(
                "W18 provider-adapter contract drift"
            )

        expected_return = {
            "dispatch_envelope_schema": DISPATCH_ENVELOPE_SCHEMA,
            "witness_return_schema": WITNESS_RETURN_SCHEMA,
            "admission_schema": ADMISSION_SCHEMA,
            "workflow_path": ".github/workflows/p10-host-readiness.yml",
            "workflow_ref_policy": "EXACT_CANDIDATE_HEAD_REQUIRED",
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "endpoint_scheme": "https",
            "endpoint_path": "/mcp",
            "protocol": "2025-03-26",
            "return_signature_required": True,
            "external_return_persistence_required": True,
            "runtime_dispatch_capability": "NONE",
            "runtime_has_persistence_adapter": False,
            "runtime_can_admit_external_authority": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if snapshot.get("persistent_witness_return_contract") != expected_return:
            raise ProviderAdapterWitnessReturnError(
                "W18 persistent-witness return contract drift"
            )

        expected_boundaries = {
            "provider_selected": False,
            "provider_adapter_executed": False,
            "live_provider_fetch_executed": False,
            "trust_anchor_verified": False,
            "authorization_externally_verified": False,
            "submitted_inputs_persisted": False,
            "secret_material_accepted": False,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "workflow_dispatched": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admitted": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise ProviderAdapterWitnessReturnError(
                "W18 repository boundaries must remain false"
            )
        if snapshot.get("successor") != (
            "KC144.XNAV.W19::AUTHORIZED-PROVIDER-ADAPTER-ADMISSION-"
            "AND-PERSISTENT-WITNESS-EXECUTION"
        ):
            raise ProviderAdapterWitnessReturnError("W18 successor drift")
        material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(material):
            raise ProviderAdapterWitnessReturnError(
                "W18 contract digest mismatch"
            )
        return cls(snapshot, predecessor)

    @classmethod
    def load(
        cls, path: Path = DATA_PATH
    ) -> "FrozenProviderAdapterWitnessReturn":
        return cls.from_snapshot(_load_json(path))

    @property
    def adapter_contract(self) -> dict[str, Any]:
        return self.snapshot["provider_adapter_contract"]

    @property
    def return_contract(self) -> dict[str, Any]:
        return self.snapshot["persistent_witness_return_contract"]

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "PROVIDER_ADAPTER_AND_WITNESS_RETURN_CONTRACT_READY__"
                "EXTERNAL_EXECUTION_NOT_PRESENT"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w17_contract_digest": self.snapshot["predecessor"][
                "w17_contract_digest"
            ],
            "provider_adapter_contract": deepcopy(self.adapter_contract),
            "persistent_witness_return_contract": deepcopy(
                self.return_contract
            ),
            "cross_navigation_law": (
                "STRUCTURAL_RETURN_BINDING_NEQ_EXTERNAL_SIGNATURE_"
                "VERIFICATION_NEQ_CONTROL_ADMISSION"
            ),
            "cross_navigation_state": (
                "W18_CRYPTO_VERIFIER_AND_PERSISTENT_RETURN_SCHEMAS_CLOSED__"
                "PROVIDER_ADMISSION_EXECUTION_AND_CONTROL_RETURN_OPEN"
            ),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "successor": self.snapshot["successor"],
        }

    def _bound_w17_inputs(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ]:
        if (
            not isinstance(provenance_witness_json, str)
            or len(provenance_witness_json) > 32768
        ):
            raise ValueError("provenance witness must be bounded JSON text")
        packet, evidence = self.predecessor._packet_evidence(
            activation_packet_json, provider_evidence_json
        )
        provenance = self.predecessor._validate_provenance(
            json.loads(provenance_witness_json), packet, evidence
        )
        binding = self.predecessor.inspect_provenance(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
        )
        if not binding["status"].startswith(
            "PASS_STRUCTURAL_EVIDENCE_PROVENANCE_BINDING"
        ):
            raise ValueError("W17 provenance binding did not pass")
        return packet, evidence, provenance, binding

    def build_provider_adapter_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> dict[str, Any]:
        """Return a content-bound adapter/receipt/return template bundle."""
        try:
            packet, evidence, provenance, binding = self._bound_w17_inputs(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))
        profile = {
            "schema": PROFILE_SCHEMA,
            "provider_id": packet["provider"]["id"],
            "adapter": {
                "id": None,
                "version": None,
                "kind": provenance["verifier"]["method"],
                "retrieval_mode": provenance["retrieval"]["mode"],
                "verification_method": provenance["verifier"]["method"],
            },
            "identity_binding": {
                "account_scope": packet["provider"]["account_scope"],
                "deployment_id": packet["provider"]["deployment_id"],
                "evidence_origin": _origin(
                    evidence["evidence_url"], "evidence.evidence_url"
                ),
                "endpoint_origin": _origin(
                    evidence["endpoint"], "evidence.endpoint"
                ),
            },
            "trust_anchor": {
                "kind": provenance["trust_anchor"]["kind"],
                "issuer": None,
                "reference": provenance["trust_anchor"]["reference"],
                "fingerprint": provenance["trust_anchor"]["fingerprint"],
                "signature_algorithm": None,
            },
            "authorization_binding": deepcopy(packet["authorization"]),
            "capabilities": {
                "read_deployment_evidence": True,
                "verify_evidence_signature": True,
                "verify_account_scope": True,
                "verify_authorization": True,
                "dispatch_protected_workflow": False,
                "access_bearer_secret": False,
                "contact_endpoint": False,
            },
            "secret_material_recorded": False,
            "profile_digest": None,
        }
        return {
            "status": "UNRESOLVED_PROVIDER_ADAPTER_AND_RETURN_TEMPLATE",
            "provider_adapter_profile_template": profile,
            "trust_verification_receipt_template": {
                "schema": TRUST_RECEIPT_SCHEMA,
                "adapter_profile_digest": None,
                "provenance_binding_digest": binding[
                    "provenance_binding_digest"
                ],
                "provider_evidence_digest": _digest(evidence),
                "provider_id": packet["provider"]["id"],
                "provider_account_scope": packet["provider"]["account_scope"],
                "deployment_id": packet["provider"]["deployment_id"],
                "trust_anchor_fingerprint": provenance["trust_anchor"][
                    "fingerprint"
                ],
                "verification": None,
                "assertions": None,
                "receipt_digest": None,
            },
            "persistent_witness_return_template": {
                "schema": WITNESS_RETURN_SCHEMA,
                "dispatch_envelope_digest": None,
                "candidate_head": None,
                "provider_id": packet["provider"]["id"],
                "provider_account_scope": packet["provider"]["account_scope"],
                "deployment_id": packet["provider"]["deployment_id"],
                "endpoint": packet["target"]["endpoint"],
                "image": packet["image"],
                "source_commit": packet["source_commit"],
                "runtime_p09_head": packet["runtime_p09_head"],
                "started_at": None,
                "completed_at": None,
                "observations": [],
                "provider_trust_receipt_digest": None,
                "execution": None,
                "assertions": None,
                "return_digest": None,
            },
            "submitted_inputs_persisted": False,
            "provider_selected": False,
            "provider_adapter_executed": False,
            "external_signatures_verified": False,
            "dispatch_allowed": False,
        }

    def _validate_profile(
        self,
        value: Any,
        packet: dict[str, Any],
        evidence: dict[str, Any],
        provenance: dict[str, Any],
    ) -> dict[str, Any]:
        _assert_secret_free(value, "provider_adapter_profile")
        profile = _exact_object(value, PROFILE_FIELDS, "provider adapter profile")
        if profile.get("schema") != PROFILE_SCHEMA:
            raise ValueError(f"profile schema must be {PROFILE_SCHEMA}")
        if profile.get("provider_id") != packet["provider"]["id"]:
            raise ValueError("profile provider_id does not match packet")

        adapter = _exact_object(profile.get("adapter"), ADAPTER_FIELDS, "adapter")
        adapter_id = _bounded_text(adapter.get("id"), "adapter.id")
        if not ADAPTER_ID.fullmatch(adapter_id):
            raise ValueError("adapter.id must be a bounded lowercase identifier")
        adapter_kind = _bounded_text(adapter.get("kind"), "adapter.kind")
        if adapter_kind not in self.adapter_contract["adapter_kind_allowlist"]:
            raise ValueError("adapter.kind is not admitted")
        normalized_adapter = {
            "id": adapter_id,
            "version": _bounded_text(adapter.get("version"), "adapter.version"),
            "kind": adapter_kind,
            "retrieval_mode": _bounded_text(
                adapter.get("retrieval_mode"), "adapter.retrieval_mode"
            ),
            "verification_method": _bounded_text(
                adapter.get("verification_method"),
                "adapter.verification_method",
            ),
        }
        if (
            normalized_adapter["retrieval_mode"]
            != provenance["retrieval"]["mode"]
            or normalized_adapter["verification_method"]
            != provenance["verifier"]["method"]
            or normalized_adapter["kind"]
            != provenance["verifier"]["method"]
        ):
            raise ValueError("adapter methods do not match W17 provenance")

        identity = _exact_object(
            profile.get("identity_binding"),
            IDENTITY_FIELDS,
            "identity_binding",
        )
        normalized_identity = {
            "account_scope": _bounded_text(
                identity.get("account_scope"), "identity_binding.account_scope"
            ),
            "deployment_id": _bounded_text(
                identity.get("deployment_id"), "identity_binding.deployment_id"
            ),
            "evidence_origin": _origin(
                identity.get("evidence_origin"),
                "identity_binding.evidence_origin",
            ),
            "endpoint_origin": _origin(
                identity.get("endpoint_origin"),
                "identity_binding.endpoint_origin",
            ),
        }
        expected_identity = {
            "account_scope": packet["provider"]["account_scope"],
            "deployment_id": packet["provider"]["deployment_id"],
            "evidence_origin": _origin(
                evidence["evidence_url"], "evidence.evidence_url"
            ),
            "endpoint_origin": _origin(evidence["endpoint"], "evidence.endpoint"),
        }
        if normalized_identity != expected_identity:
            raise ValueError("profile identity binding does not match W17 inputs")

        anchor = _exact_object(
            profile.get("trust_anchor"), TRUST_ANCHOR_FIELDS, "trust_anchor"
        )
        algorithm = _bounded_text(
            anchor.get("signature_algorithm"),
            "trust_anchor.signature_algorithm",
        )
        if algorithm not in self.adapter_contract[
            "signature_algorithm_allowlist"
        ]:
            raise ValueError("trust-anchor signature algorithm is not admitted")
        normalized_anchor = {
            "kind": _bounded_text(
                anchor.get("kind"), "trust_anchor.kind"
            ),
            "issuer": _bounded_text(
                anchor.get("issuer"), "trust_anchor.issuer"
            ),
            "reference": _https_url(
                anchor.get("reference"), "trust_anchor.reference"
            ),
            "fingerprint": _sha(
                anchor.get("fingerprint"), "trust_anchor.fingerprint"
            ),
            "signature_algorithm": algorithm,
        }
        if (
            normalized_anchor["kind"] != provenance["trust_anchor"]["kind"]
            or normalized_anchor["reference"]
            != provenance["trust_anchor"]["reference"]
            or normalized_anchor["fingerprint"]
            != provenance["trust_anchor"]["fingerprint"]
        ):
            raise ValueError("profile trust anchor does not match W17 provenance")

        authorization = _exact_object(
            profile.get("authorization_binding"),
            AUTHORIZATION_FIELDS,
            "authorization_binding",
        )
        normalized_authorization = {
            "ref": _bounded_text(
                authorization.get("ref"), "authorization_binding.ref"
            ),
            "actor": _bounded_text(
                authorization.get("actor"), "authorization_binding.actor"
            ),
            "authorized_at": _timestamp(
                authorization.get("authorized_at"),
                "authorization_binding.authorized_at",
            ),
        }
        if normalized_authorization != packet["authorization"]:
            raise ValueError("profile authorization does not match packet")

        capabilities = _exact_object(
            profile.get("capabilities"), CAPABILITY_FIELDS, "capabilities"
        )
        expected_capabilities = {
            "read_deployment_evidence": True,
            "verify_evidence_signature": True,
            "verify_account_scope": True,
            "verify_authorization": True,
            "dispatch_protected_workflow": False,
            "access_bearer_secret": False,
            "contact_endpoint": False,
        }
        if capabilities != expected_capabilities:
            raise ValueError("provider adapter crosses its capability boundary")
        if profile.get("secret_material_recorded") is not False:
            raise ValueError("provider profile must not record secret material")
        normalized = {
            "schema": PROFILE_SCHEMA,
            "provider_id": packet["provider"]["id"],
            "adapter": normalized_adapter,
            "identity_binding": normalized_identity,
            "trust_anchor": normalized_anchor,
            "authorization_binding": normalized_authorization,
            "capabilities": expected_capabilities,
            "secret_material_recorded": False,
            "profile_digest": _sha(
                profile.get("profile_digest"), "profile_digest"
            ),
        }
        if normalized["profile_digest"] != provider_adapter_profile_digest(
            normalized
        ):
            raise ValueError("provider adapter profile digest mismatch")
        return normalized

    def inspect_provider_adapter(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
    ) -> dict[str, Any]:
        try:
            if (
                not isinstance(provider_adapter_profile_json, str)
                or len(provider_adapter_profile_json) > 32768
            ):
                raise ValueError("provider adapter profile must be bounded JSON")
            packet, evidence, provenance, binding = self._bound_w17_inputs(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            profile = self._validate_profile(
                json.loads(provider_adapter_profile_json),
                packet,
                evidence,
                provenance,
            )
            binding_digest = _digest(
                {
                    "schema": SCHEMA,
                    "phase": PHASE,
                    "w17_provenance_binding_digest": binding[
                        "provenance_binding_digest"
                    ],
                    "provider_adapter_profile_digest": profile[
                        "profile_digest"
                    ],
                    "contract_digest": self.snapshot["contract_digest"],
                    "classification": (
                        "PROVIDER_ADAPTER_PROFILE_STRUCTURALLY_BOUND"
                    ),
                }
            )
            return {
                "status": (
                    "PASS_PROVIDER_ADAPTER_PROFILE_BINDING__"
                    "ADAPTER_EXECUTION_UNVERIFIED"
                ),
                "provider_adapter_profile_digest": profile["profile_digest"],
                "w17_provenance_binding_digest": binding[
                    "provenance_binding_digest"
                ],
                "provider_adapter_binding_digest": binding_digest,
                "profile_class": (
                    "PROVIDER_ADAPTER_PROFILE_STRUCTURALLY_BOUND"
                ),
                "provider_selected_by_repository": False,
                "adapter_executed_by_runtime": False,
                "external_signatures_verified_by_runtime": False,
                "trust_anchor_verified_by_runtime": False,
                "submitted_inputs_persisted": False,
                "dispatch_allowed": False,
                "runtime_can_promote": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def _validate_trust_receipt(
        self,
        value: Any,
        packet: dict[str, Any],
        evidence: dict[str, Any],
        provenance: dict[str, Any],
        binding: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        _assert_secret_free(value, "provider_trust_receipt")
        receipt = _exact_object(
            value, TRUST_RECEIPT_FIELDS, "provider trust receipt"
        )
        if receipt.get("schema") != TRUST_RECEIPT_SCHEMA:
            raise ValueError(
                f"trust receipt schema must be {TRUST_RECEIPT_SCHEMA}"
            )
        expected_scalars = {
            "adapter_profile_digest": profile["profile_digest"],
            "provenance_binding_digest": binding[
                "provenance_binding_digest"
            ],
            "provider_evidence_digest": _digest(evidence),
            "provider_id": packet["provider"]["id"],
            "provider_account_scope": packet["provider"]["account_scope"],
            "deployment_id": packet["provider"]["deployment_id"],
            "trust_anchor_fingerprint": profile["trust_anchor"]["fingerprint"],
        }
        for field, expected in expected_scalars.items():
            actual = _bounded_text(receipt.get(field), field)
            if actual != expected:
                raise ValueError(f"trust receipt {field} mismatch")

        verification = _exact_object(
            receipt.get("verification"),
            TRUST_VERIFICATION_FIELDS,
            "verification",
        )
        algorithm = _bounded_text(
            verification.get("signature_algorithm"),
            "verification.signature_algorithm",
        )
        if algorithm != profile["trust_anchor"]["signature_algorithm"]:
            raise ValueError("trust receipt signature algorithm mismatch")
        expected_payload_digest = _digest(
            {
                "adapter_profile_digest": profile["profile_digest"],
                "provenance_binding_digest": binding[
                    "provenance_binding_digest"
                ],
                "provider_evidence_digest": _digest(evidence),
                "authorization_ref": packet["authorization"]["ref"],
                "trust_anchor_fingerprint": profile["trust_anchor"][
                    "fingerprint"
                ],
            }
        )
        normalized_verification = {
            "method": _bounded_text(
                verification.get("method"), "verification.method"
            ),
            "signature_algorithm": algorithm,
            "signed_payload_digest": _sha(
                verification.get("signed_payload_digest"),
                "verification.signed_payload_digest",
            ),
            "verified_at": _timestamp(
                verification.get("verified_at"), "verification.verified_at"
            ),
            "verifier_identity": _bounded_text(
                verification.get("verifier_identity"),
                "verification.verifier_identity",
            ),
            "external_run_ref": _https_url(
                verification.get("external_run_ref"),
                "verification.external_run_ref",
            ),
        }
        if normalized_verification["method"] != profile["adapter"]["kind"]:
            raise ValueError("trust receipt verification method mismatch")
        if normalized_verification[
            "signed_payload_digest"
        ] != expected_payload_digest:
            raise ValueError("trust receipt signed-payload digest mismatch")
        if _parsed_timestamp(
            normalized_verification["verified_at"]
        ) < _parsed_timestamp(provenance["verifier"]["verified_at"]):
            raise ValueError("trust receipt predates W17 provenance verification")

        assertions = _exact_object(
            receipt.get("assertions"),
            TRUST_ASSERTION_FIELDS,
            "trust receipt assertions",
        )
        expected_assertions = {
            "provider_adapter_executed": True,
            "evidence_signature_verified": True,
            "account_scope_verified": True,
            "authorization_verified": True,
            "trust_anchor_verified": True,
            "secret_material_recorded": False,
        }
        if assertions != expected_assertions:
            raise ValueError("trust receipt assertions are incomplete")
        normalized = {
            "schema": TRUST_RECEIPT_SCHEMA,
            **expected_scalars,
            "verification": normalized_verification,
            "assertions": expected_assertions,
            "receipt_digest": _sha(
                receipt.get("receipt_digest"), "receipt_digest"
            ),
        }
        if normalized["receipt_digest"] != provider_trust_receipt_digest(
            normalized
        ):
            raise ValueError("provider trust receipt digest mismatch")
        return normalized

    def _compiled_envelope(
        self,
        packet: dict[str, Any],
        evidence: dict[str, Any],
        binding: dict[str, Any],
        profile: dict[str, Any],
        trust_receipt: dict[str, Any],
        candidate_head: str,
        compiled_at: str,
    ) -> dict[str, Any]:
        envelope = {
            "schema": DISPATCH_ENVELOPE_SCHEMA,
            "candidate_head": candidate_head,
            "workflow": {
                "path": self.return_contract["workflow_path"],
                "ref_policy": self.return_contract["workflow_ref_policy"],
                "protected_environment": self.return_contract[
                    "protected_environment"
                ],
            },
            "provider_binding": {
                "provider_id": packet["provider"]["id"],
                "account_scope": packet["provider"]["account_scope"],
                "deployment_id": packet["provider"]["deployment_id"],
                "activation_packet_digest": _digest(packet),
                "provider_evidence_digest": _digest(evidence),
                "provenance_binding_digest": binding[
                    "provenance_binding_digest"
                ],
                "adapter_profile_digest": profile["profile_digest"],
                "trust_receipt_digest": trust_receipt["receipt_digest"],
            },
            "target": {
                "endpoint": packet["target"]["endpoint"],
                "image": packet["image"],
                "source_commit": packet["source_commit"],
                "runtime_p09_head": packet["runtime_p09_head"],
                "authorization_ref": packet["authorization"]["ref"],
            },
            "witness_plan": {
                "sample_count": WITNESS_PLAN["sample_count"],
                "interval_seconds": WITNESS_PLAN["interval_seconds"],
                "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
                "protocol": self.return_contract["protocol"],
            },
            "constraints": {
                "secret_material_recorded": False,
                "execute_live_witness_default": False,
                "runtime_can_promote": False,
                "promotion_claimed": False,
                "ic10_required": True,
            },
            "compiled_at": compiled_at,
            "envelope_digest": "",
        }
        envelope["envelope_digest"] = dispatch_envelope_digest(envelope)
        return envelope

    def compile_dispatch_envelope(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        candidate_head: str,
        compiled_at: str,
    ) -> dict[str, Any]:
        try:
            for value, label in (
                (provider_adapter_profile_json, "provider adapter profile"),
                (provider_trust_receipt_json, "provider trust receipt"),
            ):
                if not isinstance(value, str) or len(value) > 32768:
                    raise ValueError(f"{label} must be bounded JSON")
            packet, evidence, provenance, binding = self._bound_w17_inputs(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            profile = self._validate_profile(
                json.loads(provider_adapter_profile_json),
                packet,
                evidence,
                provenance,
            )
            trust_receipt = self._validate_trust_receipt(
                json.loads(provider_trust_receipt_json),
                packet,
                evidence,
                provenance,
                binding,
                profile,
            )
            normalized_head = _commit(candidate_head, "candidate_head")
            normalized_compiled_at = _timestamp(compiled_at, "compiled_at")
            if _parsed_timestamp(
                normalized_compiled_at
            ) < _parsed_timestamp(trust_receipt["verification"]["verified_at"]):
                raise ValueError("dispatch envelope predates trust receipt")
            envelope = self._compiled_envelope(
                packet,
                evidence,
                binding,
                profile,
                trust_receipt,
                normalized_head,
                normalized_compiled_at,
            )
            return {
                "status": (
                    "HOLD_DISPATCH_ENVELOPE_COMPILED__"
                    "EXTERNAL_SIGNATURE_AND_PROTECTED_EXECUTION_REQUIRED"
                ),
                "dispatch_envelope": envelope,
                "dispatch_envelope_digest": envelope["envelope_digest"],
                "provider_trust_receipt_class": (
                    "STRUCTURALLY_BOUND_PROVIDER_TRUST_RECEIPT"
                ),
                "trust_receipt_signature_verified_by_runtime": False,
                "provider_adapter_executed_by_runtime": False,
                "protected_environment_approved_by_runtime": False,
                "workflow_dispatched": False,
                "endpoint_contacted": False,
                "dispatch_allowed": False,
                "runtime_can_promote": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def _validate_dispatch_envelope(
        self,
        value: Any,
        packet: dict[str, Any],
        evidence: dict[str, Any],
        binding: dict[str, Any],
        profile: dict[str, Any],
        trust_receipt: dict[str, Any],
    ) -> dict[str, Any]:
        _assert_secret_free(value, "dispatch_envelope")
        envelope = _exact_object(value, DISPATCH_FIELDS, "dispatch envelope")
        if envelope.get("schema") != DISPATCH_ENVELOPE_SCHEMA:
            raise ValueError(
                f"dispatch envelope schema must be {DISPATCH_ENVELOPE_SCHEMA}"
            )
        candidate_head = _commit(
            envelope.get("candidate_head"), "dispatch.candidate_head"
        )
        workflow = _exact_object(
            envelope.get("workflow"), WORKFLOW_FIELDS, "dispatch.workflow"
        )
        expected_workflow = {
            "path": self.return_contract["workflow_path"],
            "ref_policy": self.return_contract["workflow_ref_policy"],
            "protected_environment": self.return_contract[
                "protected_environment"
            ],
        }
        if workflow != expected_workflow:
            raise ValueError("dispatch workflow contract mismatch")
        provider_binding = _exact_object(
            envelope.get("provider_binding"),
            PROVIDER_BINDING_FIELDS,
            "dispatch.provider_binding",
        )
        expected_provider_binding = {
            "provider_id": packet["provider"]["id"],
            "account_scope": packet["provider"]["account_scope"],
            "deployment_id": packet["provider"]["deployment_id"],
            "activation_packet_digest": _digest(packet),
            "provider_evidence_digest": _digest(evidence),
            "provenance_binding_digest": binding[
                "provenance_binding_digest"
            ],
            "adapter_profile_digest": profile["profile_digest"],
            "trust_receipt_digest": trust_receipt["receipt_digest"],
        }
        if provider_binding != expected_provider_binding:
            raise ValueError("dispatch provider binding mismatch")
        target = _exact_object(
            envelope.get("target"), DISPATCH_TARGET_FIELDS, "dispatch.target"
        )
        expected_target = {
            "endpoint": packet["target"]["endpoint"],
            "image": packet["image"],
            "source_commit": packet["source_commit"],
            "runtime_p09_head": packet["runtime_p09_head"],
            "authorization_ref": packet["authorization"]["ref"],
        }
        if target != expected_target:
            raise ValueError("dispatch target mismatch")
        witness_plan = _exact_object(
            envelope.get("witness_plan"),
            WITNESS_PLAN_FIELDS,
            "dispatch.witness_plan",
        )
        expected_plan = {
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "protocol": self.return_contract["protocol"],
        }
        if witness_plan != expected_plan:
            raise ValueError("dispatch witness plan mismatch")
        constraints = _exact_object(
            envelope.get("constraints"),
            CONSTRAINT_FIELDS,
            "dispatch.constraints",
        )
        expected_constraints = {
            "secret_material_recorded": False,
            "execute_live_witness_default": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "ic10_required": True,
        }
        if constraints != expected_constraints:
            raise ValueError("dispatch constraints cross authority boundary")
        compiled_at = _timestamp(
            envelope.get("compiled_at"), "dispatch.compiled_at"
        )
        normalized = {
            "schema": DISPATCH_ENVELOPE_SCHEMA,
            "candidate_head": candidate_head,
            "workflow": expected_workflow,
            "provider_binding": expected_provider_binding,
            "target": expected_target,
            "witness_plan": expected_plan,
            "constraints": expected_constraints,
            "compiled_at": compiled_at,
            "envelope_digest": _sha(
                envelope.get("envelope_digest"), "dispatch.envelope_digest"
            ),
        }
        if normalized["envelope_digest"] != dispatch_envelope_digest(normalized):
            raise ValueError("dispatch envelope digest mismatch")
        return normalized

    def _validate_witness_return(
        self,
        value: Any,
        packet: dict[str, Any],
        envelope: dict[str, Any],
        trust_receipt: dict[str, Any],
    ) -> dict[str, Any]:
        _assert_secret_free(value, "persistent_witness_return")
        returned = _exact_object(
            value, RETURN_FIELDS, "persistent witness return"
        )
        if returned.get("schema") != WITNESS_RETURN_SCHEMA:
            raise ValueError(
                f"witness return schema must be {WITNESS_RETURN_SCHEMA}"
            )
        expected_scalars = {
            "dispatch_envelope_digest": envelope["envelope_digest"],
            "candidate_head": envelope["candidate_head"],
            "provider_id": packet["provider"]["id"],
            "provider_account_scope": packet["provider"]["account_scope"],
            "deployment_id": packet["provider"]["deployment_id"],
            "endpoint": packet["target"]["endpoint"],
            "image": IMAGE,
            "source_commit": SOURCE_COMMIT,
            "runtime_p09_head": RUNTIME_P09_HEAD,
            "provider_trust_receipt_digest": trust_receipt["receipt_digest"],
        }
        for field, expected in expected_scalars.items():
            actual = _bounded_text(returned.get(field), field)
            if actual != expected:
                raise ValueError(f"persistent witness return {field} mismatch")
        started_at = _timestamp(returned.get("started_at"), "started_at")
        completed_at = _timestamp(returned.get("completed_at"), "completed_at")
        if _parsed_timestamp(started_at) < _parsed_timestamp(
            envelope["compiled_at"]
        ):
            raise ValueError("persistent witness predates dispatch envelope")

        observations = returned.get("observations")
        if (
            not isinstance(observations, list)
            or len(observations) != WITNESS_PLAN["sample_count"]
        ):
            raise ValueError("persistent witness must contain exactly 3 samples")
        normalized_observations = []
        observed_times = []
        stable_catalog: tuple[int, int, str, str] | None = None
        for index, observation_value in enumerate(observations, start=1):
            observation = _exact_object(
                observation_value,
                OBSERVATION_FIELDS,
                f"observations[{index - 1}]",
            )
            if observation.get("sequence") != index:
                raise ValueError("observation sequence must be contiguous")
            observed_at = _timestamp(
                observation.get("observed_at"),
                f"observations[{index - 1}].observed_at",
            )
            if (
                observation.get("health_ready") is not True
                or observation.get("mcp_authenticated") is not True
                or observation.get("protocol")
                != self.return_contract["protocol"]
                or observation.get("endpoint_path")
                != self.return_contract["endpoint_path"]
                or observation.get("source_commit") != SOURCE_COMMIT
            ):
                raise ValueError(
                    "every observation must pass health, authentication, "
                    "protocol, endpoint, and source checks"
                )
            tool_count = _positive_count(
                observation.get("tool_count"),
                f"observations[{index - 1}].tool_count",
            )
            resource_count = _positive_count(
                observation.get("resource_count"),
                f"observations[{index - 1}].resource_count",
            )
            tool_digest = _sha(
                observation.get("tool_inventory_digest"),
                f"observations[{index - 1}].tool_inventory_digest",
            )
            resource_digest = _sha(
                observation.get("resource_inventory_digest"),
                f"observations[{index - 1}].resource_inventory_digest",
            )
            catalog = (
                tool_count,
                resource_count,
                tool_digest,
                resource_digest,
            )
            if stable_catalog is None:
                stable_catalog = catalog
            elif catalog != stable_catalog:
                raise ValueError("catalog identity changed across observations")
            normalized_observations.append(
                {
                    "sequence": index,
                    "observed_at": observed_at,
                    "health_ready": True,
                    "mcp_authenticated": True,
                    "protocol": self.return_contract["protocol"],
                    "endpoint_path": self.return_contract["endpoint_path"],
                    "source_commit": SOURCE_COMMIT,
                    "tool_count": tool_count,
                    "resource_count": resource_count,
                    "tool_inventory_digest": tool_digest,
                    "resource_inventory_digest": resource_digest,
                }
            )
            observed_times.append(_parsed_timestamp(observed_at))
        if observed_times[0] < _parsed_timestamp(started_at):
            raise ValueError("first observation predates witness start")
        if observed_times[-1] > _parsed_timestamp(completed_at):
            raise ValueError("witness completion predates final observation")
        gaps = [
            (later - earlier).total_seconds()
            for earlier, later in zip(observed_times, observed_times[1:])
        ]
        if any(
            gap < WITNESS_PLAN["interval_seconds"] for gap in gaps
        ):
            raise ValueError("observation interval is shorter than 20 seconds")
        span = (observed_times[-1] - observed_times[0]).total_seconds()
        if span < WITNESS_PLAN["minimum_span_seconds"]:
            raise ValueError("observation span is shorter than 40 seconds")

        execution = _exact_object(
            returned.get("execution"), EXECUTION_FIELDS, "execution"
        )
        algorithm = _bounded_text(
            execution.get("return_signature_algorithm"),
            "execution.return_signature_algorithm",
        )
        if algorithm not in self.adapter_contract[
            "signature_algorithm_allowlist"
        ]:
            raise ValueError("return signature algorithm is not admitted")
        normalized_execution = {
            "workflow_run_ref": _https_url(
                execution.get("workflow_run_ref"),
                "execution.workflow_run_ref",
            ),
            "job_ref": _https_url(
                execution.get("job_ref"), "execution.job_ref"
            ),
            "protected_environment": _bounded_text(
                execution.get("protected_environment"),
                "execution.protected_environment",
            ),
            "external_persistence_ref": _https_url(
                execution.get("external_persistence_ref"),
                "execution.external_persistence_ref",
            ),
            "return_signature_algorithm": algorithm,
            "return_signature": _bounded_text(
                execution.get("return_signature"),
                "execution.return_signature",
            ),
            "signer_identity": _bounded_text(
                execution.get("signer_identity"),
                "execution.signer_identity",
            ),
            "signer_trust_anchor_fingerprint": _sha(
                execution.get("signer_trust_anchor_fingerprint"),
                "execution.signer_trust_anchor_fingerprint",
            ),
        }
        if (
            normalized_execution["protected_environment"]
            != WITNESS_PLAN["environment"]
            or normalized_execution["return_signature_algorithm"]
            != trust_receipt["verification"]["signature_algorithm"]
            or normalized_execution["signer_trust_anchor_fingerprint"]
            != trust_receipt["trust_anchor_fingerprint"]
        ):
            raise ValueError("witness execution does not bind trusted adapter")

        assertions = _exact_object(
            returned.get("assertions"),
            RETURN_ASSERTION_FIELDS,
            "return assertions",
        )
        expected_assertions = {
            "provider_trust_verified": True,
            "authorization_verified": True,
            "bearer_secret_available_at_runtime": True,
            "endpoint_contacted": True,
            "persistent_witness_executed": True,
            "external_return_persisted": True,
            "secret_material_recorded": False,
            "promotion_claimed": False,
        }
        if assertions != expected_assertions:
            raise ValueError("persistent return assertions are incomplete")
        normalized = {
            "schema": WITNESS_RETURN_SCHEMA,
            **expected_scalars,
            "started_at": started_at,
            "completed_at": completed_at,
            "observations": normalized_observations,
            "execution": normalized_execution,
            "assertions": expected_assertions,
            "return_digest": _sha(
                returned.get("return_digest"), "return_digest"
            ),
        }
        if normalized["return_digest"] != persistent_witness_return_digest(
            normalized
        ):
            raise ValueError("persistent witness return digest mismatch")
        return normalized

    def _validated_return_bundle(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        dispatch_envelope_json: str,
        persistent_witness_return_json: str,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ]:
        values = (
            (provider_adapter_profile_json, "provider adapter profile"),
            (provider_trust_receipt_json, "provider trust receipt"),
            (dispatch_envelope_json, "dispatch envelope"),
            (persistent_witness_return_json, "persistent witness return"),
        )
        for value, label in values:
            if not isinstance(value, str) or len(value) > 65536:
                raise ValueError(f"{label} must be bounded JSON")
        packet, evidence, provenance, binding = self._bound_w17_inputs(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
        )
        profile = self._validate_profile(
            json.loads(provider_adapter_profile_json),
            packet,
            evidence,
            provenance,
        )
        trust_receipt = self._validate_trust_receipt(
            json.loads(provider_trust_receipt_json),
            packet,
            evidence,
            provenance,
            binding,
            profile,
        )
        envelope = self._validate_dispatch_envelope(
            json.loads(dispatch_envelope_json),
            packet,
            evidence,
            binding,
            profile,
            trust_receipt,
        )
        returned = self._validate_witness_return(
            json.loads(persistent_witness_return_json),
            packet,
            envelope,
            trust_receipt,
        )
        return (
            packet,
            evidence,
            provenance,
            binding,
            profile,
            trust_receipt,
            envelope,
            returned,
        )

    def inspect_persistent_witness_return(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        dispatch_envelope_json: str,
        persistent_witness_return_json: str,
    ) -> dict[str, Any]:
        try:
            (
                _packet,
                _evidence,
                _provenance,
                binding,
                profile,
                trust_receipt,
                envelope,
                returned,
            ) = self._validated_return_bundle(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_adapter_profile_json,
                provider_trust_receipt_json,
                dispatch_envelope_json,
                persistent_witness_return_json,
            )
            return_binding_digest = _digest(
                {
                    "schema": SCHEMA,
                    "phase": PHASE,
                    "contract_digest": self.snapshot["contract_digest"],
                    "w17_provenance_binding_digest": binding[
                        "provenance_binding_digest"
                    ],
                    "adapter_profile_digest": profile["profile_digest"],
                    "trust_receipt_digest": trust_receipt["receipt_digest"],
                    "dispatch_envelope_digest": envelope["envelope_digest"],
                    "persistent_witness_return_digest": returned[
                        "return_digest"
                    ],
                    "classification": (
                        "STRUCTURALLY_BOUND_PERSISTENT_WITNESS_RETURN"
                    ),
                }
            )
            return {
                "status": (
                    "PASS_STRUCTURAL_PROVIDER_AND_PERSISTENT_RETURN_BINDING__"
                    "EXTERNAL_SIGNATURES_UNVERIFIED"
                ),
                "return_class": (
                    "STRUCTURALLY_BOUND_PERSISTENT_WITNESS_RETURN"
                ),
                "w17_provenance_binding_digest": binding[
                    "provenance_binding_digest"
                ],
                "provider_adapter_profile_digest": profile["profile_digest"],
                "provider_trust_receipt_digest": trust_receipt[
                    "receipt_digest"
                ],
                "dispatch_envelope_digest": envelope["envelope_digest"],
                "persistent_witness_return_digest": returned["return_digest"],
                "return_binding_digest": return_binding_digest,
                "sample_count": len(returned["observations"]),
                "observed_span_seconds": int(
                    (
                        _parsed_timestamp(
                            returned["observations"][-1]["observed_at"]
                        )
                        - _parsed_timestamp(
                            returned["observations"][0]["observed_at"]
                        )
                    ).total_seconds()
                ),
                "provider_selected_by_repository": False,
                "provider_adapter_executed_by_runtime": False,
                "trust_receipt_signature_verified_by_runtime": False,
                "witness_return_signature_verified_by_runtime": False,
                "submitted_inputs_persisted": False,
                "endpoint_contacted_by_runtime": False,
                "workflow_dispatched_by_runtime": False,
                "persistent_witness_executed_by_runtime": False,
                "external_return_persisted_by_runtime": False,
                "control_plane_admitted": False,
                "runtime_can_promote": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def evaluate_return_admission(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        dispatch_envelope_json: str,
        persistent_witness_return_json: str,
    ) -> dict[str, Any]:
        inspected = self.inspect_persistent_witness_return(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_adapter_profile_json,
            provider_trust_receipt_json,
            dispatch_envelope_json,
            persistent_witness_return_json,
        )
        if not inspected["status"].startswith(
            "PASS_STRUCTURAL_PROVIDER_AND_PERSISTENT_RETURN_BINDING"
        ):
            return {
                **inspected,
                "admission_status": "REJECTED_PERSISTENT_WITNESS_RETURN",
            }
        gates = {
            "w17_provenance_structurally_bound": True,
            "provider_adapter_profile_structurally_bound": True,
            "provider_trust_receipt_structurally_bound": True,
            "dispatch_envelope_exact_head_bound": True,
            "three_sample_persistent_return_structurally_bound": True,
            "provider_adapter_execution_externally_witnessed": False,
            "trust_receipt_signature_cryptographically_verified": False,
            "witness_return_signature_cryptographically_verified": False,
            "external_return_persistence_verified": False,
            "control_plane_admission_recorded": False,
        }
        admission_candidate_digest = _digest(
            {
                "schema": ADMISSION_SCHEMA,
                "phase": PHASE,
                "contract_digest": self.snapshot["contract_digest"],
                "return_binding_digest": inspected["return_binding_digest"],
                "gates": gates,
            }
        )
        return {
            "status": (
                "HOLD_PERSISTENT_WITNESS_ADMISSION__"
                "AUTHORIZED_EXTERNAL_EXECUTION_AND_SIGNATURE_VERIFICATION_OPEN"
            ),
            "schema": ADMISSION_SCHEMA,
            "admission_candidate_digest": admission_candidate_digest,
            "return_binding_digest": inspected["return_binding_digest"],
            "gates": gates,
            "passed_gates": [name for name, value in gates.items() if value],
            "open_gates": [name for name, value in gates.items() if not value],
            "required_external_transition": [
                "select and authorize one explicit provider adapter profile",
                "execute that adapter with provider credentials outside this runtime",
                "cryptographically verify the provider trust receipt signature",
                "approve and dispatch the exact candidate head in the protected environment",
                "persist and cryptographically verify the three-sample witness return",
                "record a nonpromotional control-plane admission before IC10 review",
            ],
            "provider_selected_by_repository": False,
            "provider_adapter_executed_by_runtime": False,
            "external_signatures_verified_by_runtime": False,
            "submitted_inputs_persisted": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admitted": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }

    @staticmethod
    def _rejected(reason: str) -> dict[str, Any]:
        return {
            "status": "HOLD_W18_PROVIDER_ADAPTER_OR_RETURN_REJECTED",
            "error": reason,
            "provider_selected_by_repository": False,
            "provider_adapter_executed_by_runtime": False,
            "external_signatures_verified_by_runtime": False,
            "submitted_inputs_persisted": False,
            "secret_material_accepted": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admitted": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_provider_adapter_witness_return(mcp: Any) -> None:
    """Register W18 provider-adapter and persistent-return surfaces."""

    contract = FrozenProviderAdapterWitnessReturn.load()

    @mcp.tool()
    def athena_w18_provider_adapter_return_status() -> str:
        """Report the frozen W18 adapter/return contract and open authority."""
        return _render(contract.status())

    @mcp.tool()
    def build_athena_w18_provider_adapter_return_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> str:
        """Build unresolved provider-adapter and witness-return templates."""
        return _render(
            contract.build_provider_adapter_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w18_provider_adapter_profile(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
    ) -> str:
        """Bind a provider profile without claiming adapter execution."""
        return _render(
            contract.inspect_provider_adapter(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_adapter_profile_json,
            )
        )

    @mcp.tool()
    def compile_athena_w18_protected_dispatch_envelope(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        candidate_head: str,
        compiled_at: str,
    ) -> str:
        """Compile an exact-head dispatch envelope; never dispatch it."""
        return _render(
            contract.compile_dispatch_envelope(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_adapter_profile_json,
                provider_trust_receipt_json,
                candidate_head,
                compiled_at,
            )
        )

    @mcp.tool()
    def inspect_athena_w18_persistent_witness_return(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        dispatch_envelope_json: str,
        persistent_witness_return_json: str,
    ) -> str:
        """Audit a three-sample return without trusting submitted signatures."""
        return _render(
            contract.inspect_persistent_witness_return(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_adapter_profile_json,
                provider_trust_receipt_json,
                dispatch_envelope_json,
                persistent_witness_return_json,
            )
        )

    @mcp.tool()
    def evaluate_athena_w18_persistent_witness_admission(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_adapter_profile_json: str,
        provider_trust_receipt_json: str,
        dispatch_envelope_json: str,
        persistent_witness_return_json: str,
    ) -> str:
        """Evaluate fail-closed admission; never admit or promote a return."""
        return _render(
            contract.evaluate_return_admission(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_adapter_profile_json,
                provider_trust_receipt_json,
                dispatch_envelope_json,
                persistent_witness_return_json,
            )
        )

    @mcp.resource("athena://w18-provider-adapter-witness-return")
    def provider_adapter_witness_return_resource() -> str:
        """Expose the frozen W18 provider-adapter and return contract."""
        return _render(contract.status())
