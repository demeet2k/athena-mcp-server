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
    DATA_PATH as W23_DATA_PATH,
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
CONSUMPTION_SCHEMA = "athena.w24-execution-authorization-consumption/v1"
PROMOTION_SCHEMA = "athena.w24-promotion-observation/v1"
DEPLOYMENT_SCHEMA = "athena.w24-deployment-readback/v1"
HEALTH_SCHEMA = "athena.w24-health-window/v1"
PREVIOUS_SAFE_SCHEMA = "athena.w24-previous-safe-deployment-certificate/v1"
ROLLBACK_AUTH_SCHEMA = "athena.w24-rollback-authorization/v1"
ROLLBACK_OCCURRENCE_SCHEMA = "athena.w24-rollback-occurrence/v1"
ROLLBACK_OBSERVATION_SCHEMA = "athena.w24-rollback-observation/v1"
CLOSURE_SCHEMA = "athena.w24-execution-deployment-rollback-closure/v1"

W23_HISTORICAL_HEAD = "3061598cd050aa6b8ad8b647e86c2295acb54228"
W23_HISTORICAL_TREE = "61ae40f869da0fe4979cadb054e46e67007833ae"
W23_HISTORICAL_PARENT = "aa8c382419fd093507f3059751a75dc14ffa8662"
W23_HISTORICAL_CONTRACT = (
    "sha256:1ec0f8749b47c68399ce6356db6523676f5c82a449f3420bb0cd9936871eabf4"
)
W23_HISTORICAL_RECEIPT = (
    "w23-execution-handoff:sha256:"
    "c06878df07733ad8459e46fc1bca02bf844ad78b7a72a2703430e984a4479ae5"
)
W23_HARDENING_HEAD = "5ee30b98e4a6653fcbce65d733513b1e25529ddd"
W23_HARDENING_TREE = "02808be32a3aa76f0c1556b1dd736512b1523485"
W23_HARDENING_PARENT = "05d012f2e8cad0ea2d64e3b2fb8ae453b75350de"
W23_HARDENED_CONTRACT = (
    "sha256:3630dd1c67a19865c5c2e24b757f93e8c7a070439a329e70f22f281a72f53613"
)
W23_HARDENING_RECEIPT = (
    "w23-execution-handoff-hardening:sha256:"
    "b88d514648c1562177fd1697e1a5c93cb371c13f8418dc59ef6f1652399aa69e"
)
W23_LOCAL_IMAGE = (
    "sha256:8bca337faa3989f9ed94a2df0ceea29ea3b843e46e03359edfa3e9f36638f29a"
)
W24_HISTORICAL_HEAD = "6906afa2cab034f51ae7d86aae409bf0a6304a91"
W24_HISTORICAL_TREE = "e571caf572a7ee4baa553016c0f9e7315551ecab"
W24_HISTORICAL_PARENT = W23_HISTORICAL_HEAD
W24_HISTORICAL_CONTRACT = (
    "sha256:dc316ded97c885e0febe36b558d7bb17468f629988b20dd49723a1ed586b35b4"
)
W24_HISTORICAL_RECEIPT = (
    "w24-return-readback:sha256:"
    "4e013a8505042a23b373d2ab5ade474cb16a4a95d58fc9251ae62ac05963e539"
)
CANONICAL_GOVERNANCE_REPOSITORY = "demeet2k/Athena"
CANONICAL_RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
CANONICAL_RUNTIME_BRANCH = "agent/w15-reconcile-capsule-deep-hardening"
CANONICAL_RUNTIME_REF = "refs/heads/" + CANONICAL_RUNTIME_BRANCH
CANONICAL_AUTHORITY_REF = "refs/heads/authority/w24"
CANONICAL_REGISTRY_NAMESPACE = "ghcr.io/demeet2k/athena-mcp"
WORKFLOW_PATH = ".github/workflows/w24-execution-deployment-rollback-readback.yml"

# Filled from the correction-forward snapshot after its exact topology is
# finalized.  Unlike the historical v1 contract, this value is pinned outside
# the mutable JSON and therefore cannot be changed by merely re-addressing it.
W24_HARDENED_CONTRACT = (
    "sha256:ddb09f939d8b9d1662e34b1558f0ba596e7ac70aa0b1a99098b7723b7cd45f3f"
)

ROLES = {
    "EXECUTION_OPERATOR": "promotion.execute",
    "EXECUTION_CONSUMPTION_OBSERVER": "promotion.execute.consume.observe",
    "PROMOTION_OBSERVER": "promotion.observe",
    "DEPLOYMENT_OBSERVER": "deployment.observe",
    "HEALTH_OBSERVER": "deployment.health.observe",
    "PREVIOUS_SAFE_DEPLOYMENT_OBSERVER": "rollback.previous-safe.observe",
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
CONSUMPTION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "w23_authorization_digest",
    "execution_digest",
    "execution_occurrence_id",
    "provider_execution_id",
    "dispatch_digest",
    "target",
    "previous_ledger_root_digest",
    "consumed_ledger_root_digest",
    "prior_consumption_count",
    "consumption_state",
    "observed_at",
    "signature",
    "execution_consumption_digest",
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
PREVIOUS_SAFE_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "target",
    "safe_image_digest",
    "immutable_reference",
    "manifest_digest",
    "deployment_id",
    "provider_readback_digest",
    "admission_digest",
    "health_root_digest",
    "health_state",
    "deployed_at",
    "last_healthy_at",
    "observed_at",
    "signature",
    "previous_safe_certificate_digest",
}
ROLLBACK_AUTH_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "deployment_readback_digest",
    "health_window_digest",
    "previous_safe_certificate_digest",
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
    "previous_safe_certificate_digest",
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
    if normalized["governance_repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
        raise ValueError("authority source governance repository mismatch")
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
    expected_path = (
        ".athena/authority/w24/" + normalized["role"].lower() + ".json"
    )
    if (
        normalized["repository"] != CANONICAL_GOVERNANCE_REPOSITORY
        or normalized["ref"] != CANONICAL_AUTHORITY_REF
        or normalized["path"] != expected_path
    ):
        raise ValueError("authority revision governance coordinate mismatch")
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
        "execution_consumption_verified": False,
        "execution_authorization_consumed_once": False,
        "fresh_execution_authority_issued": False,
        "fresh_execution_claimed": False,
        "promotion_observed": False,
        "deployment_readback_verified": False,
        "health_window_verified": False,
        "previous_safe_deployment_verified": False,
        "rollback_authorization_verified": False,
        "rollback_occurrence_verified": False,
        "rollback_observation_verified": False,
        "merge_claimed": False,
        "deployment_claimed": False,
        "promotion_claimed": False,
    }


def _expected_predecessor() -> dict[str, Any]:
    return {
        "runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
        "runtime_pull_request": 13,
        "branch": CANONICAL_RUNTIME_BRANCH,
        "historical_w23_head": W23_HISTORICAL_HEAD,
        "historical_w23_tree": W23_HISTORICAL_TREE,
        "historical_w23_sole_parent": W23_HISTORICAL_PARENT,
        "historical_w23_contract_digest": W23_HISTORICAL_CONTRACT,
        "historical_w23_receipt_id": W23_HISTORICAL_RECEIPT,
        "historical_w24_head": W24_HISTORICAL_HEAD,
        "historical_w24_tree": W24_HISTORICAL_TREE,
        "historical_w24_sole_parent": W24_HISTORICAL_PARENT,
        "historical_w24_contract_digest": W24_HISTORICAL_CONTRACT,
        "historical_w24_receipt_id": W24_HISTORICAL_RECEIPT,
        "hardened_w23_head": W23_HARDENING_HEAD,
        "hardened_w23_tree": W23_HARDENING_TREE,
        "hardened_w23_sole_parent": W23_HARDENING_PARENT,
        "hardened_w23_contract_digest": W23_HARDENED_CONTRACT,
        "hardened_w23_receipt_id": W23_HARDENING_RECEIPT,
        "hardened_w23_is_active_verifier": True,
        "historical_w23_and_w24_preserved": True,
    }


def _expected_control_observation() -> dict[str, Any]:
    return {
        "repository": CANONICAL_GOVERNANCE_REPOSITORY,
        "pull_request": 21,
        "branch": "agent/w23-admit-promotion-execution-handoff",
        "head": "7909f6fd5d9f58ecfde0f23e5f6fd41e9b731ce5",
        "base": "b74bb6caea37569bc2c050c060bcc35641dd068e",
        "receipt_id": (
            "w23-control-admission:sha256:"
            "92adfc99e9caa63052ee17bca5a32ff26aa0bde37adeaf664641c759b70f9be9"
        ),
        "admits_historical_w23_only": True,
        "admits_hardened_w23": False,
        "grants_production_authority": False,
        "hosted_runner_status": "HOLD[PLATFORM_OBSTRUCTION_BEFORE_FIRST_STEP]",
    }


def _expected_return_contract() -> dict[str, Any]:
    return {
        "authority_source_schema": SOURCE_SCHEMA,
        "authority_revision_schema": REVISION_SCHEMA,
        "execution_occurrence_schema": EXECUTION_SCHEMA,
        "execution_consumption_schema": CONSUMPTION_SCHEMA,
        "promotion_observation_schema": PROMOTION_SCHEMA,
        "deployment_readback_schema": DEPLOYMENT_SCHEMA,
        "health_window_schema": HEALTH_SCHEMA,
        "previous_safe_deployment_schema": PREVIOUS_SAFE_SCHEMA,
        "rollback_authorization_schema": ROLLBACK_AUTH_SCHEMA,
        "rollback_occurrence_schema": ROLLBACK_OCCURRENCE_SCHEMA,
        "rollback_observation_schema": ROLLBACK_OBSERVATION_SCHEMA,
        "closure_schema": CLOSURE_SCHEMA,
        "roles": list(ROLES),
        "w23_execution_authorization_required": True,
        "one_shot_consumption_observation_required": True,
        "exact_historical_replay_is_idempotent": True,
        "historical_replay_grants_fresh_authority": False,
        "execution_operator_must_differ_from_authorizer": True,
        "promotion_observation_required": True,
        "deployment_readback_required": True,
        "canonical_registry_namespace": CANONICAL_REGISTRY_NAMESPACE,
        "minimum_health_samples": 3,
        "minimum_health_interval_seconds": 20,
        "minimum_health_span_seconds": 40,
        "previous_safe_deployment_certificate_required": True,
        "rollback_authorization_required": True,
        "rollback_occurrence_required": True,
        "independent_rollback_observation_required": True,
        "total_chronology_required": True,
        "cross_wave_occurrence_overlap_allowed": False,
        "self_supplied_sources_revisions_or_keys_allowed": False,
        "cross_role_identity_or_key_overlap_allowed": False,
        "runtime_can_dispatch": False,
        "runtime_can_contact_endpoint": False,
        "runtime_can_execute": False,
        "runtime_can_deploy_or_promote": False,
    }


def _expected_verifier_coordinates() -> dict[str, Any]:
    return {
        "repository": CANONICAL_RUNTIME_REPOSITORY,
        "ref": CANONICAL_RUNTIME_REF,
        "workflow": WORKFLOW_PATH,
        "required_parent_head": W23_HARDENING_HEAD,
        "required_parent_tree": W23_HARDENING_TREE,
        "hardened_w23_contract_digest": W23_HARDENED_CONTRACT,
        "hardened_w23_receipt_id": W23_HARDENING_RECEIPT,
        "runtime_head_bound_by_workflow_receipt": True,
    }


def _expected_registry_admission() -> dict[str, Any]:
    return {
        "repository": CANONICAL_GOVERNANCE_REPOSITORY,
        "status": "NOT_ADMITTED",
        "source_digests": [],
        "revision_digests": [],
        "grants_production_authority": False,
    }


def _expected_boundaries() -> dict[str, Any]:
    return {
        "historical_w23_and_w24_preserved": True,
        "hardened_w23_verifier_pinned": True,
        "hardened_w23_control_admitted": False,
        "w23_image_published": False,
        "production_authority_source_count": 0,
        "production_authority_revision_count": 0,
        "w23_execution_authorization_verified": False,
        "execution_occurrence_verified": False,
        "execution_consumption_verified": False,
        "execution_authorization_consumed_once": False,
        "fresh_execution_authority_issued": False,
        "fresh_execution_claimed": False,
        "promotion_observed": False,
        "deployment_readback_verified": False,
        "health_window_verified": False,
        "previous_safe_deployment_verified": False,
        "rollback_authorization_verified": False,
        "rollback_occurrence_verified": False,
        "rollback_observation_verified": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
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
        *,
        test_only_registry: bool = False,
    ):
        self.snapshot = deepcopy(snapshot)
        self.w23_gate = w23_gate or FrozenPromotionExecutionHandoff.load()
        self.test_only_registry = test_only_registry
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

    @classmethod
    def from_test_snapshot(
        cls,
        snapshot: dict[str, Any],
        w23_gate: FrozenPromotionExecutionHandoff,
    ) -> "FrozenExecutionDeploymentRollbackReadback":
        """Build an explicitly non-production fixture with synthetic authorities."""
        return cls(
            snapshot,
            w23_gate=w23_gate,
            test_only_registry=True,
        )

    def _validate_snapshot(self) -> None:
        expected_top_level = {
            "schema",
            "phase",
            "predecessor",
            "control_predecessor_observation",
            "return_contract",
            "verifier_coordinates",
            "authority_registry_admission",
            "authority_registry",
            "execution_occurrence_ledger",
            "execution_consumption_ledger",
            "deployment_readback_ledger",
            "previous_safe_deployment_ledger",
            "rollback_occurrence_ledger",
            "boundaries",
            "successor",
            "contract_digest",
        }
        if set(self.snapshot) != expected_top_level:
            raise ValueError("W24 top-level shape mismatch")
        if self.snapshot.get("schema") != SCHEMA or self.snapshot.get("phase") != PHASE:
            raise ValueError("W24 schema/phase mismatch")
        if self.snapshot["predecessor"] != _expected_predecessor():
            raise ValueError("W23/W24 predecessor mismatch")
        if (
            self.snapshot["control_predecessor_observation"]
            != _expected_control_observation()
        ):
            raise ValueError("control predecessor mismatch")
        if self.snapshot["return_contract"] != _expected_return_contract():
            raise ValueError("W24 return contract drift")
        if self.snapshot["verifier_coordinates"] != _expected_verifier_coordinates():
            raise ValueError("W24 verifier coordinate drift")
        admission = self.snapshot["authority_registry_admission"]
        if self.test_only_registry:
            if (
                set(admission)
                != {
                    "repository",
                    "status",
                    "source_digests",
                    "revision_digests",
                    "grants_production_authority",
                }
                or admission["repository"] != CANONICAL_GOVERNANCE_REPOSITORY
                or admission["status"] != "TEST_ONLY_UNTRUSTED_FIXTURE"
                or admission["grants_production_authority"] is not False
            ):
                raise ValueError("test-only authority registry admission mismatch")
        elif admission != _expected_registry_admission():
            raise ValueError("production authority registry is not admitted")
        if self.snapshot["boundaries"] != _expected_boundaries():
            raise ValueError("W24 protected boundaries drift")
        if (
            self.snapshot["successor"]
            != "KC144.XNAV.W25::ADMIT-EXECUTION-DEPLOYMENT-ROLLBACK-RETURNS-AND-ISSUE-PERSISTENT-PROMOTION-SETTLEMENT"
        ):
            raise ValueError("W24 successor drift")
        if self.test_only_registry:
            canonical_w23 = _strict_loads(
                W23_DATA_PATH.read_text(encoding="utf-8")
            )
            for field in (
                "schema",
                "phase",
                "predecessor",
                "control_predecessor_observation",
                "w22_control_protocol_observation",
                "execution_contract",
                "successor",
            ):
                if self.w23_gate.snapshot.get(field) != canonical_w23[field]:
                    raise ValueError("test W23 gate diverges from hardened contract")
        elif (
            self.w23_gate.snapshot.get("contract_digest")
            != W23_HARDENED_CONTRACT
        ):
            raise ValueError("active W23 hardened gate mismatch")
        registry = self.snapshot["authority_registry"]
        if set(registry) != {"sources", "revisions"}:
            raise ValueError("authority registry shape mismatch")
        if not isinstance(registry["sources"], list) or not isinstance(
            registry["revisions"], list
        ):
            raise ValueError("authority registry coordinates must be arrays")
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
            if revision["repository"] != source["governance_repository"]:
                raise ValueError("revision repository differs from authority source")
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
        source_digests = sorted(self.sources)
        revision_digests = sorted(self.revisions)
        if self.test_only_registry:
            if (
                admission["source_digests"] != source_digests
                or admission["revision_digests"] != revision_digests
            ):
                raise ValueError("test-only authority digest admission mismatch")
        elif source_digests or revision_digests:
            raise ValueError("production authorities remain unadmitted")
        for name in (
            "execution_occurrence_ledger",
            "execution_consumption_ledger",
            "deployment_readback_ledger",
            "previous_safe_deployment_ledger",
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
        if not self.test_only_registry and expected != W24_HARDENED_CONTRACT:
            raise ValueError("W24 contract is not pinned outside the snapshot")

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
                    "W24_HARDENED_W23_VERIFIER_PINNED__PRODUCTION_AUTHORITIES_"
                    "AND_ALL_EXECUTION_DEPLOYMENT_ROLLBACK_RETURNS_OPEN"
                ),
                "phase": PHASE,
                "historical_w23_head": W23_HISTORICAL_HEAD,
                "hardened_w23_head": W23_HARDENING_HEAD,
                "hardened_w23_tree": W23_HARDENING_TREE,
                "hardened_w23_contract_digest": W23_HARDENED_CONTRACT,
                "hardened_w23_receipt_id": W23_HARDENING_RECEIPT,
                "w23_image_published": False,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "execution_occurrence_count": 0,
                "execution_consumption_count": 0,
                "deployment_readback_count": 0,
                "previous_safe_deployment_count": 0,
                "rollback_occurrence_count": 0,
                "test_only_registry": self.test_only_registry,
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
        upstream_records = [
            _strict_loads(value)
            for value in (
                publication_json,
                publication_observation_json,
                policy_a_json,
                policy_b_json,
                authorization_json,
            )
        ]
        upstream_occurrence_ids = {
            _identifier(record["occurrence_id"], "W23 occurrence_id")
            for record in upstream_records
        }
        if len(upstream_occurrence_ids) != len(upstream_records):
            raise ValueError("W23 occurrence axes overlap")
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
            "occurrence_ids": upstream_occurrence_ids,
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

    def _execution_consumption(
        self,
        text: str,
        w23: dict[str, Any],
        execution: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=CONSUMPTION_FIELDS,
            schema=CONSUMPTION_SCHEMA,
            digest_fields=(
                "w23_authorization_digest",
                "execution_digest",
                "dispatch_digest",
                "previous_ledger_root_digest",
                "consumed_ledger_root_digest",
                "execution_consumption_digest",
            ),
            id_fields=(
                "occurrence_id",
                "execution_occurrence_id",
                "provider_execution_id",
            ),
            digest_field="execution_consumption_digest",
        )
        expected_root = _digest(
            {
                "schema": (
                    "athena.w24-execution-authorization-consumption-ledger/v1"
                ),
                "previous_ledger_root_digest": record[
                    "previous_ledger_root_digest"
                ],
                "w23_authorization_digest": w23["authorization_digest"],
                "execution_digest": execution["execution_digest"],
                "execution_occurrence_id": execution["occurrence_id"],
                "provider_execution_id": execution["provider_execution_id"],
                "dispatch_digest": execution["dispatch_digest"],
            }
        )
        if (
            record["w23_authorization_digest"] != w23["authorization_digest"]
            or record["execution_digest"] != execution["execution_digest"]
            or record["execution_occurrence_id"] != execution["occurrence_id"]
            or record["provider_execution_id"]
            != execution["provider_execution_id"]
            or record["dispatch_digest"] != execution["dispatch_digest"]
            or type(record["prior_consumption_count"]) is not int
            or record["prior_consumption_count"] != 0
            or record["consumption_state"] != "CONSUMED_ONCE"
            or record["consumed_ledger_root_digest"] != expected_root
        ):
            raise ValueError("execution authorization consumption proof invalid")
        observed = _timestamp(
            record["observed_at"], "execution consumption observed_at"
        )
        if not (
            _timestamp(execution["completed_at"], "execution.completed_at")
            <= observed
            <= _timestamp(w23["execution_expires_at"], "w23.expires_at")
        ):
            raise ValueError("execution consumption chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "EXECUTION_CONSUMPTION_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        if record["target"] != w23["target"]:
            raise ValueError("execution consumption target mismatch")
        _verify(
            record,
            revision,
            "execution_consumption_digest",
            record["observed_at"],
        )
        return record

    def _promotion(
        self,
        text: str,
        w23: dict[str, Any],
        execution: dict[str, Any],
        consumption: dict[str, Any],
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
            < _timestamp(
                consumption["observed_at"], "execution consumption observed_at"
            )
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
        expected_reference = CANONICAL_REGISTRY_NAMESPACE + "@" + target_digest
        if (
            record["execution_digest"] != execution["execution_digest"]
            or record["promotion_observation_digest"]
            != promotion["promotion_observation_digest"]
            or record["target"] != w23["target"]
            or record["manifest_digest"] != target_digest
            or record["immutable_reference"] != expected_reference
        ):
            raise ValueError("deployment readback does not bind immutable target")
        deployed = _timestamp(record["deployed_at"], "deployment.deployed_at")
        observed = _timestamp(record["observed_at"], "deployment.observed_at")
        if not (
            _timestamp(promotion["observed_at"], "promotion.observed_at")
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

    def _previous_safe_deployment(
        self,
        text: str,
        w23: dict[str, Any],
        execution: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=PREVIOUS_SAFE_FIELDS,
            schema=PREVIOUS_SAFE_SCHEMA,
            digest_fields=(
                "safe_image_digest",
                "manifest_digest",
                "provider_readback_digest",
                "admission_digest",
                "health_root_digest",
                "previous_safe_certificate_digest",
            ),
            id_fields=("occurrence_id", "deployment_id"),
            digest_field="previous_safe_certificate_digest",
        )
        expected_reference = (
            CANONICAL_REGISTRY_NAMESPACE + "@" + record["safe_image_digest"]
        )
        if (
            record["target"] != w23["target"]
            or record["safe_image_digest"]
            == w23["target"]["published_image_digest"]
            or record["manifest_digest"] != record["safe_image_digest"]
            or record["immutable_reference"] != expected_reference
            or record["health_state"] != "HEALTHY"
        ):
            raise ValueError("previous-safe deployment certificate invalid")
        deployed = _timestamp(
            record["deployed_at"], "previous-safe deployed_at"
        )
        healthy = _timestamp(
            record["last_healthy_at"], "previous-safe last_healthy_at"
        )
        observed = _timestamp(
            record["observed_at"], "previous-safe observed_at"
        )
        if not (
            deployed
            <= healthy
            <= observed
            <= _timestamp(execution["started_at"], "execution.started_at")
        ):
            raise ValueError("previous-safe deployment chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "PREVIOUS_SAFE_DEPLOYMENT_OBSERVER",
        )
        self._scope(
            revision, target=record["target"], policy_digest=w23["policy_digest"]
        )
        _verify(
            record,
            revision,
            "previous_safe_certificate_digest",
            record["observed_at"],
        )
        return record

    def _rollback_authorization(
        self,
        text: str,
        w23: dict[str, Any],
        deployment: dict[str, Any],
        health: dict[str, Any],
        previous_safe: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=ROLLBACK_AUTH_FIELDS,
            schema=ROLLBACK_AUTH_SCHEMA,
            digest_fields=(
                "deployment_readback_digest",
                "health_window_digest",
                "previous_safe_certificate_digest",
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
            or record["previous_safe_certificate_digest"]
            != previous_safe["previous_safe_certificate_digest"]
            or record["target"] != w23["target"]
            or record["previous_safe_image_digest"]
            != previous_safe["safe_image_digest"]
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
        previous_safe: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=ROLLBACK_OBSERVATION_FIELDS,
            schema=ROLLBACK_OBSERVATION_SCHEMA,
            digest_fields=(
                "rollback_occurrence_digest",
                "deployment_readback_digest",
                "previous_safe_certificate_digest",
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
            or record["previous_safe_certificate_digest"]
            != previous_safe["previous_safe_certificate_digest"]
            or record["target"] != w23["target"]
            or record["observed_image_digest"]
            != previous_safe["safe_image_digest"]
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
        execution_consumption_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        previous_safe_deployment_json: str,
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
        consumption = self._execution_consumption(
            execution_consumption_json, w23, execution
        )
        promotion = self._promotion(
            promotion_json, w23, execution, consumption
        )
        deployment = self._deployment(
            deployment_json, w23, execution, promotion
        )
        health = self._health(health_json, w23, deployment)
        previous_safe = self._previous_safe_deployment(
            previous_safe_deployment_json, w23, execution
        )
        rollback_authorization = self._rollback_authorization(
            rollback_authorization_json,
            w23,
            deployment,
            health,
            previous_safe,
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
            previous_safe,
        )
        w24_records = (
            execution,
            consumption,
            promotion,
            deployment,
            health,
            previous_safe,
            rollback_authorization,
            rollback_occurrence,
            rollback_observation,
        )
        w24_occurrence_ids = {
            record["occurrence_id"] for record in w24_records
        }
        if len(w24_occurrence_ids) != len(w24_records):
            raise ValueError("W24 occurrence axes overlap")
        if w24_occurrence_ids.intersection(w23["occurrence_ids"]):
            raise ValueError("W23/W24 occurrence axes overlap")
        if (
            execution["provider_execution_id"]
            == rollback_occurrence["provider_execution_id"]
        ):
            raise ValueError("execution and rollback provider axes overlap")
        return (
            w23,
            execution,
            consumption,
            promotion,
            deployment,
            health,
            previous_safe,
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
        execution_consumption_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        previous_safe_deployment_json: str,
        rollback_authorization_json: str,
        rollback_occurrence_json: str,
        rollback_observation_json: str,
    ) -> dict[str, Any]:
        try:
            (
                w23,
                execution,
                consumption,
                promotion,
                deployment,
                health,
                previous_safe,
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
                execution_consumption_json,
                promotion_json,
                deployment_json,
                health_json,
                previous_safe_deployment_json,
                rollback_authorization_json,
                rollback_occurrence_json,
                rollback_observation_json,
            )
            certificate = {
                "schema": CLOSURE_SCHEMA,
                "w23_authorization_digest": w23["authorization_digest"],
                "execution_digest": execution["execution_digest"],
                "execution_consumption_digest": consumption[
                    "execution_consumption_digest"
                ],
                "promotion_observation_digest": promotion[
                    "promotion_observation_digest"
                ],
                "deployment_readback_digest": deployment[
                    "deployment_readback_digest"
                ],
                "health_window_digest": health["health_window_digest"],
                "previous_safe_certificate_digest": previous_safe[
                    "previous_safe_certificate_digest"
                ],
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
                "historical_return_only": True,
                "exact_replay_is_idempotent": True,
                "fresh_execution_authority_issued": False,
                "fresh_execution_claimed": False,
                "verifier_coordinates": self.snapshot["verifier_coordinates"],
            }
            certificate["certificate_digest"] = _digest(certificate)
            return _merge(
                {
                    "status": (
                        "PASS_W24_HISTORICAL_EXECUTION_CONSUMPTION_DEPLOYMENT_"
                        "HEALTH_AND_ROLLBACK_READBACK_VERIFIED__NO_FRESH_"
                        "AUTHORITY_OR_EXECUTION_CLAIMED__PERSISTENT_SETTLEMENT_OPEN"
                    ),
                    "closure_certificate": certificate,
                    "target": w23["target"],
                    "w23_execution_authorization_verified": True,
                    "execution_occurrence_verified": True,
                    "execution_consumption_verified": True,
                    "execution_authorization_consumed_once": True,
                    "fresh_execution_authority_issued": False,
                    "fresh_execution_claimed": False,
                    "promotion_observed": True,
                    "deployment_readback_verified": True,
                    "health_window_verified": True,
                    "previous_safe_deployment_verified": True,
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
                    "AUTHORIZATION != EXECUTION != ONE-SHOT CONSUMPTION "
                    "OBSERVATION; EXECUTION != INDEPENDENT PROMOTION OBSERVATION; "
                    "PROMOTION OBSERVATION != DEPLOYMENT READBACK; DEPLOYMENT != "
                    "HEALTH WINDOW; ARBITRARY DIGEST != PREVIOUS-SAFE DEPLOYMENT; "
                    "ROLLBACK AUTHORIZATION != ROLLBACK OCCURRENCE; OCCURRENCE != "
                    "INDEPENDENT READBACK; HISTORICAL REPLAY != FRESH AUTHORITY"
                ),
                "required_roles": list(ROLES),
                "runtime_is_verifier_only": True,
                "runtime_dispatches": False,
                "runtime_contacts_endpoint": False,
                "exact_historical_replay_is_idempotent": True,
                "historical_replay_grants_fresh_authority": False,
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
                "canonical_registry_namespace": CANONICAL_REGISTRY_NAMESPACE,
                "previous_safe_schema": PREVIOUS_SAFE_SCHEMA,
                "previous_safe_role": "PREVIOUS_SAFE_DEPLOYMENT_OBSERVER",
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
        execution_consumption_json: str,
        promotion_json: str,
        deployment_json: str,
        health_json: str,
        previous_safe_deployment_json: str,
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
                execution_consumption_json,
                promotion_json,
                deployment_json,
                health_json,
                previous_safe_deployment_json,
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
