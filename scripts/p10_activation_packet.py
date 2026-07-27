"""Compile a strict, secret-free P10 live-witness activation handoff."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from scripts.p10_contract import (
    IMAGE,
    SOURCE_COMMIT,
    canonical_bytes,
    target_digest,
    validate_target,
)
from scripts.p10_provider_evidence import (
    IMAGE_DIGEST,
    RUNTIME_P09_HEAD,
    validate_provider_evidence,
)


SCHEMA = "athena.persistent-host-activation-packet/v1"
HANDOFF_SCHEMA = "athena.persistent-host-witness-handoff/v1"
AUTHORIZED_STATE = "AUTHORIZED_FOR_LIVE_WITNESS"
UNRESOLVED_STATE = "UNRESOLVED"
CANONICAL_HARDENING_HEAD = "b4e24de38788ecdf30f43514ece279d1270b998b"
WITNESS_ENVIRONMENT = "p10-persistent-host"
WITNESS_SECRET_NAME = "ATHENA_MCP_BEARER_TOKEN"
SAMPLE_COUNT = 3
INTERVAL_SECONDS = 20
MINIMUM_SPAN_SECONDS = 40

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


def _exact_object(
    value: Any,
    fields: set[str],
    path: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        raise ValueError(
            f"{path} contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if missing:
        raise ValueError(
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
        raise ValueError(f"{path} must be bounded non-empty text")
    return value.strip()


def _timestamp(value: Any, path: str) -> str:
    candidate = _text(value, path)
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


def _validate_immutable_lineage(value: dict[str, Any]) -> None:
    if value.get("canonical_hardening_head") != CANONICAL_HARDENING_HEAD:
        raise ValueError("activation packet must pin the canonical hardening head")
    if value.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("activation packet must pin the frozen source commit")
    if value.get("runtime_p09_head") != RUNTIME_P09_HEAD:
        raise ValueError("activation packet must pin the P09 runtime head")
    if value.get("image") != IMAGE:
        raise ValueError("activation packet must pin the exact P09 image digest")


def _validate_witness_plan(value: Any) -> dict[str, Any]:
    witness = _exact_object(value, WITNESS_FIELDS, "witness")
    expected = {
        "environment": WITNESS_ENVIRONMENT,
        "secret_name": WITNESS_SECRET_NAME,
        "sample_count": SAMPLE_COUNT,
        "interval_seconds": INTERVAL_SECONDS,
        "minimum_span_seconds": MINIMUM_SPAN_SECONDS,
    }
    if witness != expected:
        raise ValueError("activation packet must preserve the exact witness plan")
    return witness


def _validate_nonpromotion_authority(
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
        raise ValueError("activation packet crosses its authority boundary")
    return authority


def validate_unresolved_template(value: Any) -> dict[str, Any]:
    packet = _exact_object(value, TOP_LEVEL_FIELDS, "activation packet")
    if packet.get("schema") != SCHEMA or packet.get("state") != UNRESOLVED_STATE:
        raise ValueError("unresolved template has the wrong schema or state")
    _validate_immutable_lineage(packet)
    provider = _exact_object(packet.get("provider"), PROVIDER_FIELDS, "provider")
    target = _exact_object(packet.get("target"), TARGET_FIELDS, "target")
    authorization = _exact_object(
        packet.get("authorization"),
        AUTHORIZATION_FIELDS,
        "authorization",
    )
    if any(value is not None for value in provider.values()):
        raise ValueError("unresolved provider fields must remain null")
    if any(value is not None for value in target.values()):
        raise ValueError("unresolved target fields must remain null")
    if any(value is not None for value in authorization.values()):
        raise ValueError("unresolved authorization fields must remain null")
    _validate_witness_plan(packet.get("witness"))
    _validate_nonpromotion_authority(
        packet.get("authority"),
        live_witness_authorized=False,
    )
    if packet.get("secret_material_recorded") is not False:
        raise ValueError("activation template must not record secret material")
    return packet


def validate_activation_packet(value: Any) -> dict[str, Any]:
    packet = _exact_object(value, TOP_LEVEL_FIELDS, "activation packet")
    if packet.get("schema") != SCHEMA:
        raise ValueError(f"activation packet schema must be {SCHEMA}")
    if packet.get("state") != AUTHORIZED_STATE:
        raise ValueError(
            f"activation packet state must be {AUTHORIZED_STATE}"
        )
    _validate_immutable_lineage(packet)
    provider = _exact_object(packet.get("provider"), PROVIDER_FIELDS, "provider")
    target = _exact_object(packet.get("target"), TARGET_FIELDS, "target")
    authorization = _exact_object(
        packet.get("authorization"),
        AUTHORIZATION_FIELDS,
        "authorization",
    )
    normalized = {
        **packet,
        "provider": {
            "id": _text(provider.get("id"), "provider.id"),
            "account_scope": _text(
                provider.get("account_scope"),
                "provider.account_scope",
            ),
            "deployment_id": _text(
                provider.get("deployment_id"),
                "provider.deployment_id",
            ),
            "deployment_observed_at": _timestamp(
                provider.get("deployment_observed_at"),
                "provider.deployment_observed_at",
            ),
            "evidence_url": _text(
                provider.get("evidence_url"),
                "provider.evidence_url",
            ),
        },
        "target": {
            "id": _text(target.get("id"), "target.id"),
            "endpoint": _text(target.get("endpoint"), "target.endpoint"),
            "persistence_class": _text(
                target.get("persistence_class"),
                "target.persistence_class",
            ),
            "secret_store_ref": _text(
                target.get("secret_store_ref"),
                "target.secret_store_ref",
            ),
        },
        "authorization": {
            "ref": _text(authorization.get("ref"), "authorization.ref"),
            "actor": _text(
                authorization.get("actor"),
                "authorization.actor",
            ),
            "authorized_at": _timestamp(
                authorization.get("authorized_at"),
                "authorization.authorized_at",
            ),
        },
        "witness": _validate_witness_plan(packet.get("witness")),
        "authority": _validate_nonpromotion_authority(
            packet.get("authority"),
            live_witness_authorized=True,
        ),
    }
    if packet.get("secret_material_recorded") is not False:
        raise ValueError("activation packet must not record secret material")
    if _parsed_timestamp(
        normalized["authorization"]["authorized_at"]
    ) > _parsed_timestamp(normalized["provider"]["deployment_observed_at"]):
        raise ValueError(
            "deployment observation cannot precede authorization"
        )
    return normalized


def compile_activation_packet(
    value: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    packet = validate_activation_packet(value)
    provider = packet["provider"]
    requested_target = packet["target"]
    authorization = packet["authorization"]
    target = validate_target(
        {
            "schema": "athena.persistent-host-target/v1",
            "state": "AUTHORIZED",
            "target_id": requested_target["id"],
            "endpoint": requested_target["endpoint"],
            "image": IMAGE,
            "source_commit": SOURCE_COMMIT,
            "authorization": {
                "ref": authorization["ref"],
                "actor": authorization["actor"],
                "authorized_at": authorization["authorized_at"],
            },
            "persistence": {
                "class": requested_target["persistence_class"],
                "restart_policy": "unless-stopped",
                "ephemeral": False,
            },
            "tls": {
                "required": True,
                "minimum_version": "1.2",
            },
            "secret": {
                "environment": "ATHENA_MCP_BEARER_TOKEN",
                "provider_ref": requested_target["secret_store_ref"],
                "minimum_length": 32,
                "record_value": False,
            },
            "authority": {
                "runtime_can_promote": False,
                "promotion_claimed": False,
                "ic10_required": True,
            },
        }
    )
    evidence = validate_provider_evidence(
        {
            "schema": "athena.provider-deployment-evidence/v1",
            "provider_id": provider["id"],
            "provider_account_scope": provider["account_scope"],
            "deployment_id": provider["deployment_id"],
            "target_id": target["target_id"],
            "authorization_ref": authorization["ref"],
            "deployed_image": IMAGE,
            "image_digest": IMAGE_DIGEST,
            "source_commit": SOURCE_COMMIT,
            "runtime_p09_head": RUNTIME_P09_HEAD,
            "endpoint": target["endpoint"],
            "persistent_service": True,
            "deployment_observed_at": provider["deployment_observed_at"],
            "secret_store_ref": target["secret"]["provider_ref"],
            "secret_material_recorded": False,
            "evidence_url": provider["evidence_url"],
        },
        target,
    )
    body = {
        "schema": HANDOFF_SCHEMA,
        "phase": "P10",
        "verdict": "PASS_AUTHORIZED_WITNESS_HANDOFF_NOT_EXECUTED",
        "canonical_hardening_head": CANONICAL_HARDENING_HEAD,
        "activation_packet_digest": (
            "sha256:" + sha256(canonical_bytes(packet)).hexdigest()
        ),
        "target_digest": target_digest(target),
        "target": target,
        "provider_evidence": evidence,
        "witness_plan": packet["witness"],
        "persistent_endpoint_witnessed": False,
        "persistent_witness": None,
        "secret_material_recorded": False,
        "query_contract": {
            "return_plan": [
                "edge.runtime-to-control",
                "edge.control-to-q-shrink",
            ],
            "explicit_v1_fallback": "athena-108d-v1",
        },
        "authority": {
            "handoff_compiled": True,
            "handoff_is_live_witness": False,
            "runtime_can_promote": False,
            "promotion_claimed": False,
            "merge_claimed": False,
            "ic10_required": True,
        },
        "next_gate": (
            "Use the protected p10-persistent-host environment to execute "
            "the exact three-sample live witness, then admit that witness "
            "through the control plane before IC10 considers promotion."
        ),
    }
    receipt = {
        "receipt_id": (
            "p10-handoff:sha256:"
            + sha256(canonical_bytes(body)).hexdigest()
        ),
        **body,
    }
    return target, evidence, receipt


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--check-template", action="store_true")
    parser.add_argument("--target-out", type=Path)
    parser.add_argument("--evidence-out", type=Path)
    parser.add_argument("--receipt-out", type=Path)
    arguments = parser.parse_args()
    value = json.loads(arguments.packet.read_text(encoding="utf-8"))
    if arguments.check_template:
        validate_unresolved_template(value)
        print("PASS_UNRESOLVED_ACTIVATION_TEMPLATE")
        return 0
    if not all(
        (arguments.target_out, arguments.evidence_out, arguments.receipt_out)
    ):
        parser.error(
            "--target-out, --evidence-out, and --receipt-out are required"
        )
    target, evidence, receipt = compile_activation_packet(value)
    _write_json(arguments.target_out, target)
    _write_json(arguments.evidence_out, evidence)
    _write_json(arguments.receipt_out, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
