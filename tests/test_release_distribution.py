import json
import re
import tomllib
import unittest
from pathlib import Path

from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION
from athena_mcp.unified_manifest import UNIFIED_MANIFEST_VERSION


class ReleaseDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.manifest=json.loads((cls.root/'release'/'v3.2.0.json').read_text(encoding='utf-8'))
        cls.notes=(cls.root/'release'/'v3.2.0.md').read_text(encoding='utf-8')
        cls.project=tomllib.loads((cls.root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        cls.workflow=(cls.root/'.github'/'workflows'/'release.yml').read_text(encoding='utf-8')

    def test_release_identity_matches_current_package_and_runtime(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],self.project['version'])
        self.assertEqual(m['version'],'3.2.0')
        self.assertEqual(m['tag'],'v3.2.0')
        self.assertEqual(m['package']['name'],self.project['name'])
        self.assertEqual(m['package']['entrypoint'],self.project['scripts']['athena-mcp'])
        self.assertEqual(m['package']['entrypoint'],'athena_mcp.server:main')
        self.assertEqual(m['runtime']['manifest'],UNIFIED_MANIFEST_VERSION)
        self.assertEqual(UNIFIED_MANIFEST_VERSION,'ATHENA.RUNTIME.UNIFIED.9')
        self.assertEqual(m['runtime']['collective_frontier'],'COLLECTIVE_ROBUST_V13')
        self.assertEqual(m['runtime']['promotion'],PROMOTION_VERSION)
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2')
        self.assertEqual(m['runtime']['trusted_verifier'],GITHUB_PROMOTION_VERIFIER_VERSION)

    def test_source_policy_requires_exact_master_and_all_five_gates(self):
        p=self.manifest['source_policy']
        self.assertEqual(p['repository'],'demeet2k/athena-mcp-server')
        self.assertEqual(p['branch'],'master')
        self.assertTrue(p['publication_requires_exact_current_master'])
        self.assertTrue(p['publication_requires_clean_checkout'])
        self.assertTrue(p['publication_requires_five_stage_qualification'])
        self.assertTrue(p['exact_commit_is_bound_in_release_attestation'])
        self.assertEqual(p['qualification_checks'],['syntax','unit','critical-invariants','smoke','promotion-qualification'])

    def test_required_assets_match_current_distribution_not_historical_carrier(self):
        assets=set(self.manifest['release']['required_assets'])
        self.assertEqual(assets,{
            'athena_canonical_mcp-3.2.0-py3-none-any.whl',
            'promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS',
        })
        joined=' '.join(sorted(assets))
        self.assertNotIn('kc144-core-registries.tar.xz',joined)
        self.assertNotIn('hub_server',json.dumps(self.manifest))

    def test_current_v13_surface_is_explicit_in_manifest(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','athena_promotion_evaluate','athena_promotion_verify_github'):
            self.assertIn(name,tools)
        resources=set(self.manifest['runtime']['required_resources'])
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://promotion','athena://collective/v13'):
            self.assertIn(uri,resources)

    def test_release_workflow_is_pr_testable_but_publish_is_manual_master_only(self):
        w=self.workflow
        for fragment in (
            'pull_request:', 'workflow_dispatch:', 'package-readiness:', 'promotion-qualification:',
            "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",
            'RELEASE_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}',
            'git rev-parse origin/master', 'scripts/qualify_github_head.py',
            'actions/download-artifact@v5', 'actions/upload-artifact@v4',
            'release-candidate-v3.2.0-${{ env.RELEASE_HEAD }}', 'promotion-receipt-${{ env.RELEASE_HEAD }}',
            'python -m pip wheel --no-deps . -w dist', 'athena_mcp.server',
            'ATHENA.RUNTIME.UNIFIED.9', 'COLLECTIVE_ROBUST_V13',
            'gh release create', '--verify-tag', 'refs/tags/$TAG', 'TAG_TARGET',
            '(cd dist && sha256sum -c SHA256SUMS)', 'release-attestation.json', 'trusted_promotion',
        ):
            self.assertIn(fragment,w)
        self.assertNotIn("branches:\n      - 'agent/aor-collective-unified'",w)
        self.assertNotRegex(w,re.compile(r'(?m)^\s*push:\s*$'))
        self.assertNotRegex(w,re.compile(r'continue-on-error:\s*true'))
        self.assertNotIn('athena_mcp.hub_server',w)
        self.assertNotIn('kc144-core-registries.tar.xz',w)

    def test_package_readiness_binds_trusted_receipt_to_same_release_head(self):
        w=self.workflow
        for fragment in (
            'test "$(git rev-parse HEAD)" = "$RELEASE_HEAD"',
            "assert promotion['git_head']==os.environ['RELEASE_HEAD']",
            "assert promotion['promotion']['status']=='QUALIFIED'",
            "assert promotion['replay']['match'] is True",
            "'release_commit':os.environ['RELEASE_HEAD']",
            "'promrun':promotion['promotion']['run_id']",
            "'verification_ref':promotion['verification_ref']",
            "'receipt_sha256':sha(promo)",
            "assert att['release_commit']==os.environ['RELEASE_HEAD']",
            'test "$TAG_TARGET" = "$RELEASE_HEAD"',
        ):
            self.assertIn(fragment,w)
        self.assertNotIn("promotion['git_head']==os.environ['GITHUB_SHA']",w)
        self.assertNotIn("'release_commit':os.environ['GITHUB_SHA']",w)

    def test_release_notes_preserve_v13_and_trust_claim_ceilings(self):
        n=self.notes
        for phrase in (
            'ATHENA 3.2.0','Collective V13','UNIFIED.9','GITHUB_PROMOTION_VERIFIER.1',
            'QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES',
            'FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM',
            'STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',
            'ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION',
            'caller-bound readiness','one coherent exact-head Actions run/check-suite',
            'This release certifies repository/package/distribution state. It is not a production deployment',
        ):
            self.assertIn(phrase,n)

    def test_authority_boundaries_do_not_collapse_distribution_into_truth_or_admin(self):
        boundaries=' '.join(self.manifest['authority_boundaries']).lower()
        for phrase in ('not deployment','not empirical truth','do not become y1 authority','not github administrative hardening','does not authorize production','not evidence for v3.2.0 bytes'):
            self.assertIn(phrase,boundaries)


if __name__=='__main__':unittest.main()
