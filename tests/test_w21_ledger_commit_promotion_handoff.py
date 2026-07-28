"""Adversarial contracts for KC144.XNAV.W21."""

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

from crystal_108d.ledger_commit_promotion_handoff import (  # noqa: E402
    AUTHORIZATION_SCHEMA,
    COMMIT_RECEIPT_SCHEMA,
    PROMOTION_DECISION_SCHEMA,
    W20_CONTROL_RECEIPT_ID,
    FrozenLedgerCommitPromotionHandoff,
    _authorization_digest,
    _commit_receipt_digest,
    _digest,
    _promotion_decision_digest,
    _unsigned_material,
    register_ledger_commit_promotion_handoff,
)


W20_TEST_PATH = ROOT / "tests" / "test_w20_persistent_return_ic10.py"
W20_SPEC = importlib.util.spec_from_file_location(
    "w20_fixture_module", W20_TEST_PATH
)
assert W20_SPEC is not None and W20_SPEC.loader is not None
w20 = importlib.util.module_from_spec(W20_SPEC)
W20_SPEC.loader.exec_module(w20)

DATA = ROOT / "MCP" / "data" / "w21_ledger_commit_promotion_handoff.json"
CONTROL_RECEIPT = (
    ROOT / "tests" / "fixtures" / "w20_control_protocol_admission.json"
)
COMMIT_SEED = bytes.fromhex(
    "034fc4452707b1b6db6f5992cc06256c"
    "6d3f1c9a39e9004316b4681937c609dd"
)
PROMOTION_SEED = bytes.fromhex(
    "4a90b9a4bc852684ef34d0ec1f711d89"
    "091360714047e56ced74d74d27a59c53"
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


def _authority(
    authority_id: str,
    key_id: str,
    seed: bytes,
    environment: str,
) -> dict:
    public = _public_key_base64(seed)
    return {
        "authority_id": authority_id,
        "key_id": key_id,
        "public_key_base64": public,
        "fingerprint": _fingerprint(public),
        "repository": "demeet2k/Athena",
        "environment": environment,
        "valid_from": "2026-07-27T00:00:00Z",
        "valid_until": "2027-07-27T00:00:00Z",
    }


def _snapshot_with_authorities() -> dict:
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    snapshot["commit_authority_registry"]["authorities"] = [
        _authority(
            "synthetic-ledger-commit-authority",
            "synthetic-ledger-key",
            COMMIT_SEED,
            "kc144-ledger-commit",
        )
    ]
    snapshot["promotion_authority_registry"]["authorities"] = [
        _authority(
            "synthetic-promotion-authority",
            "synthetic-promotion-key",
            PROMOTION_SEED,
            "kc144-promotion",
        )
    ]
    snapshot["boundaries"]["production_control_authority_pinned"] = True
    snapshot["boundaries"]["production_ic10_reviewer_pinned"] = True
    snapshot["boundaries"]["production_commit_authority_pinned"] = True
    snapshot["boundaries"]["production_promotion_authority_pinned"] = True
    snapshot["contract_digest"] = _digest(
        {
            key: value
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
    )
    return snapshot


def _gate() -> FrozenLedgerCommitPromotionHandoff:
    return FrozenLedgerCommitPromotionHandoff.from_snapshot(
        _snapshot_with_authorities(),
        w20_gate=w20._gate(),
    )


def _control_receipt() -> dict:
    return json.loads(CONTROL_RECEIPT.read_text(encoding="utf-8"))


def _w20_inputs(gate: FrozenLedgerCommitPromotionHandoff) -> tuple[str, ...]:
    w20_gate = gate.w20_gate
    packet, decision = w20._review(w20_gate)
    return (
        *w20._w19_arguments(w20_gate),
        json.dumps(w20._witness()),
        json.dumps(w20._control_admission(w20_gate)),
        json.dumps(packet),
        json.dumps(decision),
        json.dumps(_control_receipt()),
    )


def _transaction(gate: FrozenLedgerCommitPromotionHandoff) -> dict:
    result = gate.compile_ledger_commit_transaction(*_w20_inputs(gate))
    assert result["status"].startswith(
        "LEDGER_COMMIT_TRANSACTION_AND_AUTHORIZATION_TEMPLATE_READY"
    )
    return result


def _authorization(gate: FrozenLedgerCommitPromotionHandoff) -> tuple[dict, dict]:
    compiled = _transaction(gate)
    transaction = compiled["transaction"]
    authorization = compiled["authorization_template"]
    authorization["authorization"] = {
        "authority_id": "synthetic-ledger-commit-authority",
        "ledger_repository": "demeet2k/Athena",
        "ledger_ref": "athena-control://w21/synthetic-ledger-commit",
        "authorized_at": "2026-07-27T16:00:00Z",
    }
    authorization["signature"]["key_id"] = "synthetic-ledger-key"
    authorization["signature"]["value"] = base64.b64encode(
        _private(COMMIT_SEED).sign(
            json.dumps(
                _unsigned_material(authorization, "authorization_digest"),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    ).decode("ascii")
    authorization["authorization_digest"] = _authorization_digest(
        authorization
    )
    return transaction, authorization


def _commit_return(
    gate: FrozenLedgerCommitPromotionHandoff,
) -> tuple[dict, dict, dict]:
    transaction, authorization = _authorization(gate)
    result = gate.build_commit_occurrence_template(
        json.dumps(transaction), json.dumps(authorization)
    )
    receipt = result["template"]
    receipt["ledger_commit"] = "9" * 40
    receipt["committed_at"] = "2026-07-27T16:01:00Z"
    receipt["signature"]["value"] = base64.b64encode(
        _private(COMMIT_SEED).sign(
            json.dumps(
                _unsigned_material(receipt, "receipt_digest"),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    ).decode("ascii")
    receipt["receipt_digest"] = _commit_receipt_digest(receipt)
    return transaction, authorization, receipt


def _promotion_return(
    gate: FrozenLedgerCommitPromotionHandoff,
) -> tuple[dict, dict, dict, dict, dict]:
    transaction, authorization, receipt = _commit_return(gate)
    compiled = gate.build_promotion_handoff(
        json.dumps(transaction),
        json.dumps(authorization),
        json.dumps(receipt),
        "kc144-production",
        "athena-control://w21/synthetic-promotion",
    )
    packet = compiled["promotion_packet"]
    decision = compiled["decision_template"]
    decision["authority_id"] = "synthetic-promotion-authority"
    decision["decision"] = "AUTHORIZE_PROMOTION"
    decision["decided_at"] = "2026-07-27T16:02:00Z"
    decision["reason_code"] = "EXACT_COMMIT_AND_IC10_CHAIN_ACCEPTED"
    decision["signature"]["key_id"] = "synthetic-promotion-key"
    decision["signature"]["value"] = base64.b64encode(
        _private(PROMOTION_SEED).sign(
            json.dumps(
                _unsigned_material(decision, "decision_digest"),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    ).decode("ascii")
    decision["decision_digest"] = _promotion_decision_digest(decision)
    return transaction, authorization, receipt, packet, decision


def test_production_w21_is_empty_and_fail_closed() -> None:
    status = FrozenLedgerCommitPromotionHandoff.load().status()
    assert status["w20_control_protocol_admission_observed"] is True
    assert status["w20_control_receipt_grants_production_authority"] is False
    assert status["production_commit_authority_count"] == 0
    assert status["production_promotion_authority_count"] == 0
    assert status["committed_ledger_entry_count"] == 0
    assert status["runtime_can_mutate_ledger"] is False
    assert status["runtime_can_promote"] is False


def test_exact_w20_control_receipt_is_observation_only() -> None:
    result = FrozenLedgerCommitPromotionHandoff.load().inspect_control_protocol_admission(
        json.dumps(_control_receipt())
    )
    assert result["status"].startswith(
        "PASS_W20_CONTROL_PROTOCOL_RECEIPT_OBSERVED"
    )
    assert result["control_receipt_id"] == W20_CONTROL_RECEIPT_ID
    assert result["production_authority_granted"] is False
    assert result["control_plane_witness_admitted"] is False


def test_control_receipt_tamper_is_rejected() -> None:
    receipt = _control_receipt()
    receipt["runtime"]["exact_tree"] = "0" * 40
    result = FrozenLedgerCommitPromotionHandoff.load().inspect_control_protocol_admission(
        json.dumps(receipt)
    )
    assert result["status"] == "HOLD_W21_CONTROL_PROTOCOL_RECEIPT_REJECTED"
    assert "content address" in result["error"]


def test_full_w20_closure_compiles_exact_append_only_transaction() -> None:
    result = _transaction(_gate())
    transaction = result["transaction"]
    assert transaction["ledger_position"]["sequence"] == 1
    assert transaction["ledger_position"]["previous_entry_digest"] is None
    assert transaction["commit_constraints"]["runtime_can_mutate_ledger"] is False
    assert result["ledger_commit_authorized"] is False
    assert result["ledger_entry_committed"] is False


def test_production_cannot_compile_transaction_without_w20_authorities() -> None:
    synthetic = _gate()
    result = FrozenLedgerCommitPromotionHandoff.load().compile_ledger_commit_transaction(
        *_w20_inputs(synthetic)
    )
    assert result["status"] == "HOLD_W21_W20_EVIDENCE_CLOSURE_OPEN"
    assert result["ledger_entry_committed"] is False


def test_unpinned_commit_authority_is_rejected() -> None:
    synthetic = _gate()
    transaction, authorization = _authorization(synthetic)
    result = FrozenLedgerCommitPromotionHandoff.load().inspect_commit_authorization(
        json.dumps(transaction), json.dumps(authorization)
    )
    assert result["status"] == "HOLD_W21_COMMIT_AUTHORITY_NOT_PINNED"


def test_signed_commit_authorization_is_not_a_commit() -> None:
    gate = _gate()
    transaction, authorization = _authorization(gate)
    result = gate.inspect_commit_authorization(
        json.dumps(transaction), json.dumps(authorization)
    )
    assert authorization["schema"] == AUTHORIZATION_SCHEMA
    assert result["ledger_commit_authorized"] is True
    assert result["ledger_entry_committed"] is False


def test_authorization_tamper_is_rejected() -> None:
    gate = _gate()
    transaction, authorization = _authorization(gate)
    authorization["ledger_constraints"]["ledger_root_after"] = "sha256:" + "0" * 64
    result = gate.inspect_commit_authorization(
        json.dumps(transaction), json.dumps(authorization)
    )
    assert result["status"] == (
        "HOLD_W21_LEDGER_COMMIT_AUTHORIZATION_REJECTED"
    )


def test_commit_occurrence_template_requires_authorization() -> None:
    gate = _gate()
    transaction, authorization = _authorization(gate)
    authorization["authorization"]["authority_id"] = "caller-supplied"
    result = gate.build_commit_occurrence_template(
        json.dumps(transaction), json.dumps(authorization)
    )
    assert result["status"] == "HOLD_W21_COMMIT_AUTHORITY_NOT_PINNED"


def test_signed_commit_occurrence_closes_ledger_fact_without_mutation() -> None:
    gate = _gate()
    transaction, authorization, receipt = _commit_return(gate)
    result = gate.inspect_commit_occurrence(
        json.dumps(transaction),
        json.dumps(authorization),
        json.dumps(receipt),
    )
    assert receipt["schema"] == COMMIT_RECEIPT_SCHEMA
    assert result["ledger_commit_authorized"] is True
    assert result["ledger_entry_committed"] is True
    assert result["runtime_mutated_ledger"] is False


def test_commit_occurrence_root_tamper_is_rejected() -> None:
    gate = _gate()
    transaction, authorization, receipt = _commit_return(gate)
    receipt["committed_ledger_root"] = "sha256:" + "1" * 64
    result = gate.inspect_commit_occurrence(
        json.dumps(transaction),
        json.dumps(authorization),
        json.dumps(receipt),
    )
    assert result["status"] == (
        "HOLD_W21_LEDGER_COMMIT_OCCURRENCE_REJECTED"
    )


def test_promotion_handoff_requires_commit_occurrence() -> None:
    gate = _gate()
    transaction, authorization, receipt = _commit_return(gate)
    receipt["ledger_commit"] = "8" * 40
    result = gate.build_promotion_handoff(
        json.dumps(transaction),
        json.dumps(authorization),
        json.dumps(receipt),
        "kc144-production",
        "athena-control://w21/synthetic-promotion",
    )
    assert result["status"] == (
        "HOLD_W21_LEDGER_COMMIT_OCCURRENCE_REJECTED"
    )


def test_unpinned_promotion_authority_is_rejected() -> None:
    gate = _gate()
    _, _, _, packet, decision = _promotion_return(gate)
    result = FrozenLedgerCommitPromotionHandoff.load().inspect_promotion_decision(
        json.dumps(packet), json.dumps(decision)
    )
    assert result["status"] == "HOLD_W21_PROMOTION_AUTHORITY_NOT_PINNED"


def test_separate_promotion_decision_authorizes_but_does_not_execute() -> None:
    gate = _gate()
    _, _, _, packet, decision = _promotion_return(gate)
    result = gate.inspect_promotion_decision(
        json.dumps(packet), json.dumps(decision)
    )
    assert decision["schema"] == PROMOTION_DECISION_SCHEMA
    assert result["promotion_authorized"] is True
    assert result["promotion_executed"] is False
    assert result["promotion_claimed"] is False


def test_promotion_decision_tamper_is_rejected() -> None:
    gate = _gate()
    _, _, _, packet, decision = _promotion_return(gate)
    decision["reason_code"] = "DIFFERENT_REASON"
    result = gate.inspect_promotion_decision(
        json.dumps(packet), json.dumps(decision)
    )
    assert result["status"] == "HOLD_W21_PROMOTION_DECISION_REJECTED"


def test_full_synthetic_closure_stops_before_promotion_execution() -> None:
    gate = _gate()
    transaction, authorization, receipt, packet, decision = _promotion_return(
        gate
    )
    result = gate.evaluate_closure(
        json.dumps(transaction),
        json.dumps(authorization),
        json.dumps(receipt),
        json.dumps(packet),
        json.dumps(decision),
    )
    assert result["status"] == (
        "PASS_W21_LEDGER_COMMIT_AND_PROMOTION_DECISION_CLOSED__"
        "PROMOTION_EXECUTION_RECEIPT_OPEN"
    )
    assert result["ledger_entry_committed"] is True
    assert result["promotion_authorized"] is True
    assert result["promotion_executed"] is False
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


def test_w21_registration_and_resource() -> None:
    fake = FakeMCP()
    register_ledger_commit_promotion_handoff(fake)
    assert set(fake.tools) == {
        "athena_w21_ledger_commit_promotion_status",
        "inspect_athena_w21_control_protocol_admission",
        "compile_athena_w21_ledger_commit_transaction",
        "inspect_athena_w21_ledger_commit_authorization",
        "build_athena_w21_commit_occurrence_template",
        "inspect_athena_w21_commit_occurrence",
        "build_athena_w21_promotion_handoff",
        "inspect_athena_w21_promotion_authority_decision",
        "evaluate_athena_w21_commit_promotion_closure",
    }
    assert set(fake.resources) == {
        "athena://w21-ledger-commit-promotion-handoff"
    }
    status = json.loads(
        fake.tools["athena_w21_ledger_commit_promotion_status"]()
    )
    assert status["production_commit_authority_count"] == 0
    assert status["production_promotion_authority_count"] == 0


def test_w21_receipt_and_workflow_are_nonclaiming() -> None:
    receipt = json.loads(
        (
            ROOT
            / ".athena"
            / "receipts"
            / "w21-ledger-commit-promotion-handoff.json"
        ).read_text(encoding="utf-8")
    )
    receipt_id = receipt.pop("receipt_id")
    assert receipt_id == (
        "w21-commit-handoff:sha256:"
        + _digest(receipt).removeprefix("sha256:")
    )
    assert receipt["boundaries"]["ledger_entry_committed"] is False
    assert receipt["boundaries"]["promotion_authorized"] is False
    assert receipt["boundaries"]["promotion_claimed"] is False
    workflow = (
        ROOT / ".github" / "workflows" / "w21-commit-promotion-handoff.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "push:" not in workflow
    assert "schedule:" not in workflow
    assert "secrets." not in workflow
    assert "environment:" not in workflow
