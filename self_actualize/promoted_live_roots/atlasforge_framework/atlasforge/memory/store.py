"""Filesystem-backed memory store.

The :class:`~atlasforge.memory.store.MemoryStore` persists :class:`~atlasforge
.memory.entry.MemoryEntry` objects to a directory.

Storage layout
--------------
<root>/
  entries/
    <hash>.json

Search remains portable (JSON files on disk), but AtlasForge also provides an
**optional** SQLite index for fast full-text search and ranking.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import json
import os

from atlasforge.memory.entry import MemoryEntry
from atlasforge.memory.knowledge import KnowledgeKind, KnowledgeRecord
from atlasforge.memory.index import MemoryIndex
from atlasforge.memory.graph import GraphStore
from atlasforge.memory.session import SessionRecord, SessionStore
from atlasforge.memory.bootstrap import builtin_seed_entries


class MemoryStore:
    """A tiny persistent knowledge base for AtlasForge.

    Parameters
    ----------
    root:
        Directory where entries are stored.
    """

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).expanduser().resolve()
        self.entries_dir = self.root / "entries"
        self.entries_dir.mkdir(parents=True, exist_ok=True)

        # Optional SQLite index (FTS5 when available)
        self.index: Optional[MemoryIndex] = None
        try:
            self.index = MemoryIndex(self.root)
            # If the index is new / empty, rebuild once.
            # We use a cheap heuristic: if the table has 0 rows, rebuild.
            cur = self.index._conn.cursor()  # type: ignore[attr-defined]
            cur.execute("SELECT COUNT(1) AS n FROM entries")
            n = int(cur.fetchone()[0])
            if n == 0 and any(self.entries_dir.glob("*.json")):
                self.index.rebuild_from_entries_dir(self.entries_dir)
        except Exception:
            self.index = None

        # Knowledge graph + sessions (both file-backed)
        self.graph = GraphStore(self.root)
        self.sessions = SessionStore(self.root)
        self._active_session: Optional[SessionRecord] = None

        # Bootstrap a fresh memory directory with a few structural seeds.
        # Users can disable this by setting ATLASFORGE_NO_BOOTSTRAP=1.
        try:
            if not os.environ.get("ATLASFORGE_NO_BOOTSTRAP"):
                if not any(self.entries_dir.glob("*.json")):
                    self.bootstrap()
        except Exception:
            pass

    # ---------------------------------------------------------------------
    # Address helpers
    # ---------------------------------------------------------------------

    def _normalize_address(self, address: Any) -> Tuple[Optional[str], Optional[int]]:
        """Normalize an address into (string, index).

        Delegates to :func:`atlasforge.memory.addressing.normalize_address`.
        """
        from atlasforge.memory.addressing import normalize_address

        return normalize_address(address)

    def add(self, entry: MemoryEntry, overwrite: bool = False) -> str:
        """Persist an entry and return its content hash."""
        h = entry.content_hash()
        path = self.entries_dir / f"{h}.json"

        # Write JSON if new or overwrite requested, but always update derived structures
        # (index / graph / sessions) even when the entry already exists.
        if (not path.exists()) or overwrite:
            path.write_text(entry.to_json(indent=2), encoding="utf-8")

        # Index update
        if self.index is not None:
            try:
                self.index.upsert(
                    entry_hash=h,
                    title=entry.title,
                    content=entry.content,
                    tags=entry.tags,
                    links=entry.links,
                    extra=entry.extra,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at,
                )
            except Exception:
                pass

        # Graph projections (best-effort): depends_on / see_also and explicit links.
        try:
            extra = entry.extra or {}
            for dep in (extra.get("depends_on") or []):
                dep = str(dep).strip()
                if dep:
                    self.graph.link(src=h, dst=dep, relation="depends_on")
            for other in (extra.get("see_also") or []):
                other = str(other).strip()
                if other:
                    self.graph.link(src=h, dst=other, relation="see_also")
            for k, v in (entry.links or {}).items():
                v = str(v).strip()
                if v:
                    self.graph.link(src=h, dst=v, relation=f"link:{k}")
        except Exception:
            pass

        # Session bookkeeping
        if self._active_session is not None:
            self._active_session.add_entry(h)
        return h

    def get(self, entry_hash: str) -> Optional[MemoryEntry]:
        """Load an entry by hash."""
        path = self.entries_dir / f"{entry_hash}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return MemoryEntry.from_dict(data)
        except Exception:
            return None

    def delete(self, entry_hash: str) -> bool:
        """Delete an entry file."""
        path = self.entries_dir / f"{entry_hash}.json"
        try:
            path.unlink()
            if self.index is not None:
                try:
                    self.index.delete(entry_hash)
                except Exception:
                    pass
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def list_hashes(self) -> List[str]:
        """List all entry hashes."""
        out = []
        for p in self.entries_dir.glob("*.json"):
            out.append(p.stem)
        out.sort()
        return out

    def iter_entries(self) -> Iterable[MemoryEntry]:
        """Yield all entries (order by filename/hash)."""
        for h in self.list_hashes():
            e = self.get(h)
            if e is not None:
                yield e

    # ---------------------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------------------

    def search(
        self,
        query: str = "",
        tags: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        kinds: Optional[Sequence[Any]] = None,
        kind: Optional[Any] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """Search entries by query + optional tag / address filters.

        - `query` is matched (case-insensitive) in title + content.
        - `tags` requires that all provided tags are present (case-insensitive).
        """
        q = (query or "").strip()
        req_tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        addr_str, addr_idx = self._normalize_address(address)

        # Kind filtering (OR across kinds).
        # Kinds are stored in entry.extra['kind'] (and usually as a tag 'kind:<kind>').
        allowed_kinds_raw = []
        if kind is not None:
            allowed_kinds_raw.append(kind)
        if kinds:
            allowed_kinds_raw.extend(list(kinds))

        allowed_kinds = set()
        for k in allowed_kinds_raw:
            if k is None:
                continue
            if isinstance(k, KnowledgeKind):
                ks = k.value
            else:
                ks = str(k)
            ks = (ks or '').strip().lower()
            if ks:
                allowed_kinds.add(ks)

        # Prefer indexed search.
        if self.index is not None:
            try:
                hits: List[MemoryEntry] = []
                idx_hits = self.index.search(
                    query=q,
                    tags=req_tags,
                    crystal_index=addr_idx,
                    limit=limit,
                )
                for h in idx_hits:
                    e = self.get(h.entry_hash)
                    if e is None:
                        continue
                    # If user passed a string address, enforce match as substring.
                    if addr_str is not None and addr_idx is None:
                        s = str(e.extra.get("crystal_address") or e.extra.get("address") or "")
                        if addr_str not in s:
                            continue

                    # Kind filter
                    if allowed_kinds:
                        e_kind = str(e.extra.get("kind") or "note").strip().lower()
                        if e_kind not in allowed_kinds:
                            continue

                    hits.append(e)
                    if len(hits) >= limit:
                        break
                return hits
            except Exception:
                # Fall back to scan
                pass

        # Portable scan fallback.
        q_low = q.lower()
        hits: List[MemoryEntry] = []
        for entry in self.iter_entries():
            if req_tags:
                entry_tags = {t.lower() for t in entry.tags}
                if any(t not in entry_tags for t in req_tags):
                    continue

            if addr_str is not None or addr_idx is not None:
                e_idx = entry.extra.get("crystal_index")
                e_addr = entry.extra.get("crystal_address") or entry.extra.get("address")
                if addr_idx is not None and e_idx != addr_idx:
                    continue
                if addr_str is not None and addr_idx is None:
                    if not e_addr or addr_str not in str(e_addr):
                        continue

            if q_low:
                hay = f"{entry.title}\n{entry.content}".lower()
                if q_low not in hay:
                    continue

            # Kind filter
            if allowed_kinds:
                e_kind = str(entry.extra.get("kind") or "note").strip().lower()
                if e_kind not in allowed_kinds:
                    continue

            hits.append(entry)
            if len(hits) >= limit:
                break

        return hits

    # ---------------------------------------------------------------------
    # CONVENIENCE
    # ---------------------------------------------------------------------

    def remember(
        self,
        title: str,
        content: str,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, Any]] = None,
        address: Optional[Any] = None,
    ) -> str:
        """Create + store a simple MemoryEntry."""
        extra_dict = dict(extra or {})

        # Default kind: treat plain remember() calls as notes.
        kind_val = extra_dict.get("kind") or "note"
        extra_dict.setdefault("kind", kind_val)

        # Crystal address normalization
        addr_str, addr_idx = self._normalize_address(address)
        if addr_str is not None:
            extra_dict.setdefault("crystal_address", addr_str)
        if addr_idx is not None:
            extra_dict.setdefault("crystal_index", int(addr_idx))

        # Tags: add a kind tag for easier filtering.
        tags_list = list(tags or [])
        kind_tag = f"kind:{str(kind_val).strip().lower()}" if kind_val else "kind:note"
        if kind_tag.lower() not in {t.lower() for t in tags_list}:
            tags_list.append(kind_tag)

        entry = MemoryEntry(
            title=title,
            content=content,
            tags=tags_list,
            links=dict(links or {}),
            extra=extra_dict,
        )
        return self.add(entry)


    # ---------------------------------------------------------------------
    # KNOWLEDGE SCHEMA CONVENIENCE
    # ---------------------------------------------------------------------

    def add_knowledge(self, record: KnowledgeRecord, overwrite: bool = False) -> str:
        """Store a structured :class:`~atlasforge.memory.knowledge.KnowledgeRecord`.

        The record compiles down to a standard :class:`~atlasforge.memory.entry.MemoryEntry`.
        """
        entry = record.to_entry()
        h = self.add(entry, overwrite=overwrite)
        return h

    # Common wrappers (sugar)

    def define(
        self,
        title: str,
        statement: str,
        *,
        proof: str | None = None,
        intuition: str | None = None,
        examples: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.DEFINITION,
                title=title,
                statement=statement,
                proof=proof,
                intuition=intuition,
                examples=list(examples or []),
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    def lemma(
        self,
        title: str,
        statement: str,
        *,
        proof: str | None = None,
        intuition: str | None = None,
        examples: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.LEMMA,
                title=title,
                statement=statement,
                proof=proof,
                intuition=intuition,
                examples=list(examples or []),
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    def theorem(
        self,
        title: str,
        statement: str,
        *,
        proof: str | None = None,
        intuition: str | None = None,
        examples: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.THEOREM,
                title=title,
                statement=statement,
                proof=proof,
                intuition=intuition,
                examples=list(examples or []),
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    def identity(
        self,
        title: str,
        statement: str,
        *,
        proof: str | None = None,
        intuition: str | None = None,
        examples: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.IDENTITY,
                title=title,
                statement=statement,
                proof=proof,
                intuition=intuition,
                examples=list(examples or []),
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    def operator(
        self,
        title: str,
        statement: str,
        *,
        proof: str | None = None,
        intuition: str | None = None,
        examples: Optional[Sequence[str]] = None,
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.OPERATOR,
                title=title,
                statement=statement,
                proof=proof,
                intuition=intuition,
                examples=list(examples or []),
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    def proof_entry(
        self,
        title: str,
        proof: str,
        *,
        statement: str = "",
        tags: Optional[Sequence[str]] = None,
        links: Optional[Dict[str, str]] = None,
        depends_on: Optional[Sequence[str]] = None,
        see_also: Optional[Sequence[str]] = None,
        sources: Optional[Sequence[str]] = None,
        address: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.add_knowledge(
            KnowledgeRecord(
                kind=KnowledgeKind.PROOF,
                title=title,
                statement=statement,
                proof=proof,
                tags=list(tags or []),
                links=dict(links or {}),
                depends_on=list(depends_on or []),
                see_also=list(see_also or []),
                sources=list(sources or []),
                address=address,
                extra=dict(extra or {}),
            )
        )

    # ---------------------------------------------------------------------
    # Bootstrap
    # ---------------------------------------------------------------------

    def bootstrap(self, overwrite: bool = False) -> List[str]:
        """Populate the store with a small built-in seed set.

        Returns a list of hashes for the added seed entries.
        """
        hashes: List[str] = []
        for e in builtin_seed_entries():
            h = self.add(e, overwrite=overwrite)
            hashes.append(h)
        return hashes

    def rebuild_index(self) -> int:
        """Force a full rebuild of the SQLite index from JSON files."""
        if self.index is None:
            return 0
        return self.index.rebuild_from_entries_dir(self.entries_dir)

    # ---------------------------------------------------------------------
    # Graph utilities
    # ---------------------------------------------------------------------

    def link(self, src: str, dst: str, relation: str, note: str = "", meta: Optional[Dict[str, Any]] = None) -> str:
        """Link two hashes (entries or artifacts) in the knowledge graph."""
        return self.graph.link(src=src, dst=dst, relation=relation, note=note, meta=meta)

    # ---------------------------------------------------------------------
    # Sessions
    # ---------------------------------------------------------------------

    def start_session(
        self,
        name: str,
        description: str = "",
        tags: Optional[Sequence[str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> SessionRecord:
        """Start an in-memory session (call :meth:`end_session` to persist)."""
        self._active_session = SessionRecord(
            name=name,
            description=description,
            tags=list(tags or []),
            extra=dict(extra or {}),
        )
        return self._active_session

    def end_session(self) -> Optional[str]:
        """Persist and close the active session (if any)."""
        if self._active_session is None:
            return None
        self._active_session.close()
        sid = self.sessions.save(self._active_session)
        self._active_session = None
        return sid

    @contextmanager
    def session(
        self,
        name: str,
        description: str = "",
        tags: Optional[Sequence[str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        """Context manager to capture a session of work."""
        self.start_session(name=name, description=description, tags=tags, extra=extra)
        try:
            yield self._active_session
        finally:
            self.end_session()

    def log_recipe(
        self,
        recipe: "Any",  # avoid import cycle; expected to be atlasforge.recipes.recipe.Recipe
        title: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
    ) -> str:
        """Store a compact record of a recipe run.

        This is designed for the workflow "use AtlasForge to do math; store the
        result + provenance in the memory bank".
        """
        try:
            blueprint = recipe.blueprint
            plan = recipe.plan
            output = recipe.output
        except Exception:
            blueprint = None
            plan = None
            output = None

        bp_hash = blueprint.content_hash() if blueprint else ""
        recipe_hash = recipe.content_hash() if hasattr(recipe, "content_hash") else ""
        out_hash = output.content_hash() if output else ""

        title = title or (getattr(blueprint, "name", "") or "Recipe")
        base_tags = list(tags or [])
        if blueprint is not None:
            base_tags.append(f"profile:{getattr(blueprint.truth_profile, 'value', blueprint.truth_profile)}")
        if plan is not None:
            base_tags.append(f"solver:{getattr(plan.primary_solver, 'value', plan.primary_solver)}")

        content_lines = []
        content_lines.append(f"# {title}")
        if blueprint is not None and getattr(blueprint, "description", ""):
            content_lines.append(blueprint.description)
        content_lines.append("")

        if output is not None:
            content_lines.append("## Result")
            content_lines.append(f"- success: {getattr(output, 'success', False)}")
            content_lines.append(f"- verified: {getattr(output, 'verified', False)}")
            content_lines.append(f"- solution: {getattr(output, 'solution', None)}")
            content_lines.append(f"- residual: {getattr(output, 'residual', None)}")
            if getattr(output, "enclosure", None) is not None:
                content_lines.append(f"- enclosure: {output.enclosure}")
            content_lines.append("")

        links = {
            "blueprint": bp_hash,
            "recipe": recipe_hash,
            "output": out_hash,
        }

        extra = {
            "kind": "recipe_log",
            "blueprint_name": getattr(blueprint, "name", "") if blueprint else "",
            "truth_profile": getattr(blueprint.truth_profile, "value", None) if blueprint else None,
            "blueprint_hash": bp_hash,
            "recipe_hash": recipe_hash,
            "output_hash": out_hash,
            "success": getattr(output, "success", None) if output else None,
            "verified": getattr(output, "verified", None) if output else None,
            "solution": getattr(output, "solution", None) if output else None,
            "residual": getattr(output, "residual", None) if output else None,
        }

        entry_hash = self.remember(
            title=title,
            content="\n".join(content_lines).strip() + "\n",
            tags=base_tags,
            links=links,
            extra=extra,
        )

        # Add a provenance edge: memory-entry -> recipe
        try:
            if recipe_hash:
                self.link(entry_hash, recipe_hash, relation="records")
            if bp_hash:
                self.link(entry_hash, bp_hash, relation="records")
            if out_hash:
                self.link(entry_hash, out_hash, relation="records")
        except Exception:
            pass

        # Session bookkeeping
        if self._active_session is not None:
            self._active_session.add_entry(entry_hash)
            self._active_session.add_recipe(recipe_hash)

        return entry_hash


    # ------------------------------------------------------------------
    # Graph closure / dependency utilities
    # ------------------------------------------------------------------

    def closure(
        self,
        roots: Sequence[str],
        *,
        relations: Optional[Sequence[str]] = None,
        direction: str = "out",
        max_depth: int = 32,
        limit: int = 5000,
    ) -> List[str]:
        """Return the graph closure starting from ``roots``.

        This is the core mechanism behind "export this theorem + everything it
        depends on".
        """
        return self.graph.closure(
            roots,
            relations=relations,
            direction=direction,
            max_depth=max_depth,
            limit=limit,
        )

    def dependency_closure(
        self,
        roots: Sequence[str],
        *,
        max_depth: int = 32,
        limit: int = 5000,
    ) -> List[str]:
        """Convenience: closure following only ``depends_on`` edges (outgoing)."""
        return self.closure(
            roots,
            relations=["depends_on"],
            direction="out",
            max_depth=max_depth,
            limit=limit,
        )
