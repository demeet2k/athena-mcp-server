from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable

from .project_atlas_graph import (
    GraphBuildOptions,
    ProjectRelationGraph,
    compile_project_relation_graph,
    git_blob_reader,
)

V2_SNAPSHOT_SCHEMA = "ATHENA.KC144.FEDERATED_RUNTIME_PROJECT_ATLAS.V2"
ADAPTER_VERSION = "ATHENA.PROJECT_ATLAS.V2_TO_RELATION_GRAPH.V3.ADAPTER.v1"
ADAPTER_LAWS = [
    "V2_SNAPSHOT_PLANES != FLAT_V1_ATLAS",
    "CONFIGURED_GIT_VERTEX != RUNTIME_GIT_VERTEX_UNLESS_V2_COLLAPSES_RUNTIME_TO_CONFIGURED",
    "MCP_VIRTUAL_VERTEX != GIT_BLOB_VERTEX",
    "UNKNOWN_RUNTIME_TREE != EMPTY_RUNTIME_TREE",
    "PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT",
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
) -> Callable[[dict], str] | None:
    readers: dict[str, Callable[[dict], str]] = {}
    if configured_root is not None:
        readers["configured_git"] = git_blob_reader(configured_root)
    if runtime_root is not None:
        readers["runtime_git"] = git_blob_reader(runtime_root)
    if not readers:
        return None

    def read(record: dict) -> str:
        source = str(record.get("source") or "configured_git")
        reader = readers.get(source)
        if reader is None:
            raise ValueError(f"exact blob reader unavailable for source plane {source}")
        return reader(record)

    return read


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


def compile_v2_snapshot_relation_graph(
    snapshot: dict,
    *,
    configured_root: str | Path | None = None,
    runtime_root: str | Path | None = None,
    options: GraphBuildOptions | None = None,
) -> ProjectRelationGraph:
    """Compile V3 from the exact three-plane V2 snapshot without flattening frontier identity.

    Git structural/content extractors run only over configured/runtime Git planes.
    MCP virtual objects remain exact PVTX vertices.  They are not treated as Git paths or
    blobs.  Optional KC144 geometric edges may be compiled inside the MCP plane explicitly.
    """
    if snapshot.get("schema") != V2_SNAPSHOT_SCHEMA:
        raise ValueError(f"expected {V2_SNAPSHOT_SCHEMA}")
    snapshot_id = snapshot.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id.startswith("PATLASV2."):
        raise ValueError("V2 snapshot adapter requires exact PATLASV2 snapshot_id")

    options = options or GraphBuildOptions()
    git_records, coverage = _git_records(snapshot)
    mcp_records = _mcp_records(snapshot)
    reader = _reader_dispatch(configured_root, runtime_root)

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

    # Coverage receipt is diagnostic only; it does not mutate graph identity or authority.
    graph.v2_adapter = {
        "version": ADAPTER_VERSION,
        "snapshot_schema": snapshot.get("schema"),
        "snapshot_status": snapshot.get("status"),
        "snapshot_id": snapshot_id,
        "coverage": {
            **coverage,
            "mcp_records": len(mcp_records),
            "total_vertices": len(graph.vertices),
        },
        "laws": list(ADAPTER_LAWS),
        "authority": "NONE",
    }
    return graph


def v2_graph_summary(graph: ProjectRelationGraph) -> dict:
    out = graph.summary()
    adapter = getattr(graph, "v2_adapter", None)
    if adapter is not None:
        out["v2_adapter"] = adapter
        if adapter["snapshot_status"] != "GENERATED":
            out["coverage_standing"] = "PARTIAL_V2_SNAPSHOT"
            out["coverage_law"] = "PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT"
        else:
            out["coverage_standing"] = "EXACT_V2_SNAPSHOT"
    return out
