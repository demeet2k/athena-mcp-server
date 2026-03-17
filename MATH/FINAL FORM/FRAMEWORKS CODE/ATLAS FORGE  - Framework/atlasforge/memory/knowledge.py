"""Structured knowledge records for the AtlasForge memory bank.

Why this exists
---------------
A plain :class:`~atlasforge.memory.entry.MemoryEntry` is intentionally generic.
That is great for portability (JSON on disk), but over time a real math memory
bank benefits from *light structure*:

- Definitions / Lemmas / Theorems / Proofs
- Identities and operators (like ⊞)
- Derivations, computations, experiments

This module provides a small schema that compiles down to a normal
:class:`~atlasforge.memory.entry.MemoryEntry` so everything stays compatible
with the existing store, index, graph and replay/proof machinery.

Design principles
-----------------
- **Backward compatible**: a KnowledgeRecord is stored as a MemoryEntry.
- **Searchable**: kinds are stored both in ``extra['kind']`` and as a tag
  ``kind:<kind>``.
- **Linkable**: dependency fields can be projected into the GraphStore.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from atlasforge.memory.entry import MemoryEntry


class KnowledgeKind(str, Enum):
    """Coarse type of a knowledge item."""

    SEED = "seed"
    DEFINITION = "definition"
    LEMMA = "lemma"
    THEOREM = "theorem"
    COROLLARY = "corollary"
    PROPOSITION = "proposition"
    PROOF = "proof"
    IDENTITY = "identity"
    OPERATOR = "operator"
    DERIVATION = "derivation"
    COMPUTATION = "computation"
    EXAMPLE = "example"
    NOTE = "note"
    RECIPE_LOG = "recipe_log"
    OTHER = "other"


def _kind_tag(kind: Union[str, KnowledgeKind]) -> str:
    k = kind.value if isinstance(kind, KnowledgeKind) else str(kind)
    return f"kind:{k.strip().lower()}" if k else "kind:other"


def _normalize_address(address: Any) -> Tuple[Optional[str], Optional[int]]:
    """Normalize a crystal address into (string, linear_index).

    Delegates to :func:`atlasforge.memory.addressing.normalize_address` so that
    addressing rules are shared across the memory subsystem.
    """
    from atlasforge.memory.addressing import normalize_address as _normalize_address_shared

    return _normalize_address_shared(address)


@dataclass
class KnowledgeRecord:
    """A structured knowledge item that compiles to a :class:`MemoryEntry`."""

    kind: KnowledgeKind = KnowledgeKind.NOTE
    title: str = ""

    # Core math payload
    statement: str = ""  # definition/lemma/theorem/identity/operator signature
    proof: Optional[str] = None
    intuition: Optional[str] = None
    examples: List[str] = field(default_factory=list)

    # Connections
    depends_on: List[str] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    address: Optional[Any] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_entry(self) -> MemoryEntry:
        """Compile this record into a MemoryEntry."""

        kind_str = self.kind.value
        addr_str, addr_idx = _normalize_address(self.address)

        # Markdown body (human-facing). We keep it simple and stable.
        lines: List[str] = []
        if self.title:
            lines.append(f"# {self.title}")
            lines.append("")

        # A one-line kind header can help scanning.
        if kind_str and kind_str not in ("note", "other"):
            lines.append(f"**{kind_str.capitalize()}.**")
            lines.append("")

        if self.statement:
            lines.append(self.statement.strip())
            lines.append("")

        if self.proof:
            lines.append("## Proof")
            lines.append(self.proof.strip())
            lines.append("")

        if self.intuition:
            lines.append("## Intuition")
            lines.append(self.intuition.strip())
            lines.append("")

        if self.examples:
            lines.append("## Examples")
            for ex in self.examples:
                ex = str(ex).strip()
                if not ex:
                    continue
                # preserve markdown if the user already used bullets
                if ex.startswith("-") or ex.startswith("*"):
                    lines.append(ex)
                else:
                    lines.append(f"- {ex}")
            lines.append("")

        if self.sources:
            lines.append("## Sources")
            for s in self.sources:
                s = str(s).strip()
                if not s:
                    continue
                if s.startswith("-") or s.startswith("*"):
                    lines.append(s)
                else:
                    lines.append(f"- {s}")
            lines.append("")

        content = "\n".join(lines).rstrip() + "\n"

        # Tags: include a kind tag for easy filtering.
        tag_set = list(dict.fromkeys([t for t in (self.tags or []) if str(t).strip()]))
        tag_set.append(_kind_tag(self.kind))

        extra = dict(self.extra or {})
        extra.setdefault("schema", "knowledge")
        extra.setdefault("schema_version", 1)
        extra["kind"] = kind_str
        if self.statement:
            extra.setdefault("statement", self.statement)
        if self.proof:
            extra.setdefault("proof", self.proof)
        if self.intuition:
            extra.setdefault("intuition", self.intuition)
        if self.examples:
            extra.setdefault("examples", list(self.examples))
        if self.depends_on:
            extra.setdefault("depends_on", list(self.depends_on))
        if self.see_also:
            extra.setdefault("see_also", list(self.see_also))
        if self.sources:
            extra.setdefault("sources", list(self.sources))
        if addr_str is not None:
            extra.setdefault("crystal_address", addr_str)
        if addr_idx is not None:
            extra.setdefault("crystal_index", int(addr_idx))

        return MemoryEntry(
            title=self.title,
            content=content,
            tags=tag_set,
            links=dict(self.links or {}),
            extra=extra,
        )

    @classmethod
    def from_entry(cls, entry: MemoryEntry) -> "KnowledgeRecord":
        """Best-effort parse of a knowledge record from a MemoryEntry."""
        extra = dict(entry.extra or {})
        kind_raw = str(extra.get("kind") or "note").lower()
        try:
            kind = KnowledgeKind(kind_raw)
        except Exception:
            kind = KnowledgeKind.OTHER

        return cls(
            kind=kind,
            title=entry.title,
            statement=str(extra.get("statement") or ""),
            proof=extra.get("proof"),
            intuition=extra.get("intuition"),
            examples=list(extra.get("examples") or []),
            depends_on=list(extra.get("depends_on") or []),
            see_also=list(extra.get("see_also") or []),
            tags=list(entry.tags or []),
            links=dict(entry.links or {}),
            sources=list(extra.get("sources") or []),
            address=extra.get("crystal_address") or extra.get("address"),
            extra=extra,
        )
