"""KC144 W23 control-admissible promotion-execution handoff.

The runtime is a verifier and candidate compiler.  It cannot issue a
production challenge, publish an image, authorize execution, contact an
endpoint, dispatch work, merge, deploy, execute, or promote.

W23 adds the coordinates W22 deliberately left open:

* a signed, expiring freshness challenge;
* independent publisher and registry-observer occurrences;
* two disjoint promotion-policy decisions with HOLD dominance; and
* a sixth, separately scoped execution-authority occurrence.
"""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .independent_authority_return import (
    FrozenIndependentAuthorityReturn,
    _addressed,
    _bounded,
    _canonical_bytes,
    _commit,
    _digest,
    _exact,
    _identifier,
    _merge,
    _pairs,
    _sha,
    _signature,
    _signed,
    _strict_loads,
    _text,
    _timestamp,
)
from .provider_trust_anchor import _verify_ed25519_signature


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w23_promotion_execution_handoff.json"
)
SCHEMA = "athena.xnav-w23-promotion-execution-handoff/v1"
PHASE = "KC144.XNAV.W23"

SOURCE_SCHEMA = "athena.w23-execution-authority-source/v1"
REVISION_SCHEMA = "athena.w23-execution-authority-revision/v1"
CHALLENGE_SCHEMA = "athena.w23-freshness-challenge/v1"
PUBLICATION_SCHEMA = "athena.w23-artifact-publication-proof/v1"
OBSERVATION_SCHEMA = "athena.w23-artifact-publication-observation/v1"
DECISION_SCHEMA = "athena.w23-promotion-policy-decision/v1"
QUORUM_SCHEMA = "athena.w23-promotion-policy-quorum/v1"
HANDOFF_SCHEMA = "athena.w23-promotion-execution-handoff/v1"
AUTHORIZATION_SCHEMA = "athena.w23-promotion-execution-authorization/v1"

W22_HEAD = "aa8c382419fd093507f3059751a75dc14ffa8662"
W22_TREE = "5ef64cc1a120542fc5997fe1ee0e860edc0f020c"
W22_PARENT = "929cfe6762a989f9595551d654b94ecc01320910"
W22_CONTRACT = (
    "sha256:d826fa73b55d4bd93dbb251d12147de40a530c9e89413f9ef9730341d13a7a02"
)
W22_RECEIPT = (
    "w22-independent-return:sha256:"
    "3500942ce1d6659f5f4d11bbf3f4a777ea3b2dc6994dae3d9033a7bdd8b35e04"
)
W22_LOCAL_IMAGE = (
    "sha256:485381472ad090768cf6033072a5617f09a9b3d1bd820a1be47dc5e244e1831d"
)
W22_CONTROL_HEAD = "754e90aa67714e3ae3cd7ad107ffd8b3aed40b67"
W22_CONTROL_RECEIPT = (
    "w22-control-admission:sha256:"
    "a477c25821788c72c843e539c51624e781d6c79a449f6aa8c28b65cb4dbb7290"
)
CANONICAL_REGISTRY_NAMESPACE = "ghcr.io/demeet2k/athena-mcp"

ROLES = {
    "FRESHNESS_ISSUER": "promotion.challenge",
    "PROMOTION_POLICY_A": "promotion.policy.a",
    "PROMOTION_POLICY_B": "promotion.policy.b",
    "ARTIFACT_PUBLISHER": "artifact.publish",
    "ARTIFACT_OBSERVER": "artifact.observe",
    "EXECUTION_AUTHORIZER": "promotion.execute.authorize",
}
DECISIONS = {"AUTHORIZE_PROMOTION", "HOLD_PROMOTION"}
COMMIT_VALUE = re.compile(r"^[0-9a-f]{40}$")

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
CUSTODY_FIELDS = {
    "w22_head",
    "w22_tree",
    "w22_sole_parent",
    "w22_contract_digest",
    "w22_receipt_id",
}
TARGET_FIELDS = {
    "runtime_repository",
    "runtime_head",
    "published_image_digest",
    "target_environment",
    "target_ref",
}
CHALLENGE_FIELDS = {
    "schema",
    "custody",
    "source_digest",
    "revision_digest",
    "challenge_id",
    "nonce",
    "target",
    "issued_at",
    "expires_at",
    "policy_digest",
    "signature",
    "challenge_digest",
}
PUBLICATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "challenge_digest",
    "target",
    "registry",
    "immutable_reference",
    "manifest_digest",
    "published_at",
    "signature",
    "proof_digest",
}
OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "challenge_digest",
    "publication_proof_digest",
    "registry",
    "immutable_reference",
    "manifest_digest",
    "registry_response_digest",
    "observed_at",
    "signature",
    "observation_digest",
}
DECISION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "challenge_digest",
    "publication_proof_digest",
    "publication_observation_digest",
    "w22_commit_return_digest",
    "w22_git_observation_digest",
    "w22_commit_return",
    "w22_git_observation",
    "target",
    "decision",
    "decided_at",
    "reason_code",
    "signature",
    "decision_digest",
}
AUTHORIZATION_FIELDS = {
    "schema",
    "custody",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "challenge_digest",
    "publication_proof_digest",
    "publication_observation_digest",
    "policy_a_decision_digest",
    "policy_b_decision_digest",
    "quorum_certificate_digest",
    "target",
    "authorized_at",
    "execution_expires_at",
    "nonce",
    "constraints",
    "signature",
    "authorization_digest",
}
CONSTRAINT_FIELDS = {
    "published_artifact_required",
    "two_policy_authorities_required",
    "hold_dominates",
    "freshness_required",
    "execution_receipt_required",
    "runtime_can_execute",
}


class PromotionExecutionHandoffError(RuntimeError):
    """Frozen W23 contract or authority registry is invalid."""


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
    if normalized["governance_repository"] != "demeet2k/Athena":
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
    if (
        normalized["repository"] != "demeet2k/Athena"
        or not normalized["ref"].startswith("refs/heads/authority-")
        or not normalized["path"].startswith(".athena/authorities/")
        or ".." in normalized["path"]
    ):
        raise ValueError("authority revision governance coordinates mismatch")
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


def _custody(value: Any) -> dict[str, Any]:
    raw = _exact(value, CUSTODY_FIELDS, "custody")
    result = {
        "w22_head": _commit(raw["w22_head"], "custody.w22_head"),
        "w22_tree": _commit(raw["w22_tree"], "custody.w22_tree"),
        "w22_sole_parent": _commit(
            raw["w22_sole_parent"], "custody.w22_sole_parent"
        ),
        "w22_contract_digest": _sha(
            raw["w22_contract_digest"], "custody.w22_contract_digest"
        ),
        "w22_receipt_id": _text(
            raw["w22_receipt_id"], "custody.w22_receipt_id", limit=128
        ),
    }
    if result != {
        "w22_head": W22_HEAD,
        "w22_tree": W22_TREE,
        "w22_sole_parent": W22_PARENT,
        "w22_contract_digest": W22_CONTRACT,
        "w22_receipt_id": W22_RECEIPT,
    }:
        raise ValueError("custody does not bind exact W22")
    return result


def _target(value: Any) -> dict[str, Any]:
    raw = _exact(value, TARGET_FIELDS, "target")
    result = {
        "runtime_repository": _text(
            raw["runtime_repository"], "target.runtime_repository"
        ),
        "runtime_head": _commit(raw["runtime_head"], "target.runtime_head"),
        "published_image_digest": _sha(
            raw["published_image_digest"], "target.published_image_digest"
        ),
        "target_environment": _identifier(
            raw["target_environment"], "target.target_environment"
        ),
        "target_ref": _text(raw["target_ref"], "target.target_ref"),
    }
    if (
        result["runtime_repository"] != "demeet2k/athena-mcp-server"
        or result["runtime_head"] != W22_HEAD
        or result["target_environment"] != "kc144-production"
        or result["target_ref"] != "refs/heads/production"
    ):
        raise ValueError("target must bind exact W22 runtime")
    if result["published_image_digest"] == W22_LOCAL_IMAGE:
        raise ValueError("workflow-local unpublished W22 image cannot execute")
    return result


def _verify(
    record: dict[str, Any],
    revision: dict[str, Any],
    digest_field: str,
    occurred_at: str,
) -> None:
    signature = _signature(record["signature"], "signature")
    if signature["key_id"] != revision["key_id"]:
        raise ValueError("signature key ID mismatch")
    when = _timestamp(occurred_at, "occurrence time")
    if not (
        _timestamp(revision["valid_from"], "revision.valid_from")
        <= when
        <= _timestamp(revision["valid_until"], "revision.valid_until")
    ):
        raise ValueError("revision not valid at occurrence")
    if not _verify_ed25519_signature(
        revision["public_key_base64"],
        signature["value"],
        _signed(record, digest_field),
    ):
        raise ValueError("signature mismatch")
    if record[digest_field] != _digest(_addressed(record, digest_field)):
        raise ValueError(f"{digest_field} mismatch")


def _negative() -> dict[str, bool]:
    return {
        "runtime_mutated_registry": False,
        "runtime_published_artifact": False,
        "runtime_issued_authority_signature": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "execution_observed": False,
        "promotion_executed": False,
        "deployment_claimed": False,
        "merge_claimed": False,
        "promotion_claimed": False,
    }


class FrozenPromotionExecutionHandoff:
    """Frozen authority-empty W23 verifier."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w22_gate: FrozenIndependentAuthorityReturn,
    ):
        self.snapshot = deepcopy(snapshot)
        self.w22_gate = w22_gate
        try:
            self._validate_snapshot()
        except PromotionExecutionHandoffError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise PromotionExecutionHandoffError(str(error)) from error

    @classmethod
    def load(cls) -> "FrozenPromotionExecutionHandoff":
        return cls(
            _strict_loads(DATA_PATH.read_text(encoding="utf-8")),
            FrozenIndependentAuthorityReturn.load(),
        )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w22_gate: FrozenIndependentAuthorityReturn | None = None,
    ) -> "FrozenPromotionExecutionHandoff":
        return cls(
            snapshot,
            w22_gate
            if w22_gate is not None
            else FrozenIndependentAuthorityReturn.load(),
        )

    def _validate_snapshot(self) -> None:
        expected_top_level = {
            "schema",
            "phase",
            "predecessor",
            "control_predecessor_observation",
            "w22_control_protocol_observation",
            "execution_contract",
            "authority_registry",
            "freshness_challenge_ledger",
            "publication_proof_ledger",
            "execution_authorization_ledger",
            "boundaries",
            "successor",
            "contract_digest",
        }
        if set(self.snapshot) != expected_top_level:
            raise PromotionExecutionHandoffError("W23 top-level shape mismatch")
        if self.snapshot.get("schema") != SCHEMA or self.snapshot.get("phase") != PHASE:
            raise PromotionExecutionHandoffError("W23 schema/phase mismatch")
        predecessor = {
            "runtime_repository": "demeet2k/athena-mcp-server",
            "runtime_pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w22_head": W22_HEAD,
            "w22_tree": W22_TREE,
            "w22_sole_parent": W22_PARENT,
            "w22_contract_digest": W22_CONTRACT,
            "w22_receipt_id": W22_RECEIPT,
            "w22_p07_run_id": 30299076295,
            "w22_p08_run_id": 30299076622,
            "w22_stdio_receipt_id": (
                "mcp-host:sha256:"
                "96b616d064712bfb4dbed958325eabe7c6865a0f5f763d8de2807f6a9505b35e"
            ),
            "w22_candidate_receipt_id": (
                "p08-candidate:sha256:"
                "efbea5248e35e4a3342480cb830bd8a3dbb696e89dc245ad0c3e8ff8fd8d9f9c"
            ),
            "w22_workflow_local_image_id": W22_LOCAL_IMAGE,
            "w22_image_published": False,
            "w22_artifact_id": 8665844055,
            "w22_artifact_digest": (
                "sha256:"
                "9e4f886066b5c66d9a433f2ad80d4a65b1bd6bb5d29f0465fb784b70dd99b17b"
            ),
        }
        if self.snapshot["predecessor"] != predecessor:
            raise PromotionExecutionHandoffError("W22 predecessor mismatch")
        if self.snapshot["control_predecessor_observation"] != {
            "repository": "demeet2k/Athena",
            "pull_request": 18,
            "branch": "agent/w21-admit-ledger-commit-promotion-handoff",
            "head": "b74bb6caea37569bc2c050c060bcc35641dd068e",
            "base": "78bfbbbfc41cfc402235793afdcd5b190e71ba5b",
            "receipt_id": (
                "w21-control-admission:sha256:"
                "78742031032e1f01a35b8ea711280b0069d8d5bfff71d59cfe517734195fc0fc"
            ),
            "grants_production_authority": False,
            "hosted_runner_status": "HOLD[PLATFORM_OBSTRUCTION_BEFORE_FIRST_STEP]",
        }:
            raise PromotionExecutionHandoffError("control observation mismatch")
        if self.snapshot["w22_control_protocol_observation"] != {
            "repository": "demeet2k/Athena",
            "pull_request": 20,
            "branch": "agent/w22-admit-independent-authority-return",
            "head": W22_CONTROL_HEAD,
            "base": "b74bb6caea37569bc2c050c060bcc35641dd068e",
            "receipt_id": W22_CONTROL_RECEIPT,
            "protocol_admission_observed": True,
            "grants_production_authority": False,
            "hosted_runner_status": "HOLD[PLATFORM_OBSTRUCTION_BEFORE_FIRST_STEP]",
        }:
            raise PromotionExecutionHandoffError(
                "W22 control protocol observation mismatch"
            )
        if self.snapshot["execution_contract"] != {
            "authority_source_schema": SOURCE_SCHEMA,
            "authority_revision_schema": REVISION_SCHEMA,
            "freshness_challenge_schema": CHALLENGE_SCHEMA,
            "publication_proof_schema": PUBLICATION_SCHEMA,
            "publication_observation_schema": OBSERVATION_SCHEMA,
            "promotion_policy_decision_schema": DECISION_SCHEMA,
            "quorum_certificate_schema": QUORUM_SCHEMA,
            "execution_handoff_schema": HANDOFF_SCHEMA,
            "execution_authorization_schema": AUTHORIZATION_SCHEMA,
            "roles": list(ROLES),
            "required_promotion_policy_quorum": "2_OF_2",
            "hold_dominates": True,
            "freshness_challenge_required": True,
            "independent_publication_observation_required": True,
            "w22_signed_return_evidence_required": True,
            "w22_control_protocol_admission_pinned": True,
            "canonical_registry_namespace": CANONICAL_REGISTRY_NAMESPACE,
            "authorization_template_must_follow_policy_decisions": True,
            "successor_must_enforce_authorization_expiry_and_replay": True,
            "unpublished_target_execution_allowed": False,
            "workflow_local_image_is_publication_proof": False,
            "self_supplied_sources_revisions_or_keys_allowed": False,
            "cross_role_identity_or_key_overlap_allowed": False,
            "runtime_can_publish": False,
            "runtime_can_authorize_execution": False,
            "runtime_can_execute_or_promote": False,
        }:
            raise PromotionExecutionHandoffError("W23 execution contract drift")
        registry = self.snapshot["authority_registry"]
        if set(registry) != {"sources", "revisions"}:
            raise PromotionExecutionHandoffError("authority registry shape mismatch")
        if not isinstance(registry["sources"], list) or not isinstance(
            registry["revisions"], list
        ):
            raise PromotionExecutionHandoffError(
                "authority registry coordinates must be arrays"
            )
        self.sources: dict[str, dict[str, Any]] = {}
        self.revisions: dict[str, dict[str, Any]] = {}
        identity_roles: dict[str, str] = {}
        source_tips: dict[str, str] = {}
        aliases: dict[str, str] = {}
        for raw in registry["sources"]:
            source = _source(raw)
            if source["source_digest"] in self.sources:
                raise PromotionExecutionHandoffError("duplicate authority source")
            prior = identity_roles.get(source["authority_id"])
            if prior is not None and prior != source["role"]:
                raise PromotionExecutionHandoffError(
                    "authority identity overlaps roles"
                )
            identity_roles[source["authority_id"]] = source["role"]
            self.sources[source["source_digest"]] = source
        for raw in registry["revisions"]:
            revision = _revision(raw)
            source = self.sources.get(revision["source_digest"])
            if source is None or source["role"] != revision["role"]:
                raise PromotionExecutionHandoffError(
                    "revision source unpinned or role-mismatched"
                )
            if revision["repository"] != source["governance_repository"]:
                raise PromotionExecutionHandoffError(
                    "revision governance repository does not bind source"
                )
            if revision["revision_digest"] in self.revisions:
                raise PromotionExecutionHandoffError("duplicate authority revision")
            if revision["parent_revision_digest"] != source_tips.get(
                revision["source_digest"]
            ):
                raise PromotionExecutionHandoffError(
                    "authority revision chain is not append-only"
                )
            source_tips[revision["source_digest"]] = revision["revision_digest"]
            for label, value in (
                ("key_id", revision["key_id"]),
                ("public_key", revision["public_key_base64"]),
                ("fingerprint", revision["fingerprint"]),
            ):
                alias = f"{label}:{value}"
                prior_role = aliases.get(alias)
                if prior_role is not None and prior_role != revision["role"]:
                    raise PromotionExecutionHandoffError(
                        f"{label} overlaps roles"
                    )
                aliases[alias] = revision["role"]
            self.revisions[revision["revision_digest"]] = revision
        for name in (
            "freshness_challenge_ledger",
            "publication_proof_ledger",
            "execution_authorization_ledger",
        ):
            if self.snapshot.get(name) != []:
                raise PromotionExecutionHandoffError(
                    f"checked-in production {name} must remain empty"
                )
        expected_boundaries = {
            "w22_custody_pinned": True,
            "w22_image_published": False,
            "w22_control_protocol_admitted": True,
            "w22_control_receipt_grants_production_authority": False,
            "production_authority_source_count": len(self.sources),
            "production_authority_revision_count": len(self.revisions),
            "freshness_challenge_returned": False,
            "artifact_publication_proved": False,
            "artifact_publication_observed": False,
            "w22_signed_return_evidence_verified": False,
            "promotion_policy_a_returned": False,
            "promotion_policy_b_returned": False,
            "promotion_quorum_satisfied": False,
            "promotion_hold_active": True,
            "execution_handoff_compiled": False,
            "execution_authorized": False,
            "execution_observed": False,
            "promotion_executed": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if self.snapshot["boundaries"] != expected_boundaries:
            raise PromotionExecutionHandoffError("W23 boundary drift")
        if self.snapshot["successor"] != (
            "KC144.XNAV.W24::RETURN-OBSERVED-PROMOTION-EXECUTION-"
            "DEPLOYMENT-AND-ROLLBACK-READBACK"
        ):
            raise PromotionExecutionHandoffError("W23 successor drift")
        expected = _digest(
            {
                key: value
                for key, value in self.snapshot.items()
                if key != "contract_digest"
            }
        )
        if self.snapshot.get("contract_digest") != expected:
            raise PromotionExecutionHandoffError("W23 contract digest mismatch")

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
        operation: str,
        target: dict[str, Any],
        policy_digest: str,
    ) -> None:
        scope = revision["scope"]
        if (
            scope["operation"] != operation
            or scope["repository"] != target["runtime_repository"]
            or scope["ref"] != target["target_ref"]
            or scope["environment"] != target["target_environment"]
            or scope["policy_digest"] != policy_digest
        ):
            raise ValueError("occurrence outside authority scope")

    def _hold(self, status: str, error: Exception | str) -> dict[str, Any]:
        return _merge(
            {
                "status": status,
                "error": str(error),
                "freshness_challenge_verified": False,
                "artifact_publication_proved": False,
                "artifact_publication_observed": False,
                "w22_signed_return_evidence_verified": False,
                "promotion_policy_a_verified": False,
                "promotion_policy_b_verified": False,
                "promotion_quorum_satisfied": False,
                "promotion_hold_active": True,
                "execution_handoff_compiled": False,
                "execution_authorized": False,
            },
            _negative(),
        )

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W23_W22_CUSTODY_PINNED__FRESHNESS_PUBLICATION_"
                    "TWO_POLICY_QUORUM_AND_EXECUTION_AUTHORITY_OPEN"
                ),
                "phase": PHASE,
                "w22_head": W22_HEAD,
                "w22_tree": W22_TREE,
                "w22_contract_digest": W22_CONTRACT,
                "w22_receipt_id": W22_RECEIPT,
                "w22_workflow_local_image_id": W22_LOCAL_IMAGE,
                "w22_image_published": False,
                "w22_control_head": W22_CONTROL_HEAD,
                "w22_control_receipt_id": W22_CONTROL_RECEIPT,
                "w22_control_protocol_admitted": True,
                "w22_control_receipt_grants_production_authority": False,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "freshness_challenge_count": 0,
                "publication_proof_count": 0,
                "execution_authorization_count": 0,
                "freshness_challenge_verified": False,
                "artifact_publication_proved": False,
                "artifact_publication_observed": False,
                "w22_signed_return_evidence_verified": False,
                "promotion_policy_a_verified": False,
                "promotion_policy_b_verified": False,
                "promotion_quorum_satisfied": False,
                "promotion_hold_active": True,
                "execution_handoff_compiled": False,
                "execution_authorized": False,
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
                source["source_digest"],
                _sha(revision_digest, "revision_digest"),
                source["role"],
            )
            return _merge(
                {
                    "status": "PASS_W23_AUTHORITY_SOURCE_REVISION_PINNED",
                    "source": deepcopy(source),
                    "revision": deepcopy(revision),
                    "source_is_revision": False,
                    "revision_is_occurrence": False,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W23_AUTHORITY_COORDINATE_UNPINNED", error)

    def _challenge(self, text: str) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(_strict_loads(text), CHALLENGE_FIELDS, "freshness challenge")
        challenge = deepcopy(raw)
        if challenge["schema"] != CHALLENGE_SCHEMA:
            raise ValueError("freshness challenge schema mismatch")
        challenge["custody"] = _custody(challenge["custody"])
        for field in (
            "source_digest",
            "revision_digest",
            "policy_digest",
            "challenge_digest",
        ):
            challenge[field] = _sha(challenge[field], f"challenge.{field}")
        challenge["challenge_id"] = _identifier(
            challenge["challenge_id"], "challenge.challenge_id"
        )
        challenge["nonce"] = _identifier(
            challenge["nonce"], "challenge.nonce"
        )
        challenge["target"] = _target(challenge["target"])
        challenge["signature"] = _signature(
            challenge["signature"], "challenge.signature"
        )
        issued = _timestamp(challenge["issued_at"], "challenge.issued_at")
        expires = _timestamp(challenge["expires_at"], "challenge.expires_at")
        if issued >= expires or (expires - issued).total_seconds() > 3600:
            raise ValueError("freshness challenge window must be 1..3600 seconds")
        _, revision = self._authority(
            challenge["source_digest"],
            challenge["revision_digest"],
            "FRESHNESS_ISSUER",
        )
        self._scope(
            revision,
            operation="promotion.challenge",
            target=challenge["target"],
            policy_digest=challenge["policy_digest"],
        )
        _verify(
            challenge, revision, "challenge_digest", challenge["issued_at"]
        )
        return challenge, revision

    def inspect_freshness_challenge(self, challenge_json: str) -> dict[str, Any]:
        try:
            challenge, _ = self._challenge(challenge_json)
            return _merge(
                {
                    "status": "PASS_W23_FRESHNESS_CHALLENGE_VERIFIED",
                    "challenge_digest": challenge["challenge_digest"],
                    "target": challenge["target"],
                    "issued_at": challenge["issued_at"],
                    "expires_at": challenge["expires_at"],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": False,
                    "artifact_publication_observed": False,
                    "promotion_policy_a_verified": False,
                    "promotion_policy_b_verified": False,
                    "promotion_quorum_satisfied": False,
                    "promotion_hold_active": True,
                    "execution_handoff_compiled": False,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W23_FRESHNESS_CHALLENGE_REJECTED", error)

    def _publication(
        self, text: str, challenge: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(_strict_loads(text), PUBLICATION_FIELDS, "publication proof")
        proof = deepcopy(raw)
        if proof["schema"] != PUBLICATION_SCHEMA:
            raise ValueError("publication proof schema mismatch")
        for field in (
            "source_digest",
            "revision_digest",
            "challenge_digest",
            "manifest_digest",
            "proof_digest",
        ):
            proof[field] = _sha(proof[field], f"publication.{field}")
        proof["occurrence_id"] = _identifier(
            proof["occurrence_id"], "publication.occurrence_id"
        )
        proof["target"] = _target(proof["target"])
        for field in ("registry", "immutable_reference"):
            proof[field] = _text(proof[field], f"publication.{field}")
        proof["signature"] = _signature(
            proof["signature"], "publication.signature"
        )
        if (
            proof["challenge_digest"] != challenge["challenge_digest"]
            or proof["target"] != challenge["target"]
            or proof["manifest_digest"]
            != proof["target"]["published_image_digest"]
        ):
            raise ValueError("publication proof does not bind challenge target")
        expected_reference = (
            CANONICAL_REGISTRY_NAMESPACE + "@" + proof["manifest_digest"]
        )
        if (
            proof["registry"] != "ghcr.io"
            or proof["immutable_reference"] != expected_reference
        ):
            raise ValueError("publication proof lacks immutable registry reference")
        published = _timestamp(proof["published_at"], "publication.published_at")
        if not (
            _timestamp(challenge["issued_at"], "challenge.issued_at")
            <= published
            <= _timestamp(challenge["expires_at"], "challenge.expires_at")
        ):
            raise ValueError("publication proof outside freshness window")
        _, revision = self._authority(
            proof["source_digest"], proof["revision_digest"], "ARTIFACT_PUBLISHER"
        )
        self._scope(
            revision,
            operation="artifact.publish",
            target=proof["target"],
            policy_digest=challenge["policy_digest"],
        )
        _verify(proof, revision, "proof_digest", proof["published_at"])
        return proof, revision

    def inspect_publication_proof(
        self, challenge_json: str, publication_json: str
    ) -> dict[str, Any]:
        try:
            challenge, _ = self._challenge(challenge_json)
            proof, _ = self._publication(publication_json, challenge)
            return _merge(
                {
                    "status": (
                        "PASS_W23_ARTIFACT_PUBLICATION_PROOF_VERIFIED__"
                        "INDEPENDENT_OBSERVATION_OPEN"
                    ),
                    "challenge_digest": challenge["challenge_digest"],
                    "publication_proof_digest": proof["proof_digest"],
                    "immutable_reference": proof["immutable_reference"],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": False,
                    "promotion_policy_a_verified": False,
                    "promotion_policy_b_verified": False,
                    "promotion_quorum_satisfied": False,
                    "promotion_hold_active": True,
                    "execution_handoff_compiled": False,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W23_PUBLICATION_PROOF_REJECTED", error)

    def _observation(
        self,
        text: str,
        challenge: dict[str, Any],
        proof: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(
            _strict_loads(text), OBSERVATION_FIELDS, "publication observation"
        )
        observation = deepcopy(raw)
        if observation["schema"] != OBSERVATION_SCHEMA:
            raise ValueError("publication observation schema mismatch")
        for field in (
            "source_digest",
            "revision_digest",
            "challenge_digest",
            "publication_proof_digest",
            "manifest_digest",
            "registry_response_digest",
            "observation_digest",
        ):
            observation[field] = _sha(
                observation[field], f"observation.{field}"
            )
        observation["occurrence_id"] = _identifier(
            observation["occurrence_id"], "observation.occurrence_id"
        )
        for field in ("registry", "immutable_reference"):
            observation[field] = _text(
                observation[field], f"observation.{field}"
            )
        observation["signature"] = _signature(
            observation["signature"], "observation.signature"
        )
        expected = {
            "challenge_digest": challenge["challenge_digest"],
            "publication_proof_digest": proof["proof_digest"],
            "registry": proof["registry"],
            "immutable_reference": proof["immutable_reference"],
            "manifest_digest": proof["manifest_digest"],
        }
        for field, value in expected.items():
            if observation[field] != value:
                raise ValueError(f"observation does not bind {field}")
        observed = _timestamp(
            observation["observed_at"], "observation.observed_at"
        )
        if not (
            _timestamp(proof["published_at"], "publication.published_at")
            <= observed
            <= _timestamp(challenge["expires_at"], "challenge.expires_at")
        ):
            raise ValueError("publication observation outside freshness window")
        _, revision = self._authority(
            observation["source_digest"],
            observation["revision_digest"],
            "ARTIFACT_OBSERVER",
        )
        self._scope(
            revision,
            operation="artifact.observe",
            target=proof["target"],
            policy_digest=challenge["policy_digest"],
        )
        _verify(
            observation,
            revision,
            "observation_digest",
            observation["observed_at"],
        )
        return observation, revision

    def inspect_publication_observation(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
    ) -> dict[str, Any]:
        try:
            challenge, _ = self._challenge(challenge_json)
            proof, publisher = self._publication(publication_json, challenge)
            observation, observer = self._observation(
                observation_json, challenge, proof
            )
            if publisher["fingerprint"] == observer["fingerprint"]:
                raise ValueError("publisher and observer are not independent")
            return _merge(
                {
                    "status": (
                        "PASS_W23_ARTIFACT_PUBLICATION_INDEPENDENTLY_OBSERVED__"
                        "POLICY_QUORUM_OPEN"
                    ),
                    "challenge_digest": challenge["challenge_digest"],
                    "publication_proof_digest": proof["proof_digest"],
                    "publication_observation_digest": observation[
                        "observation_digest"
                    ],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": True,
                    "promotion_policy_a_verified": False,
                    "promotion_policy_b_verified": False,
                    "promotion_quorum_satisfied": False,
                    "promotion_hold_active": True,
                    "execution_handoff_compiled": False,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold(
                "HOLD_W23_PUBLICATION_OBSERVATION_REJECTED", error
            )

    def _decision(
        self,
        text: str,
        challenge: dict[str, Any],
        proof: dict[str, Any],
        observation: dict[str, Any],
        role: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(_strict_loads(text), DECISION_FIELDS, "policy decision")
        decision = deepcopy(raw)
        if decision["schema"] != DECISION_SCHEMA:
            raise ValueError("policy decision schema mismatch")
        for field in (
            "source_digest",
            "revision_digest",
            "challenge_digest",
            "publication_proof_digest",
            "publication_observation_digest",
            "w22_commit_return_digest",
            "w22_git_observation_digest",
            "decision_digest",
        ):
            decision[field] = _sha(decision[field], f"decision.{field}")
        decision["occurrence_id"] = _identifier(
            decision["occurrence_id"], "decision.occurrence_id"
        )
        decision["target"] = _target(decision["target"])
        decision["decision"] = _text(decision["decision"], "decision.decision")
        if decision["decision"] not in DECISIONS:
            raise ValueError("unknown promotion policy decision")
        decision["reason_code"] = _identifier(
            decision["reason_code"], "decision.reason_code"
        )
        decision["signature"] = _signature(
            decision["signature"], "decision.signature"
        )
        commit_result = self.w22_gate.inspect_ledger_commit_return(
            json.dumps(
                decision["w22_commit_return"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            json.dumps(
                decision["w22_git_observation"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
        if not (
            commit_result.get("ledger_commit_return_verified")
            and commit_result.get("git_commit_observed")
            and commit_result.get("ledger_entry_committed")
        ):
            raise ValueError(
                "policy decision W22 signed return evidence is not verified"
            )
        w22_commit, _ = self.w22_gate._commit_return(
            json.dumps(
                decision["w22_commit_return"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        w22_observation, _ = self.w22_gate._observation(
            json.dumps(
                decision["w22_git_observation"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            w22_commit,
        )
        decision["w22_commit_return"] = w22_commit
        decision["w22_git_observation"] = w22_observation
        if (
            decision["w22_commit_return_digest"]
            != w22_commit["return_digest"]
            or decision["w22_git_observation_digest"]
            != w22_observation["observation_digest"]
        ):
            raise ValueError(
                "policy decision does not bind verified W22 return evidence"
            )
        expected = {
            "challenge_digest": challenge["challenge_digest"],
            "publication_proof_digest": proof["proof_digest"],
            "publication_observation_digest": observation[
                "observation_digest"
            ],
            "target": challenge["target"],
        }
        for field, value in expected.items():
            if decision[field] != value:
                raise ValueError(f"policy decision does not bind {field}")
        decided = _timestamp(decision["decided_at"], "decision.decided_at")
        if not (
            _timestamp(observation["observed_at"], "observation.observed_at")
            <= decided
            <= _timestamp(challenge["expires_at"], "challenge.expires_at")
        ):
            raise ValueError("policy decision outside freshness window")
        _, revision = self._authority(
            decision["source_digest"], decision["revision_digest"], role
        )
        self._scope(
            revision,
            operation=ROLES[role],
            target=decision["target"],
            policy_digest=challenge["policy_digest"],
        )
        _verify(
            decision, revision, "decision_digest", decision["decided_at"]
        )
        return decision, revision

    def inspect_policy_decision(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        decision_json: str,
        policy_role: str,
    ) -> dict[str, Any]:
        try:
            if policy_role not in {"PROMOTION_POLICY_A", "PROMOTION_POLICY_B"}:
                raise ValueError("policy role must be PROMOTION_POLICY_A or B")
            challenge, _ = self._challenge(challenge_json)
            proof, _ = self._publication(publication_json, challenge)
            observation, _ = self._observation(
                observation_json, challenge, proof
            )
            decision, _ = self._decision(
                decision_json, challenge, proof, observation, policy_role
            )
            authorized = decision["decision"] == "AUTHORIZE_PROMOTION"
            return _merge(
                {
                    "status": (
                        f"PASS_W23_{policy_role}_DECISION_VERIFIED__"
                        + ("AUTHORIZE" if authorized else "HOLD")
                    ),
                    "policy_role": policy_role,
                    "decision": decision["decision"],
                    "decision_digest": decision["decision_digest"],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": True,
                    "w22_signed_return_evidence_verified": True,
                    "promotion_policy_a_verified": (
                        policy_role == "PROMOTION_POLICY_A"
                    ),
                    "promotion_policy_b_verified": (
                        policy_role == "PROMOTION_POLICY_B"
                    ),
                    "promotion_quorum_satisfied": False,
                    "promotion_hold_active": not authorized,
                    "execution_handoff_compiled": False,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W23_POLICY_DECISION_REJECTED", error)

    def _quorum(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
        dict[str, Any],
    ]:
        challenge, _ = self._challenge(challenge_json)
        proof, publisher = self._publication(publication_json, challenge)
        observation, observer = self._observation(
            observation_json, challenge, proof
        )
        policy_a, revision_a = self._decision(
            policy_a_json,
            challenge,
            proof,
            observation,
            "PROMOTION_POLICY_A",
        )
        policy_b, revision_b = self._decision(
            policy_b_json,
            challenge,
            proof,
            observation,
            "PROMOTION_POLICY_B",
        )
        for field in (
            "w22_commit_return_digest",
            "w22_git_observation_digest",
        ):
            if policy_a[field] != policy_b[field]:
                raise ValueError(
                    f"promotion-policy authorities disagree on {field}"
                )
        if (
            policy_a["w22_commit_return"] != policy_b["w22_commit_return"]
            or policy_a["w22_git_observation"]
            != policy_b["w22_git_observation"]
        ):
            raise ValueError(
                "promotion-policy authorities disagree on W22 return evidence"
            )
        occurrence_ids = {
            proof["occurrence_id"],
            observation["occurrence_id"],
            policy_a["occurrence_id"],
            policy_b["occurrence_id"],
        }
        if len(occurrence_ids) != 4:
            raise ValueError("publication and policy occurrence axes overlap")
        fingerprints = {
            publisher["fingerprint"],
            observer["fingerprint"],
            revision_a["fingerprint"],
            revision_b["fingerprint"],
        }
        if len(fingerprints) != 4:
            raise ValueError("publication/policy roles are not independent")
        return challenge, proof, observation, policy_a, policy_b

    def evaluate_quorum(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
    ) -> dict[str, Any]:
        try:
            challenge, proof, observation, policy_a, policy_b = self._quorum(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
            )
            held = "HOLD_PROMOTION" in {
                policy_a["decision"],
                policy_b["decision"],
            }
            satisfied = not held and {
                policy_a["decision"],
                policy_b["decision"],
            } == {"AUTHORIZE_PROMOTION"}
            certificate = {
                "schema": QUORUM_SCHEMA,
                "challenge_digest": challenge["challenge_digest"],
                "publication_proof_digest": proof["proof_digest"],
                "publication_observation_digest": observation[
                    "observation_digest"
                ],
                "policy_a_decision_digest": policy_a["decision_digest"],
                "policy_b_decision_digest": policy_b["decision_digest"],
                "target": challenge["target"],
                "required_quorum": "2_OF_2",
                "hold_dominates": True,
                "quorum_satisfied": satisfied,
                "hold_active": held,
                "certificate_digest": "",
            }
            certificate["certificate_digest"] = _digest(
                _addressed(certificate, "certificate_digest")
            )
            status = (
                "PASS_W23_TWO_POLICY_QUORUM_SATISFIED__"
                "EXECUTION_AUTHORITY_RETURN_OPEN"
                if satisfied
                else "PASS_W23_POLICY_RETURNS_VERIFIED__"
                "HOLD_DOMINATES__EXECUTION_FORBIDDEN"
            )
            return _merge(
                {
                    "status": status,
                    "quorum_certificate": certificate,
                    "challenge_digest": challenge["challenge_digest"],
                    "publication_proof_digest": proof["proof_digest"],
                    "publication_observation_digest": observation[
                        "observation_digest"
                    ],
                    "policy_a_decision_digest": policy_a["decision_digest"],
                    "policy_b_decision_digest": policy_b["decision_digest"],
                    "target": challenge["target"],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": True,
                    "w22_signed_return_evidence_verified": True,
                    "promotion_policy_a_verified": True,
                    "promotion_policy_b_verified": True,
                    "promotion_quorum_satisfied": satisfied,
                    "promotion_hold_active": held,
                    "execution_handoff_compiled": False,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W23_POLICY_QUORUM_REJECTED", error)

    def compile_execution_handoff(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_source_digest: str,
        execution_revision_digest: str,
        authorized_at: str,
        execution_expires_at: str,
        nonce: str,
    ) -> dict[str, Any]:
        quorum = self.evaluate_quorum(
            challenge_json,
            publication_json,
            observation_json,
            policy_a_json,
            policy_b_json,
        )
        if not quorum.get("promotion_quorum_satisfied"):
            return quorum
        try:
            challenge, _ = self._challenge(challenge_json)
            _, _, _, policy_a, policy_b = self._quorum(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
            )
            _, revision = self._authority(
                _sha(execution_source_digest, "execution_source_digest"),
                _sha(execution_revision_digest, "execution_revision_digest"),
                "EXECUTION_AUTHORIZER",
            )
            self._scope(
                revision,
                operation="promotion.execute.authorize",
                target=challenge["target"],
                policy_digest=challenge["policy_digest"],
            )
            start = _timestamp(authorized_at, "authorized_at")
            end = _timestamp(execution_expires_at, "execution_expires_at")
            last_policy = max(
                _timestamp(policy_a["decided_at"], "policy_a.decided_at"),
                _timestamp(policy_b["decided_at"], "policy_b.decided_at"),
            )
            if not (
                last_policy <= start < end
                and end
                <= _timestamp(challenge["expires_at"], "challenge.expires_at")
                and _timestamp(revision["valid_from"], "revision.valid_from")
                <= start
                <= _timestamp(revision["valid_until"], "revision.valid_until")
            ):
                raise ValueError(
                    "execution authorization window predates policy or exceeds "
                    "challenge/authority validity"
                )
            template = {
                "schema": AUTHORIZATION_SCHEMA,
                "custody": _custody(challenge["custody"]),
                "source_digest": execution_source_digest,
                "revision_digest": execution_revision_digest,
                "occurrence_id": "REQUIRED",
                "challenge_digest": quorum["challenge_digest"],
                "publication_proof_digest": quorum["publication_proof_digest"],
                "publication_observation_digest": quorum[
                    "publication_observation_digest"
                ],
                "policy_a_decision_digest": quorum[
                    "policy_a_decision_digest"
                ],
                "policy_b_decision_digest": quorum[
                    "policy_b_decision_digest"
                ],
                "quorum_certificate_digest": quorum["quorum_certificate"][
                    "certificate_digest"
                ],
                "target": quorum["target"],
                "authorized_at": authorized_at,
                "execution_expires_at": execution_expires_at,
                "nonce": _identifier(nonce, "nonce"),
                "constraints": {
                    "published_artifact_required": True,
                    "two_policy_authorities_required": True,
                    "hold_dominates": True,
                    "freshness_required": True,
                    "execution_receipt_required": True,
                    "runtime_can_execute": False,
                },
                "signature": {
                    "key_id": revision["key_id"],
                    "value": "REQUIRED",
                },
                "authorization_digest": "RECOMPUTE_AFTER_SIGNATURE",
            }
            return _merge(
                {
                    "status": (
                        "PASS_W23_COORDINATE_SPECIFIC_EXECUTION_HANDOFF_"
                        "COMPILED__SIGNED_AUTHORITY_RETURN_OPEN"
                    ),
                    "handoff_template": template,
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": True,
                    "w22_signed_return_evidence_verified": True,
                    "promotion_policy_a_verified": True,
                    "promotion_policy_b_verified": True,
                    "promotion_quorum_satisfied": True,
                    "promotion_hold_active": False,
                    "execution_handoff_compiled": True,
                    "execution_authorized": False,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W23_EXECUTION_HANDOFF_REJECTED", error)

    def inspect_execution_authorization(
        self,
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        authorization_json: str,
    ) -> dict[str, Any]:
        quorum = self.evaluate_quorum(
            challenge_json,
            publication_json,
            observation_json,
            policy_a_json,
            policy_b_json,
        )
        if not quorum.get("promotion_quorum_satisfied"):
            return quorum
        try:
            challenge, _, _, policy_a, policy_b = self._quorum(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
            )
            authorization = deepcopy(
                _exact(
                    _strict_loads(authorization_json),
                    AUTHORIZATION_FIELDS,
                    "execution authorization",
                )
            )
            if authorization["schema"] != AUTHORIZATION_SCHEMA:
                raise ValueError("execution authorization schema mismatch")
            authorization["custody"] = _custody(authorization["custody"])
            for field in (
                "source_digest",
                "revision_digest",
                "challenge_digest",
                "publication_proof_digest",
                "publication_observation_digest",
                "policy_a_decision_digest",
                "policy_b_decision_digest",
                "quorum_certificate_digest",
                "authorization_digest",
            ):
                authorization[field] = _sha(
                    authorization[field], f"authorization.{field}"
                )
            authorization["occurrence_id"] = _identifier(
                authorization["occurrence_id"], "authorization.occurrence_id"
            )
            authorization["target"] = _target(authorization["target"])
            authorization["nonce"] = _identifier(
                authorization["nonce"], "authorization.nonce"
            )
            authorization["signature"] = _signature(
                authorization["signature"], "authorization.signature"
            )
            constraints = _exact(
                authorization["constraints"],
                CONSTRAINT_FIELDS,
                "authorization.constraints",
            )
            if constraints != {
                "published_artifact_required": True,
                "two_policy_authorities_required": True,
                "hold_dominates": True,
                "freshness_required": True,
                "execution_receipt_required": True,
                "runtime_can_execute": False,
            }:
                raise ValueError("execution constraints weakened")
            expected = {
                "challenge_digest": quorum["challenge_digest"],
                "publication_proof_digest": quorum["publication_proof_digest"],
                "publication_observation_digest": quorum[
                    "publication_observation_digest"
                ],
                "policy_a_decision_digest": policy_a["decision_digest"],
                "policy_b_decision_digest": policy_b["decision_digest"],
                "quorum_certificate_digest": quorum["quorum_certificate"][
                    "certificate_digest"
                ],
                "target": quorum["target"],
            }
            for field, value in expected.items():
                if authorization[field] != value:
                    raise ValueError(f"execution authorization does not bind {field}")
            authorized = _timestamp(
                authorization["authorized_at"], "authorization.authorized_at"
            )
            expires = _timestamp(
                authorization["execution_expires_at"],
                "authorization.execution_expires_at",
            )
            last_policy = max(
                _timestamp(policy_a["decided_at"], "policy_a.decided_at"),
                _timestamp(policy_b["decided_at"], "policy_b.decided_at"),
            )
            if not (
                last_policy
                <= authorized
                < expires
                <= _timestamp(challenge["expires_at"], "challenge.expires_at")
            ):
                raise ValueError("execution authorization outside freshness window")
            upstream_occurrences = {
                policy_a["occurrence_id"],
                policy_b["occurrence_id"],
            }
            _, proof, observation, _, _ = self._quorum(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
            )
            upstream_occurrences.update(
                {proof["occurrence_id"], observation["occurrence_id"]}
            )
            if authorization["occurrence_id"] in upstream_occurrences:
                raise ValueError(
                    "execution authorization occurrence axis overlaps evidence"
                )
            if authorization["nonce"] == challenge["nonce"]:
                raise ValueError(
                    "execution authorization nonce axis overlaps challenge"
                )
            _, revision = self._authority(
                authorization["source_digest"],
                authorization["revision_digest"],
                "EXECUTION_AUTHORIZER",
            )
            self._scope(
                revision,
                operation="promotion.execute.authorize",
                target=authorization["target"],
                policy_digest=challenge["policy_digest"],
            )
            _verify(
                authorization,
                revision,
                "authorization_digest",
                authorization["authorized_at"],
            )
            return _merge(
                {
                    "status": (
                        "PASS_W23_COORDINATE_SPECIFIC_EXECUTION_AUTHORIZATION_"
                        "VERIFIED__EXECUTION_OBSERVATION_AND_READBACK_OPEN"
                    ),
                    "authorization_digest": authorization[
                        "authorization_digest"
                    ],
                    "target": authorization["target"],
                    "execution_expires_at": authorization[
                        "execution_expires_at"
                    ],
                    "freshness_challenge_verified": True,
                    "artifact_publication_proved": True,
                    "artifact_publication_observed": True,
                    "w22_signed_return_evidence_verified": True,
                    "promotion_policy_a_verified": True,
                    "promotion_policy_b_verified": True,
                    "promotion_quorum_satisfied": True,
                    "promotion_hold_active": False,
                    "execution_handoff_compiled": True,
                    "execution_authorized": True,
                },
                _negative(),
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold(
                "HOLD_W23_EXECUTION_AUTHORIZATION_REJECTED", error
            )

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W23_EXECUTION_SEPARATION_LAW_EXPLAINED",
                "law": (
                    "CUSTODY != FRESHNESS != PUBLICATION != OBSERVATION != "
                    "POLICY QUORUM != EXECUTION AUTHORIZATION != EXECUTION "
                    "OCCURRENCE != READBACK"
                ),
                "required_roles": list(ROLES),
                "hold_dominates": True,
                "unpublished_target_execution_allowed": False,
                "w22_workflow_local_image_is_published": False,
                "w22_control_protocol_admitted": True,
                "w22_control_receipt_grants_production_authority": False,
                "w22_signed_return_evidence_required": True,
                "canonical_registry_namespace": CANONICAL_REGISTRY_NAMESPACE,
                "successor_must_enforce_authorization_expiry_and_replay": True,
                "execution_receipt_required": True,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_promotion_execution_handoff(mcp: Any) -> None:
    """Register twelve W23 tools and one frozen resource."""
    gate = FrozenPromotionExecutionHandoff.load()

    @mcp.tool()
    def athena_w23_promotion_execution_handoff_status() -> str:
        """Return W23 freshness, publication, quorum, and execution boundaries."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w23_w22_custody() -> str:
        """Inspect exact W22 custody; it grants no execution authority."""
        result = gate.status()
        result["status"] = "PASS_W23_W22_CUSTODY_PINNED__NO_AUTHORITY_GRANTED"
        return _render(result)

    @mcp.tool()
    def inspect_athena_w23_authority_source_revision(
        source_digest: str, revision_digest: str
    ) -> str:
        """Inspect one pinned execution-contract authority coordinate."""
        return _render(gate.inspect_source_revision(source_digest, revision_digest))

    @mcp.tool()
    def inspect_athena_w23_freshness_challenge(
        challenge_json: str,
    ) -> str:
        """Verify a signed, target-bound, expiring challenge."""
        return _render(gate.inspect_freshness_challenge(challenge_json))

    @mcp.tool()
    def inspect_athena_w23_artifact_publication_proof(
        challenge_json: str, publication_json: str
    ) -> str:
        """Verify publisher proof for an immutable registry digest."""
        return _render(
            gate.inspect_publication_proof(challenge_json, publication_json)
        )

    @mcp.tool()
    def inspect_athena_w23_artifact_publication_observation(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
    ) -> str:
        """Verify a disjoint observer's registry observation."""
        return _render(
            gate.inspect_publication_observation(
                challenge_json, publication_json, observation_json
            )
        )

    @mcp.tool()
    def inspect_athena_w23_promotion_policy_decision(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        decision_json: str,
        policy_role: str,
    ) -> str:
        """Verify policy A or B without treating one decision as quorum."""
        return _render(
            gate.inspect_policy_decision(
                challenge_json,
                publication_json,
                observation_json,
                decision_json,
                policy_role,
            )
        )

    @mcp.tool()
    def evaluate_athena_w23_two_policy_quorum(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
    ) -> str:
        """Evaluate 2-of-2 policy returns with HOLD dominance."""
        return _render(
            gate.evaluate_quorum(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
            )
        )

    @mcp.tool()
    def compile_athena_w23_execution_handoff(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        execution_source_digest: str,
        execution_revision_digest: str,
        authorized_at: str,
        execution_expires_at: str,
        nonce: str,
    ) -> str:
        """Compile an unsigned handoff; never issue an authority signature."""
        return _render(
            gate.compile_execution_handoff(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
                execution_source_digest,
                execution_revision_digest,
                authorized_at,
                execution_expires_at,
                nonce,
            )
        )

    @mcp.tool()
    def inspect_athena_w23_execution_authorization(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        authorization_json: str,
    ) -> str:
        """Verify signed execution authorization; never execute it."""
        return _render(
            gate.inspect_execution_authorization(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
                authorization_json,
            )
        )

    @mcp.tool()
    def evaluate_athena_w23_execution_handoff_closure(
        challenge_json: str,
        publication_json: str,
        observation_json: str,
        policy_a_json: str,
        policy_b_json: str,
        authorization_json: str,
    ) -> str:
        """Evaluate W23 closure while execution/readback remain separate."""
        return _render(
            gate.inspect_execution_authorization(
                challenge_json,
                publication_json,
                observation_json,
                policy_a_json,
                policy_b_json,
                authorization_json,
            )
        )

    @mcp.tool()
    def explain_athena_w23_execution_separation_law() -> str:
        """Explain freshness/publication/quorum/execution separation."""
        return _render(gate.explain())

    @mcp.resource("athena://w23-promotion-execution-handoff")
    def promotion_execution_handoff_resource() -> str:
        """Read the frozen W23 contract and production-empty ledgers."""
        return _render(gate.snapshot)
