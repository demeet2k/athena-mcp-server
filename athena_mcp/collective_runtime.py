from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence


COLLECTIVE_FORMS: Dict[str, Dict[str, Any]] = {
    "HIVE": {
        "biological_basis": ["ant_colony", "honeybee_colony", "termite_mound"],
        "use_when": "persistent, divisible, repetitive work with reusable infrastructure",
        "roles": {"builder": 0.40, "verifier": 0.15, "integrator": 0.15, "archivist": 0.10, "sentinel": 0.08, "scout": 0.07, "bridge_builder": 0.05},
    },
    "SWARM": {
        "biological_basis": ["honeybee_scouts", "locust_counterexample", "ant_search"],
        "use_when": "uncertain, exploratory, volatile search where diversity matters",
        "roles": {"scout": 0.40, "verifier": 0.16, "integrator": 0.14, "builder": 0.12, "sentinel": 0.07, "catalyst": 0.06, "bridge_builder": 0.05},
    },
    "PACK": {
        "biological_basis": ["wolf_pack", "lion_pride", "wild_dog_pack", "hyena_clan"],
        "use_when": "one hard, coupled target needing complementary coordinated roles",
        "roles": {"builder": 0.26, "chaser": 0.20, "verifier": 0.17, "flanker": 0.14, "integrator": 0.10, "sentinel": 0.07, "catalyst": 0.06},
    },
    "FLOCK": {
        "biological_basis": ["starling_flock", "goose_formation", "fish_school"],
        "use_when": "rapidly changing shared state where bounded-neighbor coherence beats global synchronization",
        "roles": {"scout": 0.20, "builder": 0.20, "integrator": 0.20, "sentinel": 0.12, "bridge_builder": 0.12, "verifier": 0.10, "catalyst": 0.06},
    },
    "HERD": {
        "biological_basis": ["elephant_herd", "ungulate_herd"],
        "use_when": "large-state migration or transition where invariants and vulnerable core state must survive",
        "roles": {"integrator": 0.22, "archivist": 0.18, "sentinel": 0.18, "builder": 0.16, "verifier": 0.12, "bridge_builder": 0.08, "scout": 0.06},
    },
    "POD": {
        "biological_basis": ["orca_pod", "cetacean_social_learning", "crow_social_memory"],
        "use_when": "longitudinal cultural memory, procedural transfer, and sparse weak-tie integration",
        "roles": {"archivist": 0.22, "builder": 0.18, "integrator": 0.18, "scout": 0.12, "verifier": 0.12, "bridge_builder": 0.10, "sentinel": 0.08},
    },
}

COST_KEYS = ("communication", "duplication", "switching", "synchronization", "congestion", "failure_propagation", "integration", "maintenance")
OUTPUT_KEYS = ("quality", "throughput", "velocity", "resilience", "accuracy", "innovation", "retained_knowledge", "integration")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _unit_map(values: Mapping[str, Any], keys: Iterable[str], defaults: Mapping[str, float] | None = None) -> Dict[str, float]:
    defaults = defaults or {}
    return {k: _clamp(float(values.get(k, defaults.get(k, 0.0)))) for k in keys}


def _largest_remainder(total: int, weights: Mapping[str, float]) -> Dict[str, int]:
    if total <= 0:
        return {k: 0 for k in weights}
    positive = {k: max(0.0, float(v)) for k, v in weights.items()}
    s = sum(positive.values()) or 1.0
    quotas = {k: total * v / s for k, v in positive.items()}
    counts = {k: int(math.floor(v)) for k, v in quotas.items()}
    remaining = total - sum(counts.values())
    order = sorted(quotas, key=lambda k: (quotas[k] - counts[k], positive[k], k), reverse=True)
    for k in order[:remaining]:
        counts[k] += 1
    return counts


@dataclass(frozen=True)
class CollectivePlan:
    form: str
    form_scores: Dict[str, float]
    active_workers: int
    reserve_workers: int
    protected_reserve: int
    roles: Dict[str, int]
    neighbor_k: int
    bridge_budget: int
    quorum_threshold: float
    inhibition_gain: float
    evaporation_rate: float
    marginal_stop_threshold: float
    estimated_net_utility: float
    collective_coordinate: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "form": self.form,
            "form_scores": self.form_scores,
            "active_workers": self.active_workers,
            "reserve_workers": self.reserve_workers,
            "protected_reserve": self.protected_reserve,
            "roles": self.roles,
            "neighbor_k": self.neighbor_k,
            "bridge_budget": self.bridge_budget,
            "quorum_threshold": self.quorum_threshold,
            "inhibition_gain": self.inhibition_gain,
            "evaporation_rate": self.evaporation_rate,
            "marginal_stop_threshold": self.marginal_stop_threshold,
            "estimated_net_utility": self.estimated_net_utility,
            "collective_coordinate": self.collective_coordinate,
        }


class CollectiveRuntime:
    """Deterministic controller for ATHENA collective geometry.

    It does not claim biological equivalence. Animal systems provide design priors;
    this class turns those priors into explicit, inspectable control laws.
    All continuous inputs are normalized to [0, 1].
    """

    SIGNAL_KEYS = (
        "hardness", "uncertainty", "divisibility", "coupling", "volatility", "risk",
        "migration", "repetition", "reuse", "innovation", "latency_sensitivity", "evidence_sensitivity",
    )

    def describe(self) -> Dict[str, Any]:
        return {
            "version": "COLLECTIVE_RUNTIME_V1",
            "forms": COLLECTIVE_FORMS,
            "cost_vector": list(COST_KEYS),
            "output_vector": list(OUTPUT_KEYS),
            "laws": [
                "MAX_GROWTH != MAX_ACTIVITY",
                "MAX_INTEGRATION != MAX_CONNECTIVITY",
                "CONSENSUS_SCORE != EVIDENCE_SCORE",
                "RESERVE_CAPACITY > 0",
                "BUILD_BRIDGE iff EXPECTED_REUSE_SAVINGS > BUILD+MAINTENANCE+LOCKED_CAPACITY",
                "STOP_ADDING_WORKERS when MARGINAL_OUTPUT <= MARGINAL_COORDINATION_COST",
                "STRONG_INTRA_MODULE_TIES + SPARSE_INTER_MODULE_BRIDGES",
                "POSITIVE_RECRUITMENT requires NEGATIVE_INHIBITION and EVAPORATION",
            ],
            "coordinate_schema": {
                "F": "collective form",
                "R": "role allocation",
                "N": "bounded-neighbor topology",
                "D": "demand/task signal field",
                "Q": "quorum/inhibition state",
                "C": "cost vector",
                "O": "output vector",
                "H": "homeostatic health",
                "L": "lineage/native caller coordinate",
            },
        }

    def _signals(self, signals: Mapping[str, Any]) -> Dict[str, float]:
        defaults = {
            "hardness": 0.5, "uncertainty": 0.5, "divisibility": 0.5, "coupling": 0.5,
            "volatility": 0.3, "risk": 0.3, "migration": 0.0, "repetition": 0.2,
            "reuse": 0.5, "innovation": 0.5, "latency_sensitivity": 0.3, "evidence_sensitivity": 0.5,
        }
        return _unit_map(signals, self.SIGNAL_KEYS, defaults)

    def form_scores(self, signals: Mapping[str, Any]) -> Dict[str, float]:
        s = self._signals(signals)
        stability = 1.0 - s["volatility"]
        scores = {
            "HIVE": 0.30*s["divisibility"] + 0.25*s["repetition"] + 0.20*stability + 0.15*s["reuse"] + 0.10*(1-s["migration"]),
            "SWARM": 0.30*s["uncertainty"] + 0.24*s["volatility"] + 0.20*(1-s["coupling"]) + 0.16*s["innovation"] + 0.10*s["divisibility"],
            "PACK": 0.30*s["hardness"] + 0.30*s["coupling"] + 0.18*s["risk"] + 0.12*(1-s["divisibility"]) + 0.10*s["evidence_sensitivity"],
            "FLOCK": 0.28*s["volatility"] + 0.22*(1-s["coupling"]) + 0.18*s["divisibility"] + 0.20*s["latency_sensitivity"] + 0.12*s["reuse"],
            "HERD": 0.42*s["migration"] + 0.20*s["risk"] + 0.14*s["reuse"] + 0.12*s["coupling"] + 0.12*s["evidence_sensitivity"],
            "POD": 0.28*s["reuse"] + 0.22*s["repetition"] + 0.18*s["evidence_sensitivity"] + 0.16*stability + 0.16*(1-s["migration"]),
        }
        return {k: round(_clamp(v), 6) for k, v in scores.items()}

    def _net_utility(self, n: int, max_active: int, s: Mapping[str, float], unit_cost: float) -> float:
        task_mass = 0.45 + 1.20*s["hardness"] + 0.70*s["uncertainty"] + 0.55*s["coupling"] + 0.30*s["risk"]
        parallel_scale = 1.0 + 5.0*s["divisibility"] + 2.0*s["uncertainty"]
        base_benefit = task_mass * (1.0 - math.exp(-n / parallel_scale))
        diversity_lift = 0.45*s["innovation"]*s["uncertainty"] * (math.log1p(n) / math.log1p(max(1, max_active)))
        frac = n / max(1, max_active)
        pair_frac = (n * max(0, n-1)) / max(1, max_active * max(1, max_active-1))
        coordination = (0.55*s["coupling"] + 0.25*s["volatility"] + 0.20*s["latency_sensitivity"]) * pair_frac
        operating = unit_cost * frac
        switching = 0.15*(1-s["repetition"]) * frac
        return base_benefit + diversity_lift - coordination - operating - switching

    def plan(self, signals: Mapping[str, Any], max_workers: int = 12, reserve_fraction: float = 0.17, unit_cost: float = 0.08, lineage: str | None = None) -> Dict[str, Any]:
        if max_workers < 1 or max_workers > 256:
            raise ValueError("max_workers must be in [1,256]")
        reserve_fraction = _clamp(reserve_fraction, 0.0, 0.8)
        if unit_cost < 0:
            raise ValueError("unit_cost must be >= 0")
        s = self._signals(signals)
        scores = self.form_scores(s)
        form = max(scores, key=lambda k: (scores[k], k))
        protected_reserve = min(max_workers - 1, int(math.ceil(max_workers * reserve_fraction))) if max_workers > 1 else 0
        max_active = max(1, max_workers - protected_reserve)
        utilities = [(n, self._net_utility(n, max_active, s, unit_cost)) for n in range(1, max_active + 1)]
        best_n, best_u = max(utilities, key=lambda p: (p[1], -p[0]))
        tolerance = 0.02 * max(1.0, abs(best_u))
        near = [p for p in utilities if best_u - p[1] <= tolerance]
        active = min(n for n, _ in near)
        active_u = next(u for n, u in utilities if n == active)
        reserve_workers = max_workers - active
        roles = _largest_remainder(active, COLLECTIVE_FORMS[form]["roles"])
        neighbor_k = 0 if active <= 1 else min(active - 1, max(1, int(math.ceil(math.log2(active)))))
        bridge_budget = 0 if active <= 2 else max(1, int(math.ceil(math.sqrt(active))) - 1)
        quorum = _clamp(0.50 + 0.22*s["risk"] + 0.18*s["evidence_sensitivity"] + 0.06*s["coupling"], 0.50, 0.94)
        inhibition = _clamp(0.35 + 0.30*s["risk"] + 0.20*s["uncertainty"], 0.25, 0.90)
        evaporation = _clamp(0.02 + 0.18*s["volatility"] + 0.08*s["uncertainty"], 0.01, 0.35)
        stop_threshold = _clamp(unit_cost * (1.0 + 1.2*s["coupling"] + 0.8*s["latency_sensitivity"]), 0.01, 0.60)
        coord = {
            "F": form,
            "R": roles,
            "N": {"active": active, "neighbor_k": neighbor_k, "bridge_budget": bridge_budget, "reserve": reserve_workers},
            "D": s,
            "Q": {"threshold": round(quorum, 6), "inhibition_gain": round(inhibition, 6), "evaporation_rate": round(evaporation, 6)},
            "C": {"unit_cost": round(float(unit_cost), 6), "marginal_stop_threshold": round(stop_threshold, 6)},
            "O": {"estimated_net_utility": round(active_u, 6)},
            "H": {"protected_reserve": protected_reserve, "reserve_fraction_actual": round(reserve_workers/max_workers, 6)},
            "L": lineage or "UNKNOWN",
        }
        return CollectivePlan(
            form=form, form_scores=scores, active_workers=active, reserve_workers=reserve_workers,
            protected_reserve=protected_reserve, roles=roles, neighbor_k=neighbor_k, bridge_budget=bridge_budget,
            quorum_threshold=round(quorum, 6), inhibition_gain=round(inhibition, 6), evaporation_rate=round(evaporation, 6),
            marginal_stop_threshold=round(stop_threshold, 6), estimated_net_utility=round(active_u, 6), collective_coordinate=coord,
        ).as_dict()

    def evaluate(self, configuration: Mapping[str, Any]) -> Dict[str, Any]:
        n = int(configuration.get("workers", 1))
        if n < 1 or n > 256:
            raise ValueError("workers must be in [1,256]")
        degree = int(configuration.get("avg_degree", 0 if n == 1 else min(n-1, math.ceil(math.log2(n)))))
        degree = max(0, min(max(0, n-1), degree))
        vals = _unit_map(configuration, (
            "coupling", "specialization", "diversity", "evidence_quality", "redundancy", "reserve_fraction",
            "reuse", "volatility", "duplication", "switching", "maintenance", "failure_exposure",
        ), {
            "coupling": 0.5, "specialization": 0.5, "diversity": 0.5, "evidence_quality": 0.7,
            "redundancy": 0.2, "reserve_fraction": 0.15, "reuse": 0.5, "volatility": 0.3,
            "duplication": 0.2, "switching": 0.2, "maintenance": 0.2, "failure_exposure": 0.2,
        })
        density = 0.0 if n <= 1 else degree / (n - 1)
        communication = _clamp(density * (0.35 + 0.65*vals["coupling"]))
        synchronization = _clamp(density * vals["coupling"] * (0.55 + 0.45*vals["volatility"]))
        congestion = _clamp(density*density * (0.4 + 0.6*vals["coupling"]))
        failure_propagation = _clamp(density * vals["failure_exposure"] * (1.0 - 0.45*vals["redundancy"]))
        integration_cost = _clamp((1-vals["specialization"])*0.25 + density*0.45 + vals["maintenance"]*0.30)
        costs = {
            "communication": communication, "duplication": vals["duplication"], "switching": vals["switching"],
            "synchronization": synchronization, "congestion": congestion, "failure_propagation": failure_propagation,
            "integration": integration_cost, "maintenance": vals["maintenance"],
        }
        quality = _clamp(0.35*vals["evidence_quality"] + 0.25*vals["specialization"] + 0.20*vals["diversity"] + 0.20*vals["reuse"] - 0.15*vals["duplication"])
        throughput = _clamp((1-math.exp(-n/5.0)) * (0.55 + 0.45*vals["specialization"]) * (1-0.35*synchronization))
        velocity = _clamp(throughput * (1-0.45*communication) * (1-0.35*vals["switching"]))
        resilience = _clamp(0.35*vals["redundancy"] + 0.30*vals["reserve_fraction"] + 0.20*(1-failure_propagation) + 0.15*vals["diversity"])
        accuracy = _clamp(0.70*vals["evidence_quality"] + 0.20*vals["specialization"] + 0.10*(1-failure_propagation))
        innovation = _clamp(0.55*vals["diversity"] + 0.30*(1-synchronization) + 0.15*vals["reuse"])
        retained = _clamp(0.55*vals["reuse"] + 0.25*vals["evidence_quality"] + 0.20*(1-vals["maintenance"]*0.5))
        integration_output = _clamp(0.35*vals["specialization"] + 0.30*vals["diversity"] + 0.25*vals["reuse"] + 0.10*(1-congestion))
        outputs = {
            "quality": quality, "throughput": throughput, "velocity": velocity, "resilience": resilience,
            "accuracy": accuracy, "innovation": innovation, "retained_knowledge": retained, "integration": integration_output,
        }
        cost_mean = sum(costs.values()) / len(costs)
        output_mean = sum(outputs.values()) / len(outputs)
        rgo = output_mean / (1.0 + cost_mean)
        return {
            "workers": n, "avg_degree": degree, "edge_density": round(density, 6),
            "cost_vector": {k: round(v, 6) for k, v in costs.items()},
            "output_vector": {k: round(v, 6) for k, v in outputs.items()},
            "cost_mean": round(cost_mean, 6), "output_mean": round(output_mean, 6),
            "return_on_group_organization": round(rgo, 6),
            "law": "prefer configurations with higher return_on_group_organization, not larger worker count or connectivity",
        }

    def quorum(self, candidates: Sequence[Mapping[str, Any]], risk: float = 0.3, evidence_sensitivity: float = 0.7, inhibition_gain: float | None = None) -> Dict[str, Any]:
        if not candidates:
            raise ValueError("candidates must not be empty")
        risk = _clamp(risk)
        evidence_sensitivity = _clamp(evidence_sensitivity)
        gain = _clamp(inhibition_gain if inhibition_gain is not None else 0.35 + 0.35*risk + 0.15*evidence_sensitivity, 0.0, 1.0)
        threshold = _clamp(0.50 + 0.24*risk + 0.18*evidence_sensitivity, 0.50, 0.95)
        margin_required = _clamp(0.04 + 0.16*risk, 0.04, 0.22)
        scored: List[Dict[str, Any]] = []
        for idx, c in enumerate(candidates):
            cid = str(c.get("id", f"candidate_{idx}"))
            support = _clamp(c.get("support", 0.0))
            evidence = _clamp(c.get("evidence_quality", 0.5))
            inhibition = _clamp(c.get("inhibition", 0.0))
            contradiction = _clamp(c.get("contradiction", 0.0))
            net = _clamp(support * ((1-evidence_sensitivity) + evidence_sensitivity*evidence) - gain*inhibition - 0.5*contradiction, -1.0, 1.0)
            scored.append({"id": cid, "support": support, "evidence_quality": evidence, "inhibition": inhibition, "contradiction": contradiction, "net": round(net, 6)})
        scored.sort(key=lambda x: (x["net"], x["evidence_quality"], x["support"], x["id"]), reverse=True)
        top = scored[0]
        runner = scored[1]["net"] if len(scored) > 1 else -1.0
        margin = top["net"] - runner
        commit = top["net"] >= threshold and margin >= margin_required and top["contradiction"] < 0.5
        return {
            "decision": "COMMIT" if commit else "EXPLORE", "winner": top["id"] if commit else None,
            "threshold": round(threshold, 6), "margin_required": round(margin_required, 6),
            "observed_margin": round(margin, 6), "inhibition_gain": round(gain, 6),
            "ranked_candidates": scored,
            "law": "consensus does not substitute for evidence; inhibition and contradiction can block commitment",
        }

    def stigmergy_update(self, current_score: float, observations: Mapping[str, Any], age: float = 1.0, evaporation_rate: float = 0.08, deposit_gain: float = 0.35) -> Dict[str, Any]:
        current_score = _clamp(current_score)
        age = max(0.0, float(age))
        evaporation_rate = _clamp(evaporation_rate, 0.0, 1.0)
        deposit_gain = _clamp(deposit_gain, 0.0, 1.0)
        o = _unit_map(observations, ("quality", "novelty", "evidence", "reuse", "bridge_value", "downstream_gain", "staleness", "contradiction"), {
            "quality": 0.5, "novelty": 0.5, "evidence": 0.5, "reuse": 0.0, "bridge_value": 0.0,
            "downstream_gain": 0.0, "staleness": 0.0, "contradiction": 0.0,
        })
        rho = math.exp(-evaporation_rate * age)
        evaporated = current_score * rho
        positive = 0.24*o["quality"] + 0.14*o["novelty"] + 0.24*o["evidence"] + 0.14*o["reuse"] + 0.10*o["bridge_value"] + 0.14*o["downstream_gain"]
        penalty = 0.45*o["staleness"] + 0.75*o["contradiction"]
        deposit = _clamp(positive - penalty)
        updated = _clamp(evaporated + deposit_gain * deposit * (1.0 - evaporated))
        return {
            "previous_score": round(current_score, 6), "retention_factor": round(rho, 6),
            "evaporated_score": round(evaporated, 6), "deposit": round(deposit, 6), "updated_score": round(updated, 6),
            "observations": o,
            "law": "successful reuse and evidence reinforce routes; age, staleness and contradiction evaporate them",
        }

    def health(self, metrics: Mapping[str, Any]) -> Dict[str, Any]:
        m = _unit_map(metrics, (
            "context_saturation", "duplication", "latency", "error_rate", "stale_ratio", "contagion",
            "reserve_fraction", "evidence_quality", "bridge_overhead", "coordination_overhead",
        ), {
            "context_saturation": 0.4, "duplication": 0.1, "latency": 0.2, "error_rate": 0.05,
            "stale_ratio": 0.1, "contagion": 0.05, "reserve_fraction": 0.15, "evidence_quality": 0.8,
            "bridge_overhead": 0.15, "coordination_overhead": 0.2,
        })
        checks = {
            "context_saturation": (m["context_saturation"], 0.80, "compact/split context and preserve only reconstructable state"),
            "duplication": (m["duplication"], 0.35, "increase separation and duplicate detection"),
            "latency": (m["latency"], 0.70, "reduce synchronization surface or switch to bounded-neighbor routing"),
            "error_rate": (m["error_rate"], 0.15, "increase verifier/sentinel allocation and quarantine failing path"),
            "stale_ratio": (m["stale_ratio"], 0.30, "evaporate stale attractors and refresh dependencies"),
            "contagion": (m["contagion"], 0.20, "modularize, quarantine, and restrict propagation radius"),
            "bridge_overhead": (m["bridge_overhead"], 0.40, "retire bridges whose maintenance exceeds routing savings"),
            "coordination_overhead": (m["coordination_overhead"], 0.45, "shrink swarm or split into modules"),
        }
        alerts = []
        for name, (value, limit, action) in checks.items():
            if value > limit:
                severity = "CRITICAL" if value > min(1.0, limit + 0.20) else "WARN"
                alerts.append({"metric": name, "value": value, "limit": limit, "severity": severity, "action": action})
        if m["reserve_fraction"] < 0.08:
            alerts.append({"metric": "reserve_fraction", "value": m["reserve_fraction"], "limit": 0.08, "severity": "CRITICAL" if m["reserve_fraction"] < 0.03 else "WARN", "action": "release noncritical work and restore surge capacity"})
        if m["evidence_quality"] < 0.55:
            alerts.append({"metric": "evidence_quality", "value": m["evidence_quality"], "limit": 0.55, "severity": "CRITICAL" if m["evidence_quality"] < 0.35 else "WARN", "action": "raise quorum/evidence thresholds and redirect scouts to stronger sources"})
        critical = sum(1 for a in alerts if a["severity"] == "CRITICAL")
        status = "RED" if critical >= 2 else ("YELLOW" if alerts else "GREEN")
        return {"status": status, "metrics": m, "alerts": alerts, "critical_count": critical, "law": "growth is throttled when homeostatic variables leave safe bands"}
