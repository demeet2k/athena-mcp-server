from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from .agent_bootstrap import AGENT_BOOT_TOOLS
from .message_board import MessageBoardRuntime

ARTIFACT = "ATHENA.AGENT.BOOT.MESSAGE_BOARD.V1"
_COORDINATION_MODES = {"AUTO", "READ_ONLY", "DISABLED"}
_CLAIM_MODES = {"PRIMARY", "REPLICA"}
_COORDINATION_FIELDS = {
    "coordination_mode",
    "work_key",
    "targets",
    "coordination_details",
    "coordination_claim_mode",
    "lease_seconds",
    "replication_reason",
}
_LAWS = [
    "BOOT != CLAIM unless coordination succeeds",
    "MESSAGE_BOARD = SOLE_PRESENCE_CLAIM_MESSAGE_AUTHORITY",
    "READ_BOARD_BEFORE_EXPENSIVE_SHARED_WORK",
    "PRESENT_BEFORE_WORK",
    "DUPLICATE_WORK_HOLD -> DO_NOT_DISPATCH_DUPLICATE_LANE",
    "AUTO != AUTO_JOIN",
    "FUZZY_SIMILARITY != DUPLICATE_PROOF",
    "READ_ONLY != EXECUTION_CLAIM",
    "MISSING_WORK_KEY != FABRICATED_MATA_WORK_KEY",
    "BOARD_SHARED_FRONTIER_HOLD -> BOOTSTRAP_HOLD",
]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _mode(value: str | None) -> str:
    mode = str(value or "AUTO").upper()
    if mode not in _COORDINATION_MODES:
        raise ValueError("coordination_mode must be AUTO, READ_ONLY, or DISABLED")
    return mode


def _claim_mode(value: str | None) -> str | None:
    if value is None:
        return None
    mode = str(value).upper()
    if mode not in _CLAIM_MODES:
        raise ValueError("coordination_claim_mode must be PRIMARY or REPLICA")
    return mode


def _lease_seconds(value: int | None) -> int:
    lease = int(value or 1800)
    if lease < 60 or lease > 86400:
        raise ValueError("lease_seconds must be between 60 and 86400")
    return lease


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _target(value: Any) -> str:
    return str(value or "").strip().replace("\\", "/").rstrip("/").lower()


def _targets(values: Any) -> list[str]:
    return sorted({_target(v) for v in (values or []) if _target(v)})


def _parse_time(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _active_self(snapshot: dict, agent_id: str) -> dict | None:
    return next(
        (row for row in (snapshot.get("active") or []) if row.get("agent_id") == agent_id),
        None,
    )


def _compatible_active(
    row: dict,
    *,
    task: str,
    work_key: str | None,
    targets: list[str],
    claim_mode: str | None,
) -> tuple[bool, list[str]]:
    differences: list[str] = []
    if _norm(row.get("task")) != _norm(task):
        differences.append("TASK")
    if work_key is not None and _norm(row.get("work_key")) != _norm(work_key):
        differences.append("WORK_KEY")
    if targets and _targets(row.get("targets")) != targets:
        differences.append("TARGETS")
    if claim_mode is not None and str(row.get("mode") or "").upper() != claim_mode:
        differences.append("CLAIM_MODE")
    return not differences, differences


def _remaining_lease_seconds(row: dict) -> float | None:
    expires = _parse_time(row.get("expires_at"))
    if expires is None:
        return None
    return (expires - datetime.now(timezone.utc)).total_seconds()


def _renewal_threshold(row: dict) -> float:
    try:
        lease = max(60, int(row.get("lease_seconds") or 1800))
    except (TypeError, ValueError):
        lease = 1800
    return float(max(30, min(300, round(lease * 0.20))))


def _remote_witness(value: dict, fallback: dict | None = None) -> dict:
    for key in ("remote_publish", "remote_sync"):
        witness = value.get(key)
        if isinstance(witness, dict):
            return witness
    if isinstance(fallback, dict):
        witness = fallback.get("remote_sync")
        if isinstance(witness, dict):
            return witness
    return {}


def _routing_basis(coordination: dict) -> dict:
    board = coordination.get("board") or {}
    presence = coordination.get("presence") or {}
    unread = board.get("unread_messages") or []
    conflicts = coordination.get("conflicts") or []
    return {
        "mode": coordination.get("mode"),
        "pre_dispatch": coordination.get("pre_dispatch"),
        "claim": {
            "claim_id": presence.get("claim_id"),
            "agent_id": presence.get("agent_id"),
            "mode": presence.get("mode"),
            "task": presence.get("task"),
            "work_key": presence.get("work_key"),
            "targets": presence.get("targets") or [],
            "join_of": presence.get("join_of"),
        },
        "conflicts": [
            {
                "agent_id": (row.get("agent") or {}).get("agent_id"),
                "claim_id": (row.get("agent") or {}).get("claim_id"),
                "reasons": row.get("reasons") or [],
            }
            for row in conflicts
        ],
        "exact_overlap_edges": [
            row
            for row in (board.get("exact_overlaps") or [])
            if presence.get("agent_id") in (row.get("agents") or [])
        ],
        "unread_message_ids": [row.get("event_id") for row in unread],
    }


def _coordination_packet(
    self,
    *,
    agent_id: str,
    task: str,
    coordination_mode: str,
    work_key: str | None,
    targets: list[str],
    details: str | None,
    claim_mode: str | None,
    lease_seconds: int,
    replication_reason: str | None,
    remote: str,
) -> dict:
    mode = _mode(coordination_mode)
    task = str(task or "").strip()
    work_key = str(work_key).strip() if work_key is not None else None
    work_key = work_key or None
    target_list = _targets(targets)
    claim_mode = _claim_mode(claim_mode)

    if replication_reason and claim_mode != "REPLICA":
        raise ValueError(
            "replication_reason requires coordination_claim_mode=REPLICA"
        )
    if claim_mode == "REPLICA" and not str(replication_reason or "").strip():
        raise ValueError("REPLICA requires replication_reason")

    if mode == "DISABLED":
        value = {
            "artifact": ARTIFACT,
            "mode": mode,
            "status": "DISABLED",
            "pre_dispatch": "DISABLED",
            "presence": None,
            "board": None,
            "work_key_source": "EXPLICIT" if work_key else "NONE",
            "laws": list(_LAWS),
        }
        value["routing_digest"] = _sha(_routing_basis(value))
        return value

    board = getattr(self, "_agent_boot_message_board_runtime_v1", None)
    if board is None:
        board = MessageBoardRuntime(self.git)
        self._agent_boot_message_board_runtime_v1 = board

    snapshot = board.read(
        agent_id=agent_id,
        limit=50,
        include_stale=True,
        remote=remote,
        shared_remote_mode="REQUIRED",
    )
    shared = bool(snapshot.get("shared_frontier_verified"))

    if mode == "READ_ONLY" or not task:
        value = {
            "artifact": ARTIFACT,
            "mode": mode,
            "status": snapshot.get("status"),
            "pre_dispatch": "ADVISORY_ONLY",
            "presence": _active_self(snapshot, agent_id),
            "board": snapshot,
            "work_key_source": "EXPLICIT" if work_key else "NONE",
            "shared_frontier_verified": shared,
            "laws": list(_LAWS),
        }
        value["routing_digest"] = _sha(_routing_basis(value))
        return value

    if snapshot.get("status") != "OK" or not shared:
        value = {
            "artifact": ARTIFACT,
            "mode": mode,
            "status": snapshot.get("status")
            or "MESSAGE_BOARD_SHARED_FRONTIER_HOLD",
            "pre_dispatch": "HOLD",
            "presence": _active_self(snapshot, agent_id),
            "board": snapshot,
            "work_key_source": "EXPLICIT" if work_key else "NONE",
            "shared_frontier_verified": False,
            "laws": list(_LAWS),
        }
        value["routing_digest"] = _sha(_routing_basis(value))
        return value

    existing = _active_self(snapshot, agent_id)
    transition: dict
    if existing is not None:
        compatible, differences = _compatible_active(
            existing,
            task=task,
            work_key=work_key,
            targets=target_list,
            claim_mode=claim_mode,
        )
        if not compatible:
            value = {
                "artifact": ARTIFACT,
                "mode": mode,
                "status": "AGENT_ALREADY_PRESENT_HOLD",
                "pre_dispatch": "HOLD",
                "presence": existing,
                "board": snapshot,
                "differences": differences,
                "next": "release current claim before switching work",
                "work_key_source": "EXPLICIT" if work_key else "NONE",
                "shared_frontier_verified": True,
                "laws": list(_LAWS),
            }
            value["routing_digest"] = _sha(_routing_basis(value))
            return value

        remaining = _remaining_lease_seconds(existing)
        threshold = _renewal_threshold(existing)
        if remaining is None or remaining <= threshold:
            transition = board.heartbeat(
                agent_id=agent_id,
                expected_claim_id=existing["claim_id"],
                lease_seconds=lease_seconds or None,
                note="agent bootstrap lease renewal",
                remote=remote,
            )
        else:
            transition = {
                "status": "PRESENCE_REUSED",
                "presence": existing,
                "durable_return": True,
                "remote_sync": snapshot.get("remote_sync") or {},
                "lease_remaining_seconds": remaining,
                "renewal_threshold_seconds": threshold,
            }
    else:
        transition = board.present(
            agent_id=agent_id,
            task=task,
            work_key=work_key,
            targets=target_list,
            details=details,
            mode=claim_mode or "PRIMARY",
            replication_reason=replication_reason,
            lease_seconds=lease_seconds,
            remote=remote,
        )
        if transition.get("status") == "ALREADY_PRESENT":
            transition = board.heartbeat(
                agent_id=agent_id,
                expected_claim_id=transition["presence"]["claim_id"],
                lease_seconds=lease_seconds or None,
                note="agent bootstrap concurrent same-claim renewal",
                remote=remote,
            )

    witness = _remote_witness(transition, snapshot)
    shared_after = bool(witness.get("shared_frontier_verified"))
    transition_status = str(transition.get("status") or "UNKNOWN")
    allowed = (
        transition_status in {"PRESENT", "PRESENCE_REUSED", "HEARTBEAT"}
        and bool(transition.get("durable_return", True))
        and shared_after
    )

    board_after = board.snapshot(
        agent_id=agent_id,
        limit=50,
        include_stale=True,
        remote_sync=witness,
    )
    presence = _active_self(board_after, agent_id)
    value = {
        "artifact": ARTIFACT,
        "mode": mode,
        "status": transition_status,
        "pre_dispatch": "ALLOW" if allowed else "HOLD",
        "presence": presence,
        "board": board_after,
        "transition": {
            key: transition.get(key)
            for key in (
                "status",
                "potential_overlaps",
                "hard_overlap_override",
                "conflicts",
                "next",
                "attempt",
                "lease_remaining_seconds",
                "renewal_threshold_seconds",
            )
            if key in transition
        },
        "conflicts": transition.get("conflicts") or [],
        "work_key_source": "EXPLICIT" if work_key else "NONE",
        "shared_frontier_verified": shared_after,
        "durable_return": bool(transition.get("durable_return", True)),
        "laws": list(_LAWS),
    }
    value["routing_digest"] = _sha(_routing_basis(value))
    return value


def install_agent_bootstrap_message_board(runtime_cls) -> None:
    """Install Message Board as the outer pre-dispatch membrane for AGENT_BOOT_V1."""

    if getattr(runtime_cls, "_athena_boot_message_board_v1_registered", False):
        return

    original_bootstrap = runtime_cls.bootstrap
    original_refresh = runtime_cls.refresh
    original_call_tool = runtime_cls.call_tool

    def bootstrap_with_message_board(
        self,
        *args,
        coordination_mode=None,
        work_key=None,
        targets=None,
        coordination_details=None,
        coordination_claim_mode=None,
        lease_seconds=None,
        replication_reason=None,
        **kwargs,
    ):
        override = getattr(self, "_agent_boot_message_board_override", None)
        if isinstance(override, dict):
            if coordination_mode is None:
                coordination_mode = override.get("coordination_mode")
            if work_key is None:
                work_key = override.get("work_key")
            if targets is None:
                targets = override.get("targets")
            if coordination_details is None:
                coordination_details = override.get("coordination_details")
            if coordination_claim_mode is None:
                coordination_claim_mode = override.get("coordination_claim_mode")
            if lease_seconds is None:
                lease_seconds = override.get("lease_seconds")
            if replication_reason is None:
                replication_reason = override.get("replication_reason")

        mode = _mode(coordination_mode)
        agent_id = kwargs.get("agent_id")
        task = kwargs.get("task", "")
        remote = kwargs.get("remote", "origin")
        if not agent_id:
            return original_bootstrap(self, *args, **kwargs)

        config = {
            "coordination_mode": mode,
            "work_key": str(work_key).strip() if work_key is not None else None,
            "targets": list(targets or []),
            "coordination_details": coordination_details,
            "coordination_claim_mode": _claim_mode(coordination_claim_mode),
            "lease_seconds": _lease_seconds(lease_seconds),
            "replication_reason": replication_reason,
        }
        coordination = _coordination_packet(
            self,
            agent_id=agent_id,
            task=task,
            coordination_mode=mode,
            work_key=config["work_key"],
            targets=config["targets"],
            details=coordination_details,
            claim_mode=config["coordination_claim_mode"],
            lease_seconds=config["lease_seconds"],
            replication_reason=replication_reason,
            remote=remote,
        )

        # Coordination precedes world-state composition so a successful claim/renewal
        # is already part of the Git ancestry observed by the returned boot packet.
        packet = original_bootstrap(self, *args, **kwargs)
        packet["coordination"] = coordination
        packet.setdefault("execution_surface", {})["message_board_pre_dispatch"] = {
            "mode": mode,
            "pre_dispatch": coordination.get("pre_dispatch"),
            "standing": "MESSAGE_BOARD_AUTHORITY",
        }
        packet.setdefault("witnesses", {})["message_board"] = {
            "shared_frontier_verified": coordination.get(
                "shared_frontier_verified", False
            ),
            "git_head": (coordination.get("board") or {}).get("git_head"),
            "routing_digest": coordination.get("routing_digest"),
        }
        packet.setdefault("return_contract", {})[
            "message_board_pre_dispatch_required"
        ] = bool(mode == "AUTO" and str(task or "").strip())
        laws = packet.setdefault("laws", [])
        for law in _LAWS:
            if law not in laws:
                laws.append(law)

        holds = set(str(x) for x in packet.get("holds") or [])
        if coordination.get("pre_dispatch") == "HOLD":
            holds.add("MESSAGE_BOARD_PRE_DISPATCH_HOLD")
            if coordination.get("status"):
                holds.add(str(coordination["status"]))
        packet["holds"] = sorted(holds)
        if holds:
            packet["status"] = "BOOTSTRAP_HOLD"

        session_id = packet.get("session_id")
        if (
            session_id
            and hasattr(self, "_sessions")
            and session_id in self._sessions
        ):
            self._sessions[session_id]["coordination_config"] = dict(config)
            self._sessions[session_id]["coordination_digest"] = coordination.get(
                "routing_digest"
            )
        return packet

    def refresh_with_message_board(
        self,
        *args,
        coordination_mode=None,
        work_key=None,
        targets=None,
        coordination_details=None,
        coordination_claim_mode=None,
        lease_seconds=None,
        replication_reason=None,
        **kwargs,
    ):
        session_id = kwargs.get("session_id")
        remembered = (
            self._sessions.get(session_id or "")
            if session_id and hasattr(self, "_sessions")
            else None
        )
        remembered_cfg = (
            dict(remembered.get("coordination_config") or {})
            if isinstance(remembered, dict)
            else {}
        )
        prior_digest = (
            remembered.get("coordination_digest")
            if isinstance(remembered, dict)
            else None
        )
        call_override = getattr(
            self, "_agent_boot_message_board_call_override", None
        )
        if isinstance(call_override, dict):
            remembered_cfg.update(
                {k: v for k, v in call_override.items() if v is not None}
            )

        config = {
            "coordination_mode": (
                coordination_mode
                if coordination_mode is not None
                else remembered_cfg.get("coordination_mode", "AUTO")
            ),
            "work_key": (
                work_key if work_key is not None else remembered_cfg.get("work_key")
            ),
            "targets": (
                list(targets)
                if targets is not None
                else list(remembered_cfg.get("targets") or [])
            ),
            "coordination_details": (
                coordination_details
                if coordination_details is not None
                else remembered_cfg.get("coordination_details")
            ),
            "coordination_claim_mode": (
                coordination_claim_mode
                if coordination_claim_mode is not None
                else remembered_cfg.get("coordination_claim_mode")
            ),
            "lease_seconds": (
                lease_seconds
                if lease_seconds is not None
                else remembered_cfg.get("lease_seconds", 1800)
            ),
            "replication_reason": (
                replication_reason
                if replication_reason is not None
                else remembered_cfg.get("replication_reason")
            ),
        }
        self._agent_boot_message_board_override = config
        try:
            packet = original_refresh(self, *args, **kwargs)
        finally:
            self._agent_boot_message_board_override = None

        coordination = packet.get("coordination")
        if isinstance(coordination, dict):
            current_digest = coordination.get("routing_digest")
            refresh = packet.get("refresh")
            if isinstance(refresh, dict):
                changed = bool(
                    prior_digest is not None and current_digest != prior_digest
                )
                refresh["coordination_changed"] = changed
                refresh["coordination_prior_digest"] = prior_digest
                refresh["coordination_current_digest"] = current_digest
                affected = list(refresh.get("affected_dependency_cone") or [])
                if changed and "message_board_coordination" not in affected:
                    affected.append("message_board_coordination")
                refresh["affected_dependency_cone"] = affected
                refresh["requires_replan"] = bool(
                    refresh.get("requires_replan") or changed
                )
        return packet

    def call_tool_with_message_board(self, name: str, arguments: dict):
        if name in {"athena_agent_bootstrap", "athena_agent_refresh"}:
            args = dict(arguments or {})
            coordination = {
                key: args.pop(key)
                for key in list(args)
                if key in _COORDINATION_FIELDS
            }
            if name == "athena_agent_bootstrap":
                args.setdefault("task", "")
                return self.bootstrap(**args, **coordination)
            return self.refresh(**args, **coordination)
        return original_call_tool(self, name, arguments)

    runtime_cls.bootstrap = bootstrap_with_message_board
    runtime_cls.refresh = refresh_with_message_board
    runtime_cls.call_tool = call_tool_with_message_board
    runtime_cls._athena_boot_message_board_v1_registered = True

    for tool in AGENT_BOOT_TOOLS:
        props = (tool.get("inputSchema") or {}).setdefault("properties", {})
        props.setdefault(
            "coordination_mode",
            {
                "type": ["string", "null"],
                "enum": ["AUTO", "READ_ONLY", "DISABLED", None],
            },
        )
        props.setdefault("work_key", {"type": ["string", "null"]})
        props.setdefault(
            "targets", {"type": ["array", "null"], "items": {"type": "string"}}
        )
        props.setdefault("coordination_details", {"type": ["string", "null"]})
        props.setdefault(
            "coordination_claim_mode",
            {
                "type": ["string", "null"],
                "enum": ["PRIMARY", "REPLICA", None],
            },
        )
        props.setdefault(
            "lease_seconds",
            {
                "type": ["integer", "null"],
                "minimum": 60,
                "maximum": 86400,
            },
        )
        props.setdefault("replication_reason", {"type": ["string", "null"]})
        if tool.get("name") == "athena_agent_bootstrap":
            tool["description"] = (
                "Cold-start AGENT_BOOT_V1 through the shared-current Message Board "
                "pre-dispatch gate, then compose prompt/frontier/issue/sibling/"
                "continuation state. AUTO claims or reuses the lane; exact duplicate "
                "work holds instead of dispatching a second independent build."
            )
        elif tool.get("name") == "athena_agent_refresh":
            tool["description"] = (
                "Refresh AGENT_BOOT_V1 and its Message Board coordination projection; "
                "renew a matching lease only near expiry and report coordination "
                "changes without treating routine presence reuse as new work."
            )
