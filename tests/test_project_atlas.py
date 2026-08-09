from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas import (
    COLUMN_AXIS,
    ROW_AXIS,
    classify_col,
    classify_row,
    compile_git_atlas,
    federate_atlases,
    mcp_surface_atlas,
    project_coordinate,
    route_records,
    semantic_station,
    validate_atlas,
)


def run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


class ProjectAtlasTests(unittest.TestCase):
    def repo(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name) / "brain"
        root.mkdir()
        run(root, "init")
        run(root, "config", "user.name", "test")
        run(root, "config", "user.email", "test@example.invalid")
        run(root, "remote", "add", "origin", "https://github.com/demeet2k/Athena.git")
        files = {
            "ATHENA.manifest.json": "{}\n",
            "athena_mcp/server.py": "TOOLS=[]\n",
            "coordinates/POLYATLAS.json": "{}\n",
            "navigation/README.md": "nav\n",
            "schemas/example.schema.json": "{}\n",
            "tests/test_runtime.py": "def test_x(): pass\n",
            ".github/workflows/ci.yml": "name: ci\n",
            "release/v1.json": "{}\n",
            "ledger/events/e1.json": "{}\n",
        }
        for rel, text in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        run(root, "add", ".")
        run(root, "commit", "-m", "seed")
        return root

    def test_semantic_grid_is_12_by_12_and_meaningful(self):
        self.assertEqual(len(ROW_AXIS), 12)
        self.assertEqual(len(COLUMN_AXIS), 12)
        self.assertEqual(classify_row("navigation/router.py"), 5)
        self.assertEqual(classify_col("navigation/router.py"), 3)
        self.assertEqual(classify_row("tests/test_runtime.py"), 8)
        self.assertEqual(classify_col("tests/test_runtime.py"), 7)
        self.assertEqual(classify_row("release/v3.4.0.json"), 11)
        self.assertEqual(classify_row("ledger/events/e.json"), 12)
        st = semantic_station("tests/test_runtime.py")
        self.assertEqual(st["gid"], 12 * 7 + 7)
        self.assertEqual(st["row_semantic"], "VERIFY_TEST")
        self.assertEqual(st["col_semantic"], "TEST_WITNESS")

    def test_project_coordinate_separates_station_from_identity(self):
        base = dict(repo_key="github.com/demeet2k/Athena", ref="main", head="a" * 40, tree="b" * 40, git_type="blob", mode="100644")
        a = project_coordinate(path="alpha.py", object_sha="1" * 40, **base)
        b = project_coordinate(path="beta.py", object_sha="2" * 40, **base)
        self.assertNotEqual(a["poid"], b["poid"])
        self.assertNotEqual(a["fiber"], b["fiber"])
        self.assertTrue(a["return"]["git_show"].startswith("a" * 40))
        self.assertIn("KC144_STATION != OBJECT_IDENTITY", a["laws"])

    def test_compiler_covers_every_git_tree_object_and_roundtrips(self):
        root = self.repo()
        atlas = compile_git_atlas(root)
        raw = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "-t", "HEAD"], text=True)
        self.assertEqual(atlas["counts"]["entries"], len(raw.splitlines()))
        self.assertEqual(atlas["repository"]["repo_key"], "github.com/demeet2k/Athena")
        self.assertEqual(validate_atlas(atlas)["status"], "PASS")
        paths = {r["native"]["path"] for r in atlas["records"]}
        self.assertIn("navigation/README.md", paths)
        self.assertIn("tests/test_runtime.py", paths)
        poids = [r["poid"] for r in atlas["records"]]
        self.assertEqual(len(poids), len(set(poids)))
        for rec in atlas["records"]:
            self.assertEqual(rec["native"]["head"], atlas["repository"]["head"])
            self.assertEqual(rec["native"]["tree"], atlas["repository"]["tree"])
            self.assertTrue(rec["route"])

    def test_same_blob_is_indexed_but_not_collapsed(self):
        root = self.repo()
        (root / "copy.md").write_text("nav\n")
        run(root, "add", ".")
        run(root, "commit", "-m", "copy")
        atlas = compile_git_atlas(root)
        nav = next(r for r in atlas["records"] if r["native"]["path"] == "navigation/README.md")
        copy = next(r for r in atlas["records"] if r["native"]["path"] == "copy.md")
        self.assertEqual(nav["native"]["object_sha"], copy["native"]["object_sha"])
        self.assertNotEqual(nav["poid"], copy["poid"])
        self.assertEqual(len(atlas["indexes"]["by_blob"][nav["native"]["object_sha"]]), 2)

    def test_unrelated_head_change_preserves_path_coordinate_and_changes_version_fiber(self):
        root = self.repo()
        first = compile_git_atlas(root)
        rec1 = next(r for r in first["records"] if r["native"]["path"] == "navigation/README.md")
        (root / "new.txt").write_text("new\n")
        run(root, "add", ".")
        run(root, "commit", "-m", "unrelated")
        second = compile_git_atlas(root)
        rec2 = next(r for r in second["records"] if r["native"]["path"] == "navigation/README.md")
        self.assertEqual(rec1["poid"], rec2["poid"])
        self.assertEqual(rec1["fiber"], rec2["fiber"])
        self.assertEqual(rec1["project_kc144"], rec2["project_kc144"])
        self.assertNotEqual(rec1["version_fiber"], rec2["version_fiber"])

    def test_mcp_surface_is_virtual_and_head_qualified(self):
        tools = [
            {"name": "athena_resolve", "inputSchema": {"type": "object"}},
            {"name": "athena_hydrate", "inputSchema": {"type": "object"}},
        ]
        surface = mcp_surface_atlas(repo_key="github.com/demeet2k/athena-mcp-server", head="c" * 40, server_name="athena-canonical-mcp", tools=tools)
        self.assertEqual(surface["count"], 2)
        self.assertEqual({r["mcp"]["name"] for r in surface["records"]}, {"athena_resolve", "athena_hydrate"})
        self.assertTrue(all(r["native"]["head"] == "c" * 40 for r in surface["records"]))
        self.assertTrue(all(r["native"]["git_type"] == "mcp_tool" for r in surface["records"]))

    def test_cross_repo_federation_never_collapses_heads(self):
        root = self.repo()
        atlas = compile_git_atlas(root)
        surface = mcp_surface_atlas(repo_key="github.com/demeet2k/athena-mcp-server", head="d" * 40, server_name="athena-canonical-mcp", tools=[])
        f = federate_atlases([atlas], [surface])
        self.assertEqual(f["count"], 2)
        self.assertEqual(len({(x["kind"], x["repo_key"], x["head"]) for x in f["roots"]}), 2)
        self.assertIn("EXACT_REPO_HEAD", f["law"])

    def test_station_route_reaches_destination_and_can_wrap(self):
        base = dict(repo_key="r", ref="main", head="a" * 40, tree="b" * 40, object_sha="c" * 40, git_type="blob", mode="100644")
        src = project_coordinate(path="policies/PROMPT_RUNTIME.md", **base)
        dst = project_coordinate(path="tests/test_runtime.py", **base)
        route = route_records(src, dst)
        self.assertEqual(route["station_route"][0]["gid"], src["project_kc144"]["gid"])
        self.assertEqual(route["station_route"][-1]["gid"], dst["project_kc144"]["gid"])
        wrapped = route_records(src, dst, wrap=True)
        self.assertLessEqual(wrapped["hops"], route["hops"])


if __name__ == "__main__":
    unittest.main()
