from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from athena_mcp.identity import digest
from athena_mcp.project_atlas import compile_git_atlas
from athena_mcp.project_atlas_build_topology import (
    BUILD_LAWS,
    BUILD_SCHEMA,
    BUILD_VERSION,
    ENTRYPOINT_EDGE,
    SYMBOL_PREFIX,
    compile_build_topology,
)
from athena_mcp.project_atlas_graph import compile_project_relation_graph, git_blob_reader


def run(root: Path, *args: str) -> str:
    import subprocess
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class Sigma04BuildTopologyTests(unittest.TestCase):
    def fixture(self, *, include_bad: bool = True):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        root = Path(td.name) / "project"; root.mkdir()
        run(root, "init")
        run(root, "config", "user.name", "test")
        run(root, "config", "user.email", "test@example.invalid")
        run(root, "remote", "add", "origin", "https://github.com/demeet2k/sigma04-fixture.git")
        pyproject = """[build-system]
requires = [\"setuptools>=70\"]
build-backend = \"setuptools.build_meta\"

[project]
name = \"sigma04-fixture\"
version = \"0.1.0\"

[project.scripts]
good-cli = \"pkg.cli:main\"
async-cli = \"pkg.cli:amain\"
constant-cli = \"pkg.cli:ENTRY\"
"""
        if include_bad:
            pyproject += """missing-symbol = \"pkg.cli:nope\"
external-cli = \"thirdparty.tool:main\"
nested-cli = \"pkg.cli:Runner.run\"
duplicate-cli = \"pkg.dupe:run\"
"""
        files = {
            "pyproject.toml": pyproject,
            "pkg/__init__.py": "\n",
            "pkg/cli.py": (
                "ENTRY = 'main'\n"
                "def main():\n    return 0\n\n"
                "async def amain():\n    return 0\n\n"
                "class Runner:\n    def run(self):\n        return 0\n"
            ),
            "pkg/dupe.py": "def run():\n    return 1\n\ndef run():\n    return 2\n",
        }
        for rel, text in files.items():
            path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
        run(root, "add", "."); run(root, "commit", "-m", "seed")
        atlas = compile_git_atlas(root)
        snapshot_id = "PATLASV2." + digest({"head": atlas["repository"]["head"], "test": "sigma04"}, 32)
        graph = compile_project_relation_graph(atlas, snapshot_id=snapshot_id, root=root)
        topology = compile_build_topology(graph, blob_reader=git_blob_reader(root))
        return root, atlas, graph, topology

    def test_exact_entrypoints_resolve_to_unique_psym(self):
        _, _, graph, topology = self.fixture()
        by_name = {e["witness"]["entrypoint_name"]: e for e in topology.edges}
        self.assertEqual(set(by_name), {"good-cli", "async-cli", "constant-cli"})
        for name, edge in by_name.items():
            self.assertEqual(edge["kind"], ENTRYPOINT_EDGE)
            self.assertEqual(edge["parent_graph_id"], graph.graph_id)
            self.assertEqual(edge["snapshot_id"], graph.snapshot_id)
            self.assertTrue(edge["dst_psym"].startswith(SYMBOL_PREFIX))
            self.assertIn(edge["dst_psym"], topology.symbol_index.by_psym)
            symbol = topology.symbol_index.by_psym[edge["dst_psym"]]
            self.assertEqual(symbol["vertex_id"], edge["dst_vertex_id"])
            self.assertEqual(symbol["poid"], edge["dst_poid"])
            self.assertIn("#L", symbol["return"]["uri"])
            self.assertTrue(edge["return"]["source"].startswith("athena+git://"))
            self.assertIn("#L", edge["return"]["destination"])
        self.assertEqual(by_name["good-cli"]["witness"]["target"], "pkg.cli:main")
        self.assertEqual(by_name["async-cli"]["witness"]["target"], "pkg.cli:amain")
        self.assertEqual(by_name["constant-cli"]["witness"]["target"], "pkg.cli:ENTRY")

    def test_bad_entrypoints_fail_closed_by_reason(self):
        _, _, _, topology = self.fixture()
        holds = topology.holds
        by_entrypoint = {}
        for hold in holds:
            declaration = hold.get("declaration") or {}
            if declaration.get("name"):
                by_entrypoint[declaration["name"]] = hold
        self.assertEqual(by_entrypoint["missing-symbol"]["status"], "HOLD_ENTRYPOINT_SYMBOL")
        self.assertEqual(by_entrypoint["external-cli"]["status"], "HOLD_ENTRYPOINT_MODULE")
        self.assertEqual(by_entrypoint["nested-cli"]["status"], "HOLD_NESTED_ENTRYPOINT_SYMBOL")
        self.assertEqual(by_entrypoint["duplicate-cli"]["status"], "HOLD_AMBIGUOUS_SYMBOL")
        self.assertEqual(len(by_entrypoint["duplicate-cli"]["candidate_psyms"]), 2)
        self.assertTrue(any(h["status"] == "HOLD_AMBIGUOUS_SYMBOL" and h.get("name") == "run" for h in holds))

    def test_psym_preserves_exact_vertex_and_source_span(self):
        _, _, graph, topology = self.fixture(include_bad=False)
        main_symbols = [s for s in topology.symbol_index.symbols if s["qualified_symbol"] == "pkg.cli.main"]
        self.assertEqual(len(main_symbols), 1)
        symbol = main_symbols[0]
        self.assertTrue(symbol["psym"].startswith(SYMBOL_PREFIX))
        self.assertIn(symbol["vertex_id"], graph.vertices)
        self.assertEqual(graph.vertices[symbol["vertex_id"]]["native"]["path"], "pkg/cli.py")
        self.assertGreater(symbol["span"]["lineno"], 0)
        self.assertGreaterEqual(symbol["span"]["end_lineno"], symbol["span"]["lineno"])
        self.assertEqual(len(symbol["source_span_digest"]), 64)
        self.assertEqual(symbol["authority"], "STRUCTURAL_DEFINITION_ONLY")

    def test_symbol_index_and_build_graph_are_enumeration_invariant(self):
        root, atlas, graph, first = self.fixture(include_bad=False)
        reversed_atlas = {**atlas, "records": list(reversed(atlas["records"]))}
        second_graph = compile_project_relation_graph(reversed_atlas, snapshot_id=graph.snapshot_id, root=root)
        second = compile_build_topology(second_graph, blob_reader=git_blob_reader(root))
        self.assertEqual(graph.graph_id, second_graph.graph_id)
        self.assertEqual(first.symbol_index.index_id, second.symbol_index.index_id)
        self.assertEqual(first.build_graph_id, second.build_graph_id)
        self.assertEqual([e["edge_id"] for e in first.edges], [e["edge_id"] for e in second.edges])

    def test_symbol_redefinition_changes_psym_at_new_exact_head(self):
        root, _, graph1, first = self.fixture(include_bad=False)
        before = next(s["psym"] for s in first.symbol_index.symbols if s["qualified_symbol"] == "pkg.cli.main")
        path = root / "pkg/cli.py"
        text = path.read_text(encoding="utf-8").replace("def main():\n    return 0", "def main():\n    return 7")
        path.write_text(text, encoding="utf-8")
        run(root, "add", "pkg/cli.py"); run(root, "commit", "-m", "change main")
        atlas2 = compile_git_atlas(root)
        snapshot2 = "PATLASV2." + digest({"head": atlas2["repository"]["head"], "test": "sigma04"}, 32)
        graph2 = compile_project_relation_graph(atlas2, snapshot_id=snapshot2, root=root)
        second = compile_build_topology(graph2, blob_reader=git_blob_reader(root))
        after = next(s["psym"] for s in second.symbol_index.symbols if s["qualified_symbol"] == "pkg.cli.main")
        self.assertNotEqual(graph1.snapshot_id, graph2.snapshot_id)
        self.assertNotEqual(before, after)
        self.assertNotEqual(first.build_graph_id, second.build_graph_id)

    def test_summary_is_non_authoritative_and_machine_named(self):
        _, _, graph, topology = self.fixture()
        summary = topology.summary()
        self.assertEqual(summary["schema"], BUILD_SCHEMA)
        self.assertEqual(summary["version"], BUILD_VERSION)
        self.assertEqual(summary["parent_graph_id"], graph.graph_id)
        self.assertEqual(summary["build_graph_id"], topology.build_graph_id)
        self.assertEqual(summary["edge_counts"][ENTRYPOINT_EDGE], 3)
        self.assertEqual(summary["authority"], "NONE")
        self.assertIn("PSYM != POID != PVTX != OID", BUILD_LAWS)
        self.assertIn("BUILD_EDGE != EXECUTION", BUILD_LAWS)


if __name__ == "__main__":
    unittest.main()
