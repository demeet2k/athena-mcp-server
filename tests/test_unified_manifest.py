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

    def test_live_manifest_reports_v15_deployment_github_verifier_and_compatibility(self):
        manifest=self.tool('athena_runtime_manifest')
        self.assertEqual(manifest['artifact'],'ATHENA.RUNTIME.UNIFIED.11')
        for compat in ('ATHENA.RUNTIME.UNIFIED.1','ATHENA.RUNTIME.UNIFIED.2','ATHENA.RUNTIME.UNIFIED.3','ATHENA.RUNTIME.UNIFIED.4','ATHENA.RUNTIME.UNIFIED.5','ATHENA.RUNTIME.UNIFIED.6','ATHENA.RUNTIME.UNIFIED.7','ATHENA.RUNTIME.UNIFIED.8','ATHENA.RUNTIME.UNIFIED.9','ATHENA.RUNTIME.UNIFIED.10'):self.assertIn(compat,manifest['artifact_compat'])
        self.assertEqual(manifest['runtime_class'],'Server')
        for layer in ['COLLECTIVE_MEMORY_V2','COLLECTIVE_LEARNING_V3','COLLECTIVE_ECOLOGY_V4','COLLECTIVE_SCIENCE_V5','COLLECTIVE_DISCOVERY_V6','COLLECTIVE_DUAL_CONTROL_V7','COLLECTIVE_BELIEF_V8','COLLECTIVE_INFERENCE_V9','COLLECTIVE_PROBABILISTIC_V10','COLLECTIVE_ADAPTIVE_V11','COLLECTIVE_JOINT_V12','COLLECTIVE_ROBUST_V13','COLLECTIVE_SYNTHESIS_V14','COLLECTIVE_CALIBRATED_V15','AOR_DECISION_CORTEX','AOR.3','AUTHORITY_Y1','RAG.1','HUG.ABI.1','GAP.1','FIELD.1','AORCOLL.TRANSPORT.1','CYCLE.1','SCHEMA.2','OMEGA.1','RECON.1','SELFTEST.1','SURFACE.2','COMPOSITION.2','PROMOTION.2','GITHUB_PROMOTION_VERIFIER.1']:
            self.assertIn(layer,manifest['layers'])
        joined='\n'.join(manifest['invariants'])
        for phrase in [
            'UNKNOWN != 0','one coherent host-bound GitHub Actions run/check-suite','checks from different suites/runs are never spliced','trusted GitHub repository/API/run context comes from host environment','BELIEF_POSTERIOR != CANONICAL_TRUTH','FINITE_FACTOR_PRODUCT_BELIEF != FULL_JOINT_POSTERIOR',
            'OUT_OF_FOLD_ISOTONIC_RELIABILITY != CAUSAL_GRAPH_POSTERIOR','IDENTICAL_CALIBRATION_COORDINATE != MULTIPLE_FITTED_VALUES',
            'CROSS_FITTED_TWO_TIMEPOINT_TMLE != GENERAL_LONGITUDINAL_TMLE_THEOREM','STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION',
            'CROSS_FITTED_SEQUENTIAL_DR != GENERAL_OFF_POLICY_CAUSAL_VALUE','DECISION_TIME_HISTORY != FULL_ROW_STATE',
            'LINEAR_GAUSSIAN_UPDATE != GENERAL_CONTINUOUS_JOINT_BAYES','GAUSSIAN_LINEAR_CONTROL != GENERAL_BELIEF_MDP','UNKNOWN_COEFFICIENT != ZERO_COEFFICIENT','NONFINITE_NUMERIC_STATE != MODEL_COORDINATE',
            'DECLARED_LIPSCHITZ_ERROR_ENVELOPE != EMPIRICAL_GLOBAL_ERROR_TRUTH','GEOMETRIC_NEAREST_WITNESS != TIGHTEST_ERROR_ENVELOPE_WITNESS','GLOBAL_ENVELOPE != RADIUS_ELIGIBLE_LOCAL_CERTIFICATE',
            'RECTANGULAR_TV_ROBUST_MDP != GENERAL_MULTISTAGE_DRO','UNKNOWN_STATE_COORDINATE != UNUSED_METADATA','NONFINITE_TRANSITION != PROBABILITY_MODEL','ZERO_TEST_SELECTION != PROOF',
            'athena_claim_* = Y1 canonical authority',
        ]:
            self.assertIn(phrase,joined)
        self.assertEqual(manifest['collective_synthesis']['version'],'COLLECTIVE_RUNTIME_V14')
        self.assertEqual(manifest['collective_calibrated']['version'],'COLLECTIVE_RUNTIME_V15')
        self.assertEqual(manifest['collective_calibrated']['coordinate'],'COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>')
        self.assertEqual(manifest['collective_calibrated']['decision_time_history'],{'A1':'baseline','A2':'baseline+A1+L1'})
        self.assertEqual(manifest['collective_calibrated']['error_transport_coordinates'],['geometric_nearest','global_envelope','radius_eligible_local_certificate'])
        self.assertEqual(manifest['collective_calibrated']['numeric_policy'],'reject unknown or non-finite model coordinates')
        self.assertIn('collective_v15',manifest['organs'])
        self.assertIn('DECISION_TIME_HISTORY != FULL_ROW_STATE',manifest['organs']['collective_v15']['audit_laws'])
        self.assertIn('COLLECTIVE(V1-V15)',manifest['cycle'])
        self.assertIn('COLLECTIVE_CALIBRATED_V15',manifest['navigation'])
        verifier=manifest['promotion_verifier'];self.assertEqual(verifier['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertEqual(verifier['required_checks'],['syntax','unit','critical-invariants','smoke']);self.assertEqual(verifier['trusted_app_slug'],'github-actions')
        unresolved={x['id']:x for x in manifest['unresolved']}
        for uid in ('GENERAL_BELIEF_CONTROL','FORMAL_CAUSAL_DISCOVERY','LONGITUDINAL_CAUSAL_POLICY','STOCHASTIC_RESOURCE_CONTROL'):
            self.assertIn('v15_boundary',unresolved[uid])
        self.assertEqual(unresolved['NON_GITHUB_PROMOTION_VERIFIERS']['status'],'UNRESOLVED_OPTIONAL_INTEGRATION')
        self.assertEqual(manifest['schema']['target'],2);self.assertEqual(manifest['startup']['status'],'DEGRADED_SCHEMA')

    def test_manifest_updates_live_schema_state_after_migration(self):
        before=self.tool('athena_runtime_manifest');self.assertFalse(before['schema']['up_to_date']);self.tool('athena_schema_migrate');after=self.tool('athena_runtime_manifest');self.assertTrue(after['schema']['up_to_date']);self.assertEqual(after['schema']['current'],2);self.assertEqual(after['startup']['status'],'READY_LOCAL')

    def test_maxdev_law_contains_v15_and_trusted_github_promotion_boundaries(self):
        law=self.tool('athena_maxdev_law')['text']
        for phrase in ['RECONSTRUCT through RECONRUN + canonical OMEGA','V14 SYNTHESIS LAW','V15 CALIBRATION LAW','pool identical structural-support coordinates','out-of-fold reliability','stage-1 policies may use baseline only','reject unknown Gaussian/state/action coordinates','geometric nearest witness','cross-fit two-timepoint sequential TMLE/AIPW','multivariate-Gaussian conditioning','transport approximation error','rectangular total-variation ambiguity','zero selected tests are not proof','caller-bound packets stop at ATTESTED_READY','prefer athena_promotion_verify_github','one coherent exact-head Actions run/check-suite','Never splice checks across runs/suites']:
            self.assertIn(phrase,law)

    def test_manifest_resources_surface2_promotion_and_deployment_include_v15(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        for name in ('athena_runtime_manifest','athena_maxdev_law','athena_promotion_evaluate','athena_promotion_verify_github','athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit','athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan','athena_deployment_manifest','athena_deployment_validate'):
            self.assertIn(name,names)
        for uri in ['athena://manifest','athena://runtime/unified-manifest','athena://runtime/maxdev','athena://promotion','athena://collective/v13','athena://collective/v14','athena://collective/v15','athena://deployment','athena://deployment/evidence','athena://deployment/rollout','athena://deployment/security']:
            self.assertIn(uri,uris)
        tool_manifest=self.tool('athena_runtime_manifest')
        payload=self.read_json('athena://runtime/unified-manifest');canonical=self.read_json('athena://manifest');promotion=self.read_json('athena://promotion');v15=self.read_json('athena://collective/v15')
        for current in (tool_manifest,payload,canonical):
            self.assertEqual(current['artifact'],'ATHENA.RUNTIME.UNIFIED.11')
            self.assertEqual(current['layers'],tool_manifest['layers'])
            self.assertEqual(current['collective_calibrated'],tool_manifest['collective_calibrated'])
            self.assertEqual(current['invariants'],tool_manifest['invariants'])
        self.assertEqual(v15['runtime']['version'],'COLLECTIVE_RUNTIME_V15');self.assertIn('Y1 authority',v15['boundary']);self.assertIn('trusted promotion state',v15['boundary'])
        self.assertEqual(v15['decision_time_history'],{'A1':'baseline only','A2':'baseline + A1 + L1 only'})
        self.assertIn('DECISION_TIME_HISTORY != FULL_ROW_STATE',v15['runtime']['audit_laws'])
        self.assertIn('NONFINITE_NUMERIC_STATE != MODEL_COORDINATE',v15['runtime']['audit_laws'])
        self.assertEqual(promotion['github_verifier']['version'],GITHUB_PROMOTION_VERIFIER_VERSION);self.assertIn('failed GitHub verification creates no PROMRUN',promotion['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        for group in ('manifest','collective_v13','collective_v14','collective_v15','promotion'):self.assertEqual(audit['groups'][group]['status'],'PASS')


if __name__=='__main__':unittest.main()
