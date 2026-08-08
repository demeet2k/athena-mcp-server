import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV8AdversarialTests(unittest.TestCase):
    def test_prediction_design_does_not_update_belief(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_belief_register',{'context_key':'B','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]});before=srv.call_tool('athena_belief_state',{'context_key':'B'})
            actions=[{'id':'A','utility_by_model':{'M1':1,'M2':0}},{'id':'B','utility_by_model':{'M1':0,'M2':1}}]; exp={'id':'E','outcomes':{'yes':{'M1':.9,'M2':.1},'no':{'M1':.1,'M2':.9}}}
            for _ in range(3):
                srv.call_tool('athena_decision_evi',{'context_key':'B','actions':actions,'experiments':[exp]});srv.call_tool('athena_contingent_policy',{'context_key':'B','actions':actions,'experiment':exp});srv.call_tool('athena_belief_dual_control',{'context_key':'B','actions':[dict(actions[0],observation_model=exp['outcomes']),dict(actions[1],observation_model=exp['outcomes'])]})
            after=srv.call_tool('athena_belief_state',{'context_key':'B'});self.assertEqual(before['models'],after['models']);srv.store.close()

    def test_incomplete_likelihoods_and_ethics_fail_closed(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_belief_register',{'context_key':'B','models':[{'id':'M1'},{'id':'M2'}]})
            with self.assertRaises(ValueError):srv.call_tool('athena_belief_observe',{'context_key':'B','outcome':'x','likelihoods':{'M1':.9}})
            actions=[{'id':'A1','utility_by_model':{'M1':1,'M2':0}},{'id':'A2','utility_by_model':{'M1':0,'M2':1}}];out=srv.call_tool('athena_decision_evi',{'context_key':'B','actions':actions,'experiments':[{'id':'blocked','ethical':False,'outcomes':{'yes':{'M1':1,'M2':0},'no':{'M1':0,'M2':1}}}]});self.assertIsNone(out['winner']);self.assertEqual(out['ranked'][0]['status'],'ETHICS_BLOCK');srv.store.close()

    def test_latent_confounding_blocks_effect_estimate(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[{'T':i%2,'Y':i%2 + .1*i,'Z':i/20} for i in range(20)];out=srv.call_tool('athena_causal_effect_estimate',{'method':'BACKDOOR_LINEAR','samples':rows,'treatment':'T','outcome':'Y','adjustment':['Z'],'assumptions':{'latent_confounding_possible':True}});self.assertEqual(out['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK');self.assertIsNone(out['estimate']);srv.store.close()

    def test_bootstrap_does_not_create_canonical_edges(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);before=srv.store.one('SELECT COUNT(*) AS n FROM edges')['n'];rows=[{'X':i/20,'Y':i/20,'Z':(i%4)/4} for i in range(20)];srv.call_tool('athena_causal_structure_bootstrap',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.3,'resamples':10});after=srv.store.one('SELECT COUNT(*) AS n FROM edges')['n'];self.assertEqual(before,after);srv.store.close()

    def test_missing_replication_metadata_is_not_independence(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);c=srv.call_tool('athena_discovery_claim_register',{'claim_key':'EMPTYMETA','statement':'x'})
            for k in ('a','b'):srv.call_tool('athena_discovery_claim_witness',{'claim_id':c['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k,'evidence':{}})
            out=srv.call_tool('athena_evidence_spectral',{'claim_id':c['claim_id']});self.assertLess(out['effective_n'],2.0);self.assertLess(out['spectral_participation_ratio'],2.0);srv.store.close()


if __name__=='__main__': unittest.main()
