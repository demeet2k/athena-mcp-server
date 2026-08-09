from __future__ import annotations

from typing import Any, Mapping, Sequence

from .collective_calibrated import _binary, _fold_assignment, _std_error
from .collective_probabilistic import _fit_logistic, _logit, _mean, _predict_logistic, _sigmoid
from .collective_robust import _fluctuation_epsilon


def longitudinal_tmle_crossfit(
    runtime,
    samples: Sequence[Mapping[str, Any]],
    treatment1: str,
    intermediate: str,
    treatment2: str,
    outcome: str,
    baseline: Sequence[str] | None = None,
    regimes: Sequence[Mapping[str, Any]] | None = None,
    assumptions: Mapping[str, Any] | None = None,
    propensity_clip: float = 0.05,
    folds: int = 2,
    seed: int = 0,
) -> dict[str, Any]:
    """Cross-fitted bounded two-timepoint sequential logistic TMLE.

    The stage-2 pseudo outcome preserves each row's observed A1/L1 history.
    Target A1 is applied only through the compatibility clever covariate at
    stage 2 and through the final stage-1 policy evaluation.
    """
    if len(samples) < 160:
        raise ValueError("cross-fitted two-timepoint TMLE requires at least one hundred sixty samples")
    assumptions = dict(assumptions or {})
    if assumptions.get("latent_confounding_possible") is True:
        return {
            "status": "UNIDENTIFIED_LATENT_CONFOUNDING_RISK",
            "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE",
            "assumptions": assumptions,
            "law": "declared latent confounding fails closed before estimation",
        }
    base, rows = runtime._longitudinal_rows(samples, treatment1, intermediate, treatment2, outcome, baseline)
    regs = list(regimes or [
        {"id": "00", "a1": 0, "a2": 0},
        {"id": "01", "a1": 0, "a2": 1},
        {"id": "10", "a1": 1, "a2": 0},
        {"id": "11", "a1": 1, "a2": 1},
    ])
    if not regs or len(regs) > 16:
        raise ValueError("regimes must contain 1..16 static treatment plans")
    clip = max(0.01, min(0.25, float(propensity_clip)))
    assignment = _fold_assignment(len(rows), folds, seed)
    k = max(assignment) + 1
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
                p1 = _predict_logistic(g1, r, base)
                g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                p2 = _predict_logistic(g2, r, base + ["A1", "L1"])
                g2a = max(clip, min(1 - clip, p2 if a2 == 1 else 1 - p2))
                qobs = max(1e-7, min(1 - 1e-7, _predict_logistic(q2, r, base + ["A1", "L1", "A2"])))
                ys.append(r["Y"])
                offsets.append(_logit(qobs))
                h2.append((1.0 if r["A1"] == a1 and r["A2"] == a2 else 0.0) / (g1a * g2a))
            eps2 = _fluctuation_epsilon(ys, offsets, h2)

            pseudo = []
            q2_target_train = []
            for r in train:
                # Preserve observed A1/L1 at stage 2; intervene only on A2.
                cf2 = {**r, "A2": a2}
                p1 = _predict_logistic(g1, r, base)
                g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                p2 = _predict_logistic(g2, r, base + ["A1", "L1"])
                g2a = max(clip, min(1 - clip, p2 if a2 == 1 else 1 - p2))
                q = max(1e-7, min(1 - 1e-7, _predict_logistic(q2, cf2, base + ["A1", "L1", "A2"])))
                h2_target = (1.0 if r["A1"] == a1 else 0.0) / (g1a * g2a)
                qt = _sigmoid(_logit(q) + eps2 * h2_target)
                q2_target_train.append(qt)
                pseudo.append({**{x: r[x] for x in base}, "A1": r["A1"], "Q": qt})

            q1 = _fit_logistic(pseudo, "Q", base + ["A1"])
            off1, h1 = [], []
            for r in train:
                p1 = _predict_logistic(g1, r, base)
                g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                q = max(1e-7, min(1 - 1e-7, _predict_logistic(q1, {**{x: r[x] for x in base}, "A1": r["A1"]}, base + ["A1"])))
                off1.append(_logit(q))
                h1.append((1.0 if r["A1"] == a1 else 0.0) / g1a)
            eps1 = _fluctuation_epsilon(q2_target_train, off1, h1)

            fold_values = []
            for i in test_idx:
                r = rows[i]
                cf1 = {**{x: r[x] for x in base}, "A1": a1}
                p1 = _predict_logistic(g1, r, base)
                g1a = max(clip, min(1 - clip, p1 if a1 == 1 else 1 - p1))
                q = max(1e-7, min(1 - 1e-7, _predict_logistic(q1, cf1, base + ["A1"])))
                value = _sigmoid(_logit(q) + eps1 / g1a)
                heldout_values[i] = value
                fold_values.append(value)
            fold_estimates.append(_mean(fold_values))

        vals = [float(x) for x in heldout_values]
        results.append({
            "id": str(reg.get("id", f"R{ri}")),
            "a1": a1,
            "a2": a2,
            "estimated_risk": round(_mean(vals), 10),
            "standard_error_proxy": round(_std_error(vals), 10),
            "fold_estimates": [round(x, 10) for x in fold_estimates],
        })

    results.sort(key=lambda r: (r["estimated_risk"], r["id"]), reverse=True)
    return {
        "status": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_UNDER_ASSUMPTIONS",
        "method": "CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE",
        "n": len(rows),
        "folds": k,
        "cross_fitted": True,
        "baseline": base,
        "regimes": results,
        "highest_risk_regime": results[0]["id"],
        "lowest_risk_regime": results[-1]["id"],
        "risk_contrast": round(results[0]["estimated_risk"] - results[-1]["estimated_risk"], 10),
        "propensity_clip": clip,
        "assumptions": assumptions,
        "history_invariant": "STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION",
        "law": "nuisance and targeting models are trained without each held-out evaluation fold; stage 2 preserves observed A1/L1 and intervenes only on A2 before stage-1 target evaluation; this remains a bounded two-timepoint sequential logistic TMLE construction",
    }
