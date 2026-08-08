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

    def test_live_manifest_reports_v13_github_verifier_and_compatibility(self):
        manifest=self.tool('athena_runtime_manifest')
        self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.9')
        for compat in ('ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6','ATHENA.RUNTIME.UNIFIED.7','ATHENA.RUNTIME.UNIFIED.8'):self.assertIn(compat,manifest['artifact_compat'])
        self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','COLLECTIVE_JOINT_V12','COLLECTIVE_ROBUST_V13','AOR_DECISION_CORTEX','AOR.3','AUTHORITY_Y1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1','AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants'])
        for phrase in ['UNKNOWN != 0','pheromone/reuse/popularity != evidence','reachability/navigation closure != logical or causal proof','semantic VID CAS != Git HEAD CAS != topology version CAS','caller-supplied CI/smoke attestation != externally verified promotion qualification','PROMOTION.2 ATTESTED_READY != QUALIFIED','one coherent host-bound GitHub Actions run/check-suite','checks from different suites/runs are never spliced','trusted GitHub repository/API/run context comes from host environment','BELIEF_POSTERIOR != CANONICAL_TRUTH','V10 FIXED_KERNEL_GP != GENERAL_WORLD_TRUTH','V11 marginal-likelihood optimum != true kernel','V12 finite-grid GP hyperposterior != continuous hyperparameter Bayes','V13 QMC continuous-domain hyperposterior != exact continuous hyperparameter Bayes','V13 FITC inducing GP != full GP posterior or variational optimum','V13 bounded FCI-lite != FCI/RFCI PAG theorem','V13 sequential two-timepoint TMLE != general longitudinal TMLE theorem or identification proof','V13 dynamic two-timepoint g-formula policy value != general off-policy causal value or execution authorization','V13 correlated-Gaussian ellipsoidal-mean robust certificate != general distributionally robust optimization','athena_claim_* = Y1 canonical authority']:
            self.assertIn(phrase,joined)
        self.assertIn('caller-bound CI/smoke packets are not trusted external verification',manifest['braid_law'])
        self.assertIn('host-bound independent check-suite observation',manifest['braid_law'])
        self.assertIn('athena_discovery_claim_*',manifest['claim_namespace_law'])
        verifier=manifest['promotion_verifier'];self.assertEqual(verifier['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(verifier['required_checks'],['syntax','unit','critical-invariants','smoke']);self.assertEqual(verifier['trusted_app_slug'],'github-actions')
        unresolved={x['id']:x for x in manifest['unresolved']}
        self.assertEqual(unresolved['QHUG_SEMANTICS']['status'],'UNRESOLVED_UNLESS_REGISTERED_AND_WITNESSED')
        self.assertEqual(unresolved['MODEL_TO_AUTHORITY_BRIDGE']['status'],'EXPLICIT_WITNESS_REQUIRED')
        self.assertEqual(unresolved['GENERAL_BELIEF_CONTROL']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['FORMAL_CAUSAL_DISCOVERY']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['GENERAL_NONLINEAR_BAYES']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['LONGITUDINAL_CAUSAL_POLICY']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['STOCHASTIC_RESOURCE_CONTROL']['status'],'UNRESOLVED_OPTIONAL_RESEARCH')
        self.assertEqual(unresolved['NON_GITHUB_PROMOTION_VERIFIERS']['status'],'UNRESOLVED_OPTIONAL_INTEGRATION')
        self.assertNotIn('EXTERNAL_PROMOTION_VERIFIER',unresolved)
        self.assertIn('ATTESTED_READY',manifest['promotion']);self.assertIn('GITHUB_PROMOTION_VERIFIER.1',manifest['promotion']);self.assertIn('one coherent exact-head Actions run/check-suite',manifest['promotion'])
        self.assertEqual(manifest['schema']['target'],2);self.assertEqual(manifest['startup']['status'],'DEGRADED_SCHEMA')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_v13_and_trusted_github_promotion_boundaries(self):
        law=self.tool('athena_maxdev_law')['text']
        for phrase in ['RECONSTRUCT through RECONRUN + canonical OMEGA','AOR ranks eligible comparable candidates','V11 GP hyperfit remains DESIGN_ONLY unless apply=true','V12 finite-grid hyperposterior','V13 GP hyper-QMC','V13 FITC','V13 joint GP design','V13 FCI-lite','V13 sequential TMLE','V13 dynamic policy value','V13 robust resource selection','Stage-2 pseudo outcomes preserve observed A1/L1 histories','caller-bound packets stop at ATTESTED_READY','prefer athena_promotion_verify_github','one coherent exact-head Actions run/check-suite','Never splice checks across runs/suites','caller-selected trust roots']:
            self.assertIn(phrase,law)

    def test_manifest_resources_surface2_and_promotion_include_v13_and_verifier(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for name in ('athena_runtime_manifest','athena_maxdev_law','athena_promotion_evaluate','athena_promotion_verify_github'):self.assertIn(name,names)
        for uri in ['athena://manifest','athena://runtime/unified-manifest','athena://runtime/maxdev','athena://promotion','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8','athena://collective/v9','athena://collective/v10','athena://collective/v11','athena://collective/v12','athena://collective/v13']:
            self.assertIn(uri,uris)
        payload=self.read_json('athena://runtime/unified-manifest');canonical=self.read_json('athena://manifest');promotion=self.read_json('athena://promotion')
        self.assertEqual(payload['artifact'],'ATHENA.RUNTIME.UNIFIED.9');self.assertEqual(canonical['artifact'],'ATHENA.RUNTIME.UNIFIED.9');self.assertEqual(canonical['layers'],payload['layers'])
        self.assertEqual(promotion['github_verifier']['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertIn('failed GitHub verification creates no PROMRUN',promotion['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        for group in ('manifest','collective_v4_v5_v6','collective_v7','collective_v8','collective_v9','collective_v10','collective_v11','collective_v12','collective_v13','promotion'):self.assertEqual(audit['groups'][group]['status'],'PASS')


if __name__=='__main__':unittest.main()
