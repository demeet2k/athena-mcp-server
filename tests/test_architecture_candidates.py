import unittest
from athena_mcp.architecture_candidates import ARCHITECTURE_CANDIDATE_VERSION,candidate_manifest
from athena_mcp.coordination_inventory import mature_organs

class ArchitectureCandidateTests(unittest.TestCase):
    def test_freshness_train_is_visible_but_not_mature(self):
        manifest=candidate_manifest();self.assertEqual(manifest['version'],ARCHITECTURE_CANDIDATE_VERSION)
        row=next(x for x in manifest['candidates'] if x['id']=='FRESHNESS_TRAIN_V1')
        self.assertEqual(row['status'],'CANDIDATE_NOT_YET_MATURE');self.assertEqual(row['authority_plane'],'PLANNING_EVIDENCE_ONLY')
        self.assertEqual(row['public_tools'],[]);self.assertEqual(row['public_resources'],[])
        self.assertGreaterEqual(len(row['missing_maturity_requirements']),4)
        mature_ids={x['id'] for x in mature_organs()};self.assertNotIn('FRESHNESS_TRAIN_V1',mature_ids)
    def test_candidate_laws_forbid_merge_or_promotion_authority(self):
        row=candidate_manifest()['candidates'][0];laws=set(row['laws'])
        self.assertIn('FRESHNESS_CLASSIFICATION != MERGE_AUTHORITY',laws);self.assertIn('FRESHNESS_CLASSIFICATION != PROMOTION_AUTHORITY',laws);self.assertIn('HISTORICAL_CI_PASS != CURRENT_INTEGRATION_PASS',laws);self.assertIn('FRESHNESS_ANALYSIS = READ_ONLY',laws)
if __name__=='__main__':unittest.main()
