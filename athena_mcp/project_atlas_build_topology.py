from __future__ import annotations

import ast
import hashlib
import json
import re
import tomllib
from collections import defaultdict
from pathlib import PurePosixPath
from typing import Callable, Iterable

from .identity import digest
from .project_atlas_graph import ProjectRelationGraph

BUILD_SCHEMA = "ATHENA.SIGMA04.BUILD_TOPOLOGY.v1"
SYMBOL_SCHEMA = "ATHENA.SIGMA04.PYTHON_SYMBOL.v1"
BUILD_VERSION = "ATHENA.SIGMA04.BUILD_TOPOLOGY.ENTRYPOINT_SYMBOL.V1"
SYMBOL_PREFIX = "PSYM."
BUILD_EDGE_PREFIX = "PBUILD."
BUILD_GRAPH_PREFIX = "PBUILDG1."

ENTRYPOINT_EDGE = "PYPROJECT_ENTRYPOINT_RESOLVES_TO_SYMBOL"
BUILD_EDGE_KINDS = {ENTRYPOINT_EDGE}

BUILD_LAWS = [
    "PSYM != POID != PVTX != OID",
    "SYMBOL_NAME_MATCH != SYMBOL_IDENTITY",
    "MODULE_NAME_MATCH != MODULE_IDENTITY",
    "ENTRYPOINT_TEXT != RESOLVED_LOCAL_SYMBOL",
    "PYPROJECT_ENTRYPOINT_RESOLVES_TO_SYMBOL -> EXACT_MODULE_AND_SYMBOL_WITNESS",
    "DUPLICATE_TOP_LEVEL_BINDING -> HOLD_AMBIGUOUS_SYMBOL",
    "AMBIGUOUS_LOCAL_MODULE -> HOLD_AMBIGUOUS_MODULE",
    "EXTERNAL_OR_MISSING_MODULE -> HOLD_ENTRYPOINT_MODULE",
    "UTF8_BYTE_SPAN != CHARACTER_OFFSET_SPAN",
    "SOURCE_CACHE != SYMBOL_IDENTITY",
    "BUILD_EDGE != EXECUTION",
    "BUILD_GRAPH != PROMOTION_AUTHORITY",
    "BUILD_EDGE_CLASS_CHANGE_REQUIRES_SCHEMA_BUMP",
]

_ENTRYPOINT_RE = re.compile(
    r"^(?P<module>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*):(?P<attr>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)$"
)


def python_module_name(path: str) -> str | None:
    """Map a repository Python path to its import-like module coordinate.

    This is a structural path projection only. Whether the package is importable at runtime is
    a separate build/runtime question and is not asserted here.
    """
    if not path.endswith(".py"):
        return None
    pp = PurePosixPath(path)
    if pp.name == "__init__.py":
        return ".".join(pp.parent.parts) if str(pp.parent) != "." else ""
    return ".".join(pp.with_suffix("").parts)


def _frontier(record: dict, default_plane: str) -> tuple[str, str, str]:
    native = record["native"]
    return str(record.get("source") or default_plane), native["repo"], native["head"]


def _source_cache_key(record: dict, default_plane: str = "configured_git") -> tuple[str, str, str, str]:
    native = record["native"]
    return (
        str(record.get("source") or default_plane),
        native["repo"],
        native["head"],
        native["object_sha"],
    )


def memoized_blob_reader(reader: Callable[[dict], str], *, default_plane: str = "configured_git") -> Callable[[dict], str]:
    """Cache exact blob text per manifestation/object without changing any identity receipt."""
    cache: dict[tuple[str, str, str, str], str] = {}

    def read(record: dict) -> str:
        key = _source_cache_key(record, default_plane)
        if key not in cache:
            cache[key] = reader(record)
        return cache[key]

    return read


def _span(node: ast.AST) -> dict:
    return {
        "lineno": int(getattr(node, "lineno", 0) or 0),
        "col_offset": int(getattr(node, "col_offset", 0) or 0),
        "end_lineno": int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
        "end_col_offset": int(getattr(node, "end_col_offset", 0) or 0),
    }


def _utf8_line_offsets(source: str) -> tuple[bytes, tuple[int, ...]]:
    """Return exact UTF-8 bytes and zero-based byte offset for every one-based AST line.

    CPython AST column offsets are UTF-8 byte offsets. Scanning the encoded blob once avoids
    repeated full-source splitting/scanning for every definition in a large module.
    """
    encoded = source.encode("utf-8")
    offsets = [0]
    offsets.extend(index + 1 for index, byte in enumerate(encoded) if byte == 0x0A)
    return encoded, tuple(offsets)


def _segment_witness(encoded: bytes, line_offsets: tuple[int, ...], span: dict) -> dict:
    lineno = span["lineno"]
    end_lineno = span["end_lineno"]
    if lineno < 1 or end_lineno < lineno or lineno > len(line_offsets) or end_lineno > len(line_offsets):
        raise ValueError("AST source span lies outside exact UTF-8 source line index")
    start = line_offsets[lineno - 1] + span["col_offset"]
    end = line_offsets[end_lineno - 1] + span["end_col_offset"]
    if start < 0 or end < start or end > len(encoded):
        raise ValueError("AST UTF-8 byte span lies outside exact source blob")
    segment = encoded[start:end]
    return {
        "start_byte": start,
        "end_byte": end,
        "length_bytes": len(segment),
        "sha256": hashlib.sha256(segment).hexdigest(),
    }


def _bound_names(node: ast.AST) -> list[tuple[str, str]]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [(node.name, "function" if isinstance(node, ast.FunctionDef) else "async_function")]
    if isinstance(node, ast.ClassDef):
        return [(node.name, "class")]
    if isinstance(node, ast.Assign):
        names: list[tuple[str, str]] = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append((target.id, "assignment"))
        return names
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [(node.target.id, "annotated_assignment")]
    return []


def _symbol_receipt(
    *,
    record: dict,
    vertex: str,
    module: str,
    name: str,
    kind: str,
    node: ast.AST,
    encoded_source: bytes,
    line_offsets: tuple[int, ...],
) -> dict:
    span = _span(node)
    segment = _segment_witness(encoded_source, line_offsets, span)
    span_digest = digest(
        {
            "object_sha": record["native"]["object_sha"],
            "kind": kind,
            "span": span,
            "source_segment_sha256": segment["sha256"],
        },
        32,
    )
    qualified = f"{module}.{name}" if module else name
    psym = SYMBOL_PREFIX + digest(
        {
            "schema": SYMBOL_SCHEMA,
            "vertex_id": vertex,
            "qualified_symbol": qualified,
            "source_span_digest": span_digest,
        },
        24,
    )
    base_return = record["return"]["uri"]
    return {
        "schema": SYMBOL_SCHEMA,
        "psym": psym,
        "vertex_id": vertex,
        "poid": record["poid"],
        "plane": record.get("source"),
        "repo": record["native"]["repo"],
        "head": record["native"]["head"],
        "path": record["native"]["path"],
        "module": module,
        "name": name,
        "qualified_symbol": qualified,
        "kind": kind,
        "span": span,
        "source_segment": segment,
        "source_span_digest": span_digest,
        "object_sha": record["native"]["object_sha"],
        "return": {
            "uri": f"{base_return}#L{span['lineno']}-L{span['end_lineno']}",
            "object": base_return,
            "law": "PSYM RETURN preserves exact PVTX/Git object plus AST UTF-8 source-span witness",
        },
        "authority": "STRUCTURAL_DEFINITION_ONLY",
        "laws": [
            "PSYM != RUNTIME_BINDING",
            "SOURCE_DEFINITION != EXECUTED_EFFECT",
            "UTF8_BYTE_SPAN != CHARACTER_OFFSET_SPAN",
        ],
    }


class PythonSymbolIndex:
    def __init__(
        self,
        *,
        graph: ProjectRelationGraph,
        symbols: list[dict],
        holds: list[dict],
        source_failures: list[dict],
    ):
        self.graph = graph
        self.symbols = sorted(symbols, key=lambda s: (s["vertex_id"], s["qualified_symbol"], s["psym"]))
        self.holds = sorted(holds, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
        self.source_failures = sorted(source_failures, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
        self.by_psym = {s["psym"]: s for s in self.symbols}
        self.by_vertex_name: dict[tuple[str, str], list[dict]] = defaultdict(list)
        self.module_vertices: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
        for vid, rec in graph.vertices.items():
            module = python_module_name(rec["native"]["path"])
            if module is not None and rec["native"]["git_type"] == "blob":
                self.module_vertices[(*_frontier(rec, graph.default_plane), module)].append(vid)
        for key in self.module_vertices:
            self.module_vertices[key].sort()
        for symbol in self.symbols:
            self.by_vertex_name[(symbol["vertex_id"], symbol["name"])].append(symbol)
        for key in self.by_vertex_name:
            self.by_vertex_name[key].sort(key=lambda s: s["psym"])
        self.index_id = "PSYMI1." + digest(
            {
                "schema": SYMBOL_SCHEMA,
                "parent_graph_id": graph.graph_id,
                "symbols": [
                    {
                        "psym": s["psym"],
                        "vertex_id": s["vertex_id"],
                        "qualified_symbol": s["qualified_symbol"],
                        "kind": s["kind"],
                        "source_span_digest": s["source_span_digest"],
                    }
                    for s in self.symbols
                ],
                "holds": self.holds,
                "source_failures": self.source_failures,
            },
            32,
        )

    def resolve_module(self, frontier: tuple[str, str, str], module: str) -> dict:
        candidates = self.module_vertices.get((*frontier, module), [])
        if len(candidates) == 1:
            return {"status": "RESOLVED", "vertex_id": candidates[0], "module": module}
        if len(candidates) > 1:
            return {
                "status": "HOLD_AMBIGUOUS_MODULE",
                "module": module,
                "candidate_vertex_ids": list(candidates),
                "law": "MODULE_NAME_MATCH != MODULE_IDENTITY",
            }
        return {
            "status": "HOLD_ENTRYPOINT_MODULE",
            "module": module,
            "candidate_vertex_ids": [],
            "law": "EXTERNAL_OR_MISSING_MODULE -> HOLD_ENTRYPOINT_MODULE",
        }

    def resolve_symbol(self, vertex: str, name: str) -> dict:
        candidates = self.by_vertex_name.get((vertex, name), [])
        if len(candidates) == 1:
            return {"status": "RESOLVED", "symbol": candidates[0]}
        if len(candidates) > 1:
            return {
                "status": "HOLD_AMBIGUOUS_SYMBOL",
                "vertex_id": vertex,
                "name": name,
                "candidate_psyms": [s["psym"] for s in candidates],
                "law": "DUPLICATE_TOP_LEVEL_BINDING -> HOLD_AMBIGUOUS_SYMBOL",
            }
        return {
            "status": "HOLD_ENTRYPOINT_SYMBOL",
            "vertex_id": vertex,
            "name": name,
            "candidate_psyms": [],
            "law": "SYMBOL_NAME_MATCH != SYMBOL_IDENTITY",
        }


def compile_python_symbol_index(
    graph: ProjectRelationGraph,
    *,
    blob_reader: Callable[[dict], str],
    planes: Iterable[str] = ("configured_git", "runtime_git"),
) -> PythonSymbolIndex:
    allowed_planes = set(planes)
    symbols: list[dict] = []
    holds: list[dict] = []
    failures: list[dict] = []
    parsed_cache: dict[tuple[str, str, str, str], tuple[str, ast.Module, bytes, tuple[int, ...]] | Exception] = {}

    for vid, record in sorted(graph.vertices.items()):
        plane = str(record.get("source") or graph.default_plane)
        native = record["native"]
        if plane not in allowed_planes or native["git_type"] != "blob" or not native["path"].endswith(".py"):
            continue
        module = python_module_name(native["path"])
        if module is None:
            continue
        key = _source_cache_key(record, graph.default_plane)
        if key not in parsed_cache:
            try:
                source = blob_reader(record)
                tree = ast.parse(source, filename=native["path"])
                encoded_source, line_offsets = _utf8_line_offsets(source)
                parsed_cache[key] = (source, tree, encoded_source, line_offsets)
            except (UnicodeDecodeError, SyntaxError, ValueError, RuntimeError) as exc:
                parsed_cache[key] = exc
        parsed = parsed_cache[key]
        if isinstance(parsed, Exception):
            failures.append(
                {
                    "status": "HOLD_SYMBOL_SOURCE",
                    "vertex_id": vid,
                    "poid": record["poid"],
                    "path": native["path"],
                    "reason": type(parsed).__name__,
                }
            )
            continue
        _, tree, encoded_source, line_offsets = parsed
        local: dict[str, list[dict]] = defaultdict(list)
        try:
            for node in tree.body:
                for name, kind in _bound_names(node):
                    receipt = _symbol_receipt(
                        record=record,
                        vertex=vid,
                        module=module,
                        name=name,
                        kind=kind,
                        node=node,
                        encoded_source=encoded_source,
                        line_offsets=line_offsets,
                    )
                    symbols.append(receipt)
                    local[name].append(receipt)
        except ValueError as exc:
            failures.append(
                {
                    "status": "HOLD_SYMBOL_SOURCE",
                    "vertex_id": vid,
                    "poid": record["poid"],
                    "path": native["path"],
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                }
            )
            continue
        for name, rows in sorted(local.items()):
            if len(rows) > 1:
                holds.append(
                    {
                        "status": "HOLD_AMBIGUOUS_SYMBOL",
                        "vertex_id": vid,
                        "path": native["path"],
                        "name": name,
                        "candidate_psyms": sorted(r["psym"] for r in rows),
                        "law": "DUPLICATE_TOP_LEVEL_BINDING -> HOLD_AMBIGUOUS_SYMBOL",
                    }
                )
    return PythonSymbolIndex(graph=graph, symbols=symbols, holds=holds, source_failures=failures)


def _entrypoint_declarations(pyproject: dict) -> list[dict]:
    project = pyproject.get("project") or {}
    rows: list[dict] = []
    for group_key, group_name in (("scripts", "console_scripts"), ("gui-scripts", "gui_scripts")):
        group = project.get(group_key) or {}
        if isinstance(group, dict):
            for name, target in group.items():
                rows.append({"group": group_name, "name": str(name), "target": target})
    entry_groups = project.get("entry-points") or {}
    if isinstance(entry_groups, dict):
        for group_name, group in entry_groups.items():
            if not isinstance(group, dict):
                continue
            for name, target in group.items():
                rows.append({"group": str(group_name), "name": str(name), "target": target})
    rows.sort(key=lambda r: (r["group"], r["name"], str(r["target"])))
    return rows


def _build_edge(
    *,
    graph: ProjectRelationGraph,
    pyproject_record: dict,
    pyproject_vertex: str,
    declaration: dict,
    module_vertex: str,
    symbol: dict,
) -> dict:
    witness = {
        "pyproject_vertex_id": pyproject_vertex,
        "pyproject_poid": pyproject_record["poid"],
        "pyproject_path": pyproject_record["native"]["path"],
        "group": declaration["group"],
        "entrypoint_name": declaration["name"],
        "target": declaration["target"],
        "resolved_module_vertex_id": module_vertex,
        "resolved_psym": symbol["psym"],
    }
    edge_id = BUILD_EDGE_PREFIX + digest(
        {
            "schema": BUILD_SCHEMA,
            "parent_graph_id": graph.graph_id,
            "kind": ENTRYPOINT_EDGE,
            "witness": witness,
        },
        24,
    )
    return {
        "edge_id": edge_id,
        "kind": ENTRYPOINT_EDGE,
        "src_vertex_id": pyproject_vertex,
        "src_poid": pyproject_record["poid"],
        "dst_vertex_id": module_vertex,
        "dst_psym": symbol["psym"],
        "dst_poid": symbol["poid"],
        "snapshot_id": graph.snapshot_id,
        "parent_graph_id": graph.graph_id,
        "extractor": "pep621_toml_entrypoint_to_python_ast_symbol_v1",
        "evidence": "EXACT_TOML_DECLARATION+EXACT_PVTX_MODULE+PYTHON_AST_SYMBOL",
        "witness": witness,
        "authority": "BUILD_DECLARATION_OBSERVATION",
        "loss": "ENTRYPOINT_DECLARATION_DOES_NOT_PROVE_INSTALL_OR_EXECUTION_SUCCESS",
        "return": {
            "source": pyproject_record["return"]["uri"],
            "destination": symbol["return"]["uri"],
            "law": "build edge RETURN preserves exact pyproject PVTX and exact PSYM definition witness",
        },
    }


class BuildTopology:
    def __init__(
        self,
        *,
        graph: ProjectRelationGraph,
        symbol_index: PythonSymbolIndex,
        edges: list[dict],
        holds: list[dict],
        pyprojects: list[str],
    ):
        self.graph = graph
        self.symbol_index = symbol_index
        self.edges = sorted(edges, key=lambda e: (e["kind"], e["src_vertex_id"], e["dst_psym"], e["edge_id"]))
        self.holds = sorted(holds, key=lambda h: json.dumps(h, sort_keys=True, separators=(",", ":")))
        self.pyprojects = sorted(pyprojects)
        self.build_graph_id = BUILD_GRAPH_PREFIX + digest(
            {
                "schema": BUILD_SCHEMA,
                "version": BUILD_VERSION,
                "parent_graph_id": graph.graph_id,
                "symbol_index_id": symbol_index.index_id,
                "pyprojects": self.pyprojects,
                "edges": self.edges,
                "holds": self.holds,
                "extractors": ["python_ast_top_level_symbol_utf8_v1", "pep621_toml_entrypoint_to_python_ast_symbol_v1"],
            },
            32,
        )

    def summary(self) -> dict:
        return {
            "status": "PASS",
            "schema": BUILD_SCHEMA,
            "version": BUILD_VERSION,
            "snapshot_id": self.graph.snapshot_id,
            "parent_graph_id": self.graph.graph_id,
            "symbol_index_id": self.symbol_index.index_id,
            "build_graph_id": self.build_graph_id,
            "symbols": len(self.symbol_index.symbols),
            "symbol_holds": len(self.symbol_index.holds),
            "symbol_source_failures": len(self.symbol_index.source_failures),
            "pyprojects": len(self.pyprojects),
            "edges": len(self.edges),
            "holds": len(self.holds),
            "edge_counts": {kind: sum(1 for e in self.edges if e["kind"] == kind) for kind in sorted(BUILD_EDGE_KINDS)},
            "authority": "NONE",
            "laws": list(BUILD_LAWS),
        }


def compile_build_topology(
    graph: ProjectRelationGraph,
    *,
    blob_reader: Callable[[dict], str],
    planes: Iterable[str] = ("configured_git", "runtime_git"),
) -> BuildTopology:
    allowed_planes = set(planes)
    symbol_index = compile_python_symbol_index(graph, blob_reader=blob_reader, planes=allowed_planes)
    edges: list[dict] = []
    holds: list[dict] = list(symbol_index.holds) + list(symbol_index.source_failures)
    pyprojects: list[str] = []

    for pyproject_vertex, record in sorted(graph.vertices.items()):
        plane = str(record.get("source") or graph.default_plane)
        native = record["native"]
        if plane not in allowed_planes or native["git_type"] != "blob" or native["path"] != "pyproject.toml":
            continue
        pyprojects.append(pyproject_vertex)
        try:
            raw = blob_reader(record)
            data = tomllib.loads(raw)
        except (UnicodeDecodeError, ValueError, RuntimeError) as exc:
            holds.append(
                {
                    "status": "HOLD_PYPROJECT_SOURCE",
                    "pyproject_vertex_id": pyproject_vertex,
                    "path": native["path"],
                    "reason": type(exc).__name__,
                }
            )
            continue
        frontier = _frontier(record, graph.default_plane)
        for declaration in _entrypoint_declarations(data):
            target = declaration["target"]
            if not isinstance(target, str):
                holds.append(
                    {
                        "status": "HOLD_ENTRYPOINT_SYNTAX",
                        "pyproject_vertex_id": pyproject_vertex,
                        "declaration": declaration,
                        "reason": "entrypoint target is not a string",
                    }
                )
                continue
            match = _ENTRYPOINT_RE.fullmatch(target.strip())
            if not match:
                holds.append(
                    {
                        "status": "HOLD_ENTRYPOINT_SYNTAX",
                        "pyproject_vertex_id": pyproject_vertex,
                        "declaration": declaration,
                        "reason": "unsupported or non-exact module:attribute syntax",
                    }
                )
                continue
            module, attr = match.group("module"), match.group("attr")
            module_result = symbol_index.resolve_module(frontier, module)
            if module_result["status"] != "RESOLVED":
                holds.append(
                    {
                        **module_result,
                        "pyproject_vertex_id": pyproject_vertex,
                        "declaration": declaration,
                    }
                )
                continue
            module_vertex = module_result["vertex_id"]
            if "." in attr:
                holds.append(
                    {
                        "status": "HOLD_NESTED_ENTRYPOINT_SYMBOL",
                        "pyproject_vertex_id": pyproject_vertex,
                        "declaration": declaration,
                        "module_vertex_id": module_vertex,
                        "attribute": attr,
                        "reason": "V1 resolves exact top-level AST bindings only",
                        "law": "SYMBOL_NAME_MATCH != SYMBOL_IDENTITY",
                    }
                )
                continue
            symbol_result = symbol_index.resolve_symbol(module_vertex, attr)
            if symbol_result["status"] != "RESOLVED":
                holds.append(
                    {
                        **symbol_result,
                        "pyproject_vertex_id": pyproject_vertex,
                        "declaration": declaration,
                    }
                )
                continue
            symbol = symbol_result["symbol"]
            edges.append(
                _build_edge(
                    graph=graph,
                    pyproject_record=record,
                    pyproject_vertex=pyproject_vertex,
                    declaration=declaration,
                    module_vertex=module_vertex,
                    symbol=symbol,
                )
            )

    unique_edges = {e["edge_id"]: e for e in edges}
    return BuildTopology(
        graph=graph,
        symbol_index=symbol_index,
        edges=list(unique_edges.values()),
        holds=holds,
        pyprojects=pyprojects,
    )
