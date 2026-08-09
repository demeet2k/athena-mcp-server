import json
import random
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV14AdversarialTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0

    def tearDown(self):self.server.store.close();self.tmp.close()

    def rpc(self,method,params=None):
        self.seq+=1;msg={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:msg['params']=params
        return self.server.handle(msg)

    def tool(self,name,args=None,expect_error=False):
        result=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result']
        if expect_error:
            self.assertTrue(result.get('isError'),result);return result
        self.assertFalse(result.get('isError'),result);return result['structuredContent']

    def resource(self,uri):
        return json.loads(self.rpc('resources/read',{'uri':uri})['result']['contents'][0]['text'])

    def test_joint_factor_belief_rejects_explosion_and_incomplete_likelihood(self):
        axes={f'A{i}':[{'id':f'{i}:{j}','weight':1} for j in range(5)] for i in range(5)}
        self.tool('athena_joint_factor_belief',{'axes':axes},expect_error=True)
        self.tool('athena_joint_factor_belief',{
            'axes':{'M':[{'id':'m1'},{'id':'m2'}],'G':[{'id':'g1'},{'id':'g2'}]},
            'likelihood_by_state':{'G=g1|M=m1':1.0},
        },expect_error=True)

    def test_bootstrap_structure_cannot_mutate_jspace(self):
        rng=random.Random(3);rows=[]
        for _ in range(120):
            x=rng.gauss(0,1);y=rng.gauss(0,1);z=x+y+rng.gauss(0,.2);rows.append({'X':x,'Y':y,'Z':z})
        before=self.resource('athena://jspace')
        self.tool('athena_structural_bootstrap_ensemble',{'samples':rows,'variables':['X','Y','Z'],'bootstrap_runs':8,'max_conditioning':1,'seed':2})
        after=self.resource('athena://jspace')
        self.assertEqual(before['edges'],after['edges']);self.assertEqual(before['hyperedges'],after['hyperedges'])

    def test_joint_evi_incomplete_likelihood_rejects_and_y1_is_unchanged(self):
        self.tool('athena_claim_register',{'claim_id':'C.V14','source_ref':'test://claim'})
        before=self.tool('athena_claim_state',{'claim_id':'C.V14'})
        bad={
            'joint_states':[{'id':'S1','weight':.5},{'id':'S2','weight':.5}],
            'actions':[{'id':'A','utility_by_state':{'S1':1,'S2':0}}],
            'experiments':[{'id':'E','outcomes':{'yes':{'S1':.9,'S2':.1},'no':{'S1':.2,'S2':.9}}}],
        }
        self.tool('athena_joint_science_evi',bad,expect_error=True)
        after=self.tool('athena_claim_state',{'claim_id':'C.V14'})
        self.assertEqual(before,after)

    def _rows(self,n=180):
        rng=random.Random(9);rows=[]
        for _ in range(n):
            x=rng.uniform(-1,1);a1=1 if rng.random()<.5 else 0;l1=1 if rng.random()<(.25+.35*a1) else 0;a2=1 if rng.random()<(.4+.15*l1) else 0;y=1 if rng.random()<min(.95,.08+.15*a1+.1*l1+.45*a2) else 0
            rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
        return rows

    def test_sequential_dr_fails_closed_on_latent_confounding(self):
        out=self.tool('athena_sequential_dr_policy_value',{
            'samples':self._rows(),'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],
            'policies':[{'id':'p','a1':1,'a2':1}],
            'assumptions':{'latent_confounding_possible':True},
        })
        self.assertEqual(out['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')

    def test_resolution_router_never_trains_gp(self):
        self.tool('athena_gp_register',{'context_key':'V14.READONLY','features':['x'],'length_scale':.6,'signal_variance':1,'noise_variance':.02})
        for x in [0,.25,.5,.75,1]:
            self.tool('athena_gp_observe',{'context_key':'V14.READONLY','features':{'x':x},'target':x*x,'evidence_ref':'test://obs'})
        before=self.tool('athena_gp_state',{'context_key':'V14.READONLY'})
        self.tool('athena_gp_resolution_route',{'context_key':'V14.READONLY','actions':[{'id':'a','features':{'x':.2}},{'id':'b','features':{'x':.8}}],'inducing_counts':[2,3,4]})
        after=self.tool('athena_gp_state',{'context_key':'V14.READONLY'})
        self.assertEqual(before['observation_count'],after['observation_count'])
        self.assertEqual(before['length_scale'],after['length_scale'])

    def test_robust_policy_is_plan_only_and_does_not_touch_y1(self):
        self.tool('athena_claim_register',{'claim_id':'C.POLICY','source_ref':'test://policy'})
        before=self.tool('athena_claim_state',{'claim_id':'C.POLICY'})
        out=self.tool('athena_joint_policy_robust',{
            'joint_states':[{'id':'S1','weight':.5},{'id':'S2','weight':.5}],
            'policies':[{'id':'P','utility_by_state':{'S1':1,'S2':0}},{'id':'Q','utility_by_state':{'S1':.6,'S2':.6}}],
        })
        self.assertIn('PLAN_ONLY',out['decision'])
        after=self.tool('athena_claim_state',{'claim_id':'C.POLICY'})
        self.assertEqual(before,after)

    def test_two_stage_large_problem_loses_exact_certificate_and_missing_resource_rejects(self):
        first=[{'id':f'F{i}','value':1+i/100,'resources':{'tokens':1}} for i in range(17)]
        scenarios=[{'id':'S','probability':1,'budgets':{'tokens':6},'recourse_options':[]}]
        out=self.tool('athena_two_stage_resource_plan',{'first_stage':first,'scenarios':scenarios,'exact_limit':8})
        self.assertEqual(out['status'],'TWO_STAGE_RESOURCE_GREEDY_UNCERTIFIED')
        self.assertIsNone(out['certificate'])
        self.tool('athena_two_stage_resource_plan',{
            'first_stage':[{'id':'bad','value':1,'resources':{}}],
            'scenarios':[{'id':'S','probability':1,'budgets':{'tokens':1},'recourse_options':[]}],
        },expect_error=True)


if __name__=='__main__':unittest.main()
