from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .message_board import (
    EVENT_ARTIFACT,
    PRESENCE_ARTIFACT,
    MessageBoardRuntime,
    _iso,
    _json_text,
    _norm,
    _norm_target,
    _parse_time,
    _require_id,
)

TOOL_NAME = "athena_organism_room"
STATE_PATH = "runtime/message_board/v1/organism/state.json"
STATE_ARTIFACT = "ATHENA.ORGANISM.ROOM.STATE.V1"
SESSION_ARTIFACT = "ATHENA.ORGANISM.ROOM.SESSION.V1"
RECEIPT_ARTIFACT = "ATHENA.ORGANISM.ROOM.RECEIPT.V1"

FAMILIES = (
    "BUILD_GIT",
    "INTEGRATE_META",
    "NAVIGATION",
    "TOOL_LIMITS",
    "ALCHEMY",
    "DRIVE_DISTILL",
    "MATH_MINE",
    "MYTH_MINE",
)
BASE_WEIGHTS = {
    "BUILD_GIT": 0.20,
    "INTEGRATE_META": 0.10,
    "NAVIGATION": 0.15,
    "TOOL_LIMITS": 0.10,
    "ALCHEMY": 0.10,
    "DRIVE_DISTILL": 0.15,
    "MATH_MINE": 0.15,
    "MYTH_MINE": 0.05,
}
TIE_ORDER = {name: index for index, name in enumerate(FAMILIES)}
WAVES = (
    {"wave": "IMMEDIATE", "time_percent": 50, "purpose": "enter, hydrate, claim, and produce an observed material delta"},
    {"wave": "MIDDLE", "time_percent": 30, "purpose": "integrate a producer output and consume the next runnable successor"},
    {"wave": "RECURSIVE_META", "time_percent": 20, "purpose": "attack outcomes, update pressures, generate quests, and improve the pipeline"},
)
TERMINAL_REASONS = {"NO_RESIDUAL", "EXTERNAL_WAIT", "AUTHORITY_BOUND"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _secret(name: str) -> bytes:
    value = os.environ.get(name, "").encode("utf-8")
    if len(value) < 32:
        raise RuntimeError(f"{name} must contain at least 32 bytes; room authority fails closed")
    return value


def _token(session_id: str, fence: int) -> str:
    body = f"{session_id}:{fence}".encode("utf-8")
    return hmac.new(_secret("ATHENA_ROOM_SESSION_SECRET"), body, hashlib.sha256).hexdigest()


def _idempotency_key(value: str) -> str:
    value = _require_id(value, "idempotency_key")
    if len(value) < 16:
        raise ValueError("idempotency_key must contain at least 16 characters")
    return value


def _idempotency_slot(actor: str, key: str) -> str:
    body = f"idempotency:{actor}:{key}".encode("utf-8")
    return hmac.new(_secret("ATHENA_ROOM_SESSION_SECRET"), body, hashlib.sha256).hexdigest()


def make_authority_receipt(claims: dict, authority_id: str, key: bytes) -> dict:
    """Host/evaluator helper. Claimants must not possess authority keys."""
    authority_id = _require_id(authority_id, "authority_id")
    body = {"artifact": RECEIPT_ARTIFACT, "authority_id": authority_id, "claims": claims}
    body["mac"] = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    return body


def verify_authority_receipt(receipt: dict, expected: dict, authority_keys: dict[str, bytes]) -> None:
    if receipt.get("artifact") != RECEIPT_ARTIFACT:
        raise ValueError("COMPLETION_RECEIPT_ARTIFACT_HOLD")
    authority_id = str(receipt.get("authority_id") or "")
    key = authority_keys.get(authority_id)
    if not key:
        raise ValueError("COMPLETION_AUTHORITY_NOT_CONFIGURED_HOLD")
    body = {"artifact": RECEIPT_ARTIFACT, "authority_id": authority_id, "claims": receipt.get("claims")}
    actual = str(receipt.get("mac") or "")
    wanted = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(actual, wanted):
        raise ValueError("COMPLETION_RECEIPT_MAC_HOLD")
    claims = receipt.get("claims")
    if not isinstance(claims, dict):
        raise ValueError("COMPLETION_RECEIPT_CLAIMS_HOLD")
    for field, value in expected.items():
        if claims.get(field) != value:
            raise ValueError(f"COMPLETION_RECEIPT_BINDING_HOLD:{field}")


def _largest_remainder(total: int, weights: dict[str, float]) -> dict[str, int]:
    if total <= 0 or not weights:
        return {key: 0 for key in weights}
    scale = sum(max(0.0, value) for value in weights.values())
    raw = {key: total * max(0.0, value) / scale for key, value in weights.items()}
    result = {key: int(value) for key, value in raw.items()}
    remaining = total - sum(result.values())
    order = sorted(weights, key=lambda key: (-(raw[key] - result[key]), TIE_ORDER.get(key, 1000), key))
    for key in order[:remaining]:
        result[key] += 1
    return result


def allocate_population(agent_ids: list[str], pressure: dict[str, float] | None = None) -> dict:
    """Deterministic homeostat; quotas are targets and empty lanes lend capacity."""
    ids = sorted({_require_id(value, "agent_id") for value in agent_ids})
    pressure = pressure or {}
    eligible = {name: max(0.0, float(pressure.get(name, 1.0))) for name in FAMILIES}
    active = {name: BASE_WEIGHTS[name] * eligible[name] for name in FAMILIES if eligible[name] > 0}
    if not active:
        active = {"BUILD_GIT": 1.0}
    counts = _largest_remainder(len(ids), active)
    # Tiny populations stay builder-generalists; wave time still reserves integration/meta.
    if len(ids) <= 3 and "BUILD_GIT" in active:
        counts = {key: 0 for key in active}
        counts["BUILD_GIT"] = len(ids)
    roles: dict[str, str] = {}
    cursor = 0
    for family in FAMILIES:
        for _ in range(counts.get(family, 0)):
            roles[ids[cursor]] = family
            cursor += 1
    wave_weights = {"IMMEDIATE": 0.50, "MIDDLE": 0.30, "RECURSIVE_META": 0.20}
    if len(ids) <= 2:
        wave_counts = {"IMMEDIATE": 1 if ids else 0, "MIDDLE": 1 if len(ids) == 2 else 0, "RECURSIVE_META": 0}
    else:
        wave_counts = {key: 1 for key in wave_weights}
        extras = _largest_remainder(len(ids) - 3, wave_weights)
        wave_counts = {key: wave_counts[key] + extras[key] for key in wave_weights}
    agent_waves, cursor = {}, 0
    for wave in wave_weights:
        for _ in range(wave_counts[wave]):
            agent_waves[ids[cursor]] = wave
            cursor += 1
    return {"population": len(ids), "counts": {name: counts.get(name, 0) for name in FAMILIES}, "roles": roles, "wave_counts": wave_counts, "agent_waves": agent_waves, "waves": list(WAVES)}


def _prompt_digest(root: Path) -> str:
    manifest_path = root / "prompts/PROMPT.manifest.json"
    active_path = root / "prompts/state/ACTIVE.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        active = json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:manifest_or_active") from exc
    paths = {"prompts/PROMPT.manifest.json", "prompts/state/ACTIVE.json"}
    for key in ("bootstrap", "core", "policy"):
        if manifest.get(key):
            paths.add(str(manifest[key]))
    modules = manifest.get("modules") or {}
    for name in active.get("enabled_modules") or []:
        row = modules.get(name)
        if not isinstance(row, dict) or not row.get("path"):
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:enabled_module:{name}")
        paths.add(str(row["path"]))
    for key in ("active_scoped_overlays", "active_scoped_state"):
        paths.update(str(value) for value in active.get(key) or [])
    for value in (
        active.get("harness_genotype"),
        (manifest.get("room") or {}).get("registry"),
        (manifest.get("room") or {}).get("harness_genotype"),
        (manifest.get("room") or {}).get("allocator"),
    ):
        if value:
            paths.add(str(value))
    records = []
    for rel in sorted(paths):
        path = root / rel
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:{rel}") from exc
        records.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest()})
    return _digest(records)


def _empty_state() -> dict:
    return {"artifact": STATE_ARTIFACT, "version": 0, "logical_time": 0, "sessions": {}, "quests": {}, "idempotency": {}}


class OrganismRoomRuntime:
    """Fenced orchestration over the existing Message Board transport.

    Presence remains under MessageBoardRuntime's canonical root. Room state only
    adds sessions, quest attempts, allocation, and verified completion.
    """

    def __init__(self, board: MessageBoardRuntime, *, authority_keys: dict[str, bytes] | None = None):
        self.board = board
        self.authority_keys = authority_keys or self._authority_keys_from_env()

    @staticmethod
    def _authority_keys_from_env() -> dict[str, bytes]:
        raw = os.environ.get("ATHENA_ROOM_AUTHORITY_KEYS", "")
        if not raw:
            return {}
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise RuntimeError("ATHENA_ROOM_AUTHORITY_KEYS must be a JSON object")
        return {str(key): str(secret).encode("utf-8") for key, secret in value.items()}

    def _state(self) -> dict:
        value = self.board._read_json(self.board._root() / STATE_PATH)
        return value if value and value.get("artifact") == STATE_ARTIFACT else _empty_state()

    @staticmethod
    def _live(session: dict, now: datetime) -> bool:
        expires = _parse_time(session.get("lease_until"))
        return session.get("status") in {"ACTIVE", "STALE", "DRAINING"} and expires is not None and now < expires

    @staticmethod
    def _remember(state: dict, actor: str, key: str, command: dict, result: dict) -> None:
        persisted = json.loads(json.dumps(result))
        # Capability tokens are derivable only inside the host from the session
        # secret. Persisting a bearer token in Git would destroy fencing.
        persisted.pop("session_token", None)
        state["idempotency"][_idempotency_slot(actor, key)] = {"command_digest": _digest(command), "result": persisted}

    @staticmethod
    def _replay(state: dict, actor: str, key: str, command: dict) -> dict | None:
        seen = state.get("idempotency", {}).get(_idempotency_slot(actor, key))
        if not seen:
            return None
        if seen.get("command_digest") != _digest(command):
            raise ValueError("IDEMPOTENCY_KEY_REUSE_CONFLICT")
        result = dict(seen["result"])
        if command.get("action") == "enter" and isinstance(result.get("session"), dict):
            session = result["session"]
            result["session_token"] = _token(str(session["session_id"]), int(session["fence"]))
        return result

    def _authenticate(self, state: dict, agent_id: str, session_id: str, fence: int, token: str, now: datetime) -> dict:
        row = state.get("sessions", {}).get(agent_id)
        if not row or row.get("session_id") != session_id or int(row.get("fence", -1)) != int(fence):
            raise ValueError("FENCED_SESSION_HOLD")
        if not hmac.compare_digest(str(token), _token(session_id, int(fence))):
            raise ValueError("SESSION_TOKEN_HOLD")
        if not self._live(row, now):
            raise ValueError("SESSION_LEASE_EXPIRED_HOLD")
        return row

    def read(self, *, agent_id: str | None = None, remote: str = "origin") -> dict:
        board = self.board.read(agent_id=agent_id, include_stale=True, remote=remote)
        state = self._state()
        allocation = allocate_population([row["agent_id"] for row in board.get("active", [])])
        return {"status": board.get("status"), "board": board, "room": state, "allocation": allocation, "waves": list(WAVES)}

    def enter(self, *, agent_id: str, task: str, work_key: str, targets: list[str], ack_head: str, ack_prompt_digest: str, idempotency_key: str, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        idempotency_key = _idempotency_key(idempotency_key)
        task = str(task or "").strip()
        work_key = str(work_key or "").strip()
        if not task or not work_key:
            raise ValueError("task and work_key are required")
        lease = self.board._lease_seconds(lease_seconds)
        current_head = self.board.git.head()
        current_prompt = _prompt_digest(self.board._root())
        command = {"action": "enter", "task": task, "work_key": work_key, "targets": sorted(targets), "ack_head": ack_head, "ack_prompt_digest": ack_prompt_digest, "lease_seconds": lease}

        def build(base: str) -> dict:
            state = self._state()
            replay = self._replay(state, agent_id, idempotency_key, command)
            if replay is not None:
                return {"return": replay}
            if base != ack_head or _prompt_digest(self.board._root()) != ack_prompt_digest:
                return {"return": {"status": "REHYDRATE_HOLD", "current_head": base, "current_prompt_digest": _prompt_digest(self.board._root())}}
            now = _utcnow()
            prior = state["sessions"].get(agent_id)
            if prior and self._live(prior, now):
                return {"return": {"status": "AGENT_ALREADY_PRESENT_HOLD", "session": prior}}
            candidate = {"agent_id": agent_id, "task": task, "work_key": work_key, "targets": [_norm_target(v) for v in targets], "mode": "PRIMARY"}
            conflicts = []
            for other in self.board._active():
                hard = self.board._hard_overlap(candidate, other)
                if hard:
                    conflicts.append({"agent_id": other.get("agent_id"), "reasons": hard})
            if conflicts:
                return {"return": {"status": "DUPLICATE_WORK_HOLD", "conflicts": conflicts}}
            fence = int((prior or {}).get("fence", 0)) + 1
            session_id = f"ROOM-{uuid.uuid4().hex}"
            claim_id = f"RCL-{uuid.uuid4().hex}"
            attempt = max([int(q.get("attempt", 0)) for q in state["quests"].values() if q.get("work_key") == work_key] or [0]) + 1
            active_ids = [row["agent_id"] for row in self.board._active()] + [agent_id]
            allocation = allocate_population(active_ids)
            session = {"artifact": SESSION_ARTIFACT, "agent_id": agent_id, "session_id": session_id, "fence": fence, "status": "ACTIVE", "head": base, "prompt_digest": current_prompt, "claim_id": claim_id, "quest_id": work_key, "attempt": attempt, "role": allocation["roles"][agent_id], "wave": allocation["agent_waves"][agent_id], "entered_at": _iso(now), "lease_until": _iso(now + timedelta(seconds=lease))}
            quest = {"quest_id": work_key, "work_key": work_key, "attempt": attempt, "status": "ACTIVE", "claim_id": claim_id, "session_id": session_id, "fence": fence, "task": task, "targets": candidate["targets"], "input_head": base, "prompt_digest": current_prompt}
            presence = {"artifact": PRESENCE_ARTIFACT, "agent_id": agent_id, "claim_id": claim_id, "session_id": session_id, "fence": fence, "status": "ACTIVE", "mode": "PRIMARY", "task": task, "work_key": work_key, "targets": candidate["targets"], "details": f"organism-room role={session['role']}", "join_of": None, "started_at": session["entered_at"], "heartbeat_at": session["entered_at"], "lease_seconds": lease, "expires_at": session["lease_until"], "claim_base_head": base, "law": "FENCED_CLAIM_NOT_COMPLETION"}
            state["version"] += 1
            state["logical_time"] += 1
            state["sessions"][agent_id] = session
            state["quests"][work_key] = quest
            result = {"status": "ENTERED", "session": session, "session_token": _token(session_id, fence), "allocation": allocation, "waves": list(WAVES), "next": "execute the material delta; heartbeat before lease expiry"}
            self._remember(state, agent_id, idempotency_key, command, result)
            event_rel, event = self.board._event("ROOM_ENTER", agent_id, {"session_id": session_id, "fence": fence, "claim_id": claim_id, "quest_id": work_key, "role": session["role"]})
            return {"files": {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"organism room enter {agent_id}", "result": result}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def heartbeat(self, *, agent_id: str, session_id: str, fence: int, session_token: str, idempotency_key: str, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        key = _idempotency_key(idempotency_key)
        lease = self.board._lease_seconds(lease_seconds)
        command = {"action": "heartbeat", "session_id": session_id, "fence": fence, "lease_seconds": lease}

        def build(base: str) -> dict:
            state = self._state()
            replay = self._replay(state, agent_id, key, command)
            if replay is not None:
                return {"return": replay}
            now = _utcnow()
            session = self._authenticate(state, agent_id, session_id, fence, session_token, now)
            # Message-board traffic intentionally advances Git HEAD. Prompt
            # freshness is therefore content-addressed; the accepted input HEAD
            # remains bound into the completion receipt.
            if session.get("prompt_digest") != _prompt_digest(self.board._root()):
                session["status"] = "STALE"
                result = {"status": "REHYDRATE_HOLD", "session": session}
            else:
                session["lease_until"] = _iso(now + timedelta(seconds=lease))
                result = {"status": "HEARTBEAT", "session": session}
            state["version"] += 1
            state["logical_time"] += 1
            self._remember(state, agent_id, key, command, result)
            presence = self.board._read_json(self.board._root() / self.board._presence_path(agent_id)) or {}
            presence.update({"heartbeat_at": _iso(now), "expires_at": session["lease_until"]})
            event_rel, event = self.board._event("ROOM_HEARTBEAT", agent_id, {"session_id": session_id, "fence": fence, "status": result["status"]})
            return {"files": {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"organism room heartbeat {agent_id}", "result": result}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    @contextmanager
    def epoch(self, **enter_args):
        """Python lifecycle guard: a body exit cannot leave a live presence."""
        entered = self.enter(**enter_args)
        if entered.get("status") != "ENTERED":
            raise RuntimeError(f"ROOM_ENTER_HOLD:{entered.get('status')}")
        try:
            yield entered
        finally:
            session = entered["session"]
            self.sign_out(
                agent_id=session["agent_id"],
                session_id=session["session_id"],
                fence=session["fence"],
                session_token=entered["session_token"],
                idempotency_key=f"finally-{session['session_id']}",
                force=True,
                remote=enter_args.get("remote", "origin"),
            )

    def complete(self, *, agent_id: str, session_id: str, fence: int, session_token: str, artifact_digests: list[str], result: str, receipt: dict, idempotency_key: str, residual: str | None = None, terminal_reason: str | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        key = _idempotency_key(idempotency_key)
        artifacts = sorted({str(value) for value in artifact_digests if str(value)})
        if not artifacts:
            raise ValueError("COMPLETION_ARTIFACT_DIGEST_HOLD")
        command = {"action": "complete", "session_id": session_id, "fence": fence, "artifacts": artifacts, "result": result, "receipt": receipt, "residual": residual, "terminal_reason": terminal_reason}

        def build(base: str) -> dict:
            state = self._state()
            replay = self._replay(state, agent_id, key, command)
            if replay is not None:
                return {"return": replay}
            now = _utcnow()
            session = self._authenticate(state, agent_id, session_id, fence, session_token, now)
            quest = state["quests"].get(session["quest_id"])
            if not quest or quest.get("session_id") != session_id or quest.get("fence") != fence or quest.get("status") != "ACTIVE":
                raise ValueError("CLAIM_ATTEMPT_HOLD")
            expected = {"quest_id": quest["quest_id"], "attempt": quest["attempt"], "session_id": session_id, "fence": fence, "input_head": quest["input_head"], "prompt_digest": quest["prompt_digest"], "artifact_digests": artifacts, "result": result}
            verify_authority_receipt(receipt, expected, self.authority_keys)
            successor = None
            if residual:
                successor_id = f"{quest['quest_id']}:successor:{quest['attempt']}"
                successor = {"quest_id": successor_id, "work_key": successor_id, "attempt": 0, "status": "READY", "task": residual, "parent_quest_id": quest["quest_id"], "parent_attempt": quest["attempt"], "parent_output_digest": _digest(artifacts)}
                state["quests"][successor_id] = successor
            elif terminal_reason not in TERMINAL_REASONS:
                raise ValueError("SUCCESSOR_OR_VERIFIED_TERMINAL_REASON_REQUIRED")
            quest.update({"status": "VERIFIED", "artifact_digests": artifacts, "result": result, "receipt_authority": receipt["authority_id"], "completed_at": _iso(now), "successor_id": (successor or {}).get("quest_id"), "terminal_reason": terminal_reason})
            session["claim_status"] = "VERIFIED"
            state["version"] += 1
            state["logical_time"] += 1
            outcome = {"status": "VERIFIED_COMPLETION", "quest": quest, "successor": successor, "campaign_terminal": bool(not successor and terminal_reason in TERMINAL_REASONS)}
            self._remember(state, agent_id, key, command, outcome)
            event_rel, event = self.board._event("ROOM_COMPLETE", agent_id, {"session_id": session_id, "fence": fence, "quest_id": quest["quest_id"], "attempt": quest["attempt"], "successor_id": (successor or {}).get("quest_id"), "authority_id": receipt["authority_id"]})
            return {"files": {STATE_PATH: _json_text(state), event_rel: _json_text(event)}, "message": f"organism room complete {agent_id}", "result": outcome}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def sign_out(self, *, agent_id: str, session_id: str, fence: int, session_token: str, idempotency_key: str, force: bool = False, handoff_to: str | None = None, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        key = _idempotency_key(idempotency_key)
        command = {"action": "sign_out", "session_id": session_id, "fence": fence, "force": force, "handoff_to": handoff_to}

        def build(base: str) -> dict:
            state = self._state()
            replay = self._replay(state, agent_id, key, command)
            if replay is not None:
                return {"return": replay}
            now = _utcnow()
            session = self._authenticate(state, agent_id, session_id, fence, session_token, now)
            quest = state["quests"].get(session["quest_id"])
            if quest and quest.get("status") == "ACTIVE" and not force:
                return {"return": {"status": "OPEN_CLAIM_HOLD", "next": "complete, hand off, or force sign-out"}}
            if quest and quest.get("status") == "ACTIVE":
                quest.update({"status": "READY", "session_id": None, "fence": None, "claim_id": None, "abandoned_by": session_id})
            session.update({"status": "RELEASED", "released_at": _iso(now), "handoff_to": handoff_to})
            presence = self.board._read_json(self.board._root() / self.board._presence_path(agent_id)) or {}
            presence.update({"status": "RELEASED", "release_status": "HANDOFF" if handoff_to else ("ABANDONED" if force else "DONE"), "released_at": session["released_at"], "handoff_to": handoff_to})
            state["version"] += 1
            state["logical_time"] += 1
            result = {"status": "SIGNED_OUT", "session": session, "requeued": bool(quest and quest.get("status") == "READY")}
            self._remember(state, agent_id, key, command, result)
            event_rel, event = self.board._event("ROOM_SIGN_OUT", agent_id, {"session_id": session_id, "fence": fence, "force": force, "handoff_to": handoff_to})
            return {"files": {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"organism room sign out {agent_id}", "result": result}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def call_tool(self, name: str, args: dict) -> dict:
        if name != TOOL_NAME:
            raise KeyError(name)
        action = str(args.get("action") or "").lower()
        kwargs = {key: value for key, value in args.items() if key != "action" and value is not None}
        if action == "read":
            return self.read(**kwargs)
        if action == "enter":
            return self.enter(**kwargs)
        if action == "heartbeat":
            return self.heartbeat(**kwargs)
        if action == "complete":
            return self.complete(**kwargs)
        if action == "sign_out":
            return self.sign_out(**kwargs)
        raise ValueError("action must be read, enter, heartbeat, complete, or sign_out")


ORGANISM_ROOM_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Mandatory fenced room lifecycle over ATHENA's existing Git-backed Message Board: read/ack current prompt and HEAD, sign in and claim exact work, heartbeat, externally verify a material completion, consume or create a successor, and sign out.",
    "inputSchema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["read", "enter", "heartbeat", "complete", "sign_out"]},
            "agent_id": {"type": ["string", "null"]}, "task": {"type": ["string", "null"]}, "work_key": {"type": ["string", "null"]},
            "targets": {"type": "array", "items": {"type": "string"}}, "ack_head": {"type": ["string", "null"]}, "ack_prompt_digest": {"type": ["string", "null"]},
            "session_id": {"type": ["string", "null"]}, "fence": {"type": ["integer", "null"]}, "session_token": {"type": ["string", "null"]},
            "idempotency_key": {"type": ["string", "null"], "minLength": 16, "maxLength": 128}, "lease_seconds": {"type": ["integer", "null"], "minimum": 60, "maximum": 86400},
            "artifact_digests": {"type": "array", "items": {"type": "string"}}, "result": {"type": ["string", "null"]}, "receipt": {"type": ["object", "null"]},
            "residual": {"type": ["string", "null"]}, "terminal_reason": {"type": ["string", "null"], "enum": ["NO_RESIDUAL", "EXTERNAL_WAIT", "AUTHORITY_BOUND", None]},
            "force": {"type": "boolean"}, "handoff_to": {"type": ["string", "null"]}, "remote": {"type": "string"}
        },
        "additionalProperties": False
    }
}]
ORGANISM_ROOM_TOOL_NAMES = {TOOL_NAME}
