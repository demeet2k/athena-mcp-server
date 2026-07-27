import base64
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from MCP.crystal_108d.execution_deployment_rollback_readback import (
    DATA_PATH,
    DEPLOYMENT_SCHEMA,
    EXECUTION_SCHEMA,
    HEALTH_SCHEMA,
    PHASE,
    PROMOTION_SCHEMA,
    REVISION_SCHEMA,
    ROLLBACK_AUTH_SCHEMA,
    ROLLBACK_OBSERVATION_SCHEMA,
    ROLLBACK_OCCURRENCE_SCHEMA,
    ROLES,
    SCHEMA,
    SOURCE_SCHEMA,
    ExecutionDeploymentRollbackError,
    FrozenExecutionDeploymentRollbackReadback,
    register_execution_deployment_rollback_readback,
)
from MCP.crystal_108d.independent_authority_return import (
    _addressed,
    _digest,
    _signed,
)


ROOT = Path(__file__).resolve().parents[1]
W23_TEST_PATH = ROOT / "tests" / "test_w23_promotion_execution_handoff.py"
SPEC = importlib.util.spec_from_file_location("w23_test_helpers", W23_TEST_PATH)
W23 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(W23)

PREVIOUS = "sha256:" + "7" * 64
DISPATCH = "sha256:" + "6" * 64
PROVIDER = "sha256:" + "5" * 64
ENDPOINT = "sha256:" + "4" * 64
HEALTH_ROOT = "sha256:" + "3" * 64
ROLLBACK_PLAN = "sha256:" + "2" * 64


def _private(name: str) -> Ed25519PrivateKey:
    seed = hashlib.sha256(("w24-" + name).encode()).digest()
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
        "key_id": f"key.w24.{name}.v1",
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


def _w23():
    records = W23._records()
    authorization = W23._authorization(records)
    gate = W23._gate()
    return gate, records, authorization


def _snapshot(w23_gate=None):
    if w23_gate is None:
        w23_gate, _, _ = _w23()
    snapshot = json.loads(DATA_PATH.read_text())
    sources = {}
    revisions = {}
    for role in ROLES:
        name = role.lower()
        source = {
            "schema": SOURCE_SCHEMA,
            "source_id": f"source.w24.{name}",
            "authority_id": f"authority.w24.{name}",
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
            "revision_id": f"revision.w24.{name}.v1",
            "role": role,
            "repository": "demeet2k/Athena",
            "ref": "refs/heads/authority/w24",
            "commit": hashlib.sha1(("commit-" + name).encode()).hexdigest(),
            "tree": hashlib.sha1(("tree-" + name).encode()).hexdigest(),
            "path": f".athena/authority/w24/{name}.json",
            "blob_digest": "sha256:" + hashlib.sha256(
                ("blob-" + name).encode()
            ).hexdigest(),
            "content_digest": "sha256:" + hashlib.sha256(
                ("content-" + name).encode()
            ).hexdigest(),
            "parent_revision_digest": None,
            "key_id": f"key.w24.{name}.v1",
            "public_key_base64": _public(name),
            "fingerprint": _fingerprint(name),
            "valid_from": "2026-07-27T00:00:00Z",
            "valid_until": "2026-07-28T00:00:00Z",
            "scope": {
                "operation": ROLES[role],
                "repository": "demeet2k/athena-mcp-server",
                "ref": "refs/heads/production",
                "environment": "kc144-production",
                "policy_digest": W23.POLICY,
            },
            "revision_digest": "",
        }
        revision["revision_digest"] = _digest(
            _addressed(revision, "revision_digest")
        )
        sources[name] = source
        revisions[name] = revision
    snapshot["authority_registry"] = {
        "sources": list(sources.values()),
        "revisions": list(revisions.values()),
    }
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    return snapshot, sources, revisions


def _gate():
    w23_gate, _, _ = _w23()
    snapshot, _, _ = _snapshot(w23_gate)
    return FrozenExecutionDeploymentRollbackReadback.from_snapshot(
        snapshot, w23_gate
    )


def _coordinates():
    w23_gate, w23_records, w23_authorization = _w23()
    snapshot, sources, revisions = _snapshot(w23_gate)
    gate = FrozenExecutionDeploymentRollbackReadback.from_snapshot(
        snapshot, w23_gate
    )
    challenge, publication, observation, policy_a, policy_b = w23_records
    target = deepcopy(challenge["target"])

    def coordinate(role):
        name = role.lower()
        return (
            sources[name]["source_digest"],
            revisions[name]["revision_digest"],
        )

    execution_source, execution_revision = coordinate("EXECUTION_OPERATOR")
    execution = {
        "schema": EXECUTION_SCHEMA,
        "source_digest": execution_source,
        "revision_digest": execution_revision,
        "occurrence_id": "occurrence.w24.execution.0001",
        "w23_authorization_digest": w23_authorization[
            "authorization_digest"
        ],
        "target": target,
        "provider_execution_id": "provider.execution.0001",
        "dispatch_digest": DISPATCH,
        "started_at": "2026-07-27T01:10:00Z",
        "completed_at": "2026-07-27T01:11:00Z",
        "exit_status": "SUCCESS",
        "signature": {},
        "execution_digest": "",
    }
    _sign(execution, "execution_operator", "execution_digest")

    promotion_source, promotion_revision = coordinate("PROMOTION_OBSERVER")
    promotion = {
        "schema": PROMOTION_SCHEMA,
        "source_digest": promotion_source,
        "revision_digest": promotion_revision,
        "occurrence_id": "occurrence.w24.promotion.0001",
        "execution_digest": execution["execution_digest"],
        "target": target,
        "provider_state_digest": PROVIDER,
        "observed_state": "PROMOTED",
        "observed_at": "2026-07-27T01:12:00Z",
        "signature": {},
        "promotion_observation_digest": "",
    }
    _sign(
        promotion,
        "promotion_observer",
        "promotion_observation_digest",
    )

    deployment_source, deployment_revision = coordinate(
        "DEPLOYMENT_OBSERVER"
    )
    deployment = {
        "schema": DEPLOYMENT_SCHEMA,
        "source_digest": deployment_source,
        "revision_digest": deployment_revision,
        "occurrence_id": "occurrence.w24.deployment.0001",
        "execution_digest": execution["execution_digest"],
        "promotion_observation_digest": promotion[
            "promotion_observation_digest"
        ],
        "target": target,
        "deployment_id": "deployment.kc144.0001",
        "immutable_reference": (
            "ghcr.io/demeet2k/athena-mcp@"
            + target["published_image_digest"]
        ),
        "manifest_digest": target["published_image_digest"],
        "endpoint_uri_hash": ENDPOINT,
        "provider_readback_digest": PROVIDER,
        "deployed_at": "2026-07-27T01:12:00Z",
        "observed_at": "2026-07-27T01:13:00Z",
        "signature": {},
        "deployment_readback_digest": "",
    }
    _sign(
        deployment,
        "deployment_observer",
        "deployment_readback_digest",
    )

    health_source, health_revision = coordinate("HEALTH_OBSERVER")
    health = {
        "schema": HEALTH_SCHEMA,
        "source_digest": health_source,
        "revision_digest": health_revision,
        "occurrence_id": "occurrence.w24.health.0001",
        "deployment_readback_digest": deployment[
            "deployment_readback_digest"
        ],
        "target": target,
        "sample_count": 4,
        "interval_seconds": 20,
        "span_seconds": 60,
        "first_observed_at": "2026-07-27T01:13:00Z",
        "last_observed_at": "2026-07-27T01:14:00Z",
        "health_root_digest": HEALTH_ROOT,
        "health_state": "HEALTHY",
        "signature": {},
        "health_window_digest": "",
    }
    _sign(health, "health_observer", "health_window_digest")

    auth_source, auth_revision = coordinate("ROLLBACK_AUTHORIZER")
    rollback_authorization = {
        "schema": ROLLBACK_AUTH_SCHEMA,
        "source_digest": auth_source,
        "revision_digest": auth_revision,
        "occurrence_id": "occurrence.w24.rollback.authorization.0001",
        "deployment_readback_digest": deployment[
            "deployment_readback_digest"
        ],
        "health_window_digest": health["health_window_digest"],
        "target": target,
        "previous_safe_image_digest": PREVIOUS,
        "rollback_plan_digest": ROLLBACK_PLAN,
        "rollback_mode": "DRILL",
        "authorized_at": "2026-07-27T01:14:00Z",
        "expires_at": "2026-07-27T01:30:00Z",
        "signature": {},
        "rollback_authorization_digest": "",
    }
    _sign(
        rollback_authorization,
        "rollback_authorizer",
        "rollback_authorization_digest",
    )

    occurrence_source, occurrence_revision = coordinate("ROLLBACK_OPERATOR")
    rollback_occurrence = {
        "schema": ROLLBACK_OCCURRENCE_SCHEMA,
        "source_digest": occurrence_source,
        "revision_digest": occurrence_revision,
        "occurrence_id": "occurrence.w24.rollback.0001",
        "rollback_authorization_digest": rollback_authorization[
            "rollback_authorization_digest"
        ],
        "deployment_readback_digest": deployment[
            "deployment_readback_digest"
        ],
        "target": target,
        "from_image_digest": target["published_image_digest"],
        "to_image_digest": PREVIOUS,
        "provider_execution_id": "provider.rollback.0001",
        "started_at": "2026-07-27T01:15:00Z",
        "completed_at": "2026-07-27T01:16:00Z",
        "exit_status": "SUCCESS",
        "signature": {},
        "rollback_occurrence_digest": "",
    }
    _sign(
        rollback_occurrence,
        "rollback_operator",
        "rollback_occurrence_digest",
    )

    observer_source, observer_revision = coordinate("ROLLBACK_OBSERVER")
    rollback_observation = {
        "schema": ROLLBACK_OBSERVATION_SCHEMA,
        "source_digest": observer_source,
        "revision_digest": observer_revision,
        "occurrence_id": "occurrence.w24.rollback.observation.0001",
        "rollback_occurrence_digest": rollback_occurrence[
            "rollback_occurrence_digest"
        ],
        "deployment_readback_digest": deployment[
            "deployment_readback_digest"
        ],
        "target": target,
        "observed_image_digest": PREVIOUS,
        "provider_state_digest": PROVIDER,
        "observed_state": "ROLLED_BACK",
        "observed_at": "2026-07-27T01:17:00Z",
        "signature": {},
        "rollback_observation_digest": "",
    }
    _sign(
        rollback_observation,
        "rollback_observer",
        "rollback_observation_digest",
    )
    records = (
        challenge,
        publication,
        observation,
        policy_a,
        policy_b,
        w23_authorization,
        execution,
        promotion,
        deployment,
        health,
        rollback_authorization,
        rollback_occurrence,
        rollback_observation,
    )
    return gate, records


def _closure(gate=None, records=None):
    if gate is None or records is None:
        gate, records = _coordinates()
    return gate.evaluate_closure(*(json.dumps(value) for value in records))


def _resign(records, index, name, digest_field):
    values = list(deepcopy(records))
    _sign(values[index], name, digest_field)
    return tuple(values)


def test_production_w24_is_empty_and_fail_closed():
    status = FrozenExecutionDeploymentRollbackReadback.load().status()
    assert status["authority_source_count"] == 0
    assert status["authority_revision_count"] == 0
    assert status["w23_image_published"] is False
    assert status["execution_occurrence_verified"] is False
    assert status["rollback_observation_verified"] is False


def test_complete_thirteen_role_path_verifies_without_side_effects():
    result = _closure()
    assert result["status"].startswith(
        "PASS_W24_EXECUTION_DEPLOYMENT_HEALTH_AND_ROLLBACK"
    )
    for field in (
        "w23_execution_authorization_verified",
        "execution_occurrence_verified",
        "promotion_observed",
        "deployment_readback_verified",
        "health_window_verified",
        "rollback_authorization_verified",
        "rollback_occurrence_verified",
        "rollback_observation_verified",
    ):
        assert result[field] is True
    assert result["workflow_dispatched"] is False
    assert result["endpoint_contacted"] is False
    assert result["deployment_claimed"] is False
    assert result["promotion_claimed"] is False


def test_w23_authorization_is_required():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[5]["authorization_digest"] = "sha256:" + "0" * 64
    result = _closure(gate, tuple(values))
    assert result["status"] == "HOLD_W24_RETURN_CLOSURE_REJECTED"
    assert result["w23_execution_authorization_verified"] is False


def test_execution_after_w23_expiry_rejected():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[6]["started_at"] = "2026-07-27T01:21:00Z"
    values[6]["completed_at"] = "2026-07-27T01:22:00Z"
    values = _resign(
        values, 6, "execution_operator", "execution_digest"
    )
    result = _closure(gate, values)
    assert "outside W23 authorization window" in result["error"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_count", 2),
        ("interval_seconds", 19),
        ("span_seconds", 39),
    ],
)
def test_health_minimum_geometry_enforced(field, value):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[9][field] = value
    values = _resign(values, 9, "health_observer", "health_window_digest")
    result = _closure(gate, values)
    assert "health" in result["error"]


def test_rollback_target_must_differ_from_deployed_image():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[10]["previous_safe_image_digest"] = values[0]["target"][
        "published_image_digest"
    ]
    values = _resign(
        values,
        10,
        "rollback_authorizer",
        "rollback_authorization_digest",
    )
    result = _closure(gate, values)
    assert "rollback authorization bindings invalid" in result["error"]


def test_rollback_observation_must_read_previous_safe_image():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[12]["observed_image_digest"] = "sha256:" + "8" * 64
    values = _resign(
        values,
        12,
        "rollback_observer",
        "rollback_observation_digest",
    )
    result = _closure(gate, values)
    assert "rollback observation bindings invalid" in result["error"]


@pytest.mark.parametrize(
    ("index", "field", "value", "signer", "digest_field", "message"),
    [
        (
            7,
            "observed_state",
            "PENDING",
            "promotion_observer",
            "promotion_observation_digest",
            "promotion observation",
        ),
        (
            8,
            "manifest_digest",
            "sha256:" + "1" * 64,
            "deployment_observer",
            "deployment_readback_digest",
            "immutable target",
        ),
        (
            10,
            "rollback_mode",
            "UNSCOPED",
            "rollback_authorizer",
            "rollback_authorization_digest",
            "rollback authorization",
        ),
        (
            11,
            "exit_status",
            "FAILED",
            "rollback_operator",
            "rollback_occurrence_digest",
            "rollback occurrence",
        ),
        (
            12,
            "observed_state",
            "UNKNOWN",
            "rollback_observer",
            "rollback_observation_digest",
            "rollback observation",
        ),
    ],
)
def test_return_state_substitutions_rejected(
    index, field, value, signer, digest_field, message
):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[index][field] = value
    values = _resign(values, index, signer, digest_field)
    result = _closure(gate, values)
    assert message in result["error"]


def test_rollback_authorization_window_is_bounded():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[10]["expires_at"] = "2026-07-27T02:14:01Z"
    values = _resign(
        values,
        10,
        "rollback_authorizer",
        "rollback_authorization_digest",
    )
    result = _closure(gate, values)
    assert "freshness" in result["error"]


def test_rollback_readback_cannot_precede_occurrence():
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[12]["observed_at"] = "2026-07-27T01:15:00Z"
    values = _resign(
        values,
        12,
        "rollback_observer",
        "rollback_observation_digest",
    )
    result = _closure(gate, values)
    assert "rollback observation bindings invalid" in result["error"]


@pytest.mark.parametrize(
    ("index", "field"),
    [
        (6, "w23_authorization_digest"),
        (7, "execution_digest"),
        (8, "promotion_observation_digest"),
        (9, "deployment_readback_digest"),
        (10, "health_window_digest"),
        (11, "rollback_authorization_digest"),
        (12, "rollback_occurrence_digest"),
    ],
)
def test_every_return_edge_is_digest_bound(index, field):
    gate, records = _coordinates()
    values = list(deepcopy(records))
    values[index][field] = "sha256:" + "0" * 64
    result = _closure(gate, tuple(values))
    assert result["rollback_observation_verified"] is False


def test_w24_role_cannot_reuse_w23_key():
    w23_gate, _, _ = _w23()
    snapshot, _, revisions = _snapshot(w23_gate)
    w23_revision = next(iter(w23_gate.revisions.values()))
    target = revisions["execution_operator"]
    target["key_id"] = w23_revision["key_id"]
    target["revision_digest"] = _digest(
        _addressed(target, "revision_digest")
    )
    snapshot["authority_registry"]["revisions"] = list(revisions.values())
    snapshot["contract_digest"] = _digest(
        {key: value for key, value in snapshot.items() if key != "contract_digest"}
    )
    with pytest.raises(ExecutionDeploymentRollbackError):
        FrozenExecutionDeploymentRollbackReadback.from_snapshot(
            snapshot, w23_gate
        )


def test_duplicate_json_members_rejected():
    gate, records = _coordinates()
    serialized = [json.dumps(value) for value in records]
    serialized[6] = serialized[6].replace(
        '"occurrence_id":',
        '"occurrence_id":"shadow","occurrence_id":',
        1,
    )
    result = gate.evaluate_closure(*serialized)
    assert "duplicate JSON member" in result["error"]


def test_contract_digest_and_phase_are_exact():
    snapshot = json.loads(DATA_PATH.read_text())
    claimed = snapshot.pop("contract_digest")
    assert snapshot["schema"] == SCHEMA
    assert snapshot["phase"] == PHASE
    assert claimed == _digest(snapshot)


def test_registration_has_twelve_tools_and_resource():
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
    register_execution_deployment_rollback_readback(mcp)
    assert len(mcp.tools) == 12
    assert mcp.resources == [
        "athena://w24-execution-deployment-rollback-readback"
    ]
