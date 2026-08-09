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
RESOURCE_DIMENSIONS = ("tool_calls", "api_calls", "tokens", "wall_seconds", "storage_writes", "external_mutations")

FAMILIES = (
    "GIT",
    "MATH",
    "MYTH",
    "NAV",
    "TOOLS",
    "CORPUS",
    "ALCHEMY",
    "META",
    "INTEGRATION",
)
BASE_WEIGHTS = {
    "GIT": 0.20,
    "MATH": 0.15,
    "MYTH": 0.05,
    "NAV": 0.15,
    "TOOLS": 0.10,
    "CORPUS": 0.15,
    "ALCHEMY": 0.10,
    "META": 0.10,
    "INTEGRATION": 0.10,
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


def _resource_contract(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label}_UNKNOWN_HOLD")
    allowed = set(RESOURCE_DIMENSIONS) | {"shared_sinks"}
    extra = sorted(set(value) - allowed)
    if extra:
        raise ValueError(f"{label}_UNSUPPORTED_DIMENSION_HOLD:{','.join(extra)}")
    normalized = {}
    for name in RESOURCE_DIMENSIONS:
        raw = value.get(name)
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            raise ValueError(f"{label}_{name}_UNKNOWN_HOLD")
        normalized[name] = raw
    sinks = value.get("shared_sinks")
    if not isinstance(sinks, list) or any(not isinstance(item, str) or not item.strip() for item in sinks):
        raise ValueError(f"{label}_shared_sinks_UNKNOWN_HOLD")
    normalized["shared_sinks"] = sorted(set(item.strip() for item in sinks))
    return normalized


def validate_resource_admission(resource_upper_bound: Any, room_budget: Any, protected_reserve: Any, live_quests: list[dict]) -> dict:
    request = _resource_contract(resource_upper_bound, "RESOURCE")
    budget = _resource_contract(room_budget, "ROOM_BUDGET")
    reserve = _resource_contract(protected_reserve, "PROTECTED_RESERVE")
    budget_digest, reserve_digest = _digest(budget), _digest(reserve)
    reservations = []
    for quest in live_quests:
        if quest.get("status") != "ACTIVE":
            continue
        if quest.get("room_budget_digest") != budget_digest or quest.get("protected_reserve_digest") != reserve_digest:
            raise ValueError("RESOURCE_POLICY_DRIFT_HOLD")
        reservations.append(_resource_contract(quest.get("resource_upper_bound"), "ACTIVE_RESOURCE"))
    for name in RESOURCE_DIMENSIONS:
        if sum(item[name] for item in reservations) + request[name] + reserve[name] > budget[name]:
            raise ValueError(f"RESOURCE_CAPACITY_HOLD:{name}")
    occupied = {sink for item in reservations for sink in item["shared_sinks"]}
    collision = sorted(occupied & set(request["shared_sinks"]))
    if collision:
        raise ValueError("SHARED_SINK_HOLD:" + ",".join(collision))
    return {
        "resource_upper_bound": request,
        "room_budget_digest": budget_digest,
        "protected_reserve_digest": reserve_digest,
        "resource_standing": "HOST_BOUND_UPPER_BOUND_RESERVED",
    }


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
    if not str(claims.get("evaluator_version") or "").strip():
        raise ValueError("COMPLETION_EVALUATOR_VERSION_HOLD")
    if _parse_time(str(claims.get("observed_at") or "")) is None:
        raise ValueError("COMPLETION_OBSERVED_AT_HOLD")
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


def _largest_remainder_with_minimums(total: int, weights: dict[str, float], minimums: dict[str, int]) -> dict[str, int]:
    result = {key: int(minimums.get(key, 0)) for key in weights}
    used = sum(result.values())
    if used > total:
        raise ValueError("minimums exceed population")
    extras = _largest_remainder(total - used, weights)
    return {key: result[key] + extras[key] for key in weights}


def allocate_population(agent_ids: list[str], pressure: dict[str, float] | None = None) -> dict:
    """Deterministic homeostat; quotas are targets and empty lanes lend capacity."""
    ids = sorted({_require_id(value, "agent_id") for value in agent_ids})
    pressure = pressure or {}
    eligible = {name: max(0.0, float(pressure.get(name, 0.0 if name == "INTEGRATION" else 1.0))) for name in FAMILIES}
    active = {name: BASE_WEIGHTS[name] * eligible[name] for name in FAMILIES if eligible[name] > 0}
    if not active:
        active = {"GIT": 1.0}
    counts = _largest_remainder(len(ids), active)
    # Tiny populations stay builder-generalists; wave time still reserves integration/meta.
    if len(ids) <= 3:
        counts = {key: 0 for key in active}
        counts["GIT"] = len(ids)
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
        wave_counts = _largest_remainder_with_minimums(len(ids), wave_weights, {key: 1 for key in wave_weights})
    agent_waves, cursor = {}, 0
    for wave in wave_weights:
        for _ in range(wave_counts[wave]):
            agent_waves[ids[cursor]] = wave
            cursor += 1
    return {"population": len(ids), "counts": {name: counts.get(name, 0) for name in FAMILIES}, "roles": roles, "wave_counts": wave_counts, "agent_waves": agent_waves, "waves": list(WAVES)}


def _prompt_digest(root: Path) -> str:
    manifest_path = root / "prompts/PROMPT.manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        active_rel = str(manifest.get("active_state") or "prompts/state/ACTIVE.json")
        active_path = root / active_rel
        active = json.loads(active_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:manifest_or_active") from exc
    manifest_artifact = manifest.get("artifact")
    if manifest_artifact not in {"ATHENA.PROMPT.RUNTIME.V1", "ATHENA.PROMPT.RUNTIME.V2"}:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:unsupported_manifest")
    if active.get("status") != "ACTIVE" or active.get("prompt_runtime") not in {None, manifest_artifact}:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:inactive_state")
    room = manifest.get("room") or {}
    if room.get("repo") != "demeet2k/Athena" or room.get("issue") != 555:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:canonical_room_coordinate")
    paths = {"prompts/PROMPT.manifest.json", active_rel}
    for key in ("bootstrap", "core", "policy"):
        if manifest.get(key):
            paths.add(str(manifest[key]))
    modules = manifest.get("modules") or {}
    profile = active.get("profile") or manifest.get("default_profile")
    profiles = manifest.get("profiles") or {}
    if profile not in profiles:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:profile")
    enabled = set(active.get("enabled_modules") or [])
    required = set(profiles[profile]) | {name for name, row in modules.items() if isinstance(row, dict) and row.get("mandatory")}
    if not required.issubset(enabled):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:required_module_disabled")
    for name in active.get("enabled_modules") or []:
        row = modules.get(name)
        if not isinstance(row, dict) or not row.get("path"):
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:enabled_module:{name}")
        paths.add(str(row["path"]))
    overlays = active.get("active_scoped_overlays") or []
    state_paths = active.get("active_scoped_state") or []
    if not isinstance(overlays, list) or not isinstance(state_paths, list):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:overlay_arrays")
    if any(not isinstance(value, str) for value in overlays + state_paths):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:overlay_path_type")
    state_by_overlay: dict[str, list[str]] = {}
    for state_rel in state_paths:
        try:
            state = json.loads((root / state_rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:{state_rel}") from exc
        overlay_rel = state.get("overlay")
        if not isinstance(overlay_rel, str):
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:overlay_state_binding:{state_rel}")
        state_by_overlay.setdefault(overlay_rel, []).append(state_rel)
        if state.get("status") != "ACTIVE_SCOPED":
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:overlay_state_status:{state_rel}")
    if manifest_artifact == "ATHENA.PROMPT.RUNTIME.V2" or active.get("artifact") == "ATHENA.PROMPT.STATE.ACTIVE.V2":
        for overlay_rel in overlays:
            if len(state_by_overlay.get(overlay_rel, [])) != 1:
                raise RuntimeError(f"PROMPT_HYDRATION_HOLD:overlay_state_cardinality:{overlay_rel}")
        unbound = sorted(set(state_by_overlay) - set(overlays))
        if unbound:
            raise RuntimeError(f"PROMPT_HYDRATION_HOLD:orphan_overlay_state:{unbound[0]}")
    paths.update(overlays)
    paths.update(state_paths)
    for value in (
        active.get("harness_genotype"),
        *(value for key, value in room.items() if key not in {"repo"} and isinstance(value, str)),
    ):
        if value:
            paths.add(str(value))
    registry_rel = room.get("registry")
    try:
        registry = json.loads((root / registry_rel).read_text(encoding="utf-8"))
    except (TypeError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry") from exc
    expected_jobs = {"GIT", "MATH", "MYTH", "NAV", "TOOLS", "CORPUS", "ALCHEMY", "META", "INTEGRATION"}
    if registry.get("artifact") != "ATHENA.ORGANISM.ROOM.V1" or registry.get("status") != "ACTIVE":
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry_identity")
    expected_domains = {"GIT": 0.2, "MATH": 0.15, "NAV": 0.15, "CORPUS": 0.15, "TOOLS": 0.1, "ALCHEMY": 0.1, "MYTH": 0.05, "META": 0.1}
    expected_events = {"SIGNIN", "WORK", "HEARTBEAT", "DELTA", "NEED", "OFFER", "QUEST_CREATE", "QUEST_RETIRE", "PLAN", "HARNESS_MUTATION", "HARNESS_REVERT", "SIGNOUT"}
    transport = registry.get("transport") or {}
    events = set(registry.get("events") or expected_events)
    if registry.get("waves") != {"W0": 0.5, "W1": 0.3, "W2": 0.2} or set(registry.get("job_families") or []) != expected_jobs:
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry_contract")
    if registry.get("domains") not in (None, expected_domains):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry_domains")
    if transport and (transport.get("repo") != "demeet2k/Athena" or transport.get("issue") != 555):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry_transport")
    if not expected_events.issubset(events):
        raise RuntimeError("PROMPT_HYDRATION_HOLD:room_registry_events")
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


def _observational_metrics(state: dict) -> dict:
    quests = list((state.get("quests") or {}).values())
    successors = [quest for quest in quests if quest.get("parent_quest_id")]
    consumed = [quest for quest in successors if quest.get("status") != "READY"]
    statuses: dict[str, int] = {}
    for quest in quests:
        status = str(quest.get("status") or "UNKNOWN")
        statuses[status] = statuses.get(status, 0) + 1
    sessions = list((state.get("sessions") or {}).values())
    return {
        "standing": "OBSERVATIONAL_PROJECTION_NOT_CAUSAL_EFFECT",
        "quest_status_counts": statuses,
        "verified_artifact_sets": sum(1 for quest in quests if quest.get("status") == "VERIFIED" and quest.get("artifact_digests")),
        "successors_created": len(successors),
        "successors_consumed": len(consumed),
        "successor_consumption_rate": (len(consumed) / len(successors)) if successors else None,
        "session_count": len(sessions),
        "active_session_count": sum(1 for session in sessions if session.get("status") in {"ACTIVE", "STALE", "DRAINING"}),
        "human_interventions": "NOT_OBSERVED_BY_THIS_RUNTIME",
        "control_plane_to_work_ratio": "REQUIRES_HOST_TIMING_OBSERVER",
    }


class OrganismRoomRuntime:
    """Fenced orchestration over the existing Message Board transport.

    Presence remains under MessageBoardRuntime's canonical root. Room state only
    adds sessions, quest attempts, allocation, and verified completion.
    """

    def __init__(self, board: MessageBoardRuntime, *, authority_keys: dict[str, bytes] | None = None, room_budget: dict | None = None, protected_reserve: dict | None = None):
        self.board = board
        self.authority_keys = authority_keys or self._authority_keys_from_env()
        self.room_budget = _resource_contract(room_budget, "ROOM_BUDGET") if room_budget is not None else None
        self.protected_reserve = _resource_contract(protected_reserve, "PROTECTED_RESERVE") if protected_reserve is not None else None

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
        path = self.board._root() / STATE_PATH
        if not path.exists():
            return _empty_state()
        value = self.board._read_json(path)
        if not value or value.get("artifact") != STATE_ARTIFACT:
            raise RuntimeError("ROOM_STATE_CORRUPTION_HOLD")
        if not isinstance(value.get("version"), int) or value["version"] < 0 or not isinstance(value.get("logical_time"), int) or value["logical_time"] < 0:
            raise RuntimeError("ROOM_STATE_CORRUPTION_HOLD")
        for key in ("sessions", "quests", "idempotency"):
            if not isinstance(value.get(key), dict):
                raise RuntimeError("ROOM_STATE_CORRUPTION_HOLD")
        return value

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
        # Replays never mint or reconstruct bearer credentials. The original
        # caller must retain its host-returned token.
        result.pop("session_token", None)
        return result

    @staticmethod
    def _reap_expired(state: dict, now: datetime) -> None:
        for session in state.get("sessions", {}).values():
            expires = _parse_time(session.get("lease_until"))
            if session.get("status") not in {"ACTIVE", "STALE", "DRAINING"} or expires is None or now < expires:
                continue
            session["status"] = "EXPIRED"
            quest = state.get("quests", {}).get(session.get("quest_id"))
            if quest and quest.get("status") == "ACTIVE" and quest.get("session_id") == session.get("session_id"):
                quest.update({"status": "READY", "session_id": None, "fence": None, "claim_id": None, "reclaimed_after_expiry": True})

    def _authenticate(self, state: dict, agent_id: str, session_id: str, fence: int, token: str, now: datetime, *, require_presence: bool = True) -> dict:
        row = state.get("sessions", {}).get(agent_id)
        if not row or row.get("session_id") != session_id or int(row.get("fence", -1)) != int(fence):
            raise ValueError("FENCED_SESSION_HOLD")
        if not hmac.compare_digest(str(token), _token(session_id, int(fence))):
            raise ValueError("SESSION_TOKEN_HOLD")
        if not self._live(row, now):
            raise ValueError("SESSION_LEASE_EXPIRED_HOLD")
        if require_presence:
            presence = next((item for item in self.board._active() if item.get("agent_id") == agent_id), None)
            if not presence or any(presence.get(key) != row.get(key) for key in ("session_id", "fence", "claim_id")):
                raise ValueError("ROOM_PRESENCE_LINEAGE_HOLD")
        return row

    def read(self, *, agent_id: str | None = None, remote: str = "origin") -> dict:
        board = self.board.read(agent_id=agent_id, include_stale=True, remote=remote)
        state = self._state()
        allocation = allocate_population([row["agent_id"] for row in board.get("active", [])])
        return {"status": board.get("status"), "board": board, "room": state, "allocation": allocation, "waves": list(WAVES), "metrics": _observational_metrics(state)}

    def sign_in(self, *, agent_id: str, ack_head: str, ack_prompt_digest: str, idempotency_key: str, capabilities: list[str] | None = None, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        key = _idempotency_key(idempotency_key)
        lease = self.board._lease_seconds(lease_seconds)
        capabilities = sorted({str(value).strip() for value in (capabilities or []) if str(value).strip()})
        command = {"action": "sign_in", "ack_head": ack_head, "ack_prompt_digest": ack_prompt_digest, "capabilities": capabilities, "lease_seconds": lease}

        def build(base: str) -> dict:
            state = self._state()
            replay = self._replay(state, agent_id, key, command)
            if replay is not None:
                return {"return": replay}
            current_prompt = _prompt_digest(self.board._root())
            if base != ack_head or current_prompt != ack_prompt_digest:
                return {"return": {"status": "REHYDRATE_HOLD", "current_head": base, "current_prompt_digest": current_prompt}}
            now = _utcnow()
            prior = state["sessions"].get(agent_id)
            if prior and self._live(prior, now):
                return {"return": {"status": "AGENT_ALREADY_PRESENT_HOLD", "session": prior}}
            if prior and prior.get("quest_id"):
                orphan = state["quests"].get(prior["quest_id"])
                if orphan and orphan.get("status") == "ACTIVE" and orphan.get("session_id") == prior.get("session_id"):
                    orphan.update({"status": "READY", "session_id": None, "fence": None, "claim_id": None, "reclaimed_after_expiry": True})
            fence = int((prior or {}).get("fence", 0)) + 1
            session_id = f"ROOM-{uuid.uuid4().hex}"
            active_ids = [row["agent_id"] for row in self.board._active()] + [agent_id]
            allocation = allocate_population(active_ids)
            session = {"artifact": SESSION_ARTIFACT, "agent_id": agent_id, "session_id": session_id, "fence": fence, "status": "ACTIVE", "head": base, "prompt_digest": current_prompt, "claim_id": None, "quest_id": None, "attempt": 0, "role": allocation["roles"][agent_id], "wave": allocation["agent_waves"][agent_id], "capabilities": capabilities, "entered_at": _iso(now), "lease_until": _iso(now + timedelta(seconds=lease)), "source_identity_ceiling": "LOCAL_CHECKOUT_COORDINATES_VALIDATED_PROVIDER_MEMBERSHIP_NOT_PROVEN"}
            presence = {"artifact": PRESENCE_ARTIFACT, "agent_id": agent_id, "claim_id": None, "session_id": session_id, "fence": fence, "status": "ACTIVE", "mode": "OBSERVER", "task": "ROOM_OCCUPANCY", "work_key": None, "targets": [], "details": f"organism-room signed-in role={session['role']}", "join_of": None, "started_at": session["entered_at"], "heartbeat_at": session["entered_at"], "lease_seconds": lease, "expires_at": session["lease_until"], "claim_base_head": base, "law": "SIGNIN != WORK != COMPLETION"}
            state["version"] += 1
            state["logical_time"] += 1
            state["sessions"][agent_id] = session
            result = {"status": "SIGNED_IN", "session": session, "session_token": _token(session_id, fence), "allocation": allocation, "waves": list(WAVES), "next": "claim exact WORK before consequential shared mutation"}
            self._remember(state, agent_id, key, command, result)
            event_rel, event = self.board._event("SIGNIN", agent_id, {"session_id": session_id, "fence": fence, "capabilities": capabilities, "role": session["role"], "wave": session["wave"]})
            return {"files": {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"organism room sign in {agent_id}", "result": result}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def enter(self, *, agent_id: str, task: str, work_key: str, targets: list[str], ack_head: str, ack_prompt_digest: str, idempotency_key: str, resource_upper_bound: dict, room_budget: dict | None = None, protected_reserve: dict | None = None, session_id: str | None = None, fence: int | None = None, session_token: str | None = None, lease_seconds: int = 1800, remote: str = "origin") -> dict:
        agent_id = _require_id(agent_id, "agent_id")
        idempotency_key = _idempotency_key(idempotency_key)
        task = str(task or "").strip()
        work_key = str(work_key or "").strip()
        if not task or not work_key:
            raise ValueError("task and work_key are required")
        if len(work_key) > 256:
            raise ValueError("work_key must contain at most 256 characters")
        lease = self.board._lease_seconds(lease_seconds)
        command = {"action": "enter", "task": task, "work_key": work_key, "targets": sorted(targets), "ack_head": ack_head, "ack_prompt_digest": ack_prompt_digest, "resource_upper_bound": resource_upper_bound, "session_id": session_id, "fence": fence, "lease_seconds": lease}

        def build(base: str) -> dict:
            state = self._state()
            now = _utcnow()
            prior = state["sessions"].get(agent_id)
            signed_in_upgrade = bool(prior and self._live(prior, now) and not prior.get("quest_id"))
            if session_id is not None:
                if fence is None or not session_token:
                    return {"return": {"status": "SIGNED_IN_SESSION_AUTH_REQUIRED_HOLD", "session": prior}}
                self._authenticate(state, agent_id, session_id, int(fence), session_token, now)
            replay = self._replay(state, agent_id, idempotency_key, command)
            if replay is not None:
                return {"return": replay}
            prompt_at_base = _prompt_digest(self.board._root())
            if base != ack_head or prompt_at_base != ack_prompt_digest:
                return {"return": {"status": "REHYDRATE_HOLD", "current_head": base, "current_prompt_digest": prompt_at_base}}
            self._reap_expired(state, now)
            prior = state["sessions"].get(agent_id)
            signed_in_upgrade = bool(prior and self._live(prior, now) and not prior.get("quest_id"))
            if prior and self._live(prior, now) and not signed_in_upgrade:
                return {"return": {"status": "AGENT_ALREADY_PRESENT_HOLD", "session": prior}}
            if signed_in_upgrade:
                self._authenticate(state, agent_id, session_id, int(fence), session_token, now)
            if prior and prior.get("quest_id"):
                orphan = state["quests"].get(prior["quest_id"])
                if orphan and orphan.get("status") == "ACTIVE" and orphan.get("session_id") == prior.get("session_id"):
                    orphan.update({"status": "READY", "session_id": None, "fence": None, "claim_id": None, "reclaimed_after_expiry": True})
            candidate = {"agent_id": agent_id, "task": task, "work_key": work_key, "targets": [_norm_target(v) for v in targets], "mode": "PRIMARY"}
            conflicts = []
            for other in self.board._active():
                hard = self.board._hard_overlap(candidate, other)
                if hard:
                    conflicts.append({"agent_id": other.get("agent_id"), "reasons": hard})
            if conflicts:
                return {"return": {"status": "DUPLICATE_WORK_HOLD", "conflicts": conflicts}}
            next_fence = int(prior["fence"]) if signed_in_upgrade else int((prior or {}).get("fence", 0)) + 1
            next_session_id = str(prior["session_id"]) if signed_in_upgrade else f"ROOM-{uuid.uuid4().hex}"
            claim_id = f"RCL-{uuid.uuid4().hex}"
            prior_quest = state["quests"].get(work_key)
            if prior_quest and prior_quest.get("status") not in {"READY"}:
                return {"return": {"status": "QUEST_NOT_READY_HOLD", "quest": prior_quest}}
            attempt = int((prior_quest or {}).get("attempt", 0)) + 1
            try:
                if self.room_budget is None or self.protected_reserve is None:
                    raise ValueError("HOST_RESOURCE_POLICY_UNCONFIGURED_HOLD")
                resource = validate_resource_admission(resource_upper_bound, self.room_budget, self.protected_reserve, list(state["quests"].values()))
            except ValueError as exc:
                return {"return": {"status": "RESOURCE_ADMISSION_HOLD", "detail": str(exc)}}
            active_ids = [row["agent_id"] for row in self.board._active()] + [agent_id]
            allocation = allocate_population(active_ids)
            session = {"artifact": SESSION_ARTIFACT, "agent_id": agent_id, "session_id": next_session_id, "fence": next_fence, "status": "ACTIVE", "head": base, "prompt_digest": prompt_at_base, "claim_id": claim_id, "quest_id": work_key, "attempt": attempt, "role": allocation["roles"][agent_id], "wave": allocation["agent_waves"][agent_id], "entered_at": prior.get("entered_at") if signed_in_upgrade else _iso(now), "lease_until": _iso(now + timedelta(seconds=lease)), "source_identity_ceiling": "LOCAL_CHECKOUT_COORDINATES_VALIDATED_PROVIDER_MEMBERSHIP_NOT_PROVEN", **resource}
            acceptance_digest = _digest({"task": task, "targets": candidate["targets"]})
            quest = {**(prior_quest or {}), "quest_id": work_key, "work_key": work_key, "attempt": attempt, "status": "ACTIVE", "claim_id": claim_id, "session_id": next_session_id, "fence": next_fence, "task": task, "targets": candidate["targets"], "acceptance_digest": acceptance_digest, "input_head": base, "prompt_digest": prompt_at_base, "claimed_at": _iso(now), **resource}
            parent_id = quest.get("parent_quest_id")
            if parent_id and parent_id in state["quests"]:
                state["quests"][parent_id]["successor_consumed_by"] = next_session_id
                state["quests"][parent_id]["successor_consumed_at"] = _iso(now)
            presence = {"artifact": PRESENCE_ARTIFACT, "agent_id": agent_id, "claim_id": claim_id, "session_id": next_session_id, "fence": next_fence, "status": "ACTIVE", "mode": "PRIMARY", "task": task, "work_key": work_key, "targets": candidate["targets"], "details": f"organism-room role={session['role']}", "join_of": None, "started_at": session["entered_at"], "heartbeat_at": _iso(now), "lease_seconds": lease, "expires_at": session["lease_until"], "claim_base_head": base, "law": "FENCED_CLAIM_NOT_COMPLETION"}
            state["version"] += 1
            state["logical_time"] += 1
            state["sessions"][agent_id] = session
            state["quests"][work_key] = quest
            result = {"status": "WORK_CLAIMED" if signed_in_upgrade else "ENTERED", "session": session, "session_token": _token(next_session_id, next_fence), "allocation": allocation, "waves": list(WAVES), "next": "execute the material delta; heartbeat before lease expiry"}
            self._remember(state, agent_id, idempotency_key, command, result)
            files = {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence)}
            if not signed_in_upgrade:
                signin_rel, signin_event = self.board._event("SIGNIN", agent_id, {"session_id": next_session_id, "fence": next_fence, "role": session["role"], "wave": session["wave"], "composed_with_work": True})
                files[signin_rel] = _json_text(signin_event)
            event_rel, event = self.board._event("WORK", agent_id, {"session_id": next_session_id, "fence": next_fence, "claim_id": claim_id, "quest_id": work_key, "role": session["role"], "wave": session["wave"]})
            files[event_rel] = _json_text(event)
            return {"files": files, "message": f"organism room work {agent_id}", "result": result}

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
            event_rel, event = self.board._event("HEARTBEAT", agent_id, {"session_id": session_id, "fence": fence, "status": result["status"]})
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
            if session.get("status") == "STALE" or session.get("prompt_digest") != _prompt_digest(self.board._root()):
                raise ValueError("COMPLETION_STALE_PROMPT_HOLD")
            quest = state["quests"].get(session["quest_id"])
            if not quest or quest.get("session_id") != session_id or quest.get("fence") != fence or quest.get("status") != "ACTIVE":
                raise ValueError("CLAIM_ATTEMPT_HOLD")
            expected = {"quest_id": quest["quest_id"], "attempt": quest["attempt"], "session_id": session_id, "fence": fence, "input_head": quest["input_head"], "prompt_digest": quest["prompt_digest"], "acceptance_digest": quest["acceptance_digest"], "artifact_digests": artifacts, "result": result}
            verify_authority_receipt(receipt, expected, self.authority_keys)
            successor = None
            if residual:
                successor_id = f"{quest['quest_id']}:successor:{quest['attempt']}"
                successor = {"quest_id": successor_id, "work_key": successor_id, "attempt": 0, "status": "READY", "task": residual, "parent_quest_id": quest["quest_id"], "parent_attempt": quest["attempt"], "parent_output_digest": _digest(artifacts)}
                state["quests"][successor_id] = successor
            elif terminal_reason not in TERMINAL_REASONS:
                raise ValueError("SUCCESSOR_OR_VERIFIED_TERMINAL_REASON_REQUIRED")
            quest.update({"status": "VERIFIED", "artifact_digests": artifacts, "result": result, "receipt_authority": receipt["authority_id"], "evaluator_version": receipt["claims"]["evaluator_version"], "observed_at": receipt["claims"]["observed_at"], "completed_at": _iso(now), "successor_id": (successor or {}).get("quest_id"), "terminal_reason": terminal_reason})
            session["claim_status"] = "VERIFIED"
            state["version"] += 1
            state["logical_time"] += 1
            outcome = {"status": "VERIFIED_COMPLETION", "quest": quest, "successor": successor, "campaign_terminal": bool(not successor and terminal_reason in TERMINAL_REASONS)}
            self._remember(state, agent_id, key, command, outcome)
            event_rel, event = self.board._event("DELTA", agent_id, {"session_id": session_id, "fence": fence, "quest_id": quest["quest_id"], "attempt": quest["attempt"], "successor_id": (successor or {}).get("quest_id"), "authority_id": receipt["authority_id"], "result": result})
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
            session = self._authenticate(state, agent_id, session_id, fence, session_token, now, require_presence=False)
            current_presence = self.board._read_json(self.board._root() / self.board._presence_path(agent_id)) or {}
            if current_presence.get("status") == "ACTIVE" and any(current_presence.get(k) != session.get(k) for k in ("session_id", "fence", "claim_id")):
                raise ValueError("ROOM_PRESENCE_LINEAGE_HOLD")
            quest = state["quests"].get(session["quest_id"])
            if quest and quest.get("status") == "ACTIVE" and not force:
                return {"return": {"status": "OPEN_CLAIM_HOLD", "next": "complete, hand off, or force sign-out"}}
            if quest and quest.get("status") == "ACTIVE":
                quest.update({"status": "READY", "session_id": None, "fence": None, "claim_id": None, "abandoned_by": session_id})
            session.update({"status": "RELEASED", "released_at": _iso(now), "handoff_to": handoff_to})
            presence = current_presence
            presence.update({"status": "RELEASED", "release_status": "HANDOFF" if handoff_to else ("ABANDONED" if force else "DONE"), "released_at": session["released_at"], "handoff_to": handoff_to})
            state["version"] += 1
            state["logical_time"] += 1
            result = {"status": "SIGNED_OUT", "session": session, "requeued": bool(quest and quest.get("status") == "READY")}
            self._remember(state, agent_id, key, command, result)
            event_rel, event = self.board._event("SIGNOUT", agent_id, {"session_id": session_id, "fence": fence, "force": force, "handoff_to": handoff_to})
            return {"files": {STATE_PATH: _json_text(state), self.board._presence_path(agent_id): _json_text(presence), event_rel: _json_text(event)}, "message": f"organism room sign out {agent_id}", "result": result}

        return self.board._mutate(agent_id=agent_id, remote=remote, build_files=build)

    def call_tool(self, name: str, args: dict) -> dict:
        if name != TOOL_NAME:
            raise KeyError(name)
        action = str(args.get("action") or "").lower()
        kwargs = {key: value for key, value in args.items() if key != "action" and value is not None}
        if action == "read":
            return self.read(**kwargs)
        if action == "sign_in":
            return self.sign_in(**kwargs)
        if action == "enter":
            return self.enter(**kwargs)
        if action == "heartbeat":
            return self.heartbeat(**kwargs)
        if action == "complete":
            return self.complete(**kwargs)
        if action == "sign_out":
            return self.sign_out(**kwargs)
        raise ValueError("action must be read, sign_in, enter, heartbeat, complete, or sign_out")


ORGANISM_ROOM_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Mandatory fenced room lifecycle over ATHENA's existing Git-backed Message Board: read/ack current prompt and HEAD, SIGNIN independently, claim exact WORK, heartbeat, externally verify a DELTA, consume or create a successor, and SIGNOUT only at actual exit.",
    "inputSchema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["read", "sign_in", "enter", "heartbeat", "complete", "sign_out"]},
            "agent_id": {"type": ["string", "null"]}, "task": {"type": ["string", "null"]}, "work_key": {"type": ["string", "null"]},
            "targets": {"type": "array", "items": {"type": "string"}}, "ack_head": {"type": ["string", "null"]}, "ack_prompt_digest": {"type": ["string", "null"]},
            "resource_upper_bound": {"type": ["object", "null"]}, "room_budget": {"type": ["object", "null"]}, "protected_reserve": {"type": ["object", "null"]},
            "capabilities": {"type": "array", "items": {"type": "string"}},
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
