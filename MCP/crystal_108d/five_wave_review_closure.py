"""KC144 XNAV W27-W31 dependency-closed five-wave verifier.

W27 is the exact W26 successor.  W28-W31 are explicit correction-forward
derivations that carry a typed IC10 decision through control admission,
disposition consumption, publication-or-denial readback, endpoint/retention
return, and terminal next-octave handoff.  The runtime only verifies evidence;
it cannot create authority, issue a decision, mutate a ledger, publish,
activate an endpoint, merge, deploy, or promote.
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
    / "w27_w31_five_wave_closure.json"
)
SCHEMA = "athena.xnav-w27-w31-five-wave-closure/v1"
BATCH = "KC144.XNAV.W27-W31"
SOURCE_SCHEMA = "athena.w27-w31-authority-source/v1"
REVISION_SCHEMA = "athena.w27-w31-authority-revision/v1"
CANONICAL_GOVERNANCE_REPOSITORY = "demeet2k/Athena"
CANONICAL_RUNTIME_REPOSITORY = "demeet2k/athena-mcp-server"
CANONICAL_CONTROL_REF = "refs/heads/agent/w27-w31-five-wave-closure"
AUTHORITY_REF_TEMPLATE = "refs/heads/authority/w{wave}/"
AUTHORITY_PATH_TEMPLATE = ".athena/authorities/w{wave}/"
RUNTIME_PREDECESSOR_HEAD = "32e350bf8ac6b0d96635e8fe4cdc0c10b65cfb7f"
RUNTIME_PREDECESSOR_TREE = "589450b79fd331aa4871389bc5e0f4519619139a"
CONTROL_PREDECESSOR_HEAD = "9e74586ba82a606835551638c5c9d77baf0e228e"
CONTROL_PREDECESSOR_TREE = "8ace2fd0db2470679cff96742a526dc4943cd775"
W26_CONTRACT = (
    "sha256:5128940d6a95f8d8a2def5cfe8f93d26a9db1bbbebd33387e47f9e4b0a8d6efc"
)
W26_RUNTIME_RECEIPT = (
    "w26-control-ledger-ic10-review:sha256:"
    "55c30bb8bdead838782254939b2dbb03cf76383403c434e5ff88799ca3a7b851"
)
W26_CONTROL_RECEIPT = (
    "w26-control-ledger-ic10-review-admission:sha256:"
    "ee3583e373def53438898be964ab898a8e747fc127d2b8c9ce8ae2a8e729be17"
)
W27_W31_CONTRACT = (
    "sha256:22c14aa524e66888d360f090785bca79b1c626aa9e98b50cea21c9488f0b397d"
)
MAXIMUM_RECORD_LAG_SECONDS = 900
ALLOWED_DECISIONS = {"APPROVED", "REJECTED_ROLLED_BACK", "HOLD"}

TOP_LEVEL_FIELDS = {
    "schema",
    "batch",
    "derivation",
    "predecessor",
    "waves",
    "verification_contract",
    "authority_registry",
    "record_ledger",
    "production_counts",
    "boundaries",
    "successor",
    "contract_digest",
}
SOURCE_FIELDS = {
    "schema",
    "source_id",
    "authority_id",
    "role",
    "wave",
    "governance_repository",
    "source_digest",
}
REVISION_FIELDS = {
    "schema",
    "source_digest",
    "revision_id",
    "role",
    "wave",
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
    "batch_contract_digest",
}
RECORD_FIELDS = {
    "schema",
    "phase",
    "wave",
    "record_index",
    "record_kind",
    "role",
    "source_digest",
    "revision_digest",
    "event_id",
    "previous_record_digest",
    "subject_digest",
    "decision",
    "outcome",
    "effect_claimed",
    "occurred_at",
    "nonce",
    "signature",
    "record_digest",
}
SIGNATURE_FIELDS = {"key_id", "value"}


class FiveWaveReviewClosureError(RuntimeError):
    """Frozen W27-W31 batch contract or registry is invalid."""


def _fingerprint(public_key_base64: str) -> str:
    try:
        decoded = base64.b64decode(public_key_base64, validate=True)
    except ValueError as error:
        raise ValueError("public key must be canonical base64") from error
    if len(decoded) != 32 or base64.b64encode(decoded).decode() != public_key_base64:
        raise ValueError("public key must encode exactly 32 bytes")
    return "sha256:" + hashlib.sha256(decoded).hexdigest()


def _record_schema(wave: int, kind: str) -> str:
    return f"athena.w{wave}-{kind.replace('_', '-')}/v1"


def _negative() -> dict[str, bool]:
    return {
        "runtime_mutated_authority_registry": False,
        "runtime_mutated_control_ledger": False,
        "runtime_issued_decision_or_disposition": False,
        "runtime_published_artifact": False,
        "runtime_activated_endpoint": False,
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


class FrozenFiveWaveReviewClosure:
    """Verify one complete W27-W31 evidence bundle without side effects."""

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
        self.wave_by_number = {
            wave["wave"]: deepcopy(wave) for wave in self.snapshot["waves"]
        }
        self.expected_coordinates = [
            (wave["wave"], role, kind)
            for wave in self.snapshot["waves"]
            for role, kind in zip(wave["roles"], wave["record_kinds"])
        ]

    @classmethod
    def load(cls) -> "FrozenFiveWaveReviewClosure":
        try:
            snapshot = _strict_loads(DATA_PATH.read_text(encoding="utf-8"))
            return cls(snapshot)
        except (OSError, TypeError, ValueError) as error:
            raise FiveWaveReviewClosureError(
                f"invalid frozen W27-W31 snapshot: {error}"
            ) from error

    def _validate_snapshot(self) -> None:
        snapshot = _exact(self.snapshot, TOP_LEVEL_FIELDS, "snapshot")
        if snapshot["schema"] != SCHEMA or snapshot["batch"] != BATCH:
            raise ValueError("W27-W31 schema or batch drift")
        expected_contract = _digest(_addressed(snapshot, "contract_digest"))
        if snapshot["contract_digest"] != expected_contract:
            raise ValueError("W27-W31 contract digest mismatch")
        if not self.allow_test_contract and expected_contract != W27_W31_CONTRACT:
            raise ValueError("W27-W31 frozen contract drift")

        predecessor = snapshot["predecessor"]
        required_predecessor = {
            "runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
            "runtime_pull_request": 13,
            "runtime_branch": "agent/w15-reconcile-capsule-deep-hardening",
            "runtime_head": RUNTIME_PREDECESSOR_HEAD,
            "runtime_tree": RUNTIME_PREDECESSOR_TREE,
            "w26_contract_digest": W26_CONTRACT,
            "w26_runtime_receipt_id": W26_RUNTIME_RECEIPT,
            "control_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "control_pull_request": 28,
            "control_branch": "agent/w23-w25-reconcile-combined-hardening",
            "control_head": CONTROL_PREDECESSOR_HEAD,
            "control_tree": CONTROL_PREDECESSOR_TREE,
            "w26_control_receipt_id": W26_CONTROL_RECEIPT,
        }
        if predecessor != required_predecessor:
            raise ValueError("W27-W31 exact predecessor coordinates drift")
        _commit(predecessor["runtime_head"], "predecessor.runtime_head")
        _commit(predecessor["runtime_tree"], "predecessor.runtime_tree")
        _commit(predecessor["control_head"], "predecessor.control_head")
        _commit(predecessor["control_tree"], "predecessor.control_tree")

        waves = snapshot["waves"]
        if not isinstance(waves, list) or len(waves) != 5:
            raise ValueError("exactly five waves are required")
        expected_numbers = list(range(27, 32))
        if [wave.get("wave") for wave in waves] != expected_numbers:
            raise ValueError("waves must be exactly W27 through W31")
        roles: list[str] = []
        kinds: list[str] = []
        for offset, wave in enumerate(waves):
            number = 27 + offset
            if (
                wave.get("phase") != f"KC144.XNAV.W{number}"
                or wave.get("predecessor") != f"KC144.XNAV.W{number - 1}"
                or not isinstance(wave.get("roles"), list)
                or not isinstance(wave.get("record_kinds"), list)
                or len(wave["roles"]) != 4
                or len(wave["record_kinds"]) != 4
            ):
                raise ValueError(f"W{number} topology drift")
            if number < 31 and not wave["successor"].startswith(
                f"KC144.XNAV.W{number + 1}::"
            ):
                raise ValueError(f"W{number} successor drift")
            roles.extend(wave["roles"])
            kinds.extend(wave["record_kinds"])
        if len(set(roles)) != 20 or len(set(kinds)) != 20:
            raise ValueError("W27-W31 roles and record kinds must be disjoint")
        if waves[-1]["successor"] != snapshot["successor"]:
            raise ValueError("W31 successor must equal batch successor")

        contract = snapshot["verification_contract"]
        exact_contract = {
            "authority_source_schema": SOURCE_SCHEMA,
            "authority_revision_schema": REVISION_SCHEMA,
            "record_schema_template": "athena.w{wave}-{record_kind}/v1",
            "canonical_governance_repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "canonical_runtime_repository": CANONICAL_RUNTIME_REPOSITORY,
            "canonical_control_ref": CANONICAL_CONTROL_REF,
            "canonical_authority_ref_template": AUTHORITY_REF_TEMPLATE,
            "canonical_authority_path_template": AUTHORITY_PATH_TEMPLATE,
            "maximum_record_lag_seconds": MAXIMUM_RECORD_LAG_SECONDS,
            "allowed_decisions": [
                "APPROVED",
                "REJECTED_ROLLED_BACK",
                "HOLD",
            ],
            "records_per_wave": 4,
            "new_role_count": 20,
            "total_cross_wave_roles": 45,
            "w25_w26_record_count": 24,
            "new_record_count": 20,
            "total_record_count": 44,
            "strict_outer_json_required": True,
            "canonical_provenance_required": True,
            "exact_predecessor_coordinates_required": True,
            "identity_key_axis_and_nonce_disjointness_required": True,
            "total_w27_w31_chronology_required": True,
            "decision_consistency_required": True,
            "atomic_five_wave_closure_required": True,
            "runtime_is_verifier_only": True,
            "runtime_can_mutate_authority_registry": False,
            "runtime_can_mutate_control_ledger": False,
            "runtime_can_issue_decision_or_disposition": False,
            "runtime_can_publish_or_activate_endpoint": False,
            "runtime_can_merge_deploy_or_promote": False,
        }
        if contract != exact_contract:
            raise ValueError("W27-W31 verification contract drift")
        if snapshot["authority_registry"] != {"sources": [], "revisions": []}:
            raise ValueError("production authority registry must be empty")
        if snapshot["record_ledger"] != []:
            raise ValueError("production record ledger must be empty")
        if set(snapshot["production_counts"].values()) != {0}:
            raise ValueError("production counts must remain zero")
        boundaries = snapshot["boundaries"]
        if boundaries["w26_runtime_and_control_pinned"] is not True:
            raise ValueError("W26 predecessor must remain pinned")
        if boundaries["five_wave_protocol_compiled"] is not True:
            raise ValueError("five-wave protocol must be compiled")
        for key, value in boundaries.items():
            if key not in {
                "w26_runtime_and_control_pinned",
                "five_wave_protocol_compiled",
            } and value is not False:
                raise ValueError(f"protected W27-W31 boundary changed: {key}")

    def status(self) -> dict[str, Any]:
        return _merge(
            {
                "status": (
                    "W27_W31_FIVE_WAVE_PROTOCOL_COMPILED__"
                    "AWAITING_COMPLETE_EXTERNAL_SIGNED_BUNDLE"
                ),
                "batch": BATCH,
                "runtime_predecessor_head": RUNTIME_PREDECESSOR_HEAD,
                "runtime_predecessor_tree": RUNTIME_PREDECESSOR_TREE,
                "control_predecessor_head": CONTROL_PREDECESSOR_HEAD,
                "control_predecessor_tree": CONTROL_PREDECESSOR_TREE,
                "contract_digest": self.snapshot["contract_digest"],
                "wave_count": 5,
                "new_role_count": 20,
                "new_record_count": 20,
                "authority_source_count": 0,
                "authority_revision_count": 0,
                "record_count": 0,
                "successor": self.snapshot["successor"],
            },
            _negative(),
        )

    def inspect_wave(self, wave: int) -> dict[str, Any]:
        if type(wave) is not int or wave not in self.wave_by_number:
            return _merge(
                {
                    "status": "HOLD_W27_W31_WAVE_OUT_OF_RANGE",
                    "error": "wave must be an integer from 27 through 31",
                },
                _negative(),
            )
        return _merge(
            {
                "status": f"PASS_W{wave}_PROTOCOL_PINNED",
                "wave_contract": deepcopy(self.wave_by_number[wave]),
                "record_schemas": [
                    _record_schema(wave, kind)
                    for kind in self.wave_by_number[wave]["record_kinds"]
                ],
            },
            _negative(),
        )

    def _source(self, value: Any) -> dict[str, Any]:
        source = _exact(value, SOURCE_FIELDS, "source")
        if source["schema"] != SOURCE_SCHEMA:
            raise ValueError("authority source schema drift")
        source["source_id"] = _identifier(source["source_id"], "source.source_id")
        source["authority_id"] = _identifier(
            source["authority_id"], "source.authority_id"
        )
        source["role"] = _text(source["role"], "source.role", limit=96)
        if type(source["wave"]) is not int or source["wave"] not in range(27, 32):
            raise ValueError("source.wave must be W27 through W31")
        if source["governance_repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
            raise ValueError("authority source outside canonical governance")
        _sha(source["source_digest"], "source.source_digest")
        if source["source_digest"] != _digest(
            _addressed(source, "source_digest")
        ):
            raise ValueError("authority source digest mismatch")
        return source

    def _revision(
        self, value: Any, source_by_digest: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        revision = _exact(value, REVISION_FIELDS, "revision")
        if revision["schema"] != REVISION_SCHEMA:
            raise ValueError("authority revision schema drift")
        source_digest = _sha(revision["source_digest"], "revision.source_digest")
        if source_digest not in source_by_digest:
            raise ValueError("revision source is not registered")
        source = source_by_digest[source_digest]
        if (
            revision["role"] != source["role"]
            or revision["wave"] != source["wave"]
        ):
            raise ValueError("revision role/wave does not match source")
        revision["revision_id"] = _identifier(
            revision["revision_id"], "revision.revision_id"
        )
        revision["key_id"] = _identifier(revision["key_id"], "revision.key_id")
        if revision["repository"] != CANONICAL_GOVERNANCE_REPOSITORY:
            raise ValueError("revision outside canonical governance repository")
        expected_ref = AUTHORITY_REF_TEMPLATE.format(wave=revision["wave"])
        expected_path = AUTHORITY_PATH_TEMPLATE.format(wave=revision["wave"])
        if not revision["ref"].startswith(expected_ref):
            raise ValueError("revision outside canonical authority ref")
        if not revision["path"].startswith(expected_path):
            raise ValueError("revision outside canonical authority path")
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
            raise ValueError("authority key fingerprint mismatch")
        scope = _exact(revision["scope"], SCOPE_FIELDS, "revision.scope")
        wave = revision["wave"]
        expected_kind = self.wave_by_number[wave]["record_kinds"][
            self.wave_by_number[wave]["roles"].index(revision["role"])
        ]
        if scope != {
            "operation": expected_kind,
            "phase": f"KC144.XNAV.W{wave}",
            "repository": CANONICAL_GOVERNANCE_REPOSITORY,
            "ref": CANONICAL_CONTROL_REF,
            "environment": "kc144-control",
            "batch_contract_digest": self.snapshot["contract_digest"],
        }:
            raise ValueError("revision scope drift")
        provenance = {
            "schema": "athena.w27-w31-authority-blob-provenance/v1",
            "repository": revision["repository"],
            "ref": revision["ref"],
            "commit": revision["commit"],
            "tree": revision["tree"],
            "path": revision["path"],
            "content_digest": revision["content_digest"],
        }
        if revision["blob_digest"] != _digest(provenance):
            raise ValueError("authority blob provenance mismatch")
        if revision["revision_digest"] != _digest(
            _addressed(revision, "revision_digest")
        ):
            raise ValueError("authority revision digest mismatch")
        return revision

    def verify_bundle(self, bundle_json: str) -> dict[str, Any]:
        try:
            bundle = _strict_loads(bundle_json)
            _exact(bundle, {"sources", "revisions", "records"}, "bundle")
            sources_raw = bundle["sources"]
            revisions_raw = bundle["revisions"]
            records = bundle["records"]
            if (
                not isinstance(sources_raw, list)
                or not isinstance(revisions_raw, list)
                or not isinstance(records, list)
                or len(sources_raw) != 20
                or len(revisions_raw) != 20
                or len(records) != 20
            ):
                raise ValueError(
                    "bundle requires exactly 20 sources, 20 revisions, "
                    "and 20 ordered records"
                )

            sources = [self._source(item) for item in sources_raw]
            source_by_digest = {
                item["source_digest"]: item for item in sources
            }
            if len(source_by_digest) != 20:
                raise ValueError("authority source digests must be disjoint")
            revisions = [
                self._revision(item, source_by_digest)
                for item in revisions_raw
            ]
            revision_by_digest = {
                item["revision_digest"]: item for item in revisions
            }
            if len(revision_by_digest) != 20:
                raise ValueError("authority revision digests must be disjoint")

            expected_roles = [item[1] for item in self.expected_coordinates]
            if {item["role"] for item in sources} != set(expected_roles):
                raise ValueError("bundle must contain every exact wave role")
            if {item["role"] for item in revisions} != set(expected_roles):
                raise ValueError("bundle revisions must cover every exact role")
            identity_axes = [
                {item["source_id"] for item in sources},
                {item["authority_id"] for item in sources},
                {item["revision_id"] for item in revisions},
                {item["key_id"] for item in revisions},
                {item["public_key_base64"] for item in revisions},
                {item["fingerprint"] for item in revisions},
            ]
            if any(len(axis) != 20 for axis in identity_axes):
                raise ValueError("identity and key axes must be disjoint")

            source_by_role = {item["role"]: item for item in sources}
            revision_by_role = {item["role"]: item for item in revisions}
            previous_digest = W26_RUNTIME_RECEIPT
            prior_time: datetime | None = None
            decision: str | None = None
            event_ids: set[str] = set()
            nonces: set[str] = set()
            record_digests: set[str] = set()
            wave_last_digests: dict[int, str] = {}

            for index, (record, coordinate) in enumerate(
                zip(records, self.expected_coordinates)
            ):
                wave, role, kind = coordinate
                record = _exact(record, RECORD_FIELDS, f"records[{index}]")
                source = source_by_role[role]
                revision = revision_by_role[role]
                if (
                    record["schema"] != _record_schema(wave, kind)
                    or record["phase"] != f"KC144.XNAV.W{wave}"
                    or record["wave"] != wave
                    or record["record_index"] != index
                    or record["record_kind"] != kind
                    or record["role"] != role
                    or record["source_digest"] != source["source_digest"]
                    or record["revision_digest"] != revision["revision_digest"]
                ):
                    raise ValueError(f"record {index} coordinate drift")
                event_id = _identifier(record["event_id"], f"records[{index}].event_id")
                nonce = _identifier(record["nonce"], f"records[{index}].nonce")
                if event_id in event_ids or nonce in nonces:
                    raise ValueError("event and nonce axes must be disjoint")
                event_ids.add(event_id)
                nonces.add(nonce)
                if (
                    record["previous_record_digest"] != previous_digest
                    or record["subject_digest"] != previous_digest
                ):
                    raise ValueError(f"record {index} chain link mismatch")
                if record["decision"] not in ALLOWED_DECISIONS:
                    raise ValueError("decision outside typed decision set")
                if decision is None:
                    decision = record["decision"]
                elif decision != record["decision"]:
                    raise ValueError("decision changed across five-wave batch")
                expected_outcome = kind.upper()
                if record["outcome"] != expected_outcome:
                    raise ValueError(f"record {index} outcome drift")
                if record["effect_claimed"] is not False:
                    raise ValueError("evidence record cannot claim production effect")
                occurred_at = _timestamp(
                    record["occurred_at"], f"records[{index}].occurred_at"
                )
                if prior_time is not None:
                    lag = (occurred_at - prior_time).total_seconds()
                    if lag <= 0 or lag > MAXIMUM_RECORD_LAG_SECONDS:
                        raise ValueError("record chronology or lag invalid")
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
                    raise ValueError("record digests must be disjoint")
                record_digests.add(digest)
                previous_digest = digest
                if index % 4 == 3:
                    wave_last_digests[wave] = digest

            if len(event_ids | nonces) != 40:
                raise ValueError("event IDs and nonces must be cross-axis disjoint")
            if set(event_ids | nonces) & set().union(*identity_axes):
                raise ValueError("occurrence axes overlap identity or key axes")

            wave_certificates = []
            for wave in range(27, 32):
                certificate = {
                    "schema": f"athena.w{wave}-protocol-evidence-certificate/v1",
                    "phase": f"KC144.XNAV.W{wave}",
                    "decision": decision,
                    "last_record_digest": wave_last_digests[wave],
                    "record_count": 4,
                    "production_effect_claimed": False,
                    "certificate_digest": "",
                }
                certificate["certificate_digest"] = _digest(
                    _addressed(certificate, "certificate_digest")
                )
                wave_certificates.append(certificate)
            closure = {
                "schema": "athena.w27-w31-five-wave-evidence-closure/v1",
                "batch": BATCH,
                "contract_digest": self.snapshot["contract_digest"],
                "decision": decision,
                "source_count": 20,
                "revision_count": 20,
                "record_count": 20,
                "wave_certificates": wave_certificates,
                "terminal_record_digest": previous_digest,
                "successor": self.snapshot["successor"],
                "production_effect_claimed": False,
                "closure_digest": "",
            }
            closure["closure_digest"] = _digest(
                _addressed(closure, "closure_digest")
            )
            return _merge(
                {
                    "status": (
                        "PASS_W27_W31_COMPLETE_SIGNED_EVIDENCE_BUNDLE__"
                        "VERIFIER_REMAINS_NON_EFFECTING"
                    ),
                    "external_signed_bundle_verified": True,
                    "decision": decision,
                    "wave_certificates": wave_certificates,
                    "closure": closure,
                },
                _negative(),
            )
        except (
            KeyError,
            LookupError,
            TypeError,
            ValueError,
        ) as error:
            return _merge(
                {
                    "status": "HOLD_W27_W31_FIVE_WAVE_BUNDLE_REJECTED",
                    "error": str(error),
                    "external_signed_bundle_verified": False,
                },
                _negative(),
            )

    def explain(self) -> dict[str, Any]:
        return _merge(
            {
                "status": "PASS_W27_W31_SEPARATION_LAW_EXPLAINED",
                "law": (
                    "IC10 DECISION RETURN != CONTROL ADMISSION; CONTROL "
                    "ADMISSION != PROMOTION DISPOSITION; DISPOSITION != "
                    "CONSUMPTION; CONSUMPTION != PUBLICATION; PUBLICATION != "
                    "ENDPOINT HEALTH; HEALTH != RETENTION; SETTLEMENT != "
                    "NEXT-OCTAVE AUTHORITY; VERIFICATION != PRODUCTION EFFECT"
                ),
                "waves": deepcopy(self.snapshot["waves"]),
                "atomic_five_wave_closure_required": True,
                "runtime_is_verifier_only": True,
            },
            _negative(),
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_five_wave_review_closure(mcp: Any) -> None:
    """Register seven W27-W31 tools and six frozen resources."""
    gate = FrozenFiveWaveReviewClosure.load()

    @mcp.tool()
    def athena_w27_w31_five_wave_status() -> str:
        """Return the frozen-empty W27-W31 five-wave boundary."""
        return _render(gate.status())

    @mcp.tool()
    def list_athena_w27_w31_waves() -> str:
        """List all five dependency-linked wave contracts."""
        return _render(
            _merge(
                {
                    "status": "PASS_W27_W31_FIVE_WAVES_LISTED",
                    "waves": gate.snapshot["waves"],
                },
                _negative(),
            )
        )

    @mcp.tool()
    def inspect_athena_w27_w31_wave(wave: int) -> str:
        """Inspect one exact W27-W31 wave by integer number."""
        return _render(gate.inspect_wave(wave))

    @mcp.tool()
    def inspect_athena_w27_w31_predecessor_custody() -> str:
        """Inspect exact W26 runtime/control custody without granting authority."""
        return _render(
            _merge(
                {
                    "status": "PASS_W27_W31_W26_CUSTODY_PINNED",
                    "predecessor": gate.snapshot["predecessor"],
                },
                _negative(),
            )
        )

    @mcp.tool()
    def compile_athena_w27_w31_bundle_template() -> str:
        """Compile the exact empty 20-coordinate bundle shape."""
        templates = []
        for index, (wave, role, kind) in enumerate(gate.expected_coordinates):
            templates.append(
                {
                    "schema": _record_schema(wave, kind),
                    "phase": f"KC144.XNAV.W{wave}",
                    "wave": wave,
                    "record_index": index,
                    "record_kind": kind,
                    "role": role,
                    "source_digest": None,
                    "revision_digest": None,
                    "event_id": None,
                    "previous_record_digest": (
                        W26_RUNTIME_RECEIPT if index == 0 else None
                    ),
                    "subject_digest": (
                        W26_RUNTIME_RECEIPT if index == 0 else None
                    ),
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
                    "status": "PASS_W27_W31_BUNDLE_TEMPLATE_COMPILED",
                    "bundle": {
                        "sources": [],
                        "revisions": [],
                        "records": templates,
                    },
                },
                _negative(),
            )
        )

    @mcp.tool()
    def verify_athena_w27_w31_five_wave_bundle(bundle_json: str) -> str:
        """Verify one strict, complete W27-W31 signed bundle."""
        return _render(gate.verify_bundle(bundle_json))

    @mcp.tool()
    def explain_athena_w27_w31_separation_law() -> str:
        """Explain the five-wave non-equivalence and authority law."""
        return _render(gate.explain())

    @mcp.resource("athena://w27-w31-five-wave-closure")
    def five_wave_closure_resource() -> str:
        """Read the complete frozen W27-W31 contract."""
        return _render(gate.snapshot)

    def _wave_resource(number: int):
        def resource() -> str:
            return _render(gate.inspect_wave(number))

        resource.__name__ = f"w{number}_protocol_resource"
        return resource

    for wave in range(27, 32):
        mcp.resource(f"athena://w{wave}-protocol")(_wave_resource(wave))
