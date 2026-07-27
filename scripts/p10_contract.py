"""Fail-closed P10 host-contract and receipt primitives.

This module contains no provider client and performs no deployment.  It binds
every later P10 action to the already-published P09 digest and keeps authority,
target, secret-provisioning, deployment, witness, admission, and promotion
states separate.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import ipaddress
import json
import os
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit


SCHEMA = "athena.p10-host-contract/v1"
PHASE = "P10"
SEED = (
    "KC144.MYC.SKELETON.P10::"
    "AUTHORIZED-HTTPS-ENDPOINT-AND-PERSISTENT-WITNESS"
)
PREPARED_OUTCOME = "READY_AWAITING_AUTHORIZED_TARGET"
WITNESS_OUTCOME = "PASS_PERSISTENT_HTTPS_WITNESS"
PREPARED_STATE = "PREPARED_NOT_DEPLOYED"
AUTHORIZED_STATE = "AUTHORIZED_TARGET_CONFIGURED"
TOKEN_ENV = "ATHENA_MCP_BEARER_TOKEN"
MINIMUM_TOKEN_LENGTH = 32

REPOSITORY = "demeet2k/athena-mcp-server"
P09_HEAD = "9731b24c5963b75821b381b4562aa51baa55196c"
SOURCE_COMMIT = "52d0e2abf282aee5f8bf233521989bc2c8969989"
IMAGE_DIGEST = (
    "sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2"
)
IMAGE_REFERENCE = f"ghcr.io/demeet2k/athena-mcp-server@{IMAGE_DIGEST}"
PUBLICATION_RECEIPT = (
    "oci-publication:sha256:"
    "65caf0c574b3981e8c499ff075dda5ffc1512517e413fcdb0bf424fe49432a0d"
)
CONTAINER_PORT = 8080
CONTAINER_UID = 10001
MCP_PATH = "/mcp"
HEALTH_PATH = "/healthz"
PERSISTENCE_CLASSES = {
    "managed-container-service",
    "orchestrated-container-service",
    "self-hosted-container-service",
}
BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "host.docker.internal",
    "gateway.docker.internal",
}
BLOCKED_SUFFIXES = (".localhost", ".local", ".test", ".invalid", ".example")
SECRET_ARGUMENT_MARKERS = (
    "--token",
    "--bearer-token",
    "--authorization",
    "authorization:",
    "authorization=",
)


class ContractError(ValueError):
    """Raised when a P10 contract attempts to cross a fail-closed boundary."""


def canonical_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for hashes and secret checks."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def content_digest(value: Any) -> str:
    return f"sha256:{sha256(canonical_bytes(value)).hexdigest()}"


def content_addressed_receipt(prefix: str, body: dict[str, Any]) -> dict[str, Any]:
    return {"receipt_id": f"{prefix}:sha256:{sha256(canonical_bytes(body)).hexdigest()}", **body}


def load_contract(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError("host contract must be a JSON object")
    return value


def _require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{field} must be an object")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def _require_null_fields(value: dict[str, Any], fields: Iterable[str], prefix: str) -> None:
    for field in fields:
        if value.get(field) is not None:
            raise ContractError(f"{prefix}.{field} must remain null before authorization")


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


def validate_endpoint(value: Any, *, persistent_required: bool = True) -> str:
    if not isinstance(value, str):
        raise ContractError("external MCP endpoint must be a string")
    parsed = urlsplit(value)
    if parsed.scheme != "https":
        raise ContractError("external MCP endpoint must use HTTPS")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ContractError("external MCP endpoint must contain only a host authority")
    if parsed.query or parsed.fragment or parsed.path.rstrip("/") != MCP_PATH:
        raise ContractError("external MCP endpoint must end exactly in /mcp")
    if persistent_required and _host_is_ephemeral_or_local(parsed.hostname):
        raise ContractError(
            "persistent witness endpoint cannot be localhost, test-only, or runner-local"
        )
    return urlunsplit(
        (parsed.scheme, parsed.netloc, MCP_PATH, "", "")
    )


def health_url(endpoint: str) -> str:
    parsed = urlsplit(validate_endpoint(endpoint))
    return urlunsplit((parsed.scheme, parsed.netloc, HEALTH_PATH, "", ""))


def validate_token_from_environment(
    token: str | None,
    *,
    argv: Iterable[str] = (),
) -> str:
    if token is None or len(token) < MINIMUM_TOKEN_LENGTH:
        raise ContractError(
            f"{TOKEN_ENV} must be present in the environment with at least "
            f"{MINIMUM_TOKEN_LENGTH} characters"
        )
    lowered_arguments = [argument.lower() for argument in argv]
    if any(
        marker in argument
        for argument in lowered_arguments
        for marker in SECRET_ARGUMENT_MARKERS
    ):
        raise ContractError("bearer tokens and authorization headers are forbidden in arguments")
    if any(token in argument for argument in argv):
        raise ContractError("bearer token value is forbidden in process arguments")
    return token


def validate_successful_witness(value: Any) -> dict[str, Any]:
    witness = _require_object(value, "persistent_witness")
    if witness.get("successful") is not True:
        raise ContractError("persistent witness must be explicitly successful")
    if witness.get("verdict") != WITNESS_OUTCOME:
        raise ContractError(f"persistent witness verdict must be {WITNESS_OUTCOME}")
    _require_text(witness.get("receipt_id"), "persistent_witness.receipt_id")
    if witness.get("source_commit") != SOURCE_COMMIT:
        raise ContractError("persistent witness source commit does not match P09")
    if witness.get("image_reference") != IMAGE_REFERENCE:
        raise ContractError("persistent witness image does not match the immutable digest")
    if witness.get("promotion_ready") is not False:
        raise ContractError("persistent witness cannot mark promotion_ready true")
    return witness


def validate_contract(
    contract: dict[str, Any],
    *,
    require_authorized_target: bool,
    token: str | None = None,
    argv: Iterable[str] = (),
) -> dict[str, Any]:
    if contract.get("schema") != SCHEMA or contract.get("phase") != PHASE:
        raise ContractError("host contract schema or phase is not admitted")
    if contract.get("seed") != SEED:
        raise ContractError("host contract successor seed is not the canonical P10 seed")
    if contract.get("repository") != REPOSITORY:
        raise ContractError("runtime repository does not match the publication authority")
    if contract.get("p09_predecessor_head") != P09_HEAD:
        raise ContractError("P10 contract does not descend from the canonical P09 head")
    if contract.get("source_commit") != SOURCE_COMMIT:
        raise ContractError("source commit does not match the frozen P08 runtime source")

    image = _require_object(contract.get("image"), "image")
    if image.get("reference") != IMAGE_REFERENCE:
        raise ContractError("image reference must use the exact immutable P09 digest")
    if image.get("digest") != IMAGE_DIGEST:
        raise ContractError("image digest does not match the P09 publication")
    if image.get("publication_receipt") != PUBLICATION_RECEIPT:
        raise ContractError("image publication receipt does not match P09")
    if image.get("mutable_tags_authoritative") is not False:
        raise ContractError("mutable image tags cannot be deployment authority")
    if image.get("container_port") != CONTAINER_PORT:
        raise ContractError("container port must remain 8080")
    if image.get("non_root_uid") != CONTAINER_UID:
        raise ContractError("container must run as non-root UID 10001")

    network = _require_object(contract.get("network"), "network")
    if network.get("health_path") != HEALTH_PATH or network.get("mcp_path") != MCP_PATH:
        raise ContractError("network paths do not match the frozen runtime")
    tls = _require_object(network.get("tls_termination"), "network.tls_termination")
    if (
        tls.get("required") is not True
        or tls.get("minimum_version") != "1.2"
        or tls.get("redirects_allowed") is not False
        or tls.get("downgrade_allowed") is not False
    ):
        raise ContractError("TLS termination must reject redirects and downgrade")
    forwarding = _require_object(network.get("forwarding"), "network.forwarding")
    if (
        forwarding.get("upstream_scheme") != "http"
        or forwarding.get("upstream_port") != CONTAINER_PORT
        or forwarding.get("preserve_host") is not True
        or forwarding.get("forwarded_proto") != "https"
    ):
        raise ContractError("TLS proxy forwarding contract is not admitted")

    authentication = _require_object(contract.get("authentication"), "authentication")
    if authentication.get("scheme") != "bearer":
        raise ContractError("authentication scheme must be bearer")
    if authentication.get("environment") != TOKEN_ENV:
        raise ContractError("bearer token must use ATHENA_MCP_BEARER_TOKEN")
    if authentication.get("minimum_length") != MINIMUM_TOKEN_LENGTH:
        raise ContractError("bearer token minimum length must be 32")
    if (
        authentication.get("environment_only") is not True
        or authentication.get("command_line_allowed") is not False
        or authentication.get("record_value") is not False
    ):
        raise ContractError("bearer token carrier must remain environment-only and secret-free")

    target = _require_object(contract.get("target"), "target")
    authority = _require_object(contract.get("authority"), "authority")
    witness = _require_object(contract.get("persistent_witness"), "persistent_witness")
    rollback = _require_object(contract.get("rollback"), "rollback")
    if (
        rollback.get("class") != "immutable-digest-selection"
        or rollback.get("selected_image") != IMAGE_REFERENCE
        or rollback.get("v1_fallback") != "athena-108d-v1"
    ):
        raise ContractError("rollback must select the immutable digest or explicit v1 fallback")
    if authority.get("promotion_ready") is not False:
        raise ContractError("promotion_ready must remain false")
    if authority.get("promotion_claimed") is not False:
        raise ContractError("runtime contract cannot claim promotion")
    if authority.get("merge_claimed") is not False:
        raise ContractError("runtime contract cannot claim merge")
    if authority.get("ic10_promotion_required") is not True:
        raise ContractError("IC10 must remain the promotion authority")
    if authority.get("deployment_claimed") is True:
        validate_successful_witness(witness)

    if require_authorized_target:
        if contract.get("deployment_state") != AUTHORIZED_STATE:
            raise ContractError("authorized preflight requires AUTHORIZED_TARGET_CONFIGURED")
        endpoint = validate_endpoint(network.get("external_mcp_endpoint"))
        if network.get("external_health_endpoint") != health_url(endpoint):
            raise ContractError("external health endpoint must share the exact HTTPS authority")
        for field in (
            "provider_id",
            "provider_account_scope",
            "deployment_id",
            "persistence_class",
            "authorization_ref",
            "authorized_by",
            "authorized_at",
        ):
            _require_text(target.get(field), f"target.{field}")
        if target.get("persistence_class") not in PERSISTENCE_CLASSES:
            raise ContractError("target persistence class is not admitted")
        if target.get("authorized") is not True or target.get("ephemeral") is not False:
            raise ContractError("target must be explicitly authorized and non-ephemeral")
        _require_text(authentication.get("secret_store_ref"), "authentication.secret_store_ref")
        if authentication.get("bearer_secret_provisioned") is not True:
            raise ContractError("authorized target requires bearer secret provisioning")
        validate_token_from_environment(token, argv=argv)
        if witness.get("successful") is not False or witness.get("receipt_id") is not None:
            raise ContractError("preflight target cannot contain a fabricated witness")
        if authority.get("authorized_target_selected") is not True:
            raise ContractError("authorized target selection must be explicit")
        if authority.get("deployment_claimed") is not False:
            raise ContractError("preflight cannot claim deployment before a successful witness")
    else:
        if contract.get("deployment_state") != PREPARED_STATE:
            raise ContractError("prepared contract must remain PREPARED_NOT_DEPLOYED")
        if contract.get("outcome") != PREPARED_OUTCOME:
            raise ContractError(f"prepared outcome must be {PREPARED_OUTCOME}")
        _require_null_fields(
            target,
            (
                "provider_id",
                "provider_account_scope",
                "deployment_id",
                "persistence_class",
                "authorization_ref",
                "authorized_by",
                "authorized_at",
            ),
            "target",
        )
        if target.get("authorized") is not False or target.get("ephemeral") is not None:
            raise ContractError("prepared target cannot imply authorization or persistence")
        _require_null_fields(
            network,
            ("external_mcp_endpoint", "external_health_endpoint"),
            "network",
        )
        if authentication.get("secret_store_ref") is not None:
            raise ContractError("prepared contract secret-store reference must remain null")
        if authentication.get("bearer_secret_provisioned") is not False:
            raise ContractError("prepared contract cannot claim secret provisioning")
        if any(value is not None for key, value in witness.items() if key != "successful"):
            raise ContractError("prepared contract persistent witness fields must remain null")
        if witness.get("successful") is not False:
            raise ContractError("prepared contract cannot claim a successful witness")
        if authority.get("authorized_target_selected") is not False:
            raise ContractError("prepared contract cannot select a target")
        if authority.get("deployment_claimed") is not False:
            raise ContractError("prepared contract cannot claim deployment")
    return contract


def materialize_authorized_contract(
    prepared: dict[str, Any],
    *,
    endpoint: str,
    provider_id: str,
    provider_account_scope: str,
    deployment_id: str,
    persistence_class: str,
    authorization_ref: str,
    authorized_by: str,
    authorized_at: str,
    secret_store_ref: str,
) -> dict[str, Any]:
    validate_contract(prepared, require_authorized_target=False)
    value = deepcopy(prepared)
    normalized_endpoint = validate_endpoint(endpoint)
    value["deployment_state"] = AUTHORIZED_STATE
    value["outcome"] = "READY_TO_PROBE_AUTHORIZED_TARGET"
    value["network"]["external_mcp_endpoint"] = normalized_endpoint
    value["network"]["external_health_endpoint"] = health_url(normalized_endpoint)
    value["authentication"]["secret_store_ref"] = _require_text(
        secret_store_ref, "secret_store_ref"
    )
    value["authentication"]["bearer_secret_provisioned"] = True
    value["target"].update(
        {
            "provider_id": _require_text(provider_id, "provider_id"),
            "provider_account_scope": _require_text(
                provider_account_scope, "provider_account_scope"
            ),
            "deployment_id": _require_text(deployment_id, "deployment_id"),
            "persistence_class": _require_text(
                persistence_class, "persistence_class"
            ),
            "authorization_ref": _require_text(
                authorization_ref, "authorization_ref"
            ),
            "authorized_by": _require_text(authorized_by, "authorized_by"),
            "authorized_at": _require_text(authorized_at, "authorized_at"),
            "authorized": True,
            "ephemeral": False,
        }
    )
    value["authority"]["authorized_target_selected"] = True
    return value


def secret_free(value: Any, token: str) -> bool:
    return token not in canonical_bytes(value).decode("utf-8")


def environment_target_fields() -> dict[str, str]:
    names = {
        "endpoint": "ATHENA_P10_ENDPOINT",
        "provider_id": "ATHENA_P10_PROVIDER_ID",
        "provider_account_scope": "ATHENA_P10_PROVIDER_ACCOUNT_SCOPE",
        "deployment_id": "ATHENA_P10_DEPLOYMENT_ID",
        "persistence_class": "ATHENA_P10_PERSISTENCE_CLASS",
        "authorization_ref": "ATHENA_P10_AUTHORIZATION_REF",
        "authorized_by": "ATHENA_P10_AUTHORIZED_BY",
        "authorized_at": "ATHENA_P10_AUTHORIZED_AT",
        "secret_store_ref": "ATHENA_P10_SECRET_STORE_REF",
    }
    return {field: os.environ.get(name, "") for field, name in names.items()}
