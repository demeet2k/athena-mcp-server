from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.project_atlas import compile_runtime_atlas
from athena_mcp.protocol import PROMPTS, SERVER_INFO, TOOLS


def run(root: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if p.returncode:
        raise AssertionError(p.stderr or p.stdout)
    return p.stdout.strip()


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


if __name__ == "__main__":
    unittest.main()
