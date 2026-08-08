from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Iterable

from .rehydration_loop import RehydrationLoopRuntime
from .rehydration_successor import (
    ALL_METRICS,
    BAD_METRICS,
    GOOD_METRICS,
    SuccessorCompiler,
)

ARTIFACT = "ATHENA.REHYDRATION.SUCCESSOR.REGRET.AB.V2"
_EPS = 1e-12


def _finite(value: Any, *, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _candidate_id(candidate: dict[str, Any]) -> str:
    value = candidate.get("candidate_id") or candidate.get("id") or candidate.get("task")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("candidate requires candidate_id/id/task")
    return value.strip()


def _benefit_vector(candidate: dict[str, Any]) -> dict[str, float]:
    metrics = candidate.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("candidate.metrics must be an object")
    out: dict[str, float] = {}
    for metric in GOOD_METRICS:
        value = _finite(metrics.get(metric), name=metric)
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{metric} must be in [0,1]")
        out[metric] = value
    for metric in BAD_METRICS:
        value = _finite(metrics.get(metric), name=metric)
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{metric} must be in [0,1]")
        out[metric] = 1.0 - value
    return out


def _point_weights_from_v1(policy: dict[str, Any]) -> tuple[dict[str, float], float]:
    raw = policy.get("weights") or {}
    if not isinstance(raw, dict):
        raise ValueError("V1 policy weights must be an object")

    magnitudes: dict[str, float] = {}
    violations: list[str] = []
    for metric in GOOD_METRICS:
        value = _finite(raw.get(metric, 0.0), name=f"weight.{metric}")
        if value < -_EPS:
            violations.append(metric)
        magnitudes[metric] = max(0.0, value)
    for metric in BAD_METRICS:
        value = _finite(raw.get(metric, 0.0), name=f"weight.{metric}")
        if value > _EPS:
            violations.append(metric)
        magnitudes[metric] = max(0.0, -value)

    if violations:
        raise ValueError(
            "V1 weight orientation incompatible with benefit-space calibration: "
            + ",".join(sorted(violations))
        )
    total = sum(magnitudes.values())
    if total <= _EPS:
        raise ValueError("V1 policy has zero total oriented weight")
    return {metric: magnitudes[metric] / total for metric in ALL_METRICS}, total


def _weight_box(center: dict[str, float], radius: float) -> dict[str, dict[str, float]]:
    radius = _finite(radius, name="weight radius")
    if radius < 0.0:
        raise ValueError("weight radius must be nonnegative")
    lower = {metric: max(0.0, center[metric] - radius) for metric in ALL_METRICS}
    upper = {metric: min(1.0, center[metric] + radius) for metric in ALL_METRICS}
    if sum(lower.values()) > 1.0 + 1e-10 or sum(upper.values()) < 1.0 - 1e-10:
        raise ValueError("derived weight box is infeasible")
    return {"lower": lower, "upper": upper}


def _canonical_weight_box(bounds: dict[str, Any]) -> dict[str, dict[str, float]]:
    raw_lower = bounds.get("lower") or {}
    raw_upper = bounds.get("upper") or {}
    if not isinstance(raw_lower, dict) or not isinstance(raw_upper, dict):
        raise ValueError("weight_bounds require lower/upper objects")

    lower: dict[str, float] = {}
    upper: dict[str, float] = {}
    for metric in ALL_METRICS:
        lo = _finite(raw_lower.get(metric, 0.0), name=f"lower.{metric}")
        hi = _finite(raw_upper.get(metric, 1.0), name=f"upper.{metric}")
        if not (0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0):
            raise ValueError("weight bounds must lie in [0,1]")
        if lo > hi + _EPS:
            raise ValueError(f"infeasible weight interval for {metric}")
        lower[metric] = lo
        upper[metric] = hi

    if sum(lower.values()) > 1.0 + 1e-10:
        raise ValueError("sum of lower weight bounds exceeds one")
    if sum(upper.values()) < 1.0 - 1e-10:
        raise ValueError("sum of upper weight bounds is below one")
    return {"lower": lower, "upper": upper}


def _intersect_weight_boxes(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, dict[str, float]]:
    a = _canonical_weight_box(left)
    b = _canonical_weight_box(right)
    return _canonical_weight_box(
        {
            "lower": {metric: max(a["lower"][metric], b["lower"][metric]) for metric in ALL_METRICS},
            "upper": {metric: min(a["upper"][metric], b["upper"][metric]) for metric in ALL_METRICS},
        }
    )


def maximize_linear_over_bounded_simplex(
    coefficients: dict[str, float],
    weight_bounds: dict[str, Any],
) -> dict[str, Any]:
    """Exactly maximize d*w over a box-constrained simplex."""
    bounds = _canonical_weight_box(weight_bounds)
    lower = bounds["lower"]
    upper = bounds["upper"]
    d = {
        metric: _finite(coefficients.get(metric, 0.0), name=f"coefficient.{metric}")
        for metric in ALL_METRICS
    }

    weights = dict(lower)
    remaining = 1.0 - sum(weights.values())
    order = sorted(ALL_METRICS, key=lambda metric: (-d[metric], metric))
    for metric in order:
        if remaining <= _EPS:
            break
        capacity = upper[metric] - weights[metric]
        if capacity <= 0.0:
            continue
        allocation = min(remaining, capacity)
        weights[metric] += allocation
        remaining -= allocation

    if remaining > 1e-9:
        raise ValueError("weight box is infeasible after residual allocation")

    value = sum(d[metric] * weights[metric] for metric in ALL_METRICS)
    contributions = [
        {
            "metric": metric,
            "coefficient": d[metric],
            "weight": weights[metric],
            "contribution": d[metric] * weights[metric],
        }
        for metric in ALL_METRICS
    ]
    contributions.sort(key=lambda row: (-row["contribution"], row["metric"]))
    return {
        "value": value,
        "weights": weights,
        "contributions": contributions,
        "law": "EXACT_BOX_SIMPLEX_SUPPORT",
    }


def _pairwise_regret(
    chosen: dict[str, Any],
    rival: dict[str, Any],
    weight_bounds: dict[str, Any],
) -> dict[str, Any]:
    a = _benefit_vector(chosen)
    b = _benefit_vector(rival)
    coefficients = {metric: b[metric] - a[metric] for metric in ALL_METRICS}
    solved = maximize_linear_over_bounded_simplex(coefficients, weight_bounds)
    return {
        "chosen_id": _candidate_id(chosen),
        "rival_id": _candidate_id(rival),
        "max_regret": max(0.0, solved["value"]),
        "raw_difference": solved["value"],
        "witness_weights": solved["weights"],
        "regret_dimensions": [
            row for row in solved["contributions"] if row["contribution"] > _EPS
        ],
    }


def minimax_regret(
    candidates: Iterable[dict[str, Any]],
    weight_bounds: dict[str, Any],
    *,
    tie_epsilon: float = 1e-9,
) -> dict[str, Any]:
    rows = [deepcopy(row) for row in candidates]
    if not rows:
        return {
            "status": "NO_SUCCESSOR",
            "minimax_regret": 0.0,
            "selected": None,
            "ties": [],
            "candidates": [],
            "weight_bounds": _canonical_weight_box(weight_bounds),
        }

    ids = [_candidate_id(row) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate ids must be unique")

    results = []
    for chosen in rows:
        worst = 0.0
        active = None
        for rival in rows:
            if rival is chosen:
                continue
            pair = _pairwise_regret(chosen, rival, weight_bounds)
            if pair["max_regret"] > worst + _EPS:
                worst = pair["max_regret"]
                active = pair
            elif (
                abs(pair["max_regret"] - worst) <= _EPS
                and active is not None
                and pair["rival_id"] < active["rival_id"]
            ):
                active = pair
        results.append(
            {
                "candidate_id": _candidate_id(chosen),
                "task": chosen.get("task"),
                "max_regret": worst,
                "active_rival_id": active["rival_id"] if active else None,
                "witness_weights": active["witness_weights"] if active else None,
                "regret_dimensions": active["regret_dimensions"] if active else [],
            }
        )

    results.sort(key=lambda row: (row["max_regret"], row["candidate_id"]))
    best = results[0]["max_regret"]
    ties = [row for row in results if abs(row["max_regret"] - best) <= tie_epsilon]
    selected = ties[0] if len(ties) == 1 else None
    return {
        "status": "SELECTED" if selected else "AMBIGUOUS",
        "minimax_regret": best,
        "selected": selected,
        "ties": ties,
        "candidates": results,
        "weight_bounds": _canonical_weight_box(weight_bounds),
    }


def _v1_semantic_selection(baton: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    status = str(baton.get("status") or "")
    if status == "SELECTED" and baton.get("selected"):
        return status, (_candidate_id(baton["selected"]),)
    if status == "AMBIGUOUS":
        return status, tuple(sorted(_candidate_id(row) for row in baton.get("ties") or []))
    return status, ()


def _v2_semantic_selection(result: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    status = str(result.get("status") or "")
    if status == "SELECTED" and result.get("selected"):
        return status, (str(result["selected"]["candidate_id"]),)
    if status == "AMBIGUOUS":
        return status, tuple(sorted(str(row["candidate_id"]) for row in result.get("ties") or []))
    return status, ()


def _v1_selection_tasks(baton: dict[str, Any]) -> tuple[str, ...]:
    status = str(baton.get("status") or "")
    if status == "SELECTED" and baton.get("selected"):
        return (str(baton["selected"].get("task") or ""),)
    if status == "AMBIGUOUS":
        return tuple(sorted(str(row.get("task") or "") for row in baton.get("ties") or []))
    return ()


def _v2_selection_tasks(result: dict[str, Any]) -> tuple[str, ...]:
    status = str(result.get("status") or "")
    if status == "SELECTED" and result.get("selected"):
        return (str(result["selected"].get("task") or ""),)
    if status == "AMBIGUOUS":
        return tuple(sorted(str(row.get("task") or "") for row in result.get("ties") or []))
    return ()


def _priced_cost(costs: dict[str, Any] | None, shadow_prices: dict[str, Any] | None) -> float:
    costs = dict(costs or {})
    prices = dict(shadow_prices or {})
    total = 0.0
    for resource, raw_amount in costs.items():
        amount = _finite(raw_amount, name=f"cost.{resource}")
        price = _finite(prices.get(resource, 0.0), name=f"shadow_price.{resource}")
        if amount < 0.0 or price < 0.0:
            raise ValueError("costs and shadow prices must be nonnegative")
        total += amount * price
    return total


def _evaluate_information_action(
    candidates: list[dict[str, Any]],
    base_bounds: dict[str, Any],
    action: dict[str, Any],
    *,
    shadow_prices: dict[str, Any] | None,
    tie_epsilon: float,
    min_net_gain: float,
) -> dict[str, Any]:
    action_id = str(action.get("action_id") or action.get("id") or action.get("kind") or "meta-action")
    if action.get("authority_required"):
        return {
            "action_id": action_id,
            "kind": action.get("kind"),
            "status": "OUTSIDE_INFORMATION_VOC",
            "net_voc": None,
            "reason": "authority-required query is a gate, not an optional information computation",
        }

    current = minimax_regret(candidates, base_bounds, tie_epsilon=tie_epsilon)
    cost = _priced_cost(action.get("costs"), shadow_prices)
    upper_bound = current["minimax_regret"] - cost
    if upper_bound <= min_net_gain + _EPS:
        return {
            "action_id": action_id,
            "kind": action.get("kind"),
            "status": "PRUNED_BY_REGRET_BOUND",
            "current_regret": current["minimax_regret"],
            "priced_cost": cost,
            "voc_upper_bound": upper_bound,
            "net_voc": upper_bound,
            "outcomes": [],
        }

    outcomes = action.get("outcomes")
    if not isinstance(outcomes, list) or not outcomes:
        raise ValueError("information action requires non-empty outcomes")

    probability_sum = 0.0
    expected_post_regret = 0.0
    outcome_rows = []
    for index, outcome in enumerate(outcomes):
        if not isinstance(outcome, dict):
            raise ValueError("information outcomes must be objects")
        probability = _finite(outcome.get("probability"), name="outcome probability")
        if probability < 0.0:
            raise ValueError("outcome probability must be nonnegative")
        probability_sum += probability

        post_bounds = base_bounds
        if outcome.get("weight_bounds") is not None:
            post_bounds = _intersect_weight_boxes(base_bounds, outcome["weight_bounds"])
        post_candidates = deepcopy(outcome.get("candidates") or candidates)
        post = minimax_regret(post_candidates, post_bounds, tie_epsilon=tie_epsilon)
        expected_post_regret += probability * post["minimax_regret"]
        outcome_rows.append(
            {
                "outcome_id": str(outcome.get("outcome_id") or outcome.get("id") or f"outcome-{index}"),
                "probability": probability,
                "post_regret": post["minimax_regret"],
                "post_status": post["status"],
                "post_selection": _v2_semantic_selection(post)[1],
            }
        )

    if abs(probability_sum - 1.0) > 1e-9:
        raise ValueError("outcome probabilities must sum to one")

    reduction = current["minimax_regret"] - expected_post_regret
    net_voc = reduction - cost
    return {
        "action_id": action_id,
        "kind": action.get("kind"),
        "status": "POSITIVE_VOC" if net_voc > min_net_gain + _EPS else "NONPOSITIVE_VOC",
        "current_regret": current["minimax_regret"],
        "priced_cost": cost,
        "voc_upper_bound": upper_bound,
        "expected_post_regret": expected_post_regret,
        "expected_regret_reduction": reduction,
        "net_voc": net_voc,
        "outcomes": outcome_rows,
    }


class SuccessorRegretAB:
    """Read-only V1 x V2 successor comparison.

    Canonical V1 remains the source of candidate collection, deduplication,
    Pareto pruning and automatic routing. V2 only analyzes that Pareto set.
    """

    def __init__(self, runtime: RehydrationLoopRuntime):
        self.runtime = runtime
        self.v1 = SuccessorCompiler(runtime)

    def compare(
        self,
        *,
        loop_id: str,
        expected_state_digest: str,
        completion: dict | None = None,
        candidates: list[Any] | None = None,
        policy: dict | None = None,
        weight_radii: list[float] | None = None,
        analysis_radius: float | None = None,
        information_actions: list[dict[str, Any]] | None = None,
        shadow_prices: dict[str, Any] | None = None,
        min_net_gain: float = 0.0,
    ) -> dict[str, Any]:
        v1 = self.v1.compile(
            loop_id=loop_id,
            expected_state_digest=expected_state_digest,
            completion=completion,
            candidates=candidates,
            policy=policy,
        )

        if v1["status"] in {"TERMINAL", "NO_SUCCESSOR"}:
            return {
                "artifact": ARTIFACT,
                "status": v1["status"],
                "v1": v1,
                "v2": None,
                "calibration_pass": True,
                "laws": [
                    "READ_ONLY_AB != AUTO_ROUTING_MUTATION",
                    "V2_CONSUMES_V1_PARETO_SET",
                ],
            }

        try:
            center, v1_weight_scale = _point_weights_from_v1(v1["policy"])
        except ValueError as exc:
            return {
                "artifact": ARTIFACT,
                "status": "UNSUPPORTED_POLICY_ORIENTATION_HOLD",
                "v1": v1,
                "v2": None,
                "calibration_pass": False,
                "reason": str(exc),
                "laws": [
                    "READ_ONLY_AB != AUTO_ROUTING_MUTATION",
                    "UNSUPPORTED_POLICY_ORIENTATION => HOLD",
                ],
            }

        pareto_ids = set(v1.get("pareto_candidate_ids") or [])
        pareto = [
            deepcopy(row)
            for row in v1.get("candidates") or []
            if row.get("candidate_id") in pareto_ids
        ]
        v1_tie_epsilon = float((v1.get("policy") or {}).get("tie_epsilon", 1e-9))
        tie_epsilon = v1_tie_epsilon / v1_weight_scale

        requested = weight_radii if weight_radii is not None else [0.0, 0.02, 0.05, 0.10, 0.20, 1.0]
        radii = sorted({_finite(radius, name="weight radius") for radius in requested} | {0.0})
        if any(radius < 0.0 for radius in radii):
            raise ValueError("weight radii must be nonnegative")
        if analysis_radius is None:
            analysis_radius = radii[-1]
        analysis_radius = _finite(analysis_radius, name="analysis_radius")
        if analysis_radius < 0.0:
            raise ValueError("analysis_radius must be nonnegative")
        if analysis_radius not in radii:
            radii = sorted(set(radii) | {analysis_radius})

        sensitivity = []
        for radius in radii:
            result = minimax_regret(
                pareto,
                _weight_box(center, radius),
                tie_epsilon=tie_epsilon,
            )
            sensitivity.append(
                {
                    "radius": radius,
                    "status": result["status"],
                    "minimax_regret": result["minimax_regret"],
                    "selection": _v2_semantic_selection(result)[1],
                    "selection_tasks": _v2_selection_tasks(result),
                    "selected": result["selected"],
                    "ties": result["ties"],
                }
            )

        v1_sem = _v1_semantic_selection(v1)
        zero = next(row for row in sensitivity if abs(row["radius"]) <= _EPS)
        zero_sem = (zero["status"], tuple(zero["selection"]))
        calibration_pass = zero_sem == v1_sem

        first_change = None
        for row in sensitivity:
            sem = (row["status"], tuple(row["selection"]))
            if sem != v1_sem:
                first_change = row
                break

        analysis_bounds = _weight_box(center, analysis_radius)
        analysis = minimax_regret(pareto, analysis_bounds, tie_epsilon=tie_epsilon)

        min_net_gain = _finite(min_net_gain, name="min_net_gain")
        action_rows = []
        for action in information_actions or []:
            if not isinstance(action, dict):
                raise ValueError("information_actions must contain objects")
            action_rows.append(
                _evaluate_information_action(
                    pareto,
                    analysis_bounds,
                    action,
                    shadow_prices=shadow_prices,
                    tie_epsilon=tie_epsilon,
                    min_net_gain=min_net_gain,
                )
            )

        positive = [row for row in action_rows if row.get("status") == "POSITIVE_VOC"]
        positive.sort(key=lambda row: (-row["net_voc"], row["action_id"]))
        meta_status = "NO_INFORMATION_ACTIONS"
        meta_selected = None
        meta_ties: list[dict[str, Any]] = []
        if action_rows:
            if not positive:
                meta_status = "STOP_COMPUTING"
            else:
                best = positive[0]["net_voc"]
                meta_ties = [row for row in positive if abs(row["net_voc"] - best) <= tie_epsilon]
                if len(meta_ties) == 1:
                    meta_status = "COMPUTE"
                    meta_selected = meta_ties[0]
                else:
                    meta_status = "META_AMBIGUOUS"

        last_stable_radius = 0.0
        for row in sensitivity:
            sem = (row["status"], tuple(row["selection"]))
            if sem == v1_sem:
                last_stable_radius = row["radius"]
            else:
                break

        return {
            "artifact": ARTIFACT,
            "status": "PASS" if calibration_pass else "CALIBRATION_FAILURE_HOLD",
            "loop_id": loop_id,
            "v1": {
                "status": v1["status"],
                "selection": v1_sem[1],
                "selection_tasks": _v1_selection_tasks(v1),
                "policy": v1["policy"],
                "pareto_candidate_ids": v1.get("pareto_candidate_ids") or [],
            },
            "v2": {
                "benefit_weight_center": center,
                "sensitivity": sensitivity,
                "analysis_radius": analysis_radius,
                "analysis": analysis,
                "first_semantic_change": first_change,
            },
            "calibration_pass": calibration_pass,
            "meta_decision": {
                "status": meta_status,
                "selected": meta_selected,
                "ties": meta_ties,
                "actions": sorted(action_rows, key=lambda row: row["action_id"]),
            },
            "metrics": {
                "v1_pareto_count": len(pareto),
                "largest_tested_stable_radius": last_stable_radius,
                "first_semantic_change_radius": (
                    first_change["radius"] if first_change is not None else None
                ),
                "semantic_change_observed": first_change is not None,
            },
            "laws": [
                "READ_ONLY_AB != AUTO_ROUTING_MUTATION",
                "V2_CONSUMES_V1_PARETO_SET",
                "RADIUS_ZERO_MUST_REPRODUCE_V1_SEMANTICS",
                "ROUTING_ANALYSIS != EVIDENCE",
                "ROUTING_ANALYSIS != AUTHORITY",
                "AUTHORITY_REQUIRED_QUERY != INFORMATION_VOC",
                "NONPOSITIVE_VOC => STOP_OPTIONAL_COMPUTATION",
            ],
        }


REGRET_AB_TOOLS = [
    {
        "name": "athena_rehydration_successor_regret_compare",
        "description": (
            "Read-only A/B preview: run canonical V1 successor routing, then analyze the exact same V1 Pareto "
            "candidate set under bounded-simplex minimax regret and optional one-step value-of-computation. "
            "Never changes next_task, loop state, claims, or execution authority."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["loop_id", "expected_state_digest"],
            "properties": {
                "loop_id": {"type": "string"},
                "expected_state_digest": {"type": "string"},
                "completion": {"type": ["object", "null"]},
                "candidates": {"type": "array", "items": {"type": ["object", "string"]}},
                "policy": {"type": ["object", "null"]},
                "weight_radii": {"type": "array", "items": {"type": "number", "minimum": 0}},
                "analysis_radius": {"type": ["number", "null"], "minimum": 0},
                "information_actions": {"type": "array", "items": {"type": "object"}},
                "shadow_prices": {"type": "object"},
                "min_net_gain": {"type": "number"},
            },
            "additionalProperties": False,
        },
    }
]
REGRET_AB_TOOL_NAMES = {tool["name"] for tool in REGRET_AB_TOOLS}


def install_regret_ab_extension(runtime_cls=RehydrationLoopRuntime) -> None:
    if getattr(runtime_cls, "_athena_successor_regret_ab_v2_registered", False):
        return

    original_call = runtime_cls.call_tool

    def _ab(self) -> SuccessorRegretAB:
        runtime = getattr(self, "_successor_regret_ab_v2", None)
        if runtime is None:
            runtime = SuccessorRegretAB(self)
            self._successor_regret_ab_v2 = runtime
        return runtime

    def call_tool_with_regret_ab(self, name, arguments):
        if name == "athena_rehydration_successor_regret_compare":
            return _ab(self).compare(
                loop_id=arguments["loop_id"],
                expected_state_digest=arguments["expected_state_digest"],
                completion=arguments.get("completion"),
                candidates=arguments.get("candidates"),
                policy=arguments.get("policy"),
                weight_radii=arguments.get("weight_radii"),
                analysis_radius=arguments.get("analysis_radius"),
                information_actions=arguments.get("information_actions"),
                shadow_prices=arguments.get("shadow_prices"),
                min_net_gain=float(arguments.get("min_net_gain", 0.0)),
            )
        return original_call(self, name, arguments)

    runtime_cls.call_tool = call_tool_with_regret_ab
    runtime_cls._athena_successor_regret_ab_v2_registered = True
