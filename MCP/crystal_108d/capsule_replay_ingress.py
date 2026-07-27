"""Opaque capsule replay and secret-free authority packet ingress for W15.

Blind replay accepts only a W14 capsule ID and reconstructs its exact packet from
the frozen external capsule registry. Authority ingress validates an ephemeral
JSON packet against the canonical PR #11 shape. It stores nothing, verifies no
external claim, accepts no secret value, contacts no endpoint, and cannot dispatch.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

from crystal_108d.memory_digest_capsules import FrozenMemoryDigestCapsules


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "w15_blind_replay_ingress.json"
)
SCHEMA = "athena.capsule-blind-replay-ingress/v1"
PHASE = "KC144.XNAV.W15"
ACTIVATION_SCHEMA = "athena.persistent-host-activation-packet/v1"
UNRESOLVED_STATE = "UNRESOLVED"
AUTHORIZED_STATE = "AUTHORIZED_FOR_LIVE_WITNESS"
CAPSULE_PREFIX = "mcap:sha256:"
MAX_PACKET_BYTES = 32768
TARGET_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")

TOP_LEVEL_FIELDS = {
    "schema",
    "state",
    "canonical_hardening_head",
    "source_commit",
    "runtime_p09_head",
    "image",
    "provider",
    "target",
    "authorization",
    "witness",
    "authority",
    "secret_material_recorded",
}
PROVIDER_FIELDS = {
    "id",
    "account_scope",
    "deployment_id",
    "deployment_observed_at",
    "evidence_url",
}
TARGET_FIELDS = {
    "id",
    "endpoint",
    "persistence_class",
    "secret_store_ref",
}
AUTHORIZATION_FIELDS = {"ref", "actor", "authorized_at"}
WITNESS_FIELDS = {
    "environment",
    "secret_name",
    "sample_count",
    "interval_seconds",
    "minimum_span_seconds",
}
AUTHORITY_FIELDS = {
    "live_witness_authorized",
    "runtime_can_promote",
    "promotion_claimed",
    "merge_claimed",
    "ic10_required",
}


class CapsuleReplayIngressError(RuntimeError):
    """Raised when the frozen W15 replay/ingress contract is invalid."""


class AuthorityPacketError(ValueError):
    """Raised when a submitted authority packet fails structural admission."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapsuleReplayIngressError("W15 snapshot must be a JSON object")
    return value


def _challenge_set_digest(challenges: list[dict[str, Any]]) -> str:
    material = {
        "schema": SCHEMA,
        "phase": PHASE,
        "challenges": [
            {
                "challenge_id": challenge["challenge_id"],
                "capsule_id": challenge["capsule_id"],
                "expected_packet_digest": challenge["expected_packet_digest"],
            }
            for challenge in sorted(
                challenges, key=lambda value: value["challenge_id"]
            )
        ],
    }
    return "sha256:" + sha256(_canonical_bytes(material)).hexdigest()


def _exact_object(
    value: Any,
    fields: set[str],
    path: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AuthorityPacketError(f"{path} must be an object")
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        raise AuthorityPacketError(
            f"{path} contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if missing:
        raise AuthorityPacketError(
            f"{path} is missing required fields: "
            + ", ".join(sorted(missing))
        )
    return value


def _text(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 512
        or any(ord(character) < 32 for character in value)
    ):
        raise AuthorityPacketError(f"{path} must be bounded non-empty text")
    return value.strip()


def _timestamp(value: Any, path: str) -> str:
    candidate = _text(value, path)
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise AuthorityPacketError(f"{path} must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise AuthorityPacketError(f"{path} must include a timezone")
    return candidate


def _https_url(value: Any, path: str, *, exact_mcp: bool) -> str:
    candidate = _text(value, path)
    parts = urlsplit(candidate)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
    ):
        raise AuthorityPacketError(
            f"{path} must be a secret-free absolute HTTPS URL"
        )
    if exact_mcp and parts.path.rstrip("/") != "/mcp":
        raise AuthorityPacketError(f"{path} must end exactly in /mcp")
    return candidate.rstrip("/")


class FrozenCapsuleReplayIngress:
    """Verified W15 replay challenges and non-dispatching packet ingress."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        capsules: FrozenMemoryDigestCapsules,
        challenges_by_capsule: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.capsules = capsules
        self.challenges_by_capsule = challenges_by_capsule

    @classmethod
    def load(cls, path: Path = DATA_PATH) -> "FrozenCapsuleReplayIngress":
        snapshot = _load_json(path)
        if snapshot.get("schema") != SCHEMA:
            raise CapsuleReplayIngressError(
                f"unexpected W15 schema: {snapshot.get('schema')!r}"
            )
        if snapshot.get("phase") != PHASE:
            raise CapsuleReplayIngressError(
                f"unexpected W15 phase: {snapshot.get('phase')!r}"
            )

        capsules = FrozenMemoryDigestCapsules.load()
        predecessor = snapshot.get("predecessor", {})
        if predecessor.get("capsule_set_digest") != capsules.snapshot.get(
            "capsule_set_digest"
        ):
            raise CapsuleReplayIngressError(
                "W15 predecessor must pin the exact W14 capsule-set root"
            )

        replay = snapshot.get("blind_replay")
        if not isinstance(replay, dict):
            raise CapsuleReplayIngressError("blind_replay contract is required")
        if replay.get("input_fields") != ["capsule_id"]:
            raise CapsuleReplayIngressError(
                "blind replay may disclose only capsule_id"
            )
        if (
            replay.get("request_uses_current_conversation") is not False
            or replay.get("request_uses_live_google_drive") is not False
            or replay.get("request_uses_fuzzy_lookup") is not False
            or replay.get("internal_recall_claimed") is not False
        ):
            raise CapsuleReplayIngressError(
                "blind replay must preserve external-capsule provenance"
            )

        challenges = replay.get("challenges")
        if not isinstance(challenges, list) or len(challenges) != 2:
            raise CapsuleReplayIngressError(
                "W15 requires exactly two opaque capsule challenges"
            )
        challenges_by_capsule: dict[str, dict[str, Any]] = {}
        challenge_ids: set[str] = set()
        for challenge in challenges:
            if not isinstance(challenge, dict):
                raise CapsuleReplayIngressError("each challenge must be an object")
            if set(challenge) != {
                "challenge_id",
                "capsule_id",
                "expected_packet_digest",
            }:
                raise CapsuleReplayIngressError(
                    "challenge fields must be exact and secret-free"
                )
            challenge_id = challenge.get("challenge_id")
            capsule_id = challenge.get("capsule_id")
            expected = challenge.get("expected_packet_digest")
            if not all(
                isinstance(value, str) and value
                for value in (challenge_id, capsule_id, expected)
            ):
                raise CapsuleReplayIngressError(
                    "challenge ID, capsule ID, and packet digest are required"
                )
            if challenge_id in challenge_ids or capsule_id in challenges_by_capsule:
                raise CapsuleReplayIngressError("duplicate replay challenge")
            if not capsule_id.startswith(CAPSULE_PREFIX):
                raise CapsuleReplayIngressError(
                    "blind replay input must be a capsule ID"
                )
            resolved = capsules.resolve(capsule_id)
            if resolved.get("status") != "RESOLVED_EXTERNAL_MEMORY_DIGEST_CAPSULE":
                raise CapsuleReplayIngressError(
                    f"challenge references unknown capsule: {capsule_id}"
                )
            if expected != "sha256:" + capsule_id.removeprefix(CAPSULE_PREFIX):
                raise CapsuleReplayIngressError(
                    "challenge packet digest must equal its capsule material digest"
                )
            challenge_ids.add(challenge_id)
            challenges_by_capsule[capsule_id] = challenge

        expected_challenge_digest = _challenge_set_digest(challenges)
        if snapshot.get("challenge_set_digest") != expected_challenge_digest:
            raise CapsuleReplayIngressError("challenge-set digest mismatch")

        ingress = snapshot.get("authority_ingress")
        if not isinstance(ingress, dict):
            raise CapsuleReplayIngressError("authority_ingress contract is required")
        if ingress.get("allowed_states") != [
            UNRESOLVED_STATE,
            AUTHORIZED_STATE,
        ]:
            raise CapsuleReplayIngressError("unexpected ingress state allowlist")
        if len(ingress.get("unresolved_authority_inputs", [])) != 13:
            raise CapsuleReplayIngressError(
                "all 13 unresolved authority inputs must remain explicit"
            )
        required_false = (
            "submitted_packets_persisted",
            "external_authority_verified_by_ingress",
            "provider_evidence_fetched_by_ingress",
            "secret_value_accepted",
            "secret_material_recorded",
            "endpoint_contact_capability",
            "dispatch_allowed",
            "runtime_can_promote",
        )
        for name in required_false:
            if ingress.get(name) is not False:
                raise CapsuleReplayIngressError(
                    f"authority ingress requires {name}=false"
                )
        if ingress.get("ic10_required") is not True:
            raise CapsuleReplayIngressError("authority ingress must preserve IC10")

        boundaries = snapshot.get("boundaries", {})
        for name, value in boundaries.items():
            if value is not False:
                raise CapsuleReplayIngressError(
                    f"W15 boundary {name} must remain false"
                )

        return cls(
            snapshot=snapshot,
            capsules=capsules,
            challenges_by_capsule=challenges_by_capsule,
        )

    def replay(self, capsule_id: str) -> dict[str, Any]:
        challenge = self.challenges_by_capsule.get(capsule_id)
        if challenge is None:
            return {
                "status": "INVALID_BLIND_REPLAY_ADDRESS",
                "identifier": capsule_id,
                "accepted_coordinate_classes": ["capsule_id"],
                "fuzzy_substitution_used": False,
            }

        resolved = self.capsules.resolve(capsule_id)
        packet = {
            "station": resolved["station"],
            "rid": resolved["rid"],
            "aid": resolved["aid"],
            "source": deepcopy(resolved["source"]),
        }
        packet_digest = "sha256:" + sha256(_canonical_bytes(packet)).hexdigest()
        exact = (
            packet_digest == challenge["expected_packet_digest"]
            and resolved["verification"]["verified"] is True
        )
        return {
            "status": "PASS_OPAQUE_CAPSULE_BLIND_REPLAY" if exact else "HOLD",
            "challenge_id": challenge["challenge_id"],
            "input": {"capsule_id": capsule_id},
            "withheld_request_fields": deepcopy(
                self.snapshot["blind_replay"]["withheld_request_fields"]
            ),
            "packet": packet,
            "packet_digest": packet_digest,
            "expected_packet_digest": challenge["expected_packet_digest"],
            "literal_capsule_set_verification": deepcopy(
                resolved["verification"]
            ),
            "exact_packet_reconstructed": exact,
            "request_uses_current_conversation": False,
            "request_uses_live_google_drive": False,
            "internal_recall_claimed": False,
        }

    def replay_status(self) -> dict[str, Any]:
        results = [
            self.replay(capsule_id)
            for capsule_id in sorted(self.challenges_by_capsule)
        ]
        passed = sum(
            result.get("status") == "PASS_OPAQUE_CAPSULE_BLIND_REPLAY"
            for result in results
        )
        return {
            "status": (
                "PASS_ALL_OPAQUE_CAPSULE_REPLAYS"
                if passed == len(results)
                else "HOLD"
            ),
            "schema": SCHEMA,
            "phase": PHASE,
            "challenge_set_digest": self.snapshot["challenge_set_digest"],
            "challenge_count": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "input_fields": ["capsule_id"],
            "withheld_request_fields": deepcopy(
                self.snapshot["blind_replay"]["withheld_request_fields"]
            ),
            "internal_recall_claimed": False,
            "live_provider_read": False,
            "results": results,
        }

    def _validate_lineage(self, packet: dict[str, Any]) -> None:
        lineage = self.snapshot["authority_ingress"]["immutable_lineage"]
        for field, expected in lineage.items():
            if packet.get(field) != expected:
                raise AuthorityPacketError(
                    f"activation packet must pin immutable {field}"
                )

    def _validate_witness(self, value: Any) -> dict[str, Any]:
        witness = _exact_object(value, WITNESS_FIELDS, "witness")
        expected = self.snapshot["authority_ingress"]["witness_plan"]
        if witness != expected:
            raise AuthorityPacketError(
                "activation packet must preserve the exact witness plan"
            )
        return witness

    def _validate_authority(
        self,
        value: Any,
        *,
        live_witness_authorized: bool,
    ) -> dict[str, Any]:
        authority = _exact_object(value, AUTHORITY_FIELDS, "authority")
        expected = {
            "live_witness_authorized": live_witness_authorized,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        }
        if authority != expected:
            raise AuthorityPacketError(
                "activation packet crosses its authority boundary"
            )
        return authority

    def _validate_packet(self, packet: Any) -> tuple[str, dict[str, Any]]:
        packet = _exact_object(packet, TOP_LEVEL_FIELDS, "activation packet")
        if packet.get("schema") != ACTIVATION_SCHEMA:
            raise AuthorityPacketError(
                f"activation packet schema must be {ACTIVATION_SCHEMA}"
            )
        self._validate_lineage(packet)
        provider = _exact_object(packet.get("provider"), PROVIDER_FIELDS, "provider")
        target = _exact_object(packet.get("target"), TARGET_FIELDS, "target")
        authorization = _exact_object(
            packet.get("authorization"),
            AUTHORIZATION_FIELDS,
            "authorization",
        )
        self._validate_witness(packet.get("witness"))
        if packet.get("secret_material_recorded") is not False:
            raise AuthorityPacketError(
                "authority packet must never record secret material"
            )

        state = packet.get("state")
        if state == UNRESOLVED_STATE:
            if any(value is not None for value in provider.values()):
                raise AuthorityPacketError("unresolved provider fields must be null")
            if any(value is not None for value in target.values()):
                raise AuthorityPacketError("unresolved target fields must be null")
            if any(value is not None for value in authorization.values()):
                raise AuthorityPacketError(
                    "unresolved authorization fields must be null"
                )
            self._validate_authority(
                packet.get("authority"),
                live_witness_authorized=False,
            )
            return state, packet

        if state != AUTHORIZED_STATE:
            raise AuthorityPacketError(
                "activation packet state is not admitted"
            )

        normalized = deepcopy(packet)
        normalized["provider"] = {
            "id": _text(provider.get("id"), "provider.id"),
            "account_scope": _text(
                provider.get("account_scope"), "provider.account_scope"
            ),
            "deployment_id": _text(
                provider.get("deployment_id"), "provider.deployment_id"
            ),
            "deployment_observed_at": _timestamp(
                provider.get("deployment_observed_at"),
                "provider.deployment_observed_at",
            ),
            "evidence_url": _https_url(
                provider.get("evidence_url"),
                "provider.evidence_url",
                exact_mcp=False,
            ),
        }
        target_id = _text(target.get("id"), "target.id")
        if not TARGET_ID.fullmatch(target_id):
            raise AuthorityPacketError(
                "target.id must be a bounded lowercase identifier"
            )
        persistence_class = _text(
            target.get("persistence_class"), "target.persistence_class"
        )
        allowed_classes = self.snapshot["authority_ingress"][
            "persistence_classes"
        ]
        if persistence_class not in allowed_classes:
            raise AuthorityPacketError(
                "target.persistence_class is not admitted"
            )
        normalized["target"] = {
            "id": target_id,
            "endpoint": _https_url(
                target.get("endpoint"), "target.endpoint", exact_mcp=True
            ),
            "persistence_class": persistence_class,
            "secret_store_ref": _text(
                target.get("secret_store_ref"), "target.secret_store_ref"
            ),
        }
        normalized["authorization"] = {
            "ref": _text(authorization.get("ref"), "authorization.ref"),
            "actor": _text(
                authorization.get("actor"), "authorization.actor"
            ),
            "authorized_at": _timestamp(
                authorization.get("authorized_at"),
                "authorization.authorized_at",
            ),
        }
        normalized["authority"] = self._validate_authority(
            packet.get("authority"),
            live_witness_authorized=True,
        )
        return state, normalized

    def inspect_authority_packet(self, packet_json: str) -> dict[str, Any]:
        base = {
            "submitted_packet_persisted": False,
            "external_authority_verified": False,
            "provider_evidence_fetched": False,
            "secret_value_accepted": False,
            "secret_material_recorded": False,
            "endpoint_contacted": False,
            "dispatch_allowed": False,
            "runtime_can_promote": False,
            "ic10_required": True,
        }
        if not isinstance(packet_json, str):
            return {
                "status": "REJECTED_AUTHORITY_PACKET",
                "reason": "packet_json must be text",
                **base,
            }
        encoded = packet_json.encode("utf-8")
        if len(encoded) > MAX_PACKET_BYTES:
            return {
                "status": "REJECTED_AUTHORITY_PACKET",
                "reason": "packet exceeds the bounded ingress size",
                **base,
            }
        try:
            packet = json.loads(packet_json)
            state, normalized = self._validate_packet(packet)
        except (json.JSONDecodeError, AuthorityPacketError) as error:
            return {
                "status": "REJECTED_AUTHORITY_PACKET",
                "reason": str(error),
                **base,
            }

        digest = "sha256:" + sha256(_canonical_bytes(normalized)).hexdigest()
        if state == UNRESOLVED_STATE:
            return {
                "status": "HOLD_AUTHORITY_INPUTS_UNRESOLVED",
                "packet_state": state,
                "packet_digest": digest,
                "structurally_valid": True,
                "unresolved_authority_inputs": deepcopy(
                    self.snapshot["authority_ingress"][
                        "unresolved_authority_inputs"
                    ]
                ),
                **base,
            }

        return {
            "status": "PASS_STRUCTURAL_AUTHORITY_PACKET_INGRESS_NOT_DISPATCHED",
            "packet_state": state,
            "packet_digest": digest,
            "structurally_valid": True,
            "authority_claims_present": True,
            "remaining_external_gates": [
                "independent provider evidence verification",
                "canonical PR #11 activation compiler",
                "protected bearer secret provisioning",
                "protected live-witness job",
                "three-sample persistent witness",
                "control-plane admission",
                "IC10 review",
            ],
            **base,
        }

    def authority_ingress_status(self) -> dict[str, Any]:
        ingress = deepcopy(self.snapshot["authority_ingress"])
        return {
            "status": "READY_STRUCTURAL_INGRESS_AUTHORITY_UNVERIFIED",
            **ingress,
            "packet_storage": "NONE",
            "network_capability": "NONE",
            "dispatch_capability": "NONE",
            "next_required_event": (
                "An authorized operator may submit a secret-free packet for "
                "structural inspection; external verification and dispatch "
                "remain in the canonical PR #11 protected workflow."
            ),
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_capsule_replay_ingress(mcp: Any) -> None:
    """Register W15 replay and non-dispatching authority ingress surfaces."""

    registry = FrozenCapsuleReplayIngress.load()

    @mcp.tool()
    def athena_capsule_blind_replay_status() -> str:
        """Run both frozen opaque-ID replay challenges."""
        return _render(registry.replay_status())

    @mcp.tool()
    def replay_athena_capsule_blind(capsule_id: str) -> str:
        """Replay an exact packet from only its opaque W14 capsule ID."""
        return _render(registry.replay(capsule_id))

    @mcp.tool()
    def inspect_athena_authority_packet(packet_json: str) -> str:
        """Validate a secret-free packet structurally; never store or dispatch it."""
        return _render(registry.inspect_authority_packet(packet_json))

    @mcp.tool()
    def athena_authority_packet_ingress_status() -> str:
        """Report the strict W15 ingress contract and its authority boundary."""
        return _render(registry.authority_ingress_status())

    @mcp.resource("athena://capsule-blind-replay")
    def capsule_blind_replay_resource() -> str:
        """Expose frozen replay challenge results and provenance boundaries."""
        return _render(registry.replay_status())

    @mcp.resource("athena://authority-packet-ingress")
    def authority_packet_ingress_resource() -> str:
        """Expose the non-networked, non-dispatching packet ingress contract."""
        return _render(registry.authority_ingress_status())
