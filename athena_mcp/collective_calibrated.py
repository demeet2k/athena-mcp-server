from __future__ import annotations

import math
import random
import statistics
from statistics import NormalDist
from typing import Any, Mapping, Sequence

from .collective_probabilistic import _fit_logistic, _mean, _predict_logistic
from .collective_robust import _cov_psd, _policy_action


def _binary(value: Any, label: str) -> int:
    x = float(value)
    if x not in (0.0, 1.0):
        raise ValueError(f"{label} must be binary")
    return int(x)


def _std_error(values: Sequence[float]) -> float:
    return statistics.stdev([float(x) for x in values]) / math.sqrt(len(values)) if len(values) > 1 else 0.0


def _fold_assignment(n: int, folds: int, seed: int) -> list[int]:
    k = max(2, min(int(folds), min(10, n)))
    order = list(range(n))
    random.Random(int(seed)).shuffle(order)
    out = [0] * n
    for pos, idx in enumerate(order):
        out[idx] = pos % k
    return out


def _isotonic_blocks(examples: Sequence[Mapping[str, Any]]) -> list[dict[str, float]]:
    rows = []
    for row in examples:
        support = float(row["support"])
        if not 0.0 <= support <= 1.0:
            raise ValueError("structural support must lie in [0,1]")
        correct = _binary(row["correct"], "correct")
        weight = float(row.get("weight", 1.0))
        if weight <= 0:
            raise ValueError("calibration weights must be positive")
        rows.append({"support": support, "correct": float(correct), "weight": weight})
    if len(rows) < 8:
        raise ValueError("structural calibration requires at least eight examples")
    rows.sort(key=lambda r: (r["support"], r["correct"]))
    blocks = []
    for row in rows:
        block = {"x_min": row["support"], "x_max": row["support"], "weight": row["weight"], "success": row["weight"] * row["correct"]}
        blocks.append(block)
        while len(blocks) >= 2:
            a, b = blocks[-2], blocks[-1]
            pa = a["success"] / a["weight"]
            pb = b["success"] / b["weight"]
            if pa <= pb + 1e-15:
                break
            blocks[-2:] = [{
                "x_min": a["x_min"],
                "x_max": b["x_max"],
                "weight": a["weight"] + b["weight"],
                "success": a["success"] + b["success"],
            }]
    return [{
        "x_min": float(b["x_min"]),
        "x_max": float(b["x_max"]),
        "probability": float(b["success"] / b["weight"]),
        "weight": float(b["weight"]),
    } for b in blocks]


def _isotonic_predict(blocks: Sequence[Mapping[str, Any]], support: float) -> float:
    x = max(0.0, min(1.0, float(support)))
    if not blocks:
        raise ValueError("calibration curve is empty")
    best = blocks[-1]
    for block in blocks:
        best = block
        if x <= float(block["x_max"]) + 1e-15:
            break
    return max(0.0, min(1.0, float(best["probability"])))


def _mat_vec(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    return [sum(float(row[j]) * float(vector[j]) for j in range(len(vector))) for row in matrix]


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def _gaussian_validate(variables: Sequence[str], mean: Sequence[float], covariance: Sequence[Sequence[float]]) -> tuple[list[str], list[float], list[list[float]]]:
    names = [str(x) for x in variables]
    if not 1 <= len(names) <= 16 or len(set(names)) != len(names):
        raise ValueError("continuous joint Gaussian belief requires 1..16 unique variables")
    mu = [float(x) for x in mean]
    if len(mu) != len(names):
        raise ValueError("mean length must match variables")
    cov = [[float(v) for v in row] for row in covariance]
    n = len(names)
    if len(cov) != n or any(len(row) != n for row in cov):
        raise ValueError("covariance must be square and match variables")
    for i in range(n):
        if cov[i][i] < 0:
            raise ValueError("covariance diagonal must be non-negative")
        for j in range(n):
            if abs(cov[i][j] - cov[j][i]) > 1e-8:
                raise ValueError("covariance must be symmetric")
    if not _cov_psd(cov):
        raise ValueError("covariance must be positive semidefinite")
    return names, mu, cov


def _normal_lower_cvar(mu: float, sigma: float, alpha: float) -> float:
    a = max(1e-6, min(0.5, float(alpha)))
    if sigma <= 1e-15:
        return float(mu)
    z = NormalDist().inv_cdf(a)
    phi = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    return float(mu) - float(sigma) * phi / a


def _tv_worst_expectation(probabilities: Sequence[float], values: Sequence[float], radius: float) -> tuple[float, list[float]]:
    if len(probabilities) != len(values) or not probabilities:
        raise ValueError("transition probabilities and values must align")
    p = [float(x) for x in probabilities]
    if any(x < -1e-12 for x in p) or abs(sum(p) - 1.0) > 1e-8:
        raise ValueError("transition probabilities must be non-negative and sum to one")
    q = [max(0.0, x) for x in p]
    budget = max(0.0, min(1.0, float(radius)))
    lows = sorted(range(len(values)), key=lambda i: (float(values[i]), i))
    highs = sorted(range(len(values)), key=lambda i: (float(values[i]), i), reverse=True)
    li = hi = 0
    while budget > 1e-15 and li < len(lows) and hi < len(highs):
        lo, high = lows[li], highs[hi]
        if float(values[high]) <= float(values[lo]) + 1e-15:
            break
        if lo == high:
            if q[lo] >= 1.0 - 1e-15:
                li += 1
            else:
                hi += 1
            continue
        receive = 1.0 - q[lo]
        donate = q[high]
        move = min(receive, donate, budget)
        if move <= 1e-15:
            if receive <= 1e-15:
                li += 1
            if donate <= 1e-15:
                hi += 1
            continue
        q[lo] += move
        q[high] -= move
        budget -= move
        if q[lo] >= 1.0 - 1e-15:
            li += 1
        if q[high] <= 1e-15:
            hi += 1
    return _dot(q, values), q


class CollectiveCalibratedRuntime:
    """V15 bounded calibration, cross-fitting, continuous-belief and multistage robust-control layer."""

    def __init__(self, synthesis):
        self.synthesis = synthesis
        self.robust = synthesis.robust
        self.probabilistic = synthesis.probabilistic
        self.s = synthesis.s

    def describe(self) -> dict[str, Any]:
        return {
            "version": "COLLECTIVE_RUNTIME_V15",
            "persistent_surfaces": {},
            "operators": [
                "structural_reliability_calibrate",
                "longitudinal_tmle_crossfit",
                "sequential_dr_policy_crossfit",
                "joint_gaussian_update",
                "joint_gaussian_control",
                "approx_error_transport",
                "multistage_tv_dro_plan",
            ],
            "coordinate": "COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>",
            "laws": [
                "OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR",
                "CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM",
                "CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE",
                "LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES",
                "GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP",
                "DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH",
                "RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO",
            ],
        }

    def structural_reliability_calibrate(self, calibration_examples: Sequence[Mapping[str, Any]], supports: Sequence[float] | None = None, folds: int = 5, seed: int = 0) -> dict[str, Any]:
        rows = [dict(x) for x in calibration_examples]
        if len(rows) < 40:
            raise ValueError("structural reliability calibration requires at least forty labelled examples")
        assignment = _fold_assignment(len(rows), max(2, min(int(folds), 10)), seed)
        k = max(assignment) + 1
        oof = [None] * len(rows)
        for fold in range(k):
            train = [rows[i] for i in range(len(rows)) if assignment[i] != fold]
            curve = _isotonic_blocks(train)
            for i in range(len(rows)):
                if assignment[i] == fold:
                    oof[i] = _isotonic_predict(curve, float(rows[i]["support"]))
        labels = [float(_binary(row["correct"], "correct")) for row in rows]
        raw = [max(0.0, min(1.0, float(row["support"]))) for row in rows]
        brier_raw = _mean([(p - y) ** 2 for p, y in zip(raw, labels)])
        brier_oof = _mean([(float(p) - y) ** 2 for p, y in zip(oof, labels)])
        final_curve = _isotonic_blocks(rows)
        targets = []
        for value in supports or []:
            x = float(value)
            if not 0.0 <= x <= 1.0:
                raise ValueError("supports to calibrate must lie in [0,1]")
            targets.append({"support": x, "calibrated_reliability": round(_isotonic_predict(final_curve, x), 10)})
        return {
            "status": "OUT_OF_FOLD_ISOTONIC_STRUCTURAL_RELIABILITY",
            "n": len(rows),
            "folds": k,
            "brier_raw": round(brier_raw, 10),
            "brier_oof_calibrated": round(brier_oof, 10),
            "oof_improvement": round(brier_raw - brier_oof, 10),
            "curve": [{
                "support_min": round(float(b["x_min"]), 10),
                "support_max": round(float(b["x_max"]), 10),
                "calibrated_reliability": round(float(b["probability"]), 10),
                "weight": round(float(b["weight"]), 10),
            } for b in final_curve],
            "calibrated_supports": targets,
            "law": "out-of-fold isotonic mapping calibrates empirical correctness frequency against externally labelled structural examples; it does not convert bootstrap support into a causal graph posterior, identify hidden confounding, or authorize JSPACE mutation",
        }

    def _longitudinal_rows(self, samples: Sequence[Mapping[str, Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, baseline: Sequence[str] | None) -> tuple[list[str], list[dict[str, float]]]:
        base = [str(x) for x in (baseline or [])]
        rows = []
        for src in samples:
            row = {k: float(src[k]) for k in base}
            row["A1"] = _binary(src[treatment1], treatment1)
            row["L1"] = _binary(src[intermediate], intermediate)
            row["A2"] = _binary(src[treatment2], treatment2)
            row["Y"] = _binary(src[outcome], outcome)
            rows.append(row)
        return base, rows

    def longitudinal_tmle_crossfit(self, samples: Sequence[Mapping[str, Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, baseline: Sequence[str] | None = None, regimes: Sequence[Mapping[str, Any]] | None = None, assumptions: Mapping[str, Any] | None = None, propensity_clip: float = 0.05, folds: int = 2, seed: int = 0) -> dict[str, Any]:
        if len(samples) < 160:
            raise ValueError("cross-fitted two-timepoint TMLE requires at least one hundred sixty samples")
        assumptions = dict(assumptions or {})
        if assumptions.get("latent_confounding_possible") is True:
            return {"status": "UNIDENTIFIED_LATENT_CONFOUNDING_RISK", "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE", "assumptions": assumptions, "law": "declared latent confounding fails closed before estimation"}
        base, rows = self._longitudinal_rows(samples, treatment1, intermediate, treatment2, outcome, baseline)
        regs = list(regimes or [{"id": "00", "a1": 0, "a2": 0}, {"id": "01", "a1": 0, "a2": 1}, {"id": "10", "a1": 1, "a2": 0}, {"id": "11", "a1": 1, "a2": 1}])
        if not regs or len(regs) > 16:
            raise ValueError("regimes must contain 1..16 static treatment plans")
        clip = max(0.01, min(0.25, float(propensity_clip)))
        assignment = _fold_assignment(len(rows), folds, seed)
        k = max(assignment) + 1
        from .collective_robust import _fluctuation_epsilon
        from .collective_probabilistic import _logit, _sigmoid
        results = []
        for ri, reg in enumerate(regs):
            a1 = _binary(reg.get("a1"), "regime a1")
            a2 = _binary(reg.get("a2"), "regime a2")
            heldout_values = [None] * len(rows)
            fold_estimates = []
            for fold in range(k):
                train = [rows[i] for i in range(len(rows)) if assignment[i] != fold]
                test_idx = [i for i in range(len(rows)) if assignment[i] == fold]
                if len(train) < 80 or not test_idx:
                    raise ValueError("cross-fitting fold too small")
                g1 = _fit_logistic(train, "A1", base)
                g2 = _fit_logistic(train, "A2", base + ["A1", "L1"])
                q2 = _fit_logistic(train, "Y", base + ["A1", "L1", "A2"])
                ys, offsets, h2 = [], [], []
                for r in train:
                    p1 = _predict_logistic(g1, r, base); g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                    p2 = _predict_logistic(g2, r, base + ["A1", "L1"]); g2a = max(clip, min(1 - clip, p2 if a2 == 1 else 1 - p2))
                    qobs = max(1e-7, min(1 - 1e-7, _predict_logistic(q2, r, base + ["A1", "L1", "A2"])))
                    ys.append(r["Y"]); offsets.append(_logit(qobs)); h2.append((1.0 if r["A1"] == a1 and r["A2"] == a2 else 0.0) / (g1a * g2a))
                eps2 = _fluctuation_epsilon(ys, offsets, h2)
                pseudo, q2_target_train = [], []
                for r in train:
                    cf = {**{x: r[x] for x in base}, "A1": a1, "L1": r["L1"], "A2": a2}
                    p1 = _predict_logistic(g1, cf, base); g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                    p2 = _predict_logistic(g2, cf, base + ["A1", "L1"]); g2a = max(clip, min(1 - clip, p2 if a2 == 1 else 1 - p2))
                    q = max(1e-7, min(1 - 1e-7, _predict_logistic(q2, cf, base + ["A1", "L1", "A2"])))
                    qt = _sigmoid(_logit(q) + eps2 / (g1a * g2a))
                    q2_target_train.append(qt); pseudo.append({**{x: r[x] for x in base}, "A1": r["A1"], "Q": qt})
                q1 = _fit_logistic(pseudo, "Q", base + ["A1"])
                off1, h1 = [], []
                for r in train:
                    p1 = _predict_logistic(g1, r, base); g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                    q = max(1e-7, min(1 - 1e-7, _predict_logistic(q1, {**{x: r[x] for x in base}, "A1": r["A1"]}, base + ["A1"])))
                    off1.append(_logit(q)); h1.append((1.0 if r["A1"] == a1 else 0.0) / g1a)
                eps1 = _fluctuation_epsilon(q2_target_train, off1, h1)
                fold_values = []
                for i in test_idx:
                    r = rows[i]; cf = {**{x: r[x] for x in base}, "A1": a1}
                    p1 = _predict_logistic(g1, cf, base); g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                    q = max(1e-7, min(1 - 1e-7, _predict_logistic(q1, cf, base + ["A1"])))
                    value = _sigmoid(_logit(q) + eps1 / g1a)
                    heldout_values[i] = value; fold_values.append(value)
                fold_estimates.append(_mean(fold_values))
            vals = [float(x) for x in heldout_values]
            results.append({"id": str(reg.get("id", f"R{ri}")), "a1": a1, "a2": a2, "estimated_risk": round(_mean(vals), 10), "standard_error_proxy": round(_std_error(vals), 10), "fold_estimates": [round(x, 10) for x in fold_estimates]})
        results.sort(key=lambda r: (r["estimated_risk"], r["id"]), reverse=True)
        return {"status": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_UNDER_ASSUMPTIONS", "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE", "n": len(rows), "folds": k, "cross_fitted": True, "baseline": base, "regimes": results, "highest_risk_regime": results[0]["id"], "lowest_risk_regime": results[-1]["id"], "risk_contrast": round(results[0]["estimated_risk"] - results[-1]["estimated_risk"], 10), "propensity_clip": clip, "assumptions": assumptions, "law": "nuisance and targeting models are trained without each held-out evaluation fold and predictions are aggregated across folds; this remains a bounded two-timepoint sequential logistic TMLE construction, and its standard_error_proxy is not an asymptotic efficient-influence-curve theorem"}

    def sequential_dr_policy_crossfit(self, samples: Sequence[Mapping[str, Any]], treatment1: str, intermediate: str, treatment2: str, outcome: str, policies: Sequence[Mapping[str, Any]], baseline: Sequence[str] | None = None, assumptions: Mapping[str, Any] | None = None, propensity_clip: float = 0.05, folds: int = 2, seed: int = 0) -> dict[str, Any]:
        if len(samples) < 180:
            raise ValueError("cross-fitted sequential DR policy value requires at least one hundred eighty samples")
        if not policies or len(policies) > 32:
            raise ValueError("policies must contain 1..32 dynamic policies")
        assumptions = dict(assumptions or {})
        if assumptions.get("latent_confounding_possible") is True:
            return {"status": "UNIDENTIFIED_LATENT_CONFOUNDING_RISK", "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW", "assumptions": assumptions, "law": "declared latent confounding fails closed before policy valuation"}
        base, rows = self._longitudinal_rows(samples, treatment1, intermediate, treatment2, outcome, baseline)
        clip = max(0.01, min(0.25, float(propensity_clip)))
        assignment = _fold_assignment(len(rows), folds, seed); k = max(assignment) + 1; out = []
        for pi, policy in enumerate(policies):
            pid = str(policy.get("id", f"P{pi}"))
            if "a1" not in policy or "a2" not in policy:
                raise ValueError("each dynamic policy requires a1 and a2")
            psi_all = [None] * len(rows)
            for fold in range(k):
                train = [rows[i] for i in range(len(rows)) if assignment[i] != fold]; test_idx = [i for i in range(len(rows)) if assignment[i] == fold]
                if len(train) < 90 or not test_idx:
                    raise ValueError("cross-fitting fold too small")
                g1 = _fit_logistic(train, "A1", base); g2 = _fit_logistic(train, "A2", base + ["A1", "L1"]); q2 = _fit_logistic(train, "Y", base + ["A1", "L1", "A2"])
                pseudo = []
                for r in train:
                    a2pi = _policy_action(policy["a2"], r, "a2"); cf2 = {**r, "A2": a2pi}; q2pi = max(0.0, min(1.0, _predict_logistic(q2, cf2, base + ["A1", "L1", "A2"])))
                    pseudo.append({**{x: r[x] for x in base}, "A1": r["A1"], "Q": q2pi})
                q1 = _fit_logistic(pseudo, "Q", base + ["A1"])
                for i in test_idx:
                    r = rows[i]; a1pi = _policy_action(policy["a1"], r, "a1"); a2pi = _policy_action(policy["a2"], r, "a2")
                    p1 = _predict_logistic(g1, r, base); g1obs = max(clip, min(1 - clip, p1 if r["A1"] == 1 else 1 - p1))
                    p2 = _predict_logistic(g2, r, base + ["A1", "L1"]); g2obs = max(clip, min(1 - clip, p2 if r["A2"] == 1 else 1 - p2))
                    q2obs = _predict_logistic(q2, r, base + ["A1", "L1", "A2"]); q2pi = _predict_logistic(q2, {**r, "A2": a2pi}, base + ["A1", "L1", "A2"])
                    q1obs = _predict_logistic(q1, {**{x: r[x] for x in base}, "A1": r["A1"]}, base + ["A1"]); q1pi = _predict_logistic(q1, {**{x: r[x] for x in base}, "A1": a1pi}, base + ["A1"])
                    h1 = (1.0 if r["A1"] == a1pi else 0.0) / g1obs; h2 = (1.0 if r["A1"] == a1pi and r["A2"] == a2pi else 0.0) / (g1obs * g2obs)
                    psi_all[i] = q1pi + h1 * (q2pi - q1obs) + h2 * (r["Y"] - q2obs)
            vals = [float(x) for x in psi_all]; estimate = _mean(vals); se = _std_error(vals)
            out.append({"id": pid, "estimated_value": round(estimate, 10), "standard_error": round(se, 10), "interval95": [round(estimate - 1.96 * se, 10), round(estimate + 1.96 * se, 10)]})
        out.sort(key=lambda x: (x["estimated_value"], x["id"]), reverse=True)
        return {"status": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS", "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW", "n": len(rows), "folds": k, "cross_fitted": True, "policies": out, "winner": out[0]["id"], "assumptions": assumptions, "propensity_clip": clip, "history_invariant": "STAGE2_POLICY_EVALUATION_USES_OBSERVED_A1_L1_BEFORE_STAGE1_POLICY_ACTION", "law": "out-of-fold nuisance predictions feed a bounded two-timepoint sequential AIPW score; cross-fitting reduces same-sample nuisance/evaluation coupling but does not remove sequential exchangeability, positivity, consistency/interference, temporal correctness, or general off-policy identification requirements"}

    def joint_gaussian_update(self, variables: Sequence[str], mean: Sequence[float], covariance: Sequence[Sequence[float]], observation: Mapping[str, Any]) -> dict[str, Any]:
        names, mu, cov = _gaussian_validate(variables, mean, covariance)
        coeffs = observation.get("coefficients") or {}
        if not isinstance(coeffs, Mapping) or not coeffs:
            raise ValueError("linear Gaussian observation requires coefficients")
        h = [float(coeffs.get(name, 0.0)) for name in names]
        if all(abs(x) <= 1e-15 for x in h):
            raise ValueError("observation coefficients cannot all be zero")
        value = float(observation["value"]); noise = float(observation.get("noise_variance", 0.0))
        if noise <= 0:
            raise ValueError("observation noise_variance must be positive")
        sigma_h = _mat_vec(cov, h); innovation_variance = _dot(h, sigma_h) + noise
        if innovation_variance <= 1e-15:
            raise ValueError("linear Gaussian innovation variance is degenerate")
        predicted = _dot(h, mu); innovation = value - predicted; gain = [x / innovation_variance for x in sigma_h]
        post_mu = [mu[i] + gain[i] * innovation for i in range(len(names))]
        post_cov = [[cov[i][j] - gain[i] * sigma_h[j] for j in range(len(names))] for i in range(len(names))]
        for i in range(len(names)):
            for j in range(i):
                avg = 0.5 * (post_cov[i][j] + post_cov[j][i]); post_cov[i][j] = post_cov[j][i] = avg
        if not _cov_psd(post_cov, tol=1e-7):
            raise ValueError("posterior covariance became non-PSD")
        return {"status": "EXACT_LINEAR_GAUSSIAN_JOINT_UPDATE", "variables": names, "prior_mean": [round(x, 12) for x in mu], "prior_covariance": [[round(x, 12) for x in row] for row in cov], "predicted_observation": round(predicted, 12), "innovation": round(innovation, 12), "innovation_variance": round(innovation_variance, 12), "kalman_gain": [round(x, 12) for x in gain], "posterior_mean": [round(x, 12) for x in post_mu], "posterior_covariance": [[round(x, 12) for x in row] for row in post_cov], "law": "this is the exact posterior update only for the declared finite-dimensional multivariate Gaussian state and linear Gaussian observation model; it is not general continuous joint Bayes or canonical truth"}

    def joint_gaussian_control(self, variables: Sequence[str], mean: Sequence[float], covariance: Sequence[Sequence[float]], actions: Sequence[Mapping[str, Any]], cvar_alpha: float = 0.1, risk_weight: float = 1.0, cost_weight: float = 1.0) -> dict[str, Any]:
        names, mu, cov = _gaussian_validate(variables, mean, covariance)
        if not actions or len(actions) > 64:
            raise ValueError("Gaussian control supports 1..64 linear actions")
        alpha = max(1e-4, min(0.5, float(cvar_alpha))); ranked = []
        for index, action in enumerate(actions):
            aid = str(action.get("id", f"A{index}")); coeffs = action.get("coefficients") or {}
            if not isinstance(coeffs, Mapping):
                raise ValueError("action coefficients must be an object")
            q = [float(coeffs.get(name, 0.0)) for name in names]; offset = float(action.get("offset", 0.0)); expected = offset + _dot(q, mu)
            sigma2 = max(0.0, _dot(q, _mat_vec(cov, q))); sigma = math.sqrt(sigma2); lower = _normal_lower_cvar(expected, sigma, alpha); cost = max(0.0, float(action.get("cost", 0.0)))
            score = expected + max(0.0, float(risk_weight)) * lower - max(0.0, float(cost_weight)) * cost
            ranked.append({"id": aid, "expected_utility": round(expected, 10), "utility_std": round(sigma, 10), "lower_cvar": round(lower, 10), "cost": round(cost, 10), "score": round(score, 10)})
        pareto = []
        for row in ranked:
            dominated = False
            for other in ranked:
                if other is row:
                    continue
                weak = other["expected_utility"] >= row["expected_utility"] - 1e-12 and other["lower_cvar"] >= row["lower_cvar"] - 1e-12 and other["cost"] <= row["cost"] + 1e-12
                strict = other["expected_utility"] > row["expected_utility"] + 1e-12 or other["lower_cvar"] > row["lower_cvar"] + 1e-12 or other["cost"] < row["cost"] - 1e-12
                if weak and strict:
                    dominated = True; break
            if not dominated:
                pareto.append(row["id"])
        ranked.sort(key=lambda r: (r["score"], r["id"]), reverse=True)
        return {"decision": "GAUSSIAN_LINEAR_JOINT_CONTROL_PLAN_ONLY", "winner": ranked[0]["id"], "cvar_alpha": alpha, "pareto_frontier": pareto, "ranked": ranked, "law": "linear action utilities are propagated exactly through the declared multivariate Gaussian belief and lower-tail Normal CVaR; this is not a general continuous-state belief MDP, robust-control theorem, execution authorization, or observation"}

    def approx_error_transport(self, feature_order: Sequence[str], witnesses: Sequence[Mapping[str, Any]], queries: Sequence[Mapping[str, Any]], lipschitz_bound: float, max_transport_radius: float | None = None, margin_safety: float = 0.5) -> dict[str, Any]:
        order = [str(x) for x in feature_order]
        if not order or len(order) > 32 or len(set(order)) != len(order):
            raise ValueError("feature_order requires 1..32 unique names")
        if len(witnesses) < 2 or len(witnesses) > 4096:
            raise ValueError("approximation transport requires 2..4096 witnesses")
        L = float(lipschitz_bound)
        if L < 0:
            raise ValueError("lipschitz_bound must be non-negative")
        points = []
        for w in witnesses:
            feats = w.get("features") or {}
            if any(name not in feats for name in order):
                raise ValueError("every approximation witness requires every feature")
            error = float(w["absolute_error"])
            if error < 0:
                raise ValueError("witness absolute_error must be non-negative")
            points.append(([float(feats[name]) for name in order], error))
        empirical = 0.0
        for i in range(len(points)):
            for j in range(i):
                d = math.sqrt(sum((points[i][0][k] - points[j][0][k]) ** 2 for k in range(len(order)))); de = abs(points[i][1] - points[j][1])
                if d <= 1e-15:
                    if de > 1e-10:
                        raise ValueError("duplicate approximation witness coordinate has inconsistent error")
                    continue
                empirical = max(empirical, de / d)
        if L + 1e-10 < empirical:
            raise ValueError("declared lipschitz_bound is contradicted by supplied witnesses")
        radius = None if max_transport_radius is None else max(0.0, float(max_transport_radius)); safety = max(0.0, min(1.0, float(margin_safety))); transported = []
        for qi, query in enumerate(queries):
            feats = query.get("features") or {}
            if any(name not in feats for name in order):
                raise ValueError("every approximation query requires every feature")
            x = [float(feats[name]) for name in order]; candidates = []
            for wi, (wx, error) in enumerate(points):
                d = math.sqrt(sum((x[k] - wx[k]) ** 2 for k in range(len(order)))); candidates.append((error + L * d, d, wi))
            upper, nearest, witness_index = min(candidates); in_radius = radius is None or nearest <= radius + 1e-15; decision_margin = query.get("decision_margin"); preserving = None
            if decision_margin is not None:
                dm = float(decision_margin)
                if dm < 0:
                    raise ValueError("decision_margin must be non-negative")
                preserving = bool(in_radius and upper <= safety * dm + 1e-15)
            transported.append({"id": str(query.get("id", f"Q{qi}")), "transported_error_upper_bound": round(upper, 10), "nearest_witness_distance": round(nearest, 10), "nearest_witness_index": witness_index, "within_transport_radius": in_radius, "decision_margin": None if decision_margin is None else round(float(decision_margin), 10), "decision_preserving_under_bound": preserving})
        return {"status": "DECLARED_LIPSCHITZ_APPROXIMATION_ERROR_TRANSPORT", "feature_order": order, "declared_lipschitz_bound": round(L, 10), "empirical_minimum_lipschitz": round(empirical, 10), "max_transport_radius": radius, "margin_safety": safety, "queries": transported, "law": "transported error is a mathematical envelope conditional on the declared Lipschitz assumption and supplied witness coordinates; witness consistency does not prove the bound outside the observed domain, and a local transport certificate is not empirical global approximation truth"}

    def multistage_tv_dro_plan(self, states: Sequence[str], initial_state: str, actions_by_state: Mapping[str, Any], horizon: int, tv_radius: float, discount: float = 1.0) -> dict[str, Any]:
        names = [str(x) for x in states]
        if not 1 <= len(names) <= 24 or len(set(names)) != len(names):
            raise ValueError("multistage TV-DRO requires 1..24 unique states")
        initial = str(initial_state)
        if initial not in names:
            raise ValueError("initial_state must be in states")
        H = int(horizon)
        if not 1 <= H <= 8:
            raise ValueError("horizon must lie in 1..8")
        rho = float(tv_radius)
        if not 0.0 <= rho <= 1.0:
            raise ValueError("tv_radius must lie in [0,1]")
        gamma = float(discount)
        if not 0.0 <= gamma <= 1.0:
            raise ValueError("discount must lie in [0,1]")
        if not isinstance(actions_by_state, Mapping):
            raise ValueError("actions_by_state must be an object")
        parsed = {}
        for state in names:
            actions = actions_by_state.get(state)
            if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)) or not actions or len(actions) > 16:
                raise ValueError(f"state {state} requires 1..16 actions")
            rows = []
            for ai, action in enumerate(actions):
                if not isinstance(action, Mapping):
                    raise ValueError("action rows must be objects")
                aid = str(action.get("id", f"{state}.A{ai}")); transition = action.get("transitions") or {}
                if not isinstance(transition, Mapping) or any(str(k) not in names for k in transition):
                    raise ValueError("action transitions must reference known states")
                probs = [float(transition.get(s, 0.0)) for s in names]
                if any(p < -1e-12 for p in probs) or abs(sum(probs) - 1.0) > 1e-8:
                    raise ValueError("each action transition distribution must sum to one")
                rows.append({"id": aid, "reward": float(action.get("reward", 0.0)), "probabilities": probs})
            parsed[state] = rows
        robust_next = {s: 0.0 for s in names}; nominal_next = {s: 0.0 for s in names}; policy = {}; stage_values = {}
        for stage in range(H - 1, -1, -1):
            robust_now = {}; nominal_now = {}; policy_stage = {}; detail_stage = {}; next_robust_values = [robust_next[s] for s in names]; next_nominal_values = [nominal_next[s] for s in names]
            for state in names:
                candidates = []
                for action in parsed[state]:
                    worst_cont, worst_q = _tv_worst_expectation(action["probabilities"], next_robust_values, rho); nominal_cont = _dot(action["probabilities"], next_nominal_values)
                    robust_q = action["reward"] + gamma * worst_cont; nominal_q = action["reward"] + gamma * nominal_cont
                    candidates.append({"id": action["id"], "robust_value": robust_q, "nominal_value": nominal_q, "worst_case_transition": worst_q})
                best = max(candidates, key=lambda x: (x["robust_value"], x["nominal_value"], x["id"])); robust_now[state] = best["robust_value"]; nominal_now[state] = best["nominal_value"]; policy_stage[state] = best["id"]
                detail_stage[state] = [{"id": c["id"], "robust_value": round(c["robust_value"], 10), "nominal_value": round(c["nominal_value"], 10), "worst_case_transition": [round(x, 10) for x in c["worst_case_transition"]]} for c in candidates]
            policy[str(stage)] = policy_stage; stage_values[str(stage)] = detail_stage; robust_next, nominal_next = robust_now, nominal_now
        return {"status": "FINITE_HORIZON_RECTANGULAR_TV_DRO_DYNAMIC_PROGRAM_CERTIFIED", "certificate": "EXACT_DYNAMIC_PROGRAM_FOR_SUPPLIED_FINITE_RECTANGULAR_TV_AMBIGUITY_MODEL", "states": names, "initial_state": initial, "horizon": H, "tv_radius": rho, "discount": gamma, "robust_initial_value": round(robust_next[initial], 10), "nominal_value_of_robust_policy_proxy": round(nominal_next[initial], 10), "policy": policy, "stage_action_values": stage_values, "law": "backward induction exactly solves the supplied finite-horizon state/action model under state-action rectangular total-variation ambiguity sets; this is not general multistage DRO, non-rectangular ambiguity, continuous-state control, real-world safety, or execution authority"}
