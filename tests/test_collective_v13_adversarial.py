import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV13AdversarialTests(unittest.TestCase):
    def _gp(self,srv):
        srv.call_tool('athena_gp_register',{'context_key':'G','features':['x'],'length_scale':1.0,'signal_variance':1.0,'noise_variance':.05})
        for i,x in enumerate((-.9,-.6,-.3,0,.3,.6,.9)):
            srv.call_tool('athena_gp_observe',{'context_key':'G','features':{'x':x},'target':x*x,'evidence_ref':f'test://{i}'})

    def test_qmc_fitc_and_joint_design_are_read_only(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);self._gp(srv);before=srv.call_tool('athena_gp_state',{'context_key':'G'})
            srv.call_tool('athena_gp_hyperqmc',{'context_key':'G','samples':48})
            srv.call_tool('athena_gp_fitc_predict',{'context_key':'G','features':{'x':.4},'inducing_count':3})
            srv.call_tool('athena_gp_joint_design',{'context_key':'G','actions':[{'id':'a','features':{'x':-.5}},{'id':'b','features':{'x':.5}}],'experiments':[{'id':'e','features':{'x':0}}],'hyper_samples':40,'mc_samples':80})
            after=srv.call_tool('athena_gp_state',{'context_key':'G'})
            self.assertEqual(before['observation_count'],after['observation_count']);self.assertEqual(before['length_scale'],after['length_scale']);self.assertEqual(before['signal_variance'],after['signal_variance']);self.assertEqual(before['noise_variance'],after['noise_variance'])
            srv.store.close()

    def test_hyperqmc_rejects_invalid_continuous_box(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);self._gp(srv)
            with self.assertRaises(ValueError):srv.call_tool('athena_gp_hyperqmc',{'context_key':'G','bounds':{'length_scale':[2,1]}})
            srv.store.close()

    def test_fci_lite_never_mutates_jspace(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[]
            for i in range(100):rows.append({'X':i/100,'Y':((i*17)%97)/97,'Z':((i*31)%101)/101})
            before=len(srv.store.rows('SELECT * FROM edges'));srv.call_tool('athena_fci_lite_discover',{'samples':rows,'variables':['X','Y','Z'],'max_conditioning':1});after=len(srv.store.rows('SELECT * FROM edges'));self.assertEqual(before,after);srv.store.close()

    def test_longitudinal_methods_fail_closed_on_declared_latent_confounding(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[]
            for i in range(120):rows.append({'X':i/120,'A1':i%2,'L1':(i//2)%2,'A2':(i//3)%2,'Y':(i//5)%2})
            args={'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','baseline':['X'],'assumptions':{'latent_confounding_possible':True}}
            blocked=srv.call_tool('athena_longitudinal_tmle',args);self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            blocked2=srv.call_tool('athena_dynamic_policy_value',{**args,'policies':[{'id':'p','a1':1,'a2':1}]});self.assertEqual(blocked2['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            srv.store.close()

    def test_robust_resource_rejects_invalid_covariance_and_large_n_loses_certificate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);items=[{'id':'A','value':1,'resources':{'tokens':{'mean':1}}},{'id':'B','value':1,'resources':{'tokens':{'mean':1}}}]
            with self.assertRaises(ValueError):srv.call_tool('athena_dro_resource_select',{'candidates':items,'budgets':{'tokens':4},'covariances':{'tokens':[[1,2],[0,1]]}})
            many=[{'id':f'C{i}','value':1+i/100,'resources':{'tokens':{'mean':.2,'mean_uncertainty':.01}}} for i in range(19)];cov=[[.0001 if i==j else 0 for j in range(19)] for i in range(19)]
            out=srv.call_tool('athena_dro_resource_select',{'candidates':many,'budgets':{'tokens':2.5},'covariances':{'tokens':cov},'ambiguity_radius':1,'exact_limit':18})
            self.assertEqual(out['status'],'CORRELATED_GAUSSIAN_ROBUST_GREEDY_NO_OPTIMALITY_CERTIFICATE');self.assertIsNone(out['certificate']);srv.store.close()


if __name__=='__main__':unittest.main()
