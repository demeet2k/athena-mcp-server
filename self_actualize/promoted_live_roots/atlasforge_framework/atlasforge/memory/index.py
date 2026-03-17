"""SQLite-backed index for the AtlasForge memory bank.

The base :class:`~atlasforge.memory.store.MemoryStore` persists entries as JSON
files. That's portable and easy to version-control, but linear scanning gets
slow once the bank grows.

This module adds an **optional** SQLite index (no external dependencies):

* Full-text search (FTS5 when available)
* Ranked results
* Filters by tags and (optionally) crystal address

If SQLite FTS5 isn't available in the current Python build, the index will fall
back to a plain table + `LIKE` queries, and the `MemoryStore` will still work.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import json
import os
import sqlite3


def _norm_tag(tag: str) -> str:
    return (tag or "").strip().lower()


def _tags_to_text(tags: Sequence[str]) -> str:
    # Space-separated tags for FTS.
    return " ".join(sorted({_norm_tag(t) for t in tags if _norm_tag(t)}))


def _fts_query(q: str) -> str:
    """Convert a user query into an FTS MATCH expression.

    We use a very small transformation:
    - split on whitespace
    - append '*' for prefix matching
    """
    parts = [p.strip() for p in (q or "").split() if p.strip()]
    if not parts:
        return ""
    return " ".join(f"{p}*" for p in parts)


@dataclass
class MemoryIndexHit:
    """A ranked search hit returned by the index."""

    entry_hash: str
    score: float


class MemoryIndex:
    """SQLite-backed index for MemoryEntry JSON files."""

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root).expanduser().resolve()
        self.db_path = self.root / "index.sqlite"
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row

        self._fts_enabled = False
        self._init_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
              entry_hash TEXT PRIMARY KEY,
              title      TEXT,
              content    TEXT,
              tags_json  TEXT,
              tags_text  TEXT,
              links_json TEXT,
              extra_json TEXT,
              created_at TEXT,
              updated_at TEXT,
              crystal_address TEXT,
              crystal_index INTEGER
            )
            """
        )

        # Try to enable FTS5. If this fails, we will fall back to LIKE.
        try:
            cur.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts
                USING fts5(
                  entry_hash UNINDEXED,
                  title,
                  content,
                  tags,
                  tokenize='porter'
                )
                """
            )
            self._fts_enabled = True
        except sqlite3.OperationalError:
            self._fts_enabled = False

        self._conn.commit()

    @property
    def fts_enabled(self) -> bool:
        return self._fts_enabled

    # ------------------------------------------------------------------
    # Upsert / delete
    # ------------------------------------------------------------------

    def upsert(
        self,
        entry_hash: str,
        title: str,
        content: str,
        tags: Sequence[str],
        links: Dict[str, str],
        extra: Dict[str, Any],
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> None:
        tags_norm = [_norm_tag(t) for t in tags if _norm_tag(t)]
        tags_text = _tags_to_text(tags_norm)

        crystal_address = None
        crystal_index = None
        if isinstance(extra, dict):
            crystal_address = extra.get("crystal_address") or extra.get("address")
            if isinstance(extra.get("crystal_index"), int):
                crystal_index = int(extra["crystal_index"])

        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO entries(
              entry_hash, title, content, tags_json, tags_text, links_json,
              extra_json, created_at, updated_at, crystal_address, crystal_index
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                entry_hash,
                title,
                content,
                json.dumps(list(tags_norm), ensure_ascii=False),
                tags_text,
                json.dumps(links or {}, ensure_ascii=False),
                json.dumps(extra or {}, ensure_ascii=False),
                created_at,
                updated_at,
                crystal_address,
                crystal_index,
            ),
        )

        if self._fts_enabled:
            cur.execute(
                """
                INSERT OR REPLACE INTO entries_fts(entry_hash, title, content, tags)
                VALUES(?,?,?,?)
                """,
                (entry_hash, title, content, tags_text),
            )

        self._conn.commit()

    def delete(self, entry_hash: str) -> None:
        cur = self._conn.cursor()
        cur.execute("DELETE FROM entries WHERE entry_hash=?", (entry_hash,))
        if self._fts_enabled:
            cur.execute("DELETE FROM entries_fts WHERE entry_hash=?", (entry_hash,))
        self._conn.commit()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str = "",
        tags: Optional[Sequence[str]] = None,
        crystal_index: Optional[int] = None,
        limit: int = 20,
    ) -> List[MemoryIndexHit]:
        """Search the index.

        Parameters
        ----------
        query:
            Free text query.
        tags:
            Require all tags.
        crystal_index:
            Optional CrystalAddress linear index (0..255).
        limit:
            Maximum hits.
        """

        req_tags = [_norm_tag(t) for t in (tags or []) if _norm_tag(t)]
        q = (query or "").strip()

        cur = self._conn.cursor()

        # Candidate hashes ranked by FTS or heuristic score.
        hits: List[MemoryIndexHit] = []

        if q and self._fts_enabled:
            match = _fts_query(q)
            if not match:
                match = q
            # bm25 lower is better → we negate for a "higher is better" score.
            cur.execute(
                """
                SELECT entry_hash, -bm25(entries_fts) AS score
                FROM entries_fts
                WHERE entries_fts MATCH ?
                ORDER BY bm25(entries_fts)
                LIMIT ?
                """,
                (match, int(limit) * 5),
            )
            rows = cur.fetchall()
            hits = [MemoryIndexHit(r["entry_hash"], float(r["score"])) for r in rows]
        elif q:
            # LIKE-based fallback (no FTS available)
            like = f"%{q.lower()}%"
            cur.execute(
                """
                SELECT entry_hash,
                       (CASE WHEN lower(title)   LIKE ? THEN 3 ELSE 0 END +
                        CASE WHEN lower(content) LIKE ? THEN 1 ELSE 0 END +
                        CASE WHEN lower(tags_text) LIKE ? THEN 2 ELSE 0 END) AS score
                FROM entries
                WHERE lower(title) LIKE ? OR lower(content) LIKE ? OR lower(tags_text) LIKE ?
                ORDER BY score DESC
                LIMIT ?
                """,
                (like, like, like, like, like, like, int(limit) * 10),
            )
            rows = cur.fetchall()
            hits = [MemoryIndexHit(r["entry_hash"], float(r["score"])) for r in rows]
        else:
            # No query: start from all entries.
            cur.execute(
                """SELECT entry_hash, 0.0 AS score FROM entries ORDER BY created_at DESC LIMIT ?""",
                (int(limit) * 50,),
            )
            rows = cur.fetchall()
            hits = [MemoryIndexHit(r["entry_hash"], float(r["score"])) for r in rows]

        # Apply tag + address filters by inspecting stored rows.
        filtered: List[MemoryIndexHit] = []
        for h in hits:
            cur.execute(
                """
                SELECT tags_json, crystal_index
                FROM entries
                WHERE entry_hash=?
                """,
                (h.entry_hash,),
            )
            row = cur.fetchone()
            if row is None:
                continue
            if crystal_index is not None:
                if row["crystal_index"] is None or int(row["crystal_index"]) != int(crystal_index):
                    continue
            if req_tags:
                try:
                    entry_tags = {t.lower() for t in (json.loads(row["tags_json"]) or [])}
                except Exception:
                    entry_tags = set()
                if any(t not in entry_tags for t in req_tags):
                    continue
            filtered.append(h)
            if len(filtered) >= limit:
                break

        return filtered

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def rebuild_from_entries_dir(self, entries_dir: Path) -> int:
        """Rebuild the index from JSON files on disk.

        Returns
        -------
        int
            Number of entries indexed.
        """
        count = 0
        for p in sorted(entries_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                h = data.get("content_hash") or p.stem
                title = data.get("title", "")
                content = data.get("content", "")
                tags = data.get("tags", []) or []
                links = data.get("links", {}) or {}
                extra = data.get("extra", {}) or {}
                created_at = data.get("created_at")
                updated_at = data.get("updated_at")
                self.upsert(
                    entry_hash=h,
                    title=title,
                    content=content,
                    tags=tags,
                    links=links,
                    extra=extra,
                    created_at=created_at,
                    updated_at=updated_at,
                )
                count += 1
            except Exception:
                continue
        return count

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
