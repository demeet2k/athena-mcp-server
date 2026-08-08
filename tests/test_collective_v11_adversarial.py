import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV11AdversarialTests(unittest.TestCase):
    def test_gp_hyperfit_requires_cas_and_evsi_cannot_train(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_gp_register',{'context_key':'G','features':['x']})
            for x,y in [(0,0),(.5,.25),(1,1)]: srv.call_tool('athena_gp_observe',{'context_key':'G','features':{'x':x},'target':y})
            with self.assertRaises(ValueError):
                srv.call_tool('athena_gp_hyperfit',{'context_key':'G','apply':True})
            with self.assertRaises(ValueError):
                srv.call_tool('athena_gp_hyperfit',{'context_key':'G','apply':True,'expected_observation_count':2})
            before=srv.call_tool('athena_gp_state',{'context_key':'G'})['observation_count']
            for _ in range(4):
                srv.call_tool('athena_gp_decision_evsi',{'context_key':'G','actions':[{'id':'A','features':{'x':.2}},{'id':'B','features':{'x':.8}}],'experiments':[{'id':'E','features':{'x':.5}}],'samples':50})
            after=srv.call_tool('athena_gp_state',{'context_key':'G'})['observation_count']
            self.assertEqual(before,after)
            srv.store.close()

    def test_latent_projection_rejects_cycles_and_never_mutates_jspace(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            before=len(srv.store.rows('SELECT * FROM edges'))
            out=srv.call_tool('athena_latent_project_admg',{'edges':[{'src':'U','dst':'X'},{'src':'U','dst':'Y'}],'latent_nodes':['U']})
            self.assertEqual(out['status'],'RESTRICTED_LATENT_PROJECTION_ADMG')
            self.assertEqual(before,len(srv.store.rows('SELECT * FROM edges')))
            with self.assertRaises(ValueError):
                srv.call_tool('athena_latent_project_admg',{'edges':[{'src':'A','dst':'B'},{'src':'B','dst':'A'}],'latent_nodes':['A'],'observed_nodes':['B']})
            srv.store.close()

    def test_stacked_tmle_fails_closed_and_sensitivity_rejects_invalid_grid(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[{'T':i%2,'Y':(i//2)%2,'X':i/80} for i in range(80)]
            blocked=srv.call_tool('athena_causal_tmle_ensemble',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X'],'assumptions':{'latent_confounding_possible':True}})
            self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            bad=[{'T':i%2,'Y':.2+(i%3)*.1,'X':i/80} for i in range(80)]
            with self.assertRaises(ValueError):
                srv.call_tool('athena_causal_tmle_ensemble',{'samples':bad,'treatment':'T','outcome':'Y','adjustment':['X']})
            with self.assertRaises(ValueError):
                srv.call_tool('athena_sensitivity_rr_surface',{'observed_rr':2.0,'exposure_confounder_rrs':[.8],'outcome_confounder_rrs':[2.0]})
            srv.store.close()

    def test_bapomdp_requires_common_actions_and_certificate_drops_on_node_limit(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            m1={'id':'M1','prior':.5,'actions':[{'id':'A','reward_by_state':{'S':0},'transition':{'S':{'S':1}},'observation':{'S':{'x':1}}}]}
            m2={'id':'M2','prior':.5,'actions':[{'id':'B','reward_by_state':{'S':0},'transition':{'S':{'S':1}},'observation':{'S':{'x':1}}}]}
            with self.assertRaises(ValueError):
                srv.call_tool('athena_bapomdp_solve',{'states':['S'],'initial_state_belief':{'S':1},'models':[m1,m2]})
            states=['S0','S1']; models=[]
            for mi in range(4):
                acts=[]
                for ai in range(6):
                    acts.append({'id':f'A{ai}','reward_by_state':{s:0 for s in states},'transition':{s:{sp:(1.0 if s==sp else 0.0) for sp in states} for s in states},'observation':{s:{'o0':.5,'o1':.5} for s in states}})
                models.append({'id':f'M{mi}','prior':.25,'actions':acts})
            limited=srv.call_tool('athena_bapomdp_solve',{'states':states,'initial_state_belief':{'S0':.5,'S1':.5},'models':models,'horizon':3,'max_nodes':100})
            self.assertEqual(limited['status'],'NODE_LIMIT_NO_EXACT_CERTIFICATE')
            self.assertIsNone(limited['certificate'])
            srv.store.close()

    def test_dependence_interval_requires_fitted_complete_schema(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_evidence_dependence_interval',{'scope':'none','features':{'a':1}})
            for i in range(24): srv.call_tool('athena_evidence_dependence_observe',{'scope':'D','features':{'a':float(i%2),'b':float((i//2)%2)},'label':i%2})
            srv.call_tool('athena_evidence_dependence_fit',{'scope':'D'})
            with self.assertRaises(ValueError):
                srv.call_tool('athena_evidence_dependence_interval',{'scope':'D','features':{'a':1.0}})
            labels=srv.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels WHERE scope='D'")['n']
            for _ in range(5): srv.call_tool('athena_evidence_dependence_interval',{'scope':'D','features':{'a':1.0,'b':0.0}})
            labels2=srv.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels WHERE scope='D'")['n']
            self.assertEqual(labels,labels2)
            srv.store.close()


if __name__=='__main__': unittest.main()
