import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class DeploymentCanarySubjectGateV1Tests(unittest.TestCase):
    def setUp(self):
        self.workflow = (ROOT / ".github" / "workflows" / "canary-v3.3.yml").read_text()

    def test_push_subject_gate_accepts_only_canonical_exact_or_em_dash_suffix(self):
        text = self.workflow
        for fragment in (
            "SUBJECT=$(git show -s --format=%s HEAD)",
            'case "$SUBJECT" in',
            '"$CANARY_SUBJECT"|"$CANARY_SUBJECT — "*) ;;',
            'unexpected canary subject: $SUBJECT',
        ):
            self.assertIn(fragment, text)
        self.assertNotIn(
            'test "$(git show -s --format=%s HEAD)" = "$CANARY_SUBJECT"',
            text,
        )

    def test_trigger_and_preflight_share_the_same_canonical_prefix(self):
        canonical = "Observe ATHENA v3.3.0 isolated canary"
        self.assertIn(
            "startsWith(github.event.head_commit.message, " + repr(canonical) + ")",
            self.workflow,
        )
        self.assertIn(f"CANARY_SUBJECT: {canonical}", self.workflow)

    def test_subject_repair_does_not_expand_effect_authority(self):
        for forbidden in (
            "contents: write",
            "packages: write",
            "kubectl apply",
            "helm upgrade",
            "docker service update",
            "terraform apply",
            "gh release upload",
        ):
            self.assertNotIn(forbidden, self.workflow)


if __name__ == "__main__":
    unittest.main()
