import json
import tempfile
import unittest

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

    def test_live_manifest_reports_v11_single_server_layers_and_compatibility(self):
        manifest=self.tool('athena_runtime_manifest')
        self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.6')
        for compat in ('ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5'):self.assertIn(compat,manifest['artifact_compat'])
        self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','AOR_DECISION_CORTEX','AOR.3','AUTHORITY_Y1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1','AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants'])
        for phrase in ['UNKNOWN != 0','pheromone/reuse/popularity != evidence','reachability/navigation closure != logical or causal proof','semantic VID CAS != Git HEAD CAS != topology version CAS','BELIEF_POSTERIOR != CANONICAL_TRUTH','GAUSSIAN_LINEAR_POSTERIOR != GENERAL_CONTINUOUS_BAYES','V10 FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH','V11 marginal-likelihood optimum != true kernel','V11 supplied-DAG latent projection != data-discovered PAG','V11 stacked TMLE != super-learner theorem','V11 finite-model BAPOMDP != general Bayes-adaptive control','athena_claim_* = Y1 canonical authority']:
            self.assertIn(phrase,joined)
        self.assertIn('consensus/pheromone/reward are never typed authority or evidence by themselves',manifest['braid_law'])
        self.assertIn('model posterior/replication shadow are also never typed authority or evidence by themselves',manifest['braid_law'])
        self.assertIn('athena_discovery_claim_*',manifest['claim_namespace_law'])
        unresolved={x['id']:x for x in manifest['unresolved']}
        self.assertEqual(unresolved['QHUG_SEMANTICS']['status'],'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED')
        self.assertEqual(unresolved['MODEL_TO_AUTHORITY_BRIDGE']['status'],'EXPLICIT_WITNESS_REQUIRED')
        self.assertEqual(unresolved['GENERAL_BELIEF_CONTROL']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['FORMAL_CAUSAL_DISCOVERY']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['GENERAL_NONLINEAR_BAYES']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(manifest['schema']['target'],2);self.assertEqual(manifest['startup']['status'],'DEGRADED_SCHEMA')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_v11_boundaries(self):
        law=self.tool('athena_maxdev_law')['text']
        for phrase in ['RECONSTRUCT through RECONRUN + canonical OMEGA','AOR ranks eligible comparable candidates','V11 GP hyperfit is DESIGN_ONLY unless apply=true','V11 GP decision EVSI','V11 latent ADMG projection','V11 stacked binary TMLE','V11 RR bias-factor surface','V11 finite-model BAPOMDP','V11 dependence intervals','never feed predictions/beliefs/simulations/plans/designs back as observations or Y authority','PROMOTE only the exact head']:
            self.assertIn(phrase,law)

    def test_manifest_resources_and_surface2_include_v11(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        self.assertIn('athena_runtime_manifest',names);self.assertIn('athena_maxdev_law',names)
        for uri in ['athena://manifest','athena://runtime/unified-manifest','athena://runtime/maxdev','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8','athena://collective/v9','athena://collective/v10','athena://collective/v11']:
            self.assertIn(uri,uris)
        payload=self.read_json('athena://runtime/unified-manifest');canonical=self.read_json('athena://manifest')
        self.assertEqual(payload['artifact'],'ATHENA.RUNTIME.UNIFIED.6');self.assertEqual(canonical['artifact'],'ATHENA.RUNTIME.UNIFIED.6');self.assertEqual(canonical['layers'],payload['layers'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        for group in ('manifest','collective_v4_v5_v6','collective_v7','collective_v8','collective_v9','collective_v10','collective_v11'):self.assertEqual(audit['groups'][group]['status'],'PASS')


if __name__=='__main__':unittest.main()
