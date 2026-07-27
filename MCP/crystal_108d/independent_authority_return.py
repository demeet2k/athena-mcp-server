"""KC144 W22 independent authority-return and coordinate verifier.

W22 corrects W21 forward without rewriting it.  Every authority fact is an
exact coordinate ``X = <source, revision, occurrence>``.  A W21 custody
receipt is predecessor evidence, never an authority source or an occurrence.
This module verifies and compiles candidates only; it cannot persist, dispatch,
contact an endpoint, merge, deploy, execute, or promote.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .provider_trust_anchor import (
    _canonical_bytes,
    _verify_ed25519_signature,
)


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w22_independent_authority_return.json"
)
SCHEMA = "athena.xnav-w22-independent-authority-return/v1"
PHASE = "KC144.XNAV.W22"
SOURCE_SCHEMA = "athena.w22-authority-source/v1"
REVISION_SCHEMA = "athena.w22-authority-revision/v1"
COMMIT_RETURN_SCHEMA = "athena.w22-ledger-commit-return/v1"
OBSERVATION_SCHEMA = "athena.w22-git-commit-observation/v1"
PROMOTION_RETURN_SCHEMA = "athena.w22-promotion-decision-return/v1"
CANDIDATE_SCHEMA = "athena.w22-return-admission-candidate/v1"
CORRECTION_SCHEMA = "athena.w22-correction-forward/v1"
LEDGER_ENTRY_SCHEMA = "athena.w22-return-ledger-entry/v1"

W21_HEAD = "929cfe6762a989f9595551d654b94ecc01320910"
W21_TREE = "1a4c72a3694ee3cc2f2699d0f23c2e74920762a0"
W21_PARENT = "772564d48618b3b35276baadd87cf36ce4db46fa"
W21_CONTRACT = (
    "sha256:9e68dc7c16ea75ac5c4f6445999ec8831f678e01b24b6cfa380c5097fbaf3e18"
)
W21_RECEIPT = (
    "w21-commit-handoff:sha256:"
    "4e2af32863274f977caf93be4fd719229a78ff5298f996c2f8f64762eae72c15"
)
W20_TARGET_HEAD = W21_PARENT
W21_CANDIDATE_IMAGE = (
    "sha256:416200170040c9d8ab938998dc89242e44a021b5dce743affd01694308857b47"
)

ROLES = {
    "LEDGER_COMMIT",
    "LEDGER_OBSERVER",
    "PROMOTION_DECISION",
    "CORRECTION",
}
DECISIONS = {"AUTHORIZE_PROMOTION", "HOLD_PROMOTION"}
SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^[a-z0-9][a-z0-9._:/-]{2,127}$")

SOURCE_FIELDS = {
    "schema",
    "source_id",
    "authority_id",
    "role",
    "governance_repository",
    "scope_kind",
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
    "target_head",
    "target_image_id",
    "policy_digest",
}
CUSTODY_FIELDS = {
    "w21_head",
    "w21_tree",
    "w21_sole_parent",
    "w21_contract_digest",
    "w21_receipt_id",
}
SIGNATURE_FIELDS = {"key_id", "value"}
COMMIT_RETURN_FIELDS = {
    "schema",
    "custody",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "transaction_digest",
    "authorization_digest",
    "ic10_review_packet_digest",
    "ic10_decision_digest",
    "ledger_repository",
    "ledger_ref",
    "ledger_commit",
    "parent_commit",
    "tree",
    "ledger_path",
    "ledger_blob_digest",
    "sequence",
    "previous_entry_digest",
    "ledger_root_before",
    "ledger_root_after",
    "entry_digest",
    "authorized_at",
    "authorization_expires_at",
    "occurred_at",
    "nonce",
    "policy_digest",
    "signature",
    "return_digest",
}
OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "commit_return_digest",
    "repository",
    "ref",
    "commit",
    "parent_commit",
    "tree",
    "path",
    "blob_digest",
    "previous_root",
    "resulting_root",
    "observed_ref_tip",
    "observed_at",
    "signature",
    "observation_digest",
}
PROMOTION_RETURN_FIELDS = {
    "schema",
    "custody",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "commit_return_digest",
    "git_observation_digest",
    "ledger_root",
    "entry_digest",
    "ic10_review_packet_digest",
    "ic10_decision_digest",
    "target",
    "decision",
    "decided_at",
    "nonce",
    "policy_digest",
    "signature",
    "return_digest",
}
TARGET_FIELDS = {
    "runtime_repository",
    "runtime_head",
    "candidate_image_id",
    "target_environment",
    "target_ref",
}
CORRECTION_FIELDS = {
    "schema",
    "stream_id",
    "sequence",
    "previous_correction_digest",
    "corrects_return_digest",
    "corrected_revision_digest",
    "replacement_return_digest",
    "reason_code",
    "occurred_at",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "signature",
    "correction_digest",
}


class IndependentAuthorityReturnError(RuntimeError):
    """Frozen W22 contract or coordinate registry is invalid."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def _bounded(value: Any, *, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("JSON nesting exceeds 32")
    if isinstance(value, str):
        if len(value) > 4096:
            raise ValueError("JSON string exceeds 4096 characters")
    elif isinstance(value, list):
        if len(value) > 256:
            raise ValueError("JSON array exceeds 256 items")
        for item in value:
            _bounded(item, depth=depth + 1)
    elif isinstance(value, dict):
        if len(value) > 128:
            raise ValueError("JSON object exceeds 128 members")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object key must be text")
            _bounded(item, depth=depth + 1)
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise ValueError("unsupported JSON value")


def _strict_loads(text: str, *, object_required: bool = True) -> Any:
    if not isinstance(text, str) or len(text.encode("utf-8")) > 262144:
        raise ValueError("JSON input exceeds 262144 bytes")
    value = json.loads(text, object_pairs_hook=_pairs)
    _bounded(value)
    if object_required and not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _exact(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    missing = sorted(fields - set(value))
    extra = sorted(set(value) - fields)
    if missing or extra:
        raise ValueError(f"{path} fields mismatch: missing={missing}, extra={extra}")
    return value


def _text(value: Any, path: str, *, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > limit:
        raise ValueError(f"{path} must be bounded non-empty text")
    return value


def _identifier(value: Any, path: str) -> str:
    text = _text(value, path, limit=128)
    if not ID.fullmatch(text):
        raise ValueError(f"{path} is not a canonical identifier")
    return text


def _sha(value: Any, path: str) -> str:
    text = _text(value, path, limit=71)
    if not SHA.fullmatch(text):
        raise ValueError(f"{path} must be sha256:<64 lowercase hex>")
    return text


def _commit(value: Any, path: str) -> str:
    text = _text(value, path, limit=40)
    if not COMMIT.fullmatch(text):
        raise ValueError(f"{path} must be exact 40-hex")
    return text


def _timestamp(value: Any, path: str) -> datetime:
    text = _text(value, path, limit=32)
    if not text.endswith("Z"):
        raise ValueError(f"{path} must be UTC with Z")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as error:
        raise ValueError(f"{path} must be RFC3339 UTC") from error
    if parsed.tzinfo != timezone.utc:
        raise ValueError(f"{path} must be UTC")
    return parsed


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _addressed(value: dict[str, Any], digest_field: str) -> dict[str, Any]:
    return {key: deepcopy(item) for key, item in value.items() if key != digest_field}


def _signed(value: dict[str, Any], digest_field: str) -> dict[str, Any]:
    return {
        key: deepcopy(item)
        for key, item in value.items()
        if key not in {digest_field, "signature"}
    }


def _signature(value: Any, path: str) -> dict[str, str]:
    raw = _exact(value, SIGNATURE_FIELDS, path)
    return {
        "key_id": _identifier(raw["key_id"], f"{path}.key_id"),
        "value": _text(raw["value"], f"{path}.value", limit=128),
    }


def _fingerprint(public_key_base64: str) -> str:
    try:
        decoded = base64.b64decode(public_key_base64, validate=True)
    except ValueError as error:
        raise ValueError("public_key_base64 must be canonical base64") from error
    if len(decoded) != 32 or base64.b64encode(decoded).decode() != public_key_base64:
        raise ValueError("public_key_base64 must encode exactly 32 bytes")
    return "sha256:" + hashlib.sha256(decoded).hexdigest()


def _custody(value: Any) -> dict[str, Any]:
    raw = _exact(value, CUSTODY_FIELDS, "custody")
    result = {
        "w21_head": _commit(raw["w21_head"], "custody.w21_head"),
        "w21_tree": _commit(raw["w21_tree"], "custody.w21_tree"),
        "w21_sole_parent": _commit(
            raw["w21_sole_parent"], "custody.w21_sole_parent"
        ),
        "w21_contract_digest": _sha(
            raw["w21_contract_digest"], "custody.w21_contract_digest"
        ),
        "w21_receipt_id": _text(
            raw["w21_receipt_id"], "custody.w21_receipt_id", limit=128
        ),
    }
    expected = {
        "w21_head": W21_HEAD,
        "w21_tree": W21_TREE,
        "w21_sole_parent": W21_PARENT,
        "w21_contract_digest": W21_CONTRACT,
        "w21_receipt_id": W21_RECEIPT,
    }
    if result != expected:
        raise ValueError("custody does not bind the exact immutable W21 coordinate")
    return result


def _scope(value: Any, path: str) -> dict[str, str]:
    raw = _exact(value, SCOPE_FIELDS, path)
    result = {
        "operation": _identifier(raw["operation"], f"{path}.operation"),
        "repository": _text(raw["repository"], f"{path}.repository"),
        "ref": _text(raw["ref"], f"{path}.ref"),
        "environment": _identifier(raw["environment"], f"{path}.environment"),
        "target_head": _commit(raw["target_head"], f"{path}.target_head"),
        "target_image_id": _sha(
            raw["target_image_id"], f"{path}.target_image_id"
        ),
        "policy_digest": _sha(raw["policy_digest"], f"{path}.policy_digest"),
    }
    return result


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
        "scope_kind": _identifier(raw["scope_kind"], "source.scope_kind"),
        "source_digest": _sha(raw["source_digest"], "source.source_digest"),
    }
    if normalized["schema"] != SOURCE_SCHEMA:
        raise ValueError("authority source schema mismatch")
    if normalized["role"] not in ROLES:
        raise ValueError("unknown authority source role")
    if normalized["source_digest"] != _digest(
        _addressed(normalized, "source_digest")
    ):
        raise ValueError("authority source digest mismatch")
    return normalized


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
            else _sha(raw["parent_revision_digest"], "revision.parent_revision_digest")
        ),
        "key_id": _identifier(raw["key_id"], "revision.key_id"),
        "public_key_base64": _text(
            raw["public_key_base64"], "revision.public_key_base64", limit=64
        ),
        "fingerprint": _sha(raw["fingerprint"], "revision.fingerprint"),
        "valid_from": _text(raw["valid_from"], "revision.valid_from", limit=32),
        "valid_until": _text(raw["valid_until"], "revision.valid_until", limit=32),
        "scope": _scope(raw["scope"], "revision.scope"),
        "revision_digest": _sha(
            raw["revision_digest"], "revision.revision_digest"
        ),
    }
    if normalized["schema"] != REVISION_SCHEMA:
        raise ValueError("authority revision schema mismatch")
    if normalized["role"] not in ROLES:
        raise ValueError("unknown authority revision role")
    if _fingerprint(normalized["public_key_base64"]) != normalized["fingerprint"]:
        raise ValueError("authority revision fingerprint mismatch")
    if _timestamp(normalized["valid_from"], "revision.valid_from") >= _timestamp(
        normalized["valid_until"], "revision.valid_until"
    ):
        raise ValueError("authority revision validity interval is empty")
    if normalized["revision_digest"] != _digest(
        _addressed(normalized, "revision_digest")
    ):
        raise ValueError("authority revision digest mismatch")
    return normalized


def _verify(
    record: dict[str, Any],
    revision: dict[str, Any],
    *,
    digest_field: str,
    occurred_at: str,
) -> None:
    signature = _signature(record["signature"], "signature")
    if signature["key_id"] != revision["key_id"]:
        raise ValueError("signature key ID does not match pinned revision")
    when = _timestamp(occurred_at, "occurrence timestamp")
    if not (
        _timestamp(revision["valid_from"], "revision.valid_from")
        <= when
        <= _timestamp(revision["valid_until"], "revision.valid_until")
    ):
        raise ValueError("authority revision was not valid at occurrence")
    if not _verify_ed25519_signature(
        revision["public_key_base64"],
        signature["value"],
        _signed(record, digest_field),
    ):
        raise ValueError("occurrence signature mismatch")
    if record[digest_field] != _digest(_addressed(record, digest_field)):
        raise ValueError(f"{digest_field} mismatch")


def _merge(*parts: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for part in parts:
        overlap = set(result) & set(part)
        if overlap:
            raise IndependentAuthorityReturnError(
                f"result key collision: {sorted(overlap)}"
            )
        result.update(part)
    return result


def _negative() -> dict[str, bool]:
    return {
        "runtime_mutated_registry": False,
        "runtime_mutated_return_ledger": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "promotion_execution_authorized": False,
        "promotion_executed": False,
        "deployment_claimed": False,
        "merge_claimed": False,
        "promotion_claimed": False,
    }


class FrozenIndependentAuthorityReturn:
    """Frozen, production-empty W22 verifier and candidate compiler."""

    def __init__(self, snapshot: dict[str, Any]):
        self.snapshot = deepcopy(snapshot)
        try:
            self._validate_snapshot()
        except IndependentAuthorityReturnError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise IndependentAuthorityReturnError(str(error)) from error

    @classmethod
    def load(cls) -> "FrozenIndependentAuthorityReturn":
        return cls(_strict_loads(DATA_PATH.read_text(encoding="utf-8")))

    @classmethod
    def from_snapshot(
        cls, snapshot: dict[str, Any]
    ) -> "FrozenIndependentAuthorityReturn":
        return cls(snapshot)

    def _validate_snapshot(self) -> None:
        if self.snapshot.get("schema") != SCHEMA or self.snapshot.get("phase") != PHASE:
            raise IndependentAuthorityReturnError("W22 snapshot schema/phase mismatch")
        predecessor = self.snapshot.get("predecessor", {})
        if {
            "w21_head": predecessor.get("w21_head"),
            "w21_tree": predecessor.get("w21_tree"),
            "w21_sole_parent": predecessor.get("w21_sole_parent"),
            "w21_contract_digest": predecessor.get("w21_contract_digest"),
            "w21_receipt_id": predecessor.get("w21_receipt_id"),
        } != {
            "w21_head": W21_HEAD,
            "w21_tree": W21_TREE,
            "w21_sole_parent": W21_PARENT,
            "w21_contract_digest": W21_CONTRACT,
            "w21_receipt_id": W21_RECEIPT,
        }:
            raise IndependentAuthorityReturnError("W21 custody coordinate mismatch")
        control = self.snapshot.get("control_protocol_observation", {})
        if (
            control.get("receipt_id")
            != "w21-control-admission:sha256:"
            "78742031032e1f01a35b8ea711280b0069d8d5bfff71d59cfe517734195fc0fc"
            or control.get("grants_production_authority") is not False
        ):
            raise IndependentAuthorityReturnError(
                "W21 control observation is not exact and authority-empty"
            )
        registry = self.snapshot.get("authority_source_registry")
        if not isinstance(registry, dict) or set(registry) != {"sources", "revisions"}:
            raise IndependentAuthorityReturnError("authority registry shape mismatch")
        self.sources: dict[str, dict[str, Any]] = {}
        self.revisions: dict[str, dict[str, Any]] = {}
        source_ids: set[str] = set()
        authority_roles: dict[str, str] = {}
        for raw in registry["sources"]:
            source = _source(raw)
            if source["source_digest"] in self.sources or source["source_id"] in source_ids:
                raise IndependentAuthorityReturnError("duplicate authority source")
            prior = authority_roles.get(source["authority_id"])
            if prior is not None and prior != source["role"]:
                raise IndependentAuthorityReturnError(
                    "authority identity overlaps cross-role sources"
                )
            authority_roles[source["authority_id"]] = source["role"]
            source_ids.add(source["source_id"])
            self.sources[source["source_digest"]] = source
        fingerprints: dict[str, str] = {}
        public_keys: dict[str, str] = {}
        key_ids: dict[str, str] = {}
        tips: dict[str, str] = {}
        for raw in registry["revisions"]:
            revision = _revision(raw)
            source = self.sources.get(revision["source_digest"])
            if source is None or source["role"] != revision["role"]:
                raise IndependentAuthorityReturnError(
                    "revision source is unpinned or role-mismatched"
                )
            if revision["revision_digest"] in self.revisions:
                raise IndependentAuthorityReturnError("duplicate authority revision")
            for mapping, value, label in (
                (fingerprints, revision["fingerprint"], "fingerprint"),
                (public_keys, revision["public_key_base64"], "public key"),
                (key_ids, revision["key_id"], "key ID"),
            ):
                prior_role = mapping.get(value)
                if prior_role is not None and prior_role != revision["role"]:
                    raise IndependentAuthorityReturnError(
                        f"{label} overlaps cross-role revisions"
                    )
                mapping[value] = revision["role"]
            prior_tip = tips.get(revision["source_digest"])
            if revision["parent_revision_digest"] != prior_tip:
                raise IndependentAuthorityReturnError(
                    "revision chain is not append-only in snapshot order"
                )
            tips[revision["source_digest"]] = revision["revision_digest"]
            self.revisions[revision["revision_digest"]] = revision
        ledger = self.snapshot.get("admitted_return_ledger")
        if not isinstance(ledger, dict) or set(ledger) != {"entries"}:
            raise IndependentAuthorityReturnError("return ledger shape mismatch")
        if not isinstance(ledger["entries"], list):
            raise IndependentAuthorityReturnError("return ledger entries must be list")
        previous = None
        self.occurrences: dict[str, str] = {}
        self.positions: dict[tuple[int, Any], str] = {}
        for index, entry in enumerate(ledger["entries"], 1):
            if not isinstance(entry, dict) or entry.get("schema") != LEDGER_ENTRY_SCHEMA:
                raise IndependentAuthorityReturnError("invalid return-ledger entry")
            if entry.get("sequence") != index or entry.get("previous_entry_digest") != previous:
                raise IndependentAuthorityReturnError("return ledger chain mismatch")
            if entry.get("entry_digest") != _digest(
                _addressed(entry, "entry_digest")
            ):
                raise IndependentAuthorityReturnError("return ledger digest mismatch")
            occurrence = _identifier(entry.get("occurrence_id"), "entry.occurrence_id")
            payload = _sha(entry.get("payload_digest"), "entry.payload_digest")
            if occurrence in self.occurrences:
                raise IndependentAuthorityReturnError("duplicate ledger occurrence")
            position = (index, previous)
            if position in self.positions:
                raise IndependentAuthorityReturnError("double return-ledger position")
            self.occurrences[occurrence] = payload
            self.positions[position] = entry["entry_digest"]
            previous = entry["entry_digest"]
        expected_digest = _digest(
            {
                key: value
                for key, value in self.snapshot.items()
                if key != "contract_digest"
            }
        )
        if self.snapshot.get("contract_digest") != expected_digest:
            raise IndependentAuthorityReturnError("W22 contract digest mismatch")

    def _authority(
        self, source_digest: str, revision_digest: str, role: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        source = self.sources.get(source_digest)
        revision = self.revisions.get(revision_digest)
        if source is None or revision is None:
            raise LookupError("authority source/revision coordinate is not pinned")
        if (
            source["role"] != role
            or revision["role"] != role
            or revision["source_digest"] != source_digest
        ):
            raise ValueError("authority coordinate role mismatch")
        return source, revision

    def _hold(self, status: str, error: Exception | str) -> dict[str, Any]:
        return _merge(
            {"status": status, "error": str(error)},
            {
                "ledger_commit_return_verified": False,
                "git_commit_observed": False,
                "ledger_entry_committed": False,
                "promotion_decision_return_verified": False,
                "promotion_authorized": False,
            },
            _negative(),
        )

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W22_W21_CUSTODY_PINNED__INDEPENDENT_AUTHORITY_"
                    "SOURCES_REVISIONS_AND_OCCURRENCES_OPEN"
                ),
                "phase": PHASE,
                "w21_head": W21_HEAD,
                "w21_tree": W21_TREE,
                "w21_sole_parent": W21_PARENT,
                "w21_contract_digest": W21_CONTRACT,
                "w21_receipt_id": W21_RECEIPT,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "admitted_return_count": len(
                    self.snapshot["admitted_return_ledger"]["entries"]
                ),
                "coordinate_law": self.snapshot["coordinate_contract"]["law"],
                "w21_custody_grants_authority": False,
                "w21_control_observation_grants_authority": False,
                "ledger_commit_return_verified": False,
                "git_commit_observed": False,
                "ledger_entry_committed": False,
                "promotion_decision_return_verified": False,
                "promotion_authorized": False,
                "successor": self.snapshot["successor"],
            },
            _negative(),
        )

    def inspect_source_revision(
        self, source_digest: str, revision_digest: str
    ) -> dict[str, Any]:
        try:
            source, revision = self._authority(
                _sha(source_digest, "source_digest"),
                _sha(revision_digest, "revision_digest"),
                self.sources[_sha(source_digest, "source_digest")]["role"],
            )
            return _merge(
                {
                    "status": "PASS_W22_AUTHORITY_SOURCE_AND_REVISION_PINNED",
                    "source": deepcopy(source),
                    "revision": deepcopy(revision),
                    "source_is_revision": False,
                    "revision_is_occurrence": False,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W22_AUTHORITY_COORDINATE_UNPINNED", error)

    def _commit_return(self, text: str) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(_strict_loads(text), COMMIT_RETURN_FIELDS, "commit return")
        normalized = deepcopy(raw)
        if _text(normalized["schema"], "commit.schema") != COMMIT_RETURN_SCHEMA:
            raise ValueError("commit return schema mismatch")
        normalized["custody"] = _custody(normalized["custody"])
        for field in (
            "source_digest",
            "revision_digest",
            "transaction_digest",
            "authorization_digest",
            "ic10_review_packet_digest",
            "ic10_decision_digest",
            "ledger_blob_digest",
            "ledger_root_before",
            "ledger_root_after",
            "entry_digest",
            "policy_digest",
            "return_digest",
        ):
            normalized[field] = _sha(normalized[field], f"commit.{field}")
        normalized["occurrence_id"] = _identifier(
            normalized["occurrence_id"], "commit.occurrence_id"
        )
        normalized["ledger_repository"] = _text(
            normalized["ledger_repository"], "commit.ledger_repository"
        )
        normalized["ledger_ref"] = _text(
            normalized["ledger_ref"], "commit.ledger_ref"
        )
        normalized["ledger_commit"] = _commit(
            normalized["ledger_commit"], "commit.ledger_commit"
        )
        normalized["parent_commit"] = _commit(
            normalized["parent_commit"], "commit.parent_commit"
        )
        normalized["tree"] = _commit(normalized["tree"], "commit.tree")
        normalized["ledger_path"] = _text(
            normalized["ledger_path"], "commit.ledger_path"
        )
        if (
            not isinstance(normalized["sequence"], int)
            or isinstance(normalized["sequence"], bool)
            or normalized["sequence"] <= 0
        ):
            raise ValueError("commit.sequence must be a positive integer")
        if normalized["previous_entry_digest"] is not None:
            normalized["previous_entry_digest"] = _sha(
                normalized["previous_entry_digest"],
                "commit.previous_entry_digest",
            )
        normalized["nonce"] = _identifier(normalized["nonce"], "commit.nonce")
        normalized["signature"] = _signature(
            normalized["signature"], "commit.signature"
        )
        authorized = _timestamp(normalized["authorized_at"], "commit.authorized_at")
        expires = _timestamp(
            normalized["authorization_expires_at"],
            "commit.authorization_expires_at",
        )
        occurred = _timestamp(normalized["occurred_at"], "commit.occurred_at")
        if not authorized <= occurred <= expires:
            raise ValueError("commit occurrence is outside authorization window")
        _, revision = self._authority(
            normalized["source_digest"],
            normalized["revision_digest"],
            "LEDGER_COMMIT",
        )
        scope = revision["scope"]
        if (
            scope["operation"] != "ledger.commit"
            or scope["repository"] != normalized["ledger_repository"]
            or scope["ref"] != normalized["ledger_ref"]
            or scope["policy_digest"] != normalized["policy_digest"]
        ):
            raise ValueError("commit occurrence is outside authority revision scope")
        _verify(
            normalized,
            revision,
            digest_field="return_digest",
            occurred_at=normalized["occurred_at"],
        )
        return normalized, revision

    def _observation(
        self, text: str, commit_return: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(_strict_loads(text), OBSERVATION_FIELDS, "git observation")
        normalized = deepcopy(raw)
        if _text(normalized["schema"], "observation.schema") != OBSERVATION_SCHEMA:
            raise ValueError("git observation schema mismatch")
        for field in (
            "source_digest",
            "revision_digest",
            "commit_return_digest",
            "blob_digest",
            "previous_root",
            "resulting_root",
            "observation_digest",
        ):
            normalized[field] = _sha(normalized[field], f"observation.{field}")
        normalized["occurrence_id"] = _identifier(
            normalized["occurrence_id"], "observation.occurrence_id"
        )
        for field in ("commit", "parent_commit", "tree", "observed_ref_tip"):
            normalized[field] = _commit(
                normalized[field], f"observation.{field}"
            )
        for field in ("repository", "ref", "path"):
            normalized[field] = _text(
                normalized[field], f"observation.{field}"
            )
        normalized["signature"] = _signature(
            normalized["signature"], "observation.signature"
        )
        _, revision = self._authority(
            normalized["source_digest"],
            normalized["revision_digest"],
            "LEDGER_OBSERVER",
        )
        scope = revision["scope"]
        if (
            scope["operation"] != "ledger.observe"
            or scope["repository"] != normalized["repository"]
            or scope["ref"] != normalized["ref"]
        ):
            raise ValueError("Git observation is outside authority revision scope")
        expected = {
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
        }
        for key, value in expected.items():
            if normalized[key] != value:
                raise ValueError(f"Git observation does not bind commit {key}")
        _verify(
            normalized,
            revision,
            digest_field="observation_digest",
            occurred_at=normalized["observed_at"],
        )
        if _timestamp(normalized["observed_at"], "observation.observed_at") < _timestamp(
            commit_return["occurred_at"], "commit.occurred_at"
        ):
            raise ValueError("Git observation predates commit occurrence")
        return normalized, revision

    def inspect_ledger_commit_return(
        self, commit_return_json: str, git_observation_json: str
    ) -> dict[str, Any]:
        try:
            commit_return, commit_revision = self._commit_return(
                commit_return_json
            )
            observation, observer_revision = self._observation(
                git_observation_json, commit_return
            )
            if commit_revision["fingerprint"] == observer_revision["fingerprint"]:
                raise ValueError("commit and observer roles are not independent")
            occurrence = commit_return["occurrence_id"]
            existing = self.occurrences.get(occurrence)
            if existing is not None and existing != commit_return["return_digest"]:
                raise ValueError("commit occurrence equivocation")
            position = (
                commit_return["sequence"],
                commit_return["previous_entry_digest"],
            )
            at_position = self.positions.get(position)
            if at_position is not None and existing is None:
                raise ValueError("double commit at ledger position")
            return _merge(
                {
                    "status": (
                        "PASS_W22_INDEPENDENT_LEDGER_COMMIT_RETURN_AND_"
                        "GIT_OBSERVATION_VERIFIED"
                    ),
                    "source_digest": commit_return["source_digest"],
                    "revision_digest": commit_return["revision_digest"],
                    "occurrence_id": occurrence,
                    "commit_return_digest": commit_return["return_digest"],
                    "return_digest": commit_return["return_digest"],
                    "git_observation_digest": observation["observation_digest"],
                    "ledger_commit": commit_return["ledger_commit"],
                    "ledger_root": commit_return["ledger_root_after"],
                    "entry_digest": commit_return["entry_digest"],
                    "ic10_review_packet_digest": commit_return[
                        "ic10_review_packet_digest"
                    ],
                    "ic10_decision_digest": commit_return["ic10_decision_digest"],
                    "occurred_at": commit_return["occurred_at"],
                    "observed_at": observation["observed_at"],
                    "idempotent_replay": existing == commit_return["return_digest"],
                    "ledger_commit_return_verified": True,
                    "git_commit_observed": True,
                    "ledger_entry_committed": True,
                    "promotion_decision_return_verified": False,
                    "promotion_authorized": False,
                },
                _negative(),
            )
        except (
            IndependentAuthorityReturnError,
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W22_LEDGER_COMMIT_RETURN_REJECTED", error)

    def compile_ledger_candidate(
        self, commit_return_json: str, git_observation_json: str
    ) -> dict[str, Any]:
        inspected = self.inspect_ledger_commit_return(
            commit_return_json, git_observation_json
        )
        if not inspected.get("ledger_entry_committed"):
            return inspected
        previous = (
            self.snapshot["admitted_return_ledger"]["entries"][-1]["entry_digest"]
            if self.snapshot["admitted_return_ledger"]["entries"]
            else None
        )
        candidate = {
            "schema": CANDIDATE_SCHEMA,
            "sequence": len(
                self.snapshot["admitted_return_ledger"]["entries"]
            )
            + 1,
            "previous_entry_digest": previous,
            "return_kind": "LEDGER_COMMIT",
            "payload_digest": inspected["return_digest"],
            "source_digest": inspected["source_digest"],
            "revision_digest": inspected["revision_digest"],
            "occurrence_id": inspected["occurrence_id"],
            "validation": {
                "signature_verified": True,
                "scope_verified": True,
                "git_observation_verified": True,
                "candidate_persisted": False,
            },
            "candidate_digest": "",
        }
        candidate["candidate_digest"] = _digest(
            _addressed(candidate, "candidate_digest")
        )
        return _merge(
            {
                "status": (
                    "PASS_W22_LEDGER_RETURN_ADMISSION_CANDIDATE_COMPILED__"
                    "EXTERNAL_CONTROL_ADMISSION_OPEN"
                ),
                "candidate": candidate,
                "candidate_persisted": False,
                "ledger_commit_return_verified": True,
                "git_commit_observed": True,
                "ledger_entry_committed": True,
                "promotion_decision_return_verified": False,
                "promotion_authorized": False,
            },
            _negative(),
        )

    def _promotion(
        self, text: str, commit_result: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = _exact(
            _strict_loads(text), PROMOTION_RETURN_FIELDS, "promotion return"
        )
        normalized = deepcopy(raw)
        if (
            _text(normalized["schema"], "promotion.schema")
            != PROMOTION_RETURN_SCHEMA
        ):
            raise ValueError("promotion return schema mismatch")
        normalized["custody"] = _custody(normalized["custody"])
        for field in (
            "source_digest",
            "revision_digest",
            "commit_return_digest",
            "git_observation_digest",
            "ledger_root",
            "entry_digest",
            "ic10_review_packet_digest",
            "ic10_decision_digest",
            "policy_digest",
            "return_digest",
        ):
            normalized[field] = _sha(normalized[field], f"promotion.{field}")
        normalized["occurrence_id"] = _identifier(
            normalized["occurrence_id"], "promotion.occurrence_id"
        )
        normalized["nonce"] = _identifier(normalized["nonce"], "promotion.nonce")
        normalized["decision"] = _text(
            normalized["decision"], "promotion.decision"
        )
        if normalized["decision"] not in DECISIONS:
            raise ValueError("promotion decision is not allowed")
        target = _exact(normalized["target"], TARGET_FIELDS, "promotion.target")
        normalized["target"] = {
            "runtime_repository": _text(
                target["runtime_repository"], "target.runtime_repository"
            ),
            "runtime_head": _commit(target["runtime_head"], "target.runtime_head"),
            "candidate_image_id": _sha(
                target["candidate_image_id"], "target.candidate_image_id"
            ),
            "target_environment": _identifier(
                target["target_environment"], "target.target_environment"
            ),
            "target_ref": _text(target["target_ref"], "target.target_ref"),
        }
        normalized["signature"] = _signature(
            normalized["signature"], "promotion.signature"
        )
        for field in (
            "commit_return_digest",
            "git_observation_digest",
            "ledger_root",
            "entry_digest",
            "ic10_review_packet_digest",
            "ic10_decision_digest",
        ):
            if normalized[field] != commit_result[field]:
                raise ValueError(f"promotion return does not bind verified {field}")
        _, revision = self._authority(
            normalized["source_digest"],
            normalized["revision_digest"],
            "PROMOTION_DECISION",
        )
        scope = revision["scope"]
        target = normalized["target"]
        if (
            scope["operation"] != "promotion.policy"
            or scope["repository"] != target["runtime_repository"]
            or scope["ref"] != target["target_ref"]
            or scope["environment"] != target["target_environment"]
            or scope["target_head"] != target["runtime_head"]
            or scope["target_image_id"] != target["candidate_image_id"]
            or scope["policy_digest"] != normalized["policy_digest"]
        ):
            raise ValueError("promotion return is outside authority revision scope")
        if (
            target["runtime_repository"] != "demeet2k/athena-mcp-server"
            or target["runtime_head"] != W20_TARGET_HEAD
            or target["candidate_image_id"] != W21_CANDIDATE_IMAGE
        ):
            raise ValueError("promotion target is not the exact W20 candidate")
        if target["runtime_head"] == W21_HEAD:
            raise ValueError("W21 custody revision cannot be promotion target")
        _verify(
            normalized,
            revision,
            digest_field="return_digest",
            occurred_at=normalized["decided_at"],
        )
        if _timestamp(normalized["decided_at"], "promotion.decided_at") < _timestamp(
            commit_result["observed_at"], "commit.observed_at"
        ):
            raise ValueError("promotion decision predates observed ledger commit")
        return normalized, revision

    def inspect_promotion_return(
        self,
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> dict[str, Any]:
        commit_result = self.inspect_ledger_commit_return(
            commit_return_json, git_observation_json
        )
        if not commit_result.get("ledger_entry_committed"):
            return commit_result
        try:
            commit_return, commit_revision = self._commit_return(
                commit_return_json
            )
            observation, observer_revision = self._observation(
                git_observation_json, commit_return
            )
            promotion, promotion_revision = self._promotion(
                promotion_return_json, commit_result
            )
            if promotion_revision["fingerprint"] in {
                commit_revision["fingerprint"],
                observer_revision["fingerprint"],
            }:
                raise ValueError("promotion authority is not independent")
            authorized = promotion["decision"] == "AUTHORIZE_PROMOTION"
            status = (
                "PASS_W22_INDEPENDENT_COMMIT_AND_PROMOTION_DECISION_RETURNS_"
                "VERIFIED__CONTROL_ADMISSION_AND_PROMOTION_EXECUTION_OPEN"
                if authorized
                else "PASS_W22_INDEPENDENT_COMMIT_RETURN_VERIFIED__"
                "PROMOTION_HELD__NO_EXECUTION_AUTHORITY"
            )
            return _merge(
                {
                    "status": status,
                    "source_digest": promotion["source_digest"],
                    "revision_digest": promotion["revision_digest"],
                    "occurrence_id": promotion["occurrence_id"],
                    "return_digest": promotion["return_digest"],
                    "commit_return_digest": commit_return["return_digest"],
                    "git_observation_digest": observation["observation_digest"],
                    "ledger_root": commit_return["ledger_root_after"],
                    "entry_digest": commit_return["entry_digest"],
                    "ic10_review_packet_digest": commit_return[
                        "ic10_review_packet_digest"
                    ],
                    "ic10_decision_digest": commit_return["ic10_decision_digest"],
                    "decision": promotion["decision"],
                    "decided_at": promotion["decided_at"],
                    "ledger_commit_return_verified": True,
                    "git_commit_observed": True,
                    "ledger_entry_committed": True,
                    "promotion_decision_return_verified": True,
                    "promotion_authorized": authorized,
                    "execution_receipt_open": authorized,
                },
                _negative(),
            )
        except (
            IndependentAuthorityReturnError,
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W22_PROMOTION_DECISION_RETURN_REJECTED", error)

    def compile_promotion_candidate(
        self,
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> dict[str, Any]:
        inspected = self.inspect_promotion_return(
            commit_return_json, git_observation_json, promotion_return_json
        )
        if not inspected.get("promotion_decision_return_verified"):
            return inspected
        previous = (
            self.snapshot["admitted_return_ledger"]["entries"][-1]["entry_digest"]
            if self.snapshot["admitted_return_ledger"]["entries"]
            else None
        )
        candidate = {
            "schema": CANDIDATE_SCHEMA,
            "sequence": len(
                self.snapshot["admitted_return_ledger"]["entries"]
            )
            + 1,
            "previous_entry_digest": previous,
            "return_kind": "PROMOTION_DECISION",
            "payload_digest": inspected["return_digest"],
            "source_digest": inspected["source_digest"],
            "revision_digest": inspected["revision_digest"],
            "occurrence_id": inspected["occurrence_id"],
            "validation": {
                "commit_and_observation_verified": True,
                "signature_verified": True,
                "scope_verified": True,
                "candidate_persisted": False,
            },
            "candidate_digest": "",
        }
        candidate["candidate_digest"] = _digest(
            _addressed(candidate, "candidate_digest")
        )
        return _merge(
            {
                "status": (
                    "PASS_W22_PROMOTION_RETURN_ADMISSION_CANDIDATE_COMPILED__"
                    "EXTERNAL_CONTROL_ADMISSION_OPEN"
                ),
                "candidate": candidate,
                "decision": inspected["decision"],
                "candidate_persisted": False,
                "ledger_commit_return_verified": True,
                "git_commit_observed": True,
                "ledger_entry_committed": True,
                "promotion_decision_return_verified": True,
                "promotion_authorized": inspected["promotion_authorized"],
            },
            _negative(),
        )

    def inspect_correction(self, correction_json: str) -> dict[str, Any]:
        try:
            raw = _exact(
                _strict_loads(correction_json), CORRECTION_FIELDS, "correction"
            )
            correction = deepcopy(raw)
            if correction["schema"] != CORRECTION_SCHEMA:
                raise ValueError("correction schema mismatch")
            for field in (
                "previous_correction_digest",
                "corrects_return_digest",
                "corrected_revision_digest",
                "replacement_return_digest",
                "source_digest",
                "revision_digest",
                "correction_digest",
            ):
                if correction[field] is not None:
                    correction[field] = _sha(
                        correction[field], f"correction.{field}"
                    )
            correction["stream_id"] = _identifier(
                correction["stream_id"], "correction.stream_id"
            )
            correction["occurrence_id"] = _identifier(
                correction["occurrence_id"], "correction.occurrence_id"
            )
            correction["reason_code"] = _identifier(
                correction["reason_code"], "correction.reason_code"
            )
            if (
                not isinstance(correction["sequence"], int)
                or isinstance(correction["sequence"], bool)
                or correction["sequence"] <= 0
            ):
                raise ValueError("correction.sequence must be positive")
            correction["signature"] = _signature(
                correction["signature"], "correction.signature"
            )
            _, revision = self._authority(
                correction["source_digest"],
                correction["revision_digest"],
                "CORRECTION",
            )
            if revision["scope"]["operation"] != "return.correct":
                raise ValueError("correction authority lacks return.correct scope")
            if (
                correction["corrects_return_digest"]
                == correction["replacement_return_digest"]
            ):
                raise ValueError("correction cannot be an in-place no-op")
            if correction["reason_code"] == "ERASE_LEDGER_COMMIT":
                raise ValueError("a correction cannot erase a commit occurrence")
            _verify(
                correction,
                revision,
                digest_field="correction_digest",
                occurred_at=correction["occurred_at"],
            )
            return _merge(
                {
                    "status": (
                        "PASS_W22_CORRECTION_FORWARD_VERIFIED__"
                        "HISTORICAL_OCCURRENCE_PRESERVED"
                    ),
                    "correction_digest": correction["correction_digest"],
                    "replacement_return_digest": correction[
                        "replacement_return_digest"
                    ],
                    "historical_occurrence_erased": False,
                    "candidate_persisted": False,
                },
                _negative(),
            )
        except (
            IndependentAuthorityReturnError,
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W22_CORRECTION_FORWARD_REJECTED", error)

    def resolve_effective_returns(self, entries_json: str) -> dict[str, Any]:
        try:
            entries = _strict_loads(entries_json, object_required=False)
            if not isinstance(entries, list):
                raise ValueError("entries must be a JSON array")
            seen_occurrences: dict[str, str] = {}
            positions: dict[tuple[Any, Any], str] = {}
            previous = None
            effective: dict[str, str] = {}
            for expected_sequence, entry in enumerate(entries, 1):
                if not isinstance(entry, dict):
                    raise ValueError("ledger entry must be object")
                required = {
                    "schema",
                    "sequence",
                    "previous_entry_digest",
                    "kind",
                    "source_digest",
                    "revision_digest",
                    "occurrence_id",
                    "payload_digest",
                    "entry_digest",
                }
                _exact(entry, required, "return-ledger entry")
                if entry["schema"] != LEDGER_ENTRY_SCHEMA:
                    raise ValueError("return-ledger schema mismatch")
                if (
                    entry["sequence"] != expected_sequence
                    or entry["previous_entry_digest"] != previous
                ):
                    raise ValueError("return-ledger sequence/chain mismatch")
                if entry["entry_digest"] != _digest(
                    _addressed(entry, "entry_digest")
                ):
                    raise ValueError("return-ledger entry digest mismatch")
                occurrence = _identifier(
                    entry["occurrence_id"], "entry.occurrence_id"
                )
                payload = _sha(entry["payload_digest"], "entry.payload_digest")
                if occurrence in seen_occurrences:
                    if seen_occurrences[occurrence] != payload:
                        raise ValueError("occurrence equivocation")
                    continue
                position = (entry["sequence"], entry["previous_entry_digest"])
                if position in positions:
                    raise ValueError("conflicting entry at return-ledger position")
                seen_occurrences[occurrence] = payload
                positions[position] = entry["entry_digest"]
                effective[occurrence] = payload
                previous = entry["entry_digest"]
            return _merge(
                {
                    "status": "PASS_W22_UNIQUE_APPEND_ONLY_RETURN_CHAIN_RESOLVED",
                    "entry_count": len(entries),
                    "effective_occurrences": effective,
                    "tip_digest": previous,
                },
                _negative(),
            )
        except (
            IndependentAuthorityReturnError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W22_RETURN_CHAIN_REJECTED", error)

    def evaluate_closure(
        self,
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> dict[str, Any]:
        return self.inspect_promotion_return(
            commit_return_json,
            git_observation_json,
            promotion_return_json,
        )

    def explain_coordinate_separation(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W22_COORDINATE_LAW_EXPLAINED",
                "coordinate": "X=<S,R,O>",
                "source": "stable authority identity, role, governance, and scope kind",
                "revision": (
                    "immutable repository/ref/commit/tree/path/blob/content/key/"
                    "policy coordinate"
                ),
                "occurrence": (
                    "signed event binding one pinned source and revision to exact facts"
                ),
                "projection_law": (
                    "each projection is non-injective; lost coordinates must travel "
                    "as complement witnesses"
                ),
                "custody_is_authority": False,
                "decision_is_execution": False,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_independent_authority_return(mcp: Any) -> None:
    """Register eleven W22 tools and the frozen production-empty resource."""
    gate = FrozenIndependentAuthorityReturn.load()

    @mcp.tool()
    def athena_w22_independent_authority_return_status() -> str:
        """Return W22 custody, registry, ledger, and boundary coordinates."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w22_w21_custody_transition() -> str:
        """Inspect exact W21 custody evidence; it grants no authority."""
        return _render(
            {
                **gate.status(),
                "status": "PASS_W22_W21_CUSTODY_PINNED__NO_AUTHORITY_GRANTED",
            }
        )

    @mcp.tool()
    def inspect_athena_w22_authority_source_revision(
        source_digest: str, revision_digest: str
    ) -> str:
        """Inspect one pinned source/revision coordinate."""
        return _render(gate.inspect_source_revision(source_digest, revision_digest))

    @mcp.tool()
    def inspect_athena_w22_ledger_commit_return(
        commit_return_json: str, git_observation_json: str
    ) -> str:
        """Verify independent commit attestation plus Git observation."""
        return _render(
            gate.inspect_ledger_commit_return(
                commit_return_json, git_observation_json
            )
        )

    @mcp.tool()
    def compile_athena_w22_ledger_return_admission_candidate(
        commit_return_json: str, git_observation_json: str
    ) -> str:
        """Compile, but never persist, a ledger-return admission candidate."""
        return _render(
            gate.compile_ledger_candidate(
                commit_return_json, git_observation_json
            )
        )

    @mcp.tool()
    def inspect_athena_w22_promotion_decision_return(
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> str:
        """Verify a promotion decision only after exact commit verification."""
        return _render(
            gate.inspect_promotion_return(
                commit_return_json,
                git_observation_json,
                promotion_return_json,
            )
        )

    @mcp.tool()
    def compile_athena_w22_promotion_return_admission_candidate(
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> str:
        """Compile, but never persist or execute, a promotion decision candidate."""
        return _render(
            gate.compile_promotion_candidate(
                commit_return_json,
                git_observation_json,
                promotion_return_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w22_correction_forward(correction_json: str) -> str:
        """Verify append-only correction-forward without erasing history."""
        return _render(gate.inspect_correction(correction_json))

    @mcp.tool()
    def resolve_athena_w22_effective_authority_returns(
        entries_json: str,
    ) -> str:
        """Replay one unique content-addressed return-ledger chain."""
        return _render(gate.resolve_effective_returns(entries_json))

    @mcp.tool()
    def evaluate_athena_w22_independent_authority_return_closure(
        commit_return_json: str,
        git_observation_json: str,
        promotion_return_json: str,
    ) -> str:
        """Evaluate commit plus promotion-policy closure, never execution."""
        return _render(
            gate.evaluate_closure(
                commit_return_json,
                git_observation_json,
                promotion_return_json,
            )
        )

    @mcp.tool()
    def explain_athena_w22_coordinate_separation() -> str:
        """Explain the source/revision/occurrence coordinate law."""
        return _render(gate.explain_coordinate_separation())

    @mcp.resource("athena://w22-independent-authority-return")
    def independent_authority_return_resource() -> str:
        """Read the frozen W22 contract and production-empty registries."""
        return _render(gate.snapshot)
