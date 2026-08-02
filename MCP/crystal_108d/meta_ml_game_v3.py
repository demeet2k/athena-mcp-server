"""MMLG.3 Guild Hall projection and cross-plane return layer.

This layer derives 144 quest packets from the frozen MMLG.2 goal index. It may
record local claims, digest-only observations, independent canary decisions, and
non-dispatching return packets. It cannot mutate Guild Hall source boards,
contact connectors, publish raw private source bodies, deploy, merge, or promote.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any

try:
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None

from .meta_ml_game_v2 import (
    CONTROL_HEAD,
    CONTROL_REPOSITORY,
    EXPECTED_INDEX_DIGEST,
    FrozenMetaMLGameV2,
)


SCHEMA = "athena.meta-ml-game-guild-hall-projection/v3"
RUNTIME_PARENT_HEAD = "77f8a7b456b48d173360c684d0dc2d79e7949009"
RUNTIME_BRANCH = "agent/meta-harness-3-guild-hall-144"
DEFAULT_STATE_DIR = (
    Path(__file__).resolve().parent.parent / "runtime" / "meta_ml_game_v3"
)
STATE_DIR = Path(os.environ.get("ATHENA_MMLG3_STATE", str(DEFAULT_STATE_DIR)))
LEDGER_PATH = STATE_DIR / "guild_hall_events.jsonl"
QUEST_BOARD = "06_QUEST_BOARD.md"
QUEST_STATES = (
    "OPEN",
    "CLAIMED",
    "RUNNING",
    "WITNESSED",
    "RETURNED",
    "ADMITTED",
    "ROLLED_BACK",
)
SOURCE_ADAPTERS = {
    "github": {
        "required": {"repository", "commit_sha", "path", "object_digest"},
        "source_class": "VERSIONED_GIT",
    },
    "google_drive": {
        "required": {
            "file_id",
            "revision_id",
            "mime_type",
            "content_digest",
            "consent_basis",
        },
        "source_class": "CONSENTED_DRIVE_LOCATOR",
    },
    "mcp": {
        "required": {
            "endpoint_class",
            "tool_or_resource",
            "receipt_hash",
            "output_digest",
        },
        "source_class": "MCP_RECEIPT",
    },
    "website_letter_search": {
        "required": {
            "site_id",
            "letter",
            "traversal_stage",
            "page_digest",
        },
        "source_class": "PUBLIC_WEB_DIGEST",
    },
}
VISIBILITY_CLASSES = {
    "PRIVATE_LOCATOR",
    "INTERNAL_DIGEST",
    "PUBLIC_DIGEST",
}
CANARY_ROLES = {
    "SOURCE_REVIEWER",
    "IMPLEMENTATION_REVIEWER",
    "RISK_REVIEWER",
}
FORBIDDEN_KEYS = {
    "raw_content",
    "raw_body",
    "body",
    "secret",
    "token",
    "credential",
    "password",
    "private_payload",
}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class MMLG3Error(RuntimeError):
    """Fail-closed MMLG.3 error."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _negative_effects() -> dict[str, bool]:
    return {
        "guild_hall_source_mutated": False,
        "raw_private_source_stored": False,
        "source_connector_contacted": False,
        "workflow_dispatched": False,
        "external_authority_created": False,
        "merged": False,
        "deployed": False,
        "production_promoted": False,
    }


def _parse_object(value: str | dict[str, Any] | None, field: str) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON object") from error
    if not isinstance(parsed, dict):
        raise ValueError(f"{field} must be a JSON object")
    return parsed


def _parse_list(value: str | list[Any] | None, field: str) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return deepcopy(value)
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"{field} must be a JSON array") from error
    if not isinstance(parsed, list):
        raise ValueError(f"{field} must be a JSON array")
    return parsed


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key).lower())
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def _require_digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise ValueError(f"{field} must be sha256:<64 lowercase hex>")
    return value


class GuildHallMMLG3:
    """Frozen quest projection plus local digest-only coordination ledger."""

    _fallback_lock = threading.Lock()

    def __init__(
        self,
        game: FrozenMetaMLGameV2,
        *,
        ledger_path: Path = LEDGER_PATH,
    ):
        self.game = game
        self.ledger_path = Path(ledger_path)
        if len(game.goals) != 144:
            raise ValueError("MMLG.3 requires the exact 144-goal MMLG.2 index")
        self._quests = self._compile_quests()
        self._quest_by_id = {quest["quest_id"]: quest for quest in self._quests}
        self._quest_by_goal = {quest["goal_id"]: quest for quest in self._quests}
        self.projection_digest = _digest(
            {
                "schema": SCHEMA,
                "mmlg2_index_digest": EXPECTED_INDEX_DIGEST,
                "quests": self._quests,
            }
        )

    @classmethod
    def load(cls, *, ledger_path: Path = LEDGER_PATH) -> "GuildHallMMLG3":
        return cls(FrozenMetaMLGameV2.load(), ledger_path=ledger_path)

    def _compile_quests(self) -> list[dict[str, Any]]:
        quests = []
        for index, goal_id in enumerate(sorted(self.game.goals), start=1):
            goal = self.game.goal(goal_id)
            local = ((index - 1) % 12) + 1
            quest = {
                "schema": "athena.guild-hall-mmlg-quest/v3",
                "quest_id": f"MMLG3-Q{index:03d}",
                "goal_id": goal_id,
                "coordinate": goal["coordinate"],
                "domain_id": goal["domain_id"],
                "domain": goal["domain"],
                "title": goal["title"],
                "board": QUEST_BOARD,
                "board_slot": f"{goal['domain_id']}.{local:02d}",
                "initial_state": "OPEN",
                "learning_method": goal["learning_method"],
                "learnable_layer": goal["learnable_layer"],
                "objective": (
                    f"Produce reversible evidence for {goal['title']} without "
                    "mutating source truth or self-certifying promotion."
                ),
                "source_adapters": sorted(SOURCE_ADAPTERS),
                "promotion_path": [
                    "OPEN",
                    "CLAIMED",
                    "RUNNING",
                    "WITNESSED",
                    "RETURNED",
                    "CONTROL_REVIEW",
                ],
                "required_return": {
                    "projection_digest": True,
                    "observation_receipts": True,
                    "canary_council_receipt": True,
                    "mmlg2_ledger_head": True,
                    "dispatch_performed": False,
                },
                "authority": "LOCAL_REVERSIBLE_COORDINATION_ONLY",
            }
            quest["quest_digest"] = _digest(quest)
            quests.append(quest)
        return quests

    def _open_locked(self):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        handle = self.ledger_path.open("a+", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return handle

    @staticmethod
    def _unlock(handle: Any) -> None:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()

    @staticmethod
    def _rows(handle: Any) -> list[dict[str, Any]]:
        handle.seek(0)
        rows = []
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise MMLG3Error(
                    f"MMLG.3 ledger JSON invalid at line {line_number}"
                ) from error
            rows.append(row)
        return rows

    def events(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            return self._rows(handle)

    def _append(
        self,
        event_type: str,
        quest_id: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self._fallback_lock:
            handle = self._open_locked()
            try:
                rows = self._rows(handle)
                if any(
                    row.get("idempotency_key") == idempotency_key
                    for row in rows
                ):
                    raise MMLG3Error(
                        f"duplicate idempotency key: {idempotency_key}"
                    )
                previous = rows[-1]["receipt_hash"] if rows else "GENESIS"
                body = {
                    "sequence": len(rows) + 1,
                    "event_type": event_type,
                    "quest_id": quest_id,
                    "idempotency_key": idempotency_key,
                    "previous_receipt_hash": previous,
                    "observed_at": time.time(),
                    "payload": payload,
                }
                body["receipt_hash"] = _digest(body)
                handle.seek(0, os.SEEK_END)
                handle.write(
                    json.dumps(body, ensure_ascii=False, sort_keys=True) + "\n"
                )
                handle.flush()
                os.fsync(handle.fileno())
                return body
            finally:
                self._unlock(handle)

    def verify_ledger(self) -> dict[str, Any]:
        previous = "GENESIS"
        seen_keys = set()
        rows = self.events()
        for sequence, row in enumerate(rows, start=1):
            if row.get("sequence") != sequence:
                raise MMLG3Error(f"ledger sequence gap at {sequence}")
            if row.get("previous_receipt_hash") != previous:
                raise MMLG3Error(f"ledger chain broken at {sequence}")
            key = row.get("idempotency_key")
            if key in seen_keys:
                raise MMLG3Error(
                    f"duplicate ledger idempotency key at {sequence}"
                )
            seen_keys.add(key)
            claimed = row.get("receipt_hash")
            unsigned = deepcopy(row)
            unsigned.pop("receipt_hash", None)
            if claimed != _digest(unsigned):
                raise MMLG3Error(f"ledger hash mismatch at {sequence}")
            previous = claimed
        return {
            "schema": "athena.meta-ml-game-guild-hall-ledger/v3",
            "status": "PASS",
            "events": len(rows),
            "quests_touched": len(
                {row["quest_id"] for row in rows if row["quest_id"] != "GLOBAL"}
            ),
            "head": previous,
            "projection_digest": self.projection_digest,
            **_negative_effects(),
        }

    def _resolve_quest(self, identifier: str) -> dict[str, Any]:
        if identifier in self._quest_by_id:
            return self._quest_by_id[identifier]
        if identifier in self._quest_by_goal:
            return self._quest_by_goal[identifier]
        raise ValueError(f"unknown quest or goal identifier {identifier}")

    def _quest_events(self, quest_id: str) -> list[dict[str, Any]]:
        return [row for row in self.events() if row["quest_id"] == quest_id]

    @staticmethod
    def _state_from_events(events: list[dict[str, Any]]) -> str:
        state = "OPEN"
        for row in events:
            event = row["event_type"]
            if event == "QUEST_CLAIMED":
                state = "CLAIMED"
            elif event == "OBSERVATION_INGESTED":
                state = "RUNNING"
            elif event == "CANARY_COUNCIL_ACCEPTED":
                state = "WITNESSED"
            elif event == "CONTROL_RETURN_COMPILED":
                state = "RETURNED"
            elif event == "QUEST_ROLLED_BACK":
                state = "ROLLED_BACK"
        return state

    def projection(self) -> dict[str, Any]:
        state_map = {
            quest["quest_id"]: self._state_from_events(
                self._quest_events(quest["quest_id"])
            )
            for quest in self._quests
        }
        return {
            "schema": SCHEMA,
            "status": "PROJECTED_LOCAL_NOT_WRITTEN_TO_GUILD_HALL",
            "goal_index_digest": EXPECTED_INDEX_DIGEST,
            "control_head": CONTROL_HEAD,
            "runtime_parent_head": RUNTIME_PARENT_HEAD,
            "quest_count": len(self._quests),
            "domain_count": 12,
            "projection_digest": self.projection_digest,
            "state_counts": {
                state: sum(value == state for value in state_map.values())
                for state in QUEST_STATES
            },
            "quests": [
                {**deepcopy(quest), "state": state_map[quest["quest_id"]]}
                for quest in self._quests
            ],
            **_negative_effects(),
        }

    def list_quests(
        self,
        *,
        domain_id: str | None = None,
        state: str | None = None,
        source_adapter: str | None = None,
    ) -> dict[str, Any]:
        if domain_id is not None and domain_id not in self.game.domains:
            raise ValueError(f"unknown domain_id {domain_id}")
        if state is not None and state not in QUEST_STATES:
            raise ValueError(f"unknown state {state}")
        if source_adapter is not None and source_adapter not in SOURCE_ADAPTERS:
            raise ValueError(f"unknown source_adapter {source_adapter}")
        quests = self.projection()["quests"]
        if domain_id:
            quests = [quest for quest in quests if quest["domain_id"] == domain_id]
        if state:
            quests = [quest for quest in quests if quest["state"] == state]
        if source_adapter:
            quests = [
                quest
                for quest in quests
                if source_adapter in quest["source_adapters"]
            ]
        return {
            "schema": "athena.meta-ml-game-guild-hall-quest-list/v3",
            "count": len(quests),
            "filters": {
                "domain_id": domain_id,
                "state": state,
                "source_adapter": source_adapter,
            },
            "projection_digest": self.projection_digest,
            "quests": quests,
            **_negative_effects(),
        }

    def quest(self, identifier: str) -> dict[str, Any]:
        quest = deepcopy(self._resolve_quest(identifier))
        events = self._quest_events(quest["quest_id"])
        quest["state"] = self._state_from_events(events)
        quest["event_count"] = len(events)
        quest["latest_receipt"] = (
            events[-1]["receipt_hash"] if events else None
        )
        quest["projection_digest"] = self.projection_digest
        return quest

    def claim(
        self,
        identifier: str,
        agent_id: str,
        lease_seconds: int,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        state = self._state_from_events(self._quest_events(quest["quest_id"]))
        if state != "OPEN":
            raise MMLG3Error(f"quest cannot be claimed from state {state}")
        if not agent_id.strip():
            raise ValueError("agent_id is required")
        if isinstance(lease_seconds, bool) or not 60 <= lease_seconds <= 86400:
            raise ValueError("lease_seconds must be within [60,86400]")
        payload = {
            "agent_id": agent_id,
            "lease_seconds": lease_seconds,
            "lease_expires_at": time.time() + lease_seconds,
            "claim_scope": "LOCAL_GUILD_HALL_PROJECTION",
            "source_board_written": False,
            "promotion_authority": False,
            **_negative_effects(),
        }
        key = idempotency_key or _digest(
            {"quest_id": quest["quest_id"], "agent_id": agent_id}
        )
        receipt = self._append(
            "QUEST_CLAIMED",
            quest["quest_id"],
            payload,
            f"claim:{key}",
        )
        return {
            "schema": "athena.meta-ml-game-guild-hall-claim/v3",
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "state": "CLAIMED",
            "receipt": receipt,
            **payload,
        }

    def _validate_adapter_metadata(
        self,
        adapter: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        if adapter not in SOURCE_ADAPTERS:
            raise ValueError(f"unknown source adapter {adapter}")
        forbidden = sorted(set(_walk_keys(metadata)) & FORBIDDEN_KEYS)
        if forbidden:
            raise MMLG3Error(
                f"raw or secret-bearing metadata forbidden: {forbidden}"
            )
        required = SOURCE_ADAPTERS[adapter]["required"]
        missing = sorted(required - set(metadata))
        if missing:
            raise ValueError(
                f"adapter {adapter} metadata missing {missing}"
            )
        normalized = deepcopy(metadata)
        if adapter == "github":
            if not isinstance(metadata["repository"], str) or "/" not in metadata["repository"]:
                raise ValueError("github repository must be owner/name")
            if not isinstance(metadata["commit_sha"], str) or not SHA_RE.fullmatch(
                metadata["commit_sha"]
            ):
                raise ValueError("github commit_sha must be 40 lowercase hex")
            _require_digest(metadata["object_digest"], "object_digest")
        elif adapter == "google_drive":
            if not str(metadata["consent_basis"]).strip():
                raise ValueError("google_drive consent_basis is required")
            _require_digest(metadata["content_digest"], "content_digest")
        elif adapter == "mcp":
            _require_digest(metadata["receipt_hash"], "receipt_hash")
            _require_digest(metadata["output_digest"], "output_digest")
        elif adapter == "website_letter_search":
            letter = str(metadata["letter"]).upper()
            if not re.fullmatch(r"[A-Z]", letter):
                raise ValueError("website letter must be A-Z")
            normalized["letter"] = letter
            if metadata["traversal_stage"] not in {
                "DISCOVER",
                "SITEMAP",
                "LETTER",
                "LINK",
                "CHANGE",
                "RETURN",
            }:
                raise ValueError("invalid website traversal_stage")
            _require_digest(metadata["page_digest"], "page_digest")
        return normalized

    def ingest_observation(
        self,
        identifier: str,
        adapter: str,
        source_locator: str,
        source_version: str,
        observation_digest: str,
        visibility: str,
        metadata: dict[str, Any],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        events = self._quest_events(quest["quest_id"])
        state = self._state_from_events(events)
        if state not in {"CLAIMED", "RUNNING"}:
            raise MMLG3Error(
                f"observation cannot be ingested from state {state}"
            )
        if not source_locator.strip() or not source_version.strip():
            raise ValueError("source_locator and source_version are required")
        _require_digest(observation_digest, "observation_digest")
        if visibility not in VISIBILITY_CLASSES:
            raise ValueError(f"unknown visibility {visibility}")
        normalized_metadata = self._validate_adapter_metadata(adapter, metadata)
        payload = {
            "observation_id": "OBS-" + observation_digest.split(":", 1)[1][:16],
            "adapter": adapter,
            "source_class": SOURCE_ADAPTERS[adapter]["source_class"],
            "source_locator": source_locator,
            "source_version": source_version,
            "observation_digest": observation_digest,
            "visibility": visibility,
            "metadata": normalized_metadata,
            "projection_digest": self.projection_digest,
            "raw_content_stored": False,
            "source_contact_performed": False,
            "promotion_authority": False,
            **_negative_effects(),
        }
        key = idempotency_key or observation_digest
        receipt = self._append(
            "OBSERVATION_INGESTED",
            quest["quest_id"],
            payload,
            f"observe:{key}",
        )
        return {
            "schema": "athena.meta-ml-game-source-observation/v3",
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "state": "RUNNING",
            "receipt": receipt,
            **payload,
        }

    def observations(
        self,
        identifier: str,
        *,
        adapter: str | None = None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        if adapter is not None and adapter not in SOURCE_ADAPTERS:
            raise ValueError(f"unknown source adapter {adapter}")
        rows = [
            row
            for row in self._quest_events(quest["quest_id"])
            if row["event_type"] == "OBSERVATION_INGESTED"
        ]
        if adapter:
            rows = [
                row for row in rows if row["payload"]["adapter"] == adapter
            ]
        return {
            "schema": "athena.meta-ml-game-source-observation-list/v3",
            "quest_id": quest["quest_id"],
            "count": len(rows),
            "adapter": adapter,
            "observations": [
                {
                    "receipt_hash": row["receipt_hash"],
                    "sequence": row["sequence"],
                    **deepcopy(row["payload"]),
                }
                for row in rows
            ],
            **_negative_effects(),
        }

    def letter_search_plan(
        self,
        letter: str,
        site_id: str = "athena-websites",
    ) -> dict[str, Any]:
        normalized = letter.upper()
        if not re.fullmatch(r"[A-Z]", normalized):
            raise ValueError("letter must be A-Z")
        goals = [
            self.quest("MLG-G027"),
            *[
                self.quest(f"MLG-G{index:03d}")
                for index in range(121, 133)
            ],
        ]
        return {
            "schema": "athena.meta-ml-game-letter-search-plan/v3",
            "site_id": site_id,
            "letter": normalized,
            "stages": [
                "DISCOVER",
                "SITEMAP",
                "LETTER",
                "LINK",
                "CHANGE",
                "RETURN",
            ],
            "quest_ids": [goal["quest_id"] for goal in goals],
            "goal_ids": [goal["goal_id"] for goal in goals],
            "required_observation_adapter": "website_letter_search",
            "execution_performed": False,
            "endpoint_contacted": False,
            "projection_digest": self.projection_digest,
            **_negative_effects(),
        }

    @staticmethod
    def _normalize_votes(votes: list[Any]) -> list[dict[str, Any]]:
        normalized = []
        required = {
            "role",
            "witness_id",
            "authority_domain",
            "implementation_id",
            "passed",
            "evidence_digest",
        }
        for index, raw in enumerate(votes):
            if not isinstance(raw, dict):
                raise ValueError(f"canary vote {index} must be an object")
            missing = sorted(required - set(raw))
            if missing:
                raise ValueError(f"canary vote {index} missing {missing}")
            role = str(raw["role"]).upper()
            if role not in CANARY_ROLES:
                raise ValueError(f"unknown canary role {role}")
            evidence_digest = _require_digest(
                raw["evidence_digest"],
                f"canary vote {index} evidence_digest",
            )
            normalized.append(
                {
                    "role": role,
                    "witness_id": str(raw["witness_id"]),
                    "authority_domain": str(raw["authority_domain"]),
                    "implementation_id": str(raw["implementation_id"]),
                    "passed": bool(raw["passed"]),
                    "evidence_digest": evidence_digest,
                }
            )
        return normalized

    def compile_canary(
        self,
        identifier: str,
        episode_id: str,
        candidate_digest: str,
        rollback_receipt: str,
        votes: list[Any],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        events = self._quest_events(quest["quest_id"])
        state = self._state_from_events(events)
        if state != "RUNNING":
            raise MMLG3Error(f"canary cannot be compiled from state {state}")
        if not episode_id.strip():
            raise ValueError("episode_id is required")
        _require_digest(candidate_digest, "candidate_digest")
        _require_digest(rollback_receipt, "rollback_receipt")
        observations = [
            row for row in events if row["event_type"] == "OBSERVATION_INGESTED"
        ]
        adapters = {row["payload"]["adapter"] for row in observations}
        if len(observations) < 2 or len(adapters) < 2:
            raise MMLG3Error(
                "canary requires at least two observations from two adapters"
            )
        normalized_votes = self._normalize_votes(votes)
        roles = {vote["role"] for vote in normalized_votes}
        witnesses = {vote["witness_id"] for vote in normalized_votes}
        authorities = {
            vote["authority_domain"] for vote in normalized_votes
        }
        implementations = {
            vote["implementation_id"] for vote in normalized_votes
        }
        if roles != CANARY_ROLES or len(normalized_votes) != 3:
            raise MMLG3Error(
                "canary council requires exactly the three canonical roles"
            )
        if any(not vote["passed"] for vote in normalized_votes):
            raise MMLG3Error("canary council contains a failed vote")
        if "athena-learner" in witnesses or len(witnesses) != 3:
            raise MMLG3Error("canary council witness independence failed")
        if len(authorities) < 2 or len(implementations) < 2:
            raise MMLG3Error(
                "canary council lacks authority or implementation diversity"
            )
        payload = {
            "episode_id": episode_id,
            "candidate_digest": candidate_digest,
            "rollback_receipt": rollback_receipt,
            "observation_receipts": [
                row["receipt_hash"] for row in observations
            ],
            "adapter_diversity": sorted(adapters),
            "votes": normalized_votes,
            "roles": sorted(roles),
            "authority_domains": sorted(authorities),
            "implementations": sorted(implementations),
            "decision": "ACCEPT_LOCAL_CANARY_FOR_RETURN_COMPILATION",
            "external_promotion": False,
            "dispatch_performed": False,
            **_negative_effects(),
        }
        key = idempotency_key or _digest(
            {
                "quest_id": quest["quest_id"],
                "candidate_digest": candidate_digest,
                "votes": normalized_votes,
            }
        )
        receipt = self._append(
            "CANARY_COUNCIL_ACCEPTED",
            quest["quest_id"],
            payload,
            f"canary:{key}",
        )
        return {
            "schema": "athena.meta-ml-game-canary-council/v3",
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "state": "WITNESSED",
            "receipt": receipt,
            **payload,
        }

    def compile_return(
        self,
        identifier: str,
        episode_id: str,
        canary_receipt: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        events = self._quest_events(quest["quest_id"])
        state = self._state_from_events(events)
        if state != "WITNESSED":
            raise MMLG3Error(
                f"control return cannot be compiled from state {state}"
            )
        canaries = [
            row for row in events if row["event_type"] == "CANARY_COUNCIL_ACCEPTED"
        ]
        latest_canary = canaries[-1]
        if canary_receipt != latest_canary["receipt_hash"]:
            raise MMLG3Error("canary receipt does not match latest council decision")
        if episode_id != latest_canary["payload"]["episode_id"]:
            raise MMLG3Error("episode_id does not match canary custody")
        observations = [
            row for row in events if row["event_type"] == "OBSERVATION_INGESTED"
        ]
        packet = {
            "schema": "athena.meta-ml-game-cross-plane-return/v3",
            "source_plane": {
                "repository": "demeet2k/athena-mcp-server",
                "branch": RUNTIME_BRANCH,
                "parent_head": RUNTIME_PARENT_HEAD,
            },
            "target_plane": {
                "repository": CONTROL_REPOSITORY,
                "control_head": CONTROL_HEAD,
                "gate": "MMLG3_INDEPENDENT_CONTROL_REVIEW",
            },
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "episode_id": episode_id,
            "projection_digest": self.projection_digest,
            "mmlg2_goal_index_digest": EXPECTED_INDEX_DIGEST,
            "mmlg2_ledger_head": self.game.verify_ledger()["head"],
            "observation_receipts": [
                row["receipt_hash"] for row in observations
            ],
            "canary_council_receipt": canary_receipt,
            "candidate_digest": latest_canary["payload"]["candidate_digest"],
            "rollback_receipt": latest_canary["payload"]["rollback_receipt"],
            "requested_transition": "WITNESSED_TO_CONTROL_REVIEW",
            "dispatch_performed": False,
            "external_promotion_authority": False,
            **_negative_effects(),
        }
        packet["return_id"] = "MMLG3-RETURN-" + _digest(packet).split(":", 1)[1][:24]
        key = idempotency_key or packet["return_id"]
        receipt = self._append(
            "CONTROL_RETURN_COMPILED",
            quest["quest_id"],
            packet,
            f"return:{key}",
        )
        return {
            "schema": "athena.meta-ml-game-cross-plane-return-receipt/v3",
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "state": "RETURNED",
            "receipt": receipt,
            "return_packet": packet,
            **_negative_effects(),
        }

    def rollback(
        self,
        identifier: str,
        reason: str,
        rollback_receipt: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        quest = self._resolve_quest(identifier)
        state = self._state_from_events(self._quest_events(quest["quest_id"]))
        if state in {"RETURNED", "ROLLED_BACK"}:
            raise MMLG3Error(f"quest cannot roll back from state {state}")
        if not reason.strip():
            raise ValueError("reason is required")
        _require_digest(rollback_receipt, "rollback_receipt")
        payload = {
            "from_state": state,
            "state": "ROLLED_BACK",
            "reason": reason,
            "rollback_receipt": rollback_receipt,
            "external_effect": "NONE",
            **_negative_effects(),
        }
        key = idempotency_key or _digest(
            {"quest_id": quest["quest_id"], **payload}
        )
        receipt = self._append(
            "QUEST_ROLLED_BACK",
            quest["quest_id"],
            payload,
            f"rollback:{key}",
        )
        return {
            "schema": "athena.meta-ml-game-guild-hall-rollback/v3",
            "quest_id": quest["quest_id"],
            "goal_id": quest["goal_id"],
            "state": "ROLLED_BACK",
            "receipt": receipt,
            **payload,
        }

    def adapters(self) -> dict[str, Any]:
        return {
            "schema": "athena.meta-ml-game-source-adapters/v3",
            "adapters": deepcopy(SOURCE_ADAPTERS),
            "visibility_classes": sorted(VISIBILITY_CLASSES),
            "forbidden_keys": sorted(FORBIDDEN_KEYS),
            "raw_content_allowed": False,
            "connector_execution_performed": False,
            **_negative_effects(),
        }

    def board_markdown(self) -> str:
        projection = self.projection()
        lines = [
            "# MMLG.3 — Guild Hall 144 Quest Projection",
            "",
            f"- Projection: `{self.projection_digest}`",
            f"- MMLG.2 index: `{EXPECTED_INDEX_DIGEST}`",
            "- Authority: local reversible projection; not written to source board",
            "",
        ]
        current_domain = None
        for quest in projection["quests"]:
            if quest["domain_id"] != current_domain:
                current_domain = quest["domain_id"]
                lines.extend(
                    [
                        f"## {quest['domain_id']} — {quest['domain']}",
                        "",
                    ]
                )
            lines.append(
                f"- [{quest['state']}] **{quest['quest_id']}** / "
                f"`{quest['goal_id']}` — {quest['title']} "
                f"({quest['learning_method']} → {quest['learnable_layer']})"
            )
        lines.extend(
            [
                "",
                "`PROJECTED_LOCAL_NOT_WRITTEN_TO_GUILD_HALL`",
            ]
        )
        return "\n".join(lines)

    def status(self) -> dict[str, Any]:
        projection = self.projection()
        return {
            "schema": "athena.meta-ml-game-guild-hall-status/v3",
            "status": "MMLG3_PROJECTED_LOCAL_REVERSIBLE__PROPOSED_NOT_PROMOTED",
            "control_head": CONTROL_HEAD,
            "runtime_parent_head": RUNTIME_PARENT_HEAD,
            "projection_digest": self.projection_digest,
            "quests": 144,
            "domains": 12,
            "state_counts": projection["state_counts"],
            "source_adapters": sorted(SOURCE_ADAPTERS),
            "canary_roles": sorted(CANARY_ROLES),
            "ledger": self.verify_ledger(),
            "guild_hall_source_board_written": False,
            "persistent_endpoint": False,
            "external_promotion_authority": False,
            **_negative_effects(),
        }


def register_meta_ml_game_v3(mcp: Any) -> None:
    """Register eleven MMLG.3 tools and four read-only resources."""
    game = GuildHallMMLG3.load()

    @mcp.tool()
    def mmlg3_status() -> str:
        """Return MMLG.3 projection, adapter, council, ledger, and authority status."""
        return _render(game.status())

    @mcp.tool()
    def mmlg3_quests_list(
        domain_id: str | None = None,
        state: str | None = None,
        source_adapter: str | None = None,
    ) -> str:
        """List the 144 projected Guild Hall quests with exact filters."""
        return _render(
            game.list_quests(
                domain_id=domain_id,
                state=state,
                source_adapter=source_adapter,
            )
        )

    @mcp.tool()
    def mmlg3_quest_get(identifier: str) -> str:
        """Read one MMLG.3 quest by MMLG3-Q### or MLG-G### identifier."""
        return _render(game.quest(identifier))

    @mcp.tool()
    def mmlg3_quest_claim(
        identifier: str,
        agent_id: str,
        lease_seconds: int = 3600,
        idempotency_key: str | None = None,
    ) -> str:
        """Record a local claim lease without mutating the source Guild Hall board."""
        return _render(
            game.claim(
                identifier,
                agent_id,
                lease_seconds,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg3_observation_ingest(
        identifier: str,
        adapter: str,
        source_locator: str,
        source_version: str,
        observation_digest: str,
        visibility: str,
        metadata_json: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Ingest a digest-only source observation without contacting the source."""
        return _render(
            game.ingest_observation(
                identifier,
                adapter,
                source_locator,
                source_version,
                observation_digest,
                visibility,
                _parse_object(metadata_json, "metadata_json"),
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg3_observations_list(
        identifier: str,
        adapter: str | None = None,
    ) -> str:
        """List local source-observation receipts for one projected quest."""
        return _render(game.observations(identifier, adapter=adapter))

    @mcp.tool()
    def mmlg3_letter_search_plan(
        letter: str,
        site_id: str = "athena-websites",
    ) -> str:
        """Compile a non-executing A-Z website traversal plan and linked quests."""
        return _render(game.letter_search_plan(letter, site_id))

    @mcp.tool()
    def mmlg3_canary_compile(
        identifier: str,
        episode_id: str,
        candidate_digest: str,
        rollback_receipt: str,
        votes_json: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Compile a three-role independent local canary council decision."""
        return _render(
            game.compile_canary(
                identifier,
                episode_id,
                candidate_digest,
                rollback_receipt,
                _parse_list(votes_json, "votes_json"),
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg3_return_compile(
        identifier: str,
        episode_id: str,
        canary_receipt: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Compile a non-dispatching cross-plane return for independent control review."""
        return _render(
            game.compile_return(
                identifier,
                episode_id,
                canary_receipt,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg3_quest_rollback(
        identifier: str,
        reason: str,
        rollback_receipt: str,
        idempotency_key: str | None = None,
    ) -> str:
        """Record a local quest rollback with explicit digest custody."""
        return _render(
            game.rollback(
                identifier,
                reason,
                rollback_receipt,
                idempotency_key,
            )
        )

    @mcp.tool()
    def mmlg3_receipts_verify() -> str:
        """Verify MMLG.3 sequence, idempotency, hash chain, and projection custody."""
        return _render(game.verify_ledger())

    @mcp.resource("athena://meta-ml-game/v3/guild-hall/projection")
    def mmlg3_projection_resource() -> str:
        """Read the frozen 144-quest Guild Hall projection."""
        return _render(game.projection())

    @mcp.resource("athena://meta-ml-game/v3/guild-hall/quest-board")
    def mmlg3_quest_board_resource() -> str:
        """Read the projected quest board; no source-board write is performed."""
        return game.board_markdown()

    @mcp.resource("athena://meta-ml-game/v3/source-adapters")
    def mmlg3_adapters_resource() -> str:
        """Read the four digest-only source observation adapter contracts."""
        return _render(game.adapters())

    @mcp.resource("athena://meta-ml-game/v3/status")
    def mmlg3_status_resource() -> str:
        """Read MMLG.3 runtime and authority status."""
        return _render(game.status())
