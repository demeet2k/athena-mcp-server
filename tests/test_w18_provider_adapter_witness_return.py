"""Fail-closed tests for KC144.XNAV.W18."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.evidence_provenance_gate import (  # noqa: E402
    FrozenEvidenceProvenanceGate,
    provenance_attestation_digest,
)
from crystal_108d.provider_adapter_witness_return import (  # noqa: E402
    FrozenProviderAdapterWitnessReturn,
    ProviderAdapterWitnessReturnError,
    persistent_witness_return_digest,
    provider_adapter_profile_digest,
    provider_trust_receipt_digest,
    register_provider_adapter_witness_return,
)
from crystal_108d.replay_authority_ledger import _digest  # noqa: E402


DATA = ROOT / "MCP" / "data" / "w18_provider_adapter_witness_return.json"
RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w18-provider-adapter-persistent-witness-return.json"
)
CANDIDATE_HEAD = "c" * 40


def _contract() -> FrozenProviderAdapterWitnessReturn:
    return FrozenProviderAdapterWitnessReturn.load(DATA)


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": (
            "b4e24de38788ecdf30f43514ece279d1270b998b"
        ),
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": (
            "ghcr.io/demeet2k/athena-mcp-server@sha256:"
            "31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
        ),
        "provider": {
            "id": "synthetic-provider",
            "account_scope": "synthetic-account",
            "deployment_id": "synthetic-deployment",
            "deployment_observed_at": "2026-07-27T08:05:00-07:00",
            "evidence_url": (
                "https://evidence.invalid-domain.example.net/deploy/1"
            ),
        },
        "target": {
            "id": "synthetic-target",
            "endpoint": "https://athena.invalid-domain.example.net/mcp",
            "persistence_class": "managed-service",
            "secret_store_ref": "provider://synthetic/secret-reference",
        },
        "authorization": {
            "ref": "synthetic-authorization",
            "actor": "synthetic-authority",
            "authorized_at": "2026-07-27T08:00:00-07:00",
        },
        "witness": {
            "environment": "p10-persistent-host",
            "secret_name": "ATHENA_MCP_BEARER_TOKEN",
            "sample_count": 3,
            "interval_seconds": 20,
            "minimum_span_seconds": 40,
        },
        "authority": {
            "live_witness_authorized": True,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "secret_material_recorded": False,
    }


def _evidence() -> dict:
    packet = _packet()
    return {
        "schema": "athena.provider-deployment-evidence/v1",
        "provider_id": packet["provider"]["id"],
        "provider_account_scope": packet["provider"]["account_scope"],
        "deployment_id": packet["provider"]["deployment_id"],
        "target_id": packet["target"]["id"],
        "authorization_ref": packet["authorization"]["ref"],
        "deployed_image": packet["image"],
        "image_digest": (
            "sha256:"
            "31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
        ),
        "source_commit": packet["source_commit"],
        "runtime_p09_head": packet["runtime_p09_head"],
        "endpoint": packet["target"]["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": packet["provider"]["deployment_observed_at"],
        "secret_store_ref": packet["target"]["secret_store_ref"],
        "secret_material_recorded": False,
        "evidence_url": packet["provider"]["evidence_url"],
    }


def _provenance() -> dict:
    packet = _packet()
    evidence = _evidence()
    witness = {
        "schema": "athena.provider-evidence-provenance/v1",
        "evidence_digest": _digest(evidence),
        "retrieval": {
            "mode": "provider-api-read",
            "evidence_url": evidence["evidence_url"],
            "retrieved_at": "2026-07-27T15:06:00Z",
            "content_digest": _digest(evidence),
        },
        "verifier": {
            "identity": "synthetic-independent-verifier",
            "method": "credentialed-provider-api",
            "witness_ref": (
                "https://witness.invalid-domain.example.net/runs/1"
            ),
            "verified_at": "2026-07-27T15:07:00Z",
        },
        "authorization": deepcopy(packet["authorization"]),
        "trust_anchor": {
            "kind": "synthetic-provider-account",
            "reference": (
                "https://trust.invalid-domain.example.net/anchors/1"
            ),
            "fingerprint": "sha256:" + "a" * 64,
        },
        "assertions": {
            "provider_evidence_fetched": True,
            "external_evidence_verified": True,
            "authorization_externally_verified": True,
            "secret_material_recorded": False,
        },
        "attestation_digest": "",
    }
    witness["attestation_digest"] = provenance_attestation_digest(witness)
    return witness


def _profile() -> dict:
    packet = _packet()
    provenance = _provenance()
    profile = {
        "schema": "athena.provider-adapter-profile/v1",
        "provider_id": packet["provider"]["id"],
        "adapter": {
            "id": "synthetic-provider/v1",
            "version": "1.0.0",
            "kind": "credentialed-provider-api",
            "retrieval_mode": "provider-api-read",
            "verification_method": "credentialed-provider-api",
        },
        "identity_binding": {
            "account_scope": packet["provider"]["account_scope"],
            "deployment_id": packet["provider"]["deployment_id"],
            "evidence_origin": "https://evidence.invalid-domain.example.net",
            "endpoint_origin": "https://athena.invalid-domain.example.net",
        },
        "trust_anchor": {
            "kind": provenance["trust_anchor"]["kind"],
            "issuer": "synthetic-provider-issuer",
            "reference": provenance["trust_anchor"]["reference"],
            "fingerprint": provenance["trust_anchor"]["fingerprint"],
            "signature_algorithm": "ed25519",
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
        "profile_digest": "",
    }
    profile["profile_digest"] = provider_adapter_profile_digest(profile)
    return profile


def _w17_binding() -> dict:
    return FrozenEvidenceProvenanceGate.load().inspect_provenance(
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
    )


def _trust_receipt() -> dict:
    packet = _packet()
    evidence = _evidence()
    profile = _profile()
    binding = _w17_binding()
    signed_payload_digest = _digest(
        {
            "adapter_profile_digest": profile["profile_digest"],
            "provenance_binding_digest": binding[
                "provenance_binding_digest"
            ],
            "provider_evidence_digest": _digest(evidence),
            "authorization_ref": packet["authorization"]["ref"],
            "trust_anchor_fingerprint": profile["trust_anchor"]["fingerprint"],
        }
    )
    receipt = {
        "schema": "athena.provider-trust-verification-receipt/v1",
        "adapter_profile_digest": profile["profile_digest"],
        "provenance_binding_digest": binding["provenance_binding_digest"],
        "provider_evidence_digest": _digest(evidence),
        "provider_id": packet["provider"]["id"],
        "provider_account_scope": packet["provider"]["account_scope"],
        "deployment_id": packet["provider"]["deployment_id"],
        "trust_anchor_fingerprint": profile["trust_anchor"]["fingerprint"],
        "verification": {
            "method": "credentialed-provider-api",
            "signature_algorithm": "ed25519",
            "signed_payload_digest": signed_payload_digest,
            "verified_at": "2026-07-27T15:08:00Z",
            "verifier_identity": "synthetic-provider-adapter-runner",
            "external_run_ref": (
                "https://runner.invalid-domain.example.net/runs/2"
            ),
        },
        "assertions": {
            "provider_adapter_executed": True,
            "evidence_signature_verified": True,
            "account_scope_verified": True,
            "authorization_verified": True,
            "trust_anchor_verified": True,
            "secret_material_recorded": False,
        },
        "receipt_digest": "",
    }
    receipt["receipt_digest"] = provider_trust_receipt_digest(receipt)
    return receipt


def _dispatch_envelope() -> dict:
    result = _contract().compile_dispatch_envelope(
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
        json.dumps(_profile()),
        json.dumps(_trust_receipt()),
        CANDIDATE_HEAD,
        "2026-07-27T15:10:00Z",
    )
    assert result["status"].startswith("HOLD_DISPATCH_ENVELOPE_COMPILED")
    return result["dispatch_envelope"]


def _witness_return() -> dict:
    packet = _packet()
    envelope = _dispatch_envelope()
    trust_receipt = _trust_receipt()
    tool_digest = "sha256:" + "1" * 64
    resource_digest = "sha256:" + "2" * 64
    observations = []
    for sequence, observed_at in enumerate(
        [
            "2026-07-27T15:11:00Z",
            "2026-07-27T15:11:20Z",
            "2026-07-27T15:11:40Z",
        ],
        start=1,
    ):
        observations.append(
            {
                "sequence": sequence,
                "observed_at": observed_at,
                "health_ready": True,
                "mcp_authenticated": True,
                "protocol": "2025-03-26",
                "endpoint_path": "/mcp",
                "source_commit": packet["source_commit"],
                "tool_count": 203,
                "resource_count": 36,
                "tool_inventory_digest": tool_digest,
                "resource_inventory_digest": resource_digest,
            }
        )
    returned = {
        "schema": "athena.persistent-mcp-witness-return/v1",
        "dispatch_envelope_digest": envelope["envelope_digest"],
        "candidate_head": CANDIDATE_HEAD,
        "provider_id": packet["provider"]["id"],
        "provider_account_scope": packet["provider"]["account_scope"],
        "deployment_id": packet["provider"]["deployment_id"],
        "endpoint": packet["target"]["endpoint"],
        "image": packet["image"],
        "source_commit": packet["source_commit"],
        "runtime_p09_head": packet["runtime_p09_head"],
        "started_at": "2026-07-27T15:10:30Z",
        "completed_at": "2026-07-27T15:12:00Z",
        "observations": observations,
        "provider_trust_receipt_digest": trust_receipt["receipt_digest"],
        "execution": {
            "workflow_run_ref": (
                "https://github.com/demeet2k/athena-mcp-server/actions/runs/1"
            ),
            "job_ref": (
                "https://github.com/demeet2k/athena-mcp-server/actions/runs/1/job/1"
            ),
            "protected_environment": "p10-persistent-host",
            "external_persistence_ref": (
                "https://witness.invalid-domain.example.net/returns/1"
            ),
            "return_signature_algorithm": "ed25519",
            "return_signature": "synthetic-ed25519-signature-not-verified",
            "signer_identity": "synthetic-provider-adapter-runner",
            "signer_trust_anchor_fingerprint": "sha256:" + "a" * 64,
        },
        "assertions": {
            "provider_trust_verified": True,
            "authorization_verified": True,
            "bearer_secret_available_at_runtime": True,
            "endpoint_contacted": True,
            "persistent_witness_executed": True,
            "external_return_persisted": True,
            "secret_material_recorded": False,
            "promotion_claimed": False,
        },
        "return_digest": "",
    }
    returned["return_digest"] = persistent_witness_return_digest(returned)
    return returned


def _return_args() -> tuple[str, str, str, str, str, str, str]:
    return (
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
        json.dumps(_profile()),
        json.dumps(_trust_receipt()),
        json.dumps(_dispatch_envelope()),
        json.dumps(_witness_return()),
    )


def test_frozen_w18_contract_binds_w17_and_preserves_authority() -> None:
    status = _contract().status()
    assert status["status"] == (
        "PROVIDER_ADAPTER_AND_WITNESS_RETURN_CONTRACT_READY__"
        "EXTERNAL_EXECUTION_NOT_PRESENT"
    )
    assert status["w17_contract_digest"] == (
        "sha256:8b8476b7e2b29a2c9bc59f9e2d25f85d"
        "8d39c31c73a16f7c1adbc61648aaa274"
    )
    assert status["provider_adapter_contract"][
        "committed_provider_profiles"
    ] == []
    assert status["boundaries"]["provider_selected"] is False
    assert status["boundaries"]["trust_anchor_verified"] is False
    assert status["boundaries"]["persistent_witness_executed"] is False


def test_template_is_bound_but_provider_and_execution_remain_unresolved() -> None:
    result = _contract().build_provider_adapter_template(
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
    )
    assert result["status"] == (
        "UNRESOLVED_PROVIDER_ADAPTER_AND_RETURN_TEMPLATE"
    )
    profile = result["provider_adapter_profile_template"]
    assert profile["provider_id"] == _packet()["provider"]["id"]
    assert profile["adapter"]["id"] is None
    assert profile["trust_anchor"]["signature_algorithm"] is None
    assert result["provider_selected"] is False
    assert result["provider_adapter_executed"] is False
    assert result["dispatch_allowed"] is False


def test_provider_adapter_profile_is_structurally_bound_not_executed() -> None:
    result = _contract().inspect_provider_adapter(
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
        json.dumps(_profile()),
    )
    assert result["status"] == (
        "PASS_PROVIDER_ADAPTER_PROFILE_BINDING__ADAPTER_EXECUTION_UNVERIFIED"
    )
    assert result["profile_class"] == (
        "PROVIDER_ADAPTER_PROFILE_STRUCTURALLY_BOUND"
    )
    assert result["provider_selected_by_repository"] is False
    assert result["adapter_executed_by_runtime"] is False
    assert result["external_signatures_verified_by_runtime"] is False
    assert result["dispatch_allowed"] is False


def test_exact_head_dispatch_envelope_compiles_but_never_dispatches() -> None:
    result = _contract().compile_dispatch_envelope(
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
        json.dumps(_profile()),
        json.dumps(_trust_receipt()),
        CANDIDATE_HEAD,
        "2026-07-27T15:10:00Z",
    )
    assert result["status"] == (
        "HOLD_DISPATCH_ENVELOPE_COMPILED__"
        "EXTERNAL_SIGNATURE_AND_PROTECTED_EXECUTION_REQUIRED"
    )
    envelope = result["dispatch_envelope"]
    assert envelope["candidate_head"] == CANDIDATE_HEAD
    assert envelope["workflow"]["protected_environment"] == (
        "p10-persistent-host"
    )
    assert envelope["constraints"]["execute_live_witness_default"] is False
    assert result["trust_receipt_signature_verified_by_runtime"] is False
    assert result["workflow_dispatched"] is False
    assert result["dispatch_allowed"] is False


def test_three_sample_return_is_structurally_bound_not_trusted() -> None:
    result = _contract().inspect_persistent_witness_return(*_return_args())
    assert result["status"] == (
        "PASS_STRUCTURAL_PROVIDER_AND_PERSISTENT_RETURN_BINDING__"
        "EXTERNAL_SIGNATURES_UNVERIFIED"
    )
    assert result["return_class"] == (
        "STRUCTURALLY_BOUND_PERSISTENT_WITNESS_RETURN"
    )
    assert result["sample_count"] == 3
    assert result["observed_span_seconds"] == 40
    assert result["trust_receipt_signature_verified_by_runtime"] is False
    assert result["witness_return_signature_verified_by_runtime"] is False
    assert result["endpoint_contacted_by_runtime"] is False
    assert result["persistent_witness_executed_by_runtime"] is False
    assert result["control_plane_admitted"] is False


def test_return_admission_closes_structure_and_keeps_five_external_gates() -> None:
    result = _contract().evaluate_return_admission(*_return_args())
    assert result["status"] == (
        "HOLD_PERSISTENT_WITNESS_ADMISSION__"
        "AUTHORIZED_EXTERNAL_EXECUTION_AND_SIGNATURE_VERIFICATION_OPEN"
    )
    assert result["passed_gates"] == [
        "w17_provenance_structurally_bound",
        "provider_adapter_profile_structurally_bound",
        "provider_trust_receipt_structurally_bound",
        "dispatch_envelope_exact_head_bound",
        "three_sample_persistent_return_structurally_bound",
    ]
    assert set(result["open_gates"]) == {
        "provider_adapter_execution_externally_witnessed",
        "trust_receipt_signature_cryptographically_verified",
        "witness_return_signature_cryptographically_verified",
        "external_return_persistence_verified",
        "control_plane_admission_recorded",
    }
    assert result["workflow_dispatched"] is False
    assert result["persistent_witness_return_persisted"] is False
    assert result["promotion_claimed"] is False


def test_interval_catalog_digest_secret_and_unknown_tampering_fail_closed() -> None:
    base = list(_return_args())
    variants = []

    short_interval = _witness_return()
    short_interval["observations"][1]["observed_at"] = (
        "2026-07-27T15:11:19Z"
    )
    short_interval["return_digest"] = persistent_witness_return_digest(
        short_interval
    )
    variants.append(short_interval)

    catalog_drift = _witness_return()
    catalog_drift["observations"][2]["tool_count"] = 204
    catalog_drift["return_digest"] = persistent_witness_return_digest(
        catalog_drift
    )
    variants.append(catalog_drift)

    wrong_digest = _witness_return()
    wrong_digest["return_digest"] = "sha256:" + "0" * 64
    variants.append(wrong_digest)

    secret = _witness_return()
    secret["bearer_token"] = "Bearer forbidden"
    variants.append(secret)

    unknown = _witness_return()
    unknown["notes"] = "not admitted"
    variants.append(unknown)

    for returned in variants:
        args = [*base[:-1], json.dumps(returned)]
        result = _contract().inspect_persistent_witness_return(*args)
        assert result["status"] == (
            "HOLD_W18_PROVIDER_ADAPTER_OR_RETURN_REJECTED"
        )
        assert result["external_signatures_verified_by_runtime"] is False
        assert result["workflow_dispatched"] is False
        assert result["control_plane_admitted"] is False


def test_policy_tampering_fails_before_registration() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    tampered = deepcopy(snapshot)
    tampered["provider_adapter_contract"]["provider_selected"] = True
    with pytest.raises(
        ProviderAdapterWitnessReturnError, match="provider-adapter contract drift"
    ):
        FrozenProviderAdapterWitnessReturn.from_snapshot(tampered)

    tampered = deepcopy(snapshot)
    tampered["persistent_witness_return_contract"][
        "runtime_dispatch_capability"
    ] = "WORKFLOW_WRITE"
    with pytest.raises(
        ProviderAdapterWitnessReturnError,
        match="persistent-witness return contract drift",
    ):
        FrozenProviderAdapterWitnessReturn.from_snapshot(tampered)


def test_w18_surfaces_register_without_network_dispatch_or_persistence() -> None:
    class FakeMCP:
        def __init__(self) -> None:
            self.tools: dict[str, object] = {}
            self.resources: dict[str, object] = {}

        def tool(self):
            def decorate(function):
                self.tools[function.__name__] = function
                return function

            return decorate

        def resource(self, uri: str):
            def decorate(function):
                self.resources[uri] = function
                return function

            return decorate

    fake = FakeMCP()
    register_provider_adapter_witness_return(fake)
    assert set(fake.tools) == {
        "athena_w18_provider_adapter_return_status",
        "build_athena_w18_provider_adapter_return_template",
        "inspect_athena_w18_provider_adapter_profile",
        "compile_athena_w18_protected_dispatch_envelope",
        "inspect_athena_w18_persistent_witness_return",
        "evaluate_athena_w18_persistent_witness_admission",
    }
    assert set(fake.resources) == {
        "athena://w18-provider-adapter-witness-return"
    }
    admission = json.loads(
        fake.tools["evaluate_athena_w18_persistent_witness_admission"](
            *_return_args()
        )
    )
    assert admission["workflow_dispatched"] is False
    assert admission["persistent_witness_return_persisted"] is False
    assert admission["control_plane_admitted"] is False


def test_w18_receipt_is_content_addressed_and_nonpromotional() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt_id = receipt.pop("receipt_id")
    digest = hashlib.sha256(
        json.dumps(
            receipt,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert receipt_id == f"w18-adapter-return:sha256:{digest}"
    assert receipt["validation"]["expanded_p08_regression_result"].startswith(
        "PASS_"
    )
    assert receipt["admission"]["control_plane_admitted"] is False
    assert receipt["boundaries"]["provider_adapter_executed"] is False
    assert receipt["boundaries"]["workflow_dispatched"] is False
    assert receipt["boundaries"]["persistent_witness_executed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
