from __future__ import annotations

import hashlib
import json
import math
import re
import time
from collections import Counter
from typing import Any, Dict, Mapping, Sequence

from .collective_runtime import CollectiveRuntime
from .collective_growth import CollectiveGrowthRuntime


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def _tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        text = " ".join(str(x) for x in value)
    else:
        text = str(value)
    return {x.lower() for x in re.findall(r"[A-Za-z0-9_]{2,}", text)}


SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_pheromones(
 route_key TEXT PRIMARY KEY,
 score REAL NOT NULL,
 version INTEGER NOT NULL,
 observation_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_rgo_observations(
 obs_id TEXT PRIMARY KEY,
 plan_key TEXT NOT NULL,
 predicted REAL NOT NULL,
 observed REAL NOT NULL,
 error REAL NOT NULL,
 features_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_collective_rgo_plan ON collective_rgo_observations(plan_key,created_at);
CREATE TABLE IF NOT EXISTS collective_rgo_calibration(
 scope TEXT PRIMARY KEY,
 n INTEGER NOT NULL,
 sum_pred REAL NOT NULL,
 sum_obs REAL NOT NULL,
 sum_pred2 REAL NOT NULL,
 sum_pred_obs REAL NOT NULL,
 sum_abs_error REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_topologies(
 topology_id TEXT PRIMARY KEY,
 version INTEGER NOT NULL,
 state_json TEXT NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_topology_history(
 txid TEXT PRIMARY KEY,
 topology_id TEXT NOT NULL,
 from_version INTEGER NOT NULL,
 to_version INTEGER NOT NULL,
 operation TEXT NOT NULL,
 before_json TEXT NOT NULL,
 after_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_collective_topology_hist ON collective_topology_history(topology_id,to_version);
CREATE TABLE IF NOT EXISTS failure_antibodies(
 antibody_id TEXT PRIMARY KEY,
 signature TEXT NOT NULL,
 scope TEXT NOT NULL,
 trigger_json TEXT NOT NULL,
 detector_json TEXT NOT NULL,
 repair_json TEXT NOT NULL,
 evidence_json TEXT NOT NULL,
 regression_json TEXT NOT NULL,
 hits INTEGER NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_failure_antibodies_scope ON failure_antibodies(scope,updated_at);
"""


class CollectiveMemoryRuntime:
    """Persistent third-layer collective runtime.

    V2 makes selected collective-control state durable while preserving the
    existing ATHENA distinction between advisory calculation and canonical
    semantic mutation. Topology state here is a dedicated collective control
    plane with its own CAS/version history and rollback; it does not silently
    rewrite JSPACE or canonical objects.
    """

    DEFAULT_RELATION_MODES = {
        "DEPENDS_ON": "REVERSE",
        "REQUIRES": "REVERSE",
        "DERIVED_FROM": "REVERSE",
        "SUPPORTED_BY": "REVERSE",
        "USES": "REVERSE",
        "IMPLIES": "OUTBOUND",
        "INVALIDATES": "OUTBOUND",
        "PRODUCES": "OUTBOUND",
    }

    def __init__(self, store: Any, collective: CollectiveRuntime | None = None, growth: CollectiveGrowthRuntime | None = None):
        self.s = store
        self.collective = collective or CollectiveRuntime()
        self.growth = growth or CollectiveGrowthRuntime()
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> Dict[str, Any]:
        counts = {
            "pheromones": self.s.one("SELECT COUNT(*) AS n FROM collective_pheromones")["n"],
            "rgo_observations": self.s.one("SELECT COUNT(*) AS n FROM collective_rgo_observations")["n"],
            "topologies": self.s.one("SELECT COUNT(*) AS n FROM collective_topologies")["n"],
            "topology_transactions": self.s.one("SELECT COUNT(*) AS n FROM collective_topology_history")["n"],
            "failure_antibodies": self.s.one("SELECT COUNT(*) AS n FROM failure_antibodies")["n"],
        }
        return {
            "version": "COLLECTIVE_RUNTIME_V2",
            "persistent_surfaces": counts,
            "operators": [
                "pheromone_reinforce", "pheromone_field", "jspace_dependency_alarm",
                "record_rgo_observation", "calibrate_rgo",
                "topology_get", "topology_apply", "topology_rollback",
                "register_failure_antibody", "match_failure_antibodies",
            ],
            "laws": [
                "REUSE/EVIDENCE strengthens routes; AGE/STALE/CONTRADICTION evaporates inherited privilege",
                "INVALIDATION propagates through typed JSPACE dependency semantics, not global broadcast",
                "PREDICTED_RGO is calibrated against OBSERVED_RGO; prediction is not self-certifying",
                "TOPOLOGY_MUTATION requires expected-version CAS and records reversible before/after witnesses",
                "FAILURE should become a reusable detector+repair+regression antibody rather than repeated rediscovery",
            ],
        }

    def pheromone_reinforce(self, route_key: str, observations: Mapping[str, Any], age: float | None = None, evaporation_rate: float = 0.08, deposit_gain: float = 0.35, actor: str = "agent") -> Dict[str, Any]:
        route_key = str(route_key).strip()
        if not route_key:
            raise ValueError("route_key must not be empty")
        now = time.time()
        with self.s._lock:
            row = self.s.one("SELECT * FROM collective_pheromones WHERE route_key=?", (route_key,))
            current = float(row["score"]) if row else 0.0
            version = int(row["version"]) if row else 0
            age_units = max(0.0, float(age)) if age is not None else (max(0.0, now-float(row["updated_at"])) / 3600.0 if row else 0.0)
            update = self.collective.stigmergy_update(current, observations, age_units, evaporation_rate, deposit_gain)
            score = float(update["updated_score"])
            obs_json = json.dumps(dict(observations), sort_keys=True, ensure_ascii=False)
            created = float(row["created_at"]) if row else now
            with self.s.db:
                self.s.db.execute(
                    """INSERT INTO collective_pheromones(route_key,score,version,observation_json,actor,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?)
                       ON CONFLICT(route_key) DO UPDATE SET
                         score=excluded.score,version=excluded.version,observation_json=excluded.observation_json,
                         actor=excluded.actor,updated_at=excluded.updated_at""",
                    (route_key, score, version+1, obs_json, actor, created, now),
                )
        return {"route_key": route_key, "previous_score": round(current, 6), "score": round(score, 6), "version": version+1, "age_units": round(age_units, 6), "update": update, "persisted": True}

    def pheromone_field(self, route_key: str | None = None, limit: int = 100, min_score: float = 0.0) -> Dict[str, Any]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be in [1,1000]")
        min_score = _clamp(min_score)
        if route_key is not None:
            row = self.s.one("SELECT * FROM collective_pheromones WHERE route_key=?", (str(route_key),))
            rows = [row] if row else []
        else:
            rows = self.s.rows("SELECT * FROM collective_pheromones WHERE score>=? ORDER BY score DESC,updated_at DESC LIMIT ?", (min_score, limit))
        out = []
        for r in rows:
            if not r:
                continue
            out.append({"route_key": r["route_key"], "score": round(float(r["score"]), 6), "version": int(r["version"]), "last_observation": json.loads(r["observation_json"]), "actor": r["actor"], "created_at": float(r["created_at"]), "updated_at": float(r["updated_at"])})
        return {"routes": out, "count": len(out), "law": "priority is durable but not immortal; updates require fresh evidence/reuse or decay"}

    def jspace_dependency_alarm(self, seeds: Sequence[Mapping[str, Any]], relation_modes: Mapping[str, str] | None = None, max_hops: int = 6, hop_decay: float = 0.82, threshold: float = 0.08) -> Dict[str, Any]:
        if not seeds:
            raise ValueError("seeds must not be empty")
        modes = {k.upper(): v.upper() for k, v in (relation_modes or self.DEFAULT_RELATION_MODES).items()}
        bad = {v for v in modes.values() if v not in {"OUTBOUND", "REVERSE", "IGNORE"}}
        if bad:
            raise ValueError("relation_modes values must be OUTBOUND, REVERSE, or IGNORE")
        rows = self.s.rows("SELECT src,relation,dst,attrs_json FROM edges")
        edges = []
        relation_counts = Counter()
        ignored = Counter()
        for row in rows:
            rel_raw = str(row["relation"])
            rel = rel_raw.upper()
            mode = modes.get(rel, "IGNORE")
            if mode == "IGNORE":
                ignored[rel_raw] += 1
                continue
            try:
                attrs = json.loads(row.get("attrs_json") or "{}")
            except Exception:
                attrs = {}
            weight = _clamp(attrs.get("weight", attrs.get("confidence", 1.0)))
            src, dst = str(row["src"]), str(row["dst"])
            if mode == "REVERSE":
                src, dst = dst, src
            edges.append({"src": src, "dst": dst, "weight": weight, "relation": rel_raw, "jspace_mode": mode})
            relation_counts[f"{rel_raw}:{mode}"] += 1
        result = self.growth.dependency_alarm(seeds, edges, max_hops, hop_decay, threshold)
        result.update({"source": "JSPACE", "selected_edges": len(edges), "relation_counts": dict(sorted(relation_counts.items())), "ignored_relation_counts": dict(sorted(ignored.items())), "relation_modes": dict(sorted(modes.items())), "law": "derive invalidation transport from typed JSPACE relations with explicit orientation; unknown relations are ignored"})
        return result

    def _calibration_row(self, scope: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_rgo_calibration WHERE scope=?", (scope,))
        return row or {"scope": scope, "n": 0, "sum_pred": 0.0, "sum_obs": 0.0, "sum_pred2": 0.0, "sum_pred_obs": 0.0, "sum_abs_error": 0.0, "updated_at": 0.0}

    def calibration_state(self, scope: str = "global") -> Dict[str, Any]:
        row = self._calibration_row(scope)
        n = int(row["n"])
        sx, sy = float(row["sum_pred"]), float(row["sum_obs"])
        sxx, sxy = float(row["sum_pred2"]), float(row["sum_pred_obs"])
        mean_error = (sy-sx)/n if n else 0.0
        mae = float(row["sum_abs_error"])/n if n else 0.0
        denom = n*sxx - sx*sx
        raw_slope = (n*sxy - sx*sy)/denom if n >= 3 and abs(denom) > 1e-12 else 1.0
        raw_intercept = (sy - raw_slope*sx)/n if n else 0.0
        reliability = n/(n+10.0) if n else 0.0
        slope = 1.0 + reliability*(raw_slope-1.0)
        intercept = reliability*raw_intercept if n >= 3 else reliability*mean_error
        return {"scope": scope, "n": n, "mean_error": round(mean_error, 6), "mae": round(mae, 6), "raw_slope": round(raw_slope, 6), "raw_intercept": round(raw_intercept, 6), "reliability": round(reliability, 6), "slope": round(slope, 6), "intercept": round(intercept, 6), "updated_at": float(row["updated_at"])}

    def record_rgo_observation(self, plan_key: str, predicted_rgo: float, observed_rgo: float, features: Mapping[str, Any] | None = None, scope: str = "global", actor: str = "agent") -> Dict[str, Any]:
        predicted = max(0.0, float(predicted_rgo))
        observed = max(0.0, float(observed_rgo))
        plan_key = str(plan_key).strip()
        scope = str(scope).strip() or "global"
        if not plan_key:
            raise ValueError("plan_key must not be empty")
        now = time.time()
        obs_id = _stable_id("RGO", plan_key, scope, predicted, observed, now)
        err = observed-predicted
        features_json = json.dumps(dict(features or {}), sort_keys=True, ensure_ascii=False)
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_rgo_observations VALUES(?,?,?,?,?,?,?,?)", (obs_id, plan_key, predicted, observed, err, features_json, actor, now))
            row = self._calibration_row(scope)
            self.s.db.execute(
                """INSERT INTO collective_rgo_calibration(scope,n,sum_pred,sum_obs,sum_pred2,sum_pred_obs,sum_abs_error,updated_at)
                   VALUES(?,?,?,?,?,?,?,?)
                   ON CONFLICT(scope) DO UPDATE SET
                     n=excluded.n,sum_pred=excluded.sum_pred,sum_obs=excluded.sum_obs,
                     sum_pred2=excluded.sum_pred2,sum_pred_obs=excluded.sum_pred_obs,
                     sum_abs_error=excluded.sum_abs_error,updated_at=excluded.updated_at""",
                (scope, int(row["n"])+1, float(row["sum_pred"])+predicted, float(row["sum_obs"])+observed, float(row["sum_pred2"])+predicted*predicted, float(row["sum_pred_obs"])+predicted*observed, float(row["sum_abs_error"])+abs(err), now),
            )
        return {"obs_id": obs_id, "plan_key": plan_key, "predicted_rgo": round(predicted, 6), "observed_rgo": round(observed, 6), "error": round(err, 6), "calibration": self.calibration_state(scope)}

    def calibrate_rgo(self, predicted_rgo: float, scope: str = "global") -> Dict[str, Any]:
        predicted = max(0.0, float(predicted_rgo))
        state = self.calibration_state(scope)
        adjusted = max(0.0, state["intercept"] + state["slope"]*predicted)
        return {"predicted_rgo": round(predicted, 6), "calibrated_rgo": round(adjusted, 6), "calibration": state, "law": "predictions acquire authority only through measured downstream outcomes"}

    @staticmethod
    def _normalize_state(state: Mapping[str, Any] | None) -> Dict[str, Any]:
        state = dict(state or {})
        modules = state.get("modules", {})
        if isinstance(modules, list):
            modules = {str(m["id"]): dict(m) for m in modules}
        else:
            modules = {str(k): dict(v) if isinstance(v, Mapping) else {"value": v} for k, v in dict(modules).items()}
        bridges = [dict(b) for b in state.get("bridges", [])]
        meta = dict(state.get("meta", {}))
        return {"modules": modules, "bridges": bridges, "meta": meta}

    def topology_get(self, topology_id: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_topologies WHERE topology_id=?", (str(topology_id),))
        if not row:
            return {"topology_id": str(topology_id), "version": 0, "state": {"modules": {}, "bridges": [], "meta": {}}, "exists": False}
        return {"topology_id": row["topology_id"], "version": int(row["version"]), "state": json.loads(row["state_json"]), "updated_at": float(row["updated_at"]), "exists": True}

    def _apply_operation(self, before: Dict[str, Any], operation: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        state = self._normalize_state(before)
        modules, bridges, meta = state["modules"], state["bridges"], state["meta"]
        op = operation.upper()
        if op == "INIT" or op == "REPLACE":
            return self._normalize_state(payload.get("state", payload))
        if op == "FISSION":
            module_id = str(payload["module_id"])
            if module_id not in modules:
                raise ValueError(f"module not found: {module_id}")
            children = payload.get("children") or []
            if len(children) < 2:
                raise ValueError("FISSION requires at least two children")
            parent = dict(modules[module_id])
            parent.update({"status": "REFERENCE", "active": False, "fission_children": [str(c["id"]) for c in children]})
            modules[module_id] = parent
            for child in children:
                cid = str(child["id"])
                if cid in modules and cid != module_id:
                    raise ValueError(f"child module already exists: {cid}")
                rec = dict(child)
                rec["id"] = cid
                rec.setdefault("active", True)
                rec.setdefault("status", "ACTIVE")
                rec["fission_parent"] = module_id
                modules[cid] = rec
            if payload.get("bridges"):
                bridges.extend(dict(b) for b in payload["bridges"])
            meta["last_structural_operation"] = "FISSION"
            return {"modules": modules, "bridges": bridges, "meta": meta}
        if op == "FUSE":
            source_ids = [str(x) for x in payload.get("module_ids", [])]
            if len(source_ids) < 2:
                raise ValueError("FUSE requires at least two module_ids")
            missing = [x for x in source_ids if x not in modules]
            if missing:
                raise ValueError(f"modules not found: {missing}")
            new_module = dict(payload["new_module"])
            new_id = str(new_module["id"])
            new_module["id"] = new_id
            new_module.setdefault("active", True)
            new_module.setdefault("status", "ACTIVE")
            new_module["fused_from"] = source_ids
            for sid in source_ids:
                old = dict(modules[sid])
                old.update({"status": "REFERENCE", "active": False, "fused_into": new_id})
                modules[sid] = old
            modules[new_id] = new_module
            if bool(payload.get("rewire_external", True)):
                rewired = []
                seen = set()
                for b in bridges:
                    b2 = dict(b)
                    for endpoint in ("src", "dst", "a", "b"):
                        if endpoint in b2 and str(b2[endpoint]) in source_ids:
                            b2[endpoint] = new_id
                    key = json.dumps(b2, sort_keys=True, ensure_ascii=False)
                    if key not in seen:
                        seen.add(key)
                        rewired.append(b2)
                bridges = rewired
            if payload.get("bridges"):
                bridges.extend(dict(b) for b in payload["bridges"])
            meta["last_structural_operation"] = "FUSE"
            return {"modules": modules, "bridges": bridges, "meta": meta}
        if op == "PATCH_MODULE":
            module_id = str(payload["module_id"])
            if module_id not in modules:
                raise ValueError(f"module not found: {module_id}")
            modules[module_id] = {**modules[module_id], **dict(payload.get("patch", {}))}
            meta["last_structural_operation"] = "PATCH_MODULE"
            return {"modules": modules, "bridges": bridges, "meta": meta}
        raise ValueError("operation must be INIT, REPLACE, FISSION, FUSE, or PATCH_MODULE")

    def topology_apply(self, topology_id: str, expected_version: int, operation: str, payload: Mapping[str, Any], actor: str = "agent") -> Dict[str, Any]:
        topology_id = str(topology_id).strip()
        if not topology_id:
            raise ValueError("topology_id must not be empty")
        expected_version = int(expected_version)
        now = time.time()
        with self.s._lock, self.s.db:
            row = self.s.one("SELECT * FROM collective_topologies WHERE topology_id=?", (topology_id,))
            current_version = int(row["version"]) if row else 0
            if current_version != expected_version:
                raise ValueError(f"STALE_TOPOLOGY expected={expected_version} current={current_version}")
            before = json.loads(row["state_json"]) if row else {"modules": {}, "bridges": [], "meta": {}}
            if not row and operation.upper() not in {"INIT", "REPLACE"}:
                raise ValueError("new topology must start with INIT or REPLACE")
            after = self._apply_operation(before, operation, payload)
            to_version = current_version + 1
            txid = _stable_id("CTX", topology_id, current_version, to_version, operation, actor, now)
            after_json = json.dumps(after, sort_keys=True, ensure_ascii=False)
            before_json = json.dumps(before, sort_keys=True, ensure_ascii=False)
            self.s.db.execute("""INSERT INTO collective_topologies(topology_id,version,state_json,updated_at)
                   VALUES(?,?,?,?)
                   ON CONFLICT(topology_id) DO UPDATE SET version=excluded.version,state_json=excluded.state_json,updated_at=excluded.updated_at""", (topology_id, to_version, after_json, now))
            self.s.db.execute("INSERT INTO collective_topology_history VALUES(?,?,?,?,?,?,?,?,?)", (txid, topology_id, current_version, to_version, operation.upper(), before_json, after_json, actor, now))
        return {"status": "COMMITTED", "txid": txid, "topology_id": topology_id, "from_version": current_version, "version": to_version, "operation": operation.upper(), "state": after}

    def topology_rollback(self, topology_id: str, txid: str, expected_version: int, actor: str = "agent") -> Dict[str, Any]:
        topology_id = str(topology_id)
        expected_version = int(expected_version)
        now = time.time()
        with self.s._lock, self.s.db:
            current = self.s.one("SELECT * FROM collective_topologies WHERE topology_id=?", (topology_id,))
            if not current:
                raise ValueError("topology not found")
            current_version = int(current["version"])
            if current_version != expected_version:
                raise ValueError(f"STALE_TOPOLOGY expected={expected_version} current={current_version}")
            hist = self.s.one("SELECT * FROM collective_topology_history WHERE txid=? AND topology_id=?", (str(txid), topology_id))
            if not hist:
                raise ValueError("topology transaction not found")
            before = json.loads(hist["before_json"])
            to_version = current_version + 1
            rollback_id = _stable_id("CTX", topology_id, current_version, to_version, "ROLLBACK", txid, actor, now)
            current_json = current["state_json"]
            before_json = json.dumps(before, sort_keys=True, ensure_ascii=False)
            self.s.db.execute("UPDATE collective_topologies SET version=?,state_json=?,updated_at=? WHERE topology_id=?", (to_version, before_json, now, topology_id))
            self.s.db.execute("INSERT INTO collective_topology_history VALUES(?,?,?,?,?,?,?,?,?)", (rollback_id, topology_id, current_version, to_version, f"ROLLBACK:{txid}", current_json, before_json, actor, now))
        return {"status": "ROLLED_BACK", "txid": rollback_id, "rolled_back_txid": str(txid), "topology_id": topology_id, "from_version": current_version, "version": to_version, "state": before}

    def register_failure_antibody(self, signature: str, trigger: Mapping[str, Any] | None = None, detector: Mapping[str, Any] | None = None, repair: Mapping[str, Any] | None = None, evidence: Mapping[str, Any] | None = None, regression_refs: Sequence[str] | None = None, scope: str = "global", actor: str = "agent") -> Dict[str, Any]:
        signature = str(signature).strip()
        scope = str(scope).strip() or "global"
        if not signature:
            raise ValueError("signature must not be empty")
        now = time.time()
        aid = _stable_id("AB", scope, signature.lower())
        existing = self.s.one("SELECT * FROM failure_antibodies WHERE antibody_id=?", (aid,))
        created = float(existing["created_at"]) if existing else now
        hits = int(existing["hits"]) if existing else 0
        payload = (json.dumps(dict(trigger or {}), sort_keys=True, ensure_ascii=False), json.dumps(dict(detector or {}), sort_keys=True, ensure_ascii=False), json.dumps(dict(repair or {}), sort_keys=True, ensure_ascii=False), json.dumps(dict(evidence or {}), sort_keys=True, ensure_ascii=False), json.dumps(list(regression_refs or []), sort_keys=True, ensure_ascii=False))
        with self.s._lock, self.s.db:
            self.s.db.execute("""INSERT INTO failure_antibodies(antibody_id,signature,scope,trigger_json,detector_json,repair_json,evidence_json,regression_json,hits,actor,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(antibody_id) DO UPDATE SET
                     trigger_json=excluded.trigger_json,detector_json=excluded.detector_json,
                     repair_json=excluded.repair_json,evidence_json=excluded.evidence_json,
                     regression_json=excluded.regression_json,actor=excluded.actor,updated_at=excluded.updated_at""", (aid, signature, scope, *payload, hits, actor, created, now))
        return {"antibody_id": aid, "signature": signature, "scope": scope, "hits": hits, "persisted": True}

    def match_failure_antibodies(self, event: str, tags: Sequence[str] | None = None, scope: str | None = None, threshold: float = 0.35, limit: int = 10, record_hits: bool = True) -> Dict[str, Any]:
        event_tokens = _tokens([event, *(tags or [])])
        if not event_tokens:
            raise ValueError("event/tags must contain searchable tokens")
        threshold = _clamp(threshold)
        if limit < 1 or limit > 100:
            raise ValueError("limit must be in [1,100]")
        if scope:
            rows = self.s.rows("SELECT * FROM failure_antibodies WHERE scope IN (?, 'global') ORDER BY updated_at DESC", (str(scope),))
        else:
            rows = self.s.rows("SELECT * FROM failure_antibodies ORDER BY updated_at DESC")
        matches = []
        for row in rows:
            detector = json.loads(row["detector_json"])
            signature_tokens = _tokens(row["signature"])
            keyword_tokens = _tokens(detector.get("keywords", []))
            target = keyword_tokens or signature_tokens
            if not target:
                continue
            intersection = event_tokens & target
            coverage = len(intersection) / len(target)
            union = event_tokens | target
            jaccard = len(intersection) / len(union) if union else 0.0
            score = 0.75*coverage + 0.25*jaccard
            min_hits = max(1, int(detector.get("min_keyword_hits", 1)))
            if score < threshold or len(intersection) < min_hits:
                continue
            matches.append({"antibody_id": row["antibody_id"], "signature": row["signature"], "scope": row["scope"], "score": round(score, 6), "matched_tokens": sorted(intersection), "trigger": json.loads(row["trigger_json"]), "repair": json.loads(row["repair_json"]), "evidence": json.loads(row["evidence_json"]), "regression_refs": json.loads(row["regression_json"]), "prior_hits": int(row["hits"])})
        matches.sort(key=lambda x: (-x["score"], x["antibody_id"]))
        matches = matches[:limit]
        if record_hits and matches:
            now = time.time()
            with self.s._lock, self.s.db:
                for m in matches:
                    self.s.db.execute("UPDATE failure_antibodies SET hits=hits+1,updated_at=? WHERE antibody_id=?", (now, m["antibody_id"]))
                    m["hits"] = m.pop("prior_hits") + 1
        else:
            for m in matches:
                m["hits"] = m.pop("prior_hits")
        return {"matches": matches, "count": len(matches), "event_tokens": sorted(event_tokens), "law": "one diagnosed failure should immunize future relevant work through detector+repair+regression reuse"}
