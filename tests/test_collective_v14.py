import math
import random
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV14Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db')
        self.server=Server(self.tmp.name)
        self.seq=0

    def tearDown(self):
        self.server.store.close();self.tmp.close()

    def rpc(self,method,params=None):
        self.seq+=1
        msg={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:msg['params']=params
        return self.server.handle(msg)

    def tool(self,name,args=None):
        result=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result']
        self.assertFalse(result.get('isError'),result)
        return result['structuredContent']

    def test_joint_factor_belief_and_joint_evi(self):
        joint=self.tool('athena_joint_factor_belief',{
            'axes':{
                'model':[{'id':'M1','weight':.5},{'id':'M2','weight':.5}],
                'graph':[{'id':'G1','weight':.5},{'id':'G2','weight':.5}],
            },
            'compatibility':[{'assignments':{'model':'M1','graph':'G1'},'multiplier':4.0}],
        })
        self.assertEqual(joint['status'],'FINITE_JOINT_FACTOR_BELIEF')
        self.assertEqual(joint['state_count'],4)
        self.assertAlmostEqual(sum(x['weight'] for x in joint['states']),1.0,places=8)
        ids=[x['id'] for x in joint['states']]
        actions=[
            {'id':'left','utility_by_state':{sid:(1.0 if 'model=M1' in sid else 0.0) for sid in ids}},
            {'id':'right','utility_by_state':{sid:(0.0 if 'model=M1' in sid else 1.0) for sid in ids}},
        ]
        experiment={'id':'probe','cost':0.0,'risk':0.0,'outcomes':{
            'positive':{sid:(.9 if 'model=M1' in sid else .1) for sid in ids},
            'negative':{sid:(.1 if 'model=M1' in sid else .9) for sid in ids},
        }}
        evi=self.tool('athena_joint_science_evi',{'joint_states':joint['states'],'actions':actions,'experiments':[experiment]})
        self.assertEqual(evi['decision'],'FINITE_JOINT_SCIENCE_EVI_DESIGN_ONLY')
        self.assertEqual(evi['winner'],'probe')
        self.assertGreater(evi['ranked'][0]['decision_evi'],0)
        self.assertGreater(evi['ranked'][0]['joint_information_gain_bits'],0)

    def test_structural_bootstrap_ensemble(self):
        rng=random.Random(11);rows=[]
        for _ in range(180):
            x=rng.gauss(0,1);y=rng.gauss(0,1);z=.9*x-.7*y+rng.gauss(0,.12)
            rows.append({'X':x,'Y':y,'Z':z})
        out=self.tool('athena_structural_bootstrap_ensemble',{
            'samples':rows,'variables':['X','Y','Z'],'bootstrap_runs':16,'alpha':.01,'max_conditioning':1,'seed':5,
        })
        self.assertEqual(out['status'],'BOOTSTRAP_FCI_LITE_STRUCTURAL_ENSEMBLE')
        self.assertGreaterEqual(out['valid_runs'],8)
        self.assertAlmostEqual(sum(v['support'] for v in out['variants']),1.0,places=7)
        self.assertGreaterEqual(out['variant_count'],1)

    def _longitudinal_rows(self,n=320):
        rng=random.Random(17);rows=[]
        for _ in range(n):
            x=rng.uniform(-1,1)
            p1=max(.1,min(.9,.45+.12*x));a1=1 if rng.random()<p1 else 0
            pl=max(.05,min(.95,.2+.42*a1+.08*x));l1=1 if rng.random()<pl else 0
            p2=max(.1,min(.9,.42+.12*l1-.05*x));a2=1 if rng.random()<p2 else 0
            py=max(.03,min(.97,.06+.16*a1+.09*l1+.5*a2+.05*x));y=1 if rng.random()<py else 0
            rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
        return rows

    def test_sequential_dr_policy_value(self):
        rows=self._longitudinal_rows()
        out=self.tool('athena_sequential_dr_policy_value',{
            'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],
            'policies':[{'id':'none','a1':0,'a2':0},{'id':'both','a1':1,'a2':1}],
        })
        self.assertEqual(out['status'],'TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS')
        self.assertFalse(out['cross_fitted'])
        by_id={p['id']:p for p in out['policies']}
        self.assertGreater(by_id['both']['estimated_value'],by_id['none']['estimated_value'])
        self.assertIn('OBSERVED_A1_L1',out['history_invariant'])
        self.assertGreaterEqual(by_id['both']['standard_error'],0)

    def test_joint_policy_robustness_preserves_pareto(self):
        out=self.tool('athena_joint_policy_robust',{
            'joint_states':[{'id':'S1','weight':.5},{'id':'S2','weight':.5}],
            'policies':[
                {'id':'spiky','utility_by_state':{'S1':10,'S2':0}},
                {'id':'stable','utility_by_state':{'S1':6,'S2':6}},
            ],
            'cvar_alpha':.5,'risk_weight':1.0,'regret_weight':1.0,
        })
        self.assertEqual(out['decision'],'FINITE_JOINT_SCENARIO_ROBUST_POLICY_PLAN_ONLY')
        self.assertEqual(out['winner'],'stable')
        self.assertIn('stable',out['pareto_frontier'])

    def _seed_gp(self):
        self.tool('athena_gp_register',{'context_key':'V14.GP','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.02})
        for x in [0,.2,.4,.6,.8,1.0]:
            self.tool('athena_gp_observe',{'context_key':'V14.GP','features':{'x':x},'target':x*x,'evidence_ref':'test://v14'})

    def test_gp_resolution_router(self):
        self._seed_gp()
        out=self.tool('athena_gp_resolution_route',{
            'context_key':'V14.GP',
            'actions':[{'id':'low','features':{'x':.2}},{'id':'high','features':{'x':.9}}],
            'inducing_counts':[2,3,4,6],
            'margin_safety':.5,
        })
        self.assertEqual(out['decision'],'GP_DECISION_RELATIVE_RESOLUTION_ROUTE')
        self.assertEqual(out['exact_winner'],'high')
        self.assertIn(out['selected']['mode'],{'FITC','FULL_GP'})
        self.assertTrue(out['selected']['decision_preserving_on_queried_action_set'])

    def test_two_stage_resource_exact_recourse(self):
        out=self.tool('athena_two_stage_resource_plan',{
            'first_stage':[
                {'id':'A','value':5,'resources':{'tokens':2}},
                {'id':'B','value':4,'resources':{'tokens':2}},
            ],
            'scenarios':[
                {'id':'S1','probability':.5,'budgets':{'tokens':5},'recourse_options':[{'id':'R1','value':2,'resources':{'tokens':1}}]},
                {'id':'S2','probability':.5,'budgets':{'tokens':4},'recourse_options':[{'id':'R2','value':3,'resources':{'tokens':1}}]},
            ],
        })
        self.assertEqual(out['status'],'TWO_STAGE_RESOURCE_EXACT_ENUMERATION_CERTIFIED')
        self.assertEqual(set(out['selected']),{'A','B'})
        self.assertEqual(out['certificate'],'EXACT_ENUMERATION_FOR_SUPPLIED_FINITE_TWO_STAGE_SCENARIO_MODEL')
        self.assertEqual(len(out['scenario_recourse']),2)

    def test_v14_tools_are_exposed(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']}
        for name in (
            'athena_joint_factor_belief','athena_structural_bootstrap_ensemble','athena_joint_science_evi',
            'athena_sequential_dr_policy_value','athena_joint_policy_robust','athena_gp_resolution_route',
            'athena_two_stage_resource_plan',
        ):
            self.assertIn(name,names)


if __name__=='__main__':unittest.main()
