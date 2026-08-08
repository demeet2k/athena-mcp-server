from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, Mapping, Optional

from .identity import digest, event_id

SCHEMA_LEDGER_VERSION = "ATHENA.SCHEMA.1"
CURRENT_DB_SCHEMA_VERSION = 1

SCHEMA_LEDGER_SQL = '''
CREATE TABLE IF NOT EXISTS runtime_schema_meta(
 key TEXT PRIMARY KEY,
 value_json TEXT NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS schema_migrations(
 migration_id TEXT PRIMARY KEY,
 from_version INTEGER NOT NULL,
 to_version INTEGER NOT NULL,
 name TEXT NOT NULL,
 status TEXT NOT NULL,
 preflight_json TEXT NOT NULL,
 postflight_json TEXT NOT NULL,
 component_versions_json TEXT NOT NULL,
 migration_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 applied_at REAL NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_schema_migrations_to_version ON schema_migrations(to_version);
'''

DEFAULT_COMPONENT_VERSIONS = {
    "base_runtime": "2.4+unified",
    "collective_runtime": "V1",
    "collective_growth": "V1",
    "collective_memory": "V2",
    "aor": "AOR.3.1",
    "authority": "Y.1",
    "equivalence": "EQ.1",
    "extraction": "SX.1",
    "retrieval": "RAG.1",
    "hug": "HUG.ABI.1",
    "gap": "GAP.1",
    "field": "FIELD.1",
    "transport": "AORCOLL.TRANSPORT.1",
    "surface": "ATHENA.SURFACE.2",
    "composition": "ATHENA.COMPOSITION.2",
    "promotion": "ATHENA.PROMOTION.1",
    "cycle": "ATHENA.CYCLE.1",
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _table_names(store) -> list[str]:
    rows = store.rows("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [str(row["name"]) for row in rows]


def _index_names(store) -> list[str]:
    rows = store.rows("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [str(row["name"]) for row in rows]


def _schema_fingerprint(store) -> Dict[str, Any]:
    tables = _table_names(store)
    indexes = _index_names(store)
    definitions = store.rows("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE type IN ('table','index') AND name NOT LIKE 'sqlite_%' ORDER BY type,name")
    normalized = [{"type": r["type"], "name": r["name"], "table": r["tbl_name"], "sql": r["sql"]} for r in definitions]
    return {
        "tables": tables,
        "indexes": indexes,
        "definition_digest": digest(normalized, 64),
        "table_count": len(tables),
        "index_count": len(indexes),
    }


class SchemaManager:
    """Additive schema-version ledger over the existing modular SQLite runtime.

    Version 1 intentionally does not rewrite existing organ tables. It records a
    witnessed inventory of the already-created additive schema and gives later
    migrations a version/CAS-like anchor. Future destructive migrations must be
    added as explicit numbered steps rather than hidden CREATE/ALTER side effects.
    """

    def __init__(self, core, component_versions: Optional[Mapping[str, str]] = None):
        self.core = core
        self.s = core.s
        self.component_versions = {**DEFAULT_COMPONENT_VERSIONS, **dict(component_versions or {})}
        with self.s.db:
            self.s.db.executescript(SCHEMA_LEDGER_SQL)

    def current_version(self) -> int:
        row = self.s.one("SELECT value_json FROM runtime_schema_meta WHERE key='db_schema_version'")
        if not row:
            return 0
        try:
            return int(json.loads(row["value_json"]))
        except Exception:
            return 0

    def status(self) -> Dict[str, Any]:
        current = self.current_version()
        latest = self.s.one("SELECT * FROM schema_migrations ORDER BY to_version DESC LIMIT 1")
        fingerprint = _schema_fingerprint(self.s)
        return {
            "version": SCHEMA_LEDGER_VERSION,
            "current_db_schema_version": current,
            "target_db_schema_version": CURRENT_DB_SCHEMA_VERSION,
            "up_to_date": current == CURRENT_DB_SCHEMA_VERSION,
            "latest_migration": dict(latest) if latest else None,
            "component_versions": dict(self.component_versions),
            "schema_fingerprint": fingerprint,
        }

    def plan(self) -> Dict[str, Any]:
        current = self.current_version()
        if current > CURRENT_DB_SCHEMA_VERSION:
            return {
                "status": "FUTURE_SCHEMA_BLOCKED",
                "current": current,
                "target": CURRENT_DB_SCHEMA_VERSION,
                "steps": [],
                "boundary": "runtime refuses to silently downgrade a database created by a newer schema version",
            }
        steps = []
        if current < 1:
            steps.append({
                "from_version": current,
                "to_version": 1,
                "name": "inventory_existing_modular_schema",
                "mode": "ADDITIVE_INVENTORY_NO_DESTRUCTIVE_REWRITE",
            })
        return {
            "status": "MIGRATION_REQUIRED" if steps else "UP_TO_DATE",
            "current": current,
            "target": CURRENT_DB_SCHEMA_VERSION,
            "steps": steps,
        }

    def _event(self, payload: Mapping[str, Any], actor: str) -> str:
        parent = self.s.head("global")
        parent_eid = parent["eid"] if parent else None
        eid = event_id("SCHEMA_MIGRATION", actor, parent_eid, dict(payload))
        event_digest = digest(dict(payload), 32)
        self.s.put_event(eid, "SCHEMA_MIGRATION", actor, parent_eid, dict(payload), event_digest)
        self.s.set_head("global", None, None, eid, event_digest)
        return eid

    def migrate(self, actor: str = "agent", required_tables: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        plan = self.plan()
        if plan["status"] == "FUTURE_SCHEMA_BLOCKED":
            return {**plan, "applied": False}
        if not plan["steps"]:
            return {"status": "UP_TO_DATE", "applied": False, "schema": self.status()}

        required = sorted({str(x) for x in (required_tables or []) if str(x)})
        pre = _schema_fingerprint(self.s)
        missing_before = sorted(set(required) - set(pre["tables"]))
        if missing_before:
            return {
                "status": "PREFLIGHT_FAILED",
                "applied": False,
                "missing_required_tables": missing_before,
                "preflight": pre,
            }

        step = plan["steps"][0]
        post = _schema_fingerprint(self.s)
        payload = {
            "operation": "APPLY_SCHEMA_MIGRATION",
            "from_version": step["from_version"],
            "to_version": step["to_version"],
            "name": step["name"],
            "mode": step["mode"],
            "preflight": pre,
            "postflight": post,
            "component_versions": self.component_versions,
        }
        migration_digest = digest(payload, 64)
        migration_id = "MIGRUN." + digest({"migration": migration_digest, "to": step["to_version"]}, 24)
        eid = self._event({**payload, "migration_id": migration_id, "migration_digest": migration_digest}, actor)
        now = time.time()
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO schema_migrations VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    migration_id, step["from_version"], step["to_version"], step["name"], "APPLIED",
                    _canonical(pre), _canonical(post), _canonical(self.component_versions), migration_digest, eid, now,
                ),
            )
            self.s.db.execute(
                "INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)",
                ("db_schema_version", _canonical(step["to_version"]), now),
            )
            self.s.db.execute(
                "INSERT OR REPLACE INTO runtime_schema_meta VALUES(?,?,?)",
                ("component_versions", _canonical(self.component_versions), now),
            )
        return {
            "status": "APPLIED",
            "applied": True,
            "migration_id": migration_id,
            "migration_digest": migration_digest,
            "eid": eid,
            "from_version": step["from_version"],
            "to_version": step["to_version"],
            "preflight": pre,
            "postflight": post,
            "component_versions": dict(self.component_versions),
        }

    def verify(self, required_tables: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        status = self.status()
        actual = status["schema_fingerprint"]
        required = sorted({str(x) for x in (required_tables or []) if str(x)})
        missing = sorted(set(required) - set(actual["tables"]))
        latest = status["latest_migration"]
        recorded = None
        if latest:
            recorded = json.loads(latest["postflight_json"])
        return {
            "version": SCHEMA_LEDGER_VERSION,
            "status": "PASS" if status["up_to_date"] and not missing else "FAIL",
            "up_to_date": status["up_to_date"],
            "missing_required_tables": missing,
            "actual": actual,
            "recorded_postflight": recorded,
            "definition_changed_since_migration": bool(recorded and recorded.get("definition_digest") != actual.get("definition_digest")),
            "boundary": "schema fingerprint drift is observable; drift is not automatically corruption because additive organ tables may be created after the migration receipt",
        }

    def recent(self, limit: int = 50):
        limit = max(1, min(int(limit), 500))
        return self.s.rows("SELECT migration_id,from_version,to_version,name,status,migration_digest,eid,applied_at FROM schema_migrations ORDER BY applied_at DESC LIMIT ?", (limit,))
