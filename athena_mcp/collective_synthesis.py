from __future__ import annotations

import itertools
import json
import math
import random
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence

from .collective_probabilistic import _fit_logistic, _mean, _predict_logistic
from .collective_robust import CollectiveRobustRuntime, _policy_action


def _entropy(weights: Sequence[float]) -> float:
    return -sum(float(w) * math.log(max(float(w), 1e-300), 2) for w in weights if float(w) > 0)


def _normalise(rows: Sequence[Mapping[str, Any]], key: str = "weight") -> list[dict[str, Any]]:
    out = [dict(row) for row in rows]
    vals = [max(0.0, float(row.get(key, 0.0))) for row in out]
    total = sum(vals)
    if total <= 0:
        raise ValueError("weights must contain positive total mass")
    for row, value in zip(out, vals):
        row[key] = value / total
    return out


def _lower_cvar(values: Sequence[float], weights: Sequence[float], alpha: float) -> float:
    a = max(1e-6, min(1.0, float(alpha)))
    pairs = sorted((float(v), max(0.0, float(w))) for v, w in zip(values, weights))
    remaining = a
    total = 0.0
    for value, weight in pairs:
        if remaining <= 1e-15:
            break
        take = min(remaining, weight)
        total += take * value
        remaining -= take
    if remaining > 1e-12:
        raise ValueError("joint-state weights do not cover requested CVaR mass")
    return total / a


def _pareto(rows: Sequence[Mapping[str, Any]], dimensions: Sequence[tuple[str, int]]) -> list[str]:
    frontier = []
    for i, row in enumerate(rows):
        dominated = False
        for j, other in enumerate(rows):
            if i == j:
                continue
            weak = True
            strict = False
            for key, direction in dimensions:
                a = float(row[key]) * direction
                b = float(other[key]) * direction
                if b < a - 1e-12:
                    weak = False
                    break
                if b > a + 1e-12:
                    strict = True
            if weak and strict:
                dominated = True
                break
        if not dominated:
            frontier.append(str(row["id"]))
    return frontier


def _resource_vector(item: Mapping[str, Any], resources: Sequence[str]) -> dict[str, float]:
    raw = item.get("resources") or {}
    if not isinstance(raw, Mapping):
        raise ValueError("resources must be an object")
    out = {}
    for resource in resources:
        if resource not in raw:
            raise ValueError(f"candidate missing resource {resource}")
        value = float(raw[resource])
        if value < 0:
            raise ValueError("resource consumption must be non-negative")
        out[resource] = value
    return out


class CollectiveSynthesisRuntime:
    """V14 joint-posterior scientific-control synthesis layer.

    V14 composes bounded uncertainty surfaces that already existed separately in
    V8-V13.  It does not turn finite factor products into a universal posterior,
    bootstrap graph frequencies into causal probabilities, dynamic-policy
    estimates into treatment authority, approximation checks into global
    guarantees, or finite scenario recourse into a general stochastic program.
    """

    def __init__(self, robust: CollectiveRobustRuntime):
        self.robust = robust
        self.joint = robust.joint
        self.probabilistic = robust.probabilistic
        self.s = robust.s

    def describe(self) -> dict[str, Any]:
        return {
            "version": "COLLECTIVE_RUNTIME_V14",
            "persistent_surfaces": {},
            "operators": [
                "joint_factor_belief",
                "structural_bootstrap_ensemble",
                "joint_science_evi",
                "sequential_dr_policy_value",
                "joint_policy_robust",
                "gp_resolution_route",
                "two_stage_resource_plan",
            ],
            "coordinate": "COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>",
            "laws": [
                "FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR",
                "BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR",
                "JOINT_SCIENCE_EVI != OBSERVATION_OR_EVIDENCE",
                "SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM",
                "FINITE_SCENARIO_ROBUST_POLICY != GENERAL_ROBUST_CONTROL",
                "QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE",
                "FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM",
            ],
        }

    # ---------- finite joint factor belief ----------
    def joint_factor_belief(
        self,
        axes: Mapping[str, Any],
        compatibility: Sequence[Mapping[str, Any]] | None = None,
        likelihood_by_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(axes, Mapping) or len(axes) < 2 or len(axes) > 5:
            raise ValueError("joint factor belief requires 2..5 axes")
        axis_rows: dict[str, list[dict[str, Any]]] = {}
        product_size = 1
        for axis, values in axes.items():
            name = str(axis)
            if not isinstance(values, Sequence) or isinstance(values, (str, bytes)) or not values:
                raise ValueError(f"axis {name} must contain states")
            if len(values) > 32:
                raise ValueError("each joint-belief axis supports at most 32 states")
            ids = set()
            rows = []
            for index, raw in enumerate(values):
                if not isinstance(raw, Mapping):
                    raise ValueError(f"axis {name} states must be objects")
                sid = str(raw.get("id", f"{name}:{index}"))
                if sid in ids:
                    raise ValueError(f"duplicate state id {sid} on axis {name}")
                ids.add(sid)
                weight = float(raw.get("weight", raw.get("prior", 1.0)))
                if weight < 0:
                    raise ValueError("joint factor weights must be non-negative")
                rows.append({"id": sid, "weight": weight, "metadata": dict(raw.get("metadata") or {})})
            axis_rows[name] = _normalise(rows)
            product_size *= len(rows)
        if product_size > 512:
            raise ValueError("finite joint factor product is capped at 512 states")

        rules = list(compatibility or [])
        for rule in rules:
            if not isinstance(rule, Mapping) or not isinstance(rule.get("assignments"), Mapping):
                raise ValueError("compatibility rules require assignments objects")
            multiplier = float(rule.get("multiplier", 1.0))
            if multiplier < 0:
                raise ValueError("compatibility multipliers must be non-negative")
            for axis, sid in rule["assignments"].items():
                if str(axis) not in axis_rows or str(sid) not in {r["id"] for r in axis_rows[str(axis)]}:
                    raise ValueError("compatibility rule references unknown axis state")

        ordered_axes = sorted(axis_rows)
        states = []
        for combo in itertools.product(*(axis_rows[a] for a in ordered_axes)):
            assignment = {axis: row["id"] for axis, row in zip(ordered_axes, combo)}
            prior = math.prod(float(row["weight"]) for row in combo)
            compat = 1.0
            for rule in rules:
                wanted = {str(k): str(v) for k, v in rule["assignments"].items()}
                if all(assignment.get(k) == v for k, v in wanted.items()):
                    compat *= float(rule.get("multiplier", 1.0))
            state_id = "|".join(f"{axis}={assignment[axis]}" for axis in ordered_axes)
            likelihood = 1.0
            if likelihood_by_state is not None:
                if state_id not in likelihood_by_state:
                    raise ValueError(f"missing likelihood for joint state {state_id}")
                likelihood = float(likelihood_by_state[state_id])
                if likelihood < 0:
                    raise ValueError("joint-state likelihoods must be non-negative")
            states.append({
                "id": state_id,
                "assignment": assignment,
                "prior_factor_weight": prior,
                "compatibility_multiplier": compat,
                "likelihood": likelihood,
                "weight": prior * compat * likelihood,
            })
        states = _normalise(states)
        weights = [float(s["weight"]) for s in states]
        marginals = {}
        for axis in ordered_axes:
            mass = defaultdict(float)
            for state in states:
                mass[state["assignment"][axis]] += float(state["weight"])
            marginals[axis] = [{"id": sid, "weight": round(weight, 12)} for sid, weight in sorted(mass.items())]
        top = sorted(states, key=lambda s: (float(s["weight"]), s["id"]), reverse=True)
        return {
            "status": "FINITE_JOINT_FACTOR_BELIEF",
            "axes": ordered_axes,
            "state_count": len(states),
            "entropy_bits": round(_entropy(weights), 10),
            "effective_state_count": round(1.0 / sum(w * w for w in weights), 10),
            "marginals": marginals,
            "states": [
                {
                    **{k: v for k, v in state.items() if k not in {"prior_factor_weight", "compatibility_multiplier", "likelihood", "weight"}},
                    "prior_factor_weight": round(float(state["prior_factor_weight"]), 12),
                    "compatibility_multiplier": round(float(state["compatibility_multiplier"]), 12),
                    "likelihood": round(float(state["likelihood"]), 12),
                    "weight": round(float(state["weight"]), 12),
                }
                for state in top
            ],
            "law": "finite caller-declared factor axes are multiplied, compatibility-weighted and optionally likelihood-updated exactly over the bounded Cartesian product; this is a finite science-twin belief, not a universal joint posterior or canonical truth",
        }

    # ---------- bootstrap structural ensemble over FCI-lite ----------
    def structural_bootstrap_ensemble(
        self,
        samples: Sequence[Mapping[str, Any]],
        variables: Sequence[str] | None = None,
        bootstrap_runs: int = 32,
        alpha: float = 0.05,
        max_conditioning: int = 2,
        stable_threshold: float = 0.7,
        seed: int = 0,
    ) -> dict[str, Any]:
        rows = list(samples)
        if len(rows) < 40:
            raise ValueError("structural bootstrap ensemble requires at least forty samples")
        runs = max(8, min(int(bootstrap_runs), 128))
        threshold = max(0.5, min(1.0, float(stable_threshold)))
        rng = random.Random(int(seed))
        variants: dict[str, dict[str, Any]] = {}
        edge_support = defaultdict(int)
        failures = []
        valid = 0
        for run in range(runs):
            boot = [rows[rng.randrange(len(rows))] for _ in rows]
            try:
                graph = self.robust.fci_lite_discover(boot, variables, alpha, max_conditioning)
            except Exception as exc:
                failures.append({"run": run, "error": f"{type(exc).__name__}: {exc}"})
                continue
            valid += 1
            edges = sorted(
                (
                    str(e["a"]),
                    str(e["b"]),
                    str(e["endpoint_a"]),
                    str(e["endpoint_b"]),
                )
                for e in graph.get("edges", [])
            )
            key = json.dumps(edges, separators=(",", ":"), ensure_ascii=False)
            rec = variants.setdefault(key, {"edges": edges, "count": 0})
            rec["count"] += 1
            for edge in edges:
                edge_support[edge] += 1
        if valid < 8:
            raise ValueError("too few valid bootstrap graph fits")
        ranked = []
        for key, rec in variants.items():
            support = rec["count"] / valid
            ranked.append({
                "id": f"G{len(ranked) + 1}",
                "support": round(support, 10),
                "count": rec["count"],
                "edges": [
                    {"a": a, "b": b, "endpoint_a": ea, "endpoint_b": eb}
                    for a, b, ea, eb in rec["edges"]
                ],
            })
        ranked.sort(key=lambda r: (r["support"], r["id"]), reverse=True)
        for index, row in enumerate(ranked):
            row["id"] = f"G{index + 1}"
        stable = [
            {
                "a": edge[0],
                "b": edge[1],
                "endpoint_a": edge[2],
                "endpoint_b": edge[3],
                "support": round(count / valid, 10),
            }
            for edge, count in sorted(edge_support.items())
            if count / valid >= threshold
        ]
        probs = [float(r["support"]) for r in ranked]
        return {
            "status": "BOOTSTRAP_FCI_LITE_STRUCTURAL_ENSEMBLE",
            "requested_runs": runs,
            "valid_runs": valid,
            "failed_runs": failures,
            "variant_count": len(ranked),
            "variant_entropy_bits": round(_entropy(probs), 10),
            "stable_threshold": threshold,
            "stable_marked_edges": stable,
            "variants": ranked,
            "law": "bootstrap frequency measures procedural stability of the bounded FCI-lite output under resampled observed rows; it is not a Bayesian causal-graph posterior, FCI completeness theorem, or canonical JSPACE mutation",
        }

    # ---------- exact finite EVI over joint science-twin states ----------
    def joint_science_evi(
        self,
        joint_states: Sequence[Mapping[str, Any]],
        actions: Sequence[Mapping[str, Any]],
        experiments: Sequence[Mapping[str, Any]],
        information_weight: float = 1.0,
        decision_weight: float = 1.0,
        cost_weight: float = 1.0,
        risk_weight: float = 1.0,
    ) -> dict[str, Any]:
        states = _normalise(joint_states)
        if len(states) < 2 or len(states) > 512:
            raise ValueError("joint science EVI requires 2..512 finite states")
        state_ids = [str(s.get("id")) for s in states]
        if len(set(state_ids)) != len(state_ids) or any(sid in {"", "None"} for sid in state_ids):
            raise ValueError("joint states require unique non-empty ids")
        weights = [float(s["weight"]) for s in states]
        if not actions or len(actions) > 32 or not experiments or len(experiments) > 32:
            raise ValueError("joint science EVI supports 1..32 actions and 1..32 experiments")
        utilities = {}
        for ai, action in enumerate(actions):
            aid = str(action.get("id", f"A{ai}"))
            by_state = action.get("utility_by_state") or {}
            if set(by_state) != set(state_ids):
                raise ValueError(f"action {aid} utility_by_state must cover every joint state exactly")
            utilities[aid] = {sid: float(by_state[sid]) for sid in state_ids}
        current = {
            aid: sum(weights[i] * utilities[aid][sid] for i, sid in enumerate(state_ids))
            for aid in utilities
        }
        current_best = max(current.values())
        prior_h = _entropy(weights)
        ranked = []
        for ei, experiment in enumerate(experiments):
            eid = str(experiment.get("id", f"E{ei}"))
            outcomes = experiment.get("outcomes") or {}
            if not isinstance(outcomes, Mapping) or len(outcomes) < 2 or len(outcomes) > 16:
                raise ValueError(f"experiment {eid} requires 2..16 outcomes")
            for outcome, likelihoods in outcomes.items():
                if not isinstance(likelihoods, Mapping) or set(likelihoods) != set(state_ids):
                    raise ValueError(f"experiment {eid} outcome {outcome} must cover every joint state")
                if any(float(likelihoods[sid]) < 0 for sid in state_ids):
                    raise ValueError("outcome likelihoods must be non-negative")
            for sid in state_ids:
                total = sum(float(outcomes[outcome][sid]) for outcome in outcomes)
                if abs(total - 1.0) > 1e-6:
                    raise ValueError(f"experiment {eid} likelihoods for state {sid} must sum to one")
            future_value = 0.0
            expected_h = 0.0
            branch_rows = []
            for outcome, likelihoods in outcomes.items():
                py = sum(weights[i] * float(likelihoods[sid]) for i, sid in enumerate(state_ids))
                if py <= 1e-15:
                    branch_rows.append({"outcome": str(outcome), "probability": 0.0, "best_action": None})
                    continue
                posterior = [weights[i] * float(likelihoods[sid]) / py for i, sid in enumerate(state_ids)]
                branch_utils = {
                    aid: sum(posterior[i] * utilities[aid][sid] for i, sid in enumerate(state_ids))
                    for aid in utilities
                }
                best_action = max(branch_utils, key=lambda aid: (branch_utils[aid], aid))
                best_value = branch_utils[best_action]
                future_value += py * best_value
                expected_h += py * _entropy(posterior)
                branch_rows.append({
                    "outcome": str(outcome),
                    "probability": round(py, 12),
                    "best_action": best_action,
                    "best_expected_utility": round(best_value, 10),
                    "posterior_entropy_bits": round(_entropy(posterior), 10),
                })
            evi = max(0.0, future_value - current_best)
            ig = max(0.0, prior_h - expected_h)
            cost = float(experiment.get("cost", 0.0))
            risk = float(experiment.get("risk", 0.0))
            feasibility = max(0.0, min(1.0, float(experiment.get("feasibility", 1.0))))
            ethical = bool(experiment.get("ethical", True))
            score = feasibility * (
                float(decision_weight) * evi + float(information_weight) * ig
            ) - float(cost_weight) * cost - float(risk_weight) * risk
            ranked.append({
                "id": eid,
                "status": "ELIGIBLE" if ethical and feasibility > 0 else "BLOCKED",
                "decision_evi": round(evi, 10),
                "joint_information_gain_bits": round(ig, 10),
                "cost": cost,
                "risk": risk,
                "feasibility": feasibility,
                "score": round(score, 10),
                "branches": branch_rows,
            })
        ranked.sort(key=lambda r: (r["score"], r["decision_evi"], r["joint_information_gain_bits"], r["id"]), reverse=True)
        eligible = [r for r in ranked if r["status"] == "ELIGIBLE"]
        return {
            "decision": "FINITE_JOINT_SCIENCE_EVI_DESIGN_ONLY",
            "state_count": len(states),
            "prior_entropy_bits": round(prior_h, 10),
            "current_action_values": {k: round(v, 10) for k, v in sorted(current.items())},
            "current_best_expected_utility": round(current_best, 10),
            "winner": eligible[0]["id"] if eligible else None,
            "ranked": ranked,
            "law": "exact enumeration is exact only for the supplied finite joint-state/action/outcome utility model; hypothetical outcomes and posteriors are design state and never become observations, evidence, Y1 authority, or execution history",
        }

    # ---------- two-timepoint sequential doubly robust dynamic-policy value ----------
    def sequential_dr_policy_value(
        self,
        samples: Sequence[Mapping[str, Any]],
        treatment1: str,
        intermediate: str,
        treatment2: str,
        outcome: str,
        policies: Sequence[Mapping[str, Any]],
        baseline: Sequence[str] | None = None,
        assumptions: Mapping[str, Any] | None = None,
        propensity_clip: float = 0.05,
    ) -> dict[str, Any]:
        if len(samples) < 120:
            raise ValueError("sequential DR policy value requires at least one hundred twenty samples")
        assumptions = dict(assumptions or {})
        if assumptions.get("latent_confounding_possible") is True:
            return {
                "status": "UNIDENTIFIED_LATENT_CONFOUNDING_RISK",
                "method": "TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE",
                "assumptions": assumptions,
                "law": "declared latent confounding fails closed before policy valuation",
            }
        if not policies or len(policies) > 32:
            raise ValueError("policies must contain 1..32 policy objects")
        base, rows = self.robust._longitudinal_rows(
            samples, treatment1, intermediate, treatment2, outcome, baseline
        )
        clip = max(0.01, min(0.25, float(propensity_clip)))
        g1 = _fit_logistic(rows, "A1", base)
        g2 = _fit_logistic(rows, "A2", base + ["A1", "L1"])
        q2 = _fit_logistic(rows, "Y", base + ["A1", "L1", "A2"])
        results = []
        for pi, policy in enumerate(policies):
            pseudo = []
            for row in rows:
                hist = {**{k: row[k] for k in base}, "A1": row["A1"], "L1": row["L1"]}
                a2pi = _policy_action(policy.get("a2", 0), hist, "a2")
                q2pi = _predict_logistic(q2, {**hist, "A2": a2pi}, base + ["A1", "L1", "A2"])
                pseudo.append({**{k: row[k] for k in base}, "A1": row["A1"], "Q2PI": q2pi})
            q1 = _fit_logistic(pseudo, "Q2PI", base + ["A1"])
            dr_values = []
            weights1 = []
            weights2 = []
            for row in rows:
                xb = {k: row[k] for k in base}
                a1pi = _policy_action(policy.get("a1", 0), xb, "a1")
                hist = {**xb, "A1": row["A1"], "L1": row["L1"]}
                a2pi = _policy_action(policy.get("a2", 0), hist, "a2")
                p1 = _predict_logistic(g1, xb, base)
                g1pi = max(clip, min(1 - clip, p1 if a1pi == 1 else 1 - p1))
                p2 = _predict_logistic(g2, hist, base + ["A1", "L1"])
                g2pi = max(clip, min(1 - clip, p2 if a2pi == 1 else 1 - p2))
                q2obs = _predict_logistic(q2, {**hist, "A2": row["A2"]}, base + ["A1", "L1", "A2"])
                q2pi = _predict_logistic(q2, {**hist, "A2": a2pi}, base + ["A1", "L1", "A2"])
                q1obs = _predict_logistic(q1, {**xb, "A1": row["A1"]}, base + ["A1"])
                q1pi = _predict_logistic(q1, {**xb, "A1": a1pi}, base + ["A1"])
                h1 = (1.0 if row["A1"] == a1pi else 0.0) / g1pi
                h2 = (1.0 if row["A1"] == a1pi and row["A2"] == a2pi else 0.0) / (g1pi * g2pi)
                dr = q1pi + h1 * (q2pi - q1obs) + h2 * (row["Y"] - q2obs)
                dr_values.append(dr)
                weights1.append(h1)
                weights2.append(h2)
            estimate = _mean(dr_values)
            if len(dr_values) > 1:
                sd = statistics.stdev(dr_values)
                se = sd / math.sqrt(len(dr_values))
            else:
                se = 0.0
            results.append({
                "id": str(policy.get("id", f"P{pi}")),
                "estimated_value": round(estimate, 10),
                "standard_error": round(se, 10),
                "ci95": [round(estimate - 1.96 * se, 10), round(estimate + 1.96 * se, 10)],
                "max_stage1_weight": round(max(weights1) if weights1 else 0.0, 10),
                "max_stage2_weight": round(max(weights2) if weights2 else 0.0, 10),
            })
        results.sort(key=lambda r: (r["estimated_value"], r["id"]), reverse=True)
        return {
            "status": "TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS",
            "method": "TWO_TIMEPOINT_SEQUENTIAL_AIPW",
            "n": len(rows),
            "baseline": base,
            "winner": results[0]["id"],
            "policies": results,
            "propensity_clip": clip,
            "cross_fitted": False,
            "assumptions": assumptions,
            "history_invariant": "STAGE2_POLICY_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_POLICY_EVALUATION",
            "law": "bounded two-timepoint sequential AIPW combines outcome regressions and inverse-propensity augmentation for supplied deterministic policies; without cross-fitting/general nuisance theory it is not a general longitudinal causal-value theorem, identification proof, randomized evidence, or execution authorization",
        }

    # ---------- robust policy choice over finite joint states ----------
    def joint_policy_robust(
        self,
        joint_states: Sequence[Mapping[str, Any]],
        policies: Sequence[Mapping[str, Any]],
        cvar_alpha: float = 0.1,
        risk_weight: float = 1.0,
        regret_weight: float = 1.0,
        cost_weight: float = 1.0,
    ) -> dict[str, Any]:
        states = _normalise(joint_states)
        state_ids = [str(s.get("id")) for s in states]
        if len(states) < 2 or len(states) > 512 or len(set(state_ids)) != len(state_ids):
            raise ValueError("robust policy selection requires 2..512 unique joint states")
        if not policies or len(policies) > 64:
            raise ValueError("robust policy selection supports 1..64 policies")
        weights = [float(s["weight"]) for s in states]
        utility_rows = {}
        for pi, policy in enumerate(policies):
            pid = str(policy.get("id", f"P{pi}"))
            by_state = policy.get("utility_by_state") or {}
            if set(by_state) != set(state_ids):
                raise ValueError(f"policy {pid} utility_by_state must cover every joint state exactly")
            utility_rows[pid] = [float(by_state[sid]) for sid in state_ids]
        best_by_state = [max(utility_rows[pid][i] for pid in utility_rows) for i in range(len(states))]
        rows = []
        for pi, policy in enumerate(policies):
            pid = str(policy.get("id", f"P{pi}"))
            values = utility_rows[pid]
            expected = sum(w * value for w, value in zip(weights, values))
            worst = min(values)
            cvar = _lower_cvar(values, weights, cvar_alpha)
            regrets = [best_by_state[i] - values[i] for i in range(len(states))]
            expected_regret = sum(weights[i] * regrets[i] for i in range(len(states)))
            max_regret = max(regrets)
            cost = float(policy.get("cost", 0.0))
            score = expected - float(risk_weight) * max(0.0, expected - cvar) - float(regret_weight) * expected_regret - float(cost_weight) * cost
            rows.append({
                "id": pid,
                "expected_utility": round(expected, 10),
                "worst_case_utility": round(worst, 10),
                "lower_cvar_utility": round(cvar, 10),
                "expected_regret": round(expected_regret, 10),
                "max_regret": round(max_regret, 10),
                "cost": cost,
                "score": round(score, 10),
            })
        frontier = _pareto(rows, [
            ("expected_utility", 1),
            ("lower_cvar_utility", 1),
            ("worst_case_utility", 1),
            ("expected_regret", -1),
            ("cost", -1),
        ])
        rows.sort(key=lambda r: (r["score"], r["expected_utility"], -r["expected_regret"], r["id"]), reverse=True)
        return {
            "decision": "FINITE_JOINT_SCENARIO_ROBUST_POLICY_PLAN_ONLY",
            "state_count": len(states),
            "cvar_alpha": max(1e-6, min(1.0, float(cvar_alpha))),
            "winner": rows[0]["id"],
            "pareto_frontier": frontier,
            "policies": rows,
            "law": "expected utility, lower-tail CVaR, worst case and regret are evaluated exactly only across the supplied finite weighted joint states; finite-scenario robustness is not a universal robust-control theorem or execution authorization",
        }

    # ---------- decision-relative GP approximation / zoom router ----------
    def gp_resolution_route(
        self,
        context_key: str,
        actions: Sequence[Mapping[str, Any]],
        inducing_counts: Sequence[int] | None = None,
        margin_safety: float = 0.5,
        include_observation_noise: bool = True,
    ) -> dict[str, Any]:
        if not actions or len(actions) > 32:
            raise ValueError("GP resolution routing supports 1..32 actions")
        counts = sorted(set(max(1, min(48, int(v))) for v in (inducing_counts or [4, 8, 16, 24, 32, 48])))
        safety = max(0.0, min(0.5, float(margin_safety)))
        exact_rows = []
        for ai, action in enumerate(actions):
            aid = str(action.get("id", f"A{ai}"))
            features = action.get("features") or {}
            pred = self.probabilistic.gp_predict(context_key, features, include_observation_noise)
            utility = float(action.get("utility_offset", 0.0)) + float(action.get("utility_scale", 1.0)) * float(pred["mean"])
            exact_rows.append({"id": aid, "features": features, "utility": utility})
        ranked_exact = sorted(exact_rows, key=lambda r: (r["utility"], r["id"]), reverse=True)
        exact_winner = ranked_exact[0]["id"]
        margin = math.inf if len(ranked_exact) == 1 else ranked_exact[0]["utility"] - ranked_exact[1]["utility"]
        routes = []
        selected = None
        for count in counts:
            approx_rows = []
            max_error = 0.0
            for ai, action in enumerate(actions):
                aid = str(action.get("id", f"A{ai}"))
                pred = self.robust.gp_fitc_predict(context_key, action.get("features") or {}, count, include_observation_noise)
                utility = float(action.get("utility_offset", 0.0)) + float(action.get("utility_scale", 1.0)) * float(pred["mean"])
                exact_utility = next(r["utility"] for r in exact_rows if r["id"] == aid)
                err = abs(utility - exact_utility)
                max_error = max(max_error, err)
                approx_rows.append({"id": aid, "utility": utility, "absolute_utility_error": err})
            approx_winner = max(approx_rows, key=lambda r: (r["utility"], r["id"]))["id"]
            threshold = math.inf if math.isinf(margin) else safety * max(0.0, margin)
            safe = approx_winner == exact_winner and max_error <= threshold + 1e-12
            row = {
                "mode": "FITC",
                "inducing_count": count,
                "winner": approx_winner,
                "max_query_utility_error": round(max_error, 10),
                "decision_error_threshold": None if math.isinf(threshold) else round(threshold, 10),
                "decision_preserving_on_queried_action_set": safe,
            }
            routes.append(row)
            if safe and selected is None:
                selected = row
        if selected is None:
            selected = {
                "mode": "FULL_GP",
                "inducing_count": None,
                "winner": exact_winner,
                "max_query_utility_error": 0.0,
                "decision_error_threshold": None if math.isinf(margin) else round(safety * max(0.0, margin), 10),
                "decision_preserving_on_queried_action_set": True,
            }
        return {
            "decision": "GP_DECISION_RELATIVE_RESOLUTION_ROUTE",
            "context_key": str(context_key),
            "exact_winner": exact_winner,
            "exact_decision_margin": None if math.isinf(margin) else round(margin, 10),
            "margin_safety": safety,
            "selected": selected,
            "candidate_routes": routes,
            "law": "the router compares FITC against the exact current bounded GP on the supplied action/query set and selects the cheapest tested representation preserving that decision within the declared margin rule; this is not a global approximation certificate, future-query guarantee, or permission to lower fidelity outside the witnessed set",
        }

    # ---------- finite two-stage stochastic resource recourse ----------
    def two_stage_resource_plan(
        self,
        first_stage: Sequence[Mapping[str, Any]],
        scenarios: Sequence[Mapping[str, Any]],
        risk_weight: float = 0.0,
        exact_limit: int = 16,
    ) -> dict[str, Any]:
        first = list(first_stage)
        scens = list(scenarios)
        if not first or len(first) > 24:
            raise ValueError("two-stage resource plan supports 1..24 first-stage candidates")
        if not scens or len(scens) > 16:
            raise ValueError("two-stage resource plan supports 1..16 scenarios")
        probs = [float(s.get("probability", 0.0)) for s in scens]
        if any(p < 0 for p in probs) or sum(probs) <= 0:
            raise ValueError("scenario probabilities must contain positive non-negative mass")
        totalp = sum(probs)
        probs = [p / totalp for p in probs]
        scenario_rows = []
        resources = None
        for index, (scenario, probability) in enumerate(zip(scens, probs)):
            budgets = scenario.get("budgets") or {}
            if not isinstance(budgets, Mapping) or not budgets:
                raise ValueError("every scenario requires budgets")
            names = sorted(str(k) for k in budgets)
            if resources is None:
                resources = names
            elif names != resources:
                raise ValueError("all scenarios must declare the same resource dimensions")
            clean_budgets = {r: float(budgets[r]) for r in resources}
            if any(v < 0 for v in clean_budgets.values()):
                raise ValueError("scenario budgets must be non-negative")
            recourse = list(scenario.get("recourse_options") or [])
            if len(recourse) > 32:
                raise ValueError("each scenario supports at most 32 recourse options")
            scenario_rows.append({
                "id": str(scenario.get("id", f"S{index}")),
                "probability": probability,
                "budgets": clean_budgets,
                "recourse": [
                    {
                        "id": str(option.get("id", f"R{j}")),
                        "value": float(option.get("value", 0.0)),
                        "resources": _resource_vector(option, resources),
                    }
                    for j, option in enumerate(recourse)
                ],
            })
        assert resources is not None
        first_clean = [
            {
                "id": str(item.get("id", f"F{i}")),
                "value": float(item.get("value", 0.0)),
                "resources": _resource_vector(item, resources),
            }
            for i, item in enumerate(first)
        ]
        if len({x["id"] for x in first_clean}) != len(first_clean):
            raise ValueError("first-stage candidate ids must be unique")

        def evaluate(indices: Sequence[int]):
            chosen = [first_clean[i] for i in indices]
            used = {r: sum(item["resources"][r] for item in chosen) for r in resources}
            base_value = sum(item["value"] for item in chosen)
            branches = []
            totals = []
            expected = base_value
            for scenario in scenario_rows:
                if any(used[r] > scenario["budgets"][r] + 1e-12 for r in resources):
                    return None
                residual = {r: scenario["budgets"][r] - used[r] for r in resources}
                feasible = [
                    option
                    for option in scenario["recourse"]
                    if all(option["resources"][r] <= residual[r] + 1e-12 for r in resources)
                ]
                recourse = max(feasible, key=lambda o: (o["value"], o["id"])) if feasible else None
                recourse_value = recourse["value"] if recourse is not None else 0.0
                total_value = base_value + recourse_value
                totals.append(total_value)
                expected += scenario["probability"] * recourse_value
                branches.append({
                    "scenario": scenario["id"],
                    "probability": round(scenario["probability"], 12),
                    "recourse": recourse["id"] if recourse is not None else None,
                    "recourse_value": round(recourse_value, 10),
                    "total_value": round(total_value, 10),
                    "residual_budget_before_recourse": {k: round(v, 10) for k, v in residual.items()},
                })
            worst = min(totals) if totals else base_value
            score = expected - float(risk_weight) * max(0.0, expected - worst)
            return {
                "selected": [item["id"] for item in chosen],
                "first_stage_value": round(base_value, 10),
                "expected_total_value": round(expected, 10),
                "worst_case_total_value": round(worst, 10),
                "score": round(score, 10),
                "resource_use": {k: round(v, 10) for k, v in used.items()},
                "scenario_recourse": branches,
            }

        limit = max(1, min(18, int(exact_limit)))
        evaluated = 0
        certificate = None
        plans = []
        if len(first_clean) <= limit:
            for mask in range(1 << len(first_clean)):
                indices = [i for i in range(len(first_clean)) if mask & (1 << i)]
                plan = evaluate(indices)
                evaluated += 1
                if plan is not None:
                    plans.append(plan)
            certificate = "EXACT_ENUMERATION_FOR_SUPPLIED_FINITE_TWO_STAGE_SCENARIO_MODEL"
        else:
            order = sorted(
                range(len(first_clean)),
                key=lambda i: (
                    first_clean[i]["value"]
                    / (1.0 + sum(first_clean[i]["resources"][r] / max(1e-12, min(s["budgets"][r] for s in scenario_rows)) for r in resources)),
                    first_clean[i]["id"],
                ),
                reverse=True,
            )
            current = []
            best = evaluate(current)
            if best is not None:
                plans.append(best)
            for index in order:
                candidate = current + [index]
                plan = evaluate(candidate)
                evaluated += 1
                if plan is not None:
                    current = candidate
                    plans.append(plan)
            certificate = None
        if not plans:
            raise ValueError("no feasible two-stage resource plan")
        plans.sort(key=lambda p: (p["score"], p["expected_total_value"], p["worst_case_total_value"], p["selected"]), reverse=True)
        best = plans[0]
        return {
            "status": "TWO_STAGE_RESOURCE_EXACT_ENUMERATION_CERTIFIED" if certificate else "TWO_STAGE_RESOURCE_GREEDY_UNCERTIFIED",
            "selected": best["selected"],
            "expected_total_value": best["expected_total_value"],
            "worst_case_total_value": best["worst_case_total_value"],
            "score": best["score"],
            "resource_use": best["resource_use"],
            "scenario_recourse": best["scenario_recourse"],
            "scenario_count": len(scenario_rows),
            "evaluated_first_stage_plans": evaluated,
            "certificate": certificate,
            "risk_weight": float(risk_weight),
            "law": "the exact certificate applies only to exhaustive first-stage subset enumeration with one best recourse option per supplied finite scenario and declared deterministic resource budgets; this is not a general multistage stochastic program, distributionally robust guarantee, or execution authorization",
        }
