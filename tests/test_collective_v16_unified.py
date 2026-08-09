import json
import tempfile
import unittest

import athena_mcp
from athena_mcp import unified_manifest
from athena_mcp.collective_v16_install import V16_COORDINATE,V16_LAYER,V16_MANIFEST,V16_PACKAGE_VERSION,V16_RESOURCE
from athena_mcp.collective_v16_protocol import COLLECTIVE_V16_TOOL_NAMES
from athena_mcp.protocol import SERVER_INFO,TOOLS
from athena_mcp.server import Server


class CollectiveV16UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=Server(self.tmp.name)

    def tearDown(self):
        self.server.store.close();self.tmp.close()

    def test_v16_advances_release_identity_and_preserves_unique_tool_registry(self):
        self.assertEqual(V16_PACKAGE_VERSION,'3.5.0')
        self.assertEqual(athena_mcp.__version__,'3.5.0')
        self.assertEqual(SERVER_INFO['version'],'3.5.0')
        self.assertEqual(V16_MANIFEST,'ATHENA.RUNTIME.UNIFIED.12')
        names=[tool['name'] for tool in TOOLS]
        self.assertEqual(len(names),len(set(names)))
        self.assertEqual(set(COLLECTIVE_V16_TOOL_NAMES),{
            'athena_ordered_dag_posterior',
            'athena_longitudinal_dr_multistage_crossfit',
            'athena_gaussian_mixture_update',
            'athena_approx_error_field',
            'athena_coupled_model_robust_policy',
        })
        for name in COLLECTIVE_V16_TOOL_NAMES:
            self.assertEqual(names.count(name),1,name)
        self.assertIn('athena_structural_reliability_calibrate',names)
        self.assertIn('athena_joint_factor_belief',names)
        self.assertIn('athena_deployment_manifest',names)
        self.assertIn('athena_promotion_verify_github',names)

    def test_public_manifest_holonomy_includes_v15_then_v16_without_authority_collapse(self):
        manifest=unified_manifest.build_unified_manifest(self.server)
        self.assertEqual(manifest['artifact'],V16_MANIFEST)
        self.assertIn('ATHENA.RUNTIME.UNIFIED.11',manifest['artifact_compat'])
        layers=manifest['layers']
        self.assertIn('COLLECTIVE_CALIBRATED_V15',layers)
        self.assertIn(V16_LAYER,layers)
        self.assertIn('GITHUB_PROMOTION_VERIFIER.1',layers)
        self.assertLess(layers.index('COLLECTIVE_CALIBRATED_V15'),layers.index(V16_LAYER))
        self.assertLess(layers.index(V16_LAYER),layers.index('GITHUB_PROMOTION_VERIFIER.1'))
        self.assertEqual(manifest['organs']['collective_v16']['coordinate'],V16_COORDINATE)
        self.assertEqual(manifest['collective_generalized']['authority'],'MODEL_SCIENCE_TWIN_AND_PLAN_ONLY')
        self.assertIn('COLLECTIVE(V1-V16)',manifest['cycle'])
        self.assertIn(V16_LAYER,manifest['navigation'])
        law=' '.join(manifest['invariants'])
        for phrase in (
            'ORDER_CONSTRAINED_DAG_POSTERIOR != GENERAL_CAUSAL_GRAPH_POSTERIOR',
            'BOUNDED_MULTISTAGE_CROSS_FITTED_DR != ARBITRARY_HORIZON_LONGITUDINAL_THEOREM',
            'FINITE_GAUSSIAN_MIXTURE != GENERAL_NON_GAUSSIAN_BAYES',
            'CV_RESIDUAL_QUANTILE != DISTRIBUTION_FREE_ERROR_CERTIFICATE',
            'FINITE_FIXED_MODEL_FAMILY_POLICY_EVALUATION != GENERAL_NONRECTANGULAR_DRO_OPTIMIZATION',
        ):
            self.assertIn(phrase,law)

    def test_mcp_surface_exposes_v16_resource_and_tools_without_removing_v15(self):
        init=self.server.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
        self.assertEqual(init['serverInfo']['version'],'3.5.0')
        tools=self.server.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']
        names=[tool['name'] for tool in tools]
        for name in COLLECTIVE_V16_TOOL_NAMES:
            self.assertIn(name,names)
        self.assertIn('athena_structural_reliability_calibrate',names)
        resources=self.server.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']
        uris={row['uri'] for row in resources}
        self.assertIn(V16_RESOURCE['uri'],uris)
        self.assertIn('athena://collective/v15',uris)
        self.assertIn('athena://deployment',uris)
        v16=self.server.handle({'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':V16_RESOURCE['uri']}})['result']['contents'][0]['text']
        payload=json.loads(v16)
        self.assertEqual(payload['runtime']['coordinate'],V16_COORDINATE)
        boundary=payload['boundary']
        for phrase in ('Y1 authority','canonical JSPACE','execution','deployment','release-publication','trusted promotion'):
            self.assertIn(phrase,boundary)

    def test_v16_tool_dispatch_is_read_only_science_control_surface(self):
        rows=[{'X':(i-25)/10.0,'Y':2*((i-25)/10.0)+((i%3)-1)*0.01} for i in range(50)]
        response=self.server.handle({
            'jsonrpc':'2.0','id':9,'method':'tools/call',
            'params':{'name':'athena_ordered_dag_posterior','arguments':{'samples':rows,'order':['X','Y']}}
        })
        self.assertIn('result',response)
        text=response['result']['content'][0]['text']
        payload=json.loads(text)
        self.assertEqual(payload['status'],'EXACT_ORDER_CONSTRAINED_LINEAR_GAUSSIAN_DAG_POSTERIOR')
        self.assertIn('not general causal graph posterior',payload['law'])


if __name__=='__main__':
    unittest.main()
