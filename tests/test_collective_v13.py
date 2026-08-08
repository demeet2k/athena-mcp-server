import math
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV13Tests(unittest.TestCase):
    def _gp(self,srv):
        srv.call_tool('athena_gp_register',{'context_key':'G13','features':['x'],'length_scale':.7,'signal_variance':1.0,'noise_variance':.03})
        for i,x in enumerate((-1.0,-.75,-.5,-.25,0.0,.25,.5,.75,1.0)):
            srv.call_tool('athena_gp_observe',{'context_key':'G13','features':{'x':x},'target':x*x+.04*math.sin(i),'evidence_ref':f'test://{i}'})

    def _long_rows(self,n=320):
        rows=[]
        for i in range(n):
            x=((i*17)%101)/100.0-.5
            pa1=max(.1,min(.9,.45+.15*x));a1=1 if ((i*29)%100)/100.0<pa1 else 0
            pl=max(.08,min(.92,.20+.35*a1+.15*x));l1=1 if ((i*37)%100)/100.0<pl else 0
            pa2=max(.08,min(.92,.30+.15*a1+.25*l1+.10*x));a2=1 if ((i*41)%100)/100.0<pa2 else 0
            py=max(.03,min(.97,.07+.10*a1+.16*l1+.48*a2+.08*x));y=1 if ((i*53)%100)/100.0<py else 0
            rows.append({'X':x,'A1':a1,'L1':l1,'A2':a2,'Y':y})
        return rows

    def test_qmc_hyperposterior_fitc_and_joint_design(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);self._gp(srv)
            hp=srv.call_tool('athena_gp_hyperqmc',{'context_key':'G13','samples':64,'seed':3})
            self.assertEqual(hp['status'],'QMC_CONTINUOUS_GP_HYPERPOSTERIOR_APPROXIMATION')
            self.assertGreaterEqual(hp['effective_sample_size'],1.0)
            self.assertGreaterEqual(len(hp['particles']),8)
            fitc=srv.call_tool('athena_gp_fitc_predict',{'context_key':'G13','features':{'x':.4},'inducing_count':4})
            self.assertEqual(fitc['status'],'FITC_INDUCING_GP_APPROXIMATION')
            self.assertEqual(fitc['inducing_count'],4)
            self.assertGreaterEqual(fitc['exact_reference']['absolute_mean_error'],0.0)
            design=srv.call_tool('athena_gp_joint_design',{'context_key':'G13','actions':[{'id':'left','features':{'x':-.9}},{'id':'right','features':{'x':.9}}],'experiments':[{'id':'center','features':{'x':0.0},'cost':.01},{'id':'edge','features':{'x':.75},'cost':.01}],'hyper_samples':48,'mc_samples':100,'seed':7,'cost_weight':0})
            self.assertEqual(design['decision'],'JOINT_HYPERMODEL_GP_DESIGN_ONLY')
            self.assertIn(design['winner'],{'center','edge'})
            self.assertTrue(all(r['model_information_gain_bits']>=0 for r in design['ranked']))
            srv.store.close()

    def test_fci_lite_keeps_partial_collider_geometry(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[]
            for i in range(360):
                x=((i*17)%101)/50.0-1.0;y=((i*43)%103)/51.0-1.0;noise=((i*29)%17-8)/700.0
                rows.append({'X':x,'Y':y,'Z':1.2*x-.95*y+noise})
            out=srv.call_tool('athena_fci_lite_discover',{'samples':rows,'variables':['X','Y','Z'],'alpha':.01,'max_conditioning':1})
            self.assertEqual(out['status'],'BOUNDED_FCI_LITE_CANDIDATE')
            self.assertTrue(any(c['middle']=='Z' for c in out['collider_candidates']))
            self.assertTrue(any(e['endpoint_a']=='arrowhead' or e['endpoint_b']=='arrowhead' for e in out['edges']))
            srv.store.close()

    def test_longitudinal_tmle_and_dynamic_policy_value(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=self._long_rows()
            tmle=srv.call_tool('athena_longitudinal_tmle',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X']})
            self.assertEqual(tmle['status'],'TWO_TIMEPOINT_SEQUENTIAL_LOGISTIC_TMLE_ESTIMATED_UNDER_ASSUMPTIONS')
            self.assertEqual(tmle['targeting_history'],'OBSERVED_A1_L1_RETAINED_FOR_STAGE2_PSEUDO_OUTCOME; A1_INTERVENTION_APPLIED_AT_STAGE1_EVALUATION')
            self.assertTrue(all(r['targeting_history']=='STAGE2_PRESERVES_OBSERVED_A1_L1_BEFORE_STAGE1_INTERVENTION' for r in tmle['regimes']))
            risks={(r['a1'],r['a2']):r['estimated_risk'] for r in tmle['regimes']}
            self.assertGreater(risks[(1,1)],risks[(0,0)])
            self.assertGreater(tmle['risk_contrast'],0)
            policies=[{'id':'never','a1':0,'a2':0},{'id':'always','a1':1,'a2':1},{'id':'adaptive','a1':1,'a2':{'coefficients':{'L1':2.0},'threshold':1.0}}]
            pv=srv.call_tool('athena_dynamic_policy_value',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'policies':policies})
            self.assertEqual(pv['status'],'DYNAMIC_TWO_TIMEPOINT_GFORMULA_POLICY_VALUE_UNDER_ASSUMPTIONS')
            vals={r['id']:r['estimated_value'] for r in pv['policies']}
            self.assertGreater(vals['always'],vals['never'])
            srv.store.close()

    def test_correlated_robust_resource_exact_certificate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            candidates=[
                {'id':'A','value':5,'resources':{'tokens':{'mean':3,'mean_uncertainty':.2}}},
                {'id':'B','value':4,'resources':{'tokens':{'mean':2,'mean_uncertainty':.2}}},
                {'id':'C','value':2,'resources':{'tokens':{'mean':1,'mean_uncertainty':.2}}},
            ]
            cov={'tokens':[[.04,.01,0],[.01,.04,.01],[0,.01,.04]]}
            out=srv.call_tool('athena_dro_resource_select',{'candidates':candidates,'budgets':{'tokens':6.5},'covariances':cov,'ambiguity_radius':.5,'alpha':.05})
            self.assertEqual(out['status'],'CORRELATED_GAUSSIAN_ELLIPSOIDAL_MEAN_ROBUST_EXACT_ENUMERATION')
            self.assertEqual(out['certificate'],'EXACT_ENUMERATION_UNDER_DECLARED_CORRELATED_GAUSSIAN_COVARIANCE_AND_ELLIPSOIDAL_MEAN_AMBIGUITY')
            self.assertEqual(set(out['selected']),{'A','B'})
            srv.store.close()

    def test_v13_tools_are_exposed(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for n in ('athena_gp_hyperqmc','athena_gp_fitc_predict','athena_gp_joint_design','athena_fci_lite_discover','athena_longitudinal_tmle','athena_dynamic_policy_value','athena_dro_resource_select'):
                self.assertIn(n,names)
            srv.store.close()


if __name__=='__main__':unittest.main()
