import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseOciRelayContractTests(unittest.TestCase):
    def setUp(self):
        self.relay = (ROOT / '.github/workflows/oci-v3.3-relay.yml').read_text()
        self.activation = (ROOT / '.github/workflows/release-v3.3-activation.yml').read_text()

    def test_relay_is_exact_one_shot_release_to_oci_dispatch(self):
        text = self.relay
        for needle in (
            'push:',
            'branches: [master]',
            'RELEASE_TAG: v3.3.0',
            'RELEASE_HEAD: 11211341adf599ae78784cce4ded39f21ee71ef7',
            "RELEASE_RUN_ID: '31297502454'",
            'RELAY_SUBJECT: Relay ATHENA v3.3.0 OCI publication',
            "startsWith(github.event.head_commit.message, 'Relay ATHENA v3.3.0 OCI publication')",
            'test "$(git show -s --format=%s HEAD)" = "$RELAY_SUBJECT"',
            'test "$TAG_TARGET" = "$RELEASE_HEAD"',
            "assert run['name']=='Release Distribution V3.3'",
            "assert run['event']=='workflow_dispatch'",
            "assert run['status']=='completed' and run['conclusion']=='success'",
            "assert run['head_sha']==os.environ['RELEASE_HEAD']",
            'actions/workflows/$OCI_WORKFLOW/dispatches',
            "'expected_head':os.environ['RELEASE_HEAD']",
            "'release_run_id':os.environ['RELEASE_RUN_ID']",
            'ATHENA.OCI.RELAY.RECEIPT.1',
        ):
            self.assertIn(needle, text)

    def test_relay_is_idempotent_and_does_not_claim_deployment(self):
        text = self.relay
        self.assertIn("{'oci-image-ref.txt','oci-release-attestation.json'} <= observed", text)
        self.assertIn('ALREADY_PUBLISHED', text)
        self.assertIn("if: steps.verify.outputs.status == 'DISPATCH_REQUIRED'", text)
        self.assertIn('does not apply Kubernetes objects', text)
        for forbidden in (
            'kubectl apply',
            'helm upgrade',
            'docker service update',
            'packages: write',
            'contents: write',
            'gh release create',
        ):
            self.assertNotIn(forbidden, text)

    def test_relay_write_permission_is_only_on_effectful_job(self):
        prefix = self.relay[: self.relay.index('\n  relay:')]
        self.assertNotIn('actions: write', prefix)
        self.assertEqual(self.relay.count('actions: write'), 1)
        self.assertIn('permissions:\n      contents: read\n      actions: write', self.relay)

    def test_permanent_activation_no_longer_depends_on_suppressed_second_workflow_run(self):
        text = self.activation
        self.assertIn('workflows:\n      - CI', text)
        self.assertNotIn('- Release Distribution V3.3', text)
        self.assertNotIn('\n  dispatch-oci:', text)
        self.assertIn('Resolve and await the exact release workflow run', text)
        self.assertIn('Verify the published release and dispatch exact OCI publication', text)


if __name__ == '__main__':
    unittest.main()
