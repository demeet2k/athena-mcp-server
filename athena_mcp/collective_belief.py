from __future__ import annotations

import json
import math
import random
import time
from typing import Any, Mapping, Sequence

from .collective_dual_control import CollectiveDualControlRuntime
from .collective_discovery import _clamp, _inverse, _mat_vec, _dot, _stable_id

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v8_beliefs(
 context_key TEXT NOT NULL,
 model_id TEXT NOT NULL,
 weight REAL NOT NULL,
 evidence_count INTEGER NOT NULL,
 metadata_json TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL,
 PRIMARY KEY(context_key,model_id)
);
CREATE TABLE IF NOT EXISTS collective_v8_effect_estimates(
 estimate_id TEXT PRIMARY KEY,
 method TEXT NOT NULL,
 treatment TEXT NOT NULL,
 outcome TEXT NOT NULL,
 estimate REAL,
 status TEXT NOT NULL,
 assumptions_json TEXT NOT NULL,
 witness_json TEXT NOT NULL,
 created_at REAL NOT NULL
);
"""


def _normalize(weights: Mapping[str, float]) -> dict[str, float]:
    vals = {str(k): max(0.0, float(v)) for k, v in weights.items()}
    z = sum(vals.values())
    if z <= 1e-15:
        n = len(vals)
        if not n:
            raise ValueError("belief requires at least one model")
        return {k: 1.0 / n for k in vals}
    return {k: v / z for k, v in vals.items()}


def _entropy(p: Mapping[str, float]) -> float:
    return -sum(v * math.log(v, 2) for v in p.values() if v > 0)


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _cov(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 2:
        return 0.0
    mx = _mean(xs[:n]); my = _mean(ys[:n])
    return sum((xs[i]-mx)*(ys[i]-my) for i in range(n)) / n


class CollectiveBeliefRuntime:
    """V8 finite belief-state / decision-value layer.

    V8 deliberately implements finite, inspectable belief-state operations rather
    than claiming a general Bayes-adaptive POMDP, GP posterior, FCI/PAG theorem or
    nonparametric causal estimator. Beliefs update only from explicit likelihood
    witnesses supplied after observation.
    """

    def __init__(self, dual: CollectiveDualControlRuntime):
        self.dual = dual
        self.discovery = dual.discovery
        self.science = dual.science
        self.s = dual.s
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        q1 = self.s.one("SELECT COUNT(*) AS n FROM collective_v8_beliefs")["n"]
        q2 = self.s.one("SELECT COUNT(*) AS n FROM collective_v8_effect_estimates")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V8",
            "persistent_surfaces": {"belief_rows": q1, "effect_estimates": q2},
            "operators": [
                "belief_register", "belief_state", "belief_observe",
                "decision_evi", "belief_dual_control", "causal_effect_estimate",
                "causal_structure_bootstrap", "contingent_policy", "evidence_spectral",
            ],
            "laws": [
                "BELIEF_POSTERIOR != CANONICAL_TRUTH",
                "LIKELIHOOD_WITNESS != OBSERVATION unless tied to an actual observed outcome",
                "EVI_DESIGN != EXECUTED_EXPERIMENT",
                "BELIEF_DUAL_CONTROL != EXACT_BAYES_ADAPTIVE_POMDP",
                "LINEAR_CAUSAL_ESTIMATE != IDENTIFICATION_OUTSIDE_DECLARED_ASSUMPTIONS",
                "BOOTSTRAP_ASSOCIATION_STABILITY != CAUSAL_GRAPH_TRUTH",
                "CONTINGENT_POLICY_TREE != EXECUTION_HISTORY",
                "SPECTRAL_EVIDENCE_DIVERSITY != FORMAL_INDEPENDENCE_PROOF",
            ],
        }

    def belief_register(self, context_key: str, models: Sequence[Mapping[str, Any]], replace: bool = False) -> dict[str, Any]:
        if not models:
            raise ValueError("models must not be empty")
        raw = {}
        meta = {}
        for i, m in enumerate(models):
            mid = str(m.get("id", f"M{i}"))
            if not mid:
                raise ValueError("model id must not be empty")
            if mid in raw:
                raise ValueError("duplicate model id")
            raw[mid] = max(0.0, float(m.get("prior", 1.0)))
            meta[mid] = dict(m.get("metadata") or {})
        weights = _normalize(raw)
        now = time.time()
        existing = self.s.one("SELECT COUNT(*) AS n FROM collective_v8_beliefs WHERE context_key=?", (str(context_key),))["n"]
        if existing and not replace:
            raise ValueError("belief already exists; set replace=true to reset")
        with self.s._lock, self.s.db:
            if existing:
                self.s.db.execute("DELETE FROM collective_v8_beliefs WHERE context_key=?", (str(context_key),))
            for mid, w in weights.items():
                self.s.db.execute("INSERT INTO collective_v8_beliefs VALUES(?,?,?,?,?,?,?)",
                    (str(context_key), mid, w, 0, json.dumps(meta[mid], sort_keys=True), now, now))
        return self.belief_state(context_key)

    def belief_state(self, context_key: str) -> dict[str, Any]:
        rows = self.s.rows("SELECT * FROM collective_v8_beliefs WHERE context_key=? ORDER BY model_id", (str(context_key),))
        if not rows:
            return {"status":"NOT_FOUND","context_key":str(context_key),"models":[]}
        weights = _normalize({r["model_id"]: float(r["weight"]) for r in rows})
        return {
            "status":"BELIEF_STATE", "context_key":str(context_key),
            "models":[{"id":r["model_id"],"probability":round(weights[r["model_id"]],8),"evidence_count":int(r["evidence_count"]),"metadata":json.loads(r["metadata_json"])} for r in rows],
            "entropy_bits":round(_entropy(weights),8),
            "law":"finite posterior belief is routing/model state and has no independent semantic authority",
        }

    def belief_observe(self, context_key: str, outcome: str, likelihoods: Mapping[str, Any], evidence_ref: str = "", actor: str = "agent") -> dict[str, Any]:
        rows = self.s.rows("SELECT * FROM collective_v8_beliefs WHERE context_key=? ORDER BY model_id", (str(context_key),))
        if not rows:
            raise ValueError("belief not found")
        mids = [r["model_id"] for r in rows]
        if any(mid not in likelihoods for mid in mids):
            raise ValueError("likelihood required for every model")
        prior = _normalize({r["model_id"]: float(r["weight"]) for r in rows})
        raw = {mid: prior[mid] * max(0.0, min(1.0, float(likelihoods[mid]))) for mid in mids}
        posterior = _normalize(raw)
        now = time.time()
        with self.s._lock, self.s.db:
            for r in rows:
                self.s.db.execute("UPDATE collective_v8_beliefs SET weight=?,evidence_count=?,updated_at=? WHERE context_key=? AND model_id=?",
                    (posterior[r["model_id"]], int(r["evidence_count"])+1, now, str(context_key), r["model_id"]))
        out = self.belief_state(context_key)
        return {**out, "observed_outcome":str(outcome), "evidence_ref":str(evidence_ref), "actor":str(actor),
                "prior_entropy_bits":round(_entropy(prior),8), "information_gain_bits":round(max(0.0,_entropy(prior)-out["entropy_bits"]),8),
                "law":"belief update consumes explicit likelihood witnesses for an actual declared observation; posterior does not rewrite canon"}

    @staticmethod
    def _action_utility(action: Mapping[str, Any], belief: Mapping[str, float]) -> float:
        by = action.get("utility_by_model") or {}
        default = float(action.get("utility", 0.0))
        return sum(p * float(by.get(mid, default)) for mid, p in belief.items())

    def _belief_map(self, context_key: str) -> dict[str, float]:
        st = self.belief_state(context_key)
        if st.get("status") != "BELIEF_STATE":
            raise ValueError("belief not found")
        return {m["id"]: float(m["probability"]) for m in st["models"]}

    def decision_evi(self, context_key: str, actions: Sequence[Mapping[str, Any]], experiments: Sequence[Mapping[str, Any]],
                     cost_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str, Any]:
        if not actions or not experiments:
            raise ValueError("actions and experiments must not be empty")
        belief = self._belief_map(context_key)
        current = sorted(((self._action_utility(a, belief), str(a.get("id", ""))) for a in actions), reverse=True)
        current_best, current_action = current[0]
        ranked=[]
        for i,e in enumerate(experiments):
            eid=str(e.get("id",f"E{i}")); ethical=bool(e.get("ethical",True)); outcomes=dict(e.get("outcomes") or {})
            if not outcomes:
                ranked.append({"id":eid,"status":"INCOMPLETE_OUTCOME_MODEL","evi":0.0,"score":0.0}); continue
            expected_post=0.0; branches=[]; complete=True
            for out,like in outcomes.items():
                if any(mid not in like for mid in belief): complete=False; break
                p_out=sum(belief[mid]*_clamp(like[mid]) for mid in belief)
                post=_normalize({mid:belief[mid]*_clamp(like[mid]) for mid in belief}) if p_out>1e-15 else dict(belief)
                vals=[(self._action_utility(a,post),str(a.get("id",""))) for a in actions]
                best=max(vals)
                expected_post += p_out*best[0]
                branches.append({"outcome":str(out),"probability":round(p_out,8),"posterior":{k:round(v,8) for k,v in post.items()},"best_action":best[1],"best_utility":round(best[0],8)})
            if not complete:
                ranked.append({"id":eid,"status":"INCOMPLETE_OUTCOME_MODEL","evi":0.0,"score":0.0}); continue
            evi=max(0.0, expected_post-current_best)
            cost=max(0.0,float(e.get("cost",0.0))); risk=_clamp(e.get("risk",0.0)); feasibility=_clamp(e.get("feasibility",1.0))
            score=0.0 if not ethical else evi*feasibility-max(0.0,float(cost_weight))*cost-max(0.0,float(risk_weight))*risk
            ranked.append({"id":eid,"status":"ELIGIBLE" if ethical else "ETHICS_BLOCK","evi":round(evi,8),"score":round(score,8),"expected_post_decision_utility":round(expected_post,8),"branches":branches,"cost":cost,"risk":risk})
        ranked.sort(key=lambda x:(-float(x.get("score",0)), -float(x.get("evi",0)), x["id"]))
        winner=next((r["id"] for r in ranked if r["status"]=="ELIGIBLE"),None)
        return {"decision":"DESIGN_ONLY","context_key":str(context_key),"current_best_action":current_action,"current_best_utility":round(current_best,8),"winner":winner,"ranked":ranked,
                "law":"EVI measures expected improvement in downstream decision utility under the supplied finite belief/action/outcome model; design is not evidence"}

    def belief_dual_control(self, context_key: str, actions: Sequence[Mapping[str, Any]], discount: float = .95,
                            information_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str, Any]:
        if not actions:
            raise ValueError("actions must not be empty")
        belief=self._belief_map(context_key); rows=[]
        for i,a in enumerate(actions):
            aid=str(a.get("id",f"A{i}")); immediate=self._action_utility(a,belief)
            obs=dict(a.get("observation_model") or {}); future=current_best=0.0; info=0.0; branches=[]
            if obs:
                h0=_entropy(belief)
                for out,like in obs.items():
                    if any(mid not in like for mid in belief):
                        raise ValueError(f"action {aid} observation model incomplete")
                    p_out=sum(belief[mid]*_clamp(like[mid]) for mid in belief)
                    post=_normalize({mid:belief[mid]*_clamp(like[mid]) for mid in belief}) if p_out>1e-15 else dict(belief)
                    best=max((self._action_utility(b,post),str(b.get("id",""))) for b in actions)
                    future += p_out*best[0]
                    info += p_out*(h0-_entropy(post))
                    branches.append({"outcome":str(out),"probability":round(p_out,8),"best_next_action":best[1],"posterior":{k:round(v,8) for k,v in post.items()}})
            else:
                future=max(self._action_utility(b,belief) for b in actions)
            risk=_clamp(a.get("risk",0.0)); cost=max(0.0,float(a.get("cost",0.0)))
            score=immediate+max(0.0,min(1.0,float(discount)))*future+max(0.0,float(information_weight))*info-max(0.0,float(risk_weight))*risk-cost
            rows.append({"id":aid,"score":round(score,8),"immediate_utility":round(immediate,8),"expected_next_decision_utility":round(future,8),"expected_information_gain_bits":round(info,8),"risk":risk,"cost":cost,"branches":branches})
        rows.sort(key=lambda x:(-x["score"],x["id"]))
        return {"decision":"BELIEF_DUAL_CONTROL_DEPTH1_PLAN_ONLY","selected":rows[0]["id"],"ranked":rows,
                "law":"one-step finite-belief controller values control plus future decision utility plus information; it executes nothing and is not an exact Bayes-adaptive POMDP"}

    @staticmethod
    def _numeric_samples(samples: Sequence[Mapping[str,Any]], names: Sequence[str]) -> dict[str,list[float]]:
        out={str(k):[] for k in names}
        for r in samples:
            for k in out:
                if k not in r or not isinstance(r[k],(int,float)):
                    raise ValueError(f"numeric sample missing {k}")
                out[k].append(float(r[k]))
        return out

    @staticmethod
    def _linear_coef(y: Sequence[float], cols: Sequence[Sequence[float]], ridge: float = 1e-8) -> list[float]:
        n=len(y); p=len(cols)+1
        A=[[0.0]*p for _ in range(p)]; b=[0.0]*p
        for t in range(n):
            phi=[1.0]+[float(c[t]) for c in cols]
            for i in range(p):
                b[i]+=phi[i]*float(y[t])
                for j in range(p): A[i][j]+=phi[i]*phi[j]
        for i in range(1,p): A[i][i]+=max(1e-12,float(ridge))
        return _mat_vec(_inverse(A),b)

    def causal_effect_estimate(self, method: str, samples: Sequence[Mapping[str,Any]], treatment: str, outcome: str,
                               adjustment: Sequence[str] | None = None, mediator: str | None = None,
                               instrument: str | None = None, assumptions: Mapping[str,Any] | None = None) -> dict[str,Any]:
        if len(samples)<6: raise ValueError("need at least six samples")
        method=str(method).upper(); assumptions=dict(assumptions or {})
        names=[str(treatment),str(outcome)]+list(map(str,adjustment or []))
        if mediator: names.append(str(mediator))
        if instrument: names.append(str(instrument))
        d=self._numeric_samples(samples,list(dict.fromkeys(names)))
        status="ESTIMATED_UNDER_ASSUMPTIONS"; est=None; witness={}
        if assumptions.get("latent_confounding_possible"):
            return {"status":"UNIDENTIFIED_LATENT_CONFOUNDING_RISK","method":method,"estimate":None,"assumptions":assumptions}
        if method=="BACKDOOR_LINEAR":
            z=list(map(str,adjustment or [])); beta=self._linear_coef(d[outcome],[d[treatment]]+[d[k] for k in z])
            est=beta[1]; witness={"adjustment":z,"model":"linear outcome regression"}
        elif method=="IV_WALD":
            if not instrument: raise ValueError("instrument required")
            czt=_cov(d[instrument],d[treatment]); czy=_cov(d[instrument],d[outcome])
            scale=math.sqrt(max(1e-15,_cov(d[instrument],d[instrument])*_cov(d[treatment],d[treatment])))
            strength=abs(czt)/scale if scale>0 else 0.0
            if abs(czt)<1e-8 or strength<.05:
                status="WEAK_OR_INVALID_INSTRUMENT"; est=None
            else: est=czy/czt
            witness={"instrument":str(instrument),"first_stage_abs_correlation":round(strength,8),"model":"Wald covariance ratio"}
        elif method=="FRONTDOOR_LINEAR":
            if not mediator: raise ValueError("mediator required")
            alpha=self._linear_coef(d[mediator],[d[treatment]])[1]
            beta=self._linear_coef(d[outcome],[d[mediator],d[treatment]])[1]
            est=alpha*beta; witness={"mediator":str(mediator),"treatment_to_mediator":alpha,"mediator_to_outcome_adjusted_for_treatment":beta,"model":"linear product-of-coefficients mediation proxy"}
        else:
            raise ValueError("method must be BACKDOOR_LINEAR, IV_WALD or FRONTDOOR_LINEAR")
        eid=_stable_id("EFFECT",method,treatment,outcome,time.time())
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v8_effect_estimates VALUES(?,?,?,?,?,?,?,?,?)",
                (eid,method,str(treatment),str(outcome),None if est is None else float(est),status,json.dumps(assumptions,sort_keys=True),json.dumps(witness,sort_keys=True),time.time()))
        return {"estimate_id":eid,"status":status,"method":method,"treatment":str(treatment),"outcome":str(outcome),"estimate":None if est is None else round(float(est),8),"witness":witness,"assumptions":assumptions,
                "law":"numeric estimate is conditional on the declared identification/design assumptions and the explicit linear/Wald model; estimation does not prove identification"}

    def causal_structure_bootstrap(self, samples: Sequence[Mapping[str,Any]], variables: Sequence[str] | None = None,
                                   association_threshold: float = .15, resamples: int = 50, support_threshold: float = .7, seed: int = 0) -> dict[str,Any]:
        if len(samples)<8: raise ValueError("need at least eight samples")
        B=max(5,min(int(resamples),300)); rng=random.Random(int(seed)); edge_counts={}; collider_counts={}
        for _ in range(B):
            boot=[samples[rng.randrange(len(samples))] for _ in range(len(samples))]
            sk=self.dual.causal_skeleton_discover(boot,variables,association_threshold,1)
            for e in sk["undirected_edges"]:
                key=tuple(sorted((e["a"],e["b"]))); edge_counts[key]=edge_counts.get(key,0)+1
            for v in sk["v_structure_candidates"]:
                key=(v["left"],v["collider"],v["right"]); collider_counts[key]=collider_counts.get(key,0)+1
        tau=_clamp(support_threshold)
        edges=[{"a":a,"b":b,"support":round(c/B,6),"endpoint":"o-o"} for (a,b),c in sorted(edge_counts.items()) if c/B>=tau]
        cols=[{"left":a,"collider":z,"right":b,"support":round(c/B,6),"pattern":"-> <-"} for (a,z,b),c in sorted(collider_counts.items()) if c/B>=tau]
        return {"status":"BOOTSTRAP_ASSOCIATION_STABILITY","resamples":B,"support_threshold":tau,"stable_edges":edges,"stable_v_structure_candidates":cols,
                "law":"bootstrap frequency measures stability of the heuristic association-skeleton procedure; it is not calibrated causal-edge probability or FCI/PAG truth"}

    def contingent_policy(self, context_key: str, actions: Sequence[Mapping[str,Any]], experiment: Mapping[str,Any]) -> dict[str,Any]:
        belief=self._belief_map(context_key); outcomes=dict(experiment.get("outcomes") or {})
        if not outcomes: raise ValueError("experiment outcomes required")
        branches=[]
        for out,like in outcomes.items():
            if any(mid not in like for mid in belief): raise ValueError("likelihood required for every model")
            p=sum(belief[mid]*_clamp(like[mid]) for mid in belief)
            post=_normalize({mid:belief[mid]*_clamp(like[mid]) for mid in belief}) if p>1e-15 else dict(belief)
            best=max((self._action_utility(a,post),str(a.get("id",""))) for a in actions)
            branches.append({"outcome":str(out),"probability":round(p,8),"action":best[1],"posterior":{k:round(v,8) for k,v in post.items()},"utility":round(best[0],8)})
        return {"decision":"CONTINGENT_POLICY_DEPTH1_DESIGN_ONLY","experiment_id":str(experiment.get("id","E")),"branches":branches,
                "law":"branch-specific actions are a depth-1 policy design under supplied likelihoods; no observation, belief update or execution occurs"}

    @staticmethod
    def _sim(a: Mapping[str,Any], b: Mapping[str,Any], dims: Sequence[str]) -> float:
        compared=0; same=0
        for d in dims:
            if d in a and d in b and a[d] not in (None,"") and b[d] not in (None,""):
                compared+=1; same += 1 if a[d]==b[d] else 0
        return .5 if compared==0 else same/compared

    def evidence_spectral(self, claim_id: str, dimensions: Sequence[str] | None = None, min_confidence: float = .5) -> dict[str,Any]:
        dims=list(dimensions or ["dataset","implementation","method","operator","environment","seed_family"])
        rows=self.s.rows("SELECT * FROM collective_v6_claim_witnesses WHERE claim_id=? ORDER BY created_at",(str(claim_id),))
        rows=[r for r in rows if float(r["confidence"])>=_clamp(min_confidence)]
        if not rows: return {"status":"NO_ELIGIBLE_WITNESSES","claim_id":str(claim_id),"raw_n":0}
        ev=[json.loads(r["evidence_json"]) for r in rows]; w=[max(1e-9,float(r["confidence"])) for r in rows]; n=len(rows)
        S=[[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if rows[i]["independence_key"]==rows[j]["independence_key"]: s=1.0
                elif i==j: s=1.0
                else: s=self._sim(ev[i],ev[j],dims)
                S[i][j]=s
        den=sum(w[i]*w[j]*S[i][j] for i in range(n) for j in range(n)); neff=(sum(w)**2)/den if den>1e-15 else float(n)
        trace=sum(S[i][i] for i in range(n)); fro2=sum(S[i][j]*S[i][j] for i in range(n) for j in range(n)); spectral_pr=(trace*trace/fro2) if fro2>1e-15 else 0.0
        return {"status":"SPECTRAL_DIVERSITY_PROXY","claim_id":str(claim_id),"raw_n":n,"effective_n":round(neff,8),"spectral_participation_ratio":round(spectral_pr,8),"similarity_matrix":[[round(x,6) for x in r] for r in S],"dimensions":dims,
                "law":"participation ratio and effective-N summarize metadata redundancy; neither proves formal statistical independence"}
