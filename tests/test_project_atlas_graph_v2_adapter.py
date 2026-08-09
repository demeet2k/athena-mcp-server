from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas import compile_git_atlas, mcp_surface_atlas
from athena_mcp.project_atlas_graph import GraphBuildOptions
from athena_mcp.project_atlas_graph_v2_adapter import (
    ADAPTER_LAWS,
    V2_SNAPSHOT_SCHEMA,
    compile_v2_snapshot_relation_graph,
    v2_graph_summary,
)


def run(root: Path, *args: str) -> str:
    import subprocess
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasGraphV2AdapterTests(unittest.TestCase):
    SNAPSHOT = "PATLASV2." + "B" * 32

    def fixture(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        root = Path(td.name) / "repo"; root.mkdir()
        run(root, "init")
        run(root, "config", "user.name", "test")
        run(root, "config", "user.email", "test@example.invalid")
        run(root, "remote", "add", "origin", "https://github.com/demeet2k/v2-adapter-fixture.git")
        (root / "pkg").mkdir()
        (root / "pkg" / "__init__.py").write_text("\n", encoding="utf-8")
        (root / "pkg" / "a.py").write_text("from . import b\n", encoding="utf-8")
        (root / "pkg" / "b.py").write_text("VALUE=1\n", encoding="utf-8")
        run(root, "add", "."); run(root, "commit", "-m", "seed")
        atlas = compile_git_atlas(root)
        mcp = mcp_surface_atlas(
            repo_key=atlas["repository"]["repo_key"],
            head=atlas["repository"]["head"],
            server_name="fixture-mcp",
            tools=[{"name": "fixture_tool", "description": "test", "inputSchema": {"type": "object"}}],
            prompts=[],
        )
        return root, atlas, mcp

    def snapshot(self, atlas: dict, mcp: dict, *, duplicate_runtime: bool, status: str = "GENERATED") -> dict:
        runtime = copy.deepcopy(atlas) if duplicate_runtime else atlas
        return {
            "schema": V2_SNAPSHOT_SCHEMA,
            "status": status,
            "snapshot_id": self.SNAPSHOT,
            "configured_git": atlas,
            "runtime_git": runtime,
            "runtime_git_is_configured": not duplicate_runtime,
            "runtime_provenance": {
                "status": "RESOLVED" if status == "GENERATED" else "HOLD_RUNTIME_PROVENANCE",
                "head": atlas["repository"]["head"],
                "repo_key": atlas["repository"]["repo_key"],
            },
            "runtime_tree_available": status == "GENERATED",
            "mcp_surface": mcp,
        }

    @staticmethod
    def record(atlas: dict, path: str, git_type: str = "blob") -> dict:
        rows = [r for r in atlas["records"] if r["native"]["path"] == path and r["native"]["git_type"] == git_type]
        if len(rows) != 1:
            raise AssertionError((path, git_type, len(rows)))
        return rows[0]

    def test_exact_v2_three_plane_snapshot_produces_configured_runtime_and_mcp_vertices(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, mcp, duplicate_runtime=True)
        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root, runtime_root=root)
        summary = v2_graph_summary(graph)
        configured_count = len(atlas["records"])
        self.assertEqual(summary["v2_adapter"]["coverage"]["configured_git_records"], configured_count)
        self.assertEqual(summary["v2_adapter"]["coverage"]["runtime_git_records"], configured_count)
        self.assertEqual(summary["v2_adapter"]["coverage"]["mcp_records"], 1)
        self.assertEqual(summary["v2_adapter"]["coverage"]["content_reader_planes"], ["configured_git", "runtime_git"])
        self.assertEqual(summary["v2_adapter"]["coverage"]["missing_content_reader_planes"], [])
        self.assertEqual(summary["vertices"], configured_count * 2 + 1)
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT")
        planes = {rec.get("source") for rec in graph.vertices.values()}
        self.assertEqual(planes, {"configured_git", "runtime_git", "mcp"})

    def test_runtime_content_root_derives_from_v2_provenance(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, mcp, duplicate_runtime=True)
        snapshot["runtime_provenance"]["root"] = str(root)
        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        summary = v2_graph_summary(graph)
        coverage = summary["v2_adapter"]["coverage"]
        self.assertEqual(coverage["content_reader_planes"], ["configured_git", "runtime_git"])
        self.assertEqual(coverage["runtime_root_source"], "v2_runtime_provenance")
        self.assertEqual(coverage["missing_content_reader_planes"], [])
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT")
        self.assertIn("RUNTIME_CONTENT_ROOT_DEFAULTS_TO_EXACT_V2_RUNTIME_PROVENANCE_ROOT", ADAPTER_LAWS)

    def test_exact_snapshot_with_missing_runtime_blob_reader_reports_partial_content(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, mcp, duplicate_runtime=True)
        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        summary = v2_graph_summary(graph)
        coverage = summary["v2_adapter"]["coverage"]
        self.assertEqual(coverage["content_reader_planes"], ["configured_git"])
        self.assertEqual(coverage["required_content_planes"], ["configured_git", "runtime_git"])
        self.assertEqual(coverage["missing_content_reader_planes"], ["runtime_git"])
        self.assertEqual(coverage["runtime_root_source"], "unavailable")
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT_PARTIAL_CONTENT")
        self.assertIn("BLOB_READERS_MISSING", summary["coverage_law"])
        runtime_import_holds = [
            h for h in graph.holds
            if h.get("kind") == "PY_IMPORTS" and (h.get("subject") or {}).get("frontier", [None])[0] == "runtime_git"
        ]
        self.assertTrue(runtime_import_holds)
        self.assertIn("EXACT_V2_SNAPSHOT != COMPLETE_CONTENT_EXTRACTION_IF_BLOB_READERS_MISSING", ADAPTER_LAWS)

    def test_content_extractors_disabled_need_no_blob_reader(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, mcp, duplicate_runtime=True)
        options = GraphBuildOptions(include_python_imports=False, include_exact_path_references=False)
        graph = compile_v2_snapshot_relation_graph(snapshot, options=options)
        summary = v2_graph_summary(graph)
        coverage = summary["v2_adapter"]["coverage"]
        self.assertEqual(coverage["required_content_planes"], [])
        self.assertEqual(coverage["missing_content_reader_planes"], [])
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT")

    def test_runtime_is_configured_collapses_duplicate_plane_exactly_as_v2_does(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, mcp, duplicate_runtime=False)
        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        summary = v2_graph_summary(graph)
        self.assertEqual(summary["v2_adapter"]["coverage"]["runtime_git_records"], 0)
        self.assertTrue(summary["v2_adapter"]["coverage"]["runtime_git_is_configured"])
        self.assertEqual(summary["vertices"], len(atlas["records"]) + 1)
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT")

    def test_same_poid_across_configured_runtime_requires_exact_pvtx(self):
        root, atlas, mcp = self.fixture()
        graph = compile_v2_snapshot_relation_graph(
            self.snapshot(atlas, mcp, duplicate_runtime=True),
            configured_root=root,
            runtime_root=root,
        )
        poid = self.record(atlas, "pkg/a.py")["poid"]
        vids = graph.vertex_ids_for_poid(poid)
        self.assertEqual(len(vids), 2)
        self.assertEqual(graph.neighbors(poid)["status"], "HOLD_AMBIGUOUS_VERTEX")
        self.assertEqual(graph.neighbors(vids[0])["status"], "PASS")

    def test_mcp_virtual_object_is_not_sent_through_git_hierarchy_extractor(self):
        root, atlas, mcp = self.fixture()
        graph = compile_v2_snapshot_relation_graph(
            self.snapshot(atlas, mcp, duplicate_runtime=False),
            configured_root=root,
        )
        mcp_poids = {rec["poid"] for rec in mcp["records"]}
        hierarchy_holds = [h for h in graph.holds if h.get("kind") in {"DIR_CONTAINS", "DIR_PARENT_OF"}]
        serialized = repr(hierarchy_holds)
        self.assertTrue(all(poid not in serialized for poid in mcp_poids))
        self.assertIn("MCP_VIRTUAL_VERTEX != GIT_BLOB_VERTEX", ADAPTER_LAWS)

    def test_optional_geometric_overlay_can_include_mcp_plane_without_structural_claim(self):
        root, atlas, mcp = self.fixture()
        mcp2 = mcp_surface_atlas(
            repo_key=atlas["repository"]["repo_key"],
            head=atlas["repository"]["head"],
            server_name="fixture-mcp",
            tools=[
                {"name": "fixture_tool", "description": "test", "inputSchema": {"type": "object"}},
                {"name": "fixture_tool_2", "description": "test2", "inputSchema": {"type": "object"}},
            ],
            prompts=[],
        )
        graph = compile_v2_snapshot_relation_graph(
            self.snapshot(atlas, mcp2, duplicate_runtime=False),
            configured_root=root,
            options=GraphBuildOptions(include_geometric=True),
        )
        mcp_vertices = [rec for rec in graph.vertices.values() if rec.get("source") == "mcp"]
        self.assertEqual(len(mcp_vertices), 2)
        mcp_vertex_ids = {vid for vid, rec in graph.vertices.items() if rec.get("source") == "mcp"}
        for edge in graph.edges:
            if edge["src_vertex_id"] in mcp_vertex_ids:
                self.assertNotIn(edge["kind"], {"DIR_CONTAINS", "DIR_PARENT_OF", "PY_IMPORTS", "PY_RELATIVE_IMPORTS", "EXACT_PATH_REFERENCE"})

    def test_partial_v2_snapshot_is_reported_as_partial_not_full(self):
        root, atlas, mcp = self.fixture()
        snapshot = self.snapshot(atlas, {**mcp, "records": []}, duplicate_runtime=False, status="PARTIAL_RUNTIME_PROVENANCE_HOLD")
        snapshot["runtime_git"] = None
        snapshot["runtime_git_is_configured"] = False
        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        summary = v2_graph_summary(graph)
        self.assertEqual(summary["coverage_standing"], "PARTIAL_V2_SNAPSHOT")
        self.assertEqual(summary["v2_adapter"]["snapshot_status"], "PARTIAL_RUNTIME_PROVENANCE_HOLD")
        self.assertFalse(summary["v2_adapter"]["coverage"]["runtime_tree_available"])
        self.assertIn("PARTIAL_V2_SNAPSHOT -> PARTIAL_GRAPH_COVERAGE_RECEIPT", summary["v2_adapter"]["laws"])

    def test_invalid_snapshot_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            compile_v2_snapshot_relation_graph({"schema": "V1", "snapshot_id": self.SNAPSHOT})
        with self.assertRaises(ValueError):
            compile_v2_snapshot_relation_graph({"schema": V2_SNAPSHOT_SCHEMA, "snapshot_id": "HEAD"})


if __name__ == "__main__":
    unittest.main()
