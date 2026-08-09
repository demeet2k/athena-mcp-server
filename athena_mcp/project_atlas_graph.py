from __future__ import annotations

import ast
import heapq
import json
import math
import tomllib
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable

from .identity import digest
from .project_atlas import _git

GRAPH_SCHEMA = "ATHENA.KC144.PROJECT_RELATION_GRAPH.v3"
GRAPH_VERSION = "ATHENA.PROJECT_ATLAS.RELATION_GRAPH.V3"
GRAPH_ID_PREFIX = "PATLASG3."
MAX_QUERY_LIMIT = 100
MAX_EXPANSIONS = 10000
MAX_DEPTH = 128

STRUCTURAL_EDGE_KINDS = {
    "DIR_CONTAINS",
    "DIR_PARENT_OF",
    "PY_IMPORTS",
    "PY_RELATIVE_IMPORTS",
    "SAME_BLOB_ALIAS",
    "EXACT_PATH_REFERENCE",
}
GEOMETRIC_EDGE_KINDS = {"KC144_GRID_ADJACENT"}
EDGE_KINDS = STRUCTURAL_EDGE_KINDS | GEOMETRIC_EDGE_KINDS

GRAPH_LAWS = [
    "EDGE != CLAIM_OF_SEMANTIC_EQUIVALENCE",
    "KC144_GRID_ADJACENT != DEPENDS_ON",
    "SAME_BLOB_ALIAS != SAME_OBJECT",
    "IMPORT_STRING != RESOLVED_LOCAL_IMPORT",
    "UNRESOLVED_IMPORT -> CONSERVE_UNKNOWN",
    "AMBIGUOUS_EDGE_TARGET -> HOLD_EDGE",
    "GRAPH_DIGEST_REQUIRES_EXACT_SNAPSHOT",
    "GRAPH_QUERY != PROMOTION_AUTHORITY",
    "PATH_COST != TRUTH",
    "ROUTE != EXECUTION",
    "EDGE_CLASS_CHANGE_REQUIRES_GRAPH_SCHEMA_BUMP",
]


def _plane(record: dict, default_plane: str) -> str:
    return str(record.get("source") or default_plane)


def _frontier(record: dict, default_plane: str) -> tuple[str, str, str]:
    native = record["native"]
    return _plane(record, default_plane), native["repo"], native["head"]


def _vertex_receipt(record: dict, default_plane: str) -> dict:
    native = record["native"]
    return {
        "poid": record["poid"],
        "plane": _plane(record, default_plane),
        "repo": native["repo"],
        "head": native["head"],
        "path": native["path"],
        "git_type": native["git_type"],
        "object_sha": native["object_sha"],
        "project_gid": record["project_kc144"]["gid"],
        "reference_gid": record["kc144_reference"]["gid"],
        "return_uri": record["return"]["uri"],
    }


def _edge(
    *,
    snapshot_id: str,
    kind: str,
    src: dict,
    dst: dict,
    default_plane: str,
    extractor: str,
    evidence: str,
    witness: dict,
    confidence: float = 1.0,
    authority: str = "STRUCTURAL_OBSERVATION",
    loss: str = "NONE_FOR_RELATION_AS_STATED",
) -> dict:
    if kind not in EDGE_KINDS:
        raise ValueError(f"unknown Project Relation Graph edge kind: {kind}")
    src_v, dst_v = _vertex_receipt(src, default_plane), _vertex_receipt(dst, default_plane)
    plane = src_v["plane"] if src_v["plane"] == dst_v["plane"] else "cross_plane"
    basis = {
        "schema": GRAPH_SCHEMA,
        "snapshot_id": snapshot_id,
        "kind": kind,
        "src_poid": src_v["poid"],
        "dst_poid": dst_v["poid"],
        "plane": plane,
        "extractor": extractor,
        "evidence": evidence,
        "witness": witness,
    }
    return {
        "edge_id": "PEDGE." + digest(basis, 24),
        "kind": kind,
        "src_poid": src_v["poid"],
        "dst_poid": dst_v["poid"],
        "plane": plane,
        "extractor": extractor,
        "evidence": evidence,
        "witness": witness,
        "confidence": confidence,
        "authority": authority,
        "loss": loss,
        "snapshot_id": snapshot_id,
        "return": {
            "src": src_v["return_uri"],
            "dst": dst_v["return_uri"],
            "law": "edge RETURN preserves both exact Project Atlas endpoint witnesses",
        },
    }


def _module_name(path: str) -> str | None:
    if not path.endswith(".py"):
        return None
    pp = PurePosixPath(path)
    if pp.name == "__init__.py":
        return ".".join(pp.parent.parts) if str(pp.parent) != "." else ""
    return ".".join(pp.with_suffix("").parts)


def _package_name(path: str) -> str:
    module = _module_name(path) or ""
    if path.endswith("/__init__.py") or path == "__init__.py":
        return module
    return module.rsplit(".", 1)[0] if "." in module else ""


def _relative_base(package: str, level: int, module: str | None) -> str | None:
    parts = [p for p in package.split(".") if p]
    climb = max(0, level - 1)
    if climb > len(parts):
        return None
    kept = parts[: len(parts) - climb] if climb else parts
    if module:
        kept += module.split(".")
    return ".".join(kept)


def _choose_local_module(module_index: dict[str, list[dict]], names: Iterable[str]) -> tuple[dict | None, list[str]]:
    attempted: list[str] = []
    for name in names:
        if not name:
            continue
        attempted.append(name)
        candidates = module_index.get(name, [])
        if len(candidates) == 1:
            return candidates[0], attempted
        if len(candidates) > 1:
            return None, attempted
        # `import a.b.c` may be locally represented only by a or a.b.
        parts = name.split(".")
        for cut in range(len(parts) - 1, 0, -1):
            parent = ".".join(parts[:cut])
            if parent in attempted:
                continue
            attempted.append(parent)
            candidates = module_index.get(parent, [])
            if len(candidates) == 1:
                return candidates[0], attempted
            if len(candidates) > 1:
                return None, attempted
    return None, attempted


def _scalar_strings(value) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, val in value.items():
            yield from _scalar_strings(key)
            yield from _scalar_strings(val)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _scalar_strings(item)


def _exact_reference_strings(path: str, text: str) -> list[tuple[str, str]]:
    """Return exact scalar path values only; never substring or similarity matches."""
    suffix = PurePosixPath(path).suffix.lower()
    out: list[tuple[str, str]] = []
    try:
        if suffix == ".py":
            tree = ast.parse(text, filename=path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    out.append((node.value, f"python_ast_constant:{getattr(node, 'lineno', 0)}"))
        elif suffix == ".json":
            value = json.loads(text)
            out.extend((s, "json_scalar") for s in _scalar_strings(value))
        elif suffix == ".toml":
            value = tomllib.loads(text)
            out.extend((s, "toml_scalar") for s in _scalar_strings(value))
    except (SyntaxError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError):
        return []
    return out


def git_blob_reader(root: str | Path) -> Callable[[dict], str]:
    root = Path(root).resolve()

    def read(record: dict) -> str:
        native = record["native"]
        if native["git_type"] != "blob":
            raise ValueError("blob reader requires a Git blob record")
        raw = _git(root, "cat-file", "blob", native["object_sha"], binary=True)
        if not isinstance(raw, bytes):
            raw = raw.encode("utf-8")
        return raw.decode("utf-8")

    return read


@dataclass(frozen=True)
class GraphBuildOptions:
    default_plane: str = "configured_git"
    include_hierarchy: bool = True
    include_python_imports: bool = True
    include_blob_aliases: bool = True
    include_exact_path_references: bool = True
    include_geometric: bool = False


def compile_project_relation_graph(
    atlas: dict,
    *,
    snapshot_id: str,
    root: str | Path | None = None,
    blob_reader: Callable[[dict], str] | None = None,
    options: GraphBuildOptions | None = None,
) -> "ProjectRelationGraph":
    if not isinstance(snapshot_id, str) or not snapshot_id.startswith("PATLASV2."):
        raise ValueError("Project Relation Graph V3 requires an exact PATLASV2 snapshot_id")
    options = options or GraphBuildOptions()
    records = list(atlas.get("records") or [])
    records.sort(key=lambda r: (r["poid"], _plane(r, options.default_plane)))
    by_poid = {r["poid"]: r for r in records}
    if len(by_poid) != len(records):
        raise ValueError("Project Relation Graph requires unique POIDs")
    reader = blob_reader or (git_blob_reader(root) if root is not None else None)

    edges: list[dict] = []
    holds: list[dict] = []
    unresolved_imports: list[dict] = []

    def add(**kwargs):
        edges.append(_edge(snapshot_id=snapshot_id, default_plane=options.default_plane, **kwargs))

    # Exact Git tree hierarchy.  No synthetic root object is invented.
    if options.include_hierarchy:
        by_frontier_path_type: dict[tuple[str, str, str, str, str], dict] = {}
        for rec in records:
            plane, repo, head = _frontier(rec, options.default_plane)
            native = rec["native"]
            by_frontier_path_type[(plane, repo, head, native["path"], native["git_type"])] = rec
        for child in records:
            path = child["native"]["path"]
            if "/" not in path:
                continue
            parent_path = str(PurePosixPath(path).parent)
            plane, repo, head = _frontier(child, options.default_plane)
            parent = by_frontier_path_type.get((plane, repo, head, parent_path, "tree"))
            if not parent:
                holds.append({
                    "status": "HOLD_EDGE",
                    "kind": "DIR_CONTAINS",
                    "src_poid": child["poid"],
                    "reason": "exact parent tree record unavailable",
                    "parent_path": parent_path,
                })
                continue
            witness = {"repo": repo, "head": head, "parent_path": parent_path, "child_path": path}
            add(kind="DIR_CONTAINS", src=parent, dst=child, extractor="git_tree_hierarchy_v1", evidence="EXACT_GIT_TREE", witness=witness)
            add(kind="DIR_PARENT_OF", src=child, dst=parent, extractor="git_tree_hierarchy_v1", evidence="EXACT_GIT_TREE", witness=witness)

    # Content aliases are explicit aliases, never object collapse.
    if options.include_blob_aliases:
        groups: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
        for rec in records:
            native = rec["native"]
            if native["git_type"] == "blob":
                plane, repo, head = _frontier(rec, options.default_plane)
                groups[(plane, repo, head, native["object_sha"])].append(rec)
        for (plane, repo, head, object_sha), group in sorted(groups.items()):
            group.sort(key=lambda r: r["poid"])
            if len(group) < 2:
                continue
            anchor = group[0]
            for other in group[1:]:
                witness = {"repo": repo, "head": head, "object_sha": object_sha, "paths": sorted([anchor["native"]["path"], other["native"]["path"]])}
                for src, dst in ((anchor, other), (other, anchor)):
                    add(kind="SAME_BLOB_ALIAS", src=src, dst=dst, extractor="git_object_alias_v1", evidence="EXACT_GIT_OBJECT_SHA", witness=witness, authority="CONTENT_IDENTITY_ONLY", loss="DISTINCT_PATH_OBJECTS_PRESERVED")

    # Exact local Python imports are AST parsed and frontier-scoped.
    if options.include_python_imports:
        module_indexes: dict[tuple[str, str, str], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
        for rec in records:
            native = rec["native"]
            if native["git_type"] != "blob":
                continue
            module = _module_name(native["path"])
            if module is not None:
                module_indexes[_frontier(rec, options.default_plane)][module].append(rec)
        for rec in records:
            path = rec["native"]["path"]
            if rec["native"]["git_type"] != "blob" or not path.endswith(".py"):
                continue
            if reader is None:
                holds.append({"status": "HOLD_EDGE", "kind": "PY_IMPORTS", "src_poid": rec["poid"], "reason": "exact blob reader unavailable"})
                continue
            try:
                text = reader(rec)
                tree = ast.parse(text, filename=path)
            except (UnicodeDecodeError, SyntaxError, ValueError, RuntimeError) as exc:
                holds.append({"status": "HOLD_EDGE", "kind": "PY_IMPORTS", "src_poid": rec["poid"], "reason": f"source unavailable or unparsable: {type(exc).__name__}"})
                continue
            frontier = _frontier(rec, options.default_plane)
            module_index = module_indexes[frontier]
            package = _package_name(path)
            for node in ast.walk(tree):
                requests: list[tuple[str, list[str], str]] = []
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        requests.append((alias.name, [alias.name], "PY_IMPORTS"))
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        base = _relative_base(package, node.level, node.module)
                        for alias in node.names:
                            names = [] if base is None else ([base] if alias.name == "*" else [f"{base}.{alias.name}" if base else alias.name, base])
                            requests.append(("." * node.level + (node.module or "") + (f":{alias.name}" if alias.name else ""), names, "PY_RELATIVE_IMPORTS"))
                    else:
                        base = node.module or ""
                        for alias in node.names:
                            names = [base] if alias.name == "*" else [f"{base}.{alias.name}" if base else alias.name, base]
                            requests.append((f"{base}:{alias.name}", names, "PY_IMPORTS"))
                for request, names, kind in requests:
                    target, attempted = _choose_local_module(module_index, names)
                    if target is None:
                        unresolved_imports.append({
                            "src_poid": rec["poid"],
                            "path": path,
                            "request": request,
                            "attempted_local_modules": attempted,
                            "line": getattr(node, "lineno", None),
                            "standing": "UNRESOLVED_EXTERNAL_OR_LOCAL_UNKNOWN",
                        })
                        continue
                    if target["poid"] == rec["poid"]:
                        continue
                    witness = {
                        "source_path": path,
                        "target_path": target["native"]["path"],
                        "request": request,
                        "attempted_local_modules": attempted,
                        "line": getattr(node, "lineno", None),
                    }
                    add(kind=kind, src=rec, dst=target, extractor="python_ast_import_resolver_v1", evidence="PYTHON_AST+EXACT_LOCAL_MODULE_INDEX", witness=witness)

    # Exact path references: scalar equality only, no substring/similarity inference.
    if options.include_exact_path_references:
        paths_by_frontier: dict[tuple[str, str, str], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
        for rec in records:
            paths_by_frontier[_frontier(rec, options.default_plane)][rec["native"]["path"]].append(rec)
        for rec in records:
            native = rec["native"]
            if native["git_type"] != "blob" or reader is None:
                continue
            if PurePosixPath(native["path"]).suffix.lower() not in {".py", ".json", ".toml"}:
                continue
            try:
                text = reader(rec)
            except (UnicodeDecodeError, ValueError, RuntimeError):
                continue
            for raw_value, extractor_witness in _exact_reference_strings(native["path"], text):
                value = raw_value.replace("\\", "/")
                while value.startswith("./"):
                    value = value[2:]
                candidates = paths_by_frontier[_frontier(rec, options.default_plane)].get(value, [])
                if len(candidates) != 1:
                    if len(candidates) > 1:
                        holds.append({"status": "HOLD_EDGE", "kind": "EXACT_PATH_REFERENCE", "src_poid": rec["poid"], "reason": "ambiguous exact path target", "value": value, "candidate_poids": sorted(c["poid"] for c in candidates)})
                    continue
                target = candidates[0]
                if target["poid"] == rec["poid"]:
                    continue
                add(
                    kind="EXACT_PATH_REFERENCE",
                    src=rec,
                    dst=target,
                    extractor="exact_scalar_path_reference_v1",
                    evidence="EXACT_SCALAR_PATH+UNIQUE_FRONTIER_TARGET",
                    witness={"source_path": native["path"], "target_path": value, "scalar_witness": extractor_witness},
                    authority="REFERENCE_OBSERVATION",
                    loss="REFERENCE_DOES_NOT_IMPLY_RUNTIME_DEPENDENCY",
                )

    # Optional coordinate overlay.  It is deliberately a separate, explicitly geometric edge class.
    if options.include_geometric:
        by_station: dict[tuple[str, str, str, int], list[dict]] = defaultdict(list)
        for rec in records:
            by_station[(*_frontier(rec, options.default_plane), rec["project_kc144"]["gid"])].append(rec)
        for rec in records:
            plane, repo, head = _frontier(rec, options.default_plane)
            src_gid = rec["project_kc144"]["gid"]
            for direction, dst_gid in sorted((rec.get("grid_neighbors") or {}).items()):
                if dst_gid is None:
                    continue
                for target in sorted(by_station.get((plane, repo, head, dst_gid), []), key=lambda r: r["poid"]):
                    if target["poid"] == rec["poid"]:
                        continue
                    add(
                        kind="KC144_GRID_ADJACENT",
                        src=rec,
                        dst=target,
                        extractor="project_kc144_grid_v1",
                        evidence="KC144_GEOMETRIC_PROJECTION",
                        witness={"src_gid": src_gid, "dst_gid": dst_gid, "direction": direction},
                        authority="COORDINATE_ONLY",
                        loss="GEOMETRIC_ADJACENCY_HAS_NO_DEPENDENCY_OR_SEMANTIC_EQUIVALENCE CLAIM",
                    )

    # Canonical deduplication makes enumeration order irrelevant.
    unique_edges = {edge["edge_id"]: edge for edge in edges}
    edges = sorted(unique_edges.values(), key=lambda e: (e["kind"], e["src_poid"], e["dst_poid"], e["edge_id"]))
    holds.sort(key=lambda h: json.dumps(h, sort_keys=True, separators=(",", ":")))
    unresolved_imports.sort(key=lambda h: json.dumps(h, sort_keys=True, separators=(",", ":")))
    return ProjectRelationGraph(
        snapshot_id=snapshot_id,
        records=records,
        edges=edges,
        holds=holds,
        unresolved_imports=unresolved_imports,
        default_plane=options.default_plane,
        options=options,
    )


class ProjectRelationGraph:
    def __init__(
        self,
        *,
        snapshot_id: str,
        records: list[dict],
        edges: list[dict],
        holds: list[dict] | None = None,
        unresolved_imports: list[dict] | None = None,
        default_plane: str = "configured_git",
        options: GraphBuildOptions | None = None,
    ):
        self.snapshot_id = snapshot_id
        self.default_plane = default_plane
        self.options = options or GraphBuildOptions(default_plane=default_plane)
        self.records = sorted(records, key=lambda r: (r["poid"], _plane(r, default_plane)))
        self.vertices = {r["poid"]: r for r in self.records}
        if len(self.vertices) != len(self.records):
            raise ValueError("duplicate POID in Project Relation Graph")
        self.edges = sorted(edges, key=lambda e: (e["kind"], e["src_poid"], e["dst_poid"], e["edge_id"]))
        self.holds = list(holds or [])
        self.unresolved_imports = list(unresolved_imports or [])
        for edge in self.edges:
            if edge["src_poid"] not in self.vertices or edge["dst_poid"] not in self.vertices:
                raise ValueError(f"edge endpoint missing from graph: {edge['edge_id']}")
            if edge["snapshot_id"] != snapshot_id:
                raise ValueError(f"edge snapshot mismatch: {edge['edge_id']}")
        self.out_edges: dict[str, list[dict]] = defaultdict(list)
        self.in_edges: dict[str, list[dict]] = defaultdict(list)
        for edge in self.edges:
            self.out_edges[edge["src_poid"]].append(edge)
            self.in_edges[edge["dst_poid"]].append(edge)
        for index in (self.out_edges, self.in_edges):
            for poid in index:
                index[poid].sort(key=lambda e: (e["kind"], e["src_poid"], e["dst_poid"], e["edge_id"]))
        vertex_basis = [_vertex_receipt(r, default_plane) for r in self.records]
        edge_basis = [
            {k: e[k] for k in ("edge_id", "kind", "src_poid", "dst_poid", "plane", "extractor", "evidence", "witness", "authority", "loss")}
            for e in self.edges
        ]
        self.graph_id = GRAPH_ID_PREFIX + digest({"schema": GRAPH_SCHEMA, "snapshot_id": snapshot_id, "vertices": vertex_basis, "edges": edge_basis}, 32)

    def _cas(self, expected_snapshot_id: str | None = None, expected_graph_id: str | None = None) -> dict | None:
        if expected_snapshot_id is not None and expected_snapshot_id != self.snapshot_id:
            return {"status": "HOLD_STALE_SNAPSHOT", "expected_snapshot_id": expected_snapshot_id, "current_snapshot_id": self.snapshot_id, "graph_id": self.graph_id}
        if expected_graph_id is not None and expected_graph_id != self.graph_id:
            return {"status": "HOLD_STALE_GRAPH", "expected_graph_id": expected_graph_id, "current_graph_id": self.graph_id, "snapshot_id": self.snapshot_id}
        return None

    def summary(self, *, expected_snapshot_id: str | None = None, expected_graph_id: str | None = None) -> dict:
        hold = self._cas(expected_snapshot_id, expected_graph_id)
        if hold:
            return hold
        by_kind: dict[str, int] = defaultdict(int)
        by_plane: dict[str, int] = defaultdict(int)
        for edge in self.edges:
            by_kind[edge["kind"]] += 1
            by_plane[edge["plane"]] += 1
        return {
            "status": "PASS",
            "schema": GRAPH_SCHEMA,
            "version": GRAPH_VERSION,
            "snapshot_id": self.snapshot_id,
            "graph_id": self.graph_id,
            "vertices": len(self.vertices),
            "edges": len(self.edges),
            "edge_counts": dict(sorted(by_kind.items())),
            "plane_counts": dict(sorted(by_plane.items())),
            "holds": len(self.holds),
            "unresolved_imports": len(self.unresolved_imports),
            "options": self.options.__dict__,
            "laws": GRAPH_LAWS,
            "authority": "NONE",
        }

    def neighbors(
        self,
        poid: str,
        *,
        direction: str = "both",
        kinds: Iterable[str] | None = None,
        offset: int = 0,
        limit: int = 50,
        expected_snapshot_id: str | None = None,
        expected_graph_id: str | None = None,
    ) -> dict:
        hold = self._cas(expected_snapshot_id, expected_graph_id)
        if hold:
            return hold
        if poid not in self.vertices:
            return {"status": "HOLD_UNKNOWN_VERTEX", "poid": poid, "graph_id": self.graph_id}
        if direction not in {"out", "in", "both"}:
            raise ValueError("direction must be one of out,in,both")
        if not (0 <= offset) or not (1 <= limit <= MAX_QUERY_LIMIT):
            raise ValueError(f"offset must be >=0 and limit must be 1..{MAX_QUERY_LIMIT}")
        kind_set = set(kinds or EDGE_KINDS)
        unknown = kind_set - EDGE_KINDS
        if unknown:
            raise ValueError(f"unknown edge kinds: {sorted(unknown)}")
        rows: list[dict] = []
        if direction in {"out", "both"}:
            rows.extend({"direction": "out", "edge": e, "neighbor_poid": e["dst_poid"]} for e in self.out_edges.get(poid, []) if e["kind"] in kind_set)
        if direction in {"in", "both"}:
            rows.extend({"direction": "in", "edge": e, "neighbor_poid": e["src_poid"]} for e in self.in_edges.get(poid, []) if e["kind"] in kind_set)
        rows.sort(key=lambda r: (r["edge"]["kind"], r["neighbor_poid"], r["direction"], r["edge"]["edge_id"]))
        total = len(rows)
        items = rows[offset : offset + limit]
        return {
            "status": "PASS",
            "poid": poid,
            "snapshot_id": self.snapshot_id,
            "graph_id": self.graph_id,
            "total": total,
            "offset": offset,
            "limit": limit,
            "next_offset": offset + len(items) if offset + len(items) < total else None,
            "items": items,
        }

    def _candidate_edges(self, poid: str, kind_set: set[str]) -> list[dict]:
        return [edge for edge in self.out_edges.get(poid, []) if edge["kind"] in kind_set]

    def shortest_path(
        self,
        src_poid: str,
        dst_poid: str,
        *,
        kinds: Iterable[str] | None = None,
        algorithm: str = "bfs",
        weights: dict[str, float] | None = None,
        max_depth: int = 32,
        max_expansions: int = 2000,
        expected_snapshot_id: str | None = None,
        expected_graph_id: str | None = None,
    ) -> dict:
        hold = self._cas(expected_snapshot_id, expected_graph_id)
        if hold:
            return hold
        if src_poid not in self.vertices or dst_poid not in self.vertices:
            missing = [p for p in (src_poid, dst_poid) if p not in self.vertices]
            return {"status": "HOLD_UNKNOWN_VERTEX", "missing": missing, "graph_id": self.graph_id}
        if not (1 <= max_depth <= MAX_DEPTH) or not (1 <= max_expansions <= MAX_EXPANSIONS):
            raise ValueError(f"max_depth must be 1..{MAX_DEPTH}; max_expansions must be 1..{MAX_EXPANSIONS}")
        kind_set = set(kinds or STRUCTURAL_EDGE_KINDS)
        unknown = kind_set - EDGE_KINDS
        if unknown:
            raise ValueError(f"unknown edge kinds: {sorted(unknown)}")
        if src_poid == dst_poid:
            return self._path_receipt(src_poid, dst_poid, [], algorithm, weights or {}, 0)
        if algorithm == "bfs":
            return self._bfs(src_poid, dst_poid, kind_set, max_depth, max_expansions)
        if algorithm == "dijkstra":
            if weights is None:
                raise ValueError("dijkstra requires explicit edge-kind weights; hidden scalarization is forbidden")
            normalized: dict[str, float] = {}
            for kind in kind_set:
                if kind not in weights:
                    raise ValueError(f"dijkstra requires explicit weight for edge kind {kind}")
                value = float(weights[kind])
                if not math.isfinite(value) or value < 0:
                    raise ValueError("dijkstra weights must be finite and non-negative")
                normalized[kind] = value
            return self._dijkstra(src_poid, dst_poid, kind_set, normalized, max_depth, max_expansions)
        raise ValueError("algorithm must be bfs or dijkstra")

    def _bfs(self, src: str, dst: str, kinds: set[str], max_depth: int, max_expansions: int) -> dict:
        q = deque([(src, [])])
        seen = {src}
        expansions = 0
        depth_limited = False
        while q:
            node, path = q.popleft()
            if len(path) >= max_depth:
                depth_limited = True
                continue
            expansions += 1
            if expansions > max_expansions:
                return {"status": "HOLD_EXPANSION_LIMIT", "src_poid": src, "dst_poid": dst, "expansions": expansions - 1, "max_expansions": max_expansions, "snapshot_id": self.snapshot_id, "graph_id": self.graph_id}
            for edge in self._candidate_edges(node, kinds):
                nxt = edge["dst_poid"]
                new_path = path + [edge]
                if nxt == dst:
                    return self._path_receipt(src, dst, new_path, "bfs", {}, expansions)
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, new_path))
        status = "HOLD_DEPTH_LIMIT" if depth_limited else "HOLD_NO_PATH"
        return {"status": status, "src_poid": src, "dst_poid": dst, "expansions": expansions, "max_depth": max_depth, "snapshot_id": self.snapshot_id, "graph_id": self.graph_id}

    def _dijkstra(self, src: str, dst: str, kinds: set[str], weights: dict[str, float], max_depth: int, max_expansions: int) -> dict:
        heap: list[tuple[float, int, str, tuple[str, ...], list[dict]]] = [(0.0, 0, src, (), [])]
        best: dict[tuple[str, int], float] = {(src, 0): 0.0}
        expansions = 0
        depth_limited = False
        while heap:
            cost, depth, node, _, path = heapq.heappop(heap)
            if node == dst:
                return self._path_receipt(src, dst, path, "dijkstra", weights, expansions, scalar_cost=cost)
            if depth >= max_depth:
                depth_limited = True
                continue
            expansions += 1
            if expansions > max_expansions:
                return {"status": "HOLD_EXPANSION_LIMIT", "src_poid": src, "dst_poid": dst, "expansions": expansions - 1, "max_expansions": max_expansions, "snapshot_id": self.snapshot_id, "graph_id": self.graph_id}
            for edge in self._candidate_edges(node, kinds):
                nxt, nd = edge["dst_poid"], depth + 1
                nc = cost + weights[edge["kind"]]
                key = (nxt, nd)
                if nc >= best.get(key, float("inf")):
                    continue
                best[key] = nc
                signature = tuple(e["edge_id"] for e in path) + (edge["edge_id"],)
                heapq.heappush(heap, (nc, nd, nxt, signature, path + [edge]))
        status = "HOLD_DEPTH_LIMIT" if depth_limited else "HOLD_NO_PATH"
        return {"status": status, "src_poid": src, "dst_poid": dst, "expansions": expansions, "max_depth": max_depth, "snapshot_id": self.snapshot_id, "graph_id": self.graph_id}

    def _path_receipt(self, src: str, dst: str, path: list[dict], algorithm: str, weights: dict[str, float], expansions: int, scalar_cost: float | None = None) -> dict:
        plane_crossings = 0
        coordinate_hops = 0
        structural_hops = 0
        last_plane = _plane(self.vertices[src], self.default_plane)
        for edge in path:
            next_plane = _plane(self.vertices[edge["dst_poid"]], self.default_plane)
            plane_crossings += int(next_plane != last_plane)
            coordinate_hops += int(edge["kind"] in GEOMETRIC_EDGE_KINDS)
            structural_hops += int(edge["kind"] in STRUCTURAL_EDGE_KINDS)
            last_plane = next_plane
        result = {
            "status": "ROUTED",
            "src_poid": src,
            "dst_poid": dst,
            "algorithm": algorithm,
            "snapshot_id": self.snapshot_id,
            "graph_id": self.graph_id,
            "hops": len(path),
            "edge_ids": [e["edge_id"] for e in path],
            "edges": path,
            "cost_vector": {
                "structural_hops": structural_hops,
                "authority_friction": sum(1 for e in path if e["authority"] == "COORDINATE_ONLY"),
                "uncertainty": sum(1.0 - float(e["confidence"]) for e in path),
                "plane_crossings": plane_crossings,
                "coordinate_hops": coordinate_hops,
            },
            "expansions": expansions,
            "return": [self.vertices[src]["return"], self.vertices[dst]["return"]],
            "law": "STRUCTURAL_GRAPH_ROUTE != KC144_GEOMETRIC_ROUTE != EXECUTION",
        }
        if algorithm == "dijkstra":
            result["weights"] = dict(sorted(weights.items()))
            result["scalar_cost"] = scalar_cost if scalar_cost is not None else sum(weights[e["kind"]] for e in path)
            result["scalarization_law"] = "PATH_COST_WEIGHTS_ARE_EXPLICIT_INPUT_NOT_HIDDEN_TRUTH"
        return result
