from __future__ import annotations

import hashlib
import json
import math
from typing import Any


TOOL_NAME = "athena_organism_room"
ROOM_ARTIFACT = "ATHENA.ORGANISM.ROOM.V1"
ROOM_EVENT_ARTIFACT = "ATHENA.ORGANISM.ROOM.EVENT.V1"

WAVES = ("W0", "W1", "W2")
WAVE_PRIOR = {"W0": 0.50, "W1": 0.30, "W2": 0.20}
DOMAINS = ("GIT", "MATH", "NAV", "CORPUS", "TOOLS", "ALCHEMY", "MYTH", "META")
DOMAIN_PRIOR = {
    "GIT": 0.20,
    "MATH": 0.15,
    "NAV": 0.15,
    "CORPUS": 0.15,
    "TOOLS": 0.10,
    "ALCHEMY": 0.10,
    "MYTH": 0.05,
    "META": 0.10,
}
ROOM_KINDS = {"WORK", "DELTA", "NEED", "OFFER"}
STOP_CLASSES = {"COMPLETED", "BLOCKED", "AUTHORITY_BOUNDARY", "CAPABILITY_BOUNDARY", "RESOURCE_BOUNDARY", "NO_POSITIVE_FRONTIER", "ABANDONED"}

LAWS = [
    "FULL_PROMPT_HYDRATION_PRECEDES_ROOM_ENTRY",
    "MESSAGE_BOARD_V1_IS_SOLE_PRESENCE_AND_CLAIM_TRANSPORT",
    "ISSUE_555_IS_ADVISORY_MIRROR_ONLY",
    "PRESENCE != HOST_EXECUTION != EXECUTION_AUTHORITY",
    "N_DECLARED != N_PRESENT != N_EXECUTION_OBSERVED",
    "LEASE_EXPIRY != COMPLETION",
    "SIGNOUT != VERIFIED_RESULT",
    "OLD_CLAIM_FENCE_CANNOT_MUTATE_NEW_SESSION",
    "PERCENTAGES_NEVER_MANUFACTURE_NON_POSITIVE_WORK",
]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _positive_int(value: Any, field: str) -> int:
    result = int(value)
    if result < 0:
        raise ValueError(f"{field} must be nonnegative")
    return result


def _normalize_shares(prior: dict[str, float], pressure: dict[str, float] | None = None, eligible: set[str] | None = None) -> dict[str, float]:
    pressure = pressure or {}
    keys = [key for key in prior if eligible is None or key in eligible]
    if not keys:
        return {}
    weighted = {}
    for key in keys:
        p = max(-1.0, min(1.0, float(pressure.get(key, 0.0))))
        weighted[key] = prior[key] * math.exp(math.log(4.0) * p)
    base_total = sum(prior[key] for key in keys)
    pressure_total = sum(weighted.values())
    mixed = {
        key: 0.5 * (prior[key] / base_total) + 0.5 * (weighted[key] / pressure_total)
        for key in keys
    }
    total = sum(mixed.values())
    return {key: mixed[key] / total for key in keys}


def hamilton(seats: int, shares: dict[str, float], floors: dict[str, int] | None = None) -> dict[str, int]:
    """Deterministic largest-remainder apportionment with optional hard floors."""
    seats = _positive_int(seats, "seats")
    floors = dict(floors or {})
    if not shares:
        if seats:
            raise ValueError("cannot allocate seats without eligible shares")
        return {}
    if any(value < 0 for value in floors.values()) or sum(floors.values()) > seats:
        raise ValueError("invalid allocation floors")
    result = {key: int(floors.get(key, 0)) for key in shares}
    remaining = seats - sum(result.values())
    normalized = {key: max(0.0, float(value)) for key, value in shares.items()}
    total = sum(normalized.values())
    if total <= 0:
        raise ValueError("share mass must be positive")
    normalized = {key: value / total for key, value in normalized.items()}
    raw = {key: remaining * normalized[key] for key in shares}
    for key in shares:
        result[key] += math.floor(raw[key])
    leftover = seats - sum(result.values())
    ranking = sorted(shares, key=lambda key: (-(raw[key] - math.floor(raw[key])), key))
    for key in ranking[:leftover]:
        result[key] += 1
    return result


def allocation_plan(population: int, pressures: dict[str, float] | None = None, eligible_domains: list[str] | None = None) -> dict:
    """Compile truthful small-N roles and scalable three-wave/domain quotas."""
    n = _positive_int(population, "population")
    eligible = set(eligible_domains or DOMAINS)
    invalid = eligible - set(DOMAINS)
    if invalid:
        raise ValueError(f"unknown domains: {sorted(invalid)}")
    if n == 0:
        return {"population": 0, "assignments": [], "wave_quota": {}, "domain_quota": {}, "standing": "NO_PRESENT_WORKERS"}
    if n == 1:
        return {
            "population": 1,
            "assignments": [{
                "seat": 1,
                "function": "ROOT_GENERALIST",
                "wave_schedule": ["W0", "W0", "W1", "W0", "W2", "W0", "W1", "W0", "W1", "W2"],
                "domain_scope": sorted(eligible),
            }],
            "wave_quota": {"W0": 1, "W1": 0, "W2": 0},
            "domain_quota": {},
            "standing": "TIME_SLICED_HORIZONS_NO_FICTIONAL_CONCURRENCY",
        }
    functions = [
        "ROOT_DELIVERY_INTEGRATOR",
        "MATH_NAV_LIMITS_EXPLORER",
        "CORPUS_MYTH_DISTILLER",
        "TOOLFORGE_ALCHEMIST",
        "HOMEOSTASIS_ADVERSARIAL_SCOUT",
    ]
    floors = {wave: 1 for wave in WAVES} if n >= 3 else {}
    wave_quota = hamilton(n, WAVE_PRIOR, floors)
    domain_shares = _normalize_shares(DOMAIN_PRIOR, pressures, eligible)
    domain_quota = hamilton(n, domain_shares)
    assignments = []
    for index in range(n):
        assignments.append({
            "seat": index + 1,
            "function": functions[index] if index < len(functions) else "PRESSURE_ROUTED_GENERALIST",
            "identity_is_permanent": False,
        })
    return {
        "population": n,
        "assignments": assignments,
        "wave_quota": wave_quota,
        "domain_quota": domain_quota,
        "standing": "TARGET_QUOTAS_REQUIRE_POSITIVE_FEASIBLE_QUESTS",
    }


def _room_packet(kind: str, *, agent_id: str, session_id: str, claim_id: str, expected_head: str, wave: str | None, domain: str | None, payload: dict) -> dict:
    if kind not in ROOM_KINDS:
        raise ValueError(f"unsupported room event kind: {kind}")
    if wave is not None and wave not in WAVES:
        raise ValueError("wave must be W0, W1, or W2")
    if domain is not None and domain not in DOMAINS:
        raise ValueError(f"domain must be one of {DOMAINS}")
    packet = {
        "artifact": ROOM_EVENT_ARTIFACT,
        "kind": kind,
        "agent_id": agent_id,
        "session_id": session_id,
        "claim_id": claim_id,
        "expected_head": expected_head,
        "wave": wave,
        "domain": domain,
        "payload": payload,
        "standing": "COORDINATION_EVENT_NOT_EXECUTION_OR_AUTHORITY",
    }
    packet["semantic_digest"] = _digest(packet)
    return packet


class OrganismRoomRuntime:
    """Thin organism-room lifecycle over the qualified MessageBoardRuntime.

    It deliberately creates no second presence or claim ledger.
    """

    def __init__(self, board):
        self.board = board

    def _head(self) -> str:
        return self.board.git.head()

    def _active_presence(self, agent_id: str) -> dict | None:
        snapshot = self.board.snapshot(agent_id=agent_id, include_stale=True)
        row = snapshot.get("self")
        return row if row and row.get("status") == "ACTIVE" else None

    def _fence(self, *, agent_id: str, session_id: str, claim_id: str, expected_head: str) -> dict:
        current = self._head()
        if expected_head != current:
            raise ValueError(f"STALE_GIT_HEAD expected={expected_head} current={current}")
        row = self._active_presence(agent_id)
        if not row:
            raise ValueError("NOT_PRESENT_HOLD")
        if str(row.get("claim_id")) != str(claim_id):
            raise ValueError("STALE_CLAIM_FENCE")
        details = row.get("details")
        try:
            bound = json.loads(details) if isinstance(details, str) else {}
        except json.JSONDecodeError:
            bound = {}
        if bound.get("session_id") != session_id:
            raise ValueError("STALE_SESSION_FENCE")
        return row

    def read(self, a: dict) -> dict:
        board = self.board.read(
            agent_id=a.get("agent_id"),
            limit=a.get("limit", 100),
            include_stale=bool(a.get("include_stale", True)),
            remote=a.get("remote", "origin"),
            shared_remote_mode=a.get("shared_remote_mode", "REQUIRED"),
        )
        active = board.get("active") or []
        plan = allocation_plan(len(active), a.get("pressures"), a.get("eligible_domains"))
        return {
            "artifact": ROOM_ARTIFACT,
            "status": board.get("status"),
            "board": board,
            "census": {
                "N_declared": a.get("declared_population"),
                "N_present": len(active),
                "N_execution_observed": "UNKNOWN",
                "law": "ACTIVE_LEASE_IS_NOT_PROOF_OF_SIMULTANEOUS_COMPUTATION",
            },
            "allocation": plan,
            "laws": list(LAWS),
        }

    def enter(self, a: dict) -> dict:
        expected = str(a["expected_head"])
        current = self._head()
        if expected != current:
            raise ValueError(f"STALE_GIT_HEAD expected={expected} current={current}")
        session_id = str(a["session_id"])
        details = _canonical({
            "session_id": session_id,
            "prompt_stack_digest": str(a["prompt_stack_digest"]),
            "wave_capacity": list(a.get("wave_capacity") or WAVES),
            "domains": list(a.get("domains") or []),
            "authority": "NONE_FROM_ROOM",
        })
        result = self.board.present(
            agent_id=a["agent_id"],
            task=a["task"],
            work_key=a.get("work_key"),
            targets=a.get("targets") or [],
            details=details,
            mode=a.get("mode", "PRIMARY"),
            replication_reason=a.get("replication_reason"),
            lease_seconds=a.get("lease_seconds", 1800),
            remote=a.get("remote", "origin"),
        )
        result["room_event"] = "SIGNIN"
        result["session_id"] = session_id
        result["laws"] = list(LAWS)
        return result

    def emit(self, a: dict) -> dict:
        kind = str(a["event_kind"]).upper()
        row = self._fence(
            agent_id=a["agent_id"], session_id=a["session_id"],
            claim_id=a["claim_id"], expected_head=a["expected_head"],
        )
        packet = _room_packet(
            kind,
            agent_id=a["agent_id"], session_id=a["session_id"], claim_id=a["claim_id"],
            expected_head=a["expected_head"], wave=a.get("wave"), domain=a.get("domain"),
            payload=dict(a.get("payload") or {}),
        )
        board_kind = {"WORK": "UPDATE", "DELTA": "DISCOVERY", "NEED": "QUESTION", "OFFER": "HELP"}[kind]
        result = self.board.post(
            agent_id=a["agent_id"], message=_canonical(packet), message_kind=board_kind,
            recipients=a.get("recipients") or [], remote=a.get("remote", "origin"),
        )
        result.update({"room_event": packet, "presence": row})
        return result

    def heartbeat(self, a: dict) -> dict:
        self._fence(
            agent_id=a["agent_id"], session_id=a["session_id"],
            claim_id=a["claim_id"], expected_head=a["expected_head"],
        )
        result = self.board.heartbeat(
            agent_id=a["agent_id"], lease_seconds=a.get("lease_seconds"),
            note=a.get("note"), remote=a.get("remote", "origin"),
        )
        result["room_event"] = "HEARTBEAT"
        return result

    def signout(self, a: dict) -> dict:
        self._fence(
            agent_id=a["agent_id"], session_id=a["session_id"],
            claim_id=a["claim_id"], expected_head=a["expected_head"],
        )
        stop_class = str(a["stop_class"]).upper()
        if stop_class not in STOP_CLASSES:
            raise ValueError(f"stop_class must be one of {sorted(STOP_CLASSES)}")
        evidence = list(a.get("result_refs") or [])
        residual = list(a.get("residual_portfolio") or [])
        if stop_class == "COMPLETED" and not evidence:
            raise ValueError("COMPLETED_SIGNOUT_REQUIRES_RESULT_REFERENCE")
        if stop_class == "BLOCKED" and not residual:
            raise ValueError("BLOCKED_SIGNOUT_REQUIRES_RESIDUAL")
        release_status = "DONE" if stop_class == "COMPLETED" else ("ABANDONED" if stop_class == "ABANDONED" else "PAUSED")
        outcome = _canonical({
            "stop_class": stop_class,
            "result_refs": evidence,
            "residual_portfolio": residual,
            "next_routes": list(a.get("next_routes") or []),
            "standing": "SIGNOUT_TERMINATES_SESSION_NOT_PROOF_OF_RESULT",
        })
        result = self.board.release(
            agent_id=a["agent_id"], release_status=release_status,
            outcome=outcome, handoff_to=a.get("handoff_to"), remote=a.get("remote", "origin"),
        )
        result.update({"room_event": "SIGNOUT", "stop_class": stop_class})
        return result

    def call_tool(self, name: str, a: dict) -> dict:
        if name != TOOL_NAME:
            raise KeyError(name)
        action = str(a.get("action") or "").lower()
        if action == "read" or action == "allocate":
            return self.read(a)
        if action == "enter":
            return self.enter(a)
        if action in {"work", "delta", "need", "offer"}:
            return self.emit({**a, "event_kind": action.upper()})
        if action == "heartbeat":
            return self.heartbeat(a)
        if action == "signout":
            return self.signout(a)
        raise ValueError("action must be read, allocate, enter, work, heartbeat, delta, need, offer, or signout")


ORGANISM_ROOM_TOOLS = [{
    "name": TOOL_NAME,
    "description": "Enter and operate Athena's executable organism room over Message Board V1. Full prompt hydration must precede enter. The tool provides truthful lease-backed presence, fenced work/delta/need/offer events, three-wave/domain allocation, heartbeat and typed signout. Presence and comments never grant execution authority.",
    "inputSchema": {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["read", "allocate", "enter", "work", "heartbeat", "delta", "need", "offer", "signout"]},
            "agent_id": {"type": ["string", "null"]},
            "session_id": {"type": ["string", "null"]},
            "claim_id": {"type": ["string", "null"]},
            "expected_head": {"type": ["string", "null"]},
            "prompt_stack_digest": {"type": ["string", "null"]},
            "task": {"type": ["string", "null"]},
            "work_key": {"type": ["string", "null"]},
            "targets": {"type": "array", "items": {"type": "string"}},
            "wave": {"type": ["string", "null"], "enum": ["W0", "W1", "W2", None]},
            "domain": {"type": ["string", "null"], "enum": list(DOMAINS) + [None]},
            "wave_capacity": {"type": "array", "items": {"type": "string", "enum": list(WAVES)}},
            "domains": {"type": "array", "items": {"type": "string", "enum": list(DOMAINS)}},
            "payload": {"type": "object"},
            "recipients": {"type": "array", "items": {"type": "string"}},
            "lease_seconds": {"type": ["integer", "null"], "minimum": 60, "maximum": 86400},
            "mode": {"type": "string", "enum": ["PRIMARY", "REPLICA"]},
            "replication_reason": {"type": ["string", "null"]},
            "note": {"type": ["string", "null"]},
            "stop_class": {"type": ["string", "null"]},
            "result_refs": {"type": "array", "items": {"type": "string"}},
            "residual_portfolio": {"type": "array", "items": {"type": "string"}},
            "next_routes": {"type": "array", "items": {"type": "string"}},
            "handoff_to": {"type": ["string", "null"]},
            "pressures": {"type": "object", "additionalProperties": {"type": "number"}},
            "eligible_domains": {"type": "array", "items": {"type": "string", "enum": list(DOMAINS)}},
            "declared_population": {"type": ["integer", "null"], "minimum": 0},
            "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            "include_stale": {"type": "boolean"},
            "remote": {"type": "string"},
            "shared_remote_mode": {"type": "string", "enum": ["REQUIRED", "BEST_EFFORT", "DISABLED"]}
        },
        "additionalProperties": False
    }
}]

ORGANISM_ROOM_TOOL_NAMES = {TOOL_NAME}
