"""Real child-process regressions for the fixed Wiki worker supervisor."""
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from athena_mcp.wiki_git import _run_bounded


class BoundedWorkerTests(unittest.TestCase):
    def run_worker(self, code, *, input=b"{}", timeout=3, cap=65536):
        with tempfile.TemporaryDirectory() as directory:
            worker = Path(directory) / "worker.py"
            worker.write_text(code, encoding="utf-8")
            command = [sys.executable, "-I", "-B", str(worker)]
            children = []
            original = subprocess.Popen

            def capture(*args, **kwargs):
                child = original(*args, **kwargs)
                children.append(child)
                return child

            started = time.monotonic()
            try:
                with patch("athena_mcp.wiki_git.subprocess.Popen", side_effect=capture):
                    return _run_bounded(command, input=input, cwd=directory,
                                        timeout=timeout, max_output_bytes=cap)
            finally:
                self.assertEqual(len(children), 1)
                self.assertIsNotNone(children[0].poll(), "direct worker must be reaped")
                self.assertLess(time.monotonic() - started, timeout + 2)
                for pipe in (children[0].stdin, children[0].stdout, children[0].stderr):
                    self.assertTrue(pipe.closed)

    def test_normal_request_response_and_small_stderr(self):
        result = self.run_worker("import sys\nr=sys.stdin.buffer.read()\nsys.stdout.buffer.write(r)\nsys.stderr.write('diagnostic')\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"{}")
        self.assertEqual(result.stderr, b"diagnostic")

    def test_failed_worker_preserves_bounded_diagnostic(self):
        result = self.run_worker("import sys\nsys.stderr.write('worker failure')\nsys.exit(7)\n")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.stderr, b"worker failure")

    def test_stdout_and_stderr_flood_are_killed_before_timeout(self):
        for stream in ("stdout", "stderr"):
            with self.subTest(stream=stream), self.assertRaisesRegex(ValueError, "RESPONSE_TOO_LARGE"):
                self.run_worker("import os\nwhile True: os.write(" + ("1" if stream == "stdout" else "2") + ", b'x'*8192)\n", timeout=3)

    def test_budget_counts_both_streams(self):
        with self.assertRaisesRegex(ValueError, "RESPONSE_TOO_LARGE"):
            self.run_worker("import os\nos.write(1,b'a'*40000)\nos.write(2,b'b'*40000)\n")

    def test_exact_budget_is_accepted(self):
        result = self.run_worker("import os\nos.write(1,b'a'*32768)\nos.write(2,b'b'*32768)\n")
        self.assertEqual(len(result.stdout) + len(result.stderr), 65536)

    def test_hung_worker_is_killed_and_reaped(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_worker("import time\ntime.sleep(30)\n", timeout=0.25)

    def test_unread_request_cannot_block_supervisor(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_worker("import time\ntime.sleep(30)\n", input=b'x'*1000000, timeout=0.25)


if __name__ == "__main__":
    unittest.main()
