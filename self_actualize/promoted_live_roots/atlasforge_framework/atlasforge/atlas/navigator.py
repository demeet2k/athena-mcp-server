"""Crystal navigation helpers.

A large memory bank benefits from a *structural* index, not just keyword search.
AtlasForge's 4×4×4×4 crystal (Pole·Lens·Layer·Depth) provides that.

This module provides a small helper class that:
- groups entries by crystal index
- allows lookup by index or by address string
- renders a compact Markdown navigator
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from atlasforge.memory.entry import MemoryEntry
from atlasforge.memory.store import MemoryStore
from atlasforge.memory.addressing import normalize_address


@dataclass
class CrystalCell:
    index: int
    address: str
    entries: List[MemoryEntry]


class CrystalNavigator:
    """Navigate memory entries by CrystalAddress (256-cell structure)."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def cell(self, address: Any) -> Optional[CrystalCell]:
        """Return a :class:`CrystalCell` for a given address (index/str/CrystalAddress)."""
        addr_str, idx = normalize_address(address)
        if idx is None:
            return None
        try:
            import atlasforge as af  # local import
            addr_str = addr_str or str(af.CrystalAddress.from_index(int(idx)))
        except Exception:
            addr_str = addr_str or str(idx)

        es = [e for e in self.store.iter_entries() if (e.extra or {}).get("crystal_index") == int(idx)]
        es.sort(key=lambda ee: ((ee.title or "").lower(), ee.content_hash()))
        return CrystalCell(index=int(idx), address=str(addr_str), entries=es)

    def map(self) -> Dict[int, List[MemoryEntry]]:
        """Return mapping index -> entries (non-empty cells only)."""
        out: Dict[int, List[MemoryEntry]] = {}
        for e in self.store.iter_entries():
            try:
                idx = (e.extra or {}).get("crystal_index")
                if idx is None:
                    continue
                ii = int(idx)
            except Exception:
                continue
            out.setdefault(ii, []).append(e)
        for ii in out:
            out[ii].sort(key=lambda ee: ((ee.title or "").lower(), ee.content_hash()))
        return out

    def render_markdown(self, *, include_empty: bool = False, max_entries_per_cell: int = 25) -> str:
        """Render a Markdown navigator.

        This is similar to the "Crystal map" section in the book builder, but
        can be used standalone.
        """
        mapping = self.map()
        try:
            import atlasforge as af  # local import
        except Exception:
            af = None  # type: ignore

        lines: List[str] = []
        lines.append("# Crystal Navigator")
        lines.append("")
        lines.append("Non-empty cells are listed below. Each cell is labeled by its linear index (0..255) and its decoded address.")
        lines.append("")

        indices = list(range(256)) if include_empty else sorted(mapping.keys())
        for idx in indices:
            es = mapping.get(idx, [])
            if (not es) and (not include_empty):
                continue
            addr = str(idx)
            if af is not None:
                try:
                    addr = str(af.CrystalAddress.from_index(int(idx)))
                except Exception:
                    addr = str(idx)
            lines.append(f"## Cell {idx}: {addr}")
            lines.append("")
            if not es:
                lines.append("*empty*")
                lines.append("")
                continue
            shown = es[:max_entries_per_cell]
            for e in shown:
                h = e.content_hash()
                t = e.title or h
                lines.append(f"- {t} (`{h[:10]}`)")
            if len(es) > max_entries_per_cell:
                lines.append(f"- … and {len(es) - max_entries_per_cell} more")
            lines.append("")

        return "\n".join(lines)
