import tempfile
import tomllib
import unittest
from pathlib import Path

import athena_mcp
from athena_mcp.protocol import SERVER_INFO
from athena_mcp.server import Server


class MetadataConsistencyTests(unittest.TestCase):
    def test_package_and_server_versions_match_current_release(self):
        root=Path(__file__).resolve().parents[1]
        project=tomllib.loads((root/'pyproject.toml').read_text())['project']
        self.assertEqual(project['version'],SERVER_INFO['version'])
        self.assertEqual(project['version'],athena_mcp.__version__)
        self.assertEqual(project['name'],SERVER_INFO['name'])
        self.assertEqual(project['version'],'2.5.0')
        self.assertIn('discovery',project['description'].lower())

    def test_v5_v6_and_claim_namespaces_are_exposed_without_collision(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            srv=Server(f.name)
            init=srv.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25'}})['result']
            self.assertEqual(init['serverInfo']['version'],'2.5.0')
            tools=srv.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})['result']['tools']
            names=[x['name'] for x in tools]
            self.assertEqual(len(names),len(set(names)),'tool registry must not contain duplicate RPC names')
            for name in (
                'athena_bandit_select','athena_topology_project_jspace',
                'athena_bayes_predict','athena_experiment_design','athena_schedule_multiperiod','athena_pareto_frontier','athena_projection_compensate',
                'athena_ood_score','athena_nonlinear_predict','athena_causal_identify','athena_mpc_plan','athena_schedule_certified',
                'athena_discovery_claim_register','athena_discovery_claim_witness','athena_discovery_claim_state',
                'athena_claim_register','athena_claim_state','athena_claim_promote',
            ):
                self.assertIn(name,names)
            by_name={x['name']:x for x in tools}
            self.assertEqual(by_name['athena_claim_register']['inputSchema']['required'],['claim_id','source_ref'])
            self.assertEqual(by_name['athena_discovery_claim_register']['inputSchema']['required'],['claim_key','statement'])
            self.assertNotEqual(by_name['athena_claim_register']['inputSchema'],by_name['athena_discovery_claim_register']['inputSchema'])

            uris={x['uri'] for x in srv.handle({'jsonrpc':'2.0','id':3,'method':'resources/list'})['result']['resources']}
            for uri in ('athena://collective/v4','athena://collective/v5','athena://collective/v6','athena://authority'):
                self.assertIn(uri,uris)
            v6=srv.handle({'jsonrpc':'2.0','id':4,'method':'resources/read','params':{'uri':'athena://collective/v6'}})
            self.assertIn('result',v6);text=v6['result']['contents'][0]['text'];self.assertIn('athena_discovery_claim_',text);self.assertIn('athena_claim_',text)
            srv.store.close()


if __name__=='__main__':unittest.main()
