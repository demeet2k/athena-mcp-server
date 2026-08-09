import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "canary-v3.3.yml"


class CanaryWorkflowSubjectGuardTests(unittest.TestCase):
    def _workflow(self) -> str:
        return WORKFLOW.read_text()

    def _subject_prefix(self, workflow: str) -> str:
        match = re.search(r"^  CANARY_SUBJECT: (.+)$", workflow, re.MULTILINE)
        self.assertIsNotNone(match, "CANARY_SUBJECT must remain explicit in the workflow")
        return match.group(1)

    def test_outer_and_inner_guards_use_the_same_semantic_prefix(self):
        workflow = self._workflow()
        prefix = self._subject_prefix(workflow)

        self.assertIn(
            f"startsWith(github.event.head_commit.message, '{prefix}')",
            workflow,
        )
        self.assertIn('case "$CURRENT_SUBJECT" in', workflow)
        self.assertIn('"$CANARY_SUBJECT"*) ;;', workflow)
        self.assertNotIn(
            'test "$(git show -s --format=%s HEAD)" = "$CANARY_SUBJECT"',
            workflow,
        )

    def test_repair_suffixes_remain_in_the_same_canary_trigger_class(self):
        workflow = self._workflow()
        prefix = self._subject_prefix(workflow)

        accepted = (
            prefix,
            prefix + " — import-path repair",
            prefix + " — workflow guard repair",
        )
        rejected = (
            "Update README",
            "Observe ATHENA v3.2.0 isolated canary",
        )

        for subject in accepted:
            self.assertTrue(subject.startswith(prefix), subject)
        for subject in rejected:
            self.assertFalse(subject.startswith(prefix), subject)


if __name__ == "__main__":
    unittest.main()
