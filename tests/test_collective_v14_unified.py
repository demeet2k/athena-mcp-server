import json
import random
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV14UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']
    def resource(self,uri):return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])

    def test_v14_resource_surface_and_coordinate_are_required(self):
        names={x['name'] for x in self.rpc('tools/list')['result']['tools']};uris={x['uri'] for x in self.rpc('resources/list')['result']['resources']}
        v14={
            'athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi',
            'athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route',
            'athena_two_stage_resource_plan',
        }
        self.assertTrue(v14 <= names)
        self.assertIn('athena://collective/v14',uris)
        payload=self.resource('athena://collective/v14')
        self.assertEqual(payload['runtime']['version'],'COLLECTIVE_RUNTIME_V14')
        self.assertEqual(payload['runtime']['coordinate'],'COLLECTIVE_SYNTHESIS=<JB,SE,JE,DR,RP,AZ,MR,L>')
        self.assertIn('Y1 authority',payload['boundary'])
        self.assertIn('trusted promotion verification',payload['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True})
        self.assertEqual(audit['groups']['collective_v14']['status'],'PASS')
        self.assertEqual(set(audit['contract']['required_tools']['collective_v14']) if 'contract' in audit else v14,v14)

    def test_joint_science_and_policy_outputs_do_not_mutate_y1(self):
        self.tool('athena_claim_register',{'claim_id':'C.V14.UNIFIED','source_ref':'test://v14'})
        before=self.tool('athena_claim_state',{'claim_id':'C.V14.UNIFIED'})
        joint=self.tool('athena_joint_factor_belief',{
            'axes':{'M':[{'id':'m1','weight':.6},{'id':'m2','weight':.4}],'G':[{'id':'g1','weight':.5},{'id':'g2','weight':.5}]}
        })
        ids=[s['id'] for s in joint['states']]
        self.tool('athena_joint_science_evi',{
            'joint_states':joint['states'],
            'actions':[{'id':'a','utility_by_state':{sid:(1 if 'M=m1' in sid else 0) for sid in ids}},{'id':'b','utility_by_state':{sid:(0 if 'M=m1' in sid else 1) for sid in ids}}],
            'experiments':[{'id':'e','outcomes':{'yes':{sid:(.8 if 'M=m1' in sid else .2) for sid in ids},'no':{sid:(.2 if 'M=m1' in sid else .8) for sid in ids}}}],
        })
        self.tool('athena_joint_policy_robust',{
            'joint_states':joint['states'],
            'policies':[{'id':'p','utility_by_state':{sid:.5 for sid in ids}},{'id':'q','utility_by_state':{sid:(.7 if 'G=g1' in sid else .3) for sid in ids}}],
        })
        after=self.tool('athena_claim_state',{'claim_id':'C.V14.UNIFIED'})
        self.assertEqual(before,after)

    def test_bootstrap_graph_is_shadow_only_and_jspace_unchanged(self):
        rng=random.Random(41);rows=[]
        for _ in range(120):
            x=rng.gauss(0,1);y=rng.gauss(0,1);z=.8*x-.7*y+rng.gauss(0,.15);rows.append({'X':x,'Y':y,'Z':z})
        before=self.resource('athena://jspace')
        out=self.tool('athena_structural_bootstrap_ensemble',{'samples':rows,'variables':['X','Y','Z'],'bootstrap_runs':8,'max_conditioning':1,'seed':4})
        self.assertIn('BOOTSTRAP',out['status'])
        after=self.resource('athena://jspace')
        self.assertEqual(before['edges'],after['edges']);self.assertEqual(before['hyperedges'],after['hyperedges'])

    def test_resolution_route_and_joint_design_cannot_self_train_gp(self):
        self.tool('athena_gp_register',{'context_key':'V14.UNIFIED.GP','features':['x'],'length_scale':.7,'signal_variance':1,'noise_variance':.02})
        for x in [0,.2,.4,.6,.8,1]:self.tool('athena_gp_observe',{'context_key':'V14.UNIFIED.GP','features':{'x':x},'target':x*x,'evidence_ref':'test://v14'})
        before=self.tool('athena_gp_state',{'context_key':'V14.UNIFIED.GP'})
        self.tool('athena_gp_resolution_route',{'context_key':'V14.UNIFIED.GP','actions':[{'id':'a','features':{'x':.2}},{'id':'b','features':{'x':.9}}],'inducing_counts':[2,3,4]})
        self.tool('athena_gp_joint_design',{'context_key':'V14.UNIFIED.GP','actions':[{'id':'a','features':{'x':.2}},{'id':'b','features':{'x':.9}}],'experiments':[{'id':'e','features':{'x':.5},'cost':0}],'hyper_samples':32,'mc_samples':80,'seed':2,'cost_weight':0})
        after=self.tool('athena_gp_state',{'context_key':'V14.UNIFIED.GP'})
        self.assertEqual(before['observation_count'],after['observation_count']);self.assertEqual(before['length_scale'],after['length_scale'])

    def test_v14_does_not_weaken_host_bound_promotion_verifier(self):
        names={x['name']:x for x in self.rpc('tools/list')['result']['tools']}
        schema=names['athena_promotion_verify_github']['inputSchema']
        self.assertEqual(schema['required'],['git_head'])
        for forbidden in ('repository','api_url','run_id','token','trusted_external_verification','required_checks','trusted_app_slug'):
            self.assertNotIn(forbidden,schema.get('properties',{}))
        promotion=self.resource('athena://promotion')
        self.assertEqual(promotion['github_verifier']['version'],'ATHENA.GITHUB.PROMOTION.VERIFIER.1')
        self.assertIn('host configuration',promotion['boundary'])


if __name__=='__main__':unittest.main()
