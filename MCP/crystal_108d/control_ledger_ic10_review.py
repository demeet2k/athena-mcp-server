"""KC144 W26 settlement-return and independent IC10 review-open verifier.

The runtime verifies a signed append-only control-ledger return and a signed
IC10 review request.  It cannot mutate the control ledger, send the request,
review its own evidence, issue an IC10 decision, merge, deploy, or promote.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .independent_authority_return import (
    _addressed,
    _canonical_bytes,
    _commit,
    _digest,
    _exact,
    _identifier,
    _merge,
    _sha,
    _signature,
    _strict_loads,
    _text,
    _timestamp,
)
from .promotion_execution_handoff import _verify
from .persistent_promotion_settlement import (
    FrozenPersistentPromotionSettlement,
    W25_CONTRACT,
)


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w26_control_ledger_ic10_review.json"
)
SCHEMA = "athena.xnav-w26-control-ledger-ic10-review/v1"
PHASE = "KC144.XNAV.W26"

SOURCE_SCHEMA = "athena.w26-control-review-authority-source/v1"
REVISION_SCHEMA = "athena.w26-control-review-authority-revision/v1"
LEDGER_ENTRY_SCHEMA = "athena.w26-persistent-settlement-ledger-entry/v1"
TRANSACTION_SCHEMA = "athena.w26-control-ledger-transaction/v1"
AUTHORIZATION_SCHEMA = "athena.w26-control-ledger-commit-authorization/v1"
COMMIT_SCHEMA = "athena.w26-control-ledger-commit-occurrence/v1"
OBSERVATION_SCHEMA = "athena.w26-control-ledger-readback-observation/v1"
REVIEW_PACKET_SCHEMA = "athena.w26-independent-ic10-review-packet/v1"
REVIEW_REQUEST_SCHEMA = "athena.w26-independent-ic10-review-request/v1"
REQUEST_OBSERVATION_SCHEMA = (
    "athena.w26-independent-ic10-review-request-observation/v1"
)
IC10_DECISION_SCHEMA = "athena.w26-independent-ic10-decision/v1"
CLOSURE_SCHEMA = "athena.w26-control-ledger-review-open-closure/v1"

CANONICAL_GOVERNANCE_REPOSITORY = "demeet2k/Athena"
CANONICAL_RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
CANONICAL_AUTHORITY_REF_PREFIX = "refs/heads/authority/w26/"
CANONICAL_AUTHORITY_PATH_PREFIX = ".athena/authorities/w26/"
CANONICAL_CONTROL_REF = (
    "refs/heads/agent/w26-return-persistent-settlement-ic10-review"
)
CANONICAL_LEDGER_PATH = (
    ".athena/ledger/w26-persistent-settlement-returns.jsonl"
)
CONTROL_PREDECESSOR_HEAD = "352fa27e5e5a957fb3aee15c0573f4eb73f093d7"
CONTROL_PREDECESSOR_RECEIPT = (
    "w23-w25-control-reconciliation:sha256:"
    "fd9c5d316885680d98d77ca46304cac10fbd83252bbd86d89ee4a6a5187035e5"
)
RUNTIME_PREDECESSOR_HEAD = "eb0ff6e8196f142601ea6f35d12c4dc682ff6b8f"
RUNTIME_PREDECESSOR_TREE = "924bab8c59b79ac2f9c7a62ad1f312051a69a2b8"
W25_HARDENING_RECEIPT = (
    "w25-promotion-settlement-hardening:sha256:"
    "dcc5f27ae16e1d8afac34e61ade652646c5e76dd94a7c1282e00cd249aaf846d"
)
MAXIMUM_STAGE_LAG_SECONDS = 900
MAXIMUM_AUTHORIZATION_SECONDS = 900
MAXIMUM_REVIEW_OPEN_AGE_SECONDS = 3600
ZERO_ROOT = "sha256:" + "0" * 64

W26_CONTRACT = (
    "sha256:5128940d6a95f8d8a2def5cfe8f93d26a9db1bbbebd33387e47f9e4b0a8d6efc"
)

ROLES = {
    "CONTROL_LEDGER_COMMIT_AUTHORIZER": "control.ledger.commit.authorize",
    "CONTROL_LEDGER_COMMITTER": "control.ledger.commit",
    "CONTROL_LEDGER_OBSERVER": "control.ledger.observe",
    "IC10_REVIEW_REQUEST_ISSUER": "ic10.review.request.issue",
    "IC10_REVIEW_REQUEST_OBSERVER": "ic10.review.request.observe",
    "INDEPENDENT_IC10_REVIEWER": "ic10.review.independent",
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
AUTHORIZATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "authorization_id",
    "transaction_digest",
    "ledger_repository",
    "ledger_ref",
    "ledger_path",
    "base_commit",
    "expected_sequence",
    "previous_root",
    "proposed_root",
    "entry_digest",
    "issued_at",
    "expires_at",
    "nonce",
    "signature",
    "authorization_digest",
}
COMMIT_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "authorization_digest",
    "transaction_digest",
    "ledger_repository",
    "ledger_ref",
    "ledger_path",
    "parent_commit",
    "commit",
    "tree",
    "blob_digest",
    "content_digest",
    "sequence",
    "previous_root",
    "committed_root",
    "entry_digest",
    "occurred_at",
    "nonce",
    "signature",
    "commit_occurrence_digest",
}
OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "commit_occurrence_digest",
    "transaction_digest",
    "repository",
    "ref",
    "path",
    "commit",
    "parent_commit",
    "tree",
    "blob_digest",
    "content_digest",
    "observed_ref_tip",
    "sequence",
    "previous_root",
    "observed_root",
    "entry_digest",
    "observed_at",
    "nonce",
    "signature",
    "ledger_observation_digest",
}
REQUEST_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "request_id",
    "ledger_observation_digest",
    "transaction_digest",
    "w25_closure_certificate_digest",
    "settlement_observation_digest",
    "reviewer_source_digest",
    "reviewer_revision_digest",
    "review_packet_digest",
    "review_question",
    "requested_at",
    "nonce",
    "signature",
    "review_request_digest",
}
REQUEST_OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "review_request_digest",
    "review_packet_digest",
    "reviewer_source_digest",
    "reviewer_revision_digest",
    "channel_digest",
    "prior_request_count",
    "observed_state",
    "observed_at",
    "nonce",
    "signature",
    "request_observation_digest",
}
REVIEW_QUESTION = (
    "ADMIT_REJECTED_ROLLED_BACK_SETTLEMENT_AS_CONTROL_EVIDENCE"
)


class ControlLedgerIC10ReviewError(RuntimeError):
    """Frozen W26 contract or authority registry is invalid."""


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
    result = {
        "schema": _text(raw["schema"], "source.schema"),
        "source_id": _identifier(raw["source_id"], "source.source_id"),
        "authority_id": _identifier(raw["authority_id"], "source.authority_id"),
        "role": _text(raw["role"], "source.role"),
        "governance_repository": _text(
            raw["governance_repository"], "source.governance_repository"
        ),
        "source_digest": _sha(raw["source_digest"], "source.source_digest"),
    }
    if result["schema"] != SOURCE_SCHEMA or result["role"] not in ROLES:
        raise ValueError("authority source schema/role mismatch")
    if result["governance_repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
        raise ValueError("authority source governance repository mismatch")
    if result["source_digest"] != _digest(_addressed(result, "source_digest")):
        raise ValueError("authority source digest mismatch")
    return result


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
    result = {
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
                raw["parent_revision_digest"],
                "revision.parent_revision_digest",
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
    if result["schema"] != REVISION_SCHEMA or result["role"] not in ROLES:
        raise ValueError("authority revision schema/role mismatch")
    if (
        result["repository"] != CANONICAL_GOVERNANCE_REPOSITORY
        or not result["ref"].startswith(CANONICAL_AUTHORITY_REF_PREFIX)
        or not result["path"].startswith(CANONICAL_AUTHORITY_PATH_PREFIX)
        or ".." in result["path"]
        or "//" in result["path"]
    ):
        raise ValueError("authority revision governance coordinates mismatch")
    if result["scope"]["operation"] != ROLES[result["role"]]:
        raise ValueError("authority revision capability mismatch")
    if _fingerprint(result["public_key_base64"]) != result["fingerprint"]:
        raise ValueError("authority revision fingerprint mismatch")
    if _timestamp(result["valid_from"], "revision.valid_from") >= _timestamp(
        result["valid_until"], "revision.valid_until"
    ):
        raise ValueError("authority validity window is empty")
    expected_blob = _digest(
        {
            "schema": "athena.w26-authority-blob-provenance/v1",
            "repository": result["repository"],
            "ref": result["ref"],
            "commit": result["commit"],
            "tree": result["tree"],
            "path": result["path"],
            "content_digest": result["content_digest"],
        }
    )
    if result["blob_digest"] != expected_blob:
        raise ValueError("authority revision blob provenance mismatch")
    if result["revision_digest"] != _digest(
        _addressed(result, "revision_digest")
    ):
        raise ValueError("authority revision digest mismatch")
    return result


def _record(
    text: str,
    *,
    fields: set[str],
    schema: str,
    digest_field: str,
    id_fields: tuple[str, ...],
    digest_fields: tuple[str, ...],
) -> dict[str, Any]:
    raw = deepcopy(_exact(_strict_loads(text), fields, schema))
    if raw["schema"] != schema:
        raise ValueError(f"{schema} mismatch")
    raw["source_digest"] = _sha(raw["source_digest"], "source_digest")
    raw["revision_digest"] = _sha(raw["revision_digest"], "revision_digest")
    for field in id_fields:
        raw[field] = _identifier(raw[field], f"{schema}.{field}")
    for field in digest_fields:
        raw[field] = _sha(raw[field], f"{schema}.{field}")
    raw["signature"] = _signature(raw["signature"], "signature")
    raw[digest_field] = _sha(raw[digest_field], digest_field)
    return raw


def _negative() -> dict[str, bool | None]:
    return {
        "w25_settlement_verified": False,
        "control_ledger_authorization_verified": False,
        "control_ledger_commit_verified": False,
        "control_ledger_readback_verified": False,
        "ic10_review_request_verified": False,
        "ic10_review_request_observed": False,
        "ic10_review_open": False,
        "ic10_decision_recorded": False,
        "ic10_decision_digest": None,
        "runtime_mutated_registry": False,
        "runtime_mutated_control_ledger": False,
        "runtime_sent_review_request": False,
        "runtime_issued_ic10_decision": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "merge_claimed": False,
        "deployment_claimed": False,
        "promotion_claimed": False,
    }


class FrozenControlLedgerIC10Review:
    """Verify W26 control-ledger return and IC10 review-open evidence."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w25_gate: FrozenPersistentPromotionSettlement | None = None,
        *,
        verification_time: datetime | None = None,
        allow_test_contract: bool = False,
    ):
        self.snapshot = deepcopy(snapshot)
        self.w25_gate = w25_gate or FrozenPersistentPromotionSettlement.load()
        self._verification_time_override = verification_time
        if (
            verification_time is not None
            and verification_time.tzinfo != timezone.utc
        ):
            raise ControlLedgerIC10ReviewError(
                "verification time must use UTC"
            )
        self.allow_test_contract = allow_test_contract
        try:
            self._validate_snapshot()
        except (KeyError, LookupError, TypeError, ValueError) as error:
            raise ControlLedgerIC10ReviewError(str(error)) from error

    @classmethod
    def load(cls) -> "FrozenControlLedgerIC10Review":
        return cls(_strict_loads(DATA_PATH.read_text(encoding="utf-8")))

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w25_gate: FrozenPersistentPromotionSettlement | None = None,
        *,
        verification_time: datetime | None = None,
        allow_test_contract: bool = False,
    ) -> "FrozenControlLedgerIC10Review":
        return cls(
            snapshot,
            w25_gate,
            verification_time=verification_time,
            allow_test_contract=allow_test_contract,
        )

    def _validate_snapshot(self) -> None:
        expected_top_level = {
            "schema",
            "phase",
            "runtime_predecessor",
            "control_predecessor",
            "verifier_dependencies",
            "return_contract",
            "authority_registry",
            "commit_authorization_ledger",
            "commit_occurrence_ledger",
            "ledger_observation_ledger",
            "review_request_ledger",
            "review_request_observation_ledger",
            "ic10_decision_ledger",
            "boundaries",
            "successor",
            "contract_digest",
        }
        if set(self.snapshot) != expected_top_level:
            raise ValueError("W26 top-level shape mismatch")
        if self.snapshot["schema"] != SCHEMA or self.snapshot["phase"] != PHASE:
            raise ValueError("W26 schema/phase mismatch")
        if self.snapshot["runtime_predecessor"] != {
            "repository": CANONICAL_RUNTIME_REPOSITORY,
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "head": RUNTIME_PREDECESSOR_HEAD,
            "tree": RUNTIME_PREDECESSOR_TREE,
            "w25_contract_digest": W25_CONTRACT,
            "w25_hardening_receipt_id": W25_HARDENING_RECEIPT,
        }:
            raise ValueError("W26 runtime predecessor mismatch")
        if self.snapshot["control_predecessor"] != {
            "repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "pull_request": 28,
            "branch": "agent/w23-w25-reconcile-combined-hardening",
            "head": CONTROL_PREDECESSOR_HEAD,
            "receipt_id": CONTROL_PREDECESSOR_RECEIPT,
            "grants_production_authority": False,
            "hosted_runner_status": (
                "HOLD[PLATFORM_OBSTRUCTION_BEFORE_FIRST_STEP]"
            ),
        }:
            raise ValueError("W26 control predecessor mismatch")
        if self.snapshot["verifier_dependencies"] != {
            "active_w25_contract_digest": W25_CONTRACT,
            "active_w25_hardening_receipt_id": W25_HARDENING_RECEIPT,
            "active_w25_runtime_head": RUNTIME_PREDECESSOR_HEAD,
            "active_w25_runtime_tree": RUNTIME_PREDECESSOR_TREE,
            "active_control_reconciliation_head": CONTROL_PREDECESSOR_HEAD,
            "active_control_reconciliation_receipt_id": (
                CONTROL_PREDECESSOR_RECEIPT
            ),
            "exact_w25_nested_verifier_required": True,
            "exact_control_predecessor_required": True,
        }:
            raise ValueError("W26 verifier dependency mismatch")
        if self.snapshot["return_contract"] != {
            "authority_source_schema": SOURCE_SCHEMA,
            "authority_revision_schema": REVISION_SCHEMA,
            "ledger_entry_schema": LEDGER_ENTRY_SCHEMA,
            "transaction_schema": TRANSACTION_SCHEMA,
            "commit_authorization_schema": AUTHORIZATION_SCHEMA,
            "commit_occurrence_schema": COMMIT_SCHEMA,
            "ledger_observation_schema": OBSERVATION_SCHEMA,
            "review_packet_schema": REVIEW_PACKET_SCHEMA,
            "review_request_schema": REVIEW_REQUEST_SCHEMA,
            "review_request_observation_schema": REQUEST_OBSERVATION_SCHEMA,
            "ic10_decision_schema": IC10_DECISION_SCHEMA,
            "closure_schema": CLOSURE_SCHEMA,
            "roles": list(ROLES),
            "total_cross_wave_roles": 25,
            "canonical_control_ref": CANONICAL_CONTROL_REF,
            "canonical_ledger_path": CANONICAL_LEDGER_PATH,
            "initial_sequence": 1,
            "initial_previous_root": ZERO_ROOT,
            "maximum_stage_lag_seconds": MAXIMUM_STAGE_LAG_SECONDS,
            "maximum_authorization_seconds": MAXIMUM_AUTHORIZATION_SECONDS,
            "maximum_review_open_age_seconds": (
                MAXIMUM_REVIEW_OPEN_AGE_SECONDS
            ),
            "complete_w25_closure_required": True,
            "signed_commit_authorization_required": True,
            "signed_commit_occurrence_required": True,
            "independent_signed_git_readback_required": True,
            "signed_review_request_required": True,
            "independent_signed_request_observation_required": True,
            "independent_reviewer_coordinate_required": True,
            "reviewer_may_sign_request_or_observation": False,
            "request_may_self_certify_decision": False,
            "ic10_decision_required_for_review_closure": True,
            "rollback_disposition_may_change": False,
            "self_supplied_sources_revisions_or_keys_allowed": False,
            "cross_wave_identity_or_key_overlap_allowed": False,
            "runtime_can_mutate_control_ledger": False,
            "runtime_can_send_review_request": False,
            "runtime_can_issue_ic10_decision": False,
            "runtime_can_merge_deploy_or_promote": False,
        }:
            raise ValueError("W26 return contract drift")
        registry = self.snapshot["authority_registry"]
        if set(registry) != {"sources", "revisions"}:
            raise ValueError("authority registry shape mismatch")
        if not isinstance(registry["sources"], list) or not isinstance(
            registry["revisions"], list
        ):
            raise ValueError("authority registry coordinates must be arrays")
        self.sources: dict[str, dict[str, Any]] = {}
        self.revisions: dict[str, dict[str, Any]] = {}
        earlier_sources = (
            list(self.w25_gate.w24_gate.w23_gate.sources.values())
            + list(self.w25_gate.w24_gate.sources.values())
            + list(self.w25_gate.sources.values())
        )
        earlier_revisions = (
            list(self.w25_gate.w24_gate.w23_gate.revisions.values())
            + list(self.w25_gate.w24_gate.revisions.values())
            + list(self.w25_gate.revisions.values())
        )
        identities = {
            source["authority_id"]: source["role"] for source in earlier_sources
        }
        aliases: dict[str, str] = {}
        for revision in earlier_revisions:
            aliases[f"key_id:{revision['key_id']}"] = revision["role"]
            aliases[
                f"public_key:{revision['public_key_base64']}"
            ] = revision["role"]
            aliases[f"fingerprint:{revision['fingerprint']}"] = revision["role"]
        source_tips: dict[str, str] = {}
        for value in registry["sources"]:
            source = _source(value)
            if source["source_digest"] in self.sources:
                raise ValueError("duplicate authority source")
            if source["authority_id"] in identities:
                raise ValueError("authority identity overlaps W23-W26 roles")
            identities[source["authority_id"]] = source["role"]
            self.sources[source["source_digest"]] = source
        for value in registry["revisions"]:
            revision = _revision(value)
            source = self.sources.get(revision["source_digest"])
            if source is None or source["role"] != revision["role"]:
                raise ValueError("revision source unpinned or role-mismatched")
            if revision["repository"] != source["governance_repository"]:
                raise ValueError("revision does not bind source repository")
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
                    raise ValueError(f"{label} overlaps W23-W26 roles")
                aliases[alias] = revision["role"]
            self.revisions[revision["revision_digest"]] = revision
        for name in (
            "commit_authorization_ledger",
            "commit_occurrence_ledger",
            "ledger_observation_ledger",
            "review_request_ledger",
            "review_request_observation_ledger",
            "ic10_decision_ledger",
        ):
            if self.snapshot[name] != []:
                raise ValueError(f"checked-in production {name} must remain empty")
        expected_boundaries = {
            "w25_hardened_verifier_pinned": True,
            "control_reconciliation_pinned": True,
            "production_authority_source_count": len(self.sources),
            "production_authority_revision_count": len(self.revisions),
            "production_commit_authorization_count": 0,
            "production_commit_occurrence_count": 0,
            "production_ledger_observation_count": 0,
            "production_review_request_count": 0,
            "production_review_request_observation_count": 0,
            "production_ic10_decision_count": 0,
            "w25_settlement_verified": False,
            "control_ledger_authorization_verified": False,
            "control_ledger_commit_verified": False,
            "control_ledger_readback_verified": False,
            "ic10_review_request_verified": False,
            "ic10_review_request_observed": False,
            "ic10_review_open": False,
            "ic10_decision_recorded": False,
            "workflow_dispatched": False,
            "endpoint_contacted": False,
            "merge_claimed": False,
            "deployment_claimed": False,
            "promotion_claimed": False,
        }
        if self.snapshot["boundaries"] != expected_boundaries:
            raise ValueError("W26 boundary drift")
        if self.snapshot["successor"] != (
            "KC144.XNAV.W27::RETURN-INDEPENDENT-IC10-DECISION-AND-"
            "CLOSE-CONTROL-LEDGER-REVIEW"
        ):
            raise ValueError("W26 successor drift")
        expected_digest = _digest(
            {
                key: value
                for key, value in self.snapshot.items()
                if key != "contract_digest"
            }
        )
        if self.snapshot["contract_digest"] != expected_digest:
            raise ValueError("W26 contract digest mismatch")
        if (
            not self.allow_test_contract
            and self.snapshot["contract_digest"] != W26_CONTRACT
        ):
            raise ValueError("W26 contract is not externally pinned")
        if (
            self.w25_gate.snapshot.get("contract_digest") != W25_CONTRACT
            and not self.allow_test_contract
        ):
            raise ValueError("active W25 verifier contract mismatch")

    def _verification_time(self) -> datetime:
        return self._verification_time_override or datetime.now(timezone.utc)

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

    def _scope(self, revision: dict[str, Any], policy_digest: str) -> None:
        scope = revision["scope"]
        if (
            scope["operation"] != ROLES[revision["role"]]
            or scope["repository"] != CANONICAL_GOVERNANCE_REPOSITORY
            or scope["ref"] != CANONICAL_CONTROL_REF
            or scope["environment"] != "kc144-control"
            or scope["policy_digest"] != policy_digest
        ):
            raise ValueError("W26 record outside authority scope")

    def _hold(self, status: str, error: Exception | str) -> dict[str, Any]:
        return _merge({"status": status, "error": str(error)}, _negative())

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W26_W25_SETTLEMENT_PINNED__CONTROL_LEDGER_RETURN_AND_"
                    "INDEPENDENT_IC10_REVIEW_OPEN"
                ),
                "phase": PHASE,
                "runtime_predecessor_head": RUNTIME_PREDECESSOR_HEAD,
                "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
                "w25_contract_digest": W25_CONTRACT,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "commit_authorization_count": 0,
                "commit_occurrence_count": 0,
                "ledger_observation_count": 0,
                "review_request_count": 0,
                "review_request_observation_count": 0,
                "ic10_decision_count": 0,
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
                    "status": "PASS_W26_AUTHORITY_SOURCE_REVISION_PINNED",
                    "source": source,
                    "revision": revision,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W26_AUTHORITY_COORDINATE_UNPINNED", error)

    def _w25(self, record_jsons: tuple[str, ...]) -> dict[str, Any]:
        if len(record_jsons) != 19:
            raise ValueError("complete nineteen-record W25 closure is required")
        result = self.w25_gate.evaluate_closure(*record_jsons)
        if result.get("status") != (
            "PASS_W25_W24_RETURNS_PERSISTED_AND_PROMOTION_REJECTION_"
            "SETTLED__CONTROL_LEDGER_ADMISSION_OPEN"
        ):
            raise ValueError(
                "W25 persistent-settlement closure rejected: "
                + str(result.get("error", result.get("status")))
            )
        if result.get("settlement_disposition") != "REJECTED_ROLLED_BACK":
            raise ValueError("W25 rollback disposition changed")
        settlement_observation = _strict_loads(record_jsons[-1])
        observed_at = _text(
            settlement_observation["observed_at"],
            "settlement_observation.observed_at",
            limit=32,
        )
        upstream_axes = set()
        for text in record_jsons:
            record = _strict_loads(text)
            for key, value in record.items():
                if key.endswith("_id") and isinstance(value, str):
                    upstream_axes.add(value)
        return {
            "closure": result["closure_certificate"],
            "closure_digest": result["closure_certificate"][
                "certificate_digest"
            ],
            "settlement_observation_digest": result["closure_certificate"][
                "settlement_observation_digest"
            ],
            "terminal_image_digest": result["closure_certificate"][
                "terminal_image_digest"
            ],
            "target": result["target"],
            "observed_at": observed_at,
            "upstream_occurrence_axes": upstream_axes,
        }

    @staticmethod
    def _ledger_entry(w25: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "schema": LEDGER_ENTRY_SCHEMA,
            "phase": PHASE,
            "runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
            "runtime_head": RUNTIME_PREDECESSOR_HEAD,
            "runtime_tree": RUNTIME_PREDECESSOR_TREE,
            "w25_contract_digest": W25_CONTRACT,
            "w25_hardening_receipt_id": W25_HARDENING_RECEIPT,
            "w25_closure_certificate_digest": w25["closure_digest"],
            "settlement_observation_digest": w25[
                "settlement_observation_digest"
            ],
            "terminal_image_digest": w25["terminal_image_digest"],
            "promotion_disposition": "REJECTED_ROLLED_BACK",
            "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
            "control_predecessor_receipt_id": CONTROL_PREDECESSOR_RECEIPT,
            "entry_digest": "",
        }
        entry["entry_digest"] = _digest(_addressed(entry, "entry_digest"))
        return entry

    @staticmethod
    def _transaction(entry: dict[str, Any]) -> dict[str, Any]:
        root = _digest(
            {
                "schema": "athena.w26-control-ledger-root/v1",
                "previous_root": ZERO_ROOT,
                "sequence": 1,
                "entry_digest": entry["entry_digest"],
            }
        )
        transaction = {
            "schema": TRANSACTION_SCHEMA,
            "ledger_entry": entry,
            "ledger_position": {
                "repository": CANONICAL_GOVERNANCE_REPOSITORY,
                "ref": CANONICAL_CONTROL_REF,
                "path": CANONICAL_LEDGER_PATH,
                "base_commit": CONTROL_PREDECESSOR_HEAD,
                "sequence": 1,
                "previous_root": ZERO_ROOT,
                "proposed_root": root,
            },
            "transaction_digest": "",
        }
        transaction["transaction_digest"] = _digest(
            _addressed(transaction, "transaction_digest")
        )
        return transaction

    def compile_return(
        self, *w25_record_jsons: str
    ) -> dict[str, Any]:
        try:
            w25 = self._w25(tuple(w25_record_jsons))
            transaction = self._transaction(self._ledger_entry(w25))
            position = transaction["ledger_position"]
            entry = transaction["ledger_entry"]
            template = {
                "schema": AUTHORIZATION_SCHEMA,
                "source_digest": None,
                "revision_digest": None,
                "authorization_id": None,
                "transaction_digest": transaction["transaction_digest"],
                "ledger_repository": position["repository"],
                "ledger_ref": position["ref"],
                "ledger_path": position["path"],
                "base_commit": position["base_commit"],
                "expected_sequence": position["sequence"],
                "previous_root": position["previous_root"],
                "proposed_root": position["proposed_root"],
                "entry_digest": entry["entry_digest"],
                "issued_at": None,
                "expires_at": None,
                "nonce": None,
                "signature": {"key_id": None, "value": None},
                "authorization_digest": None,
            }
            return _merge(
                {
                    "status": (
                        "W26_SETTLEMENT_RETURN_COMPILED__"
                        "CONTROL_LEDGER_AUTHORIZATION_OPEN"
                    ),
                    "transaction": transaction,
                    "authorization_template": template,
                    "w25_settlement_verified": True,
                },
                {
                    key: value
                    for key, value in _negative().items()
                    if key != "w25_settlement_verified"
                },
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W26_SETTLEMENT_RETURN_REJECTED", error)

    def _authorization(
        self,
        text: str,
        transaction: dict[str, Any],
        policy_digest: str,
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=AUTHORIZATION_FIELDS,
            schema=AUTHORIZATION_SCHEMA,
            digest_field="authorization_digest",
            id_fields=("authorization_id", "nonce"),
            digest_fields=(
                "transaction_digest",
                "previous_root",
                "proposed_root",
                "entry_digest",
                "authorization_digest",
            ),
        )
        record["base_commit"] = _commit(
            record["base_commit"], "authorization.base_commit"
        )
        if (
            type(record["expected_sequence"]) is not int
            or record["expected_sequence"] <= 0
        ):
            raise ValueError("commit authorization sequence must be positive int")
        position = transaction["ledger_position"]
        entry = transaction["ledger_entry"]
        expected = {
            "transaction_digest": transaction["transaction_digest"],
            "ledger_repository": position["repository"],
            "ledger_ref": position["ref"],
            "ledger_path": position["path"],
            "base_commit": position["base_commit"],
            "expected_sequence": position["sequence"],
            "previous_root": position["previous_root"],
            "proposed_root": position["proposed_root"],
            "entry_digest": entry["entry_digest"],
        }
        for field, value in expected.items():
            if record[field] != value:
                raise ValueError(f"commit authorization {field} mismatch")
        issued = _timestamp(record["issued_at"], "authorization.issued_at")
        expires = _timestamp(record["expires_at"], "authorization.expires_at")
        if (
            expires <= issued
            or (expires - issued).total_seconds()
            > MAXIMUM_AUTHORIZATION_SECONDS
            or self._verification_time() < issued
            or self._verification_time() > expires
        ):
            raise ValueError("commit authorization window invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "CONTROL_LEDGER_COMMIT_AUTHORIZER",
        )
        self._scope(revision, policy_digest)
        _verify(record, revision, "authorization_digest", record["issued_at"])
        return record

    def _commit(
        self,
        text: str,
        transaction: dict[str, Any],
        authorization: dict[str, Any],
        policy_digest: str,
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=COMMIT_FIELDS,
            schema=COMMIT_SCHEMA,
            digest_field="commit_occurrence_digest",
            id_fields=("occurrence_id", "nonce"),
            digest_fields=(
                "authorization_digest",
                "transaction_digest",
                "blob_digest",
                "content_digest",
                "previous_root",
                "committed_root",
                "entry_digest",
                "commit_occurrence_digest",
            ),
        )
        record["parent_commit"] = _commit(
            record["parent_commit"], "commit.parent_commit"
        )
        record["commit"] = _commit(record["commit"], "commit.commit")
        record["tree"] = _commit(record["tree"], "commit.tree")
        if type(record["sequence"]) is not int or record["sequence"] <= 0:
            raise ValueError("ledger commit sequence must be positive int")
        position = transaction["ledger_position"]
        entry = transaction["ledger_entry"]
        expected_content = _digest(
            {
                "schema": "athena.w26-ledger-line-content/v1",
                "sequence": position["sequence"],
                "entry": entry,
            }
        )
        expected_blob = _digest(
            {
                "schema": "athena.w26-control-ledger-blob/v1",
                "repository": position["repository"],
                "ref": position["ref"],
                "path": position["path"],
                "parent_commit": position["base_commit"],
                "tree": record["tree"],
                "content_digest": expected_content,
            }
        )
        expected = {
            "authorization_digest": authorization["authorization_digest"],
            "transaction_digest": transaction["transaction_digest"],
            "ledger_repository": position["repository"],
            "ledger_ref": position["ref"],
            "ledger_path": position["path"],
            "parent_commit": position["base_commit"],
            "blob_digest": expected_blob,
            "content_digest": expected_content,
            "sequence": position["sequence"],
            "previous_root": position["previous_root"],
            "committed_root": position["proposed_root"],
            "entry_digest": entry["entry_digest"],
        }
        for field, value in expected.items():
            if record[field] != value:
                raise ValueError(f"ledger commit {field} mismatch")
        occurred = _timestamp(record["occurred_at"], "commit.occurred_at")
        if (
            occurred < _timestamp(
                authorization["issued_at"], "authorization.issued_at"
            )
            or occurred > _timestamp(
                authorization["expires_at"], "authorization.expires_at"
            )
            or occurred > self._verification_time()
        ):
            raise ValueError("ledger commit chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "CONTROL_LEDGER_COMMITTER",
        )
        self._scope(revision, policy_digest)
        _verify(
            record,
            revision,
            "commit_occurrence_digest",
            record["occurred_at"],
        )
        return record

    def _observation(
        self,
        text: str,
        transaction: dict[str, Any],
        occurrence: dict[str, Any],
        policy_digest: str,
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=OBSERVATION_FIELDS,
            schema=OBSERVATION_SCHEMA,
            digest_field="ledger_observation_digest",
            id_fields=("occurrence_id", "nonce"),
            digest_fields=(
                "commit_occurrence_digest",
                "transaction_digest",
                "blob_digest",
                "content_digest",
                "previous_root",
                "observed_root",
                "entry_digest",
                "ledger_observation_digest",
            ),
        )
        for field in ("commit", "parent_commit", "tree", "observed_ref_tip"):
            record[field] = _commit(
                record[field], f"ledger observation.{field}"
            )
        if type(record["sequence"]) is not int or record["sequence"] <= 0:
            raise ValueError("ledger observation sequence must be positive int")
        expected = {
            "commit_occurrence_digest": occurrence[
                "commit_occurrence_digest"
            ],
            "transaction_digest": transaction["transaction_digest"],
            "repository": occurrence["ledger_repository"],
            "ref": occurrence["ledger_ref"],
            "path": occurrence["ledger_path"],
            "commit": occurrence["commit"],
            "parent_commit": occurrence["parent_commit"],
            "tree": occurrence["tree"],
            "blob_digest": occurrence["blob_digest"],
            "content_digest": occurrence["content_digest"],
            "observed_ref_tip": occurrence["commit"],
            "sequence": occurrence["sequence"],
            "previous_root": occurrence["previous_root"],
            "observed_root": occurrence["committed_root"],
            "entry_digest": occurrence["entry_digest"],
        }
        for field, value in expected.items():
            if record[field] != value:
                raise ValueError(f"ledger observation {field} mismatch")
        observed = _timestamp(record["observed_at"], "observation.observed_at")
        occurred = _timestamp(occurrence["occurred_at"], "commit.occurred_at")
        if (
            observed < occurred
            or (observed - occurred).total_seconds()
            > MAXIMUM_STAGE_LAG_SECONDS
            or observed > self._verification_time()
        ):
            raise ValueError("ledger readback chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "CONTROL_LEDGER_OBSERVER",
        )
        self._scope(revision, policy_digest)
        _verify(
            record,
            revision,
            "ledger_observation_digest",
            record["observed_at"],
        )
        return record

    @staticmethod
    def _review_packet(
        transaction: dict[str, Any],
        observation: dict[str, Any],
        w25: dict[str, Any],
        reviewer_source_digest: str,
        reviewer_revision_digest: str,
    ) -> dict[str, Any]:
        packet = {
            "schema": REVIEW_PACKET_SCHEMA,
            "transaction_digest": transaction["transaction_digest"],
            "ledger_observation_digest": observation[
                "ledger_observation_digest"
            ],
            "w25_closure_certificate_digest": w25["closure_digest"],
            "settlement_observation_digest": w25[
                "settlement_observation_digest"
            ],
            "reviewer_source_digest": reviewer_source_digest,
            "reviewer_revision_digest": reviewer_revision_digest,
            "review_question": REVIEW_QUESTION,
            "review_constraints": {
                "evidence_only": True,
                "decision_must_be_independently_signed": True,
                "request_is_not_decision": True,
                "review_open_is_not_review_pass": True,
                "promotion_authorized": False,
                "runtime_can_issue_decision": False,
            },
            "packet_digest": "",
        }
        packet["packet_digest"] = _digest(
            _addressed(packet, "packet_digest")
        )
        return packet

    def _request(
        self,
        text: str,
        transaction: dict[str, Any],
        observation: dict[str, Any],
        w25: dict[str, Any],
        policy_digest: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        record = _record(
            text,
            fields=REQUEST_FIELDS,
            schema=REVIEW_REQUEST_SCHEMA,
            digest_field="review_request_digest",
            id_fields=("request_id", "nonce"),
            digest_fields=(
                "ledger_observation_digest",
                "transaction_digest",
                "w25_closure_certificate_digest",
                "settlement_observation_digest",
                "reviewer_source_digest",
                "reviewer_revision_digest",
                "review_packet_digest",
                "review_request_digest",
            ),
        )
        _, reviewer = self._authority(
            record["reviewer_source_digest"],
            record["reviewer_revision_digest"],
            "INDEPENDENT_IC10_REVIEWER",
        )
        self._scope(reviewer, policy_digest)
        packet = self._review_packet(
            transaction,
            observation,
            w25,
            record["reviewer_source_digest"],
            record["reviewer_revision_digest"],
        )
        expected = {
            "ledger_observation_digest": observation[
                "ledger_observation_digest"
            ],
            "transaction_digest": transaction["transaction_digest"],
            "w25_closure_certificate_digest": w25["closure_digest"],
            "settlement_observation_digest": w25[
                "settlement_observation_digest"
            ],
            "review_packet_digest": packet["packet_digest"],
            "review_question": REVIEW_QUESTION,
        }
        for field, value in expected.items():
            if record[field] != value:
                raise ValueError(f"IC10 review request {field} mismatch")
        requested = _timestamp(record["requested_at"], "request.requested_at")
        observed = _timestamp(
            observation["observed_at"], "observation.observed_at"
        )
        if (
            requested < observed
            or (requested - observed).total_seconds()
            > MAXIMUM_STAGE_LAG_SECONDS
            or requested > self._verification_time()
        ):
            raise ValueError("IC10 review request chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "IC10_REVIEW_REQUEST_ISSUER",
        )
        self._scope(revision, policy_digest)
        if revision["revision_digest"] == reviewer["revision_digest"]:
            raise ValueError("review requester cannot be independent reviewer")
        _verify(
            record,
            revision,
            "review_request_digest",
            record["requested_at"],
        )
        return record, packet

    def _request_observation(
        self,
        text: str,
        request: dict[str, Any],
        packet: dict[str, Any],
        policy_digest: str,
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=REQUEST_OBSERVATION_FIELDS,
            schema=REQUEST_OBSERVATION_SCHEMA,
            digest_field="request_observation_digest",
            id_fields=("occurrence_id", "nonce"),
            digest_fields=(
                "review_request_digest",
                "review_packet_digest",
                "reviewer_source_digest",
                "reviewer_revision_digest",
                "channel_digest",
                "request_observation_digest",
            ),
        )
        if type(record["prior_request_count"]) is not int:
            raise ValueError("prior request count must be exact int")
        expected_channel = _digest(
            {
                "schema": "athena.w26-ic10-review-channel/v1",
                "review_request_digest": request["review_request_digest"],
                "reviewer_source_digest": request["reviewer_source_digest"],
                "reviewer_revision_digest": request[
                    "reviewer_revision_digest"
                ],
                "review_packet_digest": packet["packet_digest"],
            }
        )
        expected = {
            "review_request_digest": request["review_request_digest"],
            "review_packet_digest": packet["packet_digest"],
            "reviewer_source_digest": request["reviewer_source_digest"],
            "reviewer_revision_digest": request["reviewer_revision_digest"],
            "channel_digest": expected_channel,
            "prior_request_count": 0,
            "observed_state": "OPEN_AWAITING_INDEPENDENT_IC10_DECISION",
        }
        for field, value in expected.items():
            if record[field] != value:
                raise ValueError(f"review request observation {field} mismatch")
        observed = _timestamp(
            record["observed_at"], "request_observation.observed_at"
        )
        requested = _timestamp(request["requested_at"], "request.requested_at")
        if (
            observed < requested
            or (observed - requested).total_seconds()
            > MAXIMUM_STAGE_LAG_SECONDS
            or observed > self._verification_time()
            or (self._verification_time() - observed).total_seconds()
            > MAXIMUM_REVIEW_OPEN_AGE_SECONDS
        ):
            raise ValueError("review request observation chronology invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "IC10_REVIEW_REQUEST_OBSERVER",
        )
        self._scope(revision, policy_digest)
        if record["revision_digest"] in {
            request["revision_digest"],
            request["reviewer_revision_digest"],
        }:
            raise ValueError(
                "request observer must be independent of requester and reviewer"
            )
        _verify(
            record,
            revision,
            "request_observation_digest",
            record["observed_at"],
        )
        return record

    def evaluate_closure(
        self,
        *record_jsons: str,
    ) -> dict[str, Any]:
        try:
            if len(record_jsons) != 24:
                raise ValueError(
                    "W26 closure requires nineteen W25 and five W26 records"
                )
            w25_jsons = tuple(record_jsons[:19])
            w25 = self._w25(w25_jsons)
            transaction = self._transaction(self._ledger_entry(w25))
            policy_digest = _digest(
                {
                    "schema": "athena.w26-control-review-policy/v1",
                    "w25_contract_digest": W25_CONTRACT,
                    "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
                    "canonical_control_ref": CANONICAL_CONTROL_REF,
                    "canonical_ledger_path": CANONICAL_LEDGER_PATH,
                    "review_question": REVIEW_QUESTION,
                }
            )
            authorization = self._authorization(
                record_jsons[19], transaction, policy_digest
            )
            w25_observed = _timestamp(
                w25["observed_at"], "w25 settlement observed_at"
            )
            authorized = _timestamp(
                authorization["issued_at"], "authorization.issued_at"
            )
            if (
                authorized < w25_observed
                or (authorized - w25_observed).total_seconds()
                > MAXIMUM_STAGE_LAG_SECONDS
            ):
                raise ValueError(
                    "control-ledger authorization chronology does not follow W25"
                )
            occurrence = self._commit(
                record_jsons[20],
                transaction,
                authorization,
                policy_digest,
            )
            observation = self._observation(
                record_jsons[21],
                transaction,
                occurrence,
                policy_digest,
            )
            request, packet = self._request(
                record_jsons[22],
                transaction,
                observation,
                w25,
                policy_digest,
            )
            request_observation = self._request_observation(
                record_jsons[23],
                request,
                packet,
                policy_digest,
            )
            axes = {
                authorization["authorization_id"],
                occurrence["occurrence_id"],
                observation["occurrence_id"],
                request["request_id"],
                request_observation["occurrence_id"],
            }
            if len(axes) != 5:
                raise ValueError("W26 occurrence axes must be pairwise disjoint")
            if axes & w25["upstream_occurrence_axes"]:
                raise ValueError("W26 occurrence axis overlaps W23-W25 evidence")
            nonces = {
                authorization["nonce"],
                occurrence["nonce"],
                observation["nonce"],
                request["nonce"],
                request_observation["nonce"],
            }
            if len(nonces) != 5:
                raise ValueError("W26 replay nonces must be pairwise disjoint")
            certificate = {
                "schema": CLOSURE_SCHEMA,
                "w25_contract_digest": W25_CONTRACT,
                "w25_closure_certificate_digest": w25["closure_digest"],
                "settlement_observation_digest": w25[
                    "settlement_observation_digest"
                ],
                "transaction_digest": transaction["transaction_digest"],
                "ledger_entry_digest": transaction["ledger_entry"][
                    "entry_digest"
                ],
                "commit_authorization_digest": authorization[
                    "authorization_digest"
                ],
                "commit_occurrence_digest": occurrence[
                    "commit_occurrence_digest"
                ],
                "ledger_observation_digest": observation[
                    "ledger_observation_digest"
                ],
                "review_packet_digest": packet["packet_digest"],
                "review_request_digest": request["review_request_digest"],
                "request_observation_digest": request_observation[
                    "request_observation_digest"
                ],
                "reviewer_source_digest": request["reviewer_source_digest"],
                "reviewer_revision_digest": request[
                    "reviewer_revision_digest"
                ],
                "promotion_disposition": "REJECTED_ROLLED_BACK",
                "review_state": "OPEN_AWAITING_INDEPENDENT_IC10_DECISION",
                "ic10_decision_digest": None,
                "certificate_digest": "",
            }
            certificate["certificate_digest"] = _digest(
                _addressed(certificate, "certificate_digest")
            )
            return {
                "status": (
                    "PASS_W26_PERSISTENT_SETTLEMENT_RETURNED_TO_CONTROL_"
                    "LEDGER__INDEPENDENT_IC10_REVIEW_OPEN_DECISION_ABSENT"
                ),
                "closure_certificate": certificate,
                "review_packet": packet,
                "decision_template": {
                    "schema": IC10_DECISION_SCHEMA,
                    "review_packet_digest": packet["packet_digest"],
                    "reviewer_source_digest": request[
                        "reviewer_source_digest"
                    ],
                    "reviewer_revision_digest": request[
                        "reviewer_revision_digest"
                    ],
                    "decision": None,
                    "reason_code": None,
                    "reviewed_at": None,
                    "signature": {"key_id": None, "value": None},
                    "decision_digest": None,
                },
                "w25_settlement_verified": True,
                "control_ledger_authorization_verified": True,
                "control_ledger_commit_verified": True,
                "control_ledger_readback_verified": True,
                "ic10_review_request_verified": True,
                "ic10_review_request_observed": True,
                "ic10_review_open": True,
                "ic10_decision_recorded": False,
                "ic10_decision_digest": None,
                "runtime_mutated_registry": False,
                "runtime_mutated_control_ledger": False,
                "runtime_sent_review_request": False,
                "runtime_issued_ic10_decision": False,
                "workflow_dispatched": False,
                "endpoint_contacted": False,
                "merge_claimed": False,
                "deployment_claimed": False,
                "promotion_claimed": False,
            }
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W26_CONTROL_RETURN_OR_REVIEW_REJECTED", error)

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W26_CONTROL_RETURN_REVIEW_SEPARATION_EXPLAINED",
                "law": (
                    "SETTLEMENT CLOSURE != CONTROL-LEDGER COMMIT; COMMIT "
                    "OCCURRENCE != INDEPENDENT GIT READBACK; REVIEW REQUEST != "
                    "REQUEST OBSERVATION; REVIEW OPEN != INDEPENDENT IC10 "
                    "DECISION; IC10 REVIEW != PROMOTION"
                ),
                "required_roles": list(ROLES),
                "total_cross_wave_roles": 25,
                "review_state": "OPEN_AWAITING_INDEPENDENT_IC10_DECISION",
                "runtime_is_verifier_only": True,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_control_ledger_ic10_review(mcp: Any) -> None:
    """Register seven W26 tools and one frozen resource."""
    gate = FrozenControlLedgerIC10Review.load()

    @mcp.tool()
    def athena_w26_control_ledger_ic10_review_status() -> str:
        """Return W26 frozen-empty control-return and IC10 boundaries."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w26_predecessor_custody() -> str:
        """Inspect exact W25/runtime/control custody without granting authority."""
        result = gate.status()
        result["status"] = (
            "PASS_W26_W25_AND_CONTROL_PREDECESSORS_PINNED__"
            "NO_PRODUCTION_AUTHORITY_GRANTED"
        )
        return _render(result)

    @mcp.tool()
    def inspect_athena_w26_authority_source_revision(
        source_digest: str, revision_digest: str
    ) -> str:
        """Inspect one pinned W26 authority coordinate."""
        return _render(gate.inspect_source_revision(source_digest, revision_digest))

    @mcp.tool()
    def inspect_athena_w26_control_ledger_return_contract() -> str:
        """Inspect append-only ledger authorization/commit/readback separation."""
        return _render(
            {
                "transaction_schema": TRANSACTION_SCHEMA,
                "authorization_schema": AUTHORIZATION_SCHEMA,
                "commit_schema": COMMIT_SCHEMA,
                "observation_schema": OBSERVATION_SCHEMA,
                "canonical_ref": CANONICAL_CONTROL_REF,
                "canonical_path": CANONICAL_LEDGER_PATH,
                "runtime_can_mutate_control_ledger": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w26_independent_ic10_review_contract() -> str:
        """Inspect review-request, observation, and decision separation."""
        return _render(
            {
                "packet_schema": REVIEW_PACKET_SCHEMA,
                "request_schema": REVIEW_REQUEST_SCHEMA,
                "request_observation_schema": REQUEST_OBSERVATION_SCHEMA,
                "decision_schema": IC10_DECISION_SCHEMA,
                "review_question": REVIEW_QUESTION,
                "review_open_is_decision": False,
                "runtime_can_issue_ic10_decision": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def evaluate_athena_w26_control_ledger_ic10_review(
        bundle_json: str,
    ) -> str:
        """Verify one strict 24-record W26 bundle without side effects."""
        try:
            bundle = _strict_loads(bundle_json)
            if not isinstance(bundle, list) or len(bundle) != 24:
                raise ValueError("bundle must be an exact 24-record array")
            records = tuple(
                json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                for item in bundle
            )
            return _render(gate.evaluate_closure(*records))
        except (TypeError, ValueError) as error:
            return _render(
                gate._hold("HOLD_W26_CONTROL_RETURN_OR_REVIEW_REJECTED", error)
            )

    @mcp.tool()
    def explain_athena_w26_control_return_review_separation_law() -> str:
        """Explain why a review-open certificate is not an IC10 decision."""
        return _render(gate.explain())

    @mcp.resource("athena://w26-control-ledger-ic10-review")
    def control_ledger_ic10_review_resource() -> str:
        """Read the frozen W26 contract and production-empty ledgers."""
        return _render(gate.snapshot)
