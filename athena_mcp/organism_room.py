
from __future__ import annotations

import hashlib
import json
import posixpath
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from .message_board import (
    BOARD_ROOT,
    PRESENCE_ARTIFACT,
    MessageBoardRuntime,
    _iso,
    _json_text,
    _parse_time,
    _require_id,
)

TOOL_NAME = "athena_organism_room"
TOOL_NAMES = {TOOL_NAME}
ROOM_AGENT_ROOT = f"{BOARD_ROOT}/room/agents"
ROOM_EVENT_ROOT = f"{BOARD_ROOT}/room/events"
ROOM_ARTIFACT = "ATHENA.ORGANISM.ROOM.PRESENCE.V1"
ROOM_EVENT_ARTIFACT = "ATHENA.ORGANISM.ROOM.EVENT.V1"
ROOM_SNAPSHOT_ARTIFACT = "ATHENA.ORGANISM.ROOM.SNAPSHOT.V1"
ALLOCATION_ARTIFACT = "ATHENA.SWARM.HOMEOSTASIS.ALLOCATION.V1"
POLICY_VERSION = "ATHENA.SWARM.HOMEOSTASIS.V1"

_ACTIONS = {"read", "enter", "heartbeat", "bind", "leave", "allocate"}
_WAVES = ("W0", "W1", "W2")
_WAVE_WEIGHTS = {"W0": 0.50, "W1": 0.30, "W2": 0.20}
_DOMAINS = ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META")
_DOMAIN_WEIGHTS = {
    "GIT": 0.20,
    "MATH": 0.15,
    "NAV": 0.15,
    "CORPUS": 0.15,
    "TOOLS": 0.10,
    "ALCHEMY": 0.10,
    "MYTH": 0.05,
    "META": 0.10,
}
_LEAVE_STATES = {"BOUNDARY", "NO_POSITIVE_FRONTIER", "USER_CHOICE", "PAUSED", "CRASH_RECOVERY"}

LAWS = [
    "ROOM_ENTRY != WORK_CLAIM",
    "ALLOCATION != CLAIM != EXECUTION_AUTHORITY",
    "SCHEDULED_WAKE != LIVE_WORKER",
    "PERCENT_TARGET != MAKEWORK",
    "CAPABILITY_CLAIM != TOOL_OR_AUTHORITY_WITNESS",
    "HEARTBEAT != PROGRESS",
    "LEASE_EXPIRY != COMPLETION",
    "SIGNOUT != VERIFIED_DELTA",
    "ONE_OWNERSHIP_KEY => ONE_PRIMARY",
    "UNKNOWN != ZERO",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _norm_text(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).casefold().split())


def normalize_target(value: Any) -> str:
    raw = unicodedata.normalize("NFKC", str(value or "")).strip().replace("\\", "/")
    if not raw:
        return ""
    prefix = ""
    if "://" in raw:
        prefix, raw = raw.split("://", 1)
        prefix = prefix.casefold() + "://"
    normalized = posixpath.normpath("/" + raw).lstrip("/")
    if normalized in {"", "."}:
        return ""
    return prefix + normalized.casefold().rstrip("/")


def _require_head(value: Any, field: str = "head") -> str:
    text = str(value or "")
    if len(text) != 40 or any(ch not in "0123456789abcdef" for ch in text.casefold()):
        raise ValueError(f"{field} must be a 40-character Git SHA")
    return text.casefold()


def _lease(value: Any) -> int:
    seconds = int(value or 1800)
    if seconds < 60 or seconds > 86400:
        raise ValueError("lease_seconds must be between 60 and 86400")
    return seconds


def _room_event(kind: str, agent_id: str, session_id: str, payload: dict) -> tuple[str, dict]:
    now = datetime.now(timezone.utc)
    event_id = f"ORE-{uuid.uuid4().hex}"
    event = {
        "artifact": ROOM_EVENT_ARTIFACT,
        "event_id": event_id,
        "kind": kind,
        "agent_id": agent_id,
        "session_id": session_id,
        "created_at": _iso(now),
        "payload": payload,
    }
    rel = f"{ROOM_EVENT_ROOT}/{now:%Y/%m/%d}/{event_id}.json"
    return rel, event


def _active(row: dict, now: datetime) -> bool:
    if str(row.get("status")) != "ACTIVE":
        return False
    expires = _parse_time(row.get("expires_at"))
    return bool(expires and expires > now)


def _integer_history(history: dict | None, keys: Iterable[str]) -> dict[str, int]:
    raw = history or {}
    return {key: max(0, int(raw.get(key, 0))) for key in keys}


def _cumulative_quota(keys: tuple[str, ...], weights: dict[str, float], seats: int, history: dict[str, int]) -> dict[str, int]:
    if seats <= 0:
        return {key: 0 for key in keys}
    prior_total = sum(history.values())
    desired_after = {key: weights[key] * (prior_total + seats) for key in keys}
    quotas = {key: 0 for key in keys}
    for _ in range(seats):
        winner = max(
            keys,
            key=lambda key: (
                desired_after[key] - (history[key] + quotas[key]),
                weights[key],
                -keys.index(key),
            ),
        )
        quotas[winner] += 1
    return quotas


def _quest_score(quest: dict, wave_deficit: float, domain_deficit: float) -> tuple:
    priority = int(quest.get("priority", 0))
    age = max(0, int(quest.get("ready_seq", 0)))
    verified_gain = float(quest.get("verified_gain", 0.0))
    information_gain = float(quest.get("information_gain", 0.0))
    cost = max(0.0, float(quest.get("cost", 0.0)))
    risk = max(0.0, float(quest.get("risk", 0.0)))
    return (
        priority,
        wave_deficit,
        domain_deficit,
        age,
        verified_gain,
        information_gain,
        -(cost + risk),
        str(quest.get("quest_id") or ""),
    )


def allocate_homeostasis(
    *,
    workers: list[dict],
    quests: list[dict],
    current_head: str,
    current_frontier_digest: str,
    epoch: int = 0,
    history: dict | None = None,
) -> dict:
    """Pure deterministic advisory allocator.

    It never claims work. Its output is valid only for the exact frozen head,
    frontier digest, workers and quests whose digest it carries.
    """

    head = _require_head(current_head, "current_head")
    worker_rows = sorted(
        [dict(row) for row in workers if row.get("agent_id") and row.get("session_id")],
        key=lambda row: (str(row["agent_id"]), str(row["session_id"])),
    )
    wave_history = _integer_history((history or {}).get("waves"), _WAVES)
    domain_history = _integer_history((history or {}).get("domains"), _DOMAINS)

    eligible = []
    holds = []
    for raw in quests:
        quest = dict(raw)
        qid = str(quest.get("quest_id") or "").strip()
        wave = str(quest.get("wave") or "").upper()
        domain = str(quest.get("domain") or "").upper()
        ownership = _norm_text(quest.get("ownership_key"))
        if not qid or wave not in _WAVES or domain not in _DOMAINS or not ownership:
            holds.append({"quest_id": qid or None, "reason": "MALFORMED_QUEST"})
            continue
        if str(quest.get("expected_head") or head) != head:
            holds.append({"quest_id": qid, "reason": "STALE_HEAD"})
            continue
        if quest.get("authority") in {None, "", "UNKNOWN", "HOLD"}:
            holds.append({"quest_id": qid, "reason": "AUTHORITY_UNKNOWN_OR_HELD"})
            continue
        if quest.get("positive_value") is not True:
            holds.append({"quest_id": qid, "reason": "NO_POSITIVE_VALUE_WITNESS"})
            continue
        quest["wave"] = wave
        quest["domain"] = domain
        quest["_ownership"] = ownership
        quest["_targets"] = {normalize_target(x) for x in (quest.get("targets") or []) if normalize_target(x)}
        eligible.append(quest)

    seats = min(len(worker_rows), len({q["_ownership"] for q in eligible}))
    wave_quota = _cumulative_quota(_WAVES, _WAVE_WEIGHTS, seats, wave_history)
    domain_quota = _cumulative_quota(_DOMAINS, _DOMAIN_WEIGHTS, seats, domain_history)
    assigned: list[dict] = []
    used_workers: set[str] = set()
    used_ownership: set[str] = set()
    used_targets: set[str] = set()
    used_quests: set[str] = set()
    wave_used = {key: 0 for key in _WAVES}
    domain_used = {key: 0 for key in _DOMAINS}

    # Greedy matroid-style selection over unit-capacity workers/quests/ownership
    # keys. Tie-breaking is canonical, so input permutations replay identically.
    while len(assigned) < seats:
        candidates = []
        for worker in worker_rows:
            aid = str(worker["agent_id"])
            if aid in used_workers:
                continue
            capabilities = {_norm_text(x) for x in (worker.get("capabilities") or [])}
            domains = {str(x).upper() for x in (worker.get("domains") or _DOMAINS)}
            waves = {str(x).upper() for x in (worker.get("waves") or _WAVES)}
            for quest in eligible:
                qid = str(quest["quest_id"])
                if qid in used_quests or quest["_ownership"] in used_ownership:
                    continue
                if quest["_targets"] & used_targets:
                    continue
                if quest["wave"] not in waves or quest["domain"] not in domains:
                    continue
                required = {_norm_text(x) for x in (quest.get("required_capabilities") or [])}
                if not required.issubset(capabilities):
                    continue
                wdef = wave_quota[quest["wave"]] - wave_used[quest["wave"]]
                ddef = domain_quota[quest["domain"]] - domain_used[quest["domain"]]
                score = _quest_score(quest, wdef, ddef)
                candidates.append((score, aid, qid, worker, quest))
        if not candidates:
            break
        # descending semantic score, then ascending canonical identity
        candidates.sort(key=lambda row: (row[1], row[2]))
        score, aid, qid, worker, quest = max(candidates, key=lambda row: row[0])
        used_workers.add(aid)
        used_quests.add(qid)
        used_ownership.add(quest["_ownership"])
        used_targets.update(quest["_targets"])
        wave_used[quest["wave"]] += 1
        domain_used[quest["domain"]] += 1
        assigned.append({
            "agent_id": aid,
            "session_id": worker["session_id"],
            "quest_id": qid,
            "wave": quest["wave"],
            "domain": quest["domain"],
            "ownership_key": quest["_ownership"],
            "targets": sorted(quest["_targets"]),
            "standing": "ADVISORY_REQUIRES_MESSAGE_BOARD_CLAIM",
        })

    basis = {
        "policy_version": POLICY_VERSION,
        "epoch": int(epoch),
        "current_head": head,
        "current_frontier_digest": str(current_frontier_digest),
        "workers": worker_rows,
        "quests": sorted(
            [{k: v for k, v in q.items() if not k.startswith("_")} for q in eligible],
            key=lambda q: str(q["quest_id"]),
        ),
        "history": {"waves": wave_history, "domains": domain_history},
        "assignments": assigned,
        "holds": sorted(holds, key=lambda row: (str(row.get("quest_id")), row["reason"])),
    }
    digest = _sha(basis)
    return {
        "artifact": ALLOCATION_ARTIFACT,
        **basis,
        "wave_target": _WAVE_WEIGHTS,
        "domain_target": _DOMAIN_WEIGHTS,
        "wave_quota": wave_quota,
        "domain_quota": domain_quota,
        "coverage_holds": [
            wave for wave in _WAVES
            if wave_quota[wave] and not any(a["wave"] == wave for a in assigned)
        ],
        "allocation_digest": digest,
        "authority": "ADVISORY_ONLY",
        "laws": list(LAWS),
    }


class OrganismRoomRuntime:
    def __init__(self, git):
        self.git = git
        self.board = MessageBoardRuntime(git)

    def _root(self) -> Path:
        return self.board._root()

    def _rows(self) -> list[dict]:
        root = self._root() / ROOM_AGENT_ROOT
        if not root.exists():
            return []
        rows = []
        for path in sorted(root.glob("*.json")):
            value = self.board._read_json(path)
            if value and value.get("artifact") == ROOM_ARTIFACT:
                rows.append(value)
        return rows

    def _path(self, agent_id: str) -> str:
        return f"{ROOM_AGENT_ROOT}/{_require_id(agent_id, 'agent_id')}.json"

    def snapshot(self, *, include_stale: bool = False, remote_sync: dict | None = None) -> dict:
        now = datetime.now(timezone.utc)
        rows = self._rows()
        active = sorted([r for r in rows if _active(r, now)], key=lambda r: str(r["agent_id"]))
        inactive = sorted([r for r in rows if not _active(r, now)], key=lambda r: str(r["agent_id"]))
        working = {str(r.get("agent_id")) for r in self.board._active()}
        result = {
            "artifact": ROOM_SNAPSHOT_ARTIFACT,
            "status": "OK",
            "git_head": self.git.head(),
            "active": active,
            "inactive": inactive if include_stale else [],
            "n_live": len(active),
            "n_working": len({str(r["agent_id"]) for r in active} & working),
            "hidden_process_count": "UNKNOWN",
            "true_simultaneous_process_count": "UNKNOWN",
            "laws": list(LAWS),
            "remote_sync": remote_sync or {},
        }
        result["snapshot_digest"] = _sha({
            "git_head": result["git_head"],
            "active": active,
            "working": sorted(working),
        })
        return result

    def read(self, *, include_stale: bool = False, remote: str = "origin", shared_remote_mode: str = "REQUIRED") -> dict:
        sync = self.board._sync(remote, shared_remote_mode)
        if str(shared_remote_mode).upper() == "REQUIRED" and not sync.get("shared_frontier_verified"):
            return {**sync, "artifact": ROOM_SNAPSHOT_ARTIFACT}
        return self.snapshot(include_stale=include_stale, remote_sync=sync)

    def enter(
        self,
        *,
        agent_id: str,
        session_id: str,
        expected_head: str,
        prompt_stack_digest: str,
        capabilities=None,
        waves=None,
        domains=None,
        authority_witnesses=None,
        lease_seconds: int = 1800,
        remote: str = "origin",
    ) -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        session_id = _require_id(session_id, "session_id")
        expected_head = _require_head(expected_head, "expected_head")
        lease = _lease(lease_seconds)
        wave_list = sorted({str(x).upper() for x in (waves or _WAVES)})
        domain_list = sorted({str(x).upper() for x in (domains or _DOMAINS)})
        if not set(wave_list).issubset(_WAVES) or not set(domain_list).issubset(_DOMAINS):
            raise ValueError("invalid wave/domain")
        cap_list = sorted({_norm_text(x) for x in (capabilities or []) if _norm_text(x)})
        witnesses = sorted({_norm_text(x) for x in (authority_witnesses or []) if _norm_text(x)})

        def build(base):
            if base != expected_head:
                return {"return": {"status": "STALE_HEAD_HOLD", "expected_head": expected_head, "current_head": base}}
            now = datetime.now(timezone.utc)
            existing = next((r for r in self._rows() if r.get("agent_id") == agent_id), None)
            if existing and _active(existing, now):
                if existing.get("session_id") != session_id:
                    return {"return": {"status": "AGENT_SESSION_ALREADY_ACTIVE_HOLD", "presence": existing}}
                updated = dict(existing)
                updated.update({"heartbeat_at": _iso(now), "expires_at": _iso(now + timedelta(seconds=lease)), "lease_seconds": lease})
                rel, event = _room_event("ROOM_HEARTBEAT", agent_id, session_id, {"reason": "IDEMPOTENT_ENTER"})
                return {"files": {self._path(agent_id): _json_text(updated), rel: _json_text(event)}, "message": f"organism room re-enter {agent_id}", "result": {"status": "ALREADY_ENTERED", "presence": updated}}
            presence = {
                "artifact": ROOM_ARTIFACT,
                "agent_id": agent_id,
                "session_id": session_id,
                "status": "ACTIVE",
                "entered_at": _iso(now),
                "heartbeat_at": _iso(now),
                "lease_seconds": lease,
                "expires_at": _iso(now + timedelta(seconds=lease)),
                "entry_head": base,
                "prompt_stack_digest": str(prompt_stack_digest),
                "capabilities": cap_list,
                "waves": wave_list,
                "domains": domain_list,
                "authority_witnesses": witnesses,
                "bound_claim_id": None,
            }
            rel, event = _room_event("ROOM_ENTER", agent_id, session_id, {"entry_head": base})
            return {"files": {self._path(agent_id): _json_text(presence), rel: _json_text(event)}, "message": f"organism room enter {agent_id}", "result": {"status": "ENTERED", "presence": presence}}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def heartbeat(self, *, agent_id: str, expected_session_id: str, lease_seconds: int | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        expected_session_id = _require_id(expected_session_id, "expected_session_id")

        def build(base):
            now = datetime.now(timezone.utc)
            row = next((r for r in self._rows() if r.get("agent_id") == agent_id), None)
            if not row or not _active(row, now):
                return {"return": {"status": "ROOM_NOT_ACTIVE_HOLD"}}
            if row.get("session_id") != expected_session_id:
                return {"return": {"status": "STALE_SESSION_HOLD", "current_session_id": row.get("session_id")}}
            lease = _lease(lease_seconds or row.get("lease_seconds"))
            updated = dict(row)
            updated.update({"heartbeat_at": _iso(now), "expires_at": _iso(now + timedelta(seconds=lease)), "lease_seconds": lease})
            rel, event = _room_event("ROOM_HEARTBEAT", agent_id, expected_session_id, {})
            return {"files": {self._path(agent_id): _json_text(updated), rel: _json_text(event)}, "message": f"organism room heartbeat {agent_id}", "result": {"status": "HEARTBEAT", "presence": updated}}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def bind(self, *, agent_id: str, expected_session_id: str, expected_claim_id: str, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        expected_session_id = _require_id(expected_session_id, "expected_session_id")
        expected_claim_id = _require_id(expected_claim_id, "expected_claim_id")

        def build(base):
            now = datetime.now(timezone.utc)
            room = next((r for r in self._rows() if r.get("agent_id") == agent_id), None)
            claim = next((r for r in self.board._active() if r.get("agent_id") == agent_id), None)
            if not room or not _active(room, now) or room.get("session_id") != expected_session_id:
                return {"return": {"status": "ROOM_SESSION_HOLD"}}
            if not claim or claim.get("claim_id") != expected_claim_id:
                return {"return": {"status": "CLAIM_BINDING_HOLD", "current_claim_id": claim.get("claim_id") if claim else None}}
            updated = dict(room)
            updated["bound_claim_id"] = expected_claim_id
            rel, event = _room_event("ROOM_WORK_BOUND", agent_id, expected_session_id, {"claim_id": expected_claim_id})
            return {"files": {self._path(agent_id): _json_text(updated), rel: _json_text(event)}, "message": f"organism room bind {agent_id}", "result": {"status": "BOUND", "presence": updated}}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def leave(
        self,
        *,
        agent_id: str,
        expected_session_id: str,
        stop_class: str,
        completed_delta_refs=None,
        failed_or_held_refs=None,
        residual_portfolio=None,
        successor_routes=None,
        remote: str = "origin",
    ) -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        expected_session_id = _require_id(expected_session_id, "expected_session_id")
        stop_class = str(stop_class or "").upper()
        if stop_class not in _LEAVE_STATES:
            raise ValueError(f"stop_class must be one of {sorted(_LEAVE_STATES)}")
        completed = sorted({str(x).strip() for x in (completed_delta_refs or []) if str(x).strip()})
        held = sorted({str(x).strip() for x in (failed_or_held_refs or []) if str(x).strip()})
        residuals = [dict(x) if isinstance(x, dict) else {"residual": str(x)} for x in (residual_portfolio or [])]
        successors = [dict(x) if isinstance(x, dict) else {"route": str(x)} for x in (successor_routes or [])]

        def build(base):
            now = datetime.now(timezone.utc)
            row = next((r for r in self._rows() if r.get("agent_id") == agent_id), None)
            if not row:
                return {"return": {"status": "NOT_IN_ROOM"}}
            if row.get("session_id") != expected_session_id:
                return {"return": {"status": "STALE_SESSION_HOLD", "current_session_id": row.get("session_id")}}
            if str(row.get("status")) != "ACTIVE":
                return {"return": {"status": "ALREADY_LEFT", "presence": row}}
            active_claim = next((r for r in self.board._active() if r.get("agent_id") == agent_id), None)
            if active_claim:
                return {"return": {"status": "ACTIVE_WORK_CLAIM_HOLD", "claim_id": active_claim.get("claim_id"), "next": "release/handoff the exact claim before room leave"}}
            updated = dict(row)
            updated.update({
                "status": "LEFT",
                "left_at": _iso(now),
                "stop_class": stop_class,
                "completed_delta_refs": completed,
                "failed_or_held_refs": held,
                "residual_portfolio": residuals,
                "successor_routes": successors,
            })
            rel, event = _room_event("ROOM_LEAVE", agent_id, expected_session_id, {
                "stop_class": stop_class,
                "completed_delta_refs": completed,
                "failed_or_held_refs": held,
                "residual_portfolio": residuals,
                "successor_routes": successors,
                "completion_standing": "REFERENCED_NOT_VERIFIED_BY_ROOM",
            })
            return {"files": {self._path(agent_id): _json_text(updated), rel: _json_text(event)}, "message": f"organism room leave {agent_id}", "result": {"status": "LEFT", "presence": updated, "completion_standing": "REFERENCED_NOT_VERIFIED_BY_ROOM"}}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def call_tool(self, name: str, arguments: dict):
        if name != TOOL_NAME:
            raise KeyError(name)
        a = dict(arguments or {})
        action = str(a.get("action") or "").lower()
        if action not in _ACTIONS:
            raise ValueError(f"action must be one of {sorted(_ACTIONS)}")
        if action == "read":
            return self.read(include_stale=bool(a.get("include_stale", False)), remote=a.get("remote", "origin"), shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"))
        if action == "enter":
            return self.enter(agent_id=a["agent_id"], session_id=a["session_id"], expected_head=a["expected_head"], prompt_stack_digest=a["prompt_stack_digest"], capabilities=a.get("capabilities"), waves=a.get("waves"), domains=a.get("domains"), authority_witnesses=a.get("authority_witnesses"), lease_seconds=a.get("lease_seconds", 1800), remote=a.get("remote", "origin"))
        if action == "heartbeat":
            return self.heartbeat(agent_id=a["agent_id"], expected_session_id=a["expected_session_id"], lease_seconds=a.get("lease_seconds"), remote=a.get("remote", "origin"))
        if action == "bind":
            return self.bind(agent_id=a["agent_id"], expected_session_id=a["expected_session_id"], expected_claim_id=a["expected_claim_id"], remote=a.get("remote", "origin"))
        if action == "leave":
            return self.leave(agent_id=a["agent_id"], expected_session_id=a["expected_session_id"], stop_class=a["stop_class"], completed_delta_refs=a.get("completed_delta_refs"), failed_or_held_refs=a.get("failed_or_held_refs"), residual_portfolio=a.get("residual_portfolio"), successor_routes=a.get("successor_routes"), remote=a.get("remote", "origin"))
        if action == "allocate":
            return allocate_homeostasis(workers=a.get("workers") or [], quests=a.get("quests") or [], current_head=a["current_head"], current_frontier_digest=a["current_frontier_digest"], epoch=a.get("epoch", 0), history=a.get("history"))
        raise KeyError(action)


TOOLS = [{
    "name": TOOL_NAME,
    "description": "Enter and leave the shared ATHENA organism room independently of work claims, derive a truthful live census, bind a room session to an exact Message Board claim, and compile deterministic 50/30/20 homeostasis guidance. Allocation is advisory and never grants claim or execution authority.",
    "inputSchema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": sorted(_ACTIONS)},
            "agent_id": {"type": ["string", "null"]},
            "session_id": {"type": ["string", "null"]},
            "expected_session_id": {"type": ["string", "null"]},
            "expected_claim_id": {"type": ["string", "null"]},
            "expected_head": {"type": ["string", "null"]},
            "prompt_stack_digest": {"type": ["string", "null"]},
            "capabilities": {"type": "array", "items": {"type": "string"}},
            "authority_witnesses": {"type": "array", "items": {"type": "string"}},
            "waves": {"type": "array", "items": {"type": "string", "enum": list(_WAVES)}},
            "domains": {"type": "array", "items": {"type": "string", "enum": list(_DOMAINS)}},
            "lease_seconds": {"type": ["integer", "null"], "minimum": 60, "maximum": 86400},
            "stop_class": {"type": ["string", "null"], "enum": sorted(_LEAVE_STATES) + [None]},
            "completed_delta_refs": {"type": "array", "items": {"type": "string"}},
            "failed_or_held_refs": {"type": "array", "items": {"type": "string"}},
            "residual_portfolio": {"type": "array"},
            "successor_routes": {"type": "array"},
            "workers": {"type": "array", "items": {"type": "object"}},
            "quests": {"type": "array", "items": {"type": "object"}},
            "current_head": {"type": ["string", "null"]},
            "current_frontier_digest": {"type": ["string", "null"]},
            "epoch": {"type": "integer", "minimum": 0},
            "history": {"type": ["object", "null"]},
            "include_stale": {"type": "boolean"},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]}
        },
        "additionalProperties": False
    }
}]

