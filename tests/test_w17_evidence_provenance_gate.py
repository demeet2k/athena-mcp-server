"""Fail-closed tests for KC144.XNAV.W17."""

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
    EvidenceProvenanceGateError,
    FrozenEvidenceProvenanceGate,
    provenance_attestation_digest,
    register_evidence_provenance_gate,
)
from crystal_108d.replay_authority_ledger import _digest  # noqa: E402


DATA = ROOT / "MCP" / "data" / "w17_evidence_provenance_gate.json"
RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w17-evidence-provenance-protected-dispatch-gate.json"
)


def _gate() -> FrozenEvidenceProvenanceGate:
    return FrozenEvidenceProvenanceGate.load(DATA)


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": "b4e24de38788ecdf30f43514ece279d1270b998b",
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": "ghcr.io/demeet2k/athena-mcp-server@sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2",
        "provider": {
            "id": "synthetic-provider",
            "account_scope": "synthetic-account",
            "deployment_id": "synthetic-deployment",
            "deployment_observed_at": "2026-07-27T08:05:00-07:00",
            "evidence_url": "https://evidence.invalid-domain.example.net/deploy/1",
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
        "image_digest": "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2",
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
            "witness_ref": "https://witness.invalid-domain.example.net/runs/1",
            "verified_at": "2026-07-27T15:07:00Z",
        },
        "authorization": deepcopy(packet["authorization"]),
        "trust_anchor": {
            "kind": "synthetic-provider-account",
            "reference": "https://trust.invalid-domain.example.net/anchors/1",
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


def _encoded() -> tuple[str, str, str]:
    return (
        json.dumps(_packet()),
        json.dumps(_evidence()),
        json.dumps(_provenance()),
    )


def test_frozen_w17_policy_binds_exact_w16_and_stays_fail_closed() -> None:
    status = _gate().status()
    assert status["status"] == (
        "EVIDENCE_PROVENANCE_GATE_READY__PROTECTED_DISPATCH_FAIL_CLOSED"
    )
    assert status["w16_ledger_root"] == (
        "sha256:4ae7fe2b2f390c876ca333cf5719b977"
        "97175d369997ce77f3329c47df0f316a"
    )
    assert status["contract_digest"] == (
        "sha256:8b8476b7e2b29a2c9bc59f9e2d25f85d"
        "8d39c31c73a16f7c1adbc61648aaa274"
    )
    assert status["boundaries"]["trust_anchor_verified"] is False
    assert status["boundaries"]["workflow_dispatched"] is False
    assert status["boundaries"]["persistent_witness_executed"] is False


def test_template_is_content_bound_but_explicitly_unresolved() -> None:
    packet_json, evidence_json, _ = _encoded()
    result = _gate().build_provenance_template(packet_json, evidence_json)
    assert result["status"] == "UNRESOLVED_EXTERNAL_PROVENANCE_WITNESS_TEMPLATE"
    assert result["template"]["evidence_digest"] == _digest(_evidence())
    assert result["template"]["retrieval"]["retrieved_at"] is None
    assert result["template"]["trust_anchor"]["fingerprint"] is None
    assert result["template"]["assertions"]["external_evidence_verified"] is False
    assert result["external_evidence_verified"] is False
    assert result["dispatch_allowed"] is False


def test_structural_provenance_binding_does_not_inflate_trust() -> None:
    result = _gate().inspect_provenance(*_encoded())
    assert result["status"] == (
        "PASS_STRUCTURAL_EVIDENCE_PROVENANCE_BINDING__"
        "TRUST_ANCHOR_UNVERIFIED"
    )
    assert result["provenance_claim_structurally_valid"] is True
    assert result["evidence_class"] == (
        "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM"
    )
    assert result["provider_trust_anchor_verified_by_runtime"] is False
    assert result["authorization_externally_verified_by_runtime"] is False
    assert result["provider_evidence_fetched_by_runtime"] is False
    assert result["submitted_inputs_persisted"] is False
    assert result["secret_material_accepted"] is False
    assert result["dispatch_allowed"] is False


def test_dispatch_candidate_is_addressable_but_remains_on_hold() -> None:
    result = _gate().evaluate_dispatch(*_encoded())
    assert result["status"] == (
        "HOLD_PROTECTED_DISPATCH__"
        "EXTERNAL_TRUST_AND_ENVIRONMENT_APPROVAL_OPEN"
    )
    assert result["dispatch_candidate_digest"].startswith("sha256:")
    assert result["passed_gates"] == [
        "activation_packet_structurally_valid",
        "provider_evidence_structurally_valid",
        "packet_evidence_fields_match",
        "provenance_claim_structurally_valid",
    ]
    assert set(result["open_gates"]) == {
        "provider_trust_anchor_verified",
        "authorization_externally_verified",
        "protected_environment_approved",
        "bearer_secret_available_at_job_runtime",
        "explicit_live_witness_dispatch",
    }
    assert result["workflow"]["execute_live_witness_default"] is False
    assert result["workflow_dispatched"] is False
    assert result["endpoint_contacted"] is False
    assert result["persistent_witness_executed"] is False
    assert result["dispatch_allowed"] is False
    assert result["promotion_claimed"] is False


def test_digest_timestamp_secret_and_unknown_field_tampering_fail_closed() -> None:
    packet_json, evidence_json, _ = _encoded()
    variants = []

    wrong_digest = _provenance()
    wrong_digest["evidence_digest"] = "sha256:" + "0" * 64
    variants.append(wrong_digest)

    wrong_time = _provenance()
    wrong_time["retrieval"]["retrieved_at"] = "2026-07-27T14:00:00Z"
    wrong_time["attestation_digest"] = provenance_attestation_digest(wrong_time)
    variants.append(wrong_time)

    secret = _provenance()
    secret["bearer_token"] = "Bearer forbidden"
    variants.append(secret)

    unknown = _provenance()
    unknown["notes"] = "not admitted"
    variants.append(unknown)

    for witness in variants:
        result = _gate().inspect_provenance(
            packet_json, evidence_json, json.dumps(witness)
        )
        assert result["status"] == "HOLD_EVIDENCE_PROVENANCE_REJECTED"
        assert result["dispatch_allowed"] is False
        assert result["secret_material_accepted"] is False
        assert result["workflow_dispatched"] is False


def test_frozen_policy_tampering_fails_before_registration() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    tampered = deepcopy(snapshot)
    tampered["protected_dispatch_contract"]["execute_live_witness_default"] = True
    with pytest.raises(EvidenceProvenanceGateError, match="dispatch drift"):
        FrozenEvidenceProvenanceGate.from_snapshot(tampered)

    tampered = deepcopy(snapshot)
    tampered["successor"] = "rewritten"
    with pytest.raises(EvidenceProvenanceGateError, match="successor drift"):
        FrozenEvidenceProvenanceGate.from_snapshot(tampered)


def test_w17_surfaces_register_without_network_or_dispatch() -> None:
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
    register_evidence_provenance_gate(fake)
    assert set(fake.tools) == {
        "athena_w17_evidence_provenance_status",
        "build_athena_w17_provenance_witness_template",
        "inspect_athena_w17_evidence_provenance",
        "evaluate_athena_w17_protected_dispatch_gate",
    }
    assert set(fake.resources) == {"athena://w17-evidence-provenance-gate"}
    dispatch = json.loads(
        fake.tools["evaluate_athena_w17_protected_dispatch_gate"](*_encoded())
    )
    assert dispatch["dispatch_allowed"] is False
    assert dispatch["workflow_dispatched"] is False


def test_w17_receipt_is_content_addressed_and_nonpromotional() -> None:
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
    assert receipt_id == f"w17-provenance-gate:sha256:{digest}"
    assert receipt["validation"]["expanded_p08_regression_result"] == (
        "PASS_97_OF_97"
    )
    assert receipt["protected_dispatch"]["dispatch_allowed"] is False
    assert receipt["boundaries"]["trust_anchor_verified"] is False
    assert receipt["boundaries"]["workflow_dispatched"] is False
    assert receipt["boundaries"]["persistent_witness_executed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
