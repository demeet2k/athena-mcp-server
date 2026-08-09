from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
V33 = ROOT / ".github" / "workflows" / "release-v3.3.yml"
V34 = ROOT / ".github" / "workflows" / "release-v3.4.yml"


class HistoricalReleaseLaneIsolationTests(unittest.TestCase):
    def test_v33_is_manual_only_and_cannot_shadow_current_runtime_prs(self):
        text = V33.read_text(encoding="utf-8")
        header = text.split("permissions:", 1)[0]
        self.assertIn("workflow_dispatch:", header)
        self.assertNotIn("pull_request:", header)
        self.assertNotIn("push:", header)
        self.assertIn("RELEASE_VERSION: '3.3.0'", text)
        self.assertIn(
            "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",
            text,
        )
        self.assertIn("release/v3.3.0.json", text)
        self.assertIn("release/v3.3.0.md", text)

    def test_v34_remains_the_current_automatic_release_validation_lane(self):
        text = V34.read_text(encoding="utf-8")
        header = text.split("permissions:", 1)[0]
        self.assertIn("pull_request:", header)
        self.assertIn("branches: [master]", header)
        self.assertIn("push:", header)
        self.assertIn("workflow_dispatch:", header)
        self.assertIn("RELEASE_VERSION: '3.4.0'", text)
        self.assertIn("RELEASE_TAG: v3.4.0", text)

    def test_historical_and_current_release_versions_are_not_aliased(self):
        v33 = V33.read_text(encoding="utf-8")
        v34 = V34.read_text(encoding="utf-8")
        self.assertIn("RELEASE_VERSION: '3.3.0'", v33)
        self.assertIn("RELEASE_VERSION: '3.4.0'", v34)
        self.assertNotEqual(
            "RELEASE_VERSION: '3.3.0'",
            "RELEASE_VERSION: '3.4.0'",
        )


if __name__ == "__main__":
    unittest.main()
