"""Public example pin guards; real temporary Git only, no private brain dependency."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "athena_local_demo.py"
spec = importlib.util.spec_from_file_location("local_demo_example", EXAMPLE)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class LocalDemoPinTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(EXAMPLE), *args],
                              capture_output=True, text=True, timeout=15)

    def test_delivery_pin_is_required_before_import_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            result = self.cli("--brain", tmp, "--mcp", tmp, "--athena", tmp, "--output", str(out))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--mcp-head", result.stderr)
            self.assertFalse(out.exists())

    def test_mutable_or_malformed_delivery_pins_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for pin in ("main", "refs/pull/394/head", "cacc660", "A" * 40, "g" * 40):
                with self.subTest(pin=pin):
                    out = Path(tmp) / "output"
                    result = self.cli("--brain", tmp, "--mcp", tmp, "--athena", tmp,
                                      "--output", str(out), "--mcp-head", pin)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("complete lowercase 40-character", result.stderr)
                    self.assertFalse(out.exists())

    def test_full_delivery_sha_is_retained_without_default(self):
        pin = "a" * 40
        self.assertEqual(demo.commit_sha(pin), pin)
        self.assertEqual(demo.ADAPTER_BASELINE_HEAD, "cacc660071da1c9ba5513b950f94742563f0b13a")

    def test_help_does_not_require_private_checkout(self):
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--mcp-head", result.stdout)

    @unittest.skipUnless(shutil.which("git"), "Git required for real checkout guard")
    def test_real_checkout_pin_and_tracked_edit_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args],
                                               text=True, stderr=subprocess.DEVNULL, timeout=15)
            git("init", "-q")
            git("config", "gc.auto", "0")
            git("config", "maintenance.auto", "false")
            (root / "source.txt").write_text("synthetic source\n", encoding="utf-8")
            git("add", "source.txt")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic checkout guard")
            pin = git("rev-parse", "HEAD").strip()
            demo.verify_checkout(root, pin, "fixture")
            with self.assertRaisesRegex(ValueError, "immutable pin"):
                demo.verify_checkout(root, "0" * 40, "fixture")
            (root / "source.txt").write_text("modified synthetic source\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "tracked source edits"):
                demo.verify_checkout(root, pin, "fixture")


if __name__ == "__main__":
    unittest.main()
