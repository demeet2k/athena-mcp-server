"""Adversarial contracts for KC144.XNAV.W20."""

from __future__ import annotations

import base64
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.persistent_return_ic10 import (  # noqa: E402
    CONTROL_ADMISSION_SCHEMA,
    IC10_DECISION_SCHEMA,
    FrozenPersistentReturnIC10Gate,
    _addressed_material,
    _canonical_bytes,
    _decision_digest,
    _digest,
    _receipt_body,
    _receipt_id,
    _unsigned_material,
    register_persistent_return_ic10,
)


W19_TEST_PATH = ROOT / "tests" / "test_w19_provider_admission_execution.py"
W19_SPEC = importlib.util.spec_from_file_location(
    "w19_fixture_module", W19_TEST_PATH
)
assert W19_SPEC is not None and W19_SPEC.loader is not None
w19 = importlib.util.module_from_spec(W19_SPEC)
W19_SPEC.loader.exec_module(w19)

DATA = ROOT / "MCP" / "data" / "w20_persistent_return_ic10.json"
IC10_SEED = bytes.fromhex(
    "c5aa8df43f9f837bedb7442f31dcb7b1"
    "66d38535076f094b85ce3a2e0b4458f7"
)


def _private(seed: bytes) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(seed)


def _public_key_base64(seed: bytes) -> str:
    return base64.b64encode(
        _private(seed).public_key().public_bytes_raw()
    ).decode("ascii")


def _fingerprint(public_key_base64: str) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(
        base64.b64decode(public_key_base64)
    ).hexdigest()


def _snapshot_with_reviewers() -> dict:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    reviewer_key = _public_key_base64(IC10_SEED)
    snapshot["ic10_registry"]["reviewers"] = [
        {
            "authority_id": "synthetic-ic10-reviewer",
            "key_id": "synthetic-ic10-key",
            "public_key_base64": reviewer_key,
            "fingerprint": _fingerprint(reviewer_key),
            "repository": "demeet2k/Athena",
            "environment": "kc144-ic10",
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-07-27T00:00:00Z",
        }
    ]
    snapshot["boundaries"]["production_control_authority_pinned"] = True
    snapshot["boundaries"]["production_ic10_reviewer_pinned"] = True
    snapshot["contract_digest"] = _digest(
        {
            key: value
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
    )
    return snapshot


def _gate() -> FrozenPersistentReturnIC10Gate:
    return FrozenPersistentReturnIC10Gate.from_snapshot(
        _snapshot_with_reviewers(),
        w19_gate=w19._synthetic_gate(),
    )


def _sample(observed_at: str) -> dict:
    checks = {
        "mcp_initialize": True,
        "real_network_contact": True,
        "host_commit_attested": True,
        "required_tools_present": True,
        "actual_tool_count_exact": True,
        "actual_tool_inventory_exact": True,
        "required_resources_present": True,
        "actual_resource_count_exact": True,
        "actual_resource_inventory_exact": True,
        "unauthenticated_rejected": True,
        "invalid_token_rejected": True,
        "redirects_absent": True,
        "https_not_downgraded": True,
        "frozen_graph_exact": True,
        "v2_identity_answered": True,
        "v2_route_answered": True,
        "reciprocal_return_answered": True,
        "explicit_v1_fallback_answered": True,
        "tool_resource_receipts_equal": True,
        "promotion_boundary": True,
    }
    return {
        "observed_at": observed_at,
        "checks": checks,
        "catalog": {
            "tools_count": 174,
            "resources_count": 27,
            "required_tools": [
                "athena_federation_status",
                "resolve_athena_identity",
                "route_athena_federation",
            ],
            "required_resources": [
                "athena://federation-v2",
                "athena://federation-v2/lock",
            ],
            "required_tools_present": True,
            "required_resources_present": True,
            "tool_inventory_digest": (
                "sha256:230b41262dd77cc7e73f1acb3afcbc8de67bb52e680f35abfebb3465620fc34c"
            ),
            "resource_inventory_digest": (
                "sha256:6e74961966019708425aa26ed6bddb0c665cfffacb1ef7e44494f8861deb9eea"
            ),
        },
        "answer_provenance": {
            "v2_route": {
                "hops": [
                    "edge.q-shrink-to-control",
                    "edge.control-to-runtime",
                ],
                "return_plan": [
                    "edge.runtime-to-control",
                    "edge.control-to-q-shrink",
                ],
            },
            "v1_fallback": {
                "answered_by": "athena-108d-v1",
                "fallback_used": True,
            },
        },
        "workflow_run": (
            "https://github.com/demeet2k/athena-mcp-server/"
            "actions/runs/999999999"
        ),
    }


def _witness() -> dict:
    packet = w19._packet()
    evidence = w19._evidence()
    body = {
        "schema": "athena.persistent-mcp-witness/v2",
        "phase": "P10",
        "seed": (
            "KC144.MYC.SKELETON.P10::"
            "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
        ),
        "verdict": "PASS_PERSISTENT_HTTPS_WITNESS",
        "observed_at": "2026-07-27T15:10:41Z",
        "target": {
            "target_id": packet["target"]["id"],
            "target_digest": "sha256:" + "a1" * 32,
            "endpoint": packet["target"]["endpoint"],
            "persistence_class": packet["target"]["persistence_class"],
            "authorization_ref": packet["authorization"]["ref"],
        },
        "provider_evidence": evidence,
        "deployment": {
            "image": packet["image"],
            "image_selection_attestation": "authorized-target-contract",
            "source_commit": packet["source_commit"],
            "source_commit_attestation": "host-health-build-locked-file",
            "transport": "streamable-http",
            "authentication": "bearer-present-value-not-recorded",
            "persistent_endpoint": True,
        },
        "authentication": {
            "class": "bearer",
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": evidence["secret_store_ref"],
        },
        "observation_window": {
            "sample_count": 3,
            "interval_seconds": 20,
            "minimum_elapsed_seconds": 40.0,
            "samples": [
                _sample("2026-07-27T15:10:00Z"),
                _sample("2026-07-27T15:10:20Z"),
                _sample("2026-07-27T15:10:40Z"),
            ],
        },
        "secret_recorded": False,
        "persistent_deployment_claimed": True,
        "promotion_ready": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "authority": {
            "persistent_endpoint_witnessed": True,
            "runtime_can_promote": False,
            "ic10_required": True,
        },
        "rollback": {
            "class": "immutable-digest-selection",
            "action": (
                "Stop routing to this endpoint and reselect the exact P09 "
                "digest or explicit athena-108d-v1 fallback without rewriting history."
            ),
        },
        "next_gate": (
            "Admit this exact repeated witness in the Athena control plane; "
            "IC10 remains required for any promotion decision."
        ),
        "successor_seed": (
            "KC144.MYC.SKELETON.P11::"
            "PERSISTENT-WITNESS-ADMISSION-AND-IC10-READINESS"
        ),
    }
    return {"receipt_id": _receipt_id(body), **body}


def _w19_arguments(gate: FrozenPersistentReturnIC10Gate) -> tuple[str, ...]:
    return (
        *w19._encoded(),
        json.dumps(w19._admission()),
        json.dumps(w19._provider_return(gate.w19_gate)),
        json.dumps(w19._execution(gate.w19_gate)),
    )


def _control_admission(gate: FrozenPersistentReturnIC10Gate) -> dict:
    template = gate.build_control_admission_template(
        *_w19_arguments(gate),
        json.dumps(_witness()),
    )["template"]
    template["persistence"] = {
        "persistence_class": "append-only-content-addressed-object",
        "object_url": (
            "https://objects.invalid-domain.example.net/"
            "athena/sha256/"
            + "b2" * 32
            + "/persistent-witness-1.json"
        ),
        "object_digest": "sha256:" + "b2" * 32,
        "object_size_bytes": 8192,
        "content_addressed": True,
        "immutable": True,
        "retained_until": "2027-07-27T00:00:00Z",
    }
    template["authorization"] = {
        "authority_id": "synthetic-control-authority",
        "control_repository": "demeet2k/Athena",
        "control_pull_request": 16,
        "control_commit": "3eb869928722077e1d65119632d4e0ac8e9b1761",
        "control_ref": "athena-control://w20/synthetic-persistence",
        "admitted_at": "2026-07-27T15:11:00Z",
    }
    template["signature"]["key_id"] = "synthetic-control-key"
    template["signature"]["value"] = base64.b64encode(
        _private(w19.CONTROL_SEED).sign(
            _canonical_bytes(
                _unsigned_material(template, "admission_digest")
            )
        )
    ).decode("ascii")
    template["admission_digest"] = _digest(
        _addressed_material(template, "admission_digest")
    )
    return template


def _review(gate: FrozenPersistentReturnIC10Gate) -> tuple[dict, dict]:
    compiled = gate.compile_ic10_review_template(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(_control_admission(gate)),
    )
    packet = compiled["review_packet"]
    decision = compiled["decision_template"]
    decision["reviewer_id"] = "synthetic-ic10-reviewer"
    decision["decision"] = "ADMIT_WITNESS_EVIDENCE"
    decision["reviewed_at"] = "2026-07-27T15:12:00Z"
    decision["reason_code"] = "EXACT_SIGNED_EVIDENCE_CHAIN_ACCEPTED"
    decision["signature"]["key_id"] = "synthetic-ic10-key"
    decision["signature"]["value"] = base64.b64encode(
        _private(IC10_SEED).sign(
            _canonical_bytes(
                _unsigned_material(decision, "decision_digest")
            )
        )
    ).decode("ascii")
    decision["decision_digest"] = _decision_digest(decision)
    return packet, decision


def test_production_w20_is_empty_and_fail_closed() -> None:
    status = FrozenPersistentReturnIC10Gate.load().status()
    assert status["production_control_authority_count"] == 0
    assert status["production_ic10_reviewer_count"] == 0
    assert status["ledger_entry_count"] == 0
    assert status["runtime_can_mutate_ledger"] is False
    assert status["runtime_can_promote"] is False


def test_synthetic_w19_authorized_persistent_witness_validates() -> None:
    gate = _gate()
    result = gate.inspect_persistent_witness(
        *_w19_arguments(gate),
        json.dumps(_witness()),
    )
    assert result["status"].startswith(
        "PASS_W19_AUTHORIZED_PERSISTENT_WITNESS"
    )
    assert result["persistent_witness_validated"] is True
    assert result["control_plane_witness_admitted"] is False


def test_witness_content_address_tamper_is_rejected() -> None:
    gate = _gate()
    witness = _witness()
    witness["target"]["target_id"] = "different-target"
    result = gate.inspect_persistent_witness(
        *_w19_arguments(gate),
        json.dumps(witness),
    )
    assert result["status"] == "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED"


def test_short_observation_interval_is_rejected_even_if_readdressed() -> None:
    gate = _gate()
    witness = _witness()
    witness["observation_window"]["samples"][1][
        "observed_at"
    ] = "2026-07-27T15:10:10Z"
    witness["receipt_id"] = _receipt_id(_receipt_body(witness))
    result = gate.inspect_persistent_witness(
        *_w19_arguments(gate),
        json.dumps(witness),
    )
    assert result["status"] == "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED"
    assert "interval" in result["error"]


def test_control_admission_template_binds_every_w19_and_witness_digest() -> None:
    gate = _gate()
    result = gate.build_control_admission_template(
        *_w19_arguments(gate),
        json.dumps(_witness()),
    )
    assert result["status"] == "CONTROL_PERSISTENCE_ADMISSION_TEMPLATE_READY"
    assert result["template"]["schema"] == CONTROL_ADMISSION_SCHEMA
    assert result["template"]["persistence"]["object_url"] is None
    assert result["template"]["admission_digest"] is None


def test_unpinned_production_control_authority_cannot_admit_return() -> None:
    production = FrozenPersistentReturnIC10Gate.load()
    synthetic = _gate()
    result = production.inspect_control_admission(
        *_w19_arguments(synthetic),
        json.dumps(_witness()),
        json.dumps(_control_admission(synthetic)),
    )
    assert result["status"] == "HOLD_CONTROL_AUTHORITY_NOT_PINNED"
    assert result["control_plane_witness_admitted"] is False


def test_control_signed_persistence_admission_passes_synthetically() -> None:
    gate = _gate()
    result = gate.inspect_control_admission(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(_control_admission(gate)),
    )
    assert result["status"].startswith(
        "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_RETURN"
    )
    assert result["control_signature_verified"] is True
    assert result["external_persistence_attestation_verified"] is True
    assert result["external_persistence_fetched_by_runtime"] is False


def test_control_admission_rejects_non_content_addressed_object_url() -> None:
    gate = _gate()
    admission = _control_admission(gate)
    admission["persistence"]["object_url"] = (
        "https://objects.invalid-domain.example.net/athena/latest.json"
    )
    admission["signature"]["value"] = base64.b64encode(
        _private(w19.CONTROL_SEED).sign(
            _canonical_bytes(
                _unsigned_material(admission, "admission_digest")
            )
        )
    ).decode("ascii")
    admission["admission_digest"] = _digest(
        _addressed_material(admission, "admission_digest")
    )
    result = gate.inspect_control_admission(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(admission),
    )
    assert result["status"] == "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED"


def test_control_admission_tamper_is_rejected() -> None:
    gate = _gate()
    admission = _control_admission(gate)
    admission["persistence"]["object_size_bytes"] += 1
    result = gate.inspect_control_admission(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(admission),
    )
    assert result["status"] == "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED"
    assert "digest mismatch" in result["error"]


def test_ledger_candidate_is_hash_chained_but_not_committed() -> None:
    gate = _gate()
    result = gate.compile_ledger_entry(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(_control_admission(gate)),
    )
    assert result["status"] == (
        "LEDGER_ENTRY_CANDIDATE_COMPILED__NOT_COMMITTED"
    )
    assert result["ledger_entry"]["sequence"] == 1
    assert result["ledger_entry"]["previous_entry_digest"] is None
    assert result["ledger_entry_committed"] is False
    assert result["runtime_can_mutate_ledger"] is False


def test_ic10_template_is_evidence_only_and_nonpromotional() -> None:
    gate = _gate()
    result = gate.compile_ic10_review_template(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(_control_admission(gate)),
    )
    assert result["status"] == (
        "IC10_REVIEW_TEMPLATE_READY__REVIEW_NOT_RECORDED"
    )
    constraints = result["review_packet"]["review_constraints"]
    assert constraints["evidence_only"] is True
    assert constraints["promotion_authorized"] is False
    assert result["decision_template"]["promotion_authorized"] is False


def test_unpinned_production_ic10_reviewer_remains_untrusted() -> None:
    gate = _gate()
    packet, decision = _review(gate)
    result = FrozenPersistentReturnIC10Gate.load().inspect_ic10_review(
        json.dumps(packet),
        json.dumps(decision),
    )
    assert result["status"] == "HOLD_IC10_REVIEWER_NOT_PINNED"
    assert result["ic10_review_recorded"] is False


def test_separately_signed_ic10_review_is_recorded_not_promoted() -> None:
    gate = _gate()
    packet, decision = _review(gate)
    result = gate.inspect_ic10_review(
        json.dumps(packet),
        json.dumps(decision),
    )
    assert result["status"] == (
        "PASS_IC10_WITNESS_EVIDENCE_REVIEW_RECORDED__NOT_PROMOTED"
    )
    assert result["ic10_signature_verified"] is True
    assert result["ic10_review_recorded"] is True
    assert result["promotion_authorized"] is False
    assert result["promotion_claimed"] is False


def test_ic10_decision_tamper_is_rejected() -> None:
    gate = _gate()
    packet, decision = _review(gate)
    decision["reason_code"] = "DIFFERENT_REASON"
    result = gate.inspect_ic10_review(
        json.dumps(packet),
        json.dumps(decision),
    )
    assert result["status"] == "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED"


def test_full_synthetic_closure_stops_before_commit_and_promotion() -> None:
    gate = _gate()
    packet, decision = _review(gate)
    result = gate.evaluate_closure(
        *_w19_arguments(gate),
        json.dumps(_witness()),
        json.dumps(_control_admission(gate)),
        json.dumps(packet),
        json.dumps(decision),
    )
    assert result["status"] == (
        "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_AND_IC10_REVIEW__"
        "LEDGER_COMMIT_AND_PROMOTION_OPEN"
    )
    assert result["control_plane_witness_admitted"] is True
    assert result["ic10_review_recorded"] is True
    assert result["ledger_entry_committed"] is False
    assert result["promotion_authorized"] is False
    assert result["promotion_claimed"] is False


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


def test_w20_registration_and_resource() -> None:
    fake = FakeMCP()
    register_persistent_return_ic10(fake)
    assert set(fake.tools) == {
        "athena_w20_persistent_return_ic10_status",
        "inspect_athena_w20_persistent_witness",
        "build_athena_w20_control_admission_template",
        "inspect_athena_w20_control_admission",
        "compile_athena_w20_ledger_entry",
        "compile_athena_w20_ic10_review_template",
        "inspect_athena_w20_ic10_review",
        "evaluate_athena_w20_return_ic10_closure",
    }
    assert set(fake.resources) == {
        "athena://w20-persistent-return-ic10"
    }
    status = json.loads(
        fake.tools["athena_w20_persistent_return_ic10_status"]()
    )
    assert status["production_ic10_reviewer_count"] == 0
    assert status["ledger_entry_count"] == 0


def test_operational_surfaces_are_manual_secret_free_and_frozen() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "w20-admit-persistent-return.yml"
    ).read_text(encoding="utf-8")
    script = (
        ROOT / "scripts" / "w20_persistent_return_ic10.py"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "secrets." not in workflow
    assert "environment:" not in workflow
    assert "--check-snapshot" in workflow
    assert "ledger_entry_committed" in script
    assert "promotion_authorized" in script


def test_w20_receipt_is_content_addressed_and_nonclaiming() -> None:
    receipt = json.loads(
        (
            ROOT
            / ".athena"
            / "receipts"
            / "w20-persistent-return-ic10-gate.json"
        ).read_text(encoding="utf-8")
    )
    receipt_id = receipt.pop("receipt_id")
    assert receipt_id == (
        "w20-return-ic10:sha256:" + _digest(receipt).removeprefix("sha256:")
    )
    assert receipt["lineage"]["w19_head"] == (
        "7863692262529d7e1effbd73eb8abfc3126ac484"
    )
    assert receipt["contract"]["ledger_entry_count"] == 0
    assert receipt["boundaries"]["persistent_witness_validated"] is False
    assert receipt["boundaries"]["ledger_entry_committed"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
