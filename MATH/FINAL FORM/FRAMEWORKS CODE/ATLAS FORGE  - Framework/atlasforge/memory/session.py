"""Session capture for AtlasForge memory.

If AtlasForge is used as a *math memory bank*, you often want to group related
work:

* a sequence of recipes
* accompanying notes/lemmas
* the final synthesis summary

This module implements a small file-backed `SessionRecord` and a
`SessionStore` that can manage many sessions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import json
import os
import uuid


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SessionRecord:
    """A recorded session of work in the memory bank."""

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    started_at: str = field(default_factory=_utc_now_iso)
    ended_at: Optional[str] = None

    # The session is primarily a provenance index.
    entry_hashes: List[str] = field(default_factory=list)
    recipe_hashes: List[str] = field(default_factory=list)

    extra: Dict[str, Any] = field(default_factory=dict)

    def close(self):
        if self.ended_at is None:
            self.ended_at = _utc_now_iso()

    def add_entry(self, entry_hash: str):
        if entry_hash and entry_hash not in self.entry_hashes:
            self.entry_hashes.append(entry_hash)

    def add_recipe(self, recipe_hash: str):
        if recipe_hash and recipe_hash not in self.recipe_hashes:
            self.recipe_hashes.append(recipe_hash)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "entry_hashes": list(self.entry_hashes),
            "recipe_hashes": list(self.recipe_hashes),
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SessionRecord":
        return cls(
            session_id=d.get("session_id", uuid.uuid4().hex),
            name=d.get("name", "") or "",
            description=d.get("description", "") or "",
            tags=list(d.get("tags", []) or []),
            started_at=d.get("started_at", _utc_now_iso()),
            ended_at=d.get("ended_at"),
            entry_hashes=list(d.get("entry_hashes", []) or []),
            recipe_hashes=list(d.get("recipe_hashes", []) or []),
            extra=dict(d.get("extra", {}) or {}),
        )


class SessionStore:
    """File-backed storage for `SessionRecord`s."""

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).expanduser().resolve()
        self.sessions_dir = self.root / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def save(self, session: SessionRecord) -> str:
        p = self.path_for(session.session_id)
        p.write_text(json.dumps(session.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return session.session_id

    def get(self, session_id: str) -> Optional[SessionRecord]:
        p = self.path_for(session_id)
        if not p.exists():
            return None
        try:
            return SessionRecord.from_dict(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            return None

    def list_sessions(self) -> List[str]:
        out = [p.stem for p in self.sessions_dir.glob("*.json")]
        out.sort()
        return out

    def iter_sessions(self) -> List[SessionRecord]:
        out: List[SessionRecord] = []
        for sid in self.list_sessions():
            s = self.get(sid)
            if s is not None:
                out.append(s)
        return out
