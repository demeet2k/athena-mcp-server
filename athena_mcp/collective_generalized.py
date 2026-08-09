from __future__ import annotations

import itertools
import math
import random
import statistics
from typing import Any, Mapping, Sequence

from .collective_discovery import _inverse
from .collective_probabilistic import _fit_logistic, _predict_logistic
from .collective_v15_calibration import _isotonic_blocks, _isotonic_predict
from .collective_v15_history import policy_action_from_history


def _finite(value: Any, label: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{label} must be finite")
    return x


def _binary(value: Any, label: str) -> int:
    x = _finite(value, label)
    if x not in (0.0, 1.0):
        raise ValueError(f"{label} must be binary")
    return int(x)


def _mean(values: Sequence[float]) -> float:
    return sum(float(x) for x in values) / len(values)


def _std_error(values: Sequence[float]) -> float:
    return statistics.stdev([float(x) for x in values]) / math.sqrt(len(values)) if len(values) > 1 else 0.0


def _fold_assignment(n: int, folds: int, seed: int) -> list[int]:
    k = max(2, min(int(folds), min(10, n)))
    order = list(range(n)); random.Random(int(seed)).shuffle(order)
    out = [0] * n
    for pos, idx in enumerate(order): out[idx] = pos % k
    return out


def _fit_linear(rows: Sequence[Mapping[str, float]], targets: Sequence[float], features: Sequence[str], ridge: float = 1e-6) -> list[float]:
    if len(rows) != len(targets) or not rows:
        raise ValueError("linear fit rows and targets must align")
    names = [str(x) for x in features]
    p = len(names) + 1
    xtx = [[0.0] * p for _ in range(p)]; xty = [0.0] * p
    for row, target in zip(rows, targets):
        x = [1.0] + [_finite(row[name], f"feature {name}") for name in names]
        y = _finite(target, "linear target")
        for i in range(p):
            xty[i] += x[i] * y
            for j in range(p): xtx[i][j] += x[i] * x[j]
    lam = max(1e-12, _finite(ridge, "ridge"))
    for i in range(1, p): xtx[i][i] += lam
    inv = _inverse(xtx)
    return [sum(inv[i][j] * xty[j] for j in range(p)) for i in range(p)]


def _predict_linear(beta: Sequence[float], row: Mapping[str, float], features: Sequence[str], clip: bool = False) -> float:
    value = float(beta[0]) + sum(float(beta[j + 1]) * _finite(row[str(name)], f"feature {name}") for j, name in enumerate(features))
    if clip: value = max(0.0, min(1.0, value))
    return value


def _gaussian_local_bic(samples: Sequence[Mapping[str, float]], child: str, parents: Sequence[str]) -> float:
    rows = [{str(k): _finite(v, str(k)) for k, v in row.items()} for row in samples]
    y = [row[child] for row in rows]
    if parents:
        beta = _fit_linear(rows, y, parents, 1e-8)
        pred = [_predict_linear(beta, row, parents) for row in rows]
    else:
        mu = _mean(y); pred = [mu] * len(y)
    rss = max(1e-12, sum((a - b) ** 2 for a, b in zip(y, pred)))
    n = len(y); parameter_count = len(parents) + 2  # intercept/slopes + residual variance
    return n * math.log(rss / n) + parameter_count * math.log(n)


def _softmax_logs(log_weights: Sequence[float]) -> list[float]:
    m = max(log_weights); raw = [math.exp(x - m) for x in log_weights]; z = sum(raw)
    return [x / z for x in raw]


def ordered_dag_posterior(
    samples: Sequence[Mapping[str, Any]],
    order: Sequence[str],
    prior_edge_probability: float = 0.25,
    top_k: int = 16,
    calibration_examples: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    if not 40 <= len(samples) <= 5000:
        raise ValueError("ordered DAG posterior requires 40..5000 rows")
    names = [str(x) for x in order]
    if not 2 <= len(names) <= 5 or len(set(names)) != len(names):
        raise ValueError("order requires 2..5 unique variables")
    p_edge = _finite(prior_edge_probability, "prior_edge_probability")
    if not 0.001 <= p_edge <= 0.999:
        raise ValueError("prior_edge_probability must lie in [0.001,0.999]")
    clean = []
    for src in samples:
        if any(name not in src for name in names): raise ValueError("every DAG row requires every ordered variable")
        clean.append({name: _finite(src[name], name) for name in names})

    local: list[list[dict[str, Any]]] = []
    for j, child in enumerate(names):
        previous = names[:j]; options = []
        for r in range(len(previous) + 1):
            for subset in itertools.combinations(previous, r):
                bic = _gaussian_local_bic(clean, child, subset)
                prior = len(subset) * math.log(p_edge) + (len(previous) - len(subset)) * math.log(1 - p_edge)
                options.append({"child": child, "parents": list(subset), "local_log_weight": -0.5 * bic + prior})
        local.append(options)

    graphs = []
    for choices in itertools.product(*local):
        edges = []
        for item in choices:
            edges.extend((parent, item["child"]) for parent in item["parents"])
        graphs.append({"edges": edges, "log_weight": sum(float(item["local_log_weight"]) for item in choices)})
    weights = _softmax_logs([g["log_weight"] for g in graphs])
    for g, w in zip(graphs, weights): g["posterior_weight"] = w

    edge_post = {(a, b): 0.0 for j, b in enumerate(names) for a in names[:j]}
    for g in graphs:
        for edge in g["edges"]: edge_post[edge] += float(g["posterior_weight"])

    curve = None
    if calibration_examples is not None:
        if len(calibration_examples) < 40:
            raise ValueError("edge reliability calibration requires at least forty externally labelled examples")
        curve = _isotonic_blocks(calibration_examples)

    edges = []
    for (a, b), raw in sorted(edge_post.items()):
        row = {"source": a, "target": b, "posterior_probability": round(raw, 12)}
        if curve is not None: row["calibrated_reliability"] = round(_isotonic_predict(curve, raw), 12)
        edges.append(row)
    ranked = sorted(graphs, key=lambda g: g["posterior_weight"], reverse=True)[:max(1, min(int(top_k), 64))]
    return {
        "status": "EXACT_ORDER_CONSTRAINED_LINEAR_GAUSSIAN_DAG_POSTERIOR",
        "order": names,
        "row_count": len(clean),
        "graph_count": len(graphs),
        "prior_edge_probability": p_edge,
        "edges": edges,
        "top_graphs": [{"edges": [[a, b] for a, b in g["edges"]], "posterior_weight": round(float(g["posterior_weight"]), 12)} for g in ranked],
        "calibrated": curve is not None,
        "law": "posterior weights are exact only for the finite DAG family consistent with the caller-declared topological order under the implemented linear-Gaussian BIC approximation and edge prior; optional external isotonic reliability calibration does not make the graph posterior causal truth, discover latent confounding, or authorize JSPACE mutation",
    }


def _validate_multistage(samples, stages, outcome):
    if not 120 <= len(samples) <= 20000: raise ValueError("multistage DR requires 120..20000 rows")
    if not 1 <= len(stages) <= 6: raise ValueError("multistage DR supports 1..6 treatment stages")
    outcome = str(outcome); treatments = [str(stage.get("treatment", "")) for stage in stages]
    if any(not x for x in treatments) or len(set(treatments)) != len(treatments) or outcome in treatments:
        raise ValueError("treatment names must be nonempty unique and distinct from outcome")
    histories = []
    for t, stage in enumerate(stages):
        history = [str(x) for x in stage.get("history", [])]
        if len(set(history)) != len(history): raise ValueError("stage history names must be unique")
        forbidden = set(treatments[t:]) | {outcome}
        overlap = sorted(set(history) & forbidden)
        if overlap: raise ValueError("stage history contains current/future treatment or outcome: " + ", ".join(overlap))
        histories.append(history)
    fields = set(treatments) | {outcome}
    for history in histories: fields.update(history)
    clean = []
    for src in samples:
        if any(field not in src for field in fields): raise ValueError("every row requires every declared multistage field")
        row = {field: _finite(src[field], field) for field in fields}
        for treatment in treatments: row[treatment] = _binary(row[treatment], treatment)
        row[outcome] = _binary(row[outcome], outcome)
        clean.append(row)
    return clean, treatments, histories, outcome


def longitudinal_dr_multistage_crossfit(samples, stages, outcome, policies, folds=2, seed=0, propensity_clip=0.05):
    clean, treatments, histories, outcome = _validate_multistage(samples, stages, outcome)
    if not 1 <= len(policies) <= 32: raise ValueError("policies requires 1..32 entries")
    ids = [str(p.get("id", "")) for p in policies]
    if any(not x for x in ids) or len(set(ids)) != len(ids): raise ValueError("policy ids must be nonempty and unique")
    clip = _finite(propensity_clip, "propensity_clip")
    if not 0.01 <= clip <= 0.25: raise ValueError("propensity_clip must lie in [0.01,0.25]")
    assignment = _fold_assignment(len(clean), folds, seed); k = max(assignment) + 1; T = len(stages)
    output = []
    for policy in policies:
        actions = list(policy.get("actions") or [])
        if len(actions) != T: raise ValueError("each policy requires one action specification per stage")
        for t in range(T): policy_action_from_history(actions[t], clean[0], f"stage {t} action", histories[t])
        scores: list[float | None] = [None] * len(clean)
        for fold in range(k):
            train = [clean[i] for i in range(len(clean)) if assignment[i] != fold]
            test_idx = [i for i in range(len(clean)) if assignment[i] == fold]
            if len(train) < max(60, 10 * T) or not test_idx: raise ValueError("cross-fitting fold too small")
            g_models = [_fit_logistic(train, treatments[t], histories[t]) for t in range(T)]
            q_models: list[tuple[list[float], list[str]]] = [None] * T  # type: ignore
            pseudo = [row[outcome] for row in train]
            for t in range(T - 1, -1, -1):
                features = histories[t] + [treatments[t]]
                beta = _fit_linear(train, pseudo, features)
                q_models[t] = (beta, features)
                next_pseudo = []
                for row in train:
                    action = policy_action_from_history(actions[t], row, f"stage {t} action", histories[t])
                    cf = dict(row); cf[treatments[t]] = action
                    next_pseudo.append(_predict_linear(beta, cf, features, clip=True))
                pseudo = next_pseudo
            for i in test_idx:
                row = clean[i]; chosen = [policy_action_from_history(actions[t], row, f"stage {t} action", histories[t]) for t in range(T)]
                v = []; qobs = []; gobs = []
                for t in range(T):
                    beta, features = q_models[t]
                    cf = dict(row); cf[treatments[t]] = chosen[t]
                    v.append(_predict_linear(beta, cf, features, clip=True))
                    qobs.append(_predict_linear(beta, row, features, clip=True))
                    p = _predict_logistic(g_models[t], row, histories[t])
                    gobs.append(max(clip, min(1 - clip, p if row[treatments[t]] == 1 else 1 - p)))
                score = v[0]; weight = 1.0
                for t in range(T):
                    if row[treatments[t]] != chosen[t]: weight = 0.0
                    else: weight /= gobs[t]
                    vnext = row[outcome] if t == T - 1 else v[t + 1]
                    score += weight * (vnext - qobs[t])
                scores[i] = score
        vals = [float(x) for x in scores if x is not None]
        if len(vals) != len(clean): raise RuntimeError("multistage cross-fit assignment incomplete")
        est = _mean(vals); se = _std_error(vals)
        output.append({"id": str(policy["id"]), "estimated_value": round(est, 10), "standard_error": round(se, 10), "interval95": [round(est - 1.96 * se, 10), round(est + 1.96 * se, 10)]})
    output.sort(key=lambda row: (row["estimated_value"], row["id"]), reverse=True)
    return {
        "status": "BOUNDED_MULTISTAGE_CROSS_FITTED_SEQUENTIAL_DR",
        "stages": T,
        "folds": k,
        "row_count": len(clean),
        "history_contract": [{"stage": t, "treatment": treatments[t], "available_features": histories[t]} for t in range(T)],
        "policies": output,
        "winner": output[0]["id"],
        "law": "cross-fitted sequential regression and inverse-propensity augmentation are evaluated under caller-declared decision-time histories for at most six binary treatment stages; declared history is not independently verified chronology, and this bounded estimator is not an arbitrary-horizon longitudinal DML/TMLE theorem, identification proof, or treatment authorization",
    }


def _validate_covariance(cov):
    matrix = [[_finite(v, "covariance") for v in row] for row in cov]
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix): raise ValueError("covariance must be nonempty square")
    for i in range(n):
        if matrix[i][i] < 0: raise ValueError("covariance diagonal must be nonnegative")
        for j in range(n):
            if abs(matrix[i][j] - matrix[j][i]) > 1e-8: raise ValueError("covariance must be symmetric")
    # PSD by Cholesky-like elimination with semidefinite tolerance.
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = matrix[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s < -1e-8: raise ValueError("covariance must be positive semidefinite")
                L[i][j] = math.sqrt(max(0.0, s))
            elif L[j][j] > 1e-10: L[i][j] = s / L[j][j]
            elif abs(s) > 1e-8: raise ValueError("covariance must be positive semidefinite")
    return matrix


def gaussian_mixture_update(variables, components, observation):
    names = [str(x) for x in variables]
    if not 1 <= len(names) <= 12 or len(set(names)) != len(names): raise ValueError("mixture variables requires 1..12 unique names")
    if not 2 <= len(components) <= 16: raise ValueError("Gaussian mixture requires 2..16 components")
    coeffs = observation.get("coefficients") or {}
    if not isinstance(coeffs, Mapping) or not coeffs: raise ValueError("observation coefficients required")
    unknown = sorted(set(str(k) for k in coeffs) - set(names))
    if unknown: raise ValueError("unknown observation coefficients: " + ", ".join(unknown))
    h = [_finite(coeffs.get(name, 0.0), f"coefficient {name}") for name in names]
    if all(abs(x) <= 1e-15 for x in h): raise ValueError("observation coefficients cannot all be zero")
    y = _finite(observation.get("value"), "observation value"); noise = _finite(observation.get("noise_variance"), "noise_variance")
    if noise <= 0: raise ValueError("noise_variance must be positive")
    ids = [str(c.get("id", "")) for c in components]
    if any(not x for x in ids) or len(set(ids)) != len(ids): raise ValueError("component ids must be nonempty unique")
    prepared = []; logw = []
    for comp in components:
        weight = _finite(comp.get("weight"), "component weight")
        if weight <= 0: raise ValueError("component weights must be positive")
        mu = [_finite(x, "component mean") for x in comp.get("mean", [])]
        if len(mu) != len(names): raise ValueError("component mean length must match variables")
        cov = _validate_covariance(comp.get("covariance") or [])
        if len(cov) != len(names): raise ValueError("component covariance size must match variables")
        sigma_h = [sum(cov[i][j] * h[j] for j in range(len(names))) for i in range(len(names))]
        pred = sum(h[i] * mu[i] for i in range(len(names))); variance = sum(h[i] * sigma_h[i] for i in range(len(names))) + noise
        if variance <= 0: raise ValueError("component predictive variance must be positive")
        innovation = y - pred; gain = [x / variance for x in sigma_h]
        post_mu = [mu[i] + gain[i] * innovation for i in range(len(names))]
        post_cov = [[cov[i][j] - gain[i] * sigma_h[j] for j in range(len(names))] for i in range(len(names))]
        ll = -0.5 * (math.log(2 * math.pi * variance) + innovation * innovation / variance)
        prepared.append({"id": str(comp["id"]), "prior_weight": weight, "posterior_mean": post_mu, "posterior_covariance": post_cov, "predictive_mean": pred, "predictive_variance": variance})
        logw.append(math.log(weight) + ll)
    posterior_weights = _softmax_logs(logw)
    for comp, w in zip(prepared, posterior_weights): comp["posterior_weight"] = w
    d = len(names); mix_mu = [sum(c["posterior_weight"] * c["posterior_mean"][j] for c in prepared) for j in range(d)]
    mix_cov = [[0.0] * d for _ in range(d)]
    for c in prepared:
        w = c["posterior_weight"]; delta = [c["posterior_mean"][j] - mix_mu[j] for j in range(d)]
        for i in range(d):
            for j in range(d): mix_cov[i][j] += w * (c["posterior_covariance"][i][j] + delta[i] * delta[j])
    return {
        "status": "EXACT_FINITE_GAUSSIAN_MIXTURE_LINEAR_OBSERVATION_UPDATE",
        "variables": names,
        "components": [{"id": c["id"], "prior_weight": round(c["prior_weight"], 12), "posterior_weight": round(c["posterior_weight"], 12), "predictive_mean": round(c["predictive_mean"], 12), "predictive_variance": round(c["predictive_variance"], 12), "posterior_mean": [round(x, 12) for x in c["posterior_mean"]], "posterior_covariance": [[round(x, 12) for x in row] for row in c["posterior_covariance"]]} for c in prepared],
        "mixture_mean": [round(x, 12) for x in mix_mu],
        "mixture_covariance": [[round(x, 12) for x in row] for row in mix_cov],
        "law": "the posterior is exact only for the supplied finite Gaussian-mixture prior and shared linear-Gaussian observation model; a finite Gaussian mixture is a bounded non-Gaussian family, not general non-Gaussian Bayes or canonical truth",
    }


def _rbf(a, b, bandwidth):
    return math.exp(-sum((x - y) ** 2 for x, y in zip(a, b)) / (2.0 * bandwidth * bandwidth))


def _kernel_fit(xs, ys, bandwidth, ridge):
    n = len(xs); K = [[_rbf(xs[i], xs[j], bandwidth) for j in range(n)] for i in range(n)]
    for i in range(n): K[i][i] += ridge
    inv = _inverse(K)
    return [sum(inv[i][j] * ys[j] for j in range(n)) for i in range(n)]


def _kernel_predict(train_x, alpha, x, bandwidth):
    return max(0.0, sum(_rbf(x, train_x[i], bandwidth) * alpha[i] for i in range(len(train_x))))


def approx_error_field(feature_order, witnesses, queries, bandwidth=1.0, ridge=1e-3, folds=5, coverage=0.9, seed=0, max_support_distance=None):
    names = [str(x) for x in feature_order]
    if not 1 <= len(names) <= 8 or len(set(names)) != len(names): raise ValueError("error field feature_order requires 1..8 unique names")
    if not 30 <= len(witnesses) <= 96: raise ValueError("error field requires 30..96 explicit error witnesses")
    bw = _finite(bandwidth, "bandwidth"); reg = _finite(ridge, "ridge"); cov = _finite(coverage, "coverage")
    if bw <= 0 or reg <= 0 or not 0.5 <= cov < 1.0: raise ValueError("bandwidth/ridge must be positive and coverage in [0.5,1)")
    xs = []; ys = []
    for w in witnesses:
        f = w.get("features") or {}
        if any(name not in f for name in names): raise ValueError("each error witness requires all features")
        x = [_finite(f[name], name) for name in names]; y = _finite(w.get("absolute_error"), "absolute_error")
        if y < 0: raise ValueError("absolute_error must be nonnegative")
        xs.append(x); ys.append(y)
    assignment = _fold_assignment(len(xs), folds, seed); k = max(assignment) + 1; residuals = []
    for fold in range(k):
        train_i = [i for i in range(len(xs)) if assignment[i] != fold]; test_i = [i for i in range(len(xs)) if assignment[i] == fold]
        alpha = _kernel_fit([xs[i] for i in train_i], [ys[i] for i in train_i], bw, reg)
        for i in test_i:
            pred = _kernel_predict([xs[j] for j in train_i], alpha, xs[i], bw); residuals.append(abs(ys[i] - pred))
    residuals.sort(); q_index = min(len(residuals) - 1, max(0, math.ceil(cov * (len(residuals) + 1)) - 1)); qres = residuals[q_index]
    alpha = _kernel_fit(xs, ys, bw, reg); support_radius = None if max_support_distance is None else _finite(max_support_distance, "max_support_distance")
    if support_radius is not None and support_radius < 0: raise ValueError("max_support_distance must be nonnegative")
    out = []
    for qi, query in enumerate(queries):
        f = query.get("features") or {}
        if any(name not in f for name in names): raise ValueError("each error query requires all features")
        x = [_finite(f[name], name) for name in names]; nearest = min(math.sqrt(sum((x[j] - w[j]) ** 2 for j in range(len(names)))) for w in xs)
        pred = _kernel_predict(xs, alpha, x, bw); supported = support_radius is None or nearest <= support_radius
        out.append({"id": str(query.get("id", f"Q{qi}")), "predicted_absolute_error": round(pred, 10), "cv_residual_upper": round(pred + qres, 10), "nearest_witness_distance": round(nearest, 10), "within_support_radius": supported})
    return {
        "status": "CV_CALIBRATED_RBF_APPROXIMATION_ERROR_FIELD",
        "feature_order": names,
        "witness_count": len(xs),
        "folds": k,
        "coverage_target": cov,
        "cv_absolute_residual_quantile": round(qres, 10),
        "cv_mae": round(_mean(residuals), 10),
        "bandwidth": bw,
        "ridge": reg,
        "queries": out,
        "law": "the RBF kernel field is learned only from explicit approximation-error witnesses and the reported upper value is prediction plus an out-of-fold residual quantile; cross-validated residual calibration is not a distribution-free conformal guarantee, not a global Lipschitz certificate, and unsupported/OOD geometry remains explicit",
    }


def coupled_model_robust_policy(states, initial_state, models, policies, horizon, discount=1.0):
    names = [str(x) for x in states]
    if not 1 <= len(names) <= 8 or len(set(names)) != len(names): raise ValueError("robust model family requires 1..8 unique states")
    initial = str(initial_state)
    if initial not in names: raise ValueError("initial_state must be declared")
    H = int(horizon)
    if not 1 <= H <= 6: raise ValueError("horizon must lie in 1..6")
    gamma = _finite(discount, "discount")
    if not 0 <= gamma <= 1: raise ValueError("discount must lie in [0,1]")
    if not 2 <= len(models) <= 8: raise ValueError("coupled ambiguity requires 2..8 complete models")
    if not 1 <= len(policies) <= 32: raise ValueError("policies requires 1..32 supplied policies")
    model_ids = [str(m.get("id", "")) for m in models]; policy_ids = [str(p.get("id", "")) for p in policies]
    if any(not x for x in model_ids) or len(set(model_ids)) != len(model_ids): raise ValueError("model ids must be nonempty unique")
    if any(not x for x in policy_ids) or len(set(policy_ids)) != len(policy_ids): raise ValueError("policy ids must be nonempty unique")
    parsed_models = []
    raw_weights = []
    for model in models:
        actions_by_state = model.get("actions_by_state") or {}
        if set(str(k) for k in actions_by_state) != set(names): raise ValueError("each model must define exactly every state")
        parsed = {}
        for s in names:
            rows = actions_by_state[s]
            if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows: raise ValueError("each model state requires actions")
            ids = [str(a.get("id", "")) for a in rows]
            if any(not x for x in ids) or len(set(ids)) != len(ids): raise ValueError("model action ids must be nonempty unique per state")
            parsed[s] = {}
            for action in rows:
                trans = action.get("transitions") or {}
                if set(str(k) for k in trans) != set(names): raise ValueError("transitions must define exactly every state")
                probs = [_finite(trans[s2], "transition probability") for s2 in names]
                if any(p < 0 for p in probs) or abs(sum(probs) - 1.0) > 1e-8: raise ValueError("transition probabilities must be nonnegative and sum to one")
                parsed[s][str(action["id"])] = {"reward": _finite(action.get("reward", 0.0), "reward"), "probs": probs}
        parsed_models.append({"id": str(model["id"]), "actions": parsed})
        raw_weights.append(_finite(model.get("weight", 1.0), "model weight"))
    if any(w <= 0 for w in raw_weights): raise ValueError("model weights must be positive")
    z = sum(raw_weights); weights = [w / z for w in raw_weights]

    values_by_policy = []
    for policy in policies:
        schedule = policy.get("action_by_stage") or {}
        if set(str(k) for k in schedule) != {str(t) for t in range(H)}: raise ValueError("policy action_by_stage must define exactly stages 0..H-1")
        for t in range(H):
            if set(str(k) for k in schedule[str(t)]) != set(names): raise ValueError("each policy stage must define exactly every state")
        model_values = []
        for model in parsed_models:
            nxt = {s: 0.0 for s in names}
            for t in range(H - 1, -1, -1):
                cur = {}
                for s in names:
                    aid = str(schedule[str(t)][s]); action = model["actions"][s].get(aid)
                    if action is None: raise ValueError(f"policy action {aid} unavailable in model {model['id']} state {s}")
                    cur[s] = action["reward"] + gamma * sum(action["probs"][j] * nxt[names[j]] for j in range(len(names)))
                nxt = cur
            model_values.append(nxt[initial])
        values_by_policy.append({"id": str(policy["id"]), "model_values": model_values})
    best_by_model = [max(row["model_values"][j] for row in values_by_policy) for j in range(len(parsed_models))]
    ranked = []
    for row in values_by_policy:
        vals = row["model_values"]; regrets = [best_by_model[j] - vals[j] for j in range(len(vals))]
        ranked.append({"id": row["id"], "robust_value": round(min(vals), 10), "weighted_model_value": round(sum(weights[j] * vals[j] for j in range(len(vals))), 10), "worst_regret": round(max(regrets), 10), "weighted_regret": round(sum(weights[j] * regrets[j] for j in range(len(vals))), 10), "per_model": [{"model_id": parsed_models[j]["id"], "value": round(vals[j], 10), "weight": round(weights[j], 10)} for j in range(len(vals))]})
    ranked.sort(key=lambda row: (row["robust_value"], row["weighted_model_value"], -row["worst_regret"], row["id"]), reverse=True)
    return {
        "status": "EXACT_SUPPLIED_POLICY_SET_COUPLED_MODEL_FAMILY_ROBUST_EVALUATION",
        "ambiguity": "ONE_COMPLETE_MODEL_CHOSEN_FOR_WHOLE_HORIZON",
        "states": names,
        "horizon": H,
        "model_count": len(parsed_models),
        "policy_count": len(ranked),
        "ranked": ranked,
        "winner": ranked[0]["id"],
        "law": "one complete transition/reward model is held fixed across the horizon, coupling ambiguity across states and time; evaluation is exact only for the supplied finite model family and supplied policy set, not general non-rectangular DRO optimization, not a proof the true world lies in the family, and not execution authority",
    }


class CollectiveGeneralizedRuntime:
    def __init__(self, calibrated):
        self.calibrated = calibrated

    def describe(self):
        return {
            "version": "COLLECTIVE_RUNTIME_V16",
            "coordinate": "COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>",
            "operators": ["ordered_dag_posterior", "longitudinal_dr_multistage_crossfit", "gaussian_mixture_update", "approx_error_field", "coupled_model_robust_policy"],
            "laws": [
                "ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR",
                "BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM",
                "FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES",
                "CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE",
                "FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION",
            ],
        }
