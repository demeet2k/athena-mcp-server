"""Fail-closed tests for KC144.XNAV.W19."""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.evidence_provenance_gate import (  # noqa: E402
    provenance_attestation_digest,
)
from crystal_108d.provider_admission_execution import (  # noqa: E402
    DECISION_SCHEMA,
    FrozenProviderAdmissionExecutionGate,
    ProviderAdmissionExecutionError,
    _decision_material,
    register_provider_admission_execution,
)
from crystal_108d.provider_trust_anchor import _canonical_bytes  # noqa: E402
from crystal_108d.replay_authority_ledger import _digest  # noqa: E402


DATA = ROOT / "MCP" / "data" / "w19_provider_admission_execution.json"
RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w19-provider-admission-execution-gate.json"
)
SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc4"
    "4449c5697b326919703bac031cae7f60"
)


def _gate() -> FrozenProviderAdmissionExecutionGate:
    return FrozenProviderAdmissionExecutionGate.load(DATA)


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": "b4e24de38788ecdf30f43514ece279d1270b998b",
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


def _key_material() -> tuple[Ed25519PrivateKey, str, str]:
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    public_key = private_key.public_key().public_bytes_raw()
    public_key_base64 = base64.b64encode(public_key).decode("ascii")
    fingerprint = "sha256:" + hashlib.sha256(public_key).hexdigest()
    return private_key, public_key_base64, fingerprint


def _provenance() -> dict:
    packet = _packet()
    evidence = _evidence()
    _, _, fingerprint = _key_material()
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
            "method": "provider-signature",
            "witness_ref": "https://witness.invalid-domain.example.net/runs/1",
            "verified_at": "2026-07-27T15:07:00Z",
        },
        "authorization": deepcopy(packet["authorization"]),
        "trust_anchor": {
            "kind": "ed25519-public-key",
            "reference": "https://trust.invalid-domain.example.net/anchors/1",
            "fingerprint": fingerprint,
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


def _request() -> dict:
    _, public_key_base64, _ = _key_material()
    result = _gate().build_admission_request(
        *_encoded(),
        "synthetic-provider.adapter",
        "1.0.0",
        "synthetic-provider-key-1",
        public_key_base64,
        "2026-07-27T15:08:00Z",
    )
    assert result["status"].startswith("PASS_STRUCTURAL_ADMISSION_REQUEST")
    return result["request"]


def _self_signed_decision() -> dict:
    private_key, _, _ = _key_material()
    decision = {
        "schema": DECISION_SCHEMA,
        "request_digest": _request()["request_digest"],
        "decision": "ADMIT",
        "authority_id": "caller-controlled-authority",
        "authority_key_id": "caller-controlled-key",
        "authority_commit": "f" * 40,
        "decided_at": "2026-07-27T15:09:00Z",
        "signature": {"algorithm": "ed25519", "value": ""},
    }
    decision["signature"]["value"] = base64.b64encode(
        private_key.sign(_canonical_bytes(_decision_material(decision)))
    ).decode("ascii")
    return decision


def test_w19_registry_is_verifier_ready_but_production_empty() -> None:
    status = _gate().status()
    assert status["status"] == (
        "PROVIDER_ADMISSION_VERIFIER_READY__"
        "AUTHORITY_ADAPTER_AND_EXECUTION_OPEN"
    )
    assert status["w18_ordered_parents"] == [
        "49f2449e159fdef82b60722f35f302290934a468",
        "5eece82829abb7eba87943548e89b6c04179ef40",
    ]
    assert status["production_admission_authority_count"] == 0
    assert status["production_provider_adapter_count"] == 0
    assert status["self_supplied_admission_authorities_allowed"] is False
    assert status["boundaries"]["workflow_dispatched"] is False


def test_admission_request_is_content_addressed_but_not_authority() -> None:
    request = _request()
    assert request["w18_parent_head"] == (
        "46f394bf4b99cbc1254da1d3250f418d42012be2"
    )
    assert request["provider_id"] == "synthetic-provider"
    assert request["requested_capabilities"]["dispatch_protected_workflow"] is False
    assert request["requested_capabilities"]["access_bearer_secret"] is False
    result = _gate().build_admission_request(
        *_encoded(),
        "synthetic-provider.adapter",
        "1.0.0",
        "synthetic-provider-key-1",
        _key_material()[1],
        "2026-07-27T15:08:00Z",
    )
    assert result["provider_public_key_mathematically_well_formed"] is True
    assert result["provider_public_key_trusted"] is False
    assert result["provider_adapter_admitted"] is False
    assert result["dispatch_allowed"] is False


def test_valid_self_signed_authority_decision_remains_untrusted() -> None:
    result = _gate().inspect_admission_decision(
        json.dumps(_request()), json.dumps(_self_signed_decision())
    )
    assert result["status"] == "HOLD_ADMISSION_AUTHORITY_NOT_PINNED"
    assert result["production_admission_authority_count"] == 0
    assert result["admission_authority_signature_verified"] is False
    assert result["provider_adapter_admitted"] is False
    assert result["provider_trust_anchor_pinned"] is False
    assert result["authorization_externally_verified"] is False
    assert result["workflow_dispatched"] is False


def test_request_tampering_is_rejected_before_authority_lookup() -> None:
    tampered = _request()
    tampered["provider_id"] = "other-provider"
    result = _gate().inspect_admission_decision(
        json.dumps(tampered), json.dumps(_self_signed_decision())
    )
    assert result["status"] == "HOLD_PROVIDER_ADMISSION_REJECTED"
    assert "digest mismatch" in result["error"]
    assert result["provider_adapter_admitted"] is False


def test_execution_gate_keeps_every_external_side_effect_open() -> None:
    result = _gate().evaluate_execution_gate(
        json.dumps(_request()), json.dumps(_self_signed_decision())
    )
    assert result["status"] == (
        "HOLD_PERSISTENT_WITNESS_EXECUTION__"
        "ADMISSION_AUTHORITY_AND_PROTECTED_EXECUTION_OPEN"
    )
    assert result["gates"]["admission_request_content_addressed"] is True
    assert result["gates"]["admission_authority_commit_pinned"] is False
    assert result["gates"]["provider_adapter_admitted"] is False
    assert result["gates"]["explicit_live_witness_dispatch"] is False
    assert result["workflow_dispatched"] is False
    assert result["endpoint_contacted"] is False
    assert result["persistent_witness_executed"] is False
    assert result["promotion_claimed"] is False


def test_registry_cannot_be_mutated_by_submitted_authority_or_adapter() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    tampered = deepcopy(snapshot)
    tampered["admission_registry"]["admission_authorities"] = [
        {"authority_id": "caller"}
    ]
    with pytest.raises(
        ProviderAdmissionExecutionError, match="must remain empty"
    ):
        FrozenProviderAdmissionExecutionGate.from_snapshot(tampered)
    tampered = deepcopy(snapshot)
    tampered["admission_policy"][
        "self_supplied_admission_authorities_allowed"
    ] = True
    with pytest.raises(ProviderAdmissionExecutionError, match="policy drift"):
        FrozenProviderAdmissionExecutionGate.from_snapshot(tampered)


def test_w19_surfaces_and_receipt_are_nonpromotional() -> None:
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
    register_provider_admission_execution(fake)
    assert set(fake.tools) == {
        "athena_w19_provider_admission_status",
        "build_athena_w19_provider_admission_request",
        "inspect_athena_w19_provider_admission_decision",
        "evaluate_athena_w19_persistent_witness_execution",
    }
    assert set(fake.resources) == {
        "athena://w19-provider-admission-execution"
    }
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
    assert receipt_id == f"w19-admission-execution:sha256:{digest}"
    assert receipt["boundaries"]["workflow_dispatched"] is False
    assert receipt["boundaries"]["persistent_witness_executed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
