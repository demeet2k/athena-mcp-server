import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV9AdversarialTests(unittest.TestCase):
    def test_continuous_design_calls_do_not_self_update(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_gaussian_belief_register',{'context_key':'GA','parameters':['theta'],'prior_variance':2.0,'noise_variance':.5});before=srv.call_tool('athena_gaussian_belief_state',{'context_key':'GA'});actions=[{'id':'p','utility_linear':{'theta':1}},{'id':'m','utility_linear':{'theta':-1}}]
            for _ in range(3):srv.call_tool('athena_decision_evpi',{'context_key':'GA','actions':actions,'samples':60,'seed':1});srv.call_tool('athena_decision_evsi',{'context_key':'GA','actions':actions,'experiments':[{'id':'e','design':{'theta':1},'noise_variance':.2}],'samples':60,'seed':1,'cost_weight':0,'risk_weight':0})
            after=srv.call_tool('athena_gaussian_belief_state',{'context_key':'GA'});self.assertEqual(before['observation_count'],after['observation_count']);self.assertEqual(before['mean'],after['mean']);self.assertEqual(before['covariance'],after['covariance']);srv.store.close()

    def test_incomplete_gaussian_observation_rejects(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_gaussian_belief_register',{'context_key':'GB','parameters':['x','z']})
            with self.assertRaises(ValueError):srv.call_tool('athena_gaussian_belief_observe',{'context_key':'GB','features':{'x':1},'target':2})
            st=srv.call_tool('athena_gaussian_belief_state',{'context_key':'GB'});self.assertEqual(st['observation_count'],0);srv.store.close()

    def test_aipw_fails_closed_for_confounding_and_nonbinary_treatment(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[{'T':i%2,'Y':2*(i%2)+.1*i,'Z':i/30} for i in range(30)];blocked=srv.call_tool('athena_causal_aipw',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['Z'],'assumptions':{'latent_confounding_possible':True}});self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')
            bad=[{'T':i/30,'Y':i/10,'Z':i/30} for i in range(30)]
            with self.assertRaises(ValueError):srv.call_tool('athena_causal_aipw',{'samples':bad,'treatment':'T','outcome':'Y','adjustment':['Z']})
            srv.store.close()

    def test_multistage_incomplete_likelihood_rejects_without_belief_change(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_belief_register',{'context_key':'BP','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]});before=srv.call_tool('athena_belief_state',{'context_key':'BP'})
            with self.assertRaises(ValueError):srv.call_tool('athena_belief_policy_multistage',{'context_key':'BP','actions':[{'id':'bad','utility':.5,'observation_model':{'yes':{'M1':.9}}}],'horizon':2})
            after=srv.call_tool('athena_belief_state',{'context_key':'BP'});self.assertEqual(before['models'],after['models']);srv.store.close()

    def test_partial_graph_does_not_mutate_jspace(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);before=len(srv.core.s.rows('SELECT * FROM edges'));rows=[{'X':i/35,'Y':2*i/35+((i%3)-1)*.01,'Z':((i*11)%17)/17} for i in range(35)];pg=srv.call_tool('athena_structure_partial',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.4,'resamples':10,'support_threshold':.5,'seed':4});after=len(srv.core.s.rows('SELECT * FROM edges'));self.assertEqual(pg['status'],'HEURISTIC_PARTIAL_GRAPH');self.assertEqual(before,after);srv.store.close()

    def test_missing_metadata_does_not_imply_independence(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);claim=srv.call_tool('athena_discovery_claim_register',{'claim_key':'V9MISS','statement':'missing'})
            for k in ('a','b'):srv.call_tool('athena_discovery_claim_witness',{'claim_id':claim['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k,'evidence':{}})
            dep=srv.call_tool('athena_evidence_dependence_probability',{'claim_id':claim['claim_id']});self.assertEqual(len(dep['pairwise']),1);self.assertGreater(dep['pairwise'][0]['p_dependence'],.5);srv.store.close()


if __name__=='__main__': unittest.main()
