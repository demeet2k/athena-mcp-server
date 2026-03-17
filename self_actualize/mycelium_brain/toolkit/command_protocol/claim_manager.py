from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from .ledger_writer import append_jsonl, claim_ledger_path, read_jsonl


def _latest_claims() -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(claim_ledger_path()):
        latest[row["event_id"]] = row
    return latest


def claim_event(event_id: str, claimer_id: str, role_class: str, lease_ms: int = 1200) -> dict[str, Any]:
    latest = _latest_claims().get(event_id)
    now = datetime.now(tz=UTC)
    if latest:
        expires_at = datetime.fromisoformat(latest["expires_at"])
        if latest["status"] == "claimed" and expires_at > now:
            receipt = {
                "event_id": event_id,
                "claimer_id": claimer_id,
                "role_class": role_class,
                "lease_ms": lease_ms,
                "claimed_at": now.isoformat(),
                "expires_at": (now + timedelta(milliseconds=lease_ms)).isoformat(),
                "status": "deferred",
                "blocked_by": latest["claimer_id"],
            }
            append_jsonl(claim_ledger_path(), receipt)
            return receipt
    receipt = {
        "event_id": event_id,
        "claimer_id": claimer_id,
        "role_class": role_class,
        "lease_ms": lease_ms,
        "claimed_at": now.isoformat(),
        "expires_at": (now + timedelta(milliseconds=lease_ms)).isoformat(),
        "status": "claimed",
    }
    append_jsonl(claim_ledger_path(), receipt)
    return receipt
