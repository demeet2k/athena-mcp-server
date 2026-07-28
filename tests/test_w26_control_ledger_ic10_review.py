import base64
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
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
from MCP.crystal_108d.control_ledger_ic10_review import (
    AUTHORIZATION_SCHEMA,
    CANONICAL_AUTHORITY_PATH_PREFIX,
    CANONICAL_AUTHORITY_REF_PREFIX,
    CANONICAL_CONTROL_REF,
    CANONICAL_LEDGER_PATH,
    COMMIT_SCHEMA,
    CONTROL_PREDECESSOR_HEAD,
    DATA_PATH,
    IC10_DECISION_SCHEMA,
    OBSERVATION_SCHEMA,
    PHASE,
    REQUEST_OBSERVATION_SCHEMA,
    REVIEW_PACKET_SCHEMA,
    REVIEW_QUESTION,
    REVIEW_REQUEST_SCHEMA,
    REVISION_SCHEMA,
    ROLES,
    SCHEMA,
    SOURCE_SCHEMA,
    W25_CONTRACT,
    W26_CONTRACT,
    ZERO_ROOT,
    ControlLedgerIC10ReviewError,
    FrozenControlLedgerIC10Review,
    register_control_ledger_ic10_review,
)


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / ".athena"
    / "receipts"
    / "w26-control-ledger-ic10-review.json"
)
W25_TEST_PATH = ROOT / "tests" / "test_w25_persistent_promotion_settlement.py"
SPEC = importlib.util.spec_from_file_location("w26_w25_helpers", W25_TEST_PATH)
W25 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(W25)

W26_VERIFICATION_TIME = datetime(
    2026, 7, 27, 1, 27, tzinfo=timezone.utc
)
W25_RECORD_COUNT = 19
AUTHORIZATION_INDEX = 19
COMMIT_INDEX = 20
OBSERVATION_INDEX = 21
REQUEST_INDEX = 22
REQUEST_OBSERVATION_INDEX = 23


def _private(name: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("w26-" + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def _public(name: str) -> str:
    raw = _private(name).public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode()


def _fingerprint(name: str) -> str:
    return "sha256:" + hashlib.sha256(base64.b64decode(_public(name))).hexdigest()


def _sign(value: dict, name: str, digest_field: str) -> dict:
    value["signature"] = {
        "key_id": f"key.w26.{name}.v1",
        "value": base64.b64encode(
            _private(name).sign(
                json.dumps(
                    _signed(value, digest_field),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            )
        ).decode(),
    }
    value[digest_field] = _digest(_addressed(value, digest_field))
    return value


def _policy_digest() -> str:
    return _digest(
        {
            "schema": "athena.w26-control-review-policy/v1",
            "w25_contract_digest": W25_CONTRACT,
            "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
            "canonical_control_ref": CANONICAL_CONTROL_REF,
            "canonical_ledger_path": CANONICAL_LEDGER_PATH,
            "review_question": REVIEW_QUESTION,
        }
    )


def _snapshot(w25_gate):
    snapshot = json.loads(DATA_PATH.read_text())
    sources = {}
    revisions = {}
    policy = _policy_digest()
    for role in ROLES:
        name = role.lower()
        source = {
            "schema": SOURCE_SCHEMA,
            "source_id": f"source.w26.{name}",
            "authority_id": f"authority.w26.{name}",
            "role": role,
            "governance_repository": "demeet2k/Athena",
            "source_digest": "",
        }
        source["source_digest"] = _digest(
            _addressed(source, "source_digest")
        )
        revision = {
            "schema": REVISION_SCHEMA,
            "source_digest": source["source_digest"],
            "revision_id": f"revision.w26.{name}.v1",
            "role": role,
            "repository": "demeet2k/Athena",
            "ref": CANONICAL_AUTHORITY_REF_PREFIX + "test",
            "commit": hashlib.sha1(("w26-commit-" + name).encode()).hexdigest(),
            "tree": hashlib.sha1(("w26-tree-" + name).encode()).hexdigest(),
            "path": CANONICAL_AUTHORITY_PATH_PREFIX + f"{name}.json",
            "blob_digest": "",
            "content_digest": "sha256:"
            + hashlib.sha256(("w26-content-" + name).encode()).hexdigest(),
            "parent_revision_digest": None,
            "key_id": f"key.w26.{name}.v1",
            "public_key_base64": _public(name),
            "fingerprint": _fingerprint(name),
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-08-01T00:00:00Z",
            "scope": {
                "operation": ROLES[role],
                "repository": "demeet2k/Athena",
                "ref": CANONICAL_CONTROL_REF,
                "environment": "kc144-control",
                "policy_digest": policy,
            },
            "revision_digest": "",
        }
        revision["blob_digest"] = _digest(
            {
                "schema": "athena.w26-authority-blob-provenance/v1",
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
        sources[name] = source
        revisions[name] = revision
    snapshot["authority_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["boundaries"]["production_authority_source_count"] = len(sources)
    snapshot["boundaries"]["production_authority_revision_count"] = len(
        revisions
    )
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    return snapshot, sources, revisions


def _coordinates():
    w25_gate, w25_records = W25._coordinates()
    snapshot, sources, revisions = _snapshot(w25_gate)
    gate = FrozenControlLedgerIC10Review.from_snapshot(
        snapshot,
        w25_gate,
        verification_time=W26_VERIFICATION_TIME,
        allow_test_contract=True,
    )
    compiled = gate.compile_return(
        *(json.dumps(item) for item in w25_records)
    )
    transaction = compiled["transaction"]
    position = transaction["ledger_position"]
    entry = transaction["ledger_entry"]
    policy = _policy_digest()

    def coordinate(role):
        name = role.lower()
        return (
            sources[name]["source_digest"],
            revisions[name]["revision_digest"],
        )

    authorizer_source, authorizer_revision = coordinate(
        "CONTROL_LEDGER_COMMIT_AUTHORIZER"
    )
    authorization = {
        "schema": AUTHORIZATION_SCHEMA,
        "source_digest": authorizer_source,
        "revision_digest": authorizer_revision,
        "authorization_id": "authorization.w26.control.0001",
        "transaction_digest": transaction["transaction_digest"],
        "ledger_repository": position["repository"],
        "ledger_ref": position["ref"],
        "ledger_path": position["path"],
        "base_commit": position["base_commit"],
        "expected_sequence": position["sequence"],
        "previous_root": position["previous_root"],
        "proposed_root": position["proposed_root"],
        "entry_digest": entry["entry_digest"],
        "issued_at": "2026-07-27T01:22:00Z",
        "expires_at": "2026-07-27T01:32:00Z",
        "nonce": "nonce.w26.authorization.0001",
        "signature": {},
        "authorization_digest": "",
    }
    _sign(
        authorization,
        "control_ledger_commit_authorizer",
        "authorization_digest",
    )

    committer_source, committer_revision = coordinate(
        "CONTROL_LEDGER_COMMITTER"
    )
    tree = hashlib.sha1(b"w26-control-ledger-tree").hexdigest()
    content_digest = _digest(
        {
            "schema": "athena.w26-ledger-line-content/v1",
            "sequence": position["sequence"],
            "entry": entry,
        }
    )
    blob_digest = _digest(
        {
            "schema": "athena.w26-control-ledger-blob/v1",
            "repository": position["repository"],
            "ref": position["ref"],
            "path": position["path"],
            "parent_commit": position["base_commit"],
            "tree": tree,
            "content_digest": content_digest,
        }
    )
    commit = {
        "schema": COMMIT_SCHEMA,
        "source_digest": committer_source,
        "revision_digest": committer_revision,
        "occurrence_id": "occurrence.w26.control.commit.0001",
        "authorization_digest": authorization["authorization_digest"],
        "transaction_digest": transaction["transaction_digest"],
        "ledger_repository": position["repository"],
        "ledger_ref": position["ref"],
        "ledger_path": position["path"],
        "parent_commit": position["base_commit"],
        "commit": hashlib.sha1(b"w26-control-ledger-commit").hexdigest(),
        "tree": tree,
        "blob_digest": blob_digest,
        "content_digest": content_digest,
        "sequence": position["sequence"],
        "previous_root": position["previous_root"],
        "committed_root": position["proposed_root"],
        "entry_digest": entry["entry_digest"],
        "occurred_at": "2026-07-27T01:23:00Z",
        "nonce": "nonce.w26.commit.0001",
        "signature": {},
        "commit_occurrence_digest": "",
    }
    _sign(commit, "control_ledger_committer", "commit_occurrence_digest")

    observer_source, observer_revision = coordinate(
        "CONTROL_LEDGER_OBSERVER"
    )
    observation = {
        "schema": OBSERVATION_SCHEMA,
        "source_digest": observer_source,
        "revision_digest": observer_revision,
        "occurrence_id": "occurrence.w26.control.observation.0001",
        "commit_occurrence_digest": commit["commit_occurrence_digest"],
        "transaction_digest": transaction["transaction_digest"],
        "repository": commit["ledger_repository"],
        "ref": commit["ledger_ref"],
        "path": commit["ledger_path"],
        "commit": commit["commit"],
        "parent_commit": commit["parent_commit"],
        "tree": commit["tree"],
        "blob_digest": commit["blob_digest"],
        "content_digest": commit["content_digest"],
        "observed_ref_tip": commit["commit"],
        "sequence": commit["sequence"],
        "previous_root": commit["previous_root"],
        "observed_root": commit["committed_root"],
        "entry_digest": commit["entry_digest"],
        "observed_at": "2026-07-27T01:24:00Z",
        "nonce": "nonce.w26.observation.0001",
        "signature": {},
        "ledger_observation_digest": "",
    }
    _sign(
        observation,
        "control_ledger_observer",
        "ledger_observation_digest",
    )

    reviewer_source, reviewer_revision = coordinate(
        "INDEPENDENT_IC10_REVIEWER"
    )
    w25_closure = W25._closure(w25_gate, w25_records)
    packet = gate._review_packet(
        transaction,
        observation,
        {
            "closure_digest": w25_closure["closure_certificate"][
                "certificate_digest"
            ],
            "settlement_observation_digest": w25_closure[
                "closure_certificate"
            ]["settlement_observation_digest"],
        },
        reviewer_source,
        reviewer_revision,
    )
    requester_source, requester_revision = coordinate(
        "IC10_REVIEW_REQUEST_ISSUER"
    )
    request = {
        "schema": REVIEW_REQUEST_SCHEMA,
        "source_digest": requester_source,
        "revision_digest": requester_revision,
        "request_id": "request.w26.ic10.0001",
        "ledger_observation_digest": observation[
            "ledger_observation_digest"
        ],
        "transaction_digest": transaction["transaction_digest"],
        "w25_closure_certificate_digest": w25_closure[
            "closure_certificate"
        ]["certificate_digest"],
        "settlement_observation_digest": w25_closure[
            "closure_certificate"
        ]["settlement_observation_digest"],
        "reviewer_source_digest": reviewer_source,
        "reviewer_revision_digest": reviewer_revision,
        "review_packet_digest": packet["packet_digest"],
        "review_question": REVIEW_QUESTION,
        "requested_at": "2026-07-27T01:25:00Z",
        "nonce": "nonce.w26.request.0001",
        "signature": {},
        "review_request_digest": "",
    }
    _sign(request, "ic10_review_request_issuer", "review_request_digest")

    request_observer_source, request_observer_revision = coordinate(
        "IC10_REVIEW_REQUEST_OBSERVER"
    )
    channel_digest = _digest(
        {
            "schema": "athena.w26-ic10-review-channel/v1",
            "review_request_digest": request["review_request_digest"],
            "reviewer_source_digest": reviewer_source,
            "reviewer_revision_digest": reviewer_revision,
            "review_packet_digest": packet["packet_digest"],
        }
    )
    request_observation = {
        "schema": REQUEST_OBSERVATION_SCHEMA,
        "source_digest": request_observer_source,
        "revision_digest": request_observer_revision,
        "occurrence_id": "occurrence.w26.request.observation.0001",
        "review_request_digest": request["review_request_digest"],
        "review_packet_digest": packet["packet_digest"],
        "reviewer_source_digest": reviewer_source,
        "reviewer_revision_digest": reviewer_revision,
        "channel_digest": channel_digest,
        "prior_request_count": 0,
        "observed_state": "OPEN_AWAITING_INDEPENDENT_IC10_DECISION",
        "observed_at": "2026-07-27T01:26:00Z",
        "nonce": "nonce.w26.request.observation.0001",
        "signature": {},
        "request_observation_digest": "",
    }
    _sign(
        request_observation,
        "ic10_review_request_observer",
        "request_observation_digest",
    )
    return gate, tuple(
        list(w25_records)
        + [
            authorization,
            commit,
            observation,
            request,
            request_observation,
        ]
    )


def _closure(gate=None, records=None):
    if gate is None or records is None:
        gate, records = _coordinates()
    return gate.evaluate_closure(*(json.dumps(item) for item in records))


def _resign(values, index, name, digest_field):
    records = list(deepcopy(values))
    _sign(records[index], name, digest_field)
    return tuple(records)


def test_production_w26_is_empty_and_fail_closed():
    status = FrozenControlLedgerIC10Review.load().status()
    assert status["authority_source_count"] == 0
    assert status["commit_occurrence_count"] == 0
    assert status["review_request_count"] == 0
    assert status["ic10_decision_count"] == 0
    assert status["ic10_review_open"] is False
    assert status["promotion_claimed"] is False


def test_complete_twenty_five_role_path_opens_review_without_decision():
    result = _closure()
    assert result["status"] == (
        "PASS_W26_PERSISTENT_SETTLEMENT_RETURNED_TO_CONTROL_LEDGER__"
        "INDEPENDENT_IC10_REVIEW_OPEN_DECISION_ABSENT"
    )
    for field in (
        "w25_settlement_verified",
        "control_ledger_authorization_verified",
        "control_ledger_commit_verified",
        "control_ledger_readback_verified",
        "ic10_review_request_verified",
        "ic10_review_request_observed",
        "ic10_review_open",
    ):
        assert result[field] is True
    assert result["ic10_decision_recorded"] is False
    assert result["ic10_decision_digest"] is None
    assert result["decision_template"]["schema"] == IC10_DECISION_SCHEMA
    assert result["decision_template"]["decision"] is None
    for field in (
        "runtime_mutated_registry",
        "runtime_mutated_control_ledger",
        "runtime_sent_review_request",
        "runtime_issued_ic10_decision",
        "workflow_dispatched",
        "endpoint_contacted",
        "merge_claimed",
        "deployment_claimed",
        "promotion_claimed",
    ):
        assert result[field] is False


def test_compile_return_produces_candidate_not_commit():
    gate, records = _coordinates()
    result = gate.compile_return(
        *(json.dumps(item) for item in records[:W25_RECORD_COUNT])
    )
    assert result["status"].endswith("CONTROL_LEDGER_AUTHORIZATION_OPEN")
    assert result["transaction"]["ledger_position"]["base_commit"] == (
        CONTROL_PREDECESSOR_HEAD
    )
    assert result["transaction"]["ledger_position"]["previous_root"] == ZERO_ROOT
    assert result["authorization_template"]["signature"]["value"] is None
    assert result["runtime_mutated_control_ledger"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("transaction_digest", "sha256:" + "1" * 64),
        ("ledger_ref", "refs/heads/attacker"),
        ("ledger_path", ".athena/ledger/other.jsonl"),
        ("base_commit", "1" * 40),
        ("expected_sequence", 2),
        ("previous_root", "sha256:" + "2" * 64),
        ("entry_digest", "sha256:" + "3" * 64),
    ],
)
def test_commit_authorization_binds_exact_transaction(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[AUTHORIZATION_INDEX][field] = value
    values = _resign(
        values,
        AUTHORIZATION_INDEX,
        "control_ledger_commit_authorizer",
        "authorization_digest",
    )
    result = _closure(gate, values)
    assert "commit authorization" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authorization_digest", "sha256:" + "4" * 64),
        ("parent_commit", "2" * 40),
        ("content_digest", "sha256:" + "5" * 64),
        ("blob_digest", "sha256:" + "6" * 64),
        ("committed_root", "sha256:" + "7" * 64),
    ],
)
def test_commit_occurrence_cannot_substitute_coordinates(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[COMMIT_INDEX][field] = value
    values = _resign(
        values,
        COMMIT_INDEX,
        "control_ledger_committer",
        "commit_occurrence_digest",
    )
    result = _closure(gate, values)
    assert "ledger commit" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("commit", "3" * 40),
        ("observed_ref_tip", "4" * 40),
        ("observed_root", "sha256:" + "8" * 64),
        ("entry_digest", "sha256:" + "9" * 64),
    ],
)
def test_independent_ledger_readback_is_exact(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[OBSERVATION_INDEX][field] = value
    values = _resign(
        values,
        OBSERVATION_INDEX,
        "control_ledger_observer",
        "ledger_observation_digest",
    )
    result = _closure(gate, values)
    assert "ledger observation" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ledger_observation_digest", "sha256:" + "a" * 64),
        ("w25_closure_certificate_digest", "sha256:" + "b" * 64),
        ("settlement_observation_digest", "sha256:" + "c" * 64),
        ("review_packet_digest", "sha256:" + "d" * 64),
        ("review_question", "PROMOTE"),
    ],
)
def test_review_request_cannot_rewrite_evidence_or_question(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_INDEX][field] = value
    values = _resign(
        values,
        REQUEST_INDEX,
        "ic10_review_request_issuer",
        "review_request_digest",
    )
    result = _closure(gate, values)
    assert "IC10 review request" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("review_request_digest", "sha256:" + "e" * 64),
        ("channel_digest", "sha256:" + "f" * 64),
        ("prior_request_count", 1),
        ("observed_state", "DECIDED_APPROVE"),
    ],
)
def test_request_observation_only_opens_review(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_OBSERVATION_INDEX][field] = value
    values = _resign(
        values,
        REQUEST_OBSERVATION_INDEX,
        "ic10_review_request_observer",
        "request_observation_digest",
    )
    result = _closure(gate, values)
    assert "review request observation" in result["error"]


def test_review_request_cannot_name_non_reviewer_authority():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_INDEX]["reviewer_source_digest"] = values[
        AUTHORIZATION_INDEX
    ]["source_digest"]
    values[REQUEST_INDEX]["reviewer_revision_digest"] = values[
        AUTHORIZATION_INDEX
    ]["revision_digest"]
    values = _resign(
        values,
        REQUEST_INDEX,
        "ic10_review_request_issuer",
        "review_request_digest",
    )
    result = _closure(gate, values)
    assert "authority role mismatch" in result["error"]


def test_request_observer_cannot_be_requester_or_reviewer():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_OBSERVATION_INDEX]["source_digest"] = values[
        REQUEST_INDEX
    ]["source_digest"]
    values[REQUEST_OBSERVATION_INDEX]["revision_digest"] = values[
        REQUEST_INDEX
    ]["revision_digest"]
    values = _resign(
        values,
        REQUEST_OBSERVATION_INDEX,
        "ic10_review_request_issuer",
        "request_observation_digest",
    )
    result = _closure(gate, values)
    assert "authority role mismatch" in result["error"]


def test_control_authorization_must_follow_w25_observation():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[AUTHORIZATION_INDEX]["issued_at"] = "2026-07-27T01:20:00Z"
    values = _resign(
        values,
        AUTHORIZATION_INDEX,
        "control_ledger_commit_authorizer",
        "authorization_digest",
    )
    result = _closure(gate, values)
    assert "chronology does not follow W25" in result["error"]


def test_w26_occurrence_axis_cannot_overlap_w25():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_OBSERVATION_INDEX]["occurrence_id"] = values[15][
        "occurrence_id"
    ]
    values = _resign(
        values,
        REQUEST_OBSERVATION_INDEX,
        "ic10_review_request_observer",
        "request_observation_digest",
    )
    result = _closure(gate, values)
    assert "overlaps W23-W25" in result["error"]


def test_w26_replay_nonces_are_pairwise_disjoint():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_OBSERVATION_INDEX]["nonce"] = values[REQUEST_INDEX]["nonce"]
    values = _resign(
        values,
        REQUEST_OBSERVATION_INDEX,
        "ic10_review_request_observer",
        "request_observation_digest",
    )
    result = _closure(gate, values)
    assert "replay nonces" in result["error"]


def test_boolean_prior_request_count_is_rejected():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[REQUEST_OBSERVATION_INDEX]["prior_request_count"] = False
    values = _resign(
        values,
        REQUEST_OBSERVATION_INDEX,
        "ic10_review_request_observer",
        "request_observation_digest",
    )
    result = _closure(gate, values)
    assert "exact int" in result["error"]


def test_w26_role_cannot_reuse_w25_identity():
    w25_gate, _ = W25._coordinates()
    snapshot, _, _ = _snapshot(w25_gate)
    prior = next(iter(w25_gate.sources.values()))
    source = snapshot["authority_registry"]["sources"][0]
    source["authority_id"] = prior["authority_id"]
    source["source_digest"] = _digest(_addressed(source, "source_digest"))
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(ControlLedgerIC10ReviewError, match="identity overlaps"):
        FrozenControlLedgerIC10Review.from_snapshot(
            snapshot,
            w25_gate,
            verification_time=W26_VERIFICATION_TIME,
            allow_test_contract=True,
        )


def test_w26_role_cannot_reuse_w24_key():
    w25_gate, _ = W25._coordinates()
    snapshot, _, _ = _snapshot(w25_gate)
    prior = next(iter(w25_gate.w24_gate.revisions.values()))
    revision = snapshot["authority_registry"]["revisions"][0]
    revision["key_id"] = prior["key_id"]
    revision["revision_digest"] = _digest(
        _addressed(revision, "revision_digest")
    )
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(ControlLedgerIC10ReviewError, match="key_id overlaps"):
        FrozenControlLedgerIC10Review.from_snapshot(
            snapshot,
            w25_gate,
            verification_time=W26_VERIFICATION_TIME,
            allow_test_contract=True,
        )


def test_duplicate_json_members_are_rejected():
    gate, records = _coordinates()
    serialized = [json.dumps(item) for item in records]
    serialized[REQUEST_INDEX] = serialized[REQUEST_INDEX].replace(
        '"request_id":',
        '"request_id":"shadow","request_id":',
        1,
    )
    result = gate.evaluate_closure(*serialized)
    assert "duplicate JSON member" in result["error"]


def test_complete_record_topology_is_required():
    gate, records = _coordinates()
    result = gate.evaluate_closure(
        *(json.dumps(item) for item in records[:-1])
    )
    assert "nineteen W25 and five W26" in result["error"]


def test_checked_in_decision_and_occurrence_ledgers_must_remain_empty():
    w25_gate, _ = W25._coordinates()
    snapshot, _, _ = _snapshot(w25_gate)
    snapshot["ic10_decision_ledger"] = [{"forged": True}]
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(ControlLedgerIC10ReviewError, match="must remain empty"):
        FrozenControlLedgerIC10Review.from_snapshot(
            snapshot,
            w25_gate,
            verification_time=W26_VERIFICATION_TIME,
            allow_test_contract=True,
        )


def test_contract_digest_phase_successor_and_role_count_are_exact():
    snapshot = json.loads(DATA_PATH.read_text())
    digest = snapshot.pop("contract_digest")
    assert snapshot["schema"] == SCHEMA
    assert snapshot["phase"] == PHASE
    assert snapshot["return_contract"]["total_cross_wave_roles"] == 25
    assert snapshot["successor"] == (
        "KC144.XNAV.W27::RETURN-INDEPENDENT-IC10-DECISION-AND-"
        "CLOSE-CONTROL-LEDGER-REVIEW"
    )
    assert digest == W26_CONTRACT
    assert digest == _digest(snapshot)


def test_receipt_is_content_addressed_and_matches_contract():
    receipt = json.loads(RECEIPT_PATH.read_text())
    assert receipt["receipt_id"] == (
        "w26-control-ledger-ic10-review:"
        + _digest(_addressed(receipt, "receipt_id"))
    )
    assert receipt["contract"]["contract_digest"] == W26_CONTRACT
    assert receipt["contract"]["total_cross_wave_roles"] == 25
    assert receipt["boundaries"]["production_ic10_decision_count"] == 0
    assert receipt["boundaries"]["ic10_review_open"] is False


def test_review_packet_is_content_addressed_and_nonpromotional():
    result = _closure()
    packet = result["review_packet"]
    assert packet["schema"] == REVIEW_PACKET_SCHEMA
    assert packet["packet_digest"] == _digest(
        _addressed(packet, "packet_digest")
    )
    assert packet["review_constraints"]["request_is_not_decision"] is True
    assert packet["review_constraints"]["promotion_authorized"] is False


def test_explanation_preserves_all_separation_laws():
    result = FrozenControlLedgerIC10Review.load().explain()
    assert result["total_cross_wave_roles"] == 25
    assert "REVIEW OPEN != INDEPENDENT IC10 DECISION" in result["law"]
    assert result["runtime_issued_ic10_decision"] is False
    assert result["promotion_claimed"] is False


def test_outer_bundle_duplicate_members_are_rejected(tmp_path):
    bundle = tmp_path / "duplicate.json"
    bundle.write_text('{"challenge":{},"challenge":{}}', encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "w26_control_ledger_ic10_review.py"),
            "--bundle",
            str(bundle),
            "--verifier-head",
            "0" * 40,
            "--verifier-tree",
            "0" * 40,
            "--verifier-ref",
            CANONICAL_CONTROL_REF,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "duplicate JSON member" in result.stderr


def test_cli_rejects_unbound_verifier_ref(tmp_path):
    from scripts.w26_control_ledger_ic10_review import BUNDLE_FIELDS

    bundle = tmp_path / "shape.json"
    bundle.write_text(
        json.dumps({field: {} for field in BUNDLE_FIELDS}),
        encoding="utf-8",
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "w26_control_ledger_ic10_review.py"),
            "--bundle",
            str(bundle),
            "--verifier-head",
            head,
            "--verifier-tree",
            tree,
            "--verifier-ref",
            "refs/heads/attacker",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "canonical ref" in result.stderr


def test_registration_has_seven_tools_and_one_resource():
    class FakeMCP:
        def __init__(self):
            self.tools = []
            self.resources = []

        def tool(self):
            def decorator(function):
                self.tools.append(function.__name__)
                return function

            return decorator

        def resource(self, uri):
            def decorator(function):
                self.resources.append(uri)
                return function

            return decorator

    mcp = FakeMCP()
    register_control_ledger_ic10_review(mcp)
    assert len(mcp.tools) == 7
    assert mcp.resources == ["athena://w26-control-ledger-ic10-review"]
