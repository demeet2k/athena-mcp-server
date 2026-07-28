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
    _canonical_bytes,
    _digest,
    _signed,
)
from MCP.crystal_108d.persistent_promotion_settlement import (
    BUNDLE_SCHEMA,
    CANONICAL_AUTHORITY_PATH_PREFIX,
    CANONICAL_AUTHORITY_REF_PREFIX,
    CANONICAL_PERSISTENCE_NAMESPACE,
    CANONICAL_PERSISTENCE_PROVIDER,
    DATA_PATH,
    EXTERNAL_LEDGER_SCHEMA,
    LOCATOR_SCHEMA,
    PERSISTENCE_OBSERVATION_SCHEMA,
    PERSISTENCE_PROOF_SCHEMA,
    PHASE,
    REVISION_SCHEMA,
    ROLES,
    REPLAY_GUARD_SCHEMA,
    SCHEMA,
    SETTLEMENT_OBSERVATION_SCHEMA,
    SETTLEMENT_SCHEMA,
    SOURCE_SCHEMA,
    FrozenPersistentPromotionSettlement,
    PersistentPromotionSettlementError,
    register_persistent_promotion_settlement,
)
from MCP.crystal_108d.execution_deployment_rollback_readback import (
    DEPLOYMENT_SCHEMA as W24_DEPLOYMENT_SCHEMA,
    ROLLBACK_OBSERVATION_SCHEMA as W24_ROLLBACK_OBSERVATION_SCHEMA,
)


ROOT = Path(__file__).resolve().parents[1]
HARDENING_RECEIPT_PATH = (
    ROOT
    / ".athena"
    / "receipts"
    / "w25-persistent-promotion-settlement-hardening.json"
)
W24_TEST_PATH = (
    ROOT / "tests" / "test_w24_execution_deployment_rollback_readback.py"
)
SPEC = importlib.util.spec_from_file_location("w24_test_helpers", W24_TEST_PATH)
W24 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(W24)

W25_VERIFICATION_TIME = datetime(
    2026, 7, 27, 1, 22, tzinfo=timezone.utc
)
W24_RECORD_COUNT = 15
PROOF_INDEX = W24_RECORD_COUNT
PERSISTENCE_INDEX = PROOF_INDEX + 1
SETTLEMENT_INDEX = PERSISTENCE_INDEX + 1
SETTLEMENT_OBSERVATION_INDEX = SETTLEMENT_INDEX + 1
W25_BUNDLE_FIELDS = (
    "challenge",
    "publication",
    "publication_observation",
    "policy_a",
    "policy_b",
    "execution_authorization",
    "execution",
    "execution_consumption",
    "promotion",
    "deployment",
    "health",
    "previous_safe_deployment",
    "rollback_authorization",
    "rollback_occurrence",
    "rollback_observation",
    "persistence_proof",
    "persistence_observation",
    "promotion_settlement",
    "settlement_observation",
)


def _private(name: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("w25-" + name).encode()).digest()
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
        "key_id": f"key.w25.{name}.v1",
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


def _snapshot(w24_gate=None):
    if w24_gate is None:
        w24_gate, _ = W24._coordinates()
    _, w24_records = W24._coordinates()
    policy = w24_records[0]["policy_digest"]
    snapshot = json.loads(DATA_PATH.read_text())
    sources = {}
    revisions = {}
    for role in ROLES:
        name = role.lower()
        source = {
            "schema": SOURCE_SCHEMA,
            "source_id": f"source.w25.{name}",
            "authority_id": f"authority.w25.{name}",
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
            "revision_id": f"revision.w25.{name}.v1",
            "role": role,
            "repository": "demeet2k/Athena",
            "ref": CANONICAL_AUTHORITY_REF_PREFIX + "test",
            "commit": hashlib.sha1(("commit-" + name).encode()).hexdigest(),
            "tree": hashlib.sha1(("tree-" + name).encode()).hexdigest(),
            "path": CANONICAL_AUTHORITY_PATH_PREFIX + f"{name}.json",
            "blob_digest": "",
            "content_digest": "sha256:" + hashlib.sha256(
                ("content-" + name).encode()
            ).hexdigest(),
            "parent_revision_digest": None,
            "key_id": f"key.w25.{name}.v1",
            "public_key_base64": _public(name),
            "fingerprint": _fingerprint(name),
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2027-08-01T00:00:00Z",
            "scope": {
                "operation": ROLES[role],
                "repository": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/production",
                "environment": "kc144-production",
                "policy_digest": policy,
            },
            "revision_digest": "",
        }
        revision["blob_digest"] = _digest(
            {
                "schema": "athena.w25-authority-blob-provenance/v1",
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
    w24_gate, w24_records = W24._coordinates()
    snapshot, sources, revisions = _snapshot(w24_gate)
    gate = FrozenPersistentPromotionSettlement.from_snapshot(
        snapshot,
        w24_gate,
        verification_time=W25_VERIFICATION_TIME,
        allow_test_contract=True,
    )
    closure = W24._closure(w24_gate, w24_records)
    target = deepcopy(w24_records[0]["target"])
    bundle_digest = _digest(
        {"schema": BUNDLE_SCHEMA, "records": list(w24_records)}
    )
    rollback = next(
        record
        for record in w24_records
        if record["schema"] == W24_ROLLBACK_OBSERVATION_SCHEMA
    )
    canonical_bundle = {
        "schema": BUNDLE_SCHEMA,
        "records": list(w24_records),
    }

    def coordinate(role):
        name = role.lower()
        return (
            sources[name]["source_digest"],
            revisions[name]["revision_digest"],
        )

    writer_source, writer_revision = coordinate("RETURN_PERSISTENCE_WRITER")
    proof = {
        "schema": PERSISTENCE_PROOF_SCHEMA,
        "source_digest": writer_source,
        "revision_digest": writer_revision,
        "occurrence_id": "occurrence.w25.persistence.0001",
        "w24_return_bundle_digest": bundle_digest,
        "w24_closure_certificate_digest": closure[
            "closure_certificate"
        ]["certificate_digest"],
        "w24_rollback_observation_digest": rollback[
            "rollback_observation_digest"
        ],
        "target": target,
        "object_digest": bundle_digest,
        "object_size_bytes": len(_canonical_bytes(canonical_bundle)),
        "storage_class": "CONTENT_ADDRESSED_IMMUTABLE",
        "locator_commitment": {
            "schema": LOCATOR_SCHEMA,
            "storage_provider": CANONICAL_PERSISTENCE_PROVIDER,
            "namespace": CANONICAL_PERSISTENCE_NAMESPACE,
            "object_key": bundle_digest,
            "version_id": "version.w25.persistence.0001",
            "retention_mode": "COMPLIANCE_LOCKED",
            "retention_until": "2027-07-28T01:18:00Z",
            "locator_commitment_digest": "",
        },
        "persisted_at": "2026-07-27T01:18:00Z",
        "retention_until": "2027-07-28T01:18:00Z",
        "signature": {},
        "persistence_proof_digest": "",
    }
    proof["locator_commitment"]["locator_commitment_digest"] = _digest(
        _addressed(
            proof["locator_commitment"], "locator_commitment_digest"
        )
    )
    _sign(proof, "return_persistence_writer", "persistence_proof_digest")

    observer_source, observer_revision = coordinate(
        "RETURN_PERSISTENCE_OBSERVER"
    )
    persistence_observation = {
        "schema": PERSISTENCE_OBSERVATION_SCHEMA,
        "source_digest": observer_source,
        "revision_digest": observer_revision,
        "occurrence_id": "occurrence.w25.persistence.observation.0001",
        "persistence_proof_digest": proof["persistence_proof_digest"],
        "object_digest": bundle_digest,
        "locator_commitment_digest": proof["locator_commitment"][
            "locator_commitment_digest"
        ],
        "readback_digest": bundle_digest,
        "target": target,
        "observed_state": "PERSISTED",
        "observed_at": "2026-07-27T01:19:00Z",
        "signature": {},
        "persistence_observation_digest": "",
    }
    _sign(
        persistence_observation,
        "return_persistence_observer",
        "persistence_observation_digest",
    )

    issuer_source, issuer_revision = coordinate("PROMOTION_SETTLEMENT_ISSUER")
    settlement = {
        "schema": SETTLEMENT_SCHEMA,
        "source_digest": issuer_source,
        "revision_digest": issuer_revision,
        "settlement_id": "settlement.w25.promotion.0001",
        "w24_closure_certificate_digest": closure[
            "closure_certificate"
        ]["certificate_digest"],
        "persistence_observation_digest": persistence_observation[
            "persistence_observation_digest"
        ],
        "target": target,
        "terminal_image_digest": rollback["observed_image_digest"],
        "terminal_state": "ROLLED_BACK_TO_PREVIOUS_SAFE_IMAGE",
        "promotion_disposition": "REJECTED_ROLLED_BACK",
        "issued_at": "2026-07-27T01:20:00Z",
        "signature": {},
        "promotion_settlement_digest": "",
    }
    _sign(
        settlement,
        "promotion_settlement_issuer",
        "promotion_settlement_digest",
    )

    settlement_source, settlement_revision = coordinate(
        "PROMOTION_SETTLEMENT_OBSERVER"
    )
    settlement_observation = {
        "schema": SETTLEMENT_OBSERVATION_SCHEMA,
        "source_digest": settlement_source,
        "revision_digest": settlement_revision,
        "occurrence_id": "occurrence.w25.settlement.observation.0001",
        "promotion_settlement_digest": settlement[
            "promotion_settlement_digest"
        ],
        "persistence_observation_digest": persistence_observation[
            "persistence_observation_digest"
        ],
        "target": target,
        "terminal_image_digest": rollback["observed_image_digest"],
        "observed_disposition": "REJECTED_ROLLED_BACK",
        "external_ledger_digest": "",
        "w24_return_bundle_digest": bundle_digest,
        "prior_settlement_count": 0,
        "replay_guard_digest": "",
        "observed_at": "2026-07-27T01:21:00Z",
        "signature": {},
        "settlement_observation_digest": "",
    }
    settlement_observation["external_ledger_digest"] = _digest(
        {
            "schema": EXTERNAL_LEDGER_SCHEMA,
            "promotion_settlement_digest": settlement[
                "promotion_settlement_digest"
            ],
            "persistence_observation_digest": persistence_observation[
                "persistence_observation_digest"
            ],
            "target": target,
            "terminal_image_digest": rollback["observed_image_digest"],
            "observed_disposition": "REJECTED_ROLLED_BACK",
        }
    )
    settlement_observation["replay_guard_digest"] = _digest(
        {
            "schema": REPLAY_GUARD_SCHEMA,
            "w24_return_bundle_digest": bundle_digest,
            "promotion_settlement_digest": settlement[
                "promotion_settlement_digest"
            ],
            "settlement_observation_occurrence_id": settlement_observation[
                "occurrence_id"
            ],
            "prior_settlement_count": 0,
        }
    )
    _sign(
        settlement_observation,
        "promotion_settlement_observer",
        "settlement_observation_digest",
    )
    return gate, tuple(
        list(w24_records)
        + [proof, persistence_observation, settlement, settlement_observation]
    )


def _gate_from_snapshot(snapshot, w24_gate):
    return FrozenPersistentPromotionSettlement.from_snapshot(
        snapshot,
        w24_gate,
        verification_time=W25_VERIFICATION_TIME,
        allow_test_contract=True,
    )


def _closure(gate=None, records=None):
    if gate is None or records is None:
        gate, records = _coordinates()
    return gate.evaluate_closure(*(json.dumps(value) for value in records))


def _resign(records, index, name, digest_field):
    values = list(deepcopy(records))
    _sign(values[index], name, digest_field)
    return tuple(values)


def _resign_w25_tail(records, start_index):
    values = list(deepcopy(records))
    proof = values[PROOF_INDEX]
    persistence = values[PERSISTENCE_INDEX]
    settlement = values[SETTLEMENT_INDEX]
    observation = values[SETTLEMENT_OBSERVATION_INDEX]
    if start_index <= PROOF_INDEX:
        _sign(proof, "return_persistence_writer", "persistence_proof_digest")
    if start_index <= PERSISTENCE_INDEX:
        persistence["persistence_proof_digest"] = proof[
            "persistence_proof_digest"
        ]
        persistence["object_digest"] = proof["object_digest"]
        persistence["locator_commitment_digest"] = proof[
            "locator_commitment"
        ]["locator_commitment_digest"]
        persistence["readback_digest"] = proof["object_digest"]
        _sign(
            persistence,
            "return_persistence_observer",
            "persistence_observation_digest",
        )
    if start_index <= SETTLEMENT_INDEX:
        settlement["persistence_observation_digest"] = persistence[
            "persistence_observation_digest"
        ]
        _sign(
            settlement,
            "promotion_settlement_issuer",
            "promotion_settlement_digest",
        )
    observation["promotion_settlement_digest"] = settlement[
        "promotion_settlement_digest"
    ]
    observation["persistence_observation_digest"] = persistence[
        "persistence_observation_digest"
    ]
    observation["external_ledger_digest"] = _digest(
        {
            "schema": EXTERNAL_LEDGER_SCHEMA,
            "promotion_settlement_digest": settlement[
                "promotion_settlement_digest"
            ],
            "persistence_observation_digest": persistence[
                "persistence_observation_digest"
            ],
            "target": observation["target"],
            "terminal_image_digest": observation["terminal_image_digest"],
            "observed_disposition": observation["observed_disposition"],
        }
    )
    observation["replay_guard_digest"] = _digest(
        {
            "schema": REPLAY_GUARD_SCHEMA,
            "w24_return_bundle_digest": observation[
                "w24_return_bundle_digest"
            ],
            "promotion_settlement_digest": settlement[
                "promotion_settlement_digest"
            ],
            "settlement_observation_occurrence_id": observation[
                "occurrence_id"
            ],
            "prior_settlement_count": observation["prior_settlement_count"],
        }
    )
    _sign(
        observation,
        "promotion_settlement_observer",
        "settlement_observation_digest",
    )
    return tuple(values)


def test_production_w25_is_empty_and_fail_closed():
    status = FrozenPersistentPromotionSettlement.load().status()
    assert status["authority_source_count"] == 0
    assert status["authority_revision_count"] == 0
    assert status["w24_image_published"] is False
    assert status["return_persistence_proved"] is False
    assert status["promotion_settlement_verified"] is False


def test_complete_nineteen_role_path_settles_rollback_without_side_effects():
    result = _closure()
    assert result["status"].startswith(
        "PASS_W25_W24_RETURNS_PERSISTED_AND_PROMOTION_REJECTION_SETTLED"
    )
    for field in (
        "w24_return_bundle_verified",
        "return_persistence_proved",
        "return_persistence_observed",
        "promotion_settlement_verified",
        "settlement_observation_verified",
    ):
        assert result[field] is True
    assert result["settlement_disposition"] == "REJECTED_ROLLED_BACK"
    assert result["settlement_replay_guard_verified"] is True
    assert result["settlement_closure_is_idempotent"] is True
    assert result["runtime_persisted_return"] is False
    assert result["runtime_issued_settlement"] is False
    assert result["workflow_dispatched"] is False
    assert result["endpoint_contacted"] is False
    assert result["deployment_claimed"] is False
    assert result["promotion_claimed"] is False


def test_complete_w24_return_bundle_is_required():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[W24_RECORD_COUNT - 1]["observed_state"] = "UNKNOWN"
    values = _resign(
        values,
        W24_RECORD_COUNT - 1,
        "rollback_observer",
        "rollback_observation_digest",
    )
    result = _closure(gate, values)
    assert "W24 rollback-terminal closure" in result["error"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("object_digest", "sha256:" + "1" * 64, "persistence proof"),
        (
            "w24_closure_certificate_digest",
            "sha256:" + "2" * 64,
            "persistence proof",
        ),
        (
            "w24_rollback_observation_digest",
            "sha256:" + "3" * 64,
            "persistence proof",
        ),
        ("storage_class", "MUTABLE", "persistence proof"),
        ("object_size_bytes", 0, "persistence proof"),
    ],
)
def test_persistence_proof_substitutions_rejected(field, value, message):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[PROOF_INDEX][field] = value
    values = _resign(
        values,
        PROOF_INDEX,
        "return_persistence_writer",
        "persistence_proof_digest",
    )
    result = _closure(gate, values)
    assert message in result["error"]


def test_persistence_requires_at_least_one_year_retention():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[PROOF_INDEX]["retention_until"] = "2026-07-28T01:18:00Z"
    locator = values[PROOF_INDEX]["locator_commitment"]
    locator["retention_until"] = values[PROOF_INDEX]["retention_until"]
    locator["locator_commitment_digest"] = _digest(
        _addressed(locator, "locator_commitment_digest")
    )
    values = _resign(
        values,
        PROOF_INDEX,
        "return_persistence_writer",
        "persistence_proof_digest",
    )
    result = _closure(gate, values)
    assert "retention" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("readback_digest", "sha256:" + "4" * 64),
        ("locator_commitment_digest", "sha256:" + "5" * 64),
        ("observed_state", "MISSING"),
    ],
)
def test_independent_persistence_readback_is_exact(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[PERSISTENCE_INDEX][field] = value
    values = _resign(
        values,
        PERSISTENCE_INDEX,
        "return_persistence_observer",
        "persistence_observation_digest",
    )
    result = _closure(gate, values)
    assert "persistence observation" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("terminal_image_digest", "sha256:" + "6" * 64),
        ("terminal_state", "PROMOTED"),
        ("promotion_disposition", "APPROVED"),
    ],
)
def test_rollback_terminal_state_cannot_be_reclassified_as_promotion(
    field, value
):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[SETTLEMENT_INDEX][field] = value
    values = _resign(
        values,
        SETTLEMENT_INDEX,
        "promotion_settlement_issuer",
        "promotion_settlement_digest",
    )
    result = _closure(gate, values)
    assert "rollback-terminal promotion settlement" in result["error"]


def test_settlement_cannot_precede_persistence_observation():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[SETTLEMENT_INDEX]["issued_at"] = "2026-07-27T01:18:30Z"
    values = _resign(
        values,
        SETTLEMENT_INDEX,
        "promotion_settlement_issuer",
        "promotion_settlement_digest",
    )
    result = _closure(gate, values)
    assert "rollback-terminal promotion settlement" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("promotion_settlement_digest", "sha256:" + "1" * 64),
        ("terminal_image_digest", "sha256:" + "2" * 64),
        ("observed_disposition", "APPROVED"),
    ],
)
def test_settlement_observation_is_independent_and_exact(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[SETTLEMENT_OBSERVATION_INDEX][field] = value
    values = _resign(
        values,
        SETTLEMENT_OBSERVATION_INDEX,
        "promotion_settlement_observer",
        "settlement_observation_digest",
    )
    result = _closure(gate, values)
    assert "settlement observation" in result["error"]


@pytest.mark.parametrize(
    ("index", "field"),
    [
        (PROOF_INDEX, "w24_return_bundle_digest"),
        (PERSISTENCE_INDEX, "persistence_proof_digest"),
        (SETTLEMENT_INDEX, "persistence_observation_digest"),
        (SETTLEMENT_OBSERVATION_INDEX, "promotion_settlement_digest"),
    ],
)
def test_every_w25_edge_is_digest_bound(index, field):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[index][field] = "sha256:" + "0" * 64
    result = _closure(gate, tuple(values))
    assert result["settlement_observation_verified"] is False


def test_w25_role_cannot_reuse_w24_key():
    w24_gate, _ = W24._coordinates()
    snapshot, _, revisions = _snapshot(w24_gate)
    w24_revision = next(iter(w24_gate.revisions.values()))
    target = revisions["return_persistence_writer"]
    target["key_id"] = w24_revision["key_id"]
    target["revision_digest"] = _digest(
        _addressed(target, "revision_digest")
    )
    snapshot["authority_registry"]["revisions"] = list(revisions.values())
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PersistentPromotionSettlementError):
        _gate_from_snapshot(snapshot, w24_gate)


def test_w25_role_cannot_reuse_w23_identity():
    w24_gate, _ = W24._coordinates()
    snapshot, sources, _ = _snapshot(w24_gate)
    w23_source = next(iter(w24_gate.w23_gate.sources.values()))
    target = sources["return_persistence_writer"]
    target["authority_id"] = w23_source["authority_id"]
    target["source_digest"] = _digest(
        _addressed(target, "source_digest")
    )
    snapshot["authority_registry"]["sources"] = list(sources.values())
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PersistentPromotionSettlementError):
        _gate_from_snapshot(snapshot, w24_gate)


def test_duplicate_json_members_rejected():
    gate, records = _coordinates()
    serialized = [json.dumps(value) for value in records]
    serialized[PROOF_INDEX] = serialized[PROOF_INDEX].replace(
        '"occurrence_id":',
        '"occurrence_id":"shadow","occurrence_id":',
        1,
    )
    result = gate.evaluate_closure(*serialized)
    assert "duplicate JSON member" in result["error"]


def test_checked_in_settlement_ledgers_must_remain_empty():
    w24_gate, _ = W24._coordinates()
    snapshot, _, _ = _snapshot(w24_gate)
    snapshot["promotion_settlement_ledger"] = [{"forged": True}]
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PersistentPromotionSettlementError):
        _gate_from_snapshot(snapshot, w24_gate)


def test_contract_digest_phase_and_successor_are_exact():
    snapshot = json.loads(DATA_PATH.read_text())
    claimed = snapshot.pop("contract_digest")
    assert snapshot["schema"] == SCHEMA
    assert snapshot["phase"] == PHASE
    assert snapshot["settlement_contract"]["total_cross_wave_roles"] == 19
    assert snapshot["successor"] == (
        "KC144.XNAV.W26::RETURN-PERSISTENT-SETTLEMENT-TO-CONTROL-"
        "LEDGER-AND-OPEN-INDEPENDENT-IC10-REVIEW"
    )
    assert claimed == _digest(snapshot)


def test_hardening_receipt_is_content_addressed_and_matches_contract():
    receipt = json.loads(HARDENING_RECEIPT_PATH.read_text())
    digest = _digest(_addressed(receipt, "receipt_id"))
    assert receipt["receipt_id"] == (
        "w25-promotion-settlement-hardening:" + digest
    )
    snapshot = json.loads(DATA_PATH.read_text())
    assert receipt["contract"]["contract_digest"] == snapshot["contract_digest"]
    assert receipt["contract"]["total_cross_wave_roles"] == 19
    assert (
        receipt["active_verifier_dependencies"][
            "active_w24_hardened_contract_digest"
        ]
        == snapshot["verifier_dependencies"]["active_w24_contract_digest"]
    )


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("boundaries", "promotion_claimed", True),
        ("settlement_contract", "runtime_can_issue_settlement", True),
    ],
)
def test_frozen_snapshot_rejects_readdressed_overclaims(section, field, value):
    w24_gate, _ = W24._coordinates()
    snapshot = json.loads(DATA_PATH.read_text())
    snapshot[section][field] = value
    snapshot["contract_digest"] = _digest(
        {key: item for key, item in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PersistentPromotionSettlementError):
        FrozenPersistentPromotionSettlement.from_snapshot(snapshot, w24_gate)


def test_production_contract_is_externally_pinned():
    w24_gate, _ = W24._coordinates()
    snapshot, _, _ = _snapshot(w24_gate)
    with pytest.raises(
        PersistentPromotionSettlementError,
        match="externally pinned",
    ):
        FrozenPersistentPromotionSettlement.from_snapshot(snapshot, w24_gate)


@pytest.mark.parametrize(
    ("target", "field", "value", "message"),
    [
        ("source", "governance_repository", "attacker/evil", "governance"),
        ("revision", "repository", "attacker/evil", "governance"),
        ("revision", "ref", "refs/tags/mutable", "governance"),
        ("revision", "path", "../../outside.json", "governance"),
        ("revision", "blob_digest", "sha256:" + "0" * 64, "blob provenance"),
    ],
)
def test_authority_provenance_is_canonical(
    target, field, value, message
):
    w24_gate, _ = W24._coordinates()
    snapshot, _, _ = _snapshot(w24_gate)
    record = snapshot["authority_registry"][
        "sources" if target == "source" else "revisions"
    ][0]
    record[field] = value
    digest_field = "source_digest" if target == "source" else "revision_digest"
    record[digest_field] = _digest(_addressed(record, digest_field))
    snapshot["contract_digest"] = _digest(
        {key: item for key, item in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PersistentPromotionSettlementError, match=message):
        _gate_from_snapshot(snapshot, w24_gate)


def test_w25_occurrence_axes_are_pairwise_disjoint():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[PERSISTENCE_INDEX]["occurrence_id"] = values[PROOF_INDEX][
        "occurrence_id"
    ]
    values = _resign_w25_tail(values, PERSISTENCE_INDEX)
    result = _closure(gate, values)
    assert "pairwise disjoint" in result["error"]


def test_w25_occurrence_axis_cannot_overlap_w24():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[PROOF_INDEX]["occurrence_id"] = values[6]["occurrence_id"]
    values = _resign_w25_tail(values, PROOF_INDEX)
    result = _closure(gate, values)
    assert "overlaps W23/W24" in result["error"]


def test_persistence_must_still_be_live_at_verification():
    _, records = _coordinates()
    w24_gate, _ = W24._coordinates()
    snapshot, _, _ = _snapshot(w24_gate)
    expired_gate = FrozenPersistentPromotionSettlement.from_snapshot(
        snapshot,
        w24_gate,
        verification_time=datetime(
            2027, 7, 29, 1, 22, tzinfo=timezone.utc
        ),
        allow_test_contract=True,
    )
    result = _closure(expired_gate, records)
    assert "retention" in result["error"]


def test_settlement_stages_must_be_fresh():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[SETTLEMENT_INDEX]["issued_at"] = "2026-07-27T01:40:00Z"
    values[SETTLEMENT_OBSERVATION_INDEX][
        "observed_at"
    ] = "2026-07-27T01:41:00Z"
    values = _resign_w25_tail(values, SETTLEMENT_INDEX)
    result = _closure(gate, values)
    assert "settlement" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("storage_provider", "MUTABLE_WEB"),
        ("namespace", "attacker/evil/latest"),
        ("object_key", "sha256:" + "1" * 64),
        ("retention_mode", "NONE"),
    ],
)
def test_structured_immutable_locator_is_exact(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    locator = values[PROOF_INDEX]["locator_commitment"]
    locator[field] = value
    locator["locator_commitment_digest"] = _digest(
        _addressed(locator, "locator_commitment_digest")
    )
    values = _resign_w25_tail(values, PROOF_INDEX)
    result = _closure(gate, values)
    assert "locator" in result["error"] or "persistence proof" in result["error"]


def test_w25_rechecks_exact_canonical_w24_deployment_reference():
    base_gate, w24_records = W24._coordinates()
    original_json = tuple(json.dumps(item) for item in w24_records)
    cached_closure = base_gate.evaluate_closure(*original_json)
    cached_all = base_gate._all(*original_json)

    class PermissiveW24Proxy:
        def __getattr__(self, name):
            return getattr(base_gate, name)

        def evaluate_closure(self, *records):
            return cached_closure

        def _all(self, *records):
            return cached_all

    proxy = PermissiveW24Proxy()
    snapshot, _, _ = _snapshot(proxy)
    gate = FrozenPersistentPromotionSettlement.from_snapshot(
        snapshot,
        proxy,
        verification_time=W25_VERIFICATION_TIME,
        allow_test_contract=True,
    )
    _, all_records = _coordinates()
    values = list(deepcopy(all_records))
    deployment = next(
        item for item in values if item["schema"] == W24_DEPLOYMENT_SCHEMA
    )
    deployment["immutable_reference"] = (
        "evil.invalid/image@" + deployment["manifest_digest"]
    )
    result = _closure(gate, tuple(values))
    assert "canonical publication target" in result["error"]


def test_outer_bundle_duplicate_members_are_rejected(tmp_path):
    bundle = tmp_path / "duplicate.json"
    bundle.write_text('{"challenge":{},"challenge":{}}', encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "w25_persistent_promotion_settlement.py"),
            "--bundle",
            str(bundle),
            "--verifier-head",
            "0" * 40,
            "--verifier-tree",
            "0" * 40,
            "--verifier-ref",
            "refs/heads/agent/w15-reconcile-capsule-deep-hardening",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "duplicate JSON member" in result.stderr


def test_cli_rejects_unbound_verifier_coordinates(tmp_path):
    bundle = tmp_path / "shape.json"
    bundle.write_text(
        json.dumps({field: {} for field in W25_BUNDLE_FIELDS}),
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
            str(ROOT / "scripts" / "w25_persistent_promotion_settlement.py"),
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


@pytest.mark.parametrize("layer", ["w24", "w23"])
def test_nested_verifier_contracts_are_exact(layer):
    snapshot = json.loads(DATA_PATH.read_text())
    w24_gate = FrozenPersistentPromotionSettlement.load().w24_gate
    if layer == "w24":
        w24_gate.snapshot["contract_digest"] = "sha256:" + "0" * 64
        message = "active W24"
    else:
        w24_gate.w23_gate.snapshot["contract_digest"] = "sha256:" + "0" * 64
        message = "active W23"
    with pytest.raises(PersistentPromotionSettlementError, match=message):
        FrozenPersistentPromotionSettlement.from_snapshot(snapshot, w24_gate)


def test_registration_has_seven_tools_and_resource():
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
    register_persistent_promotion_settlement(mcp)
    assert len(mcp.tools) == 7
    assert mcp.resources == [
        "athena://w25-persistent-promotion-settlement"
    ]
