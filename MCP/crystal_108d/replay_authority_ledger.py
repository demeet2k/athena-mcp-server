"""KC144 W16 replay ledger and fail-closed authority-evidence adjunction.

The replay side accepts only an opaque external capsule ID. The authority side
checks structural agreement between two submitted JSON values, but it does not
fetch provider evidence, validate the submitter's real-world authority, persist
inputs, receive bearer material, contact an endpoint, dispatch a witness, or
promote anything.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import ipaddress
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_PATH = DATA_DIR / "w16_replay_authority_ledger.json"
CAPSULE_PATH = DATA_DIR / "w14_memory_digest_capsules.json"
SCHEMA = "athena.xnav-w16-replay-authority-ledger/v1"
PHASE = "KC144.XNAV.W16"
CAPSULE_SCHEMA = "athena.memory-digest-capsules/v1"
CAPSULE_PHASE = "KC144.XNAV.W14"
CAPSULE_PREFIX = "mcap:sha256:"
SHA_PREFIX = "sha256:"
ACTIVATION_SCHEMA = "athena.persistent-host-activation-packet/v1"
ACTIVATION_STATE = "AUTHORIZED_FOR_LIVE_WITNESS"
EVIDENCE_SCHEMA = "athena.provider-deployment-evidence/v1"
CANONICAL_HARDENING_HEAD = "b4e24de38788ecdf30f43514ece279d1270b998b"
SOURCE_COMMIT = "52d0e2abf282aee5f8bf233521989bc2c8969989"
RUNTIME_P09_HEAD = "9731b24c5963b75821b381b4562aa51baa55196c"
IMAGE_DIGEST = (
    "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
)
IMAGE = f"ghcr.io/demeet2k/athena-mcp-server@{IMAGE_DIGEST}"
WITNESS_PLAN = {
    "environment": "p10-persistent-host",
    "secret_name": "ATHENA_MCP_BEARER_TOKEN",
    "sample_count": 3,
    "interval_seconds": 20,
    "minimum_span_seconds": 40,
}
PERSISTENCE_CLASSES = {
    "managed-service",
    "orchestrated-service",
    "self-hosted-service",
}
TARGET_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "host.docker.internal",
    "gateway.docker.internal",
}
BLOCKED_SUFFIXES = (".localhost", ".local", ".test", ".invalid", ".example")
FORBIDDEN_SECRET_KEYS = {
    "authorization_header",
    "bearer",
    "bearer_token",
    "password",
    "secret_material",
    "secret_value",
    "token",
}

ACTIVATION_FIELDS = {
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
TARGET_FIELDS = {"id", "endpoint", "persistence_class", "secret_store_ref"}
AUTHORIZATION_FIELDS = {"ref", "actor", "authorized_at"}
WITNESS_FIELDS = set(WITNESS_PLAN)
AUTHORITY_FIELDS = {
    "live_witness_authorized",
    "runtime_can_promote",
    "promotion_claimed",
    "merge_claimed",
    "ic10_required",
}
EVIDENCE_FIELDS = {
    "schema",
    "provider_id",
    "provider_account_scope",
    "deployment_id",
    "target_id",
    "authorization_ref",
    "deployed_image",
    "image_digest",
    "source_commit",
    "runtime_p09_head",
    "endpoint",
    "persistent_service",
    "deployment_observed_at",
    "secret_store_ref",
    "secret_material_recorded",
    "evidence_url",
}
ROW_FIELDS = {
    "sequence",
    "prev_digest",
    "challenge_id",
    "capsule_id",
    "packet_digest",
    "outcome",
    "provenance",
    "internal_recall_claimed",
    "live_provider_read",
    "row_digest",
}


class ReplayAuthorityLedgerError(RuntimeError):
    """Raised when frozen W16 data violates its exact contract."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return SHA_PREFIX + sha256(_canonical_bytes(value)).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReplayAuthorityLedgerError(f"{path.name} must contain an object")
    return value


def _exact_object(
    value: Any, fields: set[str], path: str, error_type: type[Exception] = ValueError
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise error_type(f"{path} must be an object")
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        raise error_type(
            f"{path} contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if missing:
        raise error_type(
            f"{path} is missing required fields: " + ", ".join(sorted(missing))
        )
    return value


def _bounded_text(value: Any, path: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 512
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError(f"{path} must be bounded non-empty text")
    return value.strip()


def _timestamp(value: Any, path: str) -> str:
    candidate = _bounded_text(value, path)
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ValueError(f"{path} must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{path} must include a timezone")
    return candidate


def _parsed_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _host_is_ephemeral_or_local(hostname: str) -> bool:
    lowered = hostname.rstrip(".").lower()
    if lowered in BLOCKED_HOSTS or lowered.endswith(BLOCKED_SUFFIXES):
        return True
    try:
        address = ipaddress.ip_address(lowered)
    except ValueError:
        return False
    return (
        address.is_loopback
        or address.is_link_local
        or address.is_unspecified
        or address.is_multicast
    )


def _https_url(value: Any, path: str, *, exact_mcp: bool = False) -> str:
    candidate = _bounded_text(value, path)
    parts = urlsplit(candidate)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
    ):
        raise ValueError(f"{path} must be a secret-free absolute HTTPS URL")
    if exact_mcp and parts.path.rstrip("/") != "/mcp":
        raise ValueError(f"{path} must end exactly in /mcp")
    if exact_mcp and _host_is_ephemeral_or_local(parts.hostname):
        raise ValueError(f"{path} cannot name a local, test, or runner endpoint")
    path_value = "/mcp" if exact_mcp else parts.path
    return urlunsplit((parts.scheme, parts.netloc, path_value, "", "")).rstrip("/")


def _assert_secret_free(value: Any, path: str = "input") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.lower() in FORBIDDEN_SECRET_KEYS:
                raise ValueError(f"{path}.{key} is forbidden secret material")
            _assert_secret_free(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_secret_free(nested, f"{path}[{index}]")
    elif isinstance(value, str) and "bearer " in value.lower():
        raise ValueError(f"{path} must not contain bearer material")


def _capsule_packet(capsule: dict[str, Any]) -> dict[str, Any]:
    return {
        "station": capsule["station"],
        "rid": capsule["rid"],
        "aid": capsule["aid"],
        "source": deepcopy(capsule["source"]),
    }


def _capsule_id(capsule: dict[str, Any]) -> str:
    return CAPSULE_PREFIX + sha256(_canonical_bytes(_capsule_packet(capsule))).hexdigest()


def _capsule_set_digest(capsules: list[dict[str, Any]]) -> str:
    return _digest(
        {
            "schema": CAPSULE_SCHEMA,
            "phase": CAPSULE_PHASE,
            "capsule_ids": sorted(capsule["capsule_id"] for capsule in capsules),
        }
    )


def _row_digest(row: dict[str, Any]) -> str:
    material = {key: deepcopy(value) for key, value in row.items() if key != "row_digest"}
    return _digest(material)


def _ledger_root(rows: list[dict[str, Any]]) -> str:
    return _digest(
        {
            "schema": SCHEMA,
            "phase": PHASE,
            "row_digests": [row["row_digest"] for row in rows],
        }
    )


def _validate_activation_packet(value: Any) -> dict[str, Any]:
    _assert_secret_free(value, "activation_packet")
    packet = _exact_object(value, ACTIVATION_FIELDS, "activation packet")
    if packet.get("schema") != ACTIVATION_SCHEMA:
        raise ValueError(f"activation packet schema must be {ACTIVATION_SCHEMA}")
    if packet.get("state") != ACTIVATION_STATE:
        raise ValueError(f"activation packet state must be {ACTIVATION_STATE}")
    if packet.get("canonical_hardening_head") != CANONICAL_HARDENING_HEAD:
        raise ValueError("activation packet must pin the canonical hardening head")
    if packet.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("activation packet must pin the frozen source commit")
    if packet.get("runtime_p09_head") != RUNTIME_P09_HEAD:
        raise ValueError("activation packet must pin the P09 runtime head")
    if packet.get("image") != IMAGE:
        raise ValueError("activation packet must pin the exact P09 image")

    provider = _exact_object(packet.get("provider"), PROVIDER_FIELDS, "provider")
    normalized_provider = {
        "id": _bounded_text(provider.get("id"), "provider.id"),
        "account_scope": _bounded_text(
            provider.get("account_scope"), "provider.account_scope"
        ),
        "deployment_id": _bounded_text(
            provider.get("deployment_id"), "provider.deployment_id"
        ),
        "deployment_observed_at": _timestamp(
            provider.get("deployment_observed_at"),
            "provider.deployment_observed_at",
        ),
        "evidence_url": _https_url(
            provider.get("evidence_url"), "provider.evidence_url"
        ),
    }

    target = _exact_object(packet.get("target"), TARGET_FIELDS, "target")
    target_id = _bounded_text(target.get("id"), "target.id")
    if not TARGET_ID.fullmatch(target_id):
        raise ValueError("target.id must be a bounded lowercase identifier")
    persistence_class = _bounded_text(
        target.get("persistence_class"), "target.persistence_class"
    )
    if persistence_class not in PERSISTENCE_CLASSES:
        raise ValueError("target.persistence_class is not admitted")
    normalized_target = {
        "id": target_id,
        "endpoint": _https_url(
            target.get("endpoint"), "target.endpoint", exact_mcp=True
        ),
        "persistence_class": persistence_class,
        "secret_store_ref": _bounded_text(
            target.get("secret_store_ref"), "target.secret_store_ref"
        ),
    }

    authorization = _exact_object(
        packet.get("authorization"), AUTHORIZATION_FIELDS, "authorization"
    )
    normalized_authorization = {
        "ref": _bounded_text(authorization.get("ref"), "authorization.ref"),
        "actor": _bounded_text(authorization.get("actor"), "authorization.actor"),
        "authorized_at": _timestamp(
            authorization.get("authorized_at"), "authorization.authorized_at"
        ),
    }
    if _parsed_timestamp(
        normalized_authorization["authorized_at"]
    ) > _parsed_timestamp(normalized_provider["deployment_observed_at"]):
        raise ValueError("deployment observation cannot precede authorization")

    witness = _exact_object(packet.get("witness"), WITNESS_FIELDS, "witness")
    if witness != WITNESS_PLAN:
        raise ValueError("activation packet must preserve the exact witness plan")
    authority = _exact_object(
        packet.get("authority"), AUTHORITY_FIELDS, "authority"
    )
    expected_authority = {
        "live_witness_authorized": True,
        "runtime_can_promote": False,
        "promotion_claimed": False,
        "merge_claimed": False,
        "ic10_required": True,
    }
    if authority != expected_authority:
        raise ValueError("activation packet crosses the nonpromotion boundary")
    if packet.get("secret_material_recorded") is not False:
        raise ValueError("activation packet must not record secret material")
    return {
        **packet,
        "provider": normalized_provider,
        "target": normalized_target,
        "authorization": normalized_authorization,
        "witness": deepcopy(WITNESS_PLAN),
        "authority": expected_authority,
    }


def _validate_provider_evidence(
    value: Any, packet: dict[str, Any]
) -> dict[str, Any]:
    _assert_secret_free(value, "provider_evidence")
    evidence = _exact_object(value, EVIDENCE_FIELDS, "provider evidence")
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError(f"provider evidence schema must be {EVIDENCE_SCHEMA}")
    normalized = {
        "schema": EVIDENCE_SCHEMA,
        "provider_id": _bounded_text(evidence.get("provider_id"), "provider_id"),
        "provider_account_scope": _bounded_text(
            evidence.get("provider_account_scope"), "provider_account_scope"
        ),
        "deployment_id": _bounded_text(
            evidence.get("deployment_id"), "deployment_id"
        ),
        "target_id": _bounded_text(evidence.get("target_id"), "target_id"),
        "authorization_ref": _bounded_text(
            evidence.get("authorization_ref"), "authorization_ref"
        ),
        "deployed_image": _bounded_text(
            evidence.get("deployed_image"), "deployed_image"
        ),
        "image_digest": _bounded_text(
            evidence.get("image_digest"), "image_digest"
        ),
        "source_commit": _bounded_text(
            evidence.get("source_commit"), "source_commit"
        ),
        "runtime_p09_head": _bounded_text(
            evidence.get("runtime_p09_head"), "runtime_p09_head"
        ),
        "endpoint": _https_url(evidence.get("endpoint"), "endpoint", exact_mcp=True),
        "persistent_service": evidence.get("persistent_service"),
        "deployment_observed_at": _timestamp(
            evidence.get("deployment_observed_at"), "deployment_observed_at"
        ),
        "secret_store_ref": _bounded_text(
            evidence.get("secret_store_ref"), "secret_store_ref"
        ),
        "secret_material_recorded": evidence.get("secret_material_recorded"),
        "evidence_url": _https_url(evidence.get("evidence_url"), "evidence_url"),
    }
    provider = packet["provider"]
    target = packet["target"]
    authorization = packet["authorization"]
    expected = {
        "provider_id": provider["id"],
        "provider_account_scope": provider["account_scope"],
        "deployment_id": provider["deployment_id"],
        "target_id": target["id"],
        "authorization_ref": authorization["ref"],
        "deployed_image": IMAGE,
        "image_digest": IMAGE_DIGEST,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "endpoint": target["endpoint"],
        "persistent_service": True,
        "deployment_observed_at": provider["deployment_observed_at"],
        "secret_store_ref": target["secret_store_ref"],
        "secret_material_recorded": False,
        "evidence_url": provider["evidence_url"],
    }
    mismatches = [
        field for field, expected_value in expected.items()
        if normalized[field] != expected_value
    ]
    if mismatches:
        raise ValueError(
            "provider evidence does not match activation packet fields: "
            + ", ".join(mismatches)
        )
    return normalized


class FrozenReplayAuthorityLedger:
    """Verified append-only replay rows plus structural authority ingress."""

    def __init__(
        self,
        snapshot: dict[str, Any],
        capsule_snapshot: dict[str, Any],
        capsule_index: dict[str, dict[str, Any]],
    ) -> None:
        self.snapshot = snapshot
        self.capsule_snapshot = capsule_snapshot
        self.capsule_index = capsule_index
        self.rows = snapshot["replay_ledger"]["rows"]
        self.row_index = {row["capsule_id"]: row for row in self.rows}

    @classmethod
    def from_snapshots(
        cls, snapshot: dict[str, Any], capsule_snapshot: dict[str, Any]
    ) -> "FrozenReplayAuthorityLedger":
        if snapshot.get("schema") != SCHEMA or snapshot.get("phase") != PHASE:
            raise ReplayAuthorityLedgerError("unexpected W16 schema or phase")
        if (
            capsule_snapshot.get("schema") != CAPSULE_SCHEMA
            or capsule_snapshot.get("phase") != CAPSULE_PHASE
        ):
            raise ReplayAuthorityLedgerError("unexpected W14 capsule schema or phase")
        capsules = capsule_snapshot.get("capsules")
        if not isinstance(capsules, list) or len(capsules) != 2:
            raise ReplayAuthorityLedgerError("W16 requires exactly two W14 capsules")
        capsule_index: dict[str, dict[str, Any]] = {}
        for capsule in capsules:
            if not isinstance(capsule, dict):
                raise ReplayAuthorityLedgerError("capsules must be objects")
            capsule_id = capsule.get("capsule_id")
            if capsule_id != _capsule_id(capsule):
                raise ReplayAuthorityLedgerError("W14 capsule digest mismatch")
            literal = capsule.get("source", {}).get("literal")
            literal_digest = capsule.get("source", {}).get("literal_sha256")
            if (
                not isinstance(literal, str)
                or sha256(literal.encode("utf-8")).hexdigest() != literal_digest
            ):
                raise ReplayAuthorityLedgerError("W14 literal digest mismatch")
            if capsule_id in capsule_index:
                raise ReplayAuthorityLedgerError("duplicate W14 capsule ID")
            capsule_index[capsule_id] = capsule
        actual_capsule_root = _capsule_set_digest(capsules)
        if capsule_snapshot.get("capsule_set_digest") != actual_capsule_root:
            raise ReplayAuthorityLedgerError("W14 capsule-set digest mismatch")

        lineage = snapshot.get("lineage", {})
        expected_lineage = {
            "canonical_reconciliation_repository": "demeet2k/athena-mcp-server",
            "canonical_reconciliation_pull_request": 13,
            "canonical_reconciliation_head": "6f29ceb87838f03aa65cf25bf82a8e99ec955d6f",
            "w15_opaque_replay_origin_pull_request": 10,
            "w15_opaque_replay_origin_head": "44d3d8c7675302ff9679cda0fdaca2144de57dae",
            "w15_challenge_set_root": "sha256:753b5056a6e54c369caa4c99be2e0717b7b32d6eee66646385938d7e8115c39f",
            "w14_capsule_set_root": actual_capsule_root,
            "activation_handoff_pull_request": 11,
            "activation_handoff_head": "8bc9072fe2fa9ac9b2998653c7656ae92428be4c",
            "canonical_hardening_head": CANONICAL_HARDENING_HEAD,
            "source_commit": SOURCE_COMMIT,
            "runtime_p09_head": RUNTIME_P09_HEAD,
            "image": IMAGE,
            "image_digest": IMAGE_DIGEST,
        }
        if lineage != expected_lineage:
            raise ReplayAuthorityLedgerError("W16 immutable lineage mismatch")

        replay = snapshot.get("replay_ledger")
        if not isinstance(replay, dict):
            raise ReplayAuthorityLedgerError("replay_ledger is required")
        rows = replay.get("rows")
        if not isinstance(rows, list) or len(rows) != 2:
            raise ReplayAuthorityLedgerError("replay ledger requires exactly two rows")
        previous = replay.get("genesis_digest")
        if previous != lineage["w15_challenge_set_root"]:
            raise ReplayAuthorityLedgerError("ledger genesis must bind W15 challenge root")
        expected_challenges = ["w15:opaque:f07", "w15:opaque:m09"]
        for sequence, row in enumerate(rows, 1):
            row = _exact_object(
                row, ROW_FIELDS, f"row[{sequence}]",
                error_type=ReplayAuthorityLedgerError,
            )
            if row.get("sequence") != sequence or row.get("prev_digest") != previous:
                raise ReplayAuthorityLedgerError("replay row sequence/chain mismatch")
            if row.get("challenge_id") != expected_challenges[sequence - 1]:
                raise ReplayAuthorityLedgerError("replay challenge ordering mismatch")
            capsule = capsule_index.get(row.get("capsule_id"))
            if capsule is None:
                raise ReplayAuthorityLedgerError("replay row capsule is unknown")
            if row.get("packet_digest") != _digest(_capsule_packet(capsule)):
                raise ReplayAuthorityLedgerError("replay packet digest mismatch")
            if (
                row.get("outcome") != "PASS_OPAQUE_EXTERNAL_CAPSULE_REPLAY"
                or row.get("provenance") != "EXTERNAL_CONTENT_ADDRESSED_CAPSULE"
                or row.get("internal_recall_claimed") is not False
                or row.get("live_provider_read") is not False
            ):
                raise ReplayAuthorityLedgerError("replay row overclaims provenance")
            if row.get("row_digest") != _row_digest(row):
                raise ReplayAuthorityLedgerError("replay row digest mismatch")
            previous = row["row_digest"]
        if replay.get("ledger_root") != _ledger_root(rows):
            raise ReplayAuthorityLedgerError("replay ledger root mismatch")

        frozen_index = snapshot.get("capsule_index", {})
        expected_entries = {row["capsule_id"]: row["sequence"] for row in rows}
        if (
            frozen_index.get("accepted_request_coordinate") != "capsule_id"
            or frozen_index.get("fuzzy_resolution_allowed") is not False
            or frozen_index.get("station_rid_aid_aliases_allowed") is not False
            or frozen_index.get("entries") != expected_entries
        ):
            raise ReplayAuthorityLedgerError("capsule index is not exact-ID-only")

        contract = snapshot.get("authority_contract", {})
        expected_contract = {
            "activation_packet_schema": ACTIVATION_SCHEMA,
            "activation_state": ACTIVATION_STATE,
            "provider_evidence_schema": EVIDENCE_SCHEMA,
            "protected_environment": WITNESS_PLAN["environment"],
            "protected_secret_name": WITNESS_PLAN["secret_name"],
            "persistence_classes": sorted(PERSISTENCE_CLASSES),
            "witness_plan": WITNESS_PLAN,
            "unresolved_authority_input_count": 13,
            "submitted_evidence_class": "UNVERIFIED_EXTERNAL_ASSERTION",
            "external_evidence_verified": False,
            "dispatch_allowed": False,
        }
        if contract != expected_contract:
            raise ReplayAuthorityLedgerError("authority contract drift")
        boundaries = snapshot.get("boundaries", {})
        if not boundaries or any(value is not False for value in boundaries.values()):
            raise ReplayAuthorityLedgerError("all W16 nonauthority boundaries must be false")
        return cls(snapshot, capsule_snapshot, capsule_index)

    @classmethod
    def load(
        cls, path: Path = DATA_PATH, capsule_path: Path = CAPSULE_PATH
    ) -> "FrozenReplayAuthorityLedger":
        return cls.from_snapshots(_load_json(path), _load_json(capsule_path))

    def verify(self) -> dict[str, Any]:
        replay = self.snapshot["replay_ledger"]
        return {
            "status": "PASS_APPEND_ONLY_REPLAY_LEDGER_2_OF_2",
            "schema": SCHEMA,
            "phase": PHASE,
            "row_count": len(self.rows),
            "genesis_digest": replay["genesis_digest"],
            "ledger_root": replay["ledger_root"],
            "row_digests": [row["row_digest"] for row in self.rows],
            "capsule_set_root": self.snapshot["lineage"]["w14_capsule_set_root"],
            "challenge_set_root": self.snapshot["lineage"]["w15_challenge_set_root"],
            "verified": True,
            "internal_recall_claimed": False,
            "live_provider_read": False,
        }

    def status(self) -> dict[str, Any]:
        return {
            **self.verify(),
            "cross_navigation_state": (
                "SOURCE_REPLAY_AND_LEDGER_CLOSED__"
                "EXTERNAL_AUTHORITY_WITNESS_OPEN"
            ),
            "authority": deepcopy(self.snapshot["authority_contract"]),
            "boundaries": deepcopy(self.snapshot["boundaries"]),
            "successor": self.snapshot["successor"],
        }

    def read_row(self, sequence_or_capsule_id: str) -> dict[str, Any]:
        row = self.row_index.get(sequence_or_capsule_id)
        if row is None and sequence_or_capsule_id.isdigit():
            sequence = int(sequence_or_capsule_id)
            row = next(
                (candidate for candidate in self.rows
                 if candidate["sequence"] == sequence),
                None,
            )
        if row is None:
            return {
                "status": "INVALID_REPLAY_LEDGER_ADDRESS",
                "accepted_coordinate_classes": ["sequence", "capsule_id"],
                "fuzzy_resolution_allowed": False,
            }
        return {
            "status": "FOUND_REPLAY_LEDGER_ROW",
            "row": deepcopy(row),
            "ledger_root": self.snapshot["replay_ledger"]["ledger_root"],
        }

    def replay(self, capsule_id: str) -> dict[str, Any]:
        if not isinstance(capsule_id, str) or not capsule_id.startswith(CAPSULE_PREFIX):
            return {
                "status": "REJECT_NON_OPAQUE_CAPSULE_ID",
                "accepted_request_coordinate": "capsule_id",
                "station_rid_aid_aliases_allowed": False,
                "fuzzy_resolution_allowed": False,
            }
        row = self.row_index.get(capsule_id)
        capsule = self.capsule_index.get(capsule_id)
        if row is None or capsule is None:
            return {
                "status": "CAPSULE_ID_NOT_IN_FROZEN_REPLAY_LEDGER",
                "capsule_id": capsule_id,
            }
        packet = _capsule_packet(capsule)
        packet_digest = _digest(packet)
        verified = (
            packet_digest == row["packet_digest"]
            and _row_digest(row) == row["row_digest"]
        )
        return {
            "status": (
                "PASS_LEDGER_BOUND_OPAQUE_EXTERNAL_CAPSULE_REPLAY"
                if verified else "HOLD_REPLAY_VERIFICATION_FAILED"
            ),
            "request": {"capsule_id": capsule_id},
            "reconstructed_packet": packet,
            "packet_digest": packet_digest,
            "ledger_row_digest": row["row_digest"],
            "ledger_root": self.snapshot["replay_ledger"]["ledger_root"],
            "provenance": "EXTERNAL_CONTENT_ADDRESSED_CAPSULE",
            "verified": verified,
            "current_conversation_queried": False,
            "internal_recall_claimed": False,
            "live_google_docs_read": False,
        }

    def inspect_authority_evidence_adjunction(
        self, activation_packet_json: str, provider_evidence_json: str
    ) -> dict[str, Any]:
        try:
            if (
                not isinstance(activation_packet_json, str)
                or not isinstance(provider_evidence_json, str)
                or len(activation_packet_json) > 32768
                or len(provider_evidence_json) > 32768
            ):
                raise ValueError("inputs must be bounded JSON strings")
            packet_raw = json.loads(activation_packet_json)
            evidence_raw = json.loads(provider_evidence_json)
            packet = _validate_activation_packet(packet_raw)
            evidence = _validate_provider_evidence(evidence_raw, packet)
            packet_digest = _digest(packet)
            evidence_digest = _digest(evidence)
            adjunction_digest = _digest(
                {
                    "schema": SCHEMA,
                    "phase": PHASE,
                    "activation_packet_digest": packet_digest,
                    "provider_evidence_digest": evidence_digest,
                    "classification": "UNVERIFIED_EXTERNAL_ASSERTION",
                }
            )
            return {
                "status": (
                    "PASS_STRUCTURAL_PACKET_EVIDENCE_ADJUNCTION_"
                    "NOT_EXTERNALLY_WITNESSED"
                ),
                "activation_packet_digest": packet_digest,
                "provider_evidence_digest": evidence_digest,
                "adjunction_digest": adjunction_digest,
                "packet_structurally_valid": True,
                "provider_evidence_structurally_valid": True,
                "packet_evidence_fields_match": True,
                "submitted_evidence_class": "UNVERIFIED_EXTERNAL_ASSERTION",
                "submitted_inputs_persisted": False,
                "provider_evidence_fetched": False,
                "external_evidence_verified": False,
                "authorization_externally_verified": False,
                "secret_material_accepted": False,
                "endpoint_contacted": False,
                "persistent_witness_executed": False,
                "dispatch_allowed": False,
                "merge_claimed": False,
                "deployment_claimed": False,
                "promotion_claimed": False,
                "ic10_required": True,
            }
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return {
                "status": "HOLD_AUTHORITY_EVIDENCE_ADJUNCTION_REJECTED",
                "error": str(error),
                "submitted_inputs_persisted": False,
                "provider_evidence_fetched": False,
                "external_evidence_verified": False,
                "authorization_externally_verified": False,
                "secret_material_accepted": False,
                "endpoint_contacted": False,
                "persistent_witness_executed": False,
                "dispatch_allowed": False,
                "merge_claimed": False,
                "deployment_claimed": False,
                "promotion_claimed": False,
            }

    def authority_status(self) -> dict[str, Any]:
        return {
            "status": "AUTHORITY_EVIDENCE_ADJUNCTION_READY_INPUTS_UNRESOLVED",
            **deepcopy(self.snapshot["authority_contract"]),
            "activation_packet_present": False,
            "provider_evidence_present": False,
            "submitted_inputs_persisted": False,
            "endpoint_contacted": False,
            "persistent_witness_executed": False,
            "successor": self.snapshot["successor"],
        }


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def register_replay_authority_ledger(mcp: Any) -> None:
    """Register W16 replay-ledger and authority-adjunction surfaces."""

    registry = FrozenReplayAuthorityLedger.load()

    @mcp.tool()
    def athena_replay_authority_ledger_status() -> str:
        """Report the verified W16 ledger and still-open authority boundary."""
        return _render(registry.status())

    @mcp.tool()
    def read_athena_replay_ledger_row(sequence_or_capsule_id: str) -> str:
        """Read an exact W16 row by sequence or opaque capsule ID."""
        return _render(registry.read_row(sequence_or_capsule_id))

    @mcp.tool()
    def verify_athena_replay_authority_ledger() -> str:
        """Recompute the W16 row chain, capsule bindings, and ledger root."""
        return _render(registry.verify())

    @mcp.tool()
    def replay_athena_capsule_from_ledger(capsule_id: str) -> str:
        """Replay using only an exact opaque external capsule ID."""
        return _render(registry.replay(capsule_id))

    @mcp.tool()
    def inspect_athena_authority_evidence_adjunction(
        activation_packet_json: str, provider_evidence_json: str
    ) -> str:
        """Check packet/evidence structure without persisting or dispatching it."""
        return _render(
            registry.inspect_authority_evidence_adjunction(
                activation_packet_json, provider_evidence_json
            )
        )

    @mcp.resource("athena://replay-authority-ledger")
    def replay_authority_ledger_resource() -> str:
        """Expose the verified W16 append-only ledger."""
        return _render(
            {
                "status": registry.status(),
                "rows": [
                    registry.read_row(str(row["sequence"]))
                    for row in registry.rows
                ],
            }
        )

    @mcp.resource("athena://authority-evidence-adjunction")
    def authority_evidence_adjunction_resource() -> str:
        """Expose the nonpersisting, nondispatching authority ingress boundary."""
        return _render(registry.authority_status())
