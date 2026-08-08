from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


def candidate_id(item: Mapping[str, Any], index: int) -> str:
    for key in ("id", "oid", "cid", "name", "ref"):
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return f"candidate:{index:04d}"


def dependency_graph(candidates: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    rows = list(candidates)
    ids = [candidate_id(item, i) for i, item in enumerate(rows)]
    known = set(ids)
    requires: Dict[str, list[str]] = {}
    missing: Dict[str, list[str]] = {}
    resolved = {candidate_id(item, i): bool(item.get("resolved", False)) for i, item in enumerate(rows)}

    for i, item in enumerate(rows):
        ident = candidate_id(item, i)
        deps = [str(x) for x in (item.get("requires") or [])]
        requires[ident] = deps
        missing[ident] = [dep for dep in deps if dep not in known]

    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            try:
                start = stack.index(node)
                cycle = stack[start:] + [node]
            except ValueError:
                cycle = [node, node]
            if cycle not in cycles:
                cycles.append(cycle)
            return
        visiting.add(node)
        stack.append(node)
        for dep in requires.get(node, []):
            if dep in known:
                dfs(dep)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for ident in ids:
        dfs(ident)

    cycle_nodes = {node for cycle in cycles for node in cycle}
    readiness: Dict[str, Dict[str, Any]] = {}
    for ident in ids:
        unresolved = [dep for dep in requires[ident] if dep in known and not resolved.get(dep, False)]
        blockers = []
        if missing[ident]: blockers.append("missing_dependency")
        if unresolved: blockers.append("unresolved_dependency")
        if ident in cycle_nodes: blockers.append("dependency_cycle")
        readiness[ident] = {
            "ready": not blockers,
            "requires": requires[ident],
            "missing_dependencies": missing[ident],
            "unresolved_dependencies": unresolved,
            "blockers": blockers,
        }

    return {
        "nodes": ids,
        "requires": requires,
        "cycles": cycles,
        "readiness": readiness,
    }
