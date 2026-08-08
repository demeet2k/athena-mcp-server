from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Dict, Mapping, Sequence

from .collective_runtime import CollectiveRuntime
from .collective_memory import CollectiveMemoryRuntime


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


RESOURCE_KEYS = (
    "tokens",
    "wall_time_s",
    "tool_calls",
    "compute_units",
    "retrieval_ops",
    "storage_bytes",
    "human_attention_min",
)

SCALES = ("token", "artifact", "module", "domain", "system")

ELDER_WEIGHTS = {
    "reuse_success": 0.20,
    "prediction_success": 0.25,
    "repair_success": 0.20,
    "regression_success": 0.20,
    "generalization_success": 0.15,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_budget_observations(
 obs_id TEXT PRIMARY KEY,
 run_key TEXT NOT NULL,
 scope TEXT NOT NULL,
 resources_json TEXT NOT NULL,
 budget_json TEXT NOT NULL,
 outcome_json TEXT NOT NULL,
 pressure REAL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_collective_budget_scope ON collective_budget_observations(scope,created_at);

CREATE TABLE IF NOT EXISTS collective_runtime_usage(
 usage_id TEXT PRIMARY KEY,
 scope TEXT NOT NULL,
 tool_name TEXT NOT NULL,
 wall_time_s REAL NOT NULL,
 status TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_collective_runtime_usage_scope ON collective_runtime_usage(scope,created_at);

CREATE TABLE IF NOT EXISTS collective_policy_states(
 scope TEXT PRIMARY KEY,
 version INTEGER NOT NULL,
 bias REAL NOT NULL,
 weights_json TEXT NOT NULL,
 n INTEGER NOT NULL,
 base_learning_rate REAL NOT NULL,
 l2 REAL NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_policy_history(
 txid TEXT PRIMARY KEY,
 scope TEXT NOT NULL,
 from_version INTEGER NOT NULL,
 to_version INTEGER NOT NULL,
 operation TEXT NOT NULL,
 before_json TEXT NOT NULL,
 after_json TEXT NOT NULL,
 features_json TEXT NOT NULL,
 reward REAL,
 prediction REAL,
 error REAL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_collective_policy_history ON collective_policy_history(scope,to_version);

CREATE TABLE IF NOT EXISTS collective_elder_stats(
 entity_id TEXT NOT NULL,
 scope TEXT NOT NULL,
 observations INTEGER NOT NULL,
 sums_json TEXT NOT NULL,
 counts_json TEXT NOT NULL,
 contradiction_sum REAL NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(entity_id,scope)
);

CREATE TABLE IF NOT EXISTS collective_antibody_evolution(
 antibody_id TEXT PRIMARY KEY,
 family_id TEXT NOT NULL,
 parent_id TEXT,
 status TEXT NOT NULL,
 successes INTEGER NOT NULL,
 failures INTEGER NOT NULL,
 false_positives INTEGER NOT NULL,
 regression_passes INTEGER NOT NULL,
 regression_failures INTEGER NOT NULL,
 expires_at REAL,
 last_outcome TEXT,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_antibody_family ON collective_antibody_evolution(family_id,updated_at);
"""


class CollectiveLearningRuntime:
    """V3: measured resource metabolism and bounded self-learning ecology.

    This layer learns only through explicit observations and versioned writes.
    It never rewrites canonical semantic/Git state on its own.
    """

    def __init__(self, store: Any, collective: CollectiveRuntime, memory: CollectiveMemoryRuntime):
        self.s = store
        self.collective = collective
        self.memory = memory
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> Dict[str, Any]:
        counts = {
            "budget_observations": self.s.one("SELECT COUNT(*) AS n FROM collective_budget_observations")["n"],
            "runtime_usage_events": self.s.one("SELECT COUNT(*) AS n FROM collective_runtime_usage")["n"],
            "policy_scopes": self.s.one("SELECT COUNT(*) AS n FROM collective_policy_states")["n"],
            "elder_entities": self.s.one("SELECT COUNT(*) AS n FROM collective_elder_stats")["n"],
            "antibody_evolution_records": self.s.one("SELECT COUNT(*) AS n FROM collective_antibody_evolution")["n"],
        }
        return {
            "version": "COLLECTIVE_RUNTIME_V3",
            "persistent_surfaces": counts,
            "resource_keys": list(RESOURCE_KEYS),
            "pheromone_scales": list(SCALES),
            "operators": [
                "record_budget", "budget_summary",
                "policy_state", "policy_score", "policy_update", "policy_rollback",
                "counterfactual_simulate",
                "elder_observe", "elder_rank",
                "antibody_record_outcome", "antibody_evolve", "antibody_select",
                "pheromone_multiscale_reinforce", "pheromone_multiscale_field",
            ],
            "laws": [
                "MEASURED_COST != ESTIMATED_COST; unavailable token/compute telemetry remains UNKNOWN rather than fabricated",
                "POLICY_LEARNING is bounded, versioned, explicit, and rollbackable",
                "COUNTERFACTUAL simulation ranks candidates without committing topology",
                "ELDER_AUTHORITY derives from repeated measured success, not age or recency alone",
                "ANTIBODY_MATCH != CAUSAL_PROOF; outcomes update reliability and variant selection",
                "PHEROMONE transport is multi-scale and attenuated; local success does not globally saturate the graph",
            ],
        }

    @staticmethod
    def _resources(values: Mapping[str, Any] | None) -> Dict[str, float]:
        values = values or {}
        out: Dict[str, float] = {}
        for k in RESOURCE_KEYS:
            v = values.get(k)
            if v is not None:
                out[k] = max(0.0, float(v))
        return out

    def record_runtime_usage(self, tool_name: str, wall_time_s: float, status: str = "OK", scope: str = "global") -> None:
        now = time.time()
        uid = _stable_id("USE", scope, tool_name, now, wall_time_s, status)
        with self.s._lock, self.s.db:
            self.s.db.execute(
                "INSERT INTO collective_runtime_usage VALUES(?,?,?,?,?,?)",
                (uid, str(scope), str(tool_name), max(0.0, float(wall_time_s)), str(status), now),
            )

    def record_budget(
        self,
        run_key: str,
        resources: Mapping[str, Any],
        budget: Mapping[str, Any] | None = None,
        outcome: Mapping[str, Any] | None = None,
        scope: str = "global",
        actor: str = "agent",
    ) -> Dict[str, Any]:
        run_key = str(run_key).strip()
        if not run_key:
            raise ValueError("run_key must not be empty")
        r = self._resources(resources)
        b = self._resources(budget)
        ratios: Dict[str, float] = {}
        over = []
        for k, cap in b.items():
            if cap <= 0:
                continue
            ratio = r.get(k, 0.0) / cap
            ratios[k] = ratio
            if ratio > 1.0:
                over.append(k)
        pressure = (sum(min(1.0, x) for x in ratios.values()) / len(ratios)) if ratios else None
        out = dict(outcome or {})
        useful = out.get("useful_output")
        efficiency = None
        if useful is not None and pressure is not None:
            efficiency = max(0.0, float(useful)) / (1.0 + pressure)
        now = time.time()
        oid = _stable_id("BUD", scope, run_key, now)
        with self.s._lock, self.s.db:
            self.s.db.execute(
                "INSERT INTO collective_budget_observations VALUES(?,?,?,?,?,?,?,?,?)",
                (
                    oid, run_key, str(scope),
                    json.dumps(r, sort_keys=True),
                    json.dumps(b, sort_keys=True),
                    json.dumps(out, sort_keys=True, ensure_ascii=False),
                    pressure, str(actor), now,
                ),
            )
        return {
            "obs_id": oid,
            "run_key": run_key,
            "resources": r,
            "budget": b,
            "budget_ratios": {k: round(v, 6) for k, v in ratios.items()},
            "budget_pressure": None if pressure is None else round(pressure, 6),
            "over_budget": sorted(over),
            "efficiency": None if efficiency is None else round(efficiency, 6),
            "law": "record actual resource dimensions when observable; never infer unavailable token/compute usage",
        }

    def budget_summary(self, scope: str = "global", limit: int = 200) -> Dict[str, Any]:
        if limit < 1 or limit > 5000:
            raise ValueError("limit must be in [1,5000]")
        rows = self.s.rows(
            "SELECT * FROM collective_budget_observations WHERE scope=? ORDER BY created_at DESC LIMIT ?",
            (str(scope), int(limit)),
        )
        totals = {k: 0.0 for k in RESOURCE_KEYS}
        pressures = []
        for row in rows:
            r = json.loads(row["resources_json"])
            for k, v in r.items():
                if k in totals:
                    totals[k] += float(v)
            if row["pressure"] is not None:
                pressures.append(float(row["pressure"]))
        usage = self.s.rows(
            "SELECT tool_name,wall_time_s,status FROM collective_runtime_usage WHERE scope=? ORDER BY created_at DESC LIMIT ?",
            (str(scope), int(limit)),
        )
        tool_time: Dict[str, float] = {}
        for row in usage:
            tool_time[row["tool_name"]] = tool_time.get(row["tool_name"], 0.0) + float(row["wall_time_s"])
        return {
            "scope": str(scope),
            "budget_observations": len(rows),
            "resource_totals": {k: round(v, 6) for k, v in totals.items()},
            "mean_budget_pressure": None if not pressures else round(sum(pressures) / len(pressures), 6),
            "runtime_usage_events": len(usage),
            "tool_wall_time_s": {k: round(v, 6) for k, v in sorted(tool_time.items(), key=lambda x: (-x[1], x[0]))},
            "law": "tool-call and wall-time telemetry are automatic; token/compute dimensions require an observable client-supplied measurement",
        }

    def _policy_row(self, scope: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_policy_states WHERE scope=?", (scope,))
        if row:
            return row
        now = time.time()
        return {
            "scope": scope, "version": 0, "bias": 0.5, "weights_json": "{}",
            "n": 0, "base_learning_rate": 0.18, "l2": 0.01,
            "created_at": now, "updated_at": 0.0,
        }

    @staticmethod
    def _feature_map(features: Mapping[str, Any]) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for k, v in features.items():
            try:
                out[str(k)] = max(-1.0, min(1.0, float(v)))
            except (TypeError, ValueError):
                continue
        return out

    def policy_state(self, scope: str = "global") -> Dict[str, Any]:
        row = self._policy_row(str(scope))
        return {
            "scope": str(scope),
            "version": int(row["version"]),
            "bias": round(float(row["bias"]), 6),
            "weights": json.loads(row["weights_json"]),
            "n": int(row["n"]),
            "base_learning_rate": round(float(row["base_learning_rate"]), 6),
            "l2": round(float(row["l2"]), 6),
            "reliability": round(int(row["n"]) / (int(row["n"]) + 20.0), 6) if int(row["n"]) else 0.0,
            "updated_at": float(row["updated_at"]),
        }

    def policy_score(self, features: Mapping[str, Any], scope: str = "global") -> Dict[str, Any]:
        f = self._feature_map(features)
        state = self.policy_state(scope)
        weights = {str(k): float(v) for k, v in state["weights"].items()}
        contributions = {k: weights.get(k, 0.0) * v for k, v in f.items()}
        z = float(state["bias"]) + sum(contributions.values())
        score = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))
        return {
            "scope": str(scope),
            "version": state["version"],
            "score": round(score, 6),
            "reliability": state["reliability"],
            "features": f,
            "contributions": {k: round(v, 6) for k, v in sorted(contributions.items())},
            "law": "learned policy is advisory; authority scales with measured sample reliability",
        }

    def policy_update(
        self,
        expected_version: int,
        features: Mapping[str, Any],
        observed_reward: float,
        scope: str = "global",
        actor: str = "agent",
        learning_rate: float | None = None,
        l2: float | None = None,
    ) -> Dict[str, Any]:
        scope = str(scope)
        reward = _clamp(observed_reward)
        f = self._feature_map(features)
        now = time.time()
        with self.s._lock, self.s.db:
            row = self._policy_row(scope)
            current_version = int(row["version"])
            if current_version != int(expected_version):
                raise ValueError(f"STALE_POLICY expected={expected_version} current={current_version}")
            before = self.policy_state(scope)
            weights = {str(k): float(v) for k, v in before["weights"].items()}
            bias = float(before["bias"])
            z = bias + sum(weights.get(k, 0.0) * v for k, v in f.items())
            pred = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))
            err = reward - pred
            n = int(before["n"])
            base_eta = max(0.001, min(0.5, float(learning_rate if learning_rate is not None else row["base_learning_rate"])))
            reg = max(0.0, min(0.25, float(l2 if l2 is not None else row["l2"])))
            eta = base_eta / math.sqrt(n + 1.0)
            grad = err * pred * (1.0 - pred)
            bias = max(-3.0, min(3.0, bias + eta * grad))
            keys = set(weights) | set(f)
            for k in keys:
                w = weights.get(k, 0.0)
                x = f.get(k, 0.0)
                weights[k] = max(-3.0, min(3.0, w + eta * (grad * x - reg * w)))
            to_version = current_version + 1
            after = {
                "scope": scope,
                "version": to_version,
                "bias": bias,
                "weights": weights,
                "n": n + 1,
                "base_learning_rate": base_eta,
                "l2": reg,
            }
            txid = _stable_id("POL", scope, current_version, to_version, now, actor)
            created = float(row["created_at"]) if current_version else now
            self.s.db.execute(
                """INSERT INTO collective_policy_states(scope,version,bias,weights_json,n,base_learning_rate,l2,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(scope) DO UPDATE SET
                     version=excluded.version,bias=excluded.bias,weights_json=excluded.weights_json,n=excluded.n,
                     base_learning_rate=excluded.base_learning_rate,l2=excluded.l2,updated_at=excluded.updated_at""",
                (scope, to_version, bias, json.dumps(weights, sort_keys=True), n + 1, base_eta, reg, created, now),
            )
            self.s.db.execute(
                "INSERT INTO collective_policy_history VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    txid, scope, current_version, to_version, "UPDATE",
                    json.dumps(before, sort_keys=True),
                    json.dumps(after, sort_keys=True),
                    json.dumps(f, sort_keys=True),
                    reward, pred, err, str(actor), now,
                ),
            )
        return {
            "status": "COMMITTED",
            "txid": txid,
            "scope": scope,
            "from_version": current_version,
            "version": to_version,
            "prediction": round(pred, 6),
            "observed_reward": round(reward, 6),
            "error": round(err, 6),
            "effective_learning_rate": round(eta, 6),
            "state": self.policy_state(scope),
        }

    def policy_rollback(self, txid: str, expected_version: int, scope: str = "global", actor: str = "agent") -> Dict[str, Any]:
        scope = str(scope)
        now = time.time()
        with self.s._lock, self.s.db:
            row = self.s.one("SELECT * FROM collective_policy_states WHERE scope=?", (scope,))
            if not row:
                raise ValueError("policy state not found")
            current_version = int(row["version"])
            if current_version != int(expected_version):
                raise ValueError(f"STALE_POLICY expected={expected_version} current={current_version}")
            hist = self.s.one("SELECT * FROM collective_policy_history WHERE txid=? AND scope=?", (str(txid), scope))
            if not hist:
                raise ValueError("policy transaction not found")
            before = json.loads(hist["before_json"])
            to_version = current_version + 1
            restored = {
                "scope": scope,
                "version": to_version,
                "bias": float(before["bias"]),
                "weights": dict(before["weights"]),
                "n": int(before["n"]),
                "base_learning_rate": float(before["base_learning_rate"]),
                "l2": float(before["l2"]),
            }
            rid = _stable_id("POL", scope, current_version, to_version, "ROLLBACK", txid, now)
            current = self.policy_state(scope)
            self.s.db.execute(
                "UPDATE collective_policy_states SET version=?,bias=?,weights_json=?,n=?,base_learning_rate=?,l2=?,updated_at=? WHERE scope=?",
                (to_version, restored["bias"], json.dumps(restored["weights"], sort_keys=True), restored["n"], restored["base_learning_rate"], restored["l2"], now, scope),
            )
            self.s.db.execute(
                "INSERT INTO collective_policy_history VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    rid, scope, current_version, to_version, f"ROLLBACK:{txid}",
                    json.dumps(current, sort_keys=True),
                    json.dumps(restored, sort_keys=True),
                    "{}", None, None, None, str(actor), now,
                ),
            )
        return {"status": "ROLLED_BACK", "txid": rid, "rolled_back_txid": str(txid), "scope": scope, "version": to_version, "state": self.policy_state(scope)}

    def counterfactual_simulate(
        self,
        candidates: Sequence[Mapping[str, Any]],
        context: Mapping[str, Any] | None = None,
        scope: str = "global",
    ) -> Dict[str, Any]:
        if not candidates:
            raise ValueError("candidates must not be empty")
        context_f = self._feature_map(context or {})
        reliability = self.policy_state(scope)["reliability"]
        ranked = []
        for i, c in enumerate(candidates):
            cid = str(c.get("id", f"candidate_{i}"))
            configuration = dict(c.get("configuration", {}))
            evaluation = self.collective.evaluate(configuration)
            base_rgo = float(evaluation["return_on_group_organization"])
            calibrated = float(self.memory.calibrate_rgo(base_rgo, scope)["calibrated_rgo"])
            features = {**context_f, **self._feature_map(c.get("features", {}))}
            features.setdefault("workers_fraction", min(1.0, float(configuration.get("workers", 1)) / 256.0))
            features.setdefault("edge_density", float(evaluation["edge_density"]))
            features.setdefault("reserve_fraction", float(configuration.get("reserve_fraction", 0.15)))
            pscore = float(self.policy_score(features, scope)["score"])
            risk = _clamp(c.get("risk", context_f.get("risk", 0.0)))
            budget_pressure = _clamp(c.get("budget_pressure", context_f.get("budget_pressure", 0.0)))
            learned_mix = 0.60 * calibrated + 0.40 * pscore
            combined = (1.0 - reliability) * calibrated + reliability * learned_mix
            utility = max(0.0, combined - 0.15 * risk - 0.10 * budget_pressure)
            ranked.append({
                "id": cid,
                "predicted_utility": round(utility, 6),
                "base_rgo": round(base_rgo, 6),
                "calibrated_rgo": round(calibrated, 6),
                "policy_score": round(pscore, 6),
                "policy_reliability": reliability,
                "risk_penalty": round(0.15 * risk, 6),
                "budget_penalty": round(0.10 * budget_pressure, 6),
                "evaluation": evaluation,
            })
        ranked.sort(key=lambda x: (-x["predicted_utility"], x["id"]))
        return {
            "decision": "SIMULATE_ONLY",
            "winner": ranked[0]["id"],
            "ranked_candidates": ranked,
            "law": "counterfactual ranking never commits topology; execute/measure before policy promotion",
        }

    def _elder_state(self, entity_id: str, scope: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_elder_stats WHERE entity_id=? AND scope=?", (entity_id, scope))
        if not row:
            return {
                "entity_id": entity_id, "scope": scope, "observations": 0,
                "sums": {}, "counts": {}, "contradiction_sum": 0.0,
                "created_at": time.time(), "updated_at": 0.0,
            }
        return {
            "entity_id": entity_id, "scope": scope, "observations": int(row["observations"]),
            "sums": json.loads(row["sums_json"]), "counts": json.loads(row["counts_json"]),
            "contradiction_sum": float(row["contradiction_sum"]),
            "created_at": float(row["created_at"]), "updated_at": float(row["updated_at"]),
        }

    @staticmethod
    def _elder_authority(state: Mapping[str, Any]) -> Dict[str, Any]:
        sums = dict(state["sums"])
        counts = dict(state["counts"])
        posterior = {}
        weighted = 0.0
        total_weight = 0.0
        total_count = 0
        for k, w in ELDER_WEIGHTS.items():
            c = int(counts.get(k, 0))
            s = float(sums.get(k, 0.0))
            p = (s + 1.0) / (c + 2.0)
            posterior[k] = p
            weighted += w * p
            total_weight += w
            total_count += c
        base = weighted / total_weight if total_weight else 0.5
        obs = max(1, int(state.get("observations", 0)))
        contradiction = float(state.get("contradiction_sum", 0.0)) / obs
        confidence = total_count / (total_count + 10.0) if total_count else 0.0
        score = _clamp((1.0 - confidence) * 0.5 + confidence * (base - 0.30 * contradiction))
        return {
            "authority": round(score, 6),
            "confidence": round(confidence, 6),
            "posterior_dimensions": {k: round(v, 6) for k, v in posterior.items()},
            "contradiction_rate": round(contradiction, 6),
            "evidence_events": total_count,
        }

    def elder_observe(self, entity_id: str, outcomes: Mapping[str, Any], scope: str = "global", actor: str = "agent") -> Dict[str, Any]:
        entity_id = str(entity_id).strip()
        scope = str(scope)
        if not entity_id:
            raise ValueError("entity_id must not be empty")
        current = self._elder_state(entity_id, scope)
        sums = dict(current["sums"])
        counts = dict(current["counts"])
        for k in ELDER_WEIGHTS:
            if k in outcomes:
                v = _clamp(outcomes[k])
                sums[k] = float(sums.get(k, 0.0)) + v
                counts[k] = int(counts.get(k, 0)) + 1
        contradiction = float(current["contradiction_sum"]) + _clamp(outcomes.get("contradiction", 0.0))
        now = time.time()
        observations = int(current["observations"]) + 1
        with self.s._lock, self.s.db:
            self.s.db.execute(
                """INSERT INTO collective_elder_stats VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(entity_id,scope) DO UPDATE SET
                     observations=excluded.observations,sums_json=excluded.sums_json,counts_json=excluded.counts_json,
                     contradiction_sum=excluded.contradiction_sum,actor=excluded.actor,updated_at=excluded.updated_at""",
                (entity_id, scope, observations, json.dumps(sums, sort_keys=True), json.dumps(counts, sort_keys=True), contradiction, str(actor), current["created_at"], now),
            )
        state = self._elder_state(entity_id, scope)
        return {**state, **self._elder_authority(state), "law": "seniority is repeated measured usefulness with contradiction penalty, not age alone"}

    def elder_rank(self, scope: str = "global", limit: int = 50, min_observations: int = 1) -> Dict[str, Any]:
        if limit < 1 or limit > 500:
            raise ValueError("limit must be in [1,500]")
        rows = self.s.rows(
            "SELECT entity_id FROM collective_elder_stats WHERE scope=? AND observations>=? ORDER BY updated_at DESC",
            (str(scope), max(1, int(min_observations))),
        )
        ranked = []
        for row in rows:
            state = self._elder_state(row["entity_id"], str(scope))
            ranked.append({**state, **self._elder_authority(state)})
        ranked.sort(key=lambda x: (-x["authority"], -x["confidence"], x["entity_id"]))
        return {"scope": str(scope), "elders": ranked[:limit], "count": min(len(ranked), limit), "law": "elder authority must remain evidence-backed and defeasible"}

    def _ensure_antibody_evolution(self, antibody_id: str, actor: str = "agent", family_id: str | None = None, parent_id: str | None = None, expires_at: float | None = None) -> Dict[str, Any]:
        base = self.s.one("SELECT antibody_id FROM failure_antibodies WHERE antibody_id=?", (antibody_id,))
        if not base:
            raise ValueError("failure antibody not found")
        row = self.s.one("SELECT * FROM collective_antibody_evolution WHERE antibody_id=?", (antibody_id,))
        if row:
            return row
        now = time.time()
        family = family_id or antibody_id
        with self.s._lock, self.s.db:
            self.s.db.execute(
                "INSERT INTO collective_antibody_evolution VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (antibody_id, family, parent_id, "ACTIVE", 0, 0, 0, 0, 0, expires_at, None, str(actor), now, now),
            )
        return self.s.one("SELECT * FROM collective_antibody_evolution WHERE antibody_id=?", (antibody_id,))

    def antibody_record_outcome(self, antibody_id: str, outcome: str, actor: str = "agent") -> Dict[str, Any]:
        outcome = str(outcome).upper()
        valid = {"SUCCESS", "FAILURE", "FALSE_POSITIVE", "REGRESSION_PASS", "REGRESSION_FAIL"}
        if outcome not in valid:
            raise ValueError(f"outcome must be one of {sorted(valid)}")
        self._ensure_antibody_evolution(str(antibody_id), actor)
        column = {
            "SUCCESS": "successes",
            "FAILURE": "failures",
            "FALSE_POSITIVE": "false_positives",
            "REGRESSION_PASS": "regression_passes",
            "REGRESSION_FAIL": "regression_failures",
        }[outcome]
        now = time.time()
        with self.s._lock, self.s.db:
            self.s.db.execute(
                f"UPDATE collective_antibody_evolution SET {column}={column}+1,last_outcome=?,actor=?,updated_at=? WHERE antibody_id=?",
                (outcome, str(actor), now, str(antibody_id)),
            )
        row = self.s.one("SELECT * FROM collective_antibody_evolution WHERE antibody_id=?", (str(antibody_id),))
        trials = int(row["successes"]) + int(row["failures"]) + int(row["false_positives"])
        reliability = (int(row["successes"]) + 1.0) / (trials + 2.0)
        false_rate = int(row["false_positives"]) / max(1, trials)
        regression_rate = (int(row["regression_passes"]) + 1.0) / (int(row["regression_passes"]) + int(row["regression_failures"]) + 2.0)
        status = "ACTIVE"
        if row["expires_at"] is not None and float(row["expires_at"]) <= now:
            status = "EXPIRED"
        elif trials >= 4 and false_rate >= 0.5:
            status = "WATCH"
        elif trials >= 6 and reliability < 0.30:
            status = "RETIRED"
        with self.s._lock, self.s.db:
            self.s.db.execute("UPDATE collective_antibody_evolution SET status=? WHERE antibody_id=?", (status, str(antibody_id)))
        return {
            "antibody_id": str(antibody_id),
            "family_id": row["family_id"],
            "status": status,
            "outcome": outcome,
            "trials": trials,
            "reliability": round(reliability, 6),
            "false_positive_rate": round(false_rate, 6),
            "regression_reliability": round(regression_rate, 6),
        }

    def antibody_evolve(
        self,
        parent_id: str,
        signature: str,
        detector: Mapping[str, Any],
        repair: Mapping[str, Any],
        trigger: Mapping[str, Any] | None = None,
        evidence: Mapping[str, Any] | None = None,
        regression_refs: Sequence[str] | None = None,
        ttl_hours: float | None = None,
        scope: str = "global",
        actor: str = "agent",
    ) -> Dict[str, Any]:
        parent_stats = self._ensure_antibody_evolution(str(parent_id), actor)
        reg = self.memory.register_failure_antibody(signature, trigger, detector, repair, evidence, regression_refs, scope, actor)
        child = str(reg["antibody_id"])
        if child == str(parent_id):
            raise ValueError("variant must have a distinct normalized signature")
        expires_at = None if ttl_hours is None else time.time() + max(0.0, float(ttl_hours)) * 3600.0
        self._ensure_antibody_evolution(child, actor, parent_stats["family_id"], str(parent_id), expires_at)
        return {"status": "VARIANT_REGISTERED", "family_id": parent_stats["family_id"], "parent_id": str(parent_id), "antibody_id": child, "expires_at": expires_at}

    def antibody_select(self, event: str, tags: Sequence[str] | None = None, scope: str | None = None, threshold: float = 0.25, limit: int = 10) -> Dict[str, Any]:
        base = self.memory.match_failure_antibodies(event, tags, scope, threshold, max(limit * 3, limit), record_hits=False)
        now = time.time()
        ranked = []
        for m in base["matches"]:
            row = self._ensure_antibody_evolution(m["antibody_id"])
            trials = int(row["successes"]) + int(row["failures"]) + int(row["false_positives"])
            rel = (int(row["successes"]) + 1.0) / (trials + 2.0)
            reg_rel = (int(row["regression_passes"]) + 1.0) / (int(row["regression_passes"]) + int(row["regression_failures"]) + 2.0)
            expired = row["expires_at"] is not None and float(row["expires_at"]) <= now
            status = "EXPIRED" if expired else row["status"]
            status_factor = {"ACTIVE": 1.0, "WATCH": 0.65, "RETIRED": 0.15, "EXPIRED": 0.0}.get(status, 0.5)
            score = float(m["score"]) * (0.55 + 0.30 * rel + 0.15 * reg_rel) * status_factor
            ranked.append({**m, "family_id": row["family_id"], "variant_status": status, "empirical_reliability": round(rel, 6), "regression_reliability": round(reg_rel, 6), "selection_score": round(score, 6)})
        ranked.sort(key=lambda x: (-x["selection_score"], x["antibody_id"]))
        return {"matches": ranked[:limit], "count": min(len(ranked), limit), "law": "variant selection combines semantic match with observed repair/regression reliability and expiry"}

    def pheromone_multiscale_reinforce(
        self,
        source_scale: str,
        coordinates: Mapping[str, Any],
        observations: Mapping[str, Any],
        upward_decay: float = 0.72,
        downward_decay: float = 0.55,
        age: float | None = None,
        evaporation_rate: float = 0.08,
        deposit_gain: float = 0.35,
        actor: str = "agent",
    ) -> Dict[str, Any]:
        source_scale = str(source_scale).lower()
        if source_scale not in SCALES:
            raise ValueError(f"source_scale must be one of {SCALES}")
        coords = {str(k).lower(): str(v) for k, v in coordinates.items() if str(k).lower() in SCALES and str(v)}
        if source_scale not in coords:
            raise ValueError("coordinates must include source_scale")
        up = _clamp(upward_decay)
        down = _clamp(downward_decay)
        src_idx = SCALES.index(source_scale)
        updates = []
        for scale, key in coords.items():
            idx = SCALES.index(scale)
            dist = abs(idx - src_idx)
            attenuation = (up ** dist) if idx > src_idx else (down ** dist)
            gain = _clamp(float(deposit_gain) * attenuation)
            route = f"MSP/{scale}/{key}"
            res = self.memory.pheromone_reinforce(route, observations, age, evaporation_rate, gain, actor)
            updates.append({"scale": scale, "coordinate": key, "attenuation": round(attenuation, 6), **res})
        updates.sort(key=lambda x: SCALES.index(x["scale"]))
        return {"source_scale": source_scale, "updates": updates, "law": "reinforcement propagates across declared scales with distance attenuation; no implicit global saturation"}

    def pheromone_multiscale_field(self, min_score: float = 0.0, limit: int = 500) -> Dict[str, Any]:
        field = self.memory.pheromone_field(None, limit, min_score)
        scales: Dict[str, list] = {s: [] for s in SCALES}
        for row in field["routes"]:
            route = str(row["route_key"])
            if not route.startswith("MSP/"):
                continue
            parts = route.split("/", 2)
            if len(parts) != 3 or parts[1] not in scales:
                continue
            scales[parts[1]].append({**row, "coordinate": parts[2]})
        return {"scales": scales, "count": sum(len(v) for v in scales.values()), "law": "multi-scale pheromone is a fiber over token/artifact/module/domain/system coordinates"}
