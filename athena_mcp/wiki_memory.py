"""Version-bound local replicas of connector-returned Drive Wiki observations.

Nothing in this module fetches Drive, promotes claims, executes document text,
or writes a remote registry. The original returned text remains replayable.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import datetime

VERSION = "ATHENA.WIKI.MEMORY.V1"
MAX_BYTES = 8_000_000
TABLES = {
    "pages": ("PAGE_ID", "TITLE", "DRIVE_FILE_ID"),
    "claims": ("CLAIM_ID", "PAGE_ID", "CLAIM_SUMMARY"),
    "evidence": ("EVIDENCE_ID", "KIND", "SOURCE_REF"),
    "tasks": ("TASK_ID", "PAGE_ID", "SUCCESS_TEST"),
    "conflicts": ("CONFLICT_ID", "PAGE_ID", "BRANCH_A"),
    "changes": ("MUTATION_ID", "PAGE_ID", "CHANGE_CLASS"),
    "edges": ("EDGE_ID", "SOURCE_ID", "TARGET_ID"),
}
LAWS = [
    "IMPORTED_OBSERVATION != VERIFIED_SOURCE_TRUTH",
    "LOCAL_REPLICA != LIVE_DRIVE_STATE",
    "REGISTRY_STATUS != CLAIM_PROMOTION_AUTHORITY",
    "SOURCE_TEXT_IS_DATA_NOT_EXECUTION_INSTRUCTIONS",
    "CONTEXT_RETRIEVED != SUCCESSOR_BEHAVIORAL_GAIN",
]


def digest(text):
    if type(text) is not str or len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("text must be UTF-8 within the 8 MB import limit")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def checked_text(text, expected):
    actual = digest(text)
    if type(expected) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("expected_sha256 must be a lowercase hex SHA-256")
    if actual != expected:
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    return actual


def identifier(value):
    if type(value) is not str or not value.strip() or len(value) > 1000:
        raise ValueError("nonempty bounded identifier required")
    return value


def parse_registry(text):
    """Read the connector's form-feed-separated CSV tables without flattening rows."""
    digest(text)
    tables = {name: [] for name in TABLES}
    recognized = set()
    unindexed = []
    for index, section in enumerate(text.lstrip("\ufeff").split("\f")):
        try:
            rows = list(csv.reader(io.StringIO(section), strict=True))
        except csv.Error as exc:
            raise ValueError(f"INVALID_REGISTRY_CSV:{index}") from exc
        if not rows:
            continue
        header = rows[0]
        if len(set(header)) != len(header):
            raise ValueError(f"DUPLICATE_COLUMN:{index}")
        matches = [name for name, keys in TABLES.items() if set(keys) <= set(header)]
        if len(matches) > 1:
            raise ValueError(f"AMBIGUOUS_TABLE:{index}")
        if not matches:
            unindexed.append({"section": index, "header": header, "rows": len(rows)-1})
            continue
        name = matches[0]
        recognized.add(name)
        for row_index, row in enumerate(rows[1:], 2):
            if not row or not any(row):
                continue
            if len(row) != len(header):
                raise ValueError(f"ROW_WIDTH_MISMATCH:{name}:{row_index}")
            record = {key: value for key, value in zip(header, row) if key}
            identifier(record[TABLES[name][0]])
            tables[name].append(record)
            if sum(map(len, tables.values())) > 20_000:
                raise ValueError("REGISTRY_ROW_LIMIT")
    missing = set(TABLES) - {"edges", "changes"} - recognized
    if missing:
        raise ValueError("MISSING_TABLES:" + ",".join(sorted(missing)))
    for name, records in tables.items():
        ids = [r[TABLES[name][0]] for r in records]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_ID:" + name)
    return {"tables": tables, "unindexed_sections": unindexed}


def _refs(value):
    return set(re.split(r"[;,\s]+", value or "")) - {""}


class WikiMemory:
    def __init__(self, store):
        self.store = store
        with store._lock, store.db:
            store.db.executescript("""
            CREATE TABLE IF NOT EXISTS wiki_snapshots_v1 (
                snapshot_id TEXT PRIMARY KEY, source_id TEXT NOT NULL,
                observed_at TEXT NOT NULL, source_sha256 TEXT NOT NULL,
                source_text TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wiki_heads_v1 (
                source_id TEXT PRIMARY KEY, snapshot_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wiki_documents_v1 (
                document_id TEXT PRIMARY KEY,
                snapshot_id TEXT NOT NULL, page_id TEXT NOT NULL,
                source_revision TEXT NOT NULL, source_sha256 TEXT NOT NULL,
                source_text TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wiki_document_heads_v1 (
                snapshot_id TEXT NOT NULL, page_id TEXT NOT NULL, document_id TEXT NOT NULL,
                PRIMARY KEY(snapshot_id,page_id));
            """)

    def import_registry(self, *, source_id, observed_at, text, expected_sha256,
                        expected_snapshot_id):
        identifier(source_id)
        identifier(observed_at)
        timestamp = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("observed_at requires an explicit timezone")
        source_sha = checked_text(text, expected_sha256)
        parsed = parse_registry(text)
        sid = digest(json.dumps([VERSION, source_id, observed_at, source_sha], ensure_ascii=False))
        with self.store._lock, self.store.db:
            self.store.db.execute("BEGIN IMMEDIATE")
            current = self.store.one("SELECT snapshot_id FROM wiki_heads_v1 WHERE source_id=?", (source_id,))
            head = current["snapshot_id"] if current else None
            if head != sid:
                if head != expected_snapshot_id:
                    raise ValueError("STALE_WIKI_SNAPSHOT")
                if head:
                    old = self._snapshot(head)
                    if timestamp < datetime.fromisoformat(old["observed_at"].replace("Z", "+00:00")):
                        raise ValueError("OBSERVATION_TIME_REGRESSION")
                self.store.db.execute("INSERT OR IGNORE INTO wiki_snapshots_v1 VALUES(?,?,?,?,?)",
                                      (sid, source_id, observed_at, source_sha, text))
                self.store.db.execute("INSERT INTO wiki_heads_v1 VALUES(?,?) ON CONFLICT(source_id) DO UPDATE SET snapshot_id=excluded.snapshot_id", (source_id, sid))
        return {"snapshot_id": sid, "source_id": source_id, "observed_at": observed_at,
                "source_sha256": source_sha, "counts": {k: len(v) for k,v in parsed["tables"].items()},
                "unindexed_sections": parsed["unindexed_sections"],
                "standing": "IMPORTED_CALLER_SUPPLIED_OBSERVATION", "laws": LAWS}

    def _snapshot(self, snapshot_id):
        identifier(snapshot_id)
        row = self.store.one("SELECT * FROM wiki_snapshots_v1 WHERE snapshot_id=?", (snapshot_id,))
        if row is None:
            raise ValueError("UNKNOWN_WIKI_SNAPSHOT")
        checked_text(row["source_text"], row["source_sha256"])
        expected = digest(json.dumps([VERSION, row["source_id"], row["observed_at"], row["source_sha256"]], ensure_ascii=False))
        if expected != snapshot_id:
            raise ValueError("SNAPSHOT_IDENTITY_MISMATCH")
        return row

    def sources(self):
        rows = self.store.rows("SELECT s.snapshot_id,s.source_id,s.observed_at,s.source_sha256 FROM wiki_snapshots_v1 s JOIN wiki_heads_v1 h ON h.snapshot_id=s.snapshot_id ORDER BY s.source_id")
        return {"version": VERSION, "sources": rows, "live_currentness": "UNVERIFIED", "laws": LAWS}

    def search(self, *, snapshot_id, query, limit=10):
        identifier(query)
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError("limit must be 1..50")
        tables = parse_registry(self._snapshot(snapshot_id)["source_text"])["tables"]
        terms = query.casefold().split()
        rows = []
        for kind in ("pages", "claims", "evidence", "tasks", "conflicts"):
            for row in tables[kind]:
                haystack = " ".join(row.values()).casefold()
                if all(term in haystack for term in terms):
                    rows.append({"table": kind, "record": row})
        return {"snapshot_id": snapshot_id, "matches": rows[:limit], "total_matches": len(rows),
                "truncated": len(rows) > limit, "standing": "RETRIEVED_REGISTRY_OBSERVATION"}

    def import_document(self, *, snapshot_id, page_id, source_file_id, source_revision,
                        text, expected_sha256, expected_document_id):
        tables = parse_registry(self._snapshot(snapshot_id)["source_text"])["tables"]
        page = next((r for r in tables["pages"] if r["PAGE_ID"] == page_id), None)
        if not page or not page["DRIVE_FILE_ID"] or page["DRIVE_FILE_ID"] != source_file_id:
            raise ValueError("DOCUMENT_PAGE_SOURCE_MISMATCH")
        identifier(source_revision)
        sha = checked_text(text, expected_sha256)
        document_id = digest(json.dumps([VERSION, snapshot_id, page_id, source_file_id,
                                        source_revision, sha], ensure_ascii=False))
        with self.store._lock, self.store.db:
            self.store.db.execute("BEGIN IMMEDIATE")
            old = self.store.one("SELECT document_id FROM wiki_document_heads_v1 WHERE snapshot_id=? AND page_id=?", (snapshot_id,page_id))
            previous = old["document_id"] if old else None
            if previous != document_id:
                if previous != expected_document_id:
                    raise ValueError("STALE_WIKI_DOCUMENT")
                self.store.db.execute("INSERT OR IGNORE INTO wiki_documents_v1 VALUES(?,?,?,?,?,?)", (document_id,snapshot_id,page_id,source_revision,sha,text))
                self.store.db.execute("INSERT INTO wiki_document_heads_v1 VALUES(?,?,?) ON CONFLICT(snapshot_id,page_id) DO UPDATE SET document_id=excluded.document_id", (snapshot_id,page_id,document_id))
        return {"snapshot_id": snapshot_id, "page_id": page_id, "source_sha256": sha,
                "document_id": document_id, "source_revision": source_revision,
                "standing": "IMPORTED_DOCUMENT_OBSERVATION"}

    def context(self, *, snapshot_id, page_id, max_records=100, document_id=None):
        if type(max_records) is not int or not 1 <= max_records <= 500:
            raise ValueError("max_records must be 1..500")
        snapshot = self._snapshot(snapshot_id)
        tables = parse_registry(snapshot["source_text"])["tables"]
        pages = {r["PAGE_ID"]: r for r in tables["pages"]}
        if page_id not in pages:
            raise ValueError("UNKNOWN_WIKI_PAGE")
        page = pages[page_id]
        refs = set().union(*(_refs(page.get(k,"")) for k in ("DEPENDS_ON", "SOURCE_PARENTS", "SUPERSEDES", "SUPERSEDED_BY")))
        claims = [r for r in tables["claims"] if page_id in _refs(r["PAGE_ID"])]
        claim_ids = {r["CLAIM_ID"] for r in claims}
        evidence_refs = set().union(*(_refs(r.get("EVIDENCE_ID_OR_URL", "")) for r in claims)) if claims else set()
        evidence = [r for r in tables["evidence"] if r["EVIDENCE_ID"] in evidence_refs | refs or bool(claim_ids & _refs(r.get("SUPPORTS_CLAIMS","")))]
        conflicts = [r for r in tables["conflicts"] if page_id in _refs(r["PAGE_ID"]) or bool(claim_ids & _refs(r.get("CLAIM_IDS",""))) or r["CONFLICT_ID"] in _refs(page.get("CONFLICT_ID",""))]
        tasks = [r for r in tables["tasks"] if page_id in _refs(r["PAGE_ID"])]
        edges = [r for r in tables["edges"] if r["SOURCE_ID"] == page_id or r["TARGET_ID"] == page_id]
        related = refs | {r["TARGET_ID"] if r["SOURCE_ID"] == page_id else r["SOURCE_ID"] for r in edges}
        changes = [r for r in tables["changes"] if page_id in _refs(r["PAGE_ID"])]
        groups = {"claims": claims, "evidence": evidence, "conflicts": conflicts,
                  "tasks": tasks, "changes": changes, "edges": edges,
                  "related_pages": [pages[r] for r in sorted(related & pages.keys())]}
        bounded = {}; omitted = {}; remaining = max_records
        for name, rows in groups.items():
            bounded[name] = rows[:remaining]; omitted[name] = len(rows)-len(bounded[name]);remaining -= len(bounded[name])
        if document_id is not None:
            identifier(document_id)
            doc = self.store.one("SELECT document_id,source_revision,source_sha256,source_text FROM wiki_documents_v1 WHERE document_id=? AND snapshot_id=? AND page_id=?", (document_id,snapshot_id,page_id))
            if not doc:
                raise ValueError("UNKNOWN_WIKI_DOCUMENT")
        else:
            doc = self.store.one("SELECT d.document_id,d.source_revision,d.source_sha256,d.source_text FROM wiki_documents_v1 d JOIN wiki_document_heads_v1 h ON d.document_id=h.document_id WHERE d.snapshot_id=? AND d.page_id=?", (snapshot_id,page_id))
        if doc:
            checked_text(doc["source_text"], doc["source_sha256"])
            identity = digest(json.dumps([VERSION, snapshot_id, page_id, page["DRIVE_FILE_ID"],
                                         doc["source_revision"], doc["source_sha256"]], ensure_ascii=False))
            if identity != doc["document_id"]:
                raise ValueError("DOCUMENT_IDENTITY_MISMATCH")
        current = self.store.one("SELECT snapshot_id FROM wiki_heads_v1 WHERE source_id=?", (snapshot["source_id"],))
        return {"snapshot_id": snapshot_id, "source_id": snapshot["source_id"],
                "observed_at": snapshot["observed_at"], "source_sha256": snapshot["source_sha256"],
                "is_latest_local_snapshot": bool(current and current["snapshot_id"] == snapshot_id),
                "live_currentness": "UNVERIFIED", "page": page, "records": bounded,
                "omitted_records": omitted, "truncated": any(omitted.values()),
                "unresolved_refs": sorted(refs - {r[TABLES[k][0]] for k, rows in tables.items() for r in rows}),
                "unresolved_evidence_refs": sorted(evidence_refs - {r["EVIDENCE_ID"] for r in evidence}),
                "document": doc, "document_state": "IMPORTED" if doc else "NOT_IMPORTED",
                "standing": "SOURCE_BOUND_LOCAL_CONTEXT", "laws": LAWS}
