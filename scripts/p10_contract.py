"""Fail-closed contracts for the P10 persistent Athena MCP host."""

from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit


SCHEMA = "athena.persistent-host-target/v1"
STATE = "AUTHORIZED"
SOURCE_COMMIT = "52d0e2abf282aee5f8bf233521989bc2c8969989"
IMAGE_DIGEST = (
    "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
)
IMAGE = f"ghcr.io/demeet2k/athena-mcp-server@{IMAGE_DIGEST}"
TARGET_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
PERSISTENCE_CLASSES = {
    "managed-service",
    "orchestrated-service",
    "self-hosted-service",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def target_digest(value: dict[str, Any]) -> str:
    return f"sha256:{sha256(canonical_bytes(value)).hexdigest()}"


def validate_endpoint(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("endpoint must be a string")
    parts = urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or parts.path.rstrip("/") != "/mcp"
    ):
        raise ValueError(
            "endpoint must be an authority-only HTTPS URL ending exactly in /mcp"
        )
    return value.rstrip("/")


def validate_target(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("target must be a JSON object")
    if value.get("schema") != SCHEMA:
        raise ValueError(f"target schema must be {SCHEMA}")
    if value.get("state") != STATE:
        raise ValueError("target state must be AUTHORIZED")

    target_id = value.get("target_id")
    if not isinstance(target_id, str) or not TARGET_ID.fullmatch(target_id):
        raise ValueError("target_id must be a bounded lowercase identifier")
    validate_endpoint(value.get("endpoint"))

    if value.get("image") != IMAGE:
        raise ValueError("target image must equal the selected immutable P09 digest")
    if value.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("target source_commit must equal the attested P08 source")

    authorization = value.get("authorization")
    if not isinstance(authorization, dict):
        raise ValueError("authorization must be an object")
    for field in ("ref", "actor", "authorized_at"):
        if not isinstance(authorization.get(field), str) or not authorization[field]:
            raise ValueError(f"authorization.{field} is required")

    persistence = value.get("persistence")
    if not isinstance(persistence, dict):
        raise ValueError("persistence must be an object")
    if persistence.get("class") not in PERSISTENCE_CLASSES:
        raise ValueError("persistence.class is not an admitted persistent class")
    if persistence.get("restart_policy") != "unless-stopped":
        raise ValueError("persistence.restart_policy must be unless-stopped")
    if persistence.get("ephemeral") is not False:
        raise ValueError("persistent target cannot be marked ephemeral")

    tls = value.get("tls")
    if not isinstance(tls, dict):
        raise ValueError("tls must be an object")
    if tls.get("required") is not True or tls.get("minimum_version") != "1.2":
        raise ValueError("TLS must be required with minimum version 1.2")

    secret = value.get("secret")
    if not isinstance(secret, dict):
        raise ValueError("secret must be an object")
    if secret.get("environment") != "ATHENA_MCP_BEARER_TOKEN":
        raise ValueError("secret environment is not the admitted bearer carrier")
    if secret.get("minimum_length") != 32:
        raise ValueError("bearer secret minimum length must be 32")
    if secret.get("record_value") is not False:
        raise ValueError("target must forbid recording bearer secret material")
    if not isinstance(secret.get("provider_ref"), str) or not secret["provider_ref"]:
        raise ValueError("secret.provider_ref is required")

    authority = value.get("authority")
    if not isinstance(authority, dict):
        raise ValueError("authority must be an object")
    if authority.get("runtime_can_promote") is not False:
        raise ValueError("runtime cannot promote")
    if authority.get("promotion_claimed") is not False:
        raise ValueError("target cannot claim promotion")
    if authority.get("ic10_required") is not True:
        raise ValueError("target must preserve IC10 authority")
    return value


def validate_token(value: str | None) -> str:
    if value is None or len(value) < 32:
        raise ValueError("ATHENA_MCP_BEARER_TOKEN must contain at least 32 characters")
    return value
