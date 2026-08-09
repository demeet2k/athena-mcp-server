import json,tempfile,unittest
from athena_mcp.coordination_inventory import COORDINATION_INVENTORY_VERSION,PARTY_REWARD_VERSION
from athena_mcp.github_promotion_verifier import GITHUB_PROMOTION_VERIFIER_VERSION
from athena_mcp.server import Server

class UnifiedManifestTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
 def tearDown(self):self.server.store.close();self.tmp.close()
 def rpc(self,method,params=None):
  self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method};m.update({'params':params} if params is not None else {});return self.server.handle(m)
 def tool(self,name,args=None):
  r=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result'];self.assertFalse(r.get('isError'),r);return r['structuredContent']
 def read(self,uri):return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])
 def test_effective_manifest_preserves_v14_and_adds_coordination(self):
  m=self.tool('athena_runtime_manifest');self.assertEqual(m['artifact'],'ATHENA.RUNTIME.UNIFIED.11')
  for compat in ('ATHENA.RUNTIME.UNIFIED.9','ATHENA.RUNTIME.UNIFIED.10'):self.assertIn(compat,m['artifact_compat'])
  for layer in ('COLLECTIVE_SYNTHESIS_V14','GITHUB_PROMOTION_VERIFIER.1','MESSAGE_BOARD_V1','COHESION_MESH_V1','PARTY_REWARD_PROVENANCE_V3_2','ORGAN_INVENTORY.1','ARCHITECTURE_DRIFT_AUDIT.1'):self.assertIn(layer,m['layers'])
  joined='\n'.join(m['invariants'])
  for phrase in ('FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR','SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM','Y1_SEMANTIC_CLAIM_AUTHORITY != MESSAGE_BOARD_COORDINATION_PRESENCE_CLAIM_AUTHORITY','FUZZY_SIMILARITY != DUPLICATE_PROOF','BASE_XP_MUST_BE_FINITE_NON_BOOLEAN_BEFORE_PARTY_REWARD_PROCESSING'):self.assertIn(phrase,joined)
  self.assertEqual(m['collective_synthesis']['version'],'COLLECTIVE_RUNTIME_V14');self.assertIn('collective_v14',m['organs']);self.assertIn('coordination',m['organs']);self.assertEqual(m['organs']['coordination']['inventory_version'],COORDINATION_INVENTORY_VERSION);self.assertEqual(m['organs']['coordination']['party_reward_current'],PARTY_REWARD_VERSION)
 def test_schema_migration_survives_overlay(self):
  before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['startup']['status'],'READY_LOCAL')
 def test_maxdev_preserves_v14_and_coordination_laws(self):
  law=self.tool('athena_maxdev_law')['text']
  for phrase in ('V14 SYNTHESIS LAW','finite joint science-twin states','bootstrap FCI-lite graphs','two-timepoint sequential AIPW','lower-tail CVaR','finite two-stage resource recourse','COORDINATION ARCHITECTURE','Message Board coordination authority != Y1 semantic authority','Party V3.2','declared architecture drift blocks promotion'):self.assertIn(phrase,law)
 def test_synthesis_and_effective_manifest_are_distinct_coordinates(self):
  names={x['name'] for x in self.rpc('tools/list',{})['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list',{})['result']['resources']}
  for name in ('athena_runtime_manifest','athena_promotion_verify_github','athena_joint_factor_belief','athena_joint_science_evi','athena_party_result','athena_cohesion_duplicate_guard'):self.assertIn(name,names)
  for uri in ('athena://manifest','athena://runtime/unified-manifest','athena://collective/v14','athena://architecture/inventory','athena://architecture/drift','athena://cohesion/v1','athena://party-coordination/v1'):self.assertIn(uri,uris)
  effective=self.read('athena://runtime/unified-manifest');base=self.read('athena://manifest');promotion=self.read('athena://promotion');drift=self.read('athena://architecture/drift')
  self.assertEqual(base['artifact'],'ATHENA.RUNTIME.UNIFIED.10');self.assertEqual(effective['artifact'],'ATHENA.RUNTIME.UNIFIED.11');self.assertTrue(set(base['layers']).issubset(set(effective['layers'])));self.assertNotIn('MESSAGE_BOARD_V1',base['layers']);self.assertIn('MESSAGE_BOARD_V1',effective['layers'])
  self.assertEqual(promotion['github_verifier']['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(promotion['architecture_drift']['status'],'PASS');self.assertEqual(drift['latest']['status'],'PASS');self.assertEqual(drift['inventory']['version'],COORDINATION_INVENTORY_VERSION)
  audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['architecture_drift']['status'],'PASS')
  for group in ('collective_v14','promotion','coordination','architecture_drift'):self.assertEqual(audit['groups'][group]['status'],'PASS')
if __name__=='__main__':unittest.main()
