from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .git_backend import GitBackend, GitStateError

ARTIFACT = "ATHENA.CONTINUATION.RAW.TRACE.V1"
TOOL_NAME = "athena_continuation_raw_trace"
TRACE_STANDING = "RAW_RUNTIME_FACTS"

REHYDRATION_RECEIPT_ARTIFACT = "ATHENA.REHYDRATION.RECEIPT.V1"
REHYDRATION_EVENT_ARTIFACT = "ATHENA.REHYDRATION.EVENT.V1"
MESSAGE_BOARD_EVENT_ARTIFACT = "ATHENA.MESSAGE.BOARD.EVENT.V1"

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

_SOURCE_SPECS = (
    (
        "REHYDRATION_RECEIPT",
        "prompts/rehydration/*/receipts/*.json",
        REHYDRATION_RECEIPT_ARTIFACT,
        "created_at",
    ),
    (
        "REHYDRATION_EVENT",
        "prompts/rehydration/*/events/*.json",
        REHYDRATION_EVENT_ARTIFACT,
        "created_at",
    ),
    (
        "MESSAGE_BOARD_EVENT",
        "runtime/message_board/v1/events/**/*.json",
        MESSAGE_BOARD_EVENT_ARTIFACT,
        "created_at",
    ),
)

LAWS = [
    "RAW_TRACE != ASSAY_CLASSIFICATION",
    "RAW_RUNTIME_FACT != BEHAVIORAL_EFFECT",
    "REHYDRATION_RECEIPT != USER_UI_EVENT",
    "MESSAGE_BOARD_EVENT != COORDINATION_SUCCESS",
    "TERMINAL_GATE_REJECTION != HUMAN_REENTRY_WITHOUT_EXPLICIT_CLASSIFIER",
    "TRACE_DIGEST != SIGNATURE",
    "TRACKED_FILE != WORLD_TRUTH",
    "DIRTY_OR_MALFORMED_SOURCE => COVERAGE_HOLD",
    "HALF_OPEN_WINDOW = [window_start, window_end)",
    "READ_ONLY_OBSERVER != CONTROLLER",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _sha256(value: Any) -> str:
    return _sha256_bytes(_canonical(value))


def _parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a timezone-aware ISO-8601 string")
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid {field}") from exc
    if dt.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ContinuationRawObserver:
    """Read-only extractor over already-persisted continuation/coordination ledgers.

    The observer owns no classifier and performs no Git writes. It exposes exact
    tracked source records plus content/blob identities so a separate semantic
    layer can classify them under an explicit policy without inventing evidence.
    """

    def __init__(self, git: GitBackend):
        self.git = git

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for continuation raw trace")
        return self.git.root

    def _tracked_blob(self, rel: str) -> str | None:
        out = self.git._git("ls-files", "-s", "--", rel).strip()
        if not out:
            return None
        first = out.splitlines()[0].split()
        if len(first) < 2 or not _SHA_RE.fullmatch(first[1]):
            return None
        return first[1]

    def _dirty_paths(self) -> list[str]:
        out = self.git._git("status", "--porcelain", "--untracked-files=all")
        return [line.rstrip() for line in out.splitlines() if line.strip()]

    def _read_source(
        self,
        *,
        category: str,
        path: Path,
        expected_artifact: str,
        time_field: str,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        root = self._root()
        rel = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
        except OSError as exc:
            return None, {"source_path": rel, "category": category, "error": f"READ:{type(exc).__name__}"}
        digest = _sha256_bytes(raw)
        blob = self._tracked_blob(rel)
        if blob is None:
            return None, {
                "source_path": rel,
                "category": category,
                "record_sha256": digest,
                "error": "SOURCE_NOT_TRACKED_AT_CURRENT_INDEX",
            }
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, {
                "source_path": rel,
                "category": category,
                "git_blob_sha": blob,
                "record_sha256": digest,
                "error": f"JSON:{type(exc).__name__}",
            }
        if not isinstance(value, dict):
            return None, {
                "source_path": rel,
                "category": category,
                "git_blob_sha": blob,
                "record_sha256": digest,
                "error": "RECORD_NOT_OBJECT",
            }
        if value.get("artifact") != expected_artifact:
            return None, {
                "source_path": rel,
                "category": category,
                "git_blob_sha": blob,
                "record_sha256": digest,
                "error": "ARTIFACT_IDENTITY_MISMATCH",
                "expected_artifact": expected_artifact,
                "observed_artifact": value.get("artifact"),
            }
        try:
            observed_at = _parse_time(value.get(time_field), f"{rel}.{time_field}")
        except ValueError as exc:
            return None, {
                "source_path": rel,
                "category": category,
                "git_blob_sha": blob,
                "record_sha256": digest,
                "error": "TIMESTAMP_INVALID",
                "detail": str(exc),
            }
        return {
            "category": category,
            "source_path": rel,
            "git_blob_sha": blob,
            "record_sha256": digest,
            "observed_at": _iso(observed_at),
            "record": value,
        }, None

    def read(
        self,
        *,
        window_start: str,
        window_end: str,
        expected_git_head: str | None = None,
        max_records: int = 50000,
    ) -> dict[str, Any]:
        start = _parse_time(window_start, "window_start")
        end = _parse_time(window_end, "window_end")
        if end <= start:
            raise ValueError("window_end must be later than window_start")
        max_records = int(max_records)
        if max_records < 1 or max_records > 100000:
            raise ValueError("max_records must be between 1 and 100000")

        current_head = self.git.head()
        if expected_git_head is not None:
            if not isinstance(expected_git_head, str) or not _SHA_RE.fullmatch(expected_git_head):
                raise ValueError("expected_git_head must be an immutable 40-hex commit SHA")
            if expected_git_head != current_head:
                return {
                    "artifact": ARTIFACT,
                    "status": "HOLD_STALE_GIT_HEAD",
                    "standing": TRACE_STANDING,
                    "window_start": _iso(start),
                    "window_end": _iso(end),
                    "expected_git_head": expected_git_head,
                    "source_git_head": current_head,
                    "coverage_complete": False,
                    "records": [],
                    "malformed_sources": [],
                    "trace_digest": None,
                    "authority": {
                        "classification": False,
                        "behavioral_effect": False,
                        "causal_effect": False,
                        "promotion": False,
                        "mutation": False,
                    },
                    "laws": list(LAWS),
                }

        dirty = self._dirty_paths()
        if dirty:
            return {
                "artifact": ARTIFACT,
                "status": "HOLD_DIRTY_GIT_ROOT",
                "standing": TRACE_STANDING,
                "window_start": _iso(start),
                "window_end": _iso(end),
                "expected_git_head": expected_git_head,
                "source_git_head": current_head,
                "coverage_complete": False,
                "dirty_paths": dirty[:200],
                "dirty_path_count": len(dirty),
                "records": [],
                "malformed_sources": [],
                "trace_digest": None,
                "authority": {
                    "classification": False,
                    "behavioral_effect": False,
                    "causal_effect": False,
                    "promotion": False,
                    "mutation": False,
                },
                "laws": list(LAWS),
            }

        root = self._root()
        records: list[dict[str, Any]] = []
        malformed: list[dict[str, Any]] = []
        scanned = 0
        category_counts: dict[str, int] = {}
        for category, pattern, artifact, time_field in _SOURCE_SPECS:
            seen_for_category = 0
            for path in sorted(root.glob(pattern)):
                if not path.is_file():
                    continue
                scanned += 1
                item, error = self._read_source(
                    category=category,
                    path=path,
                    expected_artifact=artifact,
                    time_field=time_field,
                )
                if error is not None:
                    malformed.append(error)
                    continue
                assert item is not None
                observed_at = _parse_time(item["observed_at"], "observed_at")
                if start <= observed_at < end:
                    records.append(item)
                    seen_for_category += 1
            category_counts[category] = seen_for_category

        records.sort(key=lambda row: (row["observed_at"], row["category"], row["source_path"]))
        over_limit = len(records) > max_records
        returned = records[:max_records]
        coverage_complete = not malformed and not over_limit
        status = "OK" if coverage_complete else "TRACE_INTEGRITY_HOLD"
        digest_basis = {
            "artifact": ARTIFACT,
            "standing": TRACE_STANDING,
            "source_git_head": current_head,
            "window_start": _iso(start),
            "window_end": _iso(end),
            "records": [
                {
                    "category": row["category"],
                    "source_path": row["source_path"],
                    "git_blob_sha": row["git_blob_sha"],
                    "record_sha256": row["record_sha256"],
                    "observed_at": row["observed_at"],
                }
                for row in returned
            ],
            "malformed_sources": malformed,
            "over_limit": over_limit,
            "total_matching_records": len(records),
        }
        return {
            "artifact": ARTIFACT,
            "status": status,
            "standing": TRACE_STANDING,
            "window_start": _iso(start),
            "window_end": _iso(end),
            "expected_git_head": expected_git_head,
            "source_git_head": current_head,
            "coverage_complete": coverage_complete,
            "source_files_scanned": scanned,
            "category_counts": category_counts,
            "total_matching_records": len(records),
            "returned_record_count": len(returned),
            "record_limit": max_records,
            "record_limit_exceeded": over_limit,
            "records": returned,
            "malformed_sources": malformed,
            "trace_digest": _sha256(digest_basis),
            "authority": {
                "classification": False,
                "behavioral_effect": False,
                "causal_effect": False,
                "promotion": False,
                "mutation": False,
            },
            "external_mutation_performed": False,
            "source_semantics": {
                "REHYDRATION_RECEIPT": "persisted bounded-cycle receipt",
                "REHYDRATION_EVENT": "persisted rehydration lifecycle event",
                "MESSAGE_BOARD_EVENT": "persisted coordination/message-board event",
            },
            "laws": list(LAWS),
        }

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name != TOOL_NAME:
            raise KeyError(name)
        return self.read(
            window_start=arguments["window_start"],
            window_end=arguments["window_end"],
            expected_git_head=arguments.get("expected_git_head"),
            max_records=arguments.get("max_records", 50000),
        )


CONTINUATION_OBSERVER_TOOLS = [
    {
        "name": TOOL_NAME,
        "description": (
            "Read an exact half-open UTC window of already-persisted rehydration receipts/events and Message Board events. "
            "Returns raw tracked source records with Git blob and SHA-256 identities plus a deterministic trace digest. "
            "This tool is read-only and performs no assay classification, behavioral inference, causal attribution, or promotion."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["window_start", "window_end"],
            "properties": {
                "window_start": {"type": "string"},
                "window_end": {"type": "string"},
                "expected_git_head": {
                    "type": ["string", "null"],
                    "pattern": "^[0-9a-f]{40}$",
                },
                "max_records": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100000,
                },
            },
            "additionalProperties": False,
        },
    }
]
CONTINUATION_OBSERVER_TOOL_NAMES = {TOOL_NAME}
