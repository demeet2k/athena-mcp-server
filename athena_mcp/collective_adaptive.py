from __future__ import annotations

import itertools
import json
import math
import random
import time
from typing import Any, Mapping, Sequence

from .collective_probabilistic import (
    CollectiveProbabilisticRuntime,
    _dot,
    _fit_logistic,
    _logit,
    _mat_vec,
    _mean,
    _predict_logistic,
    _rbf,
    _sigmoid,
    _variance,
)
from .collective_discovery import _inverse

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v11_gp_hyperfits(
 fit_id TEXT PRIMARY KEY,
 context_key TEXT NOT NULL,
 observation_count INTEGER NOT NULL,
 candidate_count INTEGER NOT NULL,
 best_json TEXT NOT NULL,
 applied INTEGER NOT NULL,
 created_at REAL NOT NULL
);
"""


def _cholesky(a: Sequence[Sequence[float]], jitter: float = 1e-10) -> list[list[float]]:
    n = len(a)
    for attempt in range(8):
        add = jitter * (10 ** attempt)
        L = [[0.0] * n for _ in range(n)]
        ok = True
        for i in range(n):
            for j in range(i + 1):
                s = sum(L[i][k] * L[j][k] for k in range(j))
                if i == j:
                    v = float(a[i][i]) + add - s
                    if v <= 0:
                        ok = False
                        break
                    L[i][j] = math.sqrt(v)
                else:
                    if abs(L[j][j]) <= 1e-15:
                        ok = False
                        break
                    L[i][j] = (float(a[i][j]) - s) / L[j][j]
            if not ok:
                break
        if ok:
            return L
    raise ValueError("matrix is not positive definite")


def _logdet_spd(a: Sequence[Sequence[float]]) -> float:
    L = _cholesky(a)
    return 2.0 * sum(math.log(max(1e-300, L[i][i])) for i in range(len(L)))


def _poly_names(keys: Sequence[str], degree: int) -> list[str]:
    base = [str(k) for k in keys]
    if degree <= 1:
        return base
    out = list(base)
    out += [f"sq::{k}" for k in base]
    for i in range(len(base)):
        for j in range(i + 1, len(base)):
            out.append(f"int::{base[i]}::{base[j]}")
    return out


def _poly_row(row: Mapping[str, Any], keys: Sequence[str], degree: int) -> dict[str, float]:
    base = {str(k): float(row[k]) for k in keys}
    if degree <= 1:
        return base
    out = dict(base)
    for k in keys:
        out[f"sq::{k}"] = float(row[k]) ** 2
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            out[f"int::{keys[i]}::{keys[j]}"] = float(row[keys[i]]) * float(row[keys[j]])
    return out


def _logloss(y: float, p: float) -> float:
    q = max(1e-9, min(1.0 - 1e-9, float(p)))
    return -(float(y) * math.log(q) + (1.0 - float(y)) * math.log(1.0 - q))


class _NodeLimit(Exception):
    pass


class CollectiveAdaptiveRuntime:
    """V11 adaptive-world-model layer.

    This layer learns bounded GP hyperparameters, values GP measurements by downstream
    decisions, exposes a supplied-DAG latent projection, adds a stacked nonlinear
    nuisance TMLE, a risk-ratio bias-factor sensitivity surface, an exact finite-model
    Bayes-adaptive POMDP for bounded horizons, and model-conditional uncertainty for
    evidence-dependence predictions.
    """

    def __init__(self, probabilistic: CollectiveProbabilisticRuntime):
        self.probabilistic = probabilistic
        self.inference = probabilistic.inference
        self.belief = probabilistic.belief
        self.s = probabilistic.s
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        hf = self.s.one("SELECT COUNT(*) AS n FROM collective_v11_gp_hyperfits")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V11",
            "persistent_surfaces": {"gp_hyperfits": hf},
            "operators": [
                "gp_hyperfit", "gp_decision_evsi", "latent_project_admg",
                "causal_tmle_ensemble", "sensitivity_rr_surface",
                "bapomdp_solve", "evidence_dependence_interval",
            ],
            "laws": [
                "MARGINAL_LIKELIHOOD_OPTIMUM != TRUE_KERNEL",
                "GP_DECISION_EVSI != OBSERVATION",
                "SUPPLIED_DAG_LATENT_PROJECTION != DATA_DISCOVERED_PAG",
                "STACKED_TMLE != SUPER_LEARNER_THEOREM",
                "RR_BIAS_FACTOR_SURFACE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND",
                "FINITE_MODEL_BAPOMDP != GENERAL_BAYES_ADAPTIVE_CONTROL",
                "LAPLACE_DEPENDENCE_INTERVAL != CALIBRATED_COVERAGE_GUARANTEE",
            ],
        }

    # ---------- adaptive GP hyperparameters ----------
    def gp_hyperfit(self, context_key: str,
                    length_scales: Sequence[float] | None = None,
                    signal_variances: Sequence[float] | None = None,
                    noise_variances: Sequence[float] | None = None,
                    apply: bool = False,
                    expected_observation_count: int | None = None) -> dict[str, Any]:
        row = self.probabilistic._gp_row(context_key)
        obs = json.loads(row["observations_json"])
        if len(obs) < 3:
            raise ValueError("GP hyperfit requires at least three observed rows")
        ls_grid = [float(x) for x in (length_scales or [.25, .5, 1.0, 2.0, 4.0])]
        sv_grid = [float(x) for x in (signal_variances or [.25, .5, 1.0, 2.0, 4.0])]
        nv_grid = [float(x) for x in (noise_variances or [.005, .02, .05, .1, .25])]
        if not ls_grid or not sv_grid or not nv_grid or len(ls_grid) * len(sv_grid) * len(nv_grid) > 512:
            raise ValueError("hyperparameter grid must contain 1..512 combinations")
        if any(x <= 0 for x in ls_grid + sv_grid + nv_grid):
            raise ValueError("all GP hyperparameters must be positive")
        y = [float(o["y"]) for o in obs]
        n = len(obs)
        ranked = []
        for ls, sv, nv in itertools.product(ls_grid, sv_grid, nv_grid):
            K = [[_rbf(obs[i]["x"], obs[j]["x"], ls, sv) for j in range(n)] for i in range(n)]
            for i in range(n):
                K[i][i] += nv + 1e-9
            try:
                Ki = _inverse(K)
                quad = _dot(y, _mat_vec(Ki, y))
                logdet = _logdet_spd(K)
                lml = -0.5 * quad - 0.5 * logdet - 0.5 * n * math.log(2.0 * math.pi)
            except Exception:
                continue
            ranked.append({"length_scale": ls, "signal_variance": sv, "noise_variance": nv, "log_marginal_likelihood": lml})
        if not ranked:
            raise ValueError("no numerically valid GP hyperparameter candidate")
        ranked.sort(key=lambda r: (r["log_marginal_likelihood"], -r["length_scale"], -r["signal_variance"], -r["noise_variance"]), reverse=True)
        best = ranked[0]
        applied = False
        if apply:
            if expected_observation_count is None:
                raise ValueError("expected_observation_count required when apply=true")
            current = len(json.loads(self.probabilistic._gp_row(context_key)["observations_json"]))
            if int(expected_observation_count) != current:
                raise ValueError(f"STALE_GP expected_observation_count={expected_observation_count} current={current}")
            with self.s._lock, self.s.db:
                self.s.db.execute(
                    "UPDATE collective_v10_gp_models SET length_scale=?,signal_variance=?,noise_variance=?,updated_at=? WHERE context_key=?",
                    (best["length_scale"], best["signal_variance"], best["noise_variance"], time.time(), str(context_key)),
                )
            applied = True
        fit_id = f"HYPF.{int(time.time()*1000000)}"
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT INTO collective_v11_gp_hyperfits VALUES(?,?,?,?,?,?,?)", (
                fit_id, str(context_key), n, len(ranked), json.dumps(best, sort_keys=True), 1 if applied else 0, time.time(),
            ))
        return {
            "status": "GP_HYPERPARAMETERS_APPLIED" if applied else "GP_HYPERPARAMETER_DESIGN_ONLY",
            "fit_id": fit_id, "context_key": str(context_key), "observation_count": n,
            "candidate_count": len(ranked), "best": {**best, "log_marginal_likelihood": round(best["log_marginal_likelihood"], 10)},
            "top_candidates": [{**r, "log_marginal_likelihood": round(r["log_marginal_likelihood"], 10)} for r in ranked[:10]],
            "applied": applied,
            "law": "marginal-likelihood optimum is conditional on the supplied finite grid, RBF family and observations; it is not proof of the true kernel",
        }

    def _gp_joint(self, context_key: str, points: Sequence[Mapping[str, Any]]):
        row = self.probabilistic._gp_row(context_key); order = json.loads(row["feature_order_json"])
        xs = []
        for p in points:
            if any(k not in p for k in order):
                raise ValueError("feature value required for every GP feature")
            xs.append([float(p[k]) for k in order])
        obs = json.loads(row["observations_json"]); ls=float(row["length_scale"]); sv=float(row["signal_variance"]); nv=float(row["noise_variance"])
        m = len(xs); means=[0.0]*m; cov=[[ _rbf(xs[i],xs[j],ls,sv) for j in range(m)] for i in range(m)]
        if obs:
            n=len(obs); K=[[_rbf(obs[i]["x"],obs[j]["x"],ls,sv) for j in range(n)] for i in range(n)]
            for i in range(n): K[i][i]+=nv+1e-9
            Ki=_inverse(K); y=[float(o["y"]) for o in obs]; alpha=_mat_vec(Ki,y)
            ks=[]
            for x in xs:
                k=[_rbf(o["x"],x,ls,sv) for o in obs]; ks.append(k); means[len(ks)-1]=_dot(k,alpha)
            for i in range(m):
                for j in range(m):
                    cov[i][j]-=_dot(ks[i],_mat_vec(Ki,ks[j]))
        for i in range(m): cov[i][i]=max(0.0,cov[i][i])
        return order, means, cov, nv

    def gp_decision_evsi(self, context_key: str, actions: Sequence[Mapping[str, Any]], experiments: Sequence[Mapping[str, Any]],
                         samples: int = 300, seed: int = 0, cost_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str, Any]:
        if not actions or not experiments:
            raise ValueError("actions and experiments must not be empty")
        if len(actions)>64 or len(experiments)>128:
            raise ValueError("too many GP decision actions/experiments")
        points=[a.get("features") or {} for a in actions]+[e.get("features") or {} for e in experiments]
        _, means, cov, model_nv=self._gp_joint(context_key,points)
        na=len(actions); n=max(50,min(int(samples),2000))
        current=[]
        for i,a in enumerate(actions):
            scale=float(a.get("utility_scale",1.0)); offset=float(a.get("utility_offset",0.0))
            current.append((offset+scale*means[i],str(a.get("id",f"A{i}"))))
        current_best=max(current)
        ranked=[]
        for j,e in enumerate(experiments):
            eid=str(e.get("id",f"E{j}")); idx=na+j
            ethical=bool(e.get("ethical",True)); feasibility=max(0.0,min(1.0,float(e.get("feasibility",1.0))))
            cost=max(0.0,float(e.get("cost",0.0))); risk=max(0.0,min(1.0,float(e.get("risk",0.0))))
            enoise=max(1e-12,float(e.get("noise_variance",model_nv))); obs_var=max(1e-12,cov[idx][idx]+enoise)
            rng=random.Random(int(seed)+104729*(j+1)); post=[]
            for _ in range(n):
                y=rng.gauss(means[idx],math.sqrt(obs_var)); best=-float("inf")
                innovation=y-means[idx]
                for i,a in enumerate(actions):
                    updated=means[i]+cov[i][idx]/obs_var*innovation
                    val=float(a.get("utility_offset",0.0))+float(a.get("utility_scale",1.0))*updated
                    if val>best: best=val
                post.append(best)
            evsi=max(0.0,_mean(post)-current_best[0]); mcse=math.sqrt(max(0.0,_variance(post))/n)
            score=0.0 if not ethical else evsi*feasibility-max(0.0,float(cost_weight))*cost-max(0.0,float(risk_weight))*risk
            ranked.append({"id":eid,"status":"ELIGIBLE" if ethical else "ETHICS_BLOCK","evsi":round(evsi,10),"score":round(score,10),"monte_carlo_se":round(mcse,10),"samples":n,"cost":cost,"risk":risk,"feasibility":feasibility})
        ranked.sort(key=lambda r:(r["score"],r["evsi"],-r["cost"],r["id"]),reverse=True)
        eligible=[r for r in ranked if r["status"]=="ELIGIBLE"]
        return {"decision":"GP_DECISION_EVSI_DESIGN_ONLY","context_key":str(context_key),"current_best_action":current_best[1],"current_best_expected_utility":round(current_best[0],10),"winner":eligible[0]["id"] if eligible else None,"ranked":ranked,
                "law":"GP EVSI values a hypothetical measurement by downstream posterior-mean decision improvement under the current GP; no hypothetical sample is an observation or training row"}

    # ---------- supplied-DAG latent projection ----------
    def latent_project_admg(self, edges: Sequence[Mapping[str, Any]], latent_nodes: Sequence[str], observed_nodes: Sequence[str] | None = None) -> dict[str, Any]:
        latent={str(x) for x in latent_nodes}; pairs=[]; nodes=set()
        for e in edges:
            a=str(e.get("src","")); b=str(e.get("dst",""))
            if not a or not b or a==b: raise ValueError("DAG edges require distinct src/dst")
            pairs.append((a,b)); nodes|={a,b}
        obs=set(str(x) for x in observed_nodes) if observed_nodes is not None else nodes-latent
        if not obs or obs & latent: raise ValueError("observed and latent node sets must be nonempty/disjoint")
        if not obs <= nodes: raise ValueError("observed node absent from DAG")
        adj={n:[] for n in nodes}
        for a,b in pairs: adj[a].append(b)
        color={n:0 for n in nodes}
        def dfs(n):
            color[n]=1
            for v in adj[n]:
                if color[v]==1: raise ValueError("supplied causal graph must be a DAG")
                if color[v]==0: dfs(v)
            color[n]=2
        for n in sorted(nodes):
            if color[n]==0: dfs(n)
        def path_latent_internal(src,dst):
            stack=[src]; seen={src}
            while stack:
                u=stack.pop()
                for v in adj[u]:
                    if v==dst: return True
                    if v in latent and v not in seen:
                        seen.add(v); stack.append(v)
            return False
        directed=[]
        for x in sorted(obs):
            for y in sorted(obs):
                if x!=y and path_latent_internal(x,y): directed.append((x,y))
        def latent_reaches(l,target):
            stack=[l]; seen={l}
            while stack:
                u=stack.pop()
                for v in adj[u]:
                    if v==target: return True
                    if v in latent and v not in seen:
                        seen.add(v); stack.append(v)
            return False
        bidirected=[]; witnesses={}
        ol=sorted(obs)
        for i in range(len(ol)):
            for j in range(i+1,len(ol)):
                x,y=ol[i],ol[j]; ws=[l for l in sorted(latent) if latent_reaches(l,x) and latent_reaches(l,y)]
                if ws:
                    bidirected.append((x,y)); witnesses[f"{x}<->{y}"]=ws
        marks=[{"src":x,"dst":y,"mark":"tail-arrow","edge":"->"} for x,y in sorted(set(directed))]
        marks += [{"src":x,"dst":y,"mark":"arrow-arrow","edge":"<->","latent_witnesses":witnesses[f"{x}<->{y}"]} for x,y in bidirected]
        return {"status":"RESTRICTED_LATENT_PROJECTION_ADMG","observed_nodes":sorted(obs),"latent_nodes":sorted(latent),"directed_edges":[{"src":x,"dst":y} for x,y in sorted(set(directed))],"bidirected_edges":[{"a":x,"b":y,"latent_witnesses":witnesses[f"{x}<->{y}"]} for x,y in bidirected],"endpoint_marks":marks,
                "law":"this is an exact restricted latent projection for the supplied DAG using latent-only internal directed paths/common latent ancestors; it is not data-discovered FCI/PAG evidence"}

    # ---------- stacked nuisance TMLE ----------
    def _ensemble_model(self, train: Sequence[Mapping[str,float]], label: str, base_keys: Sequence[str], role: str):
        if len(train)<12: raise ValueError("ensemble nuisance training set too small")
        if role=="propensity": specs=[([],1),(list(base_keys),1),(list(base_keys),2)]
        else:
            specs=[(["T"],1),(list(base_keys),1),(list(base_keys),2)]
        unique=[]; seen=set()
        for keys,deg in specs:
            sig=(tuple(keys),deg)
            if sig not in seen: seen.add(sig); unique.append((keys,deg))
        inner_train=[r for i,r in enumerate(train) if i%4!=0]; val=[r for i,r in enumerate(train) if i%4==0]
        if not val or not inner_train: inner_train=list(train[:-max(1,len(train)//4)]); val=list(train[len(inner_train):])
        losses=[]
        for keys,deg in unique:
            names=_poly_names(keys,deg)
            tr=[]; va=[]
            for r in inner_train:
                z=_poly_row(r,keys,deg); z[label]=float(r[label]); tr.append(z)
            for r in val:
                z=_poly_row(r,keys,deg); z[label]=float(r[label]); va.append(z)
            beta=_fit_logistic(tr,label,names)
            loss=_mean([_logloss(v[label],_predict_logistic(beta,v,names)) for v in va])
            losses.append(loss)
        m=min(losses); raw=[math.exp(-8.0*(x-m)) for x in losses]; z=sum(raw); weights=[x/z for x in raw]
        fitted=[]
        for (keys,deg),w in zip(unique,weights):
            names=_poly_names(keys,deg); full=[]
            for r in train:
                q=_poly_row(r,keys,deg); q[label]=float(r[label]); full.append(q)
            fitted.append({"keys":keys,"degree":deg,"names":names,"beta":_fit_logistic(full,label,names),"weight":w})
        return fitted, [{"features":m0["keys"],"degree":m0["degree"],"weight":round(m0["weight"],8),"validation_log_loss":round(losses[i],8)} for i,m0 in enumerate(fitted)]

    @staticmethod
    def _ensemble_predict(models, row):
        out=0.0
        for m in models:
            q=_poly_row(row,m["keys"],m["degree"]); out+=m["weight"]*_predict_logistic(m["beta"],q,m["names"])
        return max(1e-6,min(1.0-1e-6,out))

    def causal_tmle_ensemble(self, samples: Sequence[Mapping[str,Any]], treatment: str, outcome: str,
                             adjustment: Sequence[str] | None = None, assumptions: Mapping[str,Any] | None = None,
                             propensity_clip: float = .05) -> dict[str,Any]:
        if len(samples)<60: raise ValueError("stacked TMLE requires at least sixty samples")
        assumptions=dict(assumptions or {})
        if assumptions.get("latent_confounding_possible"):
            return {"status":"UNIDENTIFIED_LATENT_CONFOUNDING_RISK","estimate":None,"method":"TMLE_STACKED_ENSEMBLE_CROSSFIT"}
        z=[str(v) for v in (adjustment or [])]; rows=[]
        for r in samples:
            if treatment not in r or outcome not in r or any(k not in r for k in z): raise ValueError("stacked TMLE sample missing required field")
            t=float(r[treatment]); y=float(r[outcome])
            if t not in (0.0,1.0) or y not in (0.0,1.0): raise ValueError("stacked TMLE requires binary treatment and outcome")
            q={"T":t,"Y":y}; q.update({k:float(r[k]) for k in z}); rows.append(q)
        n=len(rows); clip=max(.01,min(.25,float(propensity_clip))); e=[.5]*n; q0=[.5]*n; q1=[.5]*n; qobs=[.5]*n; libraries=[]
        for fold in (0,1):
            train=[rows[i] for i in range(n) if i%2!=fold]; test=[i for i in range(n) if i%2==fold]
            prop,pl=self._ensemble_model(train,"T",z,"propensity")
            out,ol=self._ensemble_model(train,"Y",["T"]+z,"outcome")
            libraries.append({"fold":fold,"propensity":pl,"outcome":ol})
            for i in test:
                base={k:rows[i][k] for k in z}; ei=max(clip,min(1.0-clip,self._ensemble_predict(prop,base))); e[i]=ei
                r0={"T":0.0,**base}; r1={"T":1.0,**base}; q0[i]=self._ensemble_predict(out,r0); q1[i]=self._ensemble_predict(out,r1); qobs[i]=q1[i] if rows[i]["T"]==1.0 else q0[i]
        H=[rows[i]["T"]/e[i]-(1.0-rows[i]["T"])/(1.0-e[i]) for i in range(n)]; eps=0.0
        for _ in range(80):
            grad=0.0; info=0.0
            for i in range(n):
                qs=_sigmoid(_logit(qobs[i])+eps*H[i]); grad+=H[i]*(rows[i]["Y"]-qs); info+=H[i]*H[i]*qs*(1.0-qs)
            if info<=1e-12: break
            step=grad/info; eps+=step
            if abs(step)<1e-9: break
        q1s=[];q0s=[];ic_base=[]
        for i in range(n):
            q1i=_sigmoid(_logit(q1[i])+eps/e[i]); q0i=_sigmoid(_logit(q0[i])-eps/(1.0-e[i])); qobsi=q1i if rows[i]["T"]==1.0 else q0[i]
            q1s.append(q1i);q0s.append(q0i);ic_base.append(H[i]*(rows[i]["Y"]-qobsi)+q1i-q0i)
        psi=_mean([q1s[i]-q0s[i] for i in range(n)]); ic=[v-psi for v in ic_base]; se=math.sqrt(max(0.0,_variance(ic))/n)
        return {"status":"TMLE_STACKED_ENSEMBLE_ESTIMATED_UNDER_ASSUMPTIONS","method":"TMLE_STACKED_ENSEMBLE_CROSSFIT","estimate":round(psi,8),"standard_error":round(se,8),"ci95":[round(psi-1.96*se,8),round(psi+1.96*se,8)],"targeting_epsilon":round(eps,8),"propensity_min":round(min(e),8),"propensity_max":round(max(e),8),"n":n,"adjustment":z,"libraries":libraries,"assumptions":assumptions,
                "law":"the stacked nuisance library uses deterministic validation-weighted linear/quadratic logistic candidates; this is not a full Super Learner theorem and does not establish causal identification"}

    # ---------- formal RR bias-factor surface ----------
    def sensitivity_rr_surface(self, observed_rr: float, exposure_confounder_rrs: Sequence[float], outcome_confounder_rrs: Sequence[float]) -> dict[str,Any]:
        rr=float(observed_rr)
        if rr<=0: raise ValueError("observed_rr must be positive")
        a=[float(x) for x in exposure_confounder_rrs]; b=[float(x) for x in outcome_confounder_rrs]
        if not a or not b or len(a)*len(b)>2500 or any(x<1 for x in a+b): raise ValueError("confounder RR grids must be >=1 with at most 2500 pairs")
        mag=rr if rr>=1 else 1.0/rr; rows=[]
        for eu in a:
            for uy in b:
                bf=(eu*uy)/(eu+uy-1.0); adj_mag=max(1.0,mag/max(1e-12,bf)); adjusted=adj_mag if rr>=1 else 1.0/adj_mag
                rows.append({"rr_exposure_confounder":eu,"rr_confounder_outcome":uy,"bias_factor":round(bf,8),"adjusted_rr_toward_null":round(adjusted,8),"explains_to_null":bf>=mag-1e-12})
        rows.sort(key=lambda r:(not r["explains_to_null"],r["rr_exposure_confounder"]*r["rr_confounder_outcome"],r["bias_factor"]))
        first=next((r for r in rows if r["explains_to_null"]),None)
        return {"status":"RR_BIAS_FACTOR_SENSITIVITY_SURFACE","observed_rr":rr,"pair_count":len(rows),"minimum_grid_explain_away":first,"surface":rows,
                "law":"bias-factor surface is a risk-ratio sensitivity calculation under its bounding-factor assumptions; it is not a universal hidden-confounding theorem or causal identification proof"}

    # ---------- exact static-model Bayes-adaptive POMDP ----------
    def bapomdp_solve(self, states: Sequence[str], initial_state_belief: Mapping[str,Any], models: Sequence[Mapping[str,Any]],
                      horizon: int = 3, discount: float = .95, max_nodes: int = 150000) -> dict[str,Any]:
        ss=[str(s) for s in states]
        if not ss or len(ss)>6 or len(set(ss))!=len(ss): raise ValueError("states must contain 1..6 unique values")
        if not models or len(models)>4: raise ValueError("models must contain 1..4 candidates")
        vals={s:max(0.0,float(initial_state_belief.get(s,0.0))) for s in ss}; z=sum(vals.values())
        if z<=1e-15: raise ValueError("initial state belief must have positive mass")
        sb={s:vals[s]/z for s in ss}; mids=[]; pri=[]; parsed={}; common_actions=None
        for mi,m in enumerate(models):
            mid=str(m.get("id",f"M{mi}")); prior=max(0.0,float(m.get("prior",0.0))); acts=m.get("actions") or []
            if not acts or len(acts)>6: raise ValueError("each model requires 1..6 actions")
            amap={}; ids=[]
            for ai,a in enumerate(acts):
                aid=str(a.get("id",f"A{ai}")); ids.append(aid); rew=a.get("reward_by_state") or {}; trans=a.get("transition") or {}; obs=a.get("observation") or {}
                if any(s not in rew or s not in trans or s not in obs for s in ss): raise ValueError(f"model {mid} action {aid} incomplete")
                T={};O={};onames=set()
                for s in ss:
                    tr={sp:max(0.0,float(trans[s].get(sp,0.0))) for sp in ss}
                    if abs(sum(tr.values())-1.0)>1e-6: raise ValueError("transition row must sum to 1")
                    T[s]=tr
                for sp in ss:
                    orow={str(o):max(0.0,float(p)) for o,p in obs[sp].items()}
                    if not orow or abs(sum(orow.values())-1.0)>1e-6: raise ValueError("observation row must sum to 1")
                    O[sp]=orow;onames.update(orow)
                if len(onames)>8: raise ValueError("at most eight observations per action")
                for sp in ss:
                    for o in onames: O[sp].setdefault(o,0.0)
                amap[aid]={"reward":{s:float(rew[s]) for s in ss},"T":T,"O":O,"observations":sorted(onames),"cost":max(0.0,float(a.get("cost",0.0))),"risk":max(0.0,float(a.get("risk",0.0)))}
            aset=set(ids)
            if common_actions is None: common_actions=aset
            elif aset!=common_actions: raise ValueError("all models must expose the same action ids")
            mids.append(mid);pri.append(prior);parsed[mid]=amap
        ps=sum(pri)
        if ps<=1e-15: raise ValueError("model prior mass must be positive")
        mp={mids[i]:pri[i]/ps for i in range(len(mids))}; H=max(1,min(int(horizon),3)); gamma=max(0.0,min(1.0,float(discount))); limit=max(100,min(int(max_nodes),300000)); actions=sorted(common_actions or [])
        b0={(m,s):mp[m]*sb[s] for m in mids for s in ss}; nodes=0
        def solve(b,depth):
            nonlocal nodes
            nodes+=1
            if nodes>limit: raise _NodeLimit()
            ranked=[]
            for aid in actions:
                immediate=0.0; bpred={(m,sp):0.0 for m in mids for sp in ss}; obs_names=set()
                for m in mids:
                    a=parsed[m][aid]; obs_names.update(a["observations"])
                    for s in ss:
                        q=b[(m,s)]; immediate+=q*(a["reward"][s]-a["cost"]-a["risk"])
                        for sp in ss: bpred[(m,sp)]+=q*a["T"][s][sp]
                future=0.0; branches=[]
                if depth>1:
                    for o in sorted(obs_names):
                        po=sum(bpred[(m,sp)]*parsed[m][aid]["O"][sp].get(o,0.0) for m in mids for sp in ss)
                        if po<=1e-15: continue
                        post={(m,sp):bpred[(m,sp)]*parsed[m][aid]["O"][sp].get(o,0.0)/po for m in mids for sp in ss}
                        child=solve(post,depth-1); future+=po*child["value"]
                        mpost={m:sum(post[(m,s)] for s in ss) for m in mids}
                        branches.append({"observation":o,"probability":round(po,10),"model_posterior":{m:round(mpost[m],10) for m in mids},"next_action":child["action"],"value":round(child["value"],10)})
                val=immediate+(gamma*future if depth>1 else 0.0); ranked.append({"action":aid,"value":val,"immediate":immediate,"branches":branches})
            best=max(ranked,key=lambda r:(r["value"],r["action"])); return {"action":best["action"],"value":best["value"],"ranked":ranked}
        try:
            root=solve(b0,H)
        except _NodeLimit:
            return {"status":"NODE_LIMIT_NO_EXACT_CERTIFICATE","decision":"PLAN_ONLY","selected":None,"certificate":None,"nodes_expanded":nodes,"node_limit":limit,"horizon":H,
                    "law":"node-limited finite-model belief search has no exact certificate and no branch is execution history"}
        return {"status":"FINITE_MODEL_BAYES_ADAPTIVE_POMDP_EXACT_HORIZON_CERTIFIED","decision":"PLAN_ONLY","selected":root["action"],"value":round(root["value"],10),"policy":root,"initial_model_belief":{m:round(mp[m],10) for m in mids},"horizon":H,"discount":gamma,"nodes_expanded":nodes,"certificate":"EXACT_FOR_SUPPLIED_STATIC_MODEL_SET_STATE_SPACE_ACTIONS_OBSERVATIONS_AND_HORIZON",
                "law":"exactness is only for the supplied finite static-model POMDP and completed horizon; it is not general Bayes-adaptive control, world-model correctness, or execution authorization"}

    # ---------- uncertainty around learned dependence probabilities ----------
    def evidence_dependence_interval(self, scope: str, features: Mapping[str,Any], confidence_z: float = 1.96, l2: float = 1e-4) -> dict[str,Any]:
        model=self.s.one("SELECT * FROM collective_v10_dependence_models WHERE scope=?",(str(scope),))
        if not model: raise ValueError("fitted evidence-dependence model not found")
        order=json.loads(model["feature_order_json"]); beta=[float(x) for x in json.loads(model["coefficients_json"])]
        if any(k not in features for k in order): raise ValueError("feature required for every fitted dependence dimension")
        rows=self.s.rows("SELECT features_json,label,weight FROM collective_v10_dependence_labels WHERE scope=? ORDER BY label_id",(str(scope),))
        p=len(order)+1; H=[[0.0]*p for _ in range(p)]
        for r in rows:
            x=json.loads(r["features_json"])
            if any(k not in x for k in order): continue
            phi=[1.0]+[float(x[k]) for k in order]; pr=_sigmoid(_dot(beta,phi)); w=max(0.0,float(r["weight"]))*pr*(1.0-pr)
            for i in range(p):
                for j in range(p): H[i][j]+=w*phi[i]*phi[j]
        for i in range(1,p): H[i][i]+=max(1e-9,float(l2))
        H[0][0]+=1e-9
        cov=_inverse(H); phi=[1.0]+[float(features[k]) for k in order]; eta=_dot(beta,phi); se=math.sqrt(max(0.0,_dot(phi,_mat_vec(cov,phi)))); zz=max(.1,min(5.0,float(confidence_z)))
        prob=_sigmoid(eta); lo=_sigmoid(eta-zz*se); hi=_sigmoid(eta+zz*se)
        return {"status":"LOGISTIC_DEPENDENCE_LAPLACE_INTERVAL","scope":str(scope),"probability":round(prob,10),"logit_standard_error":round(se,10),"interval":[round(lo,10),round(hi,10)],"confidence_z":zz,"n_labels":len(rows),"features":{k:float(features[k]) for k in order},
                "law":"Laplace/Hessian interval is conditional on the fitted logistic metadata model and labelled sample; it is not a calibrated finite-sample coverage guarantee or proof of evidence independence"}
