"""KC144 W21 ledger-commit and promotion-authority handoff.

W21 consumes the W20 evidence-only closure without collapsing five distinct
facts into one another:

1. the Athena control repository observed and admitted the W20 *protocol*;
2. a W20 persistent witness was control-admitted and IC10-reviewed;
3. an independent ledger authority authorized one exact append-only
   transaction;
4. that authority returned a signed commit-occurrence receipt; and
5. a different promotion authority made a separately signed decision.

The checked-in production registries and ledger are intentionally empty.
This runtime validates and compiles records.  It cannot mutate a ledger,
contact GitHub or an endpoint, dispatch a workflow, deploy, merge, or promote.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .persistent_return_ic10 import (
    FrozenPersistentReturnIC10Gate,
    _addressed_material,
    _decision_digest as _w20_decision_digest,
)
from .provider_admission_execution import (
    _normalize_authority,
    _normalized_signature,
    _unsigned_material,
)
from .provider_trust_anchor import (
    _canonical_bytes,
    _verify_ed25519_signature,
)
from .replay_authority_ledger import (
    _assert_secret_free,
    _bounded_text,
    _digest,
    _exact_object,
    _parsed_timestamp,
    _timestamp,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w21_ledger_commit_promotion_handoff.json"

SCHEMA = "athena.xnav-w21-ledger-commit-promotion-handoff/v1"
PHASE = "KC144.XNAV.W21"

W20_HEAD = "772564d48618b3b35276baadd87cf36ce4db46fa"
W20_TREE = "74920d59e26e0a7b594d54866b6e375ef04e2aad"
W20_CONTRACT_DIGEST = (
    "sha256:c896d030fd8ac2d5392e1d47e53bebcb24f244c2fdd8a9851cfc210a4a0002a7"
)
W20_RECEIPT_ID = (
    "w20-return-ic10:sha256:"
    "1a4616d28442825dac1a0ec5a63644ffc74536efc4ec939f71371e40d84b717a"
)
W20_CONTROL_HEAD = "78bfbbbfc41cfc402235793afdcd5b190e71ba5b"
W20_CONTROL_BASE = "b53e07bb4f889cfa126c3ef106fb55752603f0fe"
W20_CONTROL_RECEIPT_ID = (
    "w20-control-admission:sha256:"
    "4f110f3e44d4dfda3ae30262a6c2baacb4cd16d9091245c6c3f7ba8bb6222c10"
)
W20_CONTROL_RECEIPT_SCHEMA = (
    "athena.control-w20-runtime-persistent-return-ic10-admission/v1"
)

LEDGER_SCHEMA = "athena.persistent-witness-return-ledger/v1"
LEDGER_ENTRY_SCHEMA = "athena.persistent-witness-return-ledger-entry/v1"
TRANSACTION_SCHEMA = "athena.w21-ledger-commit-transaction/v1"
AUTHORIZATION_SCHEMA = "athena.w21-ledger-commit-authorization/v1"
COMMIT_RECEIPT_SCHEMA = "athena.w21-ledger-commit-occurrence/v1"
PROMOTION_PACKET_SCHEMA = "athena.w21-promotion-authority-handoff/v1"
PROMOTION_DECISION_SCHEMA = "athena.w21-promotion-authority-decision/v1"
AUTHORITY_REGISTRY_SCHEMA = "athena.w21-authority-registry/v1"

SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT_VALUE = re.compile(r"^[0-9a-f]{40}$")

TRANSACTION_FIELDS = {
    "schema",
    "predecessor",
    "control_protocol_receipt_id",
    "ledger_position",
    "w20_closure",
    "ledger_entry",
    "commit_constraints",
    "transaction_digest",
}
TRANSACTION_PREDECESSOR_FIELDS = {
    "w20_head",
    "w20_tree",
    "w20_contract_digest",
    "w20_runtime_receipt_id",
    "w20_control_head",
    "w20_control_receipt_id",
}
LEDGER_POSITION_FIELDS = {
    "sequence",
    "previous_entry_digest",
    "ledger_root_before",
    "ledger_root_after",
}
W20_CLOSURE_FIELDS = {
    "persistent_witness_receipt_id",
    "persistent_witness_digest",
    "control_admission_digest",
    "ic10_review_packet_digest",
    "ic10_decision_digest",
}
COMMIT_CONSTRAINT_FIELDS = {
    "append_only",
    "hash_chained",
    "exact_sequence_required",
    "exact_previous_root_required",
    "exact_next_root_required",
    "independent_authority_signature_required",
    "commit_occurrence_receipt_required",
    "runtime_can_mutate_ledger",
}
AUTHORIZATION_FIELDS = {
    "schema",
    "transaction_digest",
    "authorization",
    "ledger_constraints",
    "signature",
    "authorization_digest",
}
AUTHORIZATION_BODY_FIELDS = {
    "authority_id",
    "ledger_repository",
    "ledger_ref",
    "authorized_at",
}
AUTHORIZATION_CONSTRAINT_FIELDS = {
    "sequence",
    "previous_entry_digest",
    "ledger_root_before",
    "ledger_root_after",
}
COMMIT_RECEIPT_FIELDS = {
    "schema",
    "transaction_digest",
    "authorization_digest",
    "authority_id",
    "ledger_repository",
    "ledger_ref",
    "ledger_commit",
    "committed_at",
    "sequence",
    "entry_digest",
    "previous_ledger_root",
    "committed_ledger_root",
    "signature",
    "receipt_digest",
}
PROMOTION_PACKET_FIELDS = {
    "schema",
    "predecessor",
    "ledger_commit_receipt_digest",
    "ledger_commit",
    "committed_ledger_root",
    "ledger_entry_digest",
    "ic10_decision_digest",
    "target",
    "promotion_constraints",
    "packet_digest",
}
PROMOTION_PREDECESSOR_FIELDS = {
    "w20_head",
    "w20_control_head",
    "w21_transaction_digest",
    "w21_authorization_digest",
}
PROMOTION_TARGET_FIELDS = {
    "runtime_repository",
    "runtime_head",
    "candidate_image_id",
    "target_environment",
    "target_ref",
}
PROMOTION_CONSTRAINT_FIELDS = {
    "committed_ledger_entry_required",
    "ic10_evidence_admission_required",
    "separate_promotion_authority_required",
    "promotion_execution_receipt_required",
    "runtime_can_promote",
}
PROMOTION_DECISION_FIELDS = {
    "schema",
    "packet_digest",
    "authority_id",
    "decision",
    "decided_at",
    "target_environment",
    "reason_code",
    "signature",
    "decision_digest",
}

EXPECTED_W20_CLOSURE_STATUS = (
    "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_AND_IC10_REVIEW__"
    "LEDGER_COMMIT_AND_PROMOTION_OPEN"
)


class LedgerCommitPromotionHandoffError(RuntimeError):
    """Raised when the frozen W21 contract or ledger is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LedgerCommitPromotionHandoffError(
            f"{path.name} must contain an object"
        )
    return value


def _sha(value: Any, path: str) -> str:
    text = _bounded_text(value, path)
    if not SHA256_VALUE.fullmatch(text):
        raise ValueError(f"{path} must be sha256:<64 lowercase hex>")
    return text


def _commit(value: Any, path: str) -> str:
    text = _bounded_text(value, path)
    if not COMMIT_VALUE.fullmatch(text):
        raise ValueError(f"{path} must be exact 40-hex")
    return text


def _positive_int(value: Any, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{path} must be a positive integer")
    return value


def _nullable_sha(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return _sha(value, path)


def _transaction_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "transaction_digest"))


def _authorization_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "authorization_digest"))


def _commit_receipt_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "receipt_digest"))


def _promotion_packet_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "packet_digest"))


def _promotion_decision_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "decision_digest"))


def _control_receipt_id(value: dict[str, Any]) -> str:
    body = {
        key: deepcopy(nested)
        for key, nested in value.items()
        if key != "receipt_id"
    }
    return (
        "w20-control-admission:sha256:"
        + hashlib.sha256(_canonical_bytes(body)).hexdigest()
    )


class FrozenLedgerCommitPromotionHandoff:
    """Frozen W21 commit authority and promotion handoff verifier."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w20_gate: FrozenPersistentReturnIC10Gate,
        entries: list[dict[str, Any]],
        commit_authorities: dict[str, dict[str, Any]],
        promotion_authorities: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.w20_gate = w20_gate
        self.entries = entries
        self.commit_authorities = commit_authorities
        self.promotion_authorities = promotion_authorities

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w20_gate: FrozenPersistentReturnIC10Gate | None = None,
    ) -> "FrozenLedgerCommitPromotionHandoff":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise LedgerCommitPromotionHandoffError(
                "unexpected W21 schema or phase"
            )
        w20_gate = w20_gate or FrozenPersistentReturnIC10Gate.load()

        expected_predecessor = {
            "runtime_repository": "demeet2k/athena-mcp-server",
            "runtime_pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w20_head": W20_HEAD,
            "w20_tree": W20_TREE,
            "w20_contract_digest": W20_CONTRACT_DIGEST,
            "w20_runtime_receipt_id": W20_RECEIPT_ID,
            "w20_p07_run_id": 30257976032,
            "w20_p08_run_id": 30257975940,
            "w20_stdio_receipt_id": (
                "mcp-host:sha256:"
                "cc35cd217e0f27c0f6746e79819202bf5eaf3eb533cb48692b29f4610fc2bfd6"
            ),
            "w20_candidate_receipt_id": (
                "p08-candidate:sha256:"
                "10291f6159c9add92da6a2d04891d51f8fe363c7bb3c4c3d1bfc028f11a86dd0"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise LedgerCommitPromotionHandoffError(
                "W21 runtime predecessor lineage mismatch"
            )

        observation = _exact_object(
            snapshot.get("control_protocol_observation"),
            {
                "repository",
                "pull_request",
                "branch",
                "head",
                "base",
                "receipt_id",
                "receipt_schema",
                "runtime_head",
                "runtime_tree",
                "verdict",
                "hosted_runner_status",
                "grants_production_authority",
            },
            "control_protocol_observation",
        )
        expected_observation = {
            "repository": "demeet2k/Athena",
            "pull_request": 17,
            "branch": "agent/w20-admit-persistent-return-ic10",
            "head": W20_CONTROL_HEAD,
            "base": W20_CONTROL_BASE,
            "receipt_id": W20_CONTROL_RECEIPT_ID,
            "receipt_schema": W20_CONTROL_RECEIPT_SCHEMA,
            "runtime_head": W20_HEAD,
            "runtime_tree": W20_TREE,
            "verdict": (
                "PASS_W20_PERSISTENT_RETURN_LEDGER_IC10_PROTOCOL_ADMITTED__"
                "HOLD_EXTERNAL_WITNESS_CONTROL_REVIEW_AND_LEDGER_COMMIT"
            ),
            "hosted_runner_status": (
                "HOLD[PLATFORM_OBSTRUCTION_BEFORE_FIRST_STEP]"
            ),
            "grants_production_authority": False,
        }
        if observation != expected_observation:
            raise LedgerCommitPromotionHandoffError(
                "W20 control protocol observation mismatch"
            )

        expected_commit_contract = {
            "ledger_schema": LEDGER_SCHEMA,
            "ledger_entry_schema": LEDGER_ENTRY_SCHEMA,
            "transaction_schema": TRANSACTION_SCHEMA,
            "authorization_schema": AUTHORIZATION_SCHEMA,
            "commit_receipt_schema": COMMIT_RECEIPT_SCHEMA,
            "append_only": True,
            "hash_chained": True,
            "exact_sequence_required": True,
            "exact_previous_root_required": True,
            "exact_next_root_required": True,
            "separate_commit_authority_signature_required": True,
            "signed_commit_occurrence_required": True,
            "self_supplied_authority_keys_allowed": False,
            "runtime_can_mutate_ledger": False,
        }
        if snapshot.get("ledger_commit_contract") != expected_commit_contract:
            raise LedgerCommitPromotionHandoffError(
                "W21 ledger commit contract drift"
            )

        raw_ledger = _exact_object(
            snapshot.get("committed_ledger"),
            {"schema", "entry_schema", "entries"},
            "committed_ledger",
        )
        if (
            raw_ledger.get("schema") != LEDGER_SCHEMA
            or raw_ledger.get("entry_schema") != LEDGER_ENTRY_SCHEMA
            or not isinstance(raw_ledger.get("entries"), list)
        ):
            raise LedgerCommitPromotionHandoffError(
                "W21 committed ledger contract drift"
            )
        entries: list[dict[str, Any]] = []
        previous: str | None = None
        for sequence, raw_entry in enumerate(
            raw_ledger["entries"], start=1
        ):
            entry = w20_gate._normalize_ledger_entry(raw_entry)
            if entry["sequence"] != sequence:
                raise LedgerCommitPromotionHandoffError(
                    "W21 ledger sequence is not contiguous"
                )
            if entry["previous_entry_digest"] != previous:
                raise LedgerCommitPromotionHandoffError(
                    "W21 ledger entry chain is broken"
                )
            entries.append(entry)
            previous = entry["entry_digest"]

        commit_authorities = cls._load_authority_registry(
            snapshot.get("commit_authority_registry"),
            "commit_authority_registry",
        )
        promotion_authorities = cls._load_authority_registry(
            snapshot.get("promotion_authority_registry"),
            "promotion_authority_registry",
        )
        overlap = set(commit_authorities) & set(promotion_authorities)
        if overlap:
            raise LedgerCommitPromotionHandoffError(
                "commit and promotion authority identities must be separate"
            )

        expected_promotion_contract = {
            "packet_schema": PROMOTION_PACKET_SCHEMA,
            "decision_schema": PROMOTION_DECISION_SCHEMA,
            "allowed_decisions": [
                "AUTHORIZE_PROMOTION",
                "HOLD_PROMOTION",
            ],
            "committed_ledger_entry_required": True,
            "ic10_evidence_admission_required": True,
            "separate_promotion_authority_signature_required": True,
            "promotion_execution_receipt_required": True,
            "self_supplied_authority_keys_allowed": False,
            "runtime_can_mutate_promotion_registry": False,
            "runtime_can_promote": False,
        }
        if snapshot.get("promotion_contract") != expected_promotion_contract:
            raise LedgerCommitPromotionHandoffError(
                "W21 promotion contract drift"
            )

        expected_boundaries = {
            "w20_control_protocol_admission_observed": True,
            "w20_control_receipt_grants_production_authority": False,
            "production_control_authority_pinned": bool(
                w20_gate.w19_gate.authorities
            ),
            "production_ic10_reviewer_pinned": bool(w20_gate.reviewers),
            "production_commit_authority_pinned": bool(commit_authorities),
            "production_promotion_authority_pinned": bool(
                promotion_authorities
            ),
            "persistent_witness_validated": False,
            "control_plane_witness_admitted": False,
            "ic10_review_recorded": False,
            "ledger_commit_authorized": False,
            "ledger_entry_committed": bool(entries),
            "promotion_authorized": False,
            "promotion_executed": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise LedgerCommitPromotionHandoffError(
                "W21 boundary state drift"
            )
        if snapshot.get("successor") != (
            "KC144.XNAV.W22::RETURN-INDEPENDENT-LEDGER-COMMIT-"
            "AND-PROMOTION-AUTHORITY-DECISIONS"
        ):
            raise LedgerCommitPromotionHandoffError("W21 successor drift")
        material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(material):
            raise LedgerCommitPromotionHandoffError(
                "W21 contract digest mismatch"
            )
        return cls(
            snapshot,
            w20_gate,
            entries,
            commit_authorities,
            promotion_authorities,
        )

    @staticmethod
    def _load_authority_registry(
        value: Any,
        path: str,
    ) -> dict[str, dict[str, Any]]:
        registry = _exact_object(
            value,
            {
                "schema",
                "canonicalization",
                "signature_algorithm",
                "signature_encoding",
                "authorities",
            },
            path,
        )
        if {
            key: registry.get(key)
            for key in (
                "schema",
                "canonicalization",
                "signature_algorithm",
                "signature_encoding",
            )
        } != {
            "schema": AUTHORITY_REGISTRY_SCHEMA,
            "canonicalization": "KC144.CANON.JSON.V1",
            "signature_algorithm": "ed25519",
            "signature_encoding": "base64",
        }:
            raise LedgerCommitPromotionHandoffError(
                f"{path} contract drift"
            )
        raw_authorities = registry.get("authorities")
        if not isinstance(raw_authorities, list):
            raise LedgerCommitPromotionHandoffError(
                f"{path}.authorities must be a list"
            )
        authorities: dict[str, dict[str, Any]] = {}
        for raw_authority in raw_authorities:
            authority = _normalize_authority(raw_authority)
            authority_id = authority["authority_id"]
            if authority_id in authorities:
                raise LedgerCommitPromotionHandoffError(
                    f"duplicate authority in {path}"
                )
            authorities[authority_id] = authority
        return authorities

    @classmethod
    def load(
        cls,
        path: Path = DATA_PATH,
    ) -> "FrozenLedgerCommitPromotionHandoff":
        return cls.from_snapshot(_load_json(path))

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "W21_CONTROL_PROTOCOL_OBSERVED__LEDGER_COMMIT_AND_"
                "PROMOTION_AUTHORITIES_OPEN"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w20_head": W20_HEAD,
            "w20_tree": W20_TREE,
            "w20_control_head": W20_CONTROL_HEAD,
            "w20_control_receipt_id": W20_CONTROL_RECEIPT_ID,
            "w20_control_protocol_admission_observed": True,
            "w20_control_receipt_grants_production_authority": False,
            "production_commit_authority_count": len(
                self.commit_authorities
            ),
            "production_promotion_authority_count": len(
                self.promotion_authorities
            ),
            "committed_ledger_entry_count": len(self.entries),
            "committed_ledger_root": _digest(self.entries),
            "runtime_can_mutate_ledger": False,
            "runtime_can_promote": False,
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "cross_navigation_state": (
                "W21_PROTOCOL_COORDINATES_CLOSED__INDEPENDENT_COMMIT_"
                "AND_PROMOTION_RETURNS_OPEN"
            ),
            "successor": self.snapshot["successor"],
        }

    def inspect_control_protocol_admission(
        self,
        control_receipt_json: str,
    ) -> dict[str, Any]:
        """Verify the exact W20 control protocol receipt as observation only."""
        try:
            receipt = json.loads(control_receipt_json)
            if not isinstance(receipt, dict):
                raise ValueError("control receipt must be an object")
            _assert_secret_free(receipt, "control receipt")
            if receipt.get("schema") != W20_CONTROL_RECEIPT_SCHEMA:
                raise ValueError("control receipt schema mismatch")
            if receipt.get("phase") != "KC144.XNAV.W20":
                raise ValueError("control receipt phase mismatch")
            if receipt.get("receipt_id") != W20_CONTROL_RECEIPT_ID:
                raise ValueError("control receipt ID is not the admitted W20 ID")
            if _control_receipt_id(receipt) != W20_CONTROL_RECEIPT_ID:
                raise ValueError("control receipt content address mismatch")
            control = receipt.get("control")
            runtime = receipt.get("runtime")
            authority = receipt.get("authority")
            if not isinstance(control, dict) or not isinstance(runtime, dict):
                raise ValueError("control receipt coordinates are missing")
            if {
                "repository": control.get("repository"),
                "pull_request": control.get("pull_request"),
                "branch": control.get("branch"),
                "predecessor_head": control.get("predecessor_head"),
            } != {
                "repository": "demeet2k/Athena",
                "pull_request": 17,
                "branch": "agent/w20-admit-persistent-return-ic10",
                "predecessor_head": W20_CONTROL_BASE,
            }:
                raise ValueError("control receipt control coordinates mismatch")
            if {
                "repository": runtime.get("repository"),
                "pull_request": runtime.get("pull_request"),
                "exact_head": runtime.get("exact_head"),
                "exact_tree": runtime.get("exact_tree"),
                "contract_digest": runtime.get("contract_digest"),
                "runtime_receipt_id": runtime.get("runtime_receipt_id"),
            } != {
                "repository": "demeet2k/athena-mcp-server",
                "pull_request": 13,
                "exact_head": W20_HEAD,
                "exact_tree": W20_TREE,
                "contract_digest": W20_CONTRACT_DIGEST,
                "runtime_receipt_id": W20_RECEIPT_ID,
            }:
                raise ValueError("control receipt runtime coordinates mismatch")
            if (
                not isinstance(authority, dict)
                or any(value is not False for value in authority.values())
            ):
                raise ValueError(
                    "control protocol receipt must grant no production authority"
                )
            return {
                "status": (
                    "PASS_W20_CONTROL_PROTOCOL_RECEIPT_OBSERVED__"
                    "NO_PRODUCTION_AUTHORITY_GRANTED"
                ),
                "control_head": W20_CONTROL_HEAD,
                "control_receipt_id": W20_CONTROL_RECEIPT_ID,
                "runtime_head": W20_HEAD,
                "control_protocol_admission_observed": True,
                "control_plane_witness_admitted": False,
                "ledger_entry_committed": False,
                "production_authority_granted": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._hold(
                "HOLD_W21_CONTROL_PROTOCOL_RECEIPT_REJECTED",
                str(error),
            )

    def compile_ledger_commit_transaction(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
        review_packet_json: str,
        ic10_decision_json: str,
        control_protocol_receipt_json: str,
    ) -> dict[str, Any]:
        """Compile one exact commit transaction from a live W20 closure."""
        observation = self.inspect_control_protocol_admission(
            control_protocol_receipt_json
        )
        if not observation.get("status", "").startswith(
            "PASS_W20_CONTROL_PROTOCOL_RECEIPT_OBSERVED"
        ):
            return observation
        closure = self.w20_gate.evaluate_closure(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
            control_admission_json,
            review_packet_json,
            ic10_decision_json,
        )
        if closure.get("status") != EXPECTED_W20_CLOSURE_STATUS:
            return {
                **closure,
                "status": "HOLD_W21_W20_EVIDENCE_CLOSURE_OPEN",
                "ledger_commit_authorized": False,
                "ledger_entry_committed": False,
            }
        compiled = self.w20_gate.compile_ledger_entry(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
            control_admission_json,
        )
        if compiled.get("status") != (
            "LEDGER_ENTRY_CANDIDATE_COMPILED__NOT_COMMITTED"
        ):
            return compiled
        entry = deepcopy(compiled["ledger_entry"])
        sequence = len(self.entries) + 1
        previous = (
            self.entries[-1]["entry_digest"] if self.entries else None
        )
        if (
            entry["sequence"] != sequence
            or entry["previous_entry_digest"] != previous
        ):
            return self._hold(
                "HOLD_W21_STALE_OR_NONAPPEND_LEDGER_CANDIDATE",
                "W20 ledger candidate does not extend the frozen W21 root",
            )
        packet = self.w20_gate._normalize_review_packet(
            json.loads(review_packet_json)
        )
        decision = self.w20_gate._normalize_ic10_decision(
            json.loads(ic10_decision_json)
        )
        if decision["review_packet_digest"] != packet["packet_digest"]:
            return self._hold(
                "HOLD_W21_W20_EVIDENCE_CLOSURE_OPEN",
                "IC10 decision does not bind the review packet",
            )
        before = _digest(self.entries)
        after = _digest([*self.entries, entry])
        transaction = {
            "schema": TRANSACTION_SCHEMA,
            "predecessor": {
                "w20_head": W20_HEAD,
                "w20_tree": W20_TREE,
                "w20_contract_digest": W20_CONTRACT_DIGEST,
                "w20_runtime_receipt_id": W20_RECEIPT_ID,
                "w20_control_head": W20_CONTROL_HEAD,
                "w20_control_receipt_id": W20_CONTROL_RECEIPT_ID,
            },
            "control_protocol_receipt_id": W20_CONTROL_RECEIPT_ID,
            "ledger_position": {
                "sequence": sequence,
                "previous_entry_digest": previous,
                "ledger_root_before": before,
                "ledger_root_after": after,
            },
            "w20_closure": {
                "persistent_witness_receipt_id": entry[
                    "persistent_witness_receipt_id"
                ],
                "persistent_witness_digest": entry[
                    "persistent_witness_digest"
                ],
                "control_admission_digest": entry[
                    "control_admission_digest"
                ],
                "ic10_review_packet_digest": packet["packet_digest"],
                "ic10_decision_digest": decision["decision_digest"],
            },
            "ledger_entry": entry,
            "commit_constraints": {
                "append_only": True,
                "hash_chained": True,
                "exact_sequence_required": True,
                "exact_previous_root_required": True,
                "exact_next_root_required": True,
                "independent_authority_signature_required": True,
                "commit_occurrence_receipt_required": True,
                "runtime_can_mutate_ledger": False,
            },
            "transaction_digest": None,
        }
        transaction["transaction_digest"] = _transaction_digest(transaction)
        template = {
            "schema": AUTHORIZATION_SCHEMA,
            "transaction_digest": transaction["transaction_digest"],
            "authorization": {
                "authority_id": None,
                "ledger_repository": "demeet2k/Athena",
                "ledger_ref": None,
                "authorized_at": None,
            },
            "ledger_constraints": deepcopy(transaction["ledger_position"]),
            "signature": {
                "algorithm": "ed25519",
                "key_id": None,
                "value": None,
            },
            "authorization_digest": None,
        }
        return {
            "status": (
                "LEDGER_COMMIT_TRANSACTION_AND_AUTHORIZATION_TEMPLATE_READY__"
                "NOT_AUTHORIZED_NOT_COMMITTED"
            ),
            "transaction": transaction,
            "authorization_template": template,
            "persistent_witness_validated": True,
            "control_plane_witness_admitted": True,
            "ic10_review_recorded": True,
            "ledger_commit_authorized": False,
            "ledger_entry_committed": False,
            **self._negative_boundaries(),
        }

    def _normalize_transaction(self, value: Any) -> dict[str, Any]:
        transaction = _exact_object(
            value, TRANSACTION_FIELDS, "transaction"
        )
        predecessor = _exact_object(
            transaction.get("predecessor"),
            TRANSACTION_PREDECESSOR_FIELDS,
            "transaction.predecessor",
        )
        normalized_predecessor = {
            "w20_head": _commit(
                predecessor.get("w20_head"),
                "transaction.predecessor.w20_head",
            ),
            "w20_tree": _commit(
                predecessor.get("w20_tree"),
                "transaction.predecessor.w20_tree",
            ),
            "w20_contract_digest": _sha(
                predecessor.get("w20_contract_digest"),
                "transaction.predecessor.w20_contract_digest",
            ),
            "w20_runtime_receipt_id": _bounded_text(
                predecessor.get("w20_runtime_receipt_id"),
                "transaction.predecessor.w20_runtime_receipt_id",
            ),
            "w20_control_head": _commit(
                predecessor.get("w20_control_head"),
                "transaction.predecessor.w20_control_head",
            ),
            "w20_control_receipt_id": _bounded_text(
                predecessor.get("w20_control_receipt_id"),
                "transaction.predecessor.w20_control_receipt_id",
            ),
        }
        expected_predecessor = {
            "w20_head": W20_HEAD,
            "w20_tree": W20_TREE,
            "w20_contract_digest": W20_CONTRACT_DIGEST,
            "w20_runtime_receipt_id": W20_RECEIPT_ID,
            "w20_control_head": W20_CONTROL_HEAD,
            "w20_control_receipt_id": W20_CONTROL_RECEIPT_ID,
        }
        if normalized_predecessor != expected_predecessor:
            raise ValueError("transaction predecessor mismatch")

        position = _exact_object(
            transaction.get("ledger_position"),
            LEDGER_POSITION_FIELDS,
            "transaction.ledger_position",
        )
        normalized_position = {
            "sequence": _positive_int(
                position.get("sequence"),
                "transaction.ledger_position.sequence",
            ),
            "previous_entry_digest": _nullable_sha(
                position.get("previous_entry_digest"),
                "transaction.ledger_position.previous_entry_digest",
            ),
            "ledger_root_before": _sha(
                position.get("ledger_root_before"),
                "transaction.ledger_position.ledger_root_before",
            ),
            "ledger_root_after": _sha(
                position.get("ledger_root_after"),
                "transaction.ledger_position.ledger_root_after",
            ),
        }
        closure = _exact_object(
            transaction.get("w20_closure"),
            W20_CLOSURE_FIELDS,
            "transaction.w20_closure",
        )
        normalized_closure = {
            "persistent_witness_receipt_id": _bounded_text(
                closure.get("persistent_witness_receipt_id"),
                "transaction.w20_closure.persistent_witness_receipt_id",
            ),
            "persistent_witness_digest": _sha(
                closure.get("persistent_witness_digest"),
                "transaction.w20_closure.persistent_witness_digest",
            ),
            "control_admission_digest": _sha(
                closure.get("control_admission_digest"),
                "transaction.w20_closure.control_admission_digest",
            ),
            "ic10_review_packet_digest": _sha(
                closure.get("ic10_review_packet_digest"),
                "transaction.w20_closure.ic10_review_packet_digest",
            ),
            "ic10_decision_digest": _sha(
                closure.get("ic10_decision_digest"),
                "transaction.w20_closure.ic10_decision_digest",
            ),
        }
        constraints = _exact_object(
            transaction.get("commit_constraints"),
            COMMIT_CONSTRAINT_FIELDS,
            "transaction.commit_constraints",
        )
        expected_constraints = {
            "append_only": True,
            "hash_chained": True,
            "exact_sequence_required": True,
            "exact_previous_root_required": True,
            "exact_next_root_required": True,
            "independent_authority_signature_required": True,
            "commit_occurrence_receipt_required": True,
            "runtime_can_mutate_ledger": False,
        }
        if constraints != expected_constraints:
            raise ValueError("transaction commit constraints mismatch")
        entry = self.w20_gate._normalize_ledger_entry(
            transaction.get("ledger_entry")
        )
        expected_sequence = len(self.entries) + 1
        expected_previous = (
            self.entries[-1]["entry_digest"] if self.entries else None
        )
        expected_before = _digest(self.entries)
        expected_after = _digest([*self.entries, entry])
        if normalized_position != {
            "sequence": expected_sequence,
            "previous_entry_digest": expected_previous,
            "ledger_root_before": expected_before,
            "ledger_root_after": expected_after,
        }:
            raise ValueError("transaction does not extend exact ledger root")
        if (
            entry["sequence"] != expected_sequence
            or entry["previous_entry_digest"] != expected_previous
            or entry["persistent_witness_receipt_id"]
            != normalized_closure["persistent_witness_receipt_id"]
            or entry["persistent_witness_digest"]
            != normalized_closure["persistent_witness_digest"]
            or entry["control_admission_digest"]
            != normalized_closure["control_admission_digest"]
        ):
            raise ValueError("transaction W20 closure binding mismatch")
        normalized = {
            "schema": _bounded_text(
                transaction.get("schema"), "transaction.schema"
            ),
            "predecessor": normalized_predecessor,
            "control_protocol_receipt_id": _bounded_text(
                transaction.get("control_protocol_receipt_id"),
                "transaction.control_protocol_receipt_id",
            ),
            "ledger_position": normalized_position,
            "w20_closure": normalized_closure,
            "ledger_entry": entry,
            "commit_constraints": expected_constraints,
            "transaction_digest": _sha(
                transaction.get("transaction_digest"),
                "transaction.transaction_digest",
            ),
        }
        if normalized["schema"] != TRANSACTION_SCHEMA:
            raise ValueError("transaction schema mismatch")
        if (
            normalized["control_protocol_receipt_id"]
            != W20_CONTROL_RECEIPT_ID
        ):
            raise ValueError("transaction control receipt mismatch")
        if normalized["transaction_digest"] != _transaction_digest(
            normalized
        ):
            raise ValueError("transaction digest mismatch")
        return normalized

    def _normalize_authorization(
        self,
        value: Any,
        transaction: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        authorization = _exact_object(
            value, AUTHORIZATION_FIELDS, "commit authorization"
        )
        body = _exact_object(
            authorization.get("authorization"),
            AUTHORIZATION_BODY_FIELDS,
            "commit authorization.authorization",
        )
        normalized_body = {
            "authority_id": _bounded_text(
                body.get("authority_id"),
                "commit authorization.authorization.authority_id",
            ),
            "ledger_repository": _bounded_text(
                body.get("ledger_repository"),
                "commit authorization.authorization.ledger_repository",
            ),
            "ledger_ref": _bounded_text(
                body.get("ledger_ref"),
                "commit authorization.authorization.ledger_ref",
            ),
            "authorized_at": _timestamp(
                body.get("authorized_at"),
                "commit authorization.authorization.authorized_at",
            ),
        }
        constraints = _exact_object(
            authorization.get("ledger_constraints"),
            AUTHORIZATION_CONSTRAINT_FIELDS,
            "commit authorization.ledger_constraints",
        )
        normalized_constraints = {
            "sequence": _positive_int(
                constraints.get("sequence"),
                "commit authorization.ledger_constraints.sequence",
            ),
            "previous_entry_digest": _nullable_sha(
                constraints.get("previous_entry_digest"),
                "commit authorization.ledger_constraints.previous_entry_digest",
            ),
            "ledger_root_before": _sha(
                constraints.get("ledger_root_before"),
                "commit authorization.ledger_constraints.ledger_root_before",
            ),
            "ledger_root_after": _sha(
                constraints.get("ledger_root_after"),
                "commit authorization.ledger_constraints.ledger_root_after",
            ),
        }
        normalized = {
            "schema": _bounded_text(
                authorization.get("schema"),
                "commit authorization.schema",
            ),
            "transaction_digest": _sha(
                authorization.get("transaction_digest"),
                "commit authorization.transaction_digest",
            ),
            "authorization": normalized_body,
            "ledger_constraints": normalized_constraints,
            "signature": _normalized_signature(
                authorization.get("signature"),
                "commit authorization.signature",
            ),
            "authorization_digest": _sha(
                authorization.get("authorization_digest"),
                "commit authorization.authorization_digest",
            ),
        }
        if normalized["schema"] != AUTHORIZATION_SCHEMA:
            raise ValueError("commit authorization schema mismatch")
        if (
            normalized["transaction_digest"]
            != transaction["transaction_digest"]
            or normalized["ledger_constraints"]
            != transaction["ledger_position"]
        ):
            raise ValueError(
                "commit authorization does not bind exact transaction"
            )
        if normalized_body["ledger_repository"] != "demeet2k/Athena":
            raise ValueError("ledger repository must be demeet2k/Athena")
        authority = self.commit_authorities.get(
            normalized_body["authority_id"]
        )
        if authority is None:
            raise LookupError("commit authority is not pinned")
        if normalized["signature"]["key_id"] != authority["key_id"]:
            raise ValueError("commit authority key ID mismatch")
        authorized_at = _parsed_timestamp(normalized_body["authorized_at"])
        if not (
            _parsed_timestamp(authority["valid_from"])
            <= authorized_at
            <= _parsed_timestamp(authority["valid_until"])
        ):
            raise ValueError("commit authority was not valid at authorization")
        if not _verify_ed25519_signature(
            authority["public_key_base64"],
            normalized["signature"]["value"],
            _unsigned_material(normalized, "authorization_digest"),
        ):
            raise ValueError("commit authorization signature mismatch")
        if normalized["authorization_digest"] != _authorization_digest(
            normalized
        ):
            raise ValueError("commit authorization digest mismatch")
        return normalized, authority

    def inspect_commit_authorization(
        self,
        transaction_json: str,
        authorization_json: str,
    ) -> dict[str, Any]:
        """Verify a pinned authority's exact ledger commit authorization."""
        try:
            transaction = self._normalize_transaction(
                json.loads(transaction_json)
            )
            try:
                authorization, authority = self._normalize_authorization(
                    json.loads(authorization_json),
                    transaction,
                )
            except LookupError as error:
                return self._hold(
                    "HOLD_W21_COMMIT_AUTHORITY_NOT_PINNED", str(error)
                )
            return {
                "status": (
                    "PASS_LEDGER_COMMIT_AUTHORIZATION_VERIFIED__"
                    "COMMIT_OCCURRENCE_OPEN"
                ),
                "transaction_digest": transaction["transaction_digest"],
                "authorization_digest": authorization[
                    "authorization_digest"
                ],
                "authority_id": authority["authority_id"],
                "ledger_commit_authorized": True,
                "ledger_entry_committed": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._hold(
                "HOLD_W21_LEDGER_COMMIT_AUTHORIZATION_REJECTED", str(error)
            )

    def build_commit_occurrence_template(
        self,
        transaction_json: str,
        authorization_json: str,
    ) -> dict[str, Any]:
        """Build a receipt template after exact commit authorization."""
        inspected = self.inspect_commit_authorization(
            transaction_json, authorization_json
        )
        if inspected.get("status") != (
            "PASS_LEDGER_COMMIT_AUTHORIZATION_VERIFIED__"
            "COMMIT_OCCURRENCE_OPEN"
        ):
            return inspected
        transaction = self._normalize_transaction(
            json.loads(transaction_json)
        )
        authorization, authority = self._normalize_authorization(
            json.loads(authorization_json), transaction
        )
        body = authorization["authorization"]
        position = transaction["ledger_position"]
        template = {
            "schema": COMMIT_RECEIPT_SCHEMA,
            "transaction_digest": transaction["transaction_digest"],
            "authorization_digest": authorization[
                "authorization_digest"
            ],
            "authority_id": authority["authority_id"],
            "ledger_repository": body["ledger_repository"],
            "ledger_ref": body["ledger_ref"],
            "ledger_commit": None,
            "committed_at": None,
            "sequence": position["sequence"],
            "entry_digest": transaction["ledger_entry"]["entry_digest"],
            "previous_ledger_root": position["ledger_root_before"],
            "committed_ledger_root": position["ledger_root_after"],
            "signature": {
                "algorithm": "ed25519",
                "key_id": authority["key_id"],
                "value": None,
            },
            "receipt_digest": None,
        }
        return {
            "status": (
                "LEDGER_COMMIT_OCCURRENCE_TEMPLATE_READY__NOT_COMMITTED"
            ),
            "template": template,
            "ledger_commit_authorized": True,
            "ledger_entry_committed": False,
            **self._negative_boundaries(),
        }

    def _normalize_commit_receipt(
        self,
        value: Any,
        transaction: dict[str, Any],
        authorization: dict[str, Any],
        authority: dict[str, Any],
    ) -> dict[str, Any]:
        receipt = _exact_object(
            value, COMMIT_RECEIPT_FIELDS, "commit occurrence receipt"
        )
        normalized = {
            "schema": _bounded_text(
                receipt.get("schema"), "commit receipt.schema"
            ),
            "transaction_digest": _sha(
                receipt.get("transaction_digest"),
                "commit receipt.transaction_digest",
            ),
            "authorization_digest": _sha(
                receipt.get("authorization_digest"),
                "commit receipt.authorization_digest",
            ),
            "authority_id": _bounded_text(
                receipt.get("authority_id"),
                "commit receipt.authority_id",
            ),
            "ledger_repository": _bounded_text(
                receipt.get("ledger_repository"),
                "commit receipt.ledger_repository",
            ),
            "ledger_ref": _bounded_text(
                receipt.get("ledger_ref"), "commit receipt.ledger_ref"
            ),
            "ledger_commit": _commit(
                receipt.get("ledger_commit"),
                "commit receipt.ledger_commit",
            ),
            "committed_at": _timestamp(
                receipt.get("committed_at"),
                "commit receipt.committed_at",
            ),
            "sequence": _positive_int(
                receipt.get("sequence"), "commit receipt.sequence"
            ),
            "entry_digest": _sha(
                receipt.get("entry_digest"),
                "commit receipt.entry_digest",
            ),
            "previous_ledger_root": _sha(
                receipt.get("previous_ledger_root"),
                "commit receipt.previous_ledger_root",
            ),
            "committed_ledger_root": _sha(
                receipt.get("committed_ledger_root"),
                "commit receipt.committed_ledger_root",
            ),
            "signature": _normalized_signature(
                receipt.get("signature"), "commit receipt.signature"
            ),
            "receipt_digest": _sha(
                receipt.get("receipt_digest"),
                "commit receipt.receipt_digest",
            ),
        }
        body = authorization["authorization"]
        position = transaction["ledger_position"]
        expected = {
            "schema": COMMIT_RECEIPT_SCHEMA,
            "transaction_digest": transaction["transaction_digest"],
            "authorization_digest": authorization[
                "authorization_digest"
            ],
            "authority_id": authority["authority_id"],
            "ledger_repository": body["ledger_repository"],
            "ledger_ref": body["ledger_ref"],
            "sequence": position["sequence"],
            "entry_digest": transaction["ledger_entry"]["entry_digest"],
            "previous_ledger_root": position["ledger_root_before"],
            "committed_ledger_root": position["ledger_root_after"],
        }
        for key, expected_value in expected.items():
            if normalized[key] != expected_value:
                raise ValueError(f"commit receipt {key} mismatch")
        if normalized["signature"]["key_id"] != authority["key_id"]:
            raise ValueError("commit receipt key ID mismatch")
        committed_at = _parsed_timestamp(normalized["committed_at"])
        authorized_at = _parsed_timestamp(body["authorized_at"])
        if committed_at < authorized_at:
            raise ValueError("commit occurrence predates authorization")
        if not (
            _parsed_timestamp(authority["valid_from"])
            <= committed_at
            <= _parsed_timestamp(authority["valid_until"])
        ):
            raise ValueError("commit authority was not valid at occurrence")
        if not _verify_ed25519_signature(
            authority["public_key_base64"],
            normalized["signature"]["value"],
            _unsigned_material(normalized, "receipt_digest"),
        ):
            raise ValueError("commit occurrence signature mismatch")
        if normalized["receipt_digest"] != _commit_receipt_digest(
            normalized
        ):
            raise ValueError("commit occurrence receipt digest mismatch")
        return normalized

    def inspect_commit_occurrence(
        self,
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
    ) -> dict[str, Any]:
        """Verify a signed ledger commit occurrence without mutating state."""
        try:
            transaction = self._normalize_transaction(
                json.loads(transaction_json)
            )
            try:
                authorization, authority = self._normalize_authorization(
                    json.loads(authorization_json), transaction
                )
            except LookupError as error:
                return self._hold(
                    "HOLD_W21_COMMIT_AUTHORITY_NOT_PINNED", str(error)
                )
            receipt = self._normalize_commit_receipt(
                json.loads(commit_receipt_json),
                transaction,
                authorization,
                authority,
            )
            return {
                "status": (
                    "PASS_LEDGER_COMMIT_OCCURRENCE_VERIFIED__"
                    "PROMOTION_AUTHORITY_DECISION_OPEN"
                ),
                "transaction_digest": transaction["transaction_digest"],
                "authorization_digest": authorization[
                    "authorization_digest"
                ],
                "commit_receipt_digest": receipt["receipt_digest"],
                "ledger_commit": receipt["ledger_commit"],
                "committed_ledger_root": receipt[
                    "committed_ledger_root"
                ],
                "ledger_commit_authorized": True,
                "ledger_entry_committed": True,
                "runtime_mutated_ledger": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._hold(
                "HOLD_W21_LEDGER_COMMIT_OCCURRENCE_REJECTED", str(error)
            )

    def build_promotion_handoff(
        self,
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
        target_environment: str,
        target_ref: str,
    ) -> dict[str, Any]:
        """Build a promotion packet only after a signed commit occurrence."""
        inspected = self.inspect_commit_occurrence(
            transaction_json,
            authorization_json,
            commit_receipt_json,
        )
        if inspected.get("status") != (
            "PASS_LEDGER_COMMIT_OCCURRENCE_VERIFIED__"
            "PROMOTION_AUTHORITY_DECISION_OPEN"
        ):
            return inspected
        transaction = self._normalize_transaction(
            json.loads(transaction_json)
        )
        authorization, authority = self._normalize_authorization(
            json.loads(authorization_json), transaction
        )
        receipt = self._normalize_commit_receipt(
            json.loads(commit_receipt_json),
            transaction,
            authorization,
            authority,
        )
        target_environment = _bounded_text(
            target_environment, "target_environment"
        )
        target_ref = _bounded_text(target_ref, "target_ref")
        packet = {
            "schema": PROMOTION_PACKET_SCHEMA,
            "predecessor": {
                "w20_head": W20_HEAD,
                "w20_control_head": W20_CONTROL_HEAD,
                "w21_transaction_digest": transaction[
                    "transaction_digest"
                ],
                "w21_authorization_digest": authorization[
                    "authorization_digest"
                ],
            },
            "ledger_commit_receipt_digest": receipt["receipt_digest"],
            "ledger_commit": receipt["ledger_commit"],
            "committed_ledger_root": receipt["committed_ledger_root"],
            "ledger_entry_digest": transaction["ledger_entry"][
                "entry_digest"
            ],
            "ic10_decision_digest": transaction["w20_closure"][
                "ic10_decision_digest"
            ],
            "target": {
                "runtime_repository": "demeet2k/athena-mcp-server",
                "runtime_head": W20_HEAD,
                "candidate_image_id": (
                    "sha256:"
                    "173e0e922b13e895aca498db7ec66cf0dd324349265511cfbf59069a3d9f3612"
                ),
                "target_environment": target_environment,
                "target_ref": target_ref,
            },
            "promotion_constraints": {
                "committed_ledger_entry_required": True,
                "ic10_evidence_admission_required": True,
                "separate_promotion_authority_required": True,
                "promotion_execution_receipt_required": True,
                "runtime_can_promote": False,
            },
            "packet_digest": None,
        }
        packet["packet_digest"] = _promotion_packet_digest(packet)
        template = {
            "schema": PROMOTION_DECISION_SCHEMA,
            "packet_digest": packet["packet_digest"],
            "authority_id": None,
            "decision": None,
            "decided_at": None,
            "target_environment": target_environment,
            "reason_code": None,
            "signature": {
                "algorithm": "ed25519",
                "key_id": None,
                "value": None,
            },
            "decision_digest": None,
        }
        return {
            "status": (
                "PROMOTION_AUTHORITY_HANDOFF_READY__"
                "DECISION_AND_EXECUTION_OPEN"
            ),
            "promotion_packet": packet,
            "decision_template": template,
            "ledger_entry_committed": True,
            "promotion_authorized": False,
            **self._negative_boundaries(),
        }

    def _normalize_promotion_packet(
        self, value: Any
    ) -> dict[str, Any]:
        packet = _exact_object(
            value, PROMOTION_PACKET_FIELDS, "promotion packet"
        )
        predecessor = _exact_object(
            packet.get("predecessor"),
            PROMOTION_PREDECESSOR_FIELDS,
            "promotion packet.predecessor",
        )
        normalized_predecessor = {
            "w20_head": _commit(
                predecessor.get("w20_head"),
                "promotion packet.predecessor.w20_head",
            ),
            "w20_control_head": _commit(
                predecessor.get("w20_control_head"),
                "promotion packet.predecessor.w20_control_head",
            ),
            "w21_transaction_digest": _sha(
                predecessor.get("w21_transaction_digest"),
                "promotion packet.predecessor.w21_transaction_digest",
            ),
            "w21_authorization_digest": _sha(
                predecessor.get("w21_authorization_digest"),
                "promotion packet.predecessor.w21_authorization_digest",
            ),
        }
        if (
            normalized_predecessor["w20_head"] != W20_HEAD
            or normalized_predecessor["w20_control_head"]
            != W20_CONTROL_HEAD
        ):
            raise ValueError("promotion predecessor mismatch")
        target = _exact_object(
            packet.get("target"),
            PROMOTION_TARGET_FIELDS,
            "promotion packet.target",
        )
        normalized_target = {
            "runtime_repository": _bounded_text(
                target.get("runtime_repository"),
                "promotion packet.target.runtime_repository",
            ),
            "runtime_head": _commit(
                target.get("runtime_head"),
                "promotion packet.target.runtime_head",
            ),
            "candidate_image_id": _sha(
                target.get("candidate_image_id"),
                "promotion packet.target.candidate_image_id",
            ),
            "target_environment": _bounded_text(
                target.get("target_environment"),
                "promotion packet.target.target_environment",
            ),
            "target_ref": _bounded_text(
                target.get("target_ref"),
                "promotion packet.target.target_ref",
            ),
        }
        expected_target = {
            "runtime_repository": "demeet2k/athena-mcp-server",
            "runtime_head": W20_HEAD,
            "candidate_image_id": (
                "sha256:"
                "173e0e922b13e895aca498db7ec66cf0dd324349265511cfbf59069a3d9f3612"
            ),
        }
        for key, expected in expected_target.items():
            if normalized_target[key] != expected:
                raise ValueError(f"promotion target {key} mismatch")
        constraints = _exact_object(
            packet.get("promotion_constraints"),
            PROMOTION_CONSTRAINT_FIELDS,
            "promotion packet.promotion_constraints",
        )
        expected_constraints = {
            "committed_ledger_entry_required": True,
            "ic10_evidence_admission_required": True,
            "separate_promotion_authority_required": True,
            "promotion_execution_receipt_required": True,
            "runtime_can_promote": False,
        }
        if constraints != expected_constraints:
            raise ValueError("promotion constraints mismatch")
        normalized = {
            "schema": _bounded_text(
                packet.get("schema"), "promotion packet.schema"
            ),
            "predecessor": normalized_predecessor,
            "ledger_commit_receipt_digest": _sha(
                packet.get("ledger_commit_receipt_digest"),
                "promotion packet.ledger_commit_receipt_digest",
            ),
            "ledger_commit": _commit(
                packet.get("ledger_commit"),
                "promotion packet.ledger_commit",
            ),
            "committed_ledger_root": _sha(
                packet.get("committed_ledger_root"),
                "promotion packet.committed_ledger_root",
            ),
            "ledger_entry_digest": _sha(
                packet.get("ledger_entry_digest"),
                "promotion packet.ledger_entry_digest",
            ),
            "ic10_decision_digest": _sha(
                packet.get("ic10_decision_digest"),
                "promotion packet.ic10_decision_digest",
            ),
            "target": normalized_target,
            "promotion_constraints": expected_constraints,
            "packet_digest": _sha(
                packet.get("packet_digest"),
                "promotion packet.packet_digest",
            ),
        }
        if normalized["schema"] != PROMOTION_PACKET_SCHEMA:
            raise ValueError("promotion packet schema mismatch")
        if normalized["packet_digest"] != _promotion_packet_digest(
            normalized
        ):
            raise ValueError("promotion packet digest mismatch")
        return normalized

    def _normalize_promotion_decision(
        self,
        value: Any,
        packet: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        decision = _exact_object(
            value, PROMOTION_DECISION_FIELDS, "promotion decision"
        )
        normalized = {
            "schema": _bounded_text(
                decision.get("schema"), "promotion decision.schema"
            ),
            "packet_digest": _sha(
                decision.get("packet_digest"),
                "promotion decision.packet_digest",
            ),
            "authority_id": _bounded_text(
                decision.get("authority_id"),
                "promotion decision.authority_id",
            ),
            "decision": _bounded_text(
                decision.get("decision"), "promotion decision.decision"
            ),
            "decided_at": _timestamp(
                decision.get("decided_at"),
                "promotion decision.decided_at",
            ),
            "target_environment": _bounded_text(
                decision.get("target_environment"),
                "promotion decision.target_environment",
            ),
            "reason_code": _bounded_text(
                decision.get("reason_code"),
                "promotion decision.reason_code",
            ),
            "signature": _normalized_signature(
                decision.get("signature"), "promotion decision.signature"
            ),
            "decision_digest": _sha(
                decision.get("decision_digest"),
                "promotion decision.decision_digest",
            ),
        }
        if normalized["schema"] != PROMOTION_DECISION_SCHEMA:
            raise ValueError("promotion decision schema mismatch")
        if normalized["decision"] not in {
            "AUTHORIZE_PROMOTION",
            "HOLD_PROMOTION",
        }:
            raise ValueError("promotion decision is not allowed")
        if (
            normalized["packet_digest"] != packet["packet_digest"]
            or normalized["target_environment"]
            != packet["target"]["target_environment"]
        ):
            raise ValueError(
                "promotion decision does not bind exact packet target"
            )
        authority = self.promotion_authorities.get(
            normalized["authority_id"]
        )
        if authority is None:
            raise LookupError("promotion authority is not pinned")
        if normalized["authority_id"] in self.commit_authorities:
            raise ValueError(
                "promotion authority must be separate from commit authority"
            )
        if normalized["signature"]["key_id"] != authority["key_id"]:
            raise ValueError("promotion authority key ID mismatch")
        decided_at = _parsed_timestamp(normalized["decided_at"])
        if not (
            _parsed_timestamp(authority["valid_from"])
            <= decided_at
            <= _parsed_timestamp(authority["valid_until"])
        ):
            raise ValueError("promotion authority was not valid at decision")
        if not _verify_ed25519_signature(
            authority["public_key_base64"],
            normalized["signature"]["value"],
            _unsigned_material(normalized, "decision_digest"),
        ):
            raise ValueError("promotion decision signature mismatch")
        if normalized["decision_digest"] != _promotion_decision_digest(
            normalized
        ):
            raise ValueError("promotion decision digest mismatch")
        return normalized, authority

    def inspect_promotion_decision(
        self,
        promotion_packet_json: str,
        promotion_decision_json: str,
    ) -> dict[str, Any]:
        """Verify a distinct authority decision; never execute promotion."""
        try:
            packet = self._normalize_promotion_packet(
                json.loads(promotion_packet_json)
            )
            try:
                decision, authority = self._normalize_promotion_decision(
                    json.loads(promotion_decision_json), packet
                )
            except LookupError as error:
                return self._hold(
                    "HOLD_W21_PROMOTION_AUTHORITY_NOT_PINNED", str(error)
                )
            authorized = decision["decision"] == "AUTHORIZE_PROMOTION"
            return {
                "status": (
                    "PASS_PROMOTION_AUTHORITY_DECISION_VERIFIED__"
                    + (
                        "EXECUTION_RECEIPT_OPEN"
                        if authorized
                        else "PROMOTION_HELD"
                    )
                ),
                "packet_digest": packet["packet_digest"],
                "decision_digest": decision["decision_digest"],
                "authority_id": authority["authority_id"],
                "ledger_entry_committed": True,
                "promotion_authorized": authorized,
                "promotion_executed": False,
                "promotion_claimed": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._hold(
                "HOLD_W21_PROMOTION_DECISION_REJECTED", str(error)
            )

    def evaluate_closure(
        self,
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
        promotion_packet_json: str,
        promotion_decision_json: str,
    ) -> dict[str, Any]:
        """Evaluate the independent commit and promotion returns."""
        committed = self.inspect_commit_occurrence(
            transaction_json,
            authorization_json,
            commit_receipt_json,
        )
        if committed.get("status") != (
            "PASS_LEDGER_COMMIT_OCCURRENCE_VERIFIED__"
            "PROMOTION_AUTHORITY_DECISION_OPEN"
        ):
            return committed
        promotion = self.inspect_promotion_decision(
            promotion_packet_json, promotion_decision_json
        )
        if not promotion.get("status", "").startswith(
            "PASS_PROMOTION_AUTHORITY_DECISION_VERIFIED__"
        ):
            return promotion
        transaction = self._normalize_transaction(
            json.loads(transaction_json)
        )
        authorization, authority = self._normalize_authorization(
            json.loads(authorization_json), transaction
        )
        receipt = self._normalize_commit_receipt(
            json.loads(commit_receipt_json),
            transaction,
            authorization,
            authority,
        )
        packet = self._normalize_promotion_packet(
            json.loads(promotion_packet_json)
        )
        if {
            "transaction": packet["predecessor"][
                "w21_transaction_digest"
            ],
            "authorization": packet["predecessor"][
                "w21_authorization_digest"
            ],
            "receipt": packet["ledger_commit_receipt_digest"],
            "ledger_commit": packet["ledger_commit"],
            "ledger_root": packet["committed_ledger_root"],
            "entry": packet["ledger_entry_digest"],
            "ic10": packet["ic10_decision_digest"],
        } != {
            "transaction": transaction["transaction_digest"],
            "authorization": authorization["authorization_digest"],
            "receipt": receipt["receipt_digest"],
            "ledger_commit": receipt["ledger_commit"],
            "ledger_root": receipt["committed_ledger_root"],
            "entry": transaction["ledger_entry"]["entry_digest"],
            "ic10": transaction["w20_closure"]["ic10_decision_digest"],
        }:
            return self._hold(
                "HOLD_W21_PROMOTION_HANDOFF_BINDING_REJECTED",
                "promotion packet does not bind the committed W21 transaction",
            )
        return {
            "status": (
                "PASS_W21_LEDGER_COMMIT_AND_PROMOTION_DECISION_CLOSED__"
                "PROMOTION_EXECUTION_RECEIPT_OPEN"
            ),
            "transaction_digest": transaction["transaction_digest"],
            "authorization_digest": authorization[
                "authorization_digest"
            ],
            "commit_receipt_digest": receipt["receipt_digest"],
            "promotion_packet_digest": packet["packet_digest"],
            "promotion_decision_digest": promotion["decision_digest"],
            "persistent_witness_validated": True,
            "control_plane_witness_admitted": True,
            "ic10_review_recorded": True,
            "ledger_commit_authorized": True,
            "ledger_entry_committed": True,
            "promotion_authorized": promotion["promotion_authorized"],
            "promotion_executed": False,
            "promotion_claimed": False,
            **self._negative_boundaries(),
        }

    @staticmethod
    def _negative_boundaries() -> dict[str, Any]:
        return {
            "workflow_dispatched_by_runtime": False,
            "endpoint_contacted_by_runtime": False,
            "submitted_inputs_persisted_by_runtime": False,
            "runtime_mutated_ledger": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_executed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
        }

    def _hold(self, status: str, reason: str) -> dict[str, Any]:
        return {
            "status": status,
            "error": reason,
            "ledger_commit_authorized": False,
            "ledger_entry_committed": False,
            "promotion_authorized": False,
            **self._negative_boundaries(),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_ledger_commit_promotion_handoff(mcp: Any) -> None:
    """Register W21 tools and the frozen contract resource."""
    gate = FrozenLedgerCommitPromotionHandoff.load()

    @mcp.tool()
    def athena_w21_ledger_commit_promotion_status() -> str:
        """Return frozen W21 control, ledger, and authority coordinates."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w21_control_protocol_admission(
        control_receipt_json: str,
    ) -> str:
        """Verify exact W20 control observation without granting authority."""
        return _render(
            gate.inspect_control_protocol_admission(control_receipt_json)
        )

    @mcp.tool()
    def compile_athena_w21_ledger_commit_transaction(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
        review_packet_json: str,
        ic10_decision_json: str,
        control_protocol_receipt_json: str,
    ) -> str:
        """Compile an exact append-only transaction from a W20 closure."""
        return _render(
            gate.compile_ledger_commit_transaction(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
                control_admission_json,
                review_packet_json,
                ic10_decision_json,
                control_protocol_receipt_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w21_ledger_commit_authorization(
        transaction_json: str,
        authorization_json: str,
    ) -> str:
        """Verify a pinned ledger authority's signed authorization."""
        return _render(
            gate.inspect_commit_authorization(
                transaction_json, authorization_json
            )
        )

    @mcp.tool()
    def build_athena_w21_commit_occurrence_template(
        transaction_json: str,
        authorization_json: str,
    ) -> str:
        """Build the exact signed commit-occurrence return template."""
        return _render(
            gate.build_commit_occurrence_template(
                transaction_json, authorization_json
            )
        )

    @mcp.tool()
    def inspect_athena_w21_commit_occurrence(
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
    ) -> str:
        """Verify an external commit occurrence without mutating the ledger."""
        return _render(
            gate.inspect_commit_occurrence(
                transaction_json,
                authorization_json,
                commit_receipt_json,
            )
        )

    @mcp.tool()
    def build_athena_w21_promotion_handoff(
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
        target_environment: str,
        target_ref: str,
    ) -> str:
        """Build a promotion handoff after a verified ledger commit."""
        return _render(
            gate.build_promotion_handoff(
                transaction_json,
                authorization_json,
                commit_receipt_json,
                target_environment,
                target_ref,
            )
        )

    @mcp.tool()
    def inspect_athena_w21_promotion_authority_decision(
        promotion_packet_json: str,
        promotion_decision_json: str,
    ) -> str:
        """Verify a separate authority decision without executing promotion."""
        return _render(
            gate.inspect_promotion_decision(
                promotion_packet_json, promotion_decision_json
            )
        )

    @mcp.tool()
    def evaluate_athena_w21_commit_promotion_closure(
        transaction_json: str,
        authorization_json: str,
        commit_receipt_json: str,
        promotion_packet_json: str,
        promotion_decision_json: str,
    ) -> str:
        """Evaluate commit plus promotion-decision closure, never execution."""
        return _render(
            gate.evaluate_closure(
                transaction_json,
                authorization_json,
                commit_receipt_json,
                promotion_packet_json,
                promotion_decision_json,
            )
        )

    @mcp.resource("athena://w21-ledger-commit-promotion-handoff")
    def ledger_commit_promotion_handoff_resource() -> str:
        """Read the frozen W21 contract and production-empty registries."""
        return _render(gate.snapshot)
