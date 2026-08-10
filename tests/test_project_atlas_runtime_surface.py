from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas import compile_runtime_atlas
from athena_mcp.protocol import PROMPTS, SERVER_INFO, TOOLS

ROOT = Path(__file__).resolve().parents[1]


def run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


def tree_identity(root: Path) -> set[tuple[str, str]]:
    rows = set()
    raw = run(root, "ls-tree", "-r", "-t", "HEAD")
    for line in raw.splitlines():
        meta, path = line.split("\t", 1)
        _mode, git_type, _sha = meta.split(" ", 2)
        rows.add((path, git_type))
    return rows


class ProjectAtlasRuntimeSurfaceTests(unittest.TestCase):
    def test_runtime_compiler_coordinates_every_installed_tool_and_prompt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "runtime"
            root.mkdir()
            run(root, "init")
            run(root, "config", "user.name", "test")
            run(root, "config", "user.email", "test@example.invalid")
            run(root, "remote", "add", "origin", "https://github.com/demeet2k/athena-mcp-server.git")
            (root / "README.md").write_text("runtime\n", encoding="utf-8")
            run(root, "add", ".")
            run(root, "commit", "-m", "seed")

            compiled = compile_runtime_atlas(root)

        surface = compiled["mcp_surface"]
        self.assertEqual(surface["server"], SERVER_INFO["name"])
        self.assertEqual(surface["count"], len(TOOLS) + len(PROMPTS))
        expected = {(kind, row["name"]) for kind, rows in (("tool", TOOLS), ("prompt", PROMPTS)) for row in rows}
        observed = {(r["mcp"]["kind"], r["mcp"]["name"]) for r in surface["records"]}
        self.assertEqual(observed, expected)
        self.assertTrue(all(r["return"]["uri"].startswith("athena+mcp://") for r in surface["records"]))
        self.assertEqual(compiled["federation"]["count"], 2)
        self.assertEqual(compiled["federation"]["roots"][0]["head"], compiled["git"]["repository"]["head"])
        self.assertEqual(compiled["federation"]["roots"][1]["head"], compiled["git"]["repository"]["head"])

    def test_live_checkout_head_has_complete_git_and_mcp_coordinates(self):
        if not (ROOT / ".git").exists():
            self.skipTest("live checkout witness requires repository .git metadata")
        expected_head = run(ROOT, "rev-parse", "HEAD")
        expected_tree = run(ROOT, "rev-parse", "HEAD^{tree}")
        expected_entries = tree_identity(ROOT)

        compiled = compile_runtime_atlas(ROOT)
        git_atlas = compiled["git"]
        observed_entries = {(r["native"]["path"], r["native"]["git_type"]) for r in git_atlas["records"]}

        self.assertEqual(git_atlas["repository"]["head"], expected_head)
        self.assertEqual(git_atlas["repository"]["tree"], expected_tree)
        self.assertEqual(observed_entries, expected_entries)
        self.assertEqual(git_atlas["counts"]["entries"], len(expected_entries))
        self.assertIn(("athena_mcp/project_atlas.py", "blob"), observed_entries)
        self.assertIn(("tests/test_project_atlas.py", "blob"), observed_entries)
        self.assertEqual(compiled["mcp_surface"]["count"], len(TOOLS) + len(PROMPTS))
        self.assertTrue(compiled["git"]["atlas_digest"])
        self.assertTrue(compiled["mcp_surface"]["surface_digest"])
        self.assertTrue(compiled["federation"]["federation_digest"])


if __name__ == "__main__":
    unittest.main()
