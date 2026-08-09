import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReleaseOciActivationContractTests(unittest.TestCase):
    def setUp(self):
        self.activation = (ROOT / '.github/workflows/release-v3.3-activation.yml').read_text()
        self.oci = (ROOT / '.github/workflows/oci-v3.3.yml').read_text()
        self.release = (ROOT / '.github/workflows/release-v3.3.yml').read_text()
        self.manifest = json.loads((ROOT / 'release/v3.3.0.json').read_text())
        self.notes = (ROOT / 'release/v3.3.0.md').read_text()

    def test_activation_is_exact_ci_to_release_to_oci_workflow_dispatch_chain(self):
        text = self.activation
        for needle in (
            'workflow_run:',
            '- CI',
            '- Release Distribution V3.3',
            "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.event == 'workflow_dispatch'",
            'test "$(git rev-parse origin/master)" = "$HEAD_SHA"',
            'Activate ATHENA v3.3.0 release and OCI publication',
            'actions/workflows/$RELEASE_WORKFLOW/dispatches',
            'actions/workflows/$OCI_WORKFLOW/dispatches',
            '-f "inputs[expected_head]=$HEAD_SHA"',
            '-f "inputs[release_run_id]=$RELEASE_RUN_ID"',
        ):
            self.assertIn(needle, text)
        self.assertNotIn('gh release create', text)
        self.assertNotIn('docker buildx build', text)

    def test_oci_workflow_is_exact_head_multiarch_attested_distribution_only(self):
        text = self.oci
        for needle in (
            'workflow_dispatch:',
            'expected_head:',
            'release_run_id:',
            'packages: write',
            'id-token: write',
            'attestations: write',
            'docker/build-push-action@v6',
            'platforms: linux/amd64,linux/arm64',
            'provenance: mode=max',
            'sbom: true',
            'actions/attest-build-provenance@v2',
            'python deploy/render.py --image "$IMAGE_REF"',
            'gh release upload "$RELEASE_TAG" dist/oci/* --clobber',
        ):
            self.assertIn(needle, text)
        self.assertNotIn('RESTART_READBACK_PASS', text)
        for forbidden in ('kubectl apply', 'helm upgrade', 'docker service update'):
            self.assertNotIn(forbidden, text)

    def test_manifest_and_notes_preserve_distribution_activation_boundaries(self):
        oci = self.manifest['oci_distribution']
        self.assertEqual(oci['image'], 'ghcr.io/demeet2k/athena-mcp-server')
        self.assertEqual(oci['platforms'], ['linux/amd64', 'linux/arm64'])
        self.assertTrue(oci['deployment_requires_digest'])
        self.assertEqual(oci['activation_workflow'], '.github/workflows/release-v3.3-activation.yml')
        self.assertEqual(oci['publication_workflow'], '.github/workflows/oci-v3.3.yml')
        self.assertIn('oci-release-attestation.json', oci['release_assets'])
        self.assertIn('OCI distribution', self.notes)
        self.assertIn('OCI_PUBLISHED != CLUSTER_APPLIED != TRAFFIC_ACTIVATED', self.notes)

    def test_existing_release_workflow_remains_manual_publish_authority(self):
        self.assertIn('workflow_dispatch:', self.release)
        self.assertIn("github.event_name == 'workflow_dispatch'", self.release)
        self.assertIn("github.ref == 'refs/heads/master'", self.release)
        self.assertIn('test "$(git rev-parse origin/master)" = "$RELEASE_HEAD"', self.release)
        self.assertNotIn('packages: write', self.release)

    def test_write_permissions_are_limited_to_effectful_jobs(self):
        activation_prefix = self.activation[: self.activation.index('\n  dispatch-release:')]
        self.assertNotIn('actions: write', activation_prefix)
        self.assertEqual(self.activation.count('actions: write'), 2)

        oci_prefix = self.oci[: self.oci.index('\n  publish:')]
        self.assertNotIn('contents: write', oci_prefix)
        self.assertNotIn('packages: write', oci_prefix)
        self.assertEqual(self.oci.count('contents: write'), 1)
        self.assertEqual(self.oci.count('packages: write'), 1)


if __name__ == '__main__':
    unittest.main()
