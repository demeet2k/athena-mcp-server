from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from .collective_science import CollectiveScienceRuntime


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _signed(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def _eye(n: int, scale: float = 1.0) -> list[list[float]]:
    return [[scale if i == j else 0.0 for j in range(n)] for i in range(n)]


def _inverse(a: Sequence[Sequence[float]]) -> list[list[float]]:
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("matrix must be square")
    aug = [[float(a[i][j]) for j in range(n)] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [v / p for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            if abs(f) > 1e-18:
                aug[r] = [aug[r][j] - f * aug[col][j] for j in range(2*n)]
    return [row[n:] for row in aug]


def _mat_vec(a: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    return [sum(float(a[i][j]) * float(x[j]) for j in range(len(x))) for i in range(len(a))]


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v6_ood_models(
 scope TEXT NOT NULL,
 regime TEXT NOT NULL,
 n INTEGER NOT NULL,
 feature_order_json TEXT NOT NULL,
 sum_json TEXT NOT NULL,
 cross_json TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(scope,regime)
);
CREATE TABLE IF NOT EXISTS collective_v6_causal_analyses(
 analysis_id TEXT PRIMARY KEY,
 treatment TEXT NOT NULL,
 outcome TEXT NOT NULL,
 status TEXT NOT NULL,
 adjustment_json TEXT NOT NULL,
 graph_json TEXT NOT NULL,
 assumptions_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v6_claims(
 claim_id TEXT PRIMARY KEY,
 claim_key TEXT NOT NULL UNIQUE,
 statement TEXT NOT NULL,
 scope TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v6_claim_witnesses(
 witness_id TEXT PRIMARY KEY,
 claim_id TEXT NOT NULL,
 kind TEXT NOT NULL,
 result TEXT NOT NULL,
 confidence REAL NOT NULL,
 independence_key TEXT NOT NULL,
 evidence_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_v6_claim_witness ON collective_v6_claim_witnesses(claim_id,created_at);
"""


class CollectiveDiscoveryRuntime:
    """V6 active discovery/control layer.

    This layer adds nonlinear basis uncertainty with OOD inflation, factor-space
    experiment generation, formal backdoor adjustment checks on supplied DAGs,
    higher-order factorial contrasts, multivariate stochastic transition
    summaries, receding-horizon planning, exact/certified small scheduling,
    fail-closed hermetic witness capsules, Pareto exploration, and a persistent
    replication/falsification graph.

    It does not claim universal causal discovery, GP/neural posterior inference,
    or distributed ACID across semantic/Git stores.
    """

    def __init__(self, science: CollectiveScienceRuntime):
        self.science = science
        self.s = science.s
        self.collective = science.collective
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        q = lambda t: self.s.one(f"SELECT COUNT(*) AS n FROM {t}")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V6",
            "persistent_surfaces": {
                "ood_models": q("collective_v6_ood_models"),
                "causal_analyses": q("collective_v6_causal_analyses"),
                "science_claims": q("collective_v6_claims"),
                "science_witnesses": q("collective_v6_claim_witnesses"),
            },
            "operators": [
                "ood_observe", "ood_score", "nonlinear_predict", "nonlinear_observe",
                "experiment_generate", "causal_identify", "higher_order_interactions",
                "transition_distribution", "mpc_plan", "schedule_certified",
                "witness_capsule", "pareto_bandit_select",
                "claim_register", "claim_witness", "claim_state",
            ],
            "laws": [
                "NONLINEAR_BASIS != UNIVERSAL_FUNCTION_APPROXIMATION",
                "OOD_SCORE != FACTUAL_FALSEHOOD; it downgrades inherited calibration",
                "GENERATED_EXPERIMENT != EXECUTED_EXPERIMENT",
                "BACKDOOR_IDENTIFICATION is conditional on the supplied DAG and causal assumptions",
                "HIGHER_ORDER_CONTRAST != CAUSAL_INTERACTION without identifying design",
                "STOCHASTIC_TRANSITION_MODEL != WORLD_TRUTH",
                "MPC_PLAN != EXECUTION and never self-trains",
                "CERTIFIED_SCHEDULE means exhaustive search completed under the declared finite model",
                "HERMETIC_CAPSULE fails closed when the required OS isolation primitive is unavailable",
                "PARETO_BANDIT chooses an experiment candidate; it does not scalarize truth",
                "REPLICATION_GRAPH stores evidence provenance and independence keys, not canonical truth",
            ],
        }

    @staticmethod
    def _feature_map(features: Mapping[str, Any]) -> dict[str, float]:
        out = {}
        for k, v in features.items():
            try:
                out[str(k)] = max(-1.0, min(1.0, float(v)))
            except (TypeError, ValueError):
                continue
        return out

    @staticmethod
    def _poly(features: Mapping[str, Any], max_features: int = 12) -> dict[str, float]:
        f = CollectiveDiscoveryRuntime._feature_map(features)
        keys = sorted(f)[:max_features]
        out = {k: f[k] for k in keys}
        for k in keys:
            out[f"{k}^2"] = f[k] * f[k]
        for i, a in enumerate(keys):
            for b in keys[i+1:]:
                out[f"{a}*{b}"] = f[a] * f[b]
        return out

    def _ood_row(self, scope: str, regime: str):
        return self.s.one("SELECT * FROM collective_v6_ood_models WHERE scope=? AND regime=?", (str(scope), str(regime)))

    def ood_observe(self, features: Mapping[str, Any], regime: str, scope: str = "global") -> dict[str, Any]:
        f = self._feature_map(features)
        row = self._ood_row(scope, regime)
        old_order = json.loads(row["feature_order_json"]) if row else []
        order = sorted(set(old_order) | set(f))
        d = len(order)
        sums = [0.0] * d
        cross = [[0.0] * d for _ in range(d)]
        if row:
            old_s = json.loads(row["sum_json"]); old_c = json.loads(row["cross_json"])
            oi = {k:i for i,k in enumerate(old_order)}
            ni = {k:i for i,k in enumerate(order)}
            for k, i in oi.items():
                sums[ni[k]] = float(old_s[i])
            for a, ia in oi.items():
                for b, ib in oi.items():
                    cross[ni[a]][ni[b]] = float(old_c[ia][ib])
        x = [float(f.get(k, 0.0)) for k in order]
        for i in range(d):
            sums[i] += x[i]
            for j in range(d):
                cross[i][j] += x[i] * x[j]
        now = time.time(); n = (int(row["n"]) if row else 0) + 1
        created = float(row["created_at"]) if row else now
        with self.s._lock, self.s.db:
            self.s.db.execute(
                """INSERT INTO collective_v6_ood_models VALUES(?,?,?,?,?,?,?,?)
                   ON CONFLICT(scope,regime) DO UPDATE SET n=excluded.n,feature_order_json=excluded.feature_order_json,
                   sum_json=excluded.sum_json,cross_json=excluded.cross_json,updated_at=excluded.updated_at""",
                (str(scope), str(regime), n, json.dumps(order), json.dumps(sums), json.dumps(cross), created, now),
            )
        return {"scope": str(scope), "regime": str(regime), "n": n, "feature_order": order}

    def ood_score(self, features: Mapping[str, Any], regime: str, scope: str = "global", ridge: float = 0.05) -> dict[str, Any]:
        f = self._feature_map(features); row = self._ood_row(scope, regime)
        if not row:
            return {"status": "NO_REFERENCE_DISTRIBUTION", "ood_score": 1.0, "reliability": 0.0, "unseen_features": sorted(f)}
        order = json.loads(row["feature_order_json"]); n = int(row["n"])
        sums = [float(v) for v in json.loads(row["sum_json"])]
        cross = [[float(v) for v in r] for r in json.loads(row["cross_json"])]
        d = len(order); mean = [s / max(1, n) for s in sums]
        cov = [[cross[i][j] / max(1, n) - mean[i]*mean[j] for j in range(d)] for i in range(d)]
        for i in range(d): cov[i][i] += max(1e-6, float(ridge))
        inv = _inverse(cov) if d else []
        x = [float(f.get(k, 0.0)) for k in order]
        delta = [x[i]-mean[i] for i in range(d)]
        md2 = max(0.0, _dot(delta, _mat_vec(inv, delta))) if d else 0.0
        normalized = math.sqrt(md2 / max(1, d))
        base = 1.0 - math.exp(-0.5 * normalized * normalized)
        unseen = sorted(set(f) - set(order))
        unseen_fraction = len(unseen) / max(1, len(f))
        score = max(base, unseen_fraction)
        reliability = n / (n + 20.0)
        status = "IN_DISTRIBUTION" if score < .45 else ("SHIFT_WARNING" if score < .75 else "OOD")
        return {
            "status": status, "ood_score": round(_clamp(score), 6), "mahalanobis_normalized": round(normalized, 6),
            "reliability": round(reliability, 6), "n": n, "unseen_features": unseen,
            "law": "OOD downgrades inherited calibration/transfer; it is not evidence that the claim itself is false",
        }

    def nonlinear_predict(self, features: Mapping[str, Any], regime: str, arm_id: str,
                          scope: str = "global", target_coverage: float = .90,
                          ridge: float = 1.0, ood_gain: float = 1.5) -> dict[str, Any]:
        expanded = self._poly(features)
        base = self.science.bayes_predict(expanded, regime, f"NL:{arm_id}", scope, target_coverage, ridge)
        ood = self.ood_score(features, regime, scope)
        inflation = 1.0 + max(0.0, float(ood_gain)) * float(ood["ood_score"])
        mean = float(base["mean"]); half = max(0.0, float(base["upper"]) - float(base["lower"])) / 2.0
        return {
            **base,
            "arm_id": str(arm_id),
            "basis": "POLYNOMIAL_DEGREE_2",
            "expanded_feature_count": len(expanded),
            "ood": ood,
            "calibration_transfer_multiplier": round(inflation, 6),
            "lower": round(_clamp(mean - half * inflation), 6),
            "upper": round(_clamp(mean + half * inflation), 6),
            "law": "polynomial nonlinearization plus OOD inflation is not GP/neural universal inference",
        }

    def nonlinear_observe(self, features: Mapping[str, Any], reward: float, regime: str, arm_id: str,
                          scope: str = "global", actor: str = "agent", weight: float = 1.0,
                          target_coverage: float = .90, ridge: float = 1.0) -> dict[str, Any]:
        self.ood_observe(features, regime, scope)
        expanded = self._poly(features)
        out = self.science.bayes_observe(expanded, reward, regime, f"NL:{arm_id}", scope, actor, weight, target_coverage, ridge)
        return {**out, "basis": "POLYNOMIAL_DEGREE_2", "raw_feature_reference_updated": True}

    def experiment_generate(self, hypotheses: Sequence[Mapping[str, Any]], factors: Sequence[Mapping[str, Any]],
                            max_candidates: int = 256, sample_size: int = 20,
                            cost_weight: float = .10, risk_weight: float = .20) -> dict[str, Any]:
        if len(hypotheses) < 2: raise ValueError("need at least two hypotheses")
        if not factors: raise ValueError("factors must not be empty")
        levels = []
        for f in factors:
            name = str(f.get("name", "")).strip()
            vals = list(f.get("levels", []))
            if not name or not vals: raise ValueError("each factor needs name and non-empty levels")
            levels.append((name, vals, f))
        combos = itertools.product(*[x[1] for x in levels])
        experiments = []
        for idx, values in enumerate(combos):
            if idx >= max(1, min(int(max_candidates), 4096)): break
            assignment = {levels[i][0]: values[i] for i in range(len(levels))}
            cost = risk = 0.0; ethical = True; feasibility = 1.0
            for name, _, meta in levels:
                v = assignment[name]; key = str(v)
                cost += float((meta.get("costs") or {}).get(key, meta.get("cost", 0.0)) or 0.0)
                risk = max(risk, float((meta.get("risks") or {}).get(key, meta.get("risk", 0.0)) or 0.0))
                if v in set(meta.get("forbidden_levels", [])): ethical = False
                feasibility *= _clamp((meta.get("feasibility") or {}).get(key, 1.0) if isinstance(meta.get("feasibility"), dict) else meta.get("feasibility", 1.0))
            likelihoods = {}
            for h in hypotheses:
                hid = str(h.get("id"))
                p = float(h.get("base_p", .5))
                effects = h.get("factor_effects") or {}
                for name, value in assignment.items():
                    p += float(effects.get(f"{name}={value}", 0.0))
                likelihoods[hid] = _clamp(p)
            experiments.append({
                "id": "GEN:" + ",".join(f"{k}={assignment[k]}" for k in sorted(assignment)),
                "assignment": assignment, "likelihoods": likelihoods,
                "cost": cost, "risk": _clamp(risk), "feasibility": _clamp(feasibility), "ethical": ethical,
            })
        design = self.science.experiment_design(hypotheses, experiments, sample_size, .5, cost_weight, risk_weight)
        return {
            **design, "generated_count": len(experiments), "factor_space": [x[0] for x in levels],
            "law": "generated candidates come only from caller-declared factor levels/effect models; generation does not execute the experiment",
        }

    @staticmethod
    def _parse_edges(edges: Sequence[Any]) -> list[tuple[str,str]]:
        out = []
        for e in edges:
            if isinstance(e, Mapping):
                a, b = str(e.get("src", "")), str(e.get("dst", ""))
            else:
                a, b = str(e[0]), str(e[1])
            if a and b: out.append((a,b))
        return out

    @staticmethod
    def _descendants(node: str, edges: Sequence[tuple[str,str]]) -> set[str]:
        children = {}
        for a,b in edges: children.setdefault(a,set()).add(b)
        seen=set(); stack=list(children.get(node,set()))
        while stack:
            x=stack.pop()
            if x in seen: continue
            seen.add(x); stack.extend(children.get(x,set()))
        return seen

    @staticmethod
    def _ancestors(nodes: set[str], edges: Sequence[tuple[str,str]]) -> set[str]:
        parents={}
        for a,b in edges: parents.setdefault(b,set()).add(a)
        seen=set(nodes); stack=list(nodes)
        while stack:
            x=stack.pop()
            for p in parents.get(x,set()):
                if p not in seen: seen.add(p); stack.append(p)
        return seen

    @classmethod
    def _d_separated(cls, x: str, y: str, z: set[str], edges: Sequence[tuple[str,str]]) -> bool:
        anc = cls._ancestors({x,y} | set(z), edges)
        rel = [(a,b) for a,b in edges if a in anc and b in anc]
        und = {n:set() for n in anc}
        parents={}
        for a,b in rel:
            und[a].add(b); und[b].add(a); parents.setdefault(b,[]).append(a)
        for ps in parents.values():
            for i,a in enumerate(ps):
                for b in ps[i+1:]:
                    und[a].add(b); und[b].add(a)
        for n in z:
            und.pop(n, None)
        for ns in und.values():
            ns.difference_update(z)
        if x not in und or y not in und: return True
        seen={x}; stack=[x]
        while stack:
            q=stack.pop()
            if q==y: return False
            for n in und.get(q,set()):
                if n not in seen: seen.add(n); stack.append(n)
        return True

    def causal_identify(self, treatment: str, outcome: str, edges: Sequence[Any],
                        observed_nodes: Sequence[str] | None = None,
                        assumptions: Mapping[str, Any] | None = None,
                        max_adjustment_size: int = 4, actor: str = "agent") -> dict[str, Any]:
        treatment, outcome = str(treatment), str(outcome)
        graph = self._parse_edges(edges); assumptions = dict(assumptions or {})
        if assumptions.get("latent_confounding_possible"):
            status="UNIDENTIFIED_LATENT_CONFOUNDING_RISK"; sets=[]
        else:
            backdoor = [(a,b) for a,b in graph if a != treatment]
            desc = self._descendants(treatment, graph)
            nodes = set(observed_nodes or [n for e in graph for n in e])
            candidates = sorted(nodes - {treatment,outcome} - desc)
            if len(candidates) > 16:
                status="UNIDENTIFIED_SEARCH_SPACE_TOO_LARGE"; sets=[]
            else:
                sets=[]
                for k in range(0, min(max_adjustment_size,len(candidates))+1):
                    for combo in itertools.combinations(candidates,k):
                        if self._d_separated(treatment,outcome,set(combo),backdoor):
                            sets.append(list(combo))
                    if sets: break
                status="IDENTIFIED_BACKDOOR" if sets else "UNIDENTIFIED_NO_BACKDOOR_SET"
        aid=_stable_id("CAUSAL",treatment,outcome,time.time(),status)
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v6_causal_analyses VALUES(?,?,?,?,?,?,?,?,?)",
                (aid,treatment,outcome,status,json.dumps(sets),json.dumps(graph),json.dumps(assumptions),str(actor),time.time()))
        return {
            "analysis_id":aid,"status":status,"treatment":treatment,"outcome":outcome,
            "minimal_adjustment_sets":sets,
            "assumptions":assumptions,
            "law":"backdoor identification is conditional on the supplied DAG, observed-node set, acyclicity/causal sufficiency assumptions, and correct graph semantics",
        }

    def higher_order_interactions(self, experiments: Sequence[Mapping[str, Any]],
                                  max_order: int = 4, design_confidence: float = .5) -> dict[str, Any]:
        if not experiments: raise ValueError("experiments must not be empty")
        interventions = sorted({str(a) for r in experiments for a in r.get("interventions", [])})
        max_order=max(2,min(int(max_order),4,len(interventions)))
        rows=[(set(map(str,r.get("interventions",[]))),float(r["outcome"]),max(0.0,float(r.get("weight",1.0)))) for r in experiments]
        results=[]
        for k in range(2,max_order+1):
            for combo in itertools.combinations(interventions,k):
                cell={}
                for bits in itertools.product([0,1],repeat=k):
                    vals=[y for active,y,w in rows for _ in [0] if all(((combo[i] in active)==bool(bits[i])) for i in range(k))]
                    weights=[w for active,y,w in rows if all(((combo[i] in active)==bool(bits[i])) for i in range(k))]
                    if not vals or sum(weights)<=0:
                        cell[bits]=None
                    else:
                        cell[bits]=sum(v*w for v,w in zip(vals,weights))/sum(weights)
                if any(v is None for v in cell.values()):
                    results.append({"term":"*".join(combo),"order":k,"status":"UNIDENTIFIED","effect":None})
                    continue
                effect=0.0
                for bits,mu in cell.items():
                    parity=sum(bits)
                    effect += ((-1.0)**(k-parity))*float(mu)
                min_support=min(sum(1 for active,y,w in rows if all(((combo[i] in active)==bool(bits[i])) for i in range(k))) for bits in cell)
                confidence=_clamp(design_confidence)*min_support/(min_support+2.0)
                status="CAUSAL_SUPPORTED" if confidence>=.75 else "ASSOCIATIONAL"
                results.append({"term":"*".join(combo),"order":k,"status":status,"effect":round(effect,6),"confidence":round(confidence,6)})
        return {"interactions":results,"law":"all 2^k cells are required; higher-order contrasts remain associational without identifying design"}

    def transition_distribution(self, action_id: str, context: Mapping[str, Any], prior_strength: float = 5.0) -> dict[str, Any]:
        rows=self.s.rows("SELECT before_json,after_json,evidence_weight FROM collective_v5_transition_observations WHERE action_id=? ORDER BY created_at",(str(action_id),))
        if not rows:
            return {"status":"UNSEEN_ACTION","action_id":str(action_id),"n":0,"mean_delta":{},"covariance":{},"next_mean":dict(context)}
        parsed=[]
        features=set()
        for r in rows:
            before=json.loads(r["before_json"]); after=json.loads(r["after_json"]); w=max(0.0,float(r["evidence_weight"]))
            common={k for k in before if k in after and isinstance(before[k],(int,float)) and isinstance(after[k],(int,float))}
            delta={k:float(after[k])-float(before[k]) for k in common}; parsed.append((delta,w));features|=common
        order=sorted(features); W=sum(w for _,w in parsed); kappa=max(1e-6,float(prior_strength));rho=W/(W+kappa)
        means=[]
        for k in order:
            means.append((sum(d.get(k,0.0)*w for d,w in parsed)/W if W else 0.0)*rho)
        cov=[[0.0]*len(order) for _ in order]
        if W:
            raw=[sum(d.get(k,0.0)*w for d,w in parsed)/W for k in order]
            for i,a in enumerate(order):
                for j,b in enumerate(order):
                    cov[i][j]=sum(w*(d.get(a,0.0)-raw[i])*(d.get(b,0.0)-raw[j]) for d,w in parsed)/W
                    if i==j: cov[i][j]+= (1.0-rho)*0.10
        next_mean=dict(context)
        for k,m in zip(order,means):
            if k in next_mean and isinstance(next_mean[k],(int,float)): next_mean[k]=float(next_mean[k])+m
        return {
            "status":"MODELED","action_id":str(action_id),"n":len(rows),"weight_sum":round(W,6),"reliability":round(rho,6),
            "feature_order":order,"mean_delta":{k:round(v,6) for k,v in zip(order,means)},
            "covariance":{order[i]:{order[j]:round(cov[i][j],6) for j in range(len(order))} for i in range(len(order))},
            "next_mean":next_mean,
            "law":"empirical multivariate delta distribution is shrinkage-regularized and remains model-conditional",
        }

    def mpc_plan(self, initial_context: Mapping[str, Any], actions: Sequence[Mapping[str, Any]],
                 horizon: int = 3, beam_width: int = 64, discount: float = .95,
                 risk_aversion: float = .25, prior_strength: float = 5.0) -> dict[str, Any]:
        if not actions: raise ValueError("actions must not be empty")
        horizon=max(1,min(int(horizon),6));beam=max(1,min(int(beam_width),512))
        states=[{"context":dict(initial_context),"return":0.0,"sequence":[],"uncertainty":0.0}]
        for t in range(horizon):
            nxt=[]
            for st in states:
                for a in actions:
                    aid=str(a.get("id",""))
                    if not aid: continue
                    td=self.transition_distribution(aid,st["context"],prior_strength)
                    if a.get("configuration"):
                        reward=float(self.collective.evaluate(a["configuration"])["return_on_group_organization"])
                    else:
                        reward=_clamp(a.get("base_reward",.5))
                    cov=td.get("covariance",{})
                    diag=[float(v.get(k,0.0)) for k,v in cov.items()] if cov else []
                    u=math.sqrt(max(0.0,sum(diag)/max(1,len(diag)))) if diag else (0.5 if td["status"]=="UNSEEN_ACTION" else 0.0)
                    step=reward-max(0.0,float(risk_aversion))*u
                    nxt.append({"context":dict(td.get("next_mean",st["context"])),"return":st["return"]+(discount**t)*step,
                                "sequence":st["sequence"]+[aid],"uncertainty":st["uncertainty"]+u})
            nxt.sort(key=lambda x:(-x["return"],x["uncertainty"],x["sequence"]))
            states=nxt[:beam]
        best=states[0] if states else {"sequence":[],"return":0.0,"uncertainty":0.0}
        return {"decision":"PLAN_ONLY","first_action":best["sequence"][0] if best["sequence"] else None,
                "best_sequence":best["sequence"],"expected_risk_adjusted_return":round(best["return"],6),
                "ranked":[{"sequence":s["sequence"],"return":round(s["return"],6),"uncertainty":round(s["uncertainty"],6)} for s in states[:20]],
                "law":"MPC executes nothing, updates no transition state, and replanning is required after each real observation"}

    @staticmethod
    def _task_fit(task: Mapping[str,Any], worker: Mapping[str,Any]) -> float:
        req=set(map(str,task.get("required_capabilities",[])))
        cap=set(map(str,worker.get("capabilities",[])))
        return 1.0 if not req else len(req&cap)/len(req)

    def schedule_certified(self, tasks: Sequence[Mapping[str, Any]], workers: Sequence[Mapping[str, Any]],
                           horizon: int = 24, budget: Mapping[str, Any] | None = None,
                           max_nodes: int = 200000, exact_task_limit: int = 8,
                           discount: float = .97) -> dict[str, Any]:
        if not tasks or not workers: raise ValueError("tasks and workers must not be empty")
        if len(tasks)>exact_task_limit:
            fallback=self.science.schedule_multiperiod(tasks,workers,horizon,budget,128,"global",discount)
            return {**fallback,"certificate":"NONE","law":"task count exceeded exact-search limit; returned V5 bounded beam schedule"}
        tmap={str(t.get("id")):dict(t) for t in tasks}; wmap={str(w.get("id")):dict(w) for w in workers}
        if "" in tmap or "" in wmap: raise ValueError("tasks/workers require ids")
        B={str(k):max(0.0,float(v)) for k,v in (budget or {}).items()}
        best={"score":0.0,"schedule":[],"budget":dict(B)}; nodes=0; truncated=False
        total_positive=sum(max(0.0,float(t.get("utility",1.0))) for t in tasks)
        def rec(done, finish, free, remaining, score, schedule):
            nonlocal best,nodes,truncated
            nodes+=1
            if nodes>max_nodes: truncated=True; return
            if score>best["score"]:
                best={"score":score,"schedule":[dict(x) for x in schedule],"budget":dict(remaining)}
            optimistic=score+sum(max(0.0,float(tmap[j].get("utility",1.0))) for j in tmap if j not in done)
            if optimistic<=best["score"]+1e-12: return
            eligible=[j for j,t in tmap.items() if j not in done and all(str(d) in done for d in t.get("dependencies",[]))]
            for j in eligible:
                t=tmap[j]; dur=max(1,int(t.get("duration",1))); dep_finish=max([finish.get(str(d),0) for d in t.get("dependencies",[])]+[0])
                for wid,w in wmap.items():
                    fit=self._task_fit(t,w)
                    if fit<=0: continue
                    start=max(free.get(wid,0),dep_finish); end=start+dur
                    if end>horizon: continue
                    rcost={str(k):max(0.0,float(v)) for k,v in (t.get("resource_cost") or {}).items()}
                    if any(k in remaining and rcost.get(k,0.0)>remaining[k]+1e-12 for k in rcost): continue
                    rem=dict(remaining)
                    for k,v in rcost.items():
                        if k in rem: rem[k]-=v
                    utility=max(0.0,float(t.get("utility",1.0)))*fit*(discount**end)
                    deadline=t.get("deadline")
                    if deadline is not None and end>float(deadline): utility*=max(0.0,1.0-.1*(end-float(deadline)))
                    done2=set(done);done2.add(j);finish2=dict(finish);finish2[j]=end;free2=dict(free);free2[wid]=end
                    rec(done2,finish2,free2,rem,score+utility,schedule+[{"task":j,"worker":wid,"start":start,"finish":end,"value":round(utility,6)}])
                    if truncated: return
        rec(set(),{}, {wid:0 for wid in wmap},dict(B),0.0,[])
        cert="EXACT_ENUMERATION_CERTIFIED" if not truncated else "NODE_LIMIT_NO_OPTIMALITY_CERTIFICATE"
        upper=best["score"] if not truncated else total_positive
        return {"schedule":best["schedule"],"score":round(best["score"],6),"remaining_budget":best["budget"],
                "certificate":cert,"nodes_explored":nodes,"upper_bound":round(upper,6),
                "optimality_gap":round(max(0.0,upper-best["score"]),6),
                "law":"certificate is valid only for this finite task/worker/resource model and only when exhaustive search completed"}

    @staticmethod
    def _repo_root() -> Path:
        return Path(__file__).resolve().parent.parent

    def witness_capsule(self, regression_ref: str, timeout_s: float = 20.0) -> dict[str, Any]:
        bwrap=shutil.which("bwrap")
        if not bwrap:
            return {"status":"HERMETIC_UNAVAILABLE","executed":False,"hermetic":False,"required_primitive":"bwrap",
                    "law":"fail closed: the stronger capsule never silently falls back to the non-hermetic witness cell"}
        m=self.science._REGRESSION_REF.fullmatch(str(regression_ref))
        if not m or ".." in m.group(1).split("/"):
            return {"status":"INVALID_REF","executed":False,"hermetic":False}
        rel,cls,method=m.groups();root=self._repo_root();target=(root/rel).resolve()
        if not str(target).startswith(str(root.resolve())) or not target.is_file():
            return {"status":"INVALID_REF","executed":False,"hermetic":False}
        module=rel[:-3].replace("/","."); selector=f"{module}.{cls}.{method}"
        py=sys.executable
        cmd=[bwrap,"--die-with-parent","--unshare-net","--ro-bind",str(root),"/repo","--tmpfs","/tmp","--proc","/proc","--dev","/dev"]
        for p in ("/usr","/lib","/lib64"):
            if os.path.exists(p): cmd += ["--ro-bind",p,p]
        cmd += ["--chdir","/repo",py,"-I","-c",f"import sys;sys.path.insert(0,'/repo');import unittest; r=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromName({selector!r})); raise SystemExit(0 if r.wasSuccessful() else 1)"]
        started=time.time()
        try:
            p=subprocess.run(cmd,text=True,capture_output=True,timeout=max(1.0,min(float(timeout_s),60.0)),env={"PATH":os.environ.get("PATH","/usr/bin:/bin")})
            status="PASS" if p.returncode==0 else "FAIL"
            return {"status":status,"executed":True,"hermetic":True,"returncode":p.returncode,"duration_s":round(time.time()-started,6),
                    "stdout_tail":p.stdout[-4000:],"stderr_tail":p.stderr[-4000:],
                    "isolation":["bwrap","unshare-net","repo-readonly","tmpfs-/tmp","isolated-python"],
                    "law":"hermetic=true here means the declared bubblewrap namespace controls were actually used; it is not a proof against kernel/runtime vulnerabilities"}
        except subprocess.TimeoutExpired:
            return {"status":"TIMEOUT","executed":True,"hermetic":True,"duration_s":round(time.time()-started,6)}

    def pareto_bandit_select(self, candidates: Sequence[Mapping[str,Any]], directions: Mapping[str,Any] | None = None,
                             exploration_weight: float = .5) -> dict[str,Any]:
        if not candidates: raise ValueError("candidates must not be empty")
        directions={str(k):str(v).lower() for k,v in (directions or {}).items()}
        parsed=[]
        metrics=sorted({str(k) for c in candidates for k in (c.get("metrics") or {})})
        for c in candidates:
            m={}
            uncertainty=0.0
            for k in metrics:
                v=(c.get("metrics") or {}).get(k)
                if isinstance(v,Mapping):
                    mean=float(v.get("mean",0.0));sigma=max(0.0,float(v.get("sigma",0.0)))
                else:
                    mean=float(v or 0.0);sigma=0.0
                sign=-1.0 if directions.get(k,"max")=="min" else 1.0
                m[k]={"mean":sign*mean,"low":sign*mean-sigma,"high":sign*mean+sigma,"sigma":sigma}
                uncertainty+=sigma
            parsed.append({"id":str(c.get("id")),"metrics":m,"uncertainty":uncertainty})
        def dominates_low_vs_high(a,b):
            ge=all(a["metrics"][k]["low"]>=b["metrics"][k]["high"] for k in metrics)
            gt=any(a["metrics"][k]["low"]>b["metrics"][k]["high"] for k in metrics)
            return ge and gt
        possible=[]
        for c in parsed:
            if not any(dominates_low_vs_high(o,c) for o in parsed if o is not c): possible.append(c)
        possible.sort(key=lambda c:(-(c["uncertainty"]*max(0.0,float(exploration_weight))),c["id"]))
        return {"decision":"EXPERIMENT_SELECTION_ONLY","possible_frontier":[c["id"] for c in possible],
                "selected":possible[0]["id"] if possible else None,
                "uncertainty":{c["id"]:round(c["uncertainty"],6) for c in possible},
                "law":"interval-Pareto uncertainty can prioritize an experiment; it does not create a single universal value ordering"}

    def claim_register(self, claim_key: str, statement: str, scope: str = "global") -> dict[str,Any]:
        existing=self.s.one("SELECT * FROM collective_v6_claims WHERE claim_key=?",(str(claim_key),))
        if existing: return {"status":"EXISTS","claim_id":existing["claim_id"]}
        now=time.time();cid=_stable_id("CLAIM",claim_key,statement,scope)
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v6_claims VALUES(?,?,?,?,?,?)",(cid,str(claim_key),str(statement),str(scope),now,now))
        return {"status":"REGISTERED","claim_id":cid,"claim_key":str(claim_key)}

    def claim_witness(self, claim_id: str, kind: str, result: str, independence_key: str,
                      confidence: float = 1.0, evidence: Mapping[str,Any] | None = None, actor: str = "agent") -> dict[str,Any]:
        if not self.s.one("SELECT claim_id FROM collective_v6_claims WHERE claim_id=?",(str(claim_id),)): raise ValueError("claim not found")
        kind=str(kind).upper();result=str(result).upper()
        if kind not in {"TEST","REPLICATION","FALSIFIER"}: raise ValueError("invalid witness kind")
        if result not in {"SUPPORTS","FALSIFIES","INCONCLUSIVE"}: raise ValueError("invalid result")
        now=time.time();wid=_stable_id("WIT",claim_id,kind,result,independence_key,now)
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v6_claim_witnesses VALUES(?,?,?,?,?,?,?,?,?)",
                (wid,str(claim_id),kind,result,_clamp(confidence),str(independence_key),json.dumps(evidence or {},sort_keys=True),str(actor),now))
        return {"witness_id":wid,"claim_id":str(claim_id),"kind":kind,"result":result}

    def claim_state(self, claim_id: str, min_independent_support: int = 2) -> dict[str,Any]:
        claim=self.s.one("SELECT * FROM collective_v6_claims WHERE claim_id=?",(str(claim_id),))
        if not claim: raise ValueError("claim not found")
        rows=self.s.rows("SELECT * FROM collective_v6_claim_witnesses WHERE claim_id=? ORDER BY created_at",(str(claim_id),))
        support={r["independence_key"] for r in rows if r["result"]=="SUPPORTS" and float(r["confidence"])>=.5}
        falsify={r["independence_key"] for r in rows if r["result"]=="FALSIFIES" and float(r["confidence"])>=.5}
        if support and falsify: status="CONTESTED"
        elif len(falsify)>=1: status="FALSIFICATION_SIGNAL"
        elif len(support)>=max(1,int(min_independent_support)): status="REPLICATED_SUPPORT"
        elif support: status="PRELIMINARY_SUPPORT"
        else: status="UNRESOLVED"
        return {"claim_id":str(claim_id),"claim_key":claim["claim_key"],"statement":claim["statement"],"status":status,
                "independent_support_groups":len(support),"independent_falsification_groups":len(falsify),
                "witness_count":len(rows),
                "law":"replication/falsification state is evidential metadata and does not silently rewrite canonical semantic truth"}
