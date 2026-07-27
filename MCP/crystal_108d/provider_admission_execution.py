"""KC144 W19 control-signed provider admission and execution gate.

W19 composes the W18 structural-return and Ed25519 verifier surfaces.  A
provider key becomes usable only when a commit-pinned control authority signs
an exact admission record.  A second control signature must authorize the
exact W18 head, provider return, protected workflow, and witness plan.

The production control-authority registry is intentionally empty.  Therefore
the checked-in runtime can validate the protocol and reject caller-supplied
authority keys, but it cannot admit a provider, dispatch a workflow, contact
an endpoint, persist a return, deploy, merge, or promote.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .provider_trust_anchor import (
    FrozenProviderTrustRegistry,
    RETURN_SCHEMA,
    _canonical_bytes,
    _decode_base64,
    _origin,
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
SCHEMA = "athena.xnav-w19-provider-admission-execution-gate/v1"
PHASE = "KC144.XNAV.W19"
CONTROL_REGISTRY_SCHEMA = "athena.control-admission-authority-registry/v1"
ADMISSION_SCHEMA = "athena.provider-adapter-control-admission/v1"
EXECUTION_SCHEMA = (
    "athena.protected-persistent-witness-execution-authorization/v1"
)
W18_HEAD = "46f394bf4b99cbc1254da1d3250f418d42012be2"
W18_TREE = "db96274c1b4b0283542cce0bdadd05a3a7f505b8"
WORKFLOW_PATH = ".github/workflows/w19-authorized-provider-witness.yml"
SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT_VALUE = re.compile(r"^[0-9a-f]{40}$")

AUTHORITY_FIELDS = {
    "authority_id",
    "key_id",
    "public_key_base64",
    "fingerprint",
    "repository",
    "environment",
    "valid_from",
    "valid_until",
}
ADMISSION_FIELDS = {
    "schema",
    "candidate_head",
    "candidate_tree",
    "w18_contracts",
    "adapter",
    "authorization",
    "signature",
    "admission_digest",
}
W18_CONTRACT_FIELDS = {
    "adapter_return_contract_digest",
    "provider_trust_contract_digest",
    "convergence_receipt_id",
}
ADAPTER_FIELDS = {
    "adapter_id",
    "provider_id",
    "account_scope",
    "environment",
    "evidence_origin",
    "verification_method",
    "attests_authorization",
    "trust_anchor",
}
ANCHOR_FIELDS = {
    "kind",
    "key_id",
    "public_key_base64",
    "fingerprint",
}
ADMISSION_AUTHORIZATION_FIELDS = {
    "authority_id",
    "control_repository",
    "control_pull_request",
    "control_commit",
    "control_ref",
    "admitted_at",
    "expires_at",
}
SIGNATURE_FIELDS = {"algorithm", "key_id", "value"}
EXECUTION_FIELDS = {
    "schema",
    "candidate_head",
    "candidate_tree",
    "provider_admission_digest",
    "provider_return_digest",
    "workflow",
    "authorization",
    "signature",
    "execution_digest",
}
WORKFLOW_FIELDS = {
    "path",
    "ref",
    "environment",
    "secret_name",
    "sample_count",
    "interval_seconds",
    "minimum_span_seconds",
    "execute_live_witness",
}
EXECUTION_AUTHORIZATION_FIELDS = {
    "authority_id",
    "control_ref",
    "authorized_at",
    "expires_at",
}


class ProviderAdmissionExecutionError(RuntimeError):
    """Raised when the frozen W19 contract or submitted records are invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ProviderAdmissionExecutionError(
            f"{path.name} must contain an object"
        )
    return value


def _sha(value: Any, field: str) -> str:
    text = _bounded_text(value, field)
    if not SHA256_VALUE.fullmatch(text):
        raise ValueError(f"{field} must be sha256:<64 lowercase hex>")
    return text


def _commit(value: Any, field: str) -> str:
    text = _bounded_text(value, field)
    if not COMMIT_VALUE.fullmatch(text):
        raise ValueError(f"{field} must be 40 lowercase hex")
    return text


def _fingerprint(public_key_base64: str) -> str:
    public_key = _decode_base64(
        public_key_base64,
        "public_key_base64",
        32,
    )
    return "sha256:" + hashlib.sha256(public_key).hexdigest()


def _unsigned_material(value: dict[str, Any], digest_field: str) -> dict[str, Any]:
    return {
        key: deepcopy(nested)
        for key, nested in value.items()
        if key not in {"signature", digest_field}
    }


def _addressed_material(value: dict[str, Any], digest_field: str) -> dict[str, Any]:
    return {
        key: deepcopy(nested)
        for key, nested in value.items()
        if key != digest_field
    }


def _normalized_signature(value: Any, path: str) -> dict[str, str]:
    signature = _exact_object(value, SIGNATURE_FIELDS, path)
    normalized = {
        "algorithm": _bounded_text(
            signature.get("algorithm"), f"{path}.algorithm"
        ),
        "key_id": _bounded_text(signature.get("key_id"), f"{path}.key_id"),
        "value": _bounded_text(signature.get("value"), f"{path}.value"),
    }
    if normalized["algorithm"] != "ed25519":
        raise ValueError(f"{path}.algorithm must be ed25519")
    _decode_base64(normalized["value"], f"{path}.value", 64)
    return normalized


def _normalize_authority(value: Any) -> dict[str, Any]:
    authority = _exact_object(value, AUTHORITY_FIELDS, "control authority")
    normalized = {
        "authority_id": _bounded_text(
            authority.get("authority_id"), "authority_id"
        ),
        "key_id": _bounded_text(authority.get("key_id"), "key_id"),
        "public_key_base64": _bounded_text(
            authority.get("public_key_base64"),
            "public_key_base64",
        ),
        "fingerprint": _sha(
            authority.get("fingerprint"), "authority.fingerprint"
        ),
        "repository": _bounded_text(
            authority.get("repository"), "authority.repository"
        ),
        "environment": _bounded_text(
            authority.get("environment"), "authority.environment"
        ),
        "valid_from": _timestamp(
            authority.get("valid_from"), "authority.valid_from"
        ),
        "valid_until": _timestamp(
            authority.get("valid_until"), "authority.valid_until"
        ),
    }
    if normalized["repository"] != "demeet2k/Athena":
        raise ValueError("control authority must belong to demeet2k/Athena")
    if (
        normalized["fingerprint"]
        != _fingerprint(normalized["public_key_base64"])
    ):
        raise ValueError("control authority fingerprint mismatch")
    if _parsed_timestamp(normalized["valid_until"]) <= _parsed_timestamp(
        normalized["valid_from"]
    ):
        raise ValueError("control authority validity window is empty")
    return normalized


class FrozenProviderAdmissionExecutionGate:
    """Frozen W19 authority registry and compositional execution gate."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w18_registry: FrozenProviderTrustRegistry,
        authorities: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.w18_registry = w18_registry
        self.authorities = authorities

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w18_registry: FrozenProviderTrustRegistry | None = None,
    ) -> "FrozenProviderAdmissionExecutionGate":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise ProviderAdmissionExecutionError(
                "unexpected W19 schema or phase"
            )
        w18_registry = w18_registry or FrozenProviderTrustRegistry.load()
        expected_predecessor = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w18_head": W18_HEAD,
            "w18_tree": W18_TREE,
            "adapter_return_contract_digest": (
                "sha256:fd00f6463d512004e0900c9d01a5735f"
                "6ba77de27849a9e7c094852fa1474a23"
            ),
            "provider_trust_contract_digest": (
                "sha256:0f7f62e6e0ea83d6ee89d961ca880254"
                "cd1535ff40c794b81a1f46a1f3bfb571"
            ),
            "adapter_return_receipt_id": (
                "w18-adapter-return:sha256:"
                "91c918cbc21cdacb31b8c3420f4c5c3fb59e41a8cfb6deff32bb544527cb95fb"
            ),
            "provider_trust_receipt_id": (
                "w18-provider-trust:sha256:"
                "6bb7286a78d8db9f01277fe3fa989012be06034c25db3370092c71b5c17feca0"
            ),
            "convergence_receipt_id": (
                "w18-convergence:sha256:"
                "b557b74a14c16f3c2cfe578a35dbef19382586a508043fae6c178692f531e525"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise ProviderAdmissionExecutionError(
                "W19 predecessor lineage mismatch"
            )

        registry = _exact_object(
            snapshot.get("control_authority_registry"),
            {
                "schema",
                "canonicalization",
                "signature_algorithm",
                "signature_encoding",
                "authority_key_kind",
                "authorities",
            },
            "control_authority_registry",
        )
        expected_registry_scalars = {
            "schema": CONTROL_REGISTRY_SCHEMA,
            "canonicalization": "KC144.CANON.JSON.V1",
            "signature_algorithm": "ed25519",
            "signature_encoding": "base64",
            "authority_key_kind": "ed25519-public-key",
        }
        for field, expected in expected_registry_scalars.items():
            if registry.get(field) != expected:
                raise ProviderAdmissionExecutionError(
                    f"W19 control registry {field} drift"
                )
        authority_rows = registry.get("authorities")
        if not isinstance(authority_rows, list):
            raise ProviderAdmissionExecutionError(
                "W19 control authorities must be a list"
            )
        authorities: dict[str, dict[str, Any]] = {}
        for row in authority_rows:
            normalized = _normalize_authority(row)
            authority_id = normalized["authority_id"]
            if authority_id in authorities:
                raise ProviderAdmissionExecutionError(
                    "duplicate W19 control authority"
                )
            authorities[authority_id] = normalized

        expected_admission = {
            "provider_admission_schema": ADMISSION_SCHEMA,
            "provider_return_schema": RETURN_SCHEMA,
            "control_authority_must_be_commit_pinned": True,
            "self_supplied_control_keys_allowed": False,
            "provider_key_requires_control_signature": True,
            "exact_w18_head_and_tree_required": True,
            "provider_return_requires_admitted_provider_key": True,
            "production_control_authority_count": len(authorities),
            "runtime_can_mutate_authority_registry": False,
            "runtime_persists_submitted_admissions": False,
        }
        if snapshot.get("admission_contract") != expected_admission:
            raise ProviderAdmissionExecutionError(
                "W19 admission contract drift"
            )

        expected_execution = {
            "execution_authorization_schema": EXECUTION_SCHEMA,
            "workflow_path": WORKFLOW_PATH,
            "workflow_ref_policy": "EXACT_W18_CANDIDATE_HEAD_REQUIRED",
            "candidate_head": W18_HEAD,
            "candidate_tree": W18_TREE,
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "execute_live_witness_default": False,
            "separate_control_signature_required": True,
            "protected_environment_approval_required": True,
            "bearer_available_only_at_job_runtime": True,
            "runtime_dispatch_capability": "NONE",
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if snapshot.get("execution_contract") != expected_execution:
            raise ProviderAdmissionExecutionError(
                "W19 execution contract drift"
            )

        expected_boundaries = {
            "control_authority_pinned": bool(authorities),
            "provider_adapter_control_admitted": False,
            "provider_trust_anchor_pinned": False,
            "provider_return_signature_verified": False,
            "execution_authorization_verified": False,
            "protected_environment_approved": False,
            "bearer_secret_available_at_runtime": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admission_recorded": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise ProviderAdmissionExecutionError(
                "W19 boundary state drift"
            )
        if snapshot.get("successor") != (
            "KC144.XNAV.W20::CONTROL-ADMITTED-PERSISTENT-"
            "WITNESS-RETURN-AND-IC10-REVIEW"
        ):
            raise ProviderAdmissionExecutionError("W19 successor drift")
        contract_material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(contract_material):
            raise ProviderAdmissionExecutionError(
                "W19 contract digest mismatch"
            )
        return cls(snapshot, w18_registry, authorities)

    @classmethod
    def load(
        cls, path: Path = DATA_PATH
    ) -> "FrozenProviderAdmissionExecutionGate":
        return cls.from_snapshot(_load_json(path))

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "W19_ADMISSION_AND_EXECUTION_GATE_READY__"
                "CONTROL_AUTHORITY_AND_LIVE_WITNESS_OPEN"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w18_head": W18_HEAD,
            "w18_tree": W18_TREE,
            "control_registry_schema": CONTROL_REGISTRY_SCHEMA,
            "production_control_authority_count": len(self.authorities),
            "registered_control_authorities": sorted(self.authorities),
            "self_supplied_control_keys_allowed": False,
            "provider_key_requires_control_signature": True,
            "execution_authorization_requires_separate_signature": True,
            "workflow": deepcopy(self.snapshot["execution_contract"]),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "cross_navigation_state": (
                "W18_CRYPTO_AND_RETURN_CONVERGED__"
                "W19_CONTROL_ADMISSION_AND_EXECUTION_GATE_READY__"
                "EXTERNAL_AUTHORITY_AND_LIVE_WITNESS_OPEN"
            ),
            "successor": self.snapshot["successor"],
        }

    def build_admission_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> dict[str, Any]:
        try:
            context, inspected = self.w18_registry._w17_context(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
            if context is None:
                return {
                    **inspected,
                    "admission_status": "HOLD_W17_PROVENANCE_REJECTED",
                }
            template = {
                "schema": ADMISSION_SCHEMA,
                "candidate_head": W18_HEAD,
                "candidate_tree": W18_TREE,
                "w18_contracts": {
                    "adapter_return_contract_digest": self.snapshot[
                        "predecessor"
                    ]["adapter_return_contract_digest"],
                    "provider_trust_contract_digest": self.snapshot[
                        "predecessor"
                    ]["provider_trust_contract_digest"],
                    "convergence_receipt_id": self.snapshot["predecessor"][
                        "convergence_receipt_id"
                    ],
                },
                "adapter": {
                    "adapter_id": None,
                    "provider_id": context["provider_id"],
                    "account_scope": context["account_scope"],
                    "environment": context["environment"],
                    "evidence_origin": context["evidence_origin"],
                    "verification_method": (
                        "ed25519-detached-canonical-json"
                    ),
                    "attests_authorization": True,
                    "trust_anchor": {
                        "kind": "ed25519-public-key",
                        "key_id": None,
                        "public_key_base64": None,
                        "fingerprint": None,
                    },
                },
                "authorization": {
                    "authority_id": None,
                    "control_repository": "demeet2k/Athena",
                    "control_pull_request": None,
                    "control_commit": None,
                    "control_ref": None,
                    "admitted_at": None,
                    "expires_at": None,
                },
                "signature": {
                    "algorithm": "ed25519",
                    "key_id": None,
                    "value": None,
                },
                "admission_digest": None,
            }
            return {
                "status": "HOLD_CONTROL_AUTHORITY_NOT_PINNED",
                "template": template,
                "production_control_authority_count": len(self.authorities),
                "self_supplied_control_authority_field_present": False,
                "provider_key_trusted": False,
                "control_signature_verified": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def _normalize_admission(self, submitted: Any) -> dict[str, Any]:
        _assert_secret_free(submitted, "provider_admission")
        value = _exact_object(
            submitted,
            ADMISSION_FIELDS,
            "provider admission",
        )
        contracts = _exact_object(
            value.get("w18_contracts"),
            W18_CONTRACT_FIELDS,
            "w18_contracts",
        )
        normalized_contracts = {
            "adapter_return_contract_digest": _sha(
                contracts.get("adapter_return_contract_digest"),
                "w18_contracts.adapter_return_contract_digest",
            ),
            "provider_trust_contract_digest": _sha(
                contracts.get("provider_trust_contract_digest"),
                "w18_contracts.provider_trust_contract_digest",
            ),
            "convergence_receipt_id": _bounded_text(
                contracts.get("convergence_receipt_id"),
                "w18_contracts.convergence_receipt_id",
            ),
        }
        expected_contracts = {
            field: self.snapshot["predecessor"][field]
            for field in W18_CONTRACT_FIELDS
        }
        if normalized_contracts != expected_contracts:
            raise ValueError("provider admission W18 contract binding mismatch")

        adapter = _exact_object(
            value.get("adapter"),
            ADAPTER_FIELDS,
            "adapter",
        )
        anchor = _exact_object(
            adapter.get("trust_anchor"),
            ANCHOR_FIELDS,
            "adapter.trust_anchor",
        )
        normalized_anchor = {
            "kind": _bounded_text(
                anchor.get("kind"), "adapter.trust_anchor.kind"
            ),
            "key_id": _bounded_text(
                anchor.get("key_id"), "adapter.trust_anchor.key_id"
            ),
            "public_key_base64": _bounded_text(
                anchor.get("public_key_base64"),
                "adapter.trust_anchor.public_key_base64",
            ),
            "fingerprint": _sha(
                anchor.get("fingerprint"),
                "adapter.trust_anchor.fingerprint",
            ),
        }
        if normalized_anchor["kind"] != "ed25519-public-key":
            raise ValueError("provider trust anchor kind must be ed25519-public-key")
        if normalized_anchor["fingerprint"] != _fingerprint(
            normalized_anchor["public_key_base64"]
        ):
            raise ValueError("provider trust-anchor fingerprint mismatch")
        normalized_adapter = {
            "adapter_id": _bounded_text(
                adapter.get("adapter_id"), "adapter.adapter_id"
            ),
            "provider_id": _bounded_text(
                adapter.get("provider_id"), "adapter.provider_id"
            ),
            "account_scope": _bounded_text(
                adapter.get("account_scope"), "adapter.account_scope"
            ),
            "environment": _bounded_text(
                adapter.get("environment"), "adapter.environment"
            ),
            "evidence_origin": _origin(
                adapter.get("evidence_origin"), "adapter.evidence_origin"
            ),
            "verification_method": _bounded_text(
                adapter.get("verification_method"),
                "adapter.verification_method",
            ),
            "attests_authorization": adapter.get("attests_authorization"),
            "trust_anchor": normalized_anchor,
        }
        if (
            normalized_adapter["verification_method"]
            != "ed25519-detached-canonical-json"
            or normalized_adapter["attests_authorization"] is not True
        ):
            raise ValueError(
                "provider admission must attest authorization with Ed25519"
            )

        authorization = _exact_object(
            value.get("authorization"),
            ADMISSION_AUTHORIZATION_FIELDS,
            "authorization",
        )
        pull_request = authorization.get("control_pull_request")
        if not isinstance(pull_request, int) or isinstance(
            pull_request, bool
        ) or pull_request < 1:
            raise ValueError("authorization.control_pull_request must be positive")
        normalized_authorization = {
            "authority_id": _bounded_text(
                authorization.get("authority_id"),
                "authorization.authority_id",
            ),
            "control_repository": _bounded_text(
                authorization.get("control_repository"),
                "authorization.control_repository",
            ),
            "control_pull_request": pull_request,
            "control_commit": _commit(
                authorization.get("control_commit"),
                "authorization.control_commit",
            ),
            "control_ref": _bounded_text(
                authorization.get("control_ref"),
                "authorization.control_ref",
            ),
            "admitted_at": _timestamp(
                authorization.get("admitted_at"),
                "authorization.admitted_at",
            ),
            "expires_at": _timestamp(
                authorization.get("expires_at"),
                "authorization.expires_at",
            ),
        }
        if normalized_authorization["control_repository"] != "demeet2k/Athena":
            raise ValueError("provider admission must return through demeet2k/Athena")
        if _parsed_timestamp(
            normalized_authorization["expires_at"]
        ) <= _parsed_timestamp(normalized_authorization["admitted_at"]):
            raise ValueError("provider admission validity window is empty")

        normalized = {
            "schema": _bounded_text(value.get("schema"), "schema"),
            "candidate_head": _commit(
                value.get("candidate_head"), "candidate_head"
            ),
            "candidate_tree": _commit(
                value.get("candidate_tree"), "candidate_tree"
            ),
            "w18_contracts": normalized_contracts,
            "adapter": normalized_adapter,
            "authorization": normalized_authorization,
            "signature": _normalized_signature(
                value.get("signature"), "signature"
            ),
            "admission_digest": _sha(
                value.get("admission_digest"), "admission_digest"
            ),
        }
        if normalized["schema"] != ADMISSION_SCHEMA:
            raise ValueError(f"schema must be {ADMISSION_SCHEMA}")
        if (
            normalized["candidate_head"] != W18_HEAD
            or normalized["candidate_tree"] != W18_TREE
        ):
            raise ValueError("provider admission must bind exact W18 head and tree")
        if normalized["admission_digest"] != _digest(
            _addressed_material(normalized, "admission_digest")
        ):
            raise ValueError("provider admission digest mismatch")
        return normalized

    def inspect_admission(self, admission_json: str) -> dict[str, Any]:
        try:
            if not isinstance(admission_json, str) or len(admission_json) > 65536:
                raise ValueError("provider admission must be bounded JSON")
            normalized = self._normalize_admission(json.loads(admission_json))
            authorization = normalized["authorization"]
            authority = self.authorities.get(authorization["authority_id"])
            if authority is None:
                return self._hold(
                    "HOLD_CONTROL_AUTHORITY_NOT_PINNED",
                    "authority_id is not present in the commit-pinned registry",
                    admission_digest=normalized["admission_digest"],
                )
            signature = normalized["signature"]
            if signature["key_id"] != authority["key_id"]:
                raise ValueError("control signature key_id mismatch")
            if authority["repository"] != authorization["control_repository"]:
                raise ValueError("control authority repository mismatch")
            admitted_at = _parsed_timestamp(authorization["admitted_at"])
            expires_at = _parsed_timestamp(authorization["expires_at"])
            if admitted_at < _parsed_timestamp(authority["valid_from"]):
                raise ValueError("provider admission precedes authority validity")
            if expires_at > _parsed_timestamp(authority["valid_until"]):
                raise ValueError("provider admission exceeds authority validity")
            if not _verify_ed25519_signature(
                authority["public_key_base64"],
                signature["value"],
                _unsigned_material(normalized, "admission_digest"),
            ):
                raise ValueError("control admission Ed25519 signature invalid")
            adapter = normalized["adapter"]
            w18_adapter = {
                **deepcopy(adapter),
                "admission": {
                    "authority": authorization["authority_id"],
                    "reference": authorization["control_ref"],
                    "admitted_at": authorization["admitted_at"],
                    "commit": authorization["control_commit"],
                },
            }
            return {
                "status": "PASS_CONTROL_SIGNED_PROVIDER_ADAPTER_ADMISSION",
                "schema": ADMISSION_SCHEMA,
                "admission_digest": normalized["admission_digest"],
                "adapter_id": adapter["adapter_id"],
                "provider_id": adapter["provider_id"],
                "provider_trust_anchor_fingerprint": adapter["trust_anchor"][
                    "fingerprint"
                ],
                "control_authority_id": authorization["authority_id"],
                "control_authority_fingerprint": authority["fingerprint"],
                "control_signature_verified": True,
                "provider_adapter_control_admitted": True,
                "provider_key_trusted_for_admission_window": True,
                "submitted_admission_persisted_by_runtime": False,
                "normalized_admission": normalized,
                "w18_adapter_profile": w18_adapter,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def inspect_admitted_provider_return(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        admission_json: str,
        provider_return_json: str,
    ) -> dict[str, Any]:
        admission = self.inspect_admission(admission_json)
        if not admission["status"].startswith(
            "PASS_CONTROL_SIGNED_PROVIDER_ADAPTER_ADMISSION"
        ):
            return {
                **admission,
                "provider_return_status": "HOLD_PROVIDER_ADMISSION_REJECTED",
            }
        adapter = admission["w18_adapter_profile"]
        admitted_registry = FrozenProviderTrustRegistry(
            self.w18_registry.snapshot,
            self.w18_registry.predecessor,
            {adapter["adapter_id"]: adapter},
        )
        provider_return = admitted_registry.inspect_provider_return(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_return_json,
        )
        if not provider_return["status"].startswith(
            "PASS_PINNED_PROVIDER_RETURN_SIGNATURE"
        ):
            return {
                **provider_return,
                "provider_admission_digest": admission["admission_digest"],
                "control_signature_verified": True,
            }
        return {
            "status": "PASS_CONTROL_ADMITTED_PROVIDER_RETURN_SIGNATURE",
            "provider_admission_digest": admission["admission_digest"],
            "provider_return_digest": provider_return[
                "provider_return_digest"
            ],
            "provenance_binding_digest": provider_return[
                "provenance_binding_digest"
            ],
            "adapter_id": provider_return["adapter_id"],
            "trust_anchor_fingerprint": provider_return[
                "trust_anchor_fingerprint"
            ],
            "control_signature_verified": True,
            "provider_return_signature_verified": True,
            "authorization_externally_verified": True,
            "evidence_class": "CONTROL_ADMITTED_EXTERNALLY_VERIFIED_PROVIDER_EVIDENCE",
            "submitted_inputs_persisted": False,
            **self._negative_boundaries(),
        }

    def compile_execution_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        admission_json: str,
        provider_return_json: str,
    ) -> dict[str, Any]:
        inspected = self.inspect_admitted_provider_return(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            admission_json,
            provider_return_json,
        )
        if not inspected["status"].startswith(
            "PASS_CONTROL_ADMITTED_PROVIDER_RETURN_SIGNATURE"
        ):
            return {
                **inspected,
                "execution_authorization_status": (
                    "HOLD_ADMISSION_OR_PROVIDER_RETURN_REJECTED"
                ),
            }
        admission = self.inspect_admission(admission_json)
        template = {
            "schema": EXECUTION_SCHEMA,
            "candidate_head": W18_HEAD,
            "candidate_tree": W18_TREE,
            "provider_admission_digest": inspected[
                "provider_admission_digest"
            ],
            "provider_return_digest": inspected["provider_return_digest"],
            "workflow": {
                "path": WORKFLOW_PATH,
                "ref": W18_HEAD,
                "environment": WITNESS_PLAN["environment"],
                "secret_name": WITNESS_PLAN["secret_name"],
                "sample_count": WITNESS_PLAN["sample_count"],
                "interval_seconds": WITNESS_PLAN["interval_seconds"],
                "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
                "execute_live_witness": True,
            },
            "authorization": {
                "authority_id": admission["control_authority_id"],
                "control_ref": None,
                "authorized_at": None,
                "expires_at": None,
            },
            "signature": {
                "algorithm": "ed25519",
                "key_id": None,
                "value": None,
            },
            "execution_digest": None,
        }
        return {
            "status": "EXECUTION_AUTHORIZATION_TEMPLATE_READY",
            "template": template,
            "provider_admission_digest": inspected[
                "provider_admission_digest"
            ],
            "provider_return_digest": inspected["provider_return_digest"],
            "execution_authorization_verified": False,
            "workflow_dispatched": False,
            **self._negative_boundaries(),
        }

    def _normalize_execution(self, submitted: Any) -> dict[str, Any]:
        _assert_secret_free(submitted, "execution_authorization")
        value = _exact_object(
            submitted,
            EXECUTION_FIELDS,
            "execution authorization",
        )
        workflow = _exact_object(
            value.get("workflow"), WORKFLOW_FIELDS, "workflow"
        )
        normalized_workflow = {
            "path": _bounded_text(workflow.get("path"), "workflow.path"),
            "ref": _commit(workflow.get("ref"), "workflow.ref"),
            "environment": _bounded_text(
                workflow.get("environment"), "workflow.environment"
            ),
            "secret_name": _bounded_text(
                workflow.get("secret_name"), "workflow.secret_name"
            ),
            "sample_count": workflow.get("sample_count"),
            "interval_seconds": workflow.get("interval_seconds"),
            "minimum_span_seconds": workflow.get("minimum_span_seconds"),
            "execute_live_witness": workflow.get("execute_live_witness"),
        }
        expected_workflow = {
            "path": WORKFLOW_PATH,
            "ref": W18_HEAD,
            "environment": WITNESS_PLAN["environment"],
            "secret_name": WITNESS_PLAN["secret_name"],
            "sample_count": WITNESS_PLAN["sample_count"],
            "interval_seconds": WITNESS_PLAN["interval_seconds"],
            "minimum_span_seconds": WITNESS_PLAN["minimum_span_seconds"],
            "execute_live_witness": True,
        }
        if normalized_workflow != expected_workflow:
            raise ValueError("execution authorization workflow binding mismatch")
        authorization = _exact_object(
            value.get("authorization"),
            EXECUTION_AUTHORIZATION_FIELDS,
            "authorization",
        )
        normalized_authorization = {
            "authority_id": _bounded_text(
                authorization.get("authority_id"),
                "authorization.authority_id",
            ),
            "control_ref": _bounded_text(
                authorization.get("control_ref"),
                "authorization.control_ref",
            ),
            "authorized_at": _timestamp(
                authorization.get("authorized_at"),
                "authorization.authorized_at",
            ),
            "expires_at": _timestamp(
                authorization.get("expires_at"),
                "authorization.expires_at",
            ),
        }
        if _parsed_timestamp(
            normalized_authorization["expires_at"]
        ) <= _parsed_timestamp(normalized_authorization["authorized_at"]):
            raise ValueError("execution authorization validity window is empty")
        normalized = {
            "schema": _bounded_text(value.get("schema"), "schema"),
            "candidate_head": _commit(
                value.get("candidate_head"), "candidate_head"
            ),
            "candidate_tree": _commit(
                value.get("candidate_tree"), "candidate_tree"
            ),
            "provider_admission_digest": _sha(
                value.get("provider_admission_digest"),
                "provider_admission_digest",
            ),
            "provider_return_digest": _sha(
                value.get("provider_return_digest"),
                "provider_return_digest",
            ),
            "workflow": normalized_workflow,
            "authorization": normalized_authorization,
            "signature": _normalized_signature(
                value.get("signature"), "signature"
            ),
            "execution_digest": _sha(
                value.get("execution_digest"), "execution_digest"
            ),
        }
        if normalized["schema"] != EXECUTION_SCHEMA:
            raise ValueError(f"schema must be {EXECUTION_SCHEMA}")
        if (
            normalized["candidate_head"] != W18_HEAD
            or normalized["candidate_tree"] != W18_TREE
        ):
            raise ValueError("execution authorization must bind W18 head and tree")
        if normalized["execution_digest"] != _digest(
            _addressed_material(normalized, "execution_digest")
        ):
            raise ValueError("execution authorization digest mismatch")
        return normalized

    def evaluate_execution(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
    ) -> dict[str, Any]:
        provider = self.inspect_admitted_provider_return(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            admission_json,
            provider_return_json,
        )
        if not provider["status"].startswith(
            "PASS_CONTROL_ADMITTED_PROVIDER_RETURN_SIGNATURE"
        ):
            return {
                **provider,
                "execution_status": "HOLD_PROVIDER_RETURN_REJECTED",
            }
        admission = self.inspect_admission(admission_json)
        try:
            if (
                not isinstance(execution_authorization_json, str)
                or len(execution_authorization_json) > 65536
            ):
                raise ValueError(
                    "execution authorization must be bounded JSON"
                )
            execution = self._normalize_execution(
                json.loads(execution_authorization_json)
            )
            if execution["provider_admission_digest"] != provider[
                "provider_admission_digest"
            ]:
                raise ValueError("execution provider admission digest mismatch")
            if execution["provider_return_digest"] != provider[
                "provider_return_digest"
            ]:
                raise ValueError("execution provider return digest mismatch")
            if (
                execution["authorization"]["authority_id"]
                != admission["control_authority_id"]
            ):
                raise ValueError("execution control authority mismatch")
            authority = self.authorities.get(
                execution["authorization"]["authority_id"]
            )
            if authority is None:
                return self._hold(
                    "HOLD_CONTROL_AUTHORITY_NOT_PINNED",
                    "execution authority is not commit-pinned",
                    admission_digest=provider[
                        "provider_admission_digest"
                    ],
                )
            signature = execution["signature"]
            if signature["key_id"] != authority["key_id"]:
                raise ValueError("execution signature key_id mismatch")
            admitted = admission["normalized_admission"]["authorization"]
            authorized_at = _parsed_timestamp(
                execution["authorization"]["authorized_at"]
            )
            expires_at = _parsed_timestamp(
                execution["authorization"]["expires_at"]
            )
            if authorized_at < _parsed_timestamp(admitted["admitted_at"]):
                raise ValueError("execution authorization precedes admission")
            if expires_at > _parsed_timestamp(admitted["expires_at"]):
                raise ValueError("execution authorization exceeds admission")
            if authorized_at < _parsed_timestamp(authority["valid_from"]):
                raise ValueError("execution precedes control authority validity")
            if expires_at > _parsed_timestamp(authority["valid_until"]):
                raise ValueError("execution exceeds control authority validity")
            if not _verify_ed25519_signature(
                authority["public_key_base64"],
                signature["value"],
                _unsigned_material(execution, "execution_digest"),
            ):
                raise ValueError(
                    "execution authorization Ed25519 signature invalid"
                )
            gates = {
                "w18_exact_head_and_tree_bound": True,
                "control_authority_commit_pinned": True,
                "provider_adapter_control_admitted": True,
                "provider_return_signature_verified": True,
                "execution_authorization_signature_verified": True,
                "protected_environment_approved": False,
                "bearer_secret_available_at_job_runtime": False,
                "explicit_workflow_dispatch_observed": False,
                "three_sample_persistent_witness_returned": False,
                "external_return_persistence_verified": False,
                "control_plane_witness_admission_recorded": False,
            }
            return {
                "status": (
                    "PASS_CONTROL_SIGNED_PROTECTED_EXECUTION_AUTHORIZATION__"
                    "NOT_DISPATCHED"
                ),
                "schema": EXECUTION_SCHEMA,
                "execution_digest": execution["execution_digest"],
                "provider_admission_digest": provider[
                    "provider_admission_digest"
                ],
                "provider_return_digest": provider[
                    "provider_return_digest"
                ],
                "control_authority_id": authority["authority_id"],
                "control_signature_verified": True,
                "provider_return_signature_verified": True,
                "execution_authorization_verified": True,
                "protected_execution_authorized": True,
                "dispatch_eligible_in_protected_workflow": True,
                "gates": gates,
                "passed_gates": [
                    name for name, passed in gates.items() if passed
                ],
                "open_gates": [
                    name for name, passed in gates.items() if not passed
                ],
                "submitted_inputs_persisted": False,
                "workflow_dispatched": False,
                "endpoint_contacted": False,
                "persistent_witness_executed": False,
                "persistent_witness_return_persisted": False,
                "control_plane_admission_recorded": False,
                "deployment_claimed": False,
                "merge_claimed": False,
                "promotion_claimed": False,
                "runtime_can_promote": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    @staticmethod
    def _negative_boundaries() -> dict[str, Any]:
        return {
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "persistent_witness_return_persisted": False,
            "control_plane_admission_recorded": False,
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
        *,
        admission_digest: str | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "error": reason,
            "admission_digest": admission_digest,
            "production_control_authority_count": len(self.authorities),
            "control_signature_verified": False,
            "provider_adapter_control_admitted": False,
            "provider_return_signature_verified": False,
            "execution_authorization_verified": False,
            "submitted_inputs_persisted": False,
            **self._negative_boundaries(),
        }

    def _rejected(self, reason: str) -> dict[str, Any]:
        return {
            "status": "HOLD_W19_ADMISSION_OR_EXECUTION_REJECTED",
            "error": reason,
            "production_control_authority_count": len(self.authorities),
            "control_signature_verified": False,
            "provider_adapter_control_admitted": False,
            "provider_return_signature_verified": False,
            "execution_authorization_verified": False,
            "submitted_inputs_persisted": False,
            **self._negative_boundaries(),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_provider_admission_execution(mcp: Any) -> None:
    """Register W19 control-admission and protected-execution surfaces."""

    gate = FrozenProviderAdmissionExecutionGate.load()

    @mcp.tool()
    def athena_w19_provider_admission_status() -> str:
        """Report the frozen W19 control registry and execution boundary."""
        return _render(gate.status())

    @mcp.tool()
    def build_athena_w19_provider_admission_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
    ) -> str:
        """Build an exact W18-bound provider-admission template."""
        return _render(
            gate.build_admission_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w19_provider_admission(
        provider_admission_json: str,
    ) -> str:
        """Verify a control-signed provider adapter admission."""
        return _render(gate.inspect_admission(provider_admission_json))

    @mcp.tool()
    def inspect_athena_w19_admitted_provider_return(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
    ) -> str:
        """Verify a provider return through a control-admitted provider key."""
        return _render(
            gate.inspect_admitted_provider_return(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
            )
        )

    @mcp.tool()
    def compile_athena_w19_execution_authorization_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
    ) -> str:
        """Compile the separately signed exact-head execution template."""
        return _render(
            gate.compile_execution_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
            )
        )

    @mcp.tool()
    def evaluate_athena_w19_protected_witness_execution(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
    ) -> str:
        """Verify W19 execution authority without dispatching or persisting."""
        return _render(
            gate.evaluate_execution(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
            )
        )

    @mcp.resource("athena://w19-provider-admission-execution")
    def provider_admission_execution_resource() -> str:
        """Return the frozen W19 admission/execution status."""
        return _render(gate.status())
