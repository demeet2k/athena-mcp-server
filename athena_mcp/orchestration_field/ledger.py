from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Mapping

from ..identity import digest, event_id
from .compiler import build_field

FIELD_SCHEMA = """
CREATE TABLE IF NOT EXISTS field_runs(
 run_id TEXT PRIMARY KEY,
 seed_ref TEXT NOT NULL,
 actor TEXT NOT NULL,
 input_json TEXT NOT NULL,
 output_json TEXT NOT NULL,
 field_digest TEXT NOT NULL,
 eid TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_field_runs_created ON field_runs(created_at);
"""


def _carrier(output: Mapping[str, Any]):
    return {
        "version": output.get("version"),
        "seed_ref": output.get("seed_ref"),
        "ecosystem": output.get("ecosystem"),
        "candidate_ids": output.get("candidate_ids"),
        "candidates": output.get("candidates"),
        "unmeasured_candidate_ids": output.get("unmeasured_candidate_ids"),
        "conflict_candidate_ids": output.get("conflict_candidate_ids"),
        "field_edges": output.get("field_edges"),
        "module_presence": output.get("module_presence"),
    }


def field_digest(output: Mapping[str, Any]):
    return hashlib.sha256(json.dumps(_carrier(output), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


class FieldLedger:
    def __init__(self, core):
        self.core = core
        self.s = core.s
        with self.s.db:
            self.s.db.executescript(FIELD_SCHEMA)
        self.core.register(
            "TOOL", "DEVELOPMENT", "ASSEMBLE", "CANDIDATE_FIELD", "FIELD1_PROVENANCE_ACTIONS",
            {"seed_ref": "stable", "module_outputs": "frozen organ outputs", "explicit_candidates": "optional measured actions"},
            {"candidates": "typed actions", "metrics": "UNMEASURED|EXPLICIT|CONFLICT", "graph": "provenance edges", "run_id": "FIELDRUN"},
            actor="GENESIS.FIELD.1", status="CANONICAL",
        )

    def compile(self, seed_ref, module_outputs, explicit_candidates=None, ecosystem=None, actor="agent", persist=True):
        inputs = {
            "seed_ref": str(seed_ref),
            "module_outputs": dict(module_outputs or {}),
            "explicit_candidates": [dict(x) for x in (explicit_candidates or [])],
            "ecosystem": dict(ecosystem or {}),
        }
        output = build_field(**inputs)
        fd = field_digest(output)
        output["field_digest"] = fd
        if not persist:
            return {**output, "persisted": False}
        parent = self.s.head("global")
        pe = parent["eid"] if parent else None
        payload = {
            "operation": "FIELD_COMPILE", "seed_ref": seed_ref, "actor": actor,
            "candidate_ids": output["candidate_ids"], "unmeasured": output["unmeasured_candidate_ids"],
            "conflicts": output["conflict_candidate_ids"], "field_digest": fd,
        }
        eid = event_id("FIELD_COMPILE", actor, pe, payload)
        ed = digest(payload, 32)
        run_id = "FIELDRUN." + digest({"eid": eid, "field_digest": fd}, 24)
        with self.s.db:
            self.s.db.execute(
                "INSERT INTO field_runs VALUES(?,?,?,?,?,?,?,?)",
                (run_id, str(seed_ref), actor, json.dumps(inputs, sort_keys=True, ensure_ascii=False), json.dumps(output, sort_keys=True, ensure_ascii=False), fd, eid, time.time()),
            )
        self.s.put_event(eid, "FIELD_COMPILE", actor, pe, payload, ed)
        self.s.set_head("global", None, None, eid, ed)
        return {**output, "persisted": True, "run_id": run_id, "eid": eid}

    def get(self, run_id):
        row = self.s.one("SELECT * FROM field_runs WHERE run_id=?", (run_id,))
        if not row:
            raise KeyError("unknown field run")
        return {
            "run_id": row["run_id"], "seed_ref": row["seed_ref"], "actor": row["actor"],
            "input": json.loads(row["input_json"]), "output": json.loads(row["output_json"]),
            "field_digest": row["field_digest"], "eid": row["eid"], "created_at": row["created_at"],
        }

    def replay(self, run_id):
        stored = self.get(run_id)
        recomputed = build_field(**stored["input"])
        now = field_digest(recomputed)
        match = now == stored["field_digest"]
        return {
            "run_id": run_id,
            "status": "REPLAY_MATCH" if match else "REPLAY_DIVERGED",
            "match": match,
            "stored_field_digest": stored["field_digest"],
            "recomputed_field_digest": now,
            "stored_candidate_ids": stored["output"].get("candidate_ids", []),
            "recomputed_candidate_ids": recomputed.get("candidate_ids", []),
            "stored_edges": stored["output"].get("field_edges", []),
            "recomputed_edges": recomputed.get("field_edges", []),
            "stored_conflicts": stored["output"].get("conflict_candidate_ids", []),
            "recomputed_conflicts": recomputed.get("conflict_candidate_ids", []),
        }

    def recent(self, limit=50):
        limit = max(1, min(int(limit), 500))
        return self.s.rows("SELECT run_id,seed_ref,actor,field_digest,eid,created_at FROM field_runs ORDER BY created_at DESC LIMIT ?", (limit,))

    def benchmark(self):
        count = self.s.one("SELECT COUNT(*) n FROM field_runs")["n"]
        checked = matches = 0
        for row in self.s.rows("SELECT run_id FROM field_runs ORDER BY created_at DESC LIMIT 20"):
            checked += 1
            if self.replay(row["run_id"])["match"]:
                matches += 1
        return {
            "field_runs": count,
            "field_replay_sample": checked,
            "field_replay_matches": matches,
            "field_replay_match_rate": matches / checked if checked else None,
        }
