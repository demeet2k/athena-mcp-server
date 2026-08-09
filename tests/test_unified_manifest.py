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

    def test_live_manifest_reports_v14_github_verifier_and_compatibility(self):
        manifest=self.tool('athena_runtime_manifest')
        self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.10')
        for compat in ('ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6','ATHENA.RUNTIME.UNIFIED.7','ATHENA.RUNTIME.UNIFIED.8','ATHENA.RUNTIME.UNIFIED.9'):self.assertIn(compat,manifest['artifact_compat'])
        self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','COLLECTIVE_JOINT_V12','COLLECTIVE_ROBUST_V13','COLLECTIVE_SYNTHESIS_V14','AOR_DECISION_CORTEX','AOR.3','AUTHORITY_Y1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1','AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants'])
        for phrase in ['UNKNOWN != 0','one coherent host-bound GitHub Actions run/check-suite','checks from different suites/runs are never spliced','trusted GitHub repository/API/run context comes from host environment','BELIEF_POSTERIOR != CANONICAL_TRUTH','V13 QMC continuous-domain hyperposterior != exact continuous hyperparameter Bayes','V13 bounded FCI-lite != FCI/RFCI PAG theorem','FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR','BOOTSTRAP_GRAPH_FREQUENCY != CAUSAL_POSTERIOR','JOINT_SCIENCE_EVI != OBSERVATION_OR_EVIDENCE','SEQUENTIAL_DR_POLICY_VALUE != GENERAL_LONGITUDINAL_CAUSAL_VALUE_THEOREM','FINITE_SCENARIO_ROBUST_POLICY != GENERAL_ROBUST_CONTROL','QUERY_SET_DECISION_PRESERVATION != GLOBAL_APPROXIMATION_CERTIFICATE','FINITE_TWO_STAGE_SCENARIO_RECOURSE != GENERAL_MULTISTAGE_STOCHASTIC_PROGRAM','athena_claim_* = Y1 canonical authority']:
            self.assertIn(phrase,joined)
        self.assertEqual(manifest['collective_synthesis']['version'],'COLLECTIVE_RUNTIME_V14')
        self.assertEqual(manifest['collective_synthesis']['coordinate'],'COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>')
        self.assertIn('collective_v14',manifest['organs'])
        self.assertIn('COLLECTIVE(V1-V14)',manifest['cycle'])
        self.assertIn('COLLECTIVE_SYNTHESIS_V14',manifest['navigation'])
        self.assertIn('caller-bound CI/smoke packets are not trusted external verification',manifest['braid_law'])
        self.assertIn('host-bound independent check-suite observation',manifest['braid_law'])
        verifier=manifest['promotion_verifier'];self.assertEqual(verifier['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(verifier['required_checks'],['syntax','unit','critical-invariants','smoke']);self.assertEqual(verifier['trusted_app_slug'],'github-actions')
        unresolved={x['id']:x for x in manifest['unresolved']}
        for uid in ('GENERAL_BELIEF_CONTROL','FORMAL_CAUSAL_DISCOVERY','LONGITUDINAL_CAUSAL_POLICY','STOCHASTIC_RESOURCE_CONTROL'):
            self.assertIn('v14_boundary',unresolved[uid])
        self.assertEqual(unresolved['NON_GITHUB_PROMOTION_VERIFIERS']['status'],'UNRESOLVED_OPTIONAL_INTEGRATION')
        self.assertNotIn('EXTERNAL_PROMOTION_VERIFIER',unresolved)
        self.assertEqual(manifest['schema']['target'],2);self.assertEqual(manifest['startup']['status'],'DEGRADED_SCHEMA')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_v14_and_trusted_github_promotion_boundaries(self):
        law=self.tool('athena_maxdev_law')['text']
        for phrase in ['RECONSTRUCT through RECONRUN + canonical OMEGA','V13 GP hyper-QMC','V14 SYNTHESIS LAW','finite joint science-twin states','bootstrap FCI-lite graphs','two-timepoint sequential AIPW','lower-tail CVaR','route GP resolution','finite two-stage resource recourse','caller-bound packets stop at ATTESTED_READY','prefer athena_promotion_verify_github','one coherent exact-head Actions run/check-suite','Never splice checks across runs/suites']:
            self.assertIn(phrase,law)

    def test_manifest_resources_surface2_and_promotion_include_v14_and_verifier(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for name in ('athena_runtime_manifest','athena_maxdev_law','athena_promotion_evaluate','athena_promotion_verify_github','athena_joint_factor_belief','athena_joint_science_evi','athena_sequential_dr_policy_value','athena_gp_resolution_route','athena_two_stage_resource_plan'):self.assertIn(name,names)
        for uri in ['athena://manifest','athena://runtime/unified-manifest','athena://runtime/maxdev','athena://promotion','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8','athena://collective/v9','athena://collective/v10','athena://collective/v11','athena://collective/v12','athena://collective/v13','athena://collective/v14']:
            self.assertIn(uri,uris)
        payload=self.read_json('athena://runtime/unified-manifest');canonical=self.read_json('athena://manifest');promotion=self.read_json('athena://promotion');v14=self.read_json('athena://collective/v14')
        self.assertEqual(payload['artifact'],'ATHENA.RUNTIME.UNIFIED.10');self.assertEqual(canonical['artifact'],'ATHENA.RUNTIME.UNIFIED.10');self.assertEqual(canonical['layers'],payload['layers'])
        self.assertEqual(v14['runtime']['version'],'COLLECTIVE_RUNTIME_V14');self.assertIn('do not mutate Y1 authority',v14['boundary'])
        self.assertEqual(promotion['github_verifier']['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertIn('failed GitHub verification creates no PROMRUN',promotion['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        for group in ('manifest','collective_v10','collective_v11','collective_v12','collective_v13','collective_v14','promotion'):self.assertEqual(audit['groups'][group]['status'],'PASS')


if __name__=='__main__':unittest.main()
