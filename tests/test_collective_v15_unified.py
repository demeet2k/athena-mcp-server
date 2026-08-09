import json
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV15UnifiedTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        result=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result'];self.assertFalse(result.get('isError'),result);return result['structuredContent']
    def resource(self,uri):return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])

    def test_v15_resource_surface_coordinate_and_surface_audit(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        v15={
            'athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit',
            'athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan',
        }
        self.assertTrue(v15 <= names);self.assertIn('athena://collective/v15',uris)
        payload=self.resource('athena://collective/v15')
        self.assertEqual(payload['runtime']['version'],'COLLECTIVE_RUNTIME_V15')
        self.assertEqual(payload['runtime']['coordinate'],'COLLECTIVE_CALIBRATED=<SR,XT,XD,CJ,AT,MD,L>')
        self.assertIn('Y1 authority',payload['boundary']);self.assertIn('trusted promotion state',payload['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        self.assertEqual(audit['groups']['collective_v15']['status'],'PASS')

    def test_v15_calibration_model_and_plans_do_not_mutate_y1(self):
        self.tool('athena_claim_register',{'claim_id':'C.V15.UNIFIED','source_ref':'test://v15'})
        before=self.tool('athena_claim_state',{'claim_id':'C.V15.UNIFIED'})
        examples=[]
        for support,correct in ((.2,0),(.4,0),(.6,1),(.8,1)):
            examples.extend({'support':support,'correct':correct} for _ in range(12))
        self.tool('athena_structural_reliability_calibrate',{'calibration_examples':examples,'supports':[.5,.7]})
        update=self.tool('athena_joint_gaussian_update',{
            'variables':['x','y'],'mean':[0,0],'covariance':[[1,.2],[.2,1]],
            'observation':{'coefficients':{'x':1},'value':.5,'noise_variance':.2},
        })
        self.tool('athena_joint_gaussian_control',{
            'variables':['x','y'],'mean':update['posterior_mean'],'covariance':update['posterior_covariance'],
            'actions':[{'id':'a','coefficients':{'x':1}},{'id':'b','coefficients':{'y':1}}],
        })
        self.tool('athena_approx_error_transport',{
            'feature_order':['x'],'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.1}],
            'queries':[{'features':{'x':.5},'decision_margin':1}],'lipschitz_bound':.1,
        })
        self.tool('athena_multistage_tv_dro_plan',{
            'states':['S'],'initial_state':'S','horizon':2,'tv_radius':.1,
            'actions_by_state':{'S':[{'id':'stay','reward':1,'transitions':{'S':1}}]},
        })
        after=self.tool('athena_claim_state',{'claim_id':'C.V15.UNIFIED'})
        self.assertEqual(before,after)

    def test_structural_reliability_never_mutates_jspace(self):
        before=self.resource('athena://jspace')
        examples=[]
        for i in range(60):examples.append({'support':(i%10)/10,'correct':1 if i%10>=5 else 0})
        self.tool('athena_structural_reliability_calibrate',{'calibration_examples':examples,'supports':[.3,.8],'folds':3})
        after=self.resource('athena://jspace')
        self.assertEqual(before['edges'],after['edges']);self.assertEqual(before['hyperedges'],after['hyperedges'])

    def test_v15_preserves_host_bound_promotion_and_operational_basis(self):
        names={x['name']:x for x in self.rpc('tools/list')['result']['tools']}
        schema=names['athena_promotion_verify_github']['inputSchema']
        self.assertEqual(schema['required'],['git_head'])
        for forbidden in ('repository','api_url','run_id','token','trusted_external_verification','required_checks','trusted_app_slug'):
            self.assertNotIn(forbidden,schema.get('properties',{}))
        promotion=self.resource('athena://promotion')
        self.assertEqual(promotion['github_verifier']['version'],'ATHENA.GITHUB.PROMOTION.VERIFIER.1')
        basis=self.tool('athena_operational_basis')
        by_name={x['operation']:x for x in basis['descriptors']}
        self.assertEqual(by_name['athena_message_board']['capability_class'],'MESSAGE_BOARD_COORDINATION')
        self.assertEqual(by_name['athena_party_form']['capability_class'],'PARTY_COORDINATION')
        self.assertEqual(by_name['athena_cohesion_matchmake']['capability_class'],'COHESION_COORDINATION')


if __name__=='__main__':unittest.main()
