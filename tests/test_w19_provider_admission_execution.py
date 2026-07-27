"""Adversarial contracts for KC144.XNAV.W19."""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.evidence_provenance_gate import (  # noqa: E402
    provenance_attestation_digest,
)
from crystal_108d.provider_admission_execution import (  # noqa: E402
    ADMISSION_SCHEMA,
    EXECUTION_SCHEMA,
    FrozenProviderAdmissionExecutionGate,
    W18_HEAD,
    W18_TREE,
    _addressed_material,
    _canonical_bytes,
    _unsigned_material,
    register_provider_admission_execution,
)
from crystal_108d.provider_trust_anchor import (  # noqa: E402
    _signature_material,
)
from crystal_108d.replay_authority_ledger import _digest  # noqa: E402


DATA = ROOT / "MCP" / "data" / "w19_provider_admission_execution.json"
PROVIDER_SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc4"
    "4449c5697b326919703bac031cae7f60"
)
CONTROL_SEED = bytes.fromhex(
    "4ccd089b28ff96da9db6c346ec114e0f"
    "5b8a319f35aba624da8cf6ed4fb8a6fb"
)


def _private(seed: bytes) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(seed)


def _public_key_base64(seed: bytes) -> str:
    return base64.b64encode(
        _private(seed).public_key().public_bytes_raw()
    ).decode("ascii")


def _fingerprint(public_key_base64: str) -> str:
    return "sha256:" + hashlib.sha256(
        base64.b64decode(public_key_base64)
    ).hexdigest()


def _packet() -> dict:
    return {
        "schema": "athena.persistent-host-activation-packet/v1",
        "state": "AUTHORIZED_FOR_LIVE_WITNESS",
        "canonical_hardening_head": "b4e24de38788ecdf30f43514ece279d1270b998b",
        "source_commit": "52d0e2abf282aee5f8bf233521989bc2c8969989",
        "runtime_p09_head": "9731b24c5963b75821b381b4562aa51baa55196c",
        "image": (
            "ghcr.io/demeet2k/athena-mcp-server@"
            "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
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
        "image_digest": "sha256:" + "31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2",
        "source_commit": packet["source_commit"],
        "runtime_p09_head": packet["runtime_p09_head"],
        "endpoint": packet["target"]["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": packet["provider"][
            "deployment_observed_at"
        ],
        "secret_store_ref": packet["target"]["secret_store_ref"],
        "secret_material_recorded": False,
        "evidence_url": packet["provider"]["evidence_url"],
    }


def _provenance() -> dict:
    packet = _packet()
    evidence = _evidence()
    provider_public_key = _public_key_base64(PROVIDER_SEED)
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
            "witness_ref": (
                "https://witness.invalid-domain.example.net/runs/1"
            ),
            "verified_at": "2026-07-27T15:07:00Z",
        },
        "authorization": deepcopy(packet["authorization"]),
        "trust_anchor": {
            "kind": "ed25519-public-key",
            "reference": (
                "https://trust.invalid-domain.example.net/anchors/1"
            ),
            "fingerprint": _fingerprint(provider_public_key),
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


def _snapshot_with_control_authority() -> dict:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    control_public_key = _public_key_base64(CONTROL_SEED)
    snapshot["control_authority_registry"]["authorities"] = [
        {
            "authority_id": "synthetic-control-authority",
            "key_id": "synthetic-control-key",
            "public_key_base64": control_public_key,
            "fingerprint": _fingerprint(control_public_key),
            "repository": "demeet2k/Athena",
            "environment": "kc144-control-plane",
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-07-27T00:00:00Z",
        }
    ]
    snapshot["admission_contract"]["production_control_authority_count"] = 1
    snapshot["boundaries"]["control_authority_pinned"] = True
    snapshot["contract_digest"] = _digest(
        {
            key: value
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
    )
    return snapshot


def _synthetic_gate() -> FrozenProviderAdmissionExecutionGate:
    return FrozenProviderAdmissionExecutionGate.from_snapshot(
        _snapshot_with_control_authority()
    )


def _admission() -> dict:
    snapshot = _snapshot_with_control_authority()
    provider_public_key = _public_key_base64(PROVIDER_SEED)
    value = {
        "schema": ADMISSION_SCHEMA,
        "candidate_head": W18_HEAD,
        "candidate_tree": W18_TREE,
        "w18_contracts": {
            "adapter_return_contract_digest": snapshot["predecessor"][
                "adapter_return_contract_digest"
            ],
            "provider_trust_contract_digest": snapshot["predecessor"][
                "provider_trust_contract_digest"
            ],
            "convergence_receipt_id": snapshot["predecessor"][
                "convergence_receipt_id"
            ],
        },
        "adapter": {
            "adapter_id": "synthetic-adapter",
            "provider_id": "synthetic-provider",
            "account_scope": "synthetic-account",
            "environment": "p10-persistent-host",
            "evidence_origin": "https://evidence.invalid-domain.example.net",
            "verification_method": "ed25519-detached-canonical-json",
            "attests_authorization": True,
            "trust_anchor": {
                "kind": "ed25519-public-key",
                "key_id": "synthetic-provider-key",
                "public_key_base64": provider_public_key,
                "fingerprint": _fingerprint(provider_public_key),
            },
        },
        "authorization": {
            "authority_id": "synthetic-control-authority",
            "control_repository": "demeet2k/Athena",
            "control_pull_request": 15,
            "control_commit": "2eb869928722077e1d65119632d4e0ac8e9b1760",
            "control_ref": "athena-control://w19/synthetic-admission",
            "admitted_at": "2026-07-27T15:08:00Z",
            "expires_at": "2026-07-27T17:00:00Z",
        },
        "signature": {
            "algorithm": "ed25519",
            "key_id": "synthetic-control-key",
            "value": "",
        },
        "admission_digest": "",
    }
    value["signature"]["value"] = base64.b64encode(
        _private(CONTROL_SEED).sign(
            _canonical_bytes(_unsigned_material(value, "admission_digest"))
        )
    ).decode("ascii")
    value["admission_digest"] = _digest(
        _addressed_material(value, "admission_digest")
    )
    return value


def _provider_return(gate: FrozenProviderAdmissionExecutionGate) -> dict:
    template = gate.w18_registry.build_provider_return_template(
        *_encoded()
    )["template"]
    template["adapter_id"] = "synthetic-adapter"
    template["observed_at"] = "2026-07-27T15:08:30Z"
    template["signature"]["key_id"] = "synthetic-provider-key"
    template["signature"]["value"] = base64.b64encode(
        _private(PROVIDER_SEED).sign(
            _canonical_bytes(_signature_material(template))
        )
    ).decode("ascii")
    return template


def _execution(gate: FrozenProviderAdmissionExecutionGate) -> dict:
    admission_json = json.dumps(_admission())
    provider_return_json = json.dumps(_provider_return(gate))
    template = gate.compile_execution_template(
        *_encoded(),
        admission_json,
        provider_return_json,
    )["template"]
    template["authorization"] = {
        "authority_id": "synthetic-control-authority",
        "control_ref": "athena-control://w19/synthetic-execution",
        "authorized_at": "2026-07-27T15:09:00Z",
        "expires_at": "2026-07-27T16:00:00Z",
    }
    template["signature"]["key_id"] = "synthetic-control-key"
    template["signature"]["value"] = base64.b64encode(
        _private(CONTROL_SEED).sign(
            _canonical_bytes(_unsigned_material(template, "execution_digest"))
        )
    ).decode("ascii")
    template["execution_digest"] = _digest(
        _addressed_material(template, "execution_digest")
    )
    return template


def test_production_w19_registry_is_empty_and_fail_closed() -> None:
    status = FrozenProviderAdmissionExecutionGate.load().status()
    assert status["production_control_authority_count"] == 0
    assert status["registered_control_authorities"] == []
    assert status["self_supplied_control_keys_allowed"] is False
    assert status["boundaries"]["control_authority_pinned"] is False
    assert status["boundaries"]["workflow_dispatched"] is False


def test_template_binds_w18_without_supplying_control_authority_key() -> None:
    result = FrozenProviderAdmissionExecutionGate.load().build_admission_template(
        *_encoded()
    )
    assert result["status"] == "HOLD_CONTROL_AUTHORITY_NOT_PINNED"
    assert result["template"]["candidate_head"] == W18_HEAD
    assert result["template"]["candidate_tree"] == W18_TREE
    assert result["template"]["authorization"]["authority_id"] is None
    assert result["self_supplied_control_authority_field_present"] is False


def test_valid_signature_from_unpinned_control_key_remains_untrusted() -> None:
    result = FrozenProviderAdmissionExecutionGate.load().inspect_admission(
        json.dumps(_admission())
    )
    assert result["status"] == "HOLD_CONTROL_AUTHORITY_NOT_PINNED"
    assert result["control_signature_verified"] is False
    assert result["provider_adapter_control_admitted"] is False
    assert result["workflow_dispatched"] is False


def test_commit_pinned_control_key_admits_exact_provider_key() -> None:
    result = _synthetic_gate().inspect_admission(json.dumps(_admission()))
    assert result["status"] == "PASS_CONTROL_SIGNED_PROVIDER_ADAPTER_ADMISSION"
    assert result["control_signature_verified"] is True
    assert result["provider_adapter_control_admitted"] is True
    assert result["submitted_admission_persisted_by_runtime"] is False
    assert result["workflow_dispatched"] is False


def test_admission_tampering_invalidates_content_address() -> None:
    tampered = _admission()
    tampered["adapter"]["provider_id"] = "different-provider"
    result = _synthetic_gate().inspect_admission(json.dumps(tampered))
    assert result["status"] == "HOLD_W19_ADMISSION_OR_EXECUTION_REJECTED"
    assert "digest mismatch" in result["error"]


def test_control_admission_enables_exact_w18_provider_signature_check() -> None:
    gate = _synthetic_gate()
    result = gate.inspect_admitted_provider_return(
        *_encoded(),
        json.dumps(_admission()),
        json.dumps(_provider_return(gate)),
    )
    assert result["status"] == "PASS_CONTROL_ADMITTED_PROVIDER_RETURN_SIGNATURE"
    assert result["control_signature_verified"] is True
    assert result["provider_return_signature_verified"] is True
    assert result["authorization_externally_verified"] is True
    assert result["workflow_dispatched"] is False


def test_provider_return_tampering_is_rejected_after_admission() -> None:
    gate = _synthetic_gate()
    returned = _provider_return(gate)
    returned["authorization_ref"] = "different-authorization"
    result = gate.inspect_admitted_provider_return(
        *_encoded(),
        json.dumps(_admission()),
        json.dumps(returned),
    )
    assert result["status"] == "HOLD_PROVIDER_RETURN_REJECTED"
    assert result["provider_return_signature_verified"] is False


def test_separate_execution_signature_authorizes_but_does_not_dispatch() -> None:
    gate = _synthetic_gate()
    result = gate.evaluate_execution(
        *_encoded(),
        json.dumps(_admission()),
        json.dumps(_provider_return(gate)),
        json.dumps(_execution(gate)),
    )
    assert result["status"] == (
        "PASS_CONTROL_SIGNED_PROTECTED_EXECUTION_AUTHORIZATION__"
        "NOT_DISPATCHED"
    )
    assert result["execution_authorization_verified"] is True
    assert result["protected_execution_authorized"] is True
    assert result["dispatch_eligible_in_protected_workflow"] is True
    assert result["workflow_dispatched"] is False
    assert result["persistent_witness_executed"] is False
    assert result["promotion_claimed"] is False


def test_execution_tampering_cannot_cross_protected_gate() -> None:
    gate = _synthetic_gate()
    execution = _execution(gate)
    execution["workflow"]["sample_count"] = 2
    result = gate.evaluate_execution(
        *_encoded(),
        json.dumps(_admission()),
        json.dumps(_provider_return(gate)),
        json.dumps(execution),
    )
    assert result["status"] == "HOLD_W19_ADMISSION_OR_EXECUTION_REJECTED"
    assert result["execution_authorization_verified"] is False
    assert result["workflow_dispatched"] is False


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}
        self.resources: dict[str, object] = {}

    def tool(self):
        def decorator(function):
            self.tools[function.__name__] = function
            return function

        return decorator

    def resource(self, uri: str):
        def decorator(function):
            self.resources[uri] = function
            return function

        return decorator


def test_w19_registration_and_frozen_resource() -> None:
    fake = FakeMCP()
    register_provider_admission_execution(fake)
    assert set(fake.tools) == {
        "athena_w19_provider_admission_status",
        "build_athena_w19_provider_admission_template",
        "inspect_athena_w19_provider_admission",
        "inspect_athena_w19_admitted_provider_return",
        "compile_athena_w19_execution_authorization_template",
        "evaluate_athena_w19_protected_witness_execution",
    }
    assert set(fake.resources) == {
        "athena://w19-provider-admission-execution"
    }
    status = json.loads(fake.tools["athena_w19_provider_admission_status"]())
    assert status["production_control_authority_count"] == 0
    assert status["boundaries"]["promotion_claimed"] is False


def test_w19_workflow_is_manual_reverified_and_protected() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "w19-authorized-provider-witness.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "schedule:" not in workflow
    assert "environment: p10-persistent-host" in workflow
    assert workflow.count("scripts/w19_provider_admission.py") == 2
    assert "if: inputs.execute_live_witness == true" in workflow
    assert "secrets.ATHENA_MCP_BEARER_TOKEN" in workflow
