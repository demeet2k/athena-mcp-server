import json
import unittest
from pathlib import Path


class ReleaseDistributionV33Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.manifest=json.loads((cls.root/'release'/'v3.3.0.json').read_text(encoding='utf-8'))
        cls.notes=(cls.root/'release'/'v3.3.0.md').read_text(encoding='utf-8')

    def test_historical_release_identity_is_frozen(self):
        m=self.manifest
        self.assertEqual(m['schema'],'ATHENA.RELEASE.DISTRIBUTION.2')
        self.assertEqual(m['version'],'3.3.0');self.assertEqual(m['tag'],'v3.3.0')
        self.assertEqual(m['runtime']['manifest'],'ATHENA.RUNTIME.UNIFIED.10')
        self.assertEqual(m['runtime']['collective_frontier'],'COLLECTIVE_SYNTHESIS_V14')

    def test_historical_v14_surface_and_assets_are_frozen(self):
        tools=set(self.manifest['runtime']['required_tools'])
        for name in ('athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi','athena_sequential_dr_policy_value','athena_gp_resolution_route','athena_two_stage_resource_plan'):
            self.assertIn(name,tools)
        self.assertEqual(set(self.manifest['release']['required_assets']),{'athena_canonical_mcp-3.3.0-py3-none-any.whl','promotion-receipt.json','release-manifest.json','release-attestation.json','SHA256SUMS'})

    def test_historical_notes_preserve_v14_claim_ceilings(self):
        for phrase in ('ATHENA 3.3.0','Collective Synthesis V14','UNIFIED.10','FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR','QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE'):
            self.assertIn(phrase,self.notes)

    def test_v33_publication_lane_is_immutable_while_v34_is_current(self):
        legacy=(self.root/'.github'/'workflows'/'release-v3.3.yml').read_text(encoding='utf-8')
        current=(self.root/'.github'/'workflows'/'release-v3.4.yml').read_text(encoding='utf-8')
        self.assertIn('Release Distribution V3.3',legacy)
        self.assertIn("RELEASE_VERSION: '3.3.0'",legacy)
        self.assertIn('release/v3.3.0.json',legacy)
        self.assertNotIn('release/v3.4.0.json',legacy)
        self.assertIn('Release Distribution V3.4',current)
        self.assertIn("RELEASE_VERSION: '3.4.0'",current)
        self.assertIn('release/v3.4.0.json',current)
        self.assertNotIn('release/v3.3.0.json',current)


if __name__=='__main__':unittest.main()
