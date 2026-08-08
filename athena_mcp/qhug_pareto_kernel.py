from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from math import prod
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

VERSION = "QHUG.PARETO-KERNEL.23.2"


@dataclass(frozen=True)
class Patch:
    id: str
    value: float = 0.0
    proof_cost: float = 0.0
    governance: float = 0.0


@dataclass(frozen=True)
class Profile:
    value: float
    count: int
    proof_cost: float
    governance: float

    def add(self, other: "Profile") -> "Profile":
        return Profile(
            self.value + other.value,
            self.count + other.count,
            self.proof_cost + other.proof_cost,
            self.governance + other.governance,
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "patch_count": self.count,
            "proof_cost": self.proof_cost,
            "governance": self.governance,
        }


ZERO = Profile(0.0, 0, 0.0, 0.0)


def _patch_map(patches: Sequence[Mapping[str, Any]]) -> Dict[str, Patch]:
    out: Dict[str, Patch] = {}
    for row in patches:
        pid = str(row["id"])
        if not pid or pid in out:
            raise ValueError(f"invalid or duplicate patch id: {pid!r}")
        out[pid] = Patch(
            id=pid,
            value=float(row.get("value", 0.0)),
            proof_cost=float(row.get("proof_cost", 0.0)),
            governance=float(row.get("governance", 0.0)),
        )
    return out


def _normalize_dependencies(rows: Sequence[Mapping[str, Any]], ids: set[str]) -> Dict[str, Tuple[frozenset[str], ...]]:
    out: Dict[str, Tuple[frozenset[str], ...]] = {}
    for row in rows:
        pid = str(row["patch"])
        if pid not in ids:
            raise ValueError(f"dependency patch not found: {pid}")
        alts = []
        for alt in row.get("alternatives", []):
            dep = frozenset(str(x) for x in alt)
            missing = dep - ids
            if missing:
                raise ValueError(f"dependency references unknown patches: {sorted(missing)}")
            alts.append(dep)
        if not alts:
            alts = [frozenset()]
        out[pid] = tuple(dict.fromkeys(alts))
    return out


def _normalize_conflicts(rows: Sequence[Sequence[str]], ids: set[str]) -> Tuple[Tuple[str, str], ...]:
    out = set()
    for pair in rows:
        if len(pair) != 2:
            raise ValueError("each conflict must contain exactly two patch ids")
        a, b = map(str, pair)
        if a == b:
            raise ValueError("self-conflict is not supported")
        missing = {a, b} - ids
        if missing:
            raise ValueError(f"conflict references unknown patches: {sorted(missing)}")
        out.add(tuple(sorted((a, b))))
    return tuple(sorted(out))


def _constraint_scopes(ids: Iterable[str], conflicts: Sequence[Tuple[str, str]], deps: Mapping[str, Tuple[frozenset[str], ...]]) -> Tuple[frozenset[str], ...]:
    scopes: List[frozenset[str]] = []
    for a, b in conflicts:
        scopes.append(frozenset((a, b)))
    for p, alts in deps.items():
        scope = {p}
        for alt in alts:
            scope.update(alt)
        scopes.append(frozenset(scope))
    return tuple(scopes)


def primal_graph(patch_ids: Iterable[str], conflicts: Sequence[Tuple[str, str]], dependencies: Mapping[str, Tuple[frozenset[str], ...]]) -> Dict[str, set[str]]:
    graph = {p: set() for p in patch_ids}
    for scope in _constraint_scopes(patch_ids, conflicts, dependencies):
        for a, b in combinations(sorted(scope), 2):
            graph[a].add(b)
            graph[b].add(a)
    return graph


def connected_components(graph: Mapping[str, set[str]]) -> List[List[str]]:
    seen = set()
    out: List[List[str]] = []
    for start in sorted(graph):
        if start in seen:
            continue
        q = [start]
        seen.add(start)
        comp = []
        while q:
            u = q.pop()
            comp.append(u)
            for v in graph[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        out.append(sorted(comp))
    return out


def _feasible(selected: set[str], invalid: set[str], conflicts: Sequence[Tuple[str, str]], dependencies: Mapping[str, Tuple[frozenset[str], ...]], neutral_excluded: set[str]) -> bool:
    if selected & invalid:
        return False
    if selected & neutral_excluded:
        return False
    if any(a in selected and b in selected for a, b in conflicts):
        return False
    for p in selected:
        alts = dependencies.get(p)
        if alts is not None and not any(alt <= selected for alt in alts):
            return False
    return True


def _profile(selected: Iterable[str], patch_map: Mapping[str, Patch]) -> Profile:
    rows = [patch_map[p] for p in selected]
    return Profile(
        sum(x.value for x in rows),
        len(rows),
        sum(x.proof_cost for x in rows),
        sum(x.governance for x in rows),
    )


def dominates(a: Profile, b: Profile) -> bool:
    weak = (
        a.value >= b.value
        and a.count <= b.count
        and a.proof_cost <= b.proof_cost
        and a.governance <= b.governance
    )
    strict = (
        a.value > b.value
        or a.count < b.count
        or a.proof_cost < b.proof_cost
        or a.governance < b.governance
    )
    return weak and strict


def pareto_prune(rows: Mapping[Profile, Mapping[str, Any]]) -> Dict[Profile, Dict[str, Any]]:
    keys = list(rows)
    keep: Dict[Profile, Dict[str, Any]] = {}
    for p in keys:
        if any(q != p and dominates(q, p) for q in keys):
            continue
        keep[p] = dict(rows[p])
    return keep


def _local_component(component: Sequence[str], patch_map: Mapping[str, Patch], invalid: set[str], conflicts: Sequence[Tuple[str, str]], dependencies: Mapping[str, Tuple[frozenset[str], ...]], neutral_excluded: set[str], max_component_size: int) -> Dict[str, Any]:
    comp = list(component)
    if len(comp) > max_component_size:
        raise ValueError(f"UNSUPPORTED_COMPONENT_WIDTH size={len(comp)} max_component_size={max_component_size}")
    cset = set(comp)
    local_conflicts = tuple((a, b) for a, b in conflicts if a in cset and b in cset)
    local_deps = {p: alts for p, alts in dependencies.items() if p in cset}
    rows: Dict[Profile, Dict[str, Any]] = {}
    model_count = 0
    for mask in range(1 << len(comp)):
        sel = {comp[i] for i in range(len(comp)) if mask & (1 << i)}
        if not _feasible(sel, invalid & cset, local_conflicts, local_deps, neutral_excluded & cset):
            continue
        model_count += 1
        prof = _profile(sel, patch_map)
        cell = rows.setdefault(prof, {"multiplicity": 0, "witness": tuple(sorted(sel))})
        cell["multiplicity"] += 1
    return {
        "variables": tuple(comp),
        "assignment_work": 1 << len(comp),
        "model_count": model_count,
        "frontier": pareto_prune(rows),
    }


def _convolve(left: Mapping[Profile, Mapping[str, Any]], right: Mapping[Profile, Mapping[str, Any]]) -> Dict[Profile, Dict[str, Any]]:
    out: Dict[Profile, Dict[str, Any]] = {}
    for a, av in left.items():
        for b, bv in right.items():
            c = a.add(b)
            witness = tuple(sorted(set(av.get("witness", ())) | set(bv.get("witness", ()))))
            cell = out.setdefault(c, {"multiplicity": 0, "witness": witness})
            cell["multiplicity"] += int(av.get("multiplicity", 1)) * int(bv.get("multiplicity", 1))
    return pareto_prune(out)


def _score(profile: Profile, policy: Mapping[str, Any]) -> float:
    return (
        profile.value
        - float(policy.get("lambda_patch", 0.0)) * profile.count
        - float(policy.get("mu_proof_cost", 0.0)) * profile.proof_cost
        - float(policy.get("nu_governance", 0.0)) * profile.governance
    )


def solve_kernel(spec: Mapping[str, Any]) -> Dict[str, Any]:
    patch_map = _patch_map(spec.get("patches", []))
    ids = set(patch_map)
    if not ids:
        raise ValueError("patches must be non-empty")
    invalid = {str(x) for x in spec.get("invalid", [])}
    missing = invalid - ids
    if missing:
        raise ValueError(f"invalid references unknown patches: {sorted(missing)}")
    conflicts = _normalize_conflicts(spec.get("conflicts", []), ids)
    dependencies = _normalize_dependencies(spec.get("dependencies", []), ids)
    mode = str(spec.get("mode", "governed")).lower()
    if mode not in {"governed", "neutral"}:
        raise ValueError("mode must be governed or neutral")
    if mode == "neutral":
        if "neutral_excluded" in spec:
            neutral_excluded = {str(x) for x in spec.get("neutral_excluded", [])}
        else:
            neutral_excluded = {x for pair in conflicts for x in pair}
    else:
        neutral_excluded = set()
    if neutral_excluded - ids:
        raise ValueError(f"neutral_excluded references unknown patches: {sorted(neutral_excluded - ids)}")

    graph = primal_graph(ids, conflicts, dependencies)
    comps = connected_components(graph)
    max_component_size = int(spec.get("max_component_size", 20))
    if max_component_size < 1 or max_component_size > 24:
        raise ValueError("max_component_size must be in [1,24]")

    component_results = [
        _local_component(c, patch_map, invalid, conflicts, dependencies, neutral_excluded, max_component_size)
        for c in comps
    ]
    frontier: Dict[Profile, Dict[str, Any]] = {ZERO: {"multiplicity": 1, "witness": ()}}
    for result in component_results:
        frontier = _convolve(frontier, result["frontier"])

    total_models = prod(x["model_count"] for x in component_results)
    assignment_work = sum(x["assignment_work"] for x in component_results)
    policy = spec.get("policy")
    optimum = None
    if policy is not None:
        scored = [(p, _score(p, policy), meta) for p, meta in frontier.items()]
        best = max(x[1] for x in scored)
        ties = [(p, meta) for p, score, meta in scored if abs(score - best) <= 1e-12]
        optimum = {
            "score": best,
            "profile_count": len(ties),
            "model_count": sum(int(meta["multiplicity"]) for _, meta in ties),
            "profiles": [
                {**p.as_dict(), "multiplicity": int(meta["multiplicity"]), "witness": list(meta["witness"])}
                for p, meta in ties
            ],
        }

    return {
        "version": VERSION,
        "mode": mode,
        "patch_count": len(ids),
        "raw_candidate_count": 1 << len(ids),
        "component_count": len(comps),
        "components": [
            {
                "variables": list(x["variables"]),
                "size": len(x["variables"]),
                "assignment_work": x["assignment_work"],
                "model_count": x["model_count"],
                "pareto_vectors": len(x["frontier"]),
            }
            for x in component_results
        ],
        "assignment_work": assignment_work,
        "model_count": total_models,
        "pareto_frontier": [
            {**p.as_dict(), "multiplicity": int(meta["multiplicity"]), "witness": list(meta["witness"])}
            for p, meta in sorted(frontier.items(), key=lambda kv: (-kv[0].value, kv[0].count, kv[0].proof_cost, kv[0].governance))
        ],
        "optimum": optimum,
        "law": "exact disconnected-component enumeration + Pareto-pruned Minkowski convolution; all scalar ties are preserved",
        "boundary": "components above max_component_size fail closed; use a verified tree decomposition/junction solver rather than pretending this component solver scaled",
    }


def analyze_kernel(spec: Mapping[str, Any]) -> Dict[str, Any]:
    patch_map = _patch_map(spec.get("patches", []))
    ids = set(patch_map)
    conflicts = _normalize_conflicts(spec.get("conflicts", []), ids)
    dependencies = _normalize_dependencies(spec.get("dependencies", []), ids)
    graph = primal_graph(ids, conflicts, dependencies)
    comps = connected_components(graph)
    structural_free = []
    constrained = []
    invalid = {str(x) for x in spec.get("invalid", [])}
    neutral = {str(x) for x in spec.get("neutral_excluded", [])}
    conflict_members = {x for pair in conflicts for x in pair}
    dependency_participants = set(dependencies)
    for alts in dependencies.values():
        for alt in alts:
            dependency_participants.update(alt)
    for c in comps:
        p = c[0] if len(c) == 1 else None
        if p and p not in invalid and p not in neutral and p not in conflict_members and p not in dependency_participants:
            structural_free.append(p)
        else:
            constrained.append(c)
    return {
        "version": VERSION,
        "patch_count": len(ids),
        "raw_candidate_count": 1 << len(ids),
        "components": comps,
        "component_sizes": [len(c) for c in comps],
        "structural_free": sorted(structural_free),
        "constrained_components": constrained,
        "component_enumeration_work": sum(1 << len(c) for c in comps),
        "law": "constraint scopes define the primal graph; disconnected components are exact product factors",
    }


def _tree_ok(n: int, edges: Sequence[Sequence[int]]) -> Tuple[bool, List[set[int]]]:
    if n == 0:
        return False, []
    adj = [set() for _ in range(n)]
    if len(edges) != n - 1:
        return False, adj
    for row in edges:
        if len(row) != 2:
            return False, adj
        a, b = map(int, row)
        if a == b or min(a, b) < 0 or max(a, b) >= n:
            return False, adj
        adj[a].add(b); adj[b].add(a)
    seen = {0}; q = [0]
    while q:
        u = q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen) == n, adj


def verify_decomposition(spec: Mapping[str, Any]) -> Dict[str, Any]:
    patch_map = _patch_map(spec.get("patches", []))
    ids = set(patch_map)
    conflicts = _normalize_conflicts(spec.get("conflicts", []), ids)
    dependencies = _normalize_dependencies(spec.get("dependencies", []), ids)
    scopes = list(_constraint_scopes(ids, conflicts, dependencies))
    bags = [set(map(str, row)) for row in spec.get("bags", [])]
    if not bags:
        raise ValueError("bags must be non-empty")
    if any(b - ids for b in bags):
        raise ValueError("bags contain unknown patch ids")
    edges = spec.get("bag_edges")
    if edges is None:
        edges = [[i, i + 1] for i in range(len(bags) - 1)]
    tree_ok, adj = _tree_ok(len(bags), edges)

    uncovered = [sorted(scope) for scope in scopes if not any(scope <= bag for bag in bags)]
    running_fail = []
    if tree_ok:
        for var in sorted(ids):
            nodes = [i for i, bag in enumerate(bags) if var in bag]
            if not nodes:
                running_fail.append(var); continue
            allowed = set(nodes); seen = {nodes[0]}; q = [nodes[0]]
            while q:
                u = q.pop()
                for v in adj[u]:
                    if v in allowed and v not in seen:
                        seen.add(v); q.append(v)
            if seen != allowed:
                running_fail.append(var)

    graph = primal_graph(ids, conflicts, dependencies)
    clique_lower = 0
    clique_bags = []
    for i, bag in enumerate(bags):
        clique = all(b in graph[a] for a, b in combinations(sorted(bag), 2))
        if clique:
            clique_lower = max(clique_lower, len(bag) - 1)
            clique_bags.append(i)
    width = max(len(b) - 1 for b in bags)
    valid = tree_ok and not uncovered and not running_fail
    return {
        "version": VERSION,
        "valid": valid,
        "tree": tree_ok,
        "factor_coverage": not uncovered,
        "uncovered_scopes": uncovered,
        "running_intersection": not running_fail,
        "running_intersection_failures": running_fail,
        "width_upper_bound": width,
        "clique_lower_bound": clique_lower,
        "exact_treewidth_certified": valid and clique_lower == width,
        "clique_bag_indices": clique_bags,
        "bag_count": len(bags),
        "max_bag_size": width + 1,
        "law": "valid decomposition proves treewidth <= width; a clique of size width+1 proves treewidth >= width",
    }


class QhugParetoKernelRuntime:
    def analyze(self, args: Mapping[str, Any]) -> Dict[str, Any]:
        return analyze_kernel(args)

    def solve(self, args: Mapping[str, Any]) -> Dict[str, Any]:
        return solve_kernel(args)

    def verify_decomposition(self, args: Mapping[str, Any]) -> Dict[str, Any]:
        return verify_decomposition(args)

    def describe(self) -> Dict[str, Any]:
        return {
            "version": VERSION,
            "tools": ["athena_qhug_kernel_analyze", "athena_qhug_pareto_solve", "athena_qhug_decomposition_verify"],
            "guarantees": ["exact supported-component feasibility", "Pareto dominance pruning", "all-tie scalar argmax", "tree-decomposition verification"],
            "boundaries": ["Boolean patch kernels only", "additive four-resource profile", "large connected components require verified junction decomposition"],
        }
