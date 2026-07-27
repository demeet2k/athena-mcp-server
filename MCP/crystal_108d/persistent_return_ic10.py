"""KC144 W20 persistent-return ledger and IC10 review gate.

W20 composes the W19 control-signed execution path with the actual P10
three-sample witness receipt.  A control authority must attest a
content-addressed external persistence object before an append-only ledger
entry can be compiled.  A separately pinned IC10 reviewer must then sign a
nonpromotional review decision.

The production control and reviewer registries are intentionally empty and
the production ledger contains no entries.  This runtime validates and
compiles records; it cannot mutate the ledger, fetch external persistence,
dispatch a workflow, contact an endpoint, or promote.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from .provider_admission_execution import (
    FrozenProviderAdmissionExecutionGate,
    _addressed_material,
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
    _https_url,
    _parsed_timestamp,
    _timestamp,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w20_persistent_return_ic10.json"
SCHEMA = "athena.xnav-w20-persistent-return-ic10-gate/v1"
PHASE = "KC144.XNAV.W20"
W19_HEAD = "7863692262529d7e1effbd73eb8abfc3126ac484"
W19_TREE = "0d816c975ba23f608a7c75b8f53a78e9ff7a82f2"
W19_CONTRACT_DIGEST = (
    "sha256:92d5fc0d5bb3d7068dc167b5fdef57e"
    "1803015d6dd9eba2e6604e0449fd7f309"
)
W19_RECEIPT_ID = (
    "w19-admission-execution:sha256:"
    "32eeaf64585085658d1e71faf0e204b4aa7910f781d3cfddf240fbc9c1f1f9b0"
)
P10_WITNESS_SCHEMA = "athena.persistent-mcp-witness/v2"
CONTROL_ADMISSION_SCHEMA = "athena.persistent-witness-control-admission/v1"
LEDGER_SCHEMA = "athena.persistent-witness-return-ledger/v1"
LEDGER_ENTRY_SCHEMA = "athena.persistent-witness-return-ledger-entry/v1"
IC10_REGISTRY_SCHEMA = "athena.ic10-reviewer-registry/v1"
IC10_PACKET_SCHEMA = "athena.ic10-review-packet/v1"
IC10_DECISION_SCHEMA = "athena.ic10-nonpromotional-review/v1"

SHA256_VALUE = re.compile(r"^sha256:[0-9a-f]{64}$")
COMMIT_VALUE = re.compile(r"^[0-9a-f]{40}$")

WITNESS_FIELDS = {
    "receipt_id",
    "schema",
    "phase",
    "seed",
    "verdict",
    "observed_at",
    "target",
    "provider_evidence",
    "deployment",
    "authentication",
    "observation_window",
    "secret_recorded",
    "persistent_deployment_claimed",
    "promotion_ready",
    "promotion_claimed",
    "merge_claimed",
    "authority",
    "rollback",
    "next_gate",
    "successor_seed",
}
TARGET_FIELDS = {
    "target_id",
    "target_digest",
    "endpoint",
    "persistence_class",
    "authorization_ref",
}
DEPLOYMENT_FIELDS = {
    "image",
    "image_selection_attestation",
    "source_commit",
    "source_commit_attestation",
    "transport",
    "authentication",
    "persistent_endpoint",
}
AUTHENTICATION_FIELDS = {
    "class",
    "token_present",
    "token_recorded",
    "secret_store_ref",
}
WINDOW_FIELDS = {
    "sample_count",
    "interval_seconds",
    "minimum_elapsed_seconds",
    "samples",
}
SAMPLE_FIELDS = {
    "observed_at",
    "checks",
    "catalog",
    "answer_provenance",
    "workflow_run",
}
CATALOG_FIELDS = {
    "tools_count",
    "resources_count",
    "required_tools",
    "required_resources",
    "required_tools_present",
    "required_resources_present",
    "tool_inventory_digest",
    "resource_inventory_digest",
}
WITNESS_AUTHORITY_FIELDS = {
    "persistent_endpoint_witnessed",
    "runtime_can_promote",
    "ic10_required",
}
ROLLBACK_FIELDS = {"class", "action"}
REQUIRED_SAMPLE_CHECKS = {
    "mcp_initialize",
    "real_network_contact",
    "host_commit_attested",
    "required_tools_present",
    "actual_tool_count_exact",
    "actual_tool_inventory_exact",
    "required_resources_present",
    "actual_resource_count_exact",
    "actual_resource_inventory_exact",
    "unauthenticated_rejected",
    "invalid_token_rejected",
    "redirects_absent",
    "https_not_downgraded",
    "frozen_graph_exact",
    "v2_identity_answered",
    "v2_route_answered",
    "reciprocal_return_answered",
    "explicit_v1_fallback_answered",
    "tool_resource_receipts_equal",
    "promotion_boundary",
}

CONTROL_ADMISSION_FIELDS = {
    "schema",
    "predecessor",
    "bindings",
    "persistence",
    "authorization",
    "signature",
    "admission_digest",
}
PREDECESSOR_FIELDS = {
    "w19_head",
    "w19_tree",
    "w19_contract_digest",
    "w19_receipt_id",
}
BINDING_FIELDS = {
    "execution_digest",
    "provider_admission_digest",
    "provider_return_digest",
    "persistent_witness_receipt_id",
    "persistent_witness_digest",
}
PERSISTENCE_FIELDS = {
    "persistence_class",
    "object_url",
    "object_digest",
    "object_size_bytes",
    "content_addressed",
    "immutable",
    "retained_until",
}
CONTROL_AUTHORIZATION_FIELDS = {
    "authority_id",
    "control_repository",
    "control_pull_request",
    "control_commit",
    "control_ref",
    "admitted_at",
}
LEDGER_ENTRY_FIELDS = {
    "schema",
    "sequence",
    "previous_entry_digest",
    "control_admission_digest",
    "persistent_witness_receipt_id",
    "persistent_witness_digest",
    "external_object_url",
    "external_object_digest",
    "control_authority_id",
    "recorded_at",
    "entry_digest",
}
IC10_PACKET_FIELDS = {
    "schema",
    "predecessor_head",
    "control_admission_digest",
    "ledger_entry_digest",
    "persistent_witness_receipt_id",
    "persistent_witness_digest",
    "review_constraints",
    "packet_digest",
}
IC10_CONSTRAINT_FIELDS = {
    "evidence_only",
    "runtime_can_promote",
    "promotion_authorized",
    "promotion_claimed",
    "merge_claimed",
    "ic10_signature_required",
}
IC10_DECISION_FIELDS = {
    "schema",
    "review_packet_digest",
    "reviewer_id",
    "decision",
    "reviewed_at",
    "reason_code",
    "promotion_authorized",
    "signature",
    "decision_digest",
}


class PersistentReturnIC10Error(RuntimeError):
    """Raised when the frozen W20 contract or ledger is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PersistentReturnIC10Error(f"{path.name} must contain an object")
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


def _receipt_body(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: deepcopy(nested)
        for key, nested in value.items()
        if key != "receipt_id"
    }


def _receipt_id(body: dict[str, Any]) -> str:
    import hashlib

    return (
        "persistent-window:sha256:"
        + hashlib.sha256(_canonical_bytes(body)).hexdigest()
    )


def _entry_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "entry_digest"))


def _packet_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "packet_digest"))


def _decision_digest(value: dict[str, Any]) -> str:
    return _digest(_addressed_material(value, "decision_digest"))


class FrozenPersistentReturnIC10Gate:
    """Frozen W20 persistence ledger and nonpromotional IC10 gate."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        w19_gate: FrozenProviderAdmissionExecutionGate,
        entries: list[dict[str, Any]],
        reviewers: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.w19_gate = w19_gate
        self.entries = entries
        self.reviewers = reviewers

    @classmethod
    def from_snapshot(
        cls,
        snapshot: dict[str, Any],
        w19_gate: FrozenProviderAdmissionExecutionGate | None = None,
    ) -> "FrozenPersistentReturnIC10Gate":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise PersistentReturnIC10Error("unexpected W20 schema or phase")
        w19_gate = w19_gate or FrozenProviderAdmissionExecutionGate.load()
        expected_predecessor = {
            "repository": "demeet2k/athena-mcp-server",
            "pull_request": 13,
            "branch": "agent/w15-reconcile-capsule-deep-hardening",
            "w19_head": W19_HEAD,
            "w19_tree": W19_TREE,
            "w19_contract_digest": W19_CONTRACT_DIGEST,
            "w19_receipt_id": W19_RECEIPT_ID,
            "w19_p07_run_id": 30256053622,
            "w19_p08_run_id": 30256053580,
            "w19_stdio_receipt_id": (
                "mcp-host:sha256:"
                "c4bc082a5579901c2582e35766697ab62b26330ca3c1a3692949dcf8f84c1615"
            ),
            "w19_candidate_receipt_id": (
                "p08-candidate:sha256:"
                "68844edb96722337497f422bf97d4725a73f40d7cc46d11c3716d01219c5c2bc"
            ),
        }
        if snapshot.get("predecessor") != expected_predecessor:
            raise PersistentReturnIC10Error("W20 predecessor lineage mismatch")

        expected_return = {
            "witness_schema": P10_WITNESS_SCHEMA,
            "control_admission_schema": CONTROL_ADMISSION_SCHEMA,
            "required_witness_verdict": "PASS_PERSISTENT_HTTPS_WITNESS",
            "sample_count": 3,
            "interval_seconds": 20,
            "minimum_span_seconds": 40,
            "exact_p09_tool_count": 174,
            "exact_p09_tool_inventory_digest": (
                "sha256:230b41262dd77cc7e73f1acb3afcbc8de67bb52e680f35abfebb3465620fc34c"
            ),
            "exact_p09_resource_count": 27,
            "exact_p09_resource_inventory_digest": (
                "sha256:6e74961966019708425aa26ed6bddb0c665cfffacb1ef7e44494f8861deb9eea"
            ),
            "control_signature_required": True,
            "content_addressed_external_persistence_required": True,
            "runtime_fetches_external_persistence": False,
            "runtime_persists_submitted_returns": False,
        }
        if snapshot.get("persistent_return_contract") != expected_return:
            raise PersistentReturnIC10Error("W20 return contract drift")

        ledger = _exact_object(
            snapshot.get("ledger_contract"),
            {
                "schema",
                "entry_schema",
                "append_only",
                "hash_chained",
                "runtime_can_mutate_ledger",
                "entries",
            },
            "ledger_contract",
        )
        if {
            key: ledger.get(key)
            for key in (
                "schema",
                "entry_schema",
                "append_only",
                "hash_chained",
                "runtime_can_mutate_ledger",
            )
        } != {
            "schema": LEDGER_SCHEMA,
            "entry_schema": LEDGER_ENTRY_SCHEMA,
            "append_only": True,
            "hash_chained": True,
            "runtime_can_mutate_ledger": False,
        }:
            raise PersistentReturnIC10Error("W20 ledger contract drift")
        raw_entries = ledger.get("entries")
        if not isinstance(raw_entries, list):
            raise PersistentReturnIC10Error("W20 ledger entries must be a list")
        entries: list[dict[str, Any]] = []
        previous: str | None = None
        for index, raw_entry in enumerate(raw_entries, start=1):
            entry = cls._normalize_ledger_entry(raw_entry)
            if entry["sequence"] != index:
                raise PersistentReturnIC10Error(
                    "W20 ledger sequence is not contiguous"
                )
            if entry["previous_entry_digest"] != previous:
                raise PersistentReturnIC10Error("W20 ledger chain is broken")
            entries.append(entry)
            previous = entry["entry_digest"]

        registry = _exact_object(
            snapshot.get("ic10_registry"),
            {
                "schema",
                "canonicalization",
                "signature_algorithm",
                "signature_encoding",
                "reviewers",
            },
            "ic10_registry",
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
            "schema": IC10_REGISTRY_SCHEMA,
            "canonicalization": "KC144.CANON.JSON.V1",
            "signature_algorithm": "ed25519",
            "signature_encoding": "base64",
        }:
            raise PersistentReturnIC10Error("W20 IC10 registry drift")
        raw_reviewers = registry.get("reviewers")
        if not isinstance(raw_reviewers, list):
            raise PersistentReturnIC10Error("W20 reviewers must be a list")
        reviewers: dict[str, dict[str, Any]] = {}
        for raw_reviewer in raw_reviewers:
            reviewer = _normalize_authority(raw_reviewer)
            reviewer_id = reviewer["authority_id"]
            if reviewer_id in reviewers:
                raise PersistentReturnIC10Error("duplicate IC10 reviewer")
            reviewers[reviewer_id] = reviewer

        expected_ic10 = {
            "review_packet_schema": IC10_PACKET_SCHEMA,
            "review_decision_schema": IC10_DECISION_SCHEMA,
            "allowed_decisions": [
                "ADMIT_WITNESS_EVIDENCE",
                "REJECT_WITNESS_EVIDENCE",
            ],
            "separate_reviewer_signature_required": True,
            "self_supplied_reviewer_keys_allowed": False,
            "runtime_can_mutate_reviewer_registry": False,
            "runtime_can_promote": False,
            "promotion_authorized_must_be_false": True,
        }
        if snapshot.get("ic10_contract") != expected_ic10:
            raise PersistentReturnIC10Error("W20 IC10 contract drift")

        expected_boundaries = {
            "production_control_authority_pinned": bool(w19_gate.authorities),
            "production_ic10_reviewer_pinned": bool(reviewers),
            "provider_adapter_control_admitted": False,
            "provider_return_signature_verified": False,
            "execution_authorization_verified": False,
            "persistent_witness_validated": False,
            "external_persistence_attestation_verified": False,
            "control_plane_witness_admitted": False,
            "ledger_entry_committed": bool(entries),
            "ic10_review_recorded": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
        }
        if snapshot.get("boundaries") != expected_boundaries:
            raise PersistentReturnIC10Error("W20 boundary state drift")
        if snapshot.get("successor") != (
            "KC144.XNAV.W21::COMMIT-ADMITTED-WITNESS-LEDGER-ENTRY-"
            "AND-PROMOTION-AUTHORITY-HANDOFF"
        ):
            raise PersistentReturnIC10Error("W20 successor drift")
        material = {
            key: deepcopy(value)
            for key, value in snapshot.items()
            if key != "contract_digest"
        }
        if snapshot.get("contract_digest") != _digest(material):
            raise PersistentReturnIC10Error("W20 contract digest mismatch")
        return cls(snapshot, w19_gate, entries, reviewers)

    @classmethod
    def load(
        cls,
        path: Path = DATA_PATH,
    ) -> "FrozenPersistentReturnIC10Gate":
        return cls.from_snapshot(_load_json(path))

    @staticmethod
    def _normalize_ledger_entry(value: Any) -> dict[str, Any]:
        entry = _exact_object(value, LEDGER_ENTRY_FIELDS, "ledger entry")
        sequence = _positive_int(entry.get("sequence"), "ledger.sequence")
        previous = entry.get("previous_entry_digest")
        if previous is not None:
            previous = _sha(previous, "ledger.previous_entry_digest")
        normalized = {
            "schema": _bounded_text(entry.get("schema"), "ledger.schema"),
            "sequence": sequence,
            "previous_entry_digest": previous,
            "control_admission_digest": _sha(
                entry.get("control_admission_digest"),
                "ledger.control_admission_digest",
            ),
            "persistent_witness_receipt_id": _bounded_text(
                entry.get("persistent_witness_receipt_id"),
                "ledger.persistent_witness_receipt_id",
            ),
            "persistent_witness_digest": _sha(
                entry.get("persistent_witness_digest"),
                "ledger.persistent_witness_digest",
            ),
            "external_object_url": _https_url(
                entry.get("external_object_url"),
                "ledger.external_object_url",
            ),
            "external_object_digest": _sha(
                entry.get("external_object_digest"),
                "ledger.external_object_digest",
            ),
            "control_authority_id": _bounded_text(
                entry.get("control_authority_id"),
                "ledger.control_authority_id",
            ),
            "recorded_at": _timestamp(
                entry.get("recorded_at"), "ledger.recorded_at"
            ),
            "entry_digest": _sha(
                entry.get("entry_digest"), "ledger.entry_digest"
            ),
        }
        if normalized["schema"] != LEDGER_ENTRY_SCHEMA:
            raise ValueError("ledger entry schema mismatch")
        if normalized["entry_digest"] != _entry_digest(normalized):
            raise ValueError("ledger entry digest mismatch")
        return normalized

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "W20_PERSISTENT_RETURN_AND_IC10_GATE_READY__"
                "EXTERNAL_AUTHORITY_AND_LIVE_WITNESS_OPEN"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "contract_digest": self.snapshot["contract_digest"],
            "w19_head": W19_HEAD,
            "w19_tree": W19_TREE,
            "production_control_authority_count": len(
                self.w19_gate.authorities
            ),
            "production_ic10_reviewer_count": len(self.reviewers),
            "ledger_entry_count": len(self.entries),
            "ledger_root": _digest(self.entries),
            "runtime_can_mutate_ledger": False,
            "runtime_can_promote": False,
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "cross_navigation_state": (
                "W20_PERSISTENT_RETURN_CONTROL_ADMISSION_AND_IC10_"
                "REVIEW_PROTOCOL_READY__PRODUCTION_EVIDENCE_OPEN"
            ),
            "successor": self.snapshot["successor"],
        }

    def _normalize_witness(
        self,
        witness_json: str,
        activation_packet_json: str,
        provider_evidence_json: str,
    ) -> dict[str, Any]:
        if not isinstance(witness_json, str) or len(witness_json) > 262144:
            raise ValueError("persistent witness must be bounded JSON")
        witness = json.loads(witness_json)
        _assert_secret_free(witness, "persistent_witness")
        value = _exact_object(witness, WITNESS_FIELDS, "persistent witness")
        if (
            value.get("schema") != P10_WITNESS_SCHEMA
            or value.get("phase") != "P10"
            or value.get("verdict") != "PASS_PERSISTENT_HTTPS_WITNESS"
        ):
            raise ValueError("persistent witness schema, phase, or verdict mismatch")
        packet = json.loads(activation_packet_json)
        evidence = json.loads(provider_evidence_json)
        if not isinstance(packet, dict) or not isinstance(evidence, dict):
            raise ValueError("packet and evidence must be objects")
        if value.get("provider_evidence") != evidence:
            raise ValueError("persistent witness provider evidence mismatch")

        target = _exact_object(
            value.get("target"), TARGET_FIELDS, "witness.target"
        )
        expected_target = {
            "target_id": packet["target"]["id"],
            "endpoint": packet["target"]["endpoint"],
            "persistence_class": packet["target"]["persistence_class"],
            "authorization_ref": packet["authorization"]["ref"],
        }
        for field, expected in expected_target.items():
            if target.get(field) != expected:
                raise ValueError(f"persistent witness target {field} mismatch")
        target_digest = _sha(
            target.get("target_digest"), "witness.target.target_digest"
        )
        endpoint = _https_url(
            target.get("endpoint"),
            "witness.target.endpoint",
            exact_mcp=True,
        )

        deployment = _exact_object(
            value.get("deployment"),
            DEPLOYMENT_FIELDS,
            "witness.deployment",
        )
        expected_deployment = {
            "image": packet["image"],
            "image_selection_attestation": "authorized-target-contract",
            "source_commit": packet["source_commit"],
            "source_commit_attestation": "host-health-build-locked-file",
            "transport": "streamable-http",
            "authentication": "bearer-present-value-not-recorded",
            "persistent_endpoint": True,
        }
        if deployment != expected_deployment:
            raise ValueError("persistent witness deployment mismatch")

        authentication = _exact_object(
            value.get("authentication"),
            AUTHENTICATION_FIELDS,
            "witness.authentication",
        )
        expected_authentication = {
            "class": "bearer",
            "token_present": True,
            "token_recorded": False,
            "secret_store_ref": evidence["secret_store_ref"],
        }
        if authentication != expected_authentication:
            raise ValueError("persistent witness authentication mismatch")

        window = _exact_object(
            value.get("observation_window"),
            WINDOW_FIELDS,
            "witness.observation_window",
        )
        if (
            window.get("sample_count") != 3
            or window.get("interval_seconds") != 20
        ):
            raise ValueError("persistent witness plan mismatch")
        elapsed = window.get("minimum_elapsed_seconds")
        if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool):
            raise ValueError("persistent witness elapsed time must be numeric")
        if elapsed < 40:
            raise ValueError("persistent witness span is shorter than 40 seconds")
        samples = window.get("samples")
        if not isinstance(samples, list) or len(samples) != 3:
            raise ValueError("persistent witness must contain exactly 3 samples")

        contract = self.snapshot["persistent_return_contract"]
        normalized_samples: list[dict[str, Any]] = []
        observed_times = []
        workflow_run: str | None = None
        for index, raw_sample in enumerate(samples, start=1):
            sample = _exact_object(
                raw_sample,
                SAMPLE_FIELDS,
                f"witness.samples[{index - 1}]",
            )
            checks = sample.get("checks")
            if not isinstance(checks, dict):
                raise ValueError("persistent witness sample checks missing")
            if (
                not REQUIRED_SAMPLE_CHECKS.issubset(checks)
                or any(checks.get(name) is not True for name in REQUIRED_SAMPLE_CHECKS)
            ):
                raise ValueError("persistent witness sample check failed")
            catalog = _exact_object(
                sample.get("catalog"),
                CATALOG_FIELDS,
                f"witness.samples[{index - 1}].catalog",
            )
            expected_catalog = {
                "tools_count": contract["exact_p09_tool_count"],
                "resources_count": contract["exact_p09_resource_count"],
                "tool_inventory_digest": contract[
                    "exact_p09_tool_inventory_digest"
                ],
                "resource_inventory_digest": contract[
                    "exact_p09_resource_inventory_digest"
                ],
                "required_tools_present": True,
                "required_resources_present": True,
            }
            for field, expected in expected_catalog.items():
                if catalog.get(field) != expected:
                    raise ValueError(
                        f"persistent witness sample catalog {field} mismatch"
                    )
            current_run = _https_url(
                sample.get("workflow_run"),
                f"witness.samples[{index - 1}].workflow_run",
            )
            if workflow_run is None:
                workflow_run = current_run
            elif workflow_run != current_run:
                raise ValueError("persistent witness workflow run changed")
            observed_at = _timestamp(
                sample.get("observed_at"),
                f"witness.samples[{index - 1}].observed_at",
            )
            observed_times.append(_parsed_timestamp(observed_at))
            normalized_samples.append(
                {
                    "observed_at": observed_at,
                    "checks": deepcopy(checks),
                    "catalog": deepcopy(catalog),
                    "answer_provenance": deepcopy(
                        sample.get("answer_provenance")
                    ),
                    "workflow_run": current_run,
                }
            )
        gaps = [
            (later - earlier).total_seconds()
            for earlier, later in zip(observed_times, observed_times[1:])
        ]
        if any(gap < 20 for gap in gaps):
            raise ValueError("persistent witness sample interval is too short")
        observed_span = (
            observed_times[-1] - observed_times[0]
        ).total_seconds()
        if observed_span < 40 or elapsed < observed_span:
            raise ValueError("persistent witness elapsed span is inconsistent")
        observed_at = _timestamp(
            value.get("observed_at"), "witness.observed_at"
        )
        if _parsed_timestamp(observed_at) < observed_times[-1]:
            raise ValueError("persistent witness receipt predates final sample")

        authority = _exact_object(
            value.get("authority"),
            WITNESS_AUTHORITY_FIELDS,
            "witness.authority",
        )
        if authority != {
            "persistent_endpoint_witnessed": True,
            "runtime_can_promote": False,
            "ic10_required": True,
        }:
            raise ValueError("persistent witness authority boundary mismatch")
        rollback = _exact_object(
            value.get("rollback"), ROLLBACK_FIELDS, "witness.rollback"
        )
        if rollback.get("class") != "immutable-digest-selection":
            raise ValueError("persistent witness rollback class mismatch")
        if (
            value.get("secret_recorded") is not False
            or value.get("persistent_deployment_claimed") is not True
            or value.get("promotion_ready") is not False
            or value.get("promotion_claimed") is not False
            or value.get("merge_claimed") is not False
        ):
            raise ValueError("persistent witness crosses authority boundary")

        normalized = {
            **deepcopy(value),
            "observed_at": observed_at,
            "target": {
                **deepcopy(target),
                "target_digest": target_digest,
                "endpoint": endpoint,
            },
            "observation_window": {
                "sample_count": 3,
                "interval_seconds": 20,
                "minimum_elapsed_seconds": elapsed,
                "samples": normalized_samples,
            },
        }
        expected_receipt_id = _receipt_id(_receipt_body(normalized))
        if normalized.get("receipt_id") != expected_receipt_id:
            raise ValueError("persistent witness receipt id mismatch")
        return normalized

    def inspect_persistent_witness(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
    ) -> dict[str, Any]:
        execution = self.w19_gate.evaluate_execution(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
        )
        if execution.get("status") != (
            "PASS_CONTROL_SIGNED_PROTECTED_EXECUTION_AUTHORIZATION__"
            "NOT_DISPATCHED"
        ):
            return {
                **execution,
                "persistent_witness_status": (
                    "HOLD_W19_EXECUTION_AUTHORIZATION_REJECTED"
                ),
                "persistent_witness_validated": False,
                "external_persistence_attestation_verified": False,
                "control_plane_witness_admitted": False,
                "ledger_entry_committed": False,
                "ic10_review_recorded": False,
                **self._negative_boundaries(),
            }
        try:
            witness = self._normalize_witness(
                persistent_witness_json,
                activation_packet_json,
                provider_evidence_json,
            )
            return {
                "status": (
                    "PASS_W19_AUTHORIZED_PERSISTENT_WITNESS__"
                    "CONTROL_PERSISTENCE_ADMISSION_OPEN"
                ),
                "persistent_witness_receipt_id": witness["receipt_id"],
                "persistent_witness_digest": _digest(witness),
                "execution_digest": execution["execution_digest"],
                "provider_admission_digest": execution[
                    "provider_admission_digest"
                ],
                "provider_return_digest": execution["provider_return_digest"],
                "control_authority_id": execution["control_authority_id"],
                "workflow_run": witness["observation_window"]["samples"][0][
                    "workflow_run"
                ],
                "persistent_witness_validated": True,
                "external_persistence_attestation_verified": False,
                "control_plane_witness_admitted": False,
                "ledger_entry_committed": False,
                "ic10_review_recorded": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def build_control_admission_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
    ) -> dict[str, Any]:
        inspected = self.inspect_persistent_witness(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
        )
        if not inspected.get("status", "").startswith(
            "PASS_W19_AUTHORIZED_PERSISTENT_WITNESS"
        ):
            return inspected
        template = {
            "schema": CONTROL_ADMISSION_SCHEMA,
            "predecessor": {
                "w19_head": W19_HEAD,
                "w19_tree": W19_TREE,
                "w19_contract_digest": W19_CONTRACT_DIGEST,
                "w19_receipt_id": W19_RECEIPT_ID,
            },
            "bindings": {
                "execution_digest": inspected["execution_digest"],
                "provider_admission_digest": inspected[
                    "provider_admission_digest"
                ],
                "provider_return_digest": inspected[
                    "provider_return_digest"
                ],
                "persistent_witness_receipt_id": inspected[
                    "persistent_witness_receipt_id"
                ],
                "persistent_witness_digest": inspected[
                    "persistent_witness_digest"
                ],
            },
            "persistence": {
                "persistence_class": "append-only-content-addressed-object",
                "object_url": None,
                "object_digest": None,
                "object_size_bytes": None,
                "content_addressed": True,
                "immutable": True,
                "retained_until": None,
            },
            "authorization": {
                "authority_id": inspected["control_authority_id"],
                "control_repository": "demeet2k/Athena",
                "control_pull_request": None,
                "control_commit": None,
                "control_ref": None,
                "admitted_at": None,
            },
            "signature": {
                "algorithm": "ed25519",
                "key_id": None,
                "value": None,
            },
            "admission_digest": None,
        }
        return {
            "status": "CONTROL_PERSISTENCE_ADMISSION_TEMPLATE_READY",
            "template": template,
            "persistent_witness_validated": True,
            "external_persistence_attestation_verified": False,
            "ledger_entry_committed": False,
            **self._negative_boundaries(),
        }

    def _normalize_control_admission(self, value: Any) -> dict[str, Any]:
        _assert_secret_free(value, "control_admission")
        admission = _exact_object(
            value, CONTROL_ADMISSION_FIELDS, "control admission"
        )
        predecessor = _exact_object(
            admission.get("predecessor"),
            PREDECESSOR_FIELDS,
            "control admission predecessor",
        )
        expected_predecessor = {
            "w19_head": W19_HEAD,
            "w19_tree": W19_TREE,
            "w19_contract_digest": W19_CONTRACT_DIGEST,
            "w19_receipt_id": W19_RECEIPT_ID,
        }
        if predecessor != expected_predecessor:
            raise ValueError("control admission predecessor mismatch")
        bindings = _exact_object(
            admission.get("bindings"), BINDING_FIELDS, "control bindings"
        )
        normalized_bindings = {
            "execution_digest": _sha(
                bindings.get("execution_digest"), "bindings.execution_digest"
            ),
            "provider_admission_digest": _sha(
                bindings.get("provider_admission_digest"),
                "bindings.provider_admission_digest",
            ),
            "provider_return_digest": _sha(
                bindings.get("provider_return_digest"),
                "bindings.provider_return_digest",
            ),
            "persistent_witness_receipt_id": _bounded_text(
                bindings.get("persistent_witness_receipt_id"),
                "bindings.persistent_witness_receipt_id",
            ),
            "persistent_witness_digest": _sha(
                bindings.get("persistent_witness_digest"),
                "bindings.persistent_witness_digest",
            ),
        }
        persistence = _exact_object(
            admission.get("persistence"),
            PERSISTENCE_FIELDS,
            "control persistence",
        )
        normalized_persistence = {
            "persistence_class": _bounded_text(
                persistence.get("persistence_class"),
                "persistence.persistence_class",
            ),
            "object_url": _https_url(
                persistence.get("object_url"), "persistence.object_url"
            ),
            "object_digest": _sha(
                persistence.get("object_digest"),
                "persistence.object_digest",
            ),
            "object_size_bytes": _positive_int(
                persistence.get("object_size_bytes"),
                "persistence.object_size_bytes",
            ),
            "content_addressed": persistence.get("content_addressed"),
            "immutable": persistence.get("immutable"),
            "retained_until": _timestamp(
                persistence.get("retained_until"),
                "persistence.retained_until",
            ),
        }
        if (
            normalized_persistence["persistence_class"]
            != "append-only-content-addressed-object"
            or normalized_persistence["content_addressed"] is not True
            or normalized_persistence["immutable"] is not True
        ):
            raise ValueError("control persistence class or assertions mismatch")
        digest_hex = normalized_persistence["object_digest"].removeprefix(
            "sha256:"
        )
        if digest_hex not in normalized_persistence["object_url"].lower():
            raise ValueError(
                "content-addressed object URL does not bind object digest"
            )
        authorization = _exact_object(
            admission.get("authorization"),
            CONTROL_AUTHORIZATION_FIELDS,
            "control authorization",
        )
        pull_request = authorization.get("control_pull_request")
        if (
            not isinstance(pull_request, int)
            or isinstance(pull_request, bool)
            or pull_request < 1
        ):
            raise ValueError("control pull request must be positive")
        normalized_authorization = {
            "authority_id": _bounded_text(
                authorization.get("authority_id"),
                "authorization.authority_id",
            ),
            "control_repository": _bounded_text(
                authorization.get("control_repository"),
                "authorization.control_repository",
            ),
            "control_pull_request": pull_request,
            "control_commit": _commit(
                authorization.get("control_commit"),
                "authorization.control_commit",
            ),
            "control_ref": _bounded_text(
                authorization.get("control_ref"),
                "authorization.control_ref",
            ),
            "admitted_at": _timestamp(
                authorization.get("admitted_at"),
                "authorization.admitted_at",
            ),
        }
        if normalized_authorization["control_repository"] != "demeet2k/Athena":
            raise ValueError("control admission repository mismatch")
        normalized = {
            "schema": _bounded_text(admission.get("schema"), "schema"),
            "predecessor": expected_predecessor,
            "bindings": normalized_bindings,
            "persistence": normalized_persistence,
            "authorization": normalized_authorization,
            "signature": _normalized_signature(
                admission.get("signature"), "signature"
            ),
            "admission_digest": _sha(
                admission.get("admission_digest"), "admission_digest"
            ),
        }
        if normalized["schema"] != CONTROL_ADMISSION_SCHEMA:
            raise ValueError("control admission schema mismatch")
        if normalized["admission_digest"] != _digest(
            _addressed_material(normalized, "admission_digest")
        ):
            raise ValueError("control admission digest mismatch")
        return normalized

    def inspect_control_admission(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> dict[str, Any]:
        witness = self.inspect_persistent_witness(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
        )
        if not witness.get("status", "").startswith(
            "PASS_W19_AUTHORIZED_PERSISTENT_WITNESS"
        ):
            return witness
        try:
            if (
                not isinstance(control_admission_json, str)
                or len(control_admission_json) > 65536
            ):
                raise ValueError("control admission must be bounded JSON")
            admission = self._normalize_control_admission(
                json.loads(control_admission_json)
            )
            expected_bindings = {
                field: witness[field]
                for field in BINDING_FIELDS
            }
            if admission["bindings"] != expected_bindings:
                raise ValueError("control admission witness binding mismatch")
            authorization = admission["authorization"]
            if authorization["authority_id"] != witness["control_authority_id"]:
                raise ValueError("control admission authority mismatch")
            authority = self.w19_gate.authorities.get(
                authorization["authority_id"]
            )
            if authority is None:
                return self._hold(
                    "HOLD_CONTROL_AUTHORITY_NOT_PINNED",
                    "control authority is not pinned in W19",
                )
            signature = admission["signature"]
            if signature["key_id"] != authority["key_id"]:
                raise ValueError("control admission signature key mismatch")
            admitted_at = _parsed_timestamp(authorization["admitted_at"])
            if not (
                _parsed_timestamp(authority["valid_from"])
                <= admitted_at
                <= _parsed_timestamp(authority["valid_until"])
            ):
                raise ValueError("control admission outside authority validity")
            retained_until = _parsed_timestamp(
                admission["persistence"]["retained_until"]
            )
            if retained_until <= admitted_at:
                raise ValueError("persistent object retention already expired")
            normalized_witness = self._normalize_witness(
                persistent_witness_json,
                activation_packet_json,
                provider_evidence_json,
            )
            if admitted_at < _parsed_timestamp(
                normalized_witness["observed_at"]
            ):
                raise ValueError("control admission predates witness completion")
            if not _verify_ed25519_signature(
                authority["public_key_base64"],
                signature["value"],
                _unsigned_material(admission, "admission_digest"),
            ):
                raise ValueError("control persistence admission signature invalid")
            return {
                "status": (
                    "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_RETURN__"
                    "LEDGER_COMMIT_AND_IC10_REVIEW_OPEN"
                ),
                "control_admission_digest": admission["admission_digest"],
                "persistent_witness_receipt_id": witness[
                    "persistent_witness_receipt_id"
                ],
                "persistent_witness_digest": witness[
                    "persistent_witness_digest"
                ],
                "external_object_url": admission["persistence"]["object_url"],
                "external_object_digest": admission["persistence"][
                    "object_digest"
                ],
                "control_authority_id": authority["authority_id"],
                "control_signature_verified": True,
                "persistent_witness_validated": True,
                "external_persistence_attestation_verified": True,
                "external_persistence_fetched_by_runtime": False,
                "control_plane_witness_admitted": True,
                "ledger_entry_committed": False,
                "ic10_review_recorded": False,
                "normalized_control_admission": admission,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def compile_ledger_entry(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> dict[str, Any]:
        admitted = self.inspect_control_admission(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
            control_admission_json,
        )
        if not admitted.get("status", "").startswith(
            "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_RETURN"
        ):
            return admitted
        previous = (
            self.entries[-1]["entry_digest"] if self.entries else None
        )
        entry = {
            "schema": LEDGER_ENTRY_SCHEMA,
            "sequence": len(self.entries) + 1,
            "previous_entry_digest": previous,
            "control_admission_digest": admitted[
                "control_admission_digest"
            ],
            "persistent_witness_receipt_id": admitted[
                "persistent_witness_receipt_id"
            ],
            "persistent_witness_digest": admitted[
                "persistent_witness_digest"
            ],
            "external_object_url": admitted["external_object_url"],
            "external_object_digest": admitted["external_object_digest"],
            "control_authority_id": admitted["control_authority_id"],
            "recorded_at": admitted["normalized_control_admission"][
                "authorization"
            ]["admitted_at"],
            "entry_digest": "",
        }
        entry["entry_digest"] = _entry_digest(entry)
        return {
            "status": "LEDGER_ENTRY_CANDIDATE_COMPILED__NOT_COMMITTED",
            "ledger_entry": entry,
            "ledger_root_before": _digest(self.entries),
            "ledger_root_after_candidate": _digest(self.entries + [entry]),
            "runtime_can_mutate_ledger": False,
            "ledger_entry_committed": False,
            "control_plane_witness_admitted": True,
            "ic10_review_recorded": False,
            **self._negative_boundaries(),
        }

    def compile_ic10_review_template(
        self,
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> dict[str, Any]:
        ledger = self.compile_ledger_entry(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
            control_admission_json,
        )
        if ledger.get("status") != (
            "LEDGER_ENTRY_CANDIDATE_COMPILED__NOT_COMMITTED"
        ):
            return ledger
        entry = ledger["ledger_entry"]
        packet = {
            "schema": IC10_PACKET_SCHEMA,
            "predecessor_head": W19_HEAD,
            "control_admission_digest": entry[
                "control_admission_digest"
            ],
            "ledger_entry_digest": entry["entry_digest"],
            "persistent_witness_receipt_id": entry[
                "persistent_witness_receipt_id"
            ],
            "persistent_witness_digest": entry[
                "persistent_witness_digest"
            ],
            "review_constraints": {
                "evidence_only": True,
                "runtime_can_promote": False,
                "promotion_authorized": False,
                "promotion_claimed": False,
                "merge_claimed": False,
                "ic10_signature_required": True,
            },
            "packet_digest": "",
        }
        packet["packet_digest"] = _packet_digest(packet)
        decision = {
            "schema": IC10_DECISION_SCHEMA,
            "review_packet_digest": packet["packet_digest"],
            "reviewer_id": None,
            "decision": None,
            "reviewed_at": None,
            "reason_code": None,
            "promotion_authorized": False,
            "signature": {
                "algorithm": "ed25519",
                "key_id": None,
                "value": None,
            },
            "decision_digest": None,
        }
        return {
            "status": "IC10_REVIEW_TEMPLATE_READY__REVIEW_NOT_RECORDED",
            "review_packet": packet,
            "decision_template": decision,
            "production_ic10_reviewer_count": len(self.reviewers),
            "ledger_entry_committed": False,
            "ic10_review_recorded": False,
            **self._negative_boundaries(),
        }

    def _normalize_review_packet(self, value: Any) -> dict[str, Any]:
        packet = _exact_object(
            value, IC10_PACKET_FIELDS, "IC10 review packet"
        )
        constraints = _exact_object(
            packet.get("review_constraints"),
            IC10_CONSTRAINT_FIELDS,
            "IC10 review constraints",
        )
        expected_constraints = {
            "evidence_only": True,
            "runtime_can_promote": False,
            "promotion_authorized": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_signature_required": True,
        }
        normalized = {
            "schema": _bounded_text(packet.get("schema"), "packet.schema"),
            "predecessor_head": _commit(
                packet.get("predecessor_head"),
                "packet.predecessor_head",
            ),
            "control_admission_digest": _sha(
                packet.get("control_admission_digest"),
                "packet.control_admission_digest",
            ),
            "ledger_entry_digest": _sha(
                packet.get("ledger_entry_digest"),
                "packet.ledger_entry_digest",
            ),
            "persistent_witness_receipt_id": _bounded_text(
                packet.get("persistent_witness_receipt_id"),
                "packet.persistent_witness_receipt_id",
            ),
            "persistent_witness_digest": _sha(
                packet.get("persistent_witness_digest"),
                "packet.persistent_witness_digest",
            ),
            "review_constraints": constraints,
            "packet_digest": _sha(
                packet.get("packet_digest"), "packet.packet_digest"
            ),
        }
        if (
            normalized["schema"] != IC10_PACKET_SCHEMA
            or normalized["predecessor_head"] != W19_HEAD
            or normalized["review_constraints"] != expected_constraints
        ):
            raise ValueError("IC10 packet contract mismatch")
        if normalized["packet_digest"] != _packet_digest(normalized):
            raise ValueError("IC10 packet digest mismatch")
        return normalized

    def _normalize_ic10_decision(self, value: Any) -> dict[str, Any]:
        decision = _exact_object(
            value, IC10_DECISION_FIELDS, "IC10 decision"
        )
        normalized = {
            "schema": _bounded_text(decision.get("schema"), "decision.schema"),
            "review_packet_digest": _sha(
                decision.get("review_packet_digest"),
                "decision.review_packet_digest",
            ),
            "reviewer_id": _bounded_text(
                decision.get("reviewer_id"), "decision.reviewer_id"
            ),
            "decision": _bounded_text(
                decision.get("decision"), "decision.decision"
            ),
            "reviewed_at": _timestamp(
                decision.get("reviewed_at"), "decision.reviewed_at"
            ),
            "reason_code": _bounded_text(
                decision.get("reason_code"), "decision.reason_code"
            ),
            "promotion_authorized": decision.get("promotion_authorized"),
            "signature": _normalized_signature(
                decision.get("signature"), "decision.signature"
            ),
            "decision_digest": _sha(
                decision.get("decision_digest"), "decision.decision_digest"
            ),
        }
        if normalized["schema"] != IC10_DECISION_SCHEMA:
            raise ValueError("IC10 decision schema mismatch")
        if normalized["decision"] not in self.snapshot["ic10_contract"][
            "allowed_decisions"
        ]:
            raise ValueError("IC10 decision is not allowed")
        if normalized["promotion_authorized"] is not False:
            raise ValueError("W20 IC10 decision cannot authorize promotion")
        if normalized["decision_digest"] != _decision_digest(normalized):
            raise ValueError("IC10 decision digest mismatch")
        return normalized

    def inspect_ic10_review(
        self,
        review_packet_json: str,
        ic10_decision_json: str,
    ) -> dict[str, Any]:
        try:
            if (
                not isinstance(review_packet_json, str)
                or len(review_packet_json) > 65536
                or not isinstance(ic10_decision_json, str)
                or len(ic10_decision_json) > 65536
            ):
                raise ValueError("IC10 records must be bounded JSON")
            packet = self._normalize_review_packet(
                json.loads(review_packet_json)
            )
            decision = self._normalize_ic10_decision(
                json.loads(ic10_decision_json)
            )
            if (
                decision["review_packet_digest"]
                != packet["packet_digest"]
            ):
                raise ValueError("IC10 decision packet binding mismatch")
            reviewer = self.reviewers.get(decision["reviewer_id"])
            if reviewer is None:
                return self._hold(
                    "HOLD_IC10_REVIEWER_NOT_PINNED",
                    "reviewer_id is not in the commit-pinned IC10 registry",
                )
            if decision["signature"]["key_id"] != reviewer["key_id"]:
                raise ValueError("IC10 signature key mismatch")
            reviewed_at = _parsed_timestamp(decision["reviewed_at"])
            if not (
                _parsed_timestamp(reviewer["valid_from"])
                <= reviewed_at
                <= _parsed_timestamp(reviewer["valid_until"])
            ):
                raise ValueError("IC10 review outside reviewer validity")
            if not _verify_ed25519_signature(
                reviewer["public_key_base64"],
                decision["signature"]["value"],
                _unsigned_material(decision, "decision_digest"),
            ):
                raise ValueError("IC10 Ed25519 signature invalid")
            accepted = decision["decision"] == "ADMIT_WITNESS_EVIDENCE"
            return {
                "status": (
                    "PASS_IC10_WITNESS_EVIDENCE_REVIEW_RECORDED__NOT_PROMOTED"
                    if accepted
                    else "PASS_IC10_WITNESS_EVIDENCE_REJECTION_RECORDED__NOT_PROMOTED"
                ),
                "review_packet_digest": packet["packet_digest"],
                "decision_digest": decision["decision_digest"],
                "reviewer_id": reviewer["authority_id"],
                "decision": decision["decision"],
                "ic10_signature_verified": True,
                "ic10_review_recorded": True,
                "witness_evidence_admitted_for_review": accepted,
                "promotion_authorized": False,
                "ledger_entry_committed": False,
                **self._negative_boundaries(),
            }
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            return self._rejected(str(error))

    def evaluate_closure(
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
    ) -> dict[str, Any]:
        ledger = self.compile_ledger_entry(
            activation_packet_json,
            provider_evidence_json,
            provenance_witness_json,
            provider_admission_json,
            provider_return_json,
            execution_authorization_json,
            persistent_witness_json,
            control_admission_json,
        )
        if ledger.get("status") != (
            "LEDGER_ENTRY_CANDIDATE_COMPILED__NOT_COMMITTED"
        ):
            return ledger
        review = self.inspect_ic10_review(
            review_packet_json, ic10_decision_json
        )
        if review.get("status") != (
            "PASS_IC10_WITNESS_EVIDENCE_REVIEW_RECORDED__NOT_PROMOTED"
        ):
            return {
                **review,
                "closure_status": "HOLD_IC10_EVIDENCE_ADMISSION_OPEN",
            }
        entry = ledger["ledger_entry"]
        packet = self._normalize_review_packet(
            json.loads(review_packet_json)
        )
        if (
            packet["control_admission_digest"]
            != entry["control_admission_digest"]
            or packet["ledger_entry_digest"] != entry["entry_digest"]
            or packet["persistent_witness_receipt_id"]
            != entry["persistent_witness_receipt_id"]
            or packet["persistent_witness_digest"]
            != entry["persistent_witness_digest"]
        ):
            return self._rejected(
                "IC10 packet does not bind the compiled ledger candidate"
            )
        return {
            "status": (
                "PASS_CONTROL_ADMITTED_PERSISTENT_WITNESS_AND_IC10_REVIEW__"
                "LEDGER_COMMIT_AND_PROMOTION_OPEN"
            ),
            "control_admission_digest": entry[
                "control_admission_digest"
            ],
            "ledger_entry_digest": entry["entry_digest"],
            "ledger_root_after_candidate": ledger[
                "ledger_root_after_candidate"
            ],
            "ic10_review_packet_digest": packet["packet_digest"],
            "ic10_decision_digest": review["decision_digest"],
            "persistent_witness_validated": True,
            "external_persistence_attestation_verified": True,
            "control_plane_witness_admitted": True,
            "ic10_review_recorded": True,
            "ledger_entry_committed": False,
            "promotion_authorized": False,
            **self._negative_boundaries(),
        }

    @staticmethod
    def _negative_boundaries() -> dict[str, Any]:
        return {
            "workflow_dispatched_by_runtime": False,
            "endpoint_contacted_by_runtime": False,
            "submitted_inputs_persisted_by_runtime": False,
            "external_persistence_fetched_by_runtime": False,
            "deployment_claimed": False,
            "merge_claimed": False,
            "promotion_claimed": False,
            "runtime_can_promote": False,
        }

    def _hold(self, status: str, reason: str) -> dict[str, Any]:
        return {
            "status": status,
            "error": reason,
            "persistent_witness_validated": False,
            "external_persistence_attestation_verified": False,
            "control_plane_witness_admitted": False,
            "ledger_entry_committed": False,
            "ic10_review_recorded": False,
            **self._negative_boundaries(),
        }

    def _rejected(self, reason: str) -> dict[str, Any]:
        return self._hold(
            "HOLD_W20_PERSISTENT_RETURN_OR_IC10_REJECTED", reason
        )


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_persistent_return_ic10(mcp: Any) -> None:
    """Register W20 tools and the frozen contract resource."""
    gate = FrozenPersistentReturnIC10Gate.load()

    @mcp.tool()
    def athena_w20_persistent_return_ic10_status() -> str:
        """Return the frozen W20 ledger and IC10 gate state."""
        return _render(gate.status())

    @mcp.tool()
    def inspect_athena_w20_persistent_witness(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
    ) -> str:
        """Validate a real P10 witness through the W19 authorization chain."""
        return _render(
            gate.inspect_persistent_witness(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
            )
        )

    @mcp.tool()
    def build_athena_w20_control_admission_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
    ) -> str:
        """Build the exact control persistence-admission template."""
        return _render(
            gate.build_control_admission_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w20_control_admission(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> str:
        """Verify the control-signed persistence admission."""
        return _render(
            gate.inspect_control_admission(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
                control_admission_json,
            )
        )

    @mcp.tool()
    def compile_athena_w20_ledger_entry(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> str:
        """Compile but do not commit an append-only ledger entry."""
        return _render(
            gate.compile_ledger_entry(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
                control_admission_json,
            )
        )

    @mcp.tool()
    def compile_athena_w20_ic10_review_template(
        activation_packet_json: str,
        provider_evidence_json: str,
        provenance_witness_json: str,
        provider_admission_json: str,
        provider_return_json: str,
        execution_authorization_json: str,
        persistent_witness_json: str,
        control_admission_json: str,
    ) -> str:
        """Compile the nonpromotional IC10 review packet and decision template."""
        return _render(
            gate.compile_ic10_review_template(
                activation_packet_json,
                provider_evidence_json,
                provenance_witness_json,
                provider_admission_json,
                provider_return_json,
                execution_authorization_json,
                persistent_witness_json,
                control_admission_json,
            )
        )

    @mcp.tool()
    def inspect_athena_w20_ic10_review(
        review_packet_json: str,
        ic10_decision_json: str,
    ) -> str:
        """Verify a separately signed IC10 evidence-review decision."""
        return _render(
            gate.inspect_ic10_review(
                review_packet_json, ic10_decision_json
            )
        )

    @mcp.tool()
    def evaluate_athena_w20_return_ic10_closure(
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
    ) -> str:
        """Evaluate control admission plus IC10 review without promotion."""
        return _render(
            gate.evaluate_closure(
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
        )

    @mcp.resource("athena://w20-persistent-return-ic10")
    def persistent_return_ic10_resource() -> str:
        """Read the frozen W20 contract and production-empty registries."""
        return _render(gate.snapshot)
