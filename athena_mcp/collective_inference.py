from __future__ import annotations

import json
import math
import random
import time
from typing import Any, Mapping, Sequence

from .collective_belief import CollectiveBeliefRuntime, _normalize, _entropy
from .collective_discovery import _clamp, _inverse, _mat_vec, _dot

SCHEMA = """
CREATE TABLE IF NOT EXISTS collective_v9_gaussian_beliefs(
 context_key TEXT PRIMARY KEY,
 parameter_order_json TEXT NOT NULL,
 precision_json TEXT NOT NULL,
 natural_json TEXT NOT NULL,
 noise_variance REAL NOT NULL,
 observation_count INTEGER NOT NULL,
 metadata_json TEXT NOT NULL,
 created_at REAL NOT NULL,
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS collective_v9_robust_effects(
 estimate_id TEXT PRIMARY KEY,
 method TEXT NOT NULL,
 treatment TEXT NOT NULL,
 outcome TEXT NOT NULL,
 estimate REAL,
 standard_error REAL,
 status TEXT NOT NULL,
 assumptions_json TEXT NOT NULL,
 witness_json TEXT NOT NULL,
 created_at REAL NOT NULL
);
"""


def _eye(n: int, scale: float = 1.0) -> list[list[float]]:
    return [[float(scale) if i == j else 0.0 for j in range(n)] for i in range(n)]


def _mat_vec_local(a: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    return [sum(float(a[i][j]) * float(x[j]) for j in range(len(x))) for i in range(len(a))]


def _quad(x: Sequence[float], a: Sequence[Sequence[float]]) -> float:
    return _dot(x, _mat_vec_local(a, x))


def _sigmoid(z: float) -> float:
    if z >= 0:
        ez = math.exp(-min(60.0, z))
        return 1.0 / (1.0 + ez)
    ez = math.exp(max(-60.0, z))
    return ez / (1.0 + ez)


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _variance(xs: Sequence[float], ddof: int = 1) -> float:
    if len(xs) <= ddof:
        return 0.0
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def _cholesky(a: Sequence[Sequence[float]], jitter: float = 1e-10) -> list[list[float]]:
    n = len(a)
    for attempt in range(8):
        j = jitter * (10 ** attempt)
        L = [[0.0] * n for _ in range(n)]
        ok = True
        for i in range(n):
            for k in range(i + 1):
                s = sum(L[i][r] * L[k][r] for r in range(k))
                if i == k:
                    v = float(a[i][i]) + j - s
                    if v <= 0:
                        ok = False
                        break
                    L[i][k] = math.sqrt(v)
                else:
                    if abs(L[k][k]) <= 1e-15:
                        ok = False
                        break
                    L[i][k] = (float(a[i][k]) - s) / L[k][k]
            if not ok:
                break
        if ok:
            return L
    raise ValueError("covariance is not positive definite")


def _mvnormal(rng: random.Random, mean: Sequence[float], cov: Sequence[Sequence[float]]) -> list[float]:
    L = _cholesky(cov)
    z = [rng.gauss(0.0, 1.0) for _ in mean]
    return [float(mean[i]) + sum(L[i][j] * z[j] for j in range(i + 1)) for i in range(len(mean))]


class CollectiveInferenceRuntime:
    """V9 continuous-belief / robust-inference layer.

    The continuous posterior is deliberately a finite-dimensional Gaussian linear
    belief, not a general GP/neural posterior. EVPI/EVSI are Monte Carlo estimates.
    AIPW is a bounded cross-fitted binary-treatment estimator whose validity remains
    conditional on causal identification/positivity/consistency assumptions.
    """

    def __init__(self, belief: CollectiveBeliefRuntime):
        self.belief = belief
        self.dual = belief.dual
        self.discovery = belief.discovery
        self.science = belief.science
        self.s = belief.s
        with self.s._lock, self.s.db:
            self.s.db.executescript(SCHEMA)

    def describe(self) -> dict[str, Any]:
        gb = self.s.one("SELECT COUNT(*) AS n FROM collective_v9_gaussian_beliefs")["n"]
        re = self.s.one("SELECT COUNT(*) AS n FROM collective_v9_robust_effects")["n"]
        return {
            "version": "COLLECTIVE_RUNTIME_V9",
            "persistent_surfaces": {"gaussian_beliefs": gb, "robust_effects": re},
            "operators": [
                "gaussian_belief_register", "gaussian_belief_state", "gaussian_belief_observe",
                "decision_evpi", "decision_evsi", "belief_policy_multistage",
                "causal_aipw", "causal_robustness", "structure_partial",
                "evidence_dependence_probability",
            ],
            "laws": [
                "GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES",
                "MONTE_CARLO_EVPI_EVSI != EXACT_ANALYTIC_VALUE",
                "MULTISTAGE_FINITE_BELIEF_POLICY != GENERAL_POMDP",
                "AIPW_ESTIMATE != IDENTIFICATION_PROOF",
                "ROBUSTNESS_PERTURBATION != HIDDEN_CONFOUNDING_BOUND",
                "HEURISTIC_PARTIAL_GRAPH != PAG_OR_FCI_THEOREM",
                "DEPENDENCE_PROBABILITY_MODEL != FORMAL_EVIDENCE_INDEPENDENCE",
            ],
        }

    def gaussian_belief_register(self, context_key: str, parameters: Sequence[str],
                                 mean: Mapping[str, Any] | None = None,
                                 prior_variance: float = 1.0,
                                 noise_variance: float = 1.0,
                                 metadata: Mapping[str, Any] | None = None,
                                 replace: bool = False) -> dict[str, Any]:
        order = [str(x) for x in parameters]
        if not order or len(order) > 32 or len(set(order)) != len(order):
            raise ValueError("parameters must contain 1..32 unique names")
        pv = max(1e-9, float(prior_variance)); nv = max(1e-9, float(noise_variance))
        m = [float((mean or {}).get(k, 0.0)) for k in order]
        precision = _eye(len(order), 1.0 / pv)
        natural = _mat_vec_local(precision, m)
        exists = self.s.one("SELECT COUNT(*) AS n FROM collective_v9_gaussian_beliefs WHERE context_key=?", (str(context_key),))["n"]
        if exists and not replace:
            raise ValueError("gaussian belief already exists; set replace=true")
        now = time.time()
        with self.s._lock, self.s.db:
            if exists:
                self.s.db.execute("DELETE FROM collective_v9_gaussian_beliefs WHERE context_key=?", (str(context_key),))
            self.s.db.execute("INSERT INTO collective_v9_gaussian_beliefs VALUES(?,?,?,?,?,?,?,?,?)", (
                str(context_key), json.dumps(order), json.dumps(precision), json.dumps(natural), nv, 0,
                json.dumps(dict(metadata or {}), sort_keys=True), now, now,
            ))
        return self.gaussian_belief_state(context_key)

    def _gaussian_row(self, context_key: str):
        row = self.s.one("SELECT * FROM collective_v9_gaussian_beliefs WHERE context_key=?", (str(context_key),))
        if not row:
            raise ValueError("gaussian belief not found")
        return row

    def gaussian_belief_state(self, context_key: str) -> dict[str, Any]:
        row = self._gaussian_row(context_key)
        order = json.loads(row["parameter_order_json"])
        A = json.loads(row["precision_json"]); b = json.loads(row["natural_json"])
        cov = _inverse(A); mean = _mat_vec_local(cov, b)
        return {
            "status": "GAUSSIAN_LINEAR_BELIEF", "context_key": str(context_key),
            "parameters": order, "mean": {order[i]: round(mean[i], 10) for i in range(len(order))},
            "covariance": [[round(float(v), 10) for v in r] for r in cov],
            "noise_variance": float(row["noise_variance"]), "observation_count": int(row["observation_count"]),
            "metadata": json.loads(row["metadata_json"]),
            "law": "finite-dimensional Gaussian linear posterior is model state, not canonical truth or a general nonparametric posterior",
        }

    def gaussian_belief_observe(self, context_key: str, features: Mapping[str, Any], target: float,
                                weight: float = 1.0, noise_variance: float | None = None,
                                evidence_ref: str = "", actor: str = "agent") -> dict[str, Any]:
        row = self._gaussian_row(context_key); order = json.loads(row["parameter_order_json"])
        if any(k not in features for k in order):
            raise ValueError("feature value required for every belief parameter")
        x = [float(features[k]) for k in order]; w = max(0.0, float(weight))
        if w <= 0:
            raise ValueError("weight must be positive")
        nv = max(1e-9, float(noise_variance if noise_variance is not None else row["noise_variance"]))
        A = [[float(v) for v in r] for r in json.loads(row["precision_json"])]
        b = [float(v) for v in json.loads(row["natural_json"])]
        scale = w / nv
        for i in range(len(x)):
            b[i] += scale * x[i] * float(target)
            for j in range(len(x)):
                A[i][j] += scale * x[i] * x[j]
        now = time.time()
        with self.s._lock, self.s.db:
            self.s.db.execute("UPDATE collective_v9_gaussian_beliefs SET precision_json=?,natural_json=?,noise_variance=?,observation_count=?,updated_at=? WHERE context_key=?", (
                json.dumps(A), json.dumps(b), nv, int(row["observation_count"]) + 1, now, str(context_key),
            ))
        out = self.gaussian_belief_state(context_key)
        return {**out, "observed_target": float(target), "evidence_ref": str(evidence_ref), "actor": str(actor),
                "law": "only an explicit observed target updates the Gaussian belief; predictions and simulations never self-update"}

    @staticmethod
    def _linear_utility(action: Mapping[str, Any], theta: Mapping[str, float]) -> float:
        base = float(action.get("utility", 0.0)); co = action.get("utility_linear") or {}
        return base + sum(float(co.get(k, 0.0)) * float(v) for k, v in theta.items())

    def _gaussian_params(self, context_key: str):
        st = self.gaussian_belief_state(context_key)
        order = list(st["parameters"]); mean = [float(st["mean"][k]) for k in order]
        cov = [[float(v) for v in r] for r in st["covariance"]]
        return st, order, mean, cov

    def decision_evpi(self, context_key: str, actions: Sequence[Mapping[str, Any]],
                      samples: int = 500, seed: int = 0) -> dict[str, Any]:
        if not actions:
            raise ValueError("actions must not be empty")
        st, order, mean, cov = self._gaussian_params(context_key)
        mean_theta = dict(zip(order, mean))
        current_vals = [(self._linear_utility(a, mean_theta), str(a.get("id", ""))) for a in actions]
        current_best = max(current_vals)
        rng = random.Random(int(seed)); n = max(50, min(int(samples), 5000)); perfect = []
        for _ in range(n):
            draw = _mvnormal(rng, mean, cov); th = dict(zip(order, draw))
            perfect.append(max(self._linear_utility(a, th) for a in actions))
        vpi = max(0.0, _mean(perfect) - current_best[0])
        se = math.sqrt(max(0.0, _variance(perfect)) / n)
        return {
            "status": "MONTE_CARLO_EVPI_ESTIMATE", "context_key": str(context_key),
            "current_best_action": current_best[1], "current_best_expected_utility": round(current_best[0], 8),
            "expected_perfect_information_utility": round(_mean(perfect), 8), "evpi": round(vpi, 8),
            "monte_carlo_se": round(se, 8), "samples": n, "seed": int(seed),
            "law": "EVPI is a Monte Carlo upper-value estimate under the declared Gaussian linear belief and utility model, not universal value of truth",
        }

    def _posterior_after_linear_observation(self, mean: Sequence[float], cov: Sequence[Sequence[float]],
                                            x: Sequence[float], y: float, noise_var: float):
        A = _inverse(cov); b = _mat_vec_local(A, mean); nv = max(1e-9, float(noise_var))
        for i in range(len(x)):
            b[i] += x[i] * float(y) / nv
            for j in range(len(x)):
                A[i][j] += x[i] * x[j] / nv
        C = _inverse(A); m = _mat_vec_local(C, b)
        return m, C

    def decision_evsi(self, context_key: str, actions: Sequence[Mapping[str, Any]], experiments: Sequence[Mapping[str, Any]],
                      samples: int = 300, seed: int = 0, cost_weight: float = 1.0, risk_weight: float = 1.0) -> dict[str, Any]:
        if not actions or not experiments:
            raise ValueError("actions and experiments must not be empty")
        st, order, mean, cov = self._gaussian_params(context_key); mean_theta = dict(zip(order, mean))
        current_best = max(self._linear_utility(a, mean_theta) for a in actions)
        n = max(50, min(int(samples), 3000)); ranked = []
        for ei, e in enumerate(experiments):
            eid = str(e.get("id", f"E{ei}")); design = e.get("design") or {}
            if any(k not in design for k in order):
                ranked.append({"id": eid, "status": "INCOMPLETE_DESIGN_VECTOR", "evsi": 0.0, "score": 0.0}); continue
            x = [float(design[k]) for k in order]; nv = max(1e-9, float(e.get("noise_variance", st["noise_variance"])))
            rng = random.Random(int(seed) + 7919 * (ei + 1)); post_values = []
            for _ in range(n):
                theta = _mvnormal(rng, mean, cov); y = _dot(x, theta) + rng.gauss(0.0, math.sqrt(nv))
                pm, _ = self._posterior_after_linear_observation(mean, cov, x, y, nv)
                pth = dict(zip(order, pm)); post_values.append(max(self._linear_utility(a, pth) for a in actions))
            evsi = max(0.0, _mean(post_values) - current_best)
            mcse = math.sqrt(max(0.0, _variance(post_values)) / n)
            ethical = bool(e.get("ethical", True)); feasibility = _clamp(e.get("feasibility", 1.0)); cost = max(0.0, float(e.get("cost", 0.0))); risk = _clamp(e.get("risk", 0.0))
            score = 0.0 if not ethical else evsi * feasibility - max(0.0, float(cost_weight)) * cost - max(0.0, float(risk_weight)) * risk
            ranked.append({"id": eid, "status": "ELIGIBLE" if ethical else "ETHICS_BLOCK", "evsi": round(evsi, 8), "score": round(score, 8), "monte_carlo_se": round(mcse, 8), "samples": n, "cost": cost, "risk": risk})
        ranked.sort(key=lambda r: (-float(r.get("score", 0.0)), -float(r.get("evsi", 0.0)), r["id"]))
        winner = next((r["id"] for r in ranked if r["status"] == "ELIGIBLE"), None)
        return {"decision": "MONTE_CARLO_EVSI_DESIGN_ONLY", "context_key": str(context_key), "current_best_expected_utility": round(current_best, 8), "winner": winner, "ranked": ranked,
                "law": "EVSI is estimated under the declared Gaussian linear observation/utility model; it is design value, not experimental evidence"}

    def belief_policy_multistage(self, context_key: str, actions: Sequence[Mapping[str, Any]], horizon: int = 2,
                                 discount: float = .95, information_weight: float = 0.0) -> dict[str, Any]:
        belief = self.belief._belief_map(context_key)
        if not actions:
            raise ValueError("actions must not be empty")
        H = max(1, min(int(horizon), 3)); gamma = _clamp(discount, 0.0, 1.0); iw = max(0.0, float(information_weight))
        nodes = 0

        def solve(p: Mapping[str, float], depth: int):
            nonlocal nodes
            nodes += 1
            if depth <= 0:
                vals = [(self.belief._action_utility(a, p), str(a.get("id", ""))) for a in actions]
                best = max(vals)
                return best[0], {"leaf_best_action": best[1], "belief": {k: round(v, 8) for k, v in p.items()}}
            best_score = -1e300; best_tree = None
            h0 = _entropy(p)
            for ai, a in enumerate(actions):
                aid = str(a.get("id", f"A{ai}")); immediate = self.belief._action_utility(a, p); obs = dict(a.get("observation_model") or {})
                future = 0.0; info = 0.0; branches = []
                if obs:
                    for out, like in obs.items():
                        if any(mid not in like for mid in p):
                            raise ValueError(f"action {aid} observation model incomplete")
                        po = sum(p[mid] * _clamp(like[mid]) for mid in p)
                        post = _normalize({mid: p[mid] * _clamp(like[mid]) for mid in p}) if po > 1e-15 else dict(p)
                        child_value, child = solve(post, depth - 1)
                        future += po * child_value; info += po * (h0 - _entropy(post))
                        branches.append({"outcome": str(out), "probability": round(po, 8), "posterior": {k: round(v, 8) for k, v in post.items()}, "child": child})
                else:
                    child_value, child = solve(p, depth - 1); future = child_value; branches = [{"outcome": "NO_OBSERVATION", "probability": 1.0, "child": child}]
                score = immediate + gamma * future + iw * info - max(0.0, float(a.get("cost", 0.0))) - _clamp(a.get("risk", 0.0))
                if score > best_score:
                    best_score = score; best_tree = {"action": aid, "score": round(score, 8), "immediate_utility": round(immediate, 8), "expected_information_gain_bits": round(info, 8), "branches": branches}
            return best_score, best_tree

        value, tree = solve(belief, H)
        return {"decision": "FINITE_BELIEF_MULTISTAGE_POLICY_PLAN_ONLY", "context_key": str(context_key), "horizon": H, "value": round(value, 8), "tree": tree, "expanded_nodes": nodes,
                "law": "finite outcome/model recursion is a bounded design policy; it executes nothing, writes no observations, and is not a general POMDP solution"}

    @staticmethod
    def _features(samples: Sequence[Mapping[str, Any]], names: Sequence[str]):
        rows = []
        for r in samples:
            vals = []
            for n in names:
                if n not in r or not isinstance(r[n], (int, float)):
                    raise ValueError(f"numeric sample missing {n}")
                vals.append(float(r[n]))
            rows.append(vals)
        return rows

    @staticmethod
    def _ridge_fit(X: Sequence[Sequence[float]], y: Sequence[float], ridge: float = 1e-6) -> list[float]:
        if not X:
            raise ValueError("empty design")
        p = len(X[0]); A = [[0.0] * p for _ in range(p)]; b = [0.0] * p
        for x, yy in zip(X, y):
            for i in range(p):
                b[i] += x[i] * yy
                for j in range(p): A[i][j] += x[i] * x[j]
        for i in range(1, p): A[i][i] += max(1e-12, float(ridge))
        return _mat_vec(_inverse(A), b)

    @staticmethod
    def _logistic_fit(X: Sequence[Sequence[float]], y: Sequence[float], ridge: float = 1e-3, steps: int = 400, lr: float = .05) -> list[float]:
        p = len(X[0]); beta = [0.0] * p; n = max(1, len(X))
        for _ in range(steps):
            grad = [0.0] * p
            for x, yy in zip(X, y):
                pr = _sigmoid(_dot(beta, x)); e = yy - pr
                for j in range(p): grad[j] += e * x[j]
            for j in range(1, p): grad[j] -= ridge * beta[j]
            for j in range(p): beta[j] += lr * grad[j] / n
        return beta

    def causal_aipw(self, samples: Sequence[Mapping[str, Any]], treatment: str, outcome: str,
                    adjustment: Sequence[str] | None = None, assumptions: Mapping[str, Any] | None = None,
                    propensity_clip: float = .05) -> dict[str, Any]:
        if len(samples) < 20:
            raise ValueError("AIPW requires at least twenty samples")
        assumptions = dict(assumptions or {})
        if assumptions.get("latent_confounding_possible"):
            return {"status": "UNIDENTIFIED_LATENT_CONFOUNDING_RISK", "estimate": None, "standard_error": None}
        adj = [str(x) for x in (adjustment or [])]
        names = [str(treatment), str(outcome)] + adj
        vals = self._features(samples, names); t = [r[0] for r in vals]; y = [r[1] for r in vals]
        if any(abs(v - round(v)) > 1e-9 or int(round(v)) not in (0, 1) for v in t):
            raise ValueError("AIPW treatment must be binary 0/1")
        t = [float(int(round(v))) for v in t]
        if min(sum(t), len(t) - sum(t)) < 5:
            raise ValueError("both treatment groups need at least five samples")
        n = len(samples); clip = max(.01, min(.25, float(propensity_clip))); psi = [0.0] * n
        for fold in (0, 1):
            train = [i for i in range(n) if i % 2 != fold]; test = [i for i in range(n) if i % 2 == fold]
            Xtr = [[1.0] + [float(samples[i][z]) for z in adj] for i in train]
            ptr = [t[i] for i in train]
            prop_beta = self._logistic_fit(Xtr, ptr)
            X1 = [[1.0] + [float(samples[i][z]) for z in adj] for i in train if t[i] == 1.0]
            y1 = [y[i] for i in train if t[i] == 1.0]; X0 = [[1.0] + [float(samples[i][z]) for z in adj] for i in train if t[i] == 0.0]; y0 = [y[i] for i in train if t[i] == 0.0]
            b1 = self._ridge_fit(X1, y1); b0 = self._ridge_fit(X0, y0)
            for i in test:
                x = [1.0] + [float(samples[i][z]) for z in adj]
                e = min(1.0 - clip, max(clip, _sigmoid(_dot(prop_beta, x))))
                m1 = _dot(b1, x); m0 = _dot(b0, x)
                psi[i] = (m1 - m0) + t[i] * (y[i] - m1) / e - (1.0 - t[i]) * (y[i] - m0) / (1.0 - e)
        est = _mean(psi); se = math.sqrt(max(0.0, _variance(psi)) / n); lo = est - 1.96 * se; hi = est + 1.96 * se
        eid = f"AIPW.{abs(hash((str(treatment), str(outcome), n, round(est, 8)))):x}"
        witness = {"n": n, "adjustment": adj, "propensity_clip": clip, "cross_fit_folds": 2, "ci95": [lo, hi]}
        with self.s._lock, self.s.db:
            self.s.db.execute("INSERT OR REPLACE INTO collective_v9_robust_effects VALUES(?,?,?,?,?,?,?,?,?,?)", (
                eid, "AIPW_CROSS_FIT", str(treatment), str(outcome), est, se, "ESTIMATED_ASSUMPTION_SCOPED",
                json.dumps(assumptions, sort_keys=True), json.dumps(witness, sort_keys=True), time.time(),
            ))
        return {"status": "AIPW_CROSS_FIT_ESTIMATE", "estimate_id": eid, "estimate": round(est, 8), "standard_error": round(se, 8), "ci95": [round(lo, 8), round(hi, 8)], "n": n, "adjustment": adj,
                "law": "AIPW is doubly robust only under its identification/positivity/consistency and nuisance-model conditions; estimate does not prove those assumptions"}

    def causal_robustness(self, samples: Sequence[Mapping[str, Any]], treatment: str, outcome: str,
                          adjustment: Sequence[str], assumptions: Mapping[str, Any] | None = None) -> dict[str, Any]:
        adj = [str(x) for x in adjustment]
        base = self.belief.causal_effect_estimate("BACKDOOR_LINEAR", samples, treatment, outcome, adj, None, None, assumptions)
        if base.get("estimate") is None:
            return {"status": base.get("status", "UNAVAILABLE"), "base": base, "leave_one_out": []}
        vals = []
        for z in adj:
            a2 = [x for x in adj if x != z]
            r = self.belief.causal_effect_estimate("BACKDOOR_LINEAR", samples, treatment, outcome, a2, None, None, assumptions)
            vals.append({"omitted": z, "estimate": r.get("estimate"), "delta_from_base": None if r.get("estimate") is None else round(float(r["estimate"]) - float(base["estimate"]), 8)})
        deltas = [abs(float(v["delta_from_base"])) for v in vals if v["delta_from_base"] is not None]
        return {"status": "LEAVE_ONE_COVARIATE_ROBUSTNESS", "base_estimate": base["estimate"], "leave_one_out": vals, "max_abs_shift": round(max(deltas) if deltas else 0.0, 8),
                "law": "leave-one-adjustment sensitivity is a specification diagnostic, not a formal hidden-confounding bound"}

    def structure_partial(self, samples: Sequence[Mapping[str, Any]], variables: Sequence[str] | None = None,
                          association_threshold: float = .15, resamples: int = 50,
                          support_threshold: float = .7, seed: int = 0) -> dict[str, Any]:
        boot = self.belief.causal_structure_bootstrap(samples, variables, association_threshold, resamples, support_threshold, seed)
        edges = []
        for e in boot.get("stable_edges", []):
            a = e.get("a"); b = e.get("b"); support = float(e.get("support", 0.0)); edges.append({"a": a, "b": b, "endpoint_a": "o", "endpoint_b": "o", "support": support})
        colliders = boot.get("stable_v_structures", [])
        return {"status": "HEURISTIC_PARTIAL_GRAPH", "edges": edges, "collider_candidates": colliders, "bootstrap": boot,
                "law": "o-o partial graph summarizes stable association uncertainty; it is not an FCI PAG, CPDAG theorem, or causal orientation proof"}

    def evidence_dependence_probability(self, claim_id: str, coefficients: Mapping[str, Any] | None = None,
                                        dimensions: Sequence[str] | None = None, min_confidence: float = .5) -> dict[str, Any]:
        dims = list(dimensions or ["dataset", "implementation", "method", "operator", "environment", "seed_family"])
        co = dict(coefficients or {}); bias = float(co.get("bias", -0.5)); default_match = float(co.get("match", 1.0)); default_missing = float(co.get("missing", 0.25))
        rows = self.s.rows("SELECT * FROM collective_v6_claim_witnesses WHERE claim_id=? AND confidence>=? ORDER BY created_at", (str(claim_id), float(min_confidence)))
        ws = []
        for r in rows:
            try: ev = json.loads(r["evidence_json"])
            except Exception: ev = {}
            ws.append({"id": r["witness_id"], "confidence": float(r["confidence"]), "independence_key": r["independence_key"], "evidence": ev})
        pairs = []
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                if ws[i]["independence_key"] and ws[i]["independence_key"] == ws[j]["independence_key"]:
                    p = 1.0; shared = ["independence_key"]
                else:
                    z = bias; shared = []
                    for d in dims:
                        vi = ws[i]["evidence"].get(d); vj = ws[j]["evidence"].get(d)
                        if vi is None or vj is None:
                            z += float(co.get(f"missing:{d}", default_missing)); continue
                        if vi == vj:
                            shared.append(d); z += float(co.get(f"match:{d}", default_match))
                        else:
                            z += float(co.get(f"different:{d}", -0.5))
                    p = _sigmoid(z)
                pairs.append({"a": ws[i]["id"], "b": ws[j]["id"], "p_dependence": round(p, 8), "shared": shared})
        mean_dep = _mean([p["p_dependence"] for p in pairs]) if pairs else 1.0
        return {"status": "DECLARED_METADATA_DEPENDENCE_MODEL", "claim_id": str(claim_id), "witness_count": len(ws), "pairwise": pairs, "mean_pair_dependence": round(mean_dep, 8), "coefficients": {"bias": bias, **co},
                "law": "dependence probabilities are conditional on the caller-declared metadata model; they are not empirically identified formal independence probabilities"}
