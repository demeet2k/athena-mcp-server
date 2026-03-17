from __future__ import annotations

from ..contracts import stable_hash


TITLE = "Appendix L - Replay Validation Harness"
ACTIVE = True


def build_replay_signature(payload: dict[str, object]) -> str:
    return stable_hash(payload)


def describe_service(payload: dict[str, object] | None = None) -> dict[str, object]:
    payload = payload or {}
    return {
        "code": "L",
        "title": TITLE,
        "active": ACTIVE,
        "signature": build_replay_signature(payload),
    }
