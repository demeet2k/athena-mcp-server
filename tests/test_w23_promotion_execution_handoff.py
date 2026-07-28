"""Adversarial contracts for KC144.XNAV.W23."""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "MCP"))

from crystal_108d.promotion_execution_handoff import (  # noqa: E402
    AUTHORIZATION_SCHEMA,
    CHALLENGE_SCHEMA,
    DECISION_SCHEMA,
    OBSERVATION_SCHEMA,
    PUBLICATION_SCHEMA,
    REVISION_SCHEMA,
    SOURCE_SCHEMA,
    W22_CONTRACT,
    W22_HEAD,
    W22_LOCAL_IMAGE,
    W22_PARENT,
    W22_RECEIPT,
    W22_TREE,
    FrozenPromotionExecutionHandoff,
    PromotionExecutionHandoffError,
    _addressed,
    _digest,
    _signed,
    register_promotion_execution_handoff,
)


DATA = ROOT / "MCP" / "data" / "w23_promotion_execution_handoff.json"
HARDENING_RECEIPT = (
    ROOT
    / ".athena"
    / "receipts"
    / "w23-promotion-execution-handoff-hardening.json"
)
WORKFLOW = (
    ROOT / ".github" / "workflows" / "w23-promotion-execution-handoff.yml"
)
POLICY = "sha256:" + "a" * 64
PUBLISHED = "sha256:" + "9" * 64
REGISTRY_RESPONSE = "sha256:" + "d" * 64
ROLE_NAMES = {
    "challenge": "FRESHNESS_ISSUER",
    "publisher": "ARTIFACT_PUBLISHER",
    "observer": "ARTIFACT_OBSERVER",
    "policy_a": "PROMOTION_POLICY_A",
    "policy_b": "PROMOTION_POLICY_B",
    "execution": "EXECUTION_AUTHORIZER",
}
OPERATIONS = {
    "challenge": "promotion.challenge",
    "publisher": "artifact.publish",
    "observer": "artifact.observe",
    "policy_a": "promotion.policy.a",
    "policy_b": "promotion.policy.b",
    "execution": "promotion.execute.authorize",
}
SEEDS = {
    name: bytes([index]) * 32
    for index, name in enumerate(ROLE_NAMES, 1)
}

W22_SPEC = importlib.util.spec_from_file_location(
    "w23_w22_test_helpers",
    ROOT / "tests" / "test_w22_independent_authority_return.py",
)
assert W22_SPEC and W22_SPEC.loader
w22 = importlib.util.module_from_spec(W22_SPEC)
W22_SPEC.loader.exec_module(w22)


def _private(name: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(SEEDS[name])


def _public(name: str) -> str:
    return base64.b64encode(
        _private(name).public_key().public_bytes_raw()
    ).decode()


def _fingerprint(public: str) -> str:
    return "sha256:" + hashlib.sha256(base64.b64decode(public)).hexdigest()


def _source(name: str) -> dict:
    value = {
        "schema": SOURCE_SCHEMA,
        "source_id": f"source.{name}",
        "authority_id": f"authority.{name}",
        "role": ROLE_NAMES[name],
        "governance_repository": "demeet2k/Athena",
        "source_digest": "",
    }
    value["source_digest"] = _digest(_addressed(value, "source_digest"))
    return value


def _revision(name: str, source: dict) -> dict:
    public = _public(name)
    digit = str(list(ROLE_NAMES).index(name) + 1)
    value = {
        "schema": REVISION_SCHEMA,
        "source_digest": source["source_digest"],
        "revision_id": f"revision.{name}.v1",
        "role": ROLE_NAMES[name],
        "repository": "demeet2k/Athena",
        "ref": f"refs/heads/authority-{name}",
        "commit": digit * 40,
        "tree": str((int(digit) + 1) % 10) * 40,
        "path": f".athena/authorities/{name}.json",
        "blob_digest": "sha256:" + digit * 64,
        "content_digest": "sha256:" + str((int(digit) + 2) % 10) * 64,
        "parent_revision_digest": None,
        "key_id": f"key.{name}.v1",
        "public_key_base64": public,
        "fingerprint": _fingerprint(public),
        "valid_from": "2026-07-27T00:00:00Z",
        "valid_until": "2027-07-27T00:00:00Z",
        "scope": {
            "operation": OPERATIONS[name],
            "repository": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/production",
            "environment": "kc144-production",
            "policy_digest": POLICY,
        },
        "revision_digest": "",
    }
    value["revision_digest"] = _digest(
        _addressed(value, "revision_digest")
    )
    return value


def _snapshot() -> tuple[dict, dict[str, dict], dict[str, dict]]:
    snapshot = json.loads(DATA.read_text())
    sources = {name: _source(name) for name in ROLE_NAMES}
    revisions = {
        name: _revision(name, sources[name]) for name in ROLE_NAMES
    }
    snapshot["authority_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["boundaries"]["production_authority_source_count"] = 6
    snapshot["boundaries"]["production_authority_revision_count"] = 6
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    return snapshot, sources, revisions


def _gate() -> FrozenPromotionExecutionHandoff:
    return FrozenPromotionExecutionHandoff.from_snapshot(
        _snapshot()[0],
        w22._gate(),
    )


def _w22_records() -> tuple[dict, dict]:
    commit_return = w22._commit_return()
    observation = w22._observation(commit_return)
    return commit_return, observation


def _custody() -> dict:
    return {
        "w22_head": W22_HEAD,
        "w22_tree": W22_TREE,
        "w22_sole_parent": W22_PARENT,
        "w22_contract_digest": W22_CONTRACT,
        "w22_receipt_id": W22_RECEIPT,
    }


def _target(image: str = PUBLISHED) -> dict:
    return {
        "runtime_repository": "demeet2k/athena-mcp-server",
        "runtime_head": W22_HEAD,
        "published_image_digest": image,
        "target_environment": "kc144-production",
        "target_ref": "refs/heads/production",
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


def _challenge(image: str = PUBLISHED) -> dict:
    _, sources, revisions = _snapshot()
    value = {
        "schema": CHALLENGE_SCHEMA,
        "custody": _custody(),
        "source_digest": sources["challenge"]["source_digest"],
        "revision_digest": revisions["challenge"]["revision_digest"],
        "challenge_id": "challenge.promotion.0001",
        "nonce": "nonce.challenge.0001",
        "target": _target(image),
        "issued_at": "2026-07-27T01:00:00Z",
        "expires_at": "2026-07-27T01:30:00Z",
        "policy_digest": POLICY,
        "signature": {"key_id": "key.challenge.v1", "value": ""},
        "challenge_digest": "",
    }
    return _sign(value, "challenge", "challenge_digest")


def _publication(challenge: dict | None = None) -> dict:
    challenge = challenge or _challenge()
    _, sources, revisions = _snapshot()
    image = challenge["target"]["published_image_digest"]
    value = {
        "schema": PUBLICATION_SCHEMA,
        "source_digest": sources["publisher"]["source_digest"],
        "revision_digest": revisions["publisher"]["revision_digest"],
        "occurrence_id": "occurrence.publication.0001",
        "challenge_digest": challenge["challenge_digest"],
        "target": deepcopy(challenge["target"]),
        "registry": "ghcr.io",
        "immutable_reference": f"ghcr.io/demeet2k/athena-mcp@{image}",
        "manifest_digest": image,
        "published_at": "2026-07-27T01:05:00Z",
        "signature": {"key_id": "key.publisher.v1", "value": ""},
        "proof_digest": "",
    }
    return _sign(value, "publisher", "proof_digest")


def _observation(
    challenge: dict | None = None, publication: dict | None = None
) -> dict:
    challenge = challenge or _challenge()
    publication = publication or _publication(challenge)
    _, sources, revisions = _snapshot()
    value = {
        "schema": OBSERVATION_SCHEMA,
        "source_digest": sources["observer"]["source_digest"],
        "revision_digest": revisions["observer"]["revision_digest"],
        "occurrence_id": "occurrence.observation.0001",
        "challenge_digest": challenge["challenge_digest"],
        "publication_proof_digest": publication["proof_digest"],
        "registry": publication["registry"],
        "immutable_reference": publication["immutable_reference"],
        "manifest_digest": publication["manifest_digest"],
        "registry_response_digest": REGISTRY_RESPONSE,
        "observed_at": "2026-07-27T01:06:00Z",
        "signature": {"key_id": "key.observer.v1", "value": ""},
        "observation_digest": "",
    }
    return _sign(value, "observer", "observation_digest")


def _decision(
    name: str,
    challenge: dict | None = None,
    publication: dict | None = None,
    observation: dict | None = None,
    decision: str = "AUTHORIZE_PROMOTION",
) -> dict:
    challenge = challenge or _challenge()
    publication = publication or _publication(challenge)
    observation = observation or _observation(challenge, publication)
    w22_commit_return, w22_git_observation = _w22_records()
    _, sources, revisions = _snapshot()
    value = {
        "schema": DECISION_SCHEMA,
        "source_digest": sources[name]["source_digest"],
        "revision_digest": revisions[name]["revision_digest"],
        "occurrence_id": f"occurrence.{name}.0001",
        "challenge_digest": challenge["challenge_digest"],
        "publication_proof_digest": publication["proof_digest"],
        "publication_observation_digest": observation["observation_digest"],
        "w22_commit_return_digest": w22_commit_return["return_digest"],
        "w22_git_observation_digest": w22_git_observation[
            "observation_digest"
        ],
        "w22_commit_return": w22_commit_return,
        "w22_git_observation": w22_git_observation,
        "target": deepcopy(challenge["target"]),
        "decision": decision,
        "decided_at": (
            "2026-07-27T01:07:00Z"
            if name == "policy_a"
            else "2026-07-27T01:08:00Z"
        ),
        "reason_code": "published_target_and_policy_accepted",
        "signature": {"key_id": f"key.{name}.v1", "value": ""},
        "decision_digest": "",
    }
    return _sign(value, name, "decision_digest")


def _records(
    decision_a: str = "AUTHORIZE_PROMOTION",
    decision_b: str = "AUTHORIZE_PROMOTION",
) -> tuple[dict, dict, dict, dict, dict]:
    challenge = _challenge()
    publication = _publication(challenge)
    observation = _observation(challenge, publication)
    policy_a = _decision(
        "policy_a", challenge, publication, observation, decision_a
    )
    policy_b = _decision(
        "policy_b", challenge, publication, observation, decision_b
    )
    return challenge, publication, observation, policy_a, policy_b


def _quorum(
    gate: FrozenPromotionExecutionHandoff | None = None,
    decision_a: str = "AUTHORIZE_PROMOTION",
    decision_b: str = "AUTHORIZE_PROMOTION",
) -> dict:
    gate = gate or _gate()
    records = _records(decision_a, decision_b)
    return gate.evaluate_quorum(*(json.dumps(value) for value in records))


def _authorization(records: tuple[dict, dict, dict, dict, dict]) -> dict:
    challenge, publication, observation, policy_a, policy_b = records
    gate = _gate()
    _, sources, revisions = _snapshot()
    quorum = gate.evaluate_quorum(
        *(json.dumps(value) for value in records)
    )
    value = {
        "schema": AUTHORIZATION_SCHEMA,
        "custody": _custody(),
        "source_digest": sources["execution"]["source_digest"],
        "revision_digest": revisions["execution"]["revision_digest"],
        "occurrence_id": "occurrence.execution.authorization.0001",
        "challenge_digest": challenge["challenge_digest"],
        "publication_proof_digest": publication["proof_digest"],
        "publication_observation_digest": observation["observation_digest"],
        "policy_a_decision_digest": policy_a["decision_digest"],
        "policy_b_decision_digest": policy_b["decision_digest"],
        "quorum_certificate_digest": quorum["quorum_certificate"][
            "certificate_digest"
        ],
        "target": deepcopy(challenge["target"]),
        "authorized_at": "2026-07-27T01:09:00Z",
        "execution_expires_at": "2026-07-27T01:20:00Z",
        "nonce": "nonce.execution.0001",
        "constraints": {
            "published_artifact_required": True,
            "two_policy_authorities_required": True,
            "hold_dominates": True,
            "freshness_required": True,
            "execution_receipt_required": True,
            "runtime_can_execute": False,
        },
        "signature": {"key_id": "key.execution.v1", "value": ""},
        "authorization_digest": "",
    }
    return _sign(value, "execution", "authorization_digest")


def _closure(
    gate: FrozenPromotionExecutionHandoff | None = None,
) -> dict:
    gate = gate or _gate()
    records = _records()
    authorization = _authorization(records)
    return gate.inspect_execution_authorization(
        *(json.dumps(value) for value in records),
        json.dumps(authorization),
    )


def test_production_w23_is_empty_and_unpublished_fail_closed() -> None:
    status = FrozenPromotionExecutionHandoff.load().status()
    assert status["authority_source_count"] == 0
    assert status["authority_revision_count"] == 0
    assert status["w22_image_published"] is False
    assert status["promotion_hold_active"] is True
    assert status["execution_authorized"] is False
    assert status["execution_observed"] is False


def test_production_status_pins_non_authoritative_w22_control_admission() -> None:
    status = FrozenPromotionExecutionHandoff.load().status()
    assert status["w22_control_head"] == (
        "754e90aa67714e3ae3cd7ad107ffd8b3aed40b67"
    )
    assert status["w22_control_receipt_id"] == (
        "w22-control-admission:sha256:"
        "a477c25821788c72c843e539c51624e781d6c79a449f6aa8c28b65cb4dbb7290"
    )
    assert status["w22_control_protocol_admitted"] is True
    assert status["w22_control_receipt_grants_production_authority"] is False


def test_complete_six_role_path_authorizes_but_never_executes() -> None:
    result = _closure()
    assert result["status"].startswith(
        "PASS_W23_COORDINATE_SPECIFIC_EXECUTION_AUTHORIZATION"
    )
    assert result["promotion_quorum_satisfied"] is True
    assert result["execution_authorized"] is True
    assert result["execution_observed"] is False
    assert result["promotion_executed"] is False
    assert result["deployment_claimed"] is False


@pytest.mark.parametrize(
    ("decision_a", "decision_b"),
    [
        ("HOLD_PROMOTION", "AUTHORIZE_PROMOTION"),
        ("AUTHORIZE_PROMOTION", "HOLD_PROMOTION"),
        ("HOLD_PROMOTION", "HOLD_PROMOTION"),
    ],
)
def test_hold_dominates_any_two_policy_combination(
    decision_a: str, decision_b: str
) -> None:
    result = _quorum(decision_a=decision_a, decision_b=decision_b)
    assert result["promotion_quorum_satisfied"] is False
    assert result["promotion_hold_active"] is True
    assert result["execution_authorized"] is False


def test_one_policy_decision_is_not_quorum() -> None:
    challenge, publication, observation, policy_a, _ = _records()
    result = _gate().inspect_policy_decision(
        json.dumps(challenge),
        json.dumps(publication),
        json.dumps(observation),
        json.dumps(policy_a),
        "PROMOTION_POLICY_A",
    )
    assert result["promotion_policy_a_verified"] is True
    assert result["promotion_quorum_satisfied"] is False
    assert result["execution_authorized"] is False


def test_workflow_local_w22_image_is_explicitly_unpublished() -> None:
    challenge = _challenge(W22_LOCAL_IMAGE)
    result = _gate().inspect_freshness_challenge(json.dumps(challenge))
    assert result["status"] == "HOLD_W23_FRESHNESS_CHALLENGE_REJECTED"
    assert "unpublished" in result["error"]


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("target_ref", "refs/heads/main"),
        ("target_environment", "staging"),
    ],
)
def test_target_requires_exact_production_scope(
    field: str, replacement: str
) -> None:
    challenge = _challenge()
    challenge["target"][field] = replacement
    challenge = _sign(challenge, "challenge", "challenge_digest")
    result = _gate().inspect_freshness_challenge(json.dumps(challenge))
    assert result["freshness_challenge_verified"] is False
    assert "exact W22 runtime" in result["error"]


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("w22_head", "1" * 40),
        ("w22_tree", "2" * 40),
        ("w22_sole_parent", "3" * 40),
        ("w22_contract_digest", "sha256:" + "4" * 64),
    ],
)
def test_w22_custody_substitution_rejected(
    field: str, replacement: str
) -> None:
    challenge = _challenge()
    challenge["custody"][field] = replacement
    challenge = _sign(challenge, "challenge", "challenge_digest")
    result = _gate().inspect_freshness_challenge(json.dumps(challenge))
    assert result["freshness_challenge_verified"] is False


def test_freshness_window_over_one_hour_rejected() -> None:
    challenge = _challenge()
    challenge["expires_at"] = "2026-07-27T02:00:01Z"
    challenge = _sign(challenge, "challenge", "challenge_digest")
    result = _gate().inspect_freshness_challenge(json.dumps(challenge))
    assert "3600 seconds" in result["error"]


def test_publication_requires_immutable_registry_reference() -> None:
    challenge = _challenge()
    publication = _publication(challenge)
    publication["immutable_reference"] = "ghcr.io/demeet2k/athena-mcp:latest"
    publication = _sign(publication, "publisher", "proof_digest")
    result = _gate().inspect_publication_proof(
        json.dumps(challenge), json.dumps(publication)
    )
    assert result["artifact_publication_proved"] is False


def test_publication_rejects_unrelated_registry_namespace() -> None:
    challenge = _challenge()
    publication = _publication(challenge)
    publication["immutable_reference"] = (
        "attacker.invalid/repository@" + publication["manifest_digest"]
    )
    publication = _sign(publication, "publisher", "proof_digest")
    result = _gate().inspect_publication_proof(
        json.dumps(challenge), json.dumps(publication)
    )
    assert result["artifact_publication_proved"] is False
    assert "immutable registry reference" in result["error"]


@pytest.mark.parametrize(
    "field",
    [
        "challenge_digest",
        "publication_proof_digest",
        "manifest_digest",
        "registry_response_digest",
    ],
)
def test_publication_observation_tampering_rejected(field: str) -> None:
    challenge, publication, observation, _, _ = _records()
    observation[field] = "sha256:" + "8" * 64
    result = _gate().inspect_publication_observation(
        json.dumps(challenge),
        json.dumps(publication),
        json.dumps(observation),
    )
    assert result["artifact_publication_observed"] is False


@pytest.mark.parametrize(
    "field",
    [
        "challenge_digest",
        "publication_proof_digest",
        "publication_observation_digest",
        "w22_commit_return_digest",
        "w22_git_observation_digest",
        "decision_digest",
    ],
)
def test_policy_decision_tampering_rejected(field: str) -> None:
    challenge, publication, observation, policy_a, _ = _records()
    policy_a[field] = "sha256:" + "8" * 64
    result = _gate().inspect_policy_decision(
        json.dumps(challenge),
        json.dumps(publication),
        json.dumps(observation),
        json.dumps(policy_a),
        "PROMOTION_POLICY_A",
    )
    assert result["promotion_policy_a_verified"] is False


def test_policy_decision_after_challenge_expiry_rejected() -> None:
    challenge, publication, observation, policy_a, _ = _records()
    policy_a["decided_at"] = "2026-07-27T01:31:00Z"
    policy_a = _sign(policy_a, "policy_a", "decision_digest")
    result = _gate().inspect_policy_decision(
        json.dumps(challenge),
        json.dumps(publication),
        json.dumps(observation),
        json.dumps(policy_a),
        "PROMOTION_POLICY_A",
    )
    assert "freshness window" in result["error"]


def test_policy_quorum_cannot_agree_on_fabricated_w22_digests() -> None:
    challenge, publication, observation, policy_a, policy_b = _records()
    for name, decision in (("policy_a", policy_a), ("policy_b", policy_b)):
        decision["w22_commit_return_digest"] = "sha256:" + "1" * 64
        decision["w22_git_observation_digest"] = "sha256:" + "2" * 64
        _sign(decision, name, "decision_digest")
    result = _gate().evaluate_quorum(
        *(
            json.dumps(value)
            for value in (
                challenge,
                publication,
                observation,
                policy_a,
                policy_b,
            )
        )
    )
    assert result["promotion_quorum_satisfied"] is False
    assert "verified W22 return evidence" in result["error"]


def test_policy_quorum_rejects_tampered_embedded_w22_return() -> None:
    challenge, publication, observation, policy_a, policy_b = _records()
    for name, decision in (("policy_a", policy_a), ("policy_b", policy_b)):
        decision["w22_commit_return"]["transaction_digest"] = (
            "sha256:" + "8" * 64
        )
        _sign(decision, name, "decision_digest")
    result = _gate().evaluate_quorum(
        *(
            json.dumps(value)
            for value in (
                challenge,
                publication,
                observation,
                policy_a,
                policy_b,
            )
        )
    )
    assert result["promotion_quorum_satisfied"] is False
    assert "W22 signed return evidence" in result["error"]


@pytest.mark.parametrize(
    "mutation",
    ["unknown", "boundary", "contract"],
)
def test_readdressed_snapshot_cannot_mutate_frozen_policy(mutation: str) -> None:
    snapshot, _, _ = _snapshot()
    if mutation == "unknown":
        snapshot["unexpected_execution_claim"] = True
    elif mutation == "boundary":
        snapshot["boundaries"]["execution_authorized"] = True
    else:
        snapshot["execution_contract"]["runtime_can_authorize_execution"] = True
    snapshot["contract_digest"] = _digest(
        {
            key: value
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
    )
    with pytest.raises(PromotionExecutionHandoffError):
        FrozenPromotionExecutionHandoff.from_snapshot(snapshot, w22._gate())


def test_authority_revision_cannot_cross_governance_repository() -> None:
    snapshot, _, revisions = _snapshot()
    revisions["challenge"]["repository"] = "attacker/governance"
    revisions["challenge"]["revision_digest"] = _digest(
        _addressed(revisions["challenge"], "revision_digest")
    )
    snapshot["authority_registry"]["revisions"] = list(revisions.values())
    snapshot["contract_digest"] = _digest(
        {
            key: value
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
    )
    with pytest.raises(PromotionExecutionHandoffError):
        FrozenPromotionExecutionHandoff.from_snapshot(snapshot, w22._gate())


@pytest.mark.parametrize(
    "field",
    ["authority_id", "key_id", "public_key_base64", "fingerprint"],
)
def test_all_six_roles_require_disjoint_identity_and_keys(field: str) -> None:
    snapshot, sources, revisions = _snapshot()
    if field == "authority_id":
        sources["policy_b"][field] = sources["policy_a"][field]
        sources["policy_b"]["source_digest"] = _digest(
            _addressed(sources["policy_b"], "source_digest")
        )
        revisions["policy_b"]["source_digest"] = sources["policy_b"][
            "source_digest"
        ]
    else:
        revisions["policy_b"][field] = revisions["policy_a"][field]
        if field == "public_key_base64":
            revisions["policy_b"]["fingerprint"] = revisions["policy_a"][
                "fingerprint"
            ]
    revisions["policy_b"]["revision_digest"] = _digest(
        _addressed(revisions["policy_b"], "revision_digest")
    )
    snapshot["authority_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(PromotionExecutionHandoffError):
        FrozenPromotionExecutionHandoff.from_snapshot(snapshot, w22._gate())


def test_caller_supplied_unpinned_execution_key_rejected() -> None:
    records = _records()
    authorization = _authorization(records)
    authorization["revision_digest"] = "sha256:" + "8" * 64
    authorization = _sign(
        authorization, "execution", "authorization_digest"
    )
    result = _gate().inspect_execution_authorization(
        *(json.dumps(value) for value in records),
        json.dumps(authorization),
    )
    assert result["execution_authorized"] is False
    assert "not pinned" in result["error"]


def test_execution_expiry_cannot_outlive_challenge() -> None:
    records = _records()
    authorization = _authorization(records)
    authorization["execution_expires_at"] = "2026-07-27T01:31:00Z"
    authorization = _sign(
        authorization, "execution", "authorization_digest"
    )
    result = _gate().inspect_execution_authorization(
        *(json.dumps(value) for value in records),
        json.dumps(authorization),
    )
    assert result["execution_authorized"] is False


def test_execution_constraints_cannot_be_weakened() -> None:
    records = _records()
    authorization = _authorization(records)
    authorization["constraints"]["execution_receipt_required"] = False
    authorization = _sign(
        authorization, "execution", "authorization_digest"
    )
    result = _gate().inspect_execution_authorization(
        *(json.dumps(value) for value in records),
        json.dumps(authorization),
    )
    assert result["execution_authorized"] is False
    assert "weakened" in result["error"]


def test_unsigned_handoff_compilation_never_issues_signature() -> None:
    records = _records()
    _, sources, revisions = _snapshot()
    result = _gate().compile_execution_handoff(
        *(json.dumps(value) for value in records),
        sources["execution"]["source_digest"],
        revisions["execution"]["revision_digest"],
        "2026-07-27T01:09:00Z",
        "2026-07-27T01:20:00Z",
        "nonce.execution.0001",
    )
    assert result["execution_handoff_compiled"] is True
    assert result["execution_authorized"] is False
    assert result["runtime_issued_authority_signature"] is False
    assert result["handoff_template"]["signature"]["value"] == "REQUIRED"


@pytest.mark.parametrize(
    ("authorized_at", "execution_expires_at"),
    [
        ("2026-07-27T00:59:00Z", "2026-07-27T01:10:00Z"),
        ("2026-07-27T01:07:30Z", "2026-07-27T01:20:00Z"),
        ("2027-07-28T00:00:00Z", "2027-07-28T00:01:00Z"),
    ],
)
def test_handoff_compiler_rejects_invalid_authority_chronology(
    authorized_at: str,
    execution_expires_at: str,
) -> None:
    records = _records()
    _, sources, revisions = _snapshot()
    result = _gate().compile_execution_handoff(
        *(json.dumps(value) for value in records),
        sources["execution"]["source_digest"],
        revisions["execution"]["revision_digest"],
        authorized_at,
        execution_expires_at,
        "nonce.execution.0001",
    )
    assert result["execution_handoff_compiled"] is False
    assert "window predates policy" in result["error"]


def test_duplicate_json_members_rejected() -> None:
    challenge = json.dumps(_challenge()).replace(
        '"challenge_id":',
        '"challenge_id":"shadow","challenge_id":',
        1,
    )
    result = _gate().inspect_freshness_challenge(challenge)
    assert "duplicate JSON member" in result["error"]


def test_hardening_receipt_is_content_addressed_and_nonclaiming() -> None:
    receipt = json.loads(HARDENING_RECEIPT.read_text(encoding="utf-8"))
    expected = "w23-execution-handoff-hardening:" + _digest(
        {
            key: value
            for key, value in receipt.items()
            if key != "receipt_id"
        }
    )
    assert receipt["receipt_id"] == expected
    assert receipt["lineage"]["w23_predecessor_head"] == (
        "3061598cd050aa6b8ad8b647e86c2295acb54228"
    )
    assert receipt["contract"]["contract_digest"] == (
        "sha256:3630dd1c67a19865c5c2e24b757f93e8c7a070439a329e70f22f281a72f53613"
    )
    assert receipt["contract"]["production_authority_source_count"] == 0
    assert receipt["contract"]["production_authority_revision_count"] == 0
    assert receipt["boundaries"]["promotion_hold_active"] is True
    assert all(
        receipt["boundaries"][field] is False
        for field in (
            "production_authority_source_pinned",
            "production_authority_revision_pinned",
            "freshness_challenge_returned",
            "artifact_publication_proved",
            "artifact_publication_observed",
            "w22_signed_return_evidence_verified",
            "promotion_quorum_satisfied",
            "execution_handoff_compiled",
            "execution_authorized",
            "execution_observed",
            "promotion_executed",
            "workflow_dispatched",
            "endpoint_contacted",
            "deployment_claimed",
            "merge_claimed",
            "promotion_claimed",
        )
    )


def test_w23_workflow_remains_manual_read_only_and_secret_free() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "\npush:" not in workflow
    assert "\npull_request:" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "secrets." not in workflow
    assert "environment:" not in workflow
    assert "deploy" not in workflow.lower()
    assert "github-token" not in workflow.lower()


def test_registration_has_twelve_tools_and_resource() -> None:
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
    register_promotion_execution_handoff(mcp)
    assert len(mcp.tools) == 12
    assert mcp.resources == ["athena://w23-promotion-execution-handoff"]
