from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Mapping, Sequence


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


class CollectiveGrowthRuntime:
    """Second-layer collective growth operators.

    These operators act on allocation, infrastructure, topology transitions,
    scoped alarm transport, and knowledge lifecycle. They are deterministic and
    advisory until their results are persisted through canonical ATHENA tools.
    """

    def describe(self) -> Dict[str, Any]:
        return {
            "version": "COLLECTIVE_GROWTH_V1",
            "operators": ["demand_allocate", "bridge_account", "restructure", "dependency_alarm", "artifact_lifecycle"],
            "laws": [
                "ALLOCATE by demand*fit*available_capacity, not equal participation",
                "BUILD_BRIDGE iff expected saved work exceeds build+maintenance+locked capacity",
                "FISSION when coordination/contagion pressure dominates cohesion",
                "FUSE when complementarity/shared dependencies dominate identity conflict",
                "ALARMS propagate only through caller-declared dependency/influence edges",
                "PRUNING preserves lineage/reference even when active priority is removed",
            ],
        }

    def demand_allocate(self, tasks: Sequence[Mapping[str, Any]], workers: Sequence[Mapping[str, Any]], max_assignments_per_worker: int = 1, alpha: float = 1.0, beta: float = 1.0) -> Dict[str, Any]:
        if not tasks: raise ValueError("tasks must not be empty")
        if not workers: raise ValueError("workers must not be empty")
        if max_assignments_per_worker < 1 or max_assignments_per_worker > 16: raise ValueError("max_assignments_per_worker must be in [1,16]")
        alpha = max(0.0, float(alpha)); beta = max(0.0, float(beta))
        normalized_tasks = []
        for i, task in enumerate(tasks):
            tid = str(task.get("id", f"task_{i}"))
            utility = _clamp(task.get("utility", 0.5)); gap = _clamp(task.get("gap", 0.5)); bridge = _clamp(task.get("bridge_value", 0.5)); saturation = _clamp(task.get("saturation", 0.0)); urgency = _clamp(task.get("urgency", 0.5))
            demand = utility * gap * max(0.05, bridge) * (1.0 - saturation) * (0.5 + 0.5*urgency)
            required = {str(x) for x in task.get("required_capabilities", [])}
            normalized_tasks.append({"id": tid, "demand": demand, "required": required, "raw": dict(task)})
        worker_state = {}
        for i, worker in enumerate(workers):
            wid = str(worker.get("id", f"worker_{i}"))
            worker_state[wid] = {"capabilities": {str(x) for x in worker.get("capabilities", [])}, "load": _clamp(worker.get("load", 0.0)), "assignments": 0}
        assignments: List[Dict[str, Any]] = []; unfilled: List[Dict[str, Any]] = []
        for task in sorted(normalized_tasks, key=lambda t: (t["demand"], t["id"]), reverse=True):
            candidates = []
            for wid, ws in worker_state.items():
                if ws["assignments"] >= max_assignments_per_worker: continue
                req = task["required"]; fit = 1.0 if not req else len(req & ws["capabilities"]) / len(req); availability = 1.0 - ws["load"]
                score = (task["demand"] ** alpha) * (max(0.01, fit) ** beta) * availability
                candidates.append((score, fit, availability, wid))
            if not candidates:
                unfilled.append({"task": task["id"], "reason": "NO_CAPACITY", "demand": round(task["demand"], 6)}); continue
            score, fit, availability, wid = max(candidates, key=lambda x: (x[0], x[1], x[2], x[3]))
            if fit <= 0.0:
                unfilled.append({"task": task["id"], "reason": "NO_CAPABILITY_FIT", "demand": round(task["demand"], 6)}); continue
            worker_state[wid]["assignments"] += 1
            assignments.append({"task": task["id"], "worker": wid, "score": round(score, 6), "demand": round(task["demand"], 6), "fit": round(fit, 6), "availability": round(availability, 6)})
        return {"assignments": assignments, "unfilled": unfilled, "worker_load_slots": {wid: ws["assignments"] for wid, ws in sorted(worker_state.items())}, "law": "allocate by demand × capability fit × available capacity; do not maximize participation"}

    def bridge_account(self, bridge: Mapping[str, Any]) -> Dict[str, Any]:
        uses = max(0.0, float(bridge.get("expected_future_uses", 0.0))); route_saving = max(0.0, float(bridge.get("route_saving_per_use", 0.0))); quality_gain = max(0.0, float(bridge.get("quality_gain", 0.0))); resilience_gain = max(0.0, float(bridge.get("resilience_gain", 0.0)))
        build_cost = max(0.0, float(bridge.get("build_cost", 0.0))); maintenance_cost = max(0.0, float(bridge.get("maintenance_cost", 0.0))); locked_capacity = max(0.0, float(bridge.get("locked_capacity_cost", 0.0)))
        expected_value = uses*route_saving + quality_gain + resilience_gain; total_cost = build_cost + maintenance_cost + locked_capacity; net = expected_value - total_cost; roi = net / total_cost if total_cost > 0 else (float("inf") if expected_value > 0 else 0.0)
        return {"decision": "BUILD" if net > 0 else "DO_NOT_BUILD", "expected_value": round(expected_value, 6), "total_cost": round(total_cost, 6), "net_value": round(net, 6), "roi": "INF" if roi == float("inf") else round(roi, 6), "break_even_uses": 0.0 if route_saving <= 0 and total_cost <= quality_gain+resilience_gain else (None if route_saving <= 0 else round(max(0.0, (total_cost-quality_gain-resilience_gain)/route_saving), 6)), "law": "infrastructure must repay build, maintenance, and immobilized capacity"}

    def restructure(self, metrics: Mapping[str, Any]) -> Dict[str, Any]:
        m = {k: _clamp(metrics.get(k, d)) for k, d in {"coordination_overhead": .2, "contagion": .1, "size_pressure": .3, "internal_cohesion": .7, "complementarity": .3, "duplicate_work": .2, "shared_dependencies": .3, "interface_maturity": .5, "identity_conflict": .2}.items()}
        fission = _clamp(.35*m["coordination_overhead"] + .25*m["contagion"] + .20*m["size_pressure"] + .20*(1-m["internal_cohesion"]))
        fusion = _clamp(.30*m["complementarity"] + .25*m["duplicate_work"] + .25*m["shared_dependencies"] + .20*m["interface_maturity"] - .25*m["identity_conflict"])
        if fission >= .62 and fission >= fusion + .08: decision = "FISSION"; action = "split along strongest internal modular boundary; preserve sparse bridge and shared invariants"
        elif fusion >= .62 and fusion >= fission + .08: decision = "FUSE"; action = "merge overlapping work surfaces; preserve distinct role/culture submodules where useful"
        else: decision = "HOLD"; action = "retain topology; improve routing or measurement before structural change"
        return {"decision": decision, "fission_score": round(fission, 6), "fusion_score": round(fusion, 6), "metrics": m, "action": action, "law": "topology is adaptive: split overload, merge redundant complementary structures, otherwise hold"}

    def dependency_alarm(self, seeds: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]], max_hops: int = 6, hop_decay: float = 0.82, threshold: float = 0.08) -> Dict[str, Any]:
        if not seeds: raise ValueError("seeds must not be empty")
        if max_hops < 0 or max_hops > 64: raise ValueError("max_hops must be in [0,64]")
        hop_decay = _clamp(hop_decay); threshold = _clamp(threshold); adjacency = defaultdict(list)
        for e in edges:
            src = str(e["src"]); dst = str(e["dst"]); weight = _clamp(e.get("weight", 1.0)); relation = str(e.get("relation", "dependency")); adjacency[src].append((dst, weight, relation))
        best: Dict[str, float] = {}; witness: Dict[str, Dict[str, Any]] = {}; q = deque()
        for s in seeds:
            node = str(s["node"]); sev = _clamp(s.get("severity", 1.0))
            if sev >= threshold: best[node] = max(best.get(node, 0.0), sev); witness[node] = {"from": None, "relation": "SEED", "hop": 0}; q.append((node, sev, 0))
        while q:
            node, sev, hop = q.popleft()
            if hop >= max_hops: continue
            for dst, weight, relation in adjacency.get(node, []):
                nxt = sev * weight * hop_decay
                if nxt < threshold or nxt <= best.get(dst, -1.0) + 1e-12: continue
                best[dst] = nxt; witness[dst] = {"from": node, "relation": relation, "hop": hop+1}; q.append((dst, nxt, hop+1))
        impacted = [{"node": node, "severity": round(sev, 6), **witness[node]} for node, sev in sorted(best.items(), key=lambda x: (-x[1], x[0]))]
        return {"impacted": impacted, "count": len(impacted), "max_hops": max_hops, "hop_decay": round(hop_decay, 6), "threshold": round(threshold, 6), "law": "propagate alarms only over explicit caller-supplied influence/dependency edges with decay"}

    def artifact_lifecycle(self, artifacts: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not artifacts: raise ValueError("artifacts must not be empty")
        decisions = []; counts = defaultdict(int)
        for i, a in enumerate(artifacts):
            aid = str(a.get("id", f"artifact_{i}")); reuse = _clamp(a.get("reuse", 0.0)); novelty = _clamp(a.get("novelty", 0.0)); evidence = _clamp(a.get("evidence", 0.5)); age = _clamp(a.get("age", 0.5)); superseded = bool(a.get("superseded", False)); dependents = max(0, int(a.get("downstream_dependents", 0))); critical_lineage = bool(a.get("critical_lineage", False))
            if critical_lineage or dependents > 0: decision = "KEEP_REFERENCE"; reason = "lineage/dependency requires addressable retention"
            elif superseded and reuse < .25 and novelty < .25: decision = "PRUNE_REFERENCE"; reason = "superseded low-reuse low-novelty artifact; remove active priority but preserve tombstone/reference"
            elif reuse < .20 and novelty < .30 and age > .65: decision = "DORMANT"; reason = "low current utility; hibernate rather than erase"
            elif evidence < .35: decision = "QUARANTINE"; reason = "weak evidence; retain for audit but exclude from authoritative routing"
            else: decision = "KEEP_ACTIVE"; reason = "still contributes reuse, novelty, evidence, or future optionality"
            counts[decision] += 1; decisions.append({"id": aid, "decision": decision, "reason": reason})
        return {"decisions": decisions, "counts": dict(sorted(counts.items())), "law": "death removes active routing privilege, not lineage; hibernate before erasing uncertain future value"}
