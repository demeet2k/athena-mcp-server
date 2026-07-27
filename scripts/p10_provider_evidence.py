"""Strict, secret-free provider evidence for the canonical P10 host capsule."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SCHEMA = "athena.provider-deployment-evidence/v1"
SOURCE_COMMIT = "52d0e2abf282aee5f8bf233521989bc2c8969989"
RUNTIME_P09_HEAD = "9731b24c5963b75821b381b4562aa51baa55196c"
IMAGE_DIGEST = (
    "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
)
IMAGE = f"ghcr.io/demeet2k/athena-mcp-server@{IMAGE_DIGEST}"
ALLOWED_FIELDS = {
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


def _required_text(value: dict[str, Any], key: str) -> str:
    candidate = value.get(key)
    if not isinstance(candidate, str) or not candidate.strip():
        raise ValueError(f"provider evidence requires non-empty {key}")
    return candidate.strip()


def _https_url(value: str, field: str, *, exact_mcp: bool = False) -> str:
    parts = urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
    ):
        raise ValueError(f"{field} must be a secret-free absolute HTTPS URL")
    if exact_mcp and parts.path.rstrip("/") != "/mcp":
        raise ValueError(f"{field} must end exactly in /mcp")
    return value.rstrip("/")


def _timestamp(value: str) -> str:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError("deployment_observed_at must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise ValueError("deployment_observed_at must include a timezone")
    return value


def validate_provider_evidence(
    value: Any, target: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("provider evidence must be a JSON object")
    unknown = set(value) - ALLOWED_FIELDS
    missing = ALLOWED_FIELDS - set(value)
    if unknown:
        raise ValueError(
            "provider evidence contains forbidden or unknown fields: "
            + ", ".join(sorted(unknown))
        )
    if missing:
        raise ValueError(
            "provider evidence is missing required fields: "
            + ", ".join(sorted(missing))
        )
    if value.get("schema") != SCHEMA:
        raise ValueError(f"provider evidence schema must be {SCHEMA}")

    endpoint = _https_url(_required_text(value, "endpoint"), "endpoint", exact_mcp=True)
    target_endpoint = _https_url(target.get("endpoint"), "target.endpoint", exact_mcp=True)
    if endpoint != target_endpoint:
        raise ValueError("provider endpoint must equal the authorized target endpoint")
    if _required_text(value, "target_id") != target.get("target_id"):
        raise ValueError("provider target_id must equal the authorized target")
    if _required_text(value, "authorization_ref") != target.get("authorization", {}).get("ref"):
        raise ValueError("provider authorization_ref must equal the target authorization")
    if _required_text(value, "secret_store_ref") != target.get("secret", {}).get("provider_ref"):
        raise ValueError("provider secret_store_ref must equal the target secret reference")
    if _required_text(value, "deployed_image") != IMAGE or target.get("image") != IMAGE:
        raise ValueError("provider evidence must select the exact P09 image")
    if _required_text(value, "image_digest") != IMAGE_DIGEST:
        raise ValueError("provider evidence must pin the exact image digest")
    if _required_text(value, "source_commit") != SOURCE_COMMIT:
        raise ValueError("provider evidence must pin the frozen source commit")
    if _required_text(value, "runtime_p09_head") != RUNTIME_P09_HEAD:
        raise ValueError("provider evidence must pin the P09 runtime head")
    if value.get("persistent_service") is not True:
        raise ValueError("provider evidence must identify a persistent service")
    if value.get("secret_material_recorded") is not False:
        raise ValueError("provider evidence must not record secret material")

    return {
        "schema": SCHEMA,
        "provider_id": _required_text(value, "provider_id"),
        "provider_account_scope": _required_text(value, "provider_account_scope"),
        "deployment_id": _required_text(value, "deployment_id"),
        "target_id": target["target_id"],
        "authorization_ref": target["authorization"]["ref"],
        "deployed_image": IMAGE,
        "image_digest": IMAGE_DIGEST,
        "source_commit": SOURCE_COMMIT,
        "runtime_p09_head": RUNTIME_P09_HEAD,
        "endpoint": endpoint,
        "persistent_service": True,
        "deployment_observed_at": _timestamp(
            _required_text(value, "deployment_observed_at")
        ),
        "secret_store_ref": target["secret"]["provider_ref"],
        "secret_material_recorded": False,
        "evidence_url": _https_url(
            _required_text(value, "evidence_url"), "evidence_url"
        ),
    }


def load_provider_evidence(
    path: Path, target: dict[str, Any]
) -> dict[str, Any]:
    return validate_provider_evidence(
        json.loads(path.read_text(encoding="utf-8")), target
    )
