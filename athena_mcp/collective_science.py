from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .collective_runtime import CollectiveRuntime
from .collective_growth import CollectiveGrowthRuntime
from .collective_memory import CollectiveMemoryRuntime
from .collective_learning import CollectiveLearningRuntime
from .collective_ecology import CollectiveEcologyRuntime, V4_RESOURCE_KEYS
from .identity import event_id, digest


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _signed(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def _entropy(probs: Sequence[float]) -> float:
    out = 0.0
    for p in probs:
        if p > 1e-15:
            out -= p * math.log(p, 2)
    return out


def _normal_z(coverage: float) -> float:
    c = _clamp(coverage, 0.50, 0.999)
    pts = [(0.50, .67449), (0.80, 1.28155), (0.90, 1.64485), (0.95, 1.95996), (0.99, 2.57583), (0.999, 3.29053)]
    for (c0,z0),(c1,z1) in zip(pts, pts[1:]):
        if c <= c1:
            t = (c-c0)/(c1-c0)
            return z0 + t*(z1-z0)
    return pts[-1][1]


def _eye(n: int, scale: float = 1.0) -> list[list[float]]:
    return [[scale if i == j else 0.0 for j in range(n)] for i in range(n)]


def _mat_vec(a: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    return [sum(float(a[i][j])*float(x[j]) for j in range(len(x))) for i in range(len(a))]


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x)*float(y) for x,y in zip(a,b))


def _inverse(a: Sequence[Sequence[float]]) -> list[list[float]]:
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("matrix must be non-empty and square")
    aug = [[float(a[i][j]) for j in range(n)] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular covariance/precision matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [v/p for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            if abs(f) > 1e-18:
                aug[r] = [aug[r][j] - f*aug[col][j] for j in range(2*n)]
    return [row[n:] for row in aug]


SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v5_bayes_models(
 scope TEXT NOT NULL,
 regime TEXT NOT NULL,
 arm_id TEXT NOT NULL,
 n INTEGER NOT NULL,
 feature_order_json TEXT NOT NULL,
 precision_json TEXT NOT NULL,
 moment_json TEXT NOT NULL,
 residual_ss REAL NOT NULL,
 reward_sum REAL NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(scope,regime,arm_id)
);
CREATE TABLE IF NOT EXISTS collective_v5_bayes_observations(
 obs_id TEXT PRIMARY KEY,
 scope TEXT NOT NULL,
 regime TEXT NOT NULL,
 arm_id TEXT NOT NULL,
 reward REAL NOT NULL,
 features_json TEXT NOT NULL,
 pre_mean REAL,
 pre_sigma REAL,
 pre_lower REAL,
 pre_upper REAL,
 covered INTEGER,
 abs_error REAL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v5_bayes_obs ON collective_v5_bayes_observations(scope,regime,arm_id,created_at);

CREATE TABLE IF NOT EXISTS collective_v5_interaction_credit(
 event_id TEXT PRIMARY KEY,
 analysis_key TEXT NOT NULL,
 term TEXT NOT NULL,
 order_n INTEGER NOT NULL,
 effect REAL,
 confidence REAL NOT NULL,
 status TEXT NOT NULL,
 cells_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v5_delayed_credit(
 event_id TEXT PRIMARY KEY,
 action_id TEXT NOT NULL,
 outcome_key TEXT NOT NULL,
 outcome_delta REAL NOT NULL,
 delay_cycles INTEGER NOT NULL,
 discount REAL NOT NULL,
 causal_confidence REAL NOT NULL,
 credited_reward REAL NOT NULL,
 regime TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v5_delayed_action ON collective_v5_delayed_credit(regime,action_id,created_at);

CREATE TABLE IF NOT EXISTS collective_v5_transitions(
 action_id TEXT NOT NULL,
 feature TEXT NOT NULL,
 n INTEGER NOT NULL,
 weight_sum REAL NOT NULL,
 delta_sum REAL NOT NULL,
 delta2_sum REAL NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(action_id,feature)
);
CREATE TABLE IF NOT EXISTS collective_v5_transition_observations(
 obs_id TEXT PRIMARY KEY,
 action_id TEXT NOT NULL,
 before_json TEXT NOT NULL,
 after_json TEXT NOT NULL,
 evidence_weight REAL NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS collective_v5_regime_geometry(
 cluster_id TEXT PRIMARY KEY,
 n INTEGER NOT NULL,
 weight_sum REAL NOT NULL,
 centroid_json TEXT NOT NULL,
 reward_sum REAL NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS collective_v5_compensations(
 compensation_id TEXT PRIMARY KEY,
 projection_id TEXT NOT NULL,
 status TEXT NOT NULL,
 expected_semantic_eid TEXT,
 semantic_eid_after TEXT,
 removed_edges_json TEXT NOT NULL,
 git_compensation_required INTEGER NOT NULL,
 error TEXT,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
"""


class CollectiveScienceRuntime:
    """V5 causal experimental operating layer.

    V5 improves uncertainty, experiment design, interaction/delayed credit,
    learned transition models, multi-period scheduling, witness isolation,
    projection compensation, learned regime geometry and Pareto search.

    It deliberately does not convert statistical models into canonical truth.
    """

    _REGRESSION_REF = re.compile(r"^(tests/[A-Za-z0-9_./-]+\\.py)::([A-Za-z_][A-Za-z0-9_]*)::([A-Za-z_][A-Za-z0-9_]*)$")

    def __init__(self, store: Any, collective: CollectiveRuntime, growth: CollectiveGrowthRuntime,
                 memory: CollectiveMemoryRuntime, learning: CollectiveLearningRuntime, ecology: CollectiveEcologyRuntime):
        self.s = store
        self.collective = collective
        self.growth = growth
        self.memory = memory
        self.learning = learning
        self.ecology = ecology
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> Dict[str, Any]:
        q = lambda table: self.s.one(f"SELECT COUNT(*) AS n FROM {table}")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V5",
            "persistent_surfaces": {
                "bayes_models": q("collective_v5_bayes_models"),
                "bayes_observations": q("collective_v5_bayes_observations"),
                "interaction_credit_events": q("collective_v5_interaction_credit"),
                "delayed_credit_events": q("collective_v5_delayed_credit"),
                "transition_observations": q("collective_v5_transition_observations"),
                "regime_clusters": q("collective_v5_regime_geometry"),
                "compensation_runs": q("collective_v5_compensations"),
            },
            "operators": [
                "bayes_predict", "bayes_observe", "uncertainty_calibration",
                "experiment_design", "interaction_credit", "delayed_credit_record", "delayed_credit_summary",
                "transition_observe", "transition_predict", "rollout_learned",
                "schedule_multiperiod", "execute_witness_cell", "projection_compensate",
                "regime_geometry_observe", "regime_geometry_resolve", "pareto_frontier",
            ],
            "laws": [
                "POSTERIOR != TRUTH; full covariance improves uncertainty geometry but remains model-dependent",
                "CALIBRATION is empirical coverage, not a proof of correctness outside observed regimes",
                "EXPECTED_INFORMATION_GAIN selects experiments; it does not certify hypotheses",
                "INTERACTION_EFFECT requires identified cells; missing contrasts remain UNIDENTIFIED",
                "DELAYED_CREDIT decays and carries causal confidence; temporal proximity alone is not causation",
                "TRANSITION_MODEL is learned from observed transitions and remains SIMULATE_ONLY",
                "MULTIPERIOD_SCHEDULE is bounded beam search unless an exact proof is returned",
                "WITNESS_CELL is constrained process isolation, not OS-level hermeticity",
                "COMPENSATION is an explicit inverse only for projection-created active edges",
                "LEARNED_REGIME_GEOMETRY is a routing partition, not semantic identity",
                "PARETO_FRONTIER preserves tradeoffs rather than hiding them in one scalar reward",
            ],
        }

    def _bayes_row(self, scope: str, regime: str, arm_id: str) -> Dict[str, Any] | None:
        return self.s.one("SELECT * FROM collective_v5_bayes_models WHERE scope=? AND regime=? AND arm_id=?",
                          (str(scope), str(regime), str(arm_id)))

    @staticmethod
    def _feature_map(features: Mapping[str, Any]) -> Dict[str, float]:
        out = {}
        for k,v in features.items():
            try:
                out[str(k)] = max(-1.0, min(1.0, float(v)))
            except (TypeError, ValueError):
                continue
        return out

    def _bayes_state(self, scope: str, regime: str, arm_id: str, features: Mapping[str, Any], ridge: float = 1.0) -> Dict[str, Any]:
        f = self._feature_map(features)
        row = self._bayes_row(scope, regime, arm_id)
        old_order = json.loads(row["feature_order_json"]) if row else []
        order = sorted(set(old_order) | set(f))
        dim = len(order) + 1
        new_a = _eye(dim, max(1e-6, float(ridge)))
        new_b = [0.0] * dim
        if row:
            old_a = json.loads(row["precision_json"])
            old_b = json.loads(row["moment_json"])
            old_index = {"__bias__": 0, **{k:i+1 for i,k in enumerate(old_order)}}
            new_index = {"__bias__": 0, **{k:i+1 for i,k in enumerate(order)}}
            for ki,oi in old_index.items():
                ni = new_index[ki]
                new_b[ni] = float(old_b[oi])
                for kj,oj in old_index.items():
                    nj = new_index[kj]
                    new_a[ni][nj] = float(old_a[oi][oj])
        phi = [1.0] + [float(f.get(k, 0.0)) for k in order]
        return {
            "row": row, "order": order, "precision": new_a, "moment": new_b, "phi": phi,
            "n": int(row["n"]) if row else 0,
            "residual_ss": float(row["residual_ss"]) if row else 0.0,
            "reward_sum": float(row["reward_sum"]) if row else 0.0,
        }

    def uncertainty_calibration(self, scope: str = "global", regime: str | None = None,
                                arm_id: str | None = None, target_coverage: float = 0.90) -> Dict[str, Any]:
        where = ["scope=?", "covered IS NOT NULL"]
        args: list[Any] = [str(scope)]
        if regime is not None:
            where.append("regime=?"); args.append(str(regime))
        if arm_id is not None:
            where.append("arm_id=?"); args.append(str(arm_id))
        row = self.s.one(
            "SELECT COUNT(*) AS n,SUM(covered) AS covered,SUM(abs_error) AS abs_error,"
            "SUM(pre_upper-pre_lower) AS width FROM collective_v5_bayes_observations WHERE " + " AND ".join(where),
            tuple(args)
        ) or {"n":0,"covered":0,"abs_error":0,"width":0}
        n = int(row["n"] or 0)
        covered = int(row["covered"] or 0)
        posterior_coverage = (covered + 1.0) / (n + 2.0)
        target = _clamp(target_coverage, .50, .999)
        reliability = n / (n + 20.0) if n else 0.0
        raw_scale = target / max(0.05, posterior_coverage)
        scale = max(0.50, min(3.0, 1.0 + reliability*(raw_scale - 1.0)))
        return {
            "scope": str(scope), "regime": regime, "arm_id": arm_id,
            "n": n, "covered": covered, "empirical_coverage": round(covered/n,6) if n else None,
            "posterior_coverage": round(posterior_coverage,6), "target_coverage": round(target,6),
            "mean_abs_error": round(float(row["abs_error"] or 0)/n,6) if n else None,
            "mean_interval_width": round(float(row["width"] or 0)/n,6) if n else None,
            "reliability": round(reliability,6), "sigma_scale": round(scale,6),
            "law": "interval width is empirically corrected only from prior out-of-sample predictions; coverage does not imply causal validity",
        }

    def bayes_predict(self, features: Mapping[str, Any], regime: str, arm_id: str,
                      scope: str = "global", target_coverage: float = .90, ridge: float = 1.0) -> Dict[str, Any]:
        st = self._bayes_state(scope, regime, arm_id, features, ridge)
        inv = _inverse(st["precision"])
        theta = _mat_vec(inv, st["moment"])
        raw_mean = _dot(st["phi"], theta)
        p = len(st["phi"])
        if st["n"] > p:
            noise_var = max(1e-5, st["residual_ss"] / max(1, st["n"] - p))
        elif st["n"] > 0:
            mean_reward = st["reward_sum"] / st["n"]
            noise_var = max(.02, mean_reward*(1-mean_reward))
        else:
            noise_var = .25
        leverage = max(0.0, _dot(st["phi"], _mat_vec(inv, st["phi"])))
        raw_sigma = math.sqrt(max(1e-9, noise_var * (1.0 + leverage)))
        cal = self.uncertainty_calibration(scope, regime, arm_id, target_coverage)
        sigma = min(1.0, raw_sigma * float(cal["sigma_scale"]))
        z = _normal_z(target_coverage)
        mean = _clamp(raw_mean)
        lo, hi = _clamp(mean - z*sigma), _clamp(mean + z*sigma)
        return {
            "scope": str(scope), "regime": str(regime), "arm_id": str(arm_id), "n": st["n"],
            "feature_order": st["order"], "mean": round(mean,6), "raw_mean": round(raw_mean,6),
            "sigma": round(sigma,6), "raw_sigma": round(raw_sigma,6),
            "lower": round(lo,6), "upper": round(hi,6), "target_coverage": round(_clamp(target_coverage,.5,.999),6),
            "calibration": cal, "posterior_covariance": [[round(v,6) for v in row] for row in inv],
            "law": "full-covariance posterior preserves correlated feature uncertainty; interval remains model-conditional",
        }

    def bayes_observe(self, features: Mapping[str, Any], reward: float, regime: str, arm_id: str,
                      scope: str = "global", actor: str = "agent", weight: float = 1.0,
                      target_coverage: float = .90, ridge: float = 1.0) -> Dict[str, Any]:
        r = _clamp(reward)
        w = max(0.0, min(10.0, float(weight)))
        if w <= 0:
            raise ValueError("weight must be > 0")
        pre = self.bayes_predict(features, regime, arm_id, scope, target_coverage, ridge)
        st = self._bayes_state(scope, regime, arm_id, features, ridge)
        phi, a, b = st["phi"], st["precision"], st["moment"]
        pre_err = r - float(pre["mean"])
        for i in range(len(phi)):
            b[i] += w * phi[i] * r
            for j in range(len(phi)):
                a[i][j] += w * phi[i] * phi[j]
        now = time.time()
        created = float(st["row"]["created_at"]) if st["row"] else now
        with self.s._lock, self.s.db:
            self.s.db.execute(
                """INSERT INTO collective_v5_bayes_models(scope,regime,arm_id,n,feature_order_json,precision_json,moment_json,residual_ss,reward_sum,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(scope,regime,arm_id) DO UPDATE SET
                     n=excluded.n,feature_order_json=excluded.feature_order_json,precision_json=excluded.precision_json,
                     moment_json=excluded.moment_json,residual_ss=excluded.residual_ss,reward_sum=excluded.reward_sum,updated_at=excluded.updated_at""",
                (str(scope),str(regime),str(arm_id),st["n"]+1,json.dumps(st["order"]),json.dumps(a),json.dumps(b),
                 st["residual_ss"]+w*pre_err*pre_err,st["reward_sum"]+w*r,created,now)
            )
            oid = _stable_id("BAYES",scope,regime,arm_id,now)
            covered = None if st["n"] == 0 else (1 if float(pre["lower"]) <= r <= float(pre["upper"]) else 0)
            self.s.db.execute(
                "INSERT INTO collective_v5_bayes_observations VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (oid,str(scope),str(regime),str(arm_id),r,json.dumps(self._feature_map(features),sort_keys=True),
                 float(pre["mean"]),float(pre["sigma"]),float(pre["lower"]),float(pre["upper"]),covered,
                 abs(pre_err),str(actor),now)
            )
        return {
            "obs_id": oid, "reward": round(r,6), "pre_prediction": pre,
            "posterior": self.bayes_predict(features, regime, arm_id, scope, target_coverage, ridge),
            "law": "posterior updates only from explicit observed reward; pre-update prediction is retained for calibration",
        }

    def experiment_design(self, hypotheses: Sequence[Mapping[str, Any]], experiments: Sequence[Mapping[str, Any]],
                          sample_size: int = 20, control_fraction: float = .5,
                          cost_weight: float = .10, risk_weight: float = .20) -> Dict[str, Any]:
        if len(hypotheses) < 2:
            raise ValueError("need at least two hypotheses")
        if not experiments:
            raise ValueError("experiments must not be empty")
        if sample_size < 2 or sample_size > 100000:
            raise ValueError("sample_size must be in [2,100000]")
        ids = [str(h.get("id",f"H{i}")) for i,h in enumerate(hypotheses)]
        pri = [max(0.0,float(h.get("prior",1.0))) for h in hypotheses]
        s = sum(pri)
        if s <= 0:
            raise ValueError("hypothesis priors must have positive total")
        pri = [x/s for x in pri]
        h0 = _entropy(pri)
        ranked = []
        for i,e in enumerate(experiments):
            eid = str(e.get("id",f"E{i}"))
            ethical = bool(e.get("ethical",True))
            preds = dict(e.get("positive_probability",{}))
            if any(hid not in preds for hid in ids):
                ranked.append({"id":eid,"status":"INCOMPLETE_PREDICTIONS","score":0.0}); continue
            ph = [_clamp(preds[hid]) for hid in ids]
            ppos = sum(p*q for p,q in zip(pri,ph))
            def posterior(positive: bool) -> list[float]:
                vals = [p*(q if positive else (1-q)) for p,q in zip(pri,ph)]
                z = sum(vals)
                return [v/z for v in vals] if z > 1e-15 else list(pri)
            hp = _entropy(posterior(True)); hn = _entropy(posterior(False))
            expected_h = ppos*hp + (1-ppos)*hn
            eig = max(0.0, h0-expected_h)
            cost = max(0.0,float(e.get("cost",0.0))); risk = _clamp(e.get("risk",0.0))
            feasibility = _clamp(e.get("feasibility",1.0))
            score = 0.0 if not ethical else max(0.0, eig*feasibility - float(cost_weight)*cost - float(risk_weight)*risk)
            cf = _clamp(e.get("control_fraction",control_fraction),0.0,1.0)
            n_control = int(round(sample_size*cf)) if e.get("randomizable",True) else 0
            n_control = min(sample_size,max(0,n_control))
            allocation = {"CONTROL":n_control,"TREATMENT":sample_size-n_control} if e.get("randomizable",True) else {"OBSERVATIONAL":sample_size}
            ranked.append({
                "id":eid,"status":"ELIGIBLE" if ethical else "ETHICS_BLOCK",
                "prior_entropy_bits":round(h0,6),"expected_entropy_bits":round(expected_h,6),
                "expected_information_gain_bits":round(eig,6),"cost":round(cost,6),"risk":round(risk,6),
                "feasibility":round(feasibility,6),"score":round(score,6),"allocation":allocation,
                "requires_control":bool(e.get("requires_control",False)),
            })
        ranked.sort(key=lambda x:(-float(x.get("score",0.0)),-float(x.get("expected_information_gain_bits",0.0)),x["id"]))
        winner = next((x["id"] for x in ranked if x.get("status")=="ELIGIBLE"),None)
        return {
            "decision":"DESIGN_ONLY","winner":winner,"ranked_experiments":ranked,
            "hypotheses":[{"id":hid,"prior":round(p,6)} for hid,p in zip(ids,pri)],
            "law":"expected information gain ranks experiments under supplied likelihoods; ethics/risk/cost gates remain external authority and results are not observations",
        }

    def interaction_credit(self, analysis_key: str, experiments: Sequence[Mapping[str, Any]],
                           actor: str = "agent") -> Dict[str, Any]:
        if len(experiments) < 2:
            raise ValueError("experiments must contain at least two observations")
        interventions = sorted({str(a) for e in experiments for a in e.get("interventions",[])})
        rows = []
        now = time.time()
        def mean(group):
            vals = [(float(e.get("weight",1.0)), _signed(e["outcome_delta"])) for e in group]
            w = sum(max(0.0,a) for a,_ in vals)
            return None if w <= 0 else sum(max(0.0,a)*b for a,b in vals)/w
        for a in interventions:
            yes=[e for e in experiments if a in set(map(str,e.get("interventions",[])))]
            no=[e for e in experiments if a not in set(map(str,e.get("interventions",[])))]
            my,mn=mean(yes),mean(no)
            effect=None if my is None or mn is None else my-mn
            conf = 0.0 if effect is None else min(1.0, min(len(yes),len(no))/5.0) * sum(_clamp(e.get("design_confidence",.25)) for e in yes+no)/len(yes+no)
            status="UNIDENTIFIED" if effect is None else ("CAUSAL_SUPPORTED" if conf>=.7 else "ASSOCIATIONAL")
            rows.append({"term":a,"order":1,"effect":effect,"confidence":conf,"status":status,"cells":{"present":len(yes),"absent":len(no)}})
        for i,a in enumerate(interventions):
            for b in interventions[i+1:]:
                cells={"11":[],"10":[],"01":[],"00":[]}
                for e in experiments:
                    s=set(map(str,e.get("interventions",[])))
                    cells[("1" if a in s else "0")+("1" if b in s else "0")].append(e)
                means={k:mean(v) for k,v in cells.items()}
                identified=all(means[k] is not None for k in ("11","10","01","00"))
                effect=(means["11"]-means["10"]-means["01"]+means["00"]) if identified else None
                mincell=min(len(cells[k]) for k in cells)
                avgconf=sum(_clamp(e.get("design_confidence",.25)) for e in experiments)/len(experiments)
                conf=(min(1.0,mincell/3.0)*avgconf) if identified else 0.0
                status="UNIDENTIFIED" if not identified else ("CAUSAL_SUPPORTED" if conf>=.7 else "ASSOCIATIONAL")
                rows.append({"term":f"{a}×{b}","order":2,"effect":effect,"confidence":conf,"status":status,
                             "cells":{k:len(v) for k,v in cells.items()}})
        with self.s._lock,self.s.db:
            for idx,r in enumerate(rows):
                eid=_stable_id("IX",analysis_key,r["term"],now,idx)
                self.s.db.execute("INSERT INTO collective_v5_interaction_credit VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (eid,str(analysis_key),r["term"],r["order"],r["effect"],r["confidence"],r["status"],
                     json.dumps(r["cells"],sort_keys=True),str(actor),now))
                r["event_id"]=eid
        return {
            "analysis_key":str(analysis_key),"terms":rows,
            "law":"main effects use present-vs-absent contrasts; pair interaction requires all four 2x2 cells and remains associational unless design confidence supports causality",
        }

    def delayed_credit_record(self, action_id: str, outcome_key: str, outcome_delta: float, delay_cycles: int,
                              causal_confidence: float, discount: float = .95, regime: str = "GLOBAL",
                              actor: str = "agent") -> Dict[str, Any]:
        if delay_cycles < 0 or delay_cycles > 100000:
            raise ValueError("delay_cycles must be in [0,100000]")
        d=_signed(outcome_delta); c=_clamp(causal_confidence); g=_clamp(discount,0.0,1.0)
        credit=d*c*(g**delay_cycles)
        now=time.time(); eid=_stable_id("DC",action_id,outcome_key,delay_cycles,now)
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v5_delayed_credit VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (eid,str(action_id),str(outcome_key),d,int(delay_cycles),g,c,credit,str(regime),str(actor),now))
        return {"event_id":eid,"action_id":str(action_id),"outcome_key":str(outcome_key),
                "credited_reward":round(credit,6),"causal_confidence":round(c,6),"delay_cycles":int(delay_cycles),
                "law":"delayed credit is discounted and confidence-weighted; delay alone never establishes causation"}

    def delayed_credit_summary(self, action_id: str | None = None, regime: str | None = None, limit: int = 1000) -> Dict[str, Any]:
        where=[];args=[]
        if action_id is not None: where.append("action_id=?");args.append(str(action_id))
        if regime is not None: where.append("regime=?");args.append(str(regime))
        sql="SELECT * FROM collective_v5_delayed_credit"+((" WHERE "+" AND ".join(where)) if where else "")+" ORDER BY created_at DESC LIMIT ?";args.append(int(limit))
        rows=self.s.rows(sql,tuple(args)); by={}
        for r in rows:
            d=by.setdefault(r["action_id"],{"n":0,"credit":0.0,"conf":0.0,"delay":0.0})
            d["n"]+=1;d["credit"]+=float(r["credited_reward"]);d["conf"]+=float(r["causal_confidence"]);d["delay"]+=int(r["delay_cycles"])
        out=[{"action_id":k,"n":v["n"],"mean_credited_reward":round(v["credit"]/v["n"],6),
              "mean_causal_confidence":round(v["conf"]/v["n"],6),"mean_delay_cycles":round(v["delay"]/v["n"],6)} for k,v in by.items()]
        out.sort(key=lambda x:(-abs(x["mean_credited_reward"]),x["action_id"]))
        return {"rows":len(rows),"actions":out}

    def transition_observe(self, action_id: str, before: Mapping[str, Any], after: Mapping[str, Any],
                           evidence_weight: float = 1.0, actor: str = "agent") -> Dict[str, Any]:
        b=self._feature_map(before); a=self._feature_map(after); keys=sorted(set(b)|set(a))
        w=max(0.0,min(10.0,float(evidence_weight)))
        if w<=0: raise ValueError("evidence_weight must be > 0")
        now=time.time(); oid=_stable_id("TR",action_id,now,actor); deltas={}
        with self.s._lock,self.s.db:
            for k in keys:
                d=float(a.get(k,0.0))-float(b.get(k,0.0));deltas[k]=d
                row=self.s.one("SELECT * FROM collective_v5_transitions WHERE action_id=? AND feature=?",(str(action_id),k))
                n=int(row["n"]) if row else 0;ws=float(row["weight_sum"]) if row else 0.0;ds=float(row["delta_sum"]) if row else 0.0;d2=float(row["delta2_sum"]) if row else 0.0
                created=float(row["created_at"]) if row else now
                self.s.db.execute("""INSERT INTO collective_v5_transitions VALUES(?,?,?,?,?,?,?,?)
                    ON CONFLICT(action_id,feature) DO UPDATE SET n=excluded.n,weight_sum=excluded.weight_sum,
                    delta_sum=excluded.delta_sum,delta2_sum=excluded.delta2_sum,updated_at=excluded.updated_at""",
                    (str(action_id),k,n+1,ws+w,ds+w*d,d2+w*d*d,created,now))
            self.s.db.execute("INSERT INTO collective_v5_transition_observations VALUES(?,?,?,?,?,?,?)",
                (oid,str(action_id),json.dumps(b,sort_keys=True),json.dumps(a,sort_keys=True),w,str(actor),now))
        return {"obs_id":oid,"action_id":str(action_id),"deltas":{k:round(v,6) for k,v in deltas.items()},
                "prediction":self.transition_predict(action_id,b)}

    def transition_predict(self, action_id: str, context: Mapping[str, Any], prior_strength: float = 5.0) -> Dict[str, Any]:
        c=self._feature_map(context); rows=self.s.rows("SELECT * FROM collective_v5_transitions WHERE action_id=?",(str(action_id),))
        pred={};unc={};next_ctx=dict(c);kappa=max(0.0,float(prior_strength))
        for r in rows:
            ws=float(r["weight_sum"]); mean=float(r["delta_sum"])/(ws or 1.0)
            post=(ws*mean)/(ws+kappa) if ws+kappa>0 else 0.0
            var=max(0.0,float(r["delta2_sum"])/(ws or 1.0)-mean*mean) if ws>0 else .25
            reliability=ws/(ws+kappa) if ws+kappa>0 else 0.0
            sigma=math.sqrt(max(.000001,var/(1+ws)+(1-reliability)*.05))
            pred[r["feature"]]=post;unc[r["feature"]]=sigma
            next_ctx[r["feature"]]=max(-1.0,min(1.0,float(c.get(r["feature"],0.0))+post))
        return {"action_id":str(action_id),"context":c,"delta_mean":{k:round(v,6) for k,v in pred.items()},
                "delta_sigma":{k:round(v,6) for k,v in unc.items()},"next_context_mean":{k:round(v,6) for k,v in next_ctx.items()},
                "observed_features":len(rows),"law":"learned transitions are shrinkage estimates over observed deltas; absent features stay unchanged/unknown rather than invented"}

    def rollout_learned(self, initial_context: Mapping[str, Any], trajectories: Sequence[Mapping[str, Any]],
                        discount: float = .95, uncertainty_alpha: float = 1.0, prior_strength: float = 5.0) -> Dict[str, Any]:
        if not trajectories: raise ValueError("trajectories must not be empty")
        gamma=_clamp(discount,0.0,1.0);alpha=max(0.0,float(uncertainty_alpha)); ranked=[]
        for ti,tr in enumerate(trajectories):
            ctx=self._feature_map(initial_context);steps=[];ret=lo=hi=0.0
            for t,st in enumerate(tr.get("steps",[])):
                action=str(st["action_id"]); tp=self.transition_predict(action,ctx,prior_strength)
                config=st.get("configuration")
                base=float(self.collective.evaluate(config)["return_on_group_organization"]) if config else _clamp(st.get("base_reward",.5))
                transition_unc=sum(tp["delta_sigma"].values())/max(1,len(tp["delta_sigma"])) if tp["delta_sigma"] else .5
                mean=_clamp(base - .05*transition_unc)
                low=_clamp(mean-alpha*.10*transition_unc); upper=_clamp(mean+alpha*.10*transition_unc)
                factor=gamma**t;ret+=factor*mean;lo+=factor*low;hi+=factor*upper
                steps.append({"t":t,"action_id":action,"reward_mean":round(mean,6),"reward_lower":round(low,6),"reward_upper":round(upper,6),"transition":tp})
                ctx=dict(tp["next_context_mean"])
            ranked.append({"id":str(tr.get("id",f"trajectory_{ti}")),"expected_return":round(ret,6),"lower_return":round(lo,6),"upper_return":round(hi,6),"final_context":ctx,"steps":steps})
        ranked.sort(key=lambda x:(-x["expected_return"],-x["lower_return"],x["id"]))
        return {"decision":"SIMULATE_ONLY","winner":ranked[0]["id"],"ranked_trajectories":ranked,
                "law":"learned-transition rollout remains model-based simulation; it cannot update transition or policy state without execution"}

    def _worker_resource_profile(self, worker: Mapping[str, Any], scope: str) -> Dict[str, Any]:
        explicit={k:max(0.0,float(v)) for k,v in worker.get("expected_resources",{}).items() if k in V4_RESOURCE_KEYS and v is not None}
        if explicit: return {"source":"EXPLICIT","resources":explicit,"reliability":1.0}
        try:
            p=self.ecology._worker_profile(worker,scope)
            return {"source":p["cost_source"],"resources":dict(p["estimate"]),"reliability":float(p["reliability"])}
        except Exception:
            return {"source":"UNKNOWN","resources":{},"reliability":0.0}

    def schedule_multiperiod(self, tasks: Sequence[Mapping[str, Any]], workers: Sequence[Mapping[str, Any]],
                             horizon: int = 12, budget: Mapping[str, Any] | None = None, beam_width: int = 128,
                             scope: str = "global", discount: float = .97) -> Dict[str, Any]:
        if not tasks or not workers: raise ValueError("tasks and workers must not be empty")
        if len(tasks)>14: raise ValueError("V5 bounded scheduler supports at most 14 tasks per call")
        if horizon<1 or horizon>100: raise ValueError("horizon must be in [1,100]")
        if beam_width<1 or beam_width>1024: raise ValueError("beam_width must be in [1,1024]")
        taskmap={str(t.get("id",f"task_{i}")):dict(t) for i,t in enumerate(tasks)}
        if len(taskmap)!=len(tasks): raise ValueError("task ids must be unique")
        profiles={str(w.get("id",f"worker_{i}")):{"worker":dict(w),"profile":self._worker_resource_profile(w,scope)} for i,w in enumerate(workers)}
        caps={wid:{str(x) for x in rec["worker"].get("capabilities",[])} for wid,rec in profiles.items()}
        initial_budget={k:max(0.0,float(v)) for k,v in (budget or {}).items() if k in V4_RESOURCE_KEYS}
        states=[{"score":0.0,"scheduled":{},"worker_free":{wid:0 for wid in profiles},"budget":dict(initial_budget),"uncertainty":0.0}]
        gamma=_clamp(discount,0.0,1.0)
        for _ in range(len(taskmap)):
            next_states=[]
            for st in states:
                remaining=[tid for tid in taskmap if tid not in st["scheduled"]]
                for tid in remaining:
                    task=taskmap[tid]; deps=[str(x) for x in task.get("dependencies",[])]
                    if any(d not in st["scheduled"] for d in deps): continue
                    dep_finish=max([st["scheduled"][d]["finish"] for d in deps],default=0)
                    req={str(x) for x in task.get("required_capabilities",[])}
                    duration=max(1,int(task.get("duration",1))); utility=max(0.0,float(task.get("utility",.5)))
                    deadline=task.get("deadline")
                    for wid,rec in profiles.items():
                        fit=1.0 if not req else len(req & caps[wid])/len(req)
                        if fit<=0: continue
                        start=max(int(st["worker_free"][wid]),dep_finish);finish=start+duration
                        if finish>horizon: continue
                        prof=rec["profile"]; costs=dict(prof["resources"])
                        explicit_task={k:max(0.0,float(v)) for k,v in task.get("resource_cost",{}).items() if k in V4_RESOURCE_KEYS}
                        if explicit_task: costs=explicit_task
                        feasible=True; nb=dict(st["budget"])
                        for k,cap in initial_budget.items():
                            if k in costs:
                                if costs[k]>nb.get(k,0.0)+1e-12: feasible=False;break
                                nb[k]=nb.get(k,0.0)-costs[k]
                        if not feasible: continue
                        lateness=max(0,finish-int(deadline)) if deadline is not None else 0
                        uncertainty_penalty=.12*(1-float(prof["reliability"])) if initial_budget and any(k not in costs for k in initial_budget) else 0.0
                        reward=(utility*fit*(gamma**finish))-0.08*lateness-uncertainty_penalty
                        ns={"score":st["score"]+reward,"scheduled":dict(st["scheduled"]),"worker_free":dict(st["worker_free"]),"budget":nb,"uncertainty":st["uncertainty"]+uncertainty_penalty}
                        ns["scheduled"][tid]={"task":tid,"worker":wid,"start":start,"finish":finish,"fit":round(fit,6),"value":round(reward,6),"cost_source":prof["source"],"resources":costs}
                        ns["worker_free"][wid]=finish
                        next_states.append(ns)
            if not next_states: break
            next_states.sort(key=lambda s:(-len(s["scheduled"]),-s["score"],s["uncertainty"]))
            uniq=[];seen=set()
            for s in next_states:
                key=(tuple(sorted(s["scheduled"])),tuple(sorted(s["worker_free"].items())))
                if key in seen: continue
                seen.add(key);uniq.append(s)
                if len(uniq)>=beam_width: break
            states=uniq
        states.sort(key=lambda s:(-len(s["scheduled"]),-s["score"],s["uncertainty"]))
        best=states[0]
        unscheduled=[tid for tid in taskmap if tid not in best["scheduled"]]
        schedule=sorted(best["scheduled"].values(),key=lambda x:(x["start"],x["finish"],x["worker"],x["task"]))
        return {"schedule":schedule,"scheduled_count":len(schedule),"unscheduled":unscheduled,"objective":round(best["score"],6),
                "remaining_budget":{k:round(v,6) for k,v in best["budget"].items()},"horizon":horizon,
                "optimality":"BOUNDED_BEAM_SEARCH_NO_GLOBAL_OPTIMALITY_PROOF","beam_width":beam_width,
                "law":"multi-period schedule respects dependencies, worker capacity, horizon and known budgets; unknown constrained cost carries uncertainty rather than zero"}

    @staticmethod
    def _repo_root() -> Path:
        return Path(__file__).resolve().parent.parent

    def execute_witness_cell(self, regression_ref: str, timeout_s: float = 20.0,
                             memory_mb: int = 512, cpu_s: int = 10, actor: str = "agent") -> Dict[str, Any]:
        ref=str(regression_ref);m=self._REGRESSION_REF.fullmatch(ref)
        if not m or ".." in m.group(1).split("/"):
            return {"status":"INVALID_REF","regression_ref":ref,"hermetic":False,"executed":False}
        rel,cls,method=m.groups();root=self._repo_root();target=(root/rel).resolve()
        if root not in target.parents or not target.is_file():
            return {"status":"INVALID_REF","regression_ref":ref,"hermetic":False,"executed":False}
        module=rel[:-3].replace("/",".")
        bootstrap=(
            "import os,sys,unittest,socket;"
            f"sys.path.insert(0,{str(root)!r});"
            "class _DeniedSocket:\n"
            "    def __init__(self,*a,**k): raise RuntimeError('network disabled in witness cell')\n"
            "socket.socket=_DeniedSocket;"
            f"s=unittest.defaultTestLoader.loadTestsFromName({(module+'.'+cls+'.'+method)!r});"
            "r=unittest.TextTestRunner(verbosity=1).run(s);"
            "raise SystemExit(0 if r.wasSuccessful() else 1)"
        )
        env={"PYTHONHASHSEED":"0","PATH":os.environ.get("PATH",""),"HOME":tempfile.mkdtemp(prefix="athena-witness-")}
        preexec=None
        isolation=["python_-I","shell_false","sanitized_env","network_socket_monkeypatch","timeout"]
        if os.name=="posix":
            try:
                import resource
                def _limit():
                    resource.setrlimit(resource.RLIMIT_CPU,(max(1,int(cpu_s)),max(1,int(cpu_s))+1))
                    mem=max(64,int(memory_mb))*1024*1024
                    resource.setrlimit(resource.RLIMIT_AS,(mem,mem))
                    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024*1024,8*1024*1024))
                    resource.setrlimit(resource.RLIMIT_NOFILE,(64,64))
                preexec=_limit;isolation += ["rlimit_cpu","rlimit_as","rlimit_fsize","rlimit_nofile"]
            except Exception:
                pass
        started=time.time()
        try:
            p=subprocess.run([sys.executable,"-I","-c",bootstrap],cwd=str(root),env=env,text=True,capture_output=True,
                             timeout=max(1.0,min(60.0,float(timeout_s))),shell=False,preexec_fn=preexec)
            status="PASS" if p.returncode==0 else "FAIL";rc=p.returncode;out=p.stdout[-4000:];err=p.stderr[-4000:]
        except subprocess.TimeoutExpired as e:
            status="TIMEOUT";rc=None;out=(e.stdout or "")[-4000:] if isinstance(e.stdout,str) else "";err=(e.stderr or "")[-4000:] if isinstance(e.stderr,str) else ""
        except Exception as e:
            status="ERROR";rc=None;out="";err=str(e)
        return {"status":status,"regression_ref":ref,"returncode":rc,"duration_s":round(time.time()-started,6),
                "stdout_tail":out,"stderr_tail":err,"isolation":isolation,"hermetic":False,"executed":True,
                "law":"cell adds process/resource/network-socket constraints but is not claimed OS-hermetic; hostile native code requires stronger isolation"}

    def regime_geometry_observe(self, signals: Mapping[str, Any], reward: float, cluster_id: str | None = None,
                                domain: str | None = None, weight: float = 1.0) -> Dict[str, Any]:
        f=self.collective._signals(signals)
        cid=str(cluster_id or self.ecology.resolve_regime(f,domain)["regime"])
        w=max(0.0,min(10.0,float(weight)));r=_clamp(reward)
        if w<=0: raise ValueError("weight must be >0")
        now=time.time();row=self.s.one("SELECT * FROM collective_v5_regime_geometry WHERE cluster_id=?",(cid,))
        n=int(row["n"]) if row else 0;ws=float(row["weight_sum"]) if row else 0.0;old=json.loads(row["centroid_json"]) if row else {}
        new_ws=ws+w;centroid={}
        for k in self.collective.SIGNAL_KEYS:
            centroid[k]=(float(old.get(k,0.0))*ws+w*float(f[k]))/new_ws
        created=float(row["created_at"]) if row else now
        with self.s._lock,self.s.db:
            self.s.db.execute("""INSERT INTO collective_v5_regime_geometry VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(cluster_id) DO UPDATE SET n=excluded.n,weight_sum=excluded.weight_sum,centroid_json=excluded.centroid_json,
                reward_sum=excluded.reward_sum,updated_at=excluded.updated_at""",
                (cid,n+1,new_ws,json.dumps(centroid,sort_keys=True),(float(row["reward_sum"]) if row else 0.0)+w*r,created,now))
        return {"cluster_id":cid,"n":n+1,"centroid":{k:round(v,6) for k,v in centroid.items()},"mean_reward":round(((float(row["reward_sum"]) if row else 0.0)+w*r)/new_ws,6)}

    def regime_geometry_resolve(self, signals: Mapping[str, Any], top_k: int = 5, domain: str | None = None) -> Dict[str, Any]:
        f=self.collective._signals(signals);rows=self.s.rows("SELECT * FROM collective_v5_regime_geometry")
        ranked=[]
        for row in rows:
            c=json.loads(row["centroid_json"]);d2=sum((float(f[k])-float(c.get(k,.5)))**2 for k in self.collective.SIGNAL_KEYS)/len(self.collective.SIGNAL_KEYS)
            sim=math.exp(-4.0*d2);ws=float(row["weight_sum"]);rel=ws/(ws+10)
            ranked.append({"cluster_id":row["cluster_id"],"distance":round(math.sqrt(d2),6),"similarity":round(sim,6),
                           "reliability":round(rel,6),"n":int(row["n"]),"mean_reward":round(float(row["reward_sum"])/(ws or 1),6)})
        ranked.sort(key=lambda x:(-x["similarity"]*x["reliability"],-x["similarity"],x["cluster_id"]))
        return {"coarse_regime":self.ecology.resolve_regime(f,domain)["regime"],"learned_neighbors":ranked[:max(1,min(50,int(top_k)))],
                "law":"learned regime geometry supplies similarity/transfer neighborhoods; it never changes semantic identity"}

    def pareto_frontier(self, candidates: Sequence[Mapping[str, Any]], directions: Mapping[str, str] | None = None,
                        epsilon: float = 0.0, robust: bool = False) -> Dict[str, Any]:
        if not candidates: raise ValueError("candidates must not be empty")
        dirs={str(k):str(v).lower() for k,v in (directions or {}).items()}
        metrics=sorted({str(k) for c in candidates for k in c.get("metrics",{})})
        if not metrics: raise ValueError("candidate metrics must not be empty")
        for k in metrics:
            if dirs.get(k,"max") not in {"max","min"}: raise ValueError("directions values must be max or min")
        eps=max(0.0,float(epsilon))
        normalized=[]
        for i,c in enumerate(candidates):
            cid=str(c.get("id",f"candidate_{i}"));m={k:float(c.get("metrics",{}).get(k,0.0)) for k in metrics}
            intervals={k:tuple(map(float,v)) for k,v in c.get("intervals",{}).items() if isinstance(v,(list,tuple)) and len(v)==2}
            normalized.append({"id":cid,"metrics":m,"intervals":intervals,"raw":dict(c)})
        def val(c,k,worst: bool):
            direction=dirs.get(k,"max");interval=c["intervals"].get(k)
            if robust and interval:
                lo,hi=min(interval),max(interval)
                if direction=="max": return lo if worst else hi
                return -hi if worst else -lo
            v=c["metrics"][k];return v if direction=="max" else -v
        def dominates(a,b):
            av=[val(a,k,True) for k in metrics];bv=[val(b,k,False if robust else True) for k in metrics]
            ge=all(x+eps>=y for x,y in zip(av,bv));gt=any(x>y+eps for x,y in zip(av,bv))
            return ge and gt
        frontier=[];dominated=[]
        for c in normalized:
            dom=[o["id"] for o in normalized if o["id"]!=c["id"] and dominates(o,c)]
            if dom: dominated.append({"id":c["id"],"dominated_by":dom})
            else: frontier.append(c)
        crowd={c["id"]:0.0 for c in frontier}
        if len(frontier)>2:
            for k in metrics:
                vals=sorted(frontier,key=lambda c:val(c,k,True))
                crowd[vals[0]["id"]]=crowd[vals[-1]["id"]]=float("inf")
                low,high=val(vals[0],k,True),val(vals[-1],k,True);den=max(1e-12,high-low)
                for j in range(1,len(vals)-1):
                    if crowd[vals[j]["id"]]!=float("inf"):
                        crowd[vals[j]["id"]]+=(val(vals[j+1],k,True)-val(vals[j-1],k,True))/den
        out=[]
        for c in frontier:
            out.append({"id":c["id"],"metrics":c["metrics"],"intervals":c["intervals"],
                        "crowding_distance":"INF" if crowd[c["id"]]==float("inf") else round(crowd[c["id"]],6)})
        out.sort(key=lambda x:(0 if x["crowding_distance"]=="INF" else 1, x["id"]))
        return {"frontier":out,"frontier_count":len(out),"dominated":dominated,"metrics":metrics,"directions":{k:dirs.get(k,"max") for k in metrics},
                "robust":bool(robust),"epsilon":eps,"law":"Pareto frontier preserves non-dominated tradeoffs; robust mode requires worst-case dominance over interval-best competitor values"}

    def projection_compensate(self, core: Any, projection_id: str, expected_semantic_eid: str | None,
                              actor: str = "agent") -> Dict[str, Any]:
        pid=str(projection_id);saga=self.s.one("SELECT * FROM collective_projection_sagas WHERE projection_id=?",(pid,))
        if not saga: raise ValueError("projection saga not found")
        if saga["status"] not in {"COMPENSATION_REQUIRED","COMPLETED","SEMANTIC_APPLIED","GIT_COMMITTED"}:
            raise ValueError(f"projection status not compensable: {saga['status']}")
        head=self.s.head("global");current=head["eid"] if head else None
        if current!=expected_semantic_eid: raise ValueError(f"STALE_SEMANTIC_HEAD expected={expected_semantic_eid} current={current}")
        candidates=[]
        for row in self.s.rows("SELECT * FROM edges WHERE attrs_json LIKE ?",(f"%{pid}%",)):
            try: attrs=json.loads(row["attrs_json"])
            except Exception: attrs={}
            if attrs.get("projection_id")==pid: candidates.append(row)
        now=time.time();cid=_stable_id("COMP",pid,current,now);removed=[];last=current;error=None
        try:
            with self.s._lock,self.s.db:
                for row in candidates:
                    payload={"operation":"RETRACT_EDGE","edge_id":row["edge_id"],"src":row["src"],"relation":row["relation"],"dst":row["dst"],"projection_id":pid}
                    eid=event_id("COMPENSATE_EDGE",str(actor),last,payload);ed=digest(payload,32)
                    self.s.put_event(eid,"COMPENSATE_EDGE",str(actor),last,payload,ed)
                    self.s.db.execute("DELETE FROM edges WHERE edge_id=?",(row["edge_id"],))
                    self.s.set_head("global",None,None,eid,ed);last=eid
                    removed.append({"edge_id":row["edge_id"],"src":row["src"],"relation":row["relation"],"dst":row["dst"],"event":eid})
                git_needed=1 if saga["git_head_after"] else 0
                self.s.db.execute("INSERT INTO collective_v5_compensations VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (cid,pid,"SEMANTIC_COMPENSATED",expected_semantic_eid,last,json.dumps(removed,sort_keys=True),git_needed,None,str(actor),now,now))
            self.ecology.projection_mark(pid,"COMPENSATED",last,saga["git_head_after"],None)
            return {"compensation_id":cid,"projection_id":pid,"status":"SEMANTIC_COMPENSATED","removed_edges":removed,
                    "semantic_eid_after":last,"git_compensation_required":bool(saga["git_head_after"]),
                    "law":"inverse is valid only for active edges created by this projection; Git history and unrelated semantic effects are never silently rewritten"}
        except Exception as e:
            error=str(e)
            with self.s._lock,self.s.db:
                self.s.db.execute("INSERT INTO collective_v5_compensations VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (cid,pid,"COMPENSATION_FAILED",expected_semantic_eid,last,json.dumps(removed,sort_keys=True),1 if saga["git_head_after"] else 0,error,str(actor),now,time.time()))
            raise
