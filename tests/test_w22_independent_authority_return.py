"""Adversarial contracts for KC144.XNAV.W22."""

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

from crystal_108d.independent_authority_return import (  # noqa: E402
    CANDIDATE_SCHEMA,
    COMMIT_RETURN_SCHEMA,
    CORRECTION_SCHEMA,
    LEDGER_ENTRY_SCHEMA,
    OBSERVATION_SCHEMA,
    PROMOTION_RETURN_SCHEMA,
    REVISION_SCHEMA,
    SOURCE_SCHEMA,
    W20_TARGET_HEAD,
    W21_CANDIDATE_IMAGE,
    W21_CONTRACT,
    W21_HEAD,
    W21_PARENT,
    W21_RECEIPT,
    W21_TREE,
    FrozenIndependentAuthorityReturn,
    IndependentAuthorityReturnError,
    _addressed,
    _digest,
    _signed,
    register_independent_authority_return,
)


DATA = ROOT / "MCP" / "data" / "w22_independent_authority_return.json"
RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w22-independent-authority-return.json"
)
WORKFLOW = (
    ROOT / ".github" / "workflows" / "w22-independent-authority-return.yml"
)
SEEDS = {
    "commit": bytes.fromhex("01" * 32),
    "observer": bytes.fromhex("02" * 32),
    "promotion": bytes.fromhex("03" * 32),
    "correction": bytes.fromhex("04" * 32),
}
POLICY = "sha256:" + "a" * 64
IC10_PACKET = "sha256:" + "b" * 64
IC10_DECISION = "sha256:" + "c" * 64
ENTRY = "sha256:" + "d" * 64
ROOT_BEFORE = "sha256:" + "e" * 64
ROOT_AFTER = "sha256:" + "f" * 64
BLOB = "sha256:" + "1" * 64


def _private(name: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(SEEDS[name])


def _public(name: str) -> str:
    return base64.b64encode(
        _private(name).public_key().public_bytes_raw()
    ).decode()


def _fingerprint(public: str) -> str:
    return "sha256:" + hashlib.sha256(base64.b64decode(public)).hexdigest()


def _source(name: str, role: str) -> dict:
    value = {
        "schema": SOURCE_SCHEMA,
        "source_id": f"source.{name}",
        "authority_id": f"authority.{name}",
        "role": role,
        "governance_repository": "demeet2k/Athena",
        "scope_kind": f"scope.{name}",
        "source_digest": "",
    }
    value["source_digest"] = _digest(_addressed(value, "source_digest"))
    return value


def _scope(name: str) -> dict:
    if name == "commit":
        operation, repository, ref, environment = (
            "ledger.commit",
            "demeet2k/Athena",
            "refs/heads/ledger",
            "kc144-ledger",
        )
    elif name == "observer":
        operation, repository, ref, environment = (
            "ledger.observe",
            "demeet2k/Athena",
            "refs/heads/ledger",
            "kc144-ledger",
        )
    elif name == "promotion":
        operation, repository, ref, environment = (
            "promotion.policy",
            "demeet2k/athena-mcp-server",
            "refs/heads/main",
            "kc144-production",
        )
    else:
        operation, repository, ref, environment = (
            "return.correct",
            "demeet2k/Athena",
            "refs/heads/return-ledger",
            "kc144-control",
        )
    return {
        "operation": operation,
        "repository": repository,
        "ref": ref,
        "environment": environment,
        "target_head": W20_TARGET_HEAD,
        "target_image_id": W21_CANDIDATE_IMAGE,
        "policy_digest": POLICY,
    }


def _revision(name: str, role: str, source: dict) -> dict:
    public = _public(name)
    value = {
        "schema": REVISION_SCHEMA,
        "source_digest": source["source_digest"],
        "revision_id": f"revision.{name}.v1",
        "role": role,
        "repository": "demeet2k/Athena",
        "ref": f"refs/heads/authority-{name}",
        "commit": (str(len(name)) * 40)[:40],
        "tree": (str(len(name) + 1) * 40)[:40],
        "path": f".athena/authorities/{name}.json",
        "blob_digest": "sha256:" + str((len(name) + 2) % 10) * 64,
        "content_digest": "sha256:" + str((len(name) + 3) % 10) * 64,
        "parent_revision_digest": None,
        "key_id": f"key.{name}.v1",
        "public_key_base64": public,
        "fingerprint": _fingerprint(public),
        "valid_from": "2026-07-27T00:00:00Z",
        "valid_until": "2027-07-27T00:00:00Z",
        "scope": _scope(name),
        "revision_digest": "",
    }
    value["revision_digest"] = _digest(
        _addressed(value, "revision_digest")
    )
    return value


def _snapshot() -> tuple[dict, dict[str, dict], dict[str, dict]]:
    snapshot = json.loads(DATA.read_text())
    roles = {
        "commit": "LEDGER_COMMIT",
        "observer": "LEDGER_OBSERVER",
        "promotion": "PROMOTION_DECISION",
        "correction": "CORRECTION",
    }
    sources = {name: _source(name, role) for name, role in roles.items()}
    revisions = {
        name: _revision(name, role, sources[name])
        for name, role in roles.items()
    }
    snapshot["authority_source_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["boundaries"]["production_authority_source_count"] = 4
    snapshot["boundaries"]["production_authority_revision_count"] = 4
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    return snapshot, sources, revisions


def _gate() -> FrozenIndependentAuthorityReturn:
    return FrozenIndependentAuthorityReturn.from_snapshot(_snapshot()[0])


def _custody() -> dict:
    return {
        "w21_head": W21_HEAD,
        "w21_tree": W21_TREE,
        "w21_sole_parent": W21_PARENT,
        "w21_contract_digest": W21_CONTRACT,
        "w21_receipt_id": W21_RECEIPT,
    }


def _sign(value: dict, name: str, digest_field: str) -> dict:
    value["signature"] = {
        "key_id": f"key.{name}.v1",
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


def _commit_return() -> dict:
    _, sources, revisions = _snapshot()
    value = {
        "schema": COMMIT_RETURN_SCHEMA,
        "custody": _custody(),
        "source_digest": sources["commit"]["source_digest"],
        "revision_digest": revisions["commit"]["revision_digest"],
        "occurrence_id": "occurrence.commit.0001",
        "transaction_digest": "sha256:" + "2" * 64,
        "authorization_digest": "sha256:" + "3" * 64,
        "ic10_review_packet_digest": IC10_PACKET,
        "ic10_decision_digest": IC10_DECISION,
        "ledger_repository": "demeet2k/Athena",
        "ledger_ref": "refs/heads/ledger",
        "ledger_commit": "4" * 40,
        "parent_commit": "3" * 40,
        "tree": "5" * 40,
        "ledger_path": ".athena/return-ledger.json",
        "ledger_blob_digest": BLOB,
        "sequence": 1,
        "previous_entry_digest": None,
        "ledger_root_before": ROOT_BEFORE,
        "ledger_root_after": ROOT_AFTER,
        "entry_digest": ENTRY,
        "authorized_at": "2026-07-27T01:00:00Z",
        "authorization_expires_at": "2026-07-27T02:00:00Z",
        "occurred_at": "2026-07-27T01:10:00Z",
        "nonce": "nonce.commit.0001",
        "policy_digest": POLICY,
        "signature": {"key_id": "key.commit.v1", "value": ""},
        "return_digest": "",
    }
    return _sign(value, "commit", "return_digest")


def _observation(commit_return: dict | None = None) -> dict:
    commit_return = commit_return or _commit_return()
    _, sources, revisions = _snapshot()
    value = {
        "schema": OBSERVATION_SCHEMA,
        "source_digest": sources["observer"]["source_digest"],
        "revision_digest": revisions["observer"]["revision_digest"],
        "occurrence_id": "occurrence.observation.0001",
        "commit_return_digest": commit_return["return_digest"],
        "repository": commit_return["ledger_repository"],
        "ref": commit_return["ledger_ref"],
        "commit": commit_return["ledger_commit"],
        "parent_commit": commit_return["parent_commit"],
        "tree": commit_return["tree"],
        "path": commit_return["ledger_path"],
        "blob_digest": commit_return["ledger_blob_digest"],
        "previous_root": commit_return["ledger_root_before"],
        "resulting_root": commit_return["ledger_root_after"],
        "observed_ref_tip": commit_return["ledger_commit"],
        "observed_at": "2026-07-27T01:11:00Z",
        "signature": {"key_id": "key.observer.v1", "value": ""},
        "observation_digest": "",
    }
    return _sign(value, "observer", "observation_digest")


def _promotion(
    commit_return: dict | None = None,
    observation: dict | None = None,
    decision: str = "AUTHORIZE_PROMOTION",
) -> dict:
    commit_return = commit_return or _commit_return()
    observation = observation or _observation(commit_return)
    _, sources, revisions = _snapshot()
    value = {
        "schema": PROMOTION_RETURN_SCHEMA,
        "custody": _custody(),
        "source_digest": sources["promotion"]["source_digest"],
        "revision_digest": revisions["promotion"]["revision_digest"],
        "occurrence_id": "occurrence.promotion.0001",
        "commit_return_digest": commit_return["return_digest"],
        "git_observation_digest": observation["observation_digest"],
        "ledger_root": commit_return["ledger_root_after"],
        "entry_digest": commit_return["entry_digest"],
        "ic10_review_packet_digest": commit_return["ic10_review_packet_digest"],
        "ic10_decision_digest": commit_return["ic10_decision_digest"],
        "target": {
            "runtime_repository": "demeet2k/athena-mcp-server",
            "runtime_head": W20_TARGET_HEAD,
            "candidate_image_id": W21_CANDIDATE_IMAGE,
            "target_environment": "kc144-production",
            "target_ref": "refs/heads/main",
        },
        "decision": decision,
        "decided_at": "2026-07-27T01:12:00Z",
        "nonce": "nonce.promotion.0001",
        "policy_digest": POLICY,
        "signature": {"key_id": "key.promotion.v1", "value": ""},
        "return_digest": "",
    }
    return _sign(value, "promotion", "return_digest")


def _closure(
    gate: FrozenIndependentAuthorityReturn | None = None,
    decision: str = "AUTHORIZE_PROMOTION",
) -> dict:
    gate = gate or _gate()
    commit_return = _commit_return()
    observation = _observation(commit_return)
    promotion = _promotion(commit_return, observation, decision)
    return gate.evaluate_closure(
        json.dumps(commit_return),
        json.dumps(observation),
        json.dumps(promotion),
    )


def test_production_snapshot_is_empty_and_fail_closed() -> None:
    status = FrozenIndependentAuthorityReturn.load().status()
    assert status["authority_source_count"] == 0
    assert status["authority_revision_count"] == 0
    assert status["admitted_return_count"] == 0
    assert status["w21_custody_grants_authority"] is False
    assert status["ledger_entry_committed"] is False
    assert status["promotion_authorized"] is False
    assert status["promotion_executed"] is False


def test_w22_receipt_is_content_addressed_and_boundary_exact() -> None:
    receipt = json.loads(RECEIPT.read_text())
    expected = "w22-independent-return:" + _digest(
        {key: value for key, value in receipt.items() if key != "receipt_id"}
    )
    assert receipt["receipt_id"] == expected
    assert receipt["lineage"]["w21_head"] == W21_HEAD
    assert receipt["lineage"]["w21_tree"] == W21_TREE
    assert receipt["lineage"]["w21_sole_parent"] == W21_PARENT
    assert receipt["contract"]["production_authority_source_count"] == 0
    assert receipt["contract"]["production_authority_revision_count"] == 0
    assert receipt["contract"]["production_return_ledger_entry_count"] == 0
    assert all(
        receipt["boundaries"][field] is False
        for field in (
            "w21_custody_grants_authority",
            "ledger_commit_return_verified",
            "git_commit_observed",
            "ledger_entry_committed",
            "promotion_authorized",
            "promotion_execution_authorized",
            "promotion_executed",
            "deployment_claimed",
            "merge_claimed",
            "promotion_claimed",
        )
    )


def test_w22_workflow_is_manual_read_only_and_secret_free() -> None:
    workflow = WORKFLOW.read_text()
    assert "workflow_dispatch:" in workflow
    assert "\npush:" not in workflow
    assert "\npull_request:" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "secrets." not in workflow
    assert "environment:" not in workflow
    assert "deploy" not in workflow.lower()
    assert "github-token" not in workflow.lower()


def test_exact_source_revision_occurrence_path_passes() -> None:
    result = _closure()
    assert result["status"].startswith(
        "PASS_W22_INDEPENDENT_COMMIT_AND_PROMOTION"
    )
    assert result["ledger_entry_committed"] is True
    assert result["promotion_authorized"] is True
    assert result["promotion_execution_authorized"] is False
    assert result["promotion_executed"] is False


def test_hold_promotion_never_opens_execution() -> None:
    result = _closure(decision="HOLD_PROMOTION")
    assert result["status"].endswith("PROMOTION_HELD__NO_EXECUTION_AUTHORITY")
    assert result["promotion_authorized"] is False
    assert result["execution_receipt_open"] is False
    assert result["promotion_execution_authorized"] is False


def test_standalone_promotion_cannot_manufacture_commit() -> None:
    result = _gate().inspect_promotion_return("{}", "{}", json.dumps(_promotion()))
    assert result["status"].startswith("HOLD_W22_LEDGER_COMMIT")
    assert result["ledger_entry_committed"] is False
    assert result["promotion_authorized"] is False


@pytest.mark.parametrize(
    ("part", "field", "replacement"),
    [
        ("commit", "source_digest", "sha256:" + "9" * 64),
        ("commit", "revision_digest", "sha256:" + "9" * 64),
        ("commit", "occurrence_id", "occurrence.commit.substituted"),
        ("commit", "ledger_commit", "9" * 40),
        ("commit", "tree", "9" * 40),
        ("commit", "ledger_blob_digest", "sha256:" + "9" * 64),
        ("commit", "ledger_root_after", "sha256:" + "9" * 64),
        ("commit", "ic10_decision_digest", "sha256:" + "9" * 64),
    ],
)
def test_commit_coordinate_tampering_rejected(
    part: str, field: str, replacement: str
) -> None:
    del part
    commit_return = _commit_return()
    observation = _observation(commit_return)
    commit_return[field] = replacement
    result = _gate().inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(observation)
    )
    assert result["status"] == "HOLD_W22_LEDGER_COMMIT_RETURN_REJECTED"


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("commit", "9" * 40),
        ("parent_commit", "9" * 40),
        ("tree", "9" * 40),
        ("blob_digest", "sha256:" + "9" * 64),
        ("observed_ref_tip", "9" * 40),
        ("resulting_root", "sha256:" + "9" * 64),
    ],
)
def test_git_observation_tampering_rejected(
    field: str, replacement: str
) -> None:
    commit_return = _commit_return()
    observation = _observation(commit_return)
    observation[field] = replacement
    result = _gate().inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(observation)
    )
    assert result["git_commit_observed"] is False
    assert result["ledger_entry_committed"] is False


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("commit_return_digest", "sha256:" + "9" * 64),
        ("git_observation_digest", "sha256:" + "9" * 64),
        ("ledger_root", "sha256:" + "9" * 64),
        ("ic10_review_packet_digest", "sha256:" + "9" * 64),
        ("decided_at", "2026-07-27T01:00:00Z"),
    ],
)
def test_promotion_cross_binding_tampering_rejected(
    field: str, replacement: str
) -> None:
    commit_return = _commit_return()
    observation = _observation(commit_return)
    promotion = _promotion(commit_return, observation)
    promotion[field] = replacement
    result = _gate().inspect_promotion_return(
        json.dumps(commit_return),
        json.dumps(observation),
        json.dumps(promotion),
    )
    assert result["promotion_decision_return_verified"] is False
    assert result["promotion_authorized"] is False


def test_w21_custody_head_cannot_replace_w20_target_head() -> None:
    commit_return = _commit_return()
    observation = _observation(commit_return)
    promotion = _promotion(commit_return, observation)
    promotion["target"]["runtime_head"] = W21_HEAD
    promotion = _sign(promotion, "promotion", "return_digest")
    result = _gate().inspect_promotion_return(
        json.dumps(commit_return),
        json.dumps(observation),
        json.dumps(promotion),
    )
    assert result["status"] == "HOLD_W22_PROMOTION_DECISION_RETURN_REJECTED"


def test_target_environment_scope_is_enforced() -> None:
    commit_return = _commit_return()
    observation = _observation(commit_return)
    promotion = _promotion(commit_return, observation)
    promotion["target"]["target_environment"] = "evidence-custody"
    promotion = _sign(promotion, "promotion", "return_digest")
    result = _gate().inspect_promotion_return(
        json.dumps(commit_return),
        json.dumps(observation),
        json.dumps(promotion),
    )
    assert result["promotion_authorized"] is False


@pytest.mark.parametrize(
    "field",
    ["authority_id", "key_id", "public_key_base64", "fingerprint"],
)
def test_cross_role_identity_and_key_aliases_rejected(field: str) -> None:
    snapshot, sources, revisions = _snapshot()
    if field == "authority_id":
        sources["promotion"][field] = sources["commit"][field]
        sources["promotion"]["source_digest"] = _digest(
            _addressed(sources["promotion"], "source_digest")
        )
        revisions["promotion"]["source_digest"] = sources["promotion"][
            "source_digest"
        ]
        revisions["promotion"]["revision_digest"] = _digest(
            _addressed(revisions["promotion"], "revision_digest")
        )
    else:
        revisions["promotion"][field] = revisions["commit"][field]
        if field == "public_key_base64":
            revisions["promotion"]["fingerprint"] = revisions["commit"][
                "fingerprint"
            ]
        revisions["promotion"]["revision_digest"] = _digest(
            _addressed(revisions["promotion"], "revision_digest")
        )
    snapshot["authority_source_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(IndependentAuthorityReturnError):
        FrozenIndependentAuthorityReturn.from_snapshot(snapshot)


def test_unpinned_caller_supplied_key_has_no_route() -> None:
    commit_return = _commit_return()
    commit_return["revision_digest"] = "sha256:" + "9" * 64
    commit_return = _sign(commit_return, "commit", "return_digest")
    result = _gate().inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(_observation(commit_return))
    )
    assert "not pinned" in result["error"]


def test_expired_authority_revision_rejected() -> None:
    snapshot, _, revisions = _snapshot()
    revisions["commit"]["valid_until"] = "2026-07-27T01:05:00Z"
    revisions["commit"]["revision_digest"] = _digest(
        _addressed(revisions["commit"], "revision_digest")
    )
    commit_source = revisions["commit"]["source_digest"]
    snapshot["authority_source_registry"]["revisions"] = list(revisions.values())
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    gate = FrozenIndependentAuthorityReturn.from_snapshot(snapshot)
    commit_return = _commit_return()
    commit_return["source_digest"] = commit_source
    commit_return["revision_digest"] = revisions["commit"]["revision_digest"]
    commit_return = _sign(commit_return, "commit", "return_digest")
    result = gate.inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(_observation(commit_return))
    )
    assert result["ledger_commit_return_verified"] is False


def test_authorization_expiry_rejected() -> None:
    commit_return = _commit_return()
    commit_return["occurred_at"] = "2026-07-27T02:01:00Z"
    commit_return = _sign(commit_return, "commit", "return_digest")
    result = _gate().inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(_observation(commit_return))
    )
    assert "authorization window" in result["error"]


def test_duplicate_json_member_rejected_at_nested_depth() -> None:
    commit_return = json.dumps(_commit_return())
    commit_return = commit_return.replace(
        '"w21_head":', '"w21_head":"0x-shadow","w21_head":', 1
    )
    result = _gate().inspect_ledger_commit_return(
        commit_return, json.dumps(_observation())
    )
    assert "duplicate JSON member" in result["error"]


def test_candidate_compilation_never_persists() -> None:
    gate = _gate()
    commit_return = _commit_return()
    observation = _observation(commit_return)
    result = gate.compile_ledger_candidate(
        json.dumps(commit_return), json.dumps(observation)
    )
    assert result["candidate"]["schema"] == CANDIDATE_SCHEMA
    assert result["candidate_persisted"] is False
    assert gate.snapshot["admitted_return_ledger"]["entries"] == []


def test_return_occurrence_equivocation_rejected() -> None:
    snapshot, _, _ = _snapshot()
    commit_return = _commit_return()
    entry = {
        "schema": LEDGER_ENTRY_SCHEMA,
        "sequence": 1,
        "previous_entry_digest": None,
        "kind": "LEDGER_COMMIT",
        "source_digest": commit_return["source_digest"],
        "revision_digest": commit_return["revision_digest"],
        "occurrence_id": commit_return["occurrence_id"],
        "payload_digest": "sha256:" + "9" * 64,
        "entry_digest": "",
    }
    entry["entry_digest"] = _digest(_addressed(entry, "entry_digest"))
    snapshot["admitted_return_ledger"]["entries"] = [entry]
    snapshot["boundaries"]["production_return_ledger_entry_count"] = 1
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    gate = FrozenIndependentAuthorityReturn.from_snapshot(snapshot)
    result = gate.inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(_observation(commit_return))
    )
    assert "equivocation" in result["error"]


def test_exact_occurrence_replay_is_idempotent() -> None:
    snapshot, _, _ = _snapshot()
    commit_return = _commit_return()
    entry = {
        "schema": LEDGER_ENTRY_SCHEMA,
        "sequence": 1,
        "previous_entry_digest": None,
        "kind": "LEDGER_COMMIT",
        "source_digest": commit_return["source_digest"],
        "revision_digest": commit_return["revision_digest"],
        "occurrence_id": commit_return["occurrence_id"],
        "payload_digest": commit_return["return_digest"],
        "entry_digest": "",
    }
    entry["entry_digest"] = _digest(_addressed(entry, "entry_digest"))
    snapshot["admitted_return_ledger"]["entries"] = [entry]
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    gate = FrozenIndependentAuthorityReturn.from_snapshot(snapshot)
    result = gate.inspect_ledger_commit_return(
        json.dumps(commit_return), json.dumps(_observation(commit_return))
    )
    assert result["idempotent_replay"] is True


def test_correction_cannot_erase_commit() -> None:
    _, sources, revisions = _snapshot()
    correction = {
        "schema": CORRECTION_SCHEMA,
        "stream_id": "stream.commit.0001",
        "sequence": 1,
        "previous_correction_digest": None,
        "corrects_return_digest": _commit_return()["return_digest"],
        "corrected_revision_digest": revisions["commit"]["revision_digest"],
        "replacement_return_digest": "sha256:" + "9" * 64,
        "reason_code": "ERASE_LEDGER_COMMIT",
        "occurred_at": "2026-07-27T01:20:00Z",
        "source_digest": sources["correction"]["source_digest"],
        "revision_digest": revisions["correction"]["revision_digest"],
        "occurrence_id": "occurrence.correction.0001",
        "signature": {"key_id": "key.correction.v1", "value": ""},
        "correction_digest": "",
    }
    correction = _sign(correction, "correction", "correction_digest")
    result = _gate().inspect_correction(json.dumps(correction))
    assert result["status"] == "HOLD_W22_CORRECTION_FORWARD_REJECTED"
    assert result["promotion_executed"] is False


def test_return_chain_rejects_fork_and_accepts_unique_chain() -> None:
    first = {
        "schema": LEDGER_ENTRY_SCHEMA,
        "sequence": 1,
        "previous_entry_digest": None,
        "kind": "LEDGER_COMMIT",
        "source_digest": "sha256:" + "1" * 64,
        "revision_digest": "sha256:" + "2" * 64,
        "occurrence_id": "occurrence.chain.0001",
        "payload_digest": "sha256:" + "3" * 64,
        "entry_digest": "",
    }
    first["entry_digest"] = _digest(_addressed(first, "entry_digest"))
    result = _gate().resolve_effective_returns(json.dumps([first]))
    assert result["status"] == "PASS_W22_UNIQUE_APPEND_ONLY_RETURN_CHAIN_RESOLVED"
    fork = deepcopy(first)
    fork["sequence"] = 2
    fork["previous_entry_digest"] = None
    fork["occurrence_id"] = "occurrence.chain.0002"
    fork["entry_digest"] = _digest(_addressed(fork, "entry_digest"))
    result = _gate().resolve_effective_returns(json.dumps([first, fork]))
    assert result["status"] == "HOLD_W22_RETURN_CHAIN_REJECTED"


def test_mcp_registration_has_eleven_tools_and_resource() -> None:
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
    register_independent_authority_return(mcp)
    assert len(mcp.tools) == 11
    assert mcp.resources == ["athena://w22-independent-authority-return"]
