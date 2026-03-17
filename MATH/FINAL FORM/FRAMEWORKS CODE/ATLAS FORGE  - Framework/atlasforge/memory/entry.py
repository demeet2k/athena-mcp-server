"""Memory entries for AtlasForge.

A :class:`~atlasforge.memory.entry.MemoryEntry` is a small, content-addressed
chunk of knowledge (typically Markdown). Entries can link to AtlasForge
artifacts (blueprints, recipes, proof packs) by hash.

Design goals
------------
- **Simple**: JSON on disk, no external dependencies.
- **Content-addressed**: identical content → identical hash.
- **Linkable**: store hashes of recipes/proofs so you can jump to provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json

from atlasforge.core.base import ContentAddressed


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryEntry(ContentAddressed):
    """A single memory-bank entry.

    Parameters
    ----------
    title:
        Short human-friendly label.
    content:
        Body text (Markdown recommended).
    tags:
        Free-form tags, e.g. ["root-finding", "interval", "lemma"].
    links:
        String→string map for related AtlasForge artifacts, e.g.
        {"recipe": "<hash>", "blueprint": "<hash>"}.
    extra:
        Arbitrary JSON-serializable metadata.
    """

    title: str = ""
    content: str = ""
    tags: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: Optional[str] = None

    def canonical_repr(self) -> str:
        # canonical, deterministic JSON for hashing
        return json.dumps(
            {
                "title": self.title,
                "content": self.content,
                "tags": sorted(self.tags),
                "links": dict(sorted(self.links.items())),
                "extra": self.extra,
            },
            sort_keys=True,
            ensure_ascii=False,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "tags": list(self.tags),
            "links": dict(self.links),
            "extra": self.extra,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "content_hash": self.content_hash(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            tags=list(data.get("tags", []) or []),
            links=dict(data.get("links", {}) or {}),
            extra=dict(data.get("extra", {}) or {}),
            created_at=data.get("created_at", _utc_now_iso()),
            updated_at=data.get("updated_at"),
        )

    def touch(self):
        """Update the updated_at timestamp (does not mutate hash-critical fields)."""
        self.updated_at = _utc_now_iso()
