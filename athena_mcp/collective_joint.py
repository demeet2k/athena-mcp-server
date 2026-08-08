from __future__ import annotations

import itertools
import json
import math
import random
import statistics
from typing import Any, Mapping, Sequence

from .collective_adaptive import CollectiveAdaptiveRuntime, _logdet_spd
from .collective_probabilistic import (
    _dot,
    _fit_logistic,
    _fisher_p,
    _mat_vec,
    _mean,
    _partial_corr,
    _predict_logistic,
    _rbf,
    _variance,
)
from .collective_discovery import _inverse


def _normal_logpdf(x: float, mean: float, var: float) -> float:
    v = max(1e-12, float(var))
    d = float(x) - float(mean)
    return -0.5 * (math.log(2.0 * math.pi * v) + d * d / v)


def _softmax_logweights(values: Sequence[float]) -> list[float]:
    if not values:
        return []
    m = max(values)
    ws = [math.exp(max(-745.0, float(v) - m)) for v in values]
    z = sum(ws)
    if z <= 0.0:
        return [1.0 / len(ws)] * len(ws)
    return [w / z for w in ws]


def _binary_value(x: Any, name: str) -> float:
    v = float(x)
    if v not in (0.0, 1.0):
        raise ValueError(f"{name} must be binary 0/1")
    return v


class CollectiveJointRuntime:
    """V12 joint structural world-model layer.

    The layer preserves model uncertainty instead of collapsing a V11 finite GP
    hyperparameter grid to one winner, exposes Bayesian model-averaged nonlinear
    prediction and decision-valued measurements, adds a deterministic subset-of-data
    GP approximation, a bounded PAG-like candidate surface from observed conditional
    independences, a two-timepoint parametric g-formula, and an exact small finite
    chance-constrained resource selector under an explicit independent-Gaussian model.
    """

    def __init__(self, adaptive: CollectiveAdaptiveRuntime):
        self.adaptive = adaptive
        self.probabilistic = adaptive.probabilistic
        self.inference = adaptive.inference
        self.belief = adaptive.belief
        self.s = adaptive.s

    def describe(self) -> dict[str, Any]:
        return {
            "version": "COLLECTIVE_RUNTIME_V12",
            "persistent_surfaces": {},
            "operators": [
                "gp_hyperposterior",
                "gp_bma_predict",
                "gp_sparse_predict",
                "gp_bma_decision_evsi",
                "pag_candidate_discover",
                "longitudinal_gformula",
                "chance_resource_select",
            ],
            "laws": [
                "FINITE_GRID_HYPERPOSTERIOR != CONTINUOUS_HYPERPARAMETER_BAYES",
                "BMA_GP_POSTERIOR != WORLD_TRUTH",
                "SUBSET_GP_APPROXIMATION != FULL_GP_POSTERIOR",
                "BOUNDED_PAG_CANDIDATE != FCI_RFCI_PAG_THEOREM",
                "TWO_TIMEPOINT_GFORMULA != LONGITUDINAL_TMLE_OR_IDENTIFICATION_PROOF",
                "BMA_GP_EVSI != OBSERVATION",
                "GAUSSIAN_INDEPENDENT_CHANCE_CERTIFICATE != DISTRIBUTION_FREE_RESOURCE_GUARANTEE",
            ],
        }

    # ---------- finite-grid posterior over GP hyperparameters ----------
    def _candidate_grid(self, context_key: str, candidates: Sequence[Mapping[str, Any]] | None = None) -> tuple[Any, list[dict[str, float]]]:
        row = self.probabilistic._gp_row(context_key)
        cur_ls = float(row["length_scale"]); cur_sv = float(row["signal_variance"]); cur_nv = float(row["noise_variance"])
        if candidates is None:
            ls = [max(1e-6, cur_ls * q) for q in (.5, 1.0, 2.0)]
            sv = [max(1e-9, cur_sv * q) for q in (.5, 1.0, 2.0)]
            nv = [max(1e-9, cur_nv * q) for q in (.5, 1.0, 2.0)]
            out = [{"length_scale":a,"signal_variance":b,"noise_variance":c,"prior":1.0} for a,b,c in itertools.product(ls,sv,nv)]
        else:
            out=[]
            for c in candidates:
                ls=float(c.get("length_scale",0)); sv=float(c.get("signal_variance",0)); nv=float(c.get("noise_variance",0)); pr=float(c.get("prior",1.0))
                if ls<=0 or sv<=0 or nv<=0 or pr<=0:
                    raise ValueError("GP hyperposterior candidates require positive length_scale/signal_variance/noise_variance/prior")
                out.append({"length_scale":ls,"signal_variance":sv,"noise_variance":nv,"prior":pr})
        if not out or len(out)>256:
            raise ValueError("GP hyperposterior supports 1..256 candidate models")
        return row,out

    def _lml(self, obs: Sequence[Mapping[str, Any]], ls: float, sv: float, nv: float) -> float:
        n=len(obs)
        K=[[_rbf(obs[i]["x"],obs[j]["x"],ls,sv) for j in range(n)] for i in range(n)]
        for i in range(n): K[i][i]+=nv+1e-9
        y=[float(o["y"]) for o in obs]
        Ki=_inverse(K)
        return -0.5*_dot(y,_mat_vec(Ki,y))-0.5*_logdet_spd(K)-0.5*n*math.log(2.0*math.pi)

    def gp_hyperposterior(self, context_key: str, candidates: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
        row,grid=self._candidate_grid(context_key,candidates)
        obs=json.loads(row["observations_json"])
        if len(obs)<3:
            raise ValueError("GP hyperposterior requires at least three observed rows")
        scored=[]
        for c in grid:
            try:
                lml=self._lml(obs,c["length_scale"],c["signal_variance"],c["noise_variance"])
            except Exception:
                continue
            scored.append({**c,"log_marginal_likelihood":lml,"log_weight":lml+math.log(c["prior"])})
        if not scored:
            raise ValueError("no numerically valid GP hyperposterior candidate")
        weights=_softmax_logweights([r["log_weight"] for r in scored])
        for r,w in zip(scored,weights): r["posterior_weight"]=w
        scored.sort(key=lambda r:(r["posterior_weight"],r["log_marginal_likelihood"]),reverse=True)
        ent=-sum(r["posterior_weight"]*math.log(max(1e-300,r["posterior_weight"]),2) for r in scored)
        eff=1.0/sum(r["posterior_weight"]**2 for r in scored)
        return {
            "status":"FINITE_GRID_GP_HYPERPOSTERIOR",
            "context_key":str(context_key),
            "observation_count":len(obs),
            "candidate_count":len(scored),
            "entropy_bits":round(ent,10),
            "effective_model_count":round(eff,10),
            "posterior":[{k:(round(v,12) if isinstance(v,float) else v) for k,v in r.items() if k!="log_weight"} for r in scored],
            "law":"posterior weights are exact only for the supplied finite candidate grid/prior and GP likelihood; they are not a continuous hyperparameter posterior or proof of the true kernel",
        }

    def _gp_predict_model(self, obs: Sequence[Mapping[str, Any]], xq: Sequence[float], ls: float, sv: float, nv: float) -> tuple[float,float]:
        if not obs:
            return 0.0,sv
        n=len(obs)
        K=[[_rbf(obs[i]["x"],obs[j]["x"],ls,sv) for j in range(n)] for i in range(n)]
        for i in range(n): K[i][i]+=nv+1e-9
        Ki=_inverse(K); y=[float(o["y"]) for o in obs]
        k=[_rbf(o["x"],xq,ls,sv) for o in obs]
        mu=_dot(k,_mat_vec(Ki,y)); var=max(0.0,sv-_dot(k,_mat_vec(Ki,k)))
        return mu,var

    def gp_bma_predict(self, context_key: str, features: Mapping[str, Any], candidates: Sequence[Mapping[str, Any]] | None = None, include_observation_noise: bool = True) -> dict[str, Any]:
        hp=self.gp_hyperposterior(context_key,candidates)
        row=self.probabilistic._gp_row(context_key); order=json.loads(row["feature_order_json"]); obs=json.loads(row["observations_json"])
        if any(k not in features for k in order): raise ValueError("feature value required for every GP feature")
        xq=[float(features[k]) for k in order]
        terms=[]
        for c in hp["posterior"]:
            mu,var=self._gp_predict_model(obs,xq,float(c["length_scale"]),float(c["signal_variance"]),float(c["noise_variance"]))
            if include_observation_noise: var+=float(c["noise_variance"])
            terms.append((float(c["posterior_weight"]),mu,var))
        mean=sum(w*m for w,m,_ in terms)
        within=sum(w*v for w,_,v in terms)
        between=sum(w*(m-mean)**2 for w,m,_ in terms)
        total=within+between
        return {
            "status":"FINITE_GRID_GP_BAYESIAN_MODEL_AVERAGE",
            "context_key":str(context_key),
            "mean":round(mean,10),
            "within_model_variance":round(within,10),
            "between_model_variance":round(between,10),
            "predictive_variance":round(total,10),
            "std":round(math.sqrt(max(0.0,total)),10),
            "effective_model_count":hp["effective_model_count"],
            "candidate_count":hp["candidate_count"],
            "law":"law of total variance preserves finite-grid kernel uncertainty; BMA remains conditional on the supplied GP family, prior and observations",
        }

    # ---------- deterministic subset-of-data GP approximation ----------
    def gp_sparse_predict(self, context_key: str, features: Mapping[str, Any], inducing_count: int = 16, include_observation_noise: bool = True) -> dict[str, Any]:
        row=self.probabilistic._gp_row(context_key); order=json.loads(row["feature_order_json"]); obs=json.loads(row["observations_json"])
        if any(k not in features for k in order): raise ValueError("feature value required for every GP feature")
        if not obs: return {**self.probabilistic.gp_predict(context_key,features,include_observation_noise),"status":"SUBSET_GP_PRIOR","selected_indices":[]}
        m=max(1,min(int(inducing_count),min(64,len(obs))))
        xs=[o["x"] for o in obs]
        if len(obs)<=m:
            sel=list(range(len(obs)))
        else:
            d=len(xs[0]); centroid=[sum(float(x[j]) for x in xs)/len(xs) for j in range(d)]
            def d2(a,b): return sum((float(a[j])-float(b[j]))**2 for j in range(d))
            first=max(range(len(xs)),key=lambda i:(d2(xs[i],centroid),-i)); sel=[first]
            remaining=set(range(len(xs)))-{first}
            while len(sel)<m:
                nxt=max(remaining,key=lambda i:(min(d2(xs[i],xs[j]) for j in sel),-i)); sel.append(nxt); remaining.remove(nxt)
        subset=[obs[i] for i in sel]; xq=[float(features[k]) for k in order]
        ls=float(row["length_scale"]); sv=float(row["signal_variance"]); nv=float(row["noise_variance"])
        mu,var=self._gp_predict_model(subset,xq,ls,sv,nv)
        if include_observation_noise: var+=nv
        exact=self.probabilistic.gp_predict(context_key,features,include_observation_noise)
        return {
            "status":"SUBSET_OF_DATA_GP_APPROXIMATION",
            "context_key":str(context_key),"observation_count":len(obs),"inducing_count":len(sel),"selected_indices":sel,
            "mean":round(mu,10),"predictive_variance":round(var,10),"std":round(math.sqrt(max(0.0,var)),10),
            "exact_reference":{"mean":exact.get("mean"),"predictive_variance":exact.get("predictive_variance"),"absolute_mean_error":round(abs(mu-float(exact.get("mean",0.0))),10),"absolute_variance_error":round(abs(var-float(exact.get("predictive_variance",0.0))),10)},
            "law":"deterministic farthest-point subset-of-data GP is a bounded approximation and is not the full GP posterior, sparse variational GP, or inducing-point optimality proof",
        }

    def _gp_joint_model(self, row: Mapping[str, Any], points: Sequence[Mapping[str, Any]], ls: float, sv: float, nv: float):
        order=json.loads(row["feature_order_json"]); obs=json.loads(row["observations_json"]); xs=[]
        for p in points:
            if any(k not in p for k in order): raise ValueError("feature value required for every GP feature")
            xs.append([float(p[k]) for k in order])
        m=len(xs); means=[0.0]*m; cov=[[_rbf(xs[i],xs[j],ls,sv) for j in range(m)] for i in range(m)]
        if obs:
            n=len(obs); K=[[_rbf(obs[i]["x"],obs[j]["x"],ls,sv) for j in range(n)] for i in range(n)]
            for i in range(n): K[i][i]+=nv+1e-9
            Ki=_inverse(K); y=[float(o["y"]) for o in obs]; alpha=_mat_vec(Ki,y); ks=[]
            for x in xs:
                k=[_rbf(o["x"],x,ls,sv) for o in obs]; ks.append(k); means[len(ks)-1]=_dot(k,alpha)
            for i in range(m):
                for j in range(m): cov[i][j]-=_dot(ks[i],_mat_vec(Ki,ks[j]))
        for i in range(m): cov[i][i]=max(0.0,cov[i][i])
        return means,cov

    def gp_bma_decision_evsi(self, context_key: str, actions: Sequence[Mapping[str, Any]], experiments: Sequence[Mapping[str, Any]], candidates: Sequence[Mapping[str, Any]] | None = None, samples: int = 300, seed: int = 0, cost_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str, Any]:
        if not actions or not experiments: raise ValueError("actions and experiments must not be empty")
        if len(actions)>32 or len(experiments)>64: raise ValueError("too many BMA GP actions/experiments")
        hp=self.gp_hyperposterior(context_key,candidates); row=self.probabilistic._gp_row(context_key)
        points=[a.get("features") or {} for a in actions]+[e.get("features") or {} for e in experiments]; na=len(actions)
        models=[]
        for c in hp["posterior"]:
            means,cov=self._gp_joint_model(row,points,float(c["length_scale"]),float(c["signal_variance"]),float(c["noise_variance"]))
            models.append({"weight":float(c["posterior_weight"]),"means":means,"cov":cov,"noise":float(c["noise_variance"])})
        current=[]
        for i,a in enumerate(actions):
            m=sum(md["weight"]*md["means"][i] for md in models); val=float(a.get("utility_offset",0))+float(a.get("utility_scale",1))*m
            current.append((val,str(a.get("id",f"A{i}"))))
        current_best=max(current); n=max(50,min(int(samples),2000)); ranked=[]
        for j,e in enumerate(experiments):
            eid=str(e.get("id",f"E{j}")); idx=na+j; ethical=bool(e.get("ethical",True)); feas=max(0,min(1,float(e.get("feasibility",1))))
            cost=max(0,float(e.get("cost",0))); risk=max(0,min(1,float(e.get("risk",0)))); rng=random.Random(int(seed)+8191*(j+1)); post=[]
            cum=[]; acc=0.0
            for md in models: acc+=md["weight"]; cum.append(acc)
            for _ in range(n):
                u=rng.random(); mi=next((q for q,cw in enumerate(cum) if u<=cw),len(models)-1); truth=models[mi]
                enoise=max(1e-12,float(e.get("noise_variance",truth["noise"]))); var_truth=max(1e-12,truth["cov"][idx][idx]+enoise)
                y=rng.gauss(truth["means"][idx],math.sqrt(var_truth)); lws=[]
                for md in models:
                    v=max(1e-12,md["cov"][idx][idx]+max(1e-12,float(e.get("noise_variance",md["noise"]))))
                    lws.append(math.log(max(1e-300,md["weight"]))+_normal_logpdf(y,md["means"][idx],v))
                pw=_softmax_logweights(lws); best=-float("inf")
                for i,a in enumerate(actions):
                    am=0.0
                    for q,md in enumerate(models):
                        v=max(1e-12,md["cov"][idx][idx]+max(1e-12,float(e.get("noise_variance",md["noise"]))))
                        upd=md["means"][i]+md["cov"][i][idx]/v*(y-md["means"][idx]); am+=pw[q]*upd
                    val=float(a.get("utility_offset",0))+float(a.get("utility_scale",1))*am; best=max(best,val)
                post.append(best)
            evsi=max(0.0,_mean(post)-current_best[0]); mcse=math.sqrt(max(0.0,_variance(post))/n); score=0.0 if not ethical else evsi*feas-max(0,float(cost_weight))*cost-max(0,float(risk_weight))*risk
            ranked.append({"id":eid,"status":"ELIGIBLE" if ethical else "ETHICS_BLOCK","evsi":round(evsi,10),"score":round(score,10),"monte_carlo_se":round(mcse,10),"samples":n,"cost":cost,"risk":risk,"feasibility":feas})
        ranked.sort(key=lambda r:(r["score"],r["evsi"],-r["cost"],r["id"]),reverse=True); eligible=[r for r in ranked if r["status"]=="ELIGIBLE"]
        return {"decision":"FINITE_GRID_BMA_GP_EVSI_DESIGN_ONLY","context_key":str(context_key),"effective_model_count":hp["effective_model_count"],"current_best_action":current_best[1],"current_best_expected_utility":round(current_best[0],10),"winner":eligible[0]["id"] if eligible else None,"ranked":ranked,
                "law":"measurement simulations update finite-grid GP model weights and within-model posterior means only hypothetically; BMA EVSI never creates GP observations or canonical facts"}

    # ---------- bounded observed-data PAG candidate ----------
    def pag_candidate_discover(self, samples: Sequence[Mapping[str, Any]], variables: Sequence[str] | None = None, alpha: float = .05, max_conditioning: int = 2) -> dict[str, Any]:
        if len(samples)<20: raise ValueError("PAG candidate requires at least twenty samples")
        vars_=[str(v) for v in (variables or sorted(samples[0].keys()))]
        if len(vars_)<3 or len(vars_)>8: raise ValueError("PAG candidate supports 3..8 variables")
        data={v:[] for v in vars_}
        for row in samples:
            for v in vars_:
                if v not in row or not isinstance(row[v],(int,float)): raise ValueError(f"numeric sample missing {v}")
                data[v].append(float(row[v]))
        a=max(1e-6,min(.5,float(alpha))); mc=max(0,min(3,int(max_conditioning))); edges={tuple(sorted((vars_[i],vars_[j]))) for i in range(len(vars_)) for j in range(i+1,len(vars_))}; sep={}; tests=0
        def neigh(v,E): return {y if x==v else x for x,y in E if x==v or y==v}
        for l in range(mc+1):
            snap=set(edges); adj={v:neigh(v,snap) for v in vars_}; remove=[]
            for x,y in sorted(snap):
                pool=sorted((adj[x]|adj[y])-{x,y})
                if len(pool)<l: continue
                for cond in itertools.combinations(pool,l):
                    tests+=1; r=_partial_corr(data[x],data[y],[data[c] for c in cond]); p=_fisher_p(r,len(samples),len(cond))
                    if p>a:
                        remove.append((x,y)); sep[(x,y)]=list(cond); sep[(y,x)]=list(cond); break
            for e in remove: edges.discard(tuple(sorted(e)))
        marks={e:{e[0]:"circle",e[1]:"circle"} for e in edges}; adj={v:neigh(v,edges) for v in vars_}; colliders=[]
        for z in vars_:
            ns=sorted(adj[z])
            for i in range(len(ns)):
                for j in range(i+1,len(ns)):
                    x,y=ns[i],ns[j]
                    if tuple(sorted((x,y))) in edges: continue
                    if z not in sep.get((x,y),[]):
                        ex=tuple(sorted((x,z))); ey=tuple(sorted((y,z))); marks[ex][z]="arrowhead"; marks[ey][z]="arrowhead"; colliders.append({"left":x,"middle":z,"right":y,"mark":f"{x} o-> {z} <-o {y}"})
        # one conservative orientation propagation rule: A *-> B o-* C and A,C nonadjacent => B -> C candidate
        changed=True; rounds=0
        while changed and rounds<16:
            changed=False; rounds+=1
            for ab in list(edges):
                for a0,b in ((ab[0],ab[1]),(ab[1],ab[0])):
                    if marks[ab].get(b)!="arrowhead": continue
                    for c in sorted(adj[b]-{a0}):
                        bc=tuple(sorted((b,c)))
                        if marks[bc].get(b)!="circle" or tuple(sorted((a0,c))) in edges: continue
                        marks[bc][b]="tail"; marks[bc][c]="arrowhead"; changed=True
        def symbol(e):
            x,y=e; mx=marks[e][x]; my=marks[e][y]
            left={"circle":"o","tail":"-","arrowhead":"<"}[mx]; right={"circle":"o","tail":"-","arrowhead":">"}[my]
            return f"{left}-{right}"
        out=[]
        for e in sorted(edges): out.append({"a":e[0],"b":e[1],"endpoint_a":marks[e][e[0]],"endpoint_b":marks[e][e[1]],"mark":symbol(e)})
        return {"status":"BOUNDED_PAG_CANDIDATE","n":len(samples),"variables":vars_,"alpha":a,"max_conditioning":mc,"ci_tests":tests,"edges":out,"collider_candidates":colliders,"separation_sets":[{"a":x,"b":y,"conditioning":c} for (x,y),c in sorted(sep.items()) if x<y],
                "law":"circle/arrow/tail marks come from bounded observed Gaussian CI search, unshielded-collider logic and limited propagation only; this is not full FCI/RFCI, possible-d-sep completeness, latent-confounder proof, or canonical JSPACE truth"}

    # ---------- two-timepoint longitudinal parametric g-formula ----------
    def longitudinal_gformula(self, samples: Sequence[Mapping[str, Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, baseline: Sequence[str] | None = None, regimes: Sequence[Mapping[str, Any]] | None = None, assumptions: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if len(samples)<80: raise ValueError("two-timepoint g-formula requires at least eighty samples")
        assumptions=dict(assumptions or {})
        if assumptions.get("latent_confounding_possible"): return {"status":"UNIDENTIFIED_LATENT_CONFOUNDING_RISK","regimes":[],"method":"TWO_TIMEPOINT_PARAMETRIC_GFORMULA"}
        base=[str(x) for x in (baseline or [])]; rows=[]
        for r in samples:
            for k in [treatment1,intermediate,treatment2,outcome]+base:
                if k not in r: raise ValueError(f"longitudinal sample missing {k}")
            q={k:float(r[k]) for k in base}; q["A1"]=_binary_value(r[treatment1],treatment1); q["L1"]=_binary_value(r[intermediate],intermediate); q["A2"]=_binary_value(r[treatment2],treatment2); q["Y"]=_binary_value(r[outcome],outcome); rows.append(q)
        lfit=_fit_logistic(rows,"L1",base+["A1"]); yfit=_fit_logistic(rows,"Y",base+["A1","L1","A2"])
        regs=list(regimes or [{"id":f"A1={a1},A2={a2}","a1":a1,"a2":a2} for a1 in (0,1) for a2 in (0,1)])
        if not regs or len(regs)>16: raise ValueError("regimes must contain 1..16 static treatment plans")
        results=[]
        for ri,reg in enumerate(regs):
            a1=_binary_value(reg.get("a1"),"regime a1"); a2=_binary_value(reg.get("a2"),"regime a2"); vals=[]
            for r in rows:
                xb={k:r[k] for k in base}; lr={**xb,"A1":a1}; pL=_predict_logistic(lfit,lr,base+["A1"])
                y0={**xb,"A1":a1,"L1":0.0,"A2":a2}; y1={**xb,"A1":a1,"L1":1.0,"A2":a2}
                q0=_predict_logistic(yfit,y0,base+["A1","L1","A2"]); q1=_predict_logistic(yfit,y1,base+["A1","L1","A2"]); vals.append((1-pL)*q0+pL*q1)
            results.append({"id":str(reg.get("id",f"R{ri}")),"a1":int(a1),"a2":int(a2),"estimated_risk":round(_mean(vals),10)})
        results.sort(key=lambda r:(r["estimated_risk"],r["id"]),reverse=True); best=results[0]; worst=results[-1]
        return {"status":"TWO_TIMEPOINT_PARAMETRIC_GFORMULA_ESTIMATED_UNDER_ASSUMPTIONS","method":"TWO_TIMEPOINT_PARAMETRIC_GFORMULA","n":len(rows),"baseline":base,"treatment1":str(treatment1),"intermediate":str(intermediate),"treatment2":str(treatment2),"outcome":str(outcome),"regimes":results,"highest_risk_regime":best["id"],"lowest_risk_regime":worst["id"],"risk_contrast":round(best["estimated_risk"]-worst["estimated_risk"],10),"assumptions":assumptions,
                "law":"two-timepoint parametric g-formula requires sequential exchangeability, positivity, consistency and correct nuisance models; it is not longitudinal TMLE, randomized evidence, or identification proof"}

    # ---------- exact small chance-constrained resource selection ----------
    def chance_resource_select(self, candidates: Sequence[Mapping[str, Any]], budgets: Mapping[str, Any], alpha: float = .05, exact_limit: int = 18) -> dict[str, Any]:
        items=list(candidates); resources=sorted(str(k) for k in budgets)
        if not items or len(items)>24: raise ValueError("chance resource selector supports 1..24 candidates")
        if not resources or len(resources)>6: raise ValueError("budgets must contain 1..6 resource dimensions")
        aa=max(1e-6,min(.49,float(alpha))); z=statistics.NormalDist().inv_cdf(1.0-aa); parsed=[]
        for i,c in enumerate(items):
            rid=str(c.get("id",f"C{i}")); val=float(c.get("value",0.0)); rr=c.get("resources") or {}; pdata={}
            for r in resources:
                if r not in rr: raise ValueError(f"candidate {rid} missing resource {r}")
                x=rr[r]; mean=float(x.get("mean",0)); std=float(x.get("std",0))
                if mean<0 or std<0: raise ValueError("resource mean/std must be nonnegative")
                pdata[r]=(mean,std)
            parsed.append({"id":rid,"value":val,"resources":pdata})
        def eval_subset(indexes):
            total=sum(parsed[i]["value"] for i in indexes); rs={}; feasible=True
            for r in resources:
                mu=sum(parsed[i]["resources"][r][0] for i in indexes); sd=math.sqrt(sum(parsed[i]["resources"][r][1]**2 for i in indexes)); bound=mu+z*sd; limit=float(budgets[r]); p=1.0 if sd<=1e-15 and mu>limit else (0.0 if sd<=1e-15 else 1.0-statistics.NormalDist(mu,sd).cdf(limit)); rs[r]={"mean":round(mu,10),"std":round(sd,10),"one_sided_bound":round(bound,10),"budget":limit,"approx_violation_probability":round(p,10)}; feasible=feasible and bound<=limit+1e-12
            return total,feasible,rs
        n=len(parsed); exact=n<=max(1,min(int(exact_limit),18)); best=None; evaluated=0
        if exact:
            for mask in range(1<<n):
                idx=[i for i in range(n) if mask>>i & 1]; total,ok,rs=eval_subset(idx); evaluated+=1
                if ok and (best is None or (total,-len(idx),tuple(parsed[i]["id"] for i in idx))>(best[0],-len(best[1]),tuple(parsed[i]["id"] for i in best[1]))): best=(total,idx,rs)
            status="CHANCE_CONSTRAINED_EXACT_ENUMERATION_CERTIFIED"; cert="EXACT_ENUMERATION_UNDER_DECLARED_INDEPENDENT_GAUSSIAN_RESOURCE_MODEL"
        else:
            order=sorted(range(n),key=lambda i:(parsed[i]["value"]/(1e-9+sum(parsed[i]["resources"][r][0] for r in resources)),parsed[i]["value"],parsed[i]["id"]),reverse=True); idx=[]
            for i in order:
                _,ok,_=eval_subset(idx+[i])
                if ok: idx.append(i)
            total,_,rs=eval_subset(idx); best=(total,idx,rs); evaluated=len(order); status="CHANCE_CONSTRAINED_GREEDY_NO_OPTIMALITY_CERTIFICATE"; cert=None
        if best is None: best=(0.0,[],{r:{"mean":0.0,"std":0.0,"one_sided_bound":0.0,"budget":float(budgets[r]),"approx_violation_probability":0.0} for r in resources})
        return {"status":status,"certificate":cert,"selected":[parsed[i]["id"] for i in best[1]],"total_value":round(best[0],10),"alpha_per_resource":aa,"z_value":round(z,10),"resource_summary":best[2],"evaluated_subsets_or_steps":evaluated,"candidate_count":n,"assumption":"candidate resource consumptions are independent Gaussian within each resource dimension; cross-resource and cross-candidate dependence is omitted",
                "law":"exact enumeration certifies only the declared finite subset problem under the independent-Gaussian chance approximation; it is not distribution-free real-world feasibility or a stochastic-control theorem"}
