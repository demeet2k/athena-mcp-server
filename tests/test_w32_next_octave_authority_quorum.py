import base64
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from MCP.crystal_108d.independent_authority_return import (
    _addressed,
    _digest,
    _signed,
)
from MCP.crystal_108d.next_octave_authority_quorum import (
    AUTHORITY_PATH_PREFIX,
    AUTHORITY_REF_PREFIX,
    CANONICAL_CONTROL_REF,
    CANONICAL_GOVERNANCE_REPOSITORY,
    CONTROL_PREDECESSOR_HEAD,
    CONTROL_PREDECESSOR_TREE,
    DATA_PATH,
    NEXT_OCTAVE_NAMESPACE,
    PHASE,
    QUORUM_LEDGER_PATH,
    RECORD_KINDS,
    REGISTRY_PATH,
    REVISION_SCHEMA,
    ROLES,
    RUNTIME_PREDECESSOR_HEAD,
    RUNTIME_PREDECESSOR_PARENT,
    RUNTIME_PREDECESSOR_TREE,
    SCHEMA,
    SOURCE_SCHEMA,
    W27_W31_CONTROL_RECEIPT,
    W27_W31_RUNTIME_RECEIPT,
    W32_CONTRACT,
    FrozenNextOctaveAuthorityQuorum,
    NextOctaveAuthorityQuorumError,
    _record_schema,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT / ".athena" / "receipts" / "w32-next-octave-authority-quorum.json"
)
VERIFICATION_TIME = datetime(2026, 7, 28, 1, 0, tzinfo=timezone.utc)
W31_HELPERS = runpy.run_path(
    str(ROOT / "tests" / "test_w27_w31_five_wave_closure.py")
)
_w31_bundle = W31_HELPERS["_bundle"]


def _private(role: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("w32:" + role).encode()).digest()
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
        "key_id": f"key.w32.{role.lower().replace('_', '-')}.v1",
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
    return FrozenNextOctaveAuthorityQuorum(
        json.loads(DATA_PATH.read_text()),
        verification_time=VERIFICATION_TIME,
    )


def _bundle(decision: str = "APPROVE_REGISTRY_OPEN"):
    gate = _gate()
    w31 = _w31_bundle()
    w31_result = gate.w31_gate.verify_bundle(
        json.dumps(w31, ensure_ascii=False, separators=(",", ":"))
    )
    w31_closure = w31_result["closure"]["closure_digest"]
    proposed_root = _digest(
        {
            "schema": "athena.w32-proposed-registry-root/v1",
            "w31_closure_digest": w31_closure,
            "contract_digest": W32_CONTRACT,
            "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
        }
    )
    sources = []
    revisions = []
    records = []
    previous = w31_closure
    start = datetime(2026, 7, 28, 0, 20, tzinfo=timezone.utc)
    for index, (role, kind) in enumerate(zip(ROLES, RECORD_KINDS)):
        name = role.lower().replace("_", "-")
        source = {
            "schema": SOURCE_SCHEMA,
            "source_id": f"source.w32.{name}",
            "authority_id": f"authority.w32.{name}",
            "role": role,
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
            "revision_id": f"revision.w32.{name}.v1",
            "role": role,
            "repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "ref": AUTHORITY_REF_PREFIX + f"{name}-test",
            "commit": hashlib.sha1(f"commit:w32:{role}".encode()).hexdigest(),
            "tree": hashlib.sha1(f"tree:w32:{role}".encode()).hexdigest(),
            "path": AUTHORITY_PATH_PREFIX + f"{name}.json",
            "blob_digest": "",
            "content_digest": "sha256:"
            + hashlib.sha256(f"content:w32:{role}".encode()).hexdigest(),
            "parent_revision_digest": None,
            "key_id": f"key.w32.{name}.v1",
            "public_key_base64": public,
            "fingerprint": _fingerprint(public),
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-07-28T00:00:00Z",
            "scope": {
                "operation": kind,
                "phase": PHASE,
                "repository": CANONICAL_GOVERNANCE_REPOSITORY,
                "ref": CANONICAL_CONTROL_REF,
                "environment": "kc144-next-octave-control",
                "policy_digest": gate.quorum_policy_digest,
            },
            "revision_digest": "",
        }
        revision["blob_digest"] = _digest(
            {
                "schema": "athena.w32-authority-blob-provenance/v1",
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
            "schema": _record_schema(kind),
            "phase": PHASE,
            "record_index": index,
            "record_kind": kind,
            "role": role,
            "source_digest": source["source_digest"],
            "revision_digest": revision["revision_digest"],
            "event_id": f"event.w32.{name}",
            "previous_record_digest": previous,
            "subject_digest": w31_closure,
            "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
            "registry_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "registry_ref": CANONICAL_CONTROL_REF,
            "registry_path": REGISTRY_PATH,
            "quorum_ledger_path": QUORUM_LEDGER_PATH,
            "proposed_registry_root": proposed_root,
            "quorum_policy_digest": gate.quorum_policy_digest,
            "decision": decision,
            "outcome": kind.upper(),
            "effect_claimed": False,
            "occurred_at": occurred_at,
            "nonce": f"nonce.w32.{name}",
            "signature": {"key_id": "", "value": ""},
            "record_digest": "",
        }
        _sign(record, role)
        previous = record["record_digest"]
        sources.append(source)
        revisions.append(revision)
        records.append(record)
    return {
        "w27_w31_bundle": w31,
        "sources": sources,
        "revisions": revisions,
        "records": records,
    }


def _evaluate(bundle):
    return _gate().verify_bundle(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":"))
    )


def test_frozen_snapshot_contract_and_exact_w31_predecessors():
    gate = _gate()
    assert gate.snapshot["schema"] == SCHEMA
    assert gate.snapshot["contract_digest"] == W32_CONTRACT
    predecessor = gate.snapshot["predecessor"]
    assert predecessor["runtime_head"] == RUNTIME_PREDECESSOR_HEAD
    assert predecessor["runtime_tree"] == RUNTIME_PREDECESSOR_TREE
    assert predecessor["runtime_sole_parent"] == RUNTIME_PREDECESSOR_PARENT
    assert predecessor["control_head"] == CONTROL_PREDECESSOR_HEAD
    assert predecessor["control_tree"] == CONTROL_PREDECESSOR_TREE
    assert predecessor["w27_w31_runtime_receipt_id"] == W27_W31_RUNTIME_RECEIPT
    assert predecessor["w27_w31_control_receipt_id"] == W27_W31_CONTROL_RECEIPT


def test_six_new_roles_form_51_role_and_50_record_topology():
    contract = _gate().snapshot["gate_contract"]
    assert len(ROLES) == len(set(ROLES)) == 6
    assert len(RECORD_KINDS) == len(set(RECORD_KINDS)) == 6
    assert contract["new_role_count"] == 6
    assert contract["total_cross_wave_roles"] == 51
    assert contract["w25_w31_record_count"] == 44
    assert contract["new_record_count"] == 6
    assert contract["total_record_count"] == 50
    assert contract["reviewer_quorum"] == "2_OF_2"
    assert contract["hold_dominates"] is True


def test_production_snapshot_is_empty_and_non_effecting():
    gate = _gate()
    assert gate.snapshot["authority_registry"] == {
        "sources": [],
        "revisions": [],
    }
    assert gate.snapshot["registry_charter_ledger"] == []
    assert gate.snapshot["authority_admission_ledger"] == []
    assert gate.snapshot["ic10_quorum_vote_ledger"] == []
    assert gate.snapshot["ic10_quorum_observation_ledger"] == []
    assert set(gate.snapshot["production_counts"].values()) == {0}
    assert all(value is False for value in {
        key: value
        for key, value in gate.status().items()
        if key in {
            "production_registry_open",
            "runtime_mutated_authority_registry",
            "runtime_mutated_quorum_ledger",
            "runtime_issued_ic10_vote",
            "workflow_dispatched",
            "endpoint_contacted",
            "image_published",
            "merged",
            "deployed",
            "promoted",
            "production_effect_claimed",
        }
    }.values())


def test_complete_approve_bundle_is_eligible_but_non_effecting():
    result = _evaluate(_bundle())
    assert result["status"] == (
        "PASS_W32_COMPLETE_SIGNED_AUTHORITY_AND_IC10_"
        "QUORUM_BUNDLE__VERIFIER_REMAINS_NON_EFFECTING"
    )
    assert result["external_w27_w31_bundle_verified"] is True
    assert result["quorum_evidence_satisfied"] is True
    assert result["control_admission_eligible"] is True
    assert result["closure"]["reviewer_approvals"] == 2
    assert result["closure"]["gate_state"] == "ELIGIBLE_FOR_CONTROL_ADMISSION"
    assert result["production_registry_open"] is False
    assert result["production_effect_claimed"] is False


def test_complete_hold_bundle_remains_closed():
    result = _evaluate(_bundle("HOLD_REGISTRY_CLOSED"))
    assert result["status"].startswith("PASS_W32_COMPLETE_SIGNED")
    assert result["quorum_evidence_satisfied"] is False
    assert result["control_admission_eligible"] is False
    assert result["closure"]["reviewer_approvals"] == 0
    assert result["closure"]["gate_state"] == "HOLD_REGISTRY_CLOSED"
    assert result["production_registry_open"] is False


def test_partial_w32_bundle_is_rejected_atomically():
    bundle = _bundle()
    bundle["records"].pop()
    result = _evaluate(bundle)
    assert result["status"] == "HOLD_W32_AUTHORITY_AND_IC10_QUORUM_BUNDLE_REJECTED"
    assert result["control_admission_eligible"] is False


def test_duplicate_outer_json_key_is_rejected():
    text = (
        '{"w27_w31_bundle":{},"sources":[],"sources":[],'
        '"revisions":[],"records":[]}'
    )
    result = _gate().verify_bundle(text)
    assert result["status"] == "HOLD_W32_AUTHORITY_AND_IC10_QUORUM_BUNDLE_REJECTED"
    assert "duplicate JSON member" in result["error"]


def test_incomplete_nested_w31_bundle_is_rejected():
    bundle = _bundle()
    bundle["w27_w31_bundle"]["records"].pop()
    result = _evaluate(bundle)
    assert result["external_w27_w31_bundle_verified"] is False
    assert "complete W27-W31 signed closure is required" in result["error"]


def test_decision_cannot_change_across_quorum_chain():
    bundle = _bundle()
    bundle["records"][3]["decision"] = "HOLD_REGISTRY_CLOSED"
    _sign(bundle["records"][3], bundle["records"][3]["role"])
    result = _evaluate(bundle)
    assert "decision changed across quorum chain" in result["error"]
    assert result["control_admission_eligible"] is False


def test_record_chain_break_is_rejected():
    bundle = _bundle()
    bundle["records"][2]["previous_record_digest"] = W27_W31_RUNTIME_RECEIPT
    _sign(bundle["records"][2], bundle["records"][2]["role"])
    result = _evaluate(bundle)
    assert "chain or subject drift" in result["error"]


def test_subject_drift_is_rejected():
    bundle = _bundle()
    bundle["records"][0]["subject_digest"] = W27_W31_RUNTIME_RECEIPT
    _sign(bundle["records"][0], bundle["records"][0]["role"])
    result = _evaluate(bundle)
    assert "chain or subject drift" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("registry_ref", "refs/heads/agent/not-w32"),
        ("registry_path", ".athena/registry/not-w32.jsonl"),
        ("quorum_ledger_path", ".athena/ledger/not-w32.jsonl"),
        ("proposed_registry_root", "sha256:" + "0" * 64),
        ("quorum_policy_digest", "sha256:" + "1" * 64),
    ],
)
def test_registry_binding_drift_is_rejected(field, value):
    bundle = _bundle()
    bundle["records"][-1][field] = value
    _sign(bundle["records"][-1], bundle["records"][-1]["role"])
    result = _evaluate(bundle)
    assert "registry binding drift" in result["error"]


def test_effect_claim_is_rejected_even_with_valid_signature():
    bundle = _bundle()
    bundle["records"][1]["effect_claimed"] = True
    _sign(bundle["records"][1], bundle["records"][1]["role"])
    result = _evaluate(bundle)
    assert "cannot claim production effect" in result["error"]


def test_non_increasing_chronology_is_rejected():
    bundle = _bundle()
    bundle["records"][4]["occurred_at"] = bundle["records"][3]["occurred_at"]
    _sign(bundle["records"][4], bundle["records"][4]["role"])
    result = _evaluate(bundle)
    assert "chronology or lag invalid" in result["error"]


def test_wrong_signature_is_rejected():
    bundle = _bundle()
    record = bundle["records"][5]
    record["signature"]["value"] = bundle["records"][4]["signature"]["value"]
    record["record_digest"] = _digest(_addressed(record, "record_digest"))
    result = _evaluate(bundle)
    assert "signature mismatch" in result["error"]


def test_w32_key_reuse_across_roles_is_rejected():
    bundle = _bundle()
    first = bundle["revisions"][0]
    second = bundle["revisions"][1]
    second["public_key_base64"] = first["public_key_base64"]
    second["fingerprint"] = first["fingerprint"]
    second["revision_digest"] = _digest(
        _addressed(second, "revision_digest")
    )
    result = _evaluate(bundle)
    assert "identity and key axes must be disjoint" in result["error"]


def test_w31_key_reuse_by_w32_role_is_rejected():
    bundle = _bundle()
    prior = bundle["w27_w31_bundle"]["revisions"][0]
    current = bundle["revisions"][0]
    current["public_key_base64"] = prior["public_key_base64"]
    current["fingerprint"] = prior["fingerprint"]
    current["revision_digest"] = _digest(
        _addressed(current, "revision_digest")
    )
    result = _evaluate(bundle)
    assert "overlaps W27-W31" in result["error"]


def test_event_and_nonce_reuse_is_rejected():
    bundle = _bundle()
    bundle["records"][4]["nonce"] = bundle["records"][3]["nonce"]
    _sign(bundle["records"][4], bundle["records"][4]["role"])
    result = _evaluate(bundle)
    assert "event and nonce axes must be disjoint" in result["error"]


def test_occurrence_axis_cannot_overlap_identity_axis():
    bundle = _bundle()
    bundle["records"][-1]["event_id"] = bundle["sources"][0]["source_id"]
    _sign(bundle["records"][-1], bundle["records"][-1]["role"])
    result = _evaluate(bundle)
    assert "occurrence axes overlap identity/key axes" in result["error"]


def test_contract_and_receipt_are_content_addressed():
    snapshot = json.loads(DATA_PATH.read_text())
    stored_contract = snapshot.pop("contract_digest")
    assert _digest(snapshot) == stored_contract == W32_CONTRACT
    receipt = json.loads(RECEIPT_PATH.read_text())
    stored_receipt = receipt.pop("receipt_id")
    assert stored_receipt.startswith(
        "w32-next-octave-authority-quorum:sha256:"
    )
    assert stored_receipt == (
        "w32-next-octave-authority-quorum:sha256:"
        + _digest(receipt).split(":", 1)[1]
    )


def test_snapshot_cli_is_fail_closed_and_green():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/w32_next_octave_authority_quorum.py",
            "--check-snapshot",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert (
        "PASS_W32_FROZEN_EMPTY_NEXT_OCTAVE_AUTHORITY_"
        "AND_IC10_QUORUM_PROTOCOL"
    ) in result.stdout


def test_contract_drift_fails_closed():
    snapshot = json.loads(DATA_PATH.read_text())
    snapshot["successor"] = "KC144.XNAV.W33::DRIFT"
    snapshot["contract_digest"] = _digest(
        _addressed(snapshot, "contract_digest")
    )
    with pytest.raises(ValueError, match="frozen contract drift"):
        FrozenNextOctaveAuthorityQuorum(
            snapshot,
            verification_time=VERIFICATION_TIME,
        )


def test_loader_wraps_invalid_snapshot(monkeypatch):
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda *args, **kwargs: '{"schema":"broken"}',
    )
    with pytest.raises(NextOctaveAuthorityQuorumError):
        FrozenNextOctaveAuthorityQuorum.load()
