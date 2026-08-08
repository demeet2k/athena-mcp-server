import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveRuntimeV7Tests(unittest.TestCase):
    def test_uncertainty_decomposition_and_prequential_band(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name); regime='REGIME/V7'
            for i in range(12):
                x=(i-6)/10
                srv.call_tool('athena_nonlinear_observe',{'features':{'x':x},'reward':min(1.0,max(0.0,.2+x*x)),'regime':regime,'arm_id':'A'})
            dec=srv.call_tool('athena_uncertainty_decompose',{'features':{'x':.15},'regime':regime,'arm_id':'A'})
            self.assertIn('epistemic_parameter_proxy',dec['components']);self.assertGreaterEqual(dec['total_proxy_sigma'],0)
            band=srv.call_tool('athena_prequential_interval',{'features':{'x':.15},'regime':regime,'arm_id':'A','min_scores':5})
            self.assertEqual(band['status'],'EMPIRICAL_PREQUENTIAL_BAND');self.assertLessEqual(band['lower'],band['upper']);srv.store.close()

    def test_association_skeleton_is_hypothesis_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);samples=[]
            for i in range(20):
                x=(i-10)/10;samples.append({'x':x,'y':2*x + (0.01 if i%2 else -0.01),'z':(-1 if i%2 else 1)})
            out=srv.call_tool('athena_causal_skeleton_discover',{'samples':samples,'association_threshold':.2})
            self.assertEqual(out['status'],'HEURISTIC_ASSOCIATION_SKELETON');self.assertIn({'a':'x','b':'y'},out['undirected_edges']);self.assertIn('not a causal DAG',out['law']);srv.store.close()

    def test_state_dependent_transition_scenario_and_dual_control(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            transitions=[({'progress':0.0,'risk':.6},{'progress':.15,'risk':.54}),({'progress':.2,'risk':.5},{'progress':.38,'risk':.43}),({'progress':.4,'risk':.4},{'progress':.62,'risk':.33}),({'progress':.6,'risk':.3},{'progress':.86,'risk':.22})]
            for before,after in transitions:srv.call_tool('athena_transition_observe',{'action_id':'A','before':before,'after':after})
            model=srv.call_tool('athena_state_transition_model',{'action_id':'A','context':{'progress':.5,'risk':.35}});self.assertEqual(model['status'],'STATE_DEPENDENT_MODEL');self.assertIn('progress',model['mean_delta']);self.assertGreaterEqual(model['parameter_information_gain_nats'],0)
            scen=srv.call_tool('athena_scenario_evaluate',{'initial_context':{'progress':.5,'risk':.35},'actions':[{'id':'A','base_reward':.7,'reward_weights':{'progress':.1}},{'id':'B','base_reward':.55}],'trajectories':[{'id':'AA','actions':['A','A']},{'id':'AB','actions':['A','B']}]});self.assertEqual(scen['decision'],'SIMULATE_ONLY');self.assertTrue(scen['ranked'])
            before_n=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n'];plan=srv.call_tool('athena_dual_control_plan',{'initial_context':{'progress':.5,'risk':.35},'actions':[{'id':'A','base_reward':.7},{'id':'UNSEEN','base_reward':.45,'unseen_information_prior':1.2,'unseen_risk_prior':.9}],'horizon':2,'information_weight':.3});self.assertEqual(plan['decision'],'DUAL_CONTROL_PROXY_PLAN_ONLY');self.assertIsNotNone(plan['first_action']);after_n=srv.store.one("SELECT COUNT(*) AS n FROM collective_v5_transition_observations")['n'];self.assertEqual(before_n,after_n);srv.store.close()

    def test_frontdoor_and_instrument_identification(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            fd=srv.call_tool('athena_causal_identify_extended',{'method':'FRONTDOOR','treatment':'T','outcome':'Y','mediators':['M'],'edges':[{'src':'T','dst':'M'},{'src':'M','dst':'Y'}],'observed_nodes':['T','M','Y']});self.assertEqual(fd['status'],'IDENTIFIED_FRONTDOOR_UNDER_DAG')
            iv=srv.call_tool('athena_causal_identify_extended',{'method':'INSTRUMENT','treatment':'T','outcome':'Y','instruments':['Z'],'edges':[{'src':'Z','dst':'T'},{'src':'T','dst':'Y'}],'observed_nodes':['Z','T','Y']});self.assertEqual(iv['status'],'IDENTIFIED_INSTRUMENT_UNDER_DAG');self.assertIn('Z',iv['witness']['valid_instruments']);srv.store.close()

    def test_replication_independence_and_design(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);claim=srv.call_tool('athena_discovery_claim_register',{'claim_key':'V7C','statement':'intervention improves outcome'});cid=claim['claim_id']
            srv.call_tool('athena_discovery_claim_witness',{'claim_id':cid,'kind':'REPLICATION','result':'SUPPORTS','independence_key':'r1','confidence':.9,'evidence':{'dataset':'D1','implementation':'I1','method':'M1','environment':'E1','seed_family':'S1'}})
            srv.call_tool('athena_discovery_claim_witness',{'claim_id':cid,'kind':'REPLICATION','result':'SUPPORTS','independence_key':'r2','confidence':.9,'evidence':{'dataset':'D2','implementation':'I2','method':'M1','environment':'E2','seed_family':'S2'}})
            ind=srv.call_tool('athena_replication_independence',{'claim_id':cid});self.assertGreater(ind['support']['effective_n'],1.0)
            design=srv.call_tool('athena_replication_design',{'claim_id':cid,'candidates':[{'id':'same','expected_power':.9,'evidence':{'dataset':'D1','implementation':'I1','method':'M1','environment':'E1','seed_family':'S1'}},{'id':'novel','expected_power':.9,'evidence':{'dataset':'D3','implementation':'I3','method':'M2','environment':'E3','seed_family':'S3'}}]});self.assertEqual(design['decision'],'DESIGN_ONLY');self.assertEqual(design['selected'],'novel');srv.store.close()

    def test_v7_tool_surface(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name);names={x['name'] for x in srv.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
            for name in ('athena_uncertainty_decompose','athena_causal_skeleton_discover','athena_state_transition_model','athena_dual_control_plan','athena_causal_identify_extended','athena_replication_independence'):self.assertIn(name,names)
            srv.store.close()


if __name__=='__main__': unittest.main()
