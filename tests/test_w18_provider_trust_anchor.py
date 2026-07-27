"""Fail-closed tests for KC144.XNAV.W18."""

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
from crystal_108d.provider_trust_anchor import (  # noqa: E402
    FrozenProviderTrustRegistry,
    ProviderTrustAnchorError,
    _canonical_bytes,
    _signature_material,
    _verify_ed25519_signature,
    register_provider_trust_anchor,
)
from crystal_108d.replay_authority_ledger import _digest  # noqa: E402


DATA = ROOT / "MCP" / "data" / "w18_provider_trust_registry.json"
RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w18-provider-adapter-trust-anchor.json"
)
SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc4"
    "4449c5697b326919703bac031cae7f60"
)


def _registry() -> FrozenProviderTrustRegistry:
    return FrozenProviderTrustRegistry.load(DATA)


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
            "method": "provider-signature",
            "witness_ref": "https://witness.invalid-domain.example.net/runs/1",
            "verified_at": "2026-07-27T15:07:00Z",
        },
        "authorization": deepcopy(packet["authorization"]),
        "trust_anchor": {
            "kind": "ed25519-public-key",
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


def _unadmitted_signed_return() -> dict:
    packet_json, evidence_json, provenance_json = _encoded()
    template = _registry().build_provider_return_template(
        packet_json, evidence_json, provenance_json
    )["template"]
    template["adapter_id"] = "caller-controlled-adapter"
    template["observed_at"] = "2026-07-27T15:08:00Z"
    template["signature"]["key_id"] = "caller-controlled-key"
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    template["signature"]["value"] = base64.b64encode(
        private_key.sign(_canonical_bytes(_signature_material(template)))
    ).decode("ascii")
    return template


def test_frozen_w18_registry_is_crypto_ready_but_has_no_production_anchor() -> None:
    status = _registry().status()
    assert status["status"] == (
        "PROVIDER_TRUST_VERIFIER_READY__"
        "PRODUCTION_ADAPTER_AND_WITNESS_RETURN_OPEN"
    )
    assert status["production_adapter_count"] == 0
    assert status["registered_adapters"] == []
    assert status["self_supplied_trust_anchors_allowed"] is False
    assert status["boundaries"]["production_trust_anchor_pinned"] is False
    assert status["boundaries"]["persistent_witness_executed"] is False


def test_w17_bound_template_cannot_choose_or_supply_its_own_trust_anchor() -> None:
    result = _registry().build_provider_return_template(*_encoded())
    assert result["status"] == "HOLD_PROVIDER_ADAPTER_NOT_ADMITTED"
    assert result["adapter_match_count"] == 0
    assert result["template"]["adapter_id"] is None
    assert result["template"]["signature"]["key_id"] is None
    assert result["self_supplied_trust_anchor_field_present"] is False
    assert result["dispatch_allowed"] is False


def test_valid_signature_from_unadmitted_key_remains_untrusted() -> None:
    result = _registry().inspect_provider_return(
        *_encoded(), json.dumps(_unadmitted_signed_return())
    )
    assert result["status"] == "HOLD_PROVIDER_ADAPTER_NOT_ADMITTED"
    assert result["provider_return_signature_verified"] is False
    assert result["authorization_externally_verified"] is False
    assert result["evidence_class"] == (
        "STRUCTURALLY_BOUND_EXTERNAL_PROVENANCE_CLAIM"
    )
    assert result["workflow_dispatched"] is False


def test_ed25519_primitive_verifies_exact_canonical_material_only() -> None:
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    public_key = private_key.public_key().public_bytes_raw()
    material = {
        "schema": "athena.provider-signed-return/v1",
        "provider_evidence_digest": "sha256:" + "1" * 64,
    }
    signature = private_key.sign(_canonical_bytes(material))
    public_key_base64 = base64.b64encode(public_key).decode("ascii")
    signature_base64 = base64.b64encode(signature).decode("ascii")
    assert _verify_ed25519_signature(
        public_key_base64, signature_base64, material
    )
    tampered = {**material, "provider_evidence_digest": "sha256:" + "2" * 64}
    assert not _verify_ed25519_signature(
        public_key_base64, signature_base64, tampered
    )


def test_persistent_witness_return_keeps_all_external_gates_open() -> None:
    result = _registry().evaluate_persistent_witness_return(
        *_encoded(), json.dumps(_unadmitted_signed_return())
    )
    assert result["status"] == (
        "HOLD_PERSISTENT_WITNESS_RETURN__"
        "PROVIDER_ADMISSION_AND_PROTECTED_EXECUTION_OPEN"
    )
    assert result["gates"]["w17_provenance_structurally_valid"] is True
    assert result["gates"]["provider_adapter_commit_pinned"] is False
    assert result["gates"]["provider_return_signature_verified"] is False
    assert result["gates"]["protected_environment_approved"] is False
    assert result["workflow_dispatched"] is False
    assert result["persistent_witness_executed"] is False
    assert result["promotion_claimed"] is False


def test_registry_tampering_fails_before_registration() -> None:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    tampered = deepcopy(snapshot)
    tampered["trust_registry"]["adapters"] = [{"public_key": "caller supplied"}]
    with pytest.raises(ProviderTrustAnchorError, match="must remain empty"):
        FrozenProviderTrustRegistry.from_snapshot(tampered)

    tampered = deepcopy(snapshot)
    tampered["admission_contract"]["self_supplied_trust_anchors_allowed"] = True
    with pytest.raises(ProviderTrustAnchorError, match="contract drift"):
        FrozenProviderTrustRegistry.from_snapshot(tampered)


def test_w18_surfaces_register_without_network_dispatch_or_registry_mutation() -> None:
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
    register_provider_trust_anchor(fake)
    assert set(fake.tools) == {
        "athena_w18_provider_trust_status",
        "build_athena_w18_provider_return_template",
        "inspect_athena_w18_provider_signed_return",
        "evaluate_athena_w18_persistent_witness_return",
    }
    assert set(fake.resources) == {"athena://w18-provider-trust-anchor"}
    status = json.loads(fake.tools["athena_w18_provider_trust_status"]())
    assert status["production_adapter_count"] == 0
    assert status["runtime_can_mutate_registry"] is False


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
    assert receipt_id == f"w18-provider-trust:sha256:{digest}"
    assert receipt["registry"]["production_adapter_count"] == 0
    assert receipt["registry"]["self_supplied_trust_anchors_allowed"] is False
    assert receipt["boundaries"]["provider_return_signature_verified"] is False
    assert receipt["boundaries"]["workflow_dispatched"] is False
    assert receipt["boundaries"]["persistent_witness_executed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
