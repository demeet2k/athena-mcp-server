from __future__ import annotations

import itertools
import json
import math
import time
from typing import Any, Mapping, Sequence

from .collective_discovery import (
    CollectiveDiscoveryRuntime,
    _clamp,
    _dot,
    _eye,
    _inverse,
    _mat_vec,
    _stable_id,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v7_identifications(
 analysis_id TEXT PRIMARY KEY,
 method TEXT NOT NULL,
 treatment TEXT NOT NULL,
 outcome TEXT NOT NULL,
 status TEXT NOT NULL,
 witness_json TEXT NOT NULL,
 assumptions_json TEXT NOT NULL,
 actor TEXT NOT NULL,
 created_at REAL NOT NULL
);
"""


class CollectiveDualControlRuntime:
    """V7 dual-control and conditional causal-discovery layer.

    V7 adds an explicit uncertainty decomposition proxy, prequential empirical
    residual bands, heuristic observational skeleton discovery, state-dependent
    stochastic transition regression, scenario-tree evaluation, a bounded
    dual-control proxy, extended supplied-DAG identification, and replication
    independence/design geometry.

    It does not claim exact Bayesian dual control, distribution-free conformal
    validity under arbitrary shift, causal graph truth from observational
    association, or unconditional causal identification.
    """

    def __init__(self, discovery: CollectiveDiscoveryRuntime):
        self.discovery = discovery
        self.science = discovery.science
        self.s = discovery.s
        self.collective = discovery.collective
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        q = self.s.one("SELECT COUNT(*) AS n FROM collective_v7_identifications")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V7",
            "persistent_surfaces": {"extended_identifications": q},
            "operators": [
                "uncertainty_decompose", "prequential_interval", "causal_skeleton_discover",
                "state_transition_model", "scenario_evaluate", "dual_control_plan",
                "causal_identify_extended", "replication_independence", "replication_design",
            ],
            "laws": [
                "UNCERTAINTY_DECOMPOSITION is a model-conditional diagnostic proxy, not a unique physical decomposition",
                "PREQUENTIAL_EMPIRICAL_INTERVAL != DISTRIBUTION_FREE_CONFORMAL_GUARANTEE under arbitrary shift",
                "ASSOCIATION_SKELETON != CAUSAL_DAG",
                "STATE_DEPENDENT_TRANSITION_MODEL != WORLD_TRUTH",
                "SCENARIO_TREE != OBSERVED_FUTURE",
                "DUAL_CONTROL_PROXY != EXACT_BELIEF_STATE_OPTIMAL_CONTROL",
                "FRONTDOOR_OR_IV_IDENTIFICATION is conditional on the supplied DAG and assumptions",
                "ESTIMATED_REPLICATION_INDEPENDENCE != FORMAL_STATISTICAL_INDEPENDENCE",
                "REPLICATION_DESIGN != REPLICATION_RESULT",
            ],
        }

    def uncertainty_decompose(self, features: Mapping[str, Any], regime: str, arm_id: str,
                              scope: str = "global", target_coverage: float = .90,
                              ridge: float = 1.0, ood_gain: float = 1.5) -> dict[str, Any]:
        expanded = self.discovery._poly(features)
        model_arm = f"NL:{arm_id}"
        st = self.science._bayes_state(scope, regime, model_arm, expanded, ridge)
        inv = _inverse(st["precision"])
        leverage = max(0.0, _dot(st["phi"], _mat_vec(inv, st["phi"])))
        p = len(st["phi"])
        if st["n"] > p:
            noise_var = max(1e-6, st["residual_ss"] / max(1, st["n"] - p))
        elif st["n"] > 0:
            mean_reward = st["reward_sum"] / max(1, st["n"])
            noise_var = max(.02, mean_reward * (1.0 - mean_reward))
        else:
            noise_var = .25
        aleatoric = math.sqrt(noise_var)
        epistemic = math.sqrt(noise_var * leverage)
        base_sigma = math.sqrt(max(1e-12, noise_var * (1.0 + leverage)))
        ood = self.discovery.ood_score(features, regime, scope)
        shift = base_sigma * max(0.0, float(ood_gain)) * float(ood.get("ood_score", 1.0))
        cal = self.science.uncertainty_calibration(scope, regime, model_arm, target_coverage)
        calibration_error = float(cal.get("mean_abs_error") or 0.0)
        total_proxy = math.sqrt(aleatoric**2 + epistemic**2 + shift**2 + calibration_error**2)
        return {
            "scope": str(scope), "regime": str(regime), "arm_id": str(arm_id), "n": st["n"],
            "components": {
                "aleatoric_noise_proxy": round(aleatoric, 6),
                "epistemic_parameter_proxy": round(epistemic, 6),
                "distribution_shift_proxy": round(shift, 6),
                "calibration_error_proxy": round(calibration_error, 6),
            },
            "posterior_leverage": round(leverage, 6),
            "ood": ood,
            "total_proxy_sigma": round(total_proxy, 6),
            "law": "components are diagnostic model-conditional proxies and are not uniquely identifiable physical uncertainty sources",
        }

    @staticmethod
    def _quantile(values: Sequence[float], q: float) -> float:
        if not values:
            raise ValueError("quantile requires values")
        xs = sorted(float(v) for v in values)
        q = _clamp(q, 0.0, 1.0)
        idx = min(len(xs)-1, max(0, int(math.ceil((len(xs)+1) * q)) - 1))
        return xs[idx]

    def prequential_interval(self, features: Mapping[str, Any], regime: str, arm_id: str,
                             scope: str = "global", coverage: float = .90,
                             min_scores: int = 8, ood_gain: float = 1.5) -> dict[str, Any]:
        model_arm = f"NL:{arm_id}"
        rows = self.s.rows(
            "SELECT abs_error FROM collective_v5_bayes_observations WHERE scope=? AND regime=? AND arm_id=? AND abs_error IS NOT NULL ORDER BY created_at",
            (str(scope), str(regime), model_arm),
        )
        pred = self.discovery.nonlinear_predict(features, regime, arm_id, scope, coverage, 1.0, 0.0)
        scores = [float(r["abs_error"]) for r in rows]
        ood = self.discovery.ood_score(features, regime, scope)
        if len(scores) < max(1, int(min_scores)):
            return {
                "status": "INSUFFICIENT_PREQUENTIAL_SCORES", "n": len(scores), "required": max(1, int(min_scores)),
                "mean": pred["mean"], "lower": pred["lower"], "upper": pred["upper"], "ood": ood,
                "law": "insufficient retained pre-update residuals; Bayesian/OOD interval returned without a conformal-style coverage claim",
            }
        half = self._quantile(scores, _clamp(coverage, .5, .999))
        inflation = 1.0 + max(0.0, float(ood_gain)) * float(ood.get("ood_score", 1.0))
        half *= inflation
        mean = float(pred["mean"])
        return {
            "status": "EMPIRICAL_PREQUENTIAL_BAND", "n": len(scores), "coverage_target": round(_clamp(coverage, .5, .999), 6),
            "mean": round(mean, 6), "half_width": round(half, 6),
            "lower": round(_clamp(mean-half), 6), "upper": round(_clamp(mean+half), 6),
            "ood": ood,
            "law": "band uses retained pre-update residuals plus current OOD inflation; it is conformal-style/prequential evidence, not a distribution-free guarantee under arbitrary nonexchangeable shift",
        }

    @staticmethod
    def _numeric_row(row: Mapping[str, Any]) -> dict[str, float]:
        out = {}
        for k, v in row.items():
            if isinstance(v, (int, float)) and math.isfinite(float(v)):
                out[str(k)] = float(v)
        return out

    @staticmethod
    def _corr(xs: Sequence[float], ys: Sequence[float]) -> float:
        n = min(len(xs), len(ys))
        if n < 3:
            return 0.0
        mx = sum(xs[:n]) / n; my = sum(ys[:n]) / n
        vx = sum((x-mx)**2 for x in xs[:n]); vy = sum((y-my)**2 for y in ys[:n])
        if vx <= 1e-15 or vy <= 1e-15:
            return 0.0
        return max(-1.0, min(1.0, sum((xs[i]-mx)*(ys[i]-my) for i in range(n)) / math.sqrt(vx*vy)))

    @classmethod
    def _partial_corr_one(cls, x: Sequence[float], y: Sequence[float], z: Sequence[float]) -> float:
        rxy = cls._corr(x, y); rxz = cls._corr(x, z); ryz = cls._corr(y, z)
        den = math.sqrt(max(1e-12, (1-rxz*rxz)*(1-ryz*ryz)))
        return max(-1.0, min(1.0, (rxy-rxz*ryz)/den))

    def causal_skeleton_discover(self, samples: Sequence[Mapping[str, Any]], variables: Sequence[str] | None = None,
                                 association_threshold: float = .15, max_conditioning: int = 1) -> dict[str, Any]:
        if len(samples) < 5:
            raise ValueError("need at least five samples")
        numeric = [self._numeric_row(r) for r in samples]
        if variables is None:
            common = set(numeric[0])
            for r in numeric[1:]: common &= set(r)
            vars_ = sorted(common)
        else:
            vars_ = [str(v) for v in variables]
        vars_ = vars_[:16]
        if len(vars_) < 2:
            raise ValueError("need at least two numeric variables present in all samples")
        for r in numeric:
            if any(v not in r for v in vars_):
                raise ValueError("selected variables must be numeric in every sample")
        data = {v: [r[v] for r in numeric] for v in vars_}
        tau = max(0.0, min(1.0, float(association_threshold)))
        edges = set()
        sep: dict[tuple[str, str], list[str]] = {}
        marginal = {}
        for i, x in enumerate(vars_):
            for y in vars_[i+1:]:
                r = self._corr(data[x], data[y]); marginal[f"{x}|{y}"] = round(r, 6)
                if abs(r) >= tau:
                    edges.add((x, y))
                else:
                    sep[(x, y)] = []
        if max_conditioning >= 1:
            for x, y in list(edges):
                for z in vars_:
                    if z in {x, y}: continue
                    rp = self._partial_corr_one(data[x], data[y], data[z])
                    if abs(rp) < tau:
                        edges.discard((x, y)); sep[(x, y)] = [z]; break
        adjacency = {v:set() for v in vars_}
        for x, y in edges:
            adjacency[x].add(y); adjacency[y].add(x)
        vstructures=[]
        for z in vars_:
            ns=sorted(adjacency[z])
            for i,x in enumerate(ns):
                for y in ns[i+1:]:
                    pair=tuple(sorted((x,y)))
                    if pair in edges: continue
                    if z not in set(sep.get(pair, [])):
                        vstructures.append({"left":x,"collider":z,"right":y})
        return {
            "status":"HEURISTIC_ASSOCIATION_SKELETON",
            "variables":vars_, "n":len(samples), "threshold":tau,
            "undirected_edges":[{"a":a,"b":b} for a,b in sorted(edges)],
            "separation_sets":{f"{a}|{b}":v for (a,b),v in sorted(sep.items())},
            "v_structure_candidates":vstructures,
            "marginal_correlations":marginal,
            "law":"thresholded marginal/one-variable partial-correlation skeleton is hypothesis generation only; it is not a causal DAG, significance test, or proof of faithfulness/causal sufficiency",
        }

    def _transition_rows(self, action_id: str) -> list[tuple[dict[str,float], dict[str,float], float]]:
        rows = self.s.rows(
            "SELECT before_json,after_json,evidence_weight FROM collective_v5_transition_observations WHERE action_id=? ORDER BY created_at",
            (str(action_id),),
        )
        out=[]
        for r in rows:
            b=self._numeric_row(json.loads(r["before_json"])); a=self._numeric_row(json.loads(r["after_json"]))
            w=max(0.0,float(r["evidence_weight"]))
            if w>0: out.append((b,a,w))
        return out

    def state_transition_model(self, action_id: str, context: Mapping[str, Any], ridge: float = 1.0,
                               max_features: int = 8) -> dict[str, Any]:
        rows=self._transition_rows(action_id)
        if not rows:
            return {"status":"UNSEEN_ACTION","action_id":str(action_id),"n":0,"next_mean":dict(context),
                    "mean_delta":{},"predictive_covariance":{},"parameter_information_gain_nats":0.0}
        ctx=self._numeric_row(context)
        before_common=set(rows[0][0]); output_common=set(rows[0][0]) & set(rows[0][1])
        for b,a,w in rows[1:]:
            before_common &= set(b); output_common &= (set(b)&set(a))
        input_order=sorted(before_common & set(ctx))[:max(1,int(max_features))]
        output_order=sorted(output_common)[:max(1,int(max_features))]
        if not input_order or not output_order:
            return {"status":"INSUFFICIENT_SHARED_FEATURES","action_id":str(action_id),"n":len(rows),"next_mean":dict(context)}
        p=len(input_order)+1; lam=max(1e-6,float(ridge)); A=_eye(p,lam)
        bs={y:[0.0]*p for y in output_order}; W=0.0
        for before,after,w in rows:
            phi=[1.0]+[before[k] for k in input_order]; W+=w
            for i in range(p):
                for j in range(p): A[i][j]+=w*phi[i]*phi[j]
            for y in output_order:
                dy=after[y]-before[y]
                for i in range(p): bs[y][i]+=w*phi[i]*dy
        inv=_inverse(A); beta={y:_mat_vec(inv,b) for y,b in bs.items()}
        phi0=[1.0]+[ctx[k] for k in input_order]
        mean_delta={y:_dot(phi0,beta[y]) for y in output_order}
        leverage=max(0.0,_dot(phi0,_mat_vec(inv,phi0)))
        resid=[]
        for before,after,w in rows:
            ph=[1.0]+[before[k] for k in input_order]
            rv=[]
            for y in output_order:
                rv.append((after[y]-before[y])-_dot(ph,beta[y]))
            resid.append((rv,w))
        cov=[[0.0]*len(output_order) for _ in output_order]
        if W>0:
            for i in range(len(output_order)):
                for j in range(len(output_order)):
                    cov[i][j]=sum(w*r[i]*r[j] for r,w in resid)/W
                    if i==j: cov[i][j]+=max(.001,(1.0/(1.0+W))*.05)
        pred_cov=[[cov[i][j] for j in range(len(output_order))] for i in range(len(output_order))]
        for i in range(len(output_order)):
            pred_cov[i][i]+=max(0.0,cov[i][i])*leverage
        nxt=dict(context)
        for y,d in mean_delta.items():
            if y in nxt and isinstance(nxt[y],(int,float)): nxt[y]=float(nxt[y])+d
        info=.5*len(output_order)*math.log1p(leverage)
        return {
            "status":"STATE_DEPENDENT_MODEL","action_id":str(action_id),"n":len(rows),"weight_sum":round(W,6),
            "input_features":input_order,"output_features":output_order,
            "mean_delta":{k:round(v,6) for k,v in mean_delta.items()},"next_mean":nxt,
            "residual_covariance":{output_order[i]:{output_order[j]:round(cov[i][j],6) for j in range(len(output_order))} for i in range(len(output_order))},
            "predictive_covariance":{output_order[i]:{output_order[j]:round(pred_cov[i][j],6) for j in range(len(output_order))} for i in range(len(output_order))},
            "posterior_leverage":round(leverage,6),"parameter_information_gain_nats":round(info,6),
            "law":"ridge state-dependent delta regression is derived only from observed before/after transitions and remains model-conditional",
        }

    @staticmethod
    def _dominant_eigen(cov: Sequence[Sequence[float]], iterations: int = 16) -> tuple[float,list[float]]:
        n=len(cov)
        if n==0: return 0.0,[]
        v=[1.0/math.sqrt(n)]*n
        for _ in range(iterations):
            w=_mat_vec(cov,v); norm=math.sqrt(sum(x*x for x in w))
            if norm<=1e-12: return 0.0,[0.0]*n
            v=[x/norm for x in w]
        lam=max(0.0,_dot(v,_mat_vec(cov,v)))
        return lam,v

    def _action_reward(self, action: Mapping[str,Any], context: Mapping[str,Any]) -> float:
        if action.get("configuration"):
            return float(self.collective.evaluate(action["configuration"])["return_on_group_organization"])
        value=float(action.get("base_reward",.5))
        weights=action.get("reward_weights") or {}
        for k,w in weights.items():
            if k in context and isinstance(context[k],(int,float)): value+=float(w)*float(context[k])
        return _clamp(value)

    def scenario_evaluate(self, initial_context: Mapping[str,Any], actions: Sequence[Mapping[str,Any]],
                          trajectories: Sequence[Mapping[str,Any]], discount: float = .95,
                          scenario_sigma: float = 1.0, cvar_alpha: float = .20,
                          risk_aversion: float = .25, ridge: float = 1.0) -> dict[str,Any]:
        amap={str(a.get("id")):dict(a) for a in actions if str(a.get("id",""))}
        if not amap or not trajectories: raise ValueError("actions and trajectories must not be empty")
        alpha=max(.01,min(.99,float(cvar_alpha))); sig=max(0.0,float(scenario_sigma)); ranked=[]
        for tr in trajectories:
            seq=[str(x) for x in tr.get("actions",[])]
            if not seq or len(seq)>4 or any(a not in amap for a in seq): continue
            branches=[{"p":1.0,"context":dict(initial_context),"return":0.0}]
            truncated=False
            for t,aid in enumerate(seq):
                nxt=[]
                for b in branches:
                    action=amap[aid]; reward=self._action_reward(action,b["context"])
                    model=self.state_transition_model(aid,b["context"],ridge)
                    mean=dict(model.get("next_mean",b["context"]))
                    order=list(model.get("output_features",[])); covm=model.get("predictive_covariance",{})
                    mat=[[float(covm.get(x,{}).get(y,0.0)) for y in order] for x in order]
                    lam,vec=self._dominant_eigen(mat)
                    spread=sig*math.sqrt(max(0.0,lam))
                    scenarios=[(0.0,1.0)] if not order or spread<=1e-12 else [(-spread,.25),(0.0,.5),(spread,.25)]
                    for shock,p in scenarios:
                        c=dict(mean)
                        for i,k in enumerate(order):
                            if k in c and isinstance(c[k],(int,float)): c[k]=float(c[k])+shock*vec[i]
                        nxt.append({"p":b["p"]*p,"context":c,"return":b["return"]+(discount**t)*reward})
                branches=nxt
                if len(branches)>20000:
                    truncated=True; branches=sorted(branches,key=lambda x:-x["p"])[:20000]
                    z=sum(x["p"] for x in branches) or 1.0
                    for x in branches: x["p"]/=z
            if not branches: continue
            exp=sum(b["p"]*b["return"] for b in branches)
            ordered=sorted(branches,key=lambda x:x["return"]); need=alpha; acc=0.0; mass=0.0
            for b in ordered:
                take=min(need,b["p"]); acc+=take*b["return"];mass+=take;need-=take
                if need<=1e-12: break
            cvar=acc/max(1e-12,mass)
            score=exp-max(0.0,float(risk_aversion))*max(0.0,exp-cvar)
            ranked.append({"id":str(tr.get("id",','.join(seq))),"actions":seq,"expected_return":round(exp,6),
                           "cvar_lower_tail_return":round(cvar,6),"risk_adjusted_score":round(score,6),
                           "scenario_count":len(branches),"truncated":truncated})
        ranked.sort(key=lambda x:(-x["risk_adjusted_score"],x["id"]))
        return {"decision":"SIMULATE_ONLY","ranked":ranked,"winner":ranked[0]["id"] if ranked else None,
                "law":"finite three-branch moment scenario trees are model simulations, not observed futures or globally optimal contingent policies"}

    def dual_control_plan(self, initial_context: Mapping[str,Any], actions: Sequence[Mapping[str,Any]],
                          horizon: int = 3, beam_width: int = 64, discount: float = .95,
                          risk_aversion: float = .25, information_weight: float = .20,
                          ridge: float = 1.0) -> dict[str,Any]:
        if not actions: raise ValueError("actions must not be empty")
        H=max(1,min(int(horizon),5));beam=max(1,min(int(beam_width),512))
        states=[{"context":dict(initial_context),"score":0.0,"control":0.0,"information":0.0,"risk":0.0,"sequence":[]}]
        for t in range(H):
            nxt=[]
            for st in states:
                for a in actions:
                    aid=str(a.get("id",""))
                    if not aid: continue
                    model=self.state_transition_model(aid,st["context"],ridge)
                    control=self._action_reward(a,st["context"])
                    if model.get("status")=="UNSEEN_ACTION":
                        info=max(0.0,float(a.get("unseen_information_prior",1.0)));risk=max(.5,float(a.get("unseen_risk_prior",.75)))
                        next_context=dict(st["context"])
                    else:
                        info=max(0.0,float(model.get("parameter_information_gain_nats",0.0)))
                        cov=model.get("predictive_covariance",{});diag=[max(0.0,float(v.get(k,0.0))) for k,v in cov.items()]
                        risk=math.sqrt(sum(diag)/max(1,len(diag))) if diag else 0.0
                        next_context=dict(model.get("next_mean",st["context"]))
                    step=control+max(0.0,float(information_weight))*info-max(0.0,float(risk_aversion))*risk
                    d=discount**t
                    nxt.append({"context":next_context,"score":st["score"]+d*step,"control":st["control"]+d*control,
                                "information":st["information"]+d*info,"risk":st["risk"]+d*risk,"sequence":st["sequence"]+[aid]})
            nxt.sort(key=lambda s:(-s["score"],s["risk"],s["sequence"]));states=nxt[:beam]
        best=states[0] if states else {"sequence":[],"score":0.0,"control":0.0,"information":0.0,"risk":0.0}
        return {"decision":"DUAL_CONTROL_PROXY_PLAN_ONLY","first_action":best["sequence"][0] if best["sequence"] else None,
                "best_sequence":best["sequence"],"score":round(best["score"],6),
                "control_value":round(best["control"],6),"information_value_nats":round(best["information"],6),"risk_proxy":round(best["risk"],6),
                "ranked":[{"sequence":s["sequence"],"score":round(s["score"],6),"control":round(s["control"],6),
                           "information":round(s["information"],6),"risk":round(s["risk"],6)} for s in states[:20]],
                "law":"proxy values actions for control plus parameter information and risk; execute only the first authorized action, observe reality, and replan; this is not exact Bayesian belief-state dual control"}

    @staticmethod
    def _directed_reachable(src: str, dst: str, edges: Sequence[tuple[str,str]], blocked: set[str] | None = None) -> bool:
        blocked=set(blocked or set())
        if src in blocked or dst in blocked: return False
        children={}
        for a,b in edges:
            if a in blocked or b in blocked: continue
            children.setdefault(a,set()).add(b)
        seen={src};stack=[src]
        while stack:
            x=stack.pop()
            if x==dst: return True
            for y in children.get(x,set()):
                if y not in seen: seen.add(y);stack.append(y)
        return False

    def _persist_identification(self, method: str, treatment: str, outcome: str, status: str,
                                witness: Mapping[str,Any], assumptions: Mapping[str,Any], actor: str) -> str:
        aid=_stable_id("V7ID",method,treatment,outcome,status,time.time())
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v7_identifications VALUES(?,?,?,?,?,?,?,?,?)",
                              (aid,method,treatment,outcome,status,json.dumps(witness,sort_keys=True),json.dumps(assumptions,sort_keys=True),actor,time.time()))
        return aid

    def causal_identify_extended(self, method: str, treatment: str, outcome: str, edges: Sequence[Any],
                                 observed_nodes: Sequence[str] | None = None,
                                 mediators: Sequence[str] | None = None,
                                 instruments: Sequence[str] | None = None,
                                 assumptions: Mapping[str,Any] | None = None,
                                 max_adjustment_size: int = 4, actor: str = "agent") -> dict[str,Any]:
        method=str(method).upper();treatment=str(treatment);outcome=str(outcome);ass=dict(assumptions or {})
        graph=self.discovery._parse_edges(edges);observed=set(map(str,observed_nodes or [n for e in graph for n in e]))
        if method=="BACKDOOR":
            return self.discovery.causal_identify(treatment,outcome,edges,list(observed),ass,max_adjustment_size,actor)
        if ass.get("latent_confounding_possible"):
            status="UNIDENTIFIED_LATENT_CONFOUNDING_RISK";witness={"method":method}
        elif method=="FRONTDOOR":
            ms=[str(m) for m in (mediators or []) if str(m)]
            if not ms:
                raise ValueError("frontdoor requires mediators")
            intercepts=not self._directed_reachable(treatment,outcome,graph,set(ms))
            chain=all(self._directed_reachable(treatment,m,graph) and self._directed_reachable(m,outcome,graph) for m in ms)
            back_t=[(a,b) for a,b in graph if a!=treatment]
            no_t_m_confound=all(self.discovery._d_separated(treatment,m,set(),back_t) for m in ms)
            m_y_blocked=[]
            for m in ms:
                back_m=[(a,b) for a,b in graph if a!=m]
                m_y_blocked.append(self.discovery._d_separated(m,outcome,{treatment},back_m))
            observed_ok=all(m in observed for m in ms)
            ok=intercepts and chain and no_t_m_confound and all(m_y_blocked) and observed_ok
            status="IDENTIFIED_FRONTDOOR_UNDER_DAG" if ok else "UNIDENTIFIED_FRONTDOOR_CRITERIA"
            witness={"mediators":ms,"all_directed_paths_intercepted":intercepts,"treatment_mediator_chain":chain,
                     "no_unblocked_treatment_mediator_backdoor":no_t_m_confound,"mediator_outcome_backdoors_blocked_by_treatment":all(m_y_blocked),
                     "mediators_observed":observed_ok}
        elif method=="INSTRUMENT":
            zs=[str(z) for z in (instruments or []) if str(z)]
            if not zs: raise ValueError("instrument method requires instruments")
            back_t=[(a,b) for a,b in graph if a!=treatment]
            desc_t=self.discovery._descendants(treatment,graph)
            valid=[];detail={}
            for z in zs:
                relevance=self._directed_reachable(z,treatment,graph)
                exogeneity_exclusion=self.discovery._d_separated(z,outcome,set(),back_t)
                pre_treatment=z not in desc_t and z in observed
                detail[z]={"relevance":relevance,"exclusion_exogeneity_under_dag":exogeneity_exclusion,"observed_pre_treatment":pre_treatment}
                if relevance and exogeneity_exclusion and pre_treatment: valid.append(z)
            status="IDENTIFIED_INSTRUMENT_UNDER_DAG" if valid else "UNIDENTIFIED_NO_VALID_INSTRUMENT"
            witness={"valid_instruments":valid,"candidates":detail}
        else:
            raise ValueError("method must be BACKDOOR, FRONTDOOR, or INSTRUMENT")
        aid=self._persist_identification(method,treatment,outcome,status,witness,ass,str(actor))
        return {"analysis_id":aid,"method":method,"status":status,"treatment":treatment,"outcome":outcome,
                "witness":witness,"assumptions":ass,
                "law":"extended identification is conditional on the supplied DAG, observed-node declarations, graph semantics, and causal assumptions; it is not unconditional causal truth"}

    @staticmethod
    def _evidence_similarity(a: Mapping[str,Any], b: Mapping[str,Any], dimensions: Sequence[str],
                             same_key: bool = False) -> float:
        if same_key: return 1.0
        shared=[]
        for d in dimensions:
            if d in a and d in b and a[d] not in (None,"") and b[d] not in (None,""):
                shared.append(1.0 if str(a[d])==str(b[d]) else 0.0)
        return sum(shared)/len(shared) if shared else .5

    def _independence_group(self, rows: Sequence[Mapping[str,Any]], dimensions: Sequence[str]) -> dict[str,Any]:
        n=len(rows)
        if not n: return {"n":0,"effective_n":0.0,"matrix":[]}
        ev=[];weights=[]
        for r in rows:
            try: e=json.loads(r["evidence_json"])
            except Exception: e={}
            ev.append(e);weights.append(max(0.0,float(r["confidence"])))
        matrix=[];den=0.0
        for i in range(n):
            row=[]
            for j in range(n):
                sim=self._evidence_similarity(ev[i],ev[j],dimensions,str(rows[i]["independence_key"])==str(rows[j]["independence_key"]))
                row.append(round(sim,6));den+=weights[i]*weights[j]*sim
            matrix.append(row)
        sw=sum(weights);neff=(sw*sw/den) if den>1e-12 else 0.0
        completeness=sum(sum(1 for d in dimensions if d in e and e[d] not in (None,"")) for e in ev)/(n*max(1,len(dimensions)))
        return {"n":n,"effective_n":round(neff,6),"metadata_completeness":round(completeness,6),"similarity_matrix":matrix}

    def replication_independence(self, claim_id: str, dimensions: Sequence[str] | None = None,
                                 min_confidence: float = .5) -> dict[str,Any]:
        if not self.s.one("SELECT claim_id FROM collective_v6_claims WHERE claim_id=?",(str(claim_id),)):
            raise ValueError("claim not found")
        dims=list(dimensions or ["dataset","implementation","method","operator","environment","seed_family"])
        rows=self.s.rows("SELECT * FROM collective_v6_claim_witnesses WHERE claim_id=? ORDER BY created_at",(str(claim_id),))
        good=[r for r in rows if float(r["confidence"])>=float(min_confidence)]
        support=[r for r in good if r["result"]=="SUPPORTS"]
        falsify=[r for r in good if r["result"]=="FALSIFIES"]
        return {"claim_id":str(claim_id),"dimensions":dims,"support":self._independence_group(support,dims),
                "falsification":self._independence_group(falsify,dims),"raw_witness_count":len(rows),
                "law":"effective_n is a conservative metadata-similarity diagnostic; caller metadata and independence keys do not constitute formal statistical independence proof"}

    def replication_design(self, claim_id: str, candidates: Sequence[Mapping[str,Any]], mode: str = "REPLICATION",
                           dimensions: Sequence[str] | None = None, cost_weight: float = .10,
                           risk_weight: float = .20) -> dict[str,Any]:
        if not candidates: raise ValueError("candidates must not be empty")
        if not self.s.one("SELECT claim_id FROM collective_v6_claims WHERE claim_id=?",(str(claim_id),)):
            raise ValueError("claim not found")
        dims=list(dimensions or ["dataset","implementation","method","operator","environment","seed_family"])
        mode=str(mode).upper()
        if mode not in {"REPLICATION","FALSIFIER"}: raise ValueError("mode must be REPLICATION or FALSIFIER")
        rows=self.s.rows("SELECT * FROM collective_v6_claim_witnesses WHERE claim_id=? ORDER BY created_at",(str(claim_id),))
        existing=[]
        for r in rows:
            try: existing.append((json.loads(r["evidence_json"]),str(r["independence_key"])))
            except Exception: existing.append(({},str(r["independence_key"])))
        ranked=[]
        for i,c in enumerate(candidates):
            cid=str(c.get("id",f"D{i}"));e=dict(c.get("evidence") or {})
            sims=[self._evidence_similarity(e,old,dims,False) for old,key in existing]
            novelty=1.0-max(sims) if sims else .5
            power=_clamp(c.get("expected_power",.5));cost=max(0.0,float(c.get("cost",0.0)));risk=_clamp(c.get("risk",0.0));feas=_clamp(c.get("feasibility",1.0))
            score=power*(.5+.5*novelty)*feas-float(cost_weight)*cost-float(risk_weight)*risk
            ranked.append({"id":cid,"novelty":round(novelty,6),"expected_power":round(power,6),"feasibility":round(feas,6),
                           "cost":round(cost,6),"risk":round(risk,6),"score":round(score,6)})
        ranked.sort(key=lambda x:(-x["score"],-x["novelty"],x["id"]))
        return {"decision":"DESIGN_ONLY","mode":mode,"selected":ranked[0]["id"] if ranked else None,"ranked":ranked,
                "law":"design maximizes expected evidential power and metadata diversity subject to cost/risk; selected design is not a replication/falsification result"}
