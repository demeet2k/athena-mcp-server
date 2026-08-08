import tempfile
import tomllib
import unittest
from pathlib import Path

from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class MetadataConsistencyTests(unittest.TestCase):
    def test_package_and_server_versions_match_current_release(self):
        root=Path(__file__).resolve().parents[1]
        project=tomllib.loads((root/'pyproject.toml').read_text())['project']
        self.assertEqual(project['version'],SERVER_INFO['version'])
        self.assertEqual(project['name'],SERVER_INFO['name'])
        self.assertEqual(project['version'],'2.9.0')
        description=project['description'].lower()
        for phrase in ('nonlinear probabilistic','causal','finite belief'):
            self.assertIn(phrase,description)

    def test_v5_v10_and_claim_namespaces_are_exposed_without_collision(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            init=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
            self.assertEqual(init['serverInfo']['version'],'2.9.0')
            tools=srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']
            names=[x['name'] for x in tools]
            self.assertEqual(len(names),len(set(names)),'tool registry must not contain duplicate RPC names')
            for name in (
                'athena_bayes_predict','athena_experiment_design','athena_ood_score','athena_causal_identify',
                'athena_uncertainty_decompose','athena_dual_control_plan','athena_belief_register','athena_decision_evi',
                'athena_gaussian_belief_register','athena_decision_evpi','athena_causal_aipw','athena_structure_partial',
                'athena_gp_register','athena_gp_predict','athena_pc_stable_discover','athena_causal_tmle_binary','athena_sensitivity_evalue','athena_pomdp_solve','athena_evidence_dependence_fit',
                'athena_discovery_claim_register','athena_discovery_claim_witness','athena_discovery_claim_state',
                'athena_claim_register','athena_claim_state','athena_claim_promote',
            ):
                self.assertIn(name,names)
            by_name={x['name']:x for x in tools}
            self.assertEqual(by_name['athena_claim_register']['inputSchema']['required'],['claim_id','source_ref'])
            self.assertEqual(by_name['athena_discovery_claim_register']['inputSchema']['required'],['claim_key','statement'])
            self.assertNotEqual(by_name['athena_claim_register']['inputSchema'],by_name['athena_discovery_claim_register']['inputSchema'])

            uris={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']}
            for uri in ('athena://collective/v4','athena://collective/v5','athena://collective/v6','athena://collective/v7','athena://collective/v8','athena://collective/v9','athena://collective/v10','athena://authority'):
                self.assertIn(uri,uris)
            v6=srv.handle({'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v6'}})
            self.assertIn('result',v6);text=v6['result']['contents'][0]['text'];self.assertIn('athena_discovery_claim_',text);self.assertIn('athena_claim_',text)
            v10=srv.handle({'jsonrpc':'2.0','id':5,'method':'resources/read','params':{'uri':'athena://collective/v10'}})['result']['contents'][0]['text']
            self.assertIn('COLLECTIVE_RUNTIME_V10',v10);self.assertIn('Y1 authority',v10)
            srv.store.close()


if __name__=='__main__':unittest.main()
