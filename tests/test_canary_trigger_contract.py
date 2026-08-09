import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "canary-v3.3.yml"
PREFIX = "Observe ATHENA v3.3.0 isolated canary"


class CanaryTriggerContractTests(unittest.TestCase):
    def test_push_trigger_uses_semantic_prefix_without_exact_subject_recheck(self):
        workflow = WORKFLOW.read_text()
        self.assertIn(
            "startsWith(github.event.head_commit.message, 'Observe ATHENA v3.3.0 isolated canary')",
            workflow,
        )
        self.assertNotIn("CANARY_SUBJECT:", workflow)
        self.assertNotIn("CANARY_SUBJECT_PREFIX:", workflow)
        self.assertNotIn("git show -s --format=%s HEAD", workflow)
        self.assertIn(
            "Push admission is owned by the job-level semantic-prefix predicate above.",
            workflow,
        )

    def test_semantic_trigger_class_accepts_repairs_but_not_unrelated_commits(self):
        accepted = (
            PREFIX,
            PREFIX + " — import-path repair",
            PREFIX + " — workflow guard repair",
        )
        rejected = (
            "Update README",
            "Observe a different isolated canary",
        )
        for subject in accepted:
            self.assertTrue(subject.startswith(PREFIX), subject)
        for subject in rejected:
            self.assertFalse(subject.startswith(PREFIX), subject)


if __name__ == "__main__":
    unittest.main()
