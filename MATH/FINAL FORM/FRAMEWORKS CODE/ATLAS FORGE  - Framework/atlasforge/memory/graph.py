"""A tiny knowledge graph for the AtlasForge memory bank.

AtlasForge entries are most powerful when they are *linked*:

* a lemma depends on prior definitions
* a computational recipe supports a conjecture
* one entry refines or generalizes another

This module provides a minimal, file-backed graph with content-addressed edges.
It intentionally stays lightweight: JSON on disk, no dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
import hashlib
import json
import os


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _edge_hash(src: str, dst: str, relation: str, note: str, meta: Dict[str, Any]) -> str:
    payload = {
        "src": src,
        "dst": dst,
        "relation": relation,
        "note": note,
        "meta": meta or {},
    }
    b = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


@dataclass
class GraphEdge:
    """A directed labeled edge in the knowledge graph."""

    src: str
    dst: str
    relation: str
    note: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now_iso)

    def edge_id(self) -> str:
        return _edge_hash(self.src, self.dst, self.relation, self.note, self.meta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.edge_id(),
            "src": self.src,
            "dst": self.dst,
            "relation": self.relation,
            "note": self.note,
            "meta": self.meta,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GraphEdge":
        return cls(
            src=d.get("src", ""),
            dst=d.get("dst", ""),
            relation=d.get("relation", ""),
            note=d.get("note", "") or "",
            meta=dict(d.get("meta", {}) or {}),
            created_at=d.get("created_at", _utc_now_iso()),
        )


class GraphStore:
    """File-backed store for graph edges."""

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).expanduser().resolve()
        self.path = self.root / "graph.json"
        self._edges: Dict[str, GraphEdge] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._edges = {}
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            edges = data.get("edges", []) if isinstance(data, dict) else []
            out: Dict[str, GraphEdge] = {}
            for e in edges:
                try:
                    edge = GraphEdge.from_dict(e)
                    out[edge.edge_id()] = edge
                except Exception:
                    continue
            self._edges = out
        except Exception:
            self._edges = {}

    def _save(self) -> None:
        payload = {
            "version": 1,
            "edges": [e.to_dict() for e in self._edges.values()],
        }
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def link(
        self,
        src: str,
        dst: str,
        relation: str,
        note: str = "",
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create (or deduplicate) an edge and return its ID."""
        edge = GraphEdge(src=src, dst=dst, relation=relation, note=note, meta=dict(meta or {}))
        eid = edge.edge_id()
        if eid not in self._edges:
            self._edges[eid] = edge
            self._save()
        return eid

    def unlink(self, edge_id: str) -> bool:
        if edge_id in self._edges:
            del self._edges[edge_id]
            self._save()
            return True
        return False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def edges(
        self,
        src: Optional[str] = None,
        dst: Optional[str] = None,
        relation: Optional[str] = None,
        limit: int = 200,
    ) -> List[GraphEdge]:
        out: List[GraphEdge] = []
        for e in self._edges.values():
            if src is not None and e.src != src:
                continue
            if dst is not None and e.dst != dst:
                continue
            if relation is not None and e.relation != relation:
                continue
            out.append(e)
            if len(out) >= limit:
                break
        return out

    def neighbors(self, node: str, relation: Optional[str] = None, limit: int = 200) -> List[str]:
        """Return dst nodes reachable from node."""
        return [e.dst for e in self.edges(src=node, relation=relation, limit=limit)]


    def closure(
        self,
        roots: Sequence[str],
        *,
        relations: Optional[Sequence[str]] = None,
        direction: str = "out",
        max_depth: int = 32,
        limit: int = 5000,
    ) -> List[str]:
        """Compute a graph closure from ``roots``.

        Parameters
        ----------
        relations:
            If provided, only follow edges whose relation is in this list.
        direction:
            "out" (follow src→dst), "in" (follow dst→src), or "both".
        max_depth:
            Maximum BFS depth.
        limit:
            Maximum number of nodes returned.

        Returns
        -------
        List[str]
            Node hashes in BFS discovery order (includes roots).
        """
        relset = None
        if relations is not None:
            relset = {str(r) for r in relations if str(r)}

        direction = (direction or "out").strip().lower()
        if direction not in ("out", "in", "both"):
            direction = "out"

        visited = set()
        order: List[str] = []
        frontier: List[tuple[str, int]] = []

        for r in roots or []:
            rr = str(r).strip()
            if not rr:
                continue
            if rr not in visited:
                visited.add(rr)
                order.append(rr)
                frontier.append((rr, 0))
            if len(order) >= limit:
                return order

        # Pre-index edges for efficiency.
        out_map: Dict[str, List[GraphEdge]] = {}
        in_map: Dict[str, List[GraphEdge]] = {}
        for e in self._edges.values():
            if relset is not None and e.relation not in relset:
                continue
            out_map.setdefault(e.src, []).append(e)
            in_map.setdefault(e.dst, []).append(e)

        # BFS
        i = 0
        while i < len(frontier):
            node, depth = frontier[i]
            i += 1
            if depth >= max_depth:
                continue

            neighbors: List[str] = []
            if direction in ("out", "both"):
                neighbors.extend([e.dst for e in out_map.get(node, [])])
            if direction in ("in", "both"):
                neighbors.extend([e.src for e in in_map.get(node, [])])

            for nb in neighbors:
                if nb not in visited:
                    visited.add(nb)
                    order.append(nb)
                    frontier.append((nb, depth + 1))
                    if len(order) >= limit:
                        return order
        return order
