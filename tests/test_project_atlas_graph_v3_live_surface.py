from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas_graph_v2_adapter import (
    compile_v2_snapshot_relation_graph,
    v2_graph_summary,
)
from athena_mcp.server import PROMPTS, TOOLS, Server


def run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasGraphV3LiveSurfaceTests(unittest.TestCase):
    def live_fixture(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        base = Path(td.name)
        root = base / "configured-brain"; root.mkdir()
        run(root, "init")
        run(root, "config", "user.name", "test")
        run(root, "config", "user.email", "test@example.invalid")
        run(root, "remote", "add", "origin", "https://github.com/demeet2k/project-graph-live-fixture.git")
        files = {
            "README.md": "configured brain\n",
            "pkg/__init__.py": "\n",
            "pkg/a.py": "from . import b\n",
            "pkg/b.py": "VALUE = 1\n",
            "config.json": '{"entry": "pkg/a.py"}\n',
        }
        for rel, text in files.items():
            path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
        run(root, "add", "."); run(root, "commit", "-m", "seed configured brain")
        return root, Server(str(base / "state.db"), git_root=root)

    def test_live_v2_snapshot_compiles_exact_three_plane_v3_graph(self):
        root, server = self.live_fixture()
        surface = server.aor_development.project_atlas
        snapshot, hold, observation = surface._snapshot()
        self.assertIsNone(hold)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot["status"], "GENERATED")
        self.assertTrue(snapshot["snapshot_id"].startswith("PATLASV2."))
        self.assertTrue(snapshot["runtime_tree_available"])
        self.assertEqual(snapshot["runtime_provenance"]["status"], "RESOLVED")
        self.assertTrue(snapshot["runtime_provenance"].get("root"))
        self.assertEqual(observation["configured_git"]["head"], run(root, "rev-parse", "HEAD"))

        graph = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        summary = v2_graph_summary(graph)
        coverage = summary["v2_adapter"]["coverage"]

        expected_vertices = len(snapshot["configured_git"]["records"])
        if snapshot["runtime_git"] is not None and not snapshot["runtime_git_is_configured"]:
            expected_vertices += len(snapshot["runtime_git"]["records"])
        expected_vertices += len(snapshot["mcp_surface"]["records"])

        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(summary["snapshot_id"], snapshot["snapshot_id"])
        self.assertTrue(summary["graph_id"].startswith("PATLASG3."))
        self.assertEqual(summary["vertices"], expected_vertices)
        self.assertEqual(summary["coverage_standing"], "EXACT_V2_SNAPSHOT")
        self.assertEqual(coverage["missing_content_reader_planes"], [])
        self.assertIn("configured_git", coverage["content_reader_planes"])
        if coverage["runtime_git_records"]:
            self.assertIn("runtime_git", coverage["content_reader_planes"])
            self.assertEqual(coverage["runtime_root_source"], "v2_runtime_provenance")

        mcp_records = [rec for rec in graph.vertices.values() if rec.get("source") == "mcp"]
        self.assertEqual(len(mcp_records), len(TOOLS) + len(PROMPTS))
        self.assertEqual(len(mcp_records), snapshot["mcp_surface"]["count"])
        self.assertTrue(all(rec["return"]["uri"].startswith("athena+mcp://") for rec in mcp_records))

        # The configured fixture guarantees at least one exact relative-import edge and one
        # exact JSON path-reference edge. Runtime source contributes its own independently
        # witnessed relations without being collapsed into the configured plane.
        configured_imports = [
            edge for edge in graph.edges
            if edge["kind"] == "PY_RELATIVE_IMPORTS"
            and graph.vertices[edge["src_vertex_id"]].get("source") == "configured_git"
        ]
        configured_refs = [
            edge for edge in graph.edges
            if edge["kind"] == "EXACT_PATH_REFERENCE"
            and graph.vertices[edge["src_vertex_id"]].get("source") == "configured_git"
        ]
        self.assertTrue(configured_imports)
        self.assertTrue(configured_refs)

        # MCP virtual definitions must remain virtual vertices, never Git structural subjects.
        mcp_vertex_ids = {vid for vid, rec in graph.vertices.items() if rec.get("source") == "mcp"}
        forbidden = {"DIR_CONTAINS", "DIR_PARENT_OF", "PY_IMPORTS", "PY_RELATIVE_IMPORTS", "EXACT_PATH_REFERENCE"}
        self.assertFalse(any(edge["src_vertex_id"] in mcp_vertex_ids and edge["kind"] in forbidden for edge in graph.edges))

        # Both CAS dimensions bind subsequent graph queries to this exact observation.
        receipt = graph.summary(
            expected_snapshot_id=snapshot["snapshot_id"],
            expected_graph_id=graph.graph_id,
        )
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["graph_id"], graph.graph_id)

    def test_live_graph_recompile_is_deterministic_on_stable_v2_snapshot(self):
        root, server = self.live_fixture()
        surface = server.aor_development.project_atlas
        snapshot, hold, _ = surface._snapshot()
        self.assertIsNone(hold)
        first = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        second = compile_v2_snapshot_relation_graph(snapshot, configured_root=root)
        self.assertEqual(first.graph_id, second.graph_id)
        self.assertEqual(
            [edge["edge_id"] for edge in first.edges],
            [edge["edge_id"] for edge in second.edges],
        )


if __name__ == "__main__":
    unittest.main()
