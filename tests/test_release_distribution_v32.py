import json
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

    def test_historical_release_identity_is_frozen(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],'3.2.0')
        self.assertEqual(m['tag'],'v3.2.0')
        self.assertEqual(m['package']['name'],'athena-canonical-mcp')
        self.assertEqual(m['package']['wheel'],'athena_canonical_mcp-3.2.0-py3-none-any.whl')
        self.assertEqual(m['package']['entrypoint'],'athena_mcp.server:main')
        self.assertEqual(m['runtime']['manifest'],'ATHENA.RUNTIME.UNIFIED.9')
        self.assertEqual(m['runtime']['collective_frontier'],'COLLECTIVE_ROBUST_V13')
        self.assertEqual(m['runtime']['promotion'],PROMOTION_VERSION)
        self.assertEqual(PROMOTION_VERSION,'ATHENA.PROMOTION.2')
        self.assertEqual(m['runtime']['trusted_verifier'],GITHUB_PROMOTION_VERIFIER_VERSION)

    def test_source_policy_records_the_five_gates_used_by_v32(self):
        p=self.manifest['source_policy']
        self.assertEqual(p['repository'],'demeet2k/athena-mcp-server')
        self.assertEqual(p['branch'],'master')
        self.assertTrue(p['publication_requires_exact_current_master'])
        self.assertTrue(p['publication_requires_clean_checkout'])
        self.assertTrue(p['publication_requires_five_stage_qualification'])
        self.assertTrue(p['exact_commit_is_bound_in_release_attestation'])
        self.assertEqual(p['qualification_checks'],['syntax','unit','critical-invariants','smoke','promotion-qualification'])

    def test_historical_v13_surface_is_explicit(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select','athena_promotion_evaluate','athena_promotion_verify_github'):
            self.assertIn(name,tools)
        resources=set(self.manifest['runtime']['required_resources'])
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://promotion','athena://collective/v13'):
            self.assertIn(uri,resources)
        self.assertNotIn('athena://collective/v14',resources)

    def test_required_assets_and_authority_boundaries_are_frozen(self):
        assets=set(self.manifest['release']['required_assets'])
        self.assertEqual(assets,{'athena_canonical_mcp-3.2.0-py3-none-any.whl','promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS'})
        boundaries=' '.join(self.manifest['authority_boundaries']).lower()
        for phrase in ('not deployment','not empirical truth','do not become y1 authority','not github administrative hardening','does not authorize production','not evidence for v3.2.0 bytes'):
            self.assertIn(phrase,boundaries)

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

    def test_v32_recipe_is_historical_while_current_release_is_v34(self):
        self.assertFalse((self.root/'.github'/'workflows'/'release.yml').exists())
        current=(self.root/'.github'/'workflows'/'release-v3.4.yml').read_text(encoding='utf-8')
        self.assertIn('Release Distribution V3.4',current)
        self.assertIn('release/v3.4.0.json',current)
        self.assertNotIn('release/v3.2.0.json',current)
        legacy=(self.root/'.github'/'workflows'/'release-v3.3.yml').read_text(encoding='utf-8')
        self.assertIn('Release Distribution V3.3',legacy)
        self.assertNotIn('release/v3.2.0.json',legacy)


if __name__=='__main__':unittest.main()
