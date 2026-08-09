import json
import tempfile
import unittest

from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.server import Server


class UnifiedManifestTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']
    def read_json(self,uri):return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])

    def test_effective_manifest_reports_v13_coordination_drift_and_compatibility(self):
        manifest=self.tool('athena_runtime_manifest')
        self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.10')
        for compat in ('ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6','ATHENA.RUNTIME.UNIFIED.7','ATHENA.RUNTIME.UNIFIED.8','ATHENA.RUNTIME.UNIFIED.9'):self.assertIn(compat,manifest['artifact_compat'])
        self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_ROBUST_V13','AOR_DECISION_CORTEX','AUTHORITY_Y1','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1','MESSAGE_BOARD_V1','COHESION_MESH_V1','COHESION_DUPLICATE_GUARD_V1','COHESION_EVIDENCE_GUARD_V1','AGENT_BOOT_COHESION_TREATMENT_V1','PARTY_COORDINATION_V1','PARTY_CHANNEL_V2','PARTY_REWARD_PROVENANCE_V3_2','ORGAN_INVENTORY.1','ARCHITECTURE_DRIFT_AUDIT.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants'])
        for phrase in ['UNKNOWN != 0','V13 QMC continuous-domain hyperposterior != exact continuous hyperparameter Bayes','V13 bounded FCI-lite != FCI/RFCI PAG theorem','Y1_SEMANTIC_CLAIM_AUTHORITY != MESSAGE_BOARD_COORDINATION_PRESENCE_CLAIM_AUTHORITY','COHESION != CLAIM_AUTHORITY','PARTY_RESULT != RESULT_TRUTH','V3_PACKET_VERSION_REQUIRED','BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING','MATURE_ORGAN_CODE_OR_TOOL_EXISTENCE != CONSTITUTIONAL_INTEGRATION']:
            self.assertIn(phrase,joined)
        verifier=manifest['promotion_verifier'];self.assertEqual(verifier['version'],GITHUB_PROMOTION_VERIFIER_VERSION)
        coordination=manifest['organs']['coordination'];self.assertEqual(coordination['inventory_version'],'ATHENA.ORGAN.INVENTORY.1.1');self.assertEqual(coordination['party_reward_current'],'PARTY.REWARD.PROVENANCE.3.2');self.assertEqual(coordination['architecture_drift_version'],'ATHENA.ARCHITECTURE.DRIFT.1')
        ids={row['id'] for row in coordination['organs']};self.assertIn('MESSAGE_BOARD_V1',ids);self.assertIn('PARTY_REWARD_PROVENANCE_V3_2',ids);self.assertNotIn('PARTY_REWARD_PROVENANCE_V3',ids)
        unresolved={x['id']:x for x in manifest['unresolved']};self.assertEqual(unresolved['ORGAN_INVENTORY_EXPANSION']['status'],'ACTIVE_RECURSIVE_FRONTIER');self.assertIn('Freshness Train',unresolved['ORGAN_INVENTORY_EXPANSION']['boundary'])
        self.assertEqual(manifest['architecture_drift']['inventory_version'],'ATHENA.ORGAN.INVENTORY.1.1')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_v13_coordination_and_drift_boundaries(self):
        law=self.tool('athena_maxdev_law')['text'].upper()
        for phrase in ['V13 GP HYPER-QMC','V13 FCI-LITE','MESSAGE BOARD','COHESION','PARTY','V3.1','V3.2','ARCHITECTURE DRIFT','INVENTORY EXPANSION','FRESHNESS TRAIN']:
            self.assertIn(phrase,law)

    def test_scientific_base_and_effective_runtime_are_distinct_layered_coordinates(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for name in ('athena_runtime_manifest','athena_surface_audit','athena_promotion_verify_github','athena_message_board','athena_cohesion_duplicate_guard','athena_party_result'):self.assertIn(name,names)
        for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://architecture/inventory','athena://architecture/drift','athena://cohesion/v1','athena://party-coordination/v1','athena://collective/v13'):self.assertIn(uri,uris)
        effective=self.read_json('athena://runtime/unified-manifest');base=self.read_json('athena://manifest');promotion=self.read_json('athena://promotion');drift=self.read_json('athena://architecture/drift')
        self.assertEqual(base['artifact'],'ATHENA.RUNTIME.UNIFIED.9');self.assertEqual(effective['artifact'],'ATHENA.RUNTIME.UNIFIED.10')
        self.assertTrue(set(base['layers']).issubset(set(effective['layers'])));self.assertNotIn('MESSAGE_BOARD_V1',base['layers']);self.assertIn('MESSAGE_BOARD_V1',effective['layers'])
        self.assertEqual(promotion['github_verifier']['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(promotion['architecture_drift']['status'],'PASS')
        self.assertEqual(drift['latest']['status'],'PASS');self.assertEqual(drift['inventory']['version'],'ATHENA.ORGAN.INVENTORY.1.1')
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['architecture_drift']['status'],'PASS')
        for group in ('manifest','collective_v13','promotion','coordination','architecture_drift'):self.assertEqual(audit['groups'][group]['status'],'PASS')


if __name__=='__main__':unittest.main()
