import base64
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from MCP.crystal_108d.five_wave_review_closure import (
    AUTHORITY_PATH_TEMPLATE,
    AUTHORITY_REF_TEMPLATE,
    BATCH,
    CANONICAL_CONTROL_REF,
    CANONICAL_GOVERNANCE_REPOSITORY,
    CONTROL_PREDECESSOR_HEAD,
    CONTROL_PREDECESSOR_TREE,
    DATA_PATH,
    REVISION_SCHEMA,
    RUNTIME_PREDECESSOR_HEAD,
    RUNTIME_PREDECESSOR_TREE,
    SCHEMA,
    SOURCE_SCHEMA,
    W26_CONTRACT,
    W26_CONTROL_RECEIPT,
    W26_RUNTIME_RECEIPT,
    W27_W31_CONTRACT,
    FiveWaveReviewClosureError,
    FrozenFiveWaveReviewClosure,
    _record_schema,
)
from MCP.crystal_108d.independent_authority_return import (
    _addressed,
    _digest,
    _signed,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT / ".athena" / "receipts" / "w27-w31-five-wave-protocol.json"
)
VERIFICATION_TIME = datetime(2026, 7, 28, 0, 30, tzinfo=timezone.utc)
EXPECTED_RECEIPT = (
    "w27-w31-five-wave-protocol:sha256:"
    "4e6e5fd1ff809bbe71d35d5619aa2036c50c22e8568c0a97650c7e696c2782dc"
)


def _private(role: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("w27-w31:" + role).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def _public(role: str) -> str:
    raw = _private(role).public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode()


def _fingerprint(public_key_base64: str) -> str:
    return "sha256:" + hashlib.sha256(
        base64.b64decode(public_key_base64)
    ).hexdigest()


def _sign(record: dict, role: str) -> dict:
    record["signature"] = {
        "key_id": (
            f"key.w{record['wave']}."
            f"{role.lower().replace('_', '-')}.v1"
        ),
        "value": base64.b64encode(
            _private(role).sign(
                json.dumps(
                    _signed(record, "record_digest"),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            )
        ).decode(),
    }
    record["record_digest"] = _digest(
        _addressed(record, "record_digest")
    )
    return record


def _gate():
    return FrozenFiveWaveReviewClosure(
        json.loads(DATA_PATH.read_text()),
        verification_time=VERIFICATION_TIME,
    )


def _bundle(decision: str = "REJECTED_ROLLED_BACK"):
    gate = _gate()
    sources = []
    revisions = []
    records = []
    previous = W26_RUNTIME_RECEIPT
    start = datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc)
    for index, (wave, role, kind) in enumerate(gate.expected_coordinates):
        name = role.lower().replace("_", "-")
        source = {
            "schema": SOURCE_SCHEMA,
            "source_id": f"source.w{wave}.{name}",
            "authority_id": f"authority.w{wave}.{name}",
            "role": role,
            "wave": wave,
            "governance_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "source_digest": "",
        }
        source["source_digest"] = _digest(
            _addressed(source, "source_digest")
        )
        public = _public(role)
        revision = {
            "schema": REVISION_SCHEMA,
            "source_digest": source["source_digest"],
            "revision_id": f"revision.w{wave}.{name}.v1",
            "role": role,
            "wave": wave,
            "repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "ref": AUTHORITY_REF_TEMPLATE.format(wave=wave) + "test",
            "commit": hashlib.sha1(
                f"commit:w{wave}:{role}".encode()
            ).hexdigest(),
            "tree": hashlib.sha1(
                f"tree:w{wave}:{role}".encode()
            ).hexdigest(),
            "path": (
                AUTHORITY_PATH_TEMPLATE.format(wave=wave)
                + f"{name}.json"
            ),
            "blob_digest": "",
            "content_digest": "sha256:"
            + hashlib.sha256(
                f"content:w{wave}:{role}".encode()
            ).hexdigest(),
            "parent_revision_digest": None,
            "key_id": f"key.w{wave}.{name}.v1",
            "public_key_base64": public,
            "fingerprint": _fingerprint(public),
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-07-28T00:00:00Z",
            "scope": {
                "operation": kind,
                "phase": f"KC144.XNAV.W{wave}",
                "repository": CANONICAL_GOVERNANCE_REPOSITORY,
                "ref": CANONICAL_CONTROL_REF,
                "environment": "kc144-control",
                "batch_contract_digest": W27_W31_CONTRACT,
            },
            "revision_digest": "",
        }
        revision["blob_digest"] = _digest(
            {
                "schema": "athena.w27-w31-authority-blob-provenance/v1",
                "repository": revision["repository"],
                "ref": revision["ref"],
                "commit": revision["commit"],
                "tree": revision["tree"],
                "path": revision["path"],
                "content_digest": revision["content_digest"],
            }
        )
        revision["revision_digest"] = _digest(
            _addressed(revision, "revision_digest")
        )
        occurred_at = (
            start + timedelta(minutes=index + 1)
        ).isoformat().replace("+00:00", "Z")
        record = {
            "schema": _record_schema(wave, kind),
            "phase": f"KC144.XNAV.W{wave}",
            "wave": wave,
            "record_index": index,
            "record_kind": kind,
            "role": role,
            "source_digest": source["source_digest"],
            "revision_digest": revision["revision_digest"],
            "event_id": f"event.w{wave}.{name}",
            "previous_record_digest": previous,
            "subject_digest": previous,
            "decision": decision,
            "outcome": kind.upper(),
            "effect_claimed": False,
            "occurred_at": occurred_at,
            "nonce": f"nonce.w{wave}.{name}",
            "signature": {"key_id": "", "value": ""},
            "record_digest": "",
        }
        _sign(record, role)
        previous = record["record_digest"]
        sources.append(source)
        revisions.append(revision)
        records.append(record)
    return {"sources": sources, "revisions": revisions, "records": records}


def _evaluate(bundle):
    return _gate().verify_bundle(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    )


def test_frozen_snapshot_contract_and_exact_predecessors():
    gate = _gate()
    status = gate.status()
    assert gate.snapshot["schema"] == SCHEMA
    assert gate.snapshot["batch"] == BATCH
    assert gate.snapshot["contract_digest"] == W27_W31_CONTRACT
    assert status["runtime_predecessor_head"] == RUNTIME_PREDECESSOR_HEAD
    assert status["runtime_predecessor_tree"] == RUNTIME_PREDECESSOR_TREE
    assert status["control_predecessor_head"] == CONTROL_PREDECESSOR_HEAD
    assert status["control_predecessor_tree"] == CONTROL_PREDECESSOR_TREE
    predecessor = gate.snapshot["predecessor"]
    assert predecessor["w26_contract_digest"] == W26_CONTRACT
    assert predecessor["w26_runtime_receipt_id"] == W26_RUNTIME_RECEIPT
    assert predecessor["w26_control_receipt_id"] == W26_CONTROL_RECEIPT


def test_exact_five_wave_chain_and_next_octave_successor():
    gate = _gate()
    waves = gate.snapshot["waves"]
    assert [wave["wave"] for wave in waves] == [27, 28, 29, 30, 31]
    assert [wave["predecessor"] for wave in waves] == [
        "KC144.XNAV.W26",
        "KC144.XNAV.W27",
        "KC144.XNAV.W28",
        "KC144.XNAV.W29",
        "KC144.XNAV.W30",
    ]
    assert waves[0]["title"] == (
        "RETURN-INDEPENDENT-IC10-DECISION-AND-CLOSE-CONTROL-LEDGER-REVIEW"
    )
    assert gate.snapshot["successor"] == (
        "KC144.XNAV.W32::OPEN-NEXT-OCTAVE-AUTHORITY-REGISTRY-AND-"
        "INDEPENDENT-IC10-QUORUM-GATE"
    )
    assert waves[-1]["successor"] == gate.snapshot["successor"]


def test_twenty_new_roles_and_records_are_cross_wave_disjoint():
    gate = _gate()
    roles = [item[1] for item in gate.expected_coordinates]
    kinds = [item[2] for item in gate.expected_coordinates]
    assert len(roles) == len(set(roles)) == 20
    assert len(kinds) == len(set(kinds)) == 20
    contract = gate.snapshot["verification_contract"]
    assert contract["total_cross_wave_roles"] == 45
    assert contract["w25_w26_record_count"] == 24
    assert contract["total_record_count"] == 44
    assert contract["atomic_five_wave_closure_required"] is True


def test_production_snapshot_is_empty_and_non_effecting():
    gate = _gate()
    assert gate.snapshot["authority_registry"] == {
        "sources": [],
        "revisions": [],
    }
    assert gate.snapshot["record_ledger"] == []
    assert set(gate.snapshot["production_counts"].values()) == {0}
    status = gate.status()
    protected = (
        "runtime_mutated_authority_registry",
        "runtime_mutated_control_ledger",
        "runtime_issued_decision_or_disposition",
        "runtime_published_artifact",
        "runtime_activated_endpoint",
        "workflow_dispatched",
        "endpoint_contacted",
        "image_published",
        "merged",
        "deployed",
        "promoted",
        "production_effect_claimed",
    )
    assert all(status[field] is False for field in protected)


@pytest.mark.parametrize(
    "decision", ["APPROVED", "REJECTED_ROLLED_BACK", "HOLD"]
)
def test_complete_twenty_record_bundle_verifies_without_effect(decision):
    result = _evaluate(_bundle(decision))
    assert result["status"] == (
        "PASS_W27_W31_COMPLETE_SIGNED_EVIDENCE_BUNDLE__"
        "VERIFIER_REMAINS_NON_EFFECTING"
    )
    assert result["decision"] == decision
    assert result["external_signed_bundle_verified"] is True
    assert len(result["wave_certificates"]) == 5
    assert result["closure"]["record_count"] == 20
    assert result["closure"]["production_effect_claimed"] is False
    assert result["production_effect_claimed"] is False


def test_partial_bundle_is_rejected_atomically():
    bundle = _bundle()
    bundle["records"].pop()
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert result["external_signed_bundle_verified"] is False


def test_duplicate_outer_json_key_is_rejected():
    text = '{"sources":[],"sources":[],"revisions":[],"records":[]}'
    result = _gate().verify_bundle(text)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "duplicate JSON member" in result["error"]


def test_decision_cannot_change_between_waves():
    bundle = _bundle()
    bundle["records"][4]["decision"] = "APPROVED"
    _sign(bundle["records"][4], bundle["records"][4]["role"])
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "decision changed" in result["error"]


def test_record_chain_break_is_rejected():
    bundle = _bundle()
    bundle["records"][9]["previous_record_digest"] = W26_RUNTIME_RECEIPT
    bundle["records"][9]["subject_digest"] = W26_RUNTIME_RECEIPT
    _sign(bundle["records"][9], bundle["records"][9]["role"])
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "chain link mismatch" in result["error"]


def test_effect_claim_is_rejected_even_with_valid_signature():
    bundle = _bundle()
    bundle["records"][12]["effect_claimed"] = True
    _sign(bundle["records"][12], bundle["records"][12]["role"])
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "cannot claim production effect" in result["error"]


def test_non_increasing_chronology_is_rejected():
    bundle = _bundle()
    bundle["records"][7]["occurred_at"] = bundle["records"][6]["occurred_at"]
    _sign(bundle["records"][7], bundle["records"][7]["role"])
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "chronology or lag invalid" in result["error"]


def test_wrong_signature_is_rejected():
    bundle = _bundle()
    record = bundle["records"][15]
    record["signature"]["value"] = bundle["records"][14]["signature"]["value"]
    record["record_digest"] = _digest(_addressed(record, "record_digest"))
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "signature mismatch" in result["error"]


def test_key_reuse_across_roles_is_rejected():
    bundle = _bundle()
    first = bundle["revisions"][0]
    second = bundle["revisions"][1]
    second["public_key_base64"] = first["public_key_base64"]
    second["fingerprint"] = first["fingerprint"]
    second["revision_digest"] = _digest(
        _addressed(second, "revision_digest")
    )
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED"
    assert "identity and key axes must be disjoint" in result["error"]


def test_wave_inspection_and_template_cover_all_five_waves():
    gate = _gate()
    for wave in range(27, 32):
        result = gate.inspect_wave(wave)
        assert result["status"] == f"PASS_W{wave}_PROTOCOL_PINNED"
        assert len(result["record_schemas"]) == 4
    assert gate.inspect_wave(32)["status"] == "HOLD_W27_W31_WAVE_OUT_OF_RANGE"


def test_contract_and_receipt_are_content_addressed():
    snapshot = json.loads(DATA_PATH.read_text())
    stored_contract = snapshot.pop("contract_digest")
    assert _digest(snapshot) == stored_contract == W27_W31_CONTRACT
    receipt = json.loads(RECEIPT_PATH.read_text())
    stored_receipt = receipt.pop("receipt_id")
    assert stored_receipt == EXPECTED_RECEIPT
    assert (
        "w27-w31-five-wave-protocol:sha256:" + _digest(receipt).split(":", 1)[1]
    ) == EXPECTED_RECEIPT


def test_snapshot_cli_is_fail_closed_and_green():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/w27_w31_five_wave_closure.py",
            "--check-snapshot",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "PASS_W27_W31_FROZEN_EMPTY_FIVE_WAVE_PROTOCOL" in result.stdout


def test_contract_drift_fails_closed():
    snapshot = json.loads(DATA_PATH.read_text())
    snapshot["successor"] = "KC144.XNAV.W32::DRIFT"
    snapshot["contract_digest"] = _digest(
        _addressed(snapshot, "contract_digest")
    )
    with pytest.raises(ValueError, match="frozen contract drift"):
        FrozenFiveWaveReviewClosure(
            snapshot,
            verification_time=VERIFICATION_TIME,
        )


def test_loader_wraps_invalid_snapshot(monkeypatch):
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: '{"schema":"broken"}',
    )
    with pytest.raises(FiveWaveReviewClosureError):
        FrozenFiveWaveReviewClosure.load()
