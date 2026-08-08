import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV12AdversarialTests(unittest.TestCase):
    def _gp(self,srv):
        srv.call_tool('athena_gp_register',{'context_key':'G','features':['x'],'length_scale':1.0,'signal_variance':1.0,'noise_variance':.05})
        for i,x in enumerate((-.8,-.2,.3,.9)):
            srv.call_tool('athena_gp_observe',{'context_key':'G','features':{'x':x},'target':x*x,'evidence_ref':f'test://{i}'})

    def test_hyperposterior_bma_sparse_and_evsi_are_read_only(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._gp(srv)
            before=srv.call_tool('athena_gp_state',{'context_key':'G'})
            srv.call_tool('athena_gp_hyperposterior',{'context_key':'G'})
            srv.call_tool('athena_gp_bma_predict',{'context_key':'G','features':{'x':.4}})
            srv.call_tool('athena_gp_sparse_predict',{'context_key':'G','features':{'x':.4},'inducing_count':2})
            srv.call_tool('athena_gp_bma_decision_evsi',{'context_key':'G','actions':[{'id':'a','features':{'x':-.5}},{'id':'b','features':{'x':.5}}],'experiments':[{'id':'e','features':{'x':0.0}}],'samples':50})
            after=srv.call_tool('athena_gp_state',{'context_key':'G'})
            self.assertEqual(before['observation_count'],after['observation_count'])
            self.assertEqual(before['length_scale'],after['length_scale'])
            self.assertEqual(before['signal_variance'],after['signal_variance'])
            self.assertEqual(before['noise_variance'],after['noise_variance'])
            srv.store.close()

    def test_invalid_hyperposterior_prior_rejects(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._gp(srv)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_gp_hyperposterior',{'context_key':'G','candidates':[{'length_scale':1,'signal_variance':1,'noise_variance':.1,'prior':0}]})
            srv.store.close()

    def test_pag_candidate_cannot_mutate_jspace(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rows=[]
            for i in range(80): rows.append({'X':i/80,'Y':((i*17)%79)/79,'Z':((i*31)%83)/83})
            before=len(srv.store.rows('SELECT * FROM edges'))
            srv.call_tool('athena_pag_candidate_discover',{'samples':rows,'variables':['X','Y','Z'],'max_conditioning':1})
            after=len(srv.store.rows('SELECT * FROM edges'))
            self.assertEqual(before,after)
            srv.store.close()

    def test_longitudinal_gformula_fails_closed_and_nonbinary_rejects(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); rows=[]
            for i in range(100): rows.append({'A1':i%2,'L1':(i//2)%2,'A2':(i//3)%2,'Y':(i//5)%2})
            blocked=srv.call_tool('athena_longitudinal_gformula',{'samples':rows,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y','assumptions':{'latent_confounding_possible':True}})
            self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            bad=[dict(r,Y=.25) for r in rows]
            with self.assertRaises(ValueError):
                srv.call_tool('athena_longitudinal_gformula',{'samples':bad,'treatment1':'A1','intermediate':'L1','treatment2':'A2','outcome':'Y'})
            srv.store.close()

    def test_chance_constraint_requires_complete_resources_and_large_n_loses_certificate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_chance_resource_select',{'candidates':[{'id':'A','value':1,'resources':{}}],'budgets':{'tokens':10}})
            items=[{'id':f'C{i}','value':1+i/100,'resources':{'tokens':{'mean':.2,'std':.01}}} for i in range(19)]
            out=srv.call_tool('athena_chance_resource_select',{'candidates':items,'budgets':{'tokens':2.5},'exact_limit':18})
            self.assertEqual(out['status'],'CHANCE_CONSTRAINED_GREEDY_NO_OPTIMALITY_CERTIFICATE')
            self.assertIsNone(out['certificate'])
            srv.store.close()


if __name__=='__main__': unittest.main()
