"""Fail-closed contracts for the P10 persistent Athena MCP host."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import ipaddress
import json
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit


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
TARGET_FIELDS = {
    "schema",
    "state",
    "target_id",
    "endpoint",
    "image",
    "source_commit",
    "authorization",
    "persistence",
    "tls",
    "secret",
    "authority",
}
AUTHORIZATION_FIELDS = {"ref", "actor", "authorized_at"}
PERSISTENCE_FIELDS = {"class", "restart_policy", "ephemeral"}
TLS_FIELDS = {"required", "minimum_version"}
SECRET_FIELDS = {
    "environment",
    "provider_ref",
    "minimum_length",
    "record_value",
}
AUTHORITY_FIELDS = {
    "runtime_can_promote",
    "promotion_claimed",
    "ic10_required",
}
BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "host.docker.internal",
    "gateway.docker.internal",
}
BLOCKED_SUFFIXES = (".localhost", ".local", ".test", ".invalid", ".example")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def target_digest(value: dict[str, Any]) -> str:
    return f"sha256:{sha256(canonical_bytes(value)).hexdigest()}"


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
    if _host_is_ephemeral_or_local(parts.hostname):
        raise ValueError(
            "persistent endpoint cannot be localhost, test-only, or runner-local"
        )
    return urlunsplit((parts.scheme, parts.netloc, "/mcp", "", ""))


def health_url(endpoint: str) -> str:
    parts = urlsplit(validate_endpoint(endpoint))
    return urlunsplit((parts.scheme, parts.netloc, "/healthz", "", ""))


def validate_target(value: Any) -> dict[str, Any]:
    value = _exact_object(value, TARGET_FIELDS, "target")
    if value.get("schema") != SCHEMA:
        raise ValueError(f"target schema must be {SCHEMA}")
    if value.get("state") != STATE:
        raise ValueError("target state must be AUTHORIZED")

    target_id = value.get("target_id")
    if not isinstance(target_id, str) or not TARGET_ID.fullmatch(target_id):
        raise ValueError("target_id must be a bounded lowercase identifier")
    endpoint = validate_endpoint(value.get("endpoint"))

    if value.get("image") != IMAGE:
        raise ValueError("target image must equal the selected immutable P09 digest")
    if value.get("source_commit") != SOURCE_COMMIT:
        raise ValueError("target source_commit must equal the attested P08 source")

    authorization = _exact_object(
        value.get("authorization"),
        AUTHORIZATION_FIELDS,
        "authorization",
    )
    normalized_authorization = {
        "ref": _bounded_text(authorization.get("ref"), "authorization.ref"),
        "actor": _bounded_text(
            authorization.get("actor"),
            "authorization.actor",
        ),
        "authorized_at": _timestamp(
            authorization.get("authorized_at"),
            "authorization.authorized_at",
        ),
    }

    persistence = _exact_object(
        value.get("persistence"),
        PERSISTENCE_FIELDS,
        "persistence",
    )
    if persistence.get("class") not in PERSISTENCE_CLASSES:
        raise ValueError("persistence.class is not an admitted persistent class")
    if persistence.get("restart_policy") != "unless-stopped":
        raise ValueError("persistence.restart_policy must be unless-stopped")
    if persistence.get("ephemeral") is not False:
        raise ValueError("persistent target cannot be marked ephemeral")

    tls = _exact_object(value.get("tls"), TLS_FIELDS, "tls")
    if tls.get("required") is not True or tls.get("minimum_version") != "1.2":
        raise ValueError("TLS must be required with minimum version 1.2")

    secret = _exact_object(value.get("secret"), SECRET_FIELDS, "secret")
    if secret.get("environment") != "ATHENA_MCP_BEARER_TOKEN":
        raise ValueError("secret environment is not the admitted bearer carrier")
    if secret.get("minimum_length") != 32:
        raise ValueError("bearer secret minimum length must be 32")
    if secret.get("record_value") is not False:
        raise ValueError("target must forbid recording bearer secret material")
    provider_ref = _bounded_text(
        secret.get("provider_ref"),
        "secret.provider_ref",
    )

    authority = _exact_object(
        value.get("authority"),
        AUTHORITY_FIELDS,
        "authority",
    )
    if authority.get("runtime_can_promote") is not False:
        raise ValueError("runtime cannot promote")
    if authority.get("promotion_claimed") is not False:
        raise ValueError("target cannot claim promotion")
    if authority.get("ic10_required") is not True:
        raise ValueError("target must preserve IC10 authority")
    return {
        **value,
        "endpoint": endpoint,
        "authorization": normalized_authorization,
        "persistence": dict(persistence),
        "tls": dict(tls),
        "secret": {**secret, "provider_ref": provider_ref},
        "authority": dict(authority),
    }


def validate_token(value: str | None) -> str:
    if value is None or len(value) < 32:
        raise ValueError("ATHENA_MCP_BEARER_TOKEN must contain at least 32 characters")
    return value
