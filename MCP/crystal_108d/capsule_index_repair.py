"""Typed W16 replay ledger, capsule-index repair, and authority ingress bridge.

W16 composes the reconciled W15 runtime with the alternate opaque-ID replay
implementation. It preserves every measurement as a distinct event. A repaired
external capsule index can reconstruct an exact packet, but never becomes an
uncued-memory, provider-read, authority, endpoint, deployment, or promotion claim.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from crystal_108d.capsule_replay_ingress import FrozenCapsuleReplayIngress
from crystal_108d.memory_digest_capsules import FrozenMemoryDigestCapsules


DATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "w16_replay_ledger.json"
)
SCHEMA = "athena.replay-ledger-capsule-index/v1"
PHASE = "KC144.XNAV.W16"


class CapsuleIndexRepairError(RuntimeError):
    """Raised when the W16 replay ledger or repaired index is inconsistent."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapsuleIndexRepairError("W16 replay ledger must be a JSON object")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _ledger_material(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": snapshot["schema"],
        "phase": snapshot["phase"],
        "capsule_set_digest": snapshot["capsule_set_digest"],
        "capsule_index": snapshot["capsule_index"],
        "replay_ledger": snapshot["replay_ledger"],
    }


def _ledger_digest(snapshot: dict[str, Any]) -> str:
    return "sha256:" + sha256(_canonical_bytes(_ledger_material(snapshot))).hexdigest()


class FrozenReplayLedger:
    """Validated replay events and exact, non-fuzzy capsule index."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        capsules: FrozenMemoryDigestCapsules,
        replay: FrozenCapsuleReplayIngress,
        index: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.capsules = capsules
        self.replay = replay
        self.index = index

    @classmethod
    def load(cls, path: Path = DATA_PATH) -> "FrozenReplayLedger":
        snapshot = _load_json(path)
        if snapshot.get("schema") != SCHEMA:
            raise CapsuleIndexRepairError(
                f"unexpected W16 schema: {snapshot.get('schema')!r}"
            )
        if snapshot.get("phase") != PHASE:
            raise CapsuleIndexRepairError(
                f"unexpected W16 phase: {snapshot.get('phase')!r}"
            )

        capsules = FrozenMemoryDigestCapsules.load()
        replay = FrozenCapsuleReplayIngress.load()
        if snapshot.get("capsule_set_digest") != capsules.snapshot.get(
            "capsule_set_digest"
        ):
            raise CapsuleIndexRepairError(
                "W16 must pin the exact W14 capsule-set root"
            )

        entries = snapshot.get("capsule_index")
        if not isinstance(entries, list) or len(entries) != 2:
            raise CapsuleIndexRepairError("W16 requires exactly two index entries")

        index: dict[str, dict[str, Any]] = {}
        indexed_capsules: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise CapsuleIndexRepairError("capsule index entries must be objects")
            required = {
                "capsule_id",
                "packet_digest",
                "station",
                "rid",
                "aid",
                "file_id",
                "revision_id",
                "tab_id",
                "half_open_range",
                "literal_sha256",
            }
            if set(entry) != required:
                raise CapsuleIndexRepairError("capsule index fields must be exact")

            capsule_id = entry["capsule_id"]
            replayed = replay.replay(capsule_id)
            if replayed.get("status") != "PASS_OPAQUE_CAPSULE_BLIND_REPLAY":
                raise CapsuleIndexRepairError(
                    f"index references unverified replay: {capsule_id}"
                )
            packet = replayed["packet"]
            source = packet["source"]
            expected = {
                "packet_digest": replayed["packet_digest"],
                "station": packet["station"],
                "rid": packet["rid"],
                "aid": packet["aid"],
                "file_id": source["file_id"],
                "revision_id": source["revision_id"],
                "tab_id": source["tab_id"],
                "half_open_range": [
                    source["range"]["start"],
                    source["range"]["end"],
                ],
                "literal_sha256": source["literal_sha256"],
            }
            for field, value in expected.items():
                if entry.get(field) != value:
                    raise CapsuleIndexRepairError(
                        f"{entry.get('station', capsule_id)}: {field} mismatch"
                    )
            if capsule_id in indexed_capsules:
                raise CapsuleIndexRepairError("duplicate capsule index entry")
            indexed_capsules.add(capsule_id)

            for identifier in (
                capsule_id,
                entry["station"],
                entry["rid"],
                entry["aid"],
            ):
                if identifier in index:
                    raise CapsuleIndexRepairError(
                        f"duplicate exact index identifier: {identifier}"
                    )
                index[identifier] = entry

        if indexed_capsules != set(replay.challenges_by_capsule):
            raise CapsuleIndexRepairError(
                "W16 index and W15 replay challenge set must be identical"
            )

        events = snapshot.get("replay_ledger")
        if not isinstance(events, list) or len(events) != 3:
            raise CapsuleIndexRepairError("W16 requires three typed replay events")
        by_event = {
            event.get("event_id"): event
            for event in events
            if isinstance(event, dict)
        }
        historical = by_event.get("W14-HISTORICAL-MEASUREMENT", {})
        uncued = by_event.get("W15-UNCUED-CONTEXT-REPLAY", {})
        opaque = by_event.get("W15-OPAQUE-CAPSULE-REPLAY", {})
        if (
            historical.get("conversation_memory_exact_fields") != 10
            or historical.get("persisted_file_memory_exact_fields") != 12
            or historical.get("external_capsule_exact_fields") != 14
            or historical.get("rewritten") is not False
        ):
            raise CapsuleIndexRepairError("historical W14 measurement was altered")
        if (
            uncued.get("conversation_memory_exact_fields") != 0
            or uncued.get("persisted_file_memory_exact_fields") != 10
            or uncued.get("external_capsule_exact_fields") != 14
            or uncued.get("verdict")
            != "HOLD_UNCUED_FULL_PACKET_NOT_RECOVERED"
            or uncued.get("rewritten") is not False
        ):
            raise CapsuleIndexRepairError("W15 uncued measurement was altered")
        if (
            opaque.get("input_fields") != ["capsule_id"]
            or opaque.get("challenge_count") != 2
            or opaque.get("passed") != 2
            or opaque.get("failed") != 0
            or opaque.get("exact_external_packet_fields") != 14
            or opaque.get("internal_recall_claimed") is not False
            or opaque.get("live_provider_read") is not False
        ):
            raise CapsuleIndexRepairError("opaque replay event is not exact")

        if snapshot.get("ledger_digest") != _ledger_digest(snapshot):
            raise CapsuleIndexRepairError("W16 replay-ledger digest mismatch")

        repair = snapshot.get("index_repair", {})
        if repair.get("missing_fields_observed_in_w15_persisted_file_replay") != [
            "F07.rid",
            "F07.tab_id",
            "M09.rid",
            "M09.tab_id",
        ]:
            raise CapsuleIndexRepairError("W16 repair target fields changed")
        if (
            repair.get("exact_fields_reconstructed_total") != 14
            or repair.get("conversation_memory_measurement_rewritten") is not False
            or repair.get("persisted_file_memory_measurement_rewritten") is not False
            or repair.get("repair_is_internal_recall") is not False
            or repair.get("repair_is_live_provider_read") is not False
        ):
            raise CapsuleIndexRepairError("W16 index repair overclaims memory")

        ingress = snapshot.get("authority_ingress", {})
        if (
            ingress.get("canonical_activation_head")
            != "8bc9072fe2fa9ac9b2998653c7656ae92428be4c"
            or ingress.get("protected_secret_name") != "ATHENA_MCP_BEARER_TOKEN"
            or ingress.get("authority_inputs_unresolved") != 13
            or ingress.get("structural_packet_inspection_ready") is not True
        ):
            raise CapsuleIndexRepairError("W16 authority ingress binding mismatch")
        for name in (
            "external_authority_verified",
            "provider_evidence_fetched",
            "secret_value_accepted",
            "secret_material_recorded",
            "endpoint_contacted",
            "dispatch_allowed",
            "persistent_witness_executed",
            "runtime_can_promote",
        ):
            if ingress.get(name) is not False:
                raise CapsuleIndexRepairError(
                    f"W16 authority boundary requires {name}=false"
                )

        for name, value in snapshot.get("boundaries", {}).items():
            if value is not False:
                raise CapsuleIndexRepairError(
                    f"W16 boundary {name} must remain false"
                )

        return cls(snapshot=snapshot, capsules=capsules, replay=replay, index=index)

    def status(self) -> dict[str, Any]:
        return {
            "status": (
                "PASS_CAPSULE_INDEX_REPAIRED_REPLAY_LANES_TYPED_"
                "AUTHORITY_UNVERIFIED"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "ledger_digest": self.snapshot["ledger_digest"],
            "capsule_set_digest": self.snapshot["capsule_set_digest"],
            "index_entries": len(self.snapshot["capsule_index"]),
            "exact_index_identifiers": len(self.index),
            "events": deepcopy(self.snapshot["replay_ledger"]),
            "index_repair": deepcopy(self.snapshot["index_repair"]),
            "authority_ingress": deepcopy(self.snapshot["authority_ingress"]),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "successors": deepcopy(self.snapshot["successors"]),
        }

    def resolve(self, identifier: str) -> dict[str, Any]:
        entry = self.index.get(identifier)
        if entry is None:
            return {
                "status": "INVALID_W16_CAPSULE_INDEX_ADDRESS",
                "identifier": identifier,
                "accepted_coordinate_classes": [
                    "capsule_id",
                    "station",
                    "RID",
                    "AID",
                ],
                "fuzzy_substitution_used": False,
            }
        replayed = self.replay.replay(entry["capsule_id"])
        return {
            "status": "PASS_W16_EXTERNAL_CAPSULE_INDEX_REPAIR",
            "identifier": identifier,
            "index_entry": deepcopy(entry),
            "packet": deepcopy(replayed["packet"]),
            "packet_digest": replayed["packet_digest"],
            "exact_packet_reconstructed": replayed[
                "exact_packet_reconstructed"
            ],
            "repair_source": self.snapshot["index_repair"]["repair_source"],
            "conversation_memory_measurement_rewritten": False,
            "persisted_file_memory_measurement_rewritten": False,
            "internal_recall_claimed": False,
            "live_provider_read": False,
        }

    def authority_status(self) -> dict[str, Any]:
        live = self.replay.authority_ingress_status()
        return {
            "status": "READY_STRUCTURAL_INGRESS_AUTHORITY_UNVERIFIED",
            "canonical_activation_head": self.snapshot["authority_ingress"][
                "canonical_activation_head"
            ],
            "protected_environment": self.snapshot["authority_ingress"][
                "protected_environment"
            ],
            "protected_secret_name": self.snapshot["authority_ingress"][
                "protected_secret_name"
            ],
            "authority_inputs_unresolved": self.snapshot["authority_ingress"][
                "authority_inputs_unresolved"
            ],
            "w15_ingress_status": live["status"],
            "packet_storage": live["packet_storage"],
            "network_capability": live["network_capability"],
            "dispatch_capability": live["dispatch_capability"],
            "external_authority_verified": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "runtime_can_promote": False,
            "next_required_event": (
                "Supply independently verifiable provider and authorization "
                "evidence to the protected P10 workflow; this surface does not "
                "invent authority, accept secrets, contact endpoints, or dispatch."
            ),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_capsule_index_repair(mcp: Any) -> None:
    """Register W16 typed replay-ledger and capsule-index surfaces."""

    registry = FrozenReplayLedger.load()

    @mcp.tool()
    def athena_w16_replay_ledger_status() -> str:
        """Expose typed replay events without collapsing evidence channels."""
        return _render(registry.status())

    @mcp.tool()
    def resolve_athena_w16_capsule_index(identifier: str) -> str:
        """Resolve an exact W16 capsule index key; fuzzy substitution is forbidden."""
        return _render(registry.resolve(identifier))

    @mcp.tool()
    def athena_w16_authorized_witness_ingress_status() -> str:
        """Expose the structural ingress and its still-external authority gate."""
        return _render(registry.authority_status())

    @mcp.resource("athena://w16-replay-ledger")
    def w16_replay_ledger_resource() -> str:
        """Expose the W16 replay ledger, repaired index, and authority boundary."""
        return _render(registry.status())
