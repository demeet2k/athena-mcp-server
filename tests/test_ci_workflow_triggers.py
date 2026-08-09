from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class CIWorkflowTriggerContractTests(unittest.TestCase):
    def test_feature_branch_push_and_pr_do_not_duplicate_full_ci(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        trigger_block = text.split("permissions:", 1)[0]

        self.assertNotIn("on: [push, pull_request]", trigger_block)
        self.assertIn("on:\n  push:\n    branches: [master]", trigger_block)
        self.assertIn("  pull_request:\n    branches: [master]", trigger_block)

    def test_both_required_witness_classes_remain(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        trigger_block = text.split("permissions:", 1)[0]

        self.assertEqual(trigger_block.count("  push:"), 1)
        self.assertEqual(trigger_block.count("  pull_request:"), 1)
        self.assertEqual(trigger_block.count("    branches: [master]"), 2)


if __name__ == "__main__":
    unittest.main()
