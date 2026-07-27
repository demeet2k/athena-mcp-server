"""KC144 W25 persistent return and promotion-settlement verifier.

The runtime verifies externally signed persistence and settlement records. It
cannot persist, issue signatures, dispatch, contact an endpoint, execute,
roll back, merge, deploy, or promote.
"""

from __future__ import annotations

import base64
from copy import deepcopy
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
    _strict_loads,
    _text,
    _timestamp,
)
from .promotion_execution_handoff import _target, _verify
from .execution_deployment_rollback_readback import (
    FrozenExecutionDeploymentRollbackReadback,
)


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w25_persistent_promotion_settlement.json"
)
SCHEMA = "athena.xnav-w25-persistent-promotion-settlement/v1"
PHASE = "KC144.XNAV.W25"

SOURCE_SCHEMA = "athena.w25-settlement-authority-source/v1"
REVISION_SCHEMA = "athena.w25-settlement-authority-revision/v1"
PERSISTENCE_PROOF_SCHEMA = "athena.w25-return-persistence-proof/v1"
PERSISTENCE_OBSERVATION_SCHEMA = (
    "athena.w25-return-persistence-observation/v1"
)
SETTLEMENT_SCHEMA = "athena.w25-promotion-settlement/v1"
SETTLEMENT_OBSERVATION_SCHEMA = (
    "athena.w25-promotion-settlement-observation/v1"
)
CLOSURE_SCHEMA = "athena.w25-persistent-promotion-settlement-closure/v1"
BUNDLE_SCHEMA = "athena.w25-w24-return-bundle/v1"

W24_HEAD = "6906afa2cab034f51ae7d86aae409bf0a6304a91"
W24_TREE = "e571caf572a7ee4baa553016c0f9e7315551ecab"
W24_PARENT = "3061598cd050aa6b8ad8b647e86c2295acb54228"
W24_CONTRACT = (
    "sha256:dc316ded97c885e0febe36b558d7bb17468f629988b20dd49723a1ed586b35b4"
)
W24_RECEIPT = (
    "w24-return-readback:sha256:"
    "4e013a8505042a23b373d2ab5ade474cb16a4a95d58fc9251ae62ac05963e539"
)
W24_LOCAL_IMAGE = (
    "sha256:dad2c2dbcaa8a62d24cf196791a897f359e772526d17ad35b3fd65ed69481f3f"
)

ROLES = {
    "RETURN_PERSISTENCE_WRITER": "settlement.return.persist",
    "RETURN_PERSISTENCE_OBSERVER": "settlement.return.observe",
    "PROMOTION_SETTLEMENT_ISSUER": "settlement.promotion.issue",
    "PROMOTION_SETTLEMENT_OBSERVER": "settlement.promotion.observe",
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
PERSISTENCE_PROOF_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "w24_return_bundle_digest",
    "w24_closure_certificate_digest",
    "w24_rollback_observation_digest",
    "target",
    "object_digest",
    "object_size_bytes",
    "storage_class",
    "immutable_locator_hash",
    "persisted_at",
    "retention_until",
    "signature",
    "persistence_proof_digest",
}
PERSISTENCE_OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "persistence_proof_digest",
    "object_digest",
    "immutable_locator_hash",
    "readback_digest",
    "target",
    "observed_state",
    "observed_at",
    "signature",
    "persistence_observation_digest",
}
SETTLEMENT_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "settlement_id",
    "w24_closure_certificate_digest",
    "persistence_observation_digest",
    "target",
    "terminal_image_digest",
    "terminal_state",
    "promotion_disposition",
    "issued_at",
    "signature",
    "promotion_settlement_digest",
}
SETTLEMENT_OBSERVATION_FIELDS = {
    "schema",
    "source_digest",
    "revision_digest",
    "occurrence_id",
    "promotion_settlement_digest",
    "persistence_observation_digest",
    "target",
    "terminal_image_digest",
    "observed_disposition",
    "external_ledger_digest",
    "observed_at",
    "signature",
    "settlement_observation_digest",
}


class PersistentPromotionSettlementError(RuntimeError):
    """Frozen W25 contract or authority registry is invalid."""


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


def _negative() -> dict[str, bool | None]:
    return {
        "runtime_mutated_registry": False,
        "runtime_issued_authority_signature": False,
        "runtime_persisted_return": False,
        "runtime_issued_settlement": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "w24_return_bundle_verified": False,
        "return_persistence_proved": False,
        "return_persistence_observed": False,
        "promotion_settlement_verified": False,
        "settlement_observation_verified": False,
        "settlement_disposition": None,
        "merge_claimed": False,
        "deployment_claimed": False,
        "promotion_claimed": False,
    }


class FrozenPersistentPromotionSettlement:
    """Verify W25 persistence/settlement against frozen W24 returns."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w24_gate: FrozenExecutionDeploymentRollbackReadback | None = None,
    ):
        self.snapshot = deepcopy(snapshot)
        self.w24_gate = (
            w24_gate or FrozenExecutionDeploymentRollbackReadback.load()
        )
        try:
            self._validate_snapshot()
        except (KeyError, LookupError, TypeError, ValueError) as error:
            raise PersistentPromotionSettlementError(str(error)) from error

    @classmethod
    def load(cls) -> "FrozenPersistentPromotionSettlement":
        return cls(_strict_loads(DATA_PATH.read_text(encoding="utf-8")))

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w24_gate: FrozenExecutionDeploymentRollbackReadback | None = None,
    ) -> "FrozenPersistentPromotionSettlement":
        return cls(snapshot, w24_gate=w24_gate)

    def _validate_snapshot(self) -> None:
        if self.snapshot.get("schema") != SCHEMA or self.snapshot.get("phase") != PHASE:
            raise ValueError("W25 schema/phase mismatch")
        predecessor = self.snapshot["predecessor"]
        exact = {
            "w24_head": W24_HEAD,
            "w24_tree": W24_TREE,
            "w24_sole_parent": W24_PARENT,
            "w24_contract_digest": W24_CONTRACT,
            "w24_receipt_id": W24_RECEIPT,
        }
        if {key: predecessor.get(key) for key in exact} != exact:
            raise ValueError("W24 predecessor mismatch")
        if predecessor.get("w24_image_published") is not False:
            raise ValueError("W24 workflow-local image must remain unpublished")
        control = self.snapshot["control_predecessor_observation"]
        if (
            control.get("head")
            != "b02329d006622ff6e524b197f3a87c033abd8c3b"
            or control.get("receipt_id")
            != (
                "w24-control-admission:sha256:"
                "a73dbc1aaf7e87ccefaf3e40f107301e14d1d1ff88439990e919ad2537a8f41d"
            )
            or control.get("grants_production_authority") is not False
        ):
            raise ValueError("control predecessor mismatch")
        contract = self.snapshot["settlement_contract"]
        if (
            contract.get("total_cross_wave_roles") != 17
            or contract.get("rollback_terminal_state_must_settle_as")
            != "REJECTED_ROLLED_BACK"
            or contract.get("rollback_may_be_reclassified_as_promotion")
            is not False
            or contract.get("minimum_retention_seconds") != 31536000
        ):
            raise ValueError("settlement contract boundary mismatch")
        registry = self.snapshot["authority_registry"]
        if set(registry) != {"sources", "revisions"}:
            raise ValueError("authority registry shape mismatch")
        self.sources: dict[str, dict[str, Any]] = {}
        self.revisions: dict[str, dict[str, Any]] = {}
        earlier_sources = list(self.w24_gate.w23_gate.sources.values()) + list(
            self.w24_gate.sources.values()
        )
        earlier_revisions = list(
            self.w24_gate.w23_gate.revisions.values()
        ) + list(self.w24_gate.revisions.values())
        identities: dict[str, str] = {
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
        for raw in registry["sources"]:
            source = _source(raw)
            if source["source_digest"] in self.sources:
                raise ValueError("duplicate authority source")
            if source["authority_id"] in identities:
                raise ValueError("authority identity overlaps W23/W24/W25 roles")
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
                    raise ValueError(f"{label} overlaps W23/W24/W25 roles")
                aliases[alias] = revision["role"]
            self.revisions[revision["revision_digest"]] = revision
        for name in (
            "persistence_proof_ledger",
            "persistence_observation_ledger",
            "promotion_settlement_ledger",
            "settlement_observation_ledger",
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
            raise ValueError("W25 contract digest mismatch")

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
            raise ValueError("settlement record outside authority scope")

    def _hold(self, status: str, error: Exception | str) -> dict[str, Any]:
        return _merge({"status": status, "error": str(error)}, _negative())

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W25_W24_CUSTODY_PINNED__PERSISTENCE_AND_PROMOTION_"
                    "SETTLEMENT_RETURNS_OPEN"
                ),
                "phase": PHASE,
                "w24_head": W24_HEAD,
                "w24_tree": W24_TREE,
                "w24_contract_digest": W24_CONTRACT,
                "w24_receipt_id": W24_RECEIPT,
                "w24_image_published": False,
                "authority_source_count": len(self.sources),
                "authority_revision_count": len(self.revisions),
                "persistence_proof_count": 0,
                "persistence_observation_count": 0,
                "promotion_settlement_count": 0,
                "settlement_observation_count": 0,
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
                    "status": "PASS_W25_AUTHORITY_SOURCE_REVISION_PINNED",
                    "source": source,
                    "revision": revision,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return self._hold("HOLD_W25_AUTHORITY_COORDINATE_UNPINNED", error)

    def _w24(self, record_jsons: tuple[str, ...]) -> dict[str, Any]:
        if len(record_jsons) != 13:
            raise ValueError("W24 return topology requires exactly 13 records")
        closure = self.w24_gate.evaluate_closure(*record_jsons)
        if (
            closure.get("rollback_observation_verified") is not True
            or closure.get("promotion_claimed") is not False
            or closure.get("closure_certificate", {}).get("settlement_state")
            != "ROLLED_BACK_TO_PREVIOUS_SAFE_IMAGE"
        ):
            raise ValueError("complete W24 rollback-terminal closure not verified")
        (
            w23,
            _execution,
            _promotion,
            _deployment,
            _health,
            _rollback_authorization,
            _rollback_occurrence,
            rollback_observation,
        ) = self.w24_gate._all(*record_jsons)
        certificate = closure["closure_certificate"]
        bundle = {
            "schema": BUNDLE_SCHEMA,
            "records": [_strict_loads(text) for text in record_jsons],
        }
        return {
            "target": w23["target"],
            "policy_digest": w23["policy_digest"],
            "closure_certificate_digest": _sha(
                certificate["certificate_digest"],
                "w24.closure_certificate_digest",
            ),
            "return_bundle_digest": _digest(bundle),
            "rollback_observation_digest": rollback_observation[
                "rollback_observation_digest"
            ],
            "terminal_image_digest": rollback_observation[
                "observed_image_digest"
            ],
            "terminal_observed_at": rollback_observation["observed_at"],
        }

    def _persistence_proof(
        self, text: str, w24: dict[str, Any]
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=PERSISTENCE_PROOF_FIELDS,
            schema=PERSISTENCE_PROOF_SCHEMA,
            digest_fields=(
                "w24_return_bundle_digest",
                "w24_closure_certificate_digest",
                "w24_rollback_observation_digest",
                "object_digest",
                "immutable_locator_hash",
                "persistence_proof_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="persistence_proof_digest",
        )
        if (
            record["w24_return_bundle_digest"] != w24["return_bundle_digest"]
            or record["w24_closure_certificate_digest"]
            != w24["closure_certificate_digest"]
            or record["w24_rollback_observation_digest"]
            != w24["rollback_observation_digest"]
            or record["object_digest"] != w24["return_bundle_digest"]
            or record["target"] != w24["target"]
            or record["storage_class"] != "CONTENT_ADDRESSED_IMMUTABLE"
            or type(record["object_size_bytes"]) is not int
            or not 1 <= record["object_size_bytes"] <= 1073741824
        ):
            raise ValueError("persistence proof bindings invalid")
        persisted = _timestamp(record["persisted_at"], "persistence.persisted_at")
        retention = _timestamp(
            record["retention_until"], "persistence.retention_until"
        )
        if (
            persisted
            < _timestamp(w24["terminal_observed_at"], "w24.terminal_observed_at")
            or (retention - persisted).total_seconds() < 31536000
        ):
            raise ValueError("persistence chronology/retention invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "RETURN_PERSISTENCE_WRITER",
        )
        self._scope(
            revision,
            target=record["target"],
            policy_digest=w24["policy_digest"],
        )
        _verify(
            record,
            revision,
            "persistence_proof_digest",
            record["persisted_at"],
        )
        return record

    def _persistence_observation(
        self,
        text: str,
        w24: dict[str, Any],
        proof: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=PERSISTENCE_OBSERVATION_FIELDS,
            schema=PERSISTENCE_OBSERVATION_SCHEMA,
            digest_fields=(
                "persistence_proof_digest",
                "object_digest",
                "immutable_locator_hash",
                "readback_digest",
                "persistence_observation_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="persistence_observation_digest",
        )
        if (
            record["persistence_proof_digest"]
            != proof["persistence_proof_digest"]
            or record["object_digest"] != proof["object_digest"]
            or record["immutable_locator_hash"]
            != proof["immutable_locator_hash"]
            or record["readback_digest"] != proof["object_digest"]
            or record["target"] != w24["target"]
            or record["observed_state"] != "PERSISTED"
            or _timestamp(record["observed_at"], "persistence.observed_at")
            < _timestamp(proof["persisted_at"], "persistence.persisted_at")
        ):
            raise ValueError("persistence observation bindings invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "RETURN_PERSISTENCE_OBSERVER",
        )
        self._scope(
            revision,
            target=record["target"],
            policy_digest=w24["policy_digest"],
        )
        _verify(
            record,
            revision,
            "persistence_observation_digest",
            record["observed_at"],
        )
        return record

    def _settlement(
        self,
        text: str,
        w24: dict[str, Any],
        observation: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=SETTLEMENT_FIELDS,
            schema=SETTLEMENT_SCHEMA,
            digest_fields=(
                "w24_closure_certificate_digest",
                "persistence_observation_digest",
                "terminal_image_digest",
                "promotion_settlement_digest",
            ),
            id_fields=("settlement_id",),
            digest_field="promotion_settlement_digest",
        )
        if (
            record["w24_closure_certificate_digest"]
            != w24["closure_certificate_digest"]
            or record["persistence_observation_digest"]
            != observation["persistence_observation_digest"]
            or record["target"] != w24["target"]
            or record["terminal_image_digest"]
            != w24["terminal_image_digest"]
            or record["terminal_state"]
            != "ROLLED_BACK_TO_PREVIOUS_SAFE_IMAGE"
            or record["promotion_disposition"] != "REJECTED_ROLLED_BACK"
            or _timestamp(record["issued_at"], "settlement.issued_at")
            < _timestamp(observation["observed_at"], "persistence.observed_at")
        ):
            raise ValueError(
                "rollback-terminal promotion settlement bindings invalid"
            )
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "PROMOTION_SETTLEMENT_ISSUER",
        )
        self._scope(
            revision,
            target=record["target"],
            policy_digest=w24["policy_digest"],
        )
        _verify(
            record,
            revision,
            "promotion_settlement_digest",
            record["issued_at"],
        )
        return record

    def _settlement_observation(
        self,
        text: str,
        w24: dict[str, Any],
        persistence: dict[str, Any],
        settlement: dict[str, Any],
    ) -> dict[str, Any]:
        record = _record(
            text,
            fields=SETTLEMENT_OBSERVATION_FIELDS,
            schema=SETTLEMENT_OBSERVATION_SCHEMA,
            digest_fields=(
                "promotion_settlement_digest",
                "persistence_observation_digest",
                "terminal_image_digest",
                "external_ledger_digest",
                "settlement_observation_digest",
            ),
            id_fields=("occurrence_id",),
            digest_field="settlement_observation_digest",
        )
        if (
            record["promotion_settlement_digest"]
            != settlement["promotion_settlement_digest"]
            or record["persistence_observation_digest"]
            != persistence["persistence_observation_digest"]
            or record["target"] != w24["target"]
            or record["terminal_image_digest"]
            != settlement["terminal_image_digest"]
            or record["observed_disposition"] != "REJECTED_ROLLED_BACK"
            or _timestamp(record["observed_at"], "settlement.observed_at")
            < _timestamp(settlement["issued_at"], "settlement.issued_at")
        ):
            raise ValueError("settlement observation bindings invalid")
        _, revision = self._authority(
            record["source_digest"],
            record["revision_digest"],
            "PROMOTION_SETTLEMENT_OBSERVER",
        )
        self._scope(
            revision,
            target=record["target"],
            policy_digest=w24["policy_digest"],
        )
        _verify(
            record,
            revision,
            "settlement_observation_digest",
            record["observed_at"],
        )
        return record

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
        persistence_proof_json: str,
        persistence_observation_json: str,
        settlement_json: str,
        settlement_observation_json: str,
    ) -> dict[str, Any]:
        try:
            w24 = self._w24(
                (
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
            proof = self._persistence_proof(persistence_proof_json, w24)
            persistence = self._persistence_observation(
                persistence_observation_json, w24, proof
            )
            settlement = self._settlement(settlement_json, w24, persistence)
            observation = self._settlement_observation(
                settlement_observation_json,
                w24,
                persistence,
                settlement,
            )
            certificate = {
                "schema": CLOSURE_SCHEMA,
                "w24_return_bundle_digest": w24["return_bundle_digest"],
                "w24_closure_certificate_digest": w24[
                    "closure_certificate_digest"
                ],
                "persistence_proof_digest": proof[
                    "persistence_proof_digest"
                ],
                "persistence_observation_digest": persistence[
                    "persistence_observation_digest"
                ],
                "promotion_settlement_digest": settlement[
                    "promotion_settlement_digest"
                ],
                "settlement_observation_digest": observation[
                    "settlement_observation_digest"
                ],
                "target": w24["target"],
                "terminal_image_digest": w24["terminal_image_digest"],
                "promotion_disposition": "REJECTED_ROLLED_BACK",
            }
            certificate["certificate_digest"] = _digest(certificate)
            return _merge(
                {
                    "status": (
                        "PASS_W25_W24_RETURNS_PERSISTED_AND_PROMOTION_"
                        "REJECTION_SETTLED__CONTROL_LEDGER_ADMISSION_OPEN"
                    ),
                    "closure_certificate": certificate,
                    "target": w24["target"],
                    "w24_return_bundle_verified": True,
                    "return_persistence_proved": True,
                    "return_persistence_observed": True,
                    "promotion_settlement_verified": True,
                    "settlement_observation_verified": True,
                    "settlement_disposition": "REJECTED_ROLLED_BACK",
                    "workflow_dispatched": False,
                    "endpoint_contacted": False,
                    "merge_claimed": False,
                    "deployment_claimed": False,
                    "promotion_claimed": False,
                },
                {
                    "runtime_mutated_registry": False,
                    "runtime_issued_authority_signature": False,
                    "runtime_persisted_return": False,
                    "runtime_issued_settlement": False,
                },
            )
        except (
            json.JSONDecodeError,
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return self._hold("HOLD_W25_PERSISTENT_SETTLEMENT_REJECTED", error)

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W25_PERSISTENT_SETTLEMENT_LAW_EXPLAINED",
                "law": (
                    "W24 CLOSURE != EXTERNAL PERSISTENCE; PERSISTENCE PROOF != "
                    "INDEPENDENT READBACK; SETTLEMENT ISSUANCE != INDEPENDENT "
                    "SETTLEMENT OBSERVATION; ROLLBACK TERMINAL STATE CANNOT BE "
                    "RECLASSIFIED AS SUCCESSFUL PROMOTION"
                ),
                "required_roles": list(ROLES),
                "total_cross_wave_roles": 17,
                "rollback_disposition": "REJECTED_ROLLED_BACK",
                "runtime_is_verifier_only": True,
                "runtime_persists": False,
                "runtime_issues_settlement": False,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_persistent_promotion_settlement(mcp: Any) -> None:
    """Register seven W25 tools and one frozen resource."""
    gate = FrozenPersistentPromotionSettlement.load()

    @mcp.tool()
    def athena_w25_persistent_promotion_settlement_status() -> str:
        """Return W25 frozen-empty persistence and settlement boundaries."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w25_w24_custody() -> str:
        """Inspect exact W24 custody; it grants no settlement authority."""
        result = gate.status()
        result["status"] = "PASS_W25_W24_CUSTODY_PINNED__NO_AUTHORITY_GRANTED"
        return _render(result)

    @mcp.tool()
    def inspect_athena_w25_authority_source_revision(
        source_digest: str, revision_digest: str
    ) -> str:
        """Inspect one pinned W25 persistence/settlement authority."""
        return _render(gate.inspect_source_revision(source_digest, revision_digest))

    @mcp.tool()
    def inspect_athena_w25_return_persistence_contract() -> str:
        """Inspect content-addressed persistence and readback requirements."""
        return _render(
            {
                "proof_schema": PERSISTENCE_PROOF_SCHEMA,
                "observation_schema": PERSISTENCE_OBSERVATION_SCHEMA,
                "writer_role": "RETURN_PERSISTENCE_WRITER",
                "observer_role": "RETURN_PERSISTENCE_OBSERVER",
                "minimum_retention_seconds": 31536000,
                "raw_storage_locator_recorded": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def inspect_athena_w25_promotion_settlement_contract() -> str:
        """Inspect rollback-terminal promotion-settlement requirements."""
        return _render(
            {
                "settlement_schema": SETTLEMENT_SCHEMA,
                "observation_schema": SETTLEMENT_OBSERVATION_SCHEMA,
                "issuer_role": "PROMOTION_SETTLEMENT_ISSUER",
                "observer_role": "PROMOTION_SETTLEMENT_OBSERVER",
                "required_disposition": "REJECTED_ROLLED_BACK",
                "rollback_may_be_reclassified_as_promotion": False,
                **_negative(),
            }
        )

    @mcp.tool()
    def evaluate_athena_w25_persistent_promotion_settlement(
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
        persistence_proof_json: str,
        persistence_observation_json: str,
        settlement_json: str,
        settlement_observation_json: str,
    ) -> str:
        """Verify all W24/W25 records without performing any side effect."""
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
                persistence_proof_json,
                persistence_observation_json,
                settlement_json,
                settlement_observation_json,
            )
        )

    @mcp.tool()
    def explain_athena_w25_persistent_settlement_separation_law() -> str:
        """Explain persistence/readback/settlement separation."""
        return _render(gate.explain())

    @mcp.resource("athena://w25-persistent-promotion-settlement")
    def persistent_promotion_settlement_resource() -> str:
        """Read the frozen W25 contract and production-empty ledgers."""
        return _render(gate.snapshot)
