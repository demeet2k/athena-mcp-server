"""Content-addressed KC144 memory capsules and fail-closed endpoint link.

W13 measured incomplete cross-conversation reconstruction. This module closes the
missing digest coordinates from an explicit persisted capsule. It never labels
the capsule as hidden-weight or unassisted internal recall, performs no live
Google Drive request, accepts no bearer secret, and cannot dispatch an endpoint.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w14_memory_digest_capsules.json"
)
SCHEMA = "athena.memory-digest-capsules/v1"
PHASE = "KC144.XNAV.W14"
CAPSULE_PREFIX = "mcap:sha256:"


class MemoryDigestCapsuleError(RuntimeError):
    """Raised when a W14 capsule or endpoint link violates its contract."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise MemoryDigestCapsuleError("capsule snapshot must be a JSON object")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _literal_digest(literal: str) -> str:
    return sha256(literal.encode("utf-8")).hexdigest()


def _capsule_material(capsule: dict[str, Any]) -> dict[str, Any]:
    """Return the exact coordinate packet bound by capsule_id."""
    return {
        "station": capsule["station"],
        "rid": capsule["rid"],
        "aid": capsule["aid"],
        "source": deepcopy(capsule["source"]),
    }


def _capsule_id(capsule: dict[str, Any]) -> str:
    return CAPSULE_PREFIX + sha256(
        _canonical_bytes(_capsule_material(capsule))
    ).hexdigest()


def _capsule_set_digest(capsules: list[dict[str, Any]]) -> str:
    material = {
        "schema": SCHEMA,
        "phase": PHASE,
        "capsule_ids": sorted(capsule["capsule_id"] for capsule in capsules),
    }
    return "sha256:" + sha256(_canonical_bytes(material)).hexdigest()


class FrozenMemoryDigestCapsules:
    """Verified external-memory completion packets for exact XNAV routing."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        capsules: list[dict[str, Any]],
        index: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.capsules = capsules
        self.index = index

    @classmethod
    def load(cls, path: Path = DATA_PATH) -> "FrozenMemoryDigestCapsules":
        snapshot = _load_json(path)
        if snapshot.get("schema") != SCHEMA:
            raise MemoryDigestCapsuleError(
                f"unexpected capsule schema: {snapshot.get('schema')!r}"
            )
        if snapshot.get("phase") != PHASE:
            raise MemoryDigestCapsuleError(
                f"unexpected capsule phase: {snapshot.get('phase')!r}"
            )

        capsules = snapshot.get("capsules")
        if not isinstance(capsules, list) or len(capsules) != 2:
            raise MemoryDigestCapsuleError(
                "W14 requires exactly the witnessed F07 and M09 capsules"
            )

        index: dict[str, dict[str, Any]] = {}
        stations: set[str] = set()
        for capsule in capsules:
            if not isinstance(capsule, dict):
                raise MemoryDigestCapsuleError("each capsule must be an object")
            station = capsule.get("station")
            rid = capsule.get("rid")
            aid = capsule.get("aid")
            capsule_id = capsule.get("capsule_id")
            if not all(
                isinstance(value, str) and value
                for value in (station, rid, aid, capsule_id)
            ):
                raise MemoryDigestCapsuleError(
                    "capsule station, RID, AID, and capsule_id are required"
                )
            if station in stations:
                raise MemoryDigestCapsuleError(f"duplicate station: {station}")
            stations.add(station)

            source = capsule.get("source")
            if not isinstance(source, dict):
                raise MemoryDigestCapsuleError(f"{station}: source is required")
            literal = source.get("literal")
            literal_sha256 = source.get("literal_sha256")
            if not isinstance(literal, str) or not isinstance(
                literal_sha256, str
            ):
                raise MemoryDigestCapsuleError(
                    f"{station}: literal and full digest are required"
                )
            actual_literal_digest = _literal_digest(literal)
            if actual_literal_digest != literal_sha256:
                raise MemoryDigestCapsuleError(
                    f"{station}: literal digest mismatch"
                )

            coordinate_range = source.get("range")
            if (
                not isinstance(coordinate_range, dict)
                or coordinate_range.get("interval") != "half-open"
                or not isinstance(coordinate_range.get("start"), int)
                or not isinstance(coordinate_range.get("end"), int)
                or coordinate_range["start"] >= coordinate_range["end"]
            ):
                raise MemoryDigestCapsuleError(
                    f"{station}: invalid half-open range"
                )

            expected_capsule_id = _capsule_id(capsule)
            if capsule_id != expected_capsule_id:
                raise MemoryDigestCapsuleError(
                    f"{station}: capsule digest mismatch"
                )

            provenance = capsule.get("provenance", {})
            if (
                provenance.get("kind") != "external-persisted-memory"
                or provenance.get("internal_recall_claimed") is not False
                or provenance.get("live_provider_read_by_runtime") is not False
            ):
                raise MemoryDigestCapsuleError(
                    f"{station}: capsule provenance overclaims its source"
                )

            for identifier in (capsule_id, rid, aid, station):
                if identifier in index:
                    raise MemoryDigestCapsuleError(
                        f"duplicate capsule identifier: {identifier}"
                    )
                index[identifier] = capsule

        expected_set_digest = _capsule_set_digest(capsules)
        if snapshot.get("capsule_set_digest") != expected_set_digest:
            raise MemoryDigestCapsuleError("capsule-set digest mismatch")

        measurement = snapshot.get("memory_measurement", {})
        if (
            measurement.get("possible_field_count") != 14
            or measurement.get("conversation_memory_exact_field_count") != 10
            or measurement.get("persisted_file_memory_exact_field_count") != 12
            or measurement.get("capsule_assisted_exact_field_count") != 14
            or measurement.get("capsule_assisted_is_internal_recall") is not False
            or measurement.get("capsule_assisted_is_live_provider_read") is not False
        ):
            raise MemoryDigestCapsuleError(
                "W14 must preserve the measured 10/14 -> 12/14 -> 14/14 boundary"
            )

        binding = snapshot.get("endpoint_binding")
        if not isinstance(binding, dict):
            raise MemoryDigestCapsuleError("endpoint binding link is required")
        if binding.get("state") != "AUTHORITY_PENDING":
            raise MemoryDigestCapsuleError(
                "only the fail-closed authority-pending endpoint state is admitted"
            )
        if binding.get("authority_packet_digest") is not None:
            raise MemoryDigestCapsuleError(
                "unverified authority packet digest must remain null"
            )
        if binding.get("authorized_endpoint") is not None:
            raise MemoryDigestCapsuleError(
                "authorized endpoint must remain null until authority is supplied"
            )
        if len(binding.get("unresolved_authority_inputs", [])) != 13:
            raise MemoryDigestCapsuleError(
                "all 13 unresolved authority inputs must remain explicit"
            )
        fail_closed = (
            binding.get("activation_packet_compilable_now") is False
            and binding.get("dispatch_allowed") is False
            and binding.get("endpoint_contacted") is False
            and binding.get("persistent_witness_executed") is False
            and binding.get("secret_material_embedded") is False
            and binding.get("persistent_deployment_claimed") is False
            and binding.get("promotion_claimed") is False
        )
        if not fail_closed:
            raise MemoryDigestCapsuleError(
                "endpoint link must remain fail-closed and non-deployed"
            )

        boundaries = snapshot.get("boundaries", {})
        required_false_boundaries = (
            "raw_docs_body_committed",
            "external_capsule_is_internal_memory",
            "hidden_weight_recall_claimed",
            "live_provider_checked_by_runtime",
            "endpoint_authority_invented",
            "secret_material_recorded",
            "endpoint_contacted",
            "merge_claimed",
            "persistent_deployment_claimed",
            "promotion_claimed",
        )
        for name in required_false_boundaries:
            if boundaries.get(name) is not False:
                raise MemoryDigestCapsuleError(
                    f"W14 requires boundary {name}=false"
                )

        return cls(snapshot=snapshot, capsules=capsules, index=index)

    def status(self) -> dict[str, Any]:
        measurement = self.snapshot["memory_measurement"]
        binding = self.snapshot["endpoint_binding"]
        return {
            "status": (
                "READY_CAPSULE_ASSISTED_PACKET_COMPLETE_"
                "ENDPOINT_AUTHORITY_PENDING"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "capsule_count": len(self.capsules),
            "capsule_set_digest": self.snapshot["capsule_set_digest"],
            "stations": sorted(capsule["station"] for capsule in self.capsules),
            "memory_measurement": deepcopy(measurement),
            "endpoint_binding": {
                "state": binding["state"],
                "dispatch_allowed": binding["dispatch_allowed"],
                "unresolved_authority_input_count": len(
                    binding["unresolved_authority_inputs"]
                ),
                "canonical_activation_handoff": deepcopy(
                    binding["canonical_activation_handoff"]
                ),
            },
            "boundaries": deepcopy(self.snapshot["boundaries"]),
        }

    def _find(self, identifier: str) -> dict[str, Any] | None:
        return self.index.get(identifier)

    def verify(self, identifier: str) -> dict[str, Any]:
        capsule = self._find(identifier)
        if capsule is None:
            return {
                "status": "INVALID_CAPSULE_ADDRESS",
                "identifier": identifier,
                "accepted_coordinate_classes": [
                    "capsule_id",
                    "RID",
                    "AID",
                    "station",
                ],
            }
        source = capsule["source"]
        actual_literal_digest = _literal_digest(source["literal"])
        actual_capsule_id = _capsule_id(capsule)
        actual_set_digest = _capsule_set_digest(self.capsules)
        verified = (
            actual_literal_digest == source["literal_sha256"]
            and actual_capsule_id == capsule["capsule_id"]
            and actual_set_digest == self.snapshot["capsule_set_digest"]
        )
        return {
            "status": "PASS_CAPSULE_VERIFIED" if verified else "HOLD",
            "identifier": identifier,
            "station": capsule["station"],
            "rid": capsule["rid"],
            "capsule_id": capsule["capsule_id"],
            "literal_digest_verified": (
                actual_literal_digest == source["literal_sha256"]
            ),
            "capsule_digest_verified": actual_capsule_id == capsule["capsule_id"],
            "capsule_set_digest_verified": (
                actual_set_digest == self.snapshot["capsule_set_digest"]
            ),
            "verified": verified,
            "internal_recall_claimed": False,
            "live_provider_checked": False,
        }

    def resolve(self, identifier: str) -> dict[str, Any]:
        capsule = self._find(identifier)
        if capsule is None:
            return self.verify(identifier)
        verification = self.verify(capsule["capsule_id"])
        return {
            "status": "RESOLVED_EXTERNAL_MEMORY_DIGEST_CAPSULE",
            "identifier": identifier,
            "capsule_id": capsule["capsule_id"],
            "station": capsule["station"],
            "rid": capsule["rid"],
            "aid": capsule["aid"],
            "source": deepcopy(capsule["source"]),
            "provenance": deepcopy(capsule["provenance"]),
            "verification": verification,
            "packet_fields_completed": 14,
            "possible_packet_fields": 14,
            "capsule_assisted_is_internal_recall": False,
            "capsule_assisted_is_live_provider_read": False,
        }

    def endpoint_binding_status(self) -> dict[str, Any]:
        binding = deepcopy(self.snapshot["endpoint_binding"])
        return {
            "status": "ENDPOINT_BINDING_AUTHORITY_PENDING",
            **binding,
            "binding_ready": True,
            "binding_complete": False,
            "next_required_event": (
                "Supply a digest-bound authorized activation packet through "
                "the canonical PR #11 handoff; this runtime does not invent it."
            ),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_memory_digest_capsules(mcp: Any) -> None:
    """Register W14 capsule navigation and endpoint-gate surfaces."""

    registry = FrozenMemoryDigestCapsules.load()

    @mcp.tool()
    def athena_memory_digest_capsule_status() -> str:
        """Report W14 memory completion and the endpoint authority boundary."""
        return _render(registry.status())

    @mcp.tool()
    def resolve_athena_memory_digest_capsule(identifier: str) -> str:
        """Resolve a capsule ID, RID, AID, or station without fuzzy substitution."""
        return _render(registry.resolve(identifier))

    @mcp.tool()
    def verify_athena_memory_digest_capsule(identifier: str) -> str:
        """Recompute literal, capsule, and capsule-set digests."""
        return _render(registry.verify(identifier))

    @mcp.tool()
    def athena_endpoint_binding_status() -> str:
        """Expose the fail-closed authorized-endpoint binding state."""
        return _render(registry.endpoint_binding_status())

    @mcp.resource("athena://memory-digest-capsules")
    def memory_digest_capsule_resource() -> str:
        """Expose verified W14 capsules and their non-internal provenance."""
        return _render(
            {
                "status": registry.status(),
                "capsules": [
                    registry.resolve(capsule["capsule_id"])
                    for capsule in registry.capsules
                ],
                "endpoint_binding": registry.endpoint_binding_status(),
            }
        )
