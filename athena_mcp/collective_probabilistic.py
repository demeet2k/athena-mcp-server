from __future__ import annotations

import itertools
import json
import math
import time
from typing import Any, Mapping, Sequence

from .collective_inference import CollectiveInferenceRuntime
from .collective_discovery import _inverse

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v10_gp_models(
 context_key TEXT PRIMARY KEY,
 feature_order_json TEXT NOT NULL,
 length_scale REAL NOT NULL,
 signal_variance REAL NOT NULL,
 noise_variance REAL NOT NULL,
 observations_json TEXT NOT NULL,
 metadata_json TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v10_dependence_labels(
 label_id INTEGER PRIMARY KEY AUTOINCREMENT,
 scope TEXT NOT NULL,
 features_json TEXT NOT NULL,
 label INTEGER NOT NULL,
 weight REAL NOT NULL,
 evidence_ref TEXT NOT NULL,
 created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v10_dependence_models(
 scope TEXT PRIMARY KEY,
 feature_order_json TEXT NOT NULL,
 coefficients_json TEXT NOT NULL,
 n INTEGER NOT NULL,
 log_loss REAL NOT NULL,
 updated_at REAL NOT NULL
);
"""


def _clamp01(x: Any) -> float:
    return max(0.0, min(1.0, float(x)))


def _sigmoid(z: float) -> float:
    if z >= 0:
        ez = math.exp(-min(60.0, z))
        return 1.0 / (1.0 + ez)
    ez = math.exp(max(-60.0, z))
    return ez / (1.0 + ez)


def _logit(p: float) -> float:
    q = max(1e-9, min(1.0 - 1e-9, float(p)))
    return math.log(q / (1.0 - q))


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _variance(xs: Sequence[float], ddof: int = 1) -> float:
    if len(xs) <= ddof:
        return 0.0
    m = _mean(xs)
    return sum((float(x) - m) ** 2 for x in xs) / (len(xs) - ddof)


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _mat_vec(a: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    return [sum(float(a[i][j]) * float(x[j]) for j in range(len(x))) for i in range(len(a))]


def _rbf(x: Sequence[float], z: Sequence[float], length_scale: float, signal_variance: float) -> float:
    ls2 = max(1e-12, float(length_scale) ** 2)
    d2 = sum((float(a) - float(b)) ** 2 for a, b in zip(x, z))
    return max(1e-12, float(signal_variance)) * math.exp(-0.5 * d2 / ls2)


def _corr(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    mx = _mean(x); my = _mean(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x)); sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx <= 1e-15 or sy <= 1e-15:
        return 0.0
    return max(-0.999999999, min(0.999999999, sum((x[i] - mx) * (y[i] - my) for i in range(len(x))) / (sx * sy)))


def _residual(y: Sequence[float], controls: Sequence[Sequence[float]]) -> list[float]:
    if not controls:
        return [float(v) for v in y]
    n = len(y); p = len(controls) + 1
    A = [[0.0] * p for _ in range(p)]; b = [0.0] * p
    for t in range(n):
        phi = [1.0] + [float(c[t]) for c in controls]
        for i in range(p):
            b[i] += phi[i] * float(y[t])
            for j in range(p):
                A[i][j] += phi[i] * phi[j]
    for i in range(1, p):
        A[i][i] += 1e-8
    beta = _mat_vec(_inverse(A), b)
    return [float(y[t]) - _dot(beta, [1.0] + [float(c[t]) for c in controls]) for t in range(n)]


def _partial_corr(x: Sequence[float], y: Sequence[float], controls: Sequence[Sequence[float]]) -> float:
    return _corr(_residual(x, controls), _residual(y, controls))


def _fisher_p(r: float, n: int, k: int) -> float:
    if n - k - 3 <= 0:
        return 1.0
    rr = max(-0.999999, min(0.999999, float(r)))
    z = abs(0.5 * math.log((1.0 + rr) / (1.0 - rr))) * math.sqrt(max(1.0, n - k - 3))
    return max(0.0, min(1.0, math.erfc(z / math.sqrt(2.0))))


def _fit_logistic(rows: Sequence[Mapping[str, float]], label_key: str, feature_keys: Sequence[str], l2: float = 1e-4, steps: int = 500) -> list[float]:
    p = len(feature_keys) + 1
    beta = [0.0] * p
    n = max(1, len(rows))
    for it in range(max(50, int(steps))):
        g = [0.0] * p
        for row in rows:
            phi = [1.0] + [float(row[k]) for k in feature_keys]
            pr = _sigmoid(_dot(beta, phi)); err = float(row[label_key]) - pr
            for j in range(p):
                g[j] += err * phi[j]
        lr = 0.35 / math.sqrt(1.0 + it / 20.0)
        for j in range(p):
            reg = 0.0 if j == 0 else max(0.0, float(l2)) * beta[j]
            beta[j] += lr * (g[j] / n - reg)
    return beta


def _predict_logistic(beta: Sequence[float], row: Mapping[str, float], feature_keys: Sequence[str]) -> float:
    return _sigmoid(_dot(beta, [1.0] + [float(row[k]) for k in feature_keys]))


def _fit_linear(rows: Sequence[Mapping[str, float]], label_key: str, feature_keys: Sequence[str], ridge: float = 1e-6) -> list[float]:
    p = len(feature_keys) + 1
    A = [[0.0] * p for _ in range(p)]; b = [0.0] * p
    for row in rows:
        phi = [1.0] + [float(row[k]) for k in feature_keys]
        for i in range(p):
            b[i] += phi[i] * float(row[label_key])
            for j in range(p):
                A[i][j] += phi[i] * phi[j]
    for i in range(1, p):
        A[i][i] += max(1e-12, float(ridge))
    return _mat_vec(_inverse(A), b)


def _predict_linear(beta: Sequence[float], row: Mapping[str, float], feature_keys: Sequence[str]) -> float:
    return _dot(beta, [1.0] + [float(row[k]) for k in feature_keys])


class _NodeLimit(Exception):
    pass


class CollectiveProbabilisticRuntime:
    """V10 nonlinear probabilistic / causal-control layer.

    The GP is exact regression for the declared fixed RBF kernel and bounded stored
    data. PC-stable is a bounded Gaussian conditional-independence procedure. TMLE
    is a binary-treatment/binary-outcome logistic fluctuation estimator. The POMDP
    solver is exact only for the supplied finite model and completed bounded tree.
    """

    def __init__(self, inference: CollectiveInferenceRuntime):
        self.inference = inference
        self.belief = inference.belief
        self.s = inference.s
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        gp = self.s.one("SELECT COUNT(*) AS n FROM collective_v10_gp_models")["n"]
        lab = self.s.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels")["n"]
        mod = self.s.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_models")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V10",
            "persistent_surfaces": {"gp_models": gp, "dependence_labels": lab, "dependence_models": mod},
            "operators": [
                "gp_register", "gp_state", "gp_observe", "gp_predict",
                "pc_stable_discover", "causal_tmle_binary", "sensitivity_evalue",
                "pomdp_solve", "dependence_observe", "dependence_fit", "dependence_predict",
            ],
            "laws": [
                "FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH",
                "BOUNDED_PC_STABLE != FCI_OR_HIDDEN_CONFOUNDER_DISCOVERY",
                "TMLE_ESTIMATE != IDENTIFICATION_PROOF",
                "E_VALUE != UNIVERSAL_HIDDEN_CONFOUNDING_BOUND",
                "FINITE_POMDP_CERTIFICATE != INFINITE_HORIZON_OR_REAL_WORLD_OPTIMALITY",
                "LEARNED_DEPENDENCE_MODEL != FORMAL_INDEPENDENCE_PROOF",
            ],
        }

    # ---------- fixed-kernel exact Gaussian process ----------
    def gp_register(self, context_key: str, features: Sequence[str], length_scale: float = 1.0,
                    signal_variance: float = 1.0, noise_variance: float = .05,
                    metadata: Mapping[str, Any] | None = None, replace: bool = False) -> dict[str, Any]:
        order = [str(x) for x in features]
        if not order or len(order) > 12 or len(set(order)) != len(order):
            raise ValueError("features must contain 1..12 unique names")
        ls = max(1e-6, float(length_scale)); sv = max(1e-9, float(signal_variance)); nv = max(1e-9, float(noise_variance))
        exists = self.s.one("SELECT COUNT(*) AS n FROM collective_v10_gp_models WHERE context_key=?", (str(context_key),))["n"]
        if exists and not replace:
            raise ValueError("GP model already exists; set replace=true")
        now = time.time()
        with self.s._lock, self.s.db:
            if exists:
                self.s.db.execute("DELETE FROM collective_v10_gp_models WHERE context_key=?", (str(context_key),))
            self.s.db.execute("INSERT INTO collective_v10_gp_models VALUES(?,?,?,?,?,?,?,?,?)", (
                str(context_key), json.dumps(order), ls, sv, nv, "[]", json.dumps(dict(metadata or {}), sort_keys=True), now, now,
            ))
        return self.gp_state(context_key)

    def _gp_row(self, context_key: str):
        row = self.s.one("SELECT * FROM collective_v10_gp_models WHERE context_key=?", (str(context_key),))
        if not row:
            raise ValueError("GP model not found")
        return row

    def gp_state(self, context_key: str) -> dict[str, Any]:
        row = self._gp_row(context_key); obs = json.loads(row["observations_json"])
        return {"status":"FIXED_KERNEL_GP_STATE", "context_key":str(context_key),
                "features":json.loads(row["feature_order_json"]), "length_scale":float(row["length_scale"]),
                "signal_variance":float(row["signal_variance"]), "noise_variance":float(row["noise_variance"]),
                "observation_count":len(obs), "metadata":json.loads(row["metadata_json"]),
                "law":"exact GP regression is relative to the declared fixed RBF kernel/hyperparameters and observed rows; it is not world truth"}

    def gp_observe(self, context_key: str, features: Mapping[str, Any], target: float,
                   evidence_ref: str = "", actor: str = "agent") -> dict[str, Any]:
        row = self._gp_row(context_key); order = json.loads(row["feature_order_json"])
        if any(k not in features for k in order):
            raise ValueError("feature value required for every GP feature")
        obs = json.loads(row["observations_json"])
        if len(obs) >= 128:
            raise ValueError("GP observation cap reached (128); prune or create a new scoped model")
        obs.append({"x":[float(features[k]) for k in order], "y":float(target), "evidence_ref":str(evidence_ref), "actor":str(actor), "t":time.time()})
        with self.s._lock, self.s.db:
            self.s.db.execute("UPDATE collective_v10_gp_models SET observations_json=?,updated_at=? WHERE context_key=?", (json.dumps(obs), time.time(), str(context_key)))
        return {**self.gp_state(context_key), "observed_target":float(target), "evidence_ref":str(evidence_ref),
                "law":"only explicit observed targets enter GP training data; prediction/design calls never self-train"}

    def gp_predict(self, context_key: str, features: Mapping[str, Any], include_observation_noise: bool = True) -> dict[str, Any]:
        row = self._gp_row(context_key); order = json.loads(row["feature_order_json"])
        if any(k not in features for k in order):
            raise ValueError("feature value required for every GP feature")
        xq = [float(features[k]) for k in order]; obs = json.loads(row["observations_json"])
        ls=float(row["length_scale"]); sv=float(row["signal_variance"]); nv=float(row["noise_variance"])
        if not obs:
            latent=sv; pred=latent+(nv if include_observation_noise else 0.0)
            return {"status":"GP_PRIOR_PREDICTION","context_key":str(context_key),"mean":0.0,"latent_variance":round(latent,10),"predictive_variance":round(pred,10),"std":round(math.sqrt(max(0.0,pred)),10),"observation_count":0,
                    "law":"prediction is prior/model output and never an observation"}
        n=len(obs); K=[[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                K[i][j]=_rbf(obs[i]["x"],obs[j]["x"],ls,sv)
            K[i][i]+=nv+1e-9
        Ki=_inverse(K); y=[float(o["y"]) for o in obs]; alpha=_mat_vec(Ki,y)
        k=[_rbf(o["x"],xq,ls,sv) for o in obs]
        mean=_dot(k,alpha); latent=max(0.0,sv-_dot(k,_mat_vec(Ki,k)))
        pred=latent+(nv if include_observation_noise else 0.0)
        return {"status":"GP_POSTERIOR_PREDICTION","context_key":str(context_key),"mean":round(mean,10),"latent_variance":round(latent,10),"predictive_variance":round(pred,10),"std":round(math.sqrt(max(0.0,pred)),10),"observation_count":n,
                "kernel":{"kind":"RBF","length_scale":ls,"signal_variance":sv,"noise_variance":nv},
                "law":"exact fixed-hyperparameter GP posterior prediction is model conditional; GP uncertainty is not factual truth"}

    # ---------- bounded Gaussian PC-stable ----------
    def pc_stable_discover(self, samples: Sequence[Mapping[str, Any]], variables: Sequence[str] | None = None,
                           alpha: float = .05, max_conditioning: int = 2) -> dict[str, Any]:
        if len(samples) < 12:
            raise ValueError("need at least twelve samples")
        vars_ = [str(v) for v in (variables or sorted(samples[0].keys()))]
        if len(vars_) < 2 or len(vars_) > 10:
            raise ValueError("PC-stable supports 2..10 variables")
        data={v:[] for v in vars_}
        for row in samples:
            for v in vars_:
                if v not in row or not isinstance(row[v],(int,float)):
                    raise ValueError(f"numeric sample missing {v}")
                data[v].append(float(row[v]))
        a=max(1e-6,min(.5,float(alpha))); maxc=max(0,min(int(max_conditioning),3))
        und={tuple(sorted((vars_[i],vars_[j]))) for i in range(len(vars_)) for j in range(i+1,len(vars_))}
        sep: dict[tuple[str,str], list[str]]={}; tests=0
        def neigh(v, edges):
            return {b if a0==v else a0 for a0,b in edges if a0==v or b==v}
        for l in range(maxc+1):
            snap=set(und); adj={v:neigh(v,snap) for v in vars_}; removed=[]
            for x,y in sorted(snap):
                pools=[]
                for base in (x,y):
                    cand=sorted(adj[base]-{y if base==x else x})
                    if len(cand)>=l: pools.extend(itertools.combinations(cand,l))
                seen=set()
                for cond in pools:
                    cond=tuple(sorted(cond))
                    if cond in seen: continue
                    seen.add(cond); tests+=1
                    controls=[data[c] for c in cond]
                    r=_partial_corr(data[x],data[y],controls); p=_fisher_p(r,len(samples),len(cond))
                    if p>a:
                        removed.append((x,y)); sep[(x,y)]=list(cond); sep[(y,x)]=list(cond); break
            for e in removed: und.discard(tuple(sorted(e)))
        skeleton=set(und); directed:set[tuple[str,str]]=set()
        def adjacent(x,y):
            return tuple(sorted((x,y))) in und or (x,y) in directed or (y,x) in directed
        def orient(x,y):
            p=tuple(sorted((x,y)))
            if p in und:
                und.remove(p); directed.add((x,y)); return True
            return False
        # collider orientation
        sk_adj={v:neigh(v,skeleton) for v in vars_}
        for z in vars_:
            ns=sorted(sk_adj[z])
            for i in range(len(ns)):
                for j in range(i+1,len(ns)):
                    x,y=ns[i],ns[j]
                    if tuple(sorted((x,y))) in skeleton: continue
                    if z not in sep.get((x,y),[]):
                        orient(x,z); orient(y,z)
        # bounded Meek R1/R2 closure
        changed=True; rounds=0
        while changed and rounds<32:
            changed=False; rounds+=1
            for a0,b in list(directed):
                for p in list(und):
                    if b not in p: continue
                    c=p[1] if p[0]==b else p[0]
                    if not adjacent(a0,c):
                        changed=orient(b,c) or changed
            for p in list(und):
                a0,b=p
                for c in vars_:
                    if (a0,c) in directed and (c,b) in directed:
                        changed=orient(a0,b) or changed; break
                    if (b,c) in directed and (c,a0) in directed:
                        changed=orient(b,a0) or changed; break
        return {"status":"PC_STABLE_BOUNDED_PARTIAL_GRAPH","n":len(samples),"variables":vars_,"alpha":a,"max_conditioning":maxc,"ci_tests":tests,
                "directed_edges":[{"src":x,"dst":y,"mark":"->"} for x,y in sorted(directed)],
                "undirected_edges":[{"a":x,"b":y,"mark":"o-o"} for x,y in sorted(und)],
                "separation_sets":[{"a":x,"b":y,"conditioning":c} for (x,y),c in sorted(sep.items()) if x<y],
                "law":"bounded Gaussian PC-stable uses Fisher-z linear conditional-independence tests and limited Meek closure; it is not FCI, hidden-confounder discovery, or canonical JSPACE truth"}

    # ---------- binary-outcome cross-fitted TMLE ----------
    def causal_tmle_binary(self, samples: Sequence[Mapping[str, Any]], treatment: str, outcome: str,
                           adjustment: Sequence[str] | None = None, assumptions: Mapping[str, Any] | None = None,
                           propensity_clip: float = .05) -> dict[str, Any]:
        if len(samples)<40:
            raise ValueError("TMLE requires at least forty samples")
        assumptions=dict(assumptions or {})
        if assumptions.get("latent_confounding_possible"):
            return {"status":"UNIDENTIFIED_LATENT_CONFOUNDING_RISK","estimate":None,"method":"TMLE_LOGISTIC_CROSSFIT"}
        z=[str(v) for v in (adjustment or [])]; rows=[]
        for r in samples:
            if treatment not in r or outcome not in r or any(k not in r for k in z):
                raise ValueError("TMLE sample missing required field")
            t=float(r[treatment]); y=float(r[outcome])
            if t not in (0.0,1.0) or y not in (0.0,1.0):
                raise ValueError("TMLE_LOGISTIC_CROSSFIT requires binary treatment and binary outcome")
            q={"T":t,"Y":y}; q.update({k:float(r[k]) for k in z}); rows.append(q)
        n=len(rows); clip=max(.01,min(.25,float(propensity_clip)))
        e=[0.5]*n; q0=[0.5]*n; q1=[0.5]*n; qobs=[0.5]*n
        for fold in (0,1):
            train=[rows[i] for i in range(n) if i%2!=fold]; test=[i for i in range(n) if i%2==fold]
            if not train or len({r["T"] for r in train})<2:
                raise ValueError("cross-fit training fold lacks both treatment groups")
            bp=_fit_logistic(train,"T",z)
            bout=_fit_logistic(train,"Y",["T"]+z)
            for i in test:
                base={k:rows[i][k] for k in z}; ei=max(clip,min(1.0-clip,_predict_logistic(bp,base,z))); e[i]=ei
                r0={"T":0.0,**base}; r1={"T":1.0,**base}
                q0[i]=max(1e-6,min(1-1e-6,_predict_logistic(bout,r0,["T"]+z)))
                q1[i]=max(1e-6,min(1-1e-6,_predict_logistic(bout,r1,["T"]+z)))
                qobs[i]=q1[i] if rows[i]["T"]==1.0 else q0[i]
        H=[rows[i]["T"]/e[i]-(1.0-rows[i]["T"])/(1.0-e[i]) for i in range(n)]
        eps=0.0
        for _ in range(80):
            grad=0.0; info=0.0
            for i in range(n):
                qs=_sigmoid(_logit(qobs[i])+eps*H[i]); grad+=H[i]*(rows[i]["Y"]-qs); info+=H[i]*H[i]*qs*(1.0-qs)
            if info<=1e-12: break
            step=grad/info; eps+=step
            if abs(step)<1e-9: break
        q1s=[];q0s=[];ic_base=[]
        for i in range(n):
            q1i=_sigmoid(_logit(q1[i])+eps/e[i]); q0i=_sigmoid(_logit(q0[i])-eps/(1.0-e[i]))
            qobsi=q1i if rows[i]["T"]==1.0 else q0i
            q1s.append(q1i); q0s.append(q0i); ic_base.append(H[i]*(rows[i]["Y"]-qobsi)+q1i-q0i)
        psi=_mean([q1s[i]-q0s[i] for i in range(n)])
        ic=[v-psi for v in ic_base]; se=math.sqrt(max(0.0,_variance(ic))/n); lo=psi-1.96*se; hi=psi+1.96*se
        return {"status":"TMLE_BINARY_ESTIMATED_UNDER_ASSUMPTIONS","method":"TMLE_LOGISTIC_CROSSFIT","estimate":round(psi,8),"standard_error":round(se,8),"ci95":[round(lo,8),round(hi,8)],
                "targeting_epsilon":round(eps,8),"propensity_min":round(min(e),8),"propensity_max":round(max(e),8),"n":n,"adjustment":z,"assumptions":assumptions,
                "law":"binary TMLE estimate/interval remain conditional on identification, positivity, consistency and nuisance-model regularity; TMLE does not prove causality"}

    # ---------- E-value sensitivity metric ----------
    def sensitivity_evalue(self, risk_ratio: float, ci_limit: float | None = None) -> dict[str, Any]:
        rr=float(risk_ratio)
        if rr<=0: raise ValueError("risk_ratio must be positive")
        def ev(r):
            x=r if r>=1.0 else 1.0/r
            return x+math.sqrt(max(0.0,x*(x-1.0)))
        point=ev(rr); ci=None
        if ci_limit is not None:
            c=float(ci_limit)
            if c<=0: raise ValueError("ci_limit must be positive")
            # closest-to-null CI limit: if interval limit crosses/nulls at 1, E-value is 1.
            if (rr>=1 and c<=1) or (rr<1 and c>=1): ci=1.0
            else: ci=ev(c)
        return {"status":"E_VALUE_SENSITIVITY_METRIC","risk_ratio":rr,"evalue_point":round(point,8),"ci_limit":ci_limit,"evalue_ci_limit":None if ci is None else round(ci,8),
                "law":"E-value quantifies minimum confounder association strength on the risk-ratio scale under its standard assumptions; it is not a universal hidden-confounding bound or identification proof"}

    # ---------- exact bounded finite-horizon POMDP tree search ----------
    def pomdp_solve(self, states: Sequence[str], initial_belief: Mapping[str, Any], actions: Sequence[Mapping[str, Any]],
                    horizon: int = 3, discount: float = .95, max_nodes: int = 100000) -> dict[str, Any]:
        ss=[str(s) for s in states]
        if not ss or len(ss)>8 or len(set(ss))!=len(ss): raise ValueError("states must contain 1..8 unique values")
        if not actions or len(actions)>8: raise ValueError("actions must contain 1..8 values")
        H=max(1,min(int(horizon),4)); gamma=max(0.0,min(1.0,float(discount))); limit=max(100,min(int(max_nodes),500000))
        if any(s not in initial_belief for s in ss): raise ValueError("initial belief required for every state")
        def norm(m):
            vals={s:max(0.0,float(m[s])) for s in ss}; z=sum(vals.values())
            if z<=1e-15: raise ValueError("belief mass must be positive")
            return {s:vals[s]/z for s in ss}
        b0=norm(initial_belief); node_count=0
        parsed=[]
        for ai,a in enumerate(actions):
            aid=str(a.get("id",f"A{ai}")); rew=a.get("reward_by_state") or {}; trans=a.get("transition") or {}; obs=a.get("observation") or {}
            if any(s not in rew or s not in trans for s in ss): raise ValueError(f"action {aid} missing reward/transition state")
            T={}; O={}; obs_names=set()
            for s in ss:
                row=trans[s]
                if any(sp not in row for sp in ss): raise ValueError(f"action {aid} transition row incomplete")
                vals={sp:max(0.0,float(row[sp])) for sp in ss}; z=sum(vals.values())
                if abs(z-1.0)>1e-6: raise ValueError(f"action {aid} transition row must sum to 1")
                T[s]=vals
            for sp in ss:
                if sp not in obs: raise ValueError(f"action {aid} observation row missing {sp}")
                row={str(o):max(0.0,float(p)) for o,p in obs[sp].items()}; z=sum(row.values())
                if not row or abs(z-1.0)>1e-6: raise ValueError(f"action {aid} observation row must sum to 1")
                O[sp]=row; obs_names.update(row)
            if len(obs_names)>8: raise ValueError("at most eight observation symbols per action")
            # absent observation symbols are explicit zero probabilities
            for sp in ss:
                for o in obs_names: O[sp].setdefault(o,0.0)
            parsed.append({"id":aid,"reward":{s:float(rew[s]) for s in ss},"T":T,"O":O,"observations":sorted(obs_names),"cost":max(0.0,float(a.get("cost",0.0))),"risk":max(0.0,float(a.get("risk",0.0)))})
        def solve(b,depth):
            nonlocal node_count
            node_count+=1
            if node_count>limit: raise _NodeLimit()
            ranked=[]
            for a in parsed:
                immediate=sum(b[s]*a["reward"][s] for s in ss)-a["cost"]-a["risk"]
                bpred={sp:sum(b[s]*a["T"][s][sp] for s in ss) for sp in ss}; branches=[]; future=0.0
                if depth>1:
                    for o in a["observations"]:
                        po=sum(bpred[sp]*a["O"][sp][o] for sp in ss)
                        if po<=1e-15: continue
                        post={sp:bpred[sp]*a["O"][sp][o]/po for sp in ss}; sub=solve(post,depth-1); future+=po*sub["value"]
                        branches.append({"observation":o,"probability":round(po,10),"posterior":{s:round(post[s],10) for s in ss},"next_action":sub["action"],"subtree":sub["tree"]})
                total=immediate+gamma*future
                ranked.append({"id":a["id"],"value":total,"immediate":immediate,"expected_future":future,"branches":branches})
            best=max(ranked,key=lambda r:(r["value"],r["id"]))
            return {"value":best["value"],"action":best["id"],"tree":{"action":best["id"],"value":round(best["value"],10),"branches":best["branches"]}}
        try:
            out=solve(b0,H)
        except _NodeLimit:
            return {"status":"NODE_LIMIT_NO_EXACT_CERTIFICATE","decision":"PLAN_ONLY","horizon":H,"nodes_expanded":node_count,"max_nodes":limit,"selected":None,
                    "law":"node-limited search does not carry an optimality certificate"}
        return {"status":"FINITE_POMDP_EXACT_HORIZON_CERTIFIED","decision":"PLAN_ONLY","horizon":H,"selected":out["action"],"value":round(out["value"],10),"policy_tree":out["tree"],"nodes_expanded":node_count,"initial_belief":{s:round(b0[s],10) for s in ss},
                "certificate":"EXACT_FOR_SUPPLIED_FINITE_MODEL_AND_HORIZON","law":"exhaustive recursive search is exact only for the supplied finite states/actions/transitions/observations/rewards and bounded horizon; it is not infinite-horizon or real-world optimality"}

    # ---------- empirically calibratable evidence-dependence model ----------
    def dependence_observe(self, scope: str, features: Mapping[str, Any], label: int, weight: float = 1.0, evidence_ref: str = "") -> dict[str, Any]:
        if int(label) not in (0,1): raise ValueError("label must be 0 or 1")
        if not features or len(features)>16: raise ValueError("features must contain 1..16 numeric values")
        vals={str(k):float(v) for k,v in features.items()}; w=max(1e-9,float(weight))
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT INTO collective_v10_dependence_labels(scope,features_json,label,weight,evidence_ref,created_at) VALUES(?,?,?,?,?,?)",(str(scope),json.dumps(vals,sort_keys=True),int(label),w,str(evidence_ref),time.time()))
        n=self.s.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels WHERE scope=?",(str(scope),))["n"]
        return {"status":"DEPENDENCE_LABEL_RECORDED","scope":str(scope),"n":n,"label":int(label),"features":vals,"law":"dependence labels are explicit external calibration observations; prediction/model output cannot label itself"}

    def dependence_fit(self, scope: str, l2: float = .01, iterations: int = 600) -> dict[str, Any]:
        rows=self.s.rows("SELECT * FROM collective_v10_dependence_labels WHERE scope=? ORDER BY label_id",(str(scope),))
        if len(rows)<20: raise ValueError("need at least twenty labelled dependence observations")
        parsed=[{"features":json.loads(r["features_json"]),"label":int(r["label"]),"weight":float(r["weight"])} for r in rows]
        order=sorted({k for r in parsed for k in r["features"]})
        if len(order)>16: raise ValueError("too many dependence features")
        if any(any(k not in r["features"] for k in order) for r in parsed): raise ValueError("dependence calibration rows must share a complete feature schema")
        beta=[0.0]*(len(order)+1); total_w=sum(r["weight"] for r in parsed)
        for it in range(max(100,min(int(iterations),3000))):
            g=[0.0]*len(beta)
            for r in parsed:
                phi=[1.0]+[float(r["features"][k]) for k in order]; p=_sigmoid(_dot(beta,phi)); err=(r["label"]-p)*r["weight"]
                for j in range(len(beta)): g[j]+=err*phi[j]
            lr=.4/math.sqrt(1+it/30)
            for j in range(len(beta)):
                reg=0.0 if j==0 else max(0.0,float(l2))*beta[j]
                beta[j]+=lr*(g[j]/max(1e-9,total_w)-reg)
        losses=[]; correct=0
        for r in parsed:
            p=max(1e-9,min(1-1e-9,_sigmoid(_dot(beta,[1.0]+[float(r["features"][k]) for k in order])))); y=r["label"]
            losses.append(-(y*math.log(p)+(1-y)*math.log(1-p))); correct+=1 if (p>=.5)==bool(y) else 0
        loss=_mean(losses); now=time.time()
        with self.s._lock,self.s.db:
            self.s.db.execute("INSERT OR REPLACE INTO collective_v10_dependence_models VALUES(?,?,?,?,?,?)",(str(scope),json.dumps(order),json.dumps(beta),len(parsed),loss,now))
        return {"status":"EMPIRICAL_LOGISTIC_DEPENDENCE_MODEL","scope":str(scope),"features":order,"coefficients":{"intercept":round(beta[0],10),**{order[i]:round(beta[i+1],10) for i in range(len(order))}},"n":len(parsed),"log_loss":round(loss,10),"training_accuracy":round(correct/len(parsed),8),
                "law":"model is calibrated only to explicit labelled dependence examples from this scope; training fit is not a formal independence theorem"}

    def dependence_predict(self, scope: str, features: Mapping[str, Any]) -> dict[str, Any]:
        row=self.s.one("SELECT * FROM collective_v10_dependence_models WHERE scope=?",(str(scope),))
        if not row: raise ValueError("dependence model not fitted")
        order=json.loads(row["feature_order_json"]); beta=json.loads(row["coefficients_json"])
        if any(k not in features for k in order): raise ValueError("feature value required for every fitted dependence feature")
        p=_sigmoid(_dot(beta,[1.0]+[float(features[k]) for k in order]))
        return {"status":"CALIBRATED_DEPENDENCE_PROBABILITY","scope":str(scope),"probability":round(p,10),"features":{k:float(features[k]) for k in order},"training_n":int(row["n"]),"training_log_loss":round(float(row["log_loss"]),10),
                "law":"probability is conditional on the empirically fitted metadata-label model and its calibration population; it does not prove formal dependence or independence"}
