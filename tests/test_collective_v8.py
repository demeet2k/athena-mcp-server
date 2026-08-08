import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV8Tests(unittest.TestCase):
    def _register(self,srv,key='B'):
        return srv.call_tool('athena_belief_register',{'context_key':key,'models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]})

    def test_belief_update_and_evi(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._register(srv)
            prior=srv.call_tool('athena_belief_state',{'context_key':'B'})
            self.assertAlmostEqual(sum(m['probability'] for m in prior['models']),1.0)
            post=srv.call_tool('athena_belief_observe',{'context_key':'B','outcome':'positive','likelihoods':{'M1':.9,'M2':.1}})
            probs={m['id']:m['probability'] for m in post['models']}
            self.assertGreater(probs['M1'],.8)
            actions=[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}]
            experiments=[
                {'id':'weak','outcomes':{'yes':{'M1':.55,'M2':.45},'no':{'M1':.45,'M2':.55}}},
                {'id':'strong','outcomes':{'yes':{'M1':.95,'M2':.05},'no':{'M1':.05,'M2':.95}}},
            ]
            evi=srv.call_tool('athena_decision_evi',{'context_key':'B','actions':actions,'experiments':experiments})
            strong=next(x for x in evi['ranked'] if x['id']=='strong')
            weak=next(x for x in evi['ranked'] if x['id']=='weak')
            self.assertGreaterEqual(strong['evi'],weak['evi'])
            srv.store.close()

    def test_belief_dual_control_prefers_information_when_valuable(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); self._register(srv,'D')
            actions=[
                {'id':'exploit','utility_by_model':{'M1':.7,'M2':.7},'observation_model':{'x':{'M1':.5,'M2':.5}}},
                {'id':'probe','utility_by_model':{'M1':.58,'M2':.58},'observation_model':{'x':{'M1':.95,'M2':.05},'y':{'M1':.05,'M2':.95}}},
            ]
            out=srv.call_tool('athena_belief_dual_control',{'context_key':'D','actions':actions,'information_weight':1.0,'risk_weight':0})
            self.assertEqual(out['decision'],'BELIEF_DUAL_CONTROL_DEPTH1_PLAN_ONLY')
            self.assertEqual(out['selected'],'probe')
            srv.store.close()

    def test_causal_effect_estimators(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[]
            for i in range(40):
                z=(i%5)/4; t=1 if i%2 else 0; y=2*t+3*z
                rows.append({'T':t,'Y':y,'Z':z})
            bd=srv.call_tool('athena_causal_effect_estimate',{'method':'BACKDOOR_LINEAR','samples':rows,'treatment':'T','outcome':'Y','adjustment':['Z']})
            self.assertAlmostEqual(bd['estimate'],2.0,places=4)
            weak=[{'Z':0,'T':i%2,'Y':i%3} for i in range(20)]
            iv=srv.call_tool('athena_causal_effect_estimate',{'method':'IV_WALD','samples':weak,'treatment':'T','outcome':'Y','instrument':'Z'})
            self.assertEqual(iv['status'],'WEAK_OR_INVALID_INSTRUMENT')
            srv.store.close()

    def test_bootstrap_structure_and_contingent_policy_nonmutation(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            rows=[{'X':i/30,'Y':2*i/30 + ((i%3)-1)*.01,'Z':((i*7)%11)/11} for i in range(30)]
            out=srv.call_tool('athena_causal_structure_bootstrap',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.4,'resamples':20,'support_threshold':.6,'seed':3})
            self.assertEqual(out['status'],'BOOTSTRAP_ASSOCIATION_STABILITY')
            self.assertTrue(any(set((e['a'],e['b']))=={'X','Y'} for e in out['stable_edges']))
            self._register(srv,'P')
            before=srv.call_tool('athena_belief_state',{'context_key':'P'})
            pol=srv.call_tool('athena_contingent_policy',{'context_key':'P','actions':[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}], 'experiment':{'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}})
            after=srv.call_tool('athena_belief_state',{'context_key':'P'})
            self.assertEqual(pol['decision'],'CONTINGENT_POLICY_DEPTH1_DESIGN_ONLY')
            self.assertEqual(before['models'],after['models'])
            srv.store.close()

    def test_spectral_replication_diversity_and_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            claim=srv.call_tool('athena_claim_register',{'claim_key':'V8C','statement':'test'})
            for k in ('r1','r2','r3'):
                srv.call_tool('athena_claim_witness',{'claim_id':claim['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k,'evidence':{'dataset':'same','implementation':'same','method':'same'}})
            sp=srv.call_tool('athena_evidence_spectral',{'claim_id':claim['claim_id']})
            self.assertAlmostEqual(sp['effective_n'],1.0,places=6)
            self.assertAlmostEqual(sp['spectral_participation_ratio'],1.0,places=6)
            names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_belief_state','athena_decision_evi','athena_causal_effect_estimate','athena_evidence_spectral'):
                self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
