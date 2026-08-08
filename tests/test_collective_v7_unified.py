import json
import tempfile
import unittest

from athena_mcp.server import Server


class CollectiveV7UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.NamedTemporaryFile(suffix='.db');self.server=Server(self.tmp.name);self.seq=0
    def tearDown(self):self.server.store.close();self.tmp.close()
    def rpc(self,method,params=None):
        self.seq+=1;m={'jsonrpc':'2.0','id':self.seq,'method':method}
        if params is not None:m['params']=params
        return self.server.handle(m)
    def tool(self,name,args):
        r=self.rpc('tools/call',{'name':name,'arguments':args});result=r['result'];self.assertFalse(result.get('isError'),r);return result['structuredContent']

    def test_v7_tools_resource_and_surface_are_advertised(self):
        names={t['name'] for t in self.rpc('tools/list')['result']['tools']}
        for name in ['athena_uncertainty_decompose','athena_prequential_interval','athena_causal_skeleton_discover','athena_state_transition_model','athena_scenario_evaluate','athena_dual_control_plan','athena_causal_identify_extended','athena_replication_independence','athena_replication_design']:
            self.assertIn(name,names)
        uris={r['uri'] for r in self.rpc('resources/list')['result']['resources']};self.assertIn('athena://collective/v7',uris)
        payload=json.loads(self.rpc('resources/read',{'uri':'athena://collective/v7'})['result']['contents'][0]['text']);self.assertEqual(payload['runtime']['version'],'COLLECTIVE_RUNTIME_V7');self.assertIn('plans/simulations are not execution',payload['boundary'])
        audit=self.tool('athena_surface_audit',{'run_probes':True});self.assertEqual(audit['groups']['collective_v7']['status'],'PASS',audit)

    def test_uncertainty_and_prequential_outputs_are_diagnostic_not_certainty(self):
        dec=self.tool('athena_uncertainty_decompose',{'features':{'x':.25},'regime':'R','arm_id':'A'})
        self.assertIn('aleatoric_noise_proxy',dec['components']);self.assertIn('epistemic_parameter_proxy',dec['components']);self.assertIn('diagnostic model-conditional proxies',dec['law'])
        band=self.tool('athena_prequential_interval',{'features':{'x':.25},'regime':'R','arm_id':'A','min_scores':8})
        self.assertEqual(band['status'],'INSUFFICIENT_PREQUENTIAL_SCORES');self.assertIn('without a conformal-style coverage claim',band['law'])

    def test_causal_skeleton_is_explicit_hypothesis_generation(self):
        samples=[{'x':float(i),'y':float(2*i+1),'z':float((-1)**i)} for i in range(1,8)]
        out=self.tool('athena_causal_skeleton_discover',{'samples':samples,'association_threshold':.2})
        self.assertEqual(out['status'],'HEURISTIC_ASSOCIATION_SKELETON');self.assertTrue(any({e['a'],e['b']}=={'x','y'} for e in out['undirected_edges']));self.assertIn('not a causal DAG',out['law'])

    def test_transition_scenario_and_dual_control_do_not_self_train(self):
        unseen=self.tool('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}});self.assertEqual(unseen['status'],'UNSEEN_ACTION')
        actions=[{'id':'A','base_reward':.4},{'id':'B','base_reward':.6}]
        scenario=self.tool('athena_scenario_evaluate',{'initial_context':{'x':0.0},'actions':actions,'trajectories':[{'id':'AB','actions':['A','B']} ]})
        self.assertEqual(scenario['decision'],'SIMULATE_ONLY');self.assertIn('not observed futures',scenario['law'])
        plan=self.tool('athena_dual_control_plan',{'initial_context':{'x':0.0},'actions':actions,'horizon':2})
        self.assertEqual(plan['decision'],'DUAL_CONTROL_PROXY_PLAN_ONLY');self.assertIn(plan['first_action'],{'A','B'});self.assertIn('observe reality, and replan',plan['law'])
        after=self.tool('athena_state_transition_model',{'action_id':'A','context':{'x':0.0}});self.assertEqual(after['status'],'UNSEEN_ACTION')

    def test_extended_frontdoor_is_conditional_on_supplied_dag(self):
        edges=[{'src':'T','dst':'M'},{'src':'M','dst':'Y'}]
        out=self.tool('athena_causal_identify_extended',{'method':'FRONTDOOR','treatment':'T','outcome':'Y','edges':edges,'observed_nodes':['T','M','Y'],'mediators':['M']})
        self.assertEqual(out['status'],'IDENTIFIED_FRONTDOOR_UNDER_DAG');self.assertTrue(out['analysis_id'].startswith('V7ID:'));self.assertIn('conditional on the supplied DAG',out['law'])
        blocked=self.tool('athena_causal_identify_extended',{'method':'FRONTDOOR','treatment':'T','outcome':'Y','edges':edges,'observed_nodes':['T','M','Y'],'mediators':['M'],'assumptions':{'latent_confounding_possible':True}})
        self.assertEqual(blocked['status'],'UNIDENTIFIED_LATENT_CONFOUNDING_RISK')

    def test_replication_geometry_operates_only_on_discovery_shadow_claims(self):
        self.tool('athena_claim_register',{'claim_id':'CLAIM.Y1.V7','source_ref':'source://canonical'})
        shadow=self.tool('athena_discovery_claim_register',{'claim_key':'shadow:v7','statement':'replication target'})
        self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':'lab:A','confidence':.9,'evidence':{'dataset':'D1','implementation':'I1','method':'M1','operator':'O1','environment':'E1','seed_family':'S1'}})
        self.tool('athena_discovery_claim_witness',{'claim_id':shadow['claim_id'],'kind':'REPLICATION','result':'SUPPORTS','independence_key':'lab:B','confidence':.9,'evidence':{'dataset':'D2','implementation':'I2','method':'M2','operator':'O2','environment':'E2','seed_family':'S2'}})
        indep=self.tool('athena_replication_independence',{'claim_id':shadow['claim_id']});self.assertEqual(indep['raw_witness_count'],2);self.assertGreater(indep['support']['effective_n'],1.0);self.assertIn('not constitute formal statistical independence proof',indep['law'])
        design=self.tool('athena_replication_design',{'claim_id':shadow['claim_id'],'candidates':[{'id':'same','expected_power':.8,'feasibility':1,'evidence':{'dataset':'D1','implementation':'I1','method':'M1','operator':'O1','environment':'E1','seed_family':'S1'}},{'id':'novel','expected_power':.8,'feasibility':1,'evidence':{'dataset':'D3','implementation':'I3','method':'M3','operator':'O3','environment':'E3','seed_family':'S3'}}]})
        self.assertEqual(design['decision'],'DESIGN_ONLY');self.assertEqual(design['selected'],'novel');self.assertIn('not a replication/falsification result',design['law'])
        y1=self.tool('athena_claim_state',{'claim_id':'CLAIM.Y1.V7'});self.assertEqual(y1['y'],'?');self.assertEqual(y1['status'],'ACTIVE')


if __name__=='__main__':unittest.main()
