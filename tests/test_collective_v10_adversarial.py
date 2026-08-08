import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV10AdversarialTests(unittest.TestCase):
    def test_gp_prediction_cannot_train_itself_and_missing_feature_rejects(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            srv.call_tool('athena_gp_register',{'context_key':'G','features':['x','z']})
            for _ in range(5):
                srv.call_tool('athena_gp_predict',{'context_key':'G','features':{'x':0.2,'z':0.7}})
            st=srv.call_tool('athena_gp_state',{'context_key':'G'})
            self.assertEqual(st['observation_count'],0)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_gp_observe',{'context_key':'G','features':{'x':1.0},'target':1.0})
            srv.store.close()

    def test_pc_and_partial_graph_do_not_mutate_jspace(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[{'X':i/50,'Y':2*i/50,'Z':((i*17)%23)/23} for i in range(50)]
            before=len(srv.store.rows('SELECT * FROM edges'))
            out=srv.call_tool('athena_pc_stable_discover',{'samples':rows,'variables':['X','Y','Z'],'alpha':.05,'max_conditioning':1})
            after=len(srv.store.rows('SELECT * FROM edges'))
            self.assertEqual(out['status'],'PC_STABLE_BOUNDED_PARTIAL_GRAPH')
            self.assertEqual(before,after)
            srv.store.close()

    def test_tmle_fails_closed_on_latent_confounding_and_nonbinary_outcome(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[{'T':i%2,'Y':(i//2)%2,'X':i/50} for i in range(80)]
            blocked=srv.call_tool('athena_causal_tmle_binary',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['X'],'assumptions':{'latent_confounding_possible':True}})
            self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            bad=[{'T':i%2,'Y':0.25+(i%3)*.1,'X':i/50} for i in range(80)]
            with self.assertRaises(ValueError):
                srv.call_tool('athena_causal_tmle_binary',{'samples':bad,'treatment':'T','outcome':'Y','adjustment':['X']})
            srv.store.close()

    def test_evalue_invalid_and_pomdp_certificate_requires_complete_search_model(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_sensitivity_evalue',{'risk_ratio':0})
            bad_actions=[{'id':'bad','reward_by_state':{'A':1,'B':0},
                          'transition':{'A':{'A':.8,'B':.3},'B':{'A':0,'B':1}},
                          'observation':{'A':{'x':1},'B':{'x':1}}}]
            with self.assertRaises(ValueError):
                srv.call_tool('athena_pomdp_solve',{'states':['A','B'],'initial_belief':{'A':.5,'B':.5},'actions':bad_actions,'horizon':2})
            many=[]
            states=['S0','S1','S2']
            for j in range(5):
                many.append({'id':f'A{j}','reward_by_state':{s:0 for s in states},
                             'transition':{s:{sp:(1.0 if s==sp else 0.0) for sp in states} for s in states},
                             'observation':{s:{'o0':1/3,'o1':1/3,'o2':1/3} for s in states}})
            limited=srv.call_tool('athena_pomdp_solve',{'states':states,'initial_belief':{s:1/3 for s in states},'actions':many,'horizon':4,'max_nodes':100})
            self.assertEqual(limited['status'],'NODE_LIMIT_NO_EXACT_CERTIFICATE')
            self.assertIsNone(limited['selected'])
            srv.store.close()

    def test_dependence_predictions_require_external_labels_and_complete_schema(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            with self.assertRaises(ValueError):
                srv.call_tool('athena_evidence_dependence_fit',{'scope':'D'})
            for i in range(20):
                srv.call_tool('athena_evidence_dependence_observe',{'scope':'D','features':{'a':float(i%2),'b':float((i//2)%2)},'label':i%2})
            srv.call_tool('athena_evidence_dependence_fit',{'scope':'D'})
            with self.assertRaises(ValueError):
                srv.call_tool('athena_evidence_dependence_predict',{'scope':'D','features':{'a':1.0}})
            count=srv.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels WHERE scope='D'")['n']
            for _ in range(5):
                srv.call_tool('athena_evidence_dependence_predict',{'scope':'D','features':{'a':1.0,'b':0.0}})
            count2=srv.store.one("SELECT COUNT(*) AS n FROM collective_v10_dependence_labels WHERE scope='D'")['n']
            self.assertEqual(count,count2)
            srv.store.close()


if __name__=='__main__': unittest.main()
