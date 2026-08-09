from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable

from .identity import digest
from .project_atlas_graph import (
    GRAPH_ID_PREFIX,
    GraphBuildOptions,
    ProjectRelationGraph,
    compile_project_relation_graph,
    git_blob_reader,
)

V2_SNAPSHOT_SCHEMA = "ATHENA.KC144.FEDERATED_RUNTIME_PROJECT_ATLAS.V2"
ADAPTER_VERSION = "ATHENA.PROJECT_ATLAS.V2_TO_RELATION_GRAPH.V3.ADAPTER.v1"
ADAPTED_GRAPH_IDENTITY_SCHEMA = "ATHENA.PROJECT_ATLAS.RELATION_GRAPH.V3.ADAPTED_IDENTITY.v1"
ADAPTER_LAWS = [
    "V2_SNAPSHOT_PLANES != FLAT_V1_ATLAS",
    "CONFIGURED_GIT_VERTEX != RUNTIME_GIT_VERTEX_UNLESS_V2_COLLAPSES_RUNTIME_TO_CONFIGURED",
    "MCP_VIRTUAL_VERTEX != GIT_BLOB_VERTEX",
    "UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE",
    "PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT",
    "EXACT_V2_SNAPSHOT != COMPLETE_CONTENT_EXTRACTION_IF_BLOB_READERS_MISSING",
    "RUNTIME_CONTENT_ROOT_DEFAULTS_TO_EXACT_V2_RUNTIME_PROVENANCE_ROOT",
    "GRAPH_ID_BINDS_EXTRACTION_PROFILE_AND_COVERAGE",
    "SAME_VISIBLE_EDGES_WITH_DIFFERENT_OBSERVABILITY != SAME_GRAPH_RECEIPT",
]


def _tag(records: list[dict], source: str) -> list[dict]:
    out = []
    for record in records:
        row = dict(record)
        row["source"] = source
        out.append(row)
    return out


def _reader_dispatch(
    configured_root: str | Path | None,
    runtime_root: str | Path | None,
) -> tuple[Callable[[dict], str] | None, tuple[str, ...]]:
    readers: dict[str, Callable[[dict], str]] = {}
    if configured_root is not None:
        readers["configured_git"] = git_blob_reader(configured_root)
    if runtime_root is not None:
        readers["runtime_git"] = git_blob_reader(runtime_root)
    if not readers:
        return None, ()

    def read(record: dict) -> str:
        source = str(record.get("source") or "configured_git")
        reader = readers.get(source)
        if reader is None:
            raise ValueError(f"exact blob reader unavailable for source plane {source}")
        return reader(record)

    return read, tuple(sorted(readers))


def _git_records(snapshot: dict) -> tuple[list[dict], dict]:
    configured = snapshot.get("configured_git") or {}
    runtime = snapshot.get("runtime_git")
    runtime_is_configured = bool(snapshot.get("runtime_git_is_configured"))
    records = _tag(list(configured.get("records") or []), "configured_git")
    configured_count = len(records)
    runtime_count = 0
    if runtime is not None and not runtime_is_configured:
        runtime_rows = _tag(list(runtime.get("records") or []), "runtime_git")
        runtime_count = len(runtime_rows)
        records.extend(runtime_rows)
    coverage = {
        "configured_git_records": configured_count,
        "runtime_git_records": runtime_count,
        "runtime_git_is_configured": runtime_is_configured,
        "runtime_tree_available": bool(snapshot.get("runtime_tree_available")),
        "runtime_provenance_status": (snapshot.get("runtime_provenance") or {}).get("status"),
    }
    return records, coverage


def _mcp_records(snapshot: dict) -> list[dict]:
    return _tag(list((snapshot.get("mcp_surface") or {}).get("records") or []), "mcp")


def _runtime_root(snapshot: dict, explicit: str | Path | None) -> str | Path | None:
    if explicit is not None:
        return explicit
    provenance = snapshot.get("runtime_provenance") or {}
    if provenance.get("status") != "RESOLVED":
        return None
    return provenance.get("root") or None


def _required_content_planes(
    coverage: dict,
    options: GraphBuildOptions,
) -> tuple[str, ...]:
    if not (options.include_python_imports or options.include_exact_path_references):
        return ()
    required = []
    if coverage["configured_git_records"]:
        required.append("configured_git")
    if coverage["runtime_git_records"]:
        required.append("runtime_git")
    return tuple(required)


def _options_receipt(options: GraphBuildOptions) -> dict:
    return {
        "default_plane": options.default_plane,
        "include_hierarchy": options.include_hierarchy,
        "include_python_imports": options.include_python_imports,
        "include_blob_aliases": options.include_blob_aliases,
        "include_exact_path_references": options.include_exact_path_references,
        "include_geometric": options.include_geometric,
    }


def _adapted_graph_identity(base_graph_id: str, snapshot: dict, coverage: dict, options: GraphBuildOptions) -> tuple[str, dict]:
    """Bind graph CAS identity to what was observable, not only the emitted V/E set."""
    basis = {
        "schema": ADAPTED_GRAPH_IDENTITY_SCHEMA,
        "adapter_version": ADAPTER_VERSION,
        "base_graph_id": base_graph_id,
        "snapshot_id": snapshot["snapshot_id"],
        "snapshot_status": snapshot.get("status"),
        "runtime_provenance_status": coverage.get("runtime_provenance_status"),
        "runtime_tree_available": coverage.get("runtime_tree_available"),
        "runtime_git_is_configured": coverage.get("runtime_git_is_configured"),
        "content_reader_planes": coverage.get("content_reader_planes"),
        "required_content_planes": coverage.get("required_content_planes"),
        "missing_content_reader_planes": coverage.get("missing_content_reader_planes"),
        "options": _options_receipt(options),
    }
    return GRAPH_ID_PREFIX + digest(basis, 32), basis


def compile_v2_snapshot_relation_graph(
    snapshot: dict,
    *,
    configured_root: str | Path | None = None,
    runtime_root: str | Path | None = None,
    options: GraphBuildOptions | None = None,
) -> ProjectRelationGraph:
    """Compile V3 from the exact three-plane V2 snapshot without flattening frontier identity.

    Git structural/content extractors run only over configured/runtime Git planes.
    MCP virtual objects remain exact PVTX vertices. They are not treated as Git paths or
    blobs. Optional KC144 geometric edges may be compiled inside the MCP plane explicitly.

    `runtime_root` defaults to the exact V2 runtime-provenance root when available. The
    configured checkout root remains an explicit caller input because V2 intentionally does
    not put local configured-root paths in its durable snapshot identity.
    """
    if snapshot.get("schema") != V2_SNAPSHOT_SCHEMA:
        raise ValueError(f"expected {V2_SNAPSHOT_SCHEMA}")
    snapshot_id = snapshot.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.startswith("PATLASV2."):
        raise ValueError("V2 snapshot adapter requires exact PATLASV2 snapshot_id")

    options = options or GraphBuildOptions()
    git_records, coverage = _git_records(snapshot)
    mcp_records = _mcp_records(snapshot)
    resolved_runtime_root = _runtime_root(snapshot, runtime_root)
    reader, reader_planes = _reader_dispatch(configured_root, resolved_runtime_root)
    required_content_planes = _required_content_planes(coverage, options)
    missing_content_planes = tuple(sorted(set(required_content_planes) - set(reader_planes)))

    coverage = {
        **coverage,
        "mcp_records": len(mcp_records),
        "content_reader_planes": list(reader_planes),
        "required_content_planes": list(required_content_planes),
        "missing_content_reader_planes": list(missing_content_planes),
        "runtime_root_source": (
            "explicit"
            if runtime_root is not None
            else "v2_runtime_provenance"
            if resolved_runtime_root is not None
            else "unavailable"
        ),
    }

    git_graph = compile_project_relation_graph(
        {"records": git_records},
        snapshot_id=snapshot_id,
        blob_reader=reader,
        options=options,
    )

    edges = list(git_graph.edges)
    holds = list(git_graph.holds)
    unresolved = list(git_graph.unresolved_imports)

    # MCP virtual records are not passed through Git hierarchy/import/path extractors.
    # If explicitly requested, only their coordinate overlay is generated here.
    if mcp_records and options.include_geometric:
        mcp_options = replace(
            options,
            include_hierarchy=False,
            include_python_imports=False,
            include_blob_aliases=False,
            include_exact_path_references=False,
            include_geometric=True,
        )
        mcp_graph = compile_project_relation_graph(
            {"records": mcp_records},
            snapshot_id=snapshot_id,
            options=mcp_options,
        )
        edges.extend(mcp_graph.edges)
        holds.extend(mcp_graph.holds)

    graph = ProjectRelationGraph(
        snapshot_id=snapshot_id,
        records=git_records + mcp_records,
        edges=edges,
        holds=holds,
        unresolved_imports=unresolved,
        default_plane=options.default_plane,
        options=options,
    )

    coverage["total_vertices"] = len(graph.vertices)
    base_graph_id = graph.graph_id
    graph.graph_id, identity_basis = _adapted_graph_identity(base_graph_id, snapshot, coverage, options)

    # Coverage is part of the adapted graph CAS identity because observable edge classes are
    # semantically different from edge classes that were enabled but not readable.
    graph.v2_adapter = {
        "version": ADAPTER_VERSION,
        "identity_schema": ADAPTED_GRAPH_IDENTITY_SCHEMA,
        "snapshot_schema": snapshot.get("schema"),
        "snapshot_status": snapshot.get("status"),
        "snapshot_id": snapshot_id,
        "base_graph_id": base_graph_id,
        "adapted_graph_id": graph.graph_id,
        "identity_basis_digest": digest(identity_basis, 32),
        "extraction_profile": _options_receipt(options),
        "coverage": coverage,
        "laws": list(ADAPTER_LAWS),
        "authority": "NONE",
    }
    return graph


def v2_graph_summary(graph: ProjectRelationGraph) -> dict:
    out = graph.summary()
    adapter = getattr(graph, "v2_adapter", None)
    if adapter is not None:
        out["v2_adapter"] = adapter
        missing = adapter["coverage"].get("missing_content_reader_planes") or []
        if adapter["snapshot_status"] != "GENERATED":
            out["coverage_standing"] = "PARTIAL_V2_SNAPSHOT"
            out["coverage_law"] = "PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT"
        elif missing:
            out["coverage_standing"] = "EXACT_V2_SNAPSHOT_PARTIAL_CONTENT"
            out["coverage_law"] = "EXACT_V2_SNAPSHOT != COMPLETE_CONTENT_EXTRACTION_IF_BLOB_READERS_MISSING"
        else:
            out["coverage_standing"] = "EXACT_V2_SNAPSHOT"
    return out
