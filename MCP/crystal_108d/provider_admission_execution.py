"""KC144 W19 provider-admission authority and execution gate.

W19 makes provider admission content-addressable and cryptographically
verifiable without creating an admission authority.  A caller may propose a
provider public key, but the proposal remains untrusted unless a decision is
signed by an authority already pinned in the repository snapshot.  The
production authority and adapter registries are intentionally empty.
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

from .provider_trust_anchor import (
    FrozenProviderTrustRegistry,
    _canonical_bytes,
    _decode_base64,
    _verify_ed25519_signature,
)
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
DATA_PATH = DATA_DIR / "w19_provider_admission_execution.json"
SCHEMA = "athena.xnav-w19-authorized-provider-admission-execution/v1"
PHASE = "KC144.XNAV.W19"
REGISTRY_SCHEMA = "athena.provider-admission-registry/v1"
REQUEST_SCHEMA = "athena.provider-adapter-admission-request/v1"
DECISION_SCHEMA = "athena.provider-adapter-admission-decision/v1"
W18_HEAD = "46f394bf4b99cbc1254da1d3250f418d42012be2"
W18_TREE = "db96274c1b4b0283542cce0bdadd05a3a7f505b8"
W18_PARENTS = [
    "49f2449e159fdef82b60722f35f302290934a468",
    "5eece82829abb7eba87943548e89b6c04179ef40",
]
ADAPTER_ID = re.compile(r"^[a-z0-9][a-z0-9._/-]{2,127}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUEST_FIELDS = {
    "schema",
    "w18_parent_head",
    "provider_id",
    "account_scope",
    "environment",
    "evidence_origin",
    "adapter_id",
    "adapter_version",
    "authorization_ref",
    "provenance_binding_digest",
    "provider_evidence_digest",
    "trust_anchor",
    "requested_capabilities",
    "requested_at",
    "request_digest",
}
ANCHOR_FIELDS = {
    "kind",
    "key_id",
    "public_key_base64",
    "fingerprint",
    "reference",
}
CAPABILITY_FIELDS = {
    "read_deployment_evidence",
    "verify_evidence_signature",
    "verify_account_scope",
    "verify_authorization",
    "dispatch_protected_workflow",
    "access_bearer_secret",
    "contact_endpoint",
}
DECISION_FIELDS = {
    "schema",
    "request_digest",
    "decision",
    "authority_id",
    "authority_key_id",
    "authority_commit",
    "decided_at",
    "signature",
}
SIGNATURE_FIELDS = {"algorithm", "value"}


class ProviderAdmissionExecutionError(RuntimeError):
    """Raised when the frozen W19 gate or submitted admission is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProviderAdmissionExecutionError(f"{path.name} must contain an object")
    return value


def _digest_without(value: dict[str, Any], field: str) -> str:
    return _digest(
        {key: deepcopy(nested) for key, nested in value.items() if key != field}
    )


def _fingerprint(public_key_base64: str) -> str:
    key = _decode_base64(public_key_base64, "public_key_base64", 32)
    return "sha256:" + hashlib.sha256(key).hexdigest()


def _decision_material(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(value)
        for key, value in decision.items()
        if key != "signature"
    }


class FrozenProviderAdmissionExecutionGate:
    """Frozen W19 admission registry and fail-closed execution gate."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        predecessor: FrozenProviderTrustRegistry,
        authorities: dict[str, dict[str, Any]],
        adapters: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.predecessor = predecessor
        self.authorities = authorities
        self.adapters = adapters

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        predecessor: FrozenProviderTrustRegistry | None = None,
    ) -> "FrozenProviderAdmissionExecutionGate":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise ProviderAdmissionExecutionError("unexpected W19 schema or phase")
        predecessor = predecessor or FrozenProviderTrustRegistry.load()
        predecessor_status = predecessor.status()
        expected_predecessor = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w18_head": W18_HEAD,
            "w18_tree": W18_TREE,
            "w18_ordered_parents": W18_PARENTS,
            "w18_crypto_contract_digest": predecessor_status["contract_digest"],
            "w18_unified_return_contract_digest": (
                "sha256:fd00f6463d512004e0900c9d01a5735f"
                "6ba77de27849a9e7c094852fa1474a23"
            ),
            "w18_convergence_receipt_id": (
                "w18-convergence:sha256:"
                "b557b74a14c16f3c2cfe578a35dbef19382586a508043fae6c178692f531e525"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise ProviderAdmissionExecutionError("W19 predecessor mismatch")

        expected_registry = {
            "schema": REGISTRY_SCHEMA,
            "canonicalization": "KC144.CANON.JSON.V1",
            "authority_signature_algorithm": "ed25519",
            "authority_signature_encoding": "base64",
            "admission_authorities": [],
            "admitted_adapters": [],
        }
        if snapshot.get("admission_registry") != expected_registry:
            raise ProviderAdmissionExecutionError(
                "W19 production admission registry must remain empty"
            )

        expected_policy = {
            "request_schema": REQUEST_SCHEMA,
            "decision_schema": DECISION_SCHEMA,
            "self_supplied_admission_authorities_allowed": False,
            "self_supplied_provider_keys_are_trusted": False,
            "exact_w18_parent_required": True,
            "exact_provider_identity_required": True,
            "provider_public_key_fingerprint_required": True,
            "external_authorization_binding_required": True,
            "authority_signature_required": True,
            "authority_commit_pin_required": True,
            "production_admission_authority_count": 0,
            "production_provider_adapter_count": 0,
            "runtime_can_mutate_registry": False,
        }
        if snapshot.get("admission_policy") != expected_policy:
            raise ProviderAdmissionExecutionError("W19 admission policy drift")

        expected_execution = {
            "workflow_path": ".github/workflows/p10-host-readiness.yml",
            "workflow_ref_policy": "EXACT_CANDIDATE_HEAD_REQUIRED",
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "execute_live_witness_default": False,
            "runtime_dispatch_capability": "NONE",
            "runtime_accepts_secret_material": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if snapshot.get("persistent_execution") != expected_execution:
            raise ProviderAdmissionExecutionError("W19 execution policy drift")

        expected_boundaries = {
            "production_admission_authority_pinned": False,
            "production_provider_adapter_admitted": False,
            "production_provider_trust_anchor_pinned": False,
            "provider_return_signature_verified": False,
            "authorization_externally_verified": False,
            "protected_environment_approved": False,
            "bearer_secret_available_at_job_runtime": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admitted": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise ProviderAdmissionExecutionError(
                "W19 repository boundaries must remain false"
            )
        if snapshot.get("successor") != (
            "KC144.XNAV.W20::VERIFIED-PERSISTENT-WITNESS-RETURN-"
            "AND-CONTROL-PLANE-ADMISSION"
        ):
            raise ProviderAdmissionExecutionError("W19 successor drift")
        if snapshot.get("contract_digest") != _digest_without(
            snapshot, "contract_digest"
        ):
            raise ProviderAdmissionExecutionError("W19 contract digest mismatch")
        return cls(snapshot, predecessor, {}, {})

    @classmethod
    def load(
        cls, path: Path = DATA_PATH
    ) -> "FrozenProviderAdmissionExecutionGate":
        return cls.from_snapshot(_load_json(path))

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "PROVIDER_ADMISSION_VERIFIER_READY__"
                "AUTHORITY_ADAPTER_AND_EXECUTION_OPEN"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w18_parent_head": W18_HEAD,
            "w18_parent_tree": W18_TREE,
            "w18_ordered_parents": W18_PARENTS,
            "request_schema": REQUEST_SCHEMA,
            "decision_schema": DECISION_SCHEMA,
            "production_admission_authority_count": len(self.authorities),
            "production_provider_adapter_count": len(self.adapters),
            "registered_authorities": [],
            "registered_adapters": [],
            "self_supplied_admission_authorities_allowed": False,
            "self_supplied_provider_keys_are_trusted": False,
            "runtime_can_mutate_registry": False,
            "persistent_execution": deepcopy(
                self.snapshot["persistent_execution"]
            ),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "cross_navigation_state": (
                "W19_ADMISSION_AND_EXECUTION_VERIFIERS_CLOSED__"
                "EXTERNAL_AUTHORITY_ADAPTER_AND_PERSISTENT_RETURN_OPEN"
            ),
            "successor": self.snapshot["successor"],
        }

    def build_admission_request(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        adapter_id: str,
        adapter_version: str,
        key_id: str,
        public_key_base64: str,
        requested_at: str,
    ) -> dict[str, Any]:
        try:
            context, inspected = self.predecessor._w17_context(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            if context is None:
                return {
                    **inspected,
                    "admission_request_status": "HOLD_W17_PROVENANCE_REJECTED",
                }
            adapter_id = _bounded_text(adapter_id, "adapter_id")
            if not ADAPTER_ID.fullmatch(adapter_id):
                raise ValueError("adapter_id must be a lowercase identifier")
            adapter_version = _bounded_text(adapter_version, "adapter_version")
            key_id = _bounded_text(key_id, "key_id")
            public_key_base64 = _bounded_text(
                public_key_base64, "public_key_base64"
            )
            fingerprint = _fingerprint(public_key_base64)
            provenance = json.loads(provenance_witness_json)
            if fingerprint != context["provenance_trust_fingerprint"]:
                raise ValueError(
                    "provider public key fingerprint does not match W17 provenance"
                )
            requested_at = _timestamp(requested_at, "requested_at")
            if _parsed_timestamp(requested_at) < _parsed_timestamp(
                context["provenance_verified_at"]
            ):
                raise ValueError("admission request predates provenance verification")
            request = {
                "schema": REQUEST_SCHEMA,
                "w18_parent_head": W18_HEAD,
                "provider_id": context["provider_id"],
                "account_scope": context["account_scope"],
                "environment": context["environment"],
                "evidence_origin": context["evidence_origin"],
                "adapter_id": adapter_id,
                "adapter_version": adapter_version,
                "authorization_ref": context["authorization_ref"],
                "provenance_binding_digest": context[
                    "provenance_binding_digest"
                ],
                "provider_evidence_digest": context[
                    "provider_evidence_digest"
                ],
                "trust_anchor": {
                    "kind": "ed25519-public-key",
                    "key_id": key_id,
                    "public_key_base64": public_key_base64,
                    "fingerprint": fingerprint,
                    "reference": provenance["trust_anchor"]["reference"],
                },
                "requested_capabilities": {
                    "read_deployment_evidence": True,
                    "verify_evidence_signature": True,
                    "verify_account_scope": True,
                    "verify_authorization": True,
                    "dispatch_protected_workflow": False,
                    "access_bearer_secret": False,
                    "contact_endpoint": False,
                },
                "requested_at": requested_at,
                "request_digest": "",
            }
            request["request_digest"] = _digest_without(
                request, "request_digest"
            )
            return {
                "status": (
                    "PASS_STRUCTURAL_ADMISSION_REQUEST__"
                    "CONTROL_AUTHORITY_NOT_PINNED"
                ),
                "request": request,
                "request_digest": request["request_digest"],
                "provider_public_key_mathematically_well_formed": True,
                "provider_public_key_trusted": False,
                "admission_authority_pinned": False,
                "provider_adapter_admitted": False,
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

    def _validate_request(self, value: Any) -> dict[str, Any]:
        _assert_secret_free(value, "admission_request")
        request = _exact_object(value, REQUEST_FIELDS, "admission request")
        normalized = {
            "schema": _bounded_text(request.get("schema"), "schema"),
            "w18_parent_head": _bounded_text(
                request.get("w18_parent_head"), "w18_parent_head"
            ),
            "provider_id": _bounded_text(
                request.get("provider_id"), "provider_id"
            ),
            "account_scope": _bounded_text(
                request.get("account_scope"), "account_scope"
            ),
            "environment": _bounded_text(
                request.get("environment"), "environment"
            ),
            "evidence_origin": _bounded_text(
                request.get("evidence_origin"), "evidence_origin"
            ),
            "adapter_id": _bounded_text(request.get("adapter_id"), "adapter_id"),
            "adapter_version": _bounded_text(
                request.get("adapter_version"), "adapter_version"
            ),
            "authorization_ref": _bounded_text(
                request.get("authorization_ref"), "authorization_ref"
            ),
            "provenance_binding_digest": _bounded_text(
                request.get("provenance_binding_digest"),
                "provenance_binding_digest",
            ),
            "provider_evidence_digest": _bounded_text(
                request.get("provider_evidence_digest"),
                "provider_evidence_digest",
            ),
            "requested_at": _timestamp(request.get("requested_at"), "requested_at"),
            "request_digest": _bounded_text(
                request.get("request_digest"), "request_digest"
            ),
        }
        if normalized["schema"] != REQUEST_SCHEMA:
            raise ValueError(f"schema must be {REQUEST_SCHEMA}")
        if normalized["w18_parent_head"] != W18_HEAD:
            raise ValueError("admission request W18 parent mismatch")
        if not ADAPTER_ID.fullmatch(normalized["adapter_id"]):
            raise ValueError("adapter_id must be a lowercase identifier")
        for field in (
            "provenance_binding_digest",
            "provider_evidence_digest",
            "request_digest",
        ):
            if not SHA256_VALUE.fullmatch(normalized[field]):
                raise ValueError(f"{field} must be sha256:<64 hex>")
        anchor = _exact_object(
            request.get("trust_anchor"), ANCHOR_FIELDS, "trust_anchor"
        )
        normalized["trust_anchor"] = {
            "kind": _bounded_text(anchor.get("kind"), "trust_anchor.kind"),
            "key_id": _bounded_text(anchor.get("key_id"), "trust_anchor.key_id"),
            "public_key_base64": _bounded_text(
                anchor.get("public_key_base64"),
                "trust_anchor.public_key_base64",
            ),
            "fingerprint": _bounded_text(
                anchor.get("fingerprint"), "trust_anchor.fingerprint"
            ),
            "reference": _bounded_text(
                anchor.get("reference"), "trust_anchor.reference"
            ),
        }
        if normalized["trust_anchor"]["kind"] != "ed25519-public-key":
            raise ValueError("trust_anchor.kind must be ed25519-public-key")
        if normalized["trust_anchor"]["fingerprint"] != _fingerprint(
            normalized["trust_anchor"]["public_key_base64"]
        ):
            raise ValueError("provider public-key fingerprint mismatch")
        capabilities = _exact_object(
            request.get("requested_capabilities"),
            CAPABILITY_FIELDS,
            "requested_capabilities",
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
            raise ValueError("admission request crosses capability boundary")
        normalized["requested_capabilities"] = expected_capabilities
        if normalized["request_digest"] != _digest_without(
            normalized, "request_digest"
        ):
            raise ValueError("admission request digest mismatch")
        return normalized

    def inspect_admission_decision(
        self, admission_request_json: str, admission_decision_json: str
    ) -> dict[str, Any]:
        try:
            for value, label in (
                (admission_request_json, "admission request"),
                (admission_decision_json, "admission decision"),
            ):
                if not isinstance(value, str) or len(value) > 65536:
                    raise ValueError(f"{label} must be bounded JSON")
            request = self._validate_request(json.loads(admission_request_json))
            submitted = json.loads(admission_decision_json)
            _assert_secret_free(submitted, "admission_decision")
            decision = _exact_object(
                submitted, DECISION_FIELDS, "admission decision"
            )
            normalized = {
                "schema": _bounded_text(decision.get("schema"), "schema"),
                "request_digest": _bounded_text(
                    decision.get("request_digest"), "request_digest"
                ),
                "decision": _bounded_text(decision.get("decision"), "decision"),
                "authority_id": _bounded_text(
                    decision.get("authority_id"), "authority_id"
                ),
                "authority_key_id": _bounded_text(
                    decision.get("authority_key_id"), "authority_key_id"
                ),
                "authority_commit": _bounded_text(
                    decision.get("authority_commit"), "authority_commit"
                ),
                "decided_at": _timestamp(
                    decision.get("decided_at"), "decided_at"
                ),
            }
            if normalized["schema"] != DECISION_SCHEMA:
                raise ValueError(f"schema must be {DECISION_SCHEMA}")
            if normalized["request_digest"] != request["request_digest"]:
                raise ValueError("admission decision request digest mismatch")
            if normalized["decision"] not in {"ADMIT", "DENY"}:
                raise ValueError("decision must be ADMIT or DENY")
            if not COMMIT.fullmatch(normalized["authority_commit"]):
                raise ValueError("authority_commit must be a Git commit")
            if _parsed_timestamp(normalized["decided_at"]) < _parsed_timestamp(
                request["requested_at"]
            ):
                raise ValueError("admission decision predates request")
            signature = _exact_object(
                decision.get("signature"), SIGNATURE_FIELDS, "signature"
            )
            normalized["signature"] = {
                "algorithm": _bounded_text(
                    signature.get("algorithm"), "signature.algorithm"
                ),
                "value": _bounded_text(
                    signature.get("value"), "signature.value"
                ),
            }
            if normalized["signature"]["algorithm"] != "ed25519":
                raise ValueError("admission signature must use ed25519")
            if normalized["decision"] == "DENY":
                return self._hold(
                    "HOLD_PROVIDER_ADMISSION_DENIED",
                    "external authority denied the admission request",
                    request,
                )
            authority = self.authorities.get(normalized["authority_id"])
            if authority is None:
                return self._hold(
                    "HOLD_ADMISSION_AUTHORITY_NOT_PINNED",
                    "authority_id is not present in the commit-pinned registry",
                    request,
                )
            if (
                normalized["authority_key_id"] != authority["key_id"]
                or normalized["authority_commit"] != authority["commit"]
            ):
                raise ValueError("admission authority pin mismatch")
            if not _verify_ed25519_signature(
                authority["public_key_base64"],
                normalized["signature"]["value"],
                _decision_material(normalized),
            ):
                raise ValueError("admission authority signature invalid")
            return {
                "status": "PASS_PINNED_PROVIDER_ADMISSION_DECISION",
                "request_digest": request["request_digest"],
                "decision_digest": _digest(normalized),
                "authority_id": normalized["authority_id"],
                "provider_adapter_admitted": True,
                "provider_trust_anchor_pinned": True,
                "authorization_externally_verified": True,
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

    def evaluate_execution_gate(
        self, admission_request_json: str, admission_decision_json: str
    ) -> dict[str, Any]:
        inspection = self.inspect_admission_decision(
            admission_request_json, admission_decision_json
        )
        admitted = inspection["status"].startswith(
            "PASS_PINNED_PROVIDER_ADMISSION_DECISION"
        )
        gates = {
            "admission_request_content_addressed": bool(
                inspection.get("request_digest")
            ),
            "admission_authority_commit_pinned": admitted,
            "admission_authority_signature_verified": admitted,
            "provider_adapter_admitted": admitted,
            "provider_trust_anchor_pinned": admitted,
            "external_authorization_verified": admitted,
            "exact_candidate_head_approved_in_protected_environment": False,
            "bearer_secret_available_only_at_job_runtime": False,
            "explicit_live_witness_dispatch": False,
            "persistent_three_sample_witness_returned": False,
            "persistent_witness_return_externally_persisted": False,
        }
        return {
            "status": (
                "HOLD_PERSISTENT_WITNESS_EXECUTION__"
                "ADMISSION_AUTHORITY_AND_PROTECTED_EXECUTION_OPEN"
            ),
            "admission_inspection": inspection,
            "gates": gates,
            "passed_gates": [name for name, passed in gates.items() if passed],
            "open_gates": [name for name, passed in gates.items() if not passed],
            "persistent_execution": deepcopy(
                self.snapshot["persistent_execution"]
            ),
            "required_external_transition": [
                "pin an externally governed admission authority by reviewed commit",
                "receive its detached signature over the exact admission decision",
                "admit one provider adapter and public trust anchor by commit",
                "approve the exact candidate head in p10-persistent-host",
                "provision the bearer only at protected job runtime",
                "explicitly dispatch and persist the three-sample witness return",
            ],
            **self._negative_boundaries(),
        }

    @staticmethod
    def _negative_boundaries() -> dict[str, Any]:
        return {
            "submitted_inputs_persisted": False,
            "secret_material_accepted": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admitted": False,
            "dispatch_allowed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }

    def _hold(
        self, status: str, reason: str, request: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "status": status,
            "error": reason,
            "request_digest": request["request_digest"],
            "production_admission_authority_count": len(self.authorities),
            "production_provider_adapter_count": len(self.adapters),
            "admission_authority_signature_verified": False,
            "provider_adapter_admitted": False,
            "provider_trust_anchor_pinned": False,
            "authorization_externally_verified": False,
            **self._negative_boundaries(),
        }

    def _rejected(self, reason: str) -> dict[str, Any]:
        return {
            "status": "HOLD_PROVIDER_ADMISSION_REJECTED",
            "error": reason,
            "admission_authority_signature_verified": False,
            "provider_adapter_admitted": False,
            "provider_trust_anchor_pinned": False,
            "authorization_externally_verified": False,
            **self._negative_boundaries(),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_provider_admission_execution(mcp: Any) -> None:
    """Register W19 admission authority and persistent execution surfaces."""

    gate = FrozenProviderAdmissionExecutionGate.load()

    @mcp.tool()
    def athena_w19_provider_admission_status() -> str:
        """Report pinned admission authorities, adapters, and execution holds."""

        return _render(gate.status())

    @mcp.tool()
    def build_athena_w19_provider_admission_request(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        adapter_id: str,
        adapter_version: str,
        key_id: str,
        public_key_base64: str,
        requested_at: str,
    ) -> str:
        """Build a secret-free, W18-bound provider admission request."""

        return _render(
            gate.build_admission_request(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                adapter_id,
                adapter_version,
                key_id,
                public_key_base64,
                requested_at,
            )
        )

    @mcp.tool()
    def inspect_athena_w19_provider_admission_decision(
        admission_request_json: str, admission_decision_json: str
    ) -> str:
        """Verify a decision only against commit-pinned admission authorities."""

        return _render(
            gate.inspect_admission_decision(
                admission_request_json, admission_decision_json
            )
        )

    @mcp.tool()
    def evaluate_athena_w19_persistent_witness_execution(
        admission_request_json: str, admission_decision_json: str
    ) -> str:
        """Evaluate admission and protected execution without dispatching."""

        return _render(
            gate.evaluate_execution_gate(
                admission_request_json, admission_decision_json
            )
        )

    @mcp.resource("athena://w19-provider-admission-execution")
    def provider_admission_execution_resource() -> str:
        """Return the frozen W19 admission and execution gate."""

        return _render(gate.status())
