from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .collective_runtime import CollectiveRuntime
from .collective_growth import CollectiveGrowthRuntime
from .collective_memory import CollectiveMemoryRuntime
from .collective_learning import CollectiveLearningRuntime, RESOURCE_KEYS, SCALES


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _signed_clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


V4_RESOURCE_KEYS = RESOURCE_KEYS + (
    "cpu_time_s", "gpu_time_s", "energy_j", "memory_peak_mb", "network_bytes",
)

BIN_THRESHOLDS = (0.33, 0.67)

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_bandit_arms(
 regime TEXT NOT NULL,
 arm_id TEXT NOT NULL,
 n INTEGER NOT NULL,
 reward_sum REAL NOT NULL,
 precision_json TEXT NOT NULL,
 moment_json TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(regime,arm_id)
);
CREATE TABLE IF NOT EXISTS collective_bandit_observations(
 obs_id TEXT PRIMARY KEY,
 regime TEXT NOT NULL,
 arm_id TEXT NOT NULL,
 reward REAL NOT NULL,
 features_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bandit_obs_regime ON collective_bandit_observations(regime,created_at);

CREATE TABLE IF NOT EXISTS collective_credit_events(
 credit_id TEXT PRIMARY KEY,
 outcome_key TEXT NOT NULL,
 regime TEXT NOT NULL,
 intervention_id TEXT NOT NULL,
 outcome_delta REAL NOT NULL,
 raw_effect REAL NOT NULL,
 causal_confidence REAL NOT NULL,
 assigned_credit REAL NOT NULL,
 status TEXT NOT NULL,
 design_json TEXT NOT NULL,
 evidence_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_credit_intervention ON collective_credit_events(regime,intervention_id,created_at);

CREATE TABLE IF NOT EXISTS collective_worker_cost_observations(
 obs_id TEXT PRIMARY KEY,
 worker_id TEXT NOT NULL,
 task_id TEXT NOT NULL,
 scope TEXT NOT NULL,
 resources_json TEXT NOT NULL,
 budget_json TEXT NOT NULL,
 useful_output REAL,
 pressure REAL,
 efficiency REAL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_worker_cost_stats(
 worker_id TEXT NOT NULL,
 scope TEXT NOT NULL,
 n INTEGER NOT NULL,
 resource_sums_json TEXT NOT NULL,
 pressure_sum REAL NOT NULL,
 pressure_n INTEGER NOT NULL,
 useful_sum REAL NOT NULL,
 useful_n INTEGER NOT NULL,
 efficiency_sum REAL NOT NULL,
 efficiency_n INTEGER NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(worker_id,scope)
);

CREATE TABLE IF NOT EXISTS collective_diffusion_stats(
 source_scale TEXT NOT NULL,
 target_scale TEXT NOT NULL,
 n INTEGER NOT NULL,
 reward_sum REAL NOT NULL,
 evidence_weight_sum REAL NOT NULL,
 causal_weight_sum REAL NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(source_scale,target_scale)
);
CREATE TABLE IF NOT EXISTS collective_diffusion_observations(
 obs_id TEXT PRIMARY KEY,
 source_scale TEXT NOT NULL,
 target_scale TEXT NOT NULL,
 transfer_utility REAL NOT NULL,
 evidence_weight REAL NOT NULL,
 causal_confidence REAL NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS collective_regression_runs(
 run_id TEXT PRIMARY KEY,
 antibody_id TEXT NOT NULL,
 regression_ref TEXT NOT NULL,
 status TEXT NOT NULL,
 returncode INTEGER,
 duration_s REAL NOT NULL,
 stdout_tail TEXT NOT NULL,
 stderr_tail TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_regression_antibody ON collective_regression_runs(antibody_id,created_at);

CREATE TABLE IF NOT EXISTS collective_projection_sagas(
 projection_id TEXT PRIMARY KEY,
 topology_id TEXT NOT NULL,
 topology_version INTEGER NOT NULL,
 expected_semantic_eid TEXT,
 expected_git_head TEXT,
 plan_json TEXT NOT NULL,
 status TEXT NOT NULL,
 semantic_eid_after TEXT,
 git_head_after TEXT,
 error TEXT,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
"""


class CollectiveEcologyRuntime:
    """V4: uncertainty-aware, credit-aware, budget-scheduled collective ecology.

    This layer deliberately distinguishes exploration score from truth,
    attribution from causal proof, simulation from mutation, projection saga
    from atomic distributed transaction, and measured resources from unavailable
    telemetry.
    """

    def __init__(self, store: Any, collective: CollectiveRuntime, growth: CollectiveGrowthRuntime, memory: CollectiveMemoryRuntime, learning: CollectiveLearningRuntime):
        self.s = store
        self.collective = collective
        self.growth = growth
        self.memory = memory
        self.learning = learning
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> Dict[str, Any]:
        q = lambda table: self.s.one(f"SELECT COUNT(*) AS n FROM {table}")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V4",
            "persistent_surfaces": {
                "bandit_arms": q("collective_bandit_arms"),
                "bandit_observations": q("collective_bandit_observations"),
                "credit_events": q("collective_credit_events"),
                "worker_cost_observations": q("collective_worker_cost_observations"),
                "diffusion_observations": q("collective_diffusion_observations"),
                "regression_runs": q("collective_regression_runs"),
                "projection_sagas": q("collective_projection_sagas"),
            },
            "resource_keys": list(V4_RESOURCE_KEYS),
            "operators": [
                "resolve_regime", "bandit_select", "bandit_observe", "assign_credit", "credit_summary",
                "worker_cost_observe", "budget_schedule", "diffusion_observe", "diffusion_matrix",
                "pheromone_adaptive_reinforce", "execute_antibody_regressions", "rollout_simulate",
                "projection_plan", "projection_prepare", "projection_status", "projection_mark",
            ],
            "laws": [
                "EXPLORATION_SCORE != EVIDENCE; uncertainty can justify experiments but cannot promote claims",
                "ATTRIBUTION != CAUSAL_PROOF; causal confidence is carried explicitly",
                "REGIME_POLICY uses local evidence plus reliability-weighted cross-regime transfer",
                "BUDGET_SCHEDULING prefers measured efficient workers but marks unknown resource dimensions UNKNOWN",
                "REGRESSION_EXECUTION is restricted to repository-owned unittest witnesses; no arbitrary command execution",
                "DIFFUSION coefficients learn from observed transfer utility but remain uncertainty-bearing",
                "ROLLOUT simulation uses explicit transitions only and never commits topology",
                "JSPACE projection is a recoverable saga, not a falsely atomic SQLite+Git transaction",
            ],
        }

    @staticmethod
    def _bin(value: Any) -> str:
        v = _clamp(value if value is not None else 0.5)
        if v < BIN_THRESHOLDS[0]: return "L"
        if v < BIN_THRESHOLDS[1]: return "M"
        return "H"

    def resolve_regime(self, signals: Mapping[str, Any], domain: str | None = None) -> Dict[str, Any]:
        normalized = self.collective._signals(signals)
        scores = self.collective.form_scores(normalized)
        form = max(scores, key=lambda k: (scores[k], k))
        regime = (f"REGIME/{form}/H:{self._bin(normalized['hardness'])}/U:{self._bin(normalized['uncertainty'])}"
                  f"/C:{self._bin(normalized['coupling'])}/D:{self._bin(normalized['divisibility'])}/V:{self._bin(normalized['volatility'])}")
        if domain:
            clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(domain).strip())[:80]
            regime += f"/DOMAIN:{clean or 'UNKNOWN'}"
        return {"regime": regime, "form": form, "form_scores": scores, "signals": normalized,
                "law": "task regimes are deterministic observable partitions, not hidden identities"}

    def _bandit_row(self, regime: str, arm_id: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_bandit_arms WHERE regime=? AND arm_id=?", (str(regime), str(arm_id)))
        return row or {"regime": str(regime), "arm_id": str(arm_id), "n": 0, "reward_sum": 0.0,
                       "precision_json": "{}", "moment_json": "{}", "created_at": 0.0, "updated_at": 0.0}

    def _posterior(self, regime: str, arm_id: str, features: Mapping[str, Any]) -> Dict[str, Any]:
        f = {"__bias__": 1.0, **self.learning._feature_map(features)}
        row = self._bandit_row(regime, arm_id)
        precision = {str(k): max(1e-6, float(v)) for k, v in json.loads(row["precision_json"]).items()}
        moment = {str(k): float(v) for k, v in json.loads(row["moment_json"]).items()}
        mean_raw = variance_raw = 0.0
        contributions = {}
        for k, x in f.items():
            a = precision.get(k, 1.0)
            b = moment.get(k, 0.5 if k == "__bias__" else 0.0)
            theta = b / a
            contributions[k] = theta * float(x)
            mean_raw += contributions[k]
            variance_raw += float(x) * float(x) / a
        scale = max(1.0, math.sqrt(len(f)))
        return {"regime": str(regime), "arm_id": str(arm_id), "n": int(row["n"]),
                "mean": _clamp(mean_raw / scale), "uncertainty": min(1.0, math.sqrt(max(0.0, variance_raw)) / scale),
                "contributions": contributions}

    def _hierarchical_bandit_score(self, regime: str, arm_id: str, features: Mapping[str, Any], exploration_alpha: float, transfer_tau: float, policy_scope: str = "global") -> Dict[str, Any]:
        local = self._posterior(regime, arm_id, features)
        global_p = self._posterior("GLOBAL", arm_id, features)
        local_r = local["n"] / (local["n"] + max(1e-6, transfer_tau)) if local["n"] else 0.0
        if global_p["n"] == 0 and local["n"] == 0:
            baseline = self.learning.policy_score(features, policy_scope)
            mean = float(baseline["score"]); uncertainty = max(0.25, 1.0 - float(baseline["reliability"])); source = "V3_POLICY_PRIOR"
        elif global_p["n"] == 0:
            mean, uncertainty, source = local["mean"], local["uncertainty"], "LOCAL"
        elif local["n"] == 0:
            mean, uncertainty, source = global_p["mean"], global_p["uncertainty"], "GLOBAL_TRANSFER"
        else:
            mean = local_r * local["mean"] + (1.0 - local_r) * global_p["mean"]
            uncertainty = math.sqrt(local_r * local_r * local["uncertainty"] ** 2 + (1.0 - local_r) ** 2 * global_p["uncertainty"] ** 2)
            source = "HIERARCHICAL_TRANSFER"
        alpha = max(0.0, float(exploration_alpha))
        return {"arm_id": str(arm_id), "regime": str(regime), "mean_reward": round(mean, 6), "uncertainty": round(uncertainty, 6),
                "lower_bound": round(_clamp(mean - alpha * uncertainty), 6), "upper_confidence_bound": round(_clamp(mean + alpha * uncertainty), 6),
                "local_reliability": round(local_r, 6), "local_n": local["n"], "global_n": global_p["n"], "source": source}

    def bandit_select(self, arms: Sequence[Mapping[str, Any]], context: Mapping[str, Any], regime: str | None = None, signals: Mapping[str, Any] | None = None, exploration_alpha: float = 0.35, transfer_tau: float = 8.0, policy_scope: str = "global") -> Dict[str, Any]:
        if not arms: raise ValueError("arms must not be empty")
        resolved = regime or self.resolve_regime(signals or {})["regime"]
        context_f = self.learning._feature_map(context)
        ranked = []
        for i, arm in enumerate(arms):
            aid = str(arm.get("id", f"arm_{i}"))
            features = {**context_f, **self.learning._feature_map(arm.get("features", {}))}
            if arm.get("configuration"):
                ev = self.collective.evaluate(arm["configuration"])
                features.setdefault("base_rgo", float(ev["return_on_group_organization"]))
                features.setdefault("edge_density", float(ev["edge_density"]))
                features.setdefault("workers_fraction", min(1.0, float(ev["workers"]) / 256.0))
            ranked.append({**self._hierarchical_bandit_score(resolved, aid, features, exploration_alpha, transfer_tau, policy_scope), "features": features})
        ranked.sort(key=lambda x: (-x["upper_confidence_bound"], -x["mean_reward"], x["arm_id"]))
        return {"decision": "EXPLORE_OR_EXPLOIT", "regime": resolved, "winner": ranked[0]["arm_id"], "ranked_arms": ranked,
                "exploration_alpha": round(max(0.0, float(exploration_alpha)), 6),
                "law": "upper confidence can choose an experiment; it cannot certify the arm as true or globally optimal"}

    def _bandit_update_row(self, regime: str, arm_id: str, features: Mapping[str, Any], reward: float, weight: float = 1.0) -> None:
        f = {"__bias__": 1.0, **self.learning._feature_map(features)}
        row = self._bandit_row(regime, arm_id)
        precision = {str(k): float(v) for k, v in json.loads(row["precision_json"]).items()}
        moment = {str(k): float(v) for k, v in json.loads(row["moment_json"]).items()}
        w = max(0.0, float(weight))
        for k, x in f.items():
            precision[k] = precision.get(k, 1.0) + w * float(x) * float(x)
            moment[k] = moment.get(k, 0.5 if k == "__bias__" else 0.0) + w * float(x) * reward
        now = time.time(); created = float(row["created_at"]) if int(row["n"]) else now
        self.s.db.execute("""INSERT INTO collective_bandit_arms(regime,arm_id,n,reward_sum,precision_json,moment_json,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(regime,arm_id) DO UPDATE SET n=excluded.n,reward_sum=excluded.reward_sum,
            precision_json=excluded.precision_json,moment_json=excluded.moment_json,updated_at=excluded.updated_at""",
            (str(regime), str(arm_id), int(row["n"]) + 1, float(row["reward_sum"]) + reward * w,
             json.dumps(precision, sort_keys=True), json.dumps(moment, sort_keys=True), created, now))

    def bandit_observe(self, arm_id: str, reward: float, features: Mapping[str, Any], regime: str, actor: str = "agent", global_transfer_weight: float = 1.0) -> Dict[str, Any]:
        arm_id, regime = str(arm_id).strip(), str(regime).strip()
        if not arm_id or not regime: raise ValueError("arm_id and regime must not be empty")
        r = _clamp(reward); f = self.learning._feature_map(features); now = time.time(); oid = _stable_id("BANDIT", regime, arm_id, now, actor)
        with self.s._lock, self.s.db:
            self._bandit_update_row(regime, arm_id, f, r, 1.0)
            if regime != "GLOBAL" and global_transfer_weight > 0:
                self._bandit_update_row("GLOBAL", arm_id, f, r, min(1.0, max(0.0, float(global_transfer_weight))))
            self.s.db.execute("INSERT INTO collective_bandit_observations VALUES(?,?,?,?,?,?,?)", (oid, regime, arm_id, r, json.dumps(f, sort_keys=True), str(actor), now))
        return {"obs_id": oid, "regime": regime, "arm_id": arm_id, "reward": round(r, 6),
                "posterior": self._hierarchical_bandit_score(regime, arm_id, f, 0.0, 8.0),
                "law": "bandit state updates only from explicit observed reward, never from its own UCB prediction"}

    @staticmethod
    def _design_confidence(design: Mapping[str, Any], intervention: Mapping[str, Any], has_counterfactual: bool) -> float:
        randomized = 1.0 if design.get("randomized") else 0.0; controlled = 1.0 if design.get("control_group") else 0.0
        direct = _clamp(intervention.get("direct_measurement", design.get("direct_measurement", 0.0)))
        isolated = _clamp(intervention.get("temporal_isolation", design.get("temporal_isolation", 0.0)))
        replication = min(1.0, max(0.0, float(design.get("replications", 0.0))) / 5.0)
        conf = 0.10 + 0.22 * randomized + 0.22 * controlled + 0.16 * direct + 0.10 * isolated + 0.10 * replication
        if has_counterfactual: conf += 0.10
        else: conf = min(conf, 0.45)
        return _clamp(conf)

    def assign_credit(self, outcome_key: str, outcome_delta: float, interventions: Sequence[Mapping[str, Any]], design: Mapping[str, Any] | None = None, regime: str = "GLOBAL", actor: str = "agent") -> Dict[str, Any]:
        if not interventions: raise ValueError("interventions must not be empty")
        delta = _signed_clamp(outcome_delta); design = dict(design or {}); rows = []; total_credit = 0.0; now = time.time()
        for i, intervention in enumerate(interventions):
            iid = str(intervention.get("id", f"intervention_{i}")); has_cf = intervention.get("counterfactual_without_delta") is not None
            if has_cf:
                raw = delta - _signed_clamp(intervention["counterfactual_without_delta"]); evidence_mode = "COUNTERFACTUAL_DIFFERENCE"
            else:
                raw = delta * _clamp(intervention.get("evidence_weight", 0.5)) * _signed_clamp(intervention.get("direction", 1.0)); evidence_mode = "WEIGHTED_ASSOCIATION"
            conf = self._design_confidence(design, intervention, has_cf); credit = _signed_clamp(raw * conf)
            status = "CAUSAL_SUPPORTED" if conf >= 0.75 and has_cf else ("QUASI_CAUSAL" if conf >= 0.50 else "ASSOCIATIONAL")
            evidence = {"mode": evidence_mode, "counterfactual_without_delta": intervention.get("counterfactual_without_delta"), "evidence_weight": intervention.get("evidence_weight")}
            cid = _stable_id("CREDIT", outcome_key, regime, iid, now, i)
            with self.s._lock, self.s.db:
                self.s.db.execute("INSERT INTO collective_credit_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (cid, str(outcome_key), str(regime), iid, delta, raw, conf, credit, status,
                     json.dumps(design, sort_keys=True, ensure_ascii=False), json.dumps(evidence, sort_keys=True, ensure_ascii=False), str(actor), now))
            total_credit += credit
            rows.append({"credit_id": cid, "intervention_id": iid, "raw_effect": round(raw, 6), "causal_confidence": round(conf, 6),
                         "assigned_credit": round(credit, 6), "status": status, "evidence_mode": evidence_mode})
        return {"outcome_key": str(outcome_key), "outcome_delta": round(delta, 6), "regime": str(regime), "credits": rows,
                "assigned_total": round(total_credit, 6), "unattributed_residual": round(delta - total_credit, 6),
                "law": "credit preserves uncertainty and residual; weak designs remain associational rather than being relabeled causal"}

    def credit_summary(self, intervention_id: str | None = None, regime: str | None = None, limit: int = 500) -> Dict[str, Any]:
        if limit < 1 or limit > 5000: raise ValueError("limit must be in [1,5000]")
        where, args = [], []
        if intervention_id is not None: where.append("intervention_id=?"); args.append(str(intervention_id))
        if regime is not None: where.append("regime=?"); args.append(str(regime))
        sql = "SELECT * FROM collective_credit_events" + ((" WHERE " + " AND ".join(where)) if where else "") + " ORDER BY created_at DESC LIMIT ?"; args.append(int(limit))
        rows = self.s.rows(sql, tuple(args)); by = {}
        for r in rows:
            d = by.setdefault(r["intervention_id"], {"n": 0, "credit_sum": 0.0, "confidence_sum": 0.0}); d["n"] += 1
            d["credit_sum"] += float(r["assigned_credit"]); d["confidence_sum"] += float(r["causal_confidence"])
        summary = [{"intervention_id": iid, "n": d["n"], "mean_credit": round(d["credit_sum"] / d["n"], 6),
                    "mean_causal_confidence": round(d["confidence_sum"] / d["n"], 6)} for iid, d in by.items()]
        summary.sort(key=lambda x: (-abs(x["mean_credit"]), -x["mean_causal_confidence"], x["intervention_id"]))
        return {"rows": len(rows), "interventions": summary}

    @staticmethod
    def _resource_map(values: Mapping[str, Any] | None) -> Dict[str, float]:
        return {k: max(0.0, float(v)) for k, v in (values or {}).items() if k in V4_RESOURCE_KEYS and v is not None}

    def _worker_stats(self, worker_id: str, scope: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_worker_cost_stats WHERE worker_id=? AND scope=?", (str(worker_id), str(scope)))
        if not row:
            return {"worker_id": str(worker_id), "scope": str(scope), "n": 0, "resource_sums": {}, "pressure_sum": 0.0, "pressure_n": 0,
                    "useful_sum": 0.0, "useful_n": 0, "efficiency_sum": 0.0, "efficiency_n": 0, "created_at": time.time(), "updated_at": 0.0}
        return {"worker_id": row["worker_id"], "scope": row["scope"], "n": int(row["n"]), "resource_sums": json.loads(row["resource_sums_json"]),
                "pressure_sum": float(row["pressure_sum"]), "pressure_n": int(row["pressure_n"]), "useful_sum": float(row["useful_sum"]),
                "useful_n": int(row["useful_n"]), "efficiency_sum": float(row["efficiency_sum"]), "efficiency_n": int(row["efficiency_n"]),
                "created_at": float(row["created_at"]), "updated_at": float(row["updated_at"])}

    def worker_cost_observe(self, worker_id: str, task_id: str, resources: Mapping[str, Any], budget: Mapping[str, Any] | None = None, useful_output: float | None = None, scope: str = "global", actor: str = "agent") -> Dict[str, Any]:
        worker_id, task_id, scope = str(worker_id), str(task_id), str(scope); r = self._resource_map(resources); b = self._resource_map(budget)
        ratios = {k: r.get(k, 0.0) / cap for k, cap in b.items() if cap > 0}; pressure = sum(min(1.0, v) for v in ratios.values()) / len(ratios) if ratios else None
        useful = None if useful_output is None else _clamp(useful_output); efficiency = None if useful is None or pressure is None else useful / (1.0 + pressure)
        now = time.time(); oid = _stable_id("WCOST", worker_id, task_id, scope, now)
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_worker_cost_observations VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (oid, worker_id, task_id, scope, json.dumps(r, sort_keys=True), json.dumps(b, sort_keys=True), useful, pressure, efficiency, str(actor), now))
            st = self._worker_stats(worker_id, scope); sums = dict(st["resource_sums"])
            for k, v in r.items(): sums[k] = float(sums.get(k, 0.0)) + float(v)
            created = st["created_at"] if st["n"] else now
            self.s.db.execute("""INSERT INTO collective_worker_cost_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(worker_id,scope) DO UPDATE SET n=excluded.n,resource_sums_json=excluded.resource_sums_json,
                pressure_sum=excluded.pressure_sum,pressure_n=excluded.pressure_n,useful_sum=excluded.useful_sum,useful_n=excluded.useful_n,
                efficiency_sum=excluded.efficiency_sum,efficiency_n=excluded.efficiency_n,updated_at=excluded.updated_at""",
                (worker_id, scope, st["n"] + 1, json.dumps(sums, sort_keys=True), st["pressure_sum"] + (pressure or 0.0), st["pressure_n"] + (1 if pressure is not None else 0),
                 st["useful_sum"] + (useful or 0.0), st["useful_n"] + (1 if useful is not None else 0), st["efficiency_sum"] + (efficiency or 0.0),
                 st["efficiency_n"] + (1 if efficiency is not None else 0), created, now))
        return {"obs_id": oid, "worker_id": worker_id, "task_id": task_id, "resources": r, "budget": b,
                "budget_pressure": None if pressure is None else round(pressure, 6), "efficiency": None if efficiency is None else round(efficiency, 6),
                "law": "future scheduling may reuse measured worker cost; unavailable dimensions remain unknown"}

    def _worker_profile(self, worker: Mapping[str, Any], scope: str) -> Dict[str, Any]:
        wid = str(worker.get("id")); st = self._worker_stats(wid, scope); explicit = self._resource_map(worker.get("estimated_resources"))
        history = {k: float(v) / st["n"] for k, v in st["resource_sums"].items()} if st["n"] else {}; estimate = explicit or history
        source = "EXPLICIT" if explicit else ("MEASURED_HISTORY" if history else "UNKNOWN")
        eff = (st["efficiency_sum"] + 1.0) / (st["efficiency_n"] + 2.0) if st["efficiency_n"] else 0.5
        return {"worker_id": wid, "estimate": estimate, "cost_source": source, "efficiency": _clamp(eff),
                "cost_reliability": st["n"] / (st["n"] + 8.0) if st["n"] else 0.0, "stats": st}

    def budget_schedule(self, tasks: Sequence[Mapping[str, Any]], workers: Sequence[Mapping[str, Any]], remaining_budget: Mapping[str, Any], scope: str = "global", max_assignments_per_worker: int = 1, alpha: float = 1.0, beta: float = 1.0) -> Dict[str, Any]:
        if not tasks or not workers: raise ValueError("tasks and workers must not be empty")
        if max_assignments_per_worker < 1 or max_assignments_per_worker > 16: raise ValueError("max_assignments_per_worker must be in [1,16]")
        budget = self._resource_map(remaining_budget); profiles = {str(w.get("id")): self._worker_profile(w, scope) for w in workers}; worker_raw = {str(w.get("id")): dict(w) for w in workers}; slots = {wid: 0 for wid in worker_raw}
        normalized_tasks = []
        for i, task in enumerate(tasks):
            tid = str(task.get("id", f"task_{i}")); utility = _clamp(task.get("utility", 0.5)); gap = _clamp(task.get("gap", 0.5)); bridge = _clamp(task.get("bridge_value", 0.5)); saturation = _clamp(task.get("saturation", 0.0)); urgency = _clamp(task.get("urgency", 0.5))
            normalized_tasks.append({"id": tid, "demand": utility * gap * max(0.05, bridge) * (1.0 - saturation) * (0.5 + 0.5 * urgency), "required": {str(x) for x in task.get("required_capabilities", [])}})
        assignments, unfilled = [], []
        for task in sorted(normalized_tasks, key=lambda x: (x["demand"], x["id"]), reverse=True):
            candidates = []
            for wid, raw in worker_raw.items():
                if slots[wid] >= max_assignments_per_worker: continue
                caps = {str(x) for x in raw.get("capabilities", [])}; fit = 1.0 if not task["required"] else len(task["required"] & caps) / len(task["required"])
                if fit <= 0: continue
                availability = 1.0 - _clamp(raw.get("load", 0.0)); p = profiles[wid]; infeasible, unknown = [], []
                for k, cap in budget.items():
                    if k not in p["estimate"]: unknown.append(k)
                    elif p["estimate"][k] > cap + 1e-12: infeasible.append(k)
                if infeasible: continue
                uncertainty_penalty = 0.72 if unknown else (0.85 + 0.15 * p["cost_reliability"]); efficiency_factor = 0.5 + 0.5 * p["efficiency"]
                score = task["demand"] ** max(0.0, float(alpha)) * max(0.01, fit) ** max(0.0, float(beta)) * availability * efficiency_factor * uncertainty_penalty
                candidates.append((score, fit, availability, wid, unknown))
            if not candidates: unfilled.append({"task": task["id"], "reason": "NO_BUDGET_FEASIBLE_CAPABILITY"}); continue
            score, fit, availability, wid, unknown = max(candidates, key=lambda x: (x[0], x[1], x[2], x[3])); p = profiles[wid]
            for k in list(budget):
                if k in p["estimate"]: budget[k] = max(0.0, budget[k] - p["estimate"][k])
            slots[wid] += 1
            assignments.append({"task": task["id"], "worker": wid, "score": round(score, 6), "demand": round(task["demand"], 6), "fit": round(fit, 6), "availability": round(availability, 6),
                                "empirical_efficiency": round(p["efficiency"], 6), "cost_source": p["cost_source"], "unknown_constrained_resources": unknown, "estimated_resources": p["estimate"]})
        return {"assignments": assignments, "unfilled": unfilled, "remaining_budget": {k: round(v, 6) for k, v in budget.items()}, "worker_slots": slots,
                "law": "schedule by demand*fit*availability*measured-efficiency subject to observable budget feasibility; unknown cost is penalized, not fabricated"}

    @staticmethod
    def _diffusion_prior(source_scale: str, target_scale: str) -> float:
        if source_scale not in SCALES or target_scale not in SCALES: raise ValueError(f"scales must be in {SCALES}")
        si, ti = SCALES.index(source_scale), SCALES.index(target_scale); d = abs(ti - si)
        return 1.0 if d == 0 else ((0.72 ** d) if ti > si else (0.55 ** d))

    def diffusion_coefficient(self, source_scale: str, target_scale: str, prior_strength: float = 4.0) -> Dict[str, Any]:
        source_scale, target_scale = str(source_scale).lower(), str(target_scale).lower(); prior = self._diffusion_prior(source_scale, target_scale)
        row = self.s.one("SELECT * FROM collective_diffusion_stats WHERE source_scale=? AND target_scale=?", (source_scale, target_scale))
        if not row: return {"source_scale": source_scale, "target_scale": target_scale, "coefficient": round(prior, 6), "prior": round(prior, 6), "n": 0, "evidence_weight": 0.0, "causal_weight": 0.0, "reliability": 0.0}
        ew = float(row["evidence_weight_sum"]); ps = max(0.0, prior_strength); coefficient = (ps * prior + float(row["reward_sum"])) / (ps + ew) if ps + ew else prior
        return {"source_scale": source_scale, "target_scale": target_scale, "coefficient": round(_clamp(coefficient), 6), "prior": round(prior, 6), "n": int(row["n"]),
                "evidence_weight": round(ew, 6), "causal_weight": round(float(row["causal_weight_sum"]) / max(1, int(row["n"])), 6), "reliability": round(ew / (ew + ps) if ew else 0.0, 6)}

    def diffusion_observe(self, source_scale: str, target_scale: str, transfer_utility: float, evidence_weight: float = 1.0, causal_confidence: float = 0.0, actor: str = "agent") -> Dict[str, Any]:
        source_scale, target_scale = str(source_scale).lower(), str(target_scale).lower(); self._diffusion_prior(source_scale, target_scale)
        u, ew, cc = _clamp(transfer_utility), _clamp(evidence_weight), _clamp(causal_confidence); now = time.time(); oid = _stable_id("DIFF", source_scale, target_scale, now, actor)
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_diffusion_observations VALUES(?,?,?,?,?,?,?,?)", (oid, source_scale, target_scale, u, ew, cc, str(actor), now))
            row = self.s.one("SELECT * FROM collective_diffusion_stats WHERE source_scale=? AND target_scale=?", (source_scale, target_scale))
            if row: n, rs, ews, cws, created = int(row["n"]) + 1, float(row["reward_sum"]) + u * ew, float(row["evidence_weight_sum"]) + ew, float(row["causal_weight_sum"]) + cc, float(row["created_at"])
            else: n, rs, ews, cws, created = 1, u * ew, ew, cc, now
            self.s.db.execute("""INSERT INTO collective_diffusion_stats VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source_scale,target_scale) DO UPDATE SET
                n=excluded.n,reward_sum=excluded.reward_sum,evidence_weight_sum=excluded.evidence_weight_sum,causal_weight_sum=excluded.causal_weight_sum,updated_at=excluded.updated_at""",
                (source_scale, target_scale, n, rs, ews, cws, created, now))
        return {"obs_id": oid, **self.diffusion_coefficient(source_scale, target_scale), "transfer_utility": round(u, 6)}

    def diffusion_matrix(self) -> Dict[str, Any]:
        return {"scales": list(SCALES), "matrix": {src: {dst: self.diffusion_coefficient(src, dst) for dst in SCALES} for src in SCALES},
                "law": "learned diffusion is shrunk toward distance priors; observational transfer utility does not become causal authority automatically"}

    def pheromone_adaptive_reinforce(self, source_scale: str, coordinates: Mapping[str, Any], observations: Mapping[str, Any], age: float | None = None, evaporation_rate: float = 0.08, deposit_gain: float = 0.35, actor: str = "agent") -> Dict[str, Any]:
        source_scale = str(source_scale).lower(); coords = {str(k).lower(): str(v) for k, v in coordinates.items() if str(k).lower() in SCALES and str(v)}
        if source_scale not in coords: raise ValueError("coordinates must include source_scale")
        updates = []
        for scale, coordinate in coords.items():
            coef = self.diffusion_coefficient(source_scale, scale); gain = _clamp(float(deposit_gain) * float(coef["coefficient"])); route = f"MSP/{scale}/{coordinate}"
            updates.append({"scale": scale, "coordinate": coordinate, "learned_diffusion": coef, "effective_deposit_gain": round(gain, 6),
                            **self.memory.pheromone_reinforce(route, observations, age, evaporation_rate, gain, actor)})
        updates.sort(key=lambda x: SCALES.index(x["scale"]))
        return {"source_scale": source_scale, "updates": updates, "law": "cross-scale reinforcement uses learned shrinkage coefficients; missing coordinates are never synthesized"}

    _REGRESSION_REF = re.compile(r"^(tests/[A-Za-z0-9_./-]+\.py)::([A-Za-z_][A-Za-z0-9_]*)::([A-Za-z_][A-Za-z0-9_]*)$")

    @staticmethod
    def _repo_root() -> Path: return Path(__file__).resolve().parent.parent

    def _run_regression_ref(self, antibody_id: str, ref: str, timeout_s: float, actor: str) -> Dict[str, Any]:
        now = time.time(); m = self._REGRESSION_REF.fullmatch(str(ref))
        if not m or ".." in m.group(1).split("/"):
            result = {"status": "INVALID_REF", "returncode": None, "duration_s": 0.0, "stdout_tail": "", "stderr_tail": "reference must be tests/*.py::TestCase::test_method"}
        else:
            rel, cls, method = m.groups(); root = self._repo_root(); target = (root / rel).resolve()
            try: target.relative_to(root); contained = True
            except ValueError: contained = False
            if not contained or not target.exists() or not target.is_file():
                result = {"status": "INVALID_REF", "returncode": None, "duration_s": 0.0, "stdout_tail": "", "stderr_tail": "test path is absent or outside repository root"}
            else:
                script = ("import importlib.util,sys,unittest,pathlib;" "p=pathlib.Path(sys.argv[1]).resolve();" "sys.path.insert(0,str(p.parents[1]));"
                          "spec=importlib.util.spec_from_file_location('athena_regression_target',str(p));" "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
                          "c=getattr(m,sys.argv[2]);" "suite=unittest.TestSuite([c(sys.argv[3])]);" "r=unittest.TextTestRunner(verbosity=2).run(suite);" "raise SystemExit(0 if r.wasSuccessful() else 1)")
                env = os.environ.copy(); env["PYTHONNOUSERSITE"] = "1"; env["PYTHONHASHSEED"] = "0"; started = time.monotonic()
                try:
                    p = subprocess.run([sys.executable, "-I", "-c", script, str(target), cls, method], cwd=str(root), env=env, text=True, capture_output=True,
                                       timeout=max(0.1, min(60.0, float(timeout_s))), shell=False); duration = time.monotonic() - started
                    result = {"status": "PASS" if p.returncode == 0 else "FAIL", "returncode": int(p.returncode), "duration_s": duration, "stdout_tail": p.stdout[-4000:], "stderr_tail": p.stderr[-4000:]}
                except subprocess.TimeoutExpired as e:
                    duration = time.monotonic() - started; out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or ""); err = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
                    result = {"status": "TIMEOUT", "returncode": None, "duration_s": duration, "stdout_tail": out[-4000:], "stderr_tail": err[-4000:]}
                except Exception as e:
                    result = {"status": "ERROR", "returncode": None, "duration_s": time.monotonic() - started, "stdout_tail": "", "stderr_tail": str(e)[-4000:]}
        rid = _stable_id("REG", antibody_id, ref, now, result["status"])
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_regression_runs VALUES(?,?,?,?,?,?,?,?,?,?)",
                (rid, str(antibody_id), str(ref), result["status"], result["returncode"], float(result["duration_s"]), result["stdout_tail"], result["stderr_tail"], str(actor), now))
        return {"run_id": rid, "antibody_id": str(antibody_id), "regression_ref": str(ref), **result}

    def execute_antibody_regressions(self, antibody_id: str, timeout_s: float = 20.0, max_refs: int = 8, record_outcome: bool = True, actor: str = "agent") -> Dict[str, Any]:
        if max_refs < 1 or max_refs > 32: raise ValueError("max_refs must be in [1,32]")
        row = self.s.one("SELECT regression_json FROM failure_antibodies WHERE antibody_id=?", (str(antibody_id),))
        if not row: raise ValueError("failure antibody not found")
        refs = json.loads(row["regression_json"])[:max_refs]
        if not refs: return {"antibody_id": str(antibody_id), "status": "NO_WITNESSES", "runs": [], "law": "no regression claim is made when no executable witness exists"}
        runs = [self._run_regression_ref(str(antibody_id), ref, timeout_s, actor) for ref in refs]; aggregate = "PASS" if all(x["status"] == "PASS" for x in runs) else "FAIL"
        update = self.learning.antibody_record_outcome(str(antibody_id), "REGRESSION_PASS" if aggregate == "PASS" else "REGRESSION_FAIL", actor) if record_outcome else None
        return {"antibody_id": str(antibody_id), "status": aggregate, "runs": runs, "antibody_update": update,
                "restriction": "repository-owned tests/*.py::TestCase::test_method only; subprocess, no shell, hard timeout"}

    def rollout_simulate(self, trajectories: Sequence[Mapping[str, Any]], initial_context: Mapping[str, Any] | None = None, regime: str = "GLOBAL", discount: float = 0.92, exploration_alpha: float = 0.20, max_steps: int = 16) -> Dict[str, Any]:
        if not trajectories: raise ValueError("trajectories must not be empty")
        if max_steps < 1 or max_steps > 64: raise ValueError("max_steps must be in [1,64]")
        gamma = _clamp(discount); results = []
        for ti, trajectory in enumerate(trajectories):
            tid = str(trajectory.get("id", f"trajectory_{ti}")); context = self.learning._feature_map(initial_context or {}); expected_total = lower_total = upper_total = 0.0; step_rows = []
            for step_i, step in enumerate(list(trajectory.get("steps", []))[:max_steps]):
                sid = str(step.get("id", f"{tid}:step_{step_i}")); candidate = {"id": sid, "configuration": dict(step.get("configuration", {})),
                    "features": {**context, **self.learning._feature_map(step.get("features", {}))}, "risk": step.get("risk", context.get("risk", 0.0)),
                    "budget_pressure": step.get("budget_pressure", context.get("budget_pressure", 0.0))}
                cf = self.learning.counterfactual_simulate([candidate], context, regime); base = float(cf["ranked_candidates"][0]["predicted_utility"]); arm_id = str(step.get("arm_id", sid))
                band = self._hierarchical_bandit_score(regime, arm_id, candidate["features"], exploration_alpha, 8.0, regime); band_rel = (band["local_n"] + band["global_n"]) / (band["local_n"] + band["global_n"] + 12.0)
                mean = (1.0 - band_rel) * base + band_rel * float(band["mean_reward"]); unc = float(band["uncertainty"]); lo = _clamp(mean - exploration_alpha * unc); hi = _clamp(mean + exploration_alpha * unc); weight = gamma ** step_i
                expected_total += weight * mean; lower_total += weight * lo; upper_total += weight * hi
                step_rows.append({"step": step_i, "id": sid, "arm_id": arm_id, "expected_utility": round(mean, 6), "uncertainty": round(unc, 6), "lower": round(lo, 6), "upper": round(hi, 6), "discount_weight": round(weight, 6)})
                for k, dv in self.learning._feature_map(step.get("context_delta", {})).items(): context[k] = max(-1.0, min(1.0, context.get(k, 0.0) + dv))
                context["previous_predicted_utility"] = mean
            results.append({"id": tid, "expected_return": round(expected_total, 6), "lower_return": round(lower_total, 6), "upper_return": round(upper_total, 6), "steps": step_rows, "terminal_context": context})
        results.sort(key=lambda x: (-x["upper_return"], -x["expected_return"], x["id"]))
        return {"decision": "SIMULATE_ONLY", "winner": results[0]["id"], "ranked_trajectories": results, "discount": round(gamma, 6), "dynamics": "EXPLICIT_CONTEXT_DELTA_ONLY",
                "law": "multi-step rollouts expose uncertainty bands and never invent transition dynamics or commit topology"}

    def projection_plan(self, topology_id: str, expected_version: int | None = None) -> Dict[str, Any]:
        topo = self.memory.topology_get(str(topology_id))
        if not topo["exists"]: raise ValueError("topology not found")
        if expected_version is not None and int(expected_version) != int(topo["version"]): raise ValueError(f"STALE_TOPOLOGY expected={expected_version} current={topo['version']}")
        state = topo["state"]; edges = []
        for mid, rec in sorted(state.get("modules", {}).items()):
            if rec.get("fission_parent"): edges.append({"src": str(mid), "relation": "FISSIONED_FROM", "dst": str(rec["fission_parent"])})
            for parent in rec.get("fused_from", []) or []: edges.append({"src": str(mid), "relation": "FUSED_FROM", "dst": str(parent)})
            if rec.get("active", False): edges.append({"src": str(topology_id), "relation": "HAS_ACTIVE_MODULE", "dst": str(mid)})
        for bridge in state.get("bridges", []) or []:
            src, dst = bridge.get("src", bridge.get("a")), bridge.get("dst", bridge.get("b"))
            if src is not None and dst is not None: edges.append({"src": str(src), "relation": str(bridge.get("relation", "COLLECTIVE_BRIDGE")), "dst": str(dst)})
        unique = {(e["src"], e["relation"], e["dst"]): e for e in edges}; edges = [unique[k] for k in sorted(unique)]; digest = hashlib.sha256(json.dumps(edges, sort_keys=True).encode()).hexdigest()
        return {"topology_id": str(topology_id), "topology_version": int(topo["version"]), "edges": edges, "edge_count": len(edges), "plan_digest": digest,
                "law": "projection is derived from explicit topology lineage/bridges; planning alone does not mutate JSPACE"}

    def projection_prepare(self, topology_id: str, expected_topology_version: int, expected_semantic_eid: str | None, expected_git_head: str | None, actor: str = "agent") -> Dict[str, Any]:
        plan = self.projection_plan(topology_id, expected_topology_version); now = time.time(); pid = _stable_id("PROJ", topology_id, expected_topology_version, expected_semantic_eid, expected_git_head, plan["plan_digest"], now)
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_projection_sagas VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (pid, str(topology_id), int(expected_topology_version), expected_semantic_eid, expected_git_head, json.dumps(plan, sort_keys=True, ensure_ascii=False),
                 "PREPARED", None, None, None, str(actor), now, now))
        return {"projection_id": pid, "status": "PREPARED", **plan}

    def projection_status(self, projection_id: str) -> Dict[str, Any]:
        row = self.s.one("SELECT * FROM collective_projection_sagas WHERE projection_id=?", (str(projection_id),))
        if not row: raise ValueError("projection saga not found")
        return {"projection_id": row["projection_id"], "topology_id": row["topology_id"], "topology_version": int(row["topology_version"]),
                "expected_semantic_eid": row["expected_semantic_eid"], "expected_git_head": row["expected_git_head"], "plan": json.loads(row["plan_json"]),
                "status": row["status"], "semantic_eid_after": row["semantic_eid_after"], "git_head_after": row["git_head_after"], "error": row["error"],
                "actor": row["actor"], "created_at": float(row["created_at"]), "updated_at": float(row["updated_at"])}

    def projection_mark(self, projection_id: str, status: str, semantic_eid_after: str | None = None, git_head_after: str | None = None, error: str | None = None) -> Dict[str, Any]:
        valid = {"PREPARED", "SEMANTIC_APPLIED", "GIT_COMMITTED", "COMPLETED", "ABORTED", "COMPENSATION_REQUIRED"}; status = str(status).upper()
        if status not in valid: raise ValueError(f"status must be one of {sorted(valid)}")
        now = time.time()
        with self.s._lock, self.s.db:
            if not self.s.one("SELECT projection_id FROM collective_projection_sagas WHERE projection_id=?", (str(projection_id),)): raise ValueError("projection saga not found")
            self.s.db.execute("""UPDATE collective_projection_sagas SET status=?,semantic_eid_after=COALESCE(?,semantic_eid_after),
                git_head_after=COALESCE(?,git_head_after),error=?,updated_at=? WHERE projection_id=?""",
                (status, semantic_eid_after, git_head_after, error, now, str(projection_id)))
        return self.projection_status(projection_id)
