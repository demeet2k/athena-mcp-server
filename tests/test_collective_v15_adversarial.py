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

    def test_cross_fitted_longitudinal_methods_fail_closed_on_latent_confounding(self):
        rows=self.longitudinal_rows()
        common={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'assumptions':{'latent_confounding_possible':True}}
        tmle=self.tool('athena_longitudinal_tmle_crossfit',common)
        self.assertEqual(tmle['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
        dr=self.tool('athena_sequential_dr_policy_crossfit',{**common,'policies':[{'id':'p','a1':1,'a2':1}]})
        self.assertEqual(dr['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')

    def test_gaussian_joint_rejects_invalid_covariance_and_degenerate_observation(self):
        self.tool('athena_joint_gaussian_update',{
            'variables':['x','y'],'mean':[0,0],'covariance':[[1,2],[2,1]],
            'observation':{'coefficients':{'x':1},'value':0,'noise_variance':.1},
        },expect_error=True)
        self.tool('athena_joint_gaussian_update',{
            'variables':['x'],'mean':[0],'covariance':[[1]],
            'observation':{'coefficients':{'x':0},'value':0,'noise_variance':.1},
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
        self.assertFalse(out['queries'][0]['within_transport_radius'])
        self.assertFalse(out['queries'][0]['decision_preserving_under_bound'])

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


if __name__=='__main__':unittest.main()
