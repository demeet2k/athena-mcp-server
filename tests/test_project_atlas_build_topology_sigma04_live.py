from __future__ import annotations

import unittest
from pathlib import Path

from athena_mcp.identity import digest
from athena_mcp.project_atlas import compile_git_atlas
from athena_mcp.project_atlas_build_topology import ENTRYPOINT_EDGE, compile_build_topology
from athena_mcp.project_atlas_graph import compile_project_relation_graph, git_blob_reader


class Sigma04LiveRepositoryTests(unittest.TestCase):
    def test_live_pyproject_scripts_resolve_to_exact_ast_symbols(self):
        root = Path(__file__).resolve().parents[1]
        atlas = compile_git_atlas(root)
        snapshot_id = "PATLASV2." + digest(
            {"head": atlas["repository"]["head"], "tree": atlas["repository"]["tree"], "purpose": "SIGMA04_LIVE"},
            32,
        )
        graph = compile_project_relation_graph(atlas, snapshot_id=snapshot_id, root=root)
        topology = compile_build_topology(graph, blob_reader=git_blob_reader(root))

        edges = [e for e in topology.edges if e["kind"] == ENTRYPOINT_EDGE]
        by_name = {e["witness"]["entrypoint_name"]: e for e in edges}
        self.assertEqual(set(by_name), {"athena-mcp", "athena-project-atlas"})

        expected = {
            "athena-mcp": ("athena_mcp.server:main", "athena_mcp.server.main", "athena_mcp/server.py"),
            "athena-project-atlas": ("athena_mcp.project_atlas:_main", "athena_mcp.project_atlas._main", "athena_mcp/project_atlas.py"),
        }
        for name, (target, qualified_symbol, path) in expected.items():
            edge = by_name[name]
            self.assertEqual(edge["witness"]["target"], target)
            self.assertEqual(edge["snapshot_id"], graph.snapshot_id)
            self.assertEqual(edge["parent_graph_id"], graph.graph_id)
            symbol = topology.symbol_index.by_psym[edge["dst_psym"]]
            self.assertEqual(symbol["qualified_symbol"], qualified_symbol)
            self.assertEqual(symbol["path"], path)
            self.assertEqual(symbol["vertex_id"], edge["dst_vertex_id"])
            self.assertEqual(symbol["poid"], edge["dst_poid"])
            self.assertEqual(symbol["head"], atlas["repository"]["head"])
            self.assertTrue(symbol["return"]["uri"].startswith("athena+git://"))
            self.assertIn("#L", symbol["return"]["uri"])

        pyproject_edges = {e["src_vertex_id"] for e in edges}
        self.assertEqual(len(pyproject_edges), 1)
        pyproject_vertex = graph.vertices[next(iter(pyproject_edges))]
        self.assertEqual(pyproject_vertex["native"]["path"], "pyproject.toml")
        self.assertEqual(pyproject_vertex["native"]["head"], atlas["repository"]["head"])

        summary = topology.summary()
        self.assertEqual(summary["edges"], 2)
        self.assertEqual(summary["edge_counts"][ENTRYPOINT_EDGE], 2)
        self.assertGreater(summary["symbols"], 2)
        self.assertEqual(summary["authority"], "NONE")


if __name__ == "__main__":
    unittest.main()
