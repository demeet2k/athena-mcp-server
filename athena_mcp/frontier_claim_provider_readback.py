from __future__ import annotations

import base64
import json
import re
from urllib import error, parse, request

from .frontier_claim import FrontierClaimRuntime
from . import frontier_claim_provider as provider

_CLAIM_KEYS = {
    "schema_version",
    "run_id",
    "node_id",
    "worker_role",
    "attempt",
    "policy_commit",
    "claimed_at",
    "lease_expires_at",
    "input_snapshot_digest",
    "production_authority",
}
_EVENT_KEYS = {
    "schema_version",
    "event_id",
    "sequence",
    "run_id",
    "event_type",
    "at",
    "node_id",
    "data",
}


def _preflight_exact(packet: dict) -> str | None:
    kind = str((packet or {}).get("kind") or "")
    content = (packet or {}).get("content")
    if not isinstance(content, dict):
        return "provider packet content must be an object"
    if kind == "CLAIM_V1":
        if set(content) != _CLAIM_KEYS:
            return "CLAIM_V1 content keys mismatch"
        if content.get("production_authority") != "HOLD":
            return "initial claim provider membrane permits HOLD authority only"
        if not isinstance(content.get("attempt"), int) or int(content["attempt"]) <= 0:
            return "claim attempt must be positive"
        digest = str(content.get("input_snapshot_digest") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            return "claim input_snapshot_digest must be lowercase SHA-256"
    elif kind == "EVENT_V1":
        if set(content) != _EVENT_KEYS:
            return "EVENT_V1 content keys mismatch"
        if not content.get("node_id"):
            return "claim membrane event requires node_id"
        if not isinstance(content.get("data"), dict):
            return "event data must be an object"
    return None


def _token(runtime: FrontierClaimRuntime) -> str | None:
    env = runtime.environ
    return env.get("ATHENA_GITHUB_TOKEN") or env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")


def _readback(client, *, repo: str, branch: str, packet: dict) -> dict:
    token = _token(client.runtime)
    if not token or not isinstance(repo, str) or repo.count("/") != 1:
        return {"status": "READBACK_HOLD", "reason": "provider identity unavailable"}
    owner, name = repo.split("/", 1)
    path = str(packet.get("path") or "")
    url = (
        f"{client.api_base}/repos/{parse.quote(owner, safe='')}/{parse.quote(name, safe='')}/contents/"
        f"{parse.quote(path, safe='/')}?{parse.urlencode({'ref': branch})}"
    )
    req = request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "athena-mcp-frontier-claim-v2",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with client.opener(req, timeout=15) as response:
            status = int(getattr(response, "status", 0) or 0)
            raw = response.read()
    except error.HTTPError as exc:
        if int(exc.code) == 404:
            return {"status": "ABSENT"}
        return {"status": "READBACK_HOLD", "http_status": int(exc.code)}
    except Exception as exc:
        return {"status": "READBACK_HOLD", "reason": type(exc).__name__}
    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
        encoded = str(payload.get("content") or "").replace("\n", "")
        decoded = base64.b64decode(encoded).decode("utf-8")
    except Exception:
        return {"status": "READBACK_HOLD", "http_status": status, "decode_error": True}
    return {
        "status": "PRESENT",
        "http_status": status,
        "content_text": decoded,
        "content_sha": payload.get("sha"),
    }


def install_frontier_claim_provider_readback(runtime_cls=FrontierClaimRuntime) -> None:
    """Add exact provider schema/authority checks and ambiguity readback.

    Compatibility note: the underlying saga historically recognizes provider
    statuses CREATED / EXISTS / PROVIDER_HOLD. An identical readback is therefore
    returned as CREATED for control-flow compatibility *with explicit standing*
    `CREATE_EFFECT_OBSERVED` and `provider_effect_newly_created=False`. Consumers
    must use the standing fields when distinguishing a newly-created effect from
    an idempotently observed existing effect.
    """

    if getattr(runtime_cls, "_athena_claim_provider_readback_v1_registered", False):
        return

    original_create = provider.GitHubContentsCreateProvider.create

    def create_with_readback(self, *, repo: str, branch: str, packet: dict) -> dict:
        preflight_error = _preflight_exact(packet)
        if preflight_error:
            return {
                "status": "PROVIDER_PACKET_REJECTED",
                "reason": preflight_error,
                "path": (packet or {}).get("path"),
                "kind": (packet or {}).get("kind"),
            }

        result = original_create(self, repo=repo, branch=branch, packet=packet)
        if result.get("status") == "CREATED":
            return {
                **result,
                "provider_effect_standing": "CREATED_NEW",
                "provider_effect_newly_created": True,
            }

        # HTTP-200 update-like semantics are a deliberate hard HOLD installed by
        # PG-001; readback may not launder that transport violation into success.
        if result.get("law") == "HTTP_200_UPDATE_SEMANTICS != CREATE_IF_ABSENT_SUCCESS":
            return result

        should_read = result.get("status") == "EXISTS" or result.get("status") == "PROVIDER_HOLD"
        if not should_read:
            return result

        observed = _readback(self, repo=repo, branch=branch, packet=packet)
        expected_text = str(packet.get("content_text") or "")
        if observed.get("status") == "PRESENT":
            if observed.get("content_text") == expected_text:
                return {
                    "status": "CREATED",
                    "http_status": result.get("http_status"),
                    "path": packet.get("path"),
                    "kind": packet.get("kind"),
                    "content_sha": observed.get("content_sha"),
                    "commit_sha": None,
                    "provider_effect_standing": "CREATE_EFFECT_OBSERVED",
                    "provider_effect_newly_created": False,
                    "resolution": result.get("reason") or f"HTTP_{result.get('http_status')}",
                    "law": "OBSERVED_IDENTICAL_PROVIDER_EFFECT != NEW_PROVIDER_CREATE",
                }
            return {
                "status": "EXISTS",
                "http_status": result.get("http_status"),
                "path": packet.get("path"),
                "kind": packet.get("kind"),
                "provider_effect_standing": "CREATE_COLLISION",
                "provider_effect_newly_created": False,
                "law": "EXISTING_DIFFERENT_FIXED_PATH_CONTENT != IDEMPOTENT_RETRY",
            }

        if observed.get("status") == "ABSENT":
            # A deterministic provider collision still proves the fixed path was
            # not createable at the attempted instant; retain lost-race semantics.
            if result.get("status") == "EXISTS":
                return {**result, "provider_effect_standing": "CREATE_COLLISION_UNREADABLE"}
            return {
                "status": "PROVIDER_HOLD",
                "path": packet.get("path"),
                "kind": packet.get("kind"),
                "provider_effect_standing": "AMBIGUOUS_CREATE_HOLD",
                "provider_effect_newly_created": False,
                "law": "TIMEOUT_OR_PROVIDER_ERROR != SAFE_TO_BLINDLY_RETRY",
            }

        # If a collision was already deterministic but readback itself failed,
        # preserving EXISTS is safer than pretending the caller won the race.
        if result.get("status") == "EXISTS":
            return {**result, "provider_effect_standing": "CREATE_COLLISION_UNREADABLE"}
        return {
            **result,
            "status": "PROVIDER_HOLD",
            "provider_effect_standing": "AMBIGUOUS_CREATE_HOLD",
            "provider_effect_newly_created": False,
            "readback_status": observed.get("status"),
            "law": "UNVERIFIED_PROVIDER_EFFECT != FAILURE_OR_SUCCESS",
        }

    provider.GitHubContentsCreateProvider.create = create_with_readback
    runtime_cls._athena_claim_provider_readback_v1_registered = True
