from __future__ import annotations

import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .git_backend import GitBackend, GitStateError, GitStaleHead
from .prompt_remote import PromptRemoteSync

BOARD_ROOT = "runtime/message_board/v1"
AGENT_ROOT = f"{BOARD_ROOT}/agents"
EVENT_ROOT = f"{BOARD_ROOT}/events"
PRESENCE_ARTIFACT = "ATHENA.MESSAGE.BOARD.PRESENCE.V1"
EVENT_ARTIFACT = "ATHENA.MESSAGE.BOARD.EVENT.V1"
SNAPSHOT_ARTIFACT = "ATHENA.MESSAGE.BOARD.SNAPSHOT.V1"
TOOL_NAME = "athena_message_board"

_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_ACTIONS = {"read", "present", "join", "heartbeat", "post", "ack", "release"}
_MESSAGE_KINDS = {"UPDATE", "QUESTION", "ANSWER", "BLOCKER", "DISCOVERY", "HELP", "HANDOFF", "INFO"}
_REMOTE_MODES = {"REQUIRED", "BEST_EFFORT", "DISABLED"}
_RELEASE_STATES = {"DONE", "PAUSED", "HANDOFF", "ABANDONED"}

LAWS = [
    "READ_BOARD_BEFORE_EXPENSIVE_SHARED_WORK",
    "PRESENT_BEFORE_WORK",
    "EXACT_OVERLAP_WITHOUT_DECLARED_COORDINATION => DUPLICATE_WORK_HOLD",
    "COLLABORATION_OR_REPLICATION_MUST_BE_EXPLICIT",
    "FUZZY_SIMILARITY != DUPLICATE_PROOF",
    "LEASE_EXPIRY != COMPLETION",
    "MESSAGE_ROUTE != CONSUMPTION",
    "LOCAL_COMMIT != SHARED_RETURN",
    "SHARED_MUTATION_REQUIRES_FRESH_REMOTE_FRONTIER",
    "RACE_LOSER_REHYDRATES_BEFORE_RETRY",
]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _utcnow()).isoformat()


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.replace(tzinfo=dt.tzinfo or timezone.utc).astimezone(timezone.utc)


def _require_id(value: str, field: str) -> str:
    value = str(value or "")
    if not _ID_RE.fullmatch(value):
        raise ValueError(f"invalid {field}")
    return value


def _norm(value: str | None) -> str:
    return " ".join(str(value or "").casefold().split())


def _norm_target(value: str) -> str:
    return str(value or "").strip().replace("\\", "/").casefold().rstrip("/")


def _tokens(value: str | None) -> set[str]:
    return {token.casefold() for token in _TOKEN_RE.findall(str(value or "")) if len(token) > 1}


def _jaccard(a: str | None, b: str | None) -> tuple[float, int]:
    left, right = _tokens(a), _tokens(b)
    if not left or not right:
        return 0.0, 0
    shared = len(left & right)
    return shared / len(left | right), shared


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


class MessageBoardRuntime:
    """Git-backed inter-agent presence, claim, and message board.

    Board state is coordination state, not execution authority or world truth.
    Writes are local CAS commits followed by verified ordinary non-force publish.
    """

    def __init__(self, git: GitBackend):
        self.git = git
        self.remote_sync = PromptRemoteSync(git)

    def _root(self) -> Path:
        if not self.git.enabled:
            raise GitStateError("ATHENA_GIT_ROOT is required for message board")
        return self.git.root

    @staticmethod
    def _remote_mode(value: str | None) -> str:
        mode = str(value or "REQUIRED").upper()
        if mode not in _REMOTE_MODES:
            raise ValueError("shared_remote_mode must be REQUIRED, BEST_EFFORT, or DISABLED")
        return mode

    def _sync(self, remote: str, mode: str) -> dict:
        mode = self._remote_mode(mode)
        if mode == "DISABLED":
            return {"status": "DISABLED", "remote": remote, "shared_frontier_verified": False}
        state = self.remote_sync.sync(remote)
        if mode == "REQUIRED" and not state.get("shared_frontier_verified"):
            return {
                **state,
                "status": "MESSAGE_BOARD_SHARED_FRONTIER_HOLD",
                "shared_frontier_verified": False,
                "law": "COORDINATION_VIEW_MUST_BE_SHARED_CURRENT_BEFORE_DECISION",
            }
        return state

    @staticmethod
    def _lease_state(row: dict, now: datetime | None = None) -> str:
        if str(row.get("status")) != "ACTIVE":
            return str(row.get("status") or "UNKNOWN")
        expires = _parse_time(row.get("expires_at"))
        if expires is None or expires <= (now or _utcnow()):
            return "STALE"
        return "ACTIVE"

    def _read_json(self, path: Path) -> dict | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def _presence_rows(self) -> list[dict]:
        root = self._root() / AGENT_ROOT
        if not root.exists():
            return []
        rows = []
        for path in sorted(root.glob("*.json")):
            value = self._read_json(path)
            if value and value.get("artifact") == PRESENCE_ARTIFACT:
                rows.append(value)
        return rows

    def _events(self) -> list[dict]:
        root = self._root() / EVENT_ROOT
        if not root.exists():
            return []
        rows = []
        for path in root.rglob("*.json"):
            value = self._read_json(path)
            if value and value.get("artifact") == EVENT_ARTIFACT:
                rows.append(value)
        return sorted(rows, key=lambda x: (str(x.get("created_at")), str(x.get("event_id"))))

    def _active(self, rows: list[dict] | None = None) -> list[dict]:
        now = _utcnow()
        return [r for r in (rows if rows is not None else self._presence_rows()) if self._lease_state(r, now) == "ACTIVE"]

    @staticmethod
    def _targets(row: dict) -> set[str]:
        return {_norm_target(str(x)) for x in (row.get("targets") or []) if _norm_target(str(x))}

    @classmethod
    def _hard_overlap(cls, candidate: dict, other: dict) -> list[str]:
        reasons = []
        left_key, right_key = _norm(candidate.get("work_key")), _norm(other.get("work_key"))
        if left_key and right_key and left_key == right_key:
            reasons.append("EXACT_WORK_KEY")
        left_task, right_task = _norm(candidate.get("task")), _norm(other.get("task"))
        if left_task and right_task and left_task == right_task:
            reasons.append("EXACT_TASK")
        target_overlap = sorted(cls._targets(candidate) & cls._targets(other))
        if target_overlap:
            reasons.append("TARGET:" + ",".join(target_overlap))
        return reasons

    @staticmethod
    def _intentional_pair(left: dict, right: dict) -> bool:
        left_join = str(left.get("join_of") or "")
        right_join = str(right.get("join_of") or "")
        left_claim = str(left.get("claim_id") or "")
        right_claim = str(right.get("claim_id") or "")
        return bool(
            (left_join and left_join == right_claim)
            or (right_join and right_join == left_claim)
            or (left_join and right_join and left_join == right_join)
            or str(left.get("mode")) == "REPLICA"
            or str(right.get("mode")) == "REPLICA"
        )

    def _overlap_edges(self, active: list[dict]) -> tuple[list[dict], list[dict]]:
        exact, potential = [], []
        for i, left in enumerate(active):
            for right in active[i + 1 :]:
                hard = self._hard_overlap(left, right)
                if hard:
                    exact.append({
                        "agents": [left.get("agent_id"), right.get("agent_id")],
                        "reasons": hard,
                        "intentional": self._intentional_pair(left, right),
                    })
                    continue
                score, shared = _jaccard(left.get("task"), right.get("task"))
                if score >= 0.65 and shared >= 3:
                    potential.append({
                        "agents": [left.get("agent_id"), right.get("agent_id")],
                        "task_similarity": round(score, 4),
                        "shared_tokens": shared,
                        "classification": "POTENTIAL_OVERLAP_ONLY",
                    })
        return exact, potential

    @staticmethod
    def _message_visible_to(event: dict, agent_id: str) -> bool:
        recipients = [str(x) for x in (event.get("recipients") or [])]
        return not recipients or agent_id in recipients

    def _unread(self, events: list[dict], agent_id: str) -> list[dict]:
        acked = {
            str((event.get("payload") or {}).get("message_id"))
            for event in events
            if event.get("kind") == "ACK" and event.get("agent_id") == agent_id
        }
        return [
            event for event in events
            if event.get("kind") == "MESSAGE"
            and event.get("agent_id") != agent_id
            and self._message_visible_to(event, agent_id)
            and str(event.get("event_id")) not in acked
        ]

    def snapshot(self, *, agent_id: str | None = None, limit: int = 50, include_stale: bool = False, remote_sync: dict | None = None) -> dict:
        rows = self._presence_rows()
        active = self._active(rows)
        exact, potential = self._overlap_edges(active)
        events = self._events()
        limit = max(1, min(int(limit or 50), 500))
        inactive = []
        if include_stale:
            inactive = [{**row, "lease_state": self._lease_state(row)} for row in rows if self._lease_state(row) != "ACTIVE"]
        value = {
            "artifact": SNAPSHOT_ARTIFACT,
            "status": "OK",
            "git_head": self.git.head(),
            "active": sorted(active, key=lambda x: str(x.get("agent_id"))),
            "inactive": sorted(inactive, key=lambda x: str(x.get("agent_id"))),
            "exact_overlaps": exact,
            "potential_overlaps": potential,
            "recent_events": events[-limit:],
            "laws": list(LAWS),
        }
        if agent_id:
            agent_id = _require_id(agent_id, "agent_id")
            value["self"] = next((r for r in rows if r.get("agent_id") == agent_id), None)
            value["unread_messages"] = self._unread(events, agent_id)[-limit:]
        if remote_sync is not None:
            value["remote_sync"] = remote_sync
            value["shared_frontier_verified"] = bool(remote_sync.get("shared_frontier_verified"))
        return value

    def read(self, *, agent_id: str | None = None, limit: int = 50, include_stale: bool = False, remote: str = "origin", shared_remote_mode: str = "REQUIRED") -> dict:
        mode = self._remote_mode(shared_remote_mode)
        sync = self._sync(remote, mode)
        value = self.snapshot(agent_id=agent_id, limit=limit, include_stale=include_stale, remote_sync=sync)
        if mode == "REQUIRED" and not sync.get("shared_frontier_verified"):
            value["status"] = "MESSAGE_BOARD_SHARED_FRONTIER_HOLD"
        elif mode == "BEST_EFFORT" and not sync.get("shared_frontier_verified"):
            value["status"] = "OK_UNVERIFIED"
        return value

    def _event(self, kind: str, agent_id: str, payload: dict | None = None, recipients=None, reply_to=None) -> tuple[str, dict]:
        now = _utcnow()
        event_id = f"MBE-{uuid.uuid4().hex}"
        event = {
            "artifact": EVENT_ARTIFACT,
            "event_id": event_id,
            "kind": kind,
            "agent_id": agent_id,
            "created_at": _iso(now),
            "git_parent": self.git.head(),
            "payload": payload or {},
            "recipients": list(recipients or []),
            "reply_to": reply_to,
            "law": "MESSAGE_ROUTE != CONSUMPTION" if kind == "MESSAGE" else "BOARD_EVENT != EXECUTION_AUTHORITY",
        }
        return f"{EVENT_ROOT}/{now:%Y/%m/%d}/{event_id}.json", event

    def _commit_files(self, expected_head: str, files: dict[str, str], actor: str, message: str) -> dict:
        current = self.git.head()
        if current != expected_head:
            raise GitStaleHead(json.dumps({"status": "STALE_GIT_HEAD", "expected": expected_head, "current": current}))
        if self.git._git("status", "--porcelain"):
            raise GitStateError("DIRTY_GIT_ROOT: message-board write refuses unrelated working-tree state")
        actor = _require_id(actor, "agent_id")
        rels = sorted(files)
        for rel in rels:
            if not rel.startswith(BOARD_ROOT + "/"):
                raise ValueError("message board may only write under runtime/message_board/v1/")
        try:
            for rel, text in files.items():
                path = self._root() / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            self.git._git("add", "--", *rels)
            staged = self.git._git("diff", "--cached", "--name-only")
            if not staged:
                return {"status": "NO_CHANGES", "head": current, "previous_head": current, "paths": rels}
            env = os.environ.copy()
            env.setdefault("GIT_AUTHOR_NAME", actor)
            env.setdefault("GIT_AUTHOR_EMAIL", "athena@local")
            env.setdefault("GIT_COMMITTER_NAME", actor)
            env.setdefault("GIT_COMMITTER_EMAIL", "athena@local")
            proc = subprocess.run(["git", "-C", str(self._root()), "commit", "-m", message], text=True, capture_output=True, env=env)
            if proc.returncode:
                raise GitStateError(proc.stderr.strip() or proc.stdout.strip())
        except Exception:
            self.git._git("reset", "--hard", current)
            raise
        return {"status": "COMMITTED_LOCAL", "head": self.git.head(), "previous_head": current, "paths": rels, "shared_remote": False}

    def _safe_race_reset(self, base_head: str, created_head: str, remote_head: str | None) -> bool:
        if not remote_head or self.git.head() != created_head or self.git._git("status", "--porcelain"):
            return False
        try:
            parent = self.git._git("rev-parse", f"{created_head}^")
            changed = self.git._git("diff", "--name-only", f"{base_head}..{created_head}").splitlines()
            ancestor = subprocess.run(["git", "-C", str(self._root()), "merge-base", "--is-ancestor", base_head, remote_head], text=True, capture_output=True).returncode == 0
        except GitStateError:
            return False
        if parent != base_head or not ancestor:
            return False
        if any(not str(path).startswith(BOARD_ROOT + "/") for path in changed if path.strip()):
            return False
        self.git._git("reset", "--hard", base_head)
        return True

    def _mutate(self, *, agent_id: str, remote: str, build_files, max_retries: int = 3) -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        for attempt in range(1, max_retries + 1):
            sync = self._sync(remote, "REQUIRED")
            if not sync.get("shared_frontier_verified"):
                return {"status": "MESSAGE_BOARD_SHARED_FRONTIER_HOLD", "remote_sync": sync, "durable_return": False, "laws": list(LAWS)}
            base = self.git.head()
            plan = build_files(base)
            if plan.get("return") is not None:
                value = dict(plan["return"])
                value.setdefault("git_head", base)
                value.setdefault("remote_sync", sync)
                value.setdefault("durable_return", True)
                value.setdefault("laws", list(LAWS))
                return value
            commit = self._commit_files(base, plan["files"], agent_id, plan["message"])
            if commit["status"] == "NO_CHANGES":
                value = dict(plan.get("result") or {})
                value.setdefault("status", "NO_CHANGES")
                value.update({"git": commit, "remote_sync": sync, "durable_return": True, "laws": list(LAWS)})
                return value
            published = self.remote_sync.publish(commit["head"], remote)
            if published.get("shared_frontier_verified"):
                value = dict(plan.get("result") or {})
                value.setdefault("status", "OK")
                value.update({"git": commit, "remote_publish": published, "durable_return": True, "attempt": attempt, "laws": list(LAWS)})
                return value
            if published.get("status") == "PUBLISH_HOLD_DIVERGED_HOLD" and self._safe_race_reset(base, commit["head"], published.get("remote_head")):
                continue
            return {
                **dict(plan.get("result") or {}),
                "status": "LOCAL_MUTATION_PUBLISH_HOLD",
                "git": commit,
                "remote_publish": published,
                "durable_return": False,
                "attempt": attempt,
                "laws": list(LAWS),
            }
        return {"status": "MESSAGE_BOARD_RACE_HOLD", "durable_return": False, "attempts": max_retries, "laws": list(LAWS)}

    @staticmethod
    def _lease_seconds(value: int | None) -> int:
        lease = int(value or 1800)
        if lease < 60 or lease > 86400:
            raise ValueError("lease_seconds must be between 60 and 86400")
        return lease

    def _presence_path(self, agent_id: str) -> str:
        return f"{AGENT_ROOT}/{_require_id(agent_id, 'agent_id')}.json"

    def present(self, *, agent_id: str, task: str, work_key: str | None = None, targets=None, details: str | None = None, mode: str = "PRIMARY", replication_reason: str | None = None, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        task = str(task or "").strip()
        if not task:
            raise ValueError("task is required for present")
        mode = str(mode or "PRIMARY").upper()
        if mode not in {"PRIMARY", "REPLICA"}:
            raise ValueError("present mode must be PRIMARY or REPLICA; use join for COLLABORATOR")
        if mode == "REPLICA" and not str(replication_reason or "").strip():
            raise ValueError("REPLICA requires replication_reason")
        lease = self._lease_seconds(lease_seconds)
        target_list = sorted({_norm_target(str(x)) for x in (targets or []) if _norm_target(str(x))})
        candidate = {"agent_id": agent_id, "task": task, "work_key": str(work_key or "").strip() or None, "targets": target_list, "mode": mode}

        def build(base):
            active = self._active()
            existing = next((r for r in active if r.get("agent_id") == agent_id), None)
            if existing:
                same = _norm(existing.get("task")) == _norm(task) and _norm(existing.get("work_key")) == _norm(candidate.get("work_key")) and self._targets(existing) == self._targets(candidate) and str(existing.get("mode")) == mode
                return {"return": {"status": "ALREADY_PRESENT" if same else "AGENT_ALREADY_PRESENT_HOLD", "presence": existing, "next": "heartbeat" if same else "release current claim before switching work"}}
            conflicts, potential = [], []
            for other in active:
                hard = self._hard_overlap(candidate, other)
                if hard:
                    conflicts.append({"agent": other, "reasons": hard})
                    continue
                score, shared = _jaccard(task, other.get("task"))
                if score >= 0.65 and shared >= 3:
                    potential.append({"agent_id": other.get("agent_id"), "task": other.get("task"), "task_similarity": round(score, 4), "shared_tokens": shared})
            if conflicts and mode != "REPLICA":
                return {"return": {"status": "DUPLICATE_WORK_HOLD", "conflicts": conflicts, "potential_overlaps": potential, "next": "join an existing claim or choose a different residual"}}
            now = _utcnow()
            claim_id = f"MBC-{uuid.uuid4().hex}"
            presence = {
                "artifact": PRESENCE_ARTIFACT,
                "agent_id": agent_id,
                "claim_id": claim_id,
                "status": "ACTIVE",
                "mode": mode,
                "task": task,
                "work_key": candidate["work_key"],
                "targets": target_list,
                "details": str(details or "").strip() or None,
                "replication_reason": str(replication_reason or "").strip() or None,
                "join_of": None,
                "started_at": _iso(now),
                "heartbeat_at": _iso(now),
                "lease_seconds": lease,
                "expires_at": _iso(now + timedelta(seconds=lease)),
                "claim_base_head": base,
                "law": "CLAIM != COMPLETION",
            }
            event_rel, event = self._event("PRESENT", agent_id, {"claim_id": claim_id, "mode": mode, "task": task, "work_key": presence["work_key"], "targets": target_list})
            return {
                "files": {self._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)},
                "message": f"message board present {agent_id}",
                "result": {"status": "PRESENT", "presence": presence, "potential_overlaps": potential, "hard_overlap_override": bool(conflicts and mode == "REPLICA")},
            }

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def join(self, *, agent_id: str, join_agent_id: str, task: str | None = None, details: str | None = None, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        join_agent_id = _require_id(join_agent_id, "join_agent_id")
        if agent_id == join_agent_id:
            raise ValueError("agent cannot join itself")
        lease = self._lease_seconds(lease_seconds)

        def build(base):
            active = self._active()
            existing = next((r for r in active if r.get("agent_id") == agent_id), None)
            if existing:
                return {"return": {"status": "AGENT_ALREADY_PRESENT_HOLD", "presence": existing}}
            leader = next((r for r in active if r.get("agent_id") == join_agent_id), None)
            if not leader:
                return {"return": {"status": "JOIN_TARGET_NOT_ACTIVE_HOLD", "join_agent_id": join_agent_id}}
            now = _utcnow()
            claim_id = f"MBC-{uuid.uuid4().hex}"
            root_claim = leader.get("join_of") or leader.get("claim_id")
            presence = {
                "artifact": PRESENCE_ARTIFACT,
                "agent_id": agent_id,
                "claim_id": claim_id,
                "status": "ACTIVE",
                "mode": "COLLABORATOR",
                "task": str(task or leader.get("task") or "").strip(),
                "work_key": leader.get("work_key"),
                "targets": list(leader.get("targets") or []),
                "details": str(details or "").strip() or None,
                "replication_reason": None,
                "join_of": root_claim,
                "join_agent_id": join_agent_id,
                "started_at": _iso(now),
                "heartbeat_at": _iso(now),
                "lease_seconds": lease,
                "expires_at": _iso(now + timedelta(seconds=lease)),
                "claim_base_head": base,
                "law": "COLLABORATION != INDEPENDENT_REPLICATION",
            }
            event_rel, event = self._event("JOIN", agent_id, {"claim_id": claim_id, "join_of": root_claim, "join_agent_id": join_agent_id}, recipients=[join_agent_id])
            return {"files": {self._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"message board join {agent_id} -> {join_agent_id}", "result": {"status": "JOINED", "presence": presence, "leader": leader}}

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def heartbeat(self, *, agent_id: str, lease_seconds: int | None = None, note: str | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")

        def build(base):
            row = next((r for r in self._presence_rows() if r.get("agent_id") == agent_id), None)
            if not row or self._lease_state(row) != "ACTIVE":
                return {"return": {"status": "NOT_ACTIVE_HOLD", "next": "present again before continuing work"}}
            lease = self._lease_seconds(lease_seconds or row.get("lease_seconds") or 1800)
            now = _utcnow()
            updated = dict(row)
            updated.update({"heartbeat_at": _iso(now), "lease_seconds": lease, "expires_at": _iso(now + timedelta(seconds=lease))})
            event_rel, event = self._event("HEARTBEAT", agent_id, {"claim_id": row.get("claim_id"), "note": str(note or "").strip() or None})
            return {"files": {self._presence_path(agent_id): _json_text(updated), event_rel: _json_text(event)}, "message": f"message board heartbeat {agent_id}", "result": {"status": "HEARTBEAT", "presence": updated}}

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def post(self, *, agent_id: str, message: str, message_kind: str = "INFO", recipients=None, reply_to: str | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        text = str(message or "").strip()
        if not text:
            raise ValueError("message is required for post")
        kind = str(message_kind or "INFO").upper()
        if kind not in _MESSAGE_KINDS:
            raise ValueError(f"message_kind must be one of {sorted(_MESSAGE_KINDS)}")
        recips = [_require_id(str(x), "recipient") for x in (recipients or [])]

        def build(base):
            active = self._active()
            sender = next((r for r in active if r.get("agent_id") == agent_id), None)
            if not sender:
                return {"return": {"status": "NOT_PRESENT_HOLD", "next": "present or join before posting"}}
            missing = sorted(set(recips) - {str(r.get("agent_id")) for r in active})
            event_rel, event = self._event("MESSAGE", agent_id, {"message_kind": kind, "message": text, "claim_id": sender.get("claim_id")}, recipients=recips, reply_to=reply_to)
            return {"files": {event_rel: _json_text(event)}, "message": f"message board post {agent_id}", "result": {"status": "POSTED", "message_event": event, "inactive_recipients": missing, "delivery": "ROUTED_NOT_CONSUMED"}}

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def ack(self, *, agent_id: str, message_id: str, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        message_id = _require_id(message_id, "message_id")

        def build(base):
            events = self._events()
            message = next((e for e in events if e.get("event_id") == message_id and e.get("kind") == "MESSAGE"), None)
            if not message:
                return {"return": {"status": "MESSAGE_NOT_FOUND_HOLD", "message_id": message_id}}
            if not self._message_visible_to(message, agent_id):
                return {"return": {"status": "MESSAGE_NOT_ADDRESSED_HOLD", "message_id": message_id}}
            already = any(e.get("kind") == "ACK" and e.get("agent_id") == agent_id and (e.get("payload") or {}).get("message_id") == message_id for e in events)
            if already:
                return {"return": {"status": "ALREADY_ACKED", "message_id": message_id}}
            event_rel, event = self._event("ACK", agent_id, {"message_id": message_id}, reply_to=message_id)
            return {"files": {event_rel: _json_text(event)}, "message": f"message board ack {agent_id}", "result": {"status": "ACKED", "message_id": message_id, "ack_event": event}}

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def release(self, *, agent_id: str, release_status: str = "DONE", outcome: str | None = None, handoff_to: str | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        release_status = str(release_status or "DONE").upper()
        if release_status not in _RELEASE_STATES:
            raise ValueError(f"release_status must be one of {sorted(_RELEASE_STATES)}")
        if handoff_to is not None:
            handoff_to = _require_id(handoff_to, "handoff_to")

        def build(base):
            row = next((r for r in self._presence_rows() if r.get("agent_id") == agent_id), None)
            if not row or str(row.get("status")) != "ACTIVE":
                return {"return": {"status": "ALREADY_RELEASED" if row else "NOT_PRESENT", "presence": row}}
            updated = dict(row)
            updated.update({"status": "RELEASED", "release_status": release_status, "released_at": _iso(), "outcome": str(outcome or "").strip() or None, "handoff_to": handoff_to})
            kind = "HANDOFF" if handoff_to or release_status == "HANDOFF" else "RELEASE"
            event_rel, event = self._event(kind, agent_id, {"claim_id": row.get("claim_id"), "release_status": release_status, "outcome": updated["outcome"], "handoff_to": handoff_to}, recipients=[handoff_to] if handoff_to else [])
            return {"files": {self._presence_path(agent_id): _json_text(updated), event_rel: _json_text(event)}, "message": f"message board release {agent_id}", "result": {"status": "RELEASED", "presence": updated, "handoff": handoff_to, "law": "RELEASE_PRESERVES_HISTORY"}}

        return self._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def call_tool(self, name: str, a: dict):
        if name != TOOL_NAME:
            raise KeyError(name)
        action = str(a.get("action") or "").lower()
        if action not in _ACTIONS:
            raise ValueError(f"action must be one of {sorted(_ACTIONS)}")
        remote = a.get("remote", "origin")
        if action == "read":
            return self.read(agent_id=a.get("agent_id"), limit=a.get("limit", 50), include_stale=bool(a.get("include_stale", False)), remote=remote, shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"))
        if action == "present":
            return self.present(agent_id=a["agent_id"], task=a["task"], work_key=a.get("work_key"), targets=a.get("targets") or [], details=a.get("details"), mode=a.get("mode", "PRIMARY"), replication_reason=a.get("replication_reason"), lease_seconds=a.get("lease_seconds", 1800), remote=remote)
        if action == "join":
            return self.join(agent_id=a["agent_id"], join_agent_id=a["join_agent_id"], task=a.get("task"), details=a.get("details"), lease_seconds=a.get("lease_seconds", 1800), remote=remote)
        if action == "heartbeat":
            return self.heartbeat(agent_id=a["agent_id"], lease_seconds=a.get("lease_seconds"), note=a.get("note"), remote=remote)
        if action == "post":
            return self.post(agent_id=a["agent_id"], message=a["message"], message_kind=a.get("message_kind", "INFO"), recipients=a.get("recipients") or [], reply_to=a.get("reply_to"), remote=remote)
        if action == "ack":
            return self.ack(agent_id=a["agent_id"], message_id=a["message_id"], remote=remote)
        if action == "release":
            return self.release(agent_id=a["agent_id"], release_status=a.get("release_status", "DONE"), outcome=a.get("outcome"), handoff_to=a.get("handoff_to"), remote=remote)
        raise KeyError(action)


MESSAGE_BOARD_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Shared Git message board for inter-agent presence, work claims, duplicate-work prevention, collaboration, heartbeats, messages/acknowledgements, and release/handoff. Read before expensive shared work; use present to claim a lane, join to collaborate on an existing lane, or REPLICA only for deliberate independent replication. Writes always require a freshly verified shared remote frontier.",
    "inputSchema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": sorted(_ACTIONS)},
            "agent_id": {"type": ["string", "null"]},
            "task": {"type": ["string", "null"]},
            "work_key": {"type": ["string", "null"]},
            "targets": {"type": "array", "items": {"type": "string"}},
            "details": {"type": ["string", "null"]},
            "mode": {"type": "string", "enum": ["PRIMARY", "REPLICA"]},
            "replication_reason": {"type": ["string", "null"]},
            "lease_seconds": {"type": ["integer", "null"], "minimum": 60, "maximum": 86400},
            "join_agent_id": {"type": ["string", "null"]},
            "message": {"type": ["string", "null"]},
            "message_kind": {"type": "string", "enum": sorted(_MESSAGE_KINDS)},
            "recipients": {"type": "array", "items": {"type": "string"}},
            "reply_to": {"type": ["string", "null"]},
            "message_id": {"type": ["string", "null"]},
            "note": {"type": ["string", "null"]},
            "release_status": {"type": "string", "enum": sorted(_RELEASE_STATES)},
            "outcome": {"type": ["string", "null"]},
            "handoff_to": {"type": ["string", "null"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            "include_stale": {"type": "boolean"},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]}
        },
        "additionalProperties": False
    }
}]
MESSAGE_BOARD_TOOL_NAMES = {TOOL_NAME}
