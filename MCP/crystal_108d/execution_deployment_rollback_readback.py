"""KC144 W24 execution, deployment, health, and rollback return verifier.

The runtime verifies independently signed occurrences. It cannot dispatch,
contact an endpoint, execute, roll back, merge, deploy, or promote.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from .independent_authority_return import (
    _addressed,
    _commit,
    _digest,
    _exact,
    _identifier,
    _merge,
    _sha,
    _signature,
    _signed,
    _strict_loads,
    _text,
    _timestamp,
)
from .promotion_execution_handoff import (
    FrozenPromotionExecutionHandoff,
    _target,
    _verify,
)


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w24_execution_deployment_rollback_readback.json"
)
SCHEMA = "athena.xnav-w24-execution-deployment-rollback-readback/v1"
PHASE = "KC144.XNAV.W24"

SOURCE_SCHEMA = "athena.w24-return-authority-source/v1"
REVISION_SCHEMA = "athena.w24-return-authority-revision/v1"
EXECUTION_SCHEMA = "athena.w24-execution-occurrence/v1"
PROMOTION_SCHEMA = "athena.w24-promotion-observation/v1"
DEPLOYMENT_SCHEMA = "athena.w24-deployment-readback/v1"
HEALTH_SCHEMA = "athena.w24-health-window/v1"
ROLLBACK_AUTH_SCHEMA = "athena.w24-rollback-authorization/v1"
ROLLBACK_OCCURRENCE_SCHEMA = "athena.w24-rollback-occurrence/v1"
ROLLBACK_OBSERVATION_SCHEMA = "athena.w24-rollback-observation/v1"
CLOSURE_SCHEMA = "athena.w24-execution-deployment-rollback-closure/v1"

W23_HEAD = "3061598cd050aa6b8ad8b647e86c2295acb54228"
W23_TREE = "61ae40f869da0fe4979cadb054e46e67007833ae"
W23_PARENT = "aa8c382419fd093507f3059751a75dc14ffa8662"
W23_CONTRACT = (
    "sha256:1ec0f8749b47c68399ce6356db6523676f5c82a449f3420bb0cd9936871eabf4"
)
W23_RECEIPT = (
    "w23-execution-handoff:sha256:"
    "c06878df07733ad8459e46fc1bca02bf844ad78b7a72a2703430e984a4479ae5"
)
W23_LOCAL_IMAGE = (
    "sha256:8bca337faa3989f9ed94a2df0ceea29ea3b843e46e03359edfa3e9f36638f29a"
)

ROLES = {
    "EXECUTION_OPERATOR": "promotion.execute",
    "PROMOTION_OBSERVER": "promotion.observe",
    "DEPLOYMENT_OBSERVER": "deployment.observe",
    "HEALTH_OBSERVER": "deployment.health.observe",
    "ROLLBACK_AUTHORIZER": "rollback.authorize",
    "ROLLBACK_OPERATOR": "rollback.execute",
    "ROLLBACK_OBSERVER": "rollback.observe",
}

SOURCE_FIELDS = {
    "schema",
    "source_id",
    "authority_id",
    "role",
    "governance_repository",
    "source_digest",
}
REVISION_FIELDS = {
    "schema",
    "source_digest",
    "revision_id",
    "role",
    "repository",
    "ref",
    "commit",
    "tree",
    "path",
    "blob_digest",
    "content_digest",
    "parent_revision_digest",
    "key_id",
    "public_key_base64",
    "fingerprint",
    "valid_from",
    "valid_until",
    "scope",
    "revision_digest",
}
SCOPE_FIELDS = {
    "operation",
    "repository",
    "ref",
    "environment",
    "policy_digest",
}
EXECUTION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "w23_authorization_digest",
    "target",
    "provider_execution_id",
    "dispatch_digest",
    "started_at",
    "completed_at",
    "exit_status",
    "signature",
    "execution_digest",
}
PROMOTION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "execution_digest",
    "target",
    "provider_state_digest",
    "observed_state",
    "observed_at",
    "signature",
    "promotion_observation_digest",
}
DEPLOYMENT_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "execution_digest",
    "promotion_observation_digest",
    "target",
    "deployment_id",
    "immutable_reference",
    "manifest_digest",
    "endpoint_uri_hash",
    "provider_readback_digest",
    "deployed_at",
    "observed_at",
    "signature",
    "deployment_readback_digest",
}
HEALTH_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "deployment_readback_digest",
    "target",
    "sample_count",
    "interval_seconds",
    "span_seconds",
    "first_observed_at",
    "last_observed_at",
    "health_root_digest",
    "health_state",
    "signature",
    "health_window_digest",
}
ROLLBACK_AUTH_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "deployment_readback_digest",
    "health_window_digest",
    "target",
    "previous_safe_image_digest",
    "rollback_plan_digest",
    "rollback_mode",
    "authorized_at",
    "expires_at",
    "signature",
    "rollback_authorization_digest",
}
ROLLBACK_OCCURRENCE_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "rollback_authorization_digest",
    "deployment_readback_digest",
    "target",
    "from_image_digest",
    "to_image_digest",
    "provider_execution_id",
    "started_at",
    "completed_at",
    "exit_status",
    "signature",
    "rollback_occurrence_digest",
}
ROLLBACK_OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "rollback_occurrence_digest",
    "deployment_readback_digest",
    "target",
    "observed_image_digest",
    "provider_state_digest",
    "observed_state",
    "observed_at",
    "signature",
    "rollback_observation_digest",
}


class ExecutionDeploymentRollbackError(RuntimeError):
    """Frozen W24 contract or authority registry is invalid."""


def _fingerprint(public_key_base64: str) -> str:
    try:
        decoded = base64.b64decode(public_key_base64, validate=True)
    except ValueError as error:
        raise ValueError("public key must be canonical base64") from error
    if len(decoded) != 32 or base64.b64encode(decoded).decode() != public_key_base64:
        raise ValueError("public key must encode exactly 32 bytes")
    return "sha256:" + hashlib.sha256(decoded).hexdigest()


def _source(value: Any) -> dict[str, Any]:
    raw = _exact(value, SOURCE_FIELDS, "authority source")
    normalized = {
        "schema": _text(raw["schema"], "source.schema"),
        "source_id": _identifier(raw["source_id"], "source.source_id"),
        "authority_id": _identifier(raw["authority_id"], "source.authority_id"),
        "role": _text(raw["role"], "source.role"),
        "governance_repository": _text(
            raw["governance_repository"], "source.governance_repository"
        ),
        "source_digest": _sha(raw["source_digest"], "source.source_digest"),
    }
    if normalized["schema"] != SOURCE_SCHEMA or normalized["role"] not in ROLES:
        raise ValueError("authority source schema/role mismatch")
    if normalized["source_digest"] != _digest(
        _addressed(normalized, "source_digest")
    ):
        raise ValueError("authority source digest mismatch")
    return normalized


def _scope(value: Any) -> dict[str, Any]:
    raw = _exact(value, SCOPE_FIELDS, "authority scope")
    return {
        "operation": _identifier(raw["operation"], "scope.operation"),
        "repository": _text(raw["repository"], "scope.repository"),
        "ref": _text(raw["ref"], "scope.ref"),
        "environment": _identifier(raw["environment"], "scope.environment"),
        "policy_digest": _sha(raw["policy_digest"], "scope.policy_digest"),
    }


def _revision(value: Any) -> dict[str, Any]:
    raw = _exact(value, REVISION_FIELDS, "authority revision")
    normalized = {
        "schema": _text(raw["schema"], "revision.schema"),
        "source_digest": _sha(raw["source_digest"], "revision.source_digest"),
        "revision_id": _identifier(raw["revision_id"], "revision.revision_id"),
        "role": _text(raw["role"], "revision.role"),
        "repository": _text(raw["repository"], "revision.repository"),
        "ref": _text(raw["ref"], "revision.ref"),
        "commit": _commit(raw["commit"], "revision.commit"),
        "tree": _commit(raw["tree"], "revision.tree"),
        "path": _text(raw["path"], "revision.path"),
        "blob_digest": _sha(raw["blob_digest"], "revision.blob_digest"),
        "content_digest": _sha(raw["content_digest"], "revision.content_digest"),
        "parent_revision_digest": (
            None
            if raw["parent_revision_digest"] is None
            else _sha(
                raw["parent_revision_digest"], "revision.parent_revision_digest"
            )
        ),
        "key_id": _identifier(raw["key_id"], "revision.key_id"),
        "public_key_base64": _text(
            raw["public_key_base64"], "revision.public_key_base64", limit=64
        ),
        "fingerprint": _sha(raw["fingerprint"], "revision.fingerprint"),
        "valid_from": _text(raw["valid_from"], "revision.valid_from", limit=32),
        "valid_until": _text(raw["valid_until"], "revision.valid_until", limit=32),
        "scope": _scope(raw["scope"]),
        "revision_digest": _sha(
            raw["revision_digest"], "revision.revision_digest"
        ),
    }
    if normalized["schema"] != REVISION_SCHEMA or normalized["role"] not in ROLES:
        raise ValueError("authority revision schema/role mismatch")
    if normalized["scope"]["operation"] != ROLES[normalized["role"]]:
        raise ValueError("authority revision capability mismatch")
    if _fingerprint(normalized["public_key_base64"]) != normalized["fingerprint"]:
        raise ValueError("authority revision fingerprint mismatch")
    if _timestamp(normalized["valid_from"], "revision.valid_from") >= _timestamp(
        normalized["valid_until"], "revision.valid_until"
    ):
        raise ValueError("authority validity window is empty")
    if normalized["revision_digest"] != _digest(
        _addressed(normalized, "revision_digest")
    ):
        raise ValueError("authority revision digest mismatch")
    return normalized


def _record(
    text: str,
    *,
    fields: set[str],
    schema: str,
    digest_fields: tuple[str, ...],
    id_fields: tuple[str, ...],
    digest_field: str,
) -> dict[str, Any]:
    raw = deepcopy(_exact(_strict_loads(text), fields, schema))
    if raw["schema"] != schema:
        raise ValueError(f"{schema} mismatch")
    for field in digest_fields:
        raw[field] = _sha(raw[field], f"{schema}.{field}")
    for field in id_fields:
        raw[field] = _identifier(raw[field], f"{schema}.{field}")
    raw["source_digest"] = _sha(raw["source_digest"], "source_digest")
    raw["revision_digest"] = _sha(raw["revision_digest"], "revision_digest")
    raw["target"] = _target(raw["target"])
    raw["signature"] = _signature(raw["signature"], "signature")
    raw[digest_field] = _sha(raw[digest_field], digest_field)
    return raw


def _negative() -> dict[str, bool]:
    return {
        "runtime_mutated_registry": False,
        "runtime_issued_authority_signature": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "w23_execution_authorization_verified": False,
        "execution_occurrence_verified": False,
        "promotion_observed": False,
        "deployment_readback_verified": False,
        "health_window_verified": False,
        "rollback_authorization_verified": False,
        "rollback_occurrence_verified": False,
        "rollback_observation_verified": False,
        "merge_claimed": False,
        "deployment_claimed": False,
        "promotion_claimed": False,
    }


class FrozenExecutionDeploymentRollbackReadback:
    """Verify W24 returns against frozen W23 and W24 authority registries."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w23_gate: FrozenPromotionExecutionHandoff | None = None,
    ):
        self.snapshot = deepcopy(snapshot)
        self.w23_gate = w23_gate or FrozenPromotionExecutionHandoff.load()
        try:
            self._validate_snapshot()
        except (KeyError, LookupError, TypeError, ValueError) as error:
            raise ExecutionDeploymentRollbackError(str(error)) from error

    @classmethod
    def load(cls) -> "FrozenExecutionDeploymentRollbackReadback":
        return cls(_strict_loads(DATA_PATH.read_text(encoding="utf-8")))

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w23_gate: FrozenPromotionExecutionHandoff | None = None,
    ) -> "FrozenExecutionDeploymentRollbackReadback":
        return cls(snapshot, w23_gate=w23_gate)

    def _validate_snapshot(self) -> None:
        if self.snapshot.get("schema") != SCHEMA or self.snapshot.get("phase") != PHASE:
            raise ValueError("W24 schema/phase mismatch")
        predecessor = self.snapshot["predecessor"]
        exact = {
            "w23_head": W23_HEAD,
            "w23_tree": W23_TREE,
            "w23_sole_parent": W23_PARENT,
            "w23_contract_digest": W23_CONTRACT,
            "w23_receipt_id": W23_RECEIPT,
        }
        if {key: predecessor.get(key) for key in exact} != exact:
            raise ValueError("W23 predecessor mismatch")
        if predecessor.get("w23_image_published") is not False:
            raise ValueError("W23 workflow-local image must remain unpublished")
        control = self.snapshot["control_predecessor_observation"]
        if (
            control.get("head")
            != "7909f6fd5d9f58ecfde0f23e5f6fd41e9b731ce5"
            or control.get("grants_production_authority") is not False
        ):
            raise ValueError("control predecessor mismatch")
        registry = self.snapshot["authority_registry"]
        if set(registry) != {"sources", "revisions"}:
            raise ValueError("authority registry shape mismatch")
        self.sources: dict[str, dict[str, Any]] = {}
        self.revisions: dict[str, dict[str, Any]] = {}
        identities: dict[str, str] = {
            source["authority_id"]: source["role"]
            for source in self.w23_gate.sources.values()
        }
        aliases: dict[str, str] = {}
        for revision in self.w23_gate.revisions.values():
            aliases[f"key_id:{revision['key_id']}"] = revision["role"]
            aliases[
                f"public_key:{revision['public_key_base64']}"
            ] = revision["role"]
            aliases[f"fingerprint:{revision['fingerprint']}"] = revision["role"]
        source_tips: dict[str, str] = {}
        for raw in registry["sources"]:
            source = _source(raw)
            if source["source_digest"] in self.sources:
                raise ValueError("duplicate authority source")
            if source["authority_id"] in identities:
                raise ValueError("authority identity overlaps W23/W24 roles")
            identities[source["authority_id"]] = source["role"]
            self.sources[source["source_digest"]] = source
        for raw in registry["revisions"]:
            revision = _revision(raw)
            source = self.sources.get(revision["source_digest"])
            if source is None or source["role"] != revision["role"]:
                raise ValueError("revision source unpinned or role-mismatched")
            if revision["revision_digest"] in self.revisions:
                raise ValueError("duplicate authority revision")
            if revision["parent_revision_digest"] != source_tips.get(
                revision["source_digest"]
            ):
                raise ValueError("authority revision chain is not append-only")
            source_tips[revision["source_digest"]] = revision["revision_digest"]
            for label, value in (
                ("key_id", revision["key_id"]),
                ("public_key", revision["public_key_base64"]),
                ("fingerprint", revision["fingerprint"]),
            ):
                alias = f"{label}:{value}"
                if alias in aliases:
                    raise ValueError(f"{label} overlaps W23/W24 roles")
                aliases[alias] = revision["role"]
            self.revisions[revision["revision_digest"]] = revision
        for name in (
            "execution_occurrence_ledger",
            "deployment_readback_ledger",
            "rollback_occurrence_ledger",
        ):
            if self.snapshot.get(name) != []:
                raise ValueError(f"checked-in production {name} must remain empty")
        expected = _digest(
            {
                key: value
                for key, value in self.snapshot.items()
                if key != "contract_digest"
            }
        )
        if self.snapshot.get("contract_digest") != expected:
            raise ValueError("W24 contract digest mismatch")

    def _authority(
        self, source_digest: str, revision_digest: str, role: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        source = self.sources.get(source_digest)
        revision = self.revisions.get(revision_digest)
        if source is None or revision is None:
            raise LookupError("authority coordinate is not pinned")
        if (
            source["role"] != role
            or revision["role"] != role
            or revision["source_digest"] != source_digest
        ):
            raise ValueError("authority role mismatch")
        return source, revision

    def _scope(
        self,
        revision: dict[str, Any],
        *,
        target: dict[str, Any],
        policy_digest: str,
    ) -> None:
        scope = revision["scope"]
        if (
            scope["operation"] != ROLES[revision["role"]]
            or scope["repository"] != target["runtime_repository"]
            or scope["ref"] != target["target_ref"]
            or scope["environment"] != target["target_environment"]
            or scope["policy_digest"] != policy_digest
        ):
            raise ValueError("occurrence outside authority scope")

    def _hold(self, status: str, error: Exception | str) -> dict[str, Any]:
        return _merge({"status": status, "error": str(error)}, _negative())

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W24_W23_CUSTODY_PINNED__EXECUTION_DEPLOYMENT_HEALTH_"
                    "AND_ROLLBACK_RETURNS_OPEN"
                ),
                "phase": PHASE,
                "w23_head": W23_HEAD,
                "w23_tree": W23_TREE,
                "w23_contract_digest": W23_CONTRACT,
                "w23_receipt_id": W23_RECEIPT,
                "w23_image_published": False,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "execution_occurrence_count": 0,
                "deployment_readback_count": 0,
                "rollback_occurrence_count": 0,
                "successor": self.snapshot["successor"],
            },
            _negative(),
        )

    def inspect_source_revision(
        self, source_digest: str, revision_digest: str
    ) -> dict[str, Any]:
        try:
            source = self.sources[_sha(source_digest, "source_digest")]
            source, revision = self._authority(
                source_digest, revision_digest, source["role"]
            )
            return _merge(
                {
                    "status": "PASS_W24_AUTHORITY_SOURCE_REVISION_PINNED",
                    "source": source,
                    "revision": revision,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W24_AUTHORITY_COORDINATE_UNPINNED", error)

    def _w23(
        self,
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        authorization_json: str,
    ) -> dict[str, Any]:
        closure = self.w23_gate.inspect_execution_authorization(
            challenge_json,
            publication_json,
            publication_observation_json,
            policy_a_json,
            policy_b_json,
            authorization_json,
        )
        if not closure.get("execution_authorized"):
            raise ValueError(
                "W23 execution authorization is not independently verified"
            )
        challenge = _strict_loads(challenge_json)
        authorization = _strict_loads(authorization_json)
        return {
            "target": closure["target"],
            "policy_digest": _sha(
                challenge["policy_digest"], "challenge.policy_digest"
            ),
            "authorization_digest": _sha(
                closure["authorization_digest"], "authorization_digest"
            ),
            "authorized_at": authorization["authorized_at"],
            "execution_expires_at": closure["execution_expires_at"],
        }

    def _execution(self, text: str, w23: dict[str, Any]) -> dict[str, Any]:
        record = _record(
            text,
            fields=EXECUTION_FIELDS,
            schema=EXECUTION_SCHEMA,
            digest_fields=(
                "w23_authorization_digest",
                "dispatch_digest",
                "execution_digest",
            ),
            id_fields=("occurrence_id", "provider_execution_id"),
            digest_field="execution_digest",
        )
        if (
            record["w23_authorization_digest"] != w23["authorization_digest"]
            or record["target"] != w23["target"]
            or record["exit_status"] != "SUCCESS"
        ):
            raise ValueError("execution occurrence does not bind successful W23 target")
        started = _timestamp(record["started_at"], "execution.started_at")
        completed = _timestamp(record["completed_at"], "execution.completed_at")
        if not (
            _timestamp(w23["authorized_at"], "w23.authorized_at")
            <= started
            <= completed
            <= _timestamp(w23["execution_expires_at"], "w23.expires_at")
        ):
            raise ValueError("execution occurrence outside W23 authorization window")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "EXECUTION_OPERATOR",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(record, revision, "execution_digest", record["completed_at"])
        return record

    def _promotion(
        self, text: str, w23: dict[str, Any], execution: dict[str, Any]
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=PROMOTION_FIELDS,
            schema=PROMOTION_SCHEMA,
            digest_fields=(
                "execution_digest",
                "provider_state_digest",
                "promotion_observation_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="promotion_observation_digest",
        )
        if (
            record["execution_digest"] != execution["execution_digest"]
            or record["target"] != w23["target"]
            or record["observed_state"] != "PROMOTED"
            or _timestamp(record["observed_at"], "promotion.observed_at")
            < _timestamp(execution["completed_at"], "execution.completed_at")
        ):
            raise ValueError("promotion observation does not bind execution")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "PROMOTION_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "promotion_observation_digest",
            record["observed_at"],
        )
        return record

    def _deployment(
        self,
        text: str,
        w23: dict[str, Any],
        execution: dict[str, Any],
        promotion: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=DEPLOYMENT_FIELDS,
            schema=DEPLOYMENT_SCHEMA,
            digest_fields=(
                "execution_digest",
                "promotion_observation_digest",
                "manifest_digest",
                "endpoint_uri_hash",
                "provider_readback_digest",
                "deployment_readback_digest",
            ),
            id_fields=("occurrence_id", "deployment_id"),
            digest_field="deployment_readback_digest",
        )
        target_digest = w23["target"]["published_image_digest"]
        if (
            record["execution_digest"] != execution["execution_digest"]
            or record["promotion_observation_digest"]
            != promotion["promotion_observation_digest"]
            or record["target"] != w23["target"]
            or record["manifest_digest"] != target_digest
            or not record["immutable_reference"].endswith("@" + target_digest)
        ):
            raise ValueError("deployment readback does not bind immutable target")
        deployed = _timestamp(record["deployed_at"], "deployment.deployed_at")
        observed = _timestamp(record["observed_at"], "deployment.observed_at")
        if not (
            _timestamp(execution["completed_at"], "execution.completed_at")
            <= deployed
            <= observed
        ):
            raise ValueError("deployment chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "DEPLOYMENT_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "deployment_readback_digest",
            record["observed_at"],
        )
        return record

    def _health(
        self, text: str, w23: dict[str, Any], deployment: dict[str, Any]
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=HEALTH_FIELDS,
            schema=HEALTH_SCHEMA,
            digest_fields=(
                "deployment_readback_digest",
                "health_root_digest",
                "health_window_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="health_window_digest",
        )
        if (
            record["deployment_readback_digest"]
            != deployment["deployment_readback_digest"]
            or record["target"] != w23["target"]
            or record["health_state"] != "HEALTHY"
            or type(record["sample_count"]) is not int
            or record["sample_count"] < 3
            or type(record["interval_seconds"]) is not int
            or record["interval_seconds"] < 20
            or type(record["span_seconds"]) is not int
            or record["span_seconds"] < 40
        ):
            raise ValueError("health window requirements not satisfied")
        first = _timestamp(record["first_observed_at"], "health.first")
        last = _timestamp(record["last_observed_at"], "health.last")
        if (
            first
            < _timestamp(deployment["observed_at"], "deployment.observed_at")
            or last < first
            or (last - first).total_seconds() < record["span_seconds"]
            or record["span_seconds"]
            < (record["sample_count"] - 1) * record["interval_seconds"]
        ):
            raise ValueError("health chronology/sample geometry invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "HEALTH_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(record, revision, "health_window_digest", record["last_observed_at"])
        return record

    def _rollback_authorization(
        self,
        text: str,
        w23: dict[str, Any],
        deployment: dict[str, Any],
        health: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=ROLLBACK_AUTH_FIELDS,
            schema=ROLLBACK_AUTH_SCHEMA,
            digest_fields=(
                "deployment_readback_digest",
                "health_window_digest",
                "previous_safe_image_digest",
                "rollback_plan_digest",
                "rollback_authorization_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="rollback_authorization_digest",
        )
        if (
            record["deployment_readback_digest"]
            != deployment["deployment_readback_digest"]
            or record["health_window_digest"] != health["health_window_digest"]
            or record["target"] != w23["target"]
            or record["previous_safe_image_digest"]
            == w23["target"]["published_image_digest"]
            or record["rollback_mode"] not in {"DRILL", "EMERGENCY"}
        ):
            raise ValueError("rollback authorization bindings invalid")
        authorized = _timestamp(record["authorized_at"], "rollback.authorized_at")
        expires = _timestamp(record["expires_at"], "rollback.expires_at")
        if not (
            _timestamp(health["last_observed_at"], "health.last")
            <= authorized
            < expires
            and (expires - authorized).total_seconds() <= 3600
        ):
            raise ValueError("rollback authorization freshness invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "ROLLBACK_AUTHORIZER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "rollback_authorization_digest",
            record["authorized_at"],
        )
        return record

    def _rollback_occurrence(
        self,
        text: str,
        w23: dict[str, Any],
        deployment: dict[str, Any],
        authorization: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=ROLLBACK_OCCURRENCE_FIELDS,
            schema=ROLLBACK_OCCURRENCE_SCHEMA,
            digest_fields=(
                "rollback_authorization_digest",
                "deployment_readback_digest",
                "from_image_digest",
                "to_image_digest",
                "rollback_occurrence_digest",
            ),
            id_fields=("occurrence_id", "provider_execution_id"),
            digest_field="rollback_occurrence_digest",
        )
        if (
            record["rollback_authorization_digest"]
            != authorization["rollback_authorization_digest"]
            or record["deployment_readback_digest"]
            != deployment["deployment_readback_digest"]
            or record["target"] != w23["target"]
            or record["from_image_digest"]
            != w23["target"]["published_image_digest"]
            or record["to_image_digest"]
            != authorization["previous_safe_image_digest"]
            or record["exit_status"] != "SUCCESS"
        ):
            raise ValueError("rollback occurrence bindings invalid")
        started = _timestamp(record["started_at"], "rollback.started_at")
        completed = _timestamp(record["completed_at"], "rollback.completed_at")
        if not (
            _timestamp(authorization["authorized_at"], "rollback.authorized_at")
            <= started
            <= completed
            <= _timestamp(authorization["expires_at"], "rollback.expires_at")
        ):
            raise ValueError("rollback occurrence outside authorization window")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "ROLLBACK_OPERATOR",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "rollback_occurrence_digest",
            record["completed_at"],
        )
        return record

    def _rollback_observation(
        self,
        text: str,
        w23: dict[str, Any],
        deployment: dict[str, Any],
        authorization: dict[str, Any],
        occurrence: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=ROLLBACK_OBSERVATION_FIELDS,
            schema=ROLLBACK_OBSERVATION_SCHEMA,
            digest_fields=(
                "rollback_occurrence_digest",
                "deployment_readback_digest",
                "observed_image_digest",
                "provider_state_digest",
                "rollback_observation_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="rollback_observation_digest",
        )
        if (
            record["rollback_occurrence_digest"]
            != occurrence["rollback_occurrence_digest"]
            or record["deployment_readback_digest"]
            != deployment["deployment_readback_digest"]
            or record["target"] != w23["target"]
            or record["observed_image_digest"]
            != authorization["previous_safe_image_digest"]
            or record["observed_state"] != "ROLLED_BACK"
            or _timestamp(record["observed_at"], "rollback observation")
            < _timestamp(occurrence["completed_at"], "rollback completed")
        ):
            raise ValueError("rollback observation bindings invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "ROLLBACK_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "rollback_observation_digest",
            record["observed_at"],
        )
        return record

    def _all(
        self,
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_authorization_json: str,
        execution_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        rollback_authorization_json: str,
        rollback_occurrence_json: str,
        rollback_observation_json: str,
    ) -> tuple[dict[str, Any], ...]:
        w23 = self._w23(
            challenge_json,
            publication_json,
            publication_observation_json,
            policy_a_json,
            policy_b_json,
            execution_authorization_json,
        )
        execution = self._execution(execution_json, w23)
        promotion = self._promotion(promotion_json, w23, execution)
        deployment = self._deployment(
            deployment_json, w23, execution, promotion
        )
        health = self._health(health_json, w23, deployment)
        rollback_authorization = self._rollback_authorization(
            rollback_authorization_json, w23, deployment, health
        )
        rollback_occurrence = self._rollback_occurrence(
            rollback_occurrence_json,
            w23,
            deployment,
            rollback_authorization,
        )
        rollback_observation = self._rollback_observation(
            rollback_observation_json,
            w23,
            deployment,
            rollback_authorization,
            rollback_occurrence,
        )
        return (
            w23,
            execution,
            promotion,
            deployment,
            health,
            rollback_authorization,
            rollback_occurrence,
            rollback_observation,
        )

    def inspect_execution_occurrence(
        self,
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_authorization_json: str,
        execution_json: str,
    ) -> dict[str, Any]:
        try:
            w23 = self._w23(
                challenge_json,
                publication_json,
                publication_observation_json,
                policy_a_json,
                policy_b_json,
                execution_authorization_json,
            )
            execution = self._execution(execution_json, w23)
            return _merge(
                {
                    "status": "PASS_W24_EXECUTION_OCCURRENCE_VERIFIED",
                    "target": w23["target"],
                    "execution_digest": execution["execution_digest"],
                    "w23_execution_authorization_verified": True,
                    "execution_occurrence_verified": True,
                },
                _negative(),
                {
                    "w23_execution_authorization_verified": True,
                    "execution_occurrence_verified": True,
                },
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W24_EXECUTION_OCCURRENCE_REJECTED", error)

    def evaluate_closure(
        self,
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_authorization_json: str,
        execution_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        rollback_authorization_json: str,
        rollback_occurrence_json: str,
        rollback_observation_json: str,
    ) -> dict[str, Any]:
        try:
            (
                w23,
                execution,
                promotion,
                deployment,
                health,
                rollback_authorization,
                rollback_occurrence,
                rollback_observation,
            ) = self._all(
                challenge_json,
                publication_json,
                publication_observation_json,
                policy_a_json,
                policy_b_json,
                execution_authorization_json,
                execution_json,
                promotion_json,
                deployment_json,
                health_json,
                rollback_authorization_json,
                rollback_occurrence_json,
                rollback_observation_json,
            )
            certificate = {
                "schema": CLOSURE_SCHEMA,
                "w23_authorization_digest": w23["authorization_digest"],
                "execution_digest": execution["execution_digest"],
                "promotion_observation_digest": promotion[
                    "promotion_observation_digest"
                ],
                "deployment_readback_digest": deployment[
                    "deployment_readback_digest"
                ],
                "health_window_digest": health["health_window_digest"],
                "rollback_authorization_digest": rollback_authorization[
                    "rollback_authorization_digest"
                ],
                "rollback_occurrence_digest": rollback_occurrence[
                    "rollback_occurrence_digest"
                ],
                "rollback_observation_digest": rollback_observation[
                    "rollback_observation_digest"
                ],
                "target": w23["target"],
                "settlement_state": "ROLLED_BACK_TO_PREVIOUS_SAFE_IMAGE",
            }
            certificate["certificate_digest"] = _digest(certificate)
            return _merge(
                {
                    "status": (
                        "PASS_W24_EXECUTION_DEPLOYMENT_HEALTH_AND_ROLLBACK_"
                        "READBACK_VERIFIED__PERSISTENT_SETTLEMENT_OPEN"
                    ),
                    "closure_certificate": certificate,
                    "target": w23["target"],
                    "w23_execution_authorization_verified": True,
                    "execution_occurrence_verified": True,
                    "promotion_observed": True,
                    "deployment_readback_verified": True,
                    "health_window_verified": True,
                    "rollback_authorization_verified": True,
                    "rollback_occurrence_verified": True,
                    "rollback_observation_verified": True,
                    "workflow_dispatched": False,
                    "endpoint_contacted": False,
                    "merge_claimed": False,
                    "deployment_claimed": False,
                    "promotion_claimed": False,
                },
                {
                    "runtime_mutated_registry": False,
                    "runtime_issued_authority_signature": False,
                },
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W24_RETURN_CLOSURE_REJECTED", error)

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W24_RETURN_SEPARATION_LAW_EXPLAINED",
                "law": (
                    "AUTHORIZATION != EXECUTION; EXECUTION != INDEPENDENT "
                    "PROMOTION OBSERVATION; PROMOTION OBSERVATION != DEPLOYMENT "
                    "READBACK; DEPLOYMENT != HEALTH WINDOW; ROLLBACK AUTHORIZATION "
                    "!= ROLLBACK OCCURRENCE; OCCURRENCE != INDEPENDENT READBACK"
                ),
                "required_roles": list(ROLES),
                "runtime_is_verifier_only": True,
                "runtime_dispatches": False,
                "runtime_contacts_endpoint": False,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_execution_deployment_rollback_readback(mcp: Any) -> None:
    """Register twelve W24 tools and one frozen resource."""
    gate = FrozenExecutionDeploymentRollbackReadback.load()

    @mcp.tool()
    def athena_w24_execution_deployment_rollback_status() -> str:
        """Return W24 frozen-empty execution/deployment/rollback boundaries."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w24_w23_custody() -> str:
        """Inspect exact W23 custody; it grants no return authority."""
        result = gate.status()
        result["status"] = "PASS_W24_W23_CUSTODY_PINNED__NO_AUTHORITY_GRANTED"
        return _render(result)

    @mcp.tool()
    def inspect_athena_w24_authority_source_revision(
        source_digest: str, revision_digest: str
    ) -> str:
        """Inspect one pinned W24 return-authority coordinate."""
        return _render(gate.inspect_source_revision(source_digest, revision_digest))

    @mcp.tool()
    def inspect_athena_w24_execution_occurrence(
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_authorization_json: str,
        execution_json: str,
    ) -> str:
        """Verify execution against a complete W23 authorization chain."""
        return _render(
            gate.inspect_execution_occurrence(
                challenge_json,
                publication_json,
                publication_observation_json,
                policy_a_json,
                policy_b_json,
                execution_authorization_json,
                execution_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w24_promotion_observation_contract() -> str:
        """Inspect the independent promotion-observation requirement."""
        return _render(
            {
                "schema": PROMOTION_SCHEMA,
                "required_role": "PROMOTION_OBSERVER",
                "execution_digest_required": True,
                "runtime_observes_provider": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w24_deployment_readback_contract() -> str:
        """Inspect immutable deployment-readback bindings."""
        return _render(
            {
                "schema": DEPLOYMENT_SCHEMA,
                "required_role": "DEPLOYMENT_OBSERVER",
                "immutable_manifest_binding_required": True,
                "raw_endpoint_recorded": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w24_health_window_contract() -> str:
        """Inspect minimum health-window geometry."""
        return _render(
            {
                "schema": HEALTH_SCHEMA,
                "required_role": "HEALTH_OBSERVER",
                "minimum_samples": 3,
                "minimum_interval_seconds": 20,
                "minimum_span_seconds": 40,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w24_rollback_authorization_contract() -> str:
        """Inspect rollback authorization and freshness requirements."""
        return _render(
            {
                "schema": ROLLBACK_AUTH_SCHEMA,
                "required_role": "ROLLBACK_AUTHORIZER",
                "maximum_window_seconds": 3600,
                "previous_safe_image_required": True,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w24_rollback_occurrence_contract() -> str:
        """Inspect the separately signed rollback occurrence."""
        return _render(
            {
                "schema": ROLLBACK_OCCURRENCE_SCHEMA,
                "required_role": "ROLLBACK_OPERATOR",
                "authorization_is_occurrence": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w24_rollback_observation_contract() -> str:
        """Inspect independent rollback readback requirements."""
        return _render(
            {
                "schema": ROLLBACK_OBSERVATION_SCHEMA,
                "required_role": "ROLLBACK_OBSERVER",
                "operator_self_observation_allowed": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def evaluate_athena_w24_execution_deployment_rollback_closure(
        challenge_json: str,
        publication_json: str,
        publication_observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_authorization_json: str,
        execution_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        rollback_authorization_json: str,
        rollback_occurrence_json: str,
        rollback_observation_json: str,
    ) -> str:
        """Verify all W24 returns without performing any side effect."""
        return _render(
            gate.evaluate_closure(
                challenge_json,
                publication_json,
                publication_observation_json,
                policy_a_json,
                policy_b_json,
                execution_authorization_json,
                execution_json,
                promotion_json,
                deployment_json,
                health_json,
                rollback_authorization_json,
                rollback_occurrence_json,
                rollback_observation_json,
            )
        )

    @mcp.tool()
    def explain_athena_w24_return_separation_law() -> str:
        """Explain W24 authorization/occurrence/readback separation."""
        return _render(gate.explain())

    @mcp.resource("athena://w24-execution-deployment-rollback-readback")
    def execution_deployment_rollback_resource() -> str:
        """Read the frozen W24 contract and production-empty ledgers."""
        return _render(gate.snapshot)
