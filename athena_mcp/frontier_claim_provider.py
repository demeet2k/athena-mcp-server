from __future__ import annotations

import base64
import json
import re
from typing import Any
from urllib import error, parse, request

_SAFE = r"[A-Za-z0-9._-]+"
_CLAIM_PATH = re.compile(rf"^runtime/runs/(?P<run>{_SAFE})/claims/(?P<node>{_SAFE})\.json$")
_EVENT_PATH = re.compile(rf"^runtime/runs/(?P<run>{_SAFE})/events/(?P<sequence>[0-9]{{8}})\.json$")
_CLAIM_KEYS = {
    "schema_version", "run_id", "node_id", "worker_role", "attempt", "policy_commit",
    "claimed_at", "lease_expires_at", "input_snapshot_digest", "production_authority",
}
_EVENT_KEYS = {"schema_version", "event_id", "sequence", "run_id", "event_type", "at", "node_id", "data"}
_ALLOWED_EVENT_TYPES = {"NODE_READY", "CLAIM_ACQUIRED"}


def _canonical_text(content: dict) -> str:
    return json.dumps(content, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def validate_provider_descriptor(descriptor: dict) -> dict:
    """Validate a claim-membrane create descriptor before any network call."""

    if not isinstance(descriptor, dict):
        raise ValueError("provider descriptor must be an object")
    if descriptor.get("provider_operation") != "CREATE_FILE_IF_ABSENT":
        raise ValueError("only CREATE_FILE_IF_ABSENT is allowed")
    path = str(descriptor.get("path") or "")
    kind = str(descriptor.get("kind") or "")
    content = descriptor.get("content")
    if not isinstance(content, dict):
        raise ValueError("provider content must be an object")
    content_text = descriptor.get("content_text")
    canonical = _canonical_text(content)
    if content_text != canonical:
        raise ValueError("content_text must equal canonical content JSON")

    claim_match = _CLAIM_PATH.fullmatch(path)
    event_match = _EVENT_PATH.fullmatch(path)
    if kind == "CLAIM_V1":
        if not claim_match:
            raise ValueError("CLAIM_V1 path is outside the fixed claim namespace")
        if set(content) != _CLAIM_KEYS:
            raise ValueError("CLAIM_V1 content keys mismatch")
        if content.get("schema_version") != "CLAIM_V1":
            raise ValueError("claim schema_version mismatch")
        if str(content.get("run_id")) != claim_match.group("run"):
            raise ValueError("claim run_id/path mismatch")
        if str(content.get("node_id")) != claim_match.group("node"):
            raise ValueError("claim node_id/path mismatch")
        if content.get("production_authority") != "HOLD":
            raise ValueError("initial claim provider membrane permits HOLD authority only")
        if not isinstance(content.get("attempt"), int) or int(content["attempt"]) <= 0:
            raise ValueError("claim attempt must be positive")
        digest = str(content.get("input_snapshot_digest") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("claim input_snapshot_digest must be lowercase SHA-256")
    elif kind == "EVENT_V1":
        if not event_match:
            raise ValueError("EVENT_V1 path is outside the fixed event namespace")
        if set(content) != _EVENT_KEYS:
            raise ValueError("EVENT_V1 content keys mismatch")
        if content.get("schema_version") != "EVENT_V1":
            raise ValueError("event schema_version mismatch")
        if str(content.get("run_id")) != event_match.group("run"):
            raise ValueError("event run_id/path mismatch")
        if int(content.get("sequence") or 0) != int(event_match.group("sequence")):
            raise ValueError("event sequence/path mismatch")
        if content.get("event_type") not in _ALLOWED_EVENT_TYPES:
            raise ValueError("claim membrane event_type is not allowed")
        if content.get("event_type") in _ALLOWED_EVENT_TYPES and not content.get("node_id"):
            raise ValueError("claim membrane event requires node_id")
        if not isinstance(content.get("data"), dict):
            raise ValueError("event data must be an object")
    else:
        raise ValueError("provider kind must be CLAIM_V1 or EVENT_V1")

    return {
        "provider_operation": "CREATE_FILE_IF_ABSENT",
        "kind": kind,
        "path": path,
        "content": content,
        "content_text": canonical,
    }


class GitHubContentsCreateProvider:
    """Exact-path GitHub Contents create/readback adapter.

    This class is private infrastructure. It has no MCP registration here. It
    never sends update SHA, delete, force, merge, or arbitrary-path operations.
    """

    def __init__(
        self,
        *,
        repo: str,
        branch: str,
        token: str,
        api_base: str = "https://api.github.com",
        opener=None,
    ):
        if not re.fullmatch(rf"{_SAFE}/{_SAFE}", str(repo or "")):
            raise ValueError("invalid GitHub repository")
        if not branch or any(ch in branch for ch in "\r\n"):
            raise ValueError("invalid GitHub branch")
        if not token:
            raise ValueError("GitHub token is required")
        self.repo = repo
        self.branch = branch
        self._token = token
        self.api_base = api_base.rstrip("/")
        self._opener = opener or request.urlopen

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "User-Agent": "athena-mcp-frontier-claim-v1",
        }

    def _url(self, path: str) -> str:
        owner, repo = self.repo.split("/", 1)
        encoded_path = "/".join(parse.quote(part, safe="") for part in path.split("/"))
        return f"{self.api_base}/repos/{parse.quote(owner)}/{parse.quote(repo)}/contents/{encoded_path}"

    @staticmethod
    def _safe_response(value: Any) -> dict:
        if not isinstance(value, dict):
            return {}
        content = value.get("content") if isinstance(value.get("content"), dict) else {}
        commit = value.get("commit") if isinstance(value.get("commit"), dict) else {}
        return {
            "content_sha": content.get("sha"),
            "commit_sha": commit.get("sha"),
        }

    def _read_existing(self, path: str) -> dict:
        url = f"{self._url(path)}?{parse.urlencode({'ref': self.branch})}"
        req = request.Request(url, headers=self._headers(), method="GET")
        try:
            with self._opener(req, timeout=15) as response:
                raw = response.read()
                status = int(getattr(response, "status", 200))
        except error.HTTPError as exc:
            if int(getattr(exc, "code", 0) or 0) == 404:
                return {"status": "ABSENT"}
            return {"status": "READBACK_HOLD", "http_status": int(getattr(exc, "code", 0) or 0)}
        except Exception as exc:
            return {"status": "READBACK_HOLD", "error_type": type(exc).__name__}
        try:
            payload = json.loads(raw.decode("utf-8"))
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

    def _resolve_ambiguous(self, path: str, expected_text: str, *, reason: str) -> dict:
        observed = self._read_existing(path)
        if observed.get("status") == "PRESENT":
            if observed.get("content_text") == expected_text:
                return {
                    "status": "CREATE_EFFECT_OBSERVED",
                    "path": path,
                    "readback": {"content_sha": observed.get("content_sha")},
                    "resolution": reason,
                }
            return {
                "status": "CREATE_COLLISION",
                "path": path,
                "resolution": reason,
            }
        if observed.get("status") == "ABSENT":
            return {
                "status": "AMBIGUOUS_CREATE_HOLD",
                "path": path,
                "resolution": reason,
                "law": "TIMEOUT_OR_PROVIDER_ERROR != SAFE_TO_BLINDLY_RETRY",
            }
        return {
            "status": "AMBIGUOUS_CREATE_HOLD",
            "path": path,
            "resolution": reason,
            "readback_status": observed.get("status"),
            "law": "UNVERIFIED_PROVIDER_EFFECT != FAILURE",
        }

    def create_if_absent(self, descriptor: dict) -> dict:
        packet = validate_provider_descriptor(descriptor)
        path = packet["path"]
        content_text = packet["content_text"]
        body = {
            "message": f"athena: create {packet['kind']} {path}",
            "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        # Absence of a `sha` field is the create-only boundary. Existing files
        # must not be updated by this adapter.
        req = request.Request(
            self._url(path),
            headers=self._headers(),
            data=json.dumps(body, sort_keys=True).encode("utf-8"),
            method="PUT",
        )
        try:
            with self._opener(req, timeout=20) as response:
                raw = response.read()
                status = int(getattr(response, "status", 0) or 0)
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            if status != 201:
                return self._resolve_ambiguous(path, content_text, reason=f"UNEXPECTED_HTTP_{status}")
            return {
                "status": "CREATED",
                "path": path,
                "provider": self._safe_response(payload),
            }
        except error.HTTPError as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if code in {409, 422}:
                return self._resolve_ambiguous(path, content_text, reason=f"HTTP_{code}")
            return self._resolve_ambiguous(path, content_text, reason=f"HTTP_{code}_AMBIGUOUS")
        except Exception as exc:
            return self._resolve_ambiguous(path, content_text, reason=f"{type(exc).__name__}_AMBIGUOUS")
