import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV15AdversarialTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args=None,expect_error=False):
        result=self.rpc('tools/call',{'name':name,'arguments':args or {}})['result']
        if expect_error:self.assertTrue(result.get('isError'),result);return result
        self.assertFalse(result.get('isError'),result);return result['structuredContent']

    @staticmethod
    def longitudinal_rows(n=200):
        rows=[]
        for i in range(n):
            x=(i%20)/10-1;a1=i%2;l1=(i//2)%2;a2=(i//3)%2;y=1 if a2 or (a1 and l1) else 0
            rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
        return rows

    def test_structural_calibration_requires_external_labelled_mass(self):
        self.tool('athena_structural_reliability_calibrate',{'calibration_examples':[{'support':.8,'correct':1}]*8},expect_error=True)
        bad=[{'support':.5,'correct':1} for _ in range(40)];bad[0]['support']=1.2
        self.tool('athena_structural_reliability_calibrate',{'calibration_examples':bad},expect_error=True)
        nonfinite=[{'support':.5,'correct':1,'weight':1} for _ in range(40)];nonfinite[0]['weight']=float('nan')
        self.tool('athena_structural_reliability_calibrate',{'calibration_examples':nonfinite},expect_error=True)

    def test_structural_calibration_pools_duplicate_support_coordinates_before_pav(self):
        examples=[]
        for _ in range(20):examples.append({'support':.5,'correct':0,'weight':1})
        for _ in range(20):examples.append({'support':.5,'correct':1,'weight':3})
        out=self.tool('athena_structural_reliability_calibrate',{'calibration_examples':examples,'supports':[.5],'folds':5,'seed':3})
        self.assertEqual(out['status'],'OUT_OF_FOLD_WEIGHTED_ISOTONIC_STRUCTURAL_RELIABILITY')
        self.assertEqual(out['unique_support_coordinates'],1)
        self.assertEqual(len(out['curve']),1)
        self.assertAlmostEqual(out['curve'][0]['calibrated_reliability'],.75,places=10)
        self.assertAlmostEqual(out['calibrated_supports'][0]['calibrated_reliability'],.75,places=10)
        self.assertTrue(out['weighted'])
        self.assertEqual(out['interpolation'],'RIGHT_CONTINUOUS_MONOTONE_STEP_WITH_ENDPOINT_EXTENSION')

    def test_cross_fitted_longitudinal_methods_fail_closed_on_latent_confounding(self):
        rows=self.longitudinal_rows()
        common={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'assumptions':{'latent_confounding_possible':True}}
        tmle=self.tool('athena_longitudinal_tmle_crossfit',common)
        self.assertEqual(tmle['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
        dr=self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'p','a1':1,'a2':1}]})
        self.assertEqual(dr['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')

    def test_longitudinal_baseline_cannot_smuggle_treatment_or_outcome_fields(self):
        rows=self.longitudinal_rows()
        for leaked in ('A1','L1','A2','Y'):
            common={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X',leaked]}
            self.tool('athena_longitudinal_tmle_crossfit',common,expect_error=True)
            self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'p','a1':1,'a2':1}]},expect_error=True)
        duplicate_names={'samples':rows,'treatment1':'A1','intermediate':'A1','treatment2':'A2','outcome':'Y','baseline':['X']}
        self.tool('athena_longitudinal_tmle_crossfit',duplicate_names,expect_error=True)

    def test_longitudinal_rejects_nonfinite_baseline_propensity_and_policy_parameters(self):
        rows=self.longitudinal_rows();rows[0]=dict(rows[0]);rows[0]['X']=float('nan')
        common={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']}
        self.tool('athena_longitudinal_tmle_crossfit',common,expect_error=True)
        self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'p','a1':1,'a2':1}]},expect_error=True)
        rows=self.longitudinal_rows();valid={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']}
        self.tool('athena_longitudinal_tmle_crossfit',{**valid,'propensity_clip':float('nan')},expect_error=True)
        self.tool('athena_sequential_dr_policy_crossfit',{**valid,'policies':[{'id':'p','a1':1,'a2':1}],'propensity_clip':float('inf')},expect_error=True)
        self.tool('athena_sequential_dr_policy_crossfit',{**valid,'policies':[{'id':'p','a1':{'coefficients':{'X':float('nan')}},'a2':1}]},expect_error=True)

    def test_dynamic_policy_cannot_read_future_or_outcome_state(self):
        rows=self.longitudinal_rows()
        common={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']}
        forbidden=[
            {'id':'future-l1-at-a1','a1':{'coefficients':{'L1':1}},'a2':1},
            {'id':'future-a2-at-a1','a1':{'coefficients':{'A2':1}},'a2':1},
            {'id':'outcome-at-a1','a1':{'coefficients':{'Y':1}},'a2':1},
            {'id':'own-treatment-at-a2','a1':1,'a2':{'coefficients':{'A2':1}}},
            {'id':'outcome-at-a2','a1':1,'a2':{'coefficients':{'Y':1}}},
        ]
        for policy in forbidden:
            self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[policy]},expect_error=True)
        self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'same','a1':0,'a2':0},{'id':'same','a1':1,'a2':1}]},expect_error=True)
        allowed=self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'history-only','a1':{'coefficients':{'X':1}},'a2':{'coefficients':{'X':.2,'A1':.5,'L1':.7}}}]})
        self.assertEqual(allowed['history_invariant'],'A1_POLICY_USES_BASELINE_ONLY__A2_POLICY_USES_BASELINE_A1_L1_ONLY')
        self.assertEqual(allowed['policy_history_firewall']['a1_available_features'],['X'])
        self.assertEqual(allowed['policy_history_firewall']['a2_available_features'],['X','A1','L1'])

    def test_gaussian_joint_rejects_invalid_covariance_and_degenerate_observation(self):
        self.tool('athena_joint_gaussian_update',{
            'variables':['x','y'],'mean':[0,0],'covariance':[[1,2],[2,1]],
            'observation':{'coefficients':{'x':1},'value':0,'noise_variance':.1},
        },expect_error=True)
        self.tool('athena_joint_gaussian_update',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'observation':{'coefficients':{'x':0},'value':0,'noise_variance':.1},
        },expect_error=True)

    def test_gaussian_joint_rejects_nonfinite_unknown_and_ambiguous_coordinates(self):
        self.tool('athena_joint_gaussian_update',{
            'variables':['x'],'mean':[float('nan')],'covariance':[[1]],
            'observation':{'coefficients':{'x':1},'value':0,'noise_variance':.1},
        },expect_error=True)
        self.tool('athena_joint_gaussian_update',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'observation':{'coefficients':{'z':1},'value':0,'noise_variance':.1},
        },expect_error=True)
        self.tool('athena_joint_gaussian_control',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'actions':[{'id':'dup','coefficients':{'x':1}},{'id':'dup','coefficients':{'x':-1}}],
        },expect_error=True)
        self.tool('athena_joint_gaussian_control',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'actions':[{'id':'bad','coefficients':{'z':1}}],
        },expect_error=True)
        self.tool('athena_joint_gaussian_control',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'actions':[{'id':'bad','coefficients':{'x':1},'cost':-1}],
        },expect_error=True)

    def test_error_transport_rejects_unwitnessed_lipschitz_claim(self):
        self.tool('athena_approx_error_transport',{
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':0},{'features':{'x':1},'absolute_error':1}],
            'queries':[{'features':{'x':.5}}],
            'lipschitz_bound':.2,
        },expect_error=True)
        out=self.tool('athena_approx_error_transport',{
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.1}],
            'queries':[{'features':{'x':10},'decision_margin':100}],
            'lipschitz_bound':.1,'max_transport_radius':1,
        })
        query=out['queries'][0]
        self.assertFalse(query['within_transport_radius'])
        self.assertFalse(query['local_certificate_available'])
        self.assertIsNone(query['transported_error_upper_bound'])
        self.assertIsNone(query['transport_witness_index'])
        self.assertIsNone(query['transport_witness_distance'])
        self.assertIsNotNone(query['global_envelope_upper_bound'])
        self.assertFalse(query['decision_preserving_under_bound'])

    def test_error_transport_requires_unique_query_identity(self):
        common={
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.2}],
            'lipschitz_bound':.2,
        }
        self.tool('athena_approx_error_transport',{**common,'queries':[{'id':'Q','features':{'x':.2}},{'id':'Q','features':{'x':.8}}]},expect_error=True)

    def test_error_transport_rejects_nonfinite_and_invalid_locality_parameters(self):
        common={
            'feature_order':['x'],
            'witnesses':[{'features':{'x':0},'absolute_error':.1},{'features':{'x':1},'absolute_error':.2}],
            'queries':[{'features':{'x':.5}}],
            'lipschitz_bound':.2,
        }
        self.tool('athena_approx_error_transport',{**common,'max_transport_radius':-1},expect_error=True)
        self.tool('athena_approx_error_transport',{**common,'margin_safety':1.1},expect_error=True)
        bad={**common,'witnesses':[{'features':{'x':float('inf')},'absolute_error':.1},{'features':{'x':1},'absolute_error':.2}]}
        self.tool('athena_approx_error_transport',bad,expect_error=True)

    def test_multistage_tv_dro_rejects_incomplete_probability_model(self):
        self.tool('athena_multistage_tv_dro_plan',{
            'states':['A','B'],'initial_state':'A','horizon':2,'tv_radius':.2,
            'actions_by_state':{
                'A':[{'id':'a','reward':1,'transitions':{'A':.8,'B':.3}}],
                'B':[{'id':'b','reward':0,'transitions':{'B':1}}],
            },
        },expect_error=True)
        self.tool('athena_multistage_tv_dro_plan',{
            'states':['A'],'initial_state':'A','horizon':9,'tv_radius':.2,
            'actions_by_state':{'A':[{'id':'a','reward':1,'transitions':{'A':1}}]},
        },expect_error=True)

    def test_multistage_tv_dro_rejects_nonfinite_duplicate_and_extra_coordinates(self):
        base={
            'states':['A'],'initial_state':'A','horizon':2,'tv_radius':.2,
            'actions_by_state':{'A':[{'id':'a','reward':1,'transitions':{'A':1}}]},
        }
        self.tool('athena_multistage_tv_dro_plan',{**base,'actions_by_state':{'A':[{'id':'a','reward':float('nan'),'transitions':{'A':1}}]}},expect_error=True)
        self.tool('athena_multistage_tv_dro_plan',{**base,'actions_by_state':{'A':[{'id':'a','reward':1,'transitions':{'A':float('nan')}}]}},expect_error=True)
        self.tool('athena_multistage_tv_dro_plan',{**base,'actions_by_state':{'A':[{'id':'same','reward':1,'transitions':{'A':1}},{'id':'same','reward':0,'transitions':{'A':1}}]}},expect_error=True)
        self.tool('athena_multistage_tv_dro_plan',{**base,'actions_by_state':{'A':[{'id':'a','reward':1,'transitions':{'A':1}}],'EXTRA':[{'id':'x','reward':0,'transitions':{'A':1}}]}},expect_error=True)


if __name__=='__main__':unittest.main()
