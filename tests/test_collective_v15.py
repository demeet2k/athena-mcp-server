import random
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV15Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None):
        r=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result'];self.assertFalse(r.get('isError'),r);return r['structuredContent']

    def test_structural_reliability_out_of_fold(self):
        examples=[]
        for support,correct_count in ((.2,2),(.5,8),(.8,15),(.95,19)):
            examples.extend({'support':support,'correct':1 if i<correct_count else 0} for i in range(20))
        out=self.tool('athena_structural_reliability_calibrate',{'calibration_examples':examples,'supports':[.2,.5,.8,.95],'folds':4,'seed':7})
        self.assertEqual(out['status'],'OUT_OF_FOLD_WEIGHTED_ISOTONIC_STRUCTURAL_RELIABILITY')
        self.assertTrue(out['curve'])
        self.assertEqual(out['unique_support_coordinates'],4)
        probs=[row['calibrated_reliability'] for row in out['curve']]
        self.assertEqual(probs,sorted(probs))
        targets=[row['calibrated_reliability'] for row in out['calibrated_supports']]
        self.assertEqual(targets,sorted(targets))
        self.assertGreaterEqual(out['brier_oof_calibrated'],0)
        self.assertEqual(out['interpolation'],'RIGHT_CONTINUOUS_MONOTONE_STEP_WITH_ENDPOINT_EXTENSION')

    def _longitudinal_rows(self,n=360):
        rng=random.Random(17);rows=[]
        for _ in range(n):
            x=rng.uniform(-1,1)
            p1=max(.1,min(.9,.45+.12*x));a1=1 if rng.random()<p1 else 0
            pl=max(.05,min(.95,.2+.42*a1+.08*x));l1=1 if rng.random()<pl else 0
            p2=max(.1,min(.9,.42+.12*l1-.05*x));a2=1 if rng.random()<p2 else 0
            py=max(.03,min(.97,.06+.16*a1+.09*l1+.5*a2+.05*x));y=1 if rng.random()<py else 0
            rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
        return rows

    def test_cross_fitted_longitudinal_tmle(self):
        rows=self._longitudinal_rows()
        out=self.tool('athena_longitudinal_tmle_crossfit',{
            'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'folds':3,'seed':3,
        })
        self.assertEqual(out['status'],'CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_UNDER_ASSUMPTIONS')
        self.assertTrue(out['cross_fitted']);self.assertEqual(out['folds'],3)
        self.assertEqual(out['history_invariant'],'STAGE2_PSEUDO_OUTCOME_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION')
        by_id={x['id']:x for x in out['regimes']}
        self.assertGreater(by_id['11']['estimated_risk'],by_id['00']['estimated_risk'])

    def test_cross_fitted_sequential_dr_policy(self):
        rows=self._longitudinal_rows()
        out=self.tool('athena_sequential_dr_policy_crossfit',{
            'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'folds':3,'seed':9,
            'policies':[{'id':'none','a1':0,'a2':0},{'id':'both','a1':1,'a2':1}],
        })
        self.assertEqual(out['status'],'CROSS_FITTED_TWO_TIMEPOINT_SEQUENTIAL_AIPW_POLICY_VALUE_UNDER_ASSUMPTIONS')
        self.assertTrue(out['cross_fitted'])
        self.assertEqual(out['history_invariant'],'A1_POLICY_USES_BASELINE_ONLY__A2_POLICY_USES_BASELINE_A1_L1_ONLY')
        self.assertEqual(out['policy_history_firewall']['a1_available_features'],['X'])
        self.assertEqual(out['policy_history_firewall']['a2_available_features'],['X','A1','L1'])
        by_id={x['id']:x for x in out['policies']}
        self.assertGreater(by_id['both']['estimated_value'],by_id['none']['estimated_value'])

    def test_joint_gaussian_update_and_control(self):
        update=self.tool('athena_joint_gaussian_update',{
            'variables':['x','y'],'mean':[0,0],'covariance':[[1,.5],[.5,1]],
            'observation':{'coefficients':{'x':1},'value':1,'noise_variance':.1},
        })
        self.assertEqual(update['status'],'EXACT_LINEAR_GAUSSIAN_JOINT_UPDATE')
        self.assertGreater(update['posterior_mean'][0],0)
        self.assertLess(update['posterior_covariance'][0][0],1)
        control=self.tool('athena_joint_gaussian_control',{
            'variables':['x','y'],'mean':update['posterior_mean'],'covariance':update['posterior_covariance'],
            'actions':[{'id':'long','coefficients':{'x':1}},{'id':'short','coefficients':{'x':-1}}],
            'risk_weight':.25,
        })
        self.assertEqual(control['decision'],'GAUSSIAN_LINEAR_JOINT_CONTROL_PLAN_ONLY')
        self.assertEqual(control['winner'],'long')
        self.assertIn('long',control['pareto_frontier'])

    def test_approximation_error_transport(self):
        out=self.tool('athena_approx_error_transport',{
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.2}],
            'queries':[{'id':'mid','features':{'x':.5},'decision_margin':.6}],
            'lipschitz_bound':.2,'max_transport_radius':.75,'margin_safety':.5,
        })
        self.assertEqual(out['status'],'DECLARED_LIPSCHITZ_APPROXIMATION_ERROR_TRANSPORT')
        self.assertTrue(out['queries'][0]['decision_preserving_under_bound'])
        self.assertLessEqual(out['empirical_minimum_lipschitz'],out['declared_lipschitz_bound'])
        self.assertEqual(out['queries'][0]['nearest_witness_distance'],.5)
        self.assertTrue(out['queries'][0]['within_transport_radius'])

    def test_approximation_radius_uses_best_eligible_witness_not_global_envelope_witness(self):
        out=self.tool('athena_approx_error_transport',{
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':10},{'features':{'x':1},'absolute_error':0}],
            'queries':[{'id':'local','features':{'x':.1},'decision_margin':30}],
            'lipschitz_bound':10,'max_transport_radius':.2,'margin_safety':.5,
        })
        row=out['queries'][0]
        self.assertEqual(row['nearest_witness_index'],0)
        self.assertEqual(row['transport_witness_index'],0)
        self.assertEqual(row['global_envelope_witness_index'],1)
        self.assertTrue(row['within_transport_radius'])
        self.assertTrue(row['decision_preserving_under_bound'])
        self.assertGreater(row['transported_error_upper_bound'],row['global_envelope_upper_bound'])

    def test_multistage_tv_dro_dynamic_program(self):
        out=self.tool('athena_multistage_tv_dro_plan',{
            'states':['G','B'],'initial_state':'G','horizon':3,'tv_radius':.2,
            'actions_by_state':{
                'G':[
                    {'id':'safe','reward':1,'transitions':{'G':.95,'B':.05}},
                    {'id':'risky','reward':2,'transitions':{'G':.5,'B':.5}},
                ],
                'B':[
                    {'id':'recover','reward':-1,'transitions':{'G':.8,'B':.2}},
                    {'id':'stuck','reward':-4,'transitions':{'G':.1,'B':.9}},
                ],
            },
        })
        self.assertEqual(out['status'],'FINITE_HORIZON_RECTANGULAR_TV_DRO_DYNAMIC_PROGRAM_CERTIFIED')
        self.assertEqual(out['certificate'],'EXACT_DYNAMIC_PROGRAM_FOR_SUPPLIED_FINITE_RECTANGULAR_TV_AMBIGUITY_MODEL')
        self.assertEqual(out['policy']['0']['G'],'safe')
        self.assertGreater(out['robust_initial_value'],0)

    def test_v15_tools_are_exposed(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']}
        for name in (
            'athena_structural_reliability_calibrate','athena_longitudinal_tmle_crossfit','athena_sequential_dr_policy_crossfit',
            'athena_joint_gaussian_update','athena_joint_gaussian_control','athena_approx_error_transport','athena_multistage_tv_dro_plan',
        ):
            self.assertIn(name,names)


if __name__=='__main__':unittest.main()
