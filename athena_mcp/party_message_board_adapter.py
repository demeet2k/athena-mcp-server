from __future__ import annotations

import json
from typing import Any, Iterable, Mapping, Sequence

VERSION = "PARTY.MESSAGE.BOARD.ADAPTER.1"
ENVELOPE_ARTIFACT = "ATHENA.PARTY.MESSAGE.BOARD.ENVELOPE.V1"

PARTY_KINDS = frozenset(
    {"CLAIM", "OFFER", "HANDOFF", "BLOCKER", "DECISION", "RESULT", "VERIFY"}
)
WITNESS_REQUIRED_KINDS = frozenset({"DECISION", "RESULT", "VERIFY"})
OUTER_MESSAGE_KIND = {
    "CLAIM": "INFO",
    "OFFER": "INFO",
    "HANDOFF": "HANDOFF",
    "BLOCKER": "BLOCKER",
    "DECISION": "INFO",
    "RESULT": "INFO",
    "VERIFY": "INFO",
}


def _text(value: Any, field: str) -> str:
    out = str(value or "").strip()
    if not out:
        raise ValueError(f"{field} must be non-empty")
    return out


def _names(values: Iterable[Any] | None) -> list[str]:
    return sorted({_text(value, "reference") for value in (values or [])})


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def build_envelope(
    *,
    party_id: str,
    cycle_id: str,
    channel: str,
    kind: str,
    body: str,
    goal_refs: Iterable[str] | None = None,
    claim_refs: Iterable[str] | None = None,
    witness_ref: str | None = None,
) -> str:
    """Build the canonical Party V2 envelope carried by Message Board V1.

    The envelope is metadata, not a second message record. Its durable source identity
    is the Message Board event that carries this JSON string.
    """

    kind = _text(kind, "kind").upper()
    if kind not in PARTY_KINDS:
        raise ValueError(f"kind must be one of {sorted(PARTY_KINDS)}")
    witness = str(witness_ref or "").strip() or None
    if kind in WITNESS_REQUIRED_KINDS and witness is None:
        raise ValueError(f"{kind}_WITNESS_REQUIRED")
    envelope = {
        "artifact": ENVELOPE_ARTIFACT,
        "version": VERSION,
        "party_id": _text(party_id, "party_id"),
        "cycle_id": _text(cycle_id, "cycle_id"),
        "channel": _text(channel, "channel"),
        "kind": kind,
        "body": _text(body, "body"),
        "goal_refs": _names(goal_refs),
        "claim_refs": _names(claim_refs),
        "witness_ref": witness,
        "laws": [
            "MESSAGE_BOARD_EVENT_IS_SOURCE_IDENTITY",
            "MESSAGE_ROUTE != CONSUMPTION",
            "COMMUNICATION != CONTENT_TRUTH",
            "PARTY_MESSAGE_XP = 0",
        ],
    }
    return _canonical(envelope)


def message_board_post_args(
    *,
    agent_id: str,
    recipients: Sequence[str],
    party_id: str,
    cycle_id: str,
    channel: str,
    kind: str,
    body: str,
    goal_refs: Iterable[str] | None = None,
    claim_refs: Iterable[str] | None = None,
    witness_ref: str | None = None,
    reply_to: str | None = None,
) -> dict[str, Any]:
    """Return exact args for the existing ``athena_message_board`` post action.

    Party broadcasts must enumerate party recipients instead of using the board's
    global empty-recipient broadcast. This keeps the party projection scoped.
    """

    author = _text(agent_id, "agent_id")
    recips = _names(recipients)
    if not recips:
        raise ValueError("party message requires at least one explicit recipient")
    if author in recips:
        raise ValueError("party message cannot target its author")
    inner_kind = _text(kind, "kind").upper()
    envelope = build_envelope(
        party_id=party_id,
        cycle_id=cycle_id,
        channel=channel,
        kind=inner_kind,
        body=body,
        goal_refs=goal_refs,
        claim_refs=claim_refs,
        witness_ref=witness_ref,
    )
    return {
        "action": "post",
        "agent_id": author,
        "message": envelope,
        "message_kind": OUTER_MESSAGE_KIND[inner_kind],
        "recipients": recips,
        "reply_to": str(reply_to or "").strip() or None,
    }


def _decode_envelope(event: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    if str(event.get("kind") or "") != "MESSAGE":
        return None, None
    payload = event.get("payload") or {}
    if not isinstance(payload, Mapping):
        return None, "MESSAGE_PAYLOAD_INVALID"
    raw = payload.get("message")
    if not isinstance(raw, str):
        return None, "MESSAGE_TEXT_INVALID"
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None, None
    if not isinstance(value, dict) or value.get("artifact") != ENVELOPE_ARTIFACT:
        return None, None
    return value, None


def _legacy_rows(
    *,
    event: Mapping[str, Any],
    envelope: Mapping[str, Any],
    recipients: list[str],
) -> list[dict[str, Any]]:
    """Project one board event into legacy PartyRuntime communication rows.

    One explicit recipient becomes one row. Multiple recipients are expanded only
    as a compatibility projection; every row keeps the same ``source_event_id`` so
    downstream code can avoid mistaking the expansion for independent messages.
    """

    event_id = _text(event.get("event_id"), "event_id")
    refs = sorted(
        set(envelope.get("goal_refs") or [])
        | set(envelope.get("claim_refs") or [])
        | ({str(envelope.get("witness_ref"))} if envelope.get("witness_ref") else set())
    )
    rows = []
    for target in recipients:
        rows.append(
            {
                "message_id": event_id if len(recipients) == 1 else f"{event_id}#{target}",
                "source_event_id": event_id,
                "channel": envelope["channel"],
                "author": event["agent_id"],
                "target": target,
                "kind": envelope["kind"],
                "body": envelope["body"],
                "refs": refs,
                "witness_ref": envelope.get("witness_ref"),
                "goal_refs": list(envelope.get("goal_refs") or []),
                "claim_refs": list(envelope.get("claim_refs") or []),
                "cycle_id": envelope["cycle_id"],
                "party_id": envelope["party_id"],
                "created_at": event.get("created_at"),
                "projection_only": True,
            }
        )
    return rows


def project_snapshot(
    snapshot: Mapping[str, Any],
    *,
    party_id: str,
    cycle_id: str,
    party_members: Iterable[str],
    party_channels: Iterable[str],
) -> dict[str, Any]:
    """Project Message Board V1 state into Party V2 communication evidence.

    Fail closed when the board did not verify the shared frontier. Only exact Party
    V2 envelopes from the requested party/cycle are considered. Unrelated board
    messages are ignored rather than treated as failures.
    """

    party_id = _text(party_id, "party_id")
    cycle_id = _text(cycle_id, "cycle_id")
    members = set(_names(party_members))
    channels = set(_names(party_channels))
    if len(members) < 2:
        raise ValueError("party projection requires at least two members")
    if not channels:
        raise ValueError("party projection requires at least one channel")

    if not bool(snapshot.get("shared_frontier_verified")):
        return {
            "version": VERSION,
            "status": "MESSAGE_BOARD_SHARED_FRONTIER_HOLD",
            "party_id": party_id,
            "cycle_id": cycle_id,
            "active_members": [],
            "messages": [],
            "ineligible": [],
            "laws": [
                "SHARED_COORDINATION_REQUIRES_VERIFIED_BOARD_FRONTIER",
                "NO_BOARD_WITNESS -> NO_PARTY_COMMUNICATION_CREDIT",
            ],
        }

    active_rows = {
        str(row.get("agent_id")): row
        for row in (snapshot.get("active") or [])
        if isinstance(row, Mapping)
        and str(row.get("agent_id") or "") in members
        and str(row.get("status") or "ACTIVE") == "ACTIVE"
        and str(row.get("claim_id") or "").strip()
    }
    active_claims = {
        agent: str(row.get("claim_id")) for agent, row in active_rows.items()
    }

    messages: list[dict[str, Any]] = []
    ineligible: list[dict[str, Any]] = []
    seen_source_ids: set[str] = set()

    for event in snapshot.get("recent_events") or []:
        if not isinstance(event, Mapping):
            continue
        envelope, decode_error = _decode_envelope(event)
        if decode_error:
            ineligible.append(
                {"source_event_id": event.get("event_id"), "reason": decode_error}
            )
            continue
        if envelope is None:
            continue
        if envelope.get("party_id") != party_id or envelope.get("cycle_id") != cycle_id:
            continue

        event_id = str(event.get("event_id") or "")
        author = str(event.get("agent_id") or "")
        payload = event.get("payload") or {}
        recipients = sorted({str(x) for x in (event.get("recipients") or []) if str(x)})
        reason = None

        if not event_id:
            reason = "SOURCE_EVENT_ID_MISSING"
        elif event_id in seen_source_ids:
            reason = "SOURCE_EVENT_REPLAY"
        elif author not in members:
            reason = "AUTHOR_NOT_PARTY_MEMBER"
        elif author not in active_claims:
            reason = "AUTHOR_NOT_ACTIVE_ON_MESSAGE_BOARD"
        elif not recipients:
            reason = "GLOBAL_BOARD_BROADCAST_NOT_PARTY_SCOPED"
        elif author in recipients:
            reason = "SELF_TARGETED_PARTY_MESSAGE"
        elif not set(recipients).issubset(members):
            reason = "RECIPIENT_OUTSIDE_PARTY"
        elif envelope.get("channel") not in channels:
            reason = "PARTY_CHANNEL_MISMATCH"
        elif envelope.get("kind") not in PARTY_KINDS:
            reason = "PARTY_KIND_INVALID"
        elif envelope.get("kind") in WITNESS_REQUIRED_KINDS and not str(
            envelope.get("witness_ref") or ""
        ).strip():
            reason = f"{envelope.get('kind')}_WITNESS_REQUIRED"
        elif str(payload.get("claim_id") or "") != active_claims[author]:
            reason = "MESSAGE_CLAIM_NOT_CURRENT"
        elif str(payload.get("message_kind") or "").upper() != OUTER_MESSAGE_KIND[
            str(envelope.get("kind"))
        ]:
            reason = "OUTER_MESSAGE_KIND_MISMATCH"

        if reason:
            ineligible.append({"source_event_id": event_id or None, "reason": reason})
            continue

        seen_source_ids.add(event_id)
        messages.extend(_legacy_rows(event=event, envelope=envelope, recipients=recipients))

    return {
        "version": VERSION,
        "status": "OK",
        "party_id": party_id,
        "cycle_id": cycle_id,
        "board_git_head": snapshot.get("git_head"),
        "shared_frontier_verified": True,
        "active_members": sorted(active_rows),
        "active_claims": dict(sorted(active_claims.items())),
        "messages": messages,
        "source_event_count": len(seen_source_ids),
        "ineligible": ineligible,
        "laws": [
            "MESSAGE_BOARD_V1_IS_COMMUNICATION_SOURCE_AUTHORITY",
            "PARTY_PROJECTION_IS_NOT_SECOND_MUTABLE_MESSAGE_STORE",
            "MESSAGE_ROUTE != CONSUMPTION",
            "COMMUNICATION != CONTENT_TRUTH",
            "PROJECTION_EXPANSION != INDEPENDENT_MESSAGE_COUNT",
            "PARTY_MESSAGE_XP = 0",
        ],
    }
