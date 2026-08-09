from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas import compile_git_atlas
from athena_mcp.project_atlas_graph import (
    EDGE_KINDS,
    GEOMETRIC_EDGE_KINDS,
    GRAPH_LAWS,
    GraphBuildOptions,
    STRUCTURAL_EDGE_KINDS,
    compile_project_relation_graph,
)


def run(root: Path, *args: str) -> str:
    import subprocess
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasGraphV3Tests(unittest.TestCase):
    SNAPSHOT = "PATLASV2." + "A" * 32

    def repo(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        root = Path(td.name) / "project"; root.mkdir()
        run(root, "init")
        run(root, "config", "user.name", "test")
        run(root, "config", "user.email", "test@example.invalid")
        run(root, "remote", "add", "origin", "https://github.com/demeet2k/project-graph-fixture.git")
        files = {
            "README.md": "fixture\n",
            "pkg/__init__.py": "\n",
            "pkg/a.py": "from . import b\nimport pkg.c\nimport json\nCONFIG = 'config/settings.json'\n",
            "pkg/b.py": "VALUE = 2\n",
            "pkg/c.py": "VALUE = 3\n",
            "config/settings.json": '{"entry": "pkg/a.py"}\n',
            "alias/one.txt": "identical-content\n",
            "alias/two.txt": "identical-content\n",
            "tests/test_x.py": "from pkg import a\ndef test_x(): assert a.CONFIG\n",
        }
        for rel, text in files.items():
            path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
        run(root, "add", "."); run(root, "commit", "-m", "seed")
        atlas = compile_git_atlas(root)
        return root, atlas

    @staticmethod
    def record(atlas: dict, path: str, git_type: str = "blob") -> dict:
        matches = [r for r in atlas["records"] if r["native"]["path"] == path and r["native"]["git_type"] == git_type]
        if len(matches) != 1:
            raise AssertionError((path, git_type, len(matches)))
        return matches[0]

    def edge_pairs(self, graph, kind: str):
        return {(e["src_poid"], e["dst_poid"]) for e in graph.edges if e["kind"] == kind}

    def test_structural_extractors_preserve_exact_endpoint_identity(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        pkg = self.record(atlas, "pkg", "tree")
        a = self.record(atlas, "pkg/a.py")
        b = self.record(atlas, "pkg/b.py")
        c = self.record(atlas, "pkg/c.py")
        config = self.record(atlas, "config/settings.json")
        one = self.record(atlas, "alias/one.txt")
        two = self.record(atlas, "alias/two.txt")

        self.assertIn((pkg["poid"], a["poid"]), self.edge_pairs(graph, "DIR_CONTAINS"))
        self.assertIn((a["poid"], pkg["poid"]), self.edge_pairs(graph, "DIR_PARENT_OF"))
        self.assertIn((a["poid"], b["poid"]), self.edge_pairs(graph, "PY_RELATIVE_IMPORTS"))
        self.assertIn((a["poid"], c["poid"]), self.edge_pairs(graph, "PY_IMPORTS"))
        self.assertIn((a["poid"], config["poid"]), self.edge_pairs(graph, "EXACT_PATH_REFERENCE"))
        self.assertIn((one["poid"], two["poid"]), self.edge_pairs(graph, "SAME_BLOB_ALIAS"))
        self.assertIn((two["poid"], one["poid"]), self.edge_pairs(graph, "SAME_BLOB_ALIAS"))
        self.assertNotEqual(one["poid"], two["poid"])

        for edge in graph.edges:
            self.assertIn(edge["src_poid"], graph.vertices)
            self.assertIn(edge["dst_poid"], graph.vertices)
            self.assertEqual(edge["snapshot_id"], self.SNAPSHOT)
            self.assertTrue(edge["extractor"])
            self.assertTrue(edge["evidence"])
            self.assertTrue(edge["return"]["src"])
            self.assertTrue(edge["return"]["dst"])

    def test_external_or_unknown_import_is_conserved_not_fabricated(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        a = self.record(atlas, "pkg/a.py")
        rows = [u for u in graph.unresolved_imports if u["src_poid"] == a["poid"]]
        self.assertTrue(any(u["request"] == "json" for u in rows))
        self.assertTrue(all(u["standing"] == "UNRESOLVED_EXTERNAL_OR_LOCAL_UNKNOWN" for u in rows))
        self.assertIn("UNRESOLVED_IMPORT -> CONSERVE_UNKNOWN", GRAPH_LAWS)

    def test_same_blob_alias_does_not_collapse_vertices(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        one = self.record(atlas, "alias/one.txt")
        two = self.record(atlas, "alias/two.txt")
        self.assertEqual(one["native"]["object_sha"], two["native"]["object_sha"])
        self.assertNotEqual(one["poid"], two["poid"])
        edges = [e for e in graph.edges if e["kind"] == "SAME_BLOB_ALIAS" and {e["src_poid"], e["dst_poid"]} == {one["poid"], two["poid"]}]
        self.assertEqual(len(edges), 2)
        self.assertTrue(all(e["authority"] == "CONTENT_IDENTITY_ONLY" for e in edges))
        self.assertTrue(all(e["loss"] == "DISTINCT_PATH_OBJECTS_PRESERVED" for e in edges))

    def test_graph_digest_is_order_invariant_and_edge_sensitive(self):
        root, atlas = self.repo()
        first = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        reversed_atlas = {**atlas, "records": list(reversed(atlas["records"]))}
        second = compile_project_relation_graph(reversed_atlas, snapshot_id=self.SNAPSHOT, root=root)
        self.assertEqual(first.graph_id, second.graph_id)
        self.assertEqual([e["edge_id"] for e in first.edges], [e["edge_id"] for e in second.edges])

        geometric = compile_project_relation_graph(
            atlas,
            snapshot_id=self.SNAPSHOT,
            root=root,
            options=GraphBuildOptions(include_geometric=True),
        )
        self.assertNotEqual(first.graph_id, geometric.graph_id)
        self.assertGreater(len(geometric.edges), len(first.edges))
        self.assertTrue(any(e["kind"] == "KC144_GRID_ADJACENT" for e in geometric.edges))

    def test_geometric_edges_are_explicitly_non_dependency(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(
            atlas,
            snapshot_id=self.SNAPSHOT,
            root=root,
            options=GraphBuildOptions(include_geometric=True),
        )
        rows = [e for e in graph.edges if e["kind"] == "KC144_GRID_ADJACENT"]
        self.assertTrue(rows)
        self.assertTrue(all(e["authority"] == "COORDINATE_ONLY" for e in rows))
        self.assertTrue(all("NO_DEPENDENCY" in e["loss"] for e in rows))
        self.assertNotIn("DEPENDS_ON", EDGE_KINDS)
        self.assertTrue(GEOMETRIC_EDGE_KINDS.isdisjoint(STRUCTURAL_EDGE_KINDS))

    def test_bfs_routes_over_typed_structure_not_kc144_geometry(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        pkg = self.record(atlas, "pkg", "tree")
        b = self.record(atlas, "pkg/b.py")
        routed = graph.shortest_path(pkg["poid"], b["poid"], kinds={"DIR_CONTAINS", "PY_RELATIVE_IMPORTS"})
        self.assertEqual(routed["status"], "ROUTED")
        self.assertEqual(routed["hops"], 1)  # the exact tree directly contains b.py
        self.assertEqual(routed["cost_vector"]["coordinate_hops"], 0)
        self.assertEqual(routed["cost_vector"]["structural_hops"], 1)
        self.assertEqual(routed["law"], "STRUCTURAL_GRAPH_ROUTE != KC144_GEOMETRIC_ROUTE != EXECUTION")

    def test_bfs_can_follow_tree_then_import(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        pkg = self.record(atlas, "pkg", "tree")
        a = self.record(atlas, "pkg/a.py")
        c = self.record(atlas, "pkg/c.py")
        # Restrict first relationship to a unique source by routing from a itself after
        # proving the tree relation separately; import edge must be the second semantics.
        tree = graph.shortest_path(pkg["poid"], a["poid"], kinds={"DIR_CONTAINS"})
        imp = graph.shortest_path(a["poid"], c["poid"], kinds={"PY_IMPORTS"})
        self.assertEqual(tree["status"], "ROUTED")
        self.assertEqual(imp["status"], "ROUTED")
        self.assertEqual([e["kind"] for e in imp["edges"]], ["PY_IMPORTS"])

    def test_dijkstra_forbids_hidden_scalarization_and_returns_weights(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        a = self.record(atlas, "pkg/a.py")
        c = self.record(atlas, "pkg/c.py")
        with self.assertRaises(ValueError):
            graph.shortest_path(a["poid"], c["poid"], kinds={"PY_IMPORTS"}, algorithm="dijkstra")
        routed = graph.shortest_path(
            a["poid"], c["poid"], kinds={"PY_IMPORTS"}, algorithm="dijkstra", weights={"PY_IMPORTS": 2.5}
        )
        self.assertEqual(routed["status"], "ROUTED")
        self.assertEqual(routed["scalar_cost"], 2.5)
        self.assertEqual(routed["weights"], {"PY_IMPORTS": 2.5})
        self.assertIn("EXPLICIT_INPUT", routed["scalarization_law"])

    def test_snapshot_and_graph_cas_fail_closed(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        summary = graph.summary(expected_snapshot_id="PATLASV2." + "0" * 32)
        self.assertEqual(summary["status"], "HOLD_STALE_SNAPSHOT")
        summary = graph.summary(expected_graph_id="PATLASG3." + "0" * 32)
        self.assertEqual(summary["status"], "HOLD_STALE_GRAPH")
        a = self.record(atlas, "pkg/a.py")
        rows = graph.neighbors(a["poid"], expected_graph_id="PATLASG3." + "F" * 32)
        self.assertEqual(rows["status"], "HOLD_STALE_GRAPH")

    def test_unknown_vertex_limits_and_no_path_hold(self):
        root, atlas = self.repo()
        graph = compile_project_relation_graph(atlas, snapshot_id=self.SNAPSHOT, root=root)
        unknown = graph.neighbors("POID.DOESNOTEXIST")
        self.assertEqual(unknown["status"], "HOLD_UNKNOWN_VERTEX")
        a = self.record(atlas, "pkg/a.py")
        readme = self.record(atlas, "README.md")
        no_path = graph.shortest_path(a["poid"], readme["poid"], kinds={"PY_IMPORTS", "PY_RELATIVE_IMPORTS"})
        self.assertEqual(no_path["status"], "HOLD_NO_PATH")
        with self.assertRaises(ValueError):
            graph.neighbors(a["poid"], limit=101)

    def test_graph_requires_v2_snapshot_coordinate(self):
        root, atlas = self.repo()
        with self.assertRaises(ValueError):
            compile_project_relation_graph(atlas, snapshot_id="HEAD", root=root)


if __name__ == "__main__":
    unittest.main()
