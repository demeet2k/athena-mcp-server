import json
import re
import tomllib
import unittest
from pathlib import Path

from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.promotion import PROMOTION_VERSION


class ReleaseDistributionV32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.manifest=json.loads((cls.root/'release'/'v3.2.0.json').read_text(encoding='utf-8'))
        cls.notes=(cls.root/'release'/'v3.2.0.md').read_text(encoding='utf-8')
        cls.workflow=(cls.root/'.github'/'workflows'/'release.yml').read_text(encoding='utf-8')
        cls.gitignore=(cls.root/'.gitignore').read_text(encoding='utf-8')

    def test_historical_release_identity_is_self_contained(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],'3.2.0')
        self.assertEqual(m['tag'],'v3.2.0')
        self.assertEqual(m['package']['name'],'athena-canonical-mcp')
        self.assertEqual(m['package']['entrypoint'],'athena_mcp.server:main')
        self.assertEqual(m['runtime']['manifest'],'ATHENA.RUNTIME.UNIFIED.9')
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

    def test_required_assets_match_v32_distribution(self):
        assets=set(self.manifest['release']['required_assets'])
        self.assertEqual(assets,{'athena_canonical_mcp-3.2.0-py3-none-any.whl','promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS'})
        self.assertNotIn('kc144-core-registries.tar.xz',' '.join(sorted(assets)))

    def test_historical_v13_surface_is_explicit(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','athena_promotion_evaluate','athena_promotion_verify_github'):
            self.assertIn(name,tools)
        resources=set(self.manifest['runtime']['required_resources'])
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://promotion','athena://collective/v13'):
            self.assertIn(uri,resources)

    def test_historical_workflow_is_self_contained_and_manual_publish_only(self):
        w=self.workflow
        for fragment in (
            'pull_request:', 'workflow_dispatch:', 'package-readiness:', 'promotion-qualification:',
            "if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/master'",
            'release/v3.2.0.json','release/v3.2.0.md','tests/test_release_distribution_v32.py',
            'release-candidate-v3.2.0-${{ env.RELEASE_HEAD }}','ATHENA.RUNTIME.UNIFIED.9','COLLECTIVE_ROBUST_V13',
            'scripts/qualify_github_head.py','gh release create','--verify-tag','TAG_TARGET',
        ):self.assertIn(fragment,w)
        self.assertNotIn("tests/test_release_distribution.py' -v",w)
        self.assertNotRegex(w,re.compile(r'(?m)^\s*push:\s*$'))
        self.assertNotRegex(w,re.compile(r'continue-on-error:\s*true'))

    def test_historical_notes_preserve_v13_claim_ceilings(self):
        n=self.notes
        for phrase in (
            'ATHENA 3.2.0','Collective V13','UNIFIED.9','GITHUB_PROMOTION_VERIFIER.1',
            'QMC_CONTINUOUS_HYPERPOSTERIOR != EXACT_CONTINUOUS_HYPERPARAMETER_BAYES',
            'FITC_INDUCING_GP != FULL_GP_POSTERIOR_OR_VARIATIONAL_OPTIMUM',
            'STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',
            'ELLIPSOIDAL_GAUSSIAN_ROBUST_PLAN != GENERAL_DISTRIBUTIONALLY_ROBUST_OPTIMIZATION',
            'caller-bound readiness','one coherent exact-head Actions run/check-suite',
            'This release certifies repository/package/distribution state. It is not a production deployment',
        ):self.assertIn(phrase,n)

    def test_authority_boundaries_remain_historical_and_scoped(self):
        boundaries=' '.join(self.manifest['authority_boundaries']).lower()
        for phrase in ('not deployment','not empirical truth','do not become y1 authority','not github administrative hardening','does not authorize production','not evidence for v3.2.0 bytes'):
            self.assertIn(phrase,boundaries)


if __name__=='__main__':unittest.main()
