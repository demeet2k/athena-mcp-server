from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from athena_mcp.git_backend import GitBackend
from athena_mcp.prompt_runtime import PROMPT_RUNTIME_TOOL_NAMES, PromptRuntime
from athena_mcp.protocol import TOOLS


class MessageBoardRegistrationTests(unittest.TestCase):
    def test_tool_is_registered_in_prompt_and_protocol_surfaces(self):
        self.assertIn("athena_message_board", PROMPT_RUNTIME_TOOL_NAMES)
        self.assertIn("athena_message_board", {tool["name"] for tool in TOOLS})

    def test_prompt_runtime_dispatches_message_board_tool(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            proc = subprocess.run(["git", "init", "-b", "master", str(root)], text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            for key, value in (("user.name", "test"), ("user.email", "test@example.invalid")):
                proc = subprocess.run(["git", "-C", str(root), "config", key, value], text=True, capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            for args in (("add", "."), ("commit", "-m", "seed")):
                proc = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

            runtime = PromptRuntime(GitBackend(root))
            result = runtime.call_tool("athena_message_board", {"action": "read", "shared_remote_mode": "DISABLED"})
            self.assertEqual(result["artifact"], "ATHENA.MESSAGE.BOARD.SNAPSHOT.V1")
            self.assertEqual(result["status"], "OK")


if __name__ == "__main__":
    unittest.main()
