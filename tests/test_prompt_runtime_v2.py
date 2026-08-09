from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PromptRuntime


def _run(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if proc.returncode:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout.strip()


def _write(root: Path, rel: str, value: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _fixture(root: Path) -> None:
    _run(root, "init", "-b", "master")
    _run(root, "config", "user.name", "prompt-v2-test")
    _run(root, "config", "user.email", "prompt-v2@example.invalid")
    manifest = {
        "artifact": "ATHENA.PROMPT.RUNTIME.V2", "active_state": "prompts/state/ACTIVE.json",
        "policy": "policies/PROMPT_RUNTIME.md", "default_profile": "MAXDEV",
        "profiles": {"MAXDEV": ["core"]},
        "modules": {"core": {"path": "prompts/CORE.md", "order": 0, "mandatory": True}},
        "authority_ceiling": "NO_HIGHER_AUTHORITY",
    }
    active = {
        "artifact": "ATHENA.PROMPT.STATE.ACTIVE.V2", "prompt_runtime": "ATHENA.PROMPT.RUNTIME.V2",
        "status": "ACTIVE", "profile": "MAXDEV", "enabled_modules": ["core"], "revision": 1,
        "active_scoped_overlays": ["prompts/overlays/GLOBAL.md"],
        "active_scoped_state": ["prompts/state/GLOBAL.json"],
    }
    state = {"artifact": "ATHENA.PROMPT.OVERLAY.STATE.TEST.V1", "status": "ACTIVE_SCOPED", "overlay": "prompts/overlays/GLOBAL.md", "activation": {"automatic": True}}
    _write(root, "prompts/PROMPT.manifest.json", json.dumps(manifest))
    _write(root, "prompts/state/ACTIVE.json", json.dumps(active))
    _write(root, "prompts/state/GLOBAL.json", json.dumps(state))
    _write(root, "prompts/CORE.md", "core\n")
    _write(root, "prompts/overlays/GLOBAL.md", "global overlay\n")
    _write(root, "policies/PROMPT_RUNTIME.md", "policy\n")
    _run(root, "add", ".")
    _run(root, "commit", "-m", "fixture")


class PromptRuntimeV2Tests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        _fixture(self.root)
        self.runtime = PromptRuntime(GitBackend(self.root))

    def test_string_overlay_and_state_compile_into_exact_ancestry(self):
        result = self.runtime.compile(task="material task", profile="MAXDEV")
        self.assertEqual(result["artifact"], "ATHENA.PROMPT.RUNTIME.V2")
        self.assertEqual(result["selected_modules"], ["core"])
        self.assertEqual(result["selected_overlays"], ["ATHENA.PROMPT.OVERLAY.STATE.TEST.V1"])
        overlay = result["ancestry"]["overlays"][0]
        self.assertEqual(overlay["path"], "prompts/overlays/GLOBAL.md")
        self.assertEqual(overlay["state_path"], "prompts/state/GLOBAL.json")
        self.assertIn("prompt_content_digest", result)

    def test_state_mutation_changes_content_digest(self):
        before = self.runtime.compile(include_text=False)["prompt_content_digest"]
        state_path = self.root / "prompts/state/GLOBAL.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["mutation"] = "changed"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        after = self.runtime.compile(include_text=False)["prompt_content_digest"]
        self.assertNotEqual(before, after)

    def test_missing_inactive_and_ambiguous_state_fail_closed(self):
        state_path = self.root / "prompts/state/GLOBAL.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["status"] = "CANDIDATE"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "lacks ACTIVE_SCOPED state"):
            self.runtime.compile()
        state["status"] = "ACTIVE_SCOPED"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        active_path = self.root / "prompts/state/ACTIVE.json"
        active = json.loads(active_path.read_text(encoding="utf-8"))
        active["active_scoped_state"].append("prompts/state/DUPLICATE.json")
        active_path.write_text(json.dumps(active), encoding="utf-8")
        _write(self.root, "prompts/state/DUPLICATE.json", json.dumps(state))
        with self.assertRaisesRegex(ValueError, "ambiguous overlay state binding"):
            self.runtime.compile()


if __name__ == "__main__":
    unittest.main()
