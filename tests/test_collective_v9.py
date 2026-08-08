import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV9Tests(unittest.TestCase):
    def test_gaussian_belief_update_evpi_evsi(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);st=srv.call_tool('athena_gaussian_belief_register',{'context_key':'G','parameters':['theta'],'mean':{'theta':0.0},'prior_variance':4.0,'noise_variance':.25});self.assertEqual(st['status'],'GAUSSIAN_LINEAR_BELIEF');self.assertAlmostEqual(st['mean']['theta'],0.0,places=6)
            post=srv.call_tool('athena_gaussian_belief_observe',{'context_key':'G','features':{'theta':1.0},'target':2.0});self.assertGreater(post['mean']['theta'],1.7)
            actions=[{'id':'plus','utility_linear':{'theta':1.0}},{'id':'minus','utility_linear':{'theta':-1.0}}];evpi=srv.call_tool('athena_decision_evpi',{'context_key':'G','actions':actions,'samples':300,'seed':4});self.assertEqual(evpi['status'],'MONTE_CARLO_EVPI_ESTIMATE');self.assertGreaterEqual(evpi['evpi'],0.0)
            srv.call_tool('athena_gaussian_belief_register',{'context_key':'G2','parameters':['theta'],'mean':{'theta':0.0},'prior_variance':4.0,'noise_variance':.25});evsi=srv.call_tool('athena_decision_evsi',{'context_key':'G2','actions':actions,'experiments':[{'id':'measure','design':{'theta':1.0},'noise_variance':.1}],'samples':300,'seed':5,'cost_weight':0,'risk_weight':0});self.assertEqual(evsi['decision'],'MONTE_CARLO_EVSI_DESIGN_ONLY');self.assertGreater(evsi['ranked'][0]['evsi'],0.1);srv.store.close()

    def test_multistage_belief_policy_is_read_only(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);srv.call_tool('athena_belief_register',{'context_key':'P9','models':[{'id':'M1','prior':.5},{'id':'M2','prior':.5}]});before=srv.call_tool('athena_belief_state',{'context_key':'P9'})
            actions=[{'id':'probe','utility_by_model':{'M1':.2,'M2':.2},'observation_model':{'yes':{'M1':.95,'M2':.05},'no':{'M1':.05,'M2':.95}}},{'id':'a1','utility_by_model':{'M1':1.0,'M2':0.0}},{'id':'a2','utility_by_model':{'M1':0.0,'M2':1.0}}]
            pol=srv.call_tool('athena_belief_policy_multistage',{'context_key':'P9','actions':actions,'horizon':2,'information_weight':.2});after=srv.call_tool('athena_belief_state',{'context_key':'P9'});self.assertEqual(pol['decision'],'FINITE_BELIEF_MULTISTAGE_POLICY_PLAN_ONLY');self.assertGreater(pol['expanded_nodes'],1);self.assertEqual(before['models'],after['models']);srv.store.close()

    def test_aipw_and_robustness(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[]
            for i in range(120):
                z=((i*13)%37)/36.0;t=1 if i%4 in (1,2) else 0;y=2.0*t+1.5*z+((i%5)-2)*.01;rows.append({'T':t,'Y':y,'Z':z})
            aipw=srv.call_tool('athena_causal_aipw',{'samples':rows,'treatment':'T','outcome':'Y','adjustment':['Z']});self.assertEqual(aipw['status'],'AIPW_CROSS_FIT_ESTIMATE');self.assertAlmostEqual(aipw['estimate'],2.0,delta=.25);self.assertGreater(aipw['standard_error'],0)
            rows2=[]
            for i in range(100):
                z=(i%20)/19.0;t=1 if (i%20)>=9 else 0;y=2*t+4*z+((i%3)-1)*.02;rows2.append({'T':t,'Y':y,'Z':z})
            rob=srv.call_tool('athena_causal_robustness',{'samples':rows2,'treatment':'T','outcome':'Y','adjustment':['Z']});self.assertEqual(rob['status'],'LEAVE_ONE_COVARIATE_ROBUSTNESS');self.assertGreater(rob['max_abs_shift'],.2);srv.store.close()

    def test_partial_graph_and_dependence_probability(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);rows=[{'X':i/40,'Y':2*i/40+((i%3)-1)*.01,'Z':((i*7)%13)/13} for i in range(40)];pg=srv.call_tool('athena_structure_partial',{'samples':rows,'variables':['X','Y','Z'],'association_threshold':.4,'resamples':20,'support_threshold':.6,'seed':2});self.assertEqual(pg['status'],'HEURISTIC_PARTIAL_GRAPH');self.assertTrue(any(set((e['a'],e['b']))=={'X','Y'} for e in pg['edges']));self.assertTrue(all(e['endpoint_a']=='o' and e['endpoint_b']=='o' for e in pg['edges']))
            claim=srv.call_tool('athena_discovery_claim_register',{'claim_key':'V9DEP','statement':'dep'})
            for k in ('r1','r2','r3'):srv.call_tool('athena_discovery_claim_witness',{'claim_id':claim['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':k,'evidence':{'dataset':'same','implementation':'same','method':'same'}})
            dep=srv.call_tool('athena_evidence_dependence_probability',{'claim_id':claim['claim_id'],'coefficients':{'bias':-1,'match':1.5,'different':-.5}});self.assertEqual(dep['status'],'DECLARED_METADATA_DEPENDENCE_MODEL');self.assertGreater(dep['mean_pair_dependence'],.9);srv.store.close()

    def test_v9_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_gaussian_belief_register','athena_decision_evpi','athena_decision_evsi','athena_belief_policy_multistage','athena_causal_aipw','athena_structure_partial','athena_evidence_dependence_probability'):self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
