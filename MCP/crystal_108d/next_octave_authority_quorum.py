"""KC144 XNAV W32 next-octave authority and independent IC10 quorum gate.

The runtime verifies a complete W27-W31 signed closure followed by six
identity/key-disjoint W32 authority and quorum records.  It cannot create or
mutate a production registry, cast an IC10 vote, write a quorum ledger, merge,
deploy, or promote.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .five_wave_review_closure import (
    FrozenFiveWaveReviewClosure,
    W27_W31_CONTRACT,
)
from .independent_authority_return import (
    _addressed,
    _commit,
    _digest,
    _exact,
    _identifier,
    _sha,
    _strict_loads,
    _text,
    _timestamp,
)
from .promotion_execution_handoff import _verify


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w32_next_octave_authority_quorum.json"
)
SCHEMA = "athena.xnav-w32-next-octave-authority-quorum/v1"
PHASE = "KC144.XNAV.W32"
TITLE = (
    "OPEN-NEXT-OCTAVE-AUTHORITY-REGISTRY-AND-"
    "INDEPENDENT-IC10-QUORUM-GATE"
)
SOURCE_SCHEMA = "athena.w32-next-octave-authority-source/v1"
REVISION_SCHEMA = "athena.w32-next-octave-authority-revision/v1"
CLOSURE_SCHEMA = "athena.w32-next-octave-authority-quorum-closure/v1"
CANONICAL_GOVERNANCE_REPOSITORY = "demeet2k/Athena"
CANONICAL_RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
CANONICAL_CONTROL_REF = (
    "refs/heads/agent/w32-next-octave-authority-registry"
)
AUTHORITY_REF_PREFIX = "refs/heads/authority/w32/"
AUTHORITY_PATH_PREFIX = ".athena/authorities/w32/"
REGISTRY_PATH = ".athena/registry/w32-next-octave-authorities.jsonl"
QUORUM_LEDGER_PATH = ".athena/ledger/w32-independent-ic10-quorum.jsonl"
NEXT_OCTAVE_NAMESPACE = "KC144.XNAV.OCTAVE.2"
RUNTIME_PREDECESSOR_HEAD = "8a02320333a7f72e28fad1e857dfa3c8be124d33"
RUNTIME_PREDECESSOR_TREE = "75c8a49004dc2bc8ea465241ac20067fa9b20487"
RUNTIME_PREDECESSOR_PARENT = "32e350bf8ac6b0d96635e8fe4cdc0c10b65cfb7f"
CONTROL_PREDECESSOR_HEAD = "c2af24c378a0d4c65c7de258692c190e8bd15dbe"
CONTROL_PREDECESSOR_TREE = "13232b9591f8a7ea02c5e3e3767d430c1c073bbb"
W27_W31_RUNTIME_RECEIPT = (
    "w27-w31-five-wave-protocol:sha256:"
    "4e6e5fd1ff809bbe71d35d5619aa2036c50c22e8568c0a97650c7e696c2782dc"
)
W27_W31_CONTROL_RECEIPT = (
    "w27-w31-five-wave-control-admission:sha256:"
    "367f806e1182617456ab3c599b6d980c078de5714f1e3f12a7d2e7bd6758ccbb"
)
W32_CONTRACT = (
    "sha256:5b0c7aa4faecc86fe7633814025de15f5760476d4cdb2c7247526367ee4a0dcb"
)
MAXIMUM_RECORD_LAG_SECONDS = 900
ALLOWED_DECISIONS = {
    "APPROVE_REGISTRY_OPEN",
    "HOLD_REGISTRY_CLOSED",
}
ROLES = [
    "NEXT_OCTAVE_REGISTRY_CHARTER_ISSUER",
    "NEXT_OCTAVE_AUTHORITY_REGISTRAR_A",
    "NEXT_OCTAVE_AUTHORITY_REGISTRAR_B",
    "INDEPENDENT_IC10_REVIEWER_A",
    "INDEPENDENT_IC10_REVIEWER_B",
    "IC10_QUORUM_OBSERVER",
]
RECORD_KINDS = [
    "registry_charter",
    "authority_admission_a",
    "authority_admission_b",
    "ic10_quorum_vote_a",
    "ic10_quorum_vote_b",
    "ic10_quorum_observation",
]

TOP_LEVEL_FIELDS = {
    "schema",
    "phase",
    "title",
    "predecessor",
    "gate_contract",
    "authority_registry",
    "registry_charter_ledger",
    "authority_admission_ledger",
    "ic10_quorum_vote_ledger",
    "ic10_quorum_observation_ledger",
    "production_counts",
    "boundaries",
    "successor",
    "successor_source_status",
    "contract_digest",
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
    "phase",
    "repository",
    "ref",
    "environment",
    "policy_digest",
}
RECORD_FIELDS = {
    "schema",
    "phase",
    "record_index",
    "record_kind",
    "role",
    "source_digest",
    "revision_digest",
    "event_id",
    "previous_record_digest",
    "subject_digest",
    "next_octave_namespace",
    "registry_repository",
    "registry_ref",
    "registry_path",
    "quorum_ledger_path",
    "proposed_registry_root",
    "quorum_policy_digest",
    "decision",
    "outcome",
    "effect_claimed",
    "occurred_at",
    "nonce",
    "signature",
    "record_digest",
}


class NextOctaveAuthorityQuorumError(RuntimeError):
    """Frozen W32 contract or registry is invalid."""


def _fingerprint(public_key_base64: str) -> str:
    try:
        decoded = base64.b64decode(public_key_base64, validate=True)
    except ValueError as error:
        raise ValueError("public key must be canonical base64") from error
    if len(decoded) != 32 or base64.b64encode(decoded).decode() != public_key_base64:
        raise ValueError("public key must encode exactly 32 bytes")
    return "sha256:" + hashlib.sha256(decoded).hexdigest()


def _record_schema(kind: str) -> str:
    return f"athena.w32-{kind.replace('_', '-')}/v1"


def _negative() -> dict[str, bool]:
    return {
        "production_registry_open": False,
        "runtime_mutated_authority_registry": False,
        "runtime_mutated_quorum_ledger": False,
        "runtime_issued_ic10_vote": False,
        "workflow_dispatched": False,
        "endpoint_contacted": False,
        "image_published": False,
        "merged": False,
        "deployed": False,
        "promoted": False,
        "production_effect_claimed": False,
    }


def _merge(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(primary)
    result.update(deepcopy(secondary))
    return result


class FrozenNextOctaveAuthorityQuorum:
    """Verify the complete W32 opening gate without side effects."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        *,
        verification_time: datetime | None = None,
        allow_test_contract: bool = False,
    ):
        self.snapshot = deepcopy(snapshot)
        self.verification_time = verification_time or datetime.now(timezone.utc)
        self.allow_test_contract = allow_test_contract
        self._validate_snapshot()
        self.w31_gate = FrozenFiveWaveReviewClosure.load()
        self.expected_coordinates = list(zip(ROLES, RECORD_KINDS))
        self.quorum_policy_digest = _digest(
            {
                "schema": "athena.w32-independent-ic10-quorum-policy/v1",
                "contract_digest": self.snapshot["contract_digest"],
                "reviewer_quorum": "2_OF_2",
                "hold_dominates": True,
            }
        )

    @classmethod
    def load(cls) -> "FrozenNextOctaveAuthorityQuorum":
        try:
            return cls(_strict_loads(DATA_PATH.read_text(encoding="utf-8")))
        except (OSError, TypeError, ValueError) as error:
            raise NextOctaveAuthorityQuorumError(
                f"invalid frozen W32 snapshot: {error}"
            ) from error

    def _validate_snapshot(self) -> None:
        snapshot = _exact(self.snapshot, TOP_LEVEL_FIELDS, "snapshot")
        if (
            snapshot["schema"] != SCHEMA
            or snapshot["phase"] != PHASE
            or snapshot["title"] != TITLE
        ):
            raise ValueError("W32 schema, phase, or title drift")
        expected_contract = _digest(_addressed(snapshot, "contract_digest"))
        if snapshot["contract_digest"] != expected_contract:
            raise ValueError("W32 contract digest mismatch")
        if not self.allow_test_contract and expected_contract != W32_CONTRACT:
            raise ValueError("W32 frozen contract drift")
        predecessor = snapshot["predecessor"]
        required_predecessor = {
            "runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
            "runtime_pull_request": 13,
            "runtime_branch": "agent/w15-reconcile-capsule-deep-hardening",
            "runtime_head": RUNTIME_PREDECESSOR_HEAD,
            "runtime_tree": RUNTIME_PREDECESSOR_TREE,
            "runtime_sole_parent": RUNTIME_PREDECESSOR_PARENT,
            "w27_w31_contract_digest": W27_W31_CONTRACT,
            "w27_w31_runtime_receipt_id": W27_W31_RUNTIME_RECEIPT,
            "control_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "control_pull_request": 28,
            "control_branch": "agent/w23-w25-reconcile-combined-hardening",
            "control_head": CONTROL_PREDECESSOR_HEAD,
            "control_tree": CONTROL_PREDECESSOR_TREE,
            "w27_w31_control_receipt_id": W27_W31_CONTROL_RECEIPT,
        }
        if predecessor != required_predecessor:
            raise ValueError("W32 exact predecessor coordinates drift")
        for key in (
            "runtime_head",
            "runtime_tree",
            "runtime_sole_parent",
            "control_head",
            "control_tree",
        ):
            _commit(predecessor[key], f"predecessor.{key}")
        contract = snapshot["gate_contract"]
        exact_contract = {
            "authority_source_schema": SOURCE_SCHEMA,
            "authority_revision_schema": REVISION_SCHEMA,
            "record_schema_template": "athena.w32-{record_kind}/v1",
            "closure_schema": CLOSURE_SCHEMA,
            "canonical_governance_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "canonical_runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
            "canonical_control_ref": CANONICAL_CONTROL_REF,
            "canonical_authority_ref_prefix": AUTHORITY_REF_PREFIX,
            "canonical_authority_path_prefix": AUTHORITY_PATH_PREFIX,
            "canonical_registry_path": REGISTRY_PATH,
            "canonical_quorum_ledger_path": QUORUM_LEDGER_PATH,
            "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
            "roles": ROLES,
            "record_kinds": RECORD_KINDS,
            "allowed_decisions": [
                "APPROVE_REGISTRY_OPEN",
                "HOLD_REGISTRY_CLOSED",
            ],
            "reviewer_quorum": "2_OF_2",
            "hold_dominates": True,
            "new_role_count": 6,
            "total_cross_wave_roles": 51,
            "w25_w31_record_count": 44,
            "new_record_count": 6,
            "total_record_count": 50,
            "maximum_record_lag_seconds": MAXIMUM_RECORD_LAG_SECONDS,
            "complete_w27_w31_bundle_required": True,
            "strict_outer_json_required": True,
            "canonical_provenance_required": True,
            "identity_key_event_nonce_disjointness_required": True,
            "cross_wave_identity_and_key_disjointness_required": True,
            "total_chronology_required": True,
            "unanimous_record_decision_required": True,
            "independent_registrars_required": True,
            "independent_reviewers_required": True,
            "independent_quorum_observer_required": True,
            "runtime_is_verifier_only": True,
            "runtime_can_mutate_authority_registry": False,
            "runtime_can_mutate_quorum_ledger": False,
            "runtime_can_open_production_registry": False,
            "runtime_can_issue_ic10_vote": False,
            "runtime_can_merge_deploy_or_promote": False,
        }
        if contract != exact_contract:
            raise ValueError("W32 gate contract drift")
        if snapshot["authority_registry"] != {"sources": [], "revisions": []}:
            raise ValueError("production authority registry must be empty")
        for ledger in (
            "registry_charter_ledger",
            "authority_admission_ledger",
            "ic10_quorum_vote_ledger",
            "ic10_quorum_observation_ledger",
        ):
            if snapshot[ledger] != []:
                raise ValueError(f"production {ledger} must be empty")
        if set(snapshot["production_counts"].values()) != {0}:
            raise ValueError("W32 production counts must remain zero")
        for key, value in snapshot["boundaries"].items():
            if key in {"w31_runtime_and_control_pinned", "w32_protocol_compiled"}:
                if value is not True:
                    raise ValueError(f"required W32 boundary missing: {key}")
            elif value is not False:
                raise ValueError(f"protected W32 boundary changed: {key}")

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W32_NEXT_OCTAVE_AUTHORITY_AND_IC10_QUORUM_PROTOCOL_"
                    "COMPILED__AWAITING_COMPLETE_EXTERNAL_SIGNED_BUNDLE"
                ),
                "phase": PHASE,
                "runtime_predecessor_head": RUNTIME_PREDECESSOR_HEAD,
                "runtime_predecessor_tree": RUNTIME_PREDECESSOR_TREE,
                "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
                "control_predecessor_tree": CONTROL_PREDECESSOR_TREE,
                "contract_digest": self.snapshot["contract_digest"],
                "new_role_count": 6,
                "total_cross_wave_roles": 51,
                "new_record_count": 6,
                "total_record_count": 50,
                "reviewer_quorum": "2_OF_2",
                "authority_source_count": 0,
                "authority_revision_count": 0,
                "record_count": 0,
                "successor": self.snapshot["successor"],
            },
            _negative(),
        )

    def _source(self, value: Any) -> dict[str, Any]:
        source = _exact(value, SOURCE_FIELDS, "source")
        if source["schema"] != SOURCE_SCHEMA:
            raise ValueError("W32 authority source schema drift")
        source["source_id"] = _identifier(source["source_id"], "source.source_id")
        source["authority_id"] = _identifier(
            source["authority_id"], "source.authority_id"
        )
        source["role"] = _text(source["role"], "source.role", limit=96)
        if source["role"] not in ROLES:
            raise ValueError("source role outside W32 coordinate set")
        if source["governance_repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
            raise ValueError("authority source outside canonical governance")
        _sha(source["source_digest"], "source.source_digest")
        if source["source_digest"] != _digest(
            _addressed(source, "source_digest")
        ):
            raise ValueError("W32 authority source digest mismatch")
        return source

    def _revision(
        self, value: Any, source_by_digest: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        revision = _exact(value, REVISION_FIELDS, "revision")
        if revision["schema"] != REVISION_SCHEMA:
            raise ValueError("W32 authority revision schema drift")
        source_digest = _sha(revision["source_digest"], "revision.source_digest")
        if source_digest not in source_by_digest:
            raise ValueError("revision source is not registered")
        source = source_by_digest[source_digest]
        if revision["role"] != source["role"]:
            raise ValueError("revision role does not match source")
        revision["revision_id"] = _identifier(
            revision["revision_id"], "revision.revision_id"
        )
        revision["key_id"] = _identifier(revision["key_id"], "revision.key_id")
        if revision["repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
            raise ValueError("revision outside canonical governance")
        if not revision["ref"].startswith(AUTHORITY_REF_PREFIX):
            raise ValueError("revision outside canonical W32 authority ref")
        if not revision["path"].startswith(AUTHORITY_PATH_PREFIX):
            raise ValueError("revision outside canonical W32 authority path")
        _commit(revision["commit"], "revision.commit")
        _commit(revision["tree"], "revision.tree")
        _sha(revision["blob_digest"], "revision.blob_digest")
        _sha(revision["content_digest"], "revision.content_digest")
        if revision["parent_revision_digest"] is not None:
            _sha(
                revision["parent_revision_digest"],
                "revision.parent_revision_digest",
            )
        if revision["fingerprint"] != _fingerprint(
            revision["public_key_base64"]
        ):
            raise ValueError("W32 authority key fingerprint mismatch")
        role_index = ROLES.index(revision["role"])
        scope = _exact(revision["scope"], SCOPE_FIELDS, "revision.scope")
        if scope != {
            "operation": RECORD_KINDS[role_index],
            "phase": PHASE,
            "repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "ref": CANONICAL_CONTROL_REF,
            "environment": "kc144-next-octave-control",
            "policy_digest": self.quorum_policy_digest,
        }:
            raise ValueError("W32 revision scope drift")
        provenance = {
            "schema": "athena.w32-authority-blob-provenance/v1",
            "repository": revision["repository"],
            "ref": revision["ref"],
            "commit": revision["commit"],
            "tree": revision["tree"],
            "path": revision["path"],
            "content_digest": revision["content_digest"],
        }
        if revision["blob_digest"] != _digest(provenance):
            raise ValueError("W32 authority blob provenance mismatch")
        if revision["revision_digest"] != _digest(
            _addressed(revision, "revision_digest")
        ):
            raise ValueError("W32 authority revision digest mismatch")
        return revision

    @staticmethod
    def _cross_wave_axes(bundle: dict[str, Any]) -> list[set[Any]]:
        sources = bundle["sources"]
        revisions = bundle["revisions"]
        return [
            {item["source_id"] for item in sources},
            {item["authority_id"] for item in sources},
            {item["revision_id"] for item in revisions},
            {item["key_id"] for item in revisions},
            {item["public_key_base64"] for item in revisions},
            {item["fingerprint"] for item in revisions},
        ]

    def verify_bundle(self, bundle_json: str) -> dict[str, Any]:
        try:
            bundle = _strict_loads(bundle_json)
            _exact(
                bundle,
                {"w27_w31_bundle", "sources", "revisions", "records"},
                "bundle",
            )
            w31_bundle = bundle["w27_w31_bundle"]
            w31_result = self.w31_gate.verify_bundle(
                json.dumps(
                    w31_bundle,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            if w31_result.get("external_signed_bundle_verified") is not True:
                raise ValueError("complete W27-W31 signed closure is required")
            w31_closure_digest = w31_result["closure"]["closure_digest"]
            sources_raw = bundle["sources"]
            revisions_raw = bundle["revisions"]
            records = bundle["records"]
            if (
                not isinstance(sources_raw, list)
                or not isinstance(revisions_raw, list)
                or not isinstance(records, list)
                or len(sources_raw) != 6
                or len(revisions_raw) != 6
                or len(records) != 6
            ):
                raise ValueError(
                    "W32 bundle requires exactly 6 sources, 6 revisions, "
                    "and 6 ordered records"
                )
            sources = [self._source(item) for item in sources_raw]
            source_by_digest = {
                item["source_digest"]: item for item in sources
            }
            if len(source_by_digest) != 6:
                raise ValueError("W32 source digests must be disjoint")
            revisions = [
                self._revision(item, source_by_digest)
                for item in revisions_raw
            ]
            revision_by_digest = {
                item["revision_digest"]: item for item in revisions
            }
            if len(revision_by_digest) != 6:
                raise ValueError("W32 revision digests must be disjoint")
            if {item["role"] for item in sources} != set(ROLES):
                raise ValueError("W32 sources must cover every exact role")
            if {item["role"] for item in revisions} != set(ROLES):
                raise ValueError("W32 revisions must cover every exact role")
            w32_axes = self._cross_wave_axes(
                {"sources": sources, "revisions": revisions}
            )
            if any(len(axis) != 6 for axis in w32_axes):
                raise ValueError("W32 identity and key axes must be disjoint")
            w31_axes = self._cross_wave_axes(w31_bundle)
            for older, current in zip(w31_axes, w32_axes):
                if older & current:
                    raise ValueError(
                        "W32 identity or key axis overlaps W27-W31"
                    )
            source_by_role = {item["role"]: item for item in sources}
            revision_by_role = {item["role"]: item for item in revisions}
            expected_root = _digest(
                {
                    "schema": "athena.w32-proposed-registry-root/v1",
                    "w31_closure_digest": w31_closure_digest,
                    "contract_digest": self.snapshot["contract_digest"],
                    "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
                }
            )
            previous_digest = w31_closure_digest
            prior_time = _timestamp(
                w31_bundle["records"][-1]["occurred_at"],
                "w27_w31_bundle.records[-1].occurred_at",
            )
            decision: str | None = None
            event_ids: set[str] = set()
            nonces: set[str] = set()
            record_digests: set[str] = set()
            for index, ((role, kind), record) in enumerate(
                zip(self.expected_coordinates, records)
            ):
                record = _exact(record, RECORD_FIELDS, f"records[{index}]")
                source = source_by_role[role]
                revision = revision_by_role[role]
                if (
                    record["schema"] != _record_schema(kind)
                    or record["phase"] != PHASE
                    or record["record_index"] != index
                    or record["record_kind"] != kind
                    or record["role"] != role
                    or record["source_digest"] != source["source_digest"]
                    or record["revision_digest"] != revision["revision_digest"]
                ):
                    raise ValueError(f"W32 record {index} coordinate drift")
                if (
                    record["previous_record_digest"] != previous_digest
                    or record["subject_digest"] != w31_closure_digest
                ):
                    raise ValueError(f"W32 record {index} chain or subject drift")
                if (
                    record["next_octave_namespace"] != NEXT_OCTAVE_NAMESPACE
                    or record["registry_repository"]
                    != CANONICAL_GOVERNANCE_REPOSITORY
                    or record["registry_ref"] != CANONICAL_CONTROL_REF
                    or record["registry_path"] != REGISTRY_PATH
                    or record["quorum_ledger_path"] != QUORUM_LEDGER_PATH
                    or record["proposed_registry_root"] != expected_root
                    or record["quorum_policy_digest"]
                    != self.quorum_policy_digest
                ):
                    raise ValueError(f"W32 record {index} registry binding drift")
                if record["decision"] not in ALLOWED_DECISIONS:
                    raise ValueError("W32 decision outside typed decision set")
                if decision is None:
                    decision = record["decision"]
                elif decision != record["decision"]:
                    raise ValueError("W32 decision changed across quorum chain")
                if record["outcome"] != kind.upper():
                    raise ValueError(f"W32 record {index} outcome drift")
                if record["effect_claimed"] is not False:
                    raise ValueError("W32 evidence cannot claim production effect")
                event_id = _identifier(
                    record["event_id"], f"records[{index}].event_id"
                )
                nonce = _identifier(record["nonce"], f"records[{index}].nonce")
                if event_id in event_ids or nonce in nonces:
                    raise ValueError("W32 event and nonce axes must be disjoint")
                event_ids.add(event_id)
                nonces.add(nonce)
                occurred_at = _timestamp(
                    record["occurred_at"], f"records[{index}].occurred_at"
                )
                lag = (occurred_at - prior_time).total_seconds()
                if lag <= 0 or lag > MAXIMUM_RECORD_LAG_SECONDS:
                    raise ValueError("W32 record chronology or lag invalid")
                prior_time = occurred_at
                _verify(
                    record,
                    revision,
                    "record_digest",
                    record["occurred_at"],
                )
                digest = _sha(
                    record["record_digest"], f"records[{index}].record_digest"
                )
                if digest in record_digests:
                    raise ValueError("W32 record digests must be disjoint")
                record_digests.add(digest)
                previous_digest = digest
            if len(event_ids | nonces) != 12:
                raise ValueError("W32 event IDs and nonces must be cross-disjoint")
            if set(event_ids | nonces) & set().union(*w31_axes, *w32_axes):
                raise ValueError("W32 occurrence axes overlap identity/key axes")
            approvals = 2 if decision == "APPROVE_REGISTRY_OPEN" else 0
            gate_state = (
                "ELIGIBLE_FOR_CONTROL_ADMISSION"
                if approvals == 2
                else "HOLD_REGISTRY_CLOSED"
            )
            closure = {
                "schema": CLOSURE_SCHEMA,
                "phase": PHASE,
                "contract_digest": self.snapshot["contract_digest"],
                "w31_closure_digest": w31_closure_digest,
                "proposed_registry_root": expected_root,
                "quorum_policy_digest": self.quorum_policy_digest,
                "decision": decision,
                "reviewer_approvals": approvals,
                "required_reviewer_approvals": 2,
                "gate_state": gate_state,
                "record_count": 6,
                "terminal_record_digest": previous_digest,
                "successor": self.snapshot["successor"],
                "production_registry_open": False,
                "production_effect_claimed": False,
                "closure_digest": "",
            }
            closure["closure_digest"] = _digest(
                _addressed(closure, "closure_digest")
            )
            return _merge(
                {
                    "status": (
                        "PASS_W32_COMPLETE_SIGNED_AUTHORITY_AND_IC10_"
                        "QUORUM_BUNDLE__VERIFIER_REMAINS_NON_EFFECTING"
                    ),
                    "external_w27_w31_bundle_verified": True,
                    "registry_charter_verified": True,
                    "registrar_a_admission_verified": True,
                    "registrar_b_admission_verified": True,
                    "ic10_reviewer_a_vote_verified": True,
                    "ic10_reviewer_b_vote_verified": True,
                    "ic10_quorum_observed": True,
                    "quorum_evidence_satisfied": approvals == 2,
                    "control_admission_eligible": approvals == 2,
                    "decision": decision,
                    "closure": closure,
                },
                _negative(),
            )
        except (KeyError, LookupError, TypeError, ValueError) as error:
            return _merge(
                {
                    "status": "HOLD_W32_AUTHORITY_AND_IC10_QUORUM_BUNDLE_REJECTED",
                    "error": str(error),
                    "external_w27_w31_bundle_verified": False,
                    "quorum_evidence_satisfied": False,
                    "control_admission_eligible": False,
                },
                _negative(),
            )

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W32_SEPARATION_LAW_EXPLAINED",
                "law": (
                    "W31 HANDOFF != W32 REGISTRY CHARTER; CHARTER != "
                    "AUTHORITY ADMISSION; TWO REGISTRARS != TWO IC10 "
                    "REVIEWERS; TWO REVIEWER VOTES != INDEPENDENT QUORUM "
                    "OBSERVATION; VERIFIED QUORUM EVIDENCE != PRODUCTION "
                    "REGISTRY MUTATION; CONTROL ELIGIBILITY != PROMOTION"
                ),
                "roles": ROLES,
                "record_kinds": RECORD_KINDS,
                "reviewer_quorum": "2_OF_2",
                "hold_dominates": True,
                "runtime_is_verifier_only": True,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_next_octave_authority_quorum(mcp: Any) -> None:
    """Register seven W32 tools and two frozen resources."""
    gate = FrozenNextOctaveAuthorityQuorum.load()

    @mcp.tool()
    def athena_w32_next_octave_quorum_status() -> str:
        """Return the frozen-empty W32 authority/quorum boundary."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w32_w31_custody() -> str:
        """Inspect exact W31 runtime/control custody."""
        return _render(
            _merge(
                {
                    "status": "PASS_W32_W31_CUSTODY_PINNED",
                    "predecessor": gate.snapshot["predecessor"],
                },
                _negative(),
            )
        )

    @mcp.tool()
    def inspect_athena_w32_registry_contract() -> str:
        """Inspect registry coordinates without opening the registry."""
        return _render(
            _merge(
                {
                    "status": "PASS_W32_REGISTRY_CONTRACT_PINNED",
                    "registry_repository": CANONICAL_GOVERNANCE_REPOSITORY,
                    "registry_ref": CANONICAL_CONTROL_REF,
                    "registry_path": REGISTRY_PATH,
                    "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
                    "production_registry_open": False,
                },
                _negative(),
            )
        )

    @mcp.tool()
    def inspect_athena_w32_ic10_quorum_contract() -> str:
        """Inspect the 2-of-2 reviewer and observer separation law."""
        return _render(
            _merge(
                {
                    "status": "PASS_W32_IC10_QUORUM_CONTRACT_PINNED",
                    "quorum_policy_digest": gate.quorum_policy_digest,
                    "reviewer_quorum": "2_OF_2",
                    "hold_dominates": True,
                    "roles": ROLES,
                },
                _negative(),
            )
        )

    @mcp.tool()
    def compile_athena_w32_bundle_template() -> str:
        """Compile the exact empty W32 bundle shape."""
        records = []
        for index, (role, kind) in enumerate(gate.expected_coordinates):
            records.append(
                {
                    "schema": _record_schema(kind),
                    "phase": PHASE,
                    "record_index": index,
                    "record_kind": kind,
                    "role": role,
                    "source_digest": None,
                    "revision_digest": None,
                    "event_id": None,
                    "previous_record_digest": None,
                    "subject_digest": None,
                    "next_octave_namespace": NEXT_OCTAVE_NAMESPACE,
                    "registry_repository": CANONICAL_GOVERNANCE_REPOSITORY,
                    "registry_ref": CANONICAL_CONTROL_REF,
                    "registry_path": REGISTRY_PATH,
                    "quorum_ledger_path": QUORUM_LEDGER_PATH,
                    "proposed_registry_root": None,
                    "quorum_policy_digest": gate.quorum_policy_digest,
                    "decision": None,
                    "outcome": kind.upper(),
                    "effect_claimed": False,
                    "occurred_at": None,
                    "nonce": None,
                    "signature": {"key_id": None, "value": None},
                    "record_digest": None,
                }
            )
        return _render(
            _merge(
                {
                    "status": "PASS_W32_BUNDLE_TEMPLATE_COMPILED",
                    "bundle": {
                        "w27_w31_bundle": None,
                        "sources": [],
                        "revisions": [],
                        "records": records,
                    },
                },
                _negative(),
            )
        )

    @mcp.tool()
    def verify_athena_w32_next_octave_quorum_bundle(bundle_json: str) -> str:
        """Verify one complete strict W31→W32 signed bundle."""
        return _render(gate.verify_bundle(bundle_json))

    @mcp.tool()
    def explain_athena_w32_separation_law() -> str:
        """Explain W32 authority, quorum, observation, and effect separation."""
        return _render(gate.explain())

    @mcp.resource("athena://w32-next-octave-authority-quorum")
    def w32_authority_quorum_resource() -> str:
        """Read the complete frozen W32 contract."""
        return _render(gate.snapshot)

    @mcp.resource("athena://w32-independent-ic10-quorum")
    def w32_ic10_quorum_resource() -> str:
        """Read the frozen W32 independent IC10 quorum contract."""
        return _render(
            {
                "schema": "athena.w32-independent-ic10-quorum-policy/v1",
                "quorum_policy_digest": gate.quorum_policy_digest,
                "reviewer_quorum": "2_OF_2",
                "hold_dominates": True,
                "roles": ROLES,
                "production_registry_open": False,
            }
        )
