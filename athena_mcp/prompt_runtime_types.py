from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

PROMPT_RUNTIME_VERSION = "PROMPT.RUNTIME.1"
PROMPT_MANIFEST_PATH = "prompts/PROMPT.manifest.json"
PROMPT_RESOURCE_URI = "athena://prompt/runtime"
AUTHORITY_LAW = (
    "repository prompt runtime < host platform/system/developer/current-user authority, "
    "safety policy and granted tool permissions"
)
CANDIDATE_META_OPEN = "<!-- ATHENA_PROMPT_META_V1"
CANDIDATE_META_CLOSE = "ATHENA_PROMPT_META_V1 -->"
OBSERVED_EXPERIMENT_STATUSES = {"PASSED", "FAILED", "INCONCLUSIVE"}
EXPERIMENT_STATUSES = {"PLANNED", "RUNNING", *OBSERVED_EXPERIMENT_STATUSES}


class PromptRuntimeError(ValueError):
    """Raised when the Git-governed prompt runtime violates a hard invariant."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PromptRuntimeError(f"{field} must be a non-empty string")
    return value.strip()


def safe_actor(value: Any) -> str:
    actor = nonempty(value, "actor")
    if any(ord(char) < 32 or ord(char) == 127 for char in actor):
        raise PromptRuntimeError("actor may not contain control characters")
    return actor[:200]


def string_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if value is None:
        result: list[str] = []
    elif isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value):
        result = [item.strip() for item in value]
    else:
        raise PromptRuntimeError(f"{field} must be an array of non-empty strings")
    if not allow_empty and not result:
        raise PromptRuntimeError(f"{field} must not be empty")
    if len(result) != len(set(result)):
        raise PromptRuntimeError(f"{field} must contain unique values")
    return result


def slug(value: str, field: str) -> str:
    raw = nonempty(value, field).lower()
    result = re.sub(r"[^a-z0-9._-]+", "-", raw).strip("-._")
    if not result:
        raise PromptRuntimeError(f"{field} does not contain a safe path component")
    return result[:80]


def json_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))
